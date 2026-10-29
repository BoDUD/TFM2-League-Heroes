//! 塞薇卡（`tft_sevika`）数据做不到的部分（金铲铲第 13 赛季的百变铁手 / 炼金男爵 / 搏击手，技能按用户选的方案 A
//! 「百变铁手」，2026-10-29）。她的数据（tools/kit/build_sevika.py）的 `passive` 是这里的 `tft_sevika:roll`，参数从数据的
//! `passive.params` 来（build_sevika.py 从参数表 P 写进去，`NATIVE_KEYS`），按她的单位编号记一份给效果用：
//!
//! - **百变铁手**（`tft_sevika:roll`：Q、E、R 施放时各调用一次）：用效果给的确定性种子摇老虎机（预演和观战一样）：
//!   `p_tri`% 中头奖（三倍：给她挂 `p_triple` `p_tri_t` 拍，这次技能强化），否则三个改件机会均等：火箭（`p_rk_n` 枚，
//!   每 `p_rk_gap` 拍一枚，各飞向 `p_rk_r` 以内随机一个敌人（先英雄），`p_rk_dmg` + 攻击 `p_rk_ad`%）、护盾（`p_sh` +
//!   攻击 `p_sh_ad`%，`p_sh_t` 拍）、微光（攻速 +`p_as`%，`p_as_t` 拍）。
//! - **伸缩拳**（`tft_sevika:punch`）：拳头沿她到目标的直线射出（`e_w` 宽、`e_speed`），打中的第一个敌人受 `e_dmg` +
//!   攻击 `e_ad`% 并被击退 `e_kb_speed` × `e_kb_t`；它落点 `e_behind` 以内另有敌人，那人受这一拳的 `e_dmg2`%，两人都
//!   眩晕 `e_stun` 拍；头奖时目标不撞人也眩晕，伤害 +`e_tri`%。
//! - **嚼一嚼**（`tft_sevika:chomp`：数据冲到目标后调用）：咬 `r_n` 口（头奖 `r_tri_n` 口），每 `r_gap` 拍一口，每口
//!   `r_dmg` + 攻击 `r_ad`%，第一口眩晕 `r_stun` 拍，每口给目标挂 `r_bleed` 拍的流血（被动每 10 拍结算，共攻击
//!   `r_bl_ad`%）；最后一口后目标生命低于 `r_exec`%（头奖 `r_exec_tri`%）直接咬死；目标死了就冲向她 `r_reset` 以内
//!   最近的敌方英雄再咬一轮（每次施法最多 `r_resets` 次，每次伤害乘 `r_fall`%）。
//!
//! 每次施法的状态都挂在她身上（`r_tri` 头奖、`r_hop` 已冲了几次），不存静态表（参数表除外：两个模拟里一样），预演和
//! 观战两个模拟同时跑也互不干扰。只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_sevika.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_sevika";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const ROCKET_FX: &str = "tft_sevika:rocket";
const ROCKET_HIT_FX: &str = "tft_sevika:rocket_hit";
const FIST_FX: &str = "tft_sevika:fist";
const BITE_FX: [&str; MAX_BITES] = ["tft_sevika:bite1", "tft_sevika:bite2", "tft_sevika:bite3", "tft_sevika:bite4",
                                    "tft_sevika:bite5", "tft_sevika:bite6"];
const MAX_BITES: usize = 6;
/// The sounds tft.dll plays itself (the tft pack's sound_info; the rest the data plays).
const SFX_ROCKET: &str = "tft_sevika_p_rocket";
const SFX_ROCKET_HIT: &str = "tft_sevika_p_rocket_hit";
const SFX_SHIELD: &str = "tft_sevika_p_shield";
const SFX_SHIMMER: &str = "tft_sevika_p_shimmer";
const SFX_JACKPOT: &str = "tft_sevika_p_jackpot";
const SFX_JACKPOT_FX: &str = "tft_sevika_p_jackpot_fx";
const SFX_LAUNCH: &str = "tft_sevika_e_launch";
const SFX_FIST: &str = "tft_sevika_e_hit";
const SFX_STUN: &str = "tft_sevika_e_stun";
const SFX_DASH: &str = "tft_sevika_r_dash";
const SFX_BITE: &str = "tft_sevika_r_hit";
const SFX_KILL: &str = "tft_sevika_r_kill";
/// The bleed lands in steps this many ticks apart (one number every tick would bury the health bar).
const STEP: usize = 10;
/// The rockets leave the slot machine on her shoulder, this far over her pivot; the fist leaves her arm.
const ROCKET_LIFT: u64 = 16000;
const FIST_LIFT: u64 = 8000;
/// A line projectile flies this far past its end point (it must reach a target standing on it).
const OVERSHOOT: u64 = 10000;
/// Where a re-dash puts her: this far short of the new target, on the line from her.
const HOP_GAP: u64 = 16000;
/// How long the cast's flags last (longer than any chomp with its re-dashes).
const CAST_T: usize = 360;

