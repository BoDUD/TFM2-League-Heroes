//! 奎因附加包（用户 2026-10-19：大招主包冲刺 + 附加包换形态）。主包保持纯数据；`mod.override_info` 把主包的奎因换成 `override/`
//! 里的副本（`make_override.py` 用 tools/kit/build_quinn.py 的 `native=1` 生成：被动换成本包的 `league_quinn:ride`，大招只叫来华洛
//! 骑上、挂 `league_quinn_r_ride`（`R_RIDE_T` tick，移速 +`r_ride_ms`%），骑着时普攻、技能 1、技能 2 先施放鹰翼天翔，大招的说明开头加
//! 【扩展包】），本包补数据做不到的三件事：
//!
//! - **骑行到时自动落地**：英雄联盟里她骑着华洛一直跑，直到出招或骑行结束才施放鹰翼天翔；数据在 buff 到期时什么也做不了。本包每 tick
//!   看她身上的 `r_ride`：骑了 `R_RIDE_T - 2` tick 还没出招，就挂 2 tick 的 `league_quinn_r_end`，副本里骑上时起的每 tick 守望看到就
//!   施放鹰翼天翔（伤害、标记、华洛回到头顶、落地动作，和出招时一样）。
//! - **旋翔掠杀踢完翻回去**（用户 2026-10-22：「奎因E完人不会拉开距离」）：冲刺停在目标身上、和它重合，数据的 MoveBack「背离目标」没有
//!   方向、挪 0（经典引擎模拟里量的）。副本踢中时挂 `league_quinn_e_vault`，本包把她往冲过来的方向翻回去 `E_BACK` x `E_BACK_T`
//!   （2400 x 20 = 48000，约一个攻击距离），被控就停。0.3.0（用户 2026-10-23：「奎因的E后空翻不拉开距离」）：0.2.0 装进游戏后
//!   所有对局（预演和画面）一次 VAULT 都没有——冲刺 end_effects 里挂的标记本包从来没看到。现在副本出 E 时就挂
//!   `league_quinn_e_dash`（`DASH_T` tick，和 `r_ride` 一样挂在动作里，本包看得到），本包看着她冲：冲起来（一 tick 挪 `DASH_STEP`
//!   以上）后停下的那一 tick，或者 `STILL_T` tick 都没冲（贴身踢）就翻；踢中的标记要是看到了也照样翻，一次 E 只翻一次。
//!   0.7.2（用户 2026-11-21：「我看局内是不会后空翻的」）：以前逐 tick 直接改坐标（`entity_set_pos`），画面不跟——11-21 那局
//!   的日志里她在画面上整个后空翻都钉在踢中的地方，翻完才一下被拉到落点。现在踢中时给她一段强制位移（`CcKindV1::ForceMove`，
//!   宿主每 tick 挪她，画面上是连着退的），宿主哪一 tick 没挪（被挡、被缩短）本包才自己走一步。
//! - **后空翻一帧一帧画**（0.7.0 / 0.7.2，`view.rs`）：踢中后本包每 tick 给她挂这一帧的标记 `league_quinn_flip<k>`，画面钩子把
//!   正在播的动画换成单帧标签 `e_flip_<k>`。0.7.1 让数据挂过标记，被踢的单位一死就挂不全（同上），0.7.2 改回本包挂；数据的
//!   踢中效果没跑时 `e_flip` 也由本包补。
//! - **什么时候骑**（0.4.0，`ride_ai.rs`）：游戏的 AI 从来不按这一招，钩子照英雄联盟高手的用法替它按——走远路（回线、游走、
//!   支援）且不在交战中就骑，远处有残血、她血量健康就骑过去追。
//! - **骑乘的样子**（`view.rs`，游戏 0.6.4 起的 Windows 版）：骑着的时候站着、走着、挨打都是骑在华洛背上的 `r_idle` / `r_run` / `r_hit`。
//! - **两张 5v5 地图**（2026-11-10）：翻回去夹在这一场的地图里（`game_places::terrain::map_of_sim`：游戏自己的 960000 见方，
//!   Rin 的召唤师峡谷 1614545 见方）；以前一律按 960000，峡谷上过了 960000 就被夹回半张图的边。峡谷上翻的每一步还要落在
//!   能站的地方（`game_places::terrain::stand_ok`：峡谷的墙往外长一格，和作者的寻路一致）：下一步站不住就翻到这里为止，
//!   停在上一个能站的地方，从不挪进墙里（用户 2026-11-10：「有的地方会走路卡住」）。没有墙体文件时只有地图边。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_quinn.log`，每次启动游戏重写，上一次的留在 .prev.log：`RIDE`（骑上、
//! 出招落地 / 到时落地、骑了多久多远）、`E`（出 E、冲了几 tick）、`VAULT`（为什么翻、往哪翻、给了多长的强制位移、挪了多远、自己走了
//! 几步）、`FLIP`（逐帧标记挂完没有；画面那边画了哪几帧、她在画面上走过的位置）、`FORM`（画面里换形态），
//! 都限了条数。

