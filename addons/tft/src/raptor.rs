//! 深红锋喙鸟（`tft_raptor`，用户叫它锋啄鸟）数据做不到的部分（金铲铲第 18 赛季的峡谷野怪 / 召唤师 / 迅捷射手；技能按用户选的
//! 方案 A「鸟群之家」，2026-10-31）。她的数据（tools/kit/build_raptor.py）的 `passive` 是这里的 `tft_raptor:flock`，参数从数据的
//! `passive.params` 来（build_raptor.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **羽刃扇射**：数据里的投射物不能带角度，所以出手那一 tick（`tft_raptor:fan`）由这里朝目标方向扇形发出 `q_n` 根羽刃，
//!   相邻两根差 `q_spread` 度，每根各自直飞 `q_len`、碰到第一个敌人就停（`tft_raptor_q_feather`）；命中
//!   （`tft_raptor:fan_hit`）受到 `q_dmg` + `q_ratio`% 攻击力的物理伤害，再挂一层橙霸符。近身时一个敌人会吃到好几根。
//!   2026-11-05（0.53.0，11-04 的日志：十分之一的 Q `FAN: no aim (input kind 1)`，一根都没出——目标在 11 拍起手里死了，
//!   出手那一拍已经查不到它）：被动每拍记下她 `q_len` 一倍半内每个敌人最后的位置（`SEEN`），目标没了就朝它最后的位置扇
//!   （`aim_fallback`：`last place`），没记过就朝 `q_len` 内最近的、看得见的、不是塔的敌人（`nearest`），都没有才作罢
//!   （SDK 读不到她的朝向）。日志 `FAN ... (aimed at X's last place / the nearest, Y)`。
//!   2026-11-06（0.54.0，11-06 的日志：95 次扇射还有 25 次 `no aim`）：`SEEN` 原来是一张全局表、只按她的实体编号记，每份
//!   模拟的被动都按自己的 tick 清它——同时跑的别的模拟里同一个编号的锋喙鸟（#21、#26 几乎每局都是）一清，这份的记录就没了。
//!   现在按（这份模拟的编号 `SIM_TAG`，她）分行记（sim_tag.rs，洛里斯、赛芬的做法），每份只清自己那一行。
//! - **橙霸符**：她的每次物理命中（普攻、羽刃、小锋喙鸟的啄击）都调 `tft_raptor:shred`：目标护甲 -`p_arm`，持续 `p_t`
//!   tick，最多 `p_max` 层，再中一下刷新时长（引擎的叠层 buff；数据的同名 buff 只会无限叠）。叠满那一下播 `tft_raptor_p`。
//! - **死亡**：倒下时播 `tft_raptor_d`（数据没有死亡的时机）。
//!
//! 普攻的羽毛、惊飞跃退（后跳、攻速）和大招的小锋喙鸟（旗子 `tft_raptor_r_flock` 期间每次普攻追加的啄击）是数据自己的。
//! 两张 5v5 地图（2026-11-10）：羽刃飞到的点夹在这一场的地图里（`game_places::terrain::map_of_sim`：游戏自己的 960000 见方，
//! Rin 的召唤师峡谷 1614545 见方；以前一律按 960000，峡谷上过了 960000 的羽刃都朝半张图的边上飞）。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_raptor.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{map_of_sim, rift_status, Map};
use mod_api_stable::*;

use crate::sim_tag::{Key, SimTag};

const ID: &str = "tft_raptor";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 游戏自己的 5v5 地图边长；峡谷的看 `Map::extent`。
const MAP: f64 = 960_000.0;
const FAN_HIT: &str = "tft_raptor:fan_hit";

fn rp(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_RAPTOR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_raptor.log");
        }
    }
    PathBuf::from("tft_raptor.log")
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

/// 这次启动已经在日志里说过峡谷了。
static RIFT_TOLD: AtomicBool = AtomicBool::new(false);

