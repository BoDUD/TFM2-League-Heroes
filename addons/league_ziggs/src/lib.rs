//! 吉格斯附加包（用户 2026-10-18 选：「可以」——小扩展包；2026-11-14：「吉格斯和维克托按照联盟的重做」）：主包数据做不到的
//! 三件事在这里做。
//!
//! `mod.override_info` 把主包的吉格斯换成 `override/` 里的副本（tools/kit/build_ziggs.py 的 native=1）：数据和主包一样，
//! 只是守望里没有数据的 W（脚下自爆），被动挂本包的 `league_ziggs:hexplode`，弹跳炸弹第一次落地没炸到人时交给本包的
//! `league_ziggs:q_hop`，被动强化弹打中时给他挂 2 tick 的 `league_ziggs_p_now`。
//!
//! - **定点爆破**（英雄联盟 V25.04：扔到 1000 码内的一点，引爆时把敌人从爆炸中心往外推到 500 码（0.5 秒），炸到他自己就把他
//!   炸到离中心 825 码；血量低于 25–35% 的防御塔直接炸掉）：被动每 `LOOK` tick 看一次场面（他活着、3 级以上、W 不在冷却
//!   `league_ziggs_w_cd`、没在放别的技能 `league_ziggs_busy`、没被控住也没被推着走），按 [`decide`] 扔：
//!   1. 敌方英雄贴身（`w_trig` 以内，身体边到边，和主包一样）：炸药包放在两人之间（离他 `w_gap`），把那人往外炸、他自己往反方向
//!      被炸飞——他落下的地方在敌方塔下、或者那里还有两个以上别的敌方英雄就不扔；
//!   2. `w_hex_r` 以内有血量不到 `w_ex`% 的敌方防御塔：扔在塔上，炸掉；
//!   3. 生命 `w_catch_hp`% 以下的敌方英雄在 `w_catch_lo`..`w_catch_hi`（刚出他的普攻）：炸药包落在那人落地时会站的地方身后，
//!      把他炸回离吉格斯约 `w_keep`——他自己生命不到 `SAFE_HP`%、那人在敌方塔下、那边敌人比我们多就不扔。
//!   出手：W 进冷却、他的动作（贴身用 W 的蹲下放包，扔远用 E 的扔包）、声音、台词、一触即发少等三分之一（主包的 `cut`），
//!   `w_rel` / `e_rel` tick 后炸药包离手（`:throw`，雷包那张飞行图 `league_ziggs_w_throw`，每 tick `w_speed`），落地就炸
//!   （`:blast`）：`w_dmg` + `w_ratio`% 法强的魔法伤害、推人、炸塔（塔血量高于线就只吃伤害）、炸飞他自己。
//! - **弹跳炸弹往前弹**（英雄联盟 V25.14：落在瞄准点，旁边没敌人就往前弹，最多两次，每次 0.495 秒，远近按扔出的距离）：主包
//!   第一次落地没炸到人时原地弹起（数据的投射物只能从英雄身上出发）；副本交给 `:q_hop`：第二落点在第一落点再往前投掷距离的
//!   `q_b1`%，第三落点再往前那一段的 `q_b2`%（英雄联盟扔 850 码、连两次弹跳 1400 码：850 × (1 + 0.4 + 0.24) = 1394），空中的
//!   炸弹按弧线一帧帧贴在路上（主包的 `q_air<高度>`），落地旁边有敌人就炸（`q_dmg` + `q_ratio`% 法强），第三次一定炸；他死了
//!   炸弹就停（和主包一样）。
//! - **一触即发打塔**（英雄联盟：对建筑 ×1.75）：被动强化弹打中防御塔的那一下伤害 ×`p_tower`%（整下，含普攻本身的部分）。
//!
//! 本包不按任何技能键。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ziggs.log`，每次启动游戏重写：`SATCHEL`（扔出、
//! 为什么、扔多远）、`BLAST`（炸到几个、推到哪、他被炸飞多远）、`HEXPLODE`（炸掉的塔）、`HOP` / `BOUNCE` / `QBLAST`（弹跳炸弹）、
//! `FUSE`（强化弹打塔）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_ziggs";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_ziggs") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

fn sn(x: &str) -> String {
    format!("league_ziggs_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ZIGGS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ziggs.log");
        }
    }
    PathBuf::from("league_ziggs.log")
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
const LOG_EVERY: usize = 50;
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数；`make_override.py` 写进去）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 炸塔的血量线：最大生命的百分比（英雄联盟 25–35%）。
    pub w_ex: u64,
    /// 能炸的塔离他多远（他和塔中心；英雄联盟扔 1000 码。原来的 60000 够不着：他站在攻击距离 55000 外打塔，
    /// 加上两边的半径离塔中心 75000 以上，2026-10-22 两份日志一次都没炸过）。
    pub w_hex_r: u64,
    /// W 的冷却（tick，主包数据的 `league_ziggs_w_cd`）。
    pub w_cd: usize,
    /// 被动强化弹打塔的倍率（%）。
    pub p_tower: u64,
    /// 炸药包：伤害（固定 + 法强%）、爆炸半径、贴身多近（身体边到边，同主包的 `RandomTarget`）、贴身那次的动作时长和出手 tick、
    /// 他被炸飞时每 tick 走多远。
    pub w_dmg: u64,
    pub w_ratio: u64,
    pub w_r: u64,
    pub w_trig: u64,
    pub w_dur: usize,
    pub w_rel: usize,
    pub w_hop: u64,
    /// 英雄联盟的数（×100）：能扔多远、每 tick 飞多远、敌人被推到离炸点多远、推多少 tick、他自己被炸到离炸点多远。
    pub w_range: u64,
    pub w_speed: u64,
    pub w_push: u64,
    pub w_push_t: usize,
    pub w_self: u64,
    /// 贴身那次炸药包往敌人那边放多远；「炸回来」：生命不高于 `w_catch_hp`%、离他 `w_catch_lo`..`w_catch_hi`（中心距离）的
    /// 敌方英雄，炸到离他 `w_keep`。
    pub w_gap: u64,
    pub w_catch_hp: u64,
    pub w_catch_lo: u64,
    pub w_catch_hi: u64,
    pub w_keep: u64,
    /// 扔远那次用 E 扔雷包的动作：时长、出手 tick。
    pub e_dur: usize,
    pub e_rel: usize,
    /// 一触即发的等待（每放一个技能少三分之一，W 也算）、台词的间隔。
    pub p_t: usize,
    pub vo_gap: usize,
    /// 弹跳炸弹：伤害、爆炸半径（加身体）、第二 / 第三次落地离上一次多少 tick、两次弹起的高度（主包 q_air 图的高度）、
    /// 空中的炸弹每几 tick 贴一帧、两次弹跳的远近（第一段是投掷距离的 `q_b1`%，第二段是第一段的 `q_b2`%）。
    pub q_dmg: u64,
    pub q_ratio: u64,
    pub q_r: u64,
    pub q_t2: usize,
    pub q_t3: usize,
    pub q_h2: u64,
    pub q_h3: u64,
    pub q_step: usize,
    pub q_b1: u64,
    pub q_b2: u64,
}

