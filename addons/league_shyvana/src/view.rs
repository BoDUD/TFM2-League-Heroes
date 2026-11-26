//! 整身变龙：龙形时站着、跑着、挨打、阵亡也是龙（用户 2026-10-24：「龙女变成龙不能保持住？」——主包只能用
//! `CasterAnimation` 换出招的动作，游戏按名字自动播的 idle / run / hit / dead 数据换不了，龙形一停下就变回人形）。照
//! league_gnar 的 view.rs（整身变巨型，同一个显示处理表的槽，game_places::hook::add 一个接一个调用）：名字是
//! `league_shyvana` 的实体身上有龙形的 buff `league_shyvana_dg`（或龙形刚结束、还没播变回动作的 `league_shyvana_was_dg`）
//! 时，正在播的 idle / run / hit / dead / attack 换成她图里的 `d_idle` …。阵亡时 buff 清掉：尸体按倒下前那一帧的形态画。
//! 找不到槽时什么都不做，退回半变身（只有出招是龙）。
//! 0.1.1（用户 2026-10-27：「龙女变龙的时候 被击飞的时候会变回去」「落地后又变回龙」：龙形没断，是画面）：被击飞时游戏播的
//! 动画名不在 `FORM_TAGS` 里、她图里也没有（`SHEET_TAGS`），画面就画回人形；那一刻读不到龙形 buff 也会画回人形。现在
//! 一旦是龙就一直按龙画，直到游戏播出变回人形的动作（`revert`）或阵亡后复活（[`Forms::form`]）；龙形时她图里没有的
//! 动画名换成 `d_hit`（挨打的龙），每个名字记一行 `plays "<名字>" - drawn as d_hit`。
//! 0.1.3（用户 2026-11-17：「龙女的变身机制有问题 变了龙之后一直就是龙 然后会龙和人体形态之间切换」）：龙形时间到后，数据
//! 等她下一个动作才变回人形，可只有普攻播 `revert`；先放 Q、E、大招时数据也变回了人形（`restore`），却直接播人形的出招
//! （`skill` …），本包一直等不到 `revert`，就把她的待机、跑步、挨打、普攻一直画成龙，出招又是人形，两种形态来回跳。现在
//! 没有龙形 buff 时：播的是人形的出招（`HUMAN_CASTS`）就马上变回人形；在她图里有的动作上龙形 buff 连续 `LOST` 帧都不在
//! （击飞那种她图里没有的动作不算）也变回人形。

use std::sync::{Mutex, Once};

use super::{wlog, DRAGON};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。

/// 希瓦娜在画面实体里的名字。
pub const NAME: &[u8] = b"league_shyvana";

/// 游戏按名字自动播、龙形有自己一套的动作（她图里的 `d_*`）；数据用 `CasterAnimation` 播的 d_skill / d_bite / d_skill2 …
/// 本来就是龙，不碰。`attack` 是普攻第一 tick（数据下一 tick 才播 `d_attack`）。
pub const FORM_TAGS: [&str; 5] = ["idle", "run", "hit", "dead", "attack"];
const PREFIX: &str = "d_";
/// 她图里的动画名（不含 hd_ / lo_，测试对照 league_shyvana#anim.fanim）。龙形时游戏播的名字不在这里（击飞之类的状态）：
/// 画成 `STATE_TAG`。
pub const SHEET_TAGS: [&str; 23] = ["idle", "hit", "run", "attack", "skill", "skill_b", "skill2", "ult", "revert", "dead",
    "d_idle", "d_run", "d_attack", "d_skill", "d_skill_b", "d_bite", "d_skill2", "d_hit", "d_fly", "d_dead", "idle_base",
    "d_idle_base", "bp"];
pub const STATE_TAG: &str = "d_hit";
/// 龙形结束：数据让她播这个动作变回人形。
pub const REVERT: &str = "revert";
/// 人形的出招（龙形的是 `d_` 开头的）：没有龙形 buff 还在播这些，就是数据已经把她变回人形了（0.1.3）。
pub const HUMAN_CASTS: [&str; 5] = ["skill", "skill_b", "skill2", "ult", REVERT];
/// 龙形 buff 在她图里有的动作上连续这么多帧都读不到，就当龙形已经结束（显示处理约 90 帧一秒；击飞那一刻读不到的只有几帧）。
pub const LOST: u32 = 120;

