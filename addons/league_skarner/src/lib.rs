//! 斯卡纳附加包（用户 2026-10-26：「和英雄联盟不一样的地方要做附加包」）：数据做不到、和英雄联盟不一样的地方，这里照英雄联盟做。
//!
//! `mod.override_info` 把主包的斯卡纳换成 `override/` 里的副本（tools/kit/build_skarner.py --native：技能、时机一字不改，只有
//! 下面几处换成本包的原生效果），`passive` 换成本包的 `league_skarner:sovereign`：
//!
//! - **战栗按每个英雄叠层**（原生效果 `league_skarner:quake`，普攻、巨石、毒刺打中英雄时）：主包读不到目标身上有几层，层数记在
//!   斯卡纳自己身上（换了目标也接着数）。本包在被打中的英雄身上叠这个斯卡纳的 `league_skarner_qk_<他>`（`P_T` 拍，最多
//!   `P_N` 层，每次刷新），满 `P_N` 层就开始战栗：`P_T` 拍里每 `P_P` 拍受到它最大生命 `P_PCT`% 的**魔法伤害**（主包：真实伤害），
//!   战栗的时候不再叠层。毒刺贯体打中的英雄（`league_skarner:impale`）直接战栗。
//! - **以绪塔尔冲击撞墙才晕**（原生效果 `league_skarner:impact`，冲锋撞上英雄时）：沿他冲的方向查墙（卡蜜尔附加包的墙格、5v5
//!   地图的四边）：拖 `E_KB_SPEED` x `E_KB_T` 的路上碰到墙就拖到墙边，到的那一刻（被动看它身上的 `league_skarner_ed_<他>` 到期）
//!   受到 `E_WALL_DMG` + `E_RATIO`% 攻击力 + 它最大生命 `E_WALL_HP`% 的物理伤害并眩晕 `E_STUN` 拍；没碰到墙就照常拖走、不晕
//!   （英雄联盟）。主包：每次拖完都砸一下、晕一下。冲锋时他穿过地形（两边一样：`league_skarner_e_ghost`，ignore_wall）。
//! - **毒刺贯体只压前 `R_N` 个英雄，并拖在身后**（原生效果 `league_skarner:impale`，尾巴打中英雄时）：一次施法数到第 `R_N`
//!   个为止（他身上的 `league_skarner_rc_<他>`），每个受到 `R_DMG` + `R_RATIO`% 攻击力的**魔法伤害**、压制 `R_SUP` 拍并立刻战栗；
//!   压制期间被动每拍把它们放在他身边、保持被打中时的方向，离他最多 `R_GAP`（他走到哪拖到哪）。主包：线上所有英雄都中，物理
//!   伤害，每 3 拍往他身上拽一下。被拽时每拍最多走 `R_PULL`：远的先被拽到他身边（不是一下瞬移）。
//!
//! 数字是主包参数表 P 的同名项（小写）；`make_override.py` 生成副本时核对，不一致就停。计数在目标身上（按斯卡纳的编号起名）
//! 和被动自己身上，不用全局变量，服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_skarner.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `SPAWN`、`QUAKE`（叠层 / 战栗）、`IMPACT`（撞墙 / 没墙）、`WALL`（撞墙眩晕）、`IMPALE`（压制 / 超过 R_N 个）、`DRAG`，限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_skarner";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_skarner") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 战栗：满几层、持续 tick、每几拍一下、每下最大生命 %。
pub const P_N: usize = 3;
pub const P_T: usize = 240;
pub const P_P: usize = 60;
pub const P_PCT: usize = 1;
/// 以绪塔尔冲击：拖的速度和 tick、撞墙眩晕、撞墙伤害（固定、攻击力 %、最大生命 %）。
pub const E_KB_SPEED: usize = 2_500;
pub const E_KB_T: usize = 20;
pub const E_STUN: usize = 40;
pub const E_WALL_DMG: usize = 60;
pub const E_RATIO: usize = 80;
pub const E_WALL_HP: usize = 6;
/// 毒刺贯体：最多压几个、压制 tick、伤害（固定、攻击力 %）。
pub const R_N: usize = 3;
pub const R_SUP: usize = 45;
pub const R_DMG: usize = 60;
pub const R_RATIO: usize = 50;
/// 被拖着的英雄离他最远多少（身体挨着身体），每拍最多被拽多远（主包的拽：每 3 拍 2 拍 3000，约每拍 2000；这里每拍
/// 3000，先被拽到他身边，之后跟着他走）。
pub const R_GAP: f64 = 9_000.0;
pub const R_PULL: f64 = 3_000.0;
/// 一次毒刺贯体数人的记号留多久（尾巴飞完整条线还有余）。
pub const R_COUNT_T: usize = 30;

