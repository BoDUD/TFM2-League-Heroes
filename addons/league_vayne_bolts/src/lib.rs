//! 薇恩附加包：圣银弩箭数的是「同一个目标」挨的连续 3 下（用户：「薇恩也顺便做了」）。
//!
//! 主包保持纯数据：数据分不清一次攻击打中的是谁，圣银弩箭的两层（`league_vayne_sb1` / `sb2`）记在薇恩自己身上，
//! 她轮流打两个人也会凑满 3 下，在第三个被打中的人身上爆。`mod.override_info` 把主包的薇恩换成 `override/` 里的副本
//! （`make_override.py` 从主包生成）：每一处圣银弩箭的判定（普攻、翻滚后的强化普攻、恶魔审判）先调用本包的
//! `league_vayne_bolts:bolt`（目标 = 被打中的单位），本包数**这个单位身上**的层数（`league_vayne_bolts_s`，每层 210 tick，
//! 每次命中刷新）：
//!
//! - 原来 0 层：挂 1 层，给薇恩加 `league_vayne_sb_r1`（数据播一环）；
//! - 原来 1 层：变 2 层，加 `league_vayne_sb_r2`（数据播两环）；
//! - 原来 2 层：清掉，加 `league_vayne_sb_go`（数据打出真实伤害和第三环的爆裂；英雄再加最大生命值的那部分）。
//!
//! 标志都留 3 tick，数据同一 tick 读一次，读不到在下一 tick 再读一次（本包加的 buff 什么时候能被数据读到，游戏里还没证实过）。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_vayne_bolts.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_vayne_bolts";
/// 目标身上的层（每层一个 buff 实例）。
pub const STACK: &str = "league_vayne_bolts_s";
/// 层留多久（League 3 秒；主包的计数是 210 tick）。
pub const STACK_T: usize = 210;
/// 薇恩身上给数据读的标志。
pub const RING1: &str = "league_vayne_sb_r1";
pub const RING2: &str = "league_vayne_sb_r2";
pub const GO: &str = "league_vayne_sb_go";
pub const FLAG_T: usize = 3;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VAYNE_BOLTS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_vayne_bolts.log");
        }
    }
    PathBuf::from("league_vayne_bolts.log")
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

/// 这一下之后：目标身上剩几层，薇恩身上加哪个标志。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Bolt {
    Ring1,
    Ring2,
    Proc,
}

/// 目标原来有 `stacks` 层时这一下的结果（2 层以上 = 第三下）。
pub fn next(stacks: usize) -> (Bolt, usize) {
    match stacks {
        0 => (Bolt::Ring1, 1),
        1 => (Bolt::Ring2, 2),
        _ => (Bolt::Proc, 0),
    }
}

fn stacks_on(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == STACK).count())
}

fn bolt(sim: &mut StableSim<'_>, vayne: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
        return;
    }
    let had = stacks_on(sim, target);
    let (what, keep) = next(had);
    // 每次命中刷新：去掉旧的层，按新层数重新挂上
    sim.entity_remove_buff(target, STACK);
    for _ in 0..keep {
        sim.add_buff(target, &BuffV1::timed(STACK, STACK_T));
    }
    let flag = match what {
        Bolt::Ring1 => RING1,
        Bolt::Ring2 => RING2,
        Bolt::Proc => GO,
    };
    sim.add_buff(vayne, &BuffV1::timed(flag, FLAG_T));
    wlog(format!("{} bolt on #{target}: {had} stack(s) before -> {what:?}", head(sim, vayne)));
}

struct BoltFx;
impl StableEffectType for BoltFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        bolt(sim, caster, input);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Vayne: Silver Bolts counted on each target) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:bolt"), BoltFx);
    host.log(LogLevel::Info, "league_vayne_bolts v1 loaded (Vayne: Silver Bolts counted on each target).");
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
    fn the_third_hit_on_one_target_procs() {
        assert_eq!(next(0), (Bolt::Ring1, 1));
        assert_eq!(next(1), (Bolt::Ring2, 2));
        assert_eq!(next(2), (Bolt::Proc, 0));
        // three hits in a row on one target
        let mut s = 0;
        let mut out = vec![];
        for _ in 0..3 {
            let (b, k) = next(s);
            out.push(b);
            s = k;
        }
        assert_eq!(out, vec![Bolt::Ring1, Bolt::Ring2, Bolt::Proc]);
        assert_eq!(s, 0);
    }
}
