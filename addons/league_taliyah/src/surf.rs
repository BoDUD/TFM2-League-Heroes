//! 浮石冲贴着地形加速（0.2.8，用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」，再说「接着做」：能做的
//! 小项都做）。
//!
//! 英雄联盟的浮石冲（被动）："While near terrain"，按等级 10% / 15% / 25% / 40% 的移速；在地形旁边待满 0.4 秒后 1 秒内渐强，
//! 离开地形 3 秒后以同样的速度渐弱；放技能、进入英雄间的交战时停几秒（静态冷却 2）；她自己立的墙也算地形。主包是纯数据，
//! 数据读不到地图上的墙，所以是「脱战时 +10%」（交战 = 她打中英雄后 `f_t` tick 内，主包的 `league_taliyah_fight`）。
//!
//! 副本（`native=1`）不再由数据挂加速的 `league_taliyah_surf`，改由这里每 tick 判断：
//! - **贴着地形**：她离地图的墙格（游戏自己的 5v5 图：league_camille_wall 的 `maps.rs`，每格 32000，加上四边画出来的墙面；
//!   召唤师峡谷：墙体文件读得到才有，读不到就没有地形）或她立着的墙幔（本包的 [`super::Wall`]）在 `NEAR` 以内；
//! - **交战 / 放技能**：身上有主包的 `league_taliyah_fight`，或者技能、技能 2、大招的冷却刚跳起来（`CAST_BLOCK` tick 内）：
//!   加速立刻没了；
//! - 渐强渐弱照英雄联盟：贴着地形连着 `ARM` tick 后每 tick 涨一点，`BUILD` tick 到满；离开地形 `LINGER` tick 后每 tick 落一点；
//! - 满的时候是 [`level_ms`]：英雄联盟的四档摊到这个游戏的 1–12 级，每 3 级一档。
//!
//! 有加速时她身上挂一个没有数值的主包 `league_taliyah_surf`（它的画面照旧：她脚下的石头），加速一直挂着它不动；移速放在另一个
//! 没有画面的 `SPEED` 上，数值变了只换它（0.1.0 复审：渐强的 1 秒里每 tick 摘了重挂带画面的那一个，石头的循环画面可能一直从头放、
//! 一顿一顿的）。脱战骑石头的动作（`view.rs`）照旧按「没在打架」换（用户 2026-11-14：「保持现在」），只有加速跟着墙走。
//! 放完墙幔的 +40%（主包的 `league_taliyah_r_surf`）照旧是数据的。

use std::sync::{Arc, LazyLock};

use game_places::terrain::{self as places, Map, Walls};
use mod_api_stable::*;

use super::{counted, head, inside, maps, wlog, Wall};

/// 「贴着地形」：离墙格（或她的墙）这么近以内（一格墙的边长）。
pub const NEAR: f64 = 32_000.0;
/// 贴着地形连着这么多 tick 才开始涨（英雄联盟 0.4 秒）；从 0 涨到满、从满落到 0 要这么多 tick（1 秒）。
pub const ARM: usize = 24;
pub const BUILD: usize = 60;
/// 离开地形这么多 tick 后才开始落（英雄联盟 3 秒）。
pub const LINGER: usize = 180;
/// 放了技能后这么多 tick 没有加速（英雄联盟的静态冷却 2 秒）。
pub const CAST_BLOCK: usize = 120;
/// 满的时候的移速 %：1–3 级、4–6 级、7–9 级、10–12 级（英雄联盟 10% / 15% / 25% / 40%）。
pub const LEVEL_MS: [i32; 4] = [10, 15, 25, 40];
/// 有加速时挂着的主包旗子（画面绑在它身上，本包挂的不带数值）；移速放在这个没有画面的 buff 上；交战中的旗子（主包）。
pub const BUFF: &str = "league_taliyah_surf";
pub const SPEED: &str = "league_taliyah_surf_ms";
pub const FIGHT: &str = "league_taliyah_fight";
/// 游戏自己的 5v5 图四边画出来的墙面（league_camille_wall 量的；league_zeri 的 `MOBA_BOUNDS`）。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);
/// 游戏自己的墙格边长。
pub const CELL: f64 = 32_000.0;

/// 满的时候的移速 %（她的等级）。
pub fn level_ms(level: usize) -> i32 {
    LEVEL_MS[((level.clamp(1, 12) - 1) / 3).min(3)]
}

