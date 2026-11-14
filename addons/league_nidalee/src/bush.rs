//! 地图的草丛格子（同 league_rengar_bush 的读法：地图自定义钩子读地图文档的 `bushes`，每种模式记一张，当前对局取站进
//! 墙里的单位最少的那张）。本包单独编译时自己注册读图钩子；合集 `league_addons` 一个 mod 只能有一个，合集的 `MapReaders`
//! 调用 [`BushReader::read`]。league_maokai、league_teemo_shrooms 编进的是这同一个文件。
//!
//! 2026-11-06（league_nidalee 0.1.2，画面和预模拟分岔的排查）：读到的地图放在有序的表里（`BTreeMap`，按模式的编号），
//! [`maps`] 按这个顺序给；一样合适时取墙多的（最「具体」的，卡密尔附加包的挑法），再一样取模式编号小的。以前从哈希表里
//! 取、一样合适时谁先谁后看哈希表的顺序——服务器的预模拟和屏幕上的比赛在不同的时候挑，表里多了一种模式就可能换一个顺序，
//! 两边用上不同的草丛。

use std::cmp::Reverse;
use std::collections::BTreeMap;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

use super::wlog;

/// 地图格子的边长（世界单位，卡密尔附加包量过墙格子：30 x 32000 = 960000）。
pub const CELL: f64 = 32_000.0;
/// 地图文档里可能装草丛格子的键。
const BUSH_KEYS: [&str; 4] = ["bushes", "bush", "bush_grid", "bushs"];

/// 一张格子：`cells[y][x]`，非 0 为有（墙或草丛）。
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

/// 一种模式的地图：墙（挑当前对局用）和草丛。
#[derive(Clone, Debug, Default)]
pub struct MapGrids {
    pub walls: Option<Grid>,
    pub bushes: Option<Grid>,
}

/// 读过的地图，按模式的编号（有序：[`maps`] 每次都按同一个顺序给）。
static MAPS: LazyLock<Mutex<BTreeMap<u32, MapGrids>>> = LazyLock::new(|| Mutex::new(BTreeMap::new()));
static SEEN: Mutex<Vec<u32>> = Mutex::new(Vec::new());

/// 当前对局的草丛：站进墙里的单位最少的那张地图（卡密尔附加包的挑法），一样少时取墙多的，再一样取 `maps` 里靠前的
/// （[`maps`] 按模式编号给）；只有一张就用它。每次跑同一局都挑同一张，不看读图的先后、不看哈希表的顺序。
pub fn pick_bushes(points: &[(f64, f64)], maps: &[MapGrids]) -> Option<Grid> {
    maps.iter()
        .filter(|m| m.bushes.is_some())
        .min_by_key(|m| {
            let in_walls = m.walls.as_ref().map_or(usize::MAX / 2, |w| points.iter().filter(|p| w.at(p.0, p.1)).count());
            (in_walls, Reverse(m.walls.as_ref().map_or(0, Grid::count)))
        })
        .and_then(|m| m.bushes.clone())
}

/// 读过的地图（每种模式一张），按模式的编号。
pub fn maps() -> Vec<MapGrids> {
    MAPS.lock().unwrap_or_else(|e| e.into_inner()).values().cloned().collect()
}

/// 地图自定义钩子：读墙和草丛，不改地图。
pub struct BushReader;

impl BushReader {
    /// 合集里和别的读图钩子一起调用（一个 mod 只能注册一个）。
    pub fn read(mode: Option<GameModeKindV1>, doc: &StableJsonDoc<'_>) {
        let code = mode.map_or(u32::MAX, |m| m.code());
        let walls = doc.get_json("walls").as_deref().and_then(parse_grid);
        let found = BUSH_KEYS.iter().find_map(|k| doc.get_json(k).as_deref().and_then(parse_grid).map(|g| (*k, g)));
        let first = {
            let mut d = SEEN.lock().unwrap_or_else(|e| e.into_inner());
            !d.contains(&code) && {
                d.push(code);
                true
            }
        };
        if first {
            wlog(match &found {
                Some((key, g)) => format!("== map mode={code}: bushes under `{key}`, {} bush cells ==", g.count()),
                None => format!("== map mode={code}: bushes NOT FOUND under {BUSH_KEYS:?} - no brush speed =="),
            });
        }
        MAPS.lock().unwrap_or_else(|e| e.into_inner()).insert(code, MapGrids { walls, bushes: found.map(|f| f.1) });
    }
}

impl StableMapCustomizer for BushReader {
    fn customize(&self, mode: Option<GameModeKindV1>, doc: &mut StableJsonDoc<'_>) {
        BushReader::read(mode, doc);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn grids_and_the_match_map() {
        let g = parse_grid("[[0,1],[true,false]]").unwrap();
        assert!(g.at(CELL * 1.5, 10.0));
        assert!(!g.at(10.0, 10.0));
        let a = MapGrids { walls: Some(Grid::from_rows(&["#.", ".."])), bushes: Some(Grid::from_rows(&["..", "#."])) };
        let b = MapGrids { walls: Some(Grid::from_rows(&[".#", "##"])), bushes: Some(Grid::from_rows(&["#.", ".."])) };
        let here = [(CELL * 1.5, CELL * 1.5)];
        assert_eq!(pick_bushes(&here, &[b, a.clone()]), a.bushes);
    }

    #[test]
    fn maps_that_fit_as_well_are_picked_the_same_way_every_time() {
        // 11-06's audit: a tie went by the hash map's order - the server's presims and the match on screen pick at
        // different times (one more mode read can reorder it): another bush grid on each side. Now the map with more walls
        // (the more specific: a lane match stands in no wall of the 5v5 map either), then the lower mode number
        let open = MapGrids { walls: Some(Grid::from_rows(&["..", ".."])), bushes: Some(Grid::from_rows(&["#.", ".."])) };
        let lane = MapGrids { walls: Some(Grid::from_rows(&[".#", "##"])), bushes: Some(Grid::from_rows(&["..", "#."])) };
        let here = [(CELL * 0.5, CELL * 0.5)];
        assert_eq!(pick_bushes(&here, &[open.clone(), lane.clone()]), lane.bushes);
        assert_eq!(pick_bushes(&here, &[lane.clone(), open.clone()]), lane.bushes);
        // the same walls: the first in the list (maps() gives them by mode number)
        let twin = MapGrids { bushes: Some(Grid::from_rows(&["..", ".#"])), ..open.clone() };
        assert_eq!(pick_bushes(&here, &[open.clone(), twin.clone()]), open.bushes);
        MAPS.lock().unwrap().insert(9, twin.clone());
        MAPS.lock().unwrap().insert(2, open.clone());
        assert_eq!(maps().iter().map(|m| m.bushes.clone()).collect::<Vec<_>>(), vec![open.bushes, twin.bushes]);
    }
}
