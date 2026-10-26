//! 诺拉附加包：数据做不到、和英雄联盟手游不一样的地方，这里照手游做（用户：「不一致的地方就做附加包」）。规则按手游
//! 现在的诺拉（Wild Rift wiki 和 7.3 的改动记录，2026-10-26 查）。
//!
//! `mod.override_info` 把金铲铲包（tft）的诺拉换成 `override/` 里的副本（tools/kit/build_norra.py --native，
//! `make_override.py` 写），`passive` 换成本包的 `tft_norra:trinkets`，副本在下面这些地方调用本包的效果：
//!
//! - **寄情琐物一个一个撒、一个一个踩**（`tft_norra:drop`：琐物冷却好了的 Q / E 落地）：主包在落点放一片琐物（每个
//!   敌方英雄走进去被打一次）。手游按等级撒 2/3/4 个，这里 3 个：落点一个茶杯、左右 `TRINKET_DX` 各一个水晶（主包那张
//!   图切成三块，各在各的位置播），`p_life` 拍内哪个敌方英雄先走到哪个的 `p_tr` 以内，那个琐物就飞到他身上炸开：
//!   `p_dmg` + 法强 `p_ratio`% 魔法伤害和线缕，那个琐物没了，别的还在。每个琐物是一个每拍重排一次的效果
//!   （`tft_norra:trinket`），位置、到期的拍、哪一块、撒下的拍、引爆了没有都记在它的输入里。
//! - **技能命中英雄缩短琐物冷却**：手游里技能（Q、W、E）命中敌方英雄，琐物冷却减少总冷却的 20%：诺拉身上
//!   `tft_norra_p_cd` 剩下的拍数减去 `p_cd` 的 `REFUND`%（E 的命中调用 `tft_norra:refund`，Q 的 `tft_norra:surge`
//!   和本包的奇异旅程自己减）。主包没有这一条。
//! - **回忆涌现对线缕目标多打最大生命、引爆琐物**（`tft_norra:surge`：Q 的命中）：手游里 Q 对挂着线缕的敌人多打最大
//!   生命的 1%–2.5%，蓄满的 Q 打中敌方英雄会把地上所有琐物变成「附近有人就炸」。打中的是英雄：身上已经有线缕（这一发
//!   之前挂上的）就再打他最大生命的 `q_bonus`‰ 魔法伤害，然后挂上线缕，给诺拉挂 `PRIME_T` 拍 `tft_norra_q_prime`；她地上
//!   的琐物（这一发 Q 撒的除外）看到它就引爆待发：从此敌方英雄走到 `q_prime_r` 以内它就飞过去。主包是 Q 落地时在落点
//!   周围打一圈琐物的伤害。
//! - **奇异旅程随时保命**（被动每拍）：主包只在她普攻、身边有敌方英雄时开门。副本的普攻不开门；本包每拍看：诺拉活着、
//!   能被选中、不在控制里、没有 `tft_norra_w_cd`、`w_r` 以内有敌方英雄，就在离她最近的那个脚下开门：`w_dmg` + 法强
//!   `w_ratio`% 魔法伤害，放逐 `w_t` 拍（放逐期间原地转的门 `w_lock`，结束吐回来 `w_out`），回来以后减速 `w_slow`%
//!   `w_slow_t` 拍（手游 7.2：放逐 1.5 秒、之后减速 80% 0.75 秒），冷却 `w_cd` 拍。
//! - **传送门欢腾！的毛线球走直线**（`tft_norra:rift`：裂隙落地）：主包每波打裂隙里所有敌方英雄。本包每 `r_gap` 拍放一波
//!   （`tft_norra:volley`）：一条横穿裂隙、穿过裂隙里一个敌方英雄的线（每波轮到下一个），两个毛线球从裂隙两头沿线对飞，
//!   穿过路上所有敌人（`tft_norra:yarn_l` / `_r`，第四波 `tft_norra:yarn4_l` / `_r`）：每个敌人每波挨一次 `r_dmg` + 法强
//!   `r_ratio`%（两个球都碰到也只算一次），第四波多 `r_last`%；每个球碰到的第一个英雄减速 `r_slow`% `r_slow_t` 拍（手游：
//!   玩家每次划一条路，两头各出一个球，各自碰到的第一个英雄减速）。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），按诺拉的单位编号记一份给效果用（服务端
//! 预模拟和你看的那场是同一份数字）；琐物、毛线球这些会变的东西都在模拟里（排着的效果、身上的状态），不用全局变量。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_norra.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_norra";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// The data's flags (tools/kit/build_norra.py --native) and the Threads (the data's buffs: their pictures are the copy's
/// view_buffs).
const P_CD: &str = "tft_norra_p_cd";
const W_CD: &str = "tft_norra_w_cd";
const T_MARK: &str = "tft_norra_t_mark";
const T_SLOW: &str = "tft_norra_t_slow";
const R_SLOW: &str = "tft_norra_r_slow";
/// The add-on's own: on her for PRIME_T ticks after a Memory Surge hit a champion; on him after Journey to Nowhere;
/// on her while each ball of a volley (left, right) has not met a champion yet; on a unit a ball of this volley hit.
const Q_PRIME: &str = "tft_norra_q_prime";
const W_SLOW: &str = "tft_norra_w_slow";
const R_FIRST: [&str; 2] = ["tft_norra_r_first_l", "tft_norra_r_first_r"];
const R_TOOK: &str = "tft_norra_r_took";
/// The pictures (the copy's view_effects; the trinkets' three pieces left, middle, right) and the sounds (the tft pack's).
const PIECES: [&str; 3] = ["tft_norra_p_trinket_l", "tft_norra_p_trinket_c", "tft_norra_p_trinket_r"];
const P_BURST: &str = "tft_norra_p_burst";
const W_IN: &str = "tft_norra_w_in";
const W_LOCK: &str = "tft_norra_w_lock";
const W_OUT: &str = "tft_norra_w_out";
const R_HIT: &str = "tft_norra_r_hit";
const SFX_DROP: &str = "tft_norra_p_drop";
const SFX_BURST: &str = "tft_norra_p_burst";
const SFX_W: &str = "tft_norra_w";
const SFX_BALL: &str = "tft_norra_r_ball";
const SFX_HIT: &str = "tft_norra_r_hit";
/// The yarn ball: a projectile, its picture the copy's view_projectiles entry.
const R_BALL: &str = "tft_norra_r_ball";
/// The effects this add-on queues for itself; a yarn ball's hit by [fourth][ball: from the left end, from the right].
const TRINKET_FX: &str = "tft_norra:trinket";
const VOLLEY_FX: &str = "tft_norra:volley";
const YARN_FX: [[&str; 2]; 2] = [["tft_norra:yarn_l", "tft_norra:yarn_r"], ["tft_norra:yarn4_l", "tft_norra:yarn4_r"]];
/// The trinkets: the teacup on the landing point, a crystal TRINKET_DX to each side (scattered: a champion on one is
/// not on the next).
const TRINKET_DX: i64 = 40_000;
/// Q_PRIME lasts PRIME_T ticks from Memory Surge's hit (the tick after it lands); a trinket PRIME_AGE ticks old was
/// dropped before that Q landed.
const PRIME_T: usize = 3;
const PRIME_AGE: usize = 4;
/// Wild Rift: an ability hitting an enemy champion takes 20% of the whole off the trinkets' cooldown.
const REFUND: usize = 20;
/// A yarn ball's flight across the rift (ticks) and its body.
const BALL_TICKS: u64 = 16;
const BALL_RADIUS: u64 = 9_000;
/// What keeps her from opening a portal (a cast): everything but a root, a disarm and a dash lock.
const NO_CAST: [CcKindV1; 8] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::BlockSkill,
    CcKindV1::ForceMove,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::Animation,
];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_NORRA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_norra.log");
        }
    }
    PathBuf::from("tft_norra.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub fn wlog(msg: impl AsRef<str>) {
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
const LOG_EVERY: usize = 100;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// The first LOG_FIRST of a kind, then every LOG_EVERY-th: its number.
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

/// 主包参数表 P 里本包用到的数字（`passive.params`，build_norra.NATIVE_KEYS）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 寄情琐物：冷却（拍）、多近算踩到、在地上多久、伤害和法强比例、它的图多久播一遍。
    pub p_cd: usize,
    pub p_tr: u64,
    pub p_life: usize,
    pub p_dmg: usize,
    pub p_ratio: usize,
    pub p_show: usize,
    /// 奇异旅程：冷却、多近开门、伤害和法强比例、放逐多久、回来后减速多少和多久。
    pub w_cd: usize,
    pub w_r: u64,
    pub w_dmg: usize,
    pub w_ratio: usize,
    pub w_t: usize,
    pub w_slow: usize,
    pub w_slow_t: usize,
    /// 回忆涌现：引爆待发的琐物多远飞过去；对线缕目标多打最大生命的千分比。
    pub q_prime_r: u64,
    pub q_bonus: usize,
    /// 线缕：多久、变大的百分比、受到伤害加深、减速和减速多久。
    pub t_t: usize,
    pub t_size: usize,
    pub t_amp: usize,
    pub t_slow: usize,
    pub t_slow_t: usize,
    /// 传送门欢腾！：裂隙半径、两波之间、每个球的伤害和法强比例、第四波多打的百分比、减速和多久。
    pub r_r: u64,
    pub r_gap: usize,
    pub r_dmg: usize,
    pub r_ratio: usize,
    pub r_last: usize,
    pub r_slow: usize,
    pub r_slow_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_cd: 600,
            p_tr: 26_000,
            p_life: 240,
            p_dmg: 30,
            p_ratio: 20,
            p_show: 60,
            w_cd: 1500,
            w_r: 18_000,
            w_dmg: 40,
            w_ratio: 30,
            w_t: 90,
            w_slow: 80,
            w_slow_t: 45,
            q_prime_r: 45_000,
            q_bonus: 20,
            t_t: 240,
            t_size: 15,
            t_amp: 0,
            t_slow: 20,
            t_slow_t: 120,
            r_r: 35_000,
            r_gap: 30,
            r_dmg: 30,
            r_ratio: 15,
            r_last: 40,
            r_slow: 80,
            r_slow_t: 30,
        }
    }
}

