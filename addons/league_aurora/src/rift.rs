//! 双界合一的领域按英雄联盟来（V26.21；用户 2026-11-04：「阿罗拉的大招机制逻辑也是不太一样」）。
//!
//! 数据（tools/kit/build_aurora.py 的附加包副本）：她朝目标跃出一小段，落地时冲击波在她前方 `r_ahead` 炸开，一根隐形的线停在
//! 冲击波的中心，那里放领域的画面，并调本包的原生效果 `league_aurora:rift`（[`Open`]）：它把中心写进她身上的 buff
//! `league_aurora_rift_new:<x>,<y>`，被动（`league_aurora:veil`）下一 tick 读走，领域就开着 `r_t` tick（[`Rift`]）：
//!
//! - **敌人碰到边界**（[`touches`]：离圈心 `RING` ± `BAND`，身体压在画出来的那一圈上）：减速 `r_edge`% `r_edge_t` tick，
//!   一次穿越只一次——离开边界、再碰上才再减（英雄联盟 50%、1.5–2 秒）。这一下顶掉冲击波的 30%（英雄联盟的减速取最强的
//!   那个，TFM2 的会相加，两个叠起来是 80%）。领域里面、外面都不减。
//! - **她碰到边界**（[`place`]：离圈心 `EDGE` 以外）：沿直径冲到对面（[`across`]，离圈心 `LAND`，落点避开墙格），
//!   `r_wrap_t` tick 的强制位移（英雄联盟 0.4 秒、选不中、不能行动）：这期间她免伤、免控、穿墙（`league_aurora_r_wrap`；
//!   TFM2 里选不中只有放逐，放逐的单位挪不动、还瞎了全队的视野），摆 `veil` 的姿势，两头各开一扇门
//!   （`league_aurora_r_blink`）。所以她走不出领域，只会绕到对面。被眩晕、定身、嘲讽、恐惧、魅惑、击飞、禁止位移时不冲
//!   （等控制过去）；她自己的后跳（怪奇喷涌、灵纱洞开：副本的数据给她挂 `league_aurora_own_hop`）撞上边界一样冲到对面
//!   （那一下后跳在边界上打住）；被敌人击退、拉扯时不冲（不白白解控），被带出去就算离开，停在边界上就等位移完了再冲。
//!   宿主没挪她（强制位移被拒：别处来的免控）就自己一步步挪（巴德附加包的做法），冲完离落点还远就直接放上去。
//! - **关闭**：她死了；到了外面（离圈心 `EDGE + OUT` 以外：闪现、被敌人带出去）；开的时候她不在里面；`r_t` 到了
//!   （正在冲就冲完再关）。画面是数据放的，提前关时照样放完（停不下来）。
//! - 开着时她身上挂 `league_aurora_rift:<x>,<y>`（每 tick 续 2 tick），AI 钩子（`realm.rs`）据此在领域里放风筝、不往外走。
//!
//! 状态都在她的被动里（每局、每个她一份），不用全局变量。日志：`RIFT OPEN` / `RIFT CROSS` / `RIFT EDGE` / `RIFT CLOSED`
//! （你看的那场每行都写，预模拟每种前 40 行、之后每 100 行一行）。
//!
//! 两张 5v5 地图（2026-11-10，用户：「要同时兼容原版地图和这个地图」）：冲到对面的落点避的墙按这局的塔和水晶判断是哪张图
//! （`game_places::terrain::map_of_sim`）。游戏自己的地图照旧；Rin 的召唤师峡谷（1614545 见方；本文件别处的「领域」是她的
//! 大招，不是这张图）用峡谷作者的墙体文件（`terrain::rift_walls`，295 x 296 格、每格 60000/11），没有文件时峡谷上只有地图外
//! 算墙（以前 960000 以外全算墙：峡谷远半边每次都往圈心退到底、冲不过去）。

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::LazyLock;

use game_places::terrain::{self, Map};
use mod_api_stable::*;

use super::maps;
use super::{counted, dist, head, on_screen, wlog, Params};

pub type Pt = (f64, f64);

