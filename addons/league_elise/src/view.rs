//! 整身变蜘蛛：蜘蛛形态时伊莉丝站着、跑着、挨打、阵亡也是蜘蛛（主包只能用 `CasterAnimation` 换出招的动作，游戏按名字
//! 自动播的 idle / run / hit / dead 数据换不了）。只在游戏 0.6.4（Windows）上生效，别的版本什么都不做，退回主包那样（只有出招
//! 是蜘蛛）。
//!
//! 照 league_nidalee 的 view.rs（奈德丽的整身变豹，2026-10-13 在游戏里认可；源自 league_kayn_form）：游戏的显示世界每帧调用显示
//! 处理表里的更新函数（rva 0x23312a0），函数指针在 .rdata 的槽 rva 0x3c82db8（凯隐、佛耶戈、奈德丽、杰斯附加包也挂在这里，一个接
//! 一个调用）。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用槽里原来的函数，再走一遍显示世界的实体表（+0x138 的哈希表，
//! 每格 0x1d0 字节，值从 +8 开始：+0x40 名字，+0x68 / +0x70 / +0x78 正在播的动画名，+0xb8 / +0xc0 buff 列表）。名字是
//! `league_elise` 的实体身上有蜘蛛形态的 buff `league_elise_sp` 时，正在播的 idle / run / hit / dead / attack 换成伊莉丝图里的
//! `c_idle` …（新名字用游戏同一个堆分配，旧的照游戏的做法释放）。高清帧不用另管：league.dll 把登记英雄动画表里每个动作（c_idle
//! 也在内）就地换成它的 hd_ 帧（addons/league_main/src/lookup.rs）。阵亡时 buff 清掉：尸体按倒下前那一帧的形态画（复活后没有
//! buff，是人形，和英雄联盟一样）。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Mutex, Once};

use super::{wlog, FORM};

/// 显示处理表里的更新函数（0.6.4）和存它的槽。
const FN_RVA: usize = 0x23312a0;
const SLOT_RVA: usize = 0x3c82db8;
/// push r15; push r14; push r13; push r12; push rsi; push rdi; push rbp; push rbx; sub rsp, 0x88; movdqa [rsp+..], xmm7
const FN_HEAD: [u8; 24] = [0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x55, 0x53, 0x48, 0x81, 0xec, 0x88,
    0x00, 0x00, 0x00, 0x66, 0x0f, 0x7f, 0x7c, 0x24];
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

/// 伊莉丝在画面实体里的名字。
pub const NAME: &[u8] = b"league_elise";

/// 游戏按名字自动播、蜘蛛有自己一套的动作（伊莉丝图里的 `c_*`）；数据用 `CasterAnimation` 播的 c_attack / c_skill / c_skill2 /
/// c_land / c_transform …
/// 本来就是蜘蛛，不碰。`attack` 是普攻第一 tick（数据下一 tick 才播 `c_attack`）。
pub const FORM_TAGS: [&str; 5] = ["idle", "run", "hit", "dead", "attack"];
const PREFIX: &str = "c_";

/// 正在播的动画名 + 是不是蜘蛛 → 该播的名字（不用换就是 None）。人形时把本包换上去的 `c_idle` 等换回来。
pub fn anim_for(cur: &str, spider: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if spider { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

/// 每个伊莉丝上一帧的形态：(显示世界, 实体号) → 蜘蛛。尸体按它画。
#[derive(Default)]
pub struct Forms {
    seen: Vec<(usize, u64, bool)>,
}

impl Forms {
    /// 这一帧该画的形态：活着按 buff（记下来），播 dead 时用记下的。
    pub fn form(&mut self, world: usize, key: u64, has_buff: bool, dead: bool) -> bool {
        let at = self.seen.iter().position(|e| e.0 == world && e.1 == key);
        if dead {
            return at.is_some_and(|i| self.seen[i].2) || has_buff;
        }
        match at {
            Some(i) => self.seen[i].2 = has_buff,
            None => {
                self.seen.push((world, key, has_buff));
                if self.seen.len() > 64 {
                    self.seen.remove(0);
                }
            }
        }
        has_buff
    }
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    looks: Vec<(usize, u64, bool)>,
}

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, seen: 0, writes: 0, last: None, looks: Vec::new() });
static FORMS: Mutex<Forms> = Mutex::new(Forms { seen: Vec::new() });
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

/// 槽里换上的函数：先做原来的事，再给伊莉丝换动作。
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

/// 显示世界里每个伊莉丝：按身上的形态 buff 换正在播的动画名。
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
    let Ok(mut forms) = FORMS.try_lock() else { return };
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Elise seen {} times, {} animation names swapped in 10 s",
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
        let has = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
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
        let dead = cur == "dead" || cur == "c_dead";
        let spider = forms.form(world, key, has, dead);
        let look = (world, key, spider);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("world {world:#x} Elise #{key}: {} (playing {cur}{})", if spider { "SPIDER" } else { "human" },
                if dead && spider && !has { ", form remembered" } else { "" }));
        }
        let Some(want) = anim_for(cur, spider) else { continue };
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
    let func = module + FN_RVA;
    if read(func, FN_HEAD.len()).as_deref() != Some(&FN_HEAD[..]) {
        return Err("not game 0.6.4 (the display handler differs)".into());
    }
    let slot = module + SLOT_RVA;
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
        let module = unsafe { GetModuleHandleW(std::ptr::null()) };
        match install() {
            Ok((slot, prev)) => wlog(format!(
                "whole-body spider on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if prev == module + FN_RVA { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("whole-body spider off ({e}): only her casts show the spider")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_form() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("c_idle"));
        assert_eq!(anim_for("run", true).as_deref(), Some("c_run"));
        assert_eq!(anim_for("attack", true).as_deref(), Some("c_attack")); // the action's first tick
        assert_eq!(anim_for("c_attack", true), None); // the data's own cast
        assert_eq!(anim_for("c_land", true), None);
        assert_eq!(anim_for("c_transform", true), None); // the turn back to human
        assert_eq!(anim_for("dead", true).as_deref(), Some("c_dead"));
        assert_eq!(anim_for("hit", true).as_deref(), Some("c_hit"));
        assert_eq!(anim_for("c_idle", false).as_deref(), Some("idle")); // back to human
        assert_eq!(anim_for("idle", false), None);
        assert_eq!(anim_for("transform", true), None);
        assert_eq!(anim_for("skill", true), None);
    }

    #[test]
    fn the_corpse_keeps_the_form_and_the_respawn_is_human() {
        let mut f = Forms::default();
        assert!(!f.form(1, 7, false, false));
        assert!(f.form(1, 7, true, false)); // turned
        assert!(f.form(1, 7, false, true)); // dead: the buff is gone, still a spider
        assert!(!f.form(1, 7, false, false)); // respawned human
        assert!(!f.form(1, 8, false, true)); // another Elise, never seen as a spider
    }

    #[test]
    fn every_swapped_tag_is_in_her_sheet() {
        let fanim = include_str!("../../../league/champions/league_elise#anim.fanim");
        for t in FORM_TAGS {
            for name in [t.to_string(), format!("{PREFIX}{t}"), format!("hd_{PREFIX}{t}")] {
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_elise#anim.fanim");
            }
        }
    }
}
