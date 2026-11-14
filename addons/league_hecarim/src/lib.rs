//! 赫卡里姆附加包：暴走的层数按英雄联盟缩短 Q 的冷却（用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」，
//! 再说「接着做」：能做的小项都做）。
//!
//! 英雄联盟的暴走（Q）：命中后得一层（V26.03：最多 3 层），每层让暴走的冷却缩短 0.75 秒（4 秒 → 满层 1.75 秒）。主包是纯
//! 数据：数据缩短冷却只有 `skill_cooldown_mult` 一种，它把毁灭冲锋（技能 2）的冷却也一起砍了，所以层数只加伤害（最多 2 层，
//! 每层 +20%）。
//!
//! `mod.override_info` 把主包的赫卡里姆换成 `override/` 里的副本（`make_override.py` 从 `tools/kit/build_hecarim.py` 生成，先核对
//! 参数表和主包一字不差）：技能一字不改，只加本包的被动 `league_hecarim:rampage`，暴走的说明换成本包的。被动每 tick 读他技能
//! （暴走）的冷却：跳起来了（他刚放了暴走）就看他这时身上的层数（主包的旗子 `league_hecarim_q1` 一层、`league_hecarim_q2`
//! 两层），用 `entity_reduce_cooldown` 只把暴走这一格的冷却减掉 `CUT` × 层数（每层 0.75 秒，冲锋不动）。层数按放的那一刻算
//! （这一下打中得的那层算到下一次）。落地回旋（R、E -> R 的那一下暴走）不进冷却，也就不减。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_hecarim.log`，每次启动游戏重写，上一次的留在 .prev.log：`SPAWN`、
//! `RAMPAGE`（放暴走时几层、冷却减到多少），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_hecarim";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_hecarim") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 主包的暴走层数旗子：一层、两层（`build_hecarim.py` 的 q1、q2，同时只有一个）。
pub const STACK_1: &str = "league_hecarim_q1";
pub const STACK_2: &str = "league_hecarim_q2";
/// 每层缩短的冷却（英雄联盟 0.75 秒）。
pub const CUT: usize = 45;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_HECARIM_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_hecarim.log");
        }
    }
    PathBuf::from("league_hecarim.log")
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
const LOG_EVERY: usize = 200;

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

/// 暴走刚放出去：上一 tick 的剩余冷却 `was`、这一 tick 的 `now`（跳高 5 tick 以上才算，冷却本来就在走的不算）。
pub fn cast(was: usize, now: usize) -> bool {
    now > was + 5
}

/// 他身上的旗子对应几层（两层的旗子在就是两层）。
pub fn stacks(has_1: bool, has_2: bool) -> usize {
    if has_2 {
        2
    } else {
        usize::from(has_1)
    }
}

/// 这么多层减掉多少冷却。
pub fn cut_for(stacks: usize) -> usize {
    CUT * stacks
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Rampage {
    /// 上一 tick 暴走的剩余冷却。
    last: usize,
}

impl StablePassive for Rampage {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.last = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Skill)).map_or(0, |c| c.remaining);
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Hecarim (player {player})", head(sim, me)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((cd, n)) = sim.get_entity(me).filter(|e| e.is_alive()).and_then(|e| {
            let n = stacks(has_buff(&e, STACK_1), has_buff(&e, STACK_2));
            e.cooldown(SkillSlotV1::Skill).map(|c| (c.remaining, n))
        }) else {
            return;
        };
        let was = std::mem::replace(&mut self.last, cd);
        if !cast(was, cd) || n == 0 {
            return;
        }
        let cut = cut_for(n);
        let ok = sim.entity_reduce_cooldown(me, SkillSlotV1::Skill, cut);
        let after = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Skill)).map_or(cd, |c| c.remaining);
        self.last = after;
        if let Some(k) = counted("rampage") {
            wlog(format!("{} RAMPAGE #{k}: {n} stacks, cooldown {cd} -> {after} (-{cut}){}", head(sim, me),
                         if ok { "" } else { " (refused)" }));
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
        "=== {ID} v{VERSION} (Hecarim: each Rampage stack takes {CUT} ticks off its cooldown) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:rampage"), Rampage::default());
    host.log(LogLevel::Info, "league_hecarim loaded (Rampage's cooldown shorter for each stack).");
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
    fn a_cast_is_a_jump_of_the_cooldown() {
        assert!(cast(0, 240));
        assert!(cast(3, 240), "cast again the tick it came back");
        assert!(!cast(100, 99), "running down");
        assert!(!cast(0, 0));
        assert!(!cast(10, 15), "5 ticks or less is no cast");
    }

    #[test]
    fn each_stack_takes_three_quarters_of_a_second() {
        assert_eq!(stacks(false, false), 0);
        assert_eq!(stacks(true, false), 1);
        assert_eq!(stacks(false, true), 2);
        assert_eq!(stacks(true, true), 2, "the two-stack flag decides");
        assert_eq!(cut_for(1), 45);
        assert_eq!(cut_for(2), 90);
        // the main pack's 4 s Rampage: 3.25 s with one stack, 2.5 s with two (League: 1.75 s at its three)
        assert_eq!(240 - cut_for(2), 150);
    }

    #[test]
    fn the_copy_is_the_main_pack_with_the_passive() {
        let copy = include_str!("../override/league_hecarim.data_champion").replace("\r\n", "\n");
        assert!(copy.contains("\"passive_ref\": \"league_hecarim:rampage\""), "the copy has no league_hecarim:rampage passive");
        for f in [STACK_1, STACK_2] {
            assert!(copy.contains(&format!("\"name\": \"{f}\"")), "the main pack's Rampage stack {f} is gone: update STACK_1 / STACK_2");
        }
        assert!(copy.contains("description.league_hecarim_addon.skill"));
    }
}
