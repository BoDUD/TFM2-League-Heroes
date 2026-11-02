//! 薇恩附加包：圣银弩箭数的是「同一个目标」挨的连续 3 下（用户：「薇恩也顺便做了」）。
//!
//! 主包保持纯数据：数据分不清一次攻击打中的是谁，圣银弩箭的两层（`league_vayne_sb1` / `sb2`）记在薇恩自己身上，
//! 她轮流打两个人也会凑满 3 下，在第三个被打中的人身上爆。`mod.override_info` 把主包的薇恩换成 `override/` 里的副本
//! （`make_override.py` 从主包生成）：每一处圣银弩箭的判定（普攻、翻滚后的强化普攻、恶魔审判）先调用本包的
//! `league_vayne_bolts:bolt`（目标 = 被打中的单位），本包数**这个单位身上**的层数（`league_vayne_bolts_s`，每层 210 tick，
//! 每次命中刷新）：
//!
//! - 原来 0 层：挂 1 层，给薇恩加 `league_vayne_sb_r1`（数据播一环）；
//! - 原来 1 层：变 2 层，加 `league_vayne_sb_r2`（数据播两环）；
//! - 原来 2 层：清掉，加 `league_vayne_sb_go`（数据打出真实伤害和第三环的爆裂；英雄再加最大生命值的那部分）。
//!
//! 标志都留 3 tick，数据同一 tick 读一次，读不到在下一 tick 再读一次（本包加的 buff 什么时候能被数据读到，游戏里还没证实过）。
//!
//! 恶魔审判撞墙才晕（用户 2026-11-02：「薇恩要改成不E到墙壁不能眩晕」，照英雄联盟）：主包每一箭推完都晕一下（数据看不到墙）。
//! 副本把重箭的击退换成本包的 `league_vayne_bolts:condemn`（目标 = 被打中的英雄）：沿击退的方向查墙（卡蜜尔附加包的墙格、
//! 5v5 地图的四边，同波比附加包的英勇冲锋）。推 `E_KB_SPEED` x `E_KB_T` 的路上碰到墙：推到墙边，给薇恩加
//! `league_vayne_e_wall`，到墙的那一刻（`queue_effect` 排好的 `league_vayne_bolts:pin`）把他按在墙边；主包第 `E_KB_T` tick
//! 的撞墙伤害和眩晕只在薇恩身上有这个标志时打出。没碰到墙：照主包击退，不伤不晕。
//! AI 钩子 `league_vayne_bolts:condemn`（`ai.rs`）替游戏的 AI 找墙放 E：预判走位，谁身后有墙就对谁放；没墙时只在贴脸自保、
//! 一箭打得死人时放，别的时候留着 E。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_vayne_bolts.log`，每次启动游戏重写，上一次的留在 .prev.log。
//! 你看的那场每一下都写，服务器的预模拟三种结果（Ring1 / Ring2 / Proc）和 `CONDEMN`（撞墙 / 没墙）、`PIN`（按在墙边）
//! 各先写 `LOG_FIRST` 行、之后每 `LOG_EVERY` 下一行（见 `tally`）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

pub mod ai;

const ID: &str = "league_vayne_bolts";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_vayne_bolts") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 目标身上的层（每层一个 buff 实例）。
pub const STACK: &str = "league_vayne_bolts_s";
/// 层留多久（League 3 秒；主包的计数是 210 tick）。
pub const STACK_T: usize = 210;
/// 薇恩身上给数据读的标志。
pub const RING1: &str = "league_vayne_sb_r1";
pub const RING2: &str = "league_vayne_sb_r2";
pub const GO: &str = "league_vayne_sb_go";
pub const FLAG_T: usize = 3;

