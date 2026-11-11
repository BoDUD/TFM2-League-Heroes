//! 本包自己画在战场上的特效（0.4.0，用户 2026-11-11：「龙魂确定生效了吗」——日志里那一局炼狱龙魂炸了 90 次，屏幕上
//! 什么都看不出来；「拿了龙魂没有特效的 都要补 还有远古龙斩杀特效的」）：
//!
//! | 什么时候 | 画什么（`effects/league_dragons_fx#sheet.png` 里的动画） |
//! |---|---|
//! | 炼狱龙魂爆炸 | 被炸的人脚下一团火、一圈火环、飘起的火星（`infernal_blast`） |
//! | 山脉龙魂上盾 | 碎石从地上升起、合成一层琥珀色的壳（`mountain_shield`） |
//! | 海洋龙魂回血 | 一圈水收到脚下、涌起、水珠往上飘（`ocean_heal`） |
//! | 云端龙魂放大招后的加速 | 一阵风卷、几道速度线（`cloud_gust`） |
//! | 海克斯龙魂的连锁闪电 | 从放的人到每个被打的人一道闪电（一格一格画的折线），落点一团电光（`hex_spark`） |
//! | 化学科技龙魂残血 | 毒液窜起、冒泡（`chem_rage`） |
//! | 拿到龙魂 | 那一队每个活着的英雄脚下一圈元素、一根元素的光柱（`soul_<元素>`） |
//! | 远古龙之力点燃 | 一小团远古的火（`elder_burn`；已经烧着的人再被打到不再放） |
//! | 远古龙之力斩杀 | 一道远古的火柱从天上砸下来、地上炸开、一圈冲击波（`elder_execute`） |
//! | 走进海克斯传送门（0.5.0） | 两头的门各一道海克斯的光柱（`gate_flash`） |
//! | 吃掉蜂蜜果实（0.5.0） | 果实的光炸成水珠、一圈水（`fruit_eat`） |
//!
//! 元素峡谷的地形（0.5.0，[`super::rift`] 的位置）也在这里画（[`terrain`]）：云端的风道（一格格接起来的流动的风）、
//! 海克斯的门、海洋的草丛 / 蜂蜜果实 / 雨、化学科技的毒雾、山脉的岩石（从地里升起来）、炼狱着火的墙。
//!
//! 图是 tools/art/dragons_soul_fx.py 一格一格画的像素图（1 格 = 1 个游戏像素）：能画贴图时整帧一条贴图命令；不能时
//! （[`super::world::plan`]）按编进 DLL 的同一份图（`fx_runs.bin`：每帧拆成一条条同色的横条）一条一条画，不靠任何文件。比赛钩子在屏幕放的那场模拟里记下
//! 「哪个 tick、在哪、什么特效」（[`super::feed::fx`]，模拟不读它），客户端扩展按屏幕时钟画（[`draw`]）：特效不跟着英雄走，
//! 留在发生的地方（半秒左右）。画法在 [`super::world`]。

use std::collections::BTreeMap;
use std::sync::{Mutex, OnceLock};

use mod_api_stable::*;

use super::fx_atlas::{Anim, ANIMS};
use super::rules::{mix, Element, DRAKES};
use super::{counted, feed, rift, wlog, world};

/// 一种特效。
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Kind {
    InfernalBlast,
    /// 海克斯龙魂的连锁闪电：`at` 是放的人，`to` 是依次打到的人。
    HexBolt,
    MountainShield,
    OceanHeal,
    CloudGust,
    ChemRage,
    ElderBurn,
    Execute,
    /// 拿到龙魂（每个英雄一份）。
    Soul(Element),
    /// 一个英雄走进海克斯传送门：`at` 是进的那扇，`to` 是出来的那扇（两头各放一次）。
    Gate,
    /// 第几个蜂蜜果实被吃掉了（画面也按它算果实什么时候再长出来）。
    Fruit(u8),
}

