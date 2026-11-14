//! 悟空附加包（用户 2026-10-18：「技能方案按 A 做（带扩展包 league_wukong）」）。主包保持纯数据；`mod.override_info` 把主包的
//! 悟空换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_wukong.py 的 `native=1` 生成：技能一字不改，被动换成本包的
//! `league_wukong:stone`，金刚不坏的五层不再带数据里的固定回血），本包补数据做不到的三件事：
//!
//! - **按最大生命回血**（英雄联盟的金刚不坏）：数据读不到生命，主包每层每秒回固定值；本包每 `every` tick 按他身上金刚不坏的层数
//!   （主包的 `league_wukong_s_1` ~ `s_5`）回复最大生命：每 5 秒 `pct`/100 %（英雄联盟 0.35%）×（1 + 层数），叠满 5 层是 2.1%。
//!   零头攒着下次一起回，不会因为取整丢掉。
//! - **分身画出来**（0.1.2，用户 2026-10-29：「猴子开大还是没分身啊」「现在分身都看不见」）：主包的分身是锚点（射程 1 的
//!   弹道）`end_effects` 里一格一格放的画面，这种画面游戏里从来不显示（锤石 R 的箱子、永恩留下的身体同一个毛病），所以玩家
//!   从没见过分身。副本里 W 施放那一刻调 `league_wukong:clone`，把分身站的地方写成他身上的一个 buff（`league_wukong_clone:…`），
//!   被动下一拍读走（每份模拟各记各的，不用全局表，两份预模拟同时跑时不会串）；伤害照旧是数据锚点的，画面由本包每 `w_slot`
//!   tick 在那里放一次：他在转（`r_on`，英雄联盟里有分身时分身也开大）放 `w_clone_spin`，每 `w_period` 一次出手的那格放
//!   `w_clone_atk`，其余 `w_clone`。他死了、`w_live` 没了（数据的分身散了）、`w_t` 到了，就不再画。
//! - **替 AI 按 W**（0.1.2，「你确定会放分身吗现在 我怎么一次没见过」→「加上」，src/trickster.rs）：游戏的 AI 几乎总先按 E，
//!   W 一局只放几次；W 好了、射程内有敌方英雄时替他按（英雄联盟里 W 开团、接大招）。
//! - **分身是真的单位**（0.2.0，2026-11-14；用户看了和英雄联盟不一样的地方的清单：「全改吧」，其中一条是「召唤物不会走、不会打、
//!   打不掉」，之后「召唤物的全做啊」）。英雄联盟的真假猴王：分身留在他施放的地方 4 秒，不会走，生命是他当时的生命，敌人
//!   打得到、打得死，自己普攻，他开大时也跟着转。稳定 mod API 的 `spawn_unit`（公用部分是萨科附加包的 `summon.rs`，这里用
//!   `#[path]` 引进来）：W 施放那一刻的 `league_wukong:clone` 照旧记下分身站的地方，再在那里生成一个叫 `league_wukong` 的单位
//!   （[`clone_spec`]：按他自己的图画；移速 1，站着不动；攻击、防御照他此刻的，生命上限照他的、当前生命设成他当时的；每
//!   `W_COOL` tick 打 `W_REACH` 内的敌人一下，每下 `W_HIT_AD`% 攻击力——都是主包分身的数字，make_override.py 对照检查），活
//!   `W_LIFE` tick；成功了给他挂 `W_UNIT`——副本里分身那块地的每一下、每一格的转棒都先看它：有，就不放数据的分身（AI 估伤害
//!   时没有这个标记，看到的还是原来那一支）。他转大招（`r_on`）时被动让单位也转：给它强制动作 `spin`，每 `SPIN_EVERY` tick
//!   在它身边 `SPIN_R` 内造成 `SPIN_HIT` + `SPIN_HIT_AD`% 攻击力的物理伤害，每次转的第一下把还没被击飞的敌人击飞 `SPIN_UP`
//!   tick（英雄联盟：已经被他击飞的人分身不再击飞）。
//! - 退路：宿主没有这个接口、生成失败、给的 id 读不成单位、单位 6 tick 内就没了、或者日志旁边的 `league_wukong.cfg` 写了
//!   `unit=off`——标记不挂（或去掉），数据的分身照旧打、本包照旧在那里画分身的三张图。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_wukong.log`，每次启动游戏重写，上一次的留在 .prev.log：`REGEN`
//! （回了多少、几层）、`W PRESS`（替他按的 W）、`CLONE`（分身站在哪）、`CLONE SPINS`（他开大时分身跟着转）、`CLONE GONE`；
//! 分身是单位时 `UNIT` 开头的一整套（`UNIT SPAWN` / `LOOK` / `DRESS` / 每秒一行 / `SPIN` / `PULSE` / `OVER` / `WAKE`，退路是
//! `UNIT SPAWN FAILED` / `UNIT LOST` / `UNIT OFF`）。预模拟限了条数，你看的那场每条都记。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod trickster;

// the shared part of the summons (萨科附加包的 summon.rs); in the bundle not every item of it is used here
#[allow(dead_code)]
#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

const ID: &str = "league_wukong";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_wukong") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 金刚不坏的层（主包数据：打中英雄时叠，最多 5 层，每层一个名字）。
pub const STACKS: [&str; 5] =
    ["league_wukong_s_1", "league_wukong_s_2", "league_wukong_s_3", "league_wukong_s_4", "league_wukong_s_5"];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_WUKONG_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_wukong.log");
        }
    }
    PathBuf::from("league_wukong.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

/// The test knobs (`league_wukong.cfg` beside the log, summon.rs), read once.
static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

pub(crate) fn wlog(msg: impl AsRef<str>) {
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

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn bump(kind: &'static str) -> usize {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    *n
}

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let n = bump(kind);
    (n <= LOG_FIRST || n % LOG_EVERY == 0).then_some(n)
}

/// The match you watch (the view, a spectated match, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

/// Like `counted`, but every one when `shown` (the match you watch): the presims stay capped.
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let n = bump(kind);
    (shown || n <= LOG_FIRST || n % LOG_EVERY == 0).then_some(n)
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 每 5 秒回复最大生命的万分比，每有一层再加一份（英雄联盟 0.35% = 35）。
    pub pct: usize,
    /// 每多少 tick 回一次（30 = 半秒，英雄联盟的回血节奏）。
    pub every: usize,
    /// 分身：活多久、一格画面多少 tick、多久出手一次（主包的 w_t、w_slot、w_period）。
    pub w_t: usize,
    pub w_slot: usize,
    pub w_period: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { pct: 35, every: 30, w_t: 240, w_slot: 20, w_period: 60 }
    }
}

