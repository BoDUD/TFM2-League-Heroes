//! 元素峡谷的地形（0.5.0，用户 2026-11-11：「但是我们现在的小龙不能改变地形？… 这些能做吗」，选了云端、海克斯、海洋 /
//! 化学科技、山脉都做，炼狱只做氛围画面，只做游戏自带的 5v5 地图，画面用程序生成的像素图）。
//!
//! 第二条元素亚龙被拿下后峡谷变成第三种元素（`rules::order` 的第三个，龙魂也是它），[`RISE_T`] tick 后地形生效：
//!
//! | 峡谷 | 做了什么 |
//! |---|---|
//! | 云端 | 五条风道（河道、两边野区各两条）：英雄走在里面移速 +20%（[`WIND`]，出来后还剩不到半秒） |
//! | 海克斯 | 四对传送门（每队两对：本方上野区 ↔ 龙坑旁，本方下野区 ↔ 男爵坑旁）：脱战、朝着另一头走的英雄踩上去立刻传过去，每人 20 秒冷却 |
//! | 海洋 | 六片新草丛（站在里面、里面没有敌方英雄、刚才没出手：敌人看不见）；四个蜂蜜果实（受了伤的英雄走过去吃掉回血，45 秒再长）；画面下雨 |
//! | 化学科技 | 六片毒雾草丛（和海洋的草丛一样的规矩，位置不同） |
//! | 山脉 | 六堆碎石（不挡人：英雄走在上面移速 -30%，[`RUBBLE`]，下来后不到 0.2 秒就没了） |
//! | 炼狱 | 只有画面（龙坑、男爵坑周围的墙上着火）：游戏烘好的草丛和墙局内改不了 |
//!
//! 游戏的接口改不了烘好的寻路、草丛和视野，所以都是「模拟出来的」：草丛是 `entity_set_invisible`（敌人丢视野和目标），碎石是
//! 减速 buff，比赛 AI 不知道有它们。位置只有游戏自带的 5v5 地图的（[`is_base_map`]：两个水晶和小龙坑在原来的地方），
//! 别的地图（召唤师峡谷布局、第三方地图）这一局没有地形。全部在模拟里、只按模拟的 tick，预演和画面一样。
//!
//! 山脉 0.5.1（用户 2026-11-12：「这里改了后 AI不会自动然后去 反正看起来像是瞬移」「会卡住人的」）：0.5.0 的岩石挡人——每 tick
//! 把站进石头的英雄推到外面，被同一块顶住 150 tick 就放到对面。AI 的寻路不知道有石头，只会直直撞上去：那一局推了 18147 次、
//! 放过去 82 次（韦鲁斯在同一块上 10 秒里来回 5 次），看上去就是卡住和瞬移。问过之后改成「减速碎石」：谁都能走过去，英雄走在
//! 上面变慢；画面还是那几块升起来的岩石（画在单位下面，英雄从上面走过）。
//!
//! 这里是规则和位置（纯函数、表）；[`Terrain`] 是一份模拟里的地形状态，`lib.rs` 每 tick 调 [`Terrain::step`]。

use mod_api_stable::*;

use super::rules::Element;

// ===================== 游戏自带的 5v5 地图 =====================

/// 一格多大；地图 30 x 30 格。
pub const CELL: u64 = 32_000;
pub const CELLS: usize = 30;
pub const SIZE: u64 = CELL * CELLS as u64;

/// 墙（0.5.1 引擎 `MapDef::moba`，0.7.2 的 league_camille_wall.log：「30 rows x 30 cols, 90 wall cells, same as
/// built-in」）：一行是 y，一列是 x。蓝色方在左下，红色方在右上，沿 x = y（河道）对称。
pub const WALLS: [&str; CELLS] = [
    "..............................",
    "..............................",
    "..............................",
    "...............##.####........",
    "......#...###........#........",
    "...............#.....#........",
    "....#..........#..............",
    "............#.................",
    "............#...##.......##...",
    "............##...#.....#..#...",
    "....#..................#..#...",
    "....#........#.......#........",
    "....#..###..........##........",
    ".........#.#........#..###....",
    ".........................#....",
    "...#.##..................#....",
    "...#....#.........#.#.........",
    "........##..........##........",
    "...#............#.............",
    "...#....................#.....",
    "...#........##..##......#.....",
    "...###.....##....#......#.....",
    "..............................",
    ".........##..#...........#....",
    ".............#.....###........",
    "........#....###.......#......",
    "........###...................",
    "..............................",
    "..............................",
    "..............................",
];

