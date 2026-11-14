//! 克格莫附加包：被动「艾卡西亚的惊喜」按英雄联盟做（用户 2026-11-14 看了旧彗星的 GIF：「大嘴死了还是看不到炸人啊」，然后
//! 「按英雄联盟改」）。英雄联盟里他死后身体本身化成发光的虚空形态，4 秒里冲向最近的敌人，然后爆炸，对周围的敌人造成真实伤害。
//!
//! 主包（纯数据）在每条命里放一个「看守」：每 6 tick 往他身上投一个看不见的抛物线弹，落地时问「他还在吗」，不在了就醒来
//! （`wake`：他倒下处的光 `p_wake` 和两个声音，再在 70000 内随便一个敌方英雄身上放一颗速度 1000 的追踪小彗星 `p_form` 和一个
//! 看不见的溅射）。彗星 29 x 11 像素、飞 0.25 秒，游戏里几乎看不见（452 次阵亡醒了 413 次，都画了）。
//!
//! `mod.override_info` 把主包的克格莫换成 `override/` 里的副本（`make_override.py` 从主包生成）：`wake` 里只有彗星和溅射那一
//! 支换成本包的原生效果 `league_kogmaw:void`，`p_wake` 的光和声音、看守本身、普攻、Q / W / E / R 一个字节不变；普攻的说明换成
//! 本包的（被动那一句）；挂上本包的被动 `league_kogmaw:life`；多一个画面 `league_kogmaw_p_void`（爆炸，
//! `league/effects/league_kogmaw_burst`）。
//!
//! - **被动 `life`**：他活着时每 tick 把他的攻击力、队伍、生命上限、护甲、魔抗、位置记下来（按这份模拟的编号和他的实体号，
//!   [`LIVES`]）——游戏里他一死英雄实体就没了（`champion()` 读不到，复活是新的实体），死后谁也读不到他的攻击力。
//! - **`:void`（看守醒来那一刻）**：在醒来的地方（他的身体）用稳定 mod API 的 `spawn_unit` 生成单位 `league_kogmaw_void`
//!   （[`form_spec`]：他的生命上限、护甲、魔抗，移速 1，攻击 0、够不着任何人，活 [`FORM_T`] + [`LIFE_SLACK`] tick）。单位的
//!   图是他自己的帧改成虚空的颜色（`tools/art/unit_kogmaw_void.py`，和他一样大），league.dll 按 PPU 1.794 画高清帧。
//! - **比赛钩子 [`Forms`]**（死了的英雄的被动不跑；比赛钩子每份模拟每 tick 都跑）：单位读成站稳的单位以后挂上
//!   [`GUARD`]（受到的伤害 -100%、不死、穿墙），之后每 tick 找最近的敌方英雄（活着、选得中），朝它挪 [`P_SPEED`]
//!   （`entity_set_pos`，主包彗星的速度），挂 1 tick 的 [`GO`]（显示钩子见它就画跑），清掉身上的控制、嘲讽到那个英雄（让引擎
//!   自己的单位 AI 也朝它，画面朝向跟着走）。离那个英雄中心不到 [`P_R`] + 它的半径（主包溅射的判定）就爆炸；[`FORM_T`]
//!   （英雄联盟的 4 秒）到了也爆炸。宿主不让挪单位（`entity_set_pos` 不收）时把它的移速换成 [`P_SPEED`]
//!   （`entity_set_base_stat`），由引擎自己朝嘲讽的那个英雄走（`VOID WALK`）。
//! - **爆炸**：[`P_R`] + 半径内每个敌人（不含防御塔、水晶、虚空形态）受到 [`P_DMG`] + [`P_RATIO`]% 他死前攻击力的真实伤害
//!   （主包溅射的数），先以他的名义（他的旧实体号），宿主不收再以形态的名义；爆炸画面 `p_void` 比旧的 `p_boom` 大得多、亮得多
//!   （`tools/art/fx_kogmaw_burst.py`），每个挨炸的人身上 `p_hit`，`p_boom` 的声音。形态随后放逐到时间结束（API 没有让单位
//!   消失的接口，萨科、妮蔻也这么做）。
//! - **退路**（和别的召唤物一样，什么都不丢）：宿主没有 `spawn_unit`、拒绝了、给的 id [`LOOKS`] tick 内读不成单位，或测试开关
//!   `unit=off`——照主包放彗星：`spawn_projectile` 一颗 `p_form` 追向 [`P_SEEK`] 内最近的敌方英雄，到了由 `:burst` 结算同样的
//!   溅射；宿主连彗星都不收，就直接在那个英雄身上炸。形态还没炸就没了（被什么东西弄没了），就在它最后站的地方炸。
//!
//! 每份模拟一个编号（[`sim_no`]，league_eggs / league_karthus 的做法：挂在两边水晶上的 `league_kogmaw_sim:<n>`，水晶不收挂防御
//! 塔）：服务器并排跑的两份预演种子、实体号都一样，状态只按这些记会串；编号带 `_sim:`，league.dll 的分叉校验不看它。两边都选
//! 克格莫时各记各的（实体号不同），各炸对面。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kogmaw.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `VOID SPAWN`（醒来、单位、他的攻击力、伤害）、`VOID LOOK`（单位读回来的样子、护身挂上没有）、`VOID STEP`（抽样：追谁、
//! 多远、离他倒下处多远）、`VOID BURST`（为什么炸、追了多久、离他倒下处多远、炸到谁各多少、以谁的名义、放逐了没有）、
//! `VOID FALLBACK`（退路：为什么、彗星放没放）、`VOID DRAW`（显示钩子：引擎画的是什么、换了几次）。你看的那场每行都记，
//! 预演限了条数。测试开关：日志旁边的 `league_kogmaw.cfg`（`unit=off` / `name=`）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

