//! 冰蛋整身替换：寒霜涅槃的蛋里，艾尼维亚从头到尾画成冰蛋（图里的 `egg_idle` / `egg_hit`，缩进蛋 `egg_in`、孵化 `hatch`）。
//! 主包没有蛋（用户：「主包不做蛋，寒霜涅槃只放在扩展包里」）。只在游戏 0.6.4 起的 Windows 版上生效（显示更新槽由
//! game_places 在运行时找），别的版本什么都不做。
//!
//! 0.1.9（2026-11-11，玩家：「冰鸟的蛋貌似没动画了 但是效果还在 冰鸟不会原地复活了」）重写，原来有三处靠不住：
//!
//! - **只换 `idle` / `hit` 两个名字。** 显示实体存着「正在播的动作名」，游戏画的时候（0.7.2 rva 0x2c4ac00）还要再挑一次：
//!   定身计时在走、存的名字以 `run` 结尾 → 画普通的 `idle`；眩晕 / 击飞计时在走 → 画普通的 `hit`；别的画存的名字。0.1.7 起蛋
//!   被定身，她挨致命一击时要是正在走，存的名字整个蛋期间都是 `run`，本包看不到 `idle` 就不换，画出来一直是站着的鸟——
//!   「蛋没动画，效果还在」。现在蛋里不管存的是什么名字（阵亡 `dead` 和数据自己在播的蛋动作除外）都换成 `egg_idle`，
//!   `hit` 换成 `egg_hit`；这些名字都不以 `run` 结尾，定身时游戏照存的名字画。
//! - **靠显示世界里的 `egg_on` buff。** 显示世界收不到原生加的 buff（佛耶戈 0.1.3 / 0.1.6、妮蔻、大小龙的教训），0.1.8 让
//!   附加包自己挂 `egg_on` 以后，数据的守望没在跑时画面这边根本不知道她是蛋。现在照妮蔻 / 佛耶戈 0.1.7 的做法：被动在
//!   屏幕放的那场模拟里记下每颗蛋从哪一 tick 到哪一 tick、是孵化还是被打碎（[`note_egg`] / [`note_end`]），这里读屏幕上的
//!   比赛时钟（`game_places::clock`，合集里由佛耶戈的时钟读取器喂），到了那段时间就画蛋。读不到时钟（单独装本包、
//!   快进 / 倒退时）才退回看 buff。
//! - **缩进蛋、孵化的动作只由数据的守望播。** 守望是这条命第一次出手才开始的，玩家旧存档里的英雄副本还是老的（只有普攻和 R
//!   启动守望）。现在这两段由这里自己播：刚变蛋的头 [`IN_FOR`] 播 `egg_in`，孵化后的 [`OUT_FOR`] 播 `hatch`；数据自己在播
//!   `egg_in` / `egg` / `hatch` 时不动它。
//!
//! 还有一处：蛋被眩晕 / 击飞时游戏直接画普通的 `hit`（鸟挨打的样子），不看存的名字。显示实体上这两个倒计时（值 +0x198 /
//! +0x184，秒；游戏 0.7.2 每帧更新 rva 0x2c4a9a0 里递减）只管画面，所以蛋里把它们清零；缩进蛋、破壳开始播时把动作时间
//! （值 +0x170）归零，从第一帧播。这三个偏移只在 0.7.2 的代码里核对过，别的游戏版本不动它们（[`set_game`]）：那时蛋被眩晕
//! 会闪成鸟挨打的样子，缩进蛋 / 破壳可能从中间一帧开始。
//!
//! 照 league_nasus 的 view.rs（源自 league_swain / league_rell / league_jayce / league_nidalee / league_kayn_form）：显示世界每帧
//! 调用显示处理表里的更新函数，函数指针在一个槽里（别的附加包也挂在这里，一个接一个调用）。

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Mutex, Once};
use std::time::{Duration, Instant};

use super::{wlog, FORM};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 艾尼维亚在画面实体里的名字。
pub const NAME: &[u8] = b"league_anivia";

