//! 约里克附加包：数据做不到、和英雄联盟不一样的地方，这里照英雄联盟做。
//!
//! `mod.override_info` 把主包的约里克换成 `override/` 里的副本（tools/kit/build_yorick.py --native，make_override.py 写），
//! `passive` 换成本包的 `league_yorick:shepherd`：
//!
//! - **坟墓照英雄联盟挖**：主包读不到「这一铲打死了谁」，所以临终仪式打英雄挖一座坟、打别的每两下挖一座。副本的这一铲给
//!   约里克挂几拍 `league_yorick_q_win`，本包在它还在时，每有一个小兵 / 野怪被他打死就挖一座坟（打英雄照旧由数据挖），
//!   不再「每两下」。0.1.1（2026-11-03 夜里的日志：6 条命一座坟都没挖）：`q_win` 和这一铲同一拍挂上。
//!   0.3.0：最多 4 座（g1..g4，和数据一样一起计时）；附近别的敌人死掉，每第 N 个也挖一座（N 按等级 8 -> 2）。
//! - **雾行者和迷雾室女是真的单位（0.2.0）**：稳定 mod API 的 `spawn_unit`（公用部分在萨科附加包的 `summon.rs`，一个召唤者
//!   好几个单位用它的 `Flock`）。唤醒的雾行者（副本给目标挂 `K_ASK` / `K_ASK4`：3 / 4 只，0.3.0 每座坟一只）、黑雾让雾行者
//!   扑过去（`E_ASK`）、迷雾室女和她的雾行者（`M_ASK`）。宿主给不出单位时数据照主包放挂着的那一套（`K_UNIT` / `M_UNIT`）。
//!   0.2.1：雾行者那本账一次只等一个要（[`Held`]）。
//!
//! 0.3.0（2026-11-22，用户：「之前玩掘墓我也发现没完美还原 没有那个地形框出来的技能 其他我不知道 你再核对一下」）照英雄联盟
//! 现在的约里克：
//!
//! - **暗灵缠身是一圈真的墙**（[`wall`]）：副本的 W 给落点的英雄挂 `W_ASK`（记圆心），立墙那一 tick 给他挂 `W_UP`：本包立墙
//!   `w_t` tick，只挡敌人，墙线上的拨开，闪现、无视地形的放过；不能被打塌（原因见 wall.rs）。
//! - **临终仪式按已损失生命回复**：副本的这一铲挂 `Q_HL`（数据自己的回复去掉），本包两拍后回复 [`q_heal`]：按等级的固定值 +
//!   已损失生命的 6–10%，打的不是英雄（没有 `Q_CH`）减半。
//! - **朝被标记的英雄走时加速**：黑雾的标记（`E_MARK`，数据挂在英雄身上）在时，约里克、雾行者、室女这一 tick 是朝它走的
//!   （位移和朝向它的方向夹角小于 60 度）就挂 3 tick 的 `E_MS`，移速 +18–30%（按等级）。
//! - **室女跟着约里克、远程攻击、挂标记**：她不再自己追人（移速 1，本包用强制位移让她跟在他身后 `MAID_BACK`），每
//!   `MAID_COOL` tick 朝她 `MAID_RANGE` 以内最近的敌方英雄（没有就打别的敌人）放一道魂弹（`spawn_projectile`，画面是数据的
//!   `r_bolt`），打中造成魔法伤害，英雄挂上她的标记（`R_MKV`，画面在数据的 view_buffs 里）；约里克的普攻或黑雾打中有标记的
//!   英雄（副本挂 3 tick 的 `HIT`）消耗标记，造成它最大生命 2 / 2.5 / 3% 的魔法伤害（按等级）。带的雾行者按等级 2 / 3 / 4 只；
//!   **亡灵大军**：她附近的敌人死掉、她手下的雾行者不到 4 只时，从尸体上拉起一只。约里克阵亡时雾行者跟着没、室女 3 秒内
//!   掉光生命（`entity_set_hp`；设成 0 不死的话放逐到时间）。
//!
//! 数字从英雄数据的 `passive.params`（坟、加伤、墙）和 `src/lib.rs` 的常量来（单位的数字，`make_override.py` 和主包的参数表 P、
//! 单位图的动作对照）。不用全局变量，服务端预模拟和你看的那场各算各的。日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yorick.log`，每次启动游戏重写。
//! 测试开关：日志旁边的 `league_yorick.cfg`（`summon.rs`：`unit=off` / `still=1` / `name=`）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;
pub mod wall;

use summon::{Event, Flock, Pt};

const ID: &str = "league_yorick";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_yorick") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// On him for a few ticks after a Last Rites blow: a unit dying meanwhile died to it.
pub const Q_WIN: &str = "league_yorick_q_win";
/// On him with a Last Rites blow (the copy has no heal of its own): the add-on heals by his missing health.
pub const Q_HL: &str = "league_yorick_q_hl";
/// On him when the blow's champion twin landed: the blow struck a champion (the full heal).
pub const Q_CH: &str = "league_yorick_q_ch";
/// On a champion his attack or the mist struck while the Maiden stands (3 ticks): her mark on it is spent.
pub const HIT: &str = "league_yorick_hit";
/// His graves, counted on him (the data's ladder: g1, g1 + g2, ... all four together; the Awakening takes them off).
pub const GRAVES: [&str; 4] = ["league_yorick_g1", "league_yorick_g2", "league_yorick_g3", "league_yorick_g4"];

// ---- 雾行者和迷雾少女作为单位（0.2.0）：主包的数字（make_override.py 对照参数表 P 检查，改主包就改这里）----

