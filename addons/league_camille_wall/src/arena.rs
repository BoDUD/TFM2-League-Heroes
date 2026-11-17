//! 大招场地里不走出去（用户 2026-10-26：「卡密尔的R三秒有点太短了 而且现在有时候都没3秒」「你要确保英雄走不出去」）：
//! AI 钩子 `league_camille_wall:arena`。
//!
//! 主包的海克斯最后通牒：场地 `ARENA_R` 内，目标走出去就被拉回她身边；她自己走出去场地就结束（英雄联盟的规则，也是因为
//! 她在外面时把目标拉向她会把目标拉出场地）。游戏的 AI 常让她追出去、撤出去，场地于是不到时间就没了。本钩子在她身上有
//! 主包的 `league_camille_r_on` 时，第一次看到就把她的位置记成场地中心（场地落在她落地的地方）；之后 AI 要她**走到**离中心
//! `KEEP` 以外的地方、或**回城**，就改成普攻被锁的目标（身上有 `league_camille_r_mark` 的敌方英雄，没有就场地里最近的
//! 敌方英雄）。场地里没有能打的敌方英雄就不管 AI（0.4.9，用户 2026-10-28「这两个顺带一起改了」：以前是走回中心，
//! 目标死了、跑了以后她在空场地里来回走，E 的攻速期间也不去打别人）。被击退、拉走出场地照旧结束（那是对面的本事）。
//!
//! 被锁的目标也出不去（[`update`] 里的 hold，她的被动每 tick 跑）：主包把人拉回来的判断问的是「场地里有没有敌方英雄」
//! （哪个都算），场地里站着别的敌人时目标走出去也不拉（经典模拟：一次 140 tick 的场地里目标只被拉了 4 下，走到离中心
//! 35000）；本包认场地的标记（`league_camille_r_mark`），目标离中心超过 `HOLD_E` 就把他放回 `HOLD_E` 处。
//!
//! 0.4.5（用户 2026-10-26 打了一局：「青钢影的大招还是没修好吧」——场地还是太短、敌人还能走出去）：场地的画面
//! （`league_camille_big` 的 `r_zone`）是横 72、纵 50 游戏像素的椭圆（1 像素 1000），判断却是半径 30000 的圆：她站在
//! 画面左右两边（30000–36000）场地就结束了，目标被放回的 27000 在画面上下两边（25000）的外面。现在都照画面的椭圆
//! （`SEMI_X` x `SEMI_Y`）：主包的 `r_area` 半径改成 `SEMI_X`（她在画面里场地就不结束），本包让她待在椭圆的 `KEEP_E`
//! 以内、把目标放回椭圆的 `HOLD_E` 处（[`reach`]：到中心的距离按椭圆折算，1 = 画面的边）。
//!
//! 0.4.12（用户 2026-11-17：「顺便查一下卡密尔的大招也有bug吧 怎么敌人走的出去？」「卡密尔离开磁场后 磁场也不消失？」）：
//! - **画面跟着场地走**：主包站着的地面是一个 240 tick 的区域（`r_floor`），区域的画面停不下来——场地提前结束（她被击退
//!   出去、残血用 E 钩走、阵亡）时地面照样留满 4 秒，里面谁也不拉了，看着就是「敌人走出了场地」。本包的副本去掉那个
//!   区域的画面（区域留着：它每 tick 给她挂主包拉人要的 `r_vis`），改由被动在场地开着（她活着、身上有 `r_on`）时每
//!   `FLOOR_STEP` tick 在中心放一段投射物画面（[`draw_floor`]：`league_camille_r_floor_<k>`，主包 `league_camille_big`
//!   的 `r_zone_<k>` = `r_zone` 循环的第 k 帧，同一张图、同样转半圈），场地一结束就不再放，最多 `FLOOR_STEP` tick 后地面就没了；
//!   目标脚下的标记（主包 30 tick 一段，原来比场地多留最多半秒）也在场地结束时摘掉。
//! - **AI 指着场地外的人出手也算走出去**：以前只管「走到哪」和回城，AI 让她普攻、放技能打场地外够不着的人（她得先走过去，
//!   [`Want::Act`]）时照旧让她走，场地就提前没了。现在这也改成打被锁的目标（规则同上，场地里没人可打照旧不管）。
//! - **日志**：每个场地一行 `ARENA END`（多久、为什么结束：满时间、她离开（走出去 / 被挪走 / 自己的 E / 被放逐）、阵亡；
//!   拉回几次、地面放了几段），看的那场比赛另有 `ARENA START` 和每一次拉回、每一次 AI 被改。
//!
//! 0.4.13（用户 2026-11-17：「青钢影的bug没修好啊」）：看的那场比赛里，塔姆在场地开了 71 tick 时吞下被锁的希瓦娜（放逐），
//! 带着她走出场地，地面还亮着；她在肚子里谁也打不着，卡蜜尔的 AI 当场地里没人可打，220 tick 时也走了出去。英雄联盟里被锁的
//! 目标被吞下（或被拖走），大招当场结束：被动看到被锁的目标被放逐（活着、不可选中），就摘掉她身上主包的 `r_on`，场地连同
//! 地面当场结束（[`swallowed`]）；被放逐的人也不再被拉回。
//!
//! 0.4.14（用户 2026-11-17：「还是有bug啊」「卡密尔离开了磁场也一直在 这个问题也没修好」）：**场地就是它的画面**。主包在她
//! 走出 `r_area` 时结束场地，那是半径 36000 的圆：和画面一样宽，上下却比画面（纵向 25000）各多 11000，她站在地面的上方、
//! 下方，看着已经出了场地，场地却还开着（看的那场她到过画面的 1.54）。现在她站到画面的边外连续 `OUT_T` tick，本包就摘掉
//! `r_on`，场地连同地面结束。她场地里不再出 E（残血逃跑也不出，见 lib.rs）。
//!
//! 判断在 [`call`]、[`clamp`]、[`floor_frame`]、[`end_reason`]（纯计算、单元测试）。

