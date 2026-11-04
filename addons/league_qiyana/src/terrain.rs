//! 地图的地形（用户 2026-10-22「改成按地形：E 落地看附近的草丛、墙、河，附近都没有就退回按局势选。河先查地图数据，没有就
//! 按中间斜带算」）：地图自定义钩子读地图文档的 `walls` 和 `bushes`（league_rengar_bush、league_nidalee 的读法），河流先找
//! `RIVER_KEYS`；地图文档里没有河（2026-10-22 读过的键：walls、bushes、nexus_pos、fountains、towers、camps），5v5 地图就按
//! 中间那条斜带算（[`RIVER_BAND`]）。每种模式记一张，当前对局取站进墙里的单位最少的那张。本包单独编译时自己注册读图钩子；
//! 合集 `league_addons` 一个 mod 只能有一个，合集的 `MapReaders` 调用 [`TerrainReader::read`]。
//!
//! 0.3.0（2026-11-04，照英雄联盟 V26.21）加了三样几何，都是纯计算（单元测试）：
//! - [`nearest_point`]：方圆塑令（W）冲向哪——某种地形离她最近的一点（草丛格子、墙格子和 5v5 地图四边、河道斜带）；
//! - [`windblast`]：惊才绝景的风（R）从她脚下朝一个方向走，碰到第一面墙（墙格子、地图四边、地图外）就停，记下路过的草丛格子和
//!   第一次进河的地方；
//! - [`shockwave`] / [`Shock::caught`]：风停下后冲击波沿它路过的草丛（连着的那一片）、河道（交点前后 `span`）和撞上的那面墙
//!   （连着的墙格子里离停点 `span` 内的，墙边 `border` 内；地图四边是停点前后 `span` 的一段）走，谁在里面、离起点多远。

use std::collections::HashMap;
use std::sync::{Arc, LazyLock, Mutex};

use mod_api_stable::*;

use super::wlog;

pub type Pt = (f64, f64);

/// 地图格子的边长（世界单位，卡密尔附加包量过墙格子：30 x 32000 = 960000）。
pub const CELL: f64 = 32_000.0;
/// 地图的边长（30 格）：外面算墙。
pub const MAP_SIZE: f64 = 960_000.0;
/// 风一步走多远（查墙、草丛、河的步长）。
pub const STEP: f64 = 1_000.0;
const BUSH_KEYS: [&str; 4] = ["bushes", "bush", "bush_grid", "bushs"];
/// 地图文档里可能装河流格子的键。
const RIVER_KEYS: [&str; 6] = ["river", "rivers", "river_grid", "water", "waters", "water_grid"];
/// 5v5 地图的河道：从左上斜到右下，穿过两个大野怪（Morgard (288000, 288000)、Serpen (672000, 672000)，英雄联盟河道里的
/// 大龙小龙），和两边水晶的连线垂直；墙格子里这条斜线两边一格以内没有墙。|x - y| 不过这么多就在河里（垂直于河约 34000）。
pub const RIVER_BAND: f64 = 48_000.0;
/// 5v5 地图四边的墙面（上下的石墙、左右的石堆，league_camille_wall 的 MOBA_BOUNDS）：外面也算墙。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);
/// 冲击波沿草丛走：连着的草丛格子最多这么多格（一片草丛 2-6 格）。
pub const BRUSH_CAP: usize = 16;
/// 冲击波沿墙走：连着的墙格子最多这么多格。
pub const WALL_CAP: usize = 24;

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一张格子：`cells[y][x]`，非 0 为有。
#[derive(Clone, Debug, PartialEq, Default)]
pub struct Grid {
    pub cells: Vec<Vec<i64>>,
}

/// (x, y) 所在的格子（可以在地图外，负数）。
pub fn cell_of(x: f64, y: f64) -> (i64, i64) {
    ((x / CELL).floor() as i64, (y / CELL).floor() as i64)
}

/// (x, y) 到格子 (cx, cy) 的方块的距离（在里面为 0）和方块上离它最近的点。
pub fn to_cell(cx: i64, cy: i64, x: f64, y: f64) -> (f64, Pt) {
    let (x0, y0) = (cx as f64 * CELL, cy as f64 * CELL);
    let p = (x.clamp(x0, x0 + CELL), y.clamp(y0, y0 + CELL));
    (dist(p, (x, y)), p)
}

