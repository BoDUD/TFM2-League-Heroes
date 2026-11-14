//! 蕾欧娜附加包：日光按英雄联盟由队友引爆（用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」，再说
//! 「接着做」：能做的小项都做）。
//!
//! 英雄联盟的日光（被动）："Leona's abilities mark enemies hit"，2.5 秒（V25.09），"Allied champions' damaging attacks and
//! abilities against a marked target" 引爆它，造成 32–151（随她的等级）魔法伤害；她自己的攻击不引爆。主包是纯数据：数据
//! 分不清谁打中了带标记的敌人，所以日光是「被她技能命中的敌人 1.5 秒内受到的所有伤害 +10%」，没有队友引爆这一步。
//!
//! `mod.override_info` 把主包的蕾欧娜换成 `override/` 里的副本（`make_override.py` 从主包生成）：她的 Q、E、W 爆发、R 照样给
//! 打中的敌人挂 `league_leona_sunlight`（画面照主包），只是不再带增伤、挂 `MARK_T` tick（2.5 秒）；被动换成本包的
//! `league_leona:sunlight`，普攻（写着被动）的说明换成本包的。本包的被动每 tick 看她这边每个友方英雄（不算她自己）出没出手
//! （冷却跳起来就是出手了），再看这一下真的打中了谁（[`allies`]，league_milio 的做法：观察钩子记下 AI 下令打谁，治疗、护盾、给
//! 队友的技能、打塔都不算；那个人在出手前后的窗口里真的掉了血才算）：打中的人带着日光就引爆：摘掉日光，按她的等级造成
//! [`sunlight_damage`] 的魔法伤害（算她的），目标身上播主包 Q 的日光闪 `POP_VIEW`。等级换算：英雄联盟 1–18 级的 32–151 线性摊到
//! 这个游戏的 1–12 级。
//!
//! 被动在玩家身上、每份模拟各一份；她阵亡时被动不跑，标记照样到时消失，不引爆。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_leona.log`，每次启动游戏重写，上一次的留在 .prev.log：`SPAWN`、
//! `POP`（哪个队友引爆了谁、多少伤害），限了条数。

use std::collections::{HashMap, VecDeque};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod allies;
use allies::{Drop, Swing};

const ID: &str = "league_leona";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_leona") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 日光的标记（主包数据的名字：画面、league_eggs 的墨镜、league_zyra 的光合作用都认它）和副本里挂的时长（英雄联盟 2.5 秒）。
pub const MARK: &str = "league_leona_sunlight";
pub const MARK_T: usize = 150;
/// 引爆的魔法伤害：1 级 `DMG_MIN`，`MAX_LEVEL` 级 `DMG_MAX`（英雄联盟 1–18 级的 32–151 摊到这个游戏的 1–12 级）。
pub const DMG_MIN: usize = 32;
pub const DMG_MAX: usize = 151;
pub const MAX_LEVEL: usize = 12;
/// 引爆时目标身上播的画面（主包 Q 打中时的日光闪）。
pub const POP_VIEW: &str = "league_leona_q_hit";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LEONA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_leona.log");
        }
    }
    PathBuf::from("league_leona.log")
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

const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    format!("{}#{id}", sim.get_entity(id).and_then(|e| e.name()).unwrap_or_default())
}

// ===================== 规则（单元测试用） =====================

/// 引爆的魔法伤害（她的等级 `level`）：1 级 `DMG_MIN` 到 `MAX_LEVEL` 级 `DMG_MAX`，中间线性。
pub fn sunlight_damage(level: usize) -> usize {
    let l = level.clamp(1, MAX_LEVEL);
    DMG_MIN + (DMG_MAX - DMG_MIN) * (l - 1) / (MAX_LEVEL - 1)
}

/// 队友的冷却计数比上一 tick 跳高了：这个栏位刚用掉（跳高 5 tick 以上才算，冷却本来就在走的不算）。
pub fn used(was: usize, now: usize) -> bool {
    now > was + 5
}

/// 上一 tick 和这一 tick 的冷却（普攻、技能、技能 2、大招）：第一个刚用掉的栏位（0 普攻、1-3 技能）。
pub fn jumped(was: (usize, usize, usize, usize), now: (usize, usize, usize, usize)) -> Option<usize> {
    [used(was.0, now.0), used(was.1, now.1), used(was.2, now.2), used(was.3, now.3)].iter().position(|j| *j)
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn tower(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_tower() || matches!(e.kind(), Some(EntityKindV1::Tower | EntityKindV1::Nexus)))
}

// ===================== 被动：日光 =====================