/// `{"p_cd":600,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        let u = v as usize;
        match k {
            "p_cd" => p.p_cd = u,
            "p_tr" => p.p_tr = v,
            "p_life" => p.p_life = u,
            "p_dmg" => p.p_dmg = u,
            "p_ratio" => p.p_ratio = u,
            "p_show" => p.p_show = u.max(1),
            "w_cd" => p.w_cd = u,
            "w_r" => p.w_r = v,
            "w_dmg" => p.w_dmg = u,
            "w_ratio" => p.w_ratio = u,
            "w_t" => p.w_t = u,
            "w_slow" => p.w_slow = u,
            "w_slow_t" => p.w_slow_t = u,
            "q_prime_r" => p.q_prime_r = v,
            "q_bonus" => p.q_bonus = u,
            "t_t" => p.t_t = u,
            "t_size" => p.t_size = u,
            "t_amp" => p.t_amp = u,
            "t_slow" => p.t_slow = u,
            "t_slow_t" => p.t_slow_t = u,
            "r_r" => p.r_r = v,
            "r_gap" => p.r_gap = u.max(1),
            "r_dmg" => p.r_dmg = u,
            "r_ratio" => p.r_ratio = u,
            "r_last" => p.r_last = u,
            "r_slow" => p.r_slow = u,
            "r_slow_t" => p.r_slow_t = u,
            _ => {}
        }
    }
    p
}

