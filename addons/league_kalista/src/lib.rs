//! 卡莉丝塔附加包（用户 2026-10-15：「全按推荐做」；被动的跳：「这个得做啊 附加包 往前还是往后灵活判断啊」）。主包保持纯数据；
//! `mod.override_info` 把主包的卡莉丝塔换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_kalista.py 的 `native=1`
//! 生成：被动 `league_kalista:oath`；投矛后的跳由本包决定方向和挪人；大招改成对队友施放、甩出去的飞行由本包做），本包补数据做不到的事：
//!
//! - **武术姿态：往前、往后还是侧跳**（每 tick 判断，挂 `hop_f` / `hop_b` 标记给数据；数据在投矛出手时按标记放前跳 / 后跳的动作并挂
//!   `hop_go`，本包看到就逐 tick 把她挪过去，`hop_v` x `hop_t`）：照英雄联盟每次投矛后都跳（用户 10-16：「前跳后跳」——第一版站在
//!   射程里舒服的位置就不跳）：最近的敌方英雄残血（40% 以下）、或者它在逃（15 tick 里自己往外挪了 4000 以上）而且快跑出射程（超过
//!   攻击距离的 80%），就往前追；贴到射程 60% 以内、或者正冲过来（15 tick 里自己往她这边挪了 4000 以上；只看它自己的位移，她走回
//!   射程不算），就往后拉开；其余（站着对射）绕着它侧跳，
//!   左右交替，跳完离它一样远（侧跳放后跳那套腾空的动作）。身边没有敌方英雄（打小兵、野怪、塔）时照最近的敌方单位原地前后交替跳，
//!   先往前。0.2.0 之前（用户 11-01：「卡莉斯塔为什么只会往后滑？」）：其余一律往后，打小兵时两个标记都不挂、数据照主包往后跳。
//! - **誓约者**：开局（每条命出生时重新看）绑定一名队友——辅助位优先，没有就离她最近的队友英雄；大招的 AI 钩子
//!   （`league_kalista:fate`）把施放目标换成誓约者（在 `r_bind` 内、能选中时）。0.2.1（11-03 夜里的日志：誓约者是蕾欧娜，
//!   6 次大招里 2 次甩出去的是龙王、努努）：英雄联盟里这一招只能对誓约者放，他死了、太远、选不中时 AI 的大招不放
//!   （`FATE HELD`），改成打最近的敌方英雄（远了走过去）。
//! - **命运的召唤的飞行**：数据把队友拉进来、保护、定身，甩出时挂 `r_launch`；本包挑落点（离她最近的敌方英雄，`r_range` 内；
//!   没有就 2 倍范围内最近的），逐 tick 把队友朝那个英雄现在的位置飞过去（`r_fly_v`），到 `r_catch` 内挂 `r_landed`，数据在队友脚下
//!   击飞周围敌人。
//! - **撕裂斩杀**：记下她对每个敌方英雄的普攻（每根矛 `sp_t` tick），按 `e_dmg` + `e_ratio`% 攻击力、对方护甲算拔矛伤害，够杀就挂
//!   `e_ok` 让数据立刻拔（数据本来要攒到 `e_need` 根）。数据拔矛（`e_pop`）后计数清零。
//!   Q 击杀后把矛转到下一个目标做不了：矛是数据挂在目标身上的独立实例，原生代码挪不了。
//!   0.1.2（2026-10-26，剑圣无限 Q 时查到：`on_attack` 连技能的每一下伤害都会触发）：一根矛打中时同一 tick 还会有
//!   W 灵魂绑定的追加伤害等，原来每一下都记一根，计数比她身上真实的矛多，估出来的拔矛伤害偏高、打不死就提前拔了 E。
//!   现在同一个目标同一个 tick 只记一根（`add_spear`）；E 拔矛那几下照旧在 `e_pop` 亮着时清掉。
//!   0.2.5（2026-11-08 夜里的日志）：`e_ok` 也是数据阶梯的标记（3 根矛打中英雄就挂 240 tick），斩杀判定以前等身上的 `e_ok`
//!   下去才再算，阶梯一挂就停 240 tick；现在只等本包自己上次挂的（`rend_until`），数据挂着的 `e_ok` 也不去缩短。
//!   两张 5v5 地图（2026-11-10）：跳、飞都夹在这一场的地图里（`game_places::terrain::map_of_sim`：游戏自己的 960000 见方，
//!   Rin 的召唤师峡谷 1614545 见方），侧跳挑留在这张图上的那边；以前一律按 960000，峡谷上过了 960000 就被夹回半张图的边。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kalista.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `OATH`（绑了谁）、`HOP`（往哪跳、为什么）、`FATE`（拉谁、飞到谁身边、几 tick）、`REND`（斩杀判定），都限了条数。

use std::collections::{BTreeMap, HashMap};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{map_of_sim, rift_status, Map};
use mod_api_stable::*;

const ID: &str = "league_kalista";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_kalista") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
const HERO: &str = "league_kalista";
/// 数据和本包之间的标记（主包数据的施法者 buff 名）。
pub const HOP_F: &str = "league_kalista_hop_f";
pub const HOP_B: &str = "league_kalista_hop_b";
pub const HOP_GO: &str = "league_kalista_hop_go";
pub const R_LAUNCH: &str = "league_kalista_r_launch";
pub const R_LANDED: &str = "league_kalista_r_landed";
pub const R_SAFE: &str = "league_kalista_r_safe";
pub const E_OK: &str = "league_kalista_e_ok";
pub const E_CD: &str = "league_kalista_e_cd";
pub const E_POP: &str = "league_kalista_e_pop";
/// 附加包自己的：「拔了能杀」的那个敌人身上挂 6 tick，AI 钩子对它按技能 2（`FateAi::rend_now`）。
pub const E_AIM: &str = "league_kalista_e_aim";
/// 游戏自己的 5v5 地图边长（坐标 0..MAP）；峡谷的看 `Map::extent`。
const MAP: f64 = 960_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KALISTA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_kalista.log");
        }
    }
    PathBuf::from("league_kalista.log")
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
const LOG_EVERY: usize = 50;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// 这次启动已经在日志里说过峡谷了。
static RIFT_TOLD: AtomicBool = AtomicBool::new(false);

/// 这一场的地图；第一次碰到峡谷（一次启动）时日志写一行。
fn map_here(sim: &StableSim<'_>) -> Map {
    let map = map_of_sim(sim);
    if map == Map::Rift && !RIFT_TOLD.swap(true, Ordering::Relaxed) {
        wlog(format!("== Rift: hops and Fate's Call flights kept on the Rift's {:.0} square, a side hop takes the side \
                      that stays on it (not the game's own {MAP:.0}); {} ==", map.extent(), rift_status()));
    }
    map
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub hop_thr: usize,
    pub hop_v: usize,
    pub hop_t: usize,
    pub atk_range: usize,
    pub r_bind: usize,
    pub r_range: usize,
    pub r_fly_v: usize,
    pub r_catch: usize,
    pub sp_t: usize,
    pub e_dmg: usize,
    pub e_ratio: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { hop_thr: 40000, hop_v: 2000, hop_t: 12, atk_range: 52500, r_bind: 70000, r_range: 90000, r_fly_v: 4500,
               r_catch: 14000, sp_t: 240, e_dmg: 20, e_ratio: 50 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "hop_thr" => p.hop_thr = v,
            "hop_v" => p.hop_v = v,
            "hop_t" => p.hop_t = v,
            "atk_range" => p.atk_range = v,
            "r_bind" => p.r_bind = v,
            "r_range" => p.r_range = v,
            "r_fly_v" => p.r_fly_v = v,
            "r_catch" => p.r_catch = v,
            "sp_t" => p.sp_t = v,
            "e_dmg" => p.e_dmg = v,
            "e_ratio" => p.e_ratio = v,
            _ => {}
        }
    }
    p
}

static SHARED: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

fn shared() -> Params {
    SHARED.lock().unwrap_or_else(|e| e.into_inner()).clone()
}

// ===================== 计算（单元测试用） =====================

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一个敌方单位：id、位置、生命百分比、最近 FLEE_WINDOW tick 里它自己往外挪了多少（`gain`）、往她这边挪了多少（`came`）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub hp_pct: usize,
    pub gain: f64,
    pub came: f64,
}

/// 「在逃」：FLEE_WINDOW tick 里它自己往外挪了 FLEE_GAIN 以上（用户 10-16 进游戏：58 次跳全是往前——原来只看距离超过射程 80%，
/// 射手本来就站在射程边上打，等于每下都往前扑）；「冲过来」：同样的窗口里往她这边挪了 FLEE_GAIN 以上。
pub const FLEE_WINDOW: usize = 15;
pub const FLEE_GAIN: f64 = 4000.0;

