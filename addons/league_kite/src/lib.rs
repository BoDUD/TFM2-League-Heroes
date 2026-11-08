//! 拉扯（用户 2026-11-06「对线 打团 拉扯 …」，2026-11-08「还有没完善的功能都帮我完善了」：比赛 AI 第 3 步里的「拉扯」）。
//!
//! 英雄联盟里远程英雄打一下就往后撤一步（在普攻的冷却里走位）：贴上来的近战够不着他，他的输出一点不少。游戏自带的 AI 有
//! `Kiting` / `KitingBack`（docs/native_ai.md），可 11-08 的打架记录里射手被贴脸后还有 28% 死掉。这个钩子（`league_kite:kite`，
//! 所有选手）只补游戏 AI 站着不动的那几 tick：
//!
//! - 他是远程：看他自己的普攻——普攻冷却重新开始的那一 tick 离 AI 让他打的目标多远，最近 `REACH_SAMPLES` 次里最远的超过
//!   `RANGED_MIN`（近战 25000 加两人的身体）就是远程；换成近战形态（杰斯、奈德丽）打几下就不算了；
//! - 普攻在冷却（还剩 `LEAD` tick 以上）、出手的动作做完了（身上没有让他不能自己走的控制 `HELD`：前摇、位移、眩晕、定身……；
//!   沉默、缴械不算）；
//! - 有敌方英雄压上来：`HIT_R` 以内，或者 `THREAT_R`（不超过他的射程减 `MARGIN`）以内、正朝他走（每 tick `CLOSING_MIN` 以上）；
//! - 游戏的 AI 这一 tick 让他普攻（打谁都行：补刀时也躲压上来的人）或者什么都没下。AI 自己在走（它的 Kiting、逃跑、追人）、
//!   放技能、回城都不管；
//!
//! 就朝离那个人远、偏向自家基地（`HOME_BEND`，免得退进墙里、退进敌人堆）的方向走；普攻目标快出射程（离他超过射程减
//! `TARGET_MARGIN`）就停，拉在最远射程上（人已经贴脸、在 `HIT_R` 以内时照退）；普攻还剩 `LEAD` tick 时把 AI 的普攻还回去。
//! 走不动（卡在墙边：`STUCK_TICKS` tick 没挪开 `STUCK_MOVE`）就等下一下普攻。卡莉丝塔不管（她的数据每投一矛都跳）。
//!
//! 优先级 `PRIORITY` 在英雄附加包和 league_macro / league_peel / league_focus 之后、league_lane（10:00 前的对线纪律）之前。只看
//! 比赛状态，没有随机数，每个选手自己的钩子实例：服务器预演和客户端重演走的一样。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kite.log`，每次启动游戏重写，上一次的留在 .prev.log：前
//! `DETAIL_LINES` 次拉扯各一行；每 `COUNT_EVERY` 个「该拉扯的 tick」一行累计——这些 tick 里游戏的 AI 自己在往外走（它自己的
//! Kiting / 逃跑）、朝他走、站着普攻、没下指令、放技能各多少，这个钩子走了多少 tick、几次。效果看 league_fight_log 的 SUM
//! （射手被贴脸后死了几成）。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_kite";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_kite") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 钩子的优先级：英雄附加包（最高 1_000_000）、league_focus（-300000）之后，league_lane（2_000_000_000）之前。
pub const PRIORITY: i32 = 1_500_000_000;
/// 普攻冷却重新开始时离目标多远：记最近这么多次，取最远的当射程。
pub const REACH_SAMPLES: usize = 3;
/// 射程超过这么多才算远程（近战 25000 加两人的身体）。
pub const RANGED_MIN: f64 = 35_000.0;
/// 普攻还剩这么多 tick 就好了：不走了，把 AI 的普攻还回去。
pub const LEAD: usize = 3;
/// 这么近的敌方英雄不管走不走都要躲（近战够得着了）。
pub const HIT_R: f64 = 30_000.0;
/// 这么近、正朝他走的敌方英雄算压上来……
pub const THREAT_R: f64 = 50_000.0;
/// ……（不超过他的射程减这么多）……
pub const MARGIN: f64 = 5_000.0;
/// ……朝他走得至少这么快（每 tick）。
pub const CLOSING_MIN: f64 = 200.0;
/// 敌方英雄怎么走：隔这么多 tick 量一次位移；隔了三倍还没量（看不见了）就从头量。
pub const SAMPLE: usize = 6;
/// 往家的方向偏多少（离压上来的人远的方向算 1）。
pub const HOME_BEND: f64 = 0.5;
/// 走向多远的点（每 tick 重新算，只定方向）。
pub const STEP: f64 = 20_000.0;
/// 普攻目标离他超过射程减这么多就不再退（拉在最远射程上）。
pub const TARGET_MARGIN: f64 = 3_000.0;
/// 拉扯了这么多 tick 还没挪开这么远：卡住了，等下一下普攻。
pub const STUCK_TICKS: usize = 4;
pub const STUCK_MOVE: f64 = 1_000.0;
/// 地图的大小上限：比这远的坐标（被放逐、藏起来的英雄）不算。
pub const MAP_MAX: f64 = 1_200_000.0;
/// 让他不能自己走的控制：普攻的前摇（`Animation`）、位移、击飞、眩晕、定身、嘲讽、恐惧、魅惑（沉默、缴械、禁位移技能不算）。
pub const HELD: [CcKindV1; 8] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::ForceMove,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::Animation,
];
/// 不管的英雄：卡莉丝塔的数据每投一矛都跳（league_kalista）。
pub const NO_KITE: [&str; 1] = ["league_kalista"];
/// 前多少次拉扯各写一行。
const DETAIL_LINES: usize = 40;
/// 每多少个「该拉扯的 tick」写一行累计。
const COUNT_EVERY: usize = 20_000;
/// 一次启动最多写多少行。
const LOG_CAP: usize = 5_000;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);
/// 该拉扯的 tick：一共、游戏的 AI 各在干什么（`Order` 的顺序）、这个钩子走了几 tick、几次（只管日志）。
static MOMENTS: AtomicUsize = AtomicUsize::new(0);
static ORDERS: [AtomicUsize; 5] =
    [AtomicUsize::new(0), AtomicUsize::new(0), AtomicUsize::new(0), AtomicUsize::new(0), AtomicUsize::new(0)];
