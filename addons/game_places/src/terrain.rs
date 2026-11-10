//! Which 5v5 map a match is played on - the game's own or Rin's Summoner's Rift - and the Rift's walls (2026-11-10,
//! the user: 「这个地图我们的大小龙兼容吗 还有所有的mod英雄 比如特殊机制墙体交互的 也查一查」「要同时兼容原版地图和这个地图」).
//!
//! **The game's own 5v5 map** is 30 x 30 wall cells of 32000 (960000 square). The add-ons keep their built-in grids
//! for it (league_camille_wall/src/maps.rs) and behave on it exactly as before.
//!
//! **Rin's 召唤师峡谷 · 玩家 α 测试** (third-party mod `tfm2_lol_map_test`, 0.1.28-alpha.game071, game 0.7.1) builds the
//! 5v5 map in its own DLL: terrain, pathing and sight, three lanes with high-ground towers and inhibitors, the camps,
//! 1614545 square. None of it goes through the map document our map customizers read (its DLL holds no document key),
//! so the game never tells an add-on where the Rift's walls are. The map's author publishes them with the mod as
//! `地图资料/墙体坐标.json` (wall rectangles in world units; 295 x 296 cells of 60000/11 from x = 30000/11): [`rift_walls`]
//! reads that file once, from the mod's folder (`mods/tfm2_lol_map_test/地图资料/墙体坐标.json`: the zip's `地图资料`
//! folder copied in) or from the path in `LEAGUE_RIFT_WALLS`. It is never shipped with our mods (it is the author's
//! data). Without it an add-on knows no wall on the Rift and its wall mechanics stay off there - better than hitting
//! the game's own walls where the Rift has none (an add-on that took the old grid treated everything past 960000 as
//! wall). The Rift has no brush data at all: brush features are off there.
//!
//! **Which map** ([`map_of`], [`map_of_sim`]): a tower or a nexus past 1000000 on either axis (and within 1700000:
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
/// The Rift's side (the mod's 墙体坐标.json `世界尺寸`).
pub const RIFT_EXTENT: f64 = 1_614_545.0;
/// A point past this on either axis is on the Rift: the game's own map ends at 960000.
pub const RIFT_FROM: f64 = 1_000_000.0;
/// Farther than this is no place on any map (banished, hidden units): never a hint.
pub const MAP_LIMIT: f64 = 1_700_000.0;
/// A path to the Rift's walls file that wins over the mod's folder (tests, other installs).
pub const RIFT_WALLS_ENV: &str = "LEAGUE_RIFT_WALLS";
/// Where the map's author keeps the walls, under the mod's folder.
pub const RIFT_WALLS_FILES: [&str; 2] = ["地图资料/墙体坐标.json", "墙体坐标.json"];

/// A 5v5 map.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Map {
    /// The game's own (960000 square).
    Native,
    /// Rin's Summoner's Rift (1614545 square).
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

// ===================== 墙体坐标.json =====================

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

/// Reads the map author's 墙体坐标.json: `世界尺寸` [w, h], `墙格尺寸_宽高` [cols, rows] and `矩形` rows of
/// [wall row y, first column x, end column x (excluded), world left, top, right (excluded), bottom (excluded)]. The grid
/// sits in the middle of the map (cell = h / rows): every rectangle's world left edge is checked against it (within 3
/// units), so a file laid out otherwise is refused rather than read wrong.
pub fn parse_rift_walls(json: &str) -> Result<Walls, String> {
    let s = json.trim_start_matches('\u{feff}');
    let pair = |key: &str| -> Result<(f64, f64), String> {
        let v = value_after(s, key).and_then(number_rows).ok_or_else(|| format!("no `{key}`"))?;
        match v.as_slice() {
            [r] if r.len() == 2 => Ok((r[0], r[1])),
            _ => Err(format!("`{key}` is not [a, b]")),
        }
    };
    let (w, h) = pair("世界尺寸")?;
    let (cols, rows) = pair("墙格尺寸_宽高")?;
    if !(w > 0.0 && h > 0.0 && cols >= 1.0 && rows >= 1.0 && cols <= 4096.0 && rows <= 4096.0) {
        return Err(format!("odd sizes: map {w} x {h}, grid {cols} x {rows}"));
    }
    let (cols, rows) = (cols as usize, rows as usize);
    let rects = value_after(s, "矩形").and_then(number_rows).ok_or("no `矩形`")?;
    let cell = h / rows as f64;
    let origin = ((w - cols as f64 * cell) / 2.0, (h - rows as f64 * cell) / 2.0);
    let mut cells = vec![vec![false; cols]; rows];
    for r in &rects {
        let [y, x0, x1, left, ..] = r.as_slice() else { return Err(format!("a rectangle of {} numbers", r.len())) };
        let (y, x0, x1) = (*y as usize, *x0 as usize, *x1 as usize);
        if y >= rows || x0 >= x1 || x1 > cols {
            return Err(format!("rectangle row {y} columns {x0}..{x1} off the {cols} x {rows} grid"));
        }
        if (left - (origin.0 + x0 as f64 * cell)).abs() > 3.0 {
            return Err(format!("rectangle row {y} starts at {left}, the grid says {:.0}", origin.0 + x0 as f64 * cell));
        }
        cells[y][x0..x1].iter_mut().for_each(|c| *c = true);
    }
    let version = value_after(s, "版本").and_then(string_value).unwrap_or_default();
    Ok(Walls { cells, cell, origin, extent: (w, h), version, source: String::new() })
}

