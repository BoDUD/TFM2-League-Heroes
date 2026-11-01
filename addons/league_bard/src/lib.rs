//! 巴德附加包：「神奇旅程」什么时候开、往哪开都由本包决定（用户：「巴德的传送别乱放啊 逻辑改一改」「往己方后撤，不穿墙」，
//! 然后「传送门还是有点怪 你也要用来追人啊 智能一点 现在一局比赛里放不出来几次都」）。
//!
//! 主包是纯数据：技能 2 被放出来、又正好被近身时才开门（一局没几次），朝最近敌人的反方向强制位移；引擎的强制位移不管地图的墙，
//! 四成左右穿过野区的石头。`mod.override_info` 把主包的巴德换成 `override/` 里的副本（tools/kit/build_bard.py 的 native=1）：
//! 技能 2 只剩圣坛，门全归本包的被动 `league_bard:door`。被动每 `EVERY` tick 看一次，门好了（他身上没有 `league_bard_e_cd`）、
//! 他活着、没被控时：
//! - **撤**（`wants_out`）：生命低于 `LOW_HP`% 而 `e_near` 内有敌方英雄；或 `e_close` 内有敌方英雄；或 `e_near` 内敌方英雄
//!   2 名以上、比身边的友方英雄多——背向身边敌人的中心（左右 `SPREAD_DEG`°）`e_reach` 内有墙的方向，门穿过墙落到另一边，
//!   落地后离敌人远 `ESCAPE_GAIN` 以上，挑离敌人最远、朝己方最近的塔走得多的（`plan_exit`）；
//! - **追**（`plan_chase`）：墙后、`CHASE_NEAR`..`e_chase_r` 远、生命不高于 `PREY_HP`% 的敌方英雄（最残的先），他自己生命不低于
//!   `CHASE_HP`%——朝目标左右 `CHASE_DEG`° 内找墙穿过去，落点比现在近 `CLOSER` 以上、离目标不近于 `KEEP`，落点旁除了目标
//!   最多一名敌方英雄。
//! - **支援**（`plan_help`）：没危险、没人可追时，`HELP_NEAR`..`HELP_FAR` 远、身边有敌方英雄的友方英雄（敌人最多的先），他自己
//!   生命不低于 `HELP_HP`%——朝队友找墙穿过去，落点离队友近 `HELP_GAIN` 以上、旁边敌方英雄不多于 `HELP_CROWD` 名
//!   （「加上吧 开门去支援」）。
//! 门只开在墙上（用户：「门的逻辑不对吧 只能在墙上放吧」，英雄联盟的神奇旅程是穿过地形的单向通道）：附近没有墙就不开；穿墙
//! 落点不在墙格里（卡蜜尔钩墙附加包的地图）、离地图边至少 `EDGE`、离起点不超过 `e_far`。
//!
//! 开门：冷却 `e_cd_t`；他先飞到墙前（入口离墙 `ENTRY_BACK`），门在他身后贴着墙打开（buff 画面 `league_bard_e_doorb`，门的 2.5 倍）、`skill2_e` 动作 `e_anim` tick、
//! 音效；`e_wind` tick 后他和门边 `e_ride` 内的友方英雄一起在 `e_tick` tick 内强制位移过去（队友同样的位移，那里有墙就落在
//! 他出口旁，再不行就不带）；到了出口门在他身后打开（buff 画面 `league_bard_e_outb`），队友身上的 `league_bard_e_rideb`，都加速 `e_ms`%
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
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_bard") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

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
pub const SPREAD_DEG: f64 = 75.0;
/// 出口离地图边至少这么远。
pub const EDGE: f64 = 8_000.0;
/// 朝己方塔每走 1 的分（离敌人每远 1 算 1）。
pub const HOME_W: f64 = 0.5;
/// 队友落不到同样位移处时，落在巴德出口旁这么远。
pub const BESIDE: f64 = 6_000.0;
/// 每隔几 tick 看一次。
pub const EVERY: usize = 3;
/// 穿墙的落点离墙的另一边再走这么远（别落在墙边上卡住）。
pub const MARGIN: f64 = 4_000.0;
/// 门的入口在墙前这么远（他站在门前，门贴着墙）。
pub const ENTRY_BACK: f64 = 6_000.0;
/// 他在墙前的门前站多久才穿进去（tick）：门开、闪光，看得见（0.15 秒时门只开出一条线：「为什么还是没特效？」）。
pub const STAND: usize = 24;
/// 出了门他在出口门前站多久（tick），出口门开了再收。
pub const OUT_STAND: usize = 24;
/// 撤：落地后离最近的敌方英雄至少比现在远这么多。
pub const ESCAPE_GAIN: f64 = 10_000.0;
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
pub const PREY_HP: usize = 60;
/// 追：巴德生命不低于这个百分比。
pub const CHASE_HP: usize = 40;
/// 追：落点这么远内（除目标外）最多一名敌方英雄。
pub const CROWD_R: f64 = 30_000.0;
/// 支援：队友这么远内有敌方英雄就是在打架。
pub const FIGHT_R: f64 = 35_000.0;
/// 支援：队友离他这么远以上才开门（近了走过去）、这么远以内才去。
pub const HELP_NEAR: f64 = 60_000.0;
pub const HELP_FAR: f64 = 220_000.0;
/// 支援：巴德生命不低于这个百分比、身边 `e_near` 内没有敌方英雄。
pub const HELP_HP: usize = 50;
/// 支援：落点要比现在离队友近这么多。
pub const HELP_GAIN: f64 = 30_000.0;
/// 支援：落点这么远内的敌方英雄不多于 2 名（不一头扎进人堆）。
pub const HELP_CROWD: usize = 2;

