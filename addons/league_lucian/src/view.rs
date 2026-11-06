//! 开大边走边开枪：卢锡安身上有主包的开大 buff `league_lucian_r_ch` 时，游戏按名字自动播的 `run` 换成 `r_run`（双枪平端朝前
//! 的走路，他图里的 r_run / hd_r_run / lo_r_run），buff 没了（射完或被控打断）换回来。照 league_anivia 的 view.rs：显示世界
//! 每帧调用显示处理表里的更新函数（槽由 game_places 运行时找，别的附加包也挂在这里，一个接一个调用），名字是
//! `league_lucian` 的实体看身上的 buff 改正在播的动画名。高清帧照常：league.dll 把每个动画名都换成它的 hd_ 帧（r_run 也有）。
//! 只在游戏 0.6.4 起的 Windows 版上生效，别的版本什么都不做。
//!
//! 朝着子弹（0.2.0，用户 2026-11-06：「卢锡安可以倒着放大招？」）：画面上的人朝哪边是显示实体值 +0x1bc 的一个字节（画身体时
//! 当作图的水平翻转交给精灵——0.7.1 的画身体 0x2abd430 在 0x2abdfe8 读它；他的图朝右，1 = 朝左）。游戏只在两处写它：显示的
//! 移动处理（0x2c6d9f0，每走一步按横向走的方向 `seta`）和出招 / 普攻的动作（0x2c6dec0，朝目标）——开大的子弹是施法排好的
//! `Delayed`，不是动作，所以开大时往远离敌人的方向走，他就背对敌人、双枪朝另一边端着，子弹从背后飞出去。显示每一步（一个模拟
//! tick）先推动画时钟、再应用这一 tick 的事件（走路就在这里把他转回去）、再调用显示处理表（本包在这里），画在所有步之后
//! （0x90bf70：0x2ac2070 → 0x8fd680 → vtable+0x30）：所以开大期间本包每步把这个字节写成 lib.rs 的 `Aim` 挂在他身上的方向旗
//! （`league_lucian_r_face_l` / `_r`：下一枪打的敌方英雄在哪边），画出来就朝着子弹。
//!
//! 往远离子弹的方向走时（横向位移和朝向相反）`r_run` 倒着播：动画时钟（+0x170，秒；游戏每步加 速度 × 步长，0x2ac2070；画的
//! 时候按动画长度取模找帧，0x2ae6780）由本包接管，每步倒退游戏这一步推进的那么多——双枪对着敌人往后退，英雄联盟的侧移射击。
//! 往前走、竖着走、站着、射完都不动时钟（游戏从本包最后写的时钟接着往前推，不跳帧）。

use std::sync::{Mutex, Once};

use super::{wlog, FACE_L, FACE_R, FORM};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 卢锡安在画面实体里的名字。
pub const NAME: &[u8] = b"league_lucian";

/// 游戏按名字自动播、开大时换掉的动作：只有走路（站着不动时照常待机，普攻在开大时被禁）。
pub const FORM_TAGS: [&str; 1] = ["run"];
const PREFIX: &str = "r_";
/// 开大时的走路（往后退时倒着播的那一条）。
pub const R_RUN: &str = "r_run";
/// `r_run` 一圈的秒数（8 帧 × 0.117，单元测试核对他的图）：倒着播时时钟在 [0, 一圈) 里转。
pub const R_RUN_CYCLE: f32 = 0.936;
/// 显示实体值里的朝向（bool：画成水平翻转 = 朝左）。
const FLIP: usize = 0x1bc;
/// 显示实体值里正在播的动画的时钟（f32 秒）。
const CLOCK: usize = 0x170;
/// 显示实体值里的位置 x（游戏像素，league.dll view.rs 的 POS_X）。
const POS_X: usize = 0x17c;
/// 横向走了这么多像素才算朝一边走（不到就当竖着走、照旧）。
pub const STEP_MIN: f32 = 0.05;
/// 游戏一步推进时钟最多这么多秒；更多（或倒退）就是动画重新开始了：从游戏的时钟接着倒着播。
pub const CLOCK_STEP_MAX: f32 = 0.25;

