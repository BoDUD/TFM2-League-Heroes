//! 索姆（`tft_sohm`）数据做不到的部分（金铲铲第 7 赛季的碧波龙 / 法师 / 龙神，技能「潮涌」；技能按用户选的方案 A
//! 「潮汐之花」，2026-10-30）。她的数据（tools/kit/build_sohm.py）的 `passive` 是这里的 `tft_sohm:lagoon`，参数从数据的
//! `passive.params` 来（build_sohm.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **碧波之力**：她的 Q、E、R 施放时各调一次 `tft_sohm:tide`：叠一层 `tft_sohm_p_tide`（法强 +`p_ap`%、攻速 +`p_as`%，
//!   `p_t` tick，最多 `p_max` 层，每叠一层所有层重新计时），挂 `tft_sohm_p_glow`（身上的潮水），播 `tft_sohm_p`。
//!   数据里的同名增益每加一次就多一层、没有上限，也不会一起重新计时，所以由这里叠。
//! - **潮涌**（金铲铲原技能）：`tft_sohm:wave` 挑一个**还没被她标记**的敌人：施法距离 `q_range` 以内最近的敌方英雄，
//!   没有就用这次施法的目标。从她身上朝那里冲出一道直线水浪（`tft_sohm_q_wave`，穿过所有人，`q_w` 宽），途经的每个
//!   敌人（`tft_sohm:wave_hit`）受到 `q_dmg` + `q_ratio`% 法强的魔法伤害；水浪到达目标时目标头上开出一朵水之花
//!   （`tft_sohm_q_flower`，`m_t` tick）。数据读不到谁身上有她的花，所以由这里挑。
//! - **花会跳**：带花的敌人倒下时，花飞向（`tft_sohm_q_jump`）它 `j_r` 以内最近的、没有花的敌人（英雄优先）。
//! - **海潮护佑**：`tft_sohm:guard` 给她 `e_ar` 以内生命比例最低的己方英雄（可以是她自己）一层 `e_sh` + `e_sh_ap`%
//!   法强的水盾（`e_sh_t` tick）和 `e_as`% 攻速（`tft_sohm_e_shield`，同样久）。游戏的 AI 选队友时不看血量
//!   （champion-data 第 3 节），所以由这里挑。
//! - **潮汐绽放**：`tft_sohm:bloom` 在她每朵花的位置炸开 `r_r` 半径的水花，范围里的敌人（同一次只算一遍）受到 `r_dmg` +
//!   `r_ratio`% 法强的魔法伤害，花都谢掉。一朵花都没有时，在这次施法的目标身上炸。
//! - **死亡**：倒下时播 `tft_sohm_d`（数据没有死亡的时机）。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_sohm.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_sohm";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const WAVE_HIT_FX: &str = "tft_sohm:wave_hit";
const FLOWER_FX: &str = "tft_sohm:flower";
/// The wave runs this far past its target, so a target that steps aside a little is still met.
const OVERSHOOT: u64 = 8_000;
/// A flower on its way (a wave or a jump still flying) is not taken for a withered one before this many ticks.
const GRACE: usize = 90;
/// At most this many bloom sounds in one cast (every flower bursts at once).
const BLOOM_SFX: usize = 3;

