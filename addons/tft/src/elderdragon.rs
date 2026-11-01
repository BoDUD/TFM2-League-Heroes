//! 远古巨龙（`tft_elderdragon`）数据做不到的部分（金铲铲第 18 赛季的顶级掠食者 / 峡谷野怪五费卡，技能按用户选的方案 A
//! 「绝伦火热」，2026-11-01）。它的数据（tools/kit/build_elderdragon.py）的 `passive` 是这里的 `tft_elderdragon:elder`，
//! 参数从数据的 `passive.params` 来（build_elderdragon.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **远古巨龙霸符（处决）**：它造成伤害后，生命不高于最大生命 `p_exec`% 的敌方英雄直接被处决（补一下真实伤害，
//!   `tft_elderdragon_p_exec` 画面、`tft_elderdragon_p` 声音）。它的普攻和技能伤害从 `on_attack` 记下目标，下一拍检查；
//!   这里自己造成的伤害（吐息、引燃、溅射）当场检查。数据读不到目标剩多少血。
//! - **龙焰撕咬（溅射）** `tft_elderdragon:bite`：普攻咬中时，目标身边 `a_r` 以内的其他敌人（不含防御塔）挨 `a_splash`%
//!   攻击力的物理伤害。数据的范围效果分不出主目标。
//! - **烈焰吐息** `tft_elderdragon:breath`：朝**穿过目标、敌方英雄最多**的直线喷火。候选方向是朝 `q_len` 以内每个敌方
//!   英雄的方向，只留目标在那条带子（长 `q_len`、半宽 `q_w` 加上身子）里的方向，数带子里的敌方英雄，取最多的；一样多时
//!   取正对目标的，再取近的；没有目标（大招落地时目标已经死了）就在所有方向里取最多的。火焰是一发穿透的直线弹道
//!   （`tft_elderdragon_q_fire`，带画面，每拍 `q_speed`，从它的嘴的高度喷出：整条线往北挪 `JAWS`），烧到的每个敌人（`tft_elderdragon:scorch`，每口吐息每人一次）挨
//!   `q_dmg` + `q_ad`% 攻击力的物理伤害，每烧过一个人后面的少 `q_decay`%（最低 `q_min`%），并被【引燃】。
//! - **引燃** `tft_elderdragon:ignite`：`ig_t` 拍里每 `ig_every` 拍挨目标最大生命 `ig_hp`‰ 的物理伤害（一次最多
//!   `ig_cap`，大龙那种上万血的不至于被烧穿）；再被引燃只续时间不叠两份（`tft_elderdragon_ig` 画面）。大招落地时数据
//!   对范围里每个敌人调用它。
//! - **死亡**：倒下时播 `tft_elderdragon_d`。
//!
//! 龙翼风暴（击退、减速、减伤）和大招的无敌升空、落地晕眩、全能吸血是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_elderdragon.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::{HashMap, HashSet};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_elderdragon";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const SCORCH_FX: &str = "tft_elderdragon:scorch";
const IGNITE_TICK_FX: &str = "tft_elderdragon:ignite_tick";
/// A champion's body on top of the breath's half width (the pack's collision radius).
const BODY: u64 = 15000;
/// The fire leaves its jaws: the breath's line runs this far north of the one through its pivot (a projectile is drawn
/// at its own point, and its jaws stand 9-11 game px over its feet); far inside q_w + BODY, so it burns the same units.
const JAWS: u64 = 9000;

