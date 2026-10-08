//! 雷恩加尔草丛附加包：被动「无形掠食者」真的看草丛（用户：「还有草丛可以跳跃 你要记住这游戏地图的草丛」）。
//!
//! 主包保持纯数据：数据读不到地形，主包的扑击在复活、约 3 秒没出手和 R 之后就绪。`mod.override_info` 把主包的雷恩加尔换成
//! `override/` 里的副本（`make_override.py` 用 tools/kit/build_rengar.py 的 `native=1` 生成：去掉「没出手就绪」，
//! `passive` 换成本包的 `league_rengar_bush:bush`），被动每 tick 看：
//!
//! - **站在草丛里**：他活着、脚下的格子是草丛、身上还没有 `league_rengar_ready` 时加上它（永久，攻击距离 +`leap_range`；
//!   下一次攻击由数据打出扑击并去掉）。
//! - **走出草丛**：本包给的 `ready` 在他离开草丛 `grace` tick 后去掉（英雄联盟里出了草丛就不能跳）；复活和 R 给的
//!   （R 期间身上有 `league_rengar_r_on`）不动。
//!
//! 草丛格子从地图自定义钩子读（地图文档的 `bushes`，和卡密尔附加包读 `walls` 一样；每种模式记一张，当前对局取站进墙里的
//! 单位最少的那张）。读不到时退回「敌方队伍看不见他」（草丛之外战争迷雾里也算，日志里写明）。
//! 合集 `league_addons` 里一个 mod 只能有一个地图钩子：合集用 [`BushReader::read`] 和卡密尔的读墙一起调用。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_rengar_bush.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_rengar_bush";
const HERO: &str = "league_rengar";
/// 地图格子的边长（世界单位，卡密尔附加包量过墙格子：30 x 32000 = 960000）。
pub const CELL: f64 = 32_000.0;
/// 地图文档里可能装草丛格子的键。
const BUSH_KEYS: [&str; 4] = ["bushes", "bush", "bush_grid", "bushs"];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_RENGAR_BUSH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_rengar_bush.log");
        }
    }
    PathBuf::from("league_rengar_bush.log")
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

fn n(x: &str) -> String {
    format!("{HERO}_{x}")
}

fn clip(s: &str, max: usize) -> String {
    if s.chars().count() <= max {
        s.to_string()
    } else {
        format!("{}…({} chars)", s.chars().take(max).collect::<String>(), s.chars().count())
    }
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 就绪时的攻击距离加成（扑击的射程）。
    pub leap_range: usize,
    /// 走出草丛多少 tick 后去掉草丛给的就绪。
    pub grace: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { leap_range: 25000, grace: 20 }
    }
}

/// `{"leap_range":25000,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "leap_range" => p.leap_range = v,
            "grace" => p.grace = v,
            _ => {}
        }
    }
    p
}

// ===================== 格子 =====================

/// 一张格子：`cells[y][x]`，非 0 为有（墙或草丛）。
#[derive(Clone, Debug, PartialEq, Default)]
pub struct Grid {
    pub cells: Vec<Vec<i64>>,
}

