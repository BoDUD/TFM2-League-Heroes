//! 婕拉附加包：照英雄联盟做主包数据做不到的种子和植物（用户 2026-10-20：技能方案 A、中单、做附加包）。
//!
//! 主包保持纯数据：数据不能在地上留东西，所以主包里每次 Q、E 都当场种一颗种子、马上长成植物（英雄联盟 W + Q / W + E 的连招）；
//! 植物是落点上的周期区域，每秒打区域里先轮到的一个敌人（小兵也可能排在英雄前面），伤害不随等级变。`mod.override_info` 把
//! 主包的婕拉换成 `override/` 里的副本（`tools/kit/build_zyra.py --native`），被动 `league_zyra:garden`：
//!
//! - **荆棘花园（种子留在地上）**：她活着时每 `s_cd` tick 在身边掉一颗种子（有敌方英雄在 `s_seek` 内就掉在朝他的方向
//!   `s_near` 远处，否则在她身边绕一圈的位置），种子在地上留 `s_life` tick，最多 `s_max` 颗（多了最早的那颗枯掉）；
//!   她参与击杀敌方英雄（击杀或助攻）时马上掉一颗（英雄联盟：击杀缩短狂野生长的充能）。
//! - **Q / E 落在种子旁边**：副本里 Q、E 出手那一 tick 给目标挂 2 tick 的 `league_zyra_q_aim` / `league_zyra_e_aim`
//!   （落点就是目标那时站的地方）；Q 落点 `s_r` 内的种子长成**荆棘喷射者**，E 的藤蔓经过的线（她到落点、再往前 `e_over`）
//!   `s_r` 内的种子长成**藤蔓鞭击者**。主包数据在落点长的那一株照旧，种子长的是本包的植物。
//! - **本包的植物**：活 `t_life` tick，每 `t_per` tick 打一次，**先打范围内最近的敌方英雄**，没有英雄才打最近的小兵、野怪
//!   （防御塔不打）；伤害随她的等级成长（英雄联盟 20–100：1 级 `pl_lo`、18 级 `pl_hi`，中间按等级线性）+ `pl_ratio`% 法强。
//!   荆棘喷射者从植物身上吐出一根看得见的刺（`league_zyra_t_spit`，飞到才扣血），藤蔓鞭击者近身抽打并减速 `v_slow`%。
//! - **绞杀之藤激怒植物**：副本里 R 出手时给目标挂 `league_zyra_r_aim`；落点 `r_r` 内本包的植物 `r_rage` tick 内出手间隔减半
//!   （英雄联盟：密林里的植物攻速提高）。主包数据的植物照主包（伤害提高）。
//!
//! - **光合作用**（0.1.3，彩蛋，用户 2026-11-05「植物大战僵尸」）：比赛里有蕾欧娜时，她的技能落在婕拉的植物上（主包 Q、E 长的、
//!   本包种子长的都算），植物在剩下的时间里画大一号（`sun.rs`）；玩法不变。0.1.6：变大时给她挂一个只有名字的
//!   `league_zyra_sun_grew`，league_eggs 读到了在屏幕上放提示「光合作用」。
//! - **大招落点的日志**（0.1.5，2026-11-08 的日志检查：两次启动 0 行 `RAGE`，80 行 `WATCH` 全是 rages 0，种子植物照常长、照常打）：
//!   副本里 R 的 `r_aim` 和 E 的 `e_aim` 接法一样（E 的认得到），读代码没找到认不到 R 的地方；植物只活 `t_life` tick，也可能只是
//!   R 落点旁边很少有植物。所以每认到一次 R 记一行 `R AIM`：打谁、落点、她活着的种子植物几株、最近的一株离落点多远（激怒要在
//!   `r_r` 内）、激怒了几株；`WATCH` 行加上认到 R 的次数（`R seen`）。
//!
//! - **植物有了身体（0.2.0，2026-11-14；用户：「召唤物的全做啊 剩下的一批英雄也做了啊」）**：英雄联盟的植物是能被选中、能被打掉
//!   的单位（不会动，打掉给 3 金币）。这里原来植物是一张画面，打不到。稳定 mod API 的 `spawn_unit`（公用部分在萨科附加包的
//!   `summon.rs`）：本包的每株植物长出来时排原生效果 `:spitter` / `:lasher`，在它站的地方生成一个「身体」单位
//!   （`league_zyra_spitter` / `_lasher`，[`plant_spec`]：移速 1 不会走、攻击 0 伤害——只为了朝着敌人、播吐刺 / 抽打的动作，
//!   生命是她上限的 `PLANT_HP_PCT`%），出手照旧由本包打，从身体现在站的地方；身体被打掉这株植物就不再出手。身体读成单位以后
//!   她身上一直挂 `P_UNIT`：副本的数据在 Q、E 落点不再长主包的那一株（画面和区域），改挂 `Q_LAND` / `E_LAND`，本包在落点
//!   长一株自己的（带身体）。比赛里有蕾欧娜时植物照旧是画面（光合作用的彩蛋要把画面画大一号）。生成不了（宿主没有这个接口、
//!   失败、测试开关 `unit=off`、读不成单位）就不挂 `P_UNIT`、植物照旧是画面。日志里 `PLANT` 开头的行。
//!
//! 游戏 0.6.4 的 `deal_damage_typed` 只把伤害排进效果队列，下一次 on_update 之前才扣血（莉莉娅 0.1.2 的教训）。
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态记在每个婕拉自己的被动实例里，
//! 服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zyra.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `SEED`（掉种子）、`GROW`（种子长成植物）、`STRIKE`（植物出手）、`R AIM`（认到她的 R）、`RAGE`（激怒）、`TAKEDOWN`（参与击杀掉种子）、
//! `WATCH`（每 30 秒的计数，植物有动静才记）、`SUN`（蕾欧娜的阳光让植物变大），都限了条数。0.1.2：`SPAWN` 的参数一次启动只写一次，`SPAWN`、`WATCH` 整个
//! 游戏一个计数（预模拟限量，你看的那场每行都记）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

mod sun;

// the shared module: Zyra uses part of it (the bundle compiles this crate as a module of its own, unused parts warn)
#[allow(dead_code)]
#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

use summon::{Event, Flock};

const ID: &str = "league_zyra";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_zyra") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 荆棘喷射者吐的刺从植物身上多高的地方出来（植物图的嘴）。
const SPIT_UP: u64 = 9_000;

