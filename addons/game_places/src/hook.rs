//! 一个显示钩子给所有整身变身的英雄用（2026-10-20，把 15 个附加包各自换槽、各自每帧走一遍实体表合成一个）。
//!
//! 每个 DLL（附加包合集，或单独装的一个附加包）只换一次显示更新槽（[`crate::display`]）：先调用槽里原来的函数（游戏的、
//! league.dll 的或别的 mod 的），再把显示世界的实体表走一遍，收成 [`Ent`] 列表，交给每个登记过的英雄（[`add`]）——
//! 每个英雄各自 `catch_unwind`，一个出错不影响别的。
//!
//! 显示世界和实体值的布局（0.6.3 / 0.6.4 / 0.6.5 一样，各附加包以前各抄一份）只在这里：
//! 显示世界 +0x138 的 hashbrown 表（控制字节指针、+0x140 掩码、+0x150 元素数），每格 0x1d0 字节，键是 8 字节实体号，
//! 值从 +8 开始：+0x40 / +0x48 名字（String 指针、长度），+0x68 / +0x70 / +0x78 正在播的动画名（String：容量、指针、
//! 长度），+0xb8 / +0xc0 buff 列表（每个 0x28 字节，名字指针 +8、长度 +0x10）。

#[cfg(windows)]
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Mutex, OnceLock};

pub const TABLE: usize = 0x138;
pub const TABLE_MASK: usize = 0x140;
pub const TABLE_ITEMS: usize = 0x150;
pub const ELEM: usize = 0x1d0;
pub const VALUE: usize = 8;
pub const NAME_PTR: usize = 0x40;
pub const NAME_LEN_AT: usize = 0x48;
pub const ANIM_CAP: usize = 0x68;
pub const ANIM_PTR: usize = 0x70;
pub const ANIM_LEN: usize = 0x78;
pub const BUFFS_PTR: usize = 0xb8;
pub const BUFFS_LEN: usize = 0xc0;
pub const BUFF_SIZE: usize = 0x28;

/// 实体表的一格：元素地址（键在开头）和实体号。值在 `elem + VALUE`。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Ent {
    pub elem: usize,
    pub key: u64,
}

/// 登记的英雄：每帧拿到显示世界和它的实体列表。
pub type Dresser = unsafe fn(world: usize, ents: &[Ent]);

static DRESSERS: Mutex<Vec<(&'static str, Dresser)>> = Mutex::new(Vec::new());
#[cfg(windows)]
static PREV: AtomicUsize = AtomicUsize::new(0);
static INSTALLED: OnceLock<Result<(usize, usize), String>> = OnceLock::new();

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// 显示世界实体表里有东西的格子（表的头不像样就是空的）。
///
/// # Safety
/// `world` must be the display world the game handed its display handler.
pub unsafe fn ents(world: usize) -> Vec<Ent> {
    if !plausible(world) {
        return Vec::new();
    }
    let ctrl = q(world + TABLE);
    let mask = q(world + TABLE_MASK);
    let items = q(world + TABLE_ITEMS);
    if items == 0 || !plausible(ctrl) || mask >= 1 << 16 || (mask + 1) & mask != 0 || items > mask + 1 {
        return Vec::new();
    }
    let mut out = Vec::with_capacity(items);
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue; // empty or deleted
        }
        let elem = ctrl - (i + 1) * ELEM;
        out.push(Ent { elem, key: q(elem) as u64 });
    }
    out
}

#[cfg(windows)]
type Update = unsafe extern "system" fn(usize, usize, usize, f32);

#[cfg(windows)]
unsafe extern "system" fn update(this: usize, a2: usize, world: usize, dt: f32) {
    let prev = PREV.load(Ordering::Acquire);
    if prev != 0 {
        let f: Update = std::mem::transmute(prev);
        f(this, a2, world, dt);
    }
    let Ok(list) = DRESSERS.try_lock() else { return };
    if list.is_empty() {
        return;
    }
    let all = match std::panic::catch_unwind(|| unsafe { ents(world) }) {
        Ok(v) => v,
        Err(_) => return,
    };
    for (_, f) in list.iter() {
        let f = *f;
        let _ = std::panic::catch_unwind(|| unsafe { f(world, &all) });
    }
}

#[cfg(windows)]
fn install() -> Result<(usize, usize), String> {
    #[link(name = "kernel32")]
    extern "system" {
        fn VirtualProtect(addr: *mut std::ffi::c_void, size: usize, new: u32, old: *mut u32) -> i32;
    }
    let (_func, slot) = crate::display()?;
    let cur = unsafe { q(slot) };
    if !plausible(cur) {
        return Err(format!("the slot holds {cur:#x}"));
    }
    PREV.store(cur, Ordering::Release);
    let mut old = 0u32;
    if unsafe { VirtualProtect(slot as *mut std::ffi::c_void, 8, 0x04, &mut old) } == 0 {
        return Err("VirtualProtect failed".into());
    }
    unsafe { std::ptr::write_volatile(slot as *mut usize, update as Update as usize) };
    let mut tmp = 0u32;
    unsafe { VirtualProtect(slot as *mut std::ffi::c_void, 8, old, &mut tmp) };
    Ok((slot, cur))
}

