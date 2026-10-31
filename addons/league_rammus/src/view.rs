//! 整身换形态：动力冲刺滚着的时候（副本的 Q 给他挂 `league_rammus_q_ball`）站着、走着、挨打都是滚动的刺球（图里的 `b_idle` /
//! `b_run` / `b_hit`），尖刺防御开着的时候（`league_rammus_w_on`）是蜷着的防御姿势（`c_idle` / `c_run` / `c_hit`）。主包只能用
//! `CasterAnimation` 换出招的动作，游戏按名字自动播的 idle / run / hit 数据换不了。只在游戏 0.6.4 起的 Windows 版上生效（地址由 game_places 运行时找，0.6.5 核对过），别的版本什么都
//! 不做：滚球照样加速、撞人，画面是主包那样站着的他。
//!
//! 照 league_reksai 的 view.rs（雷克塞的遁地整身，源自 league_rell / league_jayce / league_nidalee / league_kayn_form）：游戏的显示世界
//! 每帧调用显示处理表里的更新函数（rva 0x23312a0），函数指针在 .rdata 的槽 rva 0x3c82db8（凯隐、佛耶戈、奈德丽、杰斯、伊莉丝、厄斐
//! 琉斯、芮尔、雷克塞附加包也挂在这里，一个接一个调用）。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用槽里原来的函数，
//! 再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始：+0x40 名字，+0x68 / +0x70 / +0x78 正在播的动画名，
//! +0xb8 / +0xc0 buff 列表）。名字是 `league_rammus` 的实体身上有滚球 / 防御 buff 时，正在播的 idle / run / hit 换成 `b_*` / `c_*`
//! （滚球优先；新名字用游戏同一个堆分配，旧的照游戏的做法释放）。高清帧不用另管：league.dll 把登记英雄动画表里每个动作（b_idle 也
//! 在内）就地换成它的 hd_ 帧（addons/league_main/src/lookup.rs）。

use std::sync::{Mutex, Once};

use super::{wlog, BALL, CURL};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。

/// 拉莫斯在画面实体里的名字。
pub const NAME: &[u8] = b"league_rammus";

/// 游戏按名字自动播、两种形态各有一套的动作：待机、走、挨打。普攻、技能、阵亡不换（出招时他已经撞上 / 收起了球）。
pub const FORM_TAGS: [&str; 3] = ["idle", "run", "hit"];
const PREFIXES: [&str; 2] = ["b_", "c_"];

/// 形态：滚球（`b_`）、防御（`c_`）或都不是。
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Form {
    Stand,
    Ball,
    Curl,
}

/// 正在播的动画名 + 形态 → 该播的名字（不用换就是 None）。形态结束后把本包换上去的 `b_idle` 等换回来。
pub fn anim_for(cur: &str, form: Form) -> Option<String> {
    let base = PREFIXES.iter().find_map(|p| cur.strip_prefix(p)).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = match form {
        Form::Stand => base.to_string(),
        Form::Ball => format!("b_{base}"),
        Form::Curl => format!("c_{base}"),
    };
    (want != cur).then_some(want)
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的形态：变了才记一行 FORM。
    looks: Vec<(usize, u64, Form)>,
}

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, seen: 0, writes: 0, last: None, looks: Vec::new() });
static HOOK: Once = Once::new();

use game_places::heap::{GetProcessHeap, HeapAlloc, HeapFree};

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// 显示世界里每个拉莫斯：按身上的滚球 / 防御 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Rammus seen {} times, {} animation names swapped in 10 s",
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
        let form = if has(BALL) { Form::Ball } else if has(CURL) { Form::Curl } else { Form::Stand };
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
                wlog(format!("FORM display world {world:#x} Rammus #{key}: {} (playing {cur}) #{k}", match form {
                    Form::Ball => "the BALL - idle/run/hit drawn as b_*",
                    Form::Curl => "CURLED - idle/run/hit drawn as c_*",
                    Form::Stand => "standing",
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
        match game_places::hook::add("league_rammus", dress) {
            Ok((slot, prev)) => wlog(format!(
                "FORM ball / curl bodies on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM ball / curl bodies off ({e}): he stands on screen while rolling (the main pack's look)")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_form() {
        assert_eq!(anim_for("idle", Form::Ball).as_deref(), Some("b_idle"));
        assert_eq!(anim_for("run", Form::Ball).as_deref(), Some("b_run"));
        assert_eq!(anim_for("hit", Form::Curl).as_deref(), Some("c_hit"));
        assert_eq!(anim_for("c_run", Form::Ball).as_deref(), Some("b_run")); // the curl ends in a roll
        assert_eq!(anim_for("b_run", Form::Stand).as_deref(), Some("run")); // the ball is over
        assert_eq!(anim_for("c_idle", Form::Stand).as_deref(), Some("idle"));
        assert_eq!(anim_for("attack", Form::Ball), None);
        assert_eq!(anim_for("skill_roll", Form::Ball), None); // the main pack's own roll
        assert_eq!(anim_for("idle", Form::Stand), None);
    }

    #[test]
    fn every_swapped_tag_is_in_his_sheet() {
        let fanim = include_str!("../../../league/champions/league_rammus#anim.fanim");
        for t in FORM_TAGS {
            for p in ["", "b_", "c_", "hd_", "hd_b_", "hd_c_"] {
                let name = format!("{p}{t}");
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_rammus#anim.fanim");
            }
        }
    }
}
