//! 迭嘉（`tft_daeja`）数据做不到的部分（金铲铲第 7 赛季的幻镜龙 / 龙神；技能按用户选的方案 A「罡风弹幕」，2026-10-30）。
//! 他的数据（tools/kit/build_daeja.py）的 `passive` 是这里的 `tft_daeja:mirage`，参数从数据的 `passive.params` 来
//! （build_daeja.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **罡风轰击**：金铲铲的「朝敌人最多的一条直线」。数据数不了一条线上有几个敌人，所以出手那一 tick（`tft_daeja:windblast`）
//!   由这里挑方向：以 `q_len` 以内每个敌人的方向为候选，数每条线（长 `q_len`、半宽 `q_w` 加单位半径）上的敌人，取最多的一条
//!   （一样多时先取穿过施法目标的、再取离施法方向最近的），从他身上朝那边发一道穿透的风波（`tft_daeja_q_wave`），
//!   每个被穿过的敌人（`tft_daeja:wave_hit`）受到 `q_dmg` + `q_ratio`% 法强魔法伤害。
//! - **苍穹罡风**：大招的每一道大冲击波（`tft_daeja:skygale`）同样挑敌人最多的线，`r_*` 的长度、宽度和伤害，命中是
//!   `tft_daeja:sky_hit`。
//! - **死亡**：倒下时播 `tft_daeja_d`（数据没有死亡的时机）。
//!
//! 三连弹幕（普攻后的三颗小风弹、叠加的减魔抗）、振翼退风（后跳、减速的风）和大招的飞起、减伤、落地是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_daeja.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_daeja";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const MAP: f64 = 960_000.0;
/// A unit's own radius, added to a wave's half width when counting who it runs through.
pub const UNIT_R: f64 = 10_000.0;
const WAVE_HIT: &str = "tft_daeja:wave_hit";
const SKY_HIT: &str = "tft_daeja:sky_hit";

fn dj(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_DAEJA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_daeja.log");
        }
    }
    PathBuf::from("tft_daeja.log")
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
    pub q_len: usize,
    pub q_w: usize,
    pub q_speed: usize,
    pub q_dmg: usize,
    pub q_ratio: usize,
    pub r_len: usize,
    pub r_w: usize,
    pub r_speed: usize,
    pub r_dmg: usize,
    pub r_ratio: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            q_len: 90000,
            q_w: 9000,
            q_speed: 6000,
            q_dmg: 120,
            q_ratio: 75,
            r_len: 110000,
            r_w: 12000,
            r_speed: 7000,
            r_dmg: 150,
            r_ratio: 70,
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
            "q_len" => p.q_len = u,
            "q_w" => p.q_w = u,
            "q_speed" => p.q_speed = u.max(1),
            "q_dmg" => p.q_dmg = u,
            "q_ratio" => p.q_ratio = u,
            "r_len" => p.r_len = u,
            "r_w" => p.r_w = u,
            "r_speed" => p.r_speed = u.max(1),
            "r_dmg" => p.r_dmg = u,
            "r_ratio" => p.r_ratio = u,
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

/// One wave: Q's or R's length, half width, speed and damage.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Wave {
    pub len: usize,
    pub w: usize,
    pub speed: usize,
    pub dmg: usize,
    pub ratio: usize,
}

impl Params {
    pub fn q(&self) -> Wave {
        Wave { len: self.q_len, w: self.q_w, speed: self.q_speed, dmg: self.q_dmg, ratio: self.q_ratio }
    }
    pub fn r(&self) -> Wave {
        Wave { len: self.r_len, w: self.r_w, speed: self.r_speed, dmg: self.r_dmg, ratio: self.r_ratio }
    }
}

/// A wave's magic damage on one unit: dmg + ratio% ap.
pub fn wave_damage(ap: usize, w: &Wave) -> usize {
    (w.dmg + ap * w.ratio / 100).max(1)
}

/// The units a wave from `from` along the unit vector `dir` runs through: ahead of him, within its length (and a
/// unit's radius past it), within its half width plus a unit's radius of the line.
pub fn on_line(from: (f64, f64), dir: (f64, f64), foes: &[(usize, (f64, f64))], w: &Wave) -> Vec<usize> {
    let reach = w.w as f64 + UNIT_R;
    foes.iter()
        .filter(|&&(_, p)| {
            let (dx, dy) = (p.0 - from.0, p.1 - from.1);
            let along = dx * dir.0 + dy * dir.1;
            let off = (dx * dir.1 - dy * dir.0).abs();
            along >= 0.0 && along <= w.len as f64 + UNIT_R && off <= reach
        })
        .map(|t| t.0)
        .collect()
}

