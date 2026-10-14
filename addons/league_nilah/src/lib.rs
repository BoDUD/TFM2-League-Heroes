//! 尼菈附加包（用户 2026-10-13 选「主数据 + 附加包」：附近队友给她的治疗 / 护盾 +15%、她也给队友同样加成，W 在被敌方
//! 攻击时才开，R 选能套中最多人的时机）。主包保持纯数据；`mod.override_info` 把主包的尼菈换成 `override/` 里的副本
//! （`make_override.py` 用 tools/kit/build_nilah.py 的 `native=1` 生成：`passive` 换成本包的 `league_nilah:joy`，说明开头加
//! 【附加包】），本包补数据做不到的几件事：
//!
//! - **喜色川流**（被动 `joy`，英雄联盟的「乐无止境」）：她活着时，她自己和 `near` 以内的友方英雄每次回血、得到护盾，都多
//!   `amp`%。SDK 给被动的接口里没有「被治疗时」，所以每 tick 比对这些英雄的生命和护盾：涨了就按涨的量补一份（补的这份
//!   不再算进下一次）。复活、升级（最大生命变了）、每 tick 不到 `MIN_HEAL` 的自然回血不算。
//! - **轻纱飞漾挑时机**（AI 钩子）：E 两层都用完、轮到 W 时，只有她 `STRUCK_T` tick 内被敌方英雄打过才放；没被打就先普攻，
//!   留着 W 躲真正的集火。
//! - **纵情逐流挑目标**（AI 钩子）：E 还有层数时，冲向射程内血量比例最低的敌方英雄。
//! - **神恩激荡挑时机**（AI 钩子）：R 的圈里有 2 个以上敌方英雄，或者只有 1 个但他血量不到一半、她自己血量不到 40%、
//!   附近没有别的敌方英雄会赶来，才放；否则先普攻，最多等 `R_PATIENCE` tick。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nilah.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_nilah";
const HERO: &str = "league_nilah";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 主包数据的 buff：E 冲刺后的间隔、两层 E 在充能、W 在冷却。
const E_GAP: &str = "league_nilah_e_gap";
const E_X1: &str = "league_nilah_e_x1";
const E_X2: &str = "league_nilah_e_x2";
const W_CD: &str = "league_nilah_w_cd";
/// 本包的记号：她刚被敌方英雄打过（时长 `STRUCK_T`，没有属性）。
const STRUCK: &str = "league_nilah_struck";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_NILAH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_nilah.log");
        }
    }
    PathBuf::from("league_nilah.log")
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

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first).
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

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 回血、护盾多几成（%），多近的友方英雄算（单位：游戏的距离）。
    pub amp: usize,
    pub near: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { amp: 15, near: 100_000 }
    }
}

/// `{"amp":15,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "amp" => p.amp = v,
            "near" => p.near = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 一 tick 涨不到这么多的生命当作自然回血，不加成。
pub const MIN_HEAL: usize = 3;
/// 补的护盾持续多久（主包 R 的护盾 r_sh_t）。
pub const SHIELD_T: usize = 180;
/// 被敌方英雄打过以后多少 tick 内算「正被攻击」，可以放 W。
pub const STRUCK_T: usize = 45;
/// E 的射程（主包 e_range）、R 的圈（r_rad）、R 等人最多等多久、多远的敌方英雄算「会赶来」。
pub const E_REACH: f64 = 55_000.0;
pub const R_RAD: f64 = 38_000.0;
pub const R_PATIENCE: usize = 90;
pub const R_COMING: f64 = 80_000.0;

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 上一 tick 和这一 tick 的一个英雄：活着、生命、最大生命、护盾。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Seen {
    pub alive: bool,
    pub hp: usize,
    pub max: usize,
    pub shield: usize,
}

/// 这 tick 涨了多少生命、多少护盾该加成（复活、最大生命变了、自然回血不算）。一下涨的护盾比最大生命还多的不算：那是别的
/// 英雄数据里的机制护盾（维克托、卡莎、凯尔、卡兹克、辛德拉、崔丝塔娜测等级 / 吸伤害用的 1000000 点、1 tick 的护盾；
/// 2026-10-14 日志里给维克托补了 151537 点、3 秒，等于 3 秒无敌）。
pub fn gains(before: Seen, now: Seen) -> (usize, usize) {
    if !before.alive || !now.alive || before.max != now.max {
        return (0, 0);
    }
    let heal = now.hp.saturating_sub(before.hp);
    let heal = if heal >= MIN_HEAL { heal } else { 0 };
    let shield = now.shield.saturating_sub(before.shield);
    (heal, if shield > now.max { 0 } else { shield })
}

