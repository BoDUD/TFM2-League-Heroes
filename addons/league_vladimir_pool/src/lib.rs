//! 弗拉基米尔附加包：W「血红之池」在快没血时自动开（用户：「危险信号 + 现在就做扩展包」）。
//!
//! 主包保持纯数据：数据读不到当前生命，主包的血池由普攻里的「危险信号」开——两名以上敌方英雄贴身，或连续两次检查
//! 都挨了打（`league_vladimir_w_go`）；血池本身是数据：他身上一直跑着一个每 3 tick 看一次的轮询（`AddCasted`），
//! 看到 `w_go` 就化成血池（不可选取、减速吸血、`w_cd` 冷却）。
//! `mod.override_info` 把主包的弗拉基米尔换成 `override/` 里的副本：普攻里的危险信号去掉，`passive` 换成本包的
//! `league_vladimir_pool:guard`，由它读生命：
//!
//! - 活着、没被控住、身边 `near` 内有敌方英雄、血池不在冷却（`w_cd`）、不在池里（`w_in`）、生命低于 `hp`%——
//!   加上 `w_go`（30 tick），数据的轮询最多 3 tick 后开池（每 tick 看一次，挨打时 `on_damaged` 当场再看一次）。
//! - 只在数据的轮询在跑（他身上有 `league_vladimir_polling`）时才叫（0.2.2）：轮询由他的普攻和技能开起来、随他一起死，
//!   复活后到他第一次出手之前没人看 `w_go`。没在跑就不加 `w_go`、不扣血，每条命记一行 `GO WAIT: no poll`，等轮询开起来再叫。
//! - 血池的代价按英雄联盟：扣**当前**生命的 `cost`%（默认 20），在加上 `w_go` 的同一刻扣（还没进池，不受池里的 100% 减伤），
//!   永远不会扣死。主包的数据读不到当前生命，只能扣 5% 最大生命值——第一份日志里 3% 血开池被扣到 1 点（用户：「改吧」），
//!   所以本包的副本去掉了数据里的那一下，由这里来扣。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从 tools/kit/build_vladimir.py 的参数表 P 写进去：
//! `n_hp`、`n_near`、`n_cost`），本包不另记一份。不用全局变量，服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_vladimir_pool.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_vladimir_pool";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_vladimir_pool") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 主包弗拉基米尔的名字（buff 都以它开头）。
fn vl(x: &str) -> String {
    format!("league_vladimir_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VLADIMIR_POOL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_vladimir_pool.log");
        }
    }
    PathBuf::from("league_vladimir_pool.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (15 000 lines a session,
    // about 9 s of stalls on the simulation thread, 2026-10-12, the user: 「LOL mod让游戏掉帧很严重 加载很卡」)
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

/// The `Params` the log showed last (they come from the champion data: the same in every simulation of a launch).
static PARAMS_SHOWN: Mutex<Option<Params>> = Mutex::new(None);

/// `p` not in the log yet: once a launch, again only should they ever differ (league_zyra 0.1.2's; 0.2.1: 11-06's log had
/// 321 of its 1283 lines `SPAWN ... Params {...}`, one each life).
fn params_new(p: &Params) -> bool {
    let mut shown = PARAMS_SHOWN.lock().unwrap_or_else(|e| e.into_inner());
    if shown.as_ref() == Some(p) {
        return false;
    }
    *shown = Some(p.clone());
    true
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 生命低于 `hp`% 时开池。
    pub hp: usize,
    /// 身边这么近有敌方英雄才开。
    pub near: usize,
    /// 开池扣当前生命的 `cost`%。
    pub cost: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { hp: 35, near: 60_000, cost: 20 }
    }
}

/// `{"hp":35,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "hp" => &mut p.hp,
            "near" => &mut p.near,
            "cost" => &mut p.cost,
            _ => continue,
        };
        *slot = v;
    }
    p
}

// ===================== 判断 =====================

/// 这一 tick 看到的。
#[derive(Clone, Copy, Debug, Default)]
pub struct Now {
    pub hp: f64,
    pub enemy_near: bool,
    pub controlled: bool,
    /// 血池在冷却、已经在池里，或已经叫过（`w_go` 还在）。
    pub busy: bool,
    /// 数据的轮询在跑（`league_vladimir_polling`）：只有它看 `w_go`（0.2.2）。
    pub polling: bool,
}

/// 现在该不该开池。
pub fn want_pool(p: &Params, n: &Now) -> bool {
    !n.busy && !n.controlled && n.enemy_near && n.hp < p.hp as f64
}