/// The direction (a unit vector) of the line with the most enemies: the candidates are the directions to every enemy
/// within the wave's length; a tie goes to the line through `aim_id`, then to the one nearest the cast's own direction
/// `aim`. None when no enemy is in reach and there is no aim.
pub fn best_dir(
    from: (f64, f64),
    aim: Option<(f64, f64)>,
    aim_id: Option<usize>,
    foes: &[(usize, (f64, f64))],
    w: &Wave,
) -> Option<(f64, f64)> {
    let unit = |p: (f64, f64)| {
        let (dx, dy) = (p.0 - from.0, p.1 - from.1);
        let d = (dx * dx + dy * dy).sqrt();
        (d > 1.0).then(|| (dx / d, dy / d))
    };
    let aim_dir = aim.and_then(unit);
    let reach = w.len as f64 + UNIT_R;
    let mut cands: Vec<(f64, f64)> = foes
        .iter()
        .filter(|&&(_, p)| ((p.0 - from.0).powi(2) + (p.1 - from.1).powi(2)).sqrt() <= reach)
        .filter_map(|&(_, p)| unit(p))
        .collect();
    cands.extend(aim_dir);
    let mut best: Option<((usize, bool, f64), (f64, f64))> = None;
    for d in cands {
        let hit = on_line(from, d, foes, w);
        let through = aim_id.is_some_and(|a| hit.contains(&a));
        let near = aim_dir.map_or(0.0, |a| a.0 * d.0 + a.1 * d.1);
        let score = (hit.len(), through, near);
        let better = match &best {
            None => true,
            Some((s, _)) => (score.0, score.1) > (s.0, s.1) || ((score.0, score.1) == (s.0, s.1) && score.2 > s.2),
        };
        if better {
            best = Some((score, d));
        }
    }
    best.map(|b| b.1)
}

// ===================== 模拟里的小工具 =====================

/// Live, targetable enemy units (no towers, no nexus) of `me`: (id, position).
fn foes(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (f64, f64))> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| (u.id(), (u.pos().0 as f64, u.pos().1 as f64)))
        .collect()
}

fn upos(p: (f64, f64)) -> (u64, u64) {
    (p.0.round().clamp(0.0, MAP - 1.0) as u64, p.1.round().clamp(0.0, MAP - 1.0) as u64)
}

/// Q's or R's release: the line with the most enemies, one penetrating wave down it.
fn send(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1, ult: bool) {
    let Some((team, at)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.team(), e.pos())) else { return };
    let from = (at.0 as f64, at.1 as f64);
    let p = params_of(me);
    let w = if ult { p.r() } else { p.q() };
    let list = foes(sim, me);
    let (aim, aim_id) = if input.kind == InputTargetKindV1::Target.code() {
        let unit = sim.get_entity(input.target_id).filter(|e| e.is_alive()).map(|e| e.pos());
        (unit.map(|u| (u.0 as f64, u.1 as f64)), Some(input.target_id))
    } else if input.kind == InputTargetKindV1::Pos.code() {
        (Some((input.x as f64, input.y as f64)), None)
    } else {
        (None, None)
    };
    let kind = if ult { "SKYGALE" } else { "WINDBLAST" };
    let Some(dir) = best_dir(from, aim, aim_id, &list, &w) else {
        if let Some(k) = counted("nobody") {
            wlog(format!("{} {kind} #{k}: nobody in reach (input kind {})", head(sim, me), input.kind));
        }
        return;
    };
    let hit = on_line(from, dir, &list, &w);
    let to = upos((from.0 + dir.0 * w.len as f64, from.1 + dir.1 * w.len as f64));
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team,
        x: at.0,
        y: at.1,
        radius: w.w as u64,
        speed: w.speed as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: to.0,
        target_y: to.1,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::EnemyWithoutTower.code(),
    };
    let (pic, effect) = if ult { (dj("r_wave"), SKY_HIT) } else { (dj("q_wave"), WAVE_HIT) };
    let sent = sim.spawn_projectile(&pic, effect, &spec);
    if let Some(k) = counted(if ult { "skygale" } else { "windblast" }) {
        wlog(format!(
            "{} {kind} #{k}: toward ({}, {}), {} on the line {:?}{}",
            head(sim, me),
            to.0,
            to.1,
            hit.len(),
            hit.iter().map(|&t| name_of(sim, t)).collect::<Vec<_>>(),
            if sent { String::new() } else { " - spawn_projectile refused".to_string() }
        ));
    }
}