impl Default for Params {
    fn default() -> Self {
        Params {
            w_ex: 30,
            w_hex_r: 100000,
            w_cd: 900,
            p_tower: 175,
            w_dmg: 80,
            w_ratio: 50,
            w_r: 30000,
            w_trig: 22000,
            w_dur: 24,
            w_rel: 8,
            w_hop: 4000,
            w_range: 100000,
            w_speed: 3000,
            w_push: 50000,
            w_push_t: 30,
            w_self: 82500,
            w_gap: 10000,
            w_catch_hp: 40,
            w_catch_lo: 72000,
            w_catch_hi: 90000,
            w_keep: 45000,
            e_dur: 27,
            e_rel: 9,
            p_t: 720,
            vo_gap: 600,
            q_dmg: 75,
            q_ratio: 60,
            q_r: 20000,
            q_t2: 30,
            q_t3: 30,
            q_h2: 10,
            q_h3: 6,
            q_step: 3,
            q_b1: 40,
            q_b2: 60,
        }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        match k {
            "w_ex" => p.w_ex = v,
            "w_hex_r" => p.w_hex_r = v,
            "w_cd" => p.w_cd = v as usize,
            "p_tower" => p.p_tower = v,
            "w_dmg" => p.w_dmg = v,
            "w_ratio" => p.w_ratio = v,
            "w_r" => p.w_r = v,
            "w_trig" => p.w_trig = v,
            "w_dur" => p.w_dur = v as usize,
            "w_rel" => p.w_rel = v as usize,
            "w_hop" => p.w_hop = v,
            "w_range" => p.w_range = v,
            "w_speed" => p.w_speed = v,
            "w_push" => p.w_push = v,
            "w_push_t" => p.w_push_t = v as usize,
            "w_self" => p.w_self = v,
            "w_gap" => p.w_gap = v,
            "w_catch_hp" => p.w_catch_hp = v,
            "w_catch_lo" => p.w_catch_lo = v,
            "w_catch_hi" => p.w_catch_hi = v,
            "w_keep" => p.w_keep = v,
            "e_dur" => p.e_dur = v as usize,
            "e_rel" => p.e_rel = v as usize,
            "p_t" => p.p_t = v as usize,
            "vo_gap" => p.vo_gap = v as usize,
            "q_dmg" => p.q_dmg = v,
            "q_ratio" => p.q_ratio = v,
            "q_r" => p.q_r = v,
            "q_t2" => p.q_t2 = v as usize,
            "q_t3" => p.q_t3 = v as usize,
            "q_h2" => p.q_h2 = v,
            "q_h3" => p.q_h3 = v,
            "q_step" => p.q_step = v as usize,
            "q_b1" => p.q_b1 = v,
            "q_b2" => p.q_b2 = v,
            _ => {}
        }
    }
    p
}

/// 原生效果（出手、爆炸、弹跳）没有自己的参数：被动读到英雄数据的参数时记在这里（每个吉格斯的副本都是同一张表，
/// 默认值就是副本里的数：单元测试 `params_from_the_kit` 核对）。
static PARAMS: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

fn params() -> Params {
    *PARAMS.lock().unwrap_or_else(|e| e.into_inner())
}

// ===================== 计算（单元测试用） =====================

pub type Pt = (f64, f64);

/// 读不到身体半径时用的。
pub const BODY: f64 = 10_000.0;
/// 地图是 960000 见方。
pub const MAP: f64 = 959_999.0;
/// 敌方塔下（他落下的地方、要炸回来的人离敌方塔这么近就不扔）、数两边人数的范围（同 league_ult_press）。
pub const TOWER_REACH: f64 = 75_000.0;
pub const CROWD_R: f64 = 60_000.0;
/// 贴身往外炸时，他落下的地方这么近有两个以上别的敌方英雄就不炸（炸进人堆）。
pub const LAND_R: f64 = 40_000.0;
/// 「炸回来」只在他自己生命不低于这个 % 时做。
pub const SAFE_HP: f64 = 35.0;
/// 每隔这么多 tick 看一次；量敌方英雄的速度用最近这么多 tick。
pub const LOOK: usize = 6;
pub const LEAD_T: usize = 6;
/// 「炸回来」时炸点最少在那人身后多远（预判走偏了也是往吉格斯这边推）。
pub const CATCH_BEHIND: f64 = 8_000.0;

pub fn dist(a: Pt, b: Pt) -> f64 {
    (a.0 - b.0).hypot(a.1 - b.1)
}

pub fn unit(v: Pt) -> Option<Pt> {
    let d = v.0.hypot(v.1);
    (d >= 1.0).then(|| (v.0 / d, v.1 / d))
}

pub fn on_map(p: Pt) -> Pt {
    (p.0.clamp(0.0, MAP), p.1.clamp(0.0, MAP))
}

fn lerp(a: Pt, b: Pt, f: f64) -> Pt {
    (a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f)
}

/// 这座塔低到能炸了吗（还活着、血量不到 w_ex%）。
pub fn hexplodable(p: &Params, hp: usize, max_hp: usize) -> bool {
    hp > 0 && max_hp > 0 && (hp as u64) * 100 <= p.w_ex * max_hp as u64
}

/// 塔在不在炸药包能扔到的地方。
pub fn in_reach(p: &Params, me: (u64, u64), tower: (u64, u64)) -> bool {
    let dx = me.0 as f64 - tower.0 as f64;
    let dy = me.1 as f64 - tower.1 as f64;
    dx * dx + dy * dy <= (p.w_hex_r as f64) * (p.w_hex_r as f64)
}

/// 被动强化弹打塔的伤害。
pub fn tower_hit(p: &Params, damage: usize) -> usize {
    (damage as u64 * p.p_tower / 100) as usize
}

/// 爆炸把站在 `at` 的单位炸到哪里：从炸点 `centre` 往外，一直到离炸点 `to`（已经那么远的不动）。正好站在炸点上的往 `spare`
/// 那边去（没有方向可算时）。
pub fn thrown_to(centre: Pt, at: Pt, to: f64, spare: Pt) -> Option<Pt> {
    let d = dist(centre, at);
    if d >= to {
        return None;
    }
    let u = unit((at.0 - centre.0, at.1 - centre.1)).or_else(|| unit(spare))?;
    Some(on_map((centre.0 + u.0 * to, centre.1 + u.1 * to)))
}

