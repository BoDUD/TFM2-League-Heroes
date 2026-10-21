//! 整身变豹：美洲狮形态时奈德丽站着、跑着、挨打、阵亡也是豹子（主包只能用 `CasterAnimation` 换出招的动作，游戏按名字
//! 自动播的 idle / run / hit / dead 数据换不了）。只在游戏 0.6.4 起的 Windows 版上生效（地址由 game_places 运行时找，0.6.5 核对过），别的版本什么都不做，退回半变身。
//!
//! 照 league_kayn_form 的 view.rs（凯隐的完整变身，2026-10-08 在游戏里认可）：游戏的显示世界每帧调用显示处理表里的更新函数
//! （rva 0x23312a0；0.6.3 时 0x2808e30），函数指针在 .rdata 的槽 rva 0x3c82db8（0.6.3 时 0x3c31358；凯隐、佛耶戈附加包和群里的变身前置也挂在这里，一个接一个调用）。
//! 加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用槽里原来的函数，再走一遍显示世界的实体表（+0x138 的哈希表，每格
//! 0x1d0 字节，值从 +8 开始：+0x38 名字，+0x68 / +0x70 / +0x78 正在播的动画名，+0xb8 / +0xc0 buff 列表）。名字是
//! `league_nidalee` 的实体身上有美洲狮形态的 buff `league_nidalee_cg` 时，正在播的 idle / run / hit / dead / attack 换成奈德丽
//! 图里的 `c_idle` …（tools/art 导入时放进同一张图）。新名字用游戏同一个堆（GetProcessHeap）分配，旧的照游戏的做法释放。
//! 阵亡时 buff 清掉：尸体按倒下前那一帧的形态画（复活后没有 buff，是人形，和英雄联盟一样）。

use std::sync::{Mutex, Once};

use super::{wlog, FORM};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。

/// 奈德丽在画面实体里的名字。
pub const NAME: &[u8] = b"league_nidalee";

/// 游戏按名字自动播、美洲狮有自己一套的动作（奈德丽图里的 `c_*`）；数据用 `CasterAnimation` 播的 c_skill / c_pounce …
/// 本来就是豹子，不碰。`attack` 是普攻第一 tick（数据下一 tick 才播 `c_attack`）。
pub const FORM_TAGS: [&str; 5] = ["idle", "run", "hit", "dead", "attack"];
const PREFIX: &str = "c_";

/// 正在播的动画名 + 是不是美洲狮 → 该播的名字（不用换就是 None）。人形时把本包换上去的 `c_idle` 等换回来。
pub fn anim_for(cur: &str, cougar: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if cougar { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

/// 每个奈德丽上一帧的形态：(显示世界, 实体号) → 美洲狮。尸体按它画。
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
static HOOK: Once = Once::new();

#[link(name = "kernel32")]
extern "system" {
    fn GetProcessHeap() -> isize;
    fn HeapAlloc(heap: isize, flags: u32, bytes: usize) -> *mut u8;
    fn HeapFree(heap: isize, flags: u32, mem: *mut u8) -> i32;
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// 显示世界里每个奈德丽：按身上的形态 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut forms) = FORMS.try_lock() else { return };
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Nidalee seen {} times, {} animation names swapped in 10 s",
                st.calls, st.seen, st.writes));
        }
        st.last = Some(now);
        st.calls = 0;
        st.seen = 0;
        st.writes = 0;
    }
    for e in ents {
        let elem = e.elem;
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
        let cougar = forms.form(world, key, has, dead);
        let look = (world, key, cougar);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("world {world:#x} Nidalee #{key}: {} (playing {cur}{})", if cougar { "COUGAR" } else { "human" },
                if dead && cougar && !has { ", form remembered" } else { "" }));
        }
        let Some(want) = anim_for(cur, cougar) else { continue };
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

/// 加载时换槽（一个进程只换一次）。
pub fn install_once() {
    HOOK.call_once(|| {
        match game_places::hook::add("league_nidalee", dress) {
            Ok((slot, prev)) => wlog(format!(
                "whole-body cougar on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("whole-body cougar off ({e}): only her casts show the cougar")),
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
        assert_eq!(anim_for("c_pounce", true), None);
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
        assert!(f.form(1, 7, false, true)); // dead: the buff is gone, still a cougar
        assert!(!f.form(1, 7, false, false)); // respawned human
        assert!(!f.form(1, 8, false, true)); // another Nidalee, never seen as a cougar
    }
}