// the shared part of the summons (league_shaco_backstab's summon.rs); not every item of it is used here
#[allow(dead_code)]
#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

pub mod view;

pub use summon::Pt;

const ID: &str = "league_kogmaw";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_kogmaw") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

// ===================== 数字（主包 tools/kit/build_kogmaw.py 的 P：测试和 make_override.py 对照） =====================

/// The burst: p_dmg + p_ratio % of his attack, true damage, to every enemy within p_r (+ its radius) of it.
pub const P_DMG: usize = 80;
pub const P_RATIO: usize = 100;
pub const P_R: usize = 12_000;
/// The form's pace a tick (the main pack's comet's: a champion steps ~880).
pub const P_SPEED: usize = 1_000;
/// The fallback comet looks this far round the wake for a champion (the main pack's RandomTarget).
pub const P_SEEK: usize = 70_000;
/// League's 4 s: the form bursts at this age at the latest.
pub const FORM_T: usize = 240;
/// The unit lives a little longer than that (the burst comes first; then it is banished for what is left).
pub const LIFE_SLACK: usize = 3;
/// Ticks the hook waits for the unit to read as a settled one (summon.rs FLOCK_LOOKS) before the comet goes instead.
pub const LOOKS: usize = 5;
/// A second wake of the same Kog'Maw within this many ticks is the same death (a second watch lob in the air).
pub const WAKE_GAP: usize = 30;
/// VOID STEP lines: one every this many ticks of a form's life on the screen's match (the presims: sampled further).
pub const STEP_EVERY: usize = 15;

// ===================== 名字 =====================

/// The unit (the game draws it from asset/base/aseprite_resources/champions/<name>; mod.override_info sends that to the
/// main pack's league/champions/league_kogmaw_void).
pub const UNIT: &str = "league_kogmaw_void";
pub const PASSIVE: &str = "league_kogmaw:life";
pub const VOID_FX: &str = "league_kogmaw:void";
pub const BURST_FX: &str = "league_kogmaw:burst";
/// On the form once it has settled: no damage, undying, through walls (not crowd-control immune: the hook clears its
/// crowd control itself and taunts it at its prey).
pub const GUARD: &str = "league_kogmaw_void_guard";
/// On the form while it walks (1 tick, renewed): the display hook draws it running.
pub const GO: &str = "league_kogmaw_void_go";
/// This simulation's number on its nexuses (or towers).
pub const SIM_TAG: &str = "league_kogmaw_sim:";
/// The copy's pictures and sounds: the burst (new), a hit enemy, the comet and its hit (the main pack's).
pub const VOID_VIEW: &str = "league_kogmaw_p_void";
pub const HIT_VIEW: &str = "league_kogmaw_p_hit";
pub const BOOM: &str = "league_kogmaw_p_boom";
pub const FORM_PROJ: &str = "league_kogmaw_p_form";
/// His own champion id: an entity under his old id still his body (the guardian angel's lying) reads as this.
pub const HERO: &str = "league_kogmaw";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KOGMAW_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_kogmaw.log");
        }
    }
    PathBuf::from("league_kogmaw.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the game, 2026-10-12)
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

/// Lines of a kind: the server's presims the first `LOG_FIRST`, then every `LOG_EVERY`-th; the match on screen all.
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn shown(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let on_screen = shown(sim);
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (on_screen || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
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

/// The test knobs (`league_kogmaw.cfg` beside the log), read once: `unit=off` (the comet as before), `name=`.
static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

// ===================== 规则（单元测试用） =====================

/// The burst's true damage from his attack `ad` (the main pack's FixedAttack: p_dmg + p_ratio % AD).
pub fn burst_damage(ad: usize) -> usize {
    P_DMG + P_RATIO * ad / 100
}

/// How near a unit of radius `radius` the burst reaches (the engine's circles count the unit's radius).
pub fn reach(radius: usize) -> f64 {
    (P_R + radius) as f64
}

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// One tick's walk from `from` toward `to` at `speed`, never past it: (where it ends, how far it went).
pub fn step_toward(from: Pt, to: Pt, speed: f64) -> (Pt, f64) {
    let d = dist(from, to);
    if d < 1e-9 {
        return (from, 0.0);
    }
    let s = speed.min(d);
    ((from.0 + (to.0 - from.0) / d * s, from.1 + (to.1 - from.1) / d * s), s)
}

/// The unit the form is: his health cap, armour and magic resistance; move speed 1 (it walks only as the hook moves
/// it), an attack of nothing that reaches nobody (league_lowhp's thrall).
pub fn form_spec(max_hp: usize, defence: usize, magic_resistance: usize) -> summon::Spec {
    summon::Spec {
        name: UNIT.to_string(),
        life: FORM_T + LIFE_SLACK,
        stat: StatV1 { attack: 0, magic_power: 0, hp: max_hp.max(1), defence, magic_resistance, move_speed: 1, hp_regen: 0,
                       stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: 0, attack: 0, range: 1, cooltime: 600, duration: 12, start_timing: 6,
                               cancelable: false, attack_type: AttackTypeV1::BaseAttack.code() },
    }
}

/// The form's guard for `ticks`: no damage, undying, through walls.
pub fn guard(ticks: usize) -> BuffV1 {
    let mut b = BuffV1::timed(GUARD, ticks.max(1));
    (b.damaged_reduce, b.undying, b.ignore_wall) = (100, true, true);
    b
}

/// This add-on's tag of simulation `n`, and the number in a buff name of it.
pub fn sim_tag(n: u64) -> String {
    format!("{SIM_TAG}{n}")
}

pub fn parse_tag(buff: &str) -> Option<u64> {
    buff.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())
}

fn at_input(at: Pt) -> InputTargetV1 {
    InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64)
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    summon::at_of(e)
}

// ===================== 每份模拟的编号 =====================

/// (seed, origin kind, match, set): the presim twins share it, their buildings tell them apart.
type Origin = (u64, u32, u64, u64);

static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
/// Each origin's numbers and the buildings that carry each.
static SIMS: LazyLock<Mutex<HashMap<Origin, Vec<(u64, Vec<usize>)>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
const SIMS_MOST: usize = 4096;

fn origin(sim: &StableSim<'_>) -> Origin {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index)
}

fn tag_on(sim: &StableSim<'_>, id: usize) -> Option<u64> {
    let e = sim.get_entity(id)?;
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find_map(|b| parse_tag(b.name()))
}

/// The living nexuses and the living towers.
fn buildings(sim: &StableSim<'_>) -> (Vec<usize>, Vec<usize>) {
    let (mut nexus, mut towers) = (Vec::new(), Vec::new());
    for e in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
        if !e.is_alive() {
            continue;
        }
        match e.kind() {
            Some(EntityKindV1::Nexus) => nexus.push(e.id()),
            Some(EntityKindV1::Tower) => towers.push(e.id()),
            None if e.is_tower() => towers.push(e.id()),
            _ => {}
        }
    }
    (nexus, towers)
}

