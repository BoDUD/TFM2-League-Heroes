//! 整身变巨型：巨型纳尔时站着、跑着、挨打、阵亡也是巨型（主包只能用 `CasterAnimation` 换出招的动作，游戏按名字自动播的
//! idle / run / hit / dead 数据换不了）。照 league_nidalee 的 view.rs（整身变豹，同一个显示处理表的槽，game_places::hook::add
//! 一个接一个调用）：名字是 `league_gnar` 的实体身上有巨型的 buff `league_gnar_mg`（或巨型刚结束、还没播变回动作的
//! `league_gnar_was_mg`）时，正在播的 idle / run / hit / dead / attack 换成纳尔图里的 `m_idle` …。阵亡时 buff 清掉：
//! 尸体按倒下前那一帧的形态画（巨型的 m_dead 最后一帧就是迷你倒在地上）。找不到槽时什么都不做，退回半变身。

use std::sync::{Mutex, Once};

use super::{wlog, MEGA};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。

/// 纳尔在画面实体里的名字。
pub const NAME: &[u8] = b"league_gnar";

/// 游戏按名字自动播、巨型有自己一套的动作（纳尔图里的 `m_*`）；数据用 `CasterAnimation` 播的 m_skill / m_wallop / ult …
/// 本来就是巨型，不碰。`attack` 是普攻第一 tick（数据下一 tick 才播 `m_attack`）。
pub const FORM_TAGS: [&str; 5] = ["idle", "run", "hit", "dead", "attack"];
const PREFIX: &str = "m_";

/// 正在播的动画名 + 是不是巨型 → 该播的名字（不用换就是 None）。迷你时把本包换上去的 `m_idle` 等换回来。
pub fn anim_for(cur: &str, mega: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if mega { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

/// 每个纳尔上一帧的形态：(显示世界, 实体号) → 巨型。尸体按它画。
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

use game_places::heap::{GetProcessHeap, HeapAlloc, HeapFree};

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// 显示世界里每个纳尔：按身上的形态 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut forms) = FORMS.try_lock() else { return };
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Gnar seen {} times, {} animation names swapped in 10 s",
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
            plausible(p) && MEGA.iter().any(|f| n == f.len() && std::slice::from_raw_parts(p as *const u8, n) == f.as_bytes())
        });
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let dead = cur == "dead" || cur == "m_dead";
        let mega = forms.form(world, key, has, dead);
        let look = (world, key, mega);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("world {world:#x} Gnar #{key}: {} (playing {cur}{})", if mega { "MEGA" } else { "mini" },
                if dead && mega && !has { ", form remembered" } else { "" }));
        }
        let Some(want) = anim_for(cur, mega) else { continue };
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
        match game_places::hook::add("league_gnar", dress) {
            Ok((slot, prev)) => wlog(format!(
                "whole-body Mega on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("whole-body Mega off ({e}): only his casts show Mega")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_form() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("m_idle"));
        assert_eq!(anim_for("run", true).as_deref(), Some("m_run"));
        assert_eq!(anim_for("dead", true).as_deref(), Some("m_dead"));
        assert_eq!(anim_for("attack", true).as_deref(), Some("m_attack")); // the action's first tick
        assert_eq!(anim_for("m_attack", true), None); // the data's own cast
        assert_eq!(anim_for("m_wallop", true), None);
        assert_eq!(anim_for("ult", true), None);
        assert_eq!(anim_for("m_idle", false).as_deref(), Some("idle")); // back to Mini
        assert_eq!(anim_for("idle", false), None);
        assert_eq!(anim_for("transform", true), None);
        assert_eq!(anim_for("revert", true), None);
    }

    #[test]
    fn the_corpse_keeps_the_form_and_the_respawn_is_mini() {
        let mut f = Forms::default();
        assert!(!f.form(1, 7, false, false));
        assert!(f.form(1, 7, true, false)); // turned
        assert!(f.form(1, 7, false, true)); // dead: the buff is gone, still Mega
        assert!(!f.form(1, 7, false, false)); // respawned Mini
        assert!(!f.form(1, 8, false, true)); // another Gnar, never seen Mega
    }
}
