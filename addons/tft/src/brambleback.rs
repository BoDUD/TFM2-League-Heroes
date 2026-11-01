//! 绯红印记树怪（`tft_brambleback`）数据做不到的部分（金铲铲第 18 赛季的峡谷野怪 / 狂战士四费卡，技能按用户选的方案 A
//! 「猩红之怒」，2026-10-31）。它的数据（tools/kit/build_brambleback.py）的 `passive` 是这里的 `tft_brambleback:fury`，
//! 参数从数据的 `passive.params` 来（build_brambleback.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **红霸符** `tft_brambleback:red`（数据在普攻命中那一拍调用）：它回复自己最大生命的 `p_heal`‰；打的不是防御塔 /
//!   水晶，就让目标灼烧 `p_burn_t` 拍（`tft_brambleback_p_burn`，带画面）：每 `p_burn_every` 拍一次真实伤害，目标最大生命
//!   的 `p_burn`‰，一次最多 `p_burn_cap`（大龙、先锋那种上万血的不至于被烧穿）。再打一下只续时间，不叠两份。数据读不到
//!   目标是不是防御塔，也没有按自己最大生命回血的治疗。
//! - **扑向下一个**（金铲铲的被动）：它杀了人（英雄 `on_kill`，小兵野怪 `on_unit_kill`），`k_cd` 拍一次：扑向 `k_range`
//!   以内最近的敌方英雄；没有英雄、而杀的是野怪时，扑向最近的野怪（清野时一路扑过去；小兵不追）。每拍跳 `k_speed`，
//!   最多 `k_t` 拍，落到身前（`tft_brambleback:hop` 一拍一拍接着跳，Q 的跃起动画 `skill` 放着）；落地时那个人（还活着、
//!   碰得到）挨 `k_dmg` + `k_ad`% 攻击力的物理伤害，亮 `tft_brambleback_q_hit`。数据不知道谁被它杀了。
//! - **死亡**：倒下时播 `tft_brambleback_d`。
//!
//! 荆爪横扫、荆棘飞扑（跳脸）、绯红咆哮和猩红之怒是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_brambleback.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_brambleback";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const BURN_FX: &str = "tft_brambleback:burn";
const HOP_FX: &str = "tft_brambleback:hop";
/// 落到身前的距离（两个身子碰到）。
const TOUCH: u64 = 22000;

fn bb(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_BRAMBLEBACK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_brambleback.log");
        }
    }
    PathBuf::from("tft_brambleback.log")
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
    /// 红霸符：每 p_burn_every 拍烧目标最大生命的 p_burn‰（一次最多 p_burn_cap），共 p_burn_t 拍；每下普攻回自己最大
    /// 生命的 p_heal‰。
    pub p_burn: usize,
    pub p_burn_t: usize,
    pub p_burn_every: usize,
    pub p_burn_cap: usize,
    pub p_heal: usize,
    /// 扑向下一个：k_range 以内，每拍 k_speed，最多 k_t 拍；落地 k_dmg + k_ad% 攻击力；k_cd 拍一次。
    pub k_range: usize,
    pub k_speed: usize,
    pub k_t: usize,
    pub k_dmg: usize,
    pub k_ad: usize,
    pub k_cd: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_burn: 6,
            p_burn_t: 180,
            p_burn_every: 30,
            p_burn_cap: 40,
            p_heal: 15,
            k_range: 60000,
            k_speed: 4000,
            k_t: 24,
            k_dmg: 60,
            k_ad: 120,
            k_cd: 60,
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
            "p_burn" => p.p_burn = u,
            "p_burn_t" => p.p_burn_t = u,
            "p_burn_every" => p.p_burn_every = u.max(1),
            "p_burn_cap" => p.p_burn_cap = u,
            "p_heal" => p.p_heal = u,
            "k_range" => p.k_range = u,
            "k_speed" => p.k_speed = u.max(1),
            "k_t" => p.k_t = u,
            "k_dmg" => p.k_dmg = u,
            "k_ad" => p.k_ad = u,
            "k_cd" => p.k_cd = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// 一次扑击：扑向谁、到哪一拍为止、它最后在哪。
#[derive(Clone, Debug, Default)]
struct Leap {
    target: usize,
    until: usize,
    last: (u64, u64),
}

/// 一个目标身上的灼烧：谁点的、烧到哪一拍、上次烧在哪一拍。
#[derive(Clone, Copy, Debug, Default)]
pub struct Burn {
    pub by: usize,
    pub until: usize,
    pub last: usize,
}

