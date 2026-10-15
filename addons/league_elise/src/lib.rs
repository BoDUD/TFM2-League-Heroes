//! 伊莉丝附加包（用户 2026-10-15：「附加包要」——整身变蜘蛛 + 挑目标）。主包保持纯数据；`mod.override_info` 把主包的伊莉丝换成
//! `override/` 里的副本（`make_override.py` 用 tools/kit/build_elise.py 的 `native=1` 生成：加上本包的被动 `league_elise:queen`，
//! 技能2和大招改成对目标施放——结茧、盘丝、茧缚猎杀打向 AI 给的目标，不再是射程内随机一个英雄；技能2、大招的说明开头加【附加包】），
//! 本包补数据做不到的事：
//!
//! - **整身变蜘蛛**（`view.rs`，只在游戏 0.6.4 上）：蜘蛛形态（主包的永久 buff `league_elise_sp`）时站着、跑着、挨打、阵亡也是
//!   蜘蛛（`c_idle` / `c_run` / `c_hit` / `c_dead`，奈德丽附加包的做法）。
//! - **结茧挑目标**（AI 钩子 `league_elise:aim`，人形、结茧好了、射程 `e_range` 内有敌方英雄时）：茧碰到第一个单位就停，所以挑
//!   **线上没有小兵、野怪、别的英雄挡着**的英雄：被控住的先（必中），再挑最近的（飞得短、最难躲开）；都被挡着就挑最近的英雄
//!   （和主包一样碰运气）。
//! - **盘丝挑目标**（同一个钩子，蜘蛛形态、盘丝好了、`ce_r` 内有敌方英雄时）：落到**生命比例最低**的英雄身上（一样低就近的）。
//! - **茧缚猎杀挑目标**（大招）：`r_range` 内**被控住的**英雄先（生命比例最低的），没有就挑生命比例最低的。
//!   别的时候（自爆蜘蛛、掠行狂暴）不换 AI 的目标。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_elise.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `FORM`（显示里变蜘蛛 / 变人、模拟里蜘蛛形态 buff 上下）、`COCOON` / `RAPPEL` / `HUNT`（挑了谁、为什么），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_elise";
const HERO: &str = "league_elise";
const VERSION: &str = env!("CARGO_PKG_VERSION");
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

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
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

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

// ===================== 被动：蜘蛛女皇（参数 + 模拟里的形态日志） =====================

#[derive(Clone, Default)]
struct Queen {
    /// 上一 tick 身上有没有蜘蛛形态 buff（None = 这条命还没看过）。
    spider: Option<bool>,
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
        self.spider = None;
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN {} (the add-on's Elise) #{k}", head(sim, entity), who(sim, entity)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let sp = has_buff(sim, me, FORM);
        if self.spider.is_some_and(|was| was != sp) {
            if let Some(k) = counted("form_sim") {
                let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
                wlog(format!("{} FORM sim: {}{} #{k}", head(sim, me), if sp { "SPIDER on" } else { "spider off (human)" },
                    if alive { "" } else { ", dead" }));
            }
        }
        self.spider = Some(sp);
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
        let (pick, line) = {
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
                                  champion: u.is_champion(), cc: u.cc_count() > 0 });
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
            (u, line)
        };
        if pick.id == current {
            if let Some(k) = counted("aim") {
                wlog(format!("{line} kept #{k}"));
            }
            return None;
        }
        let input = InputV1::action(kind, InputTargetV1::target(pick.id));
        if !ctx.is_valid_input(&input) {
            if let Some(k) = counted("aim") {
                wlog(format!("{line} refused by the game, the AI's target kept #{k}"));
            }
            return None;
        }
        if let Some(k) = counted("aim") {
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
        "=== {ID} v{VERSION} (Elise: the whole-body spider, the Cocoon's, Rappel's and the hunt's targets) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:queen"), Queen::default());
    module.add_player_input_ai(AimAi);
    host.log(LogLevel::Info, "league_elise loaded (whole-body spider, Cocoon / Rappel / hunt targets).");
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
