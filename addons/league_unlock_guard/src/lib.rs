//! 解锁总闸（用户 2026-10-18：「加上总闸：合集里加一个排在最后的检查，锁着的技能 2 / 大招换成普攻或原地站一下并记日志」）。
//!
//! 游戏 0.6.4 的「输入合法」（`ctx.is_valid_input`）既不看冷却也不看解锁：AI 钩子在大招解锁（5 级）前按 R、技能 2 解锁
//! （3 级）前按技能 2，引擎照样放出来；游戏自带的 AI 看到正在施法的敌方英雄时，5 级以下（技能 2 是 3 级以下）读到类型为空的
//! 默认数据，`unwrap` 崩溃（`game-ai` 的 `battle.rs:447`、`act_gates.rs:111`），出在后台比赛线程里——那一局永远打不完，过日卡死
//! （10-18 三次：league_ult_press 0.4.0 的崔斯特、克格莫，league_bard 的争龙，#337 修好）。每个钩子自己先查格子
//! （addons/league_addons/README.md 的规矩，#339 把其余 18 个都看过），这里再兜一层底。
//!
//! 钩子 `league_unlock_guard:gate` 挂在所有英雄上，优先级 `PRIORITY`（`i32::MAX`）：引擎按优先级从小到大跑钩子、每个拿到前一个
//! 的决定（烈娜塔的狂暴是 1_000_000），所以它看到的是所有钩子改完的最终输入。是技能 2 / 大招、而那个格子还锁着
//! （`CooldownV1::unlocked` 为 false）时：输入点的是活着的敌方单位就改成普攻它；打不了（点的是自己人、地点、方向，或这次普攻
//! 不合法）就原地站一下（走到自己脚下）。SDK 的钩子只能「不改 / 替换」，撤不掉一个按键，所以只能换成别的输入。别的输入、已解锁
//! 的格子、读不到冷却的（ABI 10 以前的游戏）一律不改；游戏自带的 AI 从不按锁着的格子，正常对局里这道闸不会动。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_unlock_guard.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `GUARD [来历 m=比赛 s=第几局] t=<tick> <英雄>#<实体> player <玩家> lvl<等级> <Skill2|Ult> pressed while locked <目标> -> <ATTACK #目标|STAND> #<第几次>`。
//! 每个英雄、每个格子先记 `LOG_FIRST` 次，之后每 `LOG_EVERY` 次一行，一次启动最多 `LOG_CAP` 行（哪个钩子每 tick 都按也写不爆）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_unlock_guard";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_unlock_guard") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 排在所有钩子之后（单元测试核对别的附加包都没用它）。
pub const PRIORITY: i32 = i32::MAX;
/// 每个英雄、每个格子先记这么多次……
const LOG_FIRST: usize = 20;
/// ……之后每这么多次记一行。
const LOG_EVERY: usize = 1000;
/// 一次启动最多写多少行。
const LOG_CAP: usize = 5_000;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);

fn log_path() -> PathBuf {
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join(format!("{ID}.log"));
        }
    }
    PathBuf::from(format!("{ID}.log"))
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

