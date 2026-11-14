//! 诺提勒斯附加包：Q「疏通航道」钩墙（用户选的附加包：「做钩墙附加包」）。
//!
//! 主包是纯数据，读不到地图的墙：主包里锚飞出去只钩英雄，没钩到就落空。英雄联盟的疏通航道钩到墙上会把诺提勒斯拉到墙边，
//! 并返还一半冷却。`mod.override_info` 把主包的诺提勒斯换成 `override/` 里的副本（tools/kit/build_nautilus.py 的
//! native=1）：数据和主包一样，锚飞出去的那一 tick 多调一次本包的原生效果 `league_nautilus:hook`（输入是 Q 的方向）。
//!
//! - `hook`：沿 Q 的方向从他脚下往前找，`q_reach` 内先碰到敌方英雄（离锚的路线 `q_rad` + 身体以内）就什么都不做——主包的锚会
//!   钩住他；先碰到墙（引擎的碰撞墙，5v5 地图野区的 90 格，卡蜜尔附加包的 `maps.rs`）就按锚飞到墙的时间排一个 `pull`。
//!   主包的锚穿过小兵和野怪，所以这里也只看英雄。0.1.6（2026-11-14）曾跟着主包按英雄联盟改成「停在第一个敌人身上」（小兵、
//!   野怪也算）；模拟里他明显变弱，用户看了以后同一天说「泰坦的钩子恢复穿过小兵」，0.1.7 改回只看英雄（钩中的眩晕留着）。
//! - `pull`：锚咬在墙上：他被拉到墙边（强制位移，速度 `q_dash`，停在离墙 `GAP` 处），播主包的 skill_pull 动作、钩墙音效和
//!   钩中的水花，Q 冷却返还一半（`skill_cooldown_mult` +100 的 3 tick buff：剩下的冷却封顶到冷却时间的一半；W+E 若剩得更多
//!   也一起封顶，引擎没有只给一个技能的字段；`ult_cooldown_mult` -100 让大招不跟着封顶，0.1.2）。之后每 tick 看一次（`watch`），宿主没挪他就逐 tick 自己走一步。
//!   拉的途中（终点、上一 tick 在哪、看到哪一 tick）记在 [`WATCHES`] 里，按（这份模拟的编号、他），排的 `watch` 只带终点
//!   （0.1.4：以前塞在排队输入里，排队后丢了，`watch` 第一 tick 就收手）。
//! - 被硬控、死了就不拉。比 `HOOK_MIN` 近的墙不钩（拉不出样子）。
//!
//! 排山倒海每个英雄各算 6 秒（0.1.8，用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」）：英雄联盟 "This
//! effect cannot occur on the same target more than once every few seconds"（每个目标 6 秒）。主包的数据读不到目标身上的
//! 标记，冷却算在他自己身上（定住一个人后 6 秒内谁都不定）。副本（build_nautilus.py 的 native=1）里普攻打中英雄的那一下
//! （主包的英雄替身）先调用原生效果 `league_nautilus:stagger`：这个英雄 `P_REST_T` tick 内没被定过（身上没有 `P_REST`），或
//! 诺提勒斯身上有 Q 的连招标记 `q_land`（钩中的人下一下普攻必定住，用户要的连招），就给他挂 `P_REST`、给诺提勒斯挂 3 tick 的
//! `P_GO`；数据当 tick（读不到就下一 tick）读到它才定住、补伤害。还是只对英雄（小兵、野怪照主包不定）。
//!
//! 数字从英雄数据的 `passive.params` 来不了（这一招没有被动），所以和主包 P 表的值写在这里（`Q_*`），主包改了这里一起改
//! （`tests::the_numbers_match_the_kit` 读主包的数据核对）。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nautilus.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_nautilus";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_nautilus") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 主包诺提勒斯的名字（动作、画面、音效都以它开头）。
fn nt(x: &str) -> String {
    format!("league_nautilus_{x}")
}

// ===================== 数值（主包 build_nautilus.P） =====================