use mod_api_stable::*;

use std::sync::atomic::{AtomicUsize, Ordering};

use super::{head, watched, wlog, ID};

/// 排在 league_ult_press（100）之后。
pub const PRIORITY: i32 = 120;
/// 场地画面的椭圆（`r_zone` 不透明的部分：横 72、纵 50 游戏像素，测试核对图）：横、纵半径。
pub const SEMI_X: f64 = 36_000.0;
pub const SEMI_Y: f64 = 25_000.0;
/// 主包场地的半径（`league_camille_r_area`，她在里面场地才不结束）：画面最宽处。
pub const ARENA_R: f64 = SEMI_X;
/// 她的走路目的地在椭圆的这么多以外就算要走出去（留出身体和一步的余量）。
pub const KEEP_E: f64 = 0.7;

const R_ON: &str = "league_camille_r_on";
const R_MARK: &str = "league_camille_r_mark";

pub type Pt = (f64, f64);

/// How long the main pack's arena lasts (`league_camille_r_on`, 4 s).
pub const ARENA_TICKS: usize = 240;

/// The arena's centre and the tick it was last looked at.
pub type Slot = Option<(Pt, usize)>;

/// The arena's centre: where she stands now if this is a new arena - nothing remembered, the last look an arena's length
/// ago or more (the hook was not called in between), or the clock went back (another match) - else the remembered one.
pub fn centre_of(slot: &mut Slot, me: Pt, tick: usize) -> Pt {
    let c = match *slot {
        Some((c, t)) if tick >= t && tick - t < ARENA_TICKS => c,
        _ => me,
    };
    *slot = Some((c, tick));
    c
}

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// How far `p` is from the centre on the arena's picture: 1 on the ellipse's edge, 0.5 halfway, past 1 outside.
pub fn reach(centre: Pt, p: Pt) -> f64 {
    (((p.0 - centre.0) / SEMI_X).powi(2) + ((p.1 - centre.1) / SEMI_Y).powi(2)).sqrt()
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Want {
    /// a walk to this point
    Move(Pt),
    Return,
    /// 0.4.12: an attack or a skill on the unit standing at `at`, done from `reach` of it (the action's range and both
    /// bodies, [`act_reach`]) - farther, she walks to it first
    Act { at: Pt, reach: f64 },
    Other,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub marked: bool,
}

/// Is a walk from `me` to `to` a walk out of the arena: past `KEEP_E` on the picture and farther out than she is?
fn outward(centre: Pt, me: Pt, to: Pt) -> bool {
    reach(centre, to) > KEEP_E && reach(centre, to) > reach(centre, me)
}

/// Where she stops walking toward a unit at `at` to act on it from `reach` (None: she is in reach, she does not walk).
pub fn walk_end(me: Pt, at: Pt, reach: f64) -> Option<Pt> {
    let d = dist(me, at);
    (d > reach).then(|| (at.0 + (me.0 - at.0) / d * reach, at.1 + (me.1 - at.1) / d * reach))
}

/// Does the AI's order take her out of the arena? A recall; a walk out ([`outward`]); an attack or skill on a unit
/// standing outside the arena that she must walk toward to reach, the walk out (to one inside she stays inside: the
/// ellipse is convex).
pub fn leaves(me: Pt, centre: Pt, want: Want) -> bool {
    match want {
        Want::Return => true,
        Want::Move(to) => outward(centre, me, to),
        Want::Act { at, reach: r } => {
            reach(centre, at) > 1.0 && walk_end(me, at, r).is_some_and(|to| outward(centre, me, to))
        }
        Want::Other => false,
    }
}

/// The enemy champion to attack instead of the AI's order (None: leave the order - nothing to attack, or not leaving).
pub fn call(me: Pt, centre: Pt, want: Want, foes: &[Foe]) -> Option<usize> {
    if !leaves(me, centre, want) {
        return None;
    }
    let inside = |f: &&Foe| reach(centre, f.at) <= 1.0;
    let target = foes
        .iter()
        .filter(|f| f.marked)
        .chain(foes.iter().filter(inside).filter(|f| !f.marked))
        .min_by(|a, b| (!a.marked).cmp(&!b.marked).then(dist(me, a.at).total_cmp(&dist(me, b.at))));
    target.map(|f| f.id)
}

/// Her actions' `range` in the add-on's copy (the main pack's: attack 25000, W 42000, R 35000; E's is `ENGAGE_R` there),
/// test `the_ranges_are_the_copys`.
pub fn range_of(kind: InputKindV1) -> Option<f64> {
    match kind {
        InputKindV1::Attack => Some(25_000.0),
        InputKindV1::Skill => Some(42_000.0),
        InputKindV1::Skill2 => Some(super::ENGAGE_R),
        InputKindV1::Ult => Some(35_000.0),
        _ => None,
    }
}

/// How close she must stand to act on a unit: an action's range counts both units' bodies (champion-data.md: a 30000-range
/// ult cast from up to 48700 centre to centre).
pub fn act_reach(range: f64, my_body: f64, its_body: f64) -> f64 {
    range + my_body + its_body
}

/// The marked target is kept this far on the picture at most ([`reach`]): inside the ellipse, a body short of its edge
/// (30600 across, 21250 up and down).
pub const HOLD_E: f64 = 0.85;

/// Where the target goes back to when it is past `e` on the picture ([`reach`]): the point at `e` on the line to it.
pub fn clamp(centre: Pt, at: Pt, e: f64) -> Option<Pt> {
    let r = reach(centre, at);
    (r > e && r > 0.0).then(|| (centre.0 + (at.0 - centre.0) * e / r, centre.1 + (at.1 - centre.1) * e / r))
}

/// `to` or, when that is in a wall or past the map's edge (the arena runs into terrain), the first open point on the way
/// from it to the centre, in 1000 steps (None: walls all the way - leave the target where it is).
pub fn open_ground(centre: Pt, to: Pt, solid: impl Fn(Pt) -> bool) -> Option<Pt> {
    let d = dist(centre, to);
    let steps = (d / 1_000.0).ceil().max(1.0) as usize;
    (0..=steps)
        .map(|i| {
            let k = 1.0 - i as f64 / steps as f64;
            (centre.0 + (to.0 - centre.0) * k, centre.1 + (to.1 - centre.1) * k)
        })
        .find(|p| !solid(*p))
}

// ===================== 地面（0.4.12） =====================

/// The floor's pieces: the add-on's copy binds `league_camille_r_floor_<k>` to `league_camille_big`'s `r_zone_<k>`, frame
/// k of the main pack's `r_zone` loop (tools/fix/camille_r_zone_frames.py; test `the_floor_pieces_are_r_zones_frames`).
pub const FLOOR_VIEW: &str = "league_camille_r_floor_";
pub const FLOOR_FRAMES: usize = 6;
/// Each piece stands this many ticks: one frame of the loop (83 ms; the loop is 500 ms, 30 ticks).
pub const FLOOR_STEP: usize = 5;

/// The frame of the loop drawn on `tick` of an arena that started on `start`: the main pack's floor started its loop
/// on the landing, 5 ticks a frame.
pub fn floor_frame(start: usize, tick: usize) -> usize {
    (tick.saturating_sub(start) / FLOOR_STEP) % FLOOR_FRAMES
}

/// One piece on the arena's centre `c`. A projectile's picture is turned to its direction and the sheet keeps the arena's
/// frames turned half round for the main pack's zone, which always points (-1, 0): the piece points (-1, 0) too. It flies
/// `FLOOR_STEP` + 1 steps of 1 unit, spawned a unit right of the centre: projectiles move after the passives, in the tick
/// they are spawned too, and one is removed on its last step's tick (league_azir's tether pieces, `TETHER_MOVES`), so
/// it lies on the centre after its first step, is drawn `FLOOR_STEP` ticks (0.005 px off the centre at most) and goes on
/// the tick the next piece comes.
pub fn floor_spec(me: usize, team: usize, c: Pt) -> ProjectileSpawnV1 {
    let (x, y) = (c.0.round().max(FLOOR_STEP as f64), c.1.round().max(0.0));
    ProjectileSpawnV1 {
        caster_id: me,
        team,
        x: x as u64 + 1,
        y: y as u64,
        radius: 1_000,
        speed: 1,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: x as u64 - FLOOR_STEP as u64,
        target_y: y as u64,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    }
}

/// Her pieces on the floor now (still flying, on the centre's line within a piece's flight).
fn pieces_on_floor(sim: &StableSim<'_>, me: usize, c: Pt) -> usize {
    let (x, y) = (c.0.round(), c.1.round());
    (0..sim.projectile_count())
        .filter_map(|i| sim.projectile_at(i))
        .filter(|p| p.caster_id == me && !p.is_end && (p.y as f64 - y).abs() <= 1.0)
        .filter(|p| (p.x as f64) <= x + 1.0 && (p.x as f64) >= x - FLOOR_STEP as f64 - 1.0)
        .count()
}

// ===================== 每个场地（她的被动跟着） =====================

/// Why an arena ended.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum End {
    /// `r_on` ran its 240 ticks
    TimeOut,
    /// she died (a dead Camille keeps `r_on`)
    Died,
    /// she left the arena (the main pack took `r_on` off her when she stood out of `r_area`): walking (the AI), moved
    /// (a knock-back, pull or dash on her), her own E, banished
    Walked,
    Moved,
    HerE,
    Banished,
    /// her marked target was banished - swallowed by Tahm Kench's Devour or the like (0.4.13): League ends the
    /// ultimatum then, so her passive takes the main pack's `r_on` off her
    Swallowed,
    /// her passive stopped seeing it (not called for a while: dead and gone, or the clock went back)
    Unseen,
}

