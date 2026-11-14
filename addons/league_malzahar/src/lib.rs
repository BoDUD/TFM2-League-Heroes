//! 玛尔扎哈附加包（用户选「做：E 跳转 + 被动精确」）：主包数据做不准的两件事。
//!
//! `mod.override_info` 把主包的玛尔扎哈换成 `override/` 里的副本（tools/kit/build_malzahar.py 的 native=1）：数据和主包一样，
//! 只是
//! - 被动挂本包的 `league_malzahar:void`（参数在英雄数据的 `passive.params` 里），主包的护盾被动（数据）不再加；
//! - 煞星幻象打中的每个单位都调用本包的 `league_malzahar:vision`，主包数据里的「死亡检查 + 跳一次」不再加。
//!
//! - **虚空穿越**（英雄联盟原版）：准备好时身上挂 `league_malzahar_p_shift`（画面）：受到的伤害减少 `p_dr`%、**免疫控制**；
//!   第一次被**非小兵**（英雄、野怪、防御塔）打中后再持续 `p_linger` tick 就消失；之后 `p_cd` tick 内**没受到英雄伤害**才重新
//!   准备好（每受一次英雄伤害重新计时）。小兵的伤害照样减少，但不会打破它。每条命开始时是准备好的。
//! - **煞星幻象的跳转**：幻象（主包数据的持续伤害）在 `e_t` tick 内目标死了，立刻跳到目标倒下处 `e_jump` 内最近的敌人身上
//!   （先找英雄，没有再找别的敌人，不找防御塔），新目标重新受到完整的幻象：`e_t` tick 内每 `e_p` tick 一段，共
//!   `e_dmg` + `e_ap`% 法强的魔法伤害（由本包结算），头上挂 `league_malzahar_e_markb`（画面）；它死了照样再跳，没有次数限制。
//!   英雄联盟里跳转还会刷新 E 的冷却：TFM2 的冷却加速（`skill_cooldown_mult`）会把 Q 一起刷新，所以不做。
//! - **虚空蜂是真的单位（0.2.0，2026-11-14；用户：「召唤物的全做啊 剩下的一批英雄也做了啊」）**：主包里虚空虫群是跟着幻象挂在
//!   目标身上的画面和撕咬（数据里召唤物不会走）。英雄联盟里虚空蜂自己走、自己打、能被打死。稳定 mod API 的 `spawn_unit`
//!   （公用部分在萨科附加包的 `summon.rs`，这里用 `#[path]` 引进来）：副本的 E 出手时给目标挂 `V_ASK`（3 tick），去掉上一次的
//!   `V_UNIT`；被动看到就排原生效果 `:voidlings`，在目标两边各 `VOID_SPREAD` 生成 `V_N` 只 `league_malzahar_voidling`
//!   （[`voidling_spec`]），成功了给玛尔扎哈挂 `V_UNIT`——副本的数据在幻象打中目标时读它：有，就不放挂在目标身上的虫群；没有
//!   （宿主没有这个接口、生成失败、测试开关关了、读不成单位、一出来就没了），就和今天一模一样。
//! - **虚空蜂咬的是物理伤害**（0.2.1 改了说法）：英雄联盟的虚空蜂打魔法伤害，单位的普攻却只能是物理（API 的攻击没有伤害类型）。
//!   本来打算在引擎把虚空蜂的一下告诉他的被动（`on_attack`，以单位的 id）时改成魔法伤害，可游戏 0.7.2 的预模拟里 `on_attack`
//!   从来不报单位的攻击（报的都是他自己的）；别的路也看不到它咬了谁、什么时候咬：API 读不到单位的目标和出手，靠「目标这一拍
//!   掉了多少血」去猜要知道引擎的护甲算法、暴击、护盾和同一拍别的伤害，猜错了就是把别人的伤害改了。所以照物理伤害，日志
//!   照实写；那段改成魔法伤害的代码留着（以后的宿主要是报了，它照样管用）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_malzahar.log`，每次启动游戏重写；虚空蜂的行以 `VOIDLING` 开头。
//! 测试开关：日志旁边的 `league_malzahar.cfg`（`summon.rs`：`unit=off` / `still=1` / `name=`）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

use summon::{Event, Flock, Pt};

const ID: &str = "league_malzahar";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_malzahar") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 虚空穿越的 buff 挂多久（一直挂到被打破，用一个很长的时间）。
pub const SHIFT_T: usize = 1_000_000;

// ---- 虚空蜂作为单位（0.2.0）：主包的数字（make_override.py 对照参数表 P 检查，改主包就改这里）----

/// The riding swarm: w_t ticks, a bite every w_p ticks of w_dmg + w_ap % of his ability power (magic); the vision leaves
/// e_lag ticks after the cast (the data reads the flag when it lands, later still).
pub const W_T: usize = 240;
pub const W_P: usize = 30;
pub const V_HIT: usize = 14;
pub const V_HIT_AP: usize = 8;
pub const E_LAG: usize = 9;
/// The unit sheet's attack: ticks long and the tick the bite lands (tools/art/unit_malzahar_voidling.py: 400 ms, the
/// bite 180 ms in).
pub const VOID_ACT: usize = 24;
pub const VOID_LANDS: usize = 11;

// ---- 虚空蜂的其他数字（英雄联盟 wiki 现行页面的，照他的套路换算：生命按他的生命、距离按他的射程 52000 / 500）----

