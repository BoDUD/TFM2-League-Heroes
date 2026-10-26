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
//! 判断在 [`call`]、[`clamp`]（纯计算、单元测试）。

use mod_api_stable::*;

use std::sync::atomic::{AtomicUsize, Ordering};

use super::{head, wlog, ID};

/// 排在 league_ult_press（100）之后。
pub const PRIORITY: i32 = 120;
/// 主包场地的半径（`league_camille_r_area`）。
pub const ARENA_R: f64 = 30_000.0;
/// 她的走路目的地离中心超过这么远就算要走出去（留出身体和一步的余量）。
pub const KEEP: f64 = 22_000.0;

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
        Want::Move(to) => dist(to, centre) > KEEP && dist(to, centre) > dist(me, centre),
        Want::Other => false,
    };
    if !leaving {
        return None;
    }
    let inside = |f: &&Foe| dist(f.at, centre) <= ARENA_R;
    let target = foes
        .iter()
        .filter(|f| f.marked)
        .chain(foes.iter().filter(inside).filter(|f| !f.marked))
        .min_by(|a, b| (!a.marked).cmp(&!b.marked).then(dist(me, a.at).total_cmp(&dist(me, b.at))));
    Some(target.map_or(Call::Centre, |f| Call::Attack(f.id)))
}

/// The marked target is kept this far from the centre at most (inside the arena's picture, a body short of its edge).
pub const HOLD_R: f64 = 27_000.0;

/// Where the target goes back to when it is past `r` from the centre: the point at `r` on the line to it.
pub fn clamp(centre: Pt, at: Pt, r: f64) -> Option<Pt> {
    let d = dist(centre, at);
    (d > r && d > 0.0).then(|| (centre.0 + (at.0 - centre.0) * r / d, centre.1 + (at.1 - centre.1) * r / d))
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
/// on her (she lands on it), and the champion carrying the arena's mark is put back inside `HOLD_R` whenever it is past it -
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
        if let Some(to) = clamp(c, (ux as f64, uy as f64), HOLD_R) {
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
            wlog(format!("{} ARENA: #{id} at {:.0} from the centre put back to {HOLD_R:.0} #{n}", head(sim, me), dist(c, from)));
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
        // already out at 26000, walking back towards the centre
        assert_eq!(call((26_000.0, 0.0), (0.0, 0.0), Want::Move((24_000.0, 0.0)), &foes), None);
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
        assert_eq!(clamp((0.0, 0.0), (30_000.0, 40_000.0), 25_000.0), Some((15_000.0, 20_000.0)));
        assert_eq!(clamp((0.0, 0.0), (10_000.0, 0.0), 25_000.0), None);
        assert!(HOLD_R < ARENA_R);
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
    fn the_radius_and_length_are_the_main_packs_arena() {
        let src = include_str!("../../../league/champion/league_camille.data_champion");
        let at = src.find("\"name\": \"league_camille_r_area\"").expect("r_area");
        assert!(src[at..at + 300].contains(&format!("\"radius\": {}", ARENA_R as u64)));
        // the one AddCasterBuff that gives it (the other mentions only remove or read it)
        let at = src.find("\"name\": \"league_camille_r_on\",").expect("r_on");
        assert!(src[at..at + 200].contains(&format!("\"tick\": {ARENA_TICKS}")), "{}", &src[at..at + 200]);
    }
}