/// 排山倒海：副本调用的原生效果；英雄身上「定过了」的标记和它留多久（主包 P 的 `p_cd`，测试核对）；给数据读的旗子。
pub const STAGGER: &str = "league_nautilus:stagger";
pub const P_REST: &str = "league_nautilus_p_rest";
pub const P_REST_T: usize = 360;
pub const P_GO: &str = "league_nautilus_p_go";
pub const P_GO_T: usize = 3;

/// 墙格的边长（世界单位）。
pub const CELL: f64 = 32_000.0;
/// 锚飞多远、多快、多宽（q_reach、q_speed、q_rad）。
pub const Q_REACH: f64 = 85_000.0;
pub const Q_SPEED: f64 = 6_000.0;
pub const Q_RAD: f64 = 10_000.0;
/// 拉过去的速度（q_dash）和动作时长（q_anim）。
pub const Q_DASH: f64 = 2_500.0;
pub const Q_ANIM: u64 = 24;
/// 敌方单位的身体半径（够得着锚的路线就算会被钩住）。
pub const BODY: f64 = 6_000.0;
/// 沿路线找墙的步长。
pub const STEP: f64 = 500.0;
/// 停在离墙这么远处。
pub const GAP: f64 = 3_000.0;
/// 比这近的墙不钩。
pub const HOOK_MIN: f64 = 12_000.0;
/// 离停点这么近就算到了。
pub const ARRIVE: f64 = 2_000.0;
/// 拉的过程最多看这么多 tick。
pub const WATCH_MAX: usize = 60;
/// Q 冷却返还：`skill_cooldown_mult` 的值（+100 = 封顶到一半）和持续 tick。
pub const REFUND: i32 = 100;
pub const REFUND_T: usize = 3;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_NAUTILUS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_nautilus.log");
        }
    }
    PathBuf::from("league_nautilus.log")
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

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

// ===================== 墙 =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一张墙格子：`cells[y][x]`。
#[derive(Clone, Debug, PartialEq)]
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
}

impl Grid {
    pub fn from_rows(rows: &[&str]) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect() }
    }

    pub fn builtin() -> [Grid; 3] {
        [Grid::from_rows(&maps::MOBA), Grid::from_rows(&maps::SINGLE_LANE), Grid::from_rows(&maps::DEATH_MATCH)]
    }

    /// 世界坐标落在墙格里吗（地图外不算）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return false;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(false)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }

    /// 从 `from` 沿 `dir`（单位向量）`reach` 内第一次碰到墙的距离。
    pub fn first_wall(&self, from: (f64, f64), dir: (f64, f64), reach: f64) -> Option<f64> {
        let mut t = STEP;
        while t <= reach {
            if self.is_wall(from.0 + dir.0 * t, from.1 + dir.1 * t) {
                return Some(t);
            }
            t += STEP;
        }
        None
    }
}

/// 猜地图用的点：所有活着的单位（英雄、小兵、野怪、塔……）。只看英雄的话，大家都站在三张图都空着的那条斜带上
/// （中路、两边泉水）时打平，平手偏向墙多的单线 / 死斗图，5v5 就猜错了（2026-11-01 复查：波比的 R 有 7 次退回击退）；
/// 5v5 边路的兵和野区的野怪几乎一直在，正好落在另两张图的墙里。
fn unit_points(sim: &StableSim<'_>) -> Vec<(f64, f64)> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_alive())
        .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
        .collect()
}

/// 这局是哪张图：站在墙里的英雄最少、墙又最多的那张（泰隆附加包的判断）。
pub fn current(grids: &[Grid], champions: &[(f64, f64)]) -> Option<usize> {
    grids
        .iter()
        .enumerate()
        .min_by_key(|(_, g)| {
            let inside = champions.iter().filter(|&&(x, y)| g.is_wall(x, y)).count();
            (inside, std::cmp::Reverse(g.walls()))
        })
        .map(|(i, _)| i)
}

/// 锚沿路线先碰到的是什么：敌方单位（主包的锚会钩它）、墙（`Some(停点, 锚飞的距离)`），或什么都没有。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Hit {
    Unit,
    Wall((f64, f64), f64),
    Nothing,
}

