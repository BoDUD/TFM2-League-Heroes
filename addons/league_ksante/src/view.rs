//! 全盛姿态的整身：大招让他进入全盛（主包数据给他挂 `league_ksante_ao`），全盛时站着、走着、挨打也是弓背半蹲、两根长棍拖地的样子（图里的
//! `ao_idle` / `ao_run` / `ao_hit`）。主包只能用 `CasterAnimation` 换出招的动作，游戏按名字自动播的 idle / run / hit 数据换不了。
//!
//! 照 league_quinn 的 view.rs（骑乘整身，源自 league_rammus / league_reksai / league_rell / league_jayce / league_nidalee /
//! league_kayn_form）：game_places::hook::add 把本包的函数挂进显示处理表的槽（游戏版本不同地址不同，由 game_places 在加载时找），
//! 一个接一个调用：走一遍显示世界的实体表，名字是 `league_ksante` 的实体身上有全盛 buff 时，正在播的 idle / run / hit / attack 换成
//! `ao_*`（`attack` 是普攻第一 tick：数据下一 tick 才播 `ao_attack`，league_gnar 的做法）。全盛结束把换上去的 `ao_*` 换回来。高清帧不用另管：
//! league.dll 把登记英雄动画表里每个动作（ao_idle 也在内）就地换成它的 hd_ 帧（addons/league_main/src/lookup.rs）。阵亡不换：全盛随
//! 死亡结束，倒下的是普通姿态。

use std::sync::{Mutex, Once};

use super::{wlog, ALL_OUT};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 奎桑提在画面实体里的名字。
pub const NAME: &[u8] = b"league_ksante";

/// 游戏按名字自动播、全盛另有一套的动作：待机、走、挨打，和普攻的第一 tick。技能本来就由数据按姿态播，阵亡不换。
pub const FORM_TAGS: [&str; 4] = ["idle", "run", "hit", "attack"];
const PREFIX: &str = "ao_";

/// 正在播的动画名 + 是否全盛 → 该播的名字（不用换就是 None）。全盛结束把本包换上去的 `ao_idle` 等换回来。
pub fn anim_for(cur: &str, all_out: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if all_out { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的姿态：变了才记一行 FORM。
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

/// 显示世界里每个奎桑提：按身上的全盛 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, K'Sante seen {} times, {} animation names swapped in 10 s",
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
        let form = has(ALL_OUT);
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
                wlog(format!("FORM display world {world:#x} K'Sante #{key}: {} (playing {cur}) #{k}", if form {
                    "ALL OUT - idle/run/hit/attack drawn as ao_*"
                } else {
                    "base stance"
                }));
            }
        }
        let Some(want) = anim_for(cur, form) else { continue };
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
        match game_places::hook::add("league_ksante", dress) {
            Ok((slot, prev)) => wlog(format!(
                "FORM All Out body on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM All Out body off ({e}): he stands in the base stance between All Out's casts (the main pack's look)")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_all_out() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("ao_idle"));
        assert_eq!(anim_for("run", true).as_deref(), Some("ao_run"));
        assert_eq!(anim_for("hit", true).as_deref(), Some("ao_hit"));
        assert_eq!(anim_for("attack", true).as_deref(), Some("ao_attack")); // the action's first tick
        assert_eq!(anim_for("ao_run", false).as_deref(), Some("run")); // All Out ran out
        assert_eq!(anim_for("ao_idle", true), None);
        assert_eq!(anim_for("ao_attack", true), None); // the data's own cast
        assert_eq!(anim_for("ao_skill", true), None);
        assert_eq!(anim_for("ult", true), None);
        assert_eq!(anim_for("dead", true), None); // he falls in the base stance
        assert_eq!(anim_for("idle", false), None);
    }

    /// Checked once his sheet is exported (`league/champions/league_ksante#anim.fanim`): every swapped tag and its hd_ copy.
    #[test]
    fn every_swapped_tag_is_in_his_sheet() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../league/champions/league_ksante#anim.fanim");
        let Ok(fanim) = std::fs::read_to_string(path) else { return };
        for t in FORM_TAGS {
            for p in ["", "ao_", "hd_", "hd_ao_"] {
                let name = format!("{p}{t}");
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_ksante#anim.fanim");
            }
        }
    }
}
