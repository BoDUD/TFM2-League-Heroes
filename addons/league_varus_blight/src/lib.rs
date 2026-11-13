//! 韦鲁斯附加包：「枯萎」照英雄联盟记在每个敌人自己身上（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话
//! 全部补附加包」）。
//!
//! 主包是纯数据，读不到目标身上的层数：枯萎层数记在韦鲁斯自己身上（同卡莎的被动），打 A 叠的层会在 B 身上引爆。本包：副本里
//! 普攻的叠层梯子、Q / E / R 的引爆梯子都换成原生效果（数据在命中时调用，`input` 就是被打中的人）：
//!
//! - **`league_varus_blight:stack`**：给他叠一层（`BUFFS`，6 秒，最多 3 层，层数就是他身上挂着的那个 buff），播主包的层数画面。
//! - **`league_varus_blight:pop`**（Q、E）/ **`:pop_r`**（R）：按他身上的层数引爆，每层 `PER_STACK`% 最大生命的真实伤害（同
//!   主包），播主包的引爆画面和声音；Q、E 的引爆每层把 Q、E 的剩余冷却减 `REFUND`%（英雄联盟 13%；主包用的冷却倍率也会压
//!   到 R，这里不压）。
//! - **`league_varus_blight:fill`**（R 引爆之后）：给他叠满 3 层（主包 R 的「再叠满」）。
//! - **R 的腐化反复传染**（0.1.2，2026-11-14，用户看了「和英雄联盟不一样的地方」清单后说「全改吧」）：英雄联盟的腐败锁链
//!   "can spread repeatedly until there are no new targets"，被感染的人受到一样的效果；主包只在第一个人的位置扩散一次。副本里
//!   那一次扩散打到的每个英雄改成调用 **`:spread`**：没被感染过的（身上没有 `INF`）照主包禁锢 `ROOT2` tick、播同样的画面和
//!   声音，再叠满 3 层枯萎（主包的扩散只画了三个点，层数在韦鲁斯身上）、记上 `INF`，并排一个 `SPREAD_T` tick 后的
//!   **`:chain`**：从他站的地方再向 `SPREAD_R` 内没被感染过的敌方英雄扩散一次，一直传到没有新的人。第一个被锁住的人由
//!   `:fill` 记上 `INF`，不会被自己的扩散再禁锢一次。扩散还是不带伤害、每一跳 0.5 秒（主包的节奏；英雄联盟每一跳 2 秒、
//!   带同样的伤害）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_varus_blight.log`：整个游戏一个计数，服务器的预模拟先记
//! `LOG_FIRST` 行、之后每 `LOG_EVERY` 行记一行，你看的那场每条都记。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_varus_blight";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_varus_blight") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 目标身上的层数：挂着哪个就是几层。
pub const BUFFS: [&str; 3] = ["league_varus_blight_1", "league_varus_blight_2", "league_varus_blight_3"];
/// 主包的层数画面、引爆画面和声音。
pub const VIEWS: [&str; 3] = ["league_varus_b_v1", "league_varus_b_v2", "league_varus_b_v3"];
pub const POPS: [&str; 3] = ["league_varus_b_pop1", "league_varus_b_pop2", "league_varus_b_pop3"];
pub const POP_SFX: &str = "league_varus_b_pop";
pub const LIFE: usize = 360;
pub const PER_STACK: usize = 3;
pub const REFUND: usize = 13;
/// R 的传染：感染过的记号（一次大招里每人只感染一次）和它的时长；主包扩散的数字（`make_override.py` 核对它们和主包一致）：
/// 每一跳隔多久、多远、禁锢多久；读不到身体半径时用的（数据的区域把被测单位的身体也算进半径）。
pub const INF: &str = "league_varus_blight_inf";
pub const INF_T: usize = 360;
pub const SPREAD_T: usize = 30;
pub const SPREAD_R: usize = 55000;
pub const ROOT2: usize = 90;
pub const BODY: f64 = 10_000.0;
/// 主包的名字：禁锢的画面（buff）、被扩散到的画面、扩散的画面和声音。
pub const R_BIND: &str = "league_varus_r_bind";
pub const SPREAD_HIT: &str = "league_varus_r_spread_hit";
pub const SPREAD_FX: &str = "league_varus_r_spread";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNT: Mutex<usize> = Mutex::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VARUS_BLIGHT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_varus_blight.log");
        }
    }
    PathBuf::from("league_varus_blight.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
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

/// One count for every line of the launch: the first `LOG_FIRST`, then every `LOG_EVERY`-th, and every one when `shown`
/// (the match on screen; 0.1.1: the presims used the count up first, so the 11-01 evening's watched sets kept 4 lines).
const LOG_FIRST: usize = 150;
const LOG_EVERY: usize = 25;

fn counted(shown: bool) -> Option<usize> {
    let mut n = COUNT.lock().unwrap_or_else(|e| e.into_inner());
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

fn head(sim: &StableSim<'_>, me: usize) -> String {
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
    format!("[{kind} m={} s={}] t={} #{me}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 层数 =====================

/// Stacks after one more (at most 3).
pub fn after_stack(n: usize) -> usize {
    (n + 1).min(BUFFS.len())
}

/// A pop of `n` stacks on `max` health: the true damage, and the share of Q's and E's remaining cooldowns cut.
pub fn pop(n: usize, max: usize) -> (usize, usize) {
    (max * PER_STACK * n / 100, REFUND * n)
}

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

fn stacks(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .filter_map(|b| BUFFS.iter().position(|n| b.name() == *n)).map(|k| k + 1).max().unwrap_or(0)
    })
}

fn set_stacks(sim: &mut StableSim<'_>, id: usize, n: usize) {
    for b in BUFFS {
        sim.entity_remove_buff(id, b);
    }
    if n > 0 {
        sim.add_buff(id, &BuffV1::timed(BUFFS[n - 1], LIFE));
    }
}

fn champion(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_champion() && e.is_alive())
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

// ===================== R 的传染 =====================

/// 一个可能被传染的英雄：编号、位置、身体半径、感染过没有。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Near {
    pub id: usize,
    pub at: (f64, f64),
    pub body: f64,
    pub infected: bool,
}

/// 从 `from` 扩散得到的新目标：`r` 内（算上身体）、没被感染过的。
pub fn new_victims(from: (f64, f64), near: &[Near], r: f64) -> Vec<usize> {
    near.iter()
        .filter(|n| !n.infected && (n.at.0 - from.0).hypot(n.at.1 - from.1) <= r + n.body)
        .map(|n| n.id)
        .collect()
}

fn mark_infected(sim: &mut StableSim<'_>, id: usize) {
    sim.entity_remove_buff(id, INF);
    sim.add_buff(id, &BuffV1::timed(INF, INF_T));
}

/// 感染一个还没感染过的英雄：照主包的扩散禁锢他，叠满枯萎，记上记号，过 `SPREAD_T` tick 从他身上再传。
fn infect(sim: &mut StableSim<'_>, caster: usize, id: usize) -> bool {
    if !champion(sim, id) || has(sim, id, INF) {
        return false;
    }
    let at = InputTargetV1::target(id);
    sim.apply_cc(id, &CcV1::of_kind(CcKindV1::Bind, ROOT2 as u64));
    sim.add_buff(id, &BuffV1::timed(R_BIND, ROOT2));
    sim.play_view_effect(SPREAD_HIT, caster, &at, 0, 0, 0);
    set_stacks(sim, id, BUFFS.len());
    sim.play_view_effect(VIEWS[BUFFS.len() - 1], caster, &at, 0, 0, 0);
    sim.play_sfx(SPREAD_FX, caster, &at);
    mark_infected(sim, id);
    let name = format!("{ID}:chain");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &at, SPREAD_T) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
    true
}