/// 沿 Q 的方向：`foes`（敌方英雄）里离路线 `Q_RAD + BODY` 以内、在墙前的先被钩；否则 `Q_REACH` 内的墙（不近于 `HOOK_MIN`）。
pub fn trace(g: &Grid, from: (f64, f64), dir: (f64, f64), foes: &[(f64, f64)]) -> Hit {
    let wall = g.first_wall(from, dir, Q_REACH);
    let limit = wall.unwrap_or(Q_REACH);
    let hits_unit = foes.iter().any(|f| {
        let v = (f.0 - from.0, f.1 - from.1);
        let along = v.0 * dir.0 + v.1 * dir.1;
        let across = (v.0 * dir.1 - v.1 * dir.0).abs();
        along > 0.0 && along <= limit && across <= Q_RAD + BODY
    });
    if hits_unit {
        return Hit::Unit;
    }
    match wall {
        Some(t) if t >= HOOK_MIN => {
            let stop = t - GAP;
            Hit::Wall((from.0 + dir.0 * stop, from.1 + dir.1 * stop), t)
        }
        _ => Hit::Nothing,
    }
}

fn unit(v: (f64, f64)) -> Option<(f64, f64)> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

// ===================== 小工具 =====================

fn has_cc(sim: &StableSim<'_>, id: usize, kinds: &[CcKindV1]) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
    })
}

/// 拉不了的状态：硬控、正被别人强制位移。
const NO_PULL: [CcKindV1; 7] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::BlockMoveSkill,
];

fn alive_at(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() {
        return None;
    }
    let (x, y) = e.pos();
    Some((x as f64, y as f64))
}

fn input_pos(input: &InputTargetV1) -> Option<(f64, f64)> {
    (input.kind == InputTargetKindV1::Pos.code()).then_some((input.x as f64, input.y as f64))
}

fn input_dir(input: &InputTargetV1) -> Option<(f64, f64)> {
    (input.kind == InputTargetKindV1::Dir.code()).then(|| unit((input.dir_x as f64, input.dir_y as f64))).flatten()
}

fn queue(sim: &mut StableSim<'_>, stage: &str, caster: usize, input: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{stage}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
}

fn upos(p: (f64, f64)) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

// ===================== 拉的途中 =====================

/// 一次拉：终点、上一 tick 他在哪（看宿主有没有挪他）、看到第几 tick 为止、自己走了几步。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Watch {
    pub to: (f64, f64),
    pub last: (f64, f64),
    pub until: usize,
    pub steps: usize,
}

/// 拉的途中按（这份模拟的编号、他）记在这里。2026-11-04 修（11-03 夜里的日志复查：希尔科的畸变体、格雷福斯的撞墙标记是
/// 同一个原因）：`watch` 以前把起点塞在排队输入的 dir_x / dir_y、截止 tick 塞在 target_id 里，排队只留下位置的 x、y——
/// 截止读回来是 0，`watch` 第一 tick 就收手，宿主没挪他时从来没自己走过一步（钩墙本身靠强制位移，照样拉过去了：日志里
/// 21 次 HOOK 都有 PULL）。
static WATCHES: LazyLock<Mutex<HashMap<(u64, usize), Watch>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// 每份模拟的诺提勒斯一个编号（加里奥附加包的 `SIM_TAG`）：这一招没有被动，第一次拉墙时由效果抽一个，挂在他身上（buff
/// `league_nautilus_sim:<编号>`，没有数值、没有画面；死了再出生是新的单位，下次拉墙再抽）。服务器同一局并排跑的两份预模拟
/// 实体编号、tick 都一样，编号各是各的。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
const SIM_TAG: &str = "league_nautilus_sim:";

/// The number hung on him in this sim (0: none).
pub fn sim_tag(names: impl Iterator<Item = String>) -> u64 {
    names.into_iter().find_map(|n| n.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())).unwrap_or(0)
}

fn sim_of(sim: &StableSim<'_>, me: usize) -> u64 {
    sim.get_entity(me).map_or(0, |e| sim_tag((0..e.buff_count()).filter_map(|i| e.buff_at(i))
        .map(|b| b.name().to_string())))
}

/// His number, drawn and hung on him at this unit's first pull.
fn sim_no(sim: &mut StableSim<'_>, me: usize) -> u64 {
    let no = sim_of(sim, me);
    if no != 0 {
        return no;
    }
    let no = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
    sim.add_buff(me, &BuffV1::named(&format!("{SIM_TAG}{no}")));
    no
}

