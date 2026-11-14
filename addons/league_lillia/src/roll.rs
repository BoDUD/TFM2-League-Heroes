//! 流涡种落地没打中人就往前滚（英雄联盟："Lillia lobs a seed at the target location that rolls forward indefinitely"，
//! 碰到敌人或地形就炸。用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」）。
//!
//! 主包的 E 是数据：种子扔到目标站的地方，落点有敌人就炸（魔法伤害、减速、梦尘），没人就没了——数据的投射物都从她身上
//! 出发，从落点再发一颗也会从她身上重新飞（2026-10-07 的日志），所以主包没滚。副本（`tools/kit/build_lillia.py` 的
//! `native`）在种子落地 1 tick 后看她身上的 `league_lillia_e_hit`（落点打中人时挂的），没有就调本包的
//! `league_lillia:e_roll`，输入是落点：
//!
//! - **方向**：从她现在站的地方到落点（英雄联盟按出手结束时她站的地方定方向；种子飞的那 20 tick 里她在放 E、接着放 W 的
//!   动作，站着没动）；
//! - **滚到地形为止**：沿这个方向每 [`STEP`] 看一次地图的墙（游戏自己的 5v5 / 单线 / 死斗图：league_camille_wall 的
//!   maps.rs，每格 32000，5v5 再加四边画出来的墙面），停在墙前 [`SEED_R`]；
//!   最远 `e_roll_len`（英雄联盟没有上限；这里滚满约 5 秒，碰不到下一次 E）；
//! - 本包自己发一颗直线投射物（`spawn_projectile`：从落点出发，每 tick `e_roll_speed`——英雄联盟 1400 码/秒——半径
//!   `e_roll_r`，碰到第一个敌方单位就停，防御塔、水晶不算），画面是主包 league_lillia_fx 的 `e_roll`（往右滚：顺时针转）
//!   或 `e_roll_l`（往左滚：游戏把图转半圈，所以画的是逆时针）——`tools/art/fx_lillia_roll.py` 用她自己飞着的种子转出来的；
//! - **打中谁就在他那里炸**（`league_lillia:e_roll_hit`），和落点那一下一样：`e_r` 加身体以内的敌方单位受到 `e_dmg` +
//!   `e_ratio`% 法强的魔法伤害、减速 `e_slow`% `e_slow_t` tick（`league_lillia_e_slow` 的画面）、主包的梦尘（数据是一个
//!   `AddCasted`：本包按它的时间排 `d_dmg` + `d_ratio`% 法强的魔法伤害，[`dust_delays`]）；敌方英雄另外挂本包的梦尘
//!   `league_lillia_dust`（被动按它跳最大生命的伤害、大招按它困倦），她回复 `d_heal` + `d_heal_ratio`% 法强、身上的
//!   `league_lillia_d_on` 续上（大招读它）。炸了就在她身上挂 `league_lillia_e_boom`；
//! - **滚到头**（墙、地图边、最远；`league_lillia:e_wall`，到头后 1 tick 再看 `e_boom`）没打中过人：在那里炸一下（画面，
//!   旁边有人照样吃）。
//!
//! 她死了（种子落地时）就不滚；滚着的时候她死了，打中照样炸（英雄联盟的种子离了手就和她无关），滚到头不炸（死了的英雄身上
//! 加不了旗子，分不清打没打中，宁可少炸一次）。没做：滚着打中英雄不会让待命中的大招放出来（数据的 `go()`；本包放不了她的
//! 大招，下一次 Q / W 打中照常放）。
//!
//! 日志（league_lillia.log）：`ROLL`（从哪滚、往哪、多远、为什么停、哪张图）、`ROLL HIT`、`ROLL WALL`、`ROLL none`（落在墙前）、
//! `ROLL refused`、`ROLL input`（数据给的不是落点），前 `LOG_FIRST` 次和之后每 `LOG_EVERY` 次记一行。

use std::collections::HashMap;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

use super::{data_dust, head, ll, maps, params, wlog, Params, ID};

pub type Pt = (f64, f64);

/// 往前看墙的步长（游戏自己的墙格 32000 看得出来）。
pub const STEP: f64 = 1_000.0;
/// 种子的半径（画出来 8 格宽，1 格 1000）：停在墙前这么远，画面不压在墙上。
pub const SEED_R: f64 = 4_000.0;
/// 读不到身体半径时用的。
pub const BODY: f64 = 10_000.0;
/// 游戏自己的 5v5 图四边画出来的墙面（league_camille_wall 量的；league_taliyah 的 `MOBA_BOUNDS`）和墙格的边长。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);
pub const CELL: f64 = 32_000.0;
/// 滚着的种子的两张图（副本的 `view_projectiles`）：往右滚顺时针、往左滚逆时针（游戏把往左飞的图转半圈）。
pub const ROLL: &str = "league_lillia_e_roll";
pub const ROLL_L: &str = "league_lillia_e_roll_l";
/// 滚着打中过人：她身上的旗子（滚到头时看它，打中过就不再炸）。
pub const BOOM: &str = "league_lillia_e_boom";

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