/// 主包婕拉的名字（buff、声音、画面都以它开头）。
fn zy(x: &str) -> String {
    format!("league_zyra_{x}")
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ZYRA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_zyra.log");
        }
    }
    PathBuf::from("league_zyra.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    // the file stays open (league_lillia's log_open_once fix: opening it for every line stalled the simulation thread)
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

/// `SPAWN` / `WATCH` lines a launch (0.1.2), and `SEED` / `GROW` / `STRIKE` / `RAGE` / `TAKEDOWN` too (0.1.4: they were capped
/// in each Zyra's passive - 11-06's presim log 441 KB, SEED 1792, STRIKE 1482, GROW 1403, TAKEDOWN 811 lines): the server's
/// presims (hundreds a launch, each with new passives - a count in the passive counts one sim) the first `LOG_FIRST`, then
/// every `LOG_EVERY`-th; the match on screen all of them.
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind`: its count this launch when it is to be written (`shown`: the match on screen).
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    noted(kind, on_screen(sim))
}

/// The `Params` the log showed last (they come from the champion data: the same in every sim of a launch).
static PARAMS_SHOWN: Mutex<Option<Params>> = Mutex::new(None);

/// `p` not in the log yet: once a launch, again only if they ever differ (league_talon_vault's; 2026-11-03 night logs:
/// 250 SPAWN lines, each with the whole Params).
fn params_new(p: &Params) -> bool {
    let mut shown = PARAMS_SHOWN.lock().unwrap_or_else(|e| e.into_inner());
    if shown.as_ref() == Some(p) {
        return false;
    }
    *shown = Some(p.clone());
    true
}

/// What a `WATCH` line reports besides the seeds (which drop every `s_cd` ticks anyway): plants grown, strikes, rages,
/// takedowns, plants grown in Leona's sunlight. A line only when one of them moved since the last (2026-11-03 night logs:
/// 1399 WATCH lines of 3267, most of them only more seeds).
pub type Watch = (usize, usize, usize, usize, usize);

pub fn watch_news(last: Watch, now: Watch) -> bool {
    last != now
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 种子：掉落间隔、在地上留多久、最多几颗、朝敌方英雄掉多远、多远内的英雄算「朝他」、Q / E 长出种子的半径、
    /// 种子的画面多久重放一次（它的图一轮的长度）、E 的藤蔓越过落点多远。
    pub s_cd: usize,
    pub s_life: usize,
    pub s_max: usize,
    pub s_near: usize,
    pub s_seek: usize,
    pub s_r: usize,
    pub s_show: usize,
    pub e_over: usize,
    /// 植物：活多久、出手间隔、荆棘喷射者 / 藤蔓鞭击者的射程、刺飞多快、减速 % 和 tick。
    pub t_life: usize,
    pub t_per: usize,
    pub t_r: usize,
    pub v_r: usize,
    pub spit_speed: usize,
    pub v_slow: usize,
    pub v_slow_t: usize,
    /// 植物一下的伤害：1 级、18 级（中间按等级线性）、法强 %。
    pub pl_lo: usize,
    pub pl_hi: usize,
    pub pl_ratio: usize,
    /// 绞杀之藤：半径、激怒多久。
    pub r_r: usize,
    pub r_rage: usize,
    /// 主包数据的植物几 tick 后长在落点：Q 的棘刺（平常 / E 定住人之后的快的）、E 的藤蔓（`sun.rs` 按它认是哪一种）。
    pub q_delay: usize,
    pub q_fast: usize,
    pub e_grow: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            s_cd: 600,
            s_life: 1800,
            s_max: 4,
            s_near: 30000,
            s_seek: 90000,
            s_r: 24000,
            s_show: 60,
            e_over: 20000,
            t_life: 300,
            t_per: 60,
            t_r: 50000,
            v_r: 32000,
            spit_speed: 3000,
            v_slow: 30,
            v_slow_t: 60,
            pl_lo: 20,
            pl_hi: 100,
            pl_ratio: 12,
            r_r: 32000,
            r_rage: 300,
            q_delay: 30,
            q_fast: 4,
            e_grow: 25,
        }
    }
}

/// `{"s_cd":600,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "s_cd" => &mut p.s_cd,
            "s_life" => &mut p.s_life,
            "s_max" => &mut p.s_max,
            "s_near" => &mut p.s_near,
            "s_seek" => &mut p.s_seek,
            "s_r" => &mut p.s_r,
            "s_show" => &mut p.s_show,
            "e_over" => &mut p.e_over,
            "t_life" => &mut p.t_life,
            "t_per" => &mut p.t_per,
            "t_r" => &mut p.t_r,
            "v_r" => &mut p.v_r,
            "spit_speed" => &mut p.spit_speed,
            "v_slow" => &mut p.v_slow,
            "v_slow_t" => &mut p.v_slow_t,
            "pl_lo" => &mut p.pl_lo,
            "pl_hi" => &mut p.pl_hi,
            "pl_ratio" => &mut p.pl_ratio,
            "r_r" => &mut p.r_r,
            "r_rage" => &mut p.r_rage,
            "q_delay" => &mut p.q_delay,
            "q_fast" => &mut p.q_fast,
            "e_grow" => &mut p.e_grow,
            _ => continue,
        };
        *slot = v;
    }
    p.s_cd = p.s_cd.max(1);
    p.s_show = p.s_show.max(1);
    p.t_per = p.t_per.max(2);
    p.spit_speed = p.spit_speed.max(1);
    p.v_slow = p.v_slow.min(95);
    p
}

// ===================== 计算 =====================

/// 植物一下的魔法伤害（减免前）：等级 1 是 `pl_lo`、18 是 `pl_hi`，中间线性，加 `pl_ratio`% 法强。
pub fn plant_damage(p: &Params, level: usize, ap: usize) -> usize {
    let lv = level.clamp(1, 18);
    p.pl_lo + (p.pl_hi.saturating_sub(p.pl_lo)) * (lv - 1) / 17 + p.pl_ratio * ap / 100
}

/// 出手间隔：被激怒时减半。
pub fn strike_period(p: &Params, enraged: bool) -> usize {
    if enraged {
        (p.t_per / 2).max(1)
    } else {
        p.t_per
    }
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 点 `p` 到线段 `a`-`b` 的距离。
pub fn seg_dist(p: (f64, f64), a: (f64, f64), b: (f64, f64)) -> f64 {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let l2 = dx * dx + dy * dy;
    if l2 <= 0.0 {
        return dist(p, a);
    }
    let t = (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / l2).clamp(0.0, 1.0);
    dist(p, (a.0 + t * dx, a.1 + t * dy))
}

/// R 的落点旁边她的植物（0.1.5 的 `R AIM` 行）：活着的几株、最近的一株离落点多远（一株都没有是 None）。
pub fn round_spot(plants: &[(f64, f64)], spot: (f64, f64)) -> (usize, Option<f64>) {
    (plants.len(), plants.iter().map(|&p| dist(p, spot)).min_by(|a, b| a.total_cmp(b)))
}

/// 掉种子的位置：朝 `toward`（有的话）`near` 远处、最多到一半的路；没有就在她身边按 `turn`（0..8）绕一圈。
pub fn seed_spot(me: (f64, f64), toward: Option<(f64, f64)>, near: f64, turn: usize) -> (f64, f64) {
    match toward {
        Some(t) => {
            let d = dist(me, t).max(1.0);
            let k = near.min(d / 2.0) / d;
            (me.0 + (t.0 - me.0) * k, me.1 + (t.1 - me.1) * k)
        }
        None => {
            let a = (turn % 8) as f64 * std::f64::consts::FRAC_PI_4;
            (me.0 + near / 2.0 * a.cos(), me.1 + near / 2.0 * a.sin())
        }
    }
}

fn at(p: (f64, f64)) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

// ===================== 植物的身体（0.2.0） =====================

/// The bodies' unit names: the game draws them from asset/base/aseprite_resources/champions/<name>, which mod.override_info
/// sends to the main pack's league/champions/<name> (tools/art/unit_zyra_plants.py: the plants' own 1x life frames, the
/// size they have on screen today).
pub const SPITTER: &str = "league_zyra_spitter";
pub const LASHER: &str = "league_zyra_lasher";
/// The sheets' strike: ticks long and the tick the spit / the lash frame starts (checked by make_override.py).
pub const TP_ACT: usize = 20;
pub const TP_LANDS: usize = 5;
pub const VP_ACT: usize = 20;
pub const VP_LANDS: usize = 5;
/// League (wiki, 2026-11-14): a plant dies to one melee or two ranged champion attacks (health 8 against 8 / 4 a hit);
/// here a share of her health cap that a champion's attack or two takes, no armour, no magic resistance.
pub const PLANT_HP_PCT: usize = 15;
/// On her while her plants' bodies read as units: the copy's data grows no plant of its own where Q and E land and lays
/// `Q_LAND` / `E_LAND` on her there instead (renewed every tick for `FLAG_TICKS`).
pub const P_UNIT: &str = "league_zyra_p_unit";
pub const Q_LAND: &str = "league_zyra_q_land";
pub const E_LAND: &str = "league_zyra_e_land";
pub const P_UID: &str = "league_zyra_p_uid";
/// Laid by `:spitter` / `:lasher` when the host gave no body: the landing plants go back to the data's.
pub const P_FAIL: &str = "league_zyra_p_fail";
/// Leona in the match: the plants stay pictures (the sunlight easter egg draws the picture a size bigger).
pub const LEONA: &str = "league_leona";
const FLAG_TICKS: usize = 30;
const UID_TICKS: usize = 6;
/// Bodies on the books at once; a body gone within this many ticks was never really there.
const PLANT_CAP: usize = 12;
pub const LOST_AGE: usize = 6;

/// The test knobs (`league_zyra.cfg` beside the log), read once.
static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

/// Her passive's numbers for the native effects: (sim seed, her) -> params (league_naafiri's way).
static PLANT_PARAMS: Mutex<Vec<((u64, usize), Params)>> = Mutex::new(Vec::new());

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    let key = (sim.seed(), me);
    PLANT_PARAMS.lock().unwrap_or_else(|e| e.into_inner()).iter().find(|(k, _)| *k == key).map_or_else(Params::default, |(_, p)| p.clone())
}