impl Grid {
    #[cfg(test)]
    pub fn from_rows(rows: &[&str]) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| (c == '#') as i64).collect()).collect() }
    }

    /// 格子 (cx, cy) 有没有（地图外算没有）。
    pub fn has(&self, cx: i64, cy: i64) -> bool {
        cx >= 0 && cy >= 0 && self.cells.get(cy as usize).and_then(|row| row.get(cx as usize)).is_some_and(|v| *v != 0)
    }

    /// 世界坐标落在有的格子里吗（地图外算没有）。
    pub fn at(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return false;
        }
        let (cx, cy) = cell_of(x, y);
        self.has(cx, cy)
    }

    pub fn count(&self) -> usize {
        self.cells.iter().flatten().filter(|v| **v != 0).count()
    }

    /// `reach` 内离 (x, y) 最近的有的格子：(距离，那格上离它最近的点)；在格子里为 0。
    pub fn nearest(&self, x: f64, y: f64, reach: f64) -> Option<(f64, Pt)> {
        let (lx, ly) = cell_of(x - reach, y - reach);
        let (hx, hy) = cell_of(x + reach, y + reach);
        let mut best: Option<(f64, Pt)> = None;
        for cy in ly.max(0)..=hy {
            for cx in lx.max(0)..=hx {
                if !self.has(cx, cy) {
                    continue;
                }
                let (d, p) = to_cell(cx, cy, x, y);
                if d <= reach && best.is_none_or(|b| d < b.0) {
                    best = Some((d, p));
                }
            }
        }
        best
    }

    /// (x, y) 到最近一个有的格子的距离（在格子里为 0），`reach` 以外不算。
    pub fn dist(&self, x: f64, y: f64, reach: f64) -> Option<f64> {
        self.nearest(x, y, reach).map(|(d, _)| d)
    }

    /// 从 `seeds` 起连着（八个方向）的有的格子，`keep` 说留不留，最多 `cap` 格。
    pub fn flood(&self, seeds: &[(i64, i64)], cap: usize, keep: impl Fn(i64, i64) -> bool) -> Vec<(i64, i64)> {
        let mut out: Vec<(i64, i64)> = Vec::new();
        let mut todo: Vec<(i64, i64)> = seeds.iter().copied().filter(|&(x, y)| self.has(x, y)).collect();
        while let Some(c) = todo.pop() {
            if out.contains(&c) || !keep(c.0, c.1) {
                continue;
            }
            out.push(c);
            if out.len() >= cap {
                break;
            }
            for dy in -1..=1 {
                for dx in -1..=1 {
                    let n = (c.0 + dx, c.1 + dy);
                    if (dx, dy) != (0, 0) && self.has(n.0, n.1) && !out.contains(&n) {
                        todo.insert(0, n);
                    }
                }
            }
        }
        out
    }
}

/// 解析二维数组 `[[0,1,...],...]`：数字、`true`/`false`、`null`（算 0）都认，小数取整。
pub fn parse_grid(json: &str) -> Option<Grid> {
    let s = json.as_bytes();
    let mut i = 0;
    let ws = |i: &mut usize| {
        while *i < s.len() && (s[*i] as char).is_whitespace() {
            *i += 1;
        }
    };
    ws(&mut i);
    if s.get(i) != Some(&b'[') {
        return None;
    }
    i += 1;
    let mut rows = Vec::new();
    loop {
        ws(&mut i);
        match s.get(i)? {
            b']' => break,
            b',' => {
                i += 1;
                continue;
            }
            b'[' => i += 1,
            _ => return None,
        }
        let mut row = Vec::new();
        loop {
            ws(&mut i);
            match s.get(i)? {
                b']' => {
                    i += 1;
                    break;
                }
                b',' => i += 1,
                b't' if s[i..].starts_with(b"true") => {
                    row.push(1);
                    i += 4;
                }
                b'f' if s[i..].starts_with(b"false") => {
                    row.push(0);
                    i += 5;
                }
                b'n' if s[i..].starts_with(b"null") => {
                    row.push(0);
                    i += 4;
                }
                _ => {
                    let start = i;
                    while i < s.len() && matches!(s[i], b'-' | b'+' | b'.' | b'e' | b'E' | b'0'..=b'9') {
                        i += 1;
                    }
                    if start == i {
                        return None;
                    }
                    row.push(std::str::from_utf8(&s[start..i]).ok()?.parse::<f64>().ok()? as i64);
                }
            }
        }
        rows.push(row);
    }
    (!rows.is_empty()).then_some(Grid { cells: rows })
}

