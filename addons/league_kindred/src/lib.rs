//! 千珏附加包：R「羊灵生息」只在法阵里有人快要阵亡时放（用户：「千珏r大招逻辑不要乱放」）。
//!
//! 主包是纯数据，读不到当前生命：R 由 AI 在敌方英雄 70000 内时放出、待命 900 tick，待命期间她每支箭查一次数据看得见的
//! 「危险」（被控制的友方英雄身边有敌方英雄，或交战中某个友方英雄被两名以上敌方英雄围住），常常有人还满血就交了。
//! `mod.override_info` 把主包的千珏换成 `override/` 里的副本（`make_override.py` 用 `tools/kit/build_kindred.py` 的
//! `r_now=1` 生成）：R 一放出就落法阵（不再待命，普攻、Q、E 里不再检查），什么时候放由本包的 AI 钩子
//! `league_kindred:ult` 决定：
//!
//! - 法阵在她放出 R 后第 `R_AT` tick 落在她脚下（半径 `R_RADIUS`）。她 `IN_CIRCLE` 以内的己方英雄（含她自己）里，
//!   `DANGER_NEAR` 以内有敌方英雄、身上没有别人给的「不死」，而且生命不到 `DANGER_HP`，或 `BURST_T` tick 内掉了
//!   `BURST` 以上、只剩 `BURST_LEFT` 以下——放（AI 没想放也放），施放目标是她 `R_CAST_RANGE` 以内最近的敌方英雄
//!   （主包 R 的施放目标：`EnemyChampion`）。
//! - 其余时候 AI 想放 R：改成普攻它想放的那个人（打不到就走过去），R 留着。
//! - 她被控住（眩晕、击飞、沉默等）、R 在冷却、等级不到时不放。冷却和等级由钩子自己看（引擎的「输入合法」不看冷却，
//!   league_pyke 的教训）。
//!
//! 法阵、不死、结束时的回血、画面和声音全是主包的数据；原生代码只挑时机。放出后 `CHECK_AT` tick 记一笔：危险的那个人
//! 还活着没有、身上有没有主包法阵给的不死（`league_kindred_r_safe`）。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kindred.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_kindred";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 主包的千珏。
pub const HERO: &str = "league_kindred";
/// 主包法阵每 6 tick 给法阵里的己方英雄挂的不死（8 tick）。
pub const SAFE: &str = "league_kindred_r_safe";
/// R 从这一级起能放（同 league_darius_ult、league_pyke）。
pub const ULT_LEVEL: usize = 5;
/// 主包 R 的射程（r_arm_range）：这么近有敌方英雄才放得出。
pub const R_CAST_RANGE: f64 = 70_000.0;
/// 主包法阵的半径（r_r）、落下的 tick（r_at）。
pub const R_RADIUS: f64 = 50_000.0;
pub const R_AT: usize = 20;
/// 她这么近的己方英雄算在法阵里（比半径小一圈：落下前那 `R_AT` tick 里人还会走）。
pub const IN_CIRCLE: f64 = 42_000.0;
/// 危险：这么近有敌方英雄，而且生命比例不到 `DANGER_HP`，或 `BURST_T` tick 内掉了 `BURST` 以上、只剩 `BURST_LEFT` 以下。
pub const DANGER_NEAR: f64 = 45_000.0;
pub const DANGER_HP: f64 = 0.30;
pub const BURST: f64 = 0.30;
pub const BURST_LEFT: f64 = 0.60;
pub const BURST_T: usize = 60;
/// 放出后隔多少 tick 看结果（法阵落下后再等几 tick）。
pub const CHECK_AT: usize = R_AT + 10;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KINDRED_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_kindred.log");
        }
    }
    PathBuf::from("league_kindred.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (memory log-open-once)
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

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条（AI 每 tick 想一次）。
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

// ===================== 给谁、什么时候（单元测试用） =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一个己方英雄：id、位置、生命比例、`BURST_T` tick 内最多掉了多少（比例）、身上有没有别人给的不死。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Ally {
    pub id: usize,
    pub at: (f64, f64),
    pub hp: f64,
    pub drop: f64,
    pub undying: bool,
}

