//! 安妮附加包：Q「碎裂之火」照英雄联盟击杀目标时返还一半冷却（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话
//! 全部补附加包」）。
//!
//! 主包是纯数据：引擎没有「打死了就减冷却」的效果，Q 击杀不返还。本包：副本里 Q 的两枚火球（带不带眩晕的）打中时，在伤害之后
//! 多调用一次原生效果 `league_annie_q:refund`（`input` 就是被打中的单位）：他已经死了（小兵、野怪、英雄都算），就把 Q 的
//! 剩余冷却减 `REFUND` tick（Q 冷却 240 tick 的一半），英雄联盟还返还法力，这里没有法力。
//!
//! 提伯斯（v0.2.0，被动 `league_annie_q:tibbers`）：主包的提伯斯是挂在目标身上的一串特效和伤害，目标死了就化烟离场。英雄联盟
//! 里提伯斯接着打身边的人。副本保留召唤那一下（落地、伤害、眩晕），之后的跟随换成给目标挂 `TIB_MARK`；本包照主包每秒在他
//! 身上播站立挥爪和火圈、`TIB_R` 内的敌人受到 14 + 8% 法强的魔法伤害，一共 `TIB_LIFE` tick；他死了（或不能选中）就换到
//! `TIB_REACH` 内最近的敌方英雄，没人了才化烟离场。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_annie_q.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_annie_q";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_annie_q") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const REFUND: usize = 120;
/// 提伯斯（主包的数字和画面）：R 给目标挂的标记、跟多久、第一爪和之后每爪的 tick、灼烧半径和伤害、换目标的距离。
pub const TIB_MARK: &str = "league_annie_q_tib_mark";
pub const TIB_LIFE: usize = 384;
pub const TIB_FIRST: usize = 24;
pub const TIB_PERIOD: usize = 60;
pub const TIB_R: f64 = 30_000.0;
pub const TIB_BURN: usize = 14;
pub const TIB_BURN_AP: usize = 8;
pub const TIB_REACH: f64 = 50_000.0;
pub const TIB_VIEW: &str = "league_annie_tibbers";
pub const TIB_RING: &str = "league_annie_r_ring";
pub const TIB_SWIPE: &str = "league_annie_r_swipe";
pub const TIB_BURN_VIEW: &str = "league_annie_burn";
pub const TIB_VANISH: &str = "league_annie_tibbers_vanish";
pub const TIB_VANISH_SFX: &str = "league_annie_r_vanish";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNT: Mutex<usize> = Mutex::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ANNIE_Q_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_annie_q.log");
        }
    }
    PathBuf::from("league_annie_q.log")
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

// ===================== 返还 =====================

/// Did this hit kill him? (hp 0 or not alive any more)
pub fn killed(alive: bool, hp: usize) -> bool {
    !alive || hp == 0
}

struct Refund;

impl StableEffectType for Refund {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let id = input.target_id;
        let Some((alive, hp, champ)) = sim.get_entity(id).map(|e| (e.is_alive(), e.hp().0, e.is_champion())) else { return };
        if !killed(alive, hp) {
            return;
        }
        let left = sim.get_entity(caster).and_then(|e| e.cooldown(SkillSlotV1::Skill)).map_or(0, |c| c.remaining);
        sim.entity_reduce_cooldown(caster, SkillSlotV1::Skill, REFUND);
        if let Some(k) = counted() {
            wlog(format!("{} Q KILL #{k} on #{id}{}: cooldown {left} -> {}", head(sim, caster),
                         if champ { " (champion)" } else { "" }, left.saturating_sub(REFUND)));
        }
    }
}

