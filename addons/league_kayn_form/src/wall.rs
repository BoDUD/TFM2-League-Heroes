//! 掠影步穿墙（2026-10-06，用户：「穿墙的逻辑要改 该穿的时候不穿 你要看游戏里地图设置的」）。
//!
//! 主包的掠影步（Q 转完 2 秒，buff `league_kayn_ghost`）给了 `ignore_wall`，可宿主的寻路是事先算好的、永远绕开
//! 墙格，所以凯隐从不穿过树林里的墙抄近路。地图的墙：引擎的碰撞墙，30×30 格、每格 32000，`walls[y][x]`
//! （5v5 共 90 格，都在原画最深的树林里；卡蜜尔钩墙附加包的 `maps.rs`，game_core 0.5.1 的 MapDef，0.6.2 相同）。
//!
//! 掠影步期间每 tick 看一次：离他最近的敌方英雄在 `CHASE` 内、隔着墙格（两人之间的直线穿过墙）而且不贴身，就朝他
//! 笔直穿过去——引擎的强制位移（`ForceMove`，宿主就不再按寻路挪他），速度是他现在的移速；宿主没把他挪动时（撞墙停了）
//! 逐 tick 自己走一步（`entity_set_pos`）。掠影步结束、人到了、或者人死了就停。
//!
//! 召唤师峡谷（2026-11-10，第三方地图 mod `tfm2_lol_map_test`，用户：「要同时兼容原版地图和这个地图」）：塔站在 1000000 以外
//! （`game_places::terrain::map_of_sim`）就是峡谷，墙是作者的墙体坐标.json（[`rift_grid`]：自己的格子边长 72000/11 和原点）；
//! 没有这个文件时不知道哪里有墙，掠影步不穿墙、也不在墙里。
//! 2026-11-28（巴德的门同一个毛病）：峡谷上分两层（[`rift_layers`]）——「隔着墙」和墙里的暗影雾看真墙（`rift_walls`），
//! 落点站不站得住看墙往外长一格的那层（`rift_ground`）。以前都拿长了一格的那层：贴着墙边走也算隔墙、也挂暗影雾
//! （0.1.86 的墙上每个空地朝 8 个方向 60000 外的人：418 次隔墙冲刺有 250 次中间一格真墙都没有）。

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::LazyLock;

use game_places::terrain::{map_of_sim, rift_status, rift_ground, rift_walls, Map, Walls};
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

/// 一张墙格子：`cells[y][x]`，每格 `cell` 见方、第 (0, 0) 格的角在 `origin`（游戏自己的图 32000、(0, 0)；峡谷 72000/11、
/// (36000/11, 0)）。`cells` 是英雄中心站不住的格子，`rock` 是真墙。游戏自己的图两者一样（`rock` 为 None）；峡谷上 `cells`
/// 是墙往外长一格（`rift_ground`），`rock` 是墙体文件本身的墙（`rift_walls`）。
#[derive(Clone, Debug, PartialEq)]
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
    pub cell: f64,
    pub origin: (f64, f64),
    pub rock: Option<Vec<Vec<bool>>>,
}

impl Grid {
    pub fn from_rows(rows: &[&str]) -> Grid {
        Grid {
            cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(),
            cell: CELL,
            origin: (0.0, 0.0),
            rock: None,
        }
    }

    /// 峡谷的墙（墙体坐标.json 读出来的）：它自己的格子边长和原点。
    pub fn from_walls(w: &Walls) -> Grid {
        Grid { cells: w.cells.clone(), cell: w.cell, origin: w.origin, rock: None }
    }

    pub fn builtin() -> [Grid; 3] {
        [Grid::from_rows(&maps::MOBA), Grid::from_rows(&maps::SINGLE_LANE), Grid::from_rows(&maps::DEATH_MATCH)]
    }

    /// 世界坐标落在墙格里吗（英雄中心站不住；地图外不算：只关心树林里的墙）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        self.at_layer(&self.cells, x, y)
    }

    /// 世界坐标落在真墙里吗（游戏自己的图就是 [`Grid::is_wall`]）。
    pub fn is_rock(&self, x: f64, y: f64) -> bool {
        self.at_layer(self.rock.as_ref().unwrap_or(&self.cells), x, y)
    }

    fn at_layer(&self, layer: &[Vec<bool>], x: f64, y: f64) -> bool {
        let (fx, fy) = ((x - self.origin.0) / self.cell, (y - self.origin.1) / self.cell);
        if fx < 0.0 || fy < 0.0 {
            return false;
        }
        let (cx, cy) = (fx as usize, fy as usize);
        layer.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(false)
    }

    /// 两点之间的直线穿过真墙吗（两端不算）。
    pub fn crosses(&self, a: (f64, f64), b: (f64, f64)) -> bool {
        let d = dist(a, b);
        let n = (d / STEP).floor() as usize;
        (1..n).any(|i| {
            let t = i as f64 / n as f64;
            self.is_rock(a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
        })
    }
}

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 峡谷上的墙：墙体文件的（[`Grid::from_walls`]），没有文件时一格墙都没有（不知道哪里有墙）。
pub fn rift_grid(walls: Option<&Walls>) -> Grid {
    walls.map_or_else(|| Grid { cells: Vec::new(), cell: Map::Rift.extent(), origin: (0.0, 0.0), rock: None }, Grid::from_walls)
}