/// 争龙：大小龙这么远内有敌方英雄，就是对面在打龙。
pub const CONTEST_R: f64 = 35_000.0;
/// 争龙：龙的生命低于这个百分比（已经有人在打）。
pub const TAKEN_HP: usize = 95;
/// 争龙：`league_bard_r_drk` 标记挂几 tick（每 `EVERY` tick 重挂；副本的大招读到它就对龙放）。
pub const DRK_T: usize = 6;

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
    pub e_reach: usize,
    pub e_fly: usize,
    pub e_ride: usize,
    pub e_near: usize,
    pub e_close: usize,
    pub e_ms: usize,
    pub e_ms_t: usize,
    pub e_chase_r: usize,
    pub r_range: usize,
    pub r_arm_range: usize,
    pub r_r: usize,
    pub r_t: usize,
    pub r_lag: usize,
    pub r_travel: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            e_cd_t: 960,
            e_wind: 9,
            e_anim: 24,
            e_tick: 15,
            e_far: 130_000,
            e_min: 30_000,
            e_reach: 60_000,
            e_fly: 6_000,
            e_ride: 25_000,
            e_near: 30_000,
            e_close: 15_000,
            e_ms: 40,
            e_ms_t: 120,
            e_chase_r: 100_000,
            r_range: 80_000,
            r_arm_range: 90_000,
            r_r: 36_000,
            r_t: 150,
            r_lag: 15,
            r_travel: 24,
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
            "e_reach" => &mut p.e_reach,
            "e_fly" => &mut p.e_fly,
            "e_ride" => &mut p.e_ride,
            "e_near" => &mut p.e_near,
            "e_close" => &mut p.e_close,
            "e_ms" => &mut p.e_ms,
            "e_ms_t" => &mut p.e_ms_t,
            "e_chase_r" => &mut p.e_chase_r,
            "r_range" => &mut p.r_range,
            "r_arm_range" => &mut p.r_arm_range,
            "r_r" => &mut p.r_r,
            "r_t" => &mut p.r_t,
            "r_lag" => &mut p.r_lag,
            "r_travel" => &mut p.r_travel,
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

    /// 朝 `dir`（单位向量）穿墙（泰隆附加包的翻墙）：`reach` 内碰到墙、一路穿过去，落在墙另一边 `MARGIN` 处；落点不超过
    /// `far`、不在墙里、在地图里不贴边。返回 (入口：墙前 `ENTRY_BACK` 处，出口)。
    pub fn vault(&self, from: (f64, f64), dir: (f64, f64), reach: f64, far: f64) -> Option<((f64, f64), (f64, f64))> {
        let at = |t: f64| (from.0 + dir.0 * t, from.1 + dir.1 * t);
        let mut t = STEP;
        while t <= reach && !self.is_wall(at(t).0, at(t).1) {
            t += STEP;
        }
        if t > reach {
            return None;
        }
        let entry = at((t - ENTRY_BACK).max(0.0));
        while t <= far && self.is_wall(at(t).0, at(t).1) {
            t += STEP;
        }
        let to = at(t + MARGIN);
        (t + MARGIN <= far && !self.is_wall(to.0, to.1) && self.roomy(to)).then_some((entry, to))
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

// ===================== 什么时候开、往哪开 =====================

/// 一个敌方英雄：位置、生命百分比、id。
#[derive(Clone, Copy, Debug)]
pub struct Foe {
    pub at: (f64, f64),
    pub hp_pct: usize,
    pub id: usize,
}

/// 一扇门：入口（墙前）、出口（墙后）。
pub type Way = ((f64, f64), (f64, f64));

/// 该撤了吗：残血而身边有敌方英雄；敌方英雄贴脸；或身边敌方英雄 2 名以上、比身边的友方英雄（`allies` 个，不算他）多。
pub fn wants_out(p: &Params, me: (f64, f64), hp_pct: usize, foes: &[Foe], allies: usize) -> bool {
    let near = foes.iter().filter(|f| dist(me, f.at) <= p.e_near as f64).count();
    let close = foes.iter().any(|f| dist(me, f.at) <= p.e_close as f64);
    (hp_pct < LOW_HP && near >= 1) || close || (near >= 2 && near > allies + 1)
}

fn rays() -> impl Iterator<Item = (f64, f64)> {
    (0..RAYS).map(|i| {
        let a = i as f64 * std::f64::consts::TAU / RAYS as f64;
        (a.cos(), a.sin())
    })
}

/// 撤：背向身边敌人的中心（左右 `SPREAD_DEG`°）、`e_reach` 内有墙的方向，门穿过墙落到另一边（`Grid::vault`），落地后离最近的
/// 敌方英雄至少远 `ESCAPE_GAIN`；挑离敌人最远、又朝 `home`（己方最近的塔）走得多的那一处。附近没有墙就不开门（英雄联盟的
/// 门只开在地形上）。
pub fn plan_exit(p: &Params, g: &Grid, me: (f64, f64), foes: &[(f64, f64)], home: Option<(f64, f64)>) -> Option<Way> {
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
    let now = gap(me);
    let cos = SPREAD_DEG.to_radians().cos();
    rays()
        .filter(|d| d.0 * away.0 + d.1 * away.1 >= cos)
        .filter_map(|d| g.vault(me, d, p.e_reach as f64, p.e_far as f64))
        .filter(|&(_, to)| foes.is_empty() || gap(to) >= now + ESCAPE_GAIN)
        .map(|(entry, to)| ((entry, to), gap(to) + HOME_W * homeward(to)))
        .max_by(|a, b| a.1.total_cmp(&b.1))
        .map(|(door, _)| door)
}

/// 追：墙后（隔着墙格）、`CHASE_NEAR`..`e_chase_r` 远、生命不高于 `PREY_HP`% 的敌方英雄（最残的先），他自己生命不低于
/// `CHASE_HP`%——朝目标左右 `CHASE_DEG`° 内找墙穿过去，落点比现在近 `CLOSER` 以上、离目标不近于 `KEEP`，落点旁除了目标最多
/// 一名敌方英雄。
pub fn plan_chase(p: &Params, g: &Grid, me: (f64, f64), hp_pct: usize, foes: &[Foe]) -> Option<(Way, usize)> {
    if hp_pct < CHASE_HP {
        return None;
    }
    let mut prey: Vec<&Foe> = foes
        .iter()
        .filter(|f| {
            let d = dist(me, f.at);
            f.hp_pct <= PREY_HP && d > CHASE_NEAR && d <= p.e_chase_r as f64 && g.blocked(me, f.at)
        })
        .collect();
    prey.sort_by_key(|f| f.hp_pct);
    let cos = CHASE_DEG.to_radians().cos();
    for t in prey {
        let Some(toward) = unit((t.at.0 - me.0, t.at.1 - me.1)) else { continue };
        let now = dist(me, t.at);
        let best = rays()
            .filter(|d| d.0 * toward.0 + d.1 * toward.1 >= cos)
            .filter_map(|d| g.vault(me, d, p.e_reach as f64, p.e_far as f64))
            .filter(|&(_, to)| {
                let d = dist(to, t.at);
                d + CLOSER <= now && d >= KEEP
            })
            .filter(|&(_, to)| foes.iter().filter(|f| f.id != t.id && dist(to, f.at) <= CROWD_R).count() <= 1)
            .min_by(|a, b| dist(a.1, t.at).total_cmp(&dist(b.1, t.at)));
        if let Some(to) = best {
            return Some((to, t.id));
        }
    }
    None
}

/// 支援：远处（`HELP_NEAR`..`HELP_FAR`）正在打架（`FIGHT_R` 内有敌方英雄）的友方英雄，他自己生命不低于 `HELP_HP`%、身边
/// 没有敌方英雄——朝那个队友左右 `CHASE_DEG`° 内找墙穿过去，落点离队友近 `HELP_GAIN` 以上、旁边（`CROWD_R`）敌方英雄不多于
/// `HELP_CROWD` 名；先帮身边敌人最多的那一个（英雄联盟里巴德常这样开门游走支援）。
pub fn plan_help(
    p: &Params,
    g: &Grid,
    me: (f64, f64),
    hp_pct: usize,
    foes: &[Foe],
    friends: &[(usize, (f64, f64))],
) -> Option<(Way, usize)> {
    if hp_pct < HELP_HP || foes.iter().any(|f| dist(me, f.at) <= p.e_near as f64) {
        return None;
    }
    let crowd = |q: (f64, f64), r: f64| foes.iter().filter(|f| dist(q, f.at) <= r).count();
    let mut fights: Vec<&(usize, (f64, f64))> = friends
        .iter()
        .filter(|(_, a)| {
            let d = dist(me, *a);
            d >= HELP_NEAR && d <= HELP_FAR && crowd(*a, FIGHT_R) >= 1
        })
        .collect();
    fights.sort_by_key(|(_, a)| std::cmp::Reverse(crowd(*a, FIGHT_R)));
    let cos = CHASE_DEG.to_radians().cos();
    for &(id, ally) in fights {
        let Some(toward) = unit((ally.0 - me.0, ally.1 - me.1)) else { continue };
        let now = dist(me, ally);
        let best = rays()
            .filter(|d| d.0 * toward.0 + d.1 * toward.1 >= cos)
            .filter_map(|d| g.vault(me, d, p.e_reach as f64, p.e_far as f64))
            .filter(|&(_, to)| dist(to, ally) + HELP_GAIN <= now && crowd(to, CROWD_R) <= HELP_CROWD)
            .min_by(|a, b| dist(a.1, ally).total_cmp(&dist(b.1, ally)));
        if let Some(to) = best {
            return Some((to, id));
        }
    }
    None
}

/// 跟着走的队友的落点：同样的位移；不行就巴德出口旁（朝队友原来那边 `BESIDE`），再不行就巴德的出口；落点要在地图里、
/// 不在墙格里（路上穿墙，和他一样）。都不行就不带。
pub fn ride_exit(g: &Grid, me: (f64, f64), to: (f64, f64), ally: (f64, f64)) -> Option<(f64, f64)> {
    let same = (ally.0 + to.0 - me.0, ally.1 + to.1 - me.1);
    let side = unit((ally.0 - me.0, ally.1 - me.1)).map(|u| (to.0 + u.0 * BESIDE, to.1 + u.1 * BESIDE));
    [Some(same), side, Some(to)].into_iter().flatten().find(|&q| g.roomy(q) && !g.is_wall(q.0, q.1))
}

// ===================== 争龙：对大小龙放大招 =====================

/// 一条大小龙：实体、位置、生命百分比、是不是大龙。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Obj {
    pub id: usize,
    pub at: (f64, f64),
    pub hp_pct: usize,
    pub epic: bool,
}