/// The Awakening's walkers with three graves (k_n), each bite (k_dmg + k_ratio % of his attack, every k_p ticks); the
/// riding walkers' time (k_t: what the units replace).
pub const K_N: usize = 3;
pub const WALK_HIT: usize = 9;
pub const WALK_HIT_AD: usize = 13;
pub const WALK_COOL: usize = 60;
pub const K_T: usize = 360;
/// The pounce when Mourning Mist strikes a champion (k_jmp + k_jmp_r % of his attack, once).
pub const LEAP_HIT: usize = 20;
pub const LEAP_HIT_AD: usize = 30;
/// The Maiden's escort at the main pack's level (r_n); her bolts (r_dmg + r_ratio % of his attack, every r_p ticks);
/// the riding Maiden's time and r_on's (r_t).
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
/// A walker lives `WALK_LIFE` ticks (League: until killed or he dies; the riding ones 6 s), with `WALK_HP_PCT` % of his
/// health cap (League: 100-331 against his 650-2588), no armour or magic resistance (League's), his move speed (League:
/// 325, +60 near him, against his 340), reach `WALK_RANGE` (League: 125 against his 175).
pub const WALK_LIFE: usize = 600;
pub const WALK_HP_PCT: usize = 15;
pub const WALK_RANGE: usize = 18_000;
/// The Maiden lives `MAID_LIFE` ticks (League: until killed or he dies; the main pack's r_t), with `MAID_HP_PCT` % of his
/// health cap (League: 1050-3700 against his 1220-2588), `MAID_DEF_PCT` % of his armour as armour and magic resistance
/// (League: 30-100 both, against his 36-112). 0.3.0: she does not walk by herself (move speed 1, her own attack reaches
/// nobody: range 1) - the add-on keeps her `MAID_BACK` behind him and shoots her bolts at `MAID_RANGE` (League: 600, R's
/// range here).
pub const MAID_LIFE: usize = 900;
pub const MAID_HP_PCT: usize = 120;
pub const MAID_DEF_PCT: usize = 85;
pub const MAID_RANGE: f64 = 40_000.0;
pub const MAID_BACK: f64 = 15_000.0;
/// She glides to her spot behind him once she is farther than this from it (League: she trails him, and comes back from
/// beyond 1200 of him), at his speed, faster from beyond `MAID_LEASH`.
pub const MAID_SLACK: f64 = 15_000.0;
pub const MAID_LEASH: f64 = 80_000.0;
/// Her bolt's speed a tick and its mark's ticks on a champion (League: until spent; 4 s here).
pub const BOLT_SPEED: u64 = 3_500;
pub const MARK_T: usize = 240;
/// After his death she loses her health in `FADE_STEPS` steps `FADE_EVERY` ticks apart (League: within 3 s).
pub const FADE_STEPS: usize = 6;
pub const FADE_EVERY: usize = 30;
/// The walkers rise this far round the Awakening's target; the Maiden this far behind (up the screen from) the champion
/// she is raised on, her escort as far round her.
pub const WALK_SPREAD: f64 = 12_000.0;
pub const MAID_BEHIND: f64 = 11_000.0;
/// Walkers within `LEAP_REACH` of the champion the mist struck leap to `LEAP_SIDE` from him (League: within 1500 of the
/// cursed enemy - 2.14 times E's 700 - against our E range of 55000).
pub const LEAP_REACH: f64 = 118_000.0;
pub const LEAP_SIDE: f64 = 9_000.0;
/// Deaths near him count toward a grave within `GRAVE_NEAR` (League: "nearby"), near her toward a raised walker within
/// `MAID_RANGE`; her escort is raised up to `ARMY_CAP` (League: fewer than 4 under her).
pub const GRAVE_NEAR: f64 = 60_000.0;
pub const ARMY_CAP: usize = 4;
/// The haste toward a champion marked by the mist: within this, moving within 60 degrees of it.
pub const HASTE_NEAR: f64 = 90_000.0;
/// The copy's asks (on the target, 3 ticks), the flags on him while units stand in for the riding pictures, the handoffs.
pub const K_ASK: &str = "league_yorick_k_ask";
pub const K_ASK4: &str = "league_yorick_k_ask4";
pub const K_UNIT: &str = "league_yorick_k_unit";
pub const M_ASK: &str = "league_yorick_m_ask";
pub const M_UNIT: &str = "league_yorick_m_unit";
pub const E_ASK: &str = "league_yorick_e_ask";
pub const W_ASK: &str = "league_yorick_w_ask";
pub const W_UP: &str = "league_yorick_w_up";
/// On him once the wall broke (wall.rs): the copy's next piece of the picture is the fall, the rest none.
pub const W_DOWN: &str = "league_yorick_w_down";
pub const W_UID: &str = "league_yorick_w_uid";
pub const M_UID: &str = "league_yorick_m_uid";
/// The data's flag while the Maiden stands (Q's cooldown halved; the copy's attack marks the champions it strikes).
pub const R_ON: &str = "league_yorick_r_on";
/// The mist's mark on a champion (the data's), the haste toward it, the Maiden's mark on a champion (its picture is the
/// data's view buff), her bolt (the data's projectile picture).
pub const E_MARK: &str = "league_yorick_e_mark";
pub const E_MS: &str = "league_yorick_e_ms";
pub const R_MKV: &str = "league_yorick_r_mkv";
pub const R_BOLT: &str = "league_yorick_r_bolt";
/// The main pack's sounds and pictures the natives play.
pub const K_SPAWN_SFX: &str = "league_yorick_k_spawn";
pub const K_LEAP_VIEW: &str = "league_yorick_k_leap";
pub const R_SPAWN_SFX: &str = "league_yorick_r_spawn";
pub const R_CLAW: &str = "league_yorick_r_claw";
pub const R_MARK_VIEW: &str = "league_yorick_r_mark";
pub const Q_GRAVE: &str = "league_yorick_q_grave";
/// Walkers on the books at once (two Awakenings and an escort).
pub const WALK_CAP: usize = 10;
/// Ticks a flag stays (the data reads it once, about 15 ticks after the cast), and the handoff buffs.
const FLAG_TICKS: usize = 60;
const UID_TICKS: usize = 6;
/// A unit gone within this many ticks was never really there: the flag goes and the data's picture plays.
pub const LOST_AGE: usize = 6;
/// The level the numbers by level end at (TFM2's champions reach about 12).
pub const MAX_LEVEL: usize = 12;

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
    /// 室女的标记被消耗时，按它最大生命的这么多百分比（最高一级；低两级是它的 2/3、5/6）。
    pub r_pct: usize,
    /// 一座坟留多少拍（数据的 g1..g4 一起计时）。
    pub g_t: usize,
    /// 墙线半径、墙的半厚（圈里的中心离圆心不超过 w_r - w_half，圈外的不少于 w_r + w_half）、立多久、立墙前的延时。
    pub w_r: usize,
    pub w_half: usize,
    pub w_t: usize,
    pub w_delay: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { r_pct: 3, g_t: 1800, w_r: 30000, w_half: 10000, w_t: 120, w_delay: 45 }
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
            "w_r" => p.w_r = v,
            "w_half" => p.w_half = v,
            "w_t" => p.w_t = v,
            "w_delay" => p.w_delay = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

fn lvl(level: usize) -> usize {
    level.clamp(1, MAX_LEVEL) - 1
}

/// Graves after one more is dug, with `have` on him (the data's ladder: at most 4).
pub fn graves_after(have: usize) -> usize {
    (have + 1).min(GRAVES.len())
}

/// Graves on him: the highest rung (the rungs go up and run out together).
pub fn graves_of(has: [bool; 4]) -> usize {
    has.iter().rposition(|&h| h).map_or(0, |k| k + 1)
}