fn sv(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_SEVIKA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_sevika.log");
        }
    }
    PathBuf::from("tft_sevika.log")
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
    /// 百变铁手：头奖 p_tri%（p_triple 挂 p_tri_t 拍）；火箭、护盾、微光。
    pub p_tri: usize,
    pub p_tri_t: usize,
    pub p_rk_n: usize,
    pub p_rk_gap: usize,
    pub p_rk_r: usize,
    pub p_rk_dmg: usize,
    pub p_rk_ad: usize,
    pub p_rk_speed: usize,
    pub p_sh: usize,
    pub p_sh_ad: usize,
    pub p_sh_t: usize,
    pub p_as: usize,
    pub p_as_t: usize,
    /// 伸缩拳。
    pub e_range: usize,
    pub e_w: usize,
    pub e_speed: usize,
    pub e_dmg: usize,
    pub e_ad: usize,
    pub e_kb_speed: usize,
    pub e_kb_t: usize,
    pub e_behind: usize,
    pub e_stun: usize,
    pub e_dmg2: usize,
    pub e_tri: usize,
    /// 嚼一嚼。
    pub r_n: usize,
    pub r_tri_n: usize,
    pub r_gap: usize,
    pub r_dmg: usize,
    pub r_ad: usize,
    pub r_stun: usize,
    pub r_bleed: usize,
    pub r_bl_ad: usize,
    pub r_exec: usize,
    pub r_exec_tri: usize,
    pub r_reset: usize,
    pub r_resets: usize,
    pub r_fall: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_tri: 12,
            p_tri_t: 150,
            p_rk_n: 4,
            p_rk_gap: 6,
            p_rk_r: 60000,
            p_rk_dmg: 15,
            p_rk_ad: 30,
            p_rk_speed: 5000,
            p_sh: 60,
            p_sh_ad: 100,
            p_sh_t: 180,
            p_as: 35,
            p_as_t: 180,
            e_range: 55000,
            e_w: 8000,
            e_speed: 4000,
            e_dmg: 40,
            e_ad: 120,
            e_kb_speed: 2500,
            e_kb_t: 10,
            e_behind: 30000,
            e_stun: 72,
            e_dmg2: 50,
            e_tri: 50,
            r_n: 2,
            r_tri_n: 4,
            r_gap: 18,
            r_dmg: 60,
            r_ad: 135,
            r_stun: 66,
            r_bleed: 300,
            r_bl_ad: 60,
            r_exec: 15,
            r_exec_tri: 25,
            r_reset: 30000,
            r_resets: 2,
            r_fall: 80,
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
            "p_tri" => p.p_tri = u.min(100),
            "p_tri_t" => p.p_tri_t = u.max(1),
            "p_rk_n" => p.p_rk_n = u,
            "p_rk_gap" => p.p_rk_gap = u.max(1),
            "p_rk_r" => p.p_rk_r = u,
            "p_rk_dmg" => p.p_rk_dmg = u,
            "p_rk_ad" => p.p_rk_ad = u,
            "p_rk_speed" => p.p_rk_speed = u.max(1),
            "p_sh" => p.p_sh = u,
            "p_sh_ad" => p.p_sh_ad = u,
            "p_sh_t" => p.p_sh_t = u.max(1),
            "p_as" => p.p_as = u,
            "p_as_t" => p.p_as_t = u.max(1),
            "e_range" => p.e_range = u,
            "e_w" => p.e_w = u,
            "e_speed" => p.e_speed = u.max(1),
            "e_dmg" => p.e_dmg = u,
            "e_ad" => p.e_ad = u,
            "e_kb_speed" => p.e_kb_speed = u,
            "e_kb_t" => p.e_kb_t = u,
            "e_behind" => p.e_behind = u,
            "e_stun" => p.e_stun = u,
            "e_dmg2" => p.e_dmg2 = u,
            "e_tri" => p.e_tri = u,
            "r_n" => p.r_n = u.clamp(1, MAX_BITES),
            "r_tri_n" => p.r_tri_n = u.clamp(1, MAX_BITES),
            "r_gap" => p.r_gap = u.max(1),
            "r_dmg" => p.r_dmg = u,
            "r_ad" => p.r_ad = u,
            "r_stun" => p.r_stun = u,
            "r_bleed" => p.r_bleed = u.max(1),
            "r_bl_ad" => p.r_bl_ad = u,
            "r_exec" => p.r_exec = u.min(100),
            "r_exec_tri" => p.r_exec_tri = u.min(100),
            "r_reset" => p.r_reset = u,
            "r_resets" => p.r_resets = u,
            "r_fall" => p.r_fall = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

