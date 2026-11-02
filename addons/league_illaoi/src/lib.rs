//! 俄洛伊附加包（用户 2026-10-23：「俄洛伊不用做附加包吗」「附加包就按这四项做」）：主包的数据做不到的四件事。
//!
//! `mod.override_info` 把主包的俄洛伊换成 `override/` 里的副本（tools/kit/build_illaoi.py 的 native=1）：普攻、W、E、R
//! 和主包一样，只是触手全交给本包：长触手的地方给她挂 2 tick 的信号（`league_illaoi_p_new` 普攻时、`league_illaoi_r_new`
//! 大招落地时），E 的灵魂不再是「受到伤害增加」，W 打中后不再由数据抽打；被动挂本包的 `league_illaoi:prophet`。
//!
//! - **触手贴着墙长**（0.2.0 照英雄联盟，用户 2026-10-23：「俄洛伊触手乱长 和英雄联盟逻辑不一样」，选了「墙边优先，没墙长
//!   身边」）：不再跟着普攻长，按被动自己的冷却长——1 级 `p_cd_1` tick、18 级 `p_cd_18`（英雄联盟 20 – 10 秒），每条活
//!   `t_long`（英雄联盟 60 秒），同时最多 `t_most` 条，新的挤掉最老的（它沉下去）。本包读这局的墙格子（卡密尔附加包内置的
//!   三张地图，`league_camille_wall/src/maps.rs`），在她身边 `p_reach` 内找离她最近的「墙边」——挨着墙的空地格子的中心，
//!   往墙那边靠半格；附近没有墙就长在她身边 `t_place`（朝最近敌人的左右两侧轮着来）。大招：每个 `r_r` 内的敌方英雄身边
//!   各长一条（同样先找墙边）；躯壳：身边长一条。画面分三段在原地接着播：冒出来、摆动（活多久摆多久）、沉下去。
//! - **触手什么时候抽**（选了「照联盟：W、灵魂、躯壳才抽」）：平时不动。严酷训诫打中谁（新挂上 `w_mark`），`t_r` 的 1.5
//!   倍内的每条触手隔 `w_gap` tick 依次抽他一下；`t_r` 内有灵魂被扯出来的英雄或躯壳，每 `t_per` tick 抽一下；Q 并进了被动：
//!   她打中敌人时，离目标最近、够得着的那条触手抽目标一下，`q_cd` tick 一次；她大招期间触手每 `r_per` tick 抽 `t_r` 内的
//!   敌方英雄（先抽带灵魂的和躯壳）。物理伤害 `t_dmg` + `t_ratio`% 攻击力；抽中英雄她回 `p_heal` + `p_heal_r`% 攻击力。
//! - **灵魂分担伤害**：E 打中的英雄挂着 `e_spirit` 时，她打他的每一下（普攻和技能，`on_attack`）多算 `e_echo`%。
//! - **灵魂站在外面、连着线**（用户：「拉灵魂没有特效 完全看不出」，选了「灵魂站在外面+连线」）：灵魂从他身上朝她扯出
//!   `e_pull`，站在那里（`e_soul` 每 36 tick 播一遍，副本里不再画在他身上），每 tick 沿他和灵魂之间铺一串 `e_tether`
//!   （每节 `LINK_STEP` 远，投射物画面会转向）。他走出离灵魂 `e_leash` 外，或灵魂的 `e_t` tick 到了，就去掉
//!   `e_spirit`、挂 `e_vessel`（`e_vt` tick），播灵魂碎裂，身边长一条触手。
//!
//! 每个计时都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_illaoi.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;
pub mod souls;

const ID: &str = "league_illaoi";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_illaoi") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
const HERO: &str = "league_illaoi";
/// 触手画面的三段（tools/art/rig_illaoi.py TENT_PARTS）：冒出来、一次摆动、沉下去，tick。
pub const RISE_T: usize = 13;
pub const SWAY_T: usize = 72;
pub const SINK_T: usize = 18;
/// 灵魂画面（e_spirit，6 帧 x 100 ms）多久重播一次；灵魂线每节多远（tools/art/fx_illaoi_tether.py LENGTH x 1000）。
pub const SOUL_T: usize = 36;
pub const LINK_STEP: f64 = 10_000.0;
/// 本体一 tick 横着走了这么远才算转身（站着打、被推一下不算）。
pub const TURN: f64 = 300.0;
/// 灵魂挨打时飞回本体的鬼手多快（一 tick）。
pub const PULSE_SPEED: u64 = 8_000;
/// 墙格子每格的世界单位（地图的 `walls`，卡密尔附加包同）。
const CELL: f64 = 32000.0;