static STEPS: AtomicUsize = AtomicUsize::new(0);
static RUNS: AtomicUsize = AtomicUsize::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KITE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_kite.log");
        }
    }
    PathBuf::from("league_kite.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    if LINES.fetch_add(1, Ordering::Relaxed) >= LOG_CAP {
        return;
    }
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (memory log-open-once)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

fn clock(t: usize) -> String {
    format!("{}:{:02}", t / 3600, t / 60 % 60)
}

// ===================== 拉扯 =====================

pub type Pos = (f64, f64);

fn dist(a: Pos, b: Pos) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn unit(v: Pos) -> Pos {
    let n = v.0.hypot(v.1);
    if n < 1e-9 {
        (0.0, 0.0)
    } else {
        (v.0 / n, v.1 / n)
    }
}

/// An enemy champion near him: entity id, position, how fast he walks toward him (per tick; below 0: away).
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Threat {
    pub id: usize,
    pub at: Pos,
    pub closing: f64,
}

/// What the hook sees this tick.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Moment {
    pub me: Pos,
    /// our nexus
    pub home: Option<Pos>,
    /// his attack range as his own attacks show it (None: none seen yet)
    pub reach: Option<f64>,
    /// ticks until his attack is ready
    pub cooling: usize,
    /// crowd control keeps him from walking his own way (`HELD`): an attack's wind-up, a push, a stun
    pub busy: bool,
    /// where the unit the AI has him attack stands (None: no attack order)
    pub target: Option<Pos>,
    /// the enemy champions within `THREAT_R`
    pub threats: Vec<Threat>,
}

