//! 主包 `league` 自己的 DLL（league.dll）：用户 2026-10-12「PPU 可以先改一版亚索试试」「这个要装进主包里 不是附加包」。
//!
//! 主包的英雄还是纯数据；这个 DLL 只做数据做不到的画面：**高清帧（PPU）**——登记在 src/hd.rs 的英雄（先是亚索，PPU 3：
//! 身体 1 倍图整 3 倍，Codex 画的头每格 2×2）在战场、卡牌、图鉴、头像上都画自己图里 PPU 倍密的 `hd_` 帧，大小不变、
//! 像素更细：游戏按名字取动画表和贴图的两个函数上挂钩，交回影子表（每个动作都是高清帧，矩形 ÷ PPU）和宽高 ÷ PPU 的
//! 贴图代理（src/lookup.rs）。只在游戏 0.6.3 的 Windows 版上挂钩（核对函数开头的字节）；别的版本、Mac / Linux（没有
//! DLL）什么都不改，英雄照旧画 1 倍的帧。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league.log`，每次启动游戏重写（上一次的留作 league.prev.log）。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod hd;
#[cfg(windows)]
mod lookup;

pub const ID: &str = "league";
const VERSION: &str = "0.4.1";

static LOG_LOCK: Mutex<()> = Mutex::new(());

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
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "[{:8.2}] {}", T0.elapsed().as_secs_f64(), msg.as_ref());
        let _ = f.flush();
    }
}

fn init(host: &StableHost) -> StableMod {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!("=== {ID}.dll {VERSION} (dense frames) loaded: game {}.{}.{} abi {} log={} ===",
        v.major, v.minor, v.patch, host.abi_level(), LOG_PATH.display()));
    #[cfg(windows)]
    lookup::install_once();
    host.log(LogLevel::Info, "League Heroes: dense (PPU) frames for the heroes that have them (game 0.6.3, Windows).");
    StableMod::new(ID)
}

declare_stable_mod!(init);