impl Grid {
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

static MAPS: LazyLock<Mutex<HashMap<u32, MapGrids>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static DUMPED: Mutex<Vec<u32>> = Mutex::new(Vec::new());

/// 当前对局的草丛：站进墙里的单位最少的那张地图（卡密尔附加包的挑法）；只有一张就用它。
pub fn pick_bushes(points: &[(f64, f64)], maps: &[MapGrids]) -> Option<Grid> {
    maps.iter()
        .filter(|m| m.bushes.is_some())
        .min_by_key(|m| m.walls.as_ref().map_or(usize::MAX / 2, |w| points.iter().filter(|p| w.at(p.0, p.1)).count()))
        .and_then(|m| m.bushes.clone())
}

/// 地图自定义钩子：读墙和草丛，不改地图。
pub struct BushReader;

impl BushReader {
    /// 合集里和别的读图钩子一起调用（一个 mod 只能注册一个）。
    pub fn read(mode: Option<GameModeKindV1>, doc: &StableJsonDoc<'_>) {
        let code = mode.map_or(u32::MAX, |m| m.code());
        let walls = doc.get_json("walls").as_deref().and_then(parse_grid);
        let mut found = None;
        for key in BUSH_KEYS {
            if let Some(g) = doc.get_json(key).as_deref().and_then(parse_grid) {
                found = Some((key, g));
                break;
            }
        }
        let first = {
            let mut d = DUMPED.lock().unwrap_or_else(|e| e.into_inner());
            !d.contains(&code) && {
                d.push(code);
                true
            }
        };
        if first {
            let mut out = format!("== map mode={code} ==\n");
            match &found {
                Some((key, g)) => {
                    out += &format!("bushes: key `{key}`, {} rows x {} cols, {} bush cells (# = bush)\n", g.cells.len(),
                                    g.cells.iter().map(|r| r.len()).max().unwrap_or(0), g.count());
                    for (r, row) in g.cells.iter().enumerate() {
                        out += &format!("{r:02} {}\n", row.iter().map(|v| if *v != 0 { '#' } else { '.' }).collect::<String>());
                    }
                }
                None => {
                    let root = doc.get_json("").unwrap_or_else(|| "<none>".into());
                    out += &format!("bushes: NOT FOUND under {BUSH_KEYS:?} - vision fallback; document = {}\n", clip(&root, 1500));
                }
            }
            wlog(out);
        }
        MAPS.lock().unwrap_or_else(|e| e.into_inner()).insert(code, MapGrids { walls, bushes: found.map(|f| f.1) });
    }
}

impl StableMapCustomizer for BushReader {
    fn customize(&self, mode: Option<GameModeKindV1>, doc: &mut StableJsonDoc<'_>) {
        BushReader::read(mode, doc);
    }
}

// ===================== 判断 =====================

/// 这一 tick 该怎么做。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Step {
    Nothing,
    /// 加上就绪。
    Ready,
    /// 去掉草丛给的就绪。
    Drop,
}

/// in_bush：脚下是草丛（或退回时敌方看不见）；has_ready：身上有就绪；mine：就绪是本包给的；out_for：走出草丛几 tick；
/// stalking：R 期间。
pub fn step(p: &Params, alive: bool, in_bush: bool, has_ready: bool, mine: bool, out_for: usize, stalking: bool) -> Step {
    if !alive {
        Step::Nothing
    } else if in_bush && !has_ready {
        Step::Ready
    } else if !in_bush && has_ready && mine && !stalking && out_for >= p.grace {
        Step::Drop
    } else {
        Step::Nothing
    }
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Bush {
    p: Params,
    /// 身上的就绪是本包加的。
    mine: bool,
    /// 走出草丛的 tick 数。
    out_for: usize,
    /// 这场用的草丛（第一次 on_update 时挑）；None = 退回看视野。
    grid: Option<Option<Grid>>,
    was_in: bool,
}

impl StablePassive for Bush {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.mine = false;
        self.out_for = 0;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, team, (x, y)) = (e.is_alive(), e.team(), e.pos());
        if self.grid.is_none() {
            let points: Vec<(f64, f64)> = (0..sim.entity_count())
                .filter_map(|i| sim.get_entity(i))
                .filter(|u| u.is_alive())
                .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
                .collect();
            let maps: Vec<MapGrids> = MAPS.lock().unwrap_or_else(|e| e.into_inner()).values().cloned().collect();
            let g = pick_bushes(&points, &maps);
            wlog(match &g {
                Some(g) => format!("{} BUSHES: {} bush cells", head(sim, me), g.count()),
                None => format!("{} BUSHES: no bush grid - ready while the enemy team cannot see him", head(sim, me)),
            });
            self.grid = Some(g);
        }
        let in_bush = match self.grid.as_ref().and_then(|g| g.as_ref()) {
            Some(g) => g.at(x as f64, y as f64),
            None => !sim.is_visible(1 - team.min(1), me),
        };
        if in_bush != self.was_in && alive {
            wlog(format!("{} {} the bush at ({x}, {y})", head(sim, me), if in_bush { "INTO" } else { "OUT OF" }));
        }
        self.was_in = in_bush;
        self.out_for = if in_bush { 0 } else { self.out_for + 1 };
        let ready = n("ready");
        let has_ready = has_buff(sim, me, &ready);
        if !has_ready {
            self.mine = false;
        }
        let stalking = has_buff(sim, me, &n("r_on"));
        match step(&self.p, alive, in_bush, has_ready, self.mine, self.out_for, stalking) {
            Step::Ready => {
                let mut b = BuffV1::named(&ready);
                b.range = self.p.leap_range;
                sim.add_buff(me, &b);
                self.mine = true;
                wlog(format!("{} READY: the pounce from the bush", head(sim, me)));
            }
            Step::Drop => {
                sim.entity_remove_buff(me, &ready);
                self.mine = false;
                wlog(format!("{} DROP: out of the bush {} ticks", head(sim, me), self.out_for));
            }
            Step::Nothing => {}
        }
    }
}

