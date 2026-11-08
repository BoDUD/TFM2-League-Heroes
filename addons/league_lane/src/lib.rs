//! 对线纪律（用户 2026-11-08：「先让对线冷静」）。
//!
//! 打架记录器（league_fight_log）1189 场的底数：每场 41.8 个人头、每分钟 3.1 个，10:00 前就有 25.9 个（英雄联盟职业赛大约
//! 每分钟 0.8–0.9 个、10 分钟 4–6 个）；阵亡里 50% 是以少打多、17% 死在自家塔下（被越塔）。游戏的 AI 前期一直在打。
//!
//! 一个 AI 钩子（`league_lane:calm`，所有选手），只在 `LANE_END`（10:00）之前、只管「对英雄出手」这一件事，补兵、换线、
//! 打野怪、推塔、放不指着英雄的技能都照旧：
//!
//! - **残血就退**（`Rule::Low`）：自己生命低于 `LOW_HP`%、`DANGER` 内有敌方英雄。
//! - **以少打多就撤**（`Rule::Outnumbered`）：`NEAR` 内的敌方英雄比我方（自己算上）多——对面打野来了。
//! - **不越塔**（`Rule::Dive`）：不对站在对面防御塔射程里（`TOWER_REACH`，塔射程 75000 加一点余量）的英雄出手。
//!
//! 例外：目标生命 `KILL_HP`% 以下、能拿人头时照打；目标在对面塔下时要 `DIVE_KILL_HP`% 以下。
//!
//! 出手（普攻、技能、大招指着敌方英雄）被拦下时改成退回自家最近的塔后 `BEHIND`（没有塔就回基地）；残血或以少打多时，
//! AI 在做别的事（没下新指令、打兵、回城）也先退，往安全的方向走的照旧，到了塔后就不再管。危险过去后再退 `RETREAT_HOLD`
//! tick，不来回抖。
//!
//! 0.1.1（用户 2026-11-08「辅助想回家 想游走全被限制住了」）：往自家基地走（目的地比现在离自家基地近 `HOMEWARD` 以上）
//! 也算往安全的地方走，`RECALL_SAFE` 内没有敌方英雄时回城照旧——以前只认往塔后走，走回家、回城都被改成先退到塔后。
//!
//! 0.1.2（用户 2026-11-08「BUG挺多的 你好好修复吧」）：267 场里一次撤退会断断续续：危险过去后的 `RETREAT_HOLD` 里只拦
//! 对英雄出手、别的指令放行，到了塔后又原地站住，英雄在「往回走」和「去补兵 / 打人」之间每几 tick 换一次（日志里同一个人
//! 一秒开始退好几次）。现在撤退一旦开始就退完：`RETREAT_HOLD` 里所有往别处去的指令都改成往回走；到了塔后还要打英雄时往家里
//! 再退 `STEP_BACK`（不原地僵住），补兵照旧。日志按「一次撤退」（隔 `RETREAT_HOLD` 以上算新的一次）计数。
//!
//! 0.1.3（同一天的日志审查）：拦下的不只是普攻——技能、大招指着敌方英雄也被改成往回走，残血时别的技能（自保、加盾、治疗、
//! 位移）也一样：千珏 10:00 前的「羊灵生息」自救下了 3100 次只放出 150 次（她快死时指着最近的敌人按 R，被改成走回塔下，一路
//! 走到死），薇恩贴脸时的 E、厄斐琉斯的 Q 被拦下（Q 每 tick 重按）。现在只管普攻：技能、大招不论指着谁都照旧（游戏的 AI 和
//! 英雄附加包自己判断），残血 / 以少打多时被改成往回走的只有走路、普攻、没有指令和不安全的回城。泰达米尔、千珏等身上有「不死」
//! 的增益（`undying`）时不算危险：「无尽怒火」开着时他照打（之前 10:00 前的大招只有 9% 放得出去，放出去后的普攻也被拦）。
//!
//! 优先级 `PRIORITY` 排在所有英雄附加包和运营钩子之后（只低于兜底的 league_unlock_guard）：它们下的出手也一样拦。
//! 只看比赛的状态，没有随机数，每个选手自己的钩子实例：服务器预演和客户端重演走的一样。只下走路，不按技能。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_lane.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! 前 `DETAIL_LINES` 次开始退各一行，之后每 `COUNT_EVERY` 次一行累计。效果看 league_fight_log 的 SUM 行（10:00 前的阵亡）。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_lane";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_lane") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 钩子的优先级：英雄附加包（最高 1_000_000）、运营钩子之后，兜底的 league_unlock_guard（最大值）之前。
pub const PRIORITY: i32 = 2_000_000_000;
/// 对线期到几点（tick，10:00）。
pub const LANE_END: usize = 36_000;
/// 多久看一次场上（tick）。
pub const LOOK: usize = 10;
/// 残血：生命低于多少（%）就不再对英雄出手。
pub const LOW_HP: usize = 40;
/// 残血时这么近有敌方英雄才算危险。
pub const DANGER: f64 = 60_000.0;
/// 数人数的范围：这么近的敌方英雄比我方多就是以少打多。
pub const NEAR: f64 = 70_000.0;
/// 塔下：离对面防御塔这么近（塔射程 75000 加余量）。
pub const TOWER_REACH: f64 = 80_000.0;
/// 能拿人头：目标生命不超过多少（%）照打。
pub const KILL_HP: usize = 25;
/// 目标在对面塔下时，生命不超过多少（%）才追。
pub const DIVE_KILL_HP: usize = 10;
/// 退到自家塔后多远（朝自家基地）。
pub const BEHIND: f64 = 15_000.0;
/// 离退守点这么近就算到了。
pub const ARRIVED: f64 = 12_000.0;
/// 危险过去后还退多久（tick）。
pub const RETREAT_HOLD: usize = 120;
/// 往自家基地走：目的地比现在离自家基地近这么多以上。
pub const HOMEWARD: f64 = 20_000.0;
/// 这么近没有敌方英雄时，残血 / 以少打多也照常回城。
pub const RECALL_SAFE: f64 = 45_000.0;
/// 到了塔后还要打英雄时往家里再退多远。
pub const STEP_BACK: f64 = 8_000.0;
/// 地图的大小上限：比这远的坐标（被放逐、藏起来的英雄）不算。
pub const MAP_MAX: f64 = 1_200_000.0;
/// 前多少次开始退各写一行。
const DETAIL_LINES: usize = 40;
/// 之后每多少次写一行累计。
const COUNT_EVERY: usize = 2_000;
/// 一次启动最多写多少行。
const LOG_CAP: usize = 5_000;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);
/// Retreats started by rule (`Rule as usize`), and the ticks an order was changed.
static STARTS: [AtomicUsize; 3] = [AtomicUsize::new(0), AtomicUsize::new(0), AtomicUsize::new(0)];
static TICKS: AtomicUsize = AtomicUsize::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LANE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_lane.log");
        }
    }
    PathBuf::from("league_lane.log")
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

