//! 基兰复活附加包 v2：R「时光倒流」——给快死的队友挂符文，符文期间受到致命伤害时倒流、复活。
//!
//! 主包里基兰的 R 由 AI 在敌方英雄 60000 内时放出、待命 900 tick（`league_zilean_r_armed`，到时没用上就
//! 退还冷却）；待命期间他每次出手查一次：附近有被控制的队友、或自己被两名以上敌方英雄贴身，才给那个人挂
//! 5 秒的时光符文 `league_zilean_r_rune`（带「不死」，生命最低停在 1），到第 299 tick 不管有没有危险都回血。
//! 基本不出（主包测过平均一局 0.8 次），挂上的也多半用不上。`mod.override_info` 把主包的基兰换成
//! `override/` 里的副本：四个动作里的那段检查去掉，改由本包的被动 `guard`（挂在 `passive_ult` 上）决定给谁挂：
//!
//! - `guard`：R 待命时每 `GUARD_EVERY` tick 看一次基兰 `R_RANGE` 内的己方英雄（含他自己）：身边
//!   `DANGER_NEAR` 内有敌方英雄，而且生命不到 `DANGER_HP`，或 `BURST_T` tick 内掉了 `BURST` 以上、只剩
//!   `BURST_LEFT` 以下——给最危险（生命比例最低）的那个挂符文，播主包 R 的施法动作、画面和声音，去掉待命
//!   （冷却照常走完，不退还）。基兰被控住时不放。
//! - `rune`：记下回血量（400 + 150% 基兰法强，挂符文那一刻算）和基兰是谁，写在被保护者身上的
//!   标记 `league_zilean_rw_watch:<回血>:<基兰>` 里，然后每 tick 看一次（`watch`，以被保护者
//!   为施法者排队，基兰死了也照样跑）。
//! - `watch`：符文没了（到期没用上）就结束，不回血——同 League；被保护者生命掉到 1（符文的「不死」
//!   接住了本该致命的伤害）、而且身上没有别人给的「不死」（索拉卡 W 的 `league_soraka_w_guard`、
//!   凯尔的 `league_kayle_probe_undying` 之类）时倒流：去掉符文，`REWIND_T` tick 内不死且不受伤，
//!   清掉控制，放逐（不可选中、隐身、不能行动，播倒流的画面），符文的画面留到倒流结束。
//!   别人的「不死」还在时就等它结束，那段时间他本来就死不了。
//! - `revive`：倒流结束，回血（基兰还活着就算基兰的治疗），播画面和声音。
//!
//! 只碰身上有基兰符文的人；索拉卡、凯尔等别的英雄的数据都不在本包里，原样不动。
//! 符文的状态都在单位身上的 buff 和排队的效果里；`guard` 记的生命历史在每个基兰自己的被动里。
//! 不用全局变量，服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zilean_rewind.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_zilean_rewind";

/// 主包的时光符文（带「不死」，300 tick）。
pub const RUNE: &str = "league_zilean_r_rune";
/// 本包：正在看着这个人；名字后面带 `:<回血>:<基兰>`。
pub const WATCH: &str = "league_zilean_rw_watch";
/// 本包：倒流中（不死 + 不受伤害）。
pub const HOLD: &str = "league_zilean_rw_hold";
/// 符文时长（同主包）。
pub const RUNE_T: usize = 300;
/// 倒流时长：League 的时光倒流约 2.5 秒。
pub const REWIND_T: usize = 150;
/// 回血：400 + 150% 法强（同主包）。
pub const HEAL: usize = 400;
pub const HEAL_AP: usize = 150;
/// 主包：AI 放 R 后的待命（900 tick，到时没用上退还冷却）。
pub const ARMED: &str = "league_zilean_r_armed";
/// 符文的射程（同主包 r_save_r）：基兰这么近的己方英雄（含他自己）能挂。
pub const R_RANGE: f64 = 90_000.0;
/// 危险：这么近有敌方英雄，而且生命比例不到 `DANGER_HP`，或 `BURST_T` tick 内掉了 `BURST` 以上、只剩 `BURST_LEFT` 以下。
pub const DANGER_NEAR: f64 = 45_000.0;
pub const DANGER_HP: f64 = 0.30;
pub const BURST: f64 = 0.30;
pub const BURST_LEFT: f64 = 0.60;
pub const BURST_T: usize = 60;
/// 被动每隔几 tick 看一次。
pub const GUARD_EVERY: usize = 3;
/// 主包 R 的施法动作时长。
const CAST_ANIM: u64 = 30;

