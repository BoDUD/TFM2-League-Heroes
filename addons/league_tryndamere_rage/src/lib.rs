//! 蛮王附加包：R「无尽怒火」在快没血时开，Q「嗜血杀戮」在残血时喝（用户：「大招快没血的时候设置开也行」）。
//!
//! 主包保持纯数据：数据读不到当前生命，蛮王的 R 由 AI 在敌方英雄 60000 内时放出、待命 900 tick
//! （`league_tryndamere_r_armed`，没用上退还冷却），待命期间普攻检查「两名以上敌方英雄贴身或连续挨打」才爆发。
//! `mod.override_info` 把主包的蛮王换成 `override/` 里的副本：普攻里那段检查去掉，`passive` 换成本包的
//! `league_tryndamere_rage:guard`，由它读生命：
//!
//! - R 待命、没被控住、身边 `near` 内有敌方英雄时：生命不到 `r_hp`%，或 `burst_t` tick 内掉了 `burst`% 以上、
//!   只剩 `burst_left`% 以下——爆发（每 tick 看一次，挨打时 `on_damaged` 当场再看一次）。
//! - 爆发：去掉待命，`r_t` tick 的「不死」（`league_tryndamere_r_rage`，生命最低停在 1，同主包），怒气加满
//!   （`f_1`..`f_n`，同主包的叠法），播 R 的动作、画面和声音；`r_q_at` tick 后喝嗜血杀戮。
//! - R 在冷却（或 5 级以前）、不在待命，Q 不在冷却（`league_tryndamere_q_cd`）、身上有怒气、身边有敌方英雄、
//!   生命不到 `q_hp`% 时：喝嗜血杀戮，`q_cd` tick 冷却。
//! - 什么时候按 R（AI 钩子 `league_tryndamere_rage:ult`）：主包的 R 一看到敌方英雄就放出、待命 15 秒，游戏里显示为
//!   「开大」，满血时一次次放（用户：「再检查一下蛮王总是满血开大的问题」）。AI 想放 R 而没到上面的危险时改成普攻
//!   （打不到就走过去）；到了危险、R 冷却好、身边有敌方英雄时由它按下 R，下一 tick 被动就爆发——显示的「开大」就是爆发那一刻。
//! - 嗜血杀戮：按身上的怒气层数回血（`q_heal` + `q_per` x 层数，加 `q_heal_ratio` + `q_per_ratio` x 层数 % 攻击力），
//!   怒气清空，播 Q 的动作、画面和声音。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从 tools/kit/build_tryndamere.py 的参数表 P 写进去），
//! 本包不另记一份。生命历史记在每个蛮王自己的被动实例里；不用全局变量，服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_tryndamere_rage.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_tryndamere_rage";

/// 主包蛮王的名字（buff、特效、音效都以它开头）。
fn tr(x: &str) -> String {
    format!("league_tryndamere_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_TRYNDAMERE_RAGE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_tryndamere_rage.log");
        }
    }
    PathBuf::from("league_tryndamere_rage.log")
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 怒气层数、每层暴击率、最高一层的时长、往下每层多出的时长（同主包的叠法）。
    pub f_n: usize,
    pub f_crit: usize,
    pub f_top: usize,
    pub f_step: usize,
    /// R：不死时长、第几 tick 喝 Q、施法动作时长。
    pub r_t: usize,
    pub r_q_at: usize,
    pub r_anim: usize,
    /// Q：回血、每层怒气加的回血（固定值和攻击力百分比）、冷却、动作时长。
    pub q_heal: usize,
    pub q_heal_ratio: usize,
    pub q_per: usize,
    pub q_per_ratio: usize,
    pub q_cd: usize,
    pub q_anim: usize,
    /// 危险：这么近有敌方英雄；生命低于 `r_hp`% 开 R、低于 `q_hp`% 喝 Q；`burst_t` tick 内掉了 `burst`% 以上、
    /// 只剩 `burst_left`% 以下也开 R。
    pub near: usize,
    pub r_hp: usize,
    pub q_hp: usize,
    pub burst: usize,
    pub burst_left: usize,
    pub burst_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            f_n: 5,
            f_crit: 8,
            f_top: 300,
            f_step: 60,
            r_t: 300,
            r_q_at: 290,
            r_anim: 30,
            q_heal: 60,
            q_heal_ratio: 30,
            q_per: 50,
            q_per_ratio: 10,
            q_cd: 720,
            q_anim: 24,
            near: 50_000,
            r_hp: 15,
            q_hp: 30,
            burst: 35,
            burst_left: 40,
            burst_t: 60,
        }
    }
}