/// 争龙时冻哪条龙（用户：「给巴德加上争大小龙时主动对龙放大招拖时间」，英雄联盟里巴德用命运之轮把龙定住、等队友赶到）：
/// 大招射程 `r_range` 内、生命低于 `TAKEN_HP`%（已经有人在打）、`CONTEST_R` 内有敌方英雄、命运之轮的圈 `r_r` 里没有友方英雄
/// （巴德自己也不在，免得把自己人一起冻住），而且 `r_arm_range` 内有敌方英雄（大招放得出来）。大龙先，其次身边敌人多的。
pub fn pick_objective(p: &Params, me: (f64, f64), objs: &[Obj], foes: &[(f64, f64)], allies: &[(f64, f64)]) -> Option<Obj> {
    if !foes.iter().any(|f| dist(me, *f) <= p.r_arm_range as f64) {
        return None;
    }
    objs.iter()
        .filter(|o| dist(me, o.at) <= p.r_range as f64 && o.hp_pct < TAKEN_HP)
        .filter(|o| !allies.iter().any(|a| dist(*a, o.at) <= p.r_r as f64))
        .map(|o| (*o, foes.iter().filter(|f| dist(**f, o.at) <= CONTEST_R).count()))
        .filter(|(_, n)| *n > 0)
        .max_by_key(|(o, n)| (o.epic, *n))
        .map(|(o, _)| o)
}

