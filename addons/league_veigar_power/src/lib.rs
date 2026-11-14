//! 维迦附加包：被动「超凡邪力」叠的法术强度死了也不掉，和英雄联盟一样（用户：「顺便帮小法做一个 永久叠法强的」）。
//!
//! 主包保持纯数据：每一层是维迦身上一个永久的 `league_veigar_p_stack`（法术强度 +1，击杀英雄那一层 +5）。引擎在他死亡时清掉
//! 身上全部 buff，数据也没有「复活时」这个时机，所以主包里法强每条命从零叠起（说明里写着「死亡时清空」）。
//! `mod.override_info` 把主包的维迦换成 `override/` 里的副本：技能一字不改，只加了本包的被动 `league_veigar_power:keep`，
//! 它每 tick 看一次：
//!
//! - **活着**：把身上每一层 `league_veigar_p_stack` 原样记下来（记在被动里，被动在玩家身上，死了不丢）；
//! - **少了**（死亡或复活时引擎清掉）：缺的层原样补回（同样的数值）。死着的时候也补，倒下时数值不掉。
//!
//! 层数只会变多（主包从不去掉一层），所以「身上比记下的少」只会是死亡清掉的。
//!
//! 0.1.2（2026-11-14，用户看了「和英雄联盟不一样的地方」清单后说「全改吧」）：**E「扭曲空间」只有牢笼的边缘晕人**。英雄联盟：
//! "Enemies that collide with the edges of the cage are knocked down and stunned"，每次施放每人一次；主包的区域是实心的圆，
//! 成形时站在里面的人立刻被晕。副本把牢笼的两个眩晕区域换成原生效果 `league_veigar_power:cage`（落点上，告诉被动牢笼在哪）：
//! 它给维迦挂一个记号 `league_veigar_power_cage:<x>:<y>`，被动读到后记下这座牢笼（记在被动里，他死了牢笼照样在），之后
//! `cage_t` tick 里每 tick 看一次敌方单位（英雄、小兵、野怪；不含塔、选不中的）：身体碰到圆周（中心离牢笼中心 `cage_r` ±
//! 身体半径）的眩晕 `stun` tick，每座牢笼每人一次——站在里面不动的不晕，往外走、从外面进来、成形时正好站在圆周上的都晕；
//! 一 tick 里越过圆周的（闪现、传送）不晕。晕到英雄时照主包那样叠一层法强、记一次「连续命中」（R 的加伤）；他死着时不叠。
//! 黑暗物质、牢笼的画面、冷却都还是主包的数据。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_veigar_power.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_veigar_power";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_veigar_power") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 主包的一层法强。
pub const STACK: &str = "league_veigar_p_stack";
/// 主包的名字：被牢笼晕住的画面和声音、叠层的画面；「连续命中」的标记有这么多个（R 的加伤）。
pub const E_STUN: &str = "league_veigar_e_stun";
pub const P_GAIN: &str = "league_veigar_p_gain";
pub const HIT_MAX: usize = 4;
/// 原生效果 `cage` 给他挂的记号：`league_veigar_power_cage:<x>:<y>`，被动读到就取走。
pub const CAGE_MARK: &str = "league_veigar_power_cage:";
const MARK_T: usize = 4;
/// 读不到身体半径时用的（`champion_radius`）。
pub const BODY: f64 = 10_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VEIGAR_POWER_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_veigar_power.log");
        }
    }
    PathBuf::from("league_veigar_power.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (15 000 lines a session,
    // about 9 s of stalls on the simulation thread, 2026-10-12, the user: 「LOL mod让游戏掉帧很严重 加载很卡」)
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

// each kind of line: the first LOG_FIRST, then every LOG_EVERY-th
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;
static COUNTS: LazyLock<Mutex<std::collections::HashMap<&'static str, usize>>> =
    LazyLock::new(|| Mutex::new(std::collections::HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

// ===================== 参数 =====================

/// 牢笼的数字（`passive.params`，`make_override.py` 从主包的两个眩晕区域读出来）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 牢笼的半径、存在多久、眩晕多久。
    pub cage_r: usize,
    pub cage_t: usize,
    pub stun: usize,
    /// 「连续命中」标记的时长。
    pub hit_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { cage_r: 34_000, cage_t: 180, stun: 60, hit_t: 240 }
    }
}

/// `{"cage_r":34000,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k.trim().trim_matches('"') {
            "cage_r" => p.cage_r = v,
            "cage_t" => p.cage_t = v,
            "stun" => p.stun = v,
            "hit_t" => p.hit_t = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

pub fn cage_mark(x: u64, y: u64) -> String {
    format!("{CAGE_MARK}{x}:{y}")
}

pub fn parse_cage(name: &str) -> Option<(u64, u64)> {
    let (x, y) = name.strip_prefix(CAGE_MARK)?.split_once(':')?;
    Some((x.parse().ok()?, y.parse().ok()?))
}

/// 碰到牢笼的边缘：单位中心离牢笼中心 `d`、身体半径 `body`，圆周在 `r`。
pub fn touches(d: f64, r: f64, body: f64) -> bool {
    (d - r).abs() <= body
}

/// 一座牢笼：中心、哪一 tick 散、晕过谁（每人一次）。
#[derive(Clone, Debug, PartialEq)]
pub struct Cage {
    pub x: f64,
    pub y: f64,
    pub until: usize,
    pub done: Vec<usize>,
}

/// 一个敌方单位：编号、位置、身体半径。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: (f64, f64),
    pub body: f64,
}

