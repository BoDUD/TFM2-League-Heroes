//! 黑默丁格附加包：照英雄联盟做主包数据做不到的炮台射击和塔边加速（用户 2026-10-21：中单、技能方案 A、「做附加包啊」）。
//!
//! 主包保持纯数据：数据没有召唤物，炮台是落点上的周期区域（每座三个区域：受控英雄、英雄、其他敌人），伤害在目标身上当场结算，
//! **看不到炮弹从炮台飞出去**；被动（海克斯科技亲和）是炮台的光环区域，**只认他自己的炮台、不认己方防御塔**。`mod.override_info`
//! 把主包的黑默丁格换成 `override/` 里的副本（`tools/kit/build_heimerdinger.py --native`）：
//!
//! - **炮台由本包来打**：副本的炮台保留画面、音效和三个槽位（最多 3 座），但没有区域；Q 放炮台和升级的 Q 放巨型炮台那一 tick 跑本包的
//!   `league_heimerdinger:q` / `:x`（拿施法的方向或目标），炮台站在隐形弹停下的地方（朝那个方向 `q_place` 远，`q_place / q_speed`
//!   tick 后），和数据的炮台图同一个点。
//! - **炮台侧面朝敌人**（用户：「炮台改成侧面朝敌人」「灵活利用PPU 炮也可以调的清晰」）：目标在他左边时 `:q` / `:x` 给他挂
//!   `league_heimerdinger_t_face_l` / `_x_face_l`（`FACE_T` tick），副本的隐形弹落地时据此画朝左的侧面炮台
//!   （`league_heimerdinger_turret_l` / `_apex_l`），否则朝右（`_r`）。主包不知道目标在哪边，还是正面朝镜头的炮台。
//! - **从炮口射出看得见的炮弹**：炮台照主包区域的节奏（站稳后 `t_first` / `x_first` tick 第一发、之后每 `t_per` / `x_per`，
//!   和炮台图的炮口闪光对齐）打一个敌人：先打范围内**受控制的英雄**（击飞、眩晕、禁锢、强制位移、恐惧、魅惑：游戏 `EnemyChampionInCC`
//!   的六种）发射充能光束（`t_beam_line`，`tb_dmg` + `tb_ratio`% 法强），没有就打最近的敌方英雄，再没有就打最近的小兵、野怪
//!   （防御塔不打），发射炮弹（`t_shot`，`t_dmg` + `t_ratio`%）；巨型炮台的等离子弹（`x_shot`）还减速 `x_slow`%。
//!   炮弹从侧面炮台的炮口（`T_MUZZLE` / `X_MUZZLE`，朝左时左右反过来）飞向目标（`spawn_projectile`），**飞到才扣血**
//!   （游戏 0.6.4 的 `deal_damage_typed` 只把伤害排进效果队列）。
//! - **海克斯科技亲和**：他活着时每 `p_per` tick 看一次，站在自己的炮台 `p_r` 内或己方防御塔 `p_tr` 内就加 `p_ms`% 移速
//!   `p_t` tick（主包的 `league_heimerdinger_haste`，画面照旧）。
//!
//! - **升级给谁**（`combo.rs`；用户 2026-10-24：R 改成「升级下一个技能」）：AI 钩子 `league_heimerdinger:combo` 在 R 的升级
//!   挂着时替游戏的 AI 挑：敌方英雄扎堆就按 E（CH-3X），不然按 Q（巨型炮台），Q 没好再按 E。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态记在每个黑默丁格自己的被动实例里，
//! 原生效果把炮台交给被动时按（这局的种子、模拟的来源、他的编号）分开，服务端预模拟和你看的那场各算各的。
//!
//! - **炮台有了身体（0.3.0，2026-11-14；用户：「召唤物的全做啊 剩下的一批英雄也做了啊」）**：英雄联盟的炮台是能被选中、
//!   能被打掉的单位（生命 130–700 + 法强、护甲魔抗随等级，打掉给 5 金币；巨型炮台 725–1825、8 秒）。这里原来炮台是一张画面，
//!   打不到。稳定 mod API 的 `spawn_unit`（公用部分在萨科附加包的 `summon.rs`）：`:q` / `:x` 在施法那一 tick 就在炮台站的地方
//!   生成一个「身体」单位（`league_heimerdinger_h28g` / `_h28q`，[`turret_spec`]：移速 1 不会走，攻击 0 伤害——只为了朝着
//!   敌人、播开炮的动作），成功了给他挂 `T_UNIT` / `X_UNIT`，副本的数据在隐形弹落地时读它、不再画侧面的炮台图；射击照旧由
//!   本包按原来的节奏打（[`Workshop::fire`]），从身体现在站的地方、朝目标那边的炮口射出。身体被打掉，本包的这座炮台就停火，
//!   Q 的炮台还空出它的槽位（英雄联盟：炮台最多 3 座，打掉一座就能再放）。生成不了（宿主没有这个接口、失败、测试开关
//!   `unit=off`、读不成单位）就和以前一样：画面 + 本包射击。日志里 `TURRET` 开头的行。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_heimerdinger.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `SPAWN`（他出场和参数）、`PUT`（炮台站下，施法输入的种类）、`SHOT`（炮台出手）、`HASTE`（加速，塔边还是炮台边）、
//! `WATCH`（每 30 秒的计数）、`E CLUMP` / `Q APEX` / `E ONE`（钩子替 AI 按的，一串连着按的只记一行），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod combo;

#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

use summon::{Event, Flock};

const ID: &str = "league_heimerdinger";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_heimerdinger") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 侧面炮台朝右时炮口离炮台的点多远（游戏像素 x 1000：往前、往上；tools/art/import_heimerdinger_fx.py 写的
/// assets/source/heimerdinger/hd/side_muzzles.json，make_override.py 核对）。一颗飞行物画在它的点上方 5 px，所以发射点往南挪
/// 5 px 减去炮口的高度。
pub const T_MUZZLE: (i64, i64) = (9_710, -300);
pub const X_MUZZLE: (i64, i64) = (13_140, 3_810);
/// 朝左的标记挂多久：隐形弹飞 `q_place / q_speed`（5）tick 才落地画炮台。
const FACE_T: usize = 30;
/// 算「受控制」的控制种类：游戏 `CastingTarget::check` 的掩码 0x347（击飞、眩晕、禁锢、强制位移、恐惧、魅惑）。
const CC_MASK: u32 = 0x347;

// ===================== 炮台的身体（0.3.0） =====================

