//! 纳尔附加包（用户 2026-10-20：附加包「要」；「还有r墙眩晕别人的机制也要做」）。主包保持纯数据；`mod.override_info`
//! 把主包的纳尔换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_gnar.py 的 `native=1` 生成：技能、时机一字
//! 不改，只有大招的击退和眩晕换成本包的原生效果、加上本包的被动），本包补数据做不到的两件事（英雄联盟的规则）：
//!
//! - **整身变巨型**（`view.rs`）：巨型纳尔时站着、跑着、挨打、阵亡也是巨型（奈德丽附加包的做法）。
//! - **呐啊！撞墙才晕**（原生效果 `league_gnar:wall`，打中每个敌人时；被动 `league_gnar:slam`）：英雄联盟把所有人往**同一个
//!   方向**掀飞，玩家挑能把人砸上墙的方向。本包每次在 16 个方向里挑一个：被掀出 `R_PUSH` 的路上会撞墙的人最多（敌方英雄
//!   一个顶小兵十个），所有人都往那边飞；哪个方向都没墙就照常从他身边掀开。撞墙的人推到墙边，到的那一刻（被动看他身上的
//!   `league_gnar_r_due` 到期）眩晕 `R_STUN` tick，再受大招伤害的 `R_WALL - 100`%（合计 `R_WALL`%）；没撞墙的不晕。
//!   墙：卡蜜尔附加包的内置墙格（波比、杰斯、巴德附加包同样用它），5v5 地图另加四边。主包：从他身边击退，人人眩晕。
//!
//! 数字是主包参数表 P 的同名项（小写）；`make_override.py` 生成副本时核对，不一致就停。本包不按任何技能键。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_gnar.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `THROW`（往哪边掀、几个会撞墙）、`WALL`（撞墙眩晕），限了条数；还有整身变巨型的显示统计。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;
pub mod view;

const ID: &str = "league_gnar";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_gnar") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 巨型的 buff（主包数据：变身 mega_t tick）和巨型刚结束、还没播变回动作的标记。
pub const MEGA: [&str; 2] = ["league_gnar_mg", "league_gnar_was_mg"];

/// 呐啊！：伤害（固定、攻击力 %）、眩晕 tick、撞墙时合计的伤害 %、范围、掀飞的距离和速度。
pub const R_DMG: usize = 170;
pub const R_RATIO: usize = 60;
pub const R_STUN: usize = 70;
pub const R_WALL: usize = 150;
pub const R_R: usize = 30_000;
pub const R_PUSH: usize = 30_000;
pub const R_PUSH_V: usize = 3_000;
/// 挑方向时试的方向数；敌方英雄撞墙顶几个小兵。
pub const DIRS: usize = 16;
pub const CHAMP_WEIGHT: usize = 10;
/// 推到墙边时离墙留的距离（身体半径另算）。
pub const WALL_GAP: f64 = 1_000.0;
/// 5v5 地图四边的可走范围（卡蜜尔附加包量的）。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_GNAR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_gnar.log");
        }
    }
    PathBuf::from("league_gnar.log")
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

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

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

// ===================== 规则（单元测试用） =====================

pub type Pt = (f64, f64);

fn n(name: &str) -> String {
    format!("{ID}_{name}")
}

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn unit(v: Pt) -> Option<Pt> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

/// 墙格的边长（世界单位）和查墙的步长。
pub const CELL: f64 = 32_000.0;
pub const STEP: f64 = 1_000.0;

/// 地图的墙格（卡蜜尔附加包的内置地图）；5v5 地图另加四边。
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
    pub bounds: Option<(f64, f64, f64, f64)>,
}

impl Grid {
    pub fn from_rows(rows: &[&str], bounds: Option<(f64, f64, f64, f64)>) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(), bounds }
    }

    /// 0 = 5v5（四边也是墙），1 = 单线，2 = 死斗。
    pub fn builtin() -> [Grid; 3] {
        [
            Grid::from_rows(&maps::MOBA, Some(MOBA_BOUNDS)),
            Grid::from_rows(&maps::SINGLE_LANE, None),
            Grid::from_rows(&maps::DEATH_MATCH, None),
        ]
    }

    /// 世界坐标落在墙里吗（地图外、5v5 的四边外都算墙）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return true;
        }
        if let Some((x0, y0, x1, y1)) = self.bounds {
            if x < x0 || y < y0 || x > x1 || y > y1 {
                return true;
            }
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(true)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }
}

/// 当前对局的地图：英雄站进墙里最少的那张（同波比、杰斯、巴德附加包）。
pub fn current(grids: &[Grid], champions: &[Pt]) -> Option<usize> {
    grids
        .iter()
        .enumerate()
        .min_by_key(|(_, g)| {
            let inside = champions.iter().filter(|&&(x, y)| g.is_wall(x, y)).count();
            (inside, std::cmp::Reverse(g.walls()))
        })
        .map(|(i, _)| i)
}