/// 正在播的动画名 + 是不是在开大 → 该播的名字（不用换就是 None）。射完把本包换上去的 `r_run` 换回来。
pub fn anim_for(cur: &str, firing: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if firing { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

/// 开大时朝着子弹画的动作：站着、走（`run` 换成的 `r_run`）、开大拔枪的 `ult`。别的（开大中放的 Q / E、受击、阵亡）游戏
/// 自己朝那一招的目标，不碰。
pub const FACING_TAGS: [&str; 5] = ["idle", "idle_base", "run", "r_run", "ult"];

/// 正在播 `anim` 时要不要把他转向子弹那边。
pub fn faces_his_shots(anim: &str) -> bool {
    FACING_TAGS.contains(&anim)
}

/// 他身上的开大和方向旗（显示实体的 buff 名）：在不在开大，下一枪打哪边（`Some(true)` 左，`None` 还不知道）。
pub fn aim_of(names: &[&str]) -> (bool, Option<bool>) {
    let has = |n: &str| names.contains(&n);
    let face = if has(FACE_L) {
        Some(true)
    } else if has(FACE_R) {
        Some(false)
    } else {
        None
    };
    (has(FORM), face)
}

/// 朝 `left`（true 朝左）的他这一步横向走了 `dx` 像素：是不是背着子弹走（往后退）。`None`：没往两边走（竖着走或这一步
/// 没动），照旧。
pub fn backing(dx: f32, left: bool) -> Option<bool> {
    (dx.abs() >= STEP_MIN).then_some((dx > 0.0) == left)
}

/// 倒着播：上一步本包写下 `wrote`，游戏推进后时钟是 `now`（多了 速度 × 步长）→ 这一步要写的时钟（倒退同样多，在一圈里转）。
/// 推进的量不像一步（倒退了或太多：动画重新开始了）或刚开始倒着播（`None`），就从游戏的时钟 `now` 接着。
pub fn back_clock(wrote: Option<f32>, now: f32, cycle: f32) -> f32 {
    match wrote {
        Some(w) if (0.0..=CLOCK_STEP_MAX).contains(&(now - w)) => (w - (now - w)).rem_euclid(cycle),
        _ => now.rem_euclid(cycle),
    }
}

/// 一个（显示世界, 卢锡安）这次开大的走路：上一步的 x、是不是在往后退、倒着播时本包上一步写的时钟。
struct Walk {
    world: usize,
    key: u64,
    x: f32,
    back: bool,
    wrote: Option<f32>,
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    /// 本包把他转回子弹那边的次数（游戏让他转向走的方向之后）。
    turns: u64,
    /// 倒着播 `r_run` 的步数。
    backs: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的状态（开大、朝向）：变了才记一行 FORM。
    looks: Vec<(usize, u64, bool, Option<bool>)>,
    /// 这次开大已经记过 FACE 的（显示世界, 实体号）：一次开大记一行。
    turned: Vec<(usize, u64)>,
    walks: Vec<Walk>,
}

static STATS: Mutex<Stats> = Mutex::new(Stats {
    calls: 0,
    seen: 0,
    writes: 0,
    turns: 0,
    backs: 0,
    last: None,
    looks: Vec::new(),
    turned: Vec::new(),
    walks: Vec::new(),
});
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

fn side(left: bool) -> &'static str {
    if left {
        "left"
    } else {
        "right"
    }
}

/// 显示实体值 `v` 的 buff 名（读不通的跳过）。
unsafe fn buff_names<'a>(v: usize) -> Vec<&'a str> {
    let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
    if !plausible(bp) || bn > 256 {
        return Vec::new();
    }
    (0..bn)
        .filter_map(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            if !plausible(p) || n > 64 {
                return None;
            }
            std::str::from_utf8(std::slice::from_raw_parts(p as *const u8, n)).ok()
        })
        .collect()
}

