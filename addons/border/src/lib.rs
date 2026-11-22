//! 边境巡团包自己的代码（border.dll，和 border/mod.mod_info 放在一起）：英雄数据做不到的部分，一个英雄一个模块。
//! 新英雄：在这里加模块，在 `init` 里调它的 `register`。
//!
//! 每个英雄有一个原生被动（记账：背压、张力、灯火、热量、跟踪、结晶……）和几个原生效果（数据在技能的时间点上调用：选目标、
//! 结算）。原生效果只看施法的人自己身上的东西，不认英雄 id：佛耶戈附身、妮蔻变身用的都是同一份数据，谁放都照样结算
//! （被动攒的层数不在他身上就按 0 算）。塞拉斯偷大招不走这里：他的副本在联盟包的附加包里，用每个英雄的纯数据版 `sylas_ult()`
//! （边境包没开时也得能加载）。
//!
//! 高清帧（PPU）也在这里：src/hd.rs 是本包的表，交给和 league.dll、tft.dll、ragnarok.dll 共用的 hd_engine。游戏里第一个
//! 加载的包 DLL 自己挂钩，后加载的把表交给它、自己不挂（hd_engine 的 src/share.rs）。日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\border.log`，每次启动重写，上一次的留作 border.prev.log。

pub mod cenlei;
pub mod common;
pub mod dengmi;
pub mod fusuo;
pub mod hd;
pub mod jiyan;
pub mod lanti;
pub mod luxin;
pub mod wuling;
pub mod xiaolun;
pub mod yanxi;
pub mod yindu;
pub mod zhongli;
pub mod zhumo;

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

/// 测试写到临时目录，别让游戏的 border.log 看起来像刚写过。
#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("border_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("BORDER_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("border.log");
        }
    }
    PathBuf::from("border.log")
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

fn init(host: &StableHost) -> StableMod {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!("=== border.dll {VERSION} (Border Patrol heroes: rules and dense frames) loaded: game {}.{}.{} abi {} log={} ===",
        v.major, v.minor, v.patch, host.abi_level(), LOG_PATH.display()));
    // 显示钩子晚挂：当主时战场缩放第一帧（Frame）再换槽（和 ragnarok.dll 一样）
    #[cfg(windows)]
    hd_engine::defer_display();
    #[cfg(windows)]
    match hd_engine::start(&hd::table(), &format!("border.dll {VERSION}"), |m: &str| wlog(m)) {
        Role::Host => host.log(LogLevel::Info, "border.dll: dense (PPU) frames for the Border Patrol heroes."),
        Role::Guest { host: by, .. } => host.log(
            LogLevel::Info,
            &format!("border.dll: dense (PPU) frames for the Border Patrol heroes, drawn by {by}."),
        ),
        Role::Off(why) => host.log(LogLevel::Info, &format!("border.dll: the heroes' 1x frames - {why}.")),
    }
    let mut module = StableMod::new("border");
    cenlei::register(host, &mut module);
    xiaolun::register(host, &mut module);
    dengmi::register(host, &mut module);
    zhumo::register(host, &mut module);
    fusuo::register(host, &mut module);
    yanxi::register(host, &mut module);
    yindu::register(host, &mut module);
    lanti::register(host, &mut module);
    luxin::register(host, &mut module);
    jiyan::register(host, &mut module);
    zhongli::register(host, &mut module);
    wuling::register(host, &mut module);
    #[cfg(windows)]
    module.set_extension(Frame);
    module
}

/// 每帧：高清帧引擎当主时的显示钩子第一帧挂上、被跳过就接回来（hd_engine::frame）。
#[cfg(windows)]
struct Frame;

#[cfg(windows)]
impl StableExtension for Frame {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        hd_engine::frame(ctx.is_in_game(), |p| ctx.ui_visible(p), |p| ctx.ui_text(p));
    }
}

declare_stable_mod!(init, requires = 9);
