//! 塔莉垭扩展包（用户 2026-10-24：「技能对了，继续接入（音效、文字、注册、扩展包）」）：墙幔立起的墙是真的地形。
//!
//! 主包是纯数据：数据造不出挡路的东西，墙幔的竖墙和横墙都只是一片区域，碰到的敌人减速 `r_slow`%（卡在墙边），竖墙
//! 立起时站在上面的被拖到她那一侧。`mod.override_info` 把主包的塔莉垭换成 `override/` 里的副本（tools/kit/build_taliyah.py
//! 的 native=1）：数据和主包一样，只是墙不再减速（区域还在，只当本包找墙的位置用），立墙时多挂两个标记，`passive` 挂本包的
//! `league_taliyah:wall`：
//!
//! - **竖墙**（目标近、或她已在打架）：她身上新出现 `league_taliyah_wall_up` 的那一 tick，带 `league_taliyah_aim` 的敌方英雄
//!   （墙幔的目标）站的地方就是墙心（数据的 `r_mark` 1 tick 落在它脚下，墙从那里立起）。竖着的长方形，宽 `r_w`、高 `r_h`，
//!   立 `r_t` tick；立起时站在墙上的单位推到她那一侧（主包的拖出一样）。
//! - **横墙**（骑墙）：她身上新出现 `league_taliyah_lay_up` 的那一 tick，数据从她脚下朝带 `aim` 的目标射出 `r_n` 根看不见的线，
//!   第 k 根飞 k×`r_seg` 停下，在那里铺一段 `r_seg`×`r_w` 的横墙。本包按她和目标的位置算出每一段的落点和到达的 tick，
//!   再对到她那几 tick 新放出、停着不动的区域上（线停在哪由引擎定，最多多飞一 tick 的 `r_lay_speed`）；对不上的到点就按算的
//!   位置立。每段立 `r_t` tick；铺下时压在上面的单位推到离得近的那一侧（上或下）。
//! - **挡路**：墙立着时，每个单位（英雄、小兵、野怪、召唤物，两边都算，她自己也算）的中心一进墙（长方形四边各加单位半径），
//!   就退回上一 tick 的位置，但保留顺着墙走的那一半（竖墙保留上下、横墙保留左右），绕着墙走不会被粘住。她骑墙
//!   （`league_taliyah_riding`）时不挡她：她站在墙顶上；跳下来那一 tick 她还在墙上，就推到近的一侧。
//!   0.2.2（11-03 夜里的日志：正对着墙走的单位每 tick 被放回原处，小兵在同一个坐标站了 281 tick，布隆、洛这些队友也一样）：
//!   挡了 `STALL_T` tick 没挪动，就顺着墙往近的那头挪（[`unstick`]），过了墙头它自己就绕过去；`HOLD` 一个单位一块墙只记一行
//!   （墙倒的时候：挡了几 tick、顺着墙挪了几 tick），以前每 tick 一行。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态都在被动自己身上（每局一份）。
//! - **脱战骑石头**（0.2.0，[`view`]）：没在打架时把移动动画 `run`（用脚跑）换成 `surf`（冲浪），打起来换回来。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_taliyah.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_taliyah";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_taliyah") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 单位半径读不到时用的值。
pub const BODY: u64 = 6000;
/// 横墙一段到点后最多再等这么多 tick 对区域，过了就按算的位置立。
pub const LATE: usize = 3;
/// 两个投射物位置这么近算同一处。
pub const SAME: u64 = 200;
/// 被墙挡住、这么多 tick 自己没挪出 `STALL_MOVE` 就顺着墙往近的那头挪（0.2.2，[`unstick`]）。
pub const STALL_T: usize = 20;
pub const STALL_MOVE: u64 = 1_000;
/// 顺着墙挪时每 tick 挪它自己想走的那么远，夹在这两个数之间。
pub const STEP_MIN: u64 = 300;
pub const STEP_MAX: u64 = 2_000;
/// 顺着墙挪不动时（卡在台阶的角里）再往墙外挪最多这么多个 step（0.2.3，[`unstick`]）。
pub const OFF_STEPS: u64 = 2;
/// 横墙相邻两段的墙心相距不超过半宽的这么多倍就是同一道墙（铺下时相距一段 = 2 个半宽）。
pub const LINK_HW: u64 = 3;
/// 地图边长（坐标 0..MAP）。
const MAP: u64 = 960_000;

fn sn(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_TALIYAH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_taliyah.log");
        }
    }
    PathBuf::from("league_taliyah.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub fn wlog(msg: impl AsRef<str>) {
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

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 墙立多久（tick）。
    pub r_t: usize,
    /// 竖墙的宽、高；横墙一段的高是 `r_w`。
    pub r_w: u64,
    pub r_h: u64,
    /// 横墙一段的长（也是相邻两段的间距）、几段、铺墙的线飞多快。
    pub r_seg: u64,
    pub r_n: usize,
    pub r_lay_speed: u64,
}