/// A pull begins: watched from now on. A watch's row goes when it ends (there, time up, held, dead - his death mid-pull
/// ends it on the next tick); only a sim that ended mid-pull leaves one. 0.1.4 cleared the whole table past 4096 rows:
/// every sim running beside it lost its pull's watch at another tick than its twin (no steps of his own there) (0.1.5).
pub fn start_watch(row: (u64, usize), w: Watch) {
    let mut rows = WATCHES.lock().unwrap_or_else(|e| e.into_inner());
    rows.insert(row, w);
}

/// What the watch does this tick.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Watching {
    /// There, or the time is up: the watch ends.
    Over,
    /// The host moves him: nothing to do.
    Moving,
    /// The host did not move him since the last tick: a step of his own to this point.
    Step((f64, f64)),
}

/// The watch's call for him standing at `here` on tick `tick`.
pub fn watching(w: &Watch, here: (f64, f64), tick: usize) -> Watching {
    let d = dist(here, w.to);
    if d <= ARRIVE || tick > w.until {
        return Watching::Over;
    }
    if dist(w.last, here) >= 1.0 {
        return Watching::Moving;
    }
    let s = Q_DASH.min(d);
    Watching::Step((here.0 + (w.to.0 - here.0) / d * s, here.1 + (w.to.1 - here.1) / d * s))
}

// ===================== 三步 =====================

/// 锚飞出去的那一 tick（主包 Q 的 `q_at`）：看路线上先碰到敌人还是墙。
fn hook(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let Some(here) = alive_at(sim, caster) else { return };
    let Some(dir) = input_dir(&input).or_else(|| {
        // a Targeting cast hands a unit: aim at it
        (input.kind == InputTargetKindV1::Target.code())
            .then(|| alive_at(sim, input.target_id))
            .flatten()
            .and_then(|t| unit((t.0 - here.0, t.1 - here.1)))
    }) else {
        wlog(format!("{} hook: no direction in the input (kind {})", head(sim, caster), input.kind));
        return;
    };
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let mut foes = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if !u.is_champion() || !u.is_alive() {
            continue;
        }
        let (x, y) = u.pos();
        if u.team() != team && u.is_targetable() {
            foes.push((x as f64, y as f64));
        }
    }
    let grids = Grid::builtin();
    let Some(gi) = current(&grids, &unit_points(sim)) else { return };
    match trace(&grids[gi], here, dir, &foes) {
        Hit::Wall(stop, t) => {
            let flight = (t / Q_SPEED).ceil() as usize;
            wlog(format!("{} HOOK the wall: from {} toward ({:.2},{:.2}), wall at {:.0}, pulled to {} in {} ticks", head(sim, caster), pt(here), dir.0, dir.1, t, pt(stop), flight));
            queue(sim, "pull", caster, InputTargetV1::pos(stop.0.round().max(0.0) as u64, stop.1.round().max(0.0) as u64), flight);
        }
        Hit::Unit => {}
        Hit::Nothing => {}
    }
}

/// 锚咬在墙上：拉过去，返还一半冷却。
fn pull(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let (Some(to), Some(here)) = (input_pos(&input), alive_at(sim, caster)) else { return };
    if has_cc(sim, caster, &NO_PULL) {
        wlog(format!("{} pull: held by crowd control, stays", head(sim, caster)));
        return;
    }
    let d = dist(here, to);
    let ticks = (d / Q_DASH).ceil().max(1.0);
    let mut anim = CcV1::of_kind(CcKindV1::Animation, Q_ANIM.max(ticks as u64));
    anim.set_name("skill_pull");
    sim.apply_cc(caster, &anim);
    let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    mv.dx = (to.0 - here.0).round() as i64;
    mv.dy = (to.1 - here.1).round() as i64;
    mv.speed = (d / ticks).ceil() as u64;
    sim.apply_cc(caster, &mv);
    let mut refund = BuffV1::timed(&nt("q_refund"), REFUND_T);
    refund.skill_cooldown_mult = REFUND;
    refund.ult_cooldown_mult = -REFUND;   // the engine caps R with skill + ult: the refund is Q's (and W+E's) only
    sim.entity_remove_buff(caster, &nt("q_refund"));
    sim.add_buff(caster, &refund);
    let at_wall = InputTargetV1::pos(to.0.round().max(0.0) as u64, to.1.round().max(0.0) as u64);
    sim.play_sfx(&nt("q_wall"), caster, &at_wall);
    sim.play_view_effect(&nt("q_hit"), caster, &at_wall, 0, 0, 0);
    wlog(format!("{} PULL to the wall {} -> {} ({:.0}, {} ticks), Q cooldown halved", head(sim, caster), pt(here), pt(to), d, ticks));
    // where he started: the watch tells whether the host moved him (its row, not the queued input: 0.1.4)
    let row = (sim_no(sim, caster), caster);
    start_watch(row, Watch { to, last: here, until: sim.tick() + WATCH_MAX, steps: 0 });
    queue(sim, "watch", caster, upos(to), 1);
}

