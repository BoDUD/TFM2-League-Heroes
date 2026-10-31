//! 杰斯附加包（用户 2026-10-15 的三个选择）。主包保持纯数据；`mod.override_info` 把主包的杰斯换成 `override/` 里的副本
//! （`make_override.py` 用 tools/kit/build_jayce.py 的 `native=1` 生成：加上本包的被动 `league_jayce:hextech`，打英雄的雷霆一击
//! 的 `Knockback` 换成本包的原生效果 `league_jayce:blow`，普攻、技能2、大招的说明开头加【附加包】），本包补数据做不到的三件事：
//!
//! - **整身变炮**（`view.rs`，游戏 0.6.4 起的 Windows 版）：墨丘利之炮形态（主包的永久 buff `league_jayce_cn`）时站着、跑着、挨打也是炮
//!   （`c_idle` / `c_run` / `c_hit`），阵亡还是锤子的倒地（奈德丽附加包的做法）。
//! - **雷霆一击往己方击退**（原生效果 `blow`）：打中的敌方英雄不再笔直地被推离杰斯，而是推向他这边——`ALLY_R` 内有他的友方
//!   英雄就推向它们的中心，没有就推向离目标最近的己方塔；这个方向 `kb_speed` x `kb_t` 内碰到墙（卡蜜尔附加包的墙格）就左右
//!   最多偏 `MAX_TURN`°，都不行、或者没有友方英雄和塔，才照数据笔直推开。距离、速度和数据的击退一样（`kb_speed`、`kb_t`），
//!   用引擎的强制位移（`ForceMove`，数据的 `Knockback` 也是它；撞墙会停，韧性照样缩短），免疫控制的不推。小兵、野怪照旧是
//!   数据的击退。
//! - **加速电炮挑目标**（AI 钩子 `league_jayce:gate`）：AI 要放大招时，射程（`gate_range`）内、线上没有别的敌方英雄挡着（电炮
//!   停在第一个英雄身上）的敌方英雄里：先挑这一炮打得死的（生命 + 护盾不超过 (`gate_dmg` + `gate_ad`% 攻击力) x 100 / (100 +
//!   护甲)，生命最少的先），再挑受了伤（生命低于 `WOUNDED`%）里生命比例最低的，都满血就挑最远的（英雄联盟玩家远距离开门打炮）。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_jayce.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `FORM`（显示里变炮 / 变锤、模拟里炮形态 buff 上下）、`GATE`（挑了谁、为什么）、`BLOW`（往哪推、为什么），都限了条数。

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

const ID: &str = "league_jayce";
const HERO: &str = "league_jayce";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.1";
/// 炮形态（主包数据的永久 buff）。
pub const FORM: &str = "league_jayce_cn";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_JAYCE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_jayce.log");
        }
    }
    PathBuf::from("league_jayce.log")
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

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;

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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 雷霆一击的击退：每 tick 多远、几 tick（P 的 e_kb_speed / e_kb_t）。
    pub kb_speed: usize,
    pub kb_t: usize,
    /// 加速电炮：施法距离（r_range）、伤害（cq_dmg / cq_ad 的 r_amp%）。
    pub gate_range: usize,
    pub gate_dmg: usize,
    pub gate_ad: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { kb_speed: 2500, kb_t: 14, gate_range: 90000, gate_dmg: 140, gate_ad: 161 }
    }
}

/// `{"kb_speed":2500,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "kb_speed" => p.kb_speed = v,
            "kb_t" => p.kb_t = v,
            "gate_range" => p.gate_range = v,
            "gate_dmg" => p.gate_dmg = v,
            "gate_ad" => p.gate_ad = v,
            _ => {}
        }
    }
    p
}

/// 被动 `configure` 拿到的参数（每场都一样，都是主包的数），原生效果和 AI 钩子读它；被动还没配置时是默认值（= P）。
static SHARED: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

fn shared() -> Params {
    SHARED.lock().unwrap_or_else(|e| e.into_inner()).clone()
}

// ===================== 计算（单元测试用） =====================

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

