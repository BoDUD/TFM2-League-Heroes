//! 艾克附加包：R「时空断裂」照英雄联盟回到 4 秒前（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补
//! 附加包」）。
//!
//! 主包是纯数据：引擎不记单位过去的位置，也读不到受到的伤害，R 改成施放时留锚点、4 秒后自动回来，治疗固定。英雄联盟的 R
//! 随时回到 4 秒前的位置，按这 4 秒里损失的生命加成治疗，玩家在残血时用它逃命、或者回到人堆里打一套。本包：
//!
//! - **被动 `league_ekko_rewind:rewind`**：每 tick 记下艾克的位置和生命（`REWIND` tick 那么长）。副本的 R 不再留锚点，
//!   施放时给艾克挂 `GO`；本包看到就把他放回 `REWIND` tick 前的位置（死过一次就从复活起算），按这段时间损失的生命
//!   给 R 的治疗加成：每损失 1% 最大生命 +`per`%，最多 +`max`%（数字在英雄数据的 `passive.params`）。落地的伤害、无敌、
//!   画面和主包的那份治疗 `LAND_DELAY` tick 后由数据做。
//! - **AI 钩子 `league_ekko_rewind:ult`**：只在这些时候放 R——生命不高于 `LOW`%；或这 4 秒里掉了 `BURST`% 以上；或回去的
//!   地方 `LAND_R` 内有 `CROWD` 个以上敌方英雄；或那里有人吃得下这一下（`R_BASE` + `R_AP`% 法强，按魔抗折算）。AI 想放
//!   但都不是，改成普攻它的目标；AI 没想放但是是，就替它放。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ekko_rewind.log`。

use std::collections::VecDeque;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_ekko_rewind";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_ekko_rewind") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const HERO: &str = "league_ekko";
/// 副本的 R 施放时给艾克挂的旗子（3 tick）。
pub const GO: &str = "league_ekko_rewind_go";
/// 回到多少 tick 前（英雄联盟 4 秒）。
pub const REWIND: usize = 240;
/// 副本的 R 在挂旗子后这么多 tick 落地（伤害、无敌、画面、治疗）。
pub const LAND_DELAY: usize = 2;
/// 落地伤害的半径和数字（同主包）。
pub const LAND_R: u64 = 35_000;
pub const R_BASE: usize = 150;
pub const R_AP: usize = 100;
/// R 的施法距离（主包：30000 内有敌方英雄才能放）。
pub const R_RANGE: u64 = 30_000;
pub const LOW: usize = 35;
pub const BURST: usize = 30;
pub const CROWD: usize = 2;
/// R 从这一级起能放（同 league_darius_ult）。
const ULT_LEVEL: usize = 5;
const LOG_EVERY: usize = 120;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_EKKO_REWIND_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ekko_rewind.log");
        }
    }
    PathBuf::from("league_ekko_rewind.log")
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

fn params(json: &str) -> Vec<(String, usize)> {
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    body.split(',')
        .filter_map(|pair| {
            let (k, v) = pair.split_once(':')?;
            Some((k.trim().trim_matches('"').to_string(), v.trim().parse::<usize>().ok()?))
        })
        .collect()
}

fn get(p: &[(String, usize)], k: &str, d: usize) -> usize {
    p.iter().find(|(n, _)| n == k).map_or(d, |(_, v)| *v)
}

// ===================== 4 秒的轨迹 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Sample {
    pub tick: usize,
    pub x: u64,
    pub y: u64,
    pub hp: usize,
}

/// 艾克最近 `REWIND` tick 的位置和生命。
#[derive(Clone, Debug, Default)]
pub struct Trail(VecDeque<Sample>);

impl Trail {
    pub fn clear(&mut self) {
        self.0.clear();
    }

    pub fn push(&mut self, s: Sample) {
        if self.0.back().is_some_and(|b| b.tick >= s.tick) {
            self.0.pop_back();
        }
        self.0.push_back(s);
        while self.0.len() > 1 && self.0[1].tick + REWIND <= s.tick {
            self.0.pop_front();
        }
    }

    /// Where R takes him: the oldest sample kept (`REWIND` ticks ago, or since he respawned).
    pub fn spot(&self) -> Option<Sample> {
        self.0.front().copied()
    }

