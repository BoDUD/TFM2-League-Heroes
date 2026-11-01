//! 蔚奥莱（`tft_violet`）数据做不到的部分（金铲铲第 13 赛季的家人 / 搏击手，技能和被动按用户选的方案 A「搏击手·1-2-3连招」，
//! 2026-10-28）。她的数据（tools/kit/build_violet.py）的 `passive` 是这里的 `tft_violet:pugilist`，参数从数据的
//! `passive.params` 来（build_violet.py 从参数表 P 写进去，`NATIVE_KEYS`），按她的单位编号记一份给效果用：
//!
//! - **搏击手的回气**：数据读不到生命。被动每拍看她的生命，每条命第一次掉到 `p_line`% 以下：挂上 `tft_violet_p_wind`
//!   `p_t` 拍，这段时间一共回 `p_heal`% 最大生命（每秒回复），亮一下 `p_burst`、出一声。
//! - **底城怒拳的怒火**（`tft_violet:fury`：砸地时）：攻速 +`r_as`%、吸血 +`r_vamp`%，`r_t` 拍；她队里每有一个家人（爆爆
//!   `tft_powder`、范德尔 `tft_vander`、金克丝 `league_jinx`），攻速再加 `r_fam`%。
//!
//! 额外真实伤害和全能吸血、1-2-3连招、冲拳和跳起砸地是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_violet.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_violet";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 家人：金铲铲第 13 赛季的【家人】是爆爆、蔚奥莱、范德尔（金克丝是长大的爆爆；蔚是长大的她自己，不算）。
const FAMILY: [&str; 3] = ["tft_powder", "tft_vander", "league_jinx"];
/// The second wind's sound (the tft pack's sound_info; the rest of her sounds the data plays).
const SFX_WIND: &str = "tft_violet_p";

fn vo(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_VIOLET_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_violet.log");
        }
    }
    PathBuf::from("tft_violet.log")
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
    /// 回气：每条命第一次掉到 p_line% 以下，p_t 拍里一共回 p_heal% 最大生命。
    pub p_line: usize,
    pub p_heal: usize,
    pub p_t: usize,
    /// 怒火：攻速、吸血、每个家人再加的攻速、几拍。
    pub r_as: usize,
    pub r_vamp: usize,
    pub r_fam: usize,
    pub r_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_line: 50,
            p_heal: 15,
            p_t: 120,
            r_as: 40,
            r_vamp: 5,
            r_fam: 10,
            r_t: 300,
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
            "p_line" => p.p_line = u.min(100),
            "p_heal" => p.p_heal = u.min(100),
            "p_t" => p.p_t = u.max(1),
            "r_as" => p.r_as = u,
            "r_vamp" => p.r_vamp = u.min(100),
            "r_fam" => p.r_fam = u,
            "r_t" => p.r_t = u,
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

/// Whether the second wind starts now: under `line`% of `max` and not used yet this life.
pub fn winds(hp: usize, max: usize, line: usize, used: bool) -> bool {
    !used && max > 0 && hp * 100 < max * line
}

/// The second wind's buff: p_heal% of max health over p_t ticks, as health per second (hp_regen), at least 1.
pub fn wind_buff(max: usize, p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(&vo("p_wind"), p.p_t);
    b.hp_regen = ((max * p.p_heal * 60) / (100 * p.p_t.max(1))).max(1) as i32;
    b
}

/// 队里的家人有几个（不算她自己）。
pub fn family_count<'a>(names: impl IntoIterator<Item = &'a str>) -> usize {
    names.into_iter().filter(|n| FAMILY.contains(n)).count()
}

/// The fury's buff: r_as% attack speed (+ r_fam% a Family ally) and r_vamp% omnivamp for r_t ticks.
pub fn fury_buff(family: usize, p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(&vo("r_fury"), p.r_t);
    b.attack_speed_mult = (p.r_as + family * p.r_fam) as i32;
    b.vamp = p.r_vamp as i32;
    b
}

// ===================== 游戏里 =====================

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