/// Each Norra's numbers by her entity id, for the effects (they have no passive of their own); the server's
/// pre-simulation and the match on screen use the same numbers.
static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).cloned().unwrap_or_default()
}

// ===================== 计算 =====================

/// base + ratio% of the ability power.
pub fn magic(base: usize, ratio: usize, ap: usize) -> usize {
    base + ap * ratio / 100
}

/// A yarn ball's damage: the fourth volley's hits r_last% more.
pub fn yarn_damage(p: &Params, ap: usize, fourth: bool) -> usize {
    let d = magic(p.r_dmg, p.r_ratio, ap);
    if fourth {
        d * (100 + p.r_last) / 100
    } else {
        d
    }
}

/// What an ability hitting a champion takes off the trinkets' remaining cooldown (REFUND% of the whole).
pub fn refund(p: &Params) -> usize {
    p.p_cd * REFUND / 100
}

/// Memory Surge's bonus on a champion already in the Threads: q_bonus per mille of his maximum health.
pub fn surge_bonus(p: &Params, max_hp: usize) -> usize {
    max_hp * p.q_bonus / 1000
}

/// The trinkets round a landing point: (piece, where) - left, the landing point, right.
pub fn trinket_spots(at: (u64, u64)) -> [(i64, (u64, u64)); 3] {
    let side = |s: i64| (s, ((at.0 as i64 + s * TRINKET_DX).max(0) as u64, at.1));
    [side(-1), side(0), side(1)]
}