#[derive(Clone, Default)]
struct Sunlight {
    /// 这份模拟的编号（她第一次出生时取，挂在她身上给观察钩子读）。
    sim_no: u64,
    /// 她这边各玩家上一 tick 的冷却（普攻、技能、技能 2、大招）。
    last_cd: HashMap<usize, (usize, usize, usize, usize)>,
    /// 每个队友正在等结果的那次出手（一人一次）；他上一下认过的那次掉血的 tick。
    swings: HashMap<usize, Swing>,
    taken: HashMap<usize, usize>,
    /// 带日光的敌方单位上一 tick 的生命 + 护盾；最近掉的血。
    marked: HashMap<usize, usize>,
    drops: VecDeque<Drop>,
}

impl Sunlight {
    /// 带日光的敌方单位：这一 tick 掉了多少（生命 + 护盾；没带日光的不记，她自己的 Q 挂上日光那一下的伤害也就不算）。
    fn track(&mut self, sim: &StableSim<'_>, team: usize, now: usize) {
        let mut marked = HashMap::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || u.is_tower() || matches!(u.kind(), Some(EntityKindV1::Tower | EntityKindV1::Nexus)) {
                continue;
            }
            let id = u.id();
            if !(0..u.buff_count()).filter_map(|k| u.buff_at(k)).any(|b| b.name() == MARK) {
                continue;
            }
            let left = if u.is_alive() { u.hp().0 + u.shield() } else { 0 };
            if let Some(&was) = self.marked.get(&id) {
                if was > left {
                    self.drops.push_back(Drop { tick: now, id, at: fpos(u.pos()), amount: was - left });
                }
            }
            if u.is_alive() {
                marked.insert(id, left);
            }
        }
        self.marked = marked;
        while self.drops.front().is_some_and(|d| d.tick + allies::KEEP < now) {
            self.drops.pop_front();
        }
    }

    /// 队友出手：冷却跳起来就开始等它的结果（治疗、护盾、打塔不算）；真的打中了带日光的人就引爆。
    fn ally_hits(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, now: usize) {
        let mut from: HashMap<usize, (f64, f64)> = HashMap::new();
        for i in 0..sim.player_count() {
            let Some(pl) = sim.player_at(i) else { continue };
            let pid = pl.id();
            let Some(c) = pl.champion() else { continue };
            if c.team() != team || c.id() == me {
                continue;
            }
            let Some(cd) = pl.cooldowns() else { continue };
            let was = self.last_cd.insert(pid, cd);
            let ally = c.id();
            if !c.is_alive() {
                self.swings.remove(&ally);
                continue;
            }
            from.insert(ally, fpos(c.pos()));
            if self.swings.contains_key(&ally) {
                continue;
            }
            let Some(slot) = was.and_then(|was| jumped(was, cd)) else { continue };
            let o = allies::orders_of(self.sim_no, ally);
            let st = c.stat();
            let floor = self.taken.get(&ally).map_or(0, |t| t + 1);
            if let Some(sw) = allies::open(&o, slot, now, |id| tower(sim, id), st.attack, st.magic_power, floor) {
                self.swings.insert(ally, sw);
            }
        }
        if self.swings.is_empty() {
            return;
        }
        let mut done: Vec<(usize, Option<(usize, bool)>)> = Vec::new();
        let mut keys: Vec<usize> = self.swings.keys().copied().collect();
        keys.sort_unstable();
        for ally in keys {
            let sw = self.swings[&ally];
            let Some(&at) = from.get(&ally) else {
                done.push((ally, None));
                continue;
            };
            let marked = |id: usize| sim.get_entity(id).is_some_and(|e| e.is_alive()) && has_buff(sim, id, MARK);
            if let Some((t, at_tick)) = allies::hit_of(&sw, &self.drops, at, marked) {
                self.taken.insert(ally, at_tick);
                done.push((ally, Some((t, sw.target.is_some()))));
            } else if now > sw.until {
                done.push((ally, None));
            }
        }
        for (ally, hit) in done {
            self.swings.remove(&ally);
            if let Some((foe, ordered)) = hit {
                if sim.get_entity(foe).is_some_and(|e| e.is_alive()) && has_buff(sim, foe, MARK) {
                    Self::pop(sim, me, foe, ally, ordered);
                }
            }
        }
    }

    fn pop(sim: &mut StableSim<'_>, me: usize, foe: usize, ally: usize, ordered: bool) {
        let level = sim.get_entity(me).map_or(1, |e| e.level());
        let dmg = sunlight_damage(level);
        sim.entity_remove_buff(foe, MARK);
        let ok = sim.deal_damage_typed(me, foe, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        sim.play_view_effect(POP_VIEW, me, &InputTargetV1::target(foe), 0, 0, 0);
        if let Some(k) = counted("pop") {
            wlog(format!("{} POP #{k}: {} hit {} ({}) -> {dmg} magic (level {level}){}", head(sim, me), who(sim, ally),
                         who(sim, foe), if ordered { "ordered at it" } else { "guessed from the drops" },
                         if ok { "" } else { " (refused)" }));
        }
    }
}

