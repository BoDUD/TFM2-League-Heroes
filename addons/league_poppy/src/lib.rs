//! 波比附加包（用户 2026-10-18：「波比放辅助，技能按方案 A 做（带扩展包 league_poppy）」）。主包保持纯数据；`mod.override_info`
//! 把主包的波比换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_poppy.py 的 `native=1` 生成：技能、时机一字不改，
//! 只有下面几处换成本包的原生效果），本包补数据做不到的五件事（英雄联盟的规则）：
//!
//! - **坚定风采打断突进**（被动 `league_poppy:steadfast`）：她身上有坚定风采的光环（主包的 `league_poppy_w_on`）时，每 tick 看
//!   光环（`W_R` + 他的身体）里的每个敌方英雄：一 tick 里移动了至少 `DASH_STEP`（远超走路，不到 `BLINK_MAX`：闪现、传送不算）
//!   就是在突进——击飞 `W_UP` tick（击飞会打断突进）、`W_DMG` + `W_AP`% 法强魔法伤害，然后缚地（不能位移）并减速 `W_SLOW`%
//!   `W_GROUND` tick；每次光环每人只挡一次（他身上的 `league_poppy_w_hit`）。被她自己推着飞的（E、R，`league_poppy_push`）不算。
//!   主包：光环里的敌方英雄放不出新的位移技能。
//! - **坚定风采低血翻倍**：生命低于 `W_LOW`% 时护甲、魔抗再 +`W_DEF`%（`league_poppy_w_low`）。主包：一直 +`W_DEF`%。
//! - **英勇冲锋撞墙才晕**（原生效果 `league_poppy:charge`，撞上目标时）：沿推的方向查墙（卡蜜尔附加包的墙格、5v5 地图的四边）：
//!   推 `E_KB_SPEED` x `E_KB_T` 的路上碰到墙就推到墙边，到的那一刻（被动看他身上的 `league_poppy_e_due` 到期）再受一次
//!   `E_DMG` + `E_RATIO`% 攻击力物理伤害并眩晕 `E_STUN` tick；没碰到墙就照常推开、不晕。主包：每次推完都晕一下。
//! - **持卫的裁决打回泉水**（原生效果 `league_poppy:verdict`，冲击波打中英雄时）：5v5 地图上朝他自己的水晶方向强制位移
//!   `R_FAR`（速度 `R_FAR_SPEED`，撞墙会停），一路在空中（击飞）；别的地图照数据从她身边击飞击退。主包：击飞 `R_AIR` tick
//!   并从她身边击退 `R_KB_SPEED` x `R_KB_T`。
//! - **钢铁大使的护盾按最大生命算**（原生效果 `league_poppy:pick`，捡起圆盾时）：最大生命的 `P_SH_MIN`%（1 级）到
//!   `P_SH_MAX`%（18 级），`P_SH_T` tick。主包：固定值 + 攻击力加成。
//!
//! 数字是主包参数表 P 的同名项（小写）；`make_override.py` 生成副本时核对，不一致就停。本包不按任何技能键。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_poppy.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `BLOCK`（挡下突进）、`CHARGE`（撞墙 / 没墙）、`WALL`（撞墙眩晕）、`VERDICT`（往哪打飞）、`PICK`（护盾），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_poppy";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.2";

/// 坚定风采：护甲魔抗 %、低血线 %、光环半径、挡下突进的伤害（固定、法强 %）、击飞、缚地、减速 %。
pub const W_DEF: usize = 16;
pub const W_LOW: usize = 40;
pub const W_R: usize = 35_000;
pub const W_DMG: usize = 70;
pub const W_AP: usize = 70;
pub const W_UP: usize = 30;
pub const W_GROUND: usize = 120;
pub const W_SLOW: usize = 25;
/// 英勇冲锋：撞墙伤害（固定、攻击力 %）、推的速度和 tick、撞墙眩晕。
pub const E_DMG: usize = 70;
pub const E_RATIO: usize = 80;
pub const E_KB_SPEED: usize = 2_500;
pub const E_KB_T: usize = 12;
pub const E_STUN: usize = 105;
/// 钢铁大使的护盾：最大生命 %（1 级、18 级）、tick。
pub const P_SH_MIN: usize = 11;
pub const P_SH_MAX: usize = 21;
pub const P_SH_T: usize = 180;
/// 持卫的裁决：别的地图的击退（速度、tick）；5v5 打回泉水的距离、速度。
pub const R_KB_SPEED: usize = 6_000;
pub const R_KB_T: usize = 25;
/// 飞的时候在空中（击飞）的 tick（r_air）。
pub const R_AIR: usize = 25;
pub const R_FAR: usize = 150_000;
pub const R_FAR_SPEED: usize = 6_000;

