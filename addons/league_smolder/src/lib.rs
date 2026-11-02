//! 斯莫德附加包（用户选的三件：层数死后保留、三档斩杀、智能 E 飞过墙）。
//!
//! 主包是纯数据：被动「龙之研习」每一层是他身上一个永久的 `league_smolder_p_st`（法术强度 +1），层数的计数器、三档的旗子也都是
//! 永久 buff；引擎在他死亡时清掉身上全部 buff，所以主包里层数每条命从零叠起（说明里写着「阵亡清空」）。数据读不到生命，三档的
//! 「低于 6.5% 生命处决」做不了；扑棱只在技能 2 出手时、被近身或追残血才飞，往哪飞不看墙。`mod.override_info` 把主包的斯莫德换成
//! `override/` 里的副本（`tools/kit/build_smolder.py` 的 `native=1`）：技能 2 只剩喷嚏，E 归本包的被动 `league_smolder:dragon`，
//! 三档龙息命中时多调一次本包的效果 `league_smolder:execute`。
//!
//! - **层数死后保留**（`Dragon::keep`，维迦附加包的做法）：活着时把身上每个层数 buff（`p_st`、`p_has`、计数器 `u*` / `L*`、三档
//!   `t1`..`t3`、待记的 `pa*`）原样记下来；身上的 `p_st` 比记下的少了（死亡或复活时引擎清掉；主包从不去掉一层）就把缺的原样补回。
//! - **斩杀**：三档龙息（主目标、一档起的爆炸）打中的单位，下一 tick（伤害结算完）生命不高于最大生命的 `E_EXEC`‰ 就处决（真实伤害，
//!   击杀算他的，主包的击杀检查照样给层）。
//! - **扑棱，扑棱，扑棱！**（被动每 `EVERY` tick 看一次，E 冷却 `e_cd_t` 好了、他活着、没被控时）：
//!   - **撤**（`wants_out`）：生命低于 `LOW_HP`% 而 `e_near` 内有敌方英雄；或 `e_close` 内有敌方英雄；或 `e_near` 内敌方英雄 2 名以上、
//!     比身边的友方英雄多——背向身边敌人的中心（左右 `SPREAD_DEG`°）飞：前面 `WALL_REACH` 内有墙就飞过去落到墙另一边（最远
//!     `e_far`），没有就平飞 `e_plain`；落地后离最近的敌方英雄远 `ESCAPE_GAIN` 以上，挑离敌人最远、朝己方最近的塔走得多的，飞过墙的
//!     多算 `WALL_BONUS`（`plan_exit`）。
//!   - **追**（`plan_chase`）：身边 `e_reach` 内没有敌方英雄（打不到人），`e_chase` 内有生命不高于 `PREY_HP`% 的敌方英雄（最残的先），
//!     他自己生命不低于 `CHASE_HP`%——朝目标左右 `CHASE_DEG`° 内飞到离他 `KEEP_AT`..`IN_RANGE` 处（普攻打得到），飞得越短越好；
//!     路上隔着墙时最远 `e_far`，不隔墙 `e_plain`；落点旁除了目标最多一名敌方英雄。
//!   - 起飞：冷却、`skill2_e` 动作 `e_anim` tick、音效和台词、加速 `e_ms`% `e_ms_t` tick（主包的 `league_smolder_e_haste`，画面也是
//!     主包的）；`e_wind` tick 后穿墙强制位移过去（`e_fly` 一 tick，至少 `e_tick` tick），宿主没挪人时逐 tick 自己走一步（泰隆的做法）。
//!     起飞后第 `e_shot0` tick 起每 `e_gap` tick 一枚火球、共 `e_n` 枚（主包的 `league_smolder_e_shot` 画面）：`e_r` 内生命比例最低的
//!     敌方英雄，没有就最近的敌方单位（不打塔）；每枚 `E_DMG` + `E_RATIO`% 攻击力物理伤害，有层数时再加 `E_STACK`% 法术强度魔法伤害，
//!     每次扑棱第一枚打中英雄的给一层（和主包一样）。
//!
//! 墙是卡蜜尔钩墙附加包的那份地图（`league_camille_wall/src/maps.rs`，5v5 地图 90 格，每格 32000）。数字从英雄数据的
//! `passive.params` 来（`make_override.py` 从参数表 P 写进去）；效果用到的几个常数写在这里，`make_override.py` 核对它们和 P 一致。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_smolder.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_smolder";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_smolder") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 主包的名字（buff、画面、音效）：`league_smolder_<x>`。
fn sm(x: &str) -> String {
    format!("{ID}_{x}")
}

