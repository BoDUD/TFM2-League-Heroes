//! 亚恒附加包：数据做不到、和英雄联盟不一样的地方，这里照英雄联盟做（用户：「和英雄联盟不一样的地方都要做附加包」）。
//!
//! `mod.override_info` 把主包的亚恒换成 `override/` 里的副本（tools/kit/build_zaahen.py --native），`passive` 换成本包的
//! `league_zaahen:darkin`：
//!
//! - **不落之志照英雄联盟叠**：主包只能用一串标记一层一层叠（控制器 3 拍看一次，同一拍里的几下只算一层）。本包每一下打在敌方英雄身上的
//!   伤害（普攻、Q 的每一斩、挑飞、W 的两段、E、R）都算一层，最多 `det_n` 层，每层攻击力 +`det_lo`..`det_hi` 万分之（随等级，
//!   英雄联盟 1.5%–2.95%，`league_zaahen_det`）；最后一下之后 `det_t` 拍没再打中英雄就开始掉：每 30 拍掉 1/2/3/4/5 层（掉了几秒，
//!   英雄联盟的越掉越快）。叠满时攻击力翻倍（`league_zaahen_full`：主包数据用它播身后的暗裔气焰），并挂 `league_zaahen_fill` 让
//!   数据播叠满的画面（2026-11-12 起不再刷新 Q 和 W：英雄联盟没有这个连招）。
//! - **叠满就能复活**：主包数据看不到致命伤害，只能叠满时给一个护盾。本包在他叠满、复活冷却好了的时候一直给他挂「不死」，生命停在
//!   1 时不倒下：放逐他 `rv_rise` 拍（无敌、选不中、不能行动；画面是数据的 `league_zaahen_rv_rise_r` / `_l`：他跪起、展翼站起来，
//!   朝着最近的敌方英雄——特效图不会镜像，所以左右各画一份），这段时间里慢慢回到最大生命的 30/45/60/75%，冷却 300/240/180/120 秒
//!   （1/6/11/16 级起，英雄联盟的数：`rv_hp` + `rv_hp_step`、`rv_cd` - `rv_cd_step`，每 `rv_lv` 级一档），起来后果决重新叠满。
//!   放逐期间他的生命就是复活的进度（0.2.1，英雄联盟：这段时间别的治疗不起作用；11-12 的日志有一次站起来时 83%，该是 60%）。
//!   别人给的「不死」在身上时不触发。
//! - **赤金突袭有自己的技能位**：主包三个技能位放不下第四个技能，只能把 E 并进 W（拽完人原地绕身一斩）。本包每 `e_cd` 拍一次：
//!   `e_reach` 内有敌方英雄、他能行动时，朝最近的那个冲过去（最多 `e_dash`，停在让对方正好落在外圈的地方；冲的时候挂
//!   `league_zaahen_e_rush`，数据播冲刺的动作），落地挂
//!   `league_zaahen_e_go`，数据播绕身斩（skill3），`e_hit` 拍后本包按英雄联盟结算：内圈 `e_r0`、外圈 `e_r` 里的敌人受到
//!   `e_dmg` + `e_ratio`% 攻击力的物理伤害，外圈多 `e_out`%，外圈再加最大生命 `e_pct`% 的魔法伤害。
//! - **暗裔长刀按最大生命回血**：主包回固定的血。副本给第一斩打中的单位挂 3 拍 `league_zaahen_q_mark`（一次 Q 回一次，2026-11-12
//!   以前每斩都回）；本包看到就给他回最大生命的 5–9%（`q_hp` + `q_hp_step` 乘技能等级 - 1：英雄联盟主升 Q 在 1/4/5/7/9 级升级；
//!   打别的单位一半）。
//! - **大赦的护甲穿透随技能等级**：副本的 `own` 给 `r_pen_n`%，本包按等级再加（`league_zaahen_pen`：英雄联盟 10/20/30%，大招
//!   在 6/11/16 级升级）。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。不用全局变量，服务端预模拟和
//! 你看的那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zaahen.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_zaahen";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_zaahen") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 「不死」挂多久、多久续一次（league_zac 的做法）。
pub const GUARD_T: usize = 30;
pub const GUARD_EVERY: usize = 10;
/// 给主包数据读的标记留几拍：数据的控制器每 3 拍看一次。
pub const FLAG_T: usize = 6;
/// 果决没打中英雄 `det_t` 拍后每这么多拍掉一层。
pub const DECAY_EVERY: usize = 30;
/// 复活时每这么多拍补一次血。
pub const RISE_STEP: usize = 8;
/// 赤金突袭冲多少拍。
pub const DASH_T: usize = 10;
/// 单位半径拿不到时用的身体半径（league_ornn 的 BODY）。
const BODY: f64 = 6000.0;