/// 一个 JSON 对象最外层的键（日志用：地图文档里有什么）。
pub fn top_keys(json: &str) -> Vec<String> {
    let s = json.as_bytes();
    let (mut depth, mut i, mut keys) = (0usize, 0usize, Vec::new());
    let mut expect_key = false;
    while i < s.len() {
        match s[i] {
            b'"' => {
                let start = i + 1;
                i += 1;
                while i < s.len() && s[i] != b'"' {
                    i += if s[i] == b'\\' { 2 } else { 1 };
                }
                if depth == 1 && expect_key {
                    keys.push(String::from_utf8_lossy(&s[start..i.min(s.len())]).into_owned());
                    expect_key = false;
                }
            }
            b'{' | b'[' => {
                depth += 1;
                expect_key = depth == 1 && s[i] == b'{';
            }
            b'}' | b']' => depth = depth.saturating_sub(1),
            b',' if depth == 1 => expect_key = true,
            _ => {}
        }
        i += 1;
    }
    keys
}

/// 一种模式的地图。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct MapGrids {
    /// 模式（`GameModeKindV1::code`，读不到为 u32::MAX）。
    pub mode: u32,
    pub walls: Option<Grid>,
    pub bushes: Option<Grid>,
    /// 地图文档里的河流格子（没有就是 None：5v5 地图按 [`RIVER_BAND`]）。
    pub river: Option<Grid>,
}

/// 地图的一条边（5v5 地图四边的石墙）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Edge {
    Left,
    Top,
    Right,
    Bottom,
}

impl MapGrids {
    pub fn moba(&self) -> bool {
        self.mode == GameModeKindV1::Moba.code()
    }

    /// 墙：墙格子、地图外、5v5 地图四边之外。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 || x >= MAP_SIZE || y >= MAP_SIZE {
            return true;
        }
        if self.moba() {
            let (x0, y0, x1, y1) = MOBA_BOUNDS;
            if x < x0 || y < y0 || x > x1 || y > y1 {
                return true;
            }
        }
        self.walls.as_ref().is_some_and(|g| g.at(x, y))
    }

    pub fn in_brush(&self, x: f64, y: f64) -> bool {
        self.bushes.as_ref().is_some_and(|g| g.at(x, y))
    }

    /// 在河里（地图数据的河格子，或 5v5 地图的斜带）。
    pub fn in_river(&self, x: f64, y: f64) -> bool {
        match &self.river {
            Some(g) => g.at(x, y),
            None => self.moba() && (x - y).abs() <= RIVER_BAND,
        }
    }

    /// (x, y) 离 5v5 地图的哪条边最近、多远（别的模式没有边）。
    pub fn edge(&self, x: f64, y: f64) -> Option<(Edge, f64)> {
        if !self.moba() {
            return None;
        }
        let (x0, y0, x1, y1) = MOBA_BOUNDS;
        [(Edge::Left, x - x0), (Edge::Top, y - y0), (Edge::Right, x1 - x), (Edge::Bottom, y1 - y)]
            .into_iter()
            .map(|(e, d)| (e, d.max(0.0)))
            .min_by(|a, b| a.1.total_cmp(&b.1))
    }
}

static MAPS: LazyLock<Mutex<HashMap<u32, Arc<MapGrids>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static SEEN: Mutex<Vec<u32>> = Mutex::new(Vec::new());

/// 读过的地图（每种模式一张）。
pub fn maps() -> Vec<Arc<MapGrids>> {
    MAPS.lock().unwrap_or_else(|e| e.into_inner()).values().cloned().collect()
}

/// 当前对局的地图：站进墙里的单位最少的那张（卡密尔附加包的挑法）；只有一张就用它。
pub fn pick_map(points: &[Pt], maps: &[Arc<MapGrids>]) -> Option<Arc<MapGrids>> {
    maps.iter()
        .min_by_key(|m| m.walls.as_ref().map_or(usize::MAX / 2, |w| points.iter().filter(|p| w.at(p.0, p.1)).count()))
        .cloned()
}

/// 身边 `reach` 内三种地形各自最近的距离（没有为 None）。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Near {
    pub grass: Option<f64>,
    pub rock: Option<f64>,
    pub river: Option<f64>,
}