fn il(x: &str) -> String {
    format!("{HERO}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ILLAOI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_illaoi.log");
        }
    }
    PathBuf::from("league_illaoi.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the simulation thread in game, league_talon_vault)
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

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        _ => "unknown",
    };
    format!("[{kind} t={}] #{id}", sim.tick())
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 触手够得着的半径（主包 t_r）。
    pub t_r: u64,
    /// 触手活多少 tick（主包 t_life）。
    pub t_life: usize,
    /// 触手多久抽一下（主包 t_per；她大招期间 r_per）。
    pub t_per: usize,
    pub r_per: usize,
    /// 长出来后多久抽第一下（主包 t_first）。
    pub t_first: usize,
    /// 一下的伤害：t_dmg + t_ratio% 攻击力。
    pub t_dmg: usize,
    pub t_ratio: usize,
    /// 抽中英雄她回的血：p_heal + p_heal_r% 攻击力。
    pub p_heal: usize,
    pub p_heal_r: usize,
    /// 找墙的半径、没墙时长在身前多远（主包 p_reach / t_place）。
    pub p_reach: u64,
    pub t_place: u64,
    /// 大招长触手的半径（主包 r_r）。
    pub r_r: u64,
    /// 灵魂：持续、分担的百分比、拉断的距离、躯壳持续（主包 e_t / e_echo / e_leash / e_vt）。
    pub e_t: usize,
    pub e_echo: usize,
    pub e_leash: u64,
    pub e_vt: usize,
    /// 严酷训诫的标记持续、触手依次抽他的间隔（主包 w_mark_t / w_gap）。
    pub w_mark_t: usize,
    pub w_gap: usize,
    /// 长一条的冷却：1 级、18 级（之间按等级线性），每条活多久，同时最多几条（主包 p_cd_1 / p_cd_18 / t_long / t_most）。
    pub p_cd_1: usize,
    pub p_cd_18: usize,
    pub t_long: usize,
    pub t_most: usize,
    /// 并进被动的 Q：最近的触手抽她打中的目标，多久一次（主包 q_cd）；灵魂从身上扯出多远（e_pull）。
    pub q_cd: usize,
    pub e_pull: u64,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            t_r: 30000,
            t_life: 360,
            t_per: 90,
            r_per: 60,
            t_first: 40,
            t_dmg: 10,
            t_ratio: 35,
            p_heal: 6,
            p_heal_r: 6,
            p_reach: 60000,
            t_place: 15000,
            r_r: 45000,
            e_t: 300,
            e_echo: 15,
            e_leash: 150000,
            e_vt: 240,
            w_mark_t: 240,
            w_gap: 6,
            p_cd_1: 1200,
            p_cd_18: 600,
            t_long: 3600,
            t_most: 4,
            q_cd: 480,
            e_pull: 40000,
        }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        let u = v.max(0) as usize;
        match k {
            "t_r" => p.t_r = u as u64,
            "t_life" => p.t_life = u,
            "t_per" => p.t_per = u.max(1),
            "r_per" => p.r_per = u.max(1),
            "t_first" => p.t_first = u,
            "t_dmg" => p.t_dmg = u,
            "t_ratio" => p.t_ratio = u,
            "p_heal" => p.p_heal = u,
            "p_heal_r" => p.p_heal_r = u,
            "p_reach" => p.p_reach = u as u64,
            "t_place" => p.t_place = u as u64,
            "r_r" => p.r_r = u as u64,
            "e_t" => p.e_t = u,
            "e_echo" => p.e_echo = u,
            "e_leash" => p.e_leash = u as u64,
            "e_vt" => p.e_vt = u,
            "w_mark_t" => p.w_mark_t = u,
            "w_gap" => p.w_gap = u,
            "p_cd_1" => p.p_cd_1 = u.max(1),
            "p_cd_18" => p.p_cd_18 = u.max(1),
            "t_long" => p.t_long = u,
            "t_most" => p.t_most = u.max(1),
            "q_cd" => p.q_cd = u,
            "e_pull" => p.e_pull = u as u64,
            _ => {}
        }
    }
    p
}

// ===================== 墙（单元测试用） =====================

/// 一张墙格子：`cells[y][x]` 为真是墙（`maps.rs` 的 `#`）。
#[derive(Clone, Debug, PartialEq)]
pub struct Walls {
    pub cells: Vec<Vec<bool>>,
}

impl Walls {
    pub fn from_rows(rows: &[&str]) -> Walls {
        Walls { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect() }
    }

    fn wall_at(&self, cx: i64, cy: i64) -> bool {
        if cx < 0 || cy < 0 {
            return false; // 地图外不算（只找地图里的墙）
        }
        self.cells.get(cy as usize).and_then(|r| r.get(cx as usize)).copied().unwrap_or(false)
    }

    /// 世界坐标在墙里吗（地图外算墙）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return true;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(true)
    }

    pub fn count(&self) -> usize {
        self.cells.iter().flatten().filter(|c| **c).count()
    }

    /// `at` 附近 `reach` 内离 `at` 最近的墙边：挨着墙（上下左右）的空地格子的中心，往墙那边靠半格（触手贴着墙）。
    pub fn edge_near(&self, at: (f64, f64), reach: f64) -> Option<(f64, f64)> {
        let (cx, cy) = ((at.0 / CELL).floor() as i64, (at.1 / CELL).floor() as i64);
        let k = (reach / CELL).ceil() as i64 + 1;
        let mut best: Option<((f64, f64), f64)> = None;
        for y in cy - k..=cy + k {
            for x in cx - k..=cx + k {
                if x < 0 || y < 0 || self.wall_at(x, y) || y as usize >= self.cells.len() {
                    continue;
                }
                if x as usize >= self.cells[y as usize].len() {
                    continue;
                }
                let toward: Vec<(f64, f64)> = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    .iter()
                    .filter(|(dx, dy)| self.wall_at(x + dx, y + dy))
                    .map(|(dx, dy)| (*dx as f64, *dy as f64))
                    .collect();
                if toward.is_empty() {
                    continue;
                }
                let n = toward.len() as f64;
                let (sx, sy) = toward.iter().fold((0.0, 0.0), |a, b| (a.0 + b.0, a.1 + b.1));
                let spot = ((x as f64 + 0.5 + 0.35 * sx / n) * CELL, (y as f64 + 0.5 + 0.35 * sy / n) * CELL);
                let d = dist(spot, at);
                if d <= reach && best.is_none_or(|(_, bd)| d < bd) {
                    best = Some((spot, d));
                }
            }
        }
        best.map(|(s, _)| s)
    }
}