/// 快要阵亡吗：`DANGER_NEAR` 内有敌方英雄，生命不到 `DANGER_HP`，或刚被打掉一大截；别人的不死在身上时不算。
pub fn in_danger(a: &Ally, enemies: &[(f64, f64)]) -> bool {
    !a.undying
        && enemies.iter().any(|e| dist(a.at, *e) <= DANGER_NEAR)
        && (a.hp <= DANGER_HP || (a.drop >= BURST && a.hp <= BURST_LEFT))
}

/// 她在 `me`：`IN_CIRCLE` 内快要阵亡的己方英雄（含她）里生命比例最低的那个。
pub fn pick_save(me: (f64, f64), allies: &[Ally], enemies: &[(f64, f64)]) -> Option<Ally> {
    allies
        .iter()
        .filter(|a| dist(me, a.at) <= IN_CIRCLE && in_danger(a, enemies))
        .min_by(|a, b| a.hp.total_cmp(&b.hp))
        .copied()
}

/// 生命历史 `(tick, 比例)`（旧的在前）-> 现在的比例往前 `BURST_T` tick 内掉了多少。
pub fn drop_of(history: &[(usize, f64)], now_tick: usize, now_hp: f64) -> f64 {
    history
        .iter()
        .filter(|(t, _)| t + BURST_T >= now_tick)
        .map(|p| p.1)
        .fold(now_hp, f64::max)
        - now_hp
}

fn hp_share((now, max): (usize, usize)) -> f64 {
    if max > 0 {
        now as f64 / max as f64
    } else {
        1.0
    }
}

/// 放不出技能的控制。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];

fn controlled(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| NO_CAST.iter().any(|k| k.code() == c.kind)))
}

fn undying(e: &StableEntity<'_, '_>) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.undying)
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

// ===================== AI 钩子：R 只在有人快要阵亡时放 =====================

/// 放出去的一次 R：哪一 tick、为谁、他当时的生命比例。
#[derive(Clone, Copy, Debug)]
struct Cast {
    tick: usize,
    me: usize,
    ally: usize,
    hp: f64,
}

/// 钩子下令的一次 R（她正忙时引擎几 tick 后才接，期间每 tick 再下一次）：哪一 tick、为谁、他当时的生命比例和
/// 1 秒内掉的、R 的施放目标离他多远。冷却真的开始走时才算放出去（`R CAST`）。
#[derive(Clone, Debug)]
struct Order {
    tick: usize,
    ally: usize,
    hp: f64,
    drop: f64,
    target: usize,
    far: f64,
    saved: String,
}

#[derive(Clone, Default)]
struct UltAi {
    /// 每个己方英雄最近 `BURST_T` tick 的生命比例。
    seen: HashMap<usize, Vec<(usize, f64)>>,
    /// 放出去的 R，各等 `CHECK_AT` tick 后看结果。
    pending: Vec<Cast>,
    /// 最近一次下令（`ORDER_FRESH` tick 内冷却开始走就算是它）。
    order: Option<Order>,
    /// 上一次看到的 R 冷却。
    last_cd: Option<usize>,
    told_no_sim: bool,
}

/// 下令后这么多 tick 内 R 的冷却开始走，就算这道命令放出去的。
const ORDER_FRESH: usize = 30;
/// 她的普攻射程（主包 atk_range）：AI 想放 R 又没人危险时，这么近的敌方英雄改成普攻它。
pub const ATTACK_RANGE: f64 = 55_000.0;