/// 敌人自己往哪挪：`moved` 是它的位移（上一整段窗口、这一段到现在），投到「它 -> 她」的方向上，取往外挪得最多的（`gain`）
/// 和往她这边挪得最多的（`came`）。她自己走、自己跳都不算：0.1.x 看两人的距离变化，她往后跳完走回射程就像对方冲过来，
/// 她往后跳就像对方在逃。-> (gain, came)
pub fn its_steps(me: Pt, at: Pt, moved: [Pt; 2]) -> (f64, f64) {
    let d = dist(me, at);
    if d < 1.0 {
        return (0.0, 0.0);
    }
    let toward = |m: Pt| (m.0 * (me.0 - at.0) + m.1 * (me.1 - at.1)) / d;
    let (a, b) = (toward(moved[0]), toward(moved[1]));
    ((-a).max(-b).max(0.0), a.max(b).max(0.0))
}
/// 跳只看攻击距离这个倍数以内的敌人。
pub const REACH: f64 = 1.4;
/// 最近的敌方英雄贴到攻击距离的这个比例以内，就往后拉开。
pub const CLOSE: f64 = 0.6;
/// 打小兵的前后跳隔了这么多 tick 没跳，下一跳重新从往前开始（新的一波兵、换了野怪）。
pub const WAVE_RESET: usize = 120;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Hop {
    /// 朝 `Foe` 往前跳。
    Forward(Foe),
    /// 背离 `Foe` 往后跳。
    Back(Foe),
    /// 绕着 `Foe` 侧跳（`true` = 逆时针），跳完离它一样远。
    Side(Foe, bool),
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum HopWhy {
    /// 英雄残血：往前追。
    Low,
    /// 英雄在逃、快跑出射程：往前追。
    Fleeing,
    /// 英雄贴到射程 60% 以内：往后拉开。
    Close,
    /// 英雄正冲过来：往后拉开。
    Charging,
    /// 和英雄站着对射：左右交替侧跳。
    Strafe,
    /// 附近没有敌方英雄（小兵、野怪、塔）：原地前后交替跳。
    Wave,
}

/// 两个交替的开关：下一次侧跳往哪边（`ccw`）、下一次打小兵的跳往后（`wave_back`，不然往前）。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Turns {
    pub ccw: bool,
    pub wave_back: bool,
}

/// 投矛后往哪跳。英雄联盟里她跟着玩家的移动指令跳，前后左右都有（用户 11-01：「卡莉斯塔为什么只会往后滑？」——上一版打英雄
/// 除了追残血 / 逃跑都往后，日志 77 后 26 前，打小兵一律往后）。看攻击距离 1.4 倍内最近的敌方英雄：残血（< 40%），或者在逃
/// （离她越来越远）而且快跑出射程（> 80% 攻击距离），就往前追；贴到射程 60% 以内、或者正冲过来，就往后拉开；其余（站着对射）
/// 侧跳，左右交替，跳完离它一样远，接着打不用走回来。附近没有敌方英雄时看最近的其他敌方单位（小兵、野怪、塔），原地前后交替跳，
/// 先往前；什么都没有就 None，数据照主包往后跳。hop_thr 不再用（第一版：贴近才往后跳）。游戏自己的地图上的 [`hop_choice_on`]。
#[cfg(test)]
pub fn hop_choice(me: Pt, foes: &[Foe], units: &[Foe], turns: Turns, p: &Params) -> Option<(Hop, HopWhy)> {
    hop_choice_on(Map::Native, me, foes, units, turns, p)
}

/// [`hop_choice`] 在 `map` 上：侧跳挑留在这张图上的那边。
pub fn hop_choice_on(map: Map, me: Pt, foes: &[Foe], units: &[Foe], turns: Turns, p: &Params) -> Option<(Hop, HopWhy)> {
    let range = p.atk_range as f64;
    let nearest = |list: &[Foe]| {
        list.iter().filter(|f| dist(me, f.at) <= range * REACH).min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at))).copied()
    };
    let Some(near) = nearest(foes) else {
        let unit = nearest(units)?;
        return Some((if turns.wave_back { Hop::Back(unit) } else { Hop::Forward(unit) }, HopWhy::Wave));
    };
    let d = dist(me, near.at);
    if near.hp_pct < 40 {
        return Some((Hop::Forward(near), HopWhy::Low));
    }
    if d > range * 0.8 && near.gain >= FLEE_GAIN {
        return Some((Hop::Forward(near), HopWhy::Fleeing));
    }
    if d < range * CLOSE {
        return Some((Hop::Back(near), HopWhy::Close));
    }
    if near.came >= FLEE_GAIN {
        return Some((Hop::Back(near), HopWhy::Charging));
    }
    // the side that stays on the map
    let len = (p.hop_v * p.hop_t) as f64;
    let ccw = if inside(map, hop_end(me, Hop::Side(near, turns.ccw), len)) { turns.ccw } else { !turns.ccw };
    Some((Hop::Side(near, ccw), HopWhy::Strafe))
}

/// 单位方向：往前 = 朝目标，往后 = 背离目标，侧跳 = 以目标为圆心、她现在的距离为半径的圆上一根长 `len` 的弦（跳完离它一样远）；
/// 重合时往后跳朝画面左边（-x）、往前朝右、侧跳朝上下。
pub fn hop_dir(me: Pt, hop: Hop, len: f64) -> Pt {
    let (to, sign) = match hop {
        Hop::Forward(f) => (f.at, 1.0),
        Hop::Back(f) => (f.at, -1.0),
        Hop::Side(f, ccw) => {
            let (vx, vy) = (me.0 - f.at.0, me.1 - f.at.1);
            let r = (vx * vx + vy * vy).sqrt();
            let turn = if ccw { 1.0 } else { -1.0 };
            if r < 1.0 || len < 1.0 {
                return (0.0, turn);
            }
            // turned about the target by the angle whose chord is len
            let a = 2.0 * (len / (2.0 * r)).min(1.0).asin() * turn;
            ((f.at.0 + vx * a.cos() - vy * a.sin(), f.at.1 + vx * a.sin() + vy * a.cos()), 1.0)
        }
    };
    let (dx, dy) = (to.0 - me.0, to.1 - me.1);
    let l = (dx * dx + dy * dy).sqrt();
    if l < 1.0 {
        return (sign, 0.0);
    }
    (sign * dx / l, sign * dy / l)
}

/// 跳 `len` 之后落在哪。
pub fn hop_end(me: Pt, hop: Hop, len: f64) -> Pt {
    let d = hop_dir(me, hop, len);
    (me.0 + d.0 * len, me.1 + d.1 * len)
}

/// 在游戏自己的地图上（坐标 0..MAP）。
#[cfg(test)]
pub fn on_map(p: Pt) -> bool {
    inside(Map::Native, p)
}

/// 在 `map` 上（坐标 0..边长）。
pub fn inside(map: Map, p: Pt) -> bool {
    let e = map.extent();
    (0.0..e).contains(&p.0) && (0.0..e).contains(&p.1)
}

/// 一名队友：玩家 id、是不是辅助、英雄位置。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Mate {
    pub player: usize,
    pub support: bool,
    pub at: Option<Pt>,
}

/// 誓约者：辅助位优先（多个就近的），没有辅助就离她最近的活着的队友英雄。
pub fn pick_oath(me: Pt, mates: &[Mate]) -> Option<usize> {
    let d = |m: &Mate| m.at.map_or(f64::MAX, |a| dist(me, a));
    if let Some(m) = mates.iter().filter(|m| m.support).min_by(|a, b| d(a).total_cmp(&d(b))) {
        return Some(m.player);
    }
    mates.iter().filter(|m| m.at.is_some()).min_by(|a, b| d(a).total_cmp(&d(b))).map(|m| m.player)
}

/// 誓约者这一 tick：他活着的英雄（死了是 None）、选不选得中、离她多远（中心到中心）、两人的身体半径加起来。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Sworn {
    pub id: Option<usize>,
    pub targetable: bool,
    pub d: f64,
    pub bodies: f64,
}

/// 游戏的 AI 要放命运的召唤时拉谁（0.2.1）：英雄联盟里这一招只能对誓约者放——他活着、选得中、在 `r_bind` 内（加两人的身体：
/// 引擎和 AI 量施放距离都这么算）就对他放，不然这一下不放（`Err`：为什么）。0.2.0 这时留着 AI 自己挑的队友：11-03 夜里的日志
/// 誓约者是蕾欧娜，6 次大招里 2 次甩出去的是龙王、努努。
pub fn fate_target(sworn: Option<Sworn>, r_bind: f64) -> Result<usize, &'static str> {
    let s = sworn.ok_or("no Oathsworn")?;
    let id = s.id.ok_or("the Oathsworn is dead")?;
    if !s.targetable {
        return Err("the Oathsworn is untargetable");
    }
    if s.d > r_bind + s.bodies {
        return Err("the Oathsworn is out of reach");
    }
    Ok(id)
}

/// 一串连着的只记一行（league_ult_press 的 `ORDER_FRESH`）：AI 留着的大招每 4 tick 都再按一次。
pub const ORDER_FRESH: usize = 30;

/// A line at `tick` starts a burst: none of its kind in the `ORDER_FRESH` ticks before (`last`: that kind's last tick;
/// a tick before it is another match).
pub fn new_burst(last: Option<usize>, tick: usize) -> bool {
    last.is_none_or(|t0| tick < t0 || tick > t0 + ORDER_FRESH)
}

/// 甩出去的落点：r_range 内离她最近的敌方英雄，没有就 2 倍范围内最近的。
pub fn landing_pick(me: Pt, foes: &[Foe], p: &Params) -> Option<Foe> {
    for k in [1.0, 2.0] {
        if let Some(f) = foes.iter().filter(|f| dist(me, f.at) <= p.r_range as f64 * k)
            .min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at)))
        {
            return Some(*f);
        }
    }
    None
}

