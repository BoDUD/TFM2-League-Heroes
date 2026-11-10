//! 永恩附加包：R「封尘绝念斩」照英雄联盟冲到最后一个被斩中的英雄身后，把斩中的人拉过来（用户 2026-10-24：「查看现在没有
//! 做附加包的英雄有明显不一样的话全部补附加包」）。
//!
//! 主包是纯数据：R 斩出直线后 `RushMoveToBack` 冲到**选中的目标**身后，不拉人。英雄联盟里他停在直线上最后一个被命中的
//! 英雄身后，被命中的人都被拉向他落脚的地方。本包：副本里的 `RushMoveToBack` 换成给永恩挂 `GO`，直线上的伤害给每个被斩中的
//! 英雄挂 `STRUCK`（3 tick）；被动 `league_yone_r:dash` 看到 `GO`：
//!
//! - 等斩中的标记出来（最多 `WAIT` tick），挑离永恩最远的那个，冲到他身后（沿永恩到他的方向，两人里大的身体半径再加
//!   `BEHIND_GAP`：落在他身体外面），每 tick `SPEED`（主包的冲刺速度），离落点不到 `ARRIVE` 或按距离算好的步数用完就算到；
//!   一个都没斩中就照主包冲到离他最近的敌方英雄身后（`REACH` 内），都没有就不动。
//! - 冲到之后把斩中的英雄拉向他（`entity_pull`，每 tick `PULL_SPEED`，最多拉 `PULL_MAX`，停在他身前 `STOP`）。
//!
//! 引擎每 tick 把中心进了别的英雄半径（10000）的英雄推开 1000：原来落在他身后 6000（他身体里）、离落点不到 1 才算到，引擎推开、
//! 本包放回，永恩的编号比他小时一直顶到 20 步的上限（2026-11-02 复查 11-01 的日志：64 次里 59 次；编号大时 107 次里 3 次，
//! 到了的也多走 3-5 步）。
//!
//! 两张 5v5 地图（2026-11-10）：落点和每一步夹在这一场的地图里（`game_places::terrain::map_of_sim`：游戏自己的 960000 见方，
//! Rin 的召唤师峡谷 1614545 见方；以前一律按 960000，峡谷上过了 960000 的落点被夹回半张图的边）。峡谷上落点进了墙（离墙比
//! 作者的寻路允许的近，`game_places::terrain::stand_ok`：峡谷的墙往外长一格）就挪到 `LAND_REACH` 内最近能站的地方
//! （`stand_spot`）；冲的每一步落在站不住的地方就冲到这里为止、停在上一个能站的地方；被斩中的人也只拉到墙前（拉的每一步都要
//! 能站）。以前一步步挪进墙里，人就卡在那里（用户 2026-11-10：「有的地方会走路卡住」）。没有墙体文件时只有地图边。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yone_r.log`。你看的那场每行都写，服务器的预模拟每种先写
//! `LOG_FIRST` 行、之后每 `LOG_EVERY` 次一行（见 `tally`）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{map_of_sim, rift_status, stand_ok, stand_spot, Map};
use mod_api_stable::*;

