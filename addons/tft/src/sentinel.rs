//! 苍蓝雕纹魔像（`tft_sentinel`）数据做不到的部分（金铲铲第 18 赛季的峡谷野怪 / 重装战士 / 神谕四费坦克，技能按用户选的
//! 方案 A「蔚蓝冲击波」，2026-10-31）。它的数据（tools/kit/build_sentinel.py）的 `passive` 是这里的 `tft_sentinel:golem`，
//! 参数从数据的 `passive.params` 来（build_sentinel.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **蔚蓝冲击波（裂隙）** `tft_sentinel:fissure`：朝**敌方英雄最多**的方向砸出一道裂隙。候选方向是朝 `r_len` 以内每个
//!   敌方英雄的方向，数每个方向上 `r_len` 长、半宽 `r_w`（加上身子）的带子里有几个敌方英雄，取最多的；一样多时取 AI
//!   选的目标，再取近的。裂隙是一发穿透的直线弹道（`tft_sentinel_r_crack`，带画面，每拍 `r_speed`），撞到的每个敌人
//!   （`tft_sentinel:crack`，每次裂隙每人一次）挨 `r_dmg` + `r_ratio`% 法强 + `r_hp`% 它最大生命的魔法伤害、被击飞
//!   `r_up` 拍、亮 `tft_sentinel_r_hit`；英雄还被**破法**（`tft_sentinel_r_reave`，带画面，最多 `r_mark` 拍）。数据定不了
//!   方向。
//! - **破法**：被破法的敌方英雄，下一个技能（Q / E / R 任一个）一就绪，就被封住 `r_reave` 拍（`BlockSkill`，画面换成
//!   `tft_sentinel_r_seal`）——金铲铲的破法让下一次施法要多攒法力，我们的游戏只能缩短冷却、不能加长，所以把「下一次技能
//!   晚 `r_reave` 拍」做成就绪那一刻的封印（标记时已经有技能就绪的，马上封）。
//! - **死亡**：倒下时播 `tft_sentinel_d`。
//!
//! 岩拳猛击、蓝霸符（友军技能冷却缩短）、双拳重砸、雕纹石肤和大招的护盾是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_sentinel.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::{HashMap, HashSet};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_sentinel";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const CRACK_FX: &str = "tft_sentinel:crack";
/// A champion's body on top of the fissure's half width (the pack's collision radius).
const BODY: u64 = 15000;

fn sn(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_SENTINEL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_sentinel.log");
        }
    }
    PathBuf::from("tft_sentinel.log")
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
    /// 裂隙：长 r_len、半宽 r_w（加上身子），每拍 r_speed。
    pub r_len: usize,
    pub r_w: usize,
    pub r_speed: usize,
    /// 命中：r_dmg + r_ratio% 法强 + r_hp% 它的最大生命（魔法），击飞 r_up 拍。
    pub r_dmg: usize,
    pub r_ratio: usize,
    pub r_hp: usize,
    pub r_up: usize,
    /// 破法：标记最多 r_mark 拍；下一个技能就绪时封住 r_reave 拍。
    pub r_mark: usize,
    pub r_reave: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            r_len: 100000,
            r_w: 16000,
            r_speed: 5000,
            r_dmg: 170,
            r_ratio: 170,
            r_hp: 4,
            r_up: 50,
            r_mark: 900,
            r_reave: 120,
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
            "r_len" => p.r_len = u,
            "r_w" => p.r_w = u,
            "r_speed" => p.r_speed = u.max(1),
            "r_dmg" => p.r_dmg = u,
            "r_ratio" => p.r_ratio = u,
            "r_hp" => p.r_hp = u,
            "r_up" => p.r_up = u,
            "r_mark" => p.r_mark = u,
            "r_reave" => p.r_reave = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// 裂隙按（种子、模拟来源、比赛、局、它）分开：同一个进程里预演和观看的模拟各算各的（league_loris 的做法）。
type Key = (u64, u32, u64, u64, usize);
/// The units the current fissure has hit (each once).
static HIT: LazyLock<Mutex<HashMap<Key, HashSet<usize>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn key(sim: &StableSim<'_>, me: usize) -> Key {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index, me)
}

// ===================== 规则（单元测试用） =====================

