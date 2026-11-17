//! 泰隆附加包：「刺客之道」翻墙（用户：「有墙啊 青钢影不是勾墙了？」）。
//!
//! 主包是纯数据，读不到地图的墙，所以主包里的刺客之道是空地上的撤离：收刀或 Q 击杀时被包围就背向敌人翻身跃开。
//! 5v5 地图的野区里有 90 格引擎的碰撞墙（30 × 30 格、每格 32000，卡蜜尔钩墙附加包的 `maps.rs`），英雄联盟的 E 就是翻过这种墙。
//! `mod.override_info` 把主包的泰隆换成 `override/` 里的副本（tools/kit/build_talon.py 的 native=1）：数据和主包一样（空地撤离照旧），
//! 多了本包的被动 `league_talon_vault:path` 和翻墙的地面弧光（buff 画面 `league_talon_e_wall`，用主包刺客之道的帧）。
//!
//! 被动每 `EVERY` tick 看一次，刺客之道好了（他身上没有主包的冷却标记 `league_talon_e_cd`）、没被控时：
//! - **翻墙撤离**：生命低于 `e_low`% 而且身边（`e_safe_r`）有敌方英雄，或者身边有 `e_crowd` 名以上敌方英雄、比身边的友方英雄多、
//!   他的生命又低于 `OUT_HP`%（打得赢的团战不跑）——找一堵背向敌人（离开敌人的方向左右 75° 内）、离他不到 `e_reach` 的墙，
//!   翻到墙的另一边（落点不超过 `e_far`），选落地后离敌人最远的那一处；
//! - **翻墙追击**：`e_chase_r` 内、隔着墙的敌方英雄（不贴身），朝他左右 35° 内找墙翻过去，落点要比现在近 `CLOSER` 以上，
//!   落点旁和他身边（`CROWD_R`）除了他最多一名敌方英雄（不翻进人堆），目标生命不高于 `PREY_HP`%、泰隆生命不低于 `CHASE_HP`%。
//!
//! 翻墙：主包的冷却标记 `e_cd`（空地撤离也就不会紧接着再跳）、`skill_e` 动作、穿墙的强制位移（速度 `e_speed`，期间无视地形）、
//! 地面弧光、刺客之道的音效和台词（台词照主包隔 `vo_gap`），落地后加速 `e_haste`% `e_haste_t` tick（主包的 `e_haste`，画面也是主包的）。
//! 宿主没挪他（撞墙停了）时逐 tick 自己走一步（`entity_set_pos`，凯隐穿墙的做法）。
//!
//! 两张 5v5 地图（2026-11-10，用户：「要同时兼容原版地图和这个地图」）：每次看局面按这局的塔和水晶判断是哪张图
//! （`game_places::terrain::map_of_sim`）。游戏自己的地图照旧（三张内置地图里挑）；Rin 的召唤师峡谷（1614545 见方）用峡谷
//! 作者的墙体文件（`terrain::rift_walls`，295 x 296 格、每格 60000/11），没有文件时峡谷上不知道哪里有墙，就不翻墙（以前
//! 拿内置地图的格子：960000 以外都是格子外，落点「不在地图里」，峡谷的远半边从来翻不了，近半边翻的是内置地图的墙）。
//!
//! 刀锋之末的伤口记在每个英雄身上（0.1.8，用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」）：英雄联盟
//! "Each time Talon's abilities deal physical damage to champions and large monsters, they apply a stack of Wound"，
//! 叠满 3 层后他的下一次普攻让**那个人**流血，流血期间他不再叠层。主包的数据读不到目标身上的层数，伤口记在泰隆自己
//! 身上（劫被动的写法），换目标时会带着层数流血下一个被普攻的人。副本（build_talon.py 的 native=1）里：
//! - 技能打中英雄调用原生效果 `league_talon_vault:wound`（目标 = 被打中的英雄）：在他身上叠 `WOUND` 一层（最多
//!   `WOUND_MAX`，每层 `WOUND_T` tick，每次命中全部刷新），挂主包的伤口画面 `league_talon_p_wound`；他在流血
//!   （`BLEED`）就不叠。
//! - 普攻打中调用 `league_talon_vault:edge`（目标 = 被打中的单位）：他身上有 `WOUND_MAX` 层就清掉、挂 `BLEED`
//!   （`BLEED_T` tick）、给泰隆挂 3 tick 的 `GO`，数据当 tick（读不到就下一 tick）读到它就让这个人流血（主包的流血）；
//!   不满的层数刷新时间（英雄联盟：普攻也刷新）。主包按泰隆身上的层数、10 秒冷却（`p_cd`）；英雄联盟没有冷却，副本也没有。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。不用全局变量（日志的计数除外），服务端预模拟和你看的那场各算各的。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_talon_vault.log`，每次启动游戏重写：你看的那场（观战、回放）
//! 每一行都记；服务端的预模拟（每次启动几百场，每场的被动都是新的）每种先记 `LOG_FIRST` 行、之后每 `LOG_EVERY` 行记一行；
//! 参数（`Params`）每次启动只在第一条 `SPAWN` 里写一次。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{self, Map};
use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_talon_vault";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_talon_vault") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 主包泰隆的名字（buff、画面、音效都以它开头）。
fn tl(x: &str) -> String {
    format!("league_talon_{x}")
}

