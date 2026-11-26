//! 触发类海克斯在战场上的特效（0.3.0，用户 2026-11-26：「还有触发特效也要做吧 需要让codex帮忙的话就让codex帮忙做美术」）。
//!
//! 比赛钩子在屏幕放的那场模拟里记下「哪个 tick、哪一种、在哪」（[`super::procs::Out`] -> [`super::feed::fx`]，模拟不读它），
//! 客户端扩展按屏幕时钟画（[`draw`]）：大多数特效留在发生的地方放完（半秒到一秒）；飞弹、雪球从放的人飞到目标（雪球走一道弧）；
//! 连锁闪电、风刃画成线（大小龙海克斯龙魂的闪电画法）。图是 tools/art/hextech_fx.py 一格一格画的像素图
//! （`effects/league_hextech_fx#sheet.png`，表在 [`super::fx_atlas`]）：能画贴图时整帧一条贴图命令；不能时按编进 DLL 的同一份图
//! （`fx_runs.bin`：每帧拆成一条条同色的横条）一条一条画。画法和层级在 [`super::world`]。
//!
//! | 海克斯 | 画什么（图上的动画） |
//! |---|---|
//! | 烈焰烙印 | 每烧一下一小团火（`burn`） |
//! | 彻骨冰寒 | 冰晶炸开（`frost`） |
//! | 点亮他们！ | 金色的星爆（`light_pop`） |
//! | 逃跑计划 | 蓝色的泡泡盾、速度线（`escape`） |
//! | 坦克引擎、歌利亚巨人 | 脚下一圈绿光、往上的箭头（`grow`） |
//! | 秘术冲拳 | 一小团蓝光（`punch`，一秒最多一次） |
//! | 重击手 | 橙色的冲击（`heavy`） |
//! | 魔法飞弹 | 紫色的飞弹飞过去（`missile`）、炸开（`missile_pop`） |
//! | 连锁闪电 | 一道道闪电（线）、落点的电光（`spark`） |
//! | 弱点暴露 | 头上一个裂开的红圈（`crack`） |
//! | 以太武器 | 紫色的月牙斩（`ether`） |
//! | 巨像的勇气 | 石块升起来围成一圈（`stone`） |
//! | 处刑人 | 红色的十字斩（`execute`） |
//! | 黎明使者的决心 | 金色的光柱落下（`dawn`） |
//! | 兴奋起来！ | 绕着身体往上飞的星星（`excited`） |
//! | 守护者 | 队友身前一面盾、两人之间一道光（`guard`） |
//! | 惊世邪恶 | 一缕紫色的魂（`wisp`） |
//! | 轨道激光 | 地上的红色瞄准圈（`laser_mark`）、天上打下来的激光（`laser`） |
//! | 残忍 | 彗星从天上落下来、砸地（`comet`） |
//! | 最终形态 | 金色的光爆（`final_form`；身体变大在 [`super::hd`]） |
//! | 超级雪球 | 雪球飞过去（`snowball`）、雪花炸开（`snow_burst`） |
//! | 量子计算 | 一圈青色的斩击（`quantum`） |
//! | 不灭意志 | 光环和翅膀（`undying`） |
//! | 献祭光环 | 脚下一圈火（`immolate`，打到人的那一秒） |
//! | 台风 | 风刃（线）、落点的旋风（`gust`） |
//! | 圣光庇佑 | 金色的光罩（`ward`） |
//! | 逃跑计划、守护者、巨像的勇气、圣光庇佑的护盾还在时 | 身上一圈白里带蓝的光（线，跟着人走，盾没了就灭；0.3.3） |

use std::sync::{Mutex, OnceLock};

use mod_api_stable::*;

use super::fx_atlas::{Anim, ANIMS};
use super::procs::Show;
use super::rules::splitmix;
use super::{counted, feed, wlog, world};

/// 每一种（测试、日志用）。
pub const ALL: [Show; 29] = [
    Show::Burn, Show::Frost, Show::LightPop, Show::Escape, Show::Grow, Show::Punch, Show::Heavy, Show::Missile,
    Show::MissilePop, Show::Chain, Show::Crack, Show::Ether, Show::Stone, Show::Execute, Show::Dawn, Show::Excited,
    Show::Guard, Show::Wisp, Show::LaserMark, Show::Laser, Show::Comet, Show::FinalForm, Show::Snowball, Show::SnowBurst,
    Show::Quantum, Show::Undying, Show::Immolate, Show::Typhoon, Show::Ward,
];

