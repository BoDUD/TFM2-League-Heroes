//! 雷克塞附加包（用户 2026-10-17：「方案可以」，做附加包）。主包保持纯数据；`mod.override_info` 把主包的雷克塞换成 `override/` 里的
//! 副本（`make_override.py` 用 tools/kit/build_reksai.py 的 `native=1` 生成：被动换成本包的 `league_reksai:fury`，数据里的守望不再
//! 自己给 R 上膛（只由本包按真实血量上膛），普攻、技能2、大招的说明开头加【附加包】），本包补数据做不到的三件事：
//!
//! - **遁地整身换形态**（`view.rs`，游戏 0.6.4 起的 Windows 版）：身边没有敌人、正在赶路时，她钻进地底（buff `league_reksai_burrow`，移速
//!   +`BURROW_MS`%），站着、走着都是地上只露鳍冠和背的土包（图里的 `b_idle` / `b_run`），并按怒气回复生命（英雄联盟：遁地时消耗
//!   怒气回血）；敌人一靠近就破土。
//! - **挖掘隧道**：她每次 W 钻地，起点和破土的落点连成一条隧道（最多 `MAX_TUNNELS` 条，即 8 个入口，最旧的先塌），入口一直在地上
//!   （画面 `league_reksai_e_tunnel`）。敌方英雄站在入口上 `BREAK_T` tick 就把整条踩塌（`league_reksai_e_break`）。她走到入口旁时：
//!   残血被追就钻进去从另一头出来；不在战斗中、另一头附近有敌方英雄就钻过去突袭（每条隧道 `TUNNEL_CD` tick 才能再用）。钻的时候
//!   她被放逐（不可选取、看不见），按 `TRAVEL_SPEED` 在地下走完才从另一头冒出来。0.1.2：入口播她钻进地里的画面
//!   （`league_reksai_t_dig`，她自己图里的帧，往左走用镜像的 `_t_dig_l`），出口在放逐结束前 `UP_T` tick 把她放过去、播破土而出
//!   （`_t_up` / `_t_up_l`），播完才现身——放逐的总时长不变（原来钻地道时她直接消失、在另一头凭空出现）。
//! - **虚空猛冲按真实血量**：数据只知道「被我方打过的英雄」，副本的大招只等本包的 `league_reksai_r_ok`：被她标记为猎物（主包数据
//!   打中英雄时挂的 `league_reksai_r_mark`，本包记 `prey_t` tick）的敌方英雄里，有一个在大招范围内、看得见，而且 R 打得死它（按它的
//!   最大生命和护甲算伤害）、或它剩 `R_LOW_PCT`% 以下、或它被硬控着且剩 `R_CC_PCT`% 以下，才上膛（打得死的先、再残血、再被控）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_reksai.log`，每次启动游戏重写，上一次的留在 .prev.log：`FORM`（模拟里
//! 钻地 / 破土、画面里换形态）、`HEAL`（遁地回血）、`TUNNEL`（挖成、踩塌、钻过去）、`RARM`（为哪个猎物上膛、为什么：血量和估算伤害）、
//! `RFIRE`（大招放出时猎物的血量），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_reksai";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 遁地形态（本包挂的 buff；view.rs 照它换画面）。
pub const BURROW: &str = "league_reksai_burrow";
/// 主包数据的怒气层、W 的起落信号、猎物标记、大招上膛和潜地。
pub const FURY: [&str; 4] = ["league_reksai_f1", "league_reksai_f2", "league_reksai_f3", "league_reksai_f4"];
pub const W_GO: &str = "league_reksai_w_go";
pub const W_LAND: &str = "league_reksai_w_land";
pub const PREY: &str = "league_reksai_r_mark";
pub const R_OK: &str = "league_reksai_r_ok";
pub const R_HID: &str = "league_reksai_r_hid";
/// 遁地：加多少移速；身边多远内有敌方英雄（看得见的）、或任何敌方单位就不钻；连续赶路多少 tick 才钻。
pub const BURROW_MS: i32 = 20;
pub const SAFE_R: f64 = 60_000.0;
pub const FOE_R: f64 = 34_000.0;
pub const BURROW_AFTER: usize = 30;
/// 隧道：最多几条；起落点至少隔多远才算一条；走到入口多近能钻；敌人站在入口多近、多久就踩塌；地下走多快；每条的冷却；入口
/// 画面每隔几 tick 重播一次（e_tunnel 一轮的长度）。
pub const MAX_TUNNELS: usize = 4;
pub const TUNNEL_MIN: f64 = 15_000.0;
pub const ENTER_R: f64 = 9_000.0;
pub const STEP_R: f64 = 6_000.0;
pub const BREAK_T: usize = 90;
pub const TRAVEL_SPEED: f64 = 5_000.0;
/// 出口破土画面的长度（图里 `t_up` 333 ms）：她在放逐结束前这么多 tick 被放到出口、画面播完才现身。
pub const UP_T: usize = 20;