/// 游戏自己的地图的墙格边长（世界单位）。
pub const CELL: f64 = 32_000.0;
/// 没翻成时日志里找最近的墙找多远：游戏自己的地图的 3 格（两张图上都是这个距离）。
pub const NEAR_WALL: f64 = 3.0 * CELL;
/// 每隔几 tick 看一次。
pub const EVERY: usize = 3;
/// 沿一个方向找墙时的步长。
pub const STEP: f64 = 1_000.0;
/// 落点离墙的另一边再走这么远（别落在墙边上卡住）。
pub const MARGIN: f64 = 4_000.0;
/// 找墙的方向数（一圈）。
pub const RAYS: usize = 48;
/// 撤离：离开敌人的方向左右这么多度内的墙。
pub const ESCAPE_DEG: f64 = 75.0;
/// 撤离：落地后离最近的敌人至少比现在远这么多。
pub const ESCAPE_GAIN: f64 = 10_000.0;
/// 追击：朝目标左右这么多度内的墙。
pub const CHASE_DEG: f64 = 35.0;
/// 追击：离目标不到这么远就不翻（够得着）。
pub const CHASE_NEAR: f64 = 26_000.0;
/// 追击：落点要比现在近这么多。
pub const CLOSER: f64 = 15_000.0;
/// 追击：泰隆生命不低于这个百分比。
pub const CHASE_HP: usize = 40;
/// 追击：只追生命不高于这个百分比的英雄（收割，不是隔墙去开团）。
pub const PREY_HP: usize = 60;
/// 被围撤离：他的生命低于这个百分比才跑（满血打得赢的团战不跑）。
pub const OUT_HP: usize = 70;
/// 追击：落点和目标这么远内（除目标外）最多一名敌方英雄。
pub const CROWD_R: f64 = 35_000.0;

