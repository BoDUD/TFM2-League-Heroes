//! 星穹流丽（W）什么时候飞、往哪飞（纯计算，单元测试）。用户 2026-11-04：「龙王是不是不能边飞行边放Q 和英雄联盟也不太一样？」
//!
//! 英雄联盟 V26.21：W 朝一个方向飞越地形（1500 + 每层星尘 7.5），重置 Q 的冷却；飞行中龙息没有冷却、没有最长引导，
//! 引导时飞行速度减半——边飞边喷。主包是纯数据，只能在击杀后起飞（AI 读不到这一招），本包把它做成他自己的技能：
//! lib.rs 的被动每 [`EVERY`] tick 看一次局面（看得见的敌方英雄、队友、两边的塔、地图的墙），W 好了就按这里挑的一条
//! 直线飞过去（[`plan`]）：
//!
//! - **逃生**（[`escape`]）：残血而身边有敌方英雄，或者半血以下被两个以上、比队友多的敌方英雄围着：16 个方向里挑落地后
//!   离最近的敌方英雄最远（至少远 [`ESC_GAIN`]）、靠自己的塔、不落在敌方塔下的那一个，飞满全程；
//! - **追残血**（[`chase`]）：龙息够不着（[`CHASE_MIN`] 外）、飞得到的残血敌方英雄，落点在他前面 [`KEEP`]（龙息
//!   75000 够得着），落点旁除了他最多一名敌方英雄，不在敌方塔下；
//! - **进场**（[`engage`]）：龙息够不着的敌方英雄身边已经有队友在打（[`ALLY_R`]），他自己血量健康，落点旁的敌方英雄
//!   不比队友多两个以上，不在敌方塔下：飞到离他 [`KEEP`] 的地方，一路喷过去。
//!
//! 落点在墙里就往前飞出墙（最多再飞 [`WALL_PAST`]），出不去就退回墙前（[`landing`]）；地图外不去。墙格子是游戏的
//! 内置地图（league_camille_wall 的 maps.rs，泰隆翻墙附加包也用它），当前对局取站进墙里的单位最少的那张。
//!
//! 两张 5v5 地图（2026-11-10，用户：「要同时兼容原版地图和这个地图」）：lib.rs 按这局的塔和水晶判断是哪张图
//! （`game_places::terrain::map_of_sim`）。Rin 的召唤师峡谷（1614545 见方）用峡谷作者的墙体文件（[`Grid::rift`]，295 x 296
//! 格、每格 60000/11），没有文件时峡谷上只有地图外算墙（以前拿内置地图：960000 以外都是地图外，峡谷的远半边飞不出去）。

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

use game_places::terrain;

pub type Pt = (f64, f64);

/// 游戏自己的地图的墙格边长（世界单位，30 x 32000 = 960000）。
pub const CELL: f64 = 32_000.0;
/// 5v5 地图四边的墙面（上下的石墙、左右的石堆）：外面也算墙（league_camille_wall 的 MOBA_BOUNDS）。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);

