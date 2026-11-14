//! 集火（用户 2026-11-08「还有没完善的功能都帮我完善了」：比赛 AI 第 3 步里的「集火」）。
//!
//! 游戏的 AI 选普攻目标（FOCUS-SEL，docs/native_ai.md）时常常一直打离得近的前排，旁边一个残血的敌方英雄没人收：打架记录器
//! 1189 场每场 28.5 次交火、团战只死 2.3 人。英雄联盟里谁残血了谁先被收。这个钩子（`league_focus:focus`，所有选手）只改
//! 一件事：AI 在普攻一个敌方英雄时，看得见的另一个敌方英雄
//!
//! - 生命 `FINISH_HP`% 以下、比现在的目标血少；或者
//! - 生命不到 `SOFT_HP`%、比现在的目标少 `GAP_HP` 个百分点以上，
//!
//! 而且不比现在的目标远（离自己的距离不超过现在目标的距离加 `SLACK`）——就改打他（几个都合适时打血最少的）。只换不更远的
//! 人，不追、不越塔（10:00 前 league_lane 最后还会把越塔的出手拦下）；技能、大招、打小兵和建筑都不动。
//!
//! 优先级 `PRIORITY` 在 league_macro / league_peel 之后、英雄附加包之前：英雄的钩子还能在它之后改。只看比赛状态，没有随机数，
//! 每个选手自己的钩子实例：服务器预演和客户端重演走的一样。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_focus.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! 前 `DETAIL_LINES` 次换目标各一行，之后每 `COUNT_EVERY` 次一行累计。效果看 league_fight_log 的 SUM（团战每次死几个）。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_focus";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_focus") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 钩子的优先级：league_macro（-500000）、league_peel（-400000）之后，英雄附加包（最高 1_000_000）之前。
pub const PRIORITY: i32 = -300_000;
/// 残血：生命不超过多少（%）就该收。
pub const FINISH_HP: usize = 25;
/// 半血以下……
pub const SOFT_HP: usize = 50;
/// ……而且比现在的目标少这么多个百分点。
pub const GAP_HP: usize = 30;
/// 新目标最多比现在的目标远多少。
pub const SLACK: f64 = 10_000.0;
/// 地图的大小上限：比这远的坐标（被放逐、藏起来的英雄）不算。
pub const MAP_MAX: f64 = 1_200_000.0;
/// 前多少次换目标各写一行。
const DETAIL_LINES: usize = 40;
/// 之后每多少次写一行累计。
const COUNT_EVERY: usize = 5_000;
/// 一次启动最多写多少行。
const LOG_CAP: usize = 5_000;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);
static SWITCHES: AtomicUsize = AtomicUsize::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_FOCUS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_focus.log");
        }
    }
    PathBuf::from("league_focus.log")
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

// ===================== 选目标 =====================

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

/// The enemy champion to hit instead of `target` (the AI's), if one is weaker and no farther.
pub fn better(me: Pos, target: Foe, foes: &[Foe]) -> Option<Foe> {
    let reach = dist(me, target.at) + SLACK;
    foes.iter()
        .copied()
        .filter(|f| f.id != target.id && dist(me, f.at) <= reach)
        .filter(|f| (f.hp <= FINISH_HP && f.hp < target.hp) || (f.hp < SOFT_HP && f.hp + GAP_HP <= target.hp))
        .min_by(|a, b| a.hp.cmp(&b.hp).then(dist(me, a.at).total_cmp(&dist(me, b.at))))
}

/// The AI's attack on an enemy champion: that champion.
fn attacked(base: Option<&InputV1>, foes: &[Foe]) -> Option<Foe> {
    let b = base?;
    if b.kind != InputKindV1::Attack.code() || b.target.kind != InputTargetKindV1::Target.code() {
        return None;
    }
    foes.iter().copied().find(|f| f.id == b.target.target_id)
}

fn pct((hp, max): (usize, usize)) -> usize {
    if max == 0 {
        100
    } else {
        hp * 100 / max
    }
}

/// The visible living enemy champions: (my position, foes).
fn look(sim: &StableSim<'_>, me_id: usize, team: usize) -> Option<(Pos, Vec<Foe>)> {
    let me = sim.get_entity(me_id)?;
    let at = |e: &StableEntity<'_, '_>| (e.pos().0 as f64, e.pos().1 as f64);
    let mut foes = Vec::new();
    for i in 0..sim.player_count() {
        let Some(p) = sim.player_at(i) else { continue };
        if p.team() == team {
            continue;
        }
        let Some(c) = p.champion() else { continue };
        let pos = at(&c);
        if !c.is_alive() || pos.0 > MAP_MAX || pos.1 > MAP_MAX || !sim.is_visible(team, c.id()) {
            continue;
        }
        foes.push(Foe { id: c.id(), at: pos, hp: pct(c.hp()) });
    }
    Some((at(&me), foes))
}

