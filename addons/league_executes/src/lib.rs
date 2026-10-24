//! 斩杀附加包：伊芙琳 R「最终抚慰」和阿卡丽 R2「完美刺杀」照英雄联盟按目标的生命加伤（用户 2026-10-24：「查看现在没有做附加包
//! 的英雄有明显不一样的话全部补附加包」）。
//!
//! 主包是纯数据，读不到生命：两人的 R 都改成按她自己最近打中英雄的次数分档加伤。`mod.override_info` 换上的副本
//! （`make_override.py` 从主包生成）去掉这条分档链，命中时给目标挂一个标记；本包的被动看到标记就读目标的生命补伤害：
//!
//! - **伊芙琳 `league_executes:evelynn`**：目标生命不高于 `below`% 时，补 `bonus`% 的 R 伤害（英雄联盟：30% 以下 ×2.4）。
//! - **阿卡丽 `league_executes:akali`**：R2 按目标已损失生命补 0–`max`% 的伤害，损失 `full`% 时加满（英雄联盟 0–200%）。
//!
//! - **锐雯 `league_executes:riven`**：疾风斩照英雄联盟是斩杀，玩家留着收人头。主包在放大招 5 秒后、身边有敌方英雄就放，
//!   伤害按最大生命算。副本的每一处定时检查多等一个 `RIVEN_GO`：本包在 `RIVEN_REACH` 内有敌方英雄生命不高于 `RIVEN_LOW`%、
//!   这一斩砍得死人、或大招只剩 `RIVEN_LAST` tick 时才挂上它。疾风斩去掉 8% 最大生命，打中的人身上挂 `RIVEN_MARK`；本包按他
//!   已损失的生命补 0–`max`% 的物理伤害（损失 `full`% 时加满；英雄联盟 0–200%）。
//!
//! 伊芙琳、阿卡丽补的是魔法伤害（`deal_damage_typed`，`Ap`），锐雯的是物理（`Ad`）。数字在英雄数据的 `passive.params`
//! （`make_override.py` 从主包读）。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_executes.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_executes";
pub const EVELYNN_MARK: &str = "league_executes_ev_hit";
pub const AKALI_MARK: &str = "league_executes_ak_hit";
pub const RIVEN_MARK: &str = "league_executes_rv_hit";
pub const RIVEN_GO: &str = "league_riven_ws_go";
pub const RIVEN_READY: &str = "league_riven_r_slash_ready";
pub const RIVEN_WAIT: &str = "league_riven_r_wait";
pub const RIVEN_R: &str = "league_riven_r";
/// 疾风斩的射程（主包的 RandomTarget）、残血线、大招快结束时（tick）。
pub const RIVEN_REACH: u64 = 60_000;
pub const RIVEN_LOW: usize = 30;
pub const RIVEN_LAST: usize = 90;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_EXECUTES_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_executes.log");
        }
    }
    PathBuf::from("league_executes.log")
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

// ===================== 参数和计算 =====================

/// `{"a":1,...}` -> (key, value) pairs of non-negative integers.
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

/// The skill's own damage: `base` + `ap`% of the caster's ability power.
pub fn hit(base: usize, ap: usize, power: usize) -> usize {
    base + power * ap / 100
}

/// Evelynn: `bonus`% more when he stands at `below`% of his health or under.
pub fn evelynn_extra(hp: usize, max: usize, below: usize, bonus: usize, damage: usize) -> usize {
    if hp * 100 <= below * max.max(1) { damage * bonus / 100 } else { 0 }
}

/// Akali: 0..`top`% more as his missing health grows to `full`% of his maximum.
pub fn akali_extra(hp: usize, max: usize, full: usize, top: usize, damage: usize) -> usize {
    let missing = max.saturating_sub(hp) * 100 / max.max(1);
    let pct = (missing * top / full.max(1)).min(top);
    damage * pct / 100
}

// ===================== 被动 =====================

#[derive(Clone, Copy, PartialEq, Eq, Default)]
enum Who {
    #[default]
    Evelynn,
    Akali,
}

#[derive(Clone, Default)]
struct Execute {
    who: Who,
    p: Vec<(String, usize)>,
    n: usize,
}

impl Execute {
    fn of(who: Who) -> Self {
        Self { who, ..Self::default() }
    }

    fn mark(&self) -> &'static str {
        match self.who {
            Who::Evelynn => EVELYNN_MARK,
            Who::Akali => AKALI_MARK,
        }
    }
}

impl StablePassive for Execute {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let who = if self.who == Who::Evelynn { "Evelynn" } else { "Akali" };
        wlog(format!("{} SPAWN: the add-on's {who} (player {player}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, power) = (e.team(), e.stat().magic_power);
        let mark = self.mark();
        let marked: Vec<(usize, usize, usize)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive())
            .filter(|u| (0..u.buff_count()).filter_map(|k| u.buff_at(k)).any(|b| b.name() == mark))
            .map(|u| (u.id(), u.hp().0, u.hp().1))
            .collect();
        for (id, hp, max) in marked {
            sim.entity_remove_buff(id, mark);
            let damage = hit(get(&self.p, "base", 0), get(&self.p, "ap", 0), power);
            let extra = match self.who {
                Who::Evelynn => evelynn_extra(hp, max, get(&self.p, "below", 30), get(&self.p, "bonus", 140), damage),
                Who::Akali => akali_extra(hp, max, get(&self.p, "full", 70), get(&self.p, "max", 200), damage),
            };
            if extra > 0 {
                sim.deal_damage_typed(me, id, extra, DamageTypeV1::Ap, AttackTypeV1::Skill);
            }
            self.n += 1;
            if self.n <= 80 || self.n % 25 == 0 {
                wlog(format!("{} EXECUTE #{} on #{id}: hp {hp}/{max}, hit {damage}, +{extra} magic", head(sim, me), self.n));
            }
        }
    }
}

