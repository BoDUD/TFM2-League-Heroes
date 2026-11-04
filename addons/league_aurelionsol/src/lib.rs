//! 奥瑞利安·索尔附加包：「星海焕然」的星尘死后不掉；「星芒凝汇」黑洞中心按真实生命处决；「星穹流丽」（W）是他自己的技能，
//! 边飞边喷龙息。
//!
//! 主包保持纯数据：引擎在他死亡时清掉身上全部 buff，所以星尘（`league_aurelionsol_d1`…`d30`，每层一个名字，前 15 层各带
//! 法强，每 5 层大招和黑洞大一档）
//! 每条命从零叠起；数据读不到生命，黑洞中心只能每秒打英雄最大生命的 `e_exec`%（处决的替身）；TFM2 只有三个技能格，W 只能
//! 并进被动（击杀后起飞），喷龙息时站着不动。
//! `mod.override_info` 把主包的奥瑞利安·索尔换成 `override/` 里的副本（tools/kit/build_aurelionsol.py --native）：黑洞中心
//! 每次打到英雄时多跑一个原生效果 `league_aurelionsol:core`，击杀不再让数据起飞（只挂 `w_td` 告诉本包），`passive` 换成本包的
//! `league_aurelionsol:stardust`：
//!
//! - 活着时把身上每一层 `league_aurelionsol_d<n>` 原样记下来；少了（死亡清掉的）就原样补回（卑尔维斯附加包的做法）。层数
//!   只会变多（主包从不去掉一层），所以「身上比记下的少」只会是死亡清掉的。最多 `d_max` 层。天瀑的充能（`c1`…）不记：
//!   放天瀑时主包自己会清掉它们。
//! - 黑洞中心打到一个英雄：它的生命低于最大生命的 `e_low`% + 每层星尘 `e_low_d`%（英雄联盟：星尘越多处决线越高；只算前
//!   `e_low_n` 层，星尘上限提到 30 层后处决线仍最多 20%）就直接处决（真实伤害 = 生命 + 护盾 + 1，梅尔附加包的做法）。
//! - **星穹流丽**（用户 2026-11-04：「龙王是不是不能边飞行边放Q 和英雄联盟也不太一样？」；英雄联盟 V26.21 的 W）：被动每
//!   [`flight::EVERY`] tick 看一次局面，W 好了（开局 `w_start` 以后；冷却 1 级 `w_cd1`，匀着降到 12 级的 `w_cd12`）就按 [`flight::plan`]
//!   起飞——残血逃生、追龙息够不着的残血、飞进队友已经在打的团。起飞重置龙息的冷却（去掉主包的 `q_cd`），挂 `w_fly`
//!   （无视地形；主包副本里飞行中的龙息没有冷却、引导 `q_t_f`、伤害 `q_fdmg`%，`w_trail` 的星尘拖尾）和起飞的星云
//!   `w_up`，之后逐 tick 把他沿直线挪过去（`entity_set_pos`，凯莉丝塔跳的做法）：每 tick `w_v`，喷龙息（身上有主包的
//!   `q_ch`）时减半——边飞边喷，龙息的姿势一路跟着飞；硬控、被放逐、死亡就落地。落点在墙里就飞出墙（[`flight::landing`]）。
//!   AI 钩子 [`flight_ai`] 在飞行中替 AI 对够得着的敌方英雄按龙息（逃生时只喷残血的追兵），走路和普攻改成朝落点飞。
//!   主包副本的击杀检查挂 `w_td`：剩下的冷却返还 `w_refund`%（英雄联盟 90%）。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份；原生效果读不到参数，被动出生
//! 时按（这局的种子, 单位）记一份给它。被动自己的状态（W 的冷却、这一次飞行）在被动自己身上（每局一份）；AI 钩子读的是他身上
//! 的 buff（`w_fly`、落点 `w_to:<x>,<y>`、目标 `w_at:<id>`、`w_esc`），服务器并排跑的两份预演互不相干。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aurelionsol.log`，每次启动游戏重写：`FLY`（为什么飞、
//! 从哪到哪、龙息重置了没有）、`BREATH`（飞行中开始喷）、`FLY AI`（钩子按的龙息）、`LAND`（飞了多久多远、喷了几 tick、
//! 喷着飞了多远、怎么落地的）、`REFUND`（击杀返还），都限了条数（你看的那场每一行都记）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod flight;
pub mod flight_ai;

use flight::{along, dist, Pt, Why};