/// A volley's line: across the rift (centre `c`, radius `r`) at the height of `through` (kept within two thirds of the
/// radius of the centre, so the line is never a sliver), from its left end to its right end.
pub fn yarn_line(c: (u64, u64), r: u64, through: Option<(u64, u64)>) -> ((u64, u64), (u64, u64)) {
    let y = match through {
        Some(t) => t.1.clamp(c.1.saturating_sub(r * 2 / 3), c.1 + r * 2 / 3),
        None => c.1,
    };
    let dy = y.abs_diff(c.1) as f64;
    let half = ((r as f64).powi(2) - dy * dy).max(0.0).sqrt() as u64;
    ((c.0.saturating_sub(half), y), (c.0 + half, y))
}

/// A trinket on the ground: the queued effect's input carries it (a position; the tick it goes in `target_id`; its
/// piece and whether a Memory Surge primed it in `dir_x`: side + 1, +4 when primed; the tick it was dropped in `dir_y`).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Trinket {
    pub at: (u64, u64),
    pub until: usize,
    pub side: i64,
    pub born: usize,
    pub primed: bool,
}

impl Trinket {
    pub fn input(&self) -> InputTargetV1 {
        InputTargetV1 {
            kind: InputTargetKindV1::Pos.code(),
            target_id: self.until,
            dir_x: self.side + 1 + if self.primed { 4 } else { 0 },
            dir_y: self.born as i64,
            x: self.at.0,
            y: self.at.1,
        }
    }

    pub fn from_input(i: &InputTargetV1) -> Option<Self> {
        let ok = i.kind == InputTargetKindV1::Pos.code() && (0..8).contains(&i.dir_x) && i.dir_x & 3 != 3 && i.dir_y >= 0;
        ok.then(|| Self {
            at: (i.x, i.y),
            until: i.target_id,
            side: (i.dir_x & 3) - 1,
            born: i.dir_y as usize,
            primed: i.dir_x & 4 != 0,
        })
    }

    pub fn piece(&self) -> &'static str {
        PIECES[(self.side + 1) as usize]
    }
}

fn dist2(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0.abs_diff(b.0);
    let dy = a.1.abs_diff(b.1);
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

/// The nearest of `foes` within `r` of `at` (ties to the lower id).
pub fn nearest(foes: &[(usize, (u64, u64))], at: (u64, u64), r: u64) -> Option<usize> {
    let r2 = r.saturating_mul(r);
    foes.iter().filter(|&&(_, p)| dist2(p, at) <= r2).min_by_key(|&&(id, p)| (dist2(p, at), id)).map(|&(id, _)| id)
}

// ===================== 模拟里的小工具 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn remaining(sim: &StableSim<'_>, id: usize, name: &str) -> Option<usize> {
    let e = sim.get_entity(id)?;
    let left = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == name).map(|b| b.duration_tick);
    left
}

fn ap_of(sim: &StableSim<'_>, me: usize) -> usize {
    sim.get_entity(me).map_or(0, |e| e.stat().magic_power)
}

/// The point an effect runs on: a position, or where its unit stands.
fn point(sim: &StableSim<'_>, input: &InputTargetV1) -> Option<(u64, u64)> {
    match InputTargetKindV1::from_code(input.kind) {
        Some(InputTargetKindV1::Pos) => Some((input.x, input.y)),
        Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|e| e.pos()),
        _ => None,
    }
}

fn unit(input: &InputTargetV1) -> Option<usize> {
    (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
}

/// Her enemy champions alive and targetable: (id, where), by id.
fn foes(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64))> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    let mut out = Vec::new();
    for i in 0..sim.champion_count() {
        let id = sim.champion_id_at(i);
        let Some(c) = sim.get_entity(id) else { continue };
        if c.team() != team && c.is_alive() && c.is_targetable() {
            out.push((id, c.pos()));
        }
    }
    out.sort_by_key(|&(id, _)| id);
    out
}

/// A named timed buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

fn slow(name: &str, pct: usize, ticks: usize) -> BuffV1 {
    let mut b = BuffV1::timed(name, ticks);
    b.move_speed_mult = -(pct as i32);
    b
}

/// The Threads on a unit.
fn threads(sim: &mut StableSim<'_>, p: &Params, id: usize) {
    let mut mark = BuffV1::timed(T_MARK, p.t_t);
    mark.radius_mult = p.t_size as i32;
    mark.damaged_amplify = p.t_amp;
    put(sim, id, &mark);
    put(sim, id, &slow(T_SLOW, p.t_slow, p.t_slow_t));
}