// ===================== 钩子 =====================

#[derive(Clone, Default)]
pub struct Focus;

impl StablePlayerAi for Focus {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:focus")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        // only an attack on a champion is looked at: everything else costs nothing
        let b = base?;
        if b.kind != InputKindV1::Attack.code() || b.target.kind != InputTargetKindV1::Target.code() {
            return None;
        }
        let (player, team, tick) = (ctx.player_id(), ctx.team(), ctx.tick());
        let (me, target, pick, name) = {
            let sim = ctx.sim()?;
            let champ = sim.get_player(player)?.champion()?;
            if !champ.is_alive() {
                return None;
            }
            let (me, foes) = look(&sim, champ.id(), team)?;
            let target = attacked(Some(&b), &foes)?;
            let pick = better(me, target, &foes)?;
            (me, target, pick, champ.name().unwrap_or_default())
        };
        let out = InputV1::action(InputKindV1::Attack, InputTargetV1::target(pick.id));
        if !ctx.is_valid_input(&out) {
            return None;
        }
        let n = SWITCHES.fetch_add(1, Ordering::Relaxed) + 1;
        if n <= DETAIL_LINES {
            wlog(format!(
                "FOCUS t={} {name} T{team}: from #{} ({}%, {:.0}k) to #{} ({}%, {:.0}k)",
                clock(tick),
                target.id,
                target.hp,
                dist(me, target.at) / 1000.0,
                pick.id,
                pick.hp,
                dist(me, pick.at) / 1000.0
            ));
        } else if n % COUNT_EVERY == 0 {
            wlog(format!("COUNT attacks switched to a weaker champion so far: {n}"));
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
        "=== {ID} v{VERSION} (focus: an attack on a champion goes to a weaker one no farther away) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Focus);
    host.log(LogLevel::Info, "league_focus loaded (focus the weaker champion).");
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

    fn foe(id: usize, d: f64, hp: usize) -> Foe {
        Foe { id, at: (ME.0 + d, ME.1), hp }
    }

    #[test]
    fn a_low_champion_in_reach_is_finished_first() {
        let tank = foe(1, 30_000.0, 90);
        // at 20%, 5k farther: take it
        assert_eq!(better(ME, tank, &[tank, foe(2, 35_000.0, 20)]).map(|f| f.id), Some(2));
        // 15k farther than the tank: not worth the walk
        assert_eq!(better(ME, tank, &[tank, foe(2, 45_000.0, 20)]), None);
        // the weakest of several
        assert_eq!(better(ME, tank, &[tank, foe(2, 20_000.0, 22), foe(3, 25_000.0, 12)]).map(|f| f.id), Some(3));
    }

    #[test]
    fn a_much_weaker_one_too_but_not_a_close_call() {
        let bruiser = foe(1, 30_000.0, 80);
        // 45% against 80%: switch; 60% against 80%: no; 40% against 60%: no (20 points)
        assert_eq!(better(ME, bruiser, &[bruiser, foe(2, 30_000.0, 45)]).map(|f| f.id), Some(2));
        assert_eq!(better(ME, bruiser, &[bruiser, foe(2, 30_000.0, 60)]), None);
        let half = foe(1, 30_000.0, 60);
        assert_eq!(better(ME, half, &[half, foe(2, 30_000.0, 40)]), None);
        // the target lower already: keep it
        let low = foe(1, 30_000.0, 15);
        assert_eq!(better(ME, low, &[low, foe(2, 20_000.0, 20)]), None);
    }

    #[test]
    fn only_attacks_on_champions_are_switched() {
        let foes = [foe(1, 30_000.0, 90), foe(2, 30_000.0, 10)];
        let hit = InputV1::action(InputKindV1::Attack, InputTargetV1::target(1));
        assert_eq!(attacked(Some(&hit), &foes).map(|f| f.id), Some(1));
        // a skill on him, an attack on a minion, a walk: not ours
        assert_eq!(attacked(Some(&InputV1::action(InputKindV1::Skill, InputTargetV1::target(1))), &foes), None);
        assert_eq!(attacked(Some(&InputV1::action(InputKindV1::Attack, InputTargetV1::target(500))), &foes), None);
        assert_eq!(attacked(Some(&InputV1::move_to(1, 1)), &foes), None);
        assert_eq!(attacked(None, &foes), None);
    }
}