/// Deaths near him that dig a grave (League: every 8th at level 1 down to every 2nd at 18; 1..12 here).
pub fn deaths_per_grave(level: usize) -> usize {
    8 - (6 * lvl(level) + 5) / 11
}

/// Last Rites' heal (League: 10-78 by level + 6-10% of his missing health, half on anything but a champion).
pub fn q_heal(level: usize, hp: usize, max: usize, champion: bool) -> usize {
    let l = lvl(level);
    let amount = 10 + 6 * l + max.saturating_sub(hp) * (6 + 4 * l / (MAX_LEVEL - 1)) / 100;
    if champion { amount } else { amount / 2 }
}

/// The haste toward a champion the mist marked, in % (League: 18-30% by E's rank; by level here).
pub fn haste(level: usize) -> usize {
    18 + 12 * lvl(level) / (MAX_LEVEL - 1)
}

/// R's rank by level (League: 6 / 11 / 16 of 18; 5 / 8 / 11 of 12 here).
pub fn r_rank(level: usize) -> usize {
    match level {
        0..=7 => 1,
        8..=10 => 2,
        _ => 3,
    }
}

/// The Maiden's escort (League: 2 / 3 / 4 by R's rank).
pub fn escort(level: usize) -> usize {
    1 + r_rank(level)
}

/// Her mark spent, in per mille of the champion's max health (League: 2 / 2.5 / 3%; r_pct is the top rank).
pub fn mark_per_mille(p: &Params, level: usize) -> usize {
    p.r_pct * 10 * (r_rank(level) + 3) / 6
}

/// Is a unit that stepped from `last` to `now` going toward `foe` (within 60 degrees)?
pub fn toward(last: Pt, now: Pt, foe: Pt) -> bool {
    let (sx, sy) = (now.0 - last.0, now.1 - last.1);
    let (fx, fy) = (foe.0 - now.0, foe.1 - now.1);
    let (s, f) = (sx.hypot(sy), fx.hypot(fy));
    s > 1.0 && f > 1.0 && (sx * fx + sy * fy) / (s * f) > 0.5
}

/// Where the Maiden keeps to: `MAID_BACK` from him on her side (up the screen when she is on top of him).
pub fn follow_spot(him: Pt, her: Pt) -> Pt {
    let d = summon::dist(him, her);
    let (ux, uy) = if d < 1.0 { (0.0, -1.0) } else { ((her.0 - him.0) / d, (her.1 - him.1) / d) };
    (him.0 + ux * MAID_BACK, him.1 + uy * MAID_BACK)
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
/// and magic resistance, his attack, move speed 1 (the add-on moves her), her own claw reaching nobody (range 1): her bolts
/// are the add-on's.
pub fn maiden_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    let def = stat.defence * MAID_DEF_PCT / 100;
    summon::Spec {
        name: MAIDEN_UNIT.to_string(),
        life: MAID_LIFE,
        stat: StatV1 { attack: stat.attack, magic_power: 0, hp: (max_hp * MAID_HP_PCT / 100).max(1), defence: def,
                       magic_resistance: def, move_speed: 1, hp_regen: 0, stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: MAID_HIT_AD, attack: MAID_HIT, range: 1, cooltime: MAID_COOL,
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

/// A bolt's damage before magic resistance, from his attack.
pub fn bolt_damage(attack: usize) -> usize {
    MAID_HIT + attack * MAID_HIT_AD / 100
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

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
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

/// The Awakening's walkers for Yorick `me` round `at`: `n` of them (a grave each), the flag for the data on him when any
/// came. -> how many came.
fn make_walkers(sim: &mut StableSim<'_>, me: usize, at: Pt, n: usize, by: &str) -> usize {
    let Some((team, stat, max, here)) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1, pos(&e))) else { return 0 };
    let spec = walker_spec(&stat, max, WALK_LIFE).with(&KNOBS);
    let ids = spawn_all(sim, me, team, &walker_points(at, here, n), &spec, W_UID);
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
        wlog(format!("{} WALKERS SPAWN #{k} ({by}): {} of {n} units {:?} for team {team} round {}: {}", head(sim, me), ids.len(),
                     ids, summon::pt(at), spec.shown()));
    }
    ids.len()
}

/// The Maiden for Yorick `me` behind the champion at `at`, and her escort (`n`) round her; the flag for the data on him
/// when she came. -> she came.
fn make_maiden(sim: &mut StableSim<'_>, me: usize, at: Pt, n: usize, by: &str) -> bool {
    let Some((team, stat, max, here)) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1, pos(&e))) else { return false };
    let spec = maiden_spec(&stat, max).with(&KNOBS);
    let spot = (at.0, (at.1 - MAID_BEHIND).max(0.0));
    let her = spawn_all(sim, me, team, &[spot], &spec, M_UID);
    let Some(&id) = her.first() else {
        if let Some(k) = tally(sim, "maiden fail") {
            wlog(format!("{} MAIDEN SPAWN FAILED #{k} ({by}): spawn_unit gave no unit for '{}' at {} - she follows him as a \
                          picture as before", head(sim, me), spec.name, summon::pt(spot)));
        }
        return false;
    };
    flag(sim, me, M_UNIT);
    sim.play_sfx(R_SPAWN_SFX, me, &at_input(spot));
    let escort = walker_spec(&stat, max, MAID_LIFE).with(&KNOBS);
    let ids = spawn_all(sim, me, team, &walker_points(spot, here, n), &escort, W_UID);
    if let Some(k) = tally(sim, "maiden spawn") {
        wlog(format!("{} MAIDEN SPAWN #{k} ({by}): unit #{id} for team {team} at {}: {}; her escort: {} of {n} walkers {:?}",
                     head(sim, me), summon::pt(spot), spec.shown(), ids.len(), ids));
    }
    true
}

/// One walker raised from a body near the Maiden (League's Army of the Dead), living `life` ticks.
fn make_raised(sim: &mut StableSim<'_>, me: usize, at: Pt, life: usize) -> bool {
    let Some((team, stat, max)) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1)) else { return false };
    let spec = walker_spec(&stat, max, life.max(1)).with(&KNOBS);
    let ids = spawn_all(sim, me, team, &[at], &spec, W_UID);
    if let Some(k) = tally(sim, "raised") {
        wlog(format!("{} RAISED #{k}: a walker from the body at {} (the Maiden's army of the dead): {}", head(sim, me),
                     summon::pt(at), if ids.is_empty() { "spawn_unit gave no unit".to_string() } else { format!("unit #{} for {life} ticks", ids[0]) }));
    }
    !ids.is_empty()
}

/// `:walkers` - the passive queues it when the Awakening is cast; the input is the target's spot, `dir_x` how many.
struct WalkersFx;