/// 这一场的地图；第一次碰到峡谷（一次启动）时日志写一行。
fn map_here(sim: &StableSim<'_>) -> Map {
    let map = map_of_sim(sim);
    if map == Map::Rift && !RIFT_TOLD.swap(true, Ordering::Relaxed) {
        wlog(format!("== Rift: the feathers' end points are kept on the Rift's {:.0} square (not the game's own {MAP:.0}); \
                      {} ==", map.extent(), rift_status()));
    }
    map
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub p_arm: usize,
    pub p_max: usize,
    pub p_t: usize,
    pub q_n: usize,
    pub q_spread: usize,
    pub q_len: usize,
    pub q_w: usize,
    pub q_speed: usize,
    pub q_dmg: usize,
    pub q_ratio: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_arm: 6,
            p_max: 5,
            p_t: 180,
            q_n: 5,
            q_spread: 12,
            q_len: 70000,
            q_w: 4000,
            q_speed: 6500,
            q_dmg: 35,
            q_ratio: 55,
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
            "p_arm" => p.p_arm = u,
            "p_max" => p.p_max = u.max(1),
            "p_t" => p.p_t = u.max(1),
            "q_n" => p.q_n = u.max(1),
            "q_spread" => p.q_spread = u,
            "q_len" => p.q_len = u,
            "q_w" => p.q_w = u,
            "q_speed" => p.q_speed = u.max(1),
            "q_dmg" => p.q_dmg = u,
            "q_ratio" => p.q_ratio = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// Each simulation's number (`SIM_TAG`, 0.54.0): hung on her at every spawn, read back by Q's release (an effect).
const TAG: SimTag = SimTag("tft_raptor_sim:");

/// One raptor's row: the enemies she saw lately, id -> (where, the tick).
pub type Seen = HashMap<usize, ((u64, u64), usize)>;

/// The enemies each raptor saw lately, by (this simulation's number `SIM_TAG`, the raptor). Q's release aims at a target
/// gone in the wind-up by its last place. 0.53.0 kept one row per entity id for every simulation, and every simulation's
/// update purged it by its own clock: another match running at the same time with a raptor at the same id (#21 / #26
/// nearly every match) wiped the rows - 25 of 95 fans of 11-06 still had no aim.
static SEEN: LazyLock<Mutex<HashMap<Key, Seen>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// A place is kept this many ticks after the unit was last seen.
pub const SEEN_FOR: usize = 60;

/// One look round by the raptor of `row` at `now`: the places in her own row older than `SEEN_FOR` go (only hers - the
/// other simulations' rows run on their own clocks), then the enemies `near` her now go in. Never a clear of the table:
/// the first 0.54.0 build cleared it past 4096 rows, the rows of the simulations running beside it too (a finished
/// simulation leaves one row a raptor; `forget_lives` takes her earlier lives').
pub fn remember(all: &mut HashMap<Key, Seen>, row: Key, now: usize, near: &[(usize, (u64, u64))]) {
    let seen = all.entry(row).or_default();
    seen.retain(|_, &mut (_, t)| t <= now && now < t + SEEN_FOR);
    for &(id, pos) in near {
        seen.insert(id, (pos, now));
    }
}

/// Where the raptor of `row` last saw `target` (None: not in her row).
pub fn last_place(all: &HashMap<Key, Seen>, row: Key, target: usize) -> Option<(u64, u64)> {
    all.get(&row).and_then(|m| m.get(&target)).map(|&(p, _)| p)
}

/// A new life of the raptor numbered `no` (a respawn is a new entity): the rows of her last ones go.
pub fn forget_lives(all: &mut HashMap<Key, Seen>, no: u64) {
    all.retain(|k, _| k.0 != no);
}

/// Where Q's fan goes when its target is gone at the release: the target's last place, else the nearest of `foes`
/// (visible, no tower) within `reach`; None with neither (the SDK reads no facing).
pub fn aim_fallback(from: (f64, f64), last: Option<(f64, f64)>, foes: &[(usize, (f64, f64))], reach: f64)
    -> Option<((f64, f64), Fallback)> {
    if let Some(p) = last.filter(|p| (p.0 - from.0).hypot(p.1 - from.1) > 1.0) {
        return Some((p, Fallback::LastPlace));
    }
    foes.iter()
        .map(|f| (f, (f.1 .0 - from.0).hypot(f.1 .1 - from.1)))
        .filter(|(_, d)| *d > 1.0 && *d <= reach)
        .min_by(|a, b| a.1.total_cmp(&b.1))
        .map(|(f, _)| (f.1, Fallback::Nearest(f.0)))
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Fallback {
    LastPlace,
    Nearest(usize),
}

// ===================== 规则（单元测试用） =====================

/// The fan's directions (unit vectors): `n` feathers round `aim`, `spread` degrees apart, the middle one (an odd `n`)
/// straight at it, the rest mirrored either side.
pub fn fan_dirs(aim: (f64, f64), n: usize, spread: usize) -> Vec<(f64, f64)> {
    let base = aim.1.atan2(aim.0);
    let mid = (n as f64 - 1.0) / 2.0;
    (0..n)
        .map(|k| {
            let a = base + ((k as f64 - mid) * spread as f64).to_radians();
            (a.cos(), a.sin())
        })
        .collect()
}

/// One feather's physical damage before armour: q_dmg + q_ratio% of her attack.
pub fn feather_damage(attack: usize, p: &Params) -> usize {
    (p.q_dmg + attack * p.q_ratio / 100).max(1)
}

/// Orange Buff's stack: p_arm armour off for p_t ticks (same-name stat buffs count as stacks).
pub fn shred_buff(p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(&rp("p_shred"), p.p_t);
    b.defence = -(p.p_arm as i32);
    b
}

// ===================== 模拟里的小工具 =====================

/// A spot on `map` in whole units (a feather's end point).
fn upos(map: Map, p: (f64, f64)) -> (u64, u64) {
    let e = map.extent();
    (p.0.round().clamp(0.0, e - 1.0) as u64, p.1.round().clamp(0.0, e - 1.0) as u64)
}

fn stacks(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).count())
}

