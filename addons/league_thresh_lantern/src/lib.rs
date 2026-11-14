//! 锤石附加包：W「魂引之灯」照英雄联盟把有危险的队友拉回来（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话
//! 全部补附加包」）。
//!
//! 主包是纯数据：引擎做不了「队友点灯笼」，灯笼飞向 50000 内一名随机友方英雄，只给护盾。英雄联盟里锤石把灯笼扔给挨打的
//! 队友，队友点一下就被拉到锤石身边。本包：副本里那段随机挑人换成原生效果 `league_thresh_lantern:throw`——
//!
//! - **挑谁**：`REACH` 内的友方英雄（不含锤石），先挑有危险的（生命不高于 `LOW`%、或身边 `CROWD_R` 内有 `CROWD` 个以上
//!   敌方英雄），几个时挑生命比例最低的；都没危险就挑最近的。
//! - **灯笼**：主包的灯笼（`league_thresh_w_lantern`）飞过去，到了由 `league_thresh_lantern:land` 给他主包那份护盾
//!   （60 + 40% 锤石法强，2.5 秒，护盾画面 `league_thresh_w_shield`、声音）。
//! - **拉回来**：他有危险、离锤石超过 `NEAR`、没被硬控时，把他拉到锤石身边（`entity_pull`，每 tick `PULL_SPEED`）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_thresh_lantern.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_thresh_lantern";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_thresh_lantern") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const LANTERN: &str = "league_thresh_w_lantern";
pub const SHIELD_VIEW: &str = "league_thresh_w_shield";
pub const SHIELD_SFX: &str = "league_thresh_w_shield";
/// 灯笼扔多远（主包的 `RandomTarget` 是 50000）、飞多快（主包 5000）。
pub const REACH: f64 = 50_000.0;
pub const SPEED: u64 = 5_000;
/// 主包的护盾：60 + 40% 法强，150 tick。
pub const SHIELD: usize = 60;
pub const SHIELD_AP: usize = 40;
pub const SHIELD_TICKS: usize = 150;
pub const LOW: usize = 45;
pub const CROWD: usize = 2;
pub const CROWD_R: f64 = 25_000.0;
/// 离锤石这么近就不拉；拉到离他这么近停下。
pub const NEAR: f64 = 15_000.0;
pub const STOP: f64 = 8_000.0;
pub const PULL_SPEED: usize = 3_000;
const MAP: f64 = 960_000.0;
const HARD_CC: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                                CcKindV1::Charm, CcKindV1::ForceMove];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNT: Mutex<usize> = Mutex::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_THRESH_LANTERN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_thresh_lantern.log");
        }
    }
    PathBuf::from("league_thresh_lantern.log")
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

/// Log the first 120 and every 25th after.
fn counted() -> Option<usize> {
    let mut n = COUNT.lock().unwrap_or_else(|e| e.into_inner());
    *n += 1;
    (*n <= 120 || *n % 25 == 0).then_some(*n)
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

// ===================== 挑人 =====================

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// An ally in reach: id, where, hp, max, enemy champions within `CROWD_R`.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Ally {
    pub id: usize,
    pub at: Pt,
    pub hp: usize,
    pub max: usize,
    pub crowd: usize,
}

impl Ally {
    pub fn danger(&self) -> bool {
        self.hp * 100 <= LOW * self.max.max(1) || self.crowd >= CROWD
    }
}

/// Whom the lantern goes to: the one in danger with the lowest health share, else the nearest to Thresh at `me`.
pub fn pick(me: Pt, allies: &[Ally]) -> Option<Ally> {
    let share = |a: &Ally| a.hp * 1000 / a.max.max(1);
    allies.iter().filter(|a| a.danger()).min_by_key(|a| share(a)).copied()
        .or_else(|| allies.iter().min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at))).copied())
}

/// Ticks to pull an ally from `d` away to `STOP` from Thresh (0: no pull).
pub fn pull_ticks(d: f64) -> usize {
    if d <= NEAR {
        return 0;
    }
    ((d - STOP) / PULL_SPEED as f64).ceil().max(1.0) as usize
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn upos(p: Pt) -> (u64, u64) {
    (p.0.round().clamp(0.0, MAP - 1.0) as u64, p.1.round().clamp(0.0, MAP - 1.0) as u64)
}

fn hard_cc(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
}

fn read_allies(sim: &StableSim<'_>, me: usize) -> Option<(Pt, Vec<Ally>)> {
    let e = sim.get_entity(me)?;
    let (team, at) = (e.team(), pos(&e));
    let units: Vec<_> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_champion() && u.is_alive()).collect();
    let allies = units.iter()
        .filter(|u| u.team() == team && u.id() != me && u.is_targetable() && dist(at, pos(u)) <= REACH)
        .map(|u| Ally {
            id: u.id(),
            at: pos(u),
            hp: u.hp().0,
            max: u.hp().1,
            crowd: units.iter().filter(|f| f.team() != team && dist(pos(u), pos(f)) <= CROWD_R).count(),
        })
        .collect();
    Some((at, allies))
}

