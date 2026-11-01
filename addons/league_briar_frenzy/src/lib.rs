//! 贝蕾亚附加包：E 撞墙才眩晕、血狂锁定目标、大招的血狂持续到猎物倒下（用户 2026-10-24：「查看现在没有做附加包的英雄有明显
//! 不一样的话全部补附加包」）。
//!
//! 主包是纯数据：读不到墙，E 击退的英雄一律在击退结束时眩晕；血莽、彻底血狂期间 AI 照常挑目标（还会回城）；大招的血狂固定
//! 6 秒。英雄联盟里 E 要把人推到墙上才眩晕，血狂中的她只扑最近的敌人，大招的血狂直到她或猎物倒下。本包：
//!
//! - **E（被动 `league_briar_frenzy:frenzy`）**：副本里击退结束时的眩晕换成给英雄挂 `E_MARK`；本包从挂上那一刻记下他的
//!   位置，`KNOCK` tick 后（击退结束）他被推出去不到 `BLOCKED`%（主包推 `KNOCK_DIST`），就是撞上了墙、地图边或别的单位：
//!   眩晕 `E_STUN` tick（`apply_cc`），播主包的眩晕画面和声音。
//! - **大招**：她身上有彻底血狂 `HEMA`、猎物（身上有 `PREY`）还活着，就在血狂快结束时照主包的数值续上，猎物的标记也续上，
//!   最多 `HEMA_MAX` tick。
//! - **血狂锁定（AI 钩子 `league_briar_frenzy:lock`）**：她身上有血莽 `FRENZY` 或 `HEMA` 时，AI 要普攻、走路、回城都改成普攻
//!   ——彻底血狂时打猎物，否则打 `LOCK_R` 内最近的敌方英雄，没有就打最近的敌人；放技能不拦。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_briar_frenzy.log`。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_briar_frenzy";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_briar_frenzy") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const HERO: &str = "league_briar";
pub const E_MARK: &str = "league_briar_frenzy_e";
pub const KNOCK: usize = 16;
pub const KNOCK_DIST: f64 = 40_000.0;
pub const BLOCKED: f64 = 65.0;
pub const E_STUN: u64 = 60;
pub const E_STUN_FX: &str = "league_briar_e_stun";
pub const FRENZY: &str = "league_briar_frenzy";
pub const HEMA: &str = "league_briar_hema";
pub const PREY: &str = "league_briar_r_mark";
pub const HEMA_MAX: usize = 900;
/// 主包彻底血狂的数值（攻速、移速、护甲、魔抗、生命偷取）。
pub const HEMA_STATS: (i32, i32, i32, i32, i32) = (70, 45, 20, 20, 10);
pub const LOCK_R: u64 = 50_000;
pub const UNIT_R: u64 = 30_000;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_BRIAR_FRENZY_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_briar_frenzy.log");
        }
    }
    PathBuf::from("league_briar_frenzy.log")
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

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn buff_left(e: &StableEntity<'_, '_>, name: &str) -> Option<usize> {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).map(|b| {
        if BuffDurationV1::from_code(b.duration_kind) == Some(BuffDurationV1::Time) { b.duration_tick } else { usize::MAX }
    }).max()
}

/// Did the knock-back hit something? (pushed `moved` of `KNOCK_DIST`)
pub fn blocked(moved: f64) -> bool {
    moved * 100.0 < BLOCKED * KNOCK_DIST
}