/// 地图一格的边长（世界坐标）。
pub const CELL: f64 = 32_000.0;
/// 沿直线查墙的步长。
pub const STEP: f64 = 1_000.0;
/// 找方向的射线条数（一圈）。
pub const RAYS: usize = 48;
/// 落点离地图边至少这么远。
pub const EDGE: f64 = 8_000.0;
/// 穿墙落到墙另一边再往前这么多。
pub const MARGIN: f64 = 4_000.0;
/// 每几 tick 看一次要不要飞。
pub const EVERY: usize = 3;
/// 撤：背向敌人中心左右这么多度。
pub const SPREAD_DEG: f64 = 75.0;
/// 撤：墙要在这么近处开始，才算「飞过墙」。
pub const WALL_REACH: f64 = 30_000.0;
/// 撤：落地后至少离敌人远这么多。
pub const ESCAPE_GAIN: f64 = 10_000.0;
/// 撤：朝己方塔走的距离的分量。
pub const HOME_W: f64 = 0.5;
/// 撤：飞过墙的落点多算这么多（墙挡住追兵）。
pub const WALL_BONUS: f64 = 20_000.0;
/// 生命低于这个百分比时身边有敌人就撤。
pub const LOW_HP: usize = 40;
/// 追：目标生命不高于这个百分比。
pub const PREY_HP: usize = 50;
/// 追：他自己生命不低于这个百分比。
pub const CHASE_HP: usize = 40;
/// 追：朝目标左右这么多度内找落点。
pub const CHASE_DEG: f64 = 30.0;
/// 追：落点离目标不近于这么多。
pub const KEEP_AT: f64 = 30_000.0;
/// 追：落点离目标不远于这么多（他的普攻 55000 打得到）。
pub const IN_RANGE: f64 = 48_000.0;
/// 追：至少飞这么远才值得。
pub const CLOSER: f64 = 12_000.0;
/// 落点旁边算「挤」的半径。
pub const CROWD_R: f64 = 30_000.0;
/// 斩杀线：最大生命的千分之几（主包 P 的 e_exec）。
pub const E_EXEC: usize = 65;
/// 扑棱火球（主包 P 的 e_dmg、e_ratio、e_stack）。
pub const E_DMG: usize = 10;
pub const E_RATIO: usize = 30;
pub const E_STACK: usize = 25;
/// 一次扑棱第一枚打中英雄的才给层：这个旗子挂多久（主包 P 的 e_anim + 20）。
pub const E_GOT_T: usize = 100;
/// 待记层数的梯子有几级（主包 P 的 p_pend）。
pub const P_PEND: usize = 6;
/// 前几次扑棱每次都记日志，之后每 25 次记一次。
const LOG_FIRST: usize = 80;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SMOLDER_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_smolder.log");
        }
    }
    PathBuf::from("league_smolder.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first).
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
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

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包被动用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub e_cd_t: usize,
    pub e_anim: usize,
    pub e_wind: usize,
    pub e_tick: usize,
    pub e_far: usize,
    pub e_plain: usize,
    pub e_fly: usize,
    pub e_near: usize,
    pub e_close: usize,
    pub e_reach: usize,
    pub e_chase: usize,
    pub e_ms: usize,
    pub e_ms_t: usize,
    pub e_n: usize,
    pub e_gap: usize,
    pub e_shot0: usize,
    pub e_r: usize,
    pub e_sspeed: usize,
    pub p_base: usize,
    pub p_pend: usize,
    pub t3: usize,
    pub vo_gap: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            e_cd_t: 1200,
            e_anim: 80,
            e_wind: 8,
            e_tick: 64,
            e_far: 80_000,
            e_plain: 60_000,
            e_fly: 3_000,
            e_near: 40_000,
            e_close: 30_000,
            e_reach: 58_000,
            e_chase: 90_000,
            e_ms: 40,
            e_ms_t: 120,
            e_n: 5,
            e_gap: 12,
            e_shot0: 9,
            e_r: 70_000,
            e_sspeed: 7_000,
            p_base: 5,
            p_pend: 6,
            t3: 40,
            vo_gap: 600,
        }
    }
}

/// `{"e_tick":19,...}` -> 参数；缺的键用默认值，认不得的键忽略（e_dmg 之类是效果的常数，`make_override.py` 核对）。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "e_cd_t" => &mut p.e_cd_t,
            "e_anim" => &mut p.e_anim,
            "e_wind" => &mut p.e_wind,
            "e_tick" => &mut p.e_tick,
            "e_far" => &mut p.e_far,
            "e_plain" => &mut p.e_plain,
            "e_fly" => &mut p.e_fly,
            "e_near" => &mut p.e_near,
            "e_close" => &mut p.e_close,
            "e_reach" => &mut p.e_reach,
            "e_chase" => &mut p.e_chase,
            "e_ms" => &mut p.e_ms,
            "e_ms_t" => &mut p.e_ms_t,
            "e_n" => &mut p.e_n,
            "e_gap" => &mut p.e_gap,
            "e_shot0" => &mut p.e_shot0,
            "e_r" => &mut p.e_r,
            "e_sspeed" => &mut p.e_sspeed,
            "p_base" => &mut p.p_base,
            "p_pend" => &mut p.p_pend,
            "t3" => &mut p.t3,
            "vo_gap" => &mut p.vo_gap,
            _ => continue,
        };
        *slot = v;
    }
    p
}

/// 主包里算层数的那些 buff 的名字（短名）：每层的 `p_st`、有层的 `p_has`、计数器 `u1..u<p_base-1>`、`L1..L<t3/p_base>`、三档、
/// 待记的 `pa1..pa<p_pend>`。
pub fn stack_names(p: &Params) -> Vec<String> {
    let mut v = vec!["p_st".to_string(), "p_has".to_string(), "t1".into(), "t2".into(), "t3".into()];
    v.extend((1..p.p_base.max(1)).map(|k| format!("u{k}")));
    v.extend((1..=p.t3 / p.p_base.max(1)).map(|k| format!("L{k}")));
    v.extend((1..=p.p_pend).map(|k| format!("pa{k}")));
    v
}

// ===================== 层数 =====================

/// `kept` 里有、`have` 里没有的那些（按完整的数值配对，同名的几个各算各的）。
pub fn missing(kept: &[BuffV1], have: &[BuffV1]) -> Vec<BuffV1> {
    let mut left: Vec<Option<&BuffV1>> = have.iter().map(Some).collect();
    let mut out = Vec::new();
    for k in kept {
        match left.iter_mut().find(|h| h.is_some_and(|h| h == k)) {
            Some(slot) => *slot = None,
            None => out.push(*k),
        }
    }
    out
}

