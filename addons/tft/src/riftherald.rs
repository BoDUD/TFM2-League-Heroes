//! 峡谷先锋（`tft_riftherald`）数据做不到的部分（金铲铲第 16 赛季的虚空四费，技能按用户定的方案，上单，2026-11-02）。
//! 它的数据（tools/kit/build_riftherald.py）的 `passive` 是这里的 `tft_riftherald:shell`，参数从数据的 `passive.params`
//! 来（build_riftherald.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **虚空甲壳**：每 `CHECK` 拍数一次 `p_r` 以内（加上身子）活着的敌方英雄，最多算 `p_max` 个，每个让它受到的伤害少
//!   `p_dr`%；大招「扭曲护甲」的 `tft_riftherald_r_armor` 在身上时每个再多 `r_per`%（金铲铲「每有一个敌人以它为目标，
//!   伤害减免 +1%」）。挂成 `tft_riftherald_p_shell`（`damaged_reduce`，2 个 `CHECK` 长，每次刷新，死了就没了）。
//!   数据数不了身边有几个敌人（--plain 的数据从它的第一个动作挂上固定的 `p_plain`%）。
//! - **死亡**：倒下时播 `tft_riftherald_d`。
//!
//! 裂钳、回旋横扫、虚空冲锋、扭曲护甲（长啸变大、猛击、护甲）是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_riftherald.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_riftherald";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// How often (ticks) the passive counts the enemy champions near it.
const CHECK: usize = 15;
/// A unit's body (its collision radius, about): the reach counts it, as the data's circles do.
const BODY: u64 = 15000;

fn rh(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_RIFTHERALD_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_riftherald.log");
        }
    }
    PathBuf::from("tft_riftherald.log")
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
    /// 虚空甲壳：p_r 以内（加上身子）的敌方英雄。
    pub p_r: usize,
    /// 每个少 p_dr% 伤害，最多算 p_max 个。
    pub p_dr: usize,
    pub p_max: usize,
    /// 扭曲护甲（r_armor）在身上时每个再多 r_per%。
    pub r_per: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_r: 45000,
            p_dr: 4,
            p_max: 5,
            r_per: 3,
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
            "p_r" => p.p_r = u,
            "p_dr" => p.p_dr = u.min(100),
            "p_max" => p.p_max = u,
            "r_per" => p.r_per = u.min(100),
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// The shell's strength: p_dr% (and r_per% more under Warp Armor) for each of at most p_max enemy champions, never
/// over 90%.
pub fn shell_pct(near: usize, armored: bool, p: &Params) -> usize {
    let each = p.p_dr + if armored { p.r_per } else { 0 };
    (near.min(p.p_max) * each).min(90)
}

/// The shell buff for `pct`% less damage, lasting two checks (refreshed every check, gone soon after death).
pub fn shell_buff(pct: usize) -> BuffV1 {
    let mut b = BuffV1::timed(&rh("p_shell"), CHECK * 2);
    b.damaged_reduce = pct;
    b
}

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

// ===================== 场上 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

// ===================== 被动：虚空甲壳 =====================

#[derive(Clone, Default)]
struct Shell {
    /// The champion it belongs to (on_dead is given the player, not the unit).
    me: usize,
    p: Params,
    /// The strength put on at the last check (logged when it changes).
    last: usize,
}

impl StablePassive for Shell {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.last = 0;
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Rift Herald (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if sim.tick() % CHECK != 0 {
            return;
        }
        let Some((at, team)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.pos(), e.team())) else {
            return;
        };
        let reach = (self.p.p_r as u64 + BODY) as u128;
        let near = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive() && u.is_champion())
            .filter(|u| dist_sq(u.pos(), at) <= reach * reach)
            .count();
        let armored = has_buff(sim, me, &rh("r_armor"));
        let pct = shell_pct(near, armored, &self.p);
        if pct > 0 {
            put(sim, me, &shell_buff(pct));
        } else if self.last > 0 {
            sim.entity_remove_buff(me, &rh("p_shell"));
        }
        if pct != self.last {
            if let Some(k) = counted("shell") {
                wlog(format!("{} SHELL #{k}: {near} enemy champions near{} -> {pct}% less damage (was {}%)",
                             head(sim, me), if armored { ", warp armor" } else { "" }, self.last));
            }
            self.last = pct;
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        let me = self.me;
        self.last = 0;
        // its collapse (the data has no moment for it)
        sim.play_sfx(&rh("d"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("dead") {
            wlog(format!("{} DEAD #{k}: {}", head(sim, me), name_of(sim, me)));
        }
    }
}

// ===================== 注册 =====================

/// The Rift Herald's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Rift Herald: the void shell) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:shell"), Shell::default());
    host.log(LogLevel::Info, "tft.dll: Rift Herald (void shell).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_r":45000,"p_dr":4,"p_max":5,"r_per":3}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_shell_counts_enemies_up_to_the_cap() {
        let p = Params::default();
        assert_eq!(shell_pct(0, false, &p), 0);
        assert_eq!(shell_pct(1, false, &p), 4);
        assert_eq!(shell_pct(3, false, &p), 12);
        assert_eq!(shell_pct(5, false, &p), 20);
        assert_eq!(shell_pct(9, false, &p), 20);
        assert_eq!(shell_pct(3, true, &p), 21);
        assert_eq!(shell_pct(5, true, &p), 35);
    }

    #[test]
    fn the_shell_buff_is_short_and_named() {
        let b = shell_buff(12);
        assert_eq!((b.name(), b.damaged_reduce), ("tft_riftherald_p_shell", 12));
    }
}
