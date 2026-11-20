//! 骑乘的样子：附加包的大招让她骑在华洛背上跑（副本给她挂 `league_quinn_r_ride`），骑着的时候站着、走着、挨打都画成骑乘（图里的
//! `r_idle` / `r_run` / `r_hit`）。主包只能用 `CasterAnimation` 换出招的动作，游戏按名字自动播的 idle / run / hit 数据换不了。只在游戏
//! 0.6.4（Windows）上生效，别的版本什么都不做：骑行照样加速、到时落地，画面是主包那样站着的她。
//!
//! 照 league_rammus 的 view.rs（拉莫斯的滚球 / 蜷缩整身，源自 league_reksai / league_rell / league_jayce / league_nidalee /
//! league_kayn_form）：游戏的显示世界每帧调用显示处理表里的更新函数（rva 0x23312a0），函数指针在 .rdata 的槽 rva 0x3c82db8（凯隐、
//! 佛耶戈、奈德丽、杰斯、伊莉丝、厄斐琉斯、芮尔、雷克塞、拉莫斯附加包也挂在这里，一个接一个调用）。加载时核对函数开头 24 个字节，
//! 把槽换成本包的函数：先调用槽里原来的函数，再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始：+0x40 名字，
//! +0x68 / +0x70 / +0x78 正在播的动画名，+0xb8 / +0xc0 buff 列表）。名字是 `league_quinn` 的实体身上有骑乘 buff 时，正在播的 idle /
//! run / hit 换成 `r_*`（新名字用游戏同一个堆分配，旧的照游戏的做法释放）。高清帧不用另管：league.dll 把登记英雄动画表里每个动作
//! （r_idle 也在内）就地换成它的 hd_ 帧（addons/hd_engine/src/lookup.rs）。
//!
//! 后空翻（0.7.0，用户 2026-11-20：「奎因E往后拉距离为什么还是没动画」）：旋翔掠杀踢中后本包把她往后挪 20 tick，这段时间
//! 游戏看来不往下播强制动作（从游戏里两版的样子推的），画面停在第一帧，挪完才把剩下的几帧一闪播掉。lib.rs 每 tick 给她挂这一帧的标记
//! `league_quinn_flip<k>`，这里看到就把正在播的动画换成单帧标签 `e_flip_<k>`（图里 e_flip 第 k 帧的复制，
//! tools/art/rig_quinn.py 的 FLIP_ONE）：一个标签只有一帧，停不停都是这一帧。标记没了、画面还停在单帧标签上，就换回游戏
//! 自己最后写进来的名字。

use std::sync::{Mutex, Once};

use super::{flip_buff, wlog, FLIP_MS, RIDE};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。

/// 奎因在画面实体里的名字。
pub const NAME: &[u8] = b"league_quinn";

/// 游戏按名字自动播、骑乘时另有一套的动作：待机、走、挨打。普攻、技能、阵亡不换（骑着出招就是鹰翼天翔落地）。
pub const FORM_TAGS: [&str; 3] = ["idle", "run", "hit"];
const PREFIX: &str = "r_";