/// One of her abilities hit enemy champion `id`: REFUND% of the whole off the trinkets' remaining cooldown.
fn cut_cooldown(sim: &mut StableSim<'_>, me: usize, id: usize, by: &str) {
    let Some(left) = remaining(sim, me, P_CD) else { return };
    let cut = refund(&params_of(me));
    sim.entity_remove_buff(me, P_CD);
    if left > cut {
        sim.add_buff(me, &BuffV1::timed(P_CD, left - cut));
    }
    if let Some(k) = counted("refund") {
        wlog(format!("{} REFUND #{k}: {by} on {}, the trinkets' cooldown {left} -> {}", head(sim, me), name_of(sim, id),
                     left.saturating_sub(cut)));
    }
}

// ===================== 寄情琐物 =====================

/// A Q or E with the trinkets ready landed (the copy's `when p_cd` has put the cooldown on): three trinkets.
struct Drop;
impl StableEffectType for Drop {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(at) = point(sim, &input) else { return };
        let p = params_of(me);
        let tick = sim.tick();
        let mut queued = 0;
        for (side, spot) in trinket_spots(at) {
            let t = Trinket { at: spot, until: tick + p.p_life, side, born: tick, primed: false };
            sim.play_view_effect(t.piece(), me, &InputTargetV1::pos(spot.0, spot.1), 0, 0, 0);
            if sim.queue_effect(TRINKET_FX, AttackTypeV1::Skill, me, &t.input(), 1) {
                queued += 1;
            }
        }
        sim.play_sfx(SFX_DROP, me, &InputTargetV1::pos(at.0, at.1));
        if let Some(k) = counted("drop") {
            wlog(format!("{} DROP #{k}: {queued} trinkets at ({}, {}) for {} ticks{}", head(sim, me), at.0, at.1,
                         p.p_life, if queued == 3 { "" } else { " - queue_effect refused" }));
        }
    }
}

/// A trinket, every tick while it lies there: the first enemy champion on it (within p_tr; q_prime_r once a Memory
/// Surge primed it) takes it.
struct Trinkets;
impl StableEffectType for Trinkets {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(t) = Trinket::from_input(&input) else { return };
        let tick = sim.tick();
        if tick >= t.until || sim.get_entity(me).is_none() {
            return;
        }
        let p = params_of(me);
        let primed = t.primed || (tick >= t.born + PRIME_AGE && has(sim, me, Q_PRIME));
        let reach = if primed { p.q_prime_r.max(p.p_tr) } else { p.p_tr };
        if let Some(id) = nearest(&foes(sim, me), t.at, reach) {
            let dmg = magic(p.p_dmg, p.p_ratio, ap_of(sim, me));
            sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            threads(sim, &p, id);
            let on = InputTargetV1::target(id);
            sim.play_view_effect(P_BURST, me, &on, 0, 0, 0);
            sim.play_sfx(SFX_BURST, me, &on);
            if let Some(k) = counted("burst") {
                wlog(format!("{} TRINKET #{k} ({}{}) flies to {}: {dmg} magic + the Threads", head(sim, me), t.piece(),
                             if primed { ", primed" } else { "" }, name_of(sim, id)));
            }
            return;
        }
        if primed && !t.primed {
            if let Some(k) = counted("primed") {
                wlog(format!("{} PRIMED #{k}: {} at ({}, {}) now flies to anyone within {}", head(sim, me), t.piece(),
                             t.at.0, t.at.1, reach));
            }
        }
        if (tick - t.born) % p.p_show == 0 {
            sim.play_view_effect(t.piece(), me, &InputTargetV1::pos(t.at.0, t.at.1), 0, 0, 0);
        }
        sim.queue_effect(TRINKET_FX, AttackTypeV1::Skill, me, &Trinket { primed, ..t }.input(), 1);
    }
}

/// Threads of Homecoming hit something: a champion cuts the trinkets' cooldown.
struct Refund;
impl StableEffectType for Refund {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input) else { return };
        if sim.get_entity(id).is_some_and(|e| e.is_champion()) {
            cut_cooldown(sim, me, id, "Threads of Homecoming");
        }
    }
}

// ===================== 回忆涌现 =====================