/// 恶魔审判的击退：主包 `Knockback` 的速度和 tick（`make_override.py` 核对），撞墙伤害和眩晕是主包第 `E_KB_T` tick 的 `Delayed`。
pub const E_KB_SPEED: usize = 3_000;
pub const E_KB_T: usize = 8;
/// 恶魔审判的出手：主包第 `E_START` tick 射出重箭（`TargetProjectile`，每 tick `E_BOLT_SPEED`），射程 `E_RANGE`（`make_override.py` 核对）。
pub const E_START: usize = 12;
pub const E_BOLT_SPEED: usize = 7_000;
pub const E_RANGE: usize = 55_000;
/// 薇恩身上给数据读的标志：这一箭把人推到了墙上（留到数据的撞墙之后）。
pub const WALL: &str = "league_vayne_e_wall";
pub const WALL_T: usize = E_KB_T + 4;
/// 推到墙边的人身上：到墙时剩下的时间就是按住他多久（盖过数据第 `E_KB_T` tick 的撞墙）。
pub const PIN: &str = "league_vayne_bolts_pin";
pub const PIN_T: usize = E_KB_T + 2;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VAYNE_BOLTS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_vayne_bolts.log");
        }
    }
    PathBuf::from("league_vayne_bolts.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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

/// 日志行数的上限（2026-10-30 一次启动 0.58 MB：8 052 行全是预模拟的 `bolt on`，每一下都写、没有上限）。
/// 计数是全局的（一次启动几百场预模拟），按这一下的结果（Ring1 / Ring2 / Proc）分三种。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind`: its count when it is to be written - every one in the match on screen (watched,
/// spectated or replayed), the server's presims (and background matches) the first `LOG_FIRST`, then every
/// `LOG_EVERY`-th.
pub(crate) fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let on_screen = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (on_screen || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

pub(crate) fn head(sim: &StableSim<'_>, id: usize) -> String {
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

// ===================== 判断 =====================

/// 这一下之后：目标身上剩几层，薇恩身上加哪个标志。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Bolt {
    Ring1,
    Ring2,
    Proc,
}

/// 目标原来有 `stacks` 层时这一下的结果（2 层以上 = 第三下）。
pub fn next(stacks: usize) -> (Bolt, usize) {
    match stacks {
        0 => (Bolt::Ring1, 1),
        1 => (Bolt::Ring2, 2),
        _ => (Bolt::Proc, 0),
    }
}

fn stacks_on(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == STACK).count())
}

fn bolt(sim: &mut StableSim<'_>, vayne: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
        return;
    }
    let had = stacks_on(sim, target);
    let (what, keep) = next(had);
    // 每次命中刷新：去掉旧的层，按新层数重新挂上
    sim.entity_remove_buff(target, STACK);
    for _ in 0..keep {
        sim.add_buff(target, &BuffV1::timed(STACK, STACK_T));
    }
    let flag = match what {
        Bolt::Ring1 => RING1,
        Bolt::Ring2 => RING2,
        Bolt::Proc => GO,
    };
    sim.add_buff(vayne, &BuffV1::timed(flag, FLAG_T));
    // counted by the flag (one kind per result): the presims' first procs are written as well as the first rings
    if tally(sim, flag).is_some() {
        wlog(format!("{} bolt on #{target}: {had} stack(s) before -> {what:?}", head(sim, vayne)));
    }
}

// ===================== 恶魔审判：撞墙才晕 =====================

pub type Pt = (f64, f64);

/// 推到墙边时离墙留的距离（身体半径另算）；墙格的边长、查墙的步长；5v5 地图四边的可走范围（同波比附加包）。
pub const WALL_GAP: f64 = 1_000.0;
pub const CELL: f64 = 32_000.0;
pub const STEP: f64 = 1_000.0;
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);

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

/// 当前对局的地图：单位站进墙里最少的那张，一样少时取墙多的（同波比附加包）。
pub fn current(grids: &[Grid], units: &[Pt]) -> Option<usize> {
    grids
        .iter()
        .enumerate()
        .min_by_key(|(_, g)| {
            let inside = units.iter().filter(|&&(x, y)| g.is_wall(x, y)).count();
            (inside, std::cmp::Reverse(g.walls()))
        })
        .map(|(i, _)| i)
}

/// 从 `at` 沿 `dir` 推 `reach`（身体半径 `body`）：`Some(走多远)` 路上撞墙（推到墙边为止），`None` 一路没墙。
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

