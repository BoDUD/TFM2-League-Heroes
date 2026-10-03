//! 青钢影钩墙附加包——测试版 v0：只观测，不改玩法。
//!
//! 数据层没有任何效果能「看见」墙，所以真正的钩墙得靠原生代码。动手之前先在真实
//! 游戏里确认三件事，本版本只做这三件事，全部写进日志：
//!
//! 1. 附加包能不能替换主包的青钢影（`mod.override_info` 把
//!    `asset/league/champion/league_camille` 指到本包的副本）。副本只改了 E 的说明
//!    （开头「钩墙测试版」）和在 E 出手处加了一个原生探针；看到新说明 = 替换成功。
//! 2. 地图的墙：地图自定义钩子在每局建图时读 `walls`（30×30 格，每格 32000），
//!    每种模式第一次时把整张格子画进日志。
//! 3. 实战里 E 出手的那一刻，附近有没有墙可钩：探针从卡密尔脚下朝 32 个方向扫，
//!    找射程内的第一面墙，记下最适合突进（离敌方英雄近）和最适合逃跑（离敌人远）
//!    的钩点。格子的行列方向还不确定，两种读法都算，靠「英雄不会站在墙里」判断哪种对。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_camille_wall.log`
//! （游戏自己的 log.log 旁边），找不到时写在游戏目录。每次启动游戏清空重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_camille_wall";

/// 地图格子边长（世界单位）与钩索射程、E2 突进距离（与主包青钢影一致）。
const CELL: f64 = 32_000.0;
const HOOK_RANGE: f64 = 60_000.0;
const E2_RANGE: f64 = 40_000.0;
/// 逃跑钩点至少离她这么远才有意义。
const ESCAPE_MIN: f64 = 25_000.0;
const RAY_DIRS: usize = 32;
const RAY_STEP: f64 = 1_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
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

// ===================== 墙格子 =====================

/// 一张墙格子：`cells[r][c]`，非 0 为墙。r/c 对应 y/x 还是 x/y 由 [`Orient`] 决定。
#[derive(Clone, Debug, PartialEq)]
pub struct Grid {
    pub cells: Vec<Vec<i64>>,
}

/// 格子的两种读法。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Orient {
    /// `cells[y][x]`
    RowY,
    /// `cells[x][y]`
    RowX,
}

impl Grid {
    /// 世界坐标落在墙里（或地图外）吗。
    pub fn is_wall(&self, orient: Orient, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return true;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        let (r, c) = match orient {
            Orient::RowY => (cy, cx),
            Orient::RowX => (cx, cy),
        };
        match self.cells.get(r).and_then(|row| row.get(c)) {
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
    (!rows.is_empty()).then_some(Grid { cells: rows })
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

/// 每种模式最近一次建图读到的墙格子（同一模式的地图每局相同）。
static GRIDS: LazyLock<Mutex<HashMap<u32, Grid>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
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
            if dumped.contains(&code) {
                false
            } else {
                dumped.push(code);
                true
            }
        };
        if first {
            let mut out = format!("== map mode={} ==\n", mode_name(code));
            match &grid {
                Some(g) => {
                    let width = g.cells.iter().map(|r| r.len()).max().unwrap_or(0);
                    out += &format!(
                        "walls: {} rows x {} cols, {} wall cells (# = wall, row 0 first)\n",
                        g.cells.len(),
                        width,
                        g.walls()
                    );
                    for (r, row) in g.cells.iter().enumerate() {
                        let line: String = row.iter().map(|v| if *v != 0 { '#' } else { '.' }).collect();
                        out += &format!("{r:02} {line}\n");
                    }
                }
                None => out += &format!("walls: not a grid; raw = {}\n", clip(raw.as_deref().unwrap_or("<none>"), 600)),
            }
            for key in ["nexus_pos", "fountains", "towers", "camps", "lanes"] {
                let v = doc.get_json(key).unwrap_or_else(|| "<none>".into());
                out += &format!("{key} = {}\n", clip(&v, 1200));
            }
            wlog(out);
        }
        if let Some(g) = grid {
            GRIDS.lock().unwrap_or_else(|e| e.into_inner()).insert(code, g);
        }
    }
}

