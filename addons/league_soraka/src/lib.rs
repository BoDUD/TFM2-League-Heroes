//! 索拉卡附加包：祈愿按英雄联盟给生命低的友军多回血（用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」，
//! 再说「接着做」：能做的小项都做）。
//!
//! 英雄联盟的祈愿（R）："healing herself and all allied champions, ... increased by 50% on targets below 40% of their maximum
//! health"。主包是纯数据，数据读不到任何人的当前生命，所以祈愿给每个友方英雄一样多（`220` + `60`% 法强，`HEAL` / `HEAL_AP`）。
//! `mod.override_info` 把主包的索拉卡换成 `override/` 里的副本（`make_override.py` 从主包生成：技能一字不改，只在大招那一圈
//! 治疗的**最前面**加一个本包的原生效果 `league_soraka:wish`，大招的说明换成本包的）：圈里的每个友方英雄先过这一步——生命低于
//! 最大生命的 `LOW_HP`%（40%）就多回复主包那一下的 `BONUS`%（50%：`110` + `30`% 法强），再照常吃主包的治疗。生命是治疗之前读的
//! （英雄联盟也是落下那一刻的生命）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_soraka.log`，每次启动游戏重写，上一次的留在 .prev.log：`WISH`
//! （谁生命低、多回复了多少），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_soraka";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_soraka") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 主包祈愿的治疗：固定值、法强 %（副本里那一下 `Heal` 的 `amount` / `ap_ratio`，`make_override.py` 和测试核对）。
pub const HEAL: usize = 220;
pub const HEAL_AP: usize = 60;
/// 生命低于最大生命的这么多 % 算「生命低」（英雄联盟 40%）。
pub const LOW_HP: usize = 40;
/// 生命低的多回复主包那一下的这么多 %（英雄联盟 50%）。
pub const BONUS: usize = 50;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SORAKA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_soraka.log");
        }
    }
    PathBuf::from("league_soraka.log")
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

const LOG_FIRST: usize = 60;
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
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{kind} m={} s={}] t={} #{id}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 规则（单元测试用） =====================

/// 生命 `hp` / 最大生命 `max` 的人算不算生命低（低于 `LOW_HP`%；最大生命读不到的不算）。
pub fn low(hp: usize, max: usize) -> bool {
    max > 0 && hp * 100 < max * LOW_HP
}

/// 主包那一下治疗（法强 `ap`）之外多回复的量：它的 `BONUS`%。
pub fn bonus(ap: usize) -> usize {
    (HEAL + HEAL_AP * ap / 100) * BONUS / 100
}

// ===================== 原生效果 =====================

/// 祈愿圈里的一个友方英雄（副本在主包的治疗前面调它）：生命低就多回复。
struct Wish;

impl StableEffectType for Wish {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let target = input.target_id;
        let Some((hp, max)) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        if !low(hp, max) {
            return;
        }
        let ap = sim.get_entity(caster).map_or(0, |e| e.stat().magic_power);
        let more = bonus(ap);
        sim.heal(caster, target, more);
        if let Some(k) = counted("wish") {
            let name = sim.get_entity(target).and_then(|e| e.name()).unwrap_or_default();
            wlog(format!("{} WISH {name}#{target} at {hp}/{max} ({}%): +{more} more (ap {ap}) #{k}", head(sim, caster),
                         hp * 100 / max.max(1)));
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Soraka: Wish heals {BONUS}% more on allied champions under {LOW_HP}% health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:wish"), Wish);
    host.log(LogLevel::Info, "league_soraka loaded (Wish heals more on allied champions at low health).");
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn under_forty_percent_is_low() {
        assert!(low(399, 1000));
        assert!(!low(400, 1000), "exactly 40% is not below it");
        assert!(!low(1000, 1000));
        assert!(low(1, 1000));
        assert!(!low(0, 0), "no maximum read: not low");
    }

    #[test]
    fn the_bonus_is_half_the_main_heal() {
        assert_eq!(bonus(0), 110);
        // 300 ability power: the main heal 220 + 180 = 400, half of it more
        assert_eq!(bonus(300), 200);
        assert_eq!(HEAL + HEAL_AP * 300 / 100 + bonus(300), 600, "League's x1.5 under 40%");
    }

    #[test]
    fn the_copy_calls_wish_first_in_the_main_heal() {
        let copy = include_str!("../override/league_soraka.data_champion");
        let v = copy.replace("\r\n", "\n");
        // the ult's slot to the next top-level key (the view lists)
        let ult = &v[v.find("\n  \"ult\": {").expect("no ult in the copy")..];
        let ult = &ult[..ult.find("\n  \"view_projectiles\"").unwrap_or(ult.len())];
        let at = ult.find("\"effect_ref\": \"league_soraka:wish\"").expect("the copy's ult never calls league_soraka:wish");
        let heal = ult.find("\"type\": \"Heal\"").expect("no Heal in the copy's ult");
        assert!(at < heal, "the add-on's step must come before the main pack's heal (health read before it)");
        assert!(ult.contains(&format!("\"amount\": {HEAL},")) && ult.contains(&format!("\"ap_ratio\": {HEAL_AP},")),
                "the main pack's Wish is no longer {HEAL} + {HEAL_AP}% AP: update HEAL / HEAL_AP");
        assert_eq!(v.matches("league_soraka:wish").count(), 1);
        assert!(ult.contains("description.league_soraka_addon.ult"));
    }
}
