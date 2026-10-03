//! 青钢影钩墙附加包 v4：E「钩索」钩墙、地图四边和防御塔。
//!
//! 数据层没有任何效果能「看见」墙，所以钩墙放在这个原生附加包里。`mod.override_info`
//! 把主包的青钢影换成 `override/` 里的副本，E 的出手交给本包：
//!
//! - 被动 `e`（挂在 `passive_skill2` 上，学会 E 后每 tick 跑）：E 好了、没被控、不在大招里（跃起和场地）时，
//!   每 `AUTO_EVERY` tick 判断一次——以少打多（`E_DNG_R` 内两个敌方英雄且 `E_ALLY_R` 内没有队友，
//!   或三打一）或血量低于 `LOW_HP` 且身边有敌人时逃跑，否则突进。顺便记下敌方英雄在哪，算出他们
//!   的速度。不用等 AI 先放一下 E 来武装；主包原来的武装脉冲也还在，调的是同一套效果。
//! - 能钩的：引擎的碰撞墙（30×30 格，见 [`maps`]；原画里的树林不算，墙就在树林里）、5v5 地图的四边
//!   （上下的石墙、左右的石堆，`MOBA_BOUNDS`）、射程内的防御塔（钩上后贴着塔；敌方的塔只在扑残血时钩）。
//! - `engage`（见 [`plan_engage`]）：从她脚下朝 64 个方向找射程内的第一面墙，配一个敌方英雄——照他现在的
//!   速度预判到 E2 那一刻，钩点离他 `DIVE_MIN`..`DIVE_PLAN`（最想要 `DIVE_IDEAL`）、中间没有墙，钩的
//!   方向朝着他那一侧、钩完离他更近；贴身的只钩身边的墙、跳上去再扑回来；站在他们塔下的（不残血）、
//!   身边三个敌人而我方没人的不扑。钩子飞过去咬在墙上，把她拉到墙边，挂 `CLING` tick 就扑（`e2`）：
//!   落地伤害周围敌人、眩晕被撞的英雄、给自己加攻速（数值同主包）。
//! - `escape`：钩一面远离敌人的墙（或我方的塔），拉过去后再沿着能走的方向冲开。
//!
//! 附近没有合适的墙或塔就不出手，E 不会白交。小兵、野怪、英雄、树林、草丛都不钩。当前对局是哪张图由
//! 场上单位判断：所有单位都不在墙里、墙又最多的那张。
//!
//! v3 → v4：v3 的钩点可以离目标 50000、目标可以在 85000 外，钩完拉过去（30~45 tick，英雄每 tick 走
//! 1000）人早走远了，只好挂在墙上不动；贴身的目标也会去钩 36000 外的墙再扑回来；v4 收紧了钩点、
//! 预判走位，E2 总会扑出去，加了地图四边。
//!
//! 她的 R 跃起中不出 E，E 进行中 R 开始了就停掉（会把半空的她拉走，大招落空）。R 的场地里只在要逃时出 E（v4.2）：
//! 主包的场地不再把她拉回中心，她走出去场地就结束，钩出去等于放掉正在打的目标，所以场地里不突进。
//!
//! 位移用引擎自己的强制位移（`ForceMove`，冲刺技能走的就是它，撞墙会停）；之后每 tick
//! 看一次，她身上没有强制位移却还没到时改为逐 tick 直接设位置，保证一定能到。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_camille_wall.log`
//! （游戏自己的 log.log 旁边），找不到时写在游戏目录。每次启动游戏重写，上一次的留在 .prev.log。

pub mod maps;

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_camille_wall";

// ===================== 数值 =====================

/// 地图格子边长（世界单位）。
pub const CELL: f64 = 32_000.0;

// 主包青钢影 E 的数值（主包生成脚本的 P 表），那边改了这里一起改。
/// E 的冷却（`e_cd` 标记的时长）。
const E_CD: usize = 720;
/// 钩索射程。
pub const E_RANGE: f64 = 60_000.0;
/// 出手动作 `skill2` 的时长，钩子在第 `E_FIRE` 帧飞出。
const E_DUR: u64 = 24;
const E_FIRE: usize = 8;
/// 钩子飞行速度。
const E_SPEED: f64 = 6_000.0;
/// 冲刺动作 `skill2_dash` 的时长。
const E_DASH_ANIM: u64 = 26;
/// 落地伤害半径、伤害、攻击力加成（%）、眩晕时长。
const E_RADIUS: f64 = 25_000.0;
const E_DMG: usize = 60;
const E_RATIO: usize = 70;
const E_STUN: u64 = 45;
/// 逃跑：这么近有敌方英雄才往外冲；冲 e2_speed × e_away_t 这么远。
pub const E_AWAY_R: f64 = 70_000.0;
pub const E_AWAY_LEN: f64 = 36_000.0;
/// 逃跑的钩点：离敌方英雄至少 `E_SAFE_R`，离她至少 `E_NEAR_R`。
pub const E_SAFE_R: f64 = 40_000.0;
pub const E_NEAR_R: f64 = 25_000.0;
/// 落地后的攻速（%）和时长。
const E_AS: i32 = 50;
const E_AS_T: usize = 300;

// 钩墙的手感（本包自己定的）。
/// 多远的敌方英雄会去钩墙突进（override 里 E 的武装距离也改成这个）。
pub const ENGAGE_R: f64 = 85_000.0;
/// 拉向墙的速度（每 tick）：60000 的钩约 0.3 秒。
const PULL_SPEED: f64 = 3_200.0;
/// 挂在墙上多少 tick 再扑出去。
pub const CLING: usize = 6;
/// E2：墙上够得着的敌方英雄（扑上去必中）的距离、扑的速度。够不着时朝目标冲 `E2_RANGE - CONTACT`。
pub const E2_RANGE: f64 = 50_000.0;
const E2_SPEED: f64 = 3_500.0;
/// 选钩点：钩点到目标（预判到 E2 那一刻的位置）最想要、最近、最远的距离。最远留出
/// `E2_RANGE - DIVE_PLAN` 的余量——英雄每 tick 走 1000，钩完到扑出去要 25~45 tick。
pub const DIVE_IDEAL: f64 = 27_000.0;
pub const DIVE_MIN: f64 = 10_000.0;
pub const DIVE_PLAN: f64 = 36_000.0;
/// 钩的方向和她看向目标的方向最多差多少（cos 75°）：钩完要离他更近，不往反方向钩。
pub const TURN_COS: f64 = 0.258_819;
/// 方向偏一点的代价（选钩点的分数，1 - cos 乘这个）。
const TURN_COST: f64 = 12_000.0;
/// 钩得远的代价（每单位）：钩得越远，拉过去越久，他越可能走开。
const HOOK_COST: f64 = 0.5;
/// 扑的方向和被拉过去的方向最多差多少（cos 110°）：再大就是掉头扑回来，看起来像反着放。
pub const PULL_DIVE_COS: f64 = -0.342_020;
/// 扑的时候拐弯的代价（选钩点的分数，1 - cos 乘这个）：一路往前的最好。
const PULL_DIVE_COST: f64 = 8_000.0;
/// 预判目标位置最多往前算多远。
pub const LEAD_CAP: f64 = 24_000.0;
/// 目标身边 `CROWD_R` 内有三个敌方英雄、自己人一个都不在时不扑（一个人扑进人堆）。
pub const CROWD_R: f64 = 35_000.0;
/// 5v5 地图四边（石墙、石堆）的墙面：x 和 y 的可走范围，外面当墙钩（原画量的：左右石堆、上下石墙）。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);
/// 离他中心这么远就算撞上（两个身体挨上）。
pub const CONTACT: f64 = 13_000.0;
/// 血量低于这个比例、`LOW_HP_NEAR` 内有敌方英雄时，突进改成逃跑。
pub const LOW_HP: f64 = 0.3;
pub const LOW_HP_NEAR: f64 = 50_000.0;
/// 比这近的墙不钩：拉不出样子。
pub const HOOK_MIN: f64 = 10_000.0;
const RAY_DIRS: usize = 64;
const RAY_STEP: f64 = 500.0;
/// 钩点离墙边留的距离。
pub const WALL_GAP: f64 = 500.0;
/// 钩子咬进墙里的深度（画面上钩在墙上，不是停在墙前的空地上）。
const BITE: f64 = 2_000.0;
/// 离钩点这么近就算到了。
const ARRIVE: f64 = 1_500.0;
/// 逃跑的第二段至少要能冲这么远。
pub const FLEE_MIN: f64 = 12_000.0;
/// 读不到塔的碰撞半径时用的值。
const TOWER_R: f64 = 15_000.0;
/// 被动每隔几 tick 判断一次要不要出 E（同主包脉冲）。
pub const AUTO_EVERY: usize = 6;
/// 以少打多：`E_DNG_R` 内两个敌方英雄且 `E_ALLY_R` 内没有队友，或三个对一个（同主包）。
pub const E_DNG_R: f64 = 45_000.0;
pub const E_ALLY_R: f64 = 40_000.0;
/// 离敌方塔这么近的目标不扑（他血量低于 `LOW_HP` 时照扑）。
pub const TOWER_DIVE_R: f64 = 50_000.0;

/// 主包青钢影的名字（标记、特效、音效都以它开头）。
fn camille(x: &str) -> String {
    format!("league_camille_{x}")
}

// 本包的标记（她身上的计时 buff，不带属性）。
/// 正在被拉向墙；时长是这段位移的最晚到达时间。
const PULL: &str = "league_camille_wall_pull";
/// 正在 E2（或逃跑的第二段）。
const DASH: &str = "league_camille_wall_dash";
/// 挂在墙上、等 E2 目标的窗口。
const WAIT: &str = "league_camille_wall_wait";
/// 宿主没挪她、改为逐 tick 设位置（只为日志里提一次）。
const MANUAL: &str = "league_camille_wall_manual";
/// 这次 E 冲着谁去（`league_camille_wall_tgt:<id>`），E2 先扑他。
const TARGET: &str = "league_camille_wall_tgt:";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_CAMILLE_WALL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_camille_wall.log");
        }
    }
    PathBuf::from("league_camille_wall.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
}

