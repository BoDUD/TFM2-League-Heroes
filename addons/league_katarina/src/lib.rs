//! 卡特琳娜附加包：智能瞬步 + 贪婪按每次击杀 / 助攻刷新（用户 2026-10-15 选「要附加包」）。
//!
//! 主包是纯数据：瞬步只在两个技能里出现（Q 的匕首落地时跳过去、W 切入时先闪到英雄身边），地上的匕首在哪里数据看不见；
//! 贪婪用佛耶戈的击杀窗口，同一个窗口里只认一次阵亡。`mod.override_info` 把主包的卡特琳娜换成 `override/` 里的副本
//! （tools/kit/build_katarina.py 的 native=1）：数据和主包一样，只是击杀窗口去掉、被动换成本包的 `league_katarina:blades`。
//!
//! 被动每 `EVERY` tick 看一次：
//! - **认出地上的匕首**：她自己的投射物里，连续两次看到停在同一个地方的就是插在地上的匕首（主包的拾取区，活 `d_life` tick；
//!   飞行的飞刀、大招的匕首在动，1 tick 的探测区和 W 的锚点只出现一次）。她走到 `pick_r` 内（被主包捡起）或时间到了就不算了。
//! - **瞬步**：主包的冷却标记 `league_katarina_e_cd` 不在、没被控、没在引导大招时：
//!   - 撤离：生命低于 `e_low`% 而且身边（`SAFE_R`）有敌方英雄——跳到射程（`e_range`）内离最近的敌人最远的那把匕首（至少远
//!     `ESCAPE_GAIN`）；
//!   - 进攻：射程内、旁边（`p_r`）有敌方英雄的匕首，挑那里生命比例最低的英雄；离她太近（`WALK`）的走过去就行，不跳；
//!     匕首旁敌方英雄 `CROWD` 名以上、她生命又不到 `CROWD_HP`% 时不跳进人堆。
//!   跳过去：起点播主包的 `e_out`、落点播 `e_in`、瞬步的动作和音效（台词照主包隔 `vo_gap`），落地对 `E_HIT_R` 内最近的敌人造成
//!   `e_dmg` + `e_ap`% 法强的魔法伤害（主包 E 的数字），主包的冷却标记重新计时；落在匕首上，主包的拾取区当场捡起、旋斩、
//!   把冷却缩到 `e_short`——卡特的匕首循环。
//! - **贪婪**：她参与的每一次英雄击杀（`on_kill` 的英雄、`on_assist`）都把 Q、W 的冷却清掉、瞬步就绪（去掉冷却标记），
//!   播主包的 `p_reset` 和音效；几个人同时阵亡各算一次，不再受主包击杀窗口「一次只认一个」的限制。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。不用全局变量，服务端预模拟和你看的那场各算各的。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_katarina.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_katarina";

/// 主包卡特琳娜的名字（buff、画面、音效都以它开头）。
fn kt(x: &str) -> String {
    format!("league_katarina_{x}")
}

/// 每隔几 tick 看一次。
pub const EVERY: usize = 3;
/// 同一处投射物：两次看到的位置差在这么远内。
pub const SAME: f64 = 50.0;
/// 撤离：身边这么远内有敌方英雄才算危险。
pub const SAFE_R: f64 = 40_000.0;
/// 撤离：落地后离最近的敌人至少比现在远这么多。
pub const ESCAPE_GAIN: f64 = 20_000.0;
/// 进攻：匕首离她不到这么远就走过去，不跳。
pub const WALK: f64 = 15_000.0;
/// 进攻：匕首旁敌方英雄这么多名以上……
pub const CROWD: usize = 3;
/// ……而她生命不到这个百分比时不跳。
pub const CROWD_HP: usize = 60;
/// 落地的伤害打这么远内最近的敌人。
pub const E_HIT_R: f64 = 30_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KATARINA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_katarina.log");
        }
    }
    PathBuf::from("league_katarina.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the simulation thread in game, league_talon_vault)
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

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub e_cd: usize,
    pub e_range: usize,
    pub e_dmg: usize,
    pub e_ap: usize,
    pub e_anim: usize,
    pub e_low: usize,
    pub p_r: usize,
    pub pick_r: usize,
    pub d_life: usize,
    pub vo_gap: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            e_cd: 600,
            e_range: 72_500,
            e_dmg: 60,
            e_ap: 30,
            e_anim: 8,
            e_low: 30,
            p_r: 30_000,
            pick_r: 9_000,
            d_life: 240,
            vo_gap: 240,
        }
    }
}