    /// The health he lost since then (heals not subtracted, as League counts damage taken).
    pub fn lost(&self) -> usize {
        self.0.iter().zip(self.0.iter().skip(1)).map(|(a, b)| a.hp.saturating_sub(b.hp)).sum()
    }
}

/// R's heal bonus: `per`% of the heal for each 1% of `max` lost, at most `top`%.
pub fn heal_bonus(heal: usize, lost: usize, max: usize, per: usize, top: usize) -> usize {
    let pct = lost * 100 / max.max(1);
    heal * (pct * per).min(top) / 100
}

/// The AI's call: rewind now? (`hp`, `max`, `lost` his; `crowd` the enemy champions at the spot, `kill` one of them dies.)
pub fn go(hp: usize, max: usize, lost: usize, crowd: usize, kill: bool) -> bool {
    hp * 100 <= LOW * max || lost * 100 >= BURST * max || crowd >= CROWD || kill
}

/// R's landing hit on a target with `mr` magic resist (the game's armour curve: 100 / (100 + mr)).
pub fn land_damage(power: usize, mr: usize) -> usize {
    (R_BASE + power * R_AP / 100) * 100 / (100 + mr)
}

fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0.abs_diff(b.0);
    let dy = a.1.abs_diff(b.1);
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

fn sample(e: &StableEntity<'_, '_>, tick: usize) -> Sample {
    let (x, y) = e.pos();
    Sample { tick, x, y, hp: e.hp().0 }
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

// ===================== 被动：回到 4 秒前 =====================

#[derive(Clone, Default)]
struct Rewind {
    p: Vec<(String, usize)>,
    trail: Trail,
    n: usize,
}

impl StablePassive for Rewind {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.trail.clear();
        wlog(format!("{} SPAWN: the add-on's Ekko (player {player}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.trail.clear();
            return;
        }
        let now = sample(&e, tick);
        let (max, power, flag) = (e.hp().1, e.stat().magic_power, has_buff(&e, GO));
        if !flag {
            self.trail.push(now);
            return;
        }
        sim.entity_remove_buff(me, GO);
        let Some(spot) = self.trail.spot() else { return };
        let lost = self.trail.lost();
        sim.entity_set_pos(me, spot.x, spot.y);
        let heal = get(&self.p, "base", R_BASE) + power * get(&self.p, "ap", 80) / 100;
        let bonus = heal_bonus(heal, lost, max, get(&self.p, "per", 4), get(&self.p, "max", 200));
        if bonus > 0 {
            sim.heal(me, me, bonus);
        }
        self.n += 1;
        if self.n <= 80 || self.n % 25 == 0 {
            wlog(format!("{} REWIND #{}: back {} ticks to ({}, {}), hp {} -> {} then, lost {lost}/{max}, heal {heal} + {bonus}",
                         head(sim, me), self.n, tick - spot.tick, spot.x, spot.y, now.hp, spot.hp));
        }
        // the trail goes on from where he landed
        self.trail.clear();
        self.trail.push(Sample { tick, x: spot.x, y: spot.y, hp: now.hp });
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.trail.clear();
    }
}

// ===================== AI 钩子：什么时候放 R =====================

#[derive(Clone, Default)]
struct UltAi {
    trail: Trail,
    last_log: Option<usize>,
}

fn ult(id: usize) -> InputV1 {
    InputV1::action(InputKindV1::Ult, InputTargetV1::target(id))
}

impl StablePlayerAi for UltAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ult")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let wants = base.is_some_and(|b| b.kind == InputKindV1::Ult.code());
        let ai = base.filter(|_| wants).and_then(|b| {
            (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
        });
        let busy = base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Return))
        });
        let read = {
            let sim = ctx.sim()?;
            (|| {
                let pl = sim.get_player(player)?;
                let free = pl.level() >= ULT_LEVEL && pl.cooldowns().map(|c| c.3) == Some(0);
                let Some(me) = pl.champion().filter(|e| e.is_alive()) else {
                    return Some(None);
                };
                let (id, team, power) = (me.id(), me.team(), me.stat().magic_power);
                let now = sample(&me, tick);
                let foes: Vec<(usize, (u64, u64), usize, usize)> = (0..sim.entity_count())
                    .filter_map(|i| sim.entity_at(i))
                    .filter(|e| e.is_champion() && e.is_alive() && e.team() != team && e.is_targetable())
                    .map(|e| (e.id(), e.pos(), e.hp().0 + e.shield(), e.stat().magic_resistance))
                    .collect();
                let near: Option<usize> = foes.iter()
                    .filter(|f| sim.distance_sq(id, f.0) <= R_RANGE * R_RANGE)
                    .min_by_key(|f| sim.distance_sq(id, f.0))
                    .map(|f| f.0);
                let target_pos = ai.and_then(|t| sim.get_entity(t)).map(|e| e.pos());
                Some(Some((free, now, me.hp().1, power, foes, near, target_pos, head(&sim, id))))
            })()
        };
        let Some((free, now, max, power, foes, near, target_pos, line)) = read? else {
            self.trail.clear();
            return None;
        };
        self.trail.push(now);
        if !wants && (!free || busy) {
            return None;
        }
        let spot = self.trail.spot().map_or((now.x, now.y), |s| (s.x, s.y));
        let lost = self.trail.lost();
        let there: Vec<_> = foes.iter().filter(|f| dist_sq(f.1, spot) <= LAND_R * LAND_R).collect();
        let kill = there.iter().any(|f| f.2 <= land_damage(power, f.3));
        let yes = go(now.hp, max, lost, there.len(), kill);
        let log = self.last_log.is_none_or(|t| tick >= t + LOG_EVERY);
        if yes {
            let pick = ai.or(near)?;
            let input = ult(pick);
            if !ctx.is_valid_input(&input) {
                return None;
            }
            if log && !wants {
                self.last_log = Some(tick);
                wlog(format!("{line} R: hp {}/{max}, lost {lost} in 4s, {} foes at the spot, kill {kill} - the AI had not cast it",
                             now.hp, there.len()));
            }
            return (!wants).then_some(input);
        }
        if !wants {
            return None;
        }
        if log {
            self.last_log = Some(tick);
            wlog(format!("{line} R HELD: hp {}/{max}, lost {lost} in 4s, {} foes at the spot - attacking instead", now.hp,
                         there.len()));
        }
        let t = ai?;
        let atk = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
        if ctx.is_valid_input(&atk) {
            return Some(atk);
        }
        let (x, y) = target_pos.unwrap_or((now.x, now.y));
        Some(InputV1::move_to(x, y))
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Ekko's R back to 4 seconds ago, heal on the health lost) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(UltAi::default());
    module.add_native_passive(format!("{ID}:rewind"), Rewind::default());
    host.log(LogLevel::Info, "league_ekko_rewind v1 loaded (Ekko's Chronobreak back to 4 seconds ago).");
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

    fn s(tick: usize, x: u64, hp: usize) -> Sample {
        Sample { tick, x, y: 0, hp }
    }

    #[test]
    fn the_trail_keeps_four_seconds_and_counts_damage_not_heals() {
        let mut t = Trail::default();
        for k in 0..=300 {
            t.push(s(k, k as u64, 1000 - k));
        }
        assert_eq!(t.spot().map(|x| x.tick), Some(60));
        assert_eq!(t.lost(), 240);
        let mut t = Trail::default();
        for (k, hp) in [(0, 1000), (1, 600), (2, 900), (3, 500)] {
            t.push(s(k, 0, hp));
        }
        assert_eq!(t.lost(), 800);
    }

    #[test]
    fn the_heal_grows_with_the_health_lost_up_to_the_cap() {
        assert_eq!(heal_bonus(300, 0, 1000, 4, 200), 0);
        assert_eq!(heal_bonus(300, 250, 1000, 4, 200), 300);
        assert_eq!(heal_bonus(300, 900, 1000, 4, 200), 600);
    }

    #[test]
    fn the_ai_rewinds_when_low_burst_crowded_or_for_a_kill() {
        assert!(!go(900, 1000, 100, 1, false));
        assert!(go(300, 1000, 0, 0, false));
        assert!(go(800, 1000, 300, 0, false));
        assert!(go(900, 1000, 0, 2, false));
        assert!(go(900, 1000, 0, 1, true));
        assert_eq!(land_damage(100, 0), 250);
        assert_eq!(land_damage(100, 25), 200);
    }
}