/// `:chain`：从感染了的 `from` 身上再扩散一次，返回新感染了几个。
fn chain(sim: &mut StableSim<'_>, caster: usize, from: usize) -> usize {
    let Some(src) = sim.get_entity(from).filter(|e| e.is_alive()) else { return 0 };
    let (team, (x, y)) = (src.team(), src.pos());
    let near: Vec<Near> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.id() != from && e.team() == team && e.is_champion() && e.is_alive() && e.is_targetable())
        .map(|e| {
            let (ex, ey) = e.pos();
            let body = e.radius();
            Near {
                id: e.id(),
                at: (ex as f64, ey as f64),
                body: if body > 0 { body as f64 } else { BODY },
                infected: (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == INF),
            }
        })
        .collect();
    let victims = new_victims((x as f64, y as f64), &near, SPREAD_R as f64);
    if victims.is_empty() {
        return 0;
    }
    sim.play_view_effect(SPREAD_FX, caster, &InputTargetV1::pos(x, y), 0, 0, 0);
    victims.into_iter().filter(|&id| infect(sim, caster, id)).count()
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Step {
    Stack,
    Pop,
    PopR,
    Fill,
    /// R's corruption reaching a champion in the main pack's one spread (the data calls it on each of them).
    Spread,
    /// The corruption going on from an infected champion (queued by `infect`).
    Chain,
}

struct Blight(Step);