// ===================== 注册 =====================

/// 本包的被动（合集也用它；地图钩子合集另外合并）。
pub fn register_passive(module: &mut StableMod) {
    module.add_native_passive(format!("{ID}:bush"), Bush::default());
}

/// Everything this add-on registers, into its own DLL's module.
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Rengar: the pounce from the map's bushes) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    register_passive(module);
    host.log(LogLevel::Info, "league_rengar_bush v1 loaded (Rengar: Unseen Predator from the map's bushes).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module.set_map_customizer(BushReader);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params(r#"{"leap_range":25000}"#), Params::default());
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"leap_range":30000,"junk":7}"#).leap_range, 30000);
    }

    #[test]
    fn grids_of_numbers_and_bools() {
        let g = parse_grid("[[0,1],[true,false]]").unwrap();
        assert_eq!(g.cells, vec![vec![0, 1], vec![1, 0]]);
        assert!(g.at(CELL * 1.5, 10.0));
        assert!(g.at(10.0, CELL * 1.2));
        assert!(!g.at(10.0, 10.0));
        assert!(!g.at(CELL * 9.0, 10.0));
        assert_eq!(parse_grid(" [ [ 2.0 , null ] ] ").unwrap().cells, vec![vec![2, 0]]);
        assert!(parse_grid("{}").is_none());
        assert!(parse_grid("[]").is_none());
    }

    #[test]
    fn the_match_map_is_the_one_nobody_stands_in_walls() {
        let a = MapGrids { walls: Some(Grid::from_rows(&["#.", ".."])), bushes: Some(Grid::from_rows(&["..", "#."])) };
        let b = MapGrids { walls: Some(Grid::from_rows(&[".#", "##"])), bushes: Some(Grid::from_rows(&["#.", ".."])) };
        let here = [(CELL * 1.5, CELL * 1.5)];
        assert_eq!(pick_bushes(&here, &[b.clone(), a.clone()]), a.bushes);
        assert_eq!(pick_bushes(&here, &[MapGrids::default()]), None);
    }

    #[test]
    fn ready_in_the_bush_dropped_out_of_it() {
        let p = Params::default();
        assert_eq!(step(&p, true, true, false, false, 0, false), Step::Ready);
        assert_eq!(step(&p, true, true, true, true, 0, false), Step::Nothing);
        assert_eq!(step(&p, true, false, true, true, p.grace - 1, false), Step::Nothing);
        assert_eq!(step(&p, true, false, true, true, p.grace, false), Step::Drop);
        // R's and the respawn's readiness stay
        assert_eq!(step(&p, true, false, true, false, 99, false), Step::Nothing);
        assert_eq!(step(&p, true, false, true, true, 99, true), Step::Nothing);
        assert_eq!(step(&p, false, true, false, false, 0, false), Step::Nothing);
    }
}
