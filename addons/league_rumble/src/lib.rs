//! 兰博附加包（用户 2026-10-25：「红温整套切换」）。主包的数据不动；本包补数据做不到的两件事：
//!
//! - **整身红温**（`view.rs`）：过热时站着、跑着、挨打、阵亡也是红温的样子（希瓦娜附加包整身变龙的做法）。主包只有过热
//!   时的普攻是红温（`CasterAnimation` 播 `oh_attack`），游戏按名字自动播的 idle / run / hit / dead 仍是平常的样子。
//! - **边走边喷火**（0.2.0，用户 2026-10-29：「兰博不会边走边放火吗」→「就这么做」）：`mod.override_info` 把主包的兰博换成
//!   `override/` 里的副本（`make_override.py` 用 tools/kit/build_rumble.py 的 `native=1` 生成）：纵火盛宴只站着端平炮口
//!   （q_first tick），之后挂 `league_rumble_q_on`（q_t tick）照常喷、能走；`view.rs` 在它挂着时把 idle / run 换成他图里
//!   的 `q_stand` / `q_run`（火焰画在炮口上，tools/art/rig_rumble.py）。主包里他照旧站着喷（不装本包时跑步帧上没有火）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_rumble.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! 显示处理表的槽换上没有、每个兰博红温 / 喷火 / 平常的那一帧、每 10 秒换了几次动画名。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_rumble";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_rumble") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 过热的 buff（主包数据：热量满 100 时 oh_t tick）。
pub const OVERHEAT: [&str; 1] = ["league_rumble_oh"];
/// 边走边喷火的那 1.5 秒（副本数据：纵火盛宴挂 q_t tick）。
pub const FLAMING: [&str; 1] = ["league_rumble_q_on"];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_RUMBLE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_rumble.log");
        }
    }
    PathBuf::from("league_rumble.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line stalled the simulation thread (2026-10-12, #242)
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

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, _module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Rumble: the whole-body red-hot Overheat, Flamespitter on the move) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    host.log(LogLevel::Info, "league_rumble loaded (whole-body red-hot Overheat, Flamespitter on the move).");
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

    /// The Overheat buff is the main pack's (build_rumble.py's `oh`).
    #[test]
    fn the_overheat_buff_is_in_the_main_pack() {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../league/champion/league_rumble.data_champion");
        let data = std::fs::read_to_string(path).unwrap();
        for b in OVERHEAT {
            assert!(data.contains(&format!("\"{b}\"")), "{b}");
        }
    }

    /// The copy's Flamespitter marks the burst (FLAMING) and holds him for the aim only: the main pack plays `skill` for
    /// the whole burst (q_t 90 ticks), the copy for q_first (8).
    #[test]
    fn the_copy_lets_him_walk_while_it_burns() {
        let copy = include_str!("../override/league_rumble.data_champion").replace('\r', "");
        let main = include_str!("../../../league/champion/league_rumble.data_champion").replace('\r', "");
        for b in FLAMING {
            assert!(copy.contains(&format!("\"{b}\"")), "the copy never puts {b} on him");
            assert!(!main.contains(&format!("\"{b}\"")), "the main pack puts {b} on him");
        }
        let skill = |s: &str| {
            let q = &s[s.find("\"skill\": {").unwrap()..s.find("\"skill2\": {").unwrap()];
            q.chars().filter(|c| !c.is_whitespace()).collect::<String>()
        };
        let hold = |t: usize| format!("{{\"type\":\"CasterAnimation\",\"name\":\"skill\",\"tick\":{t}}}");
        assert!(skill(&main).contains(&hold(90)), "the main pack no longer holds him 90 ticks (update this test)");
        assert!(!skill(&copy).contains(&hold(90)), "the copy still holds him 90 ticks");
        assert!(skill(&copy).contains(&hold(8)), "the copy has no aim");
    }
}
