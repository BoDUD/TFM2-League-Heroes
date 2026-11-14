//! 有某个状态时，整套「游戏自己按名字播」的动作换成另一套（0.9.38，2026-11-14）。
//!
//! 用户看了「和英雄联盟不一样的地方」的清单后说「全改吧」，其中一类是「开大以后出招是大招的样子，站着、跑着、挨打还是
//! 平时的样子」：出招的动作数据自己能换（`CasterAnimation`），待机、移动、受击是游戏按名字 idle / run / hit 自动播的，
//! 数据换不了。以前每个这样的英雄各带一个附加包来换（斯维因、凯隐、内瑟斯……，各自的 src/view.rs）；主包里没有附加包的
//! 英雄（锐雯）就一直是「开大后站着还拿断剑」。这里把它做成主包 league.dll 的一张表 [`LOOKS`]：英雄 id、身上有哪个
//! buff（任意一个）、哪些动作名换成哪些——图里要有换上去的那套帧（带 hd_ 的）。只开主包也生效。
//!
//! 做法和那些附加包一样（照 league_swain 的 view.rs）：游戏的显示世界每帧调用显示处理表里的更新函数，game_places 在运行
//! 时找到它的槽（[`game_places::hook`]），本 DLL 的函数接在后面，走一遍显示世界的实体表；名字在表里的实体，身上有那个
//! buff 就把正在播的动作名换过去，buff 没了（时间到、阵亡）换回来。画面实体的 buff 就是屏幕上这一刻的。新名字用游戏同一个
//! 堆（GetProcessHeap）分配，旧的照游戏的做法释放。认不得的游戏版本、Mac / Linux 什么都不做，英雄照旧。
//!
//! 已经由自己的附加包换形态的英雄不进这张表（两边都换同一个名字不会出错，但一个英雄只该有一处管）。

/// (英雄 id, 身上的 buff——任意一个, [(游戏播的动作名, 换成的动作名)])。
///
/// 锐雯的放逐之刃（`league_riven_r`，15 秒）：英雄联盟里整段时间剑都是重铸的；她出招的 `*_r` 动作数据自己播，站着、
/// 跑着、挨打换成 `rf_idle` / `rf_run` / `rf_hit`（tools/art/rig_riven_hd.py 的 R_STAND：同样的帧，断剑换成重铸剑）。
///
/// 剑魔的大灭（`league_aatrox_r`，10 秒，击杀续上；用户 10-04：「剑魔的大招应该一直在天上的吧？」）：英雄联盟里整段大招
/// 他都飞在空中，只有 Q 砸地时落下。他开大的出招 `*_r` 数据自己播，原来起手离地、收招落回地面，不出招时脚在地上；
/// 现在站着、跑着、挨打换成 `r_idle` / `r_run` / `r_hit`——每一帧都是开大出招的收尾帧（展开翅膀的待机）整帧抬高
/// 7 游戏像素（tools/art/hover_aatrox.py，不重画、不缩放），悬停不上下摆动；变身 `ult` 换成 `r_ult`：前 5 帧相同，
/// 最后 3 帧停在悬停的高度、不落地（选人卡和待机小动作还播原来的 `ult`）。看的是 `league_aatrox_r` 而不是翅膀光环的
/// `league_aatrox_r_look`：后者出招时拿掉、收招时才挂回来，差一个 tick 就会落地闪一下。
pub const LOOKS: &[(&str, &[&str], &[(&str, &str)])] = &[
    ("league_riven", &["league_riven_r"], &[("idle", "rf_idle"), ("run", "rf_run"), ("hit", "rf_hit")]),
    ("league_aatrox", &["league_aatrox_r"], &[("idle", "r_idle"), ("run", "r_run"), ("hit", "r_hit"), ("ult", "r_ult")]),
];

/// 正在播的动作名 + 这个状态在不在 → 该播的名字（不用换就是 None）。状态没了时把换上去的名字换回来。
pub fn swap(pairs: &[(&'static str, &'static str)], cur: &str, on: bool) -> Option<&'static str> {
    if on {
        pairs.iter().find(|p| p.0 == cur).map(|p| p.1)
    } else {
        pairs.iter().find(|p| p.1 == cur).map(|p| p.0)
    }
}