/// 图上那段动画的名字（闪电、风刃：落点的那一小团）。
pub fn anim_name(s: Show) -> &'static str {
    match s {
        Show::Burn => "burn",
        Show::Frost => "frost",
        Show::LightPop => "light_pop",
        Show::Escape => "escape",
        Show::Grow => "grow",
        Show::Punch => "punch",
        Show::Heavy => "heavy",
        Show::Missile => "missile",
        Show::MissilePop => "missile_pop",
        Show::Chain => "spark",
        Show::Crack => "crack",
        Show::Ether => "ether",
        Show::Stone => "stone",
        Show::Execute => "execute",
        Show::Dawn => "dawn",
        Show::Excited => "excited",
        Show::Guard => "guard",
        Show::Wisp => "wisp",
        Show::LaserMark => "laser_mark",
        Show::Laser => "laser",
        Show::Comet => "comet",
        Show::FinalForm => "final_form",
        Show::Snowball => "snowball",
        Show::SnowBurst => "snow_burst",
        Show::Quantum => "quantum",
        Show::Undying => "undying",
        Show::Immolate => "immolate",
        Show::Typhoon => "gust",
        Show::Ward => "ward",
        // 下面这些是画的线，图上没有
        Show::ShieldGlow => "shield_glow",
        Show::HolyGlow => "holy_glow",
        Show::RingRed => "ring_red",
        Show::RingGold => "ring_gold",
        Show::RingBlue => "ring_blue",
        Show::RingPurple => "ring_purple",
        Show::RingCyan => "ring_cyan",
        Show::Boomerang => "boomerang",
        Show::Tether => "tether",
        Show::Trail => "trail",
        Show::Hive => "hive",
        Show::Bees => "bees",
        Show::RingGreen => "ring_green",
        Show::Blob => "blob",
    }
}

/// 画的线（不是图上的动画），放 `dur` tick（0.4.0）。
pub fn drawn_by_lines(s: Show) -> bool {
    matches!(s, Show::ShieldGlow | Show::HolyGlow | Show::RingRed | Show::RingGold | Show::RingBlue | Show::RingPurple
        | Show::RingCyan | Show::Boomerang | Show::Tether | Show::Trail | Show::Hive | Show::Bees | Show::RingGreen
        | Show::Blob)
}

pub fn anim(s: Show) -> Option<&'static Anim> {
    let name = anim_name(s);
    ANIMS.iter().find(|a| a.name == name)
}

fn length(a: &Anim) -> usize {
    a.frames as usize * a.ticks as usize
}

/// 飞的东西（飞弹、雪球）：按 `dur` 飞完为止。
fn flies(s: Show) -> bool {
    matches!(s, Show::Missile | Show::Snowball)
}

/// 这一次一共放多少 tick。
pub fn ticks(f: &feed::Fx) -> usize {
    if flies(f.show) || drawn_by_lines(f.show) {
        return (f.dur as usize).max(1);
    }
    let a = anim(f.show).map_or(0, length);
    match f.show {
        Show::Chain => a.max(BOLT_T),
        Show::Typhoon => a.max(BLADE_T),
        Show::Guard => a.max(LINK_T),
        _ => a,
    }
}

/// 最长的一种放多少 tick（[`super::feed::fx_live`] 往回找这么远）：飞得最久的也算在内。
pub fn longest() -> usize {
    static LONGEST: OnceLock<usize> = OnceLock::new();
    *LONGEST.get_or_init(|| {
        let anims = ALL.iter().filter_map(|&s| anim(s)).map(length).max().unwrap_or(0);
        anims.max(super::procs::SNOW_T).max(BOLT_T).max(BLADE_T).max(LINK_T).max(120)
    })
}

/// 开始 `age` tick 后是第几帧（放完了：None）。
pub fn frame_at(a: &Anim, age: usize) -> Option<usize> {
    let f = age / (a.ticks.max(1) as usize);
    (f < a.frames as usize).then_some(f)
}

/// 一圈一圈循环的动画（飞着的飞弹、雪球）现在是第几帧。
fn loop_frame(a: &Anim, age: usize) -> usize {
    (age / a.ticks.max(1) as usize) % a.frames.max(1) as usize
}

// ===================== 同一份图，拆成横条 =====================

/// tools/art/hextech_fx.py 写的：`DFXR`、颜色数、颜色（RGBA）、动画数，每段动画的帧数，每帧的横条数和横条
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

// ===================== 线：闪电、风刃、守护的光 =====================