/// Orange Buff on one struck enemy: one more stack up to p_max, the timer refreshed; the sound when it fills.
fn shred(sim: &mut StableSim<'_>, me: usize, id: usize) {
    let p = params_of(me);
    let alive = sim.get_entity(id).is_some_and(|e| e.is_alive() && !e.is_tower());
    if !alive {
        return;
    }
    let before = stacks(sim, id, &rp("p_shred"));
    let after = sim.entity_stack_buff(id, &shred_buff(&p), p.p_max, true);
    if before < p.p_max && after >= p.p_max {
        sim.play_sfx(&rp("p"), me, &InputTargetV1::target(id));
    }
    if let Some(k) = counted("shred") {
        wlog(format!("{} SHRED #{k}: {} armour -{} x {after}", head(sim, me), name_of(sim, id), p.p_arm));
    }
}

/// Q's release: q_n feathers in a fan toward the action's target, each stopping at the first enemy.
fn fan(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some((team, at)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.team(), e.pos())) else { return };
    let from = (at.0 as f64, at.1 as f64);
    let p = params_of(me);
    let mut how = String::new();
    let aim = if input.kind == InputTargetKindV1::Target.code() {
        let target = sim.get_entity(input.target_id).filter(|e| e.is_alive()).map(|e| (e.pos().0 as f64, e.pos().1 as f64));
        target.or_else(|| {
            // the target died in the wind-up (0.53.0): its last place, else the nearest visible enemy in reach; the place
            // from this simulation's own row (0.54.0)
            let row = TAG.key(sim, me, me);
            let last = last_place(&SEEN.lock().unwrap_or_else(|e| e.into_inner()), row, input.target_id)
                .map(|p| (p.0 as f64, p.1 as f64));
            let foes: Vec<(usize, (f64, f64))> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower() && sim.is_visible(team, u.id()))
                .map(|u| (u.id(), (u.pos().0 as f64, u.pos().1 as f64)))
                .collect();
            let (aim, by) = aim_fallback(from, last, &foes, p.q_len as f64)?;
            how = match by {
                Fallback::LastPlace => format!(" (aimed at the last place of #{})", input.target_id),
                Fallback::Nearest(id) => format!(" (#{} gone: aimed at the nearest, {})", input.target_id, name_of(sim, id)),
            };
            Some(aim)
        })
    } else if input.kind == InputTargetKindV1::Pos.code() {
        Some((input.x as f64, input.y as f64))
    } else {
        None
    };
    let Some(aim) = aim.map(|a| (a.0 - from.0, a.1 - from.1)).filter(|d| d.0.hypot(d.1) > 1.0) else {
        if let Some(k) = counted("no aim") {
            wlog(format!("{} FAN #{k}: no aim (input kind {}, nobody in reach)", head(sim, me), input.kind));
        }
        return;
    };
    let mut refused = 0;
    let map = map_here(sim);
    for d in fan_dirs(aim, p.q_n, p.q_spread) {
        let to = upos(map, (from.0 + d.0 * p.q_len as f64, from.1 + d.1 * p.q_len as f64));
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team,
            x: at.0,
            y: at.1,
            radius: p.q_w as u64,
            speed: p.q_speed as u64,
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: to.0,
            target_y: to.1,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        if !sim.spawn_projectile(&rp("q_feather"), FAN_HIT, &spec) {
            refused += 1;
        }
    }
    if let Some(k) = counted("fan") {
        wlog(format!(
            "{} FAN #{k}: {} feathers {} deg apart toward ({:.0}, {:.0}){how}{}",
            head(sim, me),
            p.q_n,
            p.q_spread,
            from.0 + aim.0,
            from.1 + aim.1,
            if refused > 0 { format!(" - spawn_projectile refused {refused}") } else { String::new() }
        ));
    }
}