/// 主包基兰的名字（特效、音效都以它开头）。
fn zilean(x: &str) -> String {
    format!("league_zilean_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ZILEAN_REWIND_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_zilean_rewind.log");
        }
    }
    PathBuf::from("league_zilean_rewind.log")
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
    format!("[{kind} m={} s={}] t={} {}", m(o.match_id), m(o.set_index), sim.tick(), who(sim, id))
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    let name = sim.get_entity(id).and_then(|e| e.name()).unwrap_or_default();
    format!("#{id} {name}")
}

// ===================== 小工具 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    buffs(sim, id).iter().any(|b| b.name() == name)
}

/// 身上有不是基兰给的「不死」吗（索拉卡 W、凯尔等）。
pub fn other_undying(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(name, undying)| *undying && !ours(name))
}

/// 基兰的符文和本包的标记。
fn ours(name: &str) -> bool {
    name == RUNE || name.starts_with(HOLD) || name.starts_with(WATCH)
}

fn holding(sim: &StableSim<'_>, id: usize) -> bool {
    buffs(sim, id).iter().any(|b| b.name().starts_with(HOLD))
}

/// 看守标记：`league_zilean_rw_watch:<回血>:<基兰>`。
pub fn watch_name(heal: usize, zilean: usize) -> String {
    format!("{WATCH}:{heal}:{zilean}")
}

/// 从看守标记读回 (回血, 基兰)。
pub fn parse_watch(name: &str) -> Option<(usize, usize)> {
    let rest = name.strip_prefix(WATCH)?.strip_prefix(':')?;
    let (heal, zilean) = rest.split_once(':')?;
    Some((heal.parse().ok()?, zilean.parse().ok()?))
}

fn watch_of(sim: &StableSim<'_>, id: usize) -> Option<(usize, usize)> {
    buffs(sim, id).iter().find_map(|b| parse_watch(b.name()))
}

fn alive(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive())
}

fn queue(sim: &mut StableSim<'_>, step: &str, caster: usize, input: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{step}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
}

// ===================== 给谁挂符文 =====================

/// 一个己方英雄：id、位置、生命比例、`BURST_T` tick 内最多掉了多少（比例）。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Ally {
    pub id: usize,
    pub at: (f64, f64),
    pub hp: f64,
    pub drop: f64,
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 有危险吗：身边 `DANGER_NEAR` 内有敌方英雄，生命不到 `DANGER_HP`，或刚被打掉一大截。
pub fn in_danger(a: &Ally, enemies: &[(f64, f64)]) -> bool {
    enemies.iter().any(|e| dist(a.at, *e) <= DANGER_NEAR) && (a.hp <= DANGER_HP || (a.drop >= BURST && a.hp <= BURST_LEFT))
}

/// 基兰在 `zilean`：`R_RANGE` 内有危险的己方英雄里生命比例最低的那个。
pub fn pick_guard(zilean: (f64, f64), allies: &[Ally], enemies: &[(f64, f64)]) -> Option<usize> {
    allies
        .iter()
        .filter(|a| dist(zilean, a.at) <= R_RANGE && in_danger(a, enemies))
        .min_by(|a, b| a.hp.total_cmp(&b.hp))
        .map(|a| a.id)
}

fn hp_share((now, max): (usize, usize)) -> f64 {
    if max > 0 {
        now as f64 / max as f64
    } else {
        1.0
    }
}

/// 打断施法的控制。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];

fn controlled(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id)
        .is_some_and(|e| (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| NO_CAST.iter().any(|k| k.code() == c.kind))))
}

/// 每个基兰一份：己方英雄最近 `BURST_T` tick 的生命比例（每 `GUARD_EVERY` tick 记一笔）。
#[derive(Clone, Default)]
struct Guard {
    seen: HashMap<usize, Vec<(usize, f64)>>,
}

