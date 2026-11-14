//! 约里克附加包：数据做不到、和英雄联盟不一样的地方，这里照英雄联盟做。
//!
//! `mod.override_info` 把主包的约里克换成 `override/` 里的副本（tools/kit/build_yorick.py --native，再由 make_override.py
//! 加上召唤单位的开关），`passive` 换成本包的 `league_yorick:shepherd`：
//!
//! - **坟墓照英雄联盟挖**：主包读不到「这一铲打死了谁」，所以临终仪式打英雄挖一座坟、打别的每两下挖一座。副本的这一铲给
//!   约里克挂几拍 `league_yorick_q_win`，本包在它还在时，每有一个小兵 / 野怪被他打死就挖一座坟（打英雄照旧由数据挖），
//!   不再「每两下」。0.1.1（2026-11-03 夜里的日志：6 条命一座坟都没挖）：`q_win` 和这一铲同一拍挂上——以前晚两拍才挂，
//!   追踪的那一铲下一拍就落地打死了小兵，`q_win` 还没在。
//! - **室女的加伤只打她的目标**：主包读不到「室女跟着谁」，所以室女在场时约里克普攻任何英雄都加伤。副本给室女的目标挂
//!   `league_yorick_maiden`，普攻打中英雄时给它挂 3 拍 `league_yorick_hit`；本包看到同时有这两个的英雄，才造成它最大生命
//!   `r_pct`% 的真实伤害。
//!
//! **雾行者和迷雾少女是真的单位（0.2.0，2026-11-14；用户：「召唤物的全做啊 剩下的一批英雄也做了啊」）。** 主包里雾行者和室女
//! 是挂在目标身上的画面和伤害（数据里召唤物不会走）。英雄联盟里它们是自己走、自己打、能被打死的小鬼和女幽灵。稳定 mod API 的
//! `spawn_unit`（公用部分在萨科附加包的 `summon.rs`，这里用 `#[path]` 引进来；一个召唤者好几个单位用它的 `Flock`）：
//!
//! - **唤醒的雾行者**：副本的 Q 在坟满（唤醒）出手时给目标挂 `K_ASK`（3 tick），去掉上一次的 `K_UNIT`。被动看到就排原生效果
//!   `:walkers`：在目标周围 `WALK_SPREAD` 生成 `K_N` 只 `league_yorick_walker`（[`walker_spec`]），成功了给约里克挂 `K_UNIT`——
//!   副本的数据在这一铲落地（出手后约 15 tick）时读它：有，就不放挂在目标身上的那三只；没有（宿主没有这个接口、生成失败、
//!   测试开关关了、读不成单位、一出来就没了），就和今天一模一样。
//! - **黑雾让雾行者扑过去**：副本的 E 的英雄分身给它打中的英雄挂 `E_ASK`；被动让离它 `LEAP_REACH` 以内的每只雾行者单位跳到
//!   它身边（`entity_set_pos`），主包的扑咬伤害（`LEAP_HIT` + `LEAP_HIT_AD`% 攻击力）由约里克打一次。
//! - **迷雾少女**：副本的 R 出手时给目标挂 `M_ASK`，去掉上一次的 `M_UNIT`；被动排 `:maiden`，在它身后 `MAID_BEHIND` 生成
//!   `league_yorick_maiden`（[`maiden_spec`]）和她身边的 `R_N` 只雾行者，成功了挂 `M_UNIT`——数据在室女升起（出手后约 17 tick）
//!   时读它，有就不放挂在目标身上的室女和她的两只雾行者。她站着的时候约里克的 `r_on`（Q 冷却减半、普攻加伤）和她目标身上的
//!   `league_yorick_maiden` 跟着她的时间（`MAID_LIFE`）；她被打死就一起去掉。
//! - 约里克先死了：单位由引擎管着接着打，到时间为止（没有「让单位消失」的接口）。
//!
//! 数字从英雄数据的 `passive.params`（坟和加伤）和 `src/lib.rs` 的常量来（单位的数字，`make_override.py` 和主包的参数表 P、
//! 单位图的动作对照）。不用全局变量，服务端预模拟和你看的那场各算各的。日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yorick.log`，每次启动游戏重写；单位的行以 `WALKER` / `MAIDEN` 开头。
//! 测试开关：日志旁边的 `league_yorick.cfg`（`summon.rs`：`unit=off` / `still=1` / `name=`）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

use summon::{Event, Flock, Pt};

const ID: &str = "league_yorick";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_yorick") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// On him for a few ticks after a Last Rites blow: a unit dying meanwhile died to it.
const Q_WIN: &str = "league_yorick_q_win";
/// On the Maiden's champion while she stands.
pub const MAIDEN: &str = "league_yorick_maiden";
/// On a champion his attack struck while she stands (3 ticks).
const HIT: &str = "league_yorick_hit";
/// His graves, counted on him (the data's ladder: the first g1, then g2, then g3; the Awakening takes them off).
const GRAVES: [&str; 3] = ["league_yorick_g1", "league_yorick_g2", "league_yorick_g3"];

// ---- 雾行者和迷雾少女作为单位（0.2.0）：主包的数字（make_override.py 对照参数表 P 检查，改主包就改这里）----

/// The Awakening's walkers (k_n), each bite (k_dmg + k_ratio % of his attack, every k_p ticks); the riding walkers' time
/// (k_t: what the units replace).
pub const K_N: usize = 3;
pub const WALK_HIT: usize = 9;
pub const WALK_HIT_AD: usize = 13;
pub const WALK_COOL: usize = 60;
pub const K_T: usize = 360;
/// The pounce when Mourning Mist strikes a champion (k_jmp + k_jmp_r % of his attack, once).
pub const LEAP_HIT: usize = 20;
pub const LEAP_HIT_AD: usize = 30;
/// The Maiden's escort (r_n); her claws (r_dmg + r_ratio % of his attack, every r_p ticks); the riding Maiden's time and
/// r_on's (r_t).
pub const R_N: usize = 2;
pub const MAID_HIT: usize = 20;
pub const MAID_HIT_AD: usize = 45;
pub const MAID_COOL: usize = 60;
pub const R_T: usize = 600;
/// When the data reads the flags: the Awakening's walkers ride from the blow's landing (q_hit, a tick later), the Maiden
/// from her rising (r_rel, a tick later).
pub const Q_HIT: usize = 14;
pub const R_REL: usize = 16;
/// The unit sheets' attack: ticks long and the tick the bite / the claws land (tools/art/unit_yorick_summons.py's frames:
/// 380 ms with the bite 170 ms in; 400 ms with the claws 180 ms in).
pub const WALK_ACT: usize = 23;
pub const WALK_LANDS: usize = 10;
pub const MAID_ACT: usize = 24;
pub const MAID_LANDS: usize = 11;

// ---- 单位的其他数字（英雄联盟 wiki 现行页面的，照约里克的套路换算：生命按他的生命、距离按他的射程 25000 / 175）----