impl Default for Params {
    fn default() -> Self {
        Params { r_t: 300, r_w: 12000, r_h: 120000, r_seg: 26000, r_n: 6, r_lay_speed: 8000 }
    }
}

/// `{"r_t":300,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        match k {
            "r_t" => p.r_t = v as usize,
            "r_w" => p.r_w = v,
            "r_h" => p.r_h = v,
            "r_seg" => p.r_seg = v,
            "r_n" => p.r_n = v as usize,
            "r_lay_speed" => p.r_lay_speed = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 墙的朝向：竖墙把压在上面的推到她那一侧（`left`：她在墙左边），横墙推到近的上下一侧。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Side {
    Upright { left: bool },
    Flat,
}

/// 一块墙：中心、半宽、半高、拆掉的 tick、朝向。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Wall {
    pub x: u64,
    pub y: u64,
    pub hw: u64,
    pub hh: u64,
    pub until: usize,
    pub side: Side,
}

impl Wall {
    pub fn upright(p: &Params, (x, y): (u64, u64), left: bool, until: usize) -> Wall {
        Wall { x, y, hw: p.r_w / 2, hh: p.r_h / 2, until, side: Side::Upright { left } }
    }

    pub fn flat(p: &Params, (x, y): (u64, u64), until: usize) -> Wall {
        Wall { x, y, hw: p.r_seg / 2, hh: p.r_w / 2, until, side: Side::Flat }
    }
}

/// 单位中心在墙里（长方形四边各加单位半径）。
pub fn inside(w: &Wall, (x, y): (u64, u64), r: u64) -> bool {
    x.abs_diff(w.x) < w.hw + r && y.abs_diff(w.y) < w.hh + r
}

fn clear(walls: &[Wall], q: (u64, u64), r: u64) -> bool {
    !walls.iter().any(|w| inside(w, q, r))
}

/// 压在墙上的单位推出去：竖墙推到她那一侧（只改 x），横墙推到近的一侧（只改 y）。
pub fn push_out(w: &Wall, (x, y): (u64, u64), r: u64) -> (u64, u64) {
    match w.side {
        Side::Upright { left } => {
            let edge = w.hw + r + 1;
            (if left { w.x.saturating_sub(edge) } else { w.x + edge }, y)
        }
        Side::Flat => {
            let edge = w.hh + r + 1;
            (x, if y < w.y { w.y.saturating_sub(edge) } else { w.y + edge })
        }
    }
}

/// 这一 tick 单位该在哪（`None`：不用动）。进了墙：上一 tick 在墙外就退回去，只留顺着墙的那一半移动（竖墙留 y、横墙
/// 留 x），留不住就整个退回；上一 tick 也在墙里（墙刚立起压着它、她刚跳下墙），就推出去（推到的地方又在另一块墙里，
/// 就接着从那块推，最多推几次）；推完还在墙里，就找最近的出口（`push_clear`），找不到就不推。
pub fn hold(walls: &[Wall], last: Option<(u64, u64)>, now: (u64, u64), r: u64) -> Option<(u64, u64)> {
    let w = walls.iter().find(|w| inside(w, now, r))?;
    if let Some(l) = last.filter(|&l| clear(walls, l, r)) {
        let slide = match w.side {
            Side::Upright { .. } => (l.0, now.1),
            Side::Flat => (now.0, l.1),
        };
        return Some(if clear(walls, slide, r) { slide } else { l });
    }
    let mut q = push_out(w, now, r);
    for _ in 0..walls.len() {
        match walls.iter().find(|w| inside(w, q, r)) {
            Some(w) => q = push_out(w, q, r),
            None => break,
        }
    }
    if clear(walls, q, r) {
        return Some(q);
    }
    push_clear(walls, now, r)
}

/// 一个被墙挡住的单位（0.2.2）：从哪开始算没挪动（`at`）、挡了几 tick 没挪出 `STALL_MOVE`（`ticks`）、正在顺着墙挪的方向
/// （`dir`：true 往这道墙 [`line_of`] 的 b 头，x 大的那头，x 一样时 y 大的那头）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Stall {
    pub at: (u64, u64),
    pub ticks: usize,
    pub dir: Option<bool>,
}

type F2 = (f64, f64);

fn fdist(a: F2, b: F2) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn unit(a: F2, b: F2) -> F2 {
    let d = fdist(a, b);
    if d < 1.0 { (1.0, 0.0) } else { ((b.0 - a.0) / d, (b.1 - a.1) / d) }
}

