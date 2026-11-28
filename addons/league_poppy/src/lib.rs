//! 波比附加包（用户 2026-10-18：「波比放辅助，技能按方案 A 做（带扩展包 league_poppy）」）。主包保持纯数据；`mod.override_info`
//! 把主包的波比换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_poppy.py 的 `native=1` 生成：技能、时机一字不改，
//! 只有下面几处换成本包的原生效果），本包补数据做不到的五件事（英雄联盟的规则）：
//!
//! - **坚定风采打断突进**（被动 `league_poppy:steadfast`）：她身上有坚定风采的光环（主包的 `league_poppy_w_on`）时，每 tick 看
//!   光环（`W_R` + 他的身体）里的每个敌方英雄：一 tick 里移动了至少 `DASH_STEP`、也超过他自己移速的 `DASH_WALK` 倍（远超
//!   走路，不到 `BLINK_MAX`：闪现、传送不算）就是在突进——击飞 `W_UP` tick（击飞会打断突进）、`W_DMG` + `W_AP`% 法强魔法
//!   伤害，然后缚地（不能位移）并减速 `W_SLOW`% `W_GROUND` tick；每次光环每人只挡一次（他身上的 `league_poppy_w_hit`）。
//!   被她自己推着飞的（E、R，`league_poppy_push`）不算；2026-11-13 起别人推着走的也不算（`external_push`：在强制位移却不在
//!   放技能——队友的击退穿过光环原来被当成突进击飞，击飞又把那一下推打断）。
//! - 2026-11-13（用户：「沙皇的反推 好像推不到人 整体检查一下各个推的逻辑」「接着修」）：E 撞墙到点还在位移就等一拍，停下了
//!   却不在墙边（被别人的控制打断、自己的位移技能顶掉）就不砸不晕（日志 `SHORT`）；5v5 的裁决先击飞再推（给正在位移的单位上
//!   击飞会把位移停掉，原来先推后击飞）。当天下午还把推和击飞按目标的韧性放长过，晚上撤了：引擎不按韧性缩短强制位移（见
//!   `push_rules`），放长只会推过头。
//!   主包：光环里的敌方英雄放不出新的位移技能。
//! - **坚定风采低血翻倍**：生命低于 `W_LOW`% 时护甲、魔抗再 +`W_DEF`%（`league_poppy_w_low`）。主包：一直 +`W_DEF`%。
//! - **英勇冲锋撞墙才晕**（原生效果 `league_poppy:charge`，撞上目标时）：沿推的方向查墙（卡蜜尔附加包的墙格、5v5 地图的四边）：
//!   推 `E_KB_SPEED` x `E_KB_T` 的路上碰到墙就推到墙边，到的那一刻（被动看他身上的 `league_poppy_e_due` 到期）再受一次
//!   `E_DMG` + `E_RATIO`% 攻击力物理伤害并眩晕 `E_STUN` tick；没碰到墙就照常推开、不晕。主包：每次推完都晕一下。
//!   峡谷地图（Rin 的召唤师峡谷 α，`game_places::terrain`）上查峡谷的墙格（没有墙体文件时只有地图四边外算墙）。
//!   2026-11-28：峡谷上分两层——撞的是真墙（`terrain::rift_walls`），推到的地方不进墙往外长一格的那一圈
//!   （`terrain::rift_ground`）。以前只拿长了一格的那层当墙，身体再另算一次：贴着墙边推、擦过那一圈也算撞墙，人停在离墙
//!   还有大半个身子的地方就晕了（拿 0.1.86 的墙算：墙边的推里旧的晕有 35% 一路碰不到真墙）。
//! - **持卫的裁决打回泉水**（原生效果 `league_poppy:verdict`，冲击波打中英雄时）：5v5 地图上朝他自己的水晶方向强制位移
//!   `R_FAR`（速度 `R_FAR_SPEED`，撞墙会停），一路在空中（击飞）；别的地图照数据从她身边击飞击退。主包：击飞 `R_AIR` tick
//!   并从她身边击退 `R_KB_SPEED` x `R_KB_T`。峡谷上的水晶读场上的（他那一队的）。
//! - **钢铁大使的护盾按最大生命算**（原生效果 `league_poppy:pick`，捡起圆盾时）：最大生命的 `P_SH_MIN`%（1 级）到
//!   `P_SH_MAX`%（18 级），`P_SH_T` tick。主包：固定值 + 攻击力加成。
//!
//! 数字是主包参数表 P 的同名项（小写）；`make_override.py` 生成副本时核对，不一致就停。本包不按任何技能键。
//!
//! 0.1.5（2026-11-08 日志审查：83 次 `BLOCK` 里 24 次只是一 tick 走了 2213-2599，刚过 `DASH_STEP`，13 次在 10:00 以后——后期
//! 走路一 tick 就有 1766-1995，加一点速就过线）：一 tick 的位移还要超过他这时的移速（`stat().move_speed`，每 tick 走多远、
//! buff 算在内，取上一 tick 和这一 tick 大的那个）的 `DASH_WALK` 倍才算突进，跑得快的人走过光环不再被当成突进挡下；
//! `BLOCK` 行写出他的移速。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_poppy.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `BLOCK`（挡下突进）、`CHARGE`（撞墙 / 没墙）、`WALL`（撞墙眩晕）、`VERDICT`（往哪打飞）、`PICK`（护盾），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex, Once};

