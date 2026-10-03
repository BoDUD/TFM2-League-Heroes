//! 盲僧 W 位移附加包 v1：手游式 W——直接冲到地上一个点，不用插眼。
//!
//! 主包的李青不能「摸眼」：R 身后没人时直接冲过目标（`RushMoveToBack`）落到他身后回旋踢，W 并进了 E、
//! 不冲刺。英雄联盟手游里李青的 W 不用插眼就能冲到一个点；`mod.override_info` 把主包的李青换成
//! `override/` 里的副本，加两处原生代码：
//!
//! - **回旋踢**（`insec`，换掉 R 第 7 tick 的 `RushMoveToBack`；R 第 17 tick 主包照常踢）——照高手的打法，把他踢回
//!   **自己队伍那边**：踢的方向朝他身边 `ALLY_R` 内己方英雄的重心，没有队友就朝最近的己方塔，都没有才踢回李青这边。
//!   李青**已经站在他背后**（和「背后」差不过 60°）就不 W，直接贴上去（`DIRECT_MIN`..`BEHIND`）摆正了踢；不在就 W 到他
//!   背后 `BEHIND`（墙里往近挪，还不行左右转 15°、30° 找落脚点）。从第 7 tick 到踢的那一刻**一路跟着他走**（`follow`：
//!   每 tick 按他当时的位置重算落点，每 tick 最多挪 `INSEC_SPEED`，不用强制位移——它算控制会打断 R），踢完就停。
//!   v1.4 以前只看李青站在哪边、绕到对面去踢：李青本来就在他背后时反而绕过去把他踢回敌方；跟随结束后还会把李青
//!   放回第 7 tick 的旧落点（踢完瞬移一下）。
//! - **W 逃跑 / 追击**（被动 `hop`，挂在 `passive_skill2` 上）：每 `AUTO_EVERY` tick 看一次（顺便记下
//!   英雄们在哪、算出每 tick 的速度），`HOP_CD` 一次，**只顺着 AI 自己要走的方向 W**：
//!   - 逃跑：血量低于 `LOW_HP`、`DANGER_R` 内有敌方英雄、**他自己正在往远离敌人的方向跑**——W 冲向
//!     他跑的方向左右 60° 内离敌人最远、路上没有墙的点（`HOP_MIN`..`HOP_RANGE`）；
//!   - 追击：敌方英雄血量低于 `CHASE_HP`、离他 `CHASE_MIN` 以外够得着、**那人正在跑开、李青正在追**——
//!     W 冲到他身前。
//!   AI 没在跑（站着打、往回走）就不 W（v1.2 以前满血时会突然冲向远处的残血敌人、残血时往反方向冲，
//!   冲完 AI 又走回去，看起来莫名其妙）。
//!
//! 冲的时候李青身上亮 W 的护盾光、播 W 的声音（只是画面，不给护盾），逃跑 / 追击时播跑步的动作
//! （`RUN_ANIM`，不借别的技能的动作；R 里绕后不加，他在放 R）。刚出手的
//! 普攻 / Q / E 之后 `AFTER_ATTACK` / `AFTER_SKILL` tick、R 之后 `AFTER_ULT` tick 内不 W（看冷却刚跳起来），
//! 免得把出手到一半的技能拉走打空。冲刺被韧性缩短时每 tick 补一段（`dash`）。墙用内置的 5v5 碰撞墙
//! （见 [`maps`]），别的地图（有单位站在 5v5 的墙里）不查墙。
//!
//! - **Q 的出手**（选手 AI `q`，只接管李青按 Q 的那一下）：主包的 Q 打任何敌方单位、第 16 tick 才发波、方向按下时就定了，
//!   模拟里三分之二的 Q 打空、对英雄只中 3%（小兵走开、野怪先死、英雄早走了）。照高手的打法：对英雄**往他走到的地方打**
//!   （按他的速度预判波飞到时的位置），路上被小兵、野怪挡住或预判后够不着就不放；**不拿 Q 打小兵**；野怪照打，快死的不打。
//!   不放时改成平 A（或走向）原来那个目标。R 里自带的 Q 不经过这里。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_leesin_hop.log`，每次启动游戏重写，上一次的留在 .prev.log。

pub mod maps;

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_leesin_hop";

/// W 绕后回旋踢：落在目标身后多远（同主包 `RushMoveToBack` 的 15000），落不了脚时最少多远，冲过去的速度。
pub const BEHIND: f64 = 15_000.0;
pub const BEHIND_MIN: f64 = 6_000.0;
const INSEC_SPEED: f64 = 8_000.0;
/// W 逃跑 / 追击：最远冲多远、冲的速度、至少冲多远才值得、多久一次。
pub const HOP_RANGE: f64 = 45_000.0;
const HOP_SPEED: f64 = 6_000.0;
pub const HOP_MIN: f64 = 18_000.0;
pub const HOP_CD: usize = 1_200;
/// 逃跑：血量比例和多近算被追。
pub const LOW_HP: f64 = 0.3;
pub const DANGER_R: f64 = 40_000.0;
/// 追击：敌人血量比例、至少离多远（近了直接打）、停在他身前多远。
pub const CHASE_HP: f64 = 0.25;
pub const CHASE_MIN: f64 = 25_000.0;
pub const CHASE_STOP: f64 = 8_000.0;
/// 被动每隔几 tick 看一次。
const AUTO_EVERY: usize = 6;
/// 在跑：两次看之间每 tick 至少走这么多（英雄走路每 tick 约 1000）；比 `MAX_WALK` 快的（冲刺、闪现）不算走路。
pub const MOVING: f64 = 300.0;
const MAX_WALK: f64 = 2_500.0;
/// 「朝着」：两个方向夹角的 cos 至少这么多（60°）。
pub const ALONG_COS: f64 = 0.5;
/// 逃跑 / 追击冲刺时播的动作。
const RUN_ANIM: &str = "run";
/// 刚出手的技能 / 普攻多久内不 W（免得把出手到一半的 Q 拉走打空）；R 后面主包还有飞踢、天音波连招，等更久。
pub const AFTER_SKILL: usize = 80;
pub const AFTER_ULT: usize = 90;
pub const AFTER_ATTACK: usize = 18;
/// W 冲刺的标记：时长是最晚到达时间；冲刺被韧性缩短时每 tick 补一段。
const DASH: &str = "league_leesin_hop_dash";
/// 刚补过一段强制位移（下一 tick 还没有位移就自己挪）。
const REDO: &str = "league_leesin_hop_redo";
/// 正在自己一步步挪（日志只记一次）。
const STEPPING: &str = "league_leesin_hop_stepping";
/// R 绕后时记下目标（`league_leesin_hop_target:<id>`），给踢的那一刻的检查用。
const TARGET: &str = "league_leesin_hop_target:";
/// 主包在 R 的第 17 tick 踢，绕后在第 7 tick：之后 10 tick。
const KICK_AFTER: usize = 10;
/// 回旋踢时跟着目标走（`league_leesin_hop_follow:<id>:<dx>:<dy>:<离他多远/100>`，dx/dy 是从他指向李青该站的那一侧
/// ×1000），到踢为止。
const FOLLOW: &str = "league_leesin_hop_follow:";
/// 回旋踢往哪边踢：他这么近的己方英雄（不含李青）算「队友那边」；没有就朝最近的己方塔。
pub const ALLY_R: f64 = 100_000.0;
/// 李青已经站在他背后（和「背后」差不过 60°）时不用 W，直接贴上去踢。
pub const BEHIND_COS: f64 = 0.5;
/// 直接踢时离他至少多远（不往后退，太近就停在这）。
pub const DIRECT_MIN: f64 = 9_000.0;
/// W 冲的时候李青身上的光和声音（主包 W 的护盾光，只是画面）。
const W_VIEW: &str = "league_leesin_shield";
const W_SFX: &str = "league_leesin_w_shield";
/// W 位移的冷却标记。
const CD: &str = "league_leesin_hop_cd";