/// 一道墙的两头（0.2.3）：横墙的几段是一次铺下的台阶，相邻段的墙心相距不超过 `LINK_HW` 个半宽的连成一道，两头是相距最远的
/// 两个墙心各往外半段（a 是 x 小的那头，x 一样时 y 小的）；只有一段就是它的左右两头；竖墙自成一道，两头是它的上下两头。
/// 0.2.2 只顺着挡住它的那一段挪：台阶里一段的两头都被相邻的段堵着，单位在角里来回（11-04 的日志：43 次 HOLD 里 5 次超过 150 tick，
/// 她自己 235 tick 只挪了 12 tick）。
pub fn line_of(walls: &[Wall], w: &Wall) -> (F2, F2) {
    if let Side::Upright { .. } = w.side {
        return ((w.x as f64, (w.y - w.hh) as f64), (w.x as f64, (w.y + w.hh) as f64));
    }
    let c = |w: &Wall| (w.x as f64, w.y as f64);
    let link = (LINK_HW * w.hw) as f64;
    let mut group = vec![c(w)];
    let mut grew = true;
    while grew {
        grew = false;
        for o in walls.iter().filter(|o| o.side == Side::Flat) {
            let q = c(o);
            if !group.contains(&q) && group.iter().any(|&g| fdist(g, q) <= link) {
                group.push(q);
                grew = true;
            }
        }
    }
    let mut ends = (group[0], group[0]);
    for &a in &group {
        for &b in &group {
            if fdist(a, b) > fdist(ends.0, ends.1) {
                ends = (a, b);
            }
        }
    }
    let (mut a, mut b) = ends;
    if a == b {
        a = (a.0 - w.hw as f64, a.1);
        b = (b.0 + w.hw as f64, b.1);
    }
    if (a.0, a.1) > (b.0, b.1) {
        std::mem::swap(&mut a, &mut b);
    }
    let (d, hw) = (unit(a, b), w.hw as f64);
    ((a.0 - d.0 * hw, a.1 - d.1 * hw), (b.0 + d.0 * hw, b.1 + d.1 * hw))
}

/// 这道墙离 `p` 近的那一头：true = b 头（投到墙线上过了一半）。
pub fn nearer_end(line: &(F2, F2), p: (u64, u64)) -> bool {
    let d = unit(line.0, line.1);
    let t = (p.0 as f64 - line.0 .0) * d.0 + (p.1 as f64 - line.0 .1) * d.1;
    t * 2.0 >= fdist(line.0, line.1)
}

/// 顺着这道墙挪 `step`（`plus` 往 b 头），再往 `p` 这一侧、离开墙的方向挪 `off` 个 `step`；不出地图。
pub fn step_off(line: &(F2, F2), p: (u64, u64), plus: bool, step: u64, off: u64) -> (u64, u64) {
    let d = unit(line.0, line.1);
    let (px, py) = (p.0 as f64, p.1 as f64);
    let cross = (px - line.0 .0) * d.1 - (py - line.0 .1) * d.0;
    let n = if cross > 0.0 { (d.1, -d.0) } else { (-d.1, d.0) };
    let (sg, k) = (if plus { 1.0 } else { -1.0 }, step as f64 * off as f64);
    let x = px + sg * d.0 * step as f64 + n.0 * k;
    let y = py + sg * d.1 * step as f64 + n.1 * k;
    let clampf = |v: f64| v.round().clamp(0.0, (MAP - 1) as f64) as u64;
    (clampf(x), clampf(y))
}

/// 被挡住的单位这一 tick 在哪（0.2.2）：`held` 是 [`hold`] 把它放回的地方，`tried` 是它想走到的地方（在墙里），`step` 是它这一
/// tick 想走多远。墙不是引擎的地形，单位的寻路不知道它，正对着墙走的单位只剩「顺着墙的那一半」= 0，每 tick 被放回原处：
/// 11-03 夜里的日志，墙立 300 tick，小兵在同一个坐标站了 281 tick，布隆 227、洛 212、赵信 205、永恩 202（队友也一样）。
/// 现在挡了 `STALL_T` tick 没挪出 `STALL_MOVE`，就每 tick 顺着整道墙（[`line_of`]，0.2.3：台阶状的横墙算一道）往近的那头挪，
/// 挪不过去就先往墙外错开最多 `OFF_STEPS` 步再挪、再不行换另一头；挪过墙头它自己就绕过去了；挪着的时候不再等。
pub fn unstick(walls: &[Wall], s: &mut Stall, held: (u64, u64), tried: (u64, u64), r: u64, step: u64) -> (u64, u64) {
    let Some(w) = walls.iter().find(|w| inside(w, tried, r)) else { return held };
    let line = line_of(walls, w);
    if s.dir.is_none() {
        if s.ticks == 0 || held.0.abs_diff(s.at.0).max(held.1.abs_diff(s.at.1)) > STALL_MOVE {
            // getting somewhere along the wall on its own (or the first tick held): the count starts here
            *s = Stall { at: held, ticks: 0, dir: None };
        }
        s.ticks += 1;
        if s.ticks < STALL_T {
            return held;
        }
        s.dir = Some(nearer_end(&line, held));
    }
    let step = step.clamp(STEP_MIN, STEP_MAX);
    let d = s.dir.unwrap_or(true);
    for plus in [d, !d] {
        for off in 0..=OFF_STEPS {
            let q = step_off(&line, held, plus, step, off);
            if q != held && clear(walls, q, r) {
                s.dir = Some(plus);
                return q;
            }
        }
    }
    held
}

/// 出口找几层（从一块墙出来又进了另一块，再从那块出）。
pub const PUSH_DEPTH: usize = 3;

