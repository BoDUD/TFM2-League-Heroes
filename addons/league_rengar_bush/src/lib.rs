//! 雷恩加尔草丛附加包：被动「无形掠食者」真的看草丛（用户：「还有草丛可以跳跃 你要记住这游戏地图的草丛」）。
//!
//! 主包保持纯数据：数据读不到地形，主包的扑击在复活、约 3 秒没出手和 R 之后就绪。`mod.override_info` 把主包的雷恩加尔换成
//! `override/` 里的副本（`make_override.py` 用 tools/kit/build_rengar.py 的 `native=1` 生成：主包的就绪全留着，`passive`
//! 换成本包的 `league_rengar_bush:bush`，普攻读 `ready` 之前先过本包的原生效果 `league_rengar_bush:aim`）。
//!
//! 0.2.0（玩家 2026-11-03：「他的跳跃机制非常不稳定，有时候会跳，有时候不跳」）：0.1.x 的副本去掉了「没出手就绪」，就绪只剩
//! 复活后的第一下（多半扑在野怪、小兵身上）、R 和草丛；AI 不会在草丛里等人，只是路过（同一张格子，奈德丽附加包 11-02 的
//! 日志：一分多钟十来次，每次 1–45 tick），出了草丛 20 tick 就收回，一场架开头跳不跳全看他刚才有没有路过草丛。现在「脱战
//! 3 秒就绪」回来了，不在打架时草丛给的就绪也留到用掉，打塔不再白扑。
//!
//! 被动每 tick 看：
//!
//! - **站在草丛里**：他活着、脚下的格子是草丛、身上没有就绪（`league_rengar_ready`，或在塔前收起的
//!   `league_rengar_ready_kept`）时加上 `ready`（永久，攻击距离 +`leap_range`；下一次攻击由数据打出扑击并去掉）。
//! - **打架时走出草丛**：本包给的就绪在他离开草丛 `grace` tick 后去掉（英雄联盟里出了草丛就不能跳）——只在打架时，即身上
//!   有数据的 `league_rengar_fight`（3 秒内出过手）。不在打架时手上的就绪就是「脱战 3 秒」那一份（主包的规矩），留到用掉；
//!   R 期间（`league_rengar_r_on`）是 R 给的，也不动。
//! - **艾翁的草丛**：身上有 `league_ivern_in_brush`（league_ivern 给站在艾翁草丛里的英雄挂的 2 tick 标记，每 tick 续上，
//!   两边都算）也算站在草丛里（英雄联盟里雷恩加尔能从艾翁的草丛扑出来）。
//!
//! 原生效果 `aim`（普攻出手、数据读 `ready` 之前，对普攻的目标跑一次）：目标是塔或水晶时把 `ready` 收成没有射程加成的
//! `ready_kept`，这一下照常挥刀——扑击落地那一下只打 `EnemyWithoutTower`，以前扑到塔上一点伤害都没有，就绪也白丢了；收起后
//! 也不会顶着 48000 的射程一直隔空砍塔。之后第一下打单位时换回 `ready`，照常扑出去（英雄联盟的扑击也不对防御塔）。原生效果
//! 改的 buff 数据同一 tick 就读得到（加里奥附加包 0.7.0 的日志：`entrance` 加的 1 tick 标记，数据紧接着读到、引导、落地）。
//!
//! 草丛格子从地图自定义钩子读（地图文档的 `bushes`，和卡密尔附加包读 `walls` 一样；每种模式记一张，当前对局取站进墙里的
//! 单位最少的那张，一样少取最后读到的）。那张地图没有草丛就没有草丛给的扑击（0.1.x 会借别的模式地图的格子）；哪张地图都
//! 读不到草丛时退回「敌方队伍看不见他」（草丛之外战争迷雾里也算，日志里写明）。
//! 合集 `league_addons` 里一个 mod 只能有一个地图钩子：合集用 [`BushReader::read`] 和卡密尔的读墙一起调用。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_rengar_bush.log`，每次启动游戏重写，上一次的留在 .prev.log。
//! 每种行先写 `LOG_FIRST` 条、之后每 `LOG_EVERY` 条一条（屏幕上那场每条都写）：`INTO` / `OUT OF`（进出草丛）、`READY`、
//! `DROP`、`AIM`（塔前收起 / 拿回）、`POUNCE`（扑出去了：谁给的就绪、离最近的敌方英雄多远）、`TALLY`（每场每 3 分钟一行
//! 这一场的累计）。