/// 场上的局面：巴德的位置、看得见的大小龙、看得见的敌方英雄、友方英雄（含他自己）。
fn objective_now(sim: &StableSim<'_>, p: &Params, me: usize) -> Option<Obj> {
    let e = sim.get_entity(me)?;
    let team = e.team();
    let here = (e.pos().0 as f64, e.pos().1 as f64);
    let (mut objs, mut foes, mut allies) = (Vec::new(), Vec::new(), Vec::new());
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if !u.is_alive() {
            continue;
        }
        let at = (u.pos().0 as f64, u.pos().1 as f64);
        match u.kind() {
            Some(k @ (EntityKindV1::Epic | EntityKindV1::Serpen)) => {
                if u.is_targetable() && sim.is_visible(team, u.id()) {
                    let (hp, max) = u.hp();
                    objs.push(Obj { id: u.id(), at, hp_pct: hp * 100 / max.max(1), epic: k == EntityKindV1::Epic });
                }
            }
            _ if u.is_champion() && u.team() == team => allies.push(at),
            _ if u.is_champion() && sim.is_visible(team, u.id()) => foes.push(at),
            _ => {}
        }
    }
    pick_objective(p, here, &objs, &foes, &allies)
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

/// Crowd control that holds a unit in place - from game 0.7.0 also when laid by native code ("movement continuing while
/// rooted" fixed): root, stun (a Sleep reaches add-ons as a Stun), knock-up, taunt, fear, charm; not a dash's own
/// ForceMove nor a cast's Animation. A step of our own while one of these is on would move him through it.
const HELD: [CcKindV1; 6] =
    [CcKindV1::Bind, CcKindV1::Stun, CcKindV1::Airborne, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];

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

/// 定下的一趟：第几 tick 到墙前开门（走去墙前的路上）、第几 tick 穿过去（开了门以后）、入口、出口、是撤、追还是支援。
#[derive(Clone, Debug)]
struct Pending {
    open_at: usize,
    go_at: Option<usize>,
    entry: (f64, f64),
    to: (f64, f64),
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
    /// 对龙放的大招：落地的 tick、龙、落点。
    drake_at: Option<(usize, usize, (f64, f64))>,
    stalls: usize,
}

