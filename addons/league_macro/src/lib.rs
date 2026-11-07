//! 比赛 AI 的运营（用户 2026-11-06：「现在游戏的AI逻辑非常差 非常不像LOL那种顶级的处理方式 … 大龙打完后该干嘛 还有不推基地
//! 之类的 … 我要看起来像极了LOL比赛那种运营和打架」→「直接做第 2 步」）。
//!
//! 运营记录器（league_macro_log）1322 场的底数：到了对面基地（3 人以上、3 秒以上）的 58% 又走掉，基地还在；大龙后 90 秒
//! 平均只有 1.7 个人抱在一起。本包一个 AI 钩子（`league_macro:macro`，所有选手），只在这两件事上替 AI 下运营的指令，打架、
//! 放技能照旧是游戏的 AI 和英雄附加包的：
//!
//! - **推掉基地**（`Intent::Finish`）：自己离对面基地 `FINISH_REACH` 以内、生命 `FINISH_HP`% 以上，对面基地能打
//!   （`is_targetable`：前面的塔倒了），基地 `BASE_NEAR` 内我方活着的英雄 3 个以上、比对面在那里的多——AI 要走开、回城、
//!   打小兵时改成打基地（`ctx.is_valid_input` 不收就走过去）；它在对英雄出手（普攻、技能打 `FIGHT` 内的敌方英雄）照旧。
//! - **大龙后跟强化兵推进**（`Intent::Join`）：莫尔加德（大龙，`Epic`）的 buff 不给英雄，给拿龙一方的小兵
//!   （`epic_minion_buff`，lol_audio 的 OBJECTIVE 行读到的）。我方有强化兵、自己生命 `JOIN_HP`% 以上、`FIGHT` 内没有敌方
//!   英雄时，全队去跟离本队中心最近的那波强化兵，站到兵线上。已经跟上（`WITH_WAVE` 以内）就让 AI 自己打兵、拆塔，
//!   它往对面基地那边走也放行；只在它往回走（目的地比兵线离对面基地远 `BACK_OFF` 以上）、回城时拉回兵线。
//!   0.1.0 站在兵线身后 25000、跟上后 AI 往哪走都拉回：大龙后 90 秒抱团 1.7 -> 3.1 人，推塔却 2.0 -> 1.3 座（830 场）。
//!   0.1.1 压到兵线上：抱团 3.0、推塔 1.6，但拿龙一方之后 90 秒击杀 2.9 / 阵亡 2.9（没有钩子时 3.3 / 2.6）——人少也被拉去
//!   对面塔下。0.1.2 起只在人数不吃亏时推：我方活着的英雄不少于对面，而且至少 `JOIN_MIN_ALIVE` 个。
//!   0.1.2 不管队伍的战术，一律拉全队跟同一波兵；可游戏的战术里有「莫尔加德 buff 用法」（`morgard_use`），七成队伍选的是
//!   分推（1-3-1 / 1-4），都被改成了抱团：880 场大龙后 90 秒推塔 1.66 座，没有钩子时 2.0（用户 2026-11-07「现在做 0.1.3」）。
//!   0.1.3 起照队伍的 `BaronPlan` 来：「全员抱团」照旧；「1-4 分推」`position` 那个位置的选手去带物件对面那一路，交给游戏的
//!   AI（钩子不拉他），另外四个跟离他们最近的那波强化兵；「1-3-1 分推」`position1` / `position2` 两个位置的选手各带一路
//!   边线，交给游戏的 AI，另外三个跟中路的强化兵（离两边基地连线 `MID_NEAR` 以内的几波里离他们最近的，中路没有就近的）。
//!   战术只在有强化兵时才读（`strategy_get_json`）。
//!
//! 每 `SCAN` tick 看一次场上（每个选手自己的钩子实例里，不共用状态：游戏会并行跑好几场），两次之间沿用上次的打算。
//! 只看比赛的状态，没有随机数：服务器预演和客户端重演走的一样。优先级 `PRIORITY` 比英雄附加包低，所以先跑，
//! 英雄的钩子（替 AI 放大招之类）还能在它之后改；只读的观察钩子（回城记录）更低。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_macro.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! 前 `DETAIL_LINES` 次改指令各一行，之后每 `COUNT_EVERY` 次一行累计数。效果看 league_macro_log 的 SUM 行。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_macro";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_macro") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 钩子的优先级：比英雄附加包（1_000_000 上下）先跑，比只读的观察钩子（-2_000_000）后跑。
pub const PRIORITY: i32 = -500_000;
/// 多久看一次场上（tick）。
pub const SCAN: usize = 15;
/// 拿龙一方小兵身上的大龙 buff。
pub const BARON_BUFF: &str = "epic_minion_buff";
/// 推基地：自己离对面基地多近。
pub const FINISH_REACH: f64 = 180_000.0;
/// 推基地：数基地这么近的双方英雄。
pub const BASE_NEAR: f64 = 200_000.0;
/// 跟强化兵推进：我方至少活着几个（而且不少于对面）。
pub const JOIN_MIN_ALIVE: usize = 3;
/// 推基地：自己的生命至少多少（%）。
pub const FINISH_HP: usize = 25;
/// 跟强化兵：自己的生命至少多少（%）。
pub const JOIN_HP: usize = 40;
/// 这么近有敌方英雄就是在打架：不改去跟兵线。
pub const FIGHT: f64 = 80_000.0;
/// 离兵线这么近算跟上了。
pub const WITH_WAVE: f64 = 90_000.0;
/// 跟上兵线后 AI 的走路目的地比兵线离对面基地远这么多，算往回走。
pub const BACK_OFF: f64 = 30_000.0;
/// 战术里大龙 buff 的用法（`strategy_get_json` 的路径）。
pub const MORGARD_USE: &str = "morgard_use";
/// 1-3-1：离两边基地连线这么近的强化兵算中路。
pub const MID_NEAR: f64 = 120_000.0;
/// 前多少次改指令各写一行。
const DETAIL_LINES: usize = 40;
/// 前多少个「分推的人交给游戏 AI」各写一行。
const SPLIT_LINES: usize = 20;
/// 之后每多少次写一行累计。
const COUNT_EVERY: usize = 2_000;
/// 一次启动最多写多少行。
const LOG_CAP: usize = 5_000;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);
/// Champions that started following each order, and the ticks orders were changed.
static FINISHES: AtomicUsize = AtomicUsize::new(0);
static JOINS: AtomicUsize = AtomicUsize::new(0);
static TICKS: AtomicUsize = AtomicUsize::new(0);
/// Split pushers of a Morgard plan left to the game's AI (counted when one starts).
static SPLITS: AtomicUsize = AtomicUsize::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_MACRO_HOOK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_macro.log");
        }
    }
    PathBuf::from("league_macro.log")
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