/// Counts a retreat starting; a line for the first few and every `COUNT_EVERY`.
fn note(rule: Rule, detail: impl FnOnce() -> String) {
    STARTS[rule as usize].fetch_add(1, Ordering::Relaxed);
    let n: usize = STARTS.iter().map(|s| s.load(Ordering::Relaxed)).sum();
    if n <= DETAIL_LINES {
        wlog(detail());
    } else if n % COUNT_EVERY == 0 {
        wlog(format!(
            "COUNT retreats so far: low {}, outnumbered {}, no dive {}; ticks with a changed order {}",
            STARTS[Rule::Low as usize].load(Ordering::Relaxed),
            STARTS[Rule::Outnumbered as usize].load(Ordering::Relaxed),
            STARTS[Rule::Dive as usize].load(Ordering::Relaxed),
            TICKS.load(Ordering::Relaxed)
        ));
    }
}

fn clock(t: usize) -> String {
    format!("{}:{:02}", t / 3600, t / 60 % 60)
}

// ===================== 规则 =====================

pub type Pos = (f64, f64);

fn dist(a: Pos, b: Pos) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// An enemy champion seen: entity id, position, health %.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pos,
    pub hp: usize,
}

/// What one look at the match saw, from one champion's side.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct View {
    pub me: Pos,
    pub hp: usize,
    /// Living allied champions, me included.
    pub allies: Vec<Pos>,
    pub foes: Vec<Foe>,
    /// The enemy's standing towers.
    pub enemy_towers: Vec<Pos>,
    /// Where to back off to: behind our nearest standing tower, else our nexus.
    pub safe: Option<Pos>,
    /// Our nexus.
    pub home: Option<Pos>,
    /// A buff keeps the champion from dying (Tryndamere's Undying Rage, Kindred's Lamb's Respite): no danger.
    pub undying: bool,
}

