//! 「备好式」大招替 AI 按（用户 2026-10-17：「莎弥拉和卡牌用附加包在合适时机替AI按R，主包保持现在这样」）。
//!
//! 莎弥拉、崔斯特的 R 格只是 3 tick 的「备好」动作，真大招由主包数据在备好期间自己判断时机放出，用不上就退还冷却。
//! 游戏 0.6.4 的 AI 几乎不按这种格子（只读观察包：莎弥拉每 10 分钟 0.2 次、崔斯特 0.7 次，多数英雄 3–9 次），格子里加
//! 200、1000 的护盾或一次搜敌方英雄都没用。本包不换主包的英雄（没有 `override/`），只加一个 AI 钩子
//! `league_ult_press:ult`，在合适的时候替 AI 按下 R，备好、判断、放出、退还全是主包的数据：
//!
//! - 莎弥拉（`league_samira`，R `Targeting EnemyChampion`，射程 `SAMIRA_RANGE`）：R 好了、她没被控住、射程内有敌方英雄
//!   ——按 R，目标是最近的那个。S 评价时这一下就放出「炼狱扳机」，不到 S 就备好 330 tick，期间到了 S 再放。
//! - 崔斯特（`league_twistedfate`，R `None`）：主包的「命运」备好 600 tick，期间每 10 tick 看一次：他身边 70000 内没有
//!   敌方英雄、360000 内有被我方打过的敌方英雄、那人 60000 内有我方英雄——就揭示敌方英雄、引导后传送过去。本包在
//!   同样的局面才按：他身边 `TF_ALONE` 内没有敌方英雄、生命不低于 `TF_MIN_HP`，而且有个离他 `TF_MIN_FAR` 以外、
//!   `TF_REACH` 以内的我方英雄，`TF_FIGHT` 内贴着敌方英雄（在打架）。
//! - 被控住（眩晕、击飞、沉默等）、R 在冷却或还没解锁时不按。冷却由钩子自己看（引擎的「输入合法」不看冷却，
//!   league_pyke 的教训）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ult_press.log`，每次启动游戏重写，上一次的留在 .prev.log。
//! ORDER = 按了；CAST = 冷却真的开始走（按下去了）；FIRED = 莎弥拉的真大招放出（主包的 `league_samira_r_on`）；
//! TELEPORT = 崔斯特备好之后一 tick 内移动了 `TF_JUMP` 以上。

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
/// 主包莎弥拉 R 的射程（ult range）。
pub const SAMIRA_RANGE: f64 = 50_000.0;
/// 主包莎弥拉真大招放出时挂的 buff（吸血 40，120 tick）。
pub const SAMIRA_R_ON: &str = "league_samira_r_on";
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
/// 按下后这么多 tick 内冷却开始走，就算按下去了；备好后这么多 tick 内看有没有放出真大招 / 传送。
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
    format!("[{kind} m={} s={}] t={} {name}#{id}", m(o.match_id), m(o.set_index), sim.tick())
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 什么时候按（单元测试用） =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 莎弥拉：射程内最近的敌方英雄（`(id, 位置)`）。
pub fn samira_target(me: (f64, f64), enemies: &[(usize, (f64, f64))]) -> Option<usize> {
    enemies
        .iter()
        .map(|&(id, at)| (id, dist(me, at)))
        .filter(|&(_, d)| d <= SAMIRA_RANGE)
        .min_by(|a, b| a.1.total_cmp(&b.1))
        .map(|(id, _)| id)
}

