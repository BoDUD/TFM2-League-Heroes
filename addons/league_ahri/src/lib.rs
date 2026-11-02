//! 阿狸附加包：摄魂夺魄按英雄联盟现在的规则数每一次击杀和助攻（用户 2026-10-24：「需要补附加包的话也补」）。
//!
//! 主包是纯数据：只认得出她自己打出的最后一击，所以小兵、野怪只数普攻打死的（Q、狐火、精魄弹打死的数不到），英雄阵亡用佛耶戈的
//! 击杀窗口（她 3 秒内打过的英雄死了就算），同一个窗口里只认一个。`mod.override_info` 把主包的阿狸换成 `override/` 里的副本
//! （`make_override.py` 从主包生成）：数据和主包一样，只是普攻的击杀检查和每次命中英雄的窗口标记去掉、被动换成本包的
//! `league_ahri:essence`。
//!
//! - **精魄**：她每补到一个小兵或野怪（`on_unit_kill`，用什么打死的都算）记一层，第 `k_need` 层时挂上 `league_ahri_k_go`，
//!   主包挂在她每个动作上的监视器看到就回血（主包的数字）；`k_show` 层以上身上显示主包的精魄画面 `league_ahri_et_ready`。
//!   层数死了也留着（英雄联盟也是）。
//! - **参与击杀**：她的每一次英雄击杀（`on_kill`）和助攻（`on_assist`）都挂一次 `league_ahri_tk_go`，监视器看到就回血、
//!   灵魄突袭的窗口开着时再给一次、窗口至少再开 10 秒。几个人同时阵亡就排队，上一个被监视器取走了再挂下一个。
//!
//! 数字都从英雄数据的 `passive.params` 来。不用全局变量，服务端预模拟和你看的那场各算各的。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ahri.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_ahri";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_ahri") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 主包阿狸的名字（buff、画面都以它开头）。
fn ah(x: &str) -> String {
    format!("league_ahri_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AHRI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ahri.log");
        }
    }
    PathBuf::from("league_ahri.log")
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

/// 本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 第几层精魄回血。
    pub k_need: usize,
    /// 几层以上显示精魄画面。
    pub k_show: usize,
    /// 奖励标记挂多久（等她下一个动作的监视器来取）。
    pub go: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { k_need: 9, k_show: 6, go: 60 }
    }
}

/// `{"k_need":9,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "k_need" => &mut p.k_need,
            "k_show" => &mut p.k_show,
            "go" => &mut p.go,
            _ => continue,
        };
        *slot = v;
    }
    p
}

// ===================== 计数 =====================

/// 精魄和等着挂出去的奖励：纯计数，和游戏无关（测试用）。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Count {
    /// 现在的精魄层数。
    pub essence: usize,
    /// 还没挂出去的参与击杀。
    pub takedowns: usize,
    /// 还没挂出去的满层回血。
    pub heals: usize,
}

impl Count {
    /// 补到一个小兵或野怪。
    pub fn unit(&mut self, p: &Params) {
        self.essence += 1;
        if self.essence >= p.k_need.max(1) {
            self.essence = 0;
            self.heals += 1;
        }
    }

    /// 精魄画面该不该亮。
    pub fn shown(&self, p: &Params) -> bool {
        self.essence >= p.k_show
    }
}

// ===================== 被动 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn timed(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

/// 每个阿狸一份：参数、计数、日志用的编号。
#[derive(Clone, Default)]
struct Essence {
    p: Params,
    c: Count,
    logged: usize,
}

impl Essence {
    fn note(&mut self, sim: &StableSim<'_>, me: usize, what: &str) {
        self.logged += 1;
        if self.logged <= 120 || self.logged % 50 == 0 {
            wlog(format!("{} {what} (essence {}, queued: takedowns {}, heals {})", head(sim, me), self.c.essence,
                         self.c.takedowns, self.c.heals));
        }
    }

    /// 精魄画面跟着层数亮灭（主包的 view buff；死了会被清掉，活着时补回来）。
    fn picture(&self, sim: &mut StableSim<'_>, me: usize) {
        let on = has_buff(sim, me, &ah("et_ready"));
        if self.c.shown(&self.p) && !on {
            sim.add_buff(me, &BuffV1::named(&ah("et_ready")));
        } else if !self.c.shown(&self.p) && on {
            sim.entity_remove_buff(me, &ah("et_ready"));
        }
    }
}

impl StablePassive for Essence {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Ahri (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _victim: usize) {
        self.c.unit(&self.p);
        self.note(sim, me, "UNIT");
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.c.takedowns += 1;
            self.note(sim, me, &format!("KILL #{victim}"));
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.c.takedowns += 1;
        self.note(sim, me, "ASSIST");
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        // one flag at a time: the next waits until a watcher has taken the last
        if self.c.takedowns > 0 && !has_buff(sim, me, &ah("tk_go")) {
            timed(sim, me, &ah("tk_go"), self.p.go);
            self.c.takedowns -= 1;
        }
        if self.c.heals > 0 && !has_buff(sim, me, &ah("k_go")) {
            timed(sim, me, &ah("k_go"), self.p.go);
            self.c.heals -= 1;
        }
        self.picture(sim, me);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Ahri's Essence Theft on every kill and takedown) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:essence"), Essence::default());
    host.log(LogLevel::Info, "league_ahri v1 loaded (Ahri's Essence Theft on every kill and takedown).");
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
        assert_eq!(parse_params(r#"{"k_need":8,"x":1}"#), Params { k_need: 8, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_ninth_essence_heals_and_starts_over() {
        let p = Params::default();
        let mut c = Count::default();
        for _ in 0..8 {
            c.unit(&p);
        }
        assert_eq!((c.essence, c.heals), (8, 0));
        assert!(c.shown(&p));
        c.unit(&p);
        assert_eq!((c.essence, c.heals), (0, 1));
        assert!(!c.shown(&p));
        for _ in 0..18 {
            c.unit(&p);
        }
        assert_eq!(c.heals, 3);
    }

    #[test]
    fn the_names_fit() {
        for x in ["tk_go", "k_go", "et_ready"] {
            assert!(ah(x).len() <= BUFF_NAME_CAP);
        }
    }
}
