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
//! 内由活变死，就在他倒下的地方播主包的冰仆画面，`THRALL_TICKS` 后碎裂：播主包的碎裂画面和声音，`THRALL_R` 内的敌人（英雄、
//! 小兵、野怪）受到 150 + 70% 法强的魔法伤害、减速 25% 1.5 秒（同主包）。冰仆不会走（画面是挂在地上的，走了画面跟不上）；
//! v0.2.1 起碎裂时扑向 `THRALL_LUNGE` 内最近的敌方英雄（没有英雄就最近的小兵、野怪），在他身上碎裂：原地碎裂 22 次只有 4 次
//! 炸到人（1.5 秒后尸体边上没人了）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_lowhp.log`。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

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
pub const THRALL_REACH: f64 = 90_000.0;
pub const THRALL_TICKS: usize = 90;
pub const THRALL_LUNGE: f64 = 45_000.0;
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
pub fn fallen(before: &HashMap<usize, (bool, Pt)>, now: &[(usize, bool, Pt)], me: Pt, reach: f64) -> Vec<Pt> {
    now.iter()
        .filter(|(id, alive, _)| !alive && before.get(id).is_some_and(|b| b.0))
        .map(|(id, _, _)| before[id].1)
        .filter(|p| dist(*p, me) <= reach)
        .collect()
}

/// Where a thrall at `p` shatters: on the nearest enemy champion within `reach`, else the nearest other enemy there, else
/// where it stands. `foes`: (champion, where) of the enemies it can hit.
pub fn lunge(p: Pt, foes: &[(bool, Pt)], reach: f64) -> Pt {
    let near = |champ: bool| foes.iter().filter(|f| f.0 == champ).map(|f| f.1).filter(|q| dist(*q, p) <= reach)
        .min_by(|a, b| dist(*a, p).total_cmp(&dist(*b, p)));
    near(true).or_else(|| near(false)).unwrap_or(p)
}

/// 丽桑卓的冰仆：上一 tick 敌方英雄的死活和位置，等着碎裂的冰仆（碎裂的 tick、位置）。
#[derive(Clone, Default)]
struct Thralls {
    seen: HashMap<usize, (bool, Pt)>,
    rising: Vec<(usize, Pt)>,
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
            for p in fallen(&self.seen, &now, at, THRALL_REACH) {
                let input = InputTargetV1::pos(p.0.round() as u64, p.1.round() as u64);
                sim.play_view_effect(THRALL_VIEW, me, &input, 0, 0, 0);
                sim.play_sfx(THRALL_RISE, me, &input);
                self.rising.push((tick + THRALL_TICKS, p));
            }
        }
        self.seen = now.iter().map(|(id, a, p)| (*id, (*a, *p))).collect();
        let due: Vec<Pt> = self.rising.iter().filter(|r| r.0 <= tick).map(|r| r.1).collect();
        self.rising.retain(|r| r.0 > tick);
        for at in due {
            let foes: Vec<(usize, bool, Pt)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() != team && u.is_alive() && !u.is_tower() && u.is_targetable())
                .map(|u| (u.id(), u.is_champion(), (u.pos().0 as f64, u.pos().1 as f64)))
                .collect();
            let p = lunge(at, &foes.iter().map(|f| (f.1, f.2)).collect::<Vec<_>>(), THRALL_LUNGE);
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
                wlog(format!("{} THRALL #{} rose at ({:.0}, {:.0}), lunged {:.0}, shattered: {} enemies hit for {damage}",
                             head(sim, me), self.n, at.0, at.1, dist(at, p), hit.len()));
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
    fn thralls_lunge_at_the_nearest_champion_first() {
        let p = (0.0, 0.0);
        let foes = [(false, (5_000.0, 0.0)), (true, (40_000.0, 0.0)), (true, (30_000.0, 0.0)), (true, (-50_000.0, 0.0))];
        assert_eq!(lunge(p, &foes, THRALL_LUNGE), (30_000.0, 0.0));
        assert_eq!(lunge(p, &foes[..1], THRALL_LUNGE), (5_000.0, 0.0));
        assert_eq!(lunge(p, &foes[3..], THRALL_LUNGE), p);
        assert_eq!(lunge(p, &[], THRALL_LUNGE), p);
    }

    #[test]
    fn the_names_fit() {
        for (_, _, flag, _) in HEROES {
            assert!(flag.len() <= BUFF_NAME_CAP);
        }
    }
}