/// 领域的边界：画面上那一圈（league_aurora_big 的 r_zone，75 像素宽）= 主包参数表的 r_zone。
pub const RING: f64 = 38_000.0;
/// 她的中心离圈心这么远就算碰到边界（脚踩到那一圈）。落地时她在 `r_ahead`（25500）处，往外还有 10500。
pub const EDGE: f64 = 36_000.0;
/// 冲到对面后离圈心这么远（在 `EDGE` 以内，不会一落地又冲回去）。
pub const LAND: f64 = 30_000.0;
/// 一下子到了 `EDGE + OUT` 以外、没在边界上停过（闪现、被远远甩出去）：算她离开了领域。她自己最快的位移一 tick 4000。
pub const OUT: f64 = 8_000.0;
/// 敌人的中心离那一圈不到这么远就算碰到边界（大半个身体压在圈上）。
pub const BAND: f64 = 8_000.0;
/// 冲完这么多 tick 内不再冲。
pub const GRACE: usize = 8;
/// 出口的门提前这么多 tick 开（门的画面 0.34 秒，约 20 tick）。
pub const EXIT_AT: usize = 14;
/// 冲完离落点超过这么远：直接放到落点上。
pub const SNAP: f64 = 6_000.0;
/// 落点在墙里时往圈心退的步长。
pub const STEP: f64 = 4_000.0;

/// 原生效果写给被动的新领域（`<x>,<y>`）。
pub const NEW: &str = "league_aurora_rift_new";
/// 被动给 AI 钩子的标记：领域开着、在哪（`<x>,<y>`）。
pub const AT: &str = "league_aurora_rift";
/// 冲到对面时她身上的：免伤、免控、穿墙。AI 钩子见到它就不管。
pub const WRAP: &str = "league_aurora_r_wrap";
/// 边界的减速（主包的画面 `league_aurora_r_edge`，脚下的霜雾）。
pub const EDGE_SLOW: &str = "league_aurora_r_edge";
/// 冲击波的减速：碰到边界的人身上的这个被边界的顶掉。
pub const SHOCK_SLOW: &str = "league_aurora_r_slow1";
/// 两头的门（主包的画面和声音）。
pub const DOOR: &str = "league_aurora_r_blink";
/// 冲的时候摆的姿势（她的 veil 动作）。
pub const POSE: &str = "veil";
/// 她自己的后跳（副本的数据在怪奇喷涌、灵纱洞开的 MoveBack 旁挂上，后跳的 tick + 2）：这样的强制位移撞上边界才冲到对面。
pub const OWN_HOP: &str = "league_aurora_own_hop";

/// `<名字>:<x>,<y>`。
pub fn at_name(prefix: &str, c: Pt) -> String {
    format!("{prefix}:{},{}", c.0.round().max(0.0) as u64, c.1.round().max(0.0) as u64)
}

/// [`at_name`] 反过来；别的名字（`league_aurora_rift_new` 对 `league_aurora_rift`）不认。
pub fn parse_at(name: &str, prefix: &str) -> Option<Pt> {
    let (x, y) = name.strip_prefix(prefix)?.strip_prefix(':')?.split_once(',')?;
    Some((x.parse::<u64>().ok()? as f64, y.parse::<u64>().ok()? as f64))
}

// ===================== 几何（单元测试） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Place {
    Inside,
    /// 碰到了边界：冲到对面。
    Border,
    /// 没碰边界就到了外面。
    Out,
}

pub fn place(c: Pt, me: Pt) -> Place {
    let d = dist(c, me);
    if d < EDGE {
        Place::Inside
    } else if d <= EDGE + OUT {
        Place::Border
    } else {
        Place::Out
    }
}

/// 对面：她的位置过圈心的那条直径另一头，离圈心 `LAND`（她正好在圈心时往右）。
pub fn across(c: Pt, me: Pt) -> Pt {
    let d = dist(c, me);
    let u = if d < 1.0 { (1.0, 0.0) } else { ((me.0 - c.0) / d, (me.1 - c.1) / d) };
    (c.0 - u.0 * LAND, c.1 - u.1 * LAND)
}