/// 这一 tick 碰到 `cage` 边缘、还没被它晕过的单位（记进 `done`）。
pub fn struck(cage: &mut Cage, units: &[Unit], r: f64) -> Vec<usize> {
    let mut out = Vec::new();
    for u in units {
        let d = (u.at.0 - cage.x).hypot(u.at.1 - cage.y);
        if touches(d, r, u.body) && !cage.done.contains(&u.id) {
            cage.done.push(u.id);
            out.push(u.id);
        }
    }
    out
}

/// 主包「连续命中」的梯子：身上到第 `have` 个标记时再命中一次，之后到第几个（1 到它全部重挂）。
pub fn next_hits(have: usize) -> usize {
    (have + 1).min(HIT_MAX)
}

fn hit_flag(k: usize) -> String {
    format!("league_veigar_r_s{k}")
}

/// `kept` 里有、`have` 里没有的那些层（按完整的数值配对）。
pub fn missing(kept: &[BuffV1], have: &[BuffV1]) -> Vec<BuffV1> {
    let mut left: Vec<Option<&BuffV1>> = have.iter().map(Some).collect();
    let mut out = Vec::new();
    for k in kept {
        match left.iter_mut().find(|h| h.is_some_and(|h| h == k)) {
            Some(slot) => *slot = None,
            None => out.push(*k),
        }
    }
    out
}

fn buffs_named(sim: &StableSim<'_>, id: usize, name: &str) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).collect()
    })
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Keep {
    /// 这一局他叠到的每一层法强（活着时在身上看到的）。
    kept: Vec<BuffV1>,
    /// 上一 tick 他活着：死了 / 复活的那一刻记一行日志。
    was_alive: bool,
    /// 牢笼的数字、立着的牢笼、他是哪一队（读不到他时用）。
    p: Params,
    cages: Vec<Cage>,
    team: Option<usize>,
}