/// Counts a champion starting to follow an order; a line for the first few and every `COUNT_EVERY`.
fn note(finish: bool, detail: impl FnOnce() -> String) {
    let (f, j) = if finish {
        (FINISHES.fetch_add(1, Ordering::Relaxed) + 1, JOINS.load(Ordering::Relaxed))
    } else {
        (FINISHES.load(Ordering::Relaxed), JOINS.fetch_add(1, Ordering::Relaxed) + 1)
    };
    let n = f + j;
    if n <= DETAIL_LINES {
        wlog(detail());
    } else if n % COUNT_EVERY == 0 {
        wlog(format!(
            "COUNT champions that took an order so far: finish the nexus {f}, join the baron waves {j}, split pushers left to the AI {}; ticks with a changed order {}",
            SPLITS.load(Ordering::Relaxed),
            TICKS.load(Ordering::Relaxed)
        ));
    }
}

/// Counts a split pusher left to the game's AI; a line for the first few.
fn note_split(detail: impl FnOnce() -> String) {
    if SPLITS.fetch_add(1, Ordering::Relaxed) < SPLIT_LINES {
        wlog(detail());
    }
}

fn clock(t: usize) -> String {
    format!("{}:{:02}", t / 3600, t / 60 % 60)
}

// ===================== 打算 =====================

pub type Pos = (f64, f64);

fn dist(a: Pos, b: Pos) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// Distance from `p` to the segment `a`-`b`.
fn seg_dist(p: Pos, a: Pos, b: Pos) -> f64 {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let len2 = dx * dx + dy * dy;
    let t = if len2 == 0.0 { 0.0 } else { (((p.0 - a.0) * dx + (p.1 - a.1) * dy) / len2).clamp(0.0, 1.0) };
    dist(p, (a.0 + t * dx, a.1 + t * dy))
}

