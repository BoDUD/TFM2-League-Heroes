//! 科加斯附加包：盛宴的层数死后不掉；R 只在一口吃得死人时放（和英雄联盟一样：盛宴是斩杀技）。
//!
//! 主包保持纯数据：盛宴吃死一个英雄，他身上多一个永久的 `league_chogath_r_stack`（最大生命 +r_stack_hp，league.dll 按
//! 个数把身体画大）。引擎在他死亡时清掉身上全部 buff，数据也没有「复活时」这个时机，所以主包里层数每条命从零叠起；
//! R 由 AI 对「队伍刚打过的敌方英雄」放出，读不到当前生命，常常咬不死。
//! `mod.override_info` 把主包的科加斯换成 `override/` 里的副本：技能一字不改，只挂上本包的被动 `league_chogath:keep`，
//! 外加一个 AI 钩子 `league_chogath:feast`：
//!
//! - **被动 keep**（维迦附加包的做法）：活着时把身上每一层 `league_chogath_r_stack` 原样记下来；少了（死亡清掉的）就原样
//!   补回。层数只会变多（主包从不去掉一层），所以「身上比记下的少」只会是死亡清掉的。补回的层带着生命，复活后生命上限照旧。
//!   第 2、3……层另挂一个没有属性的记号 `league_chogath_r_stack_2`、`_3`……（`mark`）：游戏的显示层同名的 buff 只留一个，
//!   league.dll 按身上的层数把他画大，读到的永远是 1 层（2026-11-02：两层两分钟，画的一直是 x1.30），它也数这些记号。
//! - **AI 钩子 feast**（诺手大招附加包的做法）：读射程内敌方英雄的生命、护盾、免死和受到伤害的增减，照主包的数字算这一口：
//!   `R_DMG` + 他最大生命的 `R_HP`% 真实伤害，加法强 `R_AP`% 的魔法伤害（主包先挂 100% 魔抗穿透，等于真实）。有人一口吃得死：
//!   放，几个时吃生命 + 护盾最少的，AI 没想放也放；AI 想放 R 却吃不死：改成普攻那个人（打不到就走过去）。射程和游戏的 AI
//!   一样算到两人的身体（`reach`：中心到中心 `R_RANGE` + 两个半径）；`FEAST HELD` 写出真正的原因（`held`）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_chogath.log`，每次启动游戏重写，上一次的留在 .prev.log；你看的
//! 那场全记，服务端预模拟每种前 `PRESIM_FIRST` 行、之后每 `PRESIM_EVERY` 行记一行。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_chogath";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_chogath") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const HERO: &str = "league_chogath";
/// 主包的一层盛宴。
pub const STACK: &str = "league_chogath_r_stack";
/// 主包的数字（tools/kit/build_chogath.py P；make_override.py 核对）：一口的真实伤害、他最大生命的百分比、法强的百分比，
/// R 的射程。
pub const R_DMG: usize = 300;
pub const R_HP: usize = 5;
pub const R_AP: usize = 50;
pub const R_RANGE: usize = 30_000;
/// R 从这一级起能放（同 league_pyke、league_darius_ult）。
const ULT_LEVEL: usize = 5;
/// 同一类日志至少隔这么多 tick 记一次（AI 每 tick 想一次）。
const LOG_EVERY: usize = 120;
/// A kind of line in the server's presims (hundreds of runs a launch): the first PRESIM_FIRST of the launch, then every
/// PRESIM_EVERY-th (10-30: FEAST HELD, one a LOG_EVERY per AI with no cap, was 1.1 MB of the launch's 1.4 MB).
const PRESIM_FIRST: usize = 40;
const PRESIM_EVERY: usize = 200;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_CHOGATH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_chogath.log");
        }
    }
    PathBuf::from("league_chogath.log")
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

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// The match you watch (the view, a spectated match, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

