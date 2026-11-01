//! 凯尔附加包：升阶的翅膀（和升阶本身）死了也不掉（用户：「能一直保持吗 死后不掉」）。
//!
//! 主包保持纯数据：5 / 8 / 12 级的升阶是凯尔身上永久的 `league_kayle_rank5` / `rank8` / `rank12`（12 级再加
//! `form3`），翅膀是绑在它们上的 view_buffs。引擎在她死亡时清掉身上全部 buff，数据也没有「复活时」这个时机，所以主包
//! 每条命的第一次出手才静默补读等级（`league_kayle_life` 标记这条命读过了），从复活到第一次出手之间她没有翅膀，
//! 射程也是近战的。`mod.override_info` 把主包的凯尔换成 `override/` 里的副本：技能一字不改，只加了本包的被动
//! `league_kayle:ascend`，它每 tick 看一次：
//!
//! - **活着**：身上有哪几阶就记下来（记在被动里，被动在玩家身上，死了不丢；只增不减）；
//! - **死了 / 刚复活**：身上缺了记下的哪一阶就原样补上（和主包同样的数值：rank5 射程 +27500，rank12 攻速 +30%、
//!   移速 +10%、射程 +10000，form3 只是翅膀），死着的时候也补，所以倒下时翅膀还在；补过任何一阶就同时补上
//!   `league_kayle_life`，主包这条命就不再补读（补读不看身上已有的阶，同名 buff 会叠成两层，射程变两倍）。
//!
//! - **等级**（0.2.0）：主包拿最大生命值当等级表探测（10% 最大生命打破 123 / 151 / 189 的护盾），等级表以外的生命（装备）、
//!   探测那 2 tick 里挨的一下、暴击都会让它提前好几级（游戏日志 10-24：rank5 有 9 / 23 次在 3 级，rank12 全在 6-10 级，
//!   从没在 12 级）。副本里每个探测都换成读本包挂的等级标记 `league_kayle_lv5` / `lv8` / `lv12`（make_override.py），
//!   被动每 tick 按她真实的等级（`level()`）把缺的标记补上，死了清掉也马上补回。
//!
//! 新的一阶仍由主包的那段数据在出手时给（金翼仪式和语音照旧），只是读的是等级标记；本包只补已经升过的阶，从不提前。
//! 第一条命（还什么都没记）和死着时升到新一阶的情况都交给那段数据。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kayle.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_kayle";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_kayle") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