/// 一 tick 里至少走这么远算突进（走路约 1000，加速后 1500；冲刺 2500 起），超过这么远算闪现 / 传送（英雄联盟不挡）。
pub const DASH_STEP: f64 = 2_200.0;
pub const BLINK_MAX: f64 = 20_000.0;
/// 推到墙边时离墙留的距离（身体半径另算）。
pub const WALL_GAP: f64 = 1_000.0;
/// 5v5 地图四边的可走范围（卡蜜尔附加包量的）和两边的水晶。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);
pub const NEXUS: [(f64, f64); 2] = [(96_000.0, 864_000.0), (864_000.0, 96_000.0)];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_POPPY_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_poppy.log");
        }
    }
    PathBuf::from("league_poppy.log")
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

/// 地图的墙格（卡蜜尔附加包的内置地图，杰斯、巴德附加包同样用它）；5v5 地图另加四边。
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

/// 当前对局的地图：英雄站进墙里最少的那张（同杰斯、巴德附加包）。
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

/// 一 tick 走了 `step` 算不算突进（闪现、传送那么远的不算）。
pub fn is_dash(step: f64) -> bool {
    (DASH_STEP..=BLINK_MAX).contains(&step)
}

/// 钢铁大使的护盾：等级 `level`、最大生命 `max_hp`。
pub fn shield_amount(max_hp: usize, level: usize) -> usize {
    let l = level.clamp(1, 18) - 1;
    let pct_x17 = P_SH_MIN * 17 + (P_SH_MAX - P_SH_MIN) * l;
    max_hp * pct_x17 / (100 * 17)
}

/// 他这一方的水晶：离他的塔（还在的）平均位置近的那个；一座塔都没有就 None。
pub fn home_nexus(towers: &[Pt]) -> Option<Pt> {
    if towers.is_empty() {
        return None;
    }
    let k = towers.len() as f64;
    let c = (towers.iter().map(|t| t.0).sum::<f64>() / k, towers.iter().map(|t| t.1).sum::<f64>() / k);
    NEXUS.iter().copied().min_by(|a, b| dist(*a, c).total_cmp(&dist(*b, c)))
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

/// 当前地图的墙格（和它是不是 5v5）。
fn grid_now(sim: &StableSim<'_>) -> Option<(Grid, bool)> {
    let grids = Grid::builtin();
    let i = current(&grids, &unit_points(sim))?;
    let moba = i == 0;
    grids.into_iter().nth(i).map(|g| (g, moba))
}

/// 强制位移 `target` 沿 `dir` 走 `len`，速度 `speed`；返回 tick 数。
fn shove(sim: &mut StableSim<'_>, target: usize, dir: Pt, len: f64, speed: usize) -> usize {
    let ticks = ((len / speed as f64).ceil() as usize).max(1);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (dir.0 * len).round() as i64;
    cc.dy = (dir.1 * len).round() as i64;
    cc.speed = speed as u64;
    sim.apply_cc(target, &cc);
    sim.add_buff(target, &BuffV1::timed(&n("push"), ticks + 2));
    ticks
}

// ===================== 原生效果 =====================

/// 英勇冲锋撞上目标：沿推的方向查墙，推到墙边并记下撞墙的时刻，或者照常推开。
fn charge(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some(body) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.radius() as f64) else {
        return;
    };
    if cc_immune(sim, target) {
        return;
    }
    let (Some(her), Some(at)) = (pos(sim, me), pos(sim, target)) else { return };
    let dir = unit((at.0 - her.0, at.1 - her.1)).unwrap_or((1.0, 0.0));
    let reach = (E_KB_SPEED * E_KB_T) as f64;
    let wall = grid_now(sim).and_then(|(g, _)| wall_travel(&g, at, dir, reach, body));
    match wall {
        Some(len) => {
            let ticks = if len >= 1.0 { shove(sim, target, dir, len, E_KB_SPEED) } else { 0 };
            sim.add_buff(target, &BuffV1::timed(&n("e_due"), ticks.max(1)));
            sim.add_buff(target, &BuffV1::timed(&n("e_go"), ticks + 4));
            if let Some(k) = counted("charge") {
                wlog(format!("{} CHARGE #{target} at {}: a wall {len:.0} away, slams in {ticks} ticks #{k}", head(sim, me), pt(at)));
            }
        }
        None => {
            shove(sim, target, dir, reach, E_KB_SPEED);
            if let Some(k) = counted("charge") {
                wlog(format!("{} CHARGE #{target} at {}: no wall within {reach:.0}, pushed, no stun #{k}", head(sim, me), pt(at)));
            }
        }
    }
}