use std::cmp::Reverse;
use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_rengar_bush";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_rengar_bush") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 数据的就绪：攻击距离 +`leap_range`，下一次攻击是扑击（复活后第一下、脱战 3 秒、R，和本包的草丛都给它）。
const READY: &str = "league_rengar_ready";
/// 在塔前收起的就绪（没有射程加成）：`aim` 在他下一次打单位时换回 [`READY`]。
const KEPT: &str = "league_rengar_ready_kept";
/// R 的伪装期间。
const R_ON: &str = "league_rengar_r_on";
/// 他 3 秒内出过手（数据的每个动作续上 180 tick）：在打架。
const FIGHT: &str = "league_rengar_fight";
/// 这条命出过第一下（数据的复活就绪用掉了）。
const INIT: &str = "league_rengar_init";
/// league_ivern 给站在艾翁草丛里的英雄挂的标记（用户 2026-10-22：「还有艾翁的W能触发雷恩加尔的跳 别忘了」）。
const IVERN_BRUSH: &str = "league_ivern_in_brush";
/// 地图格子的边长（世界单位，卡密尔附加包量过墙格子：30 x 32000 = 960000）。
pub const CELL: f64 = 32_000.0;
/// 地图文档里可能装草丛格子的键。
const BUSH_KEYS: [&str; 4] = ["bushes", "bush", "bush_grid", "bushs"];
/// 扑击够得着的距离（数据里扑击冲刺的 `range`：普攻 23000 + `leap_range` 25000 + 两个身体 20000）：扑出去时最近的敌方英雄
/// 在这以内，`TALLY` 记作扑在英雄跟前。
pub const NEAR: f64 = 68_000.0;
/// 每场每这么多 tick（3 分钟）写一行 `TALLY`。
pub const TALLY_EVERY: usize = 3 * 60 * 60;
/// 每种日志行先写这么多条……
const LOG_FIRST: usize = 40;
/// ……之后每这么多条写一条（服务器一晚上预模拟几百场）；屏幕上那场每条都写。
const LOG_EVERY: usize = 100;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

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

/// 这一种行的第几条，该写时给出（先写 `LOG_FIRST` 条、之后每 `LOG_EVERY` 条一条；屏幕上那场 `shown` 每条都写）。
fn counted(kind: &str, shown: bool) -> Option<usize> {
    static COUNTS: LazyLock<Mutex<HashMap<String, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let k = c.entry(kind.to_string()).or_insert(0);
    *k += 1;
    (shown || *k <= LOG_FIRST || *k % LOG_EVERY == 0).then_some(*k)
}

/// 屏幕上那场（客户端的观战、旁观、回放），不是服务器的预模拟。
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
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
    /// 打架时走出草丛多少 tick 后去掉草丛给的就绪。
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

/// 一种模式的地图：墙（挑当前对局用）、草丛，和它是第几次读到的（地图钩子在每场建好时跑，一样合适时取最后读到的）。
#[derive(Clone, Debug, Default)]
pub struct MapGrids {
    pub walls: Option<Grid>,
    pub bushes: Option<Grid>,
    pub seq: u64,
}

static MAPS: LazyLock<Mutex<HashMap<u32, MapGrids>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static DUMPED: Mutex<Vec<u32>> = Mutex::new(Vec::new());
/// 读过几次地图（[`MapGrids::seq`]）。
static READS: AtomicU64 = AtomicU64::new(0);

/// 这一场的草丛。
#[derive(Clone, Debug, PartialEq)]
pub enum Bushes {
    /// 这一场地图的草丛格子。
    Grid(Grid),
    /// 这一场的地图没有草丛（别的模式的地图有）：没有草丛给的扑击。
    Absent,
    /// 哪张地图都没读到草丛（键名不认得）：退回「敌方队伍看不见他」。
    Vision,
}

