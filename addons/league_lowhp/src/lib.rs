//! 低血量附加包：布里茨的法力屏障、乐芙兰的镜花水月、丽桑卓的自我冰封照英雄联盟在生命低时触发（用户 2026-10-24：「查看现在
//! 没有做附加包的英雄有明显不一样的话全部补附加包」）。
//!
//! 主包是纯数据，读不到生命：三人都改成「身边有两名以上敌方英雄」（布里茨再加「队友被控」）时触发——每次动作先数身边的敌人，
//! 两个以上就挂 `<名>_n2`，再读它。`mod.override_info` 换上的副本（`make_override.py` 从主包生成）把读 `n2` 的地方改成读
//! 本包的标记 `<英雄>_low`；本包的被动在生命不高于门槛时一直挂着它（每 tick 续 `HOLD` tick）：
//!
//! | 英雄 | 门槛（英雄联盟） | 触发什么（都在主包数据里） |
//! |---|---|---|
//! | 布里茨 | 30% | 法力屏障：120 + 80% 法强的护盾，冷却 60 秒 |
//! | 乐芙兰 | 40% | 镜花水月：隐身 1 秒、后闪、留下幻像，40 秒一次 |
//! | 丽桑卓 | 35% | 大招改为冰封自己 |
//!
//! 丽桑卓的被动「冰脉驱役」（v0.2.0）也在这里（她的副本只能有一份）：主包只认她自己打死的英雄（击杀检查）。英雄联盟里她身边
//! 任何敌方英雄阵亡都化成冰仆。副本去掉数据里的那 7 处冰仆；被动每 tick 记下敌方英雄的位置和死活，有人在她 `THRALL_REACH`
//! 内由活变死（或者上一拍还活着、这一拍实体就没了：阵亡英雄的实体一般下一拍就不在了，0.2.3），就在他倒下的地方（上一拍的
//! 位置）播主包的冰仆画面，`THRALL_TICKS` 后碎裂：播主包的碎裂画面和声音，`THRALL_R` 内的敌人（英雄、
//! 小兵、野怪）受到 150 + 70% 法强的魔法伤害、减速 25% 1.5 秒（同主包）。冰仆不会走（画面是挂在地上的，走了画面跟不上）；
//! v0.2.1 起碎裂时扑向 `THRALL_LUNGE` 内最近的敌方英雄（没有英雄就最近的小兵、野怪），在他身上碎裂：原地碎裂 22 次只有 4 次
//! 炸到人（1.5 秒后尸体边上没人了）。v0.2.6：`THRALL_LUNGE` 45000 → 72000（英雄联盟的冰仆追附近看得见的敌人 4 秒、速度从 33
//! 涨到 325，追得到 700 多码；11-06 的日志 42 个冰仆 31 个 45000 内一个敌人都没有），日志写上冰仆是从「死了」还是「从列表里
//! 消失」的人身上升起的，扑空时最近的敌方英雄、单位多远。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_lowhp.log`。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

/// 0.3.1: her thralls as units (src/thralls.rs).
pub mod thralls;

const ID: &str = "league_lowhp";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_lowhp") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 标记每次续多久（每 tick 都续，比 1 多一点，跨过结算顺序）。
pub const HOLD: usize = 3;
/// (英雄, 被动名, 标记, 门槛 %)。
pub const HEROES: [(&str, &str, &str, usize); 3] = [
    ("league_blitzcrank", "blitzcrank", "league_blitzcrank_low", 30),
    ("league_leblanc", "leblanc", "league_leblanc_low", 40),
    ("league_lissandra", "lissandra", "league_lissandra_low", 35),
];
/// 丽桑卓的冰仆：多远内的阵亡算、多久碎裂、碎裂时扑多远（英雄联盟的冰仆会走向敌人）、碎裂的半径和伤害（同主包）、减速。
/// 扑多远（0.2.6）：英雄联盟的冰仆追附近看得见的敌人（英雄优先）4 秒，速度从 33.48 涨到 325，一路追下来 700 多码 = 本包的 72000；
/// 这里 1.5 秒就碎（画面的长度），扑的距离照英雄联盟一整只冰仆追得到的算（以前 45000：11-06 的日志 42 个冰仆 31 个扑空，
/// 45000 内一个敌人都没有）。
pub const THRALL_REACH: f64 = 90_000.0;
pub const THRALL_TICKS: usize = 90;
pub const THRALL_LUNGE: f64 = 72_000.0;
pub const THRALL_R: f64 = 25_000.0;
pub const THRALL_BASE: usize = 150;
pub const THRALL_AP: usize = 70;
pub const THRALL_SLOW: (&str, usize, i32) = ("league_lissandra_p_slow", 90, -25);
pub const THRALL_VIEW: &str = "league_lissandra_p_thrall";
pub const THRALL_RISE: &str = "league_lissandra_p_rise";
pub const THRALL_BURST: &str = "league_lissandra_p_burst";
pub const THRALL_HIT: &str = "league_lissandra_p_hit";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LOWHP_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_lowhp.log");
        }
    }
    PathBuf::from("league_lowhp.log")
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

