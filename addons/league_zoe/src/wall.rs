//! 催眠气泡飞过墙飞得更远（0.8.0，用户 2026-11-20：「按照你的建议改吧」）。
//!
//! 英雄联盟的气泡能穿过一次地形，穿墙的那一段不算射程（"travels the entire distance as bonus range"），再碰到墙就提前
//! 落下。数据的投射物射程是死的，所以副本里放两颗气泡：平常的 `e_len`，和长 `e_wall` 的那颗；她开始踢（目标身上挂着
//! `league_zoe_e_aim`）时这里看她到目标这条线，前 `e_len` 的空地以内有一段墙、能穿出去，就给她挂 `league_zoe_e_far`，
//! 出手时数据踢长的那颗。墙是游戏内置的格子（`maps.rs`，同闪现的落点）：三张图里挑英雄站进墙里最少的那张（斯卡纳附加包的
//! 挑法）。召唤师峡谷（Rin 的地图 mod，0.1.65 起）用作者的墙体文件（`game_places::terrain::rift_walls`，地形本身，不是往外长
//! 一格的站位格），没有这个文件时峡谷上不踢长的那颗。

use super::Pt;

const CELL: f64 = 32_000.0;
/// 沿线一步看多远。
const STEP: f64 = 1_000.0;
/// 墙这么薄以下不算（擦着墙角过去）。
pub const WALL_MIN: f64 = 4_000.0;

/// 这一点在墙里吗（地图外也算）。
pub fn is_wall(rows: &[&str], x: f64, y: f64) -> bool {
    if x < 0.0 || y < 0.0 {
        return true;
    }
    let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
    rows.get(cy).and_then(|r| r.as_bytes().get(cx)).is_none_or(|c| *c == b'#')
}

/// 这场用的是哪张图：内置的 5v5、单线、死斗里，英雄站进墙里最少的那张（一样多就要墙多的）。
pub fn grid_of(champions: &[Pt]) -> &'static [&'static str] {
    let maps: [&'static [&'static str]; 3] = [&super::maps::MOBA, &super::maps::SINGLE_LANE, &super::maps::DEATH_MATCH];
    let walls = |g: &[&str]| g.iter().map(|r| r.bytes().filter(|c| *c == b'#').count()).sum::<usize>();
    maps.into_iter()
        .min_by_key(|g| (champions.iter().filter(|p| is_wall(g, p.0, p.1)).count(), std::cmp::Reverse(walls(g))))
        .unwrap_or(&super::maps::MOBA)
}

/// 气泡从 `from` 朝 `to` 踢出去，前 `open` 的空地以内碰到的第一段墙有多长（能从另一边穿出去才算，地图边上的不算）。
/// 没有墙、墙太薄（`WALL_MIN` 以下）或者穿不出去就是 None。墙是游戏自己的格子 `rows`（960000 见方）。
pub fn crossing(rows: &[&str], from: Pt, to: Pt, open: f64) -> Option<f64> {
    crossing_by(|x, y| is_wall(rows, x, y), 960_000.0, from, to, open)
}

/// 同 [`crossing`]，墙由 `wall` 说，地图 `side` 见方（峡谷：作者的墙体文件、1937454）。
pub fn crossing_by(wall: impl Fn(f64, f64) -> bool, side: f64, from: Pt, to: Pt, open: f64) -> Option<f64> {
    let (dx, dy) = (to.0 - from.0, to.1 - from.1);
    let l = (dx * dx + dy * dy).sqrt();
    if l < 1.0 {
        return None;
    }
    let (ux, uy) = (dx / l, dy / l);
    let mut used = 0.0;
    let mut t = 0.0;
    let mut entered: Option<f64> = None;
    // 墙里那段不算射程，最远看到出了地图为止
    while t < side * 1.5 {
        t += STEP;
        let (x, y) = (from.0 + ux * t, from.1 + uy * t);
        let outside = x < 0.0 || y < 0.0 || x >= side || y >= side;
        if outside {
            return None;
        }
        let w = wall(x, y);
        match (entered, w) {
            (None, true) => {
                if used >= open {
                    return None;
                }
                entered = Some(t);
            }
            (Some(t0), false) => {
                let run = t - t0;
                return (run >= WALL_MIN).then_some(run);
            }
            (None, false) => {
                used += STEP;
                if used >= open {
                    return None;
                }
            }
            (Some(_), true) => {}
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    const ROWS: [&str; 4] = ["..........", "....##....", "..........", ".........."];

    #[test]
    fn a_wall_in_reach_is_crossed_its_length_is_the_bonus() {
        // row 1 has wall cells 4-5 (x 128000..192000): from x 40000 straight right, the wall starts 88000 in - beyond 85000
        // of open ground, so no; from 70000 it starts 58000 in and is 64000 thick
        let y = 1.5 * CELL;
        assert_eq!(crossing(&ROWS, (40_000.0, y), (300_000.0, y), 85_000.0), None);
        let run = crossing(&ROWS, (70_000.0, y), (300_000.0, y), 85_000.0).unwrap();
        assert!((run - 64_000.0).abs() <= STEP, "{run}");
        // the row below has no wall: nothing to cross
        assert_eq!(crossing(&ROWS, (70_000.0, 2.5 * CELL), (300_000.0, 2.5 * CELL), 85_000.0), None);
    }

    /// 峡谷（0.1.65，1937454 见方）：墙由作者的墙体文件说，960000 以外照样能穿；出了峡谷才算到边。
    #[test]
    fn on_the_rift_the_walls_file_and_its_side() {
        // a wall 30000 thick at x 1300000..1330000 across the whole map's height
        let wall = |x: f64, _y: f64| (1_300_000.0..1_330_000.0).contains(&x);
        let side = 1_937_454.0;
        let run = crossing_by(wall, side, (1_250_000.0, 1_500_000.0), (1_500_000.0, 1_500_000.0), 85_000.0).unwrap();
        assert!((run - 30_000.0).abs() <= STEP, "{run}");
        // the game's own map ends at 960000: the same kick out there is off its map
        assert_eq!(crossing_by(wall, 960_000.0, (1_250_000.0, 1_500_000.0), (1_500_000.0, 1_500_000.0), 85_000.0), None);
        // the Rift's edge
        assert_eq!(crossing_by(|_, _| false, side, (1_900_000.0, 800_000.0), (2_100_000.0, 800_000.0), 85_000.0), None);
    }

    #[test]
    fn running_into_the_map_edge_is_no_crossing() {
        assert_eq!(crossing(&ROWS, (250_000.0, 50_000.0), (400_000.0, 50_000.0), 85_000.0), None);
    }

    #[test]
    fn the_match_map_is_the_one_nobody_stands_in_a_wall_of() {
        // the death match arena is rows 12-17, columns 6-23: a champion at (480000, 470000) stands on open ground in all three,
        // one at (100000, 100000) in a wall of the single lane and the death match only
        let g = grid_of(&[(480_000.0, 470_000.0), (100_000.0, 100_000.0)]);
        assert_eq!(g.len(), 30);
        assert!(!is_wall(g, 100_000.0, 100_000.0));
        assert_eq!(g[3], super::super::maps::MOBA[3]);
    }
}