/// 游戏自己的草丛（非 `0` 是草丛；league_nidalee.log：71 格）。
pub const BUSHES: [&str; CELLS] = [
    "111000000000000000022200000000",
    "100000000000000000000000000000",
    "100000000000000000000000000000",
    "000000000000000000000000000000",
    "000000033300000000004000000000",
    "000000000000000000004000000000",
    "000000000000500000000000000000",
    "000060000000000000000000000000",
    "000060000000000000000000000007",
    "000060000000008000000000000007",
    "000000000000000000000000000007",
    "000000000000000000000000009000",
    "000000A00000BB0000000000009000",
    "000000000000B00000000000009000",
    "000000000C00000000000000009000",
    "00000000000000000000DD00000000",
    "00000000000000000E000D00000000",
    "0000000000000000EE000000000000",
    "0000000000000000000000000F0000",
    "G000000000000000000000000F0000",
    "G000HH000000000I000000000F0000",
    "G00000000000000II00000000F0000",
    "0000000000000000000000000F0000",
    "000000000000000000000000000000",
    "00000000000000000000000000000J",
    "000000000000000000KKKKK000000J",
    "00000000000LLLL00000000000000J",
    "000000000000000000000000000000",
    "0000000000000000000000000000MM",
    "00000000NNN0000000000000OOO0MM",
];

/// 两个水晶、小龙坑、纳什男爵坑（0.7.2 的 league_camille_wall.log：`nexus_pos`、`camps` 的 Serpen / Morgard）。
pub const NEXUS: [(u64, u64); 2] = [(96_000, 864_000), (864_000, 96_000)];
pub const SERPEN: (u64, u64) = (672_000, 672_000);
pub const EPIC: (u64, u64) = (288_000, 288_000);
/// 认地图时位置可以差这么多。
const NEAR: u64 = 12_000;

fn cell(grid: &[&str; CELLS], p: (u64, u64)) -> Option<u8> {
    let (c, r) = ((p.0 / CELL) as usize, (p.1 / CELL) as usize);
    (c < CELLS && r < CELLS).then(|| grid[r].as_bytes()[c])
}

/// 这一点在墙里（地图外面也算）。
pub fn wall_at(p: (u64, u64)) -> bool {
    cell(&WALLS, p) != Some(b'.')
}

/// 这一点在游戏自己的草丛里。
pub fn bush_at(p: (u64, u64)) -> bool {
    cell(&BUSHES, p).is_some_and(|c| c != b'0')
}