/// `{"pct":35,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "pct" => p.pct = v,
            "every" => p.every = v.max(1),
            "w_t" => p.w_t = v,
            "w_slot" => p.w_slot = v.max(1),
            "w_period" => p.w_period = v.max(1),
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 一次（`every` tick）该回的生命，按百万分之一记：最大生命 x pct/10000 x (1 + 层数) x every / 300。
/// 返回 (整数部分, 新的零头)，零头留到下一次。
pub fn regen_step(p: &Params, max_hp: usize, stacks: usize, carry: u64) -> (usize, u64) {
    let micro = max_hp as u64 * p.pct as u64 * (1 + stacks as u64) * p.every as u64 * 1_000_000 / (10_000 * 300) + carry;
    ((micro / 1_000_000) as usize, micro % 1_000_000)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 他身上金刚不坏有几层（最高一层还在就是几层：低层总比高层留得久）。
fn stacks(sim: &StableSim<'_>, id: usize) -> usize {
    (0..STACKS.len()).rev().find(|&k| has_buff(sim, id, STACKS[k])).map_or(0, |k| k + 1)
}

// ===================== 分身（W）：本包画 =====================

/// 交接 buff 的前缀：`league_wukong_clone:<x>:<y>:<tick>`（W 施放那一刻他站的地方、那一拍）。
const MARK: &str = "league_wukong_clone:";
/// 数据的分身还在（W 施放时挂上，`w_t` tick；他死了就没了）、他在转大招。
const W_LIVE: &str = "league_wukong_w_live";
const R_ON: &str = "league_wukong_r_on";
/// 数据锚点下一拍落下、第 k 格再过 k * w_slot + 1 tick：第一格在施放后 2 tick（SDK 模拟里量的）。
pub const FIRST_SLOT: usize = 2;

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一个分身：站哪、哪拍散、下一格画面在哪拍、第几格、上一格在不在转（日志用）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Decoy {
    pub at: Pt,
    pub until: usize,
    pub next_slot: usize,
    pub slot: usize,
    pub spinning: bool,
}

impl Decoy {
    pub fn new(at: Pt, cast: usize, p: &Params) -> Decoy {
        Decoy { at, until: cast + p.w_t, next_slot: cast + FIRST_SLOT, slot: 0, spinning: false }
    }
}

/// 交接 buff 的名字。
pub fn mark(at: Pt, tick: usize) -> String {
    format!("{MARK}{:.0}:{:.0}:{tick}", at.0, at.1)
}

/// 交接 buff -> (位置, 施放的那拍)。
pub fn read_mark(name: &str) -> Option<(Pt, usize)> {
    let mut it = name.strip_prefix(MARK)?.split(':');
    let x = it.next()?.parse::<f64>().ok()?;
    let y = it.next()?.parse::<f64>().ok()?;
    let t = it.next()?.parse::<usize>().ok()?;
    Some(((x, y), t))
}

/// 第 k 格放哪张（主包的排法）：他在转就是转的；每 `w_period` 一次出手的那格是出手的；其余站着的。
pub fn slot_pic(p: &Params, k: usize, spinning: bool) -> &'static str {
    if spinning {
        "w_clone_spin"
    } else if k % (p.w_period / p.w_slot).max(1) == 0 {
        "w_clone_atk"
    } else {
        "w_clone"
    }
}

fn pos_input(p: Pt) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

// ===================== 分身（W）：真的单位（0.2.0）——数字是主包的，make_override.py 对照主包检查 =====================

/// The clone's unit name: his own id, so the game draws it from his own sheet (league.dll's dense frames and his size
/// are keyed by the name - to be seen in game).
pub const UNIT_NAME: &str = "league_wukong";
/// On him while his clone is a unit: the copy's data reads it in the clone's zone and spin slots and plays neither.
pub const W_UNIT: &str = "league_wukong_w_unit";
/// The handoff from `league_wukong:clone` to the passive: `<W_UID>:<unit id>` on him for a few ticks.
pub const W_UID: &str = "league_wukong_w_uid";
/// The clone's time: the main pack's w_t (League's 4 s).
pub const W_LIFE: usize = 240;
/// Each hit: `W_HIT` + `W_HIT_AD` % of its attack (his, at the cast; the main pack's strike w_ratio - League's 40-60 %),
/// every `W_COOL` ticks (w_period: once a second, his own attack interval) within `W_REACH` (the strike's w_rad); the
/// action `W_ACT` ticks long (his attack's duration), the hit landing at `W_LANDS` (his plain swing's).
pub const W_HIT: usize = 0;
pub const W_HIT_AD: usize = 50;
pub const W_COOL: usize = 60;
pub const W_REACH: usize = 30_000;
pub const W_ACT: usize = 26;
pub const W_LANDS: usize = 11;
/// It does not walk (League's clone is static; the main pack's stands at the anchor): a move speed of 1, never 0
/// (summon.rs's `still`: the engine might divide by it).
pub const W_SPEED: usize = 1;
/// While he spins (R: `r_on` on him) the unit spins too: his `spin` forced on it for `SPIN_T` (r_t), and every
/// `SPIN_EVERY` ticks (w_slot) a pulse round it: `SPIN_HIT` + `SPIN_HIT_AD` % of his attack (r_dmg / r_ratio at w_spin %),
/// physical, to every enemy but towers within `SPIN_R` (r_rad); the first pulse of a spin knocks up `SPIN_UP` ticks (r_up)
/// those not in the air already (League: "won't knock up enemies if they were already knocked up by Wukong").
pub const SPIN_T: usize = 120;
pub const SPIN_EVERY: usize = 20;
pub const SPIN_HIT: usize = 5;
pub const SPIN_HIT_AD: usize = 17;
pub const SPIN_R: f64 = 28_000.0;
pub const SPIN_UP: u64 = 36;
pub const SPIN_ANIM: &str = "spin";
pub const SPIN_VIEW: &str = "league_wukong_r_hit";
/// Ticks the flag outlasts the clone's time; ticks the handoff stays; looks a handed-over id may take to read as a unit.
const FLAG_MORE: usize = 30;
const UID_TICKS: usize = 6;
const LOOK_TRIES: usize = 5;
/// A unit gone within this many ticks was never really there: the flag goes, the data's clone plays and is drawn.
pub const LOST_AGE: usize = 6;

/// The clone from his numbers at the cast (`stat`, his health cap `max_hp`): his attack, ability power and defences, his
/// health cap (the passive sets its health to his own then), a move speed of 1, his attack's length and timing, each hit
/// `W_HIT` + `W_HIT_AD` % of that attack every `W_COOL` ticks within `W_REACH`. No crits, no regeneration.
pub fn clone_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    summon::Spec {
        name: UNIT_NAME.to_string(),
        life: W_LIFE,
        stat: StatV1 {
            attack: stat.attack,
            magic_power: stat.magic_power,
            hp: max_hp.max(1),
            defence: stat.defence,
            magic_resistance: stat.magic_resistance,
            move_speed: W_SPEED,
            hp_regen: 0,
            stack: 0,
            crit_chance: 0,
        },
        attack: UnitAttackV1 {
            attack_ratio: W_HIT_AD,
            attack: W_HIT,
            range: W_REACH,
            cooltime: W_COOL,
            duration: W_ACT,
            start_timing: W_LANDS,
            cancelable: false,
            attack_type: AttackTypeV1::BaseAttack.code(),
        },
    }
}