/// 贴身往外炸：炸药包放在他和冲上来的敌人之间，离他不超过 `w_gap`、也不过两人的中点。
pub fn escape_centre(p: &Params, me: Pt, foe: Pt) -> Pt {
    let d = dist(me, foe);
    let g = (d / 2.0).min(p.w_gap as f64);
    match unit((foe.0 - me.0, foe.1 - me.1)) {
        Some(u) => (me.0 + u.0 * g, me.1 + u.1 * g),
        None => (me.0 + 1.0, me.1),
    }
}

/// 「炸回来」：炸药包落在敌人（爆炸那一刻在 `foe`）身后，把他朝吉格斯炸回 `w_keep` 远。敌人不在 `w_catch_lo`..`w_catch_hi`、
/// 或者落点扔不到，就没有。
pub fn catch_centre(p: &Params, me: Pt, foe: Pt) -> Option<Pt> {
    let d = dist(me, foe);
    if d < p.w_catch_lo as f64 || d > p.w_catch_hi as f64 {
        return None;
    }
    // he ends w_push from the centre on Ziggs's side: d - (w_push - b) = w_keep
    let b = (p.w_keep as f64 + p.w_push as f64 - d).clamp(CATCH_BEHIND, p.w_r as f64);
    let u = unit((foe.0 - me.0, foe.1 - me.1))?;
    let centre = (foe.0 + u.0 * b, foe.1 + u.1 * b);
    (dist(me, centre) <= p.w_range as f64 && centre == on_map(centre)).then_some(centre)
}

/// 炸药包飞多少 tick。
pub fn flight(p: &Params, from: Pt, to: Pt) -> usize {
    (dist(from, to) / p.w_speed.max(1) as f64).ceil().max(1.0) as usize
}

/// 一个敌方英雄：编号、位置、每 tick 的位移、生命 %、身体半径。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub vel: Pt,
    pub hp: f64,
    pub r: f64,
}

/// 一座敌方防御塔：编号、位置、生命。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Tower {
    pub id: usize,
    pub at: Pt,
    pub hp: usize,
    pub max_hp: usize,
}

/// 他眼前的场面。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Scene {
    pub me: Pt,
    pub me_r: f64,
    pub hp: f64,
    pub foes: Vec<Foe>,
    pub allies: Vec<Pt>,
    pub towers: Vec<Tower>,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Why {
    /// 敌方英雄贴身：炸药包放在两人之间，把他炸开、自己被炸飞。
    Escape(usize),
    /// 够得着的敌方塔血量低于线：炸在塔上。
    Tower(usize),
    /// 残血的敌方英雄在够不着的地方：炸药包落在他身后，把他炸回来。
    Catch(usize),
}

/// 一次出手：炸点、为什么、离手后飞多少 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Throw {
    pub centre: Pt,
    pub why: Why,
    pub flight: usize,
}

fn under_tower(s: &Scene, at: Pt) -> bool {
    s.towers.iter().any(|t| dist(t.at, at) <= TOWER_REACH)
}

/// 现在扔不扔、扔到哪（W 好着、3 级以上、没在放别的、没被控住时才问）。先自保，再炸塔，再把残血的炸回来。
pub fn decide(p: &Params, s: &Scene) -> Option<Throw> {
    // 1. a champion on him (edge to edge, as the main pack's RandomTarget): the satchel between the two. Not when it
    //    would throw him under an enemy tower or into two more enemies
    let diver = s.foes.iter().filter(|f| dist(s.me, f.at) <= p.w_trig as f64 + s.me_r + f.r)
        .min_by(|a, b| dist(s.me, a.at).total_cmp(&dist(s.me, b.at)));
    if let Some(f) = diver {
        let centre = escape_centre(p, s.me, f.at);
        let land = thrown_to(centre, s.me, p.w_self as f64, (s.me.0 - f.at.0, s.me.1 - f.at.1)).unwrap_or(s.me);
        let crowd = s.foes.iter().filter(|o| o.id != f.id && dist(o.at, land) <= LAND_R).count();
        if under_tower(s, land) || crowd >= 2 {
            return None;
        }
        return Some(Throw { centre, why: Why::Escape(f.id), flight: flight(p, s.me, centre) });
    }
    // 2. a tower low enough within the throw
    let me_u = (s.me.0.max(0.0) as u64, s.me.1.max(0.0) as u64);
    if let Some(t) = s.towers.iter().find(|t| {
        hexplodable(p, t.hp, t.max_hp) && in_reach(p, me_u, (t.at.0 as u64, t.at.1 as u64))
    }) {
        return Some(Throw { centre: t.at, why: Why::Tower(t.id), flight: flight(p, s.me, t.at) });
    }
    // 3. a wounded champion out of his reach: behind where he will be when it lands
    if s.hp < SAFE_HP {
        return None;
    }
    let mut best: Option<(Throw, f64)> = None;
    for f in s.foes.iter().filter(|f| f.hp <= p.w_catch_hp as f64) {
        // where he is when the satchel lands: one refinement of the flight time
        let lead = |t: usize| (f.at.0 + f.vel.0 * t as f64, f.at.1 + f.vel.1 * t as f64);
        let first = lead(p.e_rel + flight(p, s.me, f.at));
        let Some(c0) = catch_centre(p, s.me, first) else { continue };
        let then = lead(p.e_rel + flight(p, s.me, c0));
        let Some(centre) = catch_centre(p, s.me, then) else { continue };
        if under_tower(s, then) {
            continue;
        }
        let theirs = s.foes.iter().filter(|o| dist(o.at, then) <= CROWD_R).count().max(1);
        let ours = s.allies.iter().filter(|&&a| dist(a, then) <= CROWD_R).count() + 1;
        if theirs > ours {
            continue;
        }
        if best.is_none_or(|(_, hp)| f.hp < hp) {
            best = Some((Throw { centre, why: Why::Catch(f.id), flight: flight(p, s.me, centre) }, f.hp));
        }
    }
    best.map(|b| b.0)
}

/// 一触即发的三个等待标记里还在的最长的那个（每放一个技能拿掉它：主包的 `cut`）。
pub fn fuse_cut(has: impl Fn(&str) -> bool) -> Option<&'static str> {
    ["p_c", "p_b", "p_a"].into_iter().find(|f| has(&sn(f)))
}

