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
//! 输入里带着这一发的信息：`x`/`y` 终点，`dir_x`/`dir_y` 出手的地方，`target_id` 1 = 撞了墙。

use std::collections::HashMap;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

use super::{counted, head, maps, params_of, sn, who, wlog, ID};

/// 墙格的边长（世界单位）。
pub const CELL: f64 = 32_000.0;
/// 沿路线找墙的步长。
pub const STEP: f64 = 500.0;
/// 炸弹停在离墙这么远处。
pub const WALL_GAP: f64 = 3_000.0;

pub type Pt = (f64, f64);

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

    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return false;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
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

/// 这一发的信息塞进输入：终点、出手的地方、撞墙了没有。
fn carry(end: Pt, from: Pt, wall: bool) -> InputTargetV1 {
    let (x, y) = upos(end);
    let (fx, fy) = upos(from);
    InputTargetV1 { kind: InputTargetKindV1::Pos.code(), target_id: wall as usize, dir_x: fx as i64, dir_y: fy as i64, x, y }
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

/// 爆炸炸到过的单位：飞回来的炮弹不再打它们（按这局的种子和格雷福斯的编号，记最近一次爆炸）。
static BLASTED: LazyLock<Mutex<HashMap<(u64, usize), Vec<usize>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

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
    let mut champs = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.is_champion() && u.is_alive() {
            let (x, y) = u.pos();
            champs.push((x as f64, y as f64));
        }
    }
    let grids = Grid::builtin();
    let (end, wall) = match current(&grids, &champs) {
        Some(gi) => end_of(&grids[gi], here, dir, p.q_range as f64),
        None => ((here.0 + dir.0 * p.q_range as f64, here.1 + dir.1 * p.q_range as f64), false),
    };
    let d = ((end.0 - here.0).powi(2) + (end.1 - here.1).powi(2)).sqrt();
    let flight = (d / p.q_speed as f64).ceil() as usize;
    let ok = fly(sim, caster, here, end, p.q_w, p.q_speed, "qhit");
    queue(sim, "bomb", caster, carry(end, here, wall), flight);
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
        let done = BLASTED.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim.seed(), caster)).is_some_and(|v| v.contains(&t));
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

/// 炸弹落地：画面、引信音效，排爆炸。
fn bomb(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let p = params_of(sim, caster);
    let wall = input.target_id == 1;
    let at = InputTargetV1::pos(input.x, input.y);
    sim.play_view_effect(&sn(if wall { "q_blast_w" } else { "q_blast" }), caster, &at, 0, 0, 0);
    sim.play_sfx(&sn("q_fuse"), caster, &at);
    queue(sim, "boom", caster, input, if wall { p.q_wall } else { p.q_fuse });
}

/// 爆炸：一圈，然后炮弹沿原路飞回去。
fn boom(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let p = params_of(sim, caster);
    let end = (input.x as f64, input.y as f64);
    let from = (input.dir_x as f64, input.dir_y as f64);
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
    BLASTED.lock().unwrap_or_else(|e| e.into_inner()).insert((sim.seed(), caster), struck.clone());
    let ok = fly(sim, caster, end, from, p.q_w, p.q_speed * 2, "qback");
    if let Some(k) = counted("q boom") {
        wlog(format!("{} Q BOOM #{k}: {} - the blast struck {} and the shell flies back{}", head(sim, caster),
                     if input.target_id == 1 { "at the wall" } else { "after the fuse" }, struck.len(),
                     if ok { "" } else { " (spawn_projectile refused)" }));
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

    #[test]
    fn the_input_carries_the_shot() {
        let i = carry((100_000.0, 50_000.0), (30_000.0, 50_000.0), true);
        assert_eq!((i.x, i.y, i.dir_x, i.dir_y, i.target_id), (100_000, 50_000, 30_000, 50_000, 1));
    }
}