/// 当前对局的地图：站进墙里的单位最少的那张（卡密尔附加包的挑法，没有墙的地图排最后），一样少取最后读到的；用它的草丛。
/// 它没有草丛就是没有——不借别的模式的（0.1.x 只在有草丛的地图里挑，没有草丛的地图上会用 5v5 的格子）。
pub fn pick_bushes(points: &[(f64, f64)], maps: &[MapGrids]) -> Bushes {
    let in_walls =
        |m: &MapGrids| m.walls.as_ref().map_or(usize::MAX / 2, |w| points.iter().filter(|p| w.at(p.0, p.1)).count());
    match maps.iter().min_by_key(|m| (in_walls(m), Reverse(m.seq))) {
        Some(MapGrids { bushes: Some(g), .. }) => Bushes::Grid(g.clone()),
        Some(_) if maps.iter().any(|m| m.bushes.is_some()) => Bushes::Absent,
        _ => Bushes::Vision,
    }
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
                    out += &format!("bushes: NOT FOUND under {BUSH_KEYS:?} - no pounce from bushes on this map (the vision \
                                     fallback only when no map has any); document = {}\n", clip(&root, 1500));
                }
            }
            wlog(out);
        }
        let seq = READS.fetch_add(1, Ordering::Relaxed) + 1;
        MAPS.lock().unwrap_or_else(|e| e.into_inner()).insert(code, MapGrids { walls, bushes: found.map(|f| f.1), seq });
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

/// 身上的就绪还归不归本包管（归本包管的，打架时出了草丛 `grace` tick 收回）：没有就绪了、R 期间（R 给的那份）、不在打架
/// （手上这份就是「脱战 3 秒」那一份，主包的规矩：留到用掉，开打先放 W、E 也不收）都不归了。
pub fn still_mine(mine: bool, has_ready: bool, stalking: bool, fighting: bool) -> bool {
    mine && has_ready && !stalking && fighting
}

/// in_bush：脚下是草丛（或退回时敌方看不见）；has_ready：身上有就绪（`ready` 或 `ready_kept`）；mine：就绪归本包管
/// （[`still_mine`]）；out_for：走出草丛几 tick；fighting：在打架（身上有 `league_rengar_fight`）。
pub fn step(p: &Params, alive: bool, in_bush: bool, has_ready: bool, mine: bool, out_for: usize, fighting: bool) -> Step {
    if !alive {
        Step::Nothing
    } else if in_bush && !has_ready {
        Step::Ready
    } else if !in_bush && has_ready && mine && fighting && out_for >= p.grace {
        Step::Drop
    } else {
        Step::Nothing
    }
}

/// 身上这份就绪是谁给的（`POUNCE`、`TALLY` 写）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum Source {
    /// 地图的草丛（本包）。
    Bush,
    /// 艾翁的草丛（本包）。
    Ivern,
    /// R（数据）。
    Ult,
    /// 脱战 3 秒（数据）。
    Quiet,
    /// 这条命的第一下（数据）。
    Respawn,
    /// 看不出来（数据）。
    #[default]
    Other,
}

impl Source {
    /// [`Tally::pounces`] 的顺序。
    pub const ALL: [Source; 6] = [Source::Bush, Source::Ivern, Source::Ult, Source::Quiet, Source::Respawn, Source::Other];

    pub fn label(self) -> &'static str {
        match self {
            Source::Bush => "a bush",
            Source::Ivern => "Ivern's brush",
            Source::Ult => "R",
            Source::Quiet => "3 s out of combat",
            Source::Respawn => "the respawn",
            Source::Other => "the data",
        }
    }
}

/// 数据给的就绪是哪一份：这条命的第一下刚出手（`first_swing`）是复活的，R 期间是 R 的，不在打架是脱战 3 秒的。
pub fn data_source(first_swing: bool, stalking: bool, fighting: bool) -> Source {
    if first_swing {
        Source::Respawn
    } else if stalking {
        Source::Ult
    } else if !fighting {
        Source::Quiet
    } else {
        Source::Other
    }
}

/// 普攻出手时（原生效果 `aim`）就绪怎么换。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Aim {
    Nothing,
    /// 打塔或水晶：去掉 `ready`、收起成 `ready_kept`（`dup`：已经收着一份，只去掉 `ready`——同名的就绪会叠）。
    Keep { dup: bool },
    /// 打单位：去掉 `ready_kept`、换回 `ready`（`dup`：`ready` 本来就在，只去掉 `ready_kept`）。
    Back { dup: bool },
}

/// at_structure：普攻的目标是塔或水晶；has_ready / has_kept：身上有 `ready` / `ready_kept`。
pub fn aim_step(at_structure: bool, has_ready: bool, has_kept: bool) -> Aim {
    match (at_structure, has_ready, has_kept) {
        (true, true, kept) => Aim::Keep { dup: kept },
        (false, ready, true) => Aim::Back { dup: ready },
        _ => Aim::Nothing,
    }
}