pub fn builtin(mode: GameModeKindV1) -> Walls {
    Walls::from_rows(match mode {
        GameModeKindV1::Moba => &maps::MOBA,
        GameModeKindV1::SingleLane => &maps::SINGLE_LANE,
        GameModeKindV1::DeathMatch => &maps::DEATH_MATCH,
    })
}

/// 这局的地图：站进墙里的单位最少的那张，一样少时墙最多的（卡密尔附加包的 pick_grid）。
pub fn pick(points: &[(f64, f64)]) -> Walls {
    [GameModeKindV1::Moba, GameModeKindV1::SingleLane, GameModeKindV1::DeathMatch]
        .into_iter()
        .map(builtin)
        .map(|w| (points.iter().filter(|p| w.is_wall(p.0, p.1)).count(), w.count(), w))
        .min_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)))
        .map(|(_, _, w)| w)
        .unwrap_or_else(|| builtin(GameModeKindV1::Moba))
}

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 没有墙时长在她身边：朝最近敌人的方向转 90 度（`side` 为 1 或 -1，左右轮着），离她 `reach`；没有敌人就在她左右。
pub fn beside(from: (f64, f64), foe: Option<(f64, f64)>, reach: f64, side: f64) -> (f64, f64) {
    let (dx, dy) = match foe {
        Some(t) if dist(from, t) > 1.0 => {
            let d = dist(from, t);
            ((t.0 - from.0) / d, (t.1 - from.1) / d)
        }
        _ => (0.0, 1.0),
    };
    (from.0 - dy * side * reach, from.1 + dx * side * reach)
}

/// 长一条触手的冷却：1 级 `p_cd_1`，18 级 `p_cd_18`，中间按等级线性（英雄联盟 20 – 10 秒）。
pub fn grow_cd(level: usize, p: &Params) -> usize {
    let l = level.clamp(1, 18) as f64;
    let (a, b) = (p.p_cd_1 as f64, p.p_cd_18 as f64);
    (a + (b - a) * (l - 1.0) / 17.0).round() as usize
}

/// 触手从 `start` 长出来，活够 `t_long`：冒出来以后整段整段地摆，到最后一段摆完的那一 tick 沉下去。
pub fn life_end(start: usize, t_long: usize) -> usize {
    let sways = (t_long.saturating_sub(RISE_T) + SWAY_T - 1) / SWAY_T;
    start + RISE_T + sways.max(1) * SWAY_T
}

/// 灵魂的画面名：英雄联盟的英雄有自己的（`souls.rs`；朝左的是镜像 `_l`），别的用通用幽灵 `e_soul`。
pub fn soul_look(champion: &str, left: bool) -> String {
    if souls::SOULS.binary_search(&champion).is_ok() {
        il(&format!("soul_{champion}{}", if left { "_l" } else { "" }))
    } else {
        il("e_soul")
    }
}

/// 本体朝哪边：这一 tick 往左走了 `TURN` 以上就朝左，往右就朝右，没怎么动就照旧（引擎接口读不到朝向）。
pub fn faces_left(was: bool, dx: f64) -> bool {
    if dx < -TURN {
        true
    } else if dx > TURN {
        false
    } else {
        was
    }
}

/// 灵魂站的地方：从他身上朝她扯出 `pull`（她比这还近就站在两人中间）。
pub fn spirit_spot(body: (f64, f64), her: (f64, f64), pull: f64) -> (f64, f64) {
    let d = dist(body, her);
    if d < 1.0 {
        return body;
    }
    let k = pull.min(d / 2.0) / d;
    (body.0 + (her.0 - body.0) * k, body.1 + (her.1 - body.1) * k)
}

/// 灵魂线：从 `a` 到 `b` 每 `step` 一节，每节的中心和方向（单位向量）。
pub fn tether_links(a: (f64, f64), b: (f64, f64), step: f64) -> Vec<((f64, f64), (f64, f64))> {
    let d = dist(a, b);
    if d < step / 2.0 {
        return Vec::new();
    }
    let n = (d / step).ceil() as usize;
    let (ux, uy) = ((b.0 - a.0) / d, (b.1 - a.1) / d);
    let len = d / n as f64;
    (0..n).map(|k| ((a.0 + ux * len * (k as f64 + 0.5), a.1 + uy * len * (k as f64 + 0.5)), (ux, uy))).collect()
}

// ===================== 选目标（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub pos: (f64, f64),
    pub champion: bool,
    /// 灵魂被扯出来的、躯壳：触手会抽。
    pub marked: bool,
}