fn ed(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_ELDERDRAGON_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_elderdragon.log");
        }
    }
    PathBuf::from("tft_elderdragon.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the simulation thread in game, league_talon_vault)
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

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;
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
        _ => "unknown",
    };
    format!("[{kind} t={}] #{id}", sim.tick())
}

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n} #{id}"))
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 霸符：生命不高于 p_exec% 的敌方英雄被处决。
    pub p_exec: usize,
    /// 溅射：目标身边 a_r 以内的其他敌人挨 a_splash% 攻击力。
    pub a_r: usize,
    pub a_splash: usize,
    /// 吐息：长 q_len、半宽 q_w（加上身子），每拍 q_speed；q_dmg + q_ad% 攻击力，每烧过一人少 q_decay%，最低 q_min%。
    pub q_len: usize,
    pub q_w: usize,
    pub q_speed: usize,
    pub q_dmg: usize,
    pub q_ad: usize,
    pub q_decay: usize,
    pub q_min: usize,
    /// 引燃：ig_t 拍里每 ig_every 拍烧目标最大生命的 ig_hp‰（一次最多 ig_cap），物理。
    pub ig_t: usize,
    pub ig_every: usize,
    pub ig_hp: usize,
    pub ig_cap: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_exec: 15,
            a_r: 22000,
            a_splash: 35,
            q_len: 75000,
            q_w: 13000,
            q_speed: 6000,
            q_dmg: 70,
            q_ad: 130,
            q_decay: 20,
            q_min: 40,
            ig_t: 180,
            ig_every: 60,
            ig_hp: 25,
            ig_cap: 100,
        }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        let u = v.max(0) as usize;
        match k {
            "p_exec" => p.p_exec = u,
            "a_r" => p.a_r = u,
            "a_splash" => p.a_splash = u,
            "q_len" => p.q_len = u,
            "q_w" => p.q_w = u,
            "q_speed" => p.q_speed = u.max(1),
            "q_dmg" => p.q_dmg = u,
            "q_ad" => p.q_ad = u,
            "q_decay" => p.q_decay = u,
            "q_min" => p.q_min = u,
            "ig_t" => p.ig_t = u,
            "ig_every" => p.ig_every = u.max(1),
            "ig_hp" => p.ig_hp = u,
            "ig_cap" => p.ig_cap = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// 按（种子、模拟来源、比赛、局、单位）分开：同一个进程里预演和观看的模拟各算各的（league_loris 的做法）。
type Key = (u64, u32, u64, u64, usize);

/// The current breath: how many it has burned so far and who (each once).
#[derive(Default)]
struct Breath {
    hits: HashSet<usize>,
}
static BREATHS: LazyLock<Mutex<HashMap<Key, Breath>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// An Ignite on a unit: who lit it, until when, when it last burned.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Ignite {
    pub by: usize,
    pub until: usize,
    pub last: usize,
}
static IGNITES: LazyLock<Mutex<HashMap<Key, Ignite>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// Units its attacks and skills struck (on_attack), with the tick: checked for the execute on its next update.
static STRUCK: LazyLock<Mutex<HashMap<Key, Vec<(usize, usize)>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn key(sim: &StableSim<'_>, id: usize) -> Key {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index, id)
}

// ===================== 规则（单元测试用） =====================

/// base + ratio% of the attack.
pub fn physical(base: usize, ratio: usize, atk: usize) -> usize {
    base + atk * ratio / 100
}

/// The breath's damage on the `k`-th it burns (0 = the first): `decay`% less for each before, never under `min`%.
pub fn decayed(full: usize, k: usize, decay: usize, min: usize) -> usize {
    full * 100usize.saturating_sub(decay * k).max(min) / 100
}

/// Whether `hp` of `max` is at or under the execute line (`pct`% of its maximum health).
pub fn executable(hp: usize, max: usize, pct: usize) -> bool {
    hp > 0 && hp * 100 <= max * pct
}

/// One Ignite tick: `per_mille` of the target's maximum health, at least 1, at most `cap`.
pub fn ignite_tick(max_hp: usize, per_mille: usize, cap: usize) -> usize {
    (max_hp * per_mille / 1000).clamp(1, cap.max(1))
}

/// Whether a queued Ignite tick at `now` burns: still lit and a full period since the last (each lighting queues its
/// own ticks; one burns per period).
pub fn ignites_now(b: &Ignite, now: usize, every: usize) -> bool {
    now <= b.until && now >= b.last + every
}

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// Whether `at` lies in the band from `from` toward `to`: `len` long, `half` to either side.
pub fn in_band(from: (u64, u64), to: (u64, u64), at: (u64, u64), len: u64, half: u64) -> bool {
    let (dx, dy) = (to.0 as f64 - from.0 as f64, to.1 as f64 - from.1 as f64);
    let d = (dx * dx + dy * dy).sqrt();
    if d < 1.0 {
        return false;
    }
    let (ux, uy) = (dx / d, dy / d);
    let (px, py) = (at.0 as f64 - from.0 as f64, at.1 as f64 - from.1 as f64);
    let along = px * ux + py * uy;
    let off = (px * uy - py * ux).abs();
    along >= -(half as f64) && along <= len as f64 && off <= half as f64
}

