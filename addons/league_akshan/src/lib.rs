//! 阿克尚扩展包（用户 2026-10-18：「技能方案按 A 做（带扩展包）」「大招改rust也做不了吗」「做成复活队友的吧 游戏更新你就做动态寻址
//! 方便自动找」）。主包保持纯数据；`mod.override_info` 把主包的阿克尚换成 `override/` 里的副本（`make_override.py` 用
//! tools/kit/build_akshan.py 的 `native=1` 生成），本包补数据做不到的几件事：
//!
//! - **无所不用按目标计 3 下**（`league_akshan:hit`，打在每一枪、回旋镖、E 的每一枪、R 的每一发子弹上）：同一个目标第 3 下时给他
//!   3 tick 的 `league_akshan_p_go`，数据读到就打出额外伤害（英雄时加护盾）。主包只能数他打中任何人的次数。
//! - **恩怨相抵按已损失生命算**（`league_akshan:rhit`）：每发 `R_DMG + R_RATIO% AD`，目标每少 1% 生命多一点，到少了 `R_FULL`%
//!   时是 `R_MAX` 倍（英雄联盟 0–200% 加成在 67% 封顶）。引导中（`r_chan`、还没开火）被动每 tick 看一眼：存的子弹打得死子弹要去的
//!   那个英雄（数据锁定的 `R_SIGHT`，没有就是射程里血最少的），或者他快跑出射程，就给 `league_akshan_r_fire`，数据提前开火（英雄
//!   联盟里玩家手动提前放）。打不打得死（`lethal`）按他的护甲减伤算；线上站着敌方单位时，它们先挨子弹（各挨到死），剩下的子弹
//!   还要多打 `LETHAL_MARGIN`% 才算。
//!   0.2.6：子弹由本包发（`league_akshan:aim`，副本里每一发的效果）：朝引导时锁定的那个英雄（记在他身上的 `r_lock:<id>`），
//!   没有就射程里血最少的；以前数据的每一发在射程里「最近打过的敌方英雄」里随机挑一个，11-04 的日志里 60 发有 33 发没打在锁定的
//!   身上、30 次 R 有 11 次一发没中。子弹是原生投射物（直线、不穿透、打到第一个敌方单位），打中走 `rhit`：伤害、命中画面和声音、
//!   无所不用计数（第 3 下也由本包打出）。每次 R 引导结束、最后一发落地后记一行 `R DONE`（发了几发、几发打中锁定的、锁定的死没死）。
//!   0.2.7：游戏的投射物每 tick 走 `speed`、只打圆心在它这一 tick 位置 `radius` 内的单位（不扫中间、不算体型），6000 的圆
//!   每 tick 飞 20000 会从人身上跨过去（11-05 的日志一半子弹没中）：圆改 11000（≥ 速度的一半）；子弹朝他走到的地方飞（被动
//!   每 tick 量他的速度，`lead`）；丢了子弹时记一行 `R MISS`（每发离锁定的人最近多远）。
//! - **放大招的时机**（AI 钩子 `league_akshan:ult`）：射程里有英雄生命 ≤ 50%（或存满能打死），自己身边 `R_SAFE` 内没有敌方英雄、
//!   自己生命 ≥ 40% 才放；AI 想在别的时候放就改成普攻 / 走过去。只按已解锁、冷却好的 R（低等级按 R 会让游戏 AI 崩溃）。
//! - **赴险夺人：恶徒和复活**（被动 `league_akshan:rogue`）：读游戏的击杀记录。敌方英雄杀了阿克尚的队友（不算他自己）就成为
//!   恶徒 60 秒（头上 `league_akshan_w_mark` 的图）；阿克尚朝恶徒附近时加移速。阿克尚击杀或助攻击杀恶徒：被这个恶徒杀死、还在等
//!   复活的队友 1 秒后在泉水复活（英雄联盟一样），阿克尚得 100 金，标记清除。
//! - **骄行荡寇击杀刷新**：阿克尚击杀或助攻击杀敌方英雄，E 的冷却清到 0.5 秒（英雄联盟一样）。
//!
//! **复活怎么做到的**：稳定接口里没有改复活时间的函数（`player_respawn_time` 只读）。游戏每个阵亡玩家身上有一个“剩余复活 tick”，
//! 每 tick 减 1，减到 0 时游戏自己在泉水重新生成英雄。本包在运行时读游戏的 `player_respawn_time` / `player_is_alive` 两个函数的
//! 机器码，自己找出“取玩家”的虚表槽、存活标记和剩余 tick 的偏移（`decode`，**动态寻址**：游戏更新后偏移变了也能找到），交叉核对
//! 两个函数一致；每次写之前还要求“阵亡、读到的值等于游戏接口读到的值、≥ 1”，只把它改小到 60 tick（绝不写 0：0 减 1 会变成
//! 永远不复活）。任何一步对不上就不写，只在日志里记一次：最坏只是不复活，不会出错。复活走的是游戏自己的复活流程（新英雄、满血、
//! 等级装备不变）。比赛会被重算好几遍（预演、观看、回放）：只在模拟里的被动钩子里写，用的都是模拟里的数据，结果每遍一样。
//!
//! **两张 5v5 地图**（2026-11-10）：子弹飞到的地图边、E 荡的弧线夹的边、钩点偏向的地图中间，都按这一场的地图
//! （`game_places::terrain::map_of_sim`：游戏自己的 960000 见方，Rin 的召唤师峡谷 1614545 见方）；以前一律按 960000，
//! 峡谷上过了 960000 的子弹停在半张图的边上、荡到一半被夹回去。峡谷上荡的每一点还要落在能站的地方
//! （`game_places::terrain::stand_ok`：峡谷的墙往外长一格，和作者的寻路一致）：弧线上下一点站不住就荡到这里为止、松手，
//! 他停在上一个能站的地方，从不挪进墙里（用户 2026-11-10：「有的地方会走路卡住」）。没有墙体文件时只有地图边。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_akshan.log`，每次启动游戏重写，上一次的留在 .prev.log：`LAYOUT`
//! （找到的偏移）、`MARK`、`REVIVE`、`VIEW`、`BANNER`、`REFRESH`、`R FIRE`、`R HELD` / `R CAST`、`R AIM`、`BULLET`、`R DONE`、
//! `R MISS`、`SWING`（开始；被打断时带上身上的控制种类），限了条数；屏幕上放的那一场不限（0.2.7，`logged`）。

use std::collections::{BTreeMap, HashMap};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{map_of_sim, rift_status, stand_ok, Map};
use mod_api_stable::*;

pub mod banner;

const ID: &str = "league_akshan";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_akshan") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
const HERO: &str = "league_akshan";

// ---- 主包数据里的名字（tools/kit/build_akshan.py）
pub const P_GO: &str = "league_akshan_p_go";
pub const R_CHAN: &str = "league_akshan_r_chan";
pub const R_OPEN: &str = "league_akshan_r_open";
pub const R_FIRE: &str = "league_akshan_r_fire";
/// The data's lock on the champion he aims at (r_ch ticks from the cast): taken off here once he fires early or the
/// channel ends (the user, 2026-10-23: 「应该是瞄准的时候没特效 导致玩家感觉没伤害」).
pub const R_SIGHT: &str = "league_akshan_r_sight";
pub const STORED: [&str; 5] =
    ["league_akshan_r_s1", "league_akshan_r_s2", "league_akshan_r_s3", "league_akshan_r_s4", "league_akshan_r_s5"];
/// 0.2.6, the add-on's own bullets: the lock kept on him through the firing as `r_lock:<id>` (the data's r_sight lasts the
/// channel only), the bullet projectile (the data's picture), and on him one `r_shot` / `r_onlock` / `r_onother` buff a
/// bullet fired / landed on the lock / landed elsewhere, read for the R DONE line.
pub const R_LOCK: &str = "league_akshan_r_lock";
pub const R_BULLET: &str = "league_akshan_r_bullet";
pub const R_SHOT: &str = "league_akshan_r_shot";
pub const R_ONLOCK: &str = "league_akshan_r_onlock";
pub const R_ONOTHER: &str = "league_akshan_r_onother";
/// 0.2.7: on him while R is on, `r_v:<id>:<vx>:<vy>` - the walk per tick of the champion the next bullet goes to, which
/// the passive measures and the bullet leads by (`lead`) - and one `r_b:<tick>:<x>:<y>:<end x>:<end y>` a bullet fired,
/// its path, for the R MISS line.
pub const R_VEL: &str = "league_akshan_r_v";
pub const R_PATH: &str = "league_akshan_r_b";
/// The walk is measured over the last TRACK_T ticks; a step faster than V_MAX a tick is a dash or a blink (over before the
/// bullet arrives: no lead); the lead is at most LEAD_CAP.
const TRACK_T: usize = 4;
pub const V_MAX: f64 = 2_500.0;
pub const LEAD_CAP: f64 = 30_000.0;
const VIEW_R_HIT: &str = "league_akshan_r_hit";
const VIEW_P_HIT: &str = "league_akshan_p_hit";
/// Dirty Fighting's shield cooldown and shield flag (the data's p_scd / p_sh).
pub const P_SCD: &str = "league_akshan_p_scd";
pub const P_SH: &str = "league_akshan_p_sh";
pub const MARK: &str = "league_akshan_w_mark";
pub const W_HASTE: &str = "league_akshan_w_haste";
// sounds of the main pack (league/sound/sfx) the add-on plays
const SFX_MARK: &str = "league_akshan_w_mark";
const SFX_REVIVE: &str = "league_akshan_w_revive";
/// The revive's golden beam (tools/art/fx_akshan_revive.py): on Akshan as the Scoundrel falls, on each ally the tick he
/// stands again at his fountain - the revive showed nothing before (the user: 「我一直在游戏里看不出什么效果」).
const VIEW_REVIVE: &str = "league_akshan_w_revive";
/// How long a revived ally is watched for his return (the revive's REVIVE_T and some).
const BACK_WAIT: usize = 240;
const SFX_GOLD: &str = "league_akshan_w_gold";

// ---- 数字（和 build_akshan.P 一致：make_override.py 把 P 写进副本的 passive.params，测试核对）
pub const P_T: usize = 300;
pub const R_DMG: usize = 35;
pub const R_RATIO: usize = 25;
pub const R_MAX: usize = 3;
pub const R_FULL: usize = 67;
pub const R_REACH: u64 = 220_000;
pub const R_RANGE: u64 = 160_000;
/// The bullet's circle (build_akshan r_w): the engine hits a unit only when its CENTRE is within this of the bullet's
/// position on a tick - no sweep between ticks, no body radius (game 0.7.1, fitted on the 11-05 bullets). 0.2.6's 6000
/// at R_SPEED 20000 left 8000-unit gaps on the line between ticks and lost half the bullets: 2 x R_W >= R_SPEED (0.2.7).
pub const R_W: f64 = 11_000.0;
/// With enemies on the line the bullets left over must kill with this much (%) to spare: the units walk, he steps aside
/// from bullets aimed where he stood.
pub const LETHAL_MARGIN: usize = 25;
/// The bullets' flight (build_akshan r_speed) and the data's poll gap while R fires (r_gap).
pub const R_SPEED: u64 = 20_000;
pub const R_GAP: usize = 6;
/// Dirty Fighting's third hit (build_akshan p_dmg / p_ratio / p_sh / p_sh_r / p_sh_t / p_scd): the add-on's bullets
/// deal it themselves (0.2.6).
pub const P_DMG: usize = 20;
pub const P_RATIO: usize = 30;
pub const P_SH_AMT: usize = 40;
pub const P_SH_R: usize = 35;
pub const P_SH_T: usize = 120;
pub const P_SCD_T: usize = 600;
const STACK: &str = "league_akshan_p_s";
const FLAG_T: usize = 3;
/// The early-fire flag must outlive one poll gap (0.2.6): FLAG_T is seen on 2 ticks and the data polls r_fire every
/// R_GAP (11-04 logs: R FIRE doubled five times, lost once).
pub const FIRE_T: usize = R_GAP + 1;
/// The R DONE line waits this long after the channel (r_chan) ends: the last bullet still flies (reach / speed = 11).
const R_DONE_WAIT: usize = 12;
/// How long the lock and the bullet counters stay on him.
const R_BOOK_T: usize = 300;
/// The game's own 5v5 map's side; the Rift's is `Map::extent` (the bullets stop at the edge of the map they fly on).
const MAP_END: f64 = 960_000.0;
const MARK_T: usize = 3600;
const REVIVE_T: u64 = 60;
const GOLD: i64 = 100;
const E_LEFT: usize = 30;
const HASTE_R: u64 = 100_000;
const HASTE: i32 = 25;
const R_SAFE: u64 = 45_000;
const R_LOW: usize = 50;
const ULT_LEVEL: usize = 5;
// ---- Heroic Swing: the swing round a hook point (build_akshan: e_n x e_every ticks; the rope picture is 42 px)
pub const SW: &str = "league_akshan_sw";
pub const ROPE: &str = "league_akshan_e_rope";
pub const SWING_T: usize = 84;
pub const ROPE_R: f64 = 42_000.0;
const SWEEP: f64 = 2.0 * std::f64::consts::PI / 3.0; // 120 degrees round the hook
const HOOK_OFF: f64 = std::f64::consts::PI / 3.0; // the hook 60 degrees off the line to the target
const HAND: f64 = 20_000.0; // the rope at his hand's height (raised on the screen)
/// The swing stays this far inside the map's edges (10000 .. side - 10000: 950000 on the game's own map).
const MAP_LO: f64 = 10_000.0;
const HARD: [CcKindV1; 8] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::ForceMove,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::BlockMoveSkill,
];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AKSHAN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_akshan.log");
        }
    }
    PathBuf::from("league_akshan.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

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

const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

static VIEW_COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// `counted` for a line of `sim` (0.2.7): the sims on screen (the match he watches, spectates or replays) are never capped
/// and keep their own count; the presims and the background matches keep LOG_FIRST / LOG_EVERY. The 11-05 presims used
/// up the first 60 R lines before the screen's set began, so the set on screen had none.
pub(crate) fn logged(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    if on_screen(sim).is_none() {
        return counted(kind);
    }
    let mut c = VIEW_COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    Some(*n)
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

/// This launch's log has told the Rift already.
static RIFT_TOLD: AtomicBool = AtomicBool::new(false);

/// The map this sim plays on; the first Rift a launch, a line in the log.
fn map_here(sim: &StableSim<'_>) -> Map {
    let map = map_of_sim(sim);
    if map == Map::Rift && !RIFT_TOLD.swap(true, Ordering::Relaxed) {
        wlog(format!("== Rift: R's bullets fly to the Rift's edge, E's swing stays {MAP_LO:.0} inside the Rift's {:.0} \
                      square and its hook leans to the Rift's middle (not the game's own {MAP_END:.0}), the swing lets go \
                      at the last spot off the Rift's walls (stand_ok); {} ==", map.extent(), rift_status()));
    }
    map
}

/// The sims the screen replays (the client's own match view, spectating, a replay) - not the server's presims nor the
/// background matches (origin unknown): their revives get the banner (banner.rs).
fn on_screen(sim: &StableSim<'_>) -> Option<(u64, u64)> {
    let o = sim.sim_origin().unwrap_or_default();
    matches!(SimOriginKindV1::from_code(o.kind),
        Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay))
        .then_some((o.match_id, o.set_index))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn count_buff(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).count())
}

