//! 奎桑提附加包（用户 2026-10-22：全盛姿态「单独一套」动作）。主包是纯数据，全盛时的出招（`ao_attack` / `ao_skill` … ）由数据的
//! `CasterAnimation` 按全盛 buff 播；游戏按名字自动播的待机、走、挨打数据换不了，本包补这一件事：
//!
//! - **全盛的整身**（`view.rs`）：他身上有全盛 buff `league_ksante_ao`（主包大招挂的，`ao_t` tick）时，站着、走着、挨打都画成全盛姿态
//!   （`ao_idle` / `ao_run` / `ao_hit`），普攻的第一 tick 也是 `ao_attack`。不改任何数据：本包没有副本，主包的奎桑提原样。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ksante.log`，每次启动游戏重写，上一次的留在 .prev.log：`FORM`（画面里换
//! 姿态，限了条数）和显示统计。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_ksante";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_ksante") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 全盛姿态的 buff（主包大招挂的）：view.rs 照它换画面。
pub const ALL_OUT: &str = "league_ksante_ao";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KSANTE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ksante.log");
        }
    }
    PathBuf::from("league_ksante.log")
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

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, _module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (K'Sante: the All Out body) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    host.log(LogLevel::Info, "league_ksante loaded (the All Out body).");
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
    fn the_all_out_buff_is_the_main_packs() {
        let kit = include_str!("../../../league/champion/league_ksante.data_champion");
        assert!(kit.contains(&format!("\"{ALL_OUT}\"")), "{ALL_OUT} is not in the main pack's K'Sante");
    }
}