const ID: &str = "league_aurelionsol";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_aurelionsol") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// A stardust stack's name: this and its number (build_aurelionsol.py: `d1` .. `d<d_max>`).
const STACK: &str = "league_aurelionsol_d";
/// 飞行（本包挂的；主包副本的龙息读它：没有冷却、引导更久、伤害更高；画面是 `w_trail` 的星尘拖尾）。
pub const W_FLY: &str = "league_aurelionsol_w_fly";
/// 起飞的星云（buff 画面 `w_lift`，四帧 0.4 秒）。
pub const W_UP: &str = "league_aurelionsol_w_up";
pub const W_UP_T: usize = 24;
/// 主包副本的击杀检查挂的：一次击杀，返还冷却。
pub const W_TD: &str = "league_aurelionsol_w_td";
/// 给 AI 钩子的：落点（`w_to:<x>,<y>`）、飞向谁（`w_at:<id>`）、这是逃生。
pub const W_TO: &str = "league_aurelionsol_w_to:";
pub const W_AT: &str = "league_aurelionsol_w_at:";
pub const W_ESC: &str = "league_aurelionsol_w_esc";
/// 主包的龙息：冷却、引导中、两条 AddCasted 还在（这期间不会再喷一次）。
pub const Q_CD: &str = "league_aurelionsol_q_cd";
pub const Q_CH: &str = "league_aurelionsol_q_ch";
pub const Q_LIVE: &str = "league_aurelionsol_q_live";
/// 主包的台词间隔（build_aurelionsol.P 的 vo_gap）和它的标记。
pub const VO_CD: &str = "league_aurelionsol_vo_cd";
pub const VO_GAP: usize = 600;
/// 起飞的音效和台词（主包的 sound_info）。
pub const SFX_W: &str = "league_aurelionsol_w";
pub const SFX_VO_W: &str = "league_aurelionsol_vo_w";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AURELIONSOL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_aurelionsol.log");
        }
    }
    PathBuf::from("league_aurelionsol.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

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

/// A unit's name and entity number for the log.
fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

fn pt(p: Pt) -> String {
    format!("({:.0}, {:.0})", p.0, p.1)
}

/// The first `n` of each kind of line are logged, then every 100th (a long game repeats the same event); every one of the
/// match on screen (`shown`: 2026-11-02, a watched set kept 2 lines, the presims had used the count up).
fn counted(kind: &str, shown: bool) -> Option<usize> {
    static COUNTS: LazyLock<Mutex<HashMap<String, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let k = c.entry(kind.to_string()).or_insert(0);
    *k += 1;
    (shown || *k <= 40 || *k % 100 == 0).then_some(*k)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Params {
    /// 星尘最多几层。
    pub d_max: usize,
    /// 黑洞中心的处决线：最大生命的这个百分比……
    pub e_low: usize,
    /// ……每层星尘再加这么多……
    pub e_low_d: usize,
    /// ……只算前这么多层。
    pub e_low_n: usize,
    /// 龙息够多远（AI 钩子挑飞行中喷谁）。
    pub q_range: usize,
    /// 龙息在地面上最长引导多久、冷却多久（飞行中开始的那口落地后照地面的上限收，收完进冷却，英雄联盟的规矩）。
    pub q_t: usize,
    pub q_cd: usize,
    /// 星穹流丽的冷却：1 级这么多 tick，匀着降到 12 级的这么多。
    pub w_cd1: usize,
    pub w_cd12: usize,
    /// 飞多远：这么多，每层星尘再多这么多。
    pub w_len: usize,
    pub w_len_d: usize,
    /// 每 tick 飞多远（喷龙息时减半）。
    pub w_v: usize,
    /// 开局这么多 tick 以后才能飞。
    pub w_start: usize,
    /// 击杀返还剩下冷却的这个百分比。
    pub w_refund: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            d_max: 30,
            e_low: 5,
            e_low_d: 1,
            e_low_n: 15,
            q_range: 75000,
            q_t: 90,
            q_cd: 300,
            w_cd1: 1320,
            w_cd12: 840,
            w_len: 150000,
            w_len_d: 750,
            w_v: 2000,
            w_start: 900,
            w_refund: 90,
        }
    }
}

