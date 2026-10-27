//! 麦迪（`tft_maddie`）数据做不到的部分（金铲铲第 13 赛季的执法官 / 狙神，技能和被动按用户选的方案 A「狙神·通缉」，
//! 2026-10-27）。她的数据（tools/kit/build_maddie.py）的 `passive` 是这里的 `tft_maddie:sniper`，参数从数据的
//! `passive.params` 来（build_maddie.py 从参数表 P 写进去，`NATIVE_KEYS`），按她的单位编号记一份给效果用：
//!
//! - **狙神**：她打出的每一下（普攻、子弹、狙击，`on_attack`）离她越远伤害越高：`p_far` 以内均匀涨到 +`p_max`%。
//! - **连拨击锤**（`tft_maddie:fan`：技能出手）：找 `q_range` 以内**最远**的敌人（先英雄），连开 `q_n` 枪、每 `q_gap` 拍一枪
//!   （`tft_maddie:shot`，目标记在输入里，死了就重新找最远的）；子弹沿直线飞，打中路上的第一个敌人
//!   （`tft_maddie:bullet`）：`q_dmg` + 攻击力 `q_ratio`% 物理伤害。
//! - **通缉令**（`tft_maddie:wanted`：技能2 出手）：`e_range` 以内当前生命最高的敌方英雄被通缉 `e_t` 拍
//!   （`tft_maddie_e_wanted`，受到的伤害 +`e_amp`%）；它在通缉中死掉，她领一份赏金：攻速 +`w_as`%，最多 `w_max` 份
//!   （`tft_maddie_p_bounty`），她死了就清零。
//! - **执法狙杀**（`tft_maddie:snipe`：大招瞄准完）：一发穿透的子弹射向 `r_range` 以内生命比例最低的敌方英雄，直线上的
//!   每个敌人（`tft_maddie:round`）受到 `r_dmg` + 攻击力 `r_ratio`% 物理伤害，按它损失的生命比例再加最多 `r_exec`%。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_maddie.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_maddie";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const SHOT_FX: &str = "tft_maddie:shot";
const BULLET_FX: &str = "tft_maddie:bullet";
const ROUND_FX: &str = "tft_maddie:round";
/// The sounds tft.dll plays itself (the tft pack's sound_info; the rest the data plays).
const SFX_SHOT: &str = "tft_maddie_q";
const SFX_BULLET_HIT: &str = "tft_maddie_q_hit";
const SFX_WANTED: &str = "tft_maddie_e";
const SFX_ROUND_HIT: &str = "tft_maddie_r_hit";
/// A bullet flies on past its target by this much (it may miss a target that moved: the line goes on).
const OVERSHOOT: u64 = 20_000;

fn md(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_MADDIE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_maddie.log");
        }
    }
    PathBuf::from("tft_maddie.log")
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
    /// 狙神：p_far 以内离得越远加得越多，最多 +p_max%。
    pub p_max: usize,
    pub p_far: u64,
    /// 子弹从她的枪口出去：起点比她的站位点高 q_lift（半蹲开枪的枪口），飞向目标那条线。
    pub q_lift: u64,
    /// 连拨击锤：找人的距离、几枪、隔几拍一枪、每枪 q_dmg + q_ratio% 攻击力、子弹的速度和宽度。
    pub q_range: u64,
    pub q_n: usize,
    pub q_gap: usize,
    pub q_dmg: usize,
    pub q_ratio: usize,
    pub q_speed: u64,
    pub q_width: u64,
    /// 通缉令：找人的距离、几拍、受到的伤害 +%；赏金每份攻速 +%、最多几份。
    pub e_range: u64,
    pub e_t: usize,
    pub e_amp: usize,
    pub w_as: i32,
    pub w_max: usize,
    /// 执法狙杀：找人的距离、r_dmg + r_ratio% 攻击力、按损失生命最多再加 r_exec%、子弹的速度和宽度。
    pub r_range: u64,
    pub r_dmg: usize,
    pub r_ratio: usize,
    pub r_exec: usize,
    pub r_speed: u64,
    pub r_width: u64,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_max: 25,
            p_far: 100000,
            q_lift: 14000,
            q_range: 80000,
            q_n: 6,
            q_gap: 8,
            q_dmg: 10,
            q_ratio: 40,
            q_speed: 9000,
            q_width: 4000,
            e_range: 90000,
            e_t: 480,
            e_amp: 15,
            w_as: 15,
            w_max: 4,
            r_range: 200000,
            r_dmg: 220,
            r_ratio: 140,
            r_exec: 60,
            r_speed: 16000,
            r_width: 6000,
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
            "p_max" => p.p_max = u,
            "p_far" => p.p_far = (u as u64).max(1),
            "q_lift" => p.q_lift = u as u64,
            "q_range" => p.q_range = u as u64,
            "q_n" => p.q_n = u,
            "q_gap" => p.q_gap = u.max(1),
            "q_dmg" => p.q_dmg = u,
            "q_ratio" => p.q_ratio = u,
            "q_speed" => p.q_speed = (u as u64).max(1),
            "q_width" => p.q_width = u as u64,
            "e_range" => p.e_range = u as u64,
            "e_t" => p.e_t = u,
            "e_amp" => p.e_amp = u,
            "w_as" => p.w_as = v as i32,
            "w_max" => p.w_max = u,
            "r_range" => p.r_range = u as u64,
            "r_dmg" => p.r_dmg = u,
            "r_ratio" => p.r_ratio = u,
            "r_exec" => p.r_exec = u,
            "r_speed" => p.r_speed = (u as u64).max(1),
            "r_width" => p.r_width = u as u64,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// Her Wanted enemy: Maddie's id -> (the enemy, the tick the mark ends).
