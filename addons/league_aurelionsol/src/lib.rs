//! 奥瑞利安·索尔附加包：「星海焕然」的星尘死后不掉；「星芒凝汇」黑洞中心按真实生命处决。
//!
//! 主包保持纯数据：引擎在他死亡时清掉身上全部 buff，所以星尘（`league_aurelionsol_d1`…`d15`，每层一个名字，各带法强）
//! 每条命从零叠起；数据读不到生命，黑洞中心只能每秒打英雄最大生命的 `e_exec`%（处决的替身）。
//! `mod.override_info` 把主包的奥瑞利安·索尔换成 `override/` 里的副本（tools/kit/build_aurelionsol.py --native）：黑洞中心
//! 每次打到英雄时多跑一个原生效果 `league_aurelionsol:core`，`passive` 换成本包的 `league_aurelionsol:stardust`：
//!
//! - 活着时把身上每一层 `league_aurelionsol_d<n>` 原样记下来；少了（死亡清掉的）就原样补回（卑尔维斯附加包的做法）。层数
//!   只会变多（主包从不去掉一层），所以「身上比记下的少」只会是死亡清掉的。最多 `d_max` 层。天瀑的充能（`c1`…）不记：
//!   放天瀑时主包自己会清掉它们。
//! - 黑洞中心打到一个英雄：它的生命低于最大生命的 `e_low`% + 每层星尘 `e_low_d`%（英雄联盟：星尘越多处决线越高）就直接
//!   处决（真实伤害 = 生命 + 护盾 + 1，梅尔附加包的做法）。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份；原生效果读不到参数，被动出生
//! 时按（这局的种子, 单位）记一份给它。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aurelionsol.log`，每次启动
//! 游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_aurelionsol";
/// A stardust stack's name: this and its number (build_aurelionsol.py: `d1` .. `d<d_max>`).
const STACK: &str = "league_aurelionsol_d";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AURELIONSOL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_aurelionsol.log");
        }
    }
    PathBuf::from("league_aurelionsol.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (league_olaf_rage's lesson: opening it for every line stalled the simulation thread)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
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

/// The first `n` of each kind of line are logged, then every 100th (a long game repeats the same event).
fn counted(kind: &str) -> Option<usize> {
    static COUNTS: LazyLock<Mutex<HashMap<String, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let k = c.entry(kind.to_string()).or_insert(0);
    *k += 1;
    (*k <= 40 || *k % 100 == 0).then_some(*k)
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Params {
    /// 星尘最多几层。
    pub d_max: usize,
    /// 黑洞中心的处决线：最大生命的这个百分比……
    pub e_low: usize,
    /// ……每层星尘再加这么多。
    pub e_low_d: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { d_max: 15, e_low: 5, e_low_d: 1 }
    }
}

/// `{"d_max":15,"e_low":5,"e_low_d":1}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "d_max" => p.d_max = v,
            "e_low" => p.e_low = v,
            "e_low_d" => p.e_low_d = v,
            _ => {}
        }
    }
    p
}

/// Each Aurelion Sol's numbers by (the game's seed, his unit), for the core's native effect (it gets none of its own).
static PARAMS: LazyLock<Mutex<HashMap<(u64, usize), Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim.seed(), me)).copied().unwrap_or_default()
}

// ===================== 计算 =====================

/// The stack number of a buff name (`league_aurelionsol_d3` -> 3), within d_max.
pub fn stack_of(name: &str, d_max: usize) -> Option<usize> {
    let n: usize = name.strip_prefix(STACK)?.parse().ok()?;
    (1..=d_max).contains(&n).then_some(n)
}

/// The execute line in percent of maximum health with this much stardust.
pub fn execute_line(p: &Params, stacks: usize) -> usize {
    p.e_low + p.e_low_d * stacks.min(p.d_max)
}

/// Is a champion with this health under the line (a unit with no maximum never is).
pub fn executes(p: &Params, stacks: usize, hp: usize, max: usize) -> bool {
    max > 0 && hp > 0 && hp * 100 < execute_line(p, stacks) * max
}

/// The stacks kept that are not on him now (a death cleared them).
fn missing(kept: &[BuffV1], have: &[BuffV1]) -> Vec<BuffV1> {
    kept.iter().filter(|k| !have.iter().any(|h| h.name() == k.name())).cloned().collect()
}

fn stacks_on(sim: &StableSim<'_>, me: usize, d_max: usize) -> Vec<BuffV1> {
    sim.get_entity(me).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| stack_of(b.name(), d_max).is_some()).collect()
    })
}

