//! 辛吉德附加包（用户 2026-10-23：「这个做附加包啊」——主包过肩摔的两处近似）。主包保持纯数据；`mod.override_info` 把主包的
//! 辛吉德换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_singed.py 的 `native=1` 生成：技能、时机一字不改，只有
//! 过肩摔的「拉过去 + 胶在地上就禁锢」换成本包的原生效果 `league_singed:fling`），按英雄联盟的规则做：
//!
//! - **真的过肩摔**：目标击飞 `E_FLY` tick，从他头顶飞过、落到他身后 `E_BEHIND` 远的地方（路上碰到墙就落在墙边，地图墙格同
//!   波比附加包）。击飞期间每 tick 由本包把它往落点挪一段（`entity_set_pos`：数据里击飞和拉扯同时上会被定在原地，2026-10-23 的
//!   模拟查出 0/33 移动）。主包：没有击飞，`Pull` 把目标从他身上拉过去。
//! - **落进胶里才禁锢**：落地后 `LAND_AT` 这几个 tick 看它身上有没有强力粘胶的减速（`league_singed_w_slow`，粘胶每
//!   `W_P` tick 给站在胶里的敌人挂一次）：有就是落在胶里——禁锢 `E_ROOT` tick。飞的途中每 tick 都摘掉这个减速，所以起飞前、
//!   空中经过的胶不算。主包：数据读不到单位站在哪，只要地上有他的胶（`league_singed_w_out`），被摔的就禁锢。
//!
//! 数字是主包参数表 P 的同名项（小写）；`make_override.py` 生成副本时核对，不一致就停。本包不按任何技能键。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_singed.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `FLING`（从哪摔到哪、有没有墙）、`ROOT`（落进胶里）、`MISS`（没落进胶里），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_singed";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.1";

/// 过肩摔：在空中的 tick（e_fly）、落到他身后多远（e_behind）、落进胶里禁锢的 tick（e_root）。
pub const E_FLY: usize = 16;
pub const E_BEHIND: usize = 30_000;
pub const E_ROOT: usize = 60;
/// 强力粘胶给站在胶里的敌人挂减速的间隔（w_p）。
pub const W_P: usize = 6;
/// 落地后看减速的时刻（距出手）：粘胶每 W_P tick 挂一次，三次查看覆盖一整个间隔还有余。
pub const LAND_AT: [usize; 3] = [E_FLY + 1, E_FLY + 1 + W_P / 2, E_FLY + 2 + W_P];