/// base + ratio% of the ability power + hp% of its maximum health.
pub fn magic(base: usize, ratio: usize, ap: usize, hp: usize, max_hp: usize) -> usize {
    base + ap * ratio / 100 + max_hp * hp / 100
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

/// The direction (an enemy champion's id) whose band holds the most enemy champions: each one in reach is a
/// candidate; ties go to the AI's target, then the nearer. `champs` = (id, where).
pub fn best_line(at: (u64, u64), champs: &[(usize, (u64, u64))], aimed: Option<usize>, len: u64, half: u64)
    -> Option<(usize, usize)> {
    let reach = ((len + half) as u128) * ((len + half) as u128);
    champs
        .iter()
        .filter(|c| dist_sq(at, c.1) <= reach && dist_sq(at, c.1) > 0)
        .map(|c| (c.0, champs.iter().filter(|o| in_band(at, c.1, o.1, len, half)).count(), dist_sq(at, c.1)))
        .max_by(|a, b| a.1.cmp(&b.1).then((Some(a.0) == aimed).cmp(&(Some(b.0) == aimed))).then(b.2.cmp(&a.2)))
        .map(|(id, n, _)| (id, n))
}

/// Where the fissure stops: `len` from `from` toward `to`, clamped to the map's corner (0, 0).
pub fn end_of(from: (u64, u64), to: (u64, u64), len: u64) -> (u64, u64) {
    let (dx, dy) = (to.0 as f64 - from.0 as f64, to.1 as f64 - from.1 as f64);
    let d = (dx * dx + dy * dy).sqrt().max(1.0);
    let x = from.0 as f64 + dx / d * len as f64;
    let y = from.1 as f64 + dy / d * len as f64;
    (x.round().max(0.0) as u64, y.round().max(0.0) as u64)
}

/// A skill of `cds` (Q, E, R) is ready: unlocked and nothing left.
pub fn any_ready(cds: &[Option<CooldownV1>]) -> bool {
    cds.iter().flatten().any(|c| c.unlocked && c.remaining == 0)
}

// ===================== 场上 =====================

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
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

// ===================== 蔚蓝冲击波 =====================

/// The slam: the fissure leaves toward the most enemy champions.
struct Fissure;
impl StableEffectType for Fissure {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some((at, team)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.pos(), e.team())) else { return };
        let p = params_of(me);
        let champs = enemy_champs(sim, me);
        let aimed = (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id);
        let half = p.r_w as u64 + BODY;
        let best = best_line(at, &champs, aimed, p.r_len as u64, half);
        let toward = best.map(|b| b.0).or(aimed.filter(|&id| reachable(sim, id)));
        let Some(toward) = toward else {
            if let Some(k) = counted("fissure_none") {
                wlog(format!("{} FISSURE NONE #{k}: nobody to aim at", head(sim, me)));
            }
            return;
        };
        let to = sim.get_entity(toward).map_or(at, |e| e.pos());
        let end = end_of(at, to, p.r_len as u64);
        HIT.lock().unwrap_or_else(|e| e.into_inner()).insert(key(sim, me), HashSet::new());
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team,
            x: at.0,
            y: at.1,
            radius: p.r_w as u64,
            speed: p.r_speed as u64,
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: end.0,
            target_y: end.1,
            penetrate: true,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        let ok = sim.spawn_projectile(&sn("r_crack"), CRACK_FX, &spec);
        if let Some(k) = counted("fissure") {
            wlog(format!("{} FISSURE #{k}: toward {} ({} enemy champions in the line; the AI aimed at {}){}",
                         head(sim, me), name_of(sim, toward), best.map_or(0, |b| b.1),
                         aimed.map_or_else(|| "nobody".to_string(), |id| name_of(sim, id)),
                         if ok { "" } else { " - spawn_projectile refused" }));
        }
    }
}

/// The fissure reaches a unit: magic damage, knocked up; a champion is Mana Reaved.
struct Crack;
impl StableEffectType for Crack {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let id = input.target_id;
        if !reachable(sim, id) || !HIT.lock().unwrap_or_else(|e| e.into_inner()).entry(key(sim, me)).or_default().insert(id) {
            return;
        }
        let p = params_of(me);
        let (ap, max_hp) = sim.get_entity(me).map_or((0, 0), |e| (e.stat().magic_power, e.hp().1));
        let dmg = magic(p.r_dmg, p.r_ratio, ap, p.r_hp, max_hp);
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        sim.apply_cc(id, &CcV1::of_kind(CcKindV1::Airborne, p.r_up as u64));
        put(sim, id, &BuffV1::timed(&sn("r_hit"), 30));
        sim.play_sfx(&sn("r_hit"), me, &InputTargetV1::target(id));
        let champion = sim.get_entity(id).is_some_and(|e| e.is_champion());
        if champion {
            put(sim, id, &BuffV1::timed(&sn("r_reave"), p.r_mark));
            sim.play_sfx(&sn("r_reave"), me, &InputTargetV1::target(id));
        }
        if let Some(k) = counted("crack") {
            wlog(format!("{} CRACK #{k}: {} takes {dmg}, knocked up {} ticks{}", head(sim, me), name_of(sim, id), p.r_up,
                         if champion { ", Mana Reaved" } else { "" }));
        }
    }
}