/// The unit name: the game draws it from asset/base/aseprite_resources/champions/<name>, which mod.override_info sends to
/// the main pack's league/champions/league_malzahar_voidling.
pub const VOIDLING: &str = "league_malzahar_voidling";
/// `V_N` voidlings an E (League: one and one more for each of up to two stacks), each `VOID_LIFE` ticks (League: 8-10 s;
/// riding, 4 s), a bite every `VOID_COOL` ticks (two of them: the riding swarm's pace; League: 0.67-0.89 a second),
/// `VOID_HP_PCT` % of his health cap (League: 65-201 against his 580-2297), `VOID_DEF_PCT` % of his armour and
/// `VOID_MR_PCT` % of his magic resistance (League: 16-50 against 18-89, 8-25 against 30-52), `VOID_SPEED_PCT` % of his
/// speed (League: 400 against 335), reach `VOID_RANGE` (League: 100 against his 500).
pub const V_N: usize = 2;
pub const VOID_LIFE: usize = 480;
pub const VOID_COOL: usize = 60;
pub const VOID_HP_PCT: usize = 10;
pub const VOID_DEF_PCT: usize = 60;
pub const VOID_MR_PCT: usize = 40;
pub const VOID_SPEED_PCT: usize = 120;
pub const VOID_RANGE: usize = 10_400;
/// They come out of the void this far on either side of the target (the riding picture's two, 14 px from it).
pub const VOID_SPREAD: f64 = 14_000.0;
/// The copy's ask (on the target, 3 ticks), the flag on him while units stand in for the riding swarm, the handoff.
pub const V_ASK: &str = "league_malzahar_v_ask";
pub const V_UNIT: &str = "league_malzahar_v_unit";
pub const V_UID: &str = "league_malzahar_v_uid";
/// The main pack's pictures and sounds the natives play: the rift they come out of.
pub const W_SPAWN_VIEW: &str = "league_malzahar_w_spawn";
/// Voidlings on the books at once (three Es).
pub const VOID_CAP: usize = 6;
/// Ticks the flag stays (the data reads it once, when the vision lands), and the handoff buffs.
const FLAG_TICKS: usize = 60;
const UID_TICKS: usize = 6;
/// A unit gone within this many ticks was never really there: the flag goes and the riding swarm plays.
pub const LOST_AGE: usize = 6;
/// Voidling bites the engine told his passive of, waiting to be dealt as magic damage next tick.
const PENDING_MAX: usize = 16;

fn sn(x: &str) -> String {
    format!("league_malzahar_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_MALZAHAR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_malzahar.log");
        }
    }
    PathBuf::from("league_malzahar.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the game, 2026-10-12)
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

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;
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

/// The test knobs (`league_malzahar.cfg` beside the log), read once.
static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

/// The units' lines (league_shaco_backstab's): the server's presims the first `LOG_FIRST`, then every `UNIT_EVERY`-th; the
/// match on screen all.
const UNIT_EVERY: usize = 200;

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let shown = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % UNIT_EVERY == 0).then_some(*n)
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub p_cd: usize,
    pub p_linger: usize,
    pub p_dr: usize,
    pub e_t: usize,
    pub e_p: usize,
    pub e_dmg: usize,
    pub e_ap: usize,
    pub e_jump: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { p_cd: 720, p_linger: 15, p_dr: 90, e_t: 240, e_p: 15, e_dmg: 170, e_ap: 80, e_jump: 40000 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "p_cd" => p.p_cd = v,
            "p_linger" => p.p_linger = v,
            "p_dr" => p.p_dr = v,
            "e_t" => p.e_t = v,
            "e_p" => p.e_p = v,
            "e_dmg" => p.e_dmg = v,
            "e_ap" => p.e_ap = v,
            "e_jump" => p.e_jump = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 幻象一段的伤害：总伤害 `e_dmg` + `e_ap`% 法强，分成 `e_t / e_p` 段（至少 1）。
pub fn part_damage(p: &Params, ap: usize) -> usize {
    let runs = (p.e_t / p.e_p.max(1)).max(1);
    ((p.e_dmg + p.e_ap * ap / 100) / runs).max(1)
}

/// 虚空穿越什么时候重新准备好：被打破的时刻和最后一次英雄伤害里晚的那个，再过 `p_cd`。
pub fn shift_back_at(broken: usize, last_champion_hit: Option<usize>, p_cd: usize) -> usize {
    broken.max(last_champion_hit.unwrap_or(0)) + p_cd
}

/// 跳转目标：`cands` 是 (id, 是英雄, 距离²)。先选范围内最近的英雄，没有再选最近的其他单位；`r` 是半径。
pub fn pick_jump(cands: &[(usize, bool, u64)], r: u64) -> Option<usize> {
    let r2 = r.saturating_mul(r);
    let near = |champ: bool| {
        cands.iter().filter(|c| c.1 == champ && c.2 <= r2).min_by_key(|c| (c.2, c.0)).map(|c| c.0)
    };
    near(true).or_else(|| near(false))
}

fn dist2(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0.abs_diff(b.0);
    let dy = a.1.abs_diff(b.1);
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

// ===================== 煞星幻象：记录和跳转 =====================

#[derive(Clone, Copy, Debug)]
struct Vision {
    target: usize,
    until: usize,
    /// 本包结算伤害（跳过来的）；主包数据打中的那个由数据结算。
    ours: bool,
    next: usize,
    last_pos: (u64, u64),
}

/// 每份模拟的编号（0.1.x，2026-11-01 复查；league_teemo_shrooms / league_galio 的做法）：被动第一次出生时抽一个，每次出生挂在
/// 他身上（buff `SIM_TAG<n>`）。以前两张表只按实体 id 记：服务器并排跑的两份预演实体 id 一样，别的比赛里同 id 的玛尔扎哈也会撞上，
/// 一份模拟的被动 `remove` 走另一份的幻象，幻象的伤害和跳转只在其中一份里发生。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
pub const SIM_TAG: &str = "league_malzahar_sim:";

/// 挂在这个单位身上的模拟编号（还没挂：0）。
fn sim_no(sim: &StableSim<'_>, id: usize) -> u64 {
    sim.get_entity(id).map_or(0, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .find_map(|b| b.name().strip_prefix(SIM_TAG).and_then(|v| v.parse().ok()))
            .unwrap_or(0)
    })
}

/// 每个玛尔扎哈（模拟编号, 实体 id）身上正在跑的幻象。效果和被动是两个对象，用这张表连起来。
static VISIONS: LazyLock<Mutex<HashMap<(u64, usize), Vec<Vision>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// 每个玛尔扎哈的参数（被动 on_spawn 时写入，效果用它算时间）。
static PARAMS: LazyLock<Mutex<HashMap<(u64, usize), Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(key: (u64, usize)) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&key).copied().unwrap_or_default()
}

