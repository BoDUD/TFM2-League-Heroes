//! 掠影步穿墙（2026-10-06，用户：「穿墙的逻辑要改 该穿的时候不穿 你要看游戏里地图设置的」）。
//!
//! 主包的掠影步（Q 转完 2 秒，buff `league_kayn_ghost`）给了 `ignore_wall`，可宿主的寻路是事先算好的、永远绕开
//! 墙格，所以凯隐从不穿过树林里的墙抄近路。地图的墙：引擎的碰撞墙，30×30 格、每格 32000，`walls[y][x]`
//! （5v5 共 90 格，都在原画最深的树林里；卡蜜尔钩墙附加包的 `maps.rs`，game_core 0.5.1 的 MapDef，0.6.2 相同）。
//!
//! 掠影步期间每 tick 看一次：离他最近的敌方英雄在 `CHASE` 内、隔着墙格（两人之间的直线穿过墙）而且不贴身，就朝他
//! 笔直穿过去——引擎的强制位移（`ForceMove`，宿主就不再按寻路挪他），速度是他现在的移速；宿主没把他挪动时（撞墙停了）
//! 逐 tick 自己走一步（`entity_set_pos`）。掠影步结束、人到了、或者人死了就停。

use mod_api_stable::*;

#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

pub const CELL: f64 = 32_000.0;
/// 掠影步的 buff（主包）。
pub const GHOST: &str = "league_kayn_ghost";
/// 追这么远内的敌方英雄。
pub const CHASE: f64 = 80_000.0;
/// 离他这么近就不用穿了（够得着）。
pub const NEAR: f64 = 22_000.0;
/// 直线上每隔这么远看一次是不是墙。
pub const STEP: f64 = 4_000.0;

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

    /// 世界坐标落在墙格里吗（地图外不算：只关心树林里的墙）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return false;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(false)
    }

    /// 两点之间的直线穿过墙格吗（两端不算）。
    pub fn crosses(&self, a: (f64, f64), b: (f64, f64)) -> bool {
        let d = dist(a, b);
        let n = (d / STEP).floor() as usize;
        (1..n).any(|i| {
            let t = i as f64 / n as f64;
            self.is_wall(a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
        })
    }
}

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 这局是哪张图：没有一个活着的英雄站在墙里、墙又最多的那张（卡蜜尔钩墙附加包的判断）。
pub fn current(grids: &[Grid], champions: &[(f64, f64)]) -> Option<usize> {
    grids
        .iter()
        .enumerate()
        .filter(|(_, g)| champions.iter().all(|&(x, y)| !g.is_wall(x, y)))
        .max_by_key(|(_, g)| g.cells.iter().flatten().filter(|w| **w).count())
        .map(|(i, _)| i)
}