/// Why the arena that started on `start` is not up on `tick`: she is dead; or `r_on` ran out (its 240 ticks, a tick
/// short when the passive first saw it a tick late); or she left - moved by something on her within `MOVED_T` ticks
/// (`moved`: the last tick a forced move or a knock-up held her, or her E pulled her), banished, else walking.
pub fn end_reason(alive: bool, start: usize, tick: usize, moved: Option<(usize, bool)>, banished: bool) -> End {
    if !alive {
        End::Died
    } else if tick.saturating_sub(start) + 2 >= ARENA_TICKS {
        End::TimeOut
    } else if let Some((_, her_e)) = moved.filter(|(t, _)| tick.saturating_sub(*t) <= MOVED_T) {
        if her_e {
            End::HerE
        } else {
            End::Moved
        }
    } else if banished {
        End::Banished
    } else {
        End::Walked
    }
}

/// She past the picture's edge this many ticks running ends the arena (0.4.14; the main pack's own r_area check ends it
/// about as fast once she is out of its circle).
pub const OUT_T: usize = 2;

/// A forced move this recent counts as what took her out (the main pack ends the arena 2 ticks after she is out).
pub const MOVED_T: usize = 6;

/// One arena while it is up, as her passive follows it.
#[derive(Clone, Debug)]
struct Up {
    /// her entity (the passive's `on_dead` gets the player only)
    me: usize,
    centre: Pt,
    start: usize,
    /// the last tick it was seen up
    seen: usize,
    /// the tick the next floor piece is due
    next: usize,
    pieces: usize,
    /// at a piece's due tick the one before was on the floor alone / gone / with another; a tick later two were left
    handover: [usize; 3],
    after: usize,
    refused: usize,
    /// put-backs of the marked target and the farthest out (on the picture) one started from
    held: usize,
    worst: f64,
    target: Option<usize>,
    /// her farthest reach on the picture, and the last tick something moved her (a forced move or knock-up: false; her
    /// own E: true)
    far: f64,
    moved: Option<(usize, bool)>,
    /// ticks running she has stood past the picture's edge (0.4.14)
    out: usize,
}