/// 塔和水晶：扑击落地那一下（`EnemyWithoutTower`）打不到。
pub fn structure(kind: Option<EntityKindV1>) -> bool {
    matches!(kind, Some(EntityKindV1::Tower | EntityKindV1::Nexus))
}

/// 一场的计数（每场每 `TALLY_EVERY` tick 写一行累计，有变化才写）。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Tally {
    /// 扑出去的，按就绪是谁给的（[`Source::ALL`] 的顺序）。
    pub pounces: [usize; 6],
    /// 其中扑出去时最近的敌方英雄在 `NEAR` 以内的。
    pub near: usize,
    /// 本包给的就绪：地图的草丛、艾翁的草丛。
    pub bush: usize,
    pub ivern: usize,
    /// 打架时出了草丛收回的。
    pub dropped: usize,
    /// 在塔前收起的。
    pub kept: usize,
}

impl Tally {
    pub fn pounce(&mut self, source: Source, near: bool) {
        self.pounces[source as usize] += 1;
        self.near += near as usize;
    }

    pub fn line(&self) -> String {
        let total: usize = self.pounces.iter().sum();
        let by: Vec<String> =
            Source::ALL.iter().zip(self.pounces).filter(|(_, k)| *k > 0).map(|(s, k)| format!("{} {k}", s.label())).collect();
        format!(
            "{total} pounces ({}), {} with an enemy champion within {NEAR:.0}; readied in bushes {} (Ivern's brush {}), \
             dropped {} after leaving one in a fight, kept {} at towers",
            if by.is_empty() { "none".to_string() } else { by.join(", ") },
            self.near,
            self.bush,
            self.ivern,
            self.dropped,
            self.kept
        )
    }
}

/// 他身上本包要看的 buff（一次看完）。
#[derive(Clone, Copy, Debug, Default)]
struct Marks {
    ready: bool,
    kept: bool,
    stalking: bool,
    fighting: bool,
    init: bool,
    ivern: bool,
}

fn marks(sim: &StableSim<'_>, me: usize) -> Marks {
    let mut m = Marks::default();
    if let Some(e) = sim.get_entity(me) {
        for b in (0..e.buff_count()).filter_map(|i| e.buff_at(i)) {
            match b.name() {
                READY => m.ready = true,
                KEPT => m.kept = true,
                R_ON => m.stalking = true,
                FIGHT => m.fighting = true,
                INIT => m.init = true,
                IVERN_BRUSH => m.ivern = true,
                _ => {}
            }
        }
    }
    m
}

/// 离 `at` 最近的活着的敌方英雄有多远（一个都没有就是 None）。
fn nearest_enemy_champion(sim: &StableSim<'_>, team: usize, at: (f64, f64)) -> Option<f64> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_champion() && u.is_alive() && u.team() != team)
        .map(|u| (u.pos().0 as f64 - at.0).hypot(u.pos().1 as f64 - at.1))
        .min_by(|a, b| a.total_cmp(b))
}

// ===================== 原生效果：塔不扑 =====================

/// 原生效果 `aim`：数据普攻出手、读 `ready` 之前，对普攻的目标跑一次（[`aim_step`]）。
fn aim(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    let Some((at_structure, what)) = sim.get_entity(target).map(|t| {
        let what = t.name().unwrap_or_else(|| t.kind().map_or_else(|| "unit".to_string(), |k| format!("{k:?}")));
        (t.is_tower() || structure(t.kind()), format!("{what}#{target}"))
    }) else {
        return;
    };
    let m = marks(sim, me);
    match aim_step(at_structure, m.ready, m.kept) {
        Aim::Keep { dup } => {
            sim.entity_remove_buff(me, READY);
            if !dup {
                sim.add_buff(me, &BuffV1::named(KEPT));
            }
            if let Some(k) = counted("aim", on_screen(sim)) {
                wlog(format!("{} AIM {what}: a tower - a plain swing, the pounce kept for the next unit #{k}", head(sim, me)));
            }
        }
        Aim::Back { dup } => {
            sim.entity_remove_buff(me, KEPT);
            if !dup {
                let mut b = BuffV1::named(READY);
                b.range = Params::default().leap_range;
                sim.add_buff(me, &b);
            }
            if let Some(k) = counted("aim", on_screen(sim)) {
                wlog(format!("{} AIM {what}: the pounce kept at a tower goes out #{k}", head(sim, me)));
            }
        }
        Aim::Nothing => {}
    }
}

