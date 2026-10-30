//! 泰拉（`tft_terra`）数据做不到的部分（金铲铲第 7 赛季的大地巨龙 / 巨岩龙 / 龙神，技能按用户选的方案 A「地震巨岩」，
//! 2026-10-31）。她的数据（tools/kit/build_terra.py）的 `passive` 是这里的 `tft_terra:monolith`，参数从数据的
//! `passive.params` 来（build_terra.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **巨岩之躯**：每条命一开始（和每 `CHECK` 拍看一次，没了就补上）挂上永久的 `tft_terra_p_rock`：受到的伤害减少
//!   `p_red`%（金铲铲的巨岩格）。数据没有一条命开始的时机。
//! - **裂地咬**（`tft_terra:q_bite`）和**地震**每一踏（`tft_terra:r_quake`）：数据的伤害只按攻击力算，这里在同一下上补
//!   她护甲 + 魔抗的 `q_def`% / `r_def`%（物理伤害，技能），读的是她当时的属性（地震之后的岩甲也算）。
//! - **死亡**：倒下时播 `tft_terra_d`（数据没有死亡的时机）。
//!
//! 岩爪、裂地咬的扑咬和减速、龙威咆哮（嘲讽 + 岩石护盾）和地震的三踏、免控、岩甲是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_terra.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_terra";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// How often (ticks) the passive looks whether the hide is still on her.
const CHECK: usize = 30;

fn te(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_TERRA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_terra.log");
        }
    }
    PathBuf::from("tft_terra.log")
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
    /// 巨岩之躯：受到的伤害减少 p_red%。
    pub p_red: usize,
    /// 裂地咬、地震每一踏补上的：她护甲 + 魔抗的 q_def% / r_def%。
    pub q_def: usize,
    pub r_def: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_red: 18,
            q_def: 50,
            r_def: 32,
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
            "p_red" => p.p_red = u.min(100),
            "q_def" => p.q_def = u,
            "r_def" => p.r_def = u,
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

/// The hide: p_red% less damage taken, for good.
pub fn hide_buff(p: &Params) -> BuffV1 {
    let mut b = BuffV1::named(&te("p_rock"));
    b.damaged_reduce = p.p_red;
    b
}

/// The armour part of a hit: pct% of her armour + magic resistance.
pub fn rock_damage(defence: usize, resistance: usize, pct: usize) -> usize {
    (defence + resistance) * pct / 100
}

// ===================== 场上 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// The armour part on the hit unit (`kind` names the log line).
fn rock_hit(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1, pct: usize, kind: &'static str) {
    if input.kind != InputTargetKindV1::Target.code() {
        if let Some(k) = counted("rock_none") {
            wlog(format!("{} {kind} NONE #{k}: no unit to hit (input kind {})", head(sim, me), input.kind));
        }
        return;
    }
    let id = input.target_id;
    let Some(s) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.stat()) else { return };
    if !sim.get_entity(id).is_some_and(|e| e.is_alive()) {
        return;
    }
    let d = rock_damage(s.defence, s.magic_resistance, pct);
    if d > 0 {
        sim.deal_damage_typed(me, id, d, DamageTypeV1::Ad, AttackTypeV1::Skill);
    }
    if let Some(k) = counted(kind) {
        wlog(format!("{} {kind} #{k}: {} takes {d} more ({pct}% of armour {} + magic resistance {})", head(sim, me),
                     name_of(sim, id), s.defence, s.magic_resistance));
    }
}

/// Rending Bite's armour part.
struct QBite;
impl StableEffectType for QBite {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let pct = params_of(me).q_def;
        rock_hit(sim, me, input, pct, "BITE");
    }
}

/// One Earthquake stomp's armour part (on each enemy in the ring).
struct RQuake;
impl StableEffectType for RQuake {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let pct = params_of(me).r_def;
        rock_hit(sim, me, input, pct, "QUAKE");
    }
}

// ===================== 被动：巨岩之躯 =====================

#[derive(Clone, Default)]
struct Monolith {
    p: Params,
    /// Whether she was alive last tick (a new life puts the hide on at once).
    was_alive: bool,
}

impl StablePassive for Monolith {
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
            wlog(format!("{} SPAWN #{k}: tft.dll's Terra (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        let new_life = alive && !self.was_alive;
        self.was_alive = alive;
        if !alive || !(new_life || sim.tick() % CHECK == 0) {
            return;
        }
        let b = hide_buff(&self.p);
        if has_buff(sim, me, b.name()) {
            return;
        }
        sim.add_buff(me, &b);
        if let Some(k) = counted("hide") {
            wlog(format!("{} HIDE #{k}: {}% less damage taken{}", head(sim, me), self.p.p_red,
                         if new_life { " (a new life)" } else { " (was gone)" }));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        // her death cry (the data has no moment for it)
        sim.play_sfx(&te("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// Terra's passive and the armour part of her bite and quake, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Terra: the Monolith hide, armour-scaled bite and quake) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:monolith"), Monolith::default());
    module.add_native_effect(format!("{ID}:q_bite"), QBite);
    module.add_native_effect(format!("{ID}:r_quake"), RQuake);
    host.log(LogLevel::Info, "tft.dll: Terra (Monolith hide, Rending Bite, Earthquake).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_red":18,"q_def":50,"r_def":32}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_hide_is_permanent() {
        let b = hide_buff(&Params::default());
        assert_eq!((b.name(), b.damaged_reduce, b.duration_kind), ("tft_terra_p_rock", 18,
                                                                  BuffDurationV1::Permanent.code()));
    }

    #[test]
    fn the_armour_part() {
        assert_eq!(rock_damage(150, 110, 40), 104);
        assert_eq!(rock_damage(150, 110, 25), 65);
        assert_eq!(rock_damage(0, 0, 40), 0);
    }
}
