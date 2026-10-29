//! 诺姆希（`tft_nomsy`）数据做不到的部分（金铲铲第 7 赛季的小龙宝宝 / 龙神、龙族小天才；技能按用户选的方案 A
//! 「龙神飞升」，2026-10-29）。她的数据（tools/kit/build_nomsy.py）的 `passive` 是这里的 `tft_nomsy:dragon`，参数从数据的
//! `passive.params` 来（build_nomsy.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **龙神之躯**：金铲铲的龙神每秒回血。数据读不到生命值，所以由本被动来看：她活着、生命值低于最大值的 `p_low`% 时，
//!   每 `p_every` tick 回复最大生命值的 `p_pct`%，挂 `tft_nomsy_p_heal`（身上的回血画面），播 `tft_nomsy_p`。
//! - **火球！的弹射**：数据里的投射物只能从施法者身上飞出去，金铲铲的小火球却是从爆炸的地方弹出去的。所以大火球落地时
//!   （`end_effects` 里的 `tft_nomsy:bounce`）由这里在落点生成 `q_n` 颗小火球（`tft_nomsy_q_bounce`），飞向落点 `q_br`
//!   以内最近的、不在爆炸范围 `q_r` 里的敌人（不够时才轮到爆炸范围里的），每颗命中（`tft_nomsy:ember`）造成大火球伤害
//!   （`q_dmg` + `q_ratio`% 法强）的 `q_k`% 魔法伤害。
//!
//! 龙息（扇形喷火、灼烧、减魔抗）和龙神飞升（飞天、火球雨、落地后攻速法强）是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_nomsy.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_nomsy";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// How long the heal picture stays on her, in ticks.
pub const HEAL_T: usize = 40;
const EMBER_FX: &str = "tft_nomsy:ember";

fn nm(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_NOMSY_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_nomsy.log");
        }
    }
    PathBuf::from("tft_nomsy.log")
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
    /// 龙神之躯：生命值低于 p_low% 时，每 p_every tick 回复最大生命值的 p_pct%。
    pub p_low: usize,
    pub p_every: usize,
    pub p_pct: usize,
    /// 火球！：大火球 q_dmg + q_ratio% 法强，爆炸半径 q_r；q_n 颗小火球弹向 q_br 以内的敌人，每颗 q_k%，速度 q_speed。
    pub q_dmg: usize,
    pub q_ratio: usize,
    pub q_r: usize,
    pub q_n: usize,
    pub q_k: usize,
    pub q_br: usize,
    pub q_speed: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_low: 40,
            p_every: 60,
            p_pct: 3,
            q_dmg: 70,
            q_ratio: 55,
            q_r: 18000,
            q_n: 2,
            q_k: 50,
            q_br: 45000,
            q_speed: 3000,
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
            "p_low" => p.p_low = u,
            "p_every" => p.p_every = u.max(1),
            "p_pct" => p.p_pct = u,
            "q_dmg" => p.q_dmg = u,
            "q_ratio" => p.q_ratio = u,
            "q_r" => p.q_r = u,
            "q_n" => p.q_n = u,
            "q_k" => p.q_k = u,
            "q_br" => p.q_br = u,
            "q_speed" => p.q_speed = u.max(1),
            _ => {}
        }
    }
    p
}

/// Each Nomsy's params by entity id (the bounce effects run without the passive at hand).
static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

// ===================== 规则（单元测试用） =====================

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// Low enough for the dragon's body to mend: health under p_low% of the maximum (and not dead).
pub fn is_low(hp: usize, max: usize, p: &Params) -> bool {
    hp > 0 && max > 0 && hp * 100 < max * p.p_low
}

/// One heal: p_pct% of her maximum health, at least 1.
pub fn heal_amount(max: usize, p: &Params) -> usize {
    (max * p.p_pct / 100).max(1)
}

/// One small fireball's magic damage: q_k% of the big one's (q_dmg + q_ratio% ap).
pub fn ember_damage(ap: usize, p: &Params) -> usize {
    ((p.q_dmg + ap * p.q_ratio / 100) * p.q_k / 100).max(1)
}

/// The enemies the small fireballs fly to from the explosion at `at`: the nearest within q_br that the blast (q_r)
/// missed first, then those it hit, at most q_n; ids break ties.
pub fn bounce_targets(foes: &[(usize, (u64, u64))], at: (u64, u64), p: &Params) -> Vec<usize> {
    let reach = (p.q_br as u128) * (p.q_br as u128);
    let blast = (p.q_r as u128) * (p.q_r as u128);
    let mut near: Vec<(bool, u128, usize)> = foes
        .iter()
        .map(|&(id, pos)| (id, dist_sq(pos, at)))
        .filter(|&(_, d)| d <= reach)
        .map(|(id, d)| (d <= blast, d, id))
        .collect();
    near.sort();
    near.into_iter().take(p.q_n).map(|t| t.2).collect()
}

// ===================== 模拟里的小工具 =====================

/// Live, targetable enemy units (no towers, no nexus) of `me`: (id, position).
fn foes(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64))> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| (u.id(), u.pos()))
        .collect()
}

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