/// 主包数据的幻象打中一个单位（`league_malzahar:vision`）：记下它，被动每 tick 看它死没死。
fn vision_hit(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let target = input.target_id;
    let Some(e) = sim.get_entity(target) else { return };
    let pos = e.pos();
    let key = (sim_no(sim, caster), caster);
    let p = params_of(key);
    let now = sim.tick();
    let mut map = VISIONS.lock().unwrap_or_else(|e| e.into_inner());
    let list = map.entry(key).or_default();
    list.retain(|v| v.target != target);
    list.push(Vision { target, until: now + p.e_t, ours: false, next: now + p.e_p, last_pos: pos });
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 虚空蜂作为单位 =====================

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    summon::at_of(e)
}

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// A voidling from his numbers now (`stat`, his health cap `max_hp`): its attack stat his ability power, each bite
/// `V_HIT` + `V_HIT_AP` % of it.
pub fn voidling_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    summon::Spec {
        name: VOIDLING.to_string(),
        life: VOID_LIFE,
        stat: StatV1 { attack: stat.magic_power, magic_power: stat.magic_power, hp: (max_hp * VOID_HP_PCT / 100).max(1),
                       defence: stat.defence * VOID_DEF_PCT / 100, magic_resistance: stat.magic_resistance * VOID_MR_PCT / 100,
                       move_speed: stat.move_speed * VOID_SPEED_PCT / 100, hp_regen: 0, stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: V_HIT_AP, attack: V_HIT, range: VOID_RANGE, cooltime: VOID_COOL, duration: VOID_ACT,
                               start_timing: VOID_LANDS, cancelable: false, attack_type: AttackTypeV1::BaseAttack.code() },
    }
}

/// Where the voidlings come out round the target at `at` (Malzahar at `here`): `VOID_SPREAD` on either side of it, across
/// the line between the two (the riding picture's two, one each side).
pub fn voidling_points(at: Pt, here: Pt) -> Vec<Pt> {
    let first = (here.1 - at.1).atan2(here.0 - at.0) + std::f64::consts::FRAC_PI_2;
    summon::spread(at, VOID_SPREAD, V_N, first)
}

fn at_input(at: Pt) -> InputTargetV1 {
    InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64)
}

/// The voidlings for Malzahar `me` round `at`: each handed to his passive by a `<V_UID>:<id>` buff, the flag for the data
/// on him when any came, the rift picture where each comes out. -> how many came.
fn make_voidlings(sim: &mut StableSim<'_>, me: usize, at: Pt, by: &str) -> usize {
    let Some((team, stat, max, here)) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1, pos(&e))) else { return 0 };
    let spec = voidling_spec(&stat, max).with(&KNOBS);
    let field = summon::field(sim);
    let mut ids = Vec::new();
    for p in voidling_points(at, here) {
        let p = summon::inside(field, p);
        if let Some(id) = summon::spawn(sim, me, team, p, &spec) {
            sim.add_buff(me, &BuffV1::timed(&summon::handoff(V_UID, id), UID_TICKS));
            sim.play_view_effect(W_SPAWN_VIEW, me, &at_input(p), 0, 0, 0);
            ids.push(id);
        }
    }
    if ids.is_empty() {
        if let Some(k) = tally(sim, "void fail") {
            wlog(format!("{} VOIDLINGS SPAWN FAILED #{k} ({by}): spawn_unit gave no unit for '{}' round {} - the swarm rides on \
                          the target as before", head(sim, me), spec.name, summon::pt(at)));
        }
        return 0;
    }
    sim.entity_remove_buff(me, V_UNIT);
    sim.add_buff(me, &BuffV1::timed(V_UNIT, FLAG_TICKS));
    sim.play_sfx(W_SPAWN_VIEW, me, &at_input(at));
    if let Some(k) = tally(sim, "void spawn") {
        wlog(format!("{} VOIDLINGS SPAWN #{k} ({by}): {} of {V_N} units {:?} for team {team} round {}: {}", head(sim, me), ids.len(),
                     ids, summon::pt(at), spec.shown()));
    }
    ids.len()
}

/// `:voidlings` - the passive queues it when E is cast; the input is the target's spot.
struct VoidlingsFx;

impl StableEffectType for VoidlingsFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let at = if InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Pos) {
            (input.x as f64, input.y as f64)
        } else {
            match sim.get_entity(caster) {
                Some(e) => pos(&e),
                None => return,
            }
        };
        make_voidlings(sim, caster, at, "the queued effect");
    }
}

