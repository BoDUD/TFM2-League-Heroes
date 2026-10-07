//! 布兰德附加包：被动「炽热之焰」的层数记在每个敌方英雄身上（英雄联盟的做法）。
//!
//! 主包保持纯数据：数据只读得到施法者自己身上的 buff，所以主包把层数记在布兰德身上（施法者标记 b_1 -> b_2，凯南、
//! 韦鲁斯的做法）——技能连中不同的英雄也会叠到第 3 层，第 3 下打中的那个英雄爆炸。`mod.override_info` 把主包的布兰德
//! 换成 `override/` 里的副本，只有一处不同：技能打中敌方英雄时的那段叠层换成原生效果 `league_brand:blaze`——
//!
//! * 层数是那个英雄身上的 buff `league_brand_bz_<布兰德的 id>`（每层 `B_KEEP` tick，再中一下全部刷新），每个敌人分开计；
//!   头上照旧亮 1、2、3 层的标记；
//! * 第 3 层：层数清掉，他变得不稳定 `P_WAIT` tick（`league_brand_p_unstable` 的画面；这期间不再叠层），之后在他所在的
//!   位置爆炸：半径 `P_DET_R` 内的敌人（不含防御塔）受到 `P_DET` + `P_DET_AP`% 法强 + `P_DET_HP`% 最大生命值的**魔法伤害**
//!   （主包的最大生命值部分只能是真实伤害），并被点燃（`P_T` tick 里每 `P_PERIOD` tick 受到 `P_BURN` + `P_BURN_AP`% 法强的
//!   魔法伤害）；他在爆炸前死了就不炸；
//! * 每叠一层都刷新布兰德身上的 `league_brand_b_1`（`B_KEEP` tick）：W 的加成伤害和 E 的大范围蔓延照旧读它。
//!
//! 诊断（v0.1.1，游戏里看不到被动说明）：副本的被动是原生被动 `league_brand:watch`，布兰德每次出生写一行 `SPAWN`，
//! 之后每 `WATCH_EVERY` tick 写一行他的状态和 `league_brand:blaze` 被调用过几次——有 SPAWN 就说明这局用的是附加包的布兰德。
//!
//! 数字是主包 tools/kit/build_brand.py 参数表 P 的同名项（小写）；`make_override.py` 生成副本时核对，不一致就停。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_brand.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_brand";

/// 层数和刷新时间（主包 P 的 b_keep）。
pub const B_KEEP: usize = 240;
/// 第 3 层到爆炸（p_wait）。
pub const P_WAIT: usize = 120;
/// 爆炸半径（p_det_r）。
pub const P_DET_R: u64 = 26_000;
/// 爆炸的固定伤害、法强加成 %（p_det、p_det_ap）。
pub const P_DET: usize = 50;
pub const P_DET_AP: usize = 30;
/// 爆炸附加的最大生命值 %（p_det_hp），这里是魔法伤害。
pub const P_DET_HP: usize = 4;
/// 点燃：持续、间隔、每次的固定伤害和法强加成 %（p_t、p_period、p_burn、p_burn_ap）。
pub const P_T: usize = 240;
pub const P_PERIOD: usize = 60;
pub const P_BURN: usize = 6;
pub const P_BURN_AP: usize = 4;
/// 诊断：每这么多 tick 报一次布兰德的状态（30 秒）。
const WATCH_EVERY: usize = 1800;