// ===================== 规则（单元测试用） =====================

/// One of Jinx's mods out of the slot machine.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Mod {
    Rockets,
    Shield,
    Shimmer,
    Triple,
}

/// A number from the effect's seed (splitmix64: the same seed, the same number, in both simulations).
pub fn mix(seed: u64) -> u64 {
    let mut z = seed.wrapping_add(0x9E37_79B9_7F4A_7C15);
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

/// The slot machine: p_tri% the jackpot, else the three mods alike.
pub fn roll(p: &Params, seed: u64) -> Mod {
    let r = mix(seed);
    if (r % 100) < p.p_tri as u64 {
        return Mod::Triple;
    }
    match (r >> 16) % 3 {
        0 => Mod::Rockets,
        1 => Mod::Shield,
        _ => Mod::Shimmer,
    }
}

/// base + ratio% of the attack, then scaled by pct%.
pub fn physical(base: usize, ratio: usize, atk: usize, pct: usize) -> usize {
    (base + atk * ratio / 100) * pct / 100
}

/// The damage of each chomp bite after `hops` re-dashes (r_fall% each).
pub fn bite_pct(p: &Params, hops: usize) -> usize {
    (0..hops).fold(100, |acc, _| acc * p.r_fall / 100)
}

/// The bleed of one step: r_bl_ad% of the attack spread over r_bleed ticks (at least 1 a step).
pub fn bleed_step(p: &Params, atk: usize) -> usize {
    (atk * p.r_bl_ad / 100 * STEP / p.r_bleed).max(1)
}

/// Whether a target at hp of max is executed (under `line`%).
pub fn executed(hp: usize, max: usize, line: usize) -> bool {
    max > 0 && hp > 0 && hp * 100 < max * line
}

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// The point `len` from `from` toward `to` (straight ahead when the two are one point); `len` may be negative.
pub fn toward(from: (u64, u64), to: (u64, u64), len: i64) -> (u64, u64) {
    let (dx, dy) = (to.0 as f64 - from.0 as f64, to.1 as f64 - from.1 as f64);
    let d = (dx * dx + dy * dy).sqrt();
    let (ux, uy) = if d < 1.0 { (1.0, 0.0) } else { (dx / d, dy / d) };
    let x = (from.0 as f64 + ux * len as f64).max(0.0);
    let y = (from.1 as f64 + uy * len as f64).max(0.0);
    (x as u64, y as u64)
}

/// A unit she may hit: (id, where, a champion, health, max health).
pub type Foe = (usize, (u64, u64), bool, usize, usize);

/// A rocket's target: a random enemy within `reach` of `at`, champions first.
pub fn rocket_target(foes: &[Foe], at: (u64, u64), reach: usize, seed: u64) -> Option<usize> {
    let r2 = (reach as u128) * (reach as u128);
    let near: Vec<&Foe> = foes.iter().filter(|f| dist_sq(f.1, at) <= r2).collect();
    let champs: Vec<&&Foe> = near.iter().filter(|f| f.2).collect();
    let r = mix(seed) as usize;
    if !champs.is_empty() {
        return Some(champs[r % champs.len()].0);
    }
    (!near.is_empty()).then(|| near[r % near.len()].0)
}

/// The enemy nearest to `at` within `reach` other than `but` (`champs`: champions only; a tie: the lower id).
pub fn nearest(foes: &[Foe], at: (u64, u64), reach: usize, but: usize, champs: bool) -> Option<usize> {
    let r2 = (reach as u128) * (reach as u128);
    foes.iter()
        .filter(|f| f.0 != but && (!champs || f.2) && dist_sq(f.1, at) <= r2)
        .min_by_key(|f| (dist_sq(f.1, at), f.0))
        .map(|f| f.0)
}

// ===================== 模拟里的小工具 =====================

fn atk_of(sim: &StableSim<'_>, me: usize) -> usize {
    sim.get_entity(me).map_or(0, |e| e.stat().attack)
}

/// Her enemies: alive, targetable, not a tower or a nexus.
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

fn alive(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive())
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    let Some(e) = sim.get_entity(id) else { return false };
    (0..).map_while(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn count(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    let Some(e) = sim.get_entity(id) else { return 0 };
    (0..).map_while(|i| e.buff_at(i)).filter(|b| b.name() == name).count()
}

/// Takes a flag off and says whether it was on.
fn take(sim: &mut StableSim<'_>, id: usize, name: &str) -> bool {
    sim.entity_remove_buff(id, name) > 0
}

/// A named buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

fn show(sim: &mut StableSim<'_>, me: usize, on: usize, picture: &str, sound: &str) {
    let at = InputTargetV1::target(on);
    if !picture.is_empty() {
        sim.play_view_effect(picture, me, &at, 0, 0, 0);
    }
    if !sound.is_empty() {
        sim.play_sfx(sound, me, &at);
    }
}

fn hit(sim: &mut StableSim<'_>, me: usize, id: usize, amount: usize) {
    sim.deal_damage_typed(me, id, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
}

// ===================== 百变铁手：老虎机 =====================

struct Roll;
impl StableEffectType for Roll {
    fn apply(&self, sim: &mut StableSim<'_>, seed: u64, me: usize, _: InputTargetV1) {
        if !alive(sim, me) {
            return;
        }
        let p = params_of(me);
        sim.entity_remove_buff(me, &sv("p_triple"));   // an unspent jackpot from the last cast is gone
        let got = roll(&p, seed);
        let atk = atk_of(sim, me);
        match got {
            Mod::Triple => {
                put(sim, me, &BuffV1::timed(&sv("p_triple"), p.p_tri_t));
                show(sim, me, me, &sv("p_jackpot"), SFX_JACKPOT);
                sim.play_sfx(SFX_JACKPOT_FX, me, &InputTargetV1::target(me));
            }
            Mod::Rockets => {
                let on = InputTargetV1::target(me);
                for k in 0..p.p_rk_n {
                    sim.queue_effect(ROCKET_FX, AttackTypeV1::Skill, me, &on, (k * p.p_rk_gap).max(1));
                }
            }
            Mod::Shield => {
                sim.entity_add_shield(me, p.p_sh + atk * p.p_sh_ad / 100, p.p_sh_t);
                show(sim, me, me, &sv("p_shield"), SFX_SHIELD);
            }
            Mod::Shimmer => {
                let mut b = BuffV1::timed(&sv("p_shimmer"), p.p_as_t);
                b.attack_speed_mult = p.p_as as i32;
                put(sim, me, &b);
                sim.play_sfx(SFX_SHIMMER, me, &InputTargetV1::target(me));
            }
        }
        if let Some(k) = counted("roll") {
            wlog(format!("{} ROLL #{k}: {got:?}", head(sim, me)));
        }
    }
}

/// One rocket of the rockets mod: from her shoulder to a random enemy.
struct Rocket;
impl StableEffectType for Rocket {
    fn apply(&self, sim: &mut StableSim<'_>, seed: u64, me: usize, _: InputTargetV1) {
        let Some((team, at)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.team(), e.pos())) else {
            return;
        };
        let p = params_of(me);
        let Some(target) = rocket_target(&foes(sim, me), at, p.p_rk_r, seed) else { return };
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team,
            x: at.0,
            y: at.1.saturating_sub(ROCKET_LIFT),
            radius: 4000,
            speed: p.p_rk_speed as u64,
            move_kind: ProjectileMoveKindV1::Target.code(),
            target_id: target,
            target_x: 0,
            target_y: 0,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        let ok = sim.spawn_projectile(&sv("p_rocket"), ROCKET_HIT_FX, &spec);
        sim.play_sfx(SFX_ROCKET, me, &InputTargetV1::target(me));
        if let Some(k) = counted("rocket") {
            wlog(format!("{} ROCKET #{k}: at {}{}", head(sim, me), name_of(sim, target),
                         if ok { "" } else { " - spawn_projectile refused" }));
        }
    }
}

struct RocketHit;
impl StableEffectType for RocketHit {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input) else { return };
        let p = params_of(me);
        let dmg = physical(p.p_rk_dmg, p.p_rk_ad, atk_of(sim, me), 100);
        hit(sim, me, id, dmg);
        show(sim, me, id, &sv("p_rocket_hit"), SFX_ROCKET_HIT);
    }
}