/// 触手自己抽谁（严酷训诫和 Q 另算）：够得着的灵魂、躯壳（`marked`），最近的；她大招期间（`fast`）没有就抽英雄。
/// 小兵、野怪和别的英雄平时都不抽（英雄联盟的触手平时不动）。
pub fn choose(foes: &[Foe], from: (f64, f64), reach: f64, fast: bool) -> Option<Foe> {
    let near: Vec<&Foe> = foes.iter().filter(|f| dist(f.pos, from) <= reach).collect();
    let by = |a: &&&Foe, b: &&&Foe| dist(a.pos, from).total_cmp(&dist(b.pos, from));
    near.iter()
        .filter(|f| f.marked)
        .min_by(by)
        .or_else(|| if fast { near.iter().filter(|f| f.champion).min_by(by) } else { None })
        .map(|f| **f)
}

pub fn strike_damage(dmg: usize, ratio: usize, attack: usize) -> usize {
    dmg + ratio * attack / 100
}

// ===================== 被动 =====================

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

fn at(p: (f64, f64)) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 一个计时 buff（先去掉再加：同名 buff 会叠）。
fn refresh(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, &buff.name());
    sim.add_buff(id, buff);
}

#[derive(Clone, Debug)]
struct Tentacle {
    pos: (f64, f64),
    /// 沉下去的那一 tick（画面再播 SINK_T 就没了）。
    until: usize,
    /// 下一段摆动画面、自己下一次抽（灵魂、躯壳、大招）的 tick。
    sway: usize,
    next: usize,
}

#[derive(Clone, Debug)]
struct Spirit {
    target: usize,
    spot: (f64, f64),
    /// 被扯出灵魂的英雄的 id（选画面：他自己的、朝哪边），本体朝左没有，上一 tick 本体的 x。
    champion: String,
    left: bool,
    last_x: f64,
    until: usize,
    /// 灵魂画面下一次重播的 tick。
    pic: usize,
}

/// 等着抽某个人的一下（严酷训诫、Q）。
#[derive(Clone, Debug)]
struct Lash {
    due: usize,
    target: usize,
    why: &'static str,
}

/// 每个俄洛伊一份。
#[derive(Clone, Default)]
struct Prophet {
    p: Params,
    walls: Option<Walls>,
    tentacles: Vec<Tentacle>,
    spirits: Vec<Spirit>,
    marked: Vec<(usize, usize)>,
    lashes: Vec<Lash>,
    /// 下一条按冷却长的 tick（0：还没定）、下一下 Q 能抽的 tick、身边长时轮到哪一侧。
    next_grow: usize,
    q_next: usize,
    side: bool,
    n_grown: usize,
    n_wall: usize,
    n_strike: usize,
    n_marked: usize,
    n_echo: usize,
    n_vessel: usize,
    n_q: usize,
    n_refused: usize,
    next_report: usize,
}

struct Unit {
    id: usize,
    pos: (f64, f64),
    champion: bool,
    enemy: bool,
}

fn units(sim: &StableSim<'_>, team: usize) -> Vec<Unit> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if !e.is_alive() {
            continue;
        }
        let ok = matches!(
            e.kind(),
            Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Epic | EntityKindV1::Serpen)
        );
        if ok {
            out.push(Unit { id: e.id(), pos: fpos(e.pos()), champion: e.kind() == Some(EntityKindV1::Champion), enemy: e.team() != team });
        }
    }
    out
}

/// 一节灵魂线：投射物画面在 `c`、朝 `dir`，1 tick 就飞到头（league_akshan 的绳子）。
fn link(sim: &mut StableSim<'_>, me: usize, c: (f64, f64), dir: (f64, f64)) -> bool {
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team: sim.get_entity(me).map_or(0, |e| e.team()),
        x: c.0.round().max(0.0) as u64,
        y: c.1.round().max(0.0) as u64,
        radius: 1_000,
        speed: 1_000,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: (c.0 + dir.0 * 1_000.0).round().max(0.0) as u64,
        target_y: (c.1 + dir.1 * 1_000.0).round().max(0.0) as u64,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    sim.spawn_projectile(&il("e_tether"), &format!("{ID}:noop"), &spec)
}

/// 灵魂挨打（用户：「打灵魂时也没特效啊 别人看了不知道在干嘛」）：灵魂身上一闪（`e_echo`），一道鬼手（`e_grab`）顺着线飞回本体。
fn echo_fx(sim: &mut StableSim<'_>, me: usize, spot: (f64, f64), body: (f64, f64)) {
    sim.play_view_effect(&il("e_echo"), me, &at(spot), 0, 0, 0);
    if dist(spot, body) < 2_000.0 {
        return;
    }
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team: sim.get_entity(me).map_or(0, |e| e.team()),
        x: spot.0.round().max(0.0) as u64,
        y: spot.1.round().max(0.0) as u64,
        radius: 1_000,
        speed: PULSE_SPEED,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: body.0.round().max(0.0) as u64,
        target_y: body.1.round().max(0.0) as u64,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    sim.spawn_projectile(&il("e_grab"), &format!("{ID}:noop"), &spec);
}