/// 待记的梯子（`pa1..` 从下往上全亮）该亮的下一级：亮着 k 级就是 k+1，满了 `None`（主包 gain() 的梯子）。
pub fn next_rung(lit: &[bool]) -> Option<usize> {
    let k = lit.iter().take_while(|l| **l).count();
    (k < lit.len()).then_some(k + 1)
}

fn buff_names(sim: &StableSim<'_>, id: usize) -> Vec<String> {
    sim.get_entity(id).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect()
    })
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 一层（主包 gain() 的样子）：`p_st`（法术强度 +1）、`p_has`、待记的梯子再亮一级。
fn gain(sim: &mut StableSim<'_>, me: usize) {
    let mut st = BuffV1::named(&sm("p_st"));
    st.magic_power = 1;
    sim.add_buff(me, &st);
    let names = buff_names(sim, me);
    if !names.iter().any(|n| *n == sm("p_has")) {
        sim.add_buff(me, &BuffV1::named(&sm("p_has")));
    }
    let lit: Vec<bool> = (1..=P_PEND).map(|k| names.iter().any(|n| *n == sm(&format!("pa{k}")))).collect();
    if let Some(k) = next_rung(&lit) {
        sim.add_buff(me, &BuffV1::named(&sm(&format!("pa{k}"))));
    }
}

// ===================== 墙 =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一张墙格子：`cells[y][x]`（卡蜜尔、泰隆、巴德附加包的那张）。
#[derive(Clone, Debug, PartialEq)]
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
}

impl Grid {
    pub fn from_rows(rows: &[&str]) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect() }
    }

    pub fn builtin() -> [Grid; 3] {
        [Grid::from_rows(&maps::MOBA), Grid::from_rows(&maps::SINGLE_LANE), Grid::from_rows(&maps::DEATH_MATCH)]
    }

    pub fn size(&self) -> (f64, f64) {
        (self.cells.first().map_or(0, |r| r.len()) as f64 * CELL, self.cells.len() as f64 * CELL)
    }

    /// 在地图里、离边至少 `EDGE` 吗。
    pub fn roomy(&self, p: (f64, f64)) -> bool {
        let (w, h) = self.size();
        p.0 >= EDGE && p.1 >= EDGE && p.0 <= w - EDGE && p.1 <= h - EDGE
    }

    /// 世界坐标落在墙格里吗（地图外不算）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return false;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(false)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }

    /// 落得下吗：在地图里不贴边、不在墙格里。
    pub fn clear(&self, p: (f64, f64)) -> bool {
        self.roomy(p) && !self.is_wall(p.0, p.1)
    }

    /// 两点之间的直线碰到墙格吗（终点也算）。
    pub fn blocked(&self, a: (f64, f64), b: (f64, f64)) -> bool {
        let n = (dist(a, b) / STEP).ceil().max(1.0) as usize;
        (1..=n).any(|i| {
            let t = i as f64 / n as f64;
            self.is_wall(a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
        })
    }

    /// 朝 `dir`（单位向量）飞过墙：`reach` 内碰到墙、一路穿过去，落在墙另一边 `MARGIN` 处；落点不超过 `far`、落得下。
    pub fn over(&self, from: (f64, f64), dir: (f64, f64), reach: f64, far: f64) -> Option<(f64, f64)> {
        let at = |t: f64| (from.0 + dir.0 * t, from.1 + dir.1 * t);
        let mut t = STEP;
        while t <= reach && !self.is_wall(at(t).0, at(t).1) {
            t += STEP;
        }
        if t > reach {
            return None;
        }
        while t <= far && self.is_wall(at(t).0, at(t).1) {
            t += STEP;
        }
        let to = at(t + MARGIN);
        (t + MARGIN <= far && self.clear(to)).then_some(to)
    }
}

/// 猜地图用的点：所有活着的单位（英雄、小兵、野怪、塔……）。只看英雄的话，大家都站在三张图都空着的那条斜带上
/// （中路、两边泉水）时打平，平手偏向墙多的单线 / 死斗图，5v5 就猜错了（2026-11-01 复查：波比的 R 有 7 次退回击退）；
/// 5v5 边路的兵和野区的野怪几乎一直在，正好落在另两张图的墙里。
fn unit_points(sim: &StableSim<'_>) -> Vec<(f64, f64)> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_alive())
        .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
        .collect()
}

/// 这局是哪张图：站在墙里的英雄最少、墙又最多的那张（泰隆、卡蜜尔、巴德附加包的判断）。
pub fn current(grids: &[Grid], champions: &[(f64, f64)]) -> Option<usize> {
    grids
        .iter()
        .enumerate()
        .min_by_key(|(_, g)| {
            let inside = champions.iter().filter(|&&(x, y)| g.is_wall(x, y)).count();
            (inside, std::cmp::Reverse(g.walls()))
        })
        .map(|(i, _)| i)
}

fn unit(v: (f64, f64)) -> Option<(f64, f64)> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

fn rays() -> impl Iterator<Item = (f64, f64)> {
    (0..RAYS).map(|i| {
        let a = i as f64 * std::f64::consts::TAU / RAYS as f64;
        (a.cos(), a.sin())
    })
}

// ===================== 什么时候飞、往哪飞 =====================

/// 一个敌方英雄：位置、生命百分比、id。
#[derive(Clone, Copy, Debug)]
pub struct Foe {
    pub at: (f64, f64),
    pub hp_pct: usize,
    pub id: usize,
}

