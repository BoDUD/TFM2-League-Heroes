//! 「备好式」技能格替 AI 按（用户 2026-10-17：「莎弥拉和卡牌用附加包在合适时机替AI按R，主包保持现在这样」，
//! 之后：大嘴的 R、卡密尔的 E 同样不按）。
//!
//! 这些格子要么只是 3 tick 的「备好」动作（真技能由主包数据在备好期间自己判断时机放出，用不上就退还冷却），要么伤害
//! 全在落地之后。游戏 0.6.4 的 AI 几乎不按（只读观察包，每 10 分钟：莎弥拉 R 0.2 次、崔斯特 R 0.7 次、克格莫 R 0.6–0.9
//! 次，卡密尔 E 每分钟 0.5 次；多数英雄的 R 3–9 次），格子里加 200、1000 的护盾、一次搜敌方英雄、把施放目标放宽都没用。
//! 本包不换主包的英雄（没有 `override/`），只加一个 AI 钩子 `league_ult_press:ult`，在合适的时候替 AI 按下，之后全是
//! 主包（或别的附加包）的数据：
//!
//! - 莎弥拉（`league_samira`，R `Targeting EnemyChampion`，射程 `SAMIRA_RANGE`）：R 好了、射程内有敌方英雄——按 R，
//!   目标是最近的那个。S 评价时这一下就放出「炼狱扳机」，不到 S 就备好 330 tick，期间到了 S 再放。
//!   S 要连着换五种出手打中英雄（枪 / 剑普攻、Q、E 冲刺、落地的 W 旋转），一下打不中 9 秒就掉。游戏的 AI 几乎不对英雄放
//!   E、Q 多半打小兵，40 局一次都没到 S（用户选「帮她连招攒评价」）：R 不按时，`SAMIRA_E_RANGE` 内有敌方英雄、她生命
//!   不低于 `SAMIRA_E_HP`、目标身边 `SAMIRA_E_RANGE` 内的敌方英雄不超过 `SAMIRA_E_CROWD` 个——按 E 冲过去（落地接 W）；
//!   再不然 `SAMIRA_Q_RANGE` 内有敌方英雄、上一下打中英雄的不是 Q——Q 朝他放。其余照旧由 AI 平 A。
//! - 崔斯特（`league_twistedfate`，R `None`）：主包的「命运」备好 600 tick，期间每 10 tick 看一次：他身边 70000 内没有
//!   敌方英雄、360000 内有被我方打过的敌方英雄、那人 60000 内有我方英雄——就揭示敌方英雄、引导后传送过去。本包在
//!   同样的局面才按：他身边 `TF_ALONE` 内没有敌方英雄、生命不低于 `TF_MIN_HP`，而且有个离他 `TF_MIN_FAR` 以外、
//!   `TF_REACH` 以内的我方英雄，`TF_FIGHT` 内贴着敌方英雄（在打架）。
//! - 克格莫（`league_kogmaw`，R `Targeting EnemyChampionRecentlyAttacked`，射程 `KOG_RANGE`）：射程内引擎接受的敌方英雄
//!   （最近被我方打过的）里挑生命比例最低的按 R（大招对残血伤害更高）；一轮三发、之后锁 20 秒都是主包的数据。
//! - 卡密尔（`league_camille`，E `Targeting EnemyChampion`）：E 好了、`CAMILLE_RANGE`（主包 E 的射程；附加包钩墙版是
//!   85000，取小的）内有敌方英雄——按 E，目标是最近的那个；钩索、钩墙、冲向敌人由主包 / league_camille_wall 决定。
//! - 被控住（眩晕、击飞、沉默等）、格子在冷却或还没解锁时不按。冷却由钩子自己看（引擎的「输入合法」不看冷却，
//!   league_pyke 的教训）；引擎不接的命令不下（`is_valid_input`）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ult_press.log`，每次启动游戏重写，上一次的留在 .prev.log。
//! ORDER = 按了；CAST = 冷却真的开始走（按下去了，莎弥拉记下当时的评价）；FIRED = 莎弥拉的真大招放出（主包的
//! `league_samira_r_on`）；TELEPORT = 崔斯特按下之后一 tick 内移动了 `TF_JUMP` 以上；STYLE = 莎弥拉这一局到过的最高评价。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_ult_press";
const VERSION: &str = env!("CARGO_PKG_VERSION");