use std::collections::{HashMap, VecDeque};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{map_of_sim, rift_status, stand_ok, Map};
use mod_api_stable::*;

pub mod ride_ai;
pub mod view;

const ID: &str = "league_quinn";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_quinn") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 骑乘（副本的大招挂的）：view.rs 照它换画面；到时落地的信号（本包挂 2 tick，副本的守望看到就施放鹰翼天翔）。
pub const RIDE: &str = "league_quinn_r_ride";
pub const END: &str = "league_quinn_r_end";
/// 骑多久（build_quinn.P 的 r_ride_t，make_override.py 核对）。
pub const R_RIDE_T: usize = 360;
/// 提前几 tick 挂落地信号：守望每 tick 看一次，骑乘 buff 在最后一 tick 还在。
pub const END_LEAD: usize = 2;
/// 旋翔掠杀踢中时副本挂的信号：本包把她往冲过来的方向翻回去（冲刺停在目标身上、和目标重合，数据的 MoveBack 没有方向、挪 0）。
pub const VAULT: &str = "league_quinn_e_vault";
/// 每 tick 挪多远、挪几 tick（build_quinn.P 的 e_back / e_back_t，单元测试核对）。
pub const E_BACK: f64 = 2400.0;
pub const E_BACK_T: usize = 20;
/// 出 E 时副本挂的标记和它的时长（build_quinn.P 的 e_dash_t，单元测试核对）：本包看着这段时间里的冲刺。
pub const DASH: &str = "league_quinn_e_dash";
pub const DASH_T: usize = 40;
/// 一 tick 挪了这么多以上就是在冲（e_speed 4000），冲起来以后少于它就是停下了（踢中）。
pub const DASH_STEP: f64 = 2000.0;
/// 出 E 后这么多 tick 都没冲起来（贴身踢，冲刺不到一 tick）也翻。
pub const STILL_T: usize = 10;
/// 记最近几 tick 的位置（冲刺前站在哪：E 的冲刺最多 e_range + 40000 / e_speed 4000 = 25 tick）。
pub const TRAIL: usize = 40;
/// 离踢中的地方至少这么远的旧位置才算「从那边冲过来」。
pub const CAME_MIN: f64 = 3000.0;
/// 游戏自己的 5v5 地图边长；峡谷的看 `Map::extent`。
const MAP: f64 = 960_000.0;
/// 后空翻每帧多少毫秒（tools/art/rig_quinn.py 的 MS["e_flip"]，单元测试核对），合计 600 毫秒 = 技能数据的 e_flip 36 tick。
pub const FLIP_MS: [usize; 7] = [60, 70, 80, 70, 70, 120, 130];
/// 正在翻第几帧：踢中后本包每 tick 给她挂 `league_quinn_flip<k>`，view.rs 看到就把画面上正在播的动画换成单帧标签
/// `e_flip_<k>`。0.7.1 改由数据挂过：被踢的单位一死，游戏就跳过它身上的 AddCasterBuff（延时的也一样），11-21 那局画面上
/// 13 次里 7 次只挂上第 0 帧，所以 0.7.2 改回本包自己挂（不管目标死活）。
pub const FLIP: &str = "league_quinn_flip";
/// 翻回去那段强制位移给出去以后最多再等几 tick：给的那一 tick 宿主还没开始挪；宿主没挪满（被挡、被缩短）时本包自己补。
pub const VAULT_SLACK: usize = 4;
/// 离落点这么近就算到了。
pub const ARRIVE: f64 = 1500.0;
/// 游戏自己播的后空翻（技能数据踢中时的 CasterAnimation）；冲刺没碰到目标、数据没播时本包补上。
pub const FLIP_ANIM: &str = "e_flip";
/// 一秒几 tick。
const TPS: usize = 60;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_QUINN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_quinn.log");
        }
    }
    PathBuf::from("league_quinn.log")
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
    counted_on(kind, false)
}

