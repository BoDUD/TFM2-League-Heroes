//! 阿利斯塔附加包：凯旋怒吼按英雄联盟从身边的阵亡叠层（用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」，
//! 再说「接着做」：能做的小项都做）。
//!
//! 英雄联盟的凯旋怒吼（被动）：他的技能每眩晕 / 击飞一个敌方英雄得 1 层「凯旋」，身边每死一个敌方小兵或非史诗野怪也得 1 层，
//! 身边的敌方英雄或史诗野怪阵亡一下得 7 层；满 7 层就怒吼回血（自己和身边的友方英雄），冷却里照样叠层、冷却一过就吼，他死了
//! 层数清零；对免控的目标控制失败不算。主包是纯数据，看不到他身边谁死了，所以只数他的控制命中英雄，3 次就吼
//! （`build_alistar.py` 的 p1 → p2 阶梯）。
//!
//! `mod.override_info` 把主包的阿利斯塔换成 `override/` 里的副本（`make_override.py` 从主包生成）：技能一字不改，只是每处「控制
//! 命中一个英雄：上一级阶梯或怒吼」（Q 的砸地、W 的头槌和落地砸地、E 的眩晕拳，四处）换成本包的原生效果
//! `league_alistar:cc`；被动换成本包的 `league_alistar:roar`，普攻（写着被动）的说明换成本包的。
//!
//! - `:cc`：命中的英雄活着、身上没有免控（`cc_immune`）就给阿利斯塔挂一层 `CC_FLAG`（`CC_FLAG_T` tick），被动取走算 1 层。
//! - 被动每 `SCAN` tick 看一次他 `NEAR` 内的敌方单位（小兵、野怪、英雄、史诗野怪，不含塔、水晶、召唤物）：上次在身边、这次
//!   死了（实体没了或不活着）就算身边阵亡——小兵、野怪 1 层，英雄、史诗野怪 `BIG_STACKS` 层；走出范围的不算。层数最多
//!   `NEED`（7），冷却里照样叠。
//! - 满 `NEED` 层、怒吼冷却（`P_CD` tick）过了：清空层数，自己回复 `P_HEAL` + `P_AP`% 法强，`P_R` 内的其他友方英雄各回复
//!   `P_ALLY` + `P_ALLY_AP`% 法强（主包的数），他身上播主包的怒吼 `league_alistar_p_roar`、每个被治疗的人身上播
//!   `league_alistar_p_heal`、放主包的吼声。
//! - 他阵亡：层数清零（英雄联盟也是）；被动在玩家身上、每份模拟各一份。
//!
//! 数字是主包参数表 `build_alistar.P` 的同名项（小写），`make_override.py` 生成副本时核对，不一致就停。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_alistar.log`，每次启动游戏重写，上一次的留在 .prev.log：`SPAWN`、
//! `TRIUMPH`（从哪来、现在几层）、`ROAR`（回了谁多少），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_alistar";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_alistar") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 满多少层怒吼（英雄联盟 7）；身边的敌方英雄、史诗野怪阵亡一下给几层（英雄联盟 7）。
pub const NEED: usize = 7;
pub const BIG_STACKS: usize = 7;
/// 「身边」：英雄联盟 1000 码，按他这套技能的比例（Q 375 码 = 28000、E 350 码 = 24000，约 ×75）。
pub const NEAR: u64 = 75_000;
/// 多久看一次身边的单位。
pub const SCAN: usize = 3;
/// `:cc` 给他挂的旗子（一层 = 控制命中一个英雄）和它挂多久（被动下一次看到就取走）。
pub const CC_FLAG: &str = "league_alistar_p_cc";
pub const CC_FLAG_T: usize = 10;
/// 主包参数表的怒吼：冷却（p_cd）、治疗范围（p_r）、自己（p_heal + p_ap% 法强）、友方英雄（p_ally + p_ally_ap% 法强）。
pub const P_CD: usize = 300;
pub const P_R: u64 = 40_000;
pub const P_HEAL: usize = 40;
pub const P_AP: usize = 20;
pub const P_ALLY: usize = 50;
pub const P_ALLY_AP: usize = 30;
/// 主包的怒吼画面（他身上、被治疗的人身上）和吼声。
pub const ROAR_VIEW: &str = "league_alistar_p_roar";
pub const HEAL_VIEW: &str = "league_alistar_p_heal";
pub const ROAR_SFX: &str = "league_alistar_p_roar";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ALISTAR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_alistar.log");
        }
    }
    PathBuf::from("league_alistar.log")
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

const LOG_FIRST: usize = 80;
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

// ===================== 规则（单元测试用） =====================

