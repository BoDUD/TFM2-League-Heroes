//! 卑尔维斯附加包：真身里的「搠面皇锋」按真实的生命触发；「溶烛化紫」的永久攻速层数死后不掉。
//!
//! 主包保持纯数据：数据读不到生命，主包里真身的风暴是「两个敌方英雄贴身」就放；引擎在她死亡时清掉身上全部 buff，所以
//! 击杀叠的永久攻速（`league_belveth_l1`…`l8`，每层一个名字）每条命从零叠起。
//! `mod.override_info` 把主包的卑尔维斯换成 `override/` 里的副本（tools/kit/build_belveth.py --native）：风暴改读她身上的
//! `league_belveth_low`，`passive` 换成本包的 `league_belveth:banquet`：
//!
//! - 每 tick 读她的生命：低于最大生命的 `e_low`% 就挂上 3 tick 的 `league_belveth_low`（先摘再挂，只留一个），回到
//!   `e_low`% 以上就不再挂，3 tick 后自己消失（阿萝拉附加包的做法）。数据在控制器每次脉冲时读它（还要在真身里、
//!   `e_cd` 已过）。
//! - 活着时把身上每一层 `league_belveth_l<n>` 原样记下来；少了（死亡清掉的）就原样补回（科加斯附加包的做法）。层数只会
//!   变多（主包从不去掉一层），所以「身上比记下的少」只会是死亡清掉的。最多 `l_max` 层。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。不用全局变量，服务端预模拟和
//! 你看的那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_belveth.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_belveth";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_belveth") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// The flag the data's storm reads (build_belveth.py: `sw("low", storm)`).
const LOW: &str = "league_belveth_low";
/// Ticks the flag lasts: renewed every tick while she is low, gone 3 ticks after she is not.
const LOW_TICKS: usize = 3;
/// A lavender stack's name: this and its number (build_belveth.py: `l1` .. `l<l_max>`).
const STACK: &str = "league_belveth_l";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_BELVETH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_belveth.log");
        }
    }
    PathBuf::from("league_belveth.log")
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 生命低于最大生命的这个百分比算「残血」（风暴）。
    pub e_low: usize,
    /// 溶烛化紫最多几层。
    pub l_max: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { e_low: 35, l_max: 8 }
    }
}

/// `{"e_low":35,"l_max":8}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "e_low" => p.e_low = v,
            "l_max" => p.l_max = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

/// Is she low: health under e_low% of her maximum (a unit with no maximum never is).
pub fn is_low(p: &Params, hp: usize, max: usize) -> bool {
    max > 0 && hp * 100 < p.e_low * max
}

/// The stack number of a buff name (`league_belveth_l3` -> 3), within l_max.
pub fn stack_of(name: &str, l_max: usize) -> Option<usize> {
    let n: usize = name.strip_prefix(STACK)?.parse().ok()?;
    (1..=l_max).contains(&n).then_some(n)
}

/// The stacks kept that are not on her now (a death cleared them).
fn missing(kept: &[BuffV1], have: &[BuffV1]) -> Vec<BuffV1> {
    kept.iter().filter(|k| !have.iter().any(|h| h.name() == k.name())).cloned().collect()
}

// ===================== 被动 =====================

/// 每个卑尔维斯一份：参数、记下的层、上一 tick 是不是残血 / 活着（只为日志）。
#[derive(Clone, Default)]
struct Banquet {
    p: Params,
    kept: Vec<BuffV1>,
    low: bool,
    was_alive: bool,
    turns: usize,
}

impl Banquet {
    fn stacks(&self, sim: &StableSim<'_>, me: usize) -> Vec<BuffV1> {
        sim.get_entity(me).map_or_else(Vec::new, |e| {
            (0..e.buff_count())
                .filter_map(|i| e.buff_at(i))
                .filter(|b| stack_of(b.name(), self.p.l_max).is_some())
                .collect()
        })
    }
}

impl StablePassive for Banquet {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.low = false;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Bel'Veth (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let alive = e.is_alive();
        let (hp, max) = e.hp();
        if alive != self.was_alive {
            wlog(format!("{} {} with {} lavender stacks kept", head(sim, me), if alive { "ALIVE" } else { "DEAD" },
                         self.kept.len()));
            self.was_alive = alive;
        }
        // the lavender stacks: remember new ones, put back the ones a death cleared
        let have = self.stacks(sim, me);
        let gone = missing(&self.kept, &have);
        if !gone.is_empty() {
            for b in &gone {
                sim.add_buff(me, b);
            }
            wlog(format!("{} KEEP {} lavender stacks put back ({}), {} in all", head(sim, me), gone.len(),
                         if alive { "alive" } else { "dead" }, self.kept.len()));
        } else if alive && have.len() > self.kept.len() {
            wlog(format!("{} STACK {} -> {}", head(sim, me), self.kept.len(), have.len()));
            self.kept = have;
        }
        if !alive {
            self.low = false;
            return;
        }
        // the storm's flag
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
        // death clears the buffs (the stacks come back on the next update); the next life starts at full health
        self.low = false;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Royal Maelstrom at low health, lavender stacks kept through death) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:banquet"), Banquet::default());
    host.log(LogLevel::Info, "league_belveth v1 loaded (Bel'Veth: the storm by her health, lavender stacks kept).");
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
        assert_eq!(parse_params(r#"{"e_low":30,"l_max":6,"x":1}"#), Params { e_low: 30, l_max: 6 });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn low_is_under_the_threshold() {
        let p = Params::default();
        assert!(!is_low(&p, 1000, 1000));
        assert!(!is_low(&p, 350, 1000));
        assert!(is_low(&p, 349, 1000));
        assert!(!is_low(&p, 0, 0));
    }

    #[test]
    fn stacks_are_the_data_s_names() {
        assert_eq!(stack_of("league_belveth_l1", 8), Some(1));
        assert_eq!(stack_of("league_belveth_l8", 8), Some(8));
        assert_eq!(stack_of("league_belveth_l9", 8), None);
        assert_eq!(stack_of("league_belveth_low", 8), None);
        assert_eq!(stack_of("league_belveth_l0", 8), None);
        assert_eq!(BuffV1::timed(LOW, LOW_TICKS).name(), "league_belveth_low");
    }

    #[test]
    fn a_death_s_cleared_stacks_come_back() {
        let kept = vec![BuffV1::timed("league_belveth_l1", 1), BuffV1::timed("league_belveth_l2", 1)];
        assert_eq!(missing(&kept, &[]).len(), 2);
        assert_eq!(missing(&kept, &kept[..1]).len(), 1);
        assert!(missing(&kept, &kept).is_empty());
    }
}