pub fn seg_dist(a: Pt, b: Pt, p: Pt) -> f64 {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len2 = dx * dx + dy * dy;
    if len2 <= 0.0 {
        return dist(a, p);
    }
    let t = (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / len2).clamp(0.0, 1.0);
    dist((a.0 + t * dx, a.1 + t * dy), p)
}

fn unit(v: Pt) -> Option<Pt> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

fn rot(v: Pt, deg: f64) -> Pt {
    let (s, c) = deg.to_radians().sin_cos();
    (v.0 * c - v.1 * s, v.0 * s + v.1 * c)
}

/// 墙格的边长（世界单位）和查一条线穿不穿墙的步长。
pub const CELL: f64 = 32_000.0;
pub const STEP: f64 = 1_000.0;

/// 地图的墙格（卡蜜尔附加包的内置地图，巴德附加包同样用它）。
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
}

impl Grid {
    pub fn from_rows(rows: &[&str]) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect() }
    }

    pub fn builtin() -> [Grid; 3] {
        [Grid::from_rows(&maps::MOBA), Grid::from_rows(&maps::SINGLE_LANE), Grid::from_rows(&maps::DEATH_MATCH)]
    }

    /// 世界坐标落在墙格里吗（地图外算墙：推不出去）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return true;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(true)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }

    /// 从 `from` 沿 `dir` 走 `len` 都不碰墙吗。
    pub fn clear(&self, from: Pt, dir: Pt, len: f64) -> bool {
        let mut s = STEP;
        while s <= len + 0.5 {
            if self.is_wall(from.0 + dir.0 * s, from.1 + dir.1 * s) {
                return false;
            }
            s += STEP;
        }
        true
    }
}

/// 猜地图用的点：所有活着的单位（英雄、小兵、野怪、塔……）。只看英雄的话，大家都站在三张图都空着的那条斜带上
/// （中路、两边泉水）时打平，平手偏向墙多的单线 / 死斗图，5v5 就猜错了（2026-11-01 复查：波比的 R 有 7 次退回击退）；
/// 5v5 边路的兵和野区的野怪几乎一直在，正好落在另两张图的墙里。
fn unit_points(sim: &StableSim<'_>) -> Vec<(f64, f64)> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_alive())
        .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
        .collect()
}

/// 当前对局的地图：英雄站进墙里最少的那张（同巴德附加包）。
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

/// 这么远内的友方英雄算「他这边的人」。
pub const ALLY_R: f64 = 80_000.0;
/// 推向的点离目标至少这么远（太近方向不稳），不然换下一个办法。
pub const MIN_SIDE: f64 = 6_000.0;
/// 推的方向碰到墙时左右试的角度。
pub const TURNS: [f64; 9] = [0.0, 15.0, -15.0, 30.0, -30.0, 45.0, -45.0, 60.0, -60.0];
pub const MAX_TURN: f64 = 60.0;