/// 拉的每一 tick：到了就停；宿主没挪他（撞到别的东西停了）就自己走一步。
fn watch(sim: &mut StableSim<'_>, caster: usize, _: InputTargetV1) {
    let row = (sim_of(sim, caster), caster);
    let Some(mut w) = WATCHES.lock().unwrap_or_else(|e| e.into_inner()).get(&row).copied() else { return };
    let end = |sim: &StableSim<'_>, w: &Watch, why: &str| {
        WATCHES.lock().unwrap_or_else(|e| e.into_inner()).remove(&row);
        if w.steps > 0 {
            wlog(format!("{} WATCH: {} steps of his own (the host did not move him), {why}", head(sim, caster), w.steps));
        }
    };
    let Some(here) = alive_at(sim, caster) else { return end(sim, &w, "dead") };
    if has_cc(sim, caster, &NO_PULL[..6]) {
        return end(sim, &w, "held by crowd control");
    }
    match watching(&w, here, sim.tick()) {
        Watching::Over => return end(sim, &w, if dist(here, w.to) <= ARRIVE { "there" } else { "time up" }),
        Watching::Moving => {}
        // 被放逐（巴德的 R 之类，不可选中）时不挪他：游戏 0.6.4 起放逐中的单位不动，宿主的强制位移也停下
        Watching::Step(next) => {
            if sim.get_entity(caster).is_some_and(|e| e.is_targetable()) {
                sim.entity_set_pos(caster, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64);
                w.steps += 1;
            }
        }
    }
    // where he stood this tick (before his own step): the next tick tells whether the host moved him
    WATCHES.lock().unwrap_or_else(|e| e.into_inner()).insert(row, Watch { last: here, ..w });
    queue(sim, "watch", caster, upos(w.to), 1);
}

// ===================== 注册 =====================

#[derive(Clone, Copy)]
enum Step {
    Hook,
    Pull,
    Watch,
}

// ===================== 排山倒海：每个英雄各算 =====================

/// 这一下定不定：这个英雄没在 `P_REST` 里（`rested` 否），或 Q 的连招（`q_land`）。
pub fn staggers(rested: bool, q_land: bool) -> bool {
    q_land || !rested
}

static STAGGER_LINES: AtomicU64 = AtomicU64::new(0);

fn stagger(sim: &mut StableSim<'_>, naut: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    let has = |sim: &StableSim<'_>, id: usize, name: &str| {
        sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
    };
    if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
        return;
    }
    let rested = has(sim, target, P_REST);
    let q_land = has(sim, naut, &nt("q_land"));
    let go = staggers(rested, q_land);
    if go {
        sim.entity_remove_buff(target, P_REST);
        sim.add_buff(target, &BuffV1::timed(P_REST, P_REST_T));
        sim.entity_remove_buff(naut, P_GO);
        sim.add_buff(naut, &BuffV1::timed(P_GO, P_GO_T));
    }
    let n = STAGGER_LINES.fetch_add(1, Ordering::Relaxed) + 1;
    let shown = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    if shown || n <= 40 || n % 100 == 0 {
        let what = if !go { "rested, no root" } else if rested { "the Q combo: rooted though rested" } else { "rooted" };
        wlog(format!("{} STAGGER #{n} on #{target}: {what}", head(sim, naut)));
    }
}

