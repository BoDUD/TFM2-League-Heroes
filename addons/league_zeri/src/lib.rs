//! 泽丽附加包：W「强穿激光」撞墙变超远激光，被动「内能迁转」真正偷取护盾（用户：「这个可以做附加包」）。
//!
//! 主包是纯数据：数据读不到地图的墙，也读不到敌人身上的护盾，所以主包里 W 打到小兵或野怪时才化为激光，被动的护盾是电击弹
//! 打中英雄时给自己的一个小护盾。`mod.override_info` 把主包的泽丽换成 `override/` 里的副本（tools/kit/build_zeri.py 的
//! native=True）：技能一样，只是
//! - W 的脉冲飞出时在她身上挂 `league_zeri_w_go`；她身上有 `league_zeri_w_wall` 时脉冲什么都不打（已经在墙上化成激光了）；
//! - 电击弹不再给小护盾（偷盾代替它）；
//! - 被动 `league_zeri:battery`。
//!
//! 被动每 tick 看一次：
//! - **撞墙激光**：看到 `w_go`（一次施放只处理一次），记下她这一刻的投射物，下一 tick 找出飞了约 `w_speed` 的那个 = 脉冲，
//!   定出方向；之后逐 tick 跟着它，它这一 tick 走过的线段碰到墙格（`maps.rs`，每格 32000）或 5v5 地图四边的墙面，就在碰到的
//!   地方挂 `w_wall`、从那里沿原方向射出 `w_laser` 长的激光（一个穿透的投射物 `league_zeri_w_wall`，打中的每个敌人
//!   受到 `w_dmg + w_ratio%` 攻击力的物理伤害并减速 `w_slow`% `w_slow_t` tick，同主包的 W）。脉冲先打中了单位（数据照常处理，
//!   小兵化激光）或飞完了，就不再跟。
//! - **偷盾**：她的伤害（普攻、技能都算，`on_attack`）打到带护盾的敌人时，被护盾挡下的部分的 `steal`% 变成她自己的护盾，
//!   持续 `steal_t` tick（英雄联盟 45%、3 秒），挂上护盾的图 `league_zeri_p_shv`。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。不用全局的对局状态，服务端预模拟和你看的
//! 那场各算各的（激光效果只读参数）。
//! 0.1.1（2026-10-19，用户：「泽丽突然没伤害」）：每 30 秒（对局时间）一行 `DMG 30s`：这 30 秒她打出的伤害（`on_attack`，
//! 普攻和技能都算）按她当时身上开着什么分（E 的穿透弹 `e_on`、R 的超限 `r_on`、都没有），其中打英雄的多少、命中次数、
//! 开始的普攻次数（其中充能弹几次）、死着的 tick 数——看伤害是哪一段、哪种状态下掉没的。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zeri.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod maps;

const ID: &str = "league_zeri";

/// 主包泽丽的名字（buff、投射物、音效都以它开头）。
fn zr(x: &str) -> String {
    format!("league_zeri_{x}")
}

/// 墙格子的边长（引擎的碰撞墙）。
pub const CELL: f64 = 32_000.0;
/// 5v5 地图四边画出来的墙面（league_camille_wall 量的：x 22500 / 937500，y 26000 / 932000）。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);
/// 沿脉冲走过的线段每隔多远看一次墙。
pub const STEP: f64 = 1_000.0;
/// 激光投射物的速度（每 tick）。
pub const LASER_SPEED: u64 = 20_000;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ZERI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_zeri.log");
        }
    }
    PathBuf::from("league_zeri.log")
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
    pub steal: usize,
    pub steal_t: usize,
    pub w_laser: usize,
    pub w_speed: usize,
    pub w_dmg: usize,
    pub w_ratio: usize,
    pub w_slow: usize,
    pub w_slow_t: usize,
    pub w_lw: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            steal: 45,
            steal_t: 180,
            w_laser: 100_000,
            w_speed: 9_000,
            w_dmg: 60,
            w_ratio: 110,
            w_slow: 35,
            w_slow_t: 120,
            w_lw: 9_000,
        }
    }
}

/// `{"steal":45,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "steal" => p.steal = v,
            "steal_t" => p.steal_t = v,
            "w_laser" => p.w_laser = v,
            "w_speed" => p.w_speed = v,
            "w_dmg" => p.w_dmg = v,
            "w_ratio" => p.w_ratio = v,
            "w_slow" => p.w_slow = v,
            "w_slow_t" => p.w_slow_t = v,
            "w_lw" => p.w_lw = v,
            _ => {}
        }
    }
    p
}