/// 闪电亮多少 tick；前这么多 tick 是整道（描边、蓝边、白芯），之后只剩芯；每这么多 tick 换一次形状。
pub const BOLT_T: usize = 14;
const BOLT_FULL: usize = 9;
const BOLT_SHAPE: usize = 3;
/// 风刃飞多少 tick；守护者的那道光亮多少 tick。
pub const BLADE_T: usize = 12;
pub const LINK_T: usize = 14;
/// 线的两头离脚底多高（世界像素，英雄的胸口）。
pub const CHEST: i32 = 14;
/// 描边、蓝边、白芯和各自的线宽（世界像素）。
const BOLT_COLOURS: [u32; 3] = [0x0b_1a_3a_ff, 0x4f_b0_ff_ff, 0xe6_f8_ff_ff];
const BOLT_WIDTHS: [f32; 3] = [5.0, 3.0, 1.4];
/// 风刃：描边、青白。
const BLADE_COLOURS: [u32; 2] = [0x1a_3a_3a_ff, 0xc8_ff_f0_ff];
const BLADE_WIDTHS: [f32; 2] = [4.0, 2.0];
/// 守护者的光：描边、亮蓝。
const LINK_COLOURS: [u32; 2] = [0x0b_1a_3a_ff, 0xb0_ec_ff_ff];
const LINK_WIDTHS: [f32; 2] = [3.0, 1.4];