static COUNTS: LazyLock<Mutex<HashMap<(String, SkillSlotV1), usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// 这个英雄的这个格子第几次被总闸拦下；该记日志时返回次数。
fn counted(champion: &str, slot: SkillSlotV1) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry((champion.to_string(), slot)).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>) -> String {
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
    format!("[{kind} m={} s={}] t={}", m(o.match_id), m(o.set_index), sim.tick())
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

/// 输入点的是什么（日志用）。
fn aimed(sim: &StableSim<'_>, t: &InputTargetV1) -> String {
    match InputTargetKindV1::from_code(t.kind) {
        Some(InputTargetKindV1::Target) => format!("at {}", who(sim, t.target_id)),
        Some(InputTargetKindV1::Pos) => format!("at ({}, {})", t.x, t.y),
        Some(InputTargetKindV1::Dir) => format!("toward ({}, {})", t.dir_x, t.dir_y),
        _ => "with no target".to_string(),
    }
}

// ===================== 判断（单元测试用） =====================

/// 输入按的格子：只有技能 2 和大招有等级锁（技能 1 一级就有）。
pub fn locked_slot(kind: u32) -> Option<SkillSlotV1> {
    match InputKindV1::from_code(kind)? {
        InputKindV1::Skill2 => Some(SkillSlotV1::Skill2),
        InputKindV1::Ult => Some(SkillSlotV1::Ult),
        _ => None,
    }
}

/// 总闸对一个技能 2 / 大招输入怎么办。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Gate {
    /// 不改：格子解锁了，或读不到冷却。
    Pass,
    /// 锁着：改成普攻这个目标。
    Attack(usize),
    /// 锁着、没有能普攻的目标：原地站一下。
    Stand,
}

/// `unlocked`：那个格子解锁了没有（`None` = 读不到冷却，ABI 10 以前的游戏）；`foe`：输入点的活着的敌方单位。
pub fn gate(unlocked: Option<bool>, foe: Option<usize>) -> Gate {
    match unlocked {
        Some(false) => foe.map_or(Gate::Stand, Gate::Attack),
        _ => Gate::Pass,
    }
}

fn slot_name(slot: SkillSlotV1) -> &'static str {
    match slot {
        SkillSlotV1::Attack => "Attack",
        SkillSlotV1::Skill => "Skill",
        SkillSlotV1::Skill2 => "Skill2",
        SkillSlotV1::Ult => "Ult",
    }
}

// ===================== 总闸（AI 钩子） =====================

#[derive(Clone, Default)]
struct Gatekeeper;

