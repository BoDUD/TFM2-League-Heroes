//! 奈德丽附加包（用户 2026-10-13：「要，整身变豹 + 智能」，被动「主包数据 + 附加包补草丛」）。主包保持纯数据；
//! `mod.override_info` 把主包的奈德丽换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_nidalee.py 的
//! `native=1` 生成：`passive` 换成本包的 `league_nidalee:prowl`，说明开头加【附加包】），本包补数据做不到的四件事：
//!
//! - **整身变豹**（`view.rs`，只在游戏 0.6.4 上）：美洲狮形态时站着、跑着、挨打、阵亡也是豹子（凯隐附加包的做法）。
//! - **草丛加速**（被动 `prowl`，英雄联盟的「寻觅」）：在草丛里、以及离开草丛后 `brush_t` tick 内移速 +`brush_ms`%；
//!   这期间 `near` 以内有看得见的敌方英雄时 +`brush_near_ms`%。草丛格子从地图读（`bush.rs`，同雷恩加尔附加包）。
//! - **标枪挑目标**（AI 钩子）：人形、标枪好了，AI 要放 Q 时，换成射程内**线上没有小兵野怪挡着**的敌方英雄：被捕猎的
//!   优先，再按飞得远（伤害高）、血少排；没有挡不住的英雄就不换。
//! - **猛扑猎杀挑目标**（AI 钩子）：大招扑向射程内被捕猎的、血量比例最低的敌方英雄。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nidalee.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod bush;
pub mod view;

const ID: &str = "league_nidalee";
const HERO: &str = "league_nidalee";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 美洲狮形态（主包数据的永久 buff）。
pub const FORM: &str = "league_nidalee_cg";
const HUMAN: &str = "league_nidalee_hu";
const Q_CD: &str = "league_nidalee_hq_cd";
const HUNTED: &str = "league_nidalee_hunted";
const BRUSH: &str = "league_nidalee_brush";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_NIDALEE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_nidalee.log");
        }
    }
    PathBuf::from("league_nidalee.log")
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

fn counted(kind: &'static str) -> Option<usize> {
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

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 草丛加速：基础 / 附近有敌方英雄时的移速百分比，离开草丛后还留多少 tick，多近算附近。
    pub brush_ms: usize,
    pub brush_near_ms: usize,
    pub brush_t: usize,
    pub near: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { brush_ms: 10, brush_near_ms: 30, brush_t: 120, near: 93000 }
    }
}

/// `{"brush_ms":10,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "brush_ms" => p.brush_ms = v,
            "brush_near_ms" => p.brush_near_ms = v,
            "brush_t" => p.brush_t = v,
            "near" => p.near = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 标枪：射程（主包 q_range）、宽（q_w + 两边身体）、飞多远算中段 / 远段（q_speed x q_t1 / q_t2）。
pub const Q_REACH: f64 = 85_000.0;
pub const Q_W: f64 = 2_500.0 + 6_000.0;
pub const Q_MID: f64 = 3_000.0 * 10.0;
pub const Q_FAR: f64 = 3_000.0 * 19.0;
/// 大招的射程（主包 r_range）。
pub const R_REACH: f64 = 65_000.0;

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

pub fn seg_dist(a: (f64, f64), b: (f64, f64), p: (f64, f64)) -> f64 {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len2 = dx * dx + dy * dy;
    if len2 <= 0.0 {
        return dist(a, p);
    }
    let t = (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / len2).clamp(0.0, 1.0);
    dist((a.0 + t * dx, a.1 + t * dy), p)
}

/// 一个敌方单位：id、位置、是不是英雄、被捕猎、血量比例（%）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: (f64, f64),
    pub champion: bool,
    pub hunted: bool,
    pub hp_pct: usize,
}

/// 标枪的倍率档（飞得越远越高）：0 近、1 中、2 远。
pub fn band(d: f64) -> usize {
    if d < Q_MID {
        0
    } else if d < Q_FAR {
        1
    } else {
        2
    }
}

/// 从 `me` 到 `to` 的线上，比 `to` 近的别的单位挡着吗（标枪碰到第一个单位就停）。
pub fn blocked(me: (f64, f64), to: &Foe, foes: &[Foe]) -> bool {
    let d = dist(me, to.at);
    foes.iter().any(|f| f.id != to.id && dist(me, f.at) < d && seg_dist(me, to.at, f.at) <= Q_W)
}

