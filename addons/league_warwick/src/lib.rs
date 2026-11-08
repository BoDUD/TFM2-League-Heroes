//! 沃里克附加包（用户选「做附加包」）：主包数据读不到生命，做不到的两件事，加上连招。
//!
//! `mod.override_info` 把主包的沃里克换成 `override/` 里的副本（tools/kit/build_warwick.py 的 native）：数据和主包一样，
//! 只是每一下爪击（普攻、Q 的撕咬、R 的三下）打中时调本包的 `league_warwick:hunger`（去掉主包每下固定的回血），
//! 普攻不再挂主包的 `w_hunt`，被动挂本包的 `league_warwick:hunt`（参数在英雄数据的 `passive.params` 里）。
//!
//! - **血之饥渴**：英雄联盟里沃里克的普攻附带魔法伤害；生命低于 50% 时回复同样多的生命，低于 25% 时回三倍。`hunger`
//!   在他生命低于 `p_half`% 时回 `p_dmg`，低于 `p_quarter`% 时回 `p_dmg` × `p_triple`（魔法伤害本身仍在数据里）。
//! - **鲜血追猎**：英雄联盟里他嗅到生命低于 50% 的敌方英雄，朝他们跑得更快、打他们打得更快，低于 25% 时加成三倍。被动每
//!   `HUNT_EVERY` tick 看一次：`w_reach` 内有看得见的、生命低于 `w_half`% 的敌方英雄（低于 `w_quarter`% 的看不见也算，
//!   `sensed`），就给他挂 `w_hunt`（攻速 +`w_as`%、移速 +`w_ms`%，`HUNT_HOLD` tick，下次看时续上），那人低于 `w_quarter`%
//!   时三倍；猎物不见了档位再留 `HUNT_LINGER` tick（`hunt_linger`）。
//! - **连招**（用户：「有连招要做连招」；`combo.rs`）：AI 钩子 `league_warwick:combo` 替游戏的 AI 按 E、Q、R——
//!   E → Q（先开远祖嗥叫的减伤再扑咬，咬中时立刻嚎叫，主包数据做的）、R → Q（压制结束接一口撕咬）、残血英雄优先 Q / R 追。
//!
//! 0.1.2（2026-11-08 日志审查：`HUNT` 约 12 tick 一次在 0 和 1 之间来回跳，A 组 42 场数到 #2600、一场约 60 次——猎物一走出
//! 视野（`is_visible`）档位就掉，每 `HUNT_EVERY` tick 看一次、加成只挂 `HUNT_HOLD` tick）：生命低于 `w_quarter`% 的猎物不看
//! 视野（英雄联盟里鲜血足迹把他们显出来）；档位往下掉之前留 `HUNT_LINGER` tick，进草丛、出视野一下又出来不再来回跳。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_warwick.log`，每次启动游戏重写：`SPAWN`、`HEAL`、`HUNT`（追猎
//! 开始、换成三倍、结束）、`E FIRST` / `R THEN Q` / `Q TO PREY` / `R HUNT`（连招），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod combo;

const ID: &str = "league_warwick";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_warwick") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 鲜血追猎每隔几 tick 看一次。
pub const HUNT_EVERY: usize = 6;
/// 追猎的加成每次挂多久（比 `HUNT_EVERY` 长一点，档位掉到 0 后很快消失）。
pub const HUNT_HOLD: usize = 10;
/// 猎物不见了（进草丛、走出视野或 `w_reach`）后档位再留多久（tick）：2026-11-08 的日志里它约 12 tick 一次在 0 和 1 之间跳。
pub const HUNT_LINGER: usize = 30;