/// 按（种子、模拟来源、比赛、局、单位）分开：同一个进程里预演和观看的模拟各算各的（league_loris 的做法）。
type Key = (u64, u32, u64, u64, usize);
static LEAPS: LazyLock<Mutex<HashMap<Key, Leap>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static BURNS: LazyLock<Mutex<HashMap<Key, Burn>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn key(sim: &StableSim<'_>, id: usize) -> Key {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index, id)
}

// ===================== 规则（单元测试用） =====================

/// base + ratio% of the attack.
pub fn physical(base: usize, ratio: usize, atk: usize) -> usize {
    base + atk * ratio / 100
}

/// One burn tick: `per_mille` of the target's maximum health, at least 1, at most `cap`.
pub fn burn_tick(max_hp: usize, per_mille: usize, cap: usize) -> usize {
    (max_hp * per_mille / 1000).clamp(1, cap.max(1))
}

/// Whether a queued burn tick at `now` burns: the burn still on and a full period since the last one (the ticks each hit
/// queues overlap; one burns per period).
pub fn burns_now(b: &Burn, now: usize, every: usize) -> bool {
    now <= b.until && now >= b.last + every
}

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// `speed` from `from` toward `to` (or onto it when nearer).
pub fn step(from: (u64, u64), to: (u64, u64), speed: u64) -> (u64, u64) {
    let d = (dist_sq(from, to) as f64).sqrt();
    if d <= speed as f64 {
        return to;
    }
    let k = speed as f64 / d;
    let x = from.0 as f64 + (to.0 as f64 - from.0 as f64) * k;
    let y = from.1 as f64 + (to.1 as f64 - from.1 as f64) * k;
    (x.round().max(0.0) as u64, y.round().max(0.0) as u64)
}

/// The point TOUCH short of `to` on the way from `from` (where it lands in front of it).
pub fn front_of(from: (u64, u64), to: (u64, u64)) -> (u64, u64) {
    let d = (dist_sq(from, to) as f64).sqrt();
    step(from, to, (d - TOUCH as f64).max(0.0) as u64)
}

/// The next to leap at among (id, where, champion, jungle monster) within `reach` of `at`: the nearest champion; with
/// none, the nearest jungle monster when `camp` (it killed a monster); ties go to the lower id.
pub fn next_target(at: (u64, u64), foes: &[(usize, (u64, u64), bool, bool)], reach: usize, camp: bool) -> Option<usize> {
    let r = (reach as u128) * (reach as u128);
    let nearest = |want: &dyn Fn(&(usize, (u64, u64), bool, bool)) -> bool| {
        foes.iter()
            .filter(|f| want(f) && dist_sq(at, f.1) <= r)
            .min_by(|a, b| dist_sq(at, a.1).cmp(&dist_sq(at, b.1)).then(a.0.cmp(&b.0)))
            .map(|f| f.0)
    };
    nearest(&|f| f.2).or_else(|| if camp { nearest(&|f| f.3) } else { None })
}

/// The leap's animation: TFT's spring and landing (the Q's `skill` tag) for the ticks it takes, at most `k_t`.
pub fn leap_ticks(from: (u64, u64), to: (u64, u64), speed: usize, cap: usize) -> usize {
    let d = (dist_sq(from, front_of(from, to)) as f64).sqrt();
    ((d / speed.max(1) as f64).ceil() as usize + 2).min(cap)
}

/// An Animation CC: `tag` of its sheet played for `ticks`, it does nothing else meanwhile (league_bard's door).
pub fn animation(tag: &str, ticks: usize) -> CcV1 {
    let mut cc = CcV1::of_kind(CcKindV1::Animation, ticks as u64);
    cc.set_name(tag);
    cc
}

// ===================== 场上 =====================

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

fn reachable(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive() && e.is_targetable())
}

/// Live, targetable enemies it may leap at: (id, where, champion, jungle monster); no towers, nexus or minions' kin
/// beyond what `next_target` picks.
fn foes(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64), bool, bool)> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable())
        .map(|u| (u.id(), u.pos(), u.is_champion(), matches!(u.kind(), Some(EntityKindV1::Jungle))))
        .collect()
}

// ===================== 红霸符 =====================