/// The unit names: the game draws them from asset/base/aseprite_resources/champions/<name>, which mod.override_info sends
/// to the main pack's league/champions/<name>.
pub const WALKER: &str = "league_yorick_walker";
pub const MAIDEN_UNIT: &str = "league_yorick_maiden";
/// A walker lives `WALK_LIFE` ticks (League: until killed; the riding ones 6 s - walking to its prey and killable, 10 s),
/// with `WALK_HP_PCT` % of his health cap (League: 100-331 against his 650-2588), no armour or magic resistance (League's),
/// his move speed (League: 325, +60 near him, against his 340), reach `WALK_RANGE` (League: 125 against his 175).
pub const WALK_LIFE: usize = 600;
pub const WALK_HP_PCT: usize = 15;
pub const WALK_RANGE: usize = 18_000;
/// The Maiden lives `MAID_LIFE` ticks (League: until killed; riding, 10 s), with `MAID_HP_PCT` % of his health cap (League:
/// 1050-3700 against his 1220-2588), `MAID_DEF_PCT` % of his armour as armour and magic resistance (League: 30-100 both,
/// against his 36-112), his move speed (League: 300, +60 near him), his own reach (League's 600 range is not taken: a
/// unit's attack has no projectile, she would strike from 86000 away with nothing flying).
pub const MAID_LIFE: usize = 900;
pub const MAID_HP_PCT: usize = 120;
pub const MAID_DEF_PCT: usize = 85;
pub const MAID_RANGE: usize = 25_000;
/// The walkers rise this far round the Awakening's target; the Maiden this far behind (up the screen from) the champion
/// she is raised on (the riding picture's place), her escort as far round her.
pub const WALK_SPREAD: f64 = 12_000.0;
pub const MAID_BEHIND: f64 = 11_000.0;
/// Walkers within `LEAP_REACH` of the champion the mist struck leap to `LEAP_SIDE` from him (League: within 1500 of the
/// cursed enemy - 2.14 times E's 700 - against our E range of 55000).
pub const LEAP_REACH: f64 = 118_000.0;
pub const LEAP_SIDE: f64 = 9_000.0;
/// The copy's asks (on the target, 3 ticks), the flags on him while units stand in for the riding pictures, the handoffs.
pub const K_ASK: &str = "league_yorick_k_ask";
pub const K_UNIT: &str = "league_yorick_k_unit";
pub const M_ASK: &str = "league_yorick_m_ask";
pub const M_UNIT: &str = "league_yorick_m_unit";
pub const E_ASK: &str = "league_yorick_e_ask";
pub const W_UID: &str = "league_yorick_w_uid";
pub const M_UID: &str = "league_yorick_m_uid";
/// The data's flag while the Maiden stands (Q's cooldown halved, the bonus on her target).
pub const R_ON: &str = "league_yorick_r_on";
/// The main pack's sounds the natives play.
pub const K_SPAWN_SFX: &str = "league_yorick_k_spawn";
pub const K_LEAP_VIEW: &str = "league_yorick_k_leap";
pub const R_SPAWN_SFX: &str = "league_yorick_r_spawn";
/// Walkers on the books at once (two Awakenings and an escort).
pub const WALK_CAP: usize = 8;
/// Ticks a flag stays (the data reads it once, about 15 ticks after the cast), and the handoff buffs.
const FLAG_TICKS: usize = 60;
const UID_TICKS: usize = 6;
/// A unit gone within this many ticks was never really there: the flag goes and the data's picture plays.
pub const LOST_AGE: usize = 6;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_YORICK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_yorick.log");
        }
    }
    PathBuf::from("league_yorick.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

/// The test knobs (`league_yorick.cfg` beside the log), read once.
static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (league_olaf_rage's lesson: opening it for every line stalled the simulation thread)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{kind} m={} s={}] t={} #{id}", m(o.match_id), m(o.set_index), sim.tick())
}

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).unwrap_or_else(|| format!("#{id}"))
}

/// Lines of each kind of the units' a launch (league_shaco_backstab's): the server's presims the first `LOG_FIRST`, then
/// every `LOG_EVERY`-th; the match on screen all.
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind`: its count this launch when it is to be written (`shown`: the match on screen).
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let shown = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    noted(kind, shown)
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 室女的目标被约里克普攻打中时，额外受到它最大生命的这么多百分比（真实伤害）。
    pub r_pct: usize,
    /// 一座坟留多少拍（数据的 g1..g3 一样长）。
    pub g_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { r_pct: 3, g_t: 1800 }
    }
}

/// `{"g_t":1800,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "r_pct" => p.r_pct = v,
            "g_t" => p.g_t = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

/// The Maiden's bonus on her target: r_pct% of its maximum health (at least 1).
pub fn maiden_bonus(p: &Params, max_hp: usize) -> usize {
    (max_hp * p.r_pct / 100).max(1)
}

/// Which grave flag a new grave raises, given which he has (the data's ladder): g1, then g2, then g3; None when full.
pub fn next_grave(has: [bool; 3]) -> Option<usize> {
    match has {
        [_, _, true] => None,
        [_, true, _] => Some(2),
        [true, _, _] => Some(1),
        _ => Some(0),
    }
}

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    summon::at_of(e)
}

/// A Mist Walker from his numbers now (`stat`, his health cap `max_hp`), living `life` ticks: his attack and speed, no
/// defences, `WALK_HP_PCT` % of his health; each bite `WALK_HIT` + `WALK_HIT_AD` % of his attack.
pub fn walker_spec(stat: &StatV1, max_hp: usize, life: usize) -> summon::Spec {
    summon::Spec {
        name: WALKER.to_string(),
        life,
        stat: StatV1 { attack: stat.attack, magic_power: 0, hp: (max_hp * WALK_HP_PCT / 100).max(1), defence: 0,
                       magic_resistance: 0, move_speed: stat.move_speed, hp_regen: 0, stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: WALK_HIT_AD, attack: WALK_HIT, range: WALK_RANGE, cooltime: WALK_COOL,
                               duration: WALK_ACT, start_timing: WALK_LANDS, cancelable: false,
                               attack_type: AttackTypeV1::BaseAttack.code() },
    }
}

/// The Maiden of the Mist from his numbers now: `MAID_HP_PCT` % of his health cap, `MAID_DEF_PCT` % of his armour as armour
/// and magic resistance, his attack and speed; each claw `MAID_HIT` + `MAID_HIT_AD` % of his attack.
pub fn maiden_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    let def = stat.defence * MAID_DEF_PCT / 100;
    summon::Spec {
        name: MAIDEN_UNIT.to_string(),
        life: MAID_LIFE,
        stat: StatV1 { attack: stat.attack, magic_power: 0, hp: (max_hp * MAID_HP_PCT / 100).max(1), defence: def,
                       magic_resistance: def, move_speed: stat.move_speed, hp_regen: 0, stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: MAID_HIT_AD, attack: MAID_HIT, range: MAID_RANGE, cooltime: MAID_COOL,
                               duration: MAID_ACT, start_timing: MAID_LANDS, cancelable: false,
                               attack_type: AttackTypeV1::BaseAttack.code() },
    }
}

/// Where the Awakening's walkers rise round its target at `at` (Yorick at `here`): `WALK_SPREAD` round it, none of them
/// on the line between the two (the first a third of a turn round from his side).
pub fn walker_points(at: Pt, here: Pt, n: usize) -> Vec<Pt> {
    let first = (here.1 - at.1).atan2(here.0 - at.0) + std::f64::consts::FRAC_PI_3;
    summon::spread(at, WALK_SPREAD, n, first)
}

/// Where a walker at `walker` lands when it leaps at a champion at `at`: `LEAP_SIDE` from him on its own side (one already
/// that near stays where it is).
pub fn leap_spot(at: Pt, walker: Pt) -> Pt {
    let d = summon::dist(at, walker);
    if d <= LEAP_SIDE {
        return walker;
    }
    (at.0 + (walker.0 - at.0) / d * LEAP_SIDE, at.1 + (walker.1 - at.1) / d * LEAP_SIDE)
}

/// The pounce's damage before armour, from his attack.
pub fn leap_damage(attack: usize) -> usize {
    LEAP_HIT + attack * LEAP_HIT_AD / 100
}

fn fx(name: &str) -> String {
    format!("{ID}:{name}")
}

fn at_input(at: Pt) -> InputTargetV1 {
    InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64)
}

fn point(input: &InputTargetV1) -> Option<Pt> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Pos)).then_some((input.x as f64, input.y as f64))
}

// ===================== 原生效果：生成 =====================