impl Keep {
    /// E 的牢笼：取走原生效果挂的记号，立着的每一座晕碰到边缘的敌方单位。
    fn watch_cages(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        let mut alive = false;
        let mut marks = Vec::new();
        if let Some(e) = sim.get_entity(me) {
            self.team = Some(e.team());
            alive = e.is_alive();
            marks = (0..e.buff_count())
                .filter_map(|i| e.buff_at(i))
                .filter_map(|b| parse_cage(b.name()).map(|at| (b.name().to_string(), at)))
                .collect();
        }
        for (name, (x, y)) in marks {
            sim.entity_remove_buff(me, &name);
            let (x, y) = (x as f64, y as f64);
            // the same mark read twice (it could not be taken off him): still one cage
            if self.cages.iter().any(|c| c.x == x && c.y == y && c.until + MARK_T >= now + self.p.cage_t) {
                continue;
            }
            self.cages.push(Cage { x, y, until: now + self.p.cage_t, done: Vec::new() });
            if let Some(k) = counted("cage") {
                wlog(format!(
                    "{} CAGE #{k} at ({x:.0}, {y:.0}): radius {}, {} ticks, its edge stuns {} ticks",
                    head(sim, me),
                    self.p.cage_r,
                    self.p.cage_t,
                    self.p.stun
                ));
            }
        }
        self.cages.retain(|c| c.until > now);
        let Some(team) = self.team else { return };
        if self.cages.is_empty() {
            return;
        }
        let mut champions = Vec::new();
        let units: Vec<Unit> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive() && u.is_targetable())
            .filter(|u| !u.is_tower() && !matches!(u.kind(), Some(EntityKindV1::Nexus | EntityKindV1::Tower)))
            .map(|u| {
                if u.is_champion() {
                    champions.push(u.id());
                }
                let (x, y) = u.pos();
                let body = u.radius();
                Unit { id: u.id(), at: (x as f64, y as f64), body: if body > 0 { body as f64 } else { BODY } }
            })
            .collect();
        let r = self.p.cage_r as f64;
        let hit: Vec<usize> = self.cages.iter_mut().flat_map(|c| struck(c, &units, r)).collect();
        for id in hit {
            sim.apply_cc(id, &CcV1::stun(self.p.stun as u64));
            let at = InputTargetV1::target(id);
            sim.play_view_effect(E_STUN, me, &at, 0, 0, 0);
            let champion = champions.contains(&id);
            if champion {
                sim.play_sfx(E_STUN, me, &at);
            }
            if champion && alive {
                // as the main pack's cage on a champion: a stack of Phenomenal Evil Power, one more hit in a row
                let mut stack = BuffV1::named(STACK);
                stack.magic_power = 1;
                sim.add_buff(me, &stack);
                sim.play_view_effect(P_GAIN, me, &InputTargetV1::target(me), 0, 0, 0);
                let have = (1..=HIT_MAX).rev().find(|&k| !buffs_named(sim, me, &hit_flag(k)).is_empty()).unwrap_or(0);
                for k in 1..=HIT_MAX {
                    sim.entity_remove_buff(me, &hit_flag(k));
                }
                for k in 1..=next_hits(have) {
                    sim.add_buff(me, &BuffV1::timed(&hit_flag(k), self.p.hit_t));
                }
            }
            if let Some(k) = counted("edge") {
                wlog(format!(
                    "{} EDGE #{k}: #{id} ({}) touched the cage's edge - stunned {} ticks{}",
                    head(sim, me),
                    if champion { "champion" } else { "unit" },
                    self.p.stun,
                    if champion && !alive { ", no stack (he is dead)" } else { "" }
                ));
            }
        }
    }
}

/// E 的牢笼立起的那一刻（副本里在落点上）：给他挂上带着落点的记号，被动下一次看到就立起牢笼。
struct CageFx;

impl StableEffectType for CageFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        // the landing's point; were the engine to hand over the unit it was cast on, where that unit stands
        let at = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Pos) => Some((input.x, input.y)),
            Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|e| e.pos()),
            _ => None,
        };
        let Some((x, y)) = at else {
            wlog(format!("{} cage: no point in the input (kind {})", head(sim, caster), input.kind));
            return;
        };
        sim.add_buff(caster, &BuffV1::timed(&cage_mark(x, y), MARK_T));
    }

    /// The edge's stun, for the AI's reading of E (the copy's tree holds no `Stun` any more).
    fn expected_cc_time(&self) -> Option<usize> {
        Some(Params::default().stun)
    }
}