/// 游戏自己的地图上的 [`fly_step_on`]。
#[cfg(test)]
pub fn fly_step(at: Pt, to: Pt, v: f64, catch: f64) -> (Pt, bool) {
    fly_step_on(Map::Native, at, to, v, catch)
}

/// 飞行的一步：朝 `to` 走 `v`，到 `catch` 内就算到了（停在原地），夹在 `map` 上。-> (下一步的位置, 到了没有)
pub fn fly_step_on(map: Map, at: Pt, to: Pt, v: f64, catch: f64) -> (Pt, bool) {
    let d = dist(at, to);
    if d <= catch {
        return (at, true);
    }
    let go = v.min(d - catch * 0.5);
    let next = (at.0 + (to.0 - at.0) / d * go, at.1 + (to.1 - at.1) / d * go);
    (clamp_on(map, next), dist(next, to) <= catch)
}

/// 夹在游戏自己的地图上（坐标 0..MAP-1）。
#[cfg(test)]
pub fn clamp(p: Pt) -> Pt {
    clamp_on(Map::Native, p)
}

/// 夹在 `map` 上（坐标 0..边长-1）。
pub fn clamp_on(map: Map, p: Pt) -> Pt {
    let e = map.extent();
    (p.0.clamp(0.0, e - 1.0), p.1.clamp(0.0, e - 1.0))
}

/// 拔 `n` 根矛的伤害（物理，护甲按 100 / (100 + 护甲) 算）。
/// One spear on a target for this tick, once: her spear's own hit and the hits riding on it the same tick (W's
/// Soul-Marked extra, the attack's spear-hanging twin) are one spear. False: already counted this tick.
pub fn add_spear(ticks: &mut Vec<usize>, tick: usize) -> bool {
    if ticks.last() == Some(&tick) {
        return false;
    }
    ticks.push(tick);
    true
}

/// 这个 buff 算不算「杀不死」：带「不死」，但别的附加包一直挂着的被动护身（名字以 `_p_guard` / `_rv_guard` 结尾：死歌、塞恩、
/// 艾尼维亚、扎克、扎恩、tft 的石甲虫）不算——英雄联盟里处决他们照样算击杀，他们死进自己的被动里（2026-11-05 复查：死歌被动
/// 好着就一直「杀不死」）。千珏的大招、基兰的符文、凯尔的大招等真的杀不死，照样等。league_renata 的救难也是这个顺序。
pub fn holds_execute(name: &str, undying: bool) -> bool {
    undying && !name.ends_with("_p_guard") && !name.ends_with("_rv_guard")
}

pub fn rend_damage(n: usize, ad: usize, def: usize, p: &Params) -> usize {
    let raw = n * (p.e_dmg + p.e_ratio * ad / 100);
    raw * 100 / (100 + def)
}

/// 斩杀拔谁：`spears` 里按实体编号从小到大第一个拔得死的（每次跑同一局都是同一个；0.2.3 以前从 HashMap 里按它的顺序找，
/// 每份模拟的顺序都不一样，两个人都拔得死时各份拔的不是同一个）。`rend(id, 矛数)` 给拔得了的人 (伤害, 当前生命)（不在了、死了、
/// 选不中、杀不死的是 None）。-> (id, 矛数, 伤害, 生命)
pub fn rend_target(spears: &BTreeMap<usize, Vec<usize>>, rend: impl Fn(usize, usize) -> Option<(usize, usize)>)
    -> Option<(usize, usize, usize, usize)> {
    spears.iter().find_map(|(&id, v)| {
        rend(id, v.len()).filter(|&(dmg, hp)| dmg >= hp).map(|(dmg, hp)| (id, v.len(), dmg, hp))
    })
}

// ===================== 被动：誓约 =====================

#[derive(Clone, Copy)]
struct Hopping {
    dir: Pt,
    left: usize,
    /// 起跳的位置、游戏拒绝挪人的次数（日志 HOP DONE 用：用户 10-16 进游戏：「还是不前后跳」）。
    from: Pt,
    refused: usize,
    /// 照着跳的那个敌人、起跳时离它多远（日志 HOP DONE 看侧跳是不是还在原来的距离上）。
    foe: usize,
    was: f64,
}

#[derive(Clone, Copy)]
struct Flight {
    ally: usize,
    foe: usize,
    ticks: usize,
}

#[derive(Clone, Default)]
struct Oath {
    /// 誓约者（玩家 id）。
    oath: Option<usize>,
    /// 现在挂着的跳的方向标记、上次挂的 tick。
    hop_flag: Option<(&'static str, usize)>,
    hopping: Option<Hopping>,
    /// 侧跳、打小兵的前后跳下一次轮到哪边，上次打小兵跳的 tick。
    turns: Turns,
    last_wave: usize,
    flight: Option<Flight>,
    /// 敌方英雄 -> 她每根矛插上的 tick（按实体编号排：斩杀按这个顺序找，`rend_target`）。
    spears: BTreeMap<usize, Vec<usize>>,
    /// 敌方英雄 -> (取样的 tick, 那时它在哪, 上一段 FLEE_WINDOW 里它自己挪了多少)。
    gaps: HashMap<usize, (usize, Pt, Pt)>,
    /// 0.2.5：本包上次判定「拔了能杀」挂的标记到哪个 tick（`REND_FLAG`）。斩杀判定只等这个，不再等身上的 `E_OK`——数据的
    /// 阶梯（3 根矛打中英雄）也挂 `E_OK`，一挂 240 tick，以前这段时间本包的斩杀判定整个停住。
    rend_until: usize,
}

/// 「拔了能杀」时她身上的 `E_OK`、那个敌人身上的 `E_AIM` 挂多少 tick；本包的斩杀判定也歇这么久（`rend_until`）。
pub const REND_FLAG: usize = 6;

/// 0.2.5: the lethal check rests while E is cooling (`e_cd`) or the add-on's own last call still stands (`own_until`) -
/// not on `E_OK`, which the data's ladder also hangs (three spears on a champion: 240 ticks, build_kalista.py `step_to`).
pub fn rend_rests(tick: usize, own_until: usize, e_cd: bool) -> bool {
    e_cd || tick < own_until
}

/// 0.2.5: the `REND WAITS` timer (`rip`: since when, told) at `tick` - armed only while an enemy champion carries the aim
/// mark (`aimed`: the add-on's lethal call); the data's ladder's `E_OK` marks nobody (11-08: all 48 REND WAITS said
/// "target none").
pub fn rip_timer(rip: Option<(usize, bool)>, aimed: bool, tick: usize) -> Option<(usize, bool)> {
    if aimed { Some(rip.unwrap_or((tick, false))) } else { None }
}

fn ent_has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| ent_has(&e, name))
}

/// 硬控（击飞、晕眩、定身、嘲讽、恐惧、魅惑、被强制位移）。不是 `cc_count() > 0`：游戏把正在播的施法动作也记成一种控制
/// （`CcKindV1::Animation`），跳的动作一开始就把挪人叫停了——游戏里 89 跳全是「moved 0 ... cut by CC」（用户 10-16：「还是不前后跳」）。
const HARD_CC: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                                CcKindV1::Charm, CcKindV1::ForceMove];

fn hard_cc(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
    })
}

fn pos_of(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

fn foes(sim: &StableSim<'_>, team: usize) -> Vec<Foe> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_champion() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
            continue;
        }
        let (hp, max) = u.hp();
        out.push(Foe { id: u.id(), at: (u.pos().0 as f64, u.pos().1 as f64), hp_pct: if max == 0 { 100 } else { hp * 100 / max },
                       gain: 0.0, came: 0.0 });
    }
    out
}

/// 附近没有敌方英雄时跳的参照：其他敌方单位（小兵、野怪、塔、召唤物）。
fn units(sim: &StableSim<'_>, team: usize) -> Vec<Foe> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || u.is_champion() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
            continue;
        }
        out.push(Foe { id: u.id(), at: (u.pos().0 as f64, u.pos().1 as f64), hp_pct: 100, gain: 0.0, came: 0.0 });
    }
    out
}

fn set_flag(sim: &mut StableSim<'_>, me: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(me, name);
    sim.add_buff(me, &BuffV1::timed(name, ticks));
}

impl Oath {
    fn choose_oath(&mut self, sim: &StableSim<'_>, me: usize) {
        let Some(at) = pos_of(sim, me) else { return };
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let mut mates = Vec::new();
        for i in 0..sim.player_count() {
            let Some(pl) = sim.player_at(i) else { continue };
            if pl.team() != team {
                continue;
            }
            let champ = pl.champion();
            if champ.as_ref().is_some_and(|c| c.id() == me) {
                continue;
            }
            mates.push(Mate { player: pl.id(), support: pl.lane() == Some(LaneV1::Support),
                              at: champ.filter(|c| c.is_alive()).map(|c| (c.pos().0 as f64, c.pos().1 as f64)) });
        }
        let pick = pick_oath(at, &mates);
        if pick != self.oath {
            self.oath = pick;
            if let Some(k) = counted("oath") {
                let name = pick.and_then(|p| sim.get_player(p)).and_then(|pl| pl.champion()).map_or("-".into(), |c| who(sim, c.id()));
                let support = pick.and_then(|p| mates.iter().find(|m| m.player == p)).is_some_and(|m| m.support);
                wlog(format!("{} OATH bound to {name}{} #{k}", head(sim, me), if support { " (support)" } else { " (nearest)" }));
            }
        }
    }