/// 加成的量（按百分之一攒着零头，`rem` 是攒下的零头 x100）。
pub fn bonus(gain: usize, amp: usize, rem: &mut usize) -> usize {
    let total = gain * amp + *rem;
    *rem = total % 100;
    total / 100
}

/// 一个敌方英雄：id、位置、血量比例（%）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: (f64, f64),
    pub hp_pct: usize,
}

/// E 冲向谁：射程内血量比例最低的敌方英雄。
pub fn dash_pick(me: (f64, f64), foes: &[Foe]) -> Option<Foe> {
    foes.iter().filter(|f| dist(me, f.at) <= E_REACH).min_by_key(|f| f.hp_pct).copied()
}

/// R 现在放不放：圈里 2 个以上；1 个时他血少、她血少或附近没别人会来；等太久也放。
pub fn ult_ready(me: (f64, f64), my_hp_pct: usize, foes: &[Foe], waited: usize) -> (bool, &'static str) {
    let inside: Vec<&Foe> = foes.iter().filter(|f| dist(me, f.at) <= R_RAD).collect();
    if inside.len() >= 2 {
        return (true, "two or more in the spin");
    }
    let Some(only) = inside.first() else { return (false, "nobody in the spin") };
    if only.hp_pct <= 50 {
        return (true, "the one in it is below half");
    }
    if my_hp_pct <= 40 {
        return (true, "she is low");
    }
    if !foes.iter().any(|f| f.id != only.id && dist(me, f.at) <= R_COMING) {
        return (true, "no other enemy champion coming");
    }
    if waited >= R_PATIENCE {
        return (true, "waited long enough");
    }
    (false, "one in the spin, others coming")
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn seen(e: &StableEntity<'_, '_>) -> Seen {
    let (hp, max) = e.hp();
    Seen { alive: e.is_alive(), hp, max, shield: e.shield() }
}

/// 场上的敌方英雄（看得见、选得中的）。
fn foes(sim: &StableSim<'_>, team: usize) -> Vec<Foe> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && u.is_champion())
        .map(|u| {
            let (x, y) = u.pos();
            let (hp, max) = u.hp();
            Foe { id: u.id(), at: (x as f64, y as f64), hp_pct: if max == 0 { 100 } else { hp * 100 / max } }
        })
        .collect()
}

// ===================== 被动：喜色川流 =====================

#[derive(Clone, Default)]
struct Joy {
    p: Params,
    /// 每个友方英雄上一 tick 的样子和攒下的零头（生命、护盾）。
    last: HashMap<usize, (Seen, usize, usize)>,
}

impl StablePassive for Joy {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.last.clear();
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _player: usize, me: usize, attacker: usize, damage: usize) {
        let Some(m) = sim.get_entity(me) else { return };
        let team = m.team();
        let by_champion = sim.get_entity(attacker).is_some_and(|a| a.is_champion() && a.team() != team);
        if !by_champion || damage == 0 {
            return;
        }
        let fresh = !has_buff(sim, me, STRUCK);
        sim.entity_remove_buff(me, STRUCK);
        sim.add_buff(me, &BuffV1::timed(STRUCK, STRUCK_T));
        if fresh {
            if let Some(k) = counted("struck") {
                wlog(format!("{} STRUCK by {} ({damage}): W allowed for {STRUCK_T} ticks #{k}", head(sim, me),
                             who(sim, attacker)));
            }
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, team, (x, y)) = (e.is_alive(), e.team(), e.pos());
        let at = (x as f64, y as f64);
        // the allied champions she is near now (herself too), as they are this tick
        let near: Vec<(usize, Seen)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.team() == team)
            .filter(|u| u.id() == me || dist(at, (u.pos().0 as f64, u.pos().1 as f64)) <= self.p.near as f64)
            .map(|u| (u.id(), seen(&u)))
            .collect();
        let mut next = HashMap::new();
        for (id, now) in near {
            let (mut rem_h, mut rem_s) = (0, 0);
            let mut now = now;
            if let Some(&(before, rh, rs)) = self.last.get(&id) {
                rem_h = rh;
                rem_s = rs;
                let (heal, shield) = if alive { gains(before, now) } else { (0, 0) };
                let extra_h = bonus(heal, self.p.amp, &mut rem_h);
                let extra_s = bonus(shield, self.p.amp, &mut rem_s);
                if extra_h > 0 {
                    sim.heal(me, id, extra_h);
                }
                if extra_s > 0 {
                    sim.entity_add_shield(id, extra_s, SHIELD_T);
                }
                if extra_h > 0 || extra_s > 0 {
                    if let Some(k) = counted("joy") {
                        wlog(format!("{} JOY {}: healed {heal} -> +{extra_h}, shield {shield} -> +{extra_s} #{k}",
                                     head(sim, me), who(sim, id)));
                    }
                    // what was added is no gain of the next tick
                    if let Some(u) = sim.get_entity(id) {
                        now = seen(&u);
                    }
                }
            }
            next.insert(id, (now, rem_h, rem_s));
        }
        self.last = next;
    }
}

