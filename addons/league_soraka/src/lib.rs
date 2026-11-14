//! 索拉卡附加包：祈愿按英雄联盟给生命低的友军多回血，被动「拯救」按英雄联盟朝生命低的友军跑时加速（用户 2026-11-14 看了
//! 「和英雄联盟不一样的地方」清单后说「全改吧」，再说「接着做」：能做的小项都做）。
//!
//! 英雄联盟的祈愿（R）："healing herself and all allied champions, ... increased by 50% on targets below 40% of their maximum
//! health"。主包是纯数据，数据读不到任何人的当前生命，所以祈愿给每个友方英雄一样多（`220` + `60`% 法强，`HEAL` / `HEAL_AP`）。
//! `mod.override_info` 把主包的索拉卡换成 `override/` 里的副本（`make_override.py` 从主包生成：只在大招那一圈治疗的**最前面**
//! 加一个本包的原生效果 `league_soraka:wish`，大招的说明换成本包的）：圈里的每个友方英雄先过这一步——生命低于最大生命的
//! `LOW_HP`%（40%）就多回复主包那一下的 `BONUS`%（50%：`110` + `30`% 法强），再照常吃主包的治疗。生命是治疗之前读的
//! （英雄联盟也是落下那一刻的生命）。
//!
//! 英雄联盟的拯救（被动，V14.4 起 90%）："Soraka gains 90% bonus movement speed while facing nearby allied champions that are
//! below 40% of their maximum health"（作用半径 2500）。数据读不到移动方向和友方的生命，主包近似成「W 施放后 2 秒移速 +30%」
//! （W 里的 `league_soraka_salvation`）。副本挂上本包的被动 `league_soraka:salvation`（[`Salvation`]）：每 `LOOK` tick 看一次
//! 她这几 tick 走的方向，朝着 `REACH` 以内一个生命低于 `LOW_HP`% 的友方英雄（左右 `CONE` 度以内）走就挂 `HOLD` tick 的
//! `league_soraka_salvation_run`（移速 +`MS`%），每次看到还朝着就续上，转开、站住、死了就没了。W 施放后那 2 秒 +30% 照旧
//! 是主包的（不叫拯救了）：经典 SDK 的模拟跑不了原生代码，拿掉它 W 每局少放 7.6 次（54.3 -> 46.7、54.4 -> 46.9，各 240 局），
//! 击杀差 -0.8 / -0.6——本包只加英雄联盟的规则，不动主包的数。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_soraka.log`，每次启动游戏重写，上一次的留在 .prev.log：`WISH`
//! （谁生命低、多回复了多少）、`SALVATION`（加速亮起：朝着谁、他的生命、多远、偏几度），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_soraka";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_soraka") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 主包祈愿的治疗：固定值、法强 %（副本里那一下 `Heal` 的 `amount` / `ap_ratio`，`make_override.py` 和测试核对）。
pub const HEAL: usize = 220;
pub const HEAL_AP: usize = 60;
/// 生命低于最大生命的这么多 % 算「生命低」（英雄联盟 40%）。
pub const LOW_HP: usize = 40;
/// 生命低的多回复主包那一下的这么多 %（英雄联盟 50%）。
pub const BONUS: usize = 50;

/// 拯救：移速 +`MS`%（英雄联盟 V14.4 起 90%，以前 70%）。
pub const MS: usize = 90;
/// 「附近」：她和那个友方英雄中心之间不超过这么远（英雄联盟的作用半径 2500 码；本包的射程按 1 码 = 100）。
pub const REACH: usize = 250000;
/// 「朝着」：她这几 tick 走的方向和她到那个友方英雄的方向差不超过这么多度（wiki 没写角度：左右各 45°）。
pub const CONE: usize = 45;
/// 每隔这么多 tick 看一次（走的方向按这几 tick 的位移算）；加速每次续 `HOLD` tick（n tick 的 buff 只在 n - 1 tick 里有），
/// 所以一直朝着就一直有，转开以后最多再有 `HOLD` - 1 tick。
pub const LOOK: usize = 3;
pub const HOLD: usize = LOOK + 2;
/// 这几 tick 走得不到这么远算站着（普攻、施法）；超过这么远是闪现、传送、被拉，不算走路。
pub const MIN_STEP: f64 = 300.0;
pub const MAX_STEP: f64 = 30_000.0;
/// 加速挂在这个名字上（主包 W 施放后那 2 秒 +30% 是 `league_soraka_salvation`，副本里照旧：名字不同，两个各算各的、加在一起）。
pub const SALVATION: &str = "league_soraka_salvation_run";
/// 主包 W 施放后的 +30%（副本里照旧）。
pub const W_HASTE: &str = "league_soraka_salvation";
/// 本包的被动（副本的 `passive.passive_ref`）。
pub const PASSIVE: &str = "league_soraka:salvation";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SORAKA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_soraka.log");
        }
    }
    PathBuf::from("league_soraka.log")
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