/// 刀锋之末（伤口记在被打中的英雄身上）：副本调用的两个原生效果。
pub const WOUND_FX: &str = "league_talon_vault:wound";
pub const EDGE_FX: &str = "league_talon_vault:edge";
/// 英雄身上的伤口（每层一个 buff 实例）、流血中（不再叠层）、给数据读的流血旗子（泰隆身上）、主包的伤口画面。
pub const WOUND: &str = "league_talon_vault_w";
pub const BLEED: &str = "league_talon_vault_bl";
pub const GO: &str = "league_talon_p_go";
pub const GO_T: usize = 3;
pub const WOUND_PIC: &str = "league_talon_p_wound";
/// 主包参数表 P 的 p_t（伤口留多久）、p_bleed（流血多久）：`make_override.py` 核对；英雄联盟最多 3 层。
pub const WOUND_T: usize = 300;
pub const BLEED_T: usize = 120;
pub const WOUND_MAX: usize = 3;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_TALON_VAULT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_talon_vault.log");
        }
    }
    PathBuf::from("league_talon_vault.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
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

/// Lines of each kind a launch: the server's presims (hundreds a launch, each with new passives - a count in the passive
/// counts one sim) the first `LOG_FIRST`, then every `LOG_EVERY`-th; the match on screen all of them.
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind`: its count this launch when it is to be written (`shown`: the match on screen).
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    noted(kind, on_screen(sim))
}

/// The `Params` the log showed last (they come from the champion data: the same in every sim of a launch).
static PARAMS_SHOWN: Mutex<Option<Params>> = Mutex::new(None);

/// `p` not in the log yet: once a launch, again only if they ever differ. Every Talon of every presim wrote them at
/// every spawn (2026-10-30: 1319 SPAWN lines, 93% of a 361 KB log).
fn params_new(p: &Params) -> bool {
    let mut shown = PARAMS_SHOWN.lock().unwrap_or_else(|e| e.into_inner());
    if shown.as_ref() == Some(p) {
        return false;
    }
    *shown = Some(p.clone());
    true
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
    pub e_cd: usize,
    pub e_safe_r: usize,
    pub e_crowd: usize,
    pub e_speed: usize,
    pub e_anim: usize,
    pub e_haste: usize,
    pub e_haste_t: usize,
    pub e_low: usize,
    pub e_reach: usize,
    pub e_far: usize,
    pub e_chase_r: usize,
    pub vo_gap: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            e_cd: 600,
            e_safe_r: 40_000,
            e_crowd: 2,
            e_speed: 3_000,
            e_anim: 20,
            e_haste: 30,
            e_haste_t: 90,
            e_low: 35,
            e_reach: 42_000,
            e_far: 120_000,
            e_chase_r: 70_000,
            vo_gap: 600,
        }
    }
}

/// `{"e_cd":600,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "e_cd" => &mut p.e_cd,
            "e_safe_r" => &mut p.e_safe_r,
            "e_crowd" => &mut p.e_crowd,
            "e_speed" => &mut p.e_speed,
            "e_anim" => &mut p.e_anim,
            "e_haste" => &mut p.e_haste,
            "e_haste_t" => &mut p.e_haste_t,
            "e_low" => &mut p.e_low,
            "e_reach" => &mut p.e_reach,
            "e_far" => &mut p.e_far,
            "e_chase_r" => &mut p.e_chase_r,
            "vo_gap" => &mut p.vo_gap,
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

/// 一张墙格子：`cells[y][x]`，每格 `cell` 见方，(0, 0) 格的角在 `origin`（游戏自己的地图 32000、(0, 0)；峡谷的墙体文件
/// 60000/11、(30000/11, 0)）。
#[derive(Clone, Debug, PartialEq)]
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
    pub cell: f64,
    pub origin: (f64, f64),
}

impl Grid {
    pub fn from_rows(rows: &[&str]) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(), cell: CELL, origin: (0.0, 0.0) }
    }

    pub fn builtin() -> [Grid; 3] {
        [Grid::from_rows(&maps::MOBA), Grid::from_rows(&maps::SINGLE_LANE), Grid::from_rows(&maps::DEATH_MATCH)]
    }

    /// 峡谷的墙：有墙体文件就是文件的墙格；没有就是一格地图大小的空地（不知道哪里有墙：峡谷上不翻墙）。
    pub fn rift(walls: Option<&terrain::Walls>) -> Grid {
        match walls {
            Some(w) => Grid { cells: w.cells.clone(), cell: w.cell, origin: w.origin },
            None => Grid { cells: vec![vec![false]], cell: terrain::RIFT_EXTENT, origin: (0.0, 0.0) },
        }
    }

    /// 格子的另一角（游戏自己的地图从 (0, 0) 起，就是它的宽、高）。
    pub fn size(&self) -> (f64, f64) {
        (self.origin.0 + self.cells.first().map_or(0, |r| r.len()) as f64 * self.cell,
         self.origin.1 + self.cells.len() as f64 * self.cell)
    }

    /// 在地图里吗。
    pub fn inside(&self, p: (f64, f64)) -> bool {
        let (w, h) = self.size();
        p.0 >= self.origin.0 && p.1 >= self.origin.1 && p.0 < w && p.1 < h
    }

    /// 世界坐标落在墙格里吗（地图外不算）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        let (x, y) = (x - self.origin.0, y - self.origin.1);
        if x < 0.0 || y < 0.0 {
            return false;
        }
        let (cx, cy) = ((x / self.cell) as usize, (y / self.cell) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(false)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }

    /// 两点之间的直线穿过墙格吗（两端不算）。
    pub fn crosses(&self, a: (f64, f64), b: (f64, f64)) -> bool {
        let n = (dist(a, b) / STEP).floor() as usize;
        (1..n).any(|i| {
            let t = i as f64 / n as f64;
            self.is_wall(a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
        })
    }

    /// 朝 `dir`（单位向量）翻墙：`reach` 内碰到墙、一路穿过去，落在墙另一边 `MARGIN` 处；落点不超过 `far`、不在墙里、
    /// 在地图里。返回 (落点, 到墙的距离)。
    pub fn vault(&self, from: (f64, f64), dir: (f64, f64), reach: f64, far: f64) -> Option<((f64, f64), f64)> {
        let at = |t: f64| (from.0 + dir.0 * t, from.1 + dir.1 * t);
        let mut t = STEP;
        while t <= reach && !self.is_wall(at(t).0, at(t).1) {
            t += STEP;
        }
        if t > reach {
            return None;
        }
        let start = t;
        while t <= far && self.is_wall(at(t).0, at(t).1) {
            t += STEP;
        }
        let land = t + MARGIN;
        let to = at(land);
        (land <= far && !self.is_wall(to.0, to.1) && self.inside(to)).then_some((to, start))
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

/// 这局是哪张图：站在墙里的英雄最少（翻墙、穿墙途中的英雄会站在墙格上）、墙又最多的那张（卡蜜尔、凯隐附加包的判断，
/// 但不因为一个正在穿墙的凯隐就换图）。
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

/// 游戏的三张内置地图，和峡谷的墙（墙体文件每次启动只读、只换一次，第一次到峡谷上才读）。
static GRIDS: LazyLock<[Grid; 3]> = LazyLock::new(Grid::builtin);
static RIFT_GRID: LazyLock<Grid> = LazyLock::new(|| Grid::rift(terrain::rift_ground()));

/// 这局的墙：峡谷上是峡谷的（第一次遇到时日志里记一行），游戏自己的地图照旧从三张内置地图里挑（[`current`]）。
fn grid_now(sim: &StableSim<'_>) -> Option<&'static Grid> {
    match terrain::map_of_sim(sim) {
        Map::Rift => {
            static MET: AtomicBool = AtomicBool::new(false);
            if !MET.swap(true, Ordering::Relaxed) {
                wlog(format!("== Rift: Assassin's Path vaults the Rift's walls (from its walls file; with no file no wall \
                              is known there and he never vaults); {} ==", terrain::rift_status()));
            }
            Some(&*RIFT_GRID)
        }
        Map::Native => current(&*GRIDS, &unit_points(sim)).map(|i| &GRIDS[i]),
    }
}

fn rays() -> impl Iterator<Item = (f64, f64)> {
    (0..RAYS).map(|i| {
        let a = i as f64 * std::f64::consts::TAU / RAYS as f64;
        (a.cos(), a.sin())
    })
}

fn unit(v: (f64, f64)) -> Option<(f64, f64)> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

// ===================== 决定 =====================

/// 一个敌方英雄：位置、生命百分比、id。
#[derive(Clone, Copy, Debug)]
pub struct Foe {
    pub at: (f64, f64),
    pub hp_pct: usize,
    pub id: usize,
}

/// 要翻的墙。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Plan {
    pub to: (f64, f64),
    pub chase: Option<usize>,
}

/// 该撤离吗：残血而身边有敌方英雄；或者身边够 `e_crowd` 名敌方英雄、比身边的友方英雄（`allies` 个，不算他）多，他的生命又低于
/// `OUT_HP`%。
pub fn wants_out(p: &Params, me: (f64, f64), hp_pct: usize, foes: &[Foe], allies: usize) -> bool {
    let near = foes.iter().filter(|f| dist(me, f.at) <= p.e_safe_r as f64).count();
    (hp_pct < p.e_low && near >= 1) || (near >= p.e_crowd.max(1) && near > allies + 1 && hp_pct < OUT_HP)
}

/// 翻墙撤离：背向身边敌人的墙，落地后离最近的敌人最远（至少比现在远 `ESCAPE_GAIN`）。
pub fn plan_escape(p: &Params, g: &Grid, me: (f64, f64), foes: &[Foe]) -> Option<Plan> {
    let near: Vec<&Foe> = foes.iter().filter(|f| dist(me, f.at) <= p.e_safe_r as f64 * 1.25).collect();
    if near.is_empty() {
        return None;
    }
    let c = near.iter().fold((0.0, 0.0), |s, f| (s.0 + f.at.0, s.1 + f.at.1));
    let c = (c.0 / near.len() as f64, c.1 / near.len() as f64);
    let away = unit((me.0 - c.0, me.1 - c.1)).unwrap_or((1.0, 0.0));
    let gap = |q: (f64, f64)| foes.iter().map(|f| dist(q, f.at)).fold(f64::MAX, f64::min);
    let now = gap(me);
    let cos = ESCAPE_DEG.to_radians().cos();
    rays()
        .filter(|d| d.0 * away.0 + d.1 * away.1 >= cos)
        .filter_map(|d| g.vault(me, d, p.e_reach as f64, p.e_far as f64))
        .map(|(to, _)| (to, gap(to)))
        .filter(|&(_, gp)| gp >= now + ESCAPE_GAIN)
        .max_by(|a, b| a.1.total_cmp(&b.1))
        .map(|(to, _)| Plan { to, chase: None })
}

/// 翻墙追击想追的人：`e_chase_r` 内、隔着墙（不贴身）、生命不高于 `PREY_HP`% 的敌方英雄，他自己生命不低于 `CHASE_HP`%；
/// 生命最低的在前。
pub fn chase_targets<'a>(p: &Params, g: &Grid, me: (f64, f64), hp_pct: usize, foes: &'a [Foe]) -> Vec<&'a Foe> {
    let mut targets: Vec<&Foe> = foes
        .iter()
        .filter(|f| {
            let d = dist(me, f.at);
            d > CHASE_NEAR && d <= p.e_chase_r as f64 && g.crosses(me, f.at)
        })
        .filter(|f| hp_pct >= CHASE_HP && f.hp_pct <= PREY_HP)
        .collect();
    targets.sort_by_key(|f| f.hp_pct);
    targets
}