/// One feather's hit.
fn fan_hit(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if input.kind != InputTargetKindV1::Target.code() {
        return;
    }
    let id = input.target_id;
    let p = params_of(me);
    let atk = sim.get_entity(me).map_or(0, |e| e.stat().attack);
    let d = feather_damage(atk, &p);
    sim.deal_damage(me, id, d, 0, AttackTypeV1::Skill);
    let on = InputTargetV1::target(id);
    sim.play_view_effect(&rp("q_hit"), me, &on, 0, 0, 0);
    sim.play_sfx(&rp("q_hit"), me, &on);
    shred(sim, me, id);
    if let Some(k) = counted("fan hit") {
        wlog(format!("{} FEATHER #{k}: {} takes {d} physical", head(sim, me), name_of(sim, id)));
    }
}

struct Fan;
impl StableEffectType for Fan {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        fan(sim, me, input);
    }
}

struct FanHit;
impl StableEffectType for FanHit {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        fan_hit(sim, me, input);
    }
}

struct Shred;
impl StableEffectType for Shred {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind == InputTargetKindV1::Target.code() {
            shred(sim, me, input.target_id);
        }
    }
}

// ===================== 被动：鸟群（参数、死亡音效） =====================

#[derive(Clone, Default)]
struct Flock {
    /// The champion it belongs to (on_dead is given the player, not the unit).
    me: usize,
    p: Params,
    /// This simulation's number (`SIM_TAG`), drawn at her first spawn (0.54.0).
    sim: u64,
}