/// 该撤了吗：残血而身边有敌方英雄；敌方英雄贴脸；或身边敌方英雄 2 名以上、比身边的友方英雄（`allies` 个，不算他）多。
pub fn wants_out(p: &Params, me: (f64, f64), hp_pct: usize, foes: &[Foe], allies: usize) -> bool {
    let near = foes.iter().filter(|f| dist(me, f.at) <= p.e_near as f64).count();
    (hp_pct < LOW_HP && near >= 1) || foes.iter().any(|f| dist(me, f.at) <= p.e_close as f64) || (near >= 2 && near > allies)
}

/// 撤：背向身边敌人的中心（左右 `SPREAD_DEG`°）——前面 `WALL_REACH` 内有墙就飞过去（`Grid::over`，最远 `e_far`），没有就平飞
/// `e_plain`；落地后离最近的敌方英雄至少远 `ESCAPE_GAIN`；挑离敌人最远、又朝 `home`（己方最近的塔）走得多的，飞过墙的多算
/// `WALL_BONUS`。返回 (落点, 飞过墙了吗)。
pub fn plan_exit(p: &Params, g: &Grid, me: (f64, f64), foes: &[(f64, f64)], home: Option<(f64, f64)>) -> Option<((f64, f64), bool)> {
    let near: Vec<&(f64, f64)> = foes.iter().filter(|f| dist(me, **f) <= p.e_near as f64 * 1.5).collect();
    let away = if near.is_empty() {
        home.and_then(|h| unit((h.0 - me.0, h.1 - me.1)))?
    } else {
        let c = near.iter().fold((0.0, 0.0), |s, f| (s.0 + f.0, s.1 + f.1));
        let c = (c.0 / near.len() as f64, c.1 / near.len() as f64);
        unit((me.0 - c.0, me.1 - c.1)).or_else(|| home.and_then(|h| unit((h.0 - me.0, h.1 - me.1))))?
    };
    let gap = |q: (f64, f64)| foes.iter().map(|f| dist(q, *f)).fold(1.0e9, f64::min);
    let homeward = |q: (f64, f64)| home.map_or(0.0, |h| dist(me, h) - dist(q, h));
    let now = gap(me);
    let cos = SPREAD_DEG.to_radians().cos();
    rays()
        .filter(|d| d.0 * away.0 + d.1 * away.1 >= cos)
        .flat_map(|d| {
            let wall = g.over(me, d, WALL_REACH, p.e_far as f64).map(|to| (to, true));
            let plain = (me.0 + d.0 * p.e_plain as f64, me.1 + d.1 * p.e_plain as f64);
            let plain = g.clear(plain).then(|| (plain, g.blocked(me, plain)));
            [wall, plain].into_iter().flatten()
        })
        .filter(|&(to, _)| foes.is_empty() || gap(to) >= now + ESCAPE_GAIN)
        .map(|(to, wall)| ((to, wall), gap(to) + HOME_W * homeward(to) + if wall { WALL_BONUS } else { 0.0 }))
        .max_by(|a, b| a.1.total_cmp(&b.1))
        .map(|(way, _)| way)
}

/// 追：身边 `e_reach` 内没有敌方英雄，`e_chase` 内生命不高于 `PREY_HP`% 的敌方英雄（最残的先），他自己生命不低于 `CHASE_HP`%——
/// 朝目标左右 `CHASE_DEG`° 内飞到离目标 `KEEP_AT`..`IN_RANGE` 处，飞得越短越好（至少 `CLOSER`）；路上隔着墙最远 `e_far`，不隔墙
/// `e_plain`；落点落得下、旁边除了目标最多一名敌方英雄。返回 (落点, 目标 id, 飞过墙了吗)。
pub fn plan_chase(p: &Params, g: &Grid, me: (f64, f64), hp_pct: usize, foes: &[Foe]) -> Option<((f64, f64), usize, bool)> {
    if hp_pct < CHASE_HP || foes.iter().any(|f| dist(me, f.at) <= p.e_reach as f64) {
        return None;
    }
    let mut prey: Vec<&Foe> = foes.iter().filter(|f| f.hp_pct <= PREY_HP && dist(me, f.at) <= p.e_chase as f64).collect();
    prey.sort_by_key(|f| f.hp_pct);
    let cos = CHASE_DEG.to_radians().cos();
    for t in prey {
        let Some(toward) = unit((t.at.0 - me.0, t.at.1 - me.1)) else { continue };
        let mut best: Option<(f64, (f64, f64), bool)> = None;
        for d in rays().filter(|d| d.0 * toward.0 + d.1 * toward.1 >= cos) {
            let mut s = CLOSER;
            while s <= p.e_far as f64 {
                let to = (me.0 + d.0 * s, me.1 + d.1 * s);
                let wall = g.blocked(me, to);
                let gap = dist(to, t.at);
                if (wall || s <= p.e_plain as f64)
                    && (KEEP_AT..=IN_RANGE).contains(&gap)
                    && g.clear(to)
                    && foes.iter().filter(|f| f.id != t.id && dist(to, f.at) <= CROWD_R).count() <= 1
                {
                    if best.is_none_or(|b| s < b.0) {
                        best = Some((s, to, wall));
                    }
                    break;
                }
                s += 2_000.0;
            }
        }
        if let Some((_, to, wall)) = best {
            return Some((to, t.id, wall));
        }
    }
    None
}

// ===================== 被动 =====================

