//! 烬附加包：「低语」照英雄联盟把额外攻速换成攻击力（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补
//! 附加包」）。
//!
//! 英雄联盟里烬的攻速是定死的：装备和增益给的额外攻速不加快他开枪，而是每 1% 换成 `AD_PER_AS`% 的攻击力（0.25%）。主包是
//! 纯数据，攻速增益照常缩短他的攻击间隔。本包的被动 `league_jhin_whisper:whisper` 每 `EVERY` tick 读一次他的攻速倍率
//! （`attack_speed_mult`，100 = 没加成），把高出 100 的部分用自己的 buff `BUFF`（攻速 −同样多、攻击力 +那么多 × 0.25%）
//! 抵掉；攻速减益照常生效。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_jhin_whisper.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_jhin_whisper";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_jhin_whisper") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const BUFF: &str = "league_jhin_whisper_ad";
/// 每 1% 额外攻速换多少 % 攻击力（英雄联盟 0.25%）：百分之几的四分之一。
pub const AD_PER_AS_DIV: i32 = 4;
pub const EVERY: usize = 6;
/// 自己的 buff 挂多久（每次重算都重挂）。
const TICKS: usize = 30;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_JHIN_WHISPER_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_jhin_whisper.log");
        }
    }
    PathBuf::from("league_jhin_whisper.log")
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

fn head(sim: &StableSim<'_>, me: usize) -> String {
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
    format!("[{kind} m={} s={}] t={} #{me}", m(o.match_id), m(o.set_index), sim.tick())
}

/// The bonus attack speed to cancel: the multiplier above 100 without this add-on's own buff (`ours`, ≤ 0).
pub fn bonus(mult: usize, ours: i32) -> i32 {
    (mult as i32 - 100 - ours).max(0)
}

/// The buff for `bonus`% attack speed: (attack speed %, attack damage %).
pub fn convert(bonus: i32) -> (i32, i32) {
    (-bonus, bonus / AD_PER_AS_DIV)
}

#[derive(Clone, Default)]
struct Whisper {
    /// 现在挂着的 (攻速 %, 攻击力 %) 和挂上的 tick。
    on: Option<((i32, i32), usize)>,
    best: i32,
}

impl StablePassive for Whisper {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.on = None;
        wlog(format!("{} SPAWN: the add-on's Jhin (player {player})", head(sim, me)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        if tick % EVERY != 0 {
            return;
        }
        let Some(e) = sim.get_entity(me).filter(|e| e.is_alive()) else {
            self.on = None;
            return;
        };
        let worn = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == BUFF).map(|b| b.attack_speed_mult);
        let (mult, interval) = (e.attack_speed_mult(), e.attack_interval());
        let want = convert(bonus(mult, worn.unwrap_or(0)));
        let stale = self.on.is_none_or(|(v, t)| v != want || tick + EVERY * 2 >= t + TICKS) || worn.is_none();
        if !stale {
            return;
        }
        sim.entity_remove_buff(me, BUFF);
        if want.0 != 0 {
            let mut b = BuffV1::timed(BUFF, TICKS);
            b.attack_speed_mult = want.0;
            b.attack_mult = want.1;
            sim.add_buff(me, &b);
        }
        if -want.0 > self.best + 9 {
            self.best = -want.0;
            wlog(format!("{} WHISPER: +{}% attack speed -> +{}% attack damage (attack speed x{mult}%, interval {interval})",
                         head(sim, me), -want.0, want.1));
        }
        self.on = Some((want, tick));
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.on = None;
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Jhin's bonus attack speed into attack damage) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:whisper"), Whisper::default());
    host.log(LogLevel::Info, "league_jhin_whisper v1 loaded (Jhin's bonus attack speed into attack damage).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bonus_attack_speed_becomes_attack_damage() {
        assert_eq!(bonus(100, 0), 0);
        assert_eq!(bonus(140, 0), 40);
        assert_eq!(bonus(100, -40), 40);
        assert_eq!(bonus(80, 0), 0);
        assert_eq!(convert(40), (-40, 10));
    }
}
