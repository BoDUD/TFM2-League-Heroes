//! 诺提勒斯附加包：Q「疏通航道」钩墙（用户选的附加包：「做钩墙附加包」）。
//!
//! 主包是纯数据，读不到地图的墙：主包里锚飞出去只钩英雄，没钩到就落空。英雄联盟的疏通航道钩到墙上会把诺提勒斯拉到墙边，
//! 并返还一半冷却。`mod.override_info` 把主包的诺提勒斯换成 `override/` 里的副本（tools/kit/build_nautilus.py 的
//! native=1）：数据和主包一样，锚飞出去的那一 tick 多调一次本包的原生效果 `league_nautilus:hook`（输入是 Q 的方向）。
//!
//! - `hook`：沿 Q 的方向从他脚下往前找，`q_reach` 内先碰到敌方英雄（离锚的路线 `q_rad` + 身体以内）就什么都不做——主包的锚会
//!   钩住他；先碰到墙（引擎的碰撞墙，5v5 地图野区的 90 格，卡蜜尔附加包的 `maps.rs`）就按锚飞到墙的时间排一个 `pull`。
//! - `pull`：锚咬在墙上：他被拉到墙边（强制位移，速度 `q_dash`，停在离墙 `GAP` 处），播主包的 skill_pull 动作、钩墙音效和
//!   钩中的水花，Q 冷却返还一半（`skill_cooldown_mult` +100 的 3 tick buff：剩下的冷却封顶到冷却时间的一半；W+E 若剩得更多
//!   也一起封顶，引擎没有只给一个技能的字段）。之后每 tick 看一次（`watch`），宿主没挪他就逐 tick 自己走一步。
//! - 被硬控、死了就不拉。比 `HOOK_MIN` 近的墙不钩（拉不出样子）。
//!
//! 数字从英雄数据的 `passive.params` 来不了（这一招没有被动），所以和主包 P 表的值写在这里（`Q_*`），主包改了这里一起改
//! （`tests::the_numbers_match_the_kit` 读主包的数据核对）。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nautilus.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_nautilus";

/// 主包诺提勒斯的名字（动作、画面、音效都以它开头）。
fn nt(x: &str) -> String {
    format!("league_nautilus_{x}")
}

// ===================== 数值（主包 build_nautilus.P） =====================

/// 墙格的边长（世界单位）。
pub const CELL: f64 = 32_000.0;
/// 锚飞多远、多快、多宽（q_reach、q_speed、q_rad）。
pub const Q_REACH: f64 = 85_000.0;
pub const Q_SPEED: f64 = 6_000.0;
pub const Q_RAD: f64 = 10_000.0;
/// 拉过去的速度（q_dash）和动作时长（q_anim）。
pub const Q_DASH: f64 = 2_500.0;
pub const Q_ANIM: u64 = 24;
/// 敌方英雄的身体半径（够得着锚的路线就算会被钩住）。
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

/// 锚沿路线先碰到的是什么：敌方英雄（主包的锚会钩他）、墙（`Some(停点, 锚飞的距离)`），或什么都没有。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Hit {
    Champion,
    Wall((f64, f64), f64),
    Nothing,
}

