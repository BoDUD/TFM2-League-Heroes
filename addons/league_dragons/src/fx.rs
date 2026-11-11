//! 本包自己画在战场上的特效（0.4.0，用户 2026-11-11：「龙魂确定生效了吗」——日志里那一局炼狱龙魂炸了 90 次，屏幕上
//! 什么都看不出来；「拿了龙魂没有特效的 都要补 还有远古龙斩杀特效的」）：
//!
//! | 什么时候 | 画什么（`effects/league_dragons_fx#sheet.png` 里的动画） |
//! |---|---|
//! | 炼狱龙魂爆炸 | 被炸的人脚下一团火、一圈火环、飘起的火星（`infernal_blast`） |
//! | 山脉龙魂上盾 | 碎石从地上升起、合成一层琥珀色的壳（`mountain_shield`） |
//! | 海洋龙魂回血 | 一圈水收到脚下、涌起、水珠往上飘（`ocean_heal`） |
//! | 云端龙魂放大招后的加速 | 一阵风卷、几道速度线（`cloud_gust`） |
//! | 海克斯龙魂的连锁闪电 | 从放的人到每个被打的人一道闪电（折线，三层线），落点一团电光（`hex_spark`） |
//! | 化学科技龙魂残血 | 毒液窜起、冒泡（`chem_rage`） |
//! | 拿到龙魂 | 那一队每个活着的英雄脚下一圈元素、一根元素的光柱（`soul_<元素>`） |
//! | 远古龙之力点燃 | 一小团远古的火（`elder_burn`；已经烧着的人再被打到不再放） |
//! | 远古龙之力斩杀 | 一道远古的火柱从天上砸下来、地上炸开、一圈冲击波（`elder_execute`） |
//!
//! 图是 tools/art/dragons_soul_fx.py 一格一格画的像素图（1 格 = 1 个游戏像素）：能画贴图时整帧一条贴图命令；不能时
//! （[`super::world::plan`]）按编进 DLL 的同一份图（`fx_runs.bin`：每帧拆成一条条同色的横条）一条一条画，不靠任何文件。比赛钩子在屏幕放的那场模拟里记下
//! 「哪个 tick、在哪、什么特效」（[`super::feed::fx`]，模拟不读它），客户端扩展按屏幕时钟画（[`draw`]）：特效不跟着英雄走，
//! 留在发生的地方（半秒左右）。画法在 [`super::world`]。

use std::sync::{Mutex, OnceLock};

use mod_api_stable::*;

use super::fx_atlas::{Anim, ANIMS};
use super::rules::{mix, Element};
use super::{counted, feed, wlog, world};

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

/// 最长的一种放多少 tick（[`super::feed::fx_live`] 往回找这么远）。
pub fn longest() -> usize {
    ANIMS.iter().map(|a| a.frames as usize * a.ticks as usize).max().unwrap_or(0).max(BOLT_T)
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
/// 描边、蓝边、白芯（tools/art/dragon_fx.py 的海克斯色）和各自的线宽（世界像素）。
const BOLT_COLOURS: [u32; 3] = [0x16_14_4e_ff, 0x4c_90_ff_ff, 0xda_f6_ff_ff];
const BOLT_WIDTHS: [f32; 3] = [5.0, 3.0, 1.4];

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

/// 一道闪电画哪几层线：(线宽, 颜色)，从下往上——整道是描边、蓝边、白芯，`full` false 只剩芯。
pub fn bolt_layers(full: bool) -> Vec<(f32, u32)> {
    (if full { 0 } else { 2 }..3).map(|i| (BOLT_WIDTHS[i], BOLT_COLOURS[i])).collect()
}

/// 画一道闪电：折线的每一段一条线，一层画完再画上面一层（同一个 z 上后推的在上面）。0.4.4 起用线（每道 3–9 段 × 三层），
/// 之前是一格一格的横条（每道几百条矩形）——横条也显示得出来（校准的第二张截图），线只是命令少。
pub fn bolt(ctx: &mut StableClient<'_>, v: &world::View, pts: &[(i32, i32)], full: bool) -> bool {
    let mut drawn = false;
    for (width, colour) in bolt_layers(full) {
        for w in pts.windows(2) {
            // through the middle of the pixels
            let a = v.px((w[0].0 as f32 + 0.5, w[0].1 as f32 + 0.5));
            let b = v.px((w[1].0 as f32 + 0.5, w[1].1 as f32 + 0.5));
            drawn |= ctx.draw_line(world::GAME, a.0, a.1, b.0, b.1, width * v.scale.0, v.z, colour);
        }
    }
    drawn
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

/// 屏幕时钟 `t` 时正在放的特效（客户端扩展的 post_render 里调）。世界认不出来（[`world::view`]）就不画。
pub fn draw(ctx: &mut StableClient<'_>, m: u64, s: u64, t: usize) {
    // every frame of a match, also with nothing to draw: the first one writes what the game's world looks like (WORLD)
    let Some(v) = world::view(ctx, m, s, t) else { return };
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
                        drawn |= bolt(ctx, &v, &path, age < BOLT_FULL);
                    }
                }
                if let Some((a, fr)) = f.kind.anim().and_then(|a| frame_at(a, age).map(|fr| (a, fr))) {
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
                              {} more place(s), z {}, sprites {} #{k}", f.tick, f.kind, f.at.0, f.at.1, at.0, at.1, f.to.len(), v.z,
                             if v.sprites { "on" } else { "OFF" }));
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::rules::DRAKES;

    #[test]
    fn every_effect_has_its_animation_on_the_sheet() {
        let mut kinds = vec![Kind::InfernalBlast, Kind::HexBolt, Kind::MountainShield, Kind::OceanHeal, Kind::CloudGust,
                             Kind::ChemRage, Kind::ElderBurn, Kind::Execute];
        kinds.extend(DRAKES.iter().map(|&e| Kind::Soul(e)));
        let mut names: Vec<&str> = kinds.iter().map(|k| k.anim_name()).collect();
        for k in &kinds {
            let a = k.anim().unwrap_or_else(|| panic!("{k:?}: no animation {}", k.anim_name()));
            assert!(k.ticks() >= 20 && k.ticks() <= longest(), "{k:?} plays {} ticks", k.ticks());
            assert_eq!(frame_at(a, 0), Some(0));
            assert_eq!(frame_at(a, a.ticks as usize), Some(1));
            assert_eq!(frame_at(a, k.ticks()), None, "{k:?} is over after its last frame");
        }
        names.sort();
        names.dedup();
        assert_eq!(names.len(), ANIMS.len(), "an animation nothing plays, or two effects on one");
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
        // drawn as lines, the widest first: outline, edge, core - later only the core
        let widths = |full: bool| bolt_layers(full).iter().map(|l| l.0).collect::<Vec<f32>>();
        assert_eq!(widths(true), vec![5.0, 3.0, 1.4]);
        assert_eq!(bolt_layers(false), vec![(1.4, BOLT_COLOURS[2])]);
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