fn d2(a: (u64, u64), b: (u64, u64)) -> u64 {
    let (dx, dy) = (a.0.abs_diff(b.0), a.1.abs_diff(b.1));
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

/// 这张地图是不是游戏自带的 5v5：两个水晶（哪个在前都行）和小龙坑（看见过小龙才知道）都在原来的地方。
pub fn is_base_map(nexus: &[(u64, u64)], pit: Option<(u64, u64)>) -> bool {
    let near = |a: (u64, u64), b: (u64, u64)| d2(a, b) <= NEAR * NEAR;
    nexus.len() == 2
        && NEXUS.iter().all(|n| nexus.iter().any(|x| near(*x, *n)))
        && pit.is_none_or(|p| near(p, SERPEN))
}

// ===================== 位置 =====================

/// 第二条小龙被拿下后这么多 tick 地形生效（画面上岩石升起、草丛长出来的时间）。
pub const RISE_T: usize = 180;
/// 风道、传送门、草丛、果实、碎石多久看一次。
pub const SCAN: usize = 6;

/// 云端：风道（一段段直线，两边各 [`WIND_HALF`] 宽）。英雄联盟的风道在野区和龙坑；这里是河道一条（男爵坑到龙坑）、
/// 蓝色方野区两条（基地往上野区、基地往龙坑），红色方照镜像。
pub const CURRENTS: [((u64, u64), (u64, u64)); 5] = [
    ((336_000, 336_000), (640_000, 640_000)),
    ((240_000, 432_000), (240_000, 704_000)),
    ((432_000, 240_000), (704_000, 240_000)),
    ((176_000, 720_000), (592_000, 720_000)),
    ((720_000, 176_000), (720_000, 592_000)),
];
pub const WIND_HALF: u64 = 36_000;
/// 风道里的移速（`league_dragons_rift_wind`，每次看到在里面续 [`WIND_T`] tick）。
pub const WIND: &str = "league_dragons_rift_wind";
pub const WIND_MS: i32 = 20;
pub const WIND_T: usize = 24;

pub fn wind_buff() -> BuffV1 {
    let mut b = BuffV1::timed(WIND, WIND_T);
    b.move_speed_mult = WIND_MS;
    b
}

/// 海克斯：成对的传送门（门, 它的另一头）。蓝色方两对：上野区 ↔ 龙坑的西南口，下野区 ↔ 男爵坑的西南口（都离兵线、营地
/// 60000 以上：中路从水晶沿 x + y = 960000 出去，基地门口没有放得下的地方）；红色方照镜像。
pub const GATES: [((u64, u64), (u64, u64)); 4] = [
    ((224_000, 544_000), (576_000, 736_000)),
    ((544_000, 224_000), (736_000, 576_000)),
    ((384_000, 736_000), (240_000, 352_000)),
    ((736_000, 384_000), (352_000, 240_000)),
];
/// 踩到门：离门心这么近。
pub const GATE_R: u64 = 18_000;
/// 传一次后这么久不能再传；多久没挨打、没出手算脱战。
pub const GATE_CD: usize = 1_200;
pub const GATE_CALM: usize = 180;
/// 两次看之间至少走了这么远才算在走。
pub const GATE_MOVE: u64 = 600;

/// 海洋：新草丛（圆，半径 [`BRUSH_R`]）——河道上两片（男爵坑口、龙坑口），两边上野区各一片，两边下野区各一片。
pub const OCEAN_BRUSH: [(u64, u64); 6] =
    [(368_000, 368_000), (592_000, 592_000), (304_000, 528_000), (528_000, 304_000), (432_000, 720_000), (720_000, 432_000)];
/// 化学科技：毒雾草丛——两边上野区各一片，两边下野区各一片，龙坑的北边和西边各一片。
pub const CHEM_BRUSH: [(u64, u64); 6] =
    [(240_000, 560_000), (560_000, 240_000), (400_000, 720_000), (720_000, 400_000), (720_000, 592_000), (592_000, 720_000)];
pub const BRUSH_R: u64 = 38_000;
/// 草丛里每次看到该藏就藏这么多 tick；出手（冷却涨上去）后这么久藏不住。
pub const HIDE_T: usize = 10;
pub const REVEAL_T: usize = 60;

/// 海洋：蜂蜜果实（男爵坑口两个、龙坑口两个）。受了伤的英雄走到 [`FRUIT_R`] 以内吃掉：回 8% 最大生命 + 10% 已损生命；
/// 吃掉后 [`FRUIT_RESPAWN`] tick 再长出来，峡谷变成海洋后 [`FRUIT_FIRST`] tick 第一次长好。
pub const FRUITS: [(u64, u64); 4] = [(336_000, 400_000), (400_000, 336_000), (624_000, 560_000), (560_000, 624_000)];
pub const FRUIT_R: u64 = 16_000;
pub const FRUIT_FIRST: usize = 600;
pub const FRUIT_RESPAWN: usize = 2_700;
/// 生命高于这么多（百分比）的不吃。
pub const FRUIT_HURT: usize = 95;

pub fn fruit_heal(hp: usize, max: usize) -> usize {
    max * 8 / 100 + max.saturating_sub(hp) * 10 / 100
}

/// 山脉：碎石堆（圆，半径 [`ROCK_R`] 加上英雄的身体）——河道上龙坑口一块、男爵坑口一块，龙坑的西南口和东北口各一块，
/// 两边上野区的过道里各一块。每块四面都留着路（离最近的墙 35000 以上：0.5.0 的岩石挡人时要的）。
pub const ROCKS: [(u64, u64); 6] =
    [(608_000, 608_000), (344_000, 344_000), (592_000, 736_000), (736_000, 592_000), (240_000, 640_000), (640_000, 240_000)];
pub const ROCK_R: u64 = 20_000;
/// 英雄的身体算这么大（读不到半径时）。
pub const BODY: u64 = 8_000;
/// 碎石上的移速（`league_dragons_rift_rubble`，每次看到站在上面续 [`RUBBLE_T`] tick：下来后不到 0.2 秒就没了）。
pub const RUBBLE: &str = "league_dragons_rift_rubble";
pub const RUBBLE_MS: i32 = -30;
pub const RUBBLE_T: usize = 12;

pub fn rubble_buff() -> BuffV1 {
    let mut b = BuffV1::timed(RUBBLE, RUBBLE_T);
    b.move_speed_mult = RUBBLE_MS;
    b
}

/// 炼狱：着火的墙（墙格子的中心，英雄走不到那里）——龙坑和男爵坑周围的墙。
pub const EMBERS: [(u64, u64); 16] = [
    // the dragon pit's walls
    (784_000, 624_000), (784_000, 688_000), (624_000, 784_000), (688_000, 784_000), (560_000, 656_000), (656_000, 560_000),
    (560_000, 688_000), (688_000, 560_000),
    // Baron's pit's walls
    (400_000, 240_000), (240_000, 400_000), (400_000, 304_000), (304_000, 400_000), (432_000, 304_000), (304_000, 432_000),
    (432_000, 368_000), (368_000, 432_000),
];

/// 这种峡谷的草丛（没有：空的）。
pub fn brush_of(e: Element) -> &'static [(u64, u64)] {
    match e {
        Element::Ocean => &OCEAN_BRUSH,
        Element::Chemtech => &CHEM_BRUSH,
        _ => &[],
    }
}

// ===================== 几何（整数，哪台机器都一样） =====================