impl StableEffectType for WalkersFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = point(&input).or_else(|| sim.get_entity(caster).map(|e| pos(&e))) else { return };
        let n = if input.dir_x > 0 { input.dir_x as usize } else { K_N };
        make_walkers(sim, caster, at, n, "the queued effect");
    }
}

/// `:maiden` - the passive queues it when R is cast; the input is the champion's spot, `dir_x` her escort.
struct MaidenFx;

impl StableEffectType for MaidenFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = point(&input).or_else(|| sim.get_entity(caster).map(|e| pos(&e))) else { return };
        let n = if input.dir_x > 0 { input.dir_x as usize } else { R_N };
        make_maiden(sim, caster, at, n, "the queued effect");
    }
}

/// `:raise` - a walker from a body near the Maiden; the input is where it fell, `dir_x` the ticks it lives.
struct RaiseFx;

impl StableEffectType for RaiseFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = point(&input) else { return };
        make_raised(sim, caster, at, input.dir_x.max(1) as usize);
    }
}

/// `:bolt` - the Maiden's bolt hit (spawn_projectile's effect): magic from his attack, her mark on a champion.
struct BoltFx;

impl StableEffectType for BoltFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(t) = target_of(&input) else { return };
        let Some(champion) = sim.get_entity(t).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.is_champion()) else { return };
        let Some(attack) = sim.get_entity(caster).map(|e| e.stat().attack) else { return };
        let dmg = bolt_damage(attack);
        sim.deal_damage_typed(caster, t, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        let on = InputTargetV1::target(t);
        sim.play_view_effect(R_CLAW, caster, &on, 0, 0, 0);
        sim.play_sfx(R_CLAW, caster, &on);
        if champion {
            sim.entity_remove_buff(t, R_MKV);
            sim.add_buff(t, &BuffV1::timed(R_MKV, MARK_T));
        }
        if let Some(k) = tally(sim, "bolt hit") {
            wlog(format!("{} BOLT HIT #{k}: #{t} {} took {dmg} magic{}", head(sim, caster), name_of(sim, t),
                         if champion { format!("; her mark on it for {MARK_T} ticks") } else { String::new() }));
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        (0, bolt_damage(caster_stat.attack))
    }
}

/// `:fade` - after his death the Maiden loses her health a step at a time (`dir_x` the step); the last step leaves her at 0,
/// and one not dead a step later is banished to her time.
struct FadeFx;

impl StableEffectType for FadeFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(her) = target_of(&input) else { return };
        let step = input.dir_x.max(1) as usize;
        let Some((hp, max)) = sim.get_entity(her).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        if step > FADE_STEPS {
            let ok = sim.entity_banish(caster, her, input.dir_y.max(1) as usize, "", "");
            if let Some(k) = tally(sim, "fade") {
                wlog(format!("{} MAIDEN FADE #{k}: #{her} still up at {hp} health after her last step - banished to her time: {}",
                             head(sim, caster), if ok { "yes" } else { "entity_banish REFUSED" }));
            }
            return;
        }
        let goal = max * (FADE_STEPS - step) / FADE_STEPS;
        let set = goal < hp && sim.entity_set_hp(her, goal);
        if let Some(k) = tally(sim, "fade") {
            wlog(format!("{} MAIDEN FADE #{k}: step {step} of {FADE_STEPS} - #{her} {hp} -> {goal} health ({})", head(sim, caster),
                         if set { "set" } else if goal >= hp { "she had less" } else { "entity_set_hp REFUSED" }));
        }
    }
}

// ===================== 被动 =====================

/// Which walkers these are.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum Walk {
    /// Raised by the Awakening.
    #[default]
    Awake,
    /// The Maiden's escort (and the walkers her army raises).
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

/// A walker as the passive keeps it: its kind, where it stood a tick ago (the haste toward a marked champion).
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct WalkerBook {
    pub kind: Walk,
    pub last: Option<Pt>,
}

/// The Maiden as the passive keeps her: the tick she was read as a unit, whether the look a tick later was logged, the
/// tick of her next bolt, where she stood a tick ago.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct MaidBook {
    pub looked: usize,
    pub dressed: bool,
    pub next_bolt: usize,
    pub last: Option<Pt>,
}

/// What an ask brings.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Ask {
    /// The Awakening's walkers (how many).
    Awake(usize),
    /// The Maiden and her escort (how many walkers).
    Maiden(usize),
    /// A walker from a body near her (the ticks it lives).
    Raise(usize),
}

impl Ask {
    fn shown(self) -> &'static str {
        match self {
            Ask::Awake(_) => "WALKERS",
            Ask::Maiden(_) => "MAIDEN",
            Ask::Raise(_) => "RAISE",
        }
    }
}

/// An ask laid while the walkers' last ask still waited for its units: kept until that one is answered (summon::Flock
/// gives all the handoffs of a tick to the oldest waiting ask, so two waiting at once would take each other's walkers).
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Held {
    /// The tick it was laid.
    pub tick: usize,
    pub target: usize,
    /// Where the target stood then (used if it is gone when the ask goes out).
    pub at: Pt,
    pub what: Ask,
}

/// Asks held at once (the oldest is dropped past it), and the ticks one is held at most before it is dropped. A waiting
/// ask is answered or given up within `FLOCK_WAIT` + 1 ticks, so a held one normally goes out within 5; the copy's data
/// reads the units' flag `Q_HIT` / `R_REL` ticks after the cast, so one that could only go out later is dropped instead
/// (its units would stand beside the riding pictures): the data plays those, as when the host gives no unit.
pub const HELD_MAX: usize = 4;
pub const HELD_TICKS: usize = Q_HIT - 4;

/// An enemy as this tick's scan read it.
#[derive(Clone, Copy, Debug)]
struct Foe {
    id: usize,
    at: Pt,
    champion: bool,
    counts: bool,
}

/// 每个约里克一份：参数、日志计数、他的单位、他的墙。
#[derive(Clone)]
struct Shepherd {
    p: Params,
    graves: usize,
    marks: usize,
    /// His own unit (on_dead is given the player).
    me: usize,
    walkers: Flock<WalkerBook>,
    maiden: Flock<MaidBook>,
    /// Asks held while the walkers' last one waits (oldest first), and the tick of the last ask that went out.
    held: Vec<Held>,
    asked: usize,
    walls: wall::Walls,
    /// The enemies (minions, monsters, champions) alive near him at the last scan, and the units Last Rites killed
    /// (their deaths dug through q_win already); deaths near him since the last grave they dug.
    near: HashMap<usize, (Pt, bool)>,
    q_dug: Vec<usize>,
    deaths: usize,
    /// Last Rites' heal: the tick it is due (two after q_hl was first seen).
    heal_due: Option<usize>,
    /// Where he stood a tick ago (the haste).
    last: Option<Pt>,
    /// W_UP was on him the last tick (a wall rises when it comes up).
    had_up: bool,
}

