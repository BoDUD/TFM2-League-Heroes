//! 安妮附加包：Q「碎裂之火」照英雄联盟击杀目标时返还一半冷却（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话
//! 全部补附加包」）。
//!
//! 主包是纯数据：引擎没有「打死了就减冷却」的效果，Q 击杀不返还。本包：副本里 Q 的两枚火球（带不带眩晕的）打中时，在伤害之后
//! 多调用一次原生效果 `league_annie_q:refund`（`input` 就是被打中的单位）：他已经死了（小兵、野怪、英雄都算），就把 Q 的
//! 剩余冷却减 `REFUND` tick（Q 冷却 240 tick 的一半），英雄联盟还返还法力，这里没有法力。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_annie_q.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_annie_q";
pub const REFUND: usize = 120;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNT: Mutex<usize> = Mutex::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ANNIE_Q_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_annie_q.log");
        }
    }
    PathBuf::from("league_annie_q.log")
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

// ===================== 返还 =====================

/// Did this hit kill him? (hp 0 or not alive any more)
pub fn killed(alive: bool, hp: usize) -> bool {
    !alive || hp == 0
}

struct Refund;

impl StableEffectType for Refund {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let id = input.target_id;
        let Some((alive, hp, champ)) = sim.get_entity(id).map(|e| (e.is_alive(), e.hp().0, e.is_champion())) else { return };
        if !killed(alive, hp) {
            return;
        }
        let left = sim.get_entity(caster).and_then(|e| e.cooldown(SkillSlotV1::Skill)).map_or(0, |c| c.remaining);
        sim.entity_reduce_cooldown(caster, SkillSlotV1::Skill, REFUND);
        if let Some(k) = counted() {
            wlog(format!("{} Q KILL #{k} on #{id}{}: cooldown {left} -> {}", head(sim, caster),
                         if champ { " (champion)" } else { "" }, left.saturating_sub(REFUND)));
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Annie's Disintegrate refunds half its cooldown on a kill) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:refund"), Refund);
    host.log(LogLevel::Info, "league_annie_q v1 loaded (Disintegrate refunds half its cooldown on a kill).");
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
    fn a_kill_is_no_life_left() {
        assert!(killed(false, 100));
        assert!(killed(true, 0));
        assert!(!killed(true, 1));
    }
}