/// Why a champion backs off.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Rule {
    Low = 0,
    Outnumbered = 1,
    Dive = 2,
}

impl Rule {
    fn name(self) -> &'static str {
        match self {
            Rule::Low => "low",
            Rule::Outnumbered => "outnumbered",
            Rule::Dive => "no dive",
        }
    }
}

impl View {
    fn under_their_tower(&self, at: Pos) -> bool {
        self.enemy_towers.iter().any(|t| dist(*t, at) <= TOWER_REACH)
    }

    /// The danger this champion is in, if any: outnumbered first, then low.
    pub fn danger(&self) -> Option<Rule> {
        if self.undying {
            return None;
        }
        let foes = self.foes.iter().filter(|f| dist(f.at, self.me) <= NEAR).count();
        let friends = self.allies.iter().filter(|a| dist(**a, self.me) <= NEAR).count().max(1);
        if foes > friends {
            return Some(Rule::Outnumbered);
        }
        if self.hp < LOW_HP && self.foes.iter().any(|f| dist(f.at, self.me) <= DANGER) {
            return Some(Rule::Low);
        }
        None
    }

    /// The way back, or `None` when already there (or nowhere to go).
    fn retreat(&self) -> Option<InputV1> {
        let safe = self.safe?;
        (dist(self.me, safe) > ARRIVED).then(|| InputV1::move_to(safe.0 as u64, safe.1 as u64))
    }

    /// A step of `STEP_BACK` toward home (behind the tower already, still asked to hit a champion); standing still when
    /// there is no home to step to.
    fn step_back(&self) -> InputV1 {
        let to = match self.home {
            Some(h) if dist(h, self.me) > 1.0 => {
                let k = (STEP_BACK / dist(h, self.me)).min(1.0);
                (self.me.0 + (h.0 - self.me.0) * k, self.me.1 + (h.1 - self.me.1) * k)
            }
            _ => self.me,
        };
        InputV1::move_to(to.0 as u64, to.1 as u64)
    }
}

/// The enemy champion a basic attack is aimed at (skills and ults are never stopped: see [`is_cast`]).
fn aimed_at(base: Option<&InputV1>, foes: &[Foe]) -> Option<Foe> {
    let b = base?;
    if b.kind != InputKindV1::Attack.code() || b.target.kind != InputTargetKindV1::Target.code() {
        return None;
    }
    foes.iter().copied().find(|f| f.id == b.target.target_id)
}

/// A skill, a second skill or an ult: saves, shields, heals, escapes, crowd control - the game's AI's and the hero
/// add-ons' own call, never turned into a walk.
fn is_cast(b: &InputV1) -> bool {
    [InputKindV1::Skill, InputKindV1::Skill2, InputKindV1::Ult].iter().any(|k| k.code() == b.kind)
}