// ===================== 计算（单元测试用） =====================

pub fn dist(a: Pt, b: Pt) -> f64 {
    (a.0 - b.0).hypot(a.1 - b.1)
}

pub fn unit(v: Pt) -> Option<Pt> {
    let d = v.0.hypot(v.1);
    (d >= 1.0).then(|| (v.0 / d, v.1 / d))
}

/// 种子炸一下的魔法伤害（减免前）。
pub fn seed_damage(p: &Params, ap: usize) -> usize {
    p.e_dmg + p.e_ratio * ap / 100
}

/// 打中一个英雄她回复多少（主包的 `heal_me(d_heal, d_heal_ratio)`）。
pub fn heal_amount(p: &Params, ap: usize) -> usize {
    p.d_heal + p.d_heal_ratio * ap / 100
}

/// 主包的梦尘（`AddCasted` `d_t` tick、每 `d_period` 一跳）从挂上起第几 tick 跳：挂上的下一 tick 第一跳，之后每 `d_period`，
/// 跳到满 `d_t` 为止（champion-data：`duration` 301、`period` 60 是 0..300 的六跳）。
pub fn dust_delays(p: &Params) -> Vec<usize> {
    let period = p.d_period.max(1);
    (0..).map(|k| 1 + k * period).take_while(|d| d - 1 < p.d_t).collect()
}

/// 往右滚（含正上、正下）用顺时针那张，往左滚用逆时针那张。
pub fn roll_picture(dir: Pt) -> &'static str {
    if dir.0 >= 0.0 {
        ROLL
    } else {
        ROLL_L
    }
}

/// 一张地图的地形。
#[derive(Clone, Copy, Debug)]
pub enum Ground {
    /// 游戏自己的墙格（`#` 是墙，每格 [`CELL`]，格子外是墙）和四边画出来的墙面。
    Grid(&'static [&'static str], Option<(f64, f64, f64, f64)>),
}

impl Ground {
    fn cell_wall(rows: &[&str], p: Pt) -> bool {
        if p.0 < 0.0 || p.1 < 0.0 {
            return true;
        }
        let (cx, cy) = ((p.0 / CELL) as usize, (p.1 / CELL) as usize);
        rows.get(cy).and_then(|r| r.as_bytes().get(cx)).is_none_or(|c| *c == b'#')
    }

    /// 种子滚不过去的地方：墙、地图外。
    pub fn is_wall(&self, p: Pt) -> bool {
        match *self {
            Ground::Grid(rows, bounds) => {
                if let Some((x0, y0, x1, y1)) = bounds {
                    if p.0 <= x0 || p.1 <= y0 || p.0 >= x1 || p.1 >= y1 {
                        return true;
                    }
                }
                Ground::cell_wall(rows, p)
            }
        }
    }
}

/// 游戏自己的三张图。
pub fn native_grounds() -> [(&'static str, Ground); 3] {
    [
        ("Moba", Ground::Grid(&maps::MOBA, Some(MOBA_BOUNDS))),
        ("SingleLane", Ground::Grid(&maps::SINGLE_LANE, None)),
        ("DeathMatch", Ground::Grid(&maps::DEATH_MATCH, None)),
    ]
}

/// 游戏自己的图里是哪一张：站进墙格的单位最少的那张，一样少时墙格最多的（league_taliyah 的 `surf::pick`）。
pub fn pick_native(points: &[Pt]) -> (&'static str, Ground) {
    native_grounds()
        .into_iter()
        .map(|(n, g)| {
            let Ground::Grid(rows, _) = g;
            let inside = points.iter().filter(|p| Ground::cell_wall(rows, **p)).count();
            let walls = rows.iter().map(|r| r.bytes().filter(|c| *c == b'#').count()).sum::<usize>();
            (inside, walls, n, g)
        })
        .min_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)))
        .map(|(_, _, n, g)| (n, g))
        .expect("three built-in maps")
}

/// 为什么停下。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stop {
    /// 前面是墙（或地图外）。
    Wall,
    /// 滚满了 `e_roll_len`。
    Far,
}