use game_places::skill_scale::sk;
use game_places::terrain::{self, Map, Walls};
use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_poppy";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_poppy") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 坚定风采：护甲魔抗 %、低血线 %、光环半径、挡下突进的伤害（固定、法强 %）、击飞、缚地、减速 %。
/// 这里的距离、速度在大地图版跟着乘 1.3（game_places::skill_scale；副本的被动参数不读，读的是这些数）。
pub const W_DEF: usize = 16;
pub const W_LOW: usize = 40;
pub const W_R: usize = 35_000;
pub const W_DMG: usize = 70;
pub const W_AP: usize = 70;
pub const W_UP: usize = 30;
pub const W_GROUND: usize = 120;
pub const W_SLOW: usize = 25;
/// 英勇冲锋：撞墙伤害（固定、攻击力 %）、推的速度和 tick、撞墙眩晕。
pub const E_DMG: usize = 70;
pub const E_RATIO: usize = 80;
pub const E_KB_SPEED: usize = 2_500;
pub const E_KB_T: usize = 12;
pub const E_STUN: usize = 105;
/// 钢铁大使的护盾：最大生命 %（1 级、18 级）、tick。
pub const P_SH_MIN: usize = 11;
pub const P_SH_MAX: usize = 21;
pub const P_SH_T: usize = 180;
/// 持卫的裁决：别的地图的击退（速度、tick）；5v5 打回泉水的距离、速度。
pub const R_KB_SPEED: usize = 6_000;
pub const R_KB_T: usize = 25;
/// 飞的时候在空中（击飞）的 tick（r_air）。
pub const R_AIR: usize = 25;
pub const R_FAR: usize = 150_000;
pub const R_FAR_SPEED: usize = 6_000;

/// 一 tick 里至少走这么远算突进（前期走路约 1000，加速后 1500；冲刺 2500 起），超过这么远算闪现 / 传送（英雄联盟不挡）。
pub const DASH_STEP: f64 = 2_200.0;
pub const BLINK_MAX: f64 = 20_000.0;
/// 还要超过他自己移速（每 tick 走多远）的这么多倍才算突进：后期走路一 tick 就有 1766-1995，加一点速就过了 `DASH_STEP`
/// （2026-11-08 日志审查：83 次 `BLOCK` 里 24 次是 2213-2599 的走路）。
pub const DASH_WALK: f64 = 1.3;
/// 推到墙边时离墙留的距离（身体半径另算）。
pub const WALL_GAP: f64 = 1_000.0;
/// 5v5 地图四边的可走范围（卡蜜尔附加包量的）和两边的水晶。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);
pub const NEXUS: [(f64, f64); 2] = [(96_000.0, 864_000.0), (864_000.0, 96_000.0)];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_POPPY_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_poppy.log");
        }
    }
    PathBuf::from("league_poppy.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
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
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
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

// ===================== 规则（单元测试用） =====================

pub type Pt = (f64, f64);

fn n(name: &str) -> String {
    format!("{ID}_{name}")
}

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn unit(v: Pt) -> Option<Pt> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

/// 墙格的边长（世界单位，游戏自己的地图）和查墙的步长。
pub const CELL: f64 = 32_000.0;
pub const STEP: f64 = 1_000.0;

/// 地图的墙格：游戏自己的三张图（卡蜜尔附加包的内置地图，杰斯、巴德附加包同样用它；每格 `CELL`，从 (0, 0) 起；5v5 地图另加
/// 四边），或峡谷的墙格（[`Grid::rift`]：格子有它自己的边长和起点）。
/// `cells` 是英雄的中心站不住的格子；`rock` 是真墙（推的人撞上的地形）。游戏自己的地图两者一样（`rock` 为 None）；
/// 峡谷上 `cells` 是墙往外长一格（`terrain::rift_ground`），`rock` 是墙体文件本身的墙（`terrain::rift_walls`）。
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
    pub bounds: Option<(f64, f64, f64, f64)>,
    /// 一格的边长、格子 (0, 0) 的角（游戏自己的地图：`CELL`、(0, 0)）。
    pub cell: f64,
    pub origin: Pt,
    pub rock: Option<Vec<Vec<bool>>>,
}

impl Grid {
    pub fn from_rows(rows: &[&str], bounds: Option<(f64, f64, f64, f64)>) -> Grid {
        Grid {
            cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(),
            bounds,
            cell: CELL,
            origin: (0.0, 0.0),
            rock: None,
        }
    }

    /// 0 = 5v5（四边也是墙），1 = 单线，2 = 死斗。
    pub fn builtin() -> [Grid; 3] {
        [
            Grid::from_rows(&maps::MOBA, Some(MOBA_BOUNDS)),
            Grid::from_rows(&maps::SINGLE_LANE, None),
            Grid::from_rows(&maps::DEATH_MATCH, None),
        ]
    }

    /// 峡谷的墙格（`game_places::terrain`）：读到墙体文件就用它的格子（格子外算墙）；没有文件时不知道哪里是墙，只有地图四边外
    /// 算墙（整张图一格空地）——撞墙的技能在峡谷上找不到墙，不会像以前拿游戏自己的墙格那样把 960000 以外全当成墙。
    pub fn rift(walls: Option<&Walls>) -> Grid {
        match walls {
            Some(w) => Grid {
                cells: w.cells.clone(),
                bounds: Some((0.0, 0.0, w.extent.0, w.extent.1)),
                cell: w.cell,
                origin: w.origin,
                rock: None,
            },
            None => {
                let e = terrain::RIFT_EXTENT;
                Grid { cells: vec![vec![false]], bounds: Some((0.0, 0.0, e, e)), cell: e, origin: (0.0, 0.0), rock: None }
            }
        }
    }

    /// 峡谷的两层：站不住的格子（`ground`，墙往外长一格）和真墙（`rock`，墙体文件）。缺一层就只用另一层（和以前一样）。
    pub fn rift_layers(rock: Option<&Walls>, ground: Option<&Walls>) -> Grid {
        match (rock, ground) {
            (Some(r), Some(g)) if r.cells.len() == g.cells.len() && r.cell == g.cell && r.origin == g.origin => {
                Grid { rock: Some(r.cells.clone()), ..Grid::rift(Some(g)) }
            }
            (_, Some(g)) => Grid::rift(Some(g)),
            (r, None) => Grid::rift(r),
        }
    }

