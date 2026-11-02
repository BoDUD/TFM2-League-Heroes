//! 慎附加包：「秘奥义！慈悲度魂落」的护盾按慎的最大生命值算（玩家：「I realised Shen ult scales with ad wouldn't it be
//! better if it scaled with hp?」，用户：「这个也要改」，选了「附加包按生命值」）。
//!
//! 数据里的护盾（`Shield`）只有固定值、攻击力和法强的比例，读不到生命值，所以主包是 `r_sh` + `r_sh_ratio`% 攻击力。
//! `mod.override_info` 把主包的慎换成 `override/` 里的副本（tools/kit/build_shen.py 的 native=1）：挑队友、引导、传送都和主包
//! 一样，只是给队友挂 `league_shen_r_shield`（护盾的画面）时不给护盾；本包的被动 `league_shen_shield:shield` 每 tick 看己方
//! 英雄，谁身上刚出现 `league_shen_r_shield`，就给他 `r_sh_base` + 慎最大生命值的 `r_sh_hp`% 的护盾，`r_sh_t` tick
//! （英雄联盟：固定值 + 17.5% 额外生命值）。数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_shen_shield.log`，每次启动游戏重写。

use std::collections::HashSet;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_shen_shield";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_shen_shield") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 主包慎大招给队友挂的 buff（护盾的画面），本包看它出现。
const MARK: &str = "league_shen_r_shield";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SHEN_SHIELD_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_shen_shield.log");
        }
    }
    PathBuf::from("league_shen_shield.log")
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

#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 护盾的固定值。
    pub r_sh_base: usize,
    /// 慎最大生命值的百分之几。
    pub r_sh_hp: usize,
    /// 护盾持续几 tick。
    pub r_sh_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { r_sh_base: 150, r_sh_hp: 12, r_sh_t: 300 }
    }
}

/// `{"r_sh_base":150,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k.trim().trim_matches('"') {
            "r_sh_base" => p.r_sh_base = v,
            "r_sh_hp" => p.r_sh_hp = v,
            "r_sh_t" => p.r_sh_t = v,
            _ => {}
        }
    }
    p
}

/// 护盾量：固定值 + 慎最大生命值的 `r_sh_hp`%。
pub fn amount(p: &Params, shen_max_hp: usize) -> usize {
    p.r_sh_base + shen_max_hp * p.r_sh_hp / 100
}

// ===================== 被动 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 每个慎一份：参数、这 tick 身上有护盾画面的队友（看新出现的）、给过几次。
#[derive(Clone, Default)]
struct Shield {
    p: Params,
    marked: HashSet<usize>,
    given: usize,
}

impl StablePassive for Shield {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.marked.clear();
        wlog(format!("{} SPAWN: the add-on's Shen (player {player}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, max_hp) = (e.team(), e.hp().1);
        let mut now = HashSet::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.is_champion() && u.team() == team && u.is_alive() {
                now.insert(u.id());
            }
        }
        now.retain(|&id| has_buff(sim, id, MARK));
        for &id in now.difference(&self.marked).copied().collect::<Vec<_>>().iter() {
            let n = amount(&self.p, max_hp);
            let ok = sim.entity_add_shield(id, n, self.p.r_sh_t);
            self.given += 1;
            wlog(format!("{} SHIELD #{} on #{id}: {n} ({} + {}% of {max_hp}) for {} ticks{}", head(sim, me), self.given,
                         self.p.r_sh_base, self.p.r_sh_hp, self.p.r_sh_t, if ok { "" } else { " - refused by the game" }));
        }
        self.marked = now;
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {}
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Shen's Stand United shield from his maximum health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:shield"), Shield::default());
    host.log(LogLevel::Info, "league_shen_shield loaded (Shen's ult shield from his maximum health).");
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
    fn the_shield_follows_his_health() {
        let p = Params::default();
        assert_eq!(amount(&p, 1200), 150 + 144);
        assert_eq!(amount(&p, 3000), 150 + 360);
    }

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"r_sh_base": 140, "r_sh_hp": 15, "r_sh_t": 280}"#);
        assert_eq!(p, Params { r_sh_base: 140, r_sh_hp: 15, r_sh_t: 280 });
        assert_eq!(parse_params("{}"), Params::default());
    }
}