/// One pulse of the clone's spin before armour, from his attack.
pub fn spin_damage(attack: usize) -> usize {
    SPIN_HIT + attack * SPIN_HIT_AD / 100
}

/// W 施放（`league_wukong:clone`，在他冲出去之前）：把他站的地方写在他身上，被动下一拍读走。0.1.4：一个短时 buff（交接位置的
/// 附加包都这么做：奥恩的柱子、阿克尚的绳子），日志 `MARK`——2026-10-30 的两次启动 W 放了，却一次 `CLONE` 都没有。
/// 0.2.0：再在那里生成分身这个单位；成功了给他挂 `W_UNIT`（副本的数据在下一拍才第一次读它）和交接 id 的短 buff，被动接手，
/// 记下的地方只留着当退路（单位读不成、很快就没了，就照旧画在那里）。
struct CloneMark;

/// 交接 buff 留多久（被动下一拍就读走）。
const MARK_T: usize = 30;

impl StableEffectType for CloneMark {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _input: InputTargetV1) {
        let Some((at, team, stat, max)) =
            sim.get_entity(me).map(|e| ((e.pos().0 as f64, e.pos().1 as f64), e.team(), e.stat(), e.hp().1))
        else {
            return;
        };
        let name = mark(at, sim.tick());
        sim.add_buff(me, &BuffV1::timed(&name, MARK_T));
        if let Some(k) = tally(sim, "mark") {
            wlog(format!("{} MARK #{k}: W cast at ({:.0}, {:.0})", head(sim, me), at.0, at.1));
        }
        if KNOBS.off {
            if let Some(k) = tally(sim, "unit off") {
                wlog(format!("{} UNIT OFF #{k}: W cast, unit=off in the test knobs - the clone is drawn as before", head(sim, me)));
            }
            return;
        }
        let spec = clone_spec(&stat, max).with(&KNOBS);
        match summon::spawn(sim, me, team, at, &spec) {
            Some(id) => {
                sim.add_buff(me, &BuffV1::timed(W_UNIT, W_LIFE + FLAG_MORE));
                sim.add_buff(me, &BuffV1::timed(&summon::handoff(W_UID, id), UID_TICKS));
                if let Some(k) = tally(sim, "unit spawn") {
                    wlog(format!("{} UNIT SPAWN #{k}: unit #{id} for team {team} where he cast W, {}: {}", head(sim, me),
                                 summon::pt(at), spec.shown()));
                }
            }
            None => {
                if let Some(k) = tally(sim, "unit fail") {
                    wlog(format!("{} UNIT SPAWN FAILED #{k}: spawn_unit gave no unit for '{}' at {} - the clone is drawn as \
                                  before", head(sim, me), spec.name, summon::pt(at)));
                }
            }
        }
    }
}

// ===================== 被动：金刚不坏 =====================

/// A handed-over unit not yet read as a settled one: its id, the cast's tick, looks so far, the drawn clone to fall back
/// on, the tick its handoff was taken.
#[derive(Clone, Copy, Debug)]
struct Fresh {
    id: usize,
    cast: usize,
    tries: usize,
    back: Option<Decoy>,
    seen: usize,
}

/// His clone as a unit, as the passive keeps it.
#[derive(Clone, Debug)]
struct Live {
    unit: summon::Unit,
    /// The drawn clone to fall back on while the unit may still turn out to be none (its first `LOST_AGE` ticks).
    back: Option<Decoy>,
    /// The health it was to start with (his then), and whether the look a tick after was logged.
    hp_goal: usize,
    dressed: bool,
    /// He was spinning at the last look; the tick of the next pulse; the next pulse is a spin's first (it knocks up).
    spinning: bool,
    next_pulse: usize,
    first: bool,
    /// What its spins did: (spins, pulses, enemies hit in all, knocked up in all).
    spun: (usize, usize, usize, usize),
}

/// One pulse of the clone's spin at `at`: `damage` physical and his hit picture on every enemy but towers within
/// `SPIN_R`, and on the spin's first (`up`) the knock-up on those not in the air already, not immune to crowd control and
/// no epic monster. -> (enemies hit, knocked up, already in the air).
fn pulse(sim: &mut StableSim<'_>, me: usize, team: usize, at: Pt, damage: usize, up: bool) -> (usize, usize, usize) {
    // (id, in the air already, not to be knocked up)
    let hit: Vec<(usize, bool, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && summon::hittable(u))
        .filter(|u| dist(summon::at_of(u), at) <= SPIN_R)
        .map(|u| (u.id(), (0..u.cc_count()).filter_map(|i| u.cc_at(i)).any(|c| c.kind == CcKindV1::Airborne.code()),
                  (0..u.buff_count()).filter_map(|i| u.buff_at(i)).any(|b| b.cc_immune)
                      || matches!(u.kind(), Some(EntityKindV1::Epic | EntityKindV1::Serpen))))
        .collect();
    let (mut ups, mut aloft) = (0, 0);
    for (id, in_air, unmoved) in &hit {
        sim.deal_damage_typed(me, *id, damage, DamageTypeV1::Ad, AttackTypeV1::Skill);
        sim.play_view_effect(SPIN_VIEW, me, &InputTargetV1::target(*id), 0, 0, 0);
        if !up || *unmoved || !sim.get_entity(*id).is_some_and(|e| e.is_alive()) {
            continue;
        }
        if *in_air {
            aloft += 1;
            continue;
        }
        sim.apply_cc(*id, &CcV1::of_kind(CcKindV1::Airborne, SPIN_UP));
        ups += 1;
    }
    (hit.len(), ups, aloft)
}

/// What a unit's crowd control reads back as: `Animation 119 spin, Stun 20`.
fn ccs_text(sim: &StableSim<'_>, id: usize) -> String {
    let Some(e) = sim.get_entity(id) else { return "no entity".to_string() };
    let v: Vec<String> = (0..e.cc_count()).filter_map(|i| e.cc_at(i)).take(6).map(|c| match CcKindV1::from_code(c.kind) {
        Some(CcKindV1::Animation) => format!("Animation {} {}", c.tick, c.name()),
        Some(k) => format!("{k:?} {}", c.tick),
        None => format!("kind {} {}", c.kind, c.tick),
    }).collect();
    if v.is_empty() { "none".to_string() } else { v.join(", ") }
}

/// Nothing but forced animations hold the unit (its spin may be cut without lifting anybody's stun from it).
fn only_posed(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        e.cc_count() > 0 && (0..e.cc_count()).filter_map(|i| e.cc_at(i)).all(|c| c.kind == CcKindV1::Animation.code())
    })
}