/// `{"d_max":30,"e_low":5,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "d_max" => &mut p.d_max,
            "e_low" => &mut p.e_low,
            "e_low_d" => &mut p.e_low_d,
            "e_low_n" => &mut p.e_low_n,
            "q_range" => &mut p.q_range,
            "q_t" => &mut p.q_t,
            "q_cd" => &mut p.q_cd,
            "w_cd1" => &mut p.w_cd1,
            "w_cd12" => &mut p.w_cd12,
            "w_len" => &mut p.w_len,
            "w_len_d" => &mut p.w_len_d,
            "w_v" => &mut p.w_v,
            "w_start" => &mut p.w_start,
            "w_refund" => &mut p.w_refund,
            _ => continue,
        };
        *slot = v;
    }
    p
}

/// Each Aurelion Sol's numbers by (the game's seed, his unit), for the core's native effect (it gets none of its own).
static PARAMS: LazyLock<Mutex<HashMap<(u64, usize), Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim.seed(), me)).copied().unwrap_or_default()
}

// ===================== 计算 =====================

/// The stack number of a buff name (`league_aurelionsol_d3` -> 3), within d_max.
pub fn stack_of(name: &str, d_max: usize) -> Option<usize> {
    let n: usize = name.strip_prefix(STACK)?.parse().ok()?;
    (1..=d_max).contains(&n).then_some(n)
}

/// The execute line in percent of maximum health with this much stardust (its first e_low_n stacks count).
pub fn execute_line(p: &Params, stacks: usize) -> usize {
    p.e_low + p.e_low_d * stacks.min(p.d_max).min(p.e_low_n)
}

/// The execute's fixed damage: his health + shield + maximum health (it lands next tick: through this tick's heal or
/// shield, league_locke's and league_pyke's way), scaled up by his damage reduction (league_mel's executes left 5 of 48
/// alive at `hp + shield + 1`, 2026-11-02). A 100% reduction (Master Yi's Alpha Strike): None, no execute this time.
pub fn execute_damage(hp: usize, shield: usize, max: usize, reduce: usize) -> Option<usize> {
    (reduce < 100).then(|| (hp + shield + max) * 100 / (100 - reduce))
}

/// A unit's damage reduction in % (damage taken and skill damage taken, up to 100).
pub fn reduction(e: &StableEntity<'_, '_>) -> usize {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.damaged_reduce + b.skill_damaged_reduce).sum::<usize>().min(100)
}

/// Is a champion with this health under the line (a unit with no maximum never is).
pub fn executes(p: &Params, stacks: usize, hp: usize, max: usize) -> bool {
    max > 0 && hp > 0 && hp * 100 < execute_line(p, stacks) * max
}

/// The stacks kept that are not on him now (a death cleared them).
fn missing(kept: &[BuffV1], have: &[BuffV1]) -> Vec<BuffV1> {
    kept.iter().filter(|k| !have.iter().any(|h| h.name() == k.name())).cloned().collect()
}

fn stacks_on(sim: &StableSim<'_>, me: usize, d_max: usize) -> Vec<BuffV1> {
    sim.get_entity(me).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| stack_of(b.name(), d_max).is_some()).collect()
    })
}

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| has(&e, name))
}

fn pos_of(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn hp_of(e: &StableEntity<'_, '_>) -> f64 {
    let (h, m) = e.hp();
    h as f64 / m.max(1) as f64
}

/// 让飞行停下、也不让起飞的控制：击飞、晕眩、定身、嘲讽、恐惧、魅惑、被强制位移、禁止位移技能（波比的 W）。
/// 施法动作（`Animation`：他自己的龙息、黑洞、大招）不算。
const GROUNDED: [CcKindV1; 8] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                                 CcKindV1::Charm, CcKindV1::ForceMove, CcKindV1::BlockMoveSkill];

pub fn grounds(kind: u32) -> bool {
    GROUNDED.iter().any(|k| k.code() == kind)
}

fn grounded(e: &StableEntity<'_, '_>) -> bool {
    !e.is_targetable() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| grounds(c.kind)))
}

// ===================== 原生效果：黑洞中心 =====================

