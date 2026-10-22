//! 地图的地形（用户 2026-10-22「改成按地形：E 落地看附近的草丛、墙、河，附近都没有就退回按局势选。河先查地图数据，没有就
//! 按中间斜带算」）：地图自定义钩子读地图文档的 `walls` 和 `bushes`（league_rengar_bush、league_nidalee 的读法），河流先找
//! `RIVER_KEYS`；地图文档里没有河（2026-10-22 读过的键：walls、bushes、nexus_pos、fountains、towers、camps），5v5 地图就按
//! 中间那条斜带算（[`RIVER_BAND`]）。每种模式记一张，当前对局取站进墙里的单位最少的那张。本包单独编译时自己注册读图钩子；
//! 合集 `league_addons` 一个 mod 只能有一个，合集的 `MapReaders` 调用 [`TerrainReader::read`]。

use std::collections::HashMap;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

use super::wlog;

/// 地图格子的边长（世界单位，卡密尔附加包量过墙格子：30 x 32000 = 960000）。
pub const CELL: f64 = 32_000.0;
const BUSH_KEYS: [&str; 4] = ["bushes", "bush", "bush_grid", "bushs"];
/// 地图文档里可能装河流格子的键。
const RIVER_KEYS: [&str; 6] = ["river", "rivers", "river_grid", "water", "waters", "water_grid"];
/// 5v5 地图的河道：从左上斜到右下，穿过两个大野怪（Morgard (288000, 288000)、Serpen (672000, 672000)，英雄联盟河道里的
/// 大龙小龙），和两边水晶的连线垂直；墙格子里这条斜线两边一格以内没有墙。|x - y| 不过这么多就在河里（垂直于河约 34000）。
pub const RIVER_BAND: f64 = 48_000.0;
/// 5v5 地图四边的墙面（上下的石墙、左右的石堆，league_camille_wall 的 MOBA_BOUNDS）：外面也算墙。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);

/// 一张格子：`cells[y][x]`，非 0 为有。
#[derive(Clone, Debug, PartialEq, Default)]
pub struct Grid {
    pub cells: Vec<Vec<i64>>,
}

impl Grid {
    #[cfg(test)]
    pub fn from_rows(rows: &[&str]) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| (c == '#') as i64).collect()).collect() }
    }

    /// 世界坐标落在有的格子里吗（地图外算没有）。
    pub fn at(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return false;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|row| row.get(cx)).is_some_and(|v| *v != 0)
    }

    pub fn count(&self) -> usize {
        self.cells.iter().flatten().filter(|v| **v != 0).count()
    }

    /// (x, y) 到最近一个有的格子的距离（在格子里为 0），`reach` 以外不算。
    pub fn dist(&self, x: f64, y: f64, reach: f64) -> Option<f64> {
        let lo = |v: f64| ((v - reach) / CELL).floor().max(0.0) as usize;
        let hi = |v: f64| ((v + reach) / CELL).floor().max(0.0) as usize;
        let mut best: Option<f64> = None;
        for cy in lo(y)..=hi(y) {
            let Some(row) = self.cells.get(cy) else { break };
            for cx in lo(x)..=hi(x).min(row.len().saturating_sub(1)) {
                if row[cx] == 0 {
                    continue;
                }
                let (x0, y0) = (cx as f64 * CELL, cy as f64 * CELL);
                let dx = (x0 - x).max(x - x0 - CELL).max(0.0);
                let dy = (y0 - y).max(y - y0 - CELL).max(0.0);
                let d = (dx * dx + dy * dy).sqrt();
                if d <= reach && best.is_none_or(|b| d < b) {
                    best = Some(d);
                }
            }
        }
        best
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

impl MapGrids {
    fn moba(&self) -> bool {
        self.mode == GameModeKindV1::Moba.code()
    }
}

static MAPS: LazyLock<Mutex<HashMap<u32, MapGrids>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static SEEN: Mutex<Vec<u32>> = Mutex::new(Vec::new());

/// 读过的地图（每种模式一张）。
pub fn maps() -> Vec<MapGrids> {
    MAPS.lock().unwrap_or_else(|e| e.into_inner()).values().cloned().collect()
}

/// 当前对局的地图：站进墙里的单位最少的那张（卡密尔附加包的挑法）；只有一张就用它。
pub fn pick_map(points: &[(f64, f64)], maps: &[MapGrids]) -> Option<MapGrids> {
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

/// (x, y) 身边的地形：草丛格子、墙格子（5v5 地图还有四边的墙面）、河流（格子，或 5v5 地图的斜带）。
pub fn near(m: &MapGrids, x: f64, y: f64, reach: f64) -> Near {
    let grass = m.bushes.as_ref().and_then(|g| g.dist(x, y, reach));
    let mut rock = m.walls.as_ref().and_then(|g| g.dist(x, y, reach));
    let river = match &m.river {
        Some(g) => g.dist(x, y, reach),
        None if m.moba() => {
            let d = ((x - y).abs() - RIVER_BAND).max(0.0) / std::f64::consts::SQRT_2;
            (d <= reach).then_some(d)
        }
        None => None,
    };
    if m.moba() {
        let (x0, y0, x1, y1) = MOBA_BOUNDS;
        let edge = (x - x0).min(y - y0).min(x1 - x).min(y1 - y).max(0.0);
        if edge <= reach && rock.is_none_or(|r| edge < r) {
            rock = Some(edge);
        }
    }
    Near { grass, rock, river }
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
        MAPS.lock().unwrap_or_else(|e| e.into_inner()).insert(code, m);
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

    #[test]
    fn distances_to_cells() {
        let g = parse_grid("[[0,0,0],[0,0,1]]").unwrap();
        assert_eq!(g.dist(CELL * 2.5, CELL * 1.5, 1.0), Some(0.0)); // inside
        assert_eq!(g.dist(CELL * 1.5, CELL * 1.5, CELL), Some(CELL * 0.5)); // half a cell to its left side
        assert_eq!(g.dist(CELL * 0.5, CELL * 0.5, CELL), None); // out of reach
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
    fn the_match_map_and_the_document_keys() {
        let a = moba(&["#.", ".."], &["..", "#."]);
        let b = moba(&[".#", "##"], &["#.", ".."]);
        assert_eq!(pick_map(&[(CELL * 1.5, CELL * 1.5)], &[b, a.clone()]), Some(a));
        assert_eq!(top_keys(r#"{"walls":[[0,1]],"bushes":[[1]],"towers":[{"pos":[1,2],"ty":"Top"}]}"#),
                   vec!["walls", "bushes", "towers"]);
    }
}