/// Who presses on him: the nearest enemy champion within `HIT_R`, or within `THREAT_R` (and his `reach` less `MARGIN`)
/// walking at him.
pub fn presser(m: &Moment, reach: f64) -> Option<Threat> {
    let edge = THREAT_R.min(reach - MARGIN);
    m.threats
        .iter()
        .copied()
        .filter(|t| {
            let d = dist(m.me, t.at);
            d <= HIT_R || (d <= edge && t.closing >= CLOSING_MIN)
        })
        .min_by(|a, b| dist(m.me, a.at).total_cmp(&dist(m.me, b.at)))
}

/// The kite: the spot to walk toward this tick and whom he steps away from (None: the AI's order stands).
pub fn kite_step(m: &Moment) -> Option<(Pos, Threat)> {
    let reach = m.reach.filter(|r| *r > RANGED_MIN)?;
    if m.busy || m.cooling <= LEAD {
        return None;
    }
    let t = presser(m, reach)?;
    // the target at the edge of his reach already: hold there (unless the presser is in melee reach)
    if dist(m.me, t.at) > HIT_R && m.target.is_some_and(|p| dist(m.me, p) >= reach - TARGET_MARGIN) {
        return None;
    }
    let away = unit((m.me.0 - t.at.0, m.me.1 - t.at.1));
    let home = m.home.map_or((0.0, 0.0), |h| unit((h.0 - m.me.0, h.1 - m.me.1)));
    let d = unit((away.0 + home.0 * HOME_BEND, away.1 + home.1 * HOME_BEND));
    if d == (0.0, 0.0) {
        return None;
    }
    Some((((m.me.0 + d.0 * STEP).clamp(0.0, MAP_MAX), (m.me.1 + d.1 * STEP).clamp(0.0, MAP_MAX)), t))
}

/// His attack range as his own attacks show it: the distance to the unit the AI had him attack each time the attack's
/// cooldown started again, the farthest of the last `REACH_SAMPLES` (a melee form's attacks bring it down).
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Reach {
    seen: Vec<f64>,
}

impl Reach {
    pub fn observe(&mut self, d: f64) {
        if self.seen.len() == REACH_SAMPLES {
            self.seen.remove(0);
        }
        self.seen.push(d);
    }

    pub fn get(&self) -> Option<f64> {
        self.seen.iter().copied().reduce(f64::max)
    }
}

/// How fast a unit that went from `then` to `now` in `ticks` walked toward `me` (per tick; below 0: away).
pub fn closing(me: Pos, then: Pos, now: Pos, ticks: usize) -> f64 {
    if ticks == 0 {
        return 0.0;
    }
    let toward = unit((me.0 - now.0, me.1 - now.1));
    ((now.0 - then.0) * toward.0 + (now.1 - then.1) * toward.1) / ticks as f64
}

/// What the game's AI has him doing at a moment to kite (counted in the log: its own kiting is a walk away).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Order {
    WalkAway,
    WalkToward,
    Attack,
    Idle,
    Other,
}

impl Order {
    fn slot(self) -> usize {
        self as usize
    }
}

/// The AI's order `base` at `me`, with `from` pressing on him.
pub fn order_of(base: Option<&InputV1>, me: Pos, from: Pos) -> Order {
    let Some(b) = base else { return Order::Idle };
    if b.kind == InputKindV1::Attack.code() {
        Order::Attack
    } else if b.kind == InputKindV1::Move.code() {
        let to = (b.x as f64 - me.0, b.y as f64 - me.1);
        let away = (me.0 - from.0, me.1 - from.1);
        if to.0 * away.0 + to.1 * away.1 > 0.0 {
            Order::WalkAway
        } else {
            Order::WalkToward
        }
    } else {
        Order::Other
    }
}