/// 她这一队的英雄（不算她自己）的名字。
fn team_names(sim: &StableSim<'_>, me: usize) -> Vec<String> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.champion_count())
        .map(|i| sim.champion_id_at(i))
        .filter(|&id| id != me)
        .filter_map(|id| sim.get_entity(id))
        .filter(|c| c.team() == team)
        .filter_map(|c| c.name())
        .collect()
}

struct Fury;
impl StableEffectType for Fury {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        let p = params_of(me);
        let family = family_count(team_names(sim, me).iter().map(String::as_str));
        let fury = fury_buff(family, &p);
        put(sim, me, &fury);
        if let Some(k) = counted("fury") {
            wlog(format!("{} FURY #{k}: {family} family on the team, +{}% attack speed, {}% vamp for {} ticks",
                         head(sim, me), fury.attack_speed_mult, fury.vamp, p.r_t));
        }
    }
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Pugilist {
    p: Params,
    /// The second wind used this life, and whether she was alive last tick (a respawn starts it over).
    used: bool,
    was_alive: bool,
}

impl StablePassive for Pugilist {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // a new life is a new unit, and on_update does not run while it is dead: the first tick of this life
        // must see a dead one, or what each life has once stays used up (2026-11-02 logs)
        self.was_alive = false;
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            let family = family_count(team_names(sim, me).iter().map(String::as_str));
            wlog(format!("{} SPAWN #{k}: tft.dll's Violet (player {player}, team {team}, {family} family), {:?}",
                         head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((alive, (hp, max))) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp())) else { return };
        if alive && !self.was_alive {   // the first tick of a life: the second wind is back
            self.used = false;
        }
        self.was_alive = alive;
        if !alive || !winds(hp, max, self.p.p_line, self.used) {
            return;
        }
        self.used = true;
        let wind = wind_buff(max, &self.p);
        put(sim, me, &wind);
        let on = InputTargetV1::target(me);
        sim.play_view_effect(&vo("p_burst"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_WIND, me, &on);
        if let Some(k) = counted("wind") {
            wlog(format!("{} WIND #{k}: {hp}/{max} under {}%: {} health a second for {} ticks", head(sim, me),
                         self.p.p_line, wind.hp_regen, self.p.p_t));
        }
    }
}

// ===================== 注册 =====================

/// Violet's passive and her fury, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Violet: the Pit Fighter's second wind at half health, the fury's Family bonus) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:pugilist"), Pugilist::default());
    module.add_native_effect(format!("{ID}:fury"), Fury);
    host.log(LogLevel::Info, "tft.dll: Violet (Pit Fighter, Undercity Fist's fury).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_heal":15,"p_line":50,"p_t":120,"r_as":40,"r_fam":10,"r_t":300,"r_vamp":5}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_second_wind_once_a_life() {
        assert!(!winds(600, 1000, 50, false));
        assert!(!winds(500, 1000, 50, false));
        assert!(winds(499, 1000, 50, false));
        assert!(!winds(499, 1000, 50, true));
        assert!(!winds(0, 0, 50, false));
    }

    #[test]
    fn the_second_wind_heals_its_share() {
        let p = Params::default();
        let b = wind_buff(1200, &p);
        assert_eq!(b.name(), "tft_violet_p_wind");
        // 15% of 1200 = 180 over 2 s
        assert_eq!(b.hp_regen, 90);
        assert_eq!(b.duration_tick, 120);
        assert_eq!(wind_buff(1, &p).hp_regen, 1);
    }

    #[test]
    fn her_family_only() {
        assert_eq!(family_count(["tft_powder", "tft_vander", "league_garen"]), 2);
        assert_eq!(family_count(["league_jinx"]), 1);
        // grown-up Vi is herself
        assert_eq!(family_count(["league_vi", "tft_silco"]), 0);
    }

    #[test]
    fn the_fury_grows_with_the_family() {
        let p = Params::default();
        assert_eq!((fury_buff(0, &p).attack_speed_mult, fury_buff(0, &p).vamp), (40, 5));
        assert_eq!(fury_buff(2, &p).attack_speed_mult, 60);
        assert_eq!(fury_buff(0, &p).duration_tick, 300);
    }
}
