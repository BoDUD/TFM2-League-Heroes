//! Lucian walks firing The Culling (needs League of Legends Heroes): while his R fires - the main pack's channel flag
//! `league_lucian_r_ch` on him (183 ticks from the cast, taken away by crowd control as the shots stop) - the `run` the
//! game plays when he walks is drawn as `r_run`, his walk with both pistols levelled forward (Codex's 8 frames, his
//! sheet's r_run / hd_r_run / lo_r_run: tools/art/casts_lucian_runshoot.py). The user, 2026-10-27: 「移动大招看不出来放大
//! 只听得到音乐」「是不是少了点动作？」「动作可以，继续做附加包让开大时换成这套动作」. No data of his is replaced and nothing in the
//! simulation changes: only the name of the animation on screen ([`view`]). Windows, game 0.6.4 on (the display handler's
//! place found at run time by game_places); elsewhere nothing happens and he runs as before.
//!
//! Log: `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_lucian.log`.

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[cfg(windows)]
pub mod view;

/// The main pack's R channel flag: the display hook swaps his run while it is on.
pub const FORM: &str = "league_lucian_r_ch";

const ID: &str = "league_lucian";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_lucian") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

// ===================== log =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LUCIAN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_lucian.log");
        }
    }
    PathBuf::from("league_lucian.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub fn wlog(msg: impl AsRef<str>) {
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

#[cfg_attr(not(windows), allow(dead_code))]
fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

// ===================== register =====================

pub fn register(host: &StableHost, _module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Lucian: his walk while The Culling fires) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    #[cfg(windows)]
    view::install_once();
    host.log(LogLevel::Info, "league_lucian loaded (his walk while The Culling fires).");
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