fn sn(x: &str) -> String {
    format!("league_warwick_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_WARWICK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_warwick.log");
        }
    }
    PathBuf::from("league_warwick.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the game, 2026-10-12)
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

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub p_dmg: usize,
    pub p_half: usize,
    pub p_quarter: usize,
    pub p_triple: usize,
    pub w_as: usize,
    pub w_ms: usize,
    pub w_half: usize,
    pub w_quarter: usize,
    pub w_reach: usize,
    // the combos (combo.rs): the reaches, Primal Howl's guard, Infinite Duress's line, its suppression and its cooldown
    pub atk_range: usize,
    pub q_range: usize,
    pub e_range: usize,
    pub e_r: usize,
    pub e_t: usize,
    pub r_cast: usize,
    pub r_range: usize,
    pub r_w: usize,
    pub r_sup: usize,
    pub r_cd: usize,
    pub r_dur: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { p_dmg: 20, p_half: 50, p_quarter: 25, p_triple: 3, w_as: 30, w_ms: 12, w_half: 50, w_quarter: 25,
                 w_reach: 150000, atk_range: 25000, q_range: 40000, e_range: 35000, e_r: 40000, e_t: 150,
                 r_cast: 90000, r_range: 95000, r_w: 10000, r_sup: 90, r_cd: 3600, r_dur: 24 }
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
            "p_dmg" => p.p_dmg = v,
            "p_half" => p.p_half = v,
            "p_quarter" => p.p_quarter = v,
            "p_triple" => p.p_triple = v,
            "w_as" => p.w_as = v,
            "w_ms" => p.w_ms = v,
            "w_half" => p.w_half = v,
            "w_quarter" => p.w_quarter = v,
            "w_reach" => p.w_reach = v,
            "atk_range" => p.atk_range = v,
            "q_range" => p.q_range = v,
            "e_range" => p.e_range = v,
            "e_r" => p.e_r = v,
            "e_t" => p.e_t = v,
            "r_cast" => p.r_cast = v,
            "r_range" => p.r_range = v,
            "r_w" => p.r_w = v,
            "r_sup" => p.r_sup = v,
            "r_cd" => p.r_cd = v,
            "r_dur" => p.r_dur = v,
            _ => {}
        }
    }
    p
}

/// 每个沃里克的参数（被动 configure 时存下，原生效果里读）：键是 (这局的种子, 他的编号)。
static PARAMS: LazyLock<Mutex<HashMap<(u64, usize), Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim.seed(), me)).copied().unwrap_or_default()
}

// ===================== 计算（单元测试用） =====================

/// 血之饥渴这一下回多少：生命比例 `share`（0–1）低于 `p_half`% 回 `p_dmg`，低于 `p_quarter`% 回三倍，否则 0。
pub fn hunger_heal(share: f64, p: &Params) -> usize {
    if share < p.p_quarter as f64 / 100.0 {
        p.p_dmg * p.p_triple
    } else if share < p.p_half as f64 / 100.0 {
        p.p_dmg
    } else {
        0
    }
}

/// 鲜血追猎的档位：0 没有猎物，1 有生命低于 `w_half`% 的，3 有低于 `w_quarter`% 的（三倍）。
pub fn hunt_level(prey: &[f64], p: &Params) -> usize {
    if prey.iter().any(|&s| s < p.w_quarter as f64 / 100.0) {
        3
    } else if prey.iter().any(|&s| s < p.w_half as f64 / 100.0) {
        1
    } else {
        0
    }
}

/// 闻得到这个敌方英雄吗（生命比例 `share`，`visible` 他这一队看得见他）：看得见的都算；生命低于 `w_quarter`% 的看不见也算
/// （英雄联盟里鲜血足迹把他们显出来）。
pub fn sensed(share: f64, visible: bool, p: &Params) -> bool {
    visible || share < p.w_quarter as f64 / 100.0
}

/// 档位的滞后：这次算出的 `now` 不比挂着的 `held` 低就用 `now`；低了，`held` 最后一次够得上（`since`）还不到
/// `HUNT_LINGER` tick 就留着 `held`（猎物进草丛、走出视野一下又出来，档位不再来回跳）。返回 (档位, 它最后一次够得上的 tick)。
pub fn hunt_linger(now: usize, held: usize, since: usize, tick: usize) -> (usize, usize) {
    if now >= held || tick >= since + HUNT_LINGER {
        (now, tick)
    } else {
        (held, since)
    }
}

