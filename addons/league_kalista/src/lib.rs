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
//!   （`league_kalista:fate`）把施放目标换成誓约者（在 `r_bind` 内、能选中时；不然留 AI 自己挑的队友）。
//! - **命运的召唤的飞行**：数据把队友拉进来、保护、定身，甩出时挂 `r_launch`；本包挑落点（离她最近的敌方英雄，`r_range` 内；
//!   没有就 2 倍范围内最近的），逐 tick 把队友朝那个英雄现在的位置飞过去（`r_fly_v`），到 `r_catch` 内挂 `r_landed`，数据在队友脚下
//!   击飞周围敌人。
//! - **撕裂斩杀**：记下她对每个敌方英雄的普攻（每根矛 `sp_t` tick），按 `e_dmg` + `e_ratio`% 攻击力、对方护甲算拔矛伤害，够杀就挂
//!   `e_ok` 让数据立刻拔（数据本来要攒到 `e_need` 根）。数据拔矛（`e_pop`）后计数清零。
//!   Q 击杀后把矛转到下一个目标做不了：矛是数据挂在目标身上的独立实例，原生代码挪不了。
//!   0.1.2（2026-10-26，剑圣无限 Q 时查到：`on_attack` 连技能的每一下伤害都会触发）：一根矛打中时同一 tick 还会有
//!   W 灵魂绑定的追加伤害等，原来每一下都记一根，计数比她身上真实的矛多，估出来的拔矛伤害偏高、打不死就提前拔了 E。
//!   现在同一个目标同一个 tick 只记一根（`add_spear`）；E 拔矛那几下照旧在 `e_pop` 亮着时清掉。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kalista.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `OATH`（绑了谁）、`HOP`（往哪跳、为什么）、`FATE`（拉谁、飞到谁身边、几 tick）、`REND`（斩杀判定），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

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
/// 地图边长（坐标 0..MAP）。
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
/// 先往前；什么都没有就 None，数据照主包往后跳。hop_thr 不再用（第一版：贴近才往后跳）。
pub fn hop_choice(me: Pt, foes: &[Foe], units: &[Foe], turns: Turns, p: &Params) -> Option<(Hop, HopWhy)> {
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
    let ccw = if on_map(hop_end(me, Hop::Side(near, turns.ccw), len)) { turns.ccw } else { !turns.ccw };
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

pub fn on_map(p: Pt) -> bool {
    (0.0..MAP).contains(&p.0) && (0.0..MAP).contains(&p.1)
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

/// 飞行的一步：朝 `to` 走 `v`，到 `catch` 内就算到了（停在原地）。-> (下一步的位置, 到了没有)
pub fn fly_step(at: Pt, to: Pt, v: f64, catch: f64) -> (Pt, bool) {
    let d = dist(at, to);
    if d <= catch {
        return (at, true);
    }
    let go = v.min(d - catch * 0.5);
    let next = (at.0 + (to.0 - at.0) / d * go, at.1 + (to.1 - at.1) / d * go);
    (clamp(next), dist(next, to) <= catch)
}

pub fn clamp(p: Pt) -> Pt {
    (p.0.clamp(0.0, MAP - 1.0), p.1.clamp(0.0, MAP - 1.0))
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

pub fn rend_damage(n: usize, ad: usize, def: usize, p: &Params) -> usize {
    let raw = n * (p.e_dmg + p.e_ratio * ad / 100);
    raw * 100 / (100 + def)
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
    /// 敌方英雄 -> 她每根矛插上的 tick。
    spears: HashMap<usize, Vec<usize>>,
    /// 敌方英雄 -> (取样的 tick, 那时它在哪, 上一段 FLEE_WINDOW 里它自己挪了多少)。
    gaps: HashMap<usize, (usize, Pt, Pt)>,
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
        let choice = hop_choice(at, &fs, &us, self.turns, p);
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
                let next = clamp((at.0 + h.dir.0 * step, at.1 + h.dir.1 * step));
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
                        wlog(format!("{} FATE {} hurled at {} ({:.0} away, {}% hp) #{k}", head(sim, me), who(sim, ally),
                                     who(sim, f.id), dist(at, f.at), f.hp_pct));
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
                    let (next, arrived) = fly_step(a, to, p.r_fly_v as f64, p.r_catch as f64);
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
        if has_buff(sim, me, E_CD) || has_buff(sim, me, E_OK) {
            return;
        }
        let Some(ad) = sim.get_entity(me).map(|e| e.stat().attack) else { return };
        let mut kill = None;
        for (&id, v) in &self.spears {
            let Some(e) = sim.get_entity(id) else { continue };
            // 选不中的、挂着不死的（阿克尚复活前停在 1 血）拔了也杀不死（2026-11-01 复查：对 1 血的阿克尚报了 33 次）
            if !e.is_alive() || !e.is_targetable() || (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.undying) {
                continue;
            }
            let (hp, _) = e.hp();
            let dmg = rend_damage(v.len(), ad, e.stat().defence, p);
            if dmg >= hp {
                kill = Some((id, v.len(), dmg, hp));
                break;
            }
        }
        if let Some((id, n, dmg, hp)) = kill {
            set_flag(sim, me, E_OK, 6);
            set_flag(sim, id, E_AIM, 6);
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
struct FateAi;

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
            return rend_now(ctx, was);
        }
        let b = base?;
        if InputTargetKindV1::from_code(b.target.kind) != Some(InputTargetKindV1::Target) {
            return None;
        }
        let current = b.target.target_id;
        let player = ctx.player_id();
        let p = shared();
        let (pick, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let (mid, team) = (me.id(), me.team());
            let at = (me.pos().0 as f64, me.pos().1 as f64);
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
                let c = champ.filter(|c| c.is_alive() && c.is_targetable());
                mates.push((Mate { player: pl.id(), support: pl.lane() == Some(LaneV1::Support),
                                   at: c.as_ref().map(|c| (c.pos().0 as f64, c.pos().1 as f64)) },
                            c.map(|c| c.id())));
            }
            let list: Vec<Mate> = mates.iter().map(|m| m.0).collect();
            let oath = pick_oath(at, &list)?;
            let (m, id) = mates.iter().find(|m| m.0.player == oath)?;
            let id = (*id)?;
            if dist(at, m.at?) > p.r_bind as f64 {
                return None;
            }
            let line = format!("{} FATE target {} -> the Oathsworn {}", head(&sim, mid), who(&sim, current), who(&sim, id));
            (id, line)
        };
        if pick == current {
            return None;
        }
        let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(pick));
        if !ctx.is_valid_input(&input) {
            if let Some(k) = counted("fate_ai") {
                wlog(format!("{line} refused by the game, the AI's ally kept #{k}"));
            }
            return None;
        }
        if let Some(k) = counted("fate_ai") {
            wlog(format!("{line} #{k}"));
        }
        Some(input)
    }
}

