//! 茂凯附加包（用户 2026-10-18：「全按推荐做」，做扩展包）。主包保持纯数据；`mod.override_info` 把主包的茂凯换成 `override/`
//! 里的副本（`make_override.py` 用 tools/kit/build_maokai.py 的 `native=1` 生成：技能一字不改，被动换成本包的
//! `league_maokai:sap_magic`，普攻的吸元秘术不再由数据回血、改成挂一个 3 tick 的 `league_maokai_sap_on` 交给本包；树苗多一份
//! 「在草丛里」的爆炸），本包补数据做不到的三件事：
//!
//! - **按最大生命回血**（英雄联盟的吸元秘术）：数据读不到生命，主包回固定值 + 法强；本包看到 `sap_on` 时按他的等级回复最大生命的
//!   `heal_lo`‰ 到 `heal_hi`‰（1 级到 18 级线性，英雄联盟 4.5%–12%）。
//! - **被敌方技能打中也会充好吸元秘术**：英雄联盟里每被敌方技能打中一次冷却减 4 秒。原生被动收到伤害时不告诉是普攻还是技能，所以按
//!   近似判断：打他的是敌方英雄、而且那名英雄的技能、技能 2 或大招在 `window` tick 内刚进入冷却，就算技能打中，给他挂上主包的
//!   `league_maokai_sap`（和自己技能命中时一样，下一次普攻就是吸元秘术）。
//! - **草丛里的树苗更强**：读地图的草丛格子（league_nidalee 的 bush.rs，同雷恩加尔的读法），他自己留下、在原地超过 `stand`
//!   tick 不动的区域就是他的树苗（他别的弹道都在飞）；树苗在草丛里时每 tick 给他挂 3 tick 的 `league_maokai_e_brush`，副本的数据
//!   据此改用更大、更痛、减速更强的爆炸。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_maokai.log`，每次启动游戏重写，上一次的留在 .prev.log：`HEAL`
//! （回了多少）、`STRUCK`（被哪名英雄的技能打中、充好吸元秘术）、`SAPLING`（树苗立在哪、在不在草丛）、`BUSHES`（这场的草丛格子）；
//! `HEAL`、`STRUCK`、`SAPLING` 服务器的预模拟限了条数（整个游戏一个计数），你看的那场每条都记。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[path = "../../league_nidalee/src/bush.rs"]
pub mod bush;

const ID: &str = "league_maokai";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_maokai") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 吸元秘术就绪（主包数据：技能命中时挂上，下一次普攻用掉）。
pub const SAP: &str = "league_maokai_sap";
/// 副本的普攻打出吸元秘术时挂 3 tick：本包按最大生命回血。
pub const SAP_ON: &str = "league_maokai_sap_on";
/// 树苗立在草丛里（本包每 tick 挂 3 tick，副本的爆炸读它）。
pub const BRUSH: &str = "league_maokai_e_brush";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_MAOKAI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_maokai.log");
        }
    }
    PathBuf::from("league_maokai.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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

/// 日志条数：每种整个游戏先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条；你看的那场每条都写（0.1.1：以前一起限，
/// 预模拟先把条数用完，2026-11-01 一晚看的几场只留下 5 行）。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind` (the count of the whole launch, every sim): its number when it is to be written - the first
/// `LOG_FIRST`, then every `LOG_EVERY`-th, and every one when `shown`.
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

/// Like `noted`, but every line of the match on screen: only the presims capped.
fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    noted(kind, on_screen(sim))
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

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 1 级时回复最大生命的千分比（英雄联盟 4.5%）。
    pub heal_lo: usize,
    /// 18 级时的千分比（12%）。
    pub heal_hi: usize,
    /// 被技能打中充好的吸元秘术挂多久（tick，同主包的 p_t）。
    pub p_t: usize,
    /// 打他的英雄的技能进入冷却多少 tick 以内算「刚放过技能」。
    pub window: usize,
    /// 他留下的区域在原地多少 tick 不动算树苗。
    pub stand: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { heal_lo: 45, heal_hi: 120, p_t: 300, window: 90, stand: 20 }
    }
}

