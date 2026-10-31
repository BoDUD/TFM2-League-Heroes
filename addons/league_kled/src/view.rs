//! 下马整身步行：斯嘎尔跑了以后，站着、跑着、挨打也是步行的克烈（主包只能用 `CasterAnimation` 换出招的动作，游戏按名字
//! 自动播的 idle / run / hit 数据换不了）。照 league_gnar 的 view.rs（整身变巨型，同一个显示处理表的槽，
//! game_places::hook::add 一个接一个调用）：名字是 `league_kled` 的实体身上有下马的 buff `league_kled_ft` 时，正在播的
//! idle / run / hit / attack 换成克烈图里的 `f_idle` …。死亡本来就是步行的克烈倒下（英雄联盟的 Rider_Death），不用换；
//! 阵亡时 buff 清掉，复活骑在斯嘎尔上。找不到槽时什么都不做，退回半步行（只有出招是步行的）。

use std::sync::{Mutex, Once};

use super::{wlog, FOOT};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 克烈在画面实体里的名字。
pub const NAME: &[u8] = b"league_kled";

/// 游戏按名字自动播、步行有自己一套的动作（克烈图里的 `f_*`）；数据用 `CasterAnimation` 播的 f_attack / f_skill
/// 本来就是步行，不碰。`attack` 是普攻第一 tick（数据同一 tick 播 `f_attack`）。
pub const FORM_TAGS: [&str; 4] = ["idle", "run", "hit", "attack"];
const PREFIX: &str = "f_";

/// 正在播的动画名 + 是不是步行 → 该播的名字（不用换就是 None）。骑上以后把本包换上去的 `f_idle` 等换回来。
pub fn anim_for(cur: &str, foot: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if foot { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
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

/// 显示世界里每个克烈：按身上的下马 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Kled seen {} times, {} animation names swapped in 10 s",
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
        let foot = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == FOOT.len() && std::slice::from_raw_parts(p as *const u8, n) == FOOT.as_bytes()
        });
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let look = (world, key, foot);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("world {world:#x} Kled #{key}: {} (playing {cur})", if foot { "ON FOOT" } else { "riding" }));
        }
        let Some(want) = anim_for(cur, foot) else { continue };
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
        match game_places::hook::add("league_kled", dress) {
            Ok((slot, prev)) => wlog(format!(
                "whole body on foot on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("whole body on foot off ({e}): only his casts show him on foot")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_skaarl() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("f_idle"));
        assert_eq!(anim_for("run", true).as_deref(), Some("f_run"));
        assert_eq!(anim_for("hit", true).as_deref(), Some("f_hit"));
        assert_eq!(anim_for("attack", true).as_deref(), Some("f_attack")); // the action's first tick
        assert_eq!(anim_for("f_attack", true), None); // the data's own cast
        assert_eq!(anim_for("f_skill", true), None);
        assert_eq!(anim_for("dead", true), None); // always on foot
        assert_eq!(anim_for("ult", false), None);
        assert_eq!(anim_for("f_idle", false).as_deref(), Some("idle")); // back on Skaarl
        assert_eq!(anim_for("idle", false), None);
    }
}