/// 被动隔几 tick 看一次要不要飞。
pub const EVERY: usize = 3;
/// 逃生：生命不到这么多、[`ESC_R`] 内有敌方英雄……
pub const ESC_HP: f64 = 0.30;
pub const ESC_R: f64 = 60_000.0;
/// ……或者生命不到这么多、[`ESC_R2`] 内至少 [`ESC_N`] 名敌方英雄，比那里的队友多。
pub const ESC_HP2: f64 = 0.45;
pub const ESC_N: usize = 2;
pub const ESC_R2: f64 = 75_000.0;
/// 逃生的落点离最近的敌方英雄至少比现在远这么多（不然不飞）。
pub const ESC_GAIN: f64 = 40_000.0;
/// 逃生时试的方向数（一圈）。
pub const RAYS: usize = 16;
/// 逃生的落点离最近的敌方英雄这么远以外就一样好……
pub const ESC_FAR: f64 = 250_000.0;
/// ……正对着背离身边敌人的方向多算这么多（侧着飞的少算）。
pub const ESC_STRAIGHT: f64 = 20_000.0;
/// 追残血：生命不到这么多的敌方英雄，他自己生命至少 [`CHASE_ME`]……
pub const CHASE_HP: f64 = 0.35;
pub const CHASE_ME: f64 = 0.40;
/// ……在龙息之外（这么远以外；龙息 75000，再加两个身体）。
pub const CHASE_MIN: f64 = 70_000.0;
/// 进场：他自己生命至少这么多，目标在这么远以外……
pub const ENGAGE_ME: f64 = 0.55;
pub const ENGAGE_MIN: f64 = 85_000.0;
/// ……目标这么近以内有我方英雄（已经在打他）。
pub const ALLY_R: f64 = 60_000.0;
/// 落点停在目标前面这么远（龙息 75000 够得着，不贴脸）。
pub const KEEP: f64 = 50_000.0;
/// 落点这么近以内的敌方英雄算「人堆」。
pub const CROWD_R: f64 = 55_000.0;
/// 落点离活着的敌方塔不到这么近不去（逃生扣分）。
pub const TOWER_R: f64 = 75_000.0;
/// 短于这么远的飞行不值得飞。
pub const MIN_FLIGHT: f64 = 30_000.0;
/// 落点在墙里：最多再往前飞这么远出墙。
pub const WALL_PAST: f64 = 48_000.0;
/// 出墙后再飞这么远（别落在墙边上，泰隆翻墙的 MARGIN）。
pub const MARGIN: f64 = 4_000.0;
/// 沿飞行方向查墙的步长。
pub const STEP: f64 = 1_000.0;

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

pub fn unit(v: Pt) -> Option<Pt> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l >= 1.0).then(|| (v.0 / l, v.1 / l))
}

/// `from` 沿 `dir` 走 `t`。
pub fn along(from: Pt, dir: Pt, t: f64) -> Pt {
    (from.0 + dir.0 * t, from.1 + dir.1 * t)
}

// ===================== 墙 =====================

/// 一张墙格子：`cells[y][x]`；`bounds` 外是地图四边画出来的墙（5v5 的；另两张图的四周本来就是格子墙）。每格 `cell`
/// 见方，(0, 0) 格的角在 `origin`（游戏自己的地图 32000、(0, 0)；峡谷的墙体文件 60000/11、(30000/11, 0)）。
#[derive(Clone, Debug, PartialEq)]
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
    pub bounds: Option<(f64, f64, f64, f64)>,
    pub cell: f64,
    pub origin: Pt,
}

impl Grid {
    pub fn from_rows(rows: &[&str]) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(), bounds: None, cell: CELL,
               origin: (0.0, 0.0) }
    }

    /// 游戏的三张内置地图：5v5（加四边的墙面）、单线、死斗。
    pub fn builtin() -> Vec<Grid> {
        let mut moba = Grid::from_rows(&maps::MOBA);
        moba.bounds = Some(MOBA_BOUNDS);
        vec![moba, Grid::from_rows(&maps::SINGLE_LANE), Grid::from_rows(&maps::DEATH_MATCH)]
    }

    /// 召唤师峡谷的墙：有墙体文件就是文件的墙格（四边在文件里就是墙）；没有就是一格地图大小的空地（只有地图外算墙）。
    pub fn rift(walls: Option<&terrain::Walls>) -> Grid {
        match walls {
            Some(w) => Grid { cells: w.cells.clone(), bounds: None, cell: w.cell, origin: w.origin },
            None => Grid { cells: vec![vec![false]], bounds: None, cell: terrain::RIFT_EXTENT, origin: (0.0, 0.0) },
        }
    }

    /// 在地图里（格子范围内、四边的墙面以内）吗。
    pub fn on_map(&self, p: Pt) -> bool {
        let w = self.origin.0 + self.cells.iter().map(|r| r.len()).max().unwrap_or(0) as f64 * self.cell;
        let h = self.origin.1 + self.cells.len() as f64 * self.cell;
        let inside = self.bounds.is_none_or(|(x0, y0, x1, y1)| p.0 >= x0 && p.1 >= y0 && p.0 <= x1 && p.1 <= y1);
        p.0 >= self.origin.0 && p.1 >= self.origin.1 && p.0 < w && p.1 < h && inside
    }

    /// 落在墙格里（或地图外）吗。
    pub fn is_wall(&self, p: Pt) -> bool {
        if !self.on_map(p) {
            return true;
        }
        let (cx, cy) = (((p.0 - self.origin.0) / self.cell) as usize, ((p.1 - self.origin.1) / self.cell) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(true)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }

    /// `a` 到 `b` 的直线穿过墙格吗（两端不算）。
    pub fn crosses(&self, a: Pt, b: Pt) -> bool {
        let n = (dist(a, b) / STEP).floor() as usize;
        (1..n).any(|i| {
            let t = i as f64 / n as f64;
            self.is_wall((a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t))
        })
    }
}