/// 点到线段的距离的平方。
pub fn seg_d2(p: (u64, u64), a: (u64, u64), b: (u64, u64)) -> u64 {
    let (px, py) = (p.0 as i128 - a.0 as i128, p.1 as i128 - a.1 as i128);
    let (bx, by) = (b.0 as i128 - a.0 as i128, b.1 as i128 - a.1 as i128);
    let len2 = bx * bx + by * by;
    if len2 == 0 {
        return d2(p, a);
    }
    let t = (px * bx + py * by).clamp(0, len2);
    // the closest point, scaled by len2
    let (cx, cy) = (px * len2 - bx * t, py * len2 - by * t);
    ((cx * cx + cy * cy) / (len2 * len2)) as u64
}

/// 这一点在风道里。
pub fn in_wind(p: (u64, u64)) -> bool {
    CURRENTS.iter().any(|&(a, b)| seg_d2(p, a, b) <= WIND_HALF * WIND_HALF)
}

/// 这一点踩着哪个门：(它的另一头)。
pub fn gate_at(p: (u64, u64)) -> Option<((u64, u64), (u64, u64))> {
    GATES
        .iter()
        .flat_map(|&(a, b)| [(a, b), (b, a)])
        .find(|&(gate, _)| d2(p, gate) <= GATE_R * GATE_R)
}

/// 从 `from` 走到 `to` 是不是朝着门的另一头走：走了 [`GATE_MOVE`] 以上，方向和「门 -> 另一头」的夹角在 60 度以内。
pub fn heading(from: (u64, u64), to: (u64, u64), gate: (u64, u64), twin: (u64, u64)) -> bool {
    let (mx, my) = (to.0 as i128 - from.0 as i128, to.1 as i128 - from.1 as i128);
    let (gx, gy) = (twin.0 as i128 - gate.0 as i128, twin.1 as i128 - gate.1 as i128);
    let (m2, g2) = (mx * mx + my * my, gx * gx + gy * gy);
    let dot = mx * gx + my * gy;
    // cos >= 0.5  <=>  dot > 0 and 4 dot^2 >= |m|^2 |g|^2
    m2 >= (GATE_MOVE * GATE_MOVE) as i128 && dot > 0 && 4 * dot * dot >= m2 * g2
}

/// 这一点在哪片草丛里（第几片）。
pub fn brush_at(e: Element, p: (u64, u64)) -> Option<usize> {
    brush_of(e).iter().position(|c| d2(p, *c) <= BRUSH_R * BRUSH_R)
}

/// 这一点（身体半径 `body`）踩在哪堆碎石上（第几块）。
pub fn rock_at(p: (u64, u64), body: u64) -> Option<usize> {
    let reach = ROCK_R + body;
    ROCKS.iter().position(|c| d2(p, *c) < reach * reach)
}

// ===================== 一份模拟里的地形 =====================

/// 地形里发生的一件事（`lib.rs` 记日志、给画面放特效）。`seat` 是座位。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Happening {
    /// 一个英雄从门 `from` 传到了 `to`。
    Gate { seat: usize, from: (u64, u64), to: (u64, u64) },
    /// 一个英雄吃了第 `fruit` 个蜂蜜果实，回了 `heal`。
    Fruit { seat: usize, fruit: usize, heal: usize },
    /// 一个英雄第一次（这一次进草丛）藏进了第 `brush` 片草丛。
    Hidden { seat: usize, brush: usize },
    /// 一个英雄踩上了第 `rock` 堆碎石（这一次踩上去；在上面移速 [`RUBBLE_MS`]%）。
    Rubble { seat: usize, rock: usize },
}

/// 一个座位在地形里记着的（跟着这条命：换了实体就重来）。
#[derive(Clone, Copy, Debug, Default)]
struct Walker {
    ent: Option<usize>,
    /// 上一次看的位置、生命加护盾、四个冷却。
    at: Option<(u64, u64)>,
    hp: usize,
    cds: Option<[usize; 4]>,
    /// 最后一次挨打、出手的 tick（没有过：0）。
    hurt_at: usize,
    acted_at: usize,
    /// 传送门的冷却到哪个 tick。
    gate_until: usize,
    /// 本包把他藏到哪个 tick；这一次进草丛说过没有。
    hid_until: usize,
    hid_told: bool,
    /// 上一次看的时候站在哪堆碎石上。
    on_rock: Option<usize>,
}

/// 一份模拟里的地形：哪种峡谷、从哪个 tick 起，每个座位的状态，每个果实什么时候长好；`END` 用的计数。
#[derive(Clone, Debug, Default)]
pub struct Terrain {
    pub rift: Option<(Element, usize)>,
    walkers: Vec<Walker>,
    fruits: [usize; FRUITS.len()],
    pub jumps: usize,
    pub eaten: usize,
    pub healed: usize,
    pub hides: usize,
    /// 踩上碎石几次、碎石减速续了几次。
    pub rubble: usize,
    pub slowed: usize,
    pub winds: usize,
}