impl Kind {
    /// 图上那段动画的名字（闪电：落点的电光）。
    pub fn anim_name(self) -> &'static str {
        match self {
            Kind::InfernalBlast => "infernal_blast",
            Kind::HexBolt => "hex_spark",
            Kind::MountainShield => "mountain_shield",
            Kind::OceanHeal => "ocean_heal",
            Kind::CloudGust => "cloud_gust",
            Kind::ChemRage => "chem_rage",
            Kind::ElderBurn => "elder_burn",
            Kind::Execute => "elder_execute",
            Kind::Soul(Element::Infernal) => "soul_infernal",
            Kind::Soul(Element::Mountain) => "soul_mountain",
            Kind::Soul(Element::Ocean) => "soul_ocean",
            Kind::Soul(Element::Cloud) => "soul_cloud",
            Kind::Soul(Element::Hextech) => "soul_hextech",
            // the Elder has no soul; were it ever asked for, Chemtech's
            Kind::Soul(Element::Chemtech) | Kind::Soul(Element::Elder) => "soul_chemtech",
            Kind::Gate => "gate_flash",
            Kind::Fruit(_) => "fruit_eat",
        }
    }

    pub fn anim(self) -> Option<&'static Anim> {
        let name = self.anim_name();
        ANIMS.iter().find(|a| a.name == name)
    }

    /// 一共放多少 tick。
    pub fn ticks(self) -> usize {
        let anim = self.anim().map_or(0, |a| a.frames as usize * a.ticks as usize);
        if self == Kind::HexBolt { anim.max(BOLT_T) } else { anim }
    }
}

/// 屏幕那一场的一次特效：发生在模拟的哪个 tick、在哪（模拟的坐标）。
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Fx {
    pub m: u64,
    pub s: u64,
    pub tick: usize,
    pub kind: Kind,
    pub at: (u64, u64),
    pub to: Vec<(u64, u64)>,
}

/// 每一种特效（龙魂按元素各一种；果实只列一个）。
pub fn kinds() -> Vec<Kind> {
    let mut v = vec![Kind::InfernalBlast, Kind::HexBolt, Kind::MountainShield, Kind::OceanHeal, Kind::CloudGust,
                     Kind::ChemRage, Kind::ElderBurn, Kind::Execute, Kind::Gate, Kind::Fruit(0)];
    v.extend(DRAKES.iter().map(|&e| Kind::Soul(e)));
    v
}

/// 最长的一种放多少 tick（[`super::feed::fx_live`] 往回找这么远）。
pub fn longest() -> usize {
    static LONGEST: OnceLock<usize> = OnceLock::new();
    *LONGEST.get_or_init(|| kinds().iter().map(|k| k.ticks()).max().unwrap_or(0))
}

/// 开始 `age` tick 后是第几帧（放完了：None）。
pub fn frame_at(a: &Anim, age: usize) -> Option<usize> {
    let f = age / (a.ticks.max(1) as usize);
    (f < a.frames as usize).then_some(f)
}

// ===================== 同一份图，拆成横条 =====================

/// tools/art/dragons_soul_fx.py 写的：`DFXR`、颜色数、颜色（RGBA）、动画数，每段动画的帧数，每帧的横条数和横条
/// （x、y、宽、颜色，各一个字节，从这一帧的左上角算）。
static RUNS_BIN: &[u8] = include_bytes!("fx_runs.bin");

/// 每段动画（[`ANIMS`] 的顺序）每一帧的横条和颜色表（`0xRRGGBBAA`）。
pub struct Runs {
    pub colours: Vec<u32>,
    pub frames: Vec<Vec<Vec<[u8; 4]>>>,
}

/// 读那份数据（对不上：None，那就只画得了贴图）。
pub fn parse_runs(b: &[u8]) -> Option<Runs> {
    let u16_at = |at: usize| b.get(at..at + 2).map(|v| u16::from_le_bytes([v[0], v[1]]) as usize);
    if b.get(..4)? != b"DFXR" {
        return None;
    }
    let n = u16_at(4)?;
    let mut at = 6;
    let mut colours = Vec::with_capacity(n);
    for _ in 0..n {
        let c = b.get(at..at + 4)?;
        colours.push(u32::from_be_bytes([c[0], c[1], c[2], c[3]]));
        at += 4;
    }
    let anims = u16_at(at)?;
    at += 2;
    let mut frames = Vec::with_capacity(anims);
    for _ in 0..anims {
        let k = *b.get(at)? as usize;
        at += 1;
        let mut of_anim = Vec::with_capacity(k);
        for _ in 0..k {
            let runs = u16_at(at)?;
            at += 2;
            let body = b.get(at..at + 4 * runs)?;
            at += 4 * runs;
            let list: Vec<[u8; 4]> = body.chunks_exact(4).map(|r| [r[0], r[1], r[2], r[3]]).collect();
            if list.iter().any(|r| r[3] as usize >= n || r[2] == 0) {
                return None;
            }
            of_anim.push(list);
        }
        frames.push(of_anim);
    }
    (at == b.len()).then_some(Runs { colours, frames })
}