/// The team's Morgard (baron) buff plan: `morgard_use` in its strategy.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub enum BaronPlan {
    /// Everyone pushes together (also when the setting can't be read).
    #[default]
    Gather,
    /// The player of this lane (a `LaneV1` code) pushes the lane opposite the objective; the other four group.
    Split14(u32),
    /// Three push mid; the players of these two lanes push a side lane each.
    Split131(u32, u32),
}

/// `LaneV1` names by code, as the strategy document writes them.
const LANES: [&str; 5] = ["Top", "Jungle", "Mid", "Bottom", "Support"];

impl BaronPlan {
    /// Whether the player of this lane is one of the plan's split pushers.
    pub fn splits(self, lane: Option<u32>) -> bool {
        match (self, lane) {
            (BaronPlan::Split14(a), Some(l)) => l == a,
            (BaronPlan::Split131(a, b), Some(l)) => l == a || l == b,
            _ => false,
        }
    }

    pub fn label(self) -> String {
        let name = |l: u32| LANES.get(l as usize).copied().unwrap_or("?");
        match self {
            BaronPlan::Gather => "Gather".to_string(),
            BaronPlan::Split14(a) => format!("Split14 {}", name(a)),
            BaronPlan::Split131(a, b) => format!("Split131 {}+{}", name(a), name(b)),
        }
    }
}

/// The text of `"key": "value"` in a small JSON object.
fn field<'a>(json: &'a str, key: &str) -> Option<&'a str> {
    let rest = &json[json.find(&format!("\"{key}\""))? + key.len() + 2..];
    let rest = &rest[rest.find(':')? + 1..];
    let start = rest.find('"')? + 1;
    let len = rest[start..].find('"')?;
    Some(&rest[start..start + len])
}

/// The plan in the strategy document's `morgard_use`: `"Gather"`, `{"Split14":{"position":"Top"}}` or
/// `{"Split131":{"position1":"Top","position2":"Bottom"}}`; anything else (a lane missing too): Gather.
pub fn baron_plan(json: &str) -> BaronPlan {
    let lane = |key: &str| field(json, key).and_then(|v| LANES.iter().position(|l| *l == v)).map(|i| i as u32);
    if json.contains("\"Split131\"") {
        if let (Some(a), Some(b)) = (lane("position1"), lane("position2")) {
            return BaronPlan::Split131(a, b);
        }
    } else if json.contains("\"Split14\"") {
        if let Some(a) = lane("position") {
            return BaronPlan::Split14(a);
        }
    }
    BaronPlan::Gather
}

/// What one look at the match saw, from one champion's side.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct View {
    pub me: Pos,
    pub hp_pct: usize,
    /// Living allied champions, me included.
    pub allies: Vec<Pos>,
    /// Living enemy champions (entity id, position).
    pub enemies: Vec<(usize, Pos)>,
    /// The enemy nexus (entity id, position, attackable now).
    pub enemy_nexus: Option<(usize, Pos, bool)>,
    pub own_nexus: Option<Pos>,
    /// Our minions carrying the baron buff.
    pub baron_minions: Vec<Pos>,
    /// Our team's Morgard plan (read only while a baron wave is up).
    pub plan: BaronPlan,
    /// I am one of the plan's split pushers: the game's AI takes me to my side lane.
    pub i_split: bool,
    /// The living allies who push with the waves: all but the plan's split pushers (empty: all of `allies`).
    pub group: Vec<Pos>,
}

/// A macro order this champion follows until the next look.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Intent {
    Finish { nexus: usize, at: Pos },
    /// The baron wave to stand with, and the enemy nexus (where forward is).
    Join { at: Pos, toward: Pos },
}