/// `{"f_n":5,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "f_n" => &mut p.f_n,
            "f_crit" => &mut p.f_crit,
            "f_top" => &mut p.f_top,
            "f_step" => &mut p.f_step,
            "r_t" => &mut p.r_t,
            "r_q_at" => &mut p.r_q_at,
            "r_anim" => &mut p.r_anim,
            "q_heal" => &mut p.q_heal,
            "q_heal_ratio" => &mut p.q_heal_ratio,
            "q_per" => &mut p.q_per,
            "q_per_ratio" => &mut p.q_per_ratio,
            "q_cd" => &mut p.q_cd,
            "q_anim" => &mut p.q_anim,
            "near" => &mut p.near,
            "r_hp" => &mut p.r_hp,
            "q_hp" => &mut p.q_hp,
            "burst" => &mut p.burst,
            "burst_left" => &mut p.burst_left,
            "burst_t" => &mut p.burst_t,
            _ => continue,
        };
        *slot = v;
    }
    p
}

// ===================== 判断 =====================

/// 这一刻的情况：生命比例（%）、`burst_t` 内最高的生命比例、身边有没有敌方英雄、R 待命 / 正在爆发 / Q 冷却、
/// 怒气层数、被不被控。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Now {
    pub hp: f64,
    pub top: f64,
    pub enemy_near: bool,
    pub armed: bool,
    /// R 冷却好了（5 级以后）：留给 R，不喝 Q。
    pub r_free: bool,
    pub raging: bool,
    pub q_cd: bool,
    pub fury: usize,
    pub controlled: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Move {
    Rage,
    Drink,
}

/// 快死了：生命不到 `r_hp`%，或 `burst_t` 内从 `top` 掉了 `burst`% 以上、只剩 `burst_left`% 以下。
pub fn about_to_die(p: &Params, hp: f64, top: f64) -> bool {
    hp <= p.r_hp as f64 || (top - hp >= p.burst as f64 && hp <= p.burst_left as f64)
}

/// 开 R、喝 Q，还是什么都不做。
pub fn decide(p: &Params, n: &Now) -> Option<Move> {
    if n.raging || n.controlled || !n.enemy_near {
        return None;
    }
    if n.armed && about_to_die(p, n.hp, n.top) {
        return Some(Move::Rage);
    }
    if !n.armed && !n.r_free && !n.q_cd && n.fury > 0 && n.hp <= p.q_hp as f64 {
        return Some(Move::Drink);
    }
    None
}

// ===================== 小工具 =====================

fn buff_names(sim: &StableSim<'_>, id: usize) -> Vec<String> {
    sim.get_entity(id)
        .map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect())
}

/// 身上怒气最高的那一层（`f_1`..`f_n` 全在身上，最高一层就是层数）。
pub fn fury_of(names: &[String], f_n: usize) -> usize {
    (1..=f_n).rev().find(|k| names.iter().any(|b| *b == tr(&format!("f_{k}")))).unwrap_or(0)
}

/// 打断施法的控制。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];

fn controlled(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id)
        .is_some_and(|e| (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| NO_CAST.iter().any(|k| k.code() == c.kind))))
}

/// 他的 R 冷却好了（5 级以后、冷却为 0）。
fn r_free(sim: &StableSim<'_>, me: usize) -> bool {
    (0..sim.player_count()).filter_map(|i| sim.player_at(i)).any(|pl| {
        pl.champion().is_some_and(|c| c.id() == me) && pl.level() >= 5 && pl.cooldowns().is_some_and(|c| c.3 == 0)
    })
}

