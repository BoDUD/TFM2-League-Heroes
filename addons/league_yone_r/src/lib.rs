//! 永恩附加包：R「封尘绝念斩」照英雄联盟冲到最后一个被斩中的英雄身后，把斩中的人拉过来（用户 2026-10-24：「查看现在没有
//! 做附加包的英雄有明显不一样的话全部补附加包」）。
//!
//! 主包是纯数据：R 斩出直线后 `RushMoveToBack` 冲到**选中的目标**身后，不拉人。英雄联盟里他停在直线上最后一个被命中的
//! 英雄身后，被命中的人都被拉向他落脚的地方。本包：副本里的 `RushMoveToBack` 换成给永恩挂 `GO`，直线上的伤害给每个被斩中的
//! 英雄挂 `STRUCK`（3 tick）；被动 `league_yone_r:dash` 看到 `GO`：
//!
//! - 等斩中的标记出来（最多 `WAIT` tick），挑离永恩最远的那个，冲到他身后 `BEHIND`（沿永恩到他的方向），每 tick `SPEED`
//!   （主包的冲刺速度）；一个都没斩中就照主包冲到离他最近的敌方英雄身后（`REACH` 内），都没有就不动。
//! - 冲到之后把斩中的英雄拉向他（`entity_pull`，每 tick `PULL_SPEED`，最多拉 `PULL_MAX`，停在他身前 `STOP`）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yone_r.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_yone_r";
pub const GO: &str = "league_yone_r_go";
pub const STRUCK: &str = "league_yone_r_struck";
/// 主包的冲刺速度（`RushMoveToBack` 12000）和直线长度（90000）。
pub const SPEED: f64 = 12_000.0;
pub const REACH: f64 = 90_000.0;
pub const BEHIND: f64 = 6_000.0;
pub const WAIT: usize = 4;
pub const PULL_SPEED: usize = 2_000;
pub const PULL_MAX: f64 = 16_000.0;
pub const STOP: f64 = 6_000.0;
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

// ===================== 落脚点 =====================

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn clamp(p: Pt) -> Pt {
    (p.0.clamp(0.0, MAP - 1.0), p.1.clamp(0.0, MAP - 1.0))
}

/// Where he lands: `BEHIND` past `last` on the way from `me` (at `last` itself when they stand on one spot).
pub fn behind(me: Pt, last: Pt) -> Pt {
    let d = dist(me, last);
    if d < 1.0 {
        return last;
    }
    clamp((last.0 + (last.0 - me.0) / d * BEHIND, last.1 + (last.1 - me.1) / d * BEHIND))
}

/// The champion struck farthest from him (the last one the slash reaches).
pub fn last_struck(me: Pt, struck: &[(usize, Pt)]) -> Option<(usize, Pt)> {
    struck.iter().copied().max_by(|a, b| dist(me, a.1).total_cmp(&dist(me, b.1)))
}

/// One dash step toward `goal` (None: there).
pub fn step(at: Pt, goal: Pt) -> Option<Pt> {
    let d = dist(at, goal);
    if d < 1.0 {
        return None;
    }
    let s = SPEED.min(d);
    Some(clamp((at.0 + (goal.0 - at.0) / d * s, at.1 + (goal.1 - at.1) / d * s)))
}

/// Ticks to pull a champion `d` away toward him (0: close enough).
pub fn pull_ticks(d: f64) -> usize {
    let far = (d - STOP).min(PULL_MAX);
    if far <= 0.0 { 0 } else { (far / PULL_SPEED as f64).ceil() as usize }
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
    /// 冲向哪里、斩中了谁、走了几步。
    Dash(Pt, Vec<usize>, usize),
}

#[derive(Clone, Default)]
struct Dash {
    phase: Phase,
    n: usize,
}

impl StablePassive for Dash {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.phase = Phase::Idle;
        wlog(format!("{} SPAWN: the add-on's Yone (player {player})", head(sim, me)));
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
                let struck: Vec<(usize, Pt)> = foes.iter().filter(|f| f.2).map(|f| (f.0, f.1)).collect();
                if struck.is_empty() && tick < t0 + WAIT {
                    return;
                }
                let goal = last_struck(at, &struck).or_else(|| {
                    foes.iter().filter(|f| dist(at, f.1) <= REACH)
                        .min_by(|a, b| dist(at, a.1).total_cmp(&dist(at, b.1))).map(|f| (f.0, f.1))
                });
                let Some((who, there)) = goal else {
                    wlog(format!("{} R: nobody struck, no enemy champion in reach - stays", head(sim, me)));
                    self.phase = Phase::Idle;
                    return;
                };
                let land = behind(at, there);
                self.n += 1;
                if self.n <= 80 || self.n % 25 == 0 {
                    wlog(format!("{} R #{}: {} struck, lands behind #{who} {:.0} away{}", head(sim, me), self.n, struck.len(),
                                 dist(at, land), if struck.is_empty() { " (nobody struck: nearest)" } else { "" }));
                }
                for (id, _) in &struck {
                    sim.entity_remove_buff(*id, STRUCK);
                }
                self.phase = Phase::Dash(land, struck.iter().map(|s| s.0).collect(), 0);
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
        let Phase::Dash(goal, struck, steps) = &mut self.phase else { return };
        if let Some(next) = step(at, *goal) {
            if *steps < 20 && sim.entity_set_pos(me, next.0.round() as u64, next.1.round() as u64) {
                *steps += 1;
                return;
            }
        }
        let landed = sim.get_entity(me).map(|e| pos(&e)).unwrap_or(at);
        let mut pulled = 0;
        for id in struck.iter() {
            let Some(d) = sim.get_entity(*id).filter(|u| u.is_alive()).map(|u| dist(landed, pos(&u))) else { continue };
            let t = pull_ticks(d);
            if t > 0 && sim.entity_pull(me, *id, PULL_SPEED, t) {
                pulled += 1;
            }
        }
        if self.n <= 80 || self.n % 25 == 0 {
            wlog(format!("{} R #{} LANDED after {steps} steps, pulled {pulled} of {}", head(sim, me), self.n, struck.len()));
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
        "=== {ID} v{} (Yone's R lands behind the last champion struck and pulls them) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
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

    #[test]
    fn he_lands_behind_the_farthest_struck() {
        let s = [(1, (30_000.0, 0.0)), (2, (70_000.0, 0.0)), (3, (50_000.0, 1_000.0))];
        assert_eq!(last_struck((0.0, 0.0), &s).map(|x| x.0), Some(2));
        let b = behind((0.0, 0.0), (70_000.0, 0.0));
        assert!((b.0 - 76_000.0).abs() < 1e-6 && b.1.abs() < 1e-6);
    }

    #[test]
    fn dash_steps_and_pulls() {
        assert_eq!(step((0.0, 0.0), (5_000.0, 0.0)), Some((5_000.0, 0.0)));
        assert_eq!(step((5_000.0, 0.0), (5_000.0, 0.0)), None);
        assert_eq!(pull_ticks(5_000.0), 0);
        assert_eq!(pull_ticks(16_000.0), 5);
        assert_eq!(pull_ticks(60_000.0), 8);
    }
}