/// The breath's direction (an enemy champion's id) and how many enemy champions its band holds. Candidates: toward each
/// enemy champion in reach whose band holds `through` (the target, when it stands among `champs`) - the line goes
/// through the target; with no such target, every one in reach. Ties go to the target itself, then the nearer.
/// `champs` = (id, where).
pub fn best_line(at: (u64, u64), champs: &[(usize, (u64, u64))], through: Option<usize>, len: u64, half: u64)
    -> Option<(usize, usize)> {
    let reach = ((len + half) as u128) * ((len + half) as u128);
    let target = through.and_then(|t| champs.iter().find(|c| c.0 == t).map(|c| c.1));
    champs
        .iter()
        .filter(|c| dist_sq(at, c.1) <= reach && dist_sq(at, c.1) > 0)
        .filter(|c| target.map_or(true, |t| in_band(at, c.1, t, len + half, half)))
        .map(|c| (c.0, champs.iter().filter(|o| in_band(at, c.1, o.1, len, half)).count(), dist_sq(at, c.1)))
        .max_by(|a, b| a.1.cmp(&b.1).then((Some(a.0) == through).cmp(&(Some(b.0) == through))).then(b.2.cmp(&a.2)))
        .map(|(id, n, _)| (id, n))
}

/// Where the breath stops: `len` from `from` toward `to`, clamped to the map's corner (0, 0).
pub fn end_of(from: (u64, u64), to: (u64, u64), len: u64) -> (u64, u64) {
    let (dx, dy) = (to.0 as f64 - from.0 as f64, to.1 as f64 - from.1 as f64);
    let d = (dx * dx + dy * dy).sqrt().max(1.0);
    let x = from.0 as f64 + dx / d * len as f64;
    let y = from.1 as f64 + dy / d * len as f64;
    (x.round().max(0.0) as u64, y.round().max(0.0) as u64)
}

// ===================== 场上 =====================

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

fn reachable(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive() && e.is_targetable())
}

/// Live, targetable enemy champions: (id, where).
fn enemy_champs(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64))> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && u.is_champion())
        .map(|u| (u.id(), u.pos()))
        .collect()
}

/// A unit that is no tower or nexus (the splash and the Ignite leave those alone).
fn burnable(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id)
        .is_some_and(|e| e.is_alive() && !e.is_tower() && !matches!(e.kind(), Some(EntityKindV1::Nexus)))
}

/// The Elder buff: an enemy champion at or under the line dies (true damage for what it has left).
fn execute(sim: &mut StableSim<'_>, me: usize, id: usize) {
    let Some((hp, max)) = sim.get_entity(id).filter(|e| e.is_alive() && e.is_champion()).map(|e| e.hp()) else { return };
    let team = sim.get_entity(me).map(|e| e.team());
    if sim.get_entity(id).map(|e| e.team()) == team {
        return;
    }
    let p = params_of(me);
    if !executable(hp, max, p.p_exec) {
        return;
    }
    sim.deal_damage_typed(me, id, hp + 1, DamageTypeV1::Fixed, AttackTypeV1::Skill);
    put(sim, id, &BuffV1::timed(&ed("p_exec"), 40));
    sim.play_sfx(&ed("p"), me, &InputTargetV1::target(id));
    if let Some(k) = counted("execute") {
        wlog(format!("{} EXECUTE #{k}: {} at {hp}/{max} (line {}%){}", head(sim, me), name_of(sim, id), p.p_exec,
                     if sim.get_entity(id).is_some_and(|e| e.is_alive()) { " - still alive" } else { "" }));
    }
}