/// The order for this champion now, if any.
pub fn plan(v: &View) -> Option<Intent> {
    let near = |at: Pos, list: &mut dyn Iterator<Item = Pos>| list.filter(|p| dist(*p, at) <= BASE_NEAR).count();
    if let Some((nexus, at, true)) = v.enemy_nexus {
        let ours = near(at, &mut v.allies.iter().copied());
        let theirs = near(at, &mut v.enemies.iter().map(|e| e.1));
        if dist(v.me, at) <= FINISH_REACH && v.hp_pct >= FINISH_HP && ours >= 3 && ours > theirs {
            return Some(Intent::Finish { nexus, at });
        }
    }
    if v.baron_minions.is_empty() || v.hp_pct < JOIN_HP || v.enemies.iter().any(|e| dist(e.1, v.me) <= FIGHT) {
        return None;
    }
    // only with the numbers: not into a 4 v 5 under their towers
    if v.allies.len() < JOIN_MIN_ALIVE || v.allies.len() < v.enemies.len() {
        return None;
    }
    // a split pusher of the team's Morgard plan: the game's AI takes it to its side lane
    if v.i_split {
        return None;
    }
    // the group (all but the split pushers) goes to one baron wave: the one nearest it - in 1-3-1 the nearest in mid
    let group = if v.group.is_empty() { &v.allies } else { &v.group };
    let n = group.len().max(1) as f64;
    let centre = (group.iter().map(|p| p.0).sum::<f64>() / n, group.iter().map(|p| p.1).sum::<f64>() / n);
    let centre = if group.is_empty() { v.me } else { centre };
    let toward = v.enemy_nexus.map(|n| n.1)?;
    let nearest = |waves: &mut dyn Iterator<Item = Pos>| waves.min_by(|a, b| dist(*a, centre).total_cmp(&dist(*b, centre)));
    let mid = match (v.plan, v.own_nexus) {
        (BaronPlan::Split131(..), Some(own)) => {
            nearest(&mut v.baron_minions.iter().copied().filter(|p| seg_dist(*p, own, toward) <= MID_NEAR))
        }
        _ => None,
    };
    let wave = mid.or_else(|| nearest(&mut v.baron_minions.iter().copied()))?;
    Some(Intent::Join { at: wave, toward })
}

/// Whether the AI's own order is a hit on one of these enemy champions (a fight it is in).
fn at_champion(base: Option<&InputV1>, enemies: &[(usize, Pos)]) -> bool {
    base.is_some_and(|b| {
        b.kind != InputKindV1::Move.code()
            && b.kind != InputKindV1::Return.code()
            && b.target.kind == InputTargetKindV1::Target.code()
            && enemies.iter().any(|e| e.0 == b.target.target_id)
    })
}

/// What `intent` makes of the AI's order (`None`: keep it). `attack_ok` tells whether the attack on the nexus would be
/// taken.
pub fn order(intent: Intent, me: Pos, base: Option<&InputV1>, enemies: &[(usize, Pos)], attack_ok: &dyn Fn(&InputV1) -> bool) -> Option<InputV1> {
    if at_champion(base, enemies) {
        return None;
    }
    match intent {
        Intent::Finish { nexus, at } => {
            // already hitting the nexus
            if base.is_some_and(|b| b.target.kind == InputTargetKindV1::Target.code() && b.target.target_id == nexus) {
                return None;
            }
            let hit = InputV1::action(InputKindV1::Attack, InputTargetV1::target(nexus));
            Some(if attack_ok(&hit) { hit } else { InputV1::move_to(at.0 as u64, at.1 as u64) })
        }
        Intent::Join { at, toward } => {
            if dist(me, at) > WITH_WAVE {
                return Some(InputV1::move_to(at.0 as u64, at.1 as u64));
            }
            // with the wave the AI farms, sieges and walks on toward the enemy base; only a recall or a walk back
            // goes back to the wave
            let back = base.is_some_and(|b| {
                b.kind == InputKindV1::Return.code()
                    || (b.kind == InputKindV1::Move.code() && dist((b.x as f64, b.y as f64), toward) > dist(at, toward) + BACK_OFF)
            });
            back.then(|| InputV1::move_to(at.0 as u64, at.1 as u64))
        }
    }
}

// ===================== 钩子 =====================