/// 同上，`shown`：这一行出自你看的那场（画面、观战、回放），每条都记（0.6.0）。以前整次启动每种行只记前 `LOG_FIRST` 条，
/// 后台预演先把它用完，11-19 你看的那场骑没骑、为什么，日志里一行都没有。
pub(crate) fn counted_on(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// 这一场在屏幕上（你看的、观战、回放），不是服务器的后台预演。
pub(crate) fn on_screen(sim: &StableSim<'_>) -> bool {
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

/// 这次启动已经在日志里说过峡谷了。
static RIFT_TOLD: AtomicBool = AtomicBool::new(false);

/// 这一场的地图；第一次碰到峡谷（一次启动）时日志写一行。
fn map_here(sim: &StableSim<'_>) -> Map {
    let map = map_of_sim(sim);
    if map == Map::Rift && !RIFT_TOLD.swap(true, Ordering::Relaxed) {
        wlog(format!("== Rift: the vault back after Harrier's kick is kept on the Rift's {:.0} square (not the game's own \
                      {MAP:.0}) and stops at the last spot off the Rift's walls (stand_ok); {} ==", map.extent(),
                     rift_status()));
    }
    map
}

// ===================== 规则（单元测试用） =====================

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 翻回去的方向（单位向量）：从踢中的地方指向冲刺前站的地方——`trail` 里（旧的在前）离 `at` 至少 CAME_MIN 的最近一个，
/// 也就是冲刺开始前那一 tick；都太近（贴身踢的）就背离最近的、不和她重合的敌人 `foe`；都没有就不翻（None）。
pub fn vault_dir(at: Pt, trail: &[Pt], foe: Option<Pt>) -> Option<Pt> {
    let unit = |to: Pt| {
        let (dx, dy) = (to.0 - at.0, to.1 - at.1);
        let l = (dx * dx + dy * dy).sqrt();
        (l >= 1.0).then(|| (dx / l, dy / l))
    };
    let came = trail.iter().rev().find(|p| dist(**p, at) >= CAME_MIN).copied();
    came.and_then(unit).or_else(|| foe.and_then(|f| unit(f).map(|d| (-d.0, -d.1))))
}

/// 夹在 `map` 上（坐标 0..边长-1）。
pub fn clamp(map: Map, p: Pt) -> Pt {
    let e = map.extent();
    (p.0.clamp(0.0, e - 1.0), p.1.clamp(0.0, e - 1.0))
}

/// 翻回去的一步：从 `at` 朝 `d` 挪 E_BACK，夹在 `map` 上；落点站不住（`ok` 说不行：运行时是 `stand_ok`，峡谷的墙往外长一格；
/// 游戏自己的地图上总是行）就不挪（None：翻到这里为止，她停在上一个能站的地方）。
pub fn vault_step(map: Map, at: Pt, d: Pt, ok: impl Fn(Pt) -> bool) -> Option<Pt> {
    let next = clamp(map, (at.0 + d.0 * E_BACK, at.1 + d.1 * E_BACK));
    ok(next).then_some(next)
}

/// 翻回去的落点：从踢中的地方朝 `d` 一步 E_BACK 地退，最多 E_BACK_T 步，每一步夹在 `map` 上；哪一步站不住（`ok`：运行时是
/// `stand_ok`，峡谷的墙往外长一格；游戏自己的地图上总是行）就停在上一步，不进墙。
pub fn vault_to(map: Map, at: Pt, d: Pt, ok: impl Fn(Pt) -> bool) -> Pt {
    let mut p = at;
    for _ in 0..E_BACK_T {
        match vault_step(map, p, d, &ok) {
            Some(next) => p = next,
            None => break,
        }
    }
    p
}

/// 从 `from` 到 `to` 的强制位移 (dx, dy, 每 tick 多远, 几 tick)：每 tick 一样长、不超过 E_BACK，走满正好到；不到 1 就不挪。
pub fn vault_push(from: Pt, to: Pt) -> Option<(i64, i64, u64, u64)> {
    let d = dist(from, to);
    if d < 1.0 {
        return None;
    }
    let ticks = (d / E_BACK).ceil().max(1.0);
    Some(((to.0 - from.0).round() as i64, (to.1 - from.1).round() as i64, (d / ticks).ceil() as u64, ticks as u64))
}

/// 这一 tick 本包要不要自己走一步：上一 tick 记下的位置 `last` 和现在一样（宿主没挪她）。给强制位移的那一 tick 还没有
/// `last`，不算。
pub fn stalled(last: Option<Pt>, at: Pt) -> bool {
    last.is_some_and(|l| dist(l, at) < 1.0)
}

/// 自己走的一步：从 `at` 朝 `to` 最多 E_BACK。
pub fn own_step(at: Pt, to: Pt) -> Pt {
    let off = dist(at, to);
    if off <= E_BACK {
        return to;
    }
    (at.0 + (to.0 - at.0) / off * E_BACK, at.1 + (to.1 - at.1) / off * E_BACK)
}

/// 出 E 后第 `ticks` tick、这一 tick 挪了 `step`、之前冲起来过没有（`moved`）：冲刺是不是结束了（该翻了）。
pub fn dash_over(ticks: usize, moved: bool, step: f64) -> bool {
    if moved { step < DASH_STEP } else { ticks >= STILL_T }
}

/// 踢中后第 `t` tick（踢中那一 tick 是 0）该画后空翻的第几帧；翻完了是 None。
pub fn flip_frame(t: usize) -> Option<usize> {
    let ms = t * 1000 / TPS;
    let mut end = 0;
    FLIP_MS.iter().position(|d| {
        end += d;
        ms < end
    })
}

/// 后空翻一共几 tick（技能数据的 e_flip）。
pub fn flip_ticks() -> usize {
    FLIP_MS.iter().sum::<usize>() * TPS / 1000
}

/// 第 `k` 帧的标记名（view.rs 认它）。
pub fn flip_buff(k: usize) -> String {
    format!("{FLIP}{k}")
}

/// 骑了 `age` tick（骑上那一 tick 是 0）时要不要挂落地信号：只在 R_RIDE_T - END_LEAD 那一 tick。
pub fn time_to_land(age: usize) -> bool {
    age + END_LEAD == R_RIDE_T
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| &b.name_buf[..b.name_len.min(BUFF_NAME_CAP)] == name.as_bytes()))
}

