//! 克烈附加包：数据做不到、和英雄联盟不一样的地方，这里照英雄联盟做。
//!
//! `mod.override_info` 把主包的克烈换成 `override/` 里的副本（tools/kit/build_kled.py --native），`passive` 换成本包的
//! `league_kled:skaarl`：
//!
//! - **斯嘎尔自己的血量**：主包用一层护盾当斯嘎尔的血，旁边挂一个跟着护盾走的 `league_kled_sk`（WithShield），所以大招
//!   的护盾也会让斯嘎尔"活着"。副本的 `sk` 是普通标记，本包自己记斯嘎尔的血：每次骑上（这条命第一次 `sk_hp` + 攻击
//!   `sk_ad`%，勇气满了重新骑上 `re_hp` + 攻击 `re_ad`%），骑着时受到的伤害从这里扣，扣完就摘掉 `sk`，数据的控制器
//!   下一拍让他下马。
//! - **捕熊夹的绳子会断**：副本 Q 夹住英雄时给克烈挂 `league_kled_q_hold`，拽人那一下只在它还在时才拽。本包每 tick 看被
//!   夹住（身上有 `league_kled_q_slow`）的敌方英雄离克烈多远，超过 `q_break` 就摘掉减速和 `q_hold`——绳子断了，不拽。
//! - **下马整身步行**：`view.rs` 在画面上把下马时（身上有 `league_kled_ft`）正在播的 idle / run / hit 和普攻第一帧换成
//!   图里步行的 `f_idle` …（主包只能用 `CasterAnimation` 换出招的动作）。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。不用全局变量，服务端预模拟和
//! 你看的那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kled.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_kled";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_kled") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// Mounted: the copy's mount and remount raise it, this add-on takes it off when Skaarl's health is gone.
const SK: &str = "league_kled_sk";
/// On foot (the data's controller raises it once `sk` is gone; the remount takes it off).
pub const FOOT: &str = "league_kled_ft";
/// The shackle holds: the yank waits on it (on Kled).
const HOLD: &str = "league_kled_q_hold";
/// The shackle's slow on the champion caught.
const SHACKLE: &str = "league_kled_q_slow";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KLED_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_kled.log");
        }
    }
    PathBuf::from("league_kled.log")
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
    /// 这条命第一次骑上时斯嘎尔的血：固定值 + 攻击百分比。
    pub sk_hp: usize,
    pub sk_ad: usize,
    /// 勇气满了重新骑上时斯嘎尔的血：固定值 + 攻击百分比。
    pub re_hp: usize,
    pub re_ad: usize,
    /// 被夹住的英雄离克烈超过这个距离，绳子断。
    pub q_break: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { sk_hp: 500, sk_ad: 140, re_hp: 180, re_ad: 60, q_break: 60000 }
    }
}

/// `{"sk_hp":500,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "sk_hp" => p.sk_hp = v,
            "sk_ad" => p.sk_ad = v,
            "re_hp" => p.re_hp = v,
            "re_ad" => p.re_ad = v,
            "q_break" => p.q_break = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

/// Skaarl's health when Kled mounts: the life's first time full, a remount from courage the smaller one.
pub fn skaarl_health(p: &Params, attack: usize, first: bool) -> i64 {
    if first {
        (p.sk_hp + p.sk_ad * attack / 100) as i64
    } else {
        (p.re_hp + p.re_ad * attack / 100) as i64
    }
}

/// The shackle breaks when the champion caught is farther than q_break.
pub fn snaps(p: &Params, a: (u64, u64), b: (u64, u64)) -> bool {
    let dx = a.0 as f64 - b.0 as f64;
    let dy = a.1 as f64 - b.1 as f64;
    (dx * dx + dy * dy).sqrt() > p.q_break as f64
}

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

// ===================== 被动 =====================