impl StablePlayerAi for Gatekeeper {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:gate")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        // almost every tick: no new order, a walk or an attack - nothing to read
        let b = base?;
        let slot = locked_slot(b.kind)?;
        let player = ctx.player_id();
        let (todo, stand, name, line) = {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            let me = pl.champion()?;
            let team = me.team();
            let foe = (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target))
                .then_some(b.target.target_id)
                .filter(|&t| sim.get_entity(t).is_some_and(|e| e.is_alive() && e.team() != team));
            let todo = gate(me.cooldown(slot).map(|c| c.unlocked), foe);
            if todo == Gate::Pass {
                return None;
            }
            let (x, y) = me.pos();
            let name = me.name().unwrap_or_else(|| format!("player {player}"));
            let line = format!(
                "{} {} player {player} lvl{} {} pressed while locked {}",
                head(&sim),
                who(&sim, me.id()),
                pl.level(),
                slot_name(slot),
                aimed(&sim, &b.target)
            );
            (todo, InputV1::move_to(x, y), name, line)
        };
        let (input, did) = match todo {
            Gate::Attack(t) => {
                let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                if ctx.is_valid_input(&attack) {
                    (attack, format!("ATTACK #{t}"))
                } else {
                    (stand, "STAND (the attack is not valid)".to_string())
                }
            }
            _ => (stand, "STAND".to_string()),
        };
        if let Some(n) = counted(&name, slot) {
            wlog(format!("GUARD {line} -> {did} #{n}"));
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
        "=== {ID} v{VERSION} (a skill2 / ult pressed while its slot is level-locked becomes an attack or a stand) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Gatekeeper);
    host.log(LogLevel::Info, "league_unlock_guard loaded (a skill2 / ult pressed while its slot is level-locked becomes an attack or a stand).");
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
    use std::path::Path;

    #[test]
    fn only_skill2_and_ult_have_a_level_lock() {
        assert_eq!(locked_slot(InputKindV1::Skill2.code()), Some(SkillSlotV1::Skill2));
        assert_eq!(locked_slot(InputKindV1::Ult.code()), Some(SkillSlotV1::Ult));
        for k in [InputKindV1::Move, InputKindV1::Return, InputKindV1::Attack, InputKindV1::Skill] {
            assert_eq!(locked_slot(k.code()), None, "{k:?}");
        }
        assert_eq!(locked_slot(99), None);
    }

    #[test]
    fn a_locked_press_becomes_an_attack_on_its_enemy_or_a_stand() {
        assert_eq!(gate(Some(false), Some(7)), Gate::Attack(7));
        assert_eq!(gate(Some(false), None), Gate::Stand);
    }

    #[test]
    fn an_unlocked_or_unreadable_slot_is_left_alone() {
        assert_eq!(gate(Some(true), Some(7)), Gate::Pass);
        assert_eq!(gate(Some(true), None), Gate::Pass);
        assert_eq!(gate(None, Some(7)), Gate::Pass);
        assert_eq!(gate(None, None), Gate::Pass);
    }

    #[test]
    fn the_log_keeps_the_first_presses_then_one_in_every_thousand() {
        let logged: Vec<usize> = (0..3000).filter_map(|_| counted("test_champion", SkillSlotV1::Ult)).collect();
        assert_eq!(logged.len(), LOG_FIRST + 3);
        assert_eq!(logged[LOG_FIRST..], [1000, 2000, 3000]);
        // counted apart per slot
        assert_eq!(counted("test_champion", SkillSlotV1::Skill2), Some(1));
    }

    /// Line `i` gives something the top priority: `i32::MAX` in code next to a `priority`, or a constant set to it.
    fn top_priority(lines: &[&str], i: usize) -> bool {
        let l = lines[i].trim_start();
        if l.starts_with("//") || !l.contains("i32::MAX") {
            return false;
        }
        let near = lines[i.saturating_sub(2)..=i].join(" ");
        near.contains("priority") || near.contains("PRIORITY") || l.starts_with("const ") || l.starts_with("pub const ")
    }

    fn top_priority_lines(src: &str) -> usize {
        let lines: Vec<&str> = src.lines().collect();
        (0..lines.len()).filter(|&i| top_priority(&lines, i)).count()
    }

    #[test]
    fn no_other_add_on_hook_runs_after_the_gate() {
        // the engine runs the player-AI hooks by ascending priority: the gate has to stay the only one at the top
        let own = include_str!("lib.rs").split("#[cfg(test)]").next().unwrap_or_default();
        assert_eq!(top_priority_lines(own), 1, "the check must find the gate's own PRIORITY");
        assert_eq!(top_priority_lines("    fn priority(&self) -> i32 {\n        i32::MAX\n    }"), 1);
        assert_eq!(top_priority_lines("    // runs last (i32::MAX)\n    let cap = n.min(i32::MAX);"), 0);
        let addons = Path::new(env!("CARGO_MANIFEST_DIR")).join("..");
        let mut read = 0;
        for dir in std::fs::read_dir(&addons).expect("addons folder").flatten().map(|e| e.path()) {
            let name = dir.file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_default();
            if !name.starts_with("league_") || name == ID {
                continue;
            }
            for p in std::fs::read_dir(dir.join("src")).into_iter().flatten().flatten().map(|e| e.path()) {
                if p.extension().is_some_and(|e| e == "rs") {
                    let s = std::fs::read_to_string(&p).expect("source");
                    assert_eq!(top_priority_lines(&s), 0, "{} gives a hook i32::MAX: the unlock gate must run after every hook",
                               p.display());
                    read += 1;
                }
            }
        }
        assert!(read > 50, "only {read} add-on sources read");
    }

    #[test]
    fn the_bundle_registers_the_gate() {
        let bundle = Path::new(env!("CARGO_MANIFEST_DIR")).join("../league_addons/src/lib.rs");
        let s = std::fs::read_to_string(bundle).expect("league_addons/src/lib.rs");
        assert!(s.contains("#[path = \"../../league_unlock_guard/src/lib.rs\"]"));
        assert!(s.contains("unlock_guard::register(host, &mut module);"));
    }
}