impl Prophet {
    /// 灵魂被扯出来的英雄 `target` 挨了一下：灵魂闪一下、一道鬼手飞回本体。
    fn echoed(&self, sim: &mut StableSim<'_>, me: usize, target: usize) {
        let Some(s) = self.spirits.iter().find(|s| s.target == target) else { return };
        let Some(body) = sim.get_entity(target).map(|e| fpos(e.pos())) else { return };
        echo_fx(sim, me, s.spot, body);
    }

    fn walls(&mut self, us: &[Unit]) -> &Walls {
        if self.walls.is_none() {
            let points: Vec<(f64, f64)> = us.iter().map(|u| u.pos).collect();
            self.walls = Some(pick(&points));
        }
        self.walls.as_ref().unwrap()
    }

    /// 在 `near` 附近长一条触手：先找墙边，没有就在 `fallback`；多了就让最老的那条沉下去。
    fn grow(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit], near: (f64, f64), fallback: (f64, f64), why: &str) {
        let reach = self.p.p_reach as f64;
        let edge = self.walls(us).edge_near(near, reach);
        let pos = edge.unwrap_or(fallback);
        let tick = sim.tick();
        while self.tentacles.len() >= self.p.t_most {
            let old = self.tentacles.remove(0);
            sim.play_view_effect(&il("tentacle_sink"), me, &at(old.pos), 0, 0, 0);
        }
        self.tentacles.push(Tentacle { pos, until: life_end(tick, self.p.t_long), sway: tick + RISE_T, next: tick + self.p.t_first });
        sim.play_view_effect(&il("tentacle_rise"), me, &at(pos), 0, 0, 0);
        sim.play_view_effect(&il("p_spawn"), me, &at(pos), 0, 0, 0);
        sim.play_sfx(&il("p_spawn"), me, &at(pos));
        self.n_grown += 1;
        if edge.is_some() {
            self.n_wall += 1;
        }
        if self.n_grown <= 20 || self.n_grown % 50 == 0 {
            wlog(format!("{} GROW #{} ({why}): at ({:.0}, {:.0}){}, {} standing", head(sim, me), self.n_grown, pos.0, pos.1,
                         if edge.is_some() { " on a wall's edge" } else { " beside her" }, self.tentacles.len()));
        }
    }

    /// 被动的冷却到了：长一条（她活着才长；第一条在开局后半个冷却）。
    fn timer(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit], pos: (f64, f64), level: usize) {
        let tick = sim.tick();
        let cd = grow_cd(level, &self.p);
        if self.next_grow == 0 {
            self.next_grow = tick + cd / 2;
            return;
        }
        if tick < self.next_grow {
            return;
        }
        self.next_grow = tick + cd;
        let foe = us.iter().filter(|u| u.enemy).min_by(|a, b| dist(a.pos, pos).total_cmp(&dist(b.pos, pos))).map(|u| u.pos);
        self.side = !self.side;
        let fallback = beside(pos, foe, self.p.t_place as f64, if self.side { 1.0 } else { -1.0 });
        self.grow(sim, me, us, pos, fallback, "its time");
    }

    /// 触手的画面：摆动一段接一段，到时候沉下去。
    fn pictures(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        let mut gone = Vec::new();
        for t in self.tentacles.iter_mut() {
            if tick >= t.until {
                gone.push(t.pos);
            } else if tick >= t.sway {
                t.sway += SWAY_T;
                sim.play_view_effect(&il("tentacle_sway"), me, &at(t.pos), 0, 0, 0);
            }
        }
        self.tentacles.retain(|t| tick < t.until);
        for p in gone {
            sim.play_view_effect(&il("tentacle_sink"), me, &at(p), 0, 0, 0);
        }
    }

    /// 一下：伤害、画面、抽中英雄回血。
    fn strike(&mut self, sim: &mut StableSim<'_>, me: usize, attack: usize, target: usize, champion: bool, why: &str) {
        let Some(t) = sim.get_entity(target) else { return };
        if !t.is_alive() {
            return;
        }
        let tp = fpos(t.pos());
        self.echoed(sim, me, target);
        let dmg = strike_damage(self.p.t_dmg, self.p.t_ratio, attack);
        sim.deal_damage_typed(me, target, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
        sim.play_view_effect(&il("lash"), me, &at(tp), 0, 0, 0);
        sim.play_view_effect(&il("p_slam"), me, &at(tp), 0, 0, 0);
        let hit = InputTargetV1::target(target);
        sim.play_view_effect(&il("p_hit"), me, &hit, 0, 0, 0);
        sim.play_sfx(&il("p_hit"), me, &hit);
        if champion && sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            sim.heal(me, me, strike_damage(self.p.p_heal, self.p.p_heal_r, attack));
            refresh(sim, me, &BuffV1::timed(&il("p_heal"), 36));
        }
        self.n_strike += 1;
        if self.n_strike <= 20 || self.n_strike % 100 == 0 {
            wlog(format!("{} STRIKE #{} ({why}): #{target}{} for {dmg}", head(sim, me), self.n_strike,
                         if champion { " (champion)" } else { "" }));
        }
    }

    /// 大招落地：每个 r_r 内的敌方英雄身边长一条。
    fn signals(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit], pos: (f64, f64)) {
        if has_buff(sim, me, &il("r_new")) {
            sim.entity_remove_buff(me, &il("r_new"));
            let r = self.p.r_r as f64;
            let near: Vec<(f64, f64)> = us.iter().filter(|u| u.enemy && u.champion && dist(u.pos, pos) <= r).map(|u| u.pos).collect();
            for cp in near {
                self.grow(sim, me, us, cp, cp, "leap of faith");
            }
        }
    }

    /// 新挂上灵魂的英雄：灵魂朝她扯出来站着；每 tick 画灵魂和线；灵魂到时或拉断：躯壳。
    fn spirits(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit], her: (f64, f64)) {
        let tick = sim.tick();
        let spirit = il("e_spirit");
        for u in us.iter().filter(|u| u.enemy && u.champion) {
            if !self.spirits.iter().any(|s| s.target == u.id) && has_buff(sim, u.id, &spirit) {
                let spot = spirit_spot(u.pos, her, self.p.e_pull as f64);
                let champion = sim.get_entity(u.id).and_then(|e| e.name()).unwrap_or_default();
                // he faces her when she tears it out (he fights her); then the way he walks
                let left = her.0 < u.pos.0;
                self.spirits.push(Spirit { target: u.id, spot, champion, left, last_x: u.pos.0, until: tick + self.p.e_t,
                                           pic: tick });
                wlog(format!("{} SPIRIT: #{} torn out to ({:.0}, {:.0}), {:.0} from its body", head(sim, me), u.id, spot.0,
                             spot.1, dist(spot, u.pos)));
            }
        }
        let mut broken = Vec::new();
        self.spirits.retain(|s| {
            let Some(u) = us.iter().find(|u| u.id == s.target) else { return false };
            let far = dist(u.pos, s.spot) > self.p.e_leash as f64;
            if far || tick >= s.until {
                broken.push((s.target, u.pos, far));
                return false;
            }
            true
        });
        let mut drawn = Vec::new();
        for s in self.spirits.iter_mut() {
            let x = us.iter().find(|u| u.id == s.target).map_or(s.last_x, |u| u.pos.0);
            let left = faces_left(s.left, x - s.last_x);
            s.last_x = x;
            // the ghost faces the way its body does: drawn again at once when he turns (「相反问题解决了啊」)
            if tick >= s.pic || left != s.left {
                s.left = left;
                s.pic = tick + SOUL_T;
                sim.play_view_effect(&soul_look(&s.champion, s.left), me, &at(s.spot), 0, 0, 0);
            }
            if let Some(u) = us.iter().find(|u| u.id == s.target) {
                drawn.push((s.spot, Some(u.pos)));
            }
        }
        for (spot, body) in drawn {
            match body {
                None => {}
                Some(b) => {
                    for (c, dir) in tether_links(spot, b, LINK_STEP) {
                        if !link(sim, me, c, dir) {
                            self.n_refused += 1;
                            if self.n_refused <= 3 {
                                wlog(format!("{} TETHER: a link refused by spawn_projectile", head(sim, me)));
                            }
                        }
                    }
                }
            }
        }
        for (target, tp, far) in broken {
            sim.entity_remove_buff(target, &spirit);
            refresh(sim, target, &BuffV1::timed(&il("e_vessel"), self.p.e_vt));
            sim.play_view_effect(&il("e_break"), me, &InputTargetV1::target(target), 0, 0, 0);
            sim.play_sfx(&il("e_break"), me, &InputTargetV1::target(target));
            self.n_vessel += 1;
            wlog(format!("{} VESSEL: #{target} ({})", head(sim, me), if far { "walked off its spirit" } else { "spirit ran out" }));
            self.grow(sim, me, us, tp, tp, "vessel");
        }
    }

    /// 严酷训诫新打中的人：够得着的触手依次抽他。
    fn lessons(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit]) {
        let tick = sim.tick();
        let mark = il("w_mark");
        self.marked.retain(|(_, until)| *until > tick);
        for u in us.iter().filter(|u| u.enemy) {
            if self.marked.iter().any(|(id, _)| *id == u.id) || !has_buff(sim, u.id, &mark) {
                continue;
            }
            self.marked.push((u.id, tick + self.p.w_mark_t));
            self.n_marked += 1;
            let reach = self.p.t_r as f64 * 1.5;
            let n = self.tentacles.iter().filter(|t| dist(t.pos, u.pos) <= reach).count();
            for k in 0..n {
                self.lashes.push(Lash { due: tick + 1 + k * self.p.w_gap, target: u.id, why: "lesson" });
            }
            if self.n_marked <= 20 {
                wlog(format!("{} LESSON: #{} - {n} tentacles lash it", head(sim, me), u.id));
            }
        }
    }

    fn fire(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit], attack: usize, fast: bool) {
        let tick = sim.tick();
        let vessel = il("e_vessel");
        let spirited: Vec<usize> = self.spirits.iter().map(|s| s.target).collect();
        let foes: Vec<Foe> = us
            .iter()
            .filter(|u| u.enemy)
            .map(|u| Foe { id: u.id, pos: u.pos, champion: u.champion,
                           marked: spirited.contains(&u.id) || has_buff(sim, u.id, &vessel) })
            .collect();
        let per = if fast { self.p.r_per } else { self.p.t_per };
        let reach = self.p.t_r as f64;
        let mut hits = Vec::new();
        for t in self.tentacles.iter_mut() {
            if t.next > tick {
                continue;
            }
            if let Some(f) = choose(&foes, t.pos, reach, fast) {
                t.next = tick + per;
                hits.push((f.id, f.champion, if f.marked { "spirit or vessel" } else { "leap of faith" }));
            }
        }
        let (due, wait): (Vec<Lash>, Vec<Lash>) = std::mem::take(&mut self.lashes).into_iter().partition(|l| l.due <= tick);
        self.lashes = wait;
        for l in due {
            let champ = us.iter().any(|u| u.id == l.target && u.champion);
            hits.push((l.target, champ, l.why));
        }
        for (id, champ, why) in hits {
            self.strike(sim, me, attack, id, champ, why);
        }
    }
}