fn pos(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    sim.get_entity(id).map(|e| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

fn hp_pct(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(100, |e| {
        let (hp, max) = e.hp();
        hp * 100 / max.max(1)
    })
}

/// Crowd control that holds a unit in place - from game 0.7.0 also when laid by native code ("movement continuing while
/// rooted" fixed): root, stun (a Sleep reaches add-ons as a Stun), knock-up, taunt, fear, charm; not a dash's own
/// ForceMove nor a cast's Animation. A step of our own while one of these is on would move him through it.
const HELD: [CcKindV1; 6] =
    [CcKindV1::Bind, CcKindV1::Stun, CcKindV1::Airborne, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];

fn has_cc(sim: &StableSim<'_>, id: usize, kinds: &[CcKindV1]) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
    })
}

/// 不能飞的状态：硬控、沉默、禁位移技能、正被强制位移（泰隆、巴德附加包的那张表）。
const NO_FLAP: [CcKindV1; 9] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::BlockSkill,
    CcKindV1::BlockMoveSkill,
    CcKindV1::ForceMove,
];

/// 一次扑棱：第几 tick 起飞、落点、还没发的火球（第几 tick）、上一 tick 在哪（看宿主有没有挪他）、飞到第几 tick 为止、每 tick 飞多远。
#[derive(Clone, Debug)]
struct Flight {
    go_at: usize,
    to: (f64, f64),
    shots: Vec<usize>,
    moving: bool,
    last: (f64, f64),
    until: usize,
    step: f64,
    why: String,
}

/// 每个斯莫德一份：参数、记下的层数、这一次扑棱、扑棱次数。
#[derive(Clone, Default)]
struct Dragon {
    p: Params,
    names: Vec<String>,
    kept: Vec<BuffV1>,
    kept_st: usize,
    was_alive: bool,
    flight: Option<Flight>,
    flaps: usize,
    shots: usize,
}

impl Dragon {
    /// 层数：活着时记下来，`p_st` 少了就原样补回。
    fn keep(&mut self, sim: &mut StableSim<'_>, me: usize, alive: bool) {
        if self.names.is_empty() {
            self.names = stack_names(&self.p).iter().map(|n| sm(n)).collect();
        }
        let have: Vec<BuffV1> = sim.get_entity(me).map_or_else(Vec::new, |e| {
            (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| self.names.iter().any(|n| n == b.name())).collect()
        });
        let st_name = sm("p_st");
        let st = have.iter().filter(|b| b.name() == st_name).count();
        if st < self.kept_st {
            let gone = missing(&self.kept, &have);
            for b in &gone {
                sim.add_buff(me, b);
            }
            wlog(format!(
                "{} KEEP {} buffs put back ({}): {} stacks",
                head(sim, me),
                gone.len(),
                if alive { "alive" } else { "dead" },
                self.kept_st
            ));
        } else if alive {
            self.kept = have;
            self.kept_st = st;
        }
    }