pub const SAMIRA: &str = "league_samira";
pub const TF: &str = "league_twistedfate";
pub const KOGMAW: &str = "league_kogmaw";
pub const CAMILLE: &str = "league_camille";
/// 主包莎弥拉 R 的射程（ult range）。
pub const SAMIRA_RANGE: f64 = 50_000.0;
/// 主包莎弥拉真大招放出时挂的 buff（吸血 40，120 tick）。
pub const SAMIRA_R_ON: &str = "league_samira_r_on";
/// 主包莎弥拉的评价 E..S（一次只挂一个）。
pub const SAMIRA_GRADES: [&str; 6] =
    ["league_samira_g1", "league_samira_g2", "league_samira_g3", "league_samira_g4", "league_samira_g5", "league_samira_g6"];
/// 主包：上一下打中英雄的是 Q（同一种出手再来只保住评价，不升）。
pub const SAMIRA_LAST_Q: &str = "league_samira_l_q";
/// E（`Targeting EnemyChampion`，主包射程 60000）：这么近有敌方英雄才冲；她生命不低于这个比例；目标身边这么近的敌方
/// 英雄（含目标）不超过这么多个。
pub const SAMIRA_E_RANGE: f64 = 60_000.0;
pub const SAMIRA_E_HP: f64 = 0.4;
pub const SAMIRA_E_CROWD: usize = 2;
/// Q（`Direction`，主包射程 90000，枪弹打中第一个敌人就停）：这么近有敌方英雄才朝他放。
pub const SAMIRA_Q_RANGE: f64 = 70_000.0;
/// 崔斯特：身边这么近有敌方英雄就不按（主包门槛 70000，多留一点）。
pub const TF_ALONE: f64 = 75_000.0;
/// 我方英雄这么近贴着敌方英雄算在打架（主包门槛：敌方英雄 60000 内有我方英雄）。
pub const TF_FIGHT: f64 = 50_000.0;
/// 那个敌方英雄离他这么近以内（主包门槛 360000，少留一点：备好后人还会走）。
pub const TF_REACH: f64 = 340_000.0;
/// 那个我方英雄离他至少这么远才值得传送。
pub const TF_MIN_FAR: f64 = 100_000.0;
/// 生命比例低于这个不传送过去送死。
pub const TF_MIN_HP: f64 = 0.4;
/// 一 tick 内移动超过这么多算传送了（日志用）。
pub const TF_JUMP: f64 = 50_000.0;
/// 主包克格莫 R 的射程（r_range）。
pub const KOG_RANGE: f64 = 130_000.0;
/// 引擎每 tick 最多问几个克格莫 R 的目标（生命比例从低到高）。
const KOG_ASK: usize = 5;
/// 卡密尔 E：主包的射程（league_camille_wall 的副本是 85000）。
pub const CAMILLE_RANGE: f64 = 60_000.0;
/// 按下后这么多 tick 内冷却开始走，就算按下去了；之后这么多 tick 内看有没有放出真大招 / 传送。
const ORDER_FRESH: usize = 30;
const WATCH_AFTER: usize = 700;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ULT_PRESS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ult_press.log");
        }
    }
    PathBuf::from("league_ult_press.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (league_kindred)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;

static COUNTS: LazyLock<Mutex<HashMap<String, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: String) -> Option<usize> {
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
    let name = sim.get_entity(id).and_then(|e| e.name()).unwrap_or_default();
    format!("[{kind} m={} s={} seed={}] t={} {name}#{id}", m(o.match_id), m(o.set_index), sim.seed(), sim.tick())
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 什么时候按（单元测试用） =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一个敌方 / 我方英雄：id、位置、生命比例。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: (f64, f64),
    pub hp: f64,
}

/// `range` 内最近的敌方英雄（莎弥拉的 R、卡密尔的 E）。
pub fn nearest_in(me: (f64, f64), range: f64, enemies: &[Unit]) -> Option<usize> {
    enemies
        .iter()
        .map(|u| (u.id, dist(me, u.at)))
        .filter(|&(_, d)| d <= range)
        .min_by(|a, b| a.1.total_cmp(&b.1))
        .map(|(id, _)| id)
}