/// 一张墙格子：`cells[y][x]` 为 true 是墙，每格 `cell` 见方、第 (0, 0) 格的角在 `origin`；格子外算墙；`bounds` 外是 5v5
/// 地图四边的墙面。
#[derive(Clone, Debug, PartialEq)]
pub struct Ground {
    pub cells: Vec<Vec<bool>>,
    pub cell: f64,
    pub origin: (f64, f64),
    pub bounds: Option<(f64, f64, f64, f64)>,
}

impl Ground {
    pub fn from_rows(rows: &[&str], bounds: Option<(f64, f64, f64, f64)>) -> Ground {
        Ground { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(), cell: CELL, origin: (0.0, 0.0), bounds }
    }

    /// 峡谷的墙（墙体文件读出来的）：它自己的格子边长和原点。
    pub fn from_walls(w: &Walls) -> Ground {
        Ground { cells: w.cells.clone(), cell: w.cell, origin: w.origin, bounds: None }
    }

    /// 游戏自己的三张图（5v5 加四边的墙面）。
    pub fn builtin() -> Vec<(&'static str, Ground)> {
        vec![
            ("Moba", Ground::from_rows(&maps::MOBA, Some(MOBA_BOUNDS))),
            ("SingleLane", Ground::from_rows(&maps::SINGLE_LANE, None)),
            ("DeathMatch", Ground::from_rows(&maps::DEATH_MATCH, None)),
        ]
    }

    fn wall_cell(&self, cx: i64, cy: i64) -> bool {
        if cx < 0 || cy < 0 {
            return true;
        }
        self.cells.get(cy as usize).and_then(|row| row.get(cx as usize)).copied().unwrap_or(true)
    }

    /// 墙格（或格子外）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        self.wall_cell(((x - self.origin.0) / self.cell).floor() as i64, ((y - self.origin.1) / self.cell).floor() as i64)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|v| **v).count()
    }

    /// `p` 离墙格（或四边的墙面）在 `r` 以内。
    pub fn near(&self, p: (f64, f64), r: f64) -> bool {
        if let Some((x0, y0, x1, y1)) = self.bounds {
            if p.0 - x0 <= r || p.1 - y0 <= r || x1 - p.0 <= r || y1 - p.1 <= r {
                return true;
            }
        }
        let c = self.cell;
        let (ox, oy) = self.origin;
        let cx = |x: f64| ((x - ox) / c).floor() as i64;
        let cy = |y: f64| ((y - oy) / c).floor() as i64;
        for gy in cy(p.1 - r)..=cy(p.1 + r) {
            for gx in cx(p.0 - r)..=cx(p.0 + r) {
                if !self.wall_cell(gx, gy) {
                    continue;
                }
                let (rx0, ry0) = (ox + gx as f64 * c, oy + gy as f64 * c);
                let dx = (rx0 - p.0).max(0.0).max(p.0 - (rx0 + c));
                let dy = (ry0 - p.1).max(0.0).max(p.1 - (ry0 + c));
                if dx * dx + dy * dy <= r * r {
                    return true;
                }
            }
        }
        false
    }
}

/// 游戏自己的图：站进墙里的单位最少的那张，一样少时墙最多的（league_zeri 的 `pick_grid`）。
pub fn pick(points: &[(f64, f64)]) -> (&'static str, Ground) {
    Ground::builtin()
        .into_iter()
        .map(|(n, g)| (points.iter().filter(|p| g.is_wall(p.0, p.1)).count(), g.walls(), n, g))
        .min_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)))
        .map(|(_, _, n, g)| (n, g))
        .expect("three built-in maps")
}

/// 峡谷的墙，换成本包的格子一次。
static RIFT: LazyLock<Option<Arc<Ground>>> = LazyLock::new(|| places::rift_ground().map(|w| Arc::new(Ground::from_walls(w))));

/// 渐强渐弱：贴着地形连着几 tick、离开几 tick、现在几成（0..=`BUILD`）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Ramp {
    pub near_for: usize,
    pub away_for: usize,
    pub power: usize,
}

/// 走一 tick：`near` 贴着地形，`combat` 交战或刚放技能（加速立刻没了）。
pub fn step(r: Ramp, near: bool, combat: bool) -> Ramp {
    if combat {
        return Ramp { near_for: if near { 1 } else { 0 }, away_for: if near { 0 } else { LINGER }, power: 0 };
    }
    if near {
        let near_for = r.near_for + 1;
        let power = if near_for >= ARM { (r.power + 1).min(BUILD) } else { r.power };
        Ramp { near_for, away_for: 0, power }
    } else {
        let away_for = r.away_for + 1;
        let power = if away_for >= LINGER { r.power.saturating_sub(1) } else { r.power };
        Ramp { near_for: 0, away_for, power }
    }
}