/// `{"e_cd":600,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "e_cd" => &mut p.e_cd,
            "e_range" => &mut p.e_range,
            "e_dmg" => &mut p.e_dmg,
            "e_ap" => &mut p.e_ap,
            "e_anim" => &mut p.e_anim,
            "e_low" => &mut p.e_low,
            "p_r" => &mut p.p_r,
            "pick_r" => &mut p.pick_r,
            "d_life" => &mut p.d_life,
            "vo_gap" => &mut p.vo_gap,
            _ => continue,
        };
        *slot = v;
    }
    p
}

// ===================== 匕首 =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一处看到过的、她的投射物。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Seen {
    pub at: (f64, f64),
    /// 第一次看到的 tick。
    pub first: usize,
    /// 连续看到了几次。
    pub hits: usize,
    /// 已经被捡起（她走到过拾取范围内）。
    pub gone: bool,
}

/// 地上的匕首：她自己的投射物里停在原地的。每次看一遍更新 `seen`：同一个地方再看到的累加一次，没再看到的删掉。
pub fn update_daggers(seen: &mut Vec<Seen>, now: &[(f64, f64)], tick: usize) {
    let mut next = Vec::with_capacity(now.len());
    for &at in now {
        if next.iter().any(|s: &Seen| dist(s.at, at) <= SAME) {
            continue;
        }
        match seen.iter().find(|s| dist(s.at, at) <= SAME) {
            Some(s) => next.push(Seen { at: s.at, first: s.first, hits: s.hits + 1, gone: s.gone }),
            None => next.push(Seen { at, first: tick, hits: 1, gone: false }),
        }
    }
    *seen = next;
}

/// 能跳的匕首：停住看到两次以上、没被捡、还没到时间。
pub fn live(seen: &[Seen], tick: usize, life: usize) -> Vec<(f64, f64)> {
    seen.iter().filter(|s| s.hits >= 2 && !s.gone && tick < s.first + life).map(|s| s.at).collect()
}

/// 一个敌方英雄：位置、生命百分比。
#[derive(Clone, Copy, Debug)]
pub struct Foe {
    pub at: (f64, f64),
    pub hp_pct: usize,
}

/// 撤离：射程内离最近的敌人最远的匕首（比现在至少远 `ESCAPE_GAIN`）。
pub fn plan_escape(p: &Params, me: (f64, f64), daggers: &[(f64, f64)], foes: &[Foe]) -> Option<(f64, f64)> {
    let gap = |q: (f64, f64)| foes.iter().map(|f| dist(q, f.at)).fold(f64::MAX, f64::min);
    let now = gap(me);
    daggers
        .iter()
        .copied()
        .filter(|&d| dist(me, d) <= p.e_range as f64)
        .map(|d| (d, gap(d)))
        .filter(|&(_, g)| g >= now + ESCAPE_GAIN)
        .max_by(|a, b| a.1.total_cmp(&b.1))
        .map(|(d, _)| d)
}

/// 进攻：射程内、旁边有敌方英雄的匕首，那里生命比例最低的英雄优先；太近的走过去；人堆里她不够血不跳。
pub fn plan_strike(p: &Params, me: (f64, f64), hp_pct: usize, daggers: &[(f64, f64)], foes: &[Foe]) -> Option<(f64, f64)> {
    daggers
        .iter()
        .copied()
        .filter(|&d| {
            let r = dist(me, d);
            r > WALK && r <= p.e_range as f64
        })
        .filter_map(|d| {
            let near: Vec<&Foe> = foes.iter().filter(|f| dist(d, f.at) <= p.p_r as f64).collect();
            if near.is_empty() || (near.len() >= CROWD && hp_pct < CROWD_HP) {
                return None;
            }
            Some((d, near.iter().map(|f| f.hp_pct).min().unwrap_or(100)))
        })
        .min_by_key(|&(_, low)| low)
        .map(|(d, _)| d)
}

// ===================== 小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn has_cc(sim: &StableSim<'_>, id: usize, kinds: &[CcKindV1]) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
    })
}

/// 不能瞬步的状态：硬控、沉默、禁位移技能、正被强制位移。
const NO_BLINK: [CcKindV1; 9] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::BlockSkill,
    CcKindV1::BlockMoveSkill,
    CcKindV1::ForceMove,
];