/// 隧道里走多久（放逐总 tick）和几 tick 后到出口（之后播破土画面）。
pub fn tunnel_times(dist: f64) -> (usize, usize) {
    let total = ((dist / TRAVEL_SPEED).ceil() as usize).max(UP_T + 10);
    (total, total - UP_T)
}

/// 钻入 / 破土画面的名字：往左走用镜像的（客户端不镜像画面）。
pub fn tunnel_view(up: bool, left: bool) -> &'static str {
    match (up, left) {
        (false, false) => "t_dig",
        (false, true) => "t_dig_l",
        (true, false) => "t_up",
        (true, true) => "t_up_l",
    }
}
pub const TUNNEL_CD: usize = 360;
pub const SHOW_EVERY: usize = 24;
/// 钻隧道的时机：残血线；被追 = 这么近有敌方英雄；另一头要多空；突袭 = 另一头这么近有敌方英雄、自己身边这么远内没有。
pub const ESCAPE_HP: usize = 35;
pub const CHASED_R: f64 = 45_000.0;
pub const CLEAR_R: f64 = 50_000.0;
pub const ENGAGE_R: f64 = 35_000.0;
pub const ENGAGE_HP: usize = 50;
/// 虚空猛冲上膛：猎物血量在这个百分比以下就算残血；被硬控时在这个百分比以下就打（用户 2026-10-17：「附加包的 R 太保守了，
/// 放宽一点（不只等能打死的）」——只等打得死的，两局里一次都没放）。
pub const R_LOW_PCT: usize = 40;
pub const R_CC_PCT: usize = 70;
/// 算「被控」的硬控（游戏 0.6.4 把施法动作也记成一种控制 Animation，不能用 cc_count() > 0）。
pub const HARD_CC: [CcKindV1; 7] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::ForceMove,
];

fn rk(x: &str) -> String {
    format!("league_reksai_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_REKSAI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_reksai.log");
        }
    }
    PathBuf::from("league_reksai.log")
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

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 满怒时遁地回血：w_heal + w_heal_r% 攻击力，每层怒气四分之一。
    pub w_heal: usize,
    pub w_heal_r: usize,
    /// 虚空猛冲：r_dmg + r_ratio% 攻击力 + 目标最大生命 r_hp%（物理），范围 r_range。
    pub r_dmg: usize,
    pub r_ratio: usize,
    pub r_hp: usize,
    pub r_range: usize,
    /// 一个标记记多久（英雄联盟 5 秒）。
    pub prey_t: usize,
    /// W 钻在地下的帧数（w_go 的长度；记起点用不到，日志里写）。
    pub w_dig: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { w_heal: 50, w_heal_r: 50, r_dmg: 120, r_ratio: 100, r_hp: 15, r_range: 70_000, prey_t: 300, w_dig: 28 }
    }
}

/// `{"w_heal":50,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "w_heal" => p.w_heal = v,
            "w_heal_r" => p.w_heal_r = v,
            "r_dmg" => p.r_dmg = v,
            "r_ratio" => p.r_ratio = v,
            "r_hp" => p.r_hp = v,
            "r_range" => p.r_range = v,
            "prey_t" => p.prey_t = v,
            "w_dig" => p.w_dig = v,
            _ => {}
        }
    }
    p
}

static SHARED: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

fn shared() -> Params {
    SHARED.lock().unwrap_or_else(|e| e.into_inner()).clone()
}

// ===================== 计算（单元测试用） =====================

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn fpos(p: (u64, u64)) -> Pt {
    (p.0 as f64, p.1 as f64)
}

fn pos_input(p: Pt) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

/// 遁地时回多少血：怒气 k 层（0-4）。
pub fn fury_heal(p: &Params, attack: usize, k: usize) -> usize {
    (p.w_heal + p.w_heal_r * attack / 100) * k.min(4) / 4
}

