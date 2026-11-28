//! Which 5v5 map a match is played on - the game's own or Rin's Summoner's Rift - and the Rift's walls (2026-11-10,
//! the user: 「这个地图我们的大小龙兼容吗 还有所有的mod英雄 比如特殊机制墙体交互的 也查一查」「要同时兼容原版地图和这个地图」).
//!
//! **The game's own 5v5 map** is 30 x 30 wall cells of 32000 (960000 square). The add-ons keep their built-in grids
//! for it (league_camille_wall/src/maps.rs) and behave on it exactly as before.
//!
//! **Rin 的召唤师峡谷**（第三方 mod `tfm2_lol_map_test`）在它自己的 DLL 里建 5v5 地图：地形、寻路、视野、三路的高地塔和
//! 兵营、野区。这些都不走我们的地图钩子读的地图文档，游戏不会告诉附加包峡谷的墙在哪；作者把地图资料跟 mod 一起发在
//! `地图资料/` 里，本模块从 mod 文件夹（`mods/tfm2_lol_map_test/地图资料/`）或 `LEAGUE_RIFT_WALLS` 指的地方读一次，
//! 从不随我们的包发（那是作者的数据）。
//!
//! 2026-11-26 起按 0.1.65（`0.1.65-game073+scale120.1.integrated.1`，游戏 0.7.3，用户：「大地图已经更新了」）：
//! 整张图比 0.1.28 放大 1.2 倍，边长 1937454，原版地图上的坐标 × 2.018。读三样：
//! - 墙：`墙体坐标.json`，每格一个矩形 [左, 上, 右, 下]，按 `坐标分母`（11）的分子写，295 x 296 格、每格 72000/11，
//!   从 x = 36000/11 起（[`rift_walls`]）。
//! - 英雄中心站得住的地方：墙往外长一格（[`rift_ground`]），拿作者的寻路网格 `walk.bin`（1180 x 1184 细格、每格 18000/11，
//!   离墙不到 5000 的都不能走）核对：0.1.65 上长一格以后剩下的格子全在寻路网格能走的地方里，一格不差。
//! - 草丛：`brush-fine.bin`，同一套细格，每格一个连通的草丛编号，0 不是草丛（[`rift_brush`]）。以前峡谷没有草丛资料，
//!   附加包的草丛机制在峡谷上一律关着。
//! 旧的 0.1.28（墙体坐标.json 是按行合并的矩形、边长 1614545，要游戏 0.7.1）不再读：现在的游戏装不上它。
//! 没有资料文件时附加包不知道峡谷哪里有墙、哪里是草丛，那些机制在峡谷上关着，比拿原版地图的墙去撞峡谷强。
//!
//! **Which map** ([`map_of`], [`map_of_sim`]): a tower or a nexus past 1000000 on either axis (and within 2000000:
//! farther is no place on any map) stands on the Rift; none past it is the game's own map. [`map_of_sim`] reads only
//! the towers and nexuses (they never move, never get banished); [`map_of`] takes any points, so a caller without a sim
//! should pass structures first (a champion alone may be parked somewhere odd while banished). Single lane and death
//! match are the game's own on both (the Rift replaces only the 5v5 map).

use std::path::{Path, PathBuf};
use std::sync::OnceLock;

use mod_api_stable::{EntityKindV1, StableSim};

/// The game's own wall cells (world units).
pub const NATIVE_CELL: f64 = 32_000.0;
/// The game's own 5v5 map's side (30 cells).
pub const NATIVE_EXTENT: f64 = 960_000.0;
/// Rin's map mod.
pub const RIFT_MOD: &str = "tfm2_lol_map_test";
/// 峡谷的边长：0.1.65 的 数据说明.json「地图边长」、墙体坐标.json「世界边长」（0.1.28 是 1614545）。
pub const RIFT_EXTENT: f64 = 1_937_454.0;
/// A point past this on either axis is on the Rift: the game's own map ends at 960000.
pub const RIFT_FROM: f64 = 1_000_000.0;
/// 比这还远就不在任何一张图上（被放逐、藏起来的单位），从不拿来认图。峡谷放大以后塔和水晶到了 1818439，旧的 1700000 不够。
pub const MAP_LIMIT: f64 = 2_000_000.0;
/// 测试和别的安装位置用：指向墙体坐标.json，或者放着它的 地图资料 文件夹。比 mod 文件夹优先。
pub const RIFT_WALLS_ENV: &str = "LEAGUE_RIFT_WALLS";
/// mod 文件夹里放地图资料的文件夹和文件名。
pub const RIFT_DATA_DIR: &str = "地图资料";
pub const RIFT_WALLS_FILE: &str = "墙体坐标.json";
pub const RIFT_INFO_FILE: &str = "数据说明.json";
pub const RIFT_WALK_FILE: &str = "walk.bin";
pub const RIFT_BRUSH_FILE: &str = "brush-fine.bin";
/// 作者的寻路半径：寻路网格让英雄中心离墙这么远。
pub const RIFT_PATH_RADIUS: f64 = 5_000.0;

/// A 5v5 map.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Map {
    /// The game's own (960000 square).
    Native,
    /// Rin's Summoner's Rift (1937454 square).
    Rift,
}

impl Map {
    /// The map's side (world units).
    pub fn extent(self) -> f64 {
        match self {
            Map::Native => NATIVE_EXTENT,
            Map::Rift => RIFT_EXTENT,
        }
    }

    /// The middle of the map.
    pub fn center(self) -> (f64, f64) {
        let h = self.extent() / 2.0;
        (h, h)
    }

    /// How much bigger than the game's own map: a length tuned on it that follows the map's size (the river's width,
    /// how far a base reaches) times this. Fight distances (ranges, speeds, radii) do not: the heroes are the same size.
    pub fn scale(self) -> f64 {
        self.extent() / NATIVE_EXTENT
    }

    /// Past this a position is no place on the map (banished, hidden units): 1.25 x the side, 1200000 on the game's own
    /// map (the add-ons' old `MAP_MAX`).
    pub fn limit(self) -> f64 {
        self.extent() * 1.25
    }

    /// Inside the map's square (a step clamped here stays on the map).
    pub fn clamp(self, p: (f64, f64)) -> (f64, f64) {
        let e = self.extent();
        (p.0.clamp(0.0, e), p.1.clamp(0.0, e))
    }

    /// For log lines.
    pub fn key(self) -> &'static str {
        match self {
            Map::Native => "native",
            Map::Rift => "rift",
        }
    }
}