// ===================== 计算（单元测试用） =====================

/// 一发恩怨相抵：最低伤害 x (100% .. R_MAX x 100%)，按目标少了多少生命（R_FULL% 时封顶）。
pub fn bullet_damage(attack: usize, hp: usize, max_hp: usize) -> usize {
    let base = R_DMG + R_RATIO * attack / 100;
    if max_hp == 0 {
        return base;
    }
    let missing = (max_hp.saturating_sub(hp) * 100 / max_hp).min(R_FULL);
    base * (100 + (R_MAX - 1) * 100 * missing / R_FULL) / 100
}

/// `n` 发连着打在一个人身上（每发按打之前的生命算）一共多少，护甲减伤前。
pub fn volley(attack: usize, mut hp: usize, max_hp: usize, n: usize) -> usize {
    let mut sum = 0;
    for _ in 0..n {
        let d = bullet_damage(attack, hp, max_hp);
        sum += d;
        hp = hp.saturating_sub(d);
    }
    sum
}

/// A unit the bullets may hit: where it stands, its body (for the log; the bullets go by the centre), health, shield, max
/// health and armour.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Body {
    pub id: usize,
    pub at: (f64, f64),
    pub r: f64,
    pub hp: usize,
    pub shield: usize,
    pub max: usize,
    pub armor: usize,
}

/// Physical damage after armour (the bullets deal `DamageTypeV1::Ad`; league_vayne_bolts' `bolt_damage`).
pub fn armoured(d: usize, armor: usize) -> usize {
    d * 100 / (100 + armor)
}

/// `n` bullets on `u`, one by one: what each deals (`keep`% of it after his armour; each read on the health he has
/// then, the shield taking it first) and the health it leaves him.
fn rain(attack: usize, u: &Body, n: usize, keep: usize) -> Vec<(usize, usize)> {
    let (mut hp, mut shield) = (u.hp, u.shield);
    (0..n)
        .map(|_| {
            let d = armoured(bullet_damage(attack, hp, u.max), u.armor) * keep / 100;
            let s = d.min(shield);
            shield -= s;
            hp = hp.saturating_sub(d - s);
            (d, hp)
        })
        .collect()
}

/// What `n` bullets deal `u` in all, after his armour.
pub fn armoured_volley(attack: usize, u: &Body, n: usize) -> usize {
    rain(attack, u, n, 100).iter().map(|x| x.0).sum()
}

/// How many of `n` bullets it takes to drop `u` (`keep`% of each after his armour); None when they leave him standing.
pub fn bullets_to_drop(attack: usize, u: &Body, n: usize, keep: usize) -> Option<usize> {
    rain(attack, u, n, keep).iter().position(|x| x.1 == 0).map(|k| k + 1)
}

/// The units standing on the bullets' line from `me` to `to` - between the two, their centre within the bullet's R_W of
/// it - nearest first: the bullets stop on the first enemy they meet. 0.2.7: the engine counts the centre only (no body
/// radius); 0.2.6 added the unit's body (13000-21000 off the line) and held early fires for units the bullets pass by.
pub fn on_line(me: (f64, f64), to: (f64, f64), units: &[Body]) -> Vec<Body> {
    let (dx, dy) = (to.0 - me.0, to.1 - me.1);
    let len = (dx * dx + dy * dy).sqrt();
    if len < 1.0 {
        return Vec::new();
    }
    let u = (dx / len, dy / len);
    let mut on: Vec<(f64, Body)> = units
        .iter()
        .filter_map(|b| {
            let v = (b.at.0 - me.0, b.at.1 - me.1);
            let along = v.0 * u.0 + v.1 * u.1;
            let off = (v.0 * u.1 - v.1 * u.0).abs();
            (along > 0.0 && along < len && off <= R_W).then_some((along, *b))
        })
        .collect();
    on.sort_by(|a, b| a.0.total_cmp(&b.0));
    on.into_iter().map(|x| x.1).collect()
}

/// Whether `n` stored bullets kill `him`: after his armour; with no enemy on the line every bullet reaches him, else
/// the units on it take theirs first (each until it falls) and the rest must kill him with LETHAL_MARGIN% to spare.
/// 0.2.4 summed the bullets before armour and gave him all of them: in the 11-02 logs only 5 of 20 early "lethal"
/// fires put all their bullets on him, and he lived.
pub fn lethal(attack: usize, him: &Body, n: usize, blockers: &[Body]) -> bool {
    if blockers.is_empty() {
        return bullets_to_drop(attack, him, n, 100).is_some();
    }
    let taken: usize = blockers.iter().map(|b| bullets_to_drop(attack, b, n, 100).unwrap_or(n)).sum();
    let left = n.saturating_sub(taken);
    bullets_to_drop(attack, him, left, 100 * 100 / (100 + LETHAL_MARGIN)).is_some()
}

/// 被动第几下：之前同一目标有几层 -> (这一下是不是第 3 下, 之后留几层)。
pub fn next_hit(stacks: usize) -> (bool, usize) {
    if stacks >= 2 {
        (true, 0)
    } else {
        (false, stacks + 1)
    }
}

// ===================== 动态寻址：游戏的剩余复活 tick =====================

/// 从游戏的两个只读函数的机器码里读出来的布局。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct LifeLayout {
    /// 世界虚表里“按编号取玩家”的槽（字节偏移）。
    pub getp: usize,
    /// 玩家身上存活标记的偏移（0 = 阵亡，1 = 存活）。
    pub tag: usize,
    /// 紧跟着的值：存活时是英雄实体编号，阵亡时是剩余复活 tick。
    pub val: usize,
}

#[derive(Default, Debug, PartialEq, Eq)]
struct Scan {
    getp: Option<usize>,
    tag_cmp: Option<usize>,
    val: Option<usize>,
    tag_movzx: Option<usize>,
    dec_rdx: bool,
    load_data: bool,
    load_vt: bool,
}

/// ModRM 的位移（mod 01 = disp8，mod 10 = disp32；rm = 100 要 SIB，不认）：(reg, disp, 指令里 ModRM 之后的长度)。
fn modrm_disp(code: &[u8], at: usize) -> Option<(u8, usize, usize)> {
    let m = *code.get(at)?;
    let (md, reg, rm) = (m >> 6, (m >> 3) & 7, m & 7);
    if rm == 4 {
        return None;
    }
    match md {
        1 => Some((reg, *code.get(at + 1)? as i8 as isize as usize, 2)),
        2 => {
            let b = code.get(at + 1..at + 5)?;
            Some((reg, i32::from_le_bytes([b[0], b[1], b[2], b[3]]) as isize as usize, 5))
        }
        _ => None,
    }
}

/// 扫一个函数开头的 `len` 个字节，认出：`dec rdx`、从 [rcx] / [rcx+8] 取世界数据和虚表、`call [reg+X]`（取玩家的槽）、
/// `cmp byte [reg+T],0` + `je` 落到 `mov r64,[reg+V]`（存活标记和值），`movzx r32, byte [reg+T]`（存活标记）。
fn scan(code: &[u8]) -> Scan {
    let mut s = Scan::default();
    let mut i = 0;
    while i + 3 < code.len() {
        let rex = (0x40..=0x4f).contains(&code[i]);
        let (w, op) = if rex { (code[i] & 8 != 0, i + 1) } else { (false, i) };
        let b = code[op];
        if rex && code[i] == 0x48 && b == 0xff && code.get(op + 1) == Some(&0xca) {
            s.dec_rdx = true;
        }
        if w && b == 0x8b {
            if let Some(&m) = code.get(op + 1) {
                // mov r64,[rcx] (mod 00, rm 001) / mov r64,[rcx+8] (mod 01, rm 001, disp8 8)
                if m >> 6 == 0 && m & 7 == 1 {
                    s.load_data = true;
                }
                if m >> 6 == 1 && m & 7 == 1 && code.get(op + 2) == Some(&8) {
                    s.load_vt = true;
                }
            }
        }
        if b == 0xff {
            if let Some((2, disp, _)) = modrm_disp(code, op + 1) {
                s.getp.get_or_insert(disp);
            }
        }
        if b == 0x80 && s.tag_cmp.is_none() {
            if let Some((7, disp, n)) = modrm_disp(code, op + 1) {
                let imm = op + 1 + n;
                if code.get(imm) == Some(&0) && code.get(imm + 1) == Some(&0x74) {
                    let target = imm + 3 + code[imm + 2] as usize;
                    // the je lands on mov r64,[reg+V]
                    if let Some(&r) = code.get(target) {
                        if (0x48..=0x4f).contains(&r) && code.get(target + 1) == Some(&0x8b) {
                            if let Some((_, v, _)) = modrm_disp(code, target + 2) {
                                s.tag_cmp = Some(disp);
                                s.val = Some(v);
                            }
                        }
                    }
                }
            }
        }
        if b == 0x0f && code.get(op + 1) == Some(&0xb6) && s.tag_movzx.is_none() {
            if let Some((_, disp, _)) = modrm_disp(code, op + 2) {
                s.tag_movzx = Some(disp);
            }
        }
        i += 1;
    }
    s
}

/// 两个函数（剩余复活时间、是否存活）的机器码 -> 布局；交叉核对不过就 None。
pub fn decode(respawn_time: &[u8], is_alive: &[u8]) -> Option<LifeLayout> {
    let a = scan(respawn_time);
    let b = scan(is_alive);
    let (getp, tag, val) = (a.getp?, a.tag_cmp?, a.val?);
    let ok = a.dec_rdx
        && a.load_data
        && a.load_vt
        && b.dec_rdx
        && b.getp == Some(getp)
        && b.tag_movzx == Some(tag)
        && val == tag + 8
        && getp % 8 == 0
        && getp < 0x800
        && tag < 0x10000;
    ok.then_some(LifeLayout { getp, tag, val })
}

/// 跟过 jmp 跳板（E9 rel32 / EB rel8），最多 3 次。
unsafe fn follow(mut f: *const u8) -> *const u8 {
    for _ in 0..3 {
        match *f {
            0xe9 => {
                let r = i32::from_le_bytes(std::ptr::read_unaligned(f.add(1) as *const [u8; 4]));
                f = f.offset(5 + r as isize);
            }
            0xeb => f = f.offset(2 + *(f.add(1) as *const i8) as isize),
            _ => break,
        }
    }
    f
}

const SCAN_LEN: usize = 0x60;

/// 解码结果按两个函数的地址缓存（地址变了 = 换了游戏，重新解码）；None = 对不上，不写。
static LAYOUT: Mutex<Option<(usize, usize, Option<LifeLayout>)>> = Mutex::new(None);