/// Her passive's arena: the one up now (each Camille's own).
#[derive(Clone, Debug, Default)]
pub struct Field {
    up: Option<Up>,
}

/// Every tick (her passive): the arena's start (`ARENA START`, the watched match), the hold on the marked target and the
/// floor while it is up, its end (`ARENA END`, every simulation: how long, why, what the hold and the floor did).
pub fn update(sim: &mut StableSim<'_>, me: usize, field: &mut Field) {
    let tick = sim.tick();
    // not seen last tick: a gap (her passive was not called - dead and gone) or the clock went back (another match)
    if field.up.as_ref().is_some_and(|u| tick < u.seen || tick > u.seen + 1) {
        if let Some(up) = field.up.take() {
            finish(sim, me, up, End::Unseen, tick, None);
        }
    }
    let Some(e) = sim.get_entity(me) else { return };
    let (alive, on, banished) = (e.is_alive(), has(&e, R_ON), !e.is_targetable());
    let (x, y) = e.pos();
    let at = (x as f64, y as f64);
    let team = e.team();
    let e_on = [super::PULL, super::DASH, super::WAIT].iter().any(|b| has(&e, b));
    let forced = (0..e.cc_count())
        .filter_map(|i| e.cc_at(i))
        .any(|c| c.kind == CcKindV1::ForceMove.code() || c.kind == CcKindV1::Airborne.code());
    if !alive || !on {
        if let Some(up) = field.up.take() {
            let why = end_reason(alive, up.start, tick, up.moved, banished);
            finish(sim, me, up, why, tick, Some(at));
        }
        return;
    }
    let up = field.up.get_or_insert_with(|| {
        if watched(sim) {
            wlog(format!("{} ARENA START at {}: the floor is this add-on's (a piece every {FLOOR_STEP} ticks while it is \
                          up)", head(sim, me), pt(at)));
        }
        Up { me, centre: at, start: tick, seen: tick, next: tick, pieces: 0, handover: [0; 3], after: 0, refused: 0,
             held: 0, worst: 0.0, target: None, far: 0.0, moved: None, out: 0 }
    });
    up.seen = tick;
    up.far = up.far.max(reach(up.centre, at));
    if e_on || forced {
        up.moved = Some((tick, e_on));
    }
    // League: the target swallowed (Tahm Kench's Devour) or dragged off ends the ultimatum at once (0.4.13). Here a
    // banish takes him off the map: the main pack's tether cannot mark him, the hold cannot put him back, and Tahm Kench
    // walked the marked Shyvana out under a floor that stood on.
    if up.target.is_some_and(|t| swallowed(sim, t)) {
        sim.entity_remove_buff(me, R_ON);
        if let Some(up) = field.up.take() {
            finish(sim, me, up, End::Swallowed, tick, Some(at));
        }
        return;
    }
    // 0.4.14: the arena is its picture. The main pack ends it when she is out of r_area, a 36000 circle - the picture's
    // width, but 11000 more than its height up and down - so she stood above or below the floor with the arena on (the
    // user 2026-11-17: 「卡密尔离开了磁场也一直在」). Past the picture's edge OUT_T ticks running ends it here.
    up.out = if reach(up.centre, at) > 1.0 { up.out + 1 } else { 0 };
    if up.out >= OUT_T {
        sim.entity_remove_buff(me, R_ON);
        if let Some(up) = field.up.take() {
            let why = end_reason(true, up.start, tick, up.moved, banished);
            finish(sim, me, up, why, tick, Some(at));
        }
        return;
    }
    hold(sim, me, team, up);
    draw_floor(sim, me, team, up, tick);
}

/// The arena's target banished (0.4.13): swallowed by Tahm Kench's Devour, or another banish (Bard's stasis too) - alive
/// and off the map (not targetable), where the main pack's tether cannot mark him and the hold cannot put him back.
pub fn swallowed(sim: &StableSim<'_>, t: usize) -> bool {
    sim.get_entity(t).is_some_and(|u| u.is_alive() && !u.is_targetable())
}

/// Her passive's `on_dead`: the arena up ends with her (`update` would see it too, if her passive still runs while she
/// lies dead).
pub fn died(sim: &mut StableSim<'_>, field: &mut Field) {
    if let Some(up) = field.up.take() {
        let me = up.me;
        let at = sim.get_entity(me).map(|e| {
            let (x, y) = e.pos();
            (x as f64, y as f64)
        });
        finish(sim, me, up, End::Died, sim.tick(), at);
    }
}

/// The champion carrying the arena's mark goes back to `HOLD_E` whenever he is past it - the main pack's pull asks "is an
/// enemy champion inside" (any one), so with two of them inside the target walked out.
fn hold(sim: &mut StableSim<'_>, me: usize, team: usize, up: &mut Up) {
    let c = up.centre;
    let mut moves = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        // a banished one (0.4.13) is off the map: not put back
        if u.team() == team || !u.is_alive() || !u.is_champion() || !u.is_targetable() || !has(&u, R_MARK) {
            continue;
        }
        up.target.get_or_insert(u.id());
        let (ux, uy) = u.pos();
        if let Some(to) = clamp(c, (ux as f64, uy as f64), HOLD_E) {
            moves.push((u.id(), (ux as f64, uy as f64), to));
        }
    }
    if moves.is_empty() {
        return;
    }
    let grid = super::current_grid(&super::units(sim)).map(|(_, g)| g);
    let seen = watched(sim);
    for (id, from, to) in moves {
        let solid = |p: Pt| grid.as_ref().is_some_and(|g| g.solid(p.0, p.1));
        let Some(to) = open_ground(c, to, solid) else { continue };
        sim.entity_set_pos(id, to.0.round().max(0.0) as u64, to.1.round().max(0.0) as u64);
        up.held += 1;
        up.worst = up.worst.max(reach(c, from));
        // the watched match: every put-back; the server's presims: the first 40, then every 100th
        let n = if seen { Some(up.held) } else { counted() };
        if let Some(n) = n {
            wlog(format!("{} ARENA: #{id} at {:.2} of the picture ({:.0}, {:.0} from the centre) put back to {HOLD_E} #{n}{}",
                         head(sim, me), reach(c, from), from.0 - c.0, from.1 - c.1,
                         if seen { " this arena" } else { "" }));
        }
    }
}