/// Does `p` stand on the Rift (past the game's own map, within any map)?
pub fn on_rift(p: (f64, f64)) -> bool {
    let far = p.0.max(p.1);
    p.0 >= 0.0 && p.1 >= 0.0 && far > RIFT_FROM && far <= MAP_LIMIT
}

/// The map these points (towers, nexuses, living units) stand on.
pub fn map_of(points: &[(f64, f64)]) -> Map {
    if points.iter().any(|&p| on_rift(p)) {
        Map::Rift
    } else {
        Map::Native
    }
}

/// The map of `sim`'s match from its towers and nexuses (they never move, never leave the map, never get banished; the
/// game lists the nexuses with the towers). A match without any is not a 5v5 match (death match): the game's own map.
/// Champions are never asked: where the game parks a banished or hidden unit is not known for sure (the add-ons' old
/// `MAP_MAX` filter only says it is past 1200000), and one parked inside the Rift's square must not turn a match on
/// the game's own map into the Rift.
pub fn map_of_sim(sim: &StableSim<'_>) -> Map {
    let mut points: Vec<(f64, f64)> = (0..sim.tower_count())
        .filter_map(|i| sim.get_entity(sim.tower_id_at(i)))
        .map(|e| {
            let (x, y) = e.pos();
            (x as f64, y as f64)
        })
        .collect();
    if points.is_empty() {
        // a host that lists no towers: the nexuses by kind
        for i in 0..sim.entity_count() {
            if let Some(e) = sim.entity_at(i) {
                if matches!(e.kind(), Some(EntityKindV1::Nexus | EntityKindV1::Tower)) {
                    let (x, y) = e.pos();
                    points.push((x as f64, y as f64));
                }
            }
        }
    }
    map_of(&points)
}

/// A wall grid in world units: `cells[y][x]` (true = wall), each `cell` square, cell (0, 0) at `origin`; off the grid is
/// wall.
#[derive(Clone, Debug, PartialEq)]
pub struct Walls {
    pub cells: Vec<Vec<bool>>,
    pub cell: f64,
    pub origin: (f64, f64),
    /// The map's size (width, height).
    pub extent: (f64, f64),
    /// The file's `版本`.
    pub version: String,
    /// Where it was read from (empty: not from a file).
    pub source: String,
}

impl Walls {
    pub fn cols(&self) -> usize {
        self.cells.iter().map(Vec::len).max().unwrap_or(0)
    }

    pub fn rows(&self) -> usize {
        self.cells.len()
    }

    /// Wall cells.
    pub fn count(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }

    /// The cell holding (x, y), if on the grid.
    pub fn cell_of(&self, x: f64, y: f64) -> Option<(usize, usize)> {
        if !(x.is_finite() && y.is_finite()) {
            return None;
        }
        let (fx, fy) = ((x - self.origin.0) / self.cell, (y - self.origin.1) / self.cell);
        if fx < 0.0 || fy < 0.0 {
            return None;
        }
        let (cx, cy) = (fx as usize, fy as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).map(|_| (cx, cy))
    }

    /// Is (x, y) in a wall (off the grid counts)?
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        self.cell_of(x, y).is_none_or(|(cx, cy)| self.cells[cy][cx])
    }

    /// The middle of cell (cx, cy).
    pub fn center(&self, cx: usize, cy: usize) -> (f64, f64) {
        (self.origin.0 + (cx as f64 + 0.5) * self.cell, self.origin.1 + (cy as f64 + 0.5) * self.cell)
    }

    /// The walls grown by one cell all round (the 8 neighbours of every wall cell): where a hero's centre cannot stand.
    /// 只在没有 walk.bin 时顶替作者的寻路网格（0.1.65 一格 6545，比寻路半径 5000 宽，宁可少站一点也不站进墙边）。
    pub fn padded(&self) -> Walls {
        let (rows, cols) = (self.rows(), self.cols());
        let mut cells = vec![vec![false; cols]; rows];
        for (y, row) in self.cells.iter().enumerate() {
            for (x, w) in row.iter().enumerate() {
                if *w {
                    for yy in y.saturating_sub(1)..(y + 2).min(rows) {
                        for xx in x.saturating_sub(1)..(x + 2).min(cols) {
                            cells[yy][xx] = true;
                        }
                    }
                }
            }
        }
        Walls { cells, ..self.clone() }
    }

    /// The nearest point within `max` of `p` that is in no wall cell (cell by cell outward from `p`'s; the point of the
    /// open cell nearest to `p`, a unit inside it), or None. `p` itself when it is open.
    pub fn nearest_open(&self, p: (f64, f64), max: f64) -> Option<(f64, f64)> {
        if !self.is_wall(p.0, p.1) {
            return Some(p);
        }
        let (rows, cols) = (self.rows() as i64, self.cols() as i64);
        if rows == 0 || cols == 0 {
            return None;
        }
        let c = |v: f64, o: f64, n: i64| (((v - o) / self.cell).floor() as i64).clamp(0, n - 1);
        let (px, py) = (c(p.0, self.origin.0, cols), c(p.1, self.origin.1, rows));
        let rings = (max / self.cell).ceil() as i64 + 1;
        let mut best: Option<(f64, (f64, f64))> = None;
        for k in 0..=rings {
            // a ring's cells are no nearer than (k - 1) cells: stop once that is past the best found (or past max)
            let floor = (k - 1).max(0) as f64 * self.cell;
            if floor > max || best.is_some_and(|b| floor > b.0) {
                break;
            }
            for cy in (py - k)..=(py + k) {
                for cx in (px - k)..=(px + k) {
                    if (cx - px).abs().max((cy - py).abs()) != k || cx < 0 || cy < 0 || cx >= cols || cy >= rows {
                        continue;
                    }
                    if self.cells[cy as usize][cx as usize] {
                        continue;
                    }
                    let (x0, y0) = (self.origin.0 + cx as f64 * self.cell, self.origin.1 + cy as f64 * self.cell);
                    let inset = 1.0_f64.min(self.cell / 4.0);
                    let q = (p.0.clamp(x0 + inset, x0 + self.cell - inset), p.1.clamp(y0 + inset, y0 + self.cell - inset));
                    let d = ((q.0 - p.0).powi(2) + (q.1 - p.1).powi(2)).sqrt();
                    if d <= max && best.is_none_or(|b| d < b.0) {
                        best = Some((d, q));
                    }
                }
            }
        }
        best.map(|b| b.1)
    }

    /// Is the straight line from `a` to `b` clear of wall cells (looked at every `step`, both ends included)?
    pub fn line_clear(&self, a: (f64, f64), b: (f64, f64), step: f64) -> bool {
        let len = ((b.0 - a.0).powi(2) + (b.1 - a.1).powi(2)).sqrt();
        let n = (len / step.max(1.0)).ceil().max(1.0) as usize;
        (0..=n).all(|i| {
            let t = i as f64 / n as f64;
            !self.is_wall(a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
        })
    }

    /// The grid as `#` / `.` rows (tests, logs).
    pub fn rows_text(&self) -> Vec<String> {
        self.cells.iter().map(|r| r.iter().map(|w| if *w { '#' } else { '.' }).collect()).collect()
    }

    /// A grid from `#` / `.` rows (tests): cells of `cell` from `origin`, a map of `extent`.
    pub fn from_rows(rows: &[&str], cell: f64, origin: (f64, f64), extent: (f64, f64)) -> Walls {
        Walls {
            cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(),
            cell,
            origin,
            extent,
            version: String::new(),
            source: String::new(),
        }
    }
}

