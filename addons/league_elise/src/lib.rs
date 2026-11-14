//! 伊莉丝附加包（用户 2026-10-15：「附加包要」——整身变蜘蛛 + 挑目标）。主包保持纯数据；`mod.override_info` 把主包的伊莉丝换成
//! `override/` 里的副本（`make_override.py` 用 tools/kit/build_elise.py 的 `native=1` 生成：加上本包的被动 `league_elise:queen`，
//! 技能2和大招改成对目标施放——结茧、盘丝、茧缚猎杀打向 AI 给的目标，不再是射程内随机一个英雄；技能2、大招的说明开头加【附加包】），
//! 本包补数据做不到的事：
//!
//! - **整身变蜘蛛**（`view.rs`，游戏 0.6.4 起的 Windows 版）：蜘蛛形态（主包的永久 buff `league_elise_sp`）时站着、跑着、挨打、阵亡也是
//!   蜘蛛（`c_idle` / `c_run` / `c_hit` / `c_dead`，奈德丽附加包的做法）。
//! - **结茧挑目标**（AI 钩子 `league_elise:aim`，人形、结茧好了、射程 `e_range` 内有敌方英雄时）：茧碰到第一个单位就停，所以挑
//!   **线上没有小兵、野怪、别的英雄挡着**的英雄：被控住的先（必中），再挑最近的（飞得短、最难躲开）；都被挡着就挑最近的英雄
//!   （和主包一样碰运气）。
//! - **盘丝挑目标**（同一个钩子，蜘蛛形态、盘丝好了、`ce_r` 内有敌方英雄时）：落到**生命比例最低**的英雄身上（一样低就近的）。
//! - **茧缚猎杀挑目标**（大招）：`r_range` 内**被控住的**英雄先（生命比例最低的），没有就挑生命比例最低的。
//!   别的时候（自爆蜘蛛、掠行狂暴）不换 AI 的目标。
//! - **小蜘蛛是真的单位（0.2.0，2026-11-14；用户：「召唤物的全做啊 剩下的一批英雄也做了啊」）**：主包的小蜘蛛是她身上的
//!   计数（`league_elise_sl1`–`sl3`）和蜘蛛形态每次普攻时挂在目标身上的撕咬。英雄联盟里变成蜘蛛时攒下的小蜘蛛全部出来，
//!   自己走、自己咬（魔法伤害）、能被打死，变回人形时收起来。稳定 mod API 的 `spawn_unit`（公用部分在萨科附加包的
//!   `summon.rs`，一个召唤者好几个单位用它的 `Flock`）：她身上出现蜘蛛形态（`league_elise_sp`）时被动按攒下的只数排原生效果
//!   `:spiderling`，在她身边生成 `league_elise_spiderling`（[`spiderling_spec`]）；有单位时她身上一直挂着 `SL_UNIT`，副本的数据
//!   读它、不再放挂在目标身上的撕咬；被打死的一只扣掉一只攒下的；变回人形或阵亡时放逐（`entity_banish`：没有让单位消失的
//!   接口）；掠行狂暴时给它们加攻速（英雄联盟的），盘丝落地时把它们放到她身边（英雄联盟里它们跟着她一起升空落下）。它们咬的
//!   是物理伤害（0.2.1 改了说法：英雄联盟是魔法伤害，单位的普攻没有伤害类型；引擎把这一口告诉被动 `on_attack` 时改成她打出的
//!   魔法伤害的代码留着，可游戏 0.7.2 从来不报单位的攻击，见玛尔扎哈附加包 0.2.1）。生成不了（宿主没有这个接口、失败、
//!   测试开关关了、读不成单位）就不挂 `SL_UNIT`，和今天一模一样。日志里 `SPIDERLING` 开头的行；测试开关：日志旁边的
//!   `league_elise.cfg`（`summon.rs`：`unit=off` / `still=1` / `name=`）。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_elise.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `FORM`（显示里变蜘蛛 / 变人、模拟里蜘蛛形态 buff 上下）、`COCOON` / `RAPPEL` / `HUNT`（挑了谁、为什么）：服务器的预模拟
//! 限了条数（整个游戏一个计数），你看的那场每条都记。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

use summon::{Event, Flock};

const ID: &str = "league_elise";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_elise") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
const HERO: &str = "league_elise";
/// 蜘蛛形态（主包数据的永久 buff）。
pub const FORM: &str = "league_elise_sp";
/// 结茧、盘丝的冷却标记（主包数据的施法者 buff）。
const E_CD: &str = "league_elise_e_cd";
const CE_CD: &str = "league_elise_ce_cd";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ELISE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_elise.log");
        }
    }
    PathBuf::from("league_elise.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line stalled the simulation thread (2026-10-12, #242)
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

/// 日志条数：每种整个游戏先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条；你看的那场每条都写（0.1.2：以前一起限，
/// 预模拟先把条数用完，2026-11-01 一晚看的几场只留下 3 行）。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind` (the count of the whole launch, every sim): its number when it is to be written - the first
/// `LOG_FIRST`, then every `LOG_EVERY`-th, and every one when `shown`.
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

/// Like `noted`, but every line of the match on screen: only the presims capped.
fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    noted(kind, on_screen(sim))
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 结茧：射程、茧的半宽（P 的 e_range / e_w）。
    pub e_range: usize,
    pub e_w: usize,
    /// 盘丝落到多远内的英雄（ce_r）、大招的射程（r_range）。
    pub ce_r: usize,
    pub r_range: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { e_range: 75000, e_w: 2500, ce_r: 50000, r_range: 75000 }
    }
}

/// `{"e_range":75000,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "e_range" => p.e_range = v,
            "e_w" => p.e_w = v,
            "ce_r" => p.ce_r = v,
            "r_range" => p.r_range = v,
            _ => {}
        }
    }
    p
}

/// 被动 `configure` 拿到的参数（每场都一样，都是主包的数），AI 钩子读它；被动还没配置时是默认值（= P）。
static SHARED: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

fn shared() -> Params {
    SHARED.lock().unwrap_or_else(|e| e.into_inner()).clone()
}

// ===================== 计算（单元测试用） =====================

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

pub fn seg_dist(a: Pt, b: Pt, p: Pt) -> f64 {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len2 = dx * dx + dy * dy;
    if len2 <= 0.0 {
        return dist(a, p);
    }
    let t = (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / len2).clamp(0.0, 1.0);
    dist((a.0 + t * dx, a.1 + t * dy), p)
}

/// 一个敌方单位：id、位置、生命、最大生命、身体半径、是不是英雄、身上有没有控制。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: Pt,
    pub hp: usize,
    pub max: usize,
    pub r: f64,
    pub champion: bool,
    pub cc: bool,
}

impl Unit {
    pub fn hp_pct(&self) -> usize {
        if self.max == 0 { 100 } else { self.hp * 100 / self.max }
    }
}

/// 身体半径没读到时按这么大算。
pub const BODY: f64 = 6_000.0;