    fn update_hop(&mut self, sim: &mut StableSim<'_>, me: usize, p: &Params) {
        let tick = sim.tick();
        let Some(at) = pos_of(sim, me) else { return };
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let mut fs = foes(sim, team);
        for f in fs.iter_mut() {
            let g = self.gaps.entry(f.id).or_insert((tick, f.at, (0.0, 0.0)));
            if tick >= g.0 + FLEE_WINDOW || tick < g.0 {
                // a sample from before it went out of sight says nothing about where it is going
                let fresh = tick >= g.0 && tick < g.0 + 2 * FLEE_WINDOW;
                *g = (tick, f.at, if fresh { (f.at.0 - g.1.0, f.at.1 - g.1.1) } else { (0.0, 0.0) });
            }
            (f.gain, f.came) = its_steps(at, f.at, [g.2, (f.at.0 - g.1.0, f.at.1 - g.1.1)]);
        }
        // no enemy champion near: the minions, monsters and towers round her
        let us = if fs.iter().any(|f| dist(at, f.at) <= p.atk_range as f64 * REACH) { Vec::new() } else { units(sim, team) };
        if self.turns.wave_back && (tick < self.last_wave || tick - self.last_wave > WAVE_RESET) {
            self.turns.wave_back = false;
        }
        let map = map_here(sim);
        let choice = hop_choice_on(map, at, &fs, &us, self.turns, p);
        // the side hop plays the hop up (hop_b), not the lunge
        let want = match choice {
            Some((Hop::Forward(_), _)) => Some(HOP_F),
            Some((Hop::Back(_) | Hop::Side(..), _)) => Some(HOP_B),
            None => None,
        };
        let had = self.hop_flag.map(|(n, _)| n);
        if want != had || self.hop_flag.is_some_and(|(_, t)| tick >= t + 3) {
            if let Some(old) = had.filter(|o| Some(*o) != want) {
                sim.entity_remove_buff(me, old);
            }
            self.hop_flag = None;
            if let Some(n) = want {
                set_flag(sim, me, n, 5);
                self.hop_flag = Some((n, tick));
            }
        }
        // the data threw the spear and played the hop: move her
        if has_buff(sim, me, HOP_GO) && self.hopping.is_none() {
            sim.entity_remove_buff(me, HOP_GO);
            if let Some((hop, why)) = choice {
                let (way, f) = match hop {
                    Hop::Forward(f) => ("FORWARD to", f),
                    Hop::Back(f) => ("BACK from", f),
                    Hop::Side(f, _) => ("SIDE round", f),
                };
                let len = (p.hop_v * p.hop_t) as f64;
                self.hopping = Some(Hopping { dir: hop_dir(at, hop, len), left: p.hop_t.max(1), from: at, refused: 0, foe: f.id,
                                              was: dist(at, f.at) });
                match hop {
                    Hop::Side(_, ccw) => self.turns.ccw = !ccw,
                    _ if why == HopWhy::Wave => {
                        self.turns.wave_back = matches!(hop, Hop::Forward(_));
                        self.last_wave = tick;
                    }
                    _ => {}
                }
                if let Some(k) = counted("hop") {
                    wlog(format!("{} HOP {way} {} ({why:?}, {:.0} away) #{k}", head(sim, me), who(sim, f.id), dist(at, f.at)));
                }
            }
        }
        if let Some(h) = self.hopping.as_mut() {
            let held = hard_cc(sim, me);
            if h.left == 0 || held {
                if let Some(k) = counted("hop_done") {
                    let now = pos_of(sim, h.foe).map_or("gone".to_string(), |f| format!("{:.0}", dist(at, f)));
                    wlog(format!("{} HOP DONE moved {:.0} of {} ({} steps refused{}), {now} from {} (was {:.0}) #{k}", head(sim, me),
                                 dist(h.from, at), p.hop_v * p.hop_t, h.refused, if held { ", cut by CC" } else { "" },
                                 who(sim, h.foe), h.was));
                }
                self.hopping = None;
            } else {
                let step = p.hop_v as f64;
                let next = clamp_on(map, (at.0 + h.dir.0 * step, at.1 + h.dir.1 * step));
                if !sim.entity_set_pos(me, next.0.round() as u64, next.1.round() as u64) {
                    h.refused += 1;
                }
                h.left -= 1;
            }
        }
    }

    fn update_fate(&mut self, sim: &mut StableSim<'_>, me: usize, p: &Params) {
        if has_buff(sim, me, R_LAUNCH) && self.flight.is_none() {
            sim.entity_remove_buff(me, R_LAUNCH);
            let Some(at) = pos_of(sim, me) else { return };
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            // the ally the data took: the one carrying her r_safe
            let ally = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).find(|u| {
                u.team() == team && u.id() != me && u.is_alive() && u.is_champion() && ent_has(u, R_SAFE)
            }).map(|u| u.id());
            let Some(ally) = ally else {
                if let Some(k) = counted("fate") {
                    wlog(format!("{} FATE launch but no ally carries {R_SAFE}: landed in place #{k}", head(sim, me)));
                }
                set_flag(sim, me, R_LANDED, 6);
                return;
            };
            let fs = foes(sim, team);
            match landing_pick(at, &fs, p) {
                Some(f) => {
                    self.flight = Some(Flight { ally, foe: f.id, ticks: 0 });
                    if let Some(k) = counted("fate") {
                        // 0.2.1: only the Oathsworn should ever fly (the hook holds the AI's R on anyone else)
                        let sworn = self.oath.and_then(|o| sim.get_player(o)).and_then(|pl| pl.champion()).map(|c| c.id());
                        wlog(format!("{} FATE {} hurled at {} ({:.0} away, {}% hp){} #{k}", head(sim, me), who(sim, ally),
                                     who(sim, f.id), dist(at, f.at), f.hp_pct,
                                     if sworn == Some(ally) { "" } else { " - NOT the Oathsworn" }));
                    }
                }
                None => {
                    set_flag(sim, me, R_LANDED, 6);
                    if let Some(k) = counted("fate") {
                        wlog(format!("{} FATE {} has no enemy champion to land on: knock-up where he is #{k}", head(sim, me),
                                     who(sim, ally)));
                    }
                }
            }
        }
        if let Some(fl) = self.flight.as_mut() {
            fl.ticks += 1;
            let (Some(a), alive) = (pos_of(sim, fl.ally), sim.get_entity(fl.ally).is_some_and(|e| e.is_alive())) else {
                self.flight = None;
                return;
            };
            let to = sim.get_entity(fl.foe).filter(|e| e.is_alive()).map(|e| (e.pos().0 as f64, e.pos().1 as f64));
            let done = match (alive, to) {
                (true, Some(to)) if fl.ticks <= 40 => {
                    let (next, arrived) = fly_step_on(map_here(sim), a, to, p.r_fly_v as f64, p.r_catch as f64);
                    sim.entity_set_pos(fl.ally, next.0.round() as u64, next.1.round() as u64);
                    arrived
                }
                _ => true,
            };
            if done {
                set_flag(sim, me, R_LANDED, 6);
                if let Some(k) = counted("fate_land") {
                    wlog(format!("{} FATE {} landed after {} ticks #{k}", head(sim, me), who(sim, fl.ally), fl.ticks));
                }
                self.flight = None;
            }
        }
    }

    fn update_rend(&mut self, sim: &mut StableSim<'_>, me: usize, p: &Params) {
        let tick = sim.tick();
        if has_buff(sim, me, E_POP) {
            self.spears.clear();
        }
        self.spears.retain(|_, v| {
            v.retain(|t| tick < t + p.sp_t);
            !v.is_empty()
        });
        // 0.2.5: rests on its own call only (the data's ladder hangs E_OK as well, 240 ticks: the lethal check stood still)
        if rend_rests(tick, self.rend_until, has_buff(sim, me, E_CD)) {
            return;
        }
        let Some(ad) = sim.get_entity(me).map(|e| e.stat().attack) else { return };
        // the first one (by entity id: the same in every run, 0.2.3) the spears kill now
        let kill = rend_target(&self.spears, |id, n| {
            let e = sim.get_entity(id)?;
            // 选不中的、挂着不死的（阿克尚复活前停在 1 血）拔了也杀不死（2026-11-01 复查：对 1 血的阿克尚报了 33 次）；别的
            // 附加包的被动护身（*_p_guard / *_rv_guard）不算，撕裂照样拔、他们死进被动里（0.2.2）
            if !e.is_alive() || !e.is_targetable()
                || (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| holds_execute(b.name(), b.undying))
            {
                return None;
            }
            Some((rend_damage(n, ad, e.stat().defence, p), e.hp().0))
        });
        if let Some((id, n, dmg, hp)) = kill {
            // the data's ladder may hold E_OK already (240 ticks): left as it is, not cut to REND_FLAG
            if !has_buff(sim, me, E_OK) {
                set_flag(sim, me, E_OK, REND_FLAG);
            }
            set_flag(sim, id, E_AIM, REND_FLAG);
            self.rend_until = tick + REND_FLAG;
            if let Some(k) = counted("rend") {
                wlog(format!("{} REND {} spears in {} would deal {dmg} against {hp} hp: rip now #{k}", head(sim, me), n,
                             who(sim, id)));
            }
        }
    }
}

