//! 整身红温：过热时站着、跑着、挨打、阵亡也是红温的样子（用户 2026-10-25：「红温整套切换」——主包只能用
//! `CasterAnimation` 换出招的动作：过热时的普攻播 `oh_attack`，游戏按名字自动播的 idle / run / hit / dead 数据换不了）。
//! 照 league_shyvana 的 view.rs（整身变龙，同一个显示处理表的槽，game_places::hook::add 一个接一个调用）：名字是
//! `league_rumble` 的实体身上有过热的 buff `league_rumble_oh`（主包数据：oh_t tick）时，正在播的 idle / run / hit / dead /
//! attack 换成他图里的 `oh_idle` …；过热结束换回来。尸体按倒下前那一帧的样子画，复活是平常的样子。
//! 找不到槽时什么都不做，退回只有普攻是红温。
//!
//! 边走边喷火（0.2.0）：身上有 `league_rumble_q_on`（副本的纵火盛宴）时，idle / run 换成 `q_stand` / `q_run`（炮口喷着火）；
//! 同时过热也是喷火的样子先（红温那套没有火），喷完再红温。

use std::sync::{Mutex, Once};

use super::{wlog, FLAMING, OVERHEAT};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 兰博在画面实体里的名字。
pub const NAME: &[u8] = b"league_rumble";

/// 游戏按名字自动播、红温有自己一套的动作（他图里的 `oh_*`）；数据用 `CasterAnimation` 播的 skill / skill2 / ult … 不碰
/// （过热时 Q、E、W 沉默）。`attack` 是普攻第一 tick（数据同一 tick 播 `oh_attack`）。
pub const FORM_TAGS: [&str; 5] = ["idle", "run", "hit", "dead", "attack"];
const PREFIX: &str = "oh_";
/// 喷火时站着、跑着播的（他图里的 q_stand / q_run）：(平常的名字, 喷火的名字)。
pub const FLAME_TAGS: [(&str, &str); 2] = [("idle", "q_stand"), ("run", "q_run")];

/// 正在播的动画名 + 是不是过热 + 是不是在喷火 → 该播的名字（不用换就是 None）。本包换上去的 `oh_*` / `q_*` 在状态结束时换回来。
pub fn anim_for(cur: &str, hot: bool, flaming: bool) -> Option<String> {
    let base = FLAME_TAGS.iter().find(|f| f.1 == cur).map(|f| f.0)
        .or_else(|| cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)))
        .unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = match FLAME_TAGS.iter().find(|f| f.0 == base) {
        Some(f) if flaming => f.1.to_string(),
        _ if hot => format!("{PREFIX}{base}"),
        _ => base.to_string(),
    };
    (want != cur).then_some(want)
}

/// 每个兰博上一帧的样子：(显示世界, 实体号) → 红温。尸体按它画。
#[derive(Default)]
pub struct Forms {
    seen: Vec<(usize, u64, bool)>,
}

impl Forms {
    /// 这一帧该画的样子：活着按 buff（记下来），播 dead 时用记下的。
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
    looks: Vec<(usize, u64, bool, bool)>,
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

/// 显示世界里每个兰博：按身上的过热 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut forms) = FORMS.try_lock() else { return };
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Rumble seen {} times, {} animation names swapped in 10 s",
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
        let carries = |names: &[&str]| plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && names.iter().any(|f| n == f.len() && std::slice::from_raw_parts(p as *const u8, n) == f.as_bytes())
        });
        let (has, flaming) = (carries(&OVERHEAT), carries(&FLAMING));
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let dead = cur == "dead" || cur == "oh_dead";
        let hot = forms.form(world, key, has, dead);
        let look = (world, key, hot, flaming && !dead);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            let what = match (look.3, hot) {
                (true, true) => "FLAMING (red-hot after)",
                (true, false) => "FLAMING",
                (false, true) => "RED-HOT",
                _ => "plain",
            };
            wlog(format!("world {world:#x} Rumble #{key}: {what} (playing {cur}{})",
                if dead && hot && !has { ", look remembered" } else { "" }));
        }
        let Some(want) = anim_for(cur, hot, flaming && !dead) else { continue };
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
        match game_places::hook::add("league_rumble", dress) {
            Ok((slot, prev)) => wlog(format!(
                "whole-body red-hot on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("whole-body red-hot off ({e}): only his overheated attacks are red-hot")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_heat() {
        assert_eq!(anim_for("idle", true, false).as_deref(), Some("oh_idle"));
        assert_eq!(anim_for("run", true, false).as_deref(), Some("oh_run"));
        assert_eq!(anim_for("hit", true, false).as_deref(), Some("oh_hit"));
        assert_eq!(anim_for("dead", true, false).as_deref(), Some("oh_dead"));
        assert_eq!(anim_for("attack", true, false).as_deref(), Some("oh_attack")); // the attack's first tick
        assert_eq!(anim_for("oh_attack", true, false), None); // the data's own swing
        assert_eq!(anim_for("ult", true, false), None); // The Equalizer: his plain launch
        assert_eq!(anim_for("oh_idle", false, false).as_deref(), Some("idle")); // cooled down
        assert_eq!(anim_for("oh_run", false, false).as_deref(), Some("run"));
        assert_eq!(anim_for("idle", false, false), None);
        assert_eq!(anim_for("skill", false, false), None);
    }

    #[test]
    fn flamespitter_on_the_move() {
        assert_eq!(anim_for("run", false, true).as_deref(), Some("q_run"));
        assert_eq!(anim_for("idle", false, true).as_deref(), Some("q_stand"));
        assert_eq!(anim_for("q_run", false, true), None);
        assert_eq!(anim_for("skill", false, true), None); // the aim: the data's own skill frames
        assert_eq!(anim_for("attack", false, true), None); // he may swing while it burns: his plain swing
        assert_eq!(anim_for("hit", false, true), None);
        // the burst over: back to plain, or red-hot when he overheated meanwhile (the fire first while both)
        assert_eq!(anim_for("q_run", false, false).as_deref(), Some("run"));
        assert_eq!(anim_for("q_stand", false, false).as_deref(), Some("idle"));
        assert_eq!(anim_for("run", true, true).as_deref(), Some("q_run"));
        assert_eq!(anim_for("oh_run", true, true).as_deref(), Some("q_run"));
        assert_eq!(anim_for("q_run", true, false).as_deref(), Some("oh_run"));
    }

    #[test]
    fn the_corpse_keeps_the_heat_and_the_respawn_is_plain() {
        let mut f = Forms::default();
        assert!(!f.form(1, 7, false, false));
        assert!(f.form(1, 7, true, false)); // overheated
        assert!(f.form(1, 7, false, true)); // dead: the buff is gone, still red-hot
        assert!(!f.form(1, 7, false, false)); // respawned plain
        assert!(!f.form(1, 8, false, true)); // another Rumble, never seen red-hot
    }

    /// Every tag the swap writes is in his sheet (the battlefield's hd_ frames too: league.dll maps each tag to hd_<tag>).
    #[test]
    fn his_sheet_has_every_tag_swapped_in() {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../league/champions/league_rumble#anim.fanim");
        let fanim = std::fs::read_to_string(path).unwrap();
        for t in FORM_TAGS {
            for tag in [format!("{PREFIX}{t}"), format!("hd_{PREFIX}{t}")] {
                assert!(fanim.contains(&format!("\"{tag}\"")), "no {tag}");
            }
        }
        for (_, t) in FLAME_TAGS {
            for tag in [t.to_string(), format!("hd_{t}")] {
                assert!(fanim.contains(&format!("\"{tag}\"")), "no {tag}");
            }
        }
    }
}
