//! 金克丝「罪恶快感」的冲刺跑（v0.5.0，用户 2026-11-03：「金克丝刷新被动后少了点跑步的加速动作？」）：参与击杀后前两档移速
//! buff（`SPRINT_BUFFS`，+100% 起、4 秒）还在时，她跑起来播图里的 `run_x`——慢跑的同样 8 帧、每帧 0.07 秒（步频快 1.67 倍）、
//! 上身前倾、身后两道残影（tools/art/jinx_excited_run.py）；只剩最后一档（+30%）或 buff 没了，换回慢跑 `run`。移速翻倍、
//! 腿还是慢跑的步子，看着像在地上滑。游戏按名字自动播 run，主包的数据换不了它。
//!
//! 照 league_volibear 的 view.rs：本包挂在 game_places::hook 上（显示世界每帧调用一次，凯隐、沃利贝尔等附加包也挂在这里，
//! 一个接一个调用），走一遍显示世界的实体表。名字是 `league_jinx` 的实体正在播 `run`、身上有冲刺 buff 时，动画名换成
//! `run_x`（新名字用游戏同一个堆分配，旧的照游戏的做法释放）；buff 没了换回来。两套帧数一样、每帧中心（游戏的锚点）一样，
//! 跑到一半换也接得上，脚不跳。高清帧不用另管：league.dll 把她动画表里的 run_x 就地换成 hd_run_x（addons/hd_engine）。
//! 只在游戏 0.6.4 起的 Windows 版上生效（地址由 game_places 运行时找），别的版本什么都不做，照旧播慢跑。

use std::sync::{Mutex, Once};

use super::{noted, wlog};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 金克丝在画面实体里的名字。
pub const NAME: &[u8] = b"league_jinx";
/// 冲刺的 buff：罪恶快感的前两档移速（主包的名字，`JINX_EXCITED`）——第一档 2 秒、第二档 4 秒，同时挂上。
pub const SPRINT_BUFFS: [&str; 2] = ["league_jinx_excited_ms1", "league_jinx_excited_ms2"];
pub const RUN: &str = "run";
pub const SPRINT: &str = "run_x";

/// 正在播的动画名 + 是不是在冲刺 → 该播的名字（不用换就是 None）。冲刺结束后把本包换上去的 `run_x` 换回来。
pub fn anim_for(cur: &str, sprint: bool) -> Option<&'static str> {
    match (cur, sprint) {
        (RUN, true) => Some(SPRINT),
        (SPRINT, false) => Some(RUN),
        _ => None,
    }
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的样子：变了才记一行 SPRINT。
    looks: Vec<(usize, u64, bool)>,
}

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, seen: 0, writes: 0, last: None, looks: Vec::new() });
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

/// 显示世界里每个金克丝：按身上的冲刺 buff 换正在播的跑步动画。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.writes > 0 {
            wlog(format!("display handler: {} calls, Jinx seen {} times, {} run names swapped in 10 s",
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
        let sprint = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && SPRINT_BUFFS.iter().any(|s| n == s.len() && std::slice::from_raw_parts(p as *const u8, n) == s.as_bytes())
        });
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let look = (world, key, sprint);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            if let Some(k) = noted("jinx sprint view", false) {
                wlog(format!("SPRINT display world {world:#x} Jinx #{key}: {} (playing {cur}) #{k}",
                    if sprint { "Get Excited - runs as run_x (faster, leant, afterimages)" } else { "her own jog" }));
            }
        }
        let Some(want) = anim_for(cur, sprint) else { continue };
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

/// 加载时挂上（一个进程只挂一次）。
pub fn install_once() {
    HOOK.call_once(|| {
        match game_places::hook::add("league_takedowns", dress) {
            Ok((slot, prev)) => wlog(format!(
                "SPRINT Jinx's Get Excited run on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("SPRINT off ({e}): Jinx keeps her jog through Get Excited (the main pack's look)")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn she_sprints_only_while_the_first_two_speed_boosts_last() {
        assert_eq!(anim_for("run", true), Some("run_x"));
        assert_eq!(anim_for("run_x", true), None);
        assert_eq!(anim_for("run_x", false), Some("run")); // the boost is over
        assert_eq!(anim_for("run", false), None);
        for other in ["idle", "attack", "rocket", "skill", "ult", "hit", "dead"] {
            assert_eq!(anim_for(other, true), None, "{other} is not swapped");
        }
        // the buffs are the main pack's Get Excited ones, the two that end first of the three speed boosts
        let speed: Vec<(&str, usize)> =
            super::super::JINX_EXCITED.iter().filter(|b| b.3 > 0).map(|b| (b.0, b.1)).collect();
        assert_eq!(speed.len(), 3);
        for s in SPRINT_BUFFS {
            let (_, ticks) = speed.iter().find(|b| b.0 == s).copied().unwrap_or_else(|| panic!("{s} is not a speed buff"));
            assert!(ticks < speed.iter().map(|b| b.1).max().unwrap_or(0), "{s} lasts the whole boost");
        }
    }

    #[test]
    fn the_sprint_is_in_her_sheet_frame_for_frame() {
        let fanim = include_str!("../../../league/champions/league_jinx#anim.fanim");
        let frames = |tag: &str| -> usize {
            let at = fanim.find(&format!("\"{tag}\":{{\"frames\":[")).unwrap_or_else(|| panic!("{tag} is not in league_jinx#anim.fanim"));
            let rest = &fanim[at..];
            rest[..rest.find("]}").unwrap_or(rest.len())].matches("\"duration\"").count()
        };
        for p in ["", "hd_", "lo_"] {
            assert_eq!(frames(&format!("{p}{SPRINT}")), frames(&format!("{p}{RUN}")), "{p}{SPRINT}: the jog's frame count");
        }
    }
}