    /// 世界坐标落在墙里吗（英雄的中心站不住；地图外、5v5 的四边外、格子外都算墙）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        self.at_layer(&self.cells, x, y)
    }

    /// 世界坐标落在真墙里吗（推的人撞上的地形；游戏自己的地图就是 [`Grid::is_wall`]）。
    pub fn is_rock(&self, x: f64, y: f64) -> bool {
        self.at_layer(self.rock.as_ref().unwrap_or(&self.cells), x, y)
    }

    fn at_layer(&self, layer: &[Vec<bool>], x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return true;
        }
        if let Some((x0, y0, x1, y1)) = self.bounds {
            if x < x0 || y < y0 || x > x1 || y > y1 {
                return true;
            }
        }
        let (fx, fy) = ((x - self.origin.0) / self.cell, (y - self.origin.1) / self.cell);
        if fx < 0.0 || fy < 0.0 {
            return true;
        }
        layer.get(fy as usize).and_then(|r| r.get(fx as usize)).copied().unwrap_or(true)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }
}

/// 当前对局的地图：英雄站进墙里最少的那张（同杰斯、巴德附加包）。
pub fn current(grids: &[Grid], champions: &[Pt]) -> Option<usize> {
    grids
        .iter()
        .enumerate()
        .min_by_key(|(_, g)| {
            let inside = champions.iter().filter(|&&(x, y)| g.is_wall(x, y)).count();
            (inside, std::cmp::Reverse(g.walls()))
        })
        .map(|(i, _)| i)
}

/// 从 `at` 沿 `dir` 推 `reach`（身体半径 `body`）：`Some(走多远)` 路上撞墙（推到墙边为止），`None` 一路没墙。
/// 撞的是真墙（[`Grid::is_rock`]）；峡谷上推到的地方在英雄中心站不住的那一圈里，就沿来路退到圈外。
pub fn wall_travel(grid: &Grid, at: Pt, dir: Pt, reach: f64, body: f64) -> Option<f64> {
    let mut s = STEP;
    while s <= reach + body + 0.5 {
        if grid.is_rock(at.0 + dir.0 * s, at.1 + dir.1 * s) {
            let mut len = (s - body - WALL_GAP).max(0.0);
            if grid.rock.is_some() {
                while len > 0.0 && grid.is_wall(at.0 + dir.0 * len, at.1 + dir.1 * len) {
                    len = (len - STEP).max(0.0);
                }
            }
            return Some(len);
        }
        s += STEP;
    }
    None
}

/// 一 tick 走了 `step` 算不算突进：他走路一 tick 走 `walk`（移速，buff 算在内），走得再快也只是走路；闪现、传送那么远的不算。
pub fn is_dash(step: f64, walk: f64) -> bool {
    // 大地图版突进跟着快 1.3 倍，两道线一起乘；走路不乘
    (sk(DASH_STEP).max(walk * DASH_WALK)..=sk(BLINK_MAX)).contains(&step)
}

/// 钢铁大使的护盾：等级 `level`、最大生命 `max_hp`。
pub fn shield_amount(max_hp: usize, level: usize) -> usize {
    let l = level.clamp(1, 18) - 1;
    let pct_x17 = P_SH_MIN * 17 + (P_SH_MAX - P_SH_MIN) * l;
    max_hp * pct_x17 / (100 * 17)
}

/// 他这一方的水晶：离他的塔（还在的）平均位置近的那个；一座塔都没有就 None。
pub fn home_nexus(towers: &[Pt]) -> Option<Pt> {
    home_nexus_in(towers, &NEXUS)
}

/// 同 [`home_nexus`]，在 `nexuses` 里挑。
pub fn home_nexus_in(towers: &[Pt], nexuses: &[Pt]) -> Option<Pt> {
    if towers.is_empty() {
        return None;
    }
    let k = towers.len() as f64;
    let c = (towers.iter().map(|t| t.0).sum::<f64>() / k, towers.iter().map(|t| t.1).sum::<f64>() / k);
    nexuses.iter().copied().min_by(|a, b| dist(*a, c).total_cmp(&dist(*b, c)))
}

/// 峡谷上读不到水晶时猜的两个：游戏自己的两个按地图大小放大（两张图的朝向一样）。
pub fn rift_nexus() -> [Pt; 2] {
    let s = Map::Rift.scale();
    NEXUS.map(|(x, y)| (x * s, y * s))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn cc_immune(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.cc_immune))
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

fn pt(p: Pt) -> String {
    format!("({:.0}, {:.0})", p.0, p.1)
}

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

/// 猜地图用的点：所有活着的单位（英雄、小兵、野怪、塔……）。只看英雄的话，大家都站在三张图都空着的那条斜带上
/// （中路、两边泉水）时打平，平手偏向墙多的单线 / 死斗图，5v5 就猜错了（2026-11-01 复查：波比的 R 有 7 次退回击退）；
/// 5v5 边路的兵和野区的野怪几乎一直在，正好落在另两张图的墙里。
fn unit_points(sim: &StableSim<'_>) -> Vec<Pt> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_alive())
        .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
        .collect()
}

/// 游戏自己的三张图（建一次）；峡谷的墙格（第一次用时读墙体文件，建一次：近 9 万格，不每 tick 重建）。
static BUILTIN: LazyLock<[Grid; 3]> = LazyLock::new(Grid::builtin);
static RIFT: LazyLock<Grid> = LazyLock::new(|| Grid::rift_layers(terrain::rift_walls(), terrain::rift_ground()));
/// 这次启动第一次碰到峡谷时在日志里记一行。
static RIFT_SEEN: Once = Once::new();