/// A claw lands (the data calls it on the attack's hit): it heals; a target that is no tower or nexus burns.
struct Red;
impl StableEffectType for Red {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(max_hp) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.hp().1) else { return };
        let p = params_of(me);
        sim.heal(me, me, max_hp * p.p_heal / 1000);
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let id = input.target_id;
        let Some(burnable) = sim.get_entity(id).filter(|e| e.is_alive()).map(|e| {
            !e.is_tower() && !matches!(e.kind(), Some(EntityKindV1::Nexus))
        }) else {
            return;
        };
        if !burnable {
            return;
        }
        let now = sim.tick();
        let k_ = key(sim, id);
        let fresh = {
            let mut burns = BURNS.lock().unwrap_or_else(|e| e.into_inner());
            let b = burns.entry(k_).or_default();
            let fresh = now > b.until;
            if fresh {
                b.last = now;   // the first tick burns a full period after the hit
            }
            b.by = me;
            b.until = now + p.p_burn_t;
            fresh
        };
        put(sim, id, &BuffV1::timed(&bb("p_burn"), p.p_burn_t));
        let on = InputTargetV1::target(id);
        for k in 1..=p.p_burn_t / p.p_burn_every {
            sim.queue_effect(BURN_FX, AttackTypeV1::Dot, me, &on, k * p.p_burn_every);
        }
        if fresh {
            sim.play_sfx(&bb("p"), me, &on);
            if let Some(k) = counted("burn") {
                wlog(format!("{} BURN #{k}: {} burns {} ticks", head(sim, me), name_of(sim, id), p.p_burn_t));
            }
        }
    }
}

/// One burn tick on its target (queued by every hit; one burns per period while the burn lasts).
struct BurnTick;
impl StableEffectType for BurnTick {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let id = input.target_id;
        let Some(max_hp) = sim.get_entity(id).filter(|e| e.is_alive()).map(|e| e.hp().1) else {
            BURNS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, id));
            return;
        };
        let p = params_of(me);
        let now = sim.tick();
        let k_ = key(sim, id);
        let by = {
            let mut burns = BURNS.lock().unwrap_or_else(|e| e.into_inner());
            let Some(b) = burns.get_mut(&k_) else { return };
            if !burns_now(b, now, p.p_burn_every) {
                return;
            }
            b.last = now;
            b.by
        };
        if by != me {
            return;   // another Brambleback's burn: its own ticks burn it
        }
        let dmg = burn_tick(max_hp, p.p_burn, p.p_burn_cap);
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Fixed, AttackTypeV1::Dot);
        if let Some(k) = counted("burn_tick") {
            wlog(format!("{} BURN TICK #{k}: {} takes {dmg}", head(sim, me), name_of(sim, id)));
        }
    }
}

// ===================== 扑向下一个 =====================

fn leap(sim: &mut StableSim<'_>, me: usize, victim: usize, camp: bool) -> bool {
    let Some(at) = sim.get_entity(me).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.pos()) else { return false };
    let p = params_of(me);
    let Some(target) = next_target(at, &foes(sim, me), p.k_range, camp) else {
        if let Some(k) = counted("leap_none") {
            wlog(format!("{} LEAP NONE #{k}: killed {}, nobody in reach", head(sim, me), name_of(sim, victim)));
        }
        return false;
    };
    let to = sim.get_entity(target).map_or(at, |e| e.pos());
    let k_ = key(sim, me);
    LEAPS.lock().unwrap_or_else(|e| e.into_inner()).insert(k_, Leap { target, until: sim.tick() + p.k_t, last: to });
    sim.apply_cc(me, &animation("skill", leap_ticks(at, to, p.k_speed, p.k_t)));
    sim.play_sfx(&bb("q_next"), me, &InputTargetV1::target(me));
    if let Some(k) = counted("leap") {
        let d = (dist_sq(at, to) as f64).sqrt() as u64;
        wlog(format!("{} LEAP #{k}: killed {}, on to {} ({d} away)", head(sim, me), name_of(sim, victim),
                     name_of(sim, target)));
    }
    hop(sim, me, k_);
    true
}

/// One tick of the leap (queued again until it lands or runs out of ticks).
struct Hop;
impl StableEffectType for Hop {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let k_ = key(sim, me);
        hop(sim, me, k_);
    }
}

fn hop(sim: &mut StableSim<'_>, me: usize, k_: Key) {
    let Some(mut l) = LEAPS.lock().unwrap_or_else(|e| e.into_inner()).get(&k_).cloned() else { return };
    let Some(from) = sim.get_entity(me).filter(|e| e.is_alive() && e.is_targetable()).map(|e| e.pos()) else {
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
        return;
    };
    let p = params_of(me);
    if reachable(sim, l.target) {
        l.last = sim.get_entity(l.target).map_or(l.last, |e| e.pos());
    }
    let goal = front_of(from, l.last);
    let next = step(from, goal, p.k_speed as u64);
    sim.entity_set_pos(me, next.0, next.1);
    let landed = next == goal;
    if !landed && sim.tick() < l.until {
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).insert(k_, l);
        sim.queue_effect(HOP_FX, AttackTypeV1::Skill, me, &InputTargetV1::target(me), 1);
        return;
    }
    LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
    if !landed || !reachable(sim, l.target) {
        if let Some(k) = counted("land_miss") {
            wlog(format!("{} LAND MISS #{k}: {} ({})", head(sim, me), name_of(sim, l.target),
                         if landed { "the target is gone" } else { "out of ticks" }));
        }
        return;
    }
    let atk = sim.get_entity(me).map_or(0, |e| e.stat().attack);
    let dmg = physical(p.k_dmg, p.k_ad, atk);
    let id = l.target;
    sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
    let on = InputTargetV1::target(id);
    sim.play_view_effect(&bb("q_hit"), me, &on, 0, 0, 0);
    sim.play_sfx(&bb("q_hit"), me, &on);
    if let Some(k) = counted("land") {
        wlog(format!("{} LAND #{k}: {} takes {dmg}", head(sim, me), name_of(sim, id)));
    }
}