/// A voidling as the passive keeps it: bites of it turned into magic damage.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct VoidBook {
    pub turned: usize,
}

/// The OVER line's word on a voidling's bites: physical unless the engine named it in on_attack (game 0.7.2 never does).
pub fn bites_text(turned: usize) -> String {
    if turned == 0 {
        "its bites physical (no hit of it reached his on_attack, so none was made magic)".to_string()
    } else {
        format!("{turned} of its bites dealt as magic (on_attack named it)")
    }
}

// ===================== 被动 =====================

#[derive(Clone)]
struct Void {
    p: Params,
    me: usize,
    /// 虚空穿越准备好了（buff 在身上）。
    ready: bool,
    /// 被第一次打中后，到这个 tick 消失。
    linger_until: Option<usize>,
    broken_at: usize,
    last_champion_hit: Option<usize>,
    /// 这份模拟的编号（`SIM_TAG`），他第一次出生时抽。
    sim: u64,
    /// His voidlings as units (0.2.0), and their bites waiting to be dealt as magic: (target, amount, voidling).
    voidlings: Flock<VoidBook>,
    pending: Vec<(usize, usize, usize)>,
}

impl Default for Void {
    fn default() -> Self {
        Void { p: Params::default(), me: 0, ready: false, linger_until: None, broken_at: 0, last_champion_hit: None, sim: 0,
               voidlings: Flock::new(V_UID, VOID_CAP, VOID_LIFE), pending: Vec::new() }
    }
}

impl Void {
    fn arm(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let mut b = BuffV1::timed(&sn("p_shift"), SHIFT_T);
        b.damaged_reduce = self.p.p_dr;
        b.cc_immune = true;
        sim.entity_remove_buff(me, &sn("p_shift"));
        sim.add_buff(me, &b);
        sim.play_sfx(&sn("p_shift"), me, &InputTargetV1::target(me));
        self.ready = true;
        self.linger_until = None;
    }

    fn break_shift(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        sim.entity_remove_buff(me, &sn("p_shift"));
        self.ready = false;
        self.linger_until = None;
        self.broken_at = now;
        if let Some(k) = counted("break") {
            wlog(format!("{} SHIFT #{k}: Void Shift spent, back after {} ticks without champion damage", head(sim, me),
                         self.p.p_cd));
        }
    }

    fn visions(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let mut list = {
            let mut map = VISIONS.lock().unwrap_or_else(|e| e.into_inner());
            map.remove(&(self.sim, me)).unwrap_or_default()
        };
        if list.is_empty() {
            return;
        }
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let mut keep = Vec::new();
        for mut v in list.drain(..) {
            let alive = sim.get_entity(v.target).is_some_and(|e| e.is_alive());
            if alive {
                if now >= v.until {
                    continue;
                }
                if let Some(e) = sim.get_entity(v.target) {
                    v.last_pos = e.pos();
                }
                if v.ours && now >= v.next {
                    v.next += self.p.e_p;
                    sim.deal_damage_typed(me, v.target, part_damage(&self.p, ap), DamageTypeV1::Ap, AttackTypeV1::Skill);
                }
                keep.push(v);
                continue;
            }
            if now >= v.until {
                continue;
            }
            // the target fell while the vision ran: to the nearest enemy where it fell, champions first
            let mut cands = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.team() == team || !e.is_alive() || e.is_tower() || !e.is_targetable() || e.id() == v.target {
                    continue;
                }
                cands.push((e.id(), e.is_champion(), dist2(e.pos(), v.last_pos)));
            }
            let Some(next) = pick_jump(&cands, self.p.e_jump as u64) else {
                if let Some(k) = counted("lost") {
                    wlog(format!("{} JUMP #{k}: {} fell under the vision, no enemy within {}", head(sim, me),
                                 who(sim, v.target), self.p.e_jump));
                }
                continue;
            };
            let mark = BuffV1::timed(&sn("e_markb"), self.p.e_t);
            sim.entity_remove_buff(next, &sn("e_markb"));
            sim.add_buff(next, &mark);
            sim.play_sfx(&sn("e_jump"), me, &InputTargetV1::target(next));
            if let Some(k) = counted("jump") {
                wlog(format!("{} JUMP #{k}: {} fell, the vision moves to {} ({} ticks, {} a part)", head(sim, me),
                             who(sim, v.target), who(sim, next), self.p.e_t, part_damage(&self.p, ap)));
            }
            let pos = sim.get_entity(next).map_or(v.last_pos, |e| e.pos());
            keep.retain(|k: &Vision| k.target != next);
            keep.push(Vision { target: next, until: now + self.p.e_t, ours: true, next: now + self.p.e_p, last_pos: pos });
        }
        let mut map = VISIONS.lock().unwrap_or_else(|e| e.into_inner());
        let slot = map.entry((self.sim, me)).or_default();
        // visions the data started during this tick are already in the table: keep both
        for v in keep {
            if !slot.iter().any(|s| s.target == v.target) {
                slot.push(v);
            }
        }
    }
}