impl StablePlayerAi for UltAi {
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
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        // the AI's own R: a None cast, so its input carries no target (the kit's ult) - the hold picks one itself
        let wants_ult = base.is_some_and(|b| b.kind == InputKindV1::Ult.code());
        enum Do {
            Keep,
            Cast(Order),
            /// the enemy champion to attack (in her reach), else the place to walk toward
            Hold(Option<usize>, Option<(u64, u64)>, String),
        }
        let todo = {
            let Some(sim) = ctx.sim() else {
                if !self.told_no_sim {
                    self.told_no_sim = true;
                    wlog(format!("t={tick} player {player}: no simulation to read, R left to the AI"));
                }
                return None;
            };
            let pl = sim.get_player(player)?;
            let me = pl.champion()?;
            let (mid, team) = (me.id(), me.team());
            let line = head(&sim, mid);
            // R went out when its cooldown starts: the order behind it (or the AI's own, which the hold should stop)
            let cd = pl.cooldowns().map(|c| c.3);
            if let (Some(0), Some(c)) = (self.last_cd, cd) {
                if c > 0 {
                    match self.order.take().filter(|o| tick <= o.tick + ORDER_FRESH) {
                        Some(o) => {
                            if let Some(k) = counted("r_cast") {
                                wlog(format!(
                                    "{line} R CAST for {} (hp {:.0}%, lost {:.0}% in {BURST_T} ticks; R target #{}, {:.0} from him; ordered {} ticks before) #{k}",
                                    o.saved,
                                    o.hp * 100.0,
                                    o.drop * 100.0,
                                    o.target,
                                    o.far,
                                    tick - o.tick
                                ));
                            }
                            self.pending.push(Cast { tick, me: mid, ally: o.ally, hp: o.hp });
                        }
                        None => {
                            if let Some(k) = counted("r_cast_ai") {
                                wlog(format!("{line} R CAST by the AI itself (the hold did not stop it) #{k}"));
                            }
                        }
                    }
                }
            }
            self.last_cd = cd;
            // the casts waiting for their result, even when she died since
            let (due, wait): (Vec<Cast>, Vec<Cast>) = self.pending.drain(..).partition(|c| tick >= c.tick + CHECK_AT);
            self.pending = wait;
            for c in due {
                let after = match sim.get_entity(c.ally) {
                    Some(a) if a.is_alive() => format!(
                        "alive, hp {:.0}%{}",
                        hp_share(a.hp()) * 100.0,
                        if has_buff(&a, SAFE) { ", in the circle (undying)" } else { ", NOT in the circle" }
                    ),
                    _ => "dead".to_string(),
                };
                wlog(format!("{} R RESULT for {} (hp {:.0}% at the cast): {after}", head(&sim, c.me), who(&sim, c.ally), c.hp * 100.0));
            }
            // health history of her side's champions (every think, so the burst rule sees the last BURST_T ticks)
            let mut allies = Vec::new();
            let mut enemies = Vec::new();
            let mut nearest: Option<(usize, f64, (u64, u64))> = None;
            let my_at = (me.pos().0 as f64, me.pos().1 as f64);
            let mut seen = HashMap::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_champion() || !e.is_alive() {
                    continue;
                }
                let at = (e.pos().0 as f64, e.pos().1 as f64);
                if e.team() != team {
                    enemies.push(at);
                    let d = dist(my_at, at);
                    if e.is_targetable() && d <= R_CAST_RANGE && nearest.is_none_or(|(_, n, _)| d < n) {
                        nearest = Some((e.id(), d, e.pos()));
                    }
                    continue;
                }
                let hp = hp_share(e.hp());
                let mut past = self.seen.remove(&e.id()).unwrap_or_default();
                past.retain(|(t, _)| t + BURST_T >= tick);
                let drop = drop_of(&past, tick, hp);
                past.push((tick, hp));
                seen.insert(e.id(), past);
                if e.is_targetable() {
                    allies.push(Ally { id: e.id(), at, hp, drop, undying: undying(&e) });
                }
            }
            self.seen = seen;
            if !me.is_alive() {
                return None;
            }
            let ready = pl.level() >= ULT_LEVEL && cd == Some(0);
            let save = if ready && !controlled(&me) { pick_save(my_at, &allies, &enemies) } else { None };
            match (save, nearest) {
                (Some(a), Some((t, _, _))) => {
                    let enemy_at = sim.get_entity(t).map(|e| (e.pos().0 as f64, e.pos().1 as f64));
                    Do::Cast(Order {
                        tick,
                        ally: a.id,
                        hp: a.hp,
                        drop: a.drop,
                        target: t,
                        far: enemy_at.map_or(f64::NAN, |e| dist(a.at, e)),
                        saved: who(&sim, a.id),
                    })
                }
                _ if wants_ult => match nearest {
                    Some((t, d, _)) if d <= ATTACK_RANGE => Do::Hold(Some(t), None, line),
                    Some((_, _, p)) => Do::Hold(None, Some(p), line),
                    // an enemy champion in R's reach the hook cannot see (untargetable): a tick in place, R kept
                    None => Do::Hold(None, Some(me.pos()), line),
                },
                _ => Do::Keep,
            }
        };
        match todo {
            Do::Keep => None,
            Do::Cast(o) => {
                let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(o.target));
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                if let Some(k) = counted("r_order") {
                    wlog(format!("t={tick} player {player} R ORDER for {} (hp {:.0}%) #{k}", o.saved, o.hp * 100.0));
                }
                self.order = Some(o);
                Some(input)
            }
            Do::Hold(t, walk, line) => {
                if let Some(k) = counted("r_held") {
                    wlog(format!("{line} R HELD: nobody in her circle about to die, attacking instead #{k}"));
                }
                if let Some(t) = t {
                    let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                    if ctx.is_valid_input(&attack) {
                        return Some(attack);
                    }
                }
                // out of her reach (or the attack not taken): toward the nearest enemy champion, as the AI was going
                walk.map(|(x, y)| InputV1::move_to(x, y))
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
        "=== {ID} v{VERSION} (Kindred: Lamb's Respite only to save someone about to die) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(UltAi::default());
    host.log(LogLevel::Info, "league_kindred loaded (Lamb's Respite only to save someone about to die).");
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

    fn ally(id: usize, x: f64, hp: f64, drop: f64) -> Ally {
        Ally { id, at: (x, 0.0), hp, drop, undying: false }
    }

    #[test]
    fn danger_needs_an_enemy_and_low_health() {
        let near = [(30_000.0, 0.0)];
        assert!(in_danger(&ally(1, 0.0, 0.25, 0.0), &near));
        assert!(!in_danger(&ally(1, 0.0, 0.25, 0.0), &[(60_000.0, 0.0)])); // nobody close
        assert!(!in_danger(&ally(1, 0.0, 0.45, 0.0), &near)); // not low
        assert!(in_danger(&ally(1, 0.0, 0.55, 0.35), &near)); // a burst
        assert!(!in_danger(&ally(1, 0.0, 0.65, 0.35), &near)); // a burst, still above 60 %
        assert!(!in_danger(&Ally { undying: true, ..ally(1, 0.0, 0.10, 0.0) }, &near)); // someone else's save on him
    }

    #[test]
    fn the_lowest_in_her_circle_is_saved() {
        let enemies = [(10_000.0, 0.0), (80_000.0, 0.0)];
        let allies = [ally(1, 0.0, 0.28, 0.0), ally(2, 20_000.0, 0.12, 0.0), ally(3, 90_000.0, 0.05, 0.0)];
        // #3 is lower but outside her circle
        assert_eq!(pick_save((0.0, 0.0), &allies, &enemies).map(|a| a.id), Some(2));
        // nobody low: R stays
        let fine = [ally(1, 0.0, 0.9, 0.0), ally(2, 20_000.0, 0.7, 0.1)];
        assert_eq!(pick_save((0.0, 0.0), &fine, &enemies), None);
        // she herself about to die
        assert_eq!(pick_save((0.0, 0.0), &[ally(9, 0.0, 0.2, 0.0)], &enemies).map(|a| a.id), Some(9));
    }

    #[test]
    fn the_burst_looks_back_burst_t_ticks() {
        let h = [(100, 0.95), (130, 0.80), (150, 0.70)];
        assert!((drop_of(&h, 160, 0.50) - 0.45).abs() < 1e-9);
        // the 0.95 is older than BURST_T at tick 170
        assert!((drop_of(&h, 170, 0.50) - 0.30).abs() < 1e-9);
        assert_eq!(drop_of(&[], 10, 0.4), 0.0);
    }
}