impl StablePassive for Oath {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let p = parse_params(params_json);
        let mut s = SHARED.lock().unwrap_or_else(|e| e.into_inner());
        if *s != p {
            wlog(format!("params {params_json} -> {p:?}"));
            *s = p;
        }
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.hop_flag = None;
        self.hopping = None;
        self.turns = Turns::default();
        self.last_wave = 0;
        self.flight = None;
        self.spears.clear();
        self.rend_until = 0;
        self.oath = None;
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN {} (the add-on's Kalista) #{k}", head(sim, entity), who(sim, entity)));
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _player: usize, _entity: usize, target: usize, _damage: &mut usize) {
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            add_spear(self.spears.entry(target).or_default(), sim.tick());
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        let p = shared();
        if self.oath.is_none() || sim.tick() % 60 == 0 {
            self.choose_oath(sim, me);
        }
        self.update_hop(sim, me, &p);
        self.update_fate(sim, me, &p);
        self.update_rend(sim, me, &p);
    }
}

// ===================== AI 钩子：大招对誓约者施放 =====================

#[derive(Clone, Default)]
struct FateAi {
    /// 每种行最近一次的 tick（`new_burst`：一串只记一行）。
    lines: Vec<(&'static str, usize)>,
    /// 拔矛连按的记录和歇到哪个 tick（`PRESS_MAX` / `BACKOFF`，0.2.3）。
    presses: Presses,
    hold_until: usize,
    /// 这一段「拔了能杀」（E_OK）从哪个 tick 起、为什么没按记过没有（`waits`，0.2.4）。
    rip: Option<(usize, bool)>,
}

/// 「拔了能杀」挂了这么多 tick 还没按出去，记一行是哪道门挡着（0.2.4）。
pub const RIP_QUIET: usize = 30;

/// 拔矛（技能 2）连着按了这么多 tick 还没放出去（放出去了格子进冷却，下一 tick 就不按了）：有东西挡着，歇 `BACKOFF` tick
/// 再看（0.2.3，league_orianna 0.3.2 的数）。
pub const PRESS_MAX: usize = 3;
pub const BACKOFF: usize = 30;

/// 连按的记录：第一下、上一下、连着几下（league_orianna 的 `Presses`，这里只有拔矛一种）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Presses {
    pub first: usize,
    pub last: usize,
    pub n: usize,
}

impl Presses {
    /// One more press at `tick`: how many in a row (the tick after the last one), 1 for a new run.
    pub fn press(&mut self, tick: usize) -> usize {
        if self.n > 0 && tick == self.last + 1 {
            self.n += 1;
        } else {
            *self = Presses { first: tick, last: tick, n: 1 };
        }
        self.last = tick;
        self.n
    }
}

/// 放不出技能的控制（league_ult_press 的 `NO_CAST`）。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];
/// 正在出招（普攻的前摇、跳的动作，游戏记成 `Animation`）或被强制位移：这时按的技能游戏不收（league_ult_press 的 `BUSY`）。
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];

/// Any of `kinds` among the crowd-control codes.
pub fn any_cc(codes: impl IntoIterator<Item = u32>, kinds: &[CcKindV1]) -> bool {
    codes.into_iter().any(|c| kinds.iter().any(|k| k.code() == c))
}

/// 一个单位身上的控制，日志用（`Stun 30, Animation hop_b 5`：种类、动作名、引擎记的 tick）。
fn cc_names(e: &StableEntity<'_, '_>) -> String {
    let v: Vec<String> = (0..e.cc_count()).filter_map(|i| e.cc_at(i))
        .map(|c| {
            let kind = CcKindV1::from_code(c.kind).map_or_else(|| format!("kind {}", c.kind), |k| format!("{k:?}"));
            if c.kind == CcKindV1::Animation.code() { format!("{kind} {} {}", c.name(), c.tick) } else { format!("{kind} {}", c.tick) }
        })
        .collect();
    v.join(", ")
}

impl FateAi {
    /// One more line of `kind` at `tick`: true when it starts a burst (`new_burst`), the line to be written.
    fn burst(&mut self, kind: &'static str, tick: usize) -> bool {
        let last = self.lines.iter().find(|(k, _)| *k == kind).map(|&(_, t)| t);
        self.lines.retain(|(k, _)| *k != kind);
        self.lines.push((kind, tick));
        new_burst(last, tick)
    }
}

/// 大招不放时改做的（0.2.1）：最近的看得见的敌方英雄在射程里（加两人的身体）就打他，远了走过去，一个都没有就站一下。
enum Instead {
    Attack(usize),
    Walk((u64, u64)),
    Stand,
}

impl StablePlayerAi for FateAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:fate")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let was = base.and_then(|b| InputKindV1::from_code(b.kind));
        if was != Some(InputKindV1::Ult) {
            return self.rend_now(ctx, was);
        }
        let b = base?;
        if InputTargetKindV1::from_code(b.target.kind) != Some(InputTargetKindV1::Target) {
            return None;
        }
        let current = b.target.target_id;
        let player = ctx.player_id();
        let tick = ctx.tick();
        let p = shared();
        let (pick, head, names, instead, here) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let (mid, team) = (me.id(), me.team());
            let at = (me.pos().0 as f64, me.pos().1 as f64);
            let my_r = me.radius() as f64;
            let mut mates = Vec::new();
            for i in 0..sim.player_count() {
                let Some(pl) = sim.player_at(i) else { continue };
                if pl.team() != team {
                    continue;
                }
                let champ = pl.champion();
                if champ.as_ref().is_some_and(|c| c.id() == mid) {
                    continue;
                }
                // the live champion as it stands: (id, targetable, distance, radius)
                let live = champ.as_ref().filter(|c| c.is_alive()).map(|c| {
                    (c.id(), c.is_targetable(), dist(at, (c.pos().0 as f64, c.pos().1 as f64)), c.radius() as f64)
                });
                let c = champ.filter(|c| c.is_alive() && c.is_targetable());
                mates.push((Mate { player: pl.id(), support: pl.lane() == Some(LaneV1::Support),
                                   at: c.as_ref().map(|c| (c.pos().0 as f64, c.pos().1 as f64)) },
                            live));
            }
            let list: Vec<Mate> = mates.iter().map(|m| m.0).collect();
            let oath = pick_oath(at, &list);
            let sworn = oath.and_then(|o| mates.iter().find(|m| m.0.player == o)).map(|&(_, live)| Sworn {
                id: live.map(|l| l.0),
                targetable: live.is_some_and(|l| l.1),
                d: live.map_or(f64::MAX, |l| l.2),
                bodies: my_r + live.map_or(0.0, |l| l.3),
            });
            let oath_name = oath.and_then(|o| sim.get_player(o)).and_then(|pl| pl.champion())
                .map_or_else(|| "nobody".to_string(), |c| who(&sim, c.id()));
            let away = sworn.filter(|s| s.id.is_some()).map_or(String::new(), |s| format!(", {:.0} away", s.d));
            // R held: the nearest enemy champion she can see - in her reach an attack, further a walk toward him
            let foe = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|u| {
                    u.team() != team && u.is_champion() && u.is_alive() && u.is_targetable() && sim.is_visible(team, u.id())
                })
                .map(|u| (u.id(), u.pos(), dist(at, (u.pos().0 as f64, u.pos().1 as f64)), u.radius() as f64))
                .min_by(|a, b| a.2.total_cmp(&b.2));
            let instead = match foe {
                Some((id, _, d, r)) if d <= p.atk_range as f64 + my_r + r => Instead::Attack(id),
                Some((_, pos, _, _)) => Instead::Walk(pos),
                None => Instead::Stand,
            };
            let pick = fate_target(sworn, p.r_bind as f64);
            let names = (who(&sim, current), pick.map_or_else(|_| format!("{oath_name}{away}"), |id| who(&sim, id)));
            (pick, head(&sim, mid), names, instead, me.pos())
        };
        let why = match pick {
            Ok(id) if id == current => return None,
            Ok(id) => {
                let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(id));
                if ctx.is_valid_input(&input) {
                    if let Some(k) = counted("fate_ai") {
                        wlog(format!("{head} FATE target {} -> the Oathsworn {} #{k}", names.0, names.1));
                    }
                    return Some(input);
                }
                "the game took no R on the Oathsworn"
            }
            Err(why) => why,
        };
        // 0.2.1 (11-03 night logs: 2 of 6 Fate's Calls hurled Aurelion Sol and Nunu with Leona bound): in League R only
        // takes the Oathsworn - dead, out of reach or untargetable, the AI's R is held and she fights on
        let stand = InputV1::move_to(here.0, here.1);
        let (input, did) = match instead {
            Instead::Attack(t) => {
                let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                if ctx.is_valid_input(&attack) {
                    (attack, format!("attacking #{t} instead"))
                } else {
                    (stand, "standing (the attack not taken)".to_string())
                }
            }
            Instead::Walk((x, y)) => (InputV1::move_to(x, y), "walking toward the nearest enemy champion".to_string()),
            Instead::Stand => (stand, "standing (no enemy champion in sight)".to_string()),
        };
        if self.burst("fate_held", tick) {
            if let Some(k) = counted("fate_held") {
                wlog(format!("{head} FATE HELD: the AI's R on {}, but {why} ({}) - {did} #{k}", names.0, names.1));
            }
        }
        Some(input)
    }
}