fn sm(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_SOHM_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_sohm.log");
        }
    }
    PathBuf::from("tft_sohm.log")
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
    /// 碧波之力：每层法强 +p_ap%、攻速 +p_as%，p_t tick，最多 p_max 层。
    pub p_max: usize,
    pub p_t: usize,
    pub p_ap: usize,
    pub p_as: usize,
    /// 潮涌：找花的距离 q_range；水浪 q_dmg + q_ratio% 法强，宽 q_w，每 tick q_speed；花开 m_t tick。
    pub q_range: usize,
    pub q_dmg: usize,
    pub q_ratio: usize,
    pub q_w: usize,
    pub q_speed: usize,
    pub m_t: usize,
    /// 花跳到 j_r 以内的敌人身上，每 tick 飞 j_speed。
    pub j_r: usize,
    pub j_speed: usize,
    /// 海潮护佑：e_ar 以内生命比例最低的己方英雄，水盾 e_sh + e_sh_ap% 法强，e_sh_t tick，攻速 +e_as%。
    pub e_ar: usize,
    pub e_sh: usize,
    pub e_sh_ap: usize,
    pub e_sh_t: usize,
    pub e_as: usize,
    /// 潮汐绽放：每朵花 r_r 半径，r_dmg + r_ratio% 法强。
    pub r_r: usize,
    pub r_dmg: usize,
    pub r_ratio: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_max: 5,
            p_t: 360,
            p_ap: 9,
            p_as: 9,
            q_range: 62000,
            q_dmg: 95,
            q_ratio: 65,
            q_w: 9000,
            q_speed: 3500,
            m_t: 900,
            j_r: 40000,
            j_speed: 3000,
            e_ar: 55000,
            e_sh: 95,
            e_sh_ap: 65,
            e_sh_t: 180,
            e_as: 25,
            r_r: 32000,
            r_dmg: 180,
            r_ratio: 90,
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
            "p_max" => p.p_max = u.max(1),
            "p_t" => p.p_t = u.max(1),
            "p_ap" => p.p_ap = u,
            "p_as" => p.p_as = u,
            "q_range" => p.q_range = u,
            "q_dmg" => p.q_dmg = u,
            "q_ratio" => p.q_ratio = u,
            "q_w" => p.q_w = u.max(1),
            "q_speed" => p.q_speed = u.max(1),
            "m_t" => p.m_t = u.max(1),
            "j_r" => p.j_r = u,
            "j_speed" => p.j_speed = u.max(1),
            "e_ar" => p.e_ar = u,
            "e_sh" => p.e_sh = u,
            "e_sh_ap" => p.e_sh_ap = u,
            "e_sh_t" => p.e_sh_t = u.max(1),
            "e_as" => p.e_as = u,
            "r_r" => p.r_r = u,
            "r_dmg" => p.r_dmg = u,
            "r_ratio" => p.r_ratio = u,
            _ => {}
        }
    }
    p
}

/// A flower she has put on (or is sending to) a unit, from `since` on.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Mark {
    pub id: usize,
    pub since: usize,
}

/// Each Sohm's params, flowers and waves still on their way (target, the tick the wave gets there), by her entity id
/// (the effects run without the passive at hand).
static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static MARKS: LazyLock<Mutex<HashMap<usize, Vec<Mark>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static WAVES: LazyLock<Mutex<HashMap<usize, Vec<(usize, usize)>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

fn marks_of(me: usize) -> Vec<Mark> {
    MARKS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).cloned().unwrap_or_default()
}

fn set_marks(me: usize, marks: Vec<Mark>) {
    MARKS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, marks);
}

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

/// The point `len` from `from` along the line through `to`.
pub fn line_end(from: (u64, u64), to: (u64, u64), len: u64) -> (u64, u64) {
    let (dx, dy) = (to.0 as f64 - from.0 as f64, to.1 as f64 - from.1 as f64);
    let d = (dx * dx + dy * dy).sqrt();
    let (ux, uy) = if d < 1.0 { (1.0, 0.0) } else { (dx / d, dy / d) };
    let x = (from.0 as f64 + ux * len as f64).max(0.0);
    let y = (from.1 as f64 + uy * len as f64).max(0.0);
    (x as u64, y as u64)
}

/// An enemy unit as the rules see it: (id, position, is a champion).
pub type Foe = (usize, (u64, u64), bool);

/// Who Tideblossom flowers: the nearest enemy champion within `range` of her that has no flower of hers; else the
/// cast's own target (marked or not, a minion or a monster too); ids break ties.
pub fn wave_target(foes: &[Foe], at: (u64, u64), range: usize, marked: &[usize], cast: Option<usize>) -> Option<usize> {
    let reach = (range as u128) * (range as u128);
    foes.iter()
        .filter(|f| f.2 && !marked.contains(&f.0))
        .map(|f| (dist_sq(f.1, at), f.0))
        .filter(|&(d, _)| d <= reach)
        .min()
        .map(|t| t.1)
        .or(cast)
}

/// Where a dead unit's flower goes: the nearest enemy within `r` of where it fell that has no flower of hers,
/// champions first; ids break ties.
pub fn jump_target(foes: &[Foe], from: (u64, u64), r: usize, marked: &[usize]) -> Option<usize> {
    let reach = (r as u128) * (r as u128);
    foes.iter()
        .filter(|f| !marked.contains(&f.0))
        .map(|f| (!f.2, dist_sq(f.1, from), f.0))
        .filter(|&(_, d, _)| d <= reach)
        .min()
        .map(|t| t.2)
}