/// One more line of a kind: its count when it is to be logged - every one when `shown` (the match on screen), the
/// presims' the first PRESIM_FIRST, then every PRESIM_EVERY-th.
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= PRESIM_FIRST || *n % PRESIM_EVERY == 0).then_some(*n)
}

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    noted(kind, on_screen(sim))
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

// ===================== 计算 =====================

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

/// 一口盛宴的伤害（落到人身上之前）：真实伤害 R_DMG + 他最大生命的 R_HP%，加法强的 R_AP%（穿透全部魔抗）。
pub fn bite(max_hp: usize, ap: usize) -> usize {
    R_DMG + max_hp * R_HP / 100 + ap * R_AP / 100
}

/// Feast's reach, centre to centre: the game's AI starts an action at its `range` plus both units' radii
/// (champion-data.md, league_garen E). 0.1.4 counted R_RANGE alone, so a champion the AI fed on from 30000-50000 was
/// "out of range", the Feast held and turned into an attack.
pub fn reach(my_radius: usize, their_radius: usize) -> u64 {
    (R_RANGE + my_radius + their_radius) as u64
}

/// A squared centre-to-centre distance (`StableSim::distance_sq`) within `reach`.
pub fn within(dist_sq: u64, reach: u64) -> bool {
    dist_sq <= reach.saturating_mul(reach)
}

/// 一个敌方英雄：生命、护盾，身上 buff 的免死和受到伤害增减。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub hp: usize,
    pub shield: usize,
    pub undying: bool,
    pub reduce: usize,
    pub amplify: usize,
    pub skill_reduce: usize,
}

impl Foe {
    pub fn ehp(&self) -> usize {
        self.hp + self.shield
    }

    /// `d` 点伤害落到他身上是多少（league_darius_ult 在经典 SDK 的引擎里量的：减伤和增伤相加后一起乘，技能减伤再乘一次）。
    pub fn damage_from(&self, d: usize) -> usize {
        let taken = (100 + self.amplify).saturating_sub(self.reduce);
        d * taken / 100 * 100usize.saturating_sub(self.skill_reduce) / 100
    }

    pub fn dies_to(&self, d: usize) -> bool {
        !self.undying && self.damage_from(d) >= self.ehp()
    }
}

/// 这个 buff 算不算「杀不死」：带「不死」，但别的附加包一直挂着的被动护身（名字以 `_p_guard` / `_rv_guard` 结尾：死歌、塞恩、
/// 艾尼维亚、扎克、扎恩、tft 的石甲虫）不算——英雄联盟里处决他们照样算击杀，他们死进自己的被动里（2026-11-05 复查：死歌被动
/// 好着就一直「杀不死」）。千珏的大招、基兰的符文、凯尔的大招等真的杀不死，照样等。league_renata 的救难也是这个顺序。
pub fn holds_execute(name: &str, undying: bool) -> bool {
    undying && !name.ends_with("_p_guard") && !name.ends_with("_rv_guard")
}

/// 吃得死的人里生命 + 护盾最少的。
pub fn best_kill(foes: &[Foe], d: usize) -> Option<Foe> {
    foes.iter().copied().filter(|f| f.dies_to(d)).min_by_key(|f| (f.ehp(), f.id))
}

/// The AI's Feast target as the hook reads it: the champion, how far he stands (centre to centre) against the reach
/// (R_RANGE plus both bodies), and whether he can be targeted.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Aimed {
    pub foe: Foe,
    pub dist: u64,
    pub reach: u64,
    pub targetable: bool,
}

/// Why the AI's Feast was held (the HELD line; 0.1.4 always said "hp + shield > a bite", even of a champion one bite
/// killed who stood out of its range).
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Held {
    /// the AI's R has no unit target
    NoTarget,
    /// the target is no enemy champion alive
    NotFoe(usize),
    /// below ULT_LEVEL
    Level(usize),
    /// R's cooldown left (None: unread)
    Cooldown(Option<usize>),
    OutOfRange { id: usize, dist: u64, reach: u64 },
    Untargetable(usize),
    /// `is_valid_input` refuses the R on him
    Invalid(usize),
    Undying(usize),
    /// one bite (after his damage-taken changes) leaves him alive
    NoKill { id: usize, ehp: usize, bite: usize },
}