    /// 看局面：撤或追，挑好落点就起飞（冷却、动作、音效、台词、加速），`e_wind` tick 后出发，火球排好。
    fn decide(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64)) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let mut foes = Vec::new();
        let mut allies = 0;
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_champion() || !u.is_alive() {
                continue;
            }
            let (x, y) = u.pos();
            let at = (x as f64, y as f64);
            if u.team() != team {
                if u.is_targetable() {
                    let (hp, max) = u.hp();
                    foes.push(Foe { at, hp_pct: hp * 100 / max.max(1), id: u.id() });
                }
            } else if u.id() != me && dist(here, at) <= self.p.e_near as f64 {
                allies += 1;
            }
        }
        if foes.is_empty() {
            return;
        }
        let mine = hp_pct(sim, me);
        let home = (0..sim.tower_count())
            .filter_map(|k| sim.get_entity(sim.tower_id_at(k)))
            .filter(|t| t.team() == team && t.is_alive())
            .map(|t| {
                let (x, y) = t.pos();
                (x as f64, y as f64)
            })
            .min_by(|a, b| dist(here, *a).total_cmp(&dist(here, *b)));
        let grids = Grid::builtin();
        let Some(gi) = current(&grids, &unit_points(sim)) else { return };
        let g = &grids[gi];
        let plan = if wants_out(&self.p, here, mine, &foes, allies) {
            plan_exit(&self.p, g, here, &foes.iter().map(|f| f.at).collect::<Vec<_>>(), home).map(|(to, wall)| (to, wall, "out".to_string()))
        } else {
            plan_chase(&self.p, g, here, mine, &foes).map(|(to, id, wall)| (to, wall, format!("after #{id}")))
        };
        let Some((to, wall, why)) = plan else { return };
        let tick = sim.tick();
        let p = self.p.clone();
        sim.entity_remove_buff(me, &sm("e_cd"));
        sim.add_buff(me, &BuffV1::timed(&sm("e_cd"), p.e_cd_t));
        sim.entity_remove_buff(me, &sm("e_got"));
        let mut cc = CcV1::of_kind(CcKindV1::Animation, p.e_anim as u64);
        cc.set_name("skill2_e");
        sim.apply_cc(me, &cc);
        let on_me = InputTargetV1::target(me);
        sim.play_sfx(&sm("e_cast"), me, &on_me);
        if !has_buff(sim, me, &sm("vo_cd")) {
            sim.add_buff(me, &BuffV1::timed(&sm("vo_cd"), p.vo_gap));
            sim.play_sfx(&sm("vo_e"), me, &on_me);
        }
        sim.entity_remove_buff(me, &sm("e_haste"));
        let mut haste = BuffV1::timed(&sm("e_haste"), p.e_ms_t);
        haste.move_speed_mult = p.e_ms as i32;
        sim.add_buff(me, &haste);
        self.flaps += 1;
        let why = format!("{why}{}", if wall { " over a wall" } else { "" });
        if self.flaps <= LOG_FIRST || self.flaps % 25 == 0 {
            wlog(format!(
                "{} FLAP #{} {}: {} -> {} ({:.0}), hp {}%, foes near {}",
                head(sim, me),
                self.flaps,
                why,
                pt(here),
                pt(to),
                dist(here, to),
                mine,
                foes.iter().filter(|f| dist(here, f.at) <= p.e_near as f64).count()
            ));
        }
        self.flight = Some(Flight {
            go_at: tick + p.e_wind,
            to,
            shots: (0..p.e_n).map(|k| tick + p.e_shot0 + k * p.e_gap).collect(),
            moving: false,
            last: here,
            until: 0,
            step: 0.0,
            why,
        });
    }

    /// 出发：再看一次落点，穿墙强制位移过去（`e_fly` 一 tick，至少 `e_tick` tick）。
    fn go(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64)) {
        let Some(f) = self.flight.as_mut() else { return };
        f.moving = true;
        if !landing_ok(sim, f.to) {
            wlog(format!("{} FLAP #{}: the landing {} is no longer clear, he stays", head(sim, me), self.flaps, pt(f.to)));
            f.until = 0;
            return;
        }
        let d = dist(here, f.to);
        let ticks = ((d / self.p.e_fly.max(500) as f64).ceil() as usize).max(self.p.e_tick.max(1));
        let mut ghost = BuffV1::timed(&sm("e_ghost"), ticks + 3);
        ghost.ignore_wall = true;
        sim.add_buff(me, &ghost);
        let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
        mv.dx = (f.to.0 - here.0).round() as i64;
        mv.dy = (f.to.1 - here.1).round() as i64;
        mv.speed = (d / ticks as f64).ceil() as u64;
        sim.apply_cc(me, &mv);
        f.last = here;
        f.until = sim.tick() + ticks + 2;
        f.step = d / ticks as f64;
    }

    /// 飞行中：宿主没挪他就自己走一步；到了、或时间到了就停。
    fn follow(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64)) {
        let tick = sim.tick();
        let Some(f) = self.flight.as_mut() else { return };
        if !f.moving || f.until == 0 {
            return;
        }
        let d = dist(here, f.to);
        if d < f.step.max(500.0) || tick > f.until {
            f.until = 0;
            return;
        }
        // 被放逐（不可选中）时不挪他，截止时间顺延（巴德附加包：放逐中的单位不移动）；被禁锢、眩晕（含睡眠）、击飞、嘲讽、
        // 恐惧、魅惑时也不挪（[`HELD`]：游戏 0.7.0 起原生施加的控制也真的让人停下）
        if sim.get_entity(me).is_some_and(|e| !e.is_targetable()) || has_cc(sim, me, &HELD) {
            f.until += 1;
            f.last = here;
            return;
        }
        if dist(f.last, here) < 1.0 {
            let s = f.step.min(d);
            let next = (here.0 + (f.to.0 - here.0) / d * s, here.1 + (f.to.1 - here.1) / d * s);
            sim.entity_set_pos(me, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64);
            f.last = next;
        } else {
            f.last = here;
        }
    }

    /// 一枚火球：`e_r` 内生命比例最低的敌方英雄，没有就最近的敌方单位（不打塔、水晶）。
    fn shoot(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64)) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let r = self.p.e_r as f64;
        let mut champ: Option<(usize, usize)> = None;
        let mut other: Option<(f64, usize)> = None;
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() || !u.is_targetable() {
                continue;
            }
            if matches!(u.kind(), Some(EntityKindV1::Tower) | Some(EntityKindV1::Nexus)) {
                continue;
            }
            let (x, y) = u.pos();
            let d = dist(here, (x as f64, y as f64));
            if d > r {
                continue;
            }
            if u.is_champion() {
                let (hp, max) = u.hp();
                let pct = hp * 1000 / max.max(1);
                if champ.is_none_or(|c| pct < c.0) {
                    champ = Some((pct, u.id()));
                }
            } else if other.is_none_or(|o| d < o.0) {
                other = Some((d, u.id()));
            }
        }
        let Some(target) = champ.map(|c| c.1).or(other.map(|o| o.1)) else { return };
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team,
            x: here.0.round().max(0.0) as u64,
            y: here.1.round().max(0.0) as u64,
            radius: 1_000,
            speed: self.p.e_sspeed as u64,
            move_kind: ProjectileMoveKindV1::Target.code(),
            target_id: target,
            target_x: 0,
            target_y: 0,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        sim.play_sfx(&sm("e_shot"), me, &InputTargetV1::target(me));
        if sim.spawn_projectile(&sm("e_shot"), &format!("{ID}:shot"), &spec) {
            self.shots += 1;
        } else if self.flaps <= LOG_FIRST {
            wlog(format!("{} FLAP #{}: spawn_projectile refused", head(sim, me), self.flaps));
        }
    }
}

/// 出发那一刻再看一次落点（地图判断可能变了）。
fn landing_ok(sim: &StableSim<'_>, to: (f64, f64)) -> bool {
    let grids = Grid::builtin();
    current(&grids, &unit_points(sim)).is_some_and(|gi| grids[gi].clear(to))
}