/// The enemies the bloom reaches: everyone within `r` of any of the flowers, each once, in id order.
pub fn bloom_victims(foes: &[Foe], centres: &[(u64, u64)], r: usize) -> Vec<usize> {
    let reach = (r as u128) * (r as u128);
    let mut hit: Vec<usize> =
        foes.iter().filter(|f| centres.iter().any(|&c| dist_sq(f.1, c) <= reach)).map(|f| f.0).collect();
    hit.sort_unstable();
    hit.dedup();
    hit
}

/// Who the water shield goes to: the allied champion within `r` of her (her too) with the lowest health share;
/// (id, position, hp, max); ids break ties.
pub fn guard_target(allies: &[(usize, (u64, u64), usize, usize)], at: (u64, u64), r: usize) -> Option<usize> {
    let reach = (r as u128) * (r as u128);
    allies
        .iter()
        .filter(|a| a.3 > 0 && a.2 > 0 && dist_sq(a.1, at) <= reach)
        // hp / max compared without division: a.2 * b.3 < b.2 * a.3
        .min_by(|a, b| ((a.2 as u128) * (b.3 as u128)).cmp(&((b.2 as u128) * (a.3 as u128))).then(a.0.cmp(&b.0)))
        .map(|a| a.0)
}

/// Magic damage of `base` + `ratio`% of her ability power.
pub fn scaled(base: usize, ratio: usize, ap: usize) -> usize {
    (base + ap * ratio / 100).max(1)
}

/// The ticks a wave at `speed` takes over `dist` (at least 1).
pub fn travel(dist: u64, speed: usize) -> usize {
    (dist as usize).div_ceil(speed.max(1)).max(1)
}

// ===================== 模拟里的小工具 =====================

/// Live, targetable enemy units (no towers, no nexus) of `me`.
fn foes(sim: &StableSim<'_>, me: usize) -> Vec<Foe> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| (u.id(), u.pos(), u.is_champion()))
        .collect()
}

/// Live allied champions of `me` (her too): (id, position, hp, max).
fn allies(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64), usize, usize)> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() == team && u.is_alive() && u.is_champion())
        .map(|u| {
            let (hp, max) = u.hp();
            (u.id(), u.pos(), hp, max)
        })
        .collect()
}

fn ap_of(sim: &StableSim<'_>, me: usize) -> usize {
    sim.get_entity(me).map_or(0, |e| e.stat().magic_power)
}

fn unit(input: &InputTargetV1) -> Option<usize> {
    (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
}

fn alive(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive())
}

/// A named buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

/// Her flower opens on `id` (or is renewed there).
fn flower(sim: &mut StableSim<'_>, me: usize, id: usize, why: &str) {
    if !alive(sim, id) {
        return;
    }
    let p = params_of(me);
    put(sim, id, &BuffV1::timed(&sm("q_flower"), p.m_t));
    sim.play_sfx(&sm("q_mark"), me, &InputTargetV1::target(id));
    let mut marks = marks_of(me);
    let now = sim.tick();
    match marks.iter_mut().find(|m| m.id == id) {
        Some(m) => m.since = now,
        None => marks.push(Mark { id, since: now }),
    }
    let n = marks.len();
    set_marks(me, marks);
    if let Some(k) = counted("flower") {
        wlog(format!("{} FLOWER #{k} ({why}): on {}, {n} flower(s)", head(sim, me), name_of(sim, id)));
    }
}

// ===================== 碧波之力 =====================

