//! 阿萝拉附加包：被动里的「灵纱洞开」按真实的生命触发（英雄联盟的用户要的「残血时跳开」）。
//!
//! 主包保持纯数据：数据读不到生命，主包里阿萝拉的灵纱洞开是「有敌方英雄贴身」就后跳（隐身、加速，`w_cd` 一次）。
//! `mod.override_info` 把主包的阿萝拉换成 `override/` 里的副本（tools/kit/build_aurora.py --native）：后跳还要她身上有
//! `league_aurora_low`，`passive` 换成本包的 `league_aurora:veil`：
//!
//! - 每 tick 读她的生命：低于最大生命的 `w_low`% 就挂上 3 tick 的 `league_aurora_low`（先摘再挂，只留一个），
//!   回到 `w_low`% 以上就不再挂，3 tick 后自己消失。数据在普攻和怪奇喷涌的开头读它（还要敌方英雄在 `w_near` 内、
//!   `w_cd` 已过）。
//!
//! 大招的时机由 AI 钩子 `league_aurora:realm` 挑（`realm.rs`：开团关住一堆人、关住想跑的残血、被贴脸时砸下去，其余时候按住）。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。不用全局变量，服务端预模拟和
//! 你看的那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aurora.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod realm;

const ID: &str = "league_aurora";
/// The flag the data's veil reads (build_aurora.py: `sw("low", hop)`).
const LOW: &str = "league_aurora_low";
/// Ticks the flag lasts: renewed every tick while she is low, gone 3 ticks after she is not.
const LOW_TICKS: usize = 3;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// The first this many lines of a kind, then every LOG_EVERY-th.
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AURORA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_aurora.log");
        }
    }
    PathBuf::from("league_aurora.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (league_olaf_rage's lesson: opening it for every line stalled the simulation thread)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// Counts a line of this kind; Some(n) when it is to be written.
fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{kind} m={} s={}] t={} #{id}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 生命低于最大生命的这个百分比算「残血」。
    pub w_low: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { w_low: 35 }
    }
}

/// `{"w_low":35}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        if k == "w_low" {
            p.w_low = v;
        }
    }
    p
}

// ===================== 计算 =====================

/// Is she low: health under w_low% of her maximum (a unit with no maximum never is).
pub fn is_low(p: &Params, hp: usize, max: usize) -> bool {
    max > 0 && hp * 100 < p.w_low * max
}

// ===================== 被动 =====================

/// 每个阿萝拉一份：参数、上一 tick 是不是残血（只为日志）。
#[derive(Clone, Default)]
struct Veil {
    p: Params,
    low: bool,
    turns: usize,
}

impl StablePassive for Veil {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.low = false;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Aurora (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let (hp, max) = e.hp();
        let low = is_low(&self.p, hp, max);
        if low {
            sim.entity_remove_buff(me, LOW);
            sim.add_buff(me, &BuffV1::timed(LOW, LOW_TICKS));
        }
        if low != self.low {
            self.turns += 1;
            if self.turns <= 40 || self.turns % 100 == 0 {
                wlog(format!("{} {}: hp {hp}/{max} ({}%)", head(sim, me), if low { "LOW" } else { "UP" },
                             hp * 100 / max.max(1)));
            }
            self.low = low;
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        // death clears the buffs; the next life starts at full health
        self.low = false;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    COUNTS.lock().unwrap_or_else(|e| e.into_inner()).clear();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v2 (Across the Veil at low health, the realm's timing) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:veil"), Veil::default());
    module.add_player_input_ai(realm::Realm::default());
    host.log(LogLevel::Info, "league_aurora v2 loaded (Aurora's Across the Veil reads her health, her R waits for its moment).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"w_low":30,"x":1}"#), Params { w_low: 30 });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn low_is_under_the_threshold() {
        let p = Params::default();
        assert!(!is_low(&p, 1000, 1000));
        assert!(!is_low(&p, 350, 1000));
        assert!(is_low(&p, 349, 1000));
        assert!(is_low(&p, 1, 1000));
        assert!(!is_low(&p, 0, 0));
    }

    #[test]
    fn the_flag_is_the_one_the_data_reads() {
        assert_eq!(BuffV1::timed(LOW, LOW_TICKS).name(), "league_aurora_low");
    }
}