// ===================== 原生效果 =====================

struct Throw;

impl StableEffectType for Throw {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _input: InputTargetV1) {
        let Some((at, allies)) = read_allies(sim, caster) else { return };
        let Some(a) = pick(at, &allies) else { return };
        let Some(team) = sim.get_entity(caster).map(|e| e.team()) else { return };
        let (x, y) = upos(at);
        let spec = ProjectileSpawnV1 {
            caster_id: caster,
            team,
            x,
            y,
            radius: 1_000,
            speed: SPEED,
            move_kind: ProjectileMoveKindV1::Target.code(),
            target_id: a.id,
            target_x: 0,
            target_y: 0,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::AllyChampion.code(),
        };
        let flew = sim.spawn_projectile(LANTERN, &format!("{ID}:land"), &spec);
        if let Some(k) = counted() {
            wlog(format!("{} LANTERN #{k} -> #{} (hp {}/{}, {} enemies around, {:.0} away){}{}", head(sim, caster), a.id, a.hp,
                         a.max, a.crowd, dist(at, a.at), if a.danger() { " IN DANGER" } else { "" },
                         if flew { "" } else { " (spawn_projectile refused)" }));
        }
    }
}

struct Land;

impl StableEffectType for Land {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let id = input.target_id;
        let Some(me) = sim.get_entity(caster) else { return };
        let (power, at, alive) = (me.stat().magic_power, pos(&me), me.is_alive());
        let Some((_, allies)) = read_allies(sim, caster) else { return };
        let Some(a) = sim.get_entity(id).filter(|e| e.is_alive()) else { return };
        let (held, there) = (hard_cc(&a), pos(&a));
        sim.entity_add_shield(id, SHIELD + power * SHIELD_AP / 100, SHIELD_TICKS);
        let mut view = BuffV1::named(SHIELD_VIEW);
        view.duration_kind = BuffDurationV1::WithShield.code();
        sim.add_buff(id, &view);
        sim.play_sfx(SHIELD_SFX, caster, &InputTargetV1::target(id));
        let danger = allies.iter().find(|x| x.id == id).is_some_and(|x| x.danger());
        let ticks = if danger && alive && !held { pull_ticks(dist(at, there)) } else { 0 };
        let pulled = ticks > 0 && sim.entity_pull(caster, id, PULL_SPEED, ticks);
        if let Some(k) = counted() {
            wlog(format!("{} LANDED #{k} on #{id}: shield {}{}", head(sim, caster), SHIELD + power * SHIELD_AP / 100,
                         if pulled { format!(", pulled {:.0} in {ticks} ticks", dist(at, there)) }
                         else if danger { format!(", not pulled ({})", if held { "held" } else if !alive { "Thresh dead" } else { "near" }) }
                         else { String::new() }));
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Thresh's lantern to the ally in danger, who is pulled to him) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:throw"), Throw);
    module.add_native_effect(format!("{ID}:land"), Land);
    host.log(LogLevel::Info, "league_thresh_lantern v1 loaded (Dark Passage pulls the ally in danger).");
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

    fn a(id: usize, x: f64, hp: usize, crowd: usize) -> Ally {
        Ally { id, at: (x, 0.0), hp, max: 1000, crowd }
    }

    #[test]
    fn the_lantern_goes_to_the_ally_in_danger_else_the_nearest() {
        assert_eq!(pick((0.0, 0.0), &[a(1, 10_000.0, 900, 0), a(2, 40_000.0, 400, 0), a(3, 30_000.0, 300, 0)]).map(|x| x.id),
                   Some(3));
        assert_eq!(pick((0.0, 0.0), &[a(1, 10_000.0, 900, 0), a(2, 40_000.0, 800, 2)]).map(|x| x.id), Some(2));
        assert_eq!(pick((0.0, 0.0), &[a(1, 30_000.0, 900, 0), a(2, 20_000.0, 800, 1)]).map(|x| x.id), Some(2));
        assert_eq!(pick((0.0, 0.0), &[]), None);
    }

    #[test]
    fn far_allies_are_pulled_near_ones_not() {
        assert_eq!(pull_ticks(10_000.0), 0);
        assert_eq!(pull_ticks(44_000.0), 12);
    }
}