/// Called from her Q, E and R: one more tide stack, every stack timed afresh.
struct Tide;
impl StableEffectType for Tide {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let p = params_of(me);
        let mut b = BuffV1::timed(&sm("p_tide"), p.p_t);
        b.magic_power_mult = p.p_ap as i32;
        b.attack_speed_mult = p.p_as as i32;
        let n = sim.entity_stack_buff(me, &b, p.p_max, true);
        put(sim, me, &BuffV1::timed(&sm("p_glow"), p.p_t));
        sim.play_sfx(&sm("p"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("tide") {
            wlog(format!(
                "{} TIDE #{k}: {n} stack(s){}",
                head(sim, me),
                if n == 0 { " - entity_stack_buff refused" } else { "" }
            ));
        }
    }
}

// ===================== 潮涌 =====================

/// Tideblossom's wave: at an enemy without her flower, through everyone on the way.
struct Wave;
impl StableEffectType for Wave {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some((team, at)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.team(), e.pos())) else {
            return;
        };
        let p = params_of(me);
        let marked: Vec<usize> = marks_of(me).iter().map(|m| m.id).collect();
        let cast = unit(&input).filter(|&id| alive(sim, id));
        let Some(target) = wave_target(&foes(sim, me), at, p.q_range, &marked, cast) else { return };
        let Some(to) = sim.get_entity(target).map(|e| e.pos()) else { return };
        let dist = isqrt(dist_sq(at, to));
        let end = line_end(at, to, dist + OVERSHOOT);
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team,
            x: at.0,
            y: at.1,
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
        let ok = sim.spawn_projectile(&sm("q_wave"), WAVE_HIT_FX, &spec);
        // the flower opens when the wave gets there, whether or not the wave touched it (wave_hit opens it sooner)
        let due = sim.tick() + travel(dist, p.q_speed);
        WAVES.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_default().push((target, due));
        if let Some(k) = counted("wave") {
            wlog(format!(
                "{} WAVE #{k}: at {} ({dist} away, cast on {}){}",
                head(sim, me),
                name_of(sim, target),
                cast.map_or_else(|| "-".to_string(), |c| name_of(sim, c)),
                if ok { "" } else { " - spawn_projectile refused" }
            ));
        }
    }
}

/// The wave passes over an enemy.
struct WaveHit;
impl StableEffectType for WaveHit {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input) else { return };
        let p = params_of(me);
        let d = scaled(p.q_dmg, p.q_ratio, ap_of(sim, me));
        sim.deal_damage_typed(me, id, d, DamageTypeV1::Ap, AttackTypeV1::Skill);
        let on = InputTargetV1::target(id);
        sim.play_view_effect(&sm("q_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(&sm("q_hit"), me, &on);
        let due = {
            let mut waves = WAVES.lock().unwrap_or_else(|e| e.into_inner());
            let list = waves.entry(me).or_default();
            let found = list.iter().position(|w| w.0 == id);
            found.map(|i| list.remove(i))
        };
        if due.is_some() {
            flower(sim, me, id, "wave");
        }
        if let Some(k) = counted("wave hit") {
            wlog(format!("{} WAVE HIT #{k}: {} takes {d} magic", head(sim, me), name_of(sim, id)));
        }
    }
}

/// A jumping flower lands.
struct FlowerLand;
impl StableEffectType for FlowerLand {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input) else { return };
        sim.play_sfx(&sm("q_jump_hit"), me, &InputTargetV1::target(id));
        flower(sim, me, id, "jump");
    }
}

// ===================== 海潮护佑 =====================

/// Tidecaller's water shield on the weakest allied champion near her.
struct Guard;
impl StableEffectType for Guard {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let friends = allies(sim, me);
        let Some(id) = guard_target(&friends, at, p.e_ar) else { return };
        let amount = scaled(p.e_sh, p.e_sh_ap, ap_of(sim, me));
        let ok = sim.entity_add_shield(id, amount, p.e_sh_t);
        let mut b = BuffV1::timed(&sm("e_shield"), p.e_sh_t);
        b.attack_speed_mult = p.e_as as i32;
        put(sim, id, &b);
        sim.play_sfx(&sm("e_shield"), me, &InputTargetV1::target(id));
        if let Some(k) = counted("guard") {
            let (hp, max) = friends.iter().find(|a| a.0 == id).map_or((0, 0), |a| (a.2, a.3));
            wlog(format!(
                "{} GUARD #{k}: {} ({hp}/{max}) gets a {amount} shield{}",
                head(sim, me),
                name_of(sim, id),
                if ok { "" } else { " (entity_add_shield refused)" }
            ));
        }
    }
}

// ===================== 潮汐绽放 =====================

