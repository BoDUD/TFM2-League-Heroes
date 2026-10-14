//! 巴德附加包：「神奇旅程」什么时候开、往哪开都由本包决定（用户：「巴德的传送别乱放啊 逻辑改一改」「往己方后撤，不穿墙」，
//! 然后「传送门还是有点怪 你也要用来追人啊 智能一点 现在一局比赛里放不出来几次都」）。
//!
//! 主包是纯数据：技能 2 被放出来、又正好被近身时才开门（一局没几次），朝最近敌人的反方向强制位移；引擎的强制位移不管地图的墙，
//! 四成左右穿过野区的石头。`mod.override_info` 把主包的巴德换成 `override/` 里的副本（tools/kit/build_bard.py 的 native=1）：
//! 技能 2 只剩圣坛，门全归本包的被动 `league_bard:door`。被动每 `EVERY` tick 看一次，门好了（他身上没有 `league_bard_e_cd`）、
//! 他活着、没被控时：
//! - **撤**（`wants_out`）：生命低于 `LOW_HP`% 而 `e_near` 内有敌方英雄；或 `e_close` 内有敌方英雄；或 `e_near` 内敌方英雄
//!   2 名以上、比身边的友方英雄多——背向身边敌人的中心（左右 `SPREAD_DEG`°），落地后离敌人最远、朝己方最近的塔走得多
//!   （`plan_exit`）；
//! - **追**（`plan_chase`）：`CHASE_NEAR`..`e_chase_r` 远、生命不高于 `PREY_HP`% 的敌方英雄（最残的先），他自己生命不低于
//!   `CHASE_HP`%——朝目标左右 `CHASE_DEG`° 内开门，落点比现在近 `CLOSER` 以上、离目标不近于 `KEEP`，落点旁除了目标最多一名
//!   敌方英雄。
//! 出口都在 `e_min`..`e_far` 内，一路和落点都不碰墙格（卡蜜尔钩墙附加包的地图），离地图边至少 `EDGE`。
//!
//! 开门：冷却 `e_cd_t`、`skill2_e` 动作 `e_anim` tick、门的画面 `league_bard_e_door`（播在他身上；数据里不跟随，留在原地）、
//! 音效；`e_wind` tick 后他和门边 `e_ride` 内的友方英雄一起在 `e_tick` tick 内强制位移过去（队友同样的位移，那里有墙就落在
//! 他出口旁，再不行就不带）；到了播出口门 `league_bard_e_door_out` 和队友身上的 `league_bard_e_ride`，都加速 `e_ms`%
//! `e_ms_t` tick（主包的 `league_bard_e_haste`，画面也是主包的）。宿主没挪人时逐 tick 自己走一步（`entity_set_pos`，泰隆的做法）。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。不用全局变量，服务端预模拟和你看的那场各算各的。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_bard.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_bard";

/// 主包巴德的名字（buff 都以它开头）。
fn bd(x: &str) -> String {
    format!("league_bard_{x}")
}

/// 墙格的边长（世界单位）。
pub const CELL: f64 = 32_000.0;
/// 查一条直线穿不穿墙的步长。
pub const STEP: f64 = 1_000.0;
/// 出口的方向数（一圈）。
pub const RAYS: usize = 48;
/// 背向敌人的方向左右这么多度内。
pub const SPREAD_DEG: f64 = 80.0;
/// 一条射线上出口往回缩的步长。
pub const RETRY: f64 = 4_000.0;
/// 出口离地图边至少这么远。
pub const EDGE: f64 = 8_000.0;
/// 朝己方塔每走 1 的分（离敌人每远 1 算 1）。
pub const HOME_W: f64 = 0.5;
/// 队友落不到同样位移处时，落在巴德出口旁这么远。
pub const BESIDE: f64 = 6_000.0;
/// 每隔几 tick 看一次。
pub const EVERY: usize = 3;
/// 撤：生命低于这个百分比、身边有敌方英雄就走。
pub const LOW_HP: usize = 45;
/// 追：朝目标左右这么多度内。
pub const CHASE_DEG: f64 = 35.0;
/// 追：比这近不开门（普攻够得着）。
pub const CHASE_NEAR: f64 = 45_000.0;
/// 追：落点要比现在近这么多。
pub const CLOSER: f64 = 20_000.0;
/// 追：落点离目标至少这么远（不落在他脸上）。
pub const KEEP: f64 = 15_000.0;
/// 追：目标生命不高于这个百分比。
pub const PREY_HP: usize = 50;
/// 追：巴德生命不低于这个百分比。
pub const CHASE_HP: usize = 40;
/// 追：落点这么远内（除目标外）最多一名敌方英雄。
pub const CROWD_R: f64 = 30_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_BARD_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_bard.log");
        }
    }
    PathBuf::from("league_bard.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the simulation thread, 2026-10-12)
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

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub e_cd_t: usize,
    pub e_wind: usize,
    pub e_anim: usize,
    pub e_tick: usize,
    pub e_far: usize,
    pub e_min: usize,
    pub e_ride: usize,
    pub e_near: usize,
    pub e_close: usize,
    pub e_ms: usize,
    pub e_ms_t: usize,
    pub e_chase_r: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            e_cd_t: 960,
            e_wind: 9,
            e_anim: 24,
            e_tick: 15,
            e_far: 60_000,
            e_min: 30_000,
            e_ride: 25_000,
            e_near: 30_000,
            e_close: 15_000,
            e_ms: 40,
            e_ms_t: 120,
            e_chase_r: 100_000,
        }
    }
}