/// 当前地图的墙格（和它是不是 5v5）：峡谷（塔、水晶站在游戏自己的地图外，`terrain::map_of_sim`）用峡谷的墙格；游戏自己的
/// 地图照旧在三张内置图里挑单位站进墙里最少的那张。
fn grid_now(sim: &StableSim<'_>) -> Option<(&'static Grid, bool)> {
    match terrain::map_of_sim(sim) {
        Map::Rift => {
            RIFT_SEEN.call_once(|| {
                wlog(format!("== Rift: Heroic Charge stuns on the Rift's rock (its walls file; he stops clear of the walls \
                              grown by a cell; rock layer {}), Keeper's Verdict sends toward the nexus on the field; {} ==",
                             if RIFT.rock.is_some() { "on" } else { "missing" }, terrain::rift_status()))
            });
            Some((&*RIFT, true))
        }
        Map::Native => current(&*BUILTIN, &unit_points(sim)).map(|i| (&BUILTIN[i], i == 0)),
    }
}

/// 场上 `team` 这一队活着的水晶。
fn nexus_of(sim: &StableSim<'_>, team: usize) -> Option<Pt> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .find(|e| e.kind() == Some(EntityKindV1::Nexus) && e.team() == team && e.is_alive())
        .map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

/// 5v5 上他（`team`，还在的塔 `towers`）的水晶：游戏自己的地图照旧按塔挑 `NEXUS`；峡谷上读场上他那一队的水晶，读不到才按塔
/// 挑 [`rift_nexus`]。
fn home_of(sim: &StableSim<'_>, team: usize, towers: &[Pt]) -> Option<Pt> {
    match terrain::map_of_sim(sim) {
        Map::Native => home_nexus(towers),
        Map::Rift => nexus_of(sim, team).or_else(|| home_nexus_in(towers, &rift_nexus())),
    }
}

/// 2026-11-13：离墙这么近（身体之外）才算推到了墙边。
pub const AT_WALL: f64 = 4_000.0;

/// 2026-11-13：他在 `at` 贴着墙吗：16 个方向里有一个 `AT_WALL`（加身体）以内是墙格。
pub fn near_wall(grid: &Grid, at: Pt, body: f64) -> bool {
    (0..16).any(|k| {
        let a = k as f64 * std::f64::consts::TAU / 16.0;
        wall_travel(grid, at, (a.cos(), a.sin()), AT_WALL, body).is_some()
    })
}

/// 2026-11-13：别人推着他走（不是他自己的突进）：在强制位移却不在放技能（自己的突进带着施法动作，数据的击退、拉人、别的
/// 附加包的推没有）。原来只认她自己的推（`push`），队友的击退穿过光环被当成突进击飞，击飞又把那一下推打断。
pub fn external_push(force_move: bool, casting: bool) -> bool {
    force_move && !casting
}

fn pushed_by_another(sim: &StableSim<'_>, id: usize) -> bool {
    let Some(e) = sim.get_entity(id) else { return false };
    let kinds: Vec<u32> = (0..e.cc_count()).filter_map(|i| e.cc_at(i)).map(|c| c.kind).collect();
    external_push(kinds.contains(&CcKindV1::ForceMove.code()), kinds.contains(&CcKindV1::Animation.code()))
}

/// 强制位移 `target` 沿 `dir` 走 `len`，速度 `speed`；返回 tick 数。
fn shove(sim: &mut StableSim<'_>, target: usize, dir: Pt, len: f64, speed: usize) -> usize {
    let ticks = ((len / speed as f64).ceil() as usize).max(1);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (dir.0 * len).round() as i64;
    cc.dy = (dir.1 * len).round() as i64;
    cc.speed = speed as u64;
    sim.apply_cc(target, &cc);
    sim.add_buff(target, &BuffV1::timed(&n("push"), ticks + 2));
    ticks
}

// ===================== 原生效果 =====================

/// 英勇冲锋撞上目标：沿推的方向查墙，推到墙边并记下撞墙的时刻，或者照常推开。
fn charge(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some(body) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.radius() as f64) else {
        return;
    };
    if cc_immune(sim, target) {
        return;
    }
    let (Some(her), Some(at)) = (pos(sim, me), pos(sim, target)) else { return };
    let dir = unit((at.0 - her.0, at.1 - her.1)).unwrap_or((1.0, 0.0));
    let speed = sk(E_KB_SPEED);
    let reach = (speed * E_KB_T) as f64;
    let wall = grid_now(sim).and_then(|(g, _)| wall_travel(g, at, dir, reach, body));
    match wall {
        Some(len) => {
            let ticks = if len >= 1.0 { shove(sim, target, dir, len, speed) } else { 0 };
            sim.add_buff(target, &BuffV1::timed(&n("e_due"), ticks.max(1)));
            sim.add_buff(target, &BuffV1::timed(&n("e_go"), ticks + 4));
            if let Some(k) = counted("charge") {
                wlog(format!("{} CHARGE #{target} at {}: a wall {len:.0} away, slams in {ticks} ticks #{k}", head(sim, me), pt(at)));
            }
        }
        None => {
            shove(sim, target, dir, reach, speed);
            if let Some(k) = counted("charge") {
                wlog(format!("{} CHARGE #{target} at {}: no wall within {reach:.0}, pushed, no stun #{k}", head(sim, me), pt(at)));
            }
        }
    }
}