/// Every flower of hers bursts.
struct Bloom;
impl StableEffectType for Bloom {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let p = params_of(me);
        let marks: Vec<usize> = marks_of(me).iter().map(|m| m.id).filter(|&id| alive(sim, id)).collect();
        let fallback = marks.is_empty();
        let at: Vec<usize> = if fallback { unit(&input).filter(|&id| alive(sim, id)).into_iter().collect() } else { marks };
        let centres: Vec<(u64, u64)> = at.iter().filter_map(|&id| sim.get_entity(id).map(|e| e.pos())).collect();
        let victims = bloom_victims(&foes(sim, me), &centres, p.r_r);
        let d = scaled(p.r_dmg, p.r_ratio, ap_of(sim, me));
        for (k, &id) in at.iter().enumerate() {
            let on = InputTargetV1::target(id);
            sim.play_view_effect(&sm("r_bloom"), me, &on, 0, 0, 0);
            if k < BLOOM_SFX {
                sim.play_sfx(&sm("r_bloom"), me, &on);
            }
        }
        for &id in &victims {
            sim.deal_damage_typed(me, id, d, DamageTypeV1::Ap, AttackTypeV1::Skill);
            sim.play_view_effect(&sm("r_hit"), me, &InputTargetV1::target(id), 0, 0, 0);
        }
        if let Some(&first) = victims.first() {
            sim.play_sfx(&sm("r_hit"), me, &InputTargetV1::target(first));
        }
        for m in marks_of(me) {
            sim.entity_remove_buff(m.id, &sm("q_flower"));
        }
        set_marks(me, Vec::new());
        if let Some(k) = counted("bloom") {
            wlog(format!(
                "{} BLOOM #{k}: {} {} -> {} hit for {d} magic: {:?}",
                head(sim, me),
                at.len(),
                if fallback { "cast target (no flowers)" } else { "flower(s)" },
                victims.len(),
                victims.iter().map(|&t| name_of(sim, t)).collect::<Vec<_>>()
            ));
        }
    }
}

// ===================== 被动：碧波龙 =====================

#[derive(Clone, Default)]
struct Lagoon {
    /// The champion it belongs to (on_dead is given the player, not the unit).
    me: usize,
    p: Params,
}

impl Lagoon {
    /// Waves that got there without touching their target open its flower now.
    fn land_waves(&self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        let due: Vec<usize> = {
            let mut waves = WAVES.lock().unwrap_or_else(|e| e.into_inner());
            let Some(list) = waves.get_mut(&me) else { return };
            let due = list.iter().filter(|w| w.1 <= now).map(|w| w.0).collect();
            list.retain(|w| w.1 > now);
            due
        };
        for id in due {
            flower(sim, me, id, "wave arrived");
        }
    }

    /// A flower on a fallen unit jumps on; a withered one (its time out, or its unit back alive without it) goes.
    fn tend(&self, sim: &mut StableSim<'_>, me: usize) {
        let marks = marks_of(me);
        if marks.is_empty() {
            return;
        }
        let now = sim.tick();
        let mut keep = Vec::with_capacity(marks.len());
        let mut jumps = Vec::new();
        for m in &marks {
            match sim.get_entity(m.id) {
                Some(e) if e.is_alive() => {
                    let flower = sm("q_flower");
                    let has = (0..256).map_while(|i| e.buff_at(i)).any(|b| b.name() == flower);
                    if has || now < m.since + GRACE {
                        keep.push(*m);
                    }
                }
                Some(e) => jumps.push((m.id, e.pos())),
                None => {}
            }
        }
        if keep.len() == marks.len() {
            return;
        }
        set_marks(me, keep);
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        for (dead, from) in jumps {
            let marked: Vec<usize> = marks_of(me).iter().map(|m| m.id).collect();
            let Some(to) = jump_target(&foes(sim, me), from, self.p.j_r, &marked) else {
                if let Some(k) = counted("jump lost") {
                    wlog(format!("{} JUMP #{k}: {} fell, nobody within {}", head(sim, me), name_of(sim, dead), self.p.j_r));
                }
                continue;
            };
            // the flower is hers from now on (the jump's landing puts the picture on), so it is not sent twice
            let mut list = marks_of(me);
            list.push(Mark { id: to, since: now });
            set_marks(me, list);
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team,
                x: from.0,
                y: from.1,
                radius: 4000,
                speed: self.p.j_speed as u64,
                move_kind: ProjectileMoveKindV1::Target.code(),
                target_id: to,
                target_x: 0,
                target_y: 0,
                penetrate: false,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::EnemyWithoutTower.code(),
            };
            let ok = sim.spawn_projectile(&sm("q_jump"), FLOWER_FX, &spec);
            sim.play_sfx(&sm("q_jump"), me, &InputTargetV1::pos(from.0, from.1));
            if let Some(k) = counted("jump") {
                wlog(format!(
                    "{} JUMP #{k}: {} fell, the flower goes to {}{}",
                    head(sim, me),
                    name_of(sim, dead),
                    name_of(sim, to),
                    if ok { "" } else { " - spawn_projectile refused" }
                ));
            }
        }
    }
}

