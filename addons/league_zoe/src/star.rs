//! 飞星乱入！先扔出去、再拐回来砸目标（0.8.0，用户 2026-11-20：「按照你的建议改吧」）。
//!
//! 英雄联盟的 Q 扔出去以后还能再按一次，让星从它当时的位置改飞向新的地方，打中第一个敌人，飞得越远伤害越高（最多
//! +150%），所以玩家都是先往身后或旁边扔，再拐回来砸人。游戏的 AI 只会对着目标扔一次，这里替她把第二下按了：
//!
//! - 第一段：从她脚下往外飞 `q_out`（每 tick `q_out_v`，英雄联盟第一下 1200 码/秒，比第二下慢一半）。方向先看**正后方**
//!   （离目标最远、路过她自己再飞向目标，伤害最高）；正后方这条路上除了目标还有别的敌人挡着（小兵、野怪），就看**左边**、
//!   **右边**（和朝目标的方向垂直）哪边两段路都空着；都挡着还是正后方（照样砸在挡路的那个身上）。
//! - 拐弯：第一段飞完，朝目标**这时**站的地方拐（目标死了就朝最后看见他的地方），每 tick `q_speed`，一直飞到离她
//!   `q_len` 远（英雄联盟：离佐伊 800 码就消失）。
//! - 两段都是一路上碰到的第一个敌方单位（不打塔）挨打，伤害按**两段一共飞了多远**（`q_n0` 以内 100%，到 `q_n1d` 线性
//!   加到 `q_far`%）。
//!
//! 这里只有算路的纯函数，飞和打在 lib.rs 的 `Sparkles::fly_stars`。

use super::{unit, Pt};

/// 第一段往哪扔。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Out {
    Back,
    Left,
    Right,
}

impl Out {
    pub fn name(self) -> &'static str {
        match self {
            Out::Back => "behind her",
            Out::Left => "to her left",
            Out::Right => "to her right",
        }
    }
}

