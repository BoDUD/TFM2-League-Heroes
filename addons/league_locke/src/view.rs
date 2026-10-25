//! W 期间整身换成 W 的样子：灵焰仪式点燃时，站着、跑着、挨打、出招都是 W 配色的洛克（第 0 步 B：深蓝 / 靛紫皮肤、白西装、
//! 发白光的眼镜）。主包只能用 `CasterAnimation` 换出招的动作，游戏按名字自动播的 idle / run / hit 数据换不了。照 league_kled 的
//! view.rs（下马整身步行，同一个显示处理表的槽，game_places::hook::add 一个接一个调用）：名字是 `league_locke` 的实体身上有
//! `league_locke_w_on` 时，正在播的 idle / run / hit / attack / skill / skill2 / ult 换成洛克图里的 `w_idle` …。死亡不换（W 随
//! 阵亡清掉）；点燃的那一下 `w` 本身不换。找不到槽时什么都不做，W 期间就是平常的样子。

use std::sync::{Mutex, Once};

use super::{wlog, W_ON};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 洛克在画面实体里的名字。
pub const NAME: &[u8] = b"league_locke";

/// W 期间有自己一套的动作（洛克图里的 `w_*`）：游戏按名字播的 idle / run / hit，和数据用 `CasterAnimation` 播的普攻、
/// 技能、大招（`attack` 也是普攻的第一 tick）。
pub const FORM_TAGS: [&str; 7] = ["idle", "run", "hit", "attack", "skill", "skill2", "ult"];
const PREFIX: &str = "w_";

/// 正在播的动画名 + W 是不是点着 → 该播的名字（不用换就是 None）。W 结束后把本包换上去的 `w_idle` 等换回来。
pub fn anim_for(cur: &str, lit: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if lit { format!("{PREFIX}{base}") } else { base.to_string() };
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

/// 显示世界里每个洛克：按身上的 W buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Locke seen {} times, {} animation names swapped in 10 s",
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
        let lit = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == W_ON.len() && std::slice::from_raw_parts(p as *const u8, n) == W_ON.as_bytes()
        });
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let look = (world, key, lit);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("world {world:#x} Locke #{key}: {} (playing {cur})", if lit { "W LOOK" } else { "plain" }));
        }
        let Some(want) = anim_for(cur, lit) else { continue };
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
        match game_places::hook::add("league_locke", dress) {
            Ok((slot, prev)) => wlog(format!(
                "W look on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("W look off ({e}): he looks the same while W lasts")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_soul_fire() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("w_idle"));
        assert_eq!(anim_for("run", true).as_deref(), Some("w_run"));
        assert_eq!(anim_for("hit", true).as_deref(), Some("w_hit"));
        assert_eq!(anim_for("attack", true).as_deref(), Some("w_attack"));
        assert_eq!(anim_for("skill2", true).as_deref(), Some("w_skill2"));
        assert_eq!(anim_for("ult", true).as_deref(), Some("w_ult"));
        assert_eq!(anim_for("w_attack", true), None); // already swapped
        assert_eq!(anim_for("w", true), None); // the ignition itself
        assert_eq!(anim_for("dead", true), None);
        assert_eq!(anim_for("w_idle", false).as_deref(), Some("idle")); // W over
        assert_eq!(anim_for("idle", false), None);
    }
}
