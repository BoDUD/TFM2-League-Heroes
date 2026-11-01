//! 约里克附加包：数据做不到、和英雄联盟不一样的地方，这里照英雄联盟做。
//!
//! `mod.override_info` 把主包的约里克换成 `override/` 里的副本（tools/kit/build_yorick.py --native），`passive` 换成本包的
//! `league_yorick:shepherd`：
//!
//! - **坟墓照英雄联盟挖**：主包读不到「这一铲打死了谁」，所以临终仪式打英雄挖一座坟、打别的每两下挖一座。副本的这一铲给
//!   约里克挂几拍 `league_yorick_q_win`，本包在它还在时，每有一个小兵 / 野怪被他打死就挖一座坟（打英雄照旧由数据挖），
//!   不再「每两下」。
//! - **室女的加伤只打她的目标**：主包读不到「室女跟着谁」，所以室女在场时约里克普攻任何英雄都加伤。副本给室女的目标挂
//!   `league_yorick_maiden`，普攻打中英雄时给它挂 3 拍 `league_yorick_hit`；本包看到同时有这两个的英雄，才造成它最大生命
//!   `r_pct`% 的真实伤害。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。不用全局变量，服务端预模拟和
//! 你看的那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yorick.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_yorick";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_yorick") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// On him for a few ticks after a Last Rites blow: a unit dying meanwhile died to it.
const Q_WIN: &str = "league_yorick_q_win";
/// On the Maiden's champion while she stands.
const MAIDEN: &str = "league_yorick_maiden";
/// On a champion his attack struck while she stands (3 ticks).
const HIT: &str = "league_yorick_hit";
/// His graves, counted on him (the data's ladder: the first g1, then g2, then g3; the Awakening takes them off).
const GRAVES: [&str; 3] = ["league_yorick_g1", "league_yorick_g2", "league_yorick_g3"];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_YORICK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_yorick.log");
        }
    }
    PathBuf::from("league_yorick.log")
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

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).unwrap_or_else(|| format!("#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 室女的目标被约里克普攻打中时，额外受到它最大生命的这么多百分比（真实伤害）。
    pub r_pct: usize,
    /// 一座坟留多少拍（数据的 g1..g3 一样长）。
    pub g_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { r_pct: 3, g_t: 1800 }
    }
}

/// `{"g_t":1800,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "r_pct" => p.r_pct = v,
            "g_t" => p.g_t = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

/// The Maiden's bonus on her target: r_pct% of its maximum health (at least 1).
pub fn maiden_bonus(p: &Params, max_hp: usize) -> usize {
    (max_hp * p.r_pct / 100).max(1)
}

/// Which grave flag a new grave raises, given which he has (the data's ladder): g1, then g2, then g3; None when full.
pub fn next_grave(has: [bool; 3]) -> Option<usize> {
    match has {
        [_, _, true] => None,
        [_, true, _] => Some(2),
        [true, _, _] => Some(1),
        _ => Some(0),
    }
}

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

// ===================== 被动 =====================

/// 每个约里克一份：参数和日志计数。
#[derive(Clone, Default)]
struct Shepherd {
    p: Params,
    graves: usize,
    bonuses: usize,
}

impl Shepherd {
    /// A unit died to Last Rites: one grave more (the data's ladder; full graves stay full).
    fn dig(&mut self, sim: &mut StableSim<'_>, me: usize, victim: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !has(&e, Q_WIN) {
            return;
        }
        let Some(k) = next_grave([has(&e, GRAVES[0]), has(&e, GRAVES[1]), has(&e, GRAVES[2])]) else { return };
        sim.entity_remove_buff(me, GRAVES[k]);
        sim.add_buff(me, &BuffV1::timed(GRAVES[k], self.p.g_t));
        self.graves += 1;
        if self.graves <= 40 || self.graves % 100 == 0 {
            wlog(format!("{} GRAVE {} died to Last Rites: grave {} ({} in all)", head(sim, me), name_of(sim, victim),
                         k + 1, self.graves));
        }
    }

    /// His attacks on the Maiden's own target: the bonus, once a hit.
    fn maiden(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let ids: Vec<usize> = (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).collect();
        for id in ids {
            let Some(c) = sim.get_entity(id) else { continue };
            if c.team() == team || !c.is_alive() || !has(&c, HIT) {
                continue;
            }
            let target = has(&c, MAIDEN);
            let max_hp = c.hp().1;
            sim.entity_remove_buff(id, HIT);
            if !target {
                continue;
            }
            let dmg = maiden_bonus(&self.p, max_hp);
            sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Fixed, AttackTypeV1::Skill);
            self.bonuses += 1;
            if self.bonuses <= 40 || self.bonuses % 100 == 0 {
                wlog(format!("{} MAIDEN bonus {dmg} on her target {} ({} in all)", head(sim, me), name_of(sim, id),
                             self.bonuses));
            }
        }
    }
}

impl StablePassive for Shepherd {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Yorick (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        // a minion or a camp (a champion hit digs its own grave in the data)
        self.dig(sim, me, victim);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            self.maiden(sim, me);
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (graves from kills, the Maiden's bonus on her target) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:shepherd"), Shepherd::default());
    host.log(LogLevel::Info, "league_yorick loaded (graves from kills, the Maiden's bonus on her target).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"g_t":1200,"r_pct":5,"x":1}"#);
        assert_eq!(p, Params { r_pct: 5, g_t: 1200 });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_graves_climb_the_data_s_ladder() {
        assert_eq!(next_grave([false, false, false]), Some(0));
        assert_eq!(next_grave([true, false, false]), Some(1));
        assert_eq!(next_grave([true, true, false]), Some(2));
        assert_eq!(next_grave([false, true, false]), Some(2)); // g1 ran out first: the ladder goes on from g2
        assert_eq!(next_grave([true, true, true]), None);
    }

    #[test]
    fn the_maiden_s_bonus_is_a_share_of_max_health() {
        let p = Params::default();
        assert_eq!(maiden_bonus(&p, 2000), 60);
        assert_eq!(maiden_bonus(&p, 10), 1);
    }

    #[test]
    fn names_are_the_data_s() {
        for n in [Q_WIN, MAIDEN, HIT].iter().chain(GRAVES.iter()) {
            assert!(n.starts_with("league_yorick_"), "{n}");
        }
    }
}