/// 沿 Q 的方向：`foes` 里离路线 `Q_RAD + BODY` 以内、在墙前的敌方英雄先被钩；否则 `Q_REACH` 内的墙（不近于 `HOOK_MIN`）。
pub fn trace(g: &Grid, from: (f64, f64), dir: (f64, f64), foes: &[(f64, f64)]) -> Hit {
    let wall = g.first_wall(from, dir, Q_REACH);
    let limit = wall.unwrap_or(Q_REACH);
    let hits_champion = foes.iter().any(|f| {
        let v = (f.0 - from.0, f.1 - from.1);
        let along = v.0 * dir.0 + v.1 * dir.1;
        let across = (v.0 * dir.1 - v.1 * dir.0).abs();
        along > 0.0 && along <= limit && across <= Q_RAD + BODY
    });
    if hits_champion {
        return Hit::Champion;
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

// ===================== 三步 =====================

/// 锚飞出去的那一 tick（主包 Q 的 `q_at`）：看路线上先碰到英雄还是墙。
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
    let mut champs = Vec::new();
    let mut foes = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if !u.is_champion() || !u.is_alive() {
            continue;
        }
        let (x, y) = u.pos();
        champs.push((x as f64, y as f64));
        if u.team() != team && u.is_targetable() {
            foes.push((x as f64, y as f64));
        }
    }
    let grids = Grid::builtin();
    let Some(gi) = current(&grids, &champs) else { return };
    match trace(&grids[gi], here, dir, &foes) {
        Hit::Wall(stop, t) => {
            let flight = (t / Q_SPEED).ceil() as usize;
            wlog(format!("{} HOOK the wall: from {} toward ({:.2},{:.2}), wall at {:.0}, pulled to {} in {} ticks", head(sim, caster), pt(here), dir.0, dir.1, t, pt(stop), flight));
            queue(sim, "pull", caster, InputTargetV1::pos(stop.0.round().max(0.0) as u64, stop.1.round().max(0.0) as u64), flight);
        }
        Hit::Champion => {}
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
    sim.entity_remove_buff(caster, &nt("q_refund"));
    sim.add_buff(caster, &refund);
    let at_wall = InputTargetV1::pos(to.0.round().max(0.0) as u64, to.1.round().max(0.0) as u64);
    sim.play_sfx(&nt("q_wall"), caster, &at_wall);
    sim.play_view_effect(&nt("q_hit"), caster, &at_wall, 0, 0, 0);
    wlog(format!("{} PULL to the wall {} -> {} ({:.0}, {} ticks), Q cooldown halved", head(sim, caster), pt(here), pt(to), d, ticks));
    let mut follow = input;
    follow.dir_x = here.0.round() as i64;   // where he started: the watch tells whether the host moved him
    follow.dir_y = here.1.round() as i64;
    follow.target_id = sim.tick() + WATCH_MAX;
    queue(sim, "watch", caster, follow, 1);
}

/// 拉的每一 tick：到了就停；宿主没挪他（撞到别的东西停了）就自己走一步。
fn watch(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let (Some(to), Some(here)) = (input_pos(&input), alive_at(sim, caster)) else { return };
    let last = (input.dir_x as f64, input.dir_y as f64);
    let d = dist(here, to);
    if d <= ARRIVE || sim.tick() > input.target_id || has_cc(sim, caster, &NO_PULL[..6]) {
        return;
    }
    if dist(last, here) < 1.0 {
        let s = Q_DASH.min(d);
        let next = (here.0 + (to.0 - here.0) / d * s, here.1 + (to.1 - here.1) / d * s);
        sim.entity_set_pos(caster, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64);
    }
    let mut follow = input;
    follow.dir_x = here.0.round() as i64;
    follow.dir_y = here.1.round() as i64;
    queue(sim, "watch", caster, follow, 1);
}

// ===================== 注册 =====================

#[derive(Clone, Copy)]
enum Step {
    Hook,
    Pull,
    Watch,
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
        "=== {ID} v1 (Nautilus's Dredge Line hooks walls: pulled to the wall, half the cooldown back) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:hook"), Stage(Step::Hook));
    module.add_native_effect(format!("{ID}:pull"), Stage(Step::Pull));
    module.add_native_effect(format!("{ID}:watch"), Stage(Step::Watch));
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
    fn a_champion_before_the_wall_is_hooked_by_the_main_pack() {
        let g = wall();
        let from = at(3.0, 4.5);
        assert_eq!(trace(&g, from, (1.0, 0.0), &[at(4.0, 4.6)]), Hit::Champion);
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
    }

    #[test]
    fn the_names_fit() {
        for x in ["q_refund", "q_wall", "q_hit"] {
            assert!(nt(x).len() <= BUFF_NAME_CAP);
        }
    }
}