/// 第 k 次落地（2 或 3）前空中的炸弹：(上一次落地后第几 tick, q_air 图的高度)——主包 build_ziggs.air_heights 的同一张表
/// （Python 的 round 是四舍六入五成双）。
pub fn air_heights(p: &Params, k: usize) -> Vec<(usize, u64)> {
    let (t, h) = if k == 2 { (p.q_t2, p.q_h2) } else { (p.q_t3, p.q_h3) };
    let step = p.q_step.max(1);
    (step..t)
        .step_by(step)
        .map(|s| {
            let f = s as f64 / t as f64;
            let raw = (4.0 * h as f64 * f * (1.0 - f)).round_ties_even() as u64;
            (s, (raw.min(18) / 2 * 2).max(2))
        })
        .collect()
}

/// 第二、第三落点：第一落点 `l1` 再往前（从他 `z` 看过去）投掷距离的 `q_b1`%，再往前那一段的 `q_b2`%。他站在落点上就没有。
pub fn bounces(p: &Params, z: Pt, l1: Pt) -> Option<(Pt, Pt)> {
    let u = unit((l1.0 - z.0, l1.1 - z.1))?;
    let b1 = dist(z, l1) * p.q_b1 as f64 / 100.0;
    let b2 = b1 * p.q_b2 as f64 / 100.0;
    let l2 = on_map((l1.0 + u.0 * b1, l1.1 + u.1 * b1));
    let l3 = on_map((l2.0 + u.0 * b2, l2.1 + u.1 * b2));
    Some((l2, l3))
}

// ===================== 小工具 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn cc_immune(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.cc_immune))
}

fn is_tower(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).and_then(|e| e.kind()).is_some_and(|k| k == EntityKindV1::Tower)
}

fn fpos(e: &StableEntity<'_, '_>) -> Pt {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

fn upos(p: Pt) -> InputTargetV1 {
    let p = on_map(p);
    InputTargetV1::pos(p.0.round() as u64, p.1.round() as u64)
}

fn input_pos(input: &InputTargetV1) -> Option<Pt> {
    (input.kind == InputTargetKindV1::Pos.code()).then_some((input.x as f64, input.y as f64))
}

fn body(e: &StableEntity<'_, '_>) -> f64 {
    let r = e.radius();
    if r > 0 { r as f64 } else { BODY }
}

/// 按住他、让他放不出技能的控制，和别人推着他走（英雄联盟：被定住、被击飞时不出手，也不会被自己的炸药包炸飞）。
const HELD: [CcKindV1; 8] = [CcKindV1::Bind, CcKindV1::Stun, CcKindV1::Airborne, CcKindV1::Taunt, CcKindV1::Fear,
                             CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::ForceMove];

fn held(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id)
        .is_some_and(|e| (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HELD.iter().any(|k| k.code() == c.kind))))
}

fn refresh(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

/// 强制位移到 `to`（速度取整到每 tick 一样长，`ticks` tick 走完）。
fn force_move(sim: &mut StableSim<'_>, id: usize, from: Pt, to: Pt, ticks: usize) -> f64 {
    let d = dist(from, to);
    if d < 1.0 {
        return 0.0;
    }
    let ticks = ticks.max(1);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (to.0 - from.0).round() as i64;
    cc.dy = (to.1 - from.1).round() as i64;
    cc.speed = (d / ticks as f64).ceil() as u64;
    sim.apply_cc(id, &cc);
    d
}

fn queue(sim: &mut StableSim<'_>, stage: &str, caster: usize, at: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{stage}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &at, delay.max(1)) {
        if let Some(k) = counted("refused") {
            wlog(format!("{} queue_effect({name}) refused #{k}", head(sim, caster)));
        }
    }
}

/// 炸点 `at` 半径 `r`（加身体）以内活着、选得中的敌方单位（防御塔、水晶不算）：(编号, 位置, 推得动吗——大型野怪不推)。
fn foes_near(sim: &StableSim<'_>, team: usize, at: Pt, r: f64) -> Vec<(usize, Pt, bool)> {
    let mut out = Vec::new();
    for u in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
        if !u.is_alive() || u.team() == team || !u.is_targetable() || u.is_tower()
            || matches!(u.kind(), Some(EntityKindV1::Nexus | EntityKindV1::Tower))
        {
            continue;
        }
        let p = fpos(&u);
        if dist(p, at) <= r + body(&u) {
            out.push((u.id(), p, !matches!(u.kind(), Some(EntityKindV1::Epic | EntityKindV1::Serpen))));
        }
    }
    out
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Hexplode {
    p: Params,
    me: usize,
    /// 敌方英雄最近几 tick 的位置（量速度：「炸回来」要落在他那时站的地方后面）。
    trail: HashMap<usize, Vec<Pt>>,
    next_look: usize,
}