const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 100;

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

// ===================== 规则（单元测试用） =====================

/// 生命 `hp` / 最大生命 `max` 的人算不算生命低（低于 `LOW_HP`%；最大生命读不到的不算）。
pub fn low(hp: usize, max: usize) -> bool {
    max > 0 && hp * 100 < max * LOW_HP
}

/// 主包那一下治疗（法强 `ap`）之外多回复的量：它的 `BONUS`%。
pub fn bonus(ap: usize) -> usize {
    (HEAL + HEAL_AP * ap / 100) * BONUS / 100
}

/// 拯救的数（副本 `passive.params` 里的，全是非负整数；`make_override.py` 从上面的常量写进去，缺的用常量）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub ms: usize,
    pub low: usize,
    pub reach: usize,
    pub cone: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { ms: MS, low: LOW_HP, reach: REACH, cone: CONE }
    }
}

/// `{"cone":45,"low":40,...}` -> 参数；认不得的键忽略，缺的用常量。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k.trim().trim_matches('"') {
            "ms" => p.ms = v,
            "low" => p.low = v,
            "reach" => p.reach = v,
            "cone" => p.cone = v.min(180),
            _ => {}
        }
    }
    p
}

pub type Pt = (f64, f64);

/// 她这 `LOOK` tick 从 `from` 走到 `to`：走的方向（单位向量）。没怎么动（站着普攻、施法）或一下子过去太远（闪现、传送、复活）
/// 就没有。
pub fn heading(from: Pt, to: Pt) -> Option<Pt> {
    let (dx, dy) = (to.0 - from.0, to.1 - from.1);
    let d = dx.hypot(dy);
    (MIN_STEP..=MAX_STEP).contains(&d).then(|| (dx / d, dy / d))
}

/// 站在 `at`、朝 `dir` 走的她，算不算朝着站在 `ally` 的这个友方英雄（生命 `hp` / `max`）：生命低于 `p.low`%，中心距离在
/// `p.reach` 以内，方向差不超过 `p.cone` 度。
pub fn draws(p: &Params, at: Pt, dir: Pt, ally: Pt, hp: usize, max: usize) -> bool {
    if max == 0 || hp * 100 >= max * p.low {
        return false;
    }
    let (dx, dy) = (ally.0 - at.0, ally.1 - at.1);
    let d = dx.hypot(dy);
    if d < 1.0 || d > p.reach as f64 {
        return false;
    }
    (dx * dir.0 + dy * dir.1) / d >= (p.cone as f64).to_radians().cos() - 1e-9
}

/// 她走的方向和她到 `ally` 的方向差几度（日志）。
pub fn off_by(at: Pt, dir: Pt, ally: Pt) -> f64 {
    let (dx, dy) = (ally.0 - at.0, ally.1 - at.1);
    let d = dx.hypot(dy).max(1.0);
    ((dx * dir.0 + dy * dir.1) / d).clamp(-1.0, 1.0).acos().to_degrees()
}

/// 加速本身：`HOLD` tick、移速 +`p.ms`%。
pub fn haste(p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(SALVATION, HOLD);
    b.move_speed_mult = p.ms as i32;
    b
}

// ===================== 原生效果 =====================

/// 祈愿圈里的一个友方英雄（副本在主包的治疗前面调它）：生命低就多回复。
struct Wish;

impl StableEffectType for Wish {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let target = input.target_id;
        let Some((hp, max)) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        if !low(hp, max) {
            return;
        }
        let ap = sim.get_entity(caster).map_or(0, |e| e.stat().magic_power);
        let more = bonus(ap);
        sim.heal(caster, target, more);
        if let Some(k) = counted("wish") {
            let name = sim.get_entity(target).and_then(|e| e.name()).unwrap_or_default();
            wlog(format!("{} WISH {name}#{target} at {hp}/{max} ({}%): +{more} more (ap {ap}) #{k}", head(sim, caster),
                         hp * 100 / max.max(1)));
        }
    }
}

// ===================== 被动：拯救 =====================