/// 探针用的地图：优先 5v5（Moba），否则任意一张。
fn current_grid() -> Option<(u32, Grid)> {
    let grids = GRIDS.lock().unwrap_or_else(|e| e.into_inner());
    let moba = GameModeKindV1::Moba.code();
    grids
        .get(&moba)
        .map(|g| (moba, g.clone()))
        .or_else(|| grids.iter().next().map(|(k, g)| (*k, g.clone())))
}

// ===================== 钩点搜索 =====================

/// 一条射线打到的墙：钩点（墙前最后一个可走的位置）和离她的距离。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Hit {
    pub x: f64,
    pub y: f64,
    pub dist: f64,
}

/// 从 (x, y) 朝 `RAY_DIRS` 个方向扫，返回射程内每个方向第一面墙前的钩点。
/// 起点本身在墙里时返回空（说明格子读法不对或格子太粗）。
pub fn wall_hits(grid: &Grid, orient: Orient, x: f64, y: f64) -> Vec<Hit> {
    let mut hits = Vec::new();
    if grid.is_wall(orient, x, y) {
        return hits;
    }
    for k in 0..RAY_DIRS {
        let a = k as f64 * std::f64::consts::TAU / RAY_DIRS as f64;
        let (dx, dy) = (a.cos(), a.sin());
        let mut last = (x, y, 0.0);
        let mut d = RAY_STEP;
        while d <= HOOK_RANGE {
            let (px, py) = (x + dx * d, y + dy * d);
            if grid.is_wall(orient, px, py) {
                hits.push(Hit { x: last.0, y: last.1, dist: last.2 });
                break;
            }
            last = (px, py, d);
            d += RAY_STEP;
        }
    }
    hits
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 突进：离某个敌方英雄最近、且在 E2 距离内的钩点（返回钩点和那段距离）。
pub fn best_engage(hits: &[Hit], enemies: &[(f64, f64)]) -> Option<(Hit, f64)> {
    hits.iter()
        .filter_map(|h| {
            let d = enemies.iter().map(|e| dist((h.x, h.y), *e)).fold(f64::INFINITY, f64::min);
            (d <= E2_RANGE).then_some((*h, d))
        })
        .min_by(|a, b| a.1.total_cmp(&b.1))
}

/// 逃跑：离她至少 `ESCAPE_MIN`、离最近敌人最远的钩点（返回钩点和离最近敌人的距离）。
pub fn best_escape(hits: &[Hit], enemies: &[(f64, f64)]) -> Option<(Hit, f64)> {
    hits.iter()
        .filter(|h| h.dist >= ESCAPE_MIN)
        .map(|h| {
            let d = enemies.iter().map(|e| dist((h.x, h.y), *e)).fold(f64::INFINITY, f64::min);
            (*h, d)
        })
        .max_by(|a, b| a.1.total_cmp(&b.1))
}

// ===================== 探针（E 出手时调用） =====================

struct Probe {
    engage: bool,
}

impl StableEffectType for Probe {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let kind = if self.engage { "engage" } else { "escape" };
        let Some(me) = sim.get_entity(caster) else { return };
        let (mx, my) = me.pos();
        let team = me.team();
        let here = (mx as f64, my as f64);
        let hold = sim.get_entity(input.target_id).map(|h| {
            let (hx, hy) = h.pos();
            (input.target_id, dist(here, (hx as f64, hy as f64)))
        });

        let mut enemies = Vec::new();
        let mut champions = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || !e.is_alive() {
                continue;
            }
            let (ex, ey) = e.pos();
            champions.push((ex as f64, ey as f64));
            if e.team() != team {
                enemies.push((ex as f64, ey as f64));
            }
        }

        let mut line = format!(
            "[{}] t={} probe={kind} camille#{caster} pos=({mx},{my}) cell=({},{}) hold={}",
            origin_label(sim),
            sim.tick(),
            (here.0 / CELL) as i64,
            (here.1 / CELL) as i64,
            hold.map_or("-".to_string(), |(id, d)| format!("#{id} d={d:.0}")),
        );
        match current_grid() {
            None => line += " | no wall grid yet",
            Some((mode, grid)) => {
                line += &format!(" | map={}", mode_name(mode));
                for (tag, orient) in [("A[y][x]", Orient::RowY), ("B[x][y]", Orient::RowX)] {
                    let in_wall = champions.iter().filter(|c| grid.is_wall(orient, c.0, c.1)).count();
                    let hits = wall_hits(&grid, orient, here.0, here.1);
                    let near = hits.iter().map(|h| h.dist).fold(f64::INFINITY, f64::min);
                    let fmt = |b: Option<(Hit, f64)>| {
                        b.map_or("none".to_string(), |(h, d)| {
                            format!("({:.0},{:.0}) hook={:.0} enemy={:.0}", h.x, h.y, h.dist, d)
                        })
                    };
                    line += &format!(
                        " | {tag}: champs_in_wall={in_wall}/{} walls_in_range={}/{RAY_DIRS} nearest={} engage={} escape={}",
                        champions.len(),
                        hits.len(),
                        if near.is_finite() { format!("{near:.0}") } else { "-".into() },
                        fmt(best_engage(&hits, &enemies)),
                        fmt(best_escape(&hits, &enemies)),
                    );
                }
            }
        }
        wlog(line);
    }
}