// ===================== 被动：破法、死亡 =====================

#[derive(Clone, Default)]
struct Golem {
    /// The champion it belongs to (on_dead is given the player, not the unit).
    me: usize,
    p: Params,
}

impl StablePassive for Golem {
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
            wlog(format!("{} SPAWN #{k}: tft.dll's Blue Sentinel (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        // Mana Reave: an enemy it marked whose next skill comes ready is sealed for r_reave ticks (its own marks:
        // its team's enemies; the mark lapses after r_mark)
        let mark = sn("r_reave");
        for (id, _) in enemy_champs(sim, me) {
            if !has_buff(sim, id, &mark) {
                continue;
            }
            let cds: Vec<Option<CooldownV1>> = sim.get_entity(id).map_or_else(Vec::new, |e| {
                [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult].iter().map(|&s| e.cooldown(s)).collect()
            });
            if !any_ready(&cds) {
                continue;
            }
            sim.entity_remove_buff(id, &mark);
            sim.apply_cc(id, &CcV1::of_kind(CcKindV1::BlockSkill, self.p.r_reave as u64));
            put(sim, id, &BuffV1::timed(&sn("r_seal"), self.p.r_reave));
            if let Some(k) = counted("seal") {
                wlog(format!("{} SEAL #{k}: {}'s next skill is ready - sealed {} ticks", head(sim, me), name_of(sim, id),
                             self.p.r_reave));
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        let me = self.me;
        // its crumbling (the data has no moment for it)
        HIT.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me));
        sim.play_sfx(&sn("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// The Blue Sentinel's Mana Reave and Azure Shockwave's fissure, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Blue Sentinel: Azure Shockwave toward the most enemies, Mana Reave) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:golem"), Golem::default());
    module.add_native_effect(format!("{ID}:fissure"), Fissure);
    module.add_native_effect(CRACK_FX, Crack);
    host.log(LogLevel::Info, "tft.dll: Blue Sentinel (Azure Shockwave, Mana Reave).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"r_dmg":170,"r_hp":4,"r_len":100000,"r_mark":900,"r_ratio":170,"r_reave":120,"r_speed":5000,"r_up":50,"r_w":16000}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_line_with_the_most_enemies() {
        // 1 alone ahead; 2 and 3 in one line to the right; 4 too far
        let champs = [(1, (0, 40000)), (2, (40000, 0)), (3, (80000, 5000)), (4, (300000, 0))];
        assert_eq!(best_line((0, 0), &champs, Some(1), 100000, 31000), Some((2, 2)));
        // one each: the AI's target wins the tie, else the nearer
        let apart = [(1, (0, 60000)), (2, (40000, 0))];
        assert_eq!(best_line((0, 0), &apart, Some(1), 100000, 31000), Some((1, 1)));
        assert_eq!(best_line((0, 0), &apart, None, 100000, 31000), Some((2, 1)));
        assert_eq!(best_line((0, 0), &champs[3..], None, 100000, 31000), None);
    }

    #[test]
    fn the_band() {
        assert!(in_band((0, 0), (10, 0), (90000, 30000), 100000, 31000));
        assert!(!in_band((0, 0), (10, 0), (90000, 32000), 100000, 31000));
        assert!(!in_band((0, 0), (10, 0), (110000, 0), 100000, 31000));
        assert!(!in_band((50000, 0), (60000, 0), (0, 0), 100000, 31000));   // behind it
    }

    #[test]
    fn the_fissure_ends_its_length_away() {
        assert_eq!(end_of((100000, 100000), (130000, 140000), 100000), (160000, 180000));
        assert_eq!(end_of((10000, 10000), (0, 10000), 100000), (0, 10000));   // clamped at the map's edge
    }

    #[test]
    fn reave_waits_for_a_ready_skill() {
        let cd = |remaining, unlocked| Some(CooldownV1 { remaining, unlocked, ..CooldownV1::default() });
        assert!(!any_ready(&[cd(30, true), cd(5, true), cd(900, true)]));
        assert!(any_ready(&[cd(30, true), cd(0, true), cd(900, true)]));
        assert!(!any_ready(&[cd(30, true), None, cd(0, false)]));   // a locked ult is no skill
    }

    #[test]
    fn damage_by_the_numbers() {
        let p = Params::default();
        assert_eq!(magic(p.r_dmg, p.r_ratio, 50, p.r_hp, 1500), 170 + 85 + 60);
    }
}