/// 「拔了能杀」（被动在她身上挂 `E_OK`、在那个敌人身上挂 `E_AIM`）时自己按技能 2：数据只在矛打中英雄、或游戏的 AI 按技能 2
/// 的时候看 `e_ok`，游戏的 AI 一两分钟才按一次，「立刻拔」常常等到下一矛（2026-11-01 复查：18 次 rip now 都没拔）。
fn rend_now(ctx: &mut StableAiContext<'_>, was: Option<InputKindV1>) -> Option<InputV1> {
    if was == Some(InputKindV1::Skill2) {
        return None;
    }
    let player = ctx.player_id();
    let (target, line) = {
        let sim = ctx.sim()?;
        let me = sim.get_player(player)?.champion()?;
        let mid = me.id();
        if !me.is_alive() || !has_buff(&sim, mid, E_OK) || has_buff(&sim, mid, E_CD) {
            return None;
        }
        // 技能 2 解锁了（3 级）、试拔的格子好了（引擎的「输入合法」不看冷却和解锁）
        if !me.cooldown(SkillSlotV1::Skill2).is_some_and(|c| c.unlocked && c.remaining == 0) {
            return None;
        }
        let team = me.team();
        let t = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .find(|u| u.team() != team && u.is_alive() && u.is_champion() && has_buff(&sim, u.id(), E_AIM))?
            .id();
        (t, format!("{} REND PRESS: Skill2 on {}", head(&sim, mid), who(&sim, t)))
    };
    let input = InputV1::action(InputKindV1::Skill2, InputTargetV1::target(target));
    if !ctx.is_valid_input(&input) {
        return None;
    }
    if let Some(k) = counted("rend_press") {
        wlog(format!("{line} #{k}"));
    }
    Some(input)
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
    module.add_player_input_ai(FateAi);
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
}