/// 显示世界里每个卢锡安：按身上的开大 buff 换正在播的动画名，开大时朝着子弹那边，背着子弹走时倒着播。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!(
                "display handler: {} calls, Lucian seen {} times, {} animation names swapped, {} turns to his shots, {} frames walked backwards in 10 s",
                st.calls, st.seen, st.writes, st.turns, st.backs
            ));
        }
        st.last = Some(now);
        st.calls = 0;
        st.seen = 0;
        st.writes = 0;
        st.turns = 0;
        st.backs = 0;
    }
    let mut here: Vec<u64> = Vec::new();
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
        let (firing, face) = aim_of(&buff_names(v));
        st.seen += 1;
        let key = q(elem) as u64;
        here.push(key);
        if !firing {
            st.turned.retain(|t| *t != (world, key));
        }
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let look = (world, key, firing, if firing { face } else { None });
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            if let Some(k) = super::counted("form_view") {
                let what = match (firing, face) {
                    (false, _) => "Lucian".to_string(),
                    (true, Some(l)) => format!("R FIRING - run drawn as r_run, facing {} (his shots)", side(l)),
                    (true, None) => "R FIRING - run drawn as r_run, facing as the game has him (no shot side yet)".to_string(),
                };
                wlog(format!("FORM display world {world:#x} Lucian #{key}: {what} (playing {cur}) #{k}"));
            }
        }
        let shown = match anim_for(cur, firing) {
            Some(want) => {
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
                want
            }
            None => cur.to_string(),
        };
        // 朝着子弹：游戏这一步走路时让他转向了走的方向，这里转回来——只在站着、走着、拔枪（开大的头 12 tick）的时候；他在开大中
        // 出的招（Q、E）由游戏朝那一招的目标，不碰。这个字节只该是 0 / 1，不是就不碰。
        let flip = (v + FLIP) as *mut u8;
        let was = *flip;
        if let (true, Some(left), true, true) = (firing, face, faces_his_shots(&shown), was <= 1) {
            if was != u8::from(left) {
                *flip = u8::from(left);
                st.turns += 1;
                if !st.turned.contains(&(world, key)) {
                    st.turned.push((world, key));
                    if st.turned.len() > 64 {
                        st.turned.remove(0);
                    }
                    if let Some(k) = super::counted("turn") {
                        wlog(format!(
                            "FACE display world {world:#x} Lucian #{key}: the game turned him {} ({shown}), his shots go {} - turned back #{k}",
                            side(was == 1),
                            side(left)
                        ));
                    }
                }
            }
        }
        // 背着子弹走：r_run 倒着播（时钟由本包接管）；别的时候放手，游戏从本包写的时钟接着往前推
        let x = std::ptr::read_unaligned((v + POS_X) as *const f32);
        let at = st.walks.iter().position(|w| w.world == world && w.key == key);
        let (true, Some(left), true, true) = (firing, face, shown == R_RUN, x.is_finite()) else {
            if let Some(i) = at {
                st.walks.swap_remove(i);
            }
            continue;
        };
        let i = match at {
            Some(i) => i,
            None => {
                if st.walks.len() >= 32 {
                    st.walks.remove(0);
                }
                st.walks.push(Walk { world, key, x, back: false, wrote: None });
                st.walks.len() - 1
            }
        };
        let dx = x - st.walks[i].x;
        st.walks[i].x = x;
        if let Some(back) = backing(dx, left) {
            if back && !st.walks[i].back {
                if let Some(k) = super::counted("back") {
                    wlog(format!(
                        "BACK display world {world:#x} Lucian #{key}: walking {} away from his shots ({}) - r_run played backwards #{k}",
                        side(!left),
                        side(left)
                    ));
                }
            }
            st.walks[i].back = back;
        }
        let clock = (v + CLOCK) as *mut f32;
        let t = std::ptr::read_unaligned(clock);
        if !st.walks[i].back || !t.is_finite() || !(0.0..1000.0).contains(&t) {
            st.walks[i].wrote = None;
            continue;
        }
        let w = back_clock(st.walks[i].wrote, t, R_RUN_CYCLE);
        std::ptr::write_unaligned(clock, w);
        st.walks[i].wrote = Some(w);
        st.backs += 1;
    }
    // 不在这个画面上了的（换了一局）忘掉
    st.walks.retain(|w| w.world != world || here.contains(&w.key));
}