fn origin_label(sim: &StableSim<'_>) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let id = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("{kind} m={} s={}", id(o.match_id), id(o.set_index))
}

/// 一行日志的开头：哪场模拟、第几 tick、哪个卡密尔。
fn head(sim: &StableSim<'_>, caster: usize) -> String {
    format!("[{}] t={} camille#{caster}", origin_label(sim), sim.tick())
}

// ===================== 墙格子 =====================

/// 一张墙格子：`cells[y][x]`，非 0 为墙。`bounds`（x0, y0, x1, y1）外是地图四边画出来的墙
/// （5v5 的上下石墙、左右石堆）：只给钩子用，走路和冲刺的路线照旧只看格子。
#[derive(Clone, Debug, PartialEq)]
pub struct Grid {
    pub cells: Vec<Vec<i64>>,
    pub bounds: Option<(f64, f64, f64, f64)>,
}

impl Grid {
    /// 内置地图（`#` 为墙）。
    pub fn from_rows(rows: &[&str]) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| (c == '#') as i64).collect()).collect(), bounds: None }
    }

    pub fn builtin(mode: GameModeKindV1) -> Grid {
        Grid::from_rows(match mode {
            GameModeKindV1::Moba => &maps::MOBA,
            GameModeKindV1::SingleLane => &maps::SINGLE_LANE,
            GameModeKindV1::DeathMatch => &maps::DEATH_MATCH,
        })
        .with_edges(mode)
    }

    /// 5v5 地图加上四边的墙面（另两张图的四周本来就是格子墙）。
    pub fn with_edges(mut self, mode: GameModeKindV1) -> Grid {
        self.bounds = (mode == GameModeKindV1::Moba).then_some(MOBA_BOUNDS);
        self
    }

    /// 在地图四边的墙面外吗。
    pub fn beyond_edge(&self, x: f64, y: f64) -> bool {
        self.bounds.is_some_and(|(x0, y0, x1, y1)| x < x0 || y < y0 || x > x1 || y > y1)
    }

    /// 钩子能咬住吗：格子墙或四边的墙面。
    pub fn solid(&self, x: f64, y: f64) -> bool {
        self.is_wall(x, y) || self.beyond_edge(x, y)
    }

    /// 在地图范围内吗。
    pub fn on_map(&self, x: f64, y: f64) -> bool {
        let width = self.cells.iter().map(|r| r.len()).max().unwrap_or(0) as f64;
        x >= 0.0 && y >= 0.0 && x < width * CELL && y < self.cells.len() as f64 * CELL
    }

    /// 世界坐标落在墙里（或地图外）吗。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return true;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        match self.cells.get(cy).and_then(|row| row.get(cx)) {
            Some(v) => *v != 0,
            None => true,
        }
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|v| **v != 0).count()
    }
}

/// 解析 `[[0,1,...],[...],...]` 形状的整数二维数组（容忍空白、负数、小数取整）。
pub fn parse_int_grid(json: &str) -> Option<Grid> {
    let mut p = Parser { s: json.as_bytes(), i: 0 };
    p.ws();
    p.eat(b'[')?;
    let mut rows = Vec::new();
    loop {
        p.ws();
        if p.peek()? == b']' {
            break;
        }
        p.eat(b'[')?;
        let mut row = Vec::new();
        loop {
            p.ws();
            if p.peek()? == b']' {
                p.i += 1;
                break;
            }
            row.push(p.number()?);
            p.ws();
            if p.peek()? == b',' {
                p.i += 1;
            }
        }
        rows.push(row);
        p.ws();
        if p.peek()? == b',' {
            p.i += 1;
        }
    }
    (!rows.is_empty()).then_some(Grid { cells: rows, bounds: None })
}

struct Parser<'a> {
    s: &'a [u8],
    i: usize,
}

impl Parser<'_> {
    fn peek(&self) -> Option<u8> {
        self.s.get(self.i).copied()
    }
    fn ws(&mut self) {
        while matches!(self.peek(), Some(b' ' | b'\n' | b'\r' | b'\t')) {
            self.i += 1;
        }
    }
    fn eat(&mut self, c: u8) -> Option<()> {
        (self.peek()? == c).then(|| self.i += 1)
    }
    fn number(&mut self) -> Option<i64> {
        let start = self.i;
        while matches!(self.peek(), Some(b'-' | b'+' | b'.' | b'e' | b'E' | b'0'..=b'9')) {
            self.i += 1;
        }
        let text = std::str::from_utf8(&self.s[start..self.i]).ok()?;
        text.parse::<i64>().ok().or_else(|| text.parse::<f64>().ok().map(|f| f as i64))
    }
}

const MODES: [GameModeKindV1; 3] = [GameModeKindV1::Moba, GameModeKindV1::SingleLane, GameModeKindV1::DeathMatch];

/// 地图自定义钩子读到的墙格子，按模式存（同一模式的地图每局相同）。
static DOC_GRIDS: LazyLock<Mutex<HashMap<u32, Grid>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// 已经把格子画进日志的模式（每种只画一次）。
static DUMPED: LazyLock<Mutex<Vec<u32>>> = LazyLock::new(|| Mutex::new(Vec::new()));

const MODE_UNKNOWN: u32 = u32::MAX;

fn mode_name(code: u32) -> &'static str {
    match GameModeKindV1::from_code(code) {
        Some(GameModeKindV1::Moba) => "Moba",
        Some(GameModeKindV1::SingleLane) => "SingleLane",
        Some(GameModeKindV1::DeathMatch) => "DeathMatch",
        None => "unknown",
    }
}

/// 这种模式的墙：地图自定义钩子读到的优先，否则内置的；5v5 加上四边的墙面。
fn grid_for(mode: GameModeKindV1) -> Grid {
    DOC_GRIDS
        .lock()
        .unwrap_or_else(|e| e.into_inner())
        .get(&mode.code())
        .cloned()
        .map(|g| g.with_edges(mode))
        .unwrap_or_else(|| Grid::builtin(mode))
}

/// 当前对局的地图：站进墙里的单位最少的那张，一样少时取墙最多的（最「具体」的）。
pub fn pick_grid(points: &[(f64, f64)], grids: Vec<(GameModeKindV1, Grid)>) -> Option<(GameModeKindV1, Grid)> {
    grids
        .into_iter()
        .map(|(m, g)| (points.iter().filter(|p| g.is_wall(p.0, p.1)).count(), g.walls(), m, g))
        .min_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)))
        .map(|(_, _, m, g)| (m, g))
}

/// 截断过长的 JSON，日志只看个大概。
fn clip(s: &str, n: usize) -> String {
    if s.chars().count() <= n {
        s.to_string()
    } else {
        format!("{}…({} chars)", s.chars().take(n).collect::<String>(), s.chars().count())
    }
}

struct WallReader;
impl StableMapCustomizer for WallReader {
    fn customize(&self, mode: Option<GameModeKindV1>, doc: &mut StableJsonDoc<'_>) {
        let code = mode.map_or(MODE_UNKNOWN, |m| m.code());
        let raw = doc.get_json("walls");
        let grid = raw.as_deref().and_then(parse_int_grid);
        let first = {
            let mut dumped = DUMPED.lock().unwrap_or_else(|e| e.into_inner());
            !dumped.contains(&code) && {
                dumped.push(code);
                true
            }
        };
        if first {
            let mut out = format!("== map mode={} ==\n", mode_name(code));
            match &grid {
                Some(g) => {
                    let width = g.cells.iter().map(|r| r.len()).max().unwrap_or(0);
                    let same = mode.is_some_and(|m| g.cells == Grid::builtin(m).cells);
                    out += &format!(
                        "walls: {} rows x {} cols, {} wall cells, {} (# = wall, row y, column x)\n",
                        g.cells.len(),
                        width,
                        g.walls(),
                        if same { "same as built-in" } else { "DIFFERS from built-in: using this one" }
                    );
                    if !same {
                        for (r, row) in g.cells.iter().enumerate() {
                            let line: String = row.iter().map(|v| if *v != 0 { '#' } else { '.' }).collect();
                            out += &format!("{r:02} {line}\n");
                        }
                    }
                }
                None => {
                    out += &format!("walls: not a grid, using built-in; raw = {}\n", clip(raw.as_deref().unwrap_or("<none>"), 600))
                }
            }
            for key in ["nexus_pos", "fountains", "towers", "camps"] {
                let v = doc.get_json(key).unwrap_or_else(|| "<none>".into());
                out += &format!("{key} = {}\n", clip(&v, 600));
            }
            wlog(out);
        }
        if let (Some(m), Some(g)) = (mode, grid) {
            DOC_GRIDS.lock().unwrap_or_else(|e| e.into_inner()).insert(m.code(), g);
        }
    }
}

// ===================== 钩点 =====================

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 钩的是什么。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Surface {
    /// 墙（引擎的碰撞墙格子）。
    Wall,
    /// 地图四边画出来的墙（5v5 的上下石墙、左右石堆）。
    Edge,
    /// 一座塔（实体 id）。
    Tower(usize),
}

/// 一个钩点：她被拉到的位置（墙边退 `WALL_GAP`，或贴着塔）、离她的距离、钩的是什么、
/// 是不是敌方的塔（只在扑残血时钩）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Hit {
    pub x: f64,
    pub y: f64,
    pub dist: f64,
    pub surface: Surface,
    pub hostile: bool,
}

impl Hit {
    pub fn at(&self) -> (f64, f64) {
        (self.x, self.y)
    }
}