/// Lights (or relights) an Ignite on `id`: its ticks queued, one burns per period while it lasts.
fn ignite(sim: &mut StableSim<'_>, me: usize, id: usize) {
    if !burnable(sim, id) {
        return;
    }
    let p = params_of(me);
    let now = sim.tick();
    let k_ = key(sim, id);
    let fresh = {
        let mut all = IGNITES.lock().unwrap_or_else(|e| e.into_inner());
        let b = all.entry(k_).or_default();
        let fresh = now > b.until;
        if fresh {
            b.last = now;   // the first tick burns a full period after the lighting
        }
        b.by = me;
        b.until = now + p.ig_t;
        fresh
    };
    put(sim, id, &BuffV1::timed(&ed("ig"), p.ig_t));
    let on = InputTargetV1::target(id);
    for k in 1..=p.ig_t / p.ig_every {
        sim.queue_effect(IGNITE_TICK_FX, AttackTypeV1::Dot, me, &on, k * p.ig_every);
    }
    if fresh {
        sim.play_sfx(&ed("burn"), me, &on);
        if let Some(k) = counted("ignite") {
            wlog(format!("{} IGNITE #{k}: {} burns {} ticks", head(sim, me), name_of(sim, id), p.ig_t));
        }
    }
}

// ===================== 龙焰撕咬 =====================

/// The bite lands (the data calls it on the attack's hit): the others round the target take the splash.
struct Bite;
impl StableEffectType for Bite {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let Some((team, atk)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.team(), e.stat().attack)) else {
            return;
        };
        let Some(at) = sim.get_entity(input.target_id).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let r = (p.a_r as u128) * (p.a_r as u128);
        let near: Vec<usize> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && u.id() != input.target_id)
            .filter(|u| dist_sq(at, u.pos()) <= r)
            .map(|u| u.id())
            .collect();
        let dmg = atk * p.a_splash / 100;
        let mut n = 0;
        for id in near {
            if !burnable(sim, id) {
                continue;
            }
            sim.deal_damage_typed(me, id, dmg.max(1), DamageTypeV1::Ad, AttackTypeV1::Skill);
            put(sim, id, &BuffV1::timed(&ed("a_splash"), 24));
            execute(sim, me, id);
            n += 1;
        }
        if n > 0 {
            if let Some(k) = counted("splash") {
                wlog(format!("{} SPLASH #{k}: round {} - {n} more take {dmg}", head(sim, me), name_of(sim, input.target_id)));
            }
        }
    }
}

// ===================== 烈焰吐息 =====================

/// The Flame Breath: fire along the line through the target with the most enemy champions.
struct BreathFx;
impl StableEffectType for BreathFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some((at, team)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.pos(), e.team())) else { return };
        let p = params_of(me);
        let champs = enemy_champs(sim, me);
        let aimed = (input.kind == InputTargetKindV1::Target.code())
            .then_some(input.target_id)
            .filter(|&id| reachable(sim, id));
        let half = p.q_w as u64 + BODY;
        let best = best_line(at, &champs, aimed, p.q_len as u64, half);
        let to = match (best, aimed) {
            (Some((id, _)), _) | (None, Some(id)) => sim.get_entity(id).map(|e| e.pos()),
            (None, None) => None,
        };
        let Some(to) = to.filter(|&t| t != at) else {
            if let Some(k) = counted("breath_none") {
                wlog(format!("{} BREATH NONE #{k}: nobody to breathe at", head(sim, me)));
            }
            return;
        };
        let end = end_of(at, to, p.q_len as u64);
        let (from, end) = ((at.0, at.1.saturating_sub(JAWS)), (end.0, end.1.saturating_sub(JAWS)));
        BREATHS.lock().unwrap_or_else(|e| e.into_inner()).insert(key(sim, me), Breath::default());
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team,
            x: from.0,
            y: from.1,
            radius: p.q_w as u64,
            speed: p.q_speed as u64,
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: end.0,
            target_y: end.1,
            penetrate: true,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        let ok = sim.spawn_projectile(&ed("q_fire"), SCORCH_FX, &spec);
        if let Some(k) = counted("breath") {
            wlog(format!("{} BREATH #{k}: {} enemy champions in the line (aimed at {}){}", head(sim, me),
                         best.map_or(0, |b| b.1), aimed.map_or_else(|| "nobody".to_string(), |id| name_of(sim, id)),
                         if ok { "" } else { " - spawn_projectile refused" }));
        }
    }
}

