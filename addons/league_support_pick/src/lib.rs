//! 辅助挑人附加包：迦娜 E、娑娜 W、璐璐 E 照英雄联盟给最需要的队友（用户 2026-10-24：「查看现在没有做附加包的英雄有明显
//! 不一样的话全部补附加包」）。
//!
//! 主包是纯数据：给队友的那一下是 `RandomTarget AllyNotSelf`，随机挑一名队友。英雄联盟里玩家给正在挨打、快死的人，或者正在
//! 打的那个人。本包：副本里那几处 `RandomTarget` 换成原生效果，挑人（`pick`）之后照主包的数字给：
//!
//! - **迦娜 E `league_support_pick:janna_e`**（50000 内）：护盾 150 + 75% 法强 240 tick，护盾在时攻击力 +15%
//!   （`league_janna_e_storm`），并照主包给迦娜挂 `league_janna_e_lock`（3 tick，主包据此不再给她自己）。
//! - **娑娜 W `league_support_pick:sona_w`**（60000 内）：给**损失生命最多**的队友回 100 + 40% 法强，播主包的回血画面。
//! - **璐璐 E `league_support_pick:lulu_e30` / `:lulu_e60`**（30000 / 60000 内）：放出主包的小精灵（`league_lulu_e_pix`，
//!   每 tick 4500），到了由 `:lulu_e_land` 给护盾 110 + 50% 法强 150 tick、`league_lulu_e_on`、移速攻速 +25% 210 tick
//!   （`league_lulu_w_haste`）、画面和声音；照主包给璐璐挂 `league_lulu_e_got`（1 tick）。
//!
//! 挑人：范围内的友方英雄（不含施法者），先挑有危险的（生命不高于 `LOW`%、或身边 `CROWD_R` 内有 `CROWD` 个以上敌方英雄）里
//! 生命比例最低的；都没危险就挑离敌方英雄最近的（正在打的那个）。一个都没有就什么都不做，主包后面「给自己」的那段照常。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_support_pick.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_support_pick";
pub const LOW: usize = 50;
pub const CROWD: usize = 2;
pub const CROWD_R: f64 = 25_000.0;
const MAP: f64 = 960_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNT: Mutex<usize> = Mutex::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SUPPORT_PICK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_support_pick.log");
        }
    }
    PathBuf::from("league_support_pick.log")
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

// ===================== 挑人 =====================

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// An ally in reach: id, hp, max, enemy champions within `CROWD_R`, distance to the nearest enemy champion.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Ally {
    pub id: usize,
    pub hp: usize,
    pub max: usize,
    pub crowd: usize,
    pub foe: f64,
}

impl Ally {
    pub fn danger(&self) -> bool {
        self.hp * 100 <= LOW * self.max.max(1) || self.crowd >= CROWD
    }

    fn share(&self) -> usize {
        self.hp * 1000 / self.max.max(1)
    }
}

/// For a shield: the one in danger with the lowest health share, else the one nearest an enemy champion.
pub fn pick(allies: &[Ally]) -> Option<Ally> {
    allies.iter().filter(|a| a.danger()).min_by_key(|a| a.share()).copied()
        .or_else(|| allies.iter().min_by(|a, b| a.foe.total_cmp(&b.foe)).copied())
}