/// `{"e_tick":15,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "e_cd_t" => &mut p.e_cd_t,
            "e_wind" => &mut p.e_wind,
            "e_anim" => &mut p.e_anim,
            "e_tick" => &mut p.e_tick,
            "e_far" => &mut p.e_far,
            "e_min" => &mut p.e_min,
            "e_ride" => &mut p.e_ride,
            "e_near" => &mut p.e_near,
            "e_close" => &mut p.e_close,
            "e_ms" => &mut p.e_ms,
            "e_ms_t" => &mut p.e_ms_t,
            "e_chase_r" => &mut p.e_chase_r,
            _ => continue,
        };
        *slot = v;
    }
    p
}

// ===================== 墙 =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一张墙格子：`cells[y][x]`（泰隆附加包的那张）。
#[derive(Clone, Debug, PartialEq)]
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

    pub fn size(&self) -> (f64, f64) {
        (self.cells.first().map_or(0, |r| r.len()) as f64 * CELL, self.cells.len() as f64 * CELL)
    }

    /// 在地图里、离边至少 `EDGE` 吗。
    pub fn roomy(&self, p: (f64, f64)) -> bool {
        let (w, h) = self.size();
        p.0 >= EDGE && p.1 >= EDGE && p.0 <= w - EDGE && p.1 <= h - EDGE
    }

    /// 世界坐标落在墙格里吗（地图外不算）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return false;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(false)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }

    /// 两点之间的直线碰到墙格吗（终点也算）。
    pub fn blocked(&self, a: (f64, f64), b: (f64, f64)) -> bool {
        let n = (dist(a, b) / STEP).ceil().max(1.0) as usize;
        (1..=n).any(|i| {
            let t = i as f64 / n as f64;
            self.is_wall(a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
        })
    }

    /// 从 `a` 走到 `b` 行吗：终点在地图里不贴边，一路没有墙。
    pub fn clear(&self, a: (f64, f64), b: (f64, f64)) -> bool {
        self.roomy(b) && !self.blocked(a, b)
    }
}

/// 这局是哪张图：站在墙里的英雄最少、墙又最多的那张（泰隆、卡蜜尔附加包的判断）。
pub fn current(grids: &[Grid], champions: &[(f64, f64)]) -> Option<usize> {
    grids
        .iter()
        .enumerate()
        .min_by_key(|(_, g)| {
            let inside = champions.iter().filter(|&&(x, y)| g.is_wall(x, y)).count();
            (inside, std::cmp::Reverse(g.walls()))
        })
        .map(|(i, _)| i)
}

fn unit(v: (f64, f64)) -> Option<(f64, f64)> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

// ===================== 出口 =====================