/// The core struck a champion: under the line, it dies.
fn core(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let t = input.target_id;
    let p = params_of(sim, me);
    let stacks = stacks_on(sim, me, p.d_max).len();
    let Some(u) = sim.get_entity(t) else { return };
    if !u.is_alive() || !u.is_champion() {
        return;
    }
    let (hp, max) = u.hp();
    let shield = u.shield();
    let name = u.name().unwrap_or_default();
    let reduce = reduction(&u);
    if !executes(&p, stacks, hp, max) {
        return;
    }
    let Some(dmg) = execute_damage(hp, shield, max, reduce) else {
        if let Some(k) = counted("execute held", on_screen(sim)) {
            wlog(format!("{} EXECUTE HELD #{k}: {name} #{t} takes no damage now (reduced {reduce}%)", head(sim, me)));
        }
        return;
    };
    sim.deal_damage_typed(me, t, dmg, DamageTypeV1::Fixed, AttackTypeV1::Skill);
    if let Some(k) = counted("execute", on_screen(sim)) {
        wlog(format!("{} EXECUTE #{k}: {name} #{t} at {hp}/{max} ({}%) under {}% ({stacks} stardust), dealt {dmg} (reduced {reduce}%)",
                     head(sim, me), hp * 100 / max.max(1), execute_line(&p, stacks)));
    }
}

struct CoreFx;
impl StableEffectType for CoreFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        core(sim, caster, input);
    }
}

// ===================== 星穹流丽：起飞、飞、落地 =====================

/// 游戏的三张内置地图的墙（每次看局面时按单位的位置挑当前这张）。
static GRIDS: LazyLock<Vec<flight::Grid>> = LazyLock::new(flight::Grid::builtin);

/// 这一次飞行。
#[derive(Clone, Debug)]
struct Flight {
    why: Why,
    /// 飞向的那个（他倒下以后没有）。
    aim: Option<usize>,
    from: Pt,
    dir: Pt,
    len: f64,
    /// 已经飞了多远、几 tick。
    went: f64,
    ticks: usize,
    /// 飞行中开始喷了几次龙息、喷着飞了几 tick、多远；上一 tick 在不在喷。
    breaths: usize,
    breath_ticks: usize,
    breath_went: f64,
    was_breathing: bool,
    /// 游戏没让挪的 tick 数。
    refused: usize,
    /// 飞向的那个在龙息里倒下了几次（0 或 1）。
    fell: usize,
    /// 这一口龙息（多半）是喷他的：开始喷时他活着、在龙息够得着的地方。
    on_aim: bool,
}

/// 他看到的局面（`flight::Scene`）：看得见、选得中的敌方英雄，活着的队友英雄，两边活着的塔。
fn scene(sim: &StableSim<'_>, me: usize) -> Option<flight::Scene> {
    let e = sim.get_entity(me)?;
    let team = e.team();
    let mut s = flight::Scene { me: pos_of(&e), hp: hp_of(&e), ..flight::Scene::default() };
    for u in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
        if !u.is_alive() || u.id() == me {
            continue;
        }
        if u.is_champion() {
            let c = flight::Champ { id: u.id(), at: pos_of(&u), hp: hp_of(&u) };
            if u.team() == team {
                s.allies.push(c);
            } else if u.is_targetable() && sim.is_visible(team, u.id()) {
                s.foes.push(c);
            }
        } else if u.is_tower() {
            if u.team() == team { s.ally_towers.push(pos_of(&u)) } else { s.enemy_towers.push(pos_of(&u)) }
        }
    }
    Some(s)
}

/// 当前对局的墙：站进墙里的活着的单位最少的那张图。
fn grid_now(sim: &StableSim<'_>) -> &'static flight::Grid {
    let points: Vec<Pt> =
        (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).filter(|u| u.is_alive()).map(|u| pos_of(&u)).collect();
    &GRIDS[flight::current(&GRIDS, &points)]
}

/// 他身上名字以 `prefix` 开头的 buff 全去掉。
fn remove_prefixed(sim: &mut StableSim<'_>, me: usize, prefix: &str) {
    let names: Vec<String> = sim.get_entity(me).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).filter(|n| n.starts_with(prefix)).collect()
    });
    for n in names {
        sim.entity_remove_buff(me, &n);
    }
}

// ===================== 被动：星尘 + 星穹流丽 =====================

/// 每个奥瑞利安·索尔一份：参数、记下的星尘、上一 tick 是不是活着（只为日志）、W 什么时候好、这一次飞行。
#[derive(Clone, Default)]
struct Stardust {
    p: Params,
    kept: Vec<BuffV1>,
    was_alive: bool,
    /// 这个 tick 起 W 好了（冷却跨死亡照走，英雄联盟也是）。
    w_ready: usize,
    flight: Option<Flight>,
    /// 飞行中开始的、还在喷的那口龙息是哪个 tick 开始的（落地后照地面的上限 `q_t` 收）。
    fbreath: Option<usize>,
}