/// 从 `at` 沿 `dir` 掀 `reach`（身体半径 `body`）：`Some(飞多远)` 路上撞墙（推到墙边为止），`None` 一路没墙。
pub fn wall_travel(grid: &Grid, at: Pt, dir: Pt, reach: f64, body: f64) -> Option<f64> {
    let mut s = STEP;
    while s <= reach + body + 0.5 {
        if grid.is_wall(at.0 + dir.0 * s, at.1 + dir.1 * s) {
            return Some((s - body - WALL_GAP).max(0.0));
        }
        s += STEP;
    }
    None
}

/// 范围里的一个敌人：位置、身体半径、是不是英雄。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub at: Pt,
    pub body: f64,
    pub champion: bool,
}

/// 掀飞的方向：DIRS 个方向里会撞墙的人最多的那个（英雄算 CHAMP_WEIGHT 个），返回 (方向, 分数)；哪个方向都没人撞墙就 None。
pub fn best_dir(grid: &Grid, foes: &[Foe], reach: f64) -> Option<(Pt, usize)> {
    let mut best: Option<(Pt, usize)> = None;
    for k in 0..DIRS {
        let a = k as f64 * std::f64::consts::TAU / DIRS as f64;
        let d = (a.cos(), a.sin());
        let score: usize = foes
            .iter()
            .filter(|f| wall_travel(grid, f.at, d, reach, f.body).is_some())
            .map(|f| if f.champion { CHAMP_WEIGHT } else { 1 })
            .sum();
        if score > 0 && best.is_none_or(|(_, s)| score > s) {
            best = Some((d, score));
        }
    }
    best
}

/// 撞墙时补的伤害：大招伤害的 R_WALL - 100 %（攻击力 `ad`）。
pub fn wall_damage(ad: usize) -> usize {
    (R_DMG + R_RATIO * ad / 100) * R_WALL.saturating_sub(100) / 100
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn cc_immune(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.cc_immune))
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

fn pt(p: Pt) -> String {
    format!("({:.0}, {:.0})", p.0, p.1)
}

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

/// 猜地图用的点：所有活着的单位（英雄、小兵、野怪、塔……）。只看英雄的话，大家都站在三张图都空着的那条斜带上
/// （中路、两边泉水）时打平，平手偏向墙多的单线 / 死斗图，5v5 就猜错了（2026-11-01 复查：波比的 R 有 7 次退回击退）；
/// 5v5 边路的兵和野区的野怪几乎一直在，正好落在另两张图的墙里。
fn unit_points(sim: &StableSim<'_>) -> Vec<Pt> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_alive())
        .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
        .collect()
}

fn grid_now(sim: &StableSim<'_>) -> Option<Grid> {
    let grids = Grid::builtin();
    let i = current(&grids, &unit_points(sim))?;
    grids.into_iter().nth(i)
}

/// 强制位移 `target` 沿 `dir` 走 `len`；返回 tick 数。
fn shove(sim: &mut StableSim<'_>, target: usize, dir: Pt, len: f64) -> usize {
    let ticks = ((len / R_PUSH_V as f64).ceil() as usize).max(1);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (dir.0 * len).round() as i64;
    cc.dy = (dir.1 * len).round() as i64;
    cc.speed = R_PUSH_V as u64;
    sim.apply_cc(target, &cc);
    sim.add_buff(target, &BuffV1::timed(&n("r_push"), ticks + 2));
    ticks
}

/// 他身边大招范围里的敌人（塔不算）。
fn foes_round(sim: &StableSim<'_>, me: usize) -> Vec<Foe> {
    let Some((team, at)) = sim.get_entity(me).map(|e| (e.team(), (e.pos().0 as f64, e.pos().1 as f64))) else {
        return Vec::new();
    };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .map(|u| Foe { at: (u.pos().0 as f64, u.pos().1 as f64), body: u.radius() as f64, champion: u.is_champion() })
        .filter(|f| dist(f.at, at) <= R_R as f64 + f.body)
        .collect()
}

// ===================== 原生效果 =====================