/// 门的出口：背向身边敌人（没有敌人就朝 `home`）的扇面里，一路不穿墙、落点不在墙里，落地后离最近的敌方英雄最远、
/// 朝 `home`（己方最近的塔）走得多的那一点。
pub fn plan_exit(p: &Params, g: &Grid, me: (f64, f64), foes: &[(f64, f64)], home: Option<(f64, f64)>) -> Option<(f64, f64)> {
    let near: Vec<&(f64, f64)> = foes.iter().filter(|f| dist(me, **f) <= p.e_near as f64 * 1.5).collect();
    let away = if near.is_empty() {
        home.and_then(|h| unit((h.0 - me.0, h.1 - me.1)))?
    } else {
        let c = near.iter().fold((0.0, 0.0), |s, f| (s.0 + f.0, s.1 + f.1));
        let c = (c.0 / near.len() as f64, c.1 / near.len() as f64);
        unit((me.0 - c.0, me.1 - c.1)).or_else(|| home.and_then(|h| unit((h.0 - me.0, h.1 - me.1))))?
    };
    let gap = |q: (f64, f64)| foes.iter().map(|f| dist(q, *f)).fold(1.0e9, f64::min);
    let homeward = |q: (f64, f64)| home.map_or(0.0, |h| dist(me, h) - dist(q, h));
    let cos = SPREAD_DEG.to_radians().cos();
    let far = p.e_far as f64;
    let min = (p.e_min as f64).min(far);
    (0..RAYS)
        .map(|i| {
            let a = i as f64 * std::f64::consts::TAU / RAYS as f64;
            (a.cos(), a.sin())
        })
        .filter(|d| d.0 * away.0 + d.1 * away.1 >= cos)
        .filter_map(|d| {
            let mut t = far;
            while t >= min {
                let to = (me.0 + d.0 * t, me.1 + d.1 * t);
                if g.clear(me, to) {
                    return Some(to);
                }
                t -= RETRY;
            }
            None
        })
        .map(|to| (to, gap(to) + HOME_W * homeward(to)))
        .max_by(|a, b| a.1.total_cmp(&b.1))
        .map(|(to, _)| to)
}

/// 跟着走的队友的落点：同样的位移；不行就巴德出口旁（朝队友原来那边 `BESIDE`），再不行就巴德的出口；都不行就不带。
pub fn ride_exit(g: &Grid, me: (f64, f64), to: (f64, f64), ally: (f64, f64)) -> Option<(f64, f64)> {
    let same = (ally.0 + to.0 - me.0, ally.1 + to.1 - me.1);
    let side = unit((ally.0 - me.0, ally.1 - me.1)).map(|u| (to.0 + u.0 * BESIDE, to.1 + u.1 * BESIDE));
    [Some(same), side, Some(to)].into_iter().flatten().find(|&q| g.clear(ally, q))
}

// ===================== 什么时候开 =====================

/// 一个敌方英雄：位置、生命百分比、id。
#[derive(Clone, Copy, Debug)]
pub struct Foe {
    pub at: (f64, f64),
    pub hp_pct: usize,
    pub id: usize,
}

/// 该撤了吗：残血而身边有敌方英雄；敌方英雄贴脸；或身边敌方英雄 2 名以上、比身边的友方英雄（`allies` 个，不算他）多。
pub fn wants_out(p: &Params, me: (f64, f64), hp_pct: usize, foes: &[Foe], allies: usize) -> bool {
    let near = foes.iter().filter(|f| dist(me, f.at) <= p.e_near as f64).count();
    let close = foes.iter().any(|f| dist(me, f.at) <= p.e_close as f64);
    (hp_pct < LOW_HP && near >= 1) || close || (near >= 2 && near > allies + 1)
}

/// 追：远处残血的敌方英雄（最残的先），朝他开门，落点近了 `CLOSER` 以上、离他不近于 `KEEP`、旁边不是人堆。
pub fn plan_chase(p: &Params, g: &Grid, me: (f64, f64), hp_pct: usize, foes: &[Foe]) -> Option<((f64, f64), usize)> {
    if hp_pct < CHASE_HP {
        return None;
    }
    let mut prey: Vec<&Foe> = foes
        .iter()
        .filter(|f| {
            let d = dist(me, f.at);
            f.hp_pct <= PREY_HP && d > CHASE_NEAR && d <= p.e_chase_r as f64
        })
        .collect();
    prey.sort_by_key(|f| f.hp_pct);
    let cos = CHASE_DEG.to_radians().cos();
    let far = p.e_far as f64;
    let min = (p.e_min as f64).min(far);
    for t in prey {
        let Some(toward) = unit((t.at.0 - me.0, t.at.1 - me.1)) else { continue };
        let now = dist(me, t.at);
        let best = (0..RAYS)
            .map(|i| {
                let a = i as f64 * std::f64::consts::TAU / RAYS as f64;
                (a.cos(), a.sin())
            })
            .filter(|d| d.0 * toward.0 + d.1 * toward.1 >= cos)
            .flat_map(|d| {
                let mut out = Vec::new();
                let mut s = far;
                while s >= min {
                    out.push((me.0 + d.0 * s, me.1 + d.1 * s));
                    s -= RETRY;
                }
                out
            })
            .filter(|&to| g.clear(me, to))
            .filter(|&to| {
                let d = dist(to, t.at);
                d + CLOSER <= now && d >= KEEP
            })
            .filter(|&to| foes.iter().filter(|f| f.id != t.id && dist(to, f.at) <= CROWD_R).count() <= 1)
            .min_by(|a, b| dist(*a, t.at).total_cmp(&dist(*b, t.at)));
        if let Some(to) = best {
            return Some((to, t.id));
        }
    }
    None
}