/// 这局是哪张图：站在墙里的单位最少的那张，一样少时墙多的那张（泰隆翻墙附加包的判断；只看英雄的话大家都站在三张图都空着的
/// 那条斜带上，所以把小兵、野怪、塔都算上）。
pub fn current(grids: &[Grid], points: &[Pt]) -> usize {
    grids
        .iter()
        .enumerate()
        .min_by_key(|(_, g)| (points.iter().filter(|p| g.is_wall(**p)).count(), std::cmp::Reverse(g.walls())))
        .map_or(0, |(i, _)| i)
}

/// 从 `from` 沿 `dir`（单位向量）飞大约 `want`：落点在地图外就缩回地图里；落在墙里就往前飞出墙（最多再飞
/// [`WALL_PAST`]，出墙后再飞 [`MARGIN`]），出不去就退回墙前。返回飞多远（0 = 没地方落）。
pub fn landing(g: &Grid, from: Pt, dir: Pt, want: f64) -> f64 {
    let at = |t: f64| along(from, dir, t);
    let mut len = want.max(0.0);
    while len > 0.0 && !g.on_map(at(len)) {
        len -= STEP;
    }
    if len <= 0.0 {
        return 0.0;
    }
    if !g.is_wall(at(len)) {
        return len;
    }
    let mut t = len;
    while t <= len + WALL_PAST && g.on_map(at(t)) {
        if !g.is_wall(at(t)) {
            let past = t + MARGIN;
            return if g.on_map(at(past)) && !g.is_wall(at(past)) { past } else { t };
        }
        t += STEP;
    }
    let mut t = len;
    while t > 0.0 {
        if !g.is_wall(at(t)) {
            return t;
        }
        t -= STEP;
    }
    0.0
}

// ===================== 局面和决定 =====================

/// 一名英雄：实体、位置、生命比例（0..1）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Champ {
    pub id: usize,
    pub at: Pt,
    pub hp: f64,
}

/// 被动看到的局面。
#[derive(Clone, Debug, Default)]
pub struct Scene {
    pub me: Pt,
    /// 他的生命比例。
    pub hp: f64,
    /// 看得见、选得中的敌方英雄。
    pub foes: Vec<Champ>,
    /// 活着的队友英雄（不算他）。
    pub allies: Vec<Champ>,
    /// 活着的塔。
    pub enemy_towers: Vec<Pt>,
    pub ally_towers: Vec<Pt>,
}

/// 为什么飞。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Why {
    Escape,
    Chase(usize),
    Engage(usize),
}

impl Why {
    /// 飞向谁（逃生没有）。
    pub fn target(&self) -> Option<usize> {
        match self {
            Why::Escape => None,
            Why::Chase(t) | Why::Engage(t) => Some(*t),
        }
    }

    pub fn word(&self) -> &'static str {
        match self {
            Why::Escape => "escape",
            Why::Chase(_) => "chase",
            Why::Engage(_) => "engage",
        }
    }
}

/// 一次飞行：为什么、方向（单位向量）、多远。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Plan {
    pub why: Why,
    pub dir: Pt,
    pub len: f64,
}

/// 飞多远：`w_len` + 每层星尘 `w_len_d`（英雄联盟 1500 + 7.5 x 星尘，按他别的距离 x100）。
pub fn reach(w_len: usize, w_len_d: usize, stardust: usize) -> f64 {
    (w_len + w_len_d * stardust) as f64
}