fn keep_params(sim: &StableSim<'_>, me: usize, p: &Params) {
    let key = (sim.seed(), me);
    let mut all = PLANT_PARAMS.lock().unwrap_or_else(|e| e.into_inner());
    all.retain(|(k, _)| *k != key);
    all.push((key, p.clone()));
    if all.len() > 64 {
        all.remove(0);
    }
}

/// A plant's body from her numbers now (`stat`, her health cap `max_hp`): move speed 1, a harmless attack in the plant's
/// reach and pace (it faces its target and plays the strike; the add-on's natives strike).
pub(crate) fn plant_spec(kind: Kind, p: &Params, stat: &StatV1, max_hp: usize) -> summon::Spec {
    let (name, reach, act, lands) = match kind {
        Kind::Spitter => (SPITTER, p.t_r, TP_ACT, TP_LANDS),
        Kind::Lasher => (LASHER, p.v_r, VP_ACT, VP_LANDS),
    };
    summon::Spec {
        name: name.to_string(),
        life: p.t_life + 1,
        stat: StatV1 { attack: 0, magic_power: stat.magic_power, hp: (max_hp * PLANT_HP_PCT / 100).max(1), defence: 0,
                       magic_resistance: 0, move_speed: 1, hp_regen: 0, stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: 0, attack: 0, range: reach, cooltime: p.t_per.max(act + 1), duration: act,
                               start_timing: lands, cancelable: false, attack_type: AttackTypeV1::BaseAttack.code() },
    }
}

/// `:spitter` / `:lasher` - a plant's body where it grows (the input); no body: the plant's picture as before, and `P_FAIL`
/// on her.
struct PlantFx(Kind);

impl StableEffectType for PlantFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let here = if InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Pos) {
            (input.x as f64, input.y as f64)
        } else {
            match sim.get_entity(caster) {
                Some(e) => fpos(e.pos()),
                None => return,
            }
        };
        let Some((team, stat, max)) = sim.get_entity(caster).map(|e| (e.team(), e.stat(), e.hp().1)) else { return };
        let p = params_of(sim, caster);
        let spec = plant_spec(self.0, &p, &stat, max).with(&KNOBS);
        let spot = summon::inside(summon::field(sim), here);
        match summon::spawn(sim, caster, team, spot, &spec) {
            Some(id) => {
                sim.add_buff(caster, &BuffV1::timed(&summon::handoff(P_UID, id), UID_TICKS));
                if let Some(k) = tally(sim, "plant spawn") {
                    wlog(format!("{} PLANT SPAWN #{k}: a {:?}'s body, unit #{id} for team {team} at {}: {}", head(sim, caster), self.0,
                                 summon::pt(spot), spec.shown()));
                }
            }
            None => {
                let pic = match self.0 {
                    Kind::Spitter => "t_plant",
                    Kind::Lasher => "v_plant",
                };
                sim.play_view_effect(&zy(pic), caster, &at(spot), 0, 0, 0);
                sim.entity_remove_buff(caster, P_FAIL);
                sim.add_buff(caster, &BuffV1::timed(P_FAIL, 3));
                if let Some(k) = tally(sim, "plant fail") {
                    wlog(format!("{} PLANT SPAWN FAILED #{k}: spawn_unit gave no unit for '{}' at {} - the plant's picture as before",
                                 head(sim, caster), spec.name, summon::pt(spot)));
                }
            }
        }
    }
}

/// Her plants' bodies, as her passive keeps them.
#[derive(Clone)]
struct Bodies {
    flock: Flock<()>,
    /// A body read as a unit in this life and no spawn failed since: `P_UNIT` on her.
    ok: bool,
    /// Leona in the match (looked at once): the plants stay pictures.
    leona: Option<bool>,
    /// Where her last Q and E land (their marks' spots), for the plants the data leaves to the add-on there.
    q_spot: Option<(f64, f64)>,
    e_spot: Option<(f64, f64)>,
}

impl Default for Bodies {
    fn default() -> Self {
        Bodies { flock: Flock::new(P_UID, PLANT_CAP, Params::default().t_life + 1), ok: false, leona: None, q_spot: None, e_spot: None }
    }
}

// ===================== 被动 =====================

#[derive(Clone, Copy, Debug, PartialEq)]
pub(crate) enum Kind {
    Spitter,
    Lasher,
}

#[derive(Clone, Debug)]
struct Seed {
    pos: (f64, f64),
    until: usize,
    next_show: usize,
}

#[derive(Clone, Debug)]
struct Plant {
    kind: Kind,
    pos: (f64, f64),
    until: usize,
    next: usize,
    rage_until: usize,
    /// 0.2.0: its body (a unit of the flock).
    unit: Option<usize>,
}

/// 刺在飞：到了 `due` 再扣血。
#[derive(Clone, Debug)]
struct Spit {
    target: usize,
    due: usize,
    dmg: usize,
}

/// 每个婕拉一份。
#[derive(Clone, Default)]
struct Garden {
    p: Params,
    player: usize,
    seeds: Vec<Seed>,
    plants: Vec<Plant>,
    spits: Vec<Spit>,
    next_seed: usize,
    turn: usize,
    /// 上一 tick 身上有她的 q_aim / e_aim / r_aim 的单位（一个标记只算一次）。
    aim_seen: Vec<(usize, u8)>,
    kills_seen: usize,
    n_seeds: usize,
    n_grow: usize,
    n_strike: usize,
    n_rage: usize,
    /// 认到她的 R 几次（0.1.5 的 `R AIM`）。
    n_raim: usize,
    n_take: usize,
    next_report: usize,
    /// what the last `WATCH` line said (`watch_news`)
    watched: Watch,
    /// 光合作用（彩蛋）：她的植物在蕾欧娜的阳光里变大一号。
    sun: sun::Sun,
    /// 0.2.0: her plants' bodies.
    b: Bodies,
}