/// 标枪的目标：射程内、线上没被挡的敌方英雄，被捕猎的优先，再按倍率档高、血量比例低排。
pub fn javelin_pick(me: (f64, f64), foes: &[Foe]) -> Option<Foe> {
    foes.iter()
        .filter(|f| f.champion && dist(me, f.at) <= Q_REACH && !blocked(me, f, foes))
        .max_by_key(|f| (f.hunted, band(dist(me, f.at)), 100 - f.hp_pct.min(100)))
        .copied()
}

/// 猛扑猎杀的目标：射程内的敌方英雄，被捕猎的优先，再按血量比例低排。
pub fn ult_pick(me: (f64, f64), foes: &[Foe]) -> Option<Foe> {
    foes.iter()
        .filter(|f| f.champion && dist(me, f.at) <= R_REACH)
        .max_by_key(|f| (f.hunted, 100 - f.hp_pct.min(100)))
        .copied()
}

/// 草丛加速这一 tick 该是多少（0 = 不加）：`left` 是还剩几 tick（草丛里一直是满的）。
pub fn brush_speed(p: &Params, alive: bool, left: usize, foe_near: bool) -> usize {
    if !alive || left == 0 {
        0
    } else if foe_near {
        p.brush_near_ms
    } else {
        p.brush_ms
    }
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 场上的敌方单位（不算塔）。
fn foes(sim: &StableSim<'_>, team: usize) -> Vec<Foe> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower() {
            continue;
        }
        let (x, y) = u.pos();
        let (hp, max) = u.hp();
        out.push(Foe { id: u.id(), at: (x as f64, y as f64), champion: u.is_champion(), hunted: false,
                       hp_pct: if max == 0 { 100 } else { hp * 100 / max } });
    }
    for f in out.iter_mut().filter(|f| f.champion) {
        f.hunted = has_buff(sim, f.id, HUNTED);
    }
    out
}

// ===================== 被动：寻觅（草丛加速） =====================

#[derive(Clone, Default)]
struct Prowl {
    p: Params,
    /// 这场用的草丛（第一次 on_update 时挑）；None = 地图没有草丛格子。
    grid: Option<Option<bush::Grid>>,
    left: usize,
    /// 身上本包的加速现在是多少（0 = 没有）。
    speed: usize,
    was_in: bool,
}

impl StablePassive for Prowl {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.left = 0;
        self.speed = 0;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, team, (x, y)) = (e.is_alive(), e.team(), e.pos());
        if self.grid.is_none() {
            let points: Vec<(f64, f64)> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|u| u.is_alive())
                .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
                .collect();
            let g = bush::pick_bushes(&points, &bush::maps());
            wlog(match &g {
                Some(g) => format!("{} BUSHES: {} bush cells", head(sim, me), g.count()),
                None => format!("{} BUSHES: no bush grid - no brush speed", head(sim, me)),
            });
            self.grid = Some(g);
        }
        let at = (x as f64, y as f64);
        let in_bush = self.grid.as_ref().and_then(|g| g.as_ref()).is_some_and(|g| g.at(at.0, at.1));
        if in_bush != self.was_in && alive {
            if let Some(k) = counted("bush") {
                wlog(format!("{} {} the bush at ({x}, {y}) #{k}", head(sim, me), if in_bush { "INTO" } else { "OUT OF" }));
            }
        }
        self.was_in = in_bush;
        self.left = if in_bush { self.p.brush_t } else { self.left.saturating_sub(1) };
        let foe_near = self.left > 0 && (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).any(|u| {
            u.team() != team && u.is_alive() && u.is_champion() && sim.is_visible(team, u.id())
                && dist(at, (u.pos().0 as f64, u.pos().1 as f64)) <= self.p.near as f64
        });
        let want = brush_speed(&self.p, alive, self.left, foe_near);
        if want != self.speed || (want > 0 && !has_buff(sim, me, BRUSH)) {
            sim.entity_remove_buff(me, BRUSH);
            if want > 0 {
                let mut b = BuffV1::named(BRUSH);
                b.move_speed_mult = want as _;
                sim.add_buff(me, &b);
            }
            if let Some(k) = counted("speed") {
                wlog(format!("{} BRUSH SPEED {} -> {want}% #{k}", head(sim, me), self.speed));
            }
            self.speed = want;
        }
    }
}