fn sn(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ZAAHEN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_zaahen.log");
        }
    }
    PathBuf::from("league_zaahen.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub fn wlog(msg: impl AsRef<str>) {
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

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
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

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).unwrap_or_else(|| format!("#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，build_zaahen.NATIVE_KEYS）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 果决最多几层；每层攻击力（万分之一，1 级 `det_lo`、`det_lv` 级 `det_hi`，中间按等级线性）；最后一下之后多少拍开始掉。
    pub det_n: usize,
    pub det_lo: usize,
    pub det_hi: usize,
    pub det_lv: usize,
    pub det_t: usize,
    /// 复活：放逐多少拍；回到最大生命的百分比和每档多加的；两次复活之间的拍数和每档少的；每几级一档。
    pub rv_rise: usize,
    pub rv_hp: usize,
    pub rv_hp_step: usize,
    pub rv_cd: usize,
    pub rv_cd_step: usize,
    pub rv_lv: usize,
    /// 赤金突袭：冷却、找目标的范围、最远冲多远。
    pub e_cd: usize,
    pub e_reach: u64,
    pub e_dash: u64,
    /// 赤金突袭：内圈、外圈半径，外圈多几成伤害，外圈最大生命百分比的魔法伤害，基础伤害和攻击力百分比，落地后几拍结算。
    pub e_r0: u64,
    pub e_r: u64,
    pub e_out: usize,
    pub e_pct: usize,
    pub e_dmg: usize,
    pub e_ratio: usize,
    pub e_hit: usize,
    /// 暗裔长刀（一次 Q 第一斩）打中英雄回最大生命的百分比、技能每升一级多的（别的单位一半）。
    pub q_hp: usize,
    pub q_hp_step: usize,
    /// 大赦的护甲穿透：副本自带的（技能 1 级）、每升一级多的。
    pub r_pen_n: usize,
    pub r_pen_step: usize,
    /// 他的普攻距离（赤金突袭在这个距离里也会用：英雄联盟里它也拿来打伤害）。
    pub atk_range: u64,
}

impl Default for Params {
    fn default() -> Self {
        Self { det_n: 12, det_lo: 150, det_hi: 295, det_lv: 18, det_t: 300, rv_rise: 240, rv_hp: 30, rv_hp_step: 15,
               rv_cd: 18000, rv_cd_step: 3600, rv_lv: 5, e_cd: 540, e_reach: 48000, e_dash: 22000, e_r0: 13000,
               e_r: 25000, e_out: 50, e_pct: 5, e_dmg: 88, e_ratio: 88, e_hit: 14, q_hp: 5, q_hp_step: 1, r_pen_n: 10,
               r_pen_step: 10, atk_range: 25000 }
    }
}

/// `{"det_n":12,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        let u = v as usize;
        match k {
            "det_n" => p.det_n = u,
            "det_lo" => p.det_lo = u,
            "det_hi" => p.det_hi = u,
            "det_lv" => p.det_lv = u,
            "det_t" => p.det_t = u,
            "rv_rise" => p.rv_rise = u,
            "rv_hp" => p.rv_hp = u,
            "rv_hp_step" => p.rv_hp_step = u,
            "rv_cd" => p.rv_cd = u,
            "rv_cd_step" => p.rv_cd_step = u,
            "rv_lv" => p.rv_lv = u,
            "e_cd" => p.e_cd = u,
            "e_reach" => p.e_reach = v,
            "e_dash" => p.e_dash = v,
            "e_r0" => p.e_r0 = v,
            "e_r" => p.e_r = v,
            "e_out" => p.e_out = u,
            "e_pct" => p.e_pct = u,
            "e_dmg" => p.e_dmg = u,
            "e_ratio" => p.e_ratio = u,
            "e_hit" => p.e_hit = u,
            "q_hp" => p.q_hp = u,
            "q_hp_step" => p.q_hp_step = u,
            "r_pen_n" => p.r_pen_n = u,
            "r_pen_step" => p.r_pen_step = u,
            "atk_range" => p.atk_range = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// `pct`% of `of`, at least 1 when `of` is not 0.
pub fn share(of: usize, pct: usize) -> usize {
    if of == 0 { 0 } else { (of * pct / 100).max(1) }
}

/// 果决每层的攻击力（万分之一）：1 级 det_lo，det_lv 级 det_hi，中间按等级线性（英雄联盟 1.5%–2.95%）。
pub fn det_per_stack(p: &Params, level: usize) -> usize {
    let span = p.det_lv.max(2) - 1;
    let k = level.clamp(1, p.det_lv.max(1)) - 1;
    p.det_lo + (p.det_hi.saturating_sub(p.det_lo)) * k / span
}

/// 果决的攻击力百分比：每层 det_per_stack，叠满翻倍（英雄联盟 1 级满层 36%、18 级 70.87%）。
pub fn det_attack(p: &Params, stacks: usize, level: usize) -> i32 {
    let a = stacks.min(p.det_n) * det_per_stack(p, level) * if stacks >= p.det_n { 2 } else { 1 };
    ((a + 50) / 100) as i32
}

/// 果决这一拍要掉几层：最后一下之后 det_t 拍内不掉；之后每 DECAY_EVERY 拍掉一次，第 k 次（从 0 数）掉 1 + k / 2 层、最多 5
/// （英雄联盟：每 0.5 秒掉 1/2/3/4/5 层，按掉了几秒）。
pub fn decayed(p: &Params, last_hit: usize, now: usize, already: usize) -> usize {
    if now < last_hit + p.det_t {
        return 0;
    }
    let k = (now - last_hit - p.det_t) / DECAY_EVERY;
    let due: usize = (0..=k).map(|i| (1 + i / 2).min(5)).sum();
    due.saturating_sub(already)
}

/// 复活的档：每 rv_lv 级一档，最多 3（英雄联盟 1/6/11/16 级）。
pub fn revive_tier(p: &Params, level: usize) -> usize {
    ((level.max(1) - 1) / p.rv_lv.max(1)).min(3)
}

/// 这一级复活回到最大生命的百分比（30/45/60/75）。
pub fn revive_hp(p: &Params, level: usize) -> usize {
    p.rv_hp + p.rv_hp_step * revive_tier(p, level)
}

/// 这一级两次复活之间的拍数（300/240/180/120 秒）。
pub fn revive_cd(p: &Params, level: usize) -> usize {
    p.rv_cd.saturating_sub(p.rv_cd_step * revive_tier(p, level))
}

/// 复活期间每次补多少（一共 hp_pct% 最大生命，分成 rv_rise / RISE_STEP 次）。
pub fn rise_step(p: &Params, max_hp: usize, hp_pct: usize) -> usize {
    let steps = (p.rv_rise / RISE_STEP).max(1);
    (share(max_hp, hp_pct) / steps).max(1)
}

/// 复活开始 `elapsed` 拍后他的生命：1 加上已经过去的每一步（0.2.1，英雄联盟把生命强制成这个进度：别的治疗不加）。
pub fn rise_hp(p: &Params, max_hp: usize, hp_pct: usize, elapsed: usize) -> usize {
    let steps = elapsed.min(p.rv_rise) / RISE_STEP;
    (1 + rise_step(p, max_hp, hp_pct) * steps).min(max_hp.max(1))
}

/// 暗裔长刀的技能等级：英雄联盟主升 Q，1/4/5/7/9 级升到 1–5 级。
pub fn q_rank(level: usize) -> usize {
    match level {
        0..=3 => 1,
        4 => 2,
        5 | 6 => 3,
        7 | 8 => 4,
        _ => 5,
    }
}

/// 一次暗裔长刀回最大生命的百分比：打英雄 q_hp + q_hp_step x (技能等级 - 1)（英雄联盟 5–9%），别的单位一半。
pub fn glaive_pct(p: &Params, level: usize, champion: bool) -> usize {
    let pct = p.q_hp + p.q_hp_step * (q_rank(level) - 1);
    if champion { pct } else { (pct / 2).max(1) }
}

/// 大赦的技能等级：英雄联盟 6/11/16 级升级（这里 11 级前都是 1 级）。
pub fn r_rank(level: usize) -> usize {
    match level {
        0..=10 => 1,
        11..=15 => 2,
        _ => 3,
    }
}

/// 本包在副本自带的 r_pen_n 之外再加的护甲穿透（英雄联盟 10/20/30%）。
pub fn extra_pen(p: &Params, level: usize) -> usize {
    p.r_pen_step * (r_rank(level) - 1)
}

/// 赤金突袭冲到哪：朝目标冲，停在目标正好落在内外圈中间的地方；最多 e_dash，离得太近时往后退最多一半。
pub fn dash_to(p: &Params, me: (f64, f64), target: (f64, f64)) -> (f64, f64) {
    let (dx, dy) = (target.0 - me.0, target.1 - me.1);
    let d = (dx * dx + dy * dy).sqrt();
    if d < 1.0 {
        return me;
    }
    let ring = (p.e_r0 + p.e_r) as f64 / 2.0;
    let step = (d - ring).clamp(-(p.e_dash as f64) / 2.0, p.e_dash as f64);
    (me.0 + dx / d * step, me.1 + dy / d * step)
}

/// 赤金突袭打在离他 `dist` 的单位身上：(物理伤害, 魔法伤害)。外圈多 e_out%，再加最大生命 e_pct% 魔法。
pub fn spin_damage(p: &Params, attack: usize, dist: f64, radius: f64, max_hp: usize) -> (usize, usize) {
    let base = p.e_dmg + attack * p.e_ratio / 100;
    if dist - radius > p.e_r0 as f64 {
        (base + base * p.e_out / 100, share(max_hp, p.e_pct))
    } else {
        (base, 0)
    }
}

/// 名字是不是本包的「不死」（别的「不死」在身上时不触发）。
pub fn ours(name: &str) -> bool {
    name == sn("rv_guard") || name == sn("rv_hold")
}

pub fn other_undying(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(name, undying)| *undying && !ours(name))
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// "l" when the nearest enemy champion stands to his left, else "r" (the revive's picture faces it).
fn facing(sim: &StableSim<'_>, me: usize) -> &'static str {
    let Some(e) = sim.get_entity(me) else { return "r" };
    let (team, at) = (e.team(), fpos(e.pos()));
    let near = (0..sim.champion_count())
        .map(|i| sim.champion_id_at(i))
        .filter_map(|id| sim.get_entity(id).filter(|c| c.team() != team && c.is_alive()).map(|c| fpos(c.pos())))
        .min_by(|a, b| dist(at, *a).total_cmp(&dist(at, *b)));
    side_of(at, near)
}

/// The side a picture of him faces: toward `near` (none: right).
pub fn side_of(at: (f64, f64), near: Option<(f64, f64)>) -> &'static str {
    match near {
        Some(p) if p.0 < at.0 => "l",
        _ => "r",
    }
}

fn is_unit(kind: Option<EntityKindV1>) -> bool {
    matches!(kind, Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Epic
                        | EntityKindV1::Summon))
}

// ===================== 被动 =====================

/// One Aureate Rush on its way: where from, where to, its start, and the tick it strikes.
#[derive(Clone, Debug)]
struct Dash {
    from: (f64, f64),
    to: (f64, f64),
    start: usize,
    target: usize,
}

#[derive(Clone, Default)]
struct Darkin {
    p: Params,
    me: usize,
    /// Determination: the stacks, the last hit on a champion, the stacks already lost since then.
    stacks: usize,
    last_hit: usize,
    lost: usize,
    /// The attack bonus last written into the buffs (so they change only when it does).
    shown: i32,
    /// His level at the last look (Determination, the revive, the glaive's heal and R's penetration go by it) and the
    /// extra armour penetration last written.
    level: usize,
    pen_shown: Option<usize>,
    /// The revive under way: the share of his maximum health it gives back (its level's).
    rise_pct: usize,
    /// The revive: ready from this tick (kept across lives), the tick the banish began (None when not rising),
    /// the next guard renewal, and whether this life has been seen above 1 health.
    revive_at: usize,
    rising: Option<usize>,
    next_guard: usize,
    alive_seen: bool,
    /// Aureate Rush: ready from this tick, the rush on its way, the tick the spin strikes.
    e_at: usize,
    dash: Option<Dash>,
    strike_at: Option<usize>,
}

impl Darkin {
    /// The Determination buffs as the stacks stand: `det` (his level's share a stack) below the top, `full` (twice
    /// that) at it; reaching the top raises `fill` for the data (the picture).
    fn show(&mut self, sim: &mut StableSim<'_>, me: usize, filled_now: bool) {
        let a = det_attack(&self.p, self.stacks, self.level);
        let full = self.stacks >= self.p.det_n;
        if a != self.shown || filled_now {
            sim.entity_remove_buff(me, &sn("det"));
            sim.entity_remove_buff(me, &sn("full"));
            if a > 0 {
                let mut b = BuffV1::named(&sn(if full { "full" } else { "det" }));
                b.duration_kind = BuffDurationV1::Permanent.code();
                b.attack_mult = a;
                sim.add_buff(me, &b);
            }
            self.shown = a;
        }
        if filled_now {
            sim.entity_remove_buff(me, &sn("fill"));
            sim.add_buff(me, &BuffV1::timed(&sn("fill"), FLAG_T));
        }
    }

    fn stack(&mut self, sim: &mut StableSim<'_>, me: usize, target: usize) {
        let was_full = self.stacks >= self.p.det_n;
        self.stacks = (self.stacks + 1).min(self.p.det_n);
        self.last_hit = sim.tick();
        self.lost = 0;
        let filled = !was_full && self.stacks >= self.p.det_n;
        self.show(sim, me, filled);
        if filled {
            if let Some(k) = counted("full") {
                wlog(format!("{} FULL #{k}: Determination {} / {} on {} at level {} (attack +{}%), revive {}",
                             head(sim, me), self.stacks, self.p.det_n, name_of(sim, target), self.level, self.shown,
                             if sim.tick() >= self.revive_at { "ready" } else { "on cooldown" }));
            }
        }
    }

    fn decay(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if self.stacks == 0 {
            return;
        }
        let n = decayed(&self.p, self.last_hit, sim.tick(), self.lost);
        if n == 0 {
            return;
        }
        self.lost += n;
        self.stacks = self.stacks.saturating_sub(n);
        self.show(sim, me, false);
    }

    fn guard(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        if now < self.next_guard {
            return;
        }
        let mut g = BuffV1::timed(&sn("rv_guard"), GUARD_T);
        g.undying = true;
        sim.entity_remove_buff(me, &sn("rv_guard"));
        sim.add_buff(me, &g);
        self.next_guard = now + GUARD_EVERY;
    }

    fn unguard(&mut self, sim: &mut StableSim<'_>, me: usize) {
        sim.entity_remove_buff(me, &sn("rv_guard"));
        self.next_guard = 0;
    }

    /// Lethal damage caught at 1 health: banished while he rises again (the data's rv_rise picture).
    fn fall(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        // a banish is refused while he is crowd-control immune (league_yuumi's lesson): R's guard goes first
        sim.entity_remove_buff(me, &sn("r_guard"));
        self.unguard(sim, me);
        self.dash = None;
        self.strike_at = None;
        // his rising faces the nearest enemy champion: an effect picture is never mirrored (one drawn each way)
        let side = facing(sim, me);
        if !sim.entity_banish(me, me, self.p.rv_rise, &sn(&format!("rv_rise_{side}")), &sn("p_full")) {
            if let Some(k) = counted("refused") {
                wlog(format!("{} REVIVE #{k} refused (banish) - he falls", head(sim, me)));
            }
            return;
        }
        // undying for the whole rise (0.1.x: the guard went before the banish, and damage still landing on him - burns,
        // hits in flight - killed 8 of 25 risings in the 10-29 games); taken off when he stands up
        let mut hold = BuffV1::timed(&sn("rv_hold"), self.p.rv_rise + 2);
        hold.undying = true;
        sim.add_buff(me, &hold);
        self.rising = Some(now);
        self.rise_pct = revive_hp(&self.p, self.level);
        self.revive_at = now + revive_cd(&self.p, self.level);
        sim.play_sfx(&sn("rv"), me, &InputTargetV1::target(me));       // League's revive and his line
        sim.play_sfx(&sn("vo_rv"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("revive") {
            wlog(format!("{} REVIVE #{k}: lethal damage caught at 1 hp at level {}, rising for {} ticks to {}% health \
                          (next at t={})", head(sim, me), self.level, self.p.rv_rise, self.rise_pct, self.revive_at));
        }
    }

    /// While banished: his health is the revive's running total, a step every RISE_STEP ticks (0.2.1, League forces it:
    /// other heals do nothing meanwhile - 11-12's log had one rise end at 83% where 60% was due); at the end
    /// Determination full again.
    fn rise(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize, t0: usize) {
        let (hp, max) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
        let due = rise_hp(&self.p, max, self.rise_pct, now - t0);
        if max > 0 && hp != due {
            sim.entity_set_hp(me, due);
        }
        if now >= t0 + self.p.rv_rise {
            sim.entity_remove_buff(me, &sn("rv_hold"));
            self.rising = None;
            self.stacks = self.p.det_n;
            self.last_hit = now;
            self.lost = 0;
            self.show(sim, me, true);
            if let Some(k) = counted("risen") {
                let (hp, max) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
                wlog(format!("{} RISEN #{k}: up again with {hp} / {max} hp, Determination full", head(sim, me)));
            }
        }
    }

    /// Aureate Rush: the nearest enemy champion within e_reach, rushed at when he can act.
    fn rush(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if now < self.e_at || !e.is_targetable() || e.cc_count() > 0 || has(sim, me, &sn("busy")) {
            return;
        }
        let (team, at) = (e.team(), fpos(e.pos()));
        let reach = self.p.e_reach as f64;
        let best = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter_map(|id| sim.get_entity(id).filter(|c| c.team() != team && c.is_alive() && c.is_targetable())
                .map(|c| (id, fpos(c.pos()))))
            .map(|(id, p)| (id, p, dist(at, p)))
            .filter(|&(_, _, d)| d <= reach)
            .min_by(|a, b| a.2.total_cmp(&b.2));
        let Some((target, tp, d)) = best else { return };
        let to = dash_to(&self.p, at, tp);
        self.e_at = now + self.p.e_cd;
        self.dash = Some(Dash { from: at, to, start: now, target });
        let t = DASH_T as u64;
        sim.entity_remove_buff(me, &sn("e_rush"));
        sim.add_buff(me, &BuffV1::timed(&sn("e_rush"), FLAG_T));   // the data plays the rush (`dash`)
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::Bind, t));
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::BlockAttack, t));
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::BlockSkill, t));
        if let Some(k) = counted("rush") {
            wlog(format!("{} RUSH #{k} at {} ({d:.0} away): to ({:.0}, {:.0})", head(sim, me), name_of(sim, target),
                         to.0, to.1));
        }
    }

    fn dashing(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let Some(d) = self.dash.clone() else { return };
        if !sim.get_entity(me).is_some_and(|e| e.is_targetable()) {
            return;   // banished: no steps (0.6.4)
        }
        let k = ((now - d.start) as f64 / DASH_T as f64).min(1.0);
        let (x, y) = (d.from.0 + (d.to.0 - d.from.0) * k, d.from.1 + (d.to.1 - d.from.1) * k);
        sim.entity_set_pos(me, x.max(0.0).round() as u64, y.max(0.0).round() as u64);
        if k >= 1.0 {
            self.dash = None;
            sim.entity_remove_buff(me, &sn("e_go"));
            sim.add_buff(me, &BuffV1::timed(&sn("e_go"), FLAG_T));
            self.strike_at = Some(now + self.p.e_hit);
            let _ = d.target;
        }
    }

    /// The spin strikes: every enemy unit within e_r, the outer ring harder and with e_pct% of its maximum health.
    fn strike(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.strike_at = None;
        let Some(e) = sim.get_entity(me) else { return };
        let (team, at, attack) = (e.team(), fpos(e.pos()), e.stat().attack);
        let mut hits = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() || !u.is_targetable() || !is_unit(u.kind()) {
                continue;
            }
            let r = match u.radius() as f64 { r if r > 0.0 => r, _ => BODY };
            let dd = dist(at, fpos(u.pos()));
            if dd - r <= self.p.e_r as f64 {
                hits.push((u.id(), dd, r, u.hp().1, u.is_champion()));
            }
        }
        let (mut n, mut outer) = (0, 0);
        for (id, dd, r, max, champ) in hits {
            let (ad, ap) = spin_damage(&self.p, attack, dd, r, max);
            sim.deal_damage_typed(me, id, ad, DamageTypeV1::Ad, AttackTypeV1::Skill);
            if ap > 0 {
                sim.deal_damage_typed(me, id, ap, DamageTypeV1::Ap, AttackTypeV1::Skill);
                outer += 1;
            }
            if champ {
                n += 1;
            }
        }
        if let Some(k) = counted("spin") {
            wlog(format!("{} SPIN #{k}: {n} champions hit, {outer} units on the outer edge", head(sim, me)));
        }
    }

    /// His level now: Determination's share follows it at once; R's extra armour penetration (`pen`, on top of the
    /// copy's r_pen_n on `own`) is rewritten when it changes or a new life lost it.
    fn levels(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let level = sim.get_entity(me).map_or(1, |e| e.level()).max(1);
        if level != self.level {
            self.level = level;
            self.show(sim, me, false);
        }
        let pen = extra_pen(&self.p, level);
        let have = has(sim, me, &sn("pen"));
        if self.pen_shown != Some(pen) || (pen > 0 && !have) {
            sim.entity_remove_buff(me, &sn("pen"));
            if pen > 0 {
                let mut b = BuffV1::named(&sn("pen"));
                b.duration_kind = BuffDurationV1::Permanent.code();
                b.defence_penetration = pen;
                sim.add_buff(me, &b);
            }
            if self.pen_shown.is_some_and(|old| old != pen) {
                if let Some(k) = counted("pen") {
                    wlog(format!("{} PEN #{k}: level {level}, Grim Deliverance's armour penetration {}% + {pen}%",
                                 head(sim, me), self.p.r_pen_n));
                }
            }
            self.pen_shown = Some(pen);
        }
    }

    /// The Darkin Glaive's heal: once a cast (the data marks the unit its first slash hits), his level's share of his
    /// maximum health on a champion, half on other units.
    fn glaive_heal(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, max) = (e.team(), e.hp().1);
        let mark = sn("q_mark");
        let mut marked = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() != team && (0..u.buff_count()).filter_map(|k| u.buff_at(k)).any(|b| b.name() == mark) {
                marked.push((u.id(), u.is_champion()));
            }
        }
        for (id, champ) in marked {
            sim.entity_remove_buff(id, &mark);
            let pct = glaive_pct(&self.p, self.level, champ);
            let h = share(max, pct);
            sim.heal(me, me, h);
            if let Some(k) = counted("glaive") {
                wlog(format!("{} GLAIVE #{k}: the glaive on {} heals {h} ({pct}% at level {})", head(sim, me),
                             name_of(sim, id), self.level));
            }
        }
    }
}