impl StablePassive for Guard {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        if tick % GUARD_EVERY != 0 {
            return;
        }
        let Some(z) = sim.get_entity(me) else { return };
        if !z.is_alive() {
            return;
        }
        let team = z.team();
        let (zx, zy) = z.pos();
        let mut allies = Vec::new();
        let mut enemies = Vec::new();
        let mut seen = HashMap::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || !e.is_alive() {
                continue;
            }
            let (x, y) = e.pos();
            let at = (x as f64, y as f64);
            if e.team() != team {
                enemies.push(at);
                continue;
            }
            let hp = hp_share(e.hp());
            let mut past: Vec<(usize, f64)> = self.seen.remove(&e.id()).unwrap_or_default();
            past.retain(|(t, _)| t + BURST_T >= tick);
            let top = past.iter().map(|p| p.1).fold(hp, f64::max);
            past.push((tick, hp));
            seen.insert(e.id(), past);
            if e.is_targetable() && !buffs(sim, e.id()).iter().any(|b| ours(b.name())) {
                allies.push(Ally { id: e.id(), at, hp, drop: top - hp });
            }
        }
        self.seen = seen;
        if !has_buff(sim, me, ARMED) || controlled(sim, me) {
            return;
        }
        if let Some(t) = pick_guard((zx as f64, zy as f64), &allies, &enemies) {
            let a = allies.iter().find(|a| a.id == t).copied().unwrap_or_default();
            cast_rune(sim, me, t, &a, &enemies);
        }
    }
}

/// 放 R：给 `target` 挂符文（同主包：带「不死」300 tick，符文的声音），基兰播施法动作、画面和声音，
/// 去掉待命（冷却照常走完），开始看着他。
fn cast_rune(sim: &mut StableSim<'_>, me: usize, target: usize, a: &Ally, enemies: &[(f64, f64)]) {
    let mut rune_buff = BuffV1::timed(RUNE, RUNE_T);
    rune_buff.undying = true;
    sim.add_buff(target, &rune_buff);
    sim.entity_remove_buff(me, ARMED);
    let at_me = InputTargetV1::target(me);
    sim.play_sfx(&zilean("r_rune"), me, &InputTargetV1::target(target));
    sim.play_sfx(&zilean("r_cast"), me, &at_me);
    let mut anim = CcV1::of_kind(CcKindV1::Animation, CAST_ANIM);
    anim.set_name("skill");
    sim.apply_cc(me, &anim);
    sim.play_view_effect(&zilean("r_cast"), me, &at_me, 0, 0, 0);
    let near = enemies.iter().map(|e| dist(a.at, *e)).fold(f64::INFINITY, f64::min);
    wlog(format!(
        "{} GUARD: rune on {} (hp {:.0}%, lost {:.0}% in {BURST_T} ticks, enemy champion {near:.0} away)",
        head(sim, me),
        who(sim, target),
        a.hp * 100.0,
        a.drop * 100.0
    ));
    rune(sim, me, InputTargetV1::target(target));
}

// ===================== 三段 =====================

/// 主包刚给某人挂上符文：记下回血量，开始看着他。目标就是效果的输入；输入不是单位时，
/// 找基兰这边身上有符文、还没被看着的英雄。
fn rune(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let mut targets = Vec::new();
    if input.kind == InputTargetKindV1::Target.code() && has_buff(sim, input.target_id, RUNE) {
        targets.push(input.target_id);
    } else {
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_champion() && e.is_alive() && e.team() == team {
                targets.push(e.id());
            }
        }
        targets.retain(|t| has_buff(sim, *t, RUNE));
    }
    let ap = sim.get_entity(caster).map_or(0, |e| e.stat().magic_power);
    let heal = HEAL + ap * HEAL_AP / 100;
    for t in targets {
        if watch_of(sim, t).is_some() || holding(sim, t) {
            continue;
        }
        sim.add_buff(t, &BuffV1::timed(&watch_name(heal, caster), RUNE_T + 2));
        queue(sim, "watch", t, InputTargetV1::target(t), 1);
        wlog(format!("{} RUNE from {} (rewind heal {heal})", head(sim, t), who(sim, caster)));
    }
}

