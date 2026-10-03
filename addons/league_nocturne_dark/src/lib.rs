//! 魔腾黑暗附加包 v2：R「鬼影重重」——全地图变暗，敌人只能看见身边。
//!
//! 主包里魔腾的 R 让己方所有英雄隐身 3 秒、敌方英雄头上一团黑雾，再飞扑一名敌方英雄。
//! `mod.override_info` 把主包的魔腾换成 `override/` 里的副本：那条「全体隐身 180 tick」换成本包的
//! 原生效果 `start`，别的（黑雾、飞扑、伤害、画面、声音）照旧。
//!
//! - 模拟里（`start` + 每 tick 的 `tick`，`DARK_T` tick）：魔腾一方的每个英雄，`NEAR` 内没有敌方英雄
//!   时隐身 2 tick（每 tick 续上），有敌人贴近就现身——League 里被黑暗笼罩的人视野缩到身边，
//!   本作没有按队伍改视野的接口，用「贴近才看得见」来做。
//! - 画面：R 出手时在地图中心播 `VEIL_LAYERS` 层铺满整张地图的半透明暗色（`VEIL`，副本里加的特效，
//!   贴图在 `effects/`），错开 `VEIL_STEP` tick 叠上去，各播 3 秒，所以渐入、渐出。特效画在单位下面
//!   （z −2）：地面变黑，英雄和技能特效照样看得清。它是普通的特效事件，跟着比赛画面同步播。
//!   （v1 用客户端每帧叠一层暗色、跟着模拟的「黑暗还在」走；可游戏先在后台快速算完比赛再按正常
//!   速度播给你看，暗色和画面对不上，不放大也一闪一闪地黑——已去掉。）
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nocturne_dark.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_nocturne_dark";

/// 黑暗时长（同主包的隐身 180 tick）。
pub const DARK_T: usize = 180;
/// 敌方英雄这么近才看得见魔腾一方的英雄。
pub const NEAR: f64 = 40_000.0;
/// 每 tick 续的隐身时长。
const VEIL_T: usize = 2;
/// 魔腾身上的标记：黑暗还在。
const ON: &str = "league_nocturne_dark_on";

/// 铺满地图的暗色特效（副本的 view_effects 里加的，贴图 `effects/league_nocturne_dark`）、播在哪（地图中心）、
/// 叠几层、每层隔几 tick。
pub const VEIL: &str = "league_nocturne_dark_veil";
pub const MAP_CENTER: (u64, u64) = (480_000, 480_000);
pub const VEIL_LAYERS: usize = 3;
pub const VEIL_STEP: usize = 4;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_NOCTURNE_DARK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_nocturne_dark.log");
        }
    }
    PathBuf::from("league_nocturne_dark.log")
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
    let label = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{label} m={} s={}] t={} nocturne#{id}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 模拟：贴近才看得见 =====================

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 这一 tick 要隐身的己方英雄：`NEAR` 内没有敌方英雄的。
pub fn to_hide(allies: &[(usize, (f64, f64))], enemies: &[(f64, f64)]) -> Vec<usize> {
    allies.iter().filter(|(_, at)| enemies.iter().all(|e| dist(*at, *e) > NEAR)).map(|(id, _)| *id).collect()
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).any(|i| e.buff_at(i).is_some_and(|b| b.name() == name)))
}

/// 隐身 `NEAR` 外的己方英雄；返回 (隐身的, 己方总数)。
fn veil(sim: &mut StableSim<'_>, nocturne: usize) -> (usize, usize) {
    let team = sim.get_entity(nocturne).map_or(0, |e| e.team());
    let mut allies = Vec::new();
    let mut enemies = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if !e.is_champion() || !e.is_alive() {
            continue;
        }
        let (x, y) = e.pos();
        if e.team() == team {
            allies.push((e.id(), (x as f64, y as f64)));
        } else {
            enemies.push((x as f64, y as f64));
        }
    }
    let hide = to_hide(&allies, &enemies);
    for id in &hide {
        sim.entity_set_invisible(*id, VEIL_T);
    }
    (hide.len(), allies.len())
}

fn queue(sim: &mut StableSim<'_>, step: &str, nocturne: usize, delay: usize) {
    let name = format!("{ID}:{step}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, nocturne, &InputTargetV1::target(nocturne), delay) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, nocturne)));
    }
}

/// 在地图中心播一层暗色。
fn dark_layer(sim: &mut StableSim<'_>, nocturne: usize) {
    let at = InputTargetV1::pos(MAP_CENTER.0, MAP_CENTER.1);
    sim.play_view_effect(VEIL, nocturne, &at, 0, 0, 0);
}

/// R 出手：黑暗 `DARK_T` tick，画面暗色叠 `VEIL_LAYERS` 层。
fn start(sim: &mut StableSim<'_>, nocturne: usize) {
    sim.entity_remove_buff(nocturne, ON);
    sim.add_buff(nocturne, &BuffV1::timed(ON, DARK_T));
    let (hidden, allies) = veil(sim, nocturne);
    dark_layer(sim, nocturne);
    for k in 1..VEIL_LAYERS {
        queue(sim, "layer", nocturne, k * VEIL_STEP);
    }
    queue(sim, "tick", nocturne, 1);
    wlog(format!("{} DARKNESS for {DARK_T} ticks: {hidden} of {allies} allies unseen", head(sim, nocturne)));
}

/// 每 tick：黑暗还在就重新隐身（贴近的敌人看得见），没了就结束。
fn tick(sim: &mut StableSim<'_>, nocturne: usize) {
    if !has_buff(sim, nocturne, ON) {
        wlog(format!("{} darkness over", head(sim, nocturne)));
        return;
    }
    veil(sim, nocturne);
    queue(sim, "tick", nocturne, 1);
}

// ===================== 注册 =====================

struct Start;
impl StableEffectType for Start {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        start(sim, caster);
    }
}

struct Tick;
impl StableEffectType for Tick {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        tick(sim, caster);
    }
}

struct Layer;
impl StableEffectType for Layer {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        dark_layer(sim, caster);
    }
}

fn init(host: &StableHost) -> StableMod {
    // 上一次启动的日志留一份（.prev.log），重启游戏不丢
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v2 (Paranoia darkness, map veil effect) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    let mut module = StableMod::new(ID);
    module.add_native_effect(format!("{ID}:start"), Start);
    module.add_native_effect(format!("{ID}:tick"), Tick);
    module.add_native_effect(format!("{ID}:layer"), Layer);
    host.log(LogLevel::Info, "league_nocturne_dark v2 loaded (Nocturne's R darkens the map).");
    module
}

declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn only_allies_with_an_enemy_close_are_seen() {
        let allies = [(1, (100_000.0, 100_000.0)), (2, (300_000.0, 300_000.0)), (3, (500_000.0, 500_000.0))];
        let enemies = [(130_000.0, 100_000.0), (500_000.0, 545_000.0)];
        // #1 有敌人在 30000 内：看得见；#3 的敌人在 45000：看不见
        assert_eq!(to_hide(&allies, &enemies), [2, 3]);
        assert_eq!(to_hide(&allies, &[]), [1, 2, 3]);
    }
}