// ===================== 伸缩拳 =====================

struct Punch;
impl StableEffectType for Punch {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some((team, at)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.team(), e.pos())) else {
            return;
        };
        let p = params_of(me);
        let target = unit(&input).filter(|&id| alive(sim, id))
            .or_else(|| nearest(&foes(sim, me), at, p.e_range, usize::MAX, false));
        let Some(to) = target.and_then(|id| sim.get_entity(id)).map(|e| e.pos()) else { return };
        // the jackpot rides with the fist (taken now: the next cast's roll clears p_triple)
        if take(sim, me, &sv("p_triple")) {
            put(sim, me, &BuffV1::timed(&sv("e_tri"), CAST_T));
        }
        let end = toward(at, to, (p.e_range as u64 + OVERSHOOT) as i64);
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team,
            x: at.0,
            y: at.1.saturating_sub(FIST_LIFT),
            radius: p.e_w as u64,
            speed: p.e_speed as u64,
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: end.0,
            target_y: end.1,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        let ok = sim.spawn_projectile(&sv("e_fist"), FIST_FX, &spec);
        sim.play_sfx(SFX_LAUNCH, me, &InputTargetV1::target(me));
        if !ok {
            if let Some(k) = counted("punch refused") {
                wlog(format!("{} PUNCH #{k}: spawn_projectile refused", head(sim, me)));
            }
        }
    }
}