// ===================== 提伯斯 =====================

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// Whom Tibbers goes on to when his target is gone: the nearest living enemy champion within `TIB_REACH` of `at`.
pub fn next_target(at: Pt, foes: &[(usize, Pt)]) -> Option<usize> {
    foes.iter().filter(|f| dist(at, f.1) <= TIB_REACH).min_by(|a, b| dist(at, a.1).total_cmp(&dist(at, b.1))).map(|f| f.0)
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// 提伯斯：跟着谁、他在哪、从哪个 tick 起、下一次挥爪的 tick。
#[derive(Clone, Copy, Debug)]
struct Bear {
    target: usize,
    at: Pt,
    from: usize,
    next: usize,
}

#[derive(Clone, Default)]
struct Tibbers {
    bear: Option<Bear>,
    n: usize,
}

impl Tibbers {
    fn vanish(&mut self, sim: &mut StableSim<'_>, me: usize, b: Bear, why: &str) {
        let input = sim.get_entity(b.target).filter(|e| e.is_alive()).map(|_| InputTargetV1::target(b.target))
            .unwrap_or(InputTargetV1::pos(b.at.0.round() as u64, b.at.1.round() as u64));
        sim.play_view_effect(TIB_VANISH, me, &input, 0, 0, 0);
        sim.play_sfx(TIB_VANISH_SFX, me, &input);
        if self.n <= 80 {
            wlog(format!("{} TIBBERS #{} gone ({why})", head(sim, me), self.n));
        }
        self.bear = None;
    }
}

impl StablePassive for Tibbers {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.bear = None;
        wlog(format!("{} SPAWN: the add-on's Annie (player {player})", head(sim, me)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (team, power) = (e.team(), e.stat().magic_power);
        let foes: Vec<(usize, Pt, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.is_alive() && u.team() != team && u.is_targetable())
            .map(|u| (u.id(), pos(&u), has_buff(&u, TIB_MARK)))
            .collect();
        // a new Tibbers: R has just marked his target
        if let Some(f) = foes.iter().find(|f| f.2) {
            sim.entity_remove_buff(f.0, TIB_MARK);
            if let Some(old) = self.bear.take() {
                self.bear = Some(old);
                self.vanish(sim, me, old, "a new one");
            }
            self.n += 1;
            self.bear = Some(Bear { target: f.0, at: f.1, from: tick, next: tick + TIB_FIRST });
            if self.n <= 80 {
                wlog(format!("{} TIBBERS #{} on #{}", head(sim, me), self.n, f.0));
            }
        }
        let Some(mut b) = self.bear else { return };
        if tick >= b.from + TIB_LIFE {
            return self.vanish(sim, me, b, "time");
        }
        match foes.iter().find(|f| f.0 == b.target) {
            Some(f) => b.at = f.1,
            None => {
                let near: Vec<(usize, Pt)> = foes.iter().map(|f| (f.0, f.1)).collect();
                match next_target(b.at, &near) {
                    Some(t) => {
                        if self.n <= 80 {
                            wlog(format!("{} TIBBERS #{}: #{} is gone, on to #{t}", head(sim, me), self.n, b.target));
                        }
                        b.target = t;
                        b.at = foes.iter().find(|f| f.0 == t).map_or(b.at, |f| f.1);
                    }
                    None => return self.vanish(sim, me, b, "nobody left near him"),
                }
            }
        }
        if tick >= b.next {
            b.next = tick + TIB_PERIOD;
            let on = InputTargetV1::target(b.target);
            sim.play_view_effect(TIB_RING, me, &on, 0, 0, 0);
            sim.play_view_effect(TIB_VIEW, me, &on, 0, 0, 0);
            sim.play_sfx(TIB_SWIPE, me, &on);
            let damage = TIB_BURN + power * TIB_BURN_AP / 100;
            let hit: Vec<usize> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() != team && u.is_alive() && !u.is_tower() && u.is_targetable() && dist(pos(u), b.at) <= TIB_R)
                .map(|u| u.id()).collect();
            for id in hit {
                sim.deal_damage_typed(me, id, damage, DamageTypeV1::Ap, AttackTypeV1::Skill);
                sim.play_view_effect(TIB_BURN_VIEW, me, &InputTargetV1::target(id), 0, 0, 0);
            }
        }
        self.bear = Some(b);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Annie's Disintegrate refunds on a kill, Tibbers goes on to the next champion) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:refund"), Refund);
    module.add_native_passive(format!("{ID}:tibbers"), Tibbers::default());
    host.log(LogLevel::Info, "league_annie_q v1 loaded (Disintegrate refunds half its cooldown on a kill).");
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
    fn a_kill_is_no_life_left() {
        assert!(killed(false, 100));
        assert!(killed(true, 0));
        assert!(!killed(true, 1));
    }

    #[test]
    fn tibbers_goes_on_to_the_nearest() {
        let f = [(1, (40_000.0, 0.0)), (2, (20_000.0, 0.0)), (3, (5_000.0, 90_000.0))];
        assert_eq!(next_target((0.0, 0.0), &f), Some(2));
        assert_eq!(next_target((0.0, 0.0), &[(3, (5_000.0, 90_000.0))]), None);
    }
}