/// A wave's hit on one enemy.
fn strike(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1, ult: bool) {
    if input.kind != InputTargetKindV1::Target.code() {
        return;
    }
    let id = input.target_id;
    let p = params_of(me);
    let w = if ult { p.r() } else { p.q() };
    let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
    let d = wave_damage(ap, &w);
    sim.deal_damage_typed(me, id, d, DamageTypeV1::Ap, AttackTypeV1::Skill);
    let on = InputTargetV1::target(id);
    let (pic, sound) = if ult { (dj("r_hit"), dj("r_hit")) } else { (dj("q_hit"), dj("q_hit")) };
    sim.play_view_effect(&pic, me, &on, 0, 0, 0);
    sim.play_sfx(&sound, me, &on);
    if let Some(k) = counted(if ult { "sky hit" } else { "wave hit" }) {
        wlog(format!("{} {} #{k}: {} takes {d} magic", head(sim, me), if ult { "SKY" } else { "WAVE" }, name_of(sim, id)));
    }
}

struct Windblast;
impl StableEffectType for Windblast {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        send(sim, me, input, false);
    }
}

struct SkyGale;
impl StableEffectType for SkyGale {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        send(sim, me, input, true);
    }
}

struct WaveHit;
impl StableEffectType for WaveHit {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        strike(sim, me, input, false);
    }
}

struct SkyHit;
impl StableEffectType for SkyHit {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        strike(sim, me, input, true);
    }
}

// ===================== 被动：幻镜（参数、死亡音效） =====================

#[derive(Clone, Default)]
struct Mirage {
    p: Params,
}

impl StablePassive for Mirage {
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
            wlog(format!("{} SPAWN #{k}: tft.dll's Daeja (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, _: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        // his death cry (the data has no moment for it)
        sim.play_sfx(&dj("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// Daeja's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Daeja: Windblast and Sky Gale down the line with the most enemies) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:mirage"), Mirage::default());
    module.add_native_effect(format!("{ID}:windblast"), Windblast);
    module.add_native_effect(format!("{ID}:skygale"), SkyGale);
    module.add_native_effect(format!("{ID}:wave_hit"), WaveHit);
    module.add_native_effect(format!("{ID}:sky_hit"), SkyHit);
    host.log(LogLevel::Info, "tft.dll: Daeja (Windblast, Sky Gale).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"q_dmg":120,"q_len":90000,"q_ratio":75,"q_speed":6000,"q_w":9000,"r_dmg":150,"r_len":110000,"r_ratio":70,"r_speed":7000,"r_w":12000}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn a_wave_hurts_by_its_own_numbers() {
        let p = Params::default();
        assert_eq!(wave_damage(0, &p.q()), 120);
        assert_eq!(wave_damage(100, &p.q()), 195);
        assert_eq!(wave_damage(100, &p.r()), 220);
    }

    #[test]
    fn the_line_holds_only_what_is_ahead_and_near() {
        let w = Params::default().q();
        let foes = [(1, (50000.0, 0.0)), (2, (50000.0, 18000.0)), (3, (50000.0, 25000.0)), (4, (-20000.0, 0.0)),
                    (5, (105000.0, 0.0))];
        assert_eq!(on_line((0.0, 0.0), (1.0, 0.0), &foes, &w), vec![1, 2]);
    }

    #[test]
    fn the_wave_goes_where_most_enemies_stand() {
        let w = Params::default().q();
        // the target alone to the right, three in a row upward
        let foes = [(1, (40000.0, 0.0)), (2, (0.0, 30000.0)), (3, (0.0, 55000.0)), (4, (3000.0, 80000.0))];
        let d = best_dir((0.0, 0.0), Some((40000.0, 0.0)), Some(1), &foes, &w).unwrap();
        assert!(d.1 > 0.9, "{d:?}");
        // one each way: the line through the target wins the tie
        let two = [(1, (40000.0, 0.0)), (2, (0.0, 40000.0))];
        let d = best_dir((0.0, 0.0), Some((40000.0, 0.0)), Some(1), &two, &w).unwrap();
        assert!(d.0 > 0.99, "{d:?}");
        // nobody in reach: along the cast; no aim either: nothing
        let far = [(9, (500000.0, 0.0))];
        let d = best_dir((0.0, 0.0), Some((0.0, -10.0)), None, &far, &w).unwrap();
        assert!(d.1 < -0.99, "{d:?}");
        assert!(best_dir((0.0, 0.0), None, None, &far, &w).is_none());
    }
}