const CELL: f64 = 32_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LEESIN_HOP_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_leesin_hop.log");
        }
    }
    PathBuf::from("league_leesin_hop.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
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
    format!("[{kind} m={} s={}] t={} leesin#{id}", m(o.match_id), m(o.set_index), sim.tick())
}

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

// ===================== 地图和几何 =====================

/// 5v5 的碰撞墙：`MOBA[y]` 第 x 个字符是 `#` 为墙，每格 32000；地图外也算墙。
pub fn is_wall(x: f64, y: f64) -> bool {
    if x < 0.0 || y < 0.0 {
        return true;
    }
    let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
    maps::MOBA.get(cy).and_then(|row| row.as_bytes().get(cx)).is_none_or(|c| *c == b'#')
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// a 到 b 的直线上没有墙吗（`walls` 关掉时总是没有）。
pub fn path_free(walls: bool, a: (f64, f64), b: (f64, f64)) -> bool {
    if !walls {
        return true;
    }
    let n = (dist(a, b) / 1000.0).ceil().max(1.0) as usize;
    (0..=n).all(|i| {
        let f = i as f64 / n as f64;
        !is_wall(a.0 + (b.0 - a.0) * f, a.1 + (b.1 - a.1) * f)
    })
}

fn unit_vec(v: (f64, f64)) -> Option<(f64, f64)> {
    let n = v.0.hypot(v.1);
    (n > 1.0).then(|| (v.0 / n, v.1 / n))
}

/// 回旋踢该把他踢向哪（从他出发的单位向量）和为什么：他身边 `ALLY_R` 内己方英雄的重心（`allies`，不含李青）；
/// 没有就最近的己方塔；都没有就踢回李青这边。
pub fn kick_dir(target: (f64, f64), lee: (f64, f64), allies: &[(f64, f64)], towers: &[(f64, f64)]) -> ((f64, f64), &'static str) {
    let near: Vec<&(f64, f64)> = allies.iter().filter(|a| dist(**a, target) <= ALLY_R).collect();
    if !near.is_empty() {
        let n = near.len() as f64;
        let c = (near.iter().map(|a| a.0).sum::<f64>() / n, near.iter().map(|a| a.1).sum::<f64>() / n);
        if let Some(d) = unit_vec((c.0 - target.0, c.1 - target.1)) {
            return (d, "allies");
        }
    }
    if let Some(t) = towers.iter().min_by(|a, b| dist(**a, target).total_cmp(&dist(**b, target))) {
        if let Some(d) = unit_vec((t.0 - target.0, t.1 - target.1)) {
            return (d, "tower");
        }
    }
    (unit_vec((lee.0 - target.0, lee.1 - target.1)).unwrap_or((1.0, 0.0)), "back")
}

/// 他背后（`back` = 踢的反方向）`BEHIND` 的落脚点和那一侧的方向：墙里就往近挪到 `BEHIND_MIN`，还不行左右各转
/// 15°、30° 找；要在地图上、李青冲过去的路上没有墙。
pub fn behind_spot(walls: bool, lee: (f64, f64), target: (f64, f64), back: (f64, f64)) -> Option<((f64, f64), (f64, f64))> {
    for deg in [0.0f64, 15.0, -15.0, 30.0, -30.0] {
        let (sn, cs) = deg.to_radians().sin_cos();
        let dir = (back.0 * cs - back.1 * sn, back.0 * sn + back.1 * cs);
        let mut b = BEHIND;
        while b >= BEHIND_MIN {
            let w = (target.0 + dir.0 * b, target.1 + dir.1 * b);
            let on_map = w.0 >= 0.0 && w.1 >= 0.0 && w.0 < 960_000.0 && w.1 < 960_000.0;
            if on_map && !(walls && is_wall(w.0, w.1)) && path_free(walls, lee, w) {
                return Some((w, dir));
            }
            b -= 1_500.0;
        }
    }
    None
}

/// 跟着走时的落点：他现在的位置往 `dir` 走 `keep`，墙里就往近挪，最近 `BEHIND_MIN`。
pub fn follow_spot(walls: bool, target: (f64, f64), dir: (f64, f64), keep: f64) -> (f64, f64) {
    let mut b = keep;
    while b >= BEHIND_MIN {
        let w = (target.0 + dir.0 * b, target.1 + dir.1 * b);
        let on_map = w.0 >= 0.0 && w.1 >= 0.0 && w.0 < 960_000.0 && w.1 < 960_000.0;
        if on_map && !(walls && is_wall(w.0, w.1)) {
            return w;
        }
        b -= 1_500.0;
    }
    (target.0 + dir.0 * keep.min(BEHIND_MIN), target.1 + dir.1 * keep.min(BEHIND_MIN))
}

/// 跟着走的标记：目标、方向（×1000 取整）、离他多远（÷100）。
pub fn follow_name(target: usize, dir: (f64, f64), keep: f64) -> String {
    format!(
        "{FOLLOW}{target}:{}:{}:{}",
        (dir.0 * 1000.0).round() as i64,
        (dir.1 * 1000.0).round() as i64,
        (keep / 100.0).round() as i64
    )
}

/// 从跟着走的标记读回 (目标, 方向, 离他多远)。
pub fn parse_follow(name: &str) -> Option<(usize, (f64, f64), f64)> {
    let mut it = name.strip_prefix(FOLLOW)?.split(':');
    let id = it.next()?.parse().ok()?;
    let dx = it.next()?.parse::<i64>().ok()? as f64 / 1000.0;
    let dy = it.next()?.parse::<i64>().ok()? as f64 / 1000.0;
    let keep = it.next()?.parse::<i64>().ok()? as f64 * 100.0;
    unit_vec((dx * 1000.0, dy * 1000.0)).map(|d| (id, d, keep))
}

fn follow_of(sim: &StableSim<'_>, lee: usize) -> Option<(usize, (f64, f64), f64)> {
    let me = sim.get_entity(lee)?;
    (0..me.buff_count()).filter_map(|i| me.buff_at(i)).find_map(|b| parse_follow(b.name()))
}

fn nearest(p: (f64, f64), foes: &[(f64, f64)]) -> f64 {
    foes.iter().map(|f| dist(p, *f)).fold(f64::INFINITY, f64::min)
}

/// a、b 两个方向夹角的 cos（有一个长度为 0 时为 0）。
fn cos(a: (f64, f64), b: (f64, f64)) -> f64 {
    let n = (a.0.hypot(a.1) * b.0.hypot(b.1)).max(1e-9);
    (a.0 * b.0 + a.1 * b.1) / n
}

/// 他正在跑开吗：速度 `v` 至少 `MOVING`，方向和「`from` 指向 `at`」差不过 60°。
pub fn moving_away(at: (f64, f64), v: (f64, f64), from: (f64, f64)) -> bool {
    v.0.hypot(v.1) >= MOVING && cos(v, (at.0 - from.0, at.1 - from.1)) >= ALONG_COS
}

/// 李青在追他吗：两人都在跑，他跑开（远离李青）、李青朝他跑。
pub fn chasing(lee: (f64, f64), v_lee: (f64, f64), him: (f64, f64), v_him: (f64, f64)) -> bool {
    moving_away(him, v_him, lee) && v_lee.0.hypot(v_lee.1) >= MOVING && cos(v_lee, (him.0 - lee.0, him.1 - lee.1)) >= ALONG_COS
}

/// 逃跑的落点：24 个方向里和他正在跑的方向 `heading` 差不过 60° 的，路上没墙、能冲 `HOP_MIN`..`HOP_RANGE`
/// 的点里离敌人最远的，比现在至少远 15000。
pub fn escape_spot(walls: bool, me: (f64, f64), foes: &[(f64, f64)], heading: (f64, f64)) -> Option<(f64, f64)> {
    let now = nearest(me, foes);
    (0..24)
        .filter_map(|k| {
            let a = k as f64 * std::f64::consts::TAU / 24.0;
            let dir = (a.cos(), a.sin());
            if cos(dir, heading) < ALONG_COS {
                return None;
            }
            let mut run = 0.0;
            while run + 500.0 <= HOP_RANGE {
                let p = (me.0 + dir.0 * (run + 500.0), me.1 + dir.1 * (run + 500.0));
                if p.0 < 0.0 || p.1 < 0.0 || p.0 >= 960_000.0 || p.1 >= 960_000.0 || (walls && is_wall(p.0, p.1)) {
                    break;
                }
                run += 500.0;
            }
            (run >= HOP_MIN).then(|| (me.0 + dir.0 * run, me.1 + dir.1 * run))
        })
        .map(|w| (nearest(w, foes), w))
        .filter(|(m, _)| *m >= now + 15_000.0)
        .max_by(|a, b| a.0.total_cmp(&b.0))
        .map(|(_, w)| w)
}

/// 追击的落点：他身前（李青这边）`CHASE_STOP`，要够得着（`HOP_MIN`..`HOP_RANGE`）、路上没墙。
pub fn chase_spot(walls: bool, me: (f64, f64), target: (f64, f64)) -> Option<(f64, f64)> {
    let d = dist(me, target);
    if d < CHASE_MIN {
        return None;
    }
    let reach = d - CHASE_STOP;
    let w = (me.0 + (target.0 - me.0) / d * reach, me.1 + (target.1 - me.1) / d * reach);
    ((HOP_MIN..=HOP_RANGE).contains(&reach) && path_free(walls, me, w)).then_some(w)
}

// ===================== 模拟里的小工具 =====================

struct Champ {
    id: usize,
    at: (f64, f64),
    team: usize,
    hp: f64,
}

/// 活着、能选中的英雄，和这张图能不能用 5v5 的墙（没有单位站在它的墙里）。
fn scan(sim: &StableSim<'_>) -> (Vec<Champ>, bool) {
    let mut champs = Vec::new();
    let mut walls = true;
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if !e.is_alive() {
            continue;
        }
        let (x, y) = e.pos();
        let at = (x as f64, y as f64);
        if is_wall(at.0, at.1) {
            walls = false;
        }
        if e.is_champion() && e.is_targetable() {
            let (now, max) = e.hp();
            let hp = if max > 0 { now as f64 / max as f64 } else { 1.0 };
            champs.push(Champ { id: e.id(), at, team: e.team(), hp });
        }
    }
    (champs, walls)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).any(|i| e.buff_at(i).is_some_and(|b| b.name() == name)))
}

