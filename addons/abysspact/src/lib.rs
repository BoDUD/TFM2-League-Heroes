//! Abyss Pact (渊契) native DLL (`abysspact.dll`):
//! signature mechanics for all 15 dark-fantasy original champions plus shared HD PPU registration.

pub mod anchor;
pub mod bloodmoon;
pub mod bonebow;
pub mod carapace;
pub mod corvus;
pub mod effigy;
pub mod faceless;
pub mod faceless_view;
pub mod hd;
pub mod hourglass;
pub mod leech;
pub mod noctua;
pub mod oathbreaker;
pub mod sevenfold;
pub mod undertaker;
pub mod vesper;
pub mod view_forms;
pub mod voice;
pub mod whisperer;

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

#[cfg(windows)]
use hd_engine::Role;
use mod_api_stable::*;

const VERSION: &str = env!("CARGO_PKG_VERSION");

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("abysspact_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("ABYSSPACT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("abysspact.log");
        }
    }
    PathBuf::from("abysspact.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);
static T0: LazyLock<std::time::Instant> = LazyLock::new(std::time::Instant::now);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("[{:8.2}] {}\n", T0.elapsed().as_secs_f64(), msg.as_ref()).as_bytes());
    }
}

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// Squared Euclidean distance between two `(u64, u64)` world positions.
pub(crate) fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0.abs_diff(b.0);
    let dy = a.1.abs_diff(b.1);
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

pub(crate) fn has_buff(sim: &StableSim<'_>, id: usize, want: &str) -> bool {
    let Some(e) = sim.get_entity(id) else { return false };
    let n = e.buff_count();
    (0..n).any(|i| e.buff_at(i).is_some_and(|b| b.name() == want))
}

pub(crate) fn consume_buff(sim: &mut StableSim<'_>, id: usize, want: &str) -> bool {
    sim.entity_remove_buff(id, want) > 0
}

fn init(host: &StableHost) -> StableMod {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== abysspact.dll {VERSION} (Abyss Pact heroes & HD frames) loaded: game {}.{}.{} abi {} ===",
        v.major, v.minor, v.patch, host.abi_level()
    ));

    #[cfg(windows)]
    hd_engine::defer_display();

    #[cfg(windows)]
    match hd_engine::start(&hd::table(), &format!("abysspact.dll {VERSION}"), |m: &str| wlog(m)) {
        Role::Host => host.log(LogLevel::Info, "abysspact.dll: dense (PPU) frames for Abyss Pact heroes."),
        Role::Guest { host: by, .. } => host.log(
            LogLevel::Info,
            &format!("abysspact.dll: dense (PPU) frames for Abyss Pact heroes, drawn by {by}."),
        ),
        Role::Off(why) => host.log(LogLevel::Info, &format!("abysspact.dll: 1x frames - {why}.")),
    }

    let mut module = StableMod::new("abysspact");
    // Batch 1
    oathbreaker::register(host, &mut module);
    faceless::register(host, &mut module);
    whisperer::register(host, &mut module);
    bonebow::register(host, &mut module);
    corvus::register(host, &mut module);
    faceless_view::install();
    // Batch 2
    bloodmoon::register(host, &mut module);
    undertaker::register(host, &mut module);
    effigy::register(host, &mut module);
    sevenfold::register(host, &mut module);
    vesper::register(host, &mut module);
    // Batch 3
    carapace::register(host, &mut module);
    leech::register(host, &mut module);
    noctua::register(host, &mut module);
    anchor::register(host, &mut module);
    hourglass::register(host, &mut module);
    view_forms::install();

    #[cfg(windows)]
    module.set_extension(Frame);
    module
}

#[cfg(windows)]
struct Frame;

#[cfg(windows)]
impl StableExtension for Frame {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        hd_engine::frame(ctx.is_in_game(), |p| ctx.ui_visible(p), |p| ctx.ui_text(p));
        faceless_view::observe_clock(ctx);
    }
}

declare_stable_mod!(init, requires = 9);