/// 加载时换槽（一个进程只换一次）。
pub fn install_once() {
    HOOK.call_once(|| {
        match game_places::hook::add("league_lucian", dress) {
            Ok((slot, prev)) => wlog(format!(
                "FORM walk while R fires on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x}); facing his shots, backing off with r_run backwards",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM walk while R fires off ({e}): he runs with his plain run during R, facing the way he walks")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_run_follows_his_r() {
        assert_eq!(anim_for("run", true).as_deref(), Some("r_run"));
        assert_eq!(anim_for("idle", true), None);
        assert_eq!(anim_for("ult", true), None);
        assert_eq!(anim_for("attack", true), None);
        assert_eq!(anim_for("r_run", false).as_deref(), Some("run"));
        assert_eq!(anim_for("r_run", true), None);
        assert_eq!(anim_for("run", false), None);
        assert_eq!(format!("{PREFIX}{}", FORM_TAGS[0]), R_RUN);
    }

    #[test]
    fn every_swapped_tag_is_in_his_sheet() {
        let fanim = include_str!("../../../league/champions/league_lucian#anim.fanim");
        for t in FORM_TAGS {
            for name in [t.to_string(), format!("{PREFIX}{t}"), format!("hd_{PREFIX}{t}"), format!("lo_{PREFIX}{t}")] {
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_lucian#anim.fanim");
            }
        }
        // the flag it reads is the main pack's R channel
        let data = include_str!("../../../league/champion/league_lucian.data_champion");
        assert!(data.contains(&format!("\"{}\"", super::super::FORM)), "{} is not in his kit", super::super::FORM);
    }

    /// The frame durations of one animation of his sheet (`"<tag>":{"frames":[{"duration":0.117,...`).
    fn durations(fanim: &str, tag: &str) -> Vec<f32> {
        let at = fanim.find(&format!("\"{tag}\":{{\"frames\":[")).unwrap_or_else(|| panic!("no {tag}"));
        let body = &fanim[at..];
        let body = &body[..body.find("]}").unwrap()];
        body.match_indices("\"duration\":")
            .map(|(k, s)| {
                let rest = &body[k + s.len()..];
                rest[..rest.find(',').unwrap()].parse().unwrap()
            })
            .collect()
    }

    #[test]
    fn the_backwards_cycle_is_his_r_run() {
        let fanim = include_str!("../../../league/champions/league_lucian#anim.fanim");
        // the battlefield draws the dense hd_ frames under the same name: the same timing
        for tag in [R_RUN.to_string(), format!("hd_{R_RUN}"), format!("lo_{R_RUN}")] {
            let d = durations(fanim, &tag);
            assert_eq!(d.len(), 8, "{tag}");
            let total: f32 = d.iter().sum();
            assert!((total - R_RUN_CYCLE).abs() < 1e-4, "{tag}: {total} s a cycle, not {R_RUN_CYCLE}");
        }
    }

    #[test]
    fn he_backs_off_when_he_walks_away_from_his_shots() {
        // facing left (his shots go left): a step right is backing off, a step left is walking on
        assert_eq!(backing(0.9, true), Some(true));
        assert_eq!(backing(-0.9, true), Some(false));
        assert_eq!(backing(-0.9, false), Some(true));
        assert_eq!(backing(0.9, false), Some(false));
        // no step to the side (straight up or down, or a step with no move): as before
        assert_eq!(backing(0.0, true), None);
        assert_eq!(backing(STEP_MIN / 2.0, false), None);
    }

    #[test]
    fn the_clock_runs_back_by_what_the_game_added() {
        let c = R_RUN_CYCLE;
        let step = 1.0 / 60.0;
        // the first step backing off: the game's own time
        assert_eq!(back_clock(None, 0.30, c), 0.30);
        // the game added a step to what was written: that much back
        let w = back_clock(Some(0.30), 0.30 + step, c);
        assert!((w - (0.30 - step)).abs() < 1e-6, "{w}");
        // across the start of the cycle: on from its end
        let w = back_clock(Some(0.005), 0.005 + step, c);
        assert!((w - (c + 0.005 - step)).abs() < 1e-5 && w < c, "{w}");
        // the animation began again (its clock reset) or a long hitch: from the game's time
        assert_eq!(back_clock(Some(0.60), step, c), step);
        assert!((back_clock(Some(0.10), 0.80, c) - 0.80).abs() < 1e-6);
        // the frames come in reverse order and never leave the cycle
        let mut w = 0.5;
        let mut prev = w;
        for k in 0..400 {
            w = back_clock(Some(w), w + step, c);
            assert!((0.0..c).contains(&w), "{w}");
            assert!(w < prev || prev < step * 1.5, "{k}: {prev} -> {w}");
            prev = w;
        }
    }

    #[test]
    fn only_standing_walking_and_the_draw_are_turned() {
        let fanim = include_str!("../../../league/champions/league_lucian#anim.fanim");
        for t in FACING_TAGS {
            assert!(fanim.contains(&format!("\"{t}\":{{\"frames\"")), "{t} is not in league_lucian#anim.fanim");
            assert!(faces_his_shots(t));
        }
        // his Q and E cast during the R face their own targets, as the game turns him for them
        for t in ["skill", "skill2", "skill2_back", "attack", "passive", "hit", "dead"] {
            assert!(!faces_his_shots(t), "{t}");
        }
    }

    #[test]
    fn the_flags_tell_the_side() {
        assert_eq!(aim_of(&[FORM, FACE_L]), (true, Some(true)));
        assert_eq!(aim_of(&[FACE_R, FORM]), (true, Some(false)));
        assert_eq!(aim_of(&[FORM]), (true, None));
        assert_eq!(aim_of(&["league_lucian_p"]), (false, None));
    }
}