fn pos(e: &StableEntity<'_, '_>) -> Pos {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn count(order: Order) {
    ORDERS[order.slot()].fetch_add(1, Ordering::Relaxed);
    let n = MOMENTS.fetch_add(1, Ordering::Relaxed) + 1;
    if n.is_multiple_of(COUNT_EVERY) {
        let o: Vec<usize> = ORDERS.iter().map(|c| c.load(Ordering::Relaxed)).collect();
        wlog(format!(
            "COUNT moments to kite {n}: the game's AI walking away {} (its own kiting / running), walking at him {}, attacking \
             (standing) {}, no order {}, casting / recalling {}; this hook stepped {} ticks in {} kites",
            o[0],
            o[1],
            o[2],
            o[3],
            o[4],
            STEPS.load(Ordering::Relaxed),
            RUNS.load(Ordering::Relaxed)
        ));
    }
}

// ===================== 钩子 =====================

#[derive(Clone, Default)]
pub struct Kite {
    reach: Reach,
    /// his attack's cooldown left last tick, and the unit the AI had him attack then
    last_cd: usize,
    last_target: Option<usize>,
    /// enemy champions a moment ago: id, tick, position, how fast he walked at him then
    track: Vec<(usize, usize, Pos, f64)>,
    /// our nexus (it never moves), looked for once
    home: Option<Pos>,
    home_looked: bool,
    /// the kite going on: since which tick, from where (the stuck check)
    run: Option<(usize, Pos)>,
    /// stuck at a wall: no more steps till his next attack
    stuck: bool,
    /// a champion this hook leaves alone (`NO_KITE`), read once
    skip: Option<bool>,
}

impl StablePlayerAi for Kite {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:kite")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let (player, team, tick) = (ctx.player_id(), ctx.team(), ctx.tick());
        let attack_on = base
            .filter(|b| b.kind == InputKindV1::Attack.code() && b.target.kind == InputTargetKindV1::Target.code())
            .map(|b| b.target.target_id);
        let (m, name) = {
            let sim = ctx.sim()?;
            let champ = sim.get_player(player)?.champion()?;
            if !champ.is_alive() {
                self.run = None;
                return None;
            }
            let name = champ.name().unwrap_or_default();
            if *self.skip.get_or_insert_with(|| NO_KITE.contains(&name.as_str())) {
                return None;
            }
            let me = pos(&champ);
            let cd = champ.cooldown(SkillSlotV1::Attack).map_or(0, |c| c.remaining);
            // his attack started again: how far away was the unit the AI had him attack
            if cd > self.last_cd {
                if let Some(t) = self.last_target.and_then(|t| sim.get_entity(t)) {
                    let d = dist(me, pos(&t));
                    if d <= MAP_MAX {
                        self.reach.observe(d);
                    }
                }
                self.stuck = false;
                self.run = None;
            }
            self.last_cd = cd;
            self.last_target = attack_on;
            // melee (or nothing seen yet): nothing more to look at
            if !self.reach.get().is_some_and(|r| r > RANGED_MIN) {
                return None;
            }
            if !self.home_looked {
                self.home_looked = true;
                self.home = (0..sim.entity_count())
                    .filter_map(|i| sim.entity_at(i))
                    .find(|e| e.team() == team && e.kind() == Some(EntityKindV1::Nexus))
                    .map(|e| pos(&e));
            }
            let mut threats = Vec::new();
            for i in 0..sim.player_count() {
                let Some(p) = sim.player_at(i) else { continue };
                if p.team() == team {
                    continue;
                }
                let Some(c) = p.champion() else { continue };
                let at = pos(&c);
                if !c.is_alive() || at.0 > MAP_MAX || at.1 > MAP_MAX || !sim.is_visible(team, c.id()) {
                    continue;
                }
                let id = c.id();
                let walk = match self.track.iter().position(|t| t.0 == id) {
                    Some(k) => {
                        let (_, t0, p0, last) = self.track[k];
                        if tick < t0 || tick >= t0 + 3 * SAMPLE {
                            // out of sight a while (or a new run): measure again
                            self.track[k] = (id, tick, at, 0.0);
                            0.0
                        } else if tick >= t0 + SAMPLE {
                            let v = closing(me, p0, at, tick - t0);
                            self.track[k] = (id, tick, at, v);
                            v
                        } else {
                            last
                        }
                    }
                    None => {
                        self.track.push((id, tick, at, 0.0));
                        0.0
                    }
                };
                if dist(me, at) <= THREAT_R {
                    threats.push(Threat { id, at, closing: walk });
                }
            }
            // the dead and the long unseen (a respawn is a new entity) drop out
            self.track.retain(|t| t.1 <= tick && tick < t.1 + 100 * SAMPLE);
            let target = attack_on.and_then(|t| sim.get_entity(t)).map(|e| pos(&e));
            let m = Moment {
                me,
                home: self.home,
                reach: self.reach.get(),
                cooling: cd,
                busy: (0..champ.cc_count()).filter_map(|i| champ.cc_at(i)).any(|c| HELD.iter().any(|k| k.code() == c.kind)),
                target,
                threats,
            };
            (m, name)
        };
        let Some((to, from)) = kite_step(&m) else {
            self.run = None;
            return None;
        };
        // a moment to kite: what the game's AI does with it (its own kiting is a walk away)
        let order = order_of(base.as_ref(), m.me, from.at);
        count(order);
        if !matches!(order, Order::Attack | Order::Idle) || self.stuck {
            self.run = None;
            return None;
        }
        let fresh = match self.run {
            Some((t0, p0)) => {
                if tick >= t0 + STUCK_TICKS && dist(m.me, p0) < STUCK_MOVE {
                    // against a wall: wait for the next attack
                    self.stuck = true;
                    self.run = None;
                    return None;
                }
                false
            }
            None => true,
        };
        let out = InputV1::move_to(to.0.round() as u64, to.1.round() as u64);
        if !ctx.is_valid_input(&out) {
            return None;
        }
        if fresh {
            self.run = Some((tick, m.me));
            let n = RUNS.fetch_add(1, Ordering::Relaxed) + 1;
            if n <= DETAIL_LINES {
                wlog(format!(
                    "KITE #{n} t={} {name} T{team}: #{} {:.0}k away walking {:.0}/tick at him, reach {:.0}k, attack ready in {} \
                     ticks, the AI {order:?}: steps toward ({:.0},{:.0})",
                    clock(tick),
                    from.id,
                    dist(m.me, from.at) / 1000.0,
                    from.closing,
                    m.reach.unwrap_or(0.0) / 1000.0,
                    m.cooling,
                    to.0,
                    to.1
                ));
            }
        }
        STEPS.fetch_add(1, Ordering::Relaxed);
        Some(out)
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (kiting: a ranged champion steps away between attacks from a champion pressing on him) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Kite::default());
    host.log(LogLevel::Info, "league_kite loaded (ranged champions kite between attacks).");
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

    const ME: Pos = (500_000.0, 500_000.0);
    /// our nexus to the south-west
    const HOME: Pos = (100_000.0, 900_000.0);

    fn moment(threats: Vec<Threat>) -> Moment {
        Moment { me: ME, home: Some(HOME), reach: Some(55_000.0), cooling: 20, busy: false, target: None, threats }
    }

    fn diver(d: f64, closing: f64) -> Threat {
        // to the north-east of him, walking at him
        Threat { id: 7, at: (ME.0 + d * 0.6, ME.1 - d * 0.8), closing }
    }

    #[test]
    fn a_ranged_champion_steps_away_from_a_diver_while_his_attack_cools() {
        let m = moment(vec![diver(40_000.0, 900.0)]);
        let (to, from) = kite_step(&m).expect("kites");
        assert_eq!(from.id, 7);
        // farther from the diver, and toward home (south-west) more than straight away
        assert!(dist(to, m.threats[0].at) > dist(ME, m.threats[0].at) + 15_000.0, "{to:?}");
        assert!(dist(to, HOME) < dist(ME, HOME), "{to:?}");
    }

    #[test]
    fn only_between_attacks_and_only_for_ranged_champions() {
        let near = vec![diver(40_000.0, 900.0)];
        // attack almost ready: hand the attack back
        assert_eq!(kite_step(&Moment { cooling: LEAD, ..moment(near.clone()) }), None);
        assert!(kite_step(&Moment { cooling: LEAD + 1, ..moment(near.clone()) }).is_some());
        // the attack's wind-up (or any crowd control) still on him
        assert_eq!(kite_step(&Moment { busy: true, ..moment(near.clone()) }), None);
        // melee (his attacks land from 28k), or none seen yet
        assert_eq!(kite_step(&Moment { reach: Some(28_000.0), ..moment(near.clone()) }), None);
        assert_eq!(kite_step(&Moment { reach: None, ..moment(near) }), None);
    }

    #[test]
    fn a_champion_standing_off_is_no_diver_but_one_in_melee_reach_is() {
        // 40k away, not walking at him (or walking away): nothing to dodge
        assert_eq!(kite_step(&moment(vec![diver(40_000.0, 0.0)])), None);
        assert_eq!(kite_step(&moment(vec![diver(40_000.0, -500.0)])), None);
        // 25k away, standing: in melee reach, step away
        assert!(kite_step(&moment(vec![diver(25_000.0, 0.0)])).is_some());
        // walking at him from beyond his reach less the margin (55k - 5k): not yet
        assert_eq!(kite_step(&moment(vec![diver(52_000.0, 900.0)])), None);
        // the nearest of two
        let two = vec![diver(45_000.0, 900.0), Threat { id: 8, at: (ME.0 - 35_000.0, ME.1), closing: 600.0 }];
        assert_eq!(kite_step(&moment(two)).map(|(_, t)| t.id), Some(8));
    }

    #[test]
    fn he_holds_at_the_edge_of_his_reach_from_the_target() {
        let d = diver(40_000.0, 900.0);
        // his target (the diver himself) 53k away: at the edge of 55k less 3k, hold
        let edge = Moment { target: Some((ME.0 + 53_000.0, ME.1)), ..moment(vec![d]) };
        assert_eq!(kite_step(&edge), None);
        // the target well inside his reach: step
        let inside = Moment { target: Some((ME.0 + 30_000.0, ME.1)), ..moment(vec![d]) };
        assert!(kite_step(&inside).is_some());
        // the diver in melee reach: step even with the target at the edge
        let close = Moment { target: Some((ME.0 + 53_000.0, ME.1)), ..moment(vec![diver(20_000.0, 900.0)]) };
        assert!(kite_step(&close).is_some());
    }

    #[test]
    fn his_reach_is_read_from_his_own_attacks() {
        let mut r = Reach::default();
        assert_eq!(r.get(), None);
        for d in [52_000.0, 48_000.0, 55_000.0] {
            r.observe(d);
        }
        assert_eq!(r.get(), Some(55_000.0));
        // a melee form (Jayce's hammer): three attacks from 24-27k and he is melee again
        for d in [24_000.0, 27_000.0, 25_000.0] {
            r.observe(d);
        }
        assert_eq!(r.get(), Some(27_000.0));
    }

    #[test]
    fn closing_is_his_own_walk_toward_him() {
        // 6 ticks, 6000 straight at him: 1000 a tick
        assert!((closing(ME, (ME.0 + 46_000.0, ME.1), (ME.0 + 40_000.0, ME.1), 6) - 1_000.0).abs() < 1e-6);
        // walking across (north): nothing toward him
        assert!(closing(ME, (ME.0 + 40_000.0, ME.1 + 3_000.0), (ME.0 + 40_000.0, ME.1 - 3_000.0), 6).abs() < 80.0);
        // walking away
        assert!(closing(ME, (ME.0 + 40_000.0, ME.1), (ME.0 + 46_000.0, ME.1), 6) < -900.0);
        assert_eq!(closing(ME, (0.0, 0.0), (1.0, 1.0), 0), 0.0);
    }

    #[test]
    fn the_game_ais_own_walk_is_counted_apart() {
        let from = (ME.0 + 30_000.0, ME.1);
        let away = InputV1::move_to(450_000, 500_000);
        let toward = InputV1::move_to(560_000, 500_000);
        let hit = InputV1::action(InputKindV1::Attack, InputTargetV1::target(7));
        let cast = InputV1::action(InputKindV1::Skill, InputTargetV1::target(7));
        assert_eq!(order_of(Some(&away), ME, from), Order::WalkAway);
        assert_eq!(order_of(Some(&toward), ME, from), Order::WalkToward);
        assert_eq!(order_of(Some(&hit), ME, from), Order::Attack);
        assert_eq!(order_of(Some(&cast), ME, from), Order::Other);
        assert_eq!(order_of(Some(&InputV1::return_home()), ME, from), Order::Other);
        assert_eq!(order_of(None, ME, from), Order::Idle);
    }
}