pub fn runs() -> Option<&'static Runs> {
    static RUNS: OnceLock<Option<Runs>> = OnceLock::new();
    RUNS.get_or_init(|| parse_runs(RUNS_BIN)).as_ref()
}

/// 一帧动画画在 `at`：贴图画得了就一条贴图命令，不然一条条横条。
fn frame(ctx: &mut StableClient<'_>, v: &world::View, a: &'static Anim, fr: usize, at: (u64, u64)) -> bool {
    if world::sprite(ctx, v, a, fr, at) {
        return true;
    }
    let Some(list) = ANIMS.iter().position(|x| x.name == a.name)
        .and_then(|i| runs().and_then(|r| r.frames.get(i).and_then(|f| f.get(fr)).map(|l| (l, &r.colours))))
    else {
        return false;
    };
    let (bx, by) = (world::whole_px(at.0) - a.ax as i32, world::whole_px(at.1) - a.ay as i32);
    let mut drawn = false;
    for r in list.0 {
        drawn |= world::run(ctx, v, bx + r[0] as i32, by + r[1] as i32, r[2] as i32, list.1[r[3] as usize]);
    }
    drawn
}

// ===================== 海克斯的闪电 =====================

/// 闪电亮多少 tick；前这么多 tick 是整道（描边、蓝边、白芯），之后只剩芯；每这么多 tick 换一次形状。
pub const BOLT_T: usize = 14;
const BOLT_FULL: usize = 9;
const BOLT_SHAPE: usize = 3;
/// 闪电两头离脚底多高（世界像素，英雄的胸口）。
const CHEST: i32 = 14;
/// 描边、蓝边、白芯（tools/art/dragon_fx.py 的海克斯色）。
const BOLT_COLOURS: [u32; 3] = [0x16_14_4e_ff, 0x4c_90_ff_ff, 0xda_f6_ff_ff];

/// -1 .. 1，`salt` 定。
fn jitter(salt: u64) -> f32 {
    (mix(salt) % 2001) as f32 / 1000.0 - 1.0
}

/// 从 `a` 到 `b`（世界像素）的一道折线：每 9 像素左右一折（3 到 9 折），每个折点往旁边甩，中间甩得最远。
pub fn bolt_path(a: (i32, i32), b: (i32, i32), salt: u64) -> Vec<(i32, i32)> {
    let (dx, dy) = ((b.0 - a.0) as f32, (b.1 - a.1) as f32);
    let len = dx.hypot(dy);
    if len < 1.0 {
        return vec![a, b];
    }
    let segs = ((len / 9.0) as usize).clamp(3, 9);
    let amp = (len * 0.12).clamp(3.0, 7.0);
    let (nx, ny) = (-dy / len, dx / len);
    let mut pts = vec![a];
    for i in 1..segs {
        let t = i as f32 / segs as f32;
        let o = jitter(salt.wrapping_add(i as u64 * 0x9e37)) * amp * (1.0 - (2.0 * t - 1.0).abs() * 0.4);
        pts.push(((a.0 as f32 + dx * t + nx * o).round() as i32, (a.1 as f32 + dy * t + ny * o).round() as i32));
    }
    pts.push(b);
    pts
}

