//! 希瓦娜附加包（用户 2026-10-24：「龙女变成龙不能保持住？」）。主包的数据不动、不换英雄副本，本包只补数据做不到的一件事：
//!
//! - **整身变龙**（`view.rs`）：龙形时站着、跑着、挨打、阵亡也是龙（纳尔附加包整身变巨型的做法）。主包只有出招是龙
//!   （`CasterAnimation` 播 `d_*`），游戏按名字自动播的 idle / run / hit / dead 仍是人形。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_shyvana.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! 显示处理表的槽换上没有、每个希瓦娜换形态的那一帧、每 10 秒换了几次动画名。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_shyvana";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_shyvana") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 龙形的 buff（主包数据：变龙 dg_t tick）和龙形刚结束、还没播变回动作的标记。
pub const DRAGON: [&str; 2] = ["league_shyvana_dg", "league_shyvana_was_dg"];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SHYVANA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_shyvana.log");
        }
    }
    PathBuf::from("league_shyvana.log")
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
        "=== {ID} v{VERSION} (Shyvana: the whole-body dragon) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    host.log(LogLevel::Info, "league_shyvana loaded (whole-body dragon).");
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

    /// The form buffs are the main pack's (build_shyvana.py's `dg` and `was_dg`).
    #[test]
    fn the_dragon_buffs_are_in_the_main_pack() {
        let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../league/champion/league_shyvana.data_champion");
        let data = std::fs::read_to_string(path).unwrap();
        for b in DRAGON {
            assert!(data.contains(&format!("\"{b}\"")), "{b}");
        }
    }
}