/// 河道上离 (x, y) 最近的点和距离（地图数据的河格子，或 5v5 地图的斜带）。
pub fn river_point(m: &MapGrids, x: f64, y: f64, reach: f64) -> Option<(f64, Pt)> {
    match &m.river {
        Some(g) => g.nearest(x, y, reach),
        None if m.moba() => {
            let s = x - y;
            let over = (s.abs() - RIVER_BAND).max(0.0);
            let d = over / std::f64::consts::SQRT_2;
            // step back across the band's edge along (-1, 1) (s > 0) or (1, -1) (s < 0)
            let k = s.signum() * over / 2.0;
            (d <= reach).then_some((d, (x - k, y + k)))
        }
        None => None,
    }
}

/// 地图四边上离 (x, y) 最近的点和距离（5v5 地图）。
pub fn edge_point(m: &MapGrids, x: f64, y: f64, reach: f64) -> Option<(f64, Pt)> {
    let (e, d) = m.edge(x, y)?;
    let (x0, y0, x1, y1) = MOBA_BOUNDS;
    let p = match e {
        Edge::Left => (x0, y),
        Edge::Top => (x, y0),
        Edge::Right => (x1, y),
        Edge::Bottom => (x, y1),
    };
    (d <= reach).then_some((d, p))
}

/// (x, y) 身边的地形：草丛格子、墙格子（5v5 地图还有四边的墙面）、河流（格子，或 5v5 地图的斜带）。
pub fn near(m: &MapGrids, x: f64, y: f64, reach: f64) -> Near {
    let grass = m.bushes.as_ref().and_then(|g| g.dist(x, y, reach));
    let mut rock = m.walls.as_ref().and_then(|g| g.dist(x, y, reach));
    let river = river_point(m, x, y, reach).map(|(d, _)| d);
    if let Some((edge, _)) = edge_point(m, x, y, reach) {
        if rock.is_none_or(|r| edge < r) {
            rock = Some(edge);
        }
    }
    Near { grass, rock, river }
}

/// 地形的种类（方圆塑令拿哪种元素）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Brush,
    River,
    Wall,
}

/// 某种地形离 (x, y) 最近的一点（`reach` 内）：(距离，那一点)。墙算上 5v5 地图的四边。
pub fn nearest_point(m: &MapGrids, kind: Kind, x: f64, y: f64, reach: f64) -> Option<(f64, Pt)> {
    match kind {
        Kind::Brush => m.bushes.as_ref().and_then(|g| g.nearest(x, y, reach)),
        Kind::River => river_point(m, x, y, reach),
        Kind::Wall => {
            let cell = m.walls.as_ref().and_then(|g| g.nearest(x, y, reach));
            let edge = edge_point(m, x, y, reach);
            match (cell, edge) {
                (Some(a), Some(b)) => Some(if b.0 < a.0 { b } else { a }),
                (a, b) => a.or(b),
            }
        }
    }
}

/// 从 `at` 沿 `dir` 走 `reach`（身体半径 `body`）：`Some(走多远)` 路上撞墙（停在墙前 `body` + 1000），`None` 一路没墙
/// （同薇恩附加包的 wall_travel）。
pub fn wall_travel(m: &MapGrids, at: Pt, dir: Pt, reach: f64, body: f64) -> Option<f64> {
    let mut s = STEP;
    while s <= reach + body + 0.5 {
        if m.is_wall(at.0 + dir.0 * s, at.1 + dir.1 * s) {
            return Some((s - body - 1_000.0).max(0.0));
        }
        s += STEP;
    }
    None
}

/// 惊才绝景的风走过的路。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Blast {
    pub from: Pt,
    pub dir: Pt,
    /// 停在哪（撞墙前最后一个空地方，或走满）。
    pub stop: Pt,
    /// 撞上的墙那一点（没撞墙为 None）。
    pub wall: Option<Pt>,
    /// 路过的草丛格子（按先后）和第一次进草丛的地方。
    pub brush: Vec<(i64, i64)>,
    pub brush_at: Option<Pt>,
    /// 第一次进河的地方。
    pub river: Option<Pt>,
}