/// 单位在 `q`、压在墙 `w` 上时能从哪出去：竖墙只往她那一侧，横墙上下两边和两头。
fn exits(w: &Wall, q: (u64, u64), r: u64) -> Vec<(u64, u64)> {
    match w.side {
        Side::Upright { .. } => vec![push_out(w, q, r)],
        Side::Flat => {
            let (ey, ex) = (w.hh + r + 1, w.hw + r + 1);
            vec![(q.0, w.y.saturating_sub(ey)), (q.0, w.y + ey), (w.x.saturating_sub(ex), q.1), (w.x + ex, q.1)]
        }
    }
}

/// 推出所有墙：一段横墙往上推正好进了叠在上面的另一段、再推回来，照 `push_out` 一块块推会在两段之间来回（0.2.x，11-02 的
/// 日志：小兵、阿兹尔、她自己被这样每 tick 推一次，一面墙推了几千次）。这里在压着它的墙的出口里找离 `now` 最近的空地，出口
/// 还在别的墙里就从那块接着找，最多 `PUSH_DEPTH` 层；都不行就不推（None）。
pub fn push_clear(walls: &[Wall], now: (u64, u64), r: u64) -> Option<(u64, u64)> {
    let d2 = |q: (u64, u64)| (q.0 as f64 - now.0 as f64).powi(2) + (q.1 as f64 - now.1 as f64).powi(2);
    let mut frontier = vec![now];
    for _ in 0..PUSH_DEPTH {
        let mut best: Option<(u64, u64)> = None;
        let mut next = Vec::new();
        for &q in &frontier {
            for w in walls.iter().filter(|w| inside(w, q, r)) {
                for e in exits(w, q, r) {
                    if clear(walls, e, r) {
                        if best.is_none_or(|b| d2(e) < d2(b)) {
                            best = Some(e);
                        }
                    } else if !next.contains(&e) {
                        next.push(e);
                    }
                }
            }
        }
        if best.is_some() {
            return best;
        }
        next.truncate(64);
        frontier = next;
    }
    None
}

/// 横墙第 k 段算出来的墙心：从她脚下朝目标 k×`r_seg`（目标就在她脚下时朝右）。
pub fn stretch_at(p: &Params, from: (u64, u64), to: (u64, u64), k: usize) -> (u64, u64) {
    let (dx, dy) = (to.0 as f64 - from.0 as f64, to.1 as f64 - from.1 as f64);
    let len = (dx * dx + dy * dy).sqrt();
    let (ux, uy) = if len < 1.0 { (1.0, 0.0) } else { (dx / len, dy / len) };
    let d = (k as u64 * p.r_seg) as f64;
    ((from.0 as f64 + ux * d).max(0.0).round() as u64, (from.1 as f64 + uy * d).max(0.0).round() as u64)
}

/// 横墙第 k 段铺下的 tick（线从 `from` tick 起飞，每 tick 飞 `r_lay_speed`，铺下那 tick 区域才列出来）。
pub fn stretch_due(p: &Params, from: usize, k: usize) -> usize {
    from + (k as u64 * p.r_seg).div_ceil(p.r_lay_speed.max(1)) as usize + 1
}

fn near(a: (u64, u64), b: (u64, u64), d: u64) -> bool {
    a.0.abs_diff(b.0) <= d && a.1.abs_diff(b.1) <= d
}

/// 她新放出、停着不动的区域：这一 tick 和上一 tick 都在同一处，而且那里比铺墙前多了。
pub fn settled(base: &[(u64, u64)], prev: &[(u64, u64)], now: &[(u64, u64)]) -> Vec<(u64, u64)> {
    let count = |list: &[(u64, u64)], q: (u64, u64)| list.iter().filter(|&&o| near(o, q, SAME)).count();
    let mut out: Vec<(u64, u64)> = Vec::new();
    for &q in now {
        if count(prev, q) > 0 && count(now, q) > count(base, q) && !out.iter().any(|&o| near(o, q, SAME)) {
            out.push(q);
        }
    }
    out
}

/// 对区域：离算出来的墙心 `tol` 以内、还没被别的段用掉的里面最近的一个。
pub fn snap(pred: (u64, u64), found: &[(u64, u64)], taken: &[(u64, u64)], tol: u64) -> Option<(u64, u64)> {
    found
        .iter()
        .copied()
        .filter(|&q| near(q, pred, tol) && !taken.iter().any(|&t| near(t, q, SAME)))
        .min_by_key(|&q| q.0.abs_diff(pred.0).max(q.1.abs_diff(pred.1)))
}

// ===================== 被动 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 横墙还没铺下的一段：第几段、算出来的墙心、该铺下的 tick。
#[derive(Clone, Copy, Debug)]
struct Pending {
    k: usize,
    at: (u64, u64),
    due: usize,
}