static WANTED: LazyLock<Mutex<HashMap<usize, (usize, usize)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

// ===================== 规则（单元测试用） =====================

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

fn isqrt(x: u128) -> u64 {
    if x == 0 {
        return 0;
    }
    let mut r = (x as f64).sqrt() as u128;
    while r * r > x {
        r -= 1;
    }
    while (r + 1) * (r + 1) <= x {
        r += 1;
    }
    r as u64
}

/// The Sniper bonus in percent for a unit `dist` away: rising evenly to p_max at p_far.
pub fn sniper_bonus(p: &Params, dist: u64) -> usize {
    (p.p_max as u64 * dist.min(p.p_far) / p.p_far) as usize
}

/// base + ratio% of the attack.
pub fn physical(base: usize, ratio: usize, atk: usize) -> usize {
    base + atk * ratio / 100
}

/// The snipe's damage on a unit at `hp` of `max`: raised by r_exec% of the share of health it is missing.
pub fn snipe_damage(p: &Params, atk: usize, hp: usize, max: usize) -> usize {
    let base = physical(p.r_dmg, p.r_ratio, atk);
    let missing = if max == 0 { 0 } else { max.saturating_sub(hp.min(max)) * 100 / max };
    base * (100 + p.r_exec * missing / 100) / 100
}

/// A unit she may shoot at: (id, where, a champion, health, max health).
pub type Foe = (usize, (u64, u64), bool, usize, usize);

/// Fan the Hammer's target: the farthest enemy within `reach` of `at`, champions first (a tie: the lower id).
pub fn farthest(foes: &[Foe], at: (u64, u64), reach: u64) -> Option<usize> {
    let r2 = (reach as u128) * (reach as u128);
    foes.iter()
        .filter(|f| dist_sq(f.1, at) <= r2)
        .max_by_key(|f| (f.2, dist_sq(f.1, at), std::cmp::Reverse(f.0)))
        .map(|f| f.0)
}

/// Wanted: the enemy champion with the most health within `reach` (a tie: the lower id).
pub fn most_health(foes: &[Foe], at: (u64, u64), reach: u64) -> Option<usize> {
    let r2 = (reach as u128) * (reach as u128);
    foes.iter()
        .filter(|f| f.2 && dist_sq(f.1, at) <= r2)
        .max_by_key(|f| (f.3, std::cmp::Reverse(f.0)))
        .map(|f| f.0)
}

/// The snipe's target: the enemy champion with the lowest share of health within `reach` (a tie: the nearer, then the
/// lower id).
pub fn weakest(foes: &[Foe], at: (u64, u64), reach: u64) -> Option<usize> {
    let r2 = (reach as u128) * (reach as u128);
    foes.iter()
        .filter(|f| f.2 && f.4 > 0 && dist_sq(f.1, at) <= r2)
        .min_by_key(|f| (f.3 * 10_000 / f.4, dist_sq(f.1, at), f.0))
        .map(|f| f.0)
}