/// 风从 `from` 沿 `dir` 走 `len`，碰到第一面墙就停（[`MapGrids::is_wall`]），记下路过的草丛和河。
pub fn windblast(m: &MapGrids, from: Pt, dir: Pt, len: f64) -> Blast {
    let mut b = Blast { from, dir, stop: from, ..Blast::default() };
    let mut s = STEP;
    while s <= len + 0.5 {
        let q = (from.0 + dir.0 * s, from.1 + dir.1 * s);
        if m.is_wall(q.0, q.1) {
            b.wall = Some(q);
            break;
        }
        b.stop = q;
        if m.in_brush(q.0, q.1) {
            let c = cell_of(q.0, q.1);
            if !b.brush.contains(&c) {
                b.brush.push(c);
            }
            b.brush_at.get_or_insert(q);
        }
        if b.river.is_none() && m.in_river(q.0, q.1) {
            b.river = Some(q);
        }
        s += STEP;
    }
    b
}

/// 冲击波走的地形。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Shock {
    pub stop: Pt,
    /// 撞上的那面墙：连着的墙格子里离停点 `span` 内的。
    pub wall: Vec<(i64, i64)>,
    /// 撞上的是地图的边：哪条边。
    pub edge: Option<Edge>,
    /// 路过的草丛连着的那几片。
    pub brush: Vec<(i64, i64)>,
    pub brush_at: Option<Pt>,
    /// 进河的地方。
    pub river: Option<Pt>,
}

impl Shock {
    /// 什么地形都没有（风只吹开人）。
    pub fn none(&self) -> bool {
        self.wall.is_empty() && self.edge.is_none() && self.brush.is_empty() && self.river.is_none()
    }

    /// 站在 (x, y)、身体 `r` 的单位被冲击波打到吗：离这股冲击波起点（停点、进草丛、进河的地方）多远；打不到为 None。
    pub fn caught(&self, m: &MapGrids, x: f64, y: f64, r: f64, border: f64, span: f64) -> Option<f64> {
        let at = (x, y);
        let mut best: Option<f64> = None;
        let mut take = |d: f64| {
            if best.is_none_or(|b| d < b) {
                best = Some(d);
            }
        };
        // the wall it reached: within `border` (+ the body) of its cells
        if self.wall.iter().any(|&(cx, cy)| to_cell(cx, cy, x, y).0 <= border + r) {
            take(dist(at, self.stop));
        }
        // the map's edge: within `border` of that edge, `span` along it from the stop point
        if let Some(e) = self.edge {
            let (x0, y0, x1, y1) = MOBA_BOUNDS;
            let (off, along, s_along) = match e {
                Edge::Left => (x - x0, y, self.stop.1),
                Edge::Top => (y - y0, x, self.stop.0),
                Edge::Right => (x1 - x, y, self.stop.1),
                Edge::Bottom => (y1 - y, x, self.stop.0),
            };
            if off <= border + r && (along - s_along).abs() <= span {
                take(dist(at, self.stop));
            }
        }
        // the brush it crossed: in those cells (the centre within half a body of them)
        if let Some(b0) = self.brush_at {
            if self.brush.iter().any(|&(cx, cy)| to_cell(cx, cy, x, y).0 <= r * 0.5) {
                take(dist(at, b0));
            }
        }
        // the river it crossed: in the river, `span` along it from where the wind went in
        if let Some(c) = self.river {
            let inside = match &m.river {
                Some(g) => g.dist(x, y, r * 0.5).is_some(),
                None => ((x - y).abs() - RIVER_BAND) / std::f64::consts::SQRT_2 <= r * 0.5,
            };
            let along = |p: Pt| (p.0 + p.1) / std::f64::consts::SQRT_2;
            let near_enough = match &m.river {
                Some(_) => dist(at, c) <= span,
                None => (along(at) - along(c)).abs() <= span,
            };
            if inside && near_enough {
                take(dist(at, c));
            }
        }
        best
    }

    /// 冲击波的画面放在哪几处（最多 `cap` 处）：墙边、草丛格子的中间、河道上交点前后。
    pub fn spots(&self, span: f64, cap: usize) -> Vec<(Kind, Pt)> {
        let mut out = Vec::new();
        let centre = |(cx, cy): (i64, i64)| ((cx as f64 + 0.5) * CELL, (cy as f64 + 0.5) * CELL);
        if !self.wall.is_empty() || self.edge.is_some() {
            out.push((Kind::Wall, self.stop));
        }
        for &c in self.wall.iter().take(cap / 2) {
            let (_, p) = to_cell(c.0, c.1, self.stop.0, self.stop.1);
            if dist(p, self.stop) > CELL * 0.5 {
                out.push((Kind::Wall, p));
            }
        }
        for &c in &self.brush {
            out.push((Kind::Brush, centre(c)));
        }
        if let Some(c) = self.river {
            let k = span / 2.0 / std::f64::consts::SQRT_2;
            out.push((Kind::River, c));
            out.push((Kind::River, (c.0 + k, c.1 + k)));
            out.push((Kind::River, (c.0 - k, c.1 - k)));
        }
        out.truncate(cap);
        out
    }
}

