//! 风暴形态变色：天声震落落地后（主包数据给他挂 `league_volibear_r_form`，12 秒），他站着、走着、普攻、撕咬、放 Q、放 E、挨打都是
//! 雷电蓝的一套（图里的 `r_idle` / `r_run` …：他自己的帧逐格换成风暴的颜色、外圈电蓝描边，tools/art/volibear_storm.py；用户
//! 2026-10-30：「沃利贝尔开大是不是得搞个变色啊」，三份草稿里选了「2 雷电蓝+描边」）。主包只能用 `CasterAnimation` 换出招的动作，
//! 游戏按名字自动播的 idle / run / hit 数据换不了；与其出招时蓝、站着时白地来回闪，主包干脆不变色，只有身后的雷云（view_buffs
//! r_form）。只在游戏 0.6.4 起的 Windows 版上生效（地址由 game_places 运行时找），别的版本什么都不做，退回主包那样。
//!
//! 照 league_yunara 的 view.rs（源自 league_rell / league_jayce / league_nidalee / league_kayn_form）：游戏的显示世界每帧调用显示
//! 处理表里的更新函数，本包挂在 game_places::hook 上（凯隐、佛耶戈、奈德丽、杰斯、芸阿娜等附加包也挂在这里，一个接一个调用），走一遍
//! 显示世界的实体表。名字是 `league_volibear` 的实体身上有风暴形态 buff 时，正在播的动作换成它的 `r_` 双胞胎（新名字用游戏同一个
//! 堆分配，旧的照游戏的做法释放）；buff 没了（形态结束、阵亡）换回来。双胞胎和原帧帧数、时长、每帧大小和画到的格子都一样，只是颜色
//! 不同，所以动作播到一半换也接得上（落地砸地 ult_land 第一帧就换：buff 和它同一 tick 开始）。高清帧不用另管：league.dll 把登记英雄
//! 动画表里每个动作（r_idle 也在内）就地换成它的 hd_ 帧（addons/league_main/src/lookup.rs）。

use std::sync::{Mutex, Once};

use super::{wlog, R_FORM as FORM};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 沃利贝尔在画面实体里的名字。
pub const NAME: &[u8] = b"league_volibear";

/// 风暴形态里能播的每个动作（tools/art/volibear_storm.py TAGS，图里各有一个 `r_` 双胞胎）：待机、走、Q 的冲锋和扑砸、普攻、撕咬、
/// E、R 的起跳和落地、挨打。阵亡不换（形态 buff 随阵亡清掉：倒下的是原来的他）。
pub const FORM_TAGS: [&str; 10] =
    ["idle", "run", "skill_run", "attack", "attack_w", "skill", "skill2", "ult", "ult_land", "hit"];
const PREFIX: &str = "r_";

/// 正在播的动画名 + 是不是在风暴形态 → 该播的名字（不用换就是 None）。形态结束后把本包换上去的 `r_idle` 等换回来。
pub fn anim_for(cur: &str, storm: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if storm { format!("{PREFIX}{base}") } else { base.to_string() };
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

/// 显示世界里每个沃利贝尔：按身上的风暴形态 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Volibear seen {} times, {} animation names swapped in 10 s",
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
        let storm = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
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
        let look = (world, key, storm);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            if let Some(k) = super::counted("form_view") {
                wlog(format!("FORM display world {world:#x} Volibear #{key}: {} (playing {cur}) #{k}",
                    if storm { "STORM - drawn as r_* (electric blue)" } else { "plain" }));
            }
        }
        let Some(want) = anim_for(cur, storm) else { continue };
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
        match game_places::hook::add("league_volibear", dress) {
            Ok((slot, prev)) => wlog(format!(
                "FORM storm colours on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM storm colours off ({e}): in R's form he stays his own colours on screen (the main pack's look)")),
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
        assert_eq!(anim_for("attack_w", true).as_deref(), Some("r_attack_w"));
        assert_eq!(anim_for("skill_run", true).as_deref(), Some("r_skill_run"));
        assert_eq!(anim_for("ult_land", true).as_deref(), Some("r_ult_land"));
        assert_eq!(anim_for("hit", true).as_deref(), Some("r_hit"));
        assert_eq!(anim_for("r_idle", true), None);
        assert_eq!(anim_for("dead", true), None);
        assert_eq!(anim_for("idle_base", true), None);
        assert_eq!(anim_for("r_attack", false).as_deref(), Some("attack")); // the form is over
        assert_eq!(anim_for("r_skill2", false).as_deref(), Some("skill2"));
        assert_eq!(anim_for("idle", false), None);
    }

    #[test]
    fn every_swapped_tag_is_in_his_sheet() {
        let fanim = include_str!("../../../league/champions/league_volibear#anim.fanim");
        for t in FORM_TAGS {
            for name in [t.to_string(), format!("{PREFIX}{t}"), format!("hd_{PREFIX}{t}")] {
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_volibear#anim.fanim");
            }
        }
    }
}