/// The bodies' unit names: the game draws them from asset/base/aseprite_resources/champions/<name>, which mod.override_info
/// sends to the main pack's league/champions/<name> (tools/art/unit_heimerdinger_turrets.py: the side turrets' dense
/// squares as plain frames, the size the turrets have on screen today). Not the effect sheets' names: league.dll finds
/// dense frames by the resource's last name alone, and league_heimerdinger_turret / _apex are registered EFFECTS rows.
pub const H28G: &str = "league_heimerdinger_h28g";
pub const H28Q: &str = "league_heimerdinger_h28q";
/// The bodies' sheets: the shot's ticks and the tick its widest flash starts (checked by make_override.py), and the muzzle
/// forward and up of the body's spot (game px x 1000; the shots leave there, the side toward their target).
pub const TU_ACT: usize = 15;
pub const TU_LANDS: usize = 6;
pub const XU_ACT: usize = 15;
pub const XU_LANDS: usize = 3;
pub const TU_MUZZLE: (i64, i64) = (11_000, 8_000);
pub const XU_MUZZLE: (i64, i64) = (15_000, 23_000);
/// On him from a body's spawn: the copy's data draws no side turret when the hidden bolt lands (`q_place / q_speed` ticks
/// after the cast). Laid for `FLAG_TICKS`.
pub const T_UNIT: &str = "league_heimerdinger_t_unit";
pub const X_UNIT: &str = "league_heimerdinger_x_unit";
pub const T_UID: &str = "league_heimerdinger_t_uid";
pub const X_UID: &str = "league_heimerdinger_x_uid";
const FLAG_TICKS: usize = 12;
const UID_TICKS: usize = 6;
/// League (wiki, 2026-11-14): H-28G 130-700 health (+5-53 % AP) against his 558-2343 - 23-30 % of his (his 860-2424 here:
/// 1.54-1.03 times League's); armour 10-110 against his 19-90 (about 90 %), magic resistance 25-86 against his 30-52
/// (about 125 %). H-28Q 725-1825 (+50 % AP) against his 1083 at 6 and 2343 at 18 (97-78 %): 85 %; armour and magic
/// resistance 30-100 (about 110 / 150 % of his).
pub const TURRET_HP_PCT: usize = 26;
pub const TURRET_HP_AP: usize = 30;
pub const TURRET_DEF_PCT: usize = 90;
pub const TURRET_MR_PCT: usize = 125;
pub const APEX_HP_PCT: usize = 85;
pub const APEX_HP_AP: usize = 50;
pub const APEX_DEF_PCT: usize = 110;
pub const APEX_MR_PCT: usize = 150;
/// The main pack's Q slots (`t<s>_busy` while that turret stands): a destroyed turret frees its own.
pub const SLOT_FLAGS: [&str; 3] = ["league_heimerdinger_ta_busy", "league_heimerdinger_tb_busy", "league_heimerdinger_tc_busy"];
/// A body gone within this many ticks was never really there.
pub const LOST_AGE: usize = 6;
/// Bodies on the books at once (3 turrets and an apex, with room).
const BODY_CAP: usize = 6;

/// The test knobs (`league_heimerdinger.cfg` beside the log), read once.
static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

/// Lines of each kind of the bodies' a launch (league_shaco_backstab's): the server's presims the first 40, then every
/// 200th; the match on screen all.
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let shown = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= 40 || *n % 200 == 0).then_some(*n)
}

/// 主包黑默丁格的名字（buff、声音、画面都以它开头）。
fn hd(x: &str) -> String {
    format!("league_heimerdinger_{x}")
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_HEIMERDINGER_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_heimerdinger.log");
        }
    }
    PathBuf::from("league_heimerdinger.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    // the file stays open (league_lillia's log_open_once fix: opening it for every line stalled the simulation thread)
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 隐形弹飞多远、多快（炮台站在它停下的地方）。
    pub q_place: usize,
    pub q_speed: usize,
    /// Q 的炮台：活多久、出手间隔、第一发、射程、炮弹伤害和法强 %、光束伤害和法强 %。
    pub t_life: usize,
    pub t_per: usize,
    pub t_first: usize,
    pub t_r: usize,
    pub t_dmg: usize,
    pub t_ratio: usize,
    pub tb_dmg: usize,
    pub tb_ratio: usize,
    /// 升级的 Q 的巨型炮台：同上，加减速 % 和 tick。
    pub x_life: usize,
    pub x_per: usize,
    pub x_first: usize,
    pub x_r: usize,
    pub x_dmg: usize,
    pub x_ratio: usize,
    pub x_slow: usize,
    pub x_slow_t: usize,
    pub xb_dmg: usize,
    pub xb_ratio: usize,
    /// 被动：炮台 / 防御塔多近算「旁边」、多久看一次、移速 %、加多久。
    pub p_r: usize,
    pub p_tr: usize,
    pub p_per: usize,
    pub p_ms: usize,
    pub p_t: usize,
    /// 炮弹、光束、等离子弹飞多快（每 tick）。
    pub t_speed: usize,
    pub b_speed: usize,
    pub x_speed: usize,
    /// 钩子（combo.rs）：Q、E 的施放距离，CH-3X 一颗的半径。
    pub q_range: usize,
    pub e_range: usize,
    pub re_r: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            q_place: 20000,
            q_speed: 4000,
            t_life: 600,
            t_per: 50,
            t_first: 40,
            t_r: 50000,
            t_dmg: 6,
            t_ratio: 4,
            tb_dmg: 18,
            tb_ratio: 14,
            x_life: 480,
            x_per: 30,
            x_first: 30,
            x_r: 60000,
            x_dmg: 22,
            x_ratio: 12,
            x_slow: 25,
            x_slow_t: 45,
            xb_dmg: 45,
            xb_ratio: 30,
            p_r: 40000,
            p_tr: 60000,
            p_per: 20,
            p_ms: 20,
            p_t: 30,
            t_speed: 2800,
            b_speed: 9000,
            x_speed: 3500,
            q_range: 60000,
            e_range: 85000,
            re_r: 25000,
        }
    }
}

/// `{"t_per":50,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "q_place" => &mut p.q_place,
            "q_speed" => &mut p.q_speed,
            "t_life" => &mut p.t_life,
            "t_per" => &mut p.t_per,
            "t_first" => &mut p.t_first,
            "t_r" => &mut p.t_r,
            "t_dmg" => &mut p.t_dmg,
            "t_ratio" => &mut p.t_ratio,
            "tb_dmg" => &mut p.tb_dmg,
            "tb_ratio" => &mut p.tb_ratio,
            "x_life" => &mut p.x_life,
            "x_per" => &mut p.x_per,
            "x_first" => &mut p.x_first,
            "x_r" => &mut p.x_r,
            "x_dmg" => &mut p.x_dmg,
            "x_ratio" => &mut p.x_ratio,
            "x_slow" => &mut p.x_slow,
            "x_slow_t" => &mut p.x_slow_t,
            "xb_dmg" => &mut p.xb_dmg,
            "xb_ratio" => &mut p.xb_ratio,
            "p_r" => &mut p.p_r,
            "p_tr" => &mut p.p_tr,
            "p_per" => &mut p.p_per,
            "p_ms" => &mut p.p_ms,
            "p_t" => &mut p.p_t,
            "t_speed" => &mut p.t_speed,
            "b_speed" => &mut p.b_speed,
            "x_speed" => &mut p.x_speed,
            "q_range" => &mut p.q_range,
            "e_range" => &mut p.e_range,
            "re_r" => &mut p.re_r,
            _ => continue,
        };
        *slot = v;
    }
    p.q_speed = p.q_speed.max(1);
    p.t_per = p.t_per.max(1);
    p.x_per = p.x_per.max(1);
    p.p_per = p.p_per.max(1);
    p.t_speed = p.t_speed.max(1);
    p.b_speed = p.b_speed.max(1);
    p.x_speed = p.x_speed.max(1);
    p.x_slow = p.x_slow.min(95);
    p
}