impl Held {
    pub fn text(&self) -> String {
        match *self {
            Held::NoTarget => "no champion target".to_string(),
            Held::NotFoe(x) => format!("#{x} is no enemy champion alive"),
            Held::Level(l) => format!("level {l} < {ULT_LEVEL}"),
            Held::Cooldown(Some(t)) => format!("R on cooldown ({t} ticks)"),
            Held::Cooldown(None) => "R's cooldown unread".to_string(),
            Held::OutOfRange { id, dist, reach } => format!("#{id} out of range ({dist} > {reach} centre to centre)"),
            Held::Untargetable(x) => format!("#{x} untargetable"),
            Held::Invalid(x) => format!("R on #{x} is no valid input"),
            Held::Undying(x) => format!("#{x} cannot die (undying)"),
            Held::NoKill { id, ehp, bite } => format!("#{id} hp + shield {ehp} > a bite of {bite}"),
        }
    }
}

/// Every reason the AI's Feast on `target` is held: his level, R's cooldown `cd`, then the target - out of range,
/// untargetable, refused by the game (`valid`), cannot die, or one bite of `d` leaves him alive.
pub fn held(target: Option<usize>, aimed: Option<Aimed>, level: usize, cd: Option<usize>, valid: bool, d: usize) -> Vec<Held> {
    let mut why = Vec::new();
    if level < ULT_LEVEL {
        why.push(Held::Level(level));
    }
    if cd != Some(0) {
        why.push(Held::Cooldown(cd));
    }
    match (target, aimed) {
        (None, _) => why.push(Held::NoTarget),
        (Some(x), None) => why.push(Held::NotFoe(x)),
        (Some(x), Some(a)) => {
            if a.dist > a.reach {
                why.push(Held::OutOfRange { id: x, dist: a.dist, reach: a.reach });
            }
            if !a.targetable {
                why.push(Held::Untargetable(x));
            }
            if !valid {
                why.push(Held::Invalid(x));
            }
            if a.foe.undying {
                why.push(Held::Undying(x));
            } else if !a.foe.dies_to(d) {
                why.push(Held::NoKill { id: x, ehp: a.foe.ehp(), bite: a.foe.damage_from(d) });
            }
        }
    }
    why
}

/// The mark of the `k`th stack (2 and up): a name of its own, which the game's display keeps.
pub fn mark_name(k: usize) -> String {
    format!("{STACK}_{k}")
}

/// The marks of stacks 2 to `n` he lacks (a death clears them with the stacks), put on with no stats.
fn mark(sim: &mut StableSim<'_>, me: usize, n: usize) {
    let have: Vec<String> = sim.get_entity(me).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect()
    });
    for k in 2..=n {
        let name = mark_name(k);
        if !have.contains(&name) {
            sim.add_buff(me, &BuffV1::named(&name));
        }
    }
}

fn buffs_named(sim: &StableSim<'_>, id: usize, name: &str) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).collect()
    })
}

fn read_foe(e: &StableEntity<'_, '_>) -> Foe {
    let mut foe = Foe { id: e.id(), hp: e.hp().0, shield: e.shield(), ..Foe::default() };
    for b in (0..e.buff_count()).filter_map(|i| e.buff_at(i)) {
        foe.undying |= holds_execute(b.name(), b.undying);
        foe.reduce += b.damaged_reduce;
        foe.amplify += b.damaged_amplify;
        foe.skill_reduce += b.skill_damaged_reduce;
    }
    foe
}

// ===================== 被动：层数死后补回 =====================

#[derive(Clone, Default)]
struct Keep {
    /// 这一局他叠到的每一层（活着时在身上看到的）。
    kept: Vec<BuffV1>,
    /// 上一 tick 他活着：死了 / 复活的那一刻记一行日志。
    was_alive: bool,
}