impl Void {
    /// E's ask on an enemy: the voidlings asked for round it.
    fn asks(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let marked: Vec<(usize, Pt)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && has(u, V_ASK))
            .map(|u| (u.id(), pos(&u)))
            .collect();
        for (id, at) in marked {
            sim.entity_remove_buff(id, V_ASK);
            if KNOBS.off {
                if let Some(k) = tally(sim, "void off") {
                    wlog(format!("{} VOIDLINGS OFF #{k}: E cast on #{id}, unit=off in the test knobs - the swarm rides on the \
                                  target as before", head(sim, me)));
                }
                continue;
            }
            self.voidlings.ask(sim.tick(), VOID_LIFE, VoidBook::default());
            let queued = sim.queue_effect(&format!("{ID}:voidlings"), AttackTypeV1::Skill, me, &at_input(at), 1);
            if !queued {
                make_voidlings(sim, me, at, "queue_effect refused: spawned by the passive");
            }
            if let Some(k) = tally(sim, "void ask") {
                wlog(format!("{} VOIDLINGS ASK #{k}: E cast on {} at {}: {V_N} voidlings asked for {VOID_SPREAD:.0} on either \
                              side of it{}", head(sim, me), who(sim, id), summon::pt(at),
                             if queued { "" } else { " - queue_effect REFUSED" }));
            }
        }
    }

    /// The voidlings' part of a tick: the flock looked at, the bites the engine told of dealt as magic.
    fn units(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize, team: usize, here: Pt) {
        for (target, amount, unit) in std::mem::take(&mut self.pending) {
            if sim.get_entity(target).is_some_and(|e| e.is_alive()) {
                sim.deal_damage_typed(me, target, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                if let Some(m) = self.voidlings.get_mut(unit) {
                    m.extra.turned += 1;
                }
            }
        }
        for ev in self.voidlings.tick(sim, me, team, player, Some(here)) {
            match ev {
                Event::NoUnit { asked, .. } => {
                    if let Some(k) = tally(sim, "void none") {
                        wlog(format!("{} VOIDLINGS NONE #{k}: no voidling came within {} ticks of the ask at t={asked} - the \
                                      swarm rides on the target as before", head(sim, me), summon::FLOCK_WAIT));
                    }
                }
                Event::Look { n, line, .. } => {
                    if let Some(k) = tally(sim, "void look") {
                        wlog(format!("{} VOIDLING #{n} LOOK #{k}: {line}", head(sim, me)));
                    }
                }
                Event::Lost { id, why, .. } => {
                    let off = self.voidlings.out() == 0;
                    if off {
                        sim.entity_remove_buff(me, V_UNIT);
                    }
                    if let Some(k) = tally(sim, "void lost") {
                        wlog(format!("{} VOIDLING LOST #{k}: the unit #{id} spawn_unit named never read as one in {} ticks \
                                      ({why}){}", head(sim, me), summon::FLOCK_LOOKS,
                                     if off { " - the flag is off, the swarm rides on the target as before" } else { "" }));
                    }
                }
                Event::Line { n, line, .. } => {
                    if let Some(k) = tally(sim, "void unit") {
                        wlog(format!("{} VOIDLING #{n} #{k}: {line}", head(sim, me)));
                    }
                }
                Event::Over { member, end } => {
                    let n = member.unit.n;
                    if let Some(k) = tally(sim, "void over") {
                        wlog(format!("{} VOIDLING #{n} OVER #{k}: {}; {}", head(sim, me), end.text, bites_text(member.extra.turned)));
                    }
                    if end.age <= LOST_AGE && self.voidlings.out() == 0 {
                        // never really there: the data has not read the flag yet, so its swarm can still ride
                        sim.entity_remove_buff(me, V_UNIT);
                        wlog(format!("{} VOIDLING #{n}: gone {} ticks after it was asked for - the flag is off, the swarm rides \
                                      on the target as before", head(sim, me), end.age));
                    }
                }
                Event::LetGo { member } => {
                    if let Some(k) = tally(sim, "void let go") {
                        wlog(format!("{} VOIDLING #{} LET GO #{k}: {VOID_CAP} voidlings on the books - the unit #{} is out \
                                      there, no longer watched", head(sim, me), member.unit.n, member.unit.id));
                    }
                }
                Event::Wake { n, line } => {
                    if let Some(k) = tally(sim, "void wake") {
                        wlog(format!("{} VOIDLING #{n} WAKE #{k}: {line}", head(sim, me)));
                    }
                }
            }
        }
    }

    /// A line for a hook that fired while voidlings of his are out.
    fn hooked(&self, sim: &StableSim<'_>, hook: &str, entity: usize, other: usize, extra: String) {
        if self.voidlings.live.is_empty() {
            return;
        }
        let who_ = match self.voidlings.get(entity) {
            Some(m) => format!("the voidling #{}", m.unit.n),
            None if entity == self.me => "Malzahar".to_string(),
            None => "neither Malzahar nor a voidling of his".to_string(),
        };
        if let Some(k) = tally(sim, "void hook") {
            wlog(format!("{} VOIDLING HOOK #{k} {hook}: entity #{entity} ({who_}) -> {}{extra}", head(sim, self.me), who(sim, other)));
        }
    }

    /// Every voidling of his let go (he died or a new life began).
    fn orphans(&mut self, sim: &StableSim<'_>, why: &str) {
        self.pending.clear();
        let gone = self.voidlings.orphans();
        if gone.is_empty() {
            return;
        }
        let tick = sim.tick();
        let list: Vec<String> = gone.iter().map(|m| format!("#{} ({} ticks left)", m.unit.id, m.unit.left(tick))).collect();
        if let Some(k) = tally(sim, "void orphan") {
            wlog(format!("{} VOIDLING ORPHAN #{k}: {why} - {} voidlings fight on unwatched until their time: {}", head(sim, self.me),
                         list.len(), list.join(", ")));
        }
    }
}