/// 从 `me` 到 `to` 的线上，比 `to` 近的别的敌方单位挡着吗（茧碰到第一个单位就停）。
pub fn blocked(me: Pt, to: &Unit, units: &[Unit], half_w: f64) -> bool {
    let d = dist(me, to.at);
    units.iter().any(|u| {
        u.id != to.id && dist(me, u.at) < d && seg_dist(me, to.at, u.at) <= half_w + if u.r > 0.0 { u.r } else { BODY }
    })
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Why {
    /// 线上没挡着、被控住了（结茧）/ 被控住的里血最少（大招）。
    HeldClear,
    Held,
    /// 线上没挡着的里最近的。
    Clear,
    /// 都被挡着：最近的英雄。
    Blocked,
    /// 生命比例最低的。
    Lowest,
}

/// 生命比例低的在前，一样低就近的在前。
fn lower(me: Pt, a: &Unit, b: &Unit) -> std::cmp::Ordering {
    a.hp_pct().cmp(&b.hp_pct()).then(dist(me, a.at).total_cmp(&dist(me, b.at)))
}

/// 近的在前。
fn nearer(me: Pt, a: &Unit, b: &Unit) -> std::cmp::Ordering {
    dist(me, a.at).total_cmp(&dist(me, b.at))
}

/// 射程内的敌方英雄。
fn champions_within(me: Pt, units: &[Unit], reach: usize) -> Vec<Unit> {
    units.iter().copied().filter(|u| u.champion && dist(me, u.at) <= reach as f64).collect()
}

/// 结茧的目标：射程内的敌方英雄里，线上没被挡着的——被控住的先、再最近的；都被挡着就最近的。
pub fn cocoon_pick(me: Pt, units: &[Unit], p: &Params) -> Option<(Unit, Why)> {
    let champs = champions_within(me, units, p.e_range);
    let open: Vec<Unit> = champs.iter().copied().filter(|u| !blocked(me, u, units, p.e_w as f64)).collect();
    if let Some(u) = open.iter().filter(|u| u.cc).min_by(|a, b| nearer(me, a, b)) {
        return Some((*u, Why::HeldClear));
    }
    if let Some(u) = open.iter().min_by(|a, b| nearer(me, a, b)) {
        return Some((*u, Why::Clear));
    }
    champs.iter().min_by(|a, b| nearer(me, a, b)).map(|u| (*u, Why::Blocked))
}

/// 盘丝的目标：`ce_r` 内生命比例最低的敌方英雄（一样低就近的）。
pub fn rappel_pick(me: Pt, units: &[Unit], p: &Params) -> Option<(Unit, Why)> {
    champions_within(me, units, p.ce_r).iter().min_by(|a, b| lower(me, a, b)).map(|u| (*u, Why::Lowest))
}

/// 茧缚猎杀的目标：`r_range` 内被控住的敌方英雄先（生命比例最低的），没有就生命比例最低的。
pub fn hunt_pick(me: Pt, units: &[Unit], p: &Params) -> Option<(Unit, Why)> {
    let champs = champions_within(me, units, p.r_range);
    if let Some(u) = champs.iter().filter(|u| u.cc).min_by(|a, b| lower(me, a, b)) {
        return Some((*u, Why::Held));
    }
    champs.iter().min_by(|a, b| lower(me, a, b)).map(|u| (*u, Why::Lowest))
}

/// 技能2这次放的是什么（照主包数据的分支）：人形结茧、蜘蛛盘丝，别的（自爆蜘蛛、掠行狂暴）不换目标。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Skill2 {
    Cocoon,
    Rappel,
    Other,
}

/// `spider` 蜘蛛形态、`e_cd` / `ce_cd` 冷却标记、`champ_in` 射程内（人形 e_range、蜘蛛 ce_r）有没有敌方英雄。
pub fn skill2_kind(spider: bool, e_cd: bool, ce_cd: bool, champ_in: bool) -> Skill2 {
    match (spider, champ_in) {
        (false, true) if !e_cd => Skill2::Cocoon,
        (true, true) if !ce_cd => Skill2::Rappel,
        _ => Skill2::Other,
    }
}

/// 硬控（击飞、晕眩、定身、嘲讽、恐惧、魅惑、被强制位移）：结茧、盘丝和茧缚猎杀优先「被控住」的英雄。
/// 不是 `cc_count() > 0`：游戏 0.6.4 把正在播的施法动作也记成一种控制（`CcKindV1::Animation`），哪个敌人在放技能都算
/// 「被控」、都被优先选中（卡莉丝塔附加包 10-16 查出：她每一跳都被自己的动作叫停）。
const HARD_CC: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                                CcKindV1::Charm, CcKindV1::ForceMove];

/// One CC entry's kind is hard CC (not a cast animation, silence or disarm).
pub fn is_hard_cc(kind: u32) -> bool {
    HARD_CC.iter().any(|k| k.code() == kind)
}

fn hard_cc(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| is_hard_cc(c.kind)))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

// ===================== 小蜘蛛作为单位（0.2.0） =====================

/// The unit name: the game draws it from asset/base/aseprite_resources/champions/<name>, which mod.override_info sends to
/// the main pack's league/champions/league_elise_spiderling (tools/art/unit_elise_spiderling.py).
pub const SPIDERLING: &str = "league_elise_spiderling";
/// The main pack's stored spiderlings: one permanent caster flag more for each (sl1 -> sl2 -> sl3), gone at her death.
pub const SL_FLAGS: [&str; 3] = ["league_elise_sl1", "league_elise_sl2", "league_elise_sl3"];
/// Skittering Frenzy on her (the main pack's caster buff): its spiderlings bite x `SL_FZ` / 100.
pub const CW_ON: &str = "league_elise_cw_on";
/// A spiderling's bite and its pace: the main pack's sl_dmg + sl_ap % of her ability power (the unit's attack stat is
/// her ability power), once each of her attacks (atk_cd); x sl_fz % in the frenzy, made attack speed on the units
/// (League: the frenzy gives the spiderlings attack speed). make_override.py checks these against P.
pub const SL_HIT: usize = 12;
pub const SL_HIT_AP: usize = 10;
pub const SL_COOL: usize = 52;
pub const SL_FZ: usize = 150;
/// The unit sheet's attack: ticks long and the tick the bite lands (tools/art/unit_elise_spiderling.py: 400 ms, the bite
/// 140 ms in; make_override.py checks them against the sheet).
pub const SL_ACT: usize = 24;
pub const SL_LANDS: usize = 8;
/// League (wiki, 2026-11-14): health 85-390 against her 650-2503 (13-16 %), armour 30-90 against her 30-111 (about all
/// of it), magic resistance 50-110 against her 30-65 (about 170 %), move speed 350 against her 330, reach 100 against her
/// spider's 125 (her 23000 here: 18400). No timer in League (stored when she turns human); here `SL_LIFE` at a time, a
/// new one at once when one times out while she is still the spider.
pub const SL_HP_PCT: usize = 14;
pub const SL_DEF_PCT: usize = 100;
pub const SL_MR_PCT: usize = 170;
pub const SL_SPEED_PCT: usize = 106;
pub const SL_RANGE: usize = 18_400;
pub const SL_LIFE: usize = 900;
/// They come out this far round her, the first toward the nearest enemy champion.
pub const SL_SPREAD: f64 = 9_000.0;
/// On her while spiderlings of hers are units: the copy's data plays no riding bites.
pub const SL_UNIT: &str = "league_elise_sl_unit";
pub const SL_UID: &str = "league_elise_sl_uid";
/// On a spiderling in her frenzy: attack speed + (SL_FZ - 100) %.
pub const SL_FRENZY: &str = "league_elise_sl_frenzy";
/// Spiderlings on the books at once; ticks SL_UNIT is laid for (renewed every tick); the handoff buffs; the frenzy buff
/// on the units (laid again every FRENZY_EVERY ticks while hers lasts).
pub const SL_CAP: usize = 6;
const FLAG_TICKS: usize = 30;
const UID_TICKS: usize = 6;
const FRENZY_TICKS: usize = 30;
const FRENZY_EVERY: usize = 20;
/// A unit gone within this many ticks was never really there.
pub const LOST_AGE: usize = 6;
/// Spiderling bites the engine told her passive of, waiting to be dealt as magic damage next tick.
const PENDING_MAX: usize = 16;

/// The test knobs (`league_elise.cfg` beside the log), read once.
static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

/// Her stored spiderlings: how many of the main pack's flags are on her.
pub fn stored(e: &StableEntity<'_, '_>) -> usize {
    SL_FLAGS.iter().rposition(|f| summon::has_buff(e, f)).map_or(0, |k| k + 1)
}

/// A spiderling from her numbers now (`stat`, her health cap `max_hp`): its attack stat her ability power, each bite
/// `SL_HIT` + `SL_HIT_AP` % of it.
pub fn spiderling_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    summon::Spec {
        name: SPIDERLING.to_string(),
        life: SL_LIFE,
        stat: StatV1 { attack: stat.magic_power, magic_power: stat.magic_power, hp: (max_hp * SL_HP_PCT / 100).max(1),
                       defence: stat.defence * SL_DEF_PCT / 100, magic_resistance: stat.magic_resistance * SL_MR_PCT / 100,
                       move_speed: stat.move_speed * SL_SPEED_PCT / 100, hp_regen: 0, stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: SL_HIT_AP, attack: SL_HIT, range: SL_RANGE, cooltime: SL_COOL, duration: SL_ACT,
                               start_timing: SL_LANDS, cancelable: false, attack_type: AttackTypeV1::BaseAttack.code() },
    }
}