/// 每 tick：符文到期就结束；生命掉到 1、又没有别人的「不死」时倒流。
fn watch(sim: &mut StableSim<'_>, me: usize) {
    let Some((heal, zilean_id)) = watch_of(sim, me) else { return };
    let Some(e) = sim.get_entity(me) else { return };
    if !e.is_alive() {
        wlog(format!("{} died with the rune on", head(sim, me)));
        return;
    }
    let (hp, _) = e.hp();
    let list: Vec<(String, bool)> = buffs(sim, me).iter().map(|b| (b.name().to_string(), b.undying)).collect();
    let rune_on = list.iter().any(|(n, _)| n == RUNE);
    if !rune_on {
        sim.entity_remove_buff(me, &watch_name(heal, zilean_id));
        wlog(format!("{} rune ended unused: no heal", head(sim, me)));
        return;
    }
    if hp <= 1 && !other_undying(&list) {
        rewind(sim, me, heal, zilean_id);
        return;
    }
    queue(sim, "watch", me, InputTargetV1::target(me), 1);
}

/// 倒流：去掉符文，不死且不受伤 `REWIND_T` tick，清控制，放逐（不可选中），到时复活。
fn rewind(sim: &mut StableSim<'_>, me: usize, heal: usize, zilean_id: usize) {
    sim.entity_remove_buff(me, &watch_name(heal, zilean_id));
    sim.entity_remove_buff(me, RUNE);
    let mut hold = BuffV1::timed(&format!("{HOLD}:{heal}:{zilean_id}"), REWIND_T + 2);
    hold.undying = true;
    hold.damaged_reduce = 100;
    sim.add_buff(me, &hold);
    // 符文的画面留到倒流结束（不带「不死」，只是画面）
    sim.add_buff(me, &BuffV1::timed(RUNE, REWIND_T));
    sim.entity_clear_cc(me);
    let by = if alive(sim, zilean_id) { zilean_id } else { me };
    let banished = sim.entity_banish(by, me, REWIND_T, &zilean("r_rewind"), &zilean("r_cast"));
    sim.play_sfx(&zilean("r_rewind"), by, &InputTargetV1::target(me));
    queue(sim, "revive", me, InputTargetV1::target(me), REWIND_T);
    wlog(format!(
        "{} REWIND: lethal damage caught at 1 hp, {} for {REWIND_T} ticks",
        head(sim, me),
        if banished { "banished" } else { "not banished (cc immune?), immune only" }
    ));
}

/// 倒流结束：回血（基兰活着就算他的治疗），播画面和声音。
fn revive(sim: &mut StableSim<'_>, me: usize) {
    let hold = buffs(sim, me).iter().find_map(|b| b.name().strip_prefix(HOLD).map(|r| format!("{WATCH}{r}")));
    let Some((heal, zilean_id)) = hold.as_deref().and_then(parse_watch) else { return };
    if !alive(sim, me) {
        return;
    }
    let by = if alive(sim, zilean_id) { zilean_id } else { me };
    sim.heal(by, me, heal);
    sim.play_view_effect(&zilean("r_rewind"), by, &InputTargetV1::target(me), 0, 0, 0);
    sim.play_sfx(&zilean("r_rewind"), by, &InputTargetV1::target(me));
    sim.entity_remove_buff(me, &format!("{HOLD}:{heal}:{zilean_id}"));
    sim.entity_remove_buff(me, RUNE);
    let hp = sim.get_entity(me).map_or((0, 0), |e| e.hp());
    wlog(format!("{} REVIVE: healed {heal} by {} -> {}/{}", head(sim, me), who(sim, by), hp.0, hp.1));
}

// ===================== 注册 =====================

#[derive(Clone, Copy)]
enum Step {
    Rune,
    Watch,
    Revive,
}

struct Stage(Step);

impl StableEffectType for Stage {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        match self.0 {
            Step::Rune => rune(sim, caster, input),
            Step::Watch => watch(sim, caster),
            Step::Revive => revive(sim, caster),
        }
    }
}