/// 蛋自己的动作（她图里的标签）。都不以 `run` 结尾：定身时游戏把以 `run` 结尾的名字画成普通的 `idle`。
pub const EGG_IDLE: &str = "egg_idle";
pub const EGG_HIT: &str = "egg_hit";
pub const EGG_IN: &str = "egg_in";
pub const HATCH: &str = "hatch";
/// 数据的守望自己播的蛋动作（`CasterAnimation`）：在播就不动。
pub const DATA_TAGS: [&str; 3] = ["egg_in", "egg", "hatch"];
/// 缩进蛋 / 孵化由这里播多久（图里 `egg_in` 3 帧 x 70 ms，`hatch` 4 帧 x 60 ms：播一遍）。
pub const IN_FOR: Duration = Duration::from_millis(210);
pub const OUT_FOR: Duration = Duration::from_millis(240);
/// 蛋挨打的样子最多留多久（游戏不把名字换回去时不会一直是它）。
pub const HIT_FOR: Duration = Duration::from_millis(200);
/// 屏幕时钟过了孵化那一 tick 这么多 tick 以内，算刚孵化（播 `hatch`）。
pub const OUT_TICKS: usize = 45;
/// BUFFS lines per game start.
const DUMP_CAP: usize = 30;

/// 显示实体值里只管画面的三个数（f32，秒；游戏 0.7.2：每帧更新 rva 0x2c4a9a0 递减 / 累加，挑动作 rva 0x2c4ac00 读）：
/// 动作播到哪、击飞还剩多久、眩晕还剩多久（后两个大于 0 时游戏画普通的 `hit`）。
pub const ANIM_TIME: usize = 0x170;
pub const AIRBORNE_LEFT: usize = 0x184;
pub const STUN_LEFT: usize = 0x198;
/// 这三个偏移在这个游戏版本上核对过。
static FIELDS_OK: AtomicBool = AtomicBool::new(false);

/// 加载时告诉这里游戏版本：只有核对过那三个偏移的版本（0.7.2）才动它们。
pub fn set_game(major: u32, minor: u32, patch: u32) -> bool {
    let ok = fields_known(major, minor, patch);
    FIELDS_OK.store(ok, Ordering::Relaxed);
    ok
}

pub fn fields_known(major: u32, minor: u32, patch: u32) -> bool {
    (major, minor, patch) == (0, 7, 2)
}

/// 一个倒计时该不该清：是个正常的、还在走的秒数（别的东西不碰）。
pub fn running(left: f32) -> bool {
    left.is_finite() && left > 0.0 && left < 600.0
}

// ===================== 被动记下的蛋（屏幕放的那场模拟） =====================

/// 一颗蛋：哪一场、哪一局、她的实体号（显示实体的键是同一个号）、变蛋的 tick、该孵化的 tick、实际怎么结束的。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Egg {
    pub m: u64,
    pub s: u64,
    pub id: usize,
    pub from: usize,
    pub due: usize,
    /// （结束的 tick，是不是孵化）；模拟还没跑到时 None。
    pub end: Option<(usize, bool)>,
}

static EGGS: Mutex<Vec<Egg>> = Mutex::new(Vec::new());
/// 屏幕放的、有艾尼维亚的最近一场模拟。
static LATEST: Mutex<Option<(u64, u64)>> = Mutex::new(None);

pub fn note_view(m: u64, s: u64) {
    if let Ok(mut l) = LATEST.lock() {
        *l = Some((m, s));
    }
}

/// 她在 (m, s) 的 `from` tick 变蛋，`due` tick 该孵化。屏幕那一场会跑不止一遍，同一颗只记一次。
pub fn note_egg(m: u64, s: u64, id: usize, from: usize, due: usize) {
    if let Ok(mut eggs) = EGGS.lock() {
        if !eggs.iter().any(|e| e.m == m && e.s == s && e.id == id && e.from == from) {
            eggs.push(Egg { m, s, id, from, due, end: None });
            if eggs.len() > 512 {
                eggs.remove(0);
            }
        }
    }
}

/// 那颗蛋在 `tick` 结束：孵化（`hatched`）或被打碎。
pub fn note_end(m: u64, s: u64, id: usize, tick: usize, hatched: bool) {
    if let Ok(mut eggs) = EGGS.lock() {
        end_egg(&mut eggs, m, s, id, tick, hatched);
    }
}

fn end_egg(eggs: &mut [Egg], m: u64, s: u64, id: usize, tick: usize, hatched: bool) {
    let last = eggs.iter_mut().filter(|e| e.m == m && e.s == s && e.id == id && e.from <= tick).max_by_key(|e| e.from);
    if let Some(e) = last {
        if e.end.is_none() {
            e.end = Some((tick, hatched));
        }
    }
}

/// 屏幕时钟走到的那一 tick 她是什么样子。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Look {
    Bird,
    Egg,
    /// 刚孵化（[`OUT_TICKS`] 以内）
    Hatched,
}