impl Door {
    /// 强制位移过去，`e_fly` 一 tick（至少 `e_tick` tick）；返回要走几 tick。
    fn send(&mut self, sim: &mut StableSim<'_>, id: usize, to: (f64, f64)) -> usize {
        let Some(from) = pos(sim, id) else { return 0 };
        let d = dist(from, to);
        let ticks = ((d / self.p.e_fly.max(500) as f64).ceil() as usize).max(self.p.e_tick.max(1));
        let mut ghost = BuffV1::timed(&bd("e_ghost"), ticks + 3);
        ghost.ignore_wall = true;
        sim.add_buff(id, &ghost);
        let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
        mv.dx = (to.0 - from.0).round() as i64;
        mv.dy = (to.1 - from.1).round() as i64;
        mv.speed = (d / ticks as f64).ceil() as u64;
        sim.apply_cc(id, &mv);
        self.trips.push(Trip { id, goal: to, last: from, until: sim.tick() + ticks + 2, step: d / ticks as f64 });
        ticks
    }

    fn haste(&self, sim: &mut StableSim<'_>, id: usize) {
        let name = bd("e_haste");
        sim.entity_remove_buff(id, &name);
        let mut b = BuffV1::timed(&name, self.p.e_ms_t);
        b.move_speed_mult = self.p.e_ms as i32;
        sim.add_buff(id, &b);
    }

    /// 副本的大招读到 `league_bard_r_drk` 放了出来（`league_bard_r_drkgo`）：金球飞向龙（龙身上 `league_bard_r_markb` 的圈），
    /// `r_lag + r_travel` tick 后落地。
    fn stall(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        sim.entity_remove_buff(me, &bd("r_drkgo"));
        let Some(o) = objective_now(sim, &self.p, me) else {
            wlog(format!("{} STALL: cast, but no contested drake any more", head(sim, me)));
            return;
        };
        let fly = self.p.r_lag + self.p.r_travel;
        self.drake_at = Some((tick + fly, o.id, o.at));
        sim.entity_remove_buff(o.id, &bd("r_markb"));
        sim.add_buff(o.id, &BuffV1::timed(&bd("r_markb"), fly));
        self.stalls += 1;
        wlog(format!("{} STALL #{}: {} #{} at {} ({}% hp), lands in {fly} ticks", head(sim, me), self.stalls,
                     if o.epic { "baron" } else { "drake" }, o.id, pt(o.at), o.hp_pct));
    }