const _: () = assert!(std::mem::size_of::<StableSim<'static>>() == std::mem::size_of::<*mut SimCtxV1>());

/// StableSim 里唯一的字段就是 SimCtxV1 指针（大小核对过）。
fn raw_ctx(sim: &StableSim<'_>) -> *mut SimCtxV1 {
    unsafe { *(sim as *const StableSim<'_> as *const *mut SimCtxV1) }
}

fn layout(sim: &StableSim<'_>) -> Option<LifeLayout> {
    let ctx = raw_ctx(sim);
    if ctx.is_null() {
        return None;
    }
    let vt = unsafe { (*ctx).sim };
    if vt.is_null() {
        return None;
    }
    let rt = unsafe { (*vt).player_respawn_time }? as usize;
    let al = unsafe { (*vt).player_is_alive }? as usize;
    let mut cache = LAYOUT.lock().unwrap_or_else(|e| e.into_inner());
    if let Some((a, b, l)) = *cache {
        if a == rt && b == al {
            return l;
        }
    }
    let l = unsafe {
        let (frt, fal) = (follow(rt as *const u8), follow(al as *const u8));
        decode(std::slice::from_raw_parts(frt, SCAN_LEN), std::slice::from_raw_parts(fal, SCAN_LEN))
    };
    match l {
        Some(l) => wlog(format!(
            "LAYOUT found: get_player slot +0x{:x}, life tag +0x{:x}, remaining ticks +0x{:x} (respawn_time 0x{rt:x}, is_alive 0x{al:x})",
            l.getp, l.tag, l.val
        )),
        None => wlog(format!(
            "LAYOUT NOT FOUND in respawn_time 0x{rt:x} / is_alive 0x{al:x}: the game changed, revives are off (nothing is written)"
        )),
    }
    *cache = Some((rt, al, l));
    l
}

type GetPlayer = unsafe extern "C" fn(*mut std::ffi::c_void, usize) -> *mut u8;

/// 把一个阵亡玩家的剩余复活 tick 改小到 `ticks`（至少 1）。所有核对都过了才写，写完用游戏接口读回核对。
fn shorten_respawn(sim: &StableSim<'_>, player: usize, ticks: u64) -> Result<(u64, u64), &'static str> {
    let l = layout(sim).ok_or("no layout")?;
    let p = sim.get_player(player).ok_or("no such player")?;
    if p.is_alive() {
        return Err("alive");
    }
    let api = p.respawn_time() as u64;
    let ctx = raw_ctx(sim);
    unsafe {
        let st = (*ctx).state as *const usize;
        if st.is_null() {
            return Err("no state");
        }
        if *(st as *const u8).add(0x18) != 0 {
            return Err("read-only simulation");
        }
        let (world, wvt) = (*st, *st.add(1));
        if world == 0 || wvt == 0 {
            return Err("no world");
        }
        let slot = *((wvt + l.getp) as *const usize);
        if slot == 0 {
            return Err("no get_player");
        }
        let getp: GetPlayer = std::mem::transmute(slot);
        let pp = getp(world as *mut std::ffi::c_void, player);
        if pp.is_null() {
            return Err("player not found");
        }
        let tag = std::ptr::read_unaligned(pp.add(l.tag) as *const u64);
        let cur = std::ptr::read_unaligned(pp.add(l.val) as *const u64);
        if tag != 0 {
            return Err("not dead in memory");
        }
        if cur != api || cur == 0 {
            return Err("memory and the game disagree");
        }
        let new = cur.min(ticks.max(1));
        if new < cur {
            std::ptr::write_unaligned(pp.add(l.val) as *mut u64, new);
        }
        if p.respawn_time() as u64 != new {
            return Err("read back differs");
        }
        Ok((cur, new))
    }
}

// ===================== 原生效果：被动计数、R 的子弹 =====================

fn stack_name(caster: usize) -> String {
    format!("{STACK}:{caster}")
}

fn hit(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
        return;
    }
    let name = stack_name(me);
    let had = count_buff(sim, target, &name);
    let (proc_, keep) = next_hit(had);
    sim.entity_remove_buff(target, &name);
    for _ in 0..keep {
        sim.add_buff(target, &BuffV1::timed(&name, P_T));
    }
    if proc_ {
        sim.add_buff(me, &BuffV1::timed(P_GO, FLAG_T));
        if let Some(k) = counted("proc") {
            wlog(format!("{} THIRD HIT on #{target} #{k}", head(sim, me)));
        }
    }
}

struct HitFx;
impl StableEffectType for HitFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        hit(sim, caster, input);
    }
}

fn bullet(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    let Some(t) = sim.get_entity(target) else { return };
    if !t.is_alive() {
        return;
    }
    let (hp, max) = t.hp();
    let attack = sim.get_entity(me).map_or(0, |e| e.stat().attack);
    let d = bullet_damage(attack, hp, max);
    sim.deal_damage_typed(me, target, d, DamageTypeV1::Ad, AttackTypeV1::Skill);
    if let Some(k) = logged(sim, "bullet") {
        wlog(format!("{} BULLET on #{target} {hp}/{max}: {d} before armour (attack {attack}) #{k}", head(sim, me)));
    }
}

/// 他身上的 `r_lock:<id>`（0.2.6）：这次 R 锁定的英雄。
fn lock_name(id: usize) -> String {
    format!("{R_LOCK}:{id}")
}

fn locked_id(sim: &StableSim<'_>, me: usize) -> Option<usize> {
    let e = sim.get_entity(me)?;
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find_map(|b| {
        b.name().strip_prefix(R_LOCK)?.strip_prefix(':')?.parse().ok()
    })
}

/// 子弹该去的英雄：锁定的那个（活着、能选中、射程里），不然射程里血最少的敌方英雄（`release` 一样）；(id, 是不是锁定的)。
fn bullet_target(sim: &StableSim<'_>, me: usize) -> Option<(usize, bool)> {
    let e = sim.get_entity(me)?;
    let (team, my) = (e.team(), e.id());
    let reach2 = R_REACH * R_REACH;
    let ok = |t: &StableEntity<'_, '_>| {
        t.is_champion() && t.is_alive() && t.is_targetable() && t.team() != team && sim.distance_sq(my, t.id()) <= reach2
    };
    if let Some(id) = locked_id(sim, me) {
        if sim.get_entity(id).is_some_and(|t| ok(&t)) {
            return Some((id, true));
        }
    }
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|t| ok(t))
        .min_by_key(|t| {
            let (hp, max) = t.hp();
            hp * 1000 / max.max(1)
        })
        .map(|t| (t.id(), false))
}

/// 游戏自己的地图上的 [`bullet_end_on`]。
pub fn bullet_end(from: (f64, f64), to: (f64, f64)) -> (u64, u64) {
    bullet_end_on(Map::Native, from, to)
}

/// 子弹的终点：从他朝目标飞 R_REACH，到 `map` 的边就停在边上（方向不变）。
pub fn bullet_end_on(map: Map, from: (f64, f64), to: (f64, f64)) -> (u64, u64) {
    let (dx, dy) = (to.0 - from.0, to.1 - from.1);
    let d = (dx * dx + dy * dy).sqrt();
    let (ux, uy) = if d < 1.0 { (1.0, 0.0) } else { (dx / d, dy / d) };
    let r = R_REACH as f64;
    let end = map.extent();
    let room = |p: f64, u: f64| if u > 0.0 { (end - p) / (u * r) } else if u < 0.0 { -p / (u * r) } else { 1.0 };
    let t = room(from.0, ux).min(room(from.1, uy)).clamp(0.0, 1.0);
    ((from.0 + ux * r * t).round().max(0.0) as u64, (from.1 + uy * r * t).round().max(0.0) as u64)
}

/// 预判（0.2.7）：子弹以 `speed` 从 `me` 飞，目标在 `to`、每 tick 走 `v`：子弹到的时候他在哪（飞多久按距离算，迭代三次；
/// 最多往前算 LEAD_CAP；一 tick 走得比 V_MAX 还快是位移技能 / 闪现，子弹到之前就停了，不预判）。11-05 的日志：锁定的人
/// 68-74k 外每 tick 走 ~400，子弹朝他站的地方飞。
pub fn lead(me: (f64, f64), to: (f64, f64), v: (f64, f64), speed: f64) -> (f64, f64) {
    if speed <= 0.0 || v.0.hypot(v.1) > V_MAX {
        return to;
    }
    let mut p = to;
    for _ in 0..3 {
        let t = dist(me, p) / speed;
        let (mut dx, mut dy) = (v.0 * t, v.1 * t);
        let n = dx.hypot(dy);
        if n > LEAD_CAP {
            (dx, dy) = (dx * LEAD_CAP / n, dy * LEAD_CAP / n);
        }
        p = (to.0 + dx, to.1 + dy);
    }
    p
}

/// 一发子弹离锁定的人最近的一次（R MISS，0.2.7）：子弹 `t0` 那个 tick 从 `from` 出发朝 `end` 每 tick 飞 R_SPEED（出发那
/// tick 算第 0 步），每一步和他那个 tick 的位置（`track`：tick, 位置）比圆心距离；飞行中一个 tick 都没记到就是 None。
pub fn closest_pass(t0: usize, from: (f64, f64), end: (f64, f64), track: &[(usize, (f64, f64))]) -> Option<f64> {
    let len = dist(from, end);
    let u = if len < 1.0 { (0.0, 0.0) } else { ((end.0 - from.0) / len, (end.1 - from.1) / len) };
    let speed = R_SPEED as f64;
    let steps = (len / speed).ceil() as usize;
    (0..=steps)
        .filter_map(|k| {
            let s = (speed * k as f64).min(len);
            let b = (from.0 + u.0 * s, from.1 + u.1 * s);
            track.iter().find(|x| x.0 == t0 + k).map(|x| dist(b, x.1))
        })
        .min_by(f64::total_cmp)
}

fn vel_name(id: usize, v: (f64, f64)) -> String {
    format!("{R_VEL}:{id}:{}:{}", v.0.round() as i64, v.1.round() as i64)
}

fn parse_vel(name: &str) -> Option<(usize, (f64, f64))> {
    let mut it = name.strip_prefix(R_VEL)?.strip_prefix(':')?.split(':');
    let id = it.next()?.parse().ok()?;
    let vx: f64 = it.next()?.parse().ok()?;
    let vy: f64 = it.next()?.parse().ok()?;
    it.next().is_none().then_some((id, (vx, vy)))
}

fn path_name(t0: usize, from: (u64, u64), end: (u64, u64)) -> String {
    format!("{R_PATH}:{t0}:{}:{}:{}:{}", from.0, from.1, end.0, end.1)
}

/// (tick, from, end) of a bullet's `r_b` buff.
fn parse_path(name: &str) -> Option<(usize, (f64, f64), (f64, f64))> {
    let v: Vec<f64> = name.strip_prefix(R_PATH)?.strip_prefix(':')?.split(':').map(|x| x.parse().ok()).collect::<Option<_>>()?;
    (v.len() == 5).then(|| (v[0] as usize, (v[1], v[2]), (v[3], v[4])))
}

/// Buff names on him that start with `prefix:`.
fn names_on(sim: &StableSim<'_>, me: usize, prefix: &str) -> Vec<String> {
    let Some(e) = sim.get_entity(me) else { return Vec::new() };
    (0..e.buff_count())
        .filter_map(|i| e.buff_at(i))
        .map(|b| b.name().to_string())
        .filter(|n| n.strip_prefix(prefix).is_some_and(|r| r.starts_with(':')))
        .collect()
}

/// The walk the passive measured for `id` (his `r_v` buff), nothing for anyone else.
fn walk_of(sim: &StableSim<'_>, me: usize, id: usize) -> (f64, f64) {
    names_on(sim, me, R_VEL).iter().filter_map(|n| parse_vel(n)).find(|x| x.0 == id).map_or((0.0, 0.0), |x| x.1)
}

/// 一发恩怨相抵（0.2.6，副本里每一发的效果）：朝锁定的英雄放一个原生投射物（直线、R_W 的圆、R_SPEED、不穿透、打到第一个
/// 敌方单位走 `rhit`），他身上记一个 `r_shot`。0.2.7：朝他走到的地方（`lead`，被动量的速度），再记一个 `r_b`（子弹的路线）。
fn aim(sim: &mut StableSim<'_>, me: usize) {
    let Some(e) = sim.get_entity(me).filter(|e| e.is_alive()) else { return };
    let (team, at) = (e.team(), e.pos());
    let Some((id, locked)) = bullet_target(sim, me) else {
        if let Some(k) = logged(sim, "aim_none") {
            wlog(format!("{} R AIM: no enemy champion in reach, the bullet is lost #{k}", head(sim, me)));
        }
        return;
    };
    let Some(to) = sim.get_entity(id).map(|t| t.pos()) else { return };
    let from = (at.0 as f64, at.1 as f64);
    let v = walk_of(sim, me, id);
    let ahead = lead(from, (to.0 as f64, to.1 as f64), v, R_SPEED as f64);
    let end = bullet_end_on(map_here(sim), from, ahead);
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team,
        x: at.0,
        y: at.1,
        radius: R_W as u64,
        speed: R_SPEED,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: end.0,
        target_y: end.1,
        penetrate: false,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::Enemy.code(),
    };
    let ok = sim.spawn_projectile(R_BULLET, &format!("{ID}:rhit"), &spec);
    if ok {
        sim.add_buff(me, &BuffV1::timed(R_SHOT, R_BOOK_T));
        sim.add_buff(me, &BuffV1::timed(&path_name(sim.tick(), at, end), R_BOOK_T));
    }
    if let Some(k) = logged(sim, "aim") {
        let led = if v == (0.0, 0.0) {
            String::new()
        } else {
            format!(", he walks ({:.0}, {:.0}) a tick: led to ({:.0}, {:.0})", v.0, v.1, ahead.0, ahead.1)
        };
        wlog(format!("{} R AIM at #{id}{} ({}, {}) -> ({}, {}){led}{} #{k}", head(sim, me),
                     if locked { " (the lock)" } else { " (no lock in reach: the weakest)" }, to.0, to.1, end.0, end.1,
                     if ok { "" } else { ", spawn_projectile refused" }));
    }
}

