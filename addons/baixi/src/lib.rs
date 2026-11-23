//! 百戏原创系列原生模块（baixi.dll）：五位民间手艺英雄的配音、麦芽头顶转盘图标、拂面三脸切换、以及高清帧（PPU）。

pub mod fumian;
pub mod hd;
pub mod voice;

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

#[cfg(windows)]
use hd_engine::Role;
use mod_api_stable::*;

use crate::voice::HeroVoice;

const VERSION: &str = env!("CARGO_PKG_VERSION");

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("baixi_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("BAIXI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("baixi.log");
        }
    }
    PathBuf::from("baixi.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);
static T0: LazyLock<std::time::Instant> = LazyLock::new(std::time::Instant::now);

pub fn wlog(msg: impl AsRef<str>) {
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

fn init(host: &StableHost) -> StableMod {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== baixi.dll {VERSION} (Baixi Original Heroes) loaded: game {}.{}.{} abi {} ===",
        v.major, v.minor, v.patch, host.abi_level()
    ));

    #[cfg(windows)]
    hd_engine::defer_display();
    #[cfg(windows)]
    match hd_engine::start(&hd::table(), &format!("baixi.dll {VERSION}"), |m: &str| wlog(m)) {
        Role::Host => host.log(LogLevel::Info, "baixi.dll: dense (PPU) frames for Baixi heroes."),
        Role::Guest { host: by, .. } => {
            host.log(LogLevel::Info, &format!("baixi.dll: dense (PPU) frames drawn by {by}."));
        }
        Role::Off(why) => host.log(LogLevel::Info, &format!("baixi.dll: 1x frames ({why}).")),
    }

    let mut module = StableMod::new("baixi");
    module.add_native_passive("baixi_dianjing:voice", HeroVoice::new("baixi_dianjing"));
    module.add_native_passive("baixi_sangeng:voice", HeroVoice::new("baixi_sangeng"));
    module.add_native_passive(
        "baixi_maiya:voice",
        HeroVoice::new("baixi_maiya")
            .with_init_buff("baixi_maiya_wheel_dragon", &["baixi_maiya_wheel_phoenix", "baixi_maiya_wheel_fish"]),
    );
    module.add_native_passive("baixi_huoshu:voice", HeroVoice::new("baixi_huoshu"));
    fumian::register(host, &mut module);

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
    }
}

declare_stable_mod!(init, requires = 9);