struct AimFx;

impl StableEffectType for AimFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        aim(sim, caster, input);
    }
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Bush {
    p: Params,
    /// 身上的就绪归本包管（[`still_mine`]）。
    mine: bool,
    /// 走出草丛的 tick 数。
    out_for: usize,
    /// 这场的草丛（第一次 on_update 时挑）。
    bushes: Option<Bushes>,
    was_in: bool,
    /// 上一 tick 身上有没有就绪（`ready` 或 `ready_kept`）、有没有收着的、有没有 `init`。
    had: bool,
    had_kept: bool,
    had_init: bool,
    /// 身上这份就绪是谁给的。
    source: Source,
    /// 这一场的计数，上一行 `TALLY` 写出去时的计数，下一行的 tick。
    tally: Tally,
    tally_shown: Tally,
    tally_next: usize,
}

impl StablePassive for Bush {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        // a respawn is a new unit with no buffs (and on_update never runs on a dead tick)
        self.mine = false;
        self.out_for = 0;
        self.was_in = false;
        self.had = false;
        self.had_kept = false;
        self.had_init = false;
        self.source = Source::Other;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, team, (x, y)) = (e.is_alive(), e.team(), (e.pos().0 as f64, e.pos().1 as f64));
        let (tick, shown) = (sim.tick(), on_screen(sim));
        if self.bushes.is_none() {
            let points: Vec<(f64, f64)> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|u| u.is_alive())
                .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
                .collect();
            let maps: Vec<MapGrids> = MAPS.lock().unwrap_or_else(|e| e.into_inner()).values().cloned().collect();
            let b = pick_bushes(&points, &maps);
            if let Some(k) = counted("bushes", shown) {
                let what = match &b {
                    Bushes::Grid(g) => format!("{} bush cells", g.count()),
                    Bushes::Absent => "this map has none (another mode's map has): no pounce from bushes".to_string(),
                    Bushes::Vision => "no bush grid - ready while the enemy team cannot see him".to_string(),
                };
                wlog(format!("{} BUSHES: {what} #{k}", head(sim, me)));
            }
            self.bushes = Some(b);
            self.tally_next = tick + TALLY_EVERY;
        }
        let in_map_bush = match self.bushes.as_ref() {
            Some(Bushes::Grid(g)) => g.at(x, y),
            Some(Bushes::Vision) => !sim.is_visible(1 - team.min(1), me),
            _ => false,
        };
        let m = marks(sim, me);
        // Ivern's brush (league_ivern marks the champions standing in one, either team: League's rule)
        let in_bush = in_map_bush || m.ivern;
        if in_bush != self.was_in && alive {
            if let Some(k) = counted("bush", shown) {
                let how = if in_bush { "INTO" } else { "OUT OF" };
                wlog(format!("{} {how} the bush at ({x:.0}, {y:.0}) #{k}", head(sim, me)));
            }
        }
        self.was_in = in_bush;
        self.out_for = if in_bush { 0 } else { self.out_for + 1 };
        let has_ready = m.ready || m.kept;
        // the first swing of this life just went out: the data's respawn readiness came and, unless that swing was at a
        // tower (then it is kept), went with it
        let first_swing = m.init && !self.had_init;
        self.had_init = m.init;
        if m.kept && !self.had_kept {
            self.tally.kept += 1;
        }
        self.had_kept = m.kept;
        if has_ready && !self.had {
            self.source = data_source(first_swing, m.stalking, m.fighting);
        } else if has_ready && m.stalking {
            // R took over the one he had (its own remove and add in one go)
            self.source = Source::Ult;
        }
        // the pounce went out: the readiness is gone, and not by this add-on (Drop keeps `had` false)
        if alive && !has_ready && (self.had || first_swing) {
            let source = if self.had { self.source } else { Source::Respawn };
            let near = nearest_enemy_champion(sim, team, (x, y));
            self.tally.pounce(source, near.is_some_and(|d| d <= NEAR));
            if let Some(k) = counted("pounce", shown) {
                let d = near.map_or_else(|| "no enemy champion alive".to_string(),
                                         |d| format!("the nearest enemy champion {d:.0} away"));
                wlog(format!("{} POUNCE: the readiness from {}, {d} #{k}", head(sim, me), source.label()));
            }
        }
        self.mine = still_mine(self.mine, has_ready, m.stalking, m.fighting);
        let now = step(&self.p, alive, in_bush, has_ready, self.mine, self.out_for, m.fighting);
        match now {
            Step::Ready => {
                let mut b = BuffV1::named(READY);
                b.range = self.p.leap_range;
                sim.add_buff(me, &b);
                self.mine = true;
                self.source = if in_map_bush { Source::Bush } else { Source::Ivern };
                if in_map_bush {
                    self.tally.bush += 1;
                } else {
                    self.tally.ivern += 1;
                }
                if let Some(k) = counted("ready", shown) {
                    let when = if m.fighting { "in a fight" } else { "out of combat: it stays" };
                    wlog(format!("{} READY: the pounce from {} ({when}) #{k}", head(sim, me), self.source.label()));
                }
            }
            Step::Drop => {
                sim.entity_remove_buff(me, READY);
                sim.entity_remove_buff(me, KEPT);
                self.mine = false;
                self.tally.dropped += 1;
                if let Some(k) = counted("drop", shown) {
                    wlog(format!("{} DROP: out of the bush {} ticks in a fight #{k}", head(sim, me), self.out_for));
                }
            }
            Step::Nothing => {}
        }
        self.had = match now {
            Step::Ready => true,
            Step::Drop => false,
            Step::Nothing => has_ready,
        };
        if tick >= self.tally_next {
            if self.tally != self.tally_shown {
                if let Some(k) = counted("tally", shown) {
                    wlog(format!("{} TALLY {}:{:02}: {} #{k}", head(sim, me), tick / 3600, tick / 60 % 60, self.tally.line()));
                }
                self.tally_shown = self.tally.clone();
            }
            while self.tally_next <= tick {
                self.tally_next += TALLY_EVERY;
            }
        }
    }
}