/// 一个身边阵亡的单位给几层：小兵、野怪 1 层，英雄、史诗野怪（大龙、小龙、峡谷先锋这类）`BIG_STACKS` 层；别的（塔、水晶、
/// 召唤物、认不出的）不算。
pub fn stacks_for(kind: Option<EntityKindV1>) -> usize {
    match kind {
        Some(EntityKindV1::Minion) | Some(EntityKindV1::Jungle) => 1,
        Some(EntityKindV1::Champion) | Some(EntityKindV1::Epic) | Some(EntityKindV1::Serpen) => BIG_STACKS,
        _ => 0,
    }
}

/// 现有 `have` 层再得 `more` 层：最多 `NEED` 层（冷却里照样叠到满）。
pub fn add_stacks(have: usize, more: usize) -> usize {
    (have + more).min(NEED)
}

/// 满了、冷却也过了才吼。
pub fn roars(stacks: usize, now: usize, cd_until: usize) -> bool {
    stacks >= NEED && now >= cd_until
}

/// 怒吼的治疗：(他自己, 每个友方英雄)，法强 `ap`。
pub fn heals(ap: usize) -> (usize, usize) {
    (P_HEAL + P_AP * ap / 100, P_ALLY + P_ALLY_AP * ap / 100)
}

/// 上次在身边的单位里这次死了的：`was` 上次在身边的 (id, 种类)，`alive(id)` 这次还活着没有（实体没了也算死）。走出范围但还
/// 活着的不算。
pub fn died_near(was: &HashMap<usize, Option<EntityKindV1>>, alive: impl Fn(usize) -> bool) -> Vec<(usize, Option<EntityKindV1>)> {
    let mut out: Vec<_> = was.iter().filter(|(id, _)| !alive(**id)).map(|(id, k)| (*id, *k)).collect();
    out.sort_by_key(|(id, _)| *id);
    out
}

fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

// ===================== 原生效果：控制命中一个英雄 =====================

/// 副本里每处「控制命中一个英雄」：他活着、没免控就给阿利斯塔挂一层 `CC_FLAG`。
struct Cc;

impl StableEffectType for Cc {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let target = input.target_id;
        let Some(t) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_champion()) else { return };
        let immune = (0..t.buff_count()).filter_map(|i| t.buff_at(i)).any(|b| b.cc_immune);
        if immune {
            if let Some(k) = counted("immune") {
                wlog(format!("{} TRIUMPH none: #{target} was immune to the crowd control #{k}", head(sim, caster)));
            }
            return;
        }
        sim.add_buff(caster, &BuffV1::timed(CC_FLAG, CC_FLAG_T));
    }
}

// ===================== 被动：凯旋怒吼 =====================

#[derive(Clone, Default)]
struct Roar {
    stacks: usize,
    cd_until: usize,
    /// 上次看到在他身边的敌方单位：id -> 种类。
    near: HashMap<usize, Option<EntityKindV1>>,
}

impl Roar {
    fn gain(&mut self, sim: &StableSim<'_>, me: usize, more: usize, why: &str) {
        let before = self.stacks;
        self.stacks = add_stacks(self.stacks, more);
        if let Some(k) = counted("triumph") {
            wlog(format!("{} TRIUMPH +{more} ({why}): {before} -> {} #{k}", head(sim, me), self.stacks));
        }
    }

    fn scan(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, at: (u64, u64)) {
        let died = died_near(&self.near, |id| sim.get_entity(id).is_some_and(|e| e.is_alive()));
        for (id, kind) in died {
            let n = stacks_for(kind);
            if n > 0 {
                self.gain(sim, me, n, &format!("{kind:?} #{id} died near him"));
            }
        }
        self.near.clear();
        let r2 = (NEAR as u128) * (NEAR as u128);
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() || u.is_tower() {
                continue;
            }
            let kind = u.kind();
            if stacks_for(kind) == 0 || dist_sq(u.pos(), at) > r2 {
                continue;
            }
            self.near.insert(u.id(), kind);
        }
    }

    fn roar(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, at: (u64, u64), now: usize) {
        self.stacks = 0;
        self.cd_until = now + P_CD;
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let (mine, theirs) = heals(ap);
        let on_me = InputTargetV1::target(me);
        sim.play_view_effect(ROAR_VIEW, me, &on_me, 0, 0, 0);
        sim.play_sfx(ROAR_SFX, me, &on_me);
        sim.heal(me, me, mine);
        sim.play_view_effect(HEAL_VIEW, me, &on_me, 0, 0, 0);
        let r2 = (P_R as u128) * (P_R as u128);
        let allies: Vec<usize> = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter(|&id| id != me)
            .filter(|&id| sim.get_entity(id).is_some_and(|e| e.team() == team && e.is_alive() && dist_sq(e.pos(), at) <= r2))
            .collect();
        for &a in &allies {
            sim.heal(me, a, theirs);
            sim.play_view_effect(HEAL_VIEW, me, &InputTargetV1::target(a), 0, 0, 0);
        }
        if let Some(k) = counted("roar") {
            wlog(format!("{} ROAR #{k}: himself +{mine}, {} allied champions +{theirs} each {allies:?}", head(sim, me), allies.len()));
        }
    }
}