struct Unit {
    id: usize,
    pos: (f64, f64),
    champion: bool,
}

/// 能打的敌方单位（英雄、小兵、野怪；塔、水晶不算）。
fn enemies(sim: &StableSim<'_>, team: usize) -> Vec<Unit> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.team() == team || !e.is_alive() || !e.is_targetable() {
            continue;
        }
        let ok = matches!(
            e.kind(),
            Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Epic | EntityKindV1::Serpen)
        );
        if ok {
            out.push(Unit { id: e.id(), pos: fpos(e.pos()), champion: e.kind() == Some(EntityKindV1::Champion) });
        }
    }
    out
}

/// 植物打谁：范围内最近的敌方英雄，没有就最近的其他单位。
fn choose(units: &[Unit], from: (f64, f64), reach: f64) -> Option<&Unit> {
    let near = |u: &&Unit| dist(u.pos, from) <= reach;
    let by = |a: &&Unit, b: &&Unit| dist(a.pos, from).total_cmp(&dist(b.pos, from));
    units.iter().filter(|u| u.champion).filter(near).min_by(by).or_else(|| units.iter().filter(near).min_by(by))
}

impl Garden {
    fn drop_seed(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (f64, f64), why: &str) {
        let tick = sim.tick();
        let toward = enemies(sim, team)
            .into_iter()
            .filter(|u| u.champion && dist(u.pos, pos) <= self.p.s_seek as f64)
            .min_by(|a, b| dist(a.pos, pos).total_cmp(&dist(b.pos, pos)))
            .map(|u| u.pos);
        let spot = seed_spot(pos, toward, self.p.s_near as f64, self.turn);
        self.turn += 1;
        if self.seeds.len() >= self.p.s_max.max(1) {
            self.seeds.remove(0);
        }
        self.seeds.push(Seed { pos: spot, until: tick + self.p.s_life, next_show: tick });
        sim.play_sfx(&zy("s_drop"), me, &at(spot));
        self.n_seeds += 1;
        if let Some(k) = tally(sim, "seed") {
            wlog(format!("{} SEED #{} ({why}) at ({:.0}, {:.0}), {} on the ground #{k}", head(sim, me), self.n_seeds, spot.0,
                         spot.1, self.seeds.len()));
        }
    }

    /// 种子的画面（一轮 `s_show` tick）重放，过期的枯掉。
    fn seeds(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        self.seeds.retain(|s| s.until > tick);
        for s in &mut self.seeds {
            if tick >= s.next_show {
                s.next_show = tick + self.p.s_show;
                sim.play_view_effect(&zy("s_seed"), me, &at(s.pos), 0, 0, 0);
            }
        }
    }

    fn grow(&mut self, sim: &mut StableSim<'_>, me: usize, kind: Kind, hit: impl Fn((f64, f64)) -> bool) {
        let (grown, keep): (Vec<Seed>, Vec<Seed>) = std::mem::take(&mut self.seeds).into_iter().partition(|s| hit(s.pos));
        self.seeds = keep;
        for s in grown {
            self.plant_at(sim, me, kind, s.pos, "on a seed");
        }
    }

    /// Bodies are asked for: not off by the knobs, no Leona in the match.
    fn bodies_wanted(&self) -> bool {
        !KNOBS.off && self.b.leona == Some(false)
    }

    /// One plant of hers at `pos`: a body asked for (0.2.0) or her picture, the sound, the native strikes.
    fn plant_at(&mut self, sim: &mut StableSim<'_>, me: usize, kind: Kind, pos: (f64, f64), why: &str) {
        let tick = sim.tick();
        let (pic, snd, life, fx) = match kind {
            Kind::Spitter => ("t_plant", "t_grow", self.p.t_life, "spitter"),
            Kind::Lasher => ("v_plant", "v_grow", self.p.t_life, "lasher"),
        };
        let body = self.bodies_wanted() && sim.queue_effect(&format!("{ID}:{fx}"), AttackTypeV1::Skill, me, &at(pos), 1);
        if !body {
            sim.play_view_effect(&zy(pic), me, &at(pos), 0, 0, 0);
            self.sun.seed_plant(kind, pos, tick);
        }
        sim.play_sfx(&zy(snd), me, &at(pos));
        // the first strike as the data's plants: a third of a period after it grows
        self.plants.push(Plant { kind, pos, until: tick + life, next: tick + self.p.t_per / 3, rage_until: 0, unit: None });
        self.n_grow += 1;
        if let Some(k) = tally(sim, "grow") {
            wlog(format!("{} GROW #{}: a {kind:?} {why} at ({:.0}, {:.0}){} #{k}", head(sim, me), self.n_grow, pos.0, pos.1,
                         if body { ", its body asked for" } else { "" }));
        }
    }

