//! 乌迪尔附加包（用户 2026-10-22：技能方案 A，「W 坚铁甲胄（野猪）变成低血时自动护盾 + 下两次攻击回血」；每个姿态一套动作）。
//! 主包保持纯数据；`mod.override_info` 把主包的乌迪尔换成 `override/` 里的副本（`make_override.py` 用
//! tools/kit/build_udyr.py 的 `native` 生成：技能、时机一字不改，只是坚铁甲胄不再由技能触发、改由本包的被动按生命触发），
//! 本包补数据做不到的两件事：
//!
//! - **坚铁甲胄按生命**（被动 `league_udyr:mantle`）：英雄联盟的 W 是挨打、残血时按的。他的生命低于 `W_HP`% 时（两次之间至少
//!   `W_ICD` tick）给他 `W_SH` + `W_SH_R`% 攻击力的护盾（`W_SH_T` tick），挂上主包的两次回血攻击（`league_udyr_w2`，主包的
//!   普攻按它回血）、护盾的样子（`league_udyr_w_sh`，主包的 view_buffs 画玉绿护罩）和冷却标记（`league_udyr_w_icd`）。
//!   主包：每 `w_icd` tick 的第一个技能附带。
//! - **每个姿态整身**（`view.rs`）：熊、公羊、凤凰姿态时站着、跑着、挨打、阵亡也是那个姿态（纳尔附加包的做法）。
//!
//! 数字是主包参数表 P 的同名项（小写）；`make_override.py` 生成副本时核对，不一致就停。本包不按任何技能键。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_udyr.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `MANTLE`（几成生命时、护盾多少），限了条数；还有姿态整身的显示统计。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_udyr";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_udyr") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 坚铁甲胄：生命低于几 %、两次之间的 tick、护盾（固定、攻击力 %、持续 tick）、两次回血攻击的时限 tick。
pub const W_HP: usize = 50;
pub const W_ICD: usize = 720;
pub const W_SH: usize = 70;
pub const W_SH_R: usize = 40;
pub const W_SH_T: usize = 240;
pub const W_T: usize = 300;
/// 隔几 tick 看一次生命。
pub const EVERY: usize = 6;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_UDYR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_udyr.log");
        }
    }
    PathBuf::from("league_udyr.log")
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

fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
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

fn n(name: &str) -> String {
    format!("{ID}_{name}")
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Params {
    pub w_hp: usize,
    pub w_icd: usize,
    pub w_sh: usize,
    pub w_sh_r: usize,
    pub w_sh_t: usize,
    pub w_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { w_hp: W_HP, w_icd: W_ICD, w_sh: W_SH, w_sh_r: W_SH_R, w_sh_t: W_SH_T, w_t: W_T }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "w_hp" => p.w_hp = v,
            "w_icd" => p.w_icd = v,
            "w_sh" => p.w_sh = v,
            "w_sh_r" => p.w_sh_r = v,
            "w_sh_t" => p.w_sh_t = v,
            "w_t" => p.w_t = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 这一下要不要披上坚铁甲胄：生命比例 `share`（0–1）低于 `w_hp`%、不在冷却。
pub fn wants_mantle(share: f64, cooling: bool, p: &Params) -> bool {
    !cooling && share < p.w_hp as f64 / 100.0
}

/// 护盾多少：`w_sh` + `w_sh_r`% 攻击力。
pub fn shield_of(attack: usize, p: &Params) -> usize {
    p.w_sh + p.w_sh_r * attack / 100
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Mantle {
    p: Params,
}

impl Mantle {
    fn tick(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (hp, max) = e.hp();
        if hp == 0 || max == 0 {
            return;
        }
        let share = hp as f64 / max as f64;
        let attack = e.stat().attack;
        if !wants_mantle(share, has_buff(sim, me, &n("w_icd")), &self.p) {
            return;
        }
        let amount = shield_of(attack, &self.p);
        sim.entity_add_shield(me, amount, self.p.w_sh_t);
        // the main pack's buffs, read by its data: the cooldown, the shell's picture (view_buffs w_sh), the two healing
        // attacks (w2 -> w1, spent by the attack)
        sim.entity_remove_buff(me, &n("w_sh"));
        sim.entity_remove_buff(me, &n("w1"));
        sim.entity_remove_buff(me, &n("w2"));
        sim.entity_stack_buff(me, &BuffV1::timed(&n("w_icd"), self.p.w_icd), 1, true);
        sim.entity_stack_buff(me, &BuffV1::timed(&n("w_sh"), self.p.w_sh_t), 1, true);
        sim.entity_stack_buff(me, &BuffV1::timed(&n("w2"), self.p.w_t), 1, true);
        if let Some(k) = counted("mantle") {
            wlog(format!("{} MANTLE #{k}: Iron Mantle at {:.0}% health - shield {amount} for {} ticks", head(sim, me),
                         share * 100.0, self.p.w_sh_t));
        }
    }
}

impl StablePassive for Mantle {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Udyr (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if sim.tick() % EVERY == 0 {
            self.tick(sim, me);
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Udyr: Iron Mantle by health, the whole-body stances) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:mantle"), Mantle::default());
    host.log(LogLevel::Info, "league_udyr loaded (Iron Mantle by health, whole-body stances).");
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
    fn the_mantle_comes_only_when_hurt_and_ready() {
        let p = Params::default();
        assert!(!wants_mantle(0.8, false, &p));
        assert!(!wants_mantle(0.5, false, &p));
        assert!(wants_mantle(0.49, false, &p));
        assert!(!wants_mantle(0.2, true, &p)); // cooling down
    }

    #[test]
    fn the_shield_scales_with_attack() {
        let p = Params::default();
        assert_eq!(shield_of(0, &p), W_SH);
        assert_eq!(shield_of(100, &p), W_SH + W_SH_R);
    }

    #[test]
    fn params_read_back() {
        let p = parse_params("{\"w_hp\": 40, \"w_icd\": 600, \"w_sh\": 80, \"w_sh_r\": 50, \"w_sh_t\": 200, \"w_t\": 280}");
        assert_eq!(p, Params { w_hp: 40, w_icd: 600, w_sh: 80, w_sh_r: 50, w_sh_t: 200, w_t: 280 });
    }

    #[test]
    fn names_fit_a_buff() {
        for s in ["w_icd", "w_sh", "w1", "w2", "st_q", "st_e", "st_r"] {
            assert!(n(s).len() <= BUFF_NAME_CAP);
        }
    }

    #[test]
    fn the_copy_uses_the_passive_and_the_numbers() {
        let copy = include_str!("../override/league_udyr.data_champion");
        assert!(copy.contains("league_udyr:mantle"), "the copy never uses the passive");
        for (k, v) in [("w_hp", W_HP), ("w_icd", W_ICD), ("w_sh", W_SH), ("w_sh_r", W_SH_R), ("w_sh_t", W_SH_T), ("w_t", W_T)] {
            assert!(copy.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for (buff, _) in view::STANCES {
            assert!(copy.contains(&format!("\"name\": \"{buff}\"")), "the copy never lays {buff}");
        }
    }
}
