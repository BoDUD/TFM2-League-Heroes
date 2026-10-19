//! 奎因附加包（用户 2026-10-19：大招主包冲刺 + 附加包换形态）。主包保持纯数据；`mod.override_info` 把主包的奎因换成 `override/`
//! 里的副本（`make_override.py` 用 tools/kit/build_quinn.py 的 `native=1` 生成：被动换成本包的 `league_quinn:ride`，大招只叫来华洛
//! 骑上、挂 `league_quinn_r_ride`（`R_RIDE_T` tick，移速 +`r_ride_ms`%），骑着时普攻、技能 1、技能 2 先施放鹰翼天翔，大招的说明开头加
//! 【扩展包】），本包补数据做不到的两件事：
//!
//! - **骑行到时自动落地**：英雄联盟里她骑着华洛一直跑，直到出招或骑行结束才施放鹰翼天翔；数据在 buff 到期时什么也做不了。本包每 tick
//!   看她身上的 `r_ride`：骑了 `R_RIDE_T - 2` tick 还没出招，就挂 2 tick 的 `league_quinn_r_end`，副本里骑上时起的每 tick 守望看到就
//!   施放鹰翼天翔（伤害、标记、华洛回到头顶、落地动作，和出招时一样）。
//! - **骑乘的样子**（`view.rs`，只在游戏 0.6.4 上）：骑着的时候站着、走着、挨打都是骑在华洛背上的 `r_idle` / `r_run` / `r_hit`。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_quinn.log`，每次启动游戏重写，上一次的留在 .prev.log：`RIDE`（骑上、
//! 出招落地 / 到时落地、骑了多久多远）、`FORM`（画面里换形态），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_quinn";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 骑乘（副本的大招挂的）：view.rs 照它换画面；到时落地的信号（本包挂 2 tick，副本的守望看到就施放鹰翼天翔）。
pub const RIDE: &str = "league_quinn_r_ride";
pub const END: &str = "league_quinn_r_end";
/// 骑多久（build_quinn.P 的 r_ride_t，make_override.py 核对）。
pub const R_RIDE_T: usize = 360;
/// 提前几 tick 挂落地信号：守望每 tick 看一次，骑乘 buff 在最后一 tick 还在。
pub const END_LEAD: usize = 2;

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
    fn the_copy_names_this_crates_passive_and_buffs() {
        let s = include_str!("../override/league_quinn.data_champion");
        assert!(s.contains("\"league_quinn:ride\""));
        assert!(s.contains(&format!("\"{RIDE}\"")) && s.contains(&format!("\"{END}\"")));
        assert!(s.contains(&format!("\"r_ride_t\": {R_RIDE_T}")));
    }
}