impl StablePassive for Void {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.last_champion_hit = None;
        if self.sim == 0 {
            self.sim = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert((self.sim, me), self.p);
        VISIONS.lock().unwrap_or_else(|e| e.into_inner()).remove(&(self.sim, me));
        // a new life is a new entity: the voidlings of the old one are no longer his to watch
        self.orphans(sim, "Malzahar respawned (his death did not reach on_dead)");
        self.arm(sim, me);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Malzahar (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let now = sim.tick();
        if let Some(t) = self.linger_until {
            if now >= t {
                self.break_shift(sim, me, now);
            }
        } else if !self.ready && now >= shift_back_at(self.broken_at, self.last_champion_hit, self.p.p_cd) {
            self.arm(sim, me);
            if let Some(k) = counted("back") {
                wlog(format!("{} SHIFT #{k}: Void Shift ready again", head(sim, me)));
            }
        }
        self.visions(sim, me, now);
        let (team, here) = sim.get_entity(me).map_or((0, (0.0, 0.0)), |e| (e.team(), pos(&e)));
        self.asks(sim, me, team);
        self.units(sim, player, me, team, here);
    }

    // The voidlings' hits: should the engine ever tell his passive of one under the voidling's id, it is dealt as magic
    // damage next tick instead (League's voidlings deal magic damage; a unit's own attack is physical). Game 0.7.2 never
    // does (its presims, 2026-11-14: every on_attack named Malzahar himself), so the bites stay physical.
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, target: usize, damage: &mut usize) {
        let mine = self.voidlings.get(entity).is_some();
        let amount = *damage;
        let turned = mine && amount > 0 && self.pending.len() < PENDING_MAX;
        if turned {
            *damage = 0;
            self.pending.push((target, amount, entity));
        }
        self.hooked(sim, "on_attack", entity, target, if turned {
            format!(", damage {amount}: dealt as magic next tick")
        } else {
            format!(", damage {amount}")
        });
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_kill", entity, victim, String::new());
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_unit_kill", entity, victim, String::new());
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        if damage == 0 || attacker == me {
            return;
        }
        let Some(a) = sim.get_entity(attacker) else { return };
        let (champ, minion) = (a.is_champion(), a.is_minion());
        let now = sim.tick();
        if champ {
            self.last_champion_hit = Some(now);
        }
        if self.ready && !minion && self.linger_until.is_none() {
            self.linger_until = Some(now + self.p.p_linger);
            if let Some(k) = counted("hit") {
                wlog(format!("{} SHIFT #{k}: struck by {} ({damage}), Void Shift fades in {} ticks", head(sim, me),
                             who(sim, attacker), self.p.p_linger));
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.ready = false;
        self.linger_until = None;
        // a dead champion's passive does not run: his voidlings fight on by themselves until their time
        self.orphans(sim, "Malzahar died");
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Malzahar: Void Shift as in League, Malefic Visions jumping on every death, the voidlings units of \
         their own) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "VOIDLINGS: Void Swarm's voidlings are units ('{}', spawn_unit) - {}; {V_N} an E for {VOID_LIFE} ticks, {V_HIT} + {V_HIT_AP}% \
         of his ability power a bite every {VOID_COOL} ticks (physical: a unit's attack has no damage type), {VOID_HP_PCT}% of his \
         health. Test knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(VOIDLING),
        if KNOBS.off { "OFF by the test knobs: the swarm rides on the target as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(),
        KNOBS.shown()
    ));
    module.add_native_effect(format!("{ID}:vision"), Step(vision_hit));
    module.add_native_effect(format!("{ID}:voidlings"), VoidlingsFx);
    module.add_native_passive(format!("{ID}:void"), Void::default());
    host.log(LogLevel::Info, "league_malzahar loaded (Void Shift as in League, Malefic Visions jumping on every death).");
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
#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_part_of_the_vision() {
        let p = Params::default();
        assert_eq!(part_damage(&p, 0), 170 / 16);
        assert_eq!(part_damage(&p, 200), (170 + 160) / 16);
        assert_eq!(part_damage(&Params { e_dmg: 0, e_ap: 0, ..p }, 0), 1);
    }

    #[test]
    fn void_shift_waits_for_the_last_champion_hit() {
        assert_eq!(shift_back_at(100, None, 720), 820);
        assert_eq!(shift_back_at(100, Some(50), 720), 820);
        assert_eq!(shift_back_at(100, Some(400), 720), 1120);
    }

