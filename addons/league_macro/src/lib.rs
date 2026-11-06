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
/// 前多少次改指令各写一行。
const DETAIL_LINES: usize = 40;
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
            "COUNT champions that took an order so far: finish the nexus {f}, join the baron waves {j}; ticks with a changed order {}",
            TICKS.load(Ordering::Relaxed)
        ));
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
    // the baron wave nearest the team: everyone goes to the same one
    let n = v.allies.len().max(1) as f64;
    let centre = (v.allies.iter().map(|p| p.0).sum::<f64>() / n, v.allies.iter().map(|p| p.1).sum::<f64>() / n);
    let centre = if v.allies.is_empty() { v.me } else { centre };
    let wave = v.baron_minions.iter().copied().min_by(|a, b| dist(*a, centre).total_cmp(&dist(*b, centre)))?;
    let toward = v.enemy_nexus.map(|n| n.1)?;
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
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        let ours = e.team() == team;
        match e.kind() {
            Some(EntityKindV1::Champion) if e.is_alive() => {
                if ours {
                    v.allies.push(pos(&e));
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
    Some(v)
}

/// One champion's macro: its last look and the order it follows.
#[derive(Clone, Default)]
pub struct Macro {
    next_look: usize,
    intent: Option<Intent>,
    enemies: Vec<(usize, Pos)>,
    last_kind: Option<bool>,
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
                        self.enemies = v.enemies;
                    }
                    None => self.intent = None,
                }
            }
            let at = (champ.pos().0 as f64, champ.pos().1 as f64);
            (at, me_id, champ.name().unwrap_or_default())
        };
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
            note(finish, || {
                format!(
                    "{} t={} {now_head} #{me_id} T{team}: {} ({})",
                    if finish { "FINISH" } else { "JOIN" },
                    clock(tick),
                    if finish { "hits the nexus" } else { "goes to the baron wave" },
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
    fn the_baron_waves_gather_the_team() {
        let v = View {
            me: (300_000.0, 700_000.0),
            hp_pct: 90,
            allies: vec![(300_000.0, 700_000.0), (480_000.0, 480_000.0), (500_000.0, 470_000.0)],
            enemies: vec![(77, (900_000.0, 50_000.0))],
            enemy_nexus: Some((9, (860_000.0, 100_000.0), false)),
            own_nexus: Some((100_000.0, 860_000.0)),
            baron_minions: vec![(520_000.0, 440_000.0), (150_000.0, 200_000.0)],
        };
        let Some(Intent::Join { at, toward }) = plan(&v) else { panic!("{:?}", plan(&v)) };
        assert_eq!((at, toward), ((520_000.0, 440_000.0), (860_000.0, 100_000.0)), "the wave nearest the team");
        // in a fight, hurt, no baron wave, or no enemy nexus to push to: no
        assert_eq!(plan(&View { enemies: vec![(77, (310_000.0, 690_000.0))], ..v.clone() }), None);
        assert_eq!(plan(&View { enemy_nexus: None, ..v.clone() }), None);
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