#[derive(Clone, Default)]
struct Weave {
    p: Params,
    me: usize,
    had_wall_up: bool,
    had_lay_up: bool,
    /// 上一 tick 她的投射物在哪、铺横墙那一 tick 之前她的投射物在哪。
    prev_proj: Vec<(u64, u64)>,
    base: Vec<(u64, u64)>,
    pending: Vec<Pending>,
    /// 这次横墙已经对上的区域（别的段不再用）。
    taken: Vec<(u64, u64)>,
    walls: Vec<Wall>,
    /// 墙立着时每个单位上一 tick 的位置。
    last_pos: HashMap<usize, (u64, u64)>,
    /// 被挡住的单位（`unstick`）。
    stalls: HashMap<usize, Stall>,
    /// (单位, 墙心) -> 这块墙挡了它几 tick、其中顺着墙挪了几 tick、它是谁这边的；墙倒了每个单位记一行 HOLD。
    held: HashMap<(usize, (u64, u64)), Held>,
}

/// 一块墙挡一个单位的账（0.2.2：一个单位一块墙一行 HOLD，0.2.1 每 tick 一行——11-03 夜里 253 行、计数到 #10650）。
#[derive(Clone, Copy, Debug, Default)]
struct Held {
    ticks: usize,
    stepped: usize,
    side: &'static str,
}

impl Weave {
    /// 墙幔的目标：带 `aim` 的敌方英雄（不止一个就取离她近的）。
    fn target(&self, sim: &StableSim<'_>, me: (u64, u64), team: usize) -> Option<(usize, (u64, u64))> {
        let aim = sn("aim");
        (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| e.is_alive() && e.team() != team && matches!(e.kind(), Some(EntityKindV1::Champion)))
            .filter(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == aim))
            .map(|e| (e.id(), e.pos()))
            .min_by_key(|&(_, q)| q.0.abs_diff(me.0).max(q.1.abs_diff(me.1)))
    }

    fn watch(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let mine: Vec<(u64, u64)> = (0..sim.projectile_count())
            .filter_map(|i| sim.projectile_at(i))
            .filter(|q| q.caster_id == me && !q.is_end)
            .map(|q| (q.x, q.y))
            .collect();
        let (me_pos, team) = sim.get_entity(me).map_or(((0, 0), 0), |e| (e.pos(), e.team()));
        let p = self.p;

        let wall_up = has(sim, me, &sn("wall_up"));
        if wall_up && !self.had_wall_up {
            match self.target(sim, me_pos, team) {
                Some((t, at)) => {
                    let left = me_pos.0 < at.0;
                    self.walls.push(Wall::upright(&p, at, left, now + p.r_t + 1));
                    if let Some(k) = counted("upright") {
                        wlog(format!("{} UPRIGHT #{k}: the wall at ({}, {}) behind {}, she on its {} side, {} ticks",
                                     head(sim, me), at.0, at.1, who(sim, t), if left { "left" } else { "right" }, p.r_t));
                    }
                }
                None => {
                    if let Some(k) = counted("upright_lost") {
                        wlog(format!("{} UPRIGHT? #{k}: wall_up rose but no enemy champion carries aim", head(sim, me)));
                    }
                }
            }
        }
        self.had_wall_up = wall_up;

        let lay_up = has(sim, me, &sn("lay_up"));
        if lay_up && !self.had_lay_up {
            match self.target(sim, me_pos, team) {
                Some((t, at)) => {
                    self.base = self.prev_proj.clone();
                    self.taken.clear();
                    self.pending = (0..p.r_n)
                        .map(|k| Pending { k, at: stretch_at(&p, me_pos, at, k), due: stretch_due(&p, now, k) })
                        .collect();
                    if let Some(k) = counted("lay") {
                        wlog(format!("{} LAY #{k}: {} stretches from ({}, {}) toward {} at ({}, {})", head(sim, me),
                                     p.r_n, me_pos.0, me_pos.1, who(sim, t), at.0, at.1));
                    }
                }
                None => {
                    if let Some(k) = counted("lay_lost") {
                        wlog(format!("{} LAY? #{k}: lay_up rose but no enemy champion carries aim", head(sim, me)));
                    }
                }
            }
        }
        self.had_lay_up = lay_up;

        if !self.pending.is_empty() {
            let found = settled(&self.base, &self.prev_proj, &mine);
            let tol = p.r_lay_speed + 2000;
            let mut left = Vec::new();
            for s in std::mem::take(&mut self.pending) {
                let got = if now + 1 >= s.due { snap(s.at, &found, &self.taken, tol) } else { None };
                let at = match got {
                    Some(q) => {
                        self.taken.push(q);
                        Some((q, "zone"))
                    }
                    None if now >= s.due + LATE => Some((s.at, "worked out")),
                    None => None,
                };
                match at {
                    Some((q, how)) => {
                        self.walls.push(Wall::flat(&p, q, now + p.r_t));
                        if let Some(k) = counted("stretch") {
                            wlog(format!("{} STRETCH #{k}: {} at ({}, {}) ({how}; worked out ({}, {}), due t={})",
                                         head(sim, me), s.k, q.0, q.1, s.at.0, s.at.1, s.due));
                        }
                    }
                    None => left.push(s),
                }
            }
            self.pending = left;
        }
        self.prev_proj = mine;
    }

    /// 倒了的墙（墙心 `fallen`）挡过的每个单位记一行 HOLD：挡了几 tick、顺着墙挪了几 tick。
    fn report(&mut self, sim: &StableSim<'_>, fallen: &[(u64, u64)]) {
        let mut done: Vec<((usize, (u64, u64)), Held)> =
            self.held.iter().filter(|(k, _)| fallen.contains(&k.1)).map(|(k, h)| (*k, *h)).collect();
        done.sort_by_key(|(k, _)| *k);
        for ((id, at), h) in done {
            self.held.remove(&(id, at));
            if let Some(k) = counted("hold") {
                wlog(format!("{} HOLD #{k}: {} ({}) held {} ticks by the wall at ({}, {}){}", head(sim, self.me), who(sim, id),
                             h.side, h.ticks, at.0, at.1,
                             if h.stepped > 0 { format!(", stepped along it {} ticks", h.stepped) } else { String::new() }));
            }
        }
    }

    /// 墙立着时：每个单位进墙就放回去（她骑墙时不管她）。
    fn block(&mut self, sim: &mut StableSim<'_>, now: usize) {
        let fallen: Vec<(u64, u64)> = self.walls.iter().filter(|w| now >= w.until).map(|w| (w.x, w.y)).collect();
        if !fallen.is_empty() {
            self.report(sim, &fallen);
        }
        self.walls.retain(|w| now < w.until);
        if self.walls.is_empty() {
            self.last_pos.clear();
            self.stalls.clear();
            return;
        }
        let riding = has(sim, self.me, &sn("riding"));
        let team = sim.get_entity(self.me).map_or(usize::MAX, |e| e.team());
        let mut moves = Vec::new();
        let mut seen = HashMap::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() {
                continue;
            }
            match e.kind() {
                Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Summon) => {}
                _ => continue,
            }
            let id = e.id();
            let now_pos = e.pos();
            if riding && id == self.me {
                seen.insert(id, now_pos);
                continue;
            }
            let r = match e.radius() as u64 { 0 => BODY, r => r };
            let last = self.last_pos.get(&id).copied();
            let at = match hold(&self.walls, last, now_pos, r) {
                Some(q) => {
                    let held = last.is_some_and(|l| clear(&self.walls, l, r));
                    let q = if held {
                        // walking into the wall: held, and stepped along it after STALL_T ticks without getting anywhere
                        let step = last.map_or(0, |l| l.0.abs_diff(now_pos.0).max(l.1.abs_diff(now_pos.1)));
                        let to = unstick(&self.walls, self.stalls.entry(id).or_default(), q, now_pos, r, step);
                        if let Some(w) = self.walls.iter().find(|w| inside(w, now_pos, r)) {
                            let side = if id == self.me { "herself" } else if e.team() == team { "her ally" } else { "an enemy" };
                            let h = self.held.entry((id, (w.x, w.y))).or_insert(Held { side, ..Held::default() });
                            h.ticks += 1;
                            h.stepped += usize::from(to != q);
                        }
                        to
                    } else {
                        self.stalls.remove(&id);
                        q
                    };
                    moves.push((id, q, held));
                    q
                }
                None => {
                    self.stalls.remove(&id);
                    now_pos
                }
            };
            seen.insert(id, at);
        }
        for (id, (x, y), held) in moves {
            sim.entity_set_pos(id, x, y);
            // HOLD: one line a unit a wall when the wall falls (`report`)
            if !held {
                if let Some(k) = counted("push") {
                    wlog(format!("{} PUSH #{k}: {} kept out of the wall at ({x}, {y})", head(sim, self.me), who(sim, id)));
                }
            }
        }
        self.last_pos = seen;
    }
}