fn hema_buff(ticks: usize) -> BuffV1 {
    let mut b = BuffV1::timed(HEMA, ticks);
    (b.attack_speed_mult, b.move_speed_mult, b.defence, b.magic_resistance, b.vamp) = HEMA_STATS;
    b
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Frenzy {
    /// E 击退中的英雄：起点、挂上的 tick。
    knocked: HashMap<usize, (Pt, usize)>,
    /// 彻底血狂开始的 tick。
    hema_from: Option<usize>,
    n: usize,
}

impl StablePassive for Frenzy {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.knocked.clear();
        self.hema_from = None;
        wlog(format!("{} SPAWN: the add-on's Briar (player {player})", head(sim, me)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (team, alive, hema) = (e.team(), e.is_alive(), buff_left(&e, HEMA));
        let foes: Vec<(usize, Pt, bool, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.team() != team)
            .map(|u| (u.id(), pos(&u), u.is_alive() && buff_left(&u, E_MARK).is_some(), u.is_alive() && buff_left(&u, PREY).is_some()))
            .collect();
        // E: where the knocked-back champions started, and whether they got far
        for f in foes.iter().filter(|f| f.2) {
            sim.entity_remove_buff(f.0, E_MARK);
            self.knocked.insert(f.0, (f.1, tick));
        }
        let due: Vec<usize> = self.knocked.iter().filter(|(_, v)| tick >= v.1 + KNOCK).map(|(k, _)| *k).collect();
        for id in due {
            let (from, _) = self.knocked.remove(&id).unwrap_or(((0.0, 0.0), 0));
            let Some(now) = foes.iter().find(|f| f.0 == id).map(|f| f.1) else { continue };
            let moved = dist(from, now);
            let hit = blocked(moved) && sim.get_entity(id).is_some_and(|u| u.is_alive());
            if hit {
                sim.apply_cc(id, &CcV1::of_kind(CcKindV1::Stun, E_STUN));
                sim.play_view_effect(E_STUN_FX, me, &InputTargetV1::target(id), 0, 0, 0);
                sim.play_sfx(E_STUN_FX, me, &InputTargetV1::target(id));
            }
            self.n += 1;
            if self.n <= 80 || self.n % 25 == 0 {
                wlog(format!("{} E #{} on #{id}: pushed {moved:.0} of {KNOCK_DIST:.0}{}", head(sim, me), self.n,
                             if hit { " -> hit a wall, STUNNED" } else { " (no wall)" }));
            }
        }
        // R: the full frenzy lasts while the prey lives
        let Some(left) = hema.filter(|_| alive) else {
            self.hema_from = None;
            return;
        };
        let from = *self.hema_from.get_or_insert(tick);
        let prey = foes.iter().find(|f| f.3).map(|f| f.0);
        if let Some(p) = prey {
            if left < 30 && tick < from + HEMA_MAX {
                sim.entity_remove_buff(me, HEMA);
                sim.add_buff(me, &hema_buff(60));
                sim.entity_remove_buff(p, PREY);
                sim.add_buff(p, &BuffV1::timed(PREY, 90));
            }
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.hema_from = None;
    }
}

// ===================== AI 钩子 =====================

#[derive(Clone, Default)]
struct Lock {
    last_log: Option<usize>,
}

impl StablePlayerAi for Lock {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:lock")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let casting = base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Ult))
        });
        if casting {
            return None;
        }
        let tick = ctx.tick();
        let player = ctx.player_id();
        let pick = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion().filter(|e| e.is_alive())?;
            let (id, team) = (me.id(), me.team());
            let hema = buff_left(&me, HEMA).is_some();
            if !hema && buff_left(&me, FRENZY).is_none() {
                return None;
            }
            let units: Vec<(usize, bool, bool, u64)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
                .map(|u| (u.id(), u.is_champion(), buff_left(&u, PREY).is_some(), sim.distance_sq(id, u.id())))
                .collect();
            let prey = units.iter().find(|u| u.2 && hema).map(|u| u.0);
            let champ = units.iter().filter(|u| u.1 && u.3 <= LOCK_R * LOCK_R).min_by_key(|u| u.3).map(|u| u.0);
            let unit = units.iter().filter(|u| u.3 <= UNIT_R * UNIT_R).min_by_key(|u| u.3).map(|u| u.0);
            prey.or(champ).or(unit)
        }?;
        let input = InputV1::action(InputKindV1::Attack, InputTargetV1::target(pick));
        let same = base.is_some_and(|b| b.kind == InputKindV1::Attack.code() && b.target.target_id == pick);
        if same || !ctx.is_valid_input(&input) {
            return None;
        }
        if self.last_log.is_none_or(|t| tick >= t + 120) {
            self.last_log = Some(tick);
            wlog(format!("t={tick} player {player} FRENZY LOCK on #{pick} (the AI had {:?})", base.map(|b| (b.kind, b.target.target_id))));
        }
        Some(input)
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Briar's E stuns on walls, her frenzy locks on, her ult lasts while the prey lives) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:frenzy"), Frenzy::default());
    module.add_player_input_ai(Lock::default());
    host.log(LogLevel::Info, "league_briar_frenzy v1 loaded (Briar: wall stun, frenzy lock, ult on the prey).");
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
    fn a_short_push_hit_a_wall() {
        assert!(blocked(10_000.0));
        assert!(blocked(25_000.0));
        assert!(!blocked(39_000.0));
    }
}