/// 推到墙边时离墙留的距离（身体半径另算）。
pub const WALL_GAP: f64 = 1_000.0;
/// 5v5 地图四边的可走范围（卡蜜尔附加包量的）。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);
/// 墙格的边长（世界单位）和查墙的步长。
pub const CELL: f64 = 32_000.0;
pub const STEP: f64 = 1_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SKARNER_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_skarner.log");
        }
    }
    PathBuf::from("league_skarner.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (league_olaf_rage's lesson: opening it for every line stalled the simulation thread)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first).
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

/// 这个斯卡纳在目标身上的战栗层数 / 战栗中 / 撞墙在路上 / 撞墙到达 / 被拖着；他自己身上这次毒刺数到第几个。
fn stacks_name(me: usize) -> String {
    n(&format!("qk_{me}"))
}
fn quaking_name(me: usize) -> String {
    n(&format!("qq_{me}"))
}
fn wall_go_name(me: usize) -> String {
    n(&format!("eg_{me}"))
}
fn wall_due_name(me: usize) -> String {
    n(&format!("ed_{me}"))
}
fn dragged_name(me: usize) -> String {
    n(&format!("rd_{me}"))
}
fn count_name(me: usize) -> String {
    n(&format!("rc_{me}"))
}

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn unit(v: Pt) -> Option<Pt> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

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

/// 从 `at` 沿 `dir` 拖 `reach`（身体半径 `body`）：`Some(走多远)` 路上撞墙（拖到墙边为止），`None` 一路没墙。
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

/// 撞墙的伤害（减免前）：攻击力 `ad`、目标最大生命 `max_hp`。
pub fn wall_damage(ad: usize, max_hp: usize) -> usize {
    E_WALL_DMG + E_RATIO * ad / 100 + E_WALL_HP * max_hp / 100
}

/// 毒刺贯体的伤害（减免前）。
pub fn impale_damage(ad: usize) -> usize {
    R_DMG + R_RATIO * ad / 100
}

/// 战栗每一下的魔法伤害（减免前），至少 1。
pub fn quake_tick(max_hp: usize) -> usize {
    (max_hp * P_PCT / 100).max(1)
}

/// 战栗的每一下在第几 tick（从开始战栗算起）。
pub fn quake_ticks() -> Vec<usize> {
    (1..=P_T / P_P).map(|k| k * P_P).collect()
}

/// 被拖着的英雄这一拍走到哪：朝目标点 `to` 走，最多 `R_PULL`（远的先被拽过来，不是一下瞬移）。
pub fn pull_step(at: Pt, to: Pt) -> Pt {
    let d = dist(at, to);
    if d <= R_PULL {
        to
    } else {
        (at.0 + (to.0 - at.0) * R_PULL / d, at.1 + (to.1 - at.1) * R_PULL / d)
    }
}

/// 被拖着的英雄相对他的位置：保持方向 `off`，离他不超过 `R_GAP`（太近就不动它的距离）。
pub fn drag_offset(off: Pt) -> Pt {
    let d = (off.0 * off.0 + off.1 * off.1).sqrt();
    if d <= R_GAP || d < 1.0 {
        off
    } else {
        (off.0 * R_GAP / d, off.1 * R_GAP / d)
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

fn retimed(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

/// 强制位移 `target` 沿 `dir` 走 `len`，速度 `speed`；返回 tick 数。
fn shove(sim: &mut StableSim<'_>, target: usize, dir: Pt, len: f64, speed: usize) -> usize {
    let ticks = ((len / speed as f64).ceil() as usize).max(1);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (dir.0 * len).round() as i64;
    cc.dy = (dir.1 * len).round() as i64;
    cc.speed = speed as u64;
    sim.apply_cc(target, &cc);
    ticks
}

fn alive_champion(sim: &StableSim<'_>, id: usize) -> bool {
    (0..sim.champion_count()).any(|i| sim.champion_id_at(i) == id) && sim.get_entity(id).is_some_and(|e| e.is_alive())
}

// ===================== 原生效果 =====================

/// 战栗叠一层（满层开始战栗）。
fn quake(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    if !alive_champion(sim, target) || has_buff(sim, target, &quaking_name(me)) {
        return;
    }
    let c = sim.entity_stack_buff(target, &BuffV1::timed(&stacks_name(me), P_T), P_N, true);
    if c == 0 {
        wlog(format!("{} QUAKE: entity_stack_buff refused on #{target}", head(sim, me)));
        return;
    }
    if c >= P_N {
        burst(sim, me, target, "stacks");
    } else if let Some(k) = counted("stack") {
        wlog(format!("{} QUAKE #{target}: {c} stack(s) #{k}", head(sim, me)));
    }
}

/// 毒刺贯体打中的英雄：直接战栗。
fn quake_full(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    if alive_champion(sim, target) && !has_buff(sim, target, &quaking_name(me)) {
        burst(sim, me, target, "impale");
    }
}

fn burst(sim: &mut StableSim<'_>, me: usize, target: usize, why: &str) {
    sim.entity_remove_buff(target, &stacks_name(me));
    sim.add_buff(target, &BuffV1::timed(&quaking_name(me), P_T));
    retimed(sim, target, &n("p_quake"), P_T);
    let on = InputTargetV1::target(target);
    sim.play_view_effect(&n("p_burst"), me, &on, 0, 0, 0);
    sim.play_sfx(&n("p_burst"), me, &on);
    for t in quake_ticks() {
        if !sim.queue_effect(&format!("{ID}:burn"), AttackTypeV1::Skill, me, &on, t) {
            wlog(format!("{} QUAKE: queue_effect(burn) refused", head(sim, me)));
            break;
        }
    }
    if let Some(k) = counted("burst") {
        wlog(format!("{} QUAKE #{target}: quaking ({why}) - {P_PCT}% max health magic every {P_P} ticks for {P_T} #{k}", head(sim, me)));
    }
}

/// 战栗的一下。
fn burn(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some(max_hp) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.hp().1) else { return };
    if has_buff(sim, target, &quaking_name(me)) {
        sim.deal_damage_typed(me, target, quake_tick(max_hp), DamageTypeV1::Ap, AttackTypeV1::Skill);
    }
}

/// 以绪塔尔冲击撞上英雄：沿他冲的方向查墙，拖到墙边并记下撞墙的时刻，或者照常拖走。
fn impact(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some(body) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.radius() as f64) else {
        return;
    };
    if cc_immune(sim, target) {
        return;
    }
    let (Some(him), Some(at)) = (pos(sim, me), pos(sim, target)) else { return };
    let dir = unit((at.0 - him.0, at.1 - him.1)).unwrap_or((1.0, 0.0));
    let reach = (E_KB_SPEED * E_KB_T) as f64;
    match grid_now(sim).and_then(|g| wall_travel(&g, at, dir, reach, body)) {
        Some(len) => {
            let ticks = if len >= 1.0 { shove(sim, target, dir, len, E_KB_SPEED) } else { 0 };
            retimed(sim, target, &wall_due_name(me), ticks.max(1));
            retimed(sim, target, &wall_go_name(me), ticks + 4);
            if let Some(k) = counted("impact") {
                wlog(format!("{} IMPACT #{target} at {}: a wall {len:.0} away, slams in {ticks} ticks #{k}", head(sim, me), pt(at)));
            }
        }
        None => {
            shove(sim, target, dir, reach, E_KB_SPEED);
            if let Some(k) = counted("impact") {
                wlog(format!("{} IMPACT #{target} at {}: no wall within {reach:.0}, dragged, no stun #{k}", head(sim, me), pt(at)));
            }
        }
    }
}

/// 毒刺贯体打中英雄：前 R_N 个受伤、压制、战栗、被拖着走。
fn impale(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    if !alive_champion(sim, target) {
        return;
    }
    let c = sim.entity_stack_buff(me, &BuffV1::timed(&count_name(me), R_COUNT_T), 0, true);
    if c > R_N {
        if let Some(k) = counted("impale") {
            wlog(format!("{} IMPALE #{target}: champion {c} on the line, only {R_N} are impaled #{k}", head(sim, me)));
        }
        return;
    }
    let ad = sim.get_entity(me).map_or(0, |e| e.stat().attack);
    sim.deal_damage_typed(me, target, impale_damage(ad), DamageTypeV1::Ap, AttackTypeV1::Skill);
    quake_full(sim, me, InputTargetV1::target(target));
    if !sim.get_entity(target).is_some_and(|e| e.is_alive()) || cc_immune(sim, target) {
        return;
    }
    sim.apply_cc(target, &CcV1::stun(R_SUP as u64));
    retimed(sim, target, &n("r_held"), R_SUP);
    retimed(sim, target, &dragged_name(me), R_SUP);
    if let Some(k) = counted("impale") {
        wlog(format!("{} IMPALE #{target}: champion {c}/{R_N}, {} magic, suppressed {R_SUP} ticks #{k}", head(sim, me), impale_damage(ad)));
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 被动：撞墙到达、拖人 =====================

#[derive(Clone, Default)]
struct Sovereign {
    /// 被毒刺拖着的英雄 -> 相对他的位置。
    dragged: HashMap<usize, Pt>,
}

impl Sovereign {
    /// 被拖到墙边的英雄到了：撞墙伤害 + 眩晕。
    fn walls(sim: &mut StableSim<'_>, me: usize, foe: usize) {
        if !has_buff(sim, foe, &wall_go_name(me)) || has_buff(sim, foe, &wall_due_name(me)) {
            return;
        }
        sim.entity_remove_buff(foe, &wall_go_name(me));
        let Some(max_hp) = sim.get_entity(foe).filter(|e| e.is_alive()).map(|e| e.hp().1) else { return };
        let ad = sim.get_entity(me).map_or(0, |e| e.stat().attack);
        sim.deal_damage_typed(me, foe, wall_damage(ad, max_hp), DamageTypeV1::Ad, AttackTypeV1::Skill);
        let on = InputTargetV1::target(foe);
        sim.play_view_effect(&n("e_slam"), me, &on, 0, 0, 0);
        sim.play_sfx(&n("e_slam"), me, &on);
        if !cc_immune(sim, foe) {
            sim.apply_cc(foe, &CcV1::stun(E_STUN as u64));
            retimed(sim, foe, &n("e_stun"), E_STUN);
        }
        if let Some(k) = counted("wall") {
            wlog(format!("{} WALL #{foe} slammed into the wall: {} physical, stunned {E_STUN} ticks #{k}", head(sim, me), wall_damage(ad, max_hp)));
        }
    }

    /// 压制中的英雄跟着他走。
    fn drag(&mut self, sim: &mut StableSim<'_>, me: usize, foe: usize, him: Pt) {
        let held = has_buff(sim, foe, &dragged_name(me)) && sim.get_entity(foe).is_some_and(|e| e.is_alive());
        if !held {
            self.dragged.remove(&foe);
            return;
        }
        let Some(at) = pos(sim, foe) else { return };
        let off = *self.dragged.entry(foe).or_insert_with(|| drag_offset((at.0 - him.0, at.1 - him.1)));
        let to = pull_step(at, (him.0 + off.0, him.1 + off.1));
        if to.0 < 0.0 || to.1 < 0.0 || grid_now(sim).is_some_and(|g| g.is_wall(to.0, to.1)) {
            return;   // never into a wall: it waits where it is until he comes back to open ground
        }
        if dist(to, at) >= 1.0 {
            sim.entity_set_pos(foe, to.0.round() as u64, to.1.round() as u64);
            if let Some(k) = counted("drag") {
                wlog(format!("{} DRAG #{foe}: {} -> {} (behind him at {}) #{k}", head(sim, me), pt(at), pt(to), pt(him)));
            }
        }
    }
}

impl StablePassive for Sovereign {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.dragged.clear();
        let team = sim.get_entity(me).map_or(usize::MAX, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Skarner (player {player}, team {team})", head(sim, me)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some((team, him, alive)) = sim.get_entity(me).map(|e| (e.team(), (e.pos().0 as f64, e.pos().1 as f64), e.is_alive())) else {
            return;
        };
        let foes: Vec<usize> = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter(|&id| sim.get_entity(id).is_some_and(|e| e.team() != team))
            .collect();
        for foe in foes {
            Self::walls(sim, me, foe);
            if alive {
                self.drag(sim, me, foe, him);
            } else {
                self.dragged.remove(&foe);
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
        "=== {ID} v{VERSION} (Skarner: Quaking per champion, Ixtal's Impact stuns on walls, Impale drags the first {R_N}) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:quake"), Step(quake));
    module.add_native_effect(format!("{ID}:burn"), Step(burn));
    module.add_native_effect(format!("{ID}:impact"), Step(impact));
    module.add_native_effect(format!("{ID}:impale"), Step(impale));
    module.add_native_passive(format!("{ID}:sovereign"), Sovereign::default());
    host.log(LogLevel::Info, "league_skarner loaded (Quaking per champion, wall stun, Impale drags the first three).");
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
    fn walls_stop_the_carry() {
        let grids = Grid::builtin();
        let g = &grids[0];
        // the map's left edge: dragged left from 40000 with a body of 6000 the wall is 17500 + 6000 away
        let to = wall_travel(g, (40_000.0, 480_000.0), (-1.0, 0.0), 50_000.0, 6_000.0).expect("the edge is a wall");
        assert!((to - (40_000.0 - MOBA_BOUNDS.0 - 6_000.0 - WALL_GAP)).abs() <= STEP, "{to}");
        // open ground in the middle of the map, along the river: nothing within reach
        assert_eq!(wall_travel(g, (480_000.0, 480_000.0), (0.0, 1.0), 30_000.0, 6_000.0), None);
    }

    #[test]
    fn damage_numbers() {
        assert_eq!(wall_damage(100, 2_000), E_WALL_DMG + E_RATIO + E_WALL_HP * 20);
        assert_eq!(impale_damage(100), R_DMG + R_RATIO);
        assert_eq!(quake_tick(2_000), 2_000 * P_PCT / 100);
        assert_eq!(quake_tick(10), 1);
        assert_eq!(quake_ticks().len(), P_T / P_P);
        assert_eq!(*quake_ticks().last().unwrap(), P_T);
    }

    #[test]
    fn pulled_not_teleported() {
        assert_eq!(pull_step((0.0, 0.0), (2_000.0, 0.0)), (2_000.0, 0.0));
        let (x, y) = pull_step((0.0, 0.0), (30_000.0, 40_000.0));
        assert!(((x * x + y * y).sqrt() - R_PULL).abs() < 1e-6, "one step of R_PULL");
    }

    #[test]
    fn dragged_beside_him() {
        assert_eq!(drag_offset((3_000.0, 4_000.0)), (3_000.0, 4_000.0));
        let (x, y) = drag_offset((30_000.0, 40_000.0));
        assert!(((x * x + y * y).sqrt() - R_GAP).abs() < 1.0);
        assert!((x / y - 0.75).abs() < 1e-9, "keeps the direction");
    }

    #[test]
    fn names_fit_a_buff() {
        for s in [stacks_name(usize::MAX), quaking_name(usize::MAX), wall_go_name(usize::MAX), wall_due_name(usize::MAX),
                  dragged_name(usize::MAX), count_name(usize::MAX), n("p_quake"), n("r_held"), n("e_stun")] {
            assert!(s.len() <= BUFF_NAME_CAP, "{s}");
        }
    }

    #[test]
    fn the_copy_uses_the_natives_and_the_numbers() {
        let copy = include_str!("../override/league_skarner.data_champion");
        for r in ["league_skarner:quake", "league_skarner:impact", "league_skarner:impale",
                  "league_skarner:sovereign"] {
            assert!(copy.contains(r), "the copy never uses {r}");
        }
        for (k, v) in [("p_n", P_N), ("p_t", P_T), ("p_p", P_P), ("p_pct", P_PCT), ("e_kb_speed", E_KB_SPEED),
                       ("e_kb_t", E_KB_T), ("e_stun", E_STUN), ("e_wall_dmg", E_WALL_DMG), ("e_ratio", E_RATIO),
                       ("e_wall_hp", E_WALL_HP), ("r_n", R_N), ("r_sup", R_SUP), ("r_dmg", R_DMG), ("r_ratio", R_RATIO)] {
            assert!(copy.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        assert!(!copy.contains("\"type\": \"Knockback\""), "the copy still drags in data");
        assert!(!copy.contains("\"type\": \"Grab\""), "the copy still pulls in data");
    }
}
