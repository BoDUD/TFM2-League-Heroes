//! 奥恩附加包（用户 2026-10-21：「技能方案 A」「做附加包」「有连招要做连招」）。主包保持纯数据；`mod.override_info` 把主包的
//! 奥恩换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_ornn.py 的 `native=1` 生成：技能、时机一字不改，只有下面
//! 几处换成本包的原生效果），本包补数据做不到的事（英雄联盟的规则）：
//!
//! - **熔岩柱是真的地形**（原生效果 `league_ornn:pillar`，火山突堑的裂隙到头时）：柱子立在裂隙的尽头，`Q_LIFE` tick；
//!   立起时站在上面的单位被推开，之后谁（两边的英雄、小兵、野怪，他自己也算）的中心进了柱子（`PILLAR_R` + 单位半径）就放回
//!   上一 tick 的位置。柱子的位置记在他身上的 buff 名里（`league_ornn_pillar@x,y`），被动读它：同一局的两份预模拟各记各的。
//!   主包：柱子只是画面，冲撞读他身上的 `league_ornn_q_pillar`。
//! - **撞上柱子或墙才地震**（原生效果 `league_ornn:from` 记冲撞的起点、`league_ornn:charge` 在撞上目标时判断）：撞上的那一刻
//!   柱子离他不到 `E_QUAKE_R` + `PILLAR_R`，或沿冲撞的方向 `WALL_REACH` 内是墙（卡蜜尔附加包的墙格、5v5 地图的四边），就给他挂
//!   1 tick 后数据读的 `league_ornn_e_quake_go`（周围击飞、伤害、易碎），柱子碎掉。主包：Q 后 4 秒内的冲撞都算撞上柱子。
//! - **易碎记在每个英雄身上**（原生效果 `league_ornn:shatter`，普攻打中时）：只有身上带着 `league_ornn_brittle` 的英雄被引爆：
//!   最大生命 `BR_HP`% 真实伤害、击飞 `BR_UP` tick、从他身边击退 `BR_KB_SPEED` x `BR_KB_T`，易碎随之去掉。主包：W / E / R
//!   打中英雄后他的下一下普攻打中任何英雄都引爆。
//! - **活体锻炉加强装备**（被动 `league_ornn:forge`，用户：「有装备系统吧 你可以加强装备属性吧」）：每 `FORGE_EVERY` tick 按他身上的
//!   装备把主属性（攻击、法强、护甲、生命、魔抗、攻速）再加 `P_ITEM`%：装备的属性从他身上的装备 buff 读（`item_buff_stats`），
//!   游戏的、数据 mod 的、原生 mod 的装备都一样（用户：「你也要能兼容mod的装备啊」）；一条都认不出来才退回游戏的装备表 `ITEMS`；`P_MASTER_LV` 级起锻造杰作
//!   （英雄联盟 13 级）：他自己 +`P_MASTER`%，每个友方英雄的装备 +`P_ALLY`%。只补差额的永久 buff（重挂生命会掉血）。主包：
//!   护甲、魔抗 +10%、生命 +6%（数据读不到装备）。
//! - **连招**（AI 钩子 `league_ornn:combo`，`combo.rs`）：AI 想放 E 而 Q 好着时先放 Q 立柱（Q → E）；柱子立着、E 好了、
//!   柱子旁边有敌方英雄时替 AI 按 E 撞过去；身边有易碎的英雄时普攻改打他。
//!
//! 数字是主包参数表 P 的同名项（大写）；`make_override.py` 生成副本时核对，不一致就停。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ornn.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `SPAWN`、`PILLAR`（立柱、推开）、`HOLD` / `PUSH`（挡在柱子外）、`CHARGE`（撞柱 / 撞墙 / 没撞）、`BROKEN`（柱子碎了）、
//! `SHATTER`（引爆易碎）、`Q FIRST` / `E PILLAR` / `BRITTLE`（连招），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

pub mod combo;

pub const ID: &str = "league_ornn";
const VERSION: &str = env!("CARGO_PKG_VERSION");