/// 虚空猛冲打到这个目标身上的伤害（物理：按护甲减）。
pub fn void_rush(p: &Params, attack: usize, target_max_hp: usize, target_def: usize) -> usize {
    let raw = p.r_dmg + p.r_ratio * attack / 100 + p.r_hp * target_max_hp / 100;
    raw * 100 / (100 + target_def)
}

/// 一个猎物该不该让她放大招：这一下打得死（kill）、残血（low：R_LOW_PCT% 以下）、被硬控而且不满血（cc：R_CC_PCT% 以下）。
pub fn arm_reason(hp: usize, max: usize, dmg: usize, in_cc: bool) -> Option<&'static str> {
    if hp <= dmg {
        Some("kill")
    } else if hp * 100 <= R_LOW_PCT * max {
        Some("low")
    } else if in_cc && hp * 100 <= R_CC_PCT * max {
        Some("cc")
    } else {
        None
    }
}

/// 两个猎物（原因, 血量, 最大生命）里前一个是不是更该打：打得死的先，再残血，再被控；同一档挑血量比例低的。
pub fn better(a: (&str, usize, usize), b: (&str, usize, usize)) -> bool {
    let rank = |w: &str| match w {
        "kill" => 0,
        "low" => 1,
        _ => 2,
    };
    let (ra, rb) = (rank(a.0), rank(b.0));
    ra < rb || (ra == rb && a.1 * b.2.max(1) < b.1 * a.2.max(1))
}

/// 一条隧道：两个入口、每个入口上敌方英雄连续站了多少 tick、什么时候能再钻。
#[derive(Clone, Debug, PartialEq)]
pub struct Tunnel {
    pub ends: [Pt; 2],
    pub stood: [usize; 2],
    pub ready_at: usize,
    pub born: usize,
}

/// 新隧道加进去，超过上限就把最旧的挤掉（返回被挤掉的）。
pub fn add_tunnel(list: &mut Vec<Tunnel>, t: Tunnel) -> Option<Tunnel> {
    list.push(t);
    (list.len() > MAX_TUNNELS).then(|| list.remove(0))
}

/// 这一 tick 每个入口上有没有敌方英雄 -> 更新计数，返回被踩塌的隧道的序号。
pub fn trample(list: &mut [Tunnel], foes: &[Pt]) -> Option<usize> {
    for (i, t) in list.iter_mut().enumerate() {
        for e in 0..2 {
            if foes.iter().any(|f| dist(*f, t.ends[e]) <= STEP_R) {
                t.stood[e] += 1;
                if t.stood[e] >= BREAK_T {
                    return Some(i);
                }
            } else {
                t.stood[e] = 0;
            }
        }
    }
    None
}

/// 她该不该钻这条隧道（她在入口 `near` 旁），返回原因。
pub fn should_travel(me: Pt, hp_pct: usize, far: Pt, foes: &[Pt]) -> Option<&'static str> {
    let close = |p: Pt, r: f64| foes.iter().any(|f| dist(*f, p) <= r);
    if hp_pct < ESCAPE_HP && close(me, CHASED_R) && !close(far, CLEAR_R) {
        return Some("escape");
    }
    if hp_pct >= ENGAGE_HP && !close(me, CLEAR_R) && close(far, ENGAGE_R) && dist(me, far) > 30_000.0 {
        return Some("engage");
    }
    None
}

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    buffs(sim, id).iter().any(|b| b.name() == name)
}

fn hard_cc(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
    })
}

// ===================== 被动：遁地、隧道、虚空猛冲 =====================

#[derive(Clone, Default)]
struct Fury {
    /// 上一 tick 的位置、连续在赶路（没敌人）的 tick 数、是不是在地底。
    last: Option<Pt>,
    moving: usize,
    burrowed: bool,
    /// W：起点（w_go 出现时）和上一 tick 的信号。
    w_from: Option<Pt>,
    w_go: bool,
    w_land: bool,
    tunnels: Vec<Tunnel>,
    /// 正在隧道里：出口、到出口的 tick、放逐结束的 tick、是不是往左走。
    travel: Option<(Pt, usize, usize, bool)>,
    /// 猎物：敌方英雄号 -> 标记记到哪个 tick。
    prey: HashMap<usize, usize>,
    r_armed_for: Option<usize>,
    r_hid: bool,
}