impl StablePassive for Prophet {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Illaoi (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    /// 她打中敌人：Q（并进被动）好了就让够得着的触手抽他一下（下一 tick，不在这一下里面再打）；灵魂分担伤害（带着灵魂的
    /// 英雄每一下多算 e_echo%）。
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        if *damage == 0 {
            return;
        }
        let tick = sim.tick();
        let enemy = sim.get_entity(me).map(|e| e.team()) != sim.get_entity(target).map(|e| e.team());
        if enemy && tick >= self.q_next {
            if let Some(tp) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| fpos(e.pos())) {
                let reach = self.p.t_r as f64 * 1.5;
                if self.tentacles.iter().any(|t| dist(t.pos, tp) <= reach) {
                    self.q_next = tick + self.p.q_cd;
                    self.lashes.push(Lash { due: tick + 1, target, why: "tentacle smash" });
                    self.n_q += 1;
                }
            }
        }
        if !has_buff(sim, target, &il("e_spirit")) {
            return;
        }
        let extra = *damage * self.p.e_echo / 100;
        *damage += extra;
        self.echoed(sim, me, target);
        self.n_echo += 1;
        if self.n_echo <= 10 || self.n_echo % 100 == 0 {
            wlog(format!("{} ECHO #{}: #{target} +{extra}", head(sim, me), self.n_echo));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, attack, pos, alive, level) = (e.team(), e.stat().attack, fpos(e.pos()), e.is_alive(), e.level());
        let tick = sim.tick();
        let us = units(sim, team);
        if alive {
            self.timer(sim, me, &us, pos, level as usize);
        }
        self.signals(sim, me, &us, pos);
        self.spirits(sim, me, &us, pos);
        self.lessons(sim, me, &us);
        self.pictures(sim, me);
        let fast = has_buff(sim, me, &il("r_on"));
        // her tentacles stand and strike after her death (League's)
        self.fire(sim, me, &us, attack, fast);
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 {
                wlog(format!("{} WATCH: tentacles grown {} ({} on walls, {} standing), strikes {} (Q {}), lessons {}, echoes {}, vessels {}",
                             head(sim, me), self.n_grown, self.n_wall, self.tentacles.len(), self.n_strike, self.n_q,
                             self.n_marked, self.n_echo, self.n_vessel));
            }
        }
    }
}