/// 现在的移速 %（她的等级、几成）。
pub fn bonus(level: usize, power: usize) -> i32 {
    level_ms(level) * power.min(BUILD) as i32 / BUILD as i32
}

/// 这一 tick 要对两个 buff 做什么：移速 `shown` -> `want`、画面旗子在不在（`view`）。(重挂移速的 buff, 挂上画面, 摘掉画面)：
/// 画面只在加速从无到有时挂、到 0 时摘，加速涨落时不碰它。
pub fn changes(shown: i32, want: i32, view: bool) -> (bool, bool, bool) {
    (want != shown, want > 0 && !view, want == 0 && view)
}

/// 一个塔莉垭的浮石冲（被动里的一份）。
#[derive(Clone, Default)]
pub struct Rock {
    ramp: Ramp,
    /// 挂着的移速 %（0：没挂）。
    shown: i32,
    /// 技能、技能 2、大招上一 tick 的剩余冷却；放了技能后到这一 tick 为止没有加速。
    last_cd: Option<(usize, usize, usize)>,
    block_until: usize,
    /// 这一局的墙（看过一次；`None`：没有地形可读——峡谷没有墙体文件）。
    ground: Option<Option<Arc<Ground>>>,
}

impl Rock {
    pub fn reset(&mut self) {
        self.ramp = Ramp { away_for: LINGER, ..Ramp::default() };
        self.shown = 0;
        self.last_cd = None;
        self.block_until = 0;
    }

    fn ground(&mut self, sim: &StableSim<'_>, me: usize) -> Option<Arc<Ground>> {
        if self.ground.is_none() {
            let g = match places::map_of_sim(sim) {
                Map::Rift => RIFT.clone(),
                Map::Native => {
                    let points: Vec<(f64, f64)> = (0..sim.entity_count())
                        .filter_map(|i| sim.entity_at(i))
                        .filter(|e| e.is_alive())
                        .map(|e| (e.pos().0 as f64, e.pos().1 as f64))
                        .collect();
                    let (name, g) = pick(&points);
                    if let Some(k) = counted("ground") {
                        wlog(format!("{} SURF ground: {name} ({} wall cells) #{k}", head(sim, me), g.walls()));
                    }
                    Some(Arc::new(g))
                }
            };
            self.ground = Some(g);
        }
        self.ground.clone().flatten()
    }