fn enemy_near(sim: &StableSim<'_>, me: usize, team: usize, near: usize) -> bool {
    let r2 = (near as u64).saturating_mul(near as u64);
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).any(|e| {
        e.is_champion() && e.is_alive() && e.team() != team && sim.distance_sq(me, e.id()) <= r2
    })
}

fn pose(sim: &mut StableSim<'_>, me: usize, tag: &str, ticks: usize) {
    let mut anim = CcV1::of_kind(CcKindV1::Animation, ticks as u64);
    anim.set_name(tag);
    sim.apply_cc(me, &anim);
}

fn queue(sim: &mut StableSim<'_>, step: &str, caster: usize, delay: usize) {
    let name = format!("{ID}:{step}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &InputTargetV1::target(caster), delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
}

/// 怒气加满：同主包 `fury_to(f_n)`，最高一层 `f_top` tick，往下每层多 `f_step`。
fn fury_full(sim: &mut StableSim<'_>, me: usize, p: &Params) {
    for k in 1..=p.f_n {
        let name = tr(&format!("f_{k}"));
        sim.entity_remove_buff(me, &name);
        let mut b = BuffV1::timed(&name, p.f_top + (p.f_n - k) * p.f_step);
        b.crit_chance = p.f_crit as i32;
        sim.add_buff(me, &b);
    }
}

// ===================== 两个动作 =====================

/// R：去掉待命，不死 `r_t` tick，怒气加满，动作、画面、声音，`r_q_at` tick 后喝 Q。
fn rage(sim: &mut StableSim<'_>, me: usize, p: &Params, why: &str) {
    sim.entity_remove_buff(me, &tr("r_armed"));
    let mut undying = BuffV1::timed(&tr("r_rage"), p.r_t);
    undying.undying = true;
    sim.add_buff(me, &undying);
    fury_full(sim, me, p);
    pose(sim, me, "ult", p.r_anim);
    let at_me = InputTargetV1::target(me);
    sim.play_view_effect(&tr("r_cast"), me, &at_me, 0, 0, 0);
    sim.play_sfx(&tr("r_cast"), me, &at_me);
    queue(sim, "rage_end", me, p.r_q_at);
    wlog(format!("{} RAGE: {why}", head(sim, me)));
}

/// 嗜血杀戮：按怒气回血，怒气清空，动作、画面、声音。
fn drink(sim: &mut StableSim<'_>, me: usize, p: &Params, why: &str) {
    let Some(e) = sim.get_entity(me) else { return };
    if !e.is_alive() {
        return;
    }
    let atk = e.stat().attack.max(0) as usize;
    let k = fury_of(&buff_names(sim, me), p.f_n);
    let amount = p.q_heal + k * p.q_per + atk * (p.q_heal_ratio + k * p.q_per_ratio) / 100;
    sim.heal(me, me, amount);
    for j in 1..=p.f_n {
        sim.entity_remove_buff(me, &tr(&format!("f_{j}")));
    }
    pose(sim, me, "skill_q", p.q_anim);
    let at_me = InputTargetV1::target(me);
    sim.play_view_effect(&tr("q_heal"), me, &at_me, 0, 0, 0);
    sim.play_sfx(&tr("q_heal"), me, &at_me);
    let hp = sim.get_entity(me).map_or((0, 0), |e| e.hp());
    wlog(format!("{} DRINK ({why}): {k} fury, healed {amount} -> {}/{}", head(sim, me), hp.0, hp.1));
}

// ===================== 被动 =====================

/// 每个蛮王一份：参数，和最近 `burst_t` tick 的生命比例。
#[derive(Clone, Default)]
struct Guard {
    p: Params,
    seen: Vec<(usize, f64)>,
    /// R was armed at the last look (to log the tick it arms: the cast the game shows as an ult).
    was_armed: bool,
}

impl Guard {
    fn look(&mut self, sim: &mut StableSim<'_>, me: usize, from_hit: bool) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.seen.clear();
            return;
        }
        let (now, max) = e.hp();
        let team = e.team();
        let hp = if max > 0 { now as f64 * 100.0 / max as f64 } else { 100.0 };
        let tick = sim.tick();
        if !from_hit {
            self.seen.retain(|(t, _)| t + self.p.burst_t >= tick);
            self.seen.push((tick, hp));
        }
        let top = self.seen.iter().map(|s| s.1).fold(hp, f64::max);
        let names = buff_names(sim, me);
        let has = |x: &str| names.iter().any(|b| *b == tr(x));
        let n = Now {
            hp,
            top,
            enemy_near: enemy_near(sim, me, team, self.p.near),
            armed: has("r_armed"),
            // what the AI hook saw (a passive's sim has no players to read the cooldown from: the log of 2026-10-08 -
            // he drank Bloodlust at 5-13% in the very tick the hook pressed R, healed past the threshold, no rage)
            r_free: ready_seen(sim, me) || r_free(sim, me),
            raging: has("r_rage"),
            q_cd: has("q_cd"),
            fury: fury_of(&names, self.p.f_n),
            controlled: controlled(sim, me),
        };
        let why = format!("hp {hp:.0}% (top {top:.0}% in {} ticks){}{}", self.p.burst_t, if from_hit { " on a hit" } else { "" },
                          if n.r_free { ", R ready" } else { "" });
        if n.armed && !self.was_armed {
            wlog(format!("{} ARMED: {why}", head(sim, me)));
        }
        self.was_armed = n.armed;
        match decide(&self.p, &n) {
            Some(Move::Rage) => rage_with_mark(sim, me, &self.p, &why),
            Some(Move::Drink) => {
                let mut cd = BuffV1::timed(&tr("q_cd"), self.p.q_cd);
                cd.duration_kind = BuffDurationV1::Time.code();
                sim.add_buff(me, &cd);
                drink(sim, me, &self.p, &why);
            }
            None => {}
        }
    }
}