/// 崔斯特：他一个人（`TF_ALONE` 内没有敌方英雄）、生命够，远处（`TF_MIN_FAR`..`TF_REACH`）有我方英雄 `TF_FIGHT` 内贴着
/// 敌方英雄 -> `(那个敌方英雄, 那个我方英雄)`，挑离他最近的一组。
pub fn tf_fight(me: (f64, f64), hp: f64, allies: &[Unit], enemies: &[Unit]) -> Option<(usize, usize)> {
    if hp < TF_MIN_HP || enemies.iter().any(|u| dist(me, u.at) <= TF_ALONE) {
        return None;
    }
    let mut best: Option<(usize, usize, f64)> = None;
    for a in allies {
        if dist(me, a.at) < TF_MIN_FAR {
            continue;
        }
        for e in enemies {
            let reach = dist(me, e.at);
            if dist(a.at, e.at) <= TF_FIGHT && reach <= TF_REACH && best.is_none_or(|b| reach < b.2) {
                best = Some((e.id, a.id, reach));
            }
        }
    }
    best.map(|(e, a, _)| (e, a))
}

/// 莎弥拉这一 tick 按什么（先后顺序，引擎接哪个就是哪个）：`ready` = Q、E、R 好了没有，`last_q` = 上一下打中英雄的是 Q。
/// R：射程内最近的敌方英雄；E：`SAMIRA_E_RANGE` 内最近的、她生命够、目标身边不挤；Q：`SAMIRA_Q_RANGE` 内最近的、上一下不是 Q。
pub fn samira_plan(me: (f64, f64), hp: f64, ready: [bool; 3], last_q: bool, enemies: &[Unit]) -> Vec<(char, usize)> {
    let mut plan = Vec::new();
    if ready[2] {
        if let Some(t) = nearest_in(me, SAMIRA_RANGE, enemies) {
            plan.push(('R', t));
        }
    }
    if ready[1] && hp >= SAMIRA_E_HP {
        if let Some(t) = nearest_in(me, SAMIRA_E_RANGE, enemies) {
            let at = enemies.iter().find(|u| u.id == t).map(|u| u.at).unwrap_or(me);
            if enemies.iter().filter(|u| dist(at, u.at) <= SAMIRA_E_RANGE).count() <= SAMIRA_E_CROWD {
                plan.push(('E', t));
            }
        }
    }
    if ready[0] && !last_q {
        if let Some(t) = nearest_in(me, SAMIRA_Q_RANGE, enemies) {
            plan.push(('Q', t));
        }
    }
    plan
}

/// 克格莫：`KOG_RANGE` 内的敌方英雄，生命比例从低到高（前 `KOG_ASK` 个；引擎再看谁最近被我方打过）。
pub fn kog_targets(me: (f64, f64), enemies: &[Unit]) -> Vec<usize> {
    let mut v: Vec<&Unit> = enemies.iter().filter(|u| dist(me, u.at) <= KOG_RANGE).collect();
    v.sort_by(|a, b| a.hp.total_cmp(&b.hp));
    v.into_iter().take(KOG_ASK).map(|u| u.id).collect()
}

/// 放不出技能的控制。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];

fn controlled(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| NO_CAST.iter().any(|k| k.code() == c.kind)))
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// 莎弥拉现在的评价（1..6 = E..S，0 = 没有）。
fn samira_grade(e: &StableEntity<'_, '_>) -> usize {
    SAMIRA_GRADES.iter().rposition(|g| has_buff(e, g)).map_or(0, |i| i + 1)
}

fn grade_name(g: usize) -> &'static str {
    ["-", "E", "D", "C", "B", "A", "S"][g.min(6)]
}

fn hp_share((now, max): (usize, usize)) -> f64 {
    if max > 0 {
        now as f64 / max as f64
    } else {
        1.0
    }
}

fn at(e: &StableEntity<'_, '_>) -> (f64, f64) {
    (e.pos().0 as f64, e.pos().1 as f64)
}

// ===================== AI 钩子 =====================

/// 每个英雄按哪个格子、日志里叫什么。
fn slot_of(name: &str) -> Option<(SkillSlotV1, InputKindV1, &'static str)> {
    match name {
        SAMIRA | TF | KOGMAW => Some((SkillSlotV1::Ult, InputKindV1::Ult, "R")),
        CAMILLE => Some((SkillSlotV1::Skill2, InputKindV1::Skill2, "E")),
        _ => None,
    }
}

#[derive(Clone, Debug)]
struct Order {
    tick: usize,
    why: String,
}