// ===================== 注册 =====================

/// 本包的被动（合集也用它；地图钩子合集另外合并）。
pub fn register_passive(module: &mut StableMod) {
    module.add_native_passive(format!("{ID}:bush"), Bush::default());
}

/// Everything this add-on registers, into its own DLL's module or league_addons' (the map hook aside).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Rengar: the pounce from the map's bushes, out of combat and after R, kept off towers) loaded: \
         game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    register_passive(module);
    module.add_native_effect(format!("{ID}:aim"), AimFx);
    host.log(LogLevel::Info, &format!("league_rengar_bush v{VERSION} loaded (Rengar: Unseen Predator from the map's bushes)."));
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

    /// 本包的副本（make_override.py 写的）：本包读写的 buff 名、`aim`、被动参数都要和这里对得上。
    const COPY: &str = include_str!("../override/league_rengar.data_champion");

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params(r#"{"leap_range":25000}"#), Params::default());
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"leap_range":30000,"junk":7}"#).leap_range, 30000);
        // `aim` gives a kept readiness back with the default range: the copy's own must be the same
        assert!(COPY.contains(&format!("\"leap_range\": {}", Params::default().leap_range)), "run make_override.py");
    }

    #[test]
    fn the_copy_speaks_our_names() {
        for name in [READY, KEPT, R_ON, FIGHT, INIT, "league_rengar_bush:aim", "league_rengar_bush:bush"] {
            assert!(COPY.contains(&format!("\"{name}\"")), "{name} is not in the copy: run make_override.py");
        }
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
        let a = MapGrids { walls: Some(Grid::from_rows(&["#.", ".."])), bushes: Some(Grid::from_rows(&["..", "#."])), seq: 1 };
        let b = MapGrids { walls: Some(Grid::from_rows(&[".#", "##"])), bushes: Some(Grid::from_rows(&["#.", ".."])), seq: 2 };
        let here = [(CELL * 1.5, CELL * 1.5)];
        assert_eq!(pick_bushes(&here, &[b.clone(), a.clone()]), Bushes::Grid(a.bushes.clone().unwrap()));
        // no map read, or none with bushes (the key unknown): the vision fallback
        assert_eq!(pick_bushes(&here, &[]), Bushes::Vision);
        assert_eq!(pick_bushes(&here, &[MapGrids::default()]), Bushes::Vision);
    }

    #[test]
    fn a_map_without_bushes_borrows_none() {
        // the match is on `c` (nobody in its walls), which has no bushes: 0.1.x took `a`'s grid there
        let a = MapGrids { walls: Some(Grid::from_rows(&["##", "#."])), bushes: Some(Grid::from_rows(&["#.", ".#"])), seq: 1 };
        let c = MapGrids { walls: Some(Grid::from_rows(&["..", ".."])), bushes: None, seq: 2 };
        let here = [(CELL * 0.5, CELL * 0.5)];
        assert_eq!(pick_bushes(&here, &[a.clone(), c.clone()]), Bushes::Absent);
        // two maps that fit as well: the one read last (the map hook runs as each match is made)
        let d = MapGrids { walls: c.walls.clone(), bushes: Some(Grid::from_rows(&["..", ".#"])), seq: 3 };
        assert_eq!(pick_bushes(&here, &[c.clone(), d.clone()]), Bushes::Grid(d.bushes.clone().unwrap()));
        assert_eq!(pick_bushes(&here, &[MapGrids { seq: 4, ..c }, d]), Bushes::Absent);
    }

    #[test]
    fn ready_in_the_bush_dropped_out_of_it() {
        let p = Params::default();
        // in the bush: ready, once
        assert_eq!(step(&p, true, true, false, false, 0, true), Step::Ready);
        assert_eq!(step(&p, true, true, true, true, 0, true), Step::Nothing);
        // out of it in a fight: taken back after `grace` ticks
        assert_eq!(step(&p, true, false, true, true, p.grace - 1, true), Step::Nothing);
        assert_eq!(step(&p, true, false, true, true, p.grace, true), Step::Drop);
        // out of combat it stays: the 3 s readiness, the main pack's rule
        assert_eq!(step(&p, true, false, true, true, 99, false), Step::Nothing);
        // the data's (R's, the respawn's, the 3 s one) stays
        assert_eq!(step(&p, true, false, true, false, 99, true), Step::Nothing);
        assert_eq!(step(&p, false, true, false, false, 0, true), Step::Nothing);
    }

    #[test]
    fn whose_readiness() {
        // the add-on's own, in a fight
        assert!(still_mine(true, true, false, true));
        // R took it over (its own remove and add in one go: the add-on never saw it gone)
        assert!(!still_mine(true, true, true, true));
        // out of combat it is the 3 s readiness: never taken back, even when the fight then opens with W or E
        assert!(!still_mine(true, true, false, false));
        assert!(!still_mine(true, false, false, true));
        // not the add-on's again until it gives one
        assert!(!still_mine(false, true, false, true));
        assert_eq!(data_source(true, true, false), Source::Respawn);
        assert_eq!(data_source(false, true, true), Source::Ult);
        assert_eq!(data_source(false, false, false), Source::Quiet);
        assert_eq!(data_source(false, false, true), Source::Other);
    }

    #[test]
    fn towers_keep_the_pounce_for_the_next_unit() {
        assert!(structure(Some(EntityKindV1::Tower)) && structure(Some(EntityKindV1::Nexus)));
        assert!(!structure(Some(EntityKindV1::Champion)) && !structure(Some(EntityKindV1::Jungle)) && !structure(None));
        assert_eq!(aim_step(true, true, false), Aim::Keep { dup: false });
        assert_eq!(aim_step(true, true, true), Aim::Keep { dup: true });
        // already kept: a plain swing at the tower
        assert_eq!(aim_step(true, false, true), Aim::Nothing);
        assert_eq!(aim_step(true, false, false), Aim::Nothing);
        assert_eq!(aim_step(false, false, true), Aim::Back { dup: false });
        assert_eq!(aim_step(false, true, true), Aim::Back { dup: true });
        // the pounce as the data has it
        assert_eq!(aim_step(false, true, false), Aim::Nothing);
        assert_eq!(aim_step(false, false, false), Aim::Nothing);
    }

    #[test]
    fn the_tally_line() {
        let mut t = Tally::default();
        assert!(t.line().starts_with("0 pounces (none), 0 with an enemy champion within 68000;"));
        t.pounce(Source::Bush, true);
        t.pounce(Source::Quiet, false);
        t.pounce(Source::Quiet, true);
        t.bush = 4;
        t.dropped = 2;
        t.kept = 1;
        assert_eq!(
            t.line(),
            "3 pounces (a bush 1, 3 s out of combat 2), 2 with an enemy champion within 68000; readied in bushes 4 \
             (Ivern's brush 0), dropped 2 after leaving one in a fight, kept 1 at towers"
        );
    }
}