// ===================== 小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    sim.get_entity(id).map(|e| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

// ===================== 被动 =====================

fn has_cc(sim: &StableSim<'_>, id: usize, kinds: &[CcKindV1]) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
    })
}

/// 不能开门的状态：硬控、沉默、禁位移技能、正被强制位移（泰隆附加包的那张表）。
const NO_DOOR: [CcKindV1; 9] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::BlockSkill,
    CcKindV1::BlockMoveSkill,
    CcKindV1::ForceMove,
];

fn hp_pct(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(100, |e| {
        let (hp, max) = e.hp();
        hp * 100 / max.max(1)
    })
}

/// 一段正在走的路：谁、去哪、上一 tick 在哪（看宿主有没有挪他）、走到第几 tick 为止、每 tick 走多远。
#[derive(Clone, Debug)]
struct Trip {
    id: usize,
    goal: (f64, f64),
    last: (f64, f64),
    until: usize,
    step: f64,
}

/// 开了门、还没走的一趟：第几 tick 出发、去哪、带谁（id、他自己的落点）、是撤还是追。
#[derive(Clone, Debug)]
struct Pending {
    at: usize,
    to: (f64, f64),
    riders: Vec<(usize, (f64, f64))>,
    why: String,
}

/// 每个巴德一份：参数、开了门待走的一趟、正在走的路、到达的时刻（出口门和加速）、开门次数。
#[derive(Clone, Default)]
struct Door {
    p: Params,
    pending: Option<Pending>,
    trips: Vec<Trip>,
    arrive: Option<(usize, Vec<usize>)>,
    doors: usize,
}

impl Door {
    fn send(&mut self, sim: &mut StableSim<'_>, id: usize, to: (f64, f64)) {
        let Some(from) = pos(sim, id) else { return };
        let ticks = self.p.e_tick.max(1);
        let d = dist(from, to);
        let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
        mv.dx = (to.0 - from.0).round() as i64;
        mv.dy = (to.1 - from.1).round() as i64;
        mv.speed = (d / ticks as f64).ceil() as u64;
        sim.apply_cc(id, &mv);
        self.trips.push(Trip { id, goal: to, last: from, until: sim.tick() + ticks + 2, step: d / ticks as f64 });
    }

    fn haste(&self, sim: &mut StableSim<'_>, id: usize) {
        let name = bd("e_haste");
        sim.entity_remove_buff(id, &name);
        let mut b = BuffV1::timed(&name, self.p.e_ms_t);
        b.move_speed_mult = self.p.e_ms as i32;
        sim.add_buff(id, &b);
    }