/// 折线经过的每个像素（Bresenham）。
fn pixels(pts: &[(i32, i32)]) -> Vec<(i32, i32)> {
    let mut out = Vec::new();
    for w in pts.windows(2) {
        let ((mut x, mut y), (x1, y1)) = (w[0], w[1]);
        let (dx, dy) = ((x1 - x).abs(), -(y1 - y).abs());
        let (sx, sy) = (if x < x1 { 1 } else { -1 }, if y < y1 { 1 } else { -1 });
        let mut err = dx + dy;
        loop {
            out.push((x, y));
            if x == x1 && y == y1 {
                break;
            }
            let e2 = 2 * err;
            if e2 >= dy {
                err += dy;
                x += sx;
            }
            if e2 <= dx {
                err += dx;
                y += sy;
            }
        }
    }
    out
}

/// 一道闪电画成的横条：(x, y, 宽, 哪一层：0 描边、1 蓝边、2 白芯)，从上到下、从左到右。`full` false 只有芯。
pub fn bolt_runs(pts: &[(i32, i32)], full: bool) -> Vec<(i32, i32, i32, u8)> {
    let core = pixels(pts);
    let mut grid: BTreeMap<(i32, i32), u8> = BTreeMap::new();
    let mut put = |x: i32, y: i32, layer: u8| {
        let e = grid.entry((y, x)).or_insert(layer);
        *e = (*e).max(layer);
    };
    for &(x, y) in &core {
        if full {
            for (ox, oy) in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)] {
                put(x + ox, y + oy, 0);
            }
            for (ox, oy) in [(-1, 0), (1, 0), (0, -1), (0, 1)] {
                put(x + ox, y + oy, 1);
            }
        }
        put(x, y, 2);
    }
    let mut runs: Vec<(i32, i32, i32, u8)> = Vec::new();
    for (&(y, x), &layer) in &grid {
        match runs.last_mut() {
            Some(r) if r.1 == y && r.0 + r.2 == x && r.3 == layer => r.2 += 1,
            _ => runs.push((x, y, 1, layer)),
        }
    }
    runs
}

/// 一次连锁闪电在 `age` 时的每一道：放的人 -> 第一个，第一个 -> 第二个……（世界像素的折线）。
pub fn bolt_paths(f: &Fx, age: usize) -> Vec<Vec<(i32, i32)>> {
    let px = |p: (u64, u64)| (world::whole_px(p.0), world::whole_px(p.1) - CHEST);
    let shape = (age / BOLT_SHAPE) as u64;
    let mut from = px(f.at);
    let mut out = Vec::new();
    for (i, to) in f.to.iter().enumerate() {
        let to = px(*to);
        let salt = (f.tick as u64).wrapping_mul(0x1_0001).wrapping_add(shape * 131).wrapping_add(i as u64 * 7919);
        out.push(bolt_path(from, to, salt));
        from = to;
    }
    out
}

// ===================== 画 =====================

/// 画过的 (比赛, 局, 种类)：每种第一次画时记一行日志。
static SHOWN: Mutex<Vec<(u64, u64, Kind)>> = Mutex::new(Vec::new());

fn first_time(m: u64, s: u64, kind: Kind) -> bool {
    let Ok(mut l) = SHOWN.lock() else { return false };
    if l.contains(&(m, s, kind)) {
        return false;
    }
    l.retain(|x| (x.0, x.1) == (m, s));
    l.push((m, s, kind));
    true
}

// ===================== 元素峡谷的地形 =====================

fn anim(name: &str) -> Option<&'static Anim> {
    ANIMS.iter().find(|a| a.name == name)
}

/// 一条风道铺成的格子：(哪张图, 每一格放在哪)。横的、竖的每 48 像素一格（放格子的中心），河道那条斜的每 (24, 24) 一格
/// （放格子的左上角：图里的风沿着格子的对角线）。
pub fn wind_tiles(a: (u64, u64), b: (u64, u64)) -> (&'static str, Vec<(u64, u64)>) {
    let mut at = Vec::new();
    if a.1 == b.1 {
        let mut x = a.0.min(b.0) + 24_000;
        while x < a.0.max(b.0) {
            at.push((x, a.1));
            x += 48_000;
        }
        ("wind_h", at)
    } else if a.0 == b.0 {
        let mut y = a.1.min(b.1) + 24_000;
        while y < a.1.max(b.1) {
            at.push((a.0, y));
            y += 48_000;
        }
        ("wind_v", at)
    } else {
        let (mut x, mut y) = (a.0.min(b.0), a.1.min(b.1));
        while x + 24_000 < a.0.max(b.0) {
            at.push((x, y));
            x += 24_000;
            y += 24_000;
        }
        ("wind_d", at)
    }
}

