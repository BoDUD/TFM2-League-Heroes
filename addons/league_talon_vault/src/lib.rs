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
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。不用全局变量，服务端预模拟和你看的那场各算各的。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_talon_vault.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_talon_vault";

/// 主包泰隆的名字（buff、画面、音效都以它开头）。
fn tl(x: &str) -> String {
    format!("league_talon_{x}")
}

/// 墙格的边长（世界单位）。
pub const CELL: f64 = 32_000.0;
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

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

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
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
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
            e_reach: 16_000,
            e_far: 64_000,
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

/// 一张墙格子：`cells[y][x]`。
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

    /// 在地图里吗。
    pub fn inside(&self, p: (f64, f64)) -> bool {
        let (w, h) = self.size();
        p.0 >= 0.0 && p.1 >= 0.0 && p.0 < w && p.1 < h
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

/// 翻墙追击：隔着墙的敌方英雄（生命最低的先），翻过去离他更近，落点不在人堆里。
pub fn plan_chase(p: &Params, g: &Grid, me: (f64, f64), hp_pct: usize, foes: &[Foe]) -> Option<Plan> {
    let mut targets: Vec<&Foe> = foes
        .iter()
        .filter(|f| {
            let d = dist(me, f.at);
            d > CHASE_NEAR && d <= p.e_chase_r as f64 && g.crosses(me, f.at)
        })
        .filter(|f| hp_pct >= CHASE_HP && f.hp_pct <= PREY_HP)
        .collect();
    targets.sort_by_key(|f| f.hp_pct);
    let cos = CHASE_DEG.to_radians().cos();
    for t in targets {
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

// ===================== 小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

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
        if self.vaults <= 60 || self.vaults % 25 == 0 {
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
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Talon (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.goal = None;
            return;
        }
        let team = e.team();
        let Some(here) = pos(sim, me) else { return };
        if self.goal.is_some() || self.haste_at.is_some() {
            self.follow(sim, me, here);
            if self.goal.is_some() {
                return;
            }
        }
        if sim.tick() % EVERY != 0 || has_buff(sim, me, &tl("e_cd")) || has_cc(sim, me, &NO_VAULT) {
            return;
        }
        let mut champs = Vec::new();
        let mut foes = Vec::new();
        let mut allies = 0;
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_champion() || !u.is_alive() {
                continue;
            }
            let (x, y) = u.pos();
            let at = (x as f64, y as f64);
            champs.push(at);
            if u.team() != team && u.is_targetable() {
                let (hp, max) = u.hp();
                foes.push(Foe { at, hp_pct: hp * 100 / max.max(1), id: u.id() });
            } else if u.team() == team && u.id() != me && dist(here, at) <= self.p.e_safe_r as f64 {
                allies += 1;
            }
        }
        let grids = Grid::builtin();
        let Some(gi) = current(&grids, &champs) else { return };
        let g = &grids[gi];
        let mine = hp_pct(sim, me);
        let plan = if wants_out(&self.p, here, mine, &foes, allies) {
            plan_escape(&self.p, g, here, &foes)
        } else {
            plan_chase(&self.p, g, here, mine, &foes)
        };
        if let Some(plan) = plan {
            self.go(sim, me, here, plan);
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.goal = None;
        self.last = None;
        self.haste_at = None;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Talon's Assassin's Path over the map's walls: out when outnumbered or low, after a champion behind a wall) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:path"), Path::default());
    host.log(LogLevel::Info, "league_talon_vault v1 loaded (Talon's Assassin's Path vaults over walls).");
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
}