/// 主包参数表 P 的同名项：柱子留多久；易碎引爆（最大生命 %、击飞、击退速度和 tick）；地震半径；E 的动作长度、射程；Q 的射程。
pub const Q_LIFE: usize = 240;
pub const BR_HP: usize = 8;
pub const BR_UP: usize = 15;
pub const BR_KB_SPEED: usize = 1_500;
pub const BR_KB_T: usize = 8;
pub const E_QUAKE_R: usize = 30_000;
pub const E_ANIM: usize = 20;
pub const E_RANGE: usize = 55_000;
pub const Q_RANGE: usize = 75_000;
/// 活体锻炉：他的装备主属性 +`P_ITEM`%，`P_MASTER_LV` 级起锻造杰作：他自己 +`P_MASTER`%，每个友方英雄 +`P_ALLY`%。
pub const P_ITEM: usize = 20;
pub const P_MASTER: usize = 35;
pub const P_ALLY: usize = 10;
pub const P_MASTER_LV: usize = 9;
/// 多久按装备重算一次。
pub const FORGE_EVERY: usize = 30;

/// 装备的主属性（攻击、法强、护甲、生命、魔抗、攻速 %），游戏 0.6.4 的 `asset/base/setting/item_setting`（字典的键和
/// 装备自己的 `key` 都列上：铁剑的两个不一样）。吸血、暴击、穿透、减伤、韧性、冷却这些副属性不放大。
pub const ITEMS: [(&str, [i32; 6]); 31] = [
    ("iron_blade", [15, 0, 0, 0, 0, 0]),
    ("ironsword", [15, 0, 0, 0, 0, 0]),
    ("soldiers_longsword", [30, 0, 0, 0, 0, 0]),
    ("ruinous_blade", [50, 0, 0, 0, 0, 0]),
    ("conquerors_greatsword", [75, 0, 0, 0, 0, 0]),
    ("warlords_final_judgement", [100, 0, 0, 0, 0, 0]),
    ("dagger", [0, 0, 0, 0, 0, 10]),
    ("wind_dagger", [0, 0, 0, 0, 0, 20]),
    ("twin_stormblade", [0, 0, 0, 0, 0, 30]),
    ("thunderclaw", [0, 0, 0, 0, 0, 45]),
    ("storm_sovereign", [0, 0, 0, 0, 0, 60]),
    ("steel_armor", [0, 0, 20, 0, 0, 0]),
    ("gatekeepers_armor", [0, 0, 40, 0, 0, 0]),
    ("black_knights_heavy_plate", [0, 0, 70, 0, 0, 0]),
    ("eternal_iron_plate", [0, 0, 100, 0, 0, 0]),
    ("impregnable_fortress", [0, 0, 130, 0, 0, 0]),
    ("mystic_cloak", [0, 0, 0, 50, 30, 0]),
    ("night_hood", [0, 0, 0, 150, 60, 0]),
    ("dusk_raven", [0, 0, 0, 200, 100, 0]),
    ("souls_edge", [0, 0, 0, 300, 150, 0]),
    ("veil_of_annihilation", [0, 0, 0, 400, 200, 0]),
    ("arcane_crystal", [0, 30, 0, 0, 0, 0]),
    ("spirit_crystal", [0, 60, 0, 0, 0, 0]),
    ("staff_of_rapture", [0, 100, 0, 0, 0, 0]),
    ("angels_fang", [0, 150, 0, 0, 0, 0]),
    ("prophet_of_the_abyss", [0, 200, 0, 0, 0, 0]),
    ("vital_orb", [0, 0, 0, 100, 0, 0]),
    ("hardened_heart", [0, 0, 0, 200, 0, 0]),
    ("ring_of_reincarnation", [0, 0, 0, 300, 0, 0]),
    ("hourglass_of_eternity", [0, 0, 0, 500, 0, 0]),
    ("giants_horn_shard", [0, 0, 0, 800, 0, 0]),
];

/// 柱子的半径（单位半径另算）：英雄联盟的柱子差不多一个英雄那么粗。
pub const PILLAR_R: f64 = 7_000.0;
/// 撞上目标时前方这么近有墙算撞墙。
pub const WALL_REACH: f64 = 14_000.0;
/// 冲撞的起点记多久（E 的动作 + 冲刺最长的时间）。
pub const FROM_T: usize = E_ANIM + 120;
/// 单位半径读不到时用的值。
pub const BODY: f64 = 6_000.0;
/// 5v5 地图四边的可走范围（卡蜜尔附加包量的）。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);
/// 墙格的边长（世界单位）和查墙的步长。
pub const CELL: f64 = 32_000.0;
pub const STEP: f64 = 1_000.0;