    /// 看局面：撤或追，挑好出口就开门（动作、门、音效、冷却），`e_wind` tick 后出发。
    fn decide(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64)) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let mut champs = Vec::new();
        let mut foes = Vec::new();
        let mut friends = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_champion() || !u.is_alive() {
                continue;
            }
            let (x, y) = u.pos();
            let at = (x as f64, y as f64);
            champs.push(at);
            if u.team() != team {
                if u.is_targetable() {
                    let (hp, max) = u.hp();
                    foes.push(Foe { at, hp_pct: hp * 100 / max.max(1), id: u.id() });
                }
            } else if u.id() != me && u.is_targetable() {
                friends.push((u.id(), at));
            }
        }
        let allies = friends.iter().filter(|(_, a)| dist(here, *a) <= self.p.e_near as f64).count();
        let mine = hp_pct(sim, me);
        let home = (0..sim.tower_count())
            .filter_map(|k| sim.get_entity(sim.tower_id_at(k)))
            .filter(|t| t.team() == team && t.is_alive())
            .map(|t| {
                let (x, y) = t.pos();
                (x as f64, y as f64)
            })
            .min_by(|a, b| dist(here, *a).total_cmp(&dist(here, *b)));
        let grids = Grid::builtin();
        let Some(gi) = current(&grids, &champs) else { return };
        let g = &grids[gi];
        let plan = if wants_out(&self.p, here, mine, &foes, allies) {
            plan_exit(&self.p, g, here, &foes.iter().map(|f| f.at).collect::<Vec<_>>(), home).map(|to| (to, "out".to_string()))
        } else {
            plan_chase(&self.p, g, here, mine, &foes).map(|(to, id)| (to, format!("after #{id}")))
        };
        let Some((to, why)) = plan else { return };
        let riders = friends
            .iter()
            .filter(|(_, a)| dist(here, *a) <= self.p.e_ride as f64)
            .filter_map(|&(id, a)| ride_exit(g, here, to, a).map(|q| (id, q)))
            .collect();
        let tick = sim.tick();
        sim.entity_remove_buff(me, &bd("e_cd"));
        sim.add_buff(me, &BuffV1::timed(&bd("e_cd"), self.p.e_cd_t));
        let mut cc = CcV1::of_kind(CcKindV1::Animation, self.p.e_anim as u64);
        cc.set_name("skill2_e");
        sim.apply_cc(me, &cc);
        let on_me = InputTargetV1::target(me);
        sim.play_view_effect(&bd("e_door"), me, &on_me, 0, 0, 0);
        sim.play_sfx(&bd("e_cast"), me, &on_me);
        sim.play_sfx(&bd("vo_e"), me, &on_me);
        self.doors += 1;
        self.pending = Some(Pending { at: tick + self.p.e_wind, to, riders, why });
    }

    /// 出发：他和带上的队友一起走；记下到达的时刻。
    fn go(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64), plan: Pending) {
        if !g_clear_now(sim, here, plan.to) {
            wlog(format!("{} DOOR #{}: the way to {} is no longer clear, he stays", head(sim, me), self.doors, pt(plan.to)));
            return;
        }
        self.send(sim, me, plan.to);
        let mut taken = Vec::new();
        let mut ids = Vec::new();
        for (id, q) in plan.riders {
            if sim.get_entity(id).is_some_and(|e| e.is_alive() && e.is_targetable()) {
                self.send(sim, id, q);
                taken.push(format!("#{id}->{}", pt(q)));
                ids.push(id);
            }
        }
        self.arrive = Some((sim.tick() + self.p.e_tick, ids));
        if self.doors <= 80 || self.doors % 25 == 0 {
            wlog(format!(
                "{} DOOR #{} {}: {} -> {} ({:.0}), hp {}%, allies [{}]",
                head(sim, me),
                self.doors,
                plan.why,
                pt(here),
                pt(plan.to),
                dist(here, plan.to),
                hp_pct(sim, me),
                taken.join(", ")
            ));
        }
    }

    /// 走路中：宿主没挪人就自己走一步；到了、或时间到了就停。
    fn follow(&mut self, sim: &mut StableSim<'_>) {
        let tick = sim.tick();
        let mut keep = Vec::new();
        for mut t in std::mem::take(&mut self.trips) {
            let Some(here) = pos(sim, t.id) else { continue };
            let d = dist(here, t.goal);
            if d < t.step.max(500.0) || tick > t.until {
                continue;
            }
            if dist(t.last, here) < 1.0 {
                let s = t.step.min(d);
                let next = (here.0 + (t.goal.0 - here.0) / d * s, here.1 + (t.goal.1 - here.1) / d * s);
                sim.entity_set_pos(t.id, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64);
                t.last = next;
            } else {
                t.last = here;
            }
            keep.push(t);
        }
        self.trips = keep;
    }
}

/// 出发那一刻再看一次路（门开着的几 tick 里他可能被推开了）。
fn g_clear_now(sim: &StableSim<'_>, here: (f64, f64), to: (f64, f64)) -> bool {
    let mut champs = Vec::new();
    for i in 0..sim.entity_count() {
        if let Some(u) = sim.entity_at(i) {
            if u.is_champion() && u.is_alive() {
                let (x, y) = u.pos();
                champs.push((x as f64, y as f64));
            }
        }
    }
    let grids = Grid::builtin();
    current(&grids, &champs).is_some_and(|gi| grids[gi].clear(here, to))
}