impl Hexplode {
    /// 记下敌方英雄的位置，算出场面。
    fn scene(&mut self, sim: &StableSim<'_>, me: usize) -> Option<Scene> {
        let e = sim.get_entity(me)?;
        let team = e.team();
        let (hp, max) = e.hp();
        let mut s = Scene { me: fpos(&e), me_r: body(&e), hp: hp as f64 * 100.0 / max.max(1) as f64, ..Scene::default() };
        let mut seen = Vec::new();
        for u in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
            if !u.is_alive() || u.id() == me {
                continue;
            }
            if u.is_tower() && u.team() != team {
                let (hp, max_hp) = u.hp();
                s.towers.push(Tower { id: u.id(), at: fpos(&u), hp, max_hp });
            } else if u.is_champion() && u.team() == team {
                s.allies.push(fpos(&u));
            } else if u.is_champion() && u.is_targetable() {
                let at = fpos(&u);
                let trail = self.trail.entry(u.id()).or_default();
                // a blink or a respawn: the old trail says nothing about where he goes
                if trail.last().is_some_and(|&last| dist(last, at) > 20_000.0) {
                    trail.clear();
                }
                trail.push(at);
                if trail.len() > LEAD_T + 1 {
                    trail.remove(0);
                }
                let n = (trail.len() - 1).max(1) as f64;
                let vel = ((at.0 - trail[0].0) / n, (at.1 - trail[0].1) / n);
                let (hp, max) = u.hp();
                s.foes.push(Foe { id: u.id(), at, vel, hp: hp as f64 * 100.0 / max.max(1) as f64, r: body(&u) });
                seen.push(u.id());
            }
        }
        self.trail.retain(|id, _| seen.contains(id));
        Some(s)
    }

    /// 出手：冷却、动作、声音、一触即发少等三分之一；`rel` tick 后炸药包离手（`:throw`）。
    fn throw(&mut self, sim: &mut StableSim<'_>, me: usize, t: Throw, s: &Scene) {
        let far = !matches!(t.why, Why::Escape(_));
        let (pose, dur, rel) = if far { ("skill2", self.p.e_dur, self.p.e_rel) } else { ("skill_w", self.p.w_dur, self.p.w_rel) };
        refresh(sim, me, &sn("w_cd"), self.p.w_cd);
        refresh(sim, me, &sn("busy"), dur);
        let mut anim = CcV1::of_kind(CcKindV1::Animation, dur as u64);
        anim.set_name(pose);
        sim.apply_cc(me, &anim);
        let at_me = InputTargetV1::target(me);
        sim.play_sfx(&sn("w"), me, &at_me);
        if !has(sim, me, &sn("vo_cd")) {
            sim.add_buff(me, &BuffV1::timed(&sn("vo_cd"), self.p.vo_gap));
            sim.play_sfx(&sn("vo_w"), me, &at_me);
        }
        if let Some(flag) = fuse_cut(|name| has(sim, me, name)) {
            sim.entity_remove_buff(me, &sn(flag));
        }
        queue(sim, "throw", me, upos(t.centre), rel);
        if let Some(k) = counted("satchel") {
            let d = dist(s.me, t.centre);
            wlog(format!(
                "{} SATCHEL #{k} {:?}: thrown {d:.0} to ({:.0}, {:.0}), lands {} ticks after it leaves (hp {:.0}%, {} foes, {} allies)",
                head(sim, me),
                t.why,
                t.centre.0,
                t.centre.1,
                t.flight,
                s.hp,
                s.foes.len(),
                s.allies.len()
            ));
        }
    }

    fn look(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        let Some(s) = self.scene(sim, me) else { return };
        if now < self.next_look {
            return;
        }
        self.next_look = now + LOOK;
        let ready = sim.get_entity(me).is_some_and(|e| e.is_alive() && e.level() >= 3)
            && !has(sim, me, &sn("w_cd"))
            && !has(sim, me, &sn("busy"))
            && !held(sim, me);
        if !ready {
            return;
        }
        if let Some(t) = decide(&self.p, &s) {
            self.throw(sim, me, t, &s);
        }
    }
}

impl StablePassive for Hexplode {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
        *PARAMS.lock().unwrap_or_else(|e| e.into_inner()) = self.p;
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.trail.clear();
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Ziggs (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            self.look(sim, me);
        }
    }

    /// Short Fuse's bomb on a tower: x p_tower%.
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        if *damage == 0 || !has(sim, me, &sn("p_now")) || !is_tower(sim, target) {
            return;
        }
        let was = *damage;
        *damage = tower_hit(&self.p, was);
        if let Some(k) = counted("fuse") {
            wlog(format!("{} FUSE #{k}: Short Fuse on tower #{target}: {was} -> {}", head(sim, me), *damage));
        }
    }
}

// ===================== 炸药包：离手、爆炸 =====================

/// 飞着的炸药包的画面（副本的 `view_projectiles`：雷包的那张图）。
pub const BAG: &str = "league_ziggs_w_throw";

/// 炸药包离手（`rel` tick 后，他还活着）：从他手里飞向炸点，落地就炸。
struct ThrowFx;

impl StableEffectType for ThrowFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(centre) = input_pos(&input) else { return };
        let Some(e) = sim.get_entity(caster).filter(|e| e.is_alive()) else { return };
        let (from, team) = (fpos(&e), e.team());
        let p = params();
        let ticks = flight(&p, from, centre);
        let spec = ProjectileSpawnV1 {
            caster_id: caster,
            team,
            x: from.0.round() as u64,
            y: from.1.round() as u64,
            radius: 1_000,
            speed: p.w_speed.max(1),
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: input.x,
            target_y: input.y,
            penetrate: true,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        if dist(from, centre) > p.w_speed as f64 && !sim.spawn_projectile(BAG, &format!("{ID}:noop"), &spec) {
            if let Some(k) = counted("refused") {
                wlog(format!("{} spawn_projectile({BAG}) refused #{k}", head(sim, caster)));
            }
        }
        queue(sim, "blast", caster, input, ticks);
    }
}

/// 炸药包落地爆炸（英雄联盟：从炸点把敌人往外推到 500 码，吉格斯自己在里面就被炸到 825 码，血量低的塔直接炸掉，别的塔吃伤害）。
struct BlastFx;

impl StableEffectType for BlastFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(centre) = input_pos(&input) else { return };
        let Some(me) = sim.get_entity(caster) else { return };
        let (team, me_at, me_alive, me_body) = (me.team(), fpos(&me), me.is_alive(), body(&me));
        let ap = me.stat().magic_power as u64;
        let p = params();
        sim.play_view_effect(&sn("w_blast"), caster, &input, 0, 0, 0);
        sim.play_sfx(&sn("w_blast"), caster, &input);
        let damage = (p.w_dmg + p.w_ratio * ap / 100) as usize;
        // enemies in the blast: units (pushed from its centre), towers (blown up when low enough, else hurt)
        let units = foes_near(sim, team, centre, p.w_r as f64);
        let mut towers = Vec::new();
        for u in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
            if u.is_alive() && u.team() != team && u.is_tower() && dist(fpos(&u), centre) <= p.w_r as f64 + body(&u) {
                let (hp, max_hp) = u.hp();
                towers.push((u.id(), hp, max_hp));
            }
        }
        let spare = (centre.0 - me_at.0, centre.1 - me_at.1);
        let mut pushed = 0;
        for &(id, at, movable) in &units {
            sim.deal_damage_typed(caster, id, damage, DamageTypeV1::Ap, AttackTypeV1::Skill);
            if movable && !cc_immune(sim, id) && sim.get_entity(id).is_some_and(|u| u.is_alive()) {
                if let Some(to) = thrown_to(centre, at, p.w_push as f64, spare) {
                    force_move(sim, id, at, to, p.w_push_t);
                    pushed += 1;
                }
            }
            let on_him = InputTargetV1::target(id);
            sim.play_view_effect(&sn("w_hit"), caster, &on_him, 0, 0, 0);
            sim.play_sfx(&sn("w_hit"), caster, &on_him);
        }
        let mut blown = 0;
        for &(id, hp, max_hp) in &towers {
            if hexplodable(&p, hp, max_hp) {
                sim.deal_damage_typed(caster, id, hp, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                blown += 1;
                if let Some(k) = counted("hexplode") {
                    wlog(format!("{} HEXPLODE #{k}: tower #{id} at {hp}/{max_hp} blown up", head(sim, caster)));
                }
            } else {
                sim.deal_damage_typed(caster, id, damage, DamageTypeV1::Ap, AttackTypeV1::Skill);
            }
        }
        // caught in his own blast: thrown away from its centre (not while held or pushed by someone)
        let mut hop = 0.0;
        if me_alive && dist(me_at, centre) <= p.w_r as f64 + me_body && !held(sim, caster) {
            // standing right on it: away from the nearest enemy caught
            let near = units.iter().map(|u| u.1).min_by(|a, b| dist(*a, me_at).total_cmp(&dist(*b, me_at)));
            let spare = near.map_or((-1.0, 0.0), |n| (me_at.0 - n.0, me_at.1 - n.1));
            if let Some(to) = thrown_to(centre, me_at, p.w_self as f64, spare) {
                let ticks = (dist(me_at, to) / p.w_hop.max(1) as f64).ceil() as usize;
                hop = force_move(sim, caster, me_at, to, ticks);
            }
        }
        if let Some(k) = counted("blast") {
            wlog(format!(
                "{} BLAST #{k} at ({:.0}, {:.0}): {} enemies hit for {damage} ({pushed} pushed out to {}), {} tower(s) in it ({blown} blown up), he was thrown {hop:.0}",
                head(sim, caster),
                centre.0,
                centre.1,
                units.len(),
                p.w_push,
                towers.len()
            ));
        }
    }
}