/// 穿墙的目的地：朝着他走到离他 `NEAR` 处；不穿墙（没隔着墙、太远、太近）时 None。
pub fn through(grid: &Grid, me: (f64, f64), foe: (f64, f64)) -> Option<(f64, f64)> {
    let d = dist(me, foe);
    if !(NEAR..=CHASE).contains(&d) || !grid.crosses(me, foe) {
        return None;
    }
    // stop NEAR * 0.8 short of him; if that is in the wall, on along the line to the wall's far side
    let mut k = (d - NEAR * 0.8) / d;
    let at = |k: f64| (me.0 + (foe.0 - me.0) * k, me.1 + (foe.1 - me.1) * k);
    while grid.is_wall(at(k).0, at(k).1) && k < 1.0 {
        k = (k + STEP / d).min(1.0);
    }
    let to = at(k);
    (!grid.is_wall(to.0, to.1)).then_some(to)
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    sim.get_entity(id).map(|e| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

/// 每个凯隐一份（在被动里）：正在穿往哪里。
#[derive(Clone, Debug, Default)]
pub struct Walker {
    pub goal: Option<(f64, f64)>,
    pub last: Option<(f64, f64)>,
}

impl Walker {
    /// 每 tick：掠影步期间隔墙追人。返回这一 tick 他是否站在墙格里（给完整变身的「墙里的暗影」用）。
    pub fn update(&mut self, sim: &mut StableSim<'_>, me: usize, ghost: bool, log: &dyn Fn(&StableSim<'_>, String)) -> bool {
        let Some(here) = pos(sim, me) else { return false };
        let Some(k) = sim.get_entity(me) else { return false };
        let team = k.team();
        let speed = (k.stat().move_speed as f64).max(500.0);
        let mut champs = Vec::new();
        let mut foes = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || !e.is_alive() {
                continue;
            }
            let (x, y) = e.pos();
            let p = (x as f64, y as f64);
            if e.id() != me {
                champs.push(p);
            }
            if e.team() != team && e.is_targetable() {
                foes.push(p);
            }
        }
        let grids = Grid::builtin();
        let Some(gi) = current(&grids, &champs) else { return false };
        let grid = &grids[gi];
        // only during the Shadow Step: walking by the jungle his spot often falls on a wall cell (the cells are coarse),
        // and the in-wall shadow showed then - dark with red sparks, at level 1-2, gone again a moment later, it looked
        // like a transformation (「打野2级就变身了」, 「一帧变身后 又释放技能的时候突然变回去」)
        if !ghost {
            self.goal = None;
            self.last = None;
            return false;
        }
        let in_wall = grid.is_wall(here.0, here.1);
        if self.goal.is_none() {
            let foe = foes.iter().copied().min_by(|a, b| dist(here, *a).total_cmp(&dist(here, *b)));
            if let Some(to) = foe.and_then(|f| through(grid, here, f)) {
                self.goal = Some(to);
                let ticks = (dist(here, to) / speed).ceil().max(1.0);
                let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
                cc.dx = (to.0 - here.0).round() as i64;
                cc.dy = (to.1 - here.1).round() as i64;
                cc.speed = (dist(here, to) / ticks).ceil() as u64;
                sim.apply_cc(me, &cc);
                log(sim, format!("shadow step through the wall: ({:.0}, {:.0}) -> ({:.0}, {:.0}), {} ticks", here.0, here.1,
                    to.0, to.1, ticks));
            }
        } else if let Some(to) = self.goal {
            let d = dist(here, to);
            if d < speed {
                self.goal = None;
            } else if self.last.is_some_and(|l| dist(l, here) < 1.0) {
                // the host did not move him (stopped at the wall): a step of his own
                let next = (here.0 + (to.0 - here.0) / d * speed, here.1 + (to.1 - here.1) / d * speed);
                sim.entity_set_pos(me, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64);
            }
        }
        self.last = Some(here);
        in_wall
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_moba_map_has_its_ninety_wall_cells() {
        let g = &Grid::builtin()[0];
        assert_eq!(g.cells.iter().flatten().filter(|w| **w).count(), 90);
        assert!(g.is_wall(15.5 * CELL, 3.5 * CELL));
        assert!(!g.is_wall(0.5 * CELL, 0.5 * CELL));
    }

    #[test]
    fn he_cuts_through_only_when_a_wall_is_between() {
        let g = Grid::from_rows(&["....", ".#..", "....", "...."]);
        let a = (0.5 * CELL, 1.5 * CELL);
        let b = (2.5 * CELL, 1.5 * CELL);
        assert!(g.crosses(a, b));
        assert!(through(&g, a, b).is_some());
        let c = (2.5 * CELL, 3.5 * CELL);
        assert!(!g.crosses((0.5 * CELL, 3.5 * CELL), c));
        assert!(through(&g, (0.5 * CELL, 3.5 * CELL), c).is_none());
        // too close to bother
        assert!(through(&g, (1.0 * CELL, 1.5 * CELL), (1.6 * CELL, 1.5 * CELL)).is_none());
    }
}