fn has_cc(sim: &StableSim<'_>, id: usize, kinds: &[CcKindV1]) -> bool {
    sim.get_entity(id)
        .is_some_and(|e| (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind))))
}

/// 用不了 W 的状态：硬控、沉默、禁位移技能、正在位移、正在放带动作的技能。
const BUSY: [CcKindV1; 10] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::BlockSkill,
    CcKindV1::BlockMoveSkill,
    CcKindV1::ForceMove,
    CcKindV1::Animation,
];

/// 强制位移到 `to`（速度取整到每 tick 一样长）；返回 tick 数。
fn force_move(sim: &mut StableSim<'_>, lee: usize, from: (f64, f64), to: (f64, f64), speed: f64) -> usize {
    let d = dist(from, to);
    if d < 1.0 {
        return 0;
    }
    let ticks = (d / speed).ceil().max(1.0);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (to.0 - from.0).round() as i64;
    cc.dy = (to.1 - from.1).round() as i64;
    cc.speed = (d / ticks).ceil() as u64;
    sim.apply_cc(lee, &cc);
    ticks as usize
}

/// W 冲到 `spot`（逃跑 / 追击）：李青身上亮 W 的光、播 W 的声音、播跑步的动作（不借别的技能的动作），强制位移
/// 过去，之后每 tick 看一次（`dash`）；返回 tick 数。
fn w_dash(sim: &mut StableSim<'_>, lee: usize, from: (f64, f64), spot: (f64, f64), speed: f64) -> usize {
    let me = InputTargetV1::target(lee);
    sim.play_view_effect(W_VIEW, lee, &me, 0, 0, 0);
    sim.play_sfx(W_SFX, lee, &me);
    let ticks = force_move(sim, lee, from, spot, speed);
    let mut anim = CcV1::of_kind(CcKindV1::Animation, ticks as u64 + 2);
    anim.set_name(RUN_ANIM);
    sim.apply_cc(lee, &anim);
    sim.entity_remove_buff(lee, DASH);
    sim.add_buff(lee, &BuffV1::timed(DASH, ticks + 8));
    let at = InputTargetV1::pos(spot.0.round().max(0.0) as u64, spot.1.round().max(0.0) as u64);
    let name = format!("{ID}:dash");
    sim.queue_effect(&name, AttackTypeV1::Skill, lee, &at, 1);
    ticks
}

// ===================== 两个用法 =====================

/// 己方活着的防御塔。
fn allied_towers(sim: &StableSim<'_>, team: usize) -> Vec<(f64, f64)> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.is_tower() && e.is_alive() && e.team() == team)
        .map(|e| {
            let (x, y) = e.pos();
            (x as f64, y as f64)
        })
        .collect()
}