    #[test]
    fn the_jump_prefers_champions_in_reach() {
        let r = 40_000u64;
        let near_minion = (7, false, 100u64);
        let far_champ = (3, true, (r + 1) * (r + 1));
        let champ = (5, true, 30_000u64 * 30_000);
        assert_eq!(pick_jump(&[near_minion, champ], r), Some(5));
        assert_eq!(pick_jump(&[near_minion, far_champ], r), Some(7));
        assert_eq!(pick_jump(&[far_champ], r), None);
        assert_eq!(pick_jump(&[], r), None);
        let a = (9, true, 400u64);
        let b = (2, true, 400u64);
        assert_eq!(pick_jump(&[a, b], r), Some(2));
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"e_ap":80,"e_dmg":170,"e_jump":40000,"e_p":15,"e_t":240,"p_cd":720,"p_dr":90,"p_linger":15}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_malzahar.py");
        let src = std::fs::read_to_string(path).expect("build_malzahar.py");
        let d = Params::default();
        for (key, v) in [("p_cd", d.p_cd), ("p_linger", d.p_linger), ("p_dr", d.p_dr), ("e_t", d.e_t), ("e_p", d.e_p),
                         ("e_dmg", d.e_dmg), ("e_ap", d.e_ap), ("e_jump", d.e_jump)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_malzahar.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["p_shift", "e_markb", "e_jump"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }

    // ---- 0.2.0: the voidlings as units ----

    #[test]
    fn the_unit_names_fit_and_the_flag_is_up_before_the_vision_lands() {
        for name in [V_ASK, V_UNIT, &summon::handoff(V_UID, usize::MAX)] {
            assert!(name.starts_with("league_malzahar_") && name.len() <= BUFF_NAME_CAP, "{name}");
        }
        // the voidlings come at most 3 ticks after the cast; the vision lands E_LAG ticks after it at the soonest (and a
        // tick of flight): a unit gone by LOST_AGE takes the flag off before the data looks
        assert!(3 + LOST_AGE < E_LAG + 1);
        assert!(FLAG_TICKS > E_LAG + 65_000 / 5_000 + 2, "the flag outlasts the longest flight");
    }

    #[test]
    fn the_voidlings_are_built_from_his_numbers() {
        let his = StatV1 { attack: 80, magic_power: 200, hp: 900, defence: 50, magic_resistance: 40, move_speed: 910, hp_regen: 3,
                           stack: 0, crit_chance: 0 };
        let s = voidling_spec(&his, 1500);
        assert_eq!((s.name.as_str(), s.life), ("league_malzahar_voidling", 480));
        assert_eq!(s.stat, StatV1 { attack: 200, magic_power: 200, hp: 150, defence: 30, magic_resistance: 16, move_speed: 1092,
                                    hp_regen: 0, stack: 0, crit_chance: 0 });
        // a bite: 14 + 8 % of 200 = 30, every 60 ticks each (two of them: the riding swarm's bite every 30)
        let a = s.attack;
        assert_eq!(a.attack + s.stat.attack * a.attack_ratio / 100, 30);
        assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (10_400, 60, 24, 11));
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        assert_eq!(voidling_spec(&StatV1::default(), 0).stat.hp, 1);
        // either side of the target, across the line from him
        let p = voidling_points((500_000.0, 300_000.0), (450_000.0, 300_000.0));
        assert_eq!(p.len(), 2);
        assert!(p.iter().all(|q| (q.0 - 500_000.0).abs() < 1.0 && (summon::dist(*q, (500_000.0, 300_000.0)) - VOID_SPREAD).abs() < 1.0));
        assert!((p[0].1 - p[1].1).abs() > 2.0 * VOID_SPREAD - 1.0);
    }

    /// The arithmetic of the README: what the voidlings can deal against what the riding swarm dealt.
    #[test]
    fn the_voidlings_damage_is_about_the_riding_swarms() {
        let bite = |ap: usize| V_HIT + ap * V_HIT_AP / 100;
        for ap in [40, 200, 400] {
            let old = (W_T / W_P) * bite(ap);
            let max = V_N * (VOID_LANDS..VOID_LIFE).step_by(VOID_COOL).count() * bite(ap);
            assert_eq!(max, 2 * old, "ap {ap}");
            // in reach of their prey half the time: what the riding swarm dealt
            assert_eq!(max / 2, old, "ap {ap}");
        }
    }

