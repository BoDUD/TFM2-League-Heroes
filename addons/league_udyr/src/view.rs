//! 每个姿态整身：熊、公羊、凤凰姿态时站着、跑着、挨打、阵亡也是那个姿态的样子（主包只能用 `CasterAnimation` 换出招的动作，
//! 游戏按名字自动播的 idle / run / hit / dead 数据换不了）。照 league_gnar 的 view.rs（同一个显示处理表的槽，
//! game_places::hook::add 一个接一个调用）：名字是 `league_udyr` 的实体身上有姿态的 buff（主包数据：`league_udyr_st_q` 熊、
//! `_st_e` 公羊、`_st_r` 凤凰，永久，换姿态时换掉）时，正在播的 idle / run / hit / dead / attack 换成乌迪尔图里那个姿态的
//! `q_idle` / `e_run` …；没有姿态 buff（平常护头的样子）时把换上去的换回来。阵亡时 buff 还在（死了的单位 buff 冻住）：
//! 尸体按倒下前那一帧的姿态画。找不到槽时什么都不做，退回只有出招是姿态的样子。

use std::sync::{Mutex, Once};

use super::wlog;
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 乌迪尔在画面实体里的名字。
pub const NAME: &[u8] = b"league_udyr";

/// 姿态 buff → 图里那一套动作的前缀（熊 `q_`、公羊 `e_`、凤凰 `r_`）。
pub const STANCES: [(&str, &str); 3] = [("league_udyr_st_q", "q_"), ("league_udyr_st_e", "e_"), ("league_udyr_st_r", "r_")];

/// 游戏按名字自动播、每个姿态有自己一套的动作；数据用 `CasterAnimation` 播的 skill / skill2 / e_stun / ult … 不碰。
/// `attack` 是普攻第一 tick（数据同一 tick 才播 `q_attack`）。
pub const FORM_TAGS: [&str; 5] = ["idle", "run", "hit", "dead", "attack"];

/// 正在播的动画名 + 姿态前缀（None = 平常）→ 该播的名字（不用换就是 None）。
pub fn anim_for(cur: &str, stance: Option<&str>) -> Option<String> {
    let base = STANCES
        .iter()
        .find_map(|(_, pre)| cur.strip_prefix(pre).filter(|b| FORM_TAGS.contains(b)))
        .unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = match stance {
        Some(pre) => format!("{pre}{base}"),
        None => base.to_string(),
    };
    (want != cur).then_some(want)
}

/// 每个乌迪尔上一帧的姿态：(显示世界, 实体号) → 前缀。尸体按它画。
#[derive(Default)]
pub struct Forms {
    seen: Vec<(usize, u64, Option<&'static str>)>,
}

impl Forms {
    /// 这一帧该画的姿态：活着按 buff（记下来），播 dead 时用记下的（buff 还在就用 buff）。
    pub fn form(&mut self, world: usize, key: u64, has: Option<&'static str>, dead: bool) -> Option<&'static str> {
        let at = self.seen.iter().position(|e| e.0 == world && e.1 == key);
        if dead {
            return has.or_else(|| at.and_then(|i| self.seen[i].2));
        }
        match at {
            Some(i) => self.seen[i].2 = has,
            None => {
                self.seen.push((world, key, has));
                if self.seen.len() > 64 {
                    self.seen.remove(0);
                }
            }
        }
        has
    }
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    looks: Vec<(usize, u64, Option<&'static str>)>,
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

/// 显示世界里每个乌迪尔：按身上的姿态 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut forms) = FORMS.try_lock() else { return };
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Udyr seen {} times, {} animation names swapped in 10 s",
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
        let mut has: Option<&'static str> = None;
        if plausible(bp) && bn <= 256 {
            for k in 0..bn {
                let b = bp + k * BUFF_SIZE;
                let (p, n) = (q(b + 8), q(b + 0x10));
                if !plausible(p) {
                    continue;
                }
                if let Some((_, pre)) = STANCES
                    .iter()
                    .find(|(f, _)| n == f.len() && std::slice::from_raw_parts(p as *const u8, n) == f.as_bytes())
                {
                    has = Some(pre);
                }
            }
        }
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let dead = cur == "dead" || cur.ends_with("_dead");
        let stance = forms.form(world, key, has, dead);
        let look = (world, key, stance);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("world {world:#x} Udyr #{key}: {} (playing {cur}{})",
                match stance { Some("q_") => "BEAR", Some("e_") => "RAM", Some("r_") => "PHOENIX", _ => "plain" },
                if dead && stance.is_some() && has.is_none() { ", stance remembered" } else { "" }));
        }
        let Some(want) = anim_for(cur, stance) else { continue };
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
        match game_places::hook::add("league_udyr", dress) {
            Ok((slot, prev)) => wlog(format!(
                "whole-body stances on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("whole-body stances off ({e}): only his attacks and casts show the stances")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_stance() {
        assert_eq!(anim_for("idle", Some("q_")).as_deref(), Some("q_idle"));
        assert_eq!(anim_for("run", Some("e_")).as_deref(), Some("e_run"));
        assert_eq!(anim_for("dead", Some("r_")).as_deref(), Some("r_dead"));
        assert_eq!(anim_for("attack", Some("q_")).as_deref(), Some("q_attack")); // the attack's first tick
        assert_eq!(anim_for("q_attack", Some("q_")), None); // the data's own swing
        assert_eq!(anim_for("e_run", Some("e_")), None); // the charge
        assert_eq!(anim_for("q_idle", Some("e_")).as_deref(), Some("e_idle")); // a stance swap
        assert_eq!(anim_for("r_idle", None).as_deref(), Some("idle")); // back to the plain guard
        assert_eq!(anim_for("idle", None), None);
        for cast in ["skill", "skill2", "e_stun", "ult"] {
            assert_eq!(anim_for(cast, Some("q_")), None);
        }
    }

    #[test]
    fn the_corpse_keeps_the_stance_and_the_respawn_is_plain() {
        let mut f = Forms::default();
        assert_eq!(f.form(1, 7, None, false), None);
        assert_eq!(f.form(1, 7, Some("e_"), false), Some("e_"));
        assert_eq!(f.form(1, 7, None, true), Some("e_")); // dead: remembered
        assert_eq!(f.form(1, 7, None, false), None); // respawned plain
        assert_eq!(f.form(1, 8, None, true), None); // another Udyr, never seen in a stance
    }
}
