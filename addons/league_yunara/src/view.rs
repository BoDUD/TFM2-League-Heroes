//! 超凡形态整身换形态：芸阿娜开大招后（主包数据给她挂 `league_yunara_r_on`，15 秒），站着、跑着、普攻、挨打都是带金边和光环的她
//! （图里的 `r_idle` / `r_run` / `r_attack` / `r_hit`，后两个是 0.1.1 加的；主包只能用 `CasterAnimation` 换出招的动作，游戏按名字自动播的 idle / run 数据换不了）。只在游戏
//! 0.6.4（Windows）上生效，别的版本什么都不做：超凡形态只有主包脚下和身后的金光（view_buffs r_on）。
//!
//! 照 league_rell 的 view.rs（芮尔的下马整身，源自 league_jayce / league_nidalee / league_kayn_form）：游戏的显示世界每帧调用显示处理表
//! 里的更新函数（rva 0x23312a0），函数指针在 .rdata 的槽 rva 0x3c82db8（凯隐、佛耶戈、奈德丽、杰斯、伊莉丝、厄斐琉斯、芮尔附加包也挂在
//! 这里，一个接一个调用）。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用槽里原来的函数，再走一遍显示世界的实体表（+0x138
//! 的哈希表，每格 0x1d0 字节，值从 +8 开始：+0x40 名字，+0x68 / +0x70 / +0x78 正在播的动画名，+0xb8 / +0xc0 buff 列表）。名字是
//! `league_yunara` 的实体身上有超凡形态 buff 时，正在播的 idle / run / attack / hit 换成 `r_idle` …（新名字用游戏同一个堆分配，旧的照游戏的做法
//! 释放）。高清帧不用另管：league.dll 把登记英雄动画表里每个动作（r_idle 也在内）就地换成它的 hd_ 帧（addons/league_main/src/lookup.rs）。

use std::sync::{Mutex, Once};

use super::{wlog, R_ON as FORM};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。

/// 芸阿娜在画面实体里的名字。
pub const NAME: &[u8] = b"league_yunara";

/// 游戏按名字自动播、超凡形态有自己一套的动作（芸阿娜图里的 `r_*`）：待机、跑、普攻、挨打（0.1.1：原来普攻和挨打时金边、光环
/// 会闪掉）。阵亡不换（形态 buff 随阵亡清掉）；技能在超凡形态里数据自己播 `skill_r` / `skill2_r`（已带金边）。
pub const FORM_TAGS: [&str; 4] = ["idle", "run", "attack", "hit"];
const PREFIX: &str = "r_";

/// 正在播的动画名 + 是不是在超凡形态 → 该播的名字（不用换就是 None）。形态结束后把本包换上去的 `r_idle` 等换回来。
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
    /// 每个（显示世界, 实体号）上次记下的形态：变了才记一行 FORM。
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

/// 显示世界里每个芸阿娜：按身上的超凡形态 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Yunara seen {} times, {} animation names swapped in 10 s",
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
            plausible(p) && n == FORM.len() && std::slice::from_raw_parts(p as *const u8, n) == FORM.as_bytes()
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
            if let Some(k) = super::counted("form_view") {
                wlog(format!("FORM display world {world:#x} Yunara #{key}: {} (playing {cur}) #{k}",
                    if foot { "TRANSCENDENT - idle/run drawn as r_*" } else { "plain" }));
            }
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
        match game_places::hook::add("league_yunara", dress) {
            Ok((slot, prev)) => wlog(format!(
                "FORM Transcendent body on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM Transcendent body off ({e}): her idle and run stay the plain ones on screen (the main pack's look)")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_form() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("r_idle"));
        assert_eq!(anim_for("run", true).as_deref(), Some("r_run"));
        assert_eq!(anim_for("hit", true).as_deref(), Some("r_hit")); // 0.1.1: the glow stays on
        assert_eq!(anim_for("attack", true).as_deref(), Some("r_attack"));
        assert_eq!(anim_for("r_attack", false).as_deref(), Some("attack"));
        assert_eq!(anim_for("dead", true), None);
        assert_eq!(anim_for("skill2_r", true), None); // her own flip
        assert_eq!(anim_for("r_idle", false).as_deref(), Some("idle")); // the form is over
        assert_eq!(anim_for("r_run", false).as_deref(), Some("run"));
        assert_eq!(anim_for("idle", false), None);
    }

    #[test]
    fn every_swapped_tag_is_in_her_sheet() {
        let fanim = include_str!("../../../league/champions/league_yunara#anim.fanim");
        for t in FORM_TAGS {
            for name in [t.to_string(), format!("{PREFIX}{t}"), format!("hd_{PREFIX}{t}")] {
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_yunara#anim.fanim");
            }
        }
    }
}