fn fpos(e: &StableEntity<'_, '_>) -> Pt {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

/// 拯救（每个索拉卡一份，两边都选她各算各的）：每 `LOOK` tick 看一次她走的方向，朝着附近生命低的友方英雄就续上加速。
/// 她死了什么都不做（死了的英雄的被动不动；复活后从头量方向）。
#[derive(Clone, Default)]
struct Salvation {
    p: Params,
    /// 上一次看时她站的地方（刚出生、死了：没有）。
    last: Option<Pt>,
    next: usize,
    /// 上一次看完加速挂着没有。
    on: bool,
}

impl Salvation {
    /// 她走的方向 `dir` 上，第一个算数的友方英雄（她自己、死了的、选不中的不算——英雄联盟 V11.2 起骑在别人身上的悠米不算）：
    /// (编号, 生命, 最大生命, 位置)。只读英雄列表，召唤物、分身不在里面；生命先看（最便宜，多数人不低）。
    fn ally_ahead(&self, sim: &StableSim<'_>, me: usize, team: usize, at: Pt, dir: Pt) -> Option<(usize, usize, usize, Pt)> {
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            if id == me {
                continue;
            }
            let Some(e) = sim.get_entity(id) else { continue };
            if e.team() != team || !e.is_alive() {
                continue;
            }
            let (hp, max) = e.hp();
            if max == 0 || hp * 100 >= max * self.p.low || !e.is_targetable() {
                continue;
            }
            let pos = fpos(&e);
            if draws(&self.p, at, dir, pos, hp, max) {
                return Some((id, hp, max, pos));
            }
        }
        None
    }
}