/// 激光效果用的参数（被动 `configure` 时写进来；所有泽丽共用同一张参数表）。
static LASER: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

// ===================== 墙 =====================

/// 一张墙格子：`cells[y][x]` 为 true 是墙；`bounds`（x0, y0, x1, y1）外是 5v5 地图四边的墙面。
#[derive(Clone, Debug, PartialEq)]
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
    pub bounds: Option<(f64, f64, f64, f64)>,
}

impl Grid {
    pub fn from_rows(rows: &[&str], bounds: Option<(f64, f64, f64, f64)>) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(), bounds }
    }

    /// 内置的三张图（5v5 加四边的墙面）。
    pub fn builtin() -> Vec<(&'static str, Grid)> {
        vec![
            ("Moba", Grid::from_rows(&maps::MOBA, Some(MOBA_BOUNDS))),
            ("SingleLane", Grid::from_rows(&maps::SINGLE_LANE, None)),
            ("DeathMatch", Grid::from_rows(&maps::DEATH_MATCH, None)),
        ]
    }

    /// 墙格（或地图外）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return true;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|row| row.get(cx)).copied().unwrap_or(true)
    }

    /// 激光能从这里射出吗：墙格或四边的墙面。
    pub fn solid(&self, x: f64, y: f64) -> bool {
        self.is_wall(x, y) || self.bounds.is_some_and(|(x0, y0, x1, y1)| x < x0 || y < y0 || x > x1 || y > y1)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|v| **v).count()
    }
}

/// 当前对局的地图：站进墙里的单位最少的那张，一样少时取墙最多的。
pub fn pick_grid(points: &[(f64, f64)]) -> (&'static str, Grid) {
    Grid::builtin()
        .into_iter()
        .map(|(n, g)| (points.iter().filter(|p| g.is_wall(p.0, p.1)).count(), g.walls(), n, g))
        .min_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)))
        .map(|(_, _, n, g)| (n, g))
        .expect("three built-in maps")
}

/// 从 `a` 走到 `b`，第一个落在墙里的点（每 `STEP` 看一次，`a` 本身不算）。
pub fn first_wall(grid: &Grid, a: (f64, f64), b: (f64, f64)) -> Option<(f64, f64)> {
    let d = dist(a, b);
    let n = (d / STEP).ceil().max(1.0) as usize;
    (1..=n).map(|k| lerp(a, b, k as f64 / n as f64)).find(|p| grid.solid(p.0, p.1))
}

// ===================== 计算 =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn lerp(a: (f64, f64), b: (f64, f64), t: f64) -> (f64, f64) {
    (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
}

fn unit_vec(a: (f64, f64), b: (f64, f64)) -> Option<(f64, f64)> {
    let d = dist(a, b);
    (d > 1.0).then(|| ((b.0 - a.0) / d, (b.1 - a.1) / d))
}

/// 脉冲是哪个：上一 tick 记下的位置里，有一个到现在这个投射物正好飞了约一步（0.6–1.6 倍 `speed`）。
pub fn find_pulse(before: &[(f64, f64)], now: &[(f64, f64)], speed: f64) -> Option<((f64, f64), (f64, f64))> {
    let mut best: Option<(f64, (f64, f64), (f64, f64))> = None;
    for &p in now {
        for &q in before {
            let d = dist(p, q);
            if d >= 0.6 * speed && d <= 1.6 * speed {
                let off = (d - speed).abs();
                if best.is_none_or(|b| off < b.0) {
                    best = Some((off, q, p));
                }
            }
        }
    }
    best.and_then(|(_, q, p)| unit_vec(q, p).map(|dir| (p, dir)))
}

/// 这一 tick 脉冲在哪：离预计位置最近、在半步以内的那个投射物。
pub fn follow(now: &[(f64, f64)], expect: (f64, f64), speed: f64) -> Option<(f64, f64)> {
    now.iter()
        .copied()
        .map(|p| (dist(p, expect), p))
        .filter(|(d, _)| *d <= 0.5 * speed)
        .min_by(|a, b| a.0.total_cmp(&b.0))
        .map(|(_, p)| p)
}