// ===================== 被动：猩红之怒 =====================

#[derive(Clone, Default)]
struct Fury {
    /// The champion it belongs to (on_dead is given the player, not the unit).
    me: usize,
    p: Params,
    /// The tick the next leap may start (k_cd after the last).
    ready_at: usize,
}

impl Fury {
    fn killed(&mut self, sim: &mut StableSim<'_>, me: usize, victim: usize, camp: bool) {
        let now = sim.tick();
        if now < self.ready_at || LEAPS.lock().unwrap_or_else(|e| e.into_inner()).contains_key(&key(sim, me)) {
            return;
        }
        if leap(sim, me, victim, camp) {
            self.ready_at = now + self.p.k_cd;
        }
    }
}

impl StablePassive for Fury {
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
            wlog(format!("{} SPAWN #{k}: tft.dll's Brambleback (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, _: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.killed(sim, me, victim, false);
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        let camp = sim.get_entity(victim).is_some_and(|e| matches!(e.kind(), Some(EntityKindV1::Jungle)));
        if camp {
            self.killed(sim, me, victim, true);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        let me = self.me;
        // its collapse (the data has no moment for it)
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me));
        sim.play_sfx(&bb("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// The Crimson Brambleback's Red Buff and its leap on to the next, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Crimson Brambleback: Red Buff, the leap on to the next) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:fury"), Fury::default());
    module.add_native_effect(format!("{ID}:red"), Red);
    module.add_native_effect(BURN_FX, BurnTick);
    module.add_native_effect(HOP_FX, Hop);
    host.log(LogLevel::Info, "tft.dll: Crimson Brambleback (Red Buff, the leap on to the next).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"k_ad":120,"k_cd":60,"k_dmg":60,"k_range":60000,"k_speed":4000,"k_t":24,"p_burn":6,"p_burn_cap":40,"p_burn_every":30,"p_burn_t":180,"p_heal":15}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_burn() {
        assert_eq!(burn_tick(2000, 6, 40), 12);
        assert_eq!(burn_tick(12000, 6, 40), 40);   // an epic monster: capped
        assert_eq!(burn_tick(100, 6, 40), 1);      // at least 1
        let b = Burn { by: 1, until: 300, last: 120 };
        assert!(!burns_now(&b, 140, 30));   // the period not over (another hit's queued tick)
        assert!(burns_now(&b, 150, 30));
        assert!(!burns_now(&b, 301, 30));   // the burn is out
    }

    #[test]
    fn the_next_target() {
        // (id, where, champion, jungle monster): 1 a monster near, 2 a champion farther, 3 a champion out of reach
        let foes = [(1, (10000, 0), false, true), (2, (40000, 0), true, false), (3, (90000, 0), true, false),
                    (4, (5000, 0), false, false)];
        assert_eq!(next_target((0, 0), &foes, 60000, true), Some(2));    // champions first
        assert_eq!(next_target((0, 0), &foes[..1], 60000, true), Some(1));   // a camp: on to the next monster
        assert_eq!(next_target((0, 0), &foes[..1], 60000, false), None);     // a champion's kill: no monster
        assert_eq!(next_target((0, 0), &foes[3..], 60000, true), None);      // minions never
    }

    #[test]
    fn the_leap() {
        assert_eq!(front_of((0, 0), (50000, 0)), (28000, 0));
        assert_eq!(step((0, 0), (28000, 0), 4000), (4000, 0));
        assert_eq!(leap_ticks((0, 0), (50000, 0), 4000, 24), 9);
        assert_eq!(leap_ticks((0, 0), (500000, 0), 4000, 24), 24);
        assert_eq!(physical(60, 120, 100), 180);
        let c = animation("skill", 9);
        assert_eq!((c.kind, c.tick, c.name()), (CcKindV1::Animation.code(), 9, "skill"));
    }
}