/// 这一 tick 做什么（0.2.2）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Step {
    /// 不开。
    Idle,
    /// 开：加上 `w_go`、扣代价。
    Go,
    /// 该开，可数据的轮询没在跑：`w_go` 没人看（11-08 的日志：复活 758 tick 后 90 tick 里叫了 3 次、生命 18% -> 9%，一次池都没开），
    /// 不加、不扣，等他的普攻或技能把轮询开起来。
    Wait,
}

pub fn step(p: &Params, n: &Now) -> Step {
    match (want_pool(p, n), n.polling) {
        (false, _) => Step::Idle,
        (true, true) => Step::Go,
        (true, false) => Step::Wait,
    }
}

/// 开池扣的血：当前生命的 `cost`%，至少留 1 点。
pub fn cost_of(p: &Params, now: usize) -> usize {
    (now * p.cost / 100).min(now.saturating_sub(1))
}

// ===================== 小工具 =====================

fn buff_names(sim: &StableSim<'_>, id: usize) -> Vec<String> {
    sim.get_entity(id)
        .map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect())
}

/// 打断施法的控制（英雄联盟里被控住时放不了 W）。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];

fn controlled(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id)
        .is_some_and(|e| (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| NO_CAST.iter().any(|k| k.code() == c.kind))))
}

fn enemy_near(sim: &StableSim<'_>, me: usize, team: usize, near: usize) -> bool {
    let r2 = (near as u64).saturating_mul(near as u64);
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).any(|e| {
        e.is_champion() && e.is_alive() && e.team() != team && sim.distance_sq(me, e.id()) <= r2
    })
}

// ===================== 被动 =====================

/// 每个弗拉基米尔一份：参数，上一 tick 是否在池里（记日志用）、叫过几次，这条命从哪个 tick 起在等轮询（`GO WAIT`，0.2.2）。
#[derive(Clone, Default)]
struct Guard {
    p: Params,
    was_in: bool,
    calls: usize,
    wait_from: Option<usize>,
    /// 这条命已经记过 `GO WAIT`（每条命一行）。
    waited: bool,
}

impl Guard {
    fn look(&mut self, sim: &mut StableSim<'_>, me: usize, from_hit: bool) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.was_in = false;
            return;
        }
        let (now, max) = e.hp();
        let team = e.team();
        let hp = if max > 0 { now as f64 * 100.0 / max as f64 } else { 100.0 };
        let names = buff_names(sim, me);
        let has = |x: &str| names.iter().any(|b| *b == vl(x));
        let inside = has("w_in");
        if inside && !self.was_in {
            wlog(format!("{} POOL: hp {hp:.0}%", head(sim, me)));
        }
        self.was_in = inside;
        let n = Now {
            hp,
            enemy_near: enemy_near(sim, me, team, self.p.near),
            controlled: controlled(sim, me),
            busy: inside || has("w_cd") || has("w_go"),
            polling: has("polling"),
        };
        let tick = sim.tick();
        match step(&self.p, &n) {
            // no longer wanted (healed, no enemy near, controlled): a wait for the poll ends without a call
            Step::Idle => self.wait_from = None,
            Step::Wait => {
                self.wait_from.get_or_insert(tick);
                if !self.waited {
                    self.waited = true;
                    wlog(format!("{} GO WAIT: no poll - hp {hp:.0}%, an enemy champion near; no w_go and no cost till his \
                                  next attack or spell starts the data's poll", head(sim, me)));
                }
            }
            Step::Go => self.go(sim, me, now, max, hp, from_hit, tick),
        }
    }

    /// Calls the pool: `w_go` for the data's poll and the cost (the poll runs: `step`).
    #[allow(clippy::too_many_arguments)]
    fn go(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize, max: usize, hp: f64, from_hit: bool, tick: usize) {
        // the flag first: the cost below is damage, and on_damaged looks again (busy by then)
        let mut go = BuffV1::timed(&vl("w_go"), 30);
        go.duration_kind = BuffDurationV1::Time.code();
        sim.add_buff(me, &go);
        let cost = cost_of(&self.p, now);
        if cost > 0 {
            sim.deal_damage_raw(me, me, cost, 0, AttackTypeV1::Skill);
        }
        let after = sim.get_entity(me).map_or(now, |e| e.hp().0);
        let left = if max > 0 { after as f64 * 100.0 / max as f64 } else { 100.0 };
        self.calls += 1;
        // the first call after a GO WAIT is always written (how long the wait for the poll was)
        let waited = self.wait_from.take().map_or(String::new(), |t0| format!(", {} ticks after GO WAIT", tick - t0));
        if self.calls <= 20 || self.calls % 50 == 0 || !waited.is_empty() {
            wlog(format!("{} GO #{}: hp {hp:.0}% -> {left:.0}% (cost {cost} of {now}){}{waited}", head(sim, me), self.calls,
                         if from_hit { " on a hit" } else { "" }));
        }
    }
}