fn look(sim: &StableSim<'_>, me_id: usize, team: usize) -> Option<View> {
    let me = sim.get_entity(me_id)?;
    let (hp, max) = me.hp();
    let pos = |e: &StableEntity<'_, '_>| (e.pos().0 as f64, e.pos().1 as f64);
    let mut v = View { me: pos(&me), hp_pct: if max == 0 { 100 } else { hp * 100 / max }, ..View::default() };
    // living allied champions by entity id: the group leaves out the Morgard plan's split pushers
    let mut mates: Vec<(usize, Pos)> = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        let ours = e.team() == team;
        match e.kind() {
            Some(EntityKindV1::Champion) if e.is_alive() => {
                if ours {
                    v.allies.push(pos(&e));
                    mates.push((e.id(), pos(&e)));
                } else {
                    v.enemies.push((e.id(), pos(&e)));
                }
            }
            Some(EntityKindV1::Nexus) => {
                if ours {
                    v.own_nexus = Some(pos(&e));
                } else if e.is_alive() {
                    v.enemy_nexus = Some((e.id(), pos(&e), e.is_targetable()));
                }
            }
            Some(EntityKindV1::Minion) if ours && e.is_alive() => {
                if (0..e.buff_count()).filter_map(|k| e.buff_at(k)).any(|b| b.name() == BARON_BUFF) {
                    v.baron_minions.push(pos(&e));
                }
            }
            _ => {}
        }
    }
    // the Morgard plan matters only while a baron wave is up: read it then
    if !v.baron_minions.is_empty() {
        v.plan = sim.strategy_get_json(team, MORGARD_USE).map_or(BaronPlan::Gather, |j| baron_plan(&j));
        let splitters: Vec<usize> = (0..sim.player_count())
            .filter_map(|i| sim.player_at(i))
            .filter(|p| p.team() == team && v.plan.splits(p.lane().map(|l| l.code())))
            .filter_map(|p| p.champion().map(|c| c.id()))
            .collect();
        v.i_split = splitters.contains(&me_id);
        v.group = mates.iter().filter(|m| !splitters.contains(&m.0)).map(|m| m.1).collect();
    }
    Some(v)
}

/// One champion's macro: its last look and the order it follows.
#[derive(Clone, Default)]
pub struct Macro {
    next_look: usize,
    intent: Option<Intent>,
    enemies: Vec<(usize, Pos)>,
    last_kind: Option<bool>,
    /// The team's Morgard plan at the last look, and whether this champion is left to the game's AI as its split pusher.
    plan: BaronPlan,
    splitting: bool,
}