const PILLAR_TAG: &str = "league_ornn_pillar@";
const FROM_TAG: &str = "league_ornn_from@";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ORNN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ornn.log");
        }
    }
    PathBuf::from("league_ornn.log")
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

pub(crate) fn head(sim: &StableSim<'_>, id: usize) -> String {
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

pub(crate) fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 规则（单元测试用） =====================

pub type Pt = (f64, f64);

pub(crate) fn n(name: &str) -> String {
    format!("{ID}_{name}")
}

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

pub fn unit(v: Pt) -> Option<Pt> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

/// 位置写进 buff 名：`<tag>x,y`（整数）。
pub fn tag(prefix: &str, at: Pt) -> String {
    format!("{prefix}{},{}", at.0.round() as i64, at.1.round() as i64)
}

/// buff 名里的位置（不是这个前缀就 None）。
pub fn untag(prefix: &str, name: &str) -> Option<Pt> {
    let rest = name.strip_prefix(prefix)?;
    let (x, y) = rest.split_once(',')?;
    Some((x.parse::<f64>().ok()?, y.parse::<f64>().ok()?))
}

/// 地图的墙格（卡蜜尔附加包的内置地图，波比、杰斯、巴德附加包同样用它）；5v5 地图另加四边。
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
    pub bounds: Option<(f64, f64, f64, f64)>,
}

impl Grid {
    pub fn from_rows(rows: &[&str], bounds: Option<(f64, f64, f64, f64)>) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(), bounds }
    }

    /// 0 = 5v5（四边也是墙），1 = 单线，2 = 死斗。
    pub fn builtin() -> [Grid; 3] {
        [
            Grid::from_rows(&maps::MOBA, Some(MOBA_BOUNDS)),
            Grid::from_rows(&maps::SINGLE_LANE, None),
            Grid::from_rows(&maps::DEATH_MATCH, None),
        ]
    }

    /// 世界坐标落在墙里吗（地图外、5v5 的四边外都算墙）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return true;
        }
        if let Some((x0, y0, x1, y1)) = self.bounds {
            if x < x0 || y < y0 || x > x1 || y > y1 {
                return true;
            }
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(true)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }
}

/// 当前对局的地图：英雄站进墙里最少的那张（同波比、杰斯、巴德附加包）。
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

/// 从 `at` 沿 `dir` 往前 `reach`（身体半径 `body`）内有墙吗。
pub fn wall_ahead(grid: &Grid, at: Pt, dir: Pt, reach: f64, body: f64) -> bool {
    let mut s = STEP;
    while s <= reach + body + 0.5 {
        if grid.is_wall(at.0 + dir.0 * s, at.1 + dir.1 * s) {
            return true;
        }
        s += STEP;
    }
    false
}

/// 撞上目标的那一刻：撞上柱子（离他够近的那根）还是墙，还是什么都没撞到。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Hit {
    Pillar(Pt),
    Wall,
    Nothing,
}

pub fn charge_hit(at: Pt, body: f64, pillars: &[Pt], wall: impl Fn() -> bool) -> Hit {
    let reach = E_QUAKE_R as f64 + PILLAR_R + body;
    if let Some(p) = pillars.iter().copied().filter(|&p| dist(p, at) <= reach).min_by(|a, b| dist(*a, at).total_cmp(&dist(*b, at)))
    {
        return Hit::Pillar(p);
    }
    if wall() {
        Hit::Wall
    } else {
        Hit::Nothing
    }
}

/// 柱子挡路：这一 tick 单位该在哪。进了柱子就回到上一 tick 的位置；上一 tick 也在柱子里（柱子刚立起来压在他身上），
/// 就沿柱心到他的方向推到柱子外。
pub fn hold(pillars: &[Pt], last: Option<Pt>, now: Pt, r: f64) -> Option<Pt> {
    let p = *pillars.iter().find(|&&p| dist(p, now) < PILLAR_R + r)?;
    match last {
        Some(l) if dist(p, l) >= PILLAR_R + r => Some(l),
        _ => {
            let d = unit((now.0 - p.0, now.1 - p.1)).unwrap_or((-1.0, 0.0));
            let k = PILLAR_R + r + 1.0;
            Some((p.0 + d.0 * k, p.1 + d.1 * k))
        }
    }
}