    /// The bodies' part of a tick: Leona looked for once, the plants the data left to the add-on where Q and E landed,
    /// the flock (a body linked to its plant; a destroyed one takes its plant), `P_UNIT`.
    fn bodies_tick(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (f64, f64)) {
        if self.b.leona.is_none() {
            let leona = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                .any(|e| e.is_champion() && e.name().is_some_and(|n| n == LEONA));
            self.b.leona = Some(leona);
            if leona || KNOBS.off {
                if let Some(k) = tally(sim, "plant pictures") {
                    wlog(format!("{} PLANT PICTURES #{k}: {} - her plants stay pictures", head(sim, me),
                                 if KNOBS.off { "unit=off in the test knobs" } else { "Leona is in the match (the sunlight easter egg)" }));
                }
            }
        }
        for (flag, kind) in [(Q_LAND, Kind::Spitter), (E_LAND, Kind::Lasher)] {
            if sim.get_entity(me).is_some_and(|e| summon::has_buff(&e, flag)) {
                sim.entity_remove_buff(me, flag);
                let spot = if kind == Kind::Spitter { self.b.q_spot } else { self.b.e_spot };
                match spot {
                    Some(at) => self.plant_at(sim, me, kind, at, "where the data left it (its landing)"),
                    None => {
                        if let Some(k) = tally(sim, "plant nospot") {
                            wlog(format!("{} PLANT NO SPOT #{k}: {flag} with no landing seen - no plant there", head(sim, me)));
                        }
                    }
                }
            }
        }
        if sim.get_entity(me).is_some_and(|e| summon::has_buff(&e, P_FAIL)) {
            sim.entity_remove_buff(me, P_FAIL);
            self.units(sim, me, false, "a plant's body was refused");
        }
        let tick = sim.tick();
        let player = self.player;
        for ev in self.b.flock.tick(sim, me, team, player, Some(pos)) {
            match ev {
                Event::NoUnit { .. } => {}
                Event::Look { id, n, line } => {
                    let (at_, name) = self.b.flock.get(id).map_or(((0.0, 0.0), String::new()), |m| (m.unit.at, m.unit.name.clone()));
                    let kind = if name == LASHER { Kind::Lasher } else { Kind::Spitter };
                    let plant = self.plants.iter_mut().filter(|pl| pl.unit.is_none() && pl.kind == kind && pl.until > tick)
                        .min_by(|a, b| dist(a.pos, at_).total_cmp(&dist(b.pos, at_)))
                        .filter(|pl| dist(pl.pos, at_) <= 3_000.0);
                    let linked = plant.map(|pl| pl.unit = Some(id)).is_some();
                    if let Some(k) = tally(sim, "plant look") {
                        wlog(format!("{} PLANT #{n} LOOK #{k}: {line}{}", head(sim, me),
                                     if linked { "" } else { " - NO plant of hers stands there: it only stands" }));
                    }
                    self.units(sim, me, true, "a plant's body read as a unit");
                }
                Event::Lost { id, why, .. } => {
                    if let Some(k) = tally(sim, "plant lost") {
                        wlog(format!("{} PLANT LOST #{k}: the unit #{id} spawn_unit named never read as one in {} ticks ({why})",
                                     head(sim, me), summon::FLOCK_LOOKS));
                    }
                    self.units(sim, me, false, "a plant's body never read as a unit");
                }
                Event::Line { n, line, .. } => {
                    if let Some(k) = tally(sim, "plant unit") {
                        wlog(format!("{} PLANT #{n} #{k}: {line}", head(sim, me)));
                    }
                }
                Event::Over { member, end } => {
                    let id = member.unit.id;
                    let mut then = String::new();
                    if end.fate == summon::Fate::Killed {
                        let before = self.plants.len();
                        self.plants.retain(|pl| pl.unit != Some(id));
                        if self.plants.len() < before {
                            then = " - the plant is destroyed: it strikes no more".to_string();
                        }
                        if end.age <= LOST_AGE {
                            self.units(sim, me, false, "a plant's body was gone at once");
                        }
                    }
                    if let Some(k) = tally(sim, "plant over") {
                        wlog(format!("{} PLANT #{} OVER #{k}: {}{then}", head(sim, me), member.unit.n, end.text));
                    }
                }
                Event::LetGo { member } => {
                    if let Some(k) = tally(sim, "plant let go") {
                        wlog(format!("{} PLANT #{} LET GO #{k}: {PLANT_CAP} bodies on the books - the unit #{} is out there, no longer \
                                      watched", head(sim, me), member.unit.n, member.unit.id));
                    }
                }
                Event::Wake { n, line } => {
                    if let Some(k) = tally(sim, "plant wake") {
                        wlog(format!("{} PLANT #{n} WAKE #{k}: {line}", head(sim, me)));
                    }
                }
            }
        }
        if self.b.ok && self.bodies_wanted() {
            sim.entity_remove_buff(me, P_UNIT);
            sim.add_buff(me, &BuffV1::timed(P_UNIT, FLAG_TICKS));
        }
    }

    /// Bodies work (a body read as a unit) or not (refused, never read): `P_UNIT` follows.
    fn units(&mut self, sim: &mut StableSim<'_>, me: usize, on: bool, why: &str) {
        if self.b.ok == on {
            return;
        }
        self.b.ok = on;
        if !on {
            sim.entity_remove_buff(me, P_UNIT);
        }
        if let Some(k) = tally(sim, "plant units") {
            wlog(format!("{} PLANT UNITS {} #{k}: {why} - {}", head(sim, me), if on { "ON" } else { "OFF" },
                         if on { "the data leaves the plants where Q and E land to the add-on" } else { "the data grows its own where Q and E land" }));
        }
    }

    /// Where a plant's body stands now (its unit alive under its id), if it has one.
    fn body_at(&self, sim: &StableSim<'_>, pl: &Plant) -> Option<(f64, f64)> {
        let id = pl.unit?;
        let m = self.b.flock.get(id)?;
        sim.get_entity(id).filter(|e| e.is_alive() && e.name().unwrap_or_default() == m.unit.name).map(|e| fpos(e.pos()))
    }

    /// A line for a hook that fired while bodies of hers are out.
    fn hooked(&self, sim: &StableSim<'_>, hook: &str, me: usize, entity: usize, other: usize, damage: Option<usize>) {
        if self.b.flock.live.is_empty() {
            return;
        }
        let who = match self.b.flock.get(entity) {
            Some(m) => format!("the plant's body #{}", m.unit.n),
            None if entity == me => "Zyra".to_string(),
            None => "neither Zyra nor a plant of hers".to_string(),
        };
        if let Some(k) = tally(sim, "plant hook") {
            wlog(format!("{} PLANT HOOK #{k} {hook}: entity #{entity} ({who}) -> #{other}{}", head(sim, me),
                         damage.map(|d| format!(", damage {d}")).unwrap_or_default()));
        }
    }