/// 从 `from` 朝 `dir`（单位向量）滚：每 [`STEP`] 看一次，碰到墙前停下（离墙 [`SEED_R`]），最远 `max`。
/// 返回 (终点, 滚了多远, 为什么停)。
pub fn march(g: &Ground, from: Pt, dir: Pt, max: f64) -> (Pt, f64, Stop) {
    let n = (max / STEP).floor() as usize;
    let (mut open, mut stop) = (0.0, Stop::Far);
    for k in 1..=n {
        let d = k as f64 * STEP;
        if g.is_wall((from.0 + dir.0 * d, from.1 + dir.1 * d)) {
            stop = Stop::Wall;
            break;
        }
        open = d;
    }
    let len = if stop == Stop::Wall { (open - SEED_R).max(0.0) } else { open };
    ((from.0 + dir.0 * len, from.1 + dir.1 * len), len, stop)
}

/// 种子滚多少 tick 到头（滚到头那一下排在到头后 1 tick：最后一 tick 打中的人先算）。
pub fn roll_ticks(len: f64, speed: usize) -> usize {
    (len / speed.max(1) as f64).ceil().max(1.0) as usize
}

// ===================== 游戏里 =====================

fn fpos(e: &StableEntity<'_, '_>) -> Pt {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

fn upos(p: Pt) -> InputTargetV1 {
    InputTargetV1::pos(p.0.max(0.0).round() as u64, p.1.max(0.0).round() as u64)
}

fn input_pos(input: &InputTargetV1) -> Option<Pt> {
    (input.kind == InputTargetKindV1::Pos.code()).then_some((input.x as f64, input.y as f64))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn refresh(sim: &mut StableSim<'_>, id: usize, b: &BuffV1) {
    sim.entity_remove_buff(id, b.name());
    sim.add_buff(id, b);
}

/// 这一局的地形：游戏自己的图看单位站在哪（每次滚都看一次：几十个单位，几毫秒都不到）。
pub fn ground_of(sim: &StableSim<'_>) -> (&'static str, Ground) {
    let points: Vec<Pt> =
        (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).filter(|e| e.is_alive()).map(|e| fpos(&e)).collect();
    pick_native(&points)
}

/// `at` 周围 `r` 加身体以内活着、选得中的敌方单位（防御塔、水晶不算，同主包的 `EnemyWithoutTower`）：(编号, 是不是英雄)。
fn foes_near(sim: &StableSim<'_>, team: usize, at: Pt, r: f64) -> Vec<(usize, bool)> {
    let mut out = Vec::new();
    for u in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
        if !u.is_alive() || u.team() == team || !u.is_targetable() || u.is_tower()
            || matches!(u.kind(), Some(EntityKindV1::Tower | EntityKindV1::Nexus))
        {
            continue;
        }
        let body = match u.radius() {
            0 => BODY,
            b => b as f64,
        };
        if dist(fpos(&u), at) <= r + body {
            out.push((u.id(), u.is_champion()));
        }
    }
    out
}

/// 种子在 `at` 炸开（滚着打中人、滚到头）：和落点那一下一样。返回 (炸到几个, 其中几个英雄)。
fn detonate(sim: &mut StableSim<'_>, me: usize, at: Pt) -> (usize, usize) {
    let p = params();
    let Some((team, ap, alive)) = sim.get_entity(me).map(|e| (e.team(), e.stat().magic_power, e.is_alive())) else {
        return (0, 0);
    };
    sim.play_view_effect(&ll("e_land"), me, &upos(at), 0, 0, 0);
    let foes = foes_near(sim, team, at, p.e_r as f64);
    let dmg = seed_damage(&p, ap);
    let dust_run = format!("{ID}:e_dust");
    let delays = dust_delays(&p);
    let mut slow = BuffV1::timed(&ll("e_slow"), p.e_slow_t);
    slow.move_speed_mult = -(p.e_slow as i32);
    let dust = BuffV1::timed(&ll("dust"), p.d_t);
    let mut champions = 0;
    for &(id, champion) in &foes {
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        refresh(sim, id, &slow);
        let on = InputTargetV1::target(id);
        sim.play_view_effect(&ll("e_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(&ll("e_hit"), me, &on);
        for &d in &delays {
            sim.queue_effect(&dust_run, AttackTypeV1::Dot, me, &on, d);
        }
        if champion {
            champions += 1;
            refresh(sim, id, &dust);
            if alive {
                sim.heal(me, me, heal_amount(&p, ap));
            }
        }
    }
    if champions > 0 && alive {
        refresh(sim, me, &BuffV1::timed(&ll("d_on"), p.d_t));
    }
    (foes.len(), champions)
}

/// 种子落地没打中人（副本的数据在落地 1 tick 后调它，输入是落点）：往前滚。
pub struct Roll;

impl StableEffectType for Roll {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(land) = input_pos(&input) else {
            // the data hands the landing point (a `Delayed` in a lob's end_effects keeps it, as league_ziggs' q_hop)
            if let Some(k) = counted("input") {
                wlog(format!("{} ROLL input #{k}: not a point (kind {}): no roll", head(sim, caster), input.kind));
            }
            return;
        };
        let Some((me_at, team)) = sim.get_entity(caster).filter(|e| e.is_alive()).map(|e| (fpos(&e), e.team())) else {
            return;
        };
        let Some(dir) = unit((land.0 - me_at.0, land.1 - me_at.1)) else { return };
        let p = params();
        let (map, g) = ground_of(sim);
        let (end, len, stop) = march(&g, land, dir, p.e_roll_len as f64);
        if len < p.e_roll_speed.max(1) as f64 {
            if let Some(k) = counted("short") {
                wlog(format!("{} ROLL none #{k}: landed at ({:.0}, {:.0}) facing a wall ({len:.0} to roll, {map})",
                             head(sim, caster), land.0, land.1));
            }
            return;
        }
        sim.entity_remove_buff(caster, BOOM);
        let (x, y) = (land.0.round() as u64, land.1.round() as u64);
        let to = upos(end);
        let spec = ProjectileSpawnV1 {
            caster_id: caster,
            team,
            x,
            y,
            radius: p.e_roll_r as u64,
            speed: p.e_roll_speed.max(1) as u64,
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: to.x,
            target_y: to.y,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        let picture = roll_picture(dir);
        if !sim.spawn_projectile(picture, &format!("{ID}:e_roll_hit"), &spec) {
            if let Some(k) = counted("refused") {
                wlog(format!("{} ROLL refused #{k}: spawn_projectile({picture})", head(sim, caster)));
            }
            return;
        }
        let ticks = roll_ticks(len, p.e_roll_speed);
        sim.queue_effect(&format!("{ID}:e_wall"), AttackTypeV1::Skill, caster, &to, ticks + 1);
        if let Some(k) = counted("roll") {
            wlog(format!(
                "{} ROLL #{k}: from ({:.0}, {:.0}) toward ({:.2}, {:.2}), {len:.0} in {ticks} ticks to ({:.0}, {:.0}), stops at {:?} ({map}, {picture})",
                head(sim, caster),
                land.0,
                land.1,
                dir.0,
                dir.1,
                end.0,
                end.1,
                stop
            ));
        }
    }
}

/// 滚着的种子碰到第一个敌方单位（输入是他）：在他那里炸。
pub struct RollHit;

impl StableEffectType for RollHit {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let Some(at) = sim.get_entity(input.target_id).map(|e| fpos(&e)) else { return };
        if has_buff(sim, caster, BOOM) {
            return;
        }
        let p = params();
        if sim.get_entity(caster).is_some_and(|e| e.is_alive()) {
            sim.add_buff(caster, &BuffV1::timed(BOOM, roll_ticks(p.e_roll_len as f64, p.e_roll_speed) + 30));
        }
        let (n, champions) = detonate(sim, caster, at);
        if let Some(k) = counted("hit") {
            let name = sim.get_entity(input.target_id).and_then(|e| e.name()).unwrap_or_default();
            wlog(format!("{} ROLL HIT #{k}: on {name}#{} at ({:.0}, {:.0}): {n} enemies hit ({champions} champions)",
                         head(sim, caster), input.target_id, at.0, at.1));
        }
    }
}

/// 种子滚到头（墙、地图边、最远）：没打中过人就在那里炸一下。
pub struct RollEnd;

impl StableEffectType for RollEnd {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = input_pos(&input) else { return };
        if !sim.get_entity(caster).is_some_and(|e| e.is_alive()) {
            return;
        }
        if has_buff(sim, caster, BOOM) {
            sim.entity_remove_buff(caster, BOOM);
            return;
        }
        let (n, champions) = detonate(sim, caster, at);
        if let Some(k) = counted("wall") {
            wlog(format!("{} ROLL WALL #{k}: at ({:.0}, {:.0}): {n} enemies hit ({champions} champions)", head(sim, caster),
                         at.0, at.1));
        }
    }
}

/// 主包梦尘的一跳（数据的 `AddCasted` 的效果：魔法伤害，算持续伤害）：目标还活着就打。
pub struct DustRun;

impl StableEffectType for DustRun {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target)
            || !sim.get_entity(input.target_id).is_some_and(|e| e.is_alive())
        {
            return;
        }
        let ap = sim.get_entity(caster).map_or(0, |e| e.stat().magic_power);
        sim.deal_damage_typed(caster, input.target_id, data_dust(&params(), ap), DamageTypeV1::Ap, AttackTypeV1::Dot);
    }
}