/// 一座能钩的塔：中心、碰撞半径、是不是敌方的。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Post {
    pub id: usize,
    pub x: f64,
    pub y: f64,
    pub r: f64,
    pub hostile: bool,
}

impl Post {
    pub fn at(&self) -> (f64, f64) {
        (self.x, self.y)
    }
}

/// 点 p 到线段 a-b 的距离。
fn segment_dist(p: (f64, f64), a: (f64, f64), b: (f64, f64)) -> f64 {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len2 = dx * dx + dy * dy;
    let t = if len2 > 0.0 { (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / len2).clamp(0.0, 1.0) } else { 0.0 };
    dist(p, (a.0 + dx * t, a.1 + dy * t))
}

/// 钩塔：塔的近边在射程内、贴着塔的位置离她不近于 `HOOK_MIN`、一路没有墙。`my_r` 是她的碰撞半径。
pub fn tower_hits(grid: &Grid, me: (f64, f64), my_r: f64, posts: &[Post]) -> Vec<Hit> {
    posts
        .iter()
        .filter_map(|p| {
            let d = dist(me, p.at());
            let reach = d - p.r - my_r;
            if d - p.r > E_RANGE || reach < HOOK_MIN {
                return None;
            }
            let end = (me.0 + (p.x - me.0) / d * reach, me.1 + (p.y - me.1) / d * reach);
            (!grid.is_wall(end.0, end.1) && path_free(grid, me, end)).then_some(Hit {
                x: end.0,
                y: end.1,
                dist: reach,
                surface: Surface::Tower(p.id),
                hostile: p.hostile,
            })
        })
        .collect()
}

/// 她能钩的所有点：墙和地图四边（被塔挡住的方向不算，那边钩的是塔）和塔。
pub fn hook_points(grid: &Grid, me: (f64, f64), my_r: f64, posts: &[Post]) -> Vec<Hit> {
    let mut hits: Vec<Hit> = wall_hits(grid, me.0, me.1, E_RANGE)
        .into_iter()
        .filter(|h| posts.iter().all(|p| segment_dist(p.at(), me, h.at()) > p.r))
        .collect();
    hits.extend(tower_hits(grid, me, my_r, posts));
    hits
}

/// 从 (x, y) 朝 `RAY_DIRS` 个方向扫，返回 `range` 内每个方向第一面墙前的钩点（不近于 `HOOK_MIN`）。
/// 5v5 地图的四边（`Grid::bounds` 外）也是墙；没有 `bounds` 的图出了地图边不算墙。起点本身在墙里时返回空。
pub fn wall_hits(grid: &Grid, x: f64, y: f64, range: f64) -> Vec<Hit> {
    let mut hits = Vec::new();
    if grid.is_wall(x, y) {
        return hits;
    }
    for k in 0..RAY_DIRS {
        let a = k as f64 * std::f64::consts::TAU / RAY_DIRS as f64;
        let (dx, dy) = (a.cos(), a.sin());
        let at = |d: f64| (x + dx * d, y + dy * d);
        let mut free = 0.0;
        let mut d = RAY_STEP;
        while d <= range + WALL_GAP {
            let (px, py) = at(d);
            if grid.bounds.is_none() && !grid.on_map(px, py) {
                break;
            }
            if grid.solid(px, py) {
                let surface = if grid.is_wall(px, py) { Surface::Wall } else { Surface::Edge };
                // 二分找墙边
                let (mut lo, mut hi) = (free, d);
                for _ in 0..12 {
                    let mid = (lo + hi) / 2.0;
                    if grid.solid(at(mid).0, at(mid).1) {
                        hi = mid;
                    } else {
                        lo = mid;
                    }
                }
                let hd = lo - WALL_GAP;
                if (HOOK_MIN..=range).contains(&hd) {
                    hits.push(Hit { x: at(hd).0, y: at(hd).1, dist: hd, surface, hostile: false });
                }
                break;
            }
            free = d;
            d += RAY_STEP;
        }
    }
    hits
}

/// a 到 b 的直线上没有墙吗（每 1000 取一点；只看格子墙，贴着地图边的人照样扑得到）。
pub fn path_free(grid: &Grid, a: (f64, f64), b: (f64, f64)) -> bool {
    let n = (dist(a, b) / 1000.0).ceil().max(1.0) as usize;
    (0..=n).all(|i| {
        let f = i as f64 / n as f64;
        !grid.is_wall(a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f)
    })
}

/// 从 `from` 朝单位方向 `dir` 最多能冲多远（不超过 `max`，墙和地图四边前留 `WALL_GAP`）。
pub fn free_run(grid: &Grid, from: (f64, f64), dir: (f64, f64), max: f64) -> f64 {
    let mut d = RAY_STEP;
    while d <= max {
        if grid.solid(from.0 + dir.0 * d, from.1 + dir.1 * d) {
            return (d - RAY_STEP - WALL_GAP).max(0.0);
        }
        d += RAY_STEP;
    }
    max
}

/// 一个敌方英雄：位置、每 tick 的速度（被动看到的，没有时为 0）、是不是站在他们自己的塔下、残血吗。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub x: f64,
    pub y: f64,
    pub vx: f64,
    pub vy: f64,
    pub guarded: bool,
    pub low: bool,
}

impl Foe {
    pub fn at(&self) -> (f64, f64) {
        (self.x, self.y)
    }

    /// `ticks` 后他大概在哪：照现在的速度走，最多往前算 `LEAD_CAP`。
    pub fn lead(&self, ticks: f64) -> (f64, f64) {
        let (mut dx, mut dy) = (self.vx * ticks, self.vy * ticks);
        let len = (dx * dx + dy * dy).sqrt();
        if len > LEAD_CAP {
            (dx, dy) = (dx * LEAD_CAP / len, dy * LEAD_CAP / len);
        }
        (self.x + dx, self.y + dy)
    }
}

fn nearest(p: (f64, f64), foes: &[Foe]) -> f64 {
    foes.iter().map(|f| dist(p, f.at())).fold(f64::INFINITY, f64::min)
}

/// `f` 在 `ticks` 后大概在哪（同 [`Foe::lead`]），走到墙前就停。
pub fn lead_on(grid: &Grid, f: &Foe, ticks: f64) -> (f64, f64) {
    let p = f.lead(ticks);
    let n = (dist(f.at(), p) / 1000.0).ceil() as usize;
    let mut last = f.at();
    for i in 1..=n {
        let t = i as f64 / n as f64;
        let q = (f.x + (p.0 - f.x) * t, f.y + (p.1 - f.y) * t);
        if grid.is_wall(q.0, q.1) {
            return last;
        }
        last = q;
    }
    p
}

/// 从决定出 E 到 E2 扑出去要多少 tick：出手到钩子飞出、钩子飞、拉过去、挂一下。
pub fn ticks_to_e2(hook_dist: f64) -> f64 {
    E_FIRE as f64 + hook_dist / E_SPEED + hook_dist / PULL_SPEED + CLING as f64
}

/// 突进：`ENGAGE_R` 内、不在他们塔下的敌方英雄里挑一个，配一个钩点——
/// - 钩点到他（照他现在的速度预判到 E2 那一刻）`DIVE_MIN`..`DIVE_PLAN`，扑过去的路上没有墙；
/// - 钩的方向朝着他那一侧（和看向他的方向差不过 75°），钩完离他比现在近；
/// - 扑的方向和被拉过去的方向差不过 110°（`PULL_DIVE_COS`）：一路往前或拐个弯扑上去，不越过他钩到他
///   身后再掉头扑回来，也不往身后的墙跳再扑回来（贴身时就不用 E，直接打）；
/// - 敌方的塔只在他残血时钩；他身边 `CROWD_R` 内有三个敌方英雄、`friends`（她的队友）一个都不在附近时不扑。
///
/// 分数越小越好：扑的距离接近 `DIVE_IDEAL`、钩得近、钩的方向正、扑的时候拐得少，残血的优先。
pub fn plan_engage(grid: &Grid, hits: &[Hit], me: (f64, f64), foes: &[Foe], friends: &[(f64, f64)]) -> Option<(Hit, usize)> {
    let mut best: Option<(f64, Hit, usize)> = None;
    for f in foes.iter().filter(|f| !f.guarded && dist(me, f.at()) <= ENGAGE_R) {
        let crowd = foes.iter().filter(|o| dist(o.at(), f.at()) <= CROWD_R).count();
        if crowd >= 3 && friends.iter().all(|a| dist(*a, f.at()) > CROWD_R + 15_000.0) {
            continue;
        }
        for h in hits.iter().filter(|h| !h.hostile || f.low) {
            let p = lead_on(grid, f, ticks_to_e2(h.dist));
            let d = dist(h.at(), p);
            if !(DIVE_MIN..=DIVE_PLAN).contains(&d) || !path_free(grid, h.at(), p) {
                continue;
            }
            let to_him = dist(me, p).max(1.0);
            let cos = ((h.x - me.0) * (p.0 - me.0) + (h.y - me.1) * (p.1 - me.1)) / (h.dist.max(1.0) * to_him);
            let turn = ((h.x - me.0) * (p.0 - h.x) + (h.y - me.1) * (p.1 - h.y)) / (h.dist.max(1.0) * d.max(1.0));
            if cos < TURN_COS || d >= to_him || turn < PULL_DIVE_COS {
                continue;
            }
            let score = (d - DIVE_IDEAL).abs()
                + HOOK_COST * h.dist
                + TURN_COST * (1.0 - cos)
                + PULL_DIVE_COST * (1.0 - turn)
                - if f.low { 8_000.0 } else { 0.0 };
            if best.is_none_or(|b| score < b.0) {
                best = Some((score, *h, f.id));
            }
        }
    }
    best.map(|(_, h, id)| (h, id))
}