/// 为什么往这边推。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Why {
    /// 推向这么多个友方英雄的中心。
    Allies(usize),
    /// 推向离目标最近的己方塔。
    Tower,
    /// 照数据笔直推离杰斯（理由）。
    Away(&'static str),
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct BlowPlan {
    /// 单位方向。
    pub dir: Pt,
    pub why: Why,
    /// 为了避墙偏了多少度（推向他这边时）。
    pub turn: f64,
}

/// 雷霆一击往哪推：`me` 杰斯、`at` 被打中的敌方英雄、`allies` 他的友方英雄（不含他）、`towers` 他的塔、`grid` 当前地图、
/// `reach` 推多远。
pub fn blow_plan(me: Pt, at: Pt, allies: &[Pt], towers: &[Pt], grid: Option<&Grid>, reach: f64) -> BlowPlan {
    let away = unit((at.0 - me.0, at.1 - me.1)).unwrap_or((1.0, 0.0));
    let straight = |why| BlowPlan { dir: away, why: Why::Away(why), turn: 0.0 };
    let near: Vec<Pt> = allies.iter().copied().filter(|&a| dist(a, at) <= ALLY_R).collect();
    let centre = (!near.is_empty()).then(|| {
        let n = near.len() as f64;
        (near.iter().map(|a| a.0).sum::<f64>() / n, near.iter().map(|a| a.1).sum::<f64>() / n)
    });
    let goal = match centre.filter(|&c| dist(c, at) >= MIN_SIDE) {
        Some(c) => Some((c, Why::Allies(near.len()))),
        None => towers
            .iter()
            .copied()
            .filter(|&t| dist(t, at) >= MIN_SIDE)
            .min_by(|a, b| dist(*a, at).total_cmp(&dist(*b, at)))
            .map(|t| (t, Why::Tower)),
    };
    let Some((goal, why)) = goal else { return straight("no ally or tower to push toward") };
    let Some(side) = unit((goal.0 - at.0, goal.1 - at.1)) else { return straight("no ally or tower to push toward") };
    let Some(g) = grid else { return BlowPlan { dir: side, why, turn: 0.0 } };
    for deg in TURNS {
        let d = rot(side, deg);
        if g.clear(at, d, reach) {
            return BlowPlan { dir: d, why, turn: deg };
        }
    }
    straight("walls on his side")
}

/// 一个敌方英雄：id、位置、生命、护盾、最大生命、护甲、身体半径。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub hp: usize,
    pub shield: usize,
    pub max: usize,
    pub def: usize,
    pub r: f64,
}

impl Foe {
    pub fn hp_pct(&self) -> usize {
        if self.max == 0 { 100 } else { self.hp * 100 / self.max }
    }
}

/// 电炮的宽（主包 r_w），挡路的英雄身体没读到时按这么宽算。
pub const GATE_W: f64 = 3_500.0;
pub const BODY: f64 = 6_000.0;
/// 生命低于这么多 % 算受了伤（都不低于就挑最远的）。
pub const WOUNDED: usize = 90;

/// 加速电炮打一个英雄大概多少（物理伤害，按护甲打折：100 / (100 + 护甲)）。
pub fn gate_damage(ad: usize, def: usize, p: &Params) -> usize {
    (p.gate_dmg + ad * p.gate_ad / 100) * 100 / (100 + def)
}