// ===================== 计算 =====================

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Kind {
    /// Q 的 H-28G 进化炮台。
    Turret,
    /// 升级的 Q 的 H-28Q 巨型炮台。
    Apex,
}

/// 一发的样子：光束（打受控英雄）还是炮弹。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Fire {
    Cannon,
    Beam,
}

/// 一发的魔法伤害（减免前）：`dmg` + `ratio`% 法强。
pub fn shot_damage(dmg: usize, ratio: usize, ap: usize) -> usize {
    dmg + ratio * ap / 100
}

/// 炮台站在哪：`from` 朝 `dir`（不必是单位长度）`reach` 远；没有方向就在 `from`。
pub fn stand_spot(from: (f64, f64), dir: Option<(f64, f64)>, reach: f64) -> (f64, f64) {
    match dir.and_then(unit) {
        Some((ux, uy)) => (from.0 + ux * reach, from.1 + uy * reach),
        None => from,
    }
}

fn unit(v: (f64, f64)) -> Option<(f64, f64)> {
    let d = (v.0 * v.0 + v.1 * v.1).sqrt();
    (d >= 1e-6).then(|| (v.0 / d, v.1 / d))
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 控制种类的列表里有没有算「受控制」的。
pub fn hard_cc(kinds: impl IntoIterator<Item = u32>) -> bool {
    kinds.into_iter().any(|k| k < 32 && CC_MASK & (1 << k) != 0)
}

fn at(p: (f64, f64)) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

pub struct Unit {
    pub id: usize,
    pub pos: (f64, f64),
    pub champion: bool,
    pub in_cc: bool,
}

/// 能打的敌方单位（英雄、小兵、野怪；塔、水晶不算：主包区域的 `EnemyWithoutTower`）。
fn enemies(sim: &StableSim<'_>, team: usize) -> Vec<Unit> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.team() == team || !e.is_alive() || !e.is_targetable() {
            continue;
        }
        let ok = matches!(
            e.kind(),
            Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Epic | EntityKindV1::Serpen)
        );
        if ok {
            let champion = e.kind() == Some(EntityKindV1::Champion);
            let in_cc = champion && hard_cc((0..e.cc_count()).filter_map(|j| e.cc_at(j)).map(|c| c.kind));
            out.push(Unit { id: e.id(), pos: fpos(e.pos()), champion, in_cc });
        }
    }
    out
}

/// 炮台打谁：范围内最近的受控英雄（光束），没有就最近的英雄，再没有就最近的其他单位（炮弹）。
pub fn choose(units: &[Unit], from: (f64, f64), reach: f64) -> Option<(&Unit, Fire)> {
    let near = |u: &&Unit| dist(u.pos, from) <= reach;
    let by = |a: &&Unit, b: &&Unit| dist(a.pos, from).total_cmp(&dist(b.pos, from));
    if let Some(u) = units.iter().filter(|u| u.in_cc).filter(near).min_by(by) {
        return Some((u, Fire::Beam));
    }
    units
        .iter()
        .filter(|u| u.champion)
        .filter(near)
        .min_by(by)
        .or_else(|| units.iter().filter(near).min_by(by))
        .map(|u| (u, Fire::Cannon))
}

/// A turret's body from his numbers now (`stat`, his health cap `max_hp`) for `life` ticks: move speed 1 (it does not
/// walk), a harmless attack in the turret's reach and pace (it faces its target and plays the shot; the add-on's natives
/// fire), health and defences from League's turrets against him.
pub fn turret_spec(kind: Kind, p: &Params, stat: &StatV1, max_hp: usize, life: usize) -> summon::Spec {
    let (name, hp_pct, hp_ap, def, mr, reach, per, act, lands) = match kind {
        Kind::Turret => (H28G, TURRET_HP_PCT, TURRET_HP_AP, TURRET_DEF_PCT, TURRET_MR_PCT, p.t_r, p.t_per, TU_ACT, TU_LANDS),
        Kind::Apex => (H28Q, APEX_HP_PCT, APEX_HP_AP, APEX_DEF_PCT, APEX_MR_PCT, p.x_r, p.x_per, XU_ACT, XU_LANDS),
    };
    summon::Spec {
        name: name.to_string(),
        life,
        stat: StatV1 { attack: 0, magic_power: stat.magic_power, hp: (max_hp * hp_pct / 100 + stat.magic_power * hp_ap / 100).max(1),
                       defence: stat.defence * def / 100, magic_resistance: stat.magic_resistance * mr / 100, move_speed: 1,
                       hp_regen: 0, stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: 0, attack: 0, range: reach, cooltime: per.max(act + 1), duration: act, start_timing: lands,
                               cancelable: false, attack_type: AttackTypeV1::BaseAttack.code() },
    }
}

// ===================== 原生效果 -> 被动 =====================

/// 一次放炮台：施法那一 tick 他站的地方、方向（`None`：施法输入里没有）。
#[derive(Clone, Debug)]
struct Put {
    kind: Kind,
    from: (f64, f64),
    dir: Option<(f64, f64)>,
    tick: usize,
    input_kind: u32,
    /// The body spawned for it (0.3.0).
    unit: Option<usize>,
}

/// 炮台朝左吗：方向往左（x 为负）才朝左，没有方向朝右（数据默认画朝右的）。
pub fn faces_left(dir: Option<(f64, f64)>) -> bool {
    dir.is_some_and(|d| d.0 < 0.0)
}

/// 一发从哪出来：朝右的炮口 `muzzle`（往前、往上，游戏像素 x 1000）按朝向翻过来，往南挪 5 px 减炮口高度（飞行物画在点上方 5 px）。
pub fn shot_from(pos: (f64, f64), muzzle: (i64, i64), left: bool) -> (f64, f64) {
    let dx = if left { -muzzle.0 } else { muzzle.0 } as f64;
    (pos.0 + dx, pos.1 + (5_000 - muzzle.1) as f64)
}