struct Noop;
impl StableEffectType for Noop {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Illaoi: tentacles on the walls, the spirit's echo and leash, tentacles after the marked) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:prophet"), Prophet::default());
    module.add_native_effect(format!("{ID}:noop"), Noop);
    host.log(LogLevel::Info, "league_illaoi loaded (tentacles on the walls, Test of Spirit's echo and leash).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let p = parse_params(r#"{"e_echo":15,"e_leash":150000,"e_pull":40000,"e_t":300,"e_vt":240,"p_cd_1":1200,"p_cd_18":600,"p_heal":6,"p_heal_r":6,"p_reach":60000,"q_cd":480,"r_per":60,"r_r":45000,"t_dmg":10,"t_first":40,"t_life":360,"t_long":3600,"t_most":4,"t_per":90,"t_place":15000,"t_r":30000,"t_ratio":35,"w_gap":6,"w_mark_t":240}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let src = include_str!("../../../tools/kit/build_illaoi.py");
        let p = Params::default();
        for (k, v) in [("p_cd_1", p.p_cd_1), ("p_cd_18", p.p_cd_18), ("t_long", p.t_long), ("t_most", p.t_most),
                       ("q_cd", p.q_cd), ("e_pull", p.e_pull as usize)] {
            assert!(src.contains(&format!("\"{k}\": {v}")), "{k} differs from the kit");
        }
    }

    #[test]
    fn the_wall_edge_nearest_her() {
        let w = Walls::from_rows(&["....", "..#.", "....", "...."]);
        // she stands in cell (0, 1): the nearest edge is cell (1, 1) left of the wall, pushed toward it
        let her = (0.5 * CELL, 1.5 * CELL);
        let e = w.edge_near(her, 2.0 * CELL).unwrap();
        assert!((e.0 - 1.85 * CELL).abs() < 1.0 && (e.1 - 1.5 * CELL).abs() < 1.0, "{e:?}");
        // no wall within reach: none
        let open = Walls::from_rows(&["......", "......", "......"]);
        assert_eq!(open.edge_near(her, 3.0 * CELL), None);
        // a wall too far
        assert_eq!(w.edge_near((0.5 * CELL, 3.5 * CELL), 0.5 * CELL), None);
    }