/// At `pct`% of the maximum or under.
pub fn low(hp: usize, max: usize, pct: usize) -> bool {
    hp * 100 <= pct * max.max(1)
}

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// Enemy champions who died this tick within `reach` of her at `me`: `before` (alive, where) last tick, `now` this tick.
/// One alive last tick falls where it stood then if it is dead now - or no longer listed at all: a dead champion's
/// entity is usually gone by the next tick (0.2.3, the 11-03 night logs: 7 spawns, 8 LOW, 0 THRALL - 0.2.2 waited for
/// an enemy listed as dead and never saw one). The ones gone come after the ones listed dead, by id (the order the
/// thralls rise in is the same in every sim of a match; a HashMap's is not).
pub fn fallen(before: &HashMap<usize, (bool, Pt)>, now: &[(usize, bool, Pt)], me: Pt, reach: f64) -> Vec<Pt> {
    fallen_kinds(before, now, me, reach).into_iter().map(|f| f.1).collect()
}

/// `fallen` with who and how each fell (0.2.6, for the log): (id, where, listed dead this tick - else gone from the
/// list: a dead champion's entity, or one that vanished without dying).
pub fn fallen_kinds(before: &HashMap<usize, (bool, Pt)>, now: &[(usize, bool, Pt)], me: Pt, reach: f64)
    -> Vec<(usize, Pt, bool)> {
    let mut gone: Vec<(usize, Pt)> = before.iter()
        .filter(|&(id, b)| b.0 && now.iter().all(|n| n.0 != *id))
        .map(|(id, b)| (*id, b.1))
        .collect();
    gone.sort_by_key(|g| g.0);
    now.iter()
        .filter(|(id, alive, _)| !alive && before.get(id).is_some_and(|b| b.0))
        .map(|(id, _, _)| (*id, before[id].1, true))
        .chain(gone.into_iter().map(|g| (g.0, g.1, false)))
        .filter(|f| dist(f.1, me) <= reach)
        .collect()
}

/// Whether the kill log has the death of the champion of lane `lane` in team `team` in the last few ticks before `now`
/// (0.2.6, diagnostics: a unit that vanished without dying - banished, attached - would have none).
pub fn death_logged(log: &[KillLogV1], team: usize, lane: u32, now: usize) -> bool {
    log.iter().rev().take_while(|k| k.tick + 3 >= now).any(|k| k.killed_position == lane && k.killer_team != team)
}

/// How a thrall's champion fell, for its THRALL line (0.2.6).
pub fn fall_text(listed_dead: bool, logged: Option<bool>) -> &'static str {
    match (listed_dead, logged) {
        (true, Some(true)) => "one died (kill log)",
        (true, _) => "one was listed dead (no kill-log entry)",
        (false, Some(true)) => "one left the list (a death in the kill log)",
        (false, Some(false)) => "one left the list with NO death in the kill log",
        (false, None) => "one left the list (lane unknown)",
    }
}

/// Where a thrall at `p` shatters: on the nearest enemy champion within `reach`, else the nearest other enemy there, else
/// where it stands. `foes`: (champion, where) of the enemies it can hit.
pub fn lunge(p: Pt, foes: &[(bool, Pt)], reach: f64) -> Pt {
    let near = |champ: bool| foes.iter().filter(|f| f.0 == champ).map(|f| f.1).filter(|q| dist(*q, p) <= reach)
        .min_by(|a, b| dist(*a, p).total_cmp(&dist(*b, p)));
    near(true).or_else(|| near(false)).unwrap_or(p)
}

/// The nearest enemy champion and the nearest other enemy from `p` (the THRALL line of a thrall that lunged at nothing,
/// 0.2.6): "champion D, unit D" or "none".
pub fn nearest_text(p: Pt, foes: &[(bool, Pt)]) -> String {
    let near = |champ: bool| foes.iter().filter(|f| f.0 == champ).map(|f| dist(f.1, p)).min_by(|a, b| a.total_cmp(b));
    let show = |d: Option<f64>| d.map_or("none".to_string(), |d| format!("{d:.0}"));
    format!("nearest enemy champion {}, unit {}", show(near(true)), show(near(false)))
}