impl StablePassive for Sunlight {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if self.sim_no == 0 {
            self.sim_no = allies::next_sim();
        }
        allies::tag(sim, me, self.sim_no);
        self.swings.clear();
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Leona (player {player}, sim {})", head(sim, me), self.sim_no));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        let Some(team) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.team()) else {
            self.swings.clear();
            return;
        };
        self.track(sim, team, now);
        self.ally_hits(sim, me, team, now);
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        self.swings.clear();
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Leona: Sunlight marks, detonated by allied champions' hits) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:sunlight"), Sunlight::default());
    module.add_player_input_ai(allies::Watch::default());
    host.log(LogLevel::Info, "league_leona loaded (Sunlight detonated by allied champions' hits).");
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
    fn the_damage_runs_from_32_to_151_over_twelve_levels() {
        assert_eq!(sunlight_damage(1), 32);
        assert_eq!(sunlight_damage(12), 151);
        assert_eq!(sunlight_damage(0), 32, "no level read: level 1");
        assert_eq!(sunlight_damage(18), 151, "capped at the game's top level");
        assert_eq!(sunlight_damage(6), 32 + 119 * 5 / 11);
        assert!((1..12).all(|l| sunlight_damage(l) < sunlight_damage(l + 1)), "it grows every level");
    }

    #[test]
    fn a_jump_in_a_cooldown_is_the_slot_just_used() {
        assert_eq!(jumped((0, 0, 0, 0), (60, 0, 0, 0)), Some(0));
        assert_eq!(jumped((0, 100, 0, 0), (0, 99, 0, 0)), None, "a cooldown running down is nothing");
        assert_eq!(jumped((10, 0, 0, 0), (12, 0, 0, 0)), None, "a jump of 5 ticks or less is nothing");
        assert_eq!(jumped((0, 0, 0, 0), (0, 0, 480, 0)), Some(2));
        assert_eq!(jumped((0, 0, 0, 0), (0, 0, 0, 3000)), Some(3));
        assert_eq!(jumped((0, 0, 0, 0), (80, 300, 0, 0)), Some(0), "an attack and a cast together: the attack");
    }

    #[test]
    fn a_heal_only_cast_pops_nothing_and_a_damaging_cast_pops() {
        use allies::{hit_of, open, Aim, Orders};
        let marked = |_: usize| true;
        let mut drops = VecDeque::new();
        // Soraka's W on an ally: ordered at a friend - no swing at all, whatever drops near her
        let heal = Orders { skill: [None, Some((500, Aim::Friend)), None], ..Orders::default() };
        assert_eq!(open(&heal, 2, 530, |_| false, 75, 200, 0), None);
        // a cast that only arms something (no order recorded, a place / self cast) and nothing marked near lost health
        let arm = open(&Orders::default(), 3, 530, |_| false, 75, 200, 0).expect("watched");
        assert_eq!(hit_of(&arm, &drops, (0.0, 0.0), marked), None);
        // a damaging skill ordered at the marked enemy: its health drop during the action pops it
        let hit = Orders { skill: [Some((480, Aim::Foe(9))), None, None], ..Orders::default() };
        let sw = open(&hit, 1, 530, |_| false, 75, 200, 0).expect("watched");
        drops.push_back(Drop { tick: 515, id: 9, at: (20_000.0, 0.0), amount: 140 });
        assert_eq!(hit_of(&sw, &drops, (0.0, 0.0), marked).map(|h| h.0), Some(9));
        // an attack ordered at a tower: nothing, even with the marked enemy beside it losing health
        let tower_hit = Orders { attack: Some((500, 77)), ..Orders::default() };
        assert_eq!(open(&tower_hit, 0, 520, |id| id == 77, 75, 0, 0), None);
    }

    #[test]
    fn the_copy_marks_without_the_damage_bonus_and_calls_the_passive() {
        let copy = include_str!("../override/league_leona.data_champion").replace("\r\n", "\n");
        assert!(copy.contains("\"passive_ref\": \"league_leona:sunlight\""), "the copy has no league_leona:sunlight passive");
        let marks = copy.matches(&format!("\"name\": \"{MARK}\"")).count();
        // Q, the solar blade, Eclipse's burst, the ult's zone (and the mark's picture in view_buffs)
        assert_eq!(marks, 5, "the main pack's Sunlight is added in {marks} places now: update this test / make_override.py");
        assert!(!copy.contains("\"damaged_amplify\""), "a mark still carries the main pack's +10% damage taken");
        assert_eq!(copy.matches(&format!("\"tick\": {MARK_T}")).count(), 4, "every mark lasts MARK_T ticks");
        assert!(copy.contains("description.league_leona_addon.attack"));
        assert!(copy.contains(&format!("\"name\": \"{POP_VIEW}\"")), "the pop's picture is not in the copy's views");
    }
}