impl FateAi {
    /// 「拔了能杀」（被动在她身上挂 `E_OK`、在那个敌人身上挂 `E_AIM`）时自己按技能 2：数据只在矛打中英雄、或游戏的 AI 按技能 2
    /// 的时候看 `e_ok`，游戏的 AI 一两分钟才按一次，「立刻拔」常常等到下一矛（2026-11-01 复查：18 次 rip now 都没拔）。
    /// 0.2.3（2026-11-06 的日志：`REND PRESS` 每 tick 一行、一串 5–10 tick，目标的血一点没掉；REND PRESS 记到 #1150，rip now
    /// 才 #450）：正在出招（普攻的前摇、跳的动作）、被强制位移、被控时不按——这时按的游戏不收；连按 `PRESS_MAX` tick 还没放出去
    /// 就歇 `BACKOFF` tick，记一行「not taken」写出她身上的控制、技能 2 和普攻的冷却、目标的状态；一串只记第一下。
    /// 0.2.4（2026-11-08 的日志：一段 rip now 挂了 300 tick 没按、没拔，目标的血也几乎没掉）：每道门挡住时不再悄悄返回，
    /// 一段 E_OK 挂过 `RIP_QUIET` tick 还没按出去就记一行 `REND WAITS`（哪道门、她身上的控制和引擎记的 tick、目标多远、离他的塔
    /// 多远），下次的日志看清是谁挡的再改。
    /// 0.2.5（2026-11-08 夜里的日志：48 条 REND WAITS 全是 `target none`）：`E_OK` 也是数据阶梯的标记（3 根矛打中英雄就挂 240
    /// tick），那时没人身上有 `E_AIM`、本包也不按；等的计时只在有敌方英雄挂着 `E_AIM` 时才开始（`rip_timer`）。
    fn rend_now(&mut self, ctx: &mut StableAiContext<'_>, was: Option<InputKindV1>) -> Option<InputV1> {
        if was == Some(InputKindV1::Skill2) {
            return None;
        }
        let tick = ctx.tick();
        let player = ctx.player_id();
        let (target, gate, head_line, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            let mid = me.id();
            if !me.is_alive() || !has_buff(&sim, mid, E_OK) || has_buff(&sim, mid, E_CD) {
                self.rip = None;
                return None;
            }
            let team = me.team();
            let target = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .find(|u| u.team() != team && u.is_alive() && u.is_champion() && has_buff(&sim, u.id(), E_AIM))
                .map(|u| u.id());
            // the data's ladder's E_OK marks nobody: nothing for the hook to press, nothing to wait for (0.2.5)
            self.rip = rip_timer(self.rip, target.is_some(), tick);
            if target.is_none() {
                return None;
            }
            let codes: Vec<u32> = (0..me.cc_count()).filter_map(|i| me.cc_at(i)).map(|c| c.kind).collect();
            // 技能 2 解锁了（3 级）、试拔的格子好了（引擎的「输入合法」不看冷却和解锁）；正在出招（普攻的前摇、跳的动作）、
            // 被强制位移、被控时不按——这时按的游戏不收（0.2.3）
            let gate = if tick < self.hold_until {
                Some("backing off after presses nothing took")
            } else if !me.cooldown(SkillSlotV1::Skill2).is_some_and(|c| c.unlocked && c.remaining == 0) {
                Some("skill 2 locked or its try slot cooling")
            } else if any_cc(codes.iter().copied(), &BUSY) {
                Some("busy: an attack's wind-up, the hop's pose or a push")
            } else if any_cc(codes, &NO_CAST) {
                Some("held by crowd control")
            } else {
                None
            };
            let line = target.map(|t| format!("{} REND PRESS: Skill2 on {}", head(&sim, mid), who(&sim, t)));
            (target, gate, head(&sim, mid), line)
        };
        if let Some(why) = gate {
            self.waits(ctx, player, target, tick, why, &head_line);
            return None;
        }
        let (target, line) = (target?, line?);
        let input = InputV1::action(InputKindV1::Skill2, InputTargetV1::target(target));
        if !ctx.is_valid_input(&input) {
            self.waits(ctx, player, Some(target), tick, "the engine refuses the press (is_valid_input)", &head_line);
            return None;
        }
        // a run of presses nothing took (a rip that goes out starts the slot's cooldown: no press the next tick): back off
        let n = self.presses.press(tick);
        if n > PRESS_MAX {
            self.hold_until = tick + BACKOFF;
            if let Some(k) = counted("rend_blocked") {
                let state = rend_blocker(ctx, player, Some(target));
                wlog(format!("{line}: pressed {} ticks running since t={} and not taken ({state}) - backing off {BACKOFF} ticks #{k}",
                             n - 1, self.presses.first));
            }
            return None;
        }
        if n == 1 {
            if let Some(k) = counted("rend_press") {
                wlog(format!("{line} #{k}"));
            }
        }
        Some(input)
    }

    /// 「拔了能杀」挂了 `RIP_QUIET` tick 还没按出去：这一段只记一次是哪道门挡着、她和目标的状态（0.2.4）。
    fn waits(&mut self, ctx: &mut StableAiContext<'_>, player: usize, target: Option<usize>, tick: usize, why: &str, head_line: &str) {
        let Some((since, told)) = self.rip else { return };
        if told || tick < since + RIP_QUIET {
            return;
        }
        self.rip = Some((since, true));
        if let Some(k) = counted("rend_waits") {
            let state = rend_blocker(ctx, player, target);
            wlog(format!("{head_line} REND WAITS {} ticks: {why} ({state}) #{k}", tick - since));
        }
    }
}