/// 持卫的裁决打中一个敌方英雄：5v5 打回他的水晶方向，别的地图从她身边击退。
fn verdict(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some(team) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.team()) else { return };
    if cc_immune(sim, target) {
        return;
    }
    let Some(at) = pos(sim, target) else { return };
    let moba = grid_now(sim).is_some_and(|(_, m)| m);
    let towers: Vec<Pt> = (0..sim.tower_count())
        .map(|i| sim.tower_id_at(i))
        .filter(|&t| sim.get_entity(t).is_some_and(|e| e.is_alive() && e.team() == team))
        .filter_map(|t| pos(sim, t))
        .collect();
    let home = if moba { home_of(sim, team, &towers) } else { None };
    match home.and_then(|h| unit((h.0 - at.0, h.1 - at.1)).map(|d| (h, d))) {
        Some((h, dir)) => {
            let len = (sk(R_FAR) as f64).min(dist(h, at));
            // 2026-11-13: knocked up FIRST - a knock-up given to a moving unit stops its move (champion-data.md), so the
            // carry given first was cancelled by it (the data's Verdict went this way round: "an Airborne beside the
            // Knockback still lets it carry them - measured")
            let ticks = ((len / sk(R_FAR_SPEED) as f64).ceil() as usize).max(1);
            sim.apply_cc(target, &CcV1::of_kind(CcKindV1::Airborne, ticks.max(R_AIR) as u64));
            let ticks = shove(sim, target, dir, len, sk(R_FAR_SPEED));
            if let Some(k) = counted("verdict") {
                wlog(format!("{} VERDICT #{target} at {}: toward his nexus {} - {len:.0} in {ticks} ticks #{k}", head(sim, me), pt(at), pt(h)));
            }
        }
        None => {
            sim.apply_cc(target, &CcV1::of_kind(CcKindV1::Airborne, R_AIR as u64));
            sim.entity_knockback(me, target, sk(R_KB_SPEED), R_KB_T);
            sim.add_buff(target, &BuffV1::timed(&n("push"), R_KB_T + 2));
            if let Some(k) = counted("verdict") {
                wlog(format!("{} VERDICT #{target} at {}: knocked away from her (no nexus here) #{k}", head(sim, me), pt(at)));
            }
        }
    }
}

