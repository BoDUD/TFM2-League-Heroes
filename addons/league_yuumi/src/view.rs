//! 附身时整身不画：骑在队友头上的时候（本包给她挂 `league_yuumi_w_on`），她自己的动作（站着、走、挨打、出招、阵亡）全换成图里
//! 空白的 `a_*`，头上的小猫由队友身上的 buff 画面 `league_yuumi_w_ride` 画。平时她被放逐（谁都看不见）；本包只在她出招的那一小段
//! 解除放逐，这时她站在队友的位置上——不换的话会在队友脚下多出一只猫。只在游戏 0.6.4（Windows）上生效，别的版本什么都不做：出招的
//! 那一小段她照常画在队友脚下。
//!
//! 照 league_rammus 的 view.rs（源自 league_reksai / league_rell / league_jayce / league_nidalee / league_kayn_form）：游戏的显示世界
//! 每帧调用显示处理表里的更新函数（rva 0x23312a0），函数指针在 .rdata 的槽 rva 0x3c82db8（凯隐、佛耶戈、奈德丽、杰斯、伊莉丝、厄斐
//! 琉斯、芮尔、雷克塞、拉莫斯附加包也挂在这里，一个接一个调用）。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用槽里原来的
//! 函数，再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始：+0x40 名字，+0x68 / +0x70 / +0x78 正在播的动画名，
//! +0xb8 / +0xc0 buff 列表）。名字是 `league_yuumi` 的实体身上有附身 buff 时，正在播的动作换成 `a_*`（新名字用游戏同一个堆分配，旧的
//! 照游戏的做法释放）；附身结束后换回来。高清帧不用另管：league.dll 把登记英雄动画表里每个动作（a_idle 也在内）就地换成它的 hd_ 帧
//! （addons/league_main/src/lookup.rs）。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Mutex, Once};

use super::{wlog, RIDING};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。
/// 显示世界：实体表（hashbrown：控制字节指针、掩码、元素数）。
const TABLE: usize = 0x138;
const TABLE_MASK: usize = 0x140;
const TABLE_ITEMS: usize = 0x150;
const ELEM: usize = 0x1d0;
/// 值在元素里的位置（键是 8 字节的实体号）和值里的字段。
const VALUE: usize = 8;
const NAME_PTR: usize = 0x40;
const NAME_LEN_AT: usize = 0x48;
const ANIM_CAP: usize = 0x68;
const ANIM_PTR: usize = 0x70;
const ANIM_LEN: usize = 0x78;
const BUFFS_PTR: usize = 0xb8;
const BUFFS_LEN: usize = 0xc0;
const BUFF_SIZE: usize = 0x28;

/// 悠米在画面实体里的名字。
pub const NAME: &[u8] = b"league_yuumi";

/// 附身时换成空白 `a_*` 的动作：她的每一个动作。
pub const FORM_TAGS: [&str; 9] = ["idle", "run", "hit", "attack", "skill", "skill2", "w_off", "ult", "dead"];
const PREFIX: &str = "a_";

/// 正在播的动画名 + 是否附身 → 该播的名字（不用换就是 None）。附身结束后把本包换上去的 `a_idle` 等换回来。
pub fn anim_for(cur: &str, riding: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if riding { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的附身与否：变了才记一行 FORM。
    looks: Vec<(usize, u64, bool)>,
}

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, seen: 0, writes: 0, last: None, looks: Vec::new() });
static PREV: AtomicUsize = AtomicUsize::new(0);
static HOOK: Once = Once::new();

#[link(name = "kernel32")]
extern "system" {
    fn ReadProcessMemory(h: isize, base: *const c_void, buf: *mut c_void, size: usize, read: *mut usize) -> i32;
    fn GetCurrentProcess() -> isize;
    fn GetModuleHandleW(name: *const u16) -> usize;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
    fn GetProcessHeap() -> isize;
    fn HeapAlloc(heap: isize, flags: u32, bytes: usize) -> *mut u8;
    fn HeapFree(heap: isize, flags: u32, mem: *mut u8) -> i32;
}

fn read(addr: usize, len: usize) -> Option<Vec<u8>> {
    let mut buf = vec![0u8; len];
    let mut got = 0usize;
    let ok = unsafe {
        ReadProcessMemory(GetCurrentProcess(), addr as *const c_void, buf.as_mut_ptr() as *mut c_void, len, &mut got)
    };
    (ok != 0 && got == len).then_some(buf)
}

type Update = unsafe extern "system" fn(usize, usize, usize, f32);