fn remember(key: Origin, n: u64, carriers: Vec<usize>) {
    let mut sims = SIMS.lock().unwrap_or_else(|e| e.into_inner());
    if sims.len() >= SIMS_MOST && !sims.contains_key(&key) {
        sims.clear();
    }
    let list = sims.entry(key).or_default();
    list.retain(|(m, _)| *m != n);
    list.push((n, carriers));
    if list.len() > 32 {
        list.remove(0);
    }
}

/// This simulation's number: its nexuses' (or towers') `league_kogmaw_sim:<n>`. The numbers known for its origin are
/// looked for on their buildings first; else the buildings are read (a number forgotten here); with none there and
/// `hang`, a number is drawn and hung. Without `hang` (the match hook, every tick of every simulation) a match nothing of
/// ours ever numbered is left at once. 0: none.
pub fn sim_no(sim: &mut StableSim<'_>, hang: bool) -> u64 {
    let key = origin(sim);
    let known = SIMS.lock().unwrap_or_else(|e| e.into_inner()).get(&key).cloned();
    match &known {
        Some(known) => {
            for (n, carriers) in known.iter().rev() {
                if carriers.iter().any(|&a| tag_on(sim, a) == Some(*n)) {
                    return *n;
                }
            }
        }
        None if !hang => return 0,
        None => {}
    }
    let (nexus, towers) = buildings(sim);
    let all: Vec<usize> = nexus.iter().chain(&towers).copied().collect();
    if let Some(n) = all.iter().find_map(|&a| tag_on(sim, a)) {
        let carriers = all.iter().copied().filter(|&a| tag_on(sim, a) == Some(n)).collect();
        remember(key, n, carriers);
        return n;
    }
    if !hang || all.is_empty() {
        return 0;
    }
    let n = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
    let tag = sim_tag(n);
    for group in [&nexus, &towers] {
        for &a in group.iter() {
            sim.entity_remove_buff(a, &tag);
            sim.add_buff(a, &BuffV1::named(&tag));
        }
        let carriers: Vec<usize> = group.iter().copied().filter(|&a| tag_on(sim, a) == Some(n)).collect();
        if !carriers.is_empty() {
            remember(key, n, carriers);
            return n;
        }
    }
    0
}

// ===================== 他活着时记下的 =====================

/// What his passive read of him last, alive: by (simulation number, his entity).
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Life {
    pub team: usize,
    pub ad: usize,
    pub max_hp: usize,
    pub defence: usize,
    pub magic_resistance: usize,
    pub at: Pt,
    pub tick: usize,
    stamp: u64,
}

static STAMP: AtomicU64 = AtomicU64::new(1);
static LIVES: LazyLock<Mutex<HashMap<(u64, usize), Life>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// The last wake of each Kog'Maw: (simulation, his entity) -> (tick, stamp).
static WOKEN: LazyLock<Mutex<HashMap<(u64, usize), (usize, u64)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
const BOOK_MOST: usize = 2048;

fn stamp() -> u64 {
    STAMP.fetch_add(1, Ordering::Relaxed)
}

/// Drops the oldest half of a book past its size (the simulations long over are the oldest).
fn trim<K: Clone + Eq + std::hash::Hash, V>(book: &mut HashMap<K, V>, age: impl Fn(&V) -> u64) {
    if book.len() <= BOOK_MOST {
        return;
    }
    let mut ages: Vec<u64> = book.values().map(&age).collect();
    ages.sort_unstable();
    let cut = ages[ages.len() / 2];
    book.retain(|_, v| age(v) > cut);
}