/// The floor while the arena is up: a piece every `FLOOR_STEP` ticks, the loop's frame of the tick ([`floor_frame`]).
/// At each piece's due tick the one before should still be on the floor (it goes this tick, after the passives), and a
/// tick later only the new one (the counts in `ARENA END`: what the screen got).
fn draw_floor(sim: &mut StableSim<'_>, me: usize, team: usize, up: &mut Up, tick: usize) {
    if up.pieces > 1 && tick == up.next.saturating_sub(FLOOR_STEP) + 1 && pieces_on_floor(sim, me, up.centre) > 1 {
        up.after += 1;
    }
    if tick < up.next {
        return;
    }
    if up.pieces > 0 {
        let k = pieces_on_floor(sim, me, up.centre).min(2);
        up.handover[[1, 0, 2][k]] += 1;
    }
    let k = floor_frame(up.start, tick);
    let name = format!("{FLOOR_VIEW}{k}");
    if sim.spawn_projectile(&name, &format!("{ID}:noop"), &floor_spec(me, team, up.centre)) {
        up.pieces += 1;
    } else {
        up.refused += 1;
        if up.refused == 1 {
            wlog(format!("{} ARENA: spawn_projectile({name}) refused - no floor", head(sim, me)));
        }
    }
    up.next = up.start + ((tick - up.start) / FLOOR_STEP + 1) * FLOOR_STEP;
}

/// Arenas ended so far, every simulation of this launch: by `End` (its order).
static ENDS: [AtomicUsize; 8] = [const { AtomicUsize::new(0) }; 8];

fn end_slot(why: End) -> usize {
    match why {
        End::TimeOut => 0,
        End::Walked => 1,
        End::Moved => 2,
        End::HerE => 3,
        End::Banished => 4,
        End::Died => 5,
        End::Unseen => 6,
        End::Swallowed => 7,
    }
}

/// The arena's end: the mark under its target goes with it (the main pack's 30-tick mark outlived the arena by up to half
/// a second - its picture too), and its `ARENA END` line (every simulation: one a cast).
fn finish(sim: &mut StableSim<'_>, me: usize, up: Up, why: End, tick: usize, at: Option<Pt>) {
    if let (Some(t), true) = (up.target, why != End::Unseen) {
        sim.entity_remove_buff(t, R_MARK);
    }
    ENDS[end_slot(why)].fetch_add(1, Ordering::Relaxed);
    let n: Vec<usize> = ENDS.iter().map(|a| a.load(Ordering::Relaxed)).collect();
    let lasted = if why == End::Unseen { up.seen + 1 } else { tick }.saturating_sub(up.start);
    let place = at.map_or(String::new(), |p| {
        format!(" at {:.2} of the picture ({:.0} from the centre)", reach(up.centre, p), dist(up.centre, p))
    });
    let why_s = match why {
        End::TimeOut => "its time ran out".to_string(),
        End::Died => "she died".to_string(),
        End::Walked => format!("she walked out{place}"),
        End::Moved => format!("she was moved out{place} (a knock-back, pull or dash on her)"),
        End::HerE => format!("she hooked out with her E{place}"),
        End::Banished => format!("she was banished{place}"),
        End::Swallowed => "her target was banished (swallowed by Tahm Kench or the like): League ends the ultimatum then"
            .to_string(),
        End::Unseen => format!("her passive stopped seeing it after t={} (dead and gone, or another match)", up.seen),
    };
    let target = match up.target {
        None => "no marked target".to_string(),
        Some(t) => match sim.get_entity(t) {
            Some(u) if u.is_alive() => {
                let (x, y) = u.pos();
                format!("target #{t} {} alive at {:.2} of the picture", u.name().unwrap_or_default(),
                        reach(up.centre, (x as f64, y as f64)))
            }
            Some(u) => format!("target #{t} {} dead", u.name().unwrap_or_default()),
            None => format!("target #{t} gone"),
        },
    };
    let handovers = up.handover.iter().sum::<usize>();
    wlog(format!(
        "{} ARENA END after {lasted} of {ARENA_TICKS} ticks: {why_s} - started t={} at {}; {target}; put back {} times \
         (farthest {:.2} of the picture); she reached {:.2}; floor: {} pieces, the one before still on the floor at {} of {} \
         handovers ({} gone early, {} with another; {} ticks with two after one){}; so far, all simulations: time out {}, \
         she left {} (walked {}, moved {}, her E {}, banished {}), target swallowed {}, died {}, unseen {}",
        head(sim, me), up.start, pt(up.centre), up.held, up.worst, up.far, up.pieces, up.handover[0], handovers,
        up.handover[1], up.handover[2], up.after,
        if up.refused > 0 { format!(", {} refused", up.refused) } else { String::new() },
        n[0], n[1] + n[2] + n[3] + n[4], n[1], n[2], n[3], n[4], n[7], n[5], n[6]
    ));
}

fn pt(p: Pt) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

static LINES: AtomicUsize = AtomicUsize::new(0);