/// Where `n` spiderlings come out round her at `here`: `SL_SPREAD` round her, evenly, the first toward `foe` (none: east).
pub fn spiderling_points(here: summon::Pt, foe: Option<summon::Pt>, n: usize) -> Vec<summon::Pt> {
    let first = foe.map_or(0.0, |f| (f.1 - here.1).atan2(f.0 - here.0));
    summon::spread(here, SL_SPREAD, n, first).into_iter().map(|p| (p.0.max(0.0), p.1.max(0.0))).collect()
}

fn at_input(at: summon::Pt) -> InputTargetV1 {
    InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64)
}

/// One spiderling for Elise `me` at `at`, handed to her passive by a `<SL_UID>:<id>` buff. -> its id.
fn make_spiderling(sim: &mut StableSim<'_>, me: usize, at: summon::Pt, by: &str) -> Option<usize> {
    let (team, stat, max) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1))?;
    let spec = spiderling_spec(&stat, max).with(&KNOBS);
    let at = summon::inside(summon::field(sim), at);
    match summon::spawn(sim, me, team, at, &spec) {
        Some(id) => {
            sim.add_buff(me, &BuffV1::timed(&summon::handoff(SL_UID, id), UID_TICKS));
            if let Some(k) = tally(sim, "sl spawn") {
                wlog(format!("{} SPIDERLING SPAWN #{k} ({by}): unit #{id} for team {team} at {}: {}", head(sim, me), summon::pt(at),
                             spec.shown()));
            }
            Some(id)
        }
        None => {
            if let Some(k) = tally(sim, "sl fail") {
                wlog(format!("{} SPIDERLING SPAWN FAILED #{k} ({by}): spawn_unit gave no unit for '{}' at {}", head(sim, me),
                             spec.name, summon::pt(at)));
            }
            None
        }
    }
}

/// `:spiderling` - one of her spiderlings (the passive queues one for each to come); the input is where it comes out.
struct SpiderlingFx;

impl StableEffectType for SpiderlingFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let at = if InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Pos) {
            (input.x as f64, input.y as f64)
        } else {
            match sim.get_entity(caster) {
                Some(e) => summon::at_of(&e),
                None => return,
            }
        };
        make_spiderling(sim, caster, at, "the queued effect");
    }
}

/// A spiderling as the passive keeps it: its bites turned into magic damage.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct SlBook {
    pub turned: usize,
}

/// The OVER line's word on a spiderling's bites: physical unless the engine named it in on_attack (game 0.7.2 never does).
pub fn bites_text(turned: usize) -> String {
    if turned == 0 {
        "its bites physical (no hit of it reached her on_attack, so none was made magic)".to_string()
    } else {
        format!("{turned} of its bites dealt as magic (on_attack named it)")
    }
}

// ===================== 神经毒素 / 剧毒之蜇：按当前 / 已损生命（0.2.1，2026-11-14） =====================
//
// 用户 2026-11-14 看了还剩下的、做得到的小项：「接着做」。英雄联盟（wiki 现行页面）：神经毒素「deals magic damage based on the
// target's current health」，40-160 (+ 4% (+ 3% per 100 AP) of target's current health)；剧毒之蜇「deals damage based on the
// target's missing health」，50-170 (+ 8% (+ 3% per 100 AP) of target's missing health)，魔法伤害；按生命算的那部分对野怪有
// 上限 65-145 (+ 90% AP)。数据读不到当前生命：主包是目标最大生命的 3% / 5% 真实伤害（FixedAttack target_hp_ratio）。副本把这
// 两块换成本包的原生效果 `:neuro` / `:bite`，放在同一下的最前面（按挨这一下之前的生命算：英雄联盟是一下打出来的）。

/// The share of the target's health her Q deals: Neurotoxin (human Q) `Q_CUR` % of its current health, Venomous Bite
/// (spider Q, and the bite of her ult's hunt) `CQ_MISS` % of its missing health, both magic. League's base shares; League
/// adds 3 % per 100 ability power to each, while here her ability power stays in the flat part as the main pack has it
/// (q_ap 60 %, cq_ap 70 % - League's flat parts have none), so it is not counted twice. Against monsters the share is at
/// most `QM_DMG` + `QM_AP` % of her ability power (League: 65-145 + 90 %; the middle rank's 105 scaled like her Q's flat
/// damage, League's 100 -> 70 here).
pub const Q_CUR: usize = 4;
pub const CQ_MISS: usize = 8;
pub const QM_DMG: usize = 75;
pub const QM_AP: usize = 90;
/// No unit in the native's input (a move's end, should it hand over a spot): the nearest enemy this close to her.
pub const VENOM_NEAR: f64 = 25_000.0;

/// Which of her Qs a native hit is.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Venom {
    /// Neurotoxin (human): by the target's current health.
    Neuro,
    /// Venomous Bite (spider, and the hunt's bite): by its missing health.
    Bite,
}

/// The health share of `kind` on a unit with `hp` of `max` health; a `monster` (a camp, an epic monster) capped by her
/// ability power `ap`.
pub fn venom_damage(kind: Venom, hp: usize, max: usize, monster: bool, ap: usize) -> usize {
    let share = match kind {
        Venom::Neuro => hp.min(max) * Q_CUR / 100,
        Venom::Bite => max.saturating_sub(hp) * CQ_MISS / 100,
    };
    if monster { share.min(QM_DMG + ap * QM_AP / 100) } else { share }
}

/// `:neuro` / `:bite` - first in Neurotoxin's bolt hit (a projectile's applied effect is given the unit it hit), in
/// Venomous Bite's landing and in the hunt's bite.
pub struct VenomFx(pub Venom);

impl StableEffectType for VenomFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let kind = self.0;
        let (word, share, tag) = match kind {
            Venom::Neuro => ("NEURO", format!("{Q_CUR}% of its current health"), "q neuro"),
            Venom::Bite => ("BITE", format!("{CQ_MISS}% of its missing health"), "q bite"),
        };
        let Some((team, ap, at)) = sim.get_entity(caster).map(|e| (e.team(), e.stat().magic_power, summon::at_of(&e))) else { return };
        let given = (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id);
        let (target, found) = match given {
            Some(id) => (Some(id), ""),
            None => ((0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                         .filter(|u| u.team() != team && u.is_alive() && summon::hittable(u))
                         .map(|u| (u.id(), summon::dist(summon::at_of(&u), at)))
                         .filter(|u| u.1 <= VENOM_NEAR)
                         .min_by(|a, b| a.1.total_cmp(&b.1))
                         .map(|u| u.0),
                     " (no unit in the effect's input: the nearest enemy to her)"),
        };
        let seen = target.and_then(|id| sim.get_entity(id).map(|e| {
            let (hp, max) = e.hp();
            (id, hp, max, e.is_alive() && e.team() != team,
             matches!(e.kind(), Some(EntityKindV1::Jungle | EntityKindV1::Epic | EntityKindV1::Serpen)))
        }));
        let Some((id, hp, max, true, monster)) = seen else {
            if let Some(k) = tally(sim, tag) {
                wlog(format!("{} Q {word} #{k}: no living enemy to hit{found} - none of the share dealt", head(sim, caster)));
            }
            return;
        };
        let dmg = venom_damage(kind, hp, max, monster, ap);
        let full = venom_damage(kind, hp, max, false, ap);
        if dmg > 0 {
            sim.deal_damage_typed(caster, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        }
        if let Some(k) = tally(sim, tag) {
            wlog(format!("{} Q {word} #{k} on {}: hp {hp}/{max} - {share}: {dmg} magic{}{found}", head(sim, caster), who(sim, id),
                         if dmg < full { format!(" (capped against a monster: {QM_DMG} + {QM_AP}% of her {ap} ability power)") }
                         else { String::new() }));
        }
    }
}

// ===================== 被动：蜘蛛女皇（参数 + 模拟里的形态日志 + 小蜘蛛单位） =====================