/// 持卫的裁决打中一个敌方英雄：5v5 打回他的水晶方向，别的地图从她身边击退。
fn verdict(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some(team) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.team()) else { return };
    if cc_immune(sim, target) {
        return;
    }
    let Some(at) = pos(sim, target) else { return };
    let moba = grid_now(sim).is_some_and(|(_, m)| m);
    let towers: Vec<Pt> = (0..sim.tower_count())
        .map(|i| sim.tower_id_at(i))
        .filter(|&t| sim.get_entity(t).is_some_and(|e| e.is_alive() && e.team() == team))
        .filter_map(|t| pos(sim, t))
        .collect();
    let home = if moba { home_nexus(&towers) } else { None };
    match home.and_then(|h| unit((h.0 - at.0, h.1 - at.1)).map(|d| (h, d))) {
        Some((h, dir)) => {
            let len = (R_FAR as f64).min(dist(h, at));
            let ticks = shove(sim, target, dir, len, R_FAR_SPEED);
            sim.apply_cc(target, &CcV1::of_kind(CcKindV1::Airborne, ticks.max(R_AIR) as u64));
            if let Some(k) = counted("verdict") {
                wlog(format!("{} VERDICT #{target} at {}: toward his nexus {} - {len:.0} in {ticks} ticks #{k}", head(sim, me), pt(at), pt(h)));
            }
        }
        None => {
            sim.apply_cc(target, &CcV1::of_kind(CcKindV1::Airborne, R_AIR as u64));
            sim.entity_knockback(me, target, R_KB_SPEED, R_KB_T);
            sim.add_buff(target, &BuffV1::timed(&n("push"), R_KB_T + 2));
            if let Some(k) = counted("verdict") {
                wlog(format!("{} VERDICT #{target} at {}: knocked away from her (no nexus here) #{k}", head(sim, me), pt(at)));
            }
        }
    }
}