    /// 每 tick（她活着）：贴着地形、没在交战就渐强，挂上 / 换掉 / 摘掉主包的 `league_taliyah_surf`。
    pub fn tick(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize, walls: &[Wall]) {
        let Some((at, level, fight, view, cd)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| {
            let (mut fight, mut view) = (false, false);
            for b in (0..e.buff_count()).filter_map(|i| e.buff_at(i)) {
                fight |= b.name() == FIGHT;
                view |= b.name() == BUFF;
            }
            let rem = |s: SkillSlotV1| e.cooldown(s).map_or(0, |c| c.remaining);
            (e.pos(), e.level(), fight, view, (rem(SkillSlotV1::Skill), rem(SkillSlotV1::Skill2), rem(SkillSlotV1::Ult)))
        }) else {
            return;
        };
        if let Some(was) = self.last_cd {
            if cd.0 > was.0 + 5 || cd.1 > was.1 + 5 || cd.2 > was.2 + 5 {
                self.block_until = now + CAST_BLOCK;
            }
        }
        self.last_cd = Some(cd);
        let p = (at.0 as f64, at.1 as f64);
        let by_wall = self.ground(sim, me).is_some_and(|g| g.near(p, NEAR));
        let by_own = walls.iter().any(|w| inside(w, at, NEAR as u64));
        let combat = fight || now < self.block_until;
        let before = self.ramp.power;
        self.ramp = step(self.ramp, by_wall || by_own, combat);
        let want = bonus(level, self.ramp.power);
        let (speed, view_on, view_off) = changes(self.shown, want, view);
        // the picture: one stat-less flag, put on when the bonus starts and taken off when it ends (the data's
        // `fight` takes it off too when she hits a champion: put back if the bonus is still up)
        if view_on {
            sim.add_buff(me, &BuffV1::named(BUFF));
        } else if view_off {
            sim.entity_remove_buff(me, BUFF);
        }
        if !speed {
            return;
        }
        sim.entity_remove_buff(me, SPEED);
        if want > 0 {
            let mut b = BuffV1::named(SPEED);
            b.move_speed_mult = want;
            sim.add_buff(me, &b);
        }
        let full = self.ramp.power == BUILD && before < BUILD;
        if (self.shown == 0 || want == 0 || full) && counted("surf").is_some() {
            let why = if combat {
                if fight { "a fight" } else { "a cast" }
            } else if want == 0 {
                "away from terrain"
            } else if by_own && !by_wall {
                "by her own wall"
            } else {
                "by terrain"
            };
            wlog(format!("{} SURF {} -> {want}% ({why}, level {level})", head(sim, me), self.shown));
        }
        self.shown = want;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn league_s_four_steps_over_twelve_levels() {
        assert_eq!([1, 3, 4, 6, 7, 9, 10, 12, 18].map(level_ms), [10, 10, 15, 15, 25, 25, 40, 40, 40]);
        assert_eq!(bonus(12, BUILD), 40);
        assert_eq!(bonus(12, BUILD / 2), 20);
        assert_eq!(bonus(1, 0), 0);
    }

    #[test]
    fn it_builds_after_0_4_s_by_terrain_and_fades_3_s_after_leaving() {
        let mut r = Ramp { away_for: LINGER, ..Ramp::default() };
        for _ in 0..ARM - 1 {
            r = step(r, true, false);
        }
        assert_eq!(r.power, 0, "not yet 0.4 s by terrain");
        r = step(r, true, false);
        assert_eq!(r.power, 1);
        for _ in 0..BUILD {
            r = step(r, true, false);
        }
        assert_eq!(r.power, BUILD, "full a second later");
        for _ in 0..LINGER - 1 {
            r = step(r, false, false);
        }
        assert_eq!(r.power, BUILD, "it holds 3 s after leaving");
        r = step(r, false, false);
        assert_eq!(r.power, BUILD - 1);
        // a fight or a cast: gone at once, and it builds again from nothing
        let r = step(Ramp { near_for: 100, away_for: 0, power: BUILD }, true, true);
        assert_eq!(r.power, 0);
        assert_eq!(step(r, true, false).power, 0, "0.4 s again before it builds");
    }

    #[test]
    fn the_picture_stays_put_while_only_the_speed_changes() {
        // the bonus starts: the speed and the picture
        assert_eq!(changes(0, 1, false), (true, true, false));
        // the ramp: the speed changes every few ticks, the picture is not touched
        for (a, b) in [(1, 2), (2, 3), (20, 21), (39, 40)] {
            assert_eq!(changes(a, b, true), (true, false, false), "{a} -> {b}");
        }
        // full: nothing at all
        assert_eq!(changes(40, 40, true), (false, false, false));
        // the bonus ends: the speed off, the picture off
        assert_eq!(changes(40, 0, true), (true, false, true));
        // the data took the picture off (a hit on a champion) while the bonus is still up: put back
        assert_eq!(changes(25, 25, false), (false, true, false));
        assert_ne!(BUFF, SPEED);
    }

    #[test]
    fn near_the_game_s_walls_and_the_map_s_drawn_edges() {
        let g = Ground::from_rows(&maps::MOBA, Some(MOBA_BOUNDS));
        // row 3 is "...............##.####........": cells x 15-16 and 18-21 are walls (y 96000-128000)
        assert!(g.is_wall(15.0 * CELL + 10.0, 3.0 * CELL + 10.0));
        assert!(g.near((15.5 * CELL, 2.5 * CELL), NEAR), "half a cell above a wall cell");
        assert!(!g.near((5.5 * CELL, 2.0 * CELL), NEAR), "open ground, 38000 below the top edge face, 2 cells above a wall");
        assert!(g.near((5.5 * CELL, 1.5 * CELL), NEAR), "22000 below the top edge face");
        assert!(g.near((30_000.0, 480_000.0), NEAR), "by the map's left edge face");
        // the middle of the map (row 14 col 14): no wall in the cells round it
        assert!(!g.near((14.5 * CELL, 14.5 * CELL), NEAR));
        assert!(g.near((14.5 * CELL, 14.5 * CELL), 11.0 * CELL), "row 14's wall at col 25 is 10.5 cells off");
    }

    #[test]
    fn the_game_s_own_map_is_told_from_where_units_stand() {
        // a unit in the middle of the single-lane map's wall band picks the 5v5 map
        let (name, _) = pick(&[(480_000.0, 480_000.0), (100_000.0, 100_000.0)]);
        assert_eq!(name, "Moba");
    }
}