struct Fist;
impl StableEffectType for Fist {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input) else { return };
        let (Some(at), Some(was)) = (sim.get_entity(me).map(|e| e.pos()), sim.get_entity(id).map(|e| e.pos())) else {
            return;
        };
        let p = params_of(me);
        let tri = take(sim, me, &sv("e_tri"));
        let dmg = physical(p.e_dmg, p.e_ad, atk_of(sim, me), if tri { 100 + p.e_tri } else { 100 });
        hit(sim, me, id, dmg);
        show(sim, me, id, &sv("e_hit"), SFX_FIST);
        sim.entity_knockback(me, id, p.e_kb_speed, p.e_kb_t);
        // where it lands: knocked straight away from her
        let d = (dist_sq(at, was) as f64).sqrt() as i64;
        let lands = toward(at, was, d + (p.e_kb_speed * p.e_kb_t) as i64);
        let behind = alive(sim, id).then(|| nearest(&foes(sim, me), lands, p.e_behind, id, false)).flatten();
        let stun = |sim: &mut StableSim<'_>, who: usize| {
            sim.apply_cc(who, &CcV1::stun(p.e_stun as u64));
            put(sim, who, &BuffV1::timed(&sv("e_stun"), p.e_stun));
        };
        if let Some(other) = behind {
            hit(sim, me, other, dmg * p.e_dmg2 / 100);
            stun(sim, id);
            stun(sim, other);
            show(sim, me, other, &sv("e_hit"), SFX_STUN);
        } else if tri {
            stun(sim, id);
        }
        if let Some(k) = counted("fist") {
            wlog(format!("{} FIST #{k}: {} takes {dmg}{}{}", head(sim, me), name_of(sim, id),
                         if tri { " (jackpot)" } else { "" },
                         behind.map_or(String::new(), |o| format!(", knocked into {}: both stunned", name_of(sim, o)))));
        }
    }
}

// ===================== 嚼一嚼 =====================

fn bites(sim: &StableSim<'_>, me: usize, p: &Params) -> usize {
    if has(sim, me, &sv("r_tri")) { p.r_tri_n } else { p.r_n }
}

/// A round of bites on `target` (the data's after the dash, or a re-dash's).
fn chomp_on(sim: &mut StableSim<'_>, me: usize, target: usize, p: &Params) {
    let on = InputTargetV1::target(target);
    for k in 0..bites(sim, me, p) {
        sim.queue_effect(BITE_FX[k], AttackTypeV1::Skill, me, &on, (k * p.r_gap).max(1));
    }
}