/// 拔矛「not taken」那一行写的：她身上的控制和标记、技能 2 和普攻的冷却，目标选不选得中、看不看得见、身上的控制和生命。
fn rend_blocker(ctx: &mut StableAiContext<'_>, player: usize, target: Option<usize>) -> String {
    let Some(sim) = ctx.sim() else { return "no sim".to_string() };
    let Some(me) = sim.get_player(player).and_then(|p| p.champion()) else { return "no champion".to_string() };
    let cd = |s: SkillSlotV1| me.cooldown(s).map_or("?".to_string(), |c| format!("{}/{}", c.remaining, c.cooltime));
    let flags: Vec<&str> = [HOP_GO, E_OK, E_CD, E_POP].into_iter().filter(|f| ent_has(&me, f)).map(|f| &f[15..]).collect();
    let at = pos_of(&sim, me.id()).unwrap_or((0.0, 0.0));
    let it = match target.and_then(|t| sim.get_entity(t).map(|e| (t, e))) {
        Some((t, e)) => {
            let ta = pos_of(&sim, t).unwrap_or((0.0, 0.0));
            // the nearest of his towers (the spear's twin hits `EnemyWithoutTower`: does a champion under his tower count?)
            let tower = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() == e.team() && u.is_alive() && u.kind() == Some(EntityKindV1::Tower))
                .filter_map(|u| pos_of(&sim, u.id()))
                .map(|p| dist(p, ta))
                .fold(f64::INFINITY, f64::min);
            format!("{}{}{}, cc [{}], hp {}/{}, {:.0} from her, his tower {:.0} from him", who(&sim, t),
                    if e.is_targetable() { "" } else { " untargetable" },
                    if sim.is_visible(me.team(), t) { "" } else { " unseen" }, cc_names(&e), e.hp().0, e.hp().1,
                    dist(at, ta), tower)
        }
        None => "none".to_string(),
    };
    format!("her cc [{}], flags [{}], E {} attack {}; target {it}", cc_names(&me), flags.join(" "), cd(SkillSlotV1::Skill2),
            cd(SkillSlotV1::Attack))
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Kalista: the hop's way, the Oathsworn and Fate's Call's flight, Rend's execute) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:oath"), Oath::default());
    module.add_player_input_ai(FateAi::default());
    host.log(LogLevel::Info, "league_kalista loaded (hop forward / back / sideways, Oathsworn, Fate's Call flight, Rend execute).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rend_waits_while_she_casts_and_backs_off_a_run_nothing_took() {
        // 11-06's logs: REND PRESS every tick for 5-10 ticks while the target's health did not move
        assert!(any_cc([CcKindV1::Animation.code()], &BUSY), "an attack's wind-up or the hop's pose");
        assert!(any_cc([CcKindV1::ForceMove.code()], &BUSY));
        assert!(any_cc([CcKindV1::Stun.code(), CcKindV1::BlockSkill.code()], &NO_CAST));
        assert!(!any_cc([CcKindV1::Stun.code()], &BUSY));
        assert!(!any_cc(Vec::<u32>::new(), &NO_CAST));
        let mut p = Presses::default();
        assert_eq!(p.press(15625), 1);
        assert_eq!((15626..=15628).map(|t| p.press(t)).last(), Some(4));
        assert!(p.n > PRESS_MAX && p.first == 15625);
        // a gap (the rip went out, or she was busy) starts a new run
        assert_eq!(p.press(15700), 1);
        assert_eq!(p.press(15701), 2);
        assert_eq!(&HOP_GO[15..], "hop_go");
    }

    /// 0.2.5 (the 11-08 night logs: all 48 REND WAITS said "target none" - the data's ladder hangs E_OK on three spears
    /// for 240 ticks, marking nobody): the wait is timed only while an enemy champion carries the aim mark, and the
    /// lethal check rests on the add-on's own call, not on E_OK.
    #[test]
    fn the_ladders_e_ok_neither_starts_the_wait_nor_pauses_the_lethal_check() {
        // `t=1345 REND WAITS 30 ticks: skill 2 locked ... flags [e_ok] ... target none`: no aim mark, no timer
        assert_eq!(rip_timer(None, false, 1_315), None);
        assert_eq!(rip_timer(Some((1_315, false)), false, 1_345), None, "the ladder's E_OK: the timer goes");
        // the add-on's call marks him: timed from the first tick, kept (and its told flag) while he stays marked
        assert_eq!(rip_timer(None, true, 2_000), Some((2_000, false)));
        assert_eq!(rip_timer(Some((2_000, true)), true, 2_040), Some((2_000, true)));
        // the lethal check: E cooling rests it; so does its own last call for REND_FLAG ticks - and nothing else
        assert!(rend_rests(500, 0, true));
        assert!(rend_rests(500, 500 + 1, false) && rend_rests(500, 500 + REND_FLAG, false));
        assert!(!rend_rests(500 + REND_FLAG, 500 + REND_FLAG, false), "its own call over: checked again");
        assert!(!rend_rests(1_400, 0, false), "the data's ladder E_OK up 240 ticks: the check still runs");
    }

    #[test]
    fn hits_of_one_tick_are_one_spear() {
        let mut v = Vec::new();
        assert!(add_spear(&mut v, 100));
        assert!(!add_spear(&mut v, 100), "W's extra on the same spear");
        assert!(!add_spear(&mut v, 100), "the attack's twin");
        assert!(add_spear(&mut v, 146), "the next attack");
        assert!(add_spear(&mut v, 150), "Q's spear a few ticks later");
        assert_eq!(v, [100, 146, 150]);
    }

    fn foe(id: usize, at: Pt, hp_pct: usize) -> Foe {
        Foe { id, at, hp_pct, gain: 0.0, came: 0.0 }
    }

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"hop_v":2000,"junk":3,"r_fly_v":5000}"#);
        assert_eq!((p.hop_v, p.r_fly_v, p.hop_t), (2000, 5000, 12));
    }

    #[test]
    fn the_copy_carries_the_params_the_flags_and_the_ally_cast() {
        let copy = include_str!("../override/league_kalista.data_champion");
        let at = copy.find("\"passive_ref\": \"league_kalista:oath\"").expect("no league_kalista:oath passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("hop_v", d.hop_v), ("hop_t", d.hop_t), ("r_fly_v", d.r_fly_v), ("r_catch", d.r_catch),
                       ("e_dmg", d.e_dmg), ("e_ratio", d.e_ratio), ("sp_t", d.sp_t)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for name in [HOP_F, HOP_B, HOP_GO, R_LAUNCH, R_LANDED, R_SAFE, E_OK, E_CD, E_POP] {
            assert!(copy.contains(&format!("\"{name}\"")), "{name} is not in the copy");
        }
        let ult = &copy[copy.find("\"ult\"").unwrap()..];
        let target = &ult[ult.find("\"casting_target\"").unwrap()..][..40];
        assert!(target.contains("\"AllyNotSelf\""), "the copy's ult is not cast on an ally: {target}");
        // the add-on's hop flags first; the main pack's MoveBack stays only for no enemy near at all (neither flag)
        let f = copy.find(HOP_F).expect("the copy has no hop_f switch");
        let back = copy.find("\"MoveBack\"").expect("the copy has no fallback hop");
        assert!(f < back, "the copy's MoveBack comes before the add-on's hop flags");
    }

    #[test]
    fn hop_forward_back_or_round_them_like_league() {
        let p = Params::default();
        let len = (p.hop_v * p.hop_t) as f64;
        let me = (500_000.0, 500_000.0);
        let at = |dx: f64, dy: f64| (me.0 + dx, me.1 + dy);
        let t = Turns::default();
        // low: forward even when close
        let low = foe(3, at(25_000.0, 0.0), 30);
        assert_eq!(hop_choice(me, &[low], &[], t, &p), Some((Hop::Forward(low), HopWhy::Low)));
        // running off near the edge of her range: forward
        let leaving = Foe { gain: FLEE_GAIN, ..foe(2, at(0.0, 45_000.0), 100) };
        assert_eq!(hop_choice(me, &[leaving], &[], t, &p), Some((Hop::Forward(leaving), HopWhy::Fleeing)));
        assert_eq!(hop_dir(me, Hop::Forward(leaving), len), (0.0, 1.0));
        // inside 60 % of her range: back, away from it
        let close = foe(1, at(30_000.0, 0.0), 100);
        assert_eq!(hop_choice(me, &[close], &[], t, &p), Some((Hop::Back(close), HopWhy::Close)));
        assert_eq!(hop_dir(me, Hop::Back(close), len), (-1.0, 0.0));
        // coming at her from further off: back
        let charging = Foe { came: FLEE_GAIN, ..foe(4, at(45_000.0, 0.0), 100) };
        assert_eq!(hop_choice(me, &[charging], &[], t, &p), Some((Hop::Back(charging), HopWhy::Charging)));
        // standing at range (the usual trade, 77 of 103 hops in the 11-01 log went back here): round it, either way
        let edge = foe(5, at(45_000.0, 0.0), 80);
        assert_eq!(hop_choice(me, &[edge], &[], t, &p), Some((Hop::Side(edge, false), HopWhy::Strafe)));
        let other = Turns { ccw: true, ..t };
        assert_eq!(hop_choice(me, &[edge], &[], other, &p), Some((Hop::Side(edge, true), HopWhy::Strafe)));
        // the nearest decides
        assert_eq!(hop_choice(me, &[leaving, close], &[], t, &p).map(|c| c.1), Some(HopWhy::Close));
        // no champion near: the minion beside her, forward then back (in place)
        let minion = foe(9, at(-40_000.0, 0.0), 100);
        let far = foe(6, at(200_000.0, 0.0), 10);
        assert_eq!(hop_choice(me, &[far], &[minion], t, &p), Some((Hop::Forward(minion), HopWhy::Wave)));
        let back = Turns { wave_back: true, ..t };
        assert_eq!(hop_choice(me, &[far], &[minion], back, &p), Some((Hop::Back(minion), HopWhy::Wave)));
        let (fwd, bwd) = (hop_end(me, Hop::Forward(minion), len), hop_end(me, Hop::Back(minion), len));
        assert!((fwd.0 + bwd.0) / 2.0 == me.0 && fwd.1 == me.1 && bwd.1 == me.1, "the pair ends where it began");
        // a champion near counts before the minions
        assert_eq!(hop_choice(me, &[edge], &[minion], t, &p).map(|c| c.1), Some(HopWhy::Strafe));
        // nobody near: no flag, the data's own MoveBack
        assert_eq!(hop_choice(me, &[far], &[], t, &p), None);
        assert_eq!(hop_choice(me, &[far], &[foe(7, at(0.0, 90_000.0), 100)], t, &p), None);
    }

    #[test]
    fn a_side_hop_keeps_her_distance_and_stays_on_the_map() {
        let p = Params::default();
        let len = (p.hop_v * p.hop_t) as f64;
        let me = (500_000.0, 500_000.0);
        let it = foe(1, (545_000.0, 500_000.0), 80);
        let ends = [false, true].map(|ccw| hop_end(me, Hop::Side(it, ccw), len));
        for end in ends {
            assert!((dist(me, end) - len).abs() < 1.0, "the hop is {len} long: {end:?}");
            assert!((dist(end, it.at) - 45_000.0).abs() < 1.0, "as far from it after the hop: {end:?}");
        }
        assert!((ends[0].1 - me.1) * (ends[1].1 - me.1) < 0.0, "the two turns go opposite ways: {ends:?}");
        // the same 24000 moved step by step from her spot (hop_v a tick for hop_t ticks)
        let dir = hop_dir(me, Hop::Side(it, true), len);
        let mut at = me;
        for _ in 0..p.hop_t {
            at = clamp((at.0 + dir.0 * p.hop_v as f64, at.1 + dir.1 * p.hop_v as f64));
        }
        assert!(dist(at, ends[1]) < 1.0);
        // at the map's edge both turns take the side that stays on it
        let low_edge = (500_000.0, 5_000.0);
        let it2 = foe(2, (545_000.0, 5_000.0), 80);
        let side = |turns: Turns| match hop_choice(low_edge, &[it2], &[], turns, &p) {
            Some((Hop::Side(_, ccw), HopWhy::Strafe)) => ccw,
            x => panic!("{x:?}"),
        };
        let t = Turns::default();
        assert_eq!(side(t), side(Turns { ccw: true, ..t }));
        assert!(on_map(hop_end(low_edge, Hop::Side(it2, side(t)), len)));
        assert!(!on_map(hop_end(low_edge, Hop::Side(it2, !side(t)), len)));
    }

    #[test]
    fn on_the_rift_hops_and_flights_stay_on_its_bigger_square() {
        let p = Params::default();
        let rift = Map::Rift.extent();
        // past 960000 is the Rift's ground: on it, not clamped back to the game's own edge
        assert!(inside(Map::Rift, (1_200_000.0, 1_500_000.0)) && !on_map((1_200_000.0, 1_500_000.0)));
        assert!(!inside(Map::Rift, (rift, 10.0)) && !inside(Map::Rift, (-1.0, 10.0)));
        assert_eq!(clamp_on(Map::Rift, (1_300_000.0, 2_000_000.0)), (1_300_000.0, rift - 1.0));
        assert_eq!(clamp_on(Map::Native, (1_300_000.0, 5.0)), clamp((1_300_000.0, 5.0)));
        // by the game's own far edge (y 955000): there both turns take the side on it; the Rift has room both ways
        let edge = (500_000.0, 955_000.0);
        let it = foe(2, (545_000.0, 955_000.0), 80);
        let side = |map: Map, at: Pt, f: Foe, turns: Turns| match hop_choice_on(map, at, &[f], &[], turns, &p) {
            Some((Hop::Side(_, ccw), HopWhy::Strafe)) => ccw,
            x => panic!("{x:?}"),
        };
        let t = Turns::default();
        let ccw = Turns { ccw: true, ..t };
        assert_eq!(side(Map::Native, edge, it, t), side(Map::Native, edge, it, ccw));
        assert_ne!(side(Map::Rift, edge, it, t), side(Map::Rift, edge, it, ccw), "the Rift: either side, by turns");
        assert_eq!(hop_choice(edge, &[it], &[], t, &p), hop_choice_on(Map::Native, edge, &[it], &[], t, &p));
        // at the Rift's own far edge both turns take the side that stays on it
        let far = (1_000_000.0, rift - 5_000.0);
        let it2 = foe(3, (1_045_000.0, far.1), 80);
        assert_eq!(side(Map::Rift, far, it2, t), side(Map::Rift, far, it2, ccw));
        let len = (p.hop_v * p.hop_t) as f64;
        assert!(inside(Map::Rift, hop_end(far, Hop::Side(it2, side(Map::Rift, far, it2, t)), len)));
        // Fate's Call flies on past 960000 on the Rift (the game's own map stops it at its edge)
        let (from, to) = ((958_000.0, 500_000.0), (1_200_000.0, 500_000.0));
        let (next, _) = fly_step_on(Map::Rift, from, to, p.r_fly_v as f64, p.r_catch as f64);
        assert_eq!(next, (958_000.0 + p.r_fly_v as f64, 500_000.0));
        assert_eq!(fly_step(from, to, p.r_fly_v as f64, p.r_catch as f64).0, (MAP - 1.0, 500_000.0));
    }

    #[test]
    fn only_its_own_steps_say_running_off_or_coming_at_her() {
        let me = (0.0, 0.0);
        let at = (45_000.0, 0.0);
        // walked 13500 straight at her in the last window: coming; away this window: running off; across: neither
        assert_eq!(its_steps(me, at, [(-13_500.0, 0.0), (0.0, 0.0)]), (0.0, 13_500.0));
        assert_eq!(its_steps(me, at, [(0.0, 0.0), (6_000.0, 0.0)]), (6_000.0, 0.0));
        let (gain, came) = its_steps(me, at, [(0.0, 13_500.0), (0.0, -2_000.0)]);
        assert!(gain.abs() < 1e-9 && came.abs() < 1e-9);
        // standing still while she walks back into range after a hop: nothing (0.1.x saw the gap shrink: "charging")
        assert_eq!(its_steps((24_000.0, 0.0), at, [(0.0, 0.0), (0.0, 0.0)]), (0.0, 0.0));
    }

    #[test]
    fn the_oath_goes_to_the_support_else_the_nearest() {
        let me = (0.0, 0.0);
        let sup = Mate { player: 4, support: true, at: Some((300_000.0, 0.0)) };
        let near = Mate { player: 1, support: false, at: Some((10_000.0, 0.0)) };
        let dead = Mate { player: 2, support: false, at: None };
        assert_eq!(pick_oath(me, &[near, sup, dead]), Some(4));
        assert_eq!(pick_oath(me, &[near, dead]), Some(1));
        assert_eq!(pick_oath(me, &[dead]), None);
        // a dead support is still the Oathsworn (bound for the game)
        let sup_dead = Mate { at: None, ..sup };
        assert_eq!(pick_oath(me, &[near, sup_dead]), Some(4));
    }

    #[test]
    fn fates_call_takes_the_oathsworn_or_nobody() {
        // 11-03 night logs: Leona bound, the AI's R hurled Aurelion Sol and Nunu (0.2.0 kept the AI's ally then)
        let r_bind = Params::default().r_bind as f64;
        let leona = |d: f64| Sworn { id: Some(22), targetable: true, d, bodies: 20_000.0 };
        assert_eq!(fate_target(Some(leona(40_000.0)), r_bind), Ok(22));
        // the reach counts both bodies, as the engine and the AI measure a cast
        assert_eq!(fate_target(Some(leona(85_000.0)), r_bind), Ok(22));
        assert!(fate_target(Some(leona(95_000.0)), r_bind).is_err(), "out of reach: held, not another ally");
        assert!(fate_target(Some(Sworn { targetable: false, ..leona(10_000.0) }), r_bind).is_err(), "untargetable");
        // the support bound for the game and dead (pick_oath keeps her): held
        assert!(fate_target(Some(Sworn { id: None, targetable: false, d: f64::MAX, bodies: 10_000.0 }), r_bind).is_err());
        assert!(fate_target(None, r_bind).is_err(), "no teammate at all");
    }

    #[test]
    fn a_held_r_is_one_line_a_burst() {
        let mut ai = FateAi::default();
        assert!(ai.burst("fate_held", 9000));
        assert!((9004..9030).step_by(4).all(|t| !ai.burst("fate_held", t)), "the AI presses again every 4 ticks");
        assert!(ai.burst("fate_held", 9031 + ORDER_FRESH), "the next one");
        assert!(new_burst(Some(9000), 100), "another match");
    }

    #[test]
    fn the_flight_lands_on_the_nearest_and_stops_inside_the_catch() {
        let p = Params::default();
        let me = (0.0, 0.0);
        let far = foe(1, (150_000.0, 0.0), 10);
        let near = foe(2, (60_000.0, 0.0), 90);
        assert_eq!(landing_pick(me, &[far, near], &p), Some(near));
        assert_eq!(landing_pick(me, &[far], &p), Some(far)); // only within 2 x r_range
        assert_eq!(landing_pick(me, &[foe(3, (400_000.0, 0.0), 10)], &p), None);
        let mut at = (0.0, 0.0);
        let mut steps = 0;
        loop {
            let (next, arrived) = fly_step(at, near.at, p.r_fly_v as f64, p.r_catch as f64);
            at = next;
            steps += 1;
            if arrived {
                break;
            }
            assert!(steps < 40);
        }
        assert!(dist(at, near.at) <= p.r_catch as f64);
        assert!(dist(at, near.at) >= p.r_catch as f64 * 0.4, "flew into the target: {at:?}");
        assert_eq!(steps, 11);
    }

    #[test]
    fn rend_kills_when_the_spears_are_enough() {
        let p = Params::default();
        // 4 spears, 200 attack: 4 x (20 + 100) = 480, armour 50: 320
        assert_eq!(rend_damage(4, 200, 50, &p), 320);
        assert_eq!(rend_damage(0, 200, 50, &p), 0);
    }

    #[test]
    fn rend_picks_by_id_in_every_run() {
        // 11-06's audit: the spears went through a HashMap (each simulation's own random order) and the first killable
        // one in that order was ripped - two champions both killable got another rip in each run of the match
        let spears = BTreeMap::from([(41, vec![1, 2, 3]), (7, vec![1]), (19, vec![1, 2, 3, 4])]);
        // (damage, hp): #7 lives (100 < 300), #19 and #41 both die
        let rend = |id: usize, n: usize| Some((n * 100, if id == 7 { 300 } else { 250 }));
        assert_eq!(rend_target(&spears, rend), Some((19, 4, 400, 250)));
        // one Rend may not kill (dead, banished, undying): the next by id
        assert_eq!(rend_target(&spears, |id, n| (id != 19).then_some((n * 100, 250))), Some((41, 3, 300, 250)));
        assert_eq!(rend_target(&spears, |_, _| None), None);
    }

    #[test]
    fn a_passive_guard_does_not_make_him_unkillable() {
        // 11-05 review: Karthus / Sion / Anivia / Zac / Zaahen / Krug keep a permanent *_p_guard / *_rv_guard; League
        // counts an execute on them as a kill (they die into the passive)
        for g in ["league_karthus_p_guard", "league_sion_p_guard", "league_anivia_p_guard", "league_zac_p_guard",
                  "league_zaahen_rv_guard", "tft_krug_p_guard"] {
            assert!(!holds_execute(g, true), "{g}");
        }
        assert!(holds_execute("league_kindred_r_on", true));
        assert!(holds_execute("league_zilean_r_rune", true));
        assert!(holds_execute("league_karthus_p_spirit", true));
        assert!(!holds_execute("league_kindred_r_on", false));
    }
}