#[derive(Clone)]
struct Queen {
    /// 上一 tick 身上有没有蜘蛛形态 buff（None = 这条命还没看过）。
    spider: Option<bool>,
    /// 0.2.0: her own unit; her spiderlings as units; the batch asked for and not all come yet (the tick, how many still
    /// to come: the units one tick's queued effects bring are handed over together, to one ask of the flock); whether
    /// they are units (`SL_UNIT` on her); no more asks in this spider form (a spawn failed); her bites waiting to be
    /// dealt as magic; whether she was targetable last tick (Rappel); the tick of the last frenzy buff on them.
    me: usize,
    lings: Flock<SlBook>,
    batch: Option<(usize, usize)>,
    units: bool,
    failed: bool,
    magic: Vec<(usize, usize, usize)>,
    up: bool,
    frenzy_at: usize,
}

impl Default for Queen {
    fn default() -> Self {
        Queen { spider: None, me: 0, lings: Flock::new(SL_UID, SL_CAP, SL_LIFE), batch: None, units: false, failed: false,
                magic: Vec::new(), up: true, frenzy_at: 0 }
    }
}

impl Queen {
    /// Spiderlings asked for at `points` (one queued effect each, all in this tick: one ask of the flock).
    fn ask(&mut self, sim: &mut StableSim<'_>, me: usize, points: &[summon::Pt], why: &str) {
        if points.is_empty() {
            return;
        }
        self.lings.ask(sim.tick(), SL_LIFE, SlBook::default());
        self.batch = Some((sim.tick(), points.len()));
        let mut refused = 0;
        for at in points {
            if !sim.queue_effect(&format!("{ID}:spiderling"), AttackTypeV1::Skill, me, &at_input(*at), 1) {
                refused += 1;
                make_spiderling(sim, me, *at, "queue_effect refused: spawned by the passive");
            }
        }
        if let Some(k) = tally(sim, "sl ask") {
            let at: Vec<String> = points.iter().map(|p| summon::pt(*p)).collect();
            wlog(format!("{} SPIDERLING ASK #{k}: {why}: {} at {} ({SL_SPREAD:.0} round her){}", head(sim, me), points.len(),
                         at.join(" "), if refused == 0 { String::new() } else { format!(" - queue_effect REFUSED {refused} times") }));
        }
    }

    /// One of the batch came (or never will): how many are still to come; none - the batch is over.
    fn came(&mut self) {
        if let Some((t, n)) = self.batch {
            self.batch = (n > 1).then_some((t, n - 1));
        }
    }

    /// No spiderling of hers is a unit: the main pack's bites ride on her target again.
    fn units_off(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        if self.units {
            self.units = false;
            sim.entity_remove_buff(me, SL_UNIT);
            if let Some(k) = tally(sim, "sl off") {
                wlog(format!("{} SPIDERLING UNITS OFF #{k}: {why} - the spiderlings bite with her attacks as before", head(sim, me)));
            }
        }
    }

    /// Her spiderlings out of play: each banished until its time (no API ends a unit early; League stores them when she
    /// turns human, and they die with her), then off the books.
    fn banish_all(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        let tick = sim.tick();
        let ids: Vec<(usize, usize, usize)> = self.lings.live.iter().map(|m| (m.unit.id, m.unit.n, m.unit.left(tick))).collect();
        let mut done = Vec::new();
        for (id, n, left) in &ids {
            let alive = sim.get_entity(*id).is_some_and(|e| e.is_alive());
            let ok = alive && sim.entity_banish(me, *id, (*left).max(1), "", "");
            done.push(format!("#{n} (unit #{id}, {left} ticks) {}", if ok { "banished" } else if alive { "REFUSED" } else { "gone" }));
        }
        let gone = self.lings.orphans();
        self.batch = None;
        self.magic.clear();
        if self.units {
            self.units = false;
            sim.entity_remove_buff(me, SL_UNIT);
        }
        if !gone.is_empty() {
            if let Some(k) = tally(sim, "sl banish") {
                wlog(format!("{} SPIDERLING BANISH #{k}: {why} - {}", head(sim, me), done.join(", ")));
            }
        }
    }

    /// A spiderling killed: one stored spiderling fewer (League: a dead spiderling is gone until a new one is gained).
    fn lose_one(&mut self, sim: &mut StableSim<'_>, me: usize) -> usize {
        let left = sim.get_entity(me).map_or(0, |e| stored(&e));
        if left > 0 {
            sim.entity_remove_buff(me, SL_FLAGS[left - 1]);
        }
        left.saturating_sub(1)
    }