struct Stagger;

impl StableEffectType for Stagger {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        stagger(sim, caster, input);
    }
}

struct Stage(Step);

impl StableEffectType for Stage {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        match self.0 {
            Step::Hook => hook(sim, caster, input),
            Step::Pull => pull(sim, caster, input),
            Step::Watch => watch(sim, caster, input),
        }
    }
}

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Nautilus's Dredge Line hooks walls: pulled to the wall, half the cooldown back; an enemy champion before the wall is the data's catch; Staggering Blow rests on each champion) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:hook"), Stage(Step::Hook));
    module.add_native_effect(format!("{ID}:pull"), Stage(Step::Pull));
    module.add_native_effect(format!("{ID}:watch"), Stage(Step::Watch));
    module.add_native_effect(STAGGER, Stagger);
    host.log(LogLevel::Info, "league_nautilus v1 loaded (Nautilus's Dredge Line hooks walls).");
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

    fn at(cx: f64, cy: f64) -> (f64, f64) {
        (cx * CELL, cy * CELL)
    }

    /// 一堵竖墙（第 5 列，第 2-7 行）。
    fn wall() -> Grid {
        let mut rows = vec![".........."; 10];
        for r in rows.iter_mut().take(8).skip(2) {
            *r = ".....#....";
        }
        Grid::from_rows(&rows)
    }

    #[test]
    fn the_anchor_bites_the_wall_ahead() {
        let g = wall();
        let from = at(3.0, 4.5);
        match trace(&g, from, (1.0, 0.0), &[]) {
            Hit::Wall(stop, t) => {
                assert!((t - (5.0 * CELL - from.0)).abs() <= STEP + 1.0, "wall at {t}");
                assert!(stop.0 < 5.0 * CELL && !g.is_wall(stop.0, stop.1));
                assert!((stop.1 - from.1).abs() < 1.0);
            }
            h => panic!("{h:?}"),
        }
    }

    #[test]
    fn the_main_pack_anchor_passes_minions_again() {
        // 0.1.7: the copy's anchor targets enemy champions only (q_block 0), so only champions before the wall are
        // the data's catch - `hook` looks at champions alone (u.is_champion())
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_nautilus.py");
        let src = std::fs::read_to_string(path).expect("build_nautilus.py");
        assert!(src.contains("\"q_block\": 0,"), "build_nautilus.P's q_block is not 0: hook must count minions again");
    }

    #[test]
    fn a_champion_before_the_wall_is_hooked_by_the_main_pack() {
        let g = wall();
        let from = at(3.0, 4.5);
        assert_eq!(trace(&g, from, (1.0, 0.0), &[at(4.0, 4.6)]), Hit::Unit);
        // a champion behind him, or off the line, or past the wall: the wall
        assert!(matches!(trace(&g, from, (1.0, 0.0), &[at(2.0, 4.5)]), Hit::Wall(..)));
        assert!(matches!(trace(&g, from, (1.0, 0.0), &[at(4.0, 6.5)]), Hit::Wall(..)));
        assert!(matches!(trace(&g, from, (1.0, 0.0), &[at(6.5, 4.5)]), Hit::Wall(..)));
    }

    #[test]
    fn no_wall_in_reach_or_too_close() {
        let g = wall();
        assert_eq!(trace(&g, at(2.0, 9.0), (1.0, 0.0), &[]), Hit::Nothing);
        assert_eq!(trace(&g, at(4.9, 4.5), (1.0, 0.0), &[]), Hit::Nothing);
        // the wall beyond Q's reach
        assert_eq!(trace(&g, at(0.5, 4.5), (1.0, 0.0), &[]), Hit::Nothing);
    }

    #[test]
    fn the_moba_map_has_its_ninety_wall_cells() {
        assert_eq!(Grid::builtin()[0].walls(), 90);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_nautilus.py");
        let src = std::fs::read_to_string(path).expect("build_nautilus.py");
        for (key, v) in [("q_reach", Q_REACH), ("q_speed", Q_SPEED), ("q_rad", Q_RAD), ("q_dash", Q_DASH)] {
            assert!(src.contains(&format!("\"{key}\": {}", v as u64)), "{key} is not {v} in build_nautilus.P");
        }
        assert!(src.contains(&format!("\"q_anim\": {Q_ANIM}")));
        assert!(src.contains(&format!("\"p_cd\": {P_REST_T}")), "p_cd is not P_REST_T in build_nautilus.P");
    }

    /// League: once per target every 6 s; Q's combo (the hooked champion rooted by the next attack) whatever its rest.
    #[test]
    fn staggering_blow_rests_on_each_champion() {
        assert!(staggers(false, false));
        assert!(!staggers(true, false));
        assert!(staggers(true, true));
        assert!(staggers(false, true));
        for x in [P_REST, P_GO] {
            assert!(x.len() <= BUFF_NAME_CAP, "{x}");
        }
    }

    /// The copy: the champion twin asks the add-on, the root reads `P_GO` (in the tick and a tick later), no rest on him.
    #[test]
    fn the_copy_roots_by_the_targets_rest() {
        let copy = include_str!("../override/league_nautilus.data_champion");
        assert_eq!(copy.matches(&format!("\"effect_ref\": \"{STAGGER}\"")).count(), 1);
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{P_GO}\"")).count(), 2);
        assert!(!copy.contains("\"league_nautilus_p_cd\""), "the copy still rests on him");
        assert!(copy.contains("\"type\": \"Bind\""), "the root is the data's");
    }

    #[test]
    fn the_names_fit() {
        for x in ["q_refund", "q_wall", "q_hit"] {
            assert!(nt(x).len() <= BUFF_NAME_CAP);
        }
        assert!(format!("{SIM_TAG}{}", u64::MAX).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn each_sim_finds_its_own_number() {
        let names = |v: &[&str]| v.iter().map(|s| s.to_string()).collect::<Vec<_>>().into_iter();
        assert_eq!(sim_tag(names(&["league_nautilus_q_refund", "league_nautilus_sim:12"])), 12);
        assert_eq!(sim_tag(names(&["league_nautilus_q_refund"])), 0);
    }

    #[test]
    fn the_watch_steps_only_where_the_host_left_him() {
        // 11-03 night: the deadline packed into the queued input came back 0 and the watch ended on its first tick;
        // from its row it runs to the wall
        let to = (100_000.0, 50_000.0);
        let w = Watch { to, last: (60_000.0, 50_000.0), until: 160, steps: 0 };
        // the host moved him since the last tick: nothing to do
        assert_eq!(watching(&w, (62_500.0, 50_000.0), 101), Watching::Moving);
        // he stands where he stood: a step of Q_DASH toward the wall
        assert_eq!(watching(&w, (60_000.0, 50_000.0), 101), Watching::Step((60_000.0 + Q_DASH, 50_000.0)));
        // the last step stops on the spot; there, or past the deadline: over
        let near = Watch { last: (97_600.0, 50_000.0), ..w };
        assert_eq!(watching(&near, (97_600.0, 50_000.0), 101), Watching::Step(to));
        assert_eq!(watching(&w, (99_000.0, 50_000.0), 101), Watching::Over);
        assert_eq!(watching(&w, (60_000.0, 50_000.0), 161), Watching::Over);
        // twin presims (Nautilus #27 in both) keep their own rows
        start_watch((900_001, 27), w);
        start_watch((900_002, 27), Watch { until: 999, ..w });
        let rows = WATCHES.lock().unwrap();
        assert_eq!((rows[&(900_001, 27)].until, rows[&(900_002, 27)].until), (160, 999));
    }

    #[test]
    fn a_new_pull_never_clears_the_other_sims_watches() {
        // 0.1.4 cleared the whole table past 4096 rows: the sims running beside it lost their pulls' watches at another
        // tick than their twins
        let w = Watch { to: (1.0, 1.0), last: (0.0, 0.0), until: 50, steps: 0 };
        for no in 1..=5_000u64 {
            start_watch((no, 1_000_000), w);
        }
        start_watch((5_001, 1_000_000), w);
        let rows = WATCHES.lock().unwrap();
        assert!((1..=5_001u64).all(|no| rows.contains_key(&(no, 1_000_000))));
    }
}
