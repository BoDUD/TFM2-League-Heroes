//! 娜美附加包：唤潮之佑按英雄联盟强化被祝福者接下来的三次命中（用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说
//! 「全改吧」，再说「接着做」：能做的小项都做）。
//!
//! 英雄联盟的唤潮之佑（E）："Nami blesses herself or an allied champion for 6 seconds, empowering their next 3 basic attacks
//! or abilities to each deal bonus magic damage and slow enemies for 1 second"（每下 20–80 + 20% 法强，减速 15–35%）。这里没有
//! 第四个技能位，主包把它并进冲击之潮（Q）：被治疗的人 4 秒内攻击力、法强 +15%，减速放在水流自己的伤害上——数据读不到
//! 别人的出手。
//!
//! `mod.override_info` 把主包的娜美换成 `override/` 里的副本（`make_override.py` 从主包生成）：冲击之潮照样治疗、照样给被治疗
//! 的人挂 `league_nami_e_blessing`（画面照主包），只是不再加攻击力、法强，挂 `BLESS_T` tick（6 秒）；水流打中的敌人不再减速；
//! 被动换成本包的 `league_nami:tide`，冲击之潮的说明换成本包的。本包的被动每 tick 看她这边带着祝福的英雄（她自己也算）：
//! 祝福新挂上（或刷新）就有 `CHARGES` 次；他出手（league_renata / league_leona 的做法：普攻、技能的冷却跳起来就是出手了）
//! 时用掉一次——普攻算他 `ATTACK_REACH` 内最近的敌方单位，技能算他 `SKILL_REACH` 内最近的敌方英雄，身边没有敌人的出手不算；
//! `POP_WAIT` tick 后（前摇加飞行）那个人还活着就受到 `DMG` + `DMG_AP`% 娜美法强的魔法伤害（算娜美的）并减速 `SLOW`%
//! `SLOW_T` tick（`league_nami_e_slow`，换掉旧的，不叠）。三次用完就摘掉祝福。
//!
//! 被动在玩家身上、每份模拟各一份；她阵亡时被动不跑，那段时间祝福不生效（照样到时消失）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nami.log`，每次启动游戏重写，上一次的留在 .prev.log：`SPAWN`、
//! `BLESS`（谁拿到祝福）、`TIDE`（谁的第几次命中打了谁、多少伤害），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_nami";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_nami") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 祝福（主包数据的名字，画面绑在它上面）和副本里挂的时长（英雄联盟 6 秒）、次数（3 次）。
pub const BLESS: &str = "league_nami_e_blessing";
pub const BLESS_T: usize = 360;
pub const CHARGES: usize = 3;
/// 每次命中的魔法伤害：固定值 + 娜美法强 %（英雄联盟 20 / 35 / 50 / 65 / 80 + 20%：取中间一级）。
pub const DMG: usize = 50;
pub const DMG_AP: usize = 20;
/// 每次命中的减速 % 和时长（英雄联盟 15–35% 1 秒：取主包水流的 25%）；减速 buff（主包水流的名字）。
pub const SLOW: i32 = 25;
pub const SLOW_T: usize = 60;
pub const SLOW_BUFF: &str = "league_nami_e_slow";
/// 命中时目标身上播的画面（主包普攻的水花）。
pub const HIT_VIEW: &str = "league_nami_hit";
/// 出手（冷却跳起）后多少 tick 算打中：普攻的前摇加飞行（league_renata 的 POP_WAIT）。
const POP_WAIT: usize = 10;
/// 普攻：他这么远内最近的敌方单位就是他打的；技能：这么远内最近的敌方英雄。
const ATTACK_REACH: f64 = 75_000.0;
const SKILL_REACH: f64 = 90_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_NAMI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_nami.log");
        }
    }
    PathBuf::from("league_nami.log")
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

/// 每次命中的魔法伤害（娜美的法强 `ap`）。
pub fn tide_damage(ap: usize) -> usize {
    DMG + DMG_AP * ap / 100
}

/// 上一 tick 和这一 tick 的冷却（普攻、技能、技能 2、大招）：`Some(true)` 普攻出手了，`Some(false)` 放了技能，`None` 都没有
/// （league_renata 的 `swung`：跳高 5 tick 以上才算）。
pub fn swung(was: (usize, usize, usize, usize), now: (usize, usize, usize, usize)) -> Option<bool> {
    if now.0 > was.0 + 5 {
        Some(true)
    } else if now.1 > was.1 + 5 || now.2 > was.2 + 5 || now.3 > was.3 + 5 {
        Some(false)
    } else {
        None
    }
}

