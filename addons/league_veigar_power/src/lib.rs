//! 维迦附加包：被动「超凡邪力」叠的法术强度死了也不掉，和英雄联盟一样（用户：「顺便帮小法做一个 永久叠法强的」）。
//!
//! 主包保持纯数据：每一层是维迦身上一个永久的 `league_veigar_p_stack`（法术强度 +1，击杀英雄那一层 +5）。引擎在他死亡时清掉
//! 身上全部 buff，数据也没有「复活时」这个时机，所以主包里法强每条命从零叠起（说明里写着「死亡时清空」）。
//! `mod.override_info` 把主包的维迦换成 `override/` 里的副本：技能一字不改，只加了本包的被动 `league_veigar_power:keep`，
//! 它每 tick 看一次：
//!
//! - **活着**：把身上每一层 `league_veigar_p_stack` 原样记下来（记在被动里，被动在玩家身上，死了不丢）；
//! - **少了**（死亡或复活时引擎清掉）：缺的层原样补回（同样的数值）。死着的时候也补，倒下时数值不掉。
//!
//! 层数只会变多（主包从不去掉一层），所以「身上比记下的少」只会是死亡清掉的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_veigar_power.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_veigar_power";
/// 主包的一层法强。
pub const STACK: &str = "league_veigar_p_stack";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VEIGAR_POWER_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_veigar_power.log");
        }
    }
    PathBuf::from("league_veigar_power.log")
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

// ===================== 计算 =====================

/// `kept` 里有、`have` 里没有的那些层（按完整的数值配对）。
pub fn missing(kept: &[BuffV1], have: &[BuffV1]) -> Vec<BuffV1> {
    let mut left: Vec<Option<&BuffV1>> = have.iter().map(Some).collect();
    let mut out = Vec::new();
    for k in kept {
        match left.iter_mut().find(|h| h.is_some_and(|h| h == k)) {
            Some(slot) => *slot = None,
            None => out.push(*k),
        }
    }
    out
}

fn buffs_named(sim: &StableSim<'_>, id: usize, name: &str) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).collect()
    })
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Keep {
    /// 这一局他叠到的每一层法强（活着时在身上看到的）。
    kept: Vec<BuffV1>,
    /// 上一 tick 他活着：死了 / 复活的那一刻记一行日志。
    was_alive: bool,
}

impl StablePassive for Keep {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let alive = e.is_alive();
        if alive != self.was_alive {
            wlog(format!("{} {} with {} stacks kept", head(sim, me), if alive { "ALIVE" } else { "DEAD" }, self.kept.len()));
            self.was_alive = alive;
        }
        let have = buffs_named(sim, me, STACK);
        let gone = missing(&self.kept, &have);
        if gone.is_empty() {
            if alive && have.len() > self.kept.len() {
                self.kept = have;
            }
            return;
        }
        for b in &gone {
            sim.add_buff(me, b);
        }
        wlog(format!(
            "{} KEEP {} stacks put back ({}), {} in all",
            head(sim, me),
            gone.len(),
            if alive { "alive" } else { "dead" },
            self.kept.len()
        ));
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Veigar: Phenomenal Evil Power kept through death) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:keep"), Keep::default());
    host.log(LogLevel::Info, "league_veigar_power v1 loaded (Veigar: ability power stacks kept through death).");
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

    fn stack() -> BuffV1 {
        let mut b = BuffV1::named(STACK);
        b.magic_power = 1;
        b
    }

    #[test]
    fn nothing_missing_while_he_keeps_them() {
        let kept = vec![stack(); 7];
        assert!(missing(&kept, &vec![stack(); 7]).is_empty());
        assert!(missing(&kept, &vec![stack(); 9]).is_empty());
    }

    #[test]
    fn a_death_puts_every_stack_back() {
        let kept = vec![stack(); 92];
        let back = missing(&kept, &[]);
        assert_eq!(back.len(), 92);
        assert!(back.iter().all(|b| b.name() == STACK && b.magic_power == 1));
        assert_eq!(missing(&kept, &vec![stack(); 90]).len(), 2);
    }
}