impl StablePassive for Guard {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.was_in = false;
        // a new life: its poll starts with his first attack or spell (the last one died with him)
        self.wait_from = None;
        self.waited = false;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        // the Params in the first SPAWN line of a launch only (0.2.1)
        let params = if params_new(&self.p) { format!(", {:?}", self.p) } else { String::new() };
        wlog(format!("{} SPAWN: the add-on's Vladimir (player {player}, team {team}){params}", head(sim, me)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.look(sim, me, false);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _: usize, _: usize) {
        self.look(sim, me, true);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Sanguine Pool at low health, 20% of current health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:guard"), Guard::default());
    host.log(LogLevel::Info, "league_vladimir_pool v2 loaded (Vladimir's Sanguine Pool at low health, costing 20% of current health).");
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

    fn now(hp: f64) -> Now {
        Now { hp, enemy_near: true, controlled: false, busy: false, polling: true }
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"hp":30,"near":50000,"cost":15,"x":1}"#), Params { hp: 30, near: 50_000, cost: 15 });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_params_are_logged_once_a_launch() {
        // 11-06: every SPAWN line carried the whole Params (321 of 1283 lines)
        let p = Params { hp: 1, near: 2, cost: 3 };
        assert!(params_new(&p));
        assert!(!params_new(&p) && !params_new(&p.clone()));
        // changed (should a launch ever see two tables): shown again
        let q = Params { hp: 4, ..p.clone() };
        assert!(params_new(&q) && !params_new(&q));
    }

    #[test]
    fn pool_only_below_the_line_with_an_enemy_near() {
        let p = Params::default();
        assert!(want_pool(&p, &now(34.0)));
        assert!(!want_pool(&p, &now(35.0)));
        assert!(!want_pool(&p, &now(80.0)));
        assert!(!want_pool(&p, &Now { enemy_near: false, ..now(10.0) }));
    }

    #[test]
    fn never_while_busy_or_controlled() {
        let p = Params::default();
        assert!(!want_pool(&p, &Now { busy: true, ..now(10.0) }));
        assert!(!want_pool(&p, &Now { controlled: true, ..now(10.0) }));
    }

    #[test]
    fn the_cost_is_a_share_of_current_health_and_never_kills() {
        let p = Params::default();
        assert_eq!(cost_of(&p, 1000), 200);
        assert_eq!(cost_of(&p, 30), 6);
        assert_eq!(cost_of(&p, 4), 0);
        assert_eq!(cost_of(&p, 1), 0);
        assert_eq!(cost_of(&Params { cost: 100, ..p }, 50), 49);
    }

    #[test]
    fn no_call_and_no_cost_while_the_poll_is_down() {
        // 11-08, m=4458: 758 ticks after a respawn, 3 GOs in 90 ticks (hp 18 -> 15 -> 12 -> 9%) and no pool - the poll
        // that reads w_go had died with him and only his attacks and spells start it again
        let p = Params::default();
        assert_eq!(step(&p, &now(18.0)), Step::Go);
        assert_eq!(step(&p, &Now { polling: false, ..now(18.0) }), Step::Wait);
        // nothing to wait for above the line, busy or controlled
        assert_eq!(step(&p, &Now { polling: false, ..now(80.0) }), Step::Idle);
        assert_eq!(step(&p, &Now { polling: false, busy: true, ..now(10.0) }), Step::Idle);
        assert_eq!(step(&p, &Now { polling: false, controlled: true, ..now(10.0) }), Step::Idle);
        assert_eq!(step(&p, &Now { polling: true, enemy_near: false, ..now(10.0) }), Step::Idle);
    }

    #[test]
    fn the_poll_flag_is_the_kits() {
        // the data's poll keeps `polling` up while it runs (build_vladimir.py: flag("polling", ...) / refresh("polling", ...))
        let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_vladimir.py"))
            .expect("build_vladimir.py");
        assert!(src.contains("flag(\"polling\"") && src.contains("refresh(\"polling\""), "the kit's poll flag is not `polling`");
        assert_eq!(vl("polling"), "league_vladimir_polling");
        assert!(vl("polling").len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn the_flag_names_fit() {
        assert!(vl("w_go").len() <= BUFF_NAME_CAP);
        assert_eq!(vl("w_cd"), "league_vladimir_w_cd");
    }
}