// ===================== 被动：骑乘的计时 =====================

#[derive(Clone, Default)]
struct Ride {
    /// 这一次骑乘骑了几 tick（没在骑是 None）。
    riding: Option<usize>,
    /// 骑上时的位置（日志里记骑了多远）。
    from: Option<Pt>,
    /// 这一次已经挂过落地信号。
    ended: bool,
    /// 最近 TRAIL tick 的位置（旧的在前）：旋翔掠杀从哪边冲过来。
    trail: VecDeque<Pt>,
    /// 正在翻回去。
    vault: Option<Vault>,
    /// 出 E 的标记在她身上时：看到它几 tick、冲起来过没有、这次 E 翻过没有（标记没了才清掉，一次 E 只翻一次）。
    dash: Option<(usize, bool, bool)>,
    /// 后空翻的画面：踢中后第几 tick、现在挂着第几帧的标记。
    flip: Option<(usize, Option<usize>)>,
}

/// 翻回去的一程：落点、起点、还能用几 tick、上一 tick 的位置（看宿主挪没挪）、本包自己走了几步。
#[derive(Clone, Copy)]
struct Vault {
    to: Pt,
    from: Pt,
    left: usize,
    last: Option<Pt>,
    own: usize,
}

/// 她身上的控制（种类、还剩几 tick；强制动作带名字，强制位移带速度），日志用。
fn ccs_on(sim: &StableSim<'_>, id: usize) -> String {
    let Some(e) = sim.get_entity(id) else { return String::new() };
    let v: Vec<String> = (0..e.cc_count())
        .filter_map(|i| e.cc_at(i))
        .map(|c| match CcKindV1::from_code(c.kind) {
            Some(CcKindV1::Animation) => format!("anim {} {}", c.name(), c.tick),
            Some(CcKindV1::ForceMove) => format!("move {}x{}", c.tick, c.speed),
            Some(k) => format!("{k:?} {}", c.tick),
            None => format!("cc{} {}", c.kind, c.tick),
        })
        .collect();
    if v.is_empty() { "none".to_string() } else { v.join(", ") }
}

fn has_cc(sim: &StableSim<'_>, id: usize, kind: CcKindV1, name: Option<&str>) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| c.kind == kind.code() && name.is_none_or(|n| c.name() == n)))
    })
}

/// 控住她的（翻到一半被控就停）。
const HARD_CC: [CcKindV1; 6] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];

fn hard_cc(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
    })
}

/// 离 `at` 最近、不和她重合的敌人（英雄、小兵、野怪都算：踢的可能是它们）。
fn nearest_foe(sim: &StableSim<'_>, me: usize, at: Pt) -> Option<Pt> {
    let team = sim.get_entity(me)?.team();
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive())
        .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
        .filter(|p| dist(*p, at) >= 1.0)
        .min_by(|a, b| dist(*a, at).total_cmp(&dist(*b, at)))
}