/// 峡谷的草丛：作者的细格，每格一个草丛编号（同一片连着的草丛同一个号），0 不是草丛，格子外也不是。
#[derive(Clone, Debug, PartialEq)]
pub struct Brush {
    /// 行优先，`cols` x `rows`。
    pub zones: Vec<u16>,
    pub cols: usize,
    pub rows: usize,
    pub cell: f64,
    pub origin: (f64, f64),
    /// 从哪读的（空：不是文件）。
    pub source: String,
}

impl Brush {
    /// (x, y) 所在那一格。
    pub fn cell_of(&self, x: f64, y: f64) -> Option<(usize, usize)> {
        if !(x.is_finite() && y.is_finite()) {
            return None;
        }
        let (fx, fy) = ((x - self.origin.0) / self.cell, (y - self.origin.1) / self.cell);
        if fx < 0.0 || fy < 0.0 || fx >= self.cols as f64 || fy >= self.rows as f64 {
            return None;
        }
        Some((fx as usize, fy as usize))
    }

    /// (x, y) 在哪一片草丛里（0：不在草丛里）。
    pub fn zone(&self, x: f64, y: f64) -> u16 {
        self.cell_of(x, y).map_or(0, |(cx, cy)| self.zones[cy * self.cols + cx])
    }

    pub fn in_brush(&self, x: f64, y: f64) -> bool {
        self.zone(x, y) != 0
    }

    /// 草丛格数。
    pub fn count(&self) -> usize {
        self.zones.iter().filter(|z| **z != 0).count()
    }

    /// 几片草丛。
    pub fn zone_count(&self) -> usize {
        let mut seen: Vec<u16> = self.zones.iter().copied().filter(|z| *z != 0).collect();
        seen.sort_unstable();
        seen.dedup();
        seen.len()
    }

    /// 第 (cx, cy) 格的中心。
    pub fn center(&self, cx: usize, cy: usize) -> (f64, f64) {
        (self.origin.0 + (cx as f64 + 0.5) * self.cell, self.origin.1 + (cy as f64 + 0.5) * self.cell)
    }

    /// `p` 周围 `max` 以内最近的草丛格的中心（`p` 自己在草丛里就是 `p`）。
    pub fn nearest(&self, p: (f64, f64), max: f64) -> Option<(f64, f64)> {
        if self.in_brush(p.0, p.1) {
            return Some(p);
        }
        if !(p.0.is_finite() && p.1.is_finite()) || self.cols == 0 || self.rows == 0 {
            return None;
        }
        let r = (max / self.cell).ceil() as i64 + 1;
        let c = |v: f64, o: f64| ((v - o) / self.cell).floor() as i64;
        let (px, py) = (c(p.0, self.origin.0), c(p.1, self.origin.1));
        let mut best: Option<(f64, (f64, f64))> = None;
        for cy in (py - r).max(0)..=(py + r).min(self.rows as i64 - 1) {
            for cx in (px - r).max(0)..=(px + r).min(self.cols as i64 - 1) {
                if self.zones[cy as usize * self.cols + cx as usize] == 0 {
                    continue;
                }
                let q = self.center(cx as usize, cy as usize);
                let d = ((q.0 - p.0).powi(2) + (q.1 - p.1).powi(2)).sqrt();
                if d <= max && best.is_none_or(|b| d < b.0) {
                    best = Some((d, q));
                }
            }
        }
        best.map(|b| b.1)
    }

    /// 换到 `like` 那套格子上（大小、原点、行列数照它）：一格里至少 `share` 的地方是草丛就算草丛。
    pub fn coarse(&self, like: &Walls, share: f64) -> Walls {
        let (cols, rows) = (like.cols(), like.rows());
        let mut hits = vec![vec![0u32; cols]; rows];
        let mut all = vec![vec![0u32; cols]; rows];
        for y in 0..self.rows {
            for x in 0..self.cols {
                let c = self.center(x, y);
                let Some((cx, cy)) = like.cell_of(c.0, c.1) else { continue };
                all[cy][cx] += 1;
                if self.zones[y * self.cols + x] != 0 {
                    hits[cy][cx] += 1;
                }
            }
        }
        let cells = (0..rows)
            .map(|y| (0..cols).map(|x| hits[y][x] > 0 && hits[y][x] as f64 >= share * all[y][x].max(1) as f64).collect())
            .collect();
        Walls { cells, cell: like.cell, origin: like.origin, extent: like.extent, version: String::new(), source: self.source.clone() }
    }

    /// 当成一张 [`Walls`]（true = 草丛），给拿自己墙格代码处理草丛的附加包用。
    pub fn as_walls(&self, extent: (f64, f64)) -> Walls {
        let cells = (0..self.rows).map(|y| self.zones[y * self.cols..(y + 1) * self.cols].iter().map(|z| *z != 0).collect())
            .collect();
        Walls { cells, cell: self.cell, origin: self.origin, extent, version: String::new(), source: self.source.clone() }
    }
}

// ===================== 作者的地图资料 =====================

/// The text right after `"key":` (a key spelled exactly so: `"矩形"` is not `"矩形列"`).
fn value_after<'a>(s: &'a str, key: &str) -> Option<&'a str> {
    let quoted = format!("\"{key}\"");
    let mut from = 0;
    while let Some(i) = s[from..].find(&quoted) {
        let rest = s[from + i + quoted.len()..].trim_start();
        if let Some(v) = rest.strip_prefix(':') {
            return Some(v.trim_start());
        }
        from += i + quoted.len();
    }
    None
}

