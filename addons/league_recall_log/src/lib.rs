//! 回城记录器（用户 2026-10-15：「按你的建议开pr合并吧」——修了维克托 / 辛德拉 / 卡兹克的等级探针之后，用一个只读的记录器在
//! 平时的对局里收集「金克丝单独在场时对面也回城」的证据，不用专门打测试局）。
//!
//! 游戏 0.6.x 的对线 AI 在算出自己快死时回城：`my_die = (血量 − nuke) × 60 / dps`，nuke / dps 是 15 万以内可见、血量 40% 以上的
//! 敌方英雄的估算之和（champion-data 第 8 节）。AI 回城前多半先走到安全处，按下回城时身边常常已经没人，所以这里记的是回城前
//! `WINDOW` tick 里进过 `NEAR` 以内的敌方英雄（最近多近、多久以前）和这段时间自己的最低血量。
//!
//! 观察钩子 `league_recall_log:watch` 挂在所有玩家上，优先级最低，**永远不改 AI 的输入**（think 一律返回 None）。每 `SCAN`
//! tick 看一次身边的敌方英雄；AI 下回城命令（`InputKindV1::Return`，一次回城的第一道命令）时写一行：
//! `RECALL [来历 m=比赛 s=第几局] t=分:秒 <英雄> T<队> <位置> hp=<现在>% low=<窗口里最低>% near=[<敌方英雄> <最近距离>k <几秒前>, ...]`，
//! 窗口里有敌方英雄、而且血量一直没低于 `SUSPECT_HP`% 的回城再标 `SUSPECT`（不像是被打残了回家）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_recall_log.log`，每次启动游戏重写，上一次的留在 .prev.log；
//! 你看的那场全记，其余（服务端的预模拟）一次启动最多 `LOG_CAP` 行。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_recall_log";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_recall_log") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 观察钩子的优先级：最低（只看不改）。
const WATCH_PRIORITY: i32 = -2_000_000;
/// 「身边」：引擎算 nuke / dps 的范围。
pub const NEAR: u64 = 150_000;
/// 回城前看多久（tick，10 秒）。
pub const WINDOW: usize = 600;
/// 多久看一次身边（tick）。
const SCAN: usize = 10;
/// 血量一直在这以上的回城算可疑。
pub const SUSPECT_HP: usize = 60;
/// 一次启动最多写多少行不在屏幕上的（服务端的预模拟；你看的那场不算）：2 万行在 10-30 一次启动的第 4 分钟就满了，2.3 MB。
const LOG_CAP: usize = 2_000;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_RECALL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_recall_log.log");
        }
    }
    PathBuf::from("league_recall_log.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

/// One more line: whether it is to be written - every one from the match on screen (watched, spectated or replayed),
/// the rest the first LOG_CAP of the launch.
fn room(sim: &StableSim<'_>) -> bool {
    let on_screen = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    on_screen || LINES.fetch_add(1, Ordering::Relaxed) < LOG_CAP
}

fn wlog(msg: impl AsRef<str>) {
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (memory log-open-once)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

fn head(sim: &StableSim<'_>) -> String {
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
    let t = sim.tick();
    format!("[{kind} m={} s={}] t={}:{:02}", m(o.match_id), m(o.set_index), t / 3600, t / 60 % 60)
}

fn lane_name(lane: Option<LaneV1>) -> &'static str {
    match lane {
        Some(LaneV1::Top) => "Top",
        Some(LaneV1::Jungle) => "Jungle",
        Some(LaneV1::Mid) => "Mid",
        Some(LaneV1::Bottom) => "Bottom",
        Some(LaneV1::Support) => "Support",
        None => "?",
    }
}

fn percent((now, max): (usize, usize)) -> usize {
    if max == 0 {
        100
    } else {
        now * 100 / max
    }
}

// ===================== 窗口 =====================

/// An enemy champion seen near: when last, how close at the closest.
#[derive(Clone, Debug, PartialEq)]
pub struct Seen {
    pub id: usize,
    pub name: String,
    pub last: usize,
    pub closest: u64,
}

/// What one player saw over the last `WINDOW` ticks.
#[derive(Clone, Debug, Default)]
pub struct Recent {
    pub seen: Vec<Seen>,
    /// (tick, hp %) samples, oldest first.
    pub hp: Vec<(usize, usize)>,
}

impl Recent {
    pub fn note_hp(&mut self, tick: usize, hp: usize) {
        self.hp.push((tick, hp));
        self.forget(tick);
    }

    pub fn note_enemy(&mut self, tick: usize, id: usize, name: &str, dist: u64) {
        match self.seen.iter_mut().find(|s| s.id == id) {
            Some(s) => {
                // a fresh sighting after the window starts the closest distance over
                if tick.saturating_sub(s.last) > WINDOW {
                    s.closest = dist;
                }
                s.last = tick;
                s.closest = s.closest.min(dist);
            }
            None => self.seen.push(Seen { id, name: name.to_string(), last: tick, closest: dist }),
        }
    }

    fn forget(&mut self, tick: usize) {
        self.seen.retain(|s| tick.saturating_sub(s.last) <= WINDOW);
        self.hp.retain(|(t, _)| tick.saturating_sub(*t) <= WINDOW);
    }

    /// Lowest hp % in the window (100 when nothing was sampled).
    pub fn low(&self) -> usize {
        self.hp.iter().map(|(_, h)| *h).min().unwrap_or(100)
    }

    /// Enemies in the window, closest first.
    pub fn near(&self, tick: usize) -> Vec<&Seen> {
        let mut v: Vec<&Seen> = self.seen.iter().filter(|s| tick.saturating_sub(s.last) <= WINDOW).collect();
        v.sort_by_key(|s| s.closest);
        v
    }

    /// An enemy champion was near and the health never fell below `SUSPECT_HP`%: not a trip home to heal.
    pub fn suspect(&self, tick: usize, hp_now: usize) -> bool {
        !self.near(tick).is_empty() && self.low().min(hp_now) >= SUSPECT_HP
    }
}

// ===================== 观察钩子 =====================

#[derive(Clone, Default)]
struct Watch {
    recent: Recent,
    next_scan: usize,
    /// The AI is in a recall order (no new line until it gives another order).
    returning: bool,
}

/// Distance in map units from a squared distance.
fn root(sq: u64) -> u64 {
    (sq as f64).sqrt() as u64
}

impl Watch {
    fn scan(&mut self, sim: &StableSim<'_>, me: usize, team: usize, tick: usize) {
        if let Some(e) = sim.get_entity(me) {
            self.recent.note_hp(tick, percent(e.hp()));
        }
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(e) = sim.get_entity(id) else { continue };
            if e.team() == team || !e.is_alive() {
                continue;
            }
            let d = root(sim.distance_sq(me, id));
            if d <= NEAR {
                let name = e.name().unwrap_or_else(|| format!("#{id}"));
                self.recent.note_enemy(tick, id, &name, d);
            }
        }
    }
}