impl Default for Shepherd {
    fn default() -> Self {
        Shepherd { p: Params::default(), graves: 0, marks: 0, me: 0, walkers: Flock::new(W_UID, WALK_CAP, WALK_LIFE),
                   maiden: Flock::new(M_UID, 1, MAID_LIFE), held: Vec::new(), asked: 0, walls: wall::Walls::default(),
                   near: HashMap::new(), q_dug: Vec::new(), deaths: 0, heal_due: None, last: None, had_up: false }
    }
}

impl Shepherd {
    /// One grave more (the data's ladder: all the rungs up to the new count, timed together; full stays full).
    fn dig(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        let Some(e) = sim.get_entity(me) else { return };
        let have = graves_of([has(&e, GRAVES[0]), has(&e, GRAVES[1]), has(&e, GRAVES[2]), has(&e, GRAVES[3])]);
        let at = pos(&e);
        let k = graves_after(have);
        for g in &GRAVES[..k] {
            sim.entity_remove_buff(me, g);
            sim.add_buff(me, &BuffV1::timed(g, self.p.g_t));
        }
        sim.play_view_effect(Q_GRAVE, me, &at_input(at), 0, 0, 0);
        self.graves += 1;
        if let Some(n) = tally(sim, "grave") {
            wlog(format!("{} GRAVE #{n}: {why} - {k} grave(s) now ({} dug by the add-on)", head(sim, me), self.graves));
        }
    }