/// 最高等级（TFM2 的 12 级）。
pub const MAX_LEVEL: usize = 12;

/// 等级 `level` 时 W 的冷却：1 级 `w_cd1`，一级一级匀着降到 12 级的 `w_cd12`（英雄联盟 22 秒到 14 秒）。
pub fn cooldown(w_cd1: usize, w_cd12: usize, level: usize) -> usize {
    let l = level.clamp(1, MAX_LEVEL) - 1;
    w_cd1 - w_cd1.saturating_sub(w_cd12) * l / (MAX_LEVEL - 1)
}

/// 击杀返还：剩下的冷却 `left` 去掉 `refund`%。
pub fn refunded(left: usize, refund: usize) -> usize {
    left * 100usize.saturating_sub(refund) / 100
}

fn near(cs: &[Champ], at: Pt, r: f64) -> usize {
    cs.iter().filter(|c| dist(at, c.at) <= r).count()
}

fn under_enemy_tower(s: &Scene, at: Pt) -> bool {
    s.enemy_towers.iter().any(|t| dist(at, *t) <= TOWER_R)
}

/// 该逃了吗。
pub fn wants_out(s: &Scene) -> bool {
    let close = near(&s.foes, s.me, ESC_R2);
    (s.hp <= ESC_HP && near(&s.foes, s.me, ESC_R) >= 1)
        || (s.hp <= ESC_HP2 && close >= ESC_N && close > near(&s.allies, s.me, ESC_R2))
}

fn rays() -> impl Iterator<Item = Pt> {
    (0..RAYS).map(|i| {
        let a = i as f64 * std::f64::consts::TAU / RAYS as f64;
        (a.cos(), a.sin())
    })
}

/// 逃生：飞满全程，落点离最近的敌方英雄最远（远不出 [`ESC_GAIN`] 不飞；[`ESC_FAR`] 以外一样远），越正对着背离敌人越好，
/// 靠自己的塔，敌方塔下扣分。
pub fn escape(s: &Scene, reach: f64, g: &Grid) -> Option<Plan> {
    if !wants_out(s) {
        return None;
    }
    let gap = |q: Pt| s.foes.iter().map(|f| dist(q, f.at)).fold(f64::MAX, f64::min);
    let home = |q: Pt| s.ally_towers.iter().map(|t| dist(q, *t)).fold(400_000.0, f64::min);
    let now = gap(s.me);
    // away from the enemies near him (their centre)
    let close: Vec<&Champ> = s.foes.iter().filter(|f| dist(s.me, f.at) <= ESC_R2 * 1.5).collect();
    let centre = if close.is_empty() {
        s.me
    } else {
        let k = close.len() as f64;
        (close.iter().map(|f| f.at.0).sum::<f64>() / k, close.iter().map(|f| f.at.1).sum::<f64>() / k)
    };
    let away = unit((s.me.0 - centre.0, s.me.1 - centre.1)).unwrap_or((0.0, 0.0));
    rays()
        .filter_map(|d| {
            let len = landing(g, s.me, d, reach);
            (len >= MIN_FLIGHT).then_some((d, len))
        })
        .map(|(d, len)| {
            let q = along(s.me, d, len);
            let score = gap(q).min(ESC_FAR) + ESC_STRAIGHT * (d.0 * away.0 + d.1 * away.1) - 0.2 * home(q)
                - if under_enemy_tower(s, q) { 100_000.0 } else { 0.0 };
            (d, len, gap(q), score)
        })
        .filter(|c| c.2 >= now + ESC_GAIN)
        .max_by(|a, b| a.3.total_cmp(&b.3))
        .map(|(dir, len, ..)| Plan { why: Why::Escape, dir, len })
}