/// 无所不用的第 3 下（数据的 `proc`，数据的命中里由 `p_go` 触发；本包的子弹自己打）：P_DMG + P_RATIO% AD，命中画面和声音；
/// 打中英雄且 `p_scd` 不在：护盾 P_SH_AMT + P_SH_R% AD，P_SH_T tick，挂 `p_sh` 和 `p_scd`。
fn dirty_proc(sim: &mut StableSim<'_>, me: usize, target: usize) {
    let attack = sim.get_entity(me).map_or(0, |e| e.stat().attack);
    sim.deal_damage_typed(me, target, P_DMG + P_RATIO * attack / 100, DamageTypeV1::Ad, AttackTypeV1::Skill);
    let input = InputTargetV1::target(target);
    sim.play_view_effect(VIEW_P_HIT, me, &input, 0, 0, 0);
    sim.play_sfx(VIEW_P_HIT, me, &input);
    let champ = sim.get_entity(target).is_some_and(|t| t.is_champion());
    if champ && !has_buff(sim, me, P_SCD) {
        sim.add_buff(me, &BuffV1::timed(P_SCD, P_SCD_T));
        sim.entity_add_shield(me, P_SH_AMT + P_SH_R * attack / 100, P_SH_T);
        sim.entity_remove_buff(me, P_SH);
        sim.add_buff(me, &BuffV1::timed(P_SH, P_SH_T));
    }
}

/// R 的子弹打中（0.2.6，以前是数据的 r_bullet）：恩怨相抵的伤害、命中画面和声音、无所不用计数，第 3 下由本包打出（数据的
/// `p_go` 这里没人读）；他身上记一个 `r_onlock`（打中锁定的）或 `r_onother`。
fn r_hit(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        if let Some(k) = logged(sim, "rhit_kind") {
            wlog(format!("{} R HIT with an input of kind {} (no target): nothing dealt #{k}", head(sim, me), input.kind));
        }
        return;
    }
    let target = input.target_id;
    if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
        return;
    }
    bullet(sim, me, input);
    sim.play_view_effect(VIEW_R_HIT, me, &input, 0, 0, 0);
    sim.play_sfx(VIEW_R_HIT, me, &input);
    hit(sim, me, input);
    if has_buff(sim, me, P_GO) {
        sim.entity_remove_buff(me, P_GO);
        dirty_proc(sim, me, target);
    }
    let on_lock = locked_id(sim, me) == Some(target);
    sim.add_buff(me, &BuffV1::timed(if on_lock { R_ONLOCK } else { R_ONOTHER }, R_BOOK_T));
}

struct AimFx;
impl StableEffectType for AimFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        aim(sim, caster);
    }
}

struct RHitFx;
impl StableEffectType for RHitFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        r_hit(sim, caster, input);
    }
}

// ===================== 骄行荡寇：绕钩点荡（真正的弧线 + 绳子） =====================

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 游戏自己的地图上的 [`swing_plan_on`]。
pub fn swing_plan(me: (f64, f64), target: (f64, f64)) -> ((f64, f64), f64, f64) {
    swing_plan_on(Map::Native, me, target)
}

/// 荡的安排：(钩点, 起始角, 方向 ±1)。钩点在他身边 ROPE_R 处、偏离指向目标的方向 HOOK_OFF（两边各试一次），绕钩点转
/// SWEEP；钩点在他上方（屏幕上靠上、离镜头远的一侧，绳子从手往上拉，像荡秋千），其中选荡完离目标最近的那种（一样近时选钩点靠地图中间的）。英雄联盟里钩点是墙，TFM2 的地图没有这种墙，就挂在这一点。
/// 地图中间是 `map` 的中间。
pub fn swing_plan_on(map: Map, me: (f64, f64), target: (f64, f64)) -> ((f64, f64), f64, f64) {
    let mid = map.center();
    let (dx, dy) = (target.0 - me.0, target.1 - me.1);
    let d = (dx * dx + dy * dy).sqrt();
    let base = if d < 1.0 { 0.0 } else { dy.atan2(dx) };
    let mut best: Option<(f64, (f64, f64), f64, f64)> = None;
    for side in [1.0, -1.0] {
        let h = base + side * HOOK_OFF;
        let a = (me.0 + ROPE_R * h.cos(), me.1 + ROPE_R * h.sin());
        let a0 = (me.1 - a.1).atan2(me.0 - a.0);
        for dir in [1.0, -1.0] {
            let th = a0 + dir * SWEEP;
            let end = (a.0 + ROPE_R * th.cos(), a.1 + ROPE_R * th.sin());
            // the hook above him on the screen (a smaller y: farther from the camera) - the rope rises from his hand like a
            // swing's; below him it lay along his body down to his feet (「看着这么奇怪」)
            let below = if a.1 > me.1 { 100_000.0 } else { 0.0 };
            let score = dist(end, target) + below + 0.1 * dist(a, mid);
            if best.is_none_or(|b| score < b.0) {
                best = Some((score, a, a0, dir));
            }
        }
    }
    let (_, a, a0, dir) = best.unwrap();
    (a, a0, dir)
}

/// 游戏自己的地图上的 [`swing_at_on`]。
pub fn swing_at(a: (f64, f64), a0: f64, dir: f64, age: usize) -> (f64, f64) {
    swing_at_on(Map::Native, a, a0, dir, age)
}

/// 荡了 age tick 时他在哪（夹在 `map` 里，离边 MAP_LO）。
pub fn swing_at_on(map: Map, a: (f64, f64), a0: f64, dir: f64, age: usize) -> (f64, f64) {
    let th = a0 + dir * SWEEP * (age.min(SWING_T) as f64) / SWING_T as f64;
    let hi = map.extent() - MAP_LO;
    ((a.0 + ROPE_R * th.cos()).clamp(MAP_LO, hi), (a.1 + ROPE_R * th.sin()).clamp(MAP_LO, hi))
}

/// [`swing_at_on`] 挨着峡谷的墙：弧线上这一刻的点站不住（`ok` 说不行：运行时是 `stand_ok`，峡谷的墙往外长一格；游戏自己的
/// 地图上总是行）就是 None：荡到这里为止、松手，他停在上一个能站的地方。
pub fn swing_step(map: Map, a: (f64, f64), a0: f64, dir: f64, age: usize, ok: impl Fn((f64, f64)) -> bool)
    -> Option<(f64, f64)> {
    let p = swing_at_on(map, a, a0, dir, age);
    ok(p).then_some(p)
}

fn sw_name(a: (f64, f64), a0: f64, dir: f64, t0: usize) -> String {
    format!(
        "{SW}:{}:{}:{}:{}:{t0}",
        a.0.round() as i64,
        a.1.round() as i64,
        (a0 * 1000.0).round() as i64,
        if dir > 0.0 { 1 } else { -1 }
    )
}

fn parse_sw(name: &str) -> Option<((f64, f64), f64, f64, usize)> {
    let rest = name.strip_prefix(SW)?.strip_prefix(':')?;
    let v: Vec<&str> = rest.split(':').collect();
    if v.len() != 5 {
        return None;
    }
    let ax: f64 = v[0].parse().ok()?;
    let ay: f64 = v[1].parse().ok()?;
    let a0: f64 = v[2].parse::<f64>().ok()? / 1000.0;
    let dir: f64 = v[3].parse().ok()?;
    let t0: usize = v[4].parse().ok()?;
    Some(((ax, ay), a0, dir, t0))
}

/// E 甩钩（数据在 E 起手第 2 tick 调，输入 = E 的目标）：定钩点，在他身上挂
/// `league_akshan_sw:<钩点x>:<钩点y>:<起始角x1000>:<方向>:<tick>`，之后每 tick 由被动荡他、画绳子。
fn swing_start(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(e) = sim.get_entity(me) else { return };
    let here = e.pos();
    let old: Vec<String> = (0..e.buff_count())
        .filter_map(|i| e.buff_at(i))
        .map(|b| b.name().to_string())
        .filter(|n| n.starts_with(SW))
        .collect();
    let target = match InputTargetKindV1::from_code(input.kind) {
        Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|t| t.pos()),
        Some(InputTargetKindV1::Pos) => Some((input.x, input.y)),
        _ => None,
    };
    let Some(t) = target else { return };
    let (a, a0, dir) = swing_plan_on(map_here(sim), (here.0 as f64, here.1 as f64), (t.0 as f64, t.1 as f64));
    for n in old {
        sim.entity_remove_buff(me, &n);
    }
    let name = sw_name(a, a0, dir, sim.tick());
    sim.add_buff(me, &BuffV1::timed(&name, SWING_T + 30));
    if let Some(k) = logged(sim, "swing") {
        // 0.2.7: already held as the swing starts (the E cast into a root / a grounding / a knock-back)?
        let held = if hard_cc(sim, me) { format!(", already held: {}", cc_text(sim, me)) } else { String::new() };
        wlog(format!(
            "{} SWING round ({:.0}, {:.0}) from ({}, {}) toward #{}{held} #{k}",
            head(sim, me),
            a.0,
            a.1,
            here.0,
            here.1,
            input.target_id
        ));
    }
}

struct SwingFx;
impl StableEffectType for SwingFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        swing_start(sim, caster, input);
    }
}