/// Where the Rift's walls may be: `LEAGUE_RIFT_WALLS`, then the mod's folder next to the game's EXE.
fn candidates() -> Vec<PathBuf> {
    let mut out = Vec::new();
    if let Some(p) = std::env::var_os(RIFT_WALLS_ENV) {
        out.push(PathBuf::from(p));
    }
    if let Some(game) = std::env::current_exe().ok().and_then(|e| e.parent().map(Path::to_path_buf)) {
        for f in RIFT_WALLS_FILES {
            out.push(game.join("mods").join(RIFT_MOD).join(f));
        }
    }
    out
}

/// Reads the first walls file found.
pub fn load_rift_walls(paths: &[PathBuf]) -> Result<Walls, String> {
    for p in paths {
        if let Ok(text) = std::fs::read_to_string(p) {
            return parse_rift_walls(&text)
                .map(|w| Walls { source: p.display().to_string(), ..w })
                .map_err(|e| format!("Rift walls NOT read from {}: {e}", p.display()));
        }
    }
    let tried: Vec<String> = paths.iter().map(|p| p.display().to_string()).collect();
    Err(format!("Rift walls not found (looked in {}): copy the map zip's 地图资料 folder into mods/{RIFT_MOD}/ - \
                 until then no wall is known on the Rift", tried.join(", ")))
}

static RIFT: OnceLock<Result<Walls, String>> = OnceLock::new();

/// The Rift's walls, read once (None: no file, or one that did not read - [`rift_status`] says which).
pub fn rift_walls() -> Option<&'static Walls> {
    RIFT.get_or_init(|| load_rift_walls(&candidates())).as_ref().ok()
}

/// The installed map mod's version (its mod.mod_info next to the game's EXE), if any.
fn installed_rift_version() -> Option<String> {
    let game = std::env::current_exe().ok()?.parent()?.to_path_buf();
    let info = std::fs::read_to_string(game.join("mods").join(RIFT_MOD).join("mod.mod_info")).ok()?;
    value_after(info.trim_start_matches('\u{feff}'), "version").and_then(string_value)
}

/// How the walls file's version stands to the installed map's (the walls of another version may be off).
pub fn version_note(file: &str, installed: Option<&str>) -> String {
    match installed {
        None => "the map mod's mod.mod_info not found".to_string(),
        Some(v) if v == file => format!("the installed map is the same version {v}"),
        Some(v) => format!("the installed map is {v} but the walls are {file}: STALE? copy the new zip's 地图资料 in"),
    }
}

