//! 赵信附加包：R「新月护卫」之后 3 秒，挡住远处来的伤害（英雄联盟：免疫 450 码外敌人的伤害）。
//!
//! 主包保持纯数据：数据读不到伤害来自多远，主包的 R 之后 3 秒受到的伤害降低 40%（用户选的）。用户：「读不到多远就改
//! rust源代码 看看能不能」——这个附加包用原生代码读攻击者的位置：`mod.override_info` 把主包的赵信换成 `override/` 里的副本
//! （R 的护卫 buff `league_xinzhao_r_guard` 去掉 40% 减伤，只留画面和计时；`passive` 换成本包的 `league_xinzhao_guard:guard`），
//! 被动在他挨打时（`on_damaged`）看：护卫 buff 还在、攻击者离他超过 `far`（36000，英雄联盟的 450 码），这一下的伤害原样加回去。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从 tools/kit/build_xinzhao.py 的参数表 P 写进去），本包不另记一份。
//! 只有单元测试（经典 SDK 跑不了原生代码）：`on_damaged` 是在扣血之后调的，一下就致命的远程伤害可能来不及挡，要在游戏里看日志。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_xinzhao_guard.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_xinzhao_guard";
const GUARD: &str = "league_xinzhao_r_guard";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_XINZHAO_GUARD_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_xinzhao_guard.log");
        }
    }
    PathBuf::from("league_xinzhao_guard.log")
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 攻击者离他超过这么远（距离单位，中心到中心），伤害挡掉。
    pub far: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { far: 36_000 }
    }
}

/// `{"far":36000}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        if k == "far" {
            p.far = v;
        }
    }
    p
}

// ===================== 判断 =====================

/// 这一下要不要挡：护卫还在，伤害大于 0，攻击者不是他自己，离他比 `far` 远。
pub fn blocks(p: &Params, guarded: bool, damage: usize, self_hit: bool, dist_sq: u64) -> bool {
    let far = p.far as u64;
    guarded && damage > 0 && !self_hit && dist_sq > far.saturating_mul(far)
}

/// 挡掉以后的生命：加回这一下，不超过上限。
pub fn refunded(now: usize, max: usize, damage: usize) -> usize {
    now.saturating_add(damage).min(max)
}

fn guarded(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == GUARD))
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Guard {
    p: Params,
}

impl StablePassive for Guard {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let (now, max) = e.hp();
        let dist_sq = sim.distance_sq(me, attacker);
        if !blocks(&self.p, guarded(sim, me), damage, attacker == me, dist_sq) {
            return;
        }
        let hp = refunded(now, max, damage);
        sim.entity_set_hp(me, hp);
        wlog(format!(
            "{} BLOCK {damage} from #{attacker} at {:.0} (far {}): hp {now} -> {hp}/{max}",
            head(sim, me),
            (dist_sq as f64).sqrt(),
            self.p.far
        ));
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Crescent Guard blocks the damage from afar) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:guard"), Guard::default());
    host.log(LogLevel::Info, "league_xinzhao_guard v1 loaded (Xin Zhao's R blocks the damage from afar).");
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
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"far":30000,"unknown":4}"#).far, 30_000);
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn only_the_far_hits_while_guarded() {
        let p = Params::default();
        let far2 = 40_000u64 * 40_000;
        let near2 = 20_000u64 * 20_000;
        assert!(blocks(&p, true, 80, false, far2));
        assert!(!blocks(&p, true, 80, false, near2));          // the one beside him (the challenged) still hurts
        assert!(!blocks(&p, false, 80, false, far2));          // the guard is over
        assert!(!blocks(&p, true, 0, false, far2));
        assert!(!blocks(&p, true, 80, true, far2));            // his own costs
        assert!(!blocks(&p, true, 80, false, 36_000u64 * 36_000)); // exactly at the edge: not beyond it
    }

    #[test]
    fn the_refund_stops_at_full_health() {
        assert_eq!(refunded(500, 1000, 120), 620);
        assert_eq!(refunded(950, 1000, 120), 1000);
    }
}
