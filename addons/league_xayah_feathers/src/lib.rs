//! 霞附加包：「倒钩」照英雄联盟按每个敌人被几根羽毛打中定身（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话
//! 全部补附加包」）。
//!
//! 主包是纯数据，数不了每个目标各被打了几次：一次收回里打中**英雄**的第 3 次起（不管是不是同一个人），被打中的英雄定身。
//! 英雄联盟里是同一个敌人被 3 根羽毛打中才定身。本包：副本里收回的羽毛打中英雄时的计数梯子（`league_xayah_rh2` / `rh1`，
//! 记在霞身上）都换成原生效果 `league_xayah_feathers:hit`（`input` 就是被打中的人）：
//!
//! - 在他身上数：`COUNTS`（`LIFE` tick，同主包的 60 tick 计数窗口）；第 `ROOT_AT` 根定身 `ROOT` tick（`apply_cc` 禁锢，
//!   同主包 1.25 秒），挂主包的定身画面 buff `league_xayah_e_bind`，播主包的画面和声音；定身后从头数。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_xayah_feathers.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_xayah_feathers";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_xayah_feathers") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 他身上的计数：挂着哪个就是被打中了几根。
pub const COUNTS: [&str; 2] = ["league_xayah_feathers_1", "league_xayah_feathers_2"];
pub const LIFE: usize = 60;
pub const ROOT_AT: usize = 3;
pub const ROOT: usize = 75;
/// 主包的定身画面 buff、画面和声音。
pub const BIND_VIEW: &str = "league_xayah_e_bind";
pub const ROOT_FX: &str = "league_xayah_e_root";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNT: Mutex<usize> = Mutex::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_XAYAH_FEATHERS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_xayah_feathers.log");
        }
    }
    PathBuf::from("league_xayah_feathers.log")
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

/// Log the first 150 and every 25th after.
fn counted() -> Option<usize> {
    let mut n = COUNT.lock().unwrap_or_else(|e| e.into_inner());
    *n += 1;
    (*n <= 150 || *n % 25 == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>, me: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{kind} m={} s={}] t={} #{me}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 计数 =====================

/// Feathers on him after one more hit, and whether this one roots (then the count starts over).
pub fn after_hit(n: usize) -> (usize, bool) {
    if n + 1 >= ROOT_AT { (0, true) } else { (n + 1, false) }
}

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

fn count(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .filter_map(|b| COUNTS.iter().position(|n| b.name() == *n)).map(|k| k + 1).max().unwrap_or(0)
    })
}

struct Hit;

impl StableEffectType for Hit {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(id) = target_of(&input).filter(|&id| sim.get_entity(id).is_some_and(|e| e.is_champion() && e.is_alive()))
        else { return };
        let had = count(sim, id);
        let (n, root) = after_hit(had);
        for c in COUNTS {
            sim.entity_remove_buff(id, c);
        }
        if n > 0 {
            sim.add_buff(id, &BuffV1::timed(COUNTS[n - 1], LIFE));
        }
        if root {
            sim.apply_cc(id, &CcV1::of_kind(CcKindV1::Bind, ROOT as u64));
            sim.add_buff(id, &BuffV1::timed(BIND_VIEW, ROOT));
            sim.play_view_effect(ROOT_FX, caster, &InputTargetV1::target(id), 0, 0, 0);
            sim.play_sfx(ROOT_FX, caster, &InputTargetV1::target(id));
        }
        if let Some(k) = counted().filter(|_| root || had == 0) {
            wlog(format!("{} FEATHER #{k} on #{id}: {} -> {}{}", head(sim, caster), had + 1, if root { 0 } else { n },
                         if root { " ROOTED" } else { "" }));
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Xayah's feathers root whom three of them strike) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:hit"), Hit);
    host.log(LogLevel::Info, "league_xayah_feathers v1 loaded (three feathers on one enemy root him).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_third_feather_on_one_enemy_roots() {
        assert_eq!(after_hit(0), (1, false));
        assert_eq!(after_hit(1), (2, false));
        assert_eq!(after_hit(2), (0, true));
    }
}