/// 每个克烈一份：参数、斯嘎尔剩的血、这条命骑上过几次、日志计数。
#[derive(Clone, Default)]
struct Skaarl {
    p: Params,
    /// Skaarl's health left while Kled rides him.
    pool: i64,
    /// `sk` seen on him last tick (a new one is a mount).
    riding: bool,
    /// Mounts this life (the first is full health).
    mounts: usize,
    flees: usize,
    breaks: usize,
}

impl Skaarl {
    /// A mount (the life's first, or a remount from courage): Skaarl's health set.
    fn mounted(&mut self, sim: &StableSim<'_>, me: usize) {
        let attack = sim.get_entity(me).map_or(0, |e| e.stat().attack);
        self.pool = skaarl_health(&self.p, attack, self.mounts == 0);
        self.mounts += 1;
        if self.mounts <= 40 || self.mounts % 100 == 0 {
            wlog(format!("{} MOUNT Skaarl back with {} health (mount {} this life)", head(sim, me), self.pool, self.mounts));
        }
    }

    /// The shackle: the champion caught walked out of the rope's reach.
    fn rope(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !has(&e, HOLD) {
            return;
        }
        let (team, at) = (e.team(), e.pos());
        let ids: Vec<usize> = (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).collect();
        for id in ids {
            let Some(c) = sim.get_entity(id) else { continue };
            if c.team() == team || !c.is_alive() || !has(&c, SHACKLE) || !snaps(&self.p, at, c.pos()) {
                continue;
            }
            sim.entity_remove_buff(id, SHACKLE);
            sim.entity_remove_buff(me, HOLD);
            self.breaks += 1;
            if self.breaks <= 40 || self.breaks % 100 == 0 {
                wlog(format!("{} BREAK the rope on {} snapped (farther than {}): no yank ({} in all)", head(sim, me),
                             name_of(sim, id), self.p.q_break, self.breaks));
            }
            return;
        }
    }
}

impl StablePassive for Skaarl {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.riding = false;
        self.mounts = 0;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Kled (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        if damage == 0 || !self.riding {
            return;
        }
        // Skaarl takes it (the copy's shield absorbs it; his own health counts here)
        self.pool -= damage as i64;
        if self.pool > 0 {
            return;
        }
        sim.entity_remove_buff(me, SK);
        self.riding = false;
        self.flees += 1;
        if self.flees <= 40 || self.flees % 100 == 0 {
            wlog(format!("{} FLEE Skaarl's health gone ({damage} from {}): Kled on foot ({} in all)", head(sim, me),
                         name_of(sim, attacker), self.flees));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let sk = has(&e, SK) && !has(&e, FOOT);
        if sk && !self.riding {
            self.mounted(sim, me);
        }
        self.riding = sk;
        self.rope(sim, me);
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.riding = false;
        self.mounts = 0;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Skaarl's own health, the rope that snaps, the whole body on foot) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:skaarl"), Skaarl::default());
    host.log(LogLevel::Info, "league_kled loaded (Skaarl's health, the shackle's rope, the whole body on foot).");
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
        let p = parse_params(r#"{"q_break":50000,"re_ad":50,"re_hp":150,"sk_ad":120,"sk_hp":400,"x":1}"#);
        assert_eq!(p, Params { sk_hp: 400, sk_ad: 120, re_hp: 150, re_ad: 50, q_break: 50000 });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn skaarl_comes_back_weaker() {
        let p = Params::default();
        assert_eq!(skaarl_health(&p, 100, true), 500 + 140);
        assert_eq!(skaarl_health(&p, 100, false), 180 + 60);
    }

    #[test]
    fn the_rope_snaps_past_its_reach() {
        let p = Params::default();
        assert!(!snaps(&p, (0, 0), (36000, 48000))); // 60000 away: still held
        assert!(snaps(&p, (0, 0), (36000, 48001)));
        assert!(snaps(&p, (100000, 0), (0, 0)));
    }

    #[test]
    fn names_are_the_data_s() {
        for n in [SK, FOOT, HOLD, SHACKLE] {
            assert!(n.starts_with("league_kled_"), "{n}");
        }
    }
}
