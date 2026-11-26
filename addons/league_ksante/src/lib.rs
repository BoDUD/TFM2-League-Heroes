//! 奎桑提附加包（用户 2026-10-22：全盛姿态「单独一套」动作）。主包是纯数据，全盛时的出招（`ao_attack` / `ao_skill` … ）由数据的
//! `CasterAnimation` 按全盛 buff 播；游戏按名字自动播的待机、走、挨打数据换不了，本包补这一件事：
//!
//! - **全盛的整身**（`view.rs`）：他身上有全盛 buff `league_ksante_ao`（主包大招挂的，`ao_t` tick）时，站着、走着、挨打都画成全盛姿态
//!   （`ao_idle` / `ao_run` / `ao_hit`），普攻的第一 tick 也是 `ao_attack`。不改任何数据：本包没有副本，主包的奎桑提原样。
//! - **全盛的生命上限**（0.1.1，2026-11-14，用户看了「和英雄联盟不一样的地方」清单后说「全改吧」）：英雄联盟（V26.20）全盛时
//!   当前生命被压在最大生命的 65% 以内（"65% maximum health which cannot be modified nor exceeded by any means"），进入全盛时高于
//!   它的部分直接扣掉、结束后也不还。数据读不到当前生命（`hp_mult` 是按比例缩放最大生命，结束时又按比例长回来，不是这条规则），
//!   所以放在本包的比赛钩子 [`Cap`] 里：每 tick 身上有 `league_ksante_ao` 的活着的英雄，生命高于最大生命的 [`CAP_PCT`]% 就设回
//!   这条线（`entity_set_hp`）。附加包合集里由 league_addons 的 `BundleMatch` 转发。日志 `CAP`。
//! - **开大的时机**（0.1.2，用户 2026-11-18：「奎桑提为什么总是喜欢大招起手 很奇怪啊 高手的奎桑提不会这样打啊」，
//!   `opener.rs`）：游戏的 AI 敌人一进射程就放 R，满血开团第一下就进全盛、白丢三成多的血。AI 钩子 [`opener::Opener`]
//!   等他自己掉到最大生命的 70% 以下、目标残血、目标扑在残血队友身上，或者 AI 连着要了 4 秒才放，别的时候改成普攻那个
//!   目标。日志 `R HELD` / `R LET`。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ksante.log`，每次启动游戏重写，上一次的留在 .prev.log：`FORM`（画面里换
//! 姿态，限了条数）和显示统计。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod opener;
pub mod view;

const ID: &str = "league_ksante";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_ksante") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 全盛姿态的 buff（主包大招挂的）：view.rs 照它换画面，[`Cap`] 照它压生命。
pub const ALL_OUT: &str = "league_ksante_ao";
/// 全盛时生命的上限：最大生命的这么多 %（英雄联盟 65%）。
pub const CAP_PCT: usize = 65;

/// The health All Out allows (League: "65% maximum health which cannot be modified nor exceeded by any means"):
/// `Some(cap)` when `hp` is over it.
pub fn capped(hp: usize, max: usize) -> Option<usize> {
    let cap = max * CAP_PCT / 100;
    (hp > cap && max > 0).then_some(cap)
}

/// The match hook: every tick, every living champion in All Out (K'Sante, or Sylas with the stolen ult) is held at
/// [`capped`]'s line.
pub struct Cap;

/// 奎桑提这位英雄的 id（实体的名字就是英雄 id）。
const KSANTE: &str = "league_ksante";

fn is_all_out(b: &BuffV1) -> bool {
    &b.name_buf[..b.name_len.min(BUFF_NAME_CAP)] == ALL_OUT.as_bytes()
}

/// 一份模拟：来历 + 种子（league_eggs 的 Origin，同一份比赛的预演、画面里的两遍阵容都一样）。
type SimKey = (u32, u64, u64, u64, u64);

fn sim_key(sim: &StableSim<'_>) -> SimKey {
    let o = sim.sim_origin().unwrap_or_default();
    (o.kind, o.match_id, o.set_index, o.replay_id, sim.seed())
}