impl StablePassive for Weave {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.had_wall_up = false;
        self.had_lay_up = false;
        self.prev_proj.clear();
        self.pending.clear();
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Taliyah (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        if sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            self.watch(sim, me, now);
        } else {
            self.pending.clear();
        }
        self.block(sim, now);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Taliyah: Weaver's Wall as real terrain, the surf out of fights) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:wall"), Weave::default());
    view::install_once();
    host.log(LogLevel::Info, "league_taliyah loaded (Weaver's Wall as real terrain).");
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

    fn p() -> Params {
        Params::default()
    }

    #[test]
    fn params_from_the_kit() {
        let q = parse_params(r#"{"r_h":120000,"r_lay_speed":8000,"r_n":6,"r_seg":26000,"r_t":300,"r_w":12000}"#);
        assert_eq!(q, Params::default());
    }

    #[test]
    fn walking_into_the_upright_wall_keeps_only_the_step_along_it() {
        let w = [Wall::upright(&p(), (500000, 400000), true, 300)];
        // from the left, walking right and down: the step right taken back, the step down kept
        assert_eq!(hold(&w, Some((488000, 400000)), (491000, 401000), 6000), Some((488000, 401000)));
        // from the right the same
        assert_eq!(hold(&w, Some((512000, 410000)), (509000, 410000), 6000), Some((512000, 410000)));
        // past its end: free
        assert_eq!(hold(&w, Some((495000, 470000)), (500000, 470000), 6000), None);
    }

    #[test]
    fn walking_onto_the_flat_wall_keeps_only_the_step_along_it() {
        let w = [Wall::flat(&p(), (500000, 400000), 300)];
        // from below (smaller y), walking up and right: up taken back, right kept
        assert_eq!(hold(&w, Some((500000, 388000)), (502000, 391000), 6000), Some((502000, 388000)));
        // the two stretches side by side are one wall: walking along it from one to the next is free outside them
        let w2 = [Wall::flat(&p(), (500000, 400000), 300), Wall::flat(&p(), (526000, 400000), 300)];
        assert_eq!(hold(&w2, Some((512000, 388000)), (514000, 390000), 6000), Some((514000, 388000)));
    }

    #[test]
    fn standing_on_a_wall_when_it_rises_pushed_off() {
        // the upright wall: to her side, wherever they stood on it
        let w = [Wall::upright(&p(), (500000, 400000), true, 300)];
        assert_eq!(hold(&w, None, (503000, 400000), 6000), Some((500000 - 12001, 400000)));
        let w = [Wall::upright(&p(), (500000, 400000), false, 300)];
        assert_eq!(hold(&w, None, (498000, 400000), 6000), Some((500000 + 12001, 400000)));
        // a flat stretch: to the nearer side
        let w = [Wall::flat(&p(), (500000, 400000), 300)];
        assert_eq!(hold(&w, None, (510000, 398000), 6000), Some((510000, 400000 - 12001)));
        assert_eq!(hold(&w, None, (510000, 402000), 6000), Some((510000, 400000 + 12001)));
        // she jumped off the wall (her last spot on it too): pushed off the same way
        assert_eq!(hold(&w, Some((508000, 401000)), (510000, 401000), 6000), Some((510000, 412001)));
    }

    #[test]
    fn the_stretches_laid_toward_the_target() {
        let me = (300000, 400000);
        assert_eq!(stretch_at(&p(), me, (450000, 400000), 0), me);
        assert_eq!(stretch_at(&p(), me, (450000, 400000), 2), (352000, 400000));
        // toward the left and up a little: along that line
        let q = stretch_at(&p(), me, (200000, 400000 - 100000 * 3 / 4), 1);
        assert_eq!(q, (300000 - 20800, 400000 - 15600));
        // the target right on her: to the right
        assert_eq!(stretch_at(&p(), me, me, 1), (326000, 400000));
        // the k-th line flies k x r_seg at r_lay_speed a tick, its zone listed the tick after it stops
        assert_eq!(stretch_due(&p(), 100, 0), 101);
        assert_eq!(stretch_due(&p(), 100, 1), 105);
        assert_eq!(stretch_due(&p(), 100, 5), 118);
    }

    #[test]
    fn only_zones_that_stay_put_count_and_each_once() {
        let base = [(330000, 410000)];
        // a line flying (moved since last tick), an old mine field, a new zone that stayed, listed twice (two zones there)
        let prev = [(330000, 410000), (340000, 400000), (352400, 400000), (352400, 400000)];
        let now = [(330000, 410000), (348000, 400000), (352400, 400000), (352400, 400000)];
        assert_eq!(settled(&base, &prev, &now), vec![(352400, 400000)]);
        // the stretch worked out at 352000 takes it; a second stretch never takes the same one
        let found = settled(&base, &prev, &now);
        assert_eq!(snap((352000, 400000), &found, &[], 10000), Some((352400, 400000)));
        assert_eq!(snap((352000, 400000), &found, &[(352400, 400000)], 10000), None);
        // too far from where it should be
        assert_eq!(snap((378000, 400000), &found, &[], 10000), None);
    }

    #[test]
    fn a_unit_walking_straight_into_the_wall_is_stepped_round_its_near_end() {
        // 11-03 night logs: a minion held on one spot for 281 of the wall's 300 ticks, Braum 227, Rakan 212
        let w = [Wall::upright(&p(), (500000, 400000), true, 300)];
        let r = 6000;
        let mut s = Stall::default();
        let mut at = (488000, 410000);
        let mut still = 0;
        let mut free_at = None;
        for t in 0..400 {
            let tried = (at.0 + 400, at.1); // its own walk: straight right, into the wall
            let Some(q) = hold(&w, Some(at), tried, r) else {
                free_at = Some(t);
                break;
            };
            let to = unstick(&w, &mut s, q, tried, r, 400);
            still = if to == at { still + 1 } else { 0 };
            assert!(still < STALL_T, "held {still} ticks on {at:?}");
            assert!(clear(&w, to, r), "stepped into the wall at {to:?}");
            at = to;
        }
        // up (the nearer end) along the wall's face, then round its top on its own
        let t = free_at.expect("never got past the wall");
        assert!(at.1 >= 400000 + 60000 + r && at.0 == 488000, "{at:?}");
        assert!(t < STALL_T + (66000 - 10000) / 400 + 5, "{t} ticks");
    }

    #[test]
    fn the_step_turns_back_when_another_wall_is_in_the_way() {
        let p = p();
        // a flat piece just above her: the nearer end (up) is shut, down it goes
        let w = [Wall::upright(&p, (500000, 400000), true, 300), Wall::flat(&p, (480000, 422100), 300)];
        let r = 6000;
        let at = (488000, 410000);
        assert!(clear(&w, at, r));
        let mut s = Stall { at, ticks: STALL_T - 1, dir: None };
        let to = unstick(&w, &mut s, at, (488400, 410000), r, 400);
        assert_eq!((to, s.dir), ((488000, 409600), Some(false)));
        // boxed in both ways: it stays
        let mut s = Stall { at, ticks: 0, dir: Some(true) };
        let box_ = [w[0], w[1], Wall::flat(&p, (480000, 397900), 300)];
        assert!(clear(&box_, at, r));
        assert_eq!(unstick(&box_, &mut s, at, (488400, 410000), r, 400), at);
        // a slide along the wall on its own (it gets somewhere): no count
        let mut s = Stall::default();
        for k in 0..STALL_T * 2 {
            let here = (488000, 410000 + 1500 * k as u64);
            assert_eq!(unstick(&w[..1], &mut s, here, (488400, here.1), r, 1500), here);
        }
        // along the map's edge: never past it
        let f = Wall::flat(&p, (10000, 500000), 300);
        let fl = line_of(&[f], &f);
        assert_eq!(fl, ((-16000.0, 500000.0), (36000.0, 500000.0)));
        assert_eq!(step_off(&fl, (300, 488000), false, 2000, 0), (0, 488000));
        assert!(!nearer_end(&fl, (300, 488000)) && nearer_end(&line_of(&w, &w[0]), (488000, 410000)));
        // the upright wall's line runs up its face
        assert_eq!(line_of(&w, &w[0]), ((500000.0, 340000.0), (500000.0, 460000.0)));
    }

    #[test]
    fn a_unit_in_the_corner_of_a_stair_stepped_wall_is_walked_along_the_whole_wall() {
        // 11-04, m=2596: six pieces laid down a diagonal (STRETCH #1-#6); Taliyah herself held 235 of the wall's 300
        // ticks by piece 1, Orianna 173 by piece 5 - each piece's ends are shut by its neighbours
        let p = p();
        let c0 = (580730i64, 384800i64);
        let walls: Vec<Wall> = (0..6)
            .map(|k| Wall::flat(&p, ((c0.0 - 17495 * k) as u64, (c0.1 + 19234 * k) as u64), 999))
            .collect();
        // one wall: from half a piece past the first centre to half a piece past the last
        let line = line_of(&walls, &walls[1]);
        assert!(line.0 .0 < 493256.0 && line.1 .0 > 580730.0, "{line:?}");
        assert_eq!(line_of(&walls, &walls[4]), line);
        let r = 6000;
        // below and right of the wall, in the corner between pieces 1 and 2, walking up-left toward her
        let mut at = (566000u64, 417000u64);
        let side = |q: (u64, u64)| {
            let d = unit(line.0, line.1);
            ((q.0 as f64 - line.0 .0) * d.1 - (q.1 as f64 - line.0 .1) * d.0).signum()
        };
        let start_side = side(at);
        let mut s = Stall::default();
        let (mut still, mut longest, mut crossed) = (0, 0, None);
        for t in 0..300 {
            let tried = (at.0 - 600, at.1 - 600);
            let to = match hold(&walls, Some(at), tried, r) {
                Some(q) => unstick(&walls, &mut s, q, tried, r, 849),
                None => tried,
            };
            assert!(clear(&walls, to, r), "t={t}: in the wall at {to:?}");
            still = if to == at { still + 1 } else { 0 };
            longest = longest.max(still);
            at = to;
            if side(at) != start_side {
                crossed = Some(t);
                break;
            }
        }
        assert!(s.dir.is_some(), "never held long enough to be stepped");
        assert!(longest <= STALL_T, "stood {longest} ticks on one spot");
        assert!(crossed.is_some_and(|t| t < 300), "never got round the wall: at {at:?}");
    }

    #[test]
    fn a_unit_between_two_flat_pieces_ends_clear_of_both() {
        // 11-02, m=2343: three pieces of one lay 24688 apart down a steep line; minion #413 (radius 10000) was pushed up
        // out of one piece into the next and back every tick, between (483854, 474860) and (483854, 467546)
        let p = p();
        let walls = [Wall::flat(&p, (476669, 508235), 999), Wall::flat(&p, (484823, 483547), 999),
                     Wall::flat(&p, (492978, 458859), 999)];
        let r = 10000;
        for now in [(483854, 474860), (483854, 467546)] {
            let q = hold(&walls, None, now, r).expect("pushed");
            assert!(clear(&walls, q, r), "still inside a wall at {q:?} from {now:?}");
            // the next tick it stands clear: nothing more to do
            assert_eq!(hold(&walls, Some(q), q, r), None);
        }
    }
}