/// 祝福的次数：上一 tick 记的 (剩几次, 祝福还剩几 tick) 和这一 tick 他身上祝福还剩的 tick（`None` = 没有）。新挂上或刷新了
/// （剩的 tick 比上次多）就是满的 `CHARGES` 次。
pub fn charges_now(last: Option<(usize, usize)>, left: Option<usize>) -> Option<(usize, usize)> {
    let left = left?;
    Some(match last {
        Some((n, was)) if left <= was => (n, left),
        _ => (CHARGES, left),
    })
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 他身上祝福还剩的 tick（几层取最长的），没有就是 `None`。
fn blessing_left(sim: &StableSim<'_>, id: usize) -> Option<usize> {
    let e = sim.get_entity(id)?;
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == BLESS).map(|b| b.duration_tick).max()
}

/// `team` 的对手里离 `at` 最近的单位（活着、选得中、不是塔、水晶），`reach` 以内；`champion` 时只看英雄。
fn nearest_foe(sim: &StableSim<'_>, team: usize, at: (f64, f64), reach: f64, champion: bool) -> Option<usize> {
    let mut best: Option<(usize, f64)> = None;
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower() || (champion && !u.is_champion()) {
            continue;
        }
        if matches!(u.kind(), Some(EntityKindV1::Nexus) | Some(EntityKindV1::Tower)) {
            continue;
        }
        let d = dist(at, fpos(u.pos()));
        if d <= reach && best.is_none_or(|b| d < b.1) {
            best = Some((u.id(), d));
        }
    }
    best.map(|b| b.0)
}

// ===================== 被动：唤潮之佑 =====================

#[derive(Clone, Default)]
struct Tide {
    /// 她这边各玩家上一 tick 的冷却（普攻、技能、技能 2、大招）。
    last_cd: HashMap<usize, (usize, usize, usize, usize)>,
    /// 带祝福的英雄 -> (还剩几次, 祝福上一 tick 还剩几 tick)。
    blessed: HashMap<usize, (usize, usize)>,
    /// 等着打中的强化命中：(出手的英雄, 敌方单位, 第几 tick 打中, 第几次)。
    pending: Vec<(usize, usize, usize, usize)>,
}

impl Tide {
    fn watch(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, now: usize) {
        for i in 0..sim.player_count() {
            let Some(pl) = sim.player_at(i) else { continue };
            let pid = pl.id();
            let Some(c) = pl.champion() else { continue };
            if c.team() != team {
                continue;
            }
            let (ally, alive, at) = (c.id(), c.is_alive(), fpos(c.pos()));
            let cd = pl.cooldowns();
            let was = cd.and_then(|cd| self.last_cd.insert(pid, cd));
            let left = if alive { blessing_left(sim, ally) } else { None };
            let last = self.blessed.get(&ally).copied();
            let Some((mut n, left)) = charges_now(last, left) else {
                self.blessed.remove(&ally);
                continue;
            };
            if last.is_none_or(|(_, was_left)| left > was_left) {
                if let Some(k) = counted("bless") {
                    wlog(format!("{} BLESS #{k}: {} ({} ticks, {n} hits)", head(sim, me), who(sim, ally), left));
                }
            }
            let (Some(was), Some(cd)) = (was, cd) else {
                self.blessed.insert(ally, (n, left));
                continue;
            };
            let foe = match swung(was, cd) {
                Some(true) => nearest_foe(sim, team, at, ATTACK_REACH, false),
                Some(false) => nearest_foe(sim, team, at, SKILL_REACH, true),
                None => None,
            };
            if let (Some(f), true) = (foe, n > 0) {
                self.pending.push((ally, f, now + POP_WAIT, CHARGES + 1 - n));
                n -= 1;
            }
            if n == 0 {
                // the third empowered hit is on its way: the blessing (and its picture) goes
                sim.entity_remove_buff(ally, BLESS);
                self.blessed.remove(&ally);
            } else {
                self.blessed.insert(ally, (n, left));
            }
        }
        let due: Vec<(usize, usize, usize, usize)> = self.pending.iter().copied().filter(|p| p.2 <= now).collect();
        self.pending.retain(|p| p.2 > now);
        for (ally, foe, _, nth) in due {
            if sim.get_entity(foe).is_some_and(|e| e.is_alive()) {
                Self::hit(sim, me, ally, foe, nth);
            }
        }
    }