/// 表里这个名字的行。
pub fn row(name: &[u8]) -> Option<&'static (&'static str, &'static [&'static str], &'static [(&'static str, &'static str)])> {
    LOOKS.iter().find(|l| l.0.as_bytes() == name)
}

#[cfg(windows)]
mod hook {
    use std::sync::{Mutex, Once};

    use game_places::hook::{Ent, ANIM_CAP, ANIM_LEN, ANIM_PTR, BUFFS_LEN, BUFFS_PTR, BUFF_SIZE, NAME_LEN_AT, NAME_PTR, VALUE};

    use super::{row, swap, LOOKS};
    use crate::wlog;

    /// LOOK lines a game start (a hero's look changing: twice a cast).
    const LINES: usize = 80;

    struct Stats {
        writes: u64,
        last: Option<std::time::Instant>,
        /// (display world, entity, on) last logged: a line only when it changes
        looks: Vec<(usize, u64, bool)>,
        lines: usize,
    }

    static STATS: Mutex<Stats> = Mutex::new(Stats { writes: 0, last: None, looks: Vec::new(), lines: 0 });
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

    /// 显示世界里表上的每个英雄：按身上的 buff 换正在播的动作名。
    unsafe fn dress(world: usize, ents: &[Ent]) {
        let Ok(mut st) = STATS.try_lock() else { return };
        let now = std::time::Instant::now();
        if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 30.0) {
            if st.last.is_some() && st.writes > 0 {
                wlog(format!("LOOK {} animation names swapped in 30 s", st.writes));
            }
            st.last = Some(now);
            st.writes = 0;
        }
        for e in ents {
            let v = e.elem + VALUE;
            let n = q(v + NAME_LEN_AT);
            if !(8..=40).contains(&n) {
                continue;
            }
            let ptr = q(v + NAME_PTR);
            if !plausible(ptr) {
                continue;
            }
            let Some(&(id, buffs, pairs)) = row(std::slice::from_raw_parts(ptr as *const u8, n)) else { continue };
            let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
            let on = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
                let b = bp + k * BUFF_SIZE;
                let (p, len) = (q(b + 8), q(b + 0x10));
                plausible(p) && buffs.iter().any(|w| len == w.len() && std::slice::from_raw_parts(p as *const u8, len) == w.as_bytes())
            });
            let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
            if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
                continue;
            }
            let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
            let look = (world, e.key, on);
            if !st.looks.contains(&look) {
                let known = st.looks.iter().any(|l| l.0 == world && l.1 == e.key);
                st.looks.retain(|l| !(l.0 == world && l.1 == e.key));
                st.looks.push(look);
                if st.looks.len() > 64 {
                    st.looks.remove(0);
                }
                // a hero first seen without the buff is not news; the look coming and going is
                if (on || known) && st.lines < LINES {
                    st.lines += 1;
                    wlog(format!("LOOK display world {world:#x} {id} #{}: {} (playing {cur})", e.key,
                        if on { "the buff is on - its own stand / run / hit frames" } else { "back to the plain frames" }));
                }
            }
            let Some(want) = swap(pairs, cur, on) else { continue };
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

    /// 加载时换槽（一个进程只换一次）；表是空的就不挂。
    pub fn install_once() {
        if LOOKS.is_empty() {
            return;
        }
        HOOK.call_once(|| match game_places::hook::add("league_main_looks", dress) {
            Ok((slot, prev)) => wlog(format!(
                "LOOK whole-body looks on for {} heroes: display slot {slot:#x} now calls league.dll, then {} ({prev:#x})",
                LOOKS.len(),
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("LOOK whole-body looks off ({e}): between casts these heroes keep their plain frames")),
        });
    }
}