impl Terrain {
    /// 峡谷变成 `element`（在 tick `now`）。
    pub fn start(&mut self, element: Element, now: usize) {
        self.rift = Some((element, now));
        self.fruits = [now + FRUIT_FIRST; FRUITS.len()];
    }

    /// 地形生效了没有（变形后 [`RISE_T`] tick）。
    pub fn live(&self, now: usize) -> Option<Element> {
        self.rift.filter(|r| now >= r.1 + RISE_T).map(|r| r.0)
    }

    /// 第 `i` 个果实在 `now` 长好了没有。
    pub fn ripe(&self, i: usize, now: usize) -> bool {
        matches!(self.rift, Some((Element::Ocean, _))) && now >= self.fruits[i]
    }

    /// 每 tick：`seats` 是每个座位的 (玩家, 队伍)。发生的事放进 `out`。
    pub fn step(&mut self, sim: &mut StableSim<'_>, now: usize, seats: &[(usize, usize)], out: &mut Vec<Happening>) {
        let Some(element) = self.live(now) else { return };
        if self.walkers.len() != seats.len() {
            self.walkers = vec![Walker::default(); seats.len()];
        }
        if now % SCAN != 0 || element == Element::Infernal {
            return;
        }
        // every champion as it stands now: (entity, where, health + shield, max health)
        let mut here: Vec<Option<(usize, (u64, u64), usize, usize)>> = Vec::with_capacity(seats.len());
        for (i, &(player, _)) in seats.iter().enumerate() {
            let now_at = living(sim, player).and_then(|ent| {
                sim.get_entity(ent).map(|e| {
                    let (hp, max) = e.hp();
                    (ent, e.pos(), hp + e.shield(), hp, max)
                })
            });
            let w = &mut self.walkers[i];
            let Some((ent, at, total, hp, max)) = now_at else {
                here.push(None);
                w.ent = None;
                w.at = None;
                w.on_rock = None;
                continue;
            };
            if w.ent != Some(ent) {
                // a new life: nothing of the last one, but the gates' cooldown stays his
                *w = Walker { ent: Some(ent), gate_until: w.gate_until, hp: total, ..Walker::default() };
            }
            if total < w.hp {
                w.hurt_at = now;
            }
            w.hp = total;
            let cds = sim.get_player(player).and_then(|p| p.cooldowns()).map(|c| [c.0, c.1, c.2, c.3]);
            if let (Some(c), Some(prev)) = (cds, w.cds) {
                if (0..4).any(|k| c[k] > prev[k]) {
                    w.acted_at = now;
                }
            }
            w.cds = cds;
            here.push(Some((ent, at, hp, max)));
        }
        match element {
            Element::Cloud => self.wind(sim, &here),
            Element::Hextech => self.gates(sim, now, &here, out),
            Element::Ocean => {
                self.brush(sim, now, element, seats, &here, out);
                self.fruit(sim, now, &here, out);
            }
            Element::Chemtech => self.brush(sim, now, element, seats, &here, out),
            Element::Mountain => self.rubble(sim, &here, out),
            _ => {}
        }
        for (i, h) in here.iter().enumerate() {
            // where he stands after this scan (a gate moved him: from there)
            self.walkers[i].at = h.map(|h| sim.get_entity(h.0).map_or(h.1, |e| e.pos()));
        }
    }

    fn wind(&mut self, sim: &mut StableSim<'_>, here: &[Option<(usize, (u64, u64), usize, usize)>]) {
        for h in here.iter().flatten() {
            if in_wind(h.1) {
                if sim.entity_stack_buff(h.0, &wind_buff(), 1, true) == 0 {
                    sim.entity_remove_buff(h.0, WIND);
                    sim.add_buff(h.0, &wind_buff());
                }
                self.winds += 1;
            }
        }
    }

    fn gates(&mut self, sim: &mut StableSim<'_>, now: usize, here: &[Option<(usize, (u64, u64), usize, usize)>],
             out: &mut Vec<Happening>) {
        for (i, h) in here.iter().enumerate() {
            let Some((ent, at, _, _)) = *h else { continue };
            let w = self.walkers[i];
            let calm = |t: usize| t == 0 || now >= t + GATE_CALM;
            let (Some(prev), Some((gate, twin))) = (w.at, gate_at(at)) else { continue };
            if now < w.gate_until || !calm(w.hurt_at) || !calm(w.acted_at) || !heading(prev, at, gate, twin) {
                continue;
            }
            if sim.entity_set_pos(ent, twin.0, twin.1) {
                self.walkers[i].gate_until = now + GATE_CD;
                self.jumps += 1;
                out.push(Happening::Gate { seat: i, from: gate, to: twin });
            }
        }
    }