/// 捡起圆盾：按最大生命和等级给护盾。
fn pick(sim: &mut StableSim<'_>, me: usize, _input: InputTargetV1) {
    let Some((max_hp, level)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.hp().1, e.level())) else { return };
    let amount = shield_amount(max_hp, level);
    sim.entity_add_shield(me, amount, P_SH_T);
    if let Some(k) = counted("pick") {
        wlog(format!("{} PICK level {level} max hp {max_hp}: shield {amount} for {P_SH_T} ticks #{k}", head(sim, me)));
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 被动：坚定风采 =====================

#[derive(Clone, Default)]
struct Steadfast {
    /// 上一 tick 光环附近的敌方英雄在哪（id -> (tick, 位置)）。
    seen: HashMap<usize, (usize, Pt)>,
}

impl Steadfast {
    fn low_health(sim: &mut StableSim<'_>, me: usize) {
        let Some((hp, max)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        let low = max > 0 && hp * 100 < max * W_LOW;
        let name = n("w_low");
        let has = has_buff(sim, me, &name);
        if low && !has {
            let mut b = BuffV1::timed(&name, 1_000_000);
            b.defence_mult = W_DEF as i32;
            b.magic_resistance_mult = W_DEF as i32;
            sim.add_buff(me, &b);
        } else if !low && has {
            sim.entity_remove_buff(me, &name);
        }
    }

    fn block(sim: &mut StableSim<'_>, me: usize, foe: usize, step: f64) {
        sim.apply_cc(foe, &CcV1::of_kind(CcKindV1::Airborne, W_UP as u64));
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        sim.deal_damage_typed(me, foe, W_DMG + W_AP * ap / 100, DamageTypeV1::Ap, AttackTypeV1::Skill);
        sim.apply_cc(foe, &CcV1::of_kind(CcKindV1::BlockMoveSkill, (W_UP + W_GROUND) as u64));
        let mut slow = BuffV1::timed(&n("w_slow"), W_UP + W_GROUND);
        slow.move_speed_mult = -(W_SLOW as i32);
        sim.entity_remove_buff(foe, &n("w_slow"));
        sim.add_buff(foe, &slow);
        sim.add_buff(foe, &BuffV1::timed(&n("w_block"), 20));
        let left = sim.get_entity(me).and_then(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == n("w_on")));
        let hold = left.map_or(W_UP + W_GROUND, |b| b.duration_tick);
        sim.add_buff(foe, &BuffV1::timed(&n("w_hit"), hold + 2));
        if let Some(k) = counted("block") {
            wlog(format!("{} BLOCK #{foe}: {step:.0} in a tick inside her aura - knocked up, grounded #{k}", head(sim, me)));
        }
    }

    /// 被推到墙边的人到了：撞墙伤害 + 眩晕。
    fn walls(sim: &mut StableSim<'_>, me: usize, foe: usize) {
        if !has_buff(sim, foe, &n("e_go")) || has_buff(sim, foe, &n("e_due")) {
            return;
        }
        sim.entity_remove_buff(foe, &n("e_go"));
        if !sim.get_entity(foe).is_some_and(|e| e.is_alive()) {
            return;
        }
        let ad = sim.get_entity(me).map_or(0, |e| e.stat().attack);
        sim.deal_damage_typed(me, foe, E_DMG + E_RATIO * ad / 100, DamageTypeV1::Ad, AttackTypeV1::Skill);
        if !cc_immune(sim, foe) {
            sim.apply_cc(foe, &CcV1::stun(E_STUN as u64));
            sim.add_buff(foe, &BuffV1::timed(&n("e_stun"), E_STUN));
        }
        sim.add_buff(foe, &BuffV1::timed(&n("e_wall"), 20));
        if let Some(k) = counted("wall") {
            wlog(format!("{} WALL #{foe} slammed into the wall: stunned {E_STUN} ticks #{k}", head(sim, me)));
        }
    }
}

impl StablePassive for Steadfast {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.seen.clear();
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let t = sim.tick();
        if t % 6 == 0 {
            Self::low_health(sim, me);
        }
        let Some((my_team, her)) = sim.get_entity(me).map(|e| (e.team(), (e.pos().0 as f64, e.pos().1 as f64))) else { return };
        let aura = has_buff(sim, me, &n("w_on"));
        let foes: Vec<(usize, Pt, f64)> = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter_map(|id| {
                sim.get_entity(id)
                    .filter(|e| e.team() != my_team && e.is_alive())
                    .map(|e| (id, (e.pos().0 as f64, e.pos().1 as f64), e.radius() as f64))
            })
            .collect();
        for &(foe, at, body) in &foes {
            Self::walls(sim, me, foe);
            let near = dist(at, her) <= W_R as f64 + body + BLINK_MAX;
            let before = self.seen.get(&foe).copied();
            if near {
                self.seen.insert(foe, (t, at));
            } else {
                self.seen.remove(&foe);
            }
            let Some((t0, from)) = before else { continue };
            if !aura || t0 + 1 != t || dist(at, her) > W_R as f64 + body {
                continue;
            }
            let step = dist(from, at);
            if !is_dash(step)
                || has_buff(sim, foe, &n("w_hit"))
                || has_buff(sim, foe, &n("push"))
                || cc_immune(sim, foe)
                || !sim.get_entity(foe).is_some_and(|e| e.is_targetable())
            {
                continue;
            }
            Self::block(sim, me, foe, step);
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
        "=== {ID} v{VERSION} (Poppy: Steadfast Presence stops dashes, Heroic Charge stuns on walls, Keeper's Verdict sends home) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:charge"), Step(charge));
    module.add_native_effect(format!("{ID}:verdict"), Step(verdict));
    module.add_native_effect(format!("{ID}:pick"), Step(pick));
    module.add_native_passive(format!("{ID}:steadfast"), Steadfast::default());
    host.log(LogLevel::Info, "league_poppy loaded (dash interrupt, wall stun, fountain-ward verdict, buckler shield).");
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
    fn dashes_not_walks_nor_blinks() {
        assert!(!is_dash(1_000.0));
        assert!(!is_dash(1_600.0));
        assert!(is_dash(2_500.0));
        assert!(is_dash(3_500.0));
        assert!(!is_dash(60_000.0));
    }

    #[test]
    fn shield_by_level() {
        assert_eq!(shield_amount(1_000, 1), 110);
        assert_eq!(shield_amount(1_000, 18), 210);
        assert_eq!(shield_amount(1_000, 30), 210);
        assert!(shield_amount(1_000, 9) > 110 && shield_amount(1_000, 9) < 210);
    }

    #[test]
    fn walls_stop_the_carry() {
        let grids = Grid::builtin();
        let g = &grids[0];
        // the map's left edge: pushed left from 40000 with a body of 6000 the wall is 17500 + 6000 away
        let to = wall_travel(g, (40_000.0, 480_000.0), (-1.0, 0.0), 30_000.0, 6_000.0).expect("the edge is a wall");
        assert!((to - (40_000.0 - MOBA_BOUNDS.0 - 6_000.0 - WALL_GAP)).abs() <= STEP, "{to}");
        // open ground in the middle of the map, pushed along the river: nothing within reach
        assert_eq!(wall_travel(g, (480_000.0, 480_000.0), (0.0, 1.0), 30_000.0, 6_000.0), None);
        // a wall cell of the grid (row 3, columns 15-16)
        let at = (15.5 * CELL, 3.5 * CELL + 20_000.0);
        assert!(wall_travel(g, at, (0.0, -1.0), 30_000.0, 6_000.0).is_some());
    }

    #[test]
    fn home_is_the_nearer_nexus() {
        let blue = [(150_000.0, 800_000.0), (300_000.0, 700_000.0)];
        assert_eq!(home_nexus(&blue), Some(NEXUS[0]));
        let red = [(800_000.0, 150_000.0)];
        assert_eq!(home_nexus(&red), Some(NEXUS[1]));
        assert_eq!(home_nexus(&[]), None);
    }

    #[test]
    fn names_fit_a_buff() {
        for s in ["push", "e_due", "e_go", "e_stun", "e_wall", "w_on", "w_hit", "w_low", "w_slow", "w_block"] {
            assert!(n(s).len() <= BUFF_NAME_CAP);
        }
    }

    #[test]
    fn the_copy_uses_the_natives_and_the_numbers() {
        let copy = include_str!("../override/league_poppy.data_champion");
        for r in ["league_poppy:charge", "league_poppy:verdict", "league_poppy:pick", "league_poppy:steadfast"] {
            assert!(copy.contains(r), "the copy never uses {r}");
        }
        for (k, v) in [("w_def", W_DEF), ("w_low", W_LOW), ("w_r", W_R), ("w_dmg", W_DMG), ("w_ap", W_AP), ("w_up", W_UP),
                       ("w_ground", W_GROUND), ("w_slow", W_SLOW), ("e_dmg", E_DMG), ("e_ratio", E_RATIO),
                       ("e_kb_speed", E_KB_SPEED), ("e_kb_t", E_KB_T), ("e_stun", E_STUN), ("p_sh_min", P_SH_MIN),
                       ("p_sh_max", P_SH_MAX), ("p_sh_t", P_SH_T), ("r_kb_speed", R_KB_SPEED), ("r_kb_t", R_KB_T), ("r_air", R_AIR),
                       ("r_far", R_FAR), ("r_far_speed", R_FAR_SPEED)] {
            assert!(copy.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        assert!(copy.contains("\"name\": \"league_poppy_w_on\""), "the copy never raises the aura flag");
        assert!(!copy.contains("\"type\": \"Knockback\""), "the copy still pushes in data");
    }
}