/// A JSON string value at the start of `s` (no escapes needed for a version).
fn string_value(s: &str) -> Option<String> {
    let s = s.strip_prefix('"')?;
    Some(s[..s.find('"')?].to_string())
}

/// 开头的一个 JSON 数。
fn number_value(s: &str) -> Option<f64> {
    let end = s.find(|c: char| !matches!(c, '-' | '+' | '.' | 'e' | 'E' | '0'..='9')).unwrap_or(s.len());
    s[..end].parse().ok()
}

/// A JSON array of numbers and arrays at the start of `s`: the flat numbers of each innermost array, in order.
/// `[1, 2]` -> [[1, 2]]; `[[1, 2], [3]]` -> [[1, 2], [3]].
fn number_rows(s: &str) -> Option<Vec<Vec<f64>>> {
    let b = s.as_bytes();
    if b.first() != Some(&b'[') {
        return None;
    }
    let (mut depth, mut i) = (0usize, 0usize);
    let (mut rows, mut cur): (Vec<Vec<f64>>, Vec<f64>) = (Vec::new(), Vec::new());
    while i < b.len() {
        match b[i] {
            b'[' => {
                depth += 1;
                cur.clear();
                i += 1;
            }
            b']' => {
                if !cur.is_empty() {
                    rows.push(std::mem::take(&mut cur));
                }
                depth -= 1;
                i += 1;
                if depth == 0 {
                    return Some(rows);
                }
            }
            b'-' | b'+' | b'.' | b'0'..=b'9' => {
                let start = i;
                while i < b.len() && matches!(b[i], b'-' | b'+' | b'.' | b'e' | b'E' | b'0'..=b'9') {
                    i += 1;
                }
                cur.push(s[start..i].parse().ok()?);
            }
            b',' | b' ' | b'\n' | b'\r' | b'\t' => i += 1,
            _ => return None,
        }
    }
    None
}

/// 读墙体坐标.json：`世界边长`、`坐标分母`，`矩形` 每项 [左, 上, 右, 下]（分子，除以分母是世界坐标，右下不含）。
/// 格子边长取矩形里最短的那条边，原点取第一个矩形对它的余数；有矩形不在这套格子上就整个不读，免得读歪。
pub fn parse_rift_walls(json: &str) -> Result<Walls, String> {
    let s = json.trim_start_matches('\u{feff}');
    let number = |key: &str| value_after(s, key).and_then(number_value).ok_or_else(|| format!("no `{key}`"));
    let side = number("世界边长")?;
    let den = number("坐标分母")?;
    if !(side > 0.0 && side <= MAP_LIMIT && den >= 1.0 && den.fract() == 0.0) {
        return Err(format!("odd sizes: side {side}, denominator {den}"));
    }
    let rects = value_after(s, "矩形").and_then(number_rows).ok_or("no `矩形`")?;
    if rects.is_empty() {
        return Err("no rectangle".to_string());
    }
    for r in &rects {
        let [l, t, rr, b] = r.as_slice() else { return Err(format!("a rectangle of {} numbers", r.len())) };
        if [l, t, rr, b].iter().any(|v| v.fract() != 0.0 || **v < 0.0) || rr <= l || b <= t {
            return Err(format!("odd rectangle {r:?}"));
        }
    }
    let cell = rects.iter().map(|r| (r[2] - r[0]).min(r[3] - r[1])).fold(f64::INFINITY, f64::min);
    let origin = (rects[0][0].rem_euclid(cell), rects[0][1].rem_euclid(cell));
    let on = |v: f64, o: f64| (v - o).rem_euclid(cell) == 0.0;
    let mut cols = 0usize;
    let mut rows = 0usize;
    for r in &rects {
        if !(on(r[0], origin.0) && on(r[2], origin.0) && on(r[1], origin.1) && on(r[3], origin.1)) || r[0] < origin.0 {
            return Err(format!("rectangle {r:?} is off the grid of {cell} from ({}, {})", origin.0, origin.1));
        }
        cols = cols.max(((r[2] - origin.0) / cell) as usize);
        rows = rows.max(((r[3] - origin.1) / cell) as usize);
    }
    if cols > 4096 || rows > 4096 {
        return Err(format!("a grid of {cols} x {rows}"));
    }
    let mut cells = vec![vec![false; cols]; rows];
    for r in &rects {
        let (x0, x1) = (((r[0] - origin.0) / cell) as usize, ((r[2] - origin.0) / cell) as usize);
        let (y0, y1) = (((r[1] - origin.1) / cell) as usize, ((r[3] - origin.1) / cell) as usize);
        for row in &mut cells[y0..y1] {
            row[x0..x1].iter_mut().for_each(|c| *c = true);
        }
    }
    let version = value_after(s, "版本").and_then(string_value).unwrap_or_default();
    Ok(Walls { cells, cell: cell / den, origin: (origin.0 / den, origin.1 / den), extent: (side, side), version, source: String::new() })
}

/// 数据说明.json 写的细格：walk.bin 和 brush-fine.bin 都按它排。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Fine {
    pub cols: usize,
    pub rows: usize,
    pub origin: (f64, f64),
    pub cell: f64,
}

/// 读数据说明.json 的 `细网格宽高`、`原点分子`、`网格步长分子`、`分母`。
pub fn parse_fine(json: &str) -> Result<Fine, String> {
    let s = json.trim_start_matches('\u{feff}');
    let pair = |key: &str| -> Result<(f64, f64), String> {
        match value_after(s, key).and_then(number_rows).as_deref() {
            Some([r]) if r.len() == 2 => Ok((r[0], r[1])),
            _ => Err(format!("no `{key}` [a, b]")),
        }
    };
    let number = |key: &str| value_after(s, key).and_then(number_value).ok_or_else(|| format!("no `{key}`"));
    let (w, h) = pair("细网格宽高")?;
    let (ox, oy) = pair("原点分子")?;
    let (step, den) = (number("网格步长分子")?, number("分母")?);
    if !(w >= 1.0 && h >= 1.0 && w <= 8192.0 && h <= 8192.0 && step > 0.0 && den >= 1.0) {
        return Err(format!("odd fine grid: {w} x {h}, step {step} / {den}"));
    }
    Ok(Fine { cols: w as usize, rows: h as usize, origin: (ox / den, oy / den), cell: step / den })
}