impl StablePassive for Dragon {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
        self.names.clear();
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.flight = None;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!(
            "{} SPAWN: the add-on's Smolder (player {player}, team {team}), {} stacks kept, {:?}",
            head(sim, me),
            self.kept_st,
            self.p
        ));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let alive = e.is_alive();
        let targetable = e.is_targetable();
        if alive != self.was_alive {
            wlog(format!("{} {} with {} stacks kept", head(sim, me), if alive { "ALIVE" } else { "DEAD" }, self.kept_st));
            self.was_alive = alive;
        }
        self.keep(sim, me, alive);
        if !alive {
            self.flight = None;
            return;
        }
        let Some(here) = pos(sim, me) else { return };
        let tick = sim.tick();
        if let Some(f) = self.flight.clone() {
            if !f.moving && tick >= f.go_at {
                self.go(sim, me, here);
            } else {
                self.follow(sim, me, here);
            }
            let due = f.shots.iter().filter(|&&s| s <= tick).count();
            if due > 0 {
                for _ in 0..due {
                    self.shoot(sim, me, here);
                }
                if let Some(fl) = self.flight.as_mut() {
                    fl.shots.retain(|&s| s > tick);
                }
            }
            let done = self.flight.as_ref().is_some_and(|fl| fl.moving && fl.until == 0 && fl.shots.is_empty());
            if done {
                if self.flaps <= LOG_FIRST {
                    let f = self.flight.as_ref().map_or(String::new(), |f| f.why.clone());
                    wlog(format!("{} LANDED #{} ({f}) at {}, {} shots so far", head(sim, me), self.flaps, pt(here), self.shots));
                }
                self.flight = None;
            }
            return;
        }
        if tick % EVERY != 0 || !targetable || has_buff(sim, me, &sm("e_cd")) || has_cc(sim, me, &NO_FLAP) {
            return;
        }
        self.decide(sim, me, here);
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.flight = None;
    }
}

// ===================== 效果 =====================

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

/// 扑棱火球打中：物理 `E_DMG` + `E_RATIO`% 攻击力，有层数时魔法 `E_STACK`% 法术强度；画面、音效；这次扑棱第一枚打中英雄的给一层。
struct Shot;
impl StableEffectType for Shot {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(target) = target_of(&input) else { return };
        let Some(stat) = sim.get_entity(caster).map(|e| e.stat()) else { return };
        let Some(champion) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.is_champion()) else { return };
        let ad = E_DMG + stat.attack * E_RATIO / 100;
        sim.deal_damage_typed(caster, target, ad, DamageTypeV1::Ad, AttackTypeV1::Skill);
        if has_buff(sim, caster, &sm("p_has")) {
            let ap = stat.magic_power * E_STACK / 100;
            if ap > 0 {
                sim.deal_damage_typed(caster, target, ap, DamageTypeV1::Ap, AttackTypeV1::Skill);
            }
        }
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&sm("e_hit"), caster, &on, 0, 0, 0);
        sim.play_sfx(&sm("e_hit"), caster, &on);
        if champion && !has_buff(sim, caster, &sm("e_got")) {
            sim.add_buff(caster, &BuffV1::timed(&sm("e_got"), E_GOT_T));
            gain(sim, caster);
        }
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (E_DMG + s.attack * E_RATIO / 100, s.magic_power * E_STACK / 100)
    }
}

/// 三档龙息命中：下一 tick（这一 tick 的伤害结算完）再看生命。
struct Execute;
impl StableEffectType for Execute {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if target_of(&input).is_some() && !sim.queue_effect(&format!("{ID}:reap"), AttackTypeV1::Skill, caster, &input, 1) {
            wlog(format!("{} queue_effect({ID}:reap) refused", head(sim, caster)));
        }
    }
}

/// 生命不高于最大生命的 `E_EXEC`‰：处决（护盾一起打穿，击杀算他的）。
struct Reap;
impl StableEffectType for Reap {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(target) = target_of(&input) else { return };
        let Some(e) = sim.get_entity(target).filter(|e| e.is_alive()) else { return };
        if matches!(e.kind(), Some(EntityKindV1::Tower) | Some(EntityKindV1::Nexus)) {
            return;
        }
        let (hp, max) = e.hp();
        let champion = e.is_champion();
        if hp * 1000 <= max * E_EXEC {
            sim.deal_damage_typed(caster, target, hp + max, DamageTypeV1::Fixed, AttackTypeV1::Skill);
            sim.play_sfx(&sm("q_boom"), caster, &input);
            if champion {
                wlog(format!("{} EXECUTE #{target}: hp {hp}/{max} <= {}.{}%", head(sim, caster), E_EXEC / 10, E_EXEC % 10));
            }
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
        "=== {ID} v{} (Smolder: stacks kept through death, the tier-3 execute, Flap over walls) loaded: game {}.{}.{} abi {} log={} ===",
        VERSION,
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:dragon"), Dragon::default());
    module.add_native_effect(format!("{ID}:shot"), Shot);
    module.add_native_effect(format!("{ID}:execute"), Execute);
    module.add_native_effect(format!("{ID}:reap"), Reap);
    host.log(LogLevel::Info, "league_smolder loaded (stacks kept, the execute, Flap over walls).");
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

    fn at(cx: f64, cy: f64) -> (f64, f64) {
        (cx * CELL, cy * CELL)
    }

    fn foe(p: (f64, f64), hp_pct: usize, id: usize) -> Foe {
        Foe { at: p, hp_pct, id }
    }

    /// 一堵竖墙（第 5 列，第 2-7 行）。
    fn wall() -> Grid {
        let mut rows = vec![".........."; 10];
        for r in rows.iter_mut().take(8).skip(2) {
            *r = ".....#....";
        }
        Grid::from_rows(&rows)
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"e_far":50000,"e_dmg":3,"x":1}"#), Params { e_far: 50_000, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_stack_buffs_are_the_main_packs() {
        let names = stack_names(&Params::default());
        assert_eq!(names.len(), 5 + 4 + 8 + 6);
        assert!(names.contains(&"u4".to_string()) && !names.contains(&"u5".to_string()));
        assert!(names.contains(&"L8".to_string()) && names.contains(&"pa6".to_string()));
        for n in &names {
            assert!(sm(n).len() <= BUFF_NAME_CAP);
        }
    }