#[derive(Clone, Default)]
struct StoneSkin {
    p: Params,
    /// 回血的零头（百万分之一点生命）。
    carry: u64,
    /// 本包在画的分身。
    decoy: Option<Decoy>,
    /// His own unit (on_dead is given the player).
    me: usize,
    /// 0.2.0: the clone as a unit - handed over, not yet read as one; watched; watched a little after its end.
    fresh: Option<Fresh>,
    live: Option<Live>,
    wake: Option<summon::Wake>,
    units: usize,
}

impl StoneSkin {
    /// 每 tick 先读走 W 刚写的位置和单位的 id：有单位就接手（画面留着当退路），没有就照旧画。
    fn take_marks(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let marks: Vec<String> = {
            let Some(e) = sim.get_entity(me) else { return };
            (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).filter(|n| n.starts_with(MARK)).collect()
        };
        let mut spot = None;
        for name in &marks {
            sim.entity_remove_buff(me, name);
            spot = read_mark(name).or(spot);
        }
        let decoy = spot.map(|(at, cast)| Decoy::new(at, cast, &self.p));
        match summon::take_handoff(sim, me, W_UID) {
            Some(id) => {
                if let Some(old) = self.live.take() {
                    if let Some(k) = tally(sim, "unit let go") {
                        wlog(format!("{} UNIT #{} LET GO #{k}: a new clone, the unit #{} of the last one no longer watched",
                                     head(sim, me), old.unit.n, old.unit.id));
                    }
                }
                self.fresh = Some(Fresh { id, cast: spot.map_or(sim.tick(), |s| s.1), tries: 0, back: decoy, seen: sim.tick() });
            }
            None => {
                if let Some(d) = decoy {
                    self.decoy = Some(d);
                    if let Some(k) = tally(sim, "clone") {
                        wlog(format!("{} CLONE #{k} at ({:.0}, {:.0}) for {} ticks", head(sim, me), d.at.0, d.at.1, self.p.w_t));
                    }
                }
            }
        }
    }