    #[test]
    fn the_copy_asks_for_the_voidlings_and_keeps_the_riding_swarm_behind_the_flag() {
        let copy = include_str!("../override/league_malzahar.data_champion");
        assert_eq!(copy.matches(&format!("\"name\": \"{V_ASK}\"")).count(), 1);
        assert_eq!(copy.matches(&format!("\"name\": \"{V_UNIT}\"")).count(), 1);
        // the vision with and without Q's combo: the swarm behind the flag in both
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{V_UNIT}\"")).count(), 2);
    }

    // ---- the voidlings on the mock world (summon_mock.rs: our guess of the host, to check this side's logic) ----

    use super::mock::{champion, MPlayer, World};

    const GAREN: usize = 1;

    fn log_file() -> std::path::PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_malzahar_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_MALZAHAR_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// Malzahar #0 (team 0, 200 ability power, 1500 health) at (300000, 300000); Garen #1 40000 east of him, Darius #2 far
    /// south-east, an ally #3 far north-west (the field round them all); a player each for the champions.
    fn world() -> (World, Void) {
        log_file();
        let mut w = World::default();
        let mut malz = champion("league_malzahar", 0, 300_000.0, 300_000.0);
        (malz.hp, malz.max, malz.stat.magic_power, malz.stat.move_speed) = (1500, 1500, 200, 910);
        let mut garen = champion("league_garen", 1, 340_000.0, 300_000.0);
        (garen.hp, garen.max) = (5000, 5000);
        w.units = vec![malz, garen, champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() }];
        let mut me = Void::default();
        w.sim(|sim| me.on_spawn(sim, 0, 0));
        (w, me)
    }

    fn tick(w: &mut World, me: &mut Void) {
        for (name, caster, input) in w.due() {
            w.sim(|sim| match name.as_str() {
                "league_malzahar:voidlings" => VoidlingsFx.apply(sim, 0, caster, input),
                other => panic!("an effect nobody registered: {other}"),
            });
        }
        if w.units[0].hp > 0 {
            w.sim(|sim| me.on_update(sim, 0, 0, 0));
        }
        w.step();
    }

    fn run(w: &mut World, me: &mut Void, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    /// E's ask as the copy lays it on its target (3 ticks).
    fn cast_e(w: &mut World) -> usize {
        w.units[GAREN].buffs.push((BuffV1::timed(V_ASK, 3), 3));
        w.tick
    }

    fn voidlings(w: &World) -> Vec<usize> {
        w.spawns.iter().filter(|s| s.name == VOIDLING).filter_map(|s| s.gave).collect()
    }

    #[test]
    fn e_raises_two_voidlings_that_fight_and_time_out() {
        let (mut w, mut me) = world();
        let t0 = cast_e(&mut w);
        run(&mut w, &mut me, E_LAG + 1);
        let ids = voidlings(&w);
        assert_eq!(ids.len(), 2);
        for s in &w.spawns {
            assert_eq!((s.summoner, s.team, s.life as usize), (0, 0, VOID_LIFE));
            assert!(s.tick <= t0 + 3);
            assert_eq!(s.at.0, 340_000, "beside Garen, across the line from Malzahar");
            assert_eq!((s.stat.attack, s.stat.hp, s.attack.attack, s.attack.attack_ratio), (200, 150, 14, 8));
        }
        assert!(w.has(0, V_UNIT), "no flag on him when the vision lands: the riding swarm would bite too");
        assert_eq!(w.viewed(W_SPAWN_VIEW), 2);
        // they bite Garen, 30 a bite, at most 8 each in their life
        run(&mut w, &mut me, VOID_LIFE);
        for id in &ids {
            let bites = w.dealt(*id, DamageTypeV1::Ad);
            assert!(!bites.is_empty() && bites.len() <= 8 && bites.iter().all(|b| *b == (GAREN, 30)), "{bites:?}");
        }
        run(&mut w, &mut me, summon::WAKE_TICKS + 5);
        assert!(me.voidlings.is_empty() && w.queue.is_empty());
    }

    #[test]
    fn no_unit_from_the_host_leaves_the_data_its_swarm() {
        for case in 0..4 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                2 => w.spawn_never = true,
                _ => {}
            }
            let t0 = cast_e(&mut w);
            if case == 3 {
                run(&mut w, &mut me, 3);
                assert!(w.has(0, V_UNIT) && me.voidlings.live.len() == 2, "case {case}");
                for id in voidlings(&w) {
                    w.units[id].valid = false;
                }
            }
            if case == 2 {
                // an id that never reads as a unit is given up FLOCK_LOOKS ticks on: the flag goes then
                run(&mut w, &mut me, 3 + summon::FLOCK_LOOKS);
            } else {
                while w.tick < t0 + E_LAG + 1 {
                    tick(&mut w, &mut me);
                }
            }
            assert!(!w.has(0, V_UNIT), "case {case}: the flag is on him - no swarm at all");
            run(&mut w, &mut me, 200);
            assert!(me.voidlings.is_empty() && w.queue.is_empty(), "case {case}");
        }
    }

    #[test]
    fn the_over_line_says_the_bites_are_physical_unless_made_magic() {
        // game 0.7.2 never names a unit in on_attack: nothing may claim a conversion that did not run
        assert!(bites_text(0).starts_with("its bites physical") && !bites_text(0).contains("dealt as magic"));
        assert_eq!(bites_text(3), "3 of its bites dealt as magic (on_attack named it)");
    }

    #[test]
    fn a_bite_the_engine_tells_of_is_dealt_as_magic() {
        let (mut w, mut me) = world();
        cast_e(&mut w);
        run(&mut w, &mut me, 5);
        let ids = voidlings(&w);
        // the engine names the voidling: its 30 physical become his 30 magic next tick
        let mut dealt = 30;
        w.sim(|sim| me.on_attack(sim, 0, ids[0], GAREN, &mut dealt));
        assert_eq!(dealt, 0);
        run(&mut w, &mut me, 1);
        assert_eq!(w.dealt(0, DamageTypeV1::Ap), vec![(GAREN, 30)]);
        // his own hit (or one under his id) stays as it is
        let mut own = 55;
        w.sim(|sim| me.on_attack(sim, 0, 0, GAREN, &mut own));
        assert_eq!(own, 55);
        run(&mut w, &mut me, 1);
        assert_eq!(w.dealt(0, DamageTypeV1::Ap).len(), 1);
    }

    #[test]
    fn the_log_tells_the_voidlings_whole_lives() {
        let (mut w, mut me) = world();
        cast_e(&mut w);
        run(&mut w, &mut me, 100);
        let ids = voidlings(&w);
        let mut dealt = 30;
        w.sim(|sim| me.on_attack(sim, 0, ids[0], GAREN, &mut dealt));
        w.players[1].gold += 2;
        w.hurt(ids[1], 100_000);
        run(&mut w, &mut me, 500);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" VOIDLING")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "VOIDLINGS ASK #", "E cast on league_garen#1 at (340000,300000): 2 voidlings asked for 14000 on either side of it",
            "VOIDLINGS SPAWN #", "2 of 2 units [4, 5] for team 0 round (340000,300000): 'league_malzahar_voidling' for 480 ticks, \
             attack 200 ap 200 hp 150 def 12 mr 8 speed 1092; hits 14 + 8% of its attack, range 10400, every 60 ticks (24 long, lands at 11)",
            "VOIDLING #1 LOOK #", "reads back as name 'league_malzahar_voidling' kind summon team 0",
            " of 480 ticks, at (", "near it: champion #1 league_garen",
            "VOIDLING HOOK #", "on_attack: entity #4 (the voidling #1) -> league_garen#1, damage 30: dealt as magic next tick",
            "OVER #", "KILLED after ", "p1 gold +2", "TIMED OUT after ", "1 of its bites dealt as magic", "WAKE #",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
        assert!(mine.iter().map(|l| l.len()).max().unwrap() < 700);
    }
}