/// 本包的四个原生效果。
pub fn register(module: &mut StableMod) {
    module.add_native_effect(format!("{ID}:e_roll"), Roll);
    module.add_native_effect(format!("{ID}:e_roll_hit"), RollHit);
    module.add_native_effect(format!("{ID}:e_wall"), RollEnd);
    module.add_native_effect(format!("{ID}:e_dust"), DustRun);
}

#[cfg(test)]
mod tests {
    use super::*;

    fn moba() -> Ground {
        native_grounds()[0].1
    }

    #[test]
    fn it_rolls_up_to_the_wall_on_the_games_own_map() {
        // row 3 of the 5v5 grid is "...............##.####........": wall cells x 15-16 (480000-544000), y 96000-128000
        let g = moba();
        let from = (300_000.0, 110_000.0);
        let (end, len, stop) = march(&g, from, (1.0, 0.0), 700_000.0);
        assert_eq!(stop, Stop::Wall);
        assert_eq!(len, 480_000.0 - 1_000.0 - 300_000.0 - SEED_R, "the last open look before the cell, less the seed");
        assert_eq!(end, (300_000.0 + len, 110_000.0));
        assert!(!g.is_wall(end) && g.is_wall((480_001.0, 110_000.0)));
        // open ground the whole way: it stops at the cap
        let (_, len, stop) = march(&g, (300_000.0, 60_000.0), (1.0, 0.0), 100_000.0);
        assert_eq!((len, stop), (100_000.0, Stop::Far));
        // the map's drawn edge faces stop it too (the top one at y 26000)
        let (end, _, stop) = march(&g, (100_000.0, 60_000.0), (0.0, -1.0), 700_000.0);
        assert_eq!(stop, Stop::Wall);
        assert!(end.1 > MOBA_BOUNDS.1 && end.1 <= MOBA_BOUNDS.1 + 1_000.0 + SEED_R, "{end:?}");
        // a landing right in front of a wall: nothing to roll
        let (_, len, _) = march(&g, (478_000.0, 110_000.0), (1.0, 0.0), 700_000.0);
        assert_eq!(len, 0.0);
    }

