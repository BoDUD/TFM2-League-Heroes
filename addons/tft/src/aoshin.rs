//! 敖兴（`tft_aoshin`）数据做不到的部分（金铲铲第 7 赛季的风暴龙 / 龙神，本包第一个第 7 赛季的英雄；技能按用户选的方案 A
//! 「风暴龙神」，2026-10-28）。他的数据（tools/kit/build_aoshin.py）的 `passive` 是这里的 `tft_aoshin:storm`，参数从数据的
//! `passive.params` 来（build_aoshin.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **风暴龙威**：金铲铲里开战 8 秒后闪电劈遍整个棋盘。数据只在动作里跑，数不了「打了多久」，所以由本被动来数：
//!   他活着、`p_sense` 以内有敌方英雄的每个 tick 记一下（中间断开不超过 `p_quiet` tick 照样接着数，断得更久从头数），
//!   数满 `p_delay` tick、且离上次落雷过了 `p_cd` tick 时，`p_r` 以内的每个敌方英雄挨一道雷：最大生命值 `p_hp`% 的真实伤害、
//!   晕眩 `p_stun` tick、挂 `tft_aoshin_p_bolt`（落雷的画面）；他自己挂 `p_t` tick 的 `tft_aoshin_p_storm`（法强
//!   +`p_amp`%，身上噼啪的电光）。吼一声、雷声、晕眩声。画面都挂成 buff（tft.dll 直接播的画面游戏里看不到：
//!   league_bard 的门的教训）。范围里一个敌方英雄都没有时不落，接着等。
//!
//! 雷息（直线闪电、沉默）、腾云（后飞、护盾）和闪电暴雨（随机落雷、沉默）是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_aoshin.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_aoshin";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// How long the bolt picture stays on a struck champion, in ticks.
pub const BOLT_T: usize = 30;

fn ao(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_AOSHIN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_aoshin.log");
        }
    }
    PathBuf::from("tft_aoshin.log")
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 算「在打架」：p_sense 以内有敌方英雄；断开不超过 p_quiet tick 接着数；数满 p_delay tick 落雷。
    pub p_sense: u64,
    pub p_delay: usize,
    pub p_quiet: usize,
    /// 落雷：p_r 以内的敌方英雄，最大生命值 p_hp% 的真实伤害、晕眩 p_stun tick；两次至少隔 p_cd tick。
    pub p_r: u64,
    pub p_hp: usize,
    pub p_stun: usize,
    pub p_cd: usize,
    /// 落雷之后他自己：法强 +p_amp%，p_t tick。
    pub p_amp: i32,
    pub p_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_sense: 70000,
            p_delay: 180,
            p_quiet: 120,
            p_r: 85000,
            p_hp: 8,
            p_stun: 50,
            p_amp: 20,
            p_t: 360,
            p_cd: 1500,
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
            "p_sense" => p.p_sense = u as u64,
            "p_delay" => p.p_delay = u.max(1),
            "p_quiet" => p.p_quiet = u,
            "p_r" => p.p_r = u as u64,
            "p_hp" => p.p_hp = u,
            "p_stun" => p.p_stun = u,
            "p_amp" => p.p_amp = v as i32,
            "p_t" => p.p_t = u,
            "p_cd" => p.p_cd = u,
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

/// The fight's clock: how long a fight has gone on and when an enemy champion was last near him.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Clock {
    pub ticks: usize,
    pub last_near: Option<usize>,
}

impl Clock {
    /// One tick: `near` = an enemy champion within p_sense. A lull longer than p_quiet starts the count again.
    pub fn step(&mut self, now: usize, near: bool, p: &Params) {
        let lull = self.last_near.is_none_or(|t| now.saturating_sub(t) > p.p_quiet);
        if lull {
            self.ticks = 0;
        }
        if near {
            self.ticks += 1;
            self.last_near = Some(now);
        }
    }

    /// The storm may fall: the fight long enough and the cooldown over.
    pub fn due(&self, now: usize, ready_at: usize, p: &Params) -> bool {
        self.ticks >= p.p_delay && now >= ready_at
    }
}

/// A bolt's true damage: p_hp% of the champion's maximum health, at least 1.
pub fn bolt_damage(max_hp: usize, p: &Params) -> usize {
    (max_hp * p.p_hp / 100).max(1)
}

/// His storm buff: more ability power for p_t ticks.
pub fn storm_buff(p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(&ao("p_storm"), p.p_t);
    b.magic_power_mult = p.p_amp;
    b
}

// ===================== 被动 =====================

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