struct Chomp;
impl StableEffectType for Chomp {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        // a new cast: no re-dash yet, the jackpot read off the roll
        sim.entity_remove_buff(me, &sv("r_hop"));
        sim.entity_remove_buff(me, &sv("r_tri"));
        if take(sim, me, &sv("p_triple")) {
            put(sim, me, &BuffV1::timed(&sv("r_tri"), CAST_T));
        }
        let target = unit(&input).filter(|&id| alive(sim, id))
            .or_else(|| nearest(&foes(sim, me), at, p.r_reset, usize::MAX, true));
        let Some(target) = target else { return };
        chomp_on(sim, me, target, &p);
        if let Some(k) = counted("chomp") {
            wlog(format!("{} CHOMP #{k}: {} ({} bites)", head(sim, me), name_of(sim, target), bites(sim, me, &p)));
        }
    }
}

struct Bite(usize);
impl StableEffectType for Bite {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input).filter(|&id| alive(sim, id)) else { return };
        if !alive(sim, me) {
            return;
        }
        let p = params_of(me);
        let hops = count(sim, me, &sv("r_hop"));
        let tri = has(sim, me, &sv("r_tri"));
        let dmg = physical(p.r_dmg, p.r_ad, atk_of(sim, me), bite_pct(&p, hops));
        hit(sim, me, id, dmg);
        show(sim, me, id, &sv("r_hit"), SFX_BITE);
        put(sim, id, &BuffV1::timed(&sv("r_bleed"), p.r_bleed));
        if self.0 == 0 {
            sim.apply_cc(id, &CcV1::stun(p.r_stun as u64));
        }
        if self.0 + 1 < bites(sim, me, &p) {
            return;
        }
        // the last bite: the execute, then a re-dash on a kill
        let (hp, max) = sim.get_entity(id).map_or((0, 0), |e| e.hp());
        let line = if tri { p.r_exec_tri } else { p.r_exec };
        if executed(hp, max, line) {
            sim.deal_damage_typed(me, id, hp, DamageTypeV1::Fixed, AttackTypeV1::Skill);
            show(sim, me, id, &sv("r_kill"), SFX_KILL);
        }
        if alive(sim, id) || hops >= p.r_resets {
            return;
        }
        let Some(at) = sim.get_entity(me).map(|e| e.pos()) else { return };
        let Some(next) = nearest(&foes(sim, me), at, p.r_reset, id, true) else { return };
        let Some(to) = sim.get_entity(next).map(|e| e.pos()) else { return };
        let gap = (dist_sq(at, to) as f64).sqrt() as i64 - HOP_GAP as i64;
        let stand = toward(at, to, gap.max(0));
        sim.entity_set_pos(me, stand.0, stand.1);
        sim.add_buff(me, &BuffV1::timed(&sv("r_hop"), CAST_T));   // each re-dash its own stack
        sim.play_sfx(SFX_DASH, me, &InputTargetV1::target(me));
        chomp_on(sim, me, next, &p);
        if let Some(k) = counted("hop") {
            wlog(format!("{} HOP #{k}: {} down, on to {} at {}%", head(sim, me), name_of(sim, id), name_of(sim, next),
                         bite_pct(&p, hops + 1)));
        }
    }
}

// ===================== 被动：参数 + 流血 =====================

#[derive(Clone, Default)]
struct HighRoller {
    p: Params,
}

impl StablePassive for HighRoller {
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
            wlog(format!("{} SPAWN #{k}: tft.dll's Sevika (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        if sim.tick() % STEP != 0 {
            return;
        }
        // the chomp's bleed on every enemy still marked (her attack now)
        let name = sv("r_bleed");
        let bled: Vec<usize> = foes(sim, me).iter().map(|f| f.0).filter(|&id| has(sim, id, &name)).collect();
        if bled.is_empty() {
            return;
        }
        let step = bleed_step(&self.p, atk_of(sim, me));
        for id in bled {
            hit(sim, me, id, step);
        }
    }
}

// ===================== 注册 =====================

