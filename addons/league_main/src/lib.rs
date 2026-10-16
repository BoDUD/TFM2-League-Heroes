//! 主包 `league` 自己的 DLL（league.dll）：用户 2026-10-12「PPU 可以先改一版亚索试试」「这个要装进主包里 不是附加包」。
//!
//! 主包的英雄还是纯数据；这个 DLL 只做数据做不到的画面：**高清帧（PPU）**——登记在 src/hd.rs 的英雄（先是亚索，PPU 3：
//! 身体 1 倍图整 3 倍，Codex 画的头每格 2×2）在战场、卡牌、图鉴、头像上都画自己图里 PPU 倍密的 `hd_` 帧，大小不变、
//! 像素更细。src/lookup.rs：游戏按名字取动画表和贴图的两个函数上挂钩——动画表就地改成每个动作都是高清帧（矩形 ÷ PPU），
//! 贴图的宽高报 ÷ PPU，界面按帧大小画、UV 落在高清那块；战场按「UV × 图的真实像素」画，所以战场拿到真实的高清帧和真实
//! 宽高，src/view.rs 把实体的绘制缩放写成 ÷ PPU。只在 src/build.rs 认得的游戏版本上挂钩（每处要改要调的代码逐字节核对指纹，现在认得 0.6.4）；别的版本、
//! Mac / Linux（没有 DLL）什么都不改，英雄照旧画 1 倍的帧。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league.log`，每次启动游戏重写（上一次的留作 league.prev.log）。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod build;
pub mod hd;
#[cfg(windows)]
mod lookup;
#[cfg(windows)]
mod view;

pub const ID: &str = "league";
const VERSION: &str = "0.7.17";

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
    #[cfg(windows)]
    match build::detect(view::read_rva) {
        Ok(b) => {
            wlog(format!("game build: {}", b.name));
            lookup::install_once(b);
            view::install_once(b);
            host.log(LogLevel::Info, "League Heroes: dense (PPU) frames for the heroes that have them.");
        }
        Err(why) => {
            wlog(format!("game build unknown ({why}): no hooks - every hero draws its 1x frames"));
            host.log(LogLevel::Info, "League Heroes: this game build is not known to league.dll yet - 1x frames.");
        }
    }
    StableMod::new(ID)
}

declare_stable_mod!(init);