impl StablePassive for Keep {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let alive = e.is_alive();
        if alive != self.was_alive {
            if tally(sim, if alive { "alive" } else { "dead" }).is_some() {
                wlog(format!("{} {} with {} Feast stacks kept", head(sim, me), if alive { "ALIVE" } else { "DEAD" },
                             self.kept.len()));
            }
            self.was_alive = alive;
        }
        let have = buffs_named(sim, me, STACK);
        let gone = missing(&self.kept, &have);
        if gone.is_empty() {
            if alive && have.len() > self.kept.len() {
                if tally(sim, "stack").is_some() {
                    wlog(format!("{} STACK {} -> {} (+{} max health a stack)", head(sim, me), self.kept.len(),
                                 have.len(), have.last().map_or(0, |b| b.hp)));
                }
                self.kept = have;
                mark(sim, me, self.kept.len());
            }
            return;
        }
        for b in &gone {
            sim.add_buff(me, b);
        }
        mark(sim, me, self.kept.len());
        if tally(sim, "keep").is_some() {
            wlog(format!("{} KEEP {} stacks put back ({}), {} in all", head(sim, me), gone.len(),
                         if alive { "alive" } else { "dead" }, self.kept.len()));
        }
    }
}

// ===================== AI 钩子：R 只为一口吃死 =====================

fn ult(id: usize) -> InputV1 {
    InputV1::action(InputKindV1::Ult, InputTargetV1::target(id))
}

#[derive(Clone, Default)]
struct FeastAi {
    last_hold: Option<usize>,
    last_cast: Option<(usize, usize)>,
    told_no_sim: bool,
}