    fn brush(&mut self, sim: &mut StableSim<'_>, now: usize, element: Element, seats: &[(usize, usize)],
             here: &[Option<(usize, (u64, u64), usize, usize)>], out: &mut Vec<Happening>) {
        let patch: Vec<Option<usize>> = here.iter().map(|h| h.and_then(|h| brush_at(element, h.1))).collect();
        for (i, h) in here.iter().enumerate() {
            let Some((ent, _, _, _)) = *h else { continue };
            let w = self.walkers[i];
            let team = seats[i].1;
            let hidden = patch[i].is_some_and(|b| {
                // nobody of the other team in the same patch, and he has not just attacked or cast
                !(0..seats.len()).any(|j| seats[j].1 != team && patch[j] == Some(b))
                    && (w.acted_at == 0 || now >= w.acted_at + REVEAL_T)
            });
            if !hidden {
                self.walkers[i].hid_told = false;
                continue;
            }
            // only one the enemy can see now, or one this mod is hiding already: someone else's stealth is left alone
            if now <= w.hid_until || sim.is_visible(1 - team.min(1), ent) {
                if sim.entity_set_invisible(ent, HIDE_T) {
                    self.walkers[i].hid_until = now + HIDE_T;
                    if !w.hid_told {
                        self.walkers[i].hid_told = true;
                        self.hides += 1;
                        out.push(Happening::Hidden { seat: i, brush: patch[i].unwrap_or(0) });
                    }
                }
            }
        }
    }

    fn fruit(&mut self, sim: &mut StableSim<'_>, now: usize, here: &[Option<(usize, (u64, u64), usize, usize)>],
             out: &mut Vec<Happening>) {
        for (f, at) in FRUITS.iter().enumerate() {
            if now < self.fruits[f] {
                continue;
            }
            // the first seat near it that is hurt
            let eater = here.iter().enumerate().find_map(|(i, h)| {
                h.filter(|h| d2(h.1, *at) <= FRUIT_R * FRUIT_R && h.3 > 0 && h.2 * 100 < h.3 * FRUIT_HURT).map(|h| (i, h))
            });
            if let Some((i, (ent, _, hp, max))) = eater {
                let heal = fruit_heal(hp, max);
                sim.heal(ent, ent, heal);
                self.fruits[f] = now + FRUIT_RESPAWN;
                self.eaten += 1;
                self.healed += heal;
                out.push(Happening::Fruit { seat: i, fruit: f, heal });
            }
        }
    }

    fn rubble(&mut self, sim: &mut StableSim<'_>, here: &[Option<(usize, (u64, u64), usize, usize)>],
              out: &mut Vec<Happening>) {
        for (i, h) in here.iter().enumerate() {
            let Some((ent, at, _, _)) = *h else { continue };
            let body = sim.get_entity(ent).map_or(0, |e| e.radius() as u64);
            let body = if body == 0 { BODY } else { body.min(2 * BODY) };
            let Some(rock) = rock_at(at, body) else {
                self.walkers[i].on_rock = None;
                continue;
            };
            if sim.entity_stack_buff(ent, &rubble_buff(), 1, true) == 0 {
                sim.entity_remove_buff(ent, RUBBLE);
                sim.add_buff(ent, &rubble_buff());
            }
            self.slowed += 1;
            if self.walkers[i].on_rock != Some(rock) {
                self.walkers[i].on_rock = Some(rock);
                self.rubble += 1;
                out.push(Happening::Rubble { seat: i, rock });
            }
        }
    }
}