impl StableEffectType for Blight {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(id) = target_of(&input).filter(|&id| champion(sim, id)) else { return };
        let had = stacks(sim, id);
        match self.0 {
            Step::Spread | Step::Chain => {
                let n = if self.0 == Step::Spread { usize::from(infect(sim, caster, id)) } else { chain(sim, caster, id) };
                if n > 0 {
                    if let Some(k) = counted(on_screen(sim)) {
                        wlog(format!("{} {} #{k}: {n} champion(s) infected{}", head(sim, caster),
                                     if self.0 == Step::Spread { "SPREAD" } else { "CHAIN" },
                                     if self.0 == Step::Spread { format!(" (#{id})") } else { format!(" from #{id}") }));
                    }
                }
                return;
            }
            Step::Stack | Step::Fill => {
                let n = if self.0 == Step::Fill { BUFFS.len() } else { after_stack(had) };
                set_stacks(sim, id, n);
                sim.play_view_effect(VIEWS[n - 1], caster, &InputTargetV1::target(id), 0, 0, 0);
                if self.0 == Step::Fill {
                    // R's first target: infected already, its own spread must not root it again
                    mark_infected(sim, id);
                }
            }
            Step::Pop | Step::PopR => {
                if had == 0 {
                    return;
                }
                let max = sim.get_entity(id).map_or(0, |e| e.hp().1);
                let (damage, cut) = pop(had, max);
                set_stacks(sim, id, 0);
                sim.deal_damage_typed(caster, id, damage, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                sim.play_view_effect(POPS[had - 1], caster, &InputTargetV1::target(id), 0, 0, 0);
                sim.play_sfx(POP_SFX, caster, &InputTargetV1::target(id));
                if self.0 == Step::Pop {
                    for slot in [SkillSlotV1::Skill, SkillSlotV1::Skill2] {
                        let left = sim.get_entity(caster).and_then(|e| e.cooldown(slot)).map_or(0, |c| c.remaining);
                        if left > 0 {
                            sim.entity_reduce_cooldown(caster, slot, left * cut / 100);
                        }
                    }
                }
                if let Some(k) = counted(on_screen(sim)) {
                    wlog(format!("{} POP{} #{k} on #{id}: {had} stacks, {damage} true damage{}", head(sim, caster),
                                 if self.0 == Step::PopR { " (R)" } else { "" },
                                 if self.0 == Step::Pop { format!(", Q/E cooldowns -{cut}%") } else { String::new() }));
                }
                return;
            }
        }
        if let Some(k) = counted(on_screen(sim)) {
            wlog(format!("{} {:?} #{k} on #{id}: {had} -> {} stacks", head(sim, caster), self.0, stacks(sim, id)));
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Varus's Blight on each enemy apart; R's corruption spreads on and on) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    for (name, step) in [("stack", Step::Stack), ("pop", Step::Pop), ("pop_r", Step::PopR), ("fill", Step::Fill),
                         ("spread", Step::Spread), ("chain", Step::Chain)] {
        module.add_native_effect(format!("{ID}:{name}"), Blight(step));
    }
    host.log(LogLevel::Info, "league_varus_blight v1 loaded (Blight stacks on each enemy apart).");
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

    #[test]
    fn stacks_cap_at_three_and_pop_on_max_health() {
        assert_eq!(after_stack(0), 1);
        assert_eq!(after_stack(3), 3);
        assert_eq!(pop(3, 2000), (180, 39));
        assert_eq!(pop(1, 1000), (30, 13));
    }

    #[test]
    fn the_corruption_goes_on_to_the_ones_not_yet_infected() {
        // League: "The infection can spread repeatedly until there are no new targets."
        let n = |id, x: f64, infected| Near { id, at: (x, 0.0), body: BODY, infected };
        let r = SPREAD_R as f64;
        // from 0: #2 near, #3 near but infected already, #4 just in reach by its body, #5 out of reach
        let near = [n(2, 30_000.0, false), n(3, 20_000.0, true), n(4, 65_000.0, false), n(5, 65_001.0, false)];
        assert_eq!(new_victims((0.0, 0.0), &near, r), vec![2, 4]);
        // the next hop, from #4: #5 is in reach now; nobody twice
        let near = [n(2, 30_000.0, true), n(3, 20_000.0, true), n(5, 65_001.0, false)];
        assert_eq!(new_victims((65_000.0, 0.0), &near, r), vec![5]);
        let near = [n(2, 30_000.0, true), n(3, 20_000.0, true), n(4, 65_000.0, true)];
        assert_eq!(new_victims((65_001.0, 0.0), &near, r), Vec::<usize>::new());
        assert!(INF.len() <= BUFF_NAME_CAP);
        // the marks outlast any chain of five champions
        assert!(INF_T > 5 * SPREAD_T + ROOT2);
    }

    #[test]
    fn the_spread_is_the_main_packs() {
        // the copy's one spread zone calls :spread on each champion; its numbers are this file's
        let text = include_str!("../override/league_varus.data_champion");
        let at = text.find("\"name\": \"league_varus_r_spread\",").expect("the spread zone in the override");
        let zone = &text[at..at + 700];
        assert!(zone.contains(&format!("\"radius\": {SPREAD_R}")), "{zone}");
        assert!(zone.contains("\"effect_ref\": \"league_varus_blight:spread\""), "{zone}");
        assert!(!zone.contains("\"Bind\""), "the data's own root is gone from the spread: {zone}");
        let before = &text[at.saturating_sub(700)..at];
        assert!(before.contains(&format!("\"tick\": {SPREAD_T}")), "the spread comes {SPREAD_T} ticks after the hit: {before}");
    }
}