    #[test]
    fn what_death_took_comes_back() {
        let st = {
            let mut b = BuffV1::named("league_smolder_p_st");
            b.magic_power = 1;
            b
        };
        let t1 = BuffV1::named("league_smolder_t1");
        let kept = vec![st, st, st, t1];
        assert_eq!(missing(&kept, &[]).len(), 4);
        assert_eq!(missing(&kept, &[st]), vec![st, st, t1]);
        assert!(missing(&kept, &kept).is_empty());
    }

    #[test]
    fn the_pending_ladder_climbs_one_rung() {
        assert_eq!(next_rung(&[false; 6]), Some(1));
        assert_eq!(next_rung(&[true, true, false, false, false, false]), Some(3));
        assert_eq!(next_rung(&[true; 6]), None);
    }

    #[test]
    fn when_he_flies_away() {
        let p = Params::default();
        let me = at(5.0, 5.0);
        assert!(wants_out(&p, me, 30, &[foe(at(6.1, 5.0), 100, 1)], 0));
        assert!(wants_out(&p, me, 100, &[foe(at(5.8, 5.0), 100, 1)], 3));
        assert!(wants_out(&p, me, 100, &[foe(at(6.1, 5.0), 100, 1), foe(at(5.0, 6.1), 100, 2)], 0));
        assert!(!wants_out(&p, me, 100, &[foe(at(6.1, 5.0), 100, 1)], 0));
        assert!(!wants_out(&p, me, 100, &[foe(at(6.1, 5.0), 100, 1), foe(at(5.0, 6.1), 100, 2)], 2));
    }

    #[test]
    fn he_flies_over_the_wall_behind_him() {
        let p = Params::default();
        let g = wall();
        let me = at(4.6, 4.5);
        let (to, over) = plan_exit(&p, &g, me, &[at(3.8, 4.5)], None).unwrap();
        assert!(over && to.0 > 6.0 * CELL && g.clear(to), "{to:?}");
        assert!(dist(me, to) <= p.e_far as f64 + 1.0);
    }

    #[test]
    fn without_a_wall_he_flies_plain() {
        let p = Params::default();
        let g = Grid::from_rows(&vec![".........."; 10]);
        let me = at(5.0, 5.0);
        let (to, over) = plan_exit(&p, &g, me, &[at(5.8, 5.0)], Some(at(1.0, 5.0))).unwrap();
        assert!(!over && to.0 < me.0 && (dist(me, to) - p.e_plain as f64).abs() < 1.0, "{to:?}");
    }

    #[test]
    fn he_chases_a_hurt_champion() {
        let p = Params::default();
        let g = wall();
        // the one-cell wall (x 5-6 cells) between them: past it, 30000-48000 from the target, within e_far
        let me = at(4.4, 4.5);
        let prey = foe(at(7.2, 4.5), 30, 7);
        let (to, id, over) = plan_chase(&p, &g, me, 80, &[prey]).unwrap();
        assert_eq!(id, 7);
        let gap = dist(to, prey.at);
        assert!((KEEP_AT..=IN_RANGE).contains(&gap) && g.clear(to), "{to:?} {gap}");
        assert!(over, "the wall stands between them");
        // a healthy target, Smolder hurt, or an enemy already in his reach: no chase
        assert!(plan_chase(&p, &g, me, 80, &[foe(at(7.2, 4.5), 90, 7)]).is_none());
        assert!(plan_chase(&p, &g, me, 20, &[prey]).is_none());
        assert!(plan_chase(&p, &g, me, 80, &[prey, foe(at(5.0, 4.5), 100, 8)]).is_none());
    }

    #[test]
    fn on_the_moba_map_every_flight_lands_clear_of_rock() {
        let p = Params::default();
        let g = &Grid::builtin()[0];
        let (w, h) = g.size();
        let (mut flights, mut walls) = (0, 0);
        let mut y = 20_000.0;
        while y < h {
            let mut x = 20_000.0;
            while x < w {
                if !g.is_wall(x, y) {
                    for (dx, dy) in [(10_000.0, 0.0), (-10_000.0, 0.0), (0.0, 10_000.0), (0.0, -10_000.0)] {
                        if let Some((to, over)) = plan_exit(&p, g, (x, y), &[(x + dx, y + dy)], None) {
                            assert!(g.clear(to), "({x},{y}) -> {to:?}");
                            assert!(dist((x, y), to) <= p.e_far as f64 + 1.0);
                            flights += 1;
                            walls += usize::from(over);
                        }
                    }
                }
                x += 24_000.0;
            }
            y += 24_000.0;
        }
        assert!(flights > 100 && walls > 20, "{flights} flights, {walls} over walls");
    }

    #[test]
    fn the_moba_map_has_its_ninety_wall_cells() {
        assert_eq!(Grid::builtin()[0].walls(), 90);
    }

    #[test]
    fn the_names_fit() {
        for x in ["e_cd", "e_got", "e_haste", "e_ghost", "e_shot", "e_hit", "vo_cd"] {
            assert!(sm(x).len() <= BUFF_NAME_CAP);
        }
    }
}
