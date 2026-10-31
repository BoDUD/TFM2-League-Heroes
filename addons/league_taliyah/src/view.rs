//! 脱战骑石头（用户 2026-10-26：「塔利亚怎么是飞着走路的 不对吧」，选「像英雄联盟」）：她的图里 `run` 是用脚跑，
//! `surf` 是蹲在石头上冲浪（被动浮石冲）。游戏按名字自动播 `run`，数据换不了，所以照 league_kled 的 view.rs（同一个显示
//! 处理表的槽，game_places::hook::add 一个接一个调用）：名字是 `league_taliyah` 的实体没在打架（身上没有主包的
//! `league_taliyah_fight`：打中英雄挂上，`f_t` tick 后消失），或者刚放完墙幔（`league_taliyah_r_surf`，冲着墙走）时，
//! 正在播的 `run` 换成 `surf`；打起来以后换回 `run`。看的是 `fight` 而不是主包加速用的 `surf` 标记：`surf` 要等她这一条命
//! 第一次普攻才挂上，复活后从泉水走回去那一段会变成用脚走。找不到槽时什么都不做：一直用脚跑（主包的样子）。

use std::sync::{Mutex, Once};

use super::wlog;
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 塔莉垭在画面实体里的名字。
pub const NAME: &[u8] = b"league_taliyah";
/// 打架中（主包：她打中英雄时挂上，`f_t` tick）。
pub const FIGHT: &str = "league_taliyah_fight";
/// 墙幔之后冲墙（主包：`r_surf` tick）。
pub const R_SURF: &str = "league_taliyah_r_surf";

/// 正在播的动画名 + 是不是在冲浪 → 该播的名字（不用换就是 None）。只换移动：出招、挨打、死亡、骑墙（`ult_ride`）都不碰。
pub fn anim_for(cur: &str, surfing: bool) -> Option<&'static str> {
    match (cur, surfing) {
        ("run", true) => Some("surf"),
        ("surf", false) => Some("run"),
        _ => None,
    }
}

/// 身上的 buff 名 → 在不在冲浪：没在打架，或者刚放完墙幔。
pub fn surfing<'a>(mut names: impl Iterator<Item = &'a [u8]>) -> bool {
    let (mut fight, mut r_surf) = (false, false);
    for n in names.by_ref() {
        fight |= n == FIGHT.as_bytes();
        r_surf |= n == R_SURF.as_bytes();
    }
    r_surf || !fight
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
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

/// 显示世界里每个塔莉垭：按身上的 buff 换正在播的移动动画。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Taliyah seen {} times, {} run / surf swaps in 10 s",
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
        if !plausible(bp) || bn > 256 {
            continue;
        }
        let names = (0..bn).filter_map(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            (plausible(p) && n <= 64).then(|| std::slice::from_raw_parts(p as *const u8, n))
        });
        let surf = surfing(names);
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let look = (world, key, surf);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("world {world:#x} Taliyah #{key}: {} (playing {cur})", if surf { "SURFING" } else { "on foot" }));
        }
        let Some(want) = anim_for(cur, surf) else { continue };
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
        match game_places::hook::add("league_taliyah", dress) {
            Ok((slot, prev)) => wlog(format!(
                "surf out of fights on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("surf out of fights off ({e}): she always runs on foot")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn she_surfs_out_of_fights_and_runs_in_them() {
        assert_eq!(anim_for("run", true), Some("surf"));
        assert_eq!(anim_for("surf", false), Some("run"));
        assert_eq!(anim_for("run", false), None);
        assert_eq!(anim_for("surf", true), None);
        // casts, hits, the ride on her wall, death: never touched
        for tag in ["idle", "attack", "skill", "skill2", "ult", "ult_ride", "hit", "dead"] {
            assert_eq!(anim_for(tag, true), None, "{tag}");
            assert_eq!(anim_for(tag, false), None, "{tag}");
        }
    }

    #[test]
    fn the_fight_flag_decides_and_the_wall_ride_overrides_it() {
        let s = |names: &[&str]| surfing(names.iter().map(|n| n.as_bytes()));
        assert!(s(&[]), "just back from the fountain: no surf flag yet, still surfing");
        assert!(s(&["league_taliyah_surf"]));
        assert!(!s(&["league_taliyah_fight"]));
        assert!(s(&["league_taliyah_fight", "league_taliyah_r_surf"]), "riding her wall after R");
    }

    #[test]
    fn the_names_are_the_kits() {
        let src = include_str!("../../../tools/kit/build_taliyah.py");
        for flag in ["\"fight\"", "\"r_surf\""] {
            assert!(src.contains(flag), "{flag} is gone from build_taliyah.py");
        }
        assert!(src.contains("ID = \"league_taliyah\""));
    }
}