/// 飞到 `f` 前面 [`KEEP`] 的地方：方向和飞多远（落点修过墙；太短、到不了就没有）。
fn toward(s: &Scene, reach: f64, g: &Grid, f: &Champ) -> Option<(Pt, f64, Pt)> {
    let d = dist(s.me, f.at);
    if d > reach + KEEP {
        return None;
    }
    let dir = unit((f.at.0 - s.me.0, f.at.1 - s.me.1))?;
    let len = landing(g, s.me, dir, (d - KEEP).min(reach));
    (len >= MIN_FLIGHT).then(|| (dir, len, along(s.me, dir, len)))
}

/// 追残血：龙息够不着、飞得到的残血敌方英雄（生命最低的先，一样就近的先），落点旁除了他最多一名敌方英雄，不在敌方塔下。
pub fn chase(s: &Scene, reach: f64, g: &Grid) -> Option<Plan> {
    if s.hp < CHASE_ME {
        return None;
    }
    s.foes
        .iter()
        .filter(|f| f.hp <= CHASE_HP && dist(s.me, f.at) >= CHASE_MIN)
        .filter_map(|f| toward(s, reach, g, f).map(|(dir, len, land)| (f, dir, len, land)))
        .filter(|(f, _, _, land)| {
            s.foes.iter().filter(|o| o.id != f.id && dist(*land, o.at) <= CROWD_R).count() <= 1
                && !under_enemy_tower(s, *land)
        })
        .min_by(|a, b| a.0.hp.total_cmp(&b.0.hp).then(dist(s.me, a.0.at).total_cmp(&dist(s.me, b.0.at))))
        .map(|(f, dir, len, _)| Plan { why: Why::Chase(f.id), dir, len })
}

/// 进场：龙息够不着、身边已经有队友在打的敌方英雄（生命最低的先），落点旁的敌方英雄不比那里的队友（加上他）多一个以上，
/// 不在敌方塔下。
pub fn engage(s: &Scene, reach: f64, g: &Grid) -> Option<Plan> {
    if s.hp < ENGAGE_ME {
        return None;
    }
    s.foes
        .iter()
        .filter(|f| dist(s.me, f.at) >= ENGAGE_MIN && near(&s.allies, f.at, ALLY_R) >= 1)
        .filter_map(|f| toward(s, reach, g, f).map(|(dir, len, land)| (f, dir, len, land)))
        .filter(|(_, _, _, land)| {
            near(&s.foes, *land, CROWD_R) <= near(&s.allies, *land, CROWD_R + 20_000.0) + 2 && !under_enemy_tower(s, *land)
        })
        .min_by(|a, b| a.0.hp.total_cmp(&b.0.hp).then(dist(s.me, a.0.at).total_cmp(&dist(s.me, b.0.at))))
        .map(|(f, dir, len, _)| Plan { why: Why::Engage(f.id), dir, len })
}

/// 这一刻要不要飞、怎么飞：先逃生，再追残血，再进场。
pub fn plan(s: &Scene, reach: f64, g: &Grid) -> Option<Plan> {
    escape(s, reach, g).or_else(|| chase(s, reach, g)).or_else(|| engage(s, reach, g))
}

/// 飞行中这一 tick 飞多快：喷龙息时减半（英雄联盟）。
pub fn speed(w_v: usize, breathing: bool) -> f64 {
    if breathing { w_v as f64 / 2.0 } else { w_v as f64 }
}

/// 起飞时挂的「落点」buff 名（AI 钩子读它让他朝落点飞、不乱跑）：`league_aurelionsol_w_to:<x>,<y>`。
pub fn to_name(prefix: &str, at: Pt) -> String {
    format!("{prefix}{},{}", at.0.max(0.0).round() as u64, at.1.max(0.0).round() as u64)
}