/// 从 `me` 到 `to` 的线上，比 `to` 近的别的敌方英雄挡着吗（电炮碰到第一个英雄就停）。
pub fn blocked(me: Pt, to: &Foe, foes: &[Foe]) -> bool {
    let d = dist(me, to.at);
    foes.iter().any(|f| {
        f.id != to.id && dist(me, f.at) < d && seg_dist(me, to.at, f.at) <= GATE_W + if f.r > 0.0 { f.r } else { BODY }
    })
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum GateWhy {
    Kill,
    Low,
    Far,
}

/// 加速电炮的目标：射程内、线上没被别的英雄挡着的敌方英雄——打得死的（生命 + 护盾最少的先），再是受了伤的里生命比例最低的，
/// 再是最远的。
pub fn gate_pick(me: Pt, ad: usize, foes: &[Foe], p: &Params) -> Option<(Foe, GateWhy)> {
    let reach = p.gate_range as f64;
    let open: Vec<Foe> = foes.iter().copied().filter(|f| dist(me, f.at) <= reach && !blocked(me, f, foes)).collect();
    let far = |a: &Foe, b: &Foe| dist(me, a.at).total_cmp(&dist(me, b.at));
    if let Some(f) = open
        .iter()
        .filter(|f| f.hp + f.shield <= gate_damage(ad, f.def, p))
        .min_by(|a, b| (a.hp + a.shield).cmp(&(b.hp + b.shield)).then(far(b, a)))
    {
        return Some((*f, GateWhy::Kill));
    }
    if let Some(f) = open
        .iter()
        .filter(|f| f.hp_pct() < WOUNDED)
        .min_by(|a, b| a.hp_pct().cmp(&b.hp_pct()).then(a.hp.cmp(&b.hp)).then(far(b, a)))
    {
        return Some((*f, GateWhy::Low));
    }
    open.iter().max_by(|a, b| far(a, b)).map(|f| (*f, GateWhy::Far))
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

// ===================== 被动：海克斯科技电容（参数 + 模拟里的形态日志） =====================

#[derive(Clone, Default)]
struct Hextech {
    /// 上一 tick 身上有没有炮形态 buff（None = 这条命还没看过）。
    cannon: Option<bool>,
}

impl StablePassive for Hextech {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let p = parse_params(params_json);
        let mut s = SHARED.lock().unwrap_or_else(|e| e.into_inner());
        if *s != p {
            wlog(format!("params {params_json} -> {p:?}"));
            *s = p;
        }
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.cannon = None;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let cn = has_buff(sim, me, FORM);
        if self.cannon.is_some_and(|was| was != cn) {
            if let Some(k) = counted("form_sim") {
                let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
                wlog(format!("{} FORM sim: {}{} #{k}", head(sim, me), if cn { "CANNON on" } else { "cannon off (hammer)" },
                    if alive { "" } else { ", dead" }));
            }
        }
        self.cannon = Some(cn);
    }
}

// ===================== 原生效果：雷霆一击往己方击退 =====================

struct Blow;

impl StableEffectType for Blow {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(target) = target_of(&input) else { return };
        let p = shared();
        let Some(e) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()) else { return };
        let champion = e.is_champion();
        if !champion {
            // only champions come here in the copy; anything else gets the data's push straight away from him
            sim.entity_knockback(caster, target, p.kb_speed, p.kb_t);
            return;
        }
        if cc_immune(sim, target) {
            if let Some(k) = counted("blow") {
                wlog(format!("{} BLOW {}: immune to crowd control, not pushed #{k}", head(sim, caster), who(sim, target)));
            }
            return;
        }
        let (Some(me), Some(at)) = (pos(sim, caster), pos(sim, target)) else { return };
        let team = sim.get_entity(caster).map_or(0, |c| c.team());
        let (mut allies, mut towers) = (Vec::new(), Vec::new());
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_alive() {
                continue;
            }
            let at_u = (u.pos().0 as f64, u.pos().1 as f64);
            if u.is_champion() {
                if u.team() == team && u.id() != caster {
                    allies.push(at_u);
                }
            } else if u.is_tower() && u.team() == team {
                towers.push(at_u);
            }
        }
        let grids = Grid::builtin();
        let grid = current(&grids, &unit_points(sim)).map(|i| &grids[i]);
        let reach = (p.kb_speed * p.kb_t) as f64;
        let plan = blow_plan(me, at, &allies, &towers, grid, reach);
        let mut cc = CcV1::of_kind(CcKindV1::ForceMove, p.kb_t as u64);
        cc.dx = (plan.dir.0 * reach).round() as i64;
        cc.dy = (plan.dir.1 * reach).round() as i64;
        cc.speed = p.kb_speed as u64;
        sim.apply_cc(target, &cc);
        if let Some(k) = counted("blow") {
            let why = match plan.why {
                Why::Allies(n) => format!("toward {n} allied champion{}", if n == 1 { "" } else { "s" }),
                Why::Tower => "toward his nearest tower".to_string(),
                Why::Away(r) => format!("straight away from him ({r})"),
            };
            let turned = if plan.turn != 0.0 { format!(", turned {:.0} deg off a wall", plan.turn) } else { String::new() };
            wlog(format!("{} BLOW {} at {}: {why}{turned}, dir ({:.2}, {:.2}) x {reach:.0} in {} ticks #{k}",
                head(sim, caster), who(sim, target), pt(at), plan.dir.0, plan.dir.1, p.kb_t));
        }
    }
}

// ===================== AI 钩子：加速电炮挑目标 =====================

#[derive(Clone, Default)]
struct GateAi;