    /// The unit turned out to be none (or was gone at once): the flag off, so the data's zone and spin slots play for the
    /// rest of the clone's time, and its pictures drawn where it stands.
    fn fall_back(&mut self, sim: &mut StableSim<'_>, me: usize, back: Option<Decoy>) -> &'static str {
        sim.entity_remove_buff(me, W_UNIT);
        match back {
            Some(d) => {
                self.decoy = Some(d);
                "the flag is off, the clone is drawn and strikes as before"
            }
            None => "the flag is off (no spot to draw the clone at)",
        }
    }

    /// A line for a hook that fired while the clone is a unit.
    fn hooked(&self, sim: &StableSim<'_>, hook: &str, entity: usize, other: usize, damage: Option<usize>) {
        let Some(live) = &self.live else { return };
        if let Some(k) = tally(sim, "unit hook") {
            wlog(format!("{} UNIT #{} HOOK #{k} {hook}: {}{}", head(sim, self.me), live.unit.n,
                         live.unit.hook_text(sim, entity, other, self.me), damage.map(|d| format!(", damage {d}")).unwrap_or_default()));
        }
    }

    /// The unit's spin with his: his `spin` forced on it as his starts, a pulse every `SPIN_EVERY` ticks while it lasts.
    fn spin(&mut self, sim: &mut StableSim<'_>, me: usize, live: &mut Live, spinning: bool, attack: usize, team: usize) {
        let (tick, id, n) = (sim.tick(), live.unit.id, live.unit.n);
        if spinning && !live.spinning {
            // his R has just started (the passive sees `r_on` at most a tick late): League's clone casts it with him
            let ticks = SPIN_T.saturating_sub(1).min(live.unit.left(tick)).max(1);
            let mut cc = CcV1::of_kind(CcKindV1::Animation, ticks as u64);
            cc.set_name(SPIN_ANIM);
            sim.apply_cc(id, &cc);
            (live.first, live.next_pulse, live.spun.0) = (true, tick + 1, live.spun.0 + 1);
            if let Some(k) = tally(sim, "unit spin") {
                wlog(format!("{} UNIT #{n} SPIN #{k}: his R with the clone out, spin {} - '{SPIN_ANIM}' forced on it for {ticks} \
                              ticks; its crowd control reads back as: {}", head(sim, me), live.spun.0, ccs_text(sim, id)));
            }
        } else if !spinning && live.spinning {
            // his spin is over: the clone's too, should anything be left of it (and nothing but it holds the unit)
            let cut = only_posed(sim, id) && sim.entity_clear_cc(id) > 0;
            if let Some(k) = tally(sim, "unit spin end") {
                wlog(format!("{} UNIT #{n} SPIN END #{k}: his R is over{}", head(sim, me),
                             if cut { " - the clone's spin cut with it" } else { "" }));
            }
        }
        live.spinning = spinning;
        if spinning && tick >= live.next_pulse {
            live.next_pulse = tick + SPIN_EVERY;
            let damage = spin_damage(attack);
            let (hit, ups, aloft) = pulse(sim, me, team, live.unit.at, damage, live.first);
            let first = std::mem::replace(&mut live.first, false);
            let s = &mut live.spun;
            (s.1, s.2, s.3) = (s.1 + 1, s.2 + hit, s.3 + ups);
            if let Some(k) = tally(sim, "unit pulse") {
                wlog(format!("{} UNIT #{n} PULSE #{k}: {damage} physical to {hit} enemies within {SPIN_R:.0} of it at {}{}",
                             head(sim, me), summon::pt(live.unit.at),
                             if first { format!("; the spin's first: knocked up {ups} for {SPIN_UP} ticks, {aloft} in the air already") }
                             else { String::new() }));
            }
        }
    }

    /// The unit's part of a tick: the look at a handed-over one, its health, its spin with his, its end.
    fn unit_tick(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let tick = sim.tick();
        let Some((team, here, hp, attack, spinning)) = sim.get_entity(me).map(|e| {
            (e.team(), summon::at_of(&e), e.hp().0, e.stat().attack, (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == R_ON))
        }) else {
            return;
        };
        if let Some(f) = self.fresh {
            // a new unit reads max health 1 and every stat 1 on its spawn tick and the next, and a health set then is
            // lost (game 0.7.2's presims: this clone asked for 1 health a tick after its spawn - its cap read 1 - and
            // read 1851/1851 a tick later): looked at a tick after its handoff at the soonest, taken on once its health
            // cap reads (league_neeko's W; summon.rs's Unit::settled)
            if tick <= f.seen {
                return;
            }
            match summon::Unit::look(sim, f.id, self.units + 1, f.cast, W_LIFE, team, player) {
                Ok((mut unit, line)) if unit.settled() || f.tries + 1 >= LOOK_TRIES => {
                    self.fresh = None;
                    self.units += 1;
                    // League's clone has his current health: the cap is his, the health now set to his own
                    let (had, hp_goal) = (unit.hp, hp.clamp(1, unit.max.max(1)));
                    let set = hp_goal < had && sim.entity_set_hp(f.id, hp_goal);
                    if set {
                        unit.health_set(hp_goal);
                    }
                    if let Some(k) = tally(sim, "unit look") {
                        wlog(format!("{} UNIT #{} LOOK #{k}: {line}{}; health to his own {hp_goal}: {}", head(sim, me), self.units,
                                     unit.unsettled_note(f.tries + 1),
                                     if set { "set" } else if hp_goal >= had { "it has no more" } else { "entity_set_hp REFUSED" }));
                    }
                    self.live = Some(Live { unit, back: f.back, hp_goal, dressed: false, spinning: false, next_pulse: 0, first: false,
                                            spun: (0, 0, 0, 0) });
                }
                Err(why) if f.tries + 1 >= LOOK_TRIES => {
                    self.fresh = None;
                    let then = self.fall_back(sim, me, f.back);
                    if let Some(k) = tally(sim, "unit lost") {
                        wlog(format!("{} UNIT LOST #{k}: the unit spawn_unit named never read as one in {LOOK_TRIES} ticks ({why}) \
                                      - {then}", head(sim, me)));
                    }
                }
                _ => self.fresh = Some(Fresh { tries: f.tries + 1, ..f }),
            }
            return;
        }
        if let Some(mut live) = self.live.take() {
            let n = live.unit.n;
            if live.back.is_some() && live.unit.age(tick) > LOST_AGE {
                live.back = None;
            }
            if !live.dressed {
                live.dressed = true;
                let seen = sim.get_entity(live.unit.id).map(|e| e.hp());
                if let (Some(k), Some((now, max))) = (tally(sim, "unit dress"), seen) {
                    wlog(format!("{} UNIT #{n} DRESS #{k}: a tick on, its health {now}/{max} (asked {})", head(sim, me), live.hp_goal));
                }
            }
            match live.unit.step(sim, Some(here)) {
                summon::Step::Alive(line) => {
                    // counted only when there is a line (a count every tick let the presims' first 40 and every 200th
                    // go by ticks, not lines: hardly a line a second got through)
                    if let Some(line) = line {
                        if let Some(k) = tally(sim, "unit line") {
                            wlog(format!("{} UNIT #{n} #{k}: {line}", head(sim, me)));
                        }
                    }
                    self.spin(sim, me, &mut live, spinning, attack, team);
                    self.live = Some(live);
                }
                summon::Step::Over(end) => {
                    let s = live.spun;
                    if let Some(k) = tally(sim, "unit over") {
                        wlog(format!("{} UNIT #{n} OVER #{k}: {}; it spun {} times: {} pulses, {} hits, {} knocked up", head(sim, me),
                                     end.text, s.0, s.1, s.2, s.3));
                    }
                    if end.age <= LOST_AGE {
                        // never really there: the data's clone (and its pictures) for the rest of its time
                        let then = self.fall_back(sim, me, live.back);
                        wlog(format!("{} UNIT #{n}: gone {} ticks after the cast - {then}", head(sim, me), end.age));
                    }
                    self.wake = Some(live.unit.wake(sim, &end));
                }
            }
        }
        if let Some(mut w) = self.wake.take() {
            let (lines, over) = w.step(sim);
            for line in lines {
                if let Some(k) = tally(sim, "unit wake") {
                    wlog(format!("{} UNIT #{} WAKE #{k}: {line}", head(sim, me), w.n));
                }
            }
            if !over {
                self.wake = Some(w);
            }
        }
    }

    /// 每 tick：在分身站的地方按格放画面；他死了、数据的分身散了、时间到了就停。
    fn draw_clone(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        let (names, alive) = {
            let Some(e) = sim.get_entity(me) else { return };
            ((0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect::<Vec<_>>(),
             e.is_alive())
        };
        let Some(mut d) = self.decoy else { return };
        let live = names.iter().any(|n| n == W_LIVE);
        if !alive || !live || now >= d.until {
            self.decoy = None;
            if let Some(k) = tally(sim, "clone gone") {
                let why = if !alive { "he died" } else if !live { "the data's clone is gone" } else { "its time is up" };
                wlog(format!("{} CLONE GONE #{k} after {} slots: {why}", head(sim, me), d.slot));
            }
            return;
        }
        if now >= d.next_slot {
            let spinning = names.iter().any(|n| n == R_ON);
            let pic = slot_pic(&self.p, d.slot, spinning);
            sim.play_view_effect(&format!("{ID}_{pic}"), me, &pos_input(d.at), 0, 0, 0);
            if spinning && !d.spinning {
                if let Some(k) = tally(sim, "clone spins") {
                    wlog(format!("{} CLONE SPINS #{k}: his R with the clone out, slot {}", head(sim, me), d.slot));
                }
            }
            d.spinning = spinning;
            d.slot += 1;
            d.next_slot += self.p.w_slot;
        }
        self.decoy = Some(d);
    }
}

impl StablePassive for StoneSkin {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, me: usize) {
        self.carry = 0;
        self.decoy = None;
        // a new life is a new entity: nothing of the old one's clone is his to watch any more
        if let Some(live) = self.live.take() {
            wlog(format!("{} UNIT #{}: still on the books at his respawn (his death did not reach on_dead) - let go",
                         head(sim, me), live.unit.n));
        }
        (self.me, self.fresh, self.wake) = (me, None, None);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        (self.fresh, self.wake, self.decoy) = (None, None, None);
        let Some(live) = self.live.take() else { return };
        let me = sim.get_player(player).and_then(|p| p.champion()).map_or(self.me, |e| e.id());
        let (tick, u) = (sim.tick(), &live.unit);
        // a dead champion's passive does not run: the clone fights on by itself to its time; a spin of his it was
        // copying stops with him
        let cut = live.spinning && only_posed(sim, u.id) && sim.entity_clear_cc(u.id) > 0;
        if let Some(k) = tally(sim, "unit orphan") {
            wlog(format!("{} UNIT #{} ORPHAN #{k}: Wukong died, his clone #{} at {} has {} ticks left and hp {}/{} - it fights on \
                          unwatched{}", head(sim, me), u.n, u.id, summon::pt(u.at), u.left(tick), u.hp, u.max,
                         if cut { "; its spin cut" } else { "" }));
        }
    }

    // While his clone is a unit, what the engine tells his passive: do the clone's hits and kills come here, and under
    // whose id? (summon.rs: whether a summon could carry its summoner's stacks - Stone Skin's, here)
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, target: usize, damage: &mut usize) {
        self.hooked(sim, "on_attack", entity, target, Some(*damage));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_kill", entity, victim, None);
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_unit_kill", entity, victim, None);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        self.me = me;
        self.take_marks(sim, me);
        self.unit_tick(sim, player, me);
        self.draw_clone(sim, me);
        if sim.tick() % self.p.every != 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, (hp, max_hp)) = (e.is_alive(), e.hp());
        if !alive || hp >= max_hp {
            self.carry = 0;
            return;
        }
        let n = stacks(sim, me);
        let (amount, carry) = regen_step(&self.p, max_hp, n, self.carry);
        self.carry = carry;
        if amount > 0 {
            sim.heal(me, me, amount);
            if let Some(k) = counted("regen") {
                wlog(format!("{} REGEN {amount} ({hp}/{max_hp}, {n} stacks) #{k}", head(sim, me)));
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
        "=== {ID} v{VERSION} (Wukong: Stone Skin regenerates % max health, W's clone a unit of its own) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "UNIT: Warrior Trickster's clone is a unit ('{}', spawn_unit) - {}; {W_LIFE} ticks where he cast W (move speed {W_SPEED}), \
         his health then, {W_HIT} + {W_HIT_AD}% of his attack a hit every {W_COOL} ticks within {W_REACH}; it spins with his R: \
         {SPIN_HIT} + {SPIN_HIT_AD}% of his attack every {SPIN_EVERY} ticks within {SPIN_R:.0}, the first knocking up {SPIN_UP} \
         ticks. Test knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(UNIT_NAME),
        if KNOBS.off { "OFF by the test knobs: the clone is drawn as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(),
        KNOBS.shown()
    ));
    module.add_native_passive(format!("{ID}:stone"), StoneSkin::default());
    // 0.1.2: W's clone drawn by the add-on (the data's pictures in its anchor never show in game), and W pressed for the
    // AI with an enemy champion in reach (src/trickster.rs: the game's AI cast it 4 times a game)
    module.add_native_effect(format!("{ID}:clone"), CloneMark);
    module.add_player_input_ai(trickster::Trickster::default());
    host.log(LogLevel::Info, "league_wukong loaded (Stone Skin % max-health regeneration, W's clone a unit).");
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
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"pct":40,"junk":7,"every":60}"#);
        assert_eq!((p.pct, p.every), (40, 60));
        assert_eq!(parse_params(r#"{"every":0}"#).every, 1);
    }

    #[test]
    fn the_copy_carries_the_default_params_and_no_data_regen() {
        let copy = include_str!("../override/league_wukong.data_champion");
        let at = copy.find("\"passive_ref\": \"league_wukong:stone\"").expect("no league_wukong:stone passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("pct", d.pct), ("every", d.every), ("w_t", d.w_t), ("w_slot", d.w_slot), ("w_period", d.w_period)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for name in STACKS {
            assert!(copy.contains(&format!("\"name\": \"{name}\"")), "the copy never lays {name}");
        }
        assert!(copy.contains("\"hp_regen\": 0"), "the copy's stacks still regenerate in data");
    }

    #[test]
    fn the_copy_leaves_the_clone_s_pictures_to_the_add_on() {
        let copy = include_str!("../override/league_wukong.data_champion").replace('\r', "");
        let main = include_str!("../../../league/champion/league_wukong.data_champion").replace('\r', "");
        assert!(copy.contains("\"effect_ref\": \"league_wukong:clone\""), "W does not mark the clone's spot");
        for pic in ["w_clone", "w_clone_atk", "w_clone_spin"] {
            // a ViewEffect's name is its last key (no comma after it); the view_effects entry goes on with "anim"
            let call = format!("\"name\": \"league_wukong_{pic}\"\n");
            assert!(main.matches(&call).count() > 1, "the main pack never plays {pic}");
            assert_eq!(copy.matches(&call).count(), 0, "the copy still plays {pic} in data");
            assert!(copy.contains(&format!("\"name\": \"league_wukong_{pic}\",\n")), "the copy lost the {pic} view");
        }
        // no clone of the spin's own (League's: the clone spins only when W left one)
        assert!(!main.contains("league_wukong_w_rc"), "the spin still brings a clone of its own");
    }

    #[test]
    fn the_mark_carries_the_spot_and_the_tick() {
        assert_eq!(read_mark(&mark((314_040.0, 367_255.0), 15_653)), Some(((314_040.0, 367_255.0), 15_653)));
        assert_eq!(read_mark("league_wukong_w_live"), None);
        assert_eq!(read_mark("league_wukong_clone:1:2"), None);
    }

    #[test]
    fn the_slots_follow_the_data() {
        let p = Params::default();
        // the SDK simulation: W at 15652 (its effect 15653), pictures at 15655 then every 20 ticks, 12 of them
        let d = Decoy::new((0.0, 0.0), 15_653, &p);
        assert_eq!((d.next_slot, d.until), (15_655, 15_893));
        let pics: Vec<_> = (0..6).map(|k| slot_pic(&p, k, false)).collect();
        assert_eq!(pics, ["w_clone_atk", "w_clone", "w_clone", "w_clone_atk", "w_clone", "w_clone"]);
        assert_eq!(slot_pic(&p, 4, true), "w_clone_spin");
    }

    #[test]
    fn league_rates() {
        let p = Params::default();
        // 0.35% of 3000 every 5 s = 10.5; ten half-second steps
        let (mut sum, mut carry) = (0, 0);
        for _ in 0..10 {
            let (a, c) = regen_step(&p, 3000, 0, carry);
            sum += a;
            carry = c;
        }
        assert_eq!(sum, 10);
        // five stacks: 2.1% of 3000 every 5 s = 63
        let (mut sum, mut carry) = (0, 0);
        for _ in 0..10 {
            let (a, c) = regen_step(&p, 3000, 5, carry);
            sum += a;
            carry = c;
        }
        assert_eq!(sum, 63);
    }

    // ---- 0.2.0: the clone as a unit ----

    #[test]
    fn the_clone_is_him_standing_with_the_strikes_numbers() {
        let his = StatV1 { attack: 180, magic_power: 0, hp: 900, defence: 56, magic_resistance: 30, move_speed: 1100, hp_regen: 4,
                           stack: 2, crit_chance: 20 };
        let spec = clone_spec(&his, 2200);
        assert_eq!((spec.name.as_str(), spec.life), ("league_wukong", 240));
        assert_eq!(spec.stat, StatV1 { attack: 180, magic_power: 0, hp: 2200, defence: 56, magic_resistance: 30, move_speed: 1,
                                       hp_regen: 0, stack: 0, crit_chance: 0 });
        // a hit: 50 % of 180 = 90, once a second within the strike's 30000, his swing's length and moment
        let a = spec.attack;
        assert_eq!(a.attack + spec.stat.attack * a.attack_ratio / 100, 90);
        assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (30_000, 60, 26, 11));
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        assert_eq!(a.attack_type, AttackTypeV1::BaseAttack.code());
        assert_eq!(clone_spec(&his, 0).stat.hp, 1);
        // the spin's pulse: 5 + 17 % of his attack (the main pack's spin at w_spin 50 %)
        assert_eq!(spin_damage(180), 35);
        // the parameters the passive is given are the same clone's
        let p = Params::default();
        assert_eq!((W_LIFE, W_COOL, SPIN_EVERY), (p.w_t, p.w_period, p.w_slot));
        assert!(SPIN_T / SPIN_EVERY == 6 && LOST_AGE < SPIN_EVERY && FIRST_SLOT < LOST_AGE);
        for name in [W_UNIT, &summon::handoff(W_UID, usize::MAX), &mark((960_000.0, 960_000.0), usize::MAX)] {
            assert!(name.len() <= BUFF_NAME_CAP, "{name}");
        }
    }