    /// The enemies near him this tick, against the last scan: who died (a grave every Nth; a walker near the Maiden),
    /// the copy's asks, the marks to spend. -> the enemies (for the haste).
    fn scan(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, here: Pt) -> Vec<Foe> {
        struct Seen {
            foe: Foe,
            k: bool,
            k4: bool,
            m: bool,
            e: bool,
            w: bool,
            hit: bool,
            mark: bool,
            e_mark: bool,
        }
        let seen: Vec<Seen> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive())
            .map(|u| {
                let kind = u.kind();
                let counts = matches!(kind, Some(EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Champion));
                let mut s = Seen { foe: Foe { id: u.id(), at: pos(&u), champion: u.is_champion(), counts }, k: false, k4: false,
                                   m: false, e: false, w: false, hit: false, mark: false, e_mark: false };
                // 每 tick 每个敌人都看一遍：不拷名字，直接比
                for b in (0..u.buff_count()).filter_map(|i| u.buff_at(i)) {
                    match b.name() {
                        K_ASK => s.k = true,
                        K_ASK4 => s.k4 = true,
                        M_ASK => s.m = true,
                        E_ASK => s.e = true,
                        W_ASK => s.w = true,
                        HIT => s.hit = true,
                        R_MKV => s.mark = true,
                        E_MARK => s.e_mark = true,
                        _ => {}
                    }
                }
                s
            })
            .collect();
        // deaths: near him at the last scan, not alive now
        let alive: std::collections::HashSet<usize> = seen.iter().map(|s| s.foe.id).collect();
        let gone: Vec<(usize, Pt, bool)> = self.near.iter().filter(|(id, _)| !alive.contains(id)).map(|(id, (at, c))| (*id, *at, *c)).collect();
        self.near = seen.iter().filter(|s| s.foe.counts && summon::dist(s.foe.at, here) <= GRAVE_NEAR.max(MAID_RANGE + MAID_LEASH))
            .map(|s| (s.foe.id, (s.foe.at, s.foe.champion))).collect();
        for (id, at, champion) in gone {
            self.died(sim, me, id, at, champion, here);
        }
        let now = sim.tick();
        for s in &seen {
            let (id, at) = (s.foe.id, s.foe.at);
            if s.k || s.k4 {
                sim.entity_remove_buff(id, K_ASK);
                sim.entity_remove_buff(id, K_ASK4);
                self.ask_or_hold(sim, me, id, at, Ask::Awake(if s.k4 { 4 } else { K_N }));
            }
            if s.m {
                sim.entity_remove_buff(id, M_ASK);
                let n = escort(sim.get_entity(me).map_or(1, |e| e.level()));
                self.ask_or_hold(sim, me, id, at, Ask::Maiden(n));
            }
            if s.e {
                sim.entity_remove_buff(id, E_ASK);
                self.leap(sim, me, id, at);
            }
            if s.w {
                sim.entity_remove_buff(id, W_ASK);
                self.walls.asked(now, id, at);
                if let Some(k) = tally(sim, "wall ask") {
                    wlog(format!("{} WALL ASK #{k}: Dark Procession lands under #{id} {} at {} - the ring rises in {} ticks",
                                 head(sim, me), name_of(sim, id), summon::pt(at), self.p.w_delay));
                }
            }
            if s.hit {
                sim.entity_remove_buff(id, HIT);
                if s.mark && s.foe.champion {
                    self.spend(sim, me, id);
                }
            }
        }
        seen.into_iter().filter(|s| s.e_mark && s.foe.champion).map(|s| s.foe).collect()
    }

    /// An enemy that was near him died at `at`: Last Rites' kill dug already; every Nth other death near him digs a grave
    /// (League); one near the Maiden raises a walker while her escort is under `ARMY_CAP`.
    fn died(&mut self, sim: &mut StableSim<'_>, me: usize, id: usize, at: Pt, champion: bool, here: Pt) {
        if let Some(i) = self.q_dug.iter().position(|v| *v == id) {
            self.q_dug.remove(i);
        } else if summon::dist(at, here) <= GRAVE_NEAR {
            self.deaths += 1;
            let level = sim.get_entity(me).map_or(1, |e| e.level());
            let every = deaths_per_grave(level);
            if self.deaths >= every {
                self.deaths = 0;
                self.dig(sim, me, &format!("{} #{id} died near him, the {every}th death since the last such grave (level {level})",
                                           if champion { "the champion" } else { "a unit" }));
            }
        }
        // the Maiden's army of the dead
        let Some(her) = self.maiden.live.first().map(|m| (m.unit.id, m.unit.at, m.unit.left(sim.tick()))) else { return };
        let under = self.walkers.live.iter().filter(|m| m.extra.kind == Walk::Escort).count() + self.walkers.waiting();
        if summon::dist(at, her.1) <= MAID_RANGE && under < ARMY_CAP && her.2 > 60 {
            self.ask_or_hold(sim, me, id, at, Ask::Raise(her.2));
        }
    }

    /// Her mark spent on champion `id` (his attack or the mist struck it): a share of its max health as magic.
    fn spend(&mut self, sim: &mut StableSim<'_>, me: usize, id: usize) {
        let Some(max) = sim.get_entity(id).filter(|c| c.is_alive()).map(|c| c.hp().1) else { return };
        let level = sim.get_entity(me).map_or(1, |e| e.level());
        let pm = mark_per_mille(&self.p, level);
        let dmg = (max * pm / 1000).max(1);
        sim.entity_remove_buff(id, R_MKV);
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        let on = InputTargetV1::target(id);
        sim.play_view_effect(R_MARK_VIEW, me, &on, 0, 0, 0);
        self.marks += 1;
        if let Some(k) = tally(sim, "mark") {
            wlog(format!("{} MARK SPENT #{k}: the Maiden's mark on #{id} {} - {dmg} magic ({pm} per mille of its {max} max \
                          health, level {level}; {} in all)", head(sim, me), name_of(sim, id), self.marks));
        }
    }

    /// An ask the copy laid (or the army's): out now, or held while the walkers' last ask still waits for its units (or
    /// older ones are held already: they go out first).
    fn ask_or_hold(&mut self, sim: &mut StableSim<'_>, me: usize, target: usize, at: Pt, what: Ask) {
        if self.walkers.waiting() == 0 && self.held.is_empty() {
            self.ask(sim, me, target, at, what, None);
            return;
        }
        let tick = sim.tick();
        if self.held.len() >= HELD_MAX {
            let old = self.held.remove(0);
            self.dropped(sim, me, old, "too many held");
        }
        self.held.push(Held { tick, target, at, what });
        if let Some(k) = tally(sim, "held") {
            wlog(format!("{} {} HELD #{k}: on #{target} {} - the walkers' ask of t={} still waits for its units ({} held): it \
                          goes out once that one is answered", head(sim, me), what.shown(), name_of(sim, target), self.asked,
                         self.held.len()));
        }
    }

    /// A held ask given up (its log line).
    fn dropped(&mut self, sim: &StableSim<'_>, me: usize, h: Held, why: &str) {
        if let Some(k) = tally(sim, "held drop") {
            wlog(format!("{} {} HELD DROPPED #{k}: the ask of t={} on #{} ({why}) - the data's riding pictures play instead",
                         head(sim, me), h.what.shown(), h.tick, h.target));
        }
    }

    /// After the flocks' tick: the oldest held ask goes out once no walkers' ask waits (one a tick: it waits in turn),
    /// where its target stands now (else where it stood); one held past `HELD_TICKS` is dropped.
    fn release(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        while self.held.first().is_some_and(|h| now > h.tick + HELD_TICKS) {
            let h = self.held.remove(0);
            self.dropped(sim, me, h, "held too long");
        }
        if self.held.is_empty() || self.walkers.waiting() > 0 {
            return;
        }
        let h = self.held.remove(0);
        let at = match h.what {
            Ask::Raise(_) => h.at,
            _ => sim.get_entity(h.target).filter(|e| e.is_alive()).map_or(h.at, |e| pos(&e)),
        };
        self.ask(sim, me, h.target, at, h.what, Some(now - h.tick));
    }

    /// Units asked for on `target` at `at`; `held`: the ticks it was held.
    fn ask(&mut self, sim: &mut StableSim<'_>, me: usize, target: usize, at: Pt, what: Ask, held: Option<usize>) {
        let tick = sim.tick();
        if KNOBS.off {
            if let Some(k) = tally(sim, "units off") {
                wlog(format!("{} {} OFF #{k}: cast on #{target}, unit=off in the test knobs - the riding pictures as before",
                             head(sim, me), what.shown()));
            }
            return;
        }
        self.asked = tick;
        let effect = match what {
            Ask::Awake(_) => {
                self.walkers.ask(tick, WALK_LIFE, WalkerBook { kind: Walk::Awake, last: None });
                "walkers"
            }
            Ask::Maiden(_) => {
                self.maiden.ask(tick, MAID_LIFE, MaidBook { looked: 0, dressed: false, next_bolt: 0, last: None });
                self.walkers.ask(tick, MAID_LIFE, WalkerBook { kind: Walk::Escort, last: None });
                "maiden"
            }
            Ask::Raise(life) => {
                self.walkers.ask(tick, life, WalkerBook { kind: Walk::Escort, last: None });
                "raise"
            }
        };
        // 几只（唤醒、护卫）或活多久（尸体上拉起的）放在 dir_x 里给排队的效果
        let mut input = at_input(at);
        input.dir_x = match what {
            Ask::Awake(n) | Ask::Maiden(n) | Ask::Raise(n) => n as i64,
        };
        let queued = sim.queue_effect(&fx(effect), AttackTypeV1::Skill, me, &input, 1);
        if !queued {
            match what {
                Ask::Awake(n) => {
                    make_walkers(sim, me, at, n, "queue_effect refused: spawned by the passive");
                }
                Ask::Maiden(n) => {
                    make_maiden(sim, me, at, n, "queue_effect refused: spawned by the passive");
                }
                Ask::Raise(life) => {
                    make_raised(sim, me, at, life);
                }
            }
        }
        if let Some(k) = tally(sim, match what { Ask::Awake(_) => "walkers ask", Ask::Maiden(_) => "maiden ask", Ask::Raise(_) => "raise ask" }) {
            let body = match what {
                Ask::Awake(n) => format!("the Awakening on #{target} {} at {}: {n} walkers asked for round it", name_of(sim, target),
                                         summon::pt(at)),
                Ask::Maiden(n) => format!("Eulogy of the Isles on #{target} {} at {}: the Maiden asked for {MAID_BEHIND:.0} behind \
                                           it, {n} walkers round her", name_of(sim, target), summon::pt(at)),
                Ask::Raise(life) => format!("#{target} died at {} near the Maiden: a walker asked for from the body ({life} ticks)",
                                            summon::pt(at)),
            };
            wlog(format!("{} {} ASK #{k}: {body}{}{}", head(sim, me), what.shown(),
                         held.map_or(String::new(), |n| format!(" (held {n} tick(s) while the walkers' ask before it waited)")),
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
                                 else { "no walker of hers this time" }));
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
            Event::NoUnit { asked, .. } => {
                if let Some(k) = tally(sim, "maiden none") {
                    wlog(format!("{} MAIDEN NONE #{k}: no Maiden came within {} ticks of the ask at t={asked} - she follows him as a \
                                  picture as before", head(sim, me), summon::FLOCK_WAIT));
                }
            }
            Event::Look { id, n, line } => {
                // she stands for her time: r_on (Q's cooldown halved; the copy's attack marks for her) with her
                let left = self.maiden.get(id).map_or(MAID_LIFE, |m| m.unit.left(tick));
                sim.entity_remove_buff(me, R_ON);
                sim.add_buff(me, &BuffV1::timed(R_ON, left));
                if let Some(m) = self.maiden.get_mut(id) {
                    (m.extra.looked, m.extra.dressed, m.extra.next_bolt) = (tick, false, tick + 1);
                }
                if let Some(k) = tally(sim, "maiden look") {
                    wlog(format!("{} MAIDEN #{n} LOOK #{k}: {line}; {R_ON} on Yorick for her {left} ticks", head(sim, me)));
                }
            }
            Event::Lost { id, why, .. } => {
                sim.entity_remove_buff(me, M_UNIT);
                if let Some(k) = tally(sim, "maiden lost") {
                    wlog(format!("{} MAIDEN LOST #{k}: the unit #{id} spawn_unit named never read as one in {} ticks ({why}) - \
                                  the flag is off, she follows him as a picture as before", head(sim, me), summon::FLOCK_LOOKS));
                }
            }
            Event::Line { n, line, .. } => {
                if let Some(k) = tally(sim, "maiden unit") {
                    wlog(format!("{} MAIDEN #{n} #{k}: {line}", head(sim, me)));
                }
            }
            Event::Over { member, end } => {
                let n = member.unit.n;
                let why = if end.age <= LOST_AGE {
                    // never really there: the data has not read the flag yet, so its Maiden can still rise
                    sim.entity_remove_buff(me, M_UNIT);
                    format!(" - gone {} ticks after she was asked for: the flag is off, she follows him as a picture as before",
                            end.age)
                } else if end.fate == summon::Fate::Killed {
                    // she no longer stands: Q's halved cooldown goes with her
                    sim.entity_remove_buff(me, R_ON);
                    format!(" - {R_ON} taken off")
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
        let due: Vec<(usize, usize)> = self.maiden.live.iter().filter(|m| !m.extra.dressed && tick > m.extra.looked)
            .map(|m| (m.unit.id, m.unit.n)).collect();
        for (id, n) in due {
            if let Some(m) = self.maiden.get_mut(id) {
                m.extra.dressed = true;
            }
            let on_him = sim.get_entity(me).is_some_and(|e| has(&e, R_ON));
            if let Some(k) = tally(sim, "maiden dress") {
                wlog(format!("{} MAIDEN #{n} DRESS #{k}: a tick on, {R_ON} {} on Yorick", head(sim, me),
                             if on_him { "is" } else { "is NOT" }));
            }
        }
    }

    /// The Maiden follows him (a forced move to her spot behind him when she is off it) and shoots a bolt every
    /// `MAID_COOL` ticks at the nearest enemy champion within `MAID_RANGE` of her (else the nearest other enemy).
    fn maiden_acts(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, here: Pt, speed: u64) {
        let tick = sim.tick();
        let Some((id, n, her, next)) = self.maiden.live.first().map(|m| (m.unit.id, m.unit.n, m.unit.at, m.extra.next_bolt)) else {
            return;
        };
        let Some(e) = sim.get_entity(id).filter(|e| e.is_alive()) else { return };
        let moving = (0..e.cc_count()).filter_map(|i| e.cc_at(i)).any(|c| c.kind == CcKindV1::ForceMove.code());
        let spot = follow_spot(here, her);
        let off = summon::dist(her, spot);
        if !moving && off > MAID_SLACK {
            let step = (speed.max(400) as f64) * if summon::dist(her, here) > MAID_LEASH { 3.0 } else { 1.0 };
            let ticks = (off / step).ceil().max(1.0) as u64;
            let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks);
            (mv.dx, mv.dy, mv.speed) = ((spot.0 - her.0).round() as i64, (spot.1 - her.1).round() as i64, (off / ticks as f64).ceil() as u64);
            sim.apply_cc(id, &mv);
            if let Some(k) = tally(sim, "maiden follow") {
                wlog(format!("{} MAIDEN #{n} FOLLOW #{k}: {:.0} off her spot {} behind Yorick at {} - a forced move of {ticks} ticks",
                             head(sim, me), off, summon::pt(spot), summon::pt(here)));
            }
        }
        if tick < next {
            return;
        }
        // 看得见的才打（宿主没有 is_visible 这个槽时连他自己都「看不见」：那就不看这一条）
        let sight = sim.is_visible(team, me);
        let foes: Vec<(usize, Pt, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && (!sight || sim.is_visible(team, u.id())))
            .filter(|u| matches!(u.kind(), Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Summon)))
            .map(|u| (u.id(), pos(&u), u.is_champion()))
            .filter(|u| summon::dist(u.1, her) <= MAID_RANGE)
            .collect();
        let pick = foes.iter().filter(|f| f.2).min_by(|a, b| summon::dist(a.1, her).total_cmp(&summon::dist(b.1, her)))
            .or_else(|| foes.iter().min_by(|a, b| summon::dist(a.1, her).total_cmp(&summon::dist(b.1, her)))).copied();
        let Some((t, _, _)) = pick else { return };
        if let Some(m) = self.maiden.get_mut(id) {
            m.extra.next_bolt = tick + MAID_COOL;
        }
        let spec = ProjectileSpawnV1 { caster_id: me, team, x: her.0.round().max(0.0) as u64, y: her.1.round().max(0.0) as u64,
                                       speed: BOLT_SPEED, target_id: t, attack_type: AttackTypeV1::Skill.code(),
                                       casting_type: CastingTypeV1::Targeting.code(), casting_target: CastingTargetV1::Enemy.code(),
                                       ..Default::default() };
        let flew = sim.spawn_projectile(R_BOLT, &fx("bolt"), &spec);
        if !flew {
            BoltFx.apply(sim, 0, me, InputTargetV1::target(t));
        }
        if let Some(k) = tally(sim, "bolt") {
            wlog(format!("{} MAIDEN #{n} BOLT #{k}: at #{t} {} {:.0} away{}", head(sim, me), name_of(sim, t),
                         summon::dist(her, pick.map_or(her, |p| p.1)), if flew { "" } else { " - spawn_projectile REFUSED: dealt at once" }));
        }
    }

    /// The haste toward a champion the mist marked: him, his walkers and the Maiden, each moving toward one within
    /// `HASTE_NEAR`.
    fn hastes(&mut self, sim: &mut StableSim<'_>, me: usize, here: Pt, marked: &[Foe]) {
        let level = sim.get_entity(me).map_or(1, |e| e.level());
        let mut movers: Vec<(usize, Option<Pt>, Pt)> = vec![(me, self.last, here)];
        for m in self.walkers.live.iter_mut() {
            movers.push((m.unit.id, m.extra.last, m.unit.at));
            m.extra.last = Some(m.unit.at);
        }
        for m in self.maiden.live.iter_mut() {
            movers.push((m.unit.id, m.extra.last, m.unit.at));
            m.extra.last = Some(m.unit.at);
        }
        self.last = Some(here);
        if marked.is_empty() {
            return;
        }
        let ms = haste(level) as i32;
        for (id, last, now) in movers {
            let Some(last) = last else { continue };
            if !marked.iter().any(|f| summon::dist(f.at, now) <= HASTE_NEAR && toward(last, now, f.at)) {
                continue;
            }
            sim.entity_remove_buff(id, E_MS);
            let mut b = BuffV1::timed(E_MS, 3);
            b.move_speed_mult = ms;
            sim.add_buff(id, &b);
        }
    }

    /// Last Rites' heal, two ticks after its flag was first seen (the champion twin's `Q_CH` is up by then).
    fn heal(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (flagged, champion, level, (hp, max)) = (has(&e, Q_HL), has(&e, Q_CH), e.level(), e.hp());
        match self.heal_due {
            None if flagged => self.heal_due = Some(tick + 2),
            Some(due) if tick >= due => {
                self.heal_due = None;
                sim.entity_remove_buff(me, Q_HL);
                let amount = q_heal(level, hp, max, champion);
                sim.heal(me, me, amount);
                if let Some(k) = tally(sim, "heal") {
                    wlog(format!("{} HEAL #{k}: Last Rites {} - {amount} ({hp}/{max} health, level {level})", head(sim, me),
                                 if champion { "on a champion" } else { "on a unit (half)" }));
                }
            }
            _ => {}
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

    /// He died (or a new life began): League's walkers go with him (health set to 0), the Maiden fades within 3 s; the
    /// books let go.
    fn orphans(&mut self, sim: &mut StableSim<'_>, why: &str) {
        let (w, m) = (self.walkers.orphans(), self.maiden.orphans());
        if w.is_empty() && m.is_empty() {
            return;
        }
        let tick = sim.tick();
        let me = self.me;
        let mut gone = 0;
        for x in &w {
            if sim.get_entity(x.unit.id).is_some_and(|e| e.is_alive()) && sim.entity_set_hp(x.unit.id, 0) {
                gone += 1;
            }
        }
        let mut fades = 0;
        for x in &m {
            for step in 1..=FADE_STEPS + 1 {
                let mut input = InputTargetV1::target(x.unit.id);
                (input.dir_x, input.dir_y) = (step as i64, x.unit.left(tick) as i64);
                if sim.queue_effect(&fx("fade"), AttackTypeV1::Skill, me, &input, step * FADE_EVERY) {
                    fades += 1;
                }
            }
        }
        if let Some(k) = tally(sim, "orphan") {
            wlog(format!("{} ORPHAN #{k}: {why} - {} walker(s): health set to 0 for {gone}; {} Maiden: {fades} fade steps queued \
                          ({FADE_STEPS} x {FADE_EVERY} ticks)", head(sim, me), w.len(), m.len()));
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
        // a new life is a new entity: the units of the old one are no longer his to watch, his held asks gone with it
        self.orphans(sim, "Yorick respawned (his death did not reach on_dead)");
        for h in std::mem::take(&mut self.held) {
            self.dropped(sim, me, h, "Yorick respawned");
        }
        (self.me, self.heal_due, self.last, self.had_up, self.deaths) = (me, None, None, false, 0);
        self.q_dug.clear();
        wlog(format!("{} SPAWN: the add-on's Yorick (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        // a dead champion's passive does not run: his units are seen to now; an ask still held never goes out
        self.orphans(sim, "Yorick died");
        let me = self.me;
        for h in std::mem::take(&mut self.held) {
            self.dropped(sim, me, h, "Yorick died");
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, target: usize, damage: &mut usize) {
        self.hooked(sim, "on_attack", entity, target, Some(*damage));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_kill", entity, victim, None);
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.hooked(sim, "on_unit_kill", me, victim, None);
        // a minion or a camp Last Rites killed (a champion hit digs its own grave in the data)
        if sim.get_entity(me).is_some_and(|e| has(&e, Q_WIN)) {
            self.q_dug.push(victim);
            if self.q_dug.len() > 16 {
                self.q_dug.remove(0);
            }
            let what = name_of(sim, victim);
            self.dig(sim, me, &format!("{what} #{victim} died to Last Rites"));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let Some((alive, team, here, speed)) = sim.get_entity(me).map(|e| (e.is_alive(), e.team(), pos(&e), e.stat().move_speed as u64))
        else { return };
        if !alive {
            // a wall stands on (League's does) for as long as anything runs this
            self.walls.block(sim, me);
            return;
        }
        self.me = me;
        let marked = self.scan(sim, me, team, here);
        let up = sim.get_entity(me).is_some_and(|e| has(&e, W_UP));
        if up && !self.had_up {
            sim.entity_remove_buff(me, W_UP);
            let p = self.p.clone();
            self.walls.rise(sim, me, &p);
        }
        self.had_up = up;
        self.walls.block(sim, me);
        self.heal(sim, me);
        self.units(sim, player, me, team, here);
        self.maiden_acts(sim, me, team, here, speed);
        self.hastes(sim, me, here, &marked);
        self.release(sim, me);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (graves from kills and deaths near him, the real Dark Procession wall, Last Rites by missing health, \
         the Maiden following him with her bolts and mark; the walkers and the Maiden units of their own) loaded: game {}.{}.{} \
         abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "UNITS: the Mist Walkers ('{}') and the Maiden of the Mist ('{}') are units (spawn_unit) - {}; the Awakening a walker a grave \
         for {WALK_LIFE} ticks ({WALK_HIT} + {WALK_HIT_AD}% of his attack a bite, {WALK_HP_PCT}% of his health), the Maiden for \
         {MAID_LIFE} ticks ({MAID_HP_PCT}% of his health) behind him, a bolt every {MAID_COOL} ticks ({MAID_HIT} + {MAID_HIT_AD}% \
         magic, reach {MAID_RANGE:.0}) with 2-4 walkers, the mist's leap within {LEAP_REACH:.0}. Test knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(WALKER),
        KNOBS.name.as_deref().unwrap_or(MAIDEN_UNIT),
        if KNOBS.off { "OFF by the test knobs: the riding pictures as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(),
        KNOBS.shown()
    ));
    module.add_native_passive(format!("{ID}:shepherd"), Shepherd::default());
    module.add_native_effect(fx("walkers"), WalkersFx);
    module.add_native_effect(fx("maiden"), MaidenFx);
    module.add_native_effect(fx("raise"), RaiseFx);
    module.add_native_effect(fx("bolt"), BoltFx);
    module.add_native_effect(fx("fade"), FadeFx);
    host.log(LogLevel::Info, "league_yorick loaded (graves, the real wall, the Maiden; walkers and Maiden as units).");
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
mod tests;