/// 飞行这一 tick 之后：接着飞，或者落地（为什么）。
enum Step {
    On,
    Land(&'static str),
}

impl Stardust {
    /// 主包副本的击杀检查挂了 `w_td`：剩下的冷却返还 `w_refund`%。
    fn refund(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if !has_buff(sim, me, W_TD) {
            return;
        }
        sim.entity_remove_buff(me, W_TD);
        let now = sim.tick();
        let left = self.w_ready.saturating_sub(now);
        let after = flight::refunded(left, self.p.w_refund);
        self.w_ready = now + after;
        if let Some(k) = counted("refund", on_screen(sim)) {
            wlog(format!("{} REFUND #{k}: a takedown, Astral Flight's cooldown {left} -> {after} ticks{}", head(sim, me),
                         if self.flight.is_some() { " (in flight)" } else { "" }));
        }
    }

    /// W 好了就看要不要飞（[`flight::plan`]），要就起飞。
    fn take_off(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        if now < self.p.w_start || now < self.w_ready {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        if grounded(&e) {
            return;
        }
        let level = e.level();
        let Some(s) = scene(sim, me) else { return };
        if s.foes.is_empty() {
            return;
        }
        let g = grid_now(sim);
        let dust = stacks_on(sim, me, self.p.d_max).len();
        let reach = flight::reach(self.p.w_len, self.p.w_len_d, dust);
        let Some(plan) = flight::plan(&s, reach, g) else { return };
        let land = along(s.me, plan.dir, plan.len);
        // the longest it can take (all of it breathing, at half speed) and a little more: the buffs end with the landing
        let most = (plan.len / flight::speed(self.p.w_v, true)).ceil() as usize + 30;
        let mut wing = BuffV1::timed(W_FLY, most);
        wing.ignore_wall = true;
        sim.entity_remove_buff(me, W_FLY);
        sim.add_buff(me, &wing);
        remove_prefixed(sim, me, W_TO);
        remove_prefixed(sim, me, W_AT);
        sim.add_buff(me, &BuffV1::timed(&flight::to_name(W_TO, land), most));
        if let Some(t) = plan.why.target() {
            sim.add_buff(me, &BuffV1::timed(&format!("{W_AT}{t}"), most));
        }
        sim.entity_remove_buff(me, W_ESC);
        if plan.why == Why::Escape {
            sim.add_buff(me, &BuffV1::timed(W_ESC, most));
        }
        sim.entity_remove_buff(me, W_UP);
        sim.add_buff(me, &BuffV1::timed(W_UP, W_UP_T));
        // League: Astral Flight resets Breath of Light's cooldown
        let q_reset = sim.entity_remove_buff(me, Q_CD) > 0;
        let on_me = InputTargetV1::target(me);
        sim.play_sfx(SFX_W, me, &on_me);
        if !has_buff(sim, me, VO_CD) {
            sim.add_buff(me, &BuffV1::timed(VO_CD, VO_GAP));
            sim.play_sfx(SFX_VO_W, me, &on_me);
        }
        let cd = flight::cooldown(self.p.w_cd1, self.p.w_cd12, level);
        self.w_ready = now + cd;
        self.flight = Some(Flight { why: plan.why, aim: plan.why.target(), from: s.me, dir: plan.dir, len: plan.len,
                                    went: 0.0, ticks: 0, breaths: 0, breath_ticks: 0, breath_went: 0.0,
                                    was_breathing: false, refused: 0, fell: 0, on_aim: false });
        if let Some(k) = counted("fly", on_screen(sim)) {
            let aim = plan.why.target().map_or_else(String::new, |t| {
                let d = sim.get_entity(t).map(|u| (dist(s.me, pos_of(&u)), hp_of(&u)));
                d.map_or_else(|| format!(" {}", who(sim, t)),
                              |(d, hp)| format!(" {} ({:.0}% hp, {d:.0} away)", who(sim, t), hp * 100.0))
            });
            let near = s.foes.iter().map(|f| dist(s.me, f.at)).fold(f64::INFINITY, f64::min);
            wlog(format!("{} FLY #{k}: {}{aim} from {} {:.0} to {}{}; his hp {:.0}%, nearest enemy champion {near:.0}; \
                          Breath of Light {}; {dust} stardust, level {level}, next flight in {cd} ticks",
                         head(sim, me), plan.why.word(), pt(s.me), plan.len, pt(land),
                         if g.crosses(s.me, land) { " over a wall" } else { "" }, s.hp * 100.0,
                         if q_reset { "reset (its cooldown was running)" } else { "ready already" }));
        }
    }

    /// 飞一 tick：沿直线挪 `w_v`（喷龙息时减半）。
    fn fly(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let shown = on_screen(sim);
        let Some(f) = self.flight.as_mut() else { return };
        let (cut, mut breathing, posed) = match sim.get_entity(me) {
            Some(e) => (grounded(&e), has(&e, Q_CH), (0..e.cc_count()).filter_map(|i| e.cc_at(i)).all(|c| {
                CcKindV1::from_code(c.kind) == Some(CcKindV1::Animation)
            })),
            None => (true, false, false),
        };
        // the one he flew at fell (the breath he burns him with goes with him: the AddCasted on him is gone): no more
        // breath on nobody - its channel ends, its pose too (the only crowd control on him), and he flies on at full
        // speed; the next breath waits for `q_live` (the old one's pulses, a tick after its channel)
        let fell = f.aim.filter(|t| sim.get_entity(*t).is_none_or(|u| !u.is_alive()));
        if let (true, Some(t)) = (breathing && !cut && f.on_aim, fell) {
            breathing = false;
            f.was_breathing = false;
            f.aim = None;
            f.fell += 1;
            self.fbreath = None;
            sim.entity_remove_buff(me, Q_CH);
            let freed = posed && sim.entity_clear_cc(me) > 0;
            remove_prefixed(sim, me, W_AT);
            if let Some(k) = counted("breath_cut", shown) {
                wlog(format!("{} BREATH CUT #{k}: #{t}, the one he flew at, fell - the breath ends{}, on at full speed",
                             head(sim, me), if freed { " with its pose" } else { "" }));
            }
        }
        let step = if cut {
            Step::Land("cut by crowd control")
        } else {
            if breathing && !f.was_breathing {
                f.breaths += 1;
                self.fbreath = Some(sim.tick());
                // breathing at the one he flies at (the hook's first pick when the breath reaches him)?
                let here = sim.get_entity(me).map(|e| pos_of(&e));
                f.on_aim = f.aim.and_then(|t| sim.get_entity(t)).zip(here).is_some_and(|(u, h)| {
                    u.is_alive() && dist(h, pos_of(&u)) <= self.p.q_range as f64 + flight_ai::BODIES
                });
                if let Some(k) = counted("breath", shown) {
                    wlog(format!("{} BREATH #{k}: breathing in flight, {} ticks and {:.0} into it ({:.0} to go), \
                                  on at {:.0} a tick", head(sim, me), f.ticks, f.went, f.len - f.went,
                                 flight::speed(self.p.w_v, true)));
                }
            }
            if !breathing && f.was_breathing {
                // it ended in flight (its own end, crowd control): no cooldown up here
                self.fbreath = None;
            }
            f.was_breathing = breathing;
            let v = flight::speed(self.p.w_v, breathing);
            f.went = (f.went + v).min(f.len);
            f.ticks += 1;
            if breathing {
                f.breath_ticks += 1;
                f.breath_went += v;
            }
            let at = along(f.from, f.dir, f.went);
            if !sim.entity_set_pos(me, at.0.max(0.0).round() as u64, at.1.max(0.0).round() as u64) {
                f.refused += 1;
            }
            if f.went >= f.len - 0.5 {
                Step::Land("arrived")
            } else if f.refused > 10 {
                Step::Land("the game would not move him")
            } else {
                Step::On
            }
        };
        if let Step::Land(how) = step {
            self.land(sim, me, how);
        }
    }

    /// 落地以后，飞行中开始的那口龙息：英雄联盟只在飞行中没有最长引导，落地后照地面的上限 `q_t`（从开始喷算）收——超了就停
    /// （去掉 `q_ch`；施法动作是他身上唯一的控制时一起清掉），喷完（或停了）龙息进冷却 `q_cd - q_t`（冷却从引导结束算起：
    /// 主包地面上的龙息出手时进 `q_cd`，引导 `q_t`）。飞行中喷完的不进冷却（[`Stardust::fly`] 清掉了记号）。
    fn after_flight(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(from) = self.fbreath else { return };
        let now = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let on = has(&e, Q_CH);
        let posed = (0..e.cc_count()).filter_map(|i| e.cc_at(i)).all(|c| CcKindV1::from_code(c.kind) == Some(CcKindV1::Animation));
        if on && now < from + self.p.q_t {
            return;
        }
        self.fbreath = None;
        let freed = on && {
            sim.entity_remove_buff(me, Q_CH);
            posed && sim.entity_clear_cc(me) > 0
        };
        let cd = self.p.q_cd.saturating_sub(self.p.q_t);
        sim.entity_remove_buff(me, Q_CD);
        sim.add_buff(me, &BuffV1::timed(Q_CD, cd));
        if let Some(k) = counted("breath_end", on_screen(sim)) {
            let how = match (on, freed) {
                (true, true) => "stopped (with its pose) at the ground's longest,",
                (true, false) => "stopped at the ground's longest,",
                _ => "ended after the landing,",
            };
            wlog(format!("{} BREATH END #{k}: the breath begun in flight {how} {} ticks after it began; Breath of Light's \
                          cooldown {cd} ticks", head(sim, me), now - from));
        }
    }

    /// 落地：去掉飞行的 buff，记一行。
    fn land(&mut self, sim: &mut StableSim<'_>, me: usize, how: &str) {
        let Some(f) = self.flight.take() else { return };
        sim.entity_remove_buff(me, W_FLY);
        sim.entity_remove_buff(me, W_ESC);
        remove_prefixed(sim, me, W_TO);
        remove_prefixed(sim, me, W_AT);
        if let Some(k) = counted("land", on_screen(sim)) {
            wlog(format!("{} LAND #{k}: {} flight {how} after {} ticks, {:.0} of {:.0} flown; breathing {} ticks ({} breaths), \
                          {:.0} flown while breathing{}{}", head(sim, me), f.why.word(), f.ticks, f.went, f.len, f.breath_ticks,
                         f.breaths, f.breath_went, if f.fell > 0 { ", the one he flew at fell" } else { "" },
                         if f.refused > 0 { format!(", {} steps refused", f.refused) } else { String::new() }));
        }
    }
}

impl StablePassive for Stardust {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert((sim.seed(), me), self.p);
        // a new body: no flight carries over (the cooldown does)
        self.flight = None;
        self.fbreath = None;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn", on_screen(sim)) {
            wlog(format!("{} SPAWN #{k}: the add-on's Aurelion Sol (player {player}, team {team}), {:?}", head(sim, me),
                         self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let alive = e.is_alive();
        if alive != self.was_alive {
            if let Some(k) = counted("life", on_screen(sim)) {
                wlog(format!("{} {} #{k} with {} stardust kept", head(sim, me), if alive { "ALIVE" } else { "DEAD" },
                             self.kept.len()));
            }
            self.was_alive = alive;
        }
        // the stardust: remember new stacks, put back the ones a death cleared
        let have = stacks_on(sim, me, self.p.d_max);
        let gone = missing(&self.kept, &have);
        if !gone.is_empty() {
            for b in &gone {
                sim.add_buff(me, b);
            }
            if let Some(k) = counted("keep", on_screen(sim)) {
                wlog(format!("{} KEEP #{k}: {} stardust put back ({}), {} in all", head(sim, me), gone.len(),
                             if alive { "alive" } else { "dead" }, self.kept.len()));
            }
        } else if alive && have.len() > self.kept.len() {
            if let Some(k) = counted("stack", on_screen(sim)) {
                wlog(format!("{} STACK #{k}: {} -> {}", head(sim, me), self.kept.len(), have.len()));
            }
            self.kept = have;
        }
        // Astral Flight
        if !alive {
            self.land(sim, me, "ended by his death");
            self.fbreath = None;
            return;
        }
        self.refund(sim, me);
        if self.flight.is_some() {
            self.fly(sim, me);
        } else {
            self.after_flight(sim, me);
            if sim.tick() % flight::EVERY == 0 {
                self.take_off(sim, me);
            }
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (stardust kept through death, Singularity's core executing by real health, Astral Flight as his own ability: he breathes as he flies) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:core"), CoreFx);
    module.add_native_passive(format!("{ID}:stardust"), Stardust::default());
    module.add_player_input_ai(flight_ai::FlightAi::default());
    host.log(LogLevel::Info, "league_aurelionsol v1 loaded (Aurelion Sol: stardust kept, the black hole's execute, Astral Flight).");
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
mod tests {
    use super::*;

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"d_max":12,"e_low":6,"e_low_d":2,"x":1}"#),
                   Params { d_max: 12, e_low: 6, e_low_d: 2, ..Params::default() });
        assert_eq!(parse_params(r#"{"d_max":30,"e_low":5,"e_low_d":1,"e_low_n":15}"#), Params::default());
        assert_eq!(parse_params(r#"{"w_cd1":600,"w_v":1500,"w_refund":50}"#),
                   Params { w_cd1: 600, w_v: 1500, w_refund: 50, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_copy_carries_the_flight() {
        let s = include_str!("../override/league_aurelionsol.data_champion");
        for (k, v) in [("q_range", 75000), ("w_cd1", 1320), ("w_len", 150000), ("w_v", 2000), ("w_refund", 90)] {
            assert!(s.contains(&format!("\"{k}\": {v}")), "the copy's passive params lack {k} {v}");
        }
        for name in [W_FLY, W_UP, W_TD, Q_CD, Q_CH, Q_LIVE, VO_CD] {
            assert!(s.contains(&format!("\"{name}\"")), "{name} is not in the copy");
        }
        // the copy's takedown only tells the add-on: no data flight with its own speed buff
        assert!(!s.contains("\"move_speed_mult\": 60"), "the copy still lifts him by data");
        let main = include_str!("../../../league/champion/league_aurelionsol.data_champion");
        assert!(main.contains(&format!("\"{W_FLY}\"")) && !main.contains(&format!("\"{W_TD}\"")));
        // the voice's gap is the data's (both read the same flag)
        let at = s.find(&format!("\"name\": \"{VO_CD}\"")).expect("the copy has no voice gap");
        let after: String = s[at..at + 400].chars().filter(|c| !c.is_whitespace()).collect();
        assert!(after.contains(&format!("\"tick\":{VO_GAP}")), "vo_gap is not {VO_GAP}: {after}");
    }

    #[test]
    fn the_flight_s_sounds_are_the_main_pack_s() {
        for s in [SFX_W, SFX_VO_W] {
            let path = format!("{}/../../league/sound/sfx/{s}.sound_info", env!("CARGO_MANIFEST_DIR"));
            assert!(std::path::Path::new(&path).is_file(), "{path} is missing");
        }
    }

    #[test]
    fn stacks_are_the_data_s_names() {
        assert_eq!(stack_of("league_aurelionsol_d1", 30), Some(1));
        assert_eq!(stack_of("league_aurelionsol_d30", 30), Some(30));
        assert_eq!(stack_of("league_aurelionsol_d31", 30), None);
        assert_eq!(stack_of("league_aurelionsol_d0", 30), None);
        assert_eq!(stack_of("league_aurelionsol_dg", 30), None);
        // the flight's buffs are no stardust
        assert_eq!(stack_of(&flight::to_name(W_TO, (1.0, 2.0)), 30), None);
    }

    #[test]
    fn only_hard_crowd_control_grounds_him() {
        for k in [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::ForceMove, CcKindV1::BlockMoveSkill] {
            assert!(grounds(k.code()));
        }
        // his own casts' poses and a disarm or silence leave him flying
        for k in [CcKindV1::Animation, CcKindV1::BlockAttack, CcKindV1::BlockSkill] {
            assert!(!grounds(k.code()));
        }
    }

    #[test]
    fn the_line_grows_with_stardust() {
        let p = Params::default();
        assert_eq!(execute_line(&p, 0), 5);
        assert_eq!(execute_line(&p, 15), 20);
        assert_eq!(execute_line(&p, 30), 20);
        assert_eq!(execute_line(&p, 40), 20);
        assert!(executes(&p, 0, 49, 1000));
        assert!(!executes(&p, 0, 50, 1000));
        assert!(executes(&p, 15, 199, 1000));
        assert!(!executes(&p, 15, 0, 1000));
        assert!(!executes(&p, 15, 10, 0));
        // through this tick's heal or shield and any damage reduction short of 100%
        assert_eq!(execute_damage(150, 0, 1000, 0), Some(1150));
        assert!(execute_damage(150, 0, 1000, 40).unwrap() * 60 / 100 > 150);
        assert_eq!(execute_damage(150, 0, 1000, 100), None);
    }

    #[test]
    fn a_death_s_cleared_stacks_come_back() {
        let kept = vec![BuffV1::timed("league_aurelionsol_d1", 1), BuffV1::timed("league_aurelionsol_d2", 1)];
        assert_eq!(missing(&kept, &[]).len(), 2);
        assert_eq!(missing(&kept, &kept[..1]).len(), 1);
        assert!(missing(&kept, &kept).is_empty());
    }
}