/// 这个单位（中心 `u`）碰着边界吗。
pub fn touches(c: Pt, u: Pt) -> bool {
    (dist(c, u) - RING).abs() <= BAND
}

/// 地图的墙格（league_camille_wall 的内置地图，Tahm Kench、Poppy、Gnar 附加包同样用它）；5v5 地图另加四边。每格 `cell`
/// 见方，(0, 0) 格的角在 `origin`（游戏自己的地图 32000、(0, 0)；峡谷的墙体文件 60000/11、(30000/11, 0)）。
pub struct Grid {
    pub cells: Vec<Vec<bool>>,
    pub bounds: Option<(f64, f64, f64, f64)>,
    pub cell: f64,
    pub origin: (f64, f64),
}

/// 游戏自己的地图格子的边长。
pub const CELL: f64 = 32_000.0;
/// 5v5 地图四边（上下的石墙、左右的石堆）以内的可走范围（league_camille_wall 的 `MOBA_BOUNDS`）。
pub const MOBA_BOUNDS: (f64, f64, f64, f64) = (22_500.0, 26_000.0, 937_500.0, 932_000.0);

impl Grid {
    pub fn from_rows(rows: &[&str], bounds: Option<(f64, f64, f64, f64)>) -> Grid {
        Grid { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect(), bounds, cell: CELL,
               origin: (0.0, 0.0) }
    }

    /// 0 = 5v5（四边也是墙），1 = 单线，2 = 死斗。
    pub fn builtin() -> [Grid; 3] {
        [
            Grid::from_rows(&maps::MOBA, Some(MOBA_BOUNDS)),
            Grid::from_rows(&maps::SINGLE_LANE, None),
            Grid::from_rows(&maps::DEATH_MATCH, None),
        ]
    }

    /// 召唤师峡谷的墙：有墙体文件就是文件的墙格（四边在文件里就是墙）；没有就是一格地图大小的空地（只有地图外算墙）。
    pub fn summoners_rift(walls: Option<&terrain::Walls>) -> Grid {
        match walls {
            Some(w) => Grid { cells: w.cells.clone(), bounds: None, cell: w.cell, origin: w.origin },
            None => Grid { cells: vec![vec![false]], bounds: None, cell: terrain::RIFT_EXTENT, origin: (0.0, 0.0) },
        }
    }

    /// 世界坐标落在墙里吗（地图外、5v5 的四边外都算墙）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < self.origin.0 || y < self.origin.1 {
            return true;
        }
        if let Some((x0, y0, x1, y1)) = self.bounds {
            if x < x0 || y < y0 || x > x1 || y > y1 {
                return true;
            }
        }
        let (cx, cy) = (((x - self.origin.0) / self.cell) as usize, ((y - self.origin.1) / self.cell) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(true)
    }

    pub fn walls(&self) -> usize {
        self.cells.iter().flatten().filter(|w| **w).count()
    }
}

/// 当前对局的地图：单位站进墙里最少的那张（同 Tahm Kench、Poppy、巴德附加包）。
pub fn current(grids: &[Grid], points: &[Pt]) -> Option<usize> {
    grids
        .iter()
        .enumerate()
        .min_by_key(|(_, g)| (points.iter().filter(|&&(x, y)| g.is_wall(x, y)).count(), std::cmp::Reverse(g.walls())))
        .map(|(i, _)| i)
}

/// 游戏的三张内置地图，和召唤师峡谷的墙（墙体文件每次启动只读、只换一次，第一次到峡谷上才读）。
static GRIDS: LazyLock<[Grid; 3]> = LazyLock::new(Grid::builtin);
static SR_GRID: LazyLock<Grid> = LazyLock::new(|| Grid::summoners_rift(terrain::rift_ground()));

