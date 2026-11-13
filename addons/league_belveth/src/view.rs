//! 真身整身替换：万载豪筵的真身期间，卑尔维斯站着、滑行、挨打、普攻、Q、W 都是张开双翼飘在空中的她（图里的 `r_idle` /
//! `r_run` / `r_hit` / `r_attack` / `r_skill` / `r_skill2`）。用户 2026-11-14：「阿尔卑斯的变为真身是不是要做个变形啊
//! 和联盟一样」（「卑尔维斯」），选了「先变大再张翼」：变大在主包 league.dll 的 FORMS（league_main/src/hd.rs），张翼在这里。
//!
//! 主包的数据一个动作只有一个名字（真身里 Q、W 还是 `skill` / `skill2`），游戏按名字自动播的 idle / run / hit 数据也换不了，
//! 所以整套都在画面这边换：照 league_swain 的 view.rs（源自 league_rell / league_kayn_form）——游戏的显示世界每帧调用显示
//! 处理表里的更新函数，game_places 在运行时找到它的槽，本包的函数接在后面，走一遍显示世界的实体表：名字是
//! `league_belveth` 的实体身上有主包的 buff `league_belveth_r_on`（真身 15 秒，参与击杀续满）时，正在播的这六个动作换成
//! `r_` 开头的；buff 没了（真身结束、阵亡）换回来。大招本身（`ult`：蜷缩、展开）、风暴（`skill_e`，只有真身里才有，本来就是
//! 张翼的两帧）、阵亡（`dead`，那时 buff 已经清掉）不碰。高清帧不用另管：league.dll 把登记英雄动画表里每个动作就地换成它的
//! hd_ 帧。只在认得的游戏版本的 Windows 版上生效，别的什么都不做（她只是不张翼）。
//!
//! 真身的帧没有新画：都是 Codex 画过的姿势（tools/art/rig_belveth.py 的 TRUE）——风暴「横扫」那一帧（双翼往两边张开、尾巴
//! 卷在身下、离地）当站姿，普攻从大招「展开」那一帧（双翼高举）劈下来。每个 `r_` 动作的帧数和时长和原来的一样，游戏的
//! 出手时机不变。

use std::sync::{Mutex, Once};

use super::{wlog, FORM};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 卑尔维斯在画面实体里的名字。
pub const NAME: &[u8] = b"league_belveth";

/// 真身有自己一套的动作。
pub const FORM_TAGS: [&str; 6] = ["idle", "run", "hit", "attack", "skill", "skill2"];
pub const PREFIX: &str = "r_";
/// FORM lines a game start (her look changing: twice an ult).
const LOOK_LINES: usize = 60;

/// 正在播的动画名 + 是不是真身 → 该播的名字（不用换就是 None）。真身结束时把本包换上去的 `r_idle` 等换回来。
pub fn anim_for(cur: &str, true_form: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if true_form { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的样子：变了才记一行 FORM。
    looks: Vec<(usize, u64, bool)>,
    lines: usize,
}

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, seen: 0, writes: 0, last: None, looks: Vec::new(), lines: 0 });
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

/// 显示世界里每个卑尔维斯：按身上的真身 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.writes > 0 {
            wlog(format!("FORM display handler: {} calls, Bel'Veth seen {} times, {} animation names swapped in 10 s",
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
        let on = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
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
        let look = (world, key, on);
        if !st.looks.contains(&look) {
            let known = st.looks.iter().any(|l| l.0 == world && l.1 == key);
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            // a Bel'Veth first seen folded is not news; her true form coming and going is
            if (on || known) && st.lines < LOOK_LINES {
                st.lines += 1;
                wlog(format!("FORM display world {world:#x} Bel'Veth #{key}: {} (playing {cur})",
                    if on { "TRUE FORM - wings spread, r_* frames" } else { "folded again" }));
            }
        }
        let Some(want) = anim_for(cur, on) else { continue };
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
        match game_places::hook::add("league_belveth", dress) {
            Ok((slot, prev)) => wlog(format!(
                "FORM true-form body on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM true-form body off ({e}): in true form she only grows (league.dll), the wings stay folded")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_form() {
        for t in FORM_TAGS {
            assert_eq!(anim_for(t, true), Some(format!("r_{t}")));
            assert_eq!(anim_for(&format!("r_{t}"), false).as_deref(), Some(t)); // the form is over
            assert_eq!(anim_for(t, false), None);
            assert_eq!(anim_for(&format!("r_{t}"), true), None);
        }
        // the ult itself, the storm (true form only: its frames are spread already) and the death are hers as they are
        for t in ["ult", "skill_e", "dead", "bp", "idle_base", "stun"] {
            assert_eq!(anim_for(t, true), None);
            assert_eq!(anim_for(t, false), None);
        }
        assert_eq!(anim_for("r_ult", false), None); // never a name of ours
    }

    /// Every swapped tag is in her sheet with its dense twin, and plays as long as the tag it stands in for (the kit's
    /// ticks come from the folded form's frames: the same count and milliseconds, so nothing lands early or late).
    #[test]
    fn every_swapped_tag_is_in_her_sheet_with_the_same_timing() {
        let fanim = include_str!("../../../league/champions/league_belveth#anim.fanim");
        let durations = |tag: &str| -> Vec<String> {
            let at = fanim.find(&format!("\"{tag}\":")).unwrap_or_else(|| panic!("{tag} is not in league_belveth#anim.fanim"));
            let body = &fanim[at..];
            let end = body.find("]").expect("the tag's frames");
            body[..end].split("\"duration\":").skip(1).map(|s| s.trim_start().split([',', '}', '\n', '\r']).next().unwrap().trim().to_string()).collect()
        };
        for t in FORM_TAGS {
            for name in [t.to_string(), format!("{PREFIX}{t}"), format!("hd_{t}"), format!("hd_{PREFIX}{t}")] {
                assert!(fanim.contains(&format!("\"{name}\":")), "{name} is not in league_belveth#anim.fanim");
            }
            if t == "idle" {
                continue; // the idle is a reel of snippets (hero_reels); the true form hovers on its own loop
            }
            let (a, b) = (durations(&format!("hd_{t}")), durations(&format!("hd_{PREFIX}{t}")));
            assert!(!a.is_empty(), "{t}: no frames read");
            assert_eq!(a, b, "{t}: the true form's frames last differently");
        }
    }

    #[test]
    fn the_form_is_the_main_pack_s_buff() {
        for data in [include_str!("../../../league/champion/league_belveth.data_champion"),
                     include_str!("../override/league_belveth.data_champion")] {
            assert!(data.contains(&format!("\"name\": \"{FORM}\"")));
        }
    }
}