/// 这个玩家活着的英雄。
fn living(sim: &StableSim<'_>, player: usize) -> Option<usize> {
    let e = sim.get_player(player)?.champion()?;
    e.is_alive().then(|| e.id())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn mirror(p: (u64, u64)) -> (u64, u64) {
        (p.1, p.0)
    }

    /// Open ground a champion can stand on: no wall there nor within `clear` of it on the four sides.
    fn open(p: (u64, u64), clear: u64) -> bool {
        [(0i64, 0i64), (1, 0), (-1, 0), (0, 1), (0, -1)].iter().all(|(dx, dy)| {
            let x = p.0 as i64 + dx * clear as i64;
            let y = p.1 as i64 + dy * clear as i64;
            x >= 0 && y >= 0 && !wall_at((x as u64, y as u64))
        })
    }

    #[test]
    fn the_map_is_the_games_own() {
        assert_eq!(WALLS.iter().map(|r| r.bytes().filter(|c| *c == b'#').count()).sum::<usize>(), 90);
        assert_eq!(BUSHES.iter().map(|r| r.bytes().filter(|c| *c != b'0').count()).sum::<usize>(), 71);
        for r in 0..CELLS {
            assert_eq!((WALLS[r].len(), BUSHES[r].len()), (CELLS, CELLS));
            for c in 0..CELLS {
                assert_eq!(WALLS[r].as_bytes()[c], WALLS[c].as_bytes()[r], "walls mirror over the river at ({c}, {r})");
                assert_eq!(BUSHES[r].as_bytes()[c] != b'0', BUSHES[c].as_bytes()[r] != b'0', "bushes at ({c}, {r})");
            }
        }
        assert!(wall_at((12 * CELL + 5, 7 * CELL + 5)) && !wall_at((0, 0)) && wall_at((SIZE, 5)) && wall_at((5, SIZE + 9)));
        assert!(bush_at((5, 5)) && !bush_at((5 * CELL, 5 * CELL)));
        // the nexuses, the pits: where the game puts them, off the walls
        assert_eq!(mirror(NEXUS[0]), NEXUS[1]);
        assert!(!wall_at(SERPEN) && !wall_at(EPIC) && SERPEN.0 == SERPEN.1 && EPIC.0 == EPIC.1);
    }

    #[test]
    fn only_the_games_own_5v5_map_gets_terrain() {
        assert!(is_base_map(&NEXUS, Some(SERPEN)));
        assert!(is_base_map(&[NEXUS[1], NEXUS[0]], Some((SERPEN.0 + 4_000, SERPEN.1 - 3_000))));
        assert!(is_base_map(&NEXUS, None), "before a serpent was seen (a state rebuilt): the nexuses alone");
        // the pack's Summoner's Rift layout moves the dragon pit; a third-party map has its nexuses elsewhere
        assert!(!is_base_map(&NEXUS, Some((656_000, 656_000))));
        assert!(!is_base_map(&[(120_000, 1_500_000), (1_500_000, 120_000)], Some(SERPEN)));
        assert!(!is_base_map(&[NEXUS[0]], Some(SERPEN)) && !is_base_map(&[], None));
        // the tests' own little world (mock.rs) is no 5v5 map: nothing of this in the other tests
        assert!(!is_base_map(&[(0, 0), (0, 0)], Some((700_000, 300_000))));
    }

    #[test]
    fn every_place_is_on_open_ground_and_the_same_for_both_teams() {
        // currents: each has its mirror (the river's is itself), every point of them off the walls
        for (a, b) in CURRENTS {
            assert!(CURRENTS.iter().any(|c| *c == (mirror(a), mirror(b)) || *c == (mirror(b), mirror(a))), "{a:?}-{b:?}");
            for k in 0..=64u64 {
                let p = ((a.0 * (64 - k) + b.0 * k) / 64, (a.1 * (64 - k) + b.1 * k) / 64);
                assert!(open(p, 12_000), "the current {a:?}-{b:?} crosses a wall at {p:?}");
                assert!(in_wind(p));
            }
        }
        assert!(!in_wind((48_000, 500_000)) && !in_wind((480_000, 912_000)), "the lanes have no wind");
        // gates: mirrored pairs, each gate clear of the walls, a good way from its twin; one of each pair by a pit
        for (a, b) in GATES {
            assert!(GATES.contains(&(mirror(a), mirror(b))), "{a:?}");
            for g in [a, b] {
                assert!(open(g, GATE_R + 6_000), "the gate at {g:?} is against a wall");
                assert_eq!(gate_at(g).map(|t| t.1), Some(if g == a { b } else { a }));
            }
            assert!(d2(a, b) >= 250_000 * 250_000);
            assert!([SERPEN, EPIC].iter().any(|pit| d2(b, *pit) <= 120_000 * 120_000), "{b:?} is by no pit");
        }
        // brush and rocks: mirrored, their centres open; fruits: mirrored, reachable
        for list in [&OCEAN_BRUSH[..], &CHEM_BRUSH[..], &ROCKS[..], &FRUITS[..]] {
            for p in list {
                assert!(list.contains(&mirror(*p)), "{p:?} has no mirror");
                assert!(open(*p, 8_000), "{p:?} is in a wall");
            }
        }
        for p in OCEAN_BRUSH.iter().chain(&CHEM_BRUSH) {
            assert!(!bush_at(*p), "{p:?} is a bush of the game's already");
        }
        // a rock leaves a way round it: at least two of its four sides are open a body's width beyond it
        for r in ROCKS {
            let ways = [(1i64, 0i64), (-1, 0), (0, 1), (0, -1)].iter().filter(|(dx, dy)| {
                let reach = (ROCK_R + 2 * BODY + 4_000) as i64;
                !wall_at(((r.0 as i64 + dx * reach) as u64, (r.1 as i64 + dy * reach) as u64))
            }).count();
            assert!(ways >= 2, "the rock at {r:?} plugs its corridor");
        }
        // nothing on a lane (48000 off the map's left / top edge, 912000 along the bottom / right, x + y = 960000),
        // on a camp, a nexus or a pit
        let camps = [(496_000u64, 752_000u64), (176_000, 592_000), (256_000, 448_000), (351_000, 800_000)];
        let towers = [(48_000u64, 272_000u64), (368_000, 592_000), (688_000, 912_000), (111_000, 784_000), (176_000, 848_000),
                      (48_000, 528_000)];
        let all: Vec<(u64, u64)> = GATES.iter().flat_map(|g| [g.0, g.1]).chain(OCEAN_BRUSH).chain(CHEM_BRUSH).chain(ROCKS)
            .chain(FRUITS).collect();
        for p in &all {
            assert!(p.0.min(p.1) > 120_000 && p.0.max(p.1) < 840_000, "{p:?} on a side lane");
            assert!((p.0 + p.1).abs_diff(SIZE) > 70_000, "{p:?} on the mid lane");
            for c in camps.iter().chain(&towers).flat_map(|c| [*c, mirror(*c)]).chain([SERPEN, EPIC]).chain(NEXUS) {
                assert!(d2(*p, c) >= 60_000 * 60_000, "{p:?} is on top of {c:?}");
            }
        }
        // the burning walls are walls (nobody stands in the flames), mirrored
        for e in EMBERS {
            assert!(wall_at(e) && EMBERS.contains(&mirror(e)), "{e:?}");
        }
    }

    #[test]
    fn the_distance_to_a_current_is_whole_numbers() {
        let (a, b) = ((100_000, 100_000), (200_000, 100_000));
        assert_eq!(seg_d2((150_000, 130_000), a, b), 30_000 * 30_000);
        assert_eq!(seg_d2((60_000, 100_000), a, b), 40_000 * 40_000, "before its start");
        assert_eq!(seg_d2((230_000, 140_000), a, b), 30_000 * 30_000 + 40_000 * 40_000, "past its end");
        assert_eq!(seg_d2((7, 9), a, a), d2((7, 9), a));
        // the river's diagonal: 36000 off it is in, a little more is out
        let mid = (488_000u64, 488_000u64);
        assert!(in_wind((mid.0 + 25_000, mid.1 - 25_000)) && !in_wind((mid.0 + 27_000, mid.1 - 27_000)));
    }

    #[test]
    fn a_gate_takes_one_who_walks_toward_its_twin() {
        let (gate, twin) = GATES[0];
        // the twin lies east-south-east of the gate (352000, 192000): walking east over it goes there
        assert!(heading((gate.0 - 3_000, gate.1), gate, gate, twin));
        assert!(heading((gate.0 - 2_500, gate.1 - 1_500), gate, gate, twin));
        // standing on it, shuffling a little, walking away from the twin: not taken
        assert!(!heading(gate, gate, gate, twin));
        assert!(!heading((gate.0 - 300, gate.1), gate, gate, twin));
        assert!(!heading((gate.0 + 3_000, gate.1), gate, gate, twin));
        // up or down the jungle's corridor (north / south) is more than 60 degrees off: not taken
        assert!(!heading((gate.0, gate.1 + 3_000), gate, gate, twin));
        assert!(!heading((gate.0, gate.1 - 3_000), gate, gate, twin));
        // the same back from the twin
        assert!(heading((twin.0 + 3_000, twin.1), twin, twin, gate));
        assert_eq!(gate_at((twin.0 + 10_000, twin.1 - 10_000)), Some((twin, gate)));
        assert_eq!(gate_at((twin.0 + 20_000, twin.1)), None);
    }

    #[test]
    fn the_rubble_is_where_the_rocks_are() {
        let reach = ROCK_R + BODY;
        for (k, r) in ROCKS.iter().enumerate() {
            assert_eq!(rock_at(*r, BODY), Some(k));
            assert_eq!(rock_at((r.0 + reach - 100, r.1), BODY), Some(k), "rock {k}: its edge, a body's width out");
            assert_eq!(rock_at((r.0, r.1 - reach - 100), BODY), None, "rock {k}: beyond it");
            // a bigger body reaches it from farther
            assert_eq!(rock_at((r.0 + reach + 2_000, r.1), BODY + 4_000), Some(k));
        }
        // slower on it, for a moment longer than two looks
        let b = rubble_buff();
        assert_eq!((b.move_speed_mult, b.duration_tick), (RUBBLE_MS, RUBBLE_T));
        assert!(RUBBLE_MS < 0 && RUBBLE_T == 2 * SCAN);
    }

    #[test]
    fn the_fruit_heals_the_hurt() {
        assert_eq!(fruit_heal(400, 1000), 80 + 60);
        assert_eq!(fruit_heal(1000, 1000), 80);
        let mut t = Terrain::default();
        assert_eq!(t.live(999_999), None);
        t.start(Element::Ocean, 1_000);
        assert_eq!(t.live(1_000 + RISE_T - 1), None);
        assert_eq!(t.live(1_000 + RISE_T), Some(Element::Ocean));
        assert!(!t.ripe(0, 1_000 + FRUIT_FIRST - 1) && t.ripe(3, 1_000 + FRUIT_FIRST));
        t.start(Element::Cloud, 1_000);
        assert!(!t.ripe(0, 99_999), "only the Ocean rift grows them");
    }
}
