//! 穷途末路的炮弹撞墙（用户 2026-10-20：「还有Q技能碰到墙会马上弹回来吗 和英雄联盟一样」）。
//!
//! 主包是纯数据，读不到地图的墙：炮弹总是飞满 q_range、停下 q_fuse 才炸（一圈）。英雄联盟里炮弹撞到墙就停在墙边，很快
//! 炸开，爆炸再沿原路打回格雷福斯。副本里 Q 出手那一 tick 不放主包的炮弹，改调本包的 `league_graves:q`（输入是 Q 的方向）：
//!
//! - `q`：沿 Q 的方向从他脚下往前找墙（引擎的碰撞墙，5v5 地图野区的格子，卡蜜尔附加包的 `maps.rs`，诺提勒斯的判断）：
//!   终点是 q_range 处，或墙前 `WALL_GAP` 处。放一颗穿透的炮弹飞到终点（主包的 `q_shell` 画面，打中的每个敌人
//!   q_dmg + q_ratio% 攻击力，`qhit`），飞到时排 `bomb`；
//! - `bomb`：炸弹落在终点（主包的 `q_blast` 画面；撞了墙用 `q_blast_w`：只亮一下红灯就炸），q_fuse（撞墙 `q_wall`）tick 后排 `boom`；
//! - `boom`：终点 q_r 内的敌人受 q2_dmg + q2_ratio% 攻击力；再放一颗炮弹从终点沿原路飞回出手的地方（`back`：路上没被
//!   爆炸炸到的敌人各受一次同样的伤害）——「弹回来」。
//!
//! 这一发（终点、出手的地方、撞墙了没有）记在 [`SHOTS`] 里，按（这份模拟的编号、格雷福斯）；排的 `bomb` / `boom` 只带终点
//! （普通的位置输入），到时按终点找回这一发（2026-11-04：以前塞在输入的 `dir_x` / `dir_y` / `target_id` 里，排队后丢了）。
//!
//! 两张 5v5 地图（2026-11-10，用户：「要同时兼容原版地图和这个地图」）：每一发按这局的塔和水晶判断是哪张图
//! （`game_places::terrain::map_of_sim`）。游戏自己的地图照旧；Rin 的召唤师峡谷用峡谷作者的墙体文件
//! （`terrain::rift_walls`，295 x 296 格、每格 60000/11），没有文件时峡谷上不知道哪里有墙，炮弹总是飞满射程。

use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{self, Map};
use mod_api_stable::*;

use super::{counted, head, maps, params_of, sim_of, sn, who, wlog, ID};

/// 游戏自己的地图的墙格边长（世界单位）。
pub const CELL: f64 = 32_000.0;
/// 沿路线找墙的步长。
pub const STEP: f64 = 500.0;
/// 炸弹停在离墙这么远处。
pub const WALL_GAP: f64 = 3_000.0;

pub type Pt = (f64, f64);

/// 一张墙格子：`cells[y][x]`，每格 `cell` 见方，(0, 0) 格的角在 `origin`（游戏自己的地图 32000、(0, 0)；峡谷的墙体文件
/// 60000/11、(30000/11, 0)）。
#[derive(Clone, Debug, PartialEq)]
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
    pub cell: f64,
    pub origin: (f64, f64),
}