#[cfg(not(windows))]
fn install() -> Result<(usize, usize), String> {
    Err("not Windows".into())
}

/// 登记一个英雄（`id` 只用来避免重复登记），这个 DLL 第一次登记时换槽。返回 (槽, 槽里原来的函数) 给日志，或者为什么没挂上。
pub fn add(id: &'static str, f: Dresser) -> Result<(usize, usize), String> {
    {
        let mut list = DRESSERS.lock().unwrap_or_else(|e| e.into_inner());
        if !list.iter().any(|(i, _)| *i == id) {
            list.push((id, f));
        }
    }
    INSTALLED.get_or_init(install).clone()
}

/// 登记了几个英雄（日志用）。
pub fn count() -> usize {
    DRESSERS.lock().map(|l| l.len()).unwrap_or(0)
}

/// 槽里原来是不是游戏自己的显示函数（日志用）。
pub fn chained_to_game(prev: usize) -> bool {
    crate::display().is_ok_and(|d| prev == d.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    unsafe fn a(_: usize, _: &[Ent]) {}
    unsafe fn b(_: usize, _: &[Ent]) {}

    #[test]
    fn a_hero_is_listed_once() {
        let _ = add("a", a);
        let _ = add("a", a);
        let _ = add("b", b);
        assert_eq!(count(), 2);
    }

    /// Old way (15 hooks, each walking the table) against the shared walk, on a fake display world of 100 entities
    /// (128 slots): `cargo test --release -p game_places one_walk -- --ignored --nocapture`.
    #[test]
    #[ignore]
    fn one_walk_against_fifteen() {
        const SLOTS: usize = 128;
        let names: Vec<Vec<u8>> = (0..100).map(|i| format!("league_hero_{i:03}").into_bytes()).collect();
        let mut mem = vec![0u8; SLOTS * ELEM + SLOTS + 16];
        let ctrl = mem.as_mut_ptr() as usize + SLOTS * ELEM;
        for i in 0..SLOTS {
            let elem = ctrl - (i + 1) * ELEM;
            unsafe { *(ctrl as *mut u8).add(i) = if i < names.len() { 0 } else { 0x80 } };
            if i < names.len() {
                unsafe {
                    std::ptr::write_unaligned(elem as *mut u64, i as u64);
                    std::ptr::write_unaligned((elem + VALUE + NAME_PTR) as *mut usize, names[i].as_ptr() as usize);
                    std::ptr::write_unaligned((elem + VALUE + NAME_LEN_AT) as *mut usize, names[i].len());
                }
            }
        }
        let mut world = vec![0u8; 0x200];
        let w = world.as_mut_ptr() as usize;
        unsafe {
            std::ptr::write_unaligned((w + TABLE) as *mut usize, ctrl);
            std::ptr::write_unaligned((w + TABLE_MASK) as *mut usize, SLOTS - 1);
            std::ptr::write_unaligned((w + TABLE_ITEMS) as *mut usize, names.len());
        }
        let heroes: Vec<&[u8]> = (0..15).map(|k| names[k * 6].as_slice()).collect();
        let hit = |elem: usize, want: &[u8]| unsafe {
            let v = elem + VALUE;
            q(v + NAME_LEN_AT) == want.len() && std::slice::from_raw_parts(q(v + NAME_PTR) as *const u8, want.len()) == want
        };
        let frames = 20_000;
        let t0 = std::time::Instant::now();
        let mut found = 0;
        for _ in 0..frames {
            for h in &heroes {
                found += unsafe { ents(w) }.iter().filter(|e| hit(e.elem, h)).count();
            }
        }
        let old = t0.elapsed();
        let t1 = std::time::Instant::now();
        for _ in 0..frames {
            let all = unsafe { ents(w) };
            for h in &heroes {
                found += all.iter().filter(|e| hit(e.elem, h)).count();
            }
        }
        let new = t1.elapsed();
        assert_eq!(found, 2 * frames * 15);
        eprintln!("per frame: 15 walks {:.2} us, one walk {:.2} us",
                  old.as_secs_f64() * 1e6 / frames as f64, new.as_secs_f64() * 1e6 / frames as f64);
    }

    #[test]
    fn a_world_that_is_no_pointer_has_no_entities() {
        assert!(unsafe { ents(0) }.is_empty());
    }
}