/// 易碎引爆的伤害：目标最大生命的 `BR_HP`%。
pub fn shatter_damage(max_hp: usize) -> usize {
    max_hp * BR_HP / 100
}

/// 一个人身上装备的主属性加起来（不认识的装备不算）。
pub fn item_stats<S: AsRef<str>>(keys: &[S]) -> [i32; 6] {
    let mut sum = [0; 6];
    for k in keys {
        if let Some((_, s)) = ITEMS.iter().find(|(name, _)| *name == k.as_ref()) {
            for i in 0..6 {
                sum[i] += s[i];
            }
        }
    }
    sum
}

/// 一条 buff 的主属性（攻击、法强、护甲、生命、魔抗、攻速 %）。
pub fn main_stats(b: &BuffV1) -> [i32; 6] {
    [b.attack, b.magic_power, b.defence, b.hp, b.magic_resistance, b.attack_speed_mult]
}

/// 装备 buff 是哪些：永久、名字是空的（装备表里装备的 `stat.name` 都是空的）或等于他身上某件装备的名字。
/// 游戏的装备、数据 mod 的装备（装备表合并进来）、原生 mod 的装备（`StableItem::stat`）都是这样挂在英雄身上的属性 buff，
/// 所以从 buff 读能兼容任何 mod 的装备。一条都认不出来就 None（调用的地方退回 `ITEMS` 表）。
pub fn item_buff_stats<S: AsRef<str>>(buffs: &[(String, bool, [i32; 6])], keys: &[S]) -> Option<[i32; 6]> {
    let mut sum = [0; 6];
    let mut any = false;
    for (name, permanent, s) in buffs {
        if *permanent && (name.is_empty() || keys.iter().any(|k| k.as_ref() == name)) {
            any = true;
            for i in 0..6 {
                sum[i] += s[i];
            }
        }
    }
    any.then_some(sum)
}

/// 放大的那部分：每项的 `pct`%（向下取整）。
pub fn forged(sum: [i32; 6], pct: usize) -> [i32; 6] {
    sum.map(|v| v * pct as i32 / 100)
}

/// 他的等级下：他自己、友方英雄各放大多少 %。
pub fn forge_pct(level: usize) -> (usize, usize) {
    if level >= P_MASTER_LV {
        (P_MASTER, P_ALLY)
    } else {
        (P_ITEM, 0)
    }
}

/// 已经加上的 `have` 要变成 `want`：只多不少就补一个差额 buff（不动已有的，免得重挂生命时掉血），否则整个换掉。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Change {
    Keep,
    Add([i32; 6]),
    Replace([i32; 6]),
}

pub fn change(have: [i32; 6], want: [i32; 6]) -> Change {
    if have == want {
        Change::Keep
    } else if (0..6).all(|i| want[i] >= have[i]) {
        Change::Add(std::array::from_fn(|i| want[i] - have[i]))
    } else {
        Change::Replace(want)
    }
}

fn stat_buff(name: &str, s: [i32; 6]) -> BuffV1 {
    let mut b = BuffV1::named(name);
    b.duration_kind = BuffDurationV1::Permanent.code();
    b.attack = s[0];
    b.magic_power = s[1];
    b.defence = s[2];
    b.hp = s[3];
    b.magic_resistance = s[4];
    b.attack_speed_mult = s[5];
    b
}

// ===================== 游戏里 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

pub(crate) fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    buffs(sim, id).iter().any(|b| b.name() == name)
}

fn cc_immune(sim: &StableSim<'_>, id: usize) -> bool {
    buffs(sim, id).iter().any(|b| b.cc_immune)
}