impl StablePassive for Darkin {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.stacks = 0;
        self.lost = 0;
        self.shown = 0;
        self.pen_shown = None;
        self.level = sim.get_entity(me).map_or(1, |e| e.level()).max(1);
        self.rising = None;
        self.next_guard = 0;
        self.alive_seen = false;
        self.dash = None;
        self.strike_at = None;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Zaahen (player {player}, team {team}), {:?}, revive ready at t={}",
                         head(sim, me), self.p, self.revive_at));
        }
    }

    /// Every damage instance of his on an enemy champion: one stack of Determination.
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        if *damage == 0 || self.rising.is_some() {
            return;
        }
        let team = sim.get_entity(me).map(|e| e.team());
        let champ = sim.get_entity(target).filter(|t| t.is_champion() && Some(t.team()) != team).is_some();
        if champ {
            self.stack(sim, me, target);
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        if let Some(t0) = self.rising {
            self.rise(sim, me, now, t0);
            return;
        }
        let (hp, _) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
        if hp > 1 {
            self.alive_seen = true;
        }
        self.levels(sim, me);
        self.decay(sim, me);
        self.glaive_heal(sim, me);
        self.dashing(sim, me, now);
        if self.strike_at.is_some_and(|t| now >= t) {
            self.strike(sim, me);
        }
        if self.dash.is_none() && self.strike_at.is_none() {
            self.rush(sim, me, now);
        }
        let full = self.stacks >= self.p.det_n;
        if full && now >= self.revive_at {
            self.guard(sim, me, now);
            if hp <= 1 && self.alive_seen {
                let list: Vec<(String, bool)> = sim.get_entity(me).map_or_else(Vec::new, |e| {
                    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| (b.name().to_string(), b.undying)).collect()
                });
                if !other_undying(&list) {
                    self.fall(sim, me, now);
                }
            }
        } else if self.next_guard != 0 {
            self.unguard(sim, me);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        self.stacks = 0;
        self.shown = 0;
        self.pen_shown = None;
        self.dash = None;
        self.strike_at = None;
        if self.rising.take().is_some() {
            if let Some(k) = counted("killed_rising") {
                wlog(format!("{} DEAD #{k} while rising", head(sim, self.me)));
            }
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Zaahen: Determination, the revive, Aureate Rush, the glaive's heal, R's penetration as in \
         League, by level) loaded: \
         game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:darkin"), Darkin::default());
    host.log(LogLevel::Info, "league_zaahen loaded (Determination, the revive, Aureate Rush, the glaive's heal).");
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
    fn params_from_the_kit() {
        let kit = concat!(r#"{"atk_range":25000,"det_hi":295,"det_lo":150,"det_lv":18,"det_n":12,"det_t":300,"e_cd":540,"#,
                          r#""e_dash":22000,"e_dmg":88,"e_hit":14,"e_out":50,"e_pct":5,"e_r":25000,"e_r0":13000,"#,
                          r#""e_ratio":88,"e_reach":48000,"q_hp":5,"q_hp_step":1,"r_pen_n":10,"r_pen_step":10,"#,
                          r#""rv_cd":18000,"rv_cd_step":3600,"rv_hp":30,"rv_hp_step":15,"rv_lv":5,"rv_rise":240}"#);
        assert_eq!(parse_params(kit), Params::default());
        assert_eq!(parse_params(r#"{"det_n":8}"#).det_n, 8);
    }

    #[test]
    fn determination_goes_by_level_and_doubles_at_the_top() {
        let p = Params::default();
        // League: 1.5% a stack at level 1, 2.95% at 18; full (12) doubled: 36% - 70.87%
        assert_eq!((det_per_stack(&p, 1), det_per_stack(&p, 18), det_per_stack(&p, 30)), (150, 295, 295));
        assert_eq!(det_attack(&p, 0, 1), 0);
        assert_eq!(det_attack(&p, 11, 1), 17);      // 16.5
        assert_eq!(det_attack(&p, 12, 1), 36);
        assert_eq!(det_attack(&p, 12, 18), 71);     // 70.8
        assert_eq!(det_attack(&p, 30, 18), 71);
        assert!(det_attack(&p, 12, 9) > det_attack(&p, 12, 8));
    }

    #[test]
    fn determination_waits_then_falls_faster_and_faster() {
        let p = Params::default();
        assert_eq!(decayed(&p, 100, 399, 0), 0);
        // 0.0 s and 0.5 s after the 5 s: 1 each; 1.0 s and 1.5 s: 2 each; 2.0 s and 2.5 s: 3 each - all 12 gone
        assert_eq!(decayed(&p, 100, 400, 0), 1);
        assert_eq!(decayed(&p, 100, 429, 1), 0);
        assert_eq!(decayed(&p, 100, 430, 1), 1);
        assert_eq!(decayed(&p, 100, 460, 2), 2);
        assert_eq!(decayed(&p, 100, 490, 4), 2);
        assert_eq!(decayed(&p, 100, 550, 6), 6);
        // past 4 s: 5 a step
        assert_eq!(decayed(&p, 100, 640, 0) - decayed(&p, 100, 610, 0), 5);
    }

    #[test]
    fn the_revive_goes_by_level() {
        let p = Params::default();
        // League: 30 / 45 / 60 / 75% of his health and 300 / 240 / 180 / 120 s at levels 1 / 6 / 11 / 16
        for (level, hp, cd) in [(1, 30, 18000), (5, 30, 18000), (6, 45, 14400), (11, 60, 10800), (16, 75, 7200),
                                (18, 75, 7200)] {
            assert_eq!((revive_hp(&p, level), revive_cd(&p, level)), (hp, cd), "level {level}");
        }
        let steps = p.rv_rise / RISE_STEP;
        assert_eq!(rise_step(&p, 3000, 50) * steps, 1500);
        assert_eq!(rise_step(&p, 3000, revive_hp(&p, 1)) * steps, 900);
    }

    #[test]
    fn the_rise_forces_its_running_total() {
        let p = Params::default();
        // 60% of 3000 over 240 ticks: 60 a step of 8 ticks, from the 1 health he was caught at - whatever else heals him
        assert_eq!(rise_hp(&p, 3000, 60, 0), 1);
        assert_eq!(rise_hp(&p, 3000, 60, 7), 1);
        assert_eq!(rise_hp(&p, 3000, 60, 8), 61);
        assert_eq!(rise_hp(&p, 3000, 60, 120), 901);
        assert_eq!(rise_hp(&p, 3000, 60, 240), 1801);
        assert_eq!(rise_hp(&p, 3000, 60, 400), 1801, "no more after the rise");
        assert_eq!(rise_hp(&p, 0, 60, 240), 1, "no maximum read: he keeps 1");
    }

    #[test]
    fn the_glaive_heals_once_by_its_rank() {
        let p = Params::default();
        // League's Q ranked first: 1 / 4 / 5 / 7 / 9 -> 5 / 6 / 7 / 8 / 9% on a champion, half on other units
        let got: Vec<usize> = [1, 3, 4, 5, 7, 9, 12].iter().map(|&l| glaive_pct(&p, l, true)).collect();
        assert_eq!(got, vec![5, 5, 6, 7, 8, 9, 9]);
        assert_eq!((glaive_pct(&p, 1, false), glaive_pct(&p, 9, false)), (2, 4));
    }

    #[test]
    fn grim_deliverance_pierces_more_by_rank() {
        let p = Params::default();
        // League 10 / 20 / 30%: the copy's own flag gives 10, the add-on the rest (ranks at 11 / 16 here)
        assert_eq!((extra_pen(&p, 5), extra_pen(&p, 10), extra_pen(&p, 11), extra_pen(&p, 16)), (0, 0, 10, 20));
    }

    #[test]
    fn the_rush_stops_with_the_target_on_the_outer_edge() {
        let p = Params::default();
        let ring = (p.e_r0 + p.e_r) as f64 / 2.0;
        let to = dash_to(&p, (0.0, 0.0), (30000.0, 0.0));
        assert!((to.0 - (30000.0 - ring)).abs() < 1.0);
        let far = dash_to(&p, (0.0, 0.0), (100000.0, 0.0));
        assert!((far.0 - p.e_dash as f64).abs() < 1.0);
        let near = dash_to(&p, (0.0, 0.0), (2000.0, 0.0));
        assert!(near.0 < 0.0 && near.0 >= -(p.e_dash as f64) / 2.0);
    }

    #[test]
    fn the_outer_edge_hits_harder() {
        let p = Params::default();
        assert_eq!(spin_damage(&p, 100, 5000.0, 6000.0, 2000), (176, 0));
        assert_eq!(spin_damage(&p, 100, 20000.0, 6000.0, 2000), (264, 100));
    }

    #[test]
    fn the_revive_faces_the_nearest_enemy() {
        assert_eq!(side_of((100.0, 0.0), Some((50.0, 9.0))), "l");
        assert_eq!(side_of((100.0, 0.0), Some((150.0, 9.0))), "r");
        assert_eq!(side_of((100.0, 0.0), None), "r");
    }

    #[test]
    fn only_someone_elses_undying_holds_the_revive_back() {
        assert!(!other_undying(&[("league_zaahen_rv_guard".to_string(), true)]));
        assert!(!other_undying(&[("league_zaahen_rv_hold".to_string(), true)]));
        assert!(other_undying(&[("league_zilean_r_rune".to_string(), true)]));
    }

    #[test]
    fn the_kit_names_what_this_add_on_reads_and_writes() {
        let kit = include_str!("../../../tools/kit/build_zaahen.py");
        for flag in ["\"e_go\"", "\"e_rush\"", "\"fill\"", "\"q_mark\"", "\"busy\"", "\"r_guard\"", "\"full\"",
                     "rv_rise_{side}", "\"own\"", "r_pen_n"] {
            assert!(kit.contains(flag), "build_zaahen.py no longer names {flag}");
        }
    }
}