impl StablePassive for Flock {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        TAG.spawn(sim, me, &mut self.sim);
        forget_lives(&mut SEEN.lock().unwrap_or_else(|e| e.into_inner()), self.sim);
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Crimson Raptor (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        // the enemies near her, for a Q whose target dies in the wind-up (0.53.0)
        let Some((team, at)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.team(), e.pos())) else { return };
        let now = sim.tick();
        let reach = (self.p.q_len as f64) * 1.5;
        let near: Vec<(usize, (u64, u64))> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive() && !u.is_tower())
            .filter(|u| (u.pos().0 as f64 - at.0 as f64).hypot(u.pos().1 as f64 - at.1 as f64) <= reach)
            .map(|u| (u.id(), u.pos()))
            .collect();
        // her own row only (0.54.0): another simulation's raptor at the same id purges its own
        remember(&mut SEEN.lock().unwrap_or_else(|e| e.into_inner()), (self.sim, me), now, &near);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        let me = self.me;
        // her death cry (the data has no moment for it)
        sim.play_sfx(&rp("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// The Crimson Raptor's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Crimson Raptor: Feather Fan, Orange Buff's capped armour shred) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:flock"), Flock::default());
    module.add_native_effect(format!("{ID}:fan"), Fan);
    module.add_native_effect(format!("{ID}:fan_hit"), FanHit);
    module.add_native_effect(format!("{ID}:shred"), Shred);
    host.log(LogLevel::Info, "tft.dll: Crimson Raptor (Feather Fan, Orange Buff).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_arm":6,"p_max":5,"p_t":180,"q_dmg":35,"q_len":70000,"q_n":5,"q_ratio":55,"q_speed":6500,"q_spread":12,"q_w":4000}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn a_feather_hurts_by_its_attack() {
        let p = Params::default();
        assert_eq!(feather_damage(0, &p), 35);
        assert_eq!(feather_damage(100, &p), 90);
    }

    #[test]
    fn the_fan_is_centred_on_the_aim() {
        let d = fan_dirs((10.0, 0.0), 5, 12);
        assert_eq!(d.len(), 5);
        assert!((d[2].0 - 1.0).abs() < 1e-9 && d[2].1.abs() < 1e-9, "{d:?}");
        // mirrored either side, 24 degrees out at the edges
        assert!((d[0].1 + d[4].1).abs() < 1e-9 && (d[0].0 - d[4].0).abs() < 1e-9);
        assert!((d[4].1.atan2(d[4].0).to_degrees() - 24.0).abs() < 1e-9);
        // an even count has no middle feather
        let e = fan_dirs((0.0, 5.0), 4, 10);
        assert!((e[1].0.atan2(e[1].1).to_degrees().abs() - 5.0).abs() < 1e-9, "{e:?}");
    }

    #[test]
    fn a_target_gone_in_the_wind_up_still_gets_the_fan() {
        // 11-04's logs: FAN "no aim (input kind 1)" one Q in ten - the minion died in the 11-tick wind-up
        let from = (100_000.0, 100_000.0);
        let foes = [(5, (160_000.0, 100_000.0)), (6, (100_000.0, 130_000.0)), (7, (300_000.0, 100_000.0))];
        // its last place first
        assert_eq!(aim_fallback(from, Some((120_000.0, 90_000.0)), &foes, 70_000.0),
                   Some(((120_000.0, 90_000.0), Fallback::LastPlace)));
        // none recorded (or it stood on her): the nearest in reach
        assert_eq!(aim_fallback(from, None, &foes, 70_000.0), Some(((100_000.0, 130_000.0), Fallback::Nearest(6))));
        assert_eq!(aim_fallback(from, Some(from), &foes, 70_000.0), Some(((100_000.0, 130_000.0), Fallback::Nearest(6))));
        // nobody within reach: nothing
        assert_eq!(aim_fallback(from, None, &foes[2..], 70_000.0), None);
        assert_eq!(aim_fallback(from, None, &[], 70_000.0), None);
    }

    #[test]
    fn each_simulation_keeps_its_own_places() {
        // 11-06's logs: 25 of 95 fans "no aim (input kind 1)" - one table for every simulation, keyed by the raptor's
        // id alone (#21 / #26 in nearly every match) and purged by each simulation's own clock
        let mut all: HashMap<Key, Seen> = HashMap::new();
        let (a, b) = ((7, 21), (8, 21));
        remember(&mut all, a, 10_000, &[(84, (782_436, 863_235))]);
        // another match's raptor #21, 20000 ticks further on, looks round: a's row stays
        remember(&mut all, b, 30_000, &[(90, (100_000, 100_000))]);
        assert_eq!(last_place(&all, a, 84), Some((782_436, 863_235)));
        assert_eq!(last_place(&all, b, 90), Some((100_000, 100_000)));
        assert_eq!(last_place(&all, b, 84), None, "a's target is not in b's row");
        // the old way (one row for both): b's clock purges a's place at once
        let mut one: HashMap<Key, Seen> = HashMap::new();
        remember(&mut one, (0, 21), 10_000, &[(84, (782_436, 863_235))]);
        remember(&mut one, (0, 21), 30_000, &[]);
        assert_eq!(last_place(&one, (0, 21), 84), None);
        // a's own clock still drops a place older than SEEN_FOR
        remember(&mut all, a, 10_000 + SEEN_FOR - 1, &[]);
        assert!(last_place(&all, a, 84).is_some());
        remember(&mut all, a, 10_000 + SEEN_FOR, &[]);
        assert_eq!(last_place(&all, a, 84), None);
        assert!(last_place(&all, b, 90).is_some(), "b's row untouched by a's purge");
        // a new life of the raptor numbered 8 (a new entity): her old rows go, a's stay
        remember(&mut all, a, 20_000, &[(85, (5, 5))]);
        forget_lives(&mut all, 8);
        assert_eq!(last_place(&all, b, 90), None);
        assert_eq!(last_place(&all, a, 85), Some((5, 5)));
        // the tag fits a buff name
        assert_eq!(TAG.parse(&TAG.name(42)), Some(42));
        assert!(TAG.name(u64::MAX).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn a_new_row_never_clears_the_others() {
        // a clear past 4096 rows took the rows of the simulations running beside it too (they lost their places at
        // another tick than their twins)
        let mut all: HashMap<Key, Seen> = HashMap::new();
        for no in 1..=5_000u64 {
            remember(&mut all, (no, 21), 5, &[(84, (1, 1))]);
        }
        remember(&mut all, (5_001, 21), 5, &[(84, (1, 1))]);
        assert_eq!(all.len(), 5_001);
        assert_eq!(last_place(&all, (1, 21), 84), Some((1, 1)));
    }

    #[test]
    fn the_feathers_fly_to_points_on_the_map_they_are_shot_on() {
        // the game's own map: held at its edge, as before
        assert_eq!(upos(Map::Native, (970_000.4, -3.0)), (MAP as u64 - 1, 0));
        // the Rift: past 960000 is its ground, its own edge at 1614545
        assert_eq!(upos(Map::Rift, (1_300_000.4, 1_500_000.0)), (1_300_000, 1_500_000));
        assert_eq!(upos(Map::Rift, (2_000_000.0, 5.0)), (Map::Rift.extent() as u64 - 1, 5));
    }

    #[test]
    fn the_shred_is_negative_armour() {
        let b = shred_buff(&Params::default());
        assert_eq!(b.name(), "tft_raptor_p_shred");
        assert_eq!(b.defence, -6);
        assert_eq!(b.duration_tick, 180);
    }
}