/// 崔斯特：他一个人（`TF_ALONE` 内没有敌方英雄）、生命够，远处（`TF_MIN_FAR`..`TF_REACH`）有我方英雄 `TF_FIGHT` 内贴着
/// 敌方英雄 -> `(那个敌方英雄, 那个我方英雄)`，挑离他最近的一组。
pub fn tf_fight(
    me: (f64, f64),
    hp: f64,
    allies: &[(usize, (f64, f64))],
    enemies: &[(usize, (f64, f64))],
) -> Option<(usize, usize)> {
    if hp < TF_MIN_HP || enemies.iter().any(|&(_, at)| dist(me, at) <= TF_ALONE) {
        return None;
    }
    let mut best: Option<(usize, usize, f64)> = None;
    for &(a, a_at) in allies {
        let far = dist(me, a_at);
        if far < TF_MIN_FAR {
            continue;
        }
        for &(e, e_at) in enemies {
            let reach = dist(me, e_at);
            if dist(a_at, e_at) <= TF_FIGHT && reach <= TF_REACH && best.is_none_or(|b| reach < b.2) {
                best = Some((e, a, reach));
            }
        }
    }
    best.map(|(e, a, _)| (e, a))
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

#[derive(Clone, Debug)]
struct Order {
    tick: usize,
    why: String,
}

#[derive(Clone, Default)]
struct UltPress {
    /// 最近一次按（`ORDER_FRESH` tick 内冷却开始走就算是它）。
    order: Option<Order>,
    /// 上一次看到的 R 剩余冷却。
    last_cd: Option<usize>,
    /// 按下去的那一 tick（之后 `WATCH_AFTER` tick 内看结果）。
    cast_at: Option<usize>,
    last_pos: Option<(f64, f64)>,
    r_on: bool,
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
        init.champion_name == SAMIRA || init.champion_name == TF
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, _base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let order = {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            let me = pl.champion()?;
            let (mid, team) = (me.id(), me.team());
            let name = me.name().unwrap_or_default();
            let my_at = at(&me);
            // R went out when its cooldown starts: the order behind it, or the AI's own press
            let cd = me.cooldown(SkillSlotV1::Ult);
            let remaining = cd.map(|c| c.remaining);
            if let (Some(0), Some(c)) = (self.last_cd, remaining) {
                if c > 0 {
                    let why = match self.order.take().filter(|o| tick <= o.tick + ORDER_FRESH) {
                        Some(o) => format!("pressed {} ticks before: {}", tick - o.tick, o.why),
                        None => "by the AI itself".to_string(),
                    };
                    if let Some(k) = counted(format!("{name} cast")) {
                        wlog(format!("{} R CAST {why} #{k}", head(&sim, mid)));
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
                    let on = has_buff(&me, SAMIRA_R_ON);
                    if on && !self.r_on {
                        if let Some(k) = counted(format!("{name} fired")) {
                            wlog(format!("{} R FIRED (S grade) {} ticks after the press #{k}", head(&sim, mid), tick - t0));
                        }
                    }
                } else if let Some(p) = self.last_pos {
                    if dist(p, my_at) >= TF_JUMP {
                        if let Some(k) = counted(format!("{name} teleport")) {
                            wlog(format!("{} R TELEPORT {:.0} {} ticks after the press #{k}", head(&sim, mid), dist(p, my_at), tick - t0));
                        }
                        self.cast_at = None;
                    }
                }
            }
            self.r_on = name == SAMIRA && has_buff(&me, SAMIRA_R_ON);
            self.last_pos = Some(my_at);
            let ready = cd.is_some_and(|c| c.unlocked && c.remaining == 0);
            if !me.is_alive() || !ready || controlled(&me) {
                return None;
            }
            let mut allies = Vec::new();
            let mut enemies = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_champion() || !e.is_alive() || !e.is_targetable() || e.id() == mid {
                    continue;
                }
                if e.team() == team {
                    allies.push((e.id(), at(&e)));
                } else if sim.is_visible(team, e.id()) {
                    enemies.push((e.id(), at(&e)));
                }
            }
            if name == SAMIRA {
                samira_target(my_at, &enemies).map(|t| (t, format!("{} within {:.0}", who(&sim, t), SAMIRA_RANGE)))
            } else {
                tf_fight(my_at, hp_share(me.hp()), &allies, &enemies).map(|(e, a)| {
                    let (ea, aa) = (sim.get_entity(e).map(|x| at(&x)), sim.get_entity(a).map(|x| at(&x)));
                    let far = aa.map_or(f64::NAN, |p| dist(my_at, p));
                    let fight = match (ea, aa) {
                        (Some(x), Some(y)) => dist(x, y),
                        _ => f64::NAN,
                    };
                    (e, format!("{} fighting {} ({fight:.0} apart) {far:.0} away, nobody near him", who(&sim, a), who(&sim, e)))
                })
            }
        };
        let (target, why) = order?;
        let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(target));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if self.order.as_ref().is_none_or(|o| tick > o.tick + ORDER_FRESH) {
            if let Some(k) = counted(format!("player {player} order")) {
                wlog(format!("t={tick} player {player} R ORDER: {why} #{k}"));
            }
            self.order = Some(Order { tick, why });
        }
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
        "=== {ID} v{VERSION} (presses Samira's and Twisted Fate's armed ults for the AI) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(UltPress::default());
    host.log(LogLevel::Info, "league_ult_press loaded (presses Samira's and Twisted Fate's armed ults).");
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
    fn samira_presses_on_the_nearest_in_range() {
        let enemies = [(1, (40_000.0, 0.0)), (2, (20_000.0, 0.0)), (3, (60_000.0, 0.0))];
        assert_eq!(samira_target((0.0, 0.0), &enemies), Some(2));
        assert_eq!(samira_target((0.0, 0.0), &[(3, (60_000.0, 0.0))]), None); // out of R's range
        assert_eq!(samira_target((0.0, 0.0), &[]), None);
    }

    #[test]
    fn twisted_fate_presses_only_alone_with_a_fight_far_away() {
        let allies = [(10, (200_000.0, 0.0))];
        let fight = [(20, (230_000.0, 0.0))];
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &allies, &fight), Some((20, 10)));
        // an enemy champion next to him
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &allies, &[(20, (230_000.0, 0.0)), (21, (60_000.0, 0.0))]), None);
        // low on health
        assert_eq!(tf_fight((0.0, 0.0), 0.3, &allies, &fight), None);
        // the ally is not fighting (the enemy 80000 from him)
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &allies, &[(20, (280_000.0, 0.0))]), None);
        // the fight is out of R's reach
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &[(10, (400_000.0, 0.0))], &[(20, (420_000.0, 0.0))]), None);
        // the ally is close by: no need to teleport
        assert_eq!(tf_fight((0.0, 0.0), 0.9, &[(10, (80_000.0, 0.0))], &[(20, (110_000.0, 0.0))]), None);
    }

    #[test]
    fn twisted_fate_picks_the_nearest_fight() {
        let allies = [(10, (300_000.0, 0.0)), (11, (0.0, 150_000.0))];
        let enemies = [(20, (320_000.0, 0.0)), (21, (0.0, 170_000.0))];
        assert_eq!(tf_fight((0.0, 0.0), 1.0, &allies, &enemies), Some((21, 11)));
    }
}