/// 第 `i` 个蜂蜜果实在屏幕时钟 `t` 时长好了没有：峡谷变成海洋后 [`rift::FRUIT_FIRST`] tick 长好，被吃掉（`eaten`：
/// 到 `t` 为止它被吃掉的那些 tick）后 [`rift::FRUIT_RESPAWN`] tick 再长好。和模拟里一样。
pub fn fruit_ripe(since: usize, eaten: &[usize], t: usize) -> bool {
    t >= since + rift::FRUIT_FIRST && !eaten.iter().any(|&e| e <= t && t < e + rift::FRUIT_RESPAWN)
}

/// 一圈一圈循环的动画现在是第几帧。
fn loop_frame(a: &Anim, t: usize) -> usize {
    (t / a.ticks.max(1) as usize) % a.frames.max(1) as usize
}

/// 雨最多铺这么多格（镜头拉得再远也不多画）。
const RAIN_MOST: usize = 240;

/// 峡谷变成 `element`（在 tick `since`）以后的地形：变形后 [`rift::RISE_T`] tick 才有（岩石从变形那一刻开始往上升）。
/// -> 画了几样。
pub fn terrain(ctx: &mut StableClient<'_>, v: &world::View, m: u64, s: u64, t: usize, element: Element, since: usize) -> usize {
    let age = t.saturating_sub(since);
    let live = age >= rift::RISE_T;
    let mut n = 0;
    let mut put = |ctx: &mut StableClient<'_>, name: &str, fr: Option<usize>, at: (u64, u64)| {
        if let Some(a) = anim(name) {
            n += frame(ctx, v, a, fr.unwrap_or_else(|| loop_frame(a, t)), at) as usize;
        }
    };
    match element {
        Element::Cloud if live => {
            for (a, b) in rift::CURRENTS {
                let (name, tiles) = wind_tiles(a, b);
                for at in tiles {
                    put(ctx, name, None, at);
                }
            }
        }
        Element::Hextech if live => {
            for (a, b) in rift::GATES {
                put(ctx, "gate", None, a);
                put(ctx, "gate", None, b);
            }
        }
        Element::Ocean if live => {
            for at in rift::OCEAN_BRUSH {
                put(ctx, "brush_ocean", None, at);
            }
            let eaten = feed::fx_where(m, s, t, |f| matches!(f.kind, Kind::Fruit(_)));
            for (i, at) in rift::FRUITS.iter().enumerate() {
                let mine: Vec<usize> = eaten.iter().filter(|f| f.kind == Kind::Fruit(i as u8)).map(|f| f.tick).collect();
                if fruit_ripe(since, &mine, t) {
                    put(ctx, "fruit", None, *at);
                }
            }
        }
        Element::Chemtech if live => {
            for at in rift::CHEM_BRUSH {
                put(ctx, "brush_chem", None, at);
            }
        }
        Element::Mountain => {
            // rising from the moment the rift turns: its frames spread over the time until it stands
            let fr = anim("rock").map(|a| (age * a.frames as usize / rift::RISE_T.max(1)).min(a.frames as usize - 1));
            for at in rift::ROCKS {
                put(ctx, "rock", fr, at);
            }
        }
        Element::Infernal if live => {
            for (i, at) in rift::EMBERS.iter().enumerate() {
                // not all in step
                let fr = anim("ember").map(|a| loop_frame(a, t + i * 7));
                put(ctx, "ember", fr, *at);
            }
        }
        _ => {}
    }
    // the Ocean rift's rain: tiles over what the camera sees (the map's own coordinates: it does not move with the world)
    if element == Element::Ocean && live {
        if let (Some(a), Some((x, y, w, h))) = (anim("rain"), v.camera) {
            let (tw, th) = (a.w as f32, a.h as f32);
            let fr = loop_frame(a, t);
            let (x0, y0) = ((x / tw).floor() * tw, (y / th).floor() * th);
            let (cols, rows) = (((x + w - x0) / tw).ceil() as usize, ((y + h - y0) / th).ceil() as usize);
            if cols > 0 && rows > 0 && cols * rows <= RAIN_MOST {
                for r in 0..rows {
                    for c in 0..cols {
                        n += world::sprite_on_map(ctx, v, a, fr, (x0 + c as f32 * tw, y0 + r as f32 * th)) as usize;
                    }
                }
            }
        }
    }
    n
}