/// 飞着的炸药包碰到谁都不做什么（落地才炸）。
struct Noop;

impl StableEffectType for Noop {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 弹跳炸弹：往前弹 =====================

/// 弹跳炸弹第一次落地 2 tick 后旁边没有敌人（主包的 `q_boom` 没亮，副本的数据调到这里，输入是第一落点）：往前弹两次。
/// 第二、第三次落地和两段空中的炸弹现在就排好（`:q_land2` / `:q_land3`、`:q_air<h>`），第二次落地炸了就挂上 `q_done`，
/// 后面的都不做。方向和远近按他现在站的地方到第一落点算（出手 13 tick 后扔出、飞 26 tick，他多半还站在原地）。
struct QHop;

impl StableEffectType for QHop {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(l1) = input_pos(&input) else { return };
        let Some(z) = sim.get_entity(caster).filter(|e| e.is_alive()).map(|e| fpos(&e)) else { return };
        let p = params();
        let Some((l2, l3)) = bounces(&p, z, l1) else { return };
        // this runs 2 ticks after the first landing (the data's look at q_boom); bounce 2 lands q_t2 after that landing
        let t2 = p.q_t2.max(3);
        for (s, h) in air_heights(&p, 2) {
            if s > 2 {
                queue(sim, &format!("q_air{h}"), caster, upos(lerp(l1, l2, s as f64 / t2 as f64)), s - 2);
            }
        }
        queue(sim, "q_land2", caster, upos(l2), t2 - 2);
        let t3 = p.q_t3.max(1);
        for (s, h) in air_heights(&p, 3) {
            queue(sim, &format!("q_air{h}"), caster, upos(lerp(l2, l3, s as f64 / t3 as f64)), t2 - 2 + s);
        }
        queue(sim, "q_land3", caster, upos(l3), t2 - 2 + t3);
        if let Some(k) = counted("q_hop") {
            wlog(format!("{} HOP #{k}: nobody at ({:.0}, {:.0}) {:.0} from him: bounces to ({:.0}, {:.0}) and ({:.0}, {:.0})",
                         head(sim, caster), l1.0, l1.1, dist(z, l1), l2.0, l2.1, l3.0, l3.1));
        }
    }
}

/// 空中的炸弹的一帧（主包的 `league_ziggs_q_air<h>`：画着离地 h 像素的炸弹）。炸弹已经炸了（`q_done`）或他死了就不贴。
struct Stamp(u64);

impl StableEffectType for Stamp {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if input_pos(&input).is_none()
            || !sim.get_entity(caster).is_some_and(|e| e.is_alive())
            || has(sim, caster, &sn("q_done"))
        {
            return;
        }
        sim.play_view_effect(&sn(&format!("q_air{}", self.0)), caster, &input, 0, 0, 0);
    }
}

/// 第二 / 第三次落地：旁边（`q_r` 加身体）有敌人（防御塔不算，同主包的 `EnemyWithoutTower`）就炸，第三次一定炸；
/// 没炸就弹起（`q_bounce`）。
struct QLand {
    last: bool,
}

impl StableEffectType for QLand {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = input_pos(&input) else { return };
        let Some(e) = sim.get_entity(caster) else { return };
        if !e.is_alive() || has(sim, caster, &sn("q_done")) {
            return;
        }
        let (team, ap) = (e.team(), e.stat().magic_power as u64);
        let p = params();
        let foes = foes_near(sim, team, at, p.q_r as f64);
        if foes.is_empty() && !self.last {
            sim.play_view_effect(&sn("q_bounce"), caster, &input, 0, 0, 0);
            sim.play_sfx(&sn("q_bounce"), caster, &input);
            if let Some(k) = counted("q_bounce") {
                wlog(format!("{} BOUNCE #{k}: nobody at ({:.0}, {:.0}) either", head(sim, caster), at.0, at.1));
            }
            return;
        }
        sim.play_view_effect(&sn("q_blast"), caster, &input, 0, 0, 0);
        sim.play_sfx(&sn("q_blast"), caster, &input);
        let damage = (p.q_dmg + p.q_ratio * ap / 100) as usize;
        for &(id, _, _) in &foes {
            sim.deal_damage_typed(caster, id, damage, DamageTypeV1::Ap, AttackTypeV1::Skill);
            let on_him = InputTargetV1::target(id);
            sim.play_view_effect(&sn("q_hit"), caster, &on_him, 0, 0, 0);
            sim.play_sfx(&sn("q_hit"), caster, &on_him);
        }
        if !self.last {
            sim.add_buff(caster, &BuffV1::timed(&sn("q_done"), p.q_t3 + 4));
        }
        if let Some(k) = counted("q_blast") {
            wlog(format!("{} QBLAST #{k}: landing {} at ({:.0}, {:.0}): {} enemies hit for {damage}", head(sim, caster),
                         if self.last { 3 } else { 2 }, at.0, at.1, foes.len()));
        }
    }
}