impl StablePlayerAi for Macro {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:macro")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let tick = ctx.tick();
        let (player, team) = (ctx.player_id(), ctx.team());
        let mut splitting = self.splitting;
        let (me, me_id, now_head) = {
            let sim = ctx.sim()?;
            let champ = sim.get_player(player)?.champion()?;
            if !champ.is_alive() {
                self.intent = None;
                return None;
            }
            let me_id = champ.id();
            if tick >= self.next_look || tick + SCAN < self.next_look {
                self.next_look = tick + SCAN;
                match look(&sim, me_id, team) {
                    Some(v) => {
                        self.intent = plan(&v);
                        self.plan = v.plan;
                        splitting = v.i_split && self.intent.is_none();
                        self.enemies = v.enemies;
                    }
                    None => self.intent = None,
                }
            }
            let at = (champ.pos().0 as f64, champ.pos().1 as f64);
            (at, me_id, champ.name().unwrap_or_default())
        };
        // a split pusher left to the game's AI: noted when it starts
        if splitting != self.splitting {
            self.splitting = splitting;
            if splitting {
                let plan = self.plan;
                note_split(|| {
                    format!(
                        "SPLIT t={} {now_head} #{me_id} T{team}: {}, a split pusher - left to the game's AI on its side lane",
                        clock(tick),
                        plan.label()
                    )
                });
            }
        }
        let Some(intent) = self.intent else {
            self.last_kind = None;
            return None;
        };
        let out = order(intent, me, base.as_ref(), &self.enemies, &|i| ctx.is_valid_input(i))?;
        let finish = matches!(intent, Intent::Finish { .. });
        TICKS.fetch_add(1, Ordering::Relaxed);
        // counted when a champion starts following an order, not every tick
        if self.last_kind != Some(finish) {
            self.last_kind = Some(finish);
            let plan = self.plan;
            note(finish, || {
                format!(
                    "{} t={} {now_head} #{me_id} T{team}: {} ({})",
                    if finish { "FINISH" } else { "JOIN" },
                    clock(tick),
                    if finish { "hits the nexus".to_string() } else { format!("goes to the baron wave, plan {}", plan.label()) },
                    match base {
                        None => "the AI gave no order".to_string(),
                        Some(b) => format!("the AI's order was kind {} at ({}, {})", b.kind, b.x, b.y),
                    }
                )
            });
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
        "=== {ID} v{VERSION} (macro: finish the nexus, push with the baron waves) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Macro::default());
    host.log(LogLevel::Info, "league_macro loaded (macro: finish the nexus, push with the baron waves).");
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

    fn view() -> View {
        View {
            me: (800_000.0, 150_000.0),
            hp_pct: 80,
            allies: vec![(800_000.0, 150_000.0), (810_000.0, 140_000.0), (790_000.0, 160_000.0), (500_000.0, 500_000.0)],
            enemies: vec![(77, (860_000.0, 100_000.0))],
            enemy_nexus: Some((9, (860_000.0, 100_000.0), true)),
            own_nexus: Some((100_000.0, 860_000.0)),
            baron_minions: vec![],
            ..View::default()
        }
    }

    #[test]
    fn three_at_the_nexus_finish_it() {
        let v = view();
        assert_eq!(plan(&v), Some(Intent::Finish { nexus: 9, at: (860_000.0, 100_000.0) }));
        // the nexus still behind its towers, too few of us, outnumbered, or hurt: no
        assert_eq!(plan(&View { enemy_nexus: Some((9, (860_000.0, 100_000.0), false)), ..v.clone() }), None);
        assert_eq!(plan(&View { allies: v.allies[..2].to_vec(), ..v.clone() }), None);
        let crowd: Vec<(usize, Pos)> = (0..3).map(|i| (70 + i, (860_000.0, 100_000.0))).collect();
        assert_eq!(plan(&View { enemies: crowd, ..v.clone() }), None);
        assert_eq!(plan(&View { hp_pct: 10, ..v.clone() }), None);
        assert_eq!(plan(&View { me: (500_000.0, 500_000.0), ..v }), None, "too far from it");
    }

    #[test]
    fn finishing_keeps_fights_and_hits_the_nexus_otherwise() {
        let intent = Intent::Finish { nexus: 9, at: (860_000.0, 100_000.0) };
        let enemies = [(77usize, (850_000.0, 110_000.0))];
        let me = (800_000.0, 150_000.0);
        let yes = |_: &InputV1| true;
        let walk_off = InputV1::move_to(500_000, 500_000);
        let hit = order(intent, me, Some(&walk_off), &enemies, &yes).unwrap();
        assert_eq!((hit.kind, hit.target.target_id), (InputKindV1::Attack.code(), 9));
        let fight = InputV1::action(InputKindV1::Skill, InputTargetV1::target(77));
        assert_eq!(order(intent, me, Some(&fight), &enemies, &yes), None, "a skill on a defender stays");
        assert_eq!(order(intent, me, Some(&hit), &enemies, &yes), None, "already on the nexus");
        let walk = order(intent, me, Some(&InputV1::return_home()), &enemies, &|_| false).unwrap();
        assert_eq!((walk.kind, walk.x, walk.y), (InputKindV1::Move.code(), 860_000, 100_000), "the attack refused: walk there");
    }

    #[test]
    fn the_baron_plan_from_the_strategy() {
        assert_eq!(baron_plan("\"Gather\""), BaronPlan::Gather);
        assert_eq!(baron_plan(r#"{"Split14":{"position":"Top"}}"#), BaronPlan::Split14(0));
        assert_eq!(baron_plan(r#"{"Split131": {"position1": "Top", "position2": "Bottom"}}"#), BaronPlan::Split131(0, 3));
        assert_eq!(baron_plan(r#"{"Split131":{"position1":"Top"}}"#), BaronPlan::Gather, "a lane missing");
        assert_eq!(baron_plan(r#"{"Split14":{"position":"Somewhere"}}"#), BaronPlan::Gather, "not a lane");
        assert_eq!(baron_plan("null"), BaronPlan::Gather);
        let p = BaronPlan::Split131(0, 3);
        assert!(p.splits(Some(0)) && p.splits(Some(3)) && !p.splits(Some(2)) && !p.splits(None));
        assert!(BaronPlan::Split14(1).splits(Some(1)) && !BaronPlan::Split14(1).splits(Some(4)));
        assert!(!BaronPlan::Gather.splits(Some(0)));
        assert_eq!((p.label(), BaronPlan::Split14(4).label()), ("Split131 Top+Bottom".to_string(), "Split14 Support".to_string()));
    }

    #[test]
    fn split_pushers_are_the_game_ais_and_the_rest_groups() {
        // blue's base bottom left, red's top right: mid is the line between them; baron waves top, mid, bottom
        let (top, mid, bot) = ((150_000.0, 150_000.0), (480_000.0, 480_000.0), (820_000.0, 820_000.0));
        let four = vec![(750_000.0, 780_000.0), (760_000.0, 770_000.0), (740_000.0, 790_000.0), (750_000.0, 780_000.0)];
        let splitter = (150_000.0, 200_000.0);
        let v = View {
            me: four[0],
            hp_pct: 90,
            allies: [four.clone(), vec![splitter]].concat(),
            enemies: vec![(77, (900_000.0, 60_000.0))],
            enemy_nexus: Some((9, (860_000.0, 100_000.0), false)),
            own_nexus: Some((100_000.0, 860_000.0)),
            baron_minions: vec![top, mid, bot],
            ..View::default()
        };
        let at = |v: &View| match plan(v) {
            Some(Intent::Join { at, .. }) => Some(at),
            _ => None,
        };
        // all together: the wave nearest the whole team (the top laner far away pulls the centre to mid)
        assert_eq!(at(&v), Some(mid));
        // 1-4 with the top laner on its own: the four take the wave nearest them, the top laner is the game's AI's
        let one_four = View { plan: BaronPlan::Split14(0), group: four.clone(), ..v.clone() };
        assert_eq!(at(&one_four), Some(bot));
        assert_eq!(plan(&View { i_split: true, me: splitter, ..one_four.clone() }), None);
        // 1-3-1: the three take mid though the bottom wave is nearer; with no wave in mid, the nearest
        let one_three_one = View { plan: BaronPlan::Split131(0, 3), group: four[..3].to_vec(), ..v.clone() };
        assert_eq!(at(&one_three_one), Some(mid));
        assert_eq!(at(&View { baron_minions: vec![top, bot], ..one_three_one }), Some(bot));
    }

    #[test]
    fn the_baron_waves_gather_the_team() {
        let v = View {
            me: (300_000.0, 700_000.0),
            hp_pct: 90,
            allies: vec![(300_000.0, 700_000.0), (480_000.0, 480_000.0), (500_000.0, 470_000.0)],
            enemies: vec![(77, (900_000.0, 50_000.0))],
            enemy_nexus: Some((9, (860_000.0, 100_000.0), false)),
            own_nexus: Some((100_000.0, 860_000.0)),
            baron_minions: vec![(520_000.0, 440_000.0), (150_000.0, 200_000.0)],
            ..View::default()
        };
        let Some(Intent::Join { at, toward }) = plan(&v) else { panic!("{:?}", plan(&v)) };
        assert_eq!((at, toward), ((520_000.0, 440_000.0), (860_000.0, 100_000.0)), "the wave nearest the team");
        // in a fight, hurt, no baron wave, or no enemy nexus to push to: no
        assert_eq!(plan(&View { enemies: vec![(77, (310_000.0, 690_000.0))], ..v.clone() }), None);
        assert_eq!(plan(&View { enemy_nexus: None, ..v.clone() }), None);
        // down in numbers (3 of ours alive, 4 of theirs), or too few of us: no
        let far = |i: usize| (70 + i, (900_000.0, 50_000.0 + i as f64));
        assert_eq!(plan(&View { enemies: (0..4).map(far).collect(), ..v.clone() }), None);
        assert!(plan(&View { enemies: (0..3).map(far).collect(), ..v.clone() }).is_some(), "3 v 3");
        assert_eq!(plan(&View { allies: v.allies[..2].to_vec(), enemies: vec![], ..v.clone() }), None);
        assert_eq!(plan(&View { hp_pct: 30, ..v.clone() }), None);
        assert_eq!(plan(&View { baron_minions: vec![], ..v.clone() }), None);
        // far from it: walk there; with it: the AI's own (farming, sieging, walking on); a walk back or a recall: back
        let intent = Intent::Join { at, toward };
        let farm = InputV1::action(InputKindV1::Attack, InputTargetV1::target(500));
        assert!(order(intent, v.me, Some(&farm), &[], &|_| true).is_some(), "far from the wave");
        assert_eq!(order(intent, at, Some(&farm), &[], &|_| true), None, "with the wave, farming");
        assert_eq!(order(intent, at, Some(&InputV1::move_to(700_000, 260_000)), &[], &|_| true), None, "on toward their base");
        assert!(order(intent, at, Some(&InputV1::move_to(200_000, 750_000)), &[], &|_| true).is_some(), "back home");
        assert!(order(intent, at, Some(&InputV1::return_home()), &[], &|_| true).is_some());
        assert_eq!(order(intent, at, None, &[], &|_| true), None);
    }
}
