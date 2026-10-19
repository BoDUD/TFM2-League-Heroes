//! 下马整身换形态：下马作战时芮尔站着、走着、挨打、普攻、放裂阵、阵亡都是披甲步行的她（主包只能用 `CasterAnimation` 换出招的
//! 动作，游戏按名字自动播的 idle / run / hit / dead 数据换不了，所以主包里她一直骑着马，下马只是一层铁甲光环）。只在游戏 0.6.4
//! （Windows）上生效，别的版本什么都不做，退回主包那样。
//!
//! 照 league_jayce 的 view.rs（杰斯的整身变炮，源自 league_nidalee / league_kayn_form）：游戏的显示世界每帧调用显示处理表里的更新
//! 函数（rva 0x23312a0），函数指针在 .rdata 的槽 rva 0x3c82db8（凯隐、佛耶戈、奈德丽、杰斯、伊莉丝、厄斐琉斯附加包也挂在这里，
//! 一个接一个调用）。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用槽里原来的函数，再走一遍显示世界的实体表（+0x138
//! 的哈希表，每格 0x1d0 字节，值从 +8 开始：+0x40 名字，+0x68 / +0x70 / +0x78 正在播的动画名，+0xb8 / +0xc0 buff 列表）。名字是
//! `league_rell` 的实体身上有下马 buff `league_rell_foot` 时，正在播的 idle / run / hit / attack / skill / dead 换成芮尔图里的
//! `f_idle` …（新名字用游戏同一个堆分配，旧的照游戏的做法释放）。高清帧不用另管：league.dll 把登记英雄动画表里每个动作（f_idle 也在
//! 内）就地换成它的 hd_ 帧（addons/league_main/src/lookup.rs）。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Mutex, Once};

use super::{wlog, FORM};

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

/// 芮尔在画面实体里的名字。
pub const NAME: &[u8] = b"league_rell";

/// 下马有自己一套的动作（芮尔图里的 `f_*`）：游戏按名字自动播的待机、走、挨打、普攻（动作名 attack）、裂阵（动作名 skill）、
/// 阵亡（尸体留下马的样子，复活是骑马），和数据用 `CasterAnimation` 播的极涌（ult，0.1.2：原来下马放大招时马会冒出来半秒，
/// 英雄联盟下马有自己的 Biped_Spell4_Cast）。skill2 / skill2_up 不碰：轰落落地本来就是下马的她，驾临是上马冲锋。
pub const FORM_TAGS: [&str; 7] = ["idle", "run", "hit", "attack", "skill", "dead", "ult"];
const PREFIX: &str = "f_";

/// 正在播的动画名 + 是不是下马 → 该播的名字（不用换就是 None）。骑马时把本包换上去的 `f_idle` 等换回来。
pub fn anim_for(cur: &str, foot: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if foot { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的形态：变了才记一行 FORM。
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

/// 槽里换上的函数：先做原来的事，再给芮尔换动作。
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

/// 显示世界里每个芮尔：按身上的下马 buff 换正在播的动画名。
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
            wlog(format!("display handler: {} calls, Rell seen {} times, {} animation names swapped in 10 s",
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
        let foot = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == FORM.len() && std::slice::from_raw_parts(p as *const u8, n) == FORM.as_bytes()
        });
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let look = (world, key, foot);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            if let Some(k) = super::counted("form_view") {
                wlog(format!("FORM display world {world:#x} Rell #{key}: {} (playing {cur}) #{k}",
                    if foot { "ON FOOT - idle/run/hit/attack/skill/dead drawn as f_*" } else { "mounted" }));
            }
        }
        let Some(want) = anim_for(cur, foot) else { continue };
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
                "FORM whole body on foot on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::display().is_ok_and(|d| prev == d.0) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM whole body on foot off ({e}): she stays mounted on screen (the main pack's look)")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_form() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("f_idle"));
        assert_eq!(anim_for("run", true).as_deref(), Some("f_run"));
        assert_eq!(anim_for("hit", true).as_deref(), Some("f_hit"));
        assert_eq!(anim_for("attack", true).as_deref(), Some("f_attack"));
        assert_eq!(anim_for("skill", true).as_deref(), Some("f_skill")); // Shattering Strike on foot
        assert_eq!(anim_for("dead", true).as_deref(), Some("f_dead"));
        assert_eq!(anim_for("ult", true).as_deref(), Some("f_ult")); // Magnet Storm on foot
        assert_eq!(anim_for("f_ult", false).as_deref(), Some("ult"));
        assert_eq!(anim_for("skill2", true), None); // Crash Down lands her on foot by itself
        assert_eq!(anim_for("skill2_up", true), None); // Mount Up
        assert_eq!(anim_for("f_idle", false).as_deref(), Some("idle")); // mounted again
        assert_eq!(anim_for("f_skill", false).as_deref(), Some("skill"));
        assert_eq!(anim_for("idle", false), None);
    }

    #[test]
    fn every_swapped_tag_is_in_her_sheet() {
        let fanim = include_str!("../../../league/champions/league_rell#anim.fanim");
        for t in FORM_TAGS {
            for name in [t.to_string(), format!("{PREFIX}{t}"), format!("hd_{PREFIX}{t}")] {
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_rell#anim.fanim");
            }
        }
    }
}