// ===================== 火球！的弹射 =====================

/// In the big fireball's end_effects: the small ones, spawned where it exploded.
struct Bounce;
impl StableEffectType for Bounce {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let p = params_of(me);
        let at = if input.kind == InputTargetKindV1::Target.code() {
            sim.get_entity(input.target_id).map(|e| e.pos())
        } else if input.kind == InputTargetKindV1::Pos.code() {
            Some((input.x, input.y))
        } else {
            None
        };
        let Some(at) = at else {
            if let Some(k) = counted("bounce lost") {
                wlog(format!("{} BOUNCE #{k}: no landing point (input kind {})", head(sim, me), input.kind));
            }
            return;
        };
        let targets = bounce_targets(&foes(sim, me), at, &p);
        let mut refused = 0;
        for &t in &targets {
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team,
                x: at.0,
                y: at.1,
                radius: 4000,
                speed: p.q_speed as u64,
                move_kind: ProjectileMoveKindV1::Target.code(),
                target_id: t,
                target_x: 0,
                target_y: 0,
                penetrate: false,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::EnemyWithoutTower.code(),
            };
            if !sim.spawn_projectile(&nm("q_bounce"), EMBER_FX, &spec) {
                refused += 1;
            }
        }
        if !targets.is_empty() {
            sim.play_sfx(&nm("q_bounce"), me, &InputTargetV1::pos(at.0, at.1));
        }
        if let Some(k) = counted("bounce") {
            wlog(format!(
                "{} BOUNCE #{k}: from ({}, {}) to {:?}{}",
                head(sim, me),
                at.0,
                at.1,
                targets.iter().map(|&t| name_of(sim, t)).collect::<Vec<_>>(),
                if refused > 0 { format!(" - spawn_projectile refused {refused}") } else { String::new() }
            ));
        }
    }
}

/// A small fireball's hit.
struct Ember;
impl StableEffectType for Ember {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let id = input.target_id;
        let p = params_of(me);
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let d = ember_damage(ap, &p);
        sim.deal_damage_typed(me, id, d, DamageTypeV1::Ap, AttackTypeV1::Skill);
        let on = InputTargetV1::target(id);
        sim.play_view_effect(&nm("q_bounce_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(&nm("q_bounce_hit"), me, &on);
        if let Some(k) = counted("ember") {
            wlog(format!("{} EMBER #{k}: {} takes {d} magic", head(sim, me), name_of(sim, id)));
        }
    }
}

// ===================== 被动：龙神之躯 =====================

#[derive(Clone, Default)]
struct Dragon {
    p: Params,
    next_at: usize,
}

impl StablePassive for Dragon {
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
            wlog(format!("{} SPAWN #{k}: tft.dll's Nomsy (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        let now = sim.tick();
        let Some((hp, max)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        if now < self.next_at || !is_low(hp, max, &self.p) {
            return;
        }
        self.next_at = now + self.p.p_every;
        let amount = heal_amount(max, &self.p);
        sim.heal(me, me, amount);
        put(sim, me, &BuffV1::timed(&nm("p_heal"), HEAL_T));
        sim.play_sfx(&nm("p"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("heal") {
            wlog(format!("{} HEAL #{k}: {hp}/{max} -> +{amount}", head(sim, me)));
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _me: usize) {
        self.next_at = 0;
    }
}

// ===================== 注册 =====================

/// Nomsy's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Nomsy: Dragon Body heals, the bouncing fireballs) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:dragon"), Dragon::default());
    module.add_native_effect(format!("{ID}:bounce"), Bounce);
    module.add_native_effect(format!("{ID}:ember"), Ember);
    host.log(LogLevel::Info, "tft.dll: Nomsy (Dragon Body, Fireballs!).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_every":60,"p_low":40,"p_pct":3,"q_br":45000,"q_dmg":70,"q_k":50,"q_n":2,"q_r":18000,"q_ratio":55,"q_speed":3000}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn she_mends_only_when_low() {
        let p = Params::default();
        assert!(is_low(399, 1000, &p));
        assert!(!is_low(400, 1000, &p));
        assert!(!is_low(0, 1000, &p));
        assert_eq!(heal_amount(1500, &p), 45);
        assert_eq!(heal_amount(10, &p), 1);
    }

    #[test]
    fn a_small_fireball_is_half_the_big_one() {
        let p = Params::default();
        assert_eq!(ember_damage(0, &p), 35);
        assert_eq!(ember_damage(200, &p), (70 + 110) / 2);
    }

    #[test]
    fn the_bounces_go_past_the_blast_first() {
        let p = Params::default();
        let foes = [(1, (0, 0)), (2, (10000, 0)), (3, (30000, 0)), (4, (40000, 0)), (5, (60000, 0))];
        assert_eq!(bounce_targets(&foes, (0, 0), &p), vec![3, 4]);
        // only one outside the blast: then the nearest one inside it
        assert_eq!(bounce_targets(&foes[..3], (0, 0), &p), vec![3, 1]);
        // nobody within q_br
        assert!(bounce_targets(&foes[4..], (0, 0), &p).is_empty());
    }
}
