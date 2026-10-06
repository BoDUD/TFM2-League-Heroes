//! 格温附加包：被动「千穿百孔」造成百分比最大生命值的魔法伤害（用户：「这个可以改rust」）。
//!
//! 主包保持纯数据：数据里能读最大生命值的只有真实伤害（`FixedAttack` 的 `target_hp_ratio`），读不到法强，所以主包的
//! 被动对英雄造成 `p_hp`% 最大生命值的真实伤害。`mod.override_info` 把主包的格温换成 `override/` 里的副本，只有一处
//! 不同：被动打到敌方英雄时的那段真实伤害换成原生效果 `league_gwen:cuts`——读目标的最大生命值和格温的法强，造成
//! 英雄联盟的 `P_HP`% + 每 100 法强 `P_HP_AP` / 100 % 最大生命值的**魔法伤害**（会被魔抗减免）。普攻、Q 的每一剪、
//! R 的每根针都触发（同主包），回血和附加的固定魔法伤害照旧由数据做。
//!
//! 数字是主包 tools/kit/build_gwen.py 参数表 P 的 `p_hp`、`p_hp_ap`；`make_override.py` 生成副本时核对这里的常数和
//! P 一致，不一致就停。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_gwen.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_gwen";

/// 最大生命值的这么多 %（主包 P 的 p_hp）。
pub const P_HP: u64 = 1;
/// 每 100 法强再加最大生命值的这么多万分之一（主包 P 的 p_hp_ap；英雄联盟每 100 法强 +0.6%）。
pub const P_HP_AP: u64 = 60;
/// 同一个格温至少隔这么多 tick 记一行命中日志（Q 一次剪五六下）。
const LOG_EVERY: usize = 60;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_GWEN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_gwen.log");
        }
    }
    PathBuf::from("league_gwen.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
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

/// (格温的 id, 上次记日志的 tick)。
static LAST_LOG: Mutex<Vec<(usize, usize)>> = Mutex::new(Vec::new());

fn due(caster: usize, tick: usize) -> bool {
    let mut last = LAST_LOG.lock().unwrap_or_else(|e| e.into_inner());
    match last.iter_mut().find(|(id, _)| *id == caster) {
        Some((_, t)) if tick >= *t && tick < *t + LOG_EVERY => false,
        Some((_, t)) => {
            *t = tick;
            true
        }
        None => {
            last.push((caster, tick));
            true
        }
    }
}

// ===================== 伤害 =====================

/// 万分比：`P_HP`% + 每 100 法强 `P_HP_AP` 万分之一。
pub fn ratio_bp(magic_power: usize) -> u64 {
    P_HP * 100 + P_HP_AP * magic_power as u64 / 100
}

/// 最大生命值 `max_hp` 的目标吃到的魔法伤害（减免前），至少 1。
pub fn cut_damage(max_hp: usize, magic_power: usize) -> usize {
    ((max_hp as u64 * ratio_bp(magic_power) / 10_000) as usize).max(1)
}

/// 被动打到一个敌方英雄：按他的最大生命值造成魔法伤害。
fn cuts(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        // Q's cuts are a RangeEffect's own effects (the attack's and R's come in a projectile's, as Pyke's X): no data
        // in the base game puts a Native there, so a target kind other than the unit hit is logged for the test
        if due(usize::MAX - caster, sim.tick()) {
            let line = head(sim, caster);
            wlog(format!("{line} CUTS skipped: input kind {} is not a unit", input.kind));
        }
        return;
    }
    let target = input.target_id;
    let Some(ap) = sim.get_entity(caster).map(|e| e.stat().magic_power) else { return };
    let Some((hp, max)) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
    let d = cut_damage(max, ap);
    sim.deal_damage_typed(caster, target, d, DamageTypeV1::Ap, AttackTypeV1::Skill);
    if due(caster, sim.tick()) {
        let line = head(sim, caster);
        wlog(format!(
            "{line} CUTS #{target}: hp {hp}/{max}, ap {ap} -> {}.{:02}% = {d} magic (before resistance)",
            ratio_bp(ap) / 100,
            ratio_bp(ap) % 100
        ));
    }
}

struct Cuts;
impl StableEffectType for Cuts {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        cuts(sim, caster, input);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Gwen's A Thousand Cuts: % max-health magic damage) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:cuts"), Cuts);
    host.log(LogLevel::Info, "league_gwen v1 loaded (Gwen's passive: % max-health magic damage).");
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
    fn leagues_ratio() {
        // 0 法强：1%；100 法强：1.6%；230 法强：2.38%
        assert_eq!(ratio_bp(0), 100);
        assert_eq!(ratio_bp(100), 160);
        assert_eq!(ratio_bp(230), 238);
    }

    #[test]
    fn damage_from_max_health() {
        assert_eq!(cut_damage(2000, 0), 20);
        assert_eq!(cut_damage(2000, 230), 47);
        assert_eq!(cut_damage(3000, 100), 48);
        // 再小也有 1
        assert_eq!(cut_damage(10, 0), 1);
    }

    #[test]
    fn the_log_waits_per_gwen() {
        assert!(due(7, 100));
        assert!(!due(7, 130));
        assert!(due(8, 130));
        assert!(due(7, 160));
    }
}