fn read_life(sim: &StableSim<'_>, me: usize) -> Option<Life> {
    let e = sim.get_entity(me)?;
    let stat = e.stat();
    Some(Life { team: e.team(), ad: stat.attack, max_hp: e.hp().1, defence: stat.defence, magic_resistance: stat.magic_resistance,
                at: pos(&e), tick: sim.tick(), stamp: stamp() })
}

fn note_life(n: u64, me: usize, life: Life) {
    let mut book = LIVES.lock().unwrap_or_else(|e| e.into_inner());
    book.insert((n, me), life);
    trim(&mut book, |l| l.stamp);
}

pub fn life_of(n: u64, me: usize) -> Option<Life> {
    LIVES.lock().unwrap_or_else(|e| e.into_inner()).get(&(n, me)).copied()
}

// ===================== 被动 =====================

/// Icathian Surprise's record keeper (every Kog'Maw his own; a dead champion's passive does not run).
#[derive(Clone, Default)]
struct LifeWatch {
    me: usize,
    n: u64,
    /// The tick the simulation's number is read again (none yet: soon - the buildings come a few ticks into a match).
    next: usize,
}

impl LifeWatch {
    fn note(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        if now >= self.next || self.next > now + 600 {
            self.n = sim_no(sim, true);
            self.next = now + if self.n == 0 { 30 } else { 120 };
        }
        if let Some(life) = read_life(sim, me).filter(|_| sim.get_entity(me).is_some_and(|e| e.is_alive())) {
            note_life(self.n, me, life);
        }
    }
}

impl StablePassive for LifeWatch {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.next = 0;
        self.note(sim, me);
        if let Some(k) = tally(sim, "spawn") {
            let (team, ad) = sim.get_entity(me).map_or((0, 0), |e| (e.team(), e.stat().attack));
            wlog(format!("{} SPAWN #{k}: the add-on's Kog'Maw (player {player}, team {team}, attack {ad}), simulation number {}",
                         head(sim, me), self.n));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.me = me;
        self.note(sim, me);
    }

    // nothing at his death: the note of his last living tick is what the burst uses (a body read as it falls may have
    // lost what he wore)
}

// ===================== 形态 =====================

/// One void form, as the match hook keeps it.
#[derive(Clone, Debug)]
pub struct Form {
    /// The unit, which of this launch's forms (the log), the Kog'Maw (his old entity) and his team.
    pub id: usize,
    pub n: usize,
    pub kog: usize,
    pub team: usize,
    /// The tick it was spawned, its life asked for, where it woke (his body), his attack when he fell.
    pub born: usize,
    pub life: usize,
    pub wake: Pt,
    pub ad: usize,
    /// The ground every entity stood on at its spawn: it is never put outside.
    pub field: Option<(Pt, Pt)>,
    /// Looks before it read as a settled unit; then it walks (dressed).
    pub looks: usize,
    pub walking: bool,
    pub at: Pt,
    pub walked: f64,
    pub relaid: usize,
    pub summoner: usize,
    /// Its stat block as spawned; `engine_walks`: the host refused `entity_set_pos`, so its move speed became P_SPEED and
    /// the engine walks it at the champion it is taunted at.
    pub stat: StatV1,
    pub engine_walks: bool,
}

static FORMS: LazyLock<Mutex<HashMap<u64, (u64, Vec<Form>)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// Forms on the books in every simulation (the match hook does nothing while there are none).
static LIVE: AtomicUsize = AtomicUsize::new(0);
static FORM_N: AtomicUsize = AtomicUsize::new(0);
const SIMS_WITH_FORMS: usize = 256;

fn add_form(n: u64, f: Form) {
    let mut book = FORMS.lock().unwrap_or_else(|e| e.into_inner());
    let entry = book.entry(n).or_insert((0, Vec::new()));
    entry.0 = stamp();
    entry.1.push(f);
    LIVE.fetch_add(1, Ordering::Relaxed);
    if book.len() > SIMS_WITH_FORMS {
        // a simulation that ended with forms out: its forms are never stepped again
        let oldest = book.iter().min_by_key(|(_, v)| v.0).map(|(k, _)| *k);
        if let Some(k) = oldest {
            if let Some((_, v)) = book.remove(&k) {
                LIVE.fetch_sub(v.len().min(LIVE.load(Ordering::Relaxed)), Ordering::Relaxed);
            }
        }
    }
}

/// How many forms the book holds for simulation `n` (tests).
pub fn forms_of(n: u64) -> usize {
    FORMS.lock().unwrap_or_else(|e| e.into_inner()).get(&n).map_or(0, |v| v.1.len())
}

/// The enemy champion nearest `at` for `team`: alive, targetable. (id, where, radius, name, distance)
fn nearest_champion(sim: &StableSim<'_>, team: usize, at: Pt, within: f64) -> Option<(usize, Pt, usize, String, f64)> {
    let mut best: Option<(usize, Pt, usize, String, f64)> = None;
    for i in 0..sim.champion_count() {
        let Some(e) = sim.get_entity(sim.champion_id_at(i)) else { continue };
        if e.team() == team || !e.is_alive() || !e.is_targetable() || !e.is_champion() {
            continue;
        }
        let p = pos(&e);
        let d = dist(p, at);
        if d > within {
            continue;
        }
        if best.as_ref().is_none_or(|b| d < b.4 || (d == b.4 && e.id() < b.0)) {
            best = Some((e.id(), p, e.radius(), e.name().unwrap_or_default(), d));
        }
    }
    best
}