/// 画过地形的 (比赛, 局, 元素)：第一次画出来时记一行日志。
static TERRAIN_SHOWN: Mutex<Option<(u64, u64, Element, bool)>> = Mutex::new(None);

/// 屏幕时钟 `t` 时的地形（`rift`：峡谷变成了什么、哪个 tick）和正在放的特效（客户端扩展的 post_render 里调）。世界认不
/// 出来（[`world::view`]）就不画。
pub fn draw(ctx: &mut StableClient<'_>, m: u64, s: u64, t: usize, rift: Option<(Element, usize)>) {
    // every frame of a match, also with nothing to draw: the first one writes what the game's world looks like (WORLD)
    let Some(v) = world::view(ctx, m, s, t) else { return };
    if let Some((element, since)) = rift {
        let n = terrain(ctx, &v, m, s, t, element, since);
        let key = (m, s, element, t >= since + rift::RISE_T);
        if let Ok(mut shown) = TERRAIN_SHOWN.lock() {
            if n > 0 && *shown != Some(key) {
                *shown = Some(key);
                if let Some(k) = counted("terrain") {
                    wlog(format!("TERRAIN m={m} s={s} screen t={t}: the {} rift (turned at t={since}, live {}) - {n} pictures \
                                  drawn in the match world, z {}, sprites {} #{k}", element.key(), key.3, v.z, v.sprites));
                }
            }
        }
    }
    let mut live = feed::fx_live(m, s, t, longest());
    if live.is_empty() {
        return;
    }
    // further down the screen is drawn later (over what is behind it)
    live.sort_by_key(|f| (f.at.1, f.tick, f.kind));
    for f in &live {
        let age = t - f.tick;
        let mut drawn = false;
        match f.kind {
            Kind::HexBolt => {
                if age < BOLT_T {
                    for path in bolt_paths(f, age) {
                        for (x, y, w, layer) in bolt_runs(&path, age < BOLT_FULL) {
                            drawn |= world::run(ctx, &v, x, y, w, BOLT_COLOURS[layer.min(2) as usize]);
                        }
                    }
                }
                if let Some((a, fr)) = f.kind.anim().and_then(|a| frame_at(a, age).map(|fr| (a, fr))) {
                    for to in &f.to {
                        drawn |= frame(ctx, &v, a, fr, *to);
                    }
                }
            }
            Kind::Gate => {
                // the same flash at the gate he walked onto and at the one he comes out of
                if let Some((a, fr)) = f.kind.anim().and_then(|a| frame_at(a, age).map(|fr| (a, fr))) {
                    drawn |= frame(ctx, &v, a, fr, f.at);
                    for to in &f.to {
                        drawn |= frame(ctx, &v, a, fr, *to);
                    }
                }
            }
            kind => {
                if let Some((a, fr)) = kind.anim().and_then(|a| frame_at(a, age).map(|fr| (a, fr))) {
                    drawn |= frame(ctx, &v, a, fr, f.at);
                }
            }
        }
        if drawn && first_time(m, s, f.kind) {
            if let Some(k) = counted("fx") {
                let at = v.map(f.at);
                wlog(format!("FX m={m} s={s} t={} on screen at {t}: {:?} at ({}, {}) -> ({:.0}, {:.0}) on the \"Game\" map, \
                              {} more place(s), z {} #{k}", f.tick, f.kind, f.at.0, f.at.1, at.0, at.1, f.to.len(), v.z));
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_effect_has_its_animation_on_the_sheet() {
        let kinds = kinds();
        assert_eq!(kinds.len(), 16);
        let mut names: Vec<&str> = kinds.iter().map(|k| k.anim_name()).collect();
        for k in &kinds {
            let a = k.anim().unwrap_or_else(|| panic!("{k:?}: no animation {}", k.anim_name()));
            assert!(k.ticks() >= 20 && k.ticks() <= longest(), "{k:?} plays {} ticks", k.ticks());
            assert_eq!(frame_at(a, 0), Some(0));
            assert_eq!(frame_at(a, a.ticks as usize), Some(1));
            assert_eq!(frame_at(a, k.ticks()), None, "{k:?} is over after its last frame");
        }
        // every animation of the sheet is an effect's or a piece of the rift's terrain, none is both or neither
        names.extend(TERRAIN);
        names.sort();
        names.dedup();
        assert_eq!(names.len(), kinds.len() + TERRAIN.len(), "two effects on one animation");
        let mut all: Vec<&str> = ANIMS.iter().map(|a| a.name).collect();
        all.sort();
        assert_eq!(names, all, "an animation nothing plays, or one that is not on the sheet");
        // half a second to a second: read in a fight, gone before the next one
        assert!((40..=70).contains(&longest()), "{}", longest());
    }

    /// The frames compiled into the DLL are the sheet's: as many animations and frames, every run inside its frame.
    #[test]
    fn the_runs_are_the_sheets_frames() {
        let r = runs().expect("fx_runs.bin reads");
        assert_eq!(r.frames.len(), ANIMS.len());
        assert!(r.colours.iter().all(|c| c & 0xff == 0xff), "no half-transparent pixel");
        for (a, frames) in ANIMS.iter().zip(&r.frames) {
            assert_eq!(frames.len(), a.frames as usize, "{}", a.name);
            for (k, f) in frames.iter().enumerate() {
                assert!(!f.is_empty(), "{} frame {k} is empty", a.name);
                assert!(f.len() <= 1400, "{} frame {k}: {} rectangles", a.name, f.len());
                for run in f {
                    assert!(run[0] as u16 + run[2] as u16 <= a.w && (run[1] as u16) < a.h, "{} frame {k}: {run:?}", a.name);
                }
            }
        }
        // a broken file is no file
        assert!(parse_runs(b"DFXR").is_none() && parse_runs(&RUNS_BIN[..RUNS_BIN.len() - 1]).is_none());
        assert!(parse_runs(b"nope").is_none());
    }

    #[test]
    fn a_bolt_runs_from_one_to_the_other_and_is_the_same_every_time() {
        let (a, b) = ((100, 200), (160, 170));
        let p = bolt_path(a, b, 42);
        assert_eq!((p[0], *p.last().unwrap()), (a, b));
        assert_eq!(p, bolt_path(a, b, 42), "the screen's second run draws the same bolt");
        assert_ne!(p, bolt_path(a, b, 43), "another moment, another shape");
        assert!((4..=10).contains(&p.len()));
        // never far from the straight line
        let len = 60f32.hypot(30.0);
        for &(x, y) in &p {
            let off = ((x - a.0) as f32 * -30.0 - (y - a.1) as f32 * 60.0).abs() / len;
            assert!(off <= 8.5, "({x}, {y}) is {off} off the line");
        }
        // on top of each other: no bolt, no panic
        assert_eq!(bolt_path(a, a, 1), vec![a, a]);
        // the runs: every core pixel once, the full bolt wider, rows in order and no two runs overlapping
        let thin = bolt_runs(&p, false);
        let wide = bolt_runs(&p, true);
        assert!(thin.iter().all(|r| r.3 == 2));
        let area = |runs: &[(i32, i32, i32, u8)]| runs.iter().map(|r| r.2).sum::<i32>();
        assert!(area(&wide) > 3 * area(&thin));
        assert_eq!(wide.iter().filter(|r| r.3 == 2).map(|r| r.2).sum::<i32>(), area(&thin), "the core is whole inside it");
        for w in wide.windows(2) {
            assert!(w[1].1 > w[0].1 || w[1].0 >= w[0].0 + w[0].2, "{:?} then {:?}", w[0], w[1]);
        }
        assert!(wide.len() < 400, "{} rectangles for one bolt", wide.len());
    }

    /// The pictures of the rift's terrain (not effects: drawn for as long as the rift lasts).
    const TERRAIN: [&str; 10] = ["wind_h", "wind_v", "wind_d", "gate", "brush_ocean", "brush_chem", "fruit", "rock", "ember",
                                 "rain"];

    #[test]
    fn the_wind_is_tiled_along_each_current() {
        let mut seen = Vec::new();
        for (a, b) in rift::CURRENTS {
            let (name, tiles) = wind_tiles(a, b);
            let tile = anim(name).expect(name);
            seen.push(name);
            assert!(tiles.len() >= 5, "{name}: {} tiles", tiles.len());
            // every tile's picture lies on the current: its middle within the current's half width
            for at in &tiles {
                let mid = if name == "wind_d" { (at.0 + 24_000, at.1 + 24_000) } else { *at };
                assert!(rift::seg_d2(mid, a, b) <= 1_000 * 1_000, "{name} tile at {at:?} is off its current");
            }
            // end to end without a gap: the step is the picture's period along the flow
            let step = (tiles[1].0 - tiles[0].0).max(tiles[1].1 - tiles[0].1);
            assert_eq!(step, if name == "wind_d" { 24_000 } else { 48_000 });
            assert!(tile.w.max(tile.h) as u64 * 1000 >= step, "{name}: the picture is shorter than its step");
            // they cover the current from one end to the other (to within a tile)
            let last = tiles[tiles.len() - 1];
            assert!(a.0.max(b.0) - last.0 <= 48_000 && a.1.max(b.1) - last.1 <= 48_000, "{name}: ends at {last:?}");
        }
        seen.sort();
        seen.dedup();
        assert_eq!(seen, vec!["wind_d", "wind_h", "wind_v"], "the river's diagonal, the two ways of the jungles'");
    }

    #[test]
    fn a_fruit_is_drawn_while_the_simulation_has_it_ripe() {
        let since = 10_000;
        assert!(!fruit_ripe(since, &[], since + rift::FRUIT_FIRST - 1));
        assert!(fruit_ripe(since, &[], since + rift::FRUIT_FIRST));
        let eaten = [since + 2_000];
        assert!(fruit_ripe(since, &eaten, since + 1_999), "wound back before it was eaten: there again");
        assert!(!fruit_ripe(since, &eaten, since + 2_000));
        assert!(!fruit_ripe(since, &eaten, since + 2_000 + rift::FRUIT_RESPAWN - 1));
        assert!(fruit_ripe(since, &eaten, since + 2_000 + rift::FRUIT_RESPAWN));
        // the simulation's own clock says the same (rift.rs)
        let mut t = rift::Terrain::default();
        t.start(Element::Ocean, since);
        assert_eq!(t.ripe(0, since + rift::FRUIT_FIRST - 1), fruit_ripe(since, &[], since + rift::FRUIT_FIRST - 1));
        assert_eq!(t.ripe(0, since + rift::FRUIT_FIRST), fruit_ripe(since, &[], since + rift::FRUIT_FIRST));
    }

    #[test]
    fn a_chain_is_a_bolt_to_each_champion_in_turn() {
        let f = Fx { m: 1, s: 1, tick: 500, kind: Kind::HexBolt, at: (100_000, 200_000),
                     to: vec![(150_000, 200_000), (150_000, 260_000), (90_000, 300_000)] };
        let paths = bolt_paths(&f, 0);
        assert_eq!(paths.len(), 3);
        assert_eq!(paths[0][0], (100, 200 - CHEST));
        assert_eq!(*paths[0].last().unwrap(), (150, 200 - CHEST));
        assert_eq!(paths[1][0], (150, 200 - CHEST), "the second from the first one hit");
        assert_eq!(*paths[2].last().unwrap(), (90, 300 - CHEST));
        // the shape holds for BOLT_SHAPE ticks, then changes
        assert_eq!(bolt_paths(&f, 0), bolt_paths(&f, BOLT_SHAPE - 1));
        assert_ne!(bolt_paths(&f, 0), bolt_paths(&f, BOLT_SHAPE));
    }
}