    #[test]
    fn the_map_is_the_one_nobody_stands_in_walls() {
        // units in the 5v5 map's corners stand in the single lane map's rock (its rows 0-5 start with walls)
        let w = pick(&[(16000.0, 16000.0), (944000.0, 944000.0), (480000.0, 160000.0)]);
        assert_eq!(w, builtin(GameModeKindV1::Moba));
        assert_eq!(builtin(GameModeKindV1::Moba).count(), 90);
    }

    #[test]
    fn tentacles_strike_spirits_and_vessels_only_but_champions_too_in_her_ult() {
        // 「照联盟：W、灵魂、躯壳才抽」: a minion and a plain champion in reach are left alone
        let me = (0.0, 0.0);
        let foes = [
            Foe { id: 1, pos: (5000.0, 0.0), champion: false, marked: false },
            Foe { id: 2, pos: (20000.0, 0.0), champion: true, marked: false },
            Foe { id: 3, pos: (29000.0, 0.0), champion: true, marked: true },
            Foe { id: 4, pos: (90000.0, 0.0), champion: true, marked: true },
        ];
        assert_eq!(choose(&foes, me, 30000.0, false).map(|f| f.id), Some(3));
        assert_eq!(choose(&foes[..2], me, 30000.0, false), None);
        // Leap of Faith: the champion in reach
        assert_eq!(choose(&foes[..2], me, 30000.0, true).map(|f| f.id), Some(2));
        assert_eq!(choose(&foes[3..], me, 30000.0, true), None);
    }

    #[test]
    fn grows_on_its_timer_faster_with_her_level() {
        let p = Params::default();
        assert_eq!(grow_cd(1, &p), 1200);
        assert_eq!(grow_cd(18, &p), 600);
        assert_eq!(grow_cd(30, &p), 600);
        let mid = grow_cd(9, &p);
        assert!(mid < 1200 && mid > 600, "{mid}");
    }

    #[test]
    fn beside_her_left_and_right_of_the_enemy() {
        let a = beside((0.0, 0.0), Some((30000.0, 0.0)), 15000.0, 1.0);
        let b = beside((0.0, 0.0), Some((30000.0, 0.0)), 15000.0, -1.0);
        assert!((a.0).abs() < 1e-6 && (a.1 - 15000.0).abs() < 1e-6, "{a:?}");
        assert!((b.0).abs() < 1e-6 && (b.1 + 15000.0).abs() < 1e-6, "{b:?}");
        assert_eq!(strike_damage(10, 35, 100), 45);
    }

    #[test]
    fn a_tentacle_lives_a_minute_in_whole_sways() {
        let end = life_end(100, 3600);
        assert!(end >= 100 + 3600 && end < 100 + 3600 + SWAY_T, "{end}");
        assert_eq!((end - 100 - RISE_T) % SWAY_T, 0);
    }

    #[test]
    fn every_league_champion_has_its_own_spirit() {
        // 「灵魂能雕刻出每个英雄的形状吗」「只要做英雄联盟的」
        assert_eq!(soul_look("league_kaisa", false), "league_illaoi_soul_league_kaisa");
        assert_eq!(soul_look("league_kaisa", true), "league_illaoi_soul_league_kaisa_l");
        assert_eq!(soul_look("fighter", true), "league_illaoi_e_soul");
        let copy = include_str!("../override/league_illaoi.data_champion");
        for id in souls::SOULS {
            for side in ["", "_l"] {
                assert!(copy.contains(&format!("\"league_illaoi_soul_{id}{side}\"")), "{id}{side}: no view in the copy");
            }
        }
        assert!(souls::SOULS.windows(2).all(|w| w[0] < w[1]), "souls.rs must stay sorted");
        assert!(souls::SOULS.len() >= 150);
    }

    #[test]
    fn the_ghost_faces_the_way_its_body_walks() {
        // 「相反问题解决了啊」: no facing in the engine's interface - the way he walks, else as before
        assert!(faces_left(false, -1000.0));
        assert!(!faces_left(true, 1000.0));
        assert!(faces_left(true, 100.0) && !faces_left(false, -100.0));
    }

    #[test]
    fn the_spirit_stands_toward_her_tethered_to_its_body() {
        // 「拉灵魂没有特效 完全看不出」: pulled 25000 out toward her, not drawn over the body
        let s = spirit_spot((100000.0, 0.0), (0.0, 0.0), 25000.0);
        assert!((s.0 - 75000.0).abs() < 1e-6 && s.1.abs() < 1e-6, "{s:?}");
        // she stands closer than that: half way
        let s = spirit_spot((10000.0, 0.0), (0.0, 0.0), 25000.0);
        assert!((s.0 - 5000.0).abs() < 1e-6, "{s:?}");
        // the line: one link every LINK_STEP, pointing from the spirit to the body
        let l = tether_links((0.0, 0.0), (30000.0, 0.0), LINK_STEP);
        assert_eq!(l.len(), 3);
        assert!((l[0].0 .0 - 5000.0).abs() < 1e-6 && (l[2].0 .0 - 25000.0).abs() < 1e-6);
        assert_eq!(l[1].1, (1.0, 0.0));
        assert!(tether_links((0.0, 0.0), (1000.0, 0.0), LINK_STEP).is_empty());
    }
}