impl StablePassive for Guard {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.look(sim, me, false);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _: usize, _: usize) {
        self.look(sim, me, true);
    }
}

/// R 结束前喝的 Q：以蛮王为施法者排队的原生效果；参数在他的 R 结束时由被动传不过来，
/// 所以从身上的标记读回（`league_tryndamere_rg_p:<q_heal>:<q_heal_ratio>:<q_per>:<q_per_ratio>:<f_n>:<q_anim>`）。
struct RageEnd;

/// 标记名（buff 名最多 64 字节）。
pub fn mark_name(p: &Params) -> String {
    format!("{}:{}:{}:{}:{}:{}:{}", tr("rg_p"), p.q_heal, p.q_heal_ratio, p.q_per, p.q_per_ratio, p.f_n, p.q_anim)
}

pub fn parse_mark(name: &str) -> Option<Params> {
    let rest = name.strip_prefix(&tr("rg_p"))?.strip_prefix(':')?;
    let v: Vec<usize> = rest.split(':').map(|x| x.parse().ok()).collect::<Option<Vec<_>>>()?;
    let [q_heal, q_heal_ratio, q_per, q_per_ratio, f_n, q_anim] = v[..] else { return None };
    Some(Params { q_heal, q_heal_ratio, q_per, q_per_ratio, f_n, q_anim, ..Params::default() })
}

impl StableEffectType for RageEnd {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        let names = buff_names(sim, caster);
        let Some(mark) = names.iter().find(|b| b.starts_with(&tr("rg_p"))).cloned() else { return };
        let Some(p) = parse_mark(&mark) else { return };
        drink(sim, caster, &p, "R ends");
        sim.play_sfx(&tr("r_end"), caster, &InputTargetV1::target(caster));
    }
}

/// 被动在开 R 时把参数挂到身上（R 结束的 Q 读它；死了就随 buff 一起清掉）。
fn rage_with_mark(sim: &mut StableSim<'_>, me: usize, p: &Params, why: &str) {
    let mut mark = BuffV1::timed(&mark_name(p), p.r_q_at + 5);
    mark.duration_kind = BuffDurationV1::Time.code();
    sim.add_buff(me, &mark);
    rage(sim, me, p, why);
}

// ===================== AI 钩子 =====================