    /// The spiderlings' part of a tick: the asks for the stored ones, the flock, the frenzy, Rappel's drop, the flag.
    fn lings_tick(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize, spider: bool, entered: bool) {
        let tick = sim.tick();
        let Some((team, here, count, up)) = sim.get_entity(me).map(|e| (e.team(), summon::at_of(&e), stored(&e), e.is_targetable()))
        else { return };
        for (target, amount, unit) in std::mem::take(&mut self.magic) {
            if sim.get_entity(target).is_some_and(|e| e.is_alive()) {
                sim.deal_damage_typed(me, target, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                if let Some(m) = self.lings.get_mut(unit) {
                    m.extra.turned += 1;
                }
            }
        }
        if entered {
            self.failed = false;
        }
        // a batch some of which never came (a spawn refused, an id never read): no more asks in this Spider Form
        if let Some((t, n)) = self.batch {
            if tick > t + summon::FLOCK_WAIT + summon::FLOCK_LOOKS + 2 {
                self.batch = None;
                self.failed = true;
                if let Some(k) = tally(sim, "sl short") {
                    wlog(format!("{} SPIDERLING SHORT #{k}: {n} of the spiderlings asked for at t={t} never came - no more asks in \
                                  this Spider Form", head(sim, me)));
                }
            }
        }
        if spider && !KNOBS.off && !self.failed {
            let have = self.lings.live.len() + self.batch.map_or(0, |b| b.1);
            if count > have {
                let foe = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                    .filter(|u| u.team() != team && u.is_champion() && u.is_alive())
                    .map(|u| summon::at_of(&u))
                    .min_by(|a, b| summon::dist(*a, here).total_cmp(&summon::dist(*b, here)));
                let points = spiderling_points(here, foe, count);
                let why = if entered { "Spider Form: her stored spiderlings" } else { "more of hers in Spider Form" };
                let want: Vec<summon::Pt> = (have..count).map(|k| points[k % points.len().max(1)]).collect();
                self.ask(sim, me, &want, why);
            }
        } else if spider && KNOBS.off && entered {
            if let Some(k) = tally(sim, "sl knob") {
                wlog(format!("{} SPIDERLING OFF #{k}: unit=off in the test knobs - the spiderlings bite with her attacks as before",
                             head(sim, me)));
            }
        }
        for ev in self.lings.tick(sim, me, team, player, Some(here)) {
            match ev {
                Event::NoUnit { asked, .. } => {
                    self.batch = None;
                    self.failed = true;
                    if let Some(k) = tally(sim, "sl none") {
                        wlog(format!("{} SPIDERLING NONE #{k}: no spiderling came within {} ticks of the ask at t={asked} - no more \
                                      asks in this Spider Form", head(sim, me), summon::FLOCK_WAIT));
                    }
                }
                Event::Look { n, line, .. } => {
                    self.came();
                    if !self.units {
                        self.units = true;
                        if let Some(k) = tally(sim, "sl on") {
                            wlog(format!("{} SPIDERLING UNITS ON #{k}: her spiderlings are units - no riding bites in the data",
                                         head(sim, me)));
                        }
                    }
                    if let Some(k) = tally(sim, "sl look") {
                        wlog(format!("{} SPIDERLING #{n} LOOK #{k}: {line}", head(sim, me)));
                    }
                }
                Event::Lost { id, why, .. } => {
                    self.came();
                    self.failed = true;
                    if let Some(k) = tally(sim, "sl lost") {
                        wlog(format!("{} SPIDERLING LOST #{k}: the unit #{id} spawn_unit named never read as one in {} ticks ({why})",
                                     head(sim, me), summon::FLOCK_LOOKS));
                    }
                }
                Event::Line { n, line, .. } => {
                    if let Some(k) = tally(sim, "sl unit") {
                        wlog(format!("{} SPIDERLING #{n} #{k}: {line}", head(sim, me)));
                    }
                }
                Event::Over { member, end } => {
                    let n = member.unit.n;
                    let then = if end.fate == summon::Fate::Killed && end.age > LOST_AGE {
                        format!(" - one stored spiderling fewer: {} left", self.lose_one(sim, me))
                    } else if end.age <= LOST_AGE {
                        self.failed = true;
                        " - never really there: no more asks in this Spider Form".to_string()
                    } else {
                        " - another comes at once while she is the spider".to_string()
                    };
                    if let Some(k) = tally(sim, "sl over") {
                        wlog(format!("{} SPIDERLING #{n} OVER #{k}: {}; {}{then}", head(sim, me), end.text,
                                     bites_text(member.extra.turned)));
                    }
                }
                Event::LetGo { member } => {
                    if let Some(k) = tally(sim, "sl let go") {
                        wlog(format!("{} SPIDERLING #{} LET GO #{k}: {SL_CAP} spiderlings on the books - the unit #{} is out there, \
                                      no longer watched", head(sim, me), member.unit.n, member.unit.id));
                    }
                }
                Event::Wake { n, line } => {
                    if let Some(k) = tally(sim, "sl wake") {
                        wlog(format!("{} SPIDERLING #{n} WAKE #{k}: {line}", head(sim, me)));
                    }
                }
            }
        }
        if self.lings.live.is_empty() && self.batch.is_none() {
            self.units_off(sim, me, "no spiderling of hers is out");
        }
        // Skittering Frenzy: the spiderlings attack faster (League's; the main pack's bites hit harder)
        if !self.lings.live.is_empty() && tick >= self.frenzy_at + FRENZY_EVERY
            && sim.get_entity(me).is_some_and(|e| summon::has_buff(&e, CW_ON)) {
            self.frenzy_at = tick;
            let mut b = BuffV1::timed(SL_FRENZY, FRENZY_TICKS);
            b.attack_speed_mult = (SL_FZ - 100) as i32;
            let ids = self.lings.ids();
            for id in &ids {
                sim.entity_remove_buff(*id, SL_FRENZY);
                sim.add_buff(*id, &b);
            }
            let on = ids.iter().filter(|id| sim.get_entity(**id).is_some_and(|e| summon::has_buff(&e, SL_FRENZY))).count();
            if let Some(k) = tally(sim, "sl frenzy") {
                wlog(format!("{} SPIDERLING FRENZY #{k}: +{}% attack speed on {} spiderlings, the buff is on {on} of them", head(sim, me),
                             SL_FZ - 100, ids.len()));
            }
        }
        // Rappel: she comes down and her spiderlings drop with her (League's descent takes them along)
        if spider && up && !self.up && !self.lings.live.is_empty() {
            let points = spiderling_points(here, None, self.lings.live.len());
            let mut moved = 0;
            for (id, p) in self.lings.ids().into_iter().zip(points) {
                let p = summon::inside(summon::field(sim), p);
                if sim.entity_set_pos(id, p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64) {
                    moved += 1;
                }
            }
            if let Some(k) = tally(sim, "sl drop") {
                wlog(format!("{} SPIDERLING DROP #{k}: she landed at {} - {moved} of {} spiderlings set down beside her", head(sim, me),
                             summon::pt(here), self.lings.live.len()));
            }
        }
        self.up = up;
        if self.units {
            sim.entity_remove_buff(me, SL_UNIT);
            sim.add_buff(me, &BuffV1::timed(SL_UNIT, FLAG_TICKS));
        }
    }

    /// A line for a hook that fired while spiderlings of hers are out.
    fn hooked(&self, sim: &StableSim<'_>, hook: &str, entity: usize, other: usize, extra: String) {
        if self.lings.live.is_empty() {
            return;
        }
        let whose = match self.lings.get(entity) {
            Some(m) => format!("the spiderling #{}", m.unit.n),
            None if entity == self.me => "Elise".to_string(),
            None => "neither Elise nor a spiderling of hers".to_string(),
        };
        if let Some(k) = tally(sim, "sl hook") {
            wlog(format!("{} SPIDERLING HOOK #{k} {hook}: entity #{entity} ({whose}) -> {}{extra}", head(sim, self.me), who(sim, other)));
        }
    }
}

impl StablePassive for Queen {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let p = parse_params(params_json);
        let mut s = SHARED.lock().unwrap_or_else(|e| e.into_inner());
        if *s != p {
            wlog(format!("params {params_json} -> {p:?}"));
            *s = p;
        }
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        // a new life: the old one's spiderlings were banished at her death; a new one is a new entity
        self.banish_all(sim, entity, "Elise respawned");
        (self.spider, self.me, self.failed, self.up) = (None, entity, false, true);
        if let Some(k) = tally(sim, "spawn") {
            wlog(format!("{} SPAWN {} (the add-on's Elise) #{k}", head(sim, entity), who(sim, entity)));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        // League's spiderlings die with her (a dead champion's passive does not run: banished now, until their time)
        let me = self.me;
        self.banish_all(sim, me, "Elise died");
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let sp = has_buff(sim, me, FORM);
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        if self.spider.is_some_and(|was| was != sp) {
            if let Some(k) = tally(sim, "form_sim") {
                wlog(format!("{} FORM sim: {}{} #{k}", head(sim, me), if sp { "SPIDER on" } else { "spider off (human)" },
                    if alive { "" } else { ", dead" }));
            }
        }
        let entered = sp && self.spider != Some(true);
        if !sp && self.spider == Some(true) {
            // Human Form: League stores the spiderlings (here: banished until their time)
            self.banish_all(sim, me, "Human Form - her spiderlings are stored");
        }
        self.spider = Some(sp);
        if alive {
            self.me = me;
            self.lings_tick(sim, player, me, sp, entered);
        }
    }

    // The spiderlings' bites: should the engine ever tell her passive of one under the spiderling's id, it is dealt as
    // magic damage next tick instead (League's spiderlings deal magic damage; a unit's own attack is physical). Game 0.7.2
    // never names a unit in on_attack (league_malzahar's voidlings, its presims of 2026-11-14): the bites stay physical.
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, target: usize, damage: &mut usize) {
        let mine = self.lings.get(entity).is_some();
        let amount = *damage;
        let turned = mine && amount > 0 && self.magic.len() < PENDING_MAX;
        if turned {
            *damage = 0;
            self.magic.push((target, amount, entity));
        }
        self.hooked(sim, "on_attack", entity, target, if turned {
            format!(", damage {amount}: dealt as magic next tick")
        } else {
            format!(", damage {amount}")
        });
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_kill", entity, victim, String::new());
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_unit_kill", entity, victim, String::new());
    }
}

// ===================== AI 钩子：结茧、盘丝、茧缚猎杀挑目标 =====================

#[derive(Clone, Default)]
struct AimAi;