/// Memory Surge hit something. A champion: q_bonus per mille of his maximum health more when he is already in the
/// Threads; then the Threads on him, her trinkets primed and their cooldown cut.
struct Surge;
impl StableEffectType for Surge {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input) else { return };
        let Some((champion, alive, max)) = sim.get_entity(id).map(|e| (e.is_champion(), e.is_alive(), e.hp().1)) else {
            return;
        };
        if !champion {
            return;
        }
        let p = params_of(me);
        if alive && has(sim, id, T_MARK) {
            let d = surge_bonus(&p, max);
            if d > 0 {
                sim.deal_damage_typed(me, id, d, DamageTypeV1::Ap, AttackTypeV1::Skill);
            }
            if let Some(k) = counted("surge") {
                wlog(format!("{} SURGE #{k} on {} in the Threads: +{d} magic ({max} max hp)", head(sim, me),
                             name_of(sim, id)));
            }
        }
        if alive {
            threads(sim, &p, id);
        }
        put(sim, me, &BuffV1::timed(Q_PRIME, PRIME_T));
        cut_cooldown(sim, me, id, "Memory Surge");
    }
}

// ===================== 传送门欢腾！ =====================

/// The rift landed: four volleys, r_gap ticks apart, the first r_gap after it opens (the main pack's timing).
struct Rift;
impl StableEffectType for Rift {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(c) = point(sim, &input) else { return };
        let p = params_of(me);
        let mut queued = 0;
        for k in 1..=4 {
            let v = InputTargetV1 { target_id: k, ..InputTargetV1::pos(c.0, c.1) };
            if sim.queue_effect(VOLLEY_FX, AttackTypeV1::Skill, me, &v, p.r_gap * k) {
                queued += 1;
            }
        }
        if let Some(k) = counted("rift") {
            wlog(format!("{} RIFT #{k} at ({}, {}): {queued} volleys queued, {} ticks apart", head(sim, me), c.0, c.1,
                         p.r_gap));
        }
    }
}

/// Volley `target_id` (1-4): a yarn ball from each end of the rift along a line through a champion inside.
struct Volley;
impl StableEffectType for Volley {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Pos.code() || !(1..=4).contains(&input.target_id) {
            return;
        }
        let (c, k) = ((input.x, input.y), input.target_id);
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let p = params_of(me);
        let r2 = p.r_r.saturating_mul(p.r_r);
        let inside: Vec<(usize, (u64, u64))> = foes(sim, me).into_iter().filter(|&(_, at)| dist2(at, c) <= r2).collect();
        // each volley through the next champion in turn (Wild Rift: the player swipes a new path every recast)
        let through = (!inside.is_empty()).then(|| inside[(k - 1) % inside.len()].1);
        let (a, b) = yarn_line(c, p.r_r, through);
        let speed = (a.0.abs_diff(b.0) / BALL_TICKS).max(1_000);
        let mut flying = 0;
        for (ball, (from, to)) in [(a, b), (b, a)].into_iter().enumerate() {
            put(sim, me, &BuffV1::timed(R_FIRST[ball], BALL_TICKS as usize + 4));
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team,
                x: from.0,
                y: from.1,
                radius: BALL_RADIUS,
                speed,
                move_kind: ProjectileMoveKindV1::Linear.code(),
                target_id: 0,
                target_x: to.0,
                target_y: to.1,
                penetrate: true,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::EnemyWithoutTower.code(),
            };
            if sim.spawn_projectile(R_BALL, YARN_FX[(k == 4) as usize][ball], &spec) {
                flying += 1;
            }
        }
        sim.play_sfx(SFX_BALL, me, &InputTargetV1::pos(c.0, c.1));
        if let Some(n) = counted("volley") {
            let how = match through {
                Some(_) => format!(" through a champion ({} inside)", inside.len()),
                None => " through the middle (nobody inside)".to_string(),
            };
            wlog(format!("{} VOLLEY #{n} ({k} of 4): {flying} balls across ({}, {}) - ({}, {}){how}", head(sim, me),
                         a.0, a.1, b.0, b.1));
        }
    }
}