// ===================== 原生效果：黑洞中心 =====================

/// The core struck a champion: under the line, it dies.
fn core(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let t = input.target_id;
    let p = params_of(sim, me);
    let stacks = stacks_on(sim, me, p.d_max).len();
    let Some(u) = sim.get_entity(t) else { return };
    if !u.is_alive() || !u.is_champion() {
        return;
    }
    let (hp, max) = u.hp();
    let shield = u.shield();
    let name = u.name().unwrap_or_default();
    if !executes(&p, stacks, hp, max) {
        return;
    }
    sim.deal_damage_typed(me, t, hp + shield + 1, DamageTypeV1::Fixed, AttackTypeV1::Skill);
    if let Some(k) = counted("execute") {
        wlog(format!("{} EXECUTE #{k}: {name} #{t} at {hp}/{max} ({}%) under {}% ({stacks} stardust)", head(sim, me),
                     hp * 100 / max.max(1), execute_line(&p, stacks)));
    }
}

struct CoreFx;
impl StableEffectType for CoreFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        core(sim, caster, input);
    }
}

// ===================== 被动：星尘 =====================

/// 每个奥瑞利安·索尔一份：参数、记下的星尘、上一 tick 是不是活着（只为日志）。
#[derive(Clone, Default)]
struct Stardust {
    p: Params,
    kept: Vec<BuffV1>,
    was_alive: bool,
}

impl StablePassive for Stardust {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert((sim.seed(), me), self.p);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Aurelion Sol (player {player}, team {team}), {:?}", head(sim, me),
                         self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let alive = e.is_alive();
        if alive != self.was_alive {
            if let Some(k) = counted("life") {
                wlog(format!("{} {} #{k} with {} stardust kept", head(sim, me), if alive { "ALIVE" } else { "DEAD" },
                             self.kept.len()));
            }
            self.was_alive = alive;
        }
        // the stardust: remember new stacks, put back the ones a death cleared
        let have = stacks_on(sim, me, self.p.d_max);
        let gone = missing(&self.kept, &have);
        if !gone.is_empty() {
            for b in &gone {
                sim.add_buff(me, b);
            }
            if let Some(k) = counted("keep") {
                wlog(format!("{} KEEP #{k}: {} stardust put back ({}), {} in all", head(sim, me), gone.len(),
                             if alive { "alive" } else { "dead" }, self.kept.len()));
            }
        } else if alive && have.len() > self.kept.len() {
            if let Some(k) = counted("stack") {
                wlog(format!("{} STACK #{k}: {} -> {}", head(sim, me), self.kept.len(), have.len()));
            }
            self.kept = have;
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
        "=== {ID} v1 (stardust kept through death, Singularity's core executing by real health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:core"), CoreFx);
    module.add_native_passive(format!("{ID}:stardust"), Stardust::default());
    host.log(LogLevel::Info, "league_aurelionsol v1 loaded (Aurelion Sol: stardust kept, the black hole's execute).");
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
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"d_max":12,"e_low":6,"e_low_d":2,"x":1}"#), Params { d_max: 12, e_low: 6, e_low_d: 2 });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn stacks_are_the_data_s_names() {
        assert_eq!(stack_of("league_aurelionsol_d1", 15), Some(1));
        assert_eq!(stack_of("league_aurelionsol_d15", 15), Some(15));
        assert_eq!(stack_of("league_aurelionsol_d16", 15), None);
        assert_eq!(stack_of("league_aurelionsol_d0", 15), None);
        assert_eq!(stack_of("league_aurelionsol_dg", 15), None);
    }

    #[test]
    fn the_line_grows_with_stardust() {
        let p = Params::default();
        assert_eq!(execute_line(&p, 0), 5);
        assert_eq!(execute_line(&p, 15), 20);
        assert_eq!(execute_line(&p, 40), 20);
        assert!(executes(&p, 0, 49, 1000));
        assert!(!executes(&p, 0, 50, 1000));
        assert!(executes(&p, 15, 199, 1000));
        assert!(!executes(&p, 15, 0, 1000));
        assert!(!executes(&p, 15, 10, 0));
    }

    #[test]
    fn a_death_s_cleared_stacks_come_back() {
        let kept = vec![BuffV1::timed("league_aurelionsol_d1", 1), BuffV1::timed("league_aurelionsol_d2", 1)];
        assert_eq!(missing(&kept, &[]).len(), 2);
        assert_eq!(missing(&kept, &kept[..1]).len(), 1);
        assert!(missing(&kept, &kept).is_empty());
    }
}