/// R 第 7 tick（他身后没有别的敌方英雄时）：定好往哪踢（队友 / 己方塔 / 李青这边），已经在他背后就直接贴上去，
/// 不在就 W 到他背后；之后每 tick 跟着他走（`follow`），第 17 tick 主包踢。
fn insec(sim: &mut StableSim<'_>, lee: usize, input: InputTargetV1) {
    let (Some(me), Some(t)) = (sim.get_entity(lee), sim.get_entity(input.target_id)) else { return };
    let (lx, ly) = me.pos();
    let (tx, ty) = t.pos();
    let team = me.team();
    let (from, target) = ((lx as f64, ly as f64), (tx as f64, ty as f64));
    let (champs, walls) = scan(sim);
    let allies: Vec<(f64, f64)> = champs.iter().filter(|c| c.team == team && c.id != lee).map(|c| c.at).collect();
    let (kick, why) = kick_dir(target, from, &allies, &allied_towers(sim, team));
    let back = (-kick.0, -kick.1);
    let gap = dist(from, target);
    let side = unit_vec((from.0 - target.0, from.1 - target.1)).unwrap_or(back);
    let direct = (side.0 * back.0 + side.1 * back.1 >= BEHIND_COS).then_some(("DIRECT: already behind him", back));
    let (how, dir, keep) = match direct {
        Some((how, dir)) => (how, dir, gap.clamp(DIRECT_MIN, BEHIND)),
        None => match behind_spot(walls, from, target, back) {
            Some((w, dir)) => {
                let at = InputTargetV1::target(lee);
                sim.play_view_effect(W_VIEW, lee, &at, 0, 0, 0);
                sim.play_sfx(W_SFX, lee, &at);
                ("W behind him", dir, dist(w, target))
            }
            // 他背后没地方落脚：就从李青站的这边踢
            None => ("DIRECT: no room behind him", side, gap.clamp(DIRECT_MIN, BEHIND)),
        },
    };
    sim.add_buff(lee, &BuffV1::timed(&follow_name(input.target_id, dir, keep), KICK_AFTER + 1));
    sim.add_buff(lee, &BuffV1::timed(&format!("{TARGET}{}", input.target_id), KICK_AFTER + 2));
    let name = format!("{ID}:follow");
    sim.queue_effect(&name, AttackTypeV1::Skill, lee, &InputTargetV1::target(input.target_id), 1);
    let name = format!("{ID}:kick_check");
    let to = (target.0 - dir.0 * 50_000.0, target.1 - dir.1 * 50_000.0);
    let at = InputTargetV1::pos(to.0.round().max(0.0) as u64, to.1.round().max(0.0) as u64);
    sim.queue_effect(&name, AttackTypeV1::Skill, lee, &at, KICK_AFTER);
    let spot = (target.0 + dir.0 * keep, target.1 + dir.1 * keep);
    wlog(format!(
        "{} INSEC {how}: kick #{} at {} toward {why}; Lee {} ({gap:.0} from him) -> {} ({keep:.0} behind)",
        head(sim, lee),
        input.target_id,
        pt(target),
        pt(from),
        pt(spot)
    ));
}

/// 回旋踢的每一 tick：按他现在的位置重算落点，挪过去（每 tick 最多 `INSEC_SPEED`）；标记到期（踢了）就停。
fn follow(sim: &mut StableSim<'_>, lee: usize) {
    let Some((id, dir, keep)) = follow_of(sim, lee) else { return };
    let Some(me) = sim.get_entity(lee).filter(|e| e.is_alive()) else { return };
    let Some(t) = sim.get_entity(id).filter(|t| t.is_alive()) else { return };
    let (x, y) = me.pos();
    let here = (x as f64, y as f64);
    let (tx, ty) = t.pos();
    let (_, walls) = scan(sim);
    let spot = follow_spot(walls, (tx as f64, ty as f64), dir, keep);
    let off = dist(here, spot);
    if off > 1.0 {
        let step = INSEC_SPEED.min(off);
        let next = (here.0 + (spot.0 - here.0) / off * step, here.1 + (spot.1 - here.1) / off * step);
        sim.entity_set_pos(lee, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64);
    }
    let name = format!("{ID}:follow");
    sim.queue_effect(&name, AttackTypeV1::Skill, lee, &InputTargetV1::target(id), 1);
}

/// W 冲刺的每一 tick：到了就结束；身上没有强制位移了却还没到（韧性把它缩短了）就再补一段；
/// 过了最晚到达时间还差 3000 以上，直接放到落点。
fn dash(sim: &mut StableSim<'_>, lee: usize, input: InputTargetV1) {
    let Some(me) = sim.get_entity(lee) else { return };
    if !me.is_alive() || input.kind != InputTargetKindV1::Pos.code() {
        return;
    }
    let (x, y) = me.pos();
    let here = (x as f64, y as f64);
    let spot = (input.x as f64, input.y as f64);
    let off = dist(here, spot);
    if off <= 1_500.0 {
        sim.entity_remove_buff(lee, DASH);
        return;
    }
    if !has_buff(sim, lee, DASH) {
        if off > 3_000.0 {
            sim.entity_set_pos(lee, input.x, input.y);
            wlog(format!("{} host did not move him ({off:.0} short): placed on the spot", head(sim, lee)));
        }
        return;
    }
    if !has_cc(sim, lee, &[CcKindV1::ForceMove]) {
        if has_buff(sim, lee, REDO) {
            // 补的那段宿主也没执行：自己一步步挪过去（一直挪到到）
            let step = INSEC_SPEED.min(off);
            let next = (here.0 + (spot.0 - here.0) / off * step, here.1 + (spot.1 - here.1) / off * step);
            sim.entity_set_pos(lee, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64);
            sim.entity_remove_buff(lee, REDO);
            sim.add_buff(lee, &BuffV1::timed(REDO, 2));
            if !has_buff(sim, lee, STEPPING) {
                sim.add_buff(lee, &BuffV1::timed(STEPPING, 60));
                wlog(format!("{} host did not move him ({off:.0} to go): stepping to the spot", head(sim, lee)));
            }
        } else {
            force_move(sim, lee, here, spot, HOP_SPEED.max(off / 2.0));
            sim.add_buff(lee, &BuffV1::timed(REDO, 2));
        }
    }
    let name = format!("{ID}:dash");
    sim.queue_effect(&name, AttackTypeV1::Skill, lee, &input, 1);
}

/// R 的第 17 tick（主包踢的那一刻）：李青踢他的方向（李青 → 他）和该踢的方向（输入点：他往该踢的方向 50000）差多少，
/// 隔多远，记进日志。
fn kick_check(sim: &mut StableSim<'_>, lee: usize, input: InputTargetV1) {
    let Some(me) = sim.get_entity(lee) else { return };
    let (x, y) = me.pos();
    let here = (x as f64, y as f64);
    let toward = (input.x as f64, input.y as f64);
    let target_id = (0..me.buff_count())
        .filter_map(|i| me.buff_at(i))
        .find_map(|b| b.name().strip_prefix(TARGET).and_then(|id| id.parse::<usize>().ok()));
    let Some(t) = target_id.and_then(|id| sim.get_entity(id)) else { return };
    let (tx, ty) = t.pos();
    let target = (tx as f64, ty as f64);
    let kick = (target.0 - here.0, target.1 - here.1);
    let want = (toward.0 - target.0, toward.1 - target.1);
    let c = (kick.0 * want.0 + kick.1 * want.1) / (kick.0.hypot(kick.1) * want.0.hypot(want.1)).max(1e-9);
    let off = c.clamp(-1.0, 1.0).acos().to_degrees();
    wlog(format!(
        "{} KICK at t+{KICK_AFTER}: Lee {} target {} ({:.0} apart), {off:.0} deg off the planned way: {}",
        head(sim, lee),
        pt(here),
        pt(target),
        dist(here, target),
        if off <= 30.0 { "on target" } else { "OFF" }
    ));
}

