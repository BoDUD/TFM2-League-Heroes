//! 深红锋喙鸟（`tft_raptor`，用户叫它锋啄鸟）数据做不到的部分（金铲铲第 18 赛季的峡谷野怪 / 召唤师 / 迅捷射手；技能按用户选的
//! 方案 A「鸟群之家」，2026-10-31）。她的数据（tools/kit/build_raptor.py）的 `passive` 是这里的 `tft_raptor:flock`，参数从数据的
//! `passive.params` 来（build_raptor.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **羽刃扇射**：数据里的投射物不能带角度，所以出手那一 tick（`tft_raptor:fan`）由这里朝目标方向扇形发出 `q_n` 根羽刃，
//!   相邻两根差 `q_spread` 度，每根各自直飞 `q_len`、碰到第一个敌人就停（`tft_raptor_q_feather`）；命中
//!   （`tft_raptor:fan_hit`）受到 `q_dmg` + `q_ratio`% 攻击力的物理伤害，再挂一层橙霸符。近身时一个敌人会吃到好几根。
//! - **橙霸符**：她的每次物理命中（普攻、羽刃、小锋喙鸟的啄击）都调 `tft_raptor:shred`：目标护甲 -`p_arm`，持续 `p_t`
//!   tick，最多 `p_max` 层，再中一下刷新时长（引擎的叠层 buff；数据的同名 buff 只会无限叠）。叠满那一下播 `tft_raptor_p`。
//! - **死亡**：倒下时播 `tft_raptor_d`（数据没有死亡的时机）。
//!
//! 普攻的羽毛、惊飞跃退（后跳、攻速）和大招的小锋喙鸟（旗子 `tft_raptor_r_flock` 期间每次普攻追加的啄击）是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_raptor.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_raptor";
const VERSION: &str = env!("CARGO_PKG_VERSION");
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

fn upos(p: (f64, f64)) -> (u64, u64) {
    (p.0.round().clamp(0.0, MAP - 1.0) as u64, p.1.round().clamp(0.0, MAP - 1.0) as u64)
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
    let aim = if input.kind == InputTargetKindV1::Target.code() {
        sim.get_entity(input.target_id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
    } else if input.kind == InputTargetKindV1::Pos.code() {
        Some((input.x as f64, input.y as f64))
    } else {
        None
    };
    let Some(aim) = aim.map(|a| (a.0 - from.0, a.1 - from.1)).filter(|d| d.0.hypot(d.1) > 1.0) else {
        if let Some(k) = counted("no aim") {
            wlog(format!("{} FAN #{k}: no aim (input kind {})", head(sim, me), input.kind));
        }
        return;
    };
    let p = params_of(me);
    let mut refused = 0;
    for d in fan_dirs(aim, p.q_n, p.q_spread) {
        let to = upos((from.0 + d.0 * p.q_len as f64, from.1 + d.1 * p.q_len as f64));
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
            "{} FAN #{k}: {} feathers {} deg apart toward ({:.0}, {:.0}){}",
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
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Crimson Raptor (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, _: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
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
    fn the_shred_is_negative_armour() {
        let b = shred_buff(&Params::default());
        assert_eq!(b.name(), "tft_raptor_p_shred");
        assert_eq!(b.defence, -6);
        assert_eq!(b.duration_tick, 180);
    }
}