struct NoopFx;
impl StableEffectType for NoopFx {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

fn hard_cc(sim: &StableSim<'_>, id: usize) -> bool {
    let Some(e) = sim.get_entity(id) else { return false };
    (0..e.cc_count()).filter_map(|i| e.cc_at(i)).any(|c| HARD.iter().any(|k| k.code() == c.kind))
}

/// One crowd-control entry for the log: its kind and ticks left, a ForceMove's speed, a taunt's taunter, an animation's
/// name ("ForceMove 10 speed 3000", "Animation 6 skill2").
pub fn cc_entry(c: &CcV1) -> String {
    let kind = CcKindV1::from_code(c.kind);
    let name = kind.map_or_else(|| format!("kind {}", c.kind), |k| format!("{k:?}"));
    let more = match kind {
        Some(CcKindV1::ForceMove) => format!(" speed {}", c.speed),
        Some(CcKindV1::Taunt) => format!(" by #{}", c.target),
        Some(CcKindV1::Animation) => format!(" {}", c.name()),
        _ => String::new(),
    };
    format!("{name} {}{more}", c.tick)
}

/// Every crowd-control entry on `id` (0.2.7, for SWING: the 11-05 logs cut 221 swings, 78 of them 0-3 ticks in -
/// an enemy's or his own?).
fn cc_text(sim: &StableSim<'_>, id: usize) -> String {
    let Some(e) = sim.get_entity(id) else { return "-".to_string() };
    let all: Vec<String> = (0..e.cc_count()).filter_map(|i| e.cc_at(i)).map(|c| cc_entry(&c)).collect();
    if all.is_empty() { "-".to_string() } else { all.join(", ") }
}

/// 一节绳子：在他手的高度、他和钩点的正中，朝钩点（游戏把图转向它飞的方向），1 tick 就到头。
fn rope(sim: &mut StableSim<'_>, me: usize, at: (f64, f64), a: (f64, f64)) -> bool {
    let m = ((at.0 + a.0) / 2.0, (at.1 + a.1) / 2.0 - HAND);
    let (dx, dy) = (a.0 - at.0, a.1 - at.1);
    let d = (dx * dx + dy * dy).sqrt().max(1.0);
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team: sim.get_entity(me).map_or(0, |e| e.team()),
        x: m.0.round().max(0.0) as u64,
        y: m.1.round().max(0.0) as u64,
        radius: 1_000,
        speed: 1_000,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: (m.0 + dx / d * 1_000.0).round().max(0.0) as u64,
        target_y: (m.1 + dy / d * 1_000.0).round().max(0.0) as u64,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    sim.spawn_projectile(ROPE, &format!("{ID}:noop"), &spec)
}

// ===================== 被动：恶徒、复活、E 刷新、R 提前开火 =====================

#[derive(Clone, Debug, Default)]
struct Scoundrel {
    until: usize,
    /// 被他杀死的队友（玩家编号）。
    victims: Vec<usize>,
}

#[derive(Clone, Default)]
struct Rogue {
    /// 击杀记录读到第几条。
    seen: usize,
    /// 恶徒：敌方玩家编号 -> 标记。
    marks: BTreeMap<usize, Scoundrel>,
    /// 刚复活的队友（玩家编号, 等到第几 tick）：他站起来的那一 tick 在他身上放复活的光。
    back: Vec<(usize, usize)>,
    /// 上一 tick 在引导 R；引导结束后记 R DONE 的 tick（0.2.6）。
    r_was: bool,
    r_done_at: Option<usize>,
    /// 0.2.7, while R is on: where the champion the next bullet goes to stood over the last TRACK_T ticks (tick, id, at) -
    /// his walk, written on Akshan as `r_v` for the bullets to lead by - and the lock's every position (tick, at), for the
    /// R MISS line.
    aim_track: Vec<(usize, usize, (f64, f64))>,
    lock_track: Vec<(usize, (f64, f64))>,
}

/// The walk per tick over a track (oldest first) of one unit: (newest - oldest) / ticks between; none over less than a tick.
pub fn walk(track: &[(usize, usize, (f64, f64))]) -> (f64, f64) {
    match (track.first(), track.last()) {
        (Some(a), Some(b)) if b.0 > a.0 => {
            let dt = (b.0 - a.0) as f64;
            ((b.2 .0 - a.2 .0) / dt, (b.2 .1 - a.2 .1) / dt)
        }
        _ => (0.0, 0.0),
    }
}

/// 击杀记录里的“位置”就是分路（LaneV1 的编号）：按队伍和分路找玩家编号。
fn player_by_lane(sim: &StableSim<'_>, team: usize, lane: u32) -> Option<usize> {
    (0..sim.player_count()).filter_map(|i| sim.player_at(i)).find(|p| p.team() == team && p.lane().map(|l| l.code()) == Some(lane)).map(|p| p.id())
}

impl Rogue {
    fn read_kills(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let n = sim.kill_log_count();
        if self.seen > n {
            self.seen = 0; // a new match in a reused passive
        }
        let Some(mine) = sim.get_player(player) else { return };
        let (my_team, my_lane) = (mine.team(), mine.lane().map(|l| l.code()));
        let now = sim.tick();
        while self.seen < n {
            let Some(k) = sim.kill_log_at(self.seen) else { break };
            self.seen += 1;
            let killer_team = k.killer_team;
            let victim_team = 1 - killer_team.min(1);
            let Some(victim) = player_by_lane(sim, victim_team, k.killed_position) else {
                if let Some(c) = logged(sim, "nolane") {
                    wlog(format!("{} kill log #{}: no player in lane {} of team {victim_team} #{c}", head(sim, me), self.seen - 1, k.killed_position));
                }
                continue;
            };
            let killer = player_by_lane(sim, killer_team, k.killer_position);
            let recent = now <= k.tick + 3;
            if victim_team == my_team {
                // an ally down (not me): his killer becomes a Scoundrel
                if victim == player {
                    continue;
                }
                if let Some(s) = killer {
                    let m = self.marks.entry(s).or_default();
                    m.until = k.tick + MARK_T;
                    if !m.victims.contains(&victim) {
                        m.victims.push(victim);
                    }
                    if let Some(e) = sim.get_player(s).and_then(|p| p.champion()).map(|e| e.id()) {
                        sim.entity_remove_buff(e, MARK);
                        sim.add_buff(e, &BuffV1::timed(MARK, MARK_T.saturating_sub(now - k.tick.min(now))));
                        if recent {
                            sim.play_sfx(SFX_MARK, me, &InputTargetV1::target(e));
                        }
                    }
                    // the match on screen in full, the presims capped (0.2.4: ~1.9k MARK lines a launch, 2026-11-01)
                    if on_screen(sim).is_some() || counted("mark").is_some() {
                        wlog(format!("{} MARK player {s} killed ally {victim} (victims {:?})", head(sim, me), m.victims));
                    }
                }
            } else {
                // an enemy down: my takedown?
                let assists: Vec<u32> = k.assist_positions.iter().take(k.assist_count as usize).copied().collect();
                let mine_kill = killer_team == my_team
                    && my_lane.is_some_and(|l| k.killer_position == l || assists.contains(&l));
                if !mine_kill || !recent {
                    continue;
                }
                // Heroic Swing: a champion takedown refreshes it to E_LEFT ticks
                if let Some(cd) = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Skill2)) {
                    if cd.remaining > E_LEFT {
                        sim.entity_reduce_cooldown(me, SkillSlotV1::Skill2, cd.remaining - E_LEFT);
                        if let Some(c) = logged(sim, "refresh") {
                            wlog(format!("{} REFRESH E {} -> {E_LEFT} (takedown of player {victim}) #{c}", head(sim, me), cd.remaining));
                        }
                    }
                }
                if let Some(m) = self.marks.remove(&victim) {
                    sim.player_add_gold(player, GOLD);
                    sim.play_sfx(SFX_GOLD, me, &InputTargetV1::target(me));
                    if let Some(e) = sim.get_player(victim).and_then(|p| p.champion()).map(|e| e.id()) {
                        sim.entity_remove_buff(e, MARK);
                    }
                    for v in m.victims {
                        let dead = sim.get_player(v).is_some_and(|p| !p.is_alive());
                        if !dead {
                            wlog(format!("{} REVIVE player {v}: already back", head(sim, me)));
                            continue;
                        }
                        match shorten_respawn(sim, v, REVIVE_T) {
                            Ok((was, now_)) => {
                                sim.play_sfx(SFX_REVIVE, me, &InputTargetV1::target(me));
                                sim.play_view_effect(VIEW_REVIVE, me, &InputTargetV1::target(me), 0, 0, 0);
                                self.back.push((v, now + BACK_WAIT));
                                wlog(format!(
                                    "{} REVIVE player {v}: Scoundrel {victim} down, respawn {was} -> {now_} ticks",
                                    head(sim, me)
                                ))
                            }
                            Err(why) => wlog(format!("{} REVIVE player {v} REFUSED: {why}", head(sim, me))),
                        }
                    }
                }
            }
        }
        // marks run out
        self.marks.retain(|_, m| m.until > now);
        // a revived ally standing again: the beam on him
        let mut left = Vec::new();
        for (v, until) in std::mem::take(&mut self.back) {
            match sim.get_player(v).filter(|p| p.is_alive()).and_then(|p| p.champion()).map(|e| e.id()) {
                Some(e) => {
                    sim.play_view_effect(VIEW_REVIVE, e, &InputTargetV1::target(e), 0, 0, 0);
                    sim.play_sfx(SFX_REVIVE, e, &InputTargetV1::target(e));
                    wlog(format!("{} BACK player {v}: the revive's beam on him", head(sim, me)));
                    // the screen's match: the big line as he stands up (banner.rs)
                    if let Some((m, s)) = on_screen(sim) {
                        let name = |id: usize| sim.get_entity(id).and_then(|x| x.name());
                        banner::note_revive(banner::Banner { m, s, tick: now, akshan: name(me).unwrap_or_else(|| ID.to_string()),
                                                             ally: name(e).unwrap_or_default() });
                    }
                }
                None if now < until => left.push((v, until)),
                None => {}
            }
        }
        self.back = left;
    }

    /// Moving toward the Scoundrels: move speed while one lives within HASTE_R (League: +80-120 toward them).
    fn haste(&self, sim: &mut StableSim<'_>, me: usize) {
        if sim.tick() % 30 != 0 || self.marks.is_empty() {
            return;
        }
        let r2 = HASTE_R * HASTE_R;
        let near = self.marks.keys().filter_map(|&s| sim.get_player(s).and_then(|p| p.champion())).any(|e| {
            e.is_alive() && sim.distance_sq(me, e.id()) <= r2
        });
        if near {
            let mut b = BuffV1::timed(W_HASTE, 31);
            b.move_speed_mult = HASTE;
            sim.entity_remove_buff(me, W_HASTE);
            sim.add_buff(me, &b);
        }
    }

    /// 这次 R 的账（0.2.6）：引导时把锁定的英雄（带 `R_SIGHT` 的敌方英雄）记在他身上（`r_lock:<id>`，子弹朝它飞）；引导结束
    /// R_DONE_WAIT tick 后（最后一发也落了）记一行 R DONE：发了几发、几发打中锁定的、几发打中别人、锁定的还活着没，再把账摘掉。
    fn r_book(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        let chan = has_buff(sim, me, R_CHAN);
        if chan {
            if locked_id(sim, me).is_none() {
                let team = sim.get_entity(me).map_or(usize::MAX, |e| e.team());
                let lock = (0..sim.entity_count())
                    .filter_map(|i| sim.entity_at(i))
                    .filter(|u| u.team() != team && u.is_champion() && u.is_alive() && has_buff(sim, u.id(), R_SIGHT))
                    .map(|u| (u.id(), sim.distance_sq(me, u.id())))
                    .min_by_key(|u| u.1);
                if let Some((id, _)) = lock {
                    sim.add_buff(me, &BuffV1::timed(&lock_name(id), R_BOOK_T));
                }
            }
            self.r_done_at = None;
        } else if self.r_was {
            self.r_done_at = Some(now + R_DONE_WAIT);
        }
        self.r_was = chan;
        if chan || self.r_done_at.is_some() {
            self.track(sim, me, now);
        }
        if !self.r_done_at.is_some_and(|t| now >= t) {
            return;
        }
        self.r_done_at = None;
        let (shots, on, other) = (count_buff(sim, me, R_SHOT), count_buff(sim, me, R_ONLOCK), count_buff(sim, me, R_ONOTHER));
        let lost = shots.saturating_sub(on + other);
        let lock = locked_id(sim, me);
        let state = match lock.and_then(|id| sim.get_entity(id)) {
            Some(t) if t.is_alive() => {
                let (hp, max) = t.hp();
                format!("alive {hp}/{max}")
            }
            Some(_) => "DEAD".to_string(),
            None => "gone".to_string(),
        };
        let lock_txt = lock.map_or("-".to_string(), |i| i.to_string());
        if let Some(k) = logged(sim, "r_done") {
            wlog(format!("{} R DONE #{k}: {shots} fired, {on} on the lock #{lock_txt}, {other} on others, {lost} lost; the lock {state}",
                         head(sim, me)));
        }
        let paths = names_on(sim, me, R_PATH);
        // 0.2.7: a bullet lost - how near each came to the lock, centre to centre on a tick (rare: only with a loss)
        if lost > 0 && lock.is_some() {
            if let Some(k) = logged(sim, "r_miss") {
                let mut flights: Vec<(usize, (f64, f64), (f64, f64))> = paths.iter().filter_map(|n| parse_path(n)).collect();
                flights.sort_by_key(|f| f.0);
                let passes: Vec<String> = flights
                    .iter()
                    .map(|&(t0, from, end)| closest_pass(t0, from, end, &self.lock_track).map_or("-".to_string(), |d| format!("{d:.0}")))
                    .collect();
                wlog(format!("{} R MISS #{k}: {lost} of {shots} lost; each bullet's closest pass to the lock #{lock_txt} [{}] \
                              (a hit needs {R_W:.0}; the lock {state})", head(sim, me), passes.join(", ")));
            }
        }
        for name in [R_SHOT, R_ONLOCK, R_ONOTHER] {
            sim.entity_remove_buff(me, name);
        }
        for name in paths.iter().chain(names_on(sim, me, R_VEL).iter()) {
            sim.entity_remove_buff(me, name);
        }
        if let Some(id) = lock {
            sim.entity_remove_buff(me, &lock_name(id));
        }
        self.aim_track.clear();
        self.lock_track.clear();
    }

    /// While R is on (0.2.7): the lock's position this tick (for R MISS), and the walk of the champion the next bullet
    /// goes to over the last TRACK_T ticks, on Akshan as `r_v:<id>:<vx>:<vy>` (`aim` leads by it, `release` too).
    fn track(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        // a reused passive in a new match: nothing from the last one
        self.aim_track.retain(|x| x.0 <= now);
        self.lock_track.retain(|x| x.0 <= now);
        let at = |sim: &StableSim<'_>, id: usize| {
            sim.get_entity(id).filter(|t| t.is_alive()).map(|t| {
                let p = t.pos();
                (p.0 as f64, p.1 as f64)
            })
        };
        if let Some(p) = locked_id(sim, me).and_then(|id| at(sim, id)) {
            if self.lock_track.last().is_none_or(|x| x.0 < now) {
                self.lock_track.push((now, p));
            }
        }
        let next = bullet_target(sim, me).and_then(|(id, _)| at(sim, id).map(|p| (id, p)));
        let name = match next {
            Some((id, p)) => {
                self.aim_track.retain(|x| x.1 == id && now - x.0 <= TRACK_T && x.0 < now);
                self.aim_track.push((now, id, p));
                Some(vel_name(id, walk(&self.aim_track)))
            }
            None => {
                self.aim_track.clear();
                None
            }
        };
        let old = names_on(sim, me, R_VEL);
        if old.len() == 1 && name.as_ref() == old.first() {
            return;
        }
        for n in old {
            sim.entity_remove_buff(me, &n);
        }
        if let Some(n) = name {
            sim.add_buff(me, &BuffV1::timed(&n, R_BOOK_T));
        }
    }

    /// The walk this passive measured for `id` (none for anyone else).
    fn walk_of(&self, id: usize) -> (f64, f64) {
        if self.aim_track.last().is_some_and(|x| x.1 == id) {
            walk(&self.aim_track)
        } else {
            (0.0, 0.0)
        }
    }

    /// The lock comes off the enemy champions once he fires (r_open) or the channel is over (no r_chan).
    fn sight_off(&self, sim: &mut StableSim<'_>, me: usize) {
        if has_buff(sim, me, R_CHAN) && !has_buff(sim, me, R_OPEN) {
            return;
        }
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let locked: Vec<usize> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_champion() && has_buff(sim, u.id(), R_SIGHT))
            .map(|u| u.id())
            .collect();
        for id in locked {
            sim.entity_remove_buff(id, R_SIGHT);
        }
    }

    /// While R channels: fire early when the stored bullets kill the champion they go to (the one the data locked,
    /// `R_SIGHT`, else the weakest in reach) - after his armour and the enemies on the line (`lethal`) - or he is
    /// leaving the reach.
    fn release(&self, sim: &mut StableSim<'_>, me: usize) {
        if !has_buff(sim, me, R_CHAN) || has_buff(sim, me, R_OPEN) || has_buff(sim, me, R_FIRE) {
            return;
        }
        let n = STORED.iter().filter(|s| has_buff(sim, me, s)).count();
        if n == 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let (team, attack, at) = (e.team(), e.stat().attack, e.pos());
        let reach2 = R_REACH * R_REACH;
        // (id, d2) of the locked champion; (id, hp ratio, d2) of the weakest
        let mut locked: Option<(usize, u64)> = None;
        let mut weakest: Option<(usize, usize, u64)> = None;
        for i in 0..sim.entity_count() {
            let Some(t) = sim.entity_at(i) else { continue };
            if !t.is_champion() || !t.is_alive() || t.team() == team {
                continue;
            }
            let d2 = sim.distance_sq(me, t.id());
            if d2 > reach2 {
                continue;
            }
            if locked.is_none() && has_buff(sim, t.id(), R_SIGHT) {
                locked = Some((t.id(), d2));
            }
            let (hp, max) = t.hp();
            let ratio = hp * 1000 / max.max(1);
            if weakest.is_none_or(|b| ratio < b.1) {
                weakest = Some((t.id(), ratio, d2));
            }
        }
        let Some((id, d2)) = locked.or(weakest.map(|w| (w.0, w.2))) else { return };
        let body = |u: &StableEntity<'_, '_>| {
            let (hp, max) = u.hp();
            let (x, y) = u.pos();
            Body { id: u.id(), at: (x as f64, y as f64), r: u.radius() as f64, hp, shield: u.shield(), max,
                   armor: u.stat().defence }
        };
        let Some(him) = sim.get_entity(id).map(|t| body(&t)) else { return };
        // every enemy unit on the way takes a bullet first: minions, monsters, towers, other champions - on the line to
        // where the bullets meet him (0.2.7: they lead him)
        let others: Vec<Body> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.id() != id && u.is_alive() && u.team() != team && u.is_targetable())
            .map(|u| body(&u))
            .collect();
        let from = (at.0 as f64, at.1 as f64);
        let blockers = on_line(from, lead(from, him.at, self.walk_of(id), R_SPEED as f64), &others);
        let kill = lethal(attack, &him, n, &blockers);
        let leaving = d2 * 100 >= reach2 * 85;
        if kill || leaving {
            sim.add_buff(me, &BuffV1::timed(R_FIRE, FIRE_T));
            if let Some(k) = logged(sim, "fire") {
                let why = if kill { "lethal" } else { "leaving" };
                let dmg = armoured_volley(attack, &him, n);
                let line = if blockers.is_empty() {
                    "line clear".to_string()
                } else {
                    format!("{} on the line ({})", blockers.len(),
                            blockers.iter().map(|b| format!("#{} {}/{}", b.id, b.hp, b.max)).collect::<Vec<_>>().join(", "))
                };
                wlog(format!(
                    "{} R FIRE early ({why}): {n} stored, #{id}{} hp+shield {} vs {dmg} after armour {}, {line} #{k}",
                    head(sim, me),
                    if locked.is_some() { " (locked)" } else { "" },
                    him.hp + him.shield,
                    him.armor
                ));
            }
        }
    }
}