/// Whose name a burst's damage and pictures go under: his old entity while it is gone or still his body (never another
/// unit that got the id), else the form.
fn his_id_usable(sim: &StableSim<'_>, kog: usize, team: usize) -> bool {
    match sim.get_entity(kog) {
        None => true,
        Some(e) => e.team() == team && e.name().is_some_and(|n| n == HERO),
    }
}

/// The damage under his name, or the form's when the host refuses his: "his" / "the form's" / "refused".
fn deal(sim: &mut StableSim<'_>, kog: usize, form: Option<usize>, team: usize, target: usize, amount: usize) -> &'static str {
    if his_id_usable(sim, kog, team) && sim.deal_damage_typed(kog, target, amount, DamageTypeV1::Fixed, AttackTypeV1::Skill) {
        return "his";
    }
    match form {
        Some(f) if sim.deal_damage_typed(f, target, amount, DamageTypeV1::Fixed, AttackTypeV1::Skill) => "the form's",
        _ => "refused",
    }
}

/// A picture under his name (the data's own wake light plays under his gone entity and is drawn), or the form's when the
/// host refuses it.
fn picture(sim: &mut StableSim<'_>, name: &str, kog: usize, form: Option<usize>, team: usize, input: &InputTargetV1) -> bool {
    if his_id_usable(sim, kog, team) && sim.play_view_effect(name, kog, input, 0, 0, 0) {
        return true;
    }
    form.is_some_and(|f| sim.play_view_effect(name, f, input, 0, 0, 0))
}

fn sound(sim: &mut StableSim<'_>, name: &str, kog: usize, form: Option<usize>, team: usize, input: &InputTargetV1) -> bool {
    if his_id_usable(sim, kog, team) && sim.play_sfx(name, kog, input) {
        return true;
    }
    form.is_some_and(|f| sim.play_sfx(name, f, input))
}

/// What a burst did: who was hit and for how much, under whose name.
#[derive(Clone, Debug, Default)]
pub struct Blast {
    pub amount: usize,
    pub hit: Vec<(usize, String)>,
    pub by: Vec<&'static str>,
    pub picture: bool,
}

/// The burst at `at` for Kog'Maw `kog` of `team` (attack `ad`): every enemy but towers, nexuses and void forms within
/// p_r + its radius takes the true damage and the hit picture; the burst's own picture there (`big`: the new one, else
/// the comet's p_boom) and its sound.
fn blast(sim: &mut StableSim<'_>, kog: usize, form: Option<usize>, team: usize, ad: usize, at: Pt, big: bool) -> Blast {
    let amount = burst_damage(ad);
    let victims: Vec<(usize, String)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && summon::hittable(u))
        .filter(|u| u.name().is_none_or(|n| n != UNIT))
        .filter(|u| dist(pos(u), at) <= reach(u.radius()))
        .map(|u| (u.id(), u.name().unwrap_or_default()))
        .collect();
    let spot = at_input(at);
    let pic = picture(sim, if big { VOID_VIEW } else { BOOM }, kog, form, team, &spot);
    sound(sim, BOOM, kog, form, team, &spot);
    let mut out = Blast { amount, picture: pic, ..Blast::default() };
    for (id, name) in victims {
        let by = deal(sim, kog, form, team, id, amount);
        picture(sim, HIT_VIEW, kog, form, team, &InputTargetV1::target(id));
        out.hit.push((id, name));
        out.by.push(by);
    }
    out
}