// ===================== AI 钩子：标枪和猛扑猎杀挑目标 =====================

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
        if InputTargetKindV1::from_code(b.target.kind) != Some(InputTargetKindV1::Target) {
            return None;
        }
        let skill = b.kind == InputKindV1::Skill.code();
        if !skill && b.kind != InputKindV1::Ult.code() {
            return None;
        }
        let current = b.target.target_id;
        let player = ctx.player_id();
        let (kind, pick, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let mid = me.id();
            // the javelin only in human form with it ready (the cougar's Q arms Takedown: no target to pick)
            if skill && (!has_buff(&sim, mid, HUMAN) || has_buff(&sim, mid, FORM) || has_buff(&sim, mid, Q_CD)) {
                return None;
            }
            let at = (me.pos().0 as f64, me.pos().1 as f64);
            let all = foes(&sim, me.team());
            let pick = if skill { javelin_pick(at, &all) } else { ult_pick(at, &all) }?;
            if pick.id == current {
                return None;
            }
            let d = dist(at, pick.at);
            (if skill { "javelin" } else { "ult" }, pick,
             format!("{} {} {} -> {} ({:.0} away, {}hp {}%)", head(&sim, mid), if skill { "Q" } else { "R" },
                     who(&sim, current), who(&sim, pick.id), d, if pick.hunted { "HUNTED, " } else { "" }, pick.hp_pct))
        };
        let input = InputV1::action(if skill { InputKindV1::Skill } else { InputKindV1::Ult }, InputTargetV1::target(pick.id));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(k) = counted(kind) {
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
        "=== {ID} v{VERSION} (Nidalee: the whole-body cougar, Prowl's brush speed, the javelin's and the hunt pounce's targets) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:prowl"), Prowl::default());
    module.add_player_input_ai(AimAi);
    host.log(LogLevel::Info, "league_nidalee loaded (whole-body cougar, brush speed, javelin and hunt pounce targets).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module.set_map_customizer(bush::BushReader);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    fn foe(id: usize, x: f64, champion: bool, hunted: bool, hp_pct: usize) -> Foe {
        Foe { id, at: (x, 0.0), champion, hunted, hp_pct }
    }

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"brush_ms":15,"junk":7}"#).brush_ms, 15);
    }

    #[test]
    fn the_javelin_takes_a_clear_line_hunted_first_then_farther_then_lower() {
        let me = (0.0, 0.0);
        // a minion in front of the near champion blocks it; the far champion's line is clear (offset sideways)
        let near = foe(1, 20_000.0, true, false, 90);
        let minion = foe(2, 10_000.0, false, false, 100);
        let far = Foe { id: 3, at: (0.0, 60_000.0), champion: true, hunted: false, hp_pct: 90 };
        assert_eq!(javelin_pick(me, &[near, minion, far]).map(|f| f.id), Some(3));
        // hunted beats farther
        let hunted = Foe { id: 4, at: (-20_000.0, 0.0), champion: true, hunted: true, hp_pct: 100 };
        assert_eq!(javelin_pick(me, &[near, minion, far, hunted]).map(|f| f.id), Some(4));
        // out of reach or only blocked: none
        assert_eq!(javelin_pick(me, &[foe(5, 90_000.0, true, true, 10)]), None);
        assert_eq!(javelin_pick(me, &[near, minion]), None);
        // same band: the lower health
        let a = Foe { id: 6, at: (0.0, 40_000.0), champion: true, hunted: false, hp_pct: 80 };
        let b = Foe { id: 7, at: (0.0, -45_000.0), champion: true, hunted: false, hp_pct: 30 };
        assert_eq!(javelin_pick(me, &[a, b]).map(|f| f.id), Some(7));
    }

    #[test]
    fn the_hunt_pounce_takes_the_hunted_then_the_lowest() {
        let me = (0.0, 0.0);
        let a = foe(1, 30_000.0, true, false, 20);
        let b = foe(2, -40_000.0, true, true, 70);
        let c = foe(3, 70_000.0, true, true, 5); // out of reach
        assert_eq!(ult_pick(me, &[a, b, c]).map(|f| f.id), Some(2));
        assert_eq!(ult_pick(me, &[a, foe(4, 10_000.0, false, true, 1)]).map(|f| f.id), Some(1));
    }

    #[test]
    fn brush_speed_and_its_tail() {
        let p = Params::default();
        assert_eq!(brush_speed(&p, true, p.brush_t, false), 10);
        assert_eq!(brush_speed(&p, true, 1, true), 30);
        assert_eq!(brush_speed(&p, true, 0, true), 0);
        assert_eq!(brush_speed(&p, false, 50, true), 0);
    }
}