/// 捡起圆盾：按最大生命和等级给护盾。
fn pick(sim: &mut StableSim<'_>, me: usize, _input: InputTargetV1) {
    let Some((max_hp, level)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.hp().1, e.level())) else { return };
    let amount = shield_amount(max_hp, level);
    sim.entity_add_shield(me, amount, P_SH_T);
    if let Some(k) = counted("pick") {
        wlog(format!("{} PICK level {level} max hp {max_hp}: shield {amount} for {P_SH_T} ticks #{k}", head(sim, me)));
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 被动：坚定风采 =====================

#[derive(Clone, Default)]
struct Steadfast {
    /// 上一 tick 光环附近的敌方英雄在哪、移速多少（id -> (tick, 位置, 每 tick 走多远)）。
    seen: HashMap<usize, (usize, Pt, f64)>,
}

impl Steadfast {
    fn low_health(sim: &mut StableSim<'_>, me: usize) {
        let Some((hp, max)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        let low = max > 0 && hp * 100 < max * W_LOW;
        let name = n("w_low");
        let has = has_buff(sim, me, &name);
        if low && !has {
            let mut b = BuffV1::timed(&name, 1_000_000);
            b.defence_mult = W_DEF as i32;
            b.magic_resistance_mult = W_DEF as i32;
            sim.add_buff(me, &b);
        } else if !low && has {
            sim.entity_remove_buff(me, &name);
        }
    }

    fn block(sim: &mut StableSim<'_>, me: usize, foe: usize, step: f64, walk: f64) {
        sim.apply_cc(foe, &CcV1::of_kind(CcKindV1::Airborne, W_UP as u64));
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        sim.deal_damage_typed(me, foe, W_DMG + W_AP * ap / 100, DamageTypeV1::Ap, AttackTypeV1::Skill);
        sim.apply_cc(foe, &CcV1::of_kind(CcKindV1::BlockMoveSkill, (W_UP + W_GROUND) as u64));
        let mut slow = BuffV1::timed(&n("w_slow"), W_UP + W_GROUND);
        slow.move_speed_mult = -(W_SLOW as i32);
        sim.entity_remove_buff(foe, &n("w_slow"));
        sim.add_buff(foe, &slow);
        sim.add_buff(foe, &BuffV1::timed(&n("w_block"), 20));
        let left = sim.get_entity(me).and_then(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == n("w_on")));
        let hold = left.map_or(W_UP + W_GROUND, |b| b.duration_tick);
        sim.add_buff(foe, &BuffV1::timed(&n("w_hit"), hold + 2));
        if let Some(k) = counted("block") {
            wlog(format!("{} BLOCK #{foe}: {step:.0} in a tick (he walks {walk:.0}) inside her aura - knocked up, grounded #{k}",
                         head(sim, me)));
        }
    }

    /// 被推到墙边的人到了：撞墙伤害 + 眩晕。
    fn walls(sim: &mut StableSim<'_>, me: usize, foe: usize) {
        if !has_buff(sim, foe, &n("e_go")) || has_buff(sim, foe, &n("e_due")) {
            return;
        }
        if push_rules::moving_id(sim, foe) {
            return; // 2026-11-13: not there yet (e_go lasts a few ticks past e_due)
        }
        sim.entity_remove_buff(foe, &n("e_go"));
        if !sim.get_entity(foe).is_some_and(|e| e.is_alive()) {
            return;
        }
        // 2026-11-13: stopped short of the wall (another's crowd control, a dash of his own): no slam (was: slammed and
        // stunned wherever he stood when the time came)
        let body = sim.get_entity(foe).map_or(0.0, |e| e.radius() as f64);
        if let (Some(at), Some((g, _))) = (pos(sim, foe), grid_now(sim)) {
            if !near_wall(&g, at, body) {
                if let Some(k) = counted("short") {
                    wlog(format!("{} SHORT #{foe} at {}: stopped short of the wall, no slam #{k}", head(sim, me), pt(at)));
                }
                return;
            }
        }
        let ad = sim.get_entity(me).map_or(0, |e| e.stat().attack);
        sim.deal_damage_typed(me, foe, E_DMG + E_RATIO * ad / 100, DamageTypeV1::Ad, AttackTypeV1::Skill);
        if !cc_immune(sim, foe) {
            sim.apply_cc(foe, &CcV1::stun(E_STUN as u64));
            sim.add_buff(foe, &BuffV1::timed(&n("e_stun"), E_STUN));
        }
        sim.add_buff(foe, &BuffV1::timed(&n("e_wall"), 20));
        if let Some(k) = counted("wall") {
            wlog(format!("{} WALL #{foe} slammed into the wall: stunned {E_STUN} ticks #{k}", head(sim, me)));
        }
    }
}

impl StablePassive for Steadfast {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.seen.clear();
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let t = sim.tick();
        if t % 6 == 0 {
            Self::low_health(sim, me);
        }
        let Some((my_team, her)) = sim.get_entity(me).map(|e| (e.team(), (e.pos().0 as f64, e.pos().1 as f64))) else { return };
        let aura = has_buff(sim, me, &n("w_on"));
        // his move speed is a step a tick, buffs included (league_yuumi's WATCH: the host's longest step = his move speed)
        let foes: Vec<(usize, Pt, f64, f64)> = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter_map(|id| {
                sim.get_entity(id).filter(|e| e.team() != my_team && e.is_alive()).map(|e| {
                    (id, (e.pos().0 as f64, e.pos().1 as f64), e.radius() as f64, e.stat().move_speed as f64)
                })
            })
            .collect();
        for &(foe, at, body, speed) in &foes {
            Self::walls(sim, me, foe);
            let near = dist(at, her) <= sk(W_R) as f64 + body + sk(BLINK_MAX);
            let before = self.seen.get(&foe).copied();
            if near {
                self.seen.insert(foe, (t, at, speed));
            } else {
                self.seen.remove(&foe);
            }
            let Some((t0, from, speed0)) = before else { continue };
            if !aura || t0 + 1 != t || dist(at, her) > sk(W_R) as f64 + body {
                continue;
            }
            let step = dist(from, at);
            // a haste that just ran out (or just came) still counts: the faster of the two ticks
            let walk = speed.max(speed0);
            if !is_dash(step, walk)
                || has_buff(sim, foe, &n("w_hit"))
                || has_buff(sim, foe, &n("push"))
                || pushed_by_another(sim, foe)
                || cc_immune(sim, foe)
                || !sim.get_entity(foe).is_some_and(|e| e.is_targetable())
            {
                continue;
            }
            Self::block(sim, me, foe, step, walk);
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Poppy: Steadfast Presence stops dashes, Heroic Charge stuns on walls, Keeper's Verdict sends home) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:charge"), Step(charge));
    module.add_native_effect(format!("{ID}:verdict"), Step(verdict));
    module.add_native_effect(format!("{ID}:pick"), Step(pick));
    module.add_native_passive(format!("{ID}:steadfast"), Steadfast::default());
    host.log(LogLevel::Info, "league_poppy loaded (dash interrupt, wall stun, fountain-ward verdict, buckler shield).");
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

    #[test]
    fn dashes_not_walks_nor_blinks() {
        assert!(!is_dash(1_000.0, 1_000.0));
        assert!(!is_dash(1_600.0, 1_000.0));
        assert!(is_dash(2_500.0, 1_000.0));
        assert!(is_dash(3_500.0, 1_000.0));
        assert!(!is_dash(60_000.0, 1_000.0));
    }

    #[test]
    fn fast_walkers_are_no_dashers() {
        // 2026-11-08 log review: late-game walks of 2213-2599 a tick were blocked as dashes
        assert!(!is_dash(2_300.0, 2_000.0));
        assert!(!is_dash(2_599.0, 2_000.0));
        assert!(is_dash(2_700.0, 2_000.0));
        assert!(is_dash(3_000.0, 1_000.0));
        // a slow (or unknown) walker: DASH_STEP is still the floor
        assert!(!is_dash(2_000.0, 0.0));
        assert!(is_dash(2_300.0, 0.0));
        // however fast he walks, a blink is no dash
        assert!(!is_dash(BLINK_MAX + 1.0, 20_000.0));
    }

    #[test]
    fn shield_by_level() {
        assert_eq!(shield_amount(1_000, 1), 110);
        assert_eq!(shield_amount(1_000, 18), 210);
        assert_eq!(shield_amount(1_000, 30), 210);
        assert!(shield_amount(1_000, 9) > 110 && shield_amount(1_000, 9) < 210);
    }

    #[test]
    fn walls_stop_the_carry() {
        let grids = Grid::builtin();
        let g = &grids[0];
        // the map's left edge: pushed left from 40000 with a body of 6000 the wall is 17500 + 6000 away
        let to = wall_travel(g, (40_000.0, 480_000.0), (-1.0, 0.0), 30_000.0, 6_000.0).expect("the edge is a wall");
        assert!((to - (40_000.0 - MOBA_BOUNDS.0 - 6_000.0 - WALL_GAP)).abs() <= STEP, "{to}");
        // open ground in the middle of the map, pushed along the river: nothing within reach
        assert_eq!(wall_travel(g, (480_000.0, 480_000.0), (0.0, 1.0), 30_000.0, 6_000.0), None);
        // a wall cell of the grid (row 3, columns 15-16)
        let at = (15.5 * CELL, 3.5 * CELL + 20_000.0);
        assert!(wall_travel(g, at, (0.0, -1.0), 30_000.0, 6_000.0).is_some());
    }

    #[test]
    fn home_is_the_nearer_nexus() {
        let blue = [(150_000.0, 800_000.0), (300_000.0, 700_000.0)];
        assert_eq!(home_nexus(&blue), Some(NEXUS[0]));
        let red = [(800_000.0, 150_000.0)];
        assert_eq!(home_nexus(&red), Some(NEXUS[1]));
        assert_eq!(home_nexus(&[]), None);
    }

    /// 峡谷大小的假墙格：355 x 356 格（每格 60000/11，从 x = 30000/11 起，同作者的墙体文件），`walls` 里的格子 (x, y) 是墙。
    fn rift_walls(walls: &[(usize, usize)]) -> Walls {
        let rows: Vec<String> = (0..356).map(|y| (0..355).map(|x| if walls.contains(&(x, y)) { '#' } else { '.' }).collect()).collect();
        let rows: Vec<&str> = rows.iter().map(String::as_str).collect();
        Walls::from_rows(&rows, 60_000.0 / 11.0, (30_000.0 / 11.0, 0.0), (terrain::RIFT_EXTENT, terrain::RIFT_EXTENT))
    }

    /// 一堵 3 格厚、5 格长的墙，左边在 `x` 附近，`y` 那一行在中间：(格子, 墙的左边)。
    fn rift_block(x: f64, y: f64) -> (Vec<(usize, usize)>, f64) {
        let (cell, x0) = (60_000.0 / 11.0, 30_000.0 / 11.0);
        let (cx, cy) = (((x - x0) / cell) as usize, (y / cell) as usize);
        ((cx..cx + 3).flat_map(|x| (cy - 2..=cy + 2).map(move |y| (x, y))).collect(), x0 + cx as f64 * cell)
    }

    #[test]
    fn the_rifts_walls_stop_the_carry() {
        let (block, left) = rift_block(1_300_000.0, 1_300_000.0);
        let g = Grid::rift(Some(&rift_walls(&block)));
        // pushed toward a wall of the Rift past 1000000: up to it, the stun
        let to = wall_travel(&g, (left - 15_000.0, 1_300_000.0), (1.0, 0.0), 30_000.0, 6_000.0).expect("the Rift's wall");
        assert!((to - (15_000.0 - 6_000.0 - WALL_GAP)).abs() <= STEP, "{to}");
        // past 960000 is open ground on the Rift (the game's own grid called it all wall)
        let far = (1_100_000.0, 1_100_000.0);
        assert!(!g.is_wall(far.0, far.1) && Grid::builtin()[0].is_wall(far.0, far.1));
        assert_eq!(wall_travel(&g, far, (1.0, 0.0), 30_000.0, 6_000.0), None);
        // where the game's own 5v5 has a wall (row 3, columns 15-16) the Rift has none
        let at = (15.5 * CELL, 3.5 * CELL + 20_000.0);
        assert!(wall_travel(&Grid::builtin()[0], at, (0.0, -1.0), 30_000.0, 6_000.0).is_some());
        assert_eq!(wall_travel(&g, at, (0.0, -1.0), 30_000.0, 6_000.0), None);
    }

    #[test]
    fn no_walls_file_only_the_rifts_edges() {
        let g = Grid::rift(None);
        // no wall known inside: not the game's own (row 3, columns 15-16), nothing past 960000
        assert_eq!(wall_travel(&g, (15.5 * CELL, 3.5 * CELL + 20_000.0), (0.0, -1.0), 30_000.0, 6_000.0), None);
        assert_eq!(wall_travel(&g, (1_200_000.0, 1_200_000.0), (1.0, 0.0), 30_000.0, 6_000.0), None);
        // the map's edge still is one
        let to = wall_travel(&g, (terrain::RIFT_EXTENT - 20_000.0, 800_000.0), (1.0, 0.0), 30_000.0, 6_000.0).expect("the edge");
        assert!((to - (20_000.0 - 6_000.0 - WALL_GAP)).abs() <= STEP, "{to}");
    }

    /// 2026-11-28：峡谷上两层。撞的是真墙，推到的地方在长出来的那一圈外面；只碰到那一圈不算撞墙。
    #[test]
    fn on_the_rift_the_push_hits_rock_not_the_ring_round_it() {
        let (block, left) = rift_block(1_300_000.0, 1_300_000.0);
        let rock = rift_walls(&block);
        let g = Grid::rift_layers(Some(&rock), Some(&rock.padded()));
        let old = Grid::rift(Some(&rock.padded()));
        assert!(g.rock.is_some() && old.rock.is_none());
        let body = 10_000.0;
        // 迎面推向真墙：身体推到墙边才停（同游戏自己的地图），停的地方站得住；旧的停在那一圈前面，身体离墙还差一格多
        let at = (left - 20_000.0, 1_300_000.0);
        let to = wall_travel(&g, at, (1.0, 0.0), 30_000.0, body).expect("the rock");
        assert!((to - (20_000.0 - body - WALL_GAP)).abs() <= STEP, "{to}");
        assert!(!g.is_wall(at.0 + to, at.1) && near_wall(&g, (at.0 + to, at.1), body));
        let was = wall_travel(&old, at, (1.0, 0.0), 30_000.0, body).expect("the ring");
        assert!(to - was >= 4_000.0, "{was} -> {to}");
        // 停在旧的那个地方：离真墙还有一格多，不算贴着墙
        assert!(!near_wall(&g, (at.0 + was, at.1), body));
        // 真墙在 44000 外：推满 30000 身体也碰不到墙。旧的只看那一圈，推过去就晕；新的照常推开、不晕
        let far = (left - 44_000.0, 1_300_000.0);
        assert!(wall_travel(&old, far, (1.0, 0.0), 30_000.0, body).is_some(), "the old grid stunned here");
        assert_eq!(wall_travel(&g, far, (1.0, 0.0), 30_000.0, body), None);
        // 斜着推向墙面：落点要是进了那一圈就沿来路退到圈外
        let a = 10.0_f64.to_radians();
        let side = (left - 6_000.0, 1_280_000.0);
        let dir = (a.sin(), a.cos());
        let len = wall_travel(&g, side, dir, 30_000.0, body).expect("the rock at a slant");
        let stop = (side.0 + dir.0 * len, side.1 + dir.1 * len);
        assert!(!g.is_wall(stop.0, stop.1), "{len} {stop:?}");
        // 游戏自己的地图只有一层：和以前一模一样
        let n = &Grid::builtin()[0];
        assert!(n.rock.is_none() && n.is_rock(15.5 * CELL, 3.5 * CELL) && n.is_wall(15.5 * CELL, 3.5 * CELL));
    }

    /// 峡谷真的墙：开发机设了 `LEAGUE_RIFT_WALLS` 才跑（CI 没有文件，跳过）。墙边每一下推：晕的都撞上了真墙，停的地方站得住；
    /// 只有一层的旧格子在一路碰不到真墙的地方也晕。
    #[test]
    fn on_the_rifts_real_walls_every_stun_is_at_rock() {
        if std::env::var_os(terrain::RIFT_WALLS_ENV).is_none() {
            return;
        }
        let g = Grid::rift_layers(terrain::rift_walls(), terrain::rift_ground());
        let old = Grid::rift(terrain::rift_ground());
        assert!(g.rock.is_some(), "{}", terrain::rift_status());
        let (reach, body) = ((E_KB_SPEED * E_KB_T) as f64, 10_000.0);
        let (mut new_n, mut old_n, mut old_only) = (0, 0, 0);
        let mut y = 20_000.0;
        while y < terrain::RIFT_EXTENT {
            let mut x = 20_000.0;
            while x < terrain::RIFT_EXTENT {
                if !g.is_wall(x, y) {
                    for k in 0..16 {
                        let a = k as f64 * std::f64::consts::TAU / 16.0;
                        let d = (a.cos(), a.sin());
                        let new = wall_travel(&g, (x, y), d, reach, body);
                        let was = wall_travel(&old, (x, y), d, reach, body);
                        if let Some(len) = new {
                            new_n += 1;
                            let stop = (x + d.0 * len, y + d.1 * len);
                            assert!(!g.is_wall(stop.0, stop.1), "({x},{y}) {d:?}: stops in the ring at {stop:?}");
                            assert!(was.is_some(), "({x},{y}) {d:?}: the old grid saw no wall");
                        }
                        if was.is_some() {
                            old_n += 1;
                            old_only += new.is_none() as usize;
                        }
                    }
                }
                x += 40_000.0;
            }
            y += 40_000.0;
        }
        assert!(new_n > 300 && old_only * 10 > old_n, "{new_n} stuns now, {old_n} before ({old_only} without rock)");
    }

    #[test]
    fn home_on_the_rift_when_no_nexus_is_read() {
        let [blue, red] = rift_nexus();
        assert!(blue.1 > 1_400_000.0 && blue.0 < 200_000.0 && red.0 > 1_400_000.0 && red.1 < 200_000.0, "{blue:?} {red:?}");
        assert_eq!(home_nexus_in(&[(300_000.0, 1_300_000.0), (500_000.0, 1_500_000.0)], &rift_nexus()), Some(blue));
        assert_eq!(home_nexus_in(&[(1_300_000.0, 300_000.0)], &rift_nexus()), Some(red));
        assert_eq!(home_nexus_in(&[], &rift_nexus()), None);
    }

    #[test]
    fn names_fit_a_buff() {
        for s in ["push", "e_due", "e_go", "e_stun", "e_wall", "w_on", "w_hit", "w_low", "w_slow", "w_block"] {
            assert!(n(s).len() <= BUFF_NAME_CAP);
        }
    }

    #[test]
    fn the_copy_uses_the_natives_and_the_numbers() {
        let copy = include_str!("../override/league_poppy.data_champion");
        for r in ["league_poppy:charge", "league_poppy:verdict", "league_poppy:pick", "league_poppy:steadfast"] {
            assert!(copy.contains(r), "the copy never uses {r}");
        }
        for (k, v) in [("w_def", W_DEF), ("w_low", W_LOW), ("w_r", W_R), ("w_dmg", W_DMG), ("w_ap", W_AP), ("w_up", W_UP),
                       ("w_ground", W_GROUND), ("w_slow", W_SLOW), ("e_dmg", E_DMG), ("e_ratio", E_RATIO),
                       ("e_kb_speed", E_KB_SPEED), ("e_kb_t", E_KB_T), ("e_stun", E_STUN), ("p_sh_min", P_SH_MIN),
                       ("p_sh_max", P_SH_MAX), ("p_sh_t", P_SH_T), ("r_kb_speed", R_KB_SPEED), ("r_kb_t", R_KB_T), ("r_air", R_AIR),
                       ("r_far", R_FAR), ("r_far_speed", R_FAR_SPEED)] {
            assert!(copy.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        assert!(copy.contains("\"name\": \"league_poppy_w_on\""), "the copy never raises the aura flag");
        assert!(!copy.contains("\"type\": \"Knockback\""), "the copy still pushes in data");
    }

    /// 2026-11-13: the wall slam needs him at the wall; others' pushes through her aura are no dashes.
    #[test]
    fn the_slam_needs_the_wall_and_pushes_are_no_dashes() {
        let grids = Grid::builtin();
        let g = &grids[0];
        let body = 6_000.0;
        assert!(near_wall(g, (MOBA_BOUNDS.0 + body + 1_000.0, 480_000.0), body));
        assert!(!near_wall(g, (MOBA_BOUNDS.0 + body + 17_500.0, 480_000.0), body));
        assert!(!near_wall(g, (480_000.0, 480_000.0), body));
        // his own dash comes with his cast: still stopped; a knockback or another add-on's push (no cast): let through
        assert!(!external_push(true, true));
        assert!(external_push(true, false));
        // a blink (no forced move) is a dash as before
        assert!(!external_push(false, false));
        assert!(!external_push(false, true));
    }
}