struct Seen {
    team: usize,
    me: Pt,
    hp_pct: usize,
    attack: usize,
    foes_vis: Vec<(usize, Pt)>,
    any_foe_near: bool,
}

impl Fury {
    fn look(&self, sim: &StableSim<'_>, me: usize) -> Option<Seen> {
        let e = sim.get_entity(me)?;
        let (team, at) = (e.team(), fpos(e.pos()));
        let (hp, max) = e.hp();
        let mut foes_vis = Vec::new();
        let mut any_foe_near = false;
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() || u.is_tower() {
                continue;
            }
            let p = fpos(u.pos());
            if u.is_champion() && sim.is_visible(team, u.id()) {
                foes_vis.push((u.id(), p));
            }
            if dist(p, at) <= FOE_R && u.is_targetable() {
                any_foe_near = true;
            }
        }
        Some(Seen { team, me: at, hp_pct: if max > 0 { hp * 100 / max } else { 100 }, attack: e.stat().attack, foes_vis, any_foe_near })
    }

    /// 脱离战斗赶路时钻进地底，有敌人靠近就破土。
    fn burrow(&mut self, sim: &mut StableSim<'_>, me: usize, s: &Seen, p: &Params) {
        let moved = self.last.is_some_and(|l| dist(l, s.me) > 50.0);
        let safe = !s.any_foe_near && !s.foes_vis.iter().any(|(_, f)| dist(*f, s.me) <= SAFE_R) && self.travel.is_none()
            && !has_buff(sim, me, W_GO) && !has_buff(sim, me, R_HID) && !hard_cc(sim, me);
        self.moving = if safe && moved { self.moving + 1 } else if safe { self.moving } else { 0 };
        let want = safe && (self.burrowed || self.moving >= BURROW_AFTER);
        if want && !self.burrowed {
            let mut b = BuffV1::named(BURROW);
            b.move_speed_mult = BURROW_MS;
            sim.add_buff(me, &b);
            sim.play_view_effect(&rk("w_dig"), me, &pos_input(s.me), 0, 0, 0);
            sim.play_sfx(&rk("w"), me, &pos_input(s.me));
            let k = (1..=4).rev().find(|k| has_buff(sim, me, FURY[k - 1])).unwrap_or(0);
            if k > 0 {
                let amount = fury_heal(p, s.attack, k);
                sim.heal(me, me, amount);
                for f in FURY {
                    sim.entity_remove_buff(me, f);
                }
                sim.play_view_effect(&rk("w_heal"), me, &InputTargetV1::target(me), 0, 0, 0);
                if let Some(n) = counted("heal") {
                    wlog(format!("{} HEAL {k} Fury -> +{amount} hp (attack {}) #{n}", head(sim, me), s.attack));
                }
            }
            if let Some(n) = counted("form") {
                wlog(format!("{} FORM sim: BURROWED after {} ticks on the move, hp {}% #{n}", head(sim, me), self.moving, s.hp_pct));
            }
        } else if !want && self.burrowed {
            sim.entity_remove_buff(me, BURROW);
            sim.play_view_effect(&rk("q2_cast"), me, &pos_input(s.me), 0, 0, 0);
            if let Some(n) = counted("form") {
                let why = if s.any_foe_near { "an enemy near" } else if s.foes_vis.iter().any(|(_, f)| dist(*f, s.me) <= SAFE_R) {
                    "an enemy champion in sight" } else { "an action" };
                wlog(format!("{} FORM sim: up again ({why}) #{n}", head(sim, me)));
            }
        }
        self.burrowed = want;
    }

    /// W 的起落 -> 隧道；入口画面；踩塌；钻过去。
    fn tunnels(&mut self, sim: &mut StableSim<'_>, me: usize, s: &Seen) {
        let now = sim.tick();
        let go = has_buff(sim, me, W_GO);
        if go && !self.w_go {
            self.w_from = Some(s.me);
        }
        self.w_go = go;
        let land = has_buff(sim, me, W_LAND);
        if land && !self.w_land {
            if let Some(from) = self.w_from.take() {
                if dist(from, s.me) >= TUNNEL_MIN {
                    let t = Tunnel { ends: [from, s.me], stood: [0, 0], ready_at: now + TUNNEL_CD, born: now };
                    let old = add_tunnel(&mut self.tunnels, t);
                    if let Some(old) = &old {
                        for e in old.ends {
                            sim.play_view_effect(&rk("e_break"), me, &pos_input(e), 0, 0, 0);
                        }
                    }
                    if let Some(n) = counted("tunnel") {
                        wlog(format!("{} TUNNEL dug {:.0} long ({} now{}) #{n}", head(sim, me), dist(from, s.me), self.tunnels.len(),
                            if old.is_some() { ", the oldest caved in" } else { "" }));
                    }
                }
            }
        }
        self.w_land = land;
        // the entrances on the ground, a fresh picture every loop
        if now % SHOW_EVERY == 0 {
            for t in &self.tunnels {
                for e in t.ends {
                    sim.play_view_effect(&rk("e_tunnel"), me, &pos_input(e), 0, 0, 0);
                }
            }
        }
        let foes: Vec<Pt> = s.foes_vis.iter().map(|(_, p)| *p).collect();
        if let Some(i) = trample(&mut self.tunnels, &foes) {
            let t = self.tunnels.remove(i);
            for e in t.ends {
                sim.play_view_effect(&rk("e_break"), me, &pos_input(e), 0, 0, 0);
            }
            if let Some(n) = counted("tunnel") {
                wlog(format!("{} TUNNEL trampled by an enemy champion after {BREAK_T} ticks ({} left) #{n}", head(sim, me),
                    self.tunnels.len()));
            }
        }
        // under way: out at the far end
        if let Some((exit, at, until, left)) = self.travel {
            if now >= at {
                sim.entity_set_pos(me, exit.0.round() as u64, exit.1.round() as u64);
                sim.play_view_effect(&rk("q2_cast"), me, &pos_input(exit), 0, 0, 0);
                sim.play_view_effect(&rk(tunnel_view(true, left)), me, &pos_input(exit), 0, 0, 0);
                sim.play_sfx(&rk("w_up"), me, &pos_input(exit));
                self.travel = Some((exit, usize::MAX, until, left));    // out once
            }
            if now >= until {
                self.travel = None;
            }
            return;
        }
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        if !alive || hard_cc(sim, me) || has_buff(sim, me, W_GO) || has_buff(sim, me, R_HID) {
            return;
        }
        for t in self.tunnels.iter_mut() {
            if now < t.ready_at {
                continue;
            }
            for e in 0..2 {
                if dist(t.ends[e], s.me) > ENTER_R {
                    continue;
                }
                let far = t.ends[1 - e];
                let Some(why) = should_travel(s.me, s.hp_pct, far, &foes) else { continue };
                let (ticks, out_at) = tunnel_times(dist(s.me, far));
                let left = far.0 < s.me.0;
                sim.play_view_effect(&rk("w_dig"), me, &pos_input(s.me), 0, 0, 0);
                sim.play_view_effect(&rk(tunnel_view(false, left)), me, &pos_input(s.me), 0, 0, 0);
                sim.play_sfx(&rk("w"), me, &pos_input(s.me));
                sim.entity_banish(me, me, ticks, "", "");
                t.ready_at = now + TUNNEL_CD;
                self.travel = Some((far, now + out_at, now + ticks, left));
                if let Some(n) = counted("travel") {
                    wlog(format!("{} TUNNEL travel ({why}): {:.0} under the ground in {ticks} ticks, hp {}% #{n}", head(sim, me),
                        dist(s.me, far), s.hp_pct));
                }
                return;
            }
        }
    }

    /// 猎物的记忆和大招的上膛：记着的猎物里，打得死的、残血的、被硬控而不满血的，挑最该打的那个上膛。
    fn void_rush(&mut self, sim: &mut StableSim<'_>, me: usize, s: &Seen, p: &Params) {
        let now = sim.tick();
        let mut best: Option<(usize, &'static str, usize, usize, usize)> = None;   // (id, why, hp, max, damage)
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == s.team || !u.is_alive() || !u.is_champion() {
                continue;
            }
            let id = u.id();
            if (0..u.buff_count()).filter_map(|k| u.buff_at(k)).any(|b| b.name() == PREY) {
                self.prey.insert(id, now + p.prey_t);
            }
            if self.prey.get(&id).is_none_or(|&until| until < now) {
                continue;
            }
            if dist(fpos(u.pos()), s.me) > p.r_range as f64 || !sim.is_visible(s.team, id) {
                continue;
            }
            let (hp, max) = u.hp();
            let dmg = void_rush(p, s.attack, max, u.stat().defence);
            let Some(why) = arm_reason(hp, max, dmg, hard_cc(sim, id)) else { continue };
            if best.is_none_or(|b| better((why, hp, max), (b.1, b.2, b.3))) {
                best = Some((id, why, hp, max, dmg));
            }
        }
        self.prey.retain(|_, until| *until >= now);
        if let Some((id, why, hp, max, dmg)) = best {
            sim.entity_stack_buff(me, &BuffV1::timed(R_OK, 3), 1, true);
            if self.r_armed_for != Some(id) {
                if let Some(n) = counted("rarm") {
                    wlog(format!("{} RARM ({why}) for {}: hp {hp}/{max}, Void Rush {dmg} #{n}", head(sim, me), who(sim, id)));
                }
            }
            self.r_armed_for = Some(id);
        } else {
            self.r_armed_for = None;
        }
        let hid = has_buff(sim, me, R_HID);
        if hid && !self.r_hid {
            if let Some(n) = counted("rfire") {
                let list: Vec<String> = self.prey.keys().filter_map(|&id| sim.get_entity(id).map(|e| {
                    let (hp, max) = e.hp();
                    format!("{} {hp}/{max}", who(sim, id))
                })).collect();
                wlog(format!("{} RFIRE Void Rush; prey: {} #{n}", head(sim, me), list.join(", ")));
            }
        }
        self.r_hid = hid;
    }
}