#[derive(Clone, Default)]
struct UltPress {
    /// 最近一次按（`ORDER_FRESH` tick 内冷却开始走就算是它）。
    order: Option<Order>,
    /// 上一次看到的剩余冷却。
    last_cd: Option<usize>,
    /// 按下去的那一 tick（之后 `WATCH_AFTER` tick 内看结果）。
    cast_at: Option<usize>,
    last_pos: Option<(f64, f64)>,
    r_on: bool,
    /// 莎弥拉这一局到过的最高评价、上一次看到的 tick（新的一局 tick 会变小）。
    best_grade: usize,
    last_tick: usize,
    /// 上一次下的命令（哪个格子、哪一 tick）：一串连着按的只记一行日志。
    last_order: Option<(&'static str, usize)>,
}

impl StablePlayerAi for UltPress {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ult")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        slot_of(&init.champion_name).is_some()
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, _base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let (main_key, cands): (&'static str, Vec<(InputV1, &'static str, String)>) = {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            let me = pl.champion()?;
            let (mid, team) = (me.id(), me.team());
            let name = me.name().unwrap_or_default();
            let (slot, kind, key) = slot_of(&name)?;
            let my_at = at(&me);
            if tick < self.last_tick {
                self.best_grade = 0;
            }
            self.last_tick = tick;
            let grade = if name == SAMIRA { samira_grade(&me) } else { 0 };
            if grade > self.best_grade {
                self.best_grade = grade;
                if grade >= 4 {
                    if let Some(k) = counted(format!("{name} style {grade}")) {
                        wlog(format!("{} STYLE {} reached #{k}", head(&sim, mid), grade_name(grade)));
                    }
                }
            }
            // the slot went out when its cooldown starts: the press behind it, or the AI's own
            let cd = me.cooldown(slot);
            let remaining = cd.map(|c| c.remaining);
            if let (Some(0), Some(c)) = (self.last_cd, remaining) {
                if c > 0 {
                    let why = match self.order.take().filter(|o| tick <= o.tick + ORDER_FRESH) {
                        Some(o) => format!("pressed {} ticks before: {}", tick - o.tick, o.why),
                        None => "by the AI itself".to_string(),
                    };
                    let style = if name == SAMIRA { format!(" [style {}]", grade_name(grade)) } else { String::new() };
                    if let Some(k) = counted(format!("{name} cast")) {
                        wlog(format!("{} {key} CAST {why}{style} #{k}", head(&sim, mid)));
                    }
                    self.cast_at = Some(tick);
                }
            }
            self.last_cd = remaining;
            // what the press led to: Samira's real R (S grade), Twisted Fate's jump
            if let Some(t0) = self.cast_at {
                if tick > t0 + WATCH_AFTER {
                    self.cast_at = None;
                } else if name == SAMIRA {
                    if has_buff(&me, SAMIRA_R_ON) && !self.r_on {
                        if let Some(k) = counted(format!("{name} fired")) {
                            wlog(format!("{} R FIRED (S grade) {} ticks after the press #{k}", head(&sim, mid), tick - t0));
                        }
                    }
                } else if name == TF {
                    if let Some(p) = self.last_pos.filter(|p| dist(*p, my_at) >= TF_JUMP) {
                        if let Some(k) = counted(format!("{name} teleport")) {
                            wlog(format!("{} R TELEPORT {:.0} {} ticks after the press #{k}", head(&sim, mid), dist(p, my_at), tick - t0));
                        }
                        self.cast_at = None;
                    }
                }
            }
            self.r_on = name == SAMIRA && has_buff(&me, SAMIRA_R_ON);
            self.last_pos = Some(my_at);
            let ready_of = |s: SkillSlotV1| me.cooldown(s).is_some_and(|c| c.unlocked && c.remaining == 0);
            let ready = ready_of(slot);
            // Samira presses E / Q too, so her R need not be ready
            if !me.is_alive() || controlled(&me) || (!ready && name != SAMIRA) {
                return None;
            }
            let mut allies = Vec::new();
            let mut enemies = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_champion() || !e.is_alive() || !e.is_targetable() || e.id() == mid {
                    continue;
                }
                let u = Unit { id: e.id(), at: at(&e), hp: hp_share(e.hp()) };
                if e.team() == team {
                    allies.push(u);
                } else if sim.is_visible(team, e.id()) {
                    enemies.push(u);
                }
            }
            let press = |t: usize| InputV1::action(kind, InputTargetV1::target(t));
            let cands = match name.as_str() {
                SAMIRA => {
                    let ready3 = [ready_of(SkillSlotV1::Skill), ready_of(SkillSlotV1::Skill2), ready];
                    let plan = samira_plan(my_at, hp_share(me.hp()), ready3, has_buff(&me, SAMIRA_LAST_Q), &enemies);
                    let mut v = Vec::new();
                    for (k, t) in plan {
                        let why = format!("{} [style {}]", who(&sim, t), grade_name(grade));
                        match k {
                            'R' => v.push((InputV1::action(InputKindV1::Ult, InputTargetV1::target(t)), "R", why)),
                            'E' => v.push((InputV1::action(InputKindV1::Skill2, InputTargetV1::target(t)), "E", why)),
                            _ => {
                                // Q is a Direction cast: at him, else at his spot, else toward him
                                let p = enemies.iter().find(|u| u.id == t).map_or(my_at, |u| u.at);
                                let q = |target| InputV1::action(InputKindV1::Skill, target);
                                v.push((q(InputTargetV1::target(t)), "Q", why.clone()));
                                v.push((q(InputTargetV1::pos(p.0.max(0.0) as u64, p.1.max(0.0) as u64)), "Q", why.clone()));
                                v.push((q(InputTargetV1::dir((p.0 - my_at.0) as i64, (p.1 - my_at.1) as i64)), "Q", why));
                            }
                        }
                    }
                    v
                }
                CAMILLE => match nearest_in(my_at, CAMILLE_RANGE, &enemies) {
                    Some(t) => vec![(press(t), key, format!("{} within {CAMILLE_RANGE:.0}", who(&sim, t)))],
                    None => return None,
                },
                KOGMAW => {
                    let v = kog_targets(my_at, &enemies);
                    let n = v.len();
                    v.into_iter()
                        .map(|t| {
                            let hp = enemies.iter().find(|u| u.id == t).map_or(f64::NAN, |u| u.hp);
                            (press(t), key, format!("{} at {:.0}% (lowest first of {n} in range)", who(&sim, t), hp * 100.0))
                        })
                        .collect()
                }
                _ => match tf_fight(my_at, hp_share(me.hp()), &allies, &enemies) {
                    Some((e, a)) => {
                        let far = allies.iter().find(|u| u.id == a).map_or(f64::NAN, |u| dist(my_at, u.at));
                        vec![(press(e), key, format!("{} fighting {} {far:.0} away, nobody near him", who(&sim, a), who(&sim, e)))]
                    }
                    None => return None,
                },
            };
            (key, cands)
        };
        // the first press the engine takes (Kog'Maw's R: only champions his side hit lately; Samira: R, else E, else Q)
        let (input, key, why) = cands.into_iter().find(|(i, _, _)| ctx.is_valid_input(i))?;
        if key == main_key && self.order.as_ref().is_none_or(|o| tick > o.tick + ORDER_FRESH) {
            self.order = Some(Order { tick, why: why.clone() });
        }
        // one ORDER line a burst (the engine may take a few ticks; the hook presses again every tick meanwhile)
        if self.last_order.is_none_or(|(k0, t0)| k0 != key || tick > t0 + ORDER_FRESH) {
            if let Some(k) = counted(format!("player {player} {key} order")) {
                wlog(format!("t={tick} player {player} {key} ORDER: {why} #{k}"));
            }
        }
        self.last_order = Some((key, tick));
        Some(input)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (presses armed slots for the AI: Samira R, Twisted Fate R, Kog'Maw R, Camille E) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(UltPress::default());
    host.log(LogLevel::Info, "league_ult_press loaded (presses Samira's, Twisted Fate's and Kog'Maw's R and Camille's E).");
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

    fn u(id: usize, x: f64, y: f64, hp: f64) -> Unit {
        Unit { id, at: (x, y), hp }
    }

    #[test]
    fn samira_and_camille_press_on_the_nearest_in_range() {
        let enemies = [u(1, 40_000.0, 0.0, 1.0), u(2, 20_000.0, 0.0, 1.0), u(3, 60_000.0, 0.0, 1.0)];
        assert_eq!(nearest_in((0.0, 0.0), SAMIRA_RANGE, &enemies), Some(2));
        assert_eq!(nearest_in((0.0, 0.0), SAMIRA_RANGE, &[u(3, 60_000.0, 0.0, 1.0)]), None); // out of R's range
        assert_eq!(nearest_in((0.0, 0.0), CAMILLE_RANGE, &[u(3, 60_000.0, 0.0, 1.0)]), Some(3)); // E reaches 60000
        assert_eq!(nearest_in((0.0, 0.0), SAMIRA_RANGE, &[]), None);
    }

    #[test]
    fn twisted_fate_presses_only_alone_with_a_fight_far_away() {
        let allies = [u(10, 200_000.0, 0.0, 1.0)];
        let fight = [u(20, 230_000.0, 0.0, 1.0)];
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &allies, &fight), Some((20, 10)));
        // an enemy champion next to him
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &allies, &[u(20, 230_000.0, 0.0, 1.0), u(21, 60_000.0, 0.0, 1.0)]), None);
        // low on health
        assert_eq!(tf_fight((0.0, 0.0), 0.3, &allies, &fight), None);
        // the ally is not fighting (the enemy 80000 from him)
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &allies, &[u(20, 280_000.0, 0.0, 1.0)]), None);
        // the fight is out of R's reach
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &[u(10, 400_000.0, 0.0, 1.0)], &[u(20, 420_000.0, 0.0, 1.0)]), None);
        // the ally is close by: no need to teleport
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &[u(10, 80_000.0, 0.0, 1.0)], &[u(20, 110_000.0, 0.0, 1.0)]), None);
    }

    #[test]
    fn twisted_fate_picks_the_nearest_fight() {
        let allies = [u(10, 300_000.0, 0.0, 1.0), u(11, 0.0, 150_000.0, 1.0)];
        let enemies = [u(20, 320_000.0, 0.0, 1.0), u(21, 0.0, 170_000.0, 1.0)];
        assert_eq!(tf_fight((0.0, 0.0), 1.0, &allies, &enemies), Some((21, 11)));
    }

    #[test]
    fn samira_weaves_r_then_e_then_q() {
        let one = [u(1, 40_000.0, 0.0, 1.0)];
        // all ready, one champion at 40000: R first (fires at S, else arms), then E, then Q
        assert_eq!(samira_plan((0.0, 0.0), 0.9, [true, true, true], false, &one), vec![('R', 1), ('E', 1), ('Q', 1)]);
        // the last hit was a Q: another Q would not climb
        assert_eq!(samira_plan((0.0, 0.0), 0.9, [true, true, false], true, &one), vec![('E', 1)]);
        // low on health: no dash in
        assert_eq!(samira_plan((0.0, 0.0), 0.3, [true, true, false], false, &one), vec![('Q', 1)]);
        // three champions around the target: no dash into them
        let crowd = [u(1, 40_000.0, 0.0, 1.0), u(2, 60_000.0, 0.0, 1.0), u(3, 50_000.0, 20_000.0, 1.0)];
        assert_eq!(samira_plan((0.0, 0.0), 0.9, [false, true, false], false, &crowd), vec![]);
        // out of E's reach (65000), in Q's (70000)
        assert_eq!(samira_plan((0.0, 0.0), 0.9, [true, true, true], false, &[u(1, 65_000.0, 0.0, 1.0)]), vec![('Q', 1)]);
        assert_eq!(samira_plan((0.0, 0.0), 0.9, [true, true, true], false, &[]), vec![]);
    }

    #[test]
    fn kogmaw_asks_the_lowest_first_within_range() {
        let enemies = [u(1, 50_000.0, 0.0, 0.8), u(2, 120_000.0, 0.0, 0.3), u(3, 140_000.0, 0.0, 0.1), u(4, 10_000.0, 0.0, 0.5)];
        // #3 is lowest but out of range
        assert_eq!(kog_targets((0.0, 0.0), &enemies), vec![2, 4, 1]);
        assert!(kog_targets((0.0, 0.0), &[u(3, 140_000.0, 0.0, 0.1)]).is_empty());
        let many: Vec<Unit> = (0..8).map(|i| u(i, 1_000.0 * i as f64, 0.0, 1.0 - 0.1 * i as f64)).collect();
        assert_eq!(kog_targets((0.0, 0.0), &many).len(), KOG_ASK);
    }
}