/// 主包蛮王的英雄名。
const HERO: &str = "league_tryndamere";
/// 主包 R 的射程（`ult.range`）：按 R 时的目标在这么近。
const R_RANGE: usize = 60_000;
/// 同一句日志隔这么多 tick 才再记。
const LOG_EVERY: usize = 120;
/// 「R 好了」的记录在这么多 tick 内算数（AI 每次思考都更新）。
const READY_T: usize = 3;

/// AI 钩子看到的「R 好了」：(这场模拟, 蛮王) -> 最近一次看到的 tick。被动在自己的模拟里读不到玩家（也就读不到 R 的冷却），
/// AI 钩子又加不上 buff（日志：could not add），所以经由这张表告诉被动。键里有模拟的来历（预模拟 / 观看 / 回放、比赛、局），
/// 几场模拟同时跑也各算各的：来历常常都是「未知、没有比赛号」、蛮王的编号也一样（第四局日志：按 R 的下一 tick
/// 照样喝 Q——别的模拟里 R 没好的蛮王把记录删了），所以键里还有模拟的随机种子。
type SimKey = (u64, u32, u64, u64, u64, usize);
static READY: LazyLock<Mutex<HashMap<SimKey, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn sim_key(sim: &StableSim<'_>, id: usize) -> SimKey {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.replay_id, o.set_index, id)
}

/// The first key each side computes goes to the log once (both must agree for the guard to see the hook's record).
static KEY_LOGGED: [AtomicBool; 2] = [AtomicBool::new(false), AtomicBool::new(false)];

fn log_key_once(sim: &StableSim<'_>, id: usize, side: usize) {
    if !KEY_LOGGED[side].swap(true, Ordering::Relaxed) {
        wlog(format!("{} KEY ({}): {:?}", head(sim, id), ["AI hook", "guard"][side], sim_key(sim, id)));
    }
}

/// AI 钩子记下这一 tick R 好没好。
fn ready_saw(sim: &StableSim<'_>, id: usize, free: bool) {
    log_key_once(sim, id, 0);
    let key = sim_key(sim, id);
    let mut map = READY.lock().unwrap_or_else(|e| e.into_inner());
    if free {
        if map.len() > 4096 {
            map.clear();
        }
        map.insert(key, sim.tick());
    } else {
        map.remove(&key);
    }
}

/// 被动：AI 钩子最近 `READY_T` tick 内看到 R 好了。
fn ready_seen(sim: &StableSim<'_>, id: usize) -> bool {
    log_key_once(sim, id, 1);
    let tick = sim.tick();
    let map = READY.lock().unwrap_or_else(|e| e.into_inner());
    map.get(&sim_key(sim, id)).is_some_and(|&t| t <= tick + READY_T && tick <= t + READY_T)
}

/// AI 的大招：`wants_ult` AI 原来的输入是 R；`danger` 快死了、身边有敌方英雄；`free` R 冷却好、不在待命和爆发里。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum UltPlan {
    /// 照 AI 原来的输入。
    Keep,
    /// 按下 R（待命，被动下一 tick 爆发）。
    Cast,
    /// AI 想放 R 但还没到危险：改成打 / 走向它的目标。
    Hold,
}

pub fn ult_plan(wants_ult: bool, danger: bool, free: bool) -> UltPlan {
    match (wants_ult, danger && free) {
        (_, true) => UltPlan::Cast,
        (true, false) => UltPlan::Hold,
        (false, false) => UltPlan::Keep,
    }
}