/// `{"heal_lo":45,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "heal_lo" => p.heal_lo = v,
            "heal_hi" => p.heal_hi = v,
            "p_t" => p.p_t = v,
            "window" => p.window = v,
            "stand" => p.stand = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 这一级回多少：最大生命 x（lo 到 hi 千分比，1 级到 18 级线性）。
pub fn heal_amount(p: &Params, level: usize, max_hp: usize) -> usize {
    let lv = level.clamp(1, 18) as u64;
    let permille = p.heal_lo as u64 + (p.heal_hi.saturating_sub(p.heal_lo) as u64) * (lv - 1) / 17;
    (max_hp as u64 * permille / 1000) as usize
}

/// 一个技能格刚进入冷却（放过不到 `window` tick）：剩余冷却在 (cooltime - window, cooltime] 里。
pub fn just_cast(c: Option<CooldownV1>, window: usize) -> bool {
    c.is_some_and(|c| c.cooltime > 0 && c.remaining > 0 && c.remaining + window > c.cooltime)
}

/// 他留下的区域：位置 -> 第一次看到的 tick。返回这一 tick 已站够 `stand` tick 的位置（树苗），并扔掉不在了的。
pub fn still(seen: &mut HashMap<(u64, u64), usize>, now: &[(u64, u64)], tick: usize, stand: usize) -> Vec<(u64, u64)> {
    seen.retain(|k, _| now.contains(k));
    for k in now {
        seen.entry(*k).or_insert(tick);
    }
    let mut out: Vec<(u64, u64)> = seen.iter().filter(|(_, t)| tick >= **t + stand).map(|(k, _)| *k).collect();
    out.sort();
    out
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

// ===================== 被动：吸元秘术 =====================

#[derive(Clone, Default)]
struct SapMagic {
    p: Params,
    /// 上一 tick 身上有 `sap_on`（一次吸元秘术只回一次血）。
    was_on: bool,
    /// 这场用的草丛（第一次 on_update 时挑）；None = 地图没有草丛格子。
    grid: Option<Option<bush::Grid>>,
    /// 他留下的区域：位置 -> 第一次看到的 tick。
    seen: HashMap<(u64, u64), usize>,
    /// 已经记过日志的树苗位置。
    logged: Vec<(u64, u64)>,
}

impl StablePassive for SapMagic {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.was_on = false;
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _player: usize, me: usize, attacker: usize, damage: usize) {
        let (Some(e), Some(a)) = (sim.get_entity(me), sim.get_entity(attacker)) else { return };
        if !e.is_alive() || a.team() == e.team() || !a.is_champion() || damage == 0 {
            return;
        }
        let w = self.p.window;
        let slot = [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult].into_iter().find(|s| just_cast(a.cooldown(*s), w));
        let Some(slot) = slot else { return };
        if has_buff(sim, me, SAP) {
            return;
        }
        let name = a.name().unwrap_or_default();
        sim.add_buff(me, &BuffV1::timed(SAP, self.p.p_t));
        if let Some(k) = tally(sim, "struck") {
            wlog(format!("{} STRUCK by {name}'s {slot:?} ({damage}): Sap Magic ready #{k}", head(sim, me)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, level, (hp, max_hp)) = (e.is_alive(), e.level(), e.hp());
        // Sap Magic's heal: once per `sap_on` the copy's attack laid
        let on = alive && has_buff(sim, me, SAP_ON);
        if on && !self.was_on {
            let amount = heal_amount(&self.p, level, max_hp);
            sim.heal(me, me, amount);
            if let Some(k) = tally(sim, "heal") {
                wlog(format!("{} HEAL {amount} ({hp}/{max_hp}, level {level}) #{k}", head(sim, me)));
            }
        }
        self.was_on = on;
        // the saplings: his own zones standing still; in a bush -> e_brush on him
        if self.grid.is_none() {
            let points: Vec<(f64, f64)> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|u| u.is_alive())
                .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
                .collect();
            let g = bush::pick_bushes(&points, &bush::maps());
            wlog(match &g {
                Some(g) => format!("{} BUSHES: {} bush cells", head(sim, me), g.count()),
                None => format!("{} BUSHES: no bush grid - saplings never in brush", head(sim, me)),
            });
            self.grid = Some(g);
        }
        let now: Vec<(u64, u64)> = (0..sim.projectile_count())
            .filter_map(|i| sim.projectile_at(i))
            .filter(|q| q.caster_id == me && !q.is_end)
            .map(|q| (q.x, q.y))
            .collect();
        let saplings = still(&mut self.seen, &now, sim.tick(), self.p.stand);
        let grid = self.grid.as_ref().and_then(|g| g.as_ref());
        let in_brush = saplings.iter().find(|s| grid.is_some_and(|g| g.at(s.0 as f64, s.1 as f64)));
        for s in &saplings {
            if !self.logged.contains(s) {
                self.logged.push(*s);
                if self.logged.len() > 64 {
                    self.logged.remove(0);
                }
                if let Some(k) = tally(sim, "sapling") {
                    let b = grid.is_some_and(|g| g.at(s.0 as f64, s.1 as f64));
                    wlog(format!("{} SAPLING at ({}, {}) {} #{k}", head(sim, me), s.0, s.1, if b { "IN BRUSH" } else { "in the open" }));
                }
            }
        }
        if alive && in_brush.is_some() {
            sim.entity_remove_buff(me, BRUSH);
            sim.add_buff(me, &BuffV1::timed(BRUSH, 3));
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
        "=== {ID} v{VERSION} (Maokai: Sap Magic heals % max health and readies when enemy skills hit him, saplings in brush) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:sap_magic"), SapMagic::default());
    host.log(LogLevel::Info, "league_maokai loaded (Sap Magic % max-health heal and enemy-skill readiness, saplings in brush).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module.set_map_customizer(bush::BushReader);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"heal_lo":50,"junk":7,"heal_hi":100,"p_t":240,"window":60,"stand":15}"#);
        assert_eq!((p.heal_lo, p.heal_hi, p.p_t, p.window, p.stand), (50, 100, 240, 60, 15));
    }

    #[test]
    fn the_copy_carries_the_default_params_and_no_data_heal() {
        let copy = include_str!("../override/league_maokai.data_champion");
        let at = copy.find("\"passive_ref\": \"league_maokai:sap_magic\"").expect("no league_maokai:sap_magic passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("heal_lo", d.heal_lo), ("heal_hi", d.heal_hi), ("p_t", d.p_t), ("window", d.window), ("stand", d.stand)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        assert!(copy.contains(&format!("\"name\": \"{SAP_ON}\"")), "the copy never lays sap_on");
        assert!(copy.contains(&format!("\"buff_name\": \"{BRUSH}\"")), "the copy's sapling never reads e_brush");
        assert!(!copy.contains("\"heal_type\": \"Caster\""), "the copy still heals in data");
    }

    #[test]
    fn heal_grows_with_the_level() {
        let p = Params::default();
        assert_eq!(heal_amount(&p, 1, 2000), 90);       // 4.5%
        assert_eq!(heal_amount(&p, 18, 2000), 240);     // 12%
        assert_eq!(heal_amount(&p, 30, 2000), 240);
        assert!(heal_amount(&p, 9, 2000) > 90 && heal_amount(&p, 9, 2000) < 240);
    }

    #[test]
    fn a_skill_cast_within_the_window_counts() {
        let cd = |remaining, cooltime| {
            Some(CooldownV1 { size: 0, remaining, cooltime, max_charges: 1, charges: 0, next_charge_ticks: 0, unlocked: true })
        };
        assert!(just_cast(cd(600, 600), 90));
        assert!(just_cast(cd(520, 600), 90));
        assert!(!just_cast(cd(500, 600), 90));
        assert!(!just_cast(cd(0, 600), 90));
        assert!(!just_cast(None, 90));
    }

    #[test]
    fn a_zone_standing_still_is_a_sapling() {
        let mut seen = HashMap::new();
        assert!(still(&mut seen, &[(5, 5), (9, 9)], 100, 20).is_empty());
        assert_eq!(still(&mut seen, &[(5, 5), (10, 9)], 119, 20), Vec::<(u64, u64)>::new());
        assert_eq!(still(&mut seen, &[(5, 5), (11, 9)], 120, 20), vec![(5, 5)]);
        assert!(still(&mut seen, &[(11, 9)], 121, 20).is_empty());
    }
}