/// `league_brand:blaze` 被调用的次数（所有对局合计，诊断用）。
static BLAZE_CALLS: AtomicUsize = AtomicUsize::new(0);

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_BRAND_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_brand.log");
        }
    }
    PathBuf::from("league_brand.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
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

// ===================== 规则 =====================

fn n(name: &str) -> String {
    format!("{ID}_{name}")
}

/// 这个布兰德在敌人身上的层数 buff。
fn stacks_name(brand: usize) -> String {
    n(&format!("bz_{brand}"))
}

/// 这个布兰德的爆炸在等的时候挂在敌人身上（不再叠层）。
fn lock_name(brand: usize) -> String {
    n(&format!("bl_{brand}"))
}

/// 一次叠层的结果。
#[derive(Debug, PartialEq, Eq)]
pub enum Blaze {
    /// 他在等爆炸，不叠。
    Locked,
    /// 现在 1 或 2 层。
    Stack(usize),
    /// 第 3 层：变得不稳定，`P_WAIT` tick 后爆炸。
    Detonate,
}

/// 叠完以后的层数 `count`（`locked`：他已经在等爆炸）。
pub fn outcome(count: usize, locked: bool) -> Blaze {
    match (locked, count) {
        (true, _) => Blaze::Locked,
        (false, c) if c >= 3 => Blaze::Detonate,
        (false, c) => Blaze::Stack(c.max(1)),
    }
}

/// 爆炸对最大生命值 `max_hp` 的敌人造成的魔法伤害（减免前）。
pub fn detonation_damage(max_hp: usize, magic_power: usize) -> usize {
    P_DET + P_DET_AP * magic_power / 100 + P_DET_HP * max_hp / 100
}

/// 点燃每次的魔法伤害（减免前），至少 1。
pub fn burn_damage(magic_power: usize) -> usize {
    (P_BURN + P_BURN_AP * magic_power / 100).max(1)
}

/// 点燃的每一下在第几 tick（从点燃算起）。
pub fn burn_ticks() -> Vec<usize> {
    (1..=P_T / P_PERIOD).map(|k| k * P_PERIOD).collect()
}

/// 两点距离在半径以内。
pub fn within(a: (u64, u64), b: (u64, u64), r: u64) -> bool {
    let dx = a.0.abs_diff(b.0) as u128;
    let dy = a.1.abs_diff(b.1) as u128;
    dx * dx + dy * dy <= (r as u128) * (r as u128)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn flag(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

fn queue(sim: &mut StableSim<'_>, step: &str, caster: usize, input: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{step}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
}

fn magic_power(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| e.stat().magic_power)
}

/// 技能打中一个敌方英雄：在他身上叠一层。
fn blaze(sim: &mut StableSim<'_>, brand: usize, input: InputTargetV1) {
    BLAZE_CALLS.fetch_add(1, Ordering::Relaxed);
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        wlog(format!("{} BLAZE skipped: input kind {} is not a unit", head(sim, brand), input.kind));
        return;
    }
    let target = input.target_id;
    if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
        wlog(format!("{} BLAZE #{target}: not alive, skipped", head(sim, brand)));
        return;
    }
    let locked = has_buff(sim, target, &lock_name(brand));
    let count = if locked {
        0
    } else {
        let c = sim.entity_stack_buff(target, &BuffV1::timed(&stacks_name(brand), B_KEEP), 3, true);
        if c == 0 {
            wlog(format!("{} BLAZE: entity_stack_buff refused on #{target}", head(sim, brand)));
            return;
        }
        c
    };
    let on_target = InputTargetV1::target(target);
    match outcome(count, locked) {
        Blaze::Locked => {}
        Blaze::Stack(k) => {
            sim.play_view_effect(&n(&format!("p_s{k}")), brand, &on_target, 0, 0, 0);
            flag(sim, brand, &n("b_1"), B_KEEP);
            wlog(format!("{} BLAZE #{target}: {k} stack(s)", head(sim, brand)));
        }
        Blaze::Detonate => {
            sim.entity_remove_buff(target, &stacks_name(brand));
            sim.add_buff(target, &BuffV1::timed(&lock_name(brand), P_WAIT));
            sim.add_buff(target, &BuffV1::timed(&n("p_unstable"), P_WAIT));
            sim.play_view_effect(&n("p_s3"), brand, &on_target, 0, 0, 0);
            flag(sim, brand, &n("b_1"), B_KEEP);
            queue(sim, "boom", brand, on_target, P_WAIT);
            wlog(format!("{} BLAZE #{target}: 3 stacks, detonates in {P_WAIT} ticks", head(sim, brand)));
        }
    }
}