impl Ride {
    /// 旋翔掠杀：出 E 的标记 DASH 在时看着她冲，冲刺停下（或踢中的标记 VAULT 来了）就把她往冲过来的方向翻回去 E_BACK x
    /// E_BACK_T：给她一段强制位移（宿主挪她，画面跟着走），宿主没挪的 tick 本包自己走一步。
    fn vault(&mut self, sim: &mut StableSim<'_>, me: usize, at: Pt) {
        let step = self.trail.back().map_or(0.0, |p| dist(*p, at));
        let kicked = has_buff(sim, me, VAULT);
        if kicked {
            sim.entity_remove_buff(me, VAULT);
        }
        let mut why = kicked.then_some("the kick's flag");
        if has_buff(sim, me, DASH) {
            let (ticks, moved, done) = self.dash.get_or_insert((0, false, false));
            if *ticks == 0 {
                if let Some(k) = counted("e") {
                    wlog(format!("{} E cast, watching the dash #{k}", head(sim, me)));
                }
            }
            *ticks += 1;
            *moved |= step >= DASH_STEP;
            if *done {
                why = None;
            } else if why.is_none() && dash_over(*ticks, *moved, step) {
                why = Some(if *moved { "the dash stopped" } else { "no dash (point blank)" });
            }
            if why.is_some() {
                *done = true;
                if let Some(k) = counted("e_ticks") {
                    wlog(format!("{} E {} ticks after the cast, last step {step:.0} #{k}", head(sim, me), *ticks));
                }
            }
        } else {
            self.dash = None;
        }
        if let (Some(why), true) = (why, self.vault.is_none()) {
            let shown = on_screen(sim);
            let before = ccs_on(sim, me);
            // 后空翻的画面从这一 tick 起逐帧走（找不到方向、原地翻也一样翻）
            self.flip = Some((0, self.flip.and_then(|f| f.1)));
            // 冲刺没碰到目标（目标先死了、冲刺被打断）时数据的踢中效果没跑，她身上没有 e_flip：本包补上，翻完之前也不走动
            if !has_cc(sim, me, CcKindV1::Animation, Some(FLIP_ANIM)) {
                let mut a = CcV1::of_kind(CcKindV1::Animation, flip_ticks() as u64);
                a.set_name(FLIP_ANIM);
                sim.apply_cc(me, &a);
            }
            let trail: Vec<Pt> = self.trail.iter().copied().collect();
            match vault_dir(at, &trail, nearest_foe(sim, me, at)) {
                Some(d) => {
                    // 峡谷上落点停在墙前（stand_ok），强制位移只走到那里；游戏自己的地图上就是退满 E_BACK x E_BACK_T
                    let map = map_here(sim);
                    let to = vault_to(map, at, d, |q| stand_ok(map, q));
                    // 强制位移：宿主每 tick 挪她一段，画面上是连着的一段位移。以前逐 tick 直接改坐标，画面不跟：11-21 那局
                    // 13 次里 11 次她在画面上整个后空翻都钉在原地，翻完才一下被拉到落点（「往后拉距离…没动画」）
                    let push = vault_push(at, to);
                    if let Some((dx, dy, speed, ticks)) = push {
                        let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks);
                        mv.dx = dx;
                        mv.dy = dy;
                        mv.speed = speed;
                        sim.apply_cc(me, &mv);
                    }
                    self.vault = Some(Vault { to, from: at, left: E_BACK_T + VAULT_SLACK, last: None, own: 0 });
                    if let Some(k) = counted_on("vault", shown) {
                        let came = trail.iter().rev().find(|p| dist(**p, at) >= CAME_MIN).is_some();
                        wlog(format!("{} VAULT ({why}) flip back ({:.2}, {:.2}){}: forced move {} over {:.0}; on her before: {before}; \
                                      now: {} #{k}", head(sim, me), d.0, d.1,
                                     if came { ", the way she dashed in" } else { ", away from the nearest enemy" },
                                     push.map_or("none".to_string(), |(_, _, sp, t)| format!("{t} ticks x {sp}")), dist(at, to),
                                     ccs_on(sim, me)));
                    }
                }
                None => {
                    if let Some(k) = counted_on("vault", shown) {
                        wlog(format!("{} VAULT ({why}) no way to tell where to flip, flips on the spot; on her: {} #{k}",
                                     head(sim, me), ccs_on(sim, me)));
                    }
                }
            }
        }
        if let Some(v) = self.vault.as_mut() {
            let held = hard_cc(sim, me);
            let off = dist(at, v.to);
            if held || off <= ARRIVE || v.left == 0 {
                let (from, to, own, left) = (v.from, v.to, v.own, v.left);
                self.vault = None;
                if let Some(k) = counted_on("vault_done", on_screen(sim)) {
                    let why = if held { ", cut by CC" } else if off > ARRIVE { ", out of time" } else { "" };
                    wlog(format!("{} VAULT DONE moved {:.0} of {:.0} in {} ticks ({own} steps of her own{why}) #{k}",
                                 head(sim, me), dist(from, at), dist(from, to), E_BACK_T + VAULT_SLACK - left));
                }
            } else {
                // 宿主这一 tick 没挪她（强制位移被挡住、被缩短）：自己走一步，位置是对的，这一步画面上不显示
                if stalled(v.last, at) {
                    let next = own_step(at, v.to);
                    sim.entity_set_pos(me, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64);
                    v.own += 1;
                    v.last = Some(next);
                } else {
                    v.last = Some(at);
                }
                v.left -= 1;
            }
        }
    }

    /// 后空翻的画面（踢中后 FLIP_MS 那 600 毫秒）：每 tick 给她挂这一帧的标记 `league_quinn_flip<k>`，view.rs 照它换画面；
    /// 翻完、被控就摘掉。标记只挂 2 tick、每 tick 重挂：本包哪一 tick 没跑到，画面也会自己回到游戏播的动作。
    fn flip(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some((t, shown)) = self.flip else { return };
        let held = hard_cc(sim, me);
        let k = if held { None } else { flip_frame(t) };
        if let Some(old) = shown.filter(|&o| Some(o) != k) {
            sim.entity_remove_buff(me, &flip_buff(old));
        }
        match k {
            Some(k) => {
                let name = flip_buff(k);
                sim.entity_remove_buff(me, &name);
                sim.add_buff(me, &BuffV1::timed(&name, 2));
                self.flip = Some((t + 1, Some(k)));
            }
            None => {
                if let Some(n) = counted_on("flip_done", on_screen(sim)) {
                    wlog(format!("{} FLIP over after {t} ticks{}; on her: {} #{n}", head(sim, me),
                                 if held { ", cut by CC" } else { "" }, ccs_on(sim, me)));
                }
                self.flip = None;
            }
        }
    }
}