/// 丽桑卓的冰仆：上一 tick 敌方英雄的死活和位置（和他们的分路：击杀记录按分路记人），等着碎裂的冰仆（碎裂的 tick、位置、
/// 那人是怎么倒下的）。
#[derive(Clone, Default)]
struct Thralls {
    bodies: thralls::Bodies,
    seen: HashMap<usize, (bool, Pt)>,
    lanes: HashMap<usize, u32>,
    rising: Vec<(usize, Pt, &'static str)>,
    n: usize,
}

impl Thralls {
    fn update(&mut self, sim: &mut StableSim<'_>, me: usize, alive: bool) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (team, at, power) = (e.team(), (e.pos().0 as f64, e.pos().1 as f64), e.stat().magic_power);
        let now: Vec<(usize, bool, Pt)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.team() != team)
            .map(|u| (u.id(), u.is_alive(), (u.pos().0 as f64, u.pos().1 as f64)))
            .collect();
        if alive {
            let fell = fallen_kinds(&self.seen, &now, at, THRALL_REACH);
            // the kill log's last entries: did each one fall by a death (0.2.6, diagnostics)
            let log: Vec<KillLogV1> = if fell.is_empty() {
                Vec::new()
            } else {
                let n = sim.kill_log_count();
                (n.saturating_sub(10)..n).filter_map(|i| sim.kill_log_at(i)).collect()
            };
            for (id, p, listed_dead) in fell {
                let logged = self.lanes.get(&id).map(|&lane| death_logged(&log, 1 - team.min(1), lane, tick));
                let input = InputTargetV1::pos(p.0.round() as u64, p.1.round() as u64);
                if !self.bodies.rise(sim, me, p, THRALL_TICKS) {
                    sim.play_view_effect(THRALL_VIEW, me, &input, 0, 0, 0);
                }
                sim.play_sfx(THRALL_RISE, me, &input);
                self.rising.push((tick + THRALL_TICKS, p, fall_text(listed_dead, logged)));
            }
        }
        self.seen = now.iter().map(|(id, a, p)| (*id, (*a, *p))).collect();
        // the enemy champions' lanes (kept for the ones gone from the list next tick)
        for p in (0..sim.player_count()).filter_map(|i| sim.player_at(i)).filter(|p| p.team() != team) {
            if let (Some(c), Some(l)) = (p.champion(), p.lane()) {
                self.lanes.insert(c.id(), l.code());
            }
        }
        if self.lanes.len() > 256 {
            self.lanes.retain(|id, _| now.iter().any(|n| n.0 == *id)); // old lives' ids
        }
        self.bodies.tick(sim, me, team);
        let due: Vec<(Pt, &'static str)> = self.rising.iter().filter(|r| r.0 <= tick).map(|r| (r.1, r.2)).collect();
        self.rising.retain(|r| r.0 > tick);
        for (at, how) in due {
            let foes: Vec<(usize, bool, Pt)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() != team && u.is_alive() && !u.is_tower() && u.is_targetable())
                .map(|u| (u.id(), u.is_champion(), (u.pos().0 as f64, u.pos().1 as f64)))
                .collect();
            let kinds: Vec<(bool, Pt)> = foes.iter().map(|f| (f.1, f.2)).collect();
            let from = self.bodies.shatter_from(at);
            let p = lunge(from, &kinds, THRALL_LUNGE);
            let input = InputTargetV1::pos(p.0.round() as u64, p.1.round() as u64);
            sim.play_view_effect(THRALL_BURST, me, &input, 0, 0, 0);
            sim.play_sfx(THRALL_BURST, me, &input);
            let hit: Vec<usize> = foes.iter().filter(|f| dist(f.2, p) <= THRALL_R).map(|f| f.0).collect();
            let damage = THRALL_BASE + power * THRALL_AP / 100;
            for id in &hit {
                sim.deal_damage_typed(me, *id, damage, DamageTypeV1::Ap, AttackTypeV1::Skill);
                let mut slow = BuffV1::timed(THRALL_SLOW.0, THRALL_SLOW.1);
                slow.move_speed_mult = THRALL_SLOW.2;
                sim.add_buff(*id, &slow);
                sim.play_sfx(THRALL_HIT, me, &InputTargetV1::target(*id));
            }
            self.n += 1;
            if self.n <= 80 {
                // where the thrall rose from (0.2.6): one listed dead, or one gone from the list; a lunge at nothing says
                // how far the nearest enemies stood
                let missed = if p == from { format!(" ({})", nearest_text(from, &kinds)) } else { String::new() };
                wlog(format!("{} THRALL #{} rose at ({:.0}, {:.0}) where {how}, walked {:.0}, lunged {:.0}, shattered: {} enemies hit for {damage}{missed}",
                             head(sim, me), self.n, at.0, at.1, dist(at, from), dist(from, p), hit.len()));
            }
        }
    }
}