/// 空中炸弹的图有这些高度（主包的 q_air2..q_air18）。
const AIR: [u64; 9] = [2, 4, 6, 8, 10, 12, 14, 16, 18];

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Ziggs: League's Satchel Charge - thrown, pushing from the blast, hexploding low towers; Bouncing Bomb bouncing on along the throw; Short Fuse x1.75 on towers) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:throw"), ThrowFx);
    module.add_native_effect(format!("{ID}:blast"), BlastFx);
    module.add_native_effect(format!("{ID}:noop"), Noop);
    module.add_native_effect(format!("{ID}:q_hop"), QHop);
    module.add_native_effect(format!("{ID}:q_land2"), QLand { last: false });
    module.add_native_effect(format!("{ID}:q_land3"), QLand { last: true });
    for h in AIR {
        module.add_native_effect(format!("{ID}:q_air{h}"), Stamp(h));
    }
    module.add_native_passive(format!("{ID}:hexplode"), Hexplode::default());
    host.log(LogLevel::Info, "league_ziggs loaded (League's Satchel Charge and Bouncing Bomb, Short Fuse x1.75 on towers).");
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

    fn p() -> Params {
        Params::default()
    }

    fn foe(id: usize, x: f64, hp: f64) -> Foe {
        Foe { id, at: (x, 500_000.0), vel: (0.0, 0.0), hp, r: BODY }
    }

    fn scene(foes: Vec<Foe>) -> Scene {
        Scene { me: (500_000.0, 500_000.0), me_r: BODY, hp: 100.0, foes, allies: Vec::new(), towers: Vec::new() }
    }

    #[test]
    fn params_from_the_kit() {
        // the override's own params are this file's defaults (the effects read them before any configure)
        let text = include_str!("../override/league_ziggs.data_champion");
        let at = text.find("\"passive_ref\": \"league_ziggs:hexplode\"").expect("the passive in the override");
        let body = &text[at..];
        let json = &body[body.find('{').unwrap()..=body.find('}').unwrap()];
        assert_eq!(parse_params(json), Params::default(), "{json}");
        for key in ["w_catch_lo", "q_b1", "q_b2", "e_dur", "q_step"] {
            assert!(json.contains(&format!("\"{key}\"")), "{key} in the copy's params");
        }
        assert_eq!(parse_params(r#"{"w_push":40000,"w_self":70000,"unknown":3}"#), Params { w_push: 40000, w_self: 70000, ..p() });
        // the copy has the flying bag's picture, no data Satchel Charge of its own and hands Q's bounces to q_hop
        assert!(text.contains(&format!("\"name\": \"{BAG}\"")), "the bag's view in the override");
        assert!(!text.contains("\"MoveBack\""), "the watch's own at-his-feet W is not in the copy");
        assert!(text.contains("\"effect_ref\": \"league_ziggs:q_hop\""), "Q's bounce in the copy");
        assert!(!text.contains("league_ziggs_q_z2"), "no data landing 2 in the copy");
        // every bomb height the bounces stamp is a picture of the copy
        for k in [2, 3] {
            for (_, h) in air_heights(&p(), k) {
                assert!(AIR.contains(&h) && text.contains(&format!("\"name\": \"league_ziggs_q_air{h}\"")), "q_air{h}");
            }
        }
    }

    #[test]
    fn hexplode_below_the_line_only() {
        assert!(hexplodable(&p(), 600, 2000));
        assert!(hexplodable(&p(), 1, 2000));
        assert!(!hexplodable(&p(), 601, 2000));
        assert!(!hexplodable(&p(), 0, 2000));
    }

    #[test]
    fn reach() {
        assert!(in_reach(&p(), (100000, 100000), (200000, 100000)));
        assert!(!in_reach(&p(), (100000, 100000), (200001, 100000)));
        // sieging from his attack range: 55000 + both radii (10000 each) from the tower's centre
        assert!(in_reach(&p(), (100000, 100000), (175000, 100000)));
    }

    #[test]
    fn fuse_on_towers() {
        assert_eq!(tower_hit(&p(), 100), 175);
        assert_eq!(tower_hit(&p(), 0), 0);
    }

    #[test]
    fn the_blast_pushes_from_its_centre() {
        // League: enemies "knocked back ... up to 500 units away from the center of the explosion", Ziggs to 825
        let c = (100_000.0, 100_000.0);
        // 10000 right of the centre: out to 50000 right of it
        assert_eq!(thrown_to(c, (110_000.0, 100_000.0), 50_000.0, (0.0, 1.0)), Some((150_000.0, 100_000.0)));
        // left of it: thrown left - toward Ziggs when he stands on that side
        assert_eq!(thrown_to(c, (80_000.0, 100_000.0), 50_000.0, (0.0, 1.0)), Some((50_000.0, 100_000.0)));
        // already as far as the blast throws: not moved
        assert_eq!(thrown_to(c, (150_000.0, 100_000.0), 50_000.0, (0.0, 1.0)), None);
        // right on the centre: the spare direction
        assert_eq!(thrown_to(c, c, 50_000.0, (0.0, 2.0)), Some((100_000.0, 150_000.0)));
        // never off the map
        assert_eq!(thrown_to((10_000.0, 100_000.0), (5_000.0, 100_000.0), 82_500.0, (0.0, 1.0)), Some((0.0, 100_000.0)));
    }

    #[test]
    fn a_diver_gets_the_satchel_between_them() {
        let s = scene(vec![foe(7, 518_000.0, 90.0)]);
        let t = decide(&p(), &s).expect("a champion 18000 away");
        assert_eq!(t.why, Why::Escape(7));
        assert_eq!(t.centre, (509_000.0, 500_000.0), "the middle of the two");
        // he flies left, away from the diver, to 82500 from the centre; the diver right, to 50000 from it
        assert_eq!(thrown_to(t.centre, s.me, 82_500.0, (0.0, 0.0)), Some((426_500.0, 500_000.0)));
        assert_eq!(thrown_to(t.centre, s.foes[0].at, 50_000.0, (0.0, 0.0)), Some((559_000.0, 500_000.0)));
        assert_eq!(t.flight, 3);
        // the trigger is edge to edge (the main pack's RandomTarget w_trig): 22000 + both bodies = 42000 centre to centre
        let edge = decide(&p(), &scene(vec![foe(7, 541_000.0, 90.0)])).expect("41000 centre to centre");
        assert_eq!((edge.why, edge.centre), (Why::Escape(7), (510_000.0, 500_000.0)), "w_gap from him");
        assert!(dist(edge.centre, (541_000.0, 500_000.0)) <= p().w_r as f64 + BODY, "the diver is in the blast");
        assert!(dist(edge.centre, s.me) <= p().w_r as f64 + BODY, "so is Ziggs");
        // a diver farther than that: nothing (he is neither low nor out of reach)
        assert_eq!(decide(&p(), &scene(vec![foe(7, 543_000.0, 90.0)])), None);
        // the satchel never lands farther than w_gap from him
        assert_eq!(escape_centre(&p(), (0.0, 0.0), (40_000.0, 0.0)), (10_000.0, 0.0));
    }

    #[test]
    fn he_is_not_thrown_under_a_tower_or_into_a_crowd() {
        let mut s = scene(vec![foe(7, 518_000.0, 90.0)]);
        s.towers.push(Tower { id: 3, at: (400_000.0, 500_000.0), hp: 2000, max_hp: 2000 });
        assert_eq!(decide(&p(), &s), None, "the landing 26500 from an enemy tower");
        let s = scene(vec![foe(7, 518_000.0, 90.0), foe(8, 430_000.0, 90.0), foe(9, 440_000.0, 90.0)]);
        assert_eq!(decide(&p(), &s), None, "two more enemies where he would land");
    }

    #[test]
    fn a_low_tower_in_reach_is_blown_up() {
        let mut s = scene(Vec::new());
        s.towers.push(Tower { id: 3, at: (580_000.0, 500_000.0), hp: 500, max_hp: 2000 });
        let t = decide(&p(), &s).expect("a tower at 25%");
        assert_eq!((t.why, t.centre), (Why::Tower(3), (580_000.0, 500_000.0)));
        assert!(dist(t.centre, s.me) > p().w_r as f64 + BODY, "Ziggs is not in that blast");
        s.towers[0].hp = 700;
        assert_eq!(decide(&p(), &s), None, "35%: not yet");
    }

    #[test]
    fn a_wounded_champion_out_of_reach_is_knocked_back() {
        // 80000 away at 30% health, standing: the satchel 15000 behind him, he ends 45000 from Ziggs
        let s = scene(vec![foe(7, 580_000.0, 30.0)]);
        let t = decide(&p(), &s).expect("a wounded champion out of reach");
        assert_eq!(t.why, Why::Catch(7));
        assert_eq!(t.centre, (595_000.0, 500_000.0));
        assert_eq!(thrown_to(t.centre, s.foes[0].at, 50_000.0, (0.0, 0.0)), Some((545_000.0, 500_000.0)));
        assert!(dist(s.me, t.centre) > p().w_r as f64 + BODY, "Ziggs is not in that blast");
        // walking away at 300 a tick from 74000: it lands behind where he WILL be
        let mut run = s.clone();
        run.foes[0].at = (574_000.0, 500_000.0);
        run.foes[0].vel = (300.0, 0.0);
        let t2 = decide(&p(), &run).expect("still in reach when it lands");
        let lands = p().e_rel + t2.flight;
        let then = 574_000.0 + 300.0 * lands as f64;
        assert!(t2.centre.0 > then + 7_000.0, "behind him at the landing: {} vs {then}", t2.centre.0);
        // running away faster: out of the catch's reach by the landing - no throw
        run.foes[0].vel = (600.0, 0.0);
        assert_eq!(decide(&p(), &run), None);
        // healthy, inside his attack reach, too far, under his tower, more of them than of us, or Ziggs himself hurt: no
        assert_eq!(decide(&p(), &scene(vec![foe(7, 580_000.0, 60.0)])), None);
        assert_eq!(decide(&p(), &scene(vec![foe(7, 570_000.0, 30.0)])), None);
        assert_eq!(decide(&p(), &scene(vec![foe(7, 592_000.0, 30.0)])), None);
        let mut tower = s.clone();
        tower.towers.push(Tower { id: 3, at: (600_000.0, 500_000.0), hp: 2000, max_hp: 2000 });
        assert_eq!(decide(&p(), &tower), None);
        assert_eq!(decide(&p(), &scene(vec![foe(7, 580_000.0, 30.0), foe(8, 595_000.0, 90.0)])), None);
        let mut with_ally = scene(vec![foe(7, 580_000.0, 30.0), foe(8, 595_000.0, 90.0)]);
        with_ally.allies.push((565_000.0, 520_000.0));
        assert!(decide(&p(), &with_ally).is_some(), "two of them, two of us");
        assert_eq!(decide(&p(), &Scene { hp: 30.0, ..s.clone() }), None);
        // the lowest one of two
        let two = scene(vec![foe(7, 580_000.0, 35.0), foe(8, 420_000.0, 20.0)]);
        assert_eq!(decide(&p(), &two).map(|t| t.why), Some(Why::Catch(8)));
    }

    #[test]
    fn a_cast_takes_a_third_off_short_fuse() {
        assert_eq!(fuse_cut(|n| n == "league_ziggs_p_a" || n == "league_ziggs_p_c"), Some("p_c"));
        assert_eq!(fuse_cut(|n| n == "league_ziggs_p_a"), Some("p_a"));
        assert_eq!(fuse_cut(|_| false), None);
    }

    #[test]
    fn the_bomb_bounces_on_along_the_throw() {
        // League: 850 thrown, 1400 with both bounces: the first 40% of the throw, the second 60% of the first
        let (l2, l3) = bounces(&p(), (100_000.0, 100_000.0), (185_000.0, 100_000.0)).unwrap();
        assert_eq!(l2, (219_000.0, 100_000.0));
        assert!((l3.0 - 239_400.0).abs() < 1e-6 && l3.1 == 100_000.0, "{l3:?}");
        assert!((dist((100_000.0, 100_000.0), l3) / 85_000.0 - 1.64).abs() < 1e-9, "850 -> 1394");
        // a diagonal throw keeps its line; never off the map; thrown at his own feet: no bounce
        let (d2, _) = bounces(&p(), (0.0, 0.0), (30_000.0, 40_000.0)).unwrap();
        assert!((d2.0 - 42_000.0).abs() < 1e-6 && (d2.1 - 56_000.0).abs() < 1e-6, "{d2:?}");
        let (e2, e3) = bounces(&p(), (900_000.0, 500_000.0), (950_000.0, 500_000.0)).unwrap();
        assert_eq!((e2.0, e3.0), (MAP, MAP));
        assert_eq!(bounces(&p(), (1.0, 1.0), (1.0, 1.0)), None);
    }

    #[test]
    fn the_stamps_are_the_main_packs() {
        // build_ziggs.air_heights with the kit's q_t / q_h / q_step (Python rounds half to even)
        assert_eq!(air_heights(&p(), 2), vec![(3, 4), (6, 6), (9, 8), (12, 10), (15, 10), (18, 10), (21, 8), (24, 6), (27, 4)]);
        assert_eq!(air_heights(&p(), 3), vec![(3, 2), (6, 4), (9, 4), (12, 6), (15, 6), (18, 6), (21, 4), (24, 4), (27, 2)]);
    }
}
