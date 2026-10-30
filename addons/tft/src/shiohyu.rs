//! 石傲玉（`tft_shiohyu`）数据做不到的部分（金铲铲第 7 赛季的玉龙 / 秘术师 / 龙神，技能按用户选的方案 A「玉龙三连」，
//! 2026-10-30）。他的数据（tools/kit/build_shiohyu.py）的 `passive` 是这里的 `tft_shiohyu:jade`，参数从数据的
//! `passive.params` 来（build_shiohyu.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **玉石之肤**：生命掉到最大生命的 `p_low`% 以下、且冷却 `p_cd` 拍已过（每条命一开始就是好的）时，全身化作玉石：
//!   `p_t` 拍内受到的伤害减少 `p_red`%（挂 `tft_shiohyu_p_skin`，带画面），亮一下 `tft_shiohyu_p`，播 `tft_shiohyu_sfx_p`。
//!   数据读不到生命，所以由本被动每拍看他的生命。
//! - **死亡**：倒下时播 `tft_shiohyu_sfx_d`（数据没有死亡的时机）。
//!
//! 龙爪三连、玉拳连打、震地和玉龙形态（减伤免控、三记强化攻击）是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_shiohyu.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_shiohyu";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// The skin's sound and his death cry (the tft pack's sound_info; the rest of his sounds the data plays).
const SFX_SKIN: &str = "tft_shiohyu_sfx_p";
const SFX_DEAD: &str = "tft_shiohyu_sfx_d";

fn sy(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_SHIOHYU_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_shiohyu.log");
        }
    }
    PathBuf::from("tft_shiohyu.log")
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
    /// 玉石之肤：生命低于 p_low% 时 p_t 拍内受到的伤害减少 p_red%；之后 p_cd 拍内不再有。
    pub p_low: usize,
    pub p_red: usize,
    pub p_t: usize,
    pub p_cd: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_low: 50,
            p_red: 40,
            p_t: 180,
            p_cd: 1800,
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
            "p_low" => p.p_low = u.min(100),
            "p_red" => p.p_red = u.min(100),
            "p_t" => p.p_t = u,
            "p_cd" => p.p_cd = u,
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// The skin is due: alive, under p_low% of his maximum health, and `ready` (the cooldown over).
pub fn due(hp: usize, max: usize, ready: bool, p: &Params) -> bool {
    ready && hp > 0 && max > 0 && hp * 100 < max * p.p_low
}

/// The jade skin: p_red% less damage taken for p_t ticks.
pub fn skin_buff(p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(&sy("p_skin"), p.p_t);
    b.damaged_reduce = p.p_red;
    b
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Jade {
    p: Params,
    /// The tick the skin is ready again (0: ready), and whether he was alive last tick (a respawn makes it ready).
    ready_at: usize,
    was_alive: bool,
}

impl StablePassive for Jade {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Shi Oh Yu (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((alive, (hp, max))) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp())) else { return };
        if alive && !self.was_alive {   // the first tick of a life: the skin is ready
            self.ready_at = 0;
        }
        self.was_alive = alive;
        if !alive || !due(hp, max, sim.tick() >= self.ready_at, &self.p) {
            return;
        }
        let b = skin_buff(&self.p);
        sim.entity_remove_buff(me, b.name());
        sim.add_buff(me, &b);
        sim.play_view_effect(&sy("p"), me, &InputTargetV1::target(me), 0, 0, 0);
        sim.play_sfx(SFX_SKIN, me, &InputTargetV1::target(me));
        self.ready_at = sim.tick() + self.p.p_cd;
        if let Some(k) = counted("skin") {
            wlog(format!("{} SKIN #{k}: hp {hp}/{max}, {}% less damage for {} ticks", head(sim, me), self.p.p_red,
                         self.p.p_t));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        // his death cry (the data has no moment for it)
        sim.play_sfx(SFX_DEAD, me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// Shi Oh Yu's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Shi Oh Yu: the jade skin at low health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:jade"), Jade::default());
    host.log(LogLevel::Info, "tft.dll: Shi Oh Yu (the jade skin).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_cd":1800,"p_low":50,"p_red":40,"p_t":180}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_skin_under_half_when_ready() {
        let p = Params::default();
        assert!(!due(500, 1000, true, &p));
        assert!(due(499, 1000, true, &p));
        assert!(!due(499, 1000, false, &p));
        assert!(!due(0, 1000, true, &p));
        assert!(!due(10, 0, true, &p));
    }

    #[test]
    fn the_skin_buff() {
        let b = skin_buff(&Params::default());
        assert_eq!((b.name(), b.damaged_reduce, b.duration_tick), ("tft_shiohyu_p_skin", 40, 180));
    }
}