/// The server's presims: the first 40 ARENA lines, then every 100th (the watched match logs every one).
fn counted() -> Option<usize> {
    let n = LINES.fetch_add(1, Ordering::Relaxed) + 1;
    (n <= 40 || n % 100 == 0).then_some(n)
}

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// The AI's order as a walk ([`Want`]): an attack or a skill on a unit becomes where it stands and her reach to it.
fn want_of(sim: &StableSim<'_>, me: &StableEntity<'_, '_>, base: Option<InputV1>) -> (Want, Option<(InputKindV1, usize)>) {
    let Some((kind, b)) = base.and_then(|b| InputKindV1::from_code(b.kind).map(|k| (k, b))) else {
        return (Want::Other, None);
    };
    match kind {
        InputKindV1::Move => (Want::Move((b.x as f64, b.y as f64)), None),
        InputKindV1::Return => (Want::Return, None),
        _ => {
            let on = (b.target.kind == InputTargetKindV1::Target.code()).then_some(b.target.target_id);
            let (Some(range), Some(t)) = (range_of(kind), on.and_then(|id| sim.get_entity(id))) else {
                return (Want::Other, None);
            };
            let (x, y) = t.pos();
            let reach = act_reach(range, me.radius() as f64, t.radius() as f64);
            (Want::Act { at: (x as f64, y as f64), reach }, Some((kind, t.id())))
        }
    }
}

/// What the AI wanted, for the log.
fn wanted(want: Want, act: Option<(InputKindV1, usize)>, me: Pt) -> String {
    match (want, act) {
        (Want::Act { at, reach }, Some((kind, id))) => {
            format!("{kind:?} on #{id} {:.0} away (in reach within {reach:.0})", dist(me, at))
        }
        _ => format!("{want:?}"),
    }
}

#[derive(Clone, Default)]
pub struct Arena {
    centre: Slot,
    /// the watched match: no "left to the AI" line again before this tick
    quiet: usize,
}