/// walk.bin（行优先，一格一个字节，1 能走、0 不能走）读成「英雄中心站不住」的格子（true = 站不住）。
pub fn parse_walk(bytes: &[u8], fine: &Fine, side: f64) -> Result<Walls, String> {
    if bytes.len() != fine.cols * fine.rows {
        return Err(format!("{} bytes, the fine grid needs {} x {}", bytes.len(), fine.cols, fine.rows));
    }
    if bytes.iter().any(|b| *b > 1) {
        return Err("a byte other than 0 / 1".to_string());
    }
    let cells = bytes.chunks(fine.cols).map(|r| r.iter().map(|b| *b == 0).collect()).collect();
    Ok(Walls { cells, cell: fine.cell, origin: fine.origin, extent: (side, side), version: String::new(), source: String::new() })
}

/// brush-fine.bin（行优先，一格两个字节 little-endian，0 不是草丛，别的是草丛编号）。
pub fn parse_brush(bytes: &[u8], fine: &Fine) -> Result<Brush, String> {
    if bytes.len() != fine.cols * fine.rows * 2 {
        return Err(format!("{} bytes, the fine grid needs {} x {} x 2", bytes.len(), fine.cols, fine.rows));
    }
    let zones = bytes.chunks_exact(2).map(|b| u16::from_le_bytes([b[0], b[1]])).collect();
    Ok(Brush { zones, cols: fine.cols, rows: fine.rows, cell: fine.cell, origin: fine.origin, source: String::new() })
}

/// 一条候选路径对应的资料文件夹：文件就取它所在的文件夹。
fn data_dir_of(p: &Path) -> PathBuf {
    if p.is_file() {
        p.parent().map(Path::to_path_buf).unwrap_or_default()
    } else {
        p.to_path_buf()
    }
}

/// 资料可能在的地方：`LEAGUE_RIFT_WALLS`，再是游戏 EXE 旁边 mods/tfm2_lol_map_test/地图资料/（或者直接放在 mod 文件夹里）。
fn candidates() -> Vec<PathBuf> {
    let mut out = Vec::new();
    if let Some(p) = std::env::var_os(RIFT_WALLS_ENV) {
        out.push(PathBuf::from(p));
    }
    if let Some(game) = std::env::current_exe().ok().and_then(|e| e.parent().map(Path::to_path_buf)) {
        let m = game.join("mods").join(RIFT_MOD);
        out.push(m.join(RIFT_DATA_DIR));
        out.push(m);
    }
    out
}

/// 第一处读得到墙体坐标.json 的地方的墙（路径可以是文件，也可以是放着它的文件夹）。
pub fn load_rift_walls(paths: &[PathBuf]) -> Result<Walls, String> {
    for p in paths {
        let file = if p.is_file() { p.clone() } else { p.join(RIFT_WALLS_FILE) };
        if let Ok(text) = std::fs::read_to_string(&file) {
            return parse_rift_walls(&text)
                .map(|w| Walls { source: file.display().to_string(), ..w })
                .map_err(|e| format!("Rift walls NOT read from {}: {e} (a map older than 0.1.65?)", file.display()));
        }
    }
    let tried: Vec<String> = paths.iter().map(|p| p.display().to_string()).collect();
    Err(format!("Rift walls not found (looked in {}): copy the map zip's whole tfm2_lol_map_test folder (with its {RIFT_DATA_DIR}) \
                 into mods/ - until then no wall is known on the Rift", tried.join(", ")))
}

/// 墙所在的文件夹里的寻路网格和草丛（同一套细格）。
fn load_fine_in(dir: &Path, side: f64) -> (Result<Walls, String>, Result<Brush, String>) {
    let fine = std::fs::read_to_string(dir.join(RIFT_INFO_FILE))
        .map_err(|_| format!("no {RIFT_INFO_FILE}"))
        .and_then(|t| parse_fine(&t));
    let read = |name: &str| std::fs::read(dir.join(name)).map_err(|_| format!("no {name}"));
    let walk = fine.clone().and_then(|f| read(RIFT_WALK_FILE).and_then(|b| parse_walk(&b, &f, side)));
    let brush = fine.and_then(|f| read(RIFT_BRUSH_FILE).and_then(|b| parse_brush(&b, &f)));
    let at = |name: &str| dir.join(name).display().to_string();
    (walk.map(|w| Walls { source: at(RIFT_WALK_FILE), ..w }), brush.map(|b| Brush { source: at(RIFT_BRUSH_FILE), ..b }))
}

static RIFT: OnceLock<Result<Walls, String>> = OnceLock::new();

/// The Rift's walls, read once (None: no file, or one that did not read - [`rift_status`] says which).
pub fn rift_walls() -> Option<&'static Walls> {
    RIFT.get_or_init(|| load_rift_walls(&candidates())).as_ref().ok()
}

/// 寻路网格和草丛：跟着墙的那个文件夹读一次。
static FINE: OnceLock<(Result<Walls, String>, Result<Brush, String>)> = OnceLock::new();

fn fine_data() -> &'static (Result<Walls, String>, Result<Brush, String>) {
    FINE.get_or_init(|| match rift_walls() {
        Some(w) => load_fine_in(&data_dir_of(Path::new(&w.source)), w.extent.0),
        None => (Err("no walls file".to_string()), Err("no walls file".to_string())),
    })
}

/// The installed map mod's version (its mod.mod_info next to the game's EXE), if any.
fn installed_rift_version() -> Option<String> {
    let game = std::env::current_exe().ok()?.parent()?.to_path_buf();
    let info = std::fs::read_to_string(game.join("mods").join(RIFT_MOD).join("mod.mod_info")).ok()?;
    value_after(info.trim_start_matches('\u{feff}'), "version").and_then(string_value)
}

/// 墙体文件的边长和本模块按的边长不一样：作者又放大缩小过地图，我们的地图边界会不对。
pub fn side_note(side: f64) -> String {
    if (side - RIFT_EXTENT).abs() <= 1.0 {
        format!("map side {side:.0} as expected")
    } else {
        format!("map side {side:.0} but this build expects {RIFT_EXTENT:.0}: ANOTHER MAP VERSION? the map's edges will be off")
    }
}

/// `ground`（墙格那么大的格子）里凡是碰到 `walk` 里站不住的细格的，都关上；返回多关了几格。
pub fn close_unwalkable(ground: &mut Walls, walk: &Walls) -> usize {
    let mut more = 0;
    let e = walk.cell * 0.5 - 1e-6;
    for (y, row) in walk.cells.iter().enumerate() {
        for (x, closed) in row.iter().enumerate() {
            if !closed {
                continue;
            }
            let c = walk.center(x, y);
            for (dx, dy) in [(-e, -e), (e, -e), (-e, e), (e, e)] {
                if let Some((cx, cy)) = ground.cell_of(c.0 + dx, c.1 + dy) {
                    if !ground.cells[cy][cx] {
                        ground.cells[cy][cx] = true;
                        more += 1;
                    }
                }
            }
        }
    }
    more
}