/// 风停下后冲击波沿哪些地形走（`span`：沿墙、沿河走多远）。
pub fn shockwave(m: &MapGrids, b: &Blast, span: f64) -> Shock {
    let mut s = Shock { stop: b.stop, brush_at: b.brush_at, river: b.river, ..Shock::default() };
    if let Some(w) = b.wall {
        let cell = cell_of(w.0, w.1);
        match m.walls.as_ref().filter(|g| g.has(cell.0, cell.1)) {
            Some(g) => {
                let stop = b.stop;
                s.wall = g.flood(&[cell], WALL_CAP, |cx, cy| to_cell(cx, cy, stop.0, stop.1).0 <= span);
            }
            None => s.edge = m.edge(w.0, w.1).map(|(e, _)| e),
        }
    }
    if let Some(g) = m.bushes.as_ref() {
        s.brush = g.flood(&b.brush, BRUSH_CAP, |_, _| true);
    }
    s
}

/// 地图自定义钩子：读墙、草丛和河流，不改地图。
pub struct TerrainReader;

impl TerrainReader {
    /// 合集里和别的读图钩子一起调用（一个 mod 只能注册一个）。
    pub fn read(mode: Option<GameModeKindV1>, doc: &StableJsonDoc<'_>) {
        let code = mode.map_or(u32::MAX, |m| m.code());
        let grid = |keys: &[&'static str]| keys.iter().find_map(|k| doc.get_json(k).as_deref().and_then(parse_grid).map(|g| (*k, g)));
        let walls = doc.get_json("walls").as_deref().and_then(parse_grid);
        let bushes = grid(&BUSH_KEYS);
        let river = grid(&RIVER_KEYS);
        let first = {
            let mut d = SEEN.lock().unwrap_or_else(|e| e.into_inner());
            !d.contains(&code) && {
                d.push(code);
                true
            }
        };
        let m = MapGrids { mode: code, walls, bushes: bushes.as_ref().map(|b| b.1.clone()), river: river.as_ref().map(|r| r.1.clone()) };
        if first {
            let river_said = match &river {
                Some((k, g)) => format!("river under `{k}`, {} cells", g.count()),
                None => {
                    let keys = top_keys(&doc.get_json("").unwrap_or_default());
                    let band = if m.moba() { format!("the 5v5 diagonal band |x - y| <= {RIVER_BAND}") } else { "none".into() };
                    format!("river NOT in the map data (keys {keys:?}) - {band}")
                }
            };
            wlog(format!(
                "== map mode={code}: walls {}, bushes {}, {river_said} ==",
                m.walls.as_ref().map_or("NOT FOUND".into(), |g| format!("{} cells", g.count())),
                bushes.as_ref().map_or("NOT FOUND".into(), |(k, g)| format!("under `{k}`, {} cells", g.count())),
            ));
        }
        MAPS.lock().unwrap_or_else(|e| e.into_inner()).insert(code, Arc::new(m));
    }
}

impl StableMapCustomizer for TerrainReader {
    fn customize(&self, mode: Option<GameModeKindV1>, doc: &mut StableJsonDoc<'_>) {
        TerrainReader::read(mode, doc);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn moba(walls: &[&str], bushes: &[&str]) -> MapGrids {
        MapGrids { mode: GameModeKindV1::Moba.code(), walls: Some(Grid::from_rows(walls)), bushes: Some(Grid::from_rows(bushes)), river: None }
    }

    /// A 30 x 30 map: `#` at the listed cells.
    fn rows(cells: &[(usize, usize)]) -> Vec<String> {
        (0..30).map(|y| (0..30).map(|x| if cells.contains(&(x, y)) { '#' } else { '.' }).collect()).collect()
    }

    fn map30(walls: &[(usize, usize)], bushes: &[(usize, usize)]) -> MapGrids {
        let w = rows(walls);
        let b = rows(bushes);
        let wr: Vec<&str> = w.iter().map(|s| s.as_str()).collect();
        let br: Vec<&str> = b.iter().map(|s| s.as_str()).collect();
        moba(&wr, &br)
    }

    fn c(cx: f64, cy: f64) -> Pt {
        (cx * CELL, cy * CELL)
    }

    #[test]
    fn distances_to_cells() {
        let g = parse_grid("[[0,0,0],[0,0,1]]").unwrap();
        assert_eq!(g.dist(CELL * 2.5, CELL * 1.5, 1.0), Some(0.0)); // inside
        assert_eq!(g.dist(CELL * 1.5, CELL * 1.5, CELL), Some(CELL * 0.5)); // half a cell to its left side
        assert_eq!(g.dist(CELL * 0.5, CELL * 0.5, CELL), None); // out of reach
        assert_eq!(g.nearest(CELL * 1.5, CELL * 1.5, CELL), Some((CELL * 0.5, (CELL * 2.0, CELL * 1.5))));
    }

    #[test]
    fn the_river_band_and_the_edges() {
        let m = moba(&["....", "....", "....", "...."], &["....", "....", "....", "...."]);
        // on the diagonal: in the river; beside it but within the band: in the river too
        assert_eq!(near(&m, 480_000.0, 480_000.0, 64_000.0).river, Some(0.0));
        assert_eq!(near(&m, 500_000.0, 470_000.0, 64_000.0).river, Some(0.0));
        // far off the diagonal: no river
        assert_eq!(near(&m, 700_000.0, 300_000.0, 64_000.0).river, None);
        // by the map's top edge: a wall (rock)
        assert_eq!(near(&m, 300_000.0, 40_000.0, 64_000.0).rock, Some(14_000.0));
        // another mode has no river band and no edges
        let other = MapGrids { mode: GameModeKindV1::DeathMatch.code(), ..m };
        assert_eq!(near(&other, 480_000.0, 480_000.0, 64_000.0), Near::default());
    }

    #[test]
    fn the_nearest_point_of_each_terrain() {
        let m = map30(&[(10, 10)], &[(14, 14)]);
        // the river: off the band by 20000 on |x - y|: back across its edge along the perpendicular
        let (d, p) = nearest_point(&m, Kind::River, 400_000.0, 332_000.0, 64_000.0).unwrap();
        assert!((d - 20_000.0 / std::f64::consts::SQRT_2).abs() < 1.0);
        assert!(((p.0 - p.1) - RIVER_BAND).abs() < 1.0, "on the band's edge: {p:?}");
        // a wall cell, and the map's edge when it is nearer
        let (d, p) = nearest_point(&m, Kind::Wall, c(9.5, 10.5).0, c(9.5, 10.5).1, 64_000.0).unwrap();
        assert_eq!((d, p), (CELL * 0.5, (CELL * 10.0, CELL * 10.5)));
        let (d, _) = nearest_point(&m, Kind::Wall, 300_000.0, 40_000.0, 64_000.0).unwrap();
        assert_eq!(d, 14_000.0);
        // the brush
        let (d, _) = nearest_point(&m, Kind::Brush, c(14.5, 13.0).0, c(14.5, 13.0).1, 64_000.0).unwrap();
        assert_eq!(d, CELL);
        assert_eq!(nearest_point(&m, Kind::Brush, c(2.5, 2.5).0, c(2.5, 2.5).1, 64_000.0), None);
    }

    #[test]
    fn the_wind_stops_at_the_first_wall() {
        let m = map30(&[(10, 5), (11, 5), (12, 5), (11, 4)], &[]);
        // straight up the column x = 11.5 from row 8.5: the wall cell (11, 5) starts at y = 6 x CELL
        let b = windblast(&m, c(11.5, 8.5), (0.0, -1.0), 200_000.0);
        assert!(b.wall.is_some());
        assert!((b.stop.1 - CELL * 6.0).abs() <= STEP + 1.0, "stops before the wall: {:?}", b.stop);
        // the wall's cells around the stop point (span two cells): the struck one and its neighbours
        let s = shockwave(&m, &b, 2.0 * CELL);
        for cell in [(11, 5), (10, 5), (12, 5), (11, 4)] {
            assert!(s.wall.contains(&cell), "{cell:?} in {:?}", s.wall);
        }
        // by the wall: caught, nearer is nearer; off it: not
        let r = 10_000.0;
        let at = s.caught(&m, c(11.5, 6.3).0, c(11.5, 6.3).1, r, 12_000.0, 2.0 * CELL);
        assert!(at.is_some_and(|d| d < CELL));
        assert_eq!(s.caught(&m, c(11.5, 8.5).0, c(11.5, 8.5).1, r, 12_000.0, 2.0 * CELL), None);
        // no wall within its reach: it goes all the way, nothing struck
        let free = windblast(&m, c(20.5, 20.5), (1.0, 0.0), 60_000.0);
        assert_eq!(free.wall, None);
        assert!((free.stop.0 - (c(20.5, 20.5).0 + 60_000.0)).abs() < 1.0);
        assert!(shockwave(&map30(&[], &[]), &free, 2.0 * CELL).none() || free.river.is_some());
    }

    #[test]
    fn the_map_edge_is_a_wall_and_runs_along() {
        let m = map30(&[], &[]);
        let b = windblast(&m, (300_000.0, 80_000.0), (0.0, -1.0), 100_000.0);
        assert!(b.wall.is_some_and(|w| w.1 < MOBA_BOUNDS.1));
        let s = shockwave(&m, &b, 96_000.0);
        assert_eq!(s.edge, Some(Edge::Top));
        assert!(s.caught(&m, 360_000.0, 40_000.0, 10_000.0, 12_000.0, 96_000.0).is_some());
        assert!(s.caught(&m, 450_000.0, 40_000.0, 10_000.0, 12_000.0, 96_000.0).is_none(), "beyond the span along the edge");
        assert!(s.caught(&m, 300_000.0, 80_000.0, 10_000.0, 12_000.0, 96_000.0).is_none(), "off the edge");
    }

    #[test]
    fn brush_and_river_carry_the_shockwave() {
        // a brush patch of three cells on the way, and one apart that is not touched
        let m = map30(&[], &[(5, 20), (6, 20), (6, 21), (9, 20)]);
        let b = windblast(&m, c(3.5, 20.5), (1.0, 0.0), 80_000.0);
        assert_eq!(b.wall, None);
        assert!(b.brush.contains(&(5, 20)));
        let s = shockwave(&m, &b, 96_000.0);
        assert!(s.brush.contains(&(6, 21)), "the patch's other cell: {:?}", s.brush);
        assert!(!s.brush.contains(&(9, 20)));
        assert!(s.caught(&m, c(6.5, 21.5).0, c(6.5, 21.5).1, 10_000.0, 12_000.0, 96_000.0).is_some());
        assert!(s.caught(&m, c(9.5, 20.5).0, c(9.5, 20.5).1, 10_000.0, 12_000.0, 96_000.0).is_none());
        // across the river band: along it within the span, not beyond
        let r = windblast(&m, (400_000.0, 520_000.0), (1.0, -1.0 + 1e-9), 120_000.0);
        let r = Blast { dir: (std::f64::consts::FRAC_1_SQRT_2, -std::f64::consts::FRAC_1_SQRT_2), ..r };
        assert!(r.river.is_some());
        let s = shockwave(&m, &r, 96_000.0);
        let cpt = s.river.unwrap();
        let k = 60_000.0 / std::f64::consts::SQRT_2;
        assert!(s.caught(&m, cpt.0 + k, cpt.1 + k, 10_000.0, 12_000.0, 96_000.0).is_some());
        let k = 120_000.0 / std::f64::consts::SQRT_2;
        assert!(s.caught(&m, cpt.0 + k, cpt.1 + k, 10_000.0, 12_000.0, 96_000.0).is_none());
    }

    #[test]
    fn walking_to_a_wall() {
        let m = map30(&[(10, 10)], &[]);
        let at = c(8.5, 10.5);
        assert_eq!(wall_travel(&m, at, (1.0, 0.0), 30_000.0, 10_000.0), None);
        let d = wall_travel(&m, at, (1.0, 0.0), 60_000.0, 10_000.0).unwrap();
        assert!((d - (1.5 * CELL - 10_000.0 - 1_000.0)).abs() <= STEP + 1.0, "{d}");
    }

    #[test]
    fn the_match_map_and_the_document_keys() {
        let a = Arc::new(moba(&["#.", ".."], &["..", "#."]));
        let b = Arc::new(moba(&[".#", "##"], &["#.", ".."]));
        assert_eq!(pick_map(&[(CELL * 1.5, CELL * 1.5)], &[b, a.clone()]), Some(a));
        assert_eq!(top_keys(r#"{"walls":[[0,1]],"bushes":[[1]],"towers":[{"pos":[1,2],"ty":"Top"}]}"#),
                   vec!["walls", "bushes", "towers"]);
    }
}