impl StablePassive for Salvation {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.last = None;
        self.next = 0;
        self.on = false;
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: the add-on's Soraka (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        if now < self.next {
            return;
        }
        self.next = now + LOOK;
        let Some((at, team, alive)) = sim.get_entity(me).map(|e| (fpos(&e), e.team(), e.is_alive())) else { return };
        if !alive {
            self.last = None;
            self.on = false;
            return;
        }
        let from = self.last.replace(at);
        let ahead = from.and_then(|f| heading(f, at)).and_then(|dir| self.ally_ahead(sim, me, team, at, dir).map(|a| (dir, a)));
        let Some((dir, (ally, hp, max, ally_at))) = ahead else {
            if self.on {
                sim.entity_remove_buff(me, SALVATION);
                self.on = false;
            }
            return;
        };
        // one instance, its time reset (a host without entity_stack_buff: taken off and put on again)
        let b = haste(&self.p);
        if sim.entity_stack_buff(me, &b, 1, true) == 0 {
            sim.entity_remove_buff(me, SALVATION);
            sim.add_buff(me, &b);
        }
        if !self.on {
            self.on = true;
            if let Some(k) = counted("salvation") {
                let name = sim.get_entity(ally).and_then(|e| e.name()).unwrap_or_default();
                let d = (ally_at.0 - at.0).hypot(ally_at.1 - at.1);
                wlog(format!(
                    "{} SALVATION #{k}: toward {name}#{ally} at {hp}/{max} ({}%), {d:.0} away, {:.0} deg off -> +{}% move speed",
                    head(sim, me),
                    hp * 100 / max.max(1),
                    off_by(at, dir, ally_at),
                    self.p.ms
                ));
            }
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
        "=== {ID} v{VERSION} (Soraka: Wish heals {BONUS}% more on allied champions under {LOW_HP}% health; Salvation +{MS}% move speed toward them) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:wish"), Wish);
    module.add_native_passive(PASSIVE, Salvation::default());
    host.log(LogLevel::Info, "league_soraka loaded (Wish heals more on allied champions at low health, Salvation hastes her toward them).");
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
    fn under_forty_percent_is_low() {
        assert!(low(399, 1000));
        assert!(!low(400, 1000), "exactly 40% is not below it");
        assert!(!low(1000, 1000));
        assert!(low(1, 1000));
        assert!(!low(0, 0), "no maximum read: not low");
    }

    #[test]
    fn the_bonus_is_half_the_main_heal() {
        assert_eq!(bonus(0), 110);
        // 300 ability power: the main heal 220 + 180 = 400, half of it more
        assert_eq!(bonus(300), 200);
        assert_eq!(HEAL + HEAL_AP * 300 / 100 + bonus(300), 600, "League's x1.5 under 40%");
    }

    #[test]
    fn the_copy_calls_wish_first_in_the_main_heal() {
        let copy = include_str!("../override/league_soraka.data_champion");
        let v = copy.replace("\r\n", "\n");
        // the ult's slot to the next top-level key (the view lists)
        let ult = &v[v.find("\n  \"ult\": {").expect("no ult in the copy")..];
        let ult = &ult[..ult.find("\n  \"view_projectiles\"").unwrap_or(ult.len())];
        let at = ult.find("\"effect_ref\": \"league_soraka:wish\"").expect("the copy's ult never calls league_soraka:wish");
        let heal = ult.find("\"type\": \"Heal\"").expect("no Heal in the copy's ult");
        assert!(at < heal, "the add-on's step must come before the main pack's heal (health read before it)");
        assert!(ult.contains(&format!("\"amount\": {HEAL},")) && ult.contains(&format!("\"ap_ratio\": {HEAL_AP},")),
                "the main pack's Wish is no longer {HEAL} + {HEAL_AP}% AP: update HEAL / HEAL_AP");
        assert_eq!(v.matches("league_soraka:wish").count(), 1);
        assert!(ult.contains("description.league_soraka_addon.ult"));
    }

    #[test]
    fn salvation_params_are_the_copys() {
        assert_eq!(Params::default(), Params { ms: 90, low: 40, reach: 250000, cone: 45 });
        let copy = include_str!("../override/league_soraka.data_champion").replace("\r\n", "\n");
        let at = copy.find(&format!("\"passive_ref\": \"{PASSIVE}\"")).expect("the copy has no league_soraka:salvation");
        let body = &copy[at..];
        let json = &body[body.find('{').unwrap()..=body.find('}').unwrap()];
        assert_eq!(parse_params(json), Params::default(), "{json}");
        for k in ["ms", "low", "reach", "cone"] {
            assert!(json.contains(&format!("\"{k}\"")), "{k} in the copy's params");
        }
        assert_eq!(parse_params(r#"{"ms": 70, "cone": 400, "x": 1}"#), Params { ms: 70, cone: 180, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_copy_keeps_ws_own_haste_under_another_name() {
        // W's 30% for 2 s stays the main pack's (the classic sim: without it W is cast 7.6 times a game less); the
        // passive's haste has a name of its own, so neither cuts the other short
        let copy = include_str!("../override/league_soraka.data_champion").replace("\r\n", "\n");
        let main = include_str!("../../../league/champion/league_soraka.data_champion").replace("\r\n", "\n");
        let w_of = |s: &str| s[s.find("\n  \"skill2\": {").unwrap()..s.find("\n  \"ult\": {").unwrap()].to_string();
        let (w_copy, w_main) = (w_of(&copy), w_of(&main));
        assert_eq!(w_copy.replace("description.league_soraka_addon.skill2", "description.league_soraka.skill2"), w_main,
                   "the copy's W is the main pack's but for its text");
        assert!(w_main.contains(&format!("\"name\": \"{W_HASTE}\"")), "the main pack's W no longer hastes her");
        assert!(SALVATION != W_HASTE && !copy.contains(SALVATION), "the passive's haste is the add-on's own");
    }

    #[test]
    fn standing_or_blinking_is_no_heading() {
        assert_eq!(heading((0.0, 0.0), (0.0, 0.0)), None);
        assert_eq!(heading((0.0, 0.0), (299.0, 0.0)), None, "an attack's shuffle");
        assert_eq!(heading((0.0, 0.0), (3000.0, 0.0)), Some((1.0, 0.0)), "three ticks of walking");
        assert_eq!(heading((0.0, 0.0), (0.0, -5700.0)), Some((0.0, -1.0)), "running at +90%");
        assert_eq!(heading((0.0, 0.0), (30_001.0, 0.0)), None, "a blink or a respawn");
    }

    #[test]
    fn toward_a_nearby_ally_below_forty_percent() {
        let p = Params::default();
        let (at, east) = ((500_000.0, 500_000.0), (1.0, 0.0));
        let ally = (600_000.0, 500_000.0);
        assert!(draws(&p, at, east, ally, 399, 1000));
        assert!(!draws(&p, at, east, ally, 400, 1000), "40% is not below 40%");
        assert!(!draws(&p, at, east, ally, 0, 0), "no maximum read");
        assert!(!draws(&p, at, (-1.0, 0.0), ally, 100, 1000), "walking away");
        assert!(!draws(&p, at, (0.0, 1.0), ally, 100, 1000), "walking past (90 deg)");
        // the cone: 44 deg off counts, 46 does not
        let off = |deg: f64| (deg.to_radians().cos(), deg.to_radians().sin());
        assert!(draws(&p, at, off(44.0), ally, 100, 1000));
        assert!(draws(&p, at, off(45.0), ally, 100, 1000), "45 is inside");
        assert!(!draws(&p, at, off(46.0), ally, 100, 1000));
        assert!((off_by(at, off(30.0), ally) - 30.0).abs() < 1e-6);
        // nearby: 2500 units (250000)
        assert!(draws(&p, at, east, (750_000.0, 500_000.0), 100, 1000));
        assert!(!draws(&p, at, east, (750_001.0, 500_000.0), 100, 1000));
        assert!(!draws(&p, at, east, at, 100, 1000), "on top of her: no direction");
    }

    #[test]
    fn the_haste_is_one_short_buff() {
        let b = haste(&Params::default());
        assert_eq!((b.name(), b.move_speed_mult, b.duration_tick), (SALVATION, 90, HOLD));
        assert_eq!(b.duration_kind, BuffDurationV1::Time.code());
        assert!(HOLD > LOOK, "renewed every look before it runs out (a buff of n ticks shows on n - 1)");
        assert!(SALVATION.len() <= BUFF_NAME_CAP);
    }
}
