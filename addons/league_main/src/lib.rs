//! 主包 `league` 自己的 DLL（league.dll）：用户 2026-10-12「PPU 可以先改一版亚索试试」「这个要装进主包里 不是附加包」。
//!
//! 主包的英雄还是纯数据；这个 DLL 只做数据做不到的画面：**高清帧（PPU）**——登记在 src/hd.rs 的英雄（先是亚索，PPU 3：
//! 身体 1 倍图整 3 倍，Codex 画的头每格 2×2）在战场、卡牌、图鉴、头像上都画自己图里 PPU 倍密的 `hd_` 帧，大小不变、
//! 像素更细；界面（BP 格子、图鉴 / 头像、选人位、选中特写、记分板头像）画每个英雄自己的小图集（0.7.140）。
//!
//! 画法——游戏按名字取动画表和贴图的两个函数上的钩子、战场的绘制缩放、界面小图集、认游戏版本（现在认得 0.7.0，认不得的
//! 由 game_places 在运行时找）——0.9.0 起在 addons/hd_engine，和 tft 包的 tft.dll 共用（tft 包要单独上创意工坊，只订阅它
//! 也要有高清帧）。init 把 src/hd.rs 的表交给引擎：进程里第一个加载的包 DLL 挂钩、画两个包的英雄；league.dll 加载在
//! tft.dll 之后时自己一个钩子都不挂，把表交给它（hd_engine src/share.rs）——两个包都开着时 Mods 菜单里谁先谁后都一样。
//! 认不得的游戏版本、Mac / Linux（没有 DLL）什么都不改，英雄照旧画 1 倍的帧。
//!
//! src/cache.rs（0.8.16）：游戏的 GPU 图片缓存（Skia 的 GrResourceCache，默认 256 MiB）放大到 1 GiB——一屏英雄多的界面
//! 不再因为装不下而每帧清掉、重新上传贴图。
//!
//! src/warm.rs（0.7.27）：标题画面出来以后，后台线程把主包 `sound/bgm/` 里的音频按盘上的顺序读一遍进系统缓存，
//! 比赛里音频第一次播放就不用在主线程等读盘。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league.log`，每次启动游戏重写（上一次的留作 league.prev.log）。
//! 挂钩、取表、缩放的行写在挂钩的那个 DLL 的日志里：tft.dll 先加载时在 tft.log，这里只有一行「交给了谁」。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use hd_engine::Role;
use mod_api_stable::*;

#[cfg(windows)]
mod cache;
pub mod hd;
#[cfg(windows)]
mod warm;

pub const ID: &str = "league";
const VERSION: &str = "0.9.0";

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

/// `cargo test` lines (league_test ...) went into the game's own league.log and made an old game's log look recent
/// (2026-10-13): the tests log into the temp folder instead, the DLL keeps its path.
#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("league_main_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league.log");
        }
    }
    PathBuf::from("league.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);
static T0: LazyLock<std::time::Instant> = LazyLock::new(std::time::Instant::now);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (15 000 lines a session,
    // about 9 s of stalls on the simulation thread, 2026-10-12, the user: 「LOL mod让游戏掉帧很严重 加载很卡」)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("[{:8.2}] {}\n", T0.elapsed().as_secs_f64(), msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

fn init(host: &StableHost) -> StableMod {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!("=== {ID}.dll {VERSION} (dense frames) loaded: game {}.{}.{} abi {} log={} ===",
        v.major, v.minor, v.patch, host.abi_level(), LOG_PATH.display()));
    // the GPU image cache first, whatever the build: it only needs Skia's GrResourceCache (src/cache.rs)
    #[cfg(windows)]
    cache::install_once(hd_engine::module_base());
    // the dense frames: this pack's table to the engine - it hooks the game from here (build, display pair, lookups,
    // scale, as before 0.9.0), or hands the table to the pack DLL that did (tft.dll loaded first: hd_engine src/share.rs)
    match hd_engine::start(&hd::table(), &format!("{ID}.dll {VERSION}"), |m: &str| wlog(m)) {
        Role::Host => host.log(LogLevel::Info, "League Heroes: dense (PPU) frames for the heroes that have them."),
        Role::Guest { host: by, .. } => host.log(LogLevel::Info,
            &format!("League Heroes: dense (PPU) frames for the heroes that have them, drawn by {by}.")),
        Role::Off(why) => host.log(LogLevel::Info, &format!("League Heroes: 1x frames - {why}.")),
    }
    let mut module = StableMod::new(ID);
    #[cfg(windows)]
    module.set_extension(warm::Warm);
    module
}

declare_stable_mod!(init);
