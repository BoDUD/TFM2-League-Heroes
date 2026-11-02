//! 纳什男爵（`tft_baronnashor`）数据做不到的部分（金铲铲第 16 赛季的虚空五费，技能按用户选的方案 A，打野，2026-11-03）。
//! 它的数据（tools/kit/build_baronnashor.py）的 `passive` 是这里的 `tft_baronnashor:rift`，参数从数据的 `passive.params`
//! 来（build_baronnashor.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **虚空裂隙**：身边 `p_range` 以内有敌方英雄就算进入战斗；进入战斗 `p_first` 拍后、之后每 `p_every` 拍，从这个范围里
//!   随机挑一个敌方英雄，脚下喷出虚空触手：`p_dmg` + `p_ad`% 攻击力的物理伤害，击飞 `p_up` 拍（金铲铲「在虚空裂隙中时，
//!   每 3 秒在一个随机敌人下方喷出一条触手，击飞 1.5 秒」）。播 `tft_baronnashor_p`（声音）和 `tft_baronnashor_p_tent`
//!   （触手的画面，在它脚下）。附近没有敌方英雄了就算脱离战斗，下一次再从 `p_first` 数起。数据没有「每隔几秒」的时机。
//! - 它倒下时播 `tft_baronnashor_d`（数据没有阵亡的时机）。
//!
//! 腐蚀撕咬、腐蚀吐息、钻地突袭、虚空之怒是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_baronnashor.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_baronnashor";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// A unit's body (its collision radius, about): the rift's reach counts it, as the data's shapes do.
const BODY: u64 = 15000;

fn bn(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_BARONNASHOR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_baronnashor.log");
        }
    }
    PathBuf::from("tft_baronnashor.log")
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
    /// 虚空裂隙：p_range 以内（加上身子）有敌方英雄就算在战斗中，触手也只找这个范围里的。
    pub p_range: usize,
    /// 每 p_every 拍一条触手，进入战斗后第一条在 p_first 拍。
    pub p_every: usize,
    pub p_first: usize,
    /// 伤害：p_dmg + p_ad% 攻击力（物理）；击飞 p_up 拍。
    pub p_dmg: usize,
    pub p_ad: usize,
    pub p_up: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_range: 60000,
            p_every: 360,
            p_first: 120,
            p_dmg: 40,
            p_ad: 60,
            p_up: 45,
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
            "p_range" => p.p_range = u,
            "p_every" => p.p_every = u.max(1),
            "p_first" => p.p_first = u,
            "p_dmg" => p.p_dmg = u,
            "p_ad" => p.p_ad = u,
            "p_up" => p.p_up = u,
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// The tentacle: base + ratio% of its attack.
pub fn tentacle_damage(p: &Params, attack: usize) -> usize {
    p.p_dmg + attack * p.p_ad / 100
}

/// The next tentacle's tick: `p_first` after a fight starts (`since` = None: it starts now), then every `p_every`.
pub fn next_tentacle(now: usize, since: Option<usize>, last: Option<usize>, p: &Params) -> usize {
    match (since, last) {
        (_, Some(t)) => t + p.p_every,
        (Some(s), None) => s + p.p_first,
        (None, None) => now + p.p_first,
    }
}

/// Which of `n` prey the tentacle takes for this tick's seed (the ids sorted, so the pick is the same in every
/// simulation of the same game).
pub fn pick(n: usize, seed: u64, tick: usize) -> usize {
    let mut x = seed ^ (tick as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15);
    x ^= x >> 33;
    x = x.wrapping_mul(0xFF51_AFD7_ED55_8CCD);
    x ^= x >> 33;
    (x % n.max(1) as u64) as usize
}

// ===================== 场上 =====================

/// Live, targetable enemy champions of `team` within `reach` of `at`, by id: (id, where).
fn prey(sim: &StableSim<'_>, team: usize, at: (u64, u64), reach: u64) -> Vec<(usize, (u64, u64))> {
    let r = reach as u128;
    let mut out: Vec<(usize, (u64, u64))> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable())
        .filter(|u| matches!(u.kind(), Some(EntityKindV1::Champion)))
        .filter(|u| dist_sq(u.pos(), at) <= r * r)
        .map(|u| (u.id(), u.pos()))
        .collect();
    out.sort_by_key(|(id, _)| *id);
    out
}

// ===================== 被动：虚空裂隙 =====================

#[derive(Clone, Default)]
struct Rift {
    /// The champion it belongs to (on_dead is given the player, not the unit).
    me: usize,
    p: Params,
    /// The tick the fight started (an enemy champion came within p_range), None out of a fight.
    since: Option<usize>,
    /// The last tentacle's tick in this fight.
    last: Option<usize>,
}

impl StablePassive for Rift {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.since = None;
        self.last = None;
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Baron Nashor (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, seed: u64, _: usize, me: usize) {
        let Some((at, team, attack)) =
            sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.pos(), e.team(), e.stat().attack))
        else {
            self.since = None;
            self.last = None;
            return;
        };
        let p = self.p;
        let near = prey(sim, team, at, p.p_range as u64 + BODY);
        let now = sim.tick();
        if near.is_empty() {
            self.since = None;
            self.last = None;
            return;
        }
        let since = *self.since.get_or_insert(now);
        if now < next_tentacle(now, Some(since), self.last, &p) {
            return;
        }
        self.last = Some(now);
        let (id, pos) = near[pick(near.len(), seed, now)];
        let dmg = tentacle_damage(&p, attack);
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
        sim.apply_cc(id, &CcV1::of_kind(CcKindV1::Airborne, p.p_up as u64));
        let here = InputTargetV1::pos(pos.0, pos.1);
        sim.play_view_effect(&bn("p_tent"), me, &here, 0, 0, 0);
        sim.play_sfx(&bn("p"), me, &here);
        if let Some(k) = counted("tentacle") {
            wlog(format!("{} TENTACLE #{k}: under {} ({} in reach), {dmg} damage, knocked up {} ticks",
                         head(sim, me), name_of(sim, id), near.len(), p.p_up));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        let me = self.me;
        self.since = None;
        self.last = None;
        // it sinks back into the void (the data has no moment for it)
        sim.play_sfx(&bn("d"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("dead") {
            wlog(format!("{} DEAD #{k}: {}", head(sim, me), name_of(sim, me)));
        }
    }
}

// ===================== 注册 =====================

/// Baron Nashor's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Baron Nashor: the Void Rift's tentacles) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:rift"), Rift::default());
    host.log(LogLevel::Info, "tft.dll: Baron Nashor (the Void Rift's tentacles).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_ad":60,"p_dmg":40,"p_every":360,"p_first":120,"p_range":60000,"p_up":45}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn tentacles_by_the_clock() {
        let p = Params::default();
        assert_eq!(next_tentacle(500, Some(500), None, &p), 620, "the first one p_first into the fight");
        assert_eq!(next_tentacle(700, Some(500), Some(620), &p), 980, "then every p_every");
        assert_eq!(next_tentacle(900, None, None, &p), 1020);
    }

    #[test]
    fn damage_by_the_numbers() {
        assert_eq!(tentacle_damage(&Params::default(), 100), 40 + 60);
    }

    #[test]
    fn the_pick_stays_in_range_and_varies() {
        let picks: Vec<usize> = (0..60).map(|t| pick(3, 12345, t * 360)).collect();
        assert!(picks.iter().all(|&i| i < 3));
        assert!((0..3).all(|i| picks.contains(&i)), "every prey gets picked sometimes");
        assert_eq!(pick(1, 7, 99), 0);
        assert_eq!(pick(0, 7, 99), 0);
    }
}