/// -1 .. 1，`salt` 定。
fn jitter(salt: u64) -> f32 {
    (splitmix(salt) % 2001) as f32 / 1000.0 - 1.0
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

/// 一条折线按几层画（一层画完再画上面一层：同一个 z 上后推的在上面）。
fn lines(ctx: &mut StableClient<'_>, v: &world::View, pts: &[(i32, i32)], layers: &[(f32, u32)]) -> bool {
    let mut drawn = false;
    for &(width, colour) in layers {
        for w in pts.windows(2) {
            let a = v.px((w[0].0 as f32 + 0.5, w[0].1 as f32 + 0.5));
            let b = v.px((w[1].0 as f32 + 0.5, w[1].1 as f32 + 0.5));
            drawn |= ctx.draw_line(world::GAME, a.0, a.1, b.0, b.1, width * v.scale.0, v.z, colour);
        }
    }
    drawn
}

fn chest(p: (u64, u64)) -> (i32, i32) {
    (world::whole_px(p.0), world::whole_px(p.1) - CHEST)
}

// ===================== 护盾的光（0.3.3） =====================

/// 光圈的中心离脚底多高、横竖两个半径（世界像素：罩住整个人）；一圈几段；一明一暗一次多少 tick、大小差多少。
pub const GLOW_UP: f32 = 16.0;
pub const GLOW_RX: f32 = 14.0;
pub const GLOW_RY: f32 = 19.0;
const GLOW_SEGS: usize = 24;
const GLOW_BEAT: usize = 36;
const GLOW_PULSE: f32 = 0.06;
/// 外面一层淡的光晕、中间一层、最里面一道亮边（英雄联盟的护盾那种白里带蓝）。
const GLOW_COLOURS: [u32; 3] = [0x7c_d4_ff_48, 0xb4_ec_ff_8c, 0xf2_fc_ff_e0];
const GLOW_WIDTHS: [f32; 3] = [4.2, 2.4, 1.0];

/// 屏幕时钟 `t` 时罩在 `at`（脚底）那个人身上的一圈（世界像素，首尾相接）：跟着屏幕时钟轻轻一涨一缩。
pub fn glow_ring(at: (u64, u64), t: usize) -> Vec<(f32, f32)> {
    let beat = (t % GLOW_BEAT) as f32 / GLOW_BEAT as f32 * std::f32::consts::TAU;
    let k = 1.0 + GLOW_PULSE * beat.sin();
    let (cx, cy) = (world::whole_px(at.0) as f32 + 0.5, world::whole_px(at.1) as f32 - GLOW_UP);
    (0..=GLOW_SEGS)
        .map(|i| {
            let a = i as f32 / GLOW_SEGS as f32 * std::f32::consts::TAU;
            (cx + GLOW_RX * k * a.cos(), cy + GLOW_RY * k * a.sin())
        })
        .collect()
}

/// 一条折线按几层画（[`lines`] 的小数坐标版）。
fn ring(ctx: &mut StableClient<'_>, v: &world::View, pts: &[(f32, f32)], layers: &[(f32, u32)]) -> bool {
    let mut drawn = false;
    for &(width, colour) in layers {
        for w in pts.windows(2) {
            let (a, b) = (v.px(w[0]), v.px(w[1]));
            drawn |= ctx.draw_line(world::GAME, a.0, a.1, b.0, b.1, width * v.scale.0, v.z, colour);
        }
    }
    drawn
}

fn glow_layers() -> Vec<(f32, u32)> {
    GLOW_WIDTHS.into_iter().zip(GLOW_COLOURS).collect()
}

// ===================== 0.4.0：光圈、回旋刃、牵引、裂痕、无敌 =====================

/// 无敌的金光（和护盾的光一样的圈，金色）。
const HOLY_COLOURS: [u32; 3] = [0xff_d2_5a_48, 0xff_e6_8c_96, 0xff_fa_dc_e6];
/// 外扩的光圈：(外层淡、中层、亮芯) 每种颜色。
fn ring_colours(s: Show) -> [u32; 3] {
    match s {
        Show::RingRed => [0xff_50_2a_50, 0xff_86_46_a0, 0xff_d8_a0_f0],
        Show::RingGold => [0xff_c4_3c_50, 0xff_dc_78_a0, 0xff_f6_c8_f0],
        Show::RingBlue => [0x3c_8c_ff_50, 0x78_b8_ff_a0, 0xd2_ea_ff_f0],
        Show::RingPurple => [0xa0_4c_ff_50, 0xc0_82_ff_a0, 0xec_d2_ff_f0],
        Show::RingGreen => [0x3c_c8_3c_50, 0x78_e6_64_a0, 0xd2_ff_c8_f0],
        _ => [0x3c_e6_ff_50, 0x8c_f0_ff_a0, 0xdc_fc_ff_f0],
    }
}
const RING_WIDTHS: [f32; 3] = [5.0, 2.6, 1.1];
/// 光圈默认的最大半径（模拟单位）、地上的圈扁成这么多（竖着 / 横着）。
pub const RING_R: u64 = 30_000;
pub const RING_FLAT: f32 = 0.5;

/// 颜色乘上不透明度（0..1）。
fn fade(c: u32, k: f32) -> u32 {
    let a = ((c & 0xff) as f32 * k.clamp(0.0, 1.0)) as u32;
    (c & 0xffff_ff00) | a
}

/// 外扩的光圈在 `age` 时：地上一圈（世界像素，首尾相接）和这时的不透明度。从三成大扩到最大，越扩越淡。
pub fn ring_at(f: &feed::Fx, age: usize) -> (Vec<(f32, f32)>, f32) {
    let dur = (f.dur as usize).max(1);
    let s = (age as f32 / dur as f32).clamp(0.0, 1.0);
    let r_max = f.to.first().map_or(RING_R, |x| x.0) as f32 / world::UNITS_PER_PX;
    let r = r_max * (0.3 + 0.7 * s);
    let (cx, cy) = (world::whole_px(f.at.0) as f32 + 0.5, world::whole_px(f.at.1) as f32);
    let pts = (0..=GLOW_SEGS)
        .map(|i| {
            let a = i as f32 / GLOW_SEGS as f32 * std::f32::consts::TAU;
            (cx + r * a.cos(), cy + r * RING_FLAT * a.sin())
        })
        .collect();
    (pts, 1.0 - s * 0.85)
}

/// 回旋刃在 `age` 时在哪（世界像素，胸口高）：前一半从 `at` 飞到 `to[0]`，后一半飞回来。
pub fn boomerang_at(f: &feed::Fx, age: usize) -> Option<(f32, f32)> {
    let to = *f.to.first()?;
    let dur = (f.dur as usize).max(2);
    if age > dur {
        return None;
    }
    let s = age as f32 / dur as f32;
    let k = if s < 0.5 { s * 2.0 } else { 2.0 - s * 2.0 };
    let (a, b) = (chest(f.at), chest(to));
    Some((a.0 as f32 + (b.0 - a.0) as f32 * k + 0.5, a.1 as f32 + (b.1 - a.1) as f32 * k + 0.5))
}

/// 回旋刃本身：一个转着的十字（两道，世界像素的四个端点）。
pub fn boomerang_blades(p: (f32, f32), age: usize) -> [[(f32, f32); 2]; 2] {
    let a = age as f32 * 0.7;
    let r = 6.0;
    let arm = |t: f32| [(p.0 + r * t.cos(), p.1 + r * t.sin()), (p.0 - r * t.cos(), p.1 - r * t.sin())];
    [arm(a), arm(a + std::f32::consts::FRAC_PI_2)]
}

// ===================== 0.4.0 第二批：蜂巢、蜂群、黏液 =====================

/// 一个小圈（世界像素，首尾相接）。
fn small_loop(p: (f32, f32), rx: f32, ry: f32, n: usize) -> Vec<(f32, f32)> {
    (0..=n)
        .map(|i| {
            let a = i as f32 / n as f32 * std::f32::consts::TAU;
            (p.0 + rx * a.cos(), p.1 + ry * a.sin())
        })
        .collect()
}

const HIVE_COLOURS: [u32; 2] = [0x5a_32_0a_d0, 0xff_c8_32_f0];
const HIVE_WIDTHS: [f32; 2] = [4.0, 2.2];

/// 蜂巢在 `age` 时在哪（世界像素，胸口高，和雪球一样带弧线）。
pub fn hive_at(f: &feed::Fx, age: usize) -> Option<(f32, f32)> {
    let to = *f.to.first()?;
    let dur = (f.dur as usize).max(1);
    if age > dur {
        return None;
    }
    let s = age as f32 / dur as f32;
    let (a, b) = (chest(f.at), chest(to));
    let lift = 30.0 * 4.0 * s * (1.0 - s);
    Some((a.0 as f32 + (b.0 - a.0) as f32 * s + 0.5, a.1 as f32 + (b.1 - a.1) as f32 * s + 0.5 - lift))
}

const BEE_COLOURS: [u32; 2] = [0x1e_14_00_c8, 0xff_dc_28_ff];
const BEE_WIDTHS: [f32; 2] = [2.6, 1.4];

/// 蜂群在 `age` 时的四只蜜蜂（每只一小段，世界像素）：绕着 `at` 那个人的胸口转。
pub fn bees_at(f: &feed::Fx, age: usize) -> Vec<[(f32, f32); 2]> {
    let c = chest(f.at);
    let (cx, cy) = (c.0 as f32 + 0.5, c.1 as f32 + 0.5);
    (0..4)
        .map(|i| {
            let a = age as f32 * 0.45 + i as f32 * std::f32::consts::FRAC_PI_2;
            let r = 7.0 + 2.0 * (age as f32 * 0.3 + i as f32).sin();
            let (x, y) = (cx + r * a.cos(), cy + r * 0.6 * a.sin());
            [(x - 1.0, y), (x + 1.0, y)]
        })
        .collect()
}

const BLOB_COLOURS: [u32; 3] = [0x1e_6e_1e_a0, 0x50_d2_3c_d0, 0xb4_ff_8c_f0];
const BLOB_WIDTHS: [f32; 3] = [4.0, 2.4, 1.0];

/// 地上的一团黏液：扁扁的一小圈，一鼓一鼓的。
pub fn blob_ring(at: (u64, u64), t: usize) -> Vec<(f32, f32)> {
    let k = 1.0 + 0.12 * ((t % 40) as f32 / 40.0 * std::f32::consts::TAU).sin();
    let (cx, cy) = (world::whole_px(at.0) as f32 + 0.5, world::whole_px(at.1) as f32);
    small_loop((cx, cy), 5.0 * k, 2.6 * k, 12)
}

const TETHER_COLOURS: [u32; 2] = [0x3a_0b_2a_c8, 0xff_9c_e6_f0];
const TETHER_WIDTHS: [f32; 2] = [3.2, 1.4];
const TRAIL_COLOURS: [u32; 3] = [0x3a_1a_0b_d0, 0xc8_6e_28_e6, 0xff_d2_8c_f0];
const TRAIL_WIDTHS: [f32; 3] = [5.0, 3.0, 1.2];

/// 裂痕在 `age` 时的几层：越到爆开越亮、越宽。
pub fn trail_layers(f: &feed::Fx, age: usize) -> Vec<(f32, u32)> {
    let s = (age as f32 / (f.dur as usize).max(1) as f32).clamp(0.0, 1.0);
    TRAIL_WIDTHS.iter().zip(TRAIL_COLOURS).map(|(&w, c)| (w * (0.6 + 0.6 * s), fade(c, 0.5 + 0.5 * s))).collect()
}

/// 一次连锁闪电在 `age` 时的每一道：放的人 -> 第一个，第一个 -> 第二个……（世界像素的折线）。
pub fn bolt_paths(f: &feed::Fx, age: usize) -> Vec<Vec<(i32, i32)>> {
    let shape = (age / BOLT_SHAPE) as u64;
    let mut from = chest(f.at);
    let mut out = Vec::new();
    for (i, to) in f.to.iter().enumerate() {
        let to = chest(*to);
        let salt = (f.tick as u64).wrapping_mul(0x1_0001).wrapping_add(shape * 131).wrapping_add(i as u64 * 7919);
        out.push(bolt_path(from, to, salt));
        from = to;
    }
    out
}

/// 一道风刃在 `age` 时是路上的哪一小段（从放的人飞向 `to`，长度是路的三分之一）。
pub fn blade(at: (u64, u64), to: (u64, u64), age: usize) -> Option<[(i32, i32); 2]> {
    if age >= BLADE_T {
        return None;
    }
    let (a, b) = (chest(at), chest(to));
    let s0 = age as f32 / BLADE_T as f32;
    let s1 = (s0 + 0.35).min(1.0);
    let p = |s: f32| ((a.0 as f32 + (b.0 - a.0) as f32 * s).round() as i32, (a.1 as f32 + (b.1 - a.1) as f32 * s).round() as i32);
    Some([p(s0), p(s1)])
}

/// 飞弹、雪球在 `age` 时在哪（模拟坐标，已经抬到它飞的高度）：飞弹在胸口的高度，雪球走一道弧。
pub fn flight(f: &feed::Fx, age: usize) -> Option<(u64, u64)> {
    let to = *f.to.first()?;
    let dur = (f.dur as usize).max(1);
    if age > dur {
        return None;
    }
    let s = age as f64 / dur as f64;
    let x = f.at.0 as f64 + (to.0 as f64 - f.at.0 as f64) * s;
    let y = f.at.1 as f64 + (to.1 as f64 - f.at.1 as f64) * s;
    let lift = match f.show {
        Show::Snowball => CHEST as f64 + 30.0 * 4.0 * s * (1.0 - s),
        _ => CHEST as f64,
    };
    Some((x.max(0.0) as u64, (y - lift * world::UNITS_PER_PX as f64).max(0.0) as u64))
}

// ===================== 画 =====================

/// 画过的 (比赛, 局, 种类)：每种第一次画时记一行日志。
static SHOWN: Mutex<Vec<(u64, u64, Show)>> = Mutex::new(Vec::new());

fn first_time(m: u64, s: u64, show: Show) -> bool {
    let Ok(mut l) = SHOWN.lock() else { return false };
    if l.contains(&(m, s, show)) {
        return false;
    }
    l.retain(|x| (x.0, x.1) == (m, s));
    l.push((m, s, show));
    true
}

/// 屏幕时钟 `t` 时还在放的特效（客户端扩展的 post_render 里调）。世界认不出来（[`world::view`]）就不画。
pub fn draw(ctx: &mut StableClient<'_>, m: u64, s: u64, t: usize) {
    let mut live = feed::fx_live(m, s, t, longest());
    live.retain(|f| t - f.tick < ticks(f));
    if live.is_empty() {
        return;
    }
    let Some(v) = world::view(ctx, m, s, t) else { return };
    // 屏幕上越往下的越晚画（压在后面的上面）
    live.sort_by_key(|f| (f.at.1, f.tick, f.show));
    for f in &live {
        let age = t - f.tick;
        let mut drawn = false;
        match f.show {
            Show::Missile | Show::Snowball => {
                if let (Some(a), Some(p)) = (anim(f.show), flight(f, age)) {
                    drawn |= frame(ctx, &v, a, loop_frame(a, age), p);
                }
            }
            Show::Chain => {
                if age < BOLT_T {
                    for path in bolt_paths(f, age) {
                        drawn |= lines(ctx, &v, &path, &bolt_layers(age < BOLT_FULL));
                    }
                }
                if let Some((a, fr)) = anim(f.show).and_then(|a| frame_at(a, age).map(|fr| (a, fr))) {
                    for to in &f.to {
                        drawn |= frame(ctx, &v, a, fr, *to);
                    }
                }
            }
            Show::Typhoon => {
                let layers: Vec<(f32, u32)> = BLADE_WIDTHS.iter().copied().zip(BLADE_COLOURS).collect();
                for to in &f.to {
                    if let Some(seg) = blade(f.at, *to, age) {
                        drawn |= lines(ctx, &v, &seg, &layers);
                    }
                }
                // 风刃到了才在落点卷一下
                if let Some(late) = age.checked_sub(BLADE_T / 2) {
                    if let Some((a, fr)) = anim(f.show).and_then(|a| frame_at(a, late).map(|fr| (a, fr))) {
                        for to in &f.to {
                            drawn |= frame(ctx, &v, a, fr, *to);
                        }
                    }
                }
            }
            Show::Guard => {
                if age < LINK_T {
                    if let Some(me) = f.to.first() {
                        let layers: Vec<(f32, u32)> = LINK_WIDTHS.iter().copied().zip(LINK_COLOURS).collect();
                        drawn |= lines(ctx, &v, &[chest(*me), chest(f.at)], &layers);
                    }
                }
                if let Some((a, fr)) = anim(f.show).and_then(|a| frame_at(a, age).map(|fr| (a, fr))) {
                    drawn |= frame(ctx, &v, a, fr, f.at);
                }
            }
            Show::ShieldGlow => drawn |= ring(ctx, &v, &glow_ring(f.at, t), &glow_layers()),
            Show::HolyGlow => {
                let layers: Vec<(f32, u32)> = GLOW_WIDTHS.into_iter().zip(HOLY_COLOURS).collect();
                drawn |= ring(ctx, &v, &glow_ring(f.at, t), &layers);
            }
            Show::Hive => {
                if let Some(p) = hive_at(f, age) {
                    let layers: Vec<(f32, u32)> = HIVE_WIDTHS.into_iter().zip(HIVE_COLOURS).collect();
                    drawn |= ring(ctx, &v, &small_loop(p, 3.5, 3.0, 6), &layers);
                }
            }
            Show::Bees => {
                let layers: Vec<(f32, u32)> = BEE_WIDTHS.into_iter().zip(BEE_COLOURS).collect();
                for bee in bees_at(f, age) {
                    drawn |= ring(ctx, &v, &bee, &layers);
                }
            }
            Show::Blob => {
                let layers: Vec<(f32, u32)> = BLOB_WIDTHS.into_iter().zip(BLOB_COLOURS).collect();
                drawn |= ring(ctx, &v, &blob_ring(f.at, t), &layers);
            }
            Show::RingRed | Show::RingGold | Show::RingBlue | Show::RingPurple | Show::RingCyan | Show::RingGreen => {
                let (pts, k) = ring_at(f, age);
                let layers: Vec<(f32, u32)> =
                    RING_WIDTHS.into_iter().zip(ring_colours(f.show)).map(|(w, c)| (w, fade(c, k))).collect();
                drawn |= ring(ctx, &v, &pts, &layers);
            }
            Show::Boomerang => {
                if let Some(p) = boomerang_at(f, age) {
                    let layers: Vec<(f32, u32)> = BLADE_WIDTHS.iter().copied().zip(BLADE_COLOURS).collect();
                    for arm in boomerang_blades(p, age) {
                        drawn |= ring(ctx, &v, &arm, &layers);
                    }
                }
            }
            Show::Tether => {
                if let Some(to) = f.to.first() {
                    let (a, b) = (chest(f.at), chest(*to));
                    let pts = [(a.0 as f32 + 0.5, a.1 as f32 + 0.5), (b.0 as f32 + 0.5, b.1 as f32 + 0.5)];
                    let layers: Vec<(f32, u32)> = TETHER_WIDTHS.into_iter().zip(TETHER_COLOURS).collect();
                    drawn |= ring(ctx, &v, &pts, &layers);
                }
            }
            Show::Trail => {
                if let Some(to) = f.to.first() {
                    let px = |p: (u64, u64)| (world::whole_px(p.0) as f32 + 0.5, world::whole_px(p.1) as f32);
                    drawn |= ring(ctx, &v, &[px(f.at), px(*to)], &trail_layers(f, age));
                }
            }
            show => {
                if let Some((a, fr)) = anim(show).and_then(|a| frame_at(a, age).map(|fr| (a, fr))) {
                    drawn |= frame(ctx, &v, a, fr, f.at);
                }
            }
        }
        if drawn && first_time(m, s, f.show) {
            if let Some(k) = counted("fx") {
                let at = v.map(f.at);
                wlog(format!("FX m={m} s={s} t={} on screen at {t}: {:?} at ({}, {}) -> ({:.0}, {:.0}) on the \"Game\" map, \
                              {} more place(s), z {}, sprites {} #{k}", f.tick, f.show, f.at.0, f.at.1, at.0, at.1,
                             f.to.len(), v.z, if v.sprites { "on" } else { "OFF" }));
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_effect_has_its_animation_on_the_sheet() {
        for s in ALL {
            let a = anim(s).unwrap_or_else(|| panic!("{s:?}: no {} on the sheet", anim_name(s)));
            assert!(a.frames > 0 && a.ticks > 0, "{s:?}");
        }
        // every animation on the sheet is somebody's
        for a in ANIMS {
            assert!(ALL.iter().any(|&s| anim_name(s) == a.name), "{} is nobody's", a.name);
        }
        // the laser's mark lasts until the strike, the comet lands at its delay
        let mark = anim(Show::LaserMark).unwrap();
        assert_eq!(length(mark), super::super::procs::LASER_DELAY);
        let comet = anim(Show::Comet).unwrap();
        assert_eq!(6 * comet.ticks as usize, super::super::procs::COMET_DELAY, "six frames of fall, then the blast");
        assert!(longest() >= length(comet));
    }

    #[test]
    fn the_runs_are_the_sheets_frames() {
        let r = runs().expect("fx_runs.bin reads");
        assert_eq!(r.frames.len(), ANIMS.len());
        for (a, f) in ANIMS.iter().zip(&r.frames) {
            assert_eq!(f.len(), a.frames as usize, "{}", a.name);
            for runs in f {
                assert!(!runs.is_empty(), "{}: an empty frame", a.name);
                for x in runs {
                    assert!((x[0] as u16 + x[2] as u16) <= a.w && (x[1] as u16) < a.h, "{}", a.name);
                }
            }
        }
        // a broken file is no file
        assert!(parse_runs(b"DFXR").is_none() && parse_runs(&RUNS_BIN[..RUNS_BIN.len() - 1]).is_none());
    }

    #[test]
    fn a_bolt_runs_from_one_to_the_other_and_is_the_same_every_time() {
        let (a, b) = ((100, 200), (160, 170));
        let p = bolt_path(a, b, 42);
        assert_eq!((p[0], *p.last().unwrap()), (a, b));
        assert_eq!(p, bolt_path(a, b, 42), "the screen's second run draws the same bolt");
        assert!((4..=10).contains(&p.len()));
        assert_eq!(bolt_path(a, a, 1), vec![a, a]);
        assert_eq!(bolt_layers(false), vec![(1.4, BOLT_COLOURS[2])]);
    }

    /// 护盾的光：罩住整个人（中心在脚底上面），首尾相接，跟着屏幕时钟轻轻一涨一缩；一条只放一步（下一步换到他的新位置）。
    #[test]
    fn the_shield_glow_rings_the_body_for_one_step() {
        let at = (500_000, 400_000);
        let (cx, cy) = (500.5, 400.0 - GLOW_UP);
        for t in [0, 9, 18, 27] {
            let r = glow_ring(at, t);
            let (a, b) = (r[0], *r.last().unwrap());
            assert!((a.0 - b.0).abs() < 0.01 && (a.1 - b.1).abs() < 0.01, "closed");
            for p in &r {
                let e = ((p.0 - cx) / GLOW_RX).powi(2) + ((p.1 - cy) / GLOW_RY).powi(2);
                assert!((0.85..1.15).contains(&e), "{t}: {p:?}");
            }
            // the feet inside it, the head too
            assert!(r.iter().any(|p| p.1 > 400.0) && r.iter().any(|p| p.1 < 400.0 - 30.0));
        }
        assert_ne!(glow_ring(at, 0), glow_ring(at, 9), "it breathes");
        let f = feed::Fx { m: 1, s: 1, tick: 10, show: Show::ShieldGlow, at, to: Vec::new(),
                           dur: super::super::procs::EVERY as u16 };
        assert_eq!(ticks(&f), super::super::procs::EVERY);
        assert!(anim(Show::ShieldGlow).is_none(), "drawn as lines, not on the sheet");
    }

    #[test]
    fn what_flies_goes_from_the_caster_to_the_target() {
        let f = feed::Fx { m: 1, s: 1, tick: 100, show: Show::Snowball, at: (100_000, 500_000), to: vec![(180_000, 500_000)],
                           dur: 36 };
        let start = flight(&f, 0).unwrap();
        let mid = flight(&f, 18).unwrap();
        let end = flight(&f, 36).unwrap();
        assert_eq!(start.0, 100_000);
        assert_eq!(end.0, 180_000);
        // the snowball arcs: higher (smaller y) halfway than at either end
        assert!(mid.1 < start.1 && mid.1 < end.1);
        assert_eq!(start.1, end.1);
        assert!(flight(&f, 37).is_none());
        assert_eq!(ticks(&f), 36);
        // a missile flies at chest height, straight
        let m = feed::Fx { show: Show::Missile, dur: 10, ..f.clone() };
        assert_eq!(flight(&m, 5).unwrap().1, 500_000 - CHEST as u64 * 1000);
        // a blade is a third of the way, moving out
        let b0 = blade(f.at, f.to[0], 0).unwrap();
        let b1 = blade(f.at, f.to[0], 6).unwrap();
        assert!(b1[0].0 > b0[0].0 && blade(f.at, f.to[0], BLADE_T).is_none());
    }
}