/// 逃跑：离她至少 `E_NEAR_R`、离敌方英雄至少 `E_SAFE_R`、比她现在离敌人远的钩点里，离敌人最远的
/// （不钩敌方的塔）。
pub fn plan_escape(hits: &[Hit], me: (f64, f64), foes: &[Foe]) -> Option<Hit> {
    let now = nearest(me, foes);
    hits.iter()
        .copied()
        .filter(|h| h.dist >= E_NEAR_R && !h.hostile)
        .map(|h| (nearest(h.at(), foes), h))
        .filter(|(m, _)| *m >= E_SAFE_R && *m > now)
        .max_by(|a, b| a.0.total_cmp(&b.0))
        .map(|(_, h)| h)
}

/// 逃跑的第二段：`E_AWAY_R` 内有敌方英雄时，朝能冲开（至少 `FLEE_MIN`）且终点离敌人最远的方向冲。
pub fn plan_flee(grid: &Grid, me: (f64, f64), foes: &[Foe]) -> Option<(f64, f64)> {
    let near: Vec<Foe> = foes.iter().copied().filter(|f| dist(me, f.at()) <= E_AWAY_R).collect();
    if near.is_empty() {
        return None;
    }
    let now = nearest(me, &near);
    (0..32)
        .filter_map(|k| {
            let a = k as f64 * std::f64::consts::TAU / 32.0;
            let dir = (a.cos(), a.sin());
            let run = free_run(grid, me, dir, E_AWAY_LEN);
            (run >= FLEE_MIN).then(|| (me.0 + dir.0 * run, me.1 + dir.1 * run))
        })
        .map(|end| (nearest(end, &near), end))
        .filter(|(m, _)| *m > now + 5_000.0)
        .max_by(|a, b| a.0.total_cmp(&b.0))
        .map(|(_, end)| end)
}

// ===================== 模拟里的小工具 =====================

/// 场上一个单位的快照。
struct Unit {
    id: usize,
    at: (f64, f64),
    team: usize,
    champion: bool,
    tower: bool,
    alive: bool,
    targetable: bool,
    radius: f64,
    hp: f64,
}

fn units(sim: &StableSim<'_>) -> Vec<Unit> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .map(|e| {
            let (x, y) = e.pos();
            Unit {
                id: e.id(),
                at: (x as f64, y as f64),
                team: e.team(),
                champion: e.is_champion(),
                tower: e.is_tower(),
                alive: e.is_alive(),
                targetable: e.is_targetable(),
                radius: e.radius() as f64,
                hp: share(e.hp()),
            }
        })
        .collect()
}

/// 能钩的塔：活着的，敌我都算（敌方的标出来）。读不到碰撞半径时按 `TOWER_R`。
fn posts_of(us: &[Unit], team: usize) -> Vec<Post> {
    us.iter()
        .filter(|u| u.tower && u.alive)
        .map(|u| Post {
            id: u.id,
            x: u.at.0,
            y: u.at.1,
            r: if u.radius > 0.0 { u.radius } else { TOWER_R },
            hostile: u.team != team,
        })
        .collect()
}

/// 她的碰撞半径（读不到时按英雄的 10000）。
fn my_radius(sim: &StableSim<'_>, id: usize) -> f64 {
    sim.get_entity(id).map(|e| e.radius() as f64).filter(|r| *r > 0.0).unwrap_or(10_000.0)
}

/// 她的血量比例（读不到时当满血）。
fn hp_share(sim: &StableSim<'_>, id: usize) -> f64 {
    sim.get_entity(id).map_or(1.0, |e| share(e.hp()))
}

/// (当前, 最大) 血量的比例；读不到最大值时当满血。
fn share((now, max): (usize, usize)) -> f64 {
    if max > 0 {
        now as f64 / max as f64
    } else {
        1.0
    }
}

/// 每 tick 的速度（被动量的），按实体 id。
type Velocities = HashMap<usize, (f64, f64)>;

/// 活着、能选中的敌方英雄。站在他们自己活着的塔 `TOWER_DIVE_R` 内、血量又不低的算塔下（不扑）。
fn foes_of(us: &[Unit], team: usize, vel: &Velocities) -> Vec<Foe> {
    us.iter()
        .filter(|u| u.champion && u.alive && u.targetable && u.team != team)
        .map(|u| {
            let low = u.hp <= LOW_HP;
            let guarded =
                !low && us.iter().any(|t| t.tower && t.alive && t.team == u.team && dist(t.at, u.at) <= TOWER_DIVE_R);
            let (vx, vy) = vel.get(&u.id).copied().unwrap_or_default();
            Foe { id: u.id, x: u.at.0, y: u.at.1, vx, vy, guarded, low }
        })
        .collect()
}

/// 她的队友（活着的英雄，不含她）。
fn friends_of(us: &[Unit], team: usize, me: usize) -> Vec<(f64, f64)> {
    us.iter().filter(|u| u.champion && u.alive && u.team == team && u.id != me).map(|u| u.at).collect()
}

/// 这次 E 冲着谁去（`decide` 记在她身上的标记）。
fn planned_target(sim: &StableSim<'_>, id: usize) -> Option<usize> {
    let e = sim.get_entity(id)?;
    (0..e.buff_count())
        .filter_map(|i| e.buff_at(i))
        .find_map(|b| b.name().strip_prefix(TARGET).and_then(|t| t.parse::<usize>().ok()))
}

/// 这场对局的墙（按场上活着的单位判断是哪张图）。
fn current_grid(us: &[Unit]) -> Option<(GameModeKindV1, Grid)> {
    let points: Vec<(f64, f64)> = us.iter().filter(|u| u.alive).map(|u| u.at).collect();
    pick_grid(&points, MODES.iter().map(|m| (*m, grid_for(*m))).collect())
}

fn alive(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    let e = sim.get_entity(id)?;
    e.is_alive().then(|| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id)
        .is_some_and(|e| (0..e.buff_count()).any(|i| e.buff_at(i).is_some_and(|b| b.name() == name)))
}

/// 她的 R 在跃起中（主包的 `r_leap`，施放到落地）：E 会把半空的她拉走，大招落空。
fn in_ult(sim: &StableSim<'_>, id: usize) -> bool {
    has_buff(sim, id, &camille("r_leap"))
}

/// 她的 R 场地还在（主包的 `r_on`）：她走出去场地就结束，所以场地里不突进，只在要逃时出 E。
fn in_arena(sim: &StableSim<'_>, id: usize) -> bool {
    has_buff(sim, id, &camille("r_on"))
}

/// R 开始了：停掉正在进行的 E（拉人、挂墙、扑），不再排下一 tick。
fn stop_for_ult(sim: &mut StableSim<'_>, caster: usize) -> bool {
    if !in_ult(sim, caster) {
        return false;
    }
    for flag in [PULL, DASH, WAIT] {
        sim.entity_remove_buff(caster, flag);
    }
    wlog(format!("{} E stopped: her R started", head(sim, caster)));
    true
}

fn has_cc(sim: &StableSim<'_>, id: usize, kinds: &[CcKindV1]) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
    })
}