/// 一个敌方单位：(编号, 位置, 身体半径)。
pub type Body = (usize, Pt, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 点 `p` 到线段 `a`-`b` 最近的地方在线段上的比例（0 = a，1 = b）和距离。
pub fn along(p: Pt, a: Pt, b: Pt) -> (f64, f64) {
    let (vx, vy) = (b.0 - a.0, b.1 - a.1);
    let len2 = vx * vx + vy * vy;
    let t = if len2 < 1.0 { 0.0 } else { (((p.0 - a.0) * vx + (p.1 - a.1) * vy) / len2).clamp(0.0, 1.0) };
    (t, dist(p, (a.0 + vx * t, a.1 + vy * t)))
}

/// 星从 `a` 飞到 `b`（半径 `w`）一路上先碰到谁：离 `a` 最近、碰得到（星的半径 + 他的身体）的那个，`skip` 不算。
/// 返回 (编号, 碰到时在这段上的比例)。
pub fn first_on(a: Pt, b: Pt, w: f64, bodies: &[Body], skip: Option<usize>) -> Option<(usize, f64)> {
    bodies
        .iter()
        .filter(|u| Some(u.0) != skip)
        .filter_map(|&(id, p, r)| {
            let (t, d) = along(p, a, b);
            (d <= w + r).then_some((id, t))
        })
        .min_by(|x, y| x.1.total_cmp(&y.1))
}

/// 把 `f` 转到第一段的方向：正后方是 -f，左右是 f 的两条垂线（y 往下的屏幕上，左 = 朝目标看过去的左手边）。
pub fn turn(f: Pt, how: Out) -> Pt {
    match how {
        Out::Back => (-f.0, -f.1),
        Out::Left => (f.1, -f.0),
        Out::Right => (-f.1, f.0),
    }
}

/// 游戏自己的图的边长（5v5、单线、死斗都是 960000 见方）。
pub const MAP_SIDE: f64 = 960_000.0;

/// 地图上这一点能扔过去吗（星飞过墙没关系，只是别扔到地图外面去）。`side` 是这张图的边长。
fn on_map(p: Pt, side: f64) -> bool {
    p.0 >= 0.0 && p.1 >= 0.0 && p.0 < side && p.1 < side
}

/// 挑第一段：她在 `her`、目标（编号 `target`）在 `aim`，第一段长 `len`，星的半径 `w`，地图边长 `side`。返回方向和拐弯的地方。
/// 两段路上除了目标都没有别的敌人才算空；正后方空就扔正后方，不然左、右，都不空还是正后方。
pub fn pick_out(her: Pt, aim: Pt, len: f64, w: f64, bodies: &[Body], target: usize, side: f64) -> (Out, Pt) {
    let f = unit((aim.0 - her.0, aim.1 - her.1)).unwrap_or((1.0, 0.0));
    let spot = |how| {
        let d = turn(f, how);
        (her.0 + d.0 * len, her.1 + d.1 * len)
    };
    let clear = |o: Pt| first_on(her, o, w, bodies, Some(target)).is_none() && first_on(o, aim, w, bodies, Some(target)).is_none();
    for how in [Out::Back, Out::Left, Out::Right] {
        let o = spot(how);
        if on_map(o, side) && clear(o) {
            return (how, o);
        }
    }
    let back = spot(Out::Back);
    if on_map(back, side) {
        return (Out::Back, back);
    }
    // 背靠地图边上：往左右里在地图里的那边扔，都不行就原地拐（只剩第二段）
    for how in [Out::Left, Out::Right] {
        let o = spot(how);
        if on_map(o, side) {
            return (how, o);
        }
    }
    (Out::Back, her)
}

/// 这一 tick 从 `at` 朝 `to` 飞 `speed`：返回新的位置和到没到 `to`。
pub fn advance(at: Pt, to: Pt, speed: f64) -> (Pt, bool) {
    let d = dist(at, to);
    if d <= speed {
        return (to, true);
    }
    ((at.0 + (to.0 - at.0) / d * speed, at.1 + (to.1 - at.1) / d * speed), false)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_clear_lane_throws_it_straight_behind_her() {
        let her = (400_000.0, 500_000.0);
        let foe = (460_000.0, 500_000.0);
        let (how, o) = pick_out(her, foe, 30_000.0, 6_000.0, &[(7, foe, 15_000.0)], 7, MAP_SIDE);
        assert_eq!(how, Out::Back);
        assert_eq!(o, (370_000.0, 500_000.0));
    }

    #[test]
    fn a_minion_in_the_way_sends_it_round_the_side() {
        let her = (400_000.0, 500_000.0);
        let foe = (460_000.0, 500_000.0);
        // a minion a third of the way: behind her the second leg runs through it; from her left (up the screen) the star
        // comes in at an angle and passes 17900 from it (the star's 6000 + its body 8000 would touch)
        let bodies = [(7, foe, 15_000.0), (30, (420_000.0, 500_000.0), 8_000.0)];
        let (how, o) = pick_out(her, foe, 30_000.0, 6_000.0, &bodies, 7, MAP_SIDE);
        assert_eq!(how, Out::Left);
        assert!((o.0 - 400_000.0).abs() < 1.0 && (o.1 - 470_000.0).abs() < 1.0, "{o:?}");
        // a second minion on that way in: the right side
        let bodies = [(7, foe, 15_000.0), (30, (420_000.0, 500_000.0), 8_000.0), (31, (425_000.0, 483_000.0), 8_000.0)];
        assert_eq!(pick_out(her, foe, 30_000.0, 6_000.0, &bodies, 7, MAP_SIDE).0, Out::Right);
        // walled in by minions all round: behind her anyway (it hits the first of them)
        let mut many = vec![(7, foe, 15_000.0)];
        for (k, y) in [470_000.0, 485_000.0, 500_000.0, 515_000.0, 530_000.0].iter().enumerate() {
            many.push((40 + k, (430_000.0, *y), 8_000.0));
        }
        assert_eq!(pick_out(her, foe, 30_000.0, 6_000.0, &many, 7, MAP_SIDE).0, Out::Back);
    }

    #[test]
    fn never_off_the_map() {
        // her back to the map's left edge: behind her is off the map
        let (how, o) = pick_out((10_000.0, 500_000.0), (70_000.0, 500_000.0), 30_000.0, 6_000.0, &[], 1, MAP_SIDE);
        assert_ne!(how, Out::Back);
        assert!(o.0 >= 0.0 && o.1 >= 0.0);
    }

    #[test]
    fn the_first_one_on_the_way_takes_it() {
        let bodies = [(1, (50_000.0, 0.0), 10_000.0), (2, (20_000.0, 14_000.0), 10_000.0), (3, (10_000.0, 30_000.0), 10_000.0)];
        // 2 is 14000 off the line: within the star's 6000 + his body 10000; 3 is too far off
        assert_eq!(first_on((0.0, 0.0), (100_000.0, 0.0), 6_000.0, &bodies, None).map(|h| h.0), Some(2));
        assert_eq!(first_on((0.0, 0.0), (100_000.0, 0.0), 6_000.0, &bodies, Some(2)).map(|h| h.0), Some(1));
        assert_eq!(first_on((0.0, 0.0), (10_000.0, 0.0), 6_000.0, &bodies[..1], None), None);
    }

    #[test]
    fn it_flies_to_the_turn_and_stops_there() {
        let (p, done) = advance((0.0, 0.0), (5_000.0, 0.0), 2_000.0);
        assert_eq!((p, done), ((2_000.0, 0.0), false));
        assert_eq!(advance((4_000.0, 0.0), (5_000.0, 0.0), 2_000.0), ((5_000.0, 0.0), true));
        // the turns: a foe to the right (+x) - behind is -x, left is up the screen (-y), right down it
        assert_eq!(turn((1.0, 0.0), Out::Back), (-1.0, -0.0));
        assert_eq!(turn((1.0, 0.0), Out::Left), (0.0, -1.0));
        assert_eq!(turn((1.0, 0.0), Out::Right), (-0.0, 1.0));
    }
}