/// (m, s) 的艾尼维亚 `id` 在模拟的 `t` tick：最近一颗在 `t` 或之前开始的蛋还没结束就是蛋；没记到结束（模拟没跑到）按该孵化
/// 的 tick 算孵化。
pub fn look_at(eggs: &[Egg], m: u64, s: u64, id: usize, t: usize) -> Look {
    let Some(e) = eggs.iter().filter(|e| e.m == m && e.s == s && e.id == id && e.from <= t).max_by_key(|e| e.from) else {
        return Look::Bird;
    };
    let (end, hatched) = e.end.unwrap_or((e.due, true));
    if t < end {
        Look::Egg
    } else if hatched && t < end + OUT_TICKS {
        Look::Hatched
    } else {
        Look::Bird
    }
}

// ===================== 该播哪个名字 =====================

/// 这一帧她在蛋的哪一段。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Phase {
    Bird,
    /// 刚变蛋：缩进蛋
    In,
    Egg,
    /// 刚孵化：破壳
    Out,
}

fn is_egg_tag(name: &str) -> bool {
    name == EGG_IDLE || name == EGG_HIT || DATA_TAGS.contains(&name)
}

/// 存着的动作名 `cur` 该换成什么（不用换就是 None）。`mine`：`cur` 是这里上一次写的（游戏之后没再设过）；`under`：孵化后游戏
/// 自己设过的最后一个名字（还回去用，没有就是 `idle`）；`hit_over`：蛋挨打的样子已经留够 [`HIT_FOR`]。
/// 阵亡的名字从不动；数据的守望自己在播的蛋动作（不是这里写的）不动。
pub fn anim_for(cur: &str, mine: bool, phase: Phase, under: &str, hit_over: bool) -> Option<String> {
    if cur == "dead" {
        return None;
    }
    let data_plays = !mine && DATA_TAGS.contains(&cur);
    let want: &str = match phase {
        Phase::In => {
            if data_plays {
                return None;
            }
            EGG_IN
        }
        Phase::Egg => {
            if data_plays {
                return None;
            }
            if cur == "hit" || (cur == EGG_HIT && !hit_over) { EGG_HIT } else { EGG_IDLE }
        }
        Phase::Out => {
            if data_plays {
                return None;
            }
            HATCH
        }
        Phase::Bird => {
            if mine {
                // what the hook left there: back to what the game set since the hatch, else standing
                if under.is_empty() || is_egg_tag(under) || under == "hit" { "idle" } else { under }
            } else if cur == EGG_IDLE {
                "idle"
            } else if cur == EGG_HIT {
                "hit"
            } else {
                return None;
            }
        }
    };
    (want != cur).then(|| want.to_string())
}

/// 这一帧的蛋 / 刚孵化：屏幕时钟认得（`clock`）就听它的——它说是鸟时，显示世界里要是有蛋的 buff 也算蛋（时钟对不上那一场、
/// 差一两 tick）；读不到时钟只看 buff。返回（是蛋，刚孵化）。
pub fn egg_now(clock: Option<Look>, buff: bool) -> (bool, bool) {
    match clock {
        Some(Look::Egg) => (true, false),
        Some(Look::Hatched) => (false, true),
        Some(Look::Bird) | None => (buff, false),
    }
}

/// 一个显示实体上这里记着的东西。
struct Worn {
    world: usize,
    key: u64,
    egg: bool,
    since: Instant,
    out_until: Option<Instant>,
    hit_until: Option<Instant>,
    /// 这里上一次写进去的名字
    ours: String,
    /// 孵化后游戏自己设过的最后一个名字
    under: String,
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    /// stun / airborne display timers cleared on an egg
    cleared: u64,
    last: Option<Instant>,
    worn: Vec<Worn>,
    /// BUFFS lines written and when the last one was.
    dumped: usize,
    last_dump: Option<Instant>,
}

static STATS: Mutex<Stats> =
    Mutex::new(Stats { calls: 0, seen: 0, writes: 0, cleared: 0, last: None, worn: Vec::new(), dumped: 0, last_dump: None });
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