impl StablePassive for Keep {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        self.watch_cages(sim, me);
        let Some(e) = sim.get_entity(me) else { return };
        let alive = e.is_alive();
        if alive != self.was_alive {
            wlog(format!("{} {} with {} stacks kept", head(sim, me), if alive { "ALIVE" } else { "DEAD" }, self.kept.len()));
            self.was_alive = alive;
        }
        let have = buffs_named(sim, me, STACK);
        let gone = missing(&self.kept, &have);
        if gone.is_empty() {
            if alive && have.len() > self.kept.len() {
                self.kept = have;
            }
            return;
        }
        for b in &gone {
            sim.add_buff(me, b);
        }
        wlog(format!(
            "{} KEEP {} stacks put back ({}), {} in all",
            head(sim, me),
            gone.len(),
            if alive { "alive" } else { "dead" },
            self.kept.len()
        ));
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Veigar: Phenomenal Evil Power kept through death; Event Horizon stuns at its edge only) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:cage"), CageFx);
    module.add_native_passive(format!("{ID}:keep"), Keep::default());
    host.log(LogLevel::Info, "league_veigar_power v2 loaded (Veigar: ability power stacks kept through death, the cage's edge stuns).");
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

    fn stack() -> BuffV1 {
        let mut b = BuffV1::named(STACK);
        b.magic_power = 1;
        b
    }

    #[test]
    fn the_mark_carries_the_cage() {
        let m = cage_mark(959_999, 123_456);
        assert!(m.len() <= BUFF_NAME_CAP, "{m}");
        assert_eq!(parse_cage(&m), Some((959_999, 123_456)));
        assert_eq!(parse_cage(STACK), None);
        assert_eq!(parse_cage("league_veigar_power_cage:12"), None);
    }

    #[test]
    fn only_the_edge_stuns() {
        // League: "Enemies that collide with the edges of the cage are knocked down and stunned"
        let r = 34_000.0;
        assert!(!touches(0.0, r, BODY), "the one it was cast on, in the middle");
        assert!(!touches(23_000.0, r, BODY), "walking about inside");
        assert!(touches(24_000.0, r, BODY), "his body reaches the wall from inside");
        assert!(touches(34_000.0, r, BODY) && touches(44_000.0, r, BODY), "on the wall, and reaching it from outside");
        assert!(!touches(45_000.0, r, BODY), "outside");
        assert!(touches(30_000.0, r, 5_000.0) && !touches(28_000.0, r, 5_000.0), "a smaller body");
    }

    #[test]
    fn each_unit_once_a_cage() {
        let mut cage = Cage { x: 100_000.0, y: 100_000.0, until: 180, done: Vec::new() };
        let unit = |id, dx: f64| Unit { id, at: (100_000.0 + dx, 100_000.0), body: BODY };
        // formed: #1 in the middle, #2 on the wall, #3 far outside
        assert_eq!(struck(&mut cage, &[unit(1, 0.0), unit(2, 30_000.0), unit(3, 80_000.0)], 34_000.0), vec![2]);
        // #1 walks out through the wall, #3 walks in through it, #2 still stands on it
        assert_eq!(struck(&mut cage, &[unit(1, -25_000.0), unit(2, 30_000.0), unit(3, 43_000.0)], 34_000.0), vec![1, 3]);
        // nobody twice, also after walking out and back in
        assert_eq!(struck(&mut cage, &[unit(1, 0.0), unit(2, 0.0), unit(3, 0.0)], 34_000.0), Vec::<usize>::new());
        assert_eq!(struck(&mut cage, &[unit(1, 34_000.0), unit(2, 34_000.0), unit(3, 34_000.0)], 34_000.0), Vec::<usize>::new());
        // a blink from the middle to far outside within one tick never touches it
        assert_eq!(struck(&mut cage, &[unit(4, 0.0)], 34_000.0), Vec::<usize>::new());
        assert_eq!(struck(&mut cage, &[unit(4, 60_000.0)], 34_000.0), Vec::<usize>::new());
    }

    #[test]
    fn the_hits_in_a_row_climb_as_the_main_packs_ladder() {
        assert_eq!((0..=4).map(next_hits).collect::<Vec<_>>(), vec![1, 2, 3, 4, 4]);
        assert!(hit_flag(4).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn the_cage_numbers_come_from_the_champion_data() {
        let p = parse_params(r#"{"cage_r":30000,"cage_t":150,"hit_t":200,"stun":90,"unknown":1}"#);
        assert_eq!(p, Params { cage_r: 30_000, cage_t: 150, stun: 90, hit_t: 200 });
        assert_eq!(parse_params("{}"), Params::default());
        // the override's own params are the defaults (the effect's expected_cc_time reads the default stun)
        let text = include_str!("../override/league_veigar.data_champion");
        let at = text.find("\"passive_ref\": \"league_veigar_power:keep\"").expect("the passive in the override");
        let body = &text[at..];
        let json = &body[body.find('{').unwrap()..=body.find('}').unwrap()];
        assert_eq!(parse_params(json), Params::default(), "{json}");
        assert!(text.contains("\"effect_ref\": \"league_veigar_power:cage\""), "the cage's native effect in the override");
        assert!(!text.contains("league_veigar_e_zone"), "the solid stun zones are gone from the override");
    }

    #[test]
    fn nothing_missing_while_he_keeps_them() {
        let kept = vec![stack(); 7];
        assert!(missing(&kept, &vec![stack(); 7]).is_empty());
        assert!(missing(&kept, &vec![stack(); 9]).is_empty());
    }

    #[test]
    fn a_death_puts_every_stack_back() {
        let kept = vec![stack(); 92];
        let back = missing(&kept, &[]);
        assert_eq!(back.len(), 92);
        assert!(back.iter().all(|b| b.name() == STACK && b.magic_power == 1));
        assert_eq!(missing(&kept, &vec![stack(); 90]).len(), 2);
    }
}