/// 打断出手和钩索的控制。
const HARD_CC: [CcKindV1; 6] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];
/// 不能出 E 的状态：硬控、沉默、禁位移技能、正被击退。
const NO_CAST: [CcKindV1; 9] = [
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

fn timed(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

/// 播动作（数据层 CasterAnimation 同款：带名字的 Animation 控制）。
fn animate(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: u64) {
    let mut cc = CcV1::of_kind(CcKindV1::Animation, ticks);
    cc.set_name(name);
    sim.apply_cc(id, &cc);
}

/// 强制位移到 `to`，正好走到（速度取整到每 tick 一样长）；返回 tick 数。
fn force_move(sim: &mut StableSim<'_>, id: usize, from: (f64, f64), to: (f64, f64), speed: f64) -> usize {
    let d = dist(from, to);
    if d < 1.0 {
        return 0;
    }
    let ticks = (d / speed).ceil().max(1.0);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (to.0 - from.0).round() as i64;
    cc.dy = (to.1 - from.1).round() as i64;
    cc.speed = (d / ticks).ceil() as u64;
    sim.apply_cc(id, &cc);
    ticks as usize
}

/// 宿主没挪她时自己走一步（不进碰撞墙）；走不动返回 false。
fn step_toward(sim: &mut StableSim<'_>, id: usize, here: (f64, f64), to: (f64, f64), speed: f64, stop: f64) -> bool {
    let d = dist(here, to);
    if d <= stop + 1.0 {
        return false;
    }
    let s = speed.min(d - stop);
    let next = (here.0 + (to.0 - here.0) / d * s, here.1 + (to.1 - here.1) / d * s);
    let us = units(sim);
    if current_grid(&us).is_some_and(|(_, g)| g.is_wall(next.0, next.1)) {
        return false;
    }
    if !has_buff(sim, id, MANUAL) {
        timed(sim, id, MANUAL, 180);
        wlog(format!("{} host did not move her (no ForceMove on her): stepping with entity_set_pos", head(sim, id)));
    }
    sim.entity_set_pos(id, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64)
}

fn sfx(sim: &mut StableSim<'_>, name: &str, caster: usize) {
    sim.play_sfx(&camille(name), caster, &InputTargetV1::target(caster));
}

fn view(sim: &mut StableSim<'_>, name: &str, caster: usize, on: usize) {
    sim.play_view_effect(&camille(name), caster, &InputTargetV1::target(on), 0, 0, 0);
}

fn pos_input(p: (f64, f64)) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

fn input_pos(input: &InputTargetV1) -> Option<(f64, f64)> {
    (input.kind == InputTargetKindV1::Pos.code()).then_some((input.x as f64, input.y as f64))
}

fn queue(sim: &mut StableSim<'_>, step: &str, caster: usize, input: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{step}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
}

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    let name = sim.get_entity(id).and_then(|e| e.name()).unwrap_or_default();
    format!("#{id} {name}")
}

// ===================== E 的各段 =====================

/// 没找到钩点的次数（日志里每 200 次报一次）。
static MISSES: AtomicUsize = AtomicUsize::new(0);

/// 脉冲决定出 E（突进或逃跑）：找钩点，找到就出手。血少又有敌人在身边时，突进改成逃跑。
/// `vel`：被动量的敌方英雄速度（数据层的脉冲调用时没有，当他们站着不动）。
fn decide(sim: &mut StableSim<'_>, caster: usize, escape: bool, vel: &Velocities) {
    let Some(here) = alive(sim, caster) else { return };
    let busy = ["e_cd", "e_got"].iter().any(|f| has_buff(sim, caster, &camille(f))) || in_ult(sim, caster);
    if busy || has_cc(sim, caster, &NO_CAST) {
        return;
    }
    let us = units(sim);
    let Some((mode, grid)) = current_grid(&us) else { return };
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let foes = foes_of(&us, team, vel);
    let hp = hp_share(sim, caster);
    let low = !escape && hp <= LOW_HP && nearest(here, &foes) <= LOW_HP_NEAR;
    let escape = escape || low;
    if !escape && in_arena(sim, caster) {
        return;
    }
    let hits = hook_points(&grid, here, my_radius(sim, caster), &posts_of(&us, team));
    let plan = if escape {
        plan_escape(&hits, here, &foes).map(|h| (h, None))
    } else {
        plan_engage(&grid, &hits, here, &foes, &friends_of(&us, team, caster)).map(|(h, id)| (h, Some(id)))
    };
    let Some((hook, target)) = plan else {
        let n = MISSES.fetch_add(1, Ordering::Relaxed) + 1;
        if n % 200 == 1 {
            wlog(format!(
                "{} {} at {}: nothing to hook ({n} misses so far, all sims)",
                head(sim, caster),
                if escape { "escape" } else { "engage" },
                pt(here)
            ));
        }
        return;
    };

    // E 出手：同主包 fire()——冷却、出手动作，第 E_FIRE 帧钩子飞出
    timed(sim, caster, &camille("e_got"), 30);
    timed(sim, caster, &camille("e_cd"), E_CD);
    sim.entity_remove_buff(caster, &camille("e_armed"));
    if escape {
        timed(sim, caster, &camille("e_fled"), 60);
    }
    animate(sim, caster, "skill2", E_DUR);
    sfx(sim, "e_cast", caster);
    queue(sim, if escape { "throw_escape" } else { "throw" }, caster, pos_input(hook.at()), E_FIRE);
    if let Some(t) = target {
        timed(sim, caster, &format!("{TARGET}{t}"), ticks_to_e2(hook.dist) as usize + 20);
    }
    let aim = match target.and_then(|t| foes.iter().find(|f| f.id == t)) {
        Some(f) => {
            let p = lead_on(&grid, f, ticks_to_e2(hook.dist));
            format!(
                " target {} at {} ({:.0} away, {:.0} from the hook; expected at {} at E2, {:.0} from the hook)",
                who(sim, f.id),
                pt(f.at()),
                dist(here, f.at()),
                dist(hook.at(), f.at()),
                pt(p),
                dist(hook.at(), p)
            )
        }
        None => format!(" nearest enemy champion {:.0} -> {:.0}", nearest(here, &foes), nearest(hook.at(), &foes)),
    };
    let what = match hook.surface {
        Surface::Wall => "wall".to_string(),
        Surface::Edge => "map edge".to_string(),
        Surface::Tower(t) => format!("{}tower {}", if hook.hostile { "enemy " } else { "" }, who(sim, t)),
    };
    wlog(format!(
        "{} {}{} map={} from {} hook {what} -> {} ({:.0} away){aim}",
        head(sim, caster),
        if escape { "ESCAPE" } else { "ENGAGE" },
        if low { format!(" (hp {:.0}%)", hp * 100.0) } else { String::new() },
        mode_name(mode.code()),
        pt(here),
        pt(hook.at()),
        hook.dist
    ));
}

/// 第 E_FIRE 帧：钩子飞向墙。
fn throw(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1, escape: bool) {
    let (Some(hook), Some(here)) = (input_pos(&input), alive(sim, caster)) else { return };
    if in_ult(sim, caster) || has_cc(sim, caster, &HARD_CC) {
        wlog(format!("{} hook interrupted before the throw", head(sim, caster)));
        return;
    }
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    // 钩子咬进墙里（钩点再往前 WALL_GAP + BITE），或落在塔身上（钩点是她贴着塔的位置，再往前她的半径）
    let d = dist(here, hook).max(1.0);
    let dir = ((hook.0 - here.0) / d, (hook.1 - here.1) / d);
    let us = units(sim);
    let ahead = (hook.0 + dir.0 * (WALL_GAP + 300.0), hook.1 + dir.1 * (WALL_GAP + 300.0));
    let at_wall = current_grid(&us).is_some_and(|(_, g)| g.solid(ahead.0, ahead.1));
    let reach = if at_wall { WALL_GAP + BITE } else { my_radius(sim, caster) };
    let tip = (hook.0 + dir.0 * reach, hook.1 + dir.1 * reach);
    let spec = ProjectileSpawnV1 {
        caster_id: caster,
        team,
        x: here.0.round() as u64,
        y: here.1.round() as u64,
        radius: 1_000,
        speed: E_SPEED as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: tip.0.round().max(0.0) as u64,
        target_y: tip.1.round().max(0.0) as u64,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    if !sim.spawn_projectile(&camille("e_hook"), &format!("{ID}:noop"), &spec) {
        wlog(format!("{} spawn_projectile(e_hook) refused", head(sim, caster)));
    }
    let flight = (dist(here, tip) / E_SPEED).ceil() as usize;
    queue(sim, if escape { "pull_escape" } else { "pull" }, caster, input, flight);
}

/// 钩子钩上墙：把她拉过去。
fn pull(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1, escape: bool) {
    let (Some(hook), Some(here)) = (input_pos(&input), alive(sim, caster)) else { return };
    if in_ult(sim, caster) || has_cc(sim, caster, &HARD_CC) {
        wlog(format!("{} hook interrupted before the pull", head(sim, caster)));
        return;
    }
    animate(sim, caster, "skill2_dash", E_DASH_ANIM);
    sfx(sim, "e_pull", caster);
    let ticks = force_move(sim, caster, here, hook, PULL_SPEED);
    timed(sim, caster, PULL, ticks + 6);
    queue(sim, if escape { "watch_escape" } else { "watch" }, caster, input, 1);
}

/// 拉向墙的每一 tick：到了就挂在墙上，`CLING` tick 后接第二段。
fn watch(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1, escape: bool) {
    let (Some(hook), Some(here)) = (input_pos(&input), alive(sim, caster)) else { return };
    if stop_for_ult(sim, caster) {
        return;
    }
    let left = dist(here, hook);
    if left <= ARRIVE || !has_buff(sim, caster, PULL) {
        sim.entity_remove_buff(caster, PULL);
        wlog(format!("{} at the wall {} ({left:.0} short of the hook)", head(sim, caster), pt(here)));
        if escape {
            flee(sim, caster);
        } else {
            timed(sim, caster, WAIT, CLING + 2);
            queue(sim, "e2", caster, InputTargetV1::NONE, CLING);
        }
        return;
    }
    if !has_cc(sim, caster, &[CcKindV1::ForceMove]) && !step_toward(sim, caster, here, hook, PULL_SPEED, 0.0) {
        sim.entity_remove_buff(caster, PULL);
    }
    queue(sim, if escape { "watch_escape" } else { "watch" }, caster, input, 1);
}

/// E2：一挂完就从墙上扑出去，不在墙上干等——扑这次 E 冲着的那个人（够不着就朝他扑 `E2_RANGE - CONTACT`，
/// 追上去，撞到人才眩晕）；他死了（或中间隔着墙）才改扑 `E2_RANGE` 内最近的敌方英雄——不为了换人掉头扑向身后。
/// 中间有墙的不扑；场上没有能扑的敌方英雄（或她被控住了）才从墙上落下。
fn e2(sim: &mut StableSim<'_>, caster: usize) {
    let Some(here) = alive(sim, caster) else { return };
    if stop_for_ult(sim, caster) {
        return;
    }
    sim.entity_remove_buff(caster, WAIT);
    if has_cc(sim, caster, &HARD_CC) {
        wlog(format!("{} E2: controlled on the wall, no dive", head(sim, caster)));
        return;
    }
    let us = units(sim);
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let grid = current_grid(&us).map(|(_, g)| g);
    let planned = planned_target(sim, caster);
    let foes = foes_of(&us, team, &Velocities::new());
    let clear: Vec<Foe> = foes.into_iter().filter(|f| grid.as_ref().is_none_or(|g| path_free(g, here, f.at()))).collect();
    let in_reach = |f: &&Foe| dist(here, f.at()) <= E2_RANGE;
    let (target, why) = if let Some(f) = clear.iter().find(|f| Some(f.id) == planned) {
        (Some(*f), if dist(here, f.at()) <= E2_RANGE { "" } else { ", out of reach: dives after him" })
    } else if let Some(f) = clear.iter().filter(in_reach).min_by(|a, b| dist(here, a.at()).total_cmp(&dist(here, b.at()))) {
        (Some(*f), ", nearest in reach")
    } else {
        (None, "")
    };
    let Some(t) = target else {
        wlog(format!("{} E2: no enemy champion to dive at, drops off the wall", head(sim, caster)));
        return;
    };
    animate(sim, caster, "skill2_dash", E_DASH_ANIM);
    sfx(sim, "e_pull", caster);
    let d = dist(here, t.at());
    let dive = (d - CONTACT).clamp(0.0, E2_RANGE - CONTACT);
    let ticks = if dive > ARRIVE {
        let to = (here.0 + (t.x - here.0) / d * dive, here.1 + (t.y - here.1) / d * dive);
        force_move(sim, caster, here, to, E2_SPEED)
    } else {
        0
    };
    timed(sim, caster, DASH, ticks + 4);
    wlog(format!("{} E2 at {} ({d:.0} away, dive {dive:.0}{why})", head(sim, caster), who(sim, t.id)));
    queue(sim, "dash", caster, InputTargetV1::target(t.id), 1);
}

/// 逃跑的第二段：从墙边朝远离敌人的方向冲开。
fn flee(sim: &mut StableSim<'_>, caster: usize) {
    let Some(here) = alive(sim, caster) else { return };
    if stop_for_ult(sim, caster) {
        return;
    }
    let us = units(sim);
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let end = current_grid(&us).and_then(|(_, g)| plan_flee(&g, here, &foes_of(&us, team, &Velocities::new())));
    let Some(end) = end.filter(|_| !has_cc(sim, caster, &HARD_CC)) else {
        wlog(format!("{} escape: stays at the wall", head(sim, caster)));
        return;
    };
    animate(sim, caster, "skill2_dash", E_DASH_ANIM);
    sfx(sim, "e_pull", caster);
    let ticks = force_move(sim, caster, here, end, E2_SPEED);
    timed(sim, caster, DASH, ticks + 4);
    wlog(format!("{} escape dash to {}", head(sim, caster), pt(end)));
    queue(sim, "dash_escape", caster, pos_input(end), 1);
}

/// E2 / 逃跑第二段的每一 tick：到了就落地（突进）或结束（逃跑）。
fn dash(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1, escape: bool) {
    let Some(here) = alive(sim, caster) else { return };
    if stop_for_ult(sim, caster) {
        return;
    }
    let goal = if escape { input_pos(&input) } else { alive(sim, input.target_id) };
    let stop = if escape { ARRIVE } else { CONTACT + 2_000.0 };
    let Some(goal) = goal else {
        // 目标没了：原地落地（伤害身边的）
        sim.entity_remove_buff(caster, DASH);
        if !escape {
            land(sim, caster, input);
        }
        return;
    };
    if dist(here, goal) <= stop || !has_buff(sim, caster, DASH) {
        sim.entity_remove_buff(caster, DASH);
        if escape {
            wlog(format!("{} escape done at {}", head(sim, caster), pt(here)));
        } else {
            land(sim, caster, input);
        }
        return;
    }
    if !has_cc(sim, caster, &[CcKindV1::ForceMove]) && !step_toward(sim, caster, here, goal, E2_SPEED, stop - 2_000.0) {
        sim.entity_remove_buff(caster, DASH);
    }
    queue(sim, if escape { "dash_escape" } else { "dash" }, caster, input, 1);
}

/// E2 落地：周围敌人（不含防御塔）受伤，被撞的英雄眩晕，她加攻速。
fn land(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let Some(here) = alive(sim, caster) else { return };
    let (team, attack) = sim.get_entity(caster).map_or((0, 0), |e| (e.team(), e.stat().attack));
    view(sim, "e_land", caster, caster);
    sfx(sim, "e_land", caster);
    let us = units(sim);
    let ad = E_DMG + attack * E_RATIO / 100;
    let mut hit = Vec::new();
    for u in us.iter().filter(|u| u.alive && u.targetable && !u.tower && u.team != team) {
        if dist(here, u.at) <= E_RADIUS + u.radius {
            sim.deal_damage(caster, u.id, ad, 0, AttackTypeV1::Skill);
            view(sim, "e_hit", caster, u.id);
            hit.push(u.id);
        }
    }
    // 被撞的英雄：冲向的那个（还在身边的话），否则身边最近的敌方英雄
    let enemy_champ = |u: &&Unit| u.alive && u.champion && u.team != team;
    let stunned = us
        .iter()
        .filter(enemy_champ)
        .find(|u| u.id == input.target_id && dist(here, u.at) <= E_RADIUS + u.radius + 6_000.0)
        .or_else(|| {
            us.iter()
                .filter(enemy_champ)
                .filter(|u| dist(here, u.at) <= E_RADIUS + u.radius)
                .min_by(|a, b| dist(here, a.at).total_cmp(&dist(here, b.at)))
        })
        .map(|u| u.id);
    if let Some(s) = stunned {
        sim.apply_cc(s, &CcV1::stun(E_STUN));
        view(sim, "e_stun", caster, s);
    }
    sim.entity_remove_buff(caster, &camille("e_as"));
    let mut haste = BuffV1::timed(&camille("e_as"), E_AS_T);
    haste.attack_speed_mult = E_AS;
    sim.add_buff(caster, &haste);
    wlog(format!(
        "{} LAND at {}: {ad} damage to {} unit(s), stun {}",
        head(sim, caster),
        pt(here),
        hit.len(),
        stunned.map_or("none".to_string(), |s| who(sim, s))
    ));
}

// ===================== 被动：E 一好就自己找机会 =====================

/// 两次看到之间走得比这快的（闪现、冲刺、传送）不算速度。
const MAX_WALK: f64 = 2_500.0;

/// 挂在 `passive_skill2` 上：学会 E 后每 tick 调一次，每 `AUTO_EVERY` tick 记一下敌方英雄在哪
/// （算出他们每 tick 的速度，选钩点时预判 E2 那一刻他们在哪），再判断要不要出 E。每个青钢影一份。
#[derive(Clone, Default)]
struct AutoE {
    seen: HashMap<usize, (f64, f64, usize)>,
}

impl StablePassive for AutoE {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, entity: usize) {
        let tick = sim.tick();
        if tick % AUTO_EVERY != 0 {
            return;
        }
        let team = sim.get_entity(entity).map_or(0, |e| e.team());
        let mut vel = Velocities::new();
        let mut seen = HashMap::new();
        for u in units(sim).iter().filter(|u| u.champion && u.alive && u.team != team) {
            if let Some(&(x, y, t)) = self.seen.get(&u.id) {
                let dt = tick.saturating_sub(t);
                let v = ((u.at.0 - x) / dt.max(1) as f64, (u.at.1 - y) / dt.max(1) as f64);
                if (1..=2 * AUTO_EVERY).contains(&dt) && v.0.hypot(v.1) <= MAX_WALK {
                    vel.insert(u.id, v);
                }
            }
            seen.insert(u.id, (u.at.0, u.at.1, tick));
        }
        self.seen = seen;
        auto_cast(sim, entity, &vel);
    }
}

/// E 好了、`ENGAGE_R` 内有敌方英雄时：以少打多就逃，否则突进（血少时 `decide` 自己改成逃）。
fn auto_cast(sim: &mut StableSim<'_>, me: usize, vel: &Velocities) {
    let Some(here) = alive(sim, me) else { return };
    if ["e_cd", "e_got"].iter().any(|f| has_buff(sim, me, &camille(f))) || in_ult(sim, me) {
        return;
    }
    let us = units(sim);
    let team = sim.get_entity(me).map_or(0, |e| e.team());
    let foes = foes_of(&us, team, vel);
    if nearest(here, &foes) > ENGAGE_R {
        return;
    }
    let enemies = foes.iter().filter(|f| dist(here, f.at()) <= E_DNG_R).count();
    let allies =
        us.iter().filter(|u| u.champion && u.alive && u.team == team && u.id != me && dist(here, u.at) <= E_ALLY_R).count();
    let outnumbered = (enemies >= 2 && allies == 0) || (enemies >= 3 && allies <= 1);
    decide(sim, me, outnumbered, vel);
}

// ===================== 效果注册 =====================

#[derive(Clone, Copy)]
enum Step {
    Engage,
    Escape,
    Throw,
    Pull,
    Watch,
    E2,
    Dash,
    Land,
    Noop,
}

struct Stage {
    step: Step,
    escape: bool,
}

impl StableEffectType for Stage {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        match self.step {
            Step::Engage => decide(sim, caster, false, &Velocities::new()),
            Step::Escape => decide(sim, caster, true, &Velocities::new()),
            Step::Throw => throw(sim, caster, input, self.escape),
            Step::Pull => pull(sim, caster, input, self.escape),
            Step::Watch => watch(sim, caster, input, self.escape),
            Step::E2 => e2(sim, caster),
            Step::Dash => dash(sim, caster, input, self.escape),
            Step::Land => land(sim, caster, input),
            Step::Noop => {}
        }
    }
}