/// The end of a line from `from` through `to`, `len` long (straight ahead when the two are one point).
pub fn line_end(from: (u64, u64), to: (u64, u64), len: u64) -> (u64, u64) {
    let (dx, dy) = (to.0 as f64 - from.0 as f64, to.1 as f64 - from.1 as f64);
    let d = (dx * dx + dy * dy).sqrt();
    let (ux, uy) = if d < 1.0 { (1.0, 0.0) } else { (dx / d, dy / d) };
    let x = (from.0 as f64 + ux * len as f64).max(0.0);
    let y = (from.1 as f64 + uy * len as f64).max(0.0);
    (x as u64, y as u64)
}

// ===================== 模拟里的小工具 =====================

fn atk_of(sim: &StableSim<'_>, me: usize) -> usize {
    sim.get_entity(me).map_or(0, |e| e.stat().attack)
}

/// Her enemies she can shoot at: alive, targetable, not a tower or a nexus.
fn foes(sim: &StableSim<'_>, me: usize) -> Vec<Foe> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| {
            let (hp, max) = u.hp();
            (u.id(), u.pos(), u.is_champion(), hp, max)
        })
        .collect()
}

fn unit(input: &InputTargetV1) -> Option<usize> {
    (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
}

fn shootable(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive() && e.is_targetable())
}

/// A named buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

/// A bullet from her muzzle (`lift` over her pivot, as the engine lifts a TargetProjectile) to the end of the line from
/// her pivot through `to`, running `effect` on what it hits: the line still meets the target at its own height.
fn fire(sim: &mut StableSim<'_>, me: usize, to: (u64, u64), picture: &str, effect: &str, width: u64, speed: u64,
        reach: u64, penetrate: bool, lift: u64) -> bool {
    let Some((team, at)) = sim.get_entity(me).map(|e| (e.team(), e.pos())) else { return false };
    let len = isqrt(dist_sq(at, to)).saturating_add(OVERSHOOT).min(reach.saturating_add(OVERSHOOT));
    let end = line_end(at, to, len);
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team,
        x: at.0,
        y: at.1.saturating_sub(lift),
        radius: width,
        speed,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: end.0,
        target_y: end.1,
        penetrate,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::EnemyWithoutTower.code(),
    };
    sim.spawn_projectile(picture, effect, &spec)
}

// ===================== 连拨击锤 =====================

/// Fan the Hammer goes off: q_n shots at the farthest enemy, q_gap ticks apart.
struct Fan;
impl StableEffectType for Fan {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some(at) = sim.get_entity(me).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let Some(target) = farthest(&foes(sim, me), at, p.q_range) else { return };
        let on = InputTargetV1::target(target);
        let mut queued = 0;
        for k in 0..p.q_n {
            if sim.queue_effect(SHOT_FX, AttackTypeV1::Skill, me, &on, (k * p.q_gap).max(1)) {
                queued += 1;
            }
        }
        if let Some(k) = counted("fan") {
            let d = sim.get_entity(target).map_or(0, |e| isqrt(dist_sq(e.pos(), at)));
            wlog(format!("{} FAN #{k}: {queued} shots at {} ({d} away)", head(sim, me), name_of(sim, target)));
        }
    }
}

/// One shot of Fan the Hammer: a bullet along the line through the target (a new farthest one if it is gone).
struct Shot;
impl StableEffectType for Shot {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let target = unit(&input).filter(|&id| shootable(sim, id)).or_else(|| farthest(&foes(sim, me), at, p.q_range));
        let Some(to) = target.and_then(|id| sim.get_entity(id)).map(|e| e.pos()) else { return };
        let ok = fire(sim, me, to, &md("q_bullet"), BULLET_FX, p.q_width, p.q_speed, p.q_range, false, p.q_lift);
        sim.play_sfx(SFX_SHOT, me, &InputTargetV1::target(me));
        if !ok {
            if let Some(k) = counted("shot refused") {
                wlog(format!("{} SHOT #{k}: spawn_projectile refused", head(sim, me)));
            }
        }
    }
}