fn blast_text(b: &Blast) -> String {
    if b.hit.is_empty() {
        return "nobody within reach".to_string();
    }
    let mut by: Vec<&str> = b.by.clone();
    by.dedup();
    format!("{} hit for {} true damage each ({}): {}", b.hit.len(), b.amount, by.join(" / "),
            b.hit.iter().map(|(id, n)| format!("{n}#{id}")).collect::<Vec<_>>().join(", "))
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Why {
    /// Within reach of an enemy champion.
    Reached(usize),
    /// Its 4 s are up.
    Time,
    /// The unit was gone before it burst.
    Gone,
}

fn burst(sim: &mut StableSim<'_>, f: &Form, why: Why) {
    let now = sim.tick();
    let unit = (why != Why::Gone).then_some(f.id);
    let b = blast(sim, f.kog, unit, f.team, f.ad, f.at, true);
    let left = (f.born + f.life + 1).saturating_sub(now).max(1);
    let banished = why != Why::Gone && sim.entity_banish(f.id, f.id, left, "", "");
    if why != Why::Gone {
        sim.entity_remove_buff(f.id, GO);
    }
    if let Some(k) = tally(sim, "burst") {
        let age = now.saturating_sub(f.born);
        let what = match why {
            Why::Reached(t) => format!("REACHED {}", who(sim, t)),
            Why::Time => format!("TIME ({FORM_T} ticks up)"),
            Why::Gone => "GONE (the unit vanished before its burst)".to_string(),
        };
        wlog(format!(
            "{} VOID BURST #{k} form {} of Kog'Maw #{} {what} after {age} ticks ({:.2} s) at {}, {:.0} from where he fell (walked {:.0}); \
             {}; the burst picture {}; the form banished for its last {left} ticks: {}",
            head(sim, f.id), f.n, f.kog, age as f64 / 60.0, summon::pt(f.at), dist(f.at, f.wake), f.walked, blast_text(&b),
            if b.picture { "played" } else { "REFUSED" },
            if why == Why::Gone { "-".to_string() } else if banished { "yes".to_string() } else { "REFUSED".to_string() }));
    }
}

/// The fallback: today's comet from the wake at the nearest enemy champion within P_SEEK (`spawn_projectile` of the
/// copy's p_form, its hit `:burst`); refused, the burst on that champion at once; none near, nothing (the main pack's
/// RandomTarget found none either).
fn comet(sim: &mut StableSim<'_>, kog: usize, team: usize, ad: usize, wake: Pt, why: &str) {
    let Some((target, at, _, name, d)) = nearest_champion(sim, team, wake, P_SEEK as f64) else {
        if let Some(k) = tally(sim, "fallback") {
            wlog(format!("{} VOID FALLBACK #{k} ({why}): no enemy champion within {P_SEEK} of {} - nothing (the main pack's comet \
                          found none either)", head(sim, kog), summon::pt(wake)));
        }
        return;
    };
    let spec = comet_spec(kog, team, wake, target);
    let flown = sim.spawn_projectile(FORM_PROJ, BURST_FX, &spec);
    let b = if flown { None } else { Some(blast(sim, kog, None, team, ad, at, false)) };
    if let Some(k) = tally(sim, "fallback") {
        wlog(format!(
            "{} VOID FALLBACK #{k} ({why}): the comet as before at {name}#{target} {d:.0} away from {}: {}",
            head(sim, kog), summon::pt(wake),
            match &b {
                None => "spawn_projectile took it (its hit: league_kogmaw:burst)".to_string(),
                Some(b) => format!("spawn_projectile REFUSED - the burst on {name} at once: {}", blast_text(b)),
            }));
    }
}

/// The comet: homing on `target` from `from` at the form's pace, its hit the add-on's `:burst`.
pub fn comet_spec(kog: usize, team: usize, from: Pt, target: usize) -> ProjectileSpawnV1 {
    ProjectileSpawnV1 {
        caster_id: kog,
        team,
        x: from.0.round().max(0.0) as u64,
        y: from.1.round().max(0.0) as u64,
        radius: 1_000,
        speed: P_SPEED as u64,
        move_kind: ProjectileMoveKindV1::Target.code(),
        target_id: target,
        target_x: 0,
        target_y: 0,
        penetrate: false,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::EnemyChampion.code(),
    }
}

// ===================== 原生效果 =====================

/// `league_kogmaw:void` - the watch found him gone (the copy's `wake`, in place of the comet): his void form at the wake.
struct VoidFx;

impl StableEffectType for VoidFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, kog: usize, input: InputTargetV1) {
        wake(sim, kog, input);
    }
}

fn wake(sim: &mut StableSim<'_>, kog: usize, input: InputTargetV1) {
    let now = sim.tick();
    let n = sim_no(sim, true);
    // his numbers: his body when he still lives in it (a revive's untargetable lying), else what his passive noted while
    // he lived (a fallen body that still reads is not trusted: what he wore may be gone from it)
    let body = sim.get_entity(kog).filter(|e| e.is_alive() && e.name().is_some_and(|nm| nm == HERO)).is_some();
    let life = if body { read_life(sim, kog) } else { life_of(n, kog) };
    let at = match InputTargetKindV1::from_code(input.kind) {
        Some(InputTargetKindV1::Pos) => Some((input.x as f64, input.y as f64)),
        Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|e| pos(&e)),
        _ => None,
    }
    .or(life.map(|l| l.at));
    let Some((life, at)) = life.zip(at) else {
        if let Some(k) = tally(sim, "lost") {
            wlog(format!("{} VOID LOST #{k}: the watch woke for Kog'Maw #{kog}, but this simulation (number {n}) has no note of him \
                          (his passive never ran here?) - no form", head(sim, kog)));
        }
        return;
    };
    {
        let mut woken = WOKEN.lock().unwrap_or_else(|e| e.into_inner());
        if let Some(&(t, _)) = woken.get(&(n, kog)) {
            if now >= t && now - t < WAKE_GAP {
                drop(woken);
                if let Some(k) = tally(sim, "twice") {
                    wlog(format!("{} VOID TWICE #{k}: the watch woke again {} ticks after the last wake of Kog'Maw #{kog} - the same \
                                  death, one form", head(sim, kog), now - t));
                }
                return;
            }
        }
        woken.insert((n, kog), (now, stamp()));
        trim(&mut woken, |v| v.1);
    }
    let state = if body {
        "lying untargetable (a revive)"
    } else if sim.get_entity(kog).is_some() {
        "his fallen body still reads"
    } else {
        "his entity gone"
    };
    if KNOBS.off {
        comet(sim, kog, life.team, life.ad, at, "unit=off in the test knobs");
        return;
    }
    let spec = form_spec(life.max_hp, life.defence, life.magic_resistance).with(&KNOBS);
    let field = summon::field(sim);
    let spot = summon::inside(field, at);
    // the summoner: his old entity (gone or still his body); a host that wants a living one, his nearest living ally
    let mut tried = Vec::new();
    let mut made = None;
    let ally = (0..sim.champion_count()).filter_map(|i| sim.get_entity(sim.champion_id_at(i)))
        .filter(|e| e.team() == life.team && e.is_alive() && e.id() != kog)
        .min_by(|a, b| dist(pos(a), spot).total_cmp(&dist(pos(b), spot)))
        .map(|e| e.id());
    for s in [his_id_usable(sim, kog, life.team).then_some(kog), ally].into_iter().flatten() {
        tried.push(s);
        if let Some(id) = summon::spawn(sim, s, life.team, spot, &spec) {
            made = Some((id, s));
            break;
        }
    }
    let Some((id, summoner)) = made else {
        let why = if tried.is_empty() {
            "no summoner to name (his id is another unit's now and no ally lives)".to_string()
        } else {
            format!("spawn_unit gave no unit for '{}' (summoners tried: {:?})", spec.name, tried)
        };
        comet(sim, kog, life.team, life.ad, at, &why);
        return;
    };
    // the guard from its first tick too (what is laid before it settles may not hold: the look lays it again)
    sim.add_buff(id, &guard(spec.life + 5));
    let fnum = FORM_N.fetch_add(1, Ordering::Relaxed) + 1;
    add_form(n, Form { id, n: fnum, kog, team: life.team, born: now, life: spec.life, wake: at, ad: life.ad, field, looks: 0,
                       walking: false, at: spot, walked: 0.0, relaid: 0, summoner, stat: spec.stat, engine_walks: false });
    if let Some(k) = tally(sim, "spawn void") {
        wlog(format!(
            "{} VOID SPAWN #{k}: form {fnum} of Kog'Maw #{kog} ({state}, team {}) woke at {}: unit #{id} (summoner #{summoner}{}) {}; his \
             attack {} (noted at t={}) -> the burst {} true damage within {P_R} + a unit's radius, at the nearest enemy champion \
             {P_SPEED} a tick for {FORM_T} ticks at most; simulation number {n}",
            head(sim, kog), life.team, summon::pt(spot), if summoner == kog { ", his own id" } else { ", an ally: his own refused" },
            spec.shown(), life.ad, life.tick, burst_damage(life.ad)));
    }
}