impl Grid {
    pub fn from_rows(rows: &[&str]) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(), cell: CELL, origin: (0.0, 0.0) }
    }

    pub fn builtin() -> [Grid; 3] {
        [Grid::from_rows(&maps::MOBA), Grid::from_rows(&maps::SINGLE_LANE), Grid::from_rows(&maps::DEATH_MATCH)]
    }

    /// 峡谷的墙：有墙体文件就是文件的墙格；没有就是一格地图大小的空地（不知道哪里有墙：炮弹飞满射程）。
    pub fn rift(walls: Option<&terrain::Walls>) -> Grid {
        match walls {
            Some(w) => Grid { cells: w.cells.clone(), cell: w.cell, origin: w.origin },
            None => Grid { cells: vec![vec![false]], cell: terrain::RIFT_EXTENT, origin: (0.0, 0.0) },
        }
    }

    /// 世界坐标落在墙格里吗（地图外不算）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        let (x, y) = (x - self.origin.0, y - self.origin.1);
        if x < 0.0 || y < 0.0 {
            return false;
        }
        let (cx, cy) = ((x / self.cell) as usize, (y / self.cell) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(false)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }

    /// 从 `from` 沿 `dir`（单位向量）`reach` 内第一次碰到墙的距离。
    pub fn first_wall(&self, from: Pt, dir: Pt, reach: f64) -> Option<f64> {
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

/// 猜地图用的点：所有活着的单位（英雄、小兵、野怪、塔……）。只看英雄的话，大家都站在三张图都空着的那条斜带上
/// （中路、两边泉水）时打平，平手偏向墙多的单线 / 死斗图，5v5 就猜错了（2026-11-01 复查：波比的 R 有 7 次退回击退）；
/// 5v5 边路的兵和野区的野怪几乎一直在，正好落在另两张图的墙里。
fn unit_points(sim: &StableSim<'_>) -> Vec<(f64, f64)> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_alive())
        .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
        .collect()
}

/// 这局是哪张图：站在墙里的英雄最少、墙又最多的那张（泰隆、诺提勒斯附加包的判断）。
pub fn current(grids: &[Grid], champions: &[Pt]) -> Option<usize> {
    grids
        .iter()
        .enumerate()
        .min_by_key(|(_, g)| {
            let inside = champions.iter().filter(|&&(x, y)| g.is_wall(x, y)).count();
            (inside, std::cmp::Reverse(g.walls()))
        })
        .map(|(i, _)| i)
}

/// 游戏的三张内置地图，和峡谷的墙（墙体文件每次启动只读、只换一次，第一次到峡谷上才读）。
static GRIDS: LazyLock<[Grid; 3]> = LazyLock::new(Grid::builtin);
static RIFT_GRID: LazyLock<Grid> = LazyLock::new(|| Grid::rift(terrain::rift_walls()));

/// 这局的墙：峡谷上是峡谷的（第一次遇到时日志里记一行），游戏自己的地图照旧从三张内置地图里挑（[`current`]）。
fn grid_now(sim: &StableSim<'_>) -> Option<&'static Grid> {
    match terrain::map_of_sim(sim) {
        Map::Rift => {
            static MET: AtomicBool = AtomicBool::new(false);
            if !MET.swap(true, Ordering::Relaxed) {
                wlog(format!("== Rift: Q's shell stops at the Rift's walls (from its walls file; with no file no wall is \
                              known there and it flies its full range); {} ==", terrain::rift_status()));
            }
            Some(&*RIFT_GRID)
        }
        Map::Native => current(&*GRIDS, &unit_points(sim)).map(|i| &GRIDS[i]),
    }
}

/// 炮弹停在哪：(终点, 撞墙了没有)。墙比 `WALL_GAP` 还近就停在脚下前一点。
pub fn end_of(g: &Grid, from: Pt, dir: Pt, range: f64) -> (Pt, bool) {
    match g.first_wall(from, dir, range) {
        Some(t) => {
            let d = (t - WALL_GAP).max(STEP);
            ((from.0 + dir.0 * d, from.1 + dir.1 * d), true)
        }
        None => ((from.0 + dir.0 * range, from.1 + dir.1 * range), false),
    }
}

fn unit(v: Pt) -> Option<Pt> {
    let n = (v.0 * v.0 + v.1 * v.1).sqrt();
    (n > 1.0).then(|| (v.0 / n, v.1 / n))
}

fn upos(p: Pt) -> (u64, u64) {
    (p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

fn alive_at(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() {
        return None;
    }
    let (x, y) = e.pos();
    Some((x as f64, y as f64))
}

/// 一发炮弹：终点、出手的地方、撞墙了没有。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Shot {
    pub end: (u64, u64),
    pub from: (u64, u64),
    pub wall: bool,
}

/// 还没炸完的炮弹，按（这份模拟的编号 `SIM_TAG`、格雷福斯）记。2026-11-04 修（11-03 夜里的日志：7 发「stopped by a wall」，
/// 43 次 Q BOOM 全是「after the fuse」）：以前这一发塞在排队效果的输入里（出手的地方在 dir_x / dir_y，撞墙在 target_id），
/// 排队只留下位置输入的 x、y——撞了墙的照样等满 q_fuse，炸完飞回来的炮弹飞向地图的 (0, 0)，不是出手的地方。
pub static SHOTS: LazyLock<Mutex<HashMap<(u64, usize), Vec<Shot>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// 一个格雷福斯最多记这么多发（Q 的冷却比飞行加引信长得多，一般只有一发）。
const MOST_SHOTS: usize = 4;
/// 按终点找回这一发：差这么多以内都算（排队把位置原样带回来，留一点余地）。
pub const SAME_END: u64 = 1_000;

/// A shot of `row` on its way.
pub fn remember(row: (u64, usize), shot: Shot) {
    let mut shots = SHOTS.lock().unwrap_or_else(|e| e.into_inner());
    let list = shots.entry(row).or_default();
    list.push(shot);
    if list.len() > MOST_SHOTS {
        list.remove(0);
    }
}

/// The shot of `row` that ends at `end` (the nearest end within `SAME_END`); `take` takes it off.
pub fn shot_at(row: (u64, usize), end: (u64, u64), take: bool) -> Option<Shot> {
    let d2 = |a: (u64, u64)| {
        let (dx, dy) = (a.0.abs_diff(end.0) as u128, a.1.abs_diff(end.1) as u128);
        dx * dx + dy * dy
    };
    let mut shots = SHOTS.lock().unwrap_or_else(|e| e.into_inner());
    let list = shots.get_mut(&row)?;
    let i = (0..list.len()).filter(|&i| d2(list[i].end) <= (SAME_END as u128).pow(2)).min_by_key(|&i| d2(list[i].end))?;
    let shot = list[i];
    if take {
        list.remove(i);
        if list.is_empty() {
            shots.remove(&row);
        }
    }
    Some(shot)
}

fn queue(sim: &mut StableSim<'_>, stage: &str, caster: usize, input: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{stage}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
}

fn fly(sim: &mut StableSim<'_>, caster: usize, from: Pt, to: Pt, width: usize, speed: usize, effect: &str) -> bool {
    let (x, y) = upos(from);
    let (tx, ty) = upos(to);
    let spec = ProjectileSpawnV1 {
        caster_id: caster,
        team: sim.get_entity(caster).map_or(0, |e| e.team()),
        x,
        y,
        radius: (width / 2) as u64,
        speed: speed as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: tx,
        target_y: ty,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::EnemyWithoutTower.code(),
    };
    sim.spawn_projectile(&sn("q_shell"), &format!("{ID}:{effect}"), &spec)
}

/// 爆炸炸到过的单位：飞回来的炮弹不再打它们（按这份模拟的编号和格雷福斯，记最近一次爆炸；2026-11-04 以前按这局的种子，
/// 并排跑的两份预模拟共用一份）。
pub static BLASTED: LazyLock<Mutex<HashMap<(u64, usize), Vec<usize>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

// ===================== 四步 =====================

/// Q 出手的那一 tick（主包的 `q_at`）：找墙，放炮弹。
fn launch(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let Some(here) = alive_at(sim, caster) else { return };
    let dir = if input.kind == InputTargetKindV1::Dir.code() {
        unit((input.dir_x as f64, input.dir_y as f64))
    } else if input.kind == InputTargetKindV1::Pos.code() {
        unit((input.x as f64 - here.0, input.y as f64 - here.1))
    } else if input.kind == InputTargetKindV1::Target.code() {
        alive_at(sim, input.target_id).and_then(|t| unit((t.0 - here.0, t.1 - here.1)))
    } else {
        None
    };
    let Some(dir) = dir else {
        wlog(format!("{} Q: no direction in the input (kind {})", head(sim, caster), input.kind));
        return;
    };
    let p = params_of(sim, caster);
    let (end, wall) = match grid_now(sim) {
        Some(g) => end_of(g, here, dir, p.q_range as f64),
        None => ((here.0 + dir.0 * p.q_range as f64, here.1 + dir.1 * p.q_range as f64), false),
    };
    let d = ((end.0 - here.0).powi(2) + (end.1 - here.1).powi(2)).sqrt();
    let flight = (d / p.q_speed as f64).ceil() as usize;
    let ok = fly(sim, caster, here, end, p.q_w, p.q_speed, "qhit");
    let (x, y) = upos(end);
    remember((sim_of(sim, caster), caster), Shot { end: (x, y), from: upos(here), wall });
    queue(sim, "bomb", caster, InputTargetV1::pos(x, y), flight);
    if let Some(k) = counted("q") {
        wlog(format!("{} Q #{k}: the shell flies {d:.0} ({}){}", head(sim, caster),
                     if wall { "stopped by a wall" } else { "its full range" },
                     if ok { "" } else { " (spawn_projectile refused)" }));
    }
}

/// 炮弹打中一个敌人。
fn qhit(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1, back: bool) {
    if input.kind != InputTargetKindV1::Target.code() {
        return;
    }
    let t = input.target_id;
    let p = params_of(sim, caster);
    if back {
        let row = (sim_of(sim, caster), caster);
        let done = BLASTED.lock().unwrap_or_else(|e| e.into_inner()).get(&row).is_some_and(|v| v.contains(&t));
        if done {
            return;
        }
    }
    let ad = sim.get_entity(caster).map_or(0, |e| e.stat().attack);
    let (dmg, ratio, view, sfx) = if back { (p.q2_dmg, p.q2_ratio, "q_hit2", "q_hit2") } else { (p.q_dmg, p.q_ratio, "q_hit", "q_hit") };
    sim.deal_damage_typed(caster, t, dmg + ad * ratio / 100, DamageTypeV1::Ad, AttackTypeV1::Skill);
    sim.play_view_effect(&sn(view), caster, &InputTargetV1::target(t), 0, 0, 0);
    sim.play_sfx(&sn(sfx), caster, &InputTargetV1::target(t));
    if back {
        if let Some(k) = counted("q back") {
            wlog(format!("{} Q BACK #{k}: the shell flying back struck {}", head(sim, caster), who(sim, t)));
        }
    }
}

/// 炸弹落地：画面、引信音效，排爆炸（撞了墙的 q_wall 后就炸）。
fn bomb(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let p = params_of(sim, caster);
    let wall = shot_at((sim_of(sim, caster), caster), (input.x, input.y), false).is_some_and(|s| s.wall);
    let at = InputTargetV1::pos(input.x, input.y);
    sim.play_view_effect(&sn(if wall { "q_blast_w" } else { "q_blast" }), caster, &at, 0, 0, 0);
    sim.play_sfx(&sn("q_fuse"), caster, &at);
    queue(sim, "boom", caster, at, if wall { p.q_wall } else { p.q_fuse });
}

/// 爆炸：一圈，然后炮弹沿原路飞回去。
fn boom(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let p = params_of(sim, caster);
    let row = (sim_of(sim, caster), caster);
    let shot = shot_at(row, (input.x, input.y), true);
    let wall = shot.is_some_and(|s| s.wall);
    let end = (input.x as f64, input.y as f64);
    // back to where he shot from (his own spot when the shot is not found: his tag gone with him)
    let from = shot.map(|s| (s.from.0 as f64, s.from.1 as f64)).or_else(|| alive_at(sim, caster));
    let at = InputTargetV1::pos(input.x, input.y);
    sim.play_sfx(&sn("q_boom"), caster, &at);
    let (team, ad) = sim.get_entity(caster).map_or((usize::MAX, 0), |e| (e.team(), e.stat().attack));
    let mut struck = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.team() == team || !e.is_alive() || e.is_tower() || !e.is_targetable() {
            continue;
        }
        let (x, y) = e.pos();
        let d = ((x as f64 - end.0).powi(2) + (y as f64 - end.1).powi(2)).sqrt();
        if d <= p.q_r as f64 + e.radius() as f64 {
            struck.push(e.id());
        }
    }
    let amount = p.q2_dmg + ad * p.q2_ratio / 100;
    for &id in &struck {
        sim.deal_damage_typed(caster, id, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
        sim.play_view_effect(&sn("q_hit2"), caster, &InputTargetV1::target(id), 0, 0, 0);
    }
    BLASTED.lock().unwrap_or_else(|e| e.into_inner()).insert(row, struck.clone());
    let ok = from.is_some_and(|from| fly(sim, caster, end, from, p.q_w, p.q_speed * 2, "qback"));
    if let Some(k) = counted("q boom") {
        wlog(format!("{} Q BOOM #{k}: {} - the blast struck {} and the shell flies back{}{}", head(sim, caster),
                     if wall { "at the wall" } else { "after the fuse" }, struck.len(),
                     if ok { "" } else if from.is_none() { " (nowhere to fly back to)" } else { " (spawn_projectile refused)" },
                     if shot.is_none() { " - its shot was not found" } else { "" }));
    }
}

pub struct Stage(pub &'static str);

impl StableEffectType for Stage {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        match self.0 {
            "q" => launch(sim, caster, input),
            "qhit" => qhit(sim, caster, input, false),
            "qback" => qhit(sim, caster, input, true),
            "bomb" => bomb(sim, caster, input),
            "boom" => boom(sim, caster, input),
            _ => {}
        }
    }
}

pub fn register(module: &mut StableMod) {
    for s in ["q", "qhit", "qback", "bomb", "boom"] {
        module.add_native_effect(format!("{ID}:{s}"), Stage(s));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_shell_stops_short_of_a_wall() {
        let g = Grid::from_rows(&["....", "..#.", "...."]);
        // from (16000, 48000) toward +x: the wall cell x 64000..96000 at row 1
        let (end, wall) = end_of(&g, (16_000.0, 48_000.0), (1.0, 0.0), 70_000.0);
        assert!(wall);
        assert!((end.0 - (64_000.0 - WALL_GAP)).abs() <= STEP + 1.0, "{end:?}");
        // along row 0 nothing is in the way: its full range
        let (end, wall) = end_of(&g, (16_000.0, 16_000.0), (1.0, 0.0), 70_000.0);
        assert!(!wall);
        assert_eq!(end, (86_000.0, 16_000.0));
    }

    #[test]
    fn the_maps_load() {
        let g = Grid::builtin();
        assert!(g[0].walls() > 50);
    }

    /// 世界坐标的一个矩形：(左上, 右下)。
    type Rect = ((f64, f64), (f64, f64));

    /// 峡谷那样的墙格子（295 x 296 格，每格 60000/11，从 x = 30000/11 起，作者墙体文件的格子）：中心落在 `rects`
    /// （世界坐标的 (左上, 右下)）里的格子是墙。
    fn rift_walls(rects: &[Rect]) -> terrain::Walls {
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
    fn on_the_rift_the_shell_stops_at_the_rifts_walls() {
        // a wall in the Rift's far half, 40000 ahead of him
        let g = Grid::rift(Some(&rift_walls(&[((1_340_000.0, 1_200_000.0), (1_360_000.0, 1_300_000.0))])));
        let from = (1_300_000.0, 1_250_000.0);
        let (end, wall) = end_of(&g, from, (1.0, 0.0), 70_000.0);
        assert!(wall && (end.0 - (1_340_000.0 - WALL_GAP)).abs() <= g.cell + STEP && end.1 == from.1, "{end:?}");
        // the game's own grid had nothing out there: its full range
        assert_eq!(end_of(&Grid::builtin()[0], from, (1.0, 0.0), 70_000.0), ((1_370_000.0, 1_250_000.0), false));
        // past 960000 is open ground on the Rift, and a wall of the game's own 5v5 map is none on it
        let native = (15.5 * CELL, 3.5 * CELL);
        assert!(!g.is_wall(1_000_000.0, 1_000_000.0) && !g.is_wall(native.0, native.1));
        assert!(end_of(&Grid::builtin()[0], (native.0 - 40_000.0, native.1), (1.0, 0.0), 70_000.0).1);
        assert!(!end_of(&g, (native.0 - 40_000.0, native.1), (1.0, 0.0), 70_000.0).1);
        // no walls file: no wall known on the Rift, the full range everywhere
        let open = Grid::rift(None);
        assert_eq!(end_of(&open, from, (1.0, 0.0), 70_000.0), ((1_370_000.0, 1_250_000.0), false));
        assert!(!end_of(&open, (1_580_000.0, 800_000.0), (1.0, 0.0), 70_000.0).1, "past the map's edge is no wall either");
    }

    #[test]
    fn a_shot_waits_in_its_own_row_found_by_its_end() {
        // the queue hands back only the position (11-03 night: the wall flag in target_id never arrived): the wall and
        // where he shot from come back from the row, found by the end; twin presims (Graves #24 in both) keep their own
        let (a, b) = ((900_001, 24), (900_002, 24));
        let shot = Shot { end: (100_000, 50_000), from: (30_000, 50_000), wall: true };
        remember(a, shot);
        remember(b, Shot { wall: false, ..shot });
        let plain = InputTargetV1::pos(100_000, 50_000);
        assert_eq!((plain.dir_x, plain.dir_y, plain.target_id), (0, 0, 0));
        assert_eq!(shot_at(a, (plain.x, plain.y), false), Some(shot));   // the bomb lands: a wall's fuse
        assert_eq!(shot_at(a, (100_400, 49_800), true), Some(shot));     // the boom takes it
        assert_eq!(shot_at(a, (100_000, 50_000), false), None);
        assert_eq!(shot_at(b, (100_000, 50_000), true).map(|s| s.wall), Some(false));
        assert!(!SHOTS.lock().unwrap().contains_key(&b), "an emptied row goes");
        // another shot's end is not this one's
        remember(a, shot);
        assert_eq!(shot_at(a, (100_000 + SAME_END + 1, 50_000), true), None);
        assert_eq!(shot_at(a, (100_000, 50_000), true), Some(shot));
    }
}