impl StablePassive for Lagoon {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        MARKS.lock().unwrap_or_else(|e| e.into_inner()).remove(&me);
        WAVES.lock().unwrap_or_else(|e| e.into_inner()).remove(&me);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Sohm (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        self.land_waves(sim, me);
        self.tend(sim, me);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        let me = self.me;
        // her flowers stay where they are (TFT's marks outlive her); her death cry (the data has no moment for it)
        sim.play_sfx(&sm("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// Sohm's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Sohm: tide stacks, Tideblossom's flowers, the water shield, the bloom) loaded: game {}.{}.{} \
         abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:lagoon"), Lagoon::default());
    module.add_native_effect(format!("{ID}:tide"), Tide);
    module.add_native_effect(format!("{ID}:wave"), Wave);
    module.add_native_effect(format!("{ID}:wave_hit"), WaveHit);
    module.add_native_effect(format!("{ID}:flower"), FlowerLand);
    module.add_native_effect(format!("{ID}:guard"), Guard);
    module.add_native_effect(format!("{ID}:bloom"), Bloom);
    host.log(LogLevel::Info, "tft.dll: Sohm (Lagoon tides, Tideblossom, Tidecaller's shield, the bloom).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"e_ar":55000,"e_as":25,"e_sh":95,"e_sh_ap":65,"e_sh_t":180,"j_r":40000,"j_speed":3000,"m_t":900,"p_ap":9,"p_as":9,"p_max":5,"p_t":360,"q_dmg":95,"q_range":62000,"q_ratio":65,"q_speed":3500,"q_w":9000,"r_dmg":180,"r_r":32000,"r_ratio":90}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_wave_seeks_a_champion_without_a_flower() {
        let foes = [(1, (10000, 0), false), (2, (30000, 0), true), (3, (20000, 0), true), (4, (90000, 0), true)];
        // the nearest champion without a flower, past a nearer minion
        assert_eq!(wave_target(&foes, (0, 0), 62000, &[], Some(1)), Some(3));
        assert_eq!(wave_target(&foes, (0, 0), 62000, &[3], Some(1)), Some(2));
        // every champion in reach flowered (4 is too far): the cast's own target
        assert_eq!(wave_target(&foes, (0, 0), 62000, &[2, 3], Some(1)), Some(1));
        assert_eq!(wave_target(&foes, (0, 0), 62000, &[2, 3], None), None);
    }

    #[test]
    fn a_fallen_flower_jumps_to_the_nearest_champion_first() {
        let foes = [(5, (5000, 0), false), (6, (30000, 0), true), (7, (20000, 0), true), (8, (60000, 0), true)];
        assert_eq!(jump_target(&foes, (0, 0), 40000, &[]), Some(7));
        assert_eq!(jump_target(&foes, (0, 0), 40000, &[7]), Some(6));
        // no champion left within reach: a minion
        assert_eq!(jump_target(&foes, (0, 0), 40000, &[6, 7]), Some(5));
        assert_eq!(jump_target(&foes[3..], (0, 0), 40000, &[]), None);
    }

    #[test]
    fn the_bloom_hits_each_enemy_once() {
        let foes = [(1, (0, 0), true), (2, (20000, 0), true), (3, (50000, 0), true), (4, (200000, 0), true)];
        // two flowers whose circles overlap on 2
        assert_eq!(bloom_victims(&foes, &[(0, 0), (40000, 0)], 32000), vec![1, 2, 3]);
        assert!(bloom_victims(&foes, &[], 32000).is_empty());
    }

    #[test]
    fn the_shield_goes_to_the_weakest_share_in_reach() {
        let allies = [(1, (0, 0), 900, 1000), (2, (10000, 0), 500, 2000), (3, (20000, 0), 100, 1000),
                      (4, (90000, 0), 1, 1000)];
        // 3 at 10% (4 at 0.1% is out of reach)
        assert_eq!(guard_target(&allies, (0, 0), 55000), Some(3));
        assert_eq!(guard_target(&allies[..2], (0, 0), 55000), Some(2));
        // alone: herself
        assert_eq!(guard_target(&allies[..1], (0, 0), 55000), Some(1));
    }

    #[test]
    fn numbers() {
        assert_eq!(scaled(95, 65, 200), 225);
        assert_eq!(scaled(0, 0, 0), 1);
        assert_eq!(travel(35000, 3500), 10);
        assert_eq!(travel(35001, 3500), 11);
        assert_eq!(travel(0, 3500), 1);
        assert_eq!(line_end((0, 0), (3, 4), 10), (6, 8));
    }
}