fn share(e: &StableEntity<'_, '_>) -> f64 {
    let (hp, max) = e.hp();
    if max == 0 { 1.0 } else { hp as f64 / max as f64 }
}

// ===================== 原生效果 =====================

/// 一下爪击打中了：按他自己的生命回血。
fn hunger(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let Some(e) = sim.get_entity(me) else { return };
    if !e.is_alive() {
        return;
    }
    let s = share(&e);
    let p = params_of(sim, me);
    let amount = hunger_heal(s, &p);
    if amount == 0 {
        return;
    }
    sim.heal(me, me, amount);
    if let Some(k) = counted("heal") {
        wlog(format!("{} HEAL #{k}: Eternal Hunger on {} at {:.0}% health - healed {amount}", head(sim, me),
                     who(sim, input.target_id), s * 100.0));
    }
}

struct HungerFx;
impl StableEffectType for HungerFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        hunger(sim, caster, input);
    }
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Hunt {
    p: Params,
    level: usize,
    /// 最后一次有够得上 `level` 的猎物的 tick（`hunt_linger`）。
    since: usize,
}

impl Hunt {
    fn tick(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.level = 0;
            self.since = 0;
            return;
        }
        let tick = sim.tick();
        let team = e.team();
        let (x, y) = e.pos();
        let reach = self.p.w_reach as f64;
        let mut prey = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() || !u.is_champion() {
                continue;
            }
            let s = share(&u);
            if !sensed(s, sim.is_visible(team, u.id()), &self.p) {
                continue;
            }
            let (ux, uy) = u.pos();
            let d = ((ux as f64 - x as f64).powi(2) + (uy as f64 - y as f64).powi(2)).sqrt();
            if d <= reach {
                prey.push(s);
            }
        }
        let was_seen = self.since;
        let (level, since) = hunt_linger(hunt_level(&prey, &self.p), self.level, self.since, tick);
        self.since = since;
        if level > 0 {
            let mut b = BuffV1::timed(&sn("w_hunt"), HUNT_HOLD);
            b.attack_speed_mult = (self.p.w_as * level) as i32;
            b.move_speed_mult = (self.p.w_ms * level) as i32;
            if level != self.level {
                sim.entity_remove_buff(me, &sn("w_hunt"));
            }
            sim.entity_stack_buff(me, &b, 1, true);
        }
        if level != self.level {
            if let Some(k) = counted("hunt") {
                let low = prey.iter().cloned().fold(1.0f64, f64::min);
                let gone = if level < self.level {
                    format!(", level {} last had prey {} ticks ago", self.level, tick.saturating_sub(was_seen))
                } else {
                    String::new()
                };
                wlog(format!("{} HUNT #{k}: level {} -> {level} (the weakest champion in reach at {:.0}%{gone})", head(sim, me),
                             self.level, low * 100.0));
            }
            self.level = level;
        }
    }
}

impl StablePassive for Hunt {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert((sim.seed(), me), self.p);
        self.level = 0;
        self.since = 0;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Warwick (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if sim.tick() % HUNT_EVERY == 0 {
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
        "=== {ID} v{VERSION} (Warwick: Eternal Hunger by health, Blood Hunt, the combos) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:hunger"), HungerFx);
    module.add_native_passive(format!("{ID}:hunt"), Hunt::default());
    module.add_player_input_ai(combo::Combo::default());
    host.log(LogLevel::Info, "league_warwick loaded (Eternal Hunger by health, Blood Hunt, the combos).");
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
    fn hunger_heals_only_when_hurt() {
        let p = Params::default();
        assert_eq!(hunger_heal(0.8, &p), 0);
        assert_eq!(hunger_heal(0.5, &p), 0);
        assert_eq!(hunger_heal(0.49, &p), 20);
        assert_eq!(hunger_heal(0.3, &p), 20);
        assert_eq!(hunger_heal(0.2, &p), 60);
    }