/// 被动：残血、正在逃的时候 W 顺着逃的方向冲走；追着残血逃跑的敌人时 W 追上去。`vel`：英雄们每 tick 的速度。
fn hop(sim: &mut StableSim<'_>, lee: usize, vel: &HashMap<usize, (f64, f64)>) {
    let Some(me) = sim.get_entity(lee) else { return };
    if !me.is_alive() || has_buff(sim, lee, CD) || has_cc(sim, lee, &BUSY) {
        return;
    }
    let team = me.team();
    let (champs, walls) = scan(sim);
    let Some(mine) = champs.iter().find(|c| c.id == lee) else { return };
    let here = mine.at;
    let v_lee = vel.get(&lee).copied().unwrap_or_default();
    let foes: Vec<&Champ> = champs.iter().filter(|c| c.team != team).collect();
    let foe_at: Vec<(f64, f64)> = foes.iter().map(|c| c.at).collect();
    let closest = foe_at.iter().copied().min_by(|a, b| dist(here, *a).total_cmp(&dist(here, *b)));
    let (spot, why) = if mine.hp <= LOW_HP && nearest(here, &foe_at) <= DANGER_R {
        // 只在他自己正往远离最近那个敌人的方向跑时 W
        let fleeing = closest.is_some_and(|c| moving_away(here, v_lee, c));
        (fleeing.then(|| escape_spot(walls, here, &foe_at, v_lee)).flatten(), "ESCAPE")
    } else {
        let prey = foes
            .iter()
            .filter(|c| c.hp <= CHASE_HP && chasing(here, v_lee, c.at, vel.get(&c.id).copied().unwrap_or_default()))
            .filter_map(|c| chase_spot(walls, here, c.at).map(|w| (dist(here, c.at), w)))
            .min_by(|a, b| a.0.total_cmp(&b.0));
        (prey.map(|(_, w)| w), "CHASE")
    };
    let Some(w) = spot else { return };
    sim.add_buff(lee, &BuffV1::timed(CD, HOP_CD));
    let ticks = w_dash(sim, lee, here, w, HOP_SPEED);
    wlog(format!(
        "{} {why} W to {} ({:.0} away, {ticks} ticks), hp {:.0}%, running {:.0}/tick, nearest enemy {:.0} -> {:.0}",
        head(sim, lee),
        pt(w),
        dist(here, w),
        mine.hp * 100.0,
        v_lee.0.hypot(v_lee.1),
        nearest(here, &foe_at),
        nearest(w, &foe_at)
    ));
}

// ===================== Q 的出手（选手 AI） =====================

/// 主包的 Q「天音波」：出手第 `Q_WIND` tick 发波，每 tick 飞 `Q_SPEED`、半径 `Q_RADIUS`、飞 `Q_RANGE`，碰到第一个敌人就停。
/// 方向在按下 Q 的那一刻就定了，所以对走动的人要预判。
pub const Q_WIND: f64 = 16.0;
pub const Q_SPEED: f64 = 4_500.0;
pub const Q_RADIUS: f64 = 7_000.0;
pub const Q_RANGE: f64 = 75_000.0;
/// 预判最多往前算多远。
pub const Q_LEAD_CAP: f64 = 30_000.0;
/// 野怪剩这么少血（比例）就不 Q：波到之前它就被打死了。
pub const Q_MONSTER_LOW: f64 = 0.2;
/// 认内置 AI 想 Q 谁：离出手方向那条线（或出手点）这么近的敌人。
pub const Q_PICK_OFF: f64 = 20_000.0;
/// 两次看之间走得比这快的（冲刺、闪现、被击飞）不算走路。
const AI_MAX_WALK: f64 = 2_500.0;

/// 一个敌方单位是什么。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Champion,
    Minion,
    Monster,
}

/// Q 眼里的一个敌方单位：位置、每 tick 的速度、碰撞半径、种类、生命比例。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Mark {
    pub id: usize,
    pub at: (f64, f64),
    pub v: (f64, f64),
    pub r: f64,
    pub kind: Kind,
    pub hp: f64,
}

/// Q 怎么处理内置 AI 这一下：照放、改方向（往这个点打）、不放。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum QPlan {
    Keep,
    Aim((f64, f64)),
    Skip(&'static str),
}

fn sub(a: (f64, f64), b: (f64, f64)) -> (f64, f64) {
    (a.0 - b.0, a.1 - b.1)
}

/// 点 `p` 在从 `from` 朝单位方向 `d` 的线上：沿线多远、离线多远。
fn along_off(from: (f64, f64), d: (f64, f64), p: (f64, f64)) -> (f64, f64) {
    let v = sub(p, from);
    (v.0 * d.0 + v.1 * d.1, (v.0 * d.1 - v.1 * d.0).abs())
}

/// 内置 AI 的 Q 想打谁：输入是单位就是他；是方向就找离那条线最近的（射程内、`Q_PICK_OFF` 内）；是点就找离那点最近的。
pub fn intended(input: &InputTargetV1, me: (f64, f64), marks: &[Mark]) -> Option<Mark> {
    match InputTargetKindV1::from_code(input.kind) {
        Some(InputTargetKindV1::Target) => marks.iter().find(|m| m.id == input.target_id).copied(),
        Some(InputTargetKindV1::Dir) => {
            let n = (input.dir_x as f64).hypot(input.dir_y as f64);
            if n < 1.0 {
                return None;
            }
            let d = (input.dir_x as f64 / n, input.dir_y as f64 / n);
            marks
                .iter()
                .filter_map(|m| {
                    let (along, off) = along_off(me, d, m.at);
                    (along > 0.0 && along <= Q_RANGE + m.r && off <= Q_PICK_OFF).then_some((off, m))
                })
                .min_by(|a, b| a.0.total_cmp(&b.0))
                .map(|(_, m)| *m)
        }
        Some(InputTargetKindV1::Pos) => {
            let p = (input.x as f64, input.y as f64);
            marks
                .iter()
                .map(|m| (dist(m.at, p), m))
                .filter(|(d, _)| *d <= Q_PICK_OFF)
                .min_by(|a, b| a.0.total_cmp(&b.0))
                .map(|(_, m)| *m)
        }
        _ => None,
    }
}