#[cfg(windows)]
pub use hook::install_once;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_buff() {
        let pairs: &[(&str, &str)] = &[("idle", "rf_idle"), ("run", "rf_run"), ("hit", "rf_hit")];
        assert_eq!(swap(pairs, "idle", true), Some("rf_idle"));
        assert_eq!(swap(pairs, "run", true), Some("rf_run"));
        assert_eq!(swap(pairs, "hit", true), Some("rf_hit"));
        assert_eq!(swap(pairs, "rf_idle", true), None); // already swapped
        assert_eq!(swap(pairs, "attack_r", true), None); // the data plays her casts itself
        assert_eq!(swap(pairs, "dead", true), None);
        assert_eq!(swap(pairs, "rf_run", false), Some("run")); // the buff is over
        assert_eq!(swap(pairs, "idle", false), None);
        assert_eq!(swap(pairs, "ult", false), None);
    }

    #[test]
    fn a_row_is_found_by_the_entity_s_name() {
        assert!(row(b"league_riven").is_some());
        assert!(row(b"league_rive").is_none());
        assert!(row(b"league_riven_x").is_none());
        assert!(row(b"league_aatrox").is_some());
    }

    /// Aatrox in World Ender: standing, running and reeling hover (the R casts' last frame lifted), the transformation
    /// settles on the hover instead of landing; his casts (attack_r ...) are the kit's own, untouched; the plain ult
    /// comes back when R is over.
    #[test]
    fn aatrox_hovers_through_world_ender() {
        let (_, buffs, pairs) = *row(b"league_aatrox").unwrap();
        assert_eq!(buffs, &["league_aatrox_r"]);
        assert_eq!(swap(pairs, "idle", true), Some("r_idle"));
        assert_eq!(swap(pairs, "run", true), Some("r_run"));
        assert_eq!(swap(pairs, "hit", true), Some("r_hit"));
        assert_eq!(swap(pairs, "ult", true), Some("r_ult"));
        assert_eq!(swap(pairs, "attack_r", true), None);
        assert_eq!(swap(pairs, "q3_r", true), None);
        assert_eq!(swap(pairs, "dead", true), None);
        assert_eq!(swap(pairs, "r_ult", false), Some("ult"));
        assert_eq!(swap(pairs, "r_idle", false), Some("idle"));
        // r_ult is ult with its last frames on the hover: as many frames, the same timing (a swap mid-play keeps its place)
        let fanim = crate::hd::HEROES.iter().find(|h| h.0 == "league_aatrox").unwrap().2;
        let durations = |tag: &str| -> Vec<String> {
            let at = fanim.find(&format!("\"{tag}\":")).unwrap_or_else(|| panic!("no {tag}"));
            let body = &fanim[at..at + fanim[at..].find("]}").unwrap()];
            body.match_indices("\"duration\":").map(|(i, _)| body[i + 11..].split(',').next().unwrap().to_string()).collect()
        };
        for (from, to) in [("ult", "r_ult"), ("hd_ult", "hd_r_ult"), ("lo_ult", "lo_r_ult")] {
            assert_eq!(durations(from), durations(to), "{to}");
        }
    }

    /// Every row: the hero is a dense hero of this pack, its main pack data lays each buff under that name, every tag
    /// drawn instead is in its sheet with a dense twin (and so is the tag it stands in for), no tag is both a source
    /// and a target, and the hero has one row.
    #[test]
    fn every_row_s_buffs_and_frames_exist() {
        let table = crate::hd::table();
        for (i, &(id, buffs, pairs)) in LOOKS.iter().enumerate() {
            assert!(LOOKS[..i].iter().all(|l| l.0 != id), "{id} has two rows");
            let fanim = table.heroes.iter().find(|h| h.0 == id).unwrap_or_else(|| panic!("{id} is no dense hero of this pack")).2;
            let path = format!("{}/../../league/champion/{id}.data_champion", env!("CARGO_MANIFEST_DIR"));
            let data = std::fs::read_to_string(&path).unwrap_or_else(|e| panic!("{path}: {e}"));
            assert!(!buffs.is_empty() && !pairs.is_empty());
            for b in buffs {
                assert!(data.contains(&format!("\"name\": \"{b}\"")), "the main pack never gives {id} {b}");
            }
            for &(from, to) in pairs {
                for name in [from.to_string(), to.to_string(), format!("hd_{from}"), format!("hd_{to}")] {
                    assert!(fanim.contains(&format!("\"{name}\":")), "{name} is not in {id}'s sheet");
                }
                assert!(pairs.iter().all(|p| p.0 != to && p.1 != from), "{id}: {from} / {to} is both a source and a target");
            }
        }
    }
}