/// 推 `len` 到墙边：几 tick、每 tick 多快（不快过主包的击退，正好停在墙边）。
pub fn push_plan(len: f64) -> (usize, usize) {
    let ticks = ((len / E_KB_SPEED as f64).ceil() as usize).max(1);
    (ticks, (len / ticks as f64).ceil() as usize)
}

pub(crate) fn unit(v: Pt) -> Option<Pt> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

pub(crate) fn pt(p: Pt) -> String {
    format!("({:.0}, {:.0})", p.0, p.1)
}

/// 猜地图用的点：所有活着的单位（只看英雄的话大家站在三张图都空着的地方时会猜错，见波比附加包）。
pub(crate) fn unit_points(sim: &StableSim<'_>) -> Vec<Pt> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_alive())
        .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
        .collect()
}

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

/// 恶魔审判的重箭打中一个英雄：沿击退的方向查墙。有墙：推到墙边、给薇恩加 `WALL`（数据第 `E_KB_T` tick 打出撞墙伤害和眩晕），
/// 到墙的那一刻 `pin` 按住他；没墙：照主包击退，不晕。免控的人（主包的击退、眩晕本来也推不动、晕不了）什么都不做。
fn condemn(sim: &mut StableSim<'_>, vayne: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some((at, body, immune)) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| {
        let immune = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.cc_immune);
        ((e.pos().0 as f64, e.pos().1 as f64), e.radius() as f64, immune)
    }) else {
        return;
    };
    if immune {
        if let Some(k) = tally(sim, "immune") {
            wlog(format!("{} CONDEMN #{target} at {}: cc immune, not moved #{k}", head(sim, vayne), pt(at)));
        }
        return;
    }
    let Some(her) = sim.get_entity(vayne).map(|e| (e.pos().0 as f64, e.pos().1 as f64)) else { return };
    let dir = unit((at.0 - her.0, at.1 - her.1)).unwrap_or((1.0, 0.0));
    let reach = (E_KB_SPEED * E_KB_T) as f64;
    let grids = Grid::builtin();
    let wall = current(&grids, &unit_points(sim)).and_then(|i| wall_travel(&grids[i], at, dir, reach, body));
    let Some(len) = wall else {
        sim.entity_knockback(vayne, target, E_KB_SPEED, E_KB_T);
        if let Some(k) = tally(sim, "free") {
            wlog(format!("{} CONDEMN #{target} at {}: no wall within {reach:.0}, knocked back, no stun #{k}", head(sim, vayne), pt(at)));
        }
        return;
    };
    // 已经贴着墙（推不动）就下一 tick 按住
    let ticks = if len >= 1.0 {
        let (ticks, speed) = push_plan(len);
        let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
        cc.dx = (dir.0 * len).round() as i64;
        cc.dy = (dir.1 * len).round() as i64;
        cc.speed = speed as u64;
        sim.apply_cc(target, &cc);
        ticks
    } else {
        1
    };
    sim.add_buff(vayne, &BuffV1::timed(WALL, WALL_T));
    sim.entity_remove_buff(target, PIN);
    sim.add_buff(target, &BuffV1::timed(PIN, PIN_T));
    let name = format!("{ID}:pin");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, vayne, &InputTargetV1::target(target), ticks) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, vayne)));
    }
    if let Some(k) = tally(sim, "wall") {
        wlog(format!("{} CONDEMN #{target} at {}: a wall {len:.0} away, there in {ticks} ticks, slammed at tick {E_KB_T} #{k}", head(sim, vayne), pt(at)));
    }
}

/// 推到墙边的人到了：眩晕到数据的撞墙（他身上 `PIN` 剩下的时间）。
fn pin(sim: &mut StableSim<'_>, vayne: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some((at, hold, immune)) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| {
        let hold = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == PIN).map(|b| b.duration_tick);
        let immune = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.cc_immune);
        ((e.pos().0 as f64, e.pos().1 as f64), hold, immune)
    }) else {
        return;
    };
    let Some(hold) = hold.filter(|&h| h > 0) else { return };
    sim.entity_remove_buff(target, PIN);
    if !immune {
        sim.apply_cc(target, &CcV1::stun(hold as u64));
    }
    if let Some(k) = tally(sim, "pin") {
        let what = if immune { "cc immune now, not held".to_string() } else { format!("held {hold} ticks for the slam") };
        wlog(format!("{} PIN #{target} at the wall {}: {what} #{k}", head(sim, vayne), pt(at)));
    }
}

