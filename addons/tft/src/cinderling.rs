//! 绯红树怪（`tft_cinderling`，英文 Cinderling）数据做不到的部分（金铲铲第 18 赛季的峡谷野怪 / 猎人；技能按用户同意的方案，
//! 2026-11-02）。它的技能全是数据自己的（tools/kit/build_cinderling.py：绯红霸符的叠层阶梯、灼烧、刃叶、钻土突袭、燎原叶暴），
//! 数据的 `passive` 是这里的 `tft_cinderling:scarlet`，只做两件数据做不到的事：
//!
//! - **死亡**：倒下时播 `tft_cinderling_d`（数据没有死亡的时机）。
//! - **日志**：霸符叠满（它身上出现数据的旗子 `tft_cinderling_p_full`）时记一笔，游戏里看叠层有没有跑起来。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_cinderling.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_cinderling";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn gp(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_CINDERLING_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_cinderling.log");
        }
    }
    PathBuf::from("tft_cinderling.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
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
const LOG_EVERY: usize = 100;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        _ => "unknown",
    };
    format!("[{kind} t={}] #{id}", sim.tick())
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// A rising edge: true only on the tick `now` turns on after `was` was off.
pub fn rose(was: bool, now: bool) -> bool {
    now && !was
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Scarlet {
    me: usize,
    full: bool,
}

impl StablePassive for Scarlet {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, _: &str) {}

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.full = false;
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Cinderling (player {player}, team {team})", head(sim, me)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.me = me;
        let full = has_buff(sim, me, &gp("p_full"));
        if rose(self.full, full) {
            if let Some(k) = counted("full") {
                wlog(format!("{} FULL #{k}: Scarlet Buff at 4 stacks, attacks burn", head(sim, me)));
            }
        }
        self.full = full;
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        // the little sapling's death cry (the data has no moment for it)
        let me = self.me;
        self.full = false;
        sim.play_sfx(&gp("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// The Cinderling's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Cinderling: its death sound, Scarlet Buff's full stacks logged) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:scarlet"), Scarlet::default());
    host.log(LogLevel::Info, "tft.dll: Cinderling (death sound, Scarlet Buff log).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn full_is_logged_once_a_climb() {
        assert!(rose(false, true));
        assert!(!rose(true, true));
        assert!(!rose(true, false));
        assert!(!rose(false, false));
    }
}