    /// 她的 Q / E / R 的标记（副本在出手那一 tick 挂在目标身上）。
    fn casts(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (f64, f64)) {
        let tags = [(zy("q_aim"), 0u8), (zy("e_aim"), 1u8), (zy("r_aim"), 2u8)];
        let mut now = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.team() == team {
                continue;
            }
            for (name, k) in &tags {
                if (0..e.buff_count()).filter_map(|j| e.buff_at(j)).any(|b| b.name() == name.as_str()) {
                    now.push((e.id(), *k, fpos(e.pos())));
                }
            }
        }
        let fresh: Vec<_> = now.iter().filter(|(id, k, _)| !self.aim_seen.contains(&(*id, *k))).cloned().collect();
        self.aim_seen = now.iter().map(|(id, k, _)| (*id, *k)).collect();
        let tick = sim.tick();
        for (id, k, land) in fresh {
            match k {
                0 => {
                    let r = self.p.s_r as f64;
                    self.b.q_spot = Some(land);
                    self.sun.landing(Kind::Spitter, land, tick);
                    self.grow(sim, me, Kind::Spitter, |s| dist(s, land) <= r);
                }
                1 => {
                    self.b.e_spot = Some(land);
                    self.sun.landing(Kind::Lasher, land, tick);
                    let d = dist(pos, land).max(1.0);
                    let over = self.p.e_over as f64 / d;
                    let end = (land.0 + (land.0 - pos.0) * over, land.1 + (land.1 - pos.1) * over);
                    let r = self.p.s_r as f64;
                    self.grow(sim, me, Kind::Lasher, |s| seg_dist(s, pos, end) <= r);
                }
                _ => {
                    let r = self.p.r_r as f64;
                    let mut n = 0;
                    // (a plant whose time is up goes in strike() this tick)
                    for pl in self.plants.iter_mut().filter(|pl| pl.until > tick && dist(pl.pos, land) <= r) {
                        pl.rage_until = tick + self.p.r_rage;
                        pl.next = pl.next.min(tick + 1);
                        n += 1;
                    }
                    // 0.1.5 (the 11-08 logs: no RAGE line in two launches): every R seen, with her plants round its spot
                    self.n_raim += 1;
                    let alive: Vec<(f64, f64)> = self.plants.iter().filter(|pl| pl.until > tick).map(|pl| pl.pos).collect();
                    let (count, nearest) = round_spot(&alive, land);
                    if let Some(k) = tally(sim, "r aim") {
                        let name = sim.get_entity(id).and_then(|e| e.name()).unwrap_or_default();
                        let near = nearest.map_or_else(|| "-".to_string(), |d| format!("{d:.0}"));
                        wlog(format!("{} R AIM #{}: Stranglethorns on {name}#{id} at ({:.0}, {:.0}) - her seed plants alive {count}, \
                                      the nearest {near} from the spot (rage reach {}), enraged {n} #{k}", head(sim, me),
                                     self.n_raim, land.0, land.1, self.p.r_r));
                    }
                    if n > 0 {
                        self.n_rage += 1;
                        if let Some(k) = tally(sim, "rage") {
                            wlog(format!("{} RAGE #{}: {n} of her seed plants round #{id}'s spot #{k}", head(sim, me),
                                         self.n_rage));
                        }
                    }
                }
            }
        }
    }

    fn strike(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, level: usize, ap: usize) {
        let tick = sim.tick();
        self.plants.retain(|pl| pl.until > tick);
        if self.plants.iter().all(|pl| pl.next > tick) {
            return;
        }
        let units = enemies(sim, team);
        let dmg = plant_damage(&self.p, level, ap);
        let mut spits = Vec::new();
        let at_now: Vec<Option<(f64, f64)>> = self.plants.iter().map(|pl| self.body_at(sim, pl)).collect();
        for (pl, body) in self.plants.iter_mut().zip(at_now) {
            if let Some(b) = body {
                pl.pos = b; // pushed, pulled: it strikes from where its body stands
            }
            if pl.next > tick {
                continue;
            }
            let reach = match pl.kind {
                Kind::Spitter => self.p.t_r,
                Kind::Lasher => self.p.v_r,
            } as f64;
            pl.next = tick + strike_period(&self.p, pl.rage_until > tick);
            let Some(u) = choose(&units, pl.pos, reach) else { continue };
            self.n_strike += 1;
            if let Some(k) = tally(sim, "strike") {
                wlog(format!("{} STRIKE #{}: {:?} -> #{} ({}) for {dmg}{} #{k}", head(sim, me), self.n_strike, pl.kind, u.id,
                             if u.champion { "champion" } else { "unit" }, if pl.rage_until > tick { ", enraged" } else { "" }));
            }
            match pl.kind {
                Kind::Spitter => {
                    let spec = ProjectileSpawnV1 {
                        caster_id: me,
                        team,
                        x: pl.pos.0.round().max(0.0) as u64,
                        y: (pl.pos.1 - SPIT_UP as f64).round().max(0.0) as u64,
                        radius: 1_000,
                        speed: self.p.spit_speed as u64,
                        move_kind: ProjectileMoveKindV1::Target.code(),
                        target_id: u.id,
                        target_x: 0,
                        target_y: 0,
                        penetrate: false,
                        attack_type: AttackTypeV1::Skill.code(),
                        casting_type: CastingTypeV1::Targeting.code(),
                        casting_target: CastingTargetV1::None.code(),
                    };
                    sim.spawn_projectile(&zy("t_spit"), &format!("{ID}:noop"), &spec);
                    let fly = (dist(pl.pos, u.pos) / self.p.spit_speed as f64).ceil() as usize;
                    spits.push(Spit { target: u.id, due: tick + fly.max(1), dmg });
                }
                Kind::Lasher => {
                    sim.deal_damage_typed(me, u.id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    let mut slow = BuffV1::timed(&zy("v_slow"), self.p.v_slow_t);
                    slow.move_speed_mult = -(self.p.v_slow as i32);
                    sim.add_buff(u.id, &slow);
                    let hit = InputTargetV1::target(u.id);
                    sim.play_view_effect(&zy("v_hit"), me, &hit, 0, 0, 0);
                    sim.play_sfx(&zy("v_hit"), me, &hit);
                }
            }
        }
        self.spits.extend(spits);
    }

    /// 飞到的刺扣血。
    fn land(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        let (due, wait): (Vec<Spit>, Vec<Spit>) = std::mem::take(&mut self.spits).into_iter().partition(|s| s.due <= tick);
        self.spits = wait;
        for s in due {
            if !sim.get_entity(s.target).is_some_and(|e| e.is_alive()) {
                continue;
            }
            sim.deal_damage_typed(me, s.target, s.dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            let hit = InputTargetV1::target(s.target);
            sim.play_view_effect(&zy("t_hit"), me, &hit, 0, 0, 0);
            sim.play_sfx(&zy("t_hit"), me, &hit);
        }
    }

    /// 她参与击杀敌方英雄：马上掉一颗种子。
    fn takedowns(&mut self, sim: &mut StableSim<'_>) -> bool {
        let n = sim.kill_log_count();
        if self.kills_seen > n {
            self.kills_seen = 0; // a new match in a reused passive
        }
        let Some(mine) = sim.get_player(self.player) else { return false };
        let (team, lane) = (mine.team(), mine.lane().map(|l| l.code()));
        let mut took = false;
        while self.kills_seen < n {
            let Some(k) = sim.kill_log_at(self.kills_seen) else { break };
            self.kills_seen += 1;
            if k.killer_team != team || lane.is_none() {
                continue;
            }
            let lane = lane.unwrap_or(u32::MAX);
            let assist = k.assist_positions.iter().take(k.assist_count.min(4) as usize).any(|&a| a == lane);
            if k.killer_position == lane || assist {
                took = true;
            }
        }
        took
    }
}

impl StablePassive for Garden {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.player = player;
        keep_params(sim, me, &self.p);
        self.b.flock.life = self.p.t_life + 1;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if self.next_seed == 0 {
            self.next_seed = sim.tick() + self.p.s_cd;
        }
        // the Params in the first SPAWN line of a launch only; the line itself capped in the presims (every respawn
        // writes one)
        let params = params_new(&self.p).then(|| format!(", {:?}", self.p));
        if tally(sim, "spawn").is_some() || params.is_some() {
            wlog(format!("{} SPAWN: the add-on's Zyra (player {player}, team {team}){}", head(sim, me),
                         params.unwrap_or_default()));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, ap, level, pos, alive) = (e.team(), e.stat().magic_power, e.level(), fpos(e.pos()), e.is_alive());
        let tick = sim.tick();
        if self.takedowns(sim) && alive {
            self.n_take += 1;
            if let Some(k) = tally(sim, "takedown") {
                wlog(format!("{} TAKEDOWN #{}: a seed now #{k}", head(sim, me), self.n_take));
            }
            self.drop_seed(sim, me, team, pos, "takedown");
            self.next_seed = tick + self.p.s_cd;
        }
        if alive && tick >= self.next_seed {
            self.next_seed = tick + self.p.s_cd;
            self.drop_seed(sim, me, team, pos, "timer");
        }
        // her seeds and plants stay after her death (League's)
        self.seeds(sim, me);
        self.casts(sim, me, team, pos);
        self.bodies_tick(sim, me, team, pos);
        self.sun.tick(sim, me, &self.p);
        self.land(sim, me);
        self.strike(sim, me, team, level, ap);
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            // only when her plants did something since the last line, and capped in the presims (0.1.2)
            let now = (self.n_grow, self.n_strike, self.n_rage, self.n_take, self.sun.n_sun);
            if tick > 0 && watch_news(self.watched, now) {
                self.watched = now;
                if let Some(k) = tally(sim, "watch") {
                    wlog(format!("{} WATCH: seeds {} ({} on the ground), grown {}, strikes {}, rages {} (R seen {}), takedowns {}, sunlit {} #{k}",
                                 head(sim, me), self.n_seeds, self.seeds.len(), self.n_grow, self.n_strike, self.n_rage,
                                 self.n_raim, self.n_take, self.sun.n_sun));
                }
            }
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, me: usize, entity: usize, target: usize, damage: &mut usize) {
        self.hooked(sim, "on_attack", me, entity, target, Some(*damage));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, me: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_kill", me, entity, victim, None);
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, me: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_unit_kill", me, entity, victim, None);
    }
}