/// A yarn ball passed a unit: its damage once a volley (the fourth's r_last% more); the ball's first champion slowed.
struct Yarn {
    fourth: bool,
    /// 0: the ball from the rift's left end, 1: from its right end.
    ball: usize,
}
impl StableEffectType for Yarn {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(id) = unit(&input) else { return };
        let Some(champion) = sim.get_entity(id).map(|e| e.is_champion()) else { return };
        let p = params_of(me);
        let again = has(sim, id, R_TOOK);
        let d = yarn_damage(&p, ap_of(sim, me), self.fourth);
        if !again {
            sim.deal_damage_typed(me, id, d, DamageTypeV1::Ap, AttackTypeV1::Skill);
            put(sim, id, &BuffV1::timed(R_TOOK, BALL_TICKS as usize + 4));
            let on = InputTargetV1::target(id);
            sim.play_view_effect(R_HIT, me, &on, 0, 0, 0);
            sim.play_sfx(SFX_HIT, me, &on);
        }
        let first = champion && has(sim, me, R_FIRST[self.ball]);
        if first {
            sim.entity_remove_buff(me, R_FIRST[self.ball]);
            put(sim, id, &slow(R_SLOW, p.r_slow, p.r_slow_t));
        }
        if champion {
            if let Some(k) = counted("yarn") {
                wlog(format!("{} YARN #{k} ({} ball) on {}: {}{}{}", head(sim, me), ["left", "right"][self.ball],
                             name_of(sim, id), if again { "hit by the other ball already".to_string() } else {
                                 format!("{d} magic") },
                             if self.fourth { " (the fourth volley)" } else { "" },
                             if first { ", the ball's first champion: slowed" } else { "" }));
            }
        }
    }
}

// ===================== 被动：奇异旅程 =====================

#[derive(Clone, Default)]
struct Journey {
    p: Params,
}

impl Journey {
    /// The nearest enemy champion within w_r banished (then slowed), w_cd ticks to the next.
    fn open(&self, sim: &mut StableSim<'_>, me: usize) {
        let Some((alive, free, mine)) = sim.get_entity(me).map(|e| {
            let held = (0..e.cc_count()).filter_map(|i| e.cc_at(i)).any(|c| NO_CAST.iter().any(|k| k.code() == c.kind));
            (e.is_alive(), e.is_targetable() && !held, e.pos())
        }) else {
            return;
        };
        if !alive || !free || has(sim, me, W_CD) {
            return;
        }
        let Some(id) = nearest(&foes(sim, me), mine, self.p.w_r) else { return };
        let at = sim.get_entity(id).map_or(mine, |e| e.pos());
        let dmg = magic(self.p.w_dmg, self.p.w_ratio, ap_of(sim, me));
        sim.add_buff(me, &BuffV1::timed(W_CD, self.p.w_cd));
        sim.play_view_effect(W_IN, me, &InputTargetV1::pos(at.0, at.1), 0, 0, 0);
        sim.play_sfx(SFX_W, me, &InputTargetV1::target(id));
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        // slowed from the start: out of play while banished, so the slow is felt the w_slow_t ticks after it
        put(sim, id, &slow(W_SLOW, self.p.w_slow, self.p.w_t + self.p.w_slow_t));
        let banished = sim.entity_banish(me, id, self.p.w_t, W_LOCK, W_OUT);
        cut_cooldown(sim, me, id, "Journey to Nowhere");
        if let Some(k) = counted("journey") {
            wlog(format!("{} JOURNEY #{k}: {} {} away, {dmg} magic, {}", head(sim, me), name_of(sim, id),
                         (dist2(at, mine) as f64).sqrt() as u64,
                         if banished { format!("banished {} ticks", self.p.w_t) } else { "the banish refused".into() }));
        }
    }
}

impl StablePassive for Journey {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p.clone());
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: the add-on's Norra (player {player}, team {team}), {:?}", head(sim, me),
                         self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.open(sim, me);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Wild Rift's Norra: trinkets one by one, ability hits cut their cooldown, Memory Surge on the Threads and priming, Journey to Nowhere any time, Portalpalooza!'s yarn balls) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:trinkets"), Journey::default());
    module.add_native_effect(format!("{ID}:drop"), Drop);
    module.add_native_effect(TRINKET_FX.to_string(), Trinkets);
    module.add_native_effect(format!("{ID}:refund"), Refund);
    module.add_native_effect(format!("{ID}:surge"), Surge);
    module.add_native_effect(format!("{ID}:rift"), Rift);
    module.add_native_effect(VOLLEY_FX.to_string(), Volley);
    for (fourth, names) in YARN_FX.iter().enumerate() {
        for (ball, name) in names.iter().enumerate() {
            module.add_native_effect(name.to_string(), Yarn { fourth: fourth == 1, ball });
        }
    }
    host.log(LogLevel::Info, "tft_norra loaded (Wild Rift's Norra: trinkets, Journey to Nowhere, yarn balls).");
}

fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"p_cd":480,"w_r":20000,"r_last":50,"w_slow_t":30,"x":1}"#);
        assert_eq!((p.p_cd, p.w_r, p.r_last, p.w_slow_t), (480, 20000, 50, 30));
        assert_eq!(p.r_gap, Params::default().r_gap);
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"p_show":0,"r_gap":0}"#).p_show, 1);
    }

    #[test]
    fn the_fourth_volley_hits_harder() {
        let p = Params::default();
        assert_eq!(yarn_damage(&p, 100, false), 45); // 30 + 15% of 100
        assert_eq!(yarn_damage(&p, 100, true), 63); // 140%
    }

    #[test]
    fn an_ability_on_a_champion_takes_a_fifth_off() {
        assert_eq!(refund(&Params::default()), 120);
    }

    #[test]
    fn the_surge_takes_max_health_from_the_threads() {
        assert_eq!(surge_bonus(&Params::default(), 2000), 40); // 2%
    }

    #[test]
    fn three_trinkets_scattered_apart() {
        let s = trinket_spots((50_000, 30_000));
        assert_eq!(s, [(-1, (10_000, 30_000)), (0, (50_000, 30_000)), (1, (90_000, 30_000))]);
        assert_eq!(trinket_spots((5_000, 0))[0].1, (0, 0));
        // a champion on one trinket is not on the next
        assert!(TRINKET_DX as u64 > Params::default().p_tr);
    }

    #[test]
    fn a_trinket_rides_in_its_input() {
        for side in -1..=1 {
            for primed in [false, true] {
                let t = Trinket { at: (123_456, 78_901), until: 9_999, side, born: 9_759, primed };
                assert_eq!(Trinket::from_input(&t.input()), Some(t));
            }
        }
        let t = Trinket { at: (0, 0), until: 1, side: -1, born: 0, primed: false };
        assert_eq!(t.piece(), "tft_norra_p_trinket_l");
        assert_eq!(Trinket::from_input(&InputTargetV1::target(5)), None);
        assert_eq!(Trinket::from_input(&InputTargetV1 { dir_x: 3, ..t.input() }), None);
    }

    #[test]
    fn its_own_q_does_not_prime_a_trinket() {
        // dropped on the Q's landing tick b, the flag on her from the hit (b + 1) for PRIME_T ticks
        let b = 1000;
        assert!(b + 1 + PRIME_T <= b + PRIME_AGE);
        // a trinket dropped a tick before still sees it
        assert!(b + PRIME_T >= (b - 1) + PRIME_AGE);
    }

    #[test]
    fn the_nearest_champion_takes_it() {
        let foes = [(7, (10_000, 0)), (3, (0, 9_000)), (9, (30_000, 0))];
        assert_eq!(nearest(&foes, (0, 0), 26_000), Some(3));
        assert_eq!(nearest(&foes, (40_000, 0), 26_000), Some(9));
        assert_eq!(nearest(&foes, (100_000, 0), 26_000), None);
        assert_eq!(nearest(&[(4, (0, 5)), (2, (5, 0))], (0, 0), 10), Some(2)); // a tie: the lower id
    }

    #[test]
    fn a_volley_crosses_the_rift_at_the_champion_s_height() {
        let ((ax, ay), (bx, by)) = yarn_line((100_000, 100_000), 35_000, None);
        assert_eq!((ax, ay, bx, by), (65_000, 100_000, 135_000, 100_000));
        let ((ax, ay), (bx, _)) = yarn_line((100_000, 100_000), 35_000, Some((90_000, 121_000)));
        assert_eq!(ay, 121_000);
        assert!(ax > 65_000 && bx < 135_000 && ax + bx == 200_000);
        let (_, (_, y)) = yarn_line((100_000, 100_000), 30_000, Some((0, 400_000)));
        assert_eq!(y, 120_000); // kept within two thirds of the radius
        // a ball never steps over a unit (speed at most twice its radius)
        assert!(70_000 / BALL_TICKS <= 2 * BALL_RADIUS);
    }

    #[test]
    fn names_are_hers() {
        for n in [P_CD, Q_PRIME, W_CD, W_SLOW, T_MARK, T_SLOW, R_SLOW, R_TOOK, P_BURST, W_IN, W_LOCK, W_OUT, R_HIT, R_BALL,
                  SFX_DROP, SFX_BURST, SFX_W, SFX_BALL, SFX_HIT]
            .into_iter()
            .chain(PIECES)
            .chain(R_FIRST)
        {
            assert!(n.starts_with("tft_norra_"), "{n}");
        }
        for n in [TRINKET_FX, VOLLEY_FX].into_iter().chain(YARN_FX.into_iter().flatten()) {
            assert!(n.starts_with("tft_norra:"), "{n}");
        }
    }
}