/// 激光的终点：从墙上的点沿方向射出 `len`，不出地图（坐标不小于 0）。
pub fn laser_end(from: (f64, f64), dir: (f64, f64), len: f64) -> (f64, f64) {
    ((from.0 + dir.0 * len).max(0.0), (from.1 + dir.1 * len).max(0.0))
}

/// 偷到多少护盾：被护盾挡下的那部分（伤害和护盾取小）的 `steal`%。
pub fn stolen(damage: usize, shield: usize, steal: usize) -> usize {
    damage.min(shield) * steal / 100
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

fn alive(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive())
}

fn timed(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

/// 她的投射物现在都在哪。
fn mine(sim: &StableSim<'_>, me: usize) -> Vec<(f64, f64)> {
    (0..sim.projectile_count())
        .filter_map(|i| sim.projectile_at(i))
        .filter(|p| p.caster_id == me && !p.is_end)
        .map(|p| (p.x as f64, p.y as f64))
        .collect()
}

fn upos(p: (f64, f64)) -> (u64, u64) {
    (p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

// ===================== 被动 =====================

/// 正在跟的一道脉冲。
#[derive(Clone, Debug)]
struct Pulse {
    start: usize,
    before: Vec<(f64, f64)>,
    at: Option<((f64, f64), (f64, f64))>,
}

/// 诊断（2026-10-14，用户：「泽丽的普攻和技能没有打出伤害」）：每个泽丽前 `DIAG_ATTACKS` 次普攻、`DIAG_PULSES` 次 W，
/// 记下她的弹道每 tick 在哪、70000 以内的敌人在哪、打中了谁（`on_attack`，技能也算）——看真引擎里弹道是飞到目标身上，还是
/// 从头顶飞过（离线模拟器里两样都打得中，日志行都以 DIAG 开头）。
#[derive(Clone, Default)]
struct Diag {
    attacks: usize,
    pulses: usize,
    /// what is being watched (attack / W), its number and the tick it began
    open: Option<(&'static str, usize, usize)>,
}

/// 每 30 秒的伤害统计（0.1.1）：E 开着 / R 开着 / 都没有 三份（伤害, 打英雄的伤害, 命中）。
#[derive(Clone, Default)]
struct Tally {
    dmg: [(usize, usize, usize); 3],
    attacks: usize,
    charged: usize,
    /// ticks she was dead or not updated (the host may skip a dead champion's passive)
    dead: usize,
    /// the last tick seen and the next line's tick (kept across lines)
    last: usize,
    next: usize,
}

/// 30 s of match time between the `DMG 30s` lines.
const TALLY_TICKS: usize = 1800;

impl Tally {
    fn line(&self) -> String {
        let part = |n: &str, (d, c, h): (usize, usize, usize)| format!("{n} {d} ({c} on champions, {h} hits)");
        let total: usize = self.dmg.iter().map(|x| x.0).sum();
        format!("DMG 30s: {total} dealt - {}, {}, {}; attacks started {} ({} charged); dead {} ticks",
                part("E on", self.dmg[0]), part("R on", self.dmg[1]), part("plain", self.dmg[2]), self.attacks,
                self.charged, self.dead)
    }
}

const DIAG_ATTACKS: usize = 16;
const DIAG_PULSES: usize = 8;
const DIAG_TICKS: usize = 18;

impl Diag {
    fn begin(&mut self, sim: &StableSim<'_>, me: usize, kind: &'static str) {
        let n = if kind == "attack" { &mut self.attacks } else { &mut self.pulses };
        if *n >= if kind == "attack" { DIAG_ATTACKS } else { DIAG_PULSES } {
            return;
        }
        *n += 1;
        let n = *n;
        let tick = sim.tick();
        self.open = Some((kind, n, tick));
        let Some(at) = pos(sim, me) else { return };
        let team = sim.get_entity(me).map_or(usize::MAX, |e| e.team());
        let mut foes: Vec<(f64, String)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_alive() && u.team() != team && u.is_targetable())
            .filter_map(|u| {
                let (x, y) = u.pos();
                let d = dist(at, (x as f64, y as f64));
                (d <= 70000.0).then(|| (d, format!("{} {} d {d:.0}", who(sim, u.id()), pt((x as f64, y as f64)))))
            })
            .collect();
        foes.sort_by(|a, b| a.0.total_cmp(&b.0));
        let list: Vec<String> = foes.into_iter().take(6).map(|f| f.1).collect();
        wlog(format!("{} DIAG {kind} #{n}: she is at {}, enemies near: [{}], her projectiles: {:?}", head(sim, me), pt(at),
                     list.join("; "), mine(sim, me).iter().map(|p| pt(*p)).collect::<Vec<_>>()));
    }

    fn tick(&mut self, sim: &StableSim<'_>, me: usize) {
        let Some((kind, n, start)) = self.open else { return };
        let k = sim.tick().saturating_sub(start);
        if k > DIAG_TICKS {
            self.open = None;
            return;
        }
        if k == 0 {
            return;
        }
        let shots: Vec<String> = (0..sim.projectile_count())
            .filter_map(|i| sim.projectile_at(i))
            .filter(|p| p.caster_id == me)
            .map(|p| format!("{}{}", pt((p.x as f64, p.y as f64)), if p.is_end { " end" } else { "" }))
            .collect();
        wlog(format!("{} DIAG {kind} #{n} +{k}: her projectiles {shots:?}", head(sim, me)));
    }

    fn hit(&self, sim: &StableSim<'_>, me: usize, target: usize, damage: usize) {
        let Some((kind, n, start)) = self.open else { return };
        let at = pos(sim, target).map_or("-".into(), pt);
        wlog(format!("{} DIAG {kind} #{n} +{}: HIT {} at {at} for {damage}", head(sim, me), sim.tick().saturating_sub(start),
                     who(sim, target)));
    }
}

/// 每个泽丽一份：参数、地图、正在跟的脉冲、已处理到哪个 tick 的施放、计数。
#[derive(Clone, Default)]
struct Battery {
    p: Params,
    grid: Option<(&'static str, Grid)>,
    pulse: Option<Pulse>,
    done_until: usize,
    lasers: usize,
    pulses: usize,
    steals: usize,
    diag: Diag,
    tally: Tally,
}

impl Battery {
    fn grid(&mut self, sim: &StableSim<'_>, me: usize) -> Grid {
        if self.grid.is_none() {
            let points: Vec<(f64, f64)> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|e| e.is_alive())
                .map(|e| {
                    let (x, y) = e.pos();
                    (x as f64, y as f64)
                })
                .collect();
            let (name, g) = pick_grid(&points);
            wlog(format!("{} map: {name} ({} wall cells; {} units placed)", head(sim, me), g.walls(), points.len()));
            self.grid = Some((name, g));
        }
        self.grid.as_ref().map(|g| g.1.clone()).unwrap_or_else(|| Grid::builtin().remove(0).1)
    }

    /// 跟着脉冲走一 tick；碰到墙就射激光。返回 false = 不再跟。
    fn track(&mut self, sim: &mut StableSim<'_>, me: usize) -> bool {
        let Some(pulse) = self.pulse.clone() else { return false };
        let tick = sim.tick();
        if !has_buff(sim, me, &zr("w_go")) {
            return false;
        }
        let speed = self.p.w_speed as f64;
        let now = mine(sim, me);
        let (from, dir) = match pulse.at {
            None => {
                let Some((p, dir)) = find_pulse(&pulse.before, &now, speed) else {
                    if tick > pulse.start + 3 {
                        wlog(format!("{} W: the pulse was not found among her projectiles", head(sim, me)));
                        return false;
                    }
                    self.pulse.as_mut().unwrap().before = now;
                    return true;
                };
                // the first step: from where it was a tick ago
                ((p.0 - dir.0 * speed, p.1 - dir.1 * speed), dir)
            }
            Some((last, dir)) => (last, dir),
        };
        let Some(to) = follow(&now, (from.0 + dir.0 * speed, from.1 + dir.1 * speed), speed) else {
            return false; // it hit a unit (the data took it) or flew its range out
        };
        let grid = self.grid(sim, me);
        if let Some(w) = first_wall(&grid, from, to) {
            self.laser(sim, me, w, dir);
            return false;
        }
        self.pulse.as_mut().unwrap().at = Some((to, dir));
        true
    }

    fn laser(&mut self, sim: &mut StableSim<'_>, me: usize, at: (f64, f64), dir: (f64, f64)) {
        timed(sim, me, &zr("w_wall"), 30);
        let end = laser_end(at, dir, self.p.w_laser as f64);
        let (x, y) = upos(at);
        let (tx, ty) = upos(end);
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team: sim.get_entity(me).map_or(0, |e| e.team()),
            x,
            y,
            radius: (self.p.w_lw / 2) as u64,
            speed: LASER_SPEED,
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: tx,
            target_y: ty,
            penetrate: true,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        let ok = sim.spawn_projectile(&zr("w_wall"), &format!("{ID}:laser"), &spec);
        sim.play_sfx(&zr("w_beam"), me, &InputTargetV1::pos(x, y));
        self.lasers += 1;
        if self.lasers <= 60 || self.lasers % 25 == 0 {
            wlog(format!(
                "{} W #{}: the pulse met a wall at {} - laser to {}{}",
                head(sim, me),
                self.lasers,
                pt(at),
                pt(end),
                if ok { "" } else { " (spawn_projectile refused)" }
            ));
        }
    }
}

impl StablePassive for Battery {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
        *LASER.lock().unwrap_or_else(|e| e.into_inner()) = self.p.clone();
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.pulse = None;
        self.done_until = 0;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Zeri (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.diag.tick(sim, me);
        let t = sim.tick();
        if self.tally.last > 0 && t > self.tally.last + 1 {
            self.tally.dead += t - self.tally.last - 1;
        }
        self.tally.last = t;
        if self.tally.next == 0 {
            self.tally.next = (t / TALLY_TICKS + 1) * TALLY_TICKS;
        } else if t >= self.tally.next {
            wlog(format!("{} {}", head(sim, me), self.tally.line()));
            self.tally = Tally { last: t, next: (t / TALLY_TICKS + 1) * TALLY_TICKS, ..Tally::default() };
        }
        if !alive(sim, me) {
            self.tally.dead += 1;
            self.pulse = None;
            return;
        }
        if self.pulse.is_some() {
            if !self.track(sim, me) {
                self.pulse = None;
            }
            return;
        }
        let tick = sim.tick();
        if tick >= self.done_until && has_buff(sim, me, &zr("w_go")) {
            self.done_until = tick + 20;
            self.pulses += 1;
            self.pulse = Some(Pulse { start: tick, before: mine(sim, me), at: None });
            if self.pulses <= 30 || self.pulses % 25 == 0 {
                let at = pos(sim, me).map_or("-".into(), pt);
                wlog(format!("{} W #{}: pulse fired from {at}", head(sim, me), self.pulses));
            }
            self.diag.begin(sim, me, "W");
        }
    }

    fn on_base_attack(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.tally.attacks += 1;
        if has_buff(sim, me, &zr("p_full")) {
            self.tally.charged += 1;
        }
        self.diag.begin(sim, me, "attack");
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        self.diag.hit(sim, me, target, *damage);
        let slot = if has_buff(sim, me, &zr("e_on")) { 0 } else if has_buff(sim, me, &zr("r_on")) { 1 } else { 2 };
        let champ = sim.get_entity(target).is_some_and(|t| t.is_champion());
        let d = &mut self.tally.dmg[slot];
        d.0 += *damage;
        d.1 += if champ { *damage } else { 0 };
        d.2 += 1;
        let Some(t) = sim.get_entity(target) else { return };
        let shield = t.shield();
        let team = sim.get_entity(me).map_or(usize::MAX, |e| e.team());
        if shield == 0 || t.team() == team {
            return;
        }
        let gain = stolen(*damage, shield, self.p.steal);
        if gain == 0 {
            return;
        }
        sim.entity_add_shield(me, gain, self.p.steal_t);
        timed(sim, me, &zr("p_shv"), self.p.steal_t);
        sim.play_sfx(&zr("shield"), me, &InputTargetV1::target(me));
        self.steals += 1;
        if self.steals <= 60 || self.steals % 25 == 0 {
            wlog(format!(
                "{} STEAL #{}: hit {} for {} on a {shield} shield -> her shield +{gain} for {} ticks",
                head(sim, me),
                self.steals,
                who(sim, target),
                *damage,
                self.p.steal_t
            ));
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.pulse = None;
    }
}

// ===================== 激光打中 =====================

/// 激光打中一个敌人：W 的物理伤害和减速（数字同主包，从被动的参数来）。
struct Laser;

impl StableEffectType for Laser {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let target = input.target_id;
        if !alive(sim, target) {
            return;
        }
        let p = LASER.lock().unwrap_or_else(|e| e.into_inner()).clone();
        let ad = sim.get_entity(caster).map_or(0, |e| e.stat().attack);
        sim.deal_damage(caster, target, p.w_dmg + ad * p.w_ratio / 100, 0, AttackTypeV1::Skill);
        let mut slow = BuffV1::timed(&zr("w_slow"), p.w_slow_t);
        slow.move_speed_mult = -(p.w_slow as i32);
        sim.entity_remove_buff(target, &zr("w_slow"));
        sim.add_buff(target, &slow);
        sim.play_view_effect(&zr("w_hit"), caster, &InputTargetV1::target(target), 0, 0, 0);
        sim.play_sfx(&zr("w_hit"), caster, &InputTargetV1::target(target));
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = LASER.lock().unwrap_or_else(|e| e.into_inner()).clone();
        (p.w_dmg + caster_stat.attack * p.w_ratio / 100, 0)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Zeri: Ultrashock Laser off walls, Living Battery steals shields) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:battery"), Battery::default());
    module.add_native_effect(format!("{ID}:laser"), Laser);
    host.log(LogLevel::Info, "league_zeri v1 loaded (Zeri's wall laser and shield steal).");
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
    fn the_30_s_line_splits_the_damage_by_her_state() {
        let t = Tally { dmg: [(70, 70, 1), (0, 0, 0), (200, 90, 3)], attacks: 4, charged: 1, dead: 0, last: 0, next: 0 };
        let want = ["DMG 30s: 270 dealt - E on 70 (70 on champions, 1 hits), R on 0 (0 on champions, 0 hits),",
                    " plain 200 (90 on champions, 3 hits); attacks started 4 (1 charged); dead 0 ticks"];
        assert_eq!(t.line(), want.concat());
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"steal":50,"w_laser":90000,"x":1}"#),
                   Params { steal: 50, w_laser: 90_000, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_moba_map_is_picked_by_where_the_units_stand() {
        // the 5v5 bases sit in corners that are walls on the other two maps
        let (name, g) = pick_grid(&[(480_000.0, 480_000.0), (50_000.0, 50_000.0), (900_000.0, 900_000.0)]);
        assert_eq!(name, "Moba");
        assert!(g.walls() > 50);
        assert!(g.solid(10_000.0, 500_000.0), "the map's left edge is a wall face");
        assert!(!g.solid(480_000.0, 480_000.0));
    }

    #[test]
    fn the_first_wall_point_on_a_segment() {
        let g = Grid::from_rows(&["....", "..#.", "...."], None);
        // row 1, column 2 is a wall: x 64000-96000, y 32000-64000
        let w = first_wall(&g, (10_000.0, 48_000.0), (120_000.0, 48_000.0)).unwrap();
        assert!(w.0 >= 64_000.0 && w.0 < 65_100.0, "{w:?}");
        assert_eq!(first_wall(&g, (10_000.0, 10_000.0), (120_000.0, 10_000.0)), None);
    }

    #[test]
    fn the_pulse_is_the_projectile_that_flew_one_step() {
        let before = [(100_000.0, 100_000.0), (300_000.0, 100_000.0)];
        let now = [(109_000.0, 100_000.0), (302_000.0, 100_000.0)];
        let (p, dir) = find_pulse(&before, &now, 9_000.0).unwrap();
        assert_eq!(p, (109_000.0, 100_000.0));
        assert!((dir.0 - 1.0).abs() < 1e-9 && dir.1.abs() < 1e-9);
        assert_eq!(follow(&now, (109_500.0, 100_000.0), 9_000.0), Some((109_000.0, 100_000.0)));
        assert_eq!(follow(&now, (150_000.0, 100_000.0), 9_000.0), None);
    }

    #[test]
    fn a_shield_steal_takes_only_what_the_shield_stopped() {
        assert_eq!(stolen(100, 300, 45), 45);
        assert_eq!(stolen(300, 100, 45), 45);
        assert_eq!(stolen(100, 0, 45), 0);
    }

    #[test]
    fn the_laser_stays_on_the_map() {
        assert_eq!(laser_end((50_000.0, 50_000.0), (-1.0, 0.0), 100_000.0), (0.0, 50_000.0));
        assert_eq!(laser_end((50_000.0, 50_000.0), (1.0, 0.0), 100_000.0), (150_000.0, 50_000.0));
    }
}