struct Fx(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Fx {
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
        "=== {ID} v{VERSION} (Vayne: Silver Bolts counted on each target, Condemn stuns only on walls) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:bolt"), Fx(bolt));
    module.add_native_effect(format!("{ID}:condemn"), Fx(condemn));
    module.add_native_effect(format!("{ID}:pin"), Fx(pin));
    module.add_player_input_ai(ai::Condemn::default());
    host.log(LogLevel::Info, "league_vayne_bolts loaded (Vayne: Silver Bolts counted on each target, Condemn stuns only on walls).");
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
    fn the_third_hit_on_one_target_procs() {
        assert_eq!(next(0), (Bolt::Ring1, 1));
        assert_eq!(next(1), (Bolt::Ring2, 2));
        assert_eq!(next(2), (Bolt::Proc, 0));
        // three hits in a row on one target
        let mut s = 0;
        let mut out = vec![];
        for _ in 0..3 {
            let (b, k) = next(s);
            out.push(b);
            s = k;
        }
        assert_eq!(out, vec![Bolt::Ring1, Bolt::Ring2, Bolt::Proc]);
        assert_eq!(s, 0);
    }

    #[test]
    fn walls_stop_the_push() {
        let grids = Grid::builtin();
        let g = &grids[0];
        let reach = (E_KB_SPEED * E_KB_T) as f64;
        // the 5v5 map's left edge: pushed left from 40000 with a body of 6000 the wall is 17500 + 6000 away
        let to = wall_travel(g, (40_000.0, 480_000.0), (-1.0, 0.0), reach, 6_000.0).expect("the edge is a wall");
        assert!((to - (40_000.0 - MOBA_BOUNDS.0 - 6_000.0 - WALL_GAP)).abs() <= STEP, "{to}");
        // 20000 further in the edge is out of her push's reach: knocked back, no stun
        assert_eq!(wall_travel(g, (60_000.0, 480_000.0), (-1.0, 0.0), reach, 6_000.0), None);
        // open ground in the middle of the map, pushed along the river
        assert_eq!(wall_travel(g, (480_000.0, 480_000.0), (0.0, 1.0), reach, 6_000.0), None);
        // a wall cell of the grid (row 3, columns 15-16)
        assert!(wall_travel(g, (15.5 * CELL, 3.5 * CELL + 20_000.0), (0.0, -1.0), reach, 6_000.0).is_some());
    }

    #[test]
    fn the_push_ends_at_the_wall_no_faster_than_the_data() {
        // the farthest wall stop is reach - WALL_GAP: it is reached within the data's E_KB_T ticks
        let far = (E_KB_SPEED * E_KB_T) as f64 - WALL_GAP;
        for len in [500.0, 2_999.0, 3_000.0, 3_001.0, 10_500.0, far] {
            let (ticks, speed) = push_plan(len);
            assert!(speed <= E_KB_SPEED, "{len}: {speed}");
            assert!(ticks <= E_KB_T, "{len}: {ticks} ticks");
            let went = (ticks * speed) as f64;
            assert!(went >= len && went < len + ticks as f64, "{len}: {ticks} x {speed}");
        }
    }

    #[test]
    fn names_fit_a_buff() {
        for s in [STACK, RING1, RING2, GO, WALL, PIN] {
            assert!(s.len() <= BUFF_NAME_CAP, "{s}");
        }
    }

    #[test]
    fn the_copy_condemns_natively() {
        let copy = include_str!("../override/league_vayne.data_champion");
        for r in ["league_vayne_bolts:bolt", "league_vayne_bolts:condemn", "description.league_vayne_bolts.skill2"] {
            assert!(copy.contains(r), "the copy never uses {r}");
        }
        assert!(copy.contains(&format!("\"buff_name\": \"{WALL}\"")), "the copy's slam does not wait for {WALL}");
        assert!(!copy.contains("\"type\": \"Knockback\""), "the copy still knocks back in data");
    }
}