/// The breath reaches a unit: physical damage, less for each it burned before; Ignited.
struct Scorch;
impl StableEffectType for Scorch {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let id = input.target_id;
        if !reachable(sim, id) {
            return;
        }
        let k = {
            let mut all = BREATHS.lock().unwrap_or_else(|e| e.into_inner());
            let b = all.entry(key(sim, me)).or_default();
            if !b.hits.insert(id) {
                return;
            }
            b.hits.len() - 1
        };
        let p = params_of(me);
        let atk = sim.get_entity(me).map_or(0, |e| e.stat().attack);
        let dmg = decayed(physical(p.q_dmg, p.q_ad, atk), k, p.q_decay, p.q_min);
        sim.deal_damage_typed(me, id, dmg.max(1), DamageTypeV1::Ad, AttackTypeV1::Skill);
        put(sim, id, &BuffV1::timed(&ed("q_hit"), 30));
        sim.play_sfx(&ed("q_hit"), me, &InputTargetV1::target(id));
        ignite(sim, me, id);
        execute(sim, me, id);
        if let Some(n) = counted("scorch") {
            wlog(format!("{} SCORCH #{n}: {} takes {dmg} (the {}th burned)", head(sim, me), name_of(sim, id), k + 1));
        }
    }
}

// ===================== 引燃 =====================

/// The data's Ignite (the ult's landing, on each enemy in its reach).
struct IgniteFx;
impl StableEffectType for IgniteFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind == InputTargetKindV1::Target.code() {
            ignite(sim, me, input.target_id);
        }
    }
}

/// One Ignite tick on its target (queued by every lighting; one burns per period while it lasts).
struct IgniteTick;
impl StableEffectType for IgniteTick {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let id = input.target_id;
        let Some(max_hp) = sim.get_entity(id).filter(|e| e.is_alive()).map(|e| e.hp().1) else {
            IGNITES.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, id));
            return;
        };
        let p = params_of(me);
        let now = sim.tick();
        let by = {
            let mut all = IGNITES.lock().unwrap_or_else(|e| e.into_inner());
            let Some(b) = all.get_mut(&key(sim, id)) else { return };
            if !ignites_now(b, now, p.ig_every) {
                return;
            }
            b.last = now;
            b.by
        };
        if by != me {
            return;   // another Elder Dragon's Ignite: its own ticks burn it
        }
        let dmg = ignite_tick(max_hp, p.ig_hp, p.ig_cap);
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Dot);
        execute(sim, me, id);
        if let Some(k) = counted("ignite_tick") {
            wlog(format!("{} IGNITE TICK #{k}: {} takes {dmg}", head(sim, me), name_of(sim, id)));
        }
    }
}

// ===================== 被动：霸符、死亡 =====================

#[derive(Clone, Default)]
struct Elder {
    /// The champion it belongs to (on_dead is given the player, not the unit).
    me: usize,
    p: Params,
}