fn ky(x: &str) -> String {
    format!("league_kayle_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KAYLE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_kayle.log");
        }
    }
    PathBuf::from("league_kayle.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (15 000 lines a session,
    // about 9 s of stalls on the simulation thread, 2026-10-12, the user: 「LOL mod让游戏掉帧很严重 加载很卡」)
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
    let lv = sim.get_entity(id).map_or(0, |e| e.level());
    format!("[{kind} m={} s={}] t={} #{id} Lv{lv}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 升阶 =====================

/// 三阶的 buff 名（主包的），按顺序。
pub const RANKS: [&str; 3] = ["rank5", "rank8", "rank12"];

/// 三阶的等级标记和要的等级：副本的数据读它们代替主包的血量探测（make_override.py 的 PROBE_SHIELDS）。
pub const LEVEL_FLAGS: [(&str, u32); 3] = [("lv5", 5), ("lv8", 8), ("lv12", 12)];

/// 到了 `level` 级身上该有、却缺了的等级标记。
pub fn missing_flags(level: u32, has: &dyn Fn(&str) -> bool) -> Vec<String> {
    LEVEL_FLAGS.iter().filter(|(_, at)| level >= *at).map(|(f, _)| ky(f)).filter(|n| !has(n)).collect()
}

/// 第 k 阶要补上的 buff：和主包 `AddCasterBuff` 的一样（12 级的 form3 是另一条，只带翅膀）。
pub fn rank_buff(k: usize) -> BuffV1 {
    let mut b = BuffV1::named(&ky(RANKS[k]));
    match k {
        0 => b.range = 27_500,
        2 => {
            b.attack_speed_mult = 30;
            b.move_speed_mult = 10;
            b.range = 10_000;
        }
        _ => {}
    }
    b
}

/// 记下的阶（`had`）里身上缺了哪几阶：要补的 buff 名，按顺序；12 级连 form3。
pub fn missing(had: [bool; 3], has: &dyn Fn(&str) -> bool) -> Vec<String> {
    let mut out = Vec::new();
    for k in 0..3 {
        if had[k] && !has(&ky(RANKS[k])) {
            out.push(ky(RANKS[k]));
        }
    }
    if had[2] && !has(&ky("form3")) {
        out.push(ky("form3"));
    }
    out
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Ascend {
    /// 这一局里她升过的阶（活着时在身上看到过）。
    had: [bool; 3],
    /// 上一 tick 她活着：死了 / 复活的那一刻记一行日志。
    was_alive: bool,
    /// 挂过等级标记的最高等级：每个标记第一次挂上时记一行日志，死后补回的不记。
    flagged: u32,
}

impl StablePassive for Ascend {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let alive = e.is_alive();
        let level = e.level() as u32;
        // the level flags the copy's data reads in place of the health probes: laid before her next action can look
        for name in missing_flags(level, &|n| has_buff(sim, me, n)) {
            sim.add_buff(me, &BuffV1::named(&name));
            if level > self.flagged {
                wlog(format!("{} LEVEL {name} laid", head(sim, me)));
            }
        }
        self.flagged = self.flagged.max(level);
        if alive {
            for k in 0..3 {
                if !self.had[k] && has_buff(sim, me, &ky(RANKS[k])) {
                    self.had[k] = true;
                    wlog(format!("{} RANK {} seen (kept from now on)", head(sim, me), RANKS[k]));
                }
            }
        }
        if alive != self.was_alive {
            wlog(format!("{} {}", head(sim, me), if alive { "ALIVE" } else { "DEAD" }));
            self.was_alive = alive;
        }
        let gone = missing(self.had, &|n| has_buff(sim, me, n));
        for name in &gone {
            match RANKS.iter().position(|r| ky(r) == *name) {
                Some(k) => sim.add_buff(me, &rank_buff(k)),
                None => sim.add_buff(me, &BuffV1::named(name)),
            }
        }
        if !gone.is_empty() {
            wlog(format!("{} KEEP {} put back ({})", head(sim, me), gone.join(" "), if alive { "alive" } else { "dead" }));
        }
        // the main pack's once-a-life re-read adds the ranks without looking (two of a name stack: twice the range):
        // with them kept it must not run - whether they came back now or lasted through the death
        let life = ky("life");
        if alive && self.had[0] && !has_buff(sim, me, &life) {
            sim.add_buff(me, &BuffV1::named(&life));
            wlog(format!("{} LIFE flag set (the main pack's re-read skipped)", head(sim, me)));
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
        "=== {ID} v{VERSION} (Kayle: her ascension at her real levels, and its wings kept through death) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:ascend"), Ascend::default());
    host.log(LogLevel::Info, "league_kayle v2 loaded (Kayle: ascension at her real levels, kept through death).");
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
    fn nothing_before_the_first_rank() {
        assert!(missing([false; 3], &|_| false).is_empty());
    }

    #[test]
    fn puts_back_what_she_had() {
        let none = |_: &str| false;
        assert_eq!(missing([true, false, false], &none), vec!["league_kayle_rank5"]);
        assert_eq!(missing([true, true, true], &none),
            vec!["league_kayle_rank5", "league_kayle_rank8", "league_kayle_rank12", "league_kayle_form3"]);
    }

    #[test]
    fn never_twice() {
        let all = |_: &str| true;
        assert!(missing([true, true, true], &all).is_empty());
        let only5 = |n: &str| n == "league_kayle_rank5";
        assert_eq!(missing([true, true, false], &only5), vec!["league_kayle_rank8"]);
    }

    #[test]
    fn level_flags_at_their_levels() {
        let none = |_: &str| false;
        // the game logs had rank5 at level 3 and rank12 at 6-10: the flags come at the level alone
        assert!(missing_flags(4, &none).is_empty());
        assert_eq!(missing_flags(5, &none), vec!["league_kayle_lv5"]);
        assert_eq!(missing_flags(11, &none), vec!["league_kayle_lv5", "league_kayle_lv8"]);
        assert_eq!(missing_flags(12, &none), vec!["league_kayle_lv5", "league_kayle_lv8", "league_kayle_lv12"]);
        // after death only the cleared ones come back, never one twice
        let has5 = |n: &str| n == "league_kayle_lv5";
        assert_eq!(missing_flags(9, &has5), vec!["league_kayle_lv8"]);
    }

    #[test]
    fn the_copy_reads_these_flags() {
        let copy = include_str!("../override/league_kayle.data_champion");
        for (f, _) in LEVEL_FLAGS {
            assert!(copy.contains(&format!("\"buff_name\": \"{}\"", ky(f))), "{f}");
        }
        assert!(!copy.contains("league_kayle_probe_amp"), "a health probe is left in the copy");
    }

    #[test]
    fn same_numbers_as_the_main_pack() {
        assert_eq!(rank_buff(0).range, 27_500);
        assert_eq!((rank_buff(1).range, rank_buff(1).attack_speed_mult), (0, 0));
        let b = rank_buff(2);
        assert_eq!((b.attack_speed_mult, b.move_speed_mult, b.range), (30, 10, 10_000));
    }
}