/// 不稳定的英雄爆炸：周围的敌人受到伤害并被点燃。
fn boom(sim: &mut StableSim<'_>, brand: usize, input: InputTargetV1) {
    let target = input.target_id;
    let Some(at) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.pos()) else {
        wlog(format!("{} BOOM #{target}: died before the detonation", head(sim, brand)));
        return;
    };
    let Some(team) = sim.get_entity(brand).map(|e| e.team()) else { return };
    let ap = magic_power(sim, brand);
    let spot = InputTargetV1::pos(at.0, at.1);
    sim.play_view_effect(&n("p_boom"), brand, &spot, 0, 0, 0);
    sim.play_sfx(&n("p_boom"), brand, &spot);
    let hit: Vec<(usize, usize)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.is_alive() && e.team() != team && !e.is_tower() && within(e.pos(), at, P_DET_R))
        .map(|e| (e.id(), e.hp().1))
        .collect();
    for &(id, max_hp) in &hit {
        let on = InputTargetV1::target(id);
        sim.deal_damage_typed(brand, id, detonation_damage(max_hp, ap), DamageTypeV1::Ap, AttackTypeV1::Skill);
        sim.play_view_effect(&n("p_hit"), brand, &on, 0, 0, 0);
        flag(sim, id, &n("p_burn"), P_T);
        for t in burn_ticks() {
            queue(sim, "burn", brand, on, t);
        }
    }
    wlog(format!(
        "{} BOOM #{target}: {} enemies within {P_DET_R}, ap {ap} -> {} + {P_DET_HP}% max health magic each",
        head(sim, brand),
        hit.len(),
        P_DET + P_DET_AP * ap / 100
    ));
}

/// 点燃的一下。
fn burn(sim: &mut StableSim<'_>, brand: usize, input: InputTargetV1) {
    let target = input.target_id;
    if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
        return;
    }
    let d = burn_damage(magic_power(sim, brand));
    sim.deal_damage_typed(brand, target, d, DamageTypeV1::Ap, AttackTypeV1::Skill);
}

/// 诊断用的被动：证明这局的布兰德是附加包的副本，并定时报告。
#[derive(Clone, Default)]
struct Watch;

impl StablePassive for Watch {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, entity: usize) {
        let team = sim.get_entity(entity).map_or(usize::MAX, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Brand (player {player}, team {team})", head(sim, entity)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let t = sim.tick();
        if t == 0 || t % WATCH_EVERY != 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, level, ap) = (e.is_alive(), e.level(), e.stat().magic_power);
        wlog(format!(
            "{} WATCH: alive {alive}, level {level}, ap {ap}; blaze calls so far {}",
            head(sim, me),
            BLAZE_CALLS.load(Ordering::Relaxed)
        ));
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Brand's Blaze: stacks on each enemy) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:blaze"), Step(blaze));
    module.add_native_effect(format!("{ID}:boom"), Step(boom));
    module.add_native_effect(format!("{ID}:burn"), Step(burn));
    module.add_native_passive(format!("{ID}:watch"), Watch);
    host.log(LogLevel::Info, "league_brand v1 loaded (Brand's passive: Blaze stacks on each enemy).");
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
    fn three_stacks_detonate() {
        assert_eq!(outcome(1, false), Blaze::Stack(1));
        assert_eq!(outcome(2, false), Blaze::Stack(2));
        assert_eq!(outcome(3, false), Blaze::Detonate);
        // 等爆炸的时候不叠
        assert_eq!(outcome(0, true), Blaze::Locked);
    }

    #[test]
    fn detonation_and_burn() {
        // 2000 生命、0 法强：50 + 80；230 法强：50 + 69 + 80
        assert_eq!(detonation_damage(2000, 0), 130);
        assert_eq!(detonation_damage(2000, 230), 199);
        assert_eq!(burn_damage(0), 6);
        assert_eq!(burn_damage(250), 16);
        assert_eq!(burn_ticks(), vec![60, 120, 180, 240]);
    }

    #[test]
    fn the_blast_radius() {
        assert!(within((100_000, 50_000), (126_000, 50_000), P_DET_R));
        assert!(!within((100_000, 50_000), (120_000, 70_000), P_DET_R));
        assert!(within((0, 0), (0, 0), P_DET_R));
    }

    #[test]
    fn names_fit_a_buff() {
        assert!(stacks_name(usize::MAX).len() <= BUFF_NAME_CAP);
        assert_eq!(stacks_name(7), "league_brand_bz_7");
        assert_eq!(lock_name(7), "league_brand_bl_7");
    }
}
