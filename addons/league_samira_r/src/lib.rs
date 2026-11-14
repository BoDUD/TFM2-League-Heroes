//! 莎弥拉附加包：R「炼狱扳机」照英雄联盟边走边射（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补
//! 附加包」；做 R 时用户选的是「这个不能走的话可以改RUST文件」）。
//!
//! 主包是纯数据：R 的旋转是施法动作，动作期间引擎不让她走，所以原地旋转 2 秒。英雄联盟的 R 期间能走，玩家追着残血的人
//! 走、把更多的人留在枪口里。本包不换 R 的数据（伤害、枪、旋转动作都是主包的），只加一个被动：
//!
//! - **被动 `league_samira_r:walk`**：她身上有主包 R 的 `R_ON`（120 tick）时，每 tick 朝 `CHASE` 内生命 + 护盾最少的敌方
//!   英雄走一步（`entity_set_pos`），走到 `KEEP` 内就站住；被硬控（眩晕、击飞、禁锢、嘲讽、恐惧、魅惑、强制位移）时不走。
//!   一步多长：平时她走路时每 tick 挪的距离（最近 `SAMPLES` 次的中位数，冲刺、传送不算），没量到就是 `STEP`。
//!   每一步夹在这一场的地图里（2026-11-10，`game_places::terrain::map_of_sim`：游戏自己的 960000 见方，Rin 的召唤师峡谷
//!   1614545 见方；以前一律按 960000，峡谷上过了 960000 就被夹回半张图的边）。峡谷上每一步还要落在能站的地方
//!   （`game_places::terrain::stand_ok`：峡谷的墙往外长一格，和作者的寻路一致）：站不住的那一步不走、记一步被拒，和撞墙
//!   一样停在上一个能站的地方，从不挪进墙里（用户 2026-11-10：「有的地方会走路卡住」）。没有墙体文件时只有地图边。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_samira_r.log`。

use std::collections::VecDeque;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{map_of_sim, rift_status, stand_ok, Map};
use mod_api_stable::*;

const ID: &str = "league_samira_r";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_samira_r") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const HERO: &str = "league_samira";
/// 主包 R 期间她身上的 buff（120 tick，生命偷取 40%）。
pub const R_ON: &str = "league_samira_r_on";
/// 追谁：这么远内的敌方英雄。
pub const CHASE: f64 = 90_000.0;
/// 走到离他这么近就站住（主包 R 的枪打 55000 内）。
pub const KEEP: f64 = 30_000.0;
/// 没量到她平时一步多长时用的步长。
pub const STEP: f64 = 550.0;
/// 一 tick 挪了超过这么多就是冲刺、传送，不算走路。
pub const DASH: f64 = 1_500.0;
pub const SAMPLES: usize = 120;
/// 游戏自己的 5v5 地图边长；峡谷的看 `Map::extent`。
const MAP: f64 = 960_000.0;
const HARD_CC: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                                CcKindV1::Charm, CcKindV1::ForceMove];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SAMIRA_R_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_samira_r.log");
        }
    }
    PathBuf::from("league_samira_r.log")
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

/// 这次启动已经在日志里说过峡谷了。
static RIFT_TOLD: AtomicBool = AtomicBool::new(false);

/// 这一场的地图；第一次碰到峡谷（一次启动）时日志写一行。
fn map_here(sim: &StableSim<'_>) -> Map {
    let map = map_of_sim(sim);
    if map == Map::Rift && !RIFT_TOLD.swap(true, Ordering::Relaxed) {
        wlog(format!("== Rift: her steps while R spins are kept on the Rift's {:.0} square (not the game's own {MAP:.0}), \
                      a step onto the Rift's walls is refused (stand_ok); {} ==", map.extent(), rift_status()));
    }
    map
}

// ===================== 走一步 =====================

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// Her walking step: the median of the moves measured (0 and dashes left out), or `STEP`.
pub fn step_of(moves: &VecDeque<f64>) -> f64 {
    let mut v: Vec<f64> = moves.iter().copied().collect();
    if v.len() < 10 {
        return STEP;
    }
    v.sort_by(|a, b| a.total_cmp(b));
    v[v.len() / 2]
}

/// [`toward_on`] on the game's own map.
pub fn toward(at: Pt, goal: Pt, step: f64) -> Option<Pt> {
    toward_on(Map::Native, at, goal, step)
}

/// One step from `at` toward `goal`, stopping `KEEP` short of it (None: close enough already), kept on `map`.
pub fn toward_on(map: Map, at: Pt, goal: Pt, step: f64) -> Option<Pt> {
    let d = dist(at, goal);
    if d <= KEEP {
        return None;
    }
    let s = step.min(d - KEEP);
    let next = (at.0 + (goal.0 - at.0) / d * s, at.1 + (goal.1 - at.1) / d * s);
    let e = map.extent();
    Some((next.0.clamp(0.0, e - 1.0), next.1.clamp(0.0, e - 1.0)))
}