impl StablePassive for Door {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.pending = None;
        self.trips.clear();
        self.arrive = None;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Bard (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if !self.trips.is_empty() {
            self.follow(sim);
        }
        let tick = sim.tick();
        if let Some((at, ids)) = self.arrive.clone() {
            if tick >= at {
                self.arrive = None;
                if sim.get_entity(me).is_some_and(|e| e.is_alive()) {
                    let on_me = InputTargetV1::target(me);
                    sim.play_view_effect(&bd("e_door_out"), me, &on_me, 0, 0, 0);
                    sim.play_sfx(&bd("e_out"), me, &on_me);
                    self.haste(sim, me);
                }
                for id in ids {
                    if sim.get_entity(id).is_some_and(|e| e.is_alive()) {
                        sim.play_view_effect(&bd("e_ride"), me, &InputTargetV1::target(id), 0, 0, 0);
                        self.haste(sim, id);
                    }
                }
            }
        }
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() || !e.is_targetable() {
            self.pending = None;
            return;
        }
        let Some(here) = pos(sim, me) else { return };
        if let Some(plan) = self.pending.clone() {
            if tick >= plan.at {
                self.pending = None;
                self.go(sim, me, here, plan);
            }
            return;
        }
        if tick % EVERY != 0 || !self.trips.is_empty() || has_buff(sim, me, &bd("e_cd")) || has_cc(sim, me, &NO_DOOR) {
            return;
        }
        self.decide(sim, me, here);
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.pending = None;
        self.trips.clear();
        self.arrive = None;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Bard's Magical Journey: the door's exit back toward his side, clear of the map's rocks) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:door"), Door::default());
    host.log(LogLevel::Info, "league_bard v1 loaded (Bard's Magical Journey exits clear of walls).");
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

    fn at(cx: f64, cy: f64) -> (f64, f64) {
        (cx * CELL, cy * CELL)
    }

    /// 一堵竖墙（第 5 列，第 2-7 行）。
    fn wall() -> Grid {
        let mut rows = vec![".........."; 10];
        for r in rows.iter_mut().take(8).skip(2) {
            *r = ".....#....";
        }
        Grid::from_rows(&rows)
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"e_far":50000,"x":1}"#), Params { e_far: 50_000, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_exit_never_crosses_a_wall() {
        let p = Params::default();
        let g = wall();
        // the wall right behind him, the enemy in front: the door turns aside, the path and the exit clear of rock
        let me = at(4.6, 4.5);
        let foes = [at(3.6, 4.5)];
        let to = plan_exit(&p, &g, me, &foes, None).unwrap();
        assert!(!g.blocked(me, to), "{to:?}");
        assert!(dist(to, foes[0]) > dist(me, foes[0]));
        assert!(dist(me, to) >= p.e_min as f64 - 1.0);
    }

    #[test]
    fn with_open_ground_he_goes_straight_back_and_homeward() {
        let p = Params::default();
        let g = Grid::from_rows(&vec![".........."; 10]);
        let me = at(5.0, 5.0);
        let foes = [at(6.0, 5.0)];
        let to = plan_exit(&p, &g, me, &foes, Some(at(1.0, 5.0))).unwrap();
        assert!(to.0 < me.0 - 50_000.0, "{to:?}");
        // no enemy near: toward his own tower
        let to2 = plan_exit(&p, &g, me, &[at(9.5, 9.5)], Some(at(5.0, 1.0))).unwrap();
        assert!(to2.1 < me.1 - 25_000.0, "{to2:?}");
    }

    #[test]
    fn boxed_in_he_stays() {
        let p = Params::default();
        // walls everywhere but his own cell
        let mut rows = vec!["##########"; 10];
        rows[5] = "#####.####";
        let g = Grid::from_rows(&rows);
        assert_eq!(plan_exit(&p, &g, at(5.5, 5.5), &[at(5.6, 5.5)], None), None);
    }

    #[test]
    fn allies_ride_beside_him_when_their_own_way_is_walled() {
        let g = wall();
        let me = at(4.0, 8.5);
        let to = at(4.0, 6.5);
        // the ally's own shifted exit is inside the wall (column 5): he lands beside Bard's exit
        let ally = at(5.3, 8.6);
        let q = ride_exit(&g, me, to, ally).unwrap();
        assert!(!g.blocked(ally, q));
        assert!(dist(q, to) <= BESIDE + 1.0);
    }