/// 每份模拟的编号（2026-11-01 复查；league_galio 的做法）：被动第一次出生时抽一个，每次出生挂在他身上（buff `SIM_TAG<n>`）。
/// 以前按（种子、模拟的来源、比赛、局）分：服务器并排跑的两份预演这些都一样，炮台和参数会混在一起。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
pub const SIM_TAG: &str = "league_heimerdinger_sim:";

fn sim_no(sim: &StableSim<'_>, id: usize) -> u64 {
    sim.get_entity(id).map_or(0, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .find_map(|b| b.name().strip_prefix(SIM_TAG).and_then(|v| v.parse().ok()))
            .unwrap_or(0)
    })
}

/// 原生效果放下、被动还没接走的炮台：按（这份模拟的编号、他的编号）分开。
type Key = (u64, usize);
static PUTS: LazyLock<Mutex<HashMap<Key, Vec<Put>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// 每个黑默丁格的参数（被动出场时放进来，钩子读）。
static PARAMS: LazyLock<Mutex<HashMap<Key, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&key(sim, me)).cloned().unwrap_or_default()
}

fn key(sim: &StableSim<'_>, me: usize) -> Key {
    (sim_no(sim, me), me)
}

/// `league_heimerdinger:q` / `:x`：副本里炮台的槽位空着、隐形弹出手的那一 tick。
struct Stand(Kind);

impl StableEffectType for Stand {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(e) = sim.get_entity(caster) else { return };
        let from = fpos(e.pos());
        let dir = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Dir) => Some((input.dir_x as f64, input.dir_y as f64)),
            Some(InputTargetKindV1::Pos) => Some((input.x as f64 - from.0, input.y as f64 - from.1)),
            Some(InputTargetKindV1::Target) => {
                sim.get_entity(input.target_id).map(|t| fpos(t.pos())).map(|t| (t.0 - from.0, t.1 - from.1))
            }
            _ => None,
        };
        // the data's bolt draws the turret when it lands: from the side facing the target (t_face_l: to his left)
        let face = hd(match self.0 {
            Kind::Turret => "t_face_l",
            Kind::Apex => "x_face_l",
        });
        sim.entity_remove_buff(caster, &face);
        if faces_left(dir) {
            sim.add_buff(caster, &BuffV1::timed(&face, FACE_T));
        }
        let unit = body(sim, caster, self.0, from, dir);
        let put = Put { kind: self.0, from, dir, tick: sim.tick(), input_kind: input.kind, unit };
        PUTS.lock().unwrap_or_else(|e| e.into_inner()).entry(key(sim, caster)).or_default().push(put);
    }
}

/// The body of the turret `kind` the cast at `from` toward `dir` stands: spawned where the hidden bolt stops, for the
/// turret's life from then; on success the flag for the data (no side picture) and the handoff for the passive. -> its id.
fn body(sim: &mut StableSim<'_>, me: usize, kind: Kind, from: (f64, f64), dir: Option<(f64, f64)>) -> Option<usize> {
    let (flag, prefix) = match kind {
        Kind::Turret => (T_UNIT, T_UID),
        Kind::Apex => (X_UNIT, X_UID),
    };
    sim.entity_remove_buff(me, flag);
    let p = params_of(sim, me);
    let (team, stat, max) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1))?;
    let at = summon::inside(summon::field(sim), stand_spot(from, dir, p.q_place as f64));
    let life = p.q_place.div_ceil(p.q_speed.max(1)) + match kind {
        Kind::Turret => p.t_life,
        Kind::Apex => p.x_life,
    };
    if KNOBS.off {
        if let Some(k) = tally(sim, "body knob") {
            wlog(format!("{} TURRET OFF #{k}: unit=off in the test knobs - the turret is the side picture as before", head(sim, me)));
        }
        return None;
    }
    let spec = turret_spec(kind, &p, &stat, max, life).with(&KNOBS);
    match summon::spawn(sim, me, team, at, &spec) {
        Some(id) => {
            sim.add_buff(me, &BuffV1::timed(&summon::handoff(prefix, id), UID_TICKS));
            sim.add_buff(me, &BuffV1::timed(flag, FLAG_TICKS));
            if let Some(k) = tally(sim, "body spawn") {
                wlog(format!("{} TURRET SPAWN #{k}: {kind:?}'s body, unit #{id} for team {team} at {}: {}", head(sim, me), summon::pt(at),
                             spec.shown()));
            }
            Some(id)
        }
        None => {
            if let Some(k) = tally(sim, "body fail") {
                wlog(format!("{} TURRET SPAWN FAILED #{k}: spawn_unit gave no unit for '{}' at {} - the side picture as before",
                             head(sim, me), spec.name, summon::pt(at)));
            }
            None
        }
    }
}

// ===================== 被动 =====================

#[derive(Clone, Debug)]
struct Turret {
    kind: Kind,
    pos: (f64, f64),
    left: bool,
    stand: usize,
    until: usize,
    next: usize,
    /// 0.3.0: its body (a unit of the flock), and the Q slot it took (freed when the body is destroyed).
    unit: Option<usize>,
    slot: Option<usize>,
}

/// 炮弹在飞：到了 `due` 再扣血。
#[derive(Clone, Debug)]
struct Flight {
    kind: Kind,
    fire: Fire,
    target: usize,
    due: usize,
    dmg: usize,
}

/// 每个黑默丁格一份。
#[derive(Clone)]
struct Workshop {
    p: Params,
    /// 这份模拟的编号（第一次出生时抽，见 `SIM_TAG`）。
    sim: u64,
    turrets: Vec<Turret>,
    flights: Vec<Flight>,
    next_haste: usize,
    n_put: usize,
    n_shot: usize,
    n_beam: usize,
    n_haste_turret: usize,
    n_haste_tower: usize,
    next_report: usize,
    /// 0.3.0: the turrets' and the apex's bodies; the Q slots that were busy at the last update (which one a put took).
    bodies: Flock<()>,
    apexes: Flock<()>,
    busy: [bool; 3],
}

impl Default for Workshop {
    fn default() -> Self {
        let p = Params::default();
        Workshop { p: p.clone(), sim: 0, turrets: Vec::new(), flights: Vec::new(), next_haste: 0, n_put: 0, n_shot: 0, n_beam: 0,
                   n_haste_turret: 0, n_haste_tower: 0, next_report: 0, bodies: Flock::new(T_UID, BODY_CAP, p.t_life),
                   apexes: Flock::new(X_UID, BODY_CAP, p.x_life), busy: [false; 3] }
    }
}