impl StablePassive for Roar {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // League: his death takes the stacks; the roar's cooldown starts over
        self.stacks = 0;
        self.near.clear();
        sim.entity_remove_buff(me, CC_FLAG);
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Alistar (player {player})", head(sim, me)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        let Some((team, at, ccs)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| {
            let ccs = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == CC_FLAG).count();
            (e.team(), e.pos(), ccs)
        }) else {
            return;
        };
        if ccs > 0 {
            sim.entity_remove_buff(me, CC_FLAG);
            self.gain(sim, me, ccs, "his crowd control on a champion");
        }
        if now % SCAN == 0 {
            self.scan(sim, me, team, at);
        }
        if roars(self.stacks, now, self.cd_until) {
            self.roar(sim, me, team, at, now);
        }
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        self.stacks = 0;
        self.near.clear();
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Alistar: Triumph from crowd control and deaths near him, roar at {NEED}) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:cc"), Cc);
    module.add_native_passive(format!("{ID}:roar"), Roar::default());
    host.log(LogLevel::Info, "league_alistar loaded (Triumphant Roar from crowd control and deaths near him).");
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
    fn deaths_near_him_give_league_s_stacks() {
        assert_eq!(stacks_for(Some(EntityKindV1::Minion)), 1);
        assert_eq!(stacks_for(Some(EntityKindV1::Jungle)), 1);
        assert_eq!(stacks_for(Some(EntityKindV1::Champion)), 7);
        assert_eq!(stacks_for(Some(EntityKindV1::Epic)), 7);
        for k in [EntityKindV1::Tower, EntityKindV1::Nexus, EntityKindV1::Summon] {
            assert_eq!(stacks_for(Some(k)), 0, "{k:?} gives nothing");
        }
        assert_eq!(stacks_for(None), 0);
    }

    #[test]
    fn stacks_cap_at_seven_and_he_roars_after_the_cooldown() {
        assert_eq!(add_stacks(5, 1), 6);
        assert_eq!(add_stacks(5, 7), 7, "a champion's death fills him");
        assert_eq!(add_stacks(7, 1), 7, "no more than seven");
        assert!(roars(7, 100, 100));
        assert!(!roars(7, 99, 100), "stacks wait for the cooldown");
        assert!(!roars(6, 1000, 0));
    }

    #[test]
    fn the_roar_heals_the_main_pack_s_numbers() {
        assert_eq!(heals(0), (40, 50));
        assert_eq!(heals(100), (60, 80));
    }

    #[test]
    fn only_those_that_died_count_not_those_that_walked_off() {
        let mut was = HashMap::new();
        was.insert(3, Some(EntityKindV1::Minion));
        was.insert(5, Some(EntityKindV1::Champion));
        was.insert(8, Some(EntityKindV1::Minion));
        // 3 died, 5 walked out of range (alive), 8's entity is gone (dead)
        let alive = |id: usize| id == 5;
        assert_eq!(died_near(&was, alive), vec![(3, Some(EntityKindV1::Minion)), (8, Some(EntityKindV1::Minion))]);
        // a lane wave: six minions die near him, one more is a roar
        let six: HashMap<usize, Option<EntityKindV1>> = (10..16).map(|i| (i, Some(EntityKindV1::Minion))).collect();
        let got = died_near(&six, |_| false).iter().map(|(_, k)| stacks_for(*k)).sum::<usize>();
        assert_eq!(add_stacks(1, got), NEED);
    }

    #[test]
    fn the_copy_counts_his_crowd_control_with_the_native_and_has_no_data_roar() {
        let copy = include_str!("../override/league_alistar.data_champion").replace("\r\n", "\n");
        assert!(copy.contains("\"passive_ref\": \"league_alistar:roar\""), "the copy has no league_alistar:roar passive");
        assert_eq!(copy.matches("\"effect_ref\": \"league_alistar:cc\"").count(), 4, "Q's slam, W's headbutt and slam, E's punch");
        for gone in ["league_alistar_p1", "league_alistar_p2", "league_alistar_p_cd"] {
            assert!(!copy.contains(gone), "{gone} is still in the copy: the data's ladder or roar is left");
        }
        for v in [ROAR_VIEW, HEAL_VIEW] {
            assert!(copy.contains(&format!("\"name\": \"{v}\"")), "the copy's views have no {v}");
        }
        assert!(copy.contains("description.league_alistar_addon.attack"));
    }
}