/// 显示世界里每个艾尼维亚：按屏幕时钟（读不到就按身上的蛋 buff）换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Anivia seen {} times, {} animation names swapped, {} stun / airborne \
                          display timers cleared on an egg in 10 s", st.calls, st.seen, st.writes, st.cleared));
        }
        st.last = Some(now);
        st.calls = 0;
        st.seen = 0;
        st.writes = 0;
        st.cleared = 0;
    }
    let view = LATEST.lock().ok().and_then(|l| *l);
    let tick = game_places::clock::screen_tick();
    let fields = FIELDS_OK.load(Ordering::Relaxed);
    let mut cleared = 0;
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
        let key = q(elem) as u64;
        let clock = match (tick, view, EGGS.lock()) {
            (Some(t), Some((m, s)), Ok(eggs)) => Some(look_at(&eggs, m, s, key as usize, t)),
            _ => None,
        };
        let (egg, hatched) = egg_now(clock, foot);
        // what the display world holds on her (once every 10 s while she is no egg, at most DUMP_CAP lines; league_swain's
        // first game never saw its form buff here, 2026-10-17, so the names say why if it happens again)
        if !egg && st.dumped < DUMP_CAP && st.last_dump.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
            st.last_dump = Some(now);
            st.dumped += 1;
            let names: Vec<String> = if plausible(bp) && bn <= 256 {
                (0..bn).map(|k| {
                    let b = bp + k * BUFF_SIZE;
                    let (p, n) = (q(b + 8), q(b + 0x10));
                    if plausible(p) && (1..=64).contains(&n) {
                        String::from_utf8_lossy(std::slice::from_raw_parts(p as *const u8, n)).into_owned()
                    } else {
                        format!("?{p:#x}/{n}")
                    }
                }).collect()
            } else {
                Vec::new()
            };
            wlog(format!("BUFFS display world {world:#x} Anivia: {bn} buffs [{}]", names.join(", ")));
        }
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let cur = cur.to_string();
        let i = match st.worn.iter().position(|w| w.world == world && w.key == key) {
            Some(i) => i,
            None => {
                if st.worn.len() >= 64 {
                    st.worn.remove(0);
                }
                st.worn.push(Worn { world, key, egg: false, since: now, out_until: None, hit_until: None,
                                    ours: String::new(), under: String::new() });
                if let Some(k) = super::counted("form_view") {
                    wlog(format!("FORM display world {world:#x} Anivia #{key}: seen (playing {cur}; screen tick {tick:?}, \
                                  sim {view:?}) #{k}"));
                }
                st.worn.len() - 1
            }
        };
        let how = if clock.is_some_and(|c| c != Look::Bird) { "the screen clock" } else { "the egg buff" };
        let w = &mut st.worn[i];
        if egg && !w.egg {
            (w.egg, w.since, w.out_until) = (true, now, None);
            if let Some(k) = super::counted("form_view") {
                wlog(format!("FORM display world {world:#x} Anivia #{key}: EGG by {how} (was playing {cur}; screen tick \
                              {tick:?}) #{k}"));
            }
        } else if !egg && w.egg {
            w.egg = false;
            // what the game set before the egg is stale by now: only names it sets from here on are given back
            w.under.clear();
            if hatched {
                w.out_until = Some(now + OUT_FOR);
            }
            if let Some(k) = super::counted("form_view") {
                wlog(format!("FORM display world {world:#x} Anivia #{key}: {} (was playing {cur}; screen tick {tick:?}) #{k}",
                             if hatched { "hatched - Anivia again" } else { "the egg is over - Anivia again" }));
            }
        }
        let phase = if w.egg {
            if now.duration_since(w.since) < IN_FOR { Phase::In } else { Phase::Egg }
        } else if w.out_until.is_some_and(|u| now < u) {
            Phase::Out
        } else {
            w.out_until = None;
            Phase::Bird
        };
        // a stunned or knocked-up egg: the game would draw the bird's `hit` whatever name is stored
        if fields && matches!(phase, Phase::In | Phase::Egg) {
            for off in [AIRBORNE_LEFT, STUN_LEFT] {
                let at = (v + off) as *mut f32;
                if running(at.read_unaligned()) {
                    at.write_unaligned(0.0);
                    cleared += 1;
                }
            }
        }
        let mine = !w.ours.is_empty() && w.ours == cur;
        if !mine && !is_egg_tag(&cur) && cur != "hit" && cur != "dead" {
            w.under = cur.clone();
        }
        let hit_over = mine && w.hit_until.is_some_and(|u| now >= u);
        let Some(want) = anim_for(&cur, mine, phase, &w.under, hit_over) else { continue };
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
        // the curl-up and the hatch from their first frame
        if fields && (want == EGG_IN || want == HATCH) {
            let at = (v + ANIM_TIME) as *mut f32;
            if at.read_unaligned().is_finite() {
                at.write_unaligned(0.0);
            }
        }
        w.hit_until = (want == EGG_HIT).then(|| now + HIT_FOR);
        // back as the bird: nothing of the hook's is left on her
        w.ours = if phase == Phase::Bird { String::new() } else { want };
        st.writes += 1;
    }
    st.cleared += cleared;
}