    /// 金球落地：龙身上 `league_bard_r_domeb`、落地声，圈 `r_r` 里所有单位（塔除外）定住 `r_t` tick（主包命运之轮的放逐）。
    fn land(&mut self, sim: &mut StableSim<'_>, me: usize, oid: usize, spot: (f64, f64)) {
        let alive = sim.get_entity(oid).is_some_and(|e| e.is_alive());
        let spot = if alive { pos(sim, oid).unwrap_or(spot) } else { spot };
        sim.play_sfx(&bd("r_land"), me, &InputTargetV1::pos(spot.0 as u64, spot.1 as u64));
        if alive {
            sim.entity_remove_buff(oid, &bd("r_domeb"));
            sim.add_buff(oid, &BuffV1::timed(&bd("r_domeb"), 30));
        }
        let mut held = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_alive() || u.is_tower() || matches!(u.kind(), Some(EntityKindV1::Nexus | EntityKindV1::Tower)) {
                continue;
            }
            if dist((u.pos().0 as f64, u.pos().1 as f64), spot) <= self.p.r_r as f64 {
                held.push(u.id());
            }
        }
        let n = held.iter().filter(|&&id| sim.entity_banish(me, id, self.p.r_t, &bd("r_lock"), &bd("r_free"))).count();
        wlog(format!("{} STALL lands at {}: {n} of {} units held {} ticks {:?}", head(sim, me), pt(spot), held.len(),
                     self.p.r_t, held));
    }

    /// 看局面：撤或追，挑好出口就开门（动作、门、音效、冷却），`e_wind` tick 后出发。
    fn decide(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64)) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let mut foes = Vec::new();
        let mut friends = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_champion() || !u.is_alive() {
                continue;
            }
            let (x, y) = u.pos();
            let at = (x as f64, y as f64);
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
        let Some(gi) = current(&grids, &unit_points(sim)) else { return };
        let g = &grids[gi];
        let plan = if wants_out(&self.p, here, mine, &foes, allies) {
            plan_exit(&self.p, g, here, &foes.iter().map(|f| f.at).collect::<Vec<_>>(), home).map(|way| (way, "out".to_string()))
        } else {
            plan_chase(&self.p, g, here, mine, &foes)
                .map(|(way, id)| (way, format!("after #{id}")))
                .or_else(|| plan_help(&self.p, g, here, mine, &foes, &friends).map(|(way, id)| (way, format!("help #{id}"))))
        };
        let Some(((entry, to), why)) = plan else { return };
        let tick = sim.tick();
        sim.entity_remove_buff(me, &bd("e_cd"));
        sim.add_buff(me, &BuffV1::timed(&bd("e_cd"), self.p.e_cd_t));
        self.doors += 1;
        // to the wall's face first (the door stands there, as in League), then it opens
        let walk = if dist(here, entry) > 3_000.0 { self.send(sim, me, entry) } else { 0 };
        self.pending = Some(Pending { open_at: tick + walk, go_at: None, entry, to, why });
    }

    /// 到了墙前：门在他身后贴着墙打开（buff 画面 `league_bard_e_doorb`，主包特效表的 `e_portal`：门的 2.5 倍，比他高出一大截），
    /// `skill2_e` 动作、音效；他站 `STAND` tick 后穿过去。原生代码播的画面游戏里看不到（日志说播了，用户说看不出，剑魔锁链的教训），
    /// buff 画面是泰隆翻墙验证过的。
    fn open(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        sim.entity_remove_buff(me, &bd("e_doorb"));
        sim.add_buff(me, &BuffV1::timed(&bd("e_doorb"), STAND + 2));
        let mut cc = CcV1::of_kind(CcKindV1::Animation, self.p.e_anim.max(STAND) as u64);
        cc.set_name("skill2_e");
        sim.apply_cc(me, &cc);
        let on_me = InputTargetV1::target(me);
        sim.play_sfx(&bd("e_cast"), me, &on_me);
        sim.play_sfx(&bd("vo_e"), me, &on_me);
        if let Some(p) = self.pending.as_mut() {
            p.go_at = Some(tick + STAND);
        }
    }

    /// 出发：门边 `e_ride` 内的友方英雄和他一起穿过去；门的画面收起；记下到达的时刻。
    fn go(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64), plan: Pending) {
        sim.entity_remove_buff(me, &bd("e_doorb"));
        if !landing_ok(sim, plan.to) {
            wlog(format!("{} DOOR #{}: the landing {} is no longer clear, he stays", head(sim, me), self.doors, pt(plan.to)));
            return;
        }
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let mut friends = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.is_champion() && u.is_alive() {
                let (x, y) = u.pos();
                let at = (x as f64, y as f64);
                if u.team() == team && u.id() != me && u.is_targetable() && dist(here, at) <= self.p.e_ride as f64 {
                    friends.push((u.id(), at));
                }
            }
        }
        let grids = Grid::builtin();
        let riders: Vec<(usize, (f64, f64))> = match current(&grids, &unit_points(sim)) {
            Some(gi) => friends.iter().filter_map(|&(id, a)| ride_exit(&grids[gi], here, plan.to, a).map(|q| (id, q))).collect(),
            None => Vec::new(),
        };
        let mut longest = self.send(sim, me, plan.to);
        let mut taken = Vec::new();
        let mut ids = Vec::new();
        for (id, q) in riders {
            longest = longest.max(self.send(sim, id, q));
            taken.push(format!("#{id}->{}", pt(q)));
            ids.push(id);
        }
        self.arrive = Some((sim.tick() + longest, ids));
        if self.doors <= 80 || self.doors % 25 == 0 {
            wlog(format!(
                "{} DOOR #{} {}: at the wall {} -> {} ({:.0}), hp {}%, allies [{}]",
                head(sim, me),
                self.doors,
                plan.why,
                pt(plan.entry),
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
            if d < t.step.max(500.0) {
                continue;
            }
            // 被放逐（巴德自己的 R 之类，不可选中）：游戏 0.6.4 起放逐中的单位不移动，宿主的强制位移也停下；被禁锢、眩晕
            // （含睡眠）、击飞、嘲讽、恐惧、魅惑：游戏 0.7.0 起原生施加的控制也真的让人停下（[`HELD`]）——这里也不挪他，
            // 行程等着（截止时间顺延），结束再走完，不会把人留在墙里。
            if sim.get_entity(t.id).is_some_and(|e| !e.is_targetable()) || has_cc(sim, t.id, &HELD) {
                t.until += 1;
                t.last = here;
                keep.push(t);
                continue;
            }
            if tick > t.until {
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

/// 出发那一刻再看一次落点（门开着的几 tick 里地图判断可能变了）。
fn landing_ok(sim: &StableSim<'_>, to: (f64, f64)) -> bool {
    let grids = Grid::builtin();
    current(&grids, &unit_points(sim)).is_some_and(|gi| grids[gi].roomy(to) && !grids[gi].is_wall(to.0, to.1))
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
        self.drake_at = None;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Bard (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if !self.trips.is_empty() {
            self.follow(sim);
        }
        let tick = sim.tick();
        if let Some((at, oid, spot)) = self.drake_at {
            if tick >= at {
                self.drake_at = None;
                self.land(sim, me, oid, spot);
            }
        }
        if let Some((at, ids)) = self.arrive.clone() {
            if tick >= at {
                self.arrive = None;
                if sim.get_entity(me).is_some_and(|e| e.is_alive()) {
                    let on_me = InputTargetV1::target(me);
                    sim.entity_remove_buff(me, &bd("e_outb"));
                    sim.add_buff(me, &BuffV1::timed(&bd("e_outb"), OUT_STAND + 2));
                    let mut cc = CcV1::of_kind(CcKindV1::Animation, OUT_STAND as u64);
                    cc.set_name("skill2_e");
                    sim.apply_cc(me, &cc);
                    sim.play_sfx(&bd("e_out"), me, &on_me);
                    self.haste(sim, me);
                }
                for id in ids {
                    if sim.get_entity(id).is_some_and(|e| e.is_alive()) {
                        sim.entity_remove_buff(id, &bd("e_rideb"));
                        sim.add_buff(id, &BuffV1::timed(&bd("e_rideb"), 18));
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
        if has_buff(sim, me, &bd("r_drkgo")) && self.drake_at.is_none() {
            self.stall(sim, me);
        }
        if tick % EVERY == 0 {
            // the flag the copy's ult reads: on while a drake is contested and his ult could stall it
            let want = self.drake_at.is_none() && objective_now(sim, &self.p, me).is_some();
            sim.entity_remove_buff(me, &bd("r_drk"));
            if want {
                sim.add_buff(me, &BuffV1::timed(&bd("r_drk"), DRK_T));
            }
        }
        let Some(here) = pos(sim, me) else { return };
        if let Some(plan) = self.pending.clone() {
            match plan.go_at {
                None if tick >= plan.open_at => self.open(sim, me),
                Some(at) if tick >= at => {
                    self.pending = None;
                    self.go(sim, me, here, plan);
                }
                _ => {}
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

// ===================== AI 钩子：争龙时放大招 =====================

/// 他身上有 `league_bard_r_drk`（被动看到有人在打龙）时，把这一刻的操作换成放大招（副本的大招是 `None` 施放，读到标记就对龙放）。
#[derive(Clone, Default)]
struct DrakeAi;

impl StablePlayerAi for DrakeAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:drake")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        if base.is_some_and(|b| InputKindV1::from_code(b.kind) == Some(InputKindV1::Ult)) {
            return None;
        }
        let player = ctx.player_id();
        {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            // only a ready ult (unlocked and cooled down): `is_valid_input` checks neither, and the engine takes an R
            // pressed before level 5 - the game's own AI then reads a None for his ult and panics (game-ai
            // battle.rs:447 / act_gates.rs:111), the match never ends and the day stops (2026-10-18: R at level 3 and 4)
            let ready = me.cooldown(SkillSlotV1::Ult).is_some_and(|c| c.unlocked && c.remaining == 0);
            if !me.is_alive() || !ready || !has_buff(&sim, me.id(), &bd("r_drk")) {
                return None;
            }
        }
        let input = InputV1::action(InputKindV1::Ult, InputTargetV1::NONE);
        ctx.is_valid_input(&input).then_some(input)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Bard's Magical Journey: the door's exit back toward his side, clear of the map's rocks) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:door"), Door::default());
    module.add_player_input_ai(DrakeAi);
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

    fn foe(p: (f64, f64), hp_pct: usize, id: usize) -> Foe {
        Foe { at: p, hp_pct, id }
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
    fn when_he_leaves() {
        let p = Params::default();
        let me = at(5.0, 5.0);
        assert!(wants_out(&p, me, 30, &[foe(at(5.8, 5.0), 100, 1)], 0));
        assert!(wants_out(&p, me, 100, &[foe(at(5.3, 5.0), 100, 1)], 3));
        assert!(wants_out(&p, me, 100, &[foe(at(5.8, 5.0), 100, 1), foe(at(5.0, 5.8), 100, 2)], 0));
        assert!(!wants_out(&p, me, 100, &[foe(at(5.8, 5.0), 100, 1)], 0));
        assert!(!wants_out(&p, me, 100, &[foe(at(5.8, 5.0), 100, 1), foe(at(5.0, 5.8), 100, 2)], 2));
    }

    #[test]
    fn the_door_goes_through_the_wall_behind_him() {
        let p = Params::default();
        let g = wall();
        // the wall right behind him, the enemy in front: through the wall, out on its far side
        let me = at(4.6, 4.5);
        let foes = [at(3.8, 4.5)];
        let (entry, to) = plan_exit(&p, &g, me, &foes, None).unwrap();
        assert!(entry.0 < 5.0 * CELL && !g.is_wall(entry.0, entry.1), "the door at the wall's face: {entry:?}");
        assert!(to.0 > 6.0 * CELL && !g.is_wall(to.0, to.1), "{to:?}");
        assert!(g.blocked(me, to), "the door crosses the wall");
    }

    #[test]
    fn no_wall_no_door() {
        let p = Params::default();
        let g = Grid::from_rows(&vec![".........."; 10]);
        assert_eq!(plan_exit(&p, &g, at(5.0, 5.0), &[at(5.8, 5.0)], Some(at(1.0, 5.0))), None);
        // the wall is behind the enemies, not behind him
        assert_eq!(plan_exit(&p, &wall(), at(3.0, 4.5), &[at(4.0, 4.5)], None), None);
    }

    #[test]
    fn he_chases_a_hurt_champion_behind_a_wall() {
        let p = Params::default();
        let g = wall();
        let me = at(4.4, 4.5);
        let prey = foe(at(7.0, 4.4), 30, 7);
        let ((_, to), id) = plan_chase(&p, &g, me, 80, &[prey]).unwrap();
        assert_eq!(id, 7);
        assert!(dist(to, prey.at) + CLOSER <= dist(me, prey.at) && !g.is_wall(to.0, to.1), "{to:?}");
        // not behind a wall (he walks), a healthy target, or Bard hurt: no door
        let open = Grid::from_rows(&vec![".........."; 10]);
        assert!(plan_chase(&p, &open, me, 80, &[prey]).is_none());
        assert!(plan_chase(&p, &g, me, 80, &[foe(at(7.0, 4.4), 90, 7)]).is_none());
        assert!(plan_chase(&p, &g, me, 20, &[prey]).is_none());
    }

    #[test]
    fn he_doors_over_to_an_ally_in_a_fight() {
        let p = Params::default();
        let g = wall();
        let me = at(4.4, 4.5);
        let ally = (3, at(8.0, 4.5));
        let foes = [foe(at(8.6, 4.5), 100, 9)];
        let ((_, to), id) = plan_help(&p, &g, me, 90, &foes, &[ally]).unwrap();
        assert_eq!(id, 3);
        assert!(dist(to, ally.1) + HELP_GAIN <= dist(me, ally.1) && !g.is_wall(to.0, to.1), "{to:?}");
        assert!(g.blocked(me, to), "through the wall");
        // the ally not fighting, Bard hurt, or an enemy on Bard: no door
        assert!(plan_help(&p, &g, me, 90, &[foe(at(1.0, 9.0), 100, 9)], &[ally]).is_none());
        assert!(plan_help(&p, &g, me, 30, &foes, &[ally]).is_none());
        assert!(plan_help(&p, &g, me, 90, &[foes[0], foe(at(4.0, 4.5), 100, 8)], &[ally]).is_none());
    }

    #[test]
    fn allies_land_clear_of_rock() {
        let g = wall();
        let me = at(4.6, 4.5);
        let to = at(6.4, 4.5);
        // the ally's own shifted exit falls in the wall's column: he lands beside Bard's exit
        let ally = at(3.9, 4.5);
        let q = ride_exit(&g, me, to, ally).unwrap();
        assert!(!g.is_wall(q.0, q.1) && g.roomy(q), "{q:?}");
    }

    #[test]
    fn on_the_moba_map_every_door_lands_clear_of_rock() {
        let p = Params::default();
        let g = &Grid::builtin()[0];
        let (w, h) = g.size();
        let mut doors = 0;
        let mut y = 20_000.0;
        while y < h {
            let mut x = 20_000.0;
            while x < w {
                if !g.is_wall(x, y) {
                    for (dx, dy) in [(10_000.0, 0.0), (-10_000.0, 0.0), (0.0, 10_000.0), (0.0, -10_000.0)] {
                        if let Some((entry, to)) = plan_exit(&p, g, (x, y), &[(x + dx, y + dy)], None) {
                            assert!(!g.is_wall(entry.0, entry.1), "the door stands outside the wall: {entry:?}");
                            assert!(!g.is_wall(to.0, to.1) && g.roomy(to), "({x},{y}) -> {to:?}");
                            assert!(g.blocked((x, y), to), "a door crosses a wall");
                            doors += 1;
                        }
                    }
                }
                x += 24_000.0;
            }
            y += 24_000.0;
        }
        assert!(doors > 30, "{doors} doors");
    }

    #[test]
    fn the_moba_map_has_its_ninety_wall_cells() {
        assert_eq!(Grid::builtin()[0].walls(), 90);
    }

    #[test]
    fn he_stalls_a_drake_the_enemies_are_taking() {
        let p = Params::default();
        let drake = Obj { id: 9, at: (500_000.0, 500_000.0), hp_pct: 70, epic: false };
        let me = (440_000.0, 500_000.0);
        let foe_on_it = [(520_000.0, 510_000.0)];
        // enemies on a hurt drake, no ally in the circle: stall it
        assert_eq!(pick_objective(&p, me, &[drake], &foe_on_it, &[me]), Some(drake));
        // his own jungler on it: no (the stasis would hold him too)
        assert_eq!(pick_objective(&p, me, &[drake], &foe_on_it, &[me, (495_000.0, 500_000.0)]), None);
        // nobody hitting it yet (full health) or no enemy beside it: no
        assert_eq!(pick_objective(&p, me, &[Obj { hp_pct: 100, ..drake }], &foe_on_it, &[me]), None);
        assert_eq!(pick_objective(&p, me, &[drake], &[(560_000.0, 560_000.0)], &[me]), None);
        // out of the ult's reach: no
        assert_eq!(pick_objective(&p, (380_000.0, 500_000.0), &[drake], &foe_on_it, &[]), None);
        // Baron before the drake
        let baron = Obj { id: 10, at: (470_000.0, 450_000.0), hp_pct: 80, epic: true };
        let foes = [(520_000.0, 510_000.0), (480_000.0, 440_000.0)];
        assert_eq!(pick_objective(&p, me, &[drake, baron], &foes, &[me]).map(|o| o.id), Some(10));
    }

    #[test]
    fn the_ult_numbers_come_from_the_champion_data() {
        let p = parse_params(r#"{"r_range":81000,"r_r":35000,"r_t":140,"r_lag":14,"r_travel":20,"r_arm_range":91000}"#);
        assert_eq!((p.r_range, p.r_r, p.r_t, p.r_lag, p.r_travel, p.r_arm_range), (81_000, 35_000, 140, 14, 20, 91_000));
    }

    #[test]
    fn the_names_fit() {
        for x in ["e_cd", "e_haste", "e_ghost", "e_doorb", "e_outb", "e_rideb"] {
            assert!(bd(x).len() <= BUFF_NAME_CAP);
        }
    }
}
