//! The tft pack's own code (tft.dll, next to tft/mod.mod_info): what a tft hero's data cannot do, one module a hero,
//! all in the one tft mod (the user, 2026-10-26: 「诺拉和爆爆合并在一个mod啊」「tft的英雄都放一个mod里 参考英雄联盟」).
//! A new hero: its module here, its `register` called from `init`.
//!
//! The heroes' dense (PPU) frames too (0.28.0, the pack going on the Workshop on its own): src/hd.rs is the pack's table,
//! drawn by hd_engine - the same engine league.dll's are. `init` hands it the table first: the first pack DLL loaded in
//! the game hooks it (tft.dll alone, or before league in the Mods menu), a later one hands its table to that one and
//! hooks nothing (hd_engine src/share.rs). Before 0.28.0 league.dll drew these heroes' dense frames, only with both packs
//! enabled. The engine's lines: `%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft.log`, new each start (the last one
//! kept as tft.prev.log); each hero module keeps its own log.

pub mod alune;
pub mod aoshin;
pub mod daeja;
pub mod hd;
pub mod idas;
pub mod kobuko;
pub mod krug;
pub mod loris;
pub mod maddie;
pub mod nomsy;
pub mod norra;
pub mod renni;
pub mod scar;
pub mod sentinel;
pub mod sevika;
pub mod shiohyu;
pub mod silco;
pub mod smeech;
pub mod sohm;
pub mod steb;
pub mod syfen;
pub mod terra;
pub mod vander;
pub mod violet;
pub mod zippy;

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use hd_engine::Role;
use mod_api_stable::*;

const VERSION: &str = env!("CARGO_PKG_VERSION");

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

/// The tests log into the temp folder (league_main's way: their lines must not make the game's tft.log look recent).
#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("tft_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft.log");
        }
    }
    PathBuf::from("tft.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);
static T0: LazyLock<std::time::Instant> = LazyLock::new(std::time::Instant::now);

/// A line in tft.log (the engine's; the file stays open, as league.log does).
fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("[{:8.2}] {}\n", T0.elapsed().as_secs_f64(), msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first).
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

fn init(host: &StableHost) -> StableMod {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!("=== tft.dll {VERSION} (the tft heroes' rules and dense frames) loaded: game {}.{}.{} abi {} log={} ===",
        v.major, v.minor, v.patch, host.abi_level(), LOG_PATH.display()));
    // the dense frames first: this pack's table to the engine, which hooks the game from here or hands the table to the
    // pack DLL that did (league.dll loaded first)
    match hd_engine::start(&hd::table(), &format!("tft.dll {VERSION}"), |m: &str| wlog(m)) {
        Role::Host => host.log(LogLevel::Info, "tft.dll: dense (PPU) frames for the tft heroes."),
        Role::Guest { host: by, .. } => {
            host.log(LogLevel::Info, &format!("tft.dll: dense (PPU) frames for the tft heroes, drawn by {by}."))
        }
        Role::Off(why) => host.log(LogLevel::Info, &format!("tft.dll: the tft heroes' 1x frames - {why}.")),
    }
    let mut module = StableMod::new("tft");
    alune::register(host, &mut module);
    aoshin::register(host, &mut module);
    daeja::register(host, &mut module);
    idas::register(host, &mut module);
    kobuko::register(host, &mut module);
    krug::register(host, &mut module);
    loris::register(host, &mut module);
    maddie::register(host, &mut module);
    nomsy::register(host, &mut module);
    norra::register(host, &mut module);
    renni::register(host, &mut module);
    scar::register(host, &mut module);
    sentinel::register(host, &mut module);
    sevika::register(host, &mut module);
    shiohyu::register(host, &mut module);
    silco::register(host, &mut module);
    smeech::register(host, &mut module);
    sohm::register(host, &mut module);
    steb::register(host, &mut module);
    syfen::register(host, &mut module);
    terra::register(host, &mut module);
    vander::register(host, &mut module);
    violet::register(host, &mut module);
    zippy::register(host, &mut module);
    module
}

declare_stable_mod!(init, requires = 9);