/// 呐啊！打中一个敌人：所有人往同一个最能撞墙的方向掀（每个目标算一次，位置在这一 tick 里不变，算出来都一样）；撞墙的
/// 推到墙边、记下到的时刻，没撞墙的照常推开；哪个方向都没墙就从他身边掀开。
fn wall(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some(body) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.radius() as f64) else {
        return;
    };
    if cc_immune(sim, target) {
        return;
    }
    let (Some(him), Some(at)) = (pos(sim, me), pos(sim, target)) else { return };
    let reach = R_PUSH as f64;
    let Some(grid) = grid_now(sim) else {
        sim.entity_knockback(me, target, R_PUSH_V, R_PUSH / R_PUSH_V);
        return;
    };
    let foes = foes_round(sim, me);
    let pick = best_dir(&grid, &foes, reach);
    let dir = pick.map(|(d, _)| d).or_else(|| unit((at.0 - him.0, at.1 - him.1))).unwrap_or((1.0, 0.0));
    match wall_travel(&grid, at, dir, reach, body) {
        Some(len) => {
            let ticks = if len >= 1.0 { shove(sim, target, dir, len) } else { 0 };
            sim.add_buff(target, &BuffV1::timed(&n("r_due"), ticks.max(1)));
            sim.add_buff(target, &BuffV1::timed(&n("r_go"), ticks + 4));
            sim.entity_remove_buff(me, &n("r_watch"));
            sim.add_buff(me, &BuffV1::timed(&n("r_watch"), ticks + 8));
            if let Some(k) = counted("throw") {
                wlog(format!("{} THROW #{target} at {} toward ({:.2}, {:.2}): a wall {len:.0} away, slams in {ticks} ticks #{k}",
                             head(sim, me), pt(at), dir.0, dir.1));
            }
        }
        None => {
            shove(sim, target, dir, reach);
            if let Some(k) = counted("throw") {
                wlog(format!("{} THROW #{target} at {} toward ({:.2}, {:.2}): no wall within {reach:.0}{} #{k}", head(sim, me),
                             pt(at), dir.0, dir.1, if pick.is_some() { " (the others' way)" } else { ", none for anyone: away from him" }));
            }
        }
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 被动：撞墙 =====================

#[derive(Clone, Default)]
struct Slam;

impl StablePassive for Slam {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        if !has_buff(sim, me, &n("r_watch")) {
            return;
        }
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let arrived: Vec<usize> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && !u.is_tower())
            .map(|u| u.id())
            .collect::<Vec<_>>()
            .into_iter()
            .filter(|&id| has_buff(sim, id, &n("r_go")) && !has_buff(sim, id, &n("r_due")))
            .collect();
        for foe in arrived {
            sim.entity_remove_buff(foe, &n("r_go"));
            if !sim.get_entity(foe).is_some_and(|e| e.is_alive()) {
                continue;
            }
            let ad = sim.get_entity(me).map_or(0, |e| e.stat().attack);
            let dmg = wall_damage(ad);
            sim.deal_damage_typed(me, foe, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
            if !cc_immune(sim, foe) {
                sim.apply_cc(foe, &CcV1::stun(R_STUN as u64));
            }
            if let Some(k) = counted("wall") {
                wlog(format!("{} WALL #{foe} slammed into the wall: {dmg} more damage, stunned {R_STUN} ticks #{k}", head(sim, me)));
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
        "=== {ID} v{VERSION} (Gnar: the whole-body Mega, GNAR! stuns only into a wall) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_effect(format!("{ID}:wall"), Step(wall));
    module.add_native_passive(format!("{ID}:slam"), Slam);
    host.log(LogLevel::Info, "league_gnar loaded (whole-body Mega, GNAR! wall stun).");
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

    fn foe(x: f64, y: f64, champion: bool) -> Foe {
        Foe { at: (x, y), body: 6_000.0, champion }
    }

    #[test]
    fn everyone_goes_the_way_that_slams_most_into_a_wall() {
        let grids = Grid::builtin();
        let g = &grids[0];
        // near the 5v5 map's left edge: left is the wall for both
        let left = [foe(45_000.0, 480_000.0, true), foe(50_000.0, 470_000.0, false)];
        let (d, s) = best_dir(g, &left, R_PUSH as f64).expect("the edge is a wall");
        assert!(d.0 < -0.5, "{d:?}");
        assert_eq!(s, CHAMP_WEIGHT + 1);
        // open ground in the middle of the river: no way slams anyone
        assert_eq!(best_dir(g, &[foe(480_000.0, 480_000.0, true)], R_PUSH as f64), None);
    }

    #[test]
    fn a_champion_counts_ten_minions() {
        let grids = Grid::builtin();
        let g = &grids[0];
        // the champion by the left edge, three minions by the bottom-right edge: the champion's way wins
        let foes = [foe(45_000.0, 480_000.0, true), foe(915_000.0, 480_000.0, false), foe(915_000.0, 470_000.0, false),
                    foe(915_000.0, 490_000.0, false)];
        let (d, _) = best_dir(g, &foes, R_PUSH as f64).unwrap();
        assert!(d.0 < -0.5, "{d:?}");
    }

    #[test]
    fn the_wall_adds_half_the_ult() {
        assert_eq!(wall_damage(0), R_DMG / 2);
        assert_eq!(wall_damage(200), (R_DMG + R_RATIO * 2) / 2);
    }

    #[test]
    fn names_fit_a_buff() {
        for s in ["r_push", "r_due", "r_go", "r_watch"] {
            assert!(n(s).len() <= BUFF_NAME_CAP);
        }
    }

    #[test]
    fn the_copy_uses_the_natives_and_the_numbers() {
        let copy = include_str!("../override/league_gnar.data_champion");
        for r in ["league_gnar:wall", "league_gnar:slam"] {
            assert!(copy.contains(r), "the copy never uses {r}");
        }
        for (k, v) in [("r_dmg", R_DMG), ("r_ratio", R_RATIO), ("r_stun", R_STUN), ("r_wall", R_WALL), ("r_r", R_R),
                       ("r_push", R_PUSH), ("r_push_v", R_PUSH_V)] {
            assert!(copy.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        assert!(!copy.contains("\"type\": \"Knockback\""), "the copy still throws in data");
        assert!(copy.contains("\"name\": \"league_gnar_mg\""), "the copy never lays the Mega buff");
    }
}
