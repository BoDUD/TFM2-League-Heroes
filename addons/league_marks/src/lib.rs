//! 目标标记附加包：读敌人身上的标记，照英雄联盟做「只对带标记的那个目标」的效果（用户 2026-10-24：「查看现在没有做附加包的
//! 英雄有明显不一样的话全部补附加包」）。
//!
//! 主包是纯数据：`SwitchByBuff` 只读得到施放者自己身上的 buff，读不到目标身上的，所以「目标带不带标记」都改成了「她自己最近
//! 有没有打中过」。原生代码读得到每个单位的 buff。`mod.override_info` 换上的副本（`make_override.py` 从主包生成）在要判断
//! 的那一下给目标挂一个短的「问」标记，本包看那个目标身上有没有主包的标记，把答案挂在施放者身上让数据读：
//!
//! - **黛安娜 `league_marks:diana`**：E「月光冲击」冲向的目标身上有月光（主包 Q 挂的 `league_diana_moon_mark`）时，才挂
//!   `league_diana_moonlit`，数据读到就立刻再冲一次；同时把所有敌人身上的月光去掉（英雄联盟：冲到带月光的目标会消耗全部
//!   月光）。主包是 Q 打中过任何东西就能再冲。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_marks.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_marks";
pub const DIANA_MOON: &str = "league_diana_moon_mark";
pub const DIANA_ASK: &str = "league_marks_diana_e";
pub const DIANA_YES: &str = "league_diana_moonlit";
/// 答案挂多久（数据隔 2 tick 来读）。
pub const ANSWER: usize = 4;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_MARKS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_marks.log");
        }
    }
    PathBuf::from("league_marks.log")
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

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// Enemies of `team` alive with `name` on them.
fn enemies_with(sim: &StableSim<'_>, team: usize, name: &str) -> Vec<usize> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.team() != team && e.is_alive() && has(e, name))
        .map(|e| e.id())
        .collect()
}

// ===================== 黛安娜 =====================

#[derive(Clone, Default)]
struct Diana {
    asked: usize,
    yes: usize,
}

impl StablePassive for Diana {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        wlog(format!("{} SPAWN: the add-on's Diana (player {player})", head(sim, me)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        for target in enemies_with(sim, team, DIANA_ASK) {
            sim.entity_remove_buff(target, DIANA_ASK);
            self.asked += 1;
            let moonlit = sim.get_entity(target).is_some_and(|e| has(&e, DIANA_MOON));
            if moonlit {
                self.yes += 1;
                sim.entity_remove_buff(me, DIANA_YES);
                sim.add_buff(me, &BuffV1::timed(DIANA_YES, ANSWER));
                for lit in enemies_with(sim, team, DIANA_MOON) {
                    sim.entity_remove_buff(lit, DIANA_MOON);
                }
            }
            if self.asked <= 80 {
                wlog(format!("{} DIANA E #{} on #{target}: {} ({} of {} moonlit)", head(sim, me), self.asked,
                             if moonlit { "moonlit, dash again" } else { "no moonlight" }, self.yes, self.asked));
            }
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (marks read on the target: Diana) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:diana"), Diana::default());
    host.log(LogLevel::Info, "league_marks v1 loaded (marks read on the target).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_names_fit() {
        for n in [DIANA_MOON, DIANA_ASK, DIANA_YES] {
            assert!(n.len() <= BUFF_NAME_CAP);
        }
    }
}