/// 每 tick：在荡就把他放到弧线上这一刻的位置、画一节绳子；荡完、被硬控就松手。
fn swing_tick(sim: &mut StableSim<'_>, me: usize) {
    let Some(e) = sim.get_entity(me) else { return };
    let mark = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).find(|n| n.starts_with(SW));
    let Some(name) = mark else { return };
    let Some((a, a0, dir, t0)) = parse_sw(&name) else {
        sim.entity_remove_buff(me, &name);
        return;
    };
    let age = sim.tick().saturating_sub(t0);
    if age > SWING_T || hard_cc(sim, me) {
        // 0.2.7: which crowd control (221 cuts in the 11-05 logs, 78 of them 0-3 ticks in), capped like the other lines
        let cut = (age <= SWING_T).then(|| cc_text(sim, me));
        sim.entity_remove_buff(me, &name);
        if let Some(cc) = cut {
            if let Some(k) = logged(sim, "swing_cut") {
                wlog(format!("{} SWING cut by crowd control at {age}: {cc} #{k}", head(sim, me)));
            }
        }
        return;
    }
    let map = map_here(sim);
    // 峡谷上弧线的这一点站不住（离墙比峡谷的寻路允许的近）就荡到这里为止、松手：他停在上一个能站的地方，不进墙
    // （游戏自己的地图上 stand_ok 总是 true，照旧荡满）
    let Some(p) = swing_step(map, a, a0, dir, age, |q| stand_ok(map, q)) else {
        sim.entity_remove_buff(me, &name);
        if let Some(k) = logged(sim, "swing_wall") {
            wlog(format!("{} SWING stopped at the Rift's wall at {age} #{k}", head(sim, me)));
        }
        return;
    };
    sim.entity_set_pos(me, p.0.round() as u64, p.1.round() as u64);
    if !rope(sim, me, p, a) {
        if let Some(k) = logged(sim, "rope_refused") {
            wlog(format!("{} ROPE refused by spawn_projectile #{k}", head(sim, me)));
        }
    }
}

impl StablePassive for Rogue {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        if let Some((m, s)) = on_screen(sim).filter(|_| sim.tick() % 60 == 0) {
            banner::note_view(m, s);
        }
        swing_tick(sim, me);
        self.read_kills(sim, player, me);
        self.haste(sim, me);
        self.r_book(sim, me);
        self.release(sim, me);
        self.sight_off(sim, me);
    }
}

// ===================== AI：什么时候放 R =====================

/// The AI is still recalling (game 0.6.5 decides when to go home and buy): its last order was a Return - it orders only
/// on its judgement ticks, a Return again while the recall lasts, nothing in between - and any other order ends it
/// (league_ult_press 0.5.0's rule).
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// How much farther from a champion the AI's walk must end to be a retreat (league_ult_press's `HOLD_AWAY`).
pub const AWAY: f64 = 10_000.0;

/// The AI walks away from `to` this tick (a retreat, a disperse from a lost objective): its Move ends more than `AWAY`
/// farther from it than the champion stands now.
pub fn walking_away(base: Option<InputV1>, me: (f64, f64), to: (f64, f64)) -> bool {
    let d = |a: (f64, f64), b: (f64, f64)| ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt();
    base.is_some_and(|b| b.kind == InputKindV1::Move.code() && d((b.x as f64, b.y as f64), to) > d(me, to) + AWAY)
}

#[derive(Clone, Default)]
struct UltAi {
    last_log: Option<usize>,
    /// the AI is recalling (`still_recalling`)
    recalling: bool,
}

fn ult_input(id: usize) -> InputV1 {
    InputV1::action(InputKindV1::Ult, InputTargetV1::target(id))
}