    #[test]
    fn the_hunt_smells_wounded_champions() {
        let p = Params::default();
        assert_eq!(hunt_level(&[], &p), 0);
        assert_eq!(hunt_level(&[0.9, 0.6], &p), 0);
        assert_eq!(hunt_level(&[0.9, 0.4], &p), 1);
        assert_eq!(hunt_level(&[0.4, 0.2], &p), 3);
    }

    #[test]
    fn blood_trail_shows_the_quarter() {
        let p = Params::default();
        assert!(sensed(0.9, true, &p));
        assert!(!sensed(0.4, false, &p), "half health in the fog: not smelled");
        assert!(sensed(0.2, false, &p), "under the quarter line: smelled in the fog too");
        assert!(!sensed(0.25, false, &p));
    }

    #[test]
    fn the_hunt_lingers_after_the_prey_vanishes() {
        // 2026-11-08 log: t=12612 0 -> 1, 12636 1 -> 0, 12648 0 -> 1, 12660 1 -> 0 - the prey in and out of sight
        let mut held = (0, 0);
        let mut levels = Vec::new();
        for (t, now) in [(12612, 1), (12618, 1), (12624, 1), (12630, 1), (12636, 0), (12642, 0), (12648, 1), (12654, 1),
                         (12660, 0), (12666, 0), (12672, 0), (12678, 0), (12684, 0), (12690, 0)] {
            held = hunt_linger(now, held.0, held.1, t);
            levels.push(held.0);
        }
        // held through the 12-tick gap, dropped HUNT_LINGER ticks after the last prey (12654 + 30 = 12684)
        assert_eq!(levels, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]);
        // up at once, triple held too, then down a step
        assert_eq!(hunt_linger(3, 1, 100, 106), (3, 106));
        assert_eq!(hunt_linger(1, 3, 106, 130), (3, 106));
        assert_eq!(hunt_linger(1, 3, 106, 106 + HUNT_LINGER), (1, 106 + HUNT_LINGER));
        assert_eq!(hunt_linger(0, 0, 0, 5), (0, 5));
    }

    #[test]
    fn params_parse() {
        assert_eq!(parse_params(r#"{"p_dmg":20,"p_half":50,"p_quarter":25,"p_triple":3,"w_as":30,"w_ms":12,"w_half":50,"w_quarter":25,"w_reach":150000,"atk_range":25000,"q_range":40000,"e_range":35000,"e_r":40000,"e_t":150,"r_cast":90000,"r_range":95000,"r_w":10000,"r_sup":90,"r_cd":3600,"r_dur":24}"#), Params::default());
        assert_eq!(parse_params(r#"{"p_dmg":30}"#).p_dmg, 30);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_warwick.py");
        let src = std::fs::read_to_string(path).expect("build_warwick.py");
        let d = Params::default();
        for (k, v) in [("p_dmg", d.p_dmg), ("p_half", d.p_half), ("p_quarter", d.p_quarter), ("p_triple", d.p_triple),
                       ("w_as", d.w_as), ("w_ms", d.w_ms), ("w_half", d.w_half), ("w_quarter", d.w_quarter),
                       ("w_reach", d.w_reach), ("atk_range", d.atk_range), ("q_range", d.q_range),
                       ("e_range", d.e_range), ("e_r", d.e_r), ("e_t", d.e_t), ("r_cast", d.r_cast),
                       ("r_range", d.r_range), ("r_w", d.r_w), ("r_sup", d.r_sup), ("r_cd", d.r_cd), ("r_dur", d.r_dur)] {
            assert!(src.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in build_warwick.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["w_hunt", "e_on"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }
}