/// 这局的墙：召唤师峡谷上是峡谷的（第一次遇到时日志里记一行），游戏自己的地图照旧从三张内置地图里挑（[`current`]）。
fn walls_now(sim: &StableSim<'_>) -> Option<&'static Grid> {
    match terrain::map_of_sim(sim) {
        Map::Rift => {
            static MET: AtomicBool = AtomicBool::new(false);
            if !MET.swap(true, Ordering::Relaxed) {
                wlog(format!("== Rift (Summoner's Rift, the map): her crossing lands clear of its walls (from its walls \
                              file; with no file only the map's edges count); {} ==", terrain::rift_status()));
            }
            Some(&*SR_GRID)
        }
        Map::Native => {
            let points: Vec<Pt> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).filter(|u| u.is_alive())
                .map(|u| pt(u.pos())).collect();
            current(&*GRIDS, &points).map(|i| &GRIDS[i])
        }
    }
}

/// 落点：对面那一点；在墙里（或地图外）就沿直径一步步往圈心退，退到圈心还在墙里就不冲（None）。
pub fn landing(grid: &Grid, c: Pt, far: Pt) -> Option<Pt> {
    let steps = (dist(far, c) / STEP).ceil() as usize;
    (0..=steps).map(|k| {
        let f = if steps == 0 { 0.0 } else { k as f64 / steps as f64 };
        (far.0 + (c.0 - far.0) * f, far.1 + (c.1 - far.1) * f)
    }).find(|q| !grid.is_wall(q.0, q.1))
}

// ===================== 原生效果：领域开在哪 =====================

/// `league_aurora:rift`（数据在冲击波中心那根线的 end_effects 里调，输入是那一点）：把中心写给她的被动。
pub struct Open;

impl StableEffectType for Open {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let c = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Pos) => Some((input.x as f64, input.y as f64)),
            Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|t| pt(t.pos())),
            _ => None,
        };
        let Some(c) = c else {
            if let Some(n) = counted("rift input", on_screen(sim)) {
                wlog(format!("{} RIFT input kind {} is no point: no rift #{n}", head(sim, me), input.kind));
            }
            return;
        };
        sim.add_buff(me, &BuffV1::timed(&at_name(NEW, c), 3));
    }
}

// ===================== 被动：领域开着的每个 tick =====================

/// 冲到对面的那一趟。
#[derive(Clone, Debug)]
pub struct Cross {
    pub from: Pt,
    pub to: Pt,
    pub until: usize,
    /// 出口的门开了没有。
    pub door: bool,
    /// 上一 tick 她在哪（宿主没挪她就自己挪）。
    pub last: Pt,
    pub step: f64,
}

/// 一个开着的领域（她的被动里，每局每个她一份）。
#[derive(Clone, Debug)]
pub struct Rift {
    pub c: Pt,
    pub opened: usize,
    pub until: usize,
    /// 上一 tick 碰着边界的敌人。
    pub touching: Vec<usize>,
    pub cross: Option<Cross>,
    /// 这个 tick 以前不再冲。
    pub calm: usize,
    pub crossings: usize,
    pub slowed: usize,
    /// 对面整条直径都在墙里：记过一行了。
    pub blocked: bool,
}

impl Rift {
    pub fn new(c: Pt, now: usize, r_t: usize) -> Rift {
        Rift { c, opened: now, until: now + r_t, touching: Vec::new(), cross: None, calm: now, crossings: 0, slowed: 0,
               blocked: false }
    }
}

fn pt(p: (u64, u64)) -> Pt {
    (p.0 as f64, p.1 as f64)
}

fn spot(p: Pt) -> String {
    format!("({:.0}, {:.0})", p.0, p.1)
}

/// 控住了不冲（等过去）：眩晕、定身、嘲讽、恐惧、魅惑、击飞、禁止位移。
const HELD: [CcKindV1; 7] = [CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm,
                             CcKindV1::Airborne, CcKindV1::BlockMoveSkill];

