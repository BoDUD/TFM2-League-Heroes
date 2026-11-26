//! 虚空形态跑起来：附加包每 tick 用 `entity_set_pos` 把形态挪向最近的敌方英雄，引擎自己的单位 AI 只有 1 的移速——它画的
//! 是 idle 还是 run，要看引擎怎么想。这里照伊莉丝的整身蜘蛛（league_elise view.rs，game_places::hook 的显示钩子）：显示世界
//! 里名字是 `league_kogmaw_void` 的实体，身上有本包每 tick 续上的 `league_kogmaw_void_go`（正在走）时，正在播的 `idle` 换成
//! `run`；没有它（站着等时间、已经炸了）时 `run` 换成 `idle`。别的动作（hit、dead、attack）不碰。高清帧不用另管：league.dll
//! 把登记单位动画表里每个动作就地换成它的 hd_ 帧（addons/hd_engine/src/lookup.rs）。
//!
//! 只在游戏 0.6.4 起的 Windows 版上生效（地址由 game_places 运行时找），别的版本什么都不做（引擎画什么就是什么）。日志每 10 秒
//! 一行：显示钩子被调了几次、形态被看到几次、引擎自己在播什么（走着 / 站着各几次 run / idle / 别的）、换了几次——下一局能看出
//! 引擎本来画不画跑。

use std::sync::{Mutex, Once};

use game_places::hook::{Ent, ANIM_CAP, ANIM_LEN, ANIM_PTR, BUFFS_LEN, BUFFS_PTR, BUFF_SIZE, NAME_LEN_AT, NAME_PTR, VALUE};

use super::{wlog, GO, UNIT};

/// The animation the form should show for the one playing (`cur`) and whether it is walking (the flag on it): None when
/// it is right as it is.
pub fn anim_for(cur: &str, moving: bool) -> Option<&'static str> {
    match (cur, moving) {
        ("idle", true) => Some("run"),
        ("run", false) => Some("idle"),
        _ => None,
    }
}

/// What the engine played, seen in a window of 10 s: walking (run, idle, other), standing (run, idle, other).
#[derive(Default)]
struct Stats {
    calls: u64,
    seen: u64,
    played: [u64; 6],
    to_run: u64,
    to_idle: u64,
    last: Option<std::time::Instant>,
    looks: Vec<(usize, u64)>,
}

static STATS: Mutex<Option<Stats>> = Mutex::new(None);
static HOOK: Once = Once::new();

#[cfg(windows)]
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

fn flush(st: &mut Stats) {
    if st.seen > 0 {
        let p = st.played;
        wlog(format!(
            "VOID DRAW: display handler {} calls, the form seen {} times in 10 s - walking: the engine played run {} idle {} other {}; \
             standing: run {} idle {} other {}; swapped idle->run {}, run->idle {}",
            st.calls, st.seen, p[0], p[1], p[2], p[3], p[4], p[5], st.to_run, st.to_idle
        ));
    }
    let (calls, last, looks) = (0, st.last, std::mem::take(&mut st.looks));
    *st = Stats { calls, last, looks, ..Stats::default() };
}

/// Every void form in the display world: walking (the flag on it) shows `run`, standing `idle`.
#[cfg(windows)]
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut guard) = STATS.try_lock() else { return };
    let st = guard.get_or_insert_with(Stats::default);
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        flush(st);
        st.last = Some(now);
    }
    let name = UNIT.as_bytes();
    for e in ents {
        let v = e.elem + VALUE;
        if q(v + NAME_LEN_AT) != name.len() {
            continue;
        }
        let ptr = q(v + NAME_PTR);
        if !plausible(ptr) || std::slice::from_raw_parts(ptr as *const u8, name.len()) != name {
            continue;
        }
        let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
        let moving = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == GO.len() && std::slice::from_raw_parts(p as *const u8, n) == GO.as_bytes()
        });
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        st.seen += 1;
        let col = match cur {
            "run" => 0,
            "idle" => 1,
            _ => 2,
        };
        st.played[col + if moving { 0 } else { 3 }] += 1;
        let look = (world, e.key);
        if !st.looks.contains(&look) {
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("VOID DRAW world {world:#x} form #{}: first drawn playing {cur} ({})", e.key,
                         if moving { "walking" } else { "standing" }));
        }
        let Some(want) = anim_for(cur, moving) else { continue };
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
        if want == "run" {
            st.to_run += 1;
        } else {
            st.to_idle += 1;
        }
    }
}

/// At load (once a process): the display hook on, when this game's display slot is found.
pub fn install_once() {
    HOOK.call_once(|| {
        #[cfg(windows)]
        match game_places::hook::add("league_kogmaw", dress, |m: &str| wlog(m)) {
            Ok(p) => wlog(format!(
                "VOID DRAW on: {p} - the walking form shows run, the \
                 standing one idle",
            )),
            Err(e) => wlog(format!("VOID DRAW off ({e}): the form shows what the engine plays")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_walking_form_runs_and_the_standing_one_idles() {
        assert_eq!(anim_for("idle", true), Some("run"));
        assert_eq!(anim_for("run", true), None);
        assert_eq!(anim_for("run", false), Some("idle"));
        assert_eq!(anim_for("idle", false), None);
        for other in ["hit", "dead", "attack"] {
            assert_eq!(anim_for(other, true), None, "{other}");
            assert_eq!(anim_for(other, false), None, "{other}");
        }
    }

    #[test]
    fn every_swapped_tag_is_in_the_forms_sheet() {
        let fanim = include_str!("../../../league/champions/league_kogmaw_void#anim.fanim");
        for t in ["idle", "run", "hit", "dead", "attack"] {
            for name in [t.to_string(), format!("hd_{t}")] {
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_kogmaw_void#anim.fanim");
            }
        }
    }
}