// ===================== 被动 =====================

#[derive(Clone)]
struct Low {
    hero: &'static str,
    flag: &'static str,
    pct: usize,
    was: bool,
    n: usize,
    thralls: Option<Thralls>,
}

impl StablePassive for Low {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.was = false;
        wlog(format!("{} SPAWN: the add-on's {} (player {player}), low at {}%", head(sim, me), self.hero, self.pct));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(alive) = sim.get_entity(me).map(|e| e.is_alive()) else { return };
        if let Some(t) = self.thralls.as_mut() {
            t.update(sim, me, alive);
        }
        let Some(e) = sim.get_entity(me) else { return };
        if !alive {
            self.was = false;
            return;
        }
        let (hp, max) = e.hp();
        let now = low(hp, max, self.pct);
        if now {
            sim.entity_remove_buff(me, self.flag);
            sim.add_buff(me, &BuffV1::timed(self.flag, HOLD));
        }
        if now && !self.was {
            self.n += 1;
            if self.n <= 80 {
                wlog(format!("{} LOW #{}: hp {hp}/{max}", head(sim, me), self.n));
            }
        }
        self.was = now;
    }

    /// Her death also takes her pending thralls and what she saw (0.2.2, the 2026-11-01 review): a dead champion's update
    /// does not run, so a thrall raised just before her death shattered only at her respawn (10-60 s late, on whoever
    /// stood there by then), and an enemy who died while she was dead raised a thrall at her first update.
    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.was = false;
        if let Some(t) = self.thralls.as_mut() {
            t.rising.clear();
            t.seen.clear();
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Blitzcrank's Mana Barrier, LeBlanc's Mirror Image, Lissandra's self-tomb on low health and her thralls) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    for (hero, name, flag, pct) in HEROES {
        let thralls = (name == "lissandra").then(Thralls::default);
        module.add_native_passive(format!("{ID}:{name}"), Low { hero, flag, pct, was: false, n: 0, thralls });
    }
    // 0.3.1: her thralls as units (src/thralls.rs)
    wlog(format!("THRALLS: Lissandra's thralls are units ('{}', spawn_unit: her pace, no attack, cannot be hurt) - {}; they shatter \
                  from where they walked. Test knobs ({}): {}", thralls::THRALL_UNIT,
                 if thralls::KNOBS.off { "OFF by the test knobs: the thrall's picture as before" } else { "ON" },
                 LOG_PATH.with_extension("cfg").display(), thralls::KNOBS.shown()));
    module.add_native_effect(format!("{ID}:thrall"), thralls::ThrallFx);
    host.log(LogLevel::Info, "league_lowhp v1 loaded (three passives on low health).");
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
    fn low_is_at_the_line_or_under() {
        assert!(low(300, 1000, 30));
        assert!(!low(301, 1000, 30));
        assert!(low(0, 0, 30));
    }

    #[test]
    fn thralls_rise_from_deaths_near_her() {
        let before: HashMap<usize, (bool, Pt)> =
            [(1, (true, (10_000.0, 0.0))), (2, (true, (200_000.0, 0.0))), (3, (false, (0.0, 0.0)))].into();
        let now = [(1, false, (0.0, 0.0)), (2, false, (0.0, 0.0)), (3, false, (0.0, 0.0)), (4, false, (0.0, 0.0))];
        assert_eq!(fallen(&before, &now, (0.0, 0.0), THRALL_REACH), vec![(10_000.0, 0.0)]);
    }

    #[test]
    fn a_champion_whose_entity_is_gone_fell_where_it_stood() {
        // the 11-03 night logs: 0 THRALL in a game with Lissandra - the dead champion's entity is gone by the next tick,
        // so 0.2.2 never saw it listed as dead
        let before: HashMap<usize, (bool, Pt)> = [(9, (true, (30_000.0, 0.0))), (5, (true, (0.0, 20_000.0))),
            (7, (true, (200_000.0, 0.0))), (8, (false, (1_000.0, 0.0))), (6, (true, (5_000.0, 0.0)))].into();
        // 6 still alive, 8 was already dead last tick, 7 gone but too far, 5 and 9 gone near her
        let now = [(6, true, (6_000.0, 0.0))];
        assert_eq!(fallen(&before, &now, (0.0, 0.0), THRALL_REACH), vec![(0.0, 20_000.0), (30_000.0, 0.0)],
                   "both, by id (the same order in every sim)");
        // one listed dead comes first, then the ones gone
        let now = [(6, false, (6_000.0, 0.0))];
        assert_eq!(fallen(&before, &now, (0.0, 0.0), THRALL_REACH), vec![(5_000.0, 0.0), (0.0, 20_000.0), (30_000.0, 0.0)]);
        // nothing seen before (her first update, or after her own death): nothing falls
        assert!(fallen(&HashMap::new(), &now, (0.0, 0.0), THRALL_REACH).is_empty());
        // everyone still there and alive: nothing
        let all: Vec<(usize, bool, Pt)> = before.iter().map(|(id, b)| (*id, b.0, b.1)).collect();
        assert!(fallen(&before, &all, (0.0, 0.0), THRALL_REACH).is_empty());
    }

    #[test]
    fn thralls_lunge_at_the_nearest_champion_first() {
        let p = (0.0, 0.0);
        let foes = [(false, (5_000.0, 0.0)), (true, (40_000.0, 0.0)), (true, (30_000.0, 0.0)), (true, (-80_000.0, 0.0))];
        assert_eq!(lunge(p, &foes, THRALL_LUNGE), (30_000.0, 0.0));
        assert_eq!(lunge(p, &foes[..1], THRALL_LUNGE), (5_000.0, 0.0));
        assert_eq!(lunge(p, &foes[3..], THRALL_LUNGE), p);
        assert_eq!(lunge(p, &[], THRALL_LUNGE), p);
    }

    #[test]
    fn thralls_reach_as_far_as_leagues_chase() {
        // 11-06's logs: 31 of 42 thralls "lunged 0, shattered: 0 enemies hit" - nobody within 45000. League's thrall
        // chases for 4 s at 33 -> 325 speed: about 720 units, 72000 here
        assert_eq!(THRALL_LUNGE, 72_000.0);
        let p = (0.0, 0.0);
        assert_eq!(lunge(p, &[(true, (60_000.0, 0.0))], THRALL_LUNGE), (60_000.0, 0.0), "45000 missed him");
        assert_eq!(lunge(p, &[(true, (72_001.0, 0.0))], THRALL_LUNGE), p);
        // a lunge at nothing says how far the nearest enemies stood
        assert_eq!(nearest_text(p, &[(true, (90_000.0, 0.0)), (false, (75_500.4, 0.0))]),
                   "nearest enemy champion 90000, unit 75500");
        assert_eq!(nearest_text(p, &[]), "nearest enemy champion none, unit none");
    }

    #[test]
    fn the_thrall_line_says_how_the_champion_fell() {
        let k = |tick, killer_team, killed_position| KillLogV1 { tick, killer_team, killed_position, ..KillLogV1::default() };
        // team 1's lane 2 killed by team 0 at 24363, seen gone at 24364
        let log = [k(24_000, 1, 3), k(24_363, 0, 2)];
        assert!(death_logged(&log, 1, 2, 24_364));
        assert!(!death_logged(&log, 1, 2, 24_367), "too old for this fall");
        assert!(!death_logged(&log, 1, 3, 24_364), "another lane");
        assert!(!death_logged(&log, 0, 2, 24_364), "lane 2 of the other team");
        assert_eq!(fall_text(false, Some(false)), "one left the list with NO death in the kill log");
        assert_eq!(fall_text(false, Some(true)), "one left the list (a death in the kill log)");
        assert_eq!(fall_text(true, Some(true)), "one died (kill log)");
        // who fell, and how: one listed dead, one gone
        let before: HashMap<usize, (bool, Pt)> = [(5, (true, (0.0, 20_000.0))), (6, (true, (5_000.0, 0.0)))].into();
        assert_eq!(fallen_kinds(&before, &[(6, false, (0.0, 0.0))], (0.0, 0.0), THRALL_REACH),
                   vec![(6, (5_000.0, 0.0), true), (5, (0.0, 20_000.0), false)]);
    }

    #[test]
    fn the_names_fit() {
        for (_, _, flag, _) in HEROES {
            assert!(flag.len() <= BUFF_NAME_CAP);
        }
    }
}