fn buff_left(e: &StableEntity<'_, '_>, name: &str) -> Option<usize> {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).map(|b| {
        if BuffDurationV1::from_code(b.duration_kind) == Some(BuffDurationV1::Time) { b.duration_tick } else { usize::MAX }
    }).max()
}

/// Riven: is now the moment for Wind Slash? `foes` (hp, max, shield) in reach, `damage` its base hit, `r_left` ticks.
pub fn riven_go(foes: &[(usize, usize, usize)], damage: usize, full: usize, top: usize, r_left: usize) -> bool {
    r_left <= RIVEN_LAST
        || foes.iter().any(|&(hp, max, shield)| {
            hp * 100 <= RIVEN_LOW * max.max(1) || damage + akali_extra(hp, max, full, top, damage) >= hp + shield
        })
}

#[derive(Clone, Default)]
struct Riven {
    p: Vec<(String, usize)>,
    n: usize,
    gone: usize,
}

impl StablePassive for Riven {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        wlog(format!("{} SPAWN: the add-on's Riven (player {player}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, attack) = (e.team(), e.stat().attack);
        let damage = hit(get(&self.p, "base", 0), get(&self.p, "ad", 0), attack);
        let (full, top) = (get(&self.p, "full", 75), get(&self.p, "max", 200));
        // when to slash
        let ready = buff_left(&e, RIVEN_READY).is_some() && buff_left(&e, RIVEN_WAIT).is_none() && e.is_alive();
        if ready {
            let r_left = buff_left(&e, RIVEN_R).unwrap_or(0);
            let reach = RIVEN_REACH * RIVEN_REACH;
            let foes: Vec<(usize, usize, usize)> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|u| u.is_champion() && u.is_alive() && u.team() != team && sim.distance_sq(me, u.id()) <= reach)
                .map(|u| (u.hp().0, u.hp().1, u.shield()))
                .collect();
            if !foes.is_empty() && riven_go(&foes, damage, full, top, r_left) {
                sim.entity_remove_buff(me, RIVEN_GO);
                sim.add_buff(me, &BuffV1::timed(RIVEN_GO, 4));
                if self.gone < 60 {
                    self.gone += 1;
                    wlog(format!("{} RIVEN SLASH GO #{}: {} champions in reach, R left {r_left}", head(sim, me), self.gone,
                                 foes.len()));
                }
            }
        }
        // the slash's execute share on each one it hit
        let marked: Vec<(usize, usize, usize)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive())
            .filter(|u| (0..u.buff_count()).filter_map(|k| u.buff_at(k)).any(|b| b.name() == RIVEN_MARK))
            .map(|u| (u.id(), u.hp().0, u.hp().1))
            .collect();
        for (id, hp, max) in marked {
            sim.entity_remove_buff(id, RIVEN_MARK);
            let extra = akali_extra(hp, max, full, top, damage);
            if extra > 0 {
                sim.deal_damage_typed(me, id, extra, DamageTypeV1::Ad, AttackTypeV1::Skill);
            }
            self.n += 1;
            if self.n <= 80 || self.n % 25 == 0 {
                wlog(format!("{} RIVEN SLASH #{} on #{id}: hp {hp}/{max}, hit {damage}, +{extra} physical", head(sim, me), self.n));
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
        "=== {ID} v{} (Evelynn's and Akali's ults on the target's health) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:evelynn"), Execute::of(Who::Evelynn));
    module.add_native_passive(format!("{ID}:akali"), Execute::of(Who::Akali));
    module.add_native_passive(format!("{ID}:riven"), Riven::default());
    host.log(LogLevel::Info, "league_executes v1 loaded (Evelynn's and Akali's ults on the target's health).");
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
    fn evelynn_executes_below_the_line() {
        assert_eq!(evelynn_extra(290, 1000, 30, 140, 300), 420);
        assert_eq!(evelynn_extra(300, 1000, 30, 140, 300), 420);
        assert_eq!(evelynn_extra(310, 1000, 30, 140, 300), 0);
    }

    #[test]
    fn akali_grows_with_missing_health() {
        assert_eq!(akali_extra(1000, 1000, 70, 200, 200), 0);
        assert_eq!(akali_extra(650, 1000, 70, 200, 200), 200); // 35% missing: +100%
        assert_eq!(akali_extra(300, 1000, 70, 200, 200), 400); // 70% missing: +200%
        assert_eq!(akali_extra(10, 1000, 70, 200, 200), 400);
    }

    #[test]
    fn riven_slashes_for_the_kill_the_low_or_the_end() {
        // 1000 max: a healthy one, nothing ending: wait
        assert!(!riven_go(&[(900, 1000, 0)], 200, 75, 200, 600));
        assert!(riven_go(&[(300, 1000, 0)], 200, 75, 200, 600));
        // 450 hp: 200 + (55% missing -> +146%) 292 = 492 kills
        assert!(riven_go(&[(450, 1000, 0)], 200, 75, 200, 600));
        assert!(riven_go(&[(900, 1000, 0)], 200, 75, 200, RIVEN_LAST));
    }

    #[test]
    fn params_read() {
        let p = params(r#"{"ap":75,"base":150}"#);
        assert_eq!((get(&p, "base", 0), get(&p, "ap", 0), get(&p, "x", 7)), (150, 75, 7));
        assert_eq!(hit(150, 75, 200), 300);
    }
}