/// 本包的原生效果：`league_zilean_rewind:<名字>`。数据层只调 `rune`。
pub const STAGES: [&str; 3] = ["rune", "watch", "revive"];

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    // 上一次启动的日志留一份（.prev.log），重启游戏不丢
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v2 (Chronoshift guard + rewind) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:rune"), Stage(Step::Rune));
    module.add_native_effect(format!("{ID}:watch"), Stage(Step::Watch));
    module.add_native_effect(format!("{ID}:revive"), Stage(Step::Revive));
    module.add_native_passive(format!("{ID}:guard"), Guard::default());
    host.log(LogLevel::Info, "league_zilean_rewind v2 loaded (Zilean's R guards allies in danger and rewinds lethal damage).");
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
    fn the_watch_mark_carries_heal_and_zilean() {
        assert_eq!(watch_name(625, 41), "league_zilean_rw_watch:625:41");
        assert_eq!(parse_watch("league_zilean_rw_watch:625:41"), Some((625, 41)));
        assert_eq!(parse_watch("league_zilean_rw_watch"), None);
        assert_eq!(parse_watch("league_zilean_r_rune"), None);
        // 名字放得下（buff 名最多 64 字节）：回血、实体 id 都远小于 u32::MAX
        assert!(format!("{HOLD}:{}:{}", u32::MAX, u32::MAX).len() <= BUFF_NAME_CAP);
        assert!(watch_name(u32::MAX as usize, u32::MAX as usize).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn the_rune_goes_to_whoever_is_about_to_die() {
        let ally = |id: usize, x: f64, hp: f64, drop: f64| Ally { id, at: (x, 0.0), hp, drop };
        let foe = [(40_000.0, 0.0)];
        // 生命 25%、敌人 30000：有危险；生命 60% 没被打：没事；离基兰 100000：够不着
        assert_eq!(pick_guard((0.0, 0.0), &[ally(1, 70_000.0, 0.25, 0.0)], &foe), Some(1));
        assert_eq!(pick_guard((0.0, 0.0), &[ally(1, 70_000.0, 0.60, 0.0)], &foe), None);
        assert_eq!(pick_guard((0.0, 0.0), &[ally(1, 100_000.0, 0.10, 0.0)], &[(100_000.0, 0.0)]), None);
        // 残血但身边 45000 内没有敌方英雄：不挂
        assert_eq!(pick_guard((0.0, 0.0), &[ally(1, 70_000.0, 0.20, 0.0)], &[(-60_000.0, 0.0)]), None);
        // 一秒内被打掉 35%、还剩 55%：挂；掉了 35% 还剩 65%：不挂
        assert_eq!(pick_guard((0.0, 0.0), &[ally(1, 20_000.0, 0.55, 0.35)], &foe), Some(1));
        assert_eq!(pick_guard((0.0, 0.0), &[ally(1, 20_000.0, 0.65, 0.35)], &foe), None);
        // 几个人都危险：给生命比例最低的（可以是基兰自己）
        let two = [ally(0, 0.0, 0.28, 0.0), ally(2, 30_000.0, 0.15, 0.0)];
        assert_eq!(pick_guard((0.0, 0.0), &two, &foe), Some(2));
    }

    #[test]
    fn only_someone_elses_undying_holds_the_rewind_back() {
        let l = |v: &[(&str, bool)]| v.iter().map(|(n, u)| (n.to_string(), *u)).collect::<Vec<_>>();
        assert!(!other_undying(&l(&[(RUNE, true)])));
        assert!(!other_undying(&l(&[(RUNE, true), ("league_zilean_rw_hold:625:41", true), ("league_zilean_rw_watch:625:41", false)])));
        assert!(other_undying(&l(&[(RUNE, true), ("league_soraka_w_guard", true)])));
        assert!(other_undying(&l(&[(RUNE, true), ("league_kayle_probe_undying", true)])));
        // 别人的普通 buff 不算
        assert!(!other_undying(&l(&[(RUNE, true), ("league_kayle_r_buff", false)])));
    }
}
