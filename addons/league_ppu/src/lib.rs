//! 高清精灵（PPU）附加包，第一版：只读探测（用户：「我们可以研修一下昨天讲的PPU那个方法 看看怎么样完美的接入变成我们自己的东西」，
//! 选了「B 自己写渲染钩子」「先做只读探测版」）。
//!
//! 研究（2026-10-12，游戏 0.6.3）：工坊 Rin 的 tfm2_ppu_core 在战场的实体绘制函数（rva 0x231f310）里，把
//! 0x231fb80 那条 `movss xmm1, [r13 + 0x1b4]` 换成跳转，按资源名把读到的数除以 PPU。r13 是显示世界的实体值——和凯隐、
//! 佛耶戈附加包每帧走的是同一个结构（+0x40 / +0x48 英雄 id，+0x50 / +0x58 / +0x60 身体用的资源名，+0x68.. 正在播的动画名）。
//! **值 +0x1b4 是这个实体的绘制缩放**：游戏只在 |缩放 − 1| > 0.001 时走带缩放的那条路，把它写进绘制命令的 x、y 缩放。
//! 所以不用改游戏的指令：在凯隐附加包也挂着的显示更新槽（rva 0x3c31358）里，等原来的函数跑完，给我们登记的英雄换上
//! 2 倍的图、把 +0x1b4 写成「原值 ÷ PPU」就行（第二版）。
//!
//! 这一版什么都不写，只记：每个实体的英雄 id、资源名、正在播的动画、+0x1b4 和它前后几个数，变了才记一行；每 10 秒一行汇总。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ppu.log`，每次启动游戏重写（上一次的留作 .prev.log）。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[cfg(windows)]
mod view;

const ID: &str = "league_ppu";

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_PPU_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ppu.log");
        }
    }
    PathBuf::from("league_ppu.log")
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

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, _module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v0.1 (read-only probe of the display entities' draw scale) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    #[cfg(windows)]
    view::install_once();
    host.log(LogLevel::Info, "league_ppu v0.1 loaded (read-only probe of the battlefield draw scale).");
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