/// 峡谷的地面和它多关的格子数（[`rift_ground`]）。
static GROUND: OnceLock<Option<(Walls, Option<usize>)>> = OnceLock::new();

fn ground_data() -> Option<&'static (Walls, Option<usize>)> {
    GROUND.get_or_init(|| {
        let mut g = rift_walls()?.padded();
        let more = fine_data().0.as_ref().ok().map(|walk| close_unwalkable(&mut g, walk));
        Some((g, more))
    })
    .as_ref()
}

/// 峡谷上英雄中心站不住的地方：墙往外长一格（[`Walls::padded`]，格子和墙一样大，附加包各拷一份也不占地方）。0.1.65 拿作者的
/// 寻路网格 walk.bin 核对过：长一格以后剩下的格子全在寻路网格能走的地方里，一格不差；以后作者的寻路网格要是更严，碰到它站不住
/// 的细格的格子也一起关上（[`close_unwalkable`]）。附加包把英雄的落点、推开、站位放在这外面，峡谷的寻路才接得上。没有墙体文件
/// 时 None。
pub fn rift_ground() -> Option<&'static Walls> {
    ground_data().map(|g| &g.0)
}

/// 峡谷的草丛（作者的 brush-fine.bin）。None：没有资料，附加包的草丛机制在峡谷上照旧关着。
pub fn rift_brush() -> Option<&'static Brush> {
    fine_data().1.as_ref().ok()
}

/// 峡谷的草丛换到墙格那么大的格子上（true = 草丛：那一格里至少四分之一的细格是草丛），读一次。给拿自己格子代码处理草丛的
/// 附加包（奇亚娜的草元素），一格 6545，比细格省得多；要准的（站没站在草丛里）问 [`rift_brush`]。
pub fn rift_bushes() -> Option<&'static Walls> {
    static BUSHES: OnceLock<Option<Walls>> = OnceLock::new();
    BUSHES.get_or_init(|| Some(rift_brush()?.coarse(rift_walls()?, 0.25))).as_ref()
}

/// 这张图上 `p` 在不在草丛里：原版地图不归这里管（各附加包照旧读地图文档的草丛），总是 false。
pub fn in_rift_brush(map: Map, p: (f64, f64)) -> bool {
    map == Map::Rift && rift_brush().is_some_and(|b| b.in_brush(p.0, p.1))
}

/// Can a hero stand at `p` on `map`: anywhere on the game's own map (its add-ons' own checks stand as they were); on
/// the Rift off its ground ([`rift_ground`]: the author's pathing grid), or anywhere inside its square without the
/// walls file.
pub fn stand_ok(map: Map, p: (f64, f64)) -> bool {
    match map {
        Map::Native => true,
        Map::Rift => match rift_ground() {
            Some(g) => !g.is_wall(p.0, p.1),
            None => p.0 >= 0.0 && p.1 >= 0.0 && p.0 <= RIFT_EXTENT && p.1 <= RIFT_EXTENT,
        },
    }
}

/// The spot to send a hero to instead of `p` on `map`: `p` on the game's own map; on the Rift the nearest spot within
/// `max` that the Rift's pathing walks (`p` when it is open, there is none that near, or no walls file).
pub fn stand_spot(map: Map, p: (f64, f64), max: f64) -> (f64, f64) {
    match (map, rift_ground()) {
        (Map::Rift, Some(g)) => g.nearest_open(p, max).unwrap_or(p),
        _ => p,
    }
}