/// 槽里换上的函数：先做原来的事，再给悠米换动作。
unsafe extern "system" fn update(this: usize, a2: usize, world: usize, dt: f32) {
    let prev = PREV.load(Ordering::Acquire);
    if prev != 0 {
        let f: Update = std::mem::transmute(prev);
        f(this, a2, world, dt);
    }
    let _ = std::panic::catch_unwind(|| unsafe { dress(world) });
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// 显示世界里每个悠米：按身上的附身 buff 换正在播的动画名。
unsafe fn dress(world: usize) {
    if !plausible(world) {
        return;
    }
    let ctrl = q(world + TABLE);
    let mask = q(world + TABLE_MASK);
    let items = q(world + TABLE_ITEMS);
    if items == 0 || !plausible(ctrl) || mask >= 1 << 16 || (mask + 1) & mask != 0 || items > mask + 1 {
        return;
    }
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Yuumi seen {} times, {} animation names swapped in 10 s",
                st.calls, st.seen, st.writes));
        }
        st.last = Some(now);
        st.calls = 0;
        st.seen = 0;
        st.writes = 0;
    }
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue; // empty or deleted
        }
        let elem = ctrl - (i + 1) * ELEM;
        let v = elem + VALUE;
        if q(v + NAME_LEN_AT) != NAME.len() {
            continue;
        }
        let ptr = q(v + NAME_PTR);
        if !plausible(ptr) || std::slice::from_raw_parts(ptr as *const u8, NAME.len()) != NAME {
            continue;
        }
        let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
        let has = |name: &str| plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == name.len() && std::slice::from_raw_parts(p as *const u8, n) == name.as_bytes()
        });
        let form = has(RIDING);
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let look = (world, key, form);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            if let Some(k) = super::counted("form_view") {
                wlog(format!("FORM display world {world:#x} Yuumi #{key}: {} (playing {cur}) #{k}",
                             if form { "RIDING - every action drawn as the blank a_*" } else { "on her own feet" }));
            }
        }
        let Some(want) = anim_for(cur, form) else { continue };
        let heap = GetProcessHeap();
        let fresh = HeapAlloc(heap, 0, want.len());
        if fresh.is_null() {
            continue;
        }
        std::ptr::copy_nonoverlapping(want.as_ptr(), fresh, want.len());
        std::ptr::write_unaligned((v + ANIM_CAP) as *mut usize, want.len());
        std::ptr::write_unaligned((v + ANIM_PTR) as *mut usize, fresh as usize);
        std::ptr::write_unaligned((v + ANIM_LEN) as *mut usize, want.len());
        if acap > 0 {
            HeapFree(heap, 0, aptr as *mut u8);
        }
        st.writes += 1;
    }
}

fn install() -> Result<(usize, usize), String> {
    let module = unsafe { GetModuleHandleW(std::ptr::null()) };
    if module == 0 {
        return Err("no module handle".into());
    }
    // the display handler and its slot, found by game_places (shared with league.dll and the other add-ons)
    let (_func, slot) = game_places::display()?;
    let cur = read(slot, 8).map(|b| usize::from_le_bytes(b.try_into().unwrap())).ok_or("the slot is unreadable")?;
    if !plausible(cur) {
        return Err(format!("the slot holds {cur:#x}"));
    }
    PREV.store(cur, Ordering::Release);
    let mut old = 0u32;
    if unsafe { VirtualProtect(slot as *mut c_void, 8, 0x04, &mut old) } == 0 {
        return Err("VirtualProtect failed".into());
    }
    unsafe { std::ptr::write_volatile(slot as *mut usize, update as Update as usize) };
    let mut tmp = 0u32;
    unsafe { VirtualProtect(slot as *mut c_void, 8, old, &mut tmp) };
    Ok((slot, cur))
}

/// 加载时换槽（一个进程只换一次）。
pub fn install_once() {
    HOOK.call_once(|| {
        match install() {
            Ok((slot, prev)) => wlog(format!(
                "FORM riding body on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::display().is_ok_and(|d| prev == d.0) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM riding body off ({e}): while she casts from the ally she is drawn at his feet")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_ride() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("a_idle"));
        assert_eq!(anim_for("skill", true).as_deref(), Some("a_skill"));
        assert_eq!(anim_for("ult", true).as_deref(), Some("a_ult"));
        assert_eq!(anim_for("a_run", false).as_deref(), Some("run")); // off his head again
        assert_eq!(anim_for("a_skill", true), None);
        assert_eq!(anim_for("idle", false), None);
        assert_eq!(anim_for("lo_idle", true), None); // the UI's frames are not hers on the battlefield
    }

    #[test]
    fn every_swapped_tag_is_in_her_sheet() {
        let fanim = include_str!("../../../league/champions/league_yuumi#anim.fanim");
        for t in FORM_TAGS {
            for p in ["", "a_", "hd_", "hd_a_"] {
                let name = format!("{p}{t}");
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_yuumi#anim.fanim");
            }
        }
    }
}