/// 正在播的动画名 + 是否骑着 → 该播的名字（不用换就是 None）。下来以后把本包换上去的 `r_idle` 等换回来。
pub fn anim_for(cur: &str, riding: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if riding { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

/// 后空翻第 `k` 帧的单帧标签。
pub fn flip_tag(k: usize) -> String {
    format!("e_flip_{k}")
}

/// 是不是本包换上去的单帧标签（e_flip_0 … e_flip_6）。
pub fn is_flip_tag(s: &str) -> bool {
    s.strip_prefix("e_flip_").is_some_and(|d| !d.is_empty() && d.bytes().all(|b| b.is_ascii_digit()))
}

/// 正在播的 `cur`、正在翻第几帧（`flip`）、骑没骑着、游戏自己最后写进来的名字 `base` → 该播的名字（不用换是 None）。
/// 翻着就画这一帧；翻完了画面还停在单帧标签上，换回 `base`（没有就站着）；别的时候照骑乘换。
pub fn want_anim(cur: &str, flip: Option<usize>, riding: bool, base: Option<&str>) -> Option<String> {
    match flip {
        Some(k) => {
            let w = flip_tag(k);
            (w != cur).then_some(w)
        }
        None if is_flip_tag(cur) => Some(base.filter(|b| !is_flip_tag(b)).unwrap_or("idle").to_string()),
        None => anim_for(cur, riding),
    }
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的形态：变了才记一行 FORM。
    looks: Vec<(usize, u64, bool)>,
    /// 每个（显示世界, 实体号）：游戏自己最后写进来的动画名、上一帧是不是在翻（翻的开头和结尾各记一行 FLIP）。
    games: Vec<(usize, u64, String, bool)>,
}

static STATS: Mutex<Stats> =
    Mutex::new(Stats { calls: 0, seen: 0, writes: 0, last: None, looks: Vec::new(), games: Vec::new() });
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

/// 显示世界里每个奎因：按身上的骑乘 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Quinn seen {} times, {} animation names swapped in 10 s",
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
        let has = |name: &str| plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == name.len() && std::slice::from_raw_parts(p as *const u8, n) == name.as_bytes()
        });
        let form = has(RIDE);
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let look = (world, key, form);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            if let Some(k) = super::counted("form_view") {
                wlog(format!("FORM display world {world:#x} Quinn #{key}: {} (playing {cur}) #{k}", if form {
                    "RIDING Valor - idle/run/hit drawn as r_*"
                } else {
                    "on foot"
                }));
            }
        }
        let flip = (0..FLIP_MS.len()).find(|&k| has(&flip_buff(k)));
        // 游戏自己写进来的名字（不是本包换上去的单帧标签）记下来：翻完了换回它
        let gi = match st.games.iter().position(|g| g.0 == world && g.1 == key) {
            Some(i) => i,
            None => {
                st.games.push((world, key, String::new(), false));
                if st.games.len() > 64 {
                    st.games.remove(0);
                }
                st.games.len() - 1
            }
        };
        if !is_flip_tag(cur) && st.games[gi].2 != cur {
            st.games[gi].2 = cur.to_string();
        }
        if st.games[gi].3 != flip.is_some() {
            st.games[gi].3 = flip.is_some();
            if let Some(k) = super::counted("flip_view") {
                wlog(format!("FLIP display world {world:#x} Quinn #{key}: {} (the game plays {}) #{k}",
                             if flip.is_some() { "drawn frame by frame (e_flip_0 ...)" } else { "over" }, st.games[gi].2));
            }
        }
        let base = st.games[gi].2.clone();
        let Some(want) = want_anim(cur, flip, form, Some(base.as_str()).filter(|b| !b.is_empty())) else { continue };
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
        match game_places::hook::add("league_quinn", dress) {
            Ok((slot, prev)) => wlog(format!(
                "FORM riding body on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM riding body off ({e}): she stands on screen while riding (the main pack's look)")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_ride() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("r_idle"));
        assert_eq!(anim_for("run", true).as_deref(), Some("r_run"));
        assert_eq!(anim_for("hit", true).as_deref(), Some("r_hit"));
        assert_eq!(anim_for("r_run", false).as_deref(), Some("run")); // she got off
        assert_eq!(anim_for("r_idle", true), None);
        assert_eq!(anim_for("attack", true), None);
        assert_eq!(anim_for("ult_ride", true), None); // the main pack's own ride
        assert_eq!(anim_for("idle", false), None);
    }

    #[test]
    fn every_swapped_tag_is_in_her_sheet() {
        let fanim = include_str!("../../../league/champions/league_quinn#anim.fanim");
        for t in FORM_TAGS {
            for p in ["", "r_", "hd_", "hd_r_"] {
                let name = format!("{p}{t}");
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_quinn#anim.fanim");
            }
        }
        // 后空翻的单帧标签：每个只有一帧，高清的也在
        for k in 0..FLIP_MS.len() {
            for p in ["", "hd_"] {
                let name = format!("\"{p}{}\":{{\"frames\":[{{", flip_tag(k));
                let at = fanim.find(&name).unwrap_or_else(|| panic!("{p}{} is not in league_quinn#anim.fanim", flip_tag(k)));
                let rest = &fanim[at + name.len()..];
                let one = &rest[..rest.find("]}").unwrap()];
                assert_eq!(one.matches("\"duration\"").count(), 1, "{p}{} is not one frame", flip_tag(k));
            }
        }
    }

    #[test]
    fn the_flip_is_drawn_frame_by_frame_then_handed_back() {
        // 翻着：不管游戏在播什么（冲刺、e_flip、走路）都画这一帧
        assert_eq!(want_anim("e_flip", Some(0), false, Some("e_flip")).as_deref(), Some("e_flip_0"));
        assert_eq!(want_anim("skill2", Some(2), false, Some("skill2")).as_deref(), Some("e_flip_2"));
        assert_eq!(want_anim("e_flip_2", Some(3), false, Some("e_flip")).as_deref(), Some("e_flip_3"));
        assert_eq!(want_anim("e_flip_3", Some(3), false, Some("e_flip")), None);
        assert_eq!(want_anim("r_idle", Some(1), true, Some("r_idle")).as_deref(), Some("e_flip_1"));
        // 翻完：换回游戏自己最后写进来的名字，没有就站着
        assert_eq!(want_anim("e_flip_6", None, false, Some("idle")).as_deref(), Some("idle"));
        assert_eq!(want_anim("e_flip_6", None, false, Some("e_flip")).as_deref(), Some("e_flip"));
        assert_eq!(want_anim("e_flip_6", None, false, None).as_deref(), Some("idle"));
        // 不翻的时候照骑乘
        assert_eq!(want_anim("idle", None, true, Some("idle")).as_deref(), Some("r_idle"));
        assert_eq!(want_anim("e_flip", None, false, Some("e_flip")), None);
        assert!(is_flip_tag("e_flip_0") && is_flip_tag("e_flip_12"));
        assert!(!is_flip_tag("e_flip") && !is_flip_tag("e_flip_") && !is_flip_tag("hd_e_flip_1") && !is_flip_tag("e_flip_x"));
    }
}