impl StablePassive for Fury {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let p = parse_params(params_json);
        let mut s = SHARED.lock().unwrap_or_else(|e| e.into_inner());
        if *s != p {
            wlog(format!("params {params_json} -> {p:?}"));
            *s = p;
        }
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.last = None;
        self.moving = 0;
        self.burrowed = false;
        self.w_from = None;
        self.travel = None;
        self.r_armed_for = None;
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN {} ({} tunnels kept) #{k}", head(sim, entity), who(sim, entity), self.tunnels.len()));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let p = shared();
        let Some(s) = self.look(sim, me) else { return };
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        self.tunnels(sim, me, &s);
        if alive {
            self.burrow(sim, me, &s, &p);
            self.void_rush(sim, me, &s, &p);
        } else if self.burrowed {
            self.burrowed = false;
        }
        self.last = Some(s.me);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Rek'Sai: the burrowed body, tunnels, Void Rush by real health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:fury"), Fury::default());
    host.log(LogLevel::Info, "league_reksai loaded (the burrowed body, tunnels, Void Rush by real health: a kill, a low one or one held).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"r_hp":20,"junk":7,"w_heal":60}"#);
        assert_eq!((p.r_hp, p.w_heal, p.r_dmg), (20, 60, 120));
    }

    #[test]
    fn the_copy_carries_the_default_params() {
        let copy = include_str!("../override/league_reksai.data_champion");
        let at = copy.find("\"passive_ref\": \"league_reksai:fury\"").expect("no league_reksai:fury passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("w_heal", d.w_heal), ("w_heal_r", d.w_heal_r), ("r_dmg", d.r_dmg), ("r_ratio", d.r_ratio),
                       ("r_hp", d.r_hp), ("r_range", d.r_range), ("prey_t", d.prey_t), ("w_dig", d.w_dig)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for flag in [W_GO, W_LAND, PREY, R_OK, R_HID] {
            assert!(copy.contains(&format!("\"{flag}\"")), "the copy does not use {flag}");
        }
        for f in FURY {
            assert!(copy.contains(&format!("\"{f}\"")), "the copy does not use {f}");
        }
    }

    #[test]
    fn fury_heals_a_quarter_a_point() {
        let p = Params::default();
        assert_eq!(fury_heal(&p, 100, 4), 100);
        assert_eq!(fury_heal(&p, 100, 2), 50);
        assert_eq!(fury_heal(&p, 100, 0), 0);
        assert_eq!(fury_heal(&p, 100, 9), 100);
    }

    #[test]
    fn void_rush_counts_max_health_and_armour() {
        let p = Params::default();
        // 120 + 100 + 15% of 2000 = 520, armour 30 -> 400
        assert_eq!(void_rush(&p, 100, 2000, 30), 400);
        assert_eq!(void_rush(&p, 100, 2000, 0), 520);
    }

    #[test]
    fn void_rush_waits_for_a_kill_a_low_one_or_one_held() {
        assert_eq!(arm_reason(300, 2000, 400, false), Some("kill"));
        assert_eq!(arm_reason(700, 2000, 400, false), Some("low")); // 35%
        assert_eq!(arm_reason(1300, 2000, 400, true), Some("cc")); // 65% and stunned
        assert_eq!(arm_reason(1300, 2000, 400, false), None); // 65%, free
        assert_eq!(arm_reason(1900, 2000, 400, true), None); // nearly full, even held
        assert!(better(("kill", 390, 2000), ("low", 100, 2000)));
        assert!(better(("low", 300, 2000), ("low", 700, 2000)));
        assert!(!better(("cc", 100, 2000), ("low", 700, 2000)));
    }

    #[test]
    fn the_oldest_tunnel_caves_in() {
        let mut l = Vec::new();
        for i in 0..MAX_TUNNELS {
            assert!(add_tunnel(&mut l, Tunnel { ends: [(0.0, 0.0), (1.0, i as f64)], stood: [0, 0], ready_at: 0, born: i }).is_none());
        }
        let gone = add_tunnel(&mut l, Tunnel { ends: [(0.0, 0.0), (9.0, 9.0)], stood: [0, 0], ready_at: 0, born: 99 });
        assert_eq!(gone.map(|t| t.born), Some(0));
        assert_eq!(l.len(), MAX_TUNNELS);
    }

    #[test]
    fn standing_on_an_entrance_tramples_it() {
        let mut l = vec![Tunnel { ends: [(0.0, 0.0), (100_000.0, 0.0)], stood: [0, 0], ready_at: 0, born: 0 }];
        for _ in 0..BREAK_T - 1 {
            assert_eq!(trample(&mut l, &[(1_000.0, 0.0)]), None);
        }
        assert_eq!(trample(&mut l, &[(1_000.0, 0.0)]), Some(0));
        let mut l = vec![Tunnel { ends: [(0.0, 0.0), (100_000.0, 0.0)], stood: [0, 0], ready_at: 0, born: 0 }];
        for _ in 0..BREAK_T * 2 {
            assert_eq!(trample(&mut l, &[(20_000.0, 0.0)]), None); // not on it
        }
    }

    #[test]
    fn the_tunnel_run_keeps_its_length_and_leaves_room_to_come_out() {
        let (total, out) = tunnel_times(50_000.0);
        assert_eq!((total, out), (30, 10));                 // 10 ticks of travel would be 10: UP_T + 10 at least
        let (total, out) = tunnel_times(200_000.0);
        assert_eq!((total, out), (40, 40 - UP_T));          // as long as before, out UP_T ticks before the end
        assert_eq!(tunnel_view(false, false), "t_dig");
        assert_eq!(tunnel_view(true, true), "t_up_l");
    }

    #[test]
    fn every_tunnel_picture_is_in_her_sheet_and_data() {
        let fanim = include_str!("../../../league/champions/league_reksai#anim.fanim");
        let data = include_str!("../../../league/champion/league_reksai.data_champion");
        for t in ["t_dig", "t_dig_l", "t_up", "t_up_l"] {
            for name in [t.to_string(), format!("hd_{t}")] {
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_reksai#anim.fanim");
            }
            assert!(data.contains(&format!("\"league_reksai_{t}\"")), "league_reksai_{t} has no view in the data");
        }
    }

    #[test]
    fn she_tunnels_to_escape_or_to_engage() {
        let me = (0.0, 0.0);
        let far = (80_000.0, 0.0);
        assert_eq!(should_travel(me, 20, far, &[(20_000.0, 0.0)]), Some("escape"));
        assert_eq!(should_travel(me, 20, far, &[(20_000.0, 0.0), (85_000.0, 0.0)]), None); // the far end is held
        assert_eq!(should_travel(me, 80, far, &[(95_000.0, 0.0)]), Some("engage"));
        assert_eq!(should_travel(me, 30, far, &[(95_000.0, 0.0)]), None); // too low to dive
        assert_eq!(should_travel(me, 80, far, &[(20_000.0, 0.0), (95_000.0, 0.0)]), None); // already fighting
        assert_eq!(should_travel(me, 80, far, &[]), None);
    }
}
