//! 奎因附加包（用户 2026-10-19：大招主包冲刺 + 附加包换形态）。主包保持纯数据；`mod.override_info` 把主包的奎因换成 `override/`
//! 里的副本（`make_override.py` 用 tools/kit/build_quinn.py 的 `native=1` 生成：被动换成本包的 `league_quinn:ride`，大招只叫来华洛
//! 骑上、挂 `league_quinn_r_ride`（`R_RIDE_T` tick，移速 +`r_ride_ms`%），骑着时普攻、技能 1、技能 2 先施放鹰翼天翔，大招的说明开头加
//! 【扩展包】），本包补数据做不到的三件事：
//!
//! - **骑行到时自动落地**：英雄联盟里她骑着华洛一直跑，直到出招或骑行结束才施放鹰翼天翔；数据在 buff 到期时什么也做不了。本包每 tick
//!   看她身上的 `r_ride`：骑了 `R_RIDE_T - 2` tick 还没出招，就挂 2 tick 的 `league_quinn_r_end`，副本里骑上时起的每 tick 守望看到就
//!   施放鹰翼天翔（伤害、标记、华洛回到头顶、落地动作，和出招时一样）。
//! - **旋翔掠杀踢完翻回去**（用户 2026-10-22：「奎因E完人不会拉开距离」）：冲刺停在目标身上、和它重合，数据的 MoveBack「背离目标」没有
//!   方向、挪 0（经典引擎模拟里量的）。副本踢中时挂 `league_quinn_e_vault`，本包逐 tick 把她往冲过来的方向挪 `E_BACK`，共
//!   `E_BACK_T` tick（4000 x 12 = 48000，约一个攻击距离），被控就停。0.3.0（用户 2026-10-23：「奎因的E后空翻不拉开距离」）：
//!   0.2.0 装进游戏后所有对局（预演和画面）一次 VAULT 都没有——冲刺 end_effects 里挂的标记本包从来没看到。现在副本出 E 时就挂
//!   `league_quinn_e_dash`（`DASH_T` tick，和 `r_ride` 一样挂在动作里，本包看得到），本包看着她冲：冲起来（一 tick 挪 `DASH_STEP`
//!   以上）后停下的那一 tick，或者 `STILL_T` tick 都没冲（贴身踢）就翻；踢中的标记要是看到了也照样翻，一次 E 只翻一次。
//! - **骑乘的样子**（`view.rs`，游戏 0.6.4 起的 Windows 版）：骑着的时候站着、走着、挨打都是骑在华洛背上的 `r_idle` / `r_run` / `r_hit`。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_quinn.log`，每次启动游戏重写，上一次的留在 .prev.log：`RIDE`（骑上、
//! 出招落地 / 到时落地、骑了多久多远）、`E`（出 E、冲了几 tick）、`VAULT`（为什么翻、往哪翻、挪了多远）、`FORM`（画面里换形态），
//! 都限了条数。

use std::collections::{HashMap, VecDeque};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

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
pub const E_BACK: f64 = 4000.0;
pub const E_BACK_T: usize = 12;
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
const MAP: f64 = 960_000.0;

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

pub fn clamp(p: Pt) -> Pt {
    (p.0.clamp(0.0, MAP - 1.0), p.1.clamp(0.0, MAP - 1.0))
}

/// 出 E 后第 `ticks` tick、这一 tick 挪了 `step`、之前冲起来过没有（`moved`）：冲刺是不是结束了（该翻了）。
pub fn dash_over(ticks: usize, moved: bool, step: f64) -> bool {
    if moved { step < DASH_STEP } else { ticks >= STILL_T }
}

/// 骑了 `age` tick（骑上那一 tick 是 0）时要不要挂落地信号：只在 R_RIDE_T - END_LEAD 那一 tick。
pub fn time_to_land(age: usize) -> bool {
    age + END_LEAD == R_RIDE_T
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
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
    /// 正在翻回去：方向、还剩几 tick、起点、游戏拒绝挪人的次数。
    vault: Option<(Pt, usize, Pt, usize)>,
    /// 出 E 的标记在她身上时：看到它几 tick、冲起来过没有、这次 E 翻过没有（标记没了才清掉，一次 E 只翻一次）。
    dash: Option<(usize, bool, bool)>,
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
    /// 旋翔掠杀：出 E 的标记 DASH 在时看着她冲，冲刺停下（或踢中的标记 VAULT 来了）就逐 tick 把她往冲过来的方向挪 E_BACK，
    /// 共 E_BACK_T tick。
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
        if let (Some(why), None) = (why, self.vault) {
            let trail: Vec<Pt> = self.trail.iter().copied().collect();
            match vault_dir(at, &trail, nearest_foe(sim, me, at)) {
                Some(d) => {
                    self.vault = Some((d, E_BACK_T, at, 0));
                    if let Some(k) = counted("vault") {
                        let came = trail.iter().rev().find(|p| dist(**p, at) >= CAME_MIN).is_some();
                        wlog(format!("{} VAULT ({why}) flip back ({:.2}, {:.2}){} #{k}", head(sim, me), d.0, d.1,
                                     if came { ", the way she dashed in" } else { ", away from the nearest enemy" }));
                    }
                }
                None => {
                    if let Some(k) = counted("vault") {
                        wlog(format!("{} VAULT no way to tell where to flip, stays #{k}", head(sim, me)));
                    }
                }
            }
        }
        if let Some((d, left, from, refused)) = self.vault.as_mut() {
            let held = hard_cc(sim, me);
            if *left == 0 || held {
                if let Some(k) = counted("vault_done") {
                    wlog(format!("{} VAULT DONE moved {:.0} of {:.0} ({} steps refused{}) #{k}", head(sim, me), dist(*from, at),
                                 E_BACK * E_BACK_T as f64, refused, if held { ", cut by CC" } else { "" }));
                }
                self.vault = None;
            } else {
                let next = clamp((at.0 + d.0 * E_BACK, at.1 + d.1 * E_BACK));
                if !sim.entity_set_pos(me, next.0.round() as u64, next.1.round() as u64) {
                    *refused += 1;
                }
                *left -= 1;
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
                self.trail.push_back(at);
                if self.trail.len() > TRAIL {
                    self.trail.pop_front();
                }
            }
            None => {
                self.trail.clear();
                self.vault = None;
                self.dash = None;
            }
        }
        let riding = alive && has_buff(sim, me, RIDE);
        if !riding {
            if let Some(t) = self.riding.take() {
                if let Some(k) = counted("ride") {
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
                if let Some(k) = counted("ride") {
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
        "=== {ID} v{VERSION} (Quinn: League's ride on Valor, Skystrike when it runs out, the riding body) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:ride"), Ride::default());
    host.log(LogLevel::Info, "league_quinn loaded (the ride on Valor, Skystrike when it runs out, the riding body).");
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
    fn the_copy_names_this_crates_passive_and_buffs() {
        let s = include_str!("../override/league_quinn.data_champion");
        assert!(s.contains("\"league_quinn:ride\""));
        assert!(s.contains(&format!("\"{RIDE}\"")) && s.contains(&format!("\"{END}\"")));
        assert!(s.contains(&format!("\"r_ride_t\": {R_RIDE_T}")));
    }
}
