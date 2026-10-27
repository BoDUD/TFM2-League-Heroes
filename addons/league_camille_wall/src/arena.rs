//! 大招场地里不走出去（用户 2026-10-26：「卡密尔的R三秒有点太短了 而且现在有时候都没3秒」「你要确保英雄走不出去」）：
//! AI 钩子 `league_camille_wall:arena`。
//!
//! 主包的海克斯最后通牒：场地 `ARENA_R` 内，目标走出去就被拉回她身边；她自己走出去场地就结束（英雄联盟的规则，也是因为
//! 她在外面时把目标拉向她会把目标拉出场地）。游戏的 AI 常让她追出去、撤出去，场地于是不到时间就没了。本钩子在她身上有
//! 主包的 `league_camille_r_on` 时，第一次看到就把她的位置记成场地中心（场地落在她落地的地方）；之后 AI 要她**走到**离中心
//! `KEEP` 以外的地方、或**回城**，就改成普攻被锁的目标（身上有 `league_camille_r_mark` 的敌方英雄，没有就场地里最近的
//! 敌方英雄），打不了就走回中心。被击退、拉走出场地照旧结束（那是对面的本事）。
//!
//! 被锁的目标也出不去（[`hold`]，她的被动每 tick 跑）：主包把人拉回来的判断问的是「场地里有没有敌方英雄」（哪个都算），
//! 场地里站着别的敌人时目标走出去也不拉（经典模拟：一次 140 tick 的场地里目标只被拉了 4 下，走到离中心 35000）；
//! 本包认场地的标记（`league_camille_r_mark`），目标离中心超过 `HOLD_R` 就把他放回 `HOLD_R` 处。
//!
//! 0.4.5（用户 2026-10-26 打了一局：「青钢影的大招还是没修好吧」——场地还是太短、敌人还能走出去）：场地的画面
//! （`league_camille_big` 的 `r_zone`）是横 72、纵 50 游戏像素的椭圆（1 像素 1000），判断却是半径 30000 的圆：她站在
//! 画面左右两边（30000–36000）场地就结束了，目标被放回的 27000 在画面上下两边（25000）的外面。现在都照画面的椭圆
//! （`SEMI_X` x `SEMI_Y`）：主包的 `r_area` 半径改成 `SEMI_X`（她在画面里场地就不结束），本包让她待在椭圆的 `KEEP_E`
//! 以内、把目标放回椭圆的 `HOLD_E` 处（[`reach`]：到中心的距离按椭圆折算，1 = 画面的边）。
//!
//! 判断在 [`call`]、[`clamp`]（纯计算、单元测试）。

use mod_api_stable::*;

use std::sync::atomic::{AtomicUsize, Ordering};

use super::{head, wlog, ID};

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
    Other,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub marked: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Call {
    Attack(usize),
    Centre,
}

/// What to do instead of the AI's order (None: leave it).
pub fn call(me: Pt, centre: Pt, want: Want, foes: &[Foe]) -> Option<Call> {
    let leaving = match want {
        Want::Return => true,
        Want::Move(to) => reach(centre, to) > KEEP_E && reach(centre, to) > reach(centre, me),
        Want::Other => false,
    };
    if !leaving {
        return None;
    }
    let inside = |f: &&Foe| reach(centre, f.at) <= 1.0;
    let target = foes
        .iter()
        .filter(|f| f.marked)
        .chain(foes.iter().filter(inside).filter(|f| !f.marked))
        .min_by(|a, b| (!a.marked).cmp(&!b.marked).then(dist(me, a.at).total_cmp(&dist(me, b.at))));
    Some(target.map_or(Call::Centre, |f| Call::Attack(f.id)))
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

/// Every tick while the arena is up (Camille's passive): the arena's centre is where she stood the first tick `r_on` was
/// on her (she lands on it), and the champion carrying the arena's mark is put back to `HOLD_E` whenever it is past it -
/// the main pack's pull asks "is an enemy champion inside" (any one), so with two of them inside the target walked out.
pub fn hold(sim: &mut StableSim<'_>, me: usize, centre: &mut Slot) {
    let Some(e) = sim.get_entity(me) else { return };
    if !e.is_alive() || !has(&e, R_ON) {
        *centre = None;
        return;
    }
    let (x, y) = e.pos();
    let team = e.team();
    let c = centre_of(centre, (x as f64, y as f64), sim.tick());
    let mut moves = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_champion() || !has(&u, R_MARK) {
            continue;
        }
        let (ux, uy) = u.pos();
        if let Some(to) = clamp(c, (ux as f64, uy as f64), HOLD_E) {
            moves.push((u.id(), (ux as f64, uy as f64), to));
        }
    }
    if moves.is_empty() {
        return;
    }
    let grid = super::current_grid(&super::units(sim)).map(|(_, g)| g);
    for (id, from, to) in moves {
        let solid = |p: Pt| grid.as_ref().is_some_and(|g| g.solid(p.0, p.1));
        let Some(to) = open_ground(c, to, solid) else { continue };
        sim.entity_set_pos(id, to.0.round().max(0.0) as u64, to.1.round().max(0.0) as u64);
        if let Some(n) = counted() {
            wlog(format!("{} ARENA: #{id} at {:.2} of the picture ({:.0}, {:.0} from the centre) put back to {HOLD_E} #{n}",
                         head(sim, me), reach(c, from), from.0 - c.0, from.1 - c.1));
        }
    }
}