/// Sevika's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Sevika: the slot machine, Extendo-Punch, Chomp) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:roll"), HighRoller::default());
    module.add_native_effect(format!("{ID}:roll"), Roll);
    module.add_native_effect(format!("{ID}:rocket"), Rocket);
    module.add_native_effect(format!("{ID}:rocket_hit"), RocketHit);
    module.add_native_effect(format!("{ID}:punch"), Punch);
    module.add_native_effect(format!("{ID}:fist"), Fist);
    module.add_native_effect(format!("{ID}:chomp"), Chomp);
    for (k, name) in BITE_FX.iter().enumerate() {
        module.add_native_effect(name.to_string(), Bite(k));
    }
    host.log(LogLevel::Info, "tft.dll: Sevika (High Roller, Extendo-Punch, Chomp).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_tri":12,"p_tri_t":150,"p_rk_n":4,"p_rk_gap":6,"p_rk_r":60000,"p_rk_dmg":15,"p_rk_ad":30,
            "p_rk_speed":5000,"p_sh":60,"p_sh_ad":100,"p_sh_t":180,"p_as":35,"p_as_t":180,"e_range":55000,"e_w":8000,
            "e_speed":4000,"e_dmg":40,"e_ad":120,"e_kb_speed":2500,"e_kb_t":10,"e_behind":30000,"e_stun":72,
            "e_dmg2":50,"e_tri":50,"r_n":2,"r_tri_n":4,"r_gap":18,"r_dmg":60,"r_ad":135,"r_stun":66,"r_bleed":300,
            "r_bl_ad":60,"r_exec":15,"r_exec_tri":25,"r_reset":30000,"r_resets":2,"r_fall":80}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_slot_machine_pays_out_as_set() {
        let p = Params::default();
        let mut got = [0usize; 4];
        for seed in 0..20_000u64 {
            got[roll(&p, seed) as usize] += 1;
        }
        let tri = got[Mod::Triple as usize] as f64 / 20_000.0;
        assert!((tri - 0.12).abs() < 0.01, "jackpot {tri}");
        for m in [Mod::Rockets, Mod::Shield, Mod::Shimmer] {
            let share = got[m as usize] as f64 / 20_000.0;
            assert!((share - 0.88 / 3.0).abs() < 0.015, "{m:?} {share}");
        }
        assert_eq!(roll(&p, 42), roll(&p, 42));
    }

    #[test]
    fn rockets_go_to_champions_first() {
        let foes = [(1, (0, 0), false, 100, 100), (2, (1000, 0), true, 100, 100), (3, (900_000, 0), true, 50, 100)];
        for seed in 0..50 {
            assert_eq!(rocket_target(&foes, (0, 0), 60000, seed), Some(2));
        }
        assert_eq!(rocket_target(&foes[..1], (0, 0), 60000, 7), Some(1));
        assert_eq!(rocket_target(&foes, (500_000, 500_000), 1000, 7), None);
    }

    #[test]
    fn nearest_skips_the_one_hit_and_minions_on_request() {
        let foes = [(1, (0, 0), true, 100, 100), (2, (10000, 0), false, 100, 100), (3, (20000, 0), true, 100, 100)];
        assert_eq!(nearest(&foes, (0, 0), 30000, 1, false), Some(2));
        assert_eq!(nearest(&foes, (0, 0), 30000, 1, true), Some(3));
        assert_eq!(nearest(&foes, (0, 0), 15000, 1, true), None);
    }

    #[test]
    fn bites_fall_off_and_the_execute_line() {
        let p = Params::default();
        assert_eq!(bite_pct(&p, 0), 100);
        assert_eq!(bite_pct(&p, 1), 80);
        assert_eq!(bite_pct(&p, 2), 64);
        assert_eq!(physical(60, 135, 100, 80), 156);
        assert!(executed(149, 1000, 15));
        assert!(!executed(150, 1000, 15));
        assert!(!executed(0, 1000, 15));
        // the bleed: 60% of 100 attack over 300 ticks, 10 ticks a step = 2 a step, 60 in all
        assert_eq!(bleed_step(&p, 100), 2);
        assert_eq!(bleed_step(&p, 1), 1);
    }

    #[test]
    fn toward_goes_both_ways() {
        assert_eq!(toward((100, 100), (200, 100), 50), (150, 100));
        assert_eq!(toward((100, 100), (200, 100), -50), (50, 100));
        assert_eq!(toward((100, 100), (100, 100), 10), (110, 100));
    }
}