/// 离他最近的墙（任何方向、`limit` 内）多远：没翻成时记进日志（0.1.6：5 局 0 次 VAULT，16000 的 `e_reach` 只有半格）。
pub fn nearest_wall(g: &Grid, me: (f64, f64), limit: f64) -> Option<f64> {
    rays()
        .filter_map(|d| {
            let mut t = STEP;
            while t <= limit && !g.is_wall(me.0 + d.0 * t, me.1 + d.1 * t) {
                t += STEP;
            }
            (t <= limit).then_some(t)
        })
        .min_by(|a, b| a.total_cmp(b))
}

/// `NO VAULT` 一条命里隔这么多 tick 才再记一行（想翻的那几秒每 3 tick 想一次）。
pub const TALLY_GAP: usize = 300;

/// 翻墙追击：隔着墙的敌方英雄（生命最低的先），翻过去离他更近，落点不在人堆里。
pub fn plan_chase(p: &Params, g: &Grid, me: (f64, f64), hp_pct: usize, foes: &[Foe]) -> Option<Plan> {
    let cos = CHASE_DEG.to_radians().cos();
    for t in chase_targets(p, g, me, hp_pct, foes) {
        let Some(toward) = unit((t.at.0 - me.0, t.at.1 - me.1)) else { continue };
        let now = dist(me, t.at);
        let best = rays()
            .filter(|d| d.0 * toward.0 + d.1 * toward.1 >= cos)
            .filter_map(|d| g.vault(me, d, p.e_reach as f64, p.e_far as f64))
            .map(|(to, _)| to)
            .filter(|&to| dist(to, t.at) + CLOSER <= now)
            .filter(|&to| {
                foes.iter().filter(|f| f.id != t.id && (dist(to, f.at) <= CROWD_R || dist(t.at, f.at) <= CROWD_R)).count()
                    <= 1
            })
            .min_by(|a, b| dist(*a, t.at).total_cmp(&dist(*b, t.at)));
        if let Some(to) = best {
            return Some(Plan { to, chase: Some(t.id) });
        }
    }
    None
}

// ===================== 刀锋之末 =====================

/// 一次技能命中：原来 `had` 层、正在流血（`bleeding`）时叠完是几层（`None`：不叠）。
pub fn wound_after(had: usize, bleeding: bool) -> Option<usize> {
    (!bleeding).then(|| (had + 1).min(WOUND_MAX))
}

/// 一次普攻命中：原来 `had` 层时流不流血（满层就流，层清掉）。
pub fn edge_bleeds(had: usize) -> bool {
    had >= WOUND_MAX
}

fn wounds_on(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == WOUND).count())
}

/// 把 `id` 身上的伤口换成 `n` 层（时间重新算），画面跟着。
fn set_wounds(sim: &mut StableSim<'_>, id: usize, n: usize) {
    sim.entity_remove_buff(id, WOUND);
    sim.entity_remove_buff(id, WOUND_PIC);
    for _ in 0..n {
        sim.add_buff(id, &BuffV1::timed(WOUND, WOUND_T));
    }
    if n > 0 {
        sim.add_buff(id, &BuffV1::timed(WOUND_PIC, WOUND_T));
    }
}