pub(crate) fn pos(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

fn pt(p: Pt) -> String {
    format!("({:.0}, {:.0})", p.0, p.1)
}

/// 他身上记着的柱子（buff 名里的位置），和那条 buff 的名字。
pub(crate) fn pillars_of(sim: &StableSim<'_>, me: usize) -> Vec<(String, Pt)> {
    buffs(sim, me).iter().filter_map(|b| untag(PILLAR_TAG, b.name()).map(|p| (b.name().to_string(), p))).collect()
}

fn from_of(sim: &StableSim<'_>, me: usize) -> Option<Pt> {
    buffs(sim, me).iter().find_map(|b| untag(FROM_TAG, b.name()))
}

fn champion_points(sim: &StableSim<'_>) -> Vec<Pt> {
    (0..sim.champion_count()).filter_map(|i| pos(sim, sim.champion_id_at(i))).collect()
}

fn grid_now(sim: &StableSim<'_>) -> Option<Grid> {
    let grids = Grid::builtin();
    let i = current(&grids, &champion_points(sim))?;
    grids.into_iter().nth(i)
}

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

/// 裂隙到头：在尽头立柱子（他身上记一条 `Q_LIFE` tick 的 buff，旧的柱子换掉）。
fn pillar(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let at = match InputTargetKindV1::from_code(input.kind) {
        Some(InputTargetKindV1::Pos) => (input.x as f64, input.y as f64),
        Some(InputTargetKindV1::Target) => match pos(sim, input.target_id) {
            Some(p) => p,
            None => return,
        },
        _ => return,
    };
    for (name, _) in pillars_of(sim, me) {
        sim.entity_remove_buff(me, &name);
    }
    sim.add_buff(me, &BuffV1::timed(&tag(PILLAR_TAG, at), Q_LIFE));
    if let Some(k) = counted("pillar") {
        wlog(format!("{} PILLAR at {} for {Q_LIFE} ticks #{k}", head(sim, me), pt(at)));
    }
}

/// E 出手：记下冲撞的起点。
fn from(sim: &mut StableSim<'_>, me: usize, _input: InputTargetV1) {
    let Some(at) = pos(sim, me) else { return };
    for b in buffs(sim, me).iter().filter(|b| b.name().starts_with(FROM_TAG)) {
        sim.entity_remove_buff(me, b.name());
    }
    sim.add_buff(me, &BuffV1::timed(&tag(FROM_TAG, at), FROM_T));
}

/// 冲撞撞上目标：柱子够近或前方是墙就地震（数据 1 tick 后读 `e_quake_go`），柱子碎掉。
fn charge(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(at) = pos(sim, me) else { return };
    let body = sim.get_entity(me).map_or(BODY, |e| match e.radius() as f64 { r if r > 0.0 => r, _ => BODY });
    let pillars = pillars_of(sim, me);
    let points: Vec<Pt> = pillars.iter().map(|(_, p)| *p).collect();
    let dir = from_of(sim, me)
        .and_then(|f| unit((at.0 - f.0, at.1 - f.1)))
        .or_else(|| target_of(&input).and_then(|t| pos(sim, t)).and_then(|t| unit((t.0 - at.0, t.1 - at.1))));
    let grid = grid_now(sim);
    let hit = charge_hit(at, body, &points, || match (&grid, dir) {
        (Some(g), Some(d)) => wall_ahead(g, at, d, WALL_REACH, body),
        _ => false,
    });
    match hit {
        Hit::Pillar(p) => {
            for (name, q) in &pillars {
                if *q == p {
                    sim.entity_remove_buff(me, name);
                }
            }
            sim.entity_remove_buff(me, &n("q_pillar"));
            sim.add_buff(me, &BuffV1::timed(&n("e_quake_go"), 3));
            if let Some(k) = counted("charge pillar") {
                wlog(format!("{} CHARGE into the pillar at {} ({:.0} away): quake #{k}", head(sim, me), pt(p), dist(p, at)));
            }
        }
        Hit::Wall => {
            sim.add_buff(me, &BuffV1::timed(&n("e_quake_go"), 3));
            if let Some(k) = counted("charge wall") {
                wlog(format!("{} CHARGE into a wall at {}: quake #{k}", head(sim, me), pt(at)));
            }
        }
        Hit::Nothing => {
            if let Some(k) = counted("charge none") {
                wlog(format!("{} CHARGE at {}: no pillar or wall, no quake #{k}", head(sim, me), pt(at)));
            }
        }
    }
    for b in buffs(sim, me).iter().filter(|b| b.name().starts_with(FROM_TAG)) {
        sim.entity_remove_buff(me, b.name());
    }
}

/// 普攻打中一个带易碎的英雄：引爆（数据 1 tick 后读 `br_now` 播画面和声音）。
fn shatter(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let brittle = n("brittle");
    let Some(max) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_champion()).map(|e| e.hp().1) else { return };
    if !has_buff(sim, target, &brittle) {
        return;
    }
    sim.entity_remove_buff(target, &brittle);
    let dmg = shatter_damage(max);
    sim.deal_damage_typed(me, target, dmg, DamageTypeV1::Fixed, AttackTypeV1::BaseAttack);
    if !cc_immune(sim, target) {
        sim.apply_cc(target, &CcV1::of_kind(CcKindV1::Airborne, BR_UP as u64));
        sim.entity_knockback(me, target, BR_KB_SPEED, BR_KB_T);
    }
    sim.add_buff(me, &BuffV1::timed(&n("br_now"), 3));
    if let Some(k) = counted("shatter") {
        wlog(format!("{} SHATTER {}: {dmg} true damage ({BR_HP}% of {max}), knocked up #{k}", head(sim, me), who(sim, target)));
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 被动：柱子挡路 =====================

#[derive(Clone, Default)]
struct Forge {
    me: usize,
    /// 立着的柱子：位置、倒下的 tick（他阵亡时 buff 停住不走，柱子照样按时倒）。
    up: Vec<(Pt, usize)>,
    /// 柱子立着时每个单位上一 tick 的位置。
    last_pos: HashMap<usize, Pt>,
    /// 锻造已经加在每个单位身上的属性（单位编号 -> 主属性）：他自己的 `forged`、友方英雄的 `masterwork`。
    forged: HashMap<usize, [i32; 6]>,
    /// 锻造杰作记过日志没有。
    master_seen: bool,
}

impl Forge {
    /// 活体锻炉：每 `FORGE_EVERY` tick 按身上的装备补上放大的那部分（他自己；杰作后还有每个友方英雄）。
    fn forge(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let mut level = 1;
        let mut rows = Vec::new();
        for i in 0..sim.player_count() {
            let Some(pl) = sim.player_at(i) else { continue };
            if pl.team() != team {
                continue;
            }
            let Some(c) = pl.champion() else { continue };
            let id = c.id();
            let keys = pl.item_keys();
            if id == me {
                level = pl.level();
            }
            let on: Vec<(String, bool, [i32; 6])> = (0..c.buff_count())
                .filter_map(|j| c.buff_at(j))
                .map(|b| (b.name().to_string(), BuffDurationV1::from_code(b.duration_kind) == Some(BuffDurationV1::Permanent),
                          main_stats(&b)))
                .collect();
            // the item buffs on him (any mod's items); none found: the game's table
            let (sum, from) = match item_buff_stats(&on, &keys) {
                Some(s) => (s, "item buffs"),
                None => (item_stats(&keys), "the table"),
            };
            if !keys.is_empty() {
                if let Some(k) = counted(if from == "the table" { "items table" } else { "items buffs" }) {
                    let names: Vec<&str> = on.iter().filter(|(_, p, _)| *p).map(|(n, _, _)| n.as_str()).collect();
                    wlog(format!("{} ITEMS of #{id} {keys:?} read from {from}: {sum:?}; his permanent buffs {names:?} #{k}",
                                 head(sim, me)));
                }
            }
            rows.push((id, c.is_alive(), sum));
        }
        let (mine, ally) = forge_pct(level);
        if ally > 0 && !self.master_seen {
            self.master_seen = true;
            if let Some(k) = counted("masterwork") {
                wlog(format!("{} MASTERWORK at level {level}: his items +{mine}%, his allies' +{ally}% #{k}", head(sim, me)));
            }
        }
        for (id, alive, sum) in rows {
            if !alive {
                continue;
            }
            let own = id == me;
            let want = forged(sum, if own { mine } else { ally });
            let name = n(if own { "forged" } else { "masterwork" });
            let have = if has_buff(sim, id, &name) { self.forged.get(&id).copied().unwrap_or([0; 6]) } else { [0; 6] };
            match change(have, want) {
                Change::Keep => continue,
                Change::Add(d) => sim.add_buff(id, &stat_buff(&name, d)),
                Change::Replace(w) => {
                    sim.entity_remove_buff(id, &name);
                    if w != [0; 6] {
                        sim.add_buff(id, &stat_buff(&name, w));
                    }
                }
            }
            self.forged.insert(id, want);
            if let Some(k) = counted(if own { "forge" } else { "forge ally" }) {
                wlog(format!("{} FORGE {}: +{:?} (attack, AP, armour, health, MR, attack speed %) #{k}", head(sim, me),
                             who(sim, id), want));
            }
        }
    }

    /// 他身上新记的柱子加进来；buff 没了（撞碎、被换掉）且他活着就去掉。
    fn sync(&mut self, sim: &StableSim<'_>, me: usize, now: usize, alive: bool) {
        let marked: Vec<Pt> = pillars_of(sim, me).into_iter().map(|(_, p)| p).collect();
        for &p in &marked {
            if !self.up.iter().any(|&(q, _)| q == p) {
                self.up.push((p, now + Q_LIFE));
            }
        }
        if alive {
            let gone: Vec<Pt> = self.up.iter().map(|&(q, _)| q).filter(|q| !marked.contains(q)).collect();
            for q in gone {
                self.up.retain(|&(p, _)| p != q);
                if let Some(k) = counted("broken") {
                    wlog(format!("{} BROKEN: the pillar at {} is gone #{k}", head(sim, me), pt(q)));
                }
            }
        }
        self.up.retain(|&(_, until)| now < until);
    }

    fn block(&mut self, sim: &mut StableSim<'_>) {
        if self.up.is_empty() {
            self.last_pos.clear();
            return;
        }
        let pillars: Vec<Pt> = self.up.iter().map(|&(p, _)| p).collect();
        let mut moves = Vec::new();
        let mut seen = HashMap::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() {
                continue;
            }
            match e.kind() {
                Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Summon) => {}
                _ => continue,
            }
            let id = e.id();
            let now_pos = (e.pos().0 as f64, e.pos().1 as f64);
            let r = match e.radius() as f64 { r if r > 0.0 => r, _ => BODY };
            let last = self.last_pos.get(&id).copied();
            let at = match hold(&pillars, last, now_pos, r) {
                Some(q) => {
                    moves.push((id, q, last.is_some_and(|l| pillars.iter().all(|&p| dist(p, l) >= PILLAR_R + r))));
                    q
                }
                None => now_pos,
            };
            seen.insert(id, at);
        }
        for (id, (x, y), was_out) in moves {
            sim.entity_set_pos(id, x.max(0.0).round() as u64, y.max(0.0).round() as u64);
            if let Some(k) = counted(if was_out { "hold" } else { "push" }) {
                wlog(format!("{} {} #{k}: {} kept out of the pillar at ({x:.0}, {y:.0})", head(sim, self.me),
                             if was_out { "HOLD" } else { "PUSH" }, who(sim, id)));
            }
        }
        self.last_pos = seen;
    }
}