impl StablePassive for Ride {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        *self = Ride::default();
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        match pos(sim, me).filter(|_| alive) {
            Some(at) => {
                self.vault(sim, me, at);
                self.flip(sim, me);
                self.trail.push_back(at);
                if self.trail.len() > TRAIL {
                    self.trail.pop_front();
                }
            }
            None => {
                self.trail.clear();
                self.vault = None;
                self.dash = None;
                self.flip = None;
            }
        }
        let riding = alive && has_buff(sim, me, RIDE);
        if !riding {
            if let Some(t) = self.riding.take() {
                if let Some(k) = counted_on("ride", on_screen(sim)) {
                    let far = match (self.from, pos(sim, me)) {
                        (Some(a), Some(b)) => dist(a, b),
                        _ => 0.0,
                    };
                    let how = if !alive { "she died" } else if self.ended { "the ride ran out: Skystrike" } else {
                        "Skystrike on an attack or a cast" };
                    wlog(format!("{} RIDE over after {t} ticks, {far:.0} ridden ({how}) #{k}", head(sim, me)));
                }
            }
            self.ended = false;
            return;
        }
        let age = match self.riding {
            None => {
                self.from = pos(sim, me);
                self.ended = false;
                if let Some(k) = counted_on("ride", on_screen(sim)) {
                    wlog(format!("{} RIDE mounted Valor #{k}", head(sim, me)));
                }
                0
            }
            Some(t) => t + 1,
        };
        self.riding = Some(age);
        if !self.ended && time_to_land(age) {
            sim.add_buff(me, &BuffV1::timed(END, END_LEAD));
            self.ended = true;
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
        "=== {ID} v{VERSION} (Quinn: League's ride on Valor, ridden out to her lane, to allies in a fight, to roam and to chase, Skystrike when it runs out, the riding body) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:ride"), Ride::default());
    module.add_player_input_ai(ride_ai::RideAi::default());
    host.log(LogLevel::Info, "league_quinn loaded (the ride on Valor, pressed to lane, to allies, to roam and to chase, Skystrike, the riding body).");
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
    use game_places::terrain::Walls;

    #[test]
    fn the_landing_signal_comes_once_before_the_ride_runs_out() {
        assert!(!time_to_land(0));
        assert!(time_to_land(R_RIDE_T - END_LEAD));
        assert_eq!((0..R_RIDE_T * 2).filter(|&t| time_to_land(t)).count(), 1);
    }

    #[test]
    fn the_vault_goes_back_the_way_she_dashed_in() {
        // dashed in from the left, 4000 a tick, onto the target at (100000, 50000)
        let trail: Vec<Pt> = (0..10).map(|k| (60000.0 + 4000.0 * k as f64, 50000.0)).collect();
        let d = vault_dir((100000.0, 50000.0), &trail, Some((100000.0, 50000.0))).unwrap();
        assert!((d.0 + 1.0).abs() < 1e-9 && d.1.abs() < 1e-9);
        // kicked from point blank: away from the nearest enemy that is not on her spot
        let d = vault_dir((0.0, 0.0), &[(0.0, 0.0)], Some((0.0, 5000.0))).unwrap();
        assert!(d.0.abs() < 1e-9 && (d.1 + 1.0).abs() < 1e-9);
        assert_eq!(vault_dir((0.0, 0.0), &[], None), None);
    }

    #[test]
    fn the_vault_stays_on_the_map_it_is_played_on() {
        // the game's own map: its edge at 960000, as before
        assert_eq!(clamp(Map::Native, (970_000.0, -5.0)), (MAP - 1.0, 0.0));
        // the Rift: past 960000 is its ground, its own edge at 1614545
        assert_eq!(clamp(Map::Rift, (1_300_000.0, 1_500_000.0)), (1_300_000.0, 1_500_000.0));
        assert_eq!(clamp(Map::Rift, (2_000_000.0, -5.0)), (Map::Rift.extent() - 1.0, 0.0));
    }

    /// 2026-11-10 (the user on the Rift: 「有的地方会走路卡住」): the vault moved her step by step into the Rift's walls and
    /// she stood stuck there. A piece of the Rift as `stand_ok` sees it with the walls file (`!is_wall` on `rift_ground`):
    /// cells of 60000/11, 40 x 40 from (1100000, 1100000), columns 20 and 21 wall, grown by one cell (`padded`): no hero
    /// stands at x 1203636..1225455.
    #[test]
    fn on_the_rift_the_vault_stops_at_its_walls() {
        let e = Map::Rift.extent();
        let row = format!("{}##{}", ".".repeat(20), ".".repeat(18));
        let g = Walls::from_rows(&vec![row.as_str(); 40], 60_000.0 / 11.0, (1_100_000.0, 1_100_000.0), (e, e)).padded();
        let ok = |q: Pt| !g.is_wall(q.0, q.1);
        let vault = |map: Map, from: Pt, d: Pt, ok: &dyn Fn(Pt) -> bool| {
            let (mut at, mut steps) = (from, 0);
            while steps < E_BACK_T {
                let Some(next) = vault_step(map, at, d, ok) else { break };
                (at, steps) = (next, steps + 1);
            }
            (at, steps)
        };
        let y = 1_200_000.0;
        assert!(ok((1_150_000.0, y)) && !ok((1_206_000.0, y)), "past 960000 is ground; the wall's cell is not");
        // flipping back toward the wall: 5 of 20 steps of 2400, on her last good spot (the 6th, 1204400, is in the grown wall)
        assert_eq!(vault(Map::Rift, (1_190_000.0, y), (1.0, 0.0), &ok), ((1_202_000.0, y), 5));
        // away from it: the whole vault
        assert_eq!(vault(Map::Rift, (1_190_000.0, y), (-1.0, 0.0), &ok), ((1_142_000.0, y), E_BACK_T));
        // the game's own map: stand_ok never stops her - every step as before
        let native = |q: Pt| stand_ok(Map::Native, q);
        assert_eq!(vault(Map::Native, (500_000.0, 500_000.0), (1.0, 0.0), &native), ((548_000.0, 500_000.0), E_BACK_T));
        assert_eq!(vault_step(Map::Native, (958_000.0, 5.0), (1.0, 0.0), native), Some(clamp(Map::Native, (962_000.0, 5.0))));
    }

    #[test]
    fn she_flips_the_tick_her_dash_stops_or_when_there_was_none() {
        assert!(!dash_over(1, false, 0.0)); // the cast's tick, not moving yet
        assert!(!dash_over(5, true, 4000.0)); // dashing
        assert!(dash_over(6, true, 1500.0)); // the last short step onto the target
        assert!(dash_over(7, true, 0.0)); // standing on it
        assert!(!dash_over(STILL_T - 1, false, 300.0) && dash_over(STILL_T, false, 300.0)); // point blank: no dash
        assert!(STILL_T < DASH_T && 100000 / 4000 < DASH_T, "the flag outlasts the longest dash");
    }

    #[test]
    fn the_vault_numbers_match_the_kit() {
        let src = include_str!("../../../tools/kit/build_quinn.py");
        assert!(src.contains(&format!("\"e_back\": {}", E_BACK as usize)) && src.contains(&format!("\"e_back_t\": {E_BACK_T}")));
        assert!(src.contains(&format!("\"e_dash_t\": {DASH_T}")));
        let s = include_str!("../override/league_quinn.data_champion");
        assert!(s.contains(&format!("\"{VAULT}\"")), "the copy flags no vault");
        assert!(s.contains(&format!("\"{DASH}\"")), "the copy flags no cast");
        assert!(!s.contains("\"MoveBack\""), "the copy still has the data's MoveBack");
    }

    #[test]
    fn the_flip_goes_frame_by_frame_as_the_sheet_times_it() {
        // 踢中那一 tick 是蹬离（第 0 帧），一 tick 1000/60 毫秒：60 毫秒后第 1 帧……600 毫秒（36 tick）翻完
        assert_eq!(flip_frame(0), Some(0));
        assert_eq!(flip_frame(3), Some(0));
        assert_eq!(flip_frame(4), Some(1));
        assert_eq!(flip_frame(8), Some(2));
        assert_eq!(flip_frame(21), Some(5));
        assert_eq!(flip_frame(35), Some(6));
        assert_eq!(flip_frame(36), None);
        let seen: Vec<usize> = (0..36).filter_map(flip_frame).collect();
        assert_eq!(seen.len(), 36);
        assert!(seen.windows(2).all(|w| w[1] == w[0] || w[1] == w[0] + 1), "{seen:?}");
        assert_eq!(*seen.last().unwrap(), FLIP_MS.len() - 1);
        assert_eq!(flip_buff(3), "league_quinn_flip3");
    }

    #[test]
    fn the_flip_timing_matches_the_sheet_and_the_kit() {
        let ms: Vec<String> = FLIP_MS.iter().map(|m| m.to_string()).collect();
        let rig = include_str!("../../../tools/art/rig_quinn.py");
        assert!(rig.contains(&format!("\"e_flip\": [{}]", ms.join(", "))), "rig_quinn.py MS[\"e_flip\"] is not {ms:?}");
        let ticks = FLIP_MS.iter().sum::<usize>() * TPS / 1000;
        let kit = include_str!("../../../tools/kit/build_quinn.py");
        assert!(kit.contains(&format!("\"e_flip\": {ticks}")), "build_quinn.py e_flip is not {ticks} ticks");
        // 踢中时先摘掉冲刺的动作再翻，两份数据都是
        for s in [include_str!("../override/league_quinn.data_champion"),
                  include_str!("../../../league/champion/league_quinn.data_champion")] {
            let at = s.find("\"name\": \"e_flip\"").expect("no e_flip animation");
            let rm = s[..at].rfind("\"RemoveCasterAnimation\"").expect("the dash animation is not taken off");
            assert!(at - rm < 200 && s[rm..at].contains("\"name\": \"skill2\""), "skill2 is not taken off right before the flip");
        }
        // 只挪的那几 tick 里也在翻
        assert!(E_BACK_T < ticks);
    }

    #[test]
    fn the_flip_flags_are_this_crates_not_the_datas() {
        // 0.7.1 让数据挂逐帧标记：被踢的单位一死，游戏跳过它身上的 AddCasterBuff，13 次里 7 次只挂上第 0 帧。两份数据里
        // 都不许再有这个标记，本包每 tick 自己挂（flip）
        for s in [include_str!("../override/league_quinn.data_champion"),
                  include_str!("../../../league/champion/league_quinn.data_champion")] {
            assert!(!s.contains(FLIP), "the data lays flip flags");
        }
        assert_eq!(flip_ticks(), 36);
        let kit = include_str!("../../../tools/kit/build_quinn.py");
        assert!(kit.contains(&format!("\"e_flip\": {}", flip_ticks())));
    }

    #[test]
    fn the_vault_is_one_forced_move_to_where_she_lands() {
        // 落点：朝冲过来的方向退 E_BACK x E_BACK_T，夹在地图里
        let free = |_: Pt| true;
        assert_eq!(vault_to(Map::Native, (500_000.0, 500_000.0), (-1.0, 0.0), free), (452_000.0, 500_000.0));
        assert_eq!(vault_to(Map::Native, (10_000.0, 500_000.0), (-1.0, 0.0), free), (0.0, 500_000.0));
        // 峡谷上第 6 步站不住：停在第 5 步，强制位移只走 5 tick
        let wall = |q: Pt| q.0 > 487_000.0;
        let stop = vault_to(Map::Rift, (500_000.0, 500_000.0), (-1.0, 0.0), wall);
        assert_eq!(stop, (488_000.0, 500_000.0));
        assert_eq!(vault_push((500_000.0, 500_000.0), stop), Some((-12_000, 0, 2400, 5)));
        let (x, y) = vault_to(Map::Native, (500_000.0, 500_000.0), (0.6, 0.8), free);
        assert!((x - 528_800.0).abs() < 1e-6 && (y - 538_400.0).abs() < 1e-6);
        // 强制位移：整段的位移、每 tick 2400、20 tick；贴着地图边只剩一小段时 tick 数跟着少，每 tick 不超过 E_BACK
        assert_eq!(vault_push((500_000.0, 500_000.0), (452_000.0, 500_000.0)), Some((-48_000, 0, 2400, 20)));
        assert_eq!(vault_push((10_000.0, 500_000.0), (0.0, 500_000.0)), Some((-10_000, 0, 2000, 5)));
        assert_eq!(vault_push((0.0, 0.0), (0.4, 0.0)), None);
        let (dx, dy, speed, ticks) = vault_push((500_000.0, 500_000.0), (528_800.0, 538_400.0)).unwrap();
        assert_eq!((dx, dy, ticks), (28_800, 38_400, 20));
        assert!(speed as f64 <= E_BACK && speed * ticks >= 48_000);
    }

    #[test]
    fn she_steps_herself_only_when_the_host_did_not_move_her() {
        let at = (100_000.0, 100_000.0);
        assert!(!stalled(None, at)); // 给强制位移的那一 tick：宿主还没开始挪
        assert!(!stalled(Some((102_400.0, 100_000.0)), at)); // 宿主挪了
        assert!(stalled(Some(at), at)); // 没挪：自己走
        assert_eq!(own_step(at, (90_000.0, 100_000.0)), (97_600.0, 100_000.0));
        assert_eq!(own_step(at, (99_000.0, 100_000.0)), (99_000.0, 100_000.0)); // 不到一步：正好到
        // 一直没人挪她：20 步走完 48000
        let (mut p, to, mut n) = (at, (52_000.0, 100_000.0), 0);
        while dist(p, to) > ARRIVE {
            p = own_step(p, to);
            n += 1;
        }
        assert_eq!(n, 20);
        assert!(E_BACK_T + VAULT_SLACK > n);
    }

    #[test]
    fn the_copy_names_this_crates_passive_and_buffs() {
        let s = include_str!("../override/league_quinn.data_champion");
        assert!(s.contains("\"league_quinn:ride\""));
        assert!(s.contains(&format!("\"{RIDE}\"")) && s.contains(&format!("\"{END}\"")));
        assert!(s.contains(&format!("\"r_ride_t\": {R_RIDE_T}")));
    }

    #[test]
    fn the_match_on_screen_keeps_every_line() {
        // 11-19：后台预演先把每种行的前 40 条用完，你看的那场（m=6778）一行都没有
        let hidden = (0..LOG_EVERY + 10).filter(|_| counted_on("test_hidden", false).is_some()).count();
        assert_eq!(hidden, LOG_FIRST + 1, "the first 40, then one every 200");
        assert!((0..LOG_EVERY + 10).all(|_| counted_on("test_shown", true).is_some()));
    }
}