/// `league_kogmaw:burst` - the fallback comet's hit (its input: the champion it reached).
struct BurstFx;

impl StableEffectType for BurstFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, kog: usize, input: InputTargetV1) {
        let at = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|e| pos(&e)),
            Some(InputTargetKindV1::Pos) => Some((input.x as f64, input.y as f64)),
            _ => None,
        };
        let n = sim_no(sim, true);
        let Some((life, at)) = life_of(n, kog).zip(at) else { return };
        let b = blast(sim, kog, None, life.team, life.ad, at, false);
        if let Some(k) = tally(sim, "comet hit") {
            wlog(format!("{} VOID COMET HIT #{k}: Kog'Maw #{kog}'s comet burst at {}: {}", head(sim, kog), summon::pt(at),
                         blast_text(&b)));
        }
    }
}

// ===================== 比赛钩子 =====================

/// Steps every void form of a simulation each tick (a dead champion's passive does not run; this does).
pub struct Forms;

impl StableMatchHook for Forms {
    fn on_match_tick(&self, sim: &mut StableSim<'_>, _: u64) {
        step_forms(sim);
    }
}

/// This tick of the forms in `sim`.
pub fn step_forms(sim: &mut StableSim<'_>) {
    if LIVE.load(Ordering::Relaxed) == 0 {
        return;
    }
    let n = sim_no(sim, false);
    if n == 0 {
        return;
    }
    let Some((_, mine)) = FORMS.lock().unwrap_or_else(|e| e.into_inner()).remove(&n) else { return };
    let before = mine.len();
    let mut keep = Vec::with_capacity(before);
    for mut f in mine {
        if step(sim, &mut f) {
            keep.push(f);
        }
    }
    let gone = before - keep.len();
    if gone > 0 {
        LIVE.fetch_sub(gone.min(LIVE.load(Ordering::Relaxed)), Ordering::Relaxed);
    }
    if !keep.is_empty() {
        let mut book = FORMS.lock().unwrap_or_else(|e| e.into_inner());
        let entry = book.entry(n).or_insert((0, Vec::new()));
        entry.0 = stamp();
        // a form spawned while this one was stepped (the same simulation cannot: it runs on one thread at a time)
        entry.1.splice(0..0, keep);
    }
}

/// Is the entity under the form's id the form, alive?
fn read_form(sim: &StableSim<'_>, f: &Form) -> Option<(Pt, usize, bool)> {
    let e = sim.get_entity(f.id)?;
    let ours = e.is_alive() && e.team() == f.team && e.name().is_some_and(|n| n == UNIT || KNOBS.name.as_deref() == Some(n.as_str()));
    ours.then(|| (pos(&e), e.hp().1, summon::has_buff(&e, GUARD)))
}