impl Workshop {
    /// 原生效果交过来的炮台：站在隐形弹停下的地方。
    fn take_puts(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let puts = PUTS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me)).unwrap_or_default();
        let busy = self.slots_now(sim, me);
        for put in puts {
            let pos = stand_spot(put.from, put.dir, self.p.q_place as f64);
            let stand = put.tick + self.p.q_place.div_ceil(self.p.q_speed);
            let (life, first) = match put.kind {
                Kind::Turret => (self.p.t_life, self.p.t_first),
                Kind::Apex => (self.p.x_life, self.p.x_first),
            };
            let left = faces_left(put.dir);
            // the Q slot this turret took: busy now, not at the last update
            let slot = (put.kind == Kind::Turret).then(|| (0..3).find(|&k| busy[k] && !self.busy[k])).flatten();
            self.turrets.push(Turret { kind: put.kind, pos, left, stand, until: stand + life, next: stand + first, unit: put.unit,
                                       slot });
            self.n_put += 1;
            if self.n_put <= 12 || self.n_put % 25 == 0 {
                wlog(format!("{} PUT #{}: {:?} at ({:.0}, {:.0}) from ({:.0}, {:.0}) facing {}, input kind {}{}, {} standing",
                             head(sim, me), self.n_put, put.kind, pos.0, pos.1, put.from.0, put.from.1,
                             if left { "left" } else { "right" }, put.input_kind,
                             if put.dir.is_some() { "" } else { " (no direction: at his feet)" }, self.turrets.len()));
            }
        }
    }

    /// The main pack's Q slots busy on him now.
    fn slots_now(&self, sim: &StableSim<'_>, me: usize) -> [bool; 3] {
        let mut out = [false; 3];
        if let Some(e) = sim.get_entity(me) {
            for (k, f) in SLOT_FLAGS.iter().enumerate() {
                out[k] = summon::has_buff(&e, f);
            }
        }
        out
    }

    /// The bodies' part of a tick: both flocks looked at; a destroyed body stops its turret and frees its slot.
    fn bodies_tick(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize, team: usize, here: (f64, f64)) {
        let tick = sim.tick();
        for apex in [false, true] {
            let events = if apex { self.apexes.tick(sim, me, team, player, Some(here)) } else { self.bodies.tick(sim, me, team, player, Some(here)) };
            let what = if apex { "the apex" } else { "a turret" };
            for ev in events {
                match ev {
                    Event::NoUnit { .. } => {}
                    Event::Look { id, n, line } => {
                        if let Some(k) = tally(sim, "body look") {
                            wlog(format!("{} TURRET #{n} LOOK #{k} ({what}'s body): {line}", head(sim, me)));
                        }
                        let _ = id;
                    }
                    Event::Lost { id, why, .. } => {
                        for t in self.turrets.iter_mut().filter(|t| t.unit == Some(id)) {
                            t.unit = None;
                        }
                        sim.entity_remove_buff(me, if apex { X_UNIT } else { T_UNIT });
                        if let Some(k) = tally(sim, "body lost") {
                            wlog(format!("{} TURRET LOST #{k}: the unit #{id} spawn_unit named never read as one in {} ticks ({why}) - \
                                          {what} fires from its spot without a body", head(sim, me), summon::FLOCK_LOOKS));
                        }
                    }
                    Event::Line { n, line, .. } => {
                        if let Some(k) = tally(sim, "body unit") {
                            wlog(format!("{} TURRET #{n} #{k}: {line}", head(sim, me)));
                        }
                    }
                    Event::Over { member, end } => {
                        let id = member.unit.id;
                        let mut then = String::new();
                        if end.fate == summon::Fate::Killed {
                            let (gone, kept): (Vec<Turret>, Vec<Turret>) =
                                std::mem::take(&mut self.turrets).into_iter().partition(|t| t.unit == Some(id));
                            self.turrets = kept;
                            for t in gone {
                                then += &format!(" - {:?} destroyed: it stops firing {} ticks early", t.kind, t.until.saturating_sub(tick));
                                if let Some(k) = t.slot {
                                    sim.entity_remove_buff(me, SLOT_FLAGS[k]);
                                    then += &format!(", Q's slot {} free again", ["a", "b", "c"][k]);
                                }
                            }
                            if end.age <= LOST_AGE {
                                sim.entity_remove_buff(me, if apex { X_UNIT } else { T_UNIT });
                            }
                        }
                        if let Some(k) = tally(sim, "body over") {
                            wlog(format!("{} TURRET #{} OVER #{k} ({what}'s body): {}{then}", head(sim, me), member.unit.n, end.text));
                        }
                    }
                    Event::LetGo { member } => {
                        if let Some(k) = tally(sim, "body let go") {
                            wlog(format!("{} TURRET #{} LET GO #{k}: {BODY_CAP} bodies on the books - the unit #{} is out there, no \
                                          longer watched", head(sim, me), member.unit.n, member.unit.id));
                        }
                    }
                    Event::Wake { n, line } => {
                        if let Some(k) = tally(sim, "body wake") {
                            wlog(format!("{} TURRET #{n} WAKE #{k}: {line}", head(sim, me)));
                        }
                    }
                }
            }
        }
    }

    /// Where a turret's body stands now (its unit alive under its id), if it has one.
    fn body_at(&self, sim: &StableSim<'_>, t: &Turret) -> Option<(f64, f64)> {
        let id = t.unit?;
        let m = self.bodies.get(id).or_else(|| self.apexes.get(id))?;
        sim.get_entity(id).filter(|e| e.is_alive() && e.name().unwrap_or_default() == m.unit.name).map(|e| fpos(e.pos()))
    }

    /// A line for a hook that fired while bodies of his are out.
    fn hooked(&self, sim: &StableSim<'_>, hook: &str, me: usize, entity: usize, other: usize, damage: Option<usize>) {
        if self.bodies.live.is_empty() && self.apexes.live.is_empty() {
            return;
        }
        let who = match self.bodies.get(entity).or_else(|| self.apexes.get(entity)) {
            Some(m) => format!("the body #{}", m.unit.n),
            None if entity == me => "Heimerdinger".to_string(),
            None => "neither Heimerdinger nor a body of his".to_string(),
        };
        if let Some(k) = tally(sim, "body hook") {
            wlog(format!("{} TURRET HOOK #{k} {hook}: entity #{entity} ({who}) -> #{other}{}", head(sim, me),
                         damage.map(|d| format!(", damage {d}")).unwrap_or_default()));
        }
    }

    fn fire(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, ap: usize) {
        let tick = sim.tick();
        self.turrets.retain(|t| t.until > tick);
        if self.turrets.iter().all(|t| t.next > tick) {
            return;
        }
        let units = enemies(sim, team);
        let mut flights = Vec::new();
        let at: Vec<Option<(f64, f64)>> = self.turrets.iter().map(|t| self.body_at(sim, t)).collect();
        for (t, body) in self.turrets.iter_mut().zip(at) {
            if t.next > tick {
                continue;
            }
            let p = &self.p;
            let (per, reach) = match t.kind {
                Kind::Turret => (p.t_per, p.t_r),
                Kind::Apex => (p.x_per, p.x_r),
            };
            t.next = tick + per;
            // with a body: from where it stands now (pushed, pulled), its muzzle on the side of the one it fires at (the
            // game turns a unit toward its target); without: the spot and the side picture as before
            let pos = body.unwrap_or(t.pos);
            if body.is_some() {
                t.pos = pos;
            }
            let Some((u, fire)) = choose(&units, pos, reach as f64) else { continue };
            let from = match (body.is_some(), t.kind) {
                (true, Kind::Turret) => shot_from(pos, TU_MUZZLE, u.pos.0 < pos.0),
                (true, Kind::Apex) => shot_from(pos, XU_MUZZLE, u.pos.0 < pos.0),
                (false, Kind::Turret) => shot_from(pos, T_MUZZLE, t.left),
                (false, Kind::Apex) => shot_from(pos, X_MUZZLE, t.left),
            };
            let (pic, speed, dmg) = match (t.kind, fire) {
                (Kind::Turret, Fire::Cannon) => ("t_shot", p.t_speed, shot_damage(p.t_dmg, p.t_ratio, ap)),
                (Kind::Turret, Fire::Beam) => ("t_beam_line", p.b_speed, shot_damage(p.tb_dmg, p.tb_ratio, ap)),
                (Kind::Apex, Fire::Cannon) => ("x_shot", p.x_speed, shot_damage(p.x_dmg, p.x_ratio, ap)),
                (Kind::Apex, Fire::Beam) => ("t_beam_line", p.b_speed, shot_damage(p.xb_dmg, p.xb_ratio, ap)),
            };
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team,
                x: from.0.round().max(0.0) as u64,
                y: from.1.round().max(0.0) as u64,
                radius: 1_000,
                speed: speed as u64,
                move_kind: ProjectileMoveKindV1::Target.code(),
                target_id: u.id,
                target_x: 0,
                target_y: 0,
                penetrate: false,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::None.code(),
            };
            sim.spawn_projectile(&hd(pic), &format!("{ID}:noop"), &spec);
            let fly = (dist(from, u.pos) / speed as f64).ceil() as usize;
            flights.push(Flight { kind: t.kind, fire, target: u.id, due: tick + fly.max(1), dmg });
            if fire == Fire::Beam {
                self.n_beam += 1;
            }
            self.n_shot += 1;
            if self.n_shot <= 12 || self.n_shot % 100 == 0 {
                wlog(format!("{} SHOT #{}: {:?} -> #{} ({}) {:?} for {dmg}", head(sim, me), self.n_shot, t.kind, u.id,
                             if u.in_cc { "champion in cc" } else if u.champion { "champion" } else { "unit" }, fire));
            }
        }
        self.flights.extend(flights);
    }

    /// 飞到的炮弹扣血（巨型炮台的等离子弹还减速）。
    fn land(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        let (due, wait): (Vec<Flight>, Vec<Flight>) = std::mem::take(&mut self.flights).into_iter().partition(|f| f.due <= tick);
        self.flights = wait;
        for f in due {
            if !sim.get_entity(f.target).is_some_and(|e| e.is_alive()) {
                continue;
            }
            sim.deal_damage_typed(me, f.target, f.dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            let (pic, snd) = match (f.kind, f.fire) {
                (Kind::Turret, Fire::Cannon) => ("t_hit", "t_hit"),
                (Kind::Turret, Fire::Beam) => ("t_beam", "t_beam"),
                (Kind::Apex, Fire::Cannon) => ("x_hit", "x_hit"),
                (Kind::Apex, Fire::Beam) => ("x_beam", "t_beam"),
            };
            if f.kind == Kind::Apex && f.fire == Fire::Cannon {
                let mut slow = BuffV1::timed(&hd("x_slow"), self.p.x_slow_t);
                slow.move_speed_mult = -(self.p.x_slow as i32);
                sim.entity_remove_buff(f.target, &hd("x_slow"));
                sim.add_buff(f.target, &slow);
            }
            let hit = InputTargetV1::target(f.target);
            sim.play_view_effect(&hd(pic), me, &hit, 0, 0, 0);
            sim.play_sfx(&hd(snd), me, &hit);
        }
    }

    /// 海克斯科技亲和：炮台旁或己方防御塔旁加速。
    fn haste(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (f64, f64)) {
        let tick = sim.tick();
        if tick < self.next_haste {
            return;
        }
        self.next_haste = tick + self.p.p_per;
        let by_turret = self.turrets.iter().any(|t| t.stand <= tick && dist(t.pos, pos) <= self.p.p_r as f64);
        let by_tower = !by_turret
            && (0..sim.tower_count()).filter_map(|i| sim.get_entity(sim.tower_id_at(i))).any(|t| {
                t.team() == team && t.is_alive() && dist(fpos(t.pos()), pos) <= self.p.p_tr as f64
            });
        if !(by_turret || by_tower) {
            return;
        }
        let name = hd("haste");
        let mut b = BuffV1::timed(&name, self.p.p_t);
        b.move_speed_mult = self.p.p_ms as i32;
        sim.entity_remove_buff(me, &name);
        sim.add_buff(me, &b);
        let n = if by_turret {
            self.n_haste_turret += 1;
            self.n_haste_turret
        } else {
            self.n_haste_tower += 1;
            self.n_haste_tower
        };
        if n <= 4 {
            wlog(format!("{} HASTE: +{}% by {} (#{n})", head(sim, me), self.p.p_ms, if by_turret { "a turret" } else { "a tower" }));
        }
    }
}

