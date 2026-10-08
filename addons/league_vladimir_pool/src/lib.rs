//! 弗拉基米尔附加包：W「血红之池」在快没血时自动开（用户：「危险信号 + 现在就做扩展包」）。
//!
//! 主包保持纯数据：数据读不到当前生命，主包的血池由普攻里的「危险信号」开——两名以上敌方英雄贴身，或连续两次检查
//! 都挨了打（`league_vladimir_w_go`）；血池本身是数据：他身上一直跑着一个每 3 tick 看一次的轮询（`AddCasted`），
//! 看到 `w_go` 就化成血池（不可选取、减速吸血、`w_cd` 冷却）。
//! `mod.override_info` 把主包的弗拉基米尔换成 `override/` 里的副本：普攻里的危险信号去掉，`passive` 换成本包的
//! `league_vladimir_pool:guard`，由它读生命：
//!
//! - 活着、没被控住、身边 `near` 内有敌方英雄、血池不在冷却（`w_cd`）、不在池里（`w_in`）、生命低于 `hp`%——
//!   加上 `w_go`（30 tick），数据的轮询最多 3 tick 后开池（每 tick 看一次，挨打时 `on_damaged` 当场再看一次）。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从 tools/kit/build_vladimir.py 的参数表 P 写进去：
//! `n_hp`、`n_near`），本包不另记一份。不用全局变量，服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_vladimir_pool.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_vladimir_pool";

/// 主包弗拉基米尔的名字（buff 都以它开头）。
fn vl(x: &str) -> String {
    format!("league_vladimir_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VLADIMIR_POOL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_vladimir_pool.log");
        }
    }
    PathBuf::from("league_vladimir_pool.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
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

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 生命低于 `hp`% 时开池。
    pub hp: usize,
    /// 身边这么近有敌方英雄才开。
    pub near: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { hp: 35, near: 60_000 }
    }
}

/// `{"hp":35,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "hp" => &mut p.hp,
            "near" => &mut p.near,
            _ => continue,
        };
        *slot = v;
    }
    p
}

// ===================== 判断 =====================

/// 这一 tick 看到的。
#[derive(Clone, Copy, Debug, Default)]
pub struct Now {
    pub hp: f64,
    pub enemy_near: bool,
    pub controlled: bool,
    /// 血池在冷却、已经在池里，或已经叫过（`w_go` 还在）。
    pub busy: bool,
}

/// 现在该不该开池。
pub fn want_pool(p: &Params, n: &Now) -> bool {
    !n.busy && !n.controlled && n.enemy_near && n.hp < p.hp as f64
}

// ===================== 小工具 =====================

fn buff_names(sim: &StableSim<'_>, id: usize) -> Vec<String> {
    sim.get_entity(id)
        .map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect())
}

/// 打断施法的控制（英雄联盟里被控住时放不了 W）。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];

fn controlled(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id)
        .is_some_and(|e| (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| NO_CAST.iter().any(|k| k.code() == c.kind))))
}

fn enemy_near(sim: &StableSim<'_>, me: usize, team: usize, near: usize) -> bool {
    let r2 = (near as u64).saturating_mul(near as u64);
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).any(|e| {
        e.is_champion() && e.is_alive() && e.team() != team && sim.distance_sq(me, e.id()) <= r2
    })
}

// ===================== 被动 =====================

/// 每个弗拉基米尔一份：参数，上一 tick 是否在池里（记日志用）、叫过几次。
#[derive(Clone, Default)]
struct Guard {
    p: Params,
    was_in: bool,
    calls: usize,
}

impl Guard {
    fn look(&mut self, sim: &mut StableSim<'_>, me: usize, from_hit: bool) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.was_in = false;
            return;
        }
        let (now, max) = e.hp();
        let team = e.team();
        let hp = if max > 0 { now as f64 * 100.0 / max as f64 } else { 100.0 };
        let names = buff_names(sim, me);
        let has = |x: &str| names.iter().any(|b| *b == vl(x));
        let inside = has("w_in");
        if inside && !self.was_in {
            wlog(format!("{} POOL: hp {hp:.0}%", head(sim, me)));
        }
        self.was_in = inside;
        let n = Now {
            hp,
            enemy_near: enemy_near(sim, me, team, self.p.near),
            controlled: controlled(sim, me),
            busy: inside || has("w_cd") || has("w_go"),
        };
        if want_pool(&self.p, &n) {
            let mut go = BuffV1::timed(&vl("w_go"), 30);
            go.duration_kind = BuffDurationV1::Time.code();
            sim.add_buff(me, &go);
            self.calls += 1;
            if self.calls <= 20 || self.calls % 50 == 0 {
                wlog(format!("{} GO #{}: hp {hp:.0}%{}", head(sim, me), self.calls, if from_hit { " on a hit" } else { "" }));
            }
        }
    }
}

impl StablePassive for Guard {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.was_in = false;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Vladimir (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.look(sim, me, false);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _: usize, _: usize) {
        self.look(sim, me, true);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Sanguine Pool at low health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:guard"), Guard::default());
    host.log(LogLevel::Info, "league_vladimir_pool v1 loaded (Vladimir's Sanguine Pool at low health).");
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

    fn now(hp: f64) -> Now {
        Now { hp, enemy_near: true, controlled: false, busy: false }
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"hp":30,"near":50000,"x":1}"#), Params { hp: 30, near: 50_000 });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn pool_only_below_the_line_with_an_enemy_near() {
        let p = Params::default();
        assert!(want_pool(&p, &now(34.0)));
        assert!(!want_pool(&p, &now(35.0)));
        assert!(!want_pool(&p, &now(80.0)));
        assert!(!want_pool(&p, &Now { enemy_near: false, ..now(10.0) }));
    }

    #[test]
    fn never_while_busy_or_controlled() {
        let p = Params::default();
        assert!(!want_pool(&p, &Now { busy: true, ..now(10.0) }));
        assert!(!want_pool(&p, &Now { controlled: true, ..now(10.0) }));
    }

    #[test]
    fn the_flag_names_fit() {
        assert!(vl("w_go").len() <= BUFF_NAME_CAP);
        assert_eq!(vl("w_cd"), "league_vladimir_w_cd");
    }
}