// ===================== AI 钩子：W、E、R =====================

#[derive(Clone, Default)]
struct PlayAi {
    /// R 第一次想放、被压住的 tick。
    r_wanted: Option<usize>,
}

impl StablePlayerAi for PlayAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:play")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let tick = ctx.tick();
        let Some(b) = base else {
            self.r_wanted = None;
            return None;
        };
        let kind = InputKindV1::from_code(b.kind);
        if kind != Some(InputKindV1::Ult) {
            self.r_wanted = None;
        }
        if !matches!(kind, Some(InputKindV1::Skill2 | InputKindV1::Ult)) {
            return None;
        }
        let target = (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target))
            .then_some(b.target.target_id);
        let player = ctx.player_id();
        enum Do {
            Keep,
            Dash(usize, String),
            Hold(Option<usize>, (u64, u64), String, &'static str),
        }
        let todo = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let (mid, team) = (me.id(), me.team());
            let at = (me.pos().0 as f64, me.pos().1 as f64);
            let (hp, max) = me.hp();
            let my_pct = if max == 0 { 100 } else { hp * 100 / max };
            let all = foes(&sim, team);
            let line = head(&sim, mid);
            let target_pos = target.and_then(|t| sim.get_entity(t)).map_or(me.pos(), |t| t.pos());
            if kind == Some(InputKindV1::Skill2) {
                let gap = has_buff(&sim, mid, E_GAP);
                let veil = has_buff(&sim, mid, E_X1) && has_buff(&sim, mid, E_X2);
                if gap {
                    Do::Keep
                } else if veil {
                    if has_buff(&sim, mid, W_CD) || has_buff(&sim, mid, STRUCK) {
                        Do::Keep
                    } else {
                        Do::Hold(target, target_pos, line, "W HELD: no enemy champion has hit her")
                    }
                } else {
                    match dash_pick(at, &all) {
                        Some(f) if Some(f.id) != target => Do::Dash(f.id, format!(
                            "{line} E {} -> {} ({:.0} away, hp {}%) AIM", target.map_or("-".into(), |t| who(&sim, t)),
                            who(&sim, f.id), dist(at, f.at), f.hp_pct)),
                        _ => Do::Keep,
                    }
                }
            } else {
                let waited = self.r_wanted.map_or(0, |t0| tick.saturating_sub(t0));
                let (go, why) = ult_ready(at, my_pct, &all, waited);
                if go {
                    if let Some(k) = counted("r_go") {
                        wlog(format!("{line} R CAST: {why} (waited {waited}) #{k}"));
                    }
                    self.r_wanted = None;
                    Do::Keep
                } else {
                    if self.r_wanted.is_none() {
                        self.r_wanted = Some(tick);
                    }
                    Do::Hold(target, target_pos, line, if why == "nobody in the spin" { "R HELD: nobody in the spin" }
                             else { "R HELD: one in the spin, others coming" })
                }
            }
        };
        match todo {
            Do::Keep => None,
            Do::Dash(id, line) => {
                let input = InputV1::action(InputKindV1::Skill2, InputTargetV1::target(id));
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                if let Some(k) = counted("e_aim") {
                    wlog(format!("{line} #{k}"));
                }
                Some(input)
            }
            Do::Hold(t, (x, y), line, why) => {
                if let Some(k) = counted(why) {
                    wlog(format!("{line} {why}, attacking instead #{k}"));
                }
                if let Some(t) = t {
                    let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                    if ctx.is_valid_input(&attack) {
                        return Some(attack);
                    }
                }
                Some(InputV1::move_to(x, y))
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
        "=== {ID} v{VERSION} (Nilah: Joy Unending's heals and shields, Jubilant Veil when struck, Slipstream's and Apotheosis's timing) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:joy"), Joy::default());
    module.add_player_input_ai(PlayAi::default());
    host.log(LogLevel::Info, "league_nilah loaded (Joy Unending heals and shields, Jubilant Veil when struck, Slipstream and Apotheosis timing).");
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

    fn s(alive: bool, hp: usize, max: usize, shield: usize) -> Seen {
        Seen { alive, hp, max, shield }
    }

    fn foe(id: usize, x: f64, hp_pct: usize) -> Foe {
        Foe { id, at: (x, 0.0), hp_pct }
    }

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"amp":20,"near":90000,"junk":1}"#);
        assert_eq!((p.amp, p.near), (20, 90_000));
    }

    #[test]
    fn heals_and_shields_count_regen_respawns_and_level_ups_do_not() {
        assert_eq!(gains(s(true, 500, 1000, 0), s(true, 600, 1000, 80)), (100, 80));
        assert_eq!(gains(s(true, 500, 1000, 0), s(true, 502, 1000, 0)), (0, 0)); // regen
        assert_eq!(gains(s(false, 0, 1000, 0), s(true, 1000, 1000, 0)), (0, 0)); // respawn
        assert_eq!(gains(s(true, 500, 1000, 0), s(true, 590, 1090, 0)), (0, 0)); // level up
        assert_eq!(gains(s(true, 500, 1000, 50), s(true, 400, 1000, 20)), (0, 0)); // damage
        // a kit's probe / soak shield (1000000 for a tick) is no shield to amplify
        assert_eq!(gains(s(true, 900, 1000, 250), s(true, 900, 1000, 1_010_250)), (0, 0));
        assert_eq!(gains(s(true, 900, 1000, 0), s(true, 900, 1000, 1000)), (0, 1000));
    }

    #[test]
    fn the_bonus_keeps_its_hundredths() {
        let mut rem = 0;
        assert_eq!(bonus(100, 15, &mut rem), 15);
        assert_eq!(rem, 0);
        // 6 x 15% = 0.9: nothing yet, then 1.8 -> 1 (0.8 kept), then 2.7 -> 1 ...
        assert_eq!(bonus(6, 15, &mut rem), 0);
        assert_eq!(bonus(6, 15, &mut rem), 1);
        assert_eq!(rem, 80);
    }

    #[test]
    fn the_dash_goes_for_the_lowest_in_reach() {
        let me = (0.0, 0.0);
        let a = foe(1, 30_000.0, 70);
        let b = foe(2, -50_000.0, 40);
        let c = foe(3, 60_000.0, 5); // out of reach
        assert_eq!(dash_pick(me, &[a, b, c]).map(|f| f.id), Some(2));
        assert_eq!(dash_pick(me, &[c]), None);
    }

    #[test]
    fn the_spin_waits_for_a_second_champion() {
        let me = (0.0, 0.0);
        let near = foe(1, 20_000.0, 90);
        let coming = foe(2, 60_000.0, 90);
        assert_eq!(ult_ready(me, 90, &[near, foe(3, -30_000.0, 90)], 0).0, true);
        assert_eq!(ult_ready(me, 90, &[near, coming], 0), (false, "one in the spin, others coming"));
        assert_eq!(ult_ready(me, 90, &[near, coming], R_PATIENCE).0, true);
        assert_eq!(ult_ready(me, 30, &[near, coming], 0).0, true);
        assert_eq!(ult_ready(me, 90, &[foe(1, 20_000.0, 45), coming], 0).0, true);
        assert_eq!(ult_ready(me, 90, &[near], 0).0, true); // alone: no one else to wait for
        assert_eq!(ult_ready(me, 90, &[coming], 0).0, false);
    }
}