// ===================== 入口 =====================

fn init(host: &StableHost) -> StableMod {
    let _ = std::fs::remove_file(&*LOG_PATH);
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v0 (log only) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    let mut module = StableMod::new(ID);
    module.add_native_effect(format!("{ID}:probe_engage"), Probe { engage: true });
    module.add_native_effect(format!("{ID}:probe_escape"), Probe { engage: false });
    module.set_map_customizer(WallReader);
    host.log(LogLevel::Info, "league_camille_wall v0 loaded (log only).");
    module
}

declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    fn grid(rows: &[&str]) -> Grid {
        Grid {
            cells: rows.iter().map(|r| r.chars().map(|c| (c == '#') as i64).collect()).collect(),
        }
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
    fn orientation_reads_rows_as_y_or_x() {
        // 第 0 行第 2 列是墙
        let g = grid(&["..#", "...", "..."]);
        let (x, y) = (2.5 * CELL, 0.5 * CELL);
        assert!(g.is_wall(Orient::RowY, x, y));
        assert!(!g.is_wall(Orient::RowX, x, y));
        assert!(g.is_wall(Orient::RowX, y, x));
        assert!(g.is_wall(Orient::RowY, -1.0, 5.0), "off the map counts as wall");
        assert!(g.is_wall(Orient::RowY, 3.5 * CELL, 0.5 * CELL), "past the edge counts as wall");
    }

    #[test]
    fn rays_stop_in_front_of_the_first_wall() {
        // 她站在 (1.5, 1.5) 格中间；右边第 3 列整列是墙，距离 1.5 格 = 48000 < 射程。
        let g = grid(&["...#....", "...#....", "...#....", "...#....", "...#...."]);
        let (x, y) = (1.5 * CELL, 1.5 * CELL);
        let hits = wall_hits(&g, Orient::RowY, x, y);
        let east = hits.iter().find(|h| (h.y - y).abs() < 1.0 && h.x > x).expect("hit to the east");
        assert!(east.x < 3.0 * CELL && east.x >= 3.0 * CELL - RAY_STEP, "hook point just before the wall: {east:?}");
        assert!((east.dist - (east.x - x)).abs() < 1e-6);
        // 左边第 0 列外是地图边（算墙），也在射程内
        assert!(hits.iter().any(|h| h.x < x));
        // 站在墙里：不给钩点
        assert!(wall_hits(&g, Orient::RowY, 3.5 * CELL, 1.5 * CELL).is_empty());
    }

    #[test]
    fn picks_engage_and_escape_points() {
        let hits = [
            Hit { x: 100_000.0, y: 0.0, dist: 30_000.0 },
            Hit { x: 0.0, y: 100_000.0, dist: 50_000.0 },
            Hit { x: 10_000.0, y: 0.0, dist: 10_000.0 },
        ];
        let enemies = [(120_000.0, 0.0)];
        let (h, d) = best_engage(&hits, &enemies).unwrap();
        assert_eq!((h.x, d), (100_000.0, 20_000.0));
        let (h, _) = best_escape(&hits, &enemies).unwrap();
        assert_eq!(h.y, 100_000.0, "farthest from the enemy among points at least 25000 away");
        assert!(best_engage(&hits, &[(500_000.0, 500_000.0)]).is_none());
    }
}