fn pos(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    sim.get_entity(id).map(|e| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

fn hp_pct(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(100, |e| {
        let (hp, max) = e.hp();
        hp * 100 / max.max(1)
    })
}

fn timed(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

// ===================== 被动 =====================

/// 每个卡特琳娜一份：参数、看到的匕首、计数。
#[derive(Clone, Default)]
struct Blades {
    p: Params,
    seen: Vec<Seen>,
    blinks: usize,
    resets: usize,
}

impl Blades {
    /// 瞬步到 `to`：起点、落点的画面，动作、音效，落地伤害，主包的冷却标记。
    fn blink(&mut self, sim: &mut StableSim<'_>, me: usize, here: (f64, f64), to: (f64, f64), why: &str) {
        let at_me = InputTargetV1::target(me);
        sim.play_view_effect(&kt("e_out"), me, &at_me, 0, 0, 0);
        sim.entity_set_pos(me, to.0.round().max(0.0) as u64, to.1.round().max(0.0) as u64);
        sim.play_view_effect(&kt("e_in"), me, &at_me, 0, 0, 0);
        sim.play_sfx(&kt("e_blink"), me, &at_me);
        if !has_buff(sim, me, &kt("vo_cd")) {
            timed(sim, me, &kt("vo_cd"), self.p.vo_gap);
            sim.play_sfx(&kt("vo_e"), me, &at_me);
        }
        let mut cc = CcV1::of_kind(CcKindV1::Animation, self.p.e_anim as u64);
        cc.set_name("blink");
        sim.apply_cc(me, &cc);
        timed(sim, me, &kt("e_cd"), self.p.e_cd);
        // the landing's strike: the nearest enemy within E_HIT_R (League: the nearest unit)
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let mut best: Option<(f64, usize)> = None;
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() || !u.is_targetable() {
                continue;
            }
            let (x, y) = u.pos();
            let d = dist(to, (x as f64, y as f64));
            if d <= E_HIT_R && best.is_none_or(|b| d < b.0) {
                best = Some((d, u.id()));
            }
        }
        if let Some((_, target)) = best {
            sim.deal_damage(me, target, 0, self.p.e_dmg + ap * self.p.e_ap / 100, AttackTypeV1::Skill);
            sim.play_view_effect(&kt("e_hit"), me, &InputTargetV1::target(target), 0, 0, 0);
        }
        self.blinks += 1;
        if self.blinks <= 80 || self.blinks % 25 == 0 {
            wlog(format!("{} BLINK #{} {why}: {} -> {} ({:.0}), hp {}%, hit {:?}", head(sim, me), self.blinks, pt(here),
                         pt(to), dist(here, to), hp_pct(sim, me), best.map(|b| b.1)));
        }
    }

    /// 贪婪：Q、W 冷却清掉，瞬步就绪。
    fn reset(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        for slot in [SkillSlotV1::Skill, SkillSlotV1::Skill2] {
            let left = sim.get_entity(me).and_then(|e| e.cooldown(slot)).map_or(0, |c| c.remaining);
            if left > 0 {
                sim.entity_reduce_cooldown(me, slot, left);
            }
        }
        sim.entity_remove_buff(me, &kt("e_cd"));
        let at_me = InputTargetV1::target(me);
        sim.play_view_effect(&kt("p_reset"), me, &at_me, 0, 0, 0);
        sim.play_sfx(&kt("reset"), me, &at_me);
        self.resets += 1;
        if self.resets <= 80 {
            wlog(format!("{} RESET #{} ({why}): Q, W and Shunpo ready", head(sim, me), self.resets));
        }
    }
}

impl StablePassive for Blades {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.seen.clear();
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Katarina (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.reset(sim, me, &format!("killed #{victim}"));
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.reset(sim, me, "assist");
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if sim.tick() % EVERY != 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.seen.clear();
            return;
        }
        let team = e.team();
        let targetable = e.is_targetable();
        let Some(here) = pos(sim, me) else { return };
        let tick = sim.tick();
        // her projectiles where they are now; the ones standing still twice running are the daggers on the ground
        let mut now = Vec::new();
        for i in 0..sim.projectile_count() {
            let Some(pr) = sim.projectile_at(i) else { continue };
            if pr.caster_id == me && !pr.is_end {
                now.push((pr.x as f64, pr.y as f64));
            }
        }
        update_daggers(&mut self.seen, &now, tick);
        for s in self.seen.iter_mut() {
            if dist(s.at, here) <= self.p.pick_r as f64 {
                s.gone = true;           // the main pack's zone picked it up (or she stands on it)
            }
        }
        if has_buff(sim, me, &kt("e_cd")) || has_buff(sim, me, &kt("r_ch")) || has_cc(sim, me, &NO_BLINK) || !targetable {
            return;
        }
        let daggers = live(&self.seen, tick, self.p.d_life);
        if daggers.is_empty() {
            return;
        }
        let mut foes = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_champion() || !u.is_alive() || u.team() == team || !u.is_targetable() {
                continue;
            }
            let (x, y) = u.pos();
            let (hp, max) = u.hp();
            foes.push(Foe { at: (x as f64, y as f64), hp_pct: hp * 100 / max.max(1) });
        }
        let mine = hp_pct(sim, me);
        let danger = foes.iter().any(|f| dist(here, f.at) <= SAFE_R);
        if mine < self.p.e_low && danger {
            if let Some(to) = plan_escape(&self.p, here, &daggers, &foes) {
                self.blink(sim, me, here, to, "out");
            }
            return;
        }
        if let Some(to) = plan_strike(&self.p, here, mine, &daggers, &foes) {
            self.blink(sim, me, here, to, "in");
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.seen.clear();
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Katarina's smart Shunpo onto her daggers and Voracity on every takedown) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:blades"), Blades::default());
    host.log(LogLevel::Info, "league_katarina v1 loaded (Katarina's smart Shunpo and Voracity on every takedown).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    fn foe(x: f64, y: f64, hp_pct: usize) -> Foe {
        Foe { at: (x, y), hp_pct }
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"e_cd":540,"e_range":60000,"x":1}"#),
                   Params { e_cd: 540, e_range: 60_000, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn a_dagger_is_what_stands_still() {
        let mut seen = Vec::new();
        // a blade in flight and a dagger on the ground
        update_daggers(&mut seen, &[(0.0, 0.0), (50_000.0, 0.0)], 3);
        assert!(live(&seen, 3, 240).is_empty(), "seen once: not yet a dagger");
        update_daggers(&mut seen, &[(5_000.0, 0.0), (50_000.0, 0.0)], 6);
        assert_eq!(live(&seen, 6, 240), vec![(50_000.0, 0.0)]);
        // its time runs out
        assert!(live(&seen, 243 + 3, 240).is_empty());
        // gone from the world: forgotten
        update_daggers(&mut seen, &[], 9);
        assert!(seen.is_empty());
    }

    #[test]
    fn she_strikes_at_the_dagger_beside_the_weakest() {
        let p = Params::default();
        let me = (0.0, 0.0);
        let daggers = [(40_000.0, 0.0), (0.0, 50_000.0), (10_000.0, 0.0), (90_000.0, 0.0)];
        let foes = [foe(45_000.0, 5_000.0, 80), foe(5_000.0, 55_000.0, 30)];
        // the second dagger: its champion is the weakest; the near one is walked to, the far one out of range
        assert_eq!(plan_strike(&p, me, 100, &daggers, &foes), Some((0.0, 50_000.0)));
        // no champion beside any dagger: no blink
        assert_eq!(plan_strike(&p, me, 100, &daggers, &[foe(-80_000.0, 0.0, 10)]), None);
    }

    #[test]
    fn not_into_a_crowd_when_hurt() {
        let p = Params::default();
        let daggers = [(40_000.0, 0.0)];
        let crowd = [foe(45_000.0, 0.0, 50), foe(40_000.0, 8_000.0, 50), foe(35_000.0, -8_000.0, 50)];
        assert_eq!(plan_strike(&p, (0.0, 0.0), 40, &daggers, &crowd), None);
        assert_eq!(plan_strike(&p, (0.0, 0.0), 90, &daggers, &crowd), Some((40_000.0, 0.0)));
    }

    #[test]
    fn low_she_blinks_away_from_them() {
        let p = Params::default();
        let me = (0.0, 0.0);
        let foes = [foe(15_000.0, 0.0, 100)];
        let daggers = [(30_000.0, 0.0), (-50_000.0, 0.0), (-20_000.0, 0.0)];
        assert_eq!(plan_escape(&p, me, &daggers, &foes), Some((-50_000.0, 0.0)));
        // nothing far enough from them
        assert_eq!(plan_escape(&p, me, &[(30_000.0, 0.0)], &foes), None);
    }

    #[test]
    fn the_names_fit() {
        for x in ["e_cd", "e_out", "e_in", "e_hit", "e_blink", "vo_cd", "vo_e", "p_reset", "reset", "r_ch"] {
            assert!(kt(x).len() <= BUFF_NAME_CAP);
        }
    }
}