/// 预判：他照现在的速度走，波飞到时他在哪（飞多久看距离，迭代三次；最多往前算 `Q_LEAD_CAP`）。
pub fn lead(me: (f64, f64), m: &Mark) -> (f64, f64) {
    let mut p = m.at;
    for _ in 0..3 {
        let t = Q_WIND + dist(me, p) / Q_SPEED;
        let (mut dx, mut dy) = (m.v.0 * t, m.v.1 * t);
        let n = dx.hypot(dy);
        if n > Q_LEAD_CAP {
            (dx, dy) = (dx * Q_LEAD_CAP / n, dy * Q_LEAD_CAP / n);
        }
        p = (m.at.0 + dx, m.at.1 + dy);
    }
    p
}

/// 从 `me` 往 `aim` 打，在打到 `target` 之前会不会先被别的小兵、野怪挡住（不穿透；挡的是别的英雄就算打中他）。
pub fn blocked(me: (f64, f64), aim: (f64, f64), target: usize, marks: &[Mark]) -> Option<Mark> {
    let n = dist(me, aim).max(1.0);
    let d = ((aim.0 - me.0) / n, (aim.1 - me.1) / n);
    marks
        .iter()
        .filter(|m| m.id != target && m.kind != Kind::Champion)
        .filter_map(|m| {
            let (along, off) = along_off(me, d, m.at);
            (along > 0.0 && along < n && off <= Q_RADIUS + m.r).then_some((along, m))
        })
        .min_by(|a, b| a.0.total_cmp(&b.0))
        .map(|(_, m)| *m)
}

/// 照高手的打法处理内置 AI 这一下 Q：英雄——往他走到的地方打（预判），被小兵挡住或预判后够不着就不放；
/// 小兵——不放（不拿 Q 打走动的兵）；野怪——照放，快死的不放。认不出打谁就照放。
pub fn plan_q(input: &InputTargetV1, me: (f64, f64), marks: &[Mark]) -> (QPlan, Option<Mark>) {
    let Some(t) = intended(input, me, marks) else { return (QPlan::Keep, None) };
    let plan = match t.kind {
        Kind::Champion => {
            let p = lead(me, &t);
            if dist(me, p) > Q_RANGE + t.r {
                QPlan::Skip("he will be out of reach")
            } else if blocked(me, p, t.id, marks).is_some() {
                QPlan::Skip("a minion or monster is in the way")
            } else {
                QPlan::Aim(p)
            }
        }
        Kind::Monster if t.hp <= Q_MONSTER_LOW => QPlan::Skip("the monster dies before the wave lands"),
        Kind::Monster => QPlan::Keep,
        Kind::Minion => QPlan::Skip("no Q on minions"),
    };
    (plan, Some(t))
}

/// 每个李青一份：上次看到的敌方单位（算速度）。
#[derive(Clone, Default)]
struct LeeAi {
    seen: HashMap<usize, (f64, f64, usize)>,
}

impl LeeAi {
    /// 场上活着、能选中的敌方单位（英雄、小兵、野怪；不含塔），带上和上次比的速度。
    fn marks(&mut self, sim: &StableSim<'_>, team: usize, tick: usize) -> Vec<Mark> {
        let mut out = Vec::new();
        let mut seen = HashMap::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() || !e.is_targetable() || e.team() == team || e.is_tower() {
                continue;
            }
            let (x, y) = e.pos();
            let at = (x as f64, y as f64);
            let mut v = (0.0, 0.0);
            if let Some(&(px, py, t)) = self.seen.get(&e.id()) {
                let dt = tick.saturating_sub(t).max(1) as f64;
                let w = ((at.0 - px) / dt, (at.1 - py) / dt);
                if w.0.hypot(w.1) <= AI_MAX_WALK {
                    v = w;
                }
            }
            seen.insert(e.id(), (at.0, at.1, tick));
            let kind = if e.is_champion() {
                Kind::Champion
            } else if e.is_minion() {
                Kind::Minion
            } else {
                Kind::Monster
            };
            let (now, max) = e.hp();
            let hp = if max > 0 { now as f64 / max as f64 } else { 1.0 };
            out.push(Mark { id: e.id(), at, v, r: e.radius() as f64, kind, hp });
        }
        self.seen = seen;
        out
    }
}

impl StablePlayerAi for LeeAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:q")
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == "league_leesin"
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let tick = ctx.tick();
        let me_id = ctx.player_id();
        // 先把要用的读出来（sim 借着 ctx，后面还要用 ctx 验输入）
        let (plan, t, me, head_line) = {
            let sim = ctx.sim()?;
            let player = sim.get_player(me_id)?;
            let lee = player.champion()?;
            let (lx, ly) = lee.pos();
            let me = (lx as f64, ly as f64);
            let team = lee.team();
            let lee_id = lee.id();
            let marks = self.marks(&sim, team, tick);
            let base = base?;
            if base.kind != InputKindV1::Skill.code() {
                return None;
            }
            let (plan, t) = plan_q(&base.target, me, &marks);
            (plan, t, me, head(&sim, lee_id))
        };
        let t = t?;
        match plan {
            QPlan::Keep => None,
            QPlan::Aim(p) => {
                let (dx, dy) = ((p.0 - me.0).round() as i64, (p.1 - me.1).round() as i64);
                let input = InputV1::action(InputKindV1::Skill, InputTargetV1::dir(dx, dy));
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                wlog(format!(
                    "{head_line} Q AIM at #{} {:?} at {} walking {:.0}/tick: thrown at {} ({:.0} lead)",
                    t.id,
                    t.kind,
                    pt(t.at),
                    t.v.0.hypot(t.v.1),
                    pt(p),
                    dist(p, t.at)
                ));
                Some(input)
            }
            QPlan::Skip(why) => {
                let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t.id));
                let input = if ctx.is_valid_input(&attack) {
                    attack
                } else {
                    InputV1::move_to(t.at.0.round().max(0.0) as u64, t.at.1.round().max(0.0) as u64)
                };
                wlog(format!("{head_line} Q SKIP #{} {:?} at {}: {why}", t.id, t.kind, pt(t.at)));
                Some(input)
            }
        }
    }
}

// ===================== 注册 =====================

struct Insec;
impl StableEffectType for Insec {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        insec(sim, caster, input);
    }
}

struct Follow;
impl StableEffectType for Follow {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        follow(sim, caster);
    }
}

struct KickCheck;
impl StableEffectType for KickCheck {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        kick_check(sim, caster, input);
    }
}

struct Dash;
impl StableEffectType for Dash {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        dash(sim, caster, input);
    }
}

/// 每个李青一份：上一 tick 的冷却（普攻、Q、E、R）、最近一次出手后多久内不 W、上次看到英雄们在哪。
#[derive(Clone, Default)]
struct Hop {
    last: Option<(usize, usize, usize, usize)>,
    quiet_until: usize,
    seen: HashMap<usize, (f64, f64, usize)>,
    /// 按了 Q 的那一 tick（还没看到 Q2 飞踢 = 还不知道打没打中）。
    q_cast: Option<usize>,
}

/// Q 按下后这么久还没飞踢（Q2）就算打空：第 16 tick 发波，飞满射程 17 tick，打中后 12 tick 飞踢。
pub const Q_VERDICT: usize = 50;