impl StablePlayerAi for FeastAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:feast")
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
        let wants_ult = base.is_some_and(|b| b.kind == InputKindV1::Ult.code());
        let ai_target = base.filter(|_| wants_ult).and_then(|b| {
            (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
        });
        // AI 在放别的技能或回城：不抢着放 R（AI 自己想放的 R 照样检查）
        let busy = base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Return))
        });
        let read = {
            let Some(sim) = ctx.sim() else {
                if !self.told_no_sim {
                    self.told_no_sim = true;
                    wlog(format!("t={tick} player {player}: no simulation to read, R left to the AI"));
                }
                return None;
            };
            (|| {
                let pl = sim.get_player(player)?;
                let cd = pl.cooldowns().map(|c| c.3);
                let level = pl.level();
                let me = pl.champion().filter(|e| e.is_alive())?;
                // `is_valid_input` does not look at cooldowns (league_pyke): an R order on cooldown holds him still
                let free = level >= ULT_LEVEL && cd == Some(0);
                let (id, team, body) = (me.id(), me.team(), me.radius());
                let enemy = |e: &StableEntity<'_, '_>| e.is_champion() && e.is_alive() && e.team() != team;
                // (centre to centre squared, R_RANGE plus both bodies): as far as the game's AI casts from
                let span = |e: &StableEntity<'_, '_>| (sim.distance_sq(id, e.id()), reach(body, e.radius()));
                let foes: Vec<Foe> = (0..sim.entity_count())
                    .filter_map(|i| sim.entity_at(i))
                    .filter(|e| enemy(e) && e.is_targetable() && {
                        let (d2, r) = span(e);
                        within(d2, r)
                    })
                    .map(|e| read_foe(&e))
                    .collect();
                let target = ai_target.and_then(|t| sim.get_entity(t));
                let aimed = target.as_ref().filter(|e| enemy(e)).map(|e| {
                    let (d2, r) = span(e);
                    // rounded up: past the reach by any fraction reads as past it, as `within` counts it
                    Aimed { foe: read_foe(e), dist: (d2 as f64).sqrt().ceil() as u64, reach: r, targetable: e.is_targetable() }
                });
                let target_pos = target.as_ref().map(|e| e.pos());
                let d = bite(me.hp().1, me.stat().magic_power);
                let line = (head(&sim, id), on_screen(&sim));
                Some((d, (free, level, cd), foes, aimed, target_pos, me.pos(), line, buffs_named(&sim, id, STACK).len()))
            })()
        };
        let (d, (free, level, cd), foes, aimed, target_pos, my_pos, (line, shown), stacks) = read?;
        let foes: Vec<Foe> = foes.into_iter().filter(|f| ctx.is_valid_input(&ult(f.id))).collect();
        if free && !busy {
            if let Some(f) = best_kill(&foes, d) {
                if self.last_cast.is_none_or(|(t0, i)| i != f.id || tick >= t0 + LOG_EVERY) {
                    self.last_cast = Some((tick, f.id));
                    if noted("feast", shown).is_some() {
                        wlog(format!("{line} FEAST #{}: hp + shield {} vs a bite of {} ({d} before his damage taken \
                                      changes), {stacks} stacks{}", f.id, f.ehp(), f.damage_from(d),
                                     if wants_ult { "" } else { ", the AI had not cast it" }));
                    }
                }
                return Some(ult(f.id));
            }
        }
        if !wants_ult {
            return None;
        }
        // AI 想放 R 却吃不死（或够不着、冷却、等级、输入不合法）：改普攻那个人（打不到就走过去），R 留着
        if self.last_hold.is_none_or(|t0| tick >= t0 + LOG_EVERY) {
            self.last_hold = Some(tick);
            if noted("feast_held", shown).is_some() {
                let valid = ai_target.is_some_and(|x| ctx.is_valid_input(&ult(x)));
                let why: Vec<String> = held(ai_target, aimed, level, cd, valid, d).iter().map(Held::text).collect();
                let why = if why.is_empty() { "no reason found".to_string() } else { why.join(", ") };
                wlog(format!("{line} FEAST HELD: {why}, attacking instead"));
            }
        }
        if let Some(x) = ai_target {
            let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(x));
            if ctx.is_valid_input(&attack) {
                return Some(attack);
            }
        }
        let (x, y) = target_pos.unwrap_or(my_pos);
        Some(InputV1::move_to(x, y))
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Cho'Gath: Feast stacks kept through death, Feast only for a kill) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:keep"), Keep::default());
    module.add_player_input_ai(FeastAi::default());
    host.log(LogLevel::Info, "league_chogath v1 loaded (Cho'Gath: Feast stacks kept through death, Feast only for a kill).");
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
        b.hp = 70;
        b
    }

    #[test]
    fn each_stack_after_the_first_has_a_mark_of_its_own() {
        assert_eq!(mark_name(2), "league_chogath_r_stack_2");
        assert_eq!(mark_name(12), "league_chogath_r_stack_12");
        assert!(mark_name(999).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn a_death_puts_every_stack_back() {
        let kept = vec![stack(); 9];
        assert!(missing(&kept, &vec![stack(); 9]).is_empty());
        assert!(missing(&kept, &vec![stack(); 10]).is_empty());
        let back = missing(&kept, &[]);
        assert_eq!(back.len(), 9);
        assert!(back.iter().all(|b| b.name() == STACK && b.hp == 70));
    }

    #[test]
    fn feast_kills_only_what_one_bite_finishes() {
        let d = bite(2000, 100); // 300 + 100 + 50
        assert_eq!(d, 450);
        let low = Foe { id: 1, hp: 400, shield: 40, ..Foe::default() };
        let high = Foe { id: 2, hp: 900, ..Foe::default() };
        let tough = Foe { id: 3, hp: 400, reduce: 20, ..Foe::default() };
        let undying = Foe { id: 4, hp: 10, undying: true, ..Foe::default() };
        assert_eq!(best_kill(&[high, low, undying], d), Some(low));
        assert_eq!(best_kill(&[high, tough], d), None); // 450 x 80% = 360 < 400
        assert_eq!(best_kill(&[high], d), None);
    }

    #[test]
    fn feast_reaches_as_far_as_the_ai_casts() {
        // two champions of the game's 10000 radius: R_RANGE + both bodies, centre to centre
        let r = reach(10_000, 10_000);
        assert_eq!(r, 50_000);
        // 0.1.4 held these: past R_RANGE alone, within the game's reach
        assert!(within(45_000 * 45_000, r));
        assert!(within(50_000 * 50_000, r));
        assert!(!within(50_001 * 50_001, r));
        // a bigger body (Feast stacks) reaches farther
        assert!(within(55_000 * 55_000, reach(15_000, 10_000)));
        // distance_sq's "no slot" answer
        assert!(!within(u64::MAX, r));
    }

    #[test]
    fn the_held_line_gives_the_real_reason() {
        let d = 545;
        // the 11-02 log: "#522 hp + shield 240 > a bite of 545" - one bite killed him, he stood out of reach
        let low = Foe { id: 522, hp: 200, shield: 40, ..Foe::default() };
        let far = Aimed { foe: low, dist: 52_000, reach: 50_000, targetable: true };
        let why = held(Some(522), Some(far), 9, Some(0), true, d);
        assert_eq!(why, vec![Held::OutOfRange { id: 522, dist: 52_000, reach: 50_000 }]);
        assert!(!why.iter().any(|h| h.text().contains("a bite")));
        // in reach and too healthy: the bite, truthfully
        let high = Aimed { foe: Foe { id: 7, hp: 900, ..Foe::default() }, dist: 40_000, reach: 50_000, targetable: true };
        assert_eq!(held(Some(7), Some(high), 9, Some(0), true, d), vec![Held::NoKill { id: 7, ehp: 900, bite: 545 }]);
        assert_eq!(Held::NoKill { id: 7, ehp: 900, bite: 545 }.text(), "#7 hp + shield 900 > a bite of 545");
        // killable and in reach, but R not ready or not his to press
        let near = Aimed { foe: low, dist: 30_000, reach: 50_000, targetable: true };
        assert_eq!(held(Some(522), Some(near), 9, Some(120), true, d), vec![Held::Cooldown(Some(120))]);
        assert_eq!(held(Some(522), Some(near), 4, Some(0), true, d), vec![Held::Level(4)]);
        assert_eq!(held(Some(522), Some(near), 9, Some(0), false, d), vec![Held::Invalid(522)]);
        let hidden = Aimed { targetable: false, ..near };
        assert_eq!(held(Some(522), Some(hidden), 9, Some(0), false, d), vec![Held::Untargetable(522), Held::Invalid(522)]);
        let undying = Aimed { foe: Foe { undying: true, ..low }, ..near };
        assert_eq!(held(Some(522), Some(undying), 9, Some(0), true, d), vec![Held::Undying(522)]);
        // no champion to aim at
        assert_eq!(held(None, None, 9, Some(0), true, d), vec![Held::NoTarget]);
        assert_eq!(held(Some(3), None, 9, Some(0), true, d), vec![Held::NotFoe(3)]);
        // every check passed: nothing to hold (the hook casts)
        assert!(held(Some(522), Some(near), 9, Some(0), true, d).is_empty());
    }

    #[test]
    fn a_passive_guard_does_not_make_him_unkillable() {
        // 11-05 review: Karthus / Sion / Anivia / Zac / Zaahen / Krug keep a permanent *_p_guard / *_rv_guard; League
        // counts an execute on them as a kill (they die into the passive)
        for g in ["league_karthus_p_guard", "league_sion_p_guard", "league_anivia_p_guard", "league_zac_p_guard",
                  "league_zaahen_rv_guard", "tft_krug_p_guard"] {
            assert!(!holds_execute(g, true), "{g}");
        }
        assert!(holds_execute("league_kindred_r_on", true));
        assert!(holds_execute("league_zilean_r_rune", true));
        assert!(holds_execute("league_karthus_p_spirit", true));
        assert!(!holds_execute("league_kindred_r_on", false));
    }
}