impl StablePlayerAi for Watch {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:watch")
    }

    fn priority(&self) -> i32 {
        WATCH_PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let tick = ctx.tick();
        let (player, team, lane) = (ctx.player_id(), ctx.team(), ctx.lane());
        let sim = ctx.sim()?;
        let me = sim.get_player(player)?.champion()?;
        let (me_id, me_name, hp_now) = (me.id(), me.name().unwrap_or_default(), percent(me.hp()));
        if tick >= self.next_scan {
            self.next_scan = tick + SCAN;
            self.scan(&sim, me_id, team, tick);
        }
        let kind = InputKindV1::from_code(base?.kind)?;
        if kind != InputKindV1::Return {
            self.returning = false;
            return None;
        }
        if self.returning {
            return None;
        }
        self.returning = true;
        if !room(&sim) {
            return None;
        }
        let near: Vec<String> = self
            .recent
            .near(tick)
            .iter()
            .map(|s| format!("{} {}k {:.1}s", s.name, s.closest / 1000, tick.saturating_sub(s.last) as f64 / 60.0))
            .collect();
        wlog(format!(
            "RECALL {} {me_name} T{team} {} hp={hp_now}% low={}% near=[{}]{}",
            head(&sim),
            lane_name(lane),
            self.recent.low(),
            near.join(", "),
            if self.recent.suspect(tick, hp_now) { " SUSPECT" } else { "" }
        ));
        None
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (read-only recall log) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Watch::default());
    host.log(LogLevel::Info, "league_recall_log loaded (read-only recall log).");
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
    fn a_recall_with_an_enemy_near_at_full_health_is_suspect() {
        let mut r = Recent::default();
        for t in (0..300).step_by(10) {
            r.note_hp(t, 95);
        }
        r.note_enemy(100, 7, "league_jinx", 80_000);
        r.note_enemy(150, 7, "league_jinx", 60_000);
        assert!(r.suspect(300, 95));
        assert_eq!(r.near(300)[0].closest, 60_000);
        assert_eq!(r.near(300)[0].last, 150);
    }

    #[test]
    fn a_trip_home_after_losing_health_or_with_nobody_near_is_not() {
        let mut r = Recent::default();
        r.note_hp(0, 100);
        r.note_hp(100, 30);
        r.note_enemy(100, 7, "league_jinx", 50_000);
        assert!(!r.suspect(200, 45));
        let mut quiet = Recent::default();
        quiet.note_hp(0, 100);
        assert!(!quiet.suspect(100, 100));
    }

    #[test]
    fn sightings_older_than_the_window_are_dropped() {
        let mut r = Recent::default();
        r.note_enemy(0, 7, "league_jinx", 10_000);
        r.note_hp(WINDOW + 50, 100);
        assert!(r.near(WINDOW + 50).is_empty());
        r.note_enemy(WINDOW + 60, 7, "league_jinx", 90_000);
        assert_eq!(r.near(WINDOW + 60)[0].closest, 90_000);
    }
}