/// [`to_name`] 写的落点。
pub fn parse_to(prefix: &str, name: &str) -> Option<Pt> {
    let (x, y) = name.strip_prefix(prefix)?.split_once(',')?;
    Some((x.parse::<u64>().ok()? as f64, y.parse::<u64>().ok()? as f64))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn open() -> Grid {
        Grid::from_rows(&[".............................."; 30])
    }

    fn me(at: Pt, hp: f64) -> Scene {
        Scene { me: at, hp, ..Scene::default() }
    }

    fn c(id: usize, at: Pt, hp: f64) -> Champ {
        Champ { id, at, hp }
    }

    #[test]
    fn the_moba_map_and_its_edges() {
        let g = &Grid::builtin()[0];
        assert_eq!(g.walls(), 90, "the 5v5 map's ninety wall cells");
        assert!(g.is_wall((10_000.0, 500_000.0)), "beyond the left edge");
        assert!(!g.is_wall((480_000.0, 480_000.0)), "the middle of mid lane");
        // the map is the one with the fewest units in walls
        let grids = Grid::builtin();
        // units in the far corners (side lanes, camps) stand in the other two maps' walls
        let moba_units: Vec<Pt> = vec![(480_000.0, 480_000.0), (64_000.0, 64_000.0)];
        assert_eq!(current(&grids, &moba_units), 0);
        // the middle of the map is open on all three: alone it picks the one with the most walls (so every unit counts)
        assert_eq!(current(&grids, &[(480_000.0, 480_000.0)]), 2);
    }

    /// 峡谷那样的墙格子（295 x 296 格，每格 60000/11，从 x = 30000/11 起，作者墙体文件的格子）：中心落在 `rects`
    /// （世界坐标的 (左上, 右下)）里的格子是墙。
    fn rift_walls(rects: &[(Pt, Pt)]) -> terrain::Walls {
        let (cell, origin) = (60_000.0 / 11.0, (30_000.0 / 11.0, 0.0));
        let rows: Vec<String> = (0..296)
            .map(|cy| {
                (0..295)
                    .map(|cx| {
                        let c = (origin.0 + (cx as f64 + 0.5) * cell, origin.1 + (cy as f64 + 0.5) * cell);
                        let wall = rects.iter().any(|&(a, b)| c.0 >= a.0 && c.0 <= b.0 && c.1 >= a.1 && c.1 <= b.1);
                        if wall { '#' } else { '.' }
                    })
                    .collect()
            })
            .collect();
        let rows: Vec<&str> = rows.iter().map(String::as_str).collect();
        terrain::Walls::from_rows(&rows, cell, origin, (terrain::RIFT_EXTENT, terrain::RIFT_EXTENT))
    }

    #[test]
    fn on_the_rift_he_flies_over_the_rifts_walls() {
        // a wall in the Rift's far half: a flight ending in it goes on past it
        let g = Grid::rift(Some(&rift_walls(&[((1_300_000.0, 1_100_000.0), (1_330_000.0, 1_300_000.0))])));
        let from = (1_250_000.0, 1_200_000.0);
        let len = landing(&g, from, (1.0, 0.0), 65_000.0);
        let land = along(from, (1.0, 0.0), len);
        assert!(land.0 > 1_330_000.0 - g.cell && !g.is_wall(land) && g.crosses(from, land), "{len} {land:?}");
        // the game's own grid: past 960000 is off its map - no flight at all out there (the old code)
        assert_eq!(landing(&Grid::builtin()[0], from, (1.0, 0.0), 65_000.0), 0.0);
        // past 960000 it is the map on the Rift, and a wall of the game's own 5v5 map is none on it
        assert!(g.on_map((1_000_000.0, 1_500_000.0)) && !g.is_wall((1_000_000.0, 1_500_000.0)));
        let native = (15.5 * CELL, 3.5 * CELL);
        assert!(Grid::builtin()[0].is_wall(native) && !g.is_wall(native));
        // low with an enemy close in the far half: away from him, the whole way
        let mut s = me(from, 0.25);
        s.foes = vec![c(7, (1_290_000.0, 1_200_000.0), 1.0)];
        let p = plan(&s, 150_000.0, &g).expect("an escape");
        assert!(p.why == Why::Escape && p.dir.0 < -0.5 && (p.len - 150_000.0).abs() < 1.0, "{p:?}");
        assert_eq!(plan(&s, 150_000.0, &Grid::builtin()[0]), None, "the old grid: no room out there");
    }

    /// 峡谷真的墙：开发者用 `LEAGUE_RIFT_WALLS` 指着作者的墙体文件时才跑（CI 没有文件，跳过）。
    #[test]
    fn on_the_rifts_real_walls_every_landing_is_clear() {
        let Some(path) = std::env::var_os(terrain::RIFT_WALLS_ENV) else { return };
        let g = Grid::rift(Some(&terrain::load_rift_walls(&[path.into()]).unwrap()));
        let (mut flights, mut over) = (0, 0);
        let mut y = 20_000.0;
        while y < terrain::RIFT_EXTENT {
            let mut x = 20_000.0;
            while x < terrain::RIFT_EXTENT {
                if !g.is_wall((x, y)) {
                    for d in rays() {
                        let len = landing(&g, (x, y), d, 150_000.0);
                        if len > 0.0 {
                            let land = along((x, y), d, len);
                            assert!(g.on_map(land) && !g.is_wall(land), "({x},{y}) {d:?} -> {land:?}");
                            flights += 1;
                            over += usize::from(g.crosses((x, y), land));
                        }
                    }
                }
                x += 40_000.0;
            }
            y += 40_000.0;
        }
        assert!(flights > 3_000 && over > 500, "{flights} flights, {over} over walls");
    }

    #[test]
    fn on_the_rift_without_its_walls_file_only_its_edges_stop_him() {
        let g = Grid::rift(None);
        assert!(g.on_map((1_600_000.0, 1_600_000.0)) && !g.on_map((1_614_546.0, 800_000.0)) && !g.on_map((-1.0, 5.0)));
        // a flight toward the map's edge is cut to it
        let len = landing(&g, (1_550_000.0, 800_000.0), (1.0, 0.0), 150_000.0);
        assert!(len > 60_000.0 && len < 64_545.0, "{len}");
        // nothing else is wall
        assert_eq!(landing(&g, (1_250_000.0, 1_200_000.0), (1.0, 0.0), 65_000.0), 65_000.0);
        // the landing's buff name holds the Rift's coordinates
        assert!(to_name("league_aurelionsol_w_to:", (1_614_545.0, 1_614_545.0)).len() <= 64);
    }

    #[test]
    fn a_landing_in_a_wall_moves_on_past_it_or_back() {
        // a wall from x = 6 to 7 cells on row 3
        let mut g = open();
        g.cells[3][6] = true;
        g.cells[3][7] = true;
        let from = (3.0 * CELL, 3.5 * CELL);
        // flying right to the middle of the wall: on past it, a little beyond its far side
        let len = landing(&g, from, (1.0, 0.0), 3.5 * CELL);
        assert!(len >= 5.0 * CELL && len <= 5.0 * CELL + MARGIN + STEP, "past the wall: {len}");
        assert!(!g.is_wall(along(from, (1.0, 0.0), len)));
        // a wall too thick to cross: back to before it
        for x in 8..16 {
            g.cells[3][x] = true;
        }
        let len = landing(&g, from, (1.0, 0.0), 3.5 * CELL);
        assert!(len < 3.0 * CELL && !g.is_wall(along(from, (1.0, 0.0), len)), "back before the wall: {len}");
        // off the map: cut to its edge
        let len = landing(&g, (CELL, CELL), (-1.0, 0.0), 200_000.0);
        assert!(len <= CELL && g.on_map(along((CELL, CELL), (-1.0, 0.0), len)), "{len}");
        // the straight line crosses the wall: over it
        assert!(g.crosses(from, (12.0 * CELL, 3.5 * CELL)));
    }

    #[test]
    fn low_with_an_enemy_close_he_flies_away_from_it() {
        let g = open();
        let mut s = me((480_000.0, 480_000.0), 0.25);
        s.foes = vec![c(7, (520_000.0, 480_000.0), 1.0)];
        let p = plan(&s, 150_000.0, &g).expect("an escape");
        assert_eq!(p.why, Why::Escape);
        assert!(p.dir.0 < -0.5, "away from the enemy on his right: {:?}", p.dir);
        assert!((p.len - 150_000.0).abs() < 1.0);
        // healthy: no escape (and the enemy is within the breath: no chase or engage either)
        s.hp = 0.9;
        assert_eq!(plan(&s, 150_000.0, &g), None);
        // half health, two enemies and no ally: away
        s.hp = 0.4;
        s.foes.push(c(8, (480_000.0, 540_000.0), 1.0));
        assert_eq!(plan(&s, 150_000.0, &g).map(|p| p.why), Some(Why::Escape));
        // an ally beside him evens it: he stays
        s.allies = vec![c(2, (470_000.0, 470_000.0), 1.0), c(3, (490_000.0, 470_000.0), 1.0)];
        assert_eq!(plan(&s, 150_000.0, &g), None);
    }

    #[test]
    fn a_low_one_out_of_the_breath_is_chased_to_breath_range() {
        let g = open();
        let mut s = me((300_000.0, 480_000.0), 0.8);
        s.foes = vec![c(7, (450_000.0, 480_000.0), 0.2)];
        let p = plan(&s, 150_000.0, &g).expect("a chase");
        assert_eq!(p.why, Why::Chase(7));
        assert!((p.dir.0 - 1.0).abs() < 1e-9);
        assert!((p.len - (150_000.0 - KEEP)).abs() < 1.0, "stops KEEP short of him: {}", p.len);
        // within the breath already: no flight
        s.foes[0].at = (360_000.0, 480_000.0);
        assert_eq!(plan(&s, 150_000.0, &g), None);
        // too far to reach
        s.foes[0].at = (520_000.0, 480_000.0);
        assert_eq!(plan(&s, 150_000.0, &g), None);
        // into two more enemies: no
        s.foes = vec![c(7, (450_000.0, 480_000.0), 0.2), c(8, (420_000.0, 470_000.0), 1.0), c(9, (410_000.0, 490_000.0), 1.0)];
        assert_eq!(plan(&s, 150_000.0, &g), None);
        // under an enemy tower: no
        s.foes.truncate(1);
        s.enemy_towers = vec![(430_000.0, 480_000.0)];
        assert_eq!(plan(&s, 150_000.0, &g), None);
    }

    #[test]
    fn a_fight_his_allies_have_joined_is_engaged() {
        let g = open();
        let mut s = me((300_000.0, 480_000.0), 0.9);
        s.foes = vec![c(7, (420_000.0, 480_000.0), 0.8)];
        // nobody of his there yet: he does not dive in alone
        assert_eq!(plan(&s, 150_000.0, &g), None);
        s.allies = vec![c(2, (440_000.0, 490_000.0), 0.7)];
        let p = plan(&s, 150_000.0, &g).expect("an engage");
        assert_eq!(p.why, Why::Engage(7));
        assert!((p.len - (120_000.0 - KEEP)).abs() < 1.0);
        // low himself: no engage
        s.hp = 0.5;
        assert_eq!(plan(&s, 150_000.0, &g), None);
    }

    #[test]
    fn the_numbers() {
        assert_eq!(cooldown(1320, 840, 1), 1320);
        assert_eq!(cooldown(1320, 840, 6), 1320 - 480 * 5 / 11);
        assert_eq!(cooldown(1320, 840, 12), 840);
        assert_eq!(cooldown(1320, 840, 18), 840, "no level past 12");
        assert_eq!(cooldown(1320, 840, 0), 1320);
        assert_eq!(refunded(1000, 90), 100);
        assert_eq!(refunded(5, 90), 0);
        assert_eq!(reach(150_000, 750, 30), 172_500.0);
        assert_eq!(speed(2000, false), 2000.0);
        assert_eq!(speed(2000, true), 1000.0);
        let name = to_name("league_aurelionsol_w_to:", (123_456.4, 7.6));
        assert_eq!(name, "league_aurelionsol_w_to:123456,8");
        assert!(name.len() <= 64);
        assert_eq!(parse_to("league_aurelionsol_w_to:", &name), Some((123_456.0, 8.0)));
        assert_eq!(parse_to("league_aurelionsol_w_to:", "league_aurelionsol_w_fly"), None);
        assert!(to_name("league_aurelionsol_w_to:", (959_999.0, 959_999.0)).len() <= 64);
    }
}