/// One line for an add-on's log the first time it meets the Rift.
pub fn rift_status() -> String {
    let installed = installed_rift_version().unwrap_or_else(|| "? (no mod.mod_info)".to_string());
    match RIFT.get_or_init(|| load_rift_walls(&candidates())) {
        Ok(w) => {
            let ground = match (&fine_data().0, ground_data()) {
                (Ok(walk), Some((_, Some(more)))) => format!(
                    "ground: the walls grown by one cell, checked with the author's pathing grid ({} x {} cells of {:.1}, {} \
                     open): {more} more cells closed", walk.cols(), walk.rows(), walk.cell,
                    walk.cells.iter().flatten().filter(|c| !**c).count()),
                (Err(e), _) => format!("ground: the walls grown by one cell (no pathing grid to check: {e})"),
                _ => "ground: ?".to_string(),
            };
            let brush = match &fine_data().1 {
                Ok(b) => format!("brush: {} patches, {} cells", b.zone_count(), b.count()),
                Err(e) => format!("brush: none ({e}) - brush features off on the Rift"),
            };
            format!("Rift data of map {installed}: {} wall cells in {} x {} cells of {:.1} from ({:.0}, {:.0}), {}, file \
                     version {} ({}); {ground}; {brush}", w.count(), w.cols(), w.rows(), w.cell, w.origin.0, w.origin.1,
                    side_note(w.extent.0), if w.version.is_empty() { "?" } else { &w.version }, w.source)
        }
        Err(e) => format!("{e} (map {installed})"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A 4 x 3 grid of cells of 10 (numerators of 110 over 11) from x = 5, on a 50 x 50 map: walls (1..3, 0), (0, 1),
    /// (3, 2) - one rectangle a cell as the author writes them.
    const SMALL: &str = "\u{feff}{\"版本\": \"t1\", \"对象\": \"静态地形墙\", \"世界边长\": 50, \"坐标分母\": 11,
        \"列\": [\"左x分子\", \"上y分子\", \"右x分子\", \"下y分子\"], \"说明\": \"每项除以11\", \"矩形\": [[165, 0, 275, 110],
        [275, 0, 385, 110], [55, 110, 165, 220], [385, 220, 495, 330]]}";

    #[test]
    fn reads_the_authors_file() {
        let w = parse_rift_walls(SMALL).unwrap();
        assert_eq!((w.cols(), w.rows(), w.count(), w.cell, w.origin), (4, 3, 4, 10.0, (5.0, 0.0)));
        assert_eq!(w.rows_text(), vec![".##.", "#...", "...#"]);
        assert_eq!((w.version.as_str(), w.extent), ("t1", (50.0, 50.0)));
        assert!(w.is_wall(20.0, 5.0) && !w.is_wall(10.0, 5.0) && w.is_wall(40.0, 25.0));
        // off the grid is wall
        assert!(w.is_wall(4.0, 5.0) && w.is_wall(10.0, 31.0) && w.is_wall(f64::NAN, 1.0));
        assert_eq!(w.center(1, 0), (20.0, 5.0));
    }

    #[test]
    fn a_rectangle_off_the_grid_or_odd_sizes_are_refused() {
        // one rectangle 3 numerators off the others' grid
        let moved = SMALL.replace("[275, 0, 385, 110]", "[278, 0, 388, 110]");
        assert!(parse_rift_walls(&moved).unwrap_err().contains("off the grid"), "{:?}", parse_rift_walls(&moved));
        let short = SMALL.replace("[385, 220, 495, 330]", "[385, 220, 495]");
        assert!(parse_rift_walls(&short).unwrap_err().contains("3 numbers"));
        assert!(parse_rift_walls(&SMALL.replace("\"坐标分母\": 11", "\"坐标分母\": 0")).is_err());
        assert!(parse_rift_walls("{}").is_err());
        // the old 0.1.28 file (rows merged, `世界尺寸` / `墙格尺寸_宽高`): not read
        let old = "{\"版本\": \"0.1.28-alpha.game071\", \"世界尺寸\": [1614545, 1614545], \"墙格尺寸_宽高\": [295, 296], \
                   \"矩形\": [[0, 0, 295, 2728, 0, 1611819, 5455]]}";
        assert!(parse_rift_walls(old).is_err());
    }

    /// 0.1.65 的格子：295 x 296 格，每格 72000/11，左边从 36000/11 起（作者的 world_to_fine 是同一个原点）。
    #[test]
    fn the_rifts_grid_sits_where_the_author_says() {
        let json = "{\"世界边长\": 1937454, \"坐标分母\": 11, \"矩形\": [[36000, 0, 108000, 72000], \
                    [21204000, 21240000, 21276000, 21312000]]}";
        let w = parse_rift_walls(json).unwrap();
        assert_eq!((w.cols(), w.rows(), w.count()), (295, 296, 2));
        assert!((w.cell - 72_000.0 / 11.0).abs() < 1e-9, "{}", w.cell);
        assert!((w.origin.0 - 36_000.0 / 11.0).abs() < 1e-9 && w.origin.1 == 0.0, "{:?}", w.origin);
        // the author's formula: wall column = floor((x * 11 - 36000) / 72000)
        let x = 1_930_000.0;
        assert_eq!(w.cell_of(x, 1_936_000.0), Some((((x * 11.0 - 36_000.0) / 72_000.0) as usize, 295)));
        assert!(w.is_wall(x, 1_936_000.0) && !w.is_wall(900_000.0, 900_000.0) && w.is_wall(4_000.0, 1_000.0));
        assert_eq!(side_note(w.extent.0), "map side 1937454 as expected");
        assert!(side_note(1_614_545.0).contains("ANOTHER MAP VERSION"));
    }

    #[test]
    fn the_fine_grid_and_its_two_files() {
        let info = "{\"版本\": \"t\", \"地图边长\": 50, \"细网格宽高\": [4, 2], \"寻路半径\": 5000, \"原点分子\": [55, 0], \
                    \"网格步长分子\": 55, \"分母\": 11}";
        let f = parse_fine(info).unwrap();
        assert_eq!(f, Fine { cols: 4, rows: 2, origin: (5.0, 0.0), cell: 5.0 });
        // walk.bin: row 0 all open but the last, row 1 closed but the first
        let walk = parse_walk(&[1, 1, 1, 0, 1, 0, 0, 0], &f, 50.0).unwrap();
        assert_eq!(walk.rows_text(), vec!["...#", ".###"]);
        assert!(!walk.is_wall(6.0, 1.0) && walk.is_wall(21.0, 1.0) && walk.is_wall(4.0, 1.0));
        assert!(parse_walk(&[1, 1], &f, 50.0).is_err() && parse_walk(&[2; 8], &f, 50.0).is_err());
        // brush-fine.bin: patch 7 at (1, 0) and (2, 0), patch 9 at (3, 1)
        let mut bytes = vec![0u8; 16];
        bytes[2] = 7;
        bytes[4] = 7;
        bytes[14] = 9;
        let b = parse_brush(&bytes, &f).unwrap();
        assert_eq!((b.zone(11.0, 2.0), b.zone(16.0, 2.0), b.zone(21.0, 7.0), b.zone(6.0, 2.0)), (7, 7, 9, 0));
        assert_eq!((b.count(), b.zone_count()), (3, 2));
        assert!(!b.in_brush(-1.0, 2.0) && !b.in_brush(30.0, 2.0) && !b.in_brush(f64::NAN, 0.0));
        // nearest patch cell: from (6, 7) the centre of (1, 0) is (12.5, 2.5)
        assert_eq!(b.nearest((6.0, 7.0), 20.0), Some((12.5, 2.5)));
        assert_eq!(b.nearest((6.0, 7.0), 3.0), None);
        assert_eq!(b.nearest((11.0, 2.0), 3.0), Some((11.0, 2.0)));
        assert_eq!(b.as_walls((50.0, 50.0)).rows_text(), vec![".##.", "...#"]);
        // on cells of 10 from (5, 0): the left cell holds 1 brush cell of 4, the right 2 of 4
        let like = Walls::from_rows(&["..", ".."], 10.0, (5.0, 0.0), (50.0, 50.0));
        assert_eq!(b.coarse(&like, 0.25).rows_text(), vec!["##", ".."]);
        assert_eq!(b.coarse(&like, 0.5).rows_text(), vec![".#", ".."]);
        assert!(parse_brush(&bytes[..15], &f).is_err());
    }

    /// 真的资料（开发机设了 `LEAGUE_RIFT_WALLS` 才跑，CI 上没有）：墙、寻路网格、草丛都读得到，寻路网格是墙外 5000。
    /// 数字是 2026-11-28 起装着的那份：walk.bin / brush-fine.bin 取自 0.1.86 源码，墙体坐标在寻路网格改过的那片按它重算
    /// （D:/TFM2-Workshop/rift_skill/rift_data_0186.py）；0.1.40 那份是 32393 墙、761604 可走、草丛 23016 格、长一格后 46969。
    #[test]
    fn the_real_files_read_when_given() {
        let Some(p) = std::env::var_os(RIFT_WALLS_ENV) else { return };
        let w = load_rift_walls(&[PathBuf::from(p)]).unwrap();
        assert_eq!((w.cols(), w.rows(), w.count()), (295, 296, 32_352));
        assert!((w.extent.0 - RIFT_EXTENT).abs() < 1.0);
        let (walk, brush) = load_fine_in(&data_dir_of(Path::new(&w.source)), w.extent.0);
        let (walk, brush) = (walk.unwrap(), brush.unwrap());
        assert_eq!((walk.cols(), walk.rows()), (1180, 1184));
        assert_eq!(walk.cells.iter().flatten().filter(|c| !**c).count(), 762_101);
        assert_eq!((brush.zone_count(), brush.count()), (24, 22_981));
        // 墙长一格以后剩下的地方全在作者的寻路网格里：一格都不用多关
        let mut ground = w.padded();
        assert_eq!(ground.cells.iter().flatten().filter(|c| !**c).count(), 46_999);
        assert_eq!(close_unwalkable(&mut ground, &walk), 0);
        // every open fine cell is at least the path radius off every wall cell; no brush cell is in a wall
        for (y, row) in walk.cells.iter().enumerate() {
            for (x, closed) in row.iter().enumerate() {
                let c = walk.center(x, y);
                if !closed {
                    let near = [(-1.0, 0.0), (1.0, 0.0), (0.0, -1.0), (0.0, 1.0)];
                    assert!(near.iter().all(|d| !w.is_wall(c.0 + d.0 * RIFT_PATH_RADIUS, c.1 + d.1 * RIFT_PATH_RADIUS)), "{c:?}");
                }
                if brush.zones[y * brush.cols + x] != 0 {
                    assert!(!closed && !w.is_wall(c.0, c.1), "{c:?}");
                }
            }
        }
    }

    #[test]
    fn the_map_from_where_things_stand() {
        assert_eq!(map_of(&[(96_000.0, 864_000.0), (864_000.0, 96_000.0), (480_000.0, 480_000.0)]), Map::Native);
        assert_eq!(map_of(&[(120_000.0, 1_480_000.0)]), Map::Rift);
        assert_eq!(map_of(&[(1_500_000.0, 90_000.0), (10.0, 10.0)]), Map::Rift);
        // 0.1.65 的塔和水晶：红方下路外塔 (1818439, 1352066)、蓝方水晶 (206201, 1724334)
        assert_eq!(map_of(&[(1_818_439.0, 1_352_066.0)]), Map::Rift);
        assert_eq!(map_of(&[(206_201.0, 1_724_334.0)]), Map::Rift);
        // parked out of every map: no hint
        assert_eq!(map_of(&[(3_000_000.0, 10.0), (10.0, 2_100_000.0)]), Map::Native);
        assert_eq!(map_of(&[]), Map::Native);
        assert_eq!(Map::Native.limit(), 1_200_000.0);
        assert_eq!(Map::Rift.center(), (968_727.0, 968_727.0));
        assert!((Map::Rift.scale() - 2.0182).abs() < 0.001);
        assert_eq!(Map::Native.clamp((-5.0, 2_000_000.0)), (0.0, 960_000.0));
        assert_eq!(Map::Native.extent(), NATIVE_EXTENT);
    }

    /// A 5 x 5 grid of cells of 10 with one wall cell in the middle (2, 2).
    fn one_block() -> Walls {
        Walls::from_rows(&[".....", ".....", "..#..", ".....", "....."], 10.0, (0.0, 0.0), (50.0, 50.0))
    }

    #[test]
    fn padded_grows_every_wall_by_one_cell() {
        let p = one_block().padded();
        assert_eq!(p.rows_text(), vec![".....", ".###.", ".###.", ".###.", "....."]);
        // a wall on the border grows inward only
        let edge = Walls::from_rows(&["#..", "...", "..."], 10.0, (0.0, 0.0), (30.0, 30.0)).padded();
        assert_eq!(edge.rows_text(), vec!["##.", "##.", "..."]);
        assert_eq!(p.cell, 10.0);
    }

    #[test]
    fn a_ground_cell_touching_a_closed_pathing_cell_closes() {
        // ground cells of 10; pathing cells of 5 from the same corner: (2, 0) closed lies in ground cell (1, 0)
        let mut ground = Walls::from_rows(&["...", "..."], 10.0, (0.0, 0.0), (30.0, 20.0));
        let walk = Walls::from_rows(&["..#...", "......", "......", "......"], 5.0, (0.0, 0.0), (30.0, 20.0));
        assert_eq!(close_unwalkable(&mut ground, &walk), 1);
        assert_eq!(ground.rows_text(), vec![".#.", "..."]);
        assert_eq!(close_unwalkable(&mut ground, &walk), 0, "already closed");
    }

    #[test]
    fn the_nearest_open_spot() {
        let p = one_block().padded();
        // open already: itself
        assert_eq!(p.nearest_open((5.0, 5.0), 30.0), Some((5.0, 5.0)));
        // the middle of the grown block: out to the nearest open cell (row 0..1 boundary is 10 away from y = 20)
        let q = p.nearest_open((25.0, 12.0), 30.0).unwrap();
        assert!(!p.is_wall(q.0, q.1) && (q.1 - 9.0).abs() < 0.01 && (q.0 - 25.0).abs() < 0.01, "{q:?}");
        // none within the reach asked for
        assert_eq!(p.nearest_open((25.0, 25.0), 2.0), None);
        // a spot off the grid: the nearest cell on it
        let r = p.nearest_open((25.0, -8.0), 30.0).unwrap();
        assert!(!p.is_wall(r.0, r.1), "{r:?}");
    }

    #[test]
    fn a_line_through_a_wall_is_not_clear() {
        let w = one_block();
        assert!(w.line_clear((5.0, 5.0), (45.0, 5.0), 1.0));
        assert!(!w.line_clear((5.0, 25.0), (45.0, 25.0), 1.0));
    }

    #[test]
    fn standing_on_the_game_s_own_map_is_never_refused() {
        assert!(stand_ok(Map::Native, (-5.0, 9_999_999.0)));
        assert_eq!(stand_spot(Map::Native, (1.0, 2.0), 50_000.0), (1.0, 2.0));
        // 原版地图的草丛不归这里管
        assert!(!in_rift_brush(Map::Native, (480_000.0, 480_000.0)));
    }

    #[test]
    fn no_file_no_walls_and_a_line_that_says_where_to_put_it() {
        let e = load_rift_walls(&[PathBuf::from("Z:/no/such/墙体坐标.json")]).unwrap_err();
        assert!(e.contains(RIFT_DATA_DIR) && e.contains(RIFT_MOD), "{e}");
    }
}