fn anim_playing(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| c.kind == CcKindV1::Animation.code() && c.name() == name))
    })
}

impl Hop {
    /// 记下活着的英雄们在哪，返回和上次比每 tick 的速度（冲刺、闪现那种不算）。
    fn track(&mut self, sim: &StableSim<'_>, tick: usize) -> HashMap<usize, (f64, f64)> {
        let mut vel = HashMap::new();
        let mut seen = HashMap::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || !e.is_alive() {
                continue;
            }
            let (x, y) = e.pos();
            let at = (x as f64, y as f64);
            if let Some(&(px, py, t)) = self.seen.get(&e.id()) {
                let dt = tick.saturating_sub(t);
                let v = ((at.0 - px) / dt.max(1) as f64, (at.1 - py) / dt.max(1) as f64);
                if (1..=2 * AUTO_EVERY).contains(&dt) && v.0.hypot(v.1) <= MAX_WALK {
                    vel.insert(e.id(), v);
                }
            }
            seen.insert(e.id(), (at.0, at.1, tick));
        }
        self.seen = seen;
        vel
    }
}

/// 冷却从上一 tick 跳高了 = 这一 tick 刚出手；返回之后多久内不 W。
pub fn cast_quiet(last: (usize, usize, usize, usize), now: (usize, usize, usize, usize)) -> usize {
    let started = |a: usize, b: usize| b > a;
    let mut quiet = 0;
    if started(last.0, now.0) {
        quiet = quiet.max(AFTER_ATTACK);
    }
    if started(last.1, now.1) || started(last.2, now.2) {
        quiet = quiet.max(AFTER_SKILL);
    }
    if started(last.3, now.3) {
        quiet = quiet.max(AFTER_ULT);
    }
    quiet
}

impl StablePassive for Hop {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, entity: usize) {
        let tick = sim.tick();
        if let Some(now) = sim.get_player(player).and_then(|p| p.cooldowns()) {
            if let Some(last) = self.last {
                let quiet = cast_quiet(last, now);
                if quiet > 0 {
                    self.quiet_until = self.quiet_until.max(tick + quiet);
                }
                // 按了 Q（R 里自带的那一下不算：R 的冷却同时跳）
                if now.1 > last.1 && now.3 <= last.3 {
                    self.q_cast = Some(tick);
                }
            }
            self.last = Some(now);
        }
        // Q 打中没有：出了 Q2 飞踢就是打中了，`Q_VERDICT` tick 还没有就是打空
        if let Some(t0) = self.q_cast {
            if anim_playing(sim, entity, "q2") {
                self.q_cast = None;
                wlog(format!("{} Q LANDED (Q2 after {} ticks)", head(sim, entity), tick - t0));
            } else if tick > t0 + Q_VERDICT {
                self.q_cast = None;
                wlog(format!("{} Q MISSED", head(sim, entity)));
            }
        }
        if tick % AUTO_EVERY == 0 {
            let vel = self.track(sim, tick);
            if tick >= self.quiet_until {
                hop(sim, entity, &vel);
            }
        }
    }
}

fn init(host: &StableHost) -> StableMod {
    // 上一次启动的日志留一份（.prev.log），重启游戏不丢
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1.6 (W dash, no ward, aimed Q) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    let mut module = StableMod::new(ID);
    module.add_native_effect(format!("{ID}:insec"), Insec);
    module.add_native_effect(format!("{ID}:dash"), Dash);
    module.add_native_effect(format!("{ID}:kick_check"), KickCheck);
    module.add_native_effect(format!("{ID}:follow"), Follow);
    module.add_player_input_ai(LeeAi::default());
    module.add_native_passive(format!("{ID}:hop"), Hop::default());
    host.log(LogLevel::Info, "league_leesin_hop v1 loaded (Lee Sin's W dashes to a spot).");
    module
}

declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_insec_dash_lands_behind_the_target() {
        // 地图中央是空地：落在目标背后 15000
        let (w, _) = behind_spot(true, (440_000.0, 480_000.0), (480_000.0, 480_000.0), (1.0, 0.0)).unwrap();
        assert!((w.0 - 495_000.0).abs() < 1.0 && (w.1 - 480_000.0).abs() < 1.0, "{w:?}");
        // 目标背靠第 12 行那段横墙（y 384000 起）：背后 15000 在墙里，往近挪
        let target = (272_000.0, 375_000.0);
        let (w, _) = behind_spot(true, (272_000.0, 330_000.0), target, (0.0, 1.0)).unwrap();
        assert!(!is_wall(w.0, w.1) && w.1 < 384_000.0 && dist(w, target) >= BEHIND_MIN, "{w:?}");
        // 贴着墙，背后（转 30° 也）一点地方都没有：落不了脚
        assert!(behind_spot(true, (272_000.0, 340_000.0), (272_000.0, 382_000.0), (0.0, 1.0)).is_none());
        // 别的地图不查墙
        assert!(behind_spot(false, (272_000.0, 340_000.0), (272_000.0, 382_000.0), (0.0, 1.0)).is_some());
    }

    fn mark(id: usize, x: f64, y: f64, kind: Kind) -> Mark {
        Mark { id, at: (x, y), v: (0.0, 0.0), r: 5_000.0, kind, hp: 1.0 }
    }

    #[test]
    fn q_aims_where_he_will_be() {
        let me = (400_000.0, 480_000.0);
        // 他在东边 50000、往北走（每 tick 1000）：往北边预判的位置打
        let him = Mark { v: (0.0, -1_000.0), ..mark(7, 450_000.0, 480_000.0, Kind::Champion) };
        let (plan, t) = plan_q(&InputTargetV1::dir(50_000, 0), me, &[him]);
        assert_eq!(t.unwrap().id, 7);
        let QPlan::Aim(p) = plan else { panic!("{plan:?}") };
        let t_hit = Q_WIND + dist(me, p) / Q_SPEED;
        assert!((p.1 - (480_000.0 - 1_000.0 * t_hit)).abs() < 1_500.0 && (p.0 - 450_000.0).abs() < 1.0, "{p:?}");
        // 站着不动：照原样打他
        let (plan, _) = plan_q(&InputTargetV1::dir(50_000, 0), me, &[mark(7, 450_000.0, 480_000.0, Kind::Champion)]);
        assert_eq!(plan, QPlan::Aim((450_000.0, 480_000.0)));
        // 中间有个小兵挡着：不放
        let minion = mark(9, 425_000.0, 482_000.0, Kind::Minion);
        let (plan, _) = plan_q(&InputTargetV1::dir(50_000, 0), me, &[mark(7, 450_000.0, 480_000.0, Kind::Champion), minion]);
        assert!(matches!(plan, QPlan::Skip(_)), "{plan:?}");
        // 跑得太快、预判后出了射程：不放
        let runner = Mark { v: (2_000.0, 0.0), ..mark(7, 465_000.0, 480_000.0, Kind::Champion) };
        assert!(matches!(plan_q(&InputTargetV1::target(7), me, &[runner]).0, QPlan::Skip(_)));
    }

    #[test]
    fn q_leaves_minions_and_dying_monsters_alone() {
        let me = (400_000.0, 480_000.0);
        let (plan, t) = plan_q(&InputTargetV1::dir(1, 0), me, &[mark(3, 440_000.0, 485_000.0, Kind::Minion)]);
        assert_eq!((plan, t.unwrap().id), (QPlan::Skip("no Q on minions"), 3));
        let camp = mark(4, 440_000.0, 480_000.0, Kind::Monster);
        assert_eq!(plan_q(&InputTargetV1::target(4), me, &[camp]).0, QPlan::Keep);
        let dying = Mark { hp: 0.1, ..camp };
        assert!(matches!(plan_q(&InputTargetV1::target(4), me, &[dying]).0, QPlan::Skip(_)));
        // 认不出打谁：照放
        assert_eq!(plan_q(&InputTargetV1::dir(0, 1), me, &[camp]).0, QPlan::Keep);
        // 认人：方向上离线最近的；点上离点最近的
        let a = mark(1, 450_000.0, 470_000.0, Kind::Champion);
        let b = mark(2, 450_000.0, 489_000.0, Kind::Champion);
        assert_eq!(intended(&InputTargetV1::dir(50_000, -9_000), me, &[a, b]).unwrap().id, 1);
        assert_eq!(intended(&InputTargetV1::pos(450_000, 488_000), me, &[a, b]).unwrap().id, 2);
    }

    #[test]
    fn a_fresh_cast_keeps_w_quiet() {
        let idle = (0, 0, 0, 0);
        assert_eq!(cast_quiet(idle, idle), 0);
        assert_eq!(cast_quiet(idle, (64, 0, 0, 0)), AFTER_ATTACK);
        assert_eq!(cast_quiet(idle, (0, 360, 0, 0)), AFTER_SKILL);
        assert_eq!(cast_quiet(idle, (0, 0, 420, 0)), AFTER_SKILL);
        assert_eq!(cast_quiet(idle, (64, 360, 0, 3000)), AFTER_ULT);
        // 冷却在往下走：没有新的出手
        assert_eq!(cast_quiet((30, 200, 100, 2000), (29, 199, 99, 1999)), 0);
    }

    #[test]
    fn escape_runs_away_and_chase_stops_short() {
        let me = (480_000.0, 480_000.0);
        let foes = [(450_000.0, 480_000.0), (460_000.0, 500_000.0)];
        // 他正往东北跑：W 也往那边（左右 60° 内）
        let w = escape_spot(true, me, &foes, (700.0, -700.0)).unwrap();
        assert!(nearest(w, &foes) >= nearest(me, &foes) + 15_000.0 && w.0 > me.0 && w.1 < me.1, "{w:?}");
        assert!(dist(me, w) >= HOP_MIN && dist(me, w) <= HOP_RANGE + 1.0);
        assert!(cos((w.0 - me.0, w.1 - me.1), (700.0, -700.0)) >= ALONG_COS);
        // 往敌人那边跑（在打）：那个方向没有能逃的点
        assert!(escape_spot(true, me, &foes, (-900.0, 0.0)).is_none());
        // 追：停在他身前 8000
        let target = (530_000.0, 480_000.0);
        let w = chase_spot(true, me, target).unwrap();
        assert!((dist(w, target) - CHASE_STOP).abs() < 1.0);
        // 近了直接打，远了摸不着
        assert!(chase_spot(true, me, (500_000.0, 480_000.0)).is_none());
        assert!(chase_spot(true, me, (560_000.0, 480_000.0)).is_none());
    }

    #[test]
    fn the_kick_sends_him_to_lees_team() {
        let him = (480_000.0, 480_000.0);
        let lee = (520_000.0, 480_000.0);
        // 队友在西边：往西踢；李青在东边 = 已经在他背后
        let (k, why) = kick_dir(him, lee, &[(400_000.0, 470_000.0), (410_000.0, 490_000.0)], &[(480_000.0, 700_000.0)]);
        assert_eq!(why, "allies");
        assert!(k.0 < -0.99, "{k:?}");
        // 队友太远（100000 外）：朝最近的己方塔（南边）
        let (k, why) = kick_dir(him, lee, &[(300_000.0, 480_000.0)], &[(480_000.0, 700_000.0), (900_000.0, 900_000.0)]);
        assert_eq!(why, "tower");
        assert!(k.1 > 0.99, "{k:?}");
        // 都没有：踢回李青这边
        let (k, why) = kick_dir(him, lee, &[], &[]);
        assert_eq!(why, "back");
        assert!(k.0 > 0.99, "{k:?}");
        // 他背后（往北）落脚点；那里是墙就转一点找（第 3 行第 15-21 列是墙：y 96000-128000）
        let (w, dir) = behind_spot(true, (480_000.0, 150_000.0), (560_000.0, 140_000.0), (0.0, -1.0)).unwrap();
        assert!(!is_wall(w.0, w.1) && dist(w, (560_000.0, 140_000.0)) >= BEHIND_MIN - 1.0, "{w:?} {dir:?}");
    }

    #[test]
    fn the_follow_mark_round_trips() {
        let name = follow_name(41, (0.6, -0.8), 12_345.0);
        assert_eq!(name, "league_leesin_hop_follow:41:600:-800:123");
        let (id, dir, keep) = parse_follow(&name).unwrap();
        assert_eq!((id, keep), (41, 12_300.0));
        assert!((dir.0 - 0.6).abs() < 1e-9 && (dir.1 + 0.8).abs() < 1e-9);
        assert!(follow_name(u32::MAX as usize, (-0.999, 0.999), 999_999.0).len() <= BUFF_NAME_CAP);
        assert!(parse_follow("league_leesin_hop_target:41").is_none());
        let w = follow_spot(true, (489_000.0, 480_000.0), (1.0, 0.0), BEHIND);
        assert!((w.0 - (489_000.0 + BEHIND)).abs() < 1.0 && (w.1 - 480_000.0).abs() < 1.0, "{w:?}");
    }

    #[test]
    fn w_only_follows_where_he_is_already_going() {
        let lee = (480_000.0, 480_000.0);
        let him = (530_000.0, 480_000.0);
        // 他往东跑开、李青往东追：在追
        assert!(chasing(lee, (900.0, 0.0), him, (900.0, 0.0)));
        // 他朝李青走过来（来打架）、李青站着、李青往回走：都不算
        assert!(!chasing(lee, (900.0, 0.0), him, (-900.0, 0.0)));
        assert!(!chasing(lee, (0.0, 0.0), him, (900.0, 0.0)));
        assert!(!chasing(lee, (-900.0, 0.0), him, (900.0, 0.0)));
        // 走得太慢不算在跑
        assert!(!chasing(lee, (200.0, 0.0), him, (900.0, 0.0)));
        // 逃：李青往远离敌人的方向跑
        let foe = (450_000.0, 480_000.0);
        assert!(moving_away(lee, (900.0, 300.0), foe));
        assert!(!moving_away(lee, (-900.0, 0.0), foe) && !moving_away(lee, (0.0, 900.0), foe));
    }
}