/// What the discipline makes of the AI's order: the order to give instead (`None`: keep it) and why. `holding`: a
/// retreat started a moment ago is still on.
pub fn decide(v: &View, base: Option<&InputV1>, holding: bool) -> (Option<InputV1>, Option<Rule>) {
    // undying (the rage pressed at 15% right after a retreat began): the hold is over too
    let holding = holding && !v.undying;
    let danger = v.danger();
    if let Some(target) = aimed_at(base, &v.foes) {
        let dive = v.under_their_tower(target.at);
        // a kill to take: on, unless it stands under its tower and is not about to fall
        if target.hp <= KILL_HP && (!dive || target.hp <= DIVE_KILL_HP) {
            return (None, None);
        }
        let rule = danger.or(holding.then_some(Rule::Low)).or(dive.then_some(Rule::Dive));
        return match rule {
            // already behind the tower: a step further back rather than walking into the fight
            Some(r) => (Some(v.retreat().unwrap_or_else(|| v.step_back())), Some(r)),
            None => (None, None),
        };
    }
    // not a hit on a champion: a champion in danger, or still backing off from it, keeps going back
    // (a danger always has its foes near: low within DANGER, outnumbered within NEAR)
    let Some(rule) = danger.or(holding.then_some(Rule::Low)) else { return (None, None) };
    // a cast goes: a save, a shield, an escape
    if base.is_some_and(is_cast) {
        return (None, None);
    }
    if let Some(b) = base {
        // walking toward safety already - behind the tower or home: fine
        let to = (b.x as f64, b.y as f64);
        if b.kind == InputKindV1::Move.code()
            && (v.safe.is_some_and(|s| dist(to, s) < dist(v.me, s)) || v.home.is_some_and(|h| dist(to, h) + HOMEWARD < dist(v.me, h)))
        {
            return (None, None);
        }
        // a recall with no foe close: it goes
        if b.kind == InputKindV1::Return.code() && !v.foes.iter().any(|f| dist(f.at, v.me) <= RECALL_SAFE) {
            return (None, None);
        }
    }
    match v.retreat() {
        Some(go) => (Some(go), Some(rule)),
        None => (None, None),
    }
}

// ===================== 钩子 =====================

fn pos(e: &StableEntity<'_, '_>) -> Pos {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn pct((hp, max): (usize, usize)) -> usize {
    if max == 0 {
        100
    } else {
        hp * 100 / max
    }
}

fn look(sim: &StableSim<'_>, me_id: usize, team: usize) -> Option<View> {
    let me = sim.get_entity(me_id)?;
    let undying = (0..me.buff_count()).filter_map(|i| me.buff_at(i)).any(|b| b.undying);
    let mut v = View { me: pos(&me), hp: pct(me.hp()), undying, ..View::default() };
    let mut own_towers = Vec::new();
    let mut own_nexus = None;
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        let at = pos(&e);
        if at.0 > MAP_MAX || at.1 > MAP_MAX {
            continue;
        }
        let ours = e.team() == team;
        match e.kind() {
            Some(EntityKindV1::Champion) if e.is_alive() => {
                if ours {
                    v.allies.push(at);
                } else {
                    v.foes.push(Foe { id: e.id(), at, hp: pct(e.hp()) });
                }
            }
            Some(EntityKindV1::Tower) if e.is_alive() => {
                if ours {
                    own_towers.push(at);
                } else {
                    v.enemy_towers.push(at);
                }
            }
            Some(EntityKindV1::Nexus) if ours => own_nexus = Some(at),
            _ => {}
        }
    }
    v.home = own_nexus;
    let nearest = own_towers.iter().copied().min_by(|a, b| dist(*a, v.me).total_cmp(&dist(*b, v.me)));
    v.safe = match (nearest, own_nexus) {
        (Some(t), Some(n)) => {
            let d = dist(t, n).max(1.0);
            let k = (BEHIND / d).min(1.0);
            Some((t.0 + (n.0 - t.0) * k, t.1 + (n.1 - t.1) * k))
        }
        (Some(t), None) => Some(t),
        (None, n) => n,
    };
    Some(v)
}