/// Units of `spec` for Yorick `me` at `points`, each handed to his passive by a `<uid>:<id>` buff on him. -> their ids.
fn spawn_all(sim: &mut StableSim<'_>, me: usize, team: usize, points: &[Pt], spec: &summon::Spec, uid: &str) -> Vec<usize> {
    let field = summon::field(sim);
    let mut ids = Vec::new();
    for p in points {
        if let Some(id) = summon::spawn(sim, me, team, summon::inside(field, *p), spec) {
            sim.add_buff(me, &BuffV1::timed(&summon::handoff(uid, id), UID_TICKS));
            ids.push(id);
        }
    }
    ids
}

fn flag(sim: &mut StableSim<'_>, me: usize, name: &str) {
    sim.entity_remove_buff(me, name);
    sim.add_buff(me, &BuffV1::timed(name, FLAG_TICKS));
}

/// The Awakening's walkers for Yorick `me` round `at`: `K_N` of them, the flag for the data on him when any came. -> how
/// many came.
fn make_walkers(sim: &mut StableSim<'_>, me: usize, at: Pt, by: &str) -> usize {
    let Some((team, stat, max, here)) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1, pos(&e))) else { return 0 };
    let spec = walker_spec(&stat, max, WALK_LIFE).with(&KNOBS);
    let ids = spawn_all(sim, me, team, &walker_points(at, here, K_N), &spec, W_UID);
    if ids.is_empty() {
        if let Some(k) = tally(sim, "walkers fail") {
            wlog(format!("{} WALKERS SPAWN FAILED #{k} ({by}): spawn_unit gave no unit for '{}' round {} - the walkers ride on \
                          the target as before", head(sim, me), spec.name, summon::pt(at)));
        }
        return 0;
    }
    flag(sim, me, K_UNIT);
    sim.play_sfx(K_SPAWN_SFX, me, &at_input(at));
    if let Some(k) = tally(sim, "walkers spawn") {
        wlog(format!("{} WALKERS SPAWN #{k} ({by}): {} of {K_N} units {:?} for team {team} round {}: {}", head(sim, me), ids.len(),
                     ids, summon::pt(at), spec.shown()));
    }
    ids.len()
}

/// The Maiden for Yorick `me` behind the champion at `at`, and her escort round her; the flag for the data on him when
/// she came. -> she came.
fn make_maiden(sim: &mut StableSim<'_>, me: usize, at: Pt, by: &str) -> bool {
    let Some((team, stat, max, here)) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1, pos(&e))) else { return false };
    let spec = maiden_spec(&stat, max).with(&KNOBS);
    let spot = (at.0, (at.1 - MAID_BEHIND).max(0.0));
    let her = spawn_all(sim, me, team, &[spot], &spec, M_UID);
    let Some(&id) = her.first() else {
        if let Some(k) = tally(sim, "maiden fail") {
            wlog(format!("{} MAIDEN SPAWN FAILED #{k} ({by}): spawn_unit gave no unit for '{}' at {} - she rides behind the \
                          champion as before", head(sim, me), spec.name, summon::pt(spot)));
        }
        return false;
    };
    flag(sim, me, M_UNIT);
    sim.play_sfx(R_SPAWN_SFX, me, &at_input(spot));
    let escort = walker_spec(&stat, max, MAID_LIFE).with(&KNOBS);
    let ids = spawn_all(sim, me, team, &walker_points(spot, here, R_N), &escort, W_UID);
    if let Some(k) = tally(sim, "maiden spawn") {
        wlog(format!("{} MAIDEN SPAWN #{k} ({by}): unit #{id} for team {team} at {}: {}; her escort: {} of {R_N} walkers {:?}",
                     head(sim, me), summon::pt(spot), spec.shown(), ids.len(), ids));
    }
    true
}

/// `:walkers` - the passive queues it when the Awakening is cast; the input is the target's spot.
struct WalkersFx;

impl StableEffectType for WalkersFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = point(&input).or_else(|| sim.get_entity(caster).map(|e| pos(&e))) else { return };
        make_walkers(sim, caster, at, "the queued effect");
    }
}

/// `:maiden` - the passive queues it when R is cast; the input is the champion's spot.
struct MaidenFx;

impl StableEffectType for MaidenFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = point(&input).or_else(|| sim.get_entity(caster).map(|e| pos(&e))) else { return };
        make_maiden(sim, caster, at, "the queued effect");
    }
}

// ===================== 被动 =====================

/// Which walkers these are.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum Walk {
    /// Raised by the Awakening.
    #[default]
    Awake,
    /// The Maiden's escort.
    Escort,
}

impl Walk {
    fn shown(self) -> &'static str {
        match self {
            Walk::Awake => "the Awakening's",
            Walk::Escort => "the Maiden's escort",
        }
    }
}

/// A walker as the passive keeps it.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct WalkerBook {
    pub kind: Walk,
}

/// The Maiden as the passive keeps her: the champion she was raised on, the tick she was read as a unit, whether the
/// look a tick later was logged.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct MaidBook {
    pub target: usize,
    pub looked: usize,
    pub dressed: bool,
}

/// 每个约里克一份：参数、日志计数、他的单位。
#[derive(Clone)]
struct Shepherd {
    p: Params,
    graves: usize,
    bonuses: usize,
    /// His own unit (on_dead is given the player).
    me: usize,
    walkers: Flock<WalkerBook>,
    maiden: Flock<MaidBook>,
}

impl Default for Shepherd {
    fn default() -> Self {
        Shepherd { p: Params::default(), graves: 0, bonuses: 0, me: 0, walkers: Flock::new(W_UID, WALK_CAP, WALK_LIFE),
                   maiden: Flock::new(M_UID, 1, MAID_LIFE) }
    }
}