/// One line for an add-on's log the first time it meets the Rift.
pub fn rift_status() -> String {
    match RIFT.get_or_init(|| load_rift_walls(&candidates())) {
        Ok(w) => format!("Rift walls: {} wall cells in {} x {} cells of {:.1} from ({:.0}, {:.0}), map {:.0} x {:.0}, file \
                          version {} ({}); {}", w.count(), w.cols(), w.rows(), w.cell, w.origin.0, w.origin.1, w.extent.0,
                         w.extent.1, if w.version.is_empty() { "?" } else { &w.version }, w.source,
                         version_note(&w.version, installed_rift_version().as_deref())),
        Err(e) => e.clone(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A 4 x 3 grid on a 40 x 30 map: cells of 10, wall (1..3, 0), (0, 1), (3, 2).
    const SMALL: &str = "\u{feff}{\"版本\": \"t1\", \"世界尺寸\": [40, 30], \"墙格尺寸_宽高\": [4, 3],
        \"矩形列\": [\"墙格行_y\", \"起始格_x\"], \"矩形\": [[0, 1, 3, 10, 0, 30, 10], [1, 0, 1, 0, 10, 10, 20],
        [2, 3, 4, 30, 20, 40, 30]]}";

    #[test]
    fn reads_the_authors_file() {
        let w = parse_rift_walls(SMALL).unwrap();
        assert_eq!((w.cols(), w.rows(), w.count(), w.cell, w.origin), (4, 3, 4, 10.0, (0.0, 0.0)));
        assert_eq!(w.rows_text(), vec![".##.", "#...", "...#"]);
        assert_eq!(w.version, "t1");
        assert!(w.is_wall(15.0, 5.0) && !w.is_wall(5.0, 5.0) && w.is_wall(35.0, 25.0));
        // off the grid is wall
        assert!(w.is_wall(-1.0, 5.0) && w.is_wall(5.0, 31.0) && w.is_wall(f64::NAN, 1.0));
        assert_eq!(w.center(1, 0), (15.0, 5.0));
    }

    #[test]
    fn a_grid_off_the_middle_or_off_its_size_is_refused() {
        // the first rectangle claims to start at 12 where the grid's column 1 starts at 10
        let moved = SMALL.replace("[0, 1, 3, 10, 0, 30, 10]", "[0, 1, 3, 14, 0, 30, 10]");
        assert!(parse_rift_walls(&moved).unwrap_err().contains("starts at 14"));
        let off = SMALL.replace("[2, 3, 4, 30", "[2, 3, 5, 30");
        assert!(parse_rift_walls(&off).unwrap_err().contains("off the"));
        assert!(parse_rift_walls("{}").is_err());
    }

    /// The Rift's own layout: 295 x 296 cells, the grid's left edge 30000/11 in (the author's world_to_fine).
    #[test]
    fn the_rifts_grid_sits_where_the_author_says() {
        let json = format!("{{\"世界尺寸\": [{RIFT_EXTENT}, {RIFT_EXTENT}], \"墙格尺寸_宽高\": [295, 296], \"矩形\": \
                            [[0, 0, 295, 2728, 0, 1611819, 5455], [1, 288, 295, 1573637, 5455, 1611819, 10910]]}}");
        let w = parse_rift_walls(&json).unwrap();
        assert!((w.cell - 60_000.0 / 11.0).abs() < 0.01, "{}", w.cell);
        assert!((w.origin.0 - 30_000.0 / 11.0).abs() < 0.5 && w.origin.1.abs() < 0.5, "{:?}", w.origin);
        // the author's formula: wall column = floor((x * 11 - 30000) / 60000)
        let x = 1_573_700.0;
        assert_eq!(w.cell_of(x, 6_000.0), Some((((x * 11.0 - 30_000.0) / 60_000.0) as usize, 1)));
        assert!(w.is_wall(x, 6_000.0) && !w.is_wall(800_000.0, 6_000.0));
    }

    /// The real file when the developer points at it (`LEAGUE_RIFT_WALLS`); skipped elsewhere (CI has none).
    #[test]
    fn the_real_file_reads_when_given() {
        let Some(p) = std::env::var_os(RIFT_WALLS_ENV) else { return };
        let w = load_rift_walls(&[PathBuf::from(p)]).unwrap();
        assert_eq!((w.cols(), w.rows()), (295, 296));
        assert!(w.count() > 20_000, "{}", w.count());
    }

    #[test]
    fn the_map_from_where_things_stand() {
        assert_eq!(map_of(&[(96_000.0, 864_000.0), (864_000.0, 96_000.0), (480_000.0, 480_000.0)]), Map::Native);
        assert_eq!(map_of(&[(120_000.0, 1_480_000.0)]), Map::Rift);
        assert_eq!(map_of(&[(1_500_000.0, 90_000.0), (10.0, 10.0)]), Map::Rift);
        // parked out of every map: no hint
        assert_eq!(map_of(&[(3_000_000.0, 10.0), (10.0, 2_000_000.0)]), Map::Native);
        assert_eq!(map_of(&[]), Map::Native);
        assert_eq!(Map::Native.limit(), 1_200_000.0);
        assert_eq!(Map::Rift.center(), (807_272.5, 807_272.5));
        assert!((Map::Rift.scale() - 1.6818).abs() < 0.001);
        assert_eq!(Map::Native.clamp((-5.0, 2_000_000.0)), (0.0, 960_000.0));
    }

    #[test]
    fn the_walls_version_against_the_installed_map() {
        assert!(version_note("0.1.28", Some("0.1.28")).contains("same version"));
        assert!(version_note("0.1.28", Some("0.1.29")).contains("STALE"));
        assert!(version_note("0.1.28", None).contains("not found"));
    }

    #[test]
    fn no_file_no_walls_and_a_line_that_says_where_to_put_it() {
        let e = load_rift_walls(&[PathBuf::from("Z:/no/such/墙体坐标.json")]).unwrap_err();
        assert!(e.contains("地图资料") && e.contains(RIFT_MOD), "{e}");
    }
}