/// (想打的人, 他是不是被挡住) 由 AI 钩子挑：射程里生命比例最低、≤ R_LOW% 或存满就打得死的敌方英雄；身边 R_SAFE 内有敌方英雄、
/// 自己生命 < 40% 时不放。
fn pick_target(sim: &StableSim<'_>, me: &StableEntity<'_, '_>) -> Result<usize, &'static str> {
    let (my, team) = (me.id(), me.team());
    let (hp, max) = me.hp();
    if hp * 100 < max * 40 {
        return Err("own health below 40%");
    }
    let (safe2, range2) = (R_SAFE * R_SAFE, R_RANGE * R_RANGE);
    let attack = me.stat().attack;
    let mut best: Option<(usize, usize)> = None;
    for i in 0..sim.entity_count() {
        let Some(t) = sim.entity_at(i) else { continue };
        if !t.is_champion() || !t.is_alive() || t.team() == team {
            continue;
        }
        let d2 = sim.distance_sq(my, t.id());
        if d2 <= safe2 {
            return Err("an enemy champion right next to him");
        }
        if d2 > range2 || !t.is_targetable() {
            continue;
        }
        let (th, tm) = t.hp();
        let low = th * 100 <= tm * R_LOW || volley(attack, th + t.shield(), tm, STORED.len()) >= th + t.shield();
        let ratio = th * 1000 / tm.max(1);
        if low && best.is_none_or(|b| ratio < b.1) {
            best = Some((t.id(), ratio));
        }
    }
    best.map(|b| b.0).ok_or("no wounded champion in range")
}

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
        let wants_ult = base.is_some_and(|b| b.kind == InputKindV1::Ult.code());
        // game 0.6.5's AI decides when to recall (and buy): the quiet ticks of a recall are busy too
        self.recalling = still_recalling(self.recalling, base);
        let busy = self.recalling || base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Return))
        });
        let read = {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            let me = pl.champion().filter(|e| e.is_alive())?;
            let ready = pl.level() >= ULT_LEVEL && me.cooldown(SkillSlotV1::Ult).is_some_and(|c| c.unlocked && c.remaining == 0);
            let channeling = has_buff(&sim, me.id(), R_CHAN);
            let line = head(&sim, me.id());
            let pick = pick_target(&sim, &me);
            // the target's spot: a channel he starts himself waits while the AI walks away from it (0.6.5's retreats)
            let away = pick.as_ref().ok().and_then(|&t| sim.get_entity(t)).is_some_and(|t| {
                let (p, q) = (me.pos(), t.pos());
                walking_away(base, (p.0 as f64, p.1 as f64), (q.0 as f64, q.1 as f64))
            });
            (pick, ready, channeling, me.pos(), line, away)
        };
        let (pick, ready, channeling, my_pos, line, away) = read;
        if channeling {
            return None;
        }
        match pick {
            Ok(id) if ready && (wants_ult || (!busy && !away)) => {
                let input = ult_input(id);
                if ctx.is_valid_input(&input) {
                    if self.last_log.is_none_or(|t0| tick >= t0 + 60) {
                        self.last_log = Some(tick);
                        if line.starts_with("[view") || counted("r_cast").is_some() {
                            wlog(format!("{line} R CAST on #{id} ({})", if wants_ult { "the AI's R, retargeted" } else { "pressed" }));
                        }
                    }
                    return Some(input);
                }
                if wants_ult {
                    Some(InputV1::move_to(my_pos.0, my_pos.1))
                } else {
                    None
                }
            }
            Err(why) if wants_ult => {
                if self.last_log.is_none_or(|t0| tick >= t0 + LOG_EVERY) {
                    self.last_log = Some(tick);
                    wlog(format!("{line} R HELD: {why}"));
                }
                let target = base.and_then(|b| {
                    (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
                });
                if let Some(t) = target {
                    let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                    if ctx.is_valid_input(&attack) {
                        return Some(attack);
                    }
                }
                Some(InputV1::move_to(my_pos.0, my_pos.1))
            }
            _ if wants_ult => Some(InputV1::move_to(my_pos.0, my_pos.1)),
            _ => None,
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
        "=== {ID} v{VERSION} (Akshan: per-target Dirty Fighting, missing-health Comeuppance, Scoundrels and revives) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:hit"), HitFx);
    module.add_native_effect(format!("{ID}:aim"), AimFx);
    module.add_native_effect(format!("{ID}:rhit"), RHitFx);
    module.add_native_effect(format!("{ID}:swing"), SwingFx);
    module.add_native_effect(format!("{ID}:noop"), NoopFx);
    module.add_native_passive(format!("{ID}:rogue"), Rogue::default());
    module.add_player_input_ai(UltAi::default());
    module.add_player_input_ai(banner::Screen::default());
    // the revive banner: a single league_akshan.dll draws it itself; in league_addons the bundle's one client extension
    // (BundleClient) calls banner::draw
    #[cfg(not(league_bundle))]
    module.set_extension(banner::Overlay);
    host.log(LogLevel::Info, "league_akshan loaded (Dirty Fighting per target, Comeuppance on missing health, Scoundrels and revives).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;
    use game_places::terrain::Walls;

    fn hex(s: &str) -> Vec<u8> {
        let mut v: Vec<u8> = (0..s.len()).step_by(2).map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap()).collect();
        v.resize(SCAN_LEN, 0xcc);
        v
    }

    // TeamfightManager2.exe 0.6.4 (87,228,416 bytes, 2026-10-14): player_respawn_time 0x142e23260, player_is_alive 0x142e214b0
    const RESPAWN_TIME: &str = "554883ec30488d6c243048c745f8feffffff4885d2742348ffca488b014c8b41084889c141ff9058010000904885c0740980b89808000000740831c04883c4305dc3488b80a00800004883c4305dc3";
    const IS_ALIVE: &str = "554883ec30488d6c243048c745f8feffffff4885d2742748ffca488b014c8b41084889c141ff9058010000904885c0740d0fb680980800004883c4305dc3";

    #[test]
    fn decodes_the_0_6_4_getters() {
        let l = decode(&hex(RESPAWN_TIME), &hex(IS_ALIVE)).expect("layout");
        assert_eq!(l, LifeLayout { getp: 0x158, tag: 0x898, val: 0x8a0 });
    }

    // TeamfightManager2.exe 0.6.5 (87,009,792 bytes, 2026-10-21): player_respawn_time 0x142d693d0, player_is_alive
    // 0x142d67640 - the same code, the player's life fields 0x20 further on
    const RESPAWN_TIME_065: &str = "554883ec30488d6c243048c745f8feffffff4885d2742348ffca488b014c8b41084889c141ff9058010000904885c0740980b8b808000000740831c04883c4305dc3488b80c00800004883c4305dc3";
    const IS_ALIVE_065: &str = "554883ec30488d6c243048c745f8feffffff4885d2742748ffca488b014c8b41084889c141ff9058010000904885c0740d0fb680b80800004883c4305dc3";

    #[test]
    fn decodes_the_0_6_5_getters() {
        let l = decode(&hex(RESPAWN_TIME_065), &hex(IS_ALIVE_065)).expect("layout");
        assert_eq!(l, LifeLayout { getp: 0x158, tag: 0x8b8, val: 0x8c0 });
        // one build's getter with the other's: refused, nothing written
        assert!(decode(&hex(RESPAWN_TIME_065), &hex(IS_ALIVE)).is_none());
    }

    // TeamfightManager2.exe 0.7.1 (94,043,136 bytes, 2026-11-04): player_respawn_time 0x143498fe0, player_is_alive
    // 0x143497240 - 0.6.5's code and fields again (the 0.7.0 compiler's build of the same getters). 0.7.2 (94,603,776
    // bytes, 2026-11-11): these bytes again, at 0x143555970 / 0x143553a90
    const RESPAWN_TIME_071: &str = "554883ec30488d6c243048c745f8feffffff4885d2742348ffca488b014c8b41084889c141ff9058010000904885c0740980b8b808000000740831c04883c4305dc3488b80c00800004883c4305dc3";
    const IS_ALIVE_071: &str = "554883ec30488d6c243048c745f8feffffff4885d2742748ffca488b014c8b41084889c141ff9058010000904885c0740d0fb680b80800004883c4305dc331c04883c4305dc3";

    #[test]
    fn decodes_the_0_7_1_getters() {
        let l = decode(&hex(RESPAWN_TIME_071), &hex(IS_ALIVE_071)).expect("layout");
        assert_eq!(l, LifeLayout { getp: 0x158, tag: 0x8b8, val: 0x8c0 });
    }

    #[test]
    fn refuses_mismatched_code() {
        // is_alive reading another field
        let other = IS_ALIVE.replace("0fb6809808", "0fb680a008");
        assert!(decode(&hex(RESPAWN_TIME), &hex(&other)).is_none());
        // a different getter slot in one of them
        let slot = IS_ALIVE.replace("41ff9058010000", "41ff9060010000");
        assert!(decode(&hex(RESPAWN_TIME), &hex(&slot)).is_none());
        // nothing recognisable
        assert!(decode(&hex("c3"), &hex("c3")).is_none());
    }

    #[test]
    fn decodes_with_other_registers_and_disp8() {
        // cmp byte [rdx+0x40],0 ; je -> mov rcx,[rdx+0x48]; is_alive movzx eax, byte [rdx+0x40]
        let rt = "4885d2741e48ffca488b014c8b41084889c141ff5040904885c0740a807a4000740331c0c3488b4a48c3";
        let al = "4885d2741e48ffca488b014c8b41084889c141ff5040904885c074040fb64240c3";
        assert_eq!(decode(&hex(rt), &hex(al)), Some(LifeLayout { getp: 0x40, tag: 0x40, val: 0x48 }));
    }

    #[test]
    fn the_swing_ends_nearer_the_target_on_the_rope() {
        let me = (300_000.0, 500_000.0);
        let t = (360_000.0, 500_000.0);
        let (a, a0, dir) = swing_plan(me, t);
        assert!((dist(a, me) - ROPE_R).abs() < 1.0);
        assert!(a.1 < me.1, "the hook is not above him: {a:?}");
        let start = swing_at(a, a0, dir, 0);
        assert!(dist(start, me) < 2.0, "{start:?}");
        let end = swing_at(a, a0, dir, SWING_T);
        assert!((dist(end, a) - ROPE_R).abs() < 2.0);
        assert!(dist(end, t) < dist(me, t), "end {end:?} not nearer {t:?}");
        let mut prev = start;
        for k in 1..=SWING_T {
            let p = swing_at(a, a0, dir, k);
            assert!(dist(p, prev) < 1_500.0);
            prev = p;
        }
        let name = sw_name(a, a0, dir, 1234);
        assert!(name.len() <= 64, "{name}");
        let (pa, pa0, pdir, pt0) = parse_sw(&name).unwrap();
        assert!(dist(pa, a) < 1.0 && (pa0 - a0).abs() < 0.001 && pdir == dir && pt0 == 1234);
    }

    #[test]
    fn on_the_rift_the_swing_and_the_bullets_use_its_bigger_square() {
        // a swing in the Rift's far half: on the rope all the way, not held at the game's own 950000
        let me = (1_300_000.0, 1_400_000.0);
        let t = (1_360_000.0, 1_400_000.0);
        let (a, a0, dir) = swing_plan_on(Map::Rift, me, t);
        assert!(a.1 < me.1, "the hook is not above him: {a:?}");
        assert!(dist(swing_at_on(Map::Rift, a, a0, dir, 0), me) < 2.0);
        let end = swing_at_on(Map::Rift, a, a0, dir, SWING_T);
        assert!((dist(end, a) - ROPE_R).abs() < 2.0 && dist(end, t) < dist(me, t), "{end:?}");
        assert_eq!(swing_at(a, a0, dir, SWING_T), (MAP_END - MAP_LO, MAP_END - MAP_LO), "the game's own map holds him");
        // the Rift's own edges, MAP_LO inside
        let rift = Map::Rift.extent();
        let edge = swing_at_on(Map::Rift, (rift, rift), 0.0, 1.0, 0);
        assert_eq!(edge, (rift - MAP_LO, rift - MAP_LO));
        // a tie between the two hooks goes to the one nearer the middle of the map he swings on
        let (me, up) = ((700_000.0, 900_000.0), (700_000.0, 840_000.0));
        assert!(swing_plan(me, up).0 .0 < me.0, "the game's own middle (480000) is to the west");
        assert!(swing_plan_on(Map::Rift, me, up).0 .0 > me.0, "the Rift's middle (807272) is to the east");
        assert_eq!(swing_plan_on(Map::Native, me, up), swing_plan(me, up));
        // the buffs' names with the Rift's seven-digit places still fit the game's 64 bytes and read back
        let name = sw_name((1_614_544.0, 1_614_544.0), -2.618, -1.0, 123_456);
        assert!(name.len() <= BUFF_NAME_CAP, "{name}");
        assert!(parse_sw(&name).is_some_and(|(pa, _, _, t0)| pa == (1_614_544.0, 1_614_544.0) && t0 == 123_456));
        let p = path_name(123_456, (1_614_544, 1_614_544), (1_614_544, 0));
        assert!(p.len() <= BUFF_NAME_CAP, "{p}");
        assert_eq!(parse_path(&p), Some((123_456, (1_614_544.0, 1_614_544.0), (1_614_544.0, 0.0))));
        // the bullets: the full reach past 960000 on the Rift, stopped at the Rift's own edge
        let (x, y) = bullet_end_on(Map::Rift, (900_000.0, 500_000.0), (930_000.0, 540_000.0));
        assert!((x as f64 - 900_000.0 - 0.6 * R_REACH as f64).abs() < 2.0 && (y as f64 - 500_000.0 - 0.8 * R_REACH as f64).abs() < 2.0);
        assert_eq!(bullet_end((900_000.0, 500_000.0), (930_000.0, 540_000.0)).0, 960_000, "the game's own edge");
        let (x, y) = bullet_end_on(Map::Rift, (1_554_545.0, 500_000.0), (1_584_545.0, 540_000.0));
        assert_eq!(x, rift as u64);
        assert!((y as f64 - 580_000.0).abs() < 2.0, "{y}");
    }

    /// 2026-11-10 (the user on the Rift: 「有的地方会走路卡住」): the swing set him down on its arc inside the Rift's walls
    /// and he stood stuck there. A piece of the Rift as `stand_ok` sees it with the walls file (`!is_wall` on
    /// `rift_ground`): cells of 60000/11, 40 x 40 from (1100000, 1100000) - past the game's own 960000 - columns 20 and 21
    /// wall, grown by one cell (`padded`): no hero stands at x 1203636..1225455.
    #[test]
    fn on_the_rift_the_swing_lets_go_at_its_walls() {
        let e = Map::Rift.extent();
        let row = format!("{}##{}", ".".repeat(20), ".".repeat(18));
        let g = Walls::from_rows(&vec![row.as_str(); 40], 60_000.0 / 11.0, (1_100_000.0, 1_100_000.0), (e, e)).padded();
        let ok = |q: (f64, f64)| !g.is_wall(q.0, q.1);
        // swinging at someone across the wall: the arc (all on the piece) runs into it 14 ticks in
        let (me, t) = ((1_190_000.0, 1_200_000.0), (1_240_000.0, 1_200_000.0));
        let (a, a0, dir) = swing_plan_on(Map::Rift, me, t);
        let arc: Vec<Option<(f64, f64)>> = (0..=SWING_T).map(|k| swing_step(Map::Rift, a, a0, dir, k, ok)).collect();
        let stop = arc.iter().position(Option::is_none);
        assert_eq!(stop, Some(14), "{a:?}");
        // every spot before it is his on the arc, on ground; the one he stays on is the last of them
        for (k, p) in arc[..14].iter().enumerate() {
            assert_eq!(*p, Some(swing_at_on(Map::Rift, a, a0, dir, k)));
        }
        let (last, next) = (swing_at_on(Map::Rift, a, a0, dir, 13), swing_at_on(Map::Rift, a, a0, dir, 14));
        assert!(ok(last) && !ok(next), "{last:?} {next:?}");
        // the full swing would have put him past the wall's near edge (the old swing, into it)
        assert!(swing_at_on(Map::Rift, a, a0, dir, SWING_T).0 > next.0);
        // nothing in the way (away from the wall): the whole swing, past 960000
        let back = (1_140_000.0, 1_200_000.0);
        let (b, b0, bdir) = swing_plan_on(Map::Rift, me, back);
        assert!((0..=SWING_T).all(|k| swing_step(Map::Rift, b, b0, bdir, k, ok) == Some(swing_at_on(Map::Rift, b, b0, bdir, k))));
        // the game's own map: stand_ok never lets go of him - every spot as before
        let native = |q: (f64, f64)| stand_ok(Map::Native, q);
        let (n, n0, ndir) = swing_plan((300_000.0, 500_000.0), (360_000.0, 500_000.0));
        assert!((0..=SWING_T).all(|k| swing_step(Map::Native, n, n0, ndir, k, native) == Some(swing_at(n, n0, ndir, k))));
        let edge = swing_plan((900_000.0, 900_000.0), (960_000.0, 960_000.0));
        assert!((0..=SWING_T).all(|k| swing_step(Map::Native, edge.0, edge.1, edge.2, k, native)
            == Some(swing_at(edge.0, edge.1, edge.2, k))));
    }

    #[test]
    fn third_hit_procs() {
        assert_eq!(next_hit(0), (false, 1));
        assert_eq!(next_hit(1), (false, 2));
        assert_eq!(next_hit(2), (true, 0));
    }

    #[test]
    fn bullets_grow_with_missing_health() {
        // attack 200: min R_DMG + R_RATIO% of 200 (35 + 50 = 85)
        let min = R_DMG + R_RATIO * 2;
        assert_eq!(bullet_damage(200, 1000, 1000), min);
        // 67% missing or more: 3x
        assert_eq!(bullet_damage(200, 330, 1000), min * R_MAX);
        assert_eq!(bullet_damage(200, 10, 1000), min * R_MAX);
        // half way to the cap: about 2x
        let mid = bullet_damage(200, 665, 1000);
        assert!(mid > min * 19 / 10 && mid < min * 21 / 10, "{mid}");
        // each bullet is read on the health left
        assert!(volley(200, 1000, 1000, 5) > 5 * min);
    }

    fn champ(id: usize, at: (f64, f64), hp: usize, shield: usize, max: usize, armor: usize) -> Body {
        Body { id, at, r: 10_000.0, hp, shield, max, armor }
    }

    #[test]
    fn armour_is_counted_before_calling_it_lethal() {
        // the 11-02 log: 3 stored, #21 614 hp + 86 shield (1260 max), attack 233: 755 before armour "lethal" - the
        // bullets took 169 and 195 off (armour about 38) and left him alive
        let him = champ(21, (100_000.0, 0.0), 614, 86, 1260, 38);
        assert!(volley(233, 700, 1260, 3) >= 700);
        assert!(armoured_volley(233, &him, 3) < 700);
        assert!(!lethal(233, &him, 3, &[]));
        assert_eq!(armoured(270, 38), 195);
        // no armour: the same three bullets drop a weaker one
        let bare = champ(21, (100_000.0, 0.0), 500, 0, 1260, 0);
        assert!(lethal(233, &bare, 3, &[]));
        assert_eq!(bullets_to_drop(233, &bare, 3, 100), Some(2));
        // the shield takes the damage first and the bullets grow on the health under it
        let shielded = champ(21, (100_000.0, 0.0), 500, 300, 1260, 0);
        assert!(armoured_volley(233, &shielded, 3) < 800);
        assert!(!lethal(233, &shielded, 3, &[]));
    }

    #[test]
    fn the_units_on_the_line_take_their_bullets_first() {
        let me = (0.0, 0.0);
        let him = champ(370, (100_000.0, 0.0), 300, 0, 1644, 20);
        // a minion between them, one beside the line, one behind him, one behind Akshan
        let minion = |id: usize, at: (f64, f64)| Body { id, at, r: 7_000.0, hp: 468, shield: 0, max: 468, armor: 0 };
        let units = [minion(569, (50_000.0, 10_000.0)), minion(570, (50_000.0, 30_000.0)),
                     minion(571, (120_000.0, 0.0)), minion(572, (-20_000.0, 0.0))];
        let on = on_line(me, him.at, &units);
        assert_eq!(on.iter().map(|b| b.id).collect::<Vec<_>>(), vec![569]);
        // nearest first
        let two = on_line(me, him.at, &[minion(2, (80_000.0, 0.0)), minion(1, (30_000.0, -5_000.0))]);
        assert_eq!(two.iter().map(|b| b.id).collect::<Vec<_>>(), vec![1, 2]);
        // 4 bullets kill him on a clear line; the minion eats 3 of them (the 11-02 log: 3 on #569, 1 on #370)
        assert!(lethal(357, &him, 4, &[]));
        assert_eq!(bullets_to_drop(357, &on[0], 4, 100), Some(3));
        assert!(!lethal(357, &him, 4, &on));
        // one bullet and a monster in the way (the log's "#24 hp+shield 4 vs 261"): never lethal
        let low = champ(24, (100_000.0, 0.0), 4, 0, 1500, 30);
        let big = Body { id: 342, at: (40_000.0, 0.0), r: 12_000.0, hp: 1324, shield: 0, max: 1345, armor: 30 };
        assert!(lethal(208, &low, 1, &[]));
        assert!(!lethal(208, &low, 1, &[big]));
        // a tower on the line takes them all
        let tower = Body { id: 9, at: (60_000.0, 0.0), r: 15_000.0, hp: 3200, shield: 0, max: 3200, armor: 100 };
        assert!(!lethal(357, &champ(1, (100_000.0, 0.0), 1, 0, 1644, 0), 5, &[tower]));
    }

    #[test]
    fn past_the_units_on_the_line_the_rest_must_kill_with_a_margin() {
        // a nearly dead minion on the line takes one bullet (attack 200: 85 a bullet, up to 3x on low health)
        let weak = Body { id: 2, at: (50_000.0, 0.0), r: 7_000.0, hp: 50, shield: 0, max: 400, armor: 0 };
        assert_eq!(bullets_to_drop(200, &weak, 3, 100), Some(1));
        // 400 of 1000: two clean bullets (237 + 255) drop him on a clear line
        let him = champ(1, (100_000.0, 0.0), 400, 0, 1000, 0);
        assert_eq!(armoured_volley(200, &him, 2), 492);
        assert!(lethal(200, &him, 2, &[]));
        // 3 stored behind the minion: 2 get through, and 492 is not LETHAL_MARGIN% over 400
        assert!(!lethal(200, &him, 3, &[weak]));
        // 300 of 1000: the 2 left (3x: 255 + 255) clear it with room to spare
        assert!(lethal(200, &Body { hp: 300, ..him }, 3, &[weak]));
    }

    #[test]
    fn the_copy_carries_the_numbers_and_the_native_parts() {
        let copy = include_str!("../override/league_akshan.data_champion");
        for (k, v) in [("r_dmg", R_DMG), ("r_ratio", R_RATIO), ("r_max", R_MAX), ("r_full", R_FULL), ("p_t", P_T)] {
            assert!(copy.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for name in ["league_akshan:hit", "league_akshan:aim", "league_akshan:rogue", "league_akshan:swing", ROPE] {
            assert!(copy.contains(name), "the copy never uses {name}");
        }
        for name in [P_GO, R_CHAN, R_OPEN, R_FIRE, STORED[0], STORED[4], P_SCD, P_SH] {
            assert!(copy.contains(&format!("\"{name}\"")), "the copy never names {name}");
        }
        assert!(copy.contains(&format!("\"range\": {R_RANGE}")), "R's range is not {R_RANGE}");
        // 0.2.6: the add-on fires the bullets (no data bullet, no random pick in the copy); the main pack keeps the
        // data's bullet that stops on the first enemy it meets (`on_line`)
        assert!(!copy.contains("league_akshan_r_aim\""), "the copy still lobs the data's aim at a random champion");
        let flat: String = copy.split_whitespace().collect();
        assert!(!flat.contains("\"name\":\"league_akshan_r_bullet\",\"penetrate\""), "the copy still has the data's bullet");
        assert!(flat.contains("\"name\":\"league_akshan_r_bullet\""), "the copy lost the bullet's picture");
        let main = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/../../league/champion/league_akshan.data_champion"))
            .expect("the main pack's league_akshan");
        let flat: String = main.split_whitespace().collect();
        assert!(flat.contains("\"name\":\"league_akshan_r_bullet\",\"penetrate\":false,\"applied_target\":\"Enemy\""),
                "the main pack's bullet no longer stops on the first enemy");
        let kit = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_akshan.py"))
            .expect("build_akshan.py");
        for (k, v) in [("r_w", R_W as usize), ("r_speed", R_SPEED as usize), ("r_gap", R_GAP), ("r_reach", R_REACH as usize),
                       ("p_dmg", P_DMG), ("p_ratio", P_RATIO), ("p_sh", P_SH_AMT), ("p_sh_r", P_SH_R), ("p_sh_t", P_SH_T),
                       ("p_scd", P_SCD_T)] {
            assert!(kit.contains(&format!("\"{k}\": {v},")), "{k} is not {v} in build_akshan.P");
        }
    }

    #[test]
    fn the_bullets_fly_their_reach_toward_the_lock_and_the_early_fire_outlives_a_poll() {
        // 11-04 logs: 33 of the first 60 bullets went to other champions; FLAG_T 3 (seen 2 ticks) vs the 6-tick poll
        assert!(FIRE_T > R_GAP);
        assert_eq!(bullet_end((100_000.0, 100_000.0), (200_000.0, 100_000.0)), (320_000, 100_000));
        // the diagonal keeps its direction
        let (x, y) = bullet_end((100_000.0, 100_000.0), (130_000.0, 140_000.0));
        assert!((x as f64 - 100_000.0 - 0.6 * R_REACH as f64).abs() < 2.0 && (y as f64 - 100_000.0 - 0.8 * R_REACH as f64).abs() < 2.0);
        // short of the map's edge, still on the line
        let (x, y) = bullet_end((900_000.0, 500_000.0), (930_000.0, 540_000.0));
        assert_eq!(x, 960_000);
        assert!((y as f64 - 580_000.0).abs() < 2.0, "{y}");
        // the lock's name round-trips
        assert_eq!(lock_name(427).strip_prefix(R_LOCK).and_then(|r| r.strip_prefix(':')).and_then(|r| r.parse::<usize>().ok()), Some(427));
    }

    /// The engine's rule (game 0.7.1, fitted on the 11-05 bullets): a bullet from `from` toward `end` at `speed` a tick
    /// (step 0 on its spawn tick) hits a unit at `at` walking `v` a tick when his centre is within `w` of it on a tick.
    fn meets(from: (f64, f64), end: (f64, f64), at: (f64, f64), v: (f64, f64), w: f64) -> bool {
        let track: Vec<(usize, (f64, f64))> = (0..=20).map(|k| (k, (at.0 + v.0 * k as f64, at.1 + v.1 * k as f64))).collect();
        closest_pass(0, from, end, &track).is_some_and(|d| d <= w)
    }

    fn end_f(from: (f64, f64), to: (f64, f64)) -> (f64, f64) {
        let e = bullet_end(from, to);
        (e.0 as f64, e.1 as f64)
    }

    #[test]
    fn the_bullet_steps_no_longer_over_a_champion_on_its_line() {
        // 2 x R_W >= R_SPEED: a unit standing anywhere on the line is within R_W of a tick
        assert!(2.0 * R_W >= R_SPEED as f64);
        let me = (100_000.0, 500_000.0);
        let end = end_f(me, (300_000.0, 500_000.0));
        for d in (10_000..215_000).step_by(1_000) {
            let at = (me.0 + d as f64, me.1);
            assert!(meets(me, end, at, (0.0, 0.0), R_W), "{d}");
        }
        // 0.2.6's 6000 at 20000 a tick: a unit between two ticks was stepped over (11-05 .log R DONE #12: the lock 68,220
        // away, the ticks 8,220 and 11,780 from him: 4 of 5 lost)
        let to = (587_474.0, 341_171.0);
        let old_end = (437_161.0, 362_222.0);
        let u = ((old_end.0 - to.0) / dist(to, old_end), (old_end.1 - to.1) / dist(to, old_end));
        let back = R_REACH as f64 - dist(to, old_end);
        let from = (to.0 - u.0 * back, to.1 - u.1 * back);
        assert!((back - 68_220.0).abs() < 10.0, "{back}");
        let v = (-211.0, 206.0);
        assert!(!meets(from, old_end, to, v, 6_000.0));
        assert!(meets(from, end_f(from, lead(from, to, v, R_SPEED as f64)), to, v, R_W));
    }

    #[test]
    fn the_bullets_lead_a_walking_lock() {
        // 11-05 (.prev R DONE #11, 5 of 5 lost; R AIM #45): the lock #1194 196,275 away walking (1289, -197) a tick
        let to = (435_223.0, 52_418.0);
        let old_end = (445_772.0, 31_167.0);
        let u = ((old_end.0 - to.0) / dist(to, old_end), (old_end.1 - to.1) / dist(to, old_end));
        let back = R_REACH as f64 - dist(to, old_end);
        let from = (to.0 - u.0 * back, to.1 - u.1 * back);
        assert!((back - 196_275.0).abs() < 10.0, "{back}");
        let v = (1_289.0, -197.0);
        // at where he stood: missed with either circle
        assert!(!meets(from, old_end, to, v, 6_000.0));
        assert!(!meets(from, old_end, to, v, R_W));
        // led by his walk x the flight
        let ahead = lead(from, to, v, R_SPEED as f64);
        assert!(meets(from, end_f(from, ahead), to, v, R_W));
        let flight = dist(from, ahead) / R_SPEED as f64;
        assert!(dist(ahead, (to.0 + v.0 * flight, to.1 + v.1 * flight)) < 50.0, "{ahead:?}");
        // standing still: no lead; a dash or a blink (faster than V_MAX): none either; a long lead is capped
        assert_eq!(lead(from, to, (0.0, 0.0), R_SPEED as f64), to);
        assert_eq!(lead(from, to, (V_MAX + 1.0, 0.0), R_SPEED as f64), to);
        let far = lead((0.0, 0.0), (200_000.0, 0.0), (0.0, 2_400.0), 5_000.0);
        assert!((dist(far, (200_000.0, 0.0)) - LEAD_CAP).abs() < 1.0, "{far:?}");
    }

    #[test]
    fn the_walk_the_miss_and_the_names() {
        // the walk over the last ticks: (newest - oldest) / ticks between
        let track = [(10, 7, (1_000.0, 0.0)), (11, 7, (1_400.0, 300.0)), (13, 7, (2_200.0, 900.0))];
        assert_eq!(walk(&track), (400.0, 300.0));
        assert_eq!(walk(&track[..1]), (0.0, 0.0));
        // the closest pass: ticks at 0, 20000, ... ; the lock standing 5000 off the line at 100000 -> 5000 (tick 5)
        let lock: Vec<(usize, (f64, f64))> = (100..120).map(|t| (t, (100_000.0, 5_000.0))).collect();
        assert_eq!(closest_pass(100, (0.0, 0.0), (220_000.0, 0.0), &lock), Some(5_000.0));
        // his position is read at the bullet's tick: walking off the line 5000 a tick, 30000 from it as the bullet passes
        let walking: Vec<(usize, (f64, f64))> = (100..120).map(|t| (t, (100_000.0, 5_000.0 * (t - 99) as f64))).collect();
        assert_eq!(closest_pass(100, (0.0, 0.0), (220_000.0, 0.0), &walking), Some(30_000.0));
        assert_eq!(closest_pass(100, (0.0, 0.0), (220_000.0, 0.0), &[]), None);
        // the buffs' names fit the game's 64 bytes and read back
        let v = vel_name(1_234, (-985.4, 390.6));
        assert!(v.len() <= BUFF_NAME_CAP, "{v}");
        assert_eq!(parse_vel(&v), Some((1_234, (-985.0, 391.0))));
        let p = path_name(123_456, (959_999, 958_888), (960_000, 0));
        assert!(p.len() <= BUFF_NAME_CAP, "{p}");
        assert_eq!(parse_path(&p), Some((123_456, (959_999.0, 958_888.0), (960_000.0, 0.0))));
        assert_eq!(parse_vel(&p), None);
        assert_eq!(parse_path(&v), None);
        // crowd control in the log
        let mut c = CcV1::of_kind(CcKindV1::ForceMove, 10);
        c.speed = 3_000;
        assert_eq!(cc_entry(&c), "ForceMove 10 speed 3000");
        let mut a = CcV1::of_kind(CcKindV1::Animation, 6);
        a.set_name("skill2");
        assert_eq!(cc_entry(&a), "Animation 6 skill2");
        assert_eq!(cc_entry(&CcV1::of_kind(CcKindV1::Bind, 37)), "Bind 37");
    }

    #[test]
    fn the_line_counts_the_centre_only() {
        // 0.2.6 counted a unit within R_W + its body; the engine reads the centre: a minion 15000 off the line (body
        // 7000) lets the bullets by
        let him = champ(1, (100_000.0, 0.0), 300, 0, 1_000, 0);
        let minion = |id: usize, off: f64| Body { id, at: (50_000.0, off), r: 7_000.0, hp: 468, shield: 0, max: 468, armor: 0 };
        assert!(on_line((0.0, 0.0), him.at, &[minion(2, 15_000.0)]).is_empty());
        assert_eq!(on_line((0.0, 0.0), him.at, &[minion(3, R_W - 1.0)]).len(), 1);
    }
}