impl StablePlayerAi for Arena {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:arena")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == "league_camille"
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let (t, line, seen) = {
            let sim = ctx.sim()?;
            let e = sim.get_player(player)?.champion()?;
            if !e.is_alive() || !has(&e, R_ON) {
                self.centre = None;
                return None;
            }
            let (x, y) = e.pos();
            let me = (x as f64, y as f64);
            let tick = sim.tick();
            let centre = centre_of(&mut self.centre, me, tick);
            let (want, act) = want_of(&sim, &e, base);
            if want == Want::Other {
                return None;
            }
            let (id, team) = (e.id(), e.team());
            let mut foes = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(u) = sim.entity_at(i) else { continue };
                if u.team() == team || !u.is_alive() || !u.is_champion() || !u.is_targetable() {
                    continue;
                }
                let (ux, uy) = u.pos();
                foes.push(Foe { id: u.id(), at: (ux as f64, uy as f64), marked: has(&u, R_MARK) });
            }
            let seen = watched(&sim);
            let Some(t) = call(me, centre, want, &foes) else {
                // the watched match: a walk out with nobody to attack inside is the AI's (0.4.9) - said once a half second
                if seen && leaves(me, centre, want) && tick >= self.quiet {
                    self.quiet = tick + 30;
                    wlog(format!("{} ARENA: the AI wanted {} ({:.0} from the centre) - nothing to attack in the arena, \
                                  left to the AI", head(&sim, id), wanted(want, act, me), dist(me, centre)));
                }
                return None;
            };
            if act == Some((InputKindV1::Attack, t)) {
                // its own attack on the one we would pick: left as it is
                return None;
            }
            (t, format!("{} ARENA: the AI wanted {} ({:.0} from the centre) - attack #{t}", head(&sim, id),
                        wanted(want, act, me), dist(me, centre)), seen)
        };
        let input = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        // the watched match: every one; the server's presims: the first 40 ARENA lines, then every 100th
        if seen {
            wlog(line);
        } else if let Some(n) = counted() {
            wlog(format!("{line} #{n}"));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn foe(id: usize, x: f64, marked: bool) -> Foe {
        Foe { id, at: (x, 0.0), marked }
    }

    #[test]
    fn a_walk_out_of_the_arena_turns_into_an_attack_on_the_marked_target() {
        let foes = [foe(1, 10_000.0, false), foe(2, 25_000.0, true)];
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Move((60_000.0, 0.0)), &foes), Some(2));
        // a recall too
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Return, &foes), Some(2));
    }

    #[test]
    fn walks_inside_the_arena_and_back_in_are_left_alone() {
        let foes = [foe(2, 10_000.0, true)];
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Move((15_000.0, 0.0)), &foes), None);
        // already out at 30000 across, walking back towards the centre
        assert_eq!(call((30_000.0, 0.0), (0.0, 0.0), Want::Move((28_000.0, 0.0)), &foes), None);
        // up and down the picture is narrower: 20000 down is past KEEP_E
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Move((0.0, 20_000.0)), &foes), Some(2));
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Other, &foes), None);
    }

    #[test]
    fn no_target_left_lets_the_ai_go() {
        // the only enemy is far outside and not marked: the AI's walk stands (it used to be a walk back to the centre)
        let foes = [foe(1, 80_000.0, false)];
        assert_eq!(call((20_000.0, 0.0), (0.0, 0.0), Want::Move((50_000.0, 0.0)), &foes), None);
        assert_eq!(call((20_000.0, 0.0), (0.0, 0.0), Want::Return, &[]), None, "a recall with nobody left");
        // an unmarked one inside is attacked
        let foes = [foe(1, 12_000.0, false)];
        assert_eq!(call((20_000.0, 0.0), (0.0, 0.0), Want::Move((50_000.0, 0.0)), &foes), Some(1));
    }

    /// 0.4.12: an attack or a skill on someone she must walk out of the arena to reach is a walk out; one in reach (she
    /// acts from where she stands) or that she reaches inside is left alone.
    #[test]
    fn an_order_on_someone_out_of_reach_outside_is_a_walk_out() {
        let foes = [foe(2, 10_000.0, true), foe(3, 90_000.0, false)];
        // her attack on #3, 90000 away across: reach 25000 + two bodies of 10000, she would walk to 45000 (1.25 of the
        // picture across)
        let far = Want::Act { at: (90_000.0, 0.0), reach: act_reach(25_000.0, 10_000.0, 10_000.0) };
        assert_eq!(walk_end((0.0, 0.0), (90_000.0, 0.0), 45_000.0), Some((45_000.0, 0.0)));
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), far, &foes), Some(2));
        // in reach: she does not walk
        let near = Want::Act { at: (40_000.0, 0.0), reach: 45_000.0 };
        assert_eq!(walk_end((0.0, 0.0), (40_000.0, 0.0), 45_000.0), None);
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), near, &foes), None);
        // out of reach, but the walk ends inside KEEP_E: left alone
        let short = Want::Act { at: (60_000.0, 0.0), reach: 45_000.0 };
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), short, &foes), None);
        // up and down: an attack on someone 60000 below ends the walk at 15000 down (0.6): left; 80000 below: 35000 (1.4)
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Act { at: (0.0, 60_000.0), reach: 45_000.0 }, &foes), None);
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Act { at: (0.0, 80_000.0), reach: 45_000.0 }, &foes), Some(2));
        // nobody to attack inside: the AI's order stands (as for a walk)
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), far, &[foe(3, 90_000.0, false)]), None);
        // a walk to someone inside stays inside (the ellipse is convex) even past KEEP_E: 24000 down (0.96), reached from
        // 5000, the walk ends at 19000 down (0.76)
        let inside = Want::Act { at: (0.0, 24_000.0), reach: 5_000.0 };
        assert!(outward((0.0, 0.0), (0.0, 0.0), walk_end((0.0, 0.0), (0.0, 24_000.0), 5_000.0).unwrap()));
        assert!(!leaves((0.0, 0.0), (0.0, 0.0), inside));
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), inside, &foes), None);
    }

    /// 0.4.13: every way an arena ends has its own count in the `ARENA END` totals.
    #[test]
    fn every_end_has_its_own_count() {
        let all = [End::TimeOut, End::Died, End::Walked, End::Moved, End::HerE, End::Banished, End::Swallowed, End::Unseen];
        let mut slots: Vec<usize> = all.iter().map(|&e| end_slot(e)).collect();
        slots.sort();
        assert_eq!(slots, (0..ENDS.len()).collect::<Vec<_>>());
    }

    #[test]
    fn the_ranges_are_the_copys() {
        // the add-on's copy of her (make_override.py: E's range is ENGAGE_R there)
        let src = include_str!("../override/league_camille.data_champion");
        for (slot, kind) in [("attack", InputKindV1::Attack), ("skill", InputKindV1::Skill),
                             ("skill2", InputKindV1::Skill2), ("ult", InputKindV1::Ult)] {
            let at = src.find(&format!("\n  \"{slot}\": {{")).unwrap_or_else(|| panic!("{slot}"));
            let range = src[at..].split("\"range\": ").nth(1).and_then(|v| v.split([',', '\n']).next())
                .and_then(|v| v.trim().parse::<f64>().ok()).unwrap();
            assert_eq!(range_of(kind), Some(range), "{slot}");
        }
        assert_eq!(range_of(InputKindV1::Move), None);
    }

    #[test]
    fn a_target_past_the_edge_goes_back_on_the_line_to_it() {
        let near = |a: Option<Pt>, b: Pt| a.is_some_and(|a| dist(a, b) < 1.0);
        // across: the picture is 36000 wide, the target goes back to 0.85 of it
        assert!(near(clamp((0.0, 0.0), (40_000.0, 0.0), HOLD_E), (30_600.0, 0.0)));
        // up and down: 25000 - 27000 down (inside the old 27000 circle) was off the picture, now 21250
        assert!(near(clamp((0.0, 0.0), (0.0, 27_000.0), HOLD_E), (0.0, 21_250.0)));
        assert_eq!(clamp((0.0, 0.0), (20_000.0, 10_000.0), HOLD_E), None);
        assert!(HOLD_E < 1.0 && KEEP_E < HOLD_E);
    }

    #[test]
    fn never_into_a_wall() {
        let open = |_: Pt| false;
        assert_eq!(open_ground((0.0, 0.0), (27_000.0, 0.0), open), Some((27_000.0, 0.0)));
        // a wall from 20000 out: the first open point inside it
        let wall = |p: Pt| p.0 > 20_000.0;
        let at = open_ground((0.0, 0.0), (27_000.0, 0.0), wall).unwrap();
        assert!(at.0 <= 20_000.0 && at.0 > 19_000.0, "{at:?}");
        assert_eq!(open_ground((0.0, 0.0), (27_000.0, 0.0), |_: Pt| true), None);
    }

    #[test]
    fn a_new_arena_takes_a_new_centre() {
        let mut slot = None;
        assert_eq!(centre_of(&mut slot, (1.0, 0.0), 100), (1.0, 0.0));
        // the same arena: she moved, the centre did not
        assert_eq!(centre_of(&mut slot, (9.0, 0.0), 101), (1.0, 0.0));
        assert_eq!(centre_of(&mut slot, (9.0, 0.0), 101 + ARENA_TICKS - 1), (1.0, 0.0));
        // not looked at for an arena's length: a new one
        assert_eq!(centre_of(&mut slot, (5.0, 0.0), 101 + 2 * ARENA_TICKS), (5.0, 0.0));
        // the clock went back: another match
        assert_eq!(centre_of(&mut slot, (7.0, 0.0), 3), (7.0, 0.0));
    }

    #[test]
    fn the_ellipse_is_the_arenas_picture() {
        // r_zone's frames (league_camille_big): 73 x 55 px, the opaque ellipse 72 x 50 (1 px = 1000) - the frame is the
        // ellipse plus a pixel across and a shadow row band below
        let fanim = include_str!("../../../league/effects/league_camille_big#anim.fanim");
        let at = fanim.find("\"r_zone\"").expect("r_zone");
        let w: f64 = fanim[at..].split("\"w\":").nth(1).and_then(|v| v.split([',', '}']).next()).and_then(|v| v.trim().parse().ok()).unwrap();
        let h: f64 = fanim[at..].split("\"h\":").nth(1).and_then(|v| v.split([',', '}']).next()).and_then(|v| v.trim().parse().ok()).unwrap();
        assert!((w * 1000.0 / 2.0 - SEMI_X).abs() <= 1_000.0, "r_zone {w} px wide, SEMI_X {SEMI_X}");
        assert!(SEMI_Y < h * 1000.0 / 2.0, "r_zone {h} px tall, SEMI_Y {SEMI_Y}");
    }

    #[test]
    fn the_radius_and_length_are_the_main_packs_arena() {
        let src = include_str!("../../../league/champion/league_camille.data_champion");
        let at = src.find("\"name\": \"league_camille_r_area\"").expect("r_area");
        assert!(src[at..at + 300].contains(&format!("\"radius\": {}", ARENA_R as u64)));
        // the one AddCasterBuff that gives it (the other mentions only remove or read it)
        let at = src.find("\"name\": \"league_camille_r_on\",").expect("r_on");
        assert!(src[at..at + 200].contains(&format!("\"tick\": {ARENA_TICKS}")), "{}", &src[at..at + 200]);
    }

    /// A tag's frames in a minified .fanim: each `{"duration":...,"data":{...}}` as written.
    fn frames<'a>(fanim: &'a str, tag: &str) -> Vec<&'a str> {
        let key = format!("\"{tag}\":{{\"frames\":[");
        let at = fanim.find(&key).unwrap_or_else(|| panic!("no {tag} in league_camille_big")) + key.len();
        let end = at + fanim[at..].find("]}").unwrap();
        fanim[at..end].split("}},").map(|f| f.trim_end_matches("}}")).collect()
    }

    /// The floor's pieces show r_zone's frames in its order and timing: `r_zone_<k>` / `hd_r_zone_<k>` (the main pack's
    /// sheet, tools/fix/camille_r_zone_frames.py) are frame k of r_zone / hd_r_zone, and a frame lasts FLOOR_STEP ticks.
    #[test]
    fn the_floor_pieces_are_r_zones_frames() {
        let fanim = include_str!("../../../league/effects/league_camille_big#anim.fanim");
        for pre in ["", "hd_"] {
            let all = frames(fanim, &format!("{pre}r_zone"));
            assert_eq!(all.len(), FLOOR_FRAMES, "{pre}r_zone");
            for (k, f) in all.iter().enumerate() {
                assert_eq!(frames(fanim, &format!("{pre}r_zone_{k}")), [*f], "{pre}r_zone_{k}: run tools/fix/camille_r_zone_frames.py");
                let ms: f64 = f.split("\"duration\":").nth(1).and_then(|v| v.split(',').next()).and_then(|v| v.parse().ok()).unwrap();
                assert!((ms * 60.0 - FLOOR_STEP as f64).abs() < 0.1, "{pre}r_zone frame {k}: {ms} s");
            }
        }
        // the copy binds each piece to its tag, the data's 240-tick floor has no picture there
        let copy = include_str!("../override/league_camille.data_champion");
        for k in 0..FLOOR_FRAMES {
            let at = copy.find(&format!("\"name\": \"{FLOOR_VIEW}{k}\"")).unwrap_or_else(|| panic!("{FLOOR_VIEW}{k}"));
            let entry = &copy[copy[..at].rfind('{').unwrap()..at + copy[at..].find('}').unwrap()];
            for want in ["\"type\": \"Animated\"", "\"anim\": \"asset/league/effects/league_camille_big\"",
                         &format!("\"tag\": \"r_zone_{k}\""), "\"z\": -1"] {
                assert!(entry.contains(want), "{FLOOR_VIEW}{k}: {want} in {entry}");
            }
        }
        let views = &copy[copy.find("\"view_projectiles\"").unwrap()..copy.find("\"view_effects\"").unwrap()];
        assert!(!views.contains("\"name\": \"league_camille_r_floor\","), "the data's floor still has a picture");
        // its zone is still there: it gives her r_vis, the gate of the main pack's hold
        assert!(copy.contains("\"name\": \"league_camille_r_floor\","));
    }

    #[test]
    fn the_floor_steps_through_the_loop_from_the_landing() {
        assert_eq!(floor_frame(100, 100), 0);
        assert_eq!(floor_frame(100, 104), 0);
        assert_eq!(floor_frame(100, 105), 1);
        assert_eq!(floor_frame(100, 129), 5);
        assert_eq!(floor_frame(100, 130), 0, "the loop is 30 ticks");
        assert_eq!(floor_frame(100, 100 + ARENA_TICKS - 1), 5);
        // each piece: FLOOR_STEP + 1 steps of 1 unit pointing (-1, 0), its first step onto the centre
        let s = floor_spec(7, 1, (480_000.0, 470_000.0));
        assert_eq!((s.x, s.y, s.target_x, s.target_y, s.speed), (480_001, 470_000, 480_000 - FLOOR_STEP as u64, 470_000, 1));
        assert_eq!((s.caster_id, s.team, s.move_kind), (7, 1, ProjectileMoveKindV1::Linear.code()));
        assert_eq!(s.x - s.target_x, FLOOR_STEP as u64 + 1);
    }

    #[test]
    fn why_an_arena_ended() {
        // dead first, then its time (a tick short when first seen a tick late), then what moved her within MOVED_T
        assert_eq!(end_reason(false, 100, 340, None, false), End::Died);
        assert_eq!(end_reason(true, 100, 340, None, false), End::TimeOut);
        assert_eq!(end_reason(true, 101, 340, None, false), End::TimeOut);
        assert_eq!(end_reason(true, 100, 200, None, false), End::Walked);
        assert_eq!(end_reason(true, 100, 200, Some((197, false)), false), End::Moved);
        assert_eq!(end_reason(true, 100, 200, Some((199, true)), false), End::HerE);
        assert_eq!(end_reason(true, 100, 200, Some((150, false)), false), End::Walked, "moved long before");
        assert_eq!(end_reason(true, 100, 200, None, true), End::Banished);
    }
}