/// A Fan the Hammer bullet hit the first enemy in its way.
struct Bullet;
impl StableEffectType for Bullet {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input) else { return };
        let p = params_of(me);
        let dmg = physical(p.q_dmg, p.q_ratio, atk_of(sim, me));
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
        let on = InputTargetV1::target(id);
        sim.play_view_effect(&md("q_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_BULLET_HIT, me, &on);
        if let Some(k) = counted("bullet") {
            wlog(format!("{} BULLET #{k}: {} takes {dmg} (before Sniper)", head(sim, me), name_of(sim, id)));
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (physical(p.q_dmg, p.q_ratio, caster_stat.attack), 0)
    }
}

// ===================== 通缉令 =====================

/// Wanted: the enemy champion with the most health within e_range takes e_amp% more damage for e_t ticks.
struct Wanted;
impl StableEffectType for Wanted {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some(at) = sim.get_entity(me).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let Some(target) = most_health(&foes(sim, me), at, p.e_range) else { return };
        let mut mark = BuffV1::timed(&md("e_wanted"), p.e_t);
        mark.damaged_amplify = p.e_amp;
        put(sim, target, &mark);
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&md("e_mark"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_WANTED, me, &on);
        let until = sim.tick() + p.e_t;
        WANTED.lock().unwrap_or_else(|e| e.into_inner()).insert(me, (target, until));
        if let Some(k) = counted("wanted") {
            let hp = sim.get_entity(target).map_or(0, |e| e.hp().0);
            wlog(format!("{} WANTED #{k}: {} ({hp} health) until t={until}", head(sim, me), name_of(sim, target)));
        }
    }
}

// ===================== 执法狙杀 =====================

/// The aim is done: one piercing round along the line through the weakest enemy champion.
struct Snipe;
impl StableEffectType for Snipe {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        // the weakest; the AI's own target when nobody is in reach (it chose one in range)
        let target = weakest(&foes(sim, me), at, p.r_range).or_else(|| unit(&input).filter(|&id| shootable(sim, id)));
        let Some(to) = target.and_then(|id| sim.get_entity(id)).map(|e| e.pos()) else { return };
        let ok = fire(sim, me, to, &md("r_round"), ROUND_FX, p.r_width, p.r_speed, p.r_range, true, p.q_lift);
        if let Some(k) = counted("snipe") {
            let id = target.unwrap_or(0);
            let (hp, max) = sim.get_entity(id).map_or((0, 0), |e| e.hp());
            wlog(format!("{} SNIPE #{k}: at {} ({hp}/{max}){}", head(sim, me), name_of(sim, id),
                         if ok { "" } else { " - spawn_projectile refused" }));
        }
    }
}