    #[test]
    fn the_copy_plays_the_datas_clone_only_without_the_unit() {
        let copy = include_str!("../override/league_wukong.data_champion").replace('\r', "");
        let main = include_str!("../../../league/champion/league_wukong.data_champion").replace('\r', "");
        assert!(!main.contains(W_UNIT));
        // the zone's strike and the twelve slots each look for the flag; the cast takes an earlier one off
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{W_UNIT}\"")).count(), 1 + W_LIFE / SPIN_EVERY);
        assert_eq!(copy.matches(&format!("\"type\": \"RemoveCasterBuff\",\n          \"name\": \"{W_UNIT}\"")).count(), 1);
        let off = copy.find(&format!("\"name\": \"{W_UNIT}\"")).unwrap();
        assert!(off < copy.find("\"effect_ref\": \"league_wukong:clone\"").unwrap(), "the flag is taken off after the spawn");
    }

    // ---- the clone as a unit on the mock world (summon_mock.rs: our guess of the host, to check this side's logic) ----

    use super::mock::{champion, unit, MPlayer, World};

    const GAREN: usize = 1;
    const CLONE_PICS: [&str; 3] = ["league_wukong_w_clone", "league_wukong_w_clone_atk", "league_wukong_w_clone_spin"];

    /// The test log, set before anything logs (the log's path is read once a process).
    fn log_file() -> PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_wukong_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_WUKONG_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// Wukong #0 (team 0, 600 of 1000 health) at (300000, 300000); Garen #1 (team 1) 20000 east of him, an enemy minion #2
    /// far to the south; a player each.
    fn world() -> (World, StoneSkin) {
        log_file();
        let mut w = World::default();
        let mut wukong = champion("league_wukong", 0, 300_000.0, 300_000.0);
        (wukong.hp, wukong.max) = (600, 1000);
        w.units = vec![wukong, champion("league_garen", 1, 320_000.0, 300_000.0),
                       unit("melee_minion", EntityKindV1::Minion, 1, 300_000.0, 700_000.0, 300)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() },
                         MPlayer { team: 1, champion: GAREN, ..Default::default() }];
        let mut me = StoneSkin::default();
        w.sim(|sim| me.on_spawn(sim, 0, 0));
        (w, me)
    }

    /// One tick: his passive while he lives, the world's own step (nothing of this add-on is queued).
    fn tick(w: &mut World, me: &mut StoneSkin) {
        assert!(w.due().is_empty(), "an effect was queued");
        if w.units[0].hp > 0 {
            w.sim(|sim| me.on_update(sim, 0, 0, 0));
        }
        w.step();
    }

    fn run(w: &mut World, me: &mut StoneSkin, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    /// The copy's W as the data casts it: the clone's flag (`w_live`), an earlier unit's flag off, league_wukong:clone.
    fn cast_w(w: &mut World) -> usize {
        w.units[0].buffs.push((BuffV1::timed(W_LIVE, 240), 240));
        w.sim(|sim| {
            sim.entity_remove_buff(0, W_UNIT);
            CloneMark.apply(sim, 0, 0, InputTargetV1::NONE);
        });
        w.tick
    }

    fn drawn(w: &World) -> usize {
        CLONE_PICS.iter().map(|p| w.viewed(p)).sum()
    }

    fn airborne(w: &World, id: usize) -> usize {
        w.units[id].ccs.iter().filter(|c| c.0.kind == CcKindV1::Airborne.code()).count()
    }

    #[test]
    fn the_clone_is_a_unit_that_stands_fights_and_spins_with_him() {
        let (mut w, mut me) = world();
        let t0 = cast_w(&mut w);
        // spawned in the cast itself, where he stands: his name, his team, his numbers, a move speed of 1
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life, s.tick), ("league_wukong", 0, 0, 240, t0));
        assert_eq!(s.at, (300_000, 300_000));
        assert_eq!((s.stat.attack, s.stat.hp, s.stat.defence, s.stat.move_speed), (100, 1000, 20, 1));
        assert_eq!((s.attack.attack, s.attack.attack_ratio, s.attack.range, s.attack.cooltime), (0, 50, 30_000, 60));
        let clone = s.gave.unwrap();
        // the flag is on him before the data's anchor first looks (a tick later)
        assert!(w.has(0, W_UNIT));
        run(&mut w, &mut me, 2);
        assert!(!w.units[0].buffs.iter().any(|b| b.0.name().starts_with(W_UID) || b.0.name().starts_with(MARK)));
        // his health now (600 of 1000), no pictures of the drawn clone beside it
        assert_eq!((w.units[clone].hp, w.units[clone].max), (600, 1000));
        assert!(me.live.is_some() && me.decoy.is_none());
        // it stands and hits Garen, 20000 away: 50 a hit (50 % of 100), once a second
        run(&mut w, &mut me, 100);
        assert!(dist((w.units[clone].x, w.units[clone].y), (300_000.0, 300_000.0)) < 200.0, "the clone walked");
        let hits = w.dealt(clone, DamageTypeV1::Ad);
        assert!(hits.len() == 2 && hits.iter().all(|h| *h == (GAREN, 50)), "{hits:?}");
        // his R: the clone plays his spin, pulses round itself 22 a time (5 + 17 % of 100), the first knocking Garen up
        w.units[0].buffs.push((BuffV1::timed(R_ON, SPIN_T), SPIN_T));
        run(&mut w, &mut me, 3);
        let posed: Vec<(u64, String)> = w.units[clone].ccs.iter().filter(|c| c.0.kind == CcKindV1::Animation.code())
            .map(|c| (c.1, c.0.name().to_string())).collect();
        assert!(posed.len() == 1 && posed[0].1 == "spin" && posed[0].0 > 100, "{posed:?}");
        assert_eq!(airborne(&w, GAREN), 1);
        let pulses = |w: &World| w.dealt(0, DamageTypeV1::Ad).iter().filter(|d| **d == (GAREN, 22)).count();
        assert_eq!(pulses(&w), 1);
        run(&mut w, &mut me, SPIN_T);
        assert_eq!(pulses(&w), SPIN_T / SPIN_EVERY, "a pulse every 20 ticks while he spins");
        assert_eq!(w.viewed(SPIN_VIEW), SPIN_T / SPIN_EVERY);
        assert_eq!(airborne(&w, GAREN), 0, "knocked up again after the spin's first pulse");
        // a second spin knocks up again - unless Garen is in the air already (League: not again after Wukong's own)
        w.units[GAREN].ccs.push((CcV1::of_kind(CcKindV1::Airborne, 30), 30));
        w.units[0].buffs.push((BuffV1::timed(R_ON, 10), 10));
        run(&mut w, &mut me, 3);
        assert_eq!(airborne(&w, GAREN), 1, "the clone knocked up someone in the air already");
        assert_eq!(pulses(&w), SPIN_T / SPIN_EVERY + 1);
        // its time: over, no pictures ever drawn, the flag on for the rest of the data's clone time
        run(&mut w, &mut me, 240);
        assert!(!w.units[clone].valid);
        assert!(me.live.is_none() && me.wake.is_none() && me.fresh.is_none());
        assert_eq!(drawn(&w), 0, "the drawn clone played beside the unit");
        assert_eq!(me.units, 1);
        assert!(w.queue.is_empty());
        assert!(!w.has(0, W_UNIT), "the flag outlived the clone's time by more than FLAG_MORE");
        assert!(w.tick > t0 + W_LIFE + FLAG_MORE);
    }

    #[test]
    fn no_unit_from_the_host_leaves_the_datas_clone_and_its_pictures() {
        // no such slot (an older host), a refusal, an id that never reads as a unit, a unit gone at once
        for case in 0..4 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                2 => w.spawn_never = true,
                _ => {}
            }
            let t0 = cast_w(&mut w);
            if case == 3 {
                run(&mut w, &mut me, 2);
                assert!(w.has(0, W_UNIT) && me.live.is_some());
                let id = w.spawns[0].gave.unwrap();
                w.units[id].valid = false;
            }
            while w.tick < t0 + 2 * SPIN_EVERY {
                tick(&mut w, &mut me);
            }
            // the flag off (or never on) a few ticks in: the data's strikes and slots play; the clone drawn where he cast
            assert!(!w.has(0, W_UNIT), "case {case}: the flag stayed on with no unit");
            assert!(me.live.is_none() && me.fresh.is_none(), "case {case}");
            assert!(me.decoy.is_some_and(|d| d.at == (300_000.0, 300_000.0)), "case {case}: no drawn clone");
            assert!(drawn(&w) >= 2, "case {case}: {} pictures", drawn(&w));
            assert_eq!(w.spawns.len(), if case == 0 { 0 } else { 1 }, "case {case}");
            run(&mut w, &mut me, 300);
            assert!(me.decoy.is_none() && w.queue.is_empty(), "case {case}");
        }
    }

    #[test]
    fn a_clone_that_reads_unsettled_at_first_gets_his_health_once_it_settles() {
        // game 0.7.2's presims: the clone read hp 1851/1 a tick after its spawn, its health was set to 1 then (its cap
        // read 1), and it read 1851/1851 a tick later (World::settle: its first two ticks read 1, a health set then lost)
        let (mut w, mut me) = world();
        w.settle = 2;
        let t0 = cast_w(&mut w);
        let clone = w.spawns[0].gave.unwrap();
        run(&mut w, &mut me, 2);
        assert!(me.live.is_none() && me.fresh.is_some(), "taken on before it settled");
        run(&mut w, &mut me, 2);
        assert!(me.live.as_ref().is_some_and(|l| l.unit.settled()));
        assert_eq!((w.units[clone].hp, w.units[clone].max), (600, 1000), "not his health");
        assert!(w.has(0, W_UNIT) && me.decoy.is_none());
        let text = std::fs::read_to_string(log_file()).expect("the log");
        assert!(text.lines().any(|l| l.contains(&format!("t={} #0 UNIT #", t0 + 2)) && l.contains(" LOOK #")
                                && l.contains("hp 1000/1000 attack 100") && l.contains("health to his own 600: set")
                                && !l.contains("still reads")), "no settled LOOK line at t={}", t0 + 2);
    }

    #[test]
    fn the_clone_fights_on_when_he_dies() {
        let (mut w, mut me) = world();
        cast_w(&mut w);
        run(&mut w, &mut me, 80);
        let clone = w.spawns[0].gave.unwrap();
        let before = w.dealt(clone, DamageTypeV1::Ad).len();
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.on_dead(sim, 0));
        assert!(me.live.is_none() && me.decoy.is_none());
        run(&mut w, &mut me, 120);
        assert!(w.dealt(clone, DamageTypeV1::Ad).len() > before, "the clone stopped fighting when he died");
        assert!(w.queue.is_empty());
        assert_eq!(drawn(&w), 0);
    }

    #[test]
    fn the_log_tells_the_clones_whole_life() {
        let (mut w, mut me) = world();
        let t0 = cast_w(&mut w);
        run(&mut w, &mut me, 70);
        let clone = w.spawns[0].gave.unwrap();
        let mut dealt = 50;
        w.sim(|sim| me.on_attack(sim, 0, clone, GAREN, &mut dealt));
        w.units[0].buffs.push((BuffV1::timed(R_ON, 60), 60));
        run(&mut w, &mut me, 80);
        w.body_ticks = 20;
        w.players[1].gold += 30;
        w.hurt(clone, 10_000);
        run(&mut w, &mut me, 60);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" UNIT ") || l.contains(" MARK ")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "MARK #", "W cast at (300000, 300000)",
            "UNIT SPAWN #", "where he cast W, (300000,300000): 'league_wukong' for 240 ticks, attack 100 ap 30 hp 1000 def 20 mr 20 \
             speed 1; hits 0 + 50% of its attack, range 30000, every 60 ticks (26 long, lands at 11)",
            "LOOK #", "reads back as name 'league_wukong' kind summon team 0 champion=false", "health to his own 600: set",
            "DRESS #", "a tick on, its health 600/1000 (asked 600)",
            " of 240 ticks, at (", "near it: champion #1 league_garen",
            "SPIN #", "his R with the clone out, spin 1 - 'spin' forced on it for 119 ticks; its crowd control reads back as: \
             Animation 119 spin",
            "PULSE #", "22 physical to 1 enemies within 28000 of it at (300000,300000); the spin's first: knocked up 1 for 36 ticks, \
             0 in the air already",
            "SPIN END #", "OVER #", "KILLED after ", "it spun 1 times: 3 pulses, 3 hits, 1 knocked up", "p1 gold +30",
            "HOOK #", "on_attack: entity #3 (the unit itself) -> champion #1 league_garen, 20000 from the unit", "damage 50",
            "WAKE #", "its body was there for ",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
        assert!(text.contains(&format!("t={t0} #0 UNIT SPAWN")));
        let longest = mine.iter().map(|l| l.len()).max().unwrap();
        assert!(longest < 700, "a line of {longest} bytes");
    }
}

#[cfg(test)]
#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;