/// Live, targetable enemy champions within `reach` of (x, y): (id, max hp).
fn champions(sim: &StableSim<'_>, team: usize, at: (u64, u64), reach: u64) -> Vec<(usize, usize)> {
    let r = (reach as u128) * (reach as u128);
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.team() != team && e.is_alive() && e.is_targetable())
        .filter(|e| matches!(e.kind(), Some(EntityKindV1::Champion)) && dist_sq(e.pos(), at) <= r)
        .map(|e| (e.id(), e.hp().1))
        .collect()
}

#[derive(Clone, Default)]
struct Storm {
    p: Params,
    clock: Clock,
    ready_at: usize,
}

impl Storm {
    fn strike(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize, hit: &[(usize, usize)]) {
        self.ready_at = now + self.p.p_cd;
        self.clock = Clock::default();
        let stun = CcV1::of_kind(CcKindV1::Stun, self.p.p_stun as u64);
        let mut dealt = 0;
        for &(id, max) in hit {
            let d = bolt_damage(max, &self.p);
            sim.deal_damage_typed(me, id, d, DamageTypeV1::Fixed, AttackTypeV1::Skill);
            sim.apply_cc(id, &stun);
            put(sim, id, &BuffV1::timed(&ao("p_bolt"), BOLT_T));
            dealt += d;
        }
        put(sim, me, &storm_buff(&self.p));
        let on_me = InputTargetV1::target(me);
        sim.play_sfx(&ao("p"), me, &on_me);
        sim.play_sfx(&ao("p_bolt"), me, &on_me);
        sim.play_sfx(&ao("p_stun"), me, &InputTargetV1::target(hit[0].0));
        if let Some(k) = counted("storm") {
            wlog(format!(
                "{} STORM #{k}: {} champions struck {:?}, {dealt} true damage, stunned {} ticks; +{}% ap for {} ticks",
                head(sim, me),
                hit.len(),
                hit.iter().map(|h| h.0).collect::<Vec<_>>(),
                self.p.p_stun,
                self.p.p_amp,
                self.p.p_t
            ));
        }
    }
}

impl StablePassive for Storm {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Ao Shin (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        let Some((alive, team, at)) = sim.get_entity(me).map(|e| (e.is_alive(), e.team(), e.pos())) else { return };
        if !alive {
            self.clock = Clock::default();
            return;
        }
        let near = !champions(sim, team, at, self.p.p_sense).is_empty();
        self.clock.step(now, near, &self.p);
        if !self.clock.due(now, self.ready_at, &self.p) {
            return;
        }
        let hit = champions(sim, team, at, self.p.p_r);
        if !hit.is_empty() {
            self.strike(sim, me, now, &hit);
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _me: usize) {
        self.clock = Clock::default();
    }
}

// ===================== 注册 =====================

/// Ao Shin's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Ao Shin: Tempest Might, the storm a few seconds into a fight) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:storm"), Storm::default());
    host.log(LogLevel::Info, "tft.dll: Ao Shin (Tempest Might).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_amp":20,"p_cd":1500,"p_delay":180,"p_hp":8,"p_quiet":120,"p_r":85000,"p_sense":70000,"p_stun":50,"p_t":360}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_fight_clock_counts_through_short_lulls() {
        let p = Params { p_delay: 5, p_quiet: 3, ..Params::default() };
        let mut c = Clock::default();
        for t in 0..3 {
            c.step(t, true, &p);
        }
        assert_eq!(c.ticks, 3);
        c.step(3, false, &p);
        c.step(4, false, &p);
        c.step(5, true, &p);   // 3 ticks after the last: still the same fight
        assert_eq!(c.ticks, 4);
        c.step(6, true, &p);
        assert!(c.due(6, 0, &p));
        assert!(!c.due(6, 100, &p));   // the cooldown
        for t in 7..11 {
            c.step(t, false, &p);
        }
        assert_eq!(c.ticks, 0);   // a long lull: a new fight
        c.step(11, true, &p);
        assert_eq!(c.ticks, 1);
    }

    #[test]
    fn nothing_counts_before_a_champion_comes() {
        let p = Params::default();
        let mut c = Clock::default();
        for t in 0..500 {
            c.step(t, false, &p);
        }
        assert_eq!(c.ticks, 0);
        assert!(!c.due(500, 0, &p));
    }

    #[test]
    fn a_bolt_takes_part_of_the_max_health() {
        let p = Params::default();
        assert_eq!(bolt_damage(2000, &p), 160);
        assert_eq!(bolt_damage(5, &p), 1);
    }

    #[test]
    fn the_storm_buff() {
        let b = storm_buff(&Params::default());
        assert_eq!((b.name(), b.magic_power_mult, b.duration_tick), ("tft_aoshin_p_storm", 20, 360));
    }
}