/// 正在播的动画名 + 是不是龙 → 该播的名字（不用换就是 None）。人形时把本包换上去的 `d_idle` 等换回来。
pub fn anim_for(cur: &str, dragon: bool) -> Option<String> {
    if dragon && !SHEET_TAGS.contains(&cur) {
        return Some(STATE_TAG.to_string());
    }
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if dragon { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

/// 每个希瓦娜记下的形态：(显示世界, 实体号, 龙, 播过 dead, 龙形 buff 连续读不到的帧数)。
#[derive(Default)]
pub struct Forms {
    seen: Vec<(usize, u64, bool, bool, u32)>,
}

impl Forms {
    /// 这一帧该画的形态（`cur`：正在播的动画名）：龙形 buff 在就是龙；不在时照记下的——一旦是龙就一直是龙（被击飞那一刻
    /// 读不到 buff 也一样），直到播出 `REVERT`（龙形结束）或阵亡后复活；播 dead 时尸体按记下的形态。
    pub fn form(&mut self, world: usize, key: u64, has_buff: bool, cur: &str) -> bool {
        let dead = cur == "dead" || cur == "d_dead";
        let i = match self.seen.iter().position(|e| e.0 == world && e.1 == key) {
            Some(i) => i,
            None => {
                self.seen.push((world, key, false, false, 0));
                if self.seen.len() > 64 {
                    self.seen.remove(0);
                }
                self.seen.len() - 1
            }
        };
        let e = &mut self.seen[i];
        if dead {
            e.3 = true;
            e.2 |= has_buff;
            e.4 = 0;
        } else if has_buff {
            (e.2, e.3, e.4) = (true, false, 0);
        } else if HUMAN_CASTS.contains(&cur) || e.3 {
            (e.2, e.3, e.4) = (false, false, 0);
        } else if e.2 && SHEET_TAGS.contains(&cur) {
            // 0.1.3: the buffs stay gone on a state of her sheet (a knock-up plays a name her sheet lacks): the dragon ended
            e.4 += 1;
            if e.4 >= LOST {
                (e.2, e.4) = (false, 0);
            }
        }
        e.2
    }
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    looks: Vec<(usize, u64, bool)>,
    /// the animation names seen in dragon form that her sheet lacks (logged once each)
    states: Vec<String>,
}

static STATS: Mutex<Stats> =
    Mutex::new(Stats { calls: 0, seen: 0, writes: 0, last: None, looks: Vec::new(), states: Vec::new() });
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

/// 显示世界里每个希瓦娜：按身上的形态 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut forms) = FORMS.try_lock() else { return };
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Shyvana seen {} times, {} animation names swapped in 10 s",
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
            plausible(p) && DRAGON.iter().any(|f| n == f.len() && std::slice::from_raw_parts(p as *const u8, n) == f.as_bytes())
        });
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let dead = cur == "dead" || cur == "d_dead";
        let dragon = forms.form(world, key, has, cur);
        if dragon && !SHEET_TAGS.contains(&cur) && !st.states.iter().any(|s| s == cur) {
            st.states.push(cur.to_string());
            wlog(format!("world {world:#x} Shyvana #{key}: plays \"{cur}\" (not in her sheet) - drawn as {STATE_TAG}"));
        }
        let look = (world, key, dragon);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("world {world:#x} Shyvana #{key}: {} (playing {cur}{})", if dragon { "DRAGON" } else { "human" },
                if dead && dragon && !has { ", form remembered" } else { "" }));
        }
        let Some(want) = anim_for(cur, dragon) else { continue };
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
        match game_places::hook::add("league_shyvana", dress, |m: &str| wlog(m)) {
            Ok(p) => wlog(format!("whole-body dragon on: {p}")),
            Err(e) => wlog(format!("whole-body dragon off ({e}): only her casts show the dragon")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_form() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("d_idle"));
        assert_eq!(anim_for("run", true).as_deref(), Some("d_run"));
        assert_eq!(anim_for("hit", true).as_deref(), Some("d_hit"));
        assert_eq!(anim_for("dead", true).as_deref(), Some("d_dead"));
        assert_eq!(anim_for("attack", true).as_deref(), Some("d_attack")); // the action's first tick
        assert_eq!(anim_for("d_attack", true), None); // the data's own cast
        assert_eq!(anim_for("d_bite", true), None);
        assert_eq!(anim_for("d_skill2", true), None);
        assert_eq!(anim_for("ult", true), None); // Dragon's Descent: the data's human leap
        assert_eq!(anim_for("revert", true), None);
        assert_eq!(anim_for("d_idle", false).as_deref(), Some("idle")); // back to human
        assert_eq!(anim_for("d_run", false).as_deref(), Some("run"));
        assert_eq!(anim_for("idle", false), None);
        assert_eq!(anim_for("skill", false), None);
        // 2026-10-27: a state her sheet lacks (the knock-up) is the hit dragon, the human state is left alone
        assert_eq!(anim_for("airborne", true).as_deref(), Some("d_hit"));
        assert_eq!(anim_for("stun", true).as_deref(), Some("d_hit"));
        assert_eq!(anim_for("airborne", false), None);
    }

    #[test]
    fn the_corpse_keeps_the_form_and_the_respawn_is_human() {
        let mut f = Forms::default();
        assert!(!f.form(1, 7, false, "idle"));
        assert!(f.form(1, 7, true, "idle")); // turned
        assert!(f.form(1, 7, false, "dead")); // dead: the buff is gone, still a dragon
        assert!(!f.form(1, 7, false, "idle")); // respawned human
        assert!(!f.form(1, 8, false, "dead")); // another Shyvana, never seen a dragon
    }

    #[test]
    fn the_dragon_stays_through_a_knock_up_until_she_reverts() {
        let mut f = Forms::default();
        assert!(f.form(1, 7, true, "d_run"));
        // knocked up: no dragon buff read this frame, an animation she has no frames for
        assert!(f.form(1, 7, false, "airborne"));
        assert!(f.form(1, 7, false, "hit"));
        assert!(f.form(1, 7, true, "d_idle")); // landed
        // the dragon ran out: the buffs go, the data plays the turn back
        assert!(!f.form(1, 7, false, "revert"));
        assert!(!f.form(1, 7, false, "idle"));
        assert!(!f.form(1, 7, false, "airborne")); // a human knocked up stays human
    }

    /// 2026-11-17: the dragon ran out and her next action was Q / E / R - the data turned her back (`restore`) without
    /// the attack's `revert`, and she was drawn a dragon for the rest of the game, her human casts in between.
    #[test]
    fn a_human_cast_after_the_dragon_turns_her_back() {
        for cast in ["skill", "skill_b", "skill2", "ult"] {
            let mut f = Forms::default();
            assert!(f.form(1, 7, true, "d_idle"));
            assert!(f.form(1, 7, true, "d_run")); // the dragon ran out: was_dg still on until her next action
            assert!(!f.form(1, 7, false, cast), "{cast}"); // the data's human cast
            assert!(!f.form(1, 7, false, "run")); // and she stays human
            assert!(!f.form(1, 7, false, "attack"));
        }
    }

    #[test]
    fn the_dragon_ends_when_its_buffs_stay_gone() {
        let mut f = Forms::default();
        assert!(f.form(1, 7, true, "d_run"));
        for k in 1..LOST {
            assert!(f.form(1, 7, false, "run"), "frame {k}"); // a moment without the buff read: still the dragon
        }
        assert!(!f.form(1, 7, false, "run")); // gone for LOST frames: human
        // a knock-up's state her sheet lacks never counts
        let mut g = Forms::default();
        assert!(g.form(1, 7, true, "d_run"));
        for _ in 0..LOST * 3 {
            assert!(g.form(1, 7, false, "airborne"));
        }
        assert!(g.form(1, 7, true, "d_idle")); // landed, still a dragon
        // the count starts again after the buff is read
        for _ in 1..LOST {
            assert!(g.form(1, 7, false, "idle"));
        }
        assert!(g.form(1, 7, true, "d_idle"));
        assert!(g.form(1, 7, false, "idle"));
    }

    #[test]
    fn the_sheet_tags_are_her_sheets() {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../league/champions/league_shyvana#anim.fanim");
        let fanim = std::fs::read_to_string(path).unwrap();
        for t in SHEET_TAGS {
            assert!(fanim.contains(&format!("\"{t}\":")), "{t} is not in her sheet");
        }
        let n = fanim.matches("\"frames\"").count();
        // every tag has an hd_ twin and the lo_ UI frames of the reel tags: the plain ones are SHEET_TAGS
        assert!(n >= SHEET_TAGS.len(), "{n} tags in the sheet");
    }

    /// Every tag the swap writes is in her sheet (the battlefield's hd_ frames too: league.dll maps each tag to hd_<tag>).
    #[test]
    fn her_sheet_has_every_dragon_tag() {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../league/champions/league_shyvana#anim.fanim");
        let fanim = std::fs::read_to_string(path).unwrap();
        for t in FORM_TAGS {
            for tag in [format!("{PREFIX}{t}"), format!("hd_{PREFIX}{t}")] {
                assert!(fanim.contains(&format!("\"{tag}\"")), "no {tag}");
            }
        }
    }
}