/// 本包的原生效果：`league_camille_wall:<名字>`。数据层只调前两个。
pub const STAGES: [&str; 13] = [
    "engage",
    "escape",
    "throw",
    "throw_escape",
    "pull",
    "pull_escape",
    "watch",
    "watch_escape",
    "e2",
    "dash",
    "dash_escape",
    "land",
    "noop",
];

fn stage(name: &str) -> Stage {
    let escape = name.ends_with("_escape") || name == "escape";
    let step = match name.trim_end_matches("_escape") {
        "engage" => Step::Engage,
        "escape" => Step::Escape,
        "throw" => Step::Throw,
        "pull" => Step::Pull,
        "watch" => Step::Watch,
        "e2" => Step::E2,
        "dash" => Step::Dash,
        "land" => Step::Land,
        _ => Step::Noop,
    };
    Stage { step, escape }
}

fn init(host: &StableHost) -> StableMod {
    // 上一次启动的日志留一份（.prev.log），重启游戏不丢
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v4.2 (wall + map edge + tower Hookshot) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    let mut module = StableMod::new(ID);
    for name in STAGES {
        module.add_native_effect(format!("{ID}:{name}"), stage(name));
    }
    module.add_native_passive(format!("{ID}:e"), AutoE::default());
    module.set_map_customizer(WallReader);
    host.log(LogLevel::Info, "league_camille_wall v4 loaded (Camille's E hooks walls, the map edge and towers).");
    module
}

declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    fn grid(rows: &[&str]) -> Grid {
        Grid::from_rows(rows)
    }

    fn foe(id: usize, x: f64, y: f64) -> Foe {
        Foe { id, x, y, ..Default::default() }
    }

    fn post(id: usize, x: f64, y: f64, r: f64, hostile: bool) -> Post {
        Post { id, x, y, r, hostile }
    }

    /// 钩点的方向和看向 p 的方向夹角的 cos。
    fn turn(me: (f64, f64), h: &Hit, p: (f64, f64)) -> f64 {
        ((h.x - me.0) * (p.0 - me.0) + (h.y - me.1) * (p.1 - me.1)) / (h.dist * dist(me, p))
    }

    #[test]
    fn parses_nested_arrays() {
        let g = parse_int_grid(" [[0, 1,0],\n [1,0, -2], [3.0,0,0]] ").unwrap();
        assert_eq!(g.cells, vec![vec![0, 1, 0], vec![1, 0, -2], vec![3, 0, 0]]);
        assert_eq!(g.walls(), 4);
        assert!(parse_int_grid("{\"w\":30}").is_none());
        assert!(parse_int_grid("[]").is_none());
    }

    #[test]
    fn builtin_maps_read_walls_y_then_x() {
        for m in MODES {
            let g = Grid::builtin(m);
            assert_eq!((g.cells.len(), g.cells[0].len()), (30, 30));
            assert_eq!(g.bounds.is_some(), m == GameModeKindV1::Moba, "only 5v5 has drawn edges");
        }
        let moba = Grid::builtin(GameModeKindV1::Moba);
        assert_eq!(moba.walls(), 90);
        // 5v5 地图沿主对角线对称（蓝方左下、红方右上）
        assert!((0..30).all(|r| (0..30).all(|c| moba.cells[r][c] == moba.cells[c][r])));
        // 死斗的场地是第 12-17 行、第 6-23 列：基地 (224000, 480000) 在场地里，说明是 walls[y][x]
        let dm = Grid::builtin(GameModeKindV1::DeathMatch);
        assert!(!dm.is_wall(224_000.0, 480_000.0) && !dm.is_wall(736_000.0, 480_000.0));
        assert!(dm.is_wall(480_000.0, 224_000.0));
        assert!(moba.is_wall(-1.0, 5.0) && moba.is_wall(960_001.0, 5.0), "off the map counts as wall");
        // 四边的墙面只给钩子用：格子里那一圈还是空地
        assert!(!moba.is_wall(10_000.0, 300_000.0) && moba.solid(10_000.0, 300_000.0));
        assert!(!moba.solid(60_000.0, 300_000.0));
    }

    #[test]
    fn picks_the_map_nobody_stands_in_a_wall_of() {
        let all = || MODES.iter().map(|m| (*m, Grid::builtin(*m))).collect();
        // 5v5 的上路一塔 (48000, 272000) 在单线地图的墙里
        let moba = [(48_000.0, 272_000.0), (96_000.0, 864_000.0), (480_000.0, 480_000.0)];
        assert_eq!(pick_grid(&moba, all()).unwrap().0, GameModeKindV1::Moba);
        // 单线：都在对角线的路上，5v5 地图也没人在墙里，取墙多的单线
        let lane = [(96_000.0, 864_000.0), (480_000.0, 480_000.0), (864_000.0, 96_000.0)];
        assert_eq!(pick_grid(&lane, all()).unwrap().0, GameModeKindV1::SingleLane);
        // 死斗：都在场地里
        let dm = [(224_000.0, 480_000.0), (736_000.0, 480_000.0), (400_000.0, 450_000.0)];
        assert_eq!(pick_grid(&dm, all()).unwrap().0, GameModeKindV1::DeathMatch);
        // 站在 5v5 四边的墙面外（引擎让人走到那里）照样认得出 5v5
        let edge = [(10_000.0, 300_000.0), (48_000.0, 272_000.0), (96_000.0, 864_000.0)];
        assert_eq!(pick_grid(&edge, all()).unwrap().0, GameModeKindV1::Moba);
    }

    #[test]
    fn rays_stop_in_front_of_the_first_wall() {
        // 她站在 (1.5, 1.5) 格中间；右边第 3 列整列是墙，距离 1.5 格 = 48000 < 射程。
        let g = grid(&["...#....", "...#....", "...#....", "...#....", "...#...."]);
        let (x, y) = (1.5 * CELL, 1.5 * CELL);
        let hits = wall_hits(&g, x, y, E_RANGE);
        let east = hits.iter().find(|h| (h.y - y).abs() < 1.0 && h.x > x).expect("hit to the east");
        assert!((east.x - (3.0 * CELL - WALL_GAP)).abs() < 2.0, "hook point WALL_GAP before the wall: {east:?}");
        assert!((east.dist - (east.x - x)).abs() < 1e-6);
        assert_eq!(east.surface, Surface::Wall);
        // 没有四边墙面的图：左边是地图边，不算墙
        assert!(hits.iter().all(|h| h.x > x - 1.0));
        // 站在墙里：不给钩点
        assert!(wall_hits(&g, 3.5 * CELL, 1.5 * CELL, E_RANGE).is_empty());
        // 太近的墙不钩
        assert!(wall_hits(&g, 3.0 * CELL - 5_000.0, 1.5 * CELL, E_RANGE).iter().all(|h| h.dist >= HOOK_MIN));
    }

    #[test]
    fn the_map_edges_are_walls_to_hook() {
        let moba = Grid::builtin(GameModeKindV1::Moba);
        let (x0, y0, _, _) = MOBA_BOUNDS;
        // 上路靠外侧（左边石堆 x = 22500）：正西方向钩在石堆上
        let me = (60_000.0, 300_000.0);
        let hits = wall_hits(&moba, me.0, me.1, E_RANGE);
        let west = hits.iter().find(|h| (h.y - me.1).abs() < 1.0 && h.x < me.0).expect("the rocks to the west");
        assert_eq!(west.surface, Surface::Edge);
        assert!((west.x - (x0 + WALL_GAP)).abs() < 30.0, "{west:?}");
        // 左上角：西边的石堆和北边的石墙都钩得到
        let corner = wall_hits(&moba, 60_000.0, 62_000.0, E_RANGE);
        assert!(corner.iter().any(|h| h.surface == Surface::Edge && (h.x - (x0 + WALL_GAP)).abs() < 30.0));
        assert!(corner.iter().any(|h| h.surface == Surface::Edge && (h.y - (y0 + WALL_GAP)).abs() < 30.0));
        // 地图中间够不着四边
        assert!(wall_hits(&moba, 480_000.0, 480_000.0, E_RANGE).iter().all(|h| h.surface != Surface::Edge));
        // 打架时钩石堆：他在石堆边上的路上（北边），她从南边沿着石堆过去——钩石堆，拐个弯扑他
        let me = (60_000.0, 360_000.0);
        let target = foe(5, 40_000.0, 300_000.0);
        let hits = hook_points(&moba, me, 10_000.0, &[]);
        let (hook, id) = plan_engage(&moba, &hits, me, &[target], &[]).expect("the rocks beside him");
        assert_eq!((hook.surface, id), (Surface::Edge, 5), "{hook:?}");
        assert!(pull_dive(me, &hook, target.at()) >= PULL_DIVE_COS, "{hook:?}");
        // 越过他钩到他身后的石堆再掉头扑回来：不钩（v4.0 这样做，看起来像反着放）
        assert!(plan_engage(&moba, &hits, (75_000.0, 300_000.0), &[foe(5, 45_000.0, 270_000.0)], &[]).is_none_or(|(h, _)| {
            pull_dive((75_000.0, 300_000.0), &h, (45_000.0, 270_000.0)) >= PULL_DIVE_COS
        }));
        // 逃跑的第二段不往石堆里冲
        let end = plan_flee(&moba, (30_000.0, 300_000.0), &[foe(1, 70_000.0, 300_000.0)]).expect("a way out");
        assert!(end.0 >= x0, "{end:?}");
    }

    #[test]
    fn engage_hooks_toward_him_and_close_enough_to_dive() {
        let moba = Grid::builtin(GameModeKindV1::Moba);
        // 第 12 行第 7-9 列是一段横墙（x 224000-320000，y 384000-416000）；敌人在墙北边上，她在西北：
        // 钩他西边那段墙的北面，拐个弯扑上去
        let me = (240_000.0, 350_000.0);
        let target = foe(7, 300_000.0, 372_000.0);
        let hits = hook_points(&moba, me, 10_000.0, &[]);
        let (hook, id) = plan_engage(&moba, &hits, me, &[target], &[]).expect("a wall next to him");
        assert_eq!((hook.surface, id), (Surface::Wall, 7));
        assert!(hook.y > 383_000.0 && hook.y < 384_000.0 && hook.x < target.x, "{hook:?}");
        let d = dist(hook.at(), target.at());
        assert!((DIVE_MIN..=DIVE_PLAN).contains(&d) && d < dist(me, target.at()), "{d}");
        assert!(turn(me, &hook, target.at()) >= TURN_COS && path_free(&moba, hook.at(), target.at()));
        assert!(pull_dive(me, &hook, target.at()) >= PULL_DIVE_COS);
        // 她从正北过来：墙在他身后，钩过去就得掉头扑回来——不钩
        let north = (272_000.0, 330_000.0);
        assert!(plan_engage(&moba, &hook_points(&moba, north, 10_000.0, &[]), north, &[target], &[]).is_none());
        // 站在他们塔下的不扑；ENGAGE_R 外的不管
        assert!(plan_engage(&moba, &hits, me, &[Foe { guarded: true, ..target }], &[]).is_none());
        assert!(plan_engage(&moba, &hits, me, &[foe(8, 272_000.0, 420_000.0 + ENGAGE_R)], &[]).is_none());
        // 他在北边、墙在南边：不往反方向钩
        assert!(plan_engage(&moba, &hits, me, &[foe(8, 272_000.0, 270_000.0)], &[]).is_none());
        // 空地上（附近 60000 内没有墙）不出手
        let open = (480_000.0, 480_000.0);
        let target = foe(9, 535_000.0, 495_000.0);
        let none = hook_points(&moba, open, 10_000.0, &[]);
        assert!(none.is_empty() && plan_engage(&moba, &none, open, &[target], &[]).is_none());
        // 空地上有座我方塔：钩塔，拉到贴着塔的地方
        let tower = post(4, 525_000.0, 480_000.0, 5_000.0, false);
        let hits = hook_points(&moba, open, 10_000.0, &[tower]);
        let (hook, id) = plan_engage(&moba, &hits, open, &[target], &[]).expect("the tower");
        assert_eq!((hook.surface, id), (Surface::Tower(4), 9));
        assert!((hook.x - 510_000.0).abs() < 1.0 && (hook.dist - 30_000.0).abs() < 1.0, "{hook:?}");
        // 敌方的塔：他不残血就不钩，残血才钩过去扑
        let theirs = post(4, 525_000.0, 480_000.0, 5_000.0, true);
        let hits = hook_points(&moba, open, 10_000.0, &[theirs]);
        assert!(hits[0].hostile && plan_engage(&moba, &hits, open, &[target], &[]).is_none());
        assert!(plan_engage(&moba, &hits, open, &[Foe { low: true, ..target }], &[]).is_some());
        // 塔太近（贴着她）不钩
        assert!(tower_hits(&moba, (505_000.0, 480_000.0), 10_000.0, &[tower]).is_empty());
        // 塔挡在墙前面：那个方向钩的是塔，不是塔后面的墙
        let blocker = post(5, 272_000.0, 360_000.0, 8_000.0, false);
        let hits = hook_points(&moba, north, 10_000.0, &[blocker]);
        assert!(hits.iter().any(|h| h.surface == Surface::Tower(5)));
        assert!(hits.iter().all(|h| h.surface != Surface::Wall || (h.x - 272_000.0).abs() > 5_000.0), "{hits:?}");
    }

    /// 拉过去的方向和扑的方向的夹角的 cos（p：他到时的位置）。
    fn pull_dive(me: (f64, f64), h: &Hit, p: (f64, f64)) -> f64 {
        ((h.x - me.0) * (p.0 - h.x) + (h.y - me.1) * (p.1 - h.y)) / (h.dist * dist(h.at(), p))
    }

    #[test]
    fn no_more_v3_misses() {
        let moba = Grid::builtin(GameModeKindV1::Moba);
        // v3 日志 t=35760：他就在身边 10000，她去钩 36000 外的墙再扑回来——现在贴身不用 E（会掉头扑回来）
        let me = (594_000.0, 580_000.0);
        let hits = hook_points(&moba, me, 10_000.0, &[]);
        assert!(plan_engage(&moba, &hits, me, &[foe(3, 602_000.0, 574_000.0)], &[]).is_none());
        // 贴身、身边就有墙：v4.0 会跳上去再扑回来（打大力士时「一直反向放技能」）——现在不放
        let me = (272_000.0, 368_000.0);
        let hits = hook_points(&moba, me, 10_000.0, &[]);
        assert!(plan_engage(&moba, &hits, me, &[foe(3, 272_000.0, 350_000.0)], &[]).is_none(), "hopped back");
        // v3 日志 t=4526/40944：钩点离他 45000~50000，扑过去前他就走出了 E2 的范围——现在钩点离他不超过 DIVE_PLAN
        for (me, him) in [((171_529.0, 111_611.0), (214_663.0, 77_985.0)), ((324_659.0, 483_589.0), (245_846.0, 459_050.0))] {
            let hits = hook_points(&moba, me, 10_000.0, &[]);
            if let Some((hook, _)) = plan_engage(&moba, &hits, me, &[foe(1, him.0, him.1)], &[]) {
                assert!(dist(hook.at(), him) <= DIVE_PLAN, "{hook:?}");
            }
        }
    }

    #[test]
    fn plans_for_where_he_will_be() {
        let moba = Grid::builtin(GameModeKindV1::Moba);
        let me = (240_000.0, 350_000.0);
        let hits = hook_points(&moba, me, 10_000.0, &[]);
        // 站着不动能扑；同一个人正往北跑（每 tick 900）：E2 时离墙太远，不出手
        let still = foe(7, 300_000.0, 372_000.0);
        assert!(plan_engage(&moba, &hits, me, &[still], &[]).is_some());
        let running = Foe { vy: -900.0, ..still };
        let far = running.lead(30.0);
        assert!((far.1 - (372_000.0 - LEAD_CAP)).abs() < 1.0, "the lead is capped: {far:?}");
        if let Some((hook, _)) = plan_engage(&moba, &hits, me, &[running], &[]) {
            let p = lead_on(&moba, &running, ticks_to_e2(hook.dist));
            assert!(dist(hook.at(), p) <= DIVE_PLAN, "{hook:?} vs {p:?}");
        }
        // 他沿着墙往东走：照他到时的位置挑钩点
        let along = Foe { vx: 250.0, ..still };
        let (hook, _) = plan_engage(&moba, &hits, me, &[along], &[]).expect("he walks along the wall");
        let p = lead_on(&moba, &along, ticks_to_e2(hook.dist));
        assert!(p.0 > still.x + 5_000.0 && (DIVE_MIN..=DIVE_PLAN).contains(&dist(hook.at(), p)), "{hook:?} vs {p:?}");
        assert!(pull_dive(me, &hook, p) >= PULL_DIVE_COS, "{hook:?} vs {p:?}");
        // 他朝墙走：预判停在墙前，不穿进墙里
        let into = Foe { vy: 900.0, ..still };
        let p = lead_on(&moba, &into, 30.0);
        assert!(p.1 < 384_000.0 && p.1 > 382_000.0, "{p:?}");
    }

    #[test]
    fn no_dive_into_three_alone() {
        let moba = Grid::builtin(GameModeKindV1::Moba);
        let me = (240_000.0, 350_000.0);
        let hits = hook_points(&moba, me, 10_000.0, &[]);
        let pack = [foe(7, 300_000.0, 372_000.0), foe(8, 315_000.0, 365_000.0), foe(9, 290_000.0, 355_000.0)];
        assert!(plan_engage(&moba, &hits, me, &pack, &[]).is_none(), "dived three alone");
        // 队友就在那边：扑
        assert!(plan_engage(&moba, &hits, me, &pack, &[(300_000.0, 340_000.0)]).is_some());
    }

    #[test]
    fn escape_runs_away_along_the_wall() {
        let moba = Grid::builtin(GameModeKindV1::Moba);
        let me = (272_000.0, 330_000.0);
        // 逃跑：敌人在北边，钩南边的墙，再沿墙冲开
        let foes = [foe(1, 272_000.0, 285_000.0), foe(2, 305_000.0, 300_000.0)];
        let hook = plan_escape(&hook_points(&moba, me, 10_000.0, &[]), me, &foes).expect("the wall to the south");
        assert!(hook.y > 380_000.0, "{hook:?}");
        assert!(nearest(hook.at(), &foes) > nearest(me, &foes) + 20_000.0);
        // 敌人还在 E_AWAY_R 外：就停在墙边
        assert!(plan_flee(&moba, hook.at(), &foes).is_none());
        // 追上来了：沿墙冲开（南边是墙，冲不进去）
        let chasers = [foe(1, 260_000.0, 330_000.0), foe(2, 290_000.0, 340_000.0)];
        let end = plan_flee(&moba, hook.at(), &chasers).expect("a way out along the wall");
        assert!(nearest(end, &chasers) > nearest(hook.at(), &chasers) + 5_000.0);
        assert!(path_free(&moba, hook.at(), end) && end.1 < 384_000.0, "{end:?}");
        // 不往敌方的塔上钩着逃
        let theirs = post(6, 272_000.0, 372_000.0, 8_000.0, true);
        let hits = hook_points(&moba, me, 10_000.0, &[theirs]);
        assert!(plan_escape(&hits, me, &foes).is_none_or(|h| !h.hostile));
    }

    #[test]
    fn top_lane_fights_hook_the_wall_beside_the_lane() {
        let moba = Grid::builtin(GameModeKindV1::Moba);
        // 上路（x = 80000）东边第 3 列第 15-21 行是墙（x 96000-128000，y 480000-704000）
        let me = (80_000.0, 600_000.0);
        let target = foe(3, 80_000.0, 550_000.0);
        let hits = hook_points(&moba, me, 10_000.0, &[]);
        let (hook, id) = plan_engage(&moba, &hits, me, &[target], &[]).expect("the wall beside the lane");
        assert_eq!((hook.surface, id), (Surface::Wall, 3));
        // 钩路东边那段墙的西面（不是穿过第 17 行的缺口钩到 58000 外）
        assert!(hook.x > 94_000.0 && hook.x < 96_000.0 && hook.dist < 45_000.0, "{hook:?}");
        let d = dist(hook.at(), target.at());
        assert!((DIVE_MIN..=DIVE_PLAN).contains(&d) && d < dist(me, target.at()), "{hook:?}");
    }

    #[test]
    fn stage_names_map_to_steps() {
        for name in STAGES {
            let s = stage(name);
            assert_eq!(s.escape, name.ends_with("escape"), "{name}");
        }
        assert!(matches!(stage("throw_escape").step, Step::Throw));
        assert!(matches!(stage("escape").step, Step::Escape));
        assert!(matches!(stage("noop").step, Step::Noop));
    }
}
