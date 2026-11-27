//! 终末的女武神包自己的代码（ragnarok.dll，和 ragnarok/mod.mod_info 放在一起）：英雄数据做不到的部分，一个英雄一个模块。
//! 新英雄：在这里加模块，在 `init` 里调它的 `register`。
//!
//! 高清帧（PPU）也在这里：src/hd.rs 是本包的表，交给和 league.dll、tft.dll 共用的 hd_engine。游戏里第一个加载的包 DLL
//! 自己挂钩，后加载的把表交给它、自己不挂（hd_engine 的 src/share.rs）。所以只开本包也有高清帧，和英雄联盟、金铲铲包
//! 一起开也不抢。引擎的日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\ragnarok.log`，每次启动重写，
//! 上一次的留作 ragnarok.prev.log；每个英雄另有自己的日志。

pub mod adam;
pub mod apollo;
pub mod beelzebub;
pub mod hades;
pub mod hd;
pub mod heracles;
pub mod jack;
pub mod kintoki;
pub mod kojiro;
pub mod leonidas;
pub mod loki;
pub mod lubu;
pub mod odin;
pub mod okita;
pub mod poseidon;
pub mod qin;
pub mod raiden;
pub mod shiva;
pub mod simo;
pub mod susanoo;
pub mod tesla;
pub mod buddha;
pub mod thor;
pub mod zeus;
pub mod zerofuku;

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

/// 测试写到临时目录，别让游戏的 ragnarok.log 看起来像刚写过。
#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("ragnarok_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("RAGNAROK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("ragnarok.log");
        }
    }
    PathBuf::from("ragnarok.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);
static T0: LazyLock<std::time::Instant> = LazyLock::new(std::time::Instant::now);

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

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

fn init(host: &StableHost) -> StableMod {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!("=== ragnarok.dll {VERSION} (Record of Ragnarok heroes: rules and dense frames) loaded: game {}.{}.{} abi {} log={} ===",
        v.major, v.minor, v.patch, host.abi_level(), LOG_PATH.display()));
    // 显示钩子晚挂（2026-11-21）：当主时战场缩放第一帧（Frame）再换槽
    #[cfg(windows)]
    hd_engine::defer_display();
    // 先把高清帧表交给引擎：本包先加载就自己挂钩，不然交给先挂钩的那个 DLL
    #[cfg(windows)]
    match hd_engine::start(&hd::table(), &format!("ragnarok.dll {VERSION}"), |m: &str| wlog(m)) {
        Role::Host => host.log(LogLevel::Info, "ragnarok.dll: dense (PPU) frames for the Record of Ragnarok heroes."),
        Role::Guest { host: by, .. } => host.log(
            LogLevel::Info,
            &format!("ragnarok.dll: dense (PPU) frames for the Record of Ragnarok heroes, drawn by {by}."),
        ),
        Role::Off(why) => host.log(LogLevel::Info, &format!("ragnarok.dll: the heroes' 1x frames - {why}.")),
    }
    let mut module = StableMod::new("ragnarok");
    lubu::register(host, &mut module);
    thor::register(host, &mut module);
    zeus::register(host, &mut module);
    adam::register(host, &mut module);
    poseidon::register(host, &mut module);
    kojiro::register(host, &mut module);
    heracles::register(host, &mut module);
    jack::register(host, &mut module);
    raiden::register(host, &mut module);
    shiva::register(host, &mut module);
    buddha::register(host, &mut module);
    zerofuku::register(host, &mut module);
    hades::register(host, &mut module);
    qin::register(host, &mut module);
    beelzebub::register(host, &mut module);
    tesla::register(host, &mut module);
    leonidas::register(host, &mut module);
    apollo::register(host, &mut module);
    okita::register(host, &mut module);
    susanoo::register(host, &mut module);
    simo::register(host, &mut module);
    loki::register(host, &mut module);
    kintoki::register(host, &mut module);
    odin::register(host, &mut module);
    #[cfg(windows)]
    module.set_extension(Frame);
    module
}

/// 每帧：高清帧引擎当主时的显示钩子第一帧挂上、被跳过就接回来（hd_engine::frame）。本包原来没有客户端扩展。
#[cfg(windows)]
struct Frame;

#[cfg(windows)]
impl StableExtension for Frame {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        hd_engine::frame(ctx.is_in_game(), |p| ctx.ui_visible(p), |p| ctx.ui_text(p));
    }
}

declare_stable_mod!(init, requires = 9);