impl StablePassive for Workshop {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
        let lag = self.p.q_place.div_ceil(self.p.q_speed.max(1));
        self.bodies.life = lag + self.p.t_life;
        self.apexes.life = lag + self.p.x_life;
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if self.sim == 0 {
            self.sim = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        // a stale put of an earlier life
        PUTS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me));
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(key(sim, me), self.p.clone());
        wlog(format!("{} SPAWN: the add-on's Heimerdinger (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, ap, pos, alive) = (e.team(), e.stat().magic_power, fpos(e.pos()), e.is_alive());
        let tick = sim.tick();
        // his turrets stand and fire after his death (League's; the main pack's zones too)
        self.take_puts(sim, me);
        self.bodies_tick(sim, player, me, team, pos);
        self.busy = self.slots_now(sim, me);
        self.land(sim, me);
        self.fire(sim, me, team, ap);
        if alive {
            self.haste(sim, me, team, pos);
        }
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 && self.n_put > 0 {
                wlog(format!("{} WATCH: turrets put {} ({} standing, {} with a body), shots {} ({} beams), haste by turrets {} / towers {}",
                             head(sim, me), self.n_put, self.turrets.len(), self.turrets.iter().filter(|t| t.unit.is_some()).count(),
                             self.n_shot, self.n_beam, self.n_haste_turret, self.n_haste_tower));
            }
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, me: usize, entity: usize, target: usize, damage: &mut usize) {
        self.hooked(sim, "on_attack", me, entity, target, Some(*damage));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, me: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_kill", me, entity, victim, None);
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, me: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_unit_kill", me, entity, victim, None);
    }
}