/// 这份模拟的英雄里有没有奎桑提。阵容一局里不变：每条线程记最近 16 份模拟的答案，同一份每 600 tick（或 tick 倒回去了，
/// 说明是另一份）再看一次名单；读不到名字的英雄当作可能是他（照旧扫）。
fn has_ksante(sim: &StableSim<'_>) -> bool {
    use std::cell::RefCell;
    thread_local! {
        static SEEN: RefCell<Vec<(SimKey, usize, bool)>> = const { RefCell::new(Vec::new()) };
    }
    let (key, now) = (sim_key(sim), sim.tick());
    let fresh = |sim: &StableSim<'_>| {
        (0..sim.champion_count()).any(|i| {
            sim.get_entity(sim.champion_id_at(i)).and_then(|e| e.name()).is_none_or(|n| n == KSANTE)
        })
    };
    SEEN.with(|s| {
        let mut s = s.borrow_mut();
        if let Some(e) = s.iter_mut().find(|e| e.0 == key) {
            if now < e.1 || now - e.1 >= 600 {
                *e = (key, now, fresh(sim));
            }
            return e.2;
        }
        let v = fresh(sim);
        if s.len() >= 16 {
            s.remove(0);
        }
        s.push((key, now, v));
        v
    })
}

impl StableMatchHook for Cap {
    fn on_match_tick(&self, sim: &mut StableSim<'_>, _rng_seed: u64) {
        // 这份模拟里没有奎桑提，就没有人能进全盛（只有他的大招、或塞拉斯从他身上偷的那份挂这个 buff）：不用每 tick 把
        // 每个英雄的 buff 扫一遍（2026-11-22 过日采样：别人的比赛里也天天在扫，占附加包合集的 5%）
        if !has_ksante(sim) {
            return;
        }
        // 先看生命（便宜），够不着上限的就不用扫 buff；挑出来的和原来一样
        let over: Vec<(usize, usize, usize, usize)> = (0..sim.champion_count())
            .filter_map(|i| sim.get_entity(sim.champion_id_at(i)))
            .filter(|e| e.is_alive())
            .filter_map(|e| {
                let (hp, max) = e.hp();
                capped(hp, max).map(|cap| (e, hp, max, cap))
            })
            .filter(|(e, ..)| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| is_all_out(&b)))
            .map(|(e, hp, max, cap)| (e.id(), hp, max, cap))
            .collect();
        for (id, hp, max, cap) in over {
            if sim.entity_set_hp(id, cap) {
                if let Some(k) = counted("cap") {
                    wlog(format!("t={} #{id} CAP #{k}: All Out holds health at {CAP_PCT}% - {hp} -> {cap} of {max}", sim.tick()));
                }
            }
        }
    }
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KSANTE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ksante.log");
        }
    }
    PathBuf::from("league_ksante.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line stalled the simulation thread (2026-10-12, #242)
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
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (K'Sante: the All Out body, health held at {CAP_PCT}% in All Out, R held for a reason) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    // the bundle (league_addons) sets its own match hook after every register and forwards to this one
    module.set_match_hook(Cap);
    // 0.1.2: the game AI's R waits for a reason (opener.rs)
    module.add_player_input_ai(opener::Opener::default());
    host.log(LogLevel::Info, "league_ksante loaded (the All Out body, the All Out health cap, R held for a reason).");
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
    fn all_out_holds_health_at_65_percent() {
        // League: entering All Out cuts the health above 65%; below it nothing changes; it is never exceeded
        assert_eq!(capped(1800, 2000), Some(1300));
        assert_eq!(capped(1301, 2000), Some(1300));
        assert_eq!(capped(1300, 2000), None);
        assert_eq!(capped(400, 2000), None);
        assert_eq!(capped(0, 0), None);
    }

    #[test]
    fn the_all_out_buff_is_the_main_packs() {
        let kit = include_str!("../../../league/champion/league_ksante.data_champion");
        assert!(kit.contains(&format!("\"{ALL_OUT}\"")), "{ALL_OUT} is not in the main pack's K'Sante");
    }
}