static LINES: AtomicUsize = AtomicUsize::new(0);

/// The first 40 ARENA lines, then every 100th.
fn counted() -> Option<usize> {
    let n = LINES.fetch_add(1, Ordering::Relaxed) + 1;
    (n <= 40 || n % 100 == 0).then_some(n)
}

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn want_of(base: Option<InputV1>) -> Want {
    match base.and_then(|b| InputKindV1::from_code(b.kind).map(|k| (k, b))) {
        Some((InputKindV1::Move, b)) => Want::Move((b.x as f64, b.y as f64)),
        Some((InputKindV1::Return, _)) => Want::Return,
        _ => Want::Other,
    }
}

#[derive(Clone, Default)]
pub struct Arena {
    centre: Slot,
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
        let (c, line, centre) = {
            let sim = ctx.sim()?;
            let e = sim.get_player(player)?.champion()?;
            if !e.is_alive() || !has(&e, R_ON) {
                self.centre = None;
                return None;
            }
            let (x, y) = e.pos();
            let me = (x as f64, y as f64);
            let centre = centre_of(&mut self.centre, me, sim.tick());
            let want = want_of(base);
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
            let c = call(me, centre, want, &foes)?;
            super::haste::note_arena(&sim, id, c == Call::Centre);
            (c, format!("{} ARENA: the AI wanted {want:?} ({:.0} from the centre) - {c:?}", head(&sim, id),
                        dist(me, centre)), centre)
        };
        let back = InputV1::move_to(centre.0.max(0.0) as u64, centre.1.max(0.0) as u64);
        let input = match c {
            Call::Attack(t) => InputV1::action(InputKindV1::Attack, InputTargetV1::target(t)),
            Call::Centre => back,
        };
        let input = if ctx.is_valid_input(&input) {
            input
        } else if ctx.is_valid_input(&back) {
            back
        } else {
            return None;
        };
        if let Some(n) = counted() {
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
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Move((60_000.0, 0.0)), &foes), Some(Call::Attack(2)));
        // a recall too
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Return, &foes), Some(Call::Attack(2)));
    }

    #[test]
    fn walks_inside_the_arena_and_back_in_are_left_alone() {
        let foes = [foe(2, 10_000.0, true)];
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Move((15_000.0, 0.0)), &foes), None);
        // already out at 30000 across, walking back towards the centre
        assert_eq!(call((30_000.0, 0.0), (0.0, 0.0), Want::Move((28_000.0, 0.0)), &foes), None);
        // up and down the picture is narrower: 20000 down is past KEEP_E
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Move((0.0, 20_000.0)), &foes), Some(Call::Attack(2)));
        assert_eq!(call((0.0, 0.0), (0.0, 0.0), Want::Other, &foes), None);
    }

    #[test]
    fn no_target_left_means_back_to_the_centre() {
        // the only enemy is far outside and not marked
        let foes = [foe(1, 80_000.0, false)];
        assert_eq!(call((20_000.0, 0.0), (0.0, 0.0), Want::Move((50_000.0, 0.0)), &foes), Some(Call::Centre));
        // an unmarked one inside is attacked
        let foes = [foe(1, 12_000.0, false)];
        assert_eq!(call((20_000.0, 0.0), (0.0, 0.0), Want::Move((50_000.0, 0.0)), &foes), Some(Call::Attack(1)));
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
}