/// [`toward_on`] by the Rift's walls: (the step, refused). A step onto a spot no hero can stand on (`ok` says no: the
/// runtime's `stand_ok`, always yes on the game's own map) is not taken and counts as refused, like a wall the engine
/// stops her at: she stays on her last good spot.
pub fn toward_in(map: Map, at: Pt, goal: Pt, step: f64, ok: impl Fn(Pt) -> bool) -> (Option<Pt>, bool) {
    match toward_on(map, at, goal, step) {
        Some(n) if !ok(n) => (None, true),
        n => (n, false),
    }
}

/// Whom she walks at: the enemy champion within `CHASE` with the least health + shield (`foes`: id, at, hp + shield).
pub fn prey(at: Pt, foes: &[(usize, Pt, usize)]) -> Option<(usize, Pt)> {
    foes.iter().filter(|f| dist(at, f.1) <= CHASE).min_by_key(|f| f.2).map(|f| (f.0, f.1))
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn hard_cc(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
}

/// The R DONE line's text after its head: the n-th spin, (steps, how far, refused), her step, and whether she died in it
/// (0.1.3: a spin her death ended had no line at all).
pub fn done_text(n: usize, (steps, far, refused): (usize, f64, usize), step: f64, died: bool) -> String {
    format!("R #{n} DONE: walked {far:.0} in {steps} steps ({refused} refused), step {step:.0}{}",
            if died { " - she died mid-spin" } else { "" })
}

#[derive(Clone, Default)]
struct Walk {
    last: Option<Pt>,
    moves: VecDeque<f64>,
    /// 这一次 R：走了几步、多远、几步被拒（撞墙）。
    spin: Option<(usize, f64, usize)>,
    n: usize,
    /// Her unit (on_dead is given the player).
    me: usize,
}

impl Walk {
    /// The spin over: its R DONE line (0.1.3: also when she dies in it).
    fn done(&mut self, sim: &StableSim<'_>, me: usize, died: bool) {
        let Some(spin) = self.spin.take() else { return };
        self.n += 1;
        if self.n <= 80 || self.n % 25 == 0 {
            wlog(format!("{} {}", head(sim, me), done_text(self.n, spin, step_of(&self.moves), died)));
        }
    }
}

impl StablePassive for Walk {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.last = None;
        self.spin = None;
        wlog(format!("{} SPAWN: the add-on's Samira (player {player})", head(sim, me)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.last = None;
            self.done(sim, me, true);
            return;
        }
        let at = (e.pos().0 as f64, e.pos().1 as f64);
        let (team, spinning, held) = (e.team(), has_buff(&e, R_ON), hard_cc(&e));
        if !spinning {
            self.done(sim, me, false);
            if let Some(l) = self.last {
                let d = dist(l, at);
                if d > 0.5 && d < DASH {
                    self.moves.push_back(d);
                    if self.moves.len() > SAMPLES {
                        self.moves.pop_front();
                    }
                }
            }
            self.last = Some(at);
            return;
        }
        self.last = None;
        let spin = self.spin.get_or_insert((0, 0.0, 0));
        if held {
            return;
        }
        let foes: Vec<(usize, Pt, usize)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.is_alive() && u.team() != team && u.is_targetable())
            .map(|u| (u.id(), (u.pos().0 as f64, u.pos().1 as f64), u.hp().0 + u.shield()))
            .collect();
        let Some((_, goal)) = prey(at, &foes) else { return };
        let map = map_here(sim);
        // 峡谷上这一步站不住（离墙比峡谷的寻路允许的近）就不走、记一步被拒，停在原地（游戏自己的地图上 stand_ok 总是 true）
        let (next, walled) = toward_in(map, at, goal, step_of(&self.moves), |q| stand_ok(map, q));
        if walled {
            spin.2 += 1;
            return;
        }
        let Some(next) = next else { return };
        if sim.entity_set_pos(me, next.0.round() as u64, next.1.round() as u64) {
            spin.0 += 1;
            spin.1 += dist(at, next);
        } else {
            spin.2 += 1;
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.last = None;
        // a spin her death ends still gets its R DONE line (0.1.3; her update does not run once she is dead)
        let me = self.me;
        self.done(sim, me, true);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Samira walks while her R spins) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:walk"), Walk::default());
    host.log(LogLevel::Info, "league_samira_r v1 loaded (Samira walks while Inferno Trigger spins).");
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
    fn she_walks_at_the_weakest_and_stops_in_range() {
        let foes = [(1, (50_000.0, 0.0), 900), (2, (60_000.0, 0.0), 300), (3, (200_000.0, 0.0), 10)];
        assert_eq!(prey((0.0, 0.0), &foes).map(|p| p.0), Some(2));
        let n = toward((0.0, 0.0), (60_000.0, 0.0), 550.0).unwrap();
        assert!((n.0 - 550.0).abs() < 1e-6 && n.1 == 0.0);
        assert_eq!(toward((40_000.0, 0.0), (60_000.0, 0.0), 550.0), None);
        let n = toward((29_800.0, 0.0), (60_000.0, 0.0), 550.0).unwrap();
        assert!((n.0 - 30_000.0).abs() < 1e-6);
    }

    #[test]
    fn on_the_rift_she_walks_on_past_960000() {
        // stepping out past the game's own edge: there it holds her at 959999, the Rift is that much bigger
        let (at, goal) = ((959_800.0, 500_000.0), (1_100_000.0, 500_000.0));
        assert_eq!(toward(at, goal, 550.0), Some((MAP - 1.0, 500_000.0)));
        let n = toward_on(Map::Rift, at, goal, 550.0).unwrap();
        assert!((n.0 - 960_350.0).abs() < 1e-6 && n.1 == 500_000.0, "{n:?}");
        // the Rift's own edge holds her
        let edge = Map::Rift.extent() - 1.0;
        assert_eq!(toward_on(Map::Rift, (edge - 100.0, 10.0), (edge + 90_000.0, 10.0), 550.0), Some((edge, 10.0)));
    }

    /// 2026-11-10 (the user on the Rift: 「有的地方会走路卡住」): her R walk stepped her into the Rift's walls and she stood
    /// stuck there. A piece of the Rift as `stand_ok` sees it with the walls file (`!is_wall` on `rift_ground`): cells of
    /// 60000/11, 40 x 40 from (1100000, 1100000), columns 20 and 21 wall, grown by one cell (`padded`): no hero stands at x
    /// 1203636..1225455.
    #[test]
    fn on_the_rift_a_step_into_its_walls_is_refused() {
        let e = Map::Rift.extent();
        let row = format!("{}##{}", ".".repeat(20), ".".repeat(18));
        let g = Walls::from_rows(&vec![row.as_str(); 40], 60_000.0 / 11.0, (1_100_000.0, 1_100_000.0), (e, e)).padded();
        let ok = |q: Pt| !g.is_wall(q.0, q.1);
        let y = 1_200_000.0;
        // 40 ticks of her spin walking at someone across the wall: 15 steps up to her last good spot, the rest refused
        let walk = |map: Map, from: Pt, goal: Pt, ok: &dyn Fn(Pt) -> bool| {
            let (mut at, mut steps, mut refused) = (from, 0, 0);
            for _ in 0..40 {
                match toward_in(map, at, goal, 550.0, ok) {
                    (Some(next), false) => (at, steps) = (next, steps + 1),
                    (None, true) => refused += 1,
                    x => panic!("{x:?}"),
                }
            }
            (at, steps, refused)
        };
        assert_eq!(walk(Map::Rift, (1_195_000.0, y), (1_260_000.0, y), &ok), ((1_203_250.0, y), 15, 25));
        assert!(ok((1_203_250.0, y)) && !ok((1_203_800.0, y)), "the 16th step is in the grown wall");
        // past 960000 with nothing in the way, and close enough already: as before
        assert_eq!(toward_in(Map::Rift, (1_150_000.0, y), (1_100_000.0, y), 550.0, ok), (Some((1_149_450.0, y)), false));
        assert_eq!(toward_in(Map::Rift, (1_150_000.0, y), (1_170_000.0, y), 550.0, ok), (None, false));
        // the game's own map: stand_ok never refuses her - every step as before
        let native = |q: Pt| stand_ok(Map::Native, q);
        assert_eq!(walk(Map::Native, (500_000.0, 500_000.0), (565_000.0, 500_000.0), &native), ((522_000.0, 500_000.0), 40, 0));
        assert_eq!(toward_in(Map::Native, (959_800.0, 500_000.0), (1_100_000.0, 500_000.0), 550.0, native),
                   (Some((MAP - 1.0, 500_000.0)), false));
        assert_eq!(toward_in(Map::Native, (0.0, 0.0), (60_000.0, 0.0), 550.0, native), (toward((0.0, 0.0), (60_000.0, 0.0), 550.0), false));
    }

    #[test]
    fn a_spin_ended_by_her_death_still_has_its_line() {
        // 11-06's review: R DONE was missing when she died mid-spin (the spin was dropped without a line)
        assert_eq!(done_text(3, (40, 22_000.4, 2), 550.0, false), "R #3 DONE: walked 22000 in 40 steps (2 refused), step 550");
        assert_eq!(done_text(4, (7, 3_850.0, 0), 550.0, true),
                   "R #4 DONE: walked 3850 in 7 steps (0 refused), step 550 - she died mid-spin");
    }

    #[test]
    fn the_step_is_her_usual_walk() {
        let mut m = VecDeque::new();
        assert_eq!(step_of(&m), STEP);
        for d in [400.0, 410.0, 405.0, 400.0, 1200.0, 402.0, 404.0, 401.0, 403.0, 406.0, 399.0] {
            m.push_back(d);
        }
        assert_eq!(step_of(&m), 403.0);
    }
}
