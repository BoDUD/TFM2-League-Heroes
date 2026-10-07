//! 剑姬附加包：大招「无双挑战」的破绽只在被挑战的那个英雄身上（用户：「做附加包吧」）。
//!
//! 主包保持纯数据：数据分不清一次攻击打中的是谁，大招的 4 处破绽只能记在剑姬自己身上（`league_fiora_r_v4`..`r_v1`），
//! 大招期间打中任何一个敌方英雄都会刺掉一处（模拟里 42 次有 16 次刺在别人身上）；主包只保证胜利之地落在被挑战的人脚下。
//! `mod.override_info` 把主包的剑姬换成 `override/` 里的副本（`make_override.py` 从主包生成）：
//!
//! - 开大时给被挑战的英雄挂上 `league_fiora_r_mark`（480 tick，和大招一样长）；
//! - 五处破绽判定（普攻、Q 的两下、W 的两道）先调用本包的 `league_fiora_duel:vital`（目标 = 被打中的英雄）：剑姬身上有
//!   `league_fiora_r_on`、而且这个英雄身上有 `league_fiora_r_mark`，就给剑姬加 3 tick 的 `league_fiora_r_tgt`；
//! - 数据读 `r_tgt`：有就刺大招的破绽，没有就是普通的被动破绽（League 里别的英雄身上照样会出被动破绽）。数据在同一 tick 读一次，
//!   读不到再在下一 tick 读一次（本包加的 buff 什么时候能被数据读到，游戏里还没证实过）。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_fiora_duel.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_fiora_duel";
/// 剑姬身上：大招进行中（主包的 buff）。
pub const R_ON: &str = "league_fiora_r_on";
/// 被挑战的英雄身上（副本的数据在开大时挂上）。
pub const MARK: &str = "league_fiora_r_mark";
/// 剑姬身上：这一下打中的是被挑战的人（数据读）。
pub const TGT: &str = "league_fiora_r_tgt";
/// `r_tgt` 留几 tick：数据同一 tick 读，读不到下一 tick 再读。
pub const TGT_T: usize = 3;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_FIORA_DUEL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_fiora_duel.log");
        }
    }
    PathBuf::from("league_fiora_duel.log")
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

// ===================== 判断 =====================

/// 这一下算不算大招的破绽：剑姬在大招中，打中的是挂着挑战标记的人。
pub fn is_duel_hit(r_on: bool, target_marked: bool) -> bool {
    r_on && target_marked
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn vital(sim: &mut StableSim<'_>, fiora: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    let r_on = has_buff(sim, fiora, R_ON);
    if !r_on {
        return;
    }
    let marked = has_buff(sim, target, MARK);
    if is_duel_hit(r_on, marked) {
        let mut b = BuffV1::timed(TGT, TGT_T);
        b.duration_kind = BuffDurationV1::Time.code();
        sim.add_buff(fiora, &b);
    }
    wlog(format!(
        "{} R hit on #{target}: {}",
        head(sim, fiora),
        if marked { "the challenged champion - a Vital" } else { "another champion - the passive only" }
    ));
}

struct Vital;
impl StableEffectType for Vital {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        vital(sim, caster, input);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Fiora: Grand Challenge's Vitals only on the challenged champion) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:vital"), Vital);
    host.log(LogLevel::Info, "league_fiora_duel v1 loaded (Fiora: R's Vitals only on the challenged champion).");
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
    fn only_the_challenged_champion_takes_a_vital() {
        assert!(is_duel_hit(true, true));
        assert!(!is_duel_hit(true, false));
        assert!(!is_duel_hit(false, true));
        assert!(!is_duel_hit(false, false));
    }
}