fn has_cc(sim: &StableSim<'_>, id: usize, kinds: &[CcKindV1]) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.cc_count()).filter_map(|i| e.cc_at(i)).any(|c| kinds.iter().any(|k| k.code() == c.kind)))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// At the border, may she cross now: not held, and no forced move but her own hop (an enemy's knockback or pull carries
/// her on - out, or to a stop on the border, crossing then).
pub fn may_cross(held: bool, forced: bool, own_hop: bool) -> bool {
    !held && (!forced || own_hop)
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

/// 关掉：摘掉给 AI 的标记，记一行。
fn close(sim: &mut StableSim<'_>, me: usize, r: &Rift, why: &str) {
    sim.entity_remove_buff(me, &at_name(AT, r.c));
    if let Some(n) = counted("rift closed", on_screen(sim)) {
        wlog(format!("{} RIFT CLOSED ({why}) after {} of {} ticks: {} crossings, {} border slows #{n}", head(sim, me),
                     sim.tick().saturating_sub(r.opened), r.until - r.opened, r.crossings, r.slowed));
    }
}

/// 她死了（被动的 on_dead）：领域跟着关（死亡清掉 buff，标记不用摘）。
pub fn died(sim: &StableSim<'_>, me: usize, r: &Rift) {
    if let Some(n) = counted("rift closed", on_screen(sim)) {
        wlog(format!("{} RIFT CLOSED (she died) after {} of {} ticks: {} crossings, {} border slows #{n}", head(sim, me),
                     sim.tick().saturating_sub(r.opened), r.until - r.opened, r.crossings, r.slowed));
    }
}

/// 每 tick（被动的 on_update）：读新领域，开着的照规则走。
pub fn update(slot: &mut Option<Rift>, sim: &mut StableSim<'_>, me: usize, p: &Params) {
    let now = sim.tick();
    let (alive, here, team, fresh) = {
        let Some(e) = sim.get_entity(me) else { return };
        let fresh = (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .find_map(|b| parse_at(b.name(), NEW).map(|c| (b.name().to_string(), c)));
        (e.is_alive(), pt(e.pos()), e.team(), fresh)
    };
    if let Some((name, c)) = fresh {
        sim.entity_remove_buff(me, &name);
        if let Some(old) = slot.take() {
            close(sim, me, &old, "a new rift");
        }
        let d = dist(c, here);
        if place(c, here) == Place::Out {
            if let Some(n) = counted("rift open", on_screen(sim)) {
                wlog(format!("{} RIFT NOT OPENED at {}: she is {d:.0} from it, not in it (League: it closes at once) #{n}",
                             head(sim, me), spot(c)));
            }
        } else {
            if let Some(n) = counted("rift open", on_screen(sim)) {
                wlog(format!("{} RIFT OPEN at {} for {} ticks, she is {d:.0} from its centre (crosses at {EDGE:.0}) #{n}",
                             head(sim, me), spot(c), p.r_t));
            }
            *slot = Some(Rift::new(c, now, p.r_t));
        }
    }
    let Some(mut r) = slot.take() else { return };
    if !alive {
        died(sim, me, &r);
        return;
    }
    // ---- her: the crossing under way, or the border
    if let Some(mut cr) = r.cross.take() {
        if !cr.door && now + EXIT_AT >= cr.until {
            sim.play_view_effect(DOOR, me, &InputTargetV1::pos(cr.to.0.round() as u64, cr.to.1.round() as u64), 0, 0, 0);
            cr.door = true;
        }
        if now >= cr.until {
            let off = dist(here, cr.to);
            if off > SNAP {
                sim.entity_set_pos(me, cr.to.0.round() as u64, cr.to.1.round() as u64);
                if let Some(n) = counted("rift snap", on_screen(sim)) {
                    wlog(format!("{} RIFT CROSS ended {off:.0} short of {}: put there #{n}", head(sim, me), spot(cr.to)));
                }
            }
            r.calm = now + GRACE;
        } else {
            // the host did not move her this tick (the forced move refused: cc-immune from elsewhere): a step of her own
            let left = dist(here, cr.to);
            if dist(cr.last, here) < 1.0 && left > 1.0 {
                let s = cr.step.min(left);
                let next = (here.0 + (cr.to.0 - here.0) / left * s, here.1 + (cr.to.1 - here.1) / left * s);
                sim.entity_set_pos(me, next.0.round().max(0.0) as u64, next.1.round().max(0.0) as u64);
                cr.last = next;
            } else {
                cr.last = here;
            }
            r.cross = Some(cr);
        }
    } else {
        match place(r.c, here) {
            Place::Out => {
                close(sim, me, &r, &format!("she is out of it, {:.0} from its centre: a blink, or carried out", dist(r.c, here)));
                return;
            }
            Place::Border if now >= r.calm
                && may_cross(has_cc(sim, me, &HELD), has_cc(sim, me, &[CcKindV1::ForceMove]), has_buff(sim, me, OWN_HOP)) => {
                cross(sim, me, &mut r, here, p)
            }
            _ => {}
        }
    }
    if now >= r.until && r.cross.is_none() {
        close(sim, me, &r, "its time is up");
        return;
    }
    // ---- the enemies on the border: slowed once a crossing
    let mut on_it = Vec::new();
    let mut new = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || u.is_tower() || !u.is_targetable()
            || matches!(u.kind(), Some(EntityKindV1::Tower | EntityKindV1::Nexus)) {
            continue;
        }
        let at = pt(u.pos());
        if touches(r.c, at) {
            on_it.push(u.id());
            if !r.touching.contains(&u.id()) {
                new.push((u.id(), u.is_champion(), dist(r.c, at)));
            }
        }
    }
    for (id, champion, d) in new {
        // League takes the strongest slow, TFM2 adds them up: the border's 50% takes the shockwave's 30% off
        let shock = sim.entity_remove_buff(id, SHOCK_SLOW);
        sim.entity_remove_buff(id, EDGE_SLOW);
        let mut b = BuffV1::timed(EDGE_SLOW, p.r_edge_t);
        b.move_speed_mult = -(p.r_edge as i32);
        sim.add_buff(id, &b);
        r.slowed += 1;
        if champion {
            if let Some(n) = counted("rift edge", on_screen(sim)) {
                wlog(format!("{} RIFT EDGE {} touched the border ({d:.0} from the centre): slowed {}% for {} ticks{} #{n}",
                             head(sim, me), who(sim, id), p.r_edge, p.r_edge_t,
                             if shock > 0 { ", the shockwave's slow taken off" } else { "" }));
            }
        }
    }
    r.touching = on_it;
    // ---- the AI's mark: where the rift is, while it is open
    let mark = at_name(AT, r.c);
    sim.entity_remove_buff(me, &mark);
    sim.add_buff(me, &BuffV1::timed(&mark, 2));
    *slot = Some(r);
}

/// 她碰到了边界：冲到对面。
fn cross(sim: &mut StableSim<'_>, me: usize, r: &mut Rift, here: Pt, p: &Params) {
    let now = sim.tick();
    let far = across(r.c, here);
    let to = match walls_now(sim) {
        Some(g) => landing(g, r.c, far),
        None => Some(far),
    };
    let Some(to) = to else {
        if !r.blocked {
            r.blocked = true;
            if let Some(n) = counted("rift blocked", on_screen(sim)) {
                wlog(format!("{} RIFT CROSS blocked: the far side {} and the way to the centre are walls #{n}",
                             head(sim, me), spot(far)));
            }
        }
        r.calm = now + GRACE;
        return;
    };
    // her own hop carried her into the border (may_cross: no enemy's forced move): that hop ends here
    let moved = has_cc(sim, me, &[CcKindV1::ForceMove]);
    if moved {
        sim.entity_clear_cc(me);
    }
    let ticks = p.r_wrap_t.max(1);
    let d = dist(here, to);
    let mut pose = CcV1::of_kind(CcKindV1::Animation, ticks as u64);
    pose.set_name(POSE);
    sim.apply_cc(me, &pose);
    let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    mv.dx = (to.0 - here.0).round() as i64;
    mv.dy = (to.1 - here.1).round() as i64;
    mv.speed = ((d / ticks as f64).ceil() as u64).max(1);
    sim.apply_cc(me, &mv);
    // after the forced move (cc_immune refuses one): no damage, no crowd control, through walls - League's untargetable
    let mut b = BuffV1::timed(WRAP, ticks + 2);
    b.damaged_reduce = 100;
    b.cc_immune = true;
    b.ignore_wall = true;
    sim.entity_remove_buff(me, WRAP);
    sim.add_buff(me, &b);
    sim.play_view_effect(DOOR, me, &InputTargetV1::pos(here.0.round() as u64, here.1.round() as u64), 0, 0, 0);
    sim.play_sfx(DOOR, me, &InputTargetV1::target(me));
    r.cross = Some(Cross { from: here, to, until: now + ticks, door: false, last: here, step: d / ticks as f64 });
    r.crossings += 1;
    if let Some(n) = counted("rift cross", on_screen(sim)) {
        let moved_by = if moved { ", her own hop cut there" } else { "" };
        let short = if dist(to, far) >= 1.0 { format!(" (moved in from {}: a wall)", spot(far)) } else { String::new() };
        wlog(format!("{} RIFT CROSS #{} of this rift: touched the border {:.0} from the centre at {}, across to {}{short} in {ticks} ticks{moved_by} #{n}",
                     head(sim, me), r.crossings, dist(r.c, here), spot(here), spot(to)));
    }
}

#[cfg(test)]
mod tests {
    use super::super::ID;
    use super::*;

    #[test]
    fn names_carry_the_spot() {
        assert_eq!(at_name(NEW, (123_456.4, 7.6)), "league_aurora_rift_new:123456,8");
        assert_eq!(parse_at("league_aurora_rift_new:123456,8", NEW), Some((123_456.0, 8.0)));
        assert_eq!(parse_at("league_aurora_rift:5,6", AT), Some((5.0, 6.0)));
        // the AI's mark and the native's are told apart
        assert_eq!(parse_at("league_aurora_rift_new:5,6", AT), None);
        assert_eq!(parse_at("league_aurora_rift:5,6", NEW), None);
        assert_eq!(parse_at("league_aurora_rift:x,6", AT), None);
        assert!(at_name(NEW, (959_999.0, 959_999.0)).len() <= BUFF_NAME_CAP);
        for name in [NEW, AT, WRAP, EDGE_SLOW, SHOCK_SLOW, DOOR, OWN_HOP] {
            assert!(name.starts_with(ID), "{name}");
        }
    }

    #[test]
    fn she_crosses_at_the_border_and_leaves_only_past_it() {
        let c = (500_000.0, 500_000.0);
        // she lands r_ahead behind the centre: inside, with room before the border
        assert_eq!(place(c, (474_500.0, 500_000.0)), Place::Inside);
        assert_eq!(place(c, (500_000.0 - EDGE + 1.0, 500_000.0)), Place::Inside);
        assert_eq!(place(c, (500_000.0 - EDGE, 500_000.0)), Place::Border);
        // her fastest own move is 4000 a tick: a hop through the border is caught on it
        assert_eq!(place(c, (500_000.0 - EDGE - 4_000.0, 500_000.0)), Place::Border);
        assert_eq!(place(c, (500_000.0 - EDGE - OUT - 1.0, 500_000.0)), Place::Out);
    }

    #[test]
    fn across_is_the_far_end_of_the_diameter() {
        let c = (500_000.0, 500_000.0);
        let to = across(c, (500_000.0 - EDGE, 500_000.0));
        assert!((to.0 - (500_000.0 + LAND)).abs() < 1e-6 && (to.1 - 500_000.0).abs() < 1e-6);
        let to = across(c, (500_000.0, 500_000.0 + 40_000.0));
        assert!((to.1 - (500_000.0 - LAND)).abs() < 1e-6);
        // landing inside the edge: she does not cross straight back
        assert_eq!(place(c, to), Place::Inside);
        assert!(LAND + 6_000.0 <= EDGE);
        // on the centre itself: somewhere, not NaN
        let to = across(c, c);
        assert!(to.0.is_finite() && to.1.is_finite());
    }

    #[test]
    fn only_her_own_hop_crosses_the_border() {
        assert!(may_cross(false, false, false), "walking into it");
        assert!(may_cross(false, true, true), "her E or veil hop into it");
        assert!(!may_cross(false, true, false), "an enemy's knockback or pull: carried on, no free cleanse");
        assert!(!may_cross(true, false, false) && !may_cross(true, true, true), "stunned, rooted...: wait");
    }

    #[test]
    fn the_kit_marks_her_own_hops() {
        let copy = include_str!("../override/league_aurora.data_champion");
        assert!(copy.contains(&format!("\"{OWN_HOP}\"")), "the add-on's copy marks her hops");
        let main = include_str!("../../../league/champion/league_aurora.data_champion");
        assert!(!main.contains(OWN_HOP), "the main pack has no border to cross");
    }

    #[test]
    fn enemies_touch_the_ring_from_both_sides() {
        let c = (500_000.0, 500_000.0);
        assert!(touches(c, (500_000.0 + RING, 500_000.0)));
        assert!(touches(c, (500_000.0 + RING - BAND, 500_000.0)));
        assert!(touches(c, (500_000.0, 500_000.0 - RING - BAND)));
        assert!(!touches(c, (500_000.0 + RING - BAND - 1.0, 500_000.0)), "inside it: no slow");
        assert!(!touches(c, (500_000.0 + RING + BAND + 1.0, 500_000.0)), "outside it: no slow");
        assert!(!touches(c, c));
    }

    #[test]
    fn the_landing_keeps_out_of_walls() {
        // a 3 x 3 grid of 32000 cells, the right column walls
        let g = Grid::from_rows(&["..#", "..#", "..#"], None);
        let c = (48_000.0, 48_000.0);
        assert_eq!(landing(&g, c, (40_000.0, 48_000.0)), Some((40_000.0, 48_000.0)));
        let q = landing(&g, c, (78_000.0, 48_000.0)).unwrap();
        assert!(q.0 < 64_000.0 && q.0 >= c.0, "stepped back toward the centre out of the wall: {q:?}");
        let walled = Grid::from_rows(&["###", "###", "###"], None);
        assert_eq!(landing(&walled, c, (78_000.0, 48_000.0)), None);
        // off the map counts as a wall
        assert!(g.is_wall(-1.0, 10.0));
    }

    /// 世界坐标的一个矩形：(左上, 右下)。
    type Rect = ((f64, f64), (f64, f64));

    /// 召唤师峡谷那样的墙格子（295 x 296 格，每格 60000/11，从 x = 30000/11 起，作者墙体文件的格子）：中心落在 `rects`
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
    fn on_summoners_rift_the_crossing_lands_clear_of_its_walls() {
        // her rift in the map's far half, the far end of the diameter in one of its walls
        let g = Grid::summoners_rift(Some(&rift_walls(&[((1_325_000.0, 1_190_000.0), (1_345_000.0, 1_210_000.0))])));
        let c = (1_300_000.0, 1_200_000.0);
        let far = across(c, (c.0 - EDGE, c.1));
        assert!(g.is_wall(far.0, far.1), "{far:?}");
        let q = landing(&g, c, far).expect("stepped in from the wall");
        assert!(!g.is_wall(q.0, q.1) && q.0 < far.0 && q.0 >= c.0, "{q:?}");
        // the game's own grid called all of it wall out there: no crossing at all (the old code)
        assert_eq!(landing(&Grid::builtin()[0], c, far), None);
        // with no walls file only the map's edges are walls: straight across
        let open = Grid::summoners_rift(None);
        assert_eq!(landing(&open, c, far), Some(far));
        assert!(!open.is_wall(1_000_000.0, 1_000_000.0) && open.is_wall(1_614_546.0, 800_000.0) && open.is_wall(-1.0, 5.0));
        // a wall of the game's own 5v5 map is none on the Rift
        let native = (15.5 * CELL, 3.5 * CELL);
        assert!(Grid::builtin()[0].is_wall(native.0, native.1) && !g.is_wall(native.0, native.1));
    }

    #[test]
    fn the_ring_is_the_kits() {
        let src = include_str!("../../../tools/kit/build_aurora.py");
        assert!(src.contains(&format!("\"r_zone\": {}", RING as usize)));
        // the kit's own rift numbers this module's geometry was set by
        assert!(src.contains("\"r_ahead\": 25500"));
        assert!(25_500.0 < EDGE && EDGE < RING);
    }
}