struct NoopFx;
impl StableEffectType for NoopFx {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Zyra's seeds on the ground, seed plants striking champions first, plants one size bigger in Leona's sunlight) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "PLANTS: her plants have bodies of their own ('{SPITTER}' / '{LASHER}', spawn_unit: move speed 1, a harmless attack, \
         {PLANT_HP_PCT}% of her health) - {}; the add-on strikes as before, a destroyed body takes its plant; with bodies the data \
         leaves the plants where Q and E land to the add-on; pictures in a match with Leona (the sunlight egg). Test knobs ({}): {}",
        if KNOBS.off { "OFF by the test knobs: the plants are pictures as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(), KNOBS.shown()
    ));
    module.add_native_effect(format!("{ID}:noop"), NoopFx);
    module.add_native_effect(format!("{ID}:spitter"), PlantFx(Kind::Spitter));
    module.add_native_effect(format!("{ID}:lasher"), PlantFx(Kind::Lasher));
    module.add_native_passive(format!("{ID}:garden"), Garden::default());
    host.log(LogLevel::Info, "league_zyra v1 loaded (Zyra's seeds on the ground, seed plants striking champions first).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"s_cd":480,"pl_hi":90,"x":1}"#);
        assert_eq!((p.s_cd, p.pl_hi), (480, 90));
        assert_eq!(p.t_per, Params::default().t_per);
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"t_per":0,"v_slow":200}"#).t_per, 2);
        assert_eq!(parse_params(r#"{"v_slow":200}"#).v_slow, 95);
        assert_eq!(parse_params(r#"{"q_delay":31,"q_fast":5,"e_grow":26}"#).e_grow, 26);
    }

    #[test]
    fn plants_grow_stronger_with_her_level() {
        let p = Params::default();
        assert_eq!(plant_damage(&p, 1, 0), 20);
        assert_eq!(plant_damage(&p, 18, 0), 100);
        assert_eq!(plant_damage(&p, 30, 0), 100);
        assert_eq!(plant_damage(&p, 1, 100), 32); // + 12 % of 100 AP
        assert!(plant_damage(&p, 9, 0) > 50 && plant_damage(&p, 9, 0) < 60);
    }

    #[test]
    fn enraged_plants_strike_twice_as_often() {
        let p = Params::default();
        assert_eq!(strike_period(&p, false), 60);
        assert_eq!(strike_period(&p, true), 30);
    }

    #[test]
    fn seeds_fall_toward_the_nearest_champion() {
        let s = seed_spot((0.0, 0.0), Some((100_000.0, 0.0)), 30_000.0, 0);
        assert!((s.0 - 30_000.0).abs() < 1.0 && s.1.abs() < 1.0);
        let s = seed_spot((0.0, 0.0), Some((20_000.0, 0.0)), 30_000.0, 0);
        assert!((s.0 - 10_000.0).abs() < 1.0); // at most half way
        let a = seed_spot((50_000.0, 50_000.0), None, 30_000.0, 0);
        let b = seed_spot((50_000.0, 50_000.0), None, 30_000.0, 2);
        assert!(dist(a, b) > 10_000.0);
    }

    #[test]
    fn the_r_aim_line_sees_her_plants_round_the_spot() {
        assert_eq!(round_spot(&[], (0.0, 0.0)), (0, None));
        let (n, near) = round_spot(&[(40_000.0, 0.0), (0.0, 30_000.0), (-90_000.0, 0.0)], (0.0, 0.0));
        assert_eq!(n, 3);
        assert!(near.is_some_and(|d| (d - 30_000.0).abs() < 1e-6));
    }

    #[test]
    fn grasping_roots_reach_seeds_along_the_line() {
        assert!(seg_dist((50.0, 10.0), (0.0, 0.0), (100.0, 0.0)) < 10.5);
        assert!((seg_dist((150.0, 0.0), (0.0, 0.0), (100.0, 0.0)) - 50.0).abs() < 1e-6);
    }

    #[test]
    fn champions_come_first() {
        let units = [
            Unit { id: 1, pos: (1_000.0, 0.0), champion: false },
            Unit { id: 2, pos: (40_000.0, 0.0), champion: true },
            Unit { id: 3, pos: (90_000.0, 0.0), champion: true },
        ];
        assert_eq!(choose(&units, (0.0, 0.0), 50_000.0).map(|u| u.id), Some(2));
        assert_eq!(choose(&units, (0.0, 0.0), 10_000.0).map(|u| u.id), Some(1));
        assert!(choose(&units, (200_000.0, 0.0), 10_000.0).is_none());
    }

    #[test]
    fn buff_names_fit() {
        for x in ["q_aim", "e_aim", "r_aim", "v_slow", "s_seed", "t_spit", "t_plant", "v_plant", "sun_pop", "t_big_end"] {
            assert!(zy(x).len() <= BUFF_NAME_CAP);
        }
    }

    #[test]
    fn presim_lines_are_capped_for_the_launch_and_the_match_on_screen_is_not() {
        let logged: Vec<usize> = (0..LOG_EVERY * 3).filter_map(|_| noted("test presim", false)).collect();
        assert_eq!(logged.len(), LOG_FIRST + 3);
        assert_eq!(logged[LOG_FIRST..], [LOG_EVERY, LOG_EVERY * 2, LOG_EVERY * 3]);
        assert!((0..LOG_EVERY * 2).all(|_| noted("test shown", true).is_some()));
    }

    #[test]
    fn the_params_are_logged_once_and_watch_only_with_news() {
        let p = Params { s_cd: 7, ..Params::default() };
        assert!(params_new(&p));
        assert!(!params_new(&p));
        assert!(!watch_news((1, 4, 0, 0, 0), (1, 4, 0, 0, 0)), "only more seeds: no line");
        assert!(watch_news((1, 4, 0, 0, 0), (1, 5, 0, 0, 0)));
        assert!(watch_news(Watch::default(), (0, 0, 0, 1, 0)));
        assert!(watch_news(Watch::default(), (0, 0, 0, 0, 1)), "a plant grown in Leona's sunlight");
    }

    // ---- 0.2.0: the plants' bodies ----

    #[test]
    fn the_bodies_are_built_from_her_numbers() {
        let hers = StatV1 { attack: 60, magic_power: 120, hp: 1200, defence: 30, magic_resistance: 30, move_speed: 1000, hp_regen: 2,
                            stack: 0, crit_chance: 0 };
        let p = Params::default();
        let t = plant_spec(Kind::Spitter, &p, &hers, 2000);
        assert_eq!((t.name.as_str(), t.life), (SPITTER, p.t_life + 1));
        assert_eq!(t.stat, StatV1 { attack: 0, magic_power: 120, hp: 300, defence: 0, magic_resistance: 0, move_speed: 1, hp_regen: 0,
                                    stack: 0, crit_chance: 0 });
        assert_eq!((t.attack.attack, t.attack.attack_ratio, t.attack.range, t.attack.cooltime), (0, 0, p.t_r, p.t_per));
        assert_eq!((t.attack.duration, t.attack.start_timing), (TP_ACT, TP_LANDS));
        let v = plant_spec(Kind::Lasher, &p, &hers, 2000);
        assert_eq!((v.name.as_str(), v.attack.range, v.attack.duration, v.attack.start_timing), (LASHER, p.v_r, VP_ACT, VP_LANDS));
        assert_eq!(plant_spec(Kind::Spitter, &p, &StatV1::default(), 0).stat.hp, 1);
        for name in [P_UNIT, Q_LAND, E_LAND, P_FAIL, &summon::handoff(P_UID, usize::MAX)] {
            assert!(name.starts_with("league_zyra_") && name.len() <= BUFF_NAME_CAP, "{name}");
        }
    }

    #[test]
    fn the_copy_leaves_the_landing_plants_to_the_add_on_under_p_unit() {
        let copy = include_str!("../override/league_zyra.data_champion");
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{P_UNIT}\"")).count(), 3, "Q's two lobs and E's");
        assert_eq!(copy.matches(&format!("\"name\": \"{Q_LAND}\"")).count(), 2);
        assert_eq!(copy.matches(&format!("\"name\": \"{E_LAND}\"")).count(), 1);
    }

    use super::mock::{champion, MPlayer, World};

    const GAREN: usize = 1;

    fn log_file() -> std::path::PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_zyra_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_ZYRA_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// Zyra #0 (team 0, 2000 health) at (300000, 300000); Garen #1 30000 east of her; `leona`: Leona on Garen's side far
    /// off; a seed 5000 from Garen.
    fn world(leona: bool) -> (World, Garden) {
        log_file();
        let mut w = World::default();
        let mut zyra = champion("league_zyra", 0, 300_000.0, 300_000.0);
        (zyra.hp, zyra.max) = (2000, 2000);
        let mut garen = champion("league_garen", 1, 330_000.0, 300_000.0);
        (garen.hp, garen.max) = (50_000, 50_000);
        let other = if leona { "league_leona" } else { "league_darius" };
        w.units = vec![zyra, garen, champion(other, 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() }];
        let mut me = Garden::default();
        me.configure("{}");
        w.sim(|sim| me.on_spawn(sim, 0, 0));
        me.next_seed = usize::MAX;
        me.seeds.push(Seed { pos: (325_000.0, 300_000.0), until: usize::MAX, next_show: usize::MAX });
        (w, me)
    }

    fn tick(w: &mut World, me: &mut Garden) {
        for (name, caster, input) in w.due() {
            w.sim(|sim| match name.as_str() {
                "league_zyra:spitter" => PlantFx(Kind::Spitter).apply(sim, 0, caster, input),
                "league_zyra:lasher" => PlantFx(Kind::Lasher).apply(sim, 0, caster, input),
                other => panic!("an effect nobody registered: {other}"),
            });
        }
        w.sim(|sim| me.on_update(sim, 0, 0, 0));
        w.step();
    }

    fn run(w: &mut World, me: &mut Garden, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    /// The copy's Q at Garen: the 2-tick mark where it lands.
    fn q_at_garen(w: &mut World) {
        w.units[GAREN].buffs.push((BuffV1::timed(&zy("q_aim"), 2), 2));
    }

    fn bodies(w: &World) -> Vec<usize> {
        w.spawns.iter().filter(|s| s.name == SPITTER || s.name == LASHER).filter_map(|s| s.gave).collect()
    }

    #[test]
    fn a_seed_plant_gets_a_body_and_the_landing_plants_follow() {
        let (mut w, mut me) = world(false);
        run(&mut w, &mut me, 2);
        q_at_garen(&mut w);
        run(&mut w, &mut me, 4);
        let ids = bodies(&w);
        assert_eq!(ids.len(), 1, "the seed grew a Thorn Spitter with a body");
        assert_eq!((w.spawns[0].at, w.spawns[0].stat.move_speed), ((325_000, 300_000), 1));
        assert_eq!(w.viewed(&zy("t_plant")), 0, "a body and its picture both");
        assert_eq!(me.plants[0].unit, Some(ids[0]));
        assert!(w.has(0, P_UNIT), "a body read as a unit: the data leaves the landing plants to the add-on");
        // it strikes Garen (a spit, magic) from its body
        run(&mut w, &mut me, 80);
        assert!(!w.dealt(0, DamageTypeV1::Ap).is_empty());
        // the copy's landing with P_UNIT on her: Q_LAND - a plant of the add-on's where Q landed (Garen's spot)
        w.units[0].buffs.push((BuffV1::timed(Q_LAND, 3), 3));
        run(&mut w, &mut me, 3);
        assert_eq!(bodies(&w).len(), 2);
        assert_eq!(w.spawns[1].at, (330_000, 300_000));
        // destroyed: that plant strikes no more
        let n = me.plants.len();
        w.hurt(ids[0], 1_000_000);
        run(&mut w, &mut me, 3);
        assert_eq!(me.plants.len(), n - 1);
        assert!(me.plants.iter().all(|pl| pl.unit != Some(ids[0])));
    }

    #[test]
    fn no_body_from_the_host_keeps_the_pictures() {
        for case in 0..3 {
            let (mut w, mut me) = world(false);
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                _ => w.spawn_never = true,
            }
            run(&mut w, &mut me, 2);
            q_at_garen(&mut w);
            run(&mut w, &mut me, 10);
            assert!(!w.has(0, P_UNIT), "case {case}: P_UNIT without a body");
            if case < 2 {
                assert_eq!(w.viewed(&zy("t_plant")), 1, "case {case}: the plant's picture");
            }
            assert_eq!(me.plants.len(), 1, "case {case}");
            run(&mut w, &mut me, 80);
            assert!(!w.dealt(0, DamageTypeV1::Ap).is_empty(), "case {case}: the plant strikes as before");
        }
    }

    #[test]
    fn with_leona_in_the_match_the_plants_stay_pictures() {
        let (mut w, mut me) = world(true);
        run(&mut w, &mut me, 2);
        q_at_garen(&mut w);
        run(&mut w, &mut me, 10);
        assert!(bodies(&w).is_empty() && w.spawns.is_empty());
        assert_eq!(w.viewed(&zy("t_plant")), 1);
        assert!(!w.has(0, P_UNIT));
    }

    #[test]
    fn the_log_tells_the_bodies_lives() {
        let (mut w, mut me) = world(false);
        run(&mut w, &mut me, 2);
        q_at_garen(&mut w);
        run(&mut w, &mut me, 70);
        let ids = bodies(&w);
        let mut d = 0;
        w.sim(|sim| me.on_attack(sim, 0, ids[0], GAREN, &mut d));
        w.players[1].gold += 3;
        w.hurt(ids[0], 1_000_000);
        run(&mut w, &mut me, 10);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" PLANT")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "PLANT SPAWN #", "a Spitter's body, unit #4 for team 0 at (325000,300000): 'league_zyra_spitter' for 301 ticks, attack 0",
            "speed 1; hits 0 + 0% of its attack, range 50000, every 60 ticks (20 long, lands at 5)",
            "PLANT #1 LOOK #", "#4 reads back as name 'league_zyra_spitter'", "PLANT UNITS ON #",
            "the data leaves the plants where Q and E land to the add-on", " of 301 ticks, at (",
            "PLANT HOOK #", "on_attack: entity #4 (the plant's body #1) -> #1, damage 0",
            "OVER #", "KILLED after ", "p1 gold +3", "the plant is destroyed: it strikes no more",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
    }
}