fn unit_input(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

/// 技能打中一个英雄：在他身上叠一层伤口（流血中不叠）。
fn wound(sim: &mut StableSim<'_>, talon: usize, input: InputTargetV1) {
    let Some(t) = unit_input(&input) else { return };
    if !sim.get_entity(t).is_some_and(|e| e.is_alive()) {
        return;
    }
    let had = wounds_on(sim, t);
    let bleeding = has_buff(sim, t, BLEED);
    let Some(now) = wound_after(had, bleeding) else {
        if let Some(k) = tally(sim, "wound bleeding") {
            wlog(format!("{} WOUND #{t}: bleeding, no wound #{k}", head(sim, talon)));
        }
        return;
    };
    set_wounds(sim, t, now);
    if let Some(k) = tally(sim, "wound") {
        wlog(format!("{} WOUND #{t}: {had} -> {now} #{k}", head(sim, talon)));
    }
}

/// 普攻打中一个单位：他有满层伤口就流血（数据读 `GO`），不满的刷新时间。
fn edge(sim: &mut StableSim<'_>, talon: usize, input: InputTargetV1) {
    let Some(t) = unit_input(&input) else { return };
    if !sim.get_entity(t).is_some_and(|e| e.is_alive()) {
        return;
    }
    let had = wounds_on(sim, t);
    if had == 0 {
        return;
    }
    if !edge_bleeds(had) {
        set_wounds(sim, t, had);
        return;
    }
    set_wounds(sim, t, 0);
    sim.entity_remove_buff(t, BLEED);
    sim.add_buff(t, &BuffV1::timed(BLEED, BLEED_T));
    sim.entity_remove_buff(talon, GO);
    sim.add_buff(talon, &BuffV1::timed(GO, GO_T));
    if let Some(k) = tally(sim, "bleed") {
        wlog(format!("{} BLEED #{t}: {had} wounds -> bleeding {BLEED_T} ticks #{k}", head(sim, talon)));
    }
}

struct Fx(fn(&mut StableSim<'_>, usize, InputTargetV1));

impl StableEffectType for Fx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

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

/// 不能翻墙的状态：硬控、沉默、禁位移技能、正被强制位移（包括 Q 的跃击）。
const NO_VAULT: [CcKindV1; 9] = [
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

fn pos(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    sim.get_entity(id).map(|e| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

fn hp_pct(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(100, |e| {
        let (hp, max) = e.hp();
        hp * 100 / max.max(1)
    })
}

fn timed(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

// ===================== 被动 =====================

/// 每个泰隆一份：参数、正在翻往哪里、上一 tick 的位置（看宿主有没有挪他）、落地加速的时刻。
#[derive(Clone, Default)]
struct Path {
    p: Params,
    goal: Option<(f64, f64)>,
    last: Option<(f64, f64)>,
    until: usize,
    haste_at: Option<usize>,
    vaults: usize,
    /// 这条命里想翻墙撤离 / 追击而没翻成的次数，和上一行 `NO VAULT` 的 tick（0.1.6 的记账）。
    wanted: (usize, usize),
    tally_at: Option<usize>,
}

impl Path {
    fn go(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64), plan: Plan) {
        let d = dist(here, plan.to);
        let speed = self.p.e_speed.max(500) as f64;
        let ticks = (d / speed).ceil().max(1.0);
        let tick = sim.tick();
        timed(sim, me, &tl("e_cd"), self.p.e_cd);
        let mut ghost = BuffV1::timed(&tl("e_ghost"), ticks as usize + 3);
        ghost.ignore_wall = true;
        sim.add_buff(me, &ghost);
        timed(sim, me, &tl("e_wall"), self.p.e_anim);
        let mut cc = CcV1::of_kind(CcKindV1::Animation, self.p.e_anim as u64);
        cc.set_name("skill_e");
        sim.apply_cc(me, &cc);
        let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
        mv.dx = (plan.to.0 - here.0).round() as i64;
        mv.dy = (plan.to.1 - here.1).round() as i64;
        mv.speed = (d / ticks).ceil() as u64;
        sim.apply_cc(me, &mv);
        sim.play_sfx(&tl("e"), me, &InputTargetV1::target(me));
        if !has_buff(sim, me, &tl("vo_cd")) {
            timed(sim, me, &tl("vo_cd"), self.p.vo_gap);
            sim.play_sfx(&tl("vo_e"), me, &InputTargetV1::target(me));
        }
        self.goal = Some(plan.to);
        self.last = Some(here);
        self.until = tick + ticks as usize + 2;
        self.haste_at = Some(tick + ticks as usize);
        self.vaults += 1;
        if tally(sim, "vault").is_some() {
            wlog(format!(
                "{} VAULT #{} {}: {} -> {} ({:.0}, {} ticks), hp {}%",
                head(sim, me),
                self.vaults,
                plan.chase.map_or("out".to_string(), |t| format!("after #{t}")),
                pt(here),
                pt(plan.to),
                d,
                ticks,
                hp_pct(sim, me)
            ));
        }
    }

    /// 翻墙途中：宿主没挪他就自己走一步；到了、或时间到了就停。落地时加速。
    fn follow(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64)) {
        let tick = sim.tick();
        if self.haste_at.is_some_and(|t| tick >= t) {
            self.haste_at = None;
            let name = tl("e_haste");
            sim.entity_remove_buff(me, &name);
            let mut haste = BuffV1::timed(&name, self.p.e_haste_t);
            haste.move_speed_mult = self.p.e_haste as i32;
            sim.add_buff(me, &haste);
        }
        let Some(to) = self.goal else { return };
        let speed = self.p.e_speed.max(500) as f64;
        let d = dist(here, to);
        if d >= speed && (sim.get_entity(me).is_some_and(|e| !e.is_targetable()) || has_cc(sim, me, &HELD)) {
            // 被放逐（巴德的 R 之类）：游戏 0.6.4 起放逐中的单位不动、宿主的强制位移也停下；被禁锢、眩晕（含睡眠）、击飞、
            // 嘲讽、恐惧、魅惑：游戏 0.7.0 起原生施加的控制也真的让人停下（[`HELD`]）——这里也不挪他，行程等着
            // （截止时间顺延），结束再走完，不会把他留在墙里
            self.until += 1;
            self.last = Some(here);
            return;
        }
        if d < speed || tick > self.until {
            self.goal = None;
            self.last = None;
            return;
        }
        if self.last.is_some_and(|l| dist(l, here) < 1.0) {
            let s = speed.min(d);
            let next = (here.0 + (to.0 - here.0) / d * s, here.1 + (to.1 - here.1) / d * s);
            sim.entity_set_pos(me, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64);
        }
        self.last = Some(here);
    }
}

impl StablePassive for Path {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.goal = None;
        self.last = None;
        self.haste_at = None;
        // the Params in the first SPAWN line of a launch only; the line itself capped in the presims (every respawn writes one)
        let params = params_new(&self.p).then(|| format!(", {:?}", self.p));
        if tally(sim, "spawn").is_some() || params.is_some() {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN: the add-on's Talon (player {player}, team {team}){}", head(sim, me),
                         params.unwrap_or_default()));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.goal = None;
            return;
        }
        let team = e.team();
        let targetable = e.is_targetable();
        let Some(here) = pos(sim, me) else { return };
        if self.goal.is_some() || self.haste_at.is_some() {
            self.follow(sim, me, here);
            if self.goal.is_some() {
                return;
            }
        }
        // 被放逐时不出 E（游戏 0.6.4 起放逐中不能出招；本包自己出手，不经宿主的判断）
        if sim.tick() % EVERY != 0 || has_buff(sim, me, &tl("e_cd")) || has_cc(sim, me, &NO_VAULT) || !targetable {
            return;
        }
        let mut foes = Vec::new();
        let mut allies = 0;
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_champion() || !u.is_alive() {
                continue;
            }
            let (x, y) = u.pos();
            let at = (x as f64, y as f64);
            if u.team() != team && u.is_targetable() {
                let (hp, max) = u.hp();
                foes.push(Foe { at, hp_pct: hp * 100 / max.max(1), id: u.id() });
            } else if u.team() == team && u.id() != me && dist(here, at) <= self.p.e_safe_r as f64 {
                allies += 1;
            }
        }
        let Some(g) = grid_now(sim) else { return };
        let mine = hp_pct(sim, me);
        let out = wants_out(&self.p, here, mine, &foes, allies);
        let plan = if out {
            plan_escape(&self.p, g, here, &foes)
        } else {
            plan_chase(&self.p, g, here, mine, &foes)
        };
        match plan {
            Some(plan) => self.go(sim, me, here, plan),
            None => {
                // wanted and not vaulted (0.1.6: 0 VAULT in 5 games): a tally line now and then with the nearest wall
                let prey = (!out).then(|| chase_targets(&self.p, g, here, mine, &foes).first().map(|f| (f.id, dist(here, f.at)))).flatten();
                if out || prey.is_some() {
                    if out { self.wanted.0 += 1 } else { self.wanted.1 += 1 }
                    let tick = sim.tick();
                    if self.tally_at.is_none_or(|t| tick < t || tick >= t + TALLY_GAP) {
                        self.tally_at = Some(tick);
                        if tally(sim, "no_vault").is_some() {
                            let wall = nearest_wall(g, here, NEAR_WALL);
                            wlog(format!(
                                "{} NO VAULT: {} - nearest wall {} (reach {}), wanted {} escapes / {} chases this life",
                                head(sim, me),
                                match prey {
                                    Some((t, d)) => format!("a chase of #{t} behind a wall {d:.0} away found no wall to vault"),
                                    None => format!("an escape (hp {mine}%, {} enemy champions within {}) found no wall to vault",
                                                    foes.iter().filter(|f| dist(here, f.at) <= self.p.e_safe_r as f64).count(),
                                                    self.p.e_safe_r),
                                },
                                wall.map_or_else(|| format!("none within {NEAR_WALL:.0}"), |w| format!("{w:.0} away")),
                                self.p.e_reach,
                                self.wanted.0,
                                self.wanted.1
                            ));
                        }
                    }
                }
            }
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.goal = None;
        self.last = None;
        self.haste_at = None;
        self.wanted = (0, 0);
        self.tally_at = None;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Talon's Assassin's Path over the map's walls: out when outnumbered or low, after a champion behind a wall; Blade's End wounds on each champion) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:path"), Path::default());
    module.add_native_effect(WOUND_FX, Fx(wound));
    module.add_native_effect(EDGE_FX, Fx(edge));
    host.log(LogLevel::Info, "league_talon_vault v1 loaded (Talon's Assassin's Path vaults over walls, wounds per target).");
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

    /// League: a wound a spell hit on that champion (up to 3, none while it bleeds); at 3 his next attack on it bleeds
    /// it and takes them.
    #[test]
    fn wounds_stack_on_each_champion_and_the_third_bleeds() {
        assert_eq!(wound_after(0, false), Some(1));
        assert_eq!(wound_after(2, false), Some(3));
        assert_eq!(wound_after(3, false), Some(3));
        assert_eq!(wound_after(1, true), None);
        assert!(!edge_bleeds(0) && !edge_bleeds(2) && edge_bleeds(3));
        for s in [WOUND, BLEED, GO, WOUND_PIC] {
            assert!(s.len() <= BUFF_NAME_CAP, "{s}");
        }
    }

    /// The copy: every spell's wound and the attack's edge are the natives, no wound count on him left; the bleed reads
    /// `GO` (twice: the hit's tick, a tick later).
    #[test]
    fn the_copy_counts_wounds_on_the_target() {
        let copy = include_str!("../override/league_talon.data_champion");
        for gone in ["\"league_talon_p_1\"", "\"league_talon_p_3\"", "\"league_talon_p_cd\""] {
            assert!(!copy.contains(gone), "{gone} is still in the copy");
        }
        assert!(copy.matches(&format!("\"effect_ref\": \"{WOUND_FX}\"")).count() >= 5, "the spells' wounds");
        assert_eq!(copy.matches(&format!("\"effect_ref\": \"{EDGE_FX}\"")).count(), 1, "the attack's edge");
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{GO}\"")).count(), 2, "the bleed's two reads");
    }

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
        assert_eq!(parse_params(r#"{"e_cd":300,"e_reach":12000,"x":1}"#),
                   Params { e_cd: 300, e_reach: 12_000, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_moba_map_has_its_ninety_wall_cells() {
        let g = &Grid::builtin()[0];
        assert_eq!(g.walls(), 90);
        assert_eq!(g.size(), (30.0 * CELL, 30.0 * CELL));
    }

    #[test]
    fn a_vault_crosses_the_wall_and_lands_beyond() {
        let g = wall();
        let (to, start) = g.vault(at(4.7, 4.5), (1.0, 0.0), 16_000.0, 64_000.0).unwrap();
        assert!(start <= 16_000.0);
        assert!(to.0 >= 6.0 * CELL && !g.is_wall(to.0, to.1));
        // no wall within reach
        assert!(g.vault(at(2.0, 4.5), (1.0, 0.0), 16_000.0, 64_000.0).is_none());
        // the wall is too thick for the far limit
        assert!(g.vault(at(4.7, 4.5), (1.0, 0.0), 16_000.0, 30_000.0).is_none());
        // off the map
        assert!(g.vault(at(9.8, 4.5), (1.0, 0.0), 16_000.0, 64_000.0).is_none());
    }

    #[test]
    fn the_reach_is_leagues_650_units_not_half_a_cell() {
        // 11-05: 0 VAULT in 5 games with e_reach 16000 (half a 32000 cell); League's E reaches terrain 650 units = 42900
        let p = Params::default();
        assert!(p.e_reach >= CELL as usize && p.e_reach <= 45_000, "{}", p.e_reach);
        // the landing limit holds the reach, a two-cell wall and the margin
        assert!(p.e_far as f64 >= p.e_reach as f64 + 2.0 * CELL + MARGIN, "{}", p.e_far);
        let g = wall();
        // a wall 1.2 cells away (38400): vaulted now, not with the old reach
        let (to, start) = g.vault(at(3.8, 4.5), (1.0, 0.0), p.e_reach as f64, p.e_far as f64).unwrap();
        assert!(start > 16_000.0 && start <= p.e_reach as f64 && to.0 > 6.0 * CELL, "{start} {to:?}");
        assert!(g.vault(at(3.8, 4.5), (1.0, 0.0), 16_000.0, 64_000.0).is_none(), "the old reach never got there");
        // 1.5 cells away (48000): still too far
        assert!(g.vault(at(3.5, 4.5), (1.0, 0.0), p.e_reach as f64, p.e_far as f64).is_none());
        // the kit carries the same numbers (make_override writes them into the copy)
        let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_talon.py")).unwrap();
        assert!(src.contains(&format!("\"e_reach\": {}", p.e_reach)) && src.contains(&format!("\"e_far\": {}", p.e_far)));
    }

    #[test]
    fn the_nearest_wall_is_found_in_any_direction() {
        let g = wall();
        // 0.8 cell west of the wall column: 25600 (the wall's cell edge is at 5.0)
        let d = nearest_wall(&g, at(4.2, 4.5), 3.0 * CELL).unwrap();
        assert!((d - 0.8 * CELL).abs() <= STEP, "{d}");
        // east of it: the same wall behind him
        let d = nearest_wall(&g, at(6.5, 4.5), 3.0 * CELL).unwrap();
        assert!((d - 0.5 * CELL).abs() <= STEP, "{d}");
        assert_eq!(nearest_wall(&g, at(0.5, 0.5), 2.0 * CELL), None, "nothing within 2 cells");
    }

    #[test]
    fn the_chase_targets_are_the_ones_behind_a_wall() {
        let p = Params::default();
        let g = wall();
        let me = at(4.6, 4.5);
        let behind = foe(at(6.7, 4.4), 40, 7);
        let open = foe(at(3.0, 4.5), 40, 8);
        let ids: Vec<usize> = chase_targets(&p, &g, me, 80, &[open, behind]).iter().map(|f| f.id).collect();
        assert_eq!(ids, [7]);
        assert!(chase_targets(&p, &g, me, 30, &[behind]).is_empty(), "hurt himself: no chase wanted");
    }

    #[test]
    fn outnumbered_he_vaults_away_from_them() {
        let p = Params::default();
        let g = wall();
        let me = at(4.6, 4.5);
        let foes = [foe(at(3.6, 4.2), 100, 1), foe(at(3.7, 5.0), 100, 2)];
        assert!(wants_out(&p, me, 60, &foes, 0));
        // healthy, or with an ally beside him: he fights on
        assert!(!wants_out(&p, me, 90, &foes, 0));
        assert!(!wants_out(&p, me, 60, &foes, 1));
        let plan = plan_escape(&p, &g, me, &foes).unwrap();
        assert!(plan.to.0 > 6.0 * CELL, "over the wall: {:?}", plan.to);
        assert_eq!(plan.chase, None);
        // no wall on the way out (the wall is behind the enemies): the main pack's open-ground vault, not this one
        let me2 = at(2.0, 4.5);
        let foes2 = [foe(at(3.0, 4.2), 100, 1), foe(at(3.0, 5.0), 100, 2)];
        assert!(plan_escape(&p, &g, me2, &foes2).is_none());
    }

    #[test]
    fn low_with_one_near_also_wants_out() {
        let p = Params::default();
        let me = at(4.6, 4.5);
        assert!(wants_out(&p, me, 20, &[foe(at(3.8, 4.5), 100, 1)], 2));
        assert!(!wants_out(&p, me, 80, &[foe(at(3.8, 4.5), 100, 1)], 0));
        assert!(!wants_out(&p, me, 20, &[foe(at(0.5, 0.5), 100, 1)], 0));
    }

    #[test]
    fn he_chases_a_champion_behind_a_wall() {
        let p = Params::default();
        let g = wall();
        let me = at(4.6, 4.5);
        let target = foe(at(6.7, 4.4), 40, 7);
        let plan = plan_chase(&p, &g, me, 80, &[target]).unwrap();
        assert_eq!(plan.chase, Some(7));
        assert!(dist(plan.to, target.at) + CLOSER <= dist(me, target.at));
        // no wall between: he walks
        assert!(plan_chase(&p, &g, at(1.0, 9.0), 80, &[foe(at(3.0, 9.0), 40, 7)]).is_none());
        // a healthy target (no harvest), or he is hurt: no chase
        assert!(plan_chase(&p, &g, me, 80, &[foe(at(6.7, 4.4), 90, 7)]).is_none());
        assert!(plan_chase(&p, &g, me, 30, &[foe(at(6.7, 4.4), 40, 7)]).is_none());
        // not into a crowd
        let crowd = [target, foe(at(7.0, 4.0), 100, 8), foe(at(7.0, 5.0), 100, 9)];
        assert!(plan_chase(&p, &g, me, 80, &crowd).is_none());
    }

    #[test]
    fn a_champion_walking_through_a_wall_does_not_change_the_map() {
        let grids = Grid::builtin();
        let wall = (15.5 * CELL, 3.5 * CELL);                 // a moba wall cell
        assert!(grids[0].is_wall(wall.0, wall.1));
        // champions in the top and the bottom lane's corners (inside the lane maps' walls) and one crossing a jungle wall
        assert_eq!(current(&grids, &[(2.0 * CELL, 2.0 * CELL), (27.5 * CELL, 27.5 * CELL), wall]), Some(0));
    }

    #[test]
    fn the_names_fit() {
        for x in ["e_cd", "e_wall", "e_ghost", "e_haste", "vo_cd", "vo_e"] {
            assert!(tl(x).len() <= BUFF_NAME_CAP);
        }
    }

    /// 世界坐标的一个矩形：(左上, 右下)。
    type Rect = ((f64, f64), (f64, f64));

    /// 峡谷那样的墙格子（295 x 296 格，每格 60000/11，从 x = 30000/11 起，作者墙体文件的格子）：中心落在 `rects`
    /// （世界坐标的 (左上, 右下)）里的格子是墙。
    fn rift_walls(rects: &[Rect]) -> terrain::Walls {
        let (cell, origin) = (60_000.0 / 11.0, (30_000.0 / 11.0, 0.0));
        let rows: Vec<String> = (0..296)
            .map(|cy| {
                (0..295)
                    .map(|cx| {
                        let c = (origin.0 + (cx as f64 + 0.5) * cell, origin.1 + (cy as f64 + 0.5) * cell);
                        let wall = rects.iter().any(|&(a, b)| c.0 >= a.0 && c.0 <= b.0 && c.1 >= a.1 && c.1 <= b.1);
                        if wall { '#' } else { '.' }
                    })
                    .collect()
            })
            .collect();
        let rows: Vec<&str> = rows.iter().map(String::as_str).collect();
        terrain::Walls::from_rows(&rows, cell, origin, (terrain::RIFT_EXTENT, terrain::RIFT_EXTENT))
    }

    #[test]
    fn on_the_rift_he_vaults_the_rifts_walls() {
        let p = Params::default();
        // a wall 30000 thick in the Rift's far half, 20000 east of him; two enemies west of him
        let g = Grid::rift(Some(&rift_walls(&[((1_320_000.0, 1_100_000.0), (1_350_000.0, 1_300_000.0))])));
        let me = (1_300_000.0, 1_200_000.0);
        let foes = [foe((1_270_000.0, 1_190_000.0), 100, 1), foe((1_272_000.0, 1_215_000.0), 100, 2)];
        assert!(wants_out(&p, me, 60, &foes, 0));
        let plan = plan_escape(&p, &g, me, &foes).expect("over the Rift's wall");
        assert!(plan.to.0 > 1_345_000.0 && !g.is_wall(plan.to.0, plan.to.1) && g.inside(plan.to), "{:?}", plan.to);
        assert!(g.crosses(me, plan.to), "over the wall: {:?}", plan.to);
        // the game's own grid: past 960000 is off its map - never a vault out there (the old code)
        assert!(plan_escape(&p, &Grid::builtin()[0], me, &foes).is_none());
        // past 960000 it is the map on the Rift, open ground
        assert!(g.inside((1_000_000.0, 1_500_000.0)) && !g.is_wall(1_000_000.0, 1_500_000.0));
        // a wall of the game's own 5v5 map is none on the Rift: the native vault there finds no wall on the Rift
        let native = (15.5 * CELL, 3.5 * CELL);
        assert!(Grid::builtin()[0].vault((native.0 - 30_000.0, native.1), (1.0, 0.0), 42_000.0, 120_000.0).is_some());
        assert!(g.vault((native.0 - 30_000.0, native.1), (1.0, 0.0), 42_000.0, 120_000.0).is_none());
        // a champion behind the Rift's wall is chased over it
        let prey = foe((1_360_000.0, 1_200_000.0), 40, 7);
        assert_eq!(chase_targets(&p, &g, me, 80, &[prey]).len(), 1);
        assert_eq!(plan_chase(&p, &g, me, 80, &[prey]).map(|pl| pl.chase), Some(Some(7)));
    }

    /// 峡谷真的墙：开发者用 `LEAGUE_RIFT_WALLS` 指着作者的墙体文件时才跑（CI 没有文件，跳过）。
    #[test]
    fn on_the_rifts_real_walls_every_vault_lands_beyond_a_wall() {
        let Some(path) = std::env::var_os(terrain::RIFT_WALLS_ENV) else { return };
        let g = Grid::rift(Some(&terrain::load_rift_walls(&[path.into()]).unwrap()));
        let p = Params::default();
        // a wall on the way, sampled as `Grid::vault` does (every STEP from him: the Rift's small cells' corners fall
        // between `crosses`'s samples)
        let walled = |a: (f64, f64), b: (f64, f64)| {
            let d = dist(a, b);
            (1..).map(|k| k as f64 * STEP).take_while(|t| *t < d)
                .any(|t| g.is_wall(a.0 + (b.0 - a.0) / d * t, a.1 + (b.1 - a.1) / d * t))
        };
        let (mut spots, mut vaults) = (0, 0);
        let mut y = 20_000.0;
        while y < terrain::RIFT_EXTENT {
            let mut x = 20_000.0;
            while x < terrain::RIFT_EXTENT {
                if !g.is_wall(x, y) && g.inside((x, y)) {
                    spots += 1;
                    for (dx, dy) in [(20_000.0, 0.0), (-20_000.0, 0.0), (0.0, 20_000.0), (0.0, -20_000.0)] {
                        let foes = [foe((x + dx, y + dy), 100, 1), foe((x + dx * 1.1, y + dy * 1.1 + 3_000.0), 100, 2)];
                        if let Some(plan) = plan_escape(&p, &g, (x, y), &foes) {
                            assert!(!g.is_wall(plan.to.0, plan.to.1) && g.inside(plan.to), "({x},{y}) -> {:?}", plan.to);
                            assert!(walled((x, y), plan.to), "a vault crosses a wall: ({x},{y}) -> {:?}", plan.to);
                            vaults += 1;
                        }
                    }
                }
                x += 40_000.0;
            }
            y += 40_000.0;
        }
        assert!(spots > 300 && vaults > 100, "{vaults} vaults from {spots} spots");
    }

    #[test]
    fn on_the_rift_without_its_walls_file_he_never_vaults() {
        let p = Params::default();
        let g = Grid::rift(None);
        assert_eq!(g.size(), (terrain::RIFT_EXTENT, terrain::RIFT_EXTENT));
        let me = (1_300_000.0, 1_200_000.0);
        let foes = [foe((1_270_000.0, 1_190_000.0), 100, 1), foe((1_272_000.0, 1_215_000.0), 100, 2)];
        assert!(plan_escape(&p, &g, me, &foes).is_none());
        assert!(plan_chase(&p, &g, me, 80, &[foe((1_350_000.0, 1_200_000.0), 40, 7)]).is_none());
        assert_eq!(nearest_wall(&g, me, NEAR_WALL), None);
        // off the map is no wall either, and no landing
        assert!(!g.is_wall(1_700_000.0, 800_000.0) && !g.inside((1_614_546.0, 800_000.0)));
    }

    #[test]
    fn presim_lines_are_capped_for_the_launch_and_the_match_on_screen_is_not() {
        let logged: Vec<usize> = (0..LOG_EVERY * 3).filter_map(|_| noted("test presim", false)).collect();
        assert_eq!(logged.len(), LOG_FIRST + 3);
        assert_eq!(logged[LOG_FIRST..], [LOG_EVERY, LOG_EVERY * 2, LOG_EVERY * 3]);
        assert!((0..LOG_EVERY * 2).all(|_| noted("test shown", true).is_some()));
    }

    #[test]
    fn the_params_are_logged_once() {
        let p = Params::default();
        assert!(params_new(&p));
        assert!(!params_new(&p));
        assert!(params_new(&Params { e_cd: 1, ..Params::default() }), "other Params: again");
    }
}