const ID: &str = "league_yone_r";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_yone_r") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const GO: &str = "league_yone_r_go";
pub const STRUCK: &str = "league_yone_r_struck";
/// 主包的冲刺速度（`RushMoveToBack` 12000）和直线长度（90000）。
pub const SPEED: f64 = 12_000.0;
pub const REACH: f64 = 90_000.0;
/// 落点在两人里大的那个身体半径之外再留这么多（引擎的英雄半径 10000；主包的 RushMoveToBack 落在 15000）。
pub const BEHIND_GAP: f64 = 1_000.0;
/// 读不到身体半径时用的（引擎的英雄半径）。
pub const BODY: f64 = 10_000.0;
/// 离落点这么近就算到了（引擎一次推开 1000）。
pub const ARRIVE: f64 = 1_500.0;
/// 冲刺的步数：按落点的距离算的之外再多给这么多，最多 `STEP_MAX`。
pub const STEP_SPARE: usize = 2;
pub const STEP_MAX: usize = 20;
pub const WAIT: usize = 4;
pub const PULL_SPEED: usize = 2_000;
pub const PULL_MAX: f64 = 16_000.0;
/// 拉到他身前多远停（他的身体外面：停在 6000 的又被引擎推开）。
pub const STOP: f64 = 12_000.0;
/// 峡谷上落点进了墙时，在这么远内找最近能站的地方（`stand_spot`；他落在被斩中的人身后 `back_of` ~11000 处）。
pub const LAND_REACH: f64 = 30_000.0;
/// 游戏自己的 5v5 地图边长；峡谷的看 `Map::extent`。
const MAP: f64 = 960_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_YONE_R_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_yone_r.log");
        }
    }
    PathBuf::from("league_yone_r.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// 日志行数的上限（2026-10-30 一次启动 0.82 MB、10 969 行：八成是预模拟的 R / LANDED，两成是预模拟的 SPAWN）。
/// 计数是全局的：每场预模拟的被动都是新实例，以前记在实例里的 `n <= 80 || n % 25 == 0` 一行也没拦住。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind`: its count when it is to be written - every one in the match on screen (watched,
/// spectated or replayed), the server's presims (and background matches) the first `LOG_FIRST`, then every
/// `LOG_EVERY`-th.
fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let on_screen = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (on_screen || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>, me: usize) -> String {
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
    format!("[{kind} m={} s={}] t={} #{me}", m(o.match_id), m(o.set_index), sim.tick())
}

/// This launch's log has told the Rift already.
static RIFT_TOLD: AtomicBool = AtomicBool::new(false);

/// The map this sim plays on; the first Rift a launch, a line in the log.
fn map_here(sim: &StableSim<'_>) -> Map {
    let map = map_of_sim(sim);
    if map == Map::Rift && !RIFT_TOLD.swap(true, Ordering::Relaxed) {
        wlog(format!("== Rift: the landing behind the last one struck and the dash's steps are kept on the Rift's {:.0} \
                      square (not the game's own {MAP:.0}), the landing off its walls (stand_spot within {LAND_REACH:.0}), \
                      the dash and the pull stop at the last spot off them (stand_ok); {} ==", map.extent(), rift_status()));
    }
    map
}

// ===================== 落脚点 =====================

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 夹在 `map` 上（坐标 0..边长-1）。
fn clamp(map: Map, p: Pt) -> Pt {
    let e = map.extent();
    (p.0.clamp(0.0, e - 1.0), p.1.clamp(0.0, e - 1.0))
}

/// How far past the last one struck he lands: clear of both bodies (`my_r`, `their_r`; 0 = unknown, `BODY`).
pub fn back_of(my_r: f64, their_r: f64) -> f64 {
    let r = |x: f64| if x > 0.0 { x } else { BODY };
    r(my_r).max(r(their_r)) + BEHIND_GAP
}

/// [`behind_on`] on the game's own map.
pub fn behind(me: Pt, last: Pt, back: f64) -> Pt {
    behind_on(Map::Native, me, last, back)
}

/// Where he lands: `back` past `last` on the way from `me` (at `last` itself when they stand on one spot), on `map`.
pub fn behind_on(map: Map, me: Pt, last: Pt, back: f64) -> Pt {
    let d = dist(me, last);
    if d < 1.0 {
        return last;
    }
    clamp(map, (last.0 + (last.0 - me.0) / d * back, last.1 + (last.1 - me.1) / d * back))
}

/// [`behind_on`] off the Rift's walls: the landing through `spot` - the runtime's `stand_spot(map, p, LAND_REACH)`: on the
/// Rift the nearest spot within `LAND_REACH` a hero can stand on (the landing itself when it is one, or none is that
/// near), the landing as it was on the game's own map.
pub fn landing_in(map: Map, me: Pt, last: Pt, back: f64, spot: impl Fn(Pt) -> Pt) -> Pt {
    spot(behind_on(map, me, last, back))
}

/// The steps a dash of `d` may take: at SPEED a step, `STEP_SPARE` more, at most `STEP_MAX`.
pub fn dash_budget(d: f64) -> usize {
    ((d / SPEED).ceil() as usize + STEP_SPARE).min(STEP_MAX)
}

/// The champion struck farthest from him (the last one the slash reaches).
pub fn last_struck(me: Pt, struck: &[(usize, Pt)]) -> Option<(usize, Pt)> {
    struck.iter().copied().max_by(|a, b| dist(me, a.1).total_cmp(&dist(me, b.1)))
}

/// [`step_on`] on the game's own map.
pub fn step(at: Pt, goal: Pt) -> Option<Pt> {
    step_on(Map::Native, at, goal)
}

/// One dash step toward `goal` on `map` (None: there, within `ARRIVE`).
pub fn step_on(map: Map, at: Pt, goal: Pt) -> Option<Pt> {
    let d = dist(at, goal);
    if d < ARRIVE {
        return None;
    }
    let s = SPEED.min(d);
    Some(clamp(map, (at.0 + (goal.0 - at.0) / d * s, at.1 + (goal.1 - at.1) / d * s)))
}

/// [`step_on`] by the Rift's walls: (the step, stopped at a wall). A step onto a spot no hero can stand on (`ok` says no:
/// the runtime's `stand_ok`, always yes on the game's own map) is not taken - the dash ends there, he lands on his last
/// good spot.
pub fn step_in(map: Map, at: Pt, goal: Pt, ok: impl Fn(Pt) -> bool) -> (Option<Pt>, bool) {
    match step_on(map, at, goal) {
        Some(n) if !ok(n) => (None, true),
        n => (n, false),
    }
}

/// Ticks to pull a champion `d` away toward him (0: close enough).
pub fn pull_ticks(d: f64) -> usize {
    let far = (d - STOP).min(PULL_MAX);
    if far <= 0.0 { 0 } else { (far / PULL_SPEED as f64).ceil() as usize }
}

/// [`pull_ticks`] by the Rift's walls: the pull of the one struck at `from` toward him at `to` ends before its first spot
/// (one every `PULL_SPEED`) no hero can stand on (`ok`: the runtime's `stand_ok`, always yes on the game's own map) - a
/// champion struck beyond a wall his dash stopped at is pulled up to it, never into it.
pub fn pull_ticks_in(from: Pt, to: Pt, ok: impl Fn(Pt) -> bool) -> usize {
    let d = dist(from, to);
    let t = pull_ticks(d);
    if t == 0 {
        return 0;
    }
    let (ux, uy) = ((to.0 - from.0) / d, (to.1 - from.1) / d);
    (1..=t)
        .take_while(|&k| {
            let s = (k as f64 * PULL_SPEED as f64).min(d);
            ok((from.0 + ux * s, from.1 + uy * s))
        })
        .count()
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

#[derive(Clone, Debug, Default)]
enum Phase {
    #[default]
    Idle,
    /// 挂上 GO 的 tick。
    Wait(usize),
    /// 冲向哪里、斩中了谁、走了几步、最多几步。
    Dash(Pt, Vec<usize>, usize, usize),
}

#[derive(Clone, Default)]
struct Dash {
    phase: Phase,
    n: usize,
    /// This R's lines are written (`tally` asked once at the R line, so its LANDED line goes with it).
    shown: bool,
}

impl StablePassive for Dash {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.phase = Phase::Idle;
        if tally(sim, "spawn").is_some() {
            wlog(format!("{} SPAWN: the add-on's Yone (player {player})", head(sim, me)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.phase = Phase::Idle;
            return;
        }
        let (team, at, flag) = (e.team(), pos(&e), has_buff(&e, GO));
        if flag {
            sim.entity_remove_buff(me, GO);
            self.phase = Phase::Wait(tick);
        }
        match self.phase.clone() {
            Phase::Idle => {}
            Phase::Wait(t0) => {
                let foes: Vec<(usize, Pt, bool)> = (0..sim.entity_count())
                    .filter_map(|i| sim.entity_at(i))
                    .filter(|u| u.is_champion() && u.is_alive() && u.team() != team)
                    .map(|u| (u.id(), pos(&u), has_buff(&u, STRUCK)))
                    .collect();
                let my_r = sim.get_entity(me).map_or(0.0, |e| e.radius() as f64);
                let struck: Vec<(usize, Pt)> = foes.iter().filter(|f| f.2).map(|f| (f.0, f.1)).collect();
                if struck.is_empty() && tick < t0 + WAIT {
                    return;
                }
                let goal = last_struck(at, &struck).or_else(|| {
                    foes.iter().filter(|f| dist(at, f.1) <= REACH)
                        .min_by(|a, b| dist(at, a.1).total_cmp(&dist(at, b.1))).map(|f| (f.0, f.1))
                });
                let Some((who, there)) = goal else {
                    if tally(sim, "stay").is_some() {
                        wlog(format!("{} R: nobody struck, no enemy champion in reach - stays", head(sim, me)));
                    }
                    self.phase = Phase::Idle;
                    return;
                };
                let their_r = sim.get_entity(who).map_or(0.0, |e| e.radius() as f64);
                let map = map_here(sim);
                let back = back_of(my_r, their_r);
                // 峡谷上落点进了墙（离墙比峡谷的寻路允许的近）：LAND_REACH 内最近能站的地方（游戏自己的地图上原样）
                let land = landing_in(map, at, there, back, |q| stand_spot(map, q, LAND_REACH));
                self.n += 1;
                self.shown = tally(sim, "R").is_some();
                if self.shown {
                    let off = dist(land, behind_on(map, at, there, back));
                    wlog(format!("{} R #{}: {} struck, lands behind #{who} {:.0} away{}{}", head(sim, me), self.n, struck.len(),
                                 dist(at, land), if struck.is_empty() { " (nobody struck: nearest)" } else { "" },
                                 if off > 0.5 { format!(" (moved {off:.0} off the Rift's wall)") } else { String::new() }));
                }
                for (id, _) in &struck {
                    sim.entity_remove_buff(*id, STRUCK);
                }
                self.phase = Phase::Dash(land, struck.iter().map(|s| s.0).collect(), 0, dash_budget(dist(at, land)));
                self.dash(sim, me, at);
            }
            Phase::Dash(..) => self.dash(sim, me, at),
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.phase = Phase::Idle;
    }
}

impl Dash {
    /// One dash tick; at the end, pull the struck toward him.
    fn dash(&mut self, sim: &mut StableSim<'_>, me: usize, at: Pt) {
        let Phase::Dash(goal, struck, steps, budget) = &mut self.phase else { return };
        let map = map_here(sim);
        // 峡谷上下一步站不住（离墙比峡谷的寻路允许的近）就冲到这里为止，停在上一个能站的地方（游戏自己的地图上 stand_ok
        // 总是 true）
        let (next, walled) = step_in(map, at, *goal, |q| stand_ok(map, q));
        if let Some(next) = next {
            if *steps < *budget && sim.entity_set_pos(me, next.0.round() as u64, next.1.round() as u64) {
                *steps += 1;
                return;
            }
        }
        let landed = sim.get_entity(me).map(|e| pos(&e)).unwrap_or(at);
        let mut pulled = 0;
        for id in struck.iter() {
            let Some(there) = sim.get_entity(*id).filter(|u| u.is_alive()).map(|u| pos(&u)) else { continue };
            // 峡谷上拉到墙前为止（拉的每一步都要能站：他停在墙这边时，墙那边被斩中的人不被拉进墙里）
            let t = pull_ticks_in(there, landed, |q| stand_ok(map, q));
            if t > 0 && sim.entity_pull(me, *id, PULL_SPEED, t) {
                pulled += 1;
            }
        }
        if self.shown {
            wlog(format!("{} R #{} LANDED after {steps} steps ({:.0} off the spot{}), pulled {pulled} of {}", head(sim, me),
                         self.n, dist(landed, *goal), if walled { ", stopped at the Rift's wall" } else { "" }, struck.len()));
        }
        self.phase = Phase::Idle;
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Yone's R lands behind the last champion struck and pulls them) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:dash"), Dash::default());
    host.log(LogLevel::Info, "league_yone_r v1 loaded (Fate Sealed lands behind the last champion struck).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;
    use game_places::terrain::Walls;

    #[test]
    fn he_lands_behind_the_farthest_struck() {
        let s = [(1, (30_000.0, 0.0)), (2, (70_000.0, 0.0)), (3, (50_000.0, 1_000.0))];
        assert_eq!(last_struck((0.0, 0.0), &s).map(|x| x.0), Some(2));
        // past his body (and Yone's): the engine pushes apart champions whose centres are inside the other's radius
        let back = back_of(9_000.0, 10_000.0);
        assert_eq!(back, 10_000.0 + BEHIND_GAP);
        assert_eq!(back_of(0.0, 0.0), BODY + BEHIND_GAP);
        let b = behind((0.0, 0.0), (70_000.0, 0.0), back);
        assert!((b.0 - 81_000.0).abs() < 1e-6 && b.1.abs() < 1e-6);
    }

    #[test]
    fn dash_steps_and_pulls() {
        assert_eq!(step((0.0, 0.0), (5_000.0, 0.0)), Some((5_000.0, 0.0)));
        assert_eq!(step((5_000.0, 0.0), (5_000.0, 0.0)), None);
        // pushed 1000 off the spot by the engine: there, not snapped back every tick
        assert_eq!(step((4_000.0, 0.0), (5_000.0, 0.0)), None);
        // the steps it needs and 2 more, never past STEP_MAX
        assert_eq!(dash_budget(81_000.0), 9);
        assert_eq!(dash_budget(500_000.0), STEP_MAX);
        assert_eq!(pull_ticks(12_000.0), 0);
        assert_eq!(pull_ticks(20_000.0), 4);
        assert_eq!(pull_ticks(60_000.0), 8);
    }

    #[test]
    fn on_the_rift_he_lands_and_dashes_past_960000() {
        let back = back_of(0.0, 0.0);
        // the last one struck by the game's own far edge: there he lands on its edge, on the Rift behind him
        let (me, last) = ((900_000.0, 400_000.0), (955_000.0, 400_000.0));
        assert_eq!(behind(me, last, back), (MAP - 1.0, 400_000.0));
        assert_eq!(behind_on(Map::Rift, me, last, back), (955_000.0 + back, 400_000.0));
        // the Rift's own edge holds him
        let rift = Map::Rift.extent();
        assert_eq!(behind_on(Map::Rift, (rift - 60_000.0, 5.0), (rift - 5_000.0, 5.0), back), (rift - 1.0, 5.0));
        // a dash step out past 960000
        assert_eq!(step((955_000.0, 0.0), (1_100_000.0, 0.0)), Some((MAP - 1.0, 0.0)));
        assert_eq!(step_on(Map::Rift, (955_000.0, 0.0), (1_100_000.0, 0.0)), Some((955_000.0 + SPEED, 0.0)));
    }

    /// 2026-11-10 (the user on the Rift: 「有的地方会走路卡住」): the landing, the dash's steps and the pull went into the
    /// Rift's walls and left champions standing stuck there. A piece of the Rift as `stand_ok` / `stand_spot` see it with
    /// the walls file (`rift_ground`): cells of 60000/11, 40 x 40 from (1100000, 1100000) - past the game's own 960000 -
    /// columns 20 and 21 wall, grown by one cell (`padded`): no hero stands at x 1203636..1225455.
    #[test]
    fn on_the_rift_the_landing_the_dash_and_the_pull_keep_off_its_walls() {
        let e = Map::Rift.extent();
        let row = format!("{}##{}", ".".repeat(20), ".".repeat(18));
        let g = Walls::from_rows(&vec![row.as_str(); 40], 60_000.0 / 11.0, (1_100_000.0, 1_100_000.0), (e, e)).padded();
        let ok = |q: Pt| !g.is_wall(q.0, q.1);
        let spot = |q: Pt| g.nearest_open(q, LAND_REACH).unwrap_or(q);
        let y = 1_200_000.0;
        let (west, east) = (1_100_000.0 + 19.0 * 60_000.0 / 11.0, 1_100_000.0 + 23.0 * 60_000.0 / 11.0);
        assert!(ok((1_150_000.0, y)) && ok((east + 1.0, y)) && !ok((west + 1.0, y)) && !ok((east - 1.0, y)));
        // the last one struck by the wall: behind him is in it, so he lands on the nearest spot off it (this side)
        let back = back_of(0.0, 0.0);
        let (me, last) = ((1_150_000.0, y), (1_195_000.0, y));
        assert!(!ok(behind_on(Map::Rift, me, last, back)), "behind him (1206000) is in the grown wall");
        let land = landing_in(Map::Rift, me, last, back, spot);
        assert!(ok(land) && (land.0 - (west - 1.0)).abs() < 0.01 && land.1 == y, "{land:?}");
        // and dashes all the way there
        let (mut at, mut steps) = (me, 0);
        loop {
            match step_in(Map::Rift, at, land, ok) {
                (Some(next), false) => (at, steps) = (next, steps + 1),
                (None, walled) => {
                    assert!(!walled);
                    break;
                }
                x => panic!("{x:?}"),
            }
        }
        assert_eq!((at, steps), (land, 5));
        // a landing beyond the wall (none near enough to move it off): the dash ends on his last good spot, never in it
        let goal = (1_260_000.0, y);
        assert_eq!(step_in(Map::Rift, (1_180_000.0, y), goal, ok), (Some((1_192_000.0, y)), false));
        assert_eq!(step_in(Map::Rift, (1_192_000.0, y), goal, ok), (None, true), "1204000 is in the grown wall");
        assert_eq!(step_in(Map::Rift, (1_192_000.0, y), goal, |_| true), (Some((1_204_000.0, y)), false));
        // one struck beyond it is pulled up to it (7 of the 8 ticks: the 8th spot, 1224000, is in it), not into it
        let landed = (1_192_000.0, y);
        assert_eq!(pull_ticks(dist(landed, (1_240_000.0, y))), 8);
        assert_eq!(pull_ticks_in((1_240_000.0, y), landed, ok), 7);
        assert!(ok((1_240_000.0 - 7.0 * PULL_SPEED as f64, y)));
        // one struck on his side: the whole pull
        assert_eq!(pull_ticks_in((1_150_000.0, y), landed, ok), pull_ticks(42_000.0));
        // the game's own map: the landing, the steps and the pulls as before (stand_ok / stand_spot never change them)
        let native = |q: Pt| stand_ok(Map::Native, q);
        let (me, last) = ((900_000.0, 400_000.0), (955_000.0, 400_000.0));
        assert_eq!(landing_in(Map::Native, me, last, back, |q| stand_spot(Map::Native, q, LAND_REACH)), behind(me, last, back));
        assert_eq!(step_in(Map::Native, (0.0, 0.0), (5_000.0, 0.0), native), (step((0.0, 0.0), (5_000.0, 0.0)), false));
        assert_eq!(step_in(Map::Native, (955_000.0, 0.0), (1_100_000.0, 0.0), native), (Some((MAP - 1.0, 0.0)), false));
        assert_eq!(step_in(Map::Native, (4_000.0, 0.0), (5_000.0, 0.0), native), (None, false));
        for d in [12_000.0, 20_000.0, 60_000.0] {
            assert_eq!(pull_ticks_in((d, 0.0), (0.0, 0.0), native), pull_ticks(d));
        }
    }
}