/// The round passed an enemy.
struct Round;
impl StableEffectType for Round {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input) else { return };
        let Some((hp, max)) = sim.get_entity(id).map(|e| e.hp()) else { return };
        let dmg = snipe_damage(&params_of(me), atk_of(sim, me), hp, max);
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
        let on = InputTargetV1::target(id);
        sim.play_view_effect(&md("r_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_ROUND_HIT, me, &on);
        if let Some(k) = counted("round") {
            wlog(format!("{} ROUND #{k}: {} ({hp}/{max}) takes {dmg} (before Sniper)", head(sim, me), name_of(sim, id)));
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (physical(p.r_dmg, p.r_ratio, caster_stat.attack), 0)
    }
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Sniper {
    p: Params,
    /// Bounties of this life.
    bounties: usize,
}

impl Sniper {
    fn bounty(&mut self, sim: &mut StableSim<'_>, me: usize, victim: usize) {
        if self.bounties < self.p.w_max {
            self.bounties += 1;
        }
        let mut b = BuffV1::named(&md("p_bounty"));
        b.attack_speed_mult = self.p.w_as * self.bounties as i32;
        put(sim, me, &b);
        sim.play_view_effect(&md("p_bounty"), me, &InputTargetV1::target(me), 0, 0, 0);
        if let Some(k) = counted("bounty") {
            wlog(format!("{} BOUNTY #{k}: {} died Wanted -> {} bounties, +{}% attack speed", head(sim, me),
                         name_of(sim, victim), self.bounties, b.attack_speed_mult));
        }
    }
}

impl StablePassive for Sniper {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Maddie (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        if *damage == 0 {
            return;
        }
        let (Some(a), Some(b)) = (sim.get_entity(me).map(|e| e.pos()), sim.get_entity(target).map(|e| e.pos())) else {
            return;
        };
        let d = isqrt(dist_sq(a, b));
        let bonus = sniper_bonus(&self.p, d);
        if bonus == 0 {
            return;
        }
        let before = *damage;
        *damage = before * (100 + bonus) / 100;
        if let Some(k) = counted("sniper") {
            wlog(format!("{} SNIPER #{k}: {} {d} away, {before} -> {} (+{bonus}%)", head(sim, me), name_of(sim, target),
                         *damage));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        let mark = WANTED.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied();
        let Some((victim, until)) = mark else { return };
        let tick = sim.tick();
        let dead = sim.get_entity(victim).is_none_or(|e| !e.is_alive());
        if dead && tick <= until + 1 {
            WANTED.lock().unwrap_or_else(|e| e.into_inner()).remove(&me);
            if sim.get_entity(me).is_some_and(|e| e.is_alive()) {
                self.bounty(sim, me, victim);
            }
        } else if tick > until {
            WANTED.lock().unwrap_or_else(|e| e.into_inner()).remove(&me);
        }
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        self.bounties = 0;
    }
}

// ===================== 注册 =====================

/// Maddie's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Maddie: Sniper by distance, Fan the Hammer at the farthest, Wanted bounties, the snipe at the weakest) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:sniper"), Sniper::default());
    module.add_native_effect(format!("{ID}:fan"), Fan);
    module.add_native_effect(format!("{ID}:shot"), Shot);
    module.add_native_effect(format!("{ID}:bullet"), Bullet);
    module.add_native_effect(format!("{ID}:wanted"), Wanted);
    module.add_native_effect(format!("{ID}:snipe"), Snipe);
    module.add_native_effect(format!("{ID}:round"), Round);
    host.log(LogLevel::Info, "tft.dll: Maddie (Sniper, Fan the Hammer, Wanted, Enforcer's Snipe).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"e_amp":15,"e_range":90000,"e_t":480,"p_far":100000,"p_max":25,"q_lift":14000,"q_dmg":10,"q_gap":8,"q_n":6,"q_range":80000,"q_ratio":40,"q_speed":9000,"q_width":4000,"r_dmg":220,"r_exec":60,"r_range":200000,"r_ratio":140,"r_speed":16000,"r_width":6000,"w_as":15,"w_max":4}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn farther_hits_harder() {
        let p = Params::default();
        assert_eq!(sniper_bonus(&p, 0), 0);
        assert_eq!(sniper_bonus(&p, 50_000), 12);
        assert_eq!(sniper_bonus(&p, 100_000), 25);
        assert_eq!(sniper_bonus(&p, 900_000), 25);
    }

    #[test]
    fn fan_picks_the_farthest_champion_first() {
        let foes = [(1, (900, 0), false, 100, 100), (2, (500, 0), true, 100, 100), (3, (700, 0), true, 100, 100)];
        assert_eq!(farthest(&foes, (0, 0), 1000), Some(3));
        assert_eq!(farthest(&foes, (0, 0), 600), Some(2));
        assert_eq!(farthest(&foes[..1], (0, 0), 1000), Some(1));
        assert_eq!(farthest(&foes, (0, 0), 100), None);
    }

    #[test]
    fn wanted_is_the_most_health_and_the_snipe_the_weakest_share() {
        let foes = [(1, (100, 0), true, 900, 1000), (2, (200, 0), true, 500, 2000), (3, (50, 0), false, 9000, 9000)];
        assert_eq!(most_health(&foes, (0, 0), 1000), Some(1));
        assert_eq!(weakest(&foes, (0, 0), 1000), Some(2));
        assert_eq!(weakest(&foes, (0, 0), 150), Some(1));
    }

    #[test]
    fn the_snipe_grows_with_missing_health() {
        let p = Params::default();
        assert_eq!(snipe_damage(&p, 100, 1000, 1000), 360);
        assert_eq!(snipe_damage(&p, 100, 500, 1000), 360 * 130 / 100);
        assert_eq!(snipe_damage(&p, 100, 0, 1000), 360 * 160 / 100);
    }

    #[test]
    fn a_line_goes_through_its_target() {
        assert_eq!(line_end((0, 0), (100, 0), 300), (300, 0));
        assert_eq!(line_end((1000, 1000), (1000, 1000), 50), (1050, 1000));
        let (x, y) = line_end((0, 0), (300, 400), 1000);
        assert!((599..=600).contains(&x) && (799..=800).contains(&y));
    }

    #[test]
    fn names_are_hers() {
        for n in [SFX_SHOT, SFX_BULLET_HIT, SFX_WANTED, SFX_ROUND_HIT] {
            assert!(n.starts_with("tft_maddie_"), "{n}");
        }
        for n in [SHOT_FX, BULLET_FX, ROUND_FX] {
            assert!(n.starts_with("tft_maddie:"), "{n}");
        }
        assert_eq!(md("q_hit"), "tft_maddie_q_hit");
    }
}