impl StablePassive for Elder {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Elder Dragon (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _: &mut usize) {
        // its attacks and skills: the execute is checked once the hit has landed (its next update)
        let now = sim.tick();
        STRUCK.lock().unwrap_or_else(|e| e.into_inner()).entry(key(sim, me)).or_default().push((target, now));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        let now = sim.tick();
        let due: Vec<usize> = {
            let mut all = STRUCK.lock().unwrap_or_else(|e| e.into_inner());
            let Some(list) = all.get_mut(&key(sim, me)) else { return };
            let due = list.iter().filter(|&&(_, t)| t < now).map(|&(id, _)| id).collect();
            list.retain(|&(_, t)| t >= now);
            due
        };
        for id in due.into_iter().collect::<HashSet<_>>() {
            execute(sim, me, id);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        let me = self.me;
        // its fall (the data has no moment for it)
        BREATHS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me));
        STRUCK.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me));
        sim.play_sfx(&ed("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// The Elder Dragon's Elder buff, the bite's splash, the Flame Breath and the Ignite, into the tft pack's module
/// (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Elder Dragon: the Elder buff's execute, the bite's splash, Flame Breath, Ignite) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:elder"), Elder::default());
    module.add_native_effect(format!("{ID}:bite"), Bite);
    module.add_native_effect(format!("{ID}:breath"), BreathFx);
    module.add_native_effect(SCORCH_FX, Scorch);
    module.add_native_effect(format!("{ID}:ignite"), IgniteFx);
    module.add_native_effect(IGNITE_TICK_FX, IgniteTick);
    host.log(LogLevel::Info, "tft.dll: Elder Dragon (Elder buff, splash, Flame Breath, Ignite).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"a_r":22000,"a_splash":35,"ig_cap":100,"ig_every":60,"ig_hp":25,"ig_t":180,"p_exec":15,"q_ad":130,"q_decay":20,"q_dmg":70,"q_len":75000,"q_min":40,"q_speed":6000,"q_w":13000}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_breath_goes_through_the_target() {
        // the target 1 alone ahead; 2 and 3 in one line to the right, without the target in it
        let champs = [(1, (0, 40000)), (2, (40000, 0)), (3, (70000, 5000))];
        assert_eq!(best_line((0, 0), &champs, Some(1), 75000, 28000), Some((1, 1)));
        // with no target: the line with the most
        assert_eq!(best_line((0, 0), &champs, None, 75000, 28000), Some((2, 2)));
        // aiming at 3, behind 2: both lines hold both, the one straight at the target wins
        assert_eq!(best_line((0, 0), &champs, Some(3), 75000, 28000), Some((3, 2)));
        // a target just past the length is still breathed through
        assert_eq!(best_line((0, 0), &[(5, (90000, 0))], Some(5), 75000, 28000), Some((5, 0)));
        // nobody in reach
        assert_eq!(best_line((0, 0), &[(4, (300000, 0))], None, 75000, 28000), None);
    }

    #[test]
    fn the_band() {
        assert!(in_band((0, 0), (10, 0), (70000, 28000), 75000, 28000));
        assert!(!in_band((0, 0), (10, 0), (70000, 29000), 75000, 28000));
        assert!(!in_band((0, 0), (10, 0), (80000, 0), 75000, 28000));
        assert!(!in_band((50000, 0), (60000, 0), (0, 0), 75000, 28000));   // behind it
    }

    #[test]
    fn the_breath_fades_along_the_line() {
        assert_eq!(decayed(300, 0, 20, 40), 300);
        assert_eq!(decayed(300, 1, 20, 40), 240);
        assert_eq!(decayed(300, 3, 20, 40), 120);
        assert_eq!(decayed(300, 5, 20, 40), 120);   // never under 40%
        assert_eq!(end_of((100000, 100000), (130000, 140000), 75000), (145000, 160000));
    }

    #[test]
    fn the_execute_line() {
        assert!(executable(150, 1000, 15));
        assert!(!executable(151, 1000, 15));
        assert!(!executable(0, 1000, 15));   // already dead
    }

    #[test]
    fn the_ignite() {
        assert_eq!(ignite_tick(2000, 25, 100), 50);
        assert_eq!(ignite_tick(12000, 25, 100), 100);   // an epic monster: capped
        assert_eq!(ignite_tick(20, 25, 100), 1);        // at least 1
        let b = Ignite { by: 1, until: 300, last: 120 };
        assert!(!ignites_now(&b, 170, 60));   // the period not over (another lighting's queued tick)
        assert!(ignites_now(&b, 180, 60));
        assert!(!ignites_now(&b, 301, 60));   // burnt out
    }

    #[test]
    fn damage_by_the_numbers() {
        let p = Params::default();
        assert_eq!(physical(p.q_dmg, p.q_ad, 100), 70 + 130);
    }
}