#[derive(Clone, Default)]
struct UltAi {
    p: Params,
    seen: Vec<(usize, f64)>,
    last_hold: Option<usize>,
    last_cast: Option<usize>,
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
        let wants_ult = base.is_some_and(|b| b.kind == InputKindV1::Ult.code());
        let base_target = base.and_then(|b| {
            (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
        });
        // the AI's own R must never get through (its target or its position missing let it arm R at full health:
        // the log of 2026-10-08 - 376 of 442 rages armed by the AI itself): every way out below gives another input
        let stay = |ctx: &mut StableAiContext<'_>| -> Option<InputV1> {
            let sim = ctx.sim()?;
            let (x, y) = sim.get_player(player)?.champion()?.pos();
            Some(InputV1::move_to(x, y))
        };
        let Some((hp, free, danger_near, cc, target, target_pos, near_pos, line)) = (|| {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            let me = pl.champion()?;
            if !me.is_alive() {
                return None;
            }
            let (now, max) = me.hp();
            let hp = if max > 0 { now as f64 * 100.0 / max as f64 } else { 100.0 };
            let names = buff_names(&sim, me.id());
            let busy = names.iter().any(|b| *b == tr("r_armed") || *b == tr("r_rage"));
            // `is_valid_input` does not look at cooldowns (league_pyke): the slot's own state decides
            let free = !busy && pl.level() >= 5 && pl.cooldowns().is_some_and(|c| c.3 == 0);
            let (id, team) = (me.id(), me.team());
            ready_saw(&sim, id, free);
            let r2 = (R_RANGE as u64).saturating_mul(R_RANGE as u64);
            let target = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|e| e.is_champion() && e.is_alive() && e.team() != team && sim.distance_sq(id, e.id()) <= r2)
                .min_by_key(|e| sim.distance_sq(id, e.id()))
                .map(|e| e.id());
            let target_pos = base_target.and_then(|t| sim.get_entity(t)).map(|e| e.pos());
            let near_pos = target.and_then(|t| sim.get_entity(t)).map(|e| e.pos());
            Some((hp, free, enemy_near(&sim, id, team, self.p.near), controlled(&sim, id), target, target_pos, near_pos, head(&sim, id)))
        })() else {
            self.seen.clear();
            return if wants_ult { stay(ctx) } else { None };
        };
        self.seen.retain(|(t, _)| t + self.p.burst_t >= tick);
        self.seen.push((tick, hp));
        let top = self.seen.iter().map(|s| s.1).fold(hp, f64::max);
        let danger = danger_near && !cc && about_to_die(&self.p, hp, top);
        let cast = target.map(|t| InputV1::action(InputKindV1::Ult, InputTargetV1::target(t)));
        let plan = match ult_plan(wants_ult, danger, free) {
            UltPlan::Cast if !cast.is_some_and(|c| ctx.is_valid_input(&c)) => {
                if wants_ult { UltPlan::Hold } else { UltPlan::Keep }
            }
            plan => plan,
        };
        match plan {
            UltPlan::Keep => None,
            UltPlan::Cast => {
                if self.last_cast.is_none_or(|t0| tick >= t0 + LOG_EVERY) {
                    self.last_cast = Some(tick);
                    wlog(format!("{line} R CAST: hp {hp:.0}% (top {top:.0}% in {} ticks)", self.p.burst_t));
                }
                cast
            }
            UltPlan::Hold => {
                if self.last_hold.is_none_or(|t0| tick >= t0 + LOG_EVERY) {
                    self.last_hold = Some(tick);
                    wlog(format!("{line} R HELD: hp {hp:.0}%, not about to die"));
                }
                // attack the AI's target, else the nearest enemy champion; else walk to one; else stand
                for t in [base_target, target].into_iter().flatten() {
                    let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                    if ctx.is_valid_input(&attack) {
                        return Some(attack);
                    }
                }
                for (x, y) in [target_pos, near_pos].into_iter().flatten() {
                    let walk = InputV1::move_to(x, y);
                    if ctx.is_valid_input(&walk) {
                        return Some(walk);
                    }
                }
                stay(ctx)
            }
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v2 (Undying Rage at low health, R pressed only then) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:rage_end"), RageEnd);
    module.add_native_passive(format!("{ID}:guard"), Guard::default());
    module.add_player_input_ai(UltAi::default());
    host.log(LogLevel::Info, "league_tryndamere_rage v2 loaded (Tryndamere's R pressed and fired at low health, Q when hurt).");
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

    fn now(hp: f64) -> Now {
        Now { hp, top: hp, enemy_near: true, armed: true, r_free: false, raging: false, q_cd: false, fury: 3, controlled: false }
    }

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"f_crit":9,"q_heal":70,"r_hp":12,"unknown":4}"#);
        assert_eq!((p.f_crit, p.q_heal, p.r_hp), (9, 70, 12));
        assert_eq!(p.f_n, Params::default().f_n);
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn rage_only_when_about_to_die() {
        let p = Params::default();
        assert_eq!(decide(&p, &now(14.0)), Some(Move::Rage));
        assert_eq!(decide(&p, &now(60.0)), None);
        // 一秒内从 75% 掉到 38%：开；从 60% 掉到 38%：不开
        assert_eq!(decide(&p, &Now { top: 75.0, ..now(38.0) }), Some(Move::Rage));
        assert_eq!(decide(&p, &Now { top: 60.0, ..now(38.0) }), None);
        // 被控住、身边没有敌人、已经在爆发：不开
        assert_eq!(decide(&p, &Now { controlled: true, ..now(5.0) }), None);
        assert_eq!(decide(&p, &Now { enemy_near: false, ..now(5.0) }), None);
        assert_eq!(decide(&p, &Now { raging: true, ..now(5.0) }), None);
    }

    #[test]
    fn q_when_hurt_and_r_not_ready() {
        let p = Params::default();
        let q = |hp, fury, q_cd| Now { armed: false, fury, q_cd, ..now(hp) };
        assert_eq!(decide(&p, &q(25.0, 2, false)), Some(Move::Drink));
        assert_eq!(decide(&p, &q(25.0, 0, false)), None);
        assert_eq!(decide(&p, &q(25.0, 2, true)), None);
        assert_eq!(decide(&p, &q(45.0, 5, false)), None);
        // R 在待命、或冷却好了（还没按）时留给 R
        assert_eq!(decide(&p, &Now { fury: 2, ..now(25.0) }), None);
        assert_eq!(decide(&p, &Now { r_free: true, ..q(25.0, 2, false) }), None);
    }

    #[test]
    fn r_is_pressed_only_about_to_die() {
        // 满血看到敌人：AI 想放 R 也拦下
        assert_eq!(ult_plan(true, false, true), UltPlan::Hold);
        assert_eq!(ult_plan(false, false, true), UltPlan::Keep);
        // 快死了、R 好了：按 R（AI 没想放也按）
        assert_eq!(ult_plan(false, true, true), UltPlan::Cast);
        assert_eq!(ult_plan(true, true, true), UltPlan::Cast);
        // R 没好：照 AI（它放不出来）
        assert_eq!(ult_plan(false, true, false), UltPlan::Keep);
        let p = Params::default();
        assert!(about_to_die(&p, 14.0, 14.0));
        assert!(!about_to_die(&p, 100.0, 100.0));
        assert!(about_to_die(&p, 38.0, 75.0));
        assert!(!about_to_die(&p, 38.0, 60.0));
    }

    #[test]
    fn the_ai_hook_uses_the_champion_datas_numbers() {
        // UltAi has no configure(): its Params::default() must be the override's passive.params
        let text = include_str!("../override/league_tryndamere.data_champion");
        let at = text.find("\"params\"").expect("passive.params in the override");
        let body = &text[at..];
        let json = &body[body.find('{').unwrap()..=body.find('}').unwrap()];
        let p = parse_params(json);
        let d = Params::default();
        assert_eq!((p.r_hp, p.burst, p.burst_left, p.burst_t, p.near), (d.r_hp, d.burst, d.burst_left, d.burst_t, d.near));
    }

    #[test]
    fn fury_is_the_highest_stack() {
        let names: Vec<String> = ["league_tryndamere_f_1", "league_tryndamere_f_2", "league_tryndamere_f_3", "dagger"]
            .iter()
            .map(|s| s.to_string())
            .collect();
        assert_eq!(fury_of(&names, 5), 3);
        assert_eq!(fury_of(&[], 5), 0);
    }

    #[test]
    fn the_mark_carries_the_heal() {
        let p = Params { q_heal: 60, q_heal_ratio: 30, q_per: 50, q_per_ratio: 10, f_n: 5, q_anim: 24, ..Params::default() };
        let m = mark_name(&p);
        assert!(m.len() <= BUFF_NAME_CAP);
        assert_eq!(parse_mark(&m), Some(Params { ..p.clone() }));
        assert_eq!(parse_mark("league_tryndamere_r_rage"), None);
    }
}
