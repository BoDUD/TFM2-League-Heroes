//! 低血量附加包：布里茨的法力屏障、乐芙兰的镜花水月、丽桑卓的自我冰封照英雄联盟在生命低时触发（用户 2026-10-24：「查看现在
//! 没有做附加包的英雄有明显不一样的话全部补附加包」）。
//!
//! 主包是纯数据，读不到生命：三人都改成「身边有两名以上敌方英雄」（布里茨再加「队友被控」）时触发——每次动作先数身边的敌人，
//! 两个以上就挂 `<名>_n2`，再读它。`mod.override_info` 换上的副本（`make_override.py` 从主包生成）把读 `n2` 的地方改成读
//! 本包的标记 `<英雄>_low`；本包的被动在生命不高于门槛时一直挂着它（每 tick 续 `HOLD` tick）：
//!
//! | 英雄 | 门槛（英雄联盟） | 触发什么（都在主包数据里） |
//! |---|---|---|
//! | 布里茨 | 30% | 法力屏障：120 + 80% 法强的护盾，冷却 60 秒 |
//! | 乐芙兰 | 40% | 镜花水月：隐身 1 秒、后闪、留下幻像，40 秒一次 |
//! | 丽桑卓 | 35% | 大招改为冰封自己 |
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_lowhp.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_lowhp";
/// 标记每次续多久（每 tick 都续，比 1 多一点，跨过结算顺序）。
pub const HOLD: usize = 3;
/// (英雄, 被动名, 标记, 门槛 %)。
pub const HEROES: [(&str, &str, &str, usize); 3] = [
    ("league_blitzcrank", "blitzcrank", "league_blitzcrank_low", 30),
    ("league_leblanc", "leblanc", "league_leblanc_low", 40),
    ("league_lissandra", "lissandra", "league_lissandra_low", 35),
];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LOWHP_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_lowhp.log");
        }
    }
    PathBuf::from("league_lowhp.log")
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

/// At `pct`% of the maximum or under.
pub fn low(hp: usize, max: usize, pct: usize) -> bool {
    hp * 100 <= pct * max.max(1)
}

// ===================== 被动 =====================

#[derive(Clone)]
struct Low {
    hero: &'static str,
    flag: &'static str,
    pct: usize,
    was: bool,
    n: usize,
}

impl StablePassive for Low {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.was = false;
        wlog(format!("{} SPAWN: the add-on's {} (player {player}), low at {}%", head(sim, me), self.hero, self.pct));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.was = false;
            return;
        }
        let (hp, max) = e.hp();
        let now = low(hp, max, self.pct);
        if now {
            sim.entity_remove_buff(me, self.flag);
            sim.add_buff(me, &BuffV1::timed(self.flag, HOLD));
        }
        if now && !self.was {
            self.n += 1;
            if self.n <= 80 {
                wlog(format!("{} LOW #{}: hp {hp}/{max}", head(sim, me), self.n));
            }
        }
        self.was = now;
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.was = false;
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Blitzcrank's Mana Barrier, LeBlanc's Mirror Image, Lissandra's self-tomb on low health) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    for (hero, name, flag, pct) in HEROES {
        module.add_native_passive(format!("{ID}:{name}"), Low { hero, flag, pct, was: false, n: 0 });
    }
    host.log(LogLevel::Info, "league_lowhp v1 loaded (three passives on low health).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn low_is_at_the_line_or_under() {
        assert!(low(300, 1000, 30));
        assert!(!low(301, 1000, 30));
        assert!(low(0, 0, 30));
    }

    #[test]
    fn the_names_fit() {
        for (_, _, flag, _) in HEROES {
            assert!(flag.len() <= BUFF_NAME_CAP);
        }
    }
}