/// For a heal: the one missing the most health (None when nobody is hurt).
pub fn pick_heal(allies: &[Ally]) -> Option<Ally> {
    allies.iter().filter(|a| a.hp < a.max).max_by_key(|a| a.max - a.hp).copied()
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn allies(sim: &StableSim<'_>, me: usize, reach: f64) -> Vec<Ally> {
    let Some(e) = sim.get_entity(me) else { return Vec::new() };
    let (team, at) = (e.team(), pos(&e));
    let units: Vec<(usize, usize, Pt, (usize, usize), bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_champion() && u.is_alive())
        .map(|u| (u.id(), u.team(), pos(&u), u.hp(), u.is_targetable()))
        .collect();
    units.iter()
        .filter(|u| u.1 == team && u.0 != me && u.4 && dist(at, u.2) <= reach)
        .map(|u| {
            let foes: Vec<f64> = units.iter().filter(|f| f.1 != team).map(|f| dist(u.2, f.2)).collect();
            Ally {
                id: u.0,
                hp: u.3 .0,
                max: u.3 .1,
                crowd: foes.iter().filter(|d| **d <= CROWD_R).count(),
                foe: foes.iter().copied().fold(f64::MAX, f64::min),
            }
        })
        .collect()
}

fn power(sim: &StableSim<'_>, me: usize) -> usize {
    sim.get_entity(me).map_or(0, |e| e.stat().magic_power)
}

fn with_shield(name: &str) -> BuffV1 {
    let mut b = BuffV1::named(name);
    b.duration_kind = BuffDurationV1::WithShield.code();
    b
}

fn note(sim: &StableSim<'_>, me: usize, what: &str, a: &Ally, extra: String) {
    if let Some(k) = counted() {
        wlog(format!("{} {what} #{k} -> #{} (hp {}/{}, {} enemies around){}{extra}", head(sim, me), a.id, a.hp, a.max, a.crowd,
                     if a.danger() { " IN DANGER" } else { "" }));
    }
}

// ===================== 原生效果 =====================

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Step {
    JannaE,
    SonaW,
    LuluE(u32),
    LuluLand,
}

struct Support(Step);

impl StableEffectType for Support {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let ap = power(sim, caster);
        match self.0 {
            Step::JannaE => {
                let Some(a) = pick(&allies(sim, caster, 50_000.0)) else { return };
                sim.add_buff(caster, &BuffV1::timed("league_janna_e_lock", 3));
                let s = 150 + ap * 75 / 100;
                sim.entity_add_shield(a.id, s, 240);
                let mut storm = with_shield("league_janna_e_storm");
                storm.attack_mult = 15;
                sim.add_buff(a.id, &storm);
                note(sim, caster, "JANNA E", &a, format!(", shield {s}"));
            }
            Step::SonaW => {
                let Some(a) = pick_heal(&allies(sim, caster, 60_000.0)) else { return };
                let h = 100 + ap * 40 / 100;
                sim.heal(caster, a.id, h);
                sim.play_view_effect("league_sona_w_heal", caster, &InputTargetV1::target(a.id), 0, 0, 0);
                note(sim, caster, "SONA W", &a, format!(", heal {h}"));
            }
            Step::LuluE(reach) => {
                let Some(a) = pick(&allies(sim, caster, reach as f64)) else { return };
                let Some((team, at)) = sim.get_entity(caster).map(|e| (e.team(), pos(&e))) else { return };
                sim.add_buff(caster, &BuffV1::timed("league_lulu_e_got", 1));
                sim.play_sfx("league_lulu_e_cast", caster, &InputTargetV1::target(caster));
                let spec = ProjectileSpawnV1 {
                    caster_id: caster,
                    team,
                    x: at.0.round().clamp(0.0, MAP - 1.0) as u64,
                    y: at.1.round().clamp(0.0, MAP - 1.0) as u64,
                    radius: 1_000,
                    speed: 4_500,
                    move_kind: ProjectileMoveKindV1::Target.code(),
                    target_id: a.id,
                    target_x: 0,
                    target_y: 0,
                    penetrate: false,
                    attack_type: AttackTypeV1::Skill.code(),
                    casting_type: CastingTypeV1::Targeting.code(),
                    casting_target: CastingTargetV1::AllyChampion.code(),
                };
                let flew = sim.spawn_projectile("league_lulu_e_pix", &format!("{ID}:lulu_e_land"), &spec);
                note(sim, caster, "LULU E", &a, if flew { String::new() } else { " (spawn_projectile refused)".into() });
            }
            Step::LuluLand => {
                if input.kind != InputTargetKindV1::Target.code() {
                    return;
                }
                let id = input.target_id;
                if !sim.get_entity(id).is_some_and(|e| e.is_alive()) {
                    return;
                }
                sim.entity_add_shield(id, 110 + ap * 50 / 100, 150);
                sim.add_buff(id, &with_shield("league_lulu_e_on"));
                let mut haste = BuffV1::timed("league_lulu_w_haste", 210);
                haste.move_speed_mult = 25;
                haste.attack_speed_mult = 25;
                sim.add_buff(id, &haste);
                sim.play_view_effect("league_lulu_e_land", caster, &InputTargetV1::target(id), 0, 0, 0);
                sim.play_sfx("league_lulu_e_shield", caster, &InputTargetV1::target(id));
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
        "=== {ID} v{} (Janna E, Sona W and Lulu E to the ally who needs it) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    for (name, step) in [("janna_e", Step::JannaE), ("sona_w", Step::SonaW), ("lulu_e30", Step::LuluE(30_000)),
                         ("lulu_e60", Step::LuluE(60_000)), ("lulu_e_land", Step::LuluLand)] {
        module.add_native_effect(format!("{ID}:{name}"), Support(step));
    }
    host.log(LogLevel::Info, "league_support_pick v1 loaded (Janna E, Sona W, Lulu E to the ally who needs it).");
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

    fn a(id: usize, hp: usize, crowd: usize, foe: f64) -> Ally {
        Ally { id, hp, max: 1000, crowd, foe }
    }

    #[test]
    fn shields_go_to_danger_then_to_the_fight() {
        assert_eq!(pick(&[a(1, 900, 0, 20_000.0), a(2, 400, 0, 90_000.0), a(3, 300, 0, 90_000.0)]).map(|x| x.id), Some(3));
        assert_eq!(pick(&[a(1, 900, 2, 20_000.0), a(2, 800, 0, 9_000.0)]).map(|x| x.id), Some(1));
        assert_eq!(pick(&[a(1, 900, 0, 30_000.0), a(2, 800, 1, 9_000.0)]).map(|x| x.id), Some(2));
        assert_eq!(pick(&[]), None);
    }

    #[test]
    fn heals_go_to_the_most_missing() {
        assert_eq!(pick_heal(&[a(1, 500, 0, 0.0), a(2, 300, 0, 0.0)]).map(|x| x.id), Some(2));
        assert_eq!(pick_heal(&[a(1, 1000, 0, 0.0)]), None);
    }
}