    fn hit(sim: &mut StableSim<'_>, me: usize, ally: usize, foe: usize, nth: usize) {
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let dmg = tide_damage(ap);
        let ok = sim.deal_damage_typed(me, foe, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        let mut slow = BuffV1::timed(SLOW_BUFF, SLOW_T);
        slow.move_speed_mult = -SLOW;
        sim.entity_remove_buff(foe, SLOW_BUFF);
        sim.add_buff(foe, &slow);
        sim.play_view_effect(HIT_VIEW, me, &InputTargetV1::target(foe), 0, 0, 0);
        if let Some(k) = counted("tide") {
            wlog(format!("{} TIDE #{k}: {}'s hit {nth}/{CHARGES} on {} -> {dmg} magic, slowed {SLOW}%{}", head(sim, me),
                         who(sim, ally), who(sim, foe), if ok { "" } else { " (refused)" }));
        }
    }
}

impl StablePassive for Tide {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.pending.clear();
        self.blessed.clear();
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Nami (player {player})", head(sim, me)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        let Some(team) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.team()) else {
            self.pending.clear();
            return;
        };
        self.watch(sim, me, team, now);
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        self.pending.clear();
        self.blessed.clear();
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Nami: Tidecaller's Blessing empowers the next {CHARGES} hits) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:tide"), Tide::default());
    host.log(LogLevel::Info, "league_nami loaded (Tidecaller's Blessing on the blessed champion's next hits).");
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
    fn each_hit_deals_fifty_and_a_fifth_of_her_power() {
        assert_eq!(tide_damage(0), 50);
        assert_eq!(tide_damage(200), 90);
        assert_eq!(3 * tide_damage(100), 210, "three hits: 150 + 60% AP");
    }

    #[test]
    fn a_new_or_refreshed_blessing_has_three_hits() {
        assert_eq!(charges_now(None, None), None);
        assert_eq!(charges_now(None, Some(360)), Some((3, 360)), "a new blessing");
        assert_eq!(charges_now(Some((2, 300)), Some(299)), Some((2, 299)), "one used, running down");
        assert_eq!(charges_now(Some((1, 100)), Some(360)), Some((3, 360)), "blessed again: full");
        assert_eq!(charges_now(Some((2, 5)), None), None, "it ran out");
    }

    #[test]
    fn a_jump_in_a_cooldown_is_a_swing_or_a_cast() {
        assert_eq!(swung((0, 0, 0, 0), (60, 0, 0, 0)), Some(true));
        assert_eq!(swung((0, 100, 0, 0), (0, 99, 0, 0)), None);
        assert_eq!(swung((0, 0, 0, 0), (0, 420, 0, 0)), Some(false));
    }

    #[test]
    fn the_copy_blesses_without_the_stat_bonus_and_calls_the_passive() {
        let copy = include_str!("../override/league_nami.data_champion").replace("\r\n", "\n");
        assert!(copy.contains("\"passive_ref\": \"league_nami:tide\""), "the copy has no league_nami:tide passive");
        let marks = copy.matches(&format!("\"name\": \"{BLESS}\"")).count();
        // four in Ebb and Flow's branches (an ally first or herself, then the bounce) and the picture in view_buffs
        assert_eq!(marks, 5, "the main pack's blessing is added in {} places now: update this test / make_override.py", marks - 1);
        assert!(!copy.contains("\"attack_mult\": 15") && !copy.contains("\"magic_power_mult\": 15"), "the +15% is still there");
        assert_eq!(copy.matches(&format!("\"tick\": {BLESS_T}")).count(), 4, "every blessing lasts BLESS_T ticks");
        assert!(!copy.contains(&format!("\"name\": \"{SLOW_BUFF}\"")), "the stream still slows in data");
        assert!(copy.contains("description.league_nami_addon.skill"));
        assert!(copy.contains(&format!("\"name\": \"{HIT_VIEW}\"")), "the hit's picture is not in the copy's views");
    }
}