impl StablePassive for Forge {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.last_pos.clear();
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: the add-on's Ornn (player {player}, team {team})", head(sim, me)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        self.sync(sim, me, now, alive);
        self.block(sim);
        if now % FORGE_EVERY == 0 {
            self.forge(sim, me);
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
        "=== {ID} v{VERSION} (Ornn: a real magma pillar, quakes on pillars and walls, Brittle per champion, the combos) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:pillar"), Step(pillar));
    module.add_native_effect(format!("{ID}:from"), Step(from));
    module.add_native_effect(format!("{ID}:charge"), Step(charge));
    module.add_native_effect(format!("{ID}:shatter"), Step(shatter));
    module.add_native_passive(format!("{ID}:forge"), Forge::default());
    module.add_player_input_ai(combo::Combo);
    host.log(LogLevel::Info, "league_ornn loaded (a real pillar, quakes on pillars and walls, Brittle per champion, the combos).");
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
    fn a_place_survives_its_buff_name() {
        let s = tag(PILLAR_TAG, (412_345.4, 98_765.6));
        assert_eq!(s, "league_ornn_pillar@412345,98766");
        assert!(s.len() <= BUFF_NAME_CAP);
        assert_eq!(untag(PILLAR_TAG, &s), Some((412_345.0, 98_766.0)));
        assert_eq!(untag(PILLAR_TAG, "league_ornn_q_pillar"), None);
        assert_eq!(untag(FROM_TAG, &s), None);
    }

    #[test]
    fn the_charge_quakes_on_a_near_pillar_first() {
        let at = (500_000.0, 400_000.0);
        let near = (530_000.0, 400_000.0);
        let far = (600_000.0, 400_000.0);
        assert_eq!(charge_hit(at, 6000.0, &[far, near], || true), Hit::Pillar(near));
        assert_eq!(charge_hit(at, 6000.0, &[far], || true), Hit::Wall);
        assert_eq!(charge_hit(at, 6000.0, &[far], || false), Hit::Nothing);
        assert_eq!(charge_hit(at, 6000.0, &[], || false), Hit::Nothing);
    }

    #[test]
    fn the_map_edge_is_a_wall() {
        let g = &Grid::builtin()[0];
        // near the left edge, charging left: the edge is within reach
        assert!(wall_ahead(g, (30_000.0, 480_000.0), (-1.0, 0.0), WALL_REACH, 6000.0));
    }

    #[test]
    fn units_stay_out_of_the_pillar() {
        let p = [(500_000.0, 400_000.0)];
        // walking in from the left: back to where it was
        assert_eq!(hold(&p, Some((485_000.0, 400_000.0)), (490_000.0, 400_000.0), 6000.0), Some((485_000.0, 400_000.0)));
        // far away: free
        assert_eq!(hold(&p, Some((450_000.0, 400_000.0)), (455_000.0, 400_000.0), 6000.0), None);
        // standing on it when it rises: pushed straight out from its centre
        let out = hold(&p, None, (503_000.0, 400_000.0), 6000.0).unwrap();
        assert!((out.0 - (500_000.0 + PILLAR_R + 6001.0)).abs() < 1.0 && (out.1 - 400_000.0).abs() < 1.0);
    }

    #[test]
    fn the_forge_scales_the_items_main_stats() {
        let s = item_stats(&["giants_horn_shard", "impregnable_fortress", "night_hood", "a_mod_item"]);
        assert_eq!(s, [0, 0, 130, 950, 60, 0]);
        assert_eq!(forged(s, P_ITEM), [0, 0, 26, 190, 12, 0]);
        assert_eq!(forge_pct(1), (P_ITEM, 0));
        assert_eq!(forge_pct(P_MASTER_LV), (P_MASTER, P_ALLY));
        // both spellings of the iron sword
        assert_eq!(item_stats(&["ironsword"]), item_stats(&["iron_blade"]));
        assert_eq!(ITEMS.len(), 31);
    }

    #[test]
    fn any_mods_items_come_from_their_buffs() {
        let keys = ["steel_armor", "a_mods_sword"];
        let on = vec![
            ("steel_armor".to_string(), true, [0, 0, 20, 0, 0, 0]),
            ("a_mods_sword".to_string(), true, [40, 0, 0, 0, 0, 15]),
            ("".to_string(), true, [0, 0, 0, 100, 0, 0]),
            // his own flags and the forge's buff are not items
            ("league_ornn_forged".to_string(), true, [0, 0, 4, 0, 0, 0]),
            ("league_ornn_q_slow".to_string(), false, [0, 0, 0, 0, 0, 0]),
            // a timed buff named like an item is not one
            ("".to_string(), false, [99, 0, 0, 0, 0, 0]),
        ];
        assert_eq!(item_buff_stats(&on, &keys), Some([40, 0, 20, 100, 0, 15]));
        assert_eq!(item_buff_stats(&on[3..5], &keys), None);
    }

    #[test]
    fn the_forge_only_adds_the_difference() {
        assert_eq!(change([0, 0, 26, 190, 12, 0], [0, 0, 26, 190, 12, 0]), Change::Keep);
        assert_eq!(change([0, 0, 26, 190, 12, 0], [0, 0, 45, 332, 21, 0]), Change::Add([0, 0, 19, 142, 9, 0]));
        assert_eq!(change([0, 0, 26, 190, 12, 0], [0, 0, 30, 100, 12, 0]), Change::Replace([0, 0, 30, 100, 12, 0]));
    }

    #[test]
    fn shatter_is_a_share_of_max_health() {
        assert_eq!(shatter_damage(2000), 2000 * BR_HP / 100);
    }
}