    #[test]
    fn on_the_moba_map_no_exit_touches_rock() {
        let p = Params::default();
        let g = &Grid::builtin()[0];
        let (w, h) = g.size();
        let (mut found, mut none) = (0, 0);
        let mut y = 20_000.0;
        while y < h {
            let mut x = 20_000.0;
            while x < w {
                if !g.is_wall(x, y) {
                    for (dx, dy) in [(10_000.0, 0.0), (-10_000.0, 0.0), (0.0, 10_000.0), (0.0, -10_000.0)] {
                        let me = (x, y);
                        match plan_exit(&p, g, me, &[(x + dx, y + dy)], None) {
                            Some(to) => {
                                assert!(g.clear(me, to), "{me:?} -> {to:?}");
                                found += 1;
                            }
                            None => none += 1,
                        }
                    }
                }
                x += 24_000.0;
            }
            y += 24_000.0;
        }
        assert!(found > 20 * none, "{found} exits, {none} boxed in");
    }

    #[test]
    fn the_moba_map_has_its_ninety_wall_cells() {
        assert_eq!(Grid::builtin()[0].walls(), 90);
    }

    fn foe(p: (f64, f64), hp_pct: usize, id: usize) -> Foe {
        Foe { at: p, hp_pct, id }
    }

    #[test]
    fn when_he_leaves() {
        let p = Params::default();
        let me = at(5.0, 5.0);
        // hurt with one near; one right on him; two near and he alone
        assert!(wants_out(&p, me, 30, &[foe(at(5.8, 5.0), 100, 1)], 0));
        assert!(wants_out(&p, me, 100, &[foe(at(5.3, 5.0), 100, 1)], 3));
        assert!(wants_out(&p, me, 100, &[foe(at(5.8, 5.0), 100, 1), foe(at(5.0, 5.8), 100, 2)], 0));
        // healthy with one at arm's length, or two near and allies with him: he stays
        assert!(!wants_out(&p, me, 100, &[foe(at(5.8, 5.0), 100, 1)], 0));
        assert!(!wants_out(&p, me, 100, &[foe(at(5.8, 5.0), 100, 1), foe(at(5.0, 5.8), 100, 2)], 2));
    }

    #[test]
    fn he_chases_a_hurt_champion_through_his_door() {
        let p = Params::default();
        let g = Grid::from_rows(&vec![".........."; 10]);
        let me = at(2.0, 5.0);
        let prey = foe(at(5.0, 5.0), 30, 7);
        let (to, id) = plan_chase(&p, &g, me, 80, &[prey]).unwrap();
        assert_eq!(id, 7);
        assert!(dist(to, prey.at) + CLOSER <= dist(me, prey.at) && dist(to, prey.at) >= KEEP, "{to:?}");
        // healthy target, or Bard hurt, or already close: no door
        assert!(plan_chase(&p, &g, me, 80, &[foe(at(5.0, 5.0), 90, 7)]).is_none());
        assert!(plan_chase(&p, &g, me, 20, &[prey]).is_none());
        assert!(plan_chase(&p, &g, me, 80, &[foe(at(3.0, 5.0), 30, 7)]).is_none());
        // not into a crowd: wherever it lands, at most one enemy but the prey within CROWD_R
        let crowd = [prey, foe(at(4.2, 5.0), 100, 8), foe(at(4.2, 4.6), 100, 9), foe(at(4.2, 5.4), 100, 10)];
        if let Some((to, _)) = plan_chase(&p, &g, me, 80, &crowd) {
            assert!(crowd[1..].iter().filter(|f| dist(to, f.at) <= CROWD_R).count() <= 1, "{to:?}");
        }
    }

    #[test]
    fn a_chase_never_crosses_a_wall() {
        let p = Params::default();
        let g = wall();
        // the prey behind the wall: the door goes round it or not at all, never through
        let me = at(3.5, 4.5);
        if let Some((to, _)) = plan_chase(&p, &g, me, 80, &[foe(at(7.0, 4.5), 30, 7)]) {
            assert!(g.clear(me, to), "{to:?}");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["e_cd", "e_haste", "e_door", "e_door_out", "e_ride"] {
            assert!(bd(x).len() <= BUFF_NAME_CAP);
        }
    }
}