struct NoopFx;
impl StableEffectType for NoopFx {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Heimerdinger's turrets firing visible shots, Hextech Affinity by towers too, R's upgrade picked, the turrets bodies of their own) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "TURRETS: Q's turrets and the apex have bodies of their own ('{H28G}' / '{H28Q}', spawn_unit: move speed 1, a harmless \
         attack, {TURRET_HP_PCT}% / {APEX_HP_PCT}% of his health) - {}; the add-on fires their shots as before, a destroyed body \
         stops its turret. Test knobs ({}): {}",
        if KNOBS.off { "OFF by the test knobs: the turrets are side pictures as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(), KNOBS.shown()
    ));
    module.add_native_effect(format!("{ID}:noop"), NoopFx);
    module.add_native_effect(format!("{ID}:q"), Stand(Kind::Turret));
    module.add_native_effect(format!("{ID}:x"), Stand(Kind::Apex));
    module.add_native_passive(format!("{ID}:affinity"), Workshop::default());
    module.add_player_input_ai(combo::Combo::default());
    host.log(LogLevel::Info, "league_heimerdinger v1 loaded (turrets firing visible shots, Hextech Affinity by towers too, R's upgrade picked).");
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
mod tests {
    use super::*;

    #[test]
    fn the_sim_tag_fits_a_buff_name() {
        assert!(format!("{SIM_TAG}{}", u64::MAX).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"t_per":40,"p_tr":70000,"x":1}"#);
        assert_eq!((p.t_per, p.p_tr), (40, 70000));
        assert_eq!(p.x_per, Params::default().x_per);
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"t_per":0,"q_speed":0}"#).t_per, 1);
        assert_eq!(parse_params(r#"{"x_slow":200}"#).x_slow, 95);
    }

    #[test]
    fn shots_scale_with_ability_power() {
        assert_eq!(shot_damage(6, 4, 0), 6);
        assert_eq!(shot_damage(6, 4, 100), 10);
        assert_eq!(shot_damage(45, 30, 150), 90);
    }

    #[test]
    fn turrets_stand_where_the_bolt_stops() {
        let s = stand_spot((100_000.0, 50_000.0), Some((3.0, 4.0)), 20_000.0);
        assert!((s.0 - 112_000.0).abs() < 1e-6 && (s.1 - 66_000.0).abs() < 1e-6);
        assert_eq!(stand_spot((1.0, 2.0), None, 20_000.0), (1.0, 2.0));
        assert_eq!(stand_spot((1.0, 2.0), Some((0.0, 0.0)), 20_000.0), (1.0, 2.0));
    }

    #[test]
    fn side_turrets_face_their_target_and_fire_from_the_muzzle() {
        assert!(faces_left(Some((-3.0, 1.0))));
        assert!(!faces_left(Some((3.0, -1.0))));
        assert!(!faces_left(None));
        assert_eq!(shot_from((100_000.0, 50_000.0), (10_000, 2_000), false), (110_000.0, 53_000.0));
        assert_eq!(shot_from((100_000.0, 50_000.0), (10_000, 2_000), true), (90_000.0, 53_000.0));
        assert!(hd("t_face_l").len() <= BUFF_NAME_CAP && hd("x_face_l").len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn crowd_control_as_the_game_counts_it() {
        for k in [0, 1, 2, 6, 8, 9] {
            assert!(hard_cc([k]), "{k}");
        }
        for k in [3, 4, 5, 7, 10] {
            assert!(!hard_cc([k]), "{k}");
        }
        assert!(!hard_cc([]));
        assert!(hard_cc([4, 1]));
    }

    #[test]
    fn beams_first_then_champions_then_the_rest() {
        let u = |id, x: f64, champion, in_cc| Unit { id, pos: (x, 0.0), champion, in_cc };
        let units = [u(1, 1_000.0, false, false), u(2, 20_000.0, true, false), u(3, 45_000.0, true, true)];
        assert_eq!(choose(&units, (0.0, 0.0), 50_000.0).map(|(u, f)| (u.id, f)), Some((3, Fire::Beam)));
        assert_eq!(choose(&units, (0.0, 0.0), 30_000.0).map(|(u, f)| (u.id, f)), Some((2, Fire::Cannon)));
        assert_eq!(choose(&units, (0.0, 0.0), 10_000.0).map(|(u, f)| (u.id, f)), Some((1, Fire::Cannon)));
        assert!(choose(&units, (200_000.0, 0.0), 10_000.0).is_none());
    }

    #[test]
    fn buff_names_fit() {
        for x in ["haste", "x_slow", "t_shot", "t_beam_line", "x_shot", "t_hit", "x_beam"] {
            assert!(hd(x).len() <= BUFF_NAME_CAP);
        }
    }

    // ---- 0.3.0: the turrets' bodies ----

    #[test]
    fn the_bodies_are_built_from_his_numbers() {
        let his = StatV1 { attack: 70, magic_power: 100, hp: 1200, defence: 40, magic_resistance: 30, move_speed: 950, hp_regen: 2,
                           stack: 0, crit_chance: 0 };
        let p = Params::default();
        let g = turret_spec(Kind::Turret, &p, &his, 1500, 605);
        assert_eq!((g.name.as_str(), g.life), (H28G, 605));
        assert_eq!(g.stat, StatV1 { attack: 0, magic_power: 100, hp: 390 + 30, defence: 36, magic_resistance: 37, move_speed: 1,
                                    hp_regen: 0, stack: 0, crit_chance: 0 });
        // harmless, in the turret's reach and pace
        assert_eq!((g.attack.attack, g.attack.attack_ratio, g.attack.range, g.attack.cooltime), (0, 0, p.t_r, p.t_per));
        assert_eq!((g.attack.duration, g.attack.start_timing), (TU_ACT, TU_LANDS));
        let q = turret_spec(Kind::Apex, &p, &his, 1500, 485);
        assert_eq!((q.name.as_str(), q.stat.hp, q.stat.defence, q.stat.magic_resistance), (H28Q, 1275 + 50, 44, 45));
        assert_eq!((q.attack.range, q.attack.cooltime, q.attack.duration, q.attack.start_timing), (p.x_r, p.x_per, XU_ACT, XU_LANDS));
        // a knob may rename; still is already so
        assert_eq!(turret_spec(Kind::Turret, &p, &StatV1::default(), 0, 1).stat.hp, 1);
        for name in [T_UNIT, X_UNIT, &summon::handoff(T_UID, usize::MAX), &summon::handoff(X_UID, usize::MAX)] {
            assert!(name.starts_with("league_heimerdinger_") && name.len() <= BUFF_NAME_CAP, "{name}");
        }
    }

    #[test]
    fn the_copy_draws_no_side_turret_under_a_body() {
        let copy = include_str!("../override/league_heimerdinger.data_champion");
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{T_UNIT}\"")).count(), 3, "the three slots' turrets");
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{X_UNIT}\"")).count(), 1, "the apex");
        for f in SLOT_FLAGS {
            assert!(copy.contains(&format!("\"{f}\"")), "{f}");
        }
    }

    use super::mock::{champion, MPlayer, World};

    const GAREN: usize = 1;

    fn log_file() -> std::path::PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_heimerdinger_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_HEIMERDINGER_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// Heimerdinger #0 (team 0, 1500 health) at (300000, 300000); Garen #1 40000 east of him; two more far off; a player
    /// each for the champions.
    fn world() -> (World, Workshop) {
        log_file();
        let mut w = World::default();
        let mut heimer = champion("league_heimerdinger", 0, 300_000.0, 300_000.0);
        (heimer.hp, heimer.max) = (1500, 1500);
        let mut garen = champion("league_garen", 1, 340_000.0, 300_000.0);
        (garen.hp, garen.max) = (50_000, 50_000);
        w.units = vec![heimer, garen, champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() }];
        let mut me = Workshop::default();
        me.configure("{}");
        w.sim(|sim| me.on_spawn(sim, 0, 0));
        (w, me)
    }

    fn tick(w: &mut World, me: &mut Workshop) {
        w.sim(|sim| me.on_update(sim, 0, 0, 0));
        w.step();
    }

    fn run(w: &mut World, me: &mut Workshop, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    /// The copy's Q: slot `k`'s busy flag (the data lays it first), then the native put toward Garen.
    fn cast(w: &mut World, kind: Kind, slot: Option<usize>) {
        if let Some(k) = slot {
            w.units[0].buffs.push((BuffV1::timed(SLOT_FLAGS[k], 600), 600));
        }
        let input = InputTargetV1::target(GAREN);
        w.sim(|sim| Stand(kind).apply(sim, 0, 0, input));
    }

    fn bodies(w: &World, name: &str) -> Vec<usize> {
        w.spawns.iter().filter(|s| s.name == name).filter_map(|s| s.gave).collect()
    }

    #[test]
    fn a_turret_gets_a_body_and_fires_from_it() {
        let (mut w, mut me) = world();
        cast(&mut w, Kind::Turret, Some(0));
        let ids = bodies(&w, H28G);
        assert_eq!(ids.len(), 1);
        // where the hidden bolt stops: q_place toward Garen; the flag on him before it lands
        let s = &w.spawns[0];
        assert_eq!((s.at, s.life as usize, s.stat.move_speed), ((320_000, 300_000), 5 + Params::default().t_life, 1));
        assert!(w.has(0, T_UNIT));
        run(&mut w, &mut me, 5);
        assert!(w.has(0, T_UNIT), "the flag must outlast the bolt's 5 ticks");
        assert_eq!(me.turrets.len(), 1);
        assert_eq!((me.turrets[0].unit, me.turrets[0].slot), (Some(ids[0]), Some(0)));
        // its shots: the add-on's, magic, on Garen
        run(&mut w, &mut me, 120);
        let shots = w.dealt(0, DamageTypeV1::Ap);
        assert!(!shots.is_empty() && shots.iter().all(|d| d.0 == GAREN), "{shots:?}");
        // the body's own attack harms nobody
        assert!(w.damage.iter().filter(|d| d.1 == ids[0]).all(|d| d.3 == 0));
        // pushed 30000 north: it fires from there
        w.units[ids[0]].y = 270_000.0;
        run(&mut w, &mut me, 60);
        assert_eq!(me.turrets[0].pos, (320_000.0, 270_000.0));
        // destroyed: the turret stops firing and Q's slot is free again
        w.hurt(ids[0], 1_000_000);
        run(&mut w, &mut me, 3);
        assert!(me.turrets.is_empty());
        assert!(!w.has(0, SLOT_FLAGS[0]));
        let before = w.dealt(0, DamageTypeV1::Ap).len();
        run(&mut w, &mut me, 200);
        assert!(w.dealt(0, DamageTypeV1::Ap).len() <= before + 1, "a destroyed turret fired on");
    }

    #[test]
    fn the_apex_gets_a_body_for_its_own_time() {
        let (mut w, mut me) = world();
        cast(&mut w, Kind::Apex, None);
        let ids = bodies(&w, H28Q);
        assert_eq!(ids.len(), 1);
        assert_eq!(w.spawns[0].life as usize, 5 + Params::default().x_life);
        assert!(w.has(0, X_UNIT) && !w.has(0, T_UNIT));
        run(&mut w, &mut me, 5 + Params::default().x_life + 10);
        assert!(me.turrets.is_empty() && me.apexes.live.is_empty());
        assert!(!w.dealt(0, DamageTypeV1::Ap).is_empty());
    }

    #[test]
    fn no_body_from_the_host_keeps_the_picture_and_the_shots() {
        for case in 0..3 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                _ => w.spawn_never = true,
            }
            cast(&mut w, Kind::Turret, Some(1));
            run(&mut w, &mut me, 5);
            assert!(!w.has(0, T_UNIT), "case {case}: the flag on him without a body when the bolt lands");
            run(&mut w, &mut me, 120);
            assert_eq!(me.turrets.len(), 1, "case {case}");
            assert!(!w.dealt(0, DamageTypeV1::Ap).is_empty(), "case {case}: no shots");
            assert!(w.has(0, SLOT_FLAGS[1]), "case {case}");
        }
    }

    #[test]
    fn the_log_tells_the_bodies_lives() {
        let (mut w, mut me) = world();
        cast(&mut w, Kind::Turret, Some(2));
        run(&mut w, &mut me, 100);
        let ids = bodies(&w, H28G);
        let mut d = 0;
        w.sim(|sim| me.on_attack(sim, 0, ids[0], GAREN, &mut d));
        w.players[1].gold += 5;
        w.hurt(ids[0], 1_000_000);
        run(&mut w, &mut me, 10);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" TURRET")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "TURRET SPAWN #", "Turret's body, unit #4 for team 0 at (320000,300000): 'league_heimerdinger_h28g' for 605 ticks, attack 0",
            "speed 1; hits 0 + 0% of its attack, range 50000, every 50 ticks (15 long, lands at 6)",
            "TURRET #1 LOOK #", "(a turret's body): #4 reads back as name 'league_heimerdinger_h28g'", " of 605 ticks, at (",
            "TURRET HOOK #", "on_attack: entity #4 (the body #1) -> #1, damage 0",
            "OVER #", "KILLED after ", "p1 gold +5", "Turret destroyed: it stops firing", "Q's slot c free again",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
    }
}