/// 加载时换槽（一个进程只换一次）。
pub fn install_once() {
    HOOK.call_once(|| {
        match game_places::hook::add("league_anivia", dress) {
            Ok((slot, prev)) => wlog(format!(
                "FORM whole-body egg on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x}); the egg is drawn \
                 by the screen clock from the eggs the passive notes (the egg buff when the clock cannot be read)",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM whole-body egg off ({e}): the egg is drawn only while the data's watch plays it")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    const NO: &str = "";

    #[test]
    fn in_the_egg_every_name_is_the_eggs() {
        // standing, walking (the report: rooted with `run` stored, the game drew the bird's idle), mid-cast: all the egg
        for cur in ["idle", "run", "attack", "skill", "skill2", "ult"] {
            assert_eq!(anim_for(cur, false, Phase::Egg, NO, false).as_deref(), Some(EGG_IDLE), "{cur}");
        }
        assert_eq!(anim_for("hit", false, Phase::Egg, NO, false).as_deref(), Some(EGG_HIT));
        // already there: nothing to write
        assert_eq!(anim_for(EGG_IDLE, true, Phase::Egg, NO, false), None);
        assert_eq!(anim_for(EGG_HIT, true, Phase::Egg, NO, false), None);
        // the egg's hit pose does not stay for ever
        assert_eq!(anim_for(EGG_HIT, true, Phase::Egg, NO, true).as_deref(), Some(EGG_IDLE));
        // her death and what the data's own watch plays are left alone
        assert_eq!(anim_for("dead", false, Phase::Egg, NO, false), None);
        for cur in DATA_TAGS {
            assert_eq!(anim_for(cur, false, Phase::Egg, NO, false), None, "{cur}");
        }
        // the hook's own curl-up over: the egg
        assert_eq!(anim_for(EGG_IN, true, Phase::Egg, NO, false).as_deref(), Some(EGG_IDLE));
    }

    #[test]
    fn no_name_of_the_egg_ends_in_run() {
        // a rooted champion whose stored name ends in "run" is drawn with the plain idle (the game, 0.7.2 rva 0x2c4ac00)
        for phase in [Phase::In, Phase::Egg, Phase::Out] {
            for cur in ["idle", "run", "hit", "attack", "egg_idle", "egg_hit"] {
                for mine in [false, true] {
                    if let Some(want) = anim_for(cur, mine, phase, NO, false) {
                        assert!(!want.ends_with("run"), "{phase:?} {cur} -> {want}");
                    }
                }
            }
        }
        for name in [EGG_IDLE, EGG_HIT, EGG_IN, HATCH] {
            assert!(!name.ends_with("run"));
        }
    }

    #[test]
    fn the_hook_plays_the_curl_up_and_the_hatch() {
        assert_eq!(anim_for("run", false, Phase::In, NO, false).as_deref(), Some(EGG_IN));
        assert_eq!(anim_for(EGG_IN, true, Phase::In, NO, false), None);
        // the data's watch plays its own: left to it
        assert_eq!(anim_for("egg_in", false, Phase::In, NO, false), None);
        assert_eq!(anim_for(EGG_IDLE, true, Phase::Out, NO, false).as_deref(), Some(HATCH));
        assert_eq!(anim_for("run", false, Phase::Out, NO, false).as_deref(), Some(HATCH));
        assert_eq!(anim_for(HATCH, true, Phase::Out, NO, false), None);
        assert_eq!(anim_for("hatch", false, Phase::Out, NO, false), None);
        assert_eq!(anim_for("dead", false, Phase::Out, NO, false), None);
    }

    #[test]
    fn hatched_she_gets_back_what_the_game_set_since() {
        // the hook's hatch still stored: she ran off during it -> run; nothing set since -> idle
        assert_eq!(anim_for(HATCH, true, Phase::Bird, "run", false).as_deref(), Some("run"));
        assert_eq!(anim_for(HATCH, true, Phase::Bird, NO, false).as_deref(), Some("idle"));
        assert_eq!(anim_for(EGG_IDLE, true, Phase::Bird, "hit", false).as_deref(), Some("idle"));
        // names left behind without the hook's memory (another display world)
        assert_eq!(anim_for(EGG_IDLE, false, Phase::Bird, NO, false).as_deref(), Some("idle"));
        assert_eq!(anim_for(EGG_HIT, false, Phase::Bird, NO, false).as_deref(), Some("hit"));
        // the bird's own names, and the data's hatch playing after the egg: untouched
        for cur in ["idle", "run", "attack", "hit", "dead", "hatch"] {
            assert_eq!(anim_for(cur, false, Phase::Bird, NO, false), None, "{cur}");
        }
    }

    #[test]
    fn the_screen_clock_finds_the_egg() {
        let mut eggs = vec![Egg { m: 7, s: 1, id: 30, from: 1000, due: 1360, end: None }];
        // the sim has not got to the end: an egg until it is due, then hatched
        assert_eq!(look_at(&eggs, 7, 1, 30, 999), Look::Bird);
        assert_eq!(look_at(&eggs, 7, 1, 30, 1000), Look::Egg);
        assert_eq!(look_at(&eggs, 7, 1, 30, 1359), Look::Egg);
        assert_eq!(look_at(&eggs, 7, 1, 30, 1360), Look::Hatched);
        assert_eq!(look_at(&eggs, 7, 1, 30, 1360 + OUT_TICKS), Look::Bird);
        // broken at 1200: no egg from then on, and no hatch
        end_egg(&mut eggs, 7, 1, 30, 1200, false);
        assert_eq!(look_at(&eggs, 7, 1, 30, 1199), Look::Egg);
        assert_eq!(look_at(&eggs, 7, 1, 30, 1200), Look::Bird);
        // the end is noted once (the screen's sim runs more than once)
        end_egg(&mut eggs, 7, 1, 30, 1360, true);
        assert_eq!(eggs[0].end, Some((1200, false)));
        // another match, another set, another Anivia (a new entity after a death): not hers
        assert_eq!(look_at(&eggs, 8, 1, 30, 1100), Look::Bird);
        assert_eq!(look_at(&eggs, 7, 2, 30, 1100), Look::Bird);
        assert_eq!(look_at(&eggs, 7, 1, 31, 1100), Look::Bird);
        // a later egg of the same entity: the latest one started counts
        eggs.push(Egg { m: 7, s: 1, id: 30, from: 20000, due: 20360, end: Some((20360, true)) });
        assert_eq!(look_at(&eggs, 7, 1, 30, 19999), Look::Bird);
        assert_eq!(look_at(&eggs, 7, 1, 30, 20100), Look::Egg);
        assert_eq!(look_at(&eggs, 7, 1, 30, 20361), Look::Hatched);
    }

    #[test]
    fn the_clock_decides_and_the_buff_backs_it_up() {
        assert_eq!(egg_now(Some(Look::Egg), false), (true, false));
        assert_eq!(egg_now(Some(Look::Hatched), true), (false, true), "the data's buff lingering a tick does not hide the hatch");
        assert_eq!(egg_now(Some(Look::Bird), true), (true, false), "the clock off the match: the buff still shows the egg");
        assert_eq!(egg_now(Some(Look::Bird), false), (false, false));
        assert_eq!(egg_now(None, true), (true, false));
        assert_eq!(egg_now(None, false), (false, false));
    }

    #[test]
    fn the_display_fields_are_touched_on_the_game_they_were_read_from_only() {
        assert!(fields_known(0, 7, 2));
        for v in [(0, 7, 1), (0, 7, 0), (0, 7, 3), (0, 8, 2), (1, 7, 2)] {
            assert!(!fields_known(v.0, v.1, v.2), "{v:?}");
        }
        // a timer that is counting down is cleared; zero, a negative, a huge or a non-number is left alone
        assert!(running(1.5) && running(0.016));
        for left in [0.0, -1.0, 600.0, 1.0e9, f32::NAN, f32::INFINITY] {
            assert!(!running(left), "{left}");
        }
    }

    #[test]
    fn eggs_are_noted_once() {
        note_view(901, 3);
        note_egg(901, 3, 44, 500, 860);
        note_egg(901, 3, 44, 500, 860);
        note_end(901, 3, 44, 860, true);
        let eggs = EGGS.lock().unwrap();
        let mine: Vec<&Egg> = eggs.iter().filter(|e| e.m == 901).collect();
        assert_eq!(mine.len(), 1);
        assert_eq!(*mine[0], Egg { m: 901, s: 3, id: 44, from: 500, due: 860, end: Some((860, true)) });
        assert_eq!(*LATEST.lock().unwrap(), Some((901, 3)));
    }
}