impl Shepherd {
    /// A unit died to Last Rites: one grave more (the data's ladder; full graves stay full).
    fn dig(&mut self, sim: &mut StableSim<'_>, me: usize, victim: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !has(&e, Q_WIN) {
            return;
        }
        let Some(k) = next_grave([has(&e, GRAVES[0]), has(&e, GRAVES[1]), has(&e, GRAVES[2])]) else { return };
        sim.entity_remove_buff(me, GRAVES[k]);
        sim.add_buff(me, &BuffV1::timed(GRAVES[k], self.p.g_t));
        self.graves += 1;
        if self.graves <= 40 || self.graves % 100 == 0 {
            wlog(format!("{} GRAVE {} died to Last Rites: grave {} ({} in all)", head(sim, me), name_of(sim, victim),
                         k + 1, self.graves));
        }
    }

    /// His attacks on the Maiden's own target: the bonus, once a hit.
    fn maiden(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let ids: Vec<usize> = (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).collect();
        for id in ids {
            let Some(c) = sim.get_entity(id) else { continue };
            if c.team() == team || !c.is_alive() || !has(&c, HIT) {
                continue;
            }
            let target = has(&c, MAIDEN);
            let max_hp = c.hp().1;
            sim.entity_remove_buff(id, HIT);
            if !target {
                continue;
            }
            let dmg = maiden_bonus(&self.p, max_hp);
            sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Fixed, AttackTypeV1::Skill);
            self.bonuses += 1;
            if self.bonuses <= 40 || self.bonuses % 100 == 0 {
                wlog(format!("{} MAIDEN bonus {dmg} on her target {} ({} in all)", head(sim, me), name_of(sim, id),
                             self.bonuses));
            }
        }
    }

    /// The copy's asks on his enemies: the Awakening's walkers, the Maiden, the mist's pounce.
    fn asks(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let marked: Vec<(usize, Pt, bool, bool, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team)
            .map(|u| (u.id(), pos(&u), has(&u, K_ASK), has(&u, M_ASK), has(&u, E_ASK)))
            .filter(|m| m.2 || m.3 || m.4)
            .collect();
        for (id, at, k, m, e) in marked {
            if k {
                sim.entity_remove_buff(id, K_ASK);
                self.ask(sim, me, id, at, true);
            }
            if m {
                sim.entity_remove_buff(id, M_ASK);
                self.ask(sim, me, id, at, false);
            }
            if e {
                sim.entity_remove_buff(id, E_ASK);
                self.leap(sim, me, id, at);
            }
        }
    }

    /// The Awakening's walkers (`walkers`) or the Maiden asked for on `target` at `at`.
    fn ask(&mut self, sim: &mut StableSim<'_>, me: usize, target: usize, at: Pt, walkers: bool) {
        let tick = sim.tick();
        let (what, kind) = if walkers { ("WALKERS", "walkers off") } else { ("MAIDEN", "maiden off") };
        if KNOBS.off {
            if let Some(k) = tally(sim, kind) {
                wlog(format!("{} {what} OFF #{k}: cast on #{target}, unit=off in the test knobs - {} as before", head(sim, me),
                             if walkers { "the walkers ride on the target" } else { "she rides behind the champion" }));
            }
            return;
        }
        let effect = if walkers { "walkers" } else { "maiden" };
        if walkers {
            self.walkers.ask(tick, WALK_LIFE, WalkerBook { kind: Walk::Awake });
        } else {
            self.maiden.ask(tick, MAID_LIFE, MaidBook { target, looked: 0, dressed: false });
            self.walkers.ask(tick, MAID_LIFE, WalkerBook { kind: Walk::Escort });
        }
        let queued = sim.queue_effect(&fx(effect), AttackTypeV1::Skill, me, &at_input(at), 1);
        if !queued {
            if walkers {
                make_walkers(sim, me, at, "queue_effect refused: spawned by the passive");
            } else {
                make_maiden(sim, me, at, "queue_effect refused: spawned by the passive");
            }
        }
        let k = tally(sim, if walkers { "walkers ask" } else { "maiden ask" });
        if let Some(k) = k {
            wlog(format!("{} {what} ASK #{k}: {} on #{target} {} at {}: {}{}", head(sim, me),
                         if walkers { "the Awakening" } else { "Eulogy of the Isles" }, name_of(sim, target), summon::pt(at),
                         if walkers { format!("{K_N} walkers asked for round it") }
                         else { format!("the Maiden asked for {MAID_BEHIND:.0} behind it, {R_N} walkers round her") },
                         if queued { "" } else { " - queue_effect REFUSED" }));
        }
    }

    /// The mist struck `champion` at `at`: the walkers within `LEAP_REACH` leap to him, the pounce dealt once.
    fn leap(&mut self, sim: &mut StableSim<'_>, me: usize, champion: usize, at: Pt) {
        if self.walkers.live.is_empty() {
            return;
        }
        let Some((alive, attack)) = sim.get_entity(champion).map(|c| c.is_alive() && c.is_targetable())
            .zip(sim.get_entity(me).map(|e| e.stat().attack)) else { return };
        let (mut leapt, mut moved, mut far) = (Vec::new(), 0usize, 0usize);
        for id in self.walkers.ids() {
            let Some(w) = sim.get_entity(id).filter(|w| w.is_alive()).map(|w| pos(&w)) else { continue };
            if !alive || summon::dist(w, at) > LEAP_REACH {
                far += 1;
                continue;
            }
            let spot = leap_spot(at, w);
            if sim.entity_set_pos(id, spot.0.round().max(0.0) as u64, spot.1.round().max(0.0) as u64) {
                moved += 1;
            }
            leapt.push(id);
        }
        let damage = leap_damage(attack);
        if !leapt.is_empty() {
            sim.deal_damage_typed(me, champion, damage, DamageTypeV1::Ad, AttackTypeV1::Skill);
            let on = InputTargetV1::target(champion);
            sim.play_view_effect(K_LEAP_VIEW, me, &on, 0, 0, 0);
            sim.play_sfx(K_LEAP_VIEW, me, &on);
        }
        if let Some(k) = tally(sim, "leap") {
            wlog(format!("{} WALKERS LEAP #{k}: the mist struck #{champion} {} at {}{}: {} walkers leapt {:?} ({moved} moved by \
                          entity_set_pos{}), {far} out of reach; the pounce {}", head(sim, me), name_of(sim, champion),
                         summon::pt(at), if alive { "" } else { " (dead or untargetable)" }, leapt.len(), leapt,
                         if moved < leapt.len() { ", the rest REFUSED" } else { "" },
                         if leapt.is_empty() { "not dealt".to_string() } else { format!("{damage} physical, once") }));
        }
    }

    /// An Awakening walker still out, or one on its way.
    fn awake_out(&self) -> bool {
        self.walkers.live.iter().any(|m| m.extra.kind == Walk::Awake) || self.walkers.out() > self.walkers.live.len()
    }

    fn walker_event(&mut self, sim: &mut StableSim<'_>, me: usize, ev: Event<WalkerBook>) {
        match ev {
            Event::NoUnit { asked, what } => {
                if let Some(k) = tally(sim, "walkers none") {
                    wlog(format!("{} WALKERS NONE #{k}: no walker came within {} ticks of the ask at t={asked} ({}) - {}",
                                 head(sim, me), summon::FLOCK_WAIT, what.kind.shown(),
                                 if what.kind == Walk::Awake { "the walkers ride on the target as before" }
                                 else { "the Maiden has no escort of units" }));
                }
            }
            Event::Look { id, n, line } => {
                let kind = self.walkers.get(id).map_or(Walk::Awake, |m| m.extra.kind);
                if let Some(k) = tally(sim, "walker look") {
                    wlog(format!("{} WALKER #{n} LOOK #{k} ({}): {line}", head(sim, me), kind.shown()));
                }
            }
            Event::Lost { id, why, what } => {
                let off = what.kind == Walk::Awake && !self.awake_out();
                if off {
                    sim.entity_remove_buff(me, K_UNIT);
                }
                if let Some(k) = tally(sim, "walker lost") {
                    wlog(format!("{} WALKER LOST #{k}: the unit #{id} spawn_unit named never read as one in {} ticks ({why}){}",
                                 head(sim, me), summon::FLOCK_LOOKS,
                                 if off { " - the flag is off, the walkers ride on the target as before" } else { "" }));
                }
            }
            Event::Line { n, line, .. } => {
                if let Some(k) = tally(sim, "walker unit") {
                    wlog(format!("{} WALKER #{n} #{k}: {line}", head(sim, me)));
                }
            }
            Event::Over { member, end } => {
                let n = member.unit.n;
                if let Some(k) = tally(sim, "walker over") {
                    wlog(format!("{} WALKER #{n} OVER #{k} ({}): {}", head(sim, me), member.extra.kind.shown(), end.text));
                }
                if member.extra.kind == Walk::Awake && end.age <= LOST_AGE && !self.awake_out() {
                    // never really there: the data has not read the flag yet, so its walkers can still ride
                    sim.entity_remove_buff(me, K_UNIT);
                    wlog(format!("{} WALKER #{n}: gone {} ticks after it was asked for - the flag is off, the walkers ride on \
                                  the target as before", head(sim, me), end.age));
                }
            }
            Event::LetGo { member } => {
                if let Some(k) = tally(sim, "walker let go") {
                    wlog(format!("{} WALKER #{} LET GO #{k}: {WALK_CAP} walkers on the books - the unit #{} is out there, no \
                                  longer watched", head(sim, me), member.unit.n, member.unit.id));
                }
            }
            Event::Wake { n, line } => {
                if let Some(k) = tally(sim, "walker wake") {
                    wlog(format!("{} WALKER #{n} WAKE #{k}: {line}", head(sim, me)));
                }
            }
        }
    }

    fn maiden_event(&mut self, sim: &mut StableSim<'_>, me: usize, ev: Event<MaidBook>) {
        let tick = sim.tick();
        match ev {
            Event::NoUnit { asked, what } => {
                if let Some(k) = tally(sim, "maiden none") {
                    wlog(format!("{} MAIDEN NONE #{k}: no Maiden came within {} ticks of the ask at t={asked} (on #{}) - she \
                                  rides behind the champion as before", head(sim, me), summon::FLOCK_WAIT, what.target));
                }
            }
            Event::Look { id, n, line } => {
                // she stands for her time: r_on (Q's cooldown halved, the bonus) and the mark on her champion with her
                let target = self.maiden.get(id).map_or(0, |m| m.extra.target);
                let left = self.maiden.get(id).map_or(MAID_LIFE, |m| m.unit.left(tick));
                sim.entity_remove_buff(me, R_ON);
                sim.add_buff(me, &BuffV1::timed(R_ON, left));
                let marked = sim.get_entity(target).is_some_and(|c| c.is_alive() && c.is_champion());
                if marked {
                    sim.entity_remove_buff(target, MAIDEN);
                    sim.add_buff(target, &BuffV1::timed(MAIDEN, left));
                }
                if let Some(m) = self.maiden.get_mut(id) {
                    (m.extra.looked, m.extra.dressed) = (tick, false);
                }
                if let Some(k) = tally(sim, "maiden look") {
                    wlog(format!("{} MAIDEN #{n} LOOK #{k}: {line}; {R_ON} on Yorick and {MAIDEN} on #{target} {} for her \
                                  {left} ticks", head(sim, me), if marked { "set" } else { "(gone: not set)" }));
                }
            }
            Event::Lost { id, why, .. } => {
                sim.entity_remove_buff(me, M_UNIT);
                if let Some(k) = tally(sim, "maiden lost") {
                    wlog(format!("{} MAIDEN LOST #{k}: the unit #{id} spawn_unit named never read as one in {} ticks ({why}) - \
                                  the flag is off, she rides behind the champion as before", head(sim, me),
                                 summon::FLOCK_LOOKS));
                }
            }
            Event::Line { n, line, .. } => {
                if let Some(k) = tally(sim, "maiden unit") {
                    wlog(format!("{} MAIDEN #{n} #{k}: {line}", head(sim, me)));
                }
            }
            Event::Over { member, end } => {
                let (n, target) = (member.unit.n, member.extra.target);
                let why = if end.age <= LOST_AGE {
                    // never really there: the data has not read the flag yet, so its Maiden can still rise
                    sim.entity_remove_buff(me, M_UNIT);
                    format!(" - gone {} ticks after she was asked for: the flag is off, she rides behind the champion as before",
                            end.age)
                } else if end.fate == summon::Fate::Killed {
                    // she no longer stands: Q's halved cooldown and the bonus on her champion go with her
                    sim.entity_remove_buff(me, R_ON);
                    sim.entity_remove_buff(target, MAIDEN);
                    format!(" - {R_ON} and the mark on #{target} taken off")
                } else {
                    String::new()
                };
                if let Some(k) = tally(sim, "maiden over") {
                    wlog(format!("{} MAIDEN #{n} OVER #{k}: {}{why}", head(sim, me), end.text));
                }
            }
            Event::LetGo { member } => {
                if let Some(k) = tally(sim, "maiden let go") {
                    wlog(format!("{} MAIDEN #{} LET GO #{k}: a new one came - the unit #{} is out there, no longer watched",
                                 head(sim, me), member.unit.n, member.unit.id));
                }
            }
            Event::Wake { n, line } => {
                if let Some(k) = tally(sim, "maiden wake") {
                    wlog(format!("{} MAIDEN #{n} WAKE #{k}: {line}", head(sim, me)));
                }
            }
        }
    }

    /// The units' part of a tick: the flocks looked at, the Maiden's dressing checked a tick after her look.
    fn units(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize, team: usize, here: Pt) {
        let tick = sim.tick();
        for ev in self.walkers.tick(sim, me, team, player, Some(here)) {
            self.walker_event(sim, me, ev);
        }
        for ev in self.maiden.tick(sim, me, team, player, Some(here)) {
            self.maiden_event(sim, me, ev);
        }
        let due: Vec<(usize, usize, usize)> = self.maiden.live.iter()
            .filter(|m| !m.extra.dressed && tick > m.extra.looked)
            .map(|m| (m.unit.id, m.unit.n, m.extra.target)).collect();
        for (id, n, target) in due {
            if let Some(m) = self.maiden.get_mut(id) {
                m.extra.dressed = true;
            }
            let on_him = sim.get_entity(me).is_some_and(|e| has(&e, R_ON));
            let on_it = sim.get_entity(target).is_some_and(|c| has(&c, MAIDEN));
            if let Some(k) = tally(sim, "maiden dress") {
                wlog(format!("{} MAIDEN #{n} DRESS #{k}: a tick on, {R_ON} {} on Yorick, {MAIDEN} {} on #{target}", head(sim, me),
                             if on_him { "is" } else { "is NOT" }, if on_it { "is" } else { "is NOT" }));
            }
        }
    }

    /// A line for a hook that fired while units of his are out: is the one the engine names a unit of his?
    fn hooked(&self, sim: &StableSim<'_>, hook: &str, entity: usize, other: usize, damage: Option<usize>) {
        if self.walkers.live.is_empty() && self.maiden.live.is_empty() {
            return;
        }
        let who = if let Some(m) = self.walkers.get(entity) {
            format!("the walker #{}", m.unit.n)
        } else if let Some(m) = self.maiden.get(entity) {
            format!("the Maiden #{}", m.unit.n)
        } else if entity == self.me {
            "Yorick".to_string()
        } else {
            "neither Yorick nor a unit of his".to_string()
        };
        if let Some(k) = tally(sim, "hook") {
            wlog(format!("{} HOOK #{k} {hook}: entity #{entity} ({who}) -> #{other} {}{}", head(sim, self.me), name_of(sim, other),
                         damage.map(|d| format!(", damage {d}")).unwrap_or_default()));
        }
    }

    /// Everything of his units let go (he died or a new life began).
    fn orphans(&mut self, sim: &StableSim<'_>, why: &str) {
        let (w, m) = (self.walkers.orphans(), self.maiden.orphans());
        if w.is_empty() && m.is_empty() {
            return;
        }
        let tick = sim.tick();
        let list: Vec<String> = w.iter().map(|x| format!("walker #{} ({} ticks left)", x.unit.id, x.unit.left(tick)))
            .chain(m.iter().map(|x| format!("Maiden #{} ({} ticks left)", x.unit.id, x.unit.left(tick)))).collect();
        if let Some(k) = tally(sim, "orphan") {
            wlog(format!("{} ORPHAN #{k}: {why} - {} fight on unwatched until their time: {}", head(sim, self.me), list.len(),
                         list.join(", ")));
        }
    }
}