impl StablePlayerAi for GateAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:gate")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let b = base?;
        if b.kind != InputKindV1::Ult.code() || InputTargetKindV1::from_code(b.target.kind) != Some(InputTargetKindV1::Target) {
            return None;
        }
        let current = b.target.target_id;
        let player = ctx.player_id();
        let p = shared();
        let (pick, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let (mid, team, ad) = (me.id(), me.team(), me.stat().attack);
            let at = (me.pos().0 as f64, me.pos().1 as f64);
            let mut foes = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(u) = sim.entity_at(i) else { continue };
                if u.team() == team || !u.is_alive() || !u.is_champion() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
                    continue;
                }
                let (hp, max) = u.hp();
                foes.push(Foe { id: u.id(), at: (u.pos().0 as f64, u.pos().1 as f64), hp, shield: u.shield(), max,
                                def: u.stat().defence, r: u.radius() as f64 });
            }
            let (f, why) = gate_pick(at, ad, &foes, &p)?;
            let why = match why {
                GateWhy::Kill => format!("KILL: hp {}+{} <= ~{}", f.hp, f.shield, gate_damage(ad, f.def, &p)),
                GateWhy::Low => format!("LOWEST: {}% hp", f.hp_pct()),
                GateWhy::Far => format!("FARTHEST: all >= {WOUNDED}% hp"),
            };
            let line = format!("{} GATE {} -> {} ({why}; {:.0} away, {} champions in reach)", head(&sim, mid), who(&sim, current),
                               who(&sim, f.id), dist(at, f.at), foes.iter().filter(|g| dist(at, g.at) <= p.gate_range as f64).count());
            (f, line)
        };
        if pick.id == current {
            if let Some(k) = counted("gate") {
                wlog(format!("{line} kept #{k}"));
            }
            return None;
        }
        let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(pick.id));
        if !ctx.is_valid_input(&input) {
            if let Some(k) = counted("gate") {
                wlog(format!("{line} refused by the game, the AI's target kept #{k}"));
            }
            return None;
        }
        if let Some(k) = counted("gate") {
            wlog(format!("{line} AIM #{k}"));
        }
        Some(input)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Jayce: the whole-body cannon, Thundering Blow toward his side, the gate shot's target) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:hextech"), Hextech::default());
    module.add_native_effect(format!("{ID}:blow"), Blow);
    module.add_player_input_ai(GateAi);
    host.log(LogLevel::Info, "league_jayce loaded (whole-body cannon, Thundering Blow toward his side, gate shot target).");
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

    fn foe(id: usize, at: Pt, hp: usize, max: usize) -> Foe {
        Foe { id, at, hp, shield: 0, max, def: 0, r: 6_000.0 }
    }

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"gate_ad":150,"junk":7,"kb_t":10}"#);
        assert_eq!((p.gate_ad, p.kb_t, p.kb_speed), (150, 10, 2500));
    }

    #[test]
    fn the_copy_carries_the_default_params_and_the_native_blow() {
        let copy = include_str!("../override/league_jayce.data_champion");
        let at = copy.find("\"passive_ref\": \"league_jayce:hextech\"").expect("no league_jayce:hextech passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("gate_ad", d.gate_ad), ("gate_dmg", d.gate_dmg), ("gate_range", d.gate_range), ("kb_speed", d.kb_speed),
                       ("kb_t", d.kb_t)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        assert!(copy.contains("\"effect_ref\": \"league_jayce:blow\""), "the copy does not call league_jayce:blow");
        assert!(copy.contains("\"speed\": 2500") && copy.contains("\"tick\": 14"), "the data's own knock-back is gone");
    }

    #[test]
    fn the_blow_goes_toward_his_allies_then_his_tower_then_straight() {
        let me = (100_000.0, 100_000.0);
        let foe = (120_000.0, 100_000.0); // east of him
        // an ally behind him (west): the push goes west, through him
        let p = blow_plan(me, foe, &[(60_000.0, 100_000.0)], &[], None, 35_000.0);
        assert_eq!(p.why, Why::Allies(1));
        assert!(p.dir.0 < -0.99, "{p:?}");
        // the ally out of ALLY_R: his tower instead (south)
        let p = blow_plan(me, foe, &[(10_000.0, 100_000.0)], &[(120_000.0, 20_000.0), (300_000.0, 0.0)], None, 35_000.0);
        assert_eq!(p.why, Why::Tower);
        assert!(p.dir.1 < -0.99, "{p:?}");
        // nobody: straight away from him (the data's)
        let p = blow_plan(me, foe, &[], &[], None, 35_000.0);
        assert!(matches!(p.why, Why::Away(_)) && p.dir.0 > 0.99, "{p:?}");
        // two allies: their centre
        let p = blow_plan(me, foe, &[(120_000.0, 60_000.0), (120_000.0, 140_000.0)], &[], None, 35_000.0);
        assert!(matches!(p.why, Why::Away(_)), "the centre sits on the target: no side to push to ({p:?})");
    }

    #[test]
    fn the_blow_turns_off_a_wall_and_gives_up_into_walls() {
        // row 1 is a wall up to x 64000; the target at (56000, 16000), the ally straight south beyond it
        let g = Grid::from_rows(&["....", "##..", "....", "...."]);
        let me = (56_000.0, 4_000.0);
        let at = (56_000.0, 16_000.0);
        let p = blow_plan(me, at, &[(56_000.0, 85_000.0)], &[], Some(&g), 35_000.0);
        assert_eq!((p.why, p.turn), (Why::Allies(1), -30.0), "{p:?}");
        assert!(g.clear(at, p.dir, 35_000.0) && p.dir.1 > 0.8);
        // boxed in: a wall all round but behind the target -> straight away from him
        let g = Grid::from_rows(&["####", "#..#", "####"]);
        let p = blow_plan((40_000.0, 48_000.0), (56_000.0, 48_000.0), &[(40_000.0, 10_000.0)], &[], Some(&g), 35_000.0);
        assert_eq!(p.why, Why::Away("walls on his side"));
        assert!(p.dir.0 > 0.99, "{p:?}");
    }

    #[test]
    fn the_gate_takes_a_kill_then_the_lowest_then_the_farthest() {
        let pp = Params::default();
        let me = (0.0, 0.0);
        let ad = 200; // 140 + 322 = 462 raw
        assert_eq!(gate_damage(ad, 0, &pp), 462);
        assert_eq!(gate_damage(ad, 100, &pp), 231);
        let full_far = foe(1, (85_000.0, 0.0), 1500, 1500);
        let full_near = foe(2, (0.0, 30_000.0), 1400, 1400);
        let low = foe(3, (0.0, -50_000.0), 600, 3000); // 20%, too healthy to kill
        let killable = foe(4, (-60_000.0, 0.0), 400, 1400);
        let out = foe(5, (95_000.0, 0.0), 10, 1400); // out of reach
        assert_eq!(gate_pick(me, ad, &[full_far, full_near, low, killable, out], &pp).map(|(f, w)| (f.id, w)),
                   Some((4, GateWhy::Kill)));
        let armoured = Foe { def: 100, ..killable }; // 231 < 400: not a kill
        assert_eq!(gate_pick(me, ad, &[full_far, full_near, low, armoured], &pp).map(|(f, w)| (f.id, w)),
                   Some((3, GateWhy::Low)));
        let shielded = Foe { shield: 100, ..killable }; // 500 > 462
        assert_eq!(gate_pick(me, ad, &[shielded], &pp).map(|(f, w)| (f.id, w)), Some((4, GateWhy::Low)));
        assert_eq!(gate_pick(me, ad, &[full_far, full_near], &pp).map(|(f, w)| (f.id, w)), Some((1, GateWhy::Far)));
        assert_eq!(gate_pick(me, ad, &[out], &pp), None);
    }

    #[test]
    fn a_champion_in_front_takes_the_orb() {
        let pp = Params::default();
        let me = (0.0, 0.0);
        let behind = foe(1, (80_000.0, 0.0), 100, 1500); // killable but behind another champion
        let front = foe(2, (40_000.0, 2_000.0), 1500, 1500);
        assert_eq!(gate_pick(me, 200, &[behind, front], &pp).map(|(f, w)| (f.id, w)), Some((2, GateWhy::Far)));
        let aside = Foe { at: (40_000.0, 30_000.0), ..front };
        assert_eq!(gate_pick(me, 200, &[behind, aside], &pp).map(|(f, w)| (f.id, w)), Some((1, GateWhy::Kill)));
    }
}