/// 峡谷的两层：站不住的格子（`ground`，墙往外长一格）和真墙（`rock`，墙体文件）。缺一层就只用另一层（和以前一样）。
pub fn rift_layers(rock: Option<&Walls>, ground: Option<&Walls>) -> Grid {
    match (rock, ground) {
        (Some(r), Some(g)) if r.cells.len() == g.cells.len() && r.cell == g.cell && r.origin == g.origin => {
            Grid { rock: Some(r.cells.clone()), ..Grid::from_walls(g) }
        }
        (_, Some(g)) => rift_grid(Some(g)),
        (r, None) => rift_grid(r),
    }
}

/// 他站在墙里吗（挂穿墙的暗影雾）：真墙里才算，峡谷上贴着墙边那一圈不算。
pub fn in_rock(grid: &Grid, at: (f64, f64)) -> bool {
    grid.is_rock(at.0, at.1)
}

/// 峡谷的墙，换成本包的格子一次（87000 多格，不每 tick 重建）。
static RIFT_GRID: LazyLock<Grid> = LazyLock::new(|| rift_layers(rift_walls(), rift_ground()));
/// 这次启动已经在日志里说过峡谷了。
static RIFT_SEEN: AtomicBool = AtomicBool::new(false);

/// 猜地图用的点：所有活着的单位（英雄、小兵、野怪、塔……）。只看英雄的话，大家都站在三张图都空着的那条斜带上
/// （中路、两边泉水）时打平，平手偏向墙多的单线 / 死斗图，5v5 就猜错了（2026-11-01 复查：波比的 R 有 7 次退回击退）；
/// 5v5 边路的兵和野区的野怪几乎一直在，正好落在另两张图的墙里。
/// 掠影步时凯隐自己在墙里，不算他。
fn unit_points(sim: &StableSim<'_>, me: usize) -> Vec<(f64, f64)> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_alive() && u.id() != me)
        .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
        .collect()
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

/// Crowd control that holds a unit in place - from game 0.7.0 also when laid by native code ("movement continuing while
/// rooted" fixed): root, stun (a Sleep reaches add-ons as a Stun), knock-up, taunt, fear, charm; not a dash's own
/// ForceMove nor a cast's Animation. A step of our own while one of these is on would move him through it.
const HELD: [CcKindV1; 6] =
    [CcKindV1::Bind, CcKindV1::Stun, CcKindV1::Airborne, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];

fn held(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).filter_map(|i| e.cc_at(i)).any(|c| HELD.iter().any(|k| k.code() == c.kind))
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    sim.get_entity(id).map(|e| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

/// 三张图的墙格（[`Grid::builtin`]）：只建一次。
static GRIDS: LazyLock<[Grid; 3]> = LazyLock::new(Grid::builtin);

/// 每个凯隐一份（在被动里）：正在穿往哪里。
#[derive(Clone, Debug, Default)]
pub struct Walker {
    pub goal: Option<(f64, f64)>,
    pub last: Option<(f64, f64)>,
}

impl Walker {
    /// 每 tick：掠影步期间隔墙追人。返回这一 tick 他是否站在墙格里（给完整变身的「墙里的暗影」用）。
    pub fn update(&mut self, sim: &mut StableSim<'_>, me: usize, ghost: bool, log: &dyn Fn(&StableSim<'_>, String)) -> bool {
        // 不在掠影步、也没有正在走的路：往下算完也只是把两样本来就空的记录清掉、返回 false，直接回（2026-11-22 过日采样：
        // 原来每 tick 都先把三张图的墙格重建一遍、把场上的人收一遍）
        if !ghost && self.goal.is_none() && self.last.is_none() {
            return false;
        }
        let Some(here) = pos(sim, me) else { return false };
        let Some(k) = sim.get_entity(me) else { return false };
        let team = k.team();
        let speed = (k.stat().move_speed as f64).max(500.0);
        let mut foes = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || !e.is_alive() {
                continue;
            }
            let (x, y) = e.pos();
            let p = (x as f64, y as f64);
            if e.team() != team && e.is_targetable() {
                foes.push(p);
            }
        }
        // the Rift (towers past 1000000): its walls, converted once - never the game's own grids
        let grid: &Grid = if map_of_sim(sim) == Map::Rift {
            if !RIFT_SEEN.swap(true, Ordering::Relaxed) {
                super::wlog(format!("== Rift: Kayn's Shadow Step cuts through the Rift's rock (landings clear of the walls grown \
                                     by a cell; rock layer {}; none known without the walls file: no cut, no in-wall shadow); \
                                     {} ==", if RIFT_GRID.rock.is_some() { "on" } else { "missing" }, rift_status()));
            }
            &RIFT_GRID
        } else {
            let grids = &*GRIDS;
            let Some(gi) = current(grids, &unit_points(sim, me)) else { return false };
            &grids[gi]
        };
        // only during the Shadow Step: walking by the jungle his spot often falls on a wall cell (the cells are coarse),
        // and the in-wall shadow showed then - dark with red sparks, at level 1-2, gone again a moment later, it looked
        // like a transformation (「打野2级就变身了」, 「一帧变身后 又释放技能的时候突然变回去」)
        if !ghost {
            self.goal = None;
            self.last = None;
            return false;
        }
        let in_wall = in_rock(grid, here);
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
            } else if self.last.is_some_and(|l| dist(l, here) < 1.0)
                && sim.get_entity(me).is_some_and(|e| e.is_targetable() && !held(&e))
            {
                // the host did not move him (stopped at the wall): a step of his own - not while banished (game 0.6.4:
                // a banished unit does not move) nor held by crowd control ([`HELD`], game 0.7.0: native roots and stuns
                // stop a unit too); the goal stays and the steps go on once it is over
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

    /// A Rift-sized walls file as the author lays it out (355 x 356 cells of 60000/11 from x = 30000/11), its own border
    /// cells walls, plus every cell in columns `xs`, rows `ys`.
    fn rift_file(xs: std::ops::Range<usize>, ys: std::ops::Range<usize>) -> Walls {
        let rows: Vec<String> = (0..356)
            .map(|y| {
                (0..355)
                    .map(|x| {
                        let border = x == 0 || y == 0 || x == 354 || y == 355;
                        if border || (xs.contains(&x) && ys.contains(&y)) { '#' } else { '.' }
                    })
                    .collect()
            })
            .collect();
        let rows: Vec<&str> = rows.iter().map(String::as_str).collect();
        let side = Map::Rift.extent();
        Walls::from_rows(&rows, 60_000.0 / 11.0, (30_000.0 / 11.0, 0.0), (side, side))
    }

    #[test]
    fn on_the_rift_he_cuts_through_its_walls() {
        // a wall block in the Rift's far half: columns 220-222 (x 1202727-1219091), rows 200-239 (y 1090909-1309091)
        let walls = rift_file(220..223, 200..240);
        let g = rift_grid(Some(&walls));
        assert_eq!((g.cell, g.origin), (walls.cell, walls.origin));
        let (me, foe) = ((1_180_000.0, 1_200_000.0), (1_240_000.0, 1_200_000.0));
        assert!(g.crosses(me, foe) && g.is_wall(1_210_000.0, 1_200_000.0) && !g.is_wall(me.0, me.1));
        let to = through(&g, me, foe).expect("through the Rift wall");
        assert!(!g.is_wall(to.0, to.1) && to.0 > 1_219_090.0 && to.0 < foe.0, "{to:?}");
        // the game's own grid knows nothing out there (past 960000 is off it): no cut
        let moba = &Grid::builtin()[0];
        assert!(!moba.crosses(me, foe) && through(moba, me, foe).is_none());
    }

    #[test]
    fn the_rift_has_none_of_the_games_own_walls() {
        // row 3, columns 15-16 and 18-21 of the game's own map (y 96000-128000): walls there, open ground on the Rift
        let (me, foe) = ((470_000.0, 112_000.0), (550_000.0, 112_000.0));
        let moba = &Grid::builtin()[0];
        let rift = rift_grid(Some(&rift_file(0..0, 0..0)));
        assert!(moba.crosses(me, foe) && through(moba, me, foe).is_some());
        assert!(!rift.crosses(me, foe) && through(&rift, me, foe).is_none());
        assert!(moba.is_wall(15.5 * CELL, 3.5 * CELL) && !rift.is_wall(15.5 * CELL, 3.5 * CELL));
        // with no walls file nothing is known: no cut anywhere, never in a wall
        let none = rift_grid(None);
        let blocked = rift_file(220..223, 200..240);
        for (a, b) in [(me, foe), ((1_180_000.0, 1_200_000.0), (1_240_000.0, 1_200_000.0))] {
            assert!(!none.crosses(a, b) && through(&none, a, b).is_none());
        }
        assert!(blocked.is_wall(1_210_000.0, 1_200_000.0) && !none.is_wall(1_210_000.0, 1_200_000.0));
    }

    #[test]
    fn on_the_rift_he_cuts_only_through_rock_not_the_ground_round_it() {
        // 真墙：220..222 列、200..239 行（x 1202727..1219091）；站不住的那层是它往外长一格（峡谷的 rift_ground 那样）
        let rock = rift_file(220..223, 200..240);
        let ground = rock.padded();
        let (g, old) = (rift_layers(Some(&rock), Some(&ground)), rift_grid(Some(&ground)));
        assert!(g.rock.is_some() && old.rock.is_none());
        // 隔着真墙：照旧穿过去，落在长出来的那一圈外面
        let (me, foe) = ((1_180_000.0, 1_200_000.0), (1_240_000.0, 1_200_000.0));
        let to = through(&g, me, foe).expect("through the rock");
        assert!(!g.is_wall(to.0, to.1) && to.0 > 1_224_545.0 && to.0 < foe.0, "{to:?}");
        // 贴着墙的上沿（199 行只是长出来的那一圈）：中间一格真墙都没有。以前当成隔墙冲过去，现在不冲
        let (me, foe) = ((1_180_000.0, 1_088_000.0), (1_240_000.0, 1_088_000.0));
        assert!(old.crosses(me, foe) && through(&old, me, foe).is_some(), "the old grid cut here");
        assert!(!g.crosses(me, foe) && through(&g, me, foe).is_none());
        // 暗影雾：真墙里才挂；走在墙边那一圈里不挂（以前挂）
        let edge = (1_200_000.0, 1_200_000.0);
        assert!(in_rock(&g, (1_210_000.0, 1_200_000.0)) && g.is_wall(edge.0, edge.1));
        assert!(!in_rock(&g, edge) && in_rock(&old, edge));
        // 游戏自己的图只有一层，照旧
        let moba = &Grid::builtin()[0];
        assert!(moba.rock.is_none() && in_rock(moba, (15.5 * CELL, 3.5 * CELL)));
    }

    /// 峡谷真的墙（设了 `LEAGUE_RIFT_WALLS` 才跑）：游戏里的两层。每个空地朝八个方向 60000 外的人：以前只拿长了一格的
    /// 那层，有的「隔墙」冲刺中间一格真墙都没有；现在每次都隔着真墙、落在站得住的地方。
    #[test]
    fn on_the_rifts_real_rock_every_cut_is_through_rock() {
        let Some(path) = std::env::var_os(game_places::terrain::RIFT_WALLS_ENV) else { return };
        let rock = game_places::terrain::load_rift_walls(&[path.into()]).unwrap();
        let ground = rock.padded();
        let (old, g) = (rift_grid(Some(&ground)), rift_layers(Some(&rock), Some(&ground)));
        assert!(g.rock.is_some());
        let side = Map::Rift.extent();
        let (mut spots, mut old_n, mut old_bad, mut new_n) = (0, 0, 0, 0);
        let mut y = 20_000.0;
        while y < side {
            let mut x = 20_000.0;
            while x < side {
                if !g.is_wall(x, y) {
                    spots += 1;
                    for k in 0..8 {
                        let a = k as f64 * std::f64::consts::TAU / 8.0;
                        let foe = (x + 60_000.0 * a.cos(), y + 60_000.0 * a.sin());
                        if g.is_wall(foe.0, foe.1) || !(0.0..side).contains(&foe.0) || !(0.0..side).contains(&foe.1) {
                            continue;
                        }
                        if through(&old, (x, y), foe).is_some() {
                            old_n += 1;
                            old_bad += usize::from(!g.crosses((x, y), foe));
                        }
                        if let Some(to) = through(&g, (x, y), foe) {
                            new_n += 1;
                            assert!(g.crosses((x, y), foe) && !g.is_wall(to.0, to.1), "({x},{y}) -> {foe:?}: {to:?}");
                        }
                    }
                }
                x += 40_000.0;
            }
            y += 40_000.0;
        }
        println!("{spots} spots: the old grid's {old_n} cuts, {old_bad} with no rock between; now {new_n} cuts");
        assert!(spots > 300 && old_bad > 0 && new_n > 100, "{spots} spots, {old_bad} of {old_n} old, {new_n} new");
    }
}