impl StablePlayerAi for AimAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:aim")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let b = base?;
        let kind = InputKindV1::from_code(b.kind)?;
        if !matches!(kind, InputKindV1::Skill2 | InputKindV1::Ult)
            || InputTargetKindV1::from_code(b.target.kind) != Some(InputTargetKindV1::Target)
        {
            return None;
        }
        let current = b.target.target_id;
        let player = ctx.player_id();
        let p = shared();
        let (pick, line, shown) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let (mid, team) = (me.id(), me.team());
            let at = (me.pos().0 as f64, me.pos().1 as f64);
            let mut units = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(u) = sim.entity_at(i) else { continue };
                if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower() || !sim.is_visible(team, u.id()) {
                    continue;
                }
                let (hp, max) = u.hp();
                units.push(Unit { id: u.id(), at: (u.pos().0 as f64, u.pos().1 as f64), hp, max, r: u.radius() as f64,
                                  champion: u.is_champion(), cc: hard_cc(&u) });
            }
            let champ_within = |r: usize| units.iter().any(|u| u.champion && dist(at, u.at) <= r as f64);
            let (got, tag) = if kind == InputKindV1::Ult {
                (hunt_pick(at, &units, &p), "HUNT")
            } else {
                let spider = has_buff(&sim, mid, FORM);
                let reach = if spider { p.ce_r } else { p.e_range };
                match skill2_kind(spider, has_buff(&sim, mid, E_CD), has_buff(&sim, mid, CE_CD), champ_within(reach)) {
                    Skill2::Cocoon => (cocoon_pick(at, &units, &p), "COCOON"),
                    Skill2::Rappel => (rappel_pick(at, &units, &p), "RAPPEL"),
                    Skill2::Other => return None,
                }
            };
            let (u, why) = got?;
            let why = match why {
                Why::HeldClear => "HELD + CLEAR line".to_string(),
                Why::Held => format!("HELD, {}% hp", u.hp_pct()),
                Why::Clear => "CLEAR line, nearest".to_string(),
                Why::Blocked => "all blocked, nearest".to_string(),
                Why::Lowest => format!("LOWEST: {}% hp", u.hp_pct()),
            };
            let line = format!("{} {tag} {} -> {} ({why}; {:.0} away)", head(&sim, mid), who(&sim, current), who(&sim, u.id),
                               dist(at, u.at));
            (u, line, on_screen(&sim))
        };
        if pick.id == current {
            if let Some(k) = noted("aim", shown) {
                wlog(format!("{line} kept #{k}"));
            }
            return None;
        }
        let input = InputV1::action(kind, InputTargetV1::target(pick.id));
        if !ctx.is_valid_input(&input) {
            if let Some(k) = noted("aim", shown) {
                wlog(format!("{line} refused by the game, the AI's target kept #{k}"));
            }
            return None;
        }
        if let Some(k) = noted("aim", shown) {
            wlog(format!("{line} AIM #{k}"));
        }
        Some(input)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Elise: the whole-body spider, the Cocoon's, Rappel's and the hunt's targets, her spiderlings units of their own) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "SPIDERLINGS: her stored spiderlings are units in Spider Form ('{}', spawn_unit) - {}; one for each stored ({} + {}% of her \
         ability power a bite, physical - a unit's attack has no damage type - every {SL_COOL} ticks, {SL_HP_PCT}% of her health, \
         {SL_LIFE} ticks at a time), banished when she turns human or dies. Test knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(SPIDERLING),
        if KNOBS.off { "OFF by the test knobs: the spiderlings bite with her attacks as before" } else { "ON" }, SL_HIT, SL_HIT_AP,
        LOG_PATH.with_extension("cfg").display(), KNOBS.shown()
    ));
    wlog(format!(
        "VENOM: Neurotoxin deals {Q_CUR}% of the target's current health, Venomous Bite (and the hunt's bite) {CQ_MISS}% of its \
         missing health, magic (the copy's {ID}:neuro / :bite in place of the main pack's % of max health as true damage); \
         against monsters at most {QM_DMG} + {QM_AP}% of her ability power."
    ));
    view::install_once();
    module.add_native_effect(format!("{ID}:neuro"), VenomFx(Venom::Neuro));
    module.add_native_effect(format!("{ID}:bite"), VenomFx(Venom::Bite));
    module.add_native_passive(format!("{ID}:queen"), Queen::default());
    module.add_native_effect(format!("{ID}:spiderling"), SpiderlingFx);
    module.add_player_input_ai(AimAi);
    host.log(LogLevel::Info, "league_elise loaded (whole-body spider, Cocoon / Rappel / hunt targets, spiderlings as units).");
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
    fn a_cast_animation_is_not_hard_cc() {
        assert!(!is_hard_cc(CcKindV1::Animation.code()));
        assert!(!is_hard_cc(CcKindV1::BlockSkill.code()));
        for k in [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm,
                  CcKindV1::ForceMove] {
            assert!(is_hard_cc(k.code()));
        }
    }

    fn champ(id: usize, at: Pt, hp: usize, max: usize) -> Unit {
        Unit { id, at, hp, max, r: 6_000.0, champion: true, cc: false }
    }

    fn minion(id: usize, at: Pt) -> Unit {
        Unit { id, at, hp: 300, max: 300, r: 4_000.0, champion: false, cc: false }
    }

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"ce_r":40000,"junk":7,"e_w":3000}"#);
        assert_eq!((p.ce_r, p.e_w, p.e_range, p.r_range), (40000, 3000, 75000, 75000));
    }

    #[test]
    fn the_copy_carries_the_default_params_and_the_targeted_casts() {
        let copy = include_str!("../override/league_elise.data_champion");
        let at = copy.find("\"passive_ref\": \"league_elise:queen\"").expect("no league_elise:queen passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("ce_r", d.ce_r), ("e_range", d.e_range), ("e_w", d.e_w), ("r_range", d.r_range)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for slot in ["\"skill2\"", "\"ult\""] {
            let s = &copy[copy.find(slot).expect(slot)..];
            let ctype = &s[s.find("\"casting_type\"").unwrap()..][..40];
            assert!(ctype.contains("\"Targeting\""), "{slot} is not cast on a target in the copy: {ctype}");
        }
        for name in [FORM, E_CD, CE_CD] {
            assert!(copy.contains(&format!("\"{name}\"")), "{name} is not a buff in the copy");
        }
    }

    #[test]
    fn the_cocoon_takes_a_clear_line_held_first_then_the_nearest() {
        let p = Params::default();
        let me = (0.0, 0.0);
        let near = champ(1, (30_000.0, 0.0), 1000, 1000);
        let wave = minion(9, (15_000.0, 1_000.0)); // in front of `near`
        let far = champ(2, (0.0, 60_000.0), 1000, 1000);
        let out = champ(3, (80_000.0, 0.0), 10, 1000); // out of reach
        assert_eq!(cocoon_pick(me, &[near, wave, far, out], &p).map(|(u, w)| (u.id, w)), Some((2, Why::Clear)));
        assert_eq!(cocoon_pick(me, &[near, far, out], &p).map(|(u, w)| (u.id, w)), Some((1, Why::Clear)));
        let held = Unit { cc: true, ..far };
        assert_eq!(cocoon_pick(me, &[near, held], &p).map(|(u, w)| (u.id, w)), Some((2, Why::HeldClear)));
        // both behind minions: the nearest anyway
        let wave2 = minion(8, (0.0, 30_000.0));
        assert_eq!(cocoon_pick(me, &[near, wave, far, wave2], &p).map(|(u, w)| (u.id, w)), Some((1, Why::Blocked)));
        // a minion beside the line (not on it) does not block
        let aside = minion(7, (15_000.0, 15_000.0));
        assert_eq!(cocoon_pick(me, &[near, aside], &p).map(|(u, w)| (u.id, w)), Some((1, Why::Clear)));
        assert_eq!(cocoon_pick(me, &[out, wave], &p), None);
    }

    #[test]
    fn rappel_drops_on_the_lowest_and_the_hunt_on_the_held() {
        let p = Params::default();
        let me = (0.0, 0.0);
        let full = champ(1, (20_000.0, 0.0), 1500, 1500);
        let low = champ(2, (40_000.0, 0.0), 300, 1500); // 20%
        let lower_far = champ(3, (60_000.0, 0.0), 100, 1500); // out of Rappel's 50000
        assert_eq!(rappel_pick(me, &[full, low, lower_far], &p).map(|(u, w)| (u.id, w)), Some((2, Why::Lowest)));
        assert_eq!(hunt_pick(me, &[full, low, lower_far], &p).map(|(u, w)| (u.id, w)), Some((3, Why::Lowest)));
        let held = Unit { cc: true, ..full };
        assert_eq!(hunt_pick(me, &[held, low, lower_far], &p).map(|(u, w)| (u.id, w)), Some((1, Why::Held)));
        assert_eq!(rappel_pick(me, &[minion(9, (10_000.0, 0.0))], &p), None);
    }

    // ---- 0.2.0: the spiderlings as units ----

    #[test]
    fn the_spiderlings_are_built_from_her_numbers() {
        let hers = StatV1 { attack: 120, magic_power: 90, hp: 1500, defence: 40, magic_resistance: 30, move_speed: 1100, hp_regen: 3,
                            stack: 0, crit_chance: 0 };
        let s = spiderling_spec(&hers, 2000);
        assert_eq!((s.name.as_str(), s.life), ("league_elise_spiderling", SL_LIFE));
        assert_eq!(s.stat, StatV1 { attack: 90, magic_power: 90, hp: 280, defence: 40, magic_resistance: 51, move_speed: 1166,
                                    hp_regen: 0, stack: 0, crit_chance: 0 });
        // a bite: 12 + 10 % of her 90 ability power = 21, once each of her attacks
        let a = s.attack;
        assert_eq!(a.attack + s.stat.attack * a.attack_ratio / 100, 21);
        assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (18_400, 52, 24, 8));
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        assert_eq!(spiderling_spec(&StatV1::default(), 0).stat.hp, 1);
        for name in [SL_UNIT, SL_FRENZY, &summon::handoff(SL_UID, usize::MAX)] {
            assert!(name.starts_with("league_elise_") && name.len() <= BUFF_NAME_CAP, "{name}");
        }
        // round her, the first toward the foe
        let p = spiderling_points((300_000.0, 300_000.0), Some((400_000.0, 300_000.0)), 3);
        assert_eq!(p.len(), 3);
        assert!((p[0].0 - 309_000.0).abs() < 1e-6 && (p[0].1 - 300_000.0).abs() < 1e-6);
        assert!(spiderling_points((1_000.0, 1_000.0), None, 2).iter().all(|q| q.0 >= 0.0 && q.1 >= 0.0));
    }

    #[test]
    fn the_over_line_says_the_bites_are_physical_unless_made_magic() {
        // game 0.7.2 never names a unit in on_attack: nothing may claim a conversion that did not run
        assert!(bites_text(0).starts_with("its bites physical") && !bites_text(0).contains("dealt as magic"));
        assert_eq!(bites_text(2), "2 of its bites dealt as magic (on_attack named it)");
    }

    #[test]
    fn the_copy_leaves_the_riding_bites_behind_sl_unit() {
        let copy = include_str!("../override/league_elise.data_champion");
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{SL_UNIT}\"")).count(), 1);
        for f in SL_FLAGS.iter().chain([&CW_ON]) {
            assert!(copy.contains(&format!("\"{f}\"")), "{f}");
        }
    }

    // ---- 0.2.1: Neurotoxin by current health, Venomous Bite by missing health ----

    #[test]
    fn neurotoxin_and_venomous_bite_take_leagues_shares_of_health() {
        // League's base shares: 4 % of the current health, 8 % of the missing health
        assert_eq!((Q_CUR, CQ_MISS), (4, 8));
        assert_eq!(venom_damage(Venom::Neuro, 2000, 2000, false, 200), 80);
        assert_eq!(venom_damage(Venom::Neuro, 1000, 2000, false, 200), 40);
        assert_eq!(venom_damage(Venom::Neuro, 3000, 2000, false, 0), 80, "never more than its maximum");
        assert_eq!(venom_damage(Venom::Bite, 2000, 2000, false, 200), 0, "a healthy target: nothing by missing health");
        assert_eq!(venom_damage(Venom::Bite, 500, 2000, false, 200), 120);
        assert_eq!(venom_damage(Venom::Bite, 3000, 2000, false, 200), 0);
        // monsters: the share capped at 75 + 90 % of her ability power (League: 65-145 + 90 %)
        assert_eq!(venom_damage(Venom::Neuro, 10_000, 10_000, true, 100), 165);
        assert_eq!(venom_damage(Venom::Bite, 5_000, 10_000, true, 100), 165);
        assert_eq!(venom_damage(Venom::Bite, 9_000, 10_000, true, 100), 80, "under the cap: the share itself");
        // at the main pack's old 3 % / 5 % of the maximum as true damage the bite was bigger on a healthy target, the
        // bolt about the same on one (4 % magic of the current health ~ 3 % true at 33 magic resistance)
        assert!(venom_damage(Venom::Neuro, 2000, 2000, false, 0) * 100 / 133 <= 2000 * 3 / 100);
    }

    #[test]
    fn the_copy_has_the_natives_where_the_true_damage_was() {
        let copy = include_str!("../override/league_elise.data_champion").replace('\r', "");
        let main = include_str!("../../../league/champion/league_elise.data_champion").replace('\r', "");
        assert_eq!(copy.matches("\"effect_ref\": \"league_elise:neuro\"").count(), 1, "Neurotoxin's bolt");
        assert_eq!(copy.matches("\"effect_ref\": \"league_elise:bite\"").count(), 2, "Venomous Bite and the hunt's bite");
        assert!(!main.contains("league_elise:neuro") && !main.contains("league_elise:bite"));
        // the main pack's % max health true damage (q_hp 3, cq_hp 5): in the main pack, gone from the copy
        for pct in [3, 5] {
            let ratio = format!("\"target_hp_ratio\": {pct}\n");
            assert!(main.contains(&ratio), "{pct}");
            assert!(!copy.contains(&ratio), "{pct}: the copy still deals the main pack's share");
        }
    }

    use super::mock::{champion, unit, MPlayer, World};

    const GAREN: usize = 1;

    #[test]
    fn the_natives_deal_the_share_to_the_unit_hit() {
        let (mut w, _) = world();
        // the bolt's hit on Garen (50000 health, all of it): 4 % of it, magic, from her
        w.sim(|sim| VenomFx(Venom::Neuro).apply(sim, 0, 0, InputTargetV1::target(GAREN)));
        assert_eq!(w.dealt(0, DamageTypeV1::Ap), vec![(GAREN, 2000)]);
        assert_eq!(w.units[GAREN].hp, 48_000);
        // the bite on him: 8 % of the 2000 he has lost
        w.sim(|sim| VenomFx(Venom::Bite).apply(sim, 0, 0, InputTargetV1::target(GAREN)));
        assert_eq!(w.dealt(0, DamageTypeV1::Ap)[1], (GAREN, 160));
        // a spot for input: the nearest enemy close to her, none too far
        w.sim(|sim| VenomFx(Venom::Bite).apply(sim, 0, 0, InputTargetV1::pos(300_000, 300_000)));
        assert_eq!(w.dealt(0, DamageTypeV1::Ap).len(), 2, "Garen 30000 away was bitten");
        w.units[GAREN].x = 310_000.0;
        w.sim(|sim| VenomFx(Venom::Bite).apply(sim, 0, 0, InputTargetV1::pos(300_000, 300_000)));
        assert_eq!(w.dealt(0, DamageTypeV1::Ap)[2], (GAREN, (50_000 - 47_840) * 8 / 100));
        // a monster: capped at 75 + 90 % of her 90 ability power
        w.units.push(unit("rhino_monster", EntityKindV1::Jungle, 2, 305_000.0, 300_000.0, 20_000));
        let camp = w.units.len() - 1;
        w.sim(|sim| VenomFx(Venom::Neuro).apply(sim, 0, 0, InputTargetV1::target(camp)));
        assert_eq!(w.dealt(0, DamageTypeV1::Ap).last(), Some(&(camp, 75 + 81)));
        // an ally or a dead unit: nothing
        let n = w.damage.len();
        w.sim(|sim| VenomFx(Venom::Neuro).apply(sim, 0, 0, InputTargetV1::target(3)));
        w.units[GAREN].hp = 0;
        w.units[GAREN].died = Some(w.tick);
        w.sim(|sim| VenomFx(Venom::Neuro).apply(sim, 0, 0, InputTargetV1::target(GAREN)));
        assert_eq!(w.damage.len(), n);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        for what in ["Q NEURO #", "on league_garen#1: hp 50000/50000 - 4% of its current health: 2000 magic",
                     "Q BITE #", "on league_garen#1: hp 48000/50000 - 8% of its missing health: 160 magic",
                     " (no unit in the effect's input: the nearest enemy to her)",
                     "on rhino_monster#4: hp 20000/20000 - 4% of its current health: 156 magic (capped against a monster: 75 + 90% \
                      of her 90 ability power)",
                     "no living enemy to hit"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }

    fn log_file() -> std::path::PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_elise_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_ELISE_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// Elise #0 (team 0, 90 ability power, 2000 health, two stored spiderlings) at (300000, 300000); Garen #1 30000 east of
    /// her; two more far off (the field round them all); a player each for the champions.
    fn world() -> (World, Queen) {
        log_file();
        let mut w = World::default();
        let mut elise = champion("league_elise", 0, 300_000.0, 300_000.0);
        (elise.hp, elise.max, elise.stat.magic_power) = (2000, 2000, 90);
        elise.buffs = vec![(BuffV1::named(SL_FLAGS[0]), usize::MAX), (BuffV1::named(SL_FLAGS[1]), usize::MAX)];
        let mut garen = champion("league_garen", 1, 330_000.0, 300_000.0);
        (garen.hp, garen.max) = (50_000, 50_000);
        w.units = vec![elise, garen, champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() }];
        let mut me = Queen::default();
        w.sim(|sim| me.on_spawn(sim, 0, 0));
        (w, me)
    }

    fn tick(w: &mut World, me: &mut Queen) {
        for (name, caster, input) in w.due() {
            w.sim(|sim| match name.as_str() {
                "league_elise:spiderling" => SpiderlingFx.apply(sim, 0, caster, input),
                other => panic!("an effect nobody registered: {other}"),
            });
        }
        if w.units[0].hp > 0 {
            w.sim(|sim| me.on_update(sim, 0, 0, 0));
        }
        w.step();
    }

    fn run(w: &mut World, me: &mut Queen, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    fn spider(w: &mut World, on: bool) {
        w.units[0].buffs.retain(|b| b.0.name() != FORM);
        if on {
            w.units[0].buffs.push((BuffV1::named(FORM), usize::MAX));
        }
    }

    fn lings(w: &World) -> Vec<usize> {
        w.spawns.iter().filter(|s| s.name == SPIDERLING).filter_map(|s| s.gave).collect()
    }

    #[test]
    fn spider_form_brings_her_stored_spiderlings_and_human_form_puts_them_away() {
        let (mut w, mut me) = world();
        run(&mut w, &mut me, 5);
        assert!(lings(&w).is_empty(), "human: no spiderling");
        spider(&mut w, true);
        run(&mut w, &mut me, 4);
        let ids = lings(&w);
        assert_eq!(ids.len(), 2, "one for each stored");
        assert!(w.spawns.iter().all(|s| s.life as usize == SL_LIFE && s.summoner == 0 && s.team == 0));
        assert!(w.has(0, SL_UNIT) && me.units);
        // they bite Garen: 12 + 10 % of 90
        run(&mut w, &mut me, 120);
        for id in &ids {
            let bites = w.dealt(*id, DamageTypeV1::Ad);
            assert!(!bites.is_empty() && bites.iter().all(|b| *b == (GAREN, 21)), "{bites:?}");
        }
        // one killed: one stored fewer, no new one
        w.hurt(ids[0], 1_000_000);
        run(&mut w, &mut me, 30);
        assert!(!w.has(0, SL_FLAGS[1]) && w.has(0, SL_FLAGS[0]));
        assert_eq!(lings(&w).len(), 2);
        assert!(w.has(0, SL_UNIT));
        // a new hit stores one more in Spider Form: it comes at once
        w.units[0].buffs.push((BuffV1::named(SL_FLAGS[1]), usize::MAX));
        run(&mut w, &mut me, 4);
        assert_eq!(lings(&w).len(), 3);
        // Human Form: banished until their time, the flag off
        spider(&mut w, false);
        run(&mut w, &mut me, 2);
        assert_eq!(w.banishes.len(), 2);
        assert!(w.banishes.iter().all(|b| b.1 == 0 && b.3 > SL_LIFE - 200));
        assert!(!w.has(0, SL_UNIT) && !me.units && me.lings.is_empty());
        // the spider again: fresh ones (League pulls them out healed)
        spider(&mut w, true);
        run(&mut w, &mut me, 4);
        assert_eq!(lings(&w).len(), 5);
    }

    #[test]
    fn a_timed_out_spiderling_is_replaced_while_she_is_the_spider() {
        let (mut w, mut me) = world();
        spider(&mut w, true);
        run(&mut w, &mut me, SL_LIFE + 10);
        assert_eq!(lings(&w).len(), 4, "two, then two more at their time");
        assert!(w.has(0, SL_FLAGS[1]), "a time-out costs no stored spiderling");
        assert!(w.has(0, SL_UNIT));
    }

    #[test]
    fn they_die_with_her() {
        let (mut w, mut me) = world();
        spider(&mut w, true);
        run(&mut w, &mut me, 10);
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.on_dead(sim, 0));
        assert_eq!(w.banishes.len(), 2);
        assert!(me.lings.is_empty() && !me.units);
        let before = w.damage.len();
        run(&mut w, &mut me, 100);
        assert_eq!(w.damage.len(), before, "banished: they do nothing");
    }

    #[test]
    fn no_unit_from_the_host_keeps_the_riding_bites() {
        for case in 0..3 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                _ => w.spawn_never = true,
            }
            spider(&mut w, true);
            run(&mut w, &mut me, 20);
            assert!(!w.has(0, SL_UNIT) && !me.units, "case {case}: SL_UNIT without spiderlings");
            let asked = w.spawns.len();
            run(&mut w, &mut me, 200);
            assert_eq!(w.spawns.len(), asked, "case {case}: asked again in the same Spider Form");
        }
    }

    #[test]
    fn the_frenzy_and_rappel_take_them_along() {
        let (mut w, mut me) = world();
        spider(&mut w, true);
        run(&mut w, &mut me, 5);
        let ids = lings(&w);
        w.units[0].buffs.push((BuffV1::timed(CW_ON, 180), 180));
        run(&mut w, &mut me, 2);
        for id in &ids {
            let b = w.units[*id].buffs.iter().find(|b| b.0.name() == SL_FRENZY).map(|b| b.0.attack_speed_mult);
            assert_eq!(b, Some(50), "the frenzy on #{id}");
        }
        // Rappel: up out of reach, then down 80000 away
        w.units[0].targetable = false;
        run(&mut w, &mut me, 3);
        (w.units[0].x, w.units[0].targetable) = (380_000.0, true);
        run(&mut w, &mut me, 1);
        assert_eq!(w.moves.len(), 2);
        assert!(w.moves.iter().all(|m| ((m.2 .0 as f64) - 380_000.0).abs() <= SL_SPREAD + 1.0));
    }

    #[test]
    fn the_bites_the_engine_tells_of_are_dealt_as_magic() {
        let (mut w, mut me) = world();
        spider(&mut w, true);
        run(&mut w, &mut me, 5);
        let ids = lings(&w);
        let mut dealt = 21;
        w.sim(|sim| me.on_attack(sim, 0, ids[0], GAREN, &mut dealt));
        assert_eq!(dealt, 0);
        run(&mut w, &mut me, 1);
        assert_eq!(w.dealt(0, DamageTypeV1::Ap), vec![(GAREN, 21)]);
        let mut own = 55;
        w.sim(|sim| me.on_attack(sim, 0, 0, GAREN, &mut own));
        assert_eq!(own, 55);
    }

    #[test]
    fn the_log_tells_the_spiderlings_lives() {
        let (mut w, mut me) = world();
        spider(&mut w, true);
        run(&mut w, &mut me, 100);
        let ids = lings(&w);
        w.players[1].gold += 3;
        w.hurt(ids[1], 1_000_000);
        run(&mut w, &mut me, 10);
        spider(&mut w, false);
        run(&mut w, &mut me, 2);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" SPIDERLING")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "SPIDERLING ASK #", "Spider Form: her stored spiderlings: 2 at (", "(9000 round her)",
            "SPIDERLING SPAWN #", "(the queued effect): unit #4 for team 0 at (", "'league_elise_spiderling' for 900 ticks, attack 90 \
             ap 90 hp 280 def 20 mr 34 speed 1166; hits 12 + 10% of its attack, range 18400, every 52 ticks (24 long, lands at 8)",
            "SPIDERLING UNITS ON #", "SPIDERLING #1 LOOK #", "#4 reads back as name 'league_elise_spiderling'", " of 900 ticks, at (",
            "near it: champion #1 league_garen", "OVER #", "KILLED after ", "p1 gold +3", "one stored spiderling fewer: 1 left",
            "SPIDERLING BANISH #", "Human Form - her spiderlings are stored - #1 (unit #4, ", " banished",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
        assert!(mine.iter().map(|l| l.len()).max().unwrap() < 700);
    }

    #[test]
    fn only_the_cocoon_and_rappel_change_the_target() {
        assert_eq!(skill2_kind(false, false, false, true), Skill2::Cocoon);
        assert_eq!(skill2_kind(false, true, false, true), Skill2::Other); // the spiderling
        assert_eq!(skill2_kind(false, false, false, false), Skill2::Other); // no champion: the spiderling on the wave
        assert_eq!(skill2_kind(true, false, false, true), Skill2::Rappel);
        assert_eq!(skill2_kind(true, false, true, true), Skill2::Other); // frenzy
        assert_eq!(skill2_kind(true, true, false, true), Skill2::Rappel); // the human cooldown does not matter
    }
}