impl StablePassive for Shepherd {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        // a new life is a new entity: the units of the old one are no longer his to watch
        self.orphans(sim, "Yorick respawned (his death did not reach on_dead)");
        self.me = me;
        wlog(format!("{} SPAWN: the add-on's Yorick (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        // a dead champion's passive does not run: his units fight on by themselves (no API ends a unit early)
        self.orphans(sim, "Yorick died");
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, target: usize, damage: &mut usize) {
        self.hooked(sim, "on_attack", entity, target, Some(*damage));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_kill", entity, victim, None);
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.hooked(sim, "on_unit_kill", me, victim, None);
        // a minion or a camp (a champion hit digs its own grave in the data)
        self.dig(sim, me, victim);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let Some((alive, team, here)) = sim.get_entity(me).map(|e| (e.is_alive(), e.team(), pos(&e))) else { return };
        if !alive {
            return;
        }
        self.me = me;
        self.maiden(sim, me);
        self.asks(sim, me, team);
        self.units(sim, player, me, team, here);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (graves from kills, the Maiden's bonus on her target; the walkers and the Maiden units of their \
         own) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "UNITS: the Mist Walkers ('{}') and the Maiden of the Mist ('{}') are units (spawn_unit) - {}; the Awakening {K_N} walkers \
         for {WALK_LIFE} ticks ({WALK_HIT} + {WALK_HIT_AD}% of his attack a bite, {WALK_HP_PCT}% of his health), the Maiden for \
         {MAID_LIFE} ticks ({MAID_HIT} + {MAID_HIT_AD}% a claw, {MAID_HP_PCT}% of his health) with {R_N} walkers, the mist's \
         leap within {LEAP_REACH:.0}. Test knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(WALKER),
        KNOBS.name.as_deref().unwrap_or(MAIDEN_UNIT),
        if KNOBS.off { "OFF by the test knobs: they ride on the target as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(),
        KNOBS.shown()
    ));
    module.add_native_passive(format!("{ID}:shepherd"), Shepherd::default());
    module.add_native_effect(fx("walkers"), WalkersFx);
    module.add_native_effect(fx("maiden"), MaidenFx);
    host.log(LogLevel::Info, "league_yorick loaded (graves from kills, the Maiden's bonus on her target; walkers and Maiden as units).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"g_t":1200,"r_pct":5,"x":1}"#);
        assert_eq!(p, Params { r_pct: 5, g_t: 1200 });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_graves_climb_the_data_s_ladder() {
        assert_eq!(next_grave([false, false, false]), Some(0));
        assert_eq!(next_grave([true, false, false]), Some(1));
        assert_eq!(next_grave([true, true, false]), Some(2));
        assert_eq!(next_grave([false, true, false]), Some(2)); // g1 ran out first: the ladder goes on from g2
        assert_eq!(next_grave([true, true, true]), None);
    }

    #[test]
    fn the_maiden_s_bonus_is_a_share_of_max_health() {
        let p = Params::default();
        assert_eq!(maiden_bonus(&p, 2000), 60);
        assert_eq!(maiden_bonus(&p, 10), 1);
    }

    #[test]
    fn names_are_the_data_s() {
        for n in [Q_WIN, MAIDEN, HIT, K_ASK, K_UNIT, M_ASK, M_UNIT, E_ASK, R_ON].iter().chain(GRAVES.iter()) {
            assert!(n.starts_with("league_yorick_"), "{n}");
        }
        for name in [K_ASK, K_UNIT, M_ASK, M_UNIT, E_ASK, &summon::handoff(W_UID, usize::MAX), &summon::handoff(M_UID, usize::MAX)] {
            assert!(name.len() <= BUFF_NAME_CAP, "{name}");
        }
    }

    /// 0.1.1 (2026-11-03 night logs: 6 lives, 0 GRAVE): the copy raised `q_win` from a Delayed 2 after the blow, and the
    /// homing blow lands - and kills - on the next tick. Every blow (the slot's and the controller's) now raises it in its
    /// own Combine, ahead of the projectile, and no late one is left.
    #[test]
    fn every_blow_raises_q_win_before_it_lands() {
        let copy = include_str!("../override/league_yorick.data_champion");
        let parts: Vec<&str> = copy.split("\"name\": \"league_yorick_q_blow\"").collect();
        assert!(parts.len() > 1, "no Last Rites blow in the copy");
        for (i, before) in parts[..parts.len() - 1].iter().enumerate() {
            let at = before.rfind(Q_WIN).unwrap_or_else(|| panic!("blow {i}: no {Q_WIN} before it"));
            assert!(!before[at..].contains("\"Delayed\""), "blow {i}: its {Q_WIN} waits in a Delayed");
        }
        assert!(!parts[parts.len() - 1].contains(Q_WIN), "a {Q_WIN} after the last blow (a late one)");
    }

    /// 0.2.0: the copy asks for the units and lets the riding pictures play only without the flags (make_override.py
    /// writes it; here the copy as shipped is read back).
    #[test]
    fn the_copy_asks_for_the_units_and_keeps_the_riding_pictures_behind_the_flags() {
        let copy = include_str!("../override/league_yorick.data_champion");
        // the Awakening: in the slot's Q and the two controllers' (hung by the attack and the ult)
        assert_eq!(copy.matches(&format!("\"name\": \"{K_ASK}\"")).count(), 3);
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{K_UNIT}\"")).count(), 3);
        assert_eq!(copy.matches(&format!("\"name\": \"{E_ASK}\"")).count(), 3);
        assert_eq!(copy.matches(&format!("\"name\": \"{M_ASK}\"")).count(), 1);
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{M_UNIT}\"")).count(), 1);
        // every flag taken off where its ask is laid, before the units' effect lays it again
        assert_eq!(copy.matches(&format!("\"name\": \"{K_UNIT}\"")).count(), 3);
        assert_eq!(copy.matches(&format!("\"name\": \"{M_UNIT}\"")).count(), 1);
    }

    #[test]
    fn the_flags_are_up_before_the_data_reads_them_and_a_lost_unit_is_told_before_it() {
        // the units come at most 3 ticks after the cast; the data reads K_UNIT when the blow lands (Q_HIT + 1) and M_UNIT
        // when the Maiden rises (R_REL + 1): a unit unreadable for FLOCK_LOOKS ticks, or gone by LOST_AGE, takes the flag
        // off before that
        assert!(3 + summon::FLOCK_WAIT + summon::FLOCK_LOOKS < Q_HIT + 1);
        assert!(3 + LOST_AGE < Q_HIT + 1);
        assert!(R_REL >= Q_HIT);
        assert!(FLAG_TICKS > R_REL + 1 && FLAG_TICKS < WALK_LIFE);
        assert!(UID_TICKS > 2);
    }

    #[test]
    fn the_units_are_built_from_his_numbers() {
        let his = StatV1 { attack: 150, magic_power: 30, hp: 900, defence: 80, magic_resistance: 40, move_speed: 1080,
                           hp_regen: 5, stack: 1, crit_chance: 10 };
        let w = walker_spec(&his, 2000, WALK_LIFE);
        assert_eq!((w.name.as_str(), w.life), ("league_yorick_walker", 600));
        assert_eq!(w.stat, StatV1 { attack: 150, magic_power: 0, hp: 300, defence: 0, magic_resistance: 0, move_speed: 1080,
                                    hp_regen: 0, stack: 0, crit_chance: 0 });
        // a bite: 9 + 13 % of 150 = 28, every 60 ticks (the riding walkers' second)
        let a = w.attack;
        assert_eq!(a.attack + w.stat.attack * a.attack_ratio / 100, 28);
        assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (18_000, 60, 23, 10));
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        let m = maiden_spec(&his, 2000);
        assert_eq!((m.name.as_str(), m.life), ("league_yorick_maiden", 900));
        assert_eq!((m.stat.hp, m.stat.defence, m.stat.magic_resistance, m.stat.move_speed), (2400, 68, 68, 1080));
        // a claw: 20 + 45 % of 150 = 87
        assert_eq!(m.attack.attack + m.stat.attack * m.attack.attack_ratio / 100, 87);
        assert_eq!((m.attack.range, m.attack.cooltime, m.attack.duration, m.attack.start_timing), (25_000, 60, 24, 11));
        assert_eq!(walker_spec(&StatV1::default(), 0, 1).stat.hp, 1);
        assert_eq!(leap_damage(150), 65);
    }

    /// The arithmetic of the README: what the units can deal against what the riding pictures dealt.
    #[test]
    fn the_units_damage_is_about_the_riding_ones() {
        let bite = |ad: usize| WALK_HIT + ad * WALK_HIT_AD / 100;
        let claw = |ad: usize| MAID_HIT + ad * MAID_HIT_AD / 100;
        for ad in [91, 150, 250, 400] {
            // riding: three walkers bite their target once a second for K_T ticks; the Maiden claws once a second for R_T
            let (walk_old, maid_old) = (K_N * (K_T / WALK_COOL) * bite(ad), (R_T / MAID_COOL) * claw(ad));
            // units: every bite / claw of their life (the first landing at WALK_LANDS / MAID_LANDS)
            let walk_max = K_N * (WALK_LANDS..WALK_LIFE).step_by(WALK_COOL).count() * bite(ad);
            let maid_max = (MAID_LANDS..MAID_LIFE).step_by(MAID_COOL).count() * claw(ad);
            assert_eq!(walk_max * 6, walk_old * 10, "ad {ad}");
            assert_eq!(maid_max * 10, maid_old * 15, "ad {ad}");
            // in reach of their prey 60 % (the walkers) and two thirds (the Maiden) of their life: what the riding ones dealt
            assert_eq!(walk_max * 60 / 100, walk_old, "ad {ad}");
            assert_eq!(maid_max * 2 / 3, maid_old, "ad {ad}");
        }
    }

    #[test]
    fn the_walkers_rise_round_the_target_and_leap_beside_their_prey() {
        let (at, here) = ((500_000.0, 300_000.0), (450_000.0, 300_000.0));
        let p = walker_points(at, here, 3);
        assert_eq!(p.len(), 3);
        for q in &p {
            assert!((summon::dist(*q, at) - WALK_SPREAD).abs() < 1.0);
            // none between him and the target
            assert!(!(q.0 < at.0 && (q.1 - at.1).abs() < 1.0), "{q:?}");
        }
        assert_eq!(leap_spot((100_000.0, 100_000.0), (100_000.0, 160_000.0)), (100_000.0, 109_000.0));
        assert_eq!(leap_spot((100_000.0, 100_000.0), (104_000.0, 100_000.0)), (104_000.0, 100_000.0));
    }

    // ---- the units on the mock world (summon_mock.rs: our guess of the host, to check this side's logic) ----

    use super::mock::{champion, unit, MPlayer, World};

    const GAREN: usize = 1;
    const DARIUS: usize = 2;

    fn log_file() -> PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_yorick_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_YORICK_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// Yorick #0 (team 0, attack 150, 2000 health) at (300000, 300000); Garen #1 40000 east of him, Darius #2 far south-east,
    /// an enemy minion #3 far north; a player each for the champions.
    fn world() -> (World, Shepherd) {
        log_file();
        let mut w = World::default();
        let mut yorick = champion("league_yorick", 0, 300_000.0, 300_000.0);
        (yorick.hp, yorick.max, yorick.stat.attack, yorick.stat.defence) = (2000, 2000, 150, 80);
        let mut garen = champion("league_garen", 1, 340_000.0, 300_000.0);
        (garen.hp, garen.max) = (5000, 5000);
        let mut darius = champion("league_darius", 1, 600_000.0, 500_000.0);
        (darius.hp, darius.max) = (5000, 5000);
        w.units = vec![yorick, garen, darius, unit("melee_minion", EntityKindV1::Minion, 1, 300_000.0, 50_000.0, 300)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() },
                         MPlayer { team: 1, champion: DARIUS, ..Default::default() }];
        let mut me = Shepherd::default();
        w.sim(|sim| me.on_spawn(sim, 0, 0));
        (w, me)
    }

    fn tick(w: &mut World, me: &mut Shepherd) {
        for (name, caster, input) in w.due() {
            w.sim(|sim| match name.as_str() {
                "league_yorick:walkers" => WalkersFx.apply(sim, 0, caster, input),
                "league_yorick:maiden" => MaidenFx.apply(sim, 0, caster, input),
                other => panic!("an effect nobody registered: {other}"),
            });
        }
        if w.units[0].hp > 0 {
            w.sim(|sim| me.on_update(sim, 0, 0, 0));
        }
        w.step();
    }

    fn run(w: &mut World, me: &mut Shepherd, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    /// The copy's ask as the data lays it on the cast's target (3 ticks).
    fn ask(w: &mut World, target: usize, name: &str) -> usize {
        w.units[target].buffs.push((BuffV1::timed(name, 3), 3));
        w.tick
    }

    fn spawned(w: &World, name: &str) -> Vec<usize> {
        w.spawns.iter().filter(|s| s.name == name).filter_map(|s| s.gave).collect()
    }

    #[test]
    fn the_awakening_raises_three_walkers_that_fight_and_time_out() {
        let (mut w, mut me) = world();
        let t0 = ask(&mut w, GAREN, K_ASK);
        run(&mut w, &mut me, Q_HIT + 1);
        // three spawn_unit calls round Garen, his team, his numbers; the flag up when the data looks
        let walkers = spawned(&w, WALKER);
        assert_eq!(walkers.len(), 3);
        for s in w.spawns.iter() {
            assert_eq!((s.summoner, s.team, s.life as usize), (0, 0, WALK_LIFE));
            assert!(s.tick <= t0 + 3);
            let d = summon::dist((s.at.0 as f64, s.at.1 as f64), (340_000.0, 300_000.0));
            assert!((d - WALK_SPREAD).abs() < 2.0, "{d}");
            assert_eq!((s.stat.attack, s.stat.hp, s.attack.attack, s.attack.attack_ratio), (150, 300, 9, 13));
        }
        assert!(w.has(0, K_UNIT), "no flag on him when the data looks: the riding walkers would play too");
        assert_eq!(me.walkers.live.len(), 3);
        assert!(!w.has(GAREN, K_ASK) && !w.units[0].buffs.iter().any(|b| b.0.name().starts_with(W_UID)));
        // they bite Garen, 28 a bite, at most 10 bites each in their life
        run(&mut w, &mut me, WALK_LIFE);
        for id in &walkers {
            let bites = w.dealt(*id, DamageTypeV1::Ad);
            assert!(!bites.is_empty() && bites.len() <= 10 && bites.iter().all(|b| *b == (GAREN, 28)), "{bites:?}");
            assert!(!w.units[*id].valid || w.units[*id].died.is_some());
        }
        run(&mut w, &mut me, summon::WAKE_TICKS + 5);
        assert!(me.walkers.is_empty() && me.maiden.is_empty() && w.queue.is_empty());
        assert!(!w.has(0, K_UNIT), "the flag outlived its use");
    }

    #[test]
    fn no_unit_from_the_host_leaves_the_data_its_walkers() {
        // no slot, a refusal, an id that never reads as a unit, units gone at once
        for case in 0..4 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                2 => w.spawn_never = true,
                _ => {}
            }
            let t0 = ask(&mut w, GAREN, K_ASK);
            if case == 3 {
                run(&mut w, &mut me, 3);
                assert!(w.has(0, K_UNIT) && me.walkers.live.len() == 3, "case {case}");
                for id in spawned(&w, WALKER) {
                    w.units[id].valid = false;
                }
            }
            while w.tick < t0 + Q_HIT + 1 {
                tick(&mut w, &mut me);
            }
            assert!(!w.has(0, K_UNIT), "case {case}: the flag is on him when the data looks - no walkers at all");
            run(&mut w, &mut me, 200);
            assert!(me.walkers.is_empty() && w.queue.is_empty(), "case {case}");
        }
    }

    #[test]
    fn the_mist_makes_the_walkers_leap_and_pounce_once() {
        let (mut w, mut me) = world();
        ask(&mut w, GAREN, K_ASK);
        run(&mut w, &mut me, 30);
        let walkers = spawned(&w, WALKER);
        // the mist strikes Darius far south-east: only walkers within LEAP_REACH leap - none here
        ask(&mut w, DARIUS, E_ASK);
        run(&mut w, &mut me, 2);
        assert!(w.moves.is_empty());
        // Darius steps in, 100000 from the walkers: they leap to his side, the pounce (20 + 30 % of 150 = 65) once
        (w.units[DARIUS].x, w.units[DARIUS].y) = (440_000.0, 300_000.0);
        ask(&mut w, DARIUS, E_ASK);
        run(&mut w, &mut me, 2);
        assert_eq!(w.moves.len(), 3, "{:?}", w.moves);
        for (_, id, at) in &w.moves {
            assert!(walkers.contains(id));
            let d = summon::dist((at.0 as f64, at.1 as f64), (440_000.0, 300_000.0));
            assert!(d <= LEAP_SIDE + 1.0, "{d}");
        }
        assert_eq!(w.dealt(0, DamageTypeV1::Ad), vec![(DARIUS, 65)]);
        assert_eq!(w.viewed(K_LEAP_VIEW), 1);
        // no walkers out: the mist does nothing natively
        let (mut w, mut me) = world();
        ask(&mut w, DARIUS, E_ASK);
        run(&mut w, &mut me, 2);
        assert!(w.moves.is_empty() && w.damage.is_empty() && !w.has(DARIUS, E_ASK));
    }

    #[test]
    fn the_maiden_comes_with_her_escort_and_her_time_holds_the_bonus() {
        let (mut w, mut me) = world();
        // the data's R: r_on on him and the mark on Garen for R_T, the ask on Garen
        w.units[0].buffs.push((BuffV1::timed(R_ON, R_T), R_T));
        w.units[GAREN].buffs.push((BuffV1::timed(MAIDEN, R_T), R_T));
        let t0 = ask(&mut w, GAREN, M_ASK);
        run(&mut w, &mut me, R_REL + 1);
        let her = spawned(&w, MAIDEN_UNIT);
        assert_eq!(her.len(), 1);
        let s = w.spawns.iter().find(|s| s.name == MAIDEN_UNIT).unwrap().clone();
        assert_eq!((s.at, s.life as usize), ((340_000, 289_000), MAID_LIFE));
        assert_eq!((s.stat.hp, s.stat.defence, s.attack.attack, s.attack.attack_ratio), (2400, 68, 20, 45));
        assert_eq!(spawned(&w, WALKER).len(), R_N);
        assert!(w.spawns.iter().filter(|s| s.name == WALKER).all(|s| s.life as usize == MAID_LIFE));
        assert!(w.has(0, M_UNIT), "no flag when the data raises the riding Maiden");
        assert_eq!((me.maiden.live.len(), me.walkers.live.len()), (1, R_N));
        assert!(me.walkers.live.iter().all(|m| m.extra.kind == Walk::Escort));
        // r_on and the mark follow her time, not R_T
        let left = |w: &World, id: usize, name: &str| w.units[id].buffs.iter().filter(|b| b.0.name() == name).map(|b| b.1).max();
        assert!(left(&w, 0, R_ON).unwrap() > R_T, "r_on not stretched to her time");
        assert!(left(&w, GAREN, MAIDEN).unwrap() > R_T);
        assert_eq!(w.units[0].buffs.iter().filter(|b| b.0.name() == R_ON).count(), 1);
        // she claws Garen: 20 + 45 % of 150 = 87
        run(&mut w, &mut me, 200);
        let claws = w.dealt(her[0], DamageTypeV1::Ad);
        assert!(!claws.is_empty() && claws.iter().all(|c| *c == (GAREN, 87)), "{claws:?}");
        // killed: she no longer stands - r_on and the mark go with her
        w.hurt(her[0], 1_000_000);
        run(&mut w, &mut me, 3);
        assert!(!w.has(0, R_ON) && !w.has(GAREN, MAIDEN));
        assert!(me.maiden.live.is_empty());
        let _ = t0;
    }

    #[test]
    fn no_maiden_from_the_host_leaves_the_data_its_maiden() {
        for case in 0..3 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_never = true,
                _ => {}
            }
            let t0 = ask(&mut w, GAREN, M_ASK);
            if case == 2 {
                run(&mut w, &mut me, 3);
                assert!(w.has(0, M_UNIT));
                for id in spawned(&w, MAIDEN_UNIT) {
                    w.units[id].valid = false;
                }
            }
            while w.tick < t0 + R_REL + 1 {
                tick(&mut w, &mut me);
            }
            assert!(!w.has(0, M_UNIT), "case {case}: the flag is on him when the data looks - no Maiden at all");
        }
    }

    #[test]
    fn his_death_leaves_the_units_fighting() {
        let (mut w, mut me) = world();
        ask(&mut w, GAREN, K_ASK);
        run(&mut w, &mut me, 60);
        let walkers = spawned(&w, WALKER);
        let before: usize = walkers.iter().map(|id| w.dealt(*id, DamageTypeV1::Ad).len()).sum();
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.on_dead(sim, 0));
        assert!(me.walkers.is_empty());
        run(&mut w, &mut me, 200);
        let after: usize = walkers.iter().map(|id| w.dealt(*id, DamageTypeV1::Ad).len()).sum();
        assert!(after > before, "the walkers stopped when he died");
        assert!(w.queue.is_empty());
    }

    #[test]
    fn the_log_tells_the_units_whole_lives() {
        let (mut w, mut me) = world();
        ask(&mut w, GAREN, K_ASK);
        run(&mut w, &mut me, 100);
        let walkers = spawned(&w, WALKER);
        let mut dealt = 28;
        w.sim(|sim| me.on_attack(sim, 0, walkers[0], GAREN, &mut dealt));
        w.players[1].gold += 14;
        w.hurt(walkers[1], 100_000);
        w.units[0].buffs.push((BuffV1::timed(R_ON, R_T), R_T));
        ask(&mut w, GAREN, M_ASK);
        run(&mut w, &mut me, 100);
        (w.units[DARIUS].x, w.units[DARIUS].y) = (400_000.0, 300_000.0);
        ask(&mut w, DARIUS, E_ASK);
        run(&mut w, &mut me, 600);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" WALKER") || l.contains(" MAIDEN ") || l.contains(" HOOK ")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "WALKERS ASK #", "the Awakening on #1 league_garen at (340000,300000): 3 walkers asked for round it",
            "WALKERS SPAWN #", "3 of 3 units [4, 5, 6] for team 0 round (340000,300000): 'league_yorick_walker' for 600 ticks, attack \
             150 ap 0 hp 300 def 0 mr 0 speed 1100; hits 9 + 13% of its attack, range 18000, every 60 ticks (23 long, lands at 10)",
            "WALKER #1 LOOK #", "(the Awakening's): #4 reads back as name 'league_yorick_walker' kind summon team 0",
            " of 600 ticks, at (", "near it: champion #1 league_garen",
            "OVER #", "KILLED after ", "p1 gold +14",
            "HOOK #", "on_attack: entity #4 (the walker #1) -> #1 league_garen, damage 28",
            "MAIDEN ASK #", "Eulogy of the Isles on #1 league_garen at (", "the Maiden asked for 11000 behind it, 2 walkers round her",
            "MAIDEN SPAWN #", "'league_yorick_maiden' for 900 ticks", "her escort: 2 of 2 walkers",
            "MAIDEN #1 LOOK #", "league_yorick_r_on on Yorick and league_yorick_maiden on #1 set for her 899 ticks",
            "MAIDEN #1 DRESS #", "league_yorick_r_on is on Yorick, league_yorick_maiden is on #1",
            "(the Maiden's escort)", "WALKERS LEAP #", "the mist struck #2 league_darius at (400000,300000): ",
            "moved by entity_set_pos), 0 out of reach; the pounce 65 physical, once",
            "TIMED OUT after ", "WAKE #",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
        let longest = mine.iter().map(|l| l.len()).max().unwrap();
        assert!(longest < 700, "a line of {longest} bytes");
    }
}