    #[test]
    fn the_map_is_told_from_where_units_stand() {
        // (100000, 100000) is open on the 5v5 map only; (480000, 480000) is open on all three
        assert_eq!(pick_native(&[(480_000.0, 480_000.0), (100_000.0, 100_000.0)]).0, "Moba");
        // (700000, 100000) lies on the single lane and in a 5v5 wall
        assert_eq!(pick_native(&[(480_000.0, 480_000.0), (700_000.0, 100_000.0)]).0, "SingleLane");
        // everyone in the death match's box (open on the 5v5 map too): the map with more walls
        assert_eq!(pick_native(&[(300_000.0, 450_000.0), (700_000.0, 520_000.0)]).0, "DeathMatch");
    }

    #[test]
    fn its_dust_runs_when_the_data_dust_would() {
        // the data: AddCasted 181 ticks, every 45, first run a tick after the hit: 0..180 -> five runs
        let p = Params::default();
        assert_eq!(dust_delays(&p), vec![1, 46, 91, 136, 181]);
        assert_eq!(dust_delays(&Params { d_t: 180, ..Params::default() }), vec![1, 46, 91, 136]);
        assert_eq!(seed_damage(&p, 100), 45 + 40);
        assert_eq!(heal_amount(&p, 100), 12 + 8);
    }

    #[test]
    fn the_picture_spins_the_way_it_rolls() {
        assert_eq!(roll_picture((1.0, 0.0)), ROLL);
        assert_eq!(roll_picture((0.0, 1.0)), ROLL);
        assert_eq!(roll_picture((-0.6, 0.8)), ROLL_L);
        for n in [ROLL, ROLL_L, BOOM] {
            assert!(n.len() <= BUFF_NAME_CAP);
        }
        assert_eq!(roll_ticks(9_000.0, 2_330), 4);
        assert_eq!(roll_ticks(1.0, 2_330), 1);
    }

    #[test]
    fn the_roll_never_outlasts_the_next_seed() {
        // E's cooldown 600 ticks: a whole roll (cap) is over well before the next throw lands
        let p = Params::default();
        assert!(roll_ticks(p.e_roll_len as f64, p.e_roll_speed) + 30 < 600 - 27, "{}", roll_ticks(p.e_roll_len as f64, p.e_roll_speed));
    }
}