/// 推到墙边时离墙留的距离（身体半径另算）。
pub const WALL_GAP: f64 = 1_000.0;
/// 5v5 地图四边的可走范围（卡蜜尔附加包量的）。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SINGED_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_singed.log");
        }
    }
    PathBuf::from("league_singed.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

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

/// 地图的墙格（卡蜜尔附加包的内置地图，波比、杰斯、巴德附加包同样用它）；5v5 地图另加四边。
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

/// 当前对局的地图：英雄站进墙里最少的那张（同波比附加包）。
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

/// 从 `at` 沿 `dir` 飞 `reach`（身体半径 `body`）：`Some(飞多远)` 路上撞墙（落在墙边），`None` 一路没墙。
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

/// 过肩摔：他在 `me`、目标在 `at`，朝他飞过去、越过他再飞 `behind`：(方向, 飞多远)。两人重叠时朝 `fallback` 那边。
pub fn throw_line(me: Pt, at: Pt, behind: f64, fallback: Pt) -> (Pt, f64) {
    let dir = unit((me.0 - at.0, me.1 - at.1)).unwrap_or(fallback);
    (dir, dist(me, at) + behind)
}

/// 飞行中的一 tick：从 `cur` 朝 `end` 挪 `step`，最后一段直接落到 `end`。
pub fn fly_step(cur: Pt, end: Pt, step: f64) -> Pt {
    let left = dist(cur, end);
    match unit((end.0 - cur.0, end.1 - cur.1)) {
        Some(d) if left > step + 1.0 => (cur.0 + d.0 * step, cur.1 + d.1 * step),
        _ => end,
    }
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

fn queue(sim: &mut StableSim<'_>, stage: &str, caster: usize, input: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{stage}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
}

fn clamp_u(v: f64) -> u64 {
    v.round().max(0.0) as u64
}

// ===================== 原生效果 =====================

/// 过肩摔抓住目标（主包 E 的 `e_grab` 那一 tick）：击飞，排好每 tick 的飞行和落地后的查看。
fn fling(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some(body) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.radius() as f64) else {
        return;
    };
    if cc_immune(sim, target) {
        if let Some(k) = counted("fling") {
            wlog(format!("{} FLING #{target}: immune to crowd control, stays #{k}", head(sim, me)));
        }
        return;
    }
    let (Some(him), Some(at)) = (pos(sim, me), pos(sim, target)) else { return };
    let (dir, reach) = throw_line(him, at, E_BEHIND as f64, (1.0, 0.0));
    let wall = grid_now(sim).and_then(|g| wall_travel(&g, at, dir, reach, body));
    let len = wall.unwrap_or(reach);
    let end = (at.0 + dir.0 * len, at.1 + dir.1 * len);
    sim.entity_remove_buff(target, &n("w_slow"));
    sim.apply_cc(target, &CcV1::of_kind(CcKindV1::Airborne, E_FLY as u64));
    sim.entity_remove_buff(target, &n("e_air"));
    sim.add_buff(target, &BuffV1::timed(&n("e_air"), LAND_AT[LAND_AT.len() - 1] + 2));
    // each step carries the landing (x, y) and the take-off (dir_x, dir_y): the step length is the whole flight / E_FLY
    let step = InputTargetV1 {
        kind: InputTargetKindV1::Target.code(),
        target_id: target,
        dir_x: at.0.round() as i64,
        dir_y: at.1.round() as i64,
        x: clamp_u(end.0),
        y: clamp_u(end.1),
    };
    for k in 1..=E_FLY {
        queue(sim, "fly", me, step, k);
    }
    for (i, &k) in LAND_AT.iter().enumerate() {
        let mut look = InputTargetV1::target(target);
        look.dir_x = (i + 1 == LAND_AT.len()) as i64;   // 1 = the last look
        queue(sim, "land", me, look, k);
    }
    if let Some(k) = counted("fling") {
        let why = if wall.is_some() { format!("a wall after {len:.0}") } else { format!("{len:.0}, no wall") };
        wlog(format!("{} FLING #{target} from {} over him at {} to {} ({why}) #{k}", head(sim, me), pt(at), pt(him), pt(end)));
    }
}

/// 飞行中的一 tick：往落点挪一段；空中经过的胶不算（摘掉减速）。
fn fly(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let target = input.target_id;
    if !has_buff(sim, target, &n("e_air")) {
        return;
    }
    let Some(cur) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
    else {
        return;
    };
    sim.entity_remove_buff(target, &n("w_slow"));
    let start = (input.dir_x as f64, input.dir_y as f64);
    let end = (input.x as f64, input.y as f64);
    let to = fly_step(cur, end, dist(start, end) / E_FLY as f64);
    sim.entity_set_pos(target, clamp_u(to.0), clamp_u(to.1));
    let _ = me;
}

/// 落地后看一眼：身上有粘胶的减速就是落在胶里——禁锢。
fn land(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let target = input.target_id;
    if !has_buff(sim, target, &n("e_air")) || !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
        return;
    }
    if has_buff(sim, target, &n("w_slow")) {
        sim.entity_remove_buff(target, &n("e_air"));
        if cc_immune(sim, target) {
            return;
        }
        sim.apply_cc(target, &CcV1::of_kind(CcKindV1::Bind, E_ROOT as u64));
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&n("e_root"), me, &on, 0, 0, 0);
        sim.play_sfx(&n("e_root"), me, &on);
        if let Some(k) = counted("root") {
            wlog(format!("{} ROOT #{target}: landed in the glue at {} - rooted {E_ROOT} ticks #{k}", head(sim, me),
                         pos(sim, target).map_or("?".into(), pt)));
        }
    } else if input.dir_x == 1 {
        sim.entity_remove_buff(target, &n("e_air"));
        if let Some(k) = counted("miss") {
            wlog(format!("{} MISS #{target}: landed at {}, no glue #{k}", head(sim, me), pos(sim, target).map_or("?".into(), pt)));
        }
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Singed: Fling knocks up over him, roots in the glue) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:fling"), Step(fling));
    module.add_native_effect(format!("{ID}:fly"), Step(fly));
    module.add_native_effect(format!("{ID}:land"), Step(land));
    host.log(LogLevel::Info, "league_singed loaded (Fling over his shoulder, rooted in the glue).");
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
    fn thrown_over_him_to_behind() {
        // the target to his right, 25000 off: thrown left, 25000 to reach him + E_BEHIND past him
        let (dir, reach) = throw_line((100_000.0, 100_000.0), (125_000.0, 100_000.0), E_BEHIND as f64, (1.0, 0.0));
        assert_eq!(dir, (-1.0, 0.0));
        assert!((reach - (25_000.0 + E_BEHIND as f64)).abs() < 1e-6);
        let end = (125_000.0 + dir.0 * reach, 100_000.0);
        assert!(end.0 < 100_000.0, "lands on his far side");
        // standing on him: the fallback direction
        let (dir, reach) = throw_line((5.0, 5.0), (5.0, 5.0), 1_000.0, (0.0, 1.0));
        assert_eq!((dir, reach), ((0.0, 1.0), 1_000.0));
    }

    #[test]
    fn the_flight_takes_e_fly_steps() {
        let (start, end) = ((0.0, 0.0), (64_000.0, 0.0));
        let step = dist(start, end) / E_FLY as f64;
        let mut cur = start;
        for k in 1..=E_FLY {
            cur = fly_step(cur, end, step);
            if k < E_FLY {
                assert!(cur.0 < end.0, "arrived early at step {k}");
            }
        }
        assert_eq!(cur, end);
    }

    #[test]
    fn the_looks_cover_a_glue_period() {
        assert!(LAND_AT[0] > E_FLY);
        assert!(LAND_AT[LAND_AT.len() - 1] - LAND_AT[0] >= W_P);
    }

    #[test]
    fn walls_stop_the_flight() {
        let grids = Grid::builtin();
        let g = &grids[0];
        let to = wall_travel(g, (40_000.0, 480_000.0), (-1.0, 0.0), 60_000.0, 6_000.0).expect("the edge is a wall");
        assert!((to - (40_000.0 - MOBA_BOUNDS.0 - 6_000.0 - WALL_GAP)).abs() <= STEP, "{to}");
        assert_eq!(wall_travel(g, (480_000.0, 480_000.0), (0.0, 1.0), 30_000.0, 6_000.0), None);
    }

    #[test]
    fn names_fit_a_buff() {
        for s in ["e_air", "w_slow", "e_root"] {
            assert!(n(s).len() <= BUFF_NAME_CAP);
        }
    }

    #[test]
    fn the_copy_uses_the_native_and_the_numbers() {
        let copy = include_str!("../override/league_singed.data_champion");
        assert!(copy.contains("league_singed:fling"), "the copy never uses league_singed:fling");
        assert!(!copy.contains("\"type\": \"Pull\""), "the copy still pulls in data");
        assert!(!copy.contains("\"type\": \"Bind\""), "the copy still roots in data");
        assert!(copy.contains("\"name\": \"league_singed_w_slow\""), "the glue's slow is not league_singed_w_slow");
        assert!(copy.contains(&format!("\"period\": {W_P},")), "the glue's period is not {W_P}");
    }
}