/// One champion's laning discipline: its last look and the retreat it is on.
#[derive(Clone, Default)]
pub struct Calm {
    next_look: usize,
    view: Option<View>,
    hold_until: usize,
    /// The last tick an order was changed (a retreat more than `RETREAT_HOLD` after it is a new one).
    last_out: Option<usize>,
}

impl StablePlayerAi for Calm {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:calm")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let tick = ctx.tick();
        if tick >= LANE_END {
            return None;
        }
        let (player, team) = (ctx.player_id(), ctx.team());
        let name = {
            let sim = ctx.sim()?;
            let champ = sim.get_player(player)?.champion()?;
            if !champ.is_alive() {
                self.view = None;
                return None;
            }
            if tick >= self.next_look || tick + LOOK < self.next_look {
                self.next_look = tick + LOOK;
                self.view = look(&sim, champ.id(), team);
            }
            champ.name().unwrap_or_default()
        };
        let v = self.view.as_ref()?;
        let holding = tick < self.hold_until;
        let (out, rule) = decide(v, base.as_ref(), holding);
        if v.danger().is_some() {
            self.hold_until = tick + RETREAT_HOLD;
        }
        let Some(out) = out else { return None };
        TICKS.fetch_add(1, Ordering::Relaxed);
        // a new retreat: the first changed order after a gap (or a match that started over)
        let fresh = self.last_out.is_none_or(|t| tick < t || tick > t + RETREAT_HOLD);
        self.last_out = Some(tick);
        if fresh {
            if let Some(rule) = rule {
                let near = |r: f64| v.foes.iter().filter(|f| dist(f.at, v.me) <= r).count();
                note(rule, || {
                    format!(
                        "RETREAT t={} {name} T{team}: {} (hp {}%, foes within {}k {}, allies {}; the AI's order: {})",
                        clock(tick),
                        rule.name(),
                        v.hp,
                        NEAR as u64 / 1000,
                        near(NEAR),
                        v.allies.iter().filter(|a| dist(**a, v.me) <= NEAR).count(),
                        match base {
                            None => "none".to_string(),
                            Some(b) => match aimed_at(Some(&b), &v.foes) {
                                Some(f) => format!("kind {} on a champion at {}% hp", b.kind, f.hp),
                                None => format!("kind {}", b.kind),
                            },
                        }
                    )
                });
            }
        }
        Some(out)
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (laning discipline before 10:00: back off when low or outnumbered, no tower dives) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Calm::default());
    host.log(LogLevel::Info, "league_lane loaded (laning discipline before 10:00).");
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

    fn hit(id: usize) -> InputV1 {
        InputV1::action(InputKindV1::Attack, InputTargetV1::target(id))
    }

    /// Me mid lane at full health, one foe (#7) 40k ahead at 60%, our tower behind, theirs far.
    fn lane() -> View {
        View {
            me: (480_000.0, 480_000.0),
            hp: 100,
            allies: vec![(480_000.0, 480_000.0)],
            foes: vec![Foe { id: 7, at: (510_000.0, 450_000.0), hp: 60 }],
            enemy_towers: vec![(650_000.0, 310_000.0)],
            safe: Some((370_000.0, 590_000.0)),
            home: Some((100_000.0, 860_000.0)),
            undying: false,
        }
    }

    #[test]
    fn undying_is_no_danger() {
        // Tryndamere raging at 5% (undying 5 s, league_tryndamere_rage FIGHT ON): he hits on, even outnumbered
        let mut v = View { hp: 5, undying: true, ..lane() };
        assert_eq!(decide(&v, Some(&hit(7)), false), (None, None));
        assert_eq!(decide(&v, Some(&hit(7)), true), (None, None), "a retreat begun just before the rage ends with it");
        v.foes.push(Foe { id: 8, at: (450_000.0, 520_000.0), hp: 100 });
        assert_eq!(decide(&v, Some(&hit(7)), false), (None, None));
        // a foe under its tower is still not dived
        let mut dive = View { hp: 5, undying: true, ..lane() };
        dive.foes[0].at = (630_000.0, 330_000.0);
        assert_eq!(decide(&dive, Some(&hit(7)), false).1, Some(Rule::Dive));
        // the rage over (no undying buff): the same hit backs off
        let after = View { hp: 5, ..lane() };
        assert_eq!(decide(&after, Some(&hit(7)), false).1, Some(Rule::Low));
    }

    #[test]
    fn an_even_trade_goes_on() {
        let v = lane();
        assert_eq!(decide(&v, Some(&hit(7)), false), (None, None));
        assert_eq!(decide(&v, None, false), (None, None));
    }

    #[test]
    fn low_health_backs_off_unless_a_kill_is_there() {
        let v = View { hp: 30, ..lane() };
        let (out, rule) = decide(&v, Some(&hit(7)), false);
        assert_eq!(rule, Some(Rule::Low));
        let go = out.unwrap();
        assert_eq!((go.kind, go.x, go.y), (InputKindV1::Move.code(), 370_000, 590_000), "back to our tower");
        // the foe at 20%: take it
        let v2 = View { foes: vec![Foe { hp: 20, ..lane().foes[0] }], ..v.clone() };
        assert_eq!(decide(&v2, Some(&hit(7)), false), (None, None));
        // farming with a foe near: back off too; walking home already: fine
        let farm = hit(500);
        assert_eq!(decide(&v, Some(&farm), false).1, Some(Rule::Low));
        assert_eq!(decide(&v, Some(&InputV1::move_to(400_000, 560_000)), false), (None, None));
        // nobody near: carry on
        let alone = View { foes: vec![Foe { at: (900_000.0, 100_000.0), ..lane().foes[0] }], ..v.clone() };
        assert_eq!(decide(&alone, Some(&farm), false), (None, None));
    }

    #[test]
    fn a_retreat_goes_on_through_the_hold() {
        // the danger just passed (the foe 65k away, beyond DANGER) but the hold is on: farming or walking up waits
        let v = View { hp: 30, foes: vec![Foe { at: (530_000.0, 440_000.0), ..lane().foes[0] }], ..lane() };
        assert_eq!(decide(&v, Some(&hit(500)), true).1, Some(Rule::Low), "a farm order in the hold: still backing off");
        assert_eq!(decide(&v, None, true).1, Some(Rule::Low));
        // and once the hold is over too: the AI's own
        assert_eq!(decide(&v, Some(&hit(500)), false), (None, None));
        // outnumbered with the foes 65k away (beyond DANGER, inside NEAR): backing off, not flipping
        let mut crowd = lane();
        crowd.foes = vec![Foe { id: 7, at: (530_000.0, 440_000.0), hp: 90 }, Foe { id: 8, at: (440_000.0, 530_000.0), hp: 90 }];
        assert_eq!(decide(&crowd, Some(&hit(500)), false).1, Some(Rule::Outnumbered));
    }

    #[test]
    fn going_home_is_safe_too() {
        let v = View { hp: 30, ..lane() };
        // walking home past the tower, or to the fountain: fine
        assert_eq!(decide(&v, Some(&InputV1::move_to(120_000, 840_000)), false), (None, None));
        // a recall with the foe 42k away: walk off first; with it 60k away (beyond RECALL_SAFE): recall
        assert_eq!(decide(&v, Some(&InputV1::return_home()), false).1, Some(Rule::Low));
        let farther = View { foes: vec![Foe { at: (520_000.0, 440_000.0), ..lane().foes[0] }], ..v.clone() };
        assert_eq!(decide(&farther, Some(&InputV1::return_home()), false), (None, None));
        // walking somewhere else (toward the enemy): back off
        assert_eq!(decide(&v, Some(&InputV1::move_to(600_000, 350_000)), false).1, Some(Rule::Low));
    }

    #[test]
    fn outnumbered_backs_off() {
        let mut v = lane();
        v.foes.push(Foe { id: 8, at: (450_000.0, 520_000.0), hp: 100 });
        let (out, rule) = decide(&v, Some(&hit(7)), false);
        assert_eq!(rule, Some(Rule::Outnumbered));
        assert!(out.is_some());
        // an ally comes: 2 v 2, the trade is on again
        v.allies.push((470_000.0, 490_000.0));
        assert_eq!(decide(&v, Some(&hit(7)), false), (None, None));
    }

    #[test]
    fn no_dives_before_ten_minutes() {
        let mut v = lane();
        v.foes[0].at = (630_000.0, 330_000.0);
        let (out, rule) = decide(&v, Some(&hit(7)), false);
        assert_eq!(rule, Some(Rule::Dive));
        assert!(out.is_some());
        // a kill at 20% under the tower is not worth it; at 8% it is
        v.foes[0].hp = 20;
        assert_eq!(decide(&v, Some(&hit(7)), false).1, Some(Rule::Dive));
        v.foes[0].hp = 8;
        assert_eq!(decide(&v, Some(&hit(7)), false), (None, None));
        // a skill thrown at a spot is not a hit on a champion: left alone
        let throw = InputV1::action(InputKindV1::Skill, InputTargetV1::pos(630_000, 330_000));
        v.foes[0].hp = 60;
        assert_eq!(decide(&v, Some(&throw), false), (None, None));
    }

    #[test]
    fn casts_always_go() {
        // low and outnumbered: a save ult on the nearest enemy (Kindred), a condemn on the diver (Vayne), a self shield,
        // a skill on a champion under his tower - all the caster's own call
        let mut v = View { hp: 20, ..lane() };
        v.foes.push(Foe { id: 8, at: (470_000.0, 500_000.0), hp: 100 });
        for cast in [
            InputV1::action(InputKindV1::Ult, InputTargetV1::target(7)),
            InputV1::action(InputKindV1::Skill2, InputTargetV1::target(8)),
            InputV1::action(InputKindV1::Skill, InputTargetV1::NONE),
        ] {
            assert_eq!(decide(&v, Some(&cast), false), (None, None), "{cast:?}");
            assert_eq!(decide(&v, Some(&cast), true), (None, None), "in the hold too");
        }
        // the basic attack is still stopped, and farming backs off
        assert!(decide(&v, Some(&hit(7)), false).0.is_some());
        assert!(decide(&v, Some(&hit(500)), false).0.is_some());
        let mut dive = lane();
        dive.foes[0].at = (630_000.0, 330_000.0);
        assert_eq!(decide(&dive, Some(&InputV1::action(InputKindV1::Skill, InputTargetV1::target(7))), false), (None, None));
    }

    #[test]
    fn a_retreat_holds_a_moment_and_stops_behind_the_tower() {
        // the danger is over but the retreat still holds: no hit yet
        let v = lane();
        assert_eq!(decide(&v, Some(&hit(7)), true).1, Some(Rule::Low));
        // behind our tower already: a step further home rather than walk up to hit
        let home = View { me: (372_000.0, 588_000.0), hp: 30, foes: vec![Foe { at: (400_000.0, 560_000.0), ..lane().foes[0] }], ..lane() };
        let (out, rule) = decide(&home, Some(&hit(7)), false);
        assert_eq!(rule, Some(Rule::Low));
        let step = out.unwrap();
        let to = (step.x as f64, step.y as f64);
        assert!((dist(to, home.me) - STEP_BACK).abs() < 2.0 && dist(to, (100_000.0, 860_000.0)) < dist(home.me, (100_000.0, 860_000.0)), "{to:?}");
        // and when not hitting a champion there, the AI does as it likes
        assert_eq!(decide(&home, Some(&hit(500)), false), (None, None));
    }
}