/// One form's tick: -> keep it on the books.
fn step(sim: &mut StableSim<'_>, f: &mut Form) -> bool {
    let now = sim.tick();
    if !f.walking {
        f.looks += 1;
        match read_form(sim, f) {
            Some((at, max, _)) if max > 1 || f.looks >= LOOKS => {
                f.walking = true;
                f.at = at;
                sim.entity_remove_buff(f.id, GUARD);
                sim.add_buff(f.id, &guard((f.born + f.life + 5).saturating_sub(now)));
                if let Some(k) = tally(sim, "look") {
                    let line = summon::Unit::look(sim, f.id, f.n, f.born, f.life, f.team, 0).map(|(_, l)| l).unwrap_or_default();
                    let on = sim.get_entity(f.id).is_some_and(|e| summon::has_buff(&e, GUARD));
                    wlog(format!("{} VOID LOOK #{k} form {}: {line}{}; its guard (no damage, undying, through walls) {}", head(sim, f.id),
                                 f.n, if max > 1 { String::new() } else { format!(" (its health cap still reads {max} after {} looks)", f.looks) },
                                 if on { "is on it" } else { "is NOT on it" }));
                }
            }
            Some(_) => return true,
            None if f.looks >= LOOKS => {
                comet(sim, f.kog, f.team, f.ad, f.wake, &format!("the unit #{} never read as a unit in {LOOKS} ticks", f.id));
                return false;
            }
            None => return true,
        }
    }
    let Some((at, _, guarded)) = read_form(sim, f) else {
        burst(sim, f, Why::Gone);
        return false;
    };
    if f.engine_walks {
        f.walked += dist(f.at, at);
    }
    f.at = at;
    if !guarded {
        f.relaid += 1;
        sim.add_buff(f.id, &guard((f.born + f.life + 5).saturating_sub(now)));
        if let Some(k) = tally(sim, "guard") {
            wlog(format!("{} VOID GUARD #{k} form {}: its guard was gone - laid again ({} times)", head(sim, f.id), f.n, f.relaid));
        }
    }
    let age = now.saturating_sub(f.born);
    let prey = nearest_champion(sim, f.team, f.at, f64::MAX);
    if let Some((t, tp, r, _, _)) = &prey {
        if dist(f.at, *tp) <= reach(*r) {
            burst(sim, f, Why::Reached(*t));
            return false;
        }
    }
    if age >= FORM_T {
        burst(sim, f, Why::Time);
        return false;
    }
    let Some((t, tp, r, name, _)) = prey else {
        sim.entity_remove_buff(f.id, GO);
        if age % STEP_EVERY == 0 && (shown(sim) || age == 0) {
            if let Some(k) = tally(sim, "step") {
                wlog(format!("{} VOID STEP #{k} form {}: {age} of {FORM_T} ticks at {}, {:.0} from where he fell - no enemy champion to \
                              chase, it waits", head(sim, f.id), f.n, summon::pt(f.at), dist(f.at, f.wake)));
            }
        }
        return true;
    };
    let (to, moved) = step_toward(f.at, tp, P_SPEED as f64);
    let to = summon::inside(f.field, to);
    let moved_to = !f.engine_walks && sim.entity_set_pos(f.id, to.0.round().max(0.0) as u64, to.1.round().max(0.0) as u64);
    if moved_to {
        f.walked += moved;
        f.at = to;
    } else if !f.engine_walks {
        // a host that will not move a unit: its own pace, and the engine walks it at the champion it is taunted at below
        let stat = StatV1 { move_speed: P_SPEED, ..f.stat };
        f.engine_walks = sim.entity_set_base_stat(f.id, &stat);
        if let Some(k) = tally(sim, "walk") {
            wlog(format!("{} VOID WALK #{k} form {}: entity_set_pos REFUSED - {}", head(sim, f.id), f.n,
                         if f.engine_walks { format!("its move speed is {P_SPEED} now: the engine walks it, taunted at {name}#{t}") }
                         else { "entity_set_base_stat refused too: it stands until its burst".to_string() }));
        }
    }
    // walking: the flag for the display hook; the engine's own unit AI turned at the same champion
    let go = BuffV1::timed(GO, 2);
    if sim.entity_stack_buff(f.id, &go, 1, true) == 0 {
        sim.entity_remove_buff(f.id, GO);
        sim.add_buff(f.id, &go);
    }
    sim.entity_clear_cc(f.id);
    let mut taunt = CcV1::of_kind(CcKindV1::Taunt, 2);
    taunt.target = t;
    sim.apply_cc(f.id, &taunt);
    let d = dist(f.at, tp);
    if age % STEP_EVERY == 0 {
        if let Some(k) = tally(sim, "step") {
            wlog(format!("{} VOID STEP #{k} form {}: {age} of {FORM_T} ticks at {}, {:.0} from where he fell (walked {:.0}); chasing \
                          {name}#{t} {d:.0} away (it bursts within {:.0}){}", head(sim, f.id), f.n, summon::pt(f.at),
                         dist(f.at, f.wake), f.walked, reach(r),
                         if moved_to { "" } else if f.engine_walks { " (the engine walks it)" } else { " - entity_set_pos REFUSED" }));
        }
    }
    if d <= reach(r) {
        burst(sim, f, Why::Reached(t));
        return false;
    }
    true
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one; its
/// match hook is the bundle's, which calls [`Forms`]).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Kog'Maw: Icathian Surprise as in League - his body a void form that runs at the nearest enemy champion \
         and bursts) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "VOID: the form is a unit ('{}', spawn_unit) - {}; it runs {P_SPEED} a tick at the nearest enemy champion and bursts within \
         {P_R} + its radius or after {FORM_T} ticks: {P_DMG} + {P_RATIO}% of his attack as true damage to every enemy within {P_R} \
         + its radius; no unit: the comet as before. Test knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(UNIT),
        if KNOBS.off { "OFF by the test knobs: the comet as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(),
        KNOBS.shown()
    ));
    view::install_once();
    module.add_native_effect(VOID_FX, VoidFx);
    module.add_native_effect(BURST_FX, BurstFx);
    module.add_native_passive(PASSIVE, LifeWatch::default());
    module.set_match_hook(Forms);
    host.log(LogLevel::Info, "league_kogmaw loaded (Icathian Surprise: his void form runs at the nearest enemy champion and bursts).");
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
#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

#[cfg(test)]
mod tests;
