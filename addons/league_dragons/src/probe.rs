//! 画法校准（`settings.ini` 里加一行 `world_probe = 1`；每场比赛头 30 秒）。
//!
//! 往比赛世界里画东西是照反汇编推出来的，哪一种画法在这个版本的游戏里真的显示得出来、位置对不对，只有看画面才知道。
//! 所以把几种画法各画一个颜色不同的方块，排在镜头中心上面一排，下面各画一张本包的特效图，玩家截一张图就都清楚了：
//!
//! | 方块 | 画法 | 下面那张图 |
//! |---|---|---|
//! | A 红 | `"Game"`，排在游戏的命令后面（世界的平移外面，自己加平移），z 101 | 同一帧**一格一格**画（横条） |
//! | B 橙 | 同 A，z 1（游戏自己的技能特效那一层）——本包特效的画法 | 贴图 |
//! | C 黄 | `"Game"`，推进去之后把世界的「恢复」挪到它后面：在世界的平移里面，和游戏自己的命令一样 | 贴图 |
//! | F 蓝 | `"UI"`，自己把世界坐标换成屏幕坐标 | —— |
//!
//! 白框是按 F 的换算每个方块应该在的位置，白十字是每张图的脚（锚点）应该在的位置和屏幕中心；图例右边还有一张画在 `"UI"`
//! 上的贴图。日志 `PROBE` 行写下每个数。
//!
//! **第一次校准（2026-11-11，0.4.3，玩家的截图）定下来的事**：
//! - A、B、C 都显示、位置都对：排在游戏的命令后面、自己加平移的画法没有问题（z 101 和 z 1 都看得见）；挪进世界里也行，
//!   用不着。pre_render 里画的排在游戏的镜头命令前面，按另一个镜头画（1 : 1、不放大），前面先推一条一样的镜头命令就对了。
//! - 画面是 1 个世界像素 = 2 个屏幕像素：`"Game"` 那张 2048 × 2048 的图按原大小居中放在屏幕上，镜头看着的 1024 × 1024
//!   铺满它，所以屏幕上看得到的是镜头中心周围 960 × 540 个世界像素（当时的换算按 1.875 算，白框偏了）。
//! - **贴图画得出来**（`"Game"` 和 `"UI"` 上都是），但 `pivot` 不是接口文档说的「x、y 指的那一点」：给了锚点的比例，图的
//!   左上角落在 x、y **加**锚点的地方，整张图往右下偏了两个锚点。所以锚点自己减、`pivot` 给 0（[`world::sprite_top_left`]）。
//! - 上一局（0.4.1）特效看不见：那一局贴图关着，特效是一格一格画的——1 个世界像素高的横条在 `"Game"` 上几乎是透明的
//!   （这一版把它画在 A 下面，再看一眼）。

use std::sync::{Mutex, OnceLock};

use mod_api_stable::*;

use super::fx_atlas::{Anim, ANIMS};
use super::screen::{draw_text_in, FONT, UI};
use super::world::{self, View, GAME};
use super::{counted, wlog};

/// 每场比赛头这么多 tick 画（30 秒）。
pub const PROBE_T: usize = 1800;
/// 方块的边、相邻两个的间隔、在镜头中心上面多高、图的脚在方块下面多远（世界像素）。
const SIDE: f32 = 24.0;
const GAP: f32 = 80.0;
const UP: f32 = 120.0;
const BELOW: f32 = 96.0;

const RED: u32 = 0xff_28_28_ff;
const ORANGE: u32 = 0xff_96_20_ff;
const YELLOW: u32 = 0xff_f0_30_ff;
const BLUE: u32 = 0x40_68_ff_ff;
const WHITE: u32 = 0xff_ff_ff_ff;

/// `text`（settings.ini）里有没有 `world_probe = 1`（`#` 后面是说明）。
pub fn wanted(text: &str) -> bool {
    text.lines().any(|raw| {
        let line = raw.trim_start_matches('\u{feff}').split('#').next().unwrap_or("").trim();
        let mut kv = line.splitn(2, '=');
        kv.next().map(str::trim) == Some("world_probe") && kv.next().map(str::trim) == Some("1")
    })
}

/// 校准开着没有（加载后第一次问时读一次 settings.ini）。
pub fn on() -> bool {
    static ON: OnceLock<bool> = OnceLock::new();
    *ON.get_or_init(|| {
        let on = super::settings::dll_dir()
            .and_then(|d| std::fs::read(d.join("settings.ini")).ok())
            .is_some_and(|b| wanted(&String::from_utf8_lossy(&b)));
        if on {
            wlog("PROBE on: settings.ini has world_probe = 1 - the first 30 s of every match show the calibration squares \
                  (take the line out to stop them)");
        }
        on
    })
}

static FRAMES: Mutex<((u64, u64), usize)> = Mutex::new(((0, 0), 0));

/// 第 `k` 个方块左上角的世界像素：镜头中心上面一排，`k` = 0 在正中。
pub fn place(v: &View, k: i32) -> Option<(f32, f32)> {
    let cam = v.camera?;
    let centre = (cam.0 + cam.2 / 2.0 - v.shift.0, cam.1 + cam.3 / 2.0 - v.shift.1);
    Some(((centre.0 + k as f32 * GAP - SIDE / 2.0).round(), (centre.1 - UP - SIDE / 2.0).round()))
}

/// 世界像素 -> `"UI"` 里的坐标和一个世界像素是几个 `"UI"` 像素：`"Game"` 那张图（宽 `game`）按原大小居中放在屏幕上，镜头
/// 看着的那一块铺满它（`ui` 是 `"UI"` 的大小）。
pub fn to_ui(v: &View, game: f32, ui: (f32, f32), world: (f32, f32)) -> Option<(f32, f32, f32)> {
    let cam = v.camera.filter(|c| c.2 > 0.0)?;
    let k = game / cam.2;
    let map = v.px(world);
    Some((ui.0 / 2.0 + (map.0 - (cam.0 + cam.2 / 2.0)) * k, ui.1 / 2.0 + (map.1 - (cam.1 + cam.3 / 2.0)) * k, k))
}

/// 本包特效图里的一帧（拿到龙魂的光柱的中间一帧）。
fn picture() -> Option<(&'static Anim, usize)> {
    let a = ANIMS.iter().find(|a| a.name == "soul_infernal")?;
    Some((a, a.frames as usize / 2))
}

/// 那一帧一格一格画（横条），脚在世界像素 `feet`。-> 推进去几条。
fn squares(ctx: &mut StableClient<'_>, v: &View, feet: (f32, f32)) -> usize {
    let Some((a, fr)) = picture() else { return 0 };
    let Some(list) = ANIMS.iter().position(|x| x.name == a.name)
        .and_then(|i| super::fx::runs().and_then(|r| r.frames.get(i).and_then(|f| f.get(fr)).map(|l| (l, &r.colours))))
    else {
        return 0;
    };
    let (bx, by) = (feet.0.round() as i32 - a.ax as i32, feet.1.round() as i32 - a.ay as i32);
    list.0.iter().filter(|r| world::run(ctx, v, bx + r[0] as i32, by + r[1] as i32, r[2] as i32, list.1[r[3] as usize])).count()
}

/// 一个空心的框、一个十字（`"UI"`）。
fn outline(ctx: &mut StableClient<'_>, r: (f32, f32, f32, f32), z: i32, colour: u32) {
    let t = 2.0;
    ctx.draw_rect(UI, r.0, r.1, r.2, t, z, 0.0, colour);
    ctx.draw_rect(UI, r.0, r.1 + r.3 - t, r.2, t, z, 0.0, colour);
    ctx.draw_rect(UI, r.0, r.1, t, r.3, z, 0.0, colour);
    ctx.draw_rect(UI, r.0 + r.2 - t, r.1, t, r.3, z, 0.0, colour);
}

fn cross(ctx: &mut StableClient<'_>, at: (f32, f32), arm: f32, z: i32) {
    ctx.draw_rect(UI, at.0 - arm, at.1 - 1.0, arm * 2.0, 2.0, z, 0.0, WHITE);
    ctx.draw_rect(UI, at.0 - 1.0, at.1 - arm, 2.0, arm * 2.0, z, 0.0, WHITE);
}

/// post_render 里（本包别的东西之前）：C（挪进世界里）、A、B、F，各自的图，图例，日志。
pub fn after(ctx: &mut StableClient<'_>, m: u64, s: u64, t: usize) {
    if !on() || t >= PROBE_T {
        return;
    }
    let Some(v) = world::view(ctx, m, s, t) else { return };
    let (Some(a), Some(b), Some(c), Some(f), Some((anim, fr))) = (place(&v, -2), place(&v, -1), place(&v, 0), place(&v, 1), picture())
    else {
        return;
    };
    let feet = |sq: (f32, f32)| (sq.0 + SIDE / 2.0, sq.1 + SIDE + BELOW);
    let top_left = |p: (f32, f32)| (p.0 - anim.ax as f32, p.1 - anim.ay as f32);
    // C first - straight after the world's pop - in the world's own coordinates, then the pop moved behind it
    let c_ok = ctx.draw_rect(GAME, c.0, c.1, SIDE, SIDE, 1, 0.0, YELLOW);
    let cp = top_left(feet(c));
    let c_pic = world::sprite_top_left(ctx, GAME, 1, anim, fr, cp.0, cp.1);
    let moved = match (c_ok, c_pic) {
        (true, true) => world::move_into_world(ctx, 2),
        (true, false) => world::move_into_world(ctx, 1),
        _ => Err("the square was not taken".to_string()),
    };
    // A, B after the pop: the game's shift added. A's picture square by square, B's the sheet.
    let (am, bm) = (v.px(a), v.px(b));
    let a_ok = ctx.draw_rect(GAME, am.0, am.1, SIDE, SIDE, 101, 0.0, RED);
    let a_runs = squares(ctx, &v, feet(a));
    let b_ok = ctx.draw_rect(GAME, bm.0, bm.1, SIDE, SIDE, 1, 0.0, ORANGE);
    let bp = v.px(top_left(feet(b)));
    let b_pic = world::sprite_top_left(ctx, GAME, 1, anim, fr, bp.0, bp.1);
    // the UI map: F, where every square and every picture's feet should be, the screen's centre, the legend
    let (Some(ui), Some(game)) = (ctx.draw_map_size(UI).filter(|s| s.0 > 0.0 && s.1 > 0.0), ctx.draw_map_size(GAME)) else { return };
    let mut f_at = (0.0, 0.0, 0.0);
    if let Some(p) = to_ui(&v, game.0, ui, f) {
        f_at = p;
        ctx.draw_rect(UI, p.0, p.1, SIDE * p.2, SIDE * p.2, 950, 0.0, BLUE);
    }
    for sq in [a, b, c] {
        if let Some(p) = to_ui(&v, game.0, ui, sq) {
            outline(ctx, (p.0 - 4.0, p.1 - 4.0, SIDE * p.2 + 8.0, SIDE * p.2 + 8.0), 951, WHITE);
        }
        if let Some(p) = to_ui(&v, game.0, ui, feet(sq)) {
            cross(ctx, (p.0, p.1), 10.0, 951);
        }
    }
    cross(ctx, (ui.0 / 2.0, ui.1 / 2.0), 30.0, 951);
    let (lx, ly, lw) = (ui.0 / 2.0 - 380.0, 100.0, 760.0);
    ctx.draw_rect(UI, lx, ly, lw, 78.0, 948, 8.0, 0x10_14_22_e6);
    draw_text_in(ctx, "大小龙 · 画法校准（每局开头 30 秒）：请把这一屏截图发给 Claude", FONT, (lx + 14.0, ly + 4.0, lw - 28.0, 30.0), 949, 20.0,
                 WHITE, TextAlignXV1::Left);
    let chips = [("A", RED), ("B", ORANGE), ("C", YELLOW), ("F", BLUE)];
    for (i, (name, colour)) in chips.iter().enumerate() {
        let x = lx + 14.0 + i as f32 * 70.0;
        ctx.draw_rect(UI, x, ly + 44.0, 20.0, 20.0, 949, 0.0, *colour);
        draw_text_in(ctx, name, FONT, (x + 26.0, ly + 40.0, 30.0, 28.0), 949, 20.0, WHITE, TextAlignXV1::Left);
    }
    draw_text_in(ctx, "白框 / 白十字 = 方块和图的脚该在的位置　G →", FONT, (lx + 300.0, ly + 40.0, 400.0, 28.0), 949, 18.0, WHITE,
                 TextAlignXV1::Left);
    // G: the same picture on the UI map, its feet on the legend's lower right corner
    let g = (lx + lw - 30.0 - anim.ax as f32, ly + 76.0 - anim.ay as f32);
    let g_pic = world::sprite_top_left(ctx, UI, 949, anim, fr, g.0, g.1);
    // the log: the first frames of a match, then now and then
    let n = FRAMES.lock().map_or(0, |mut fr| {
        if fr.0 != (m, s) {
            *fr = ((m, s), 0);
        }
        fr.1 += 1;
        fr.1
    });
    if n <= 3 || n % 240 == 0 {
        if let Some(k) = counted("probe") {
            wlog(format!("PROBE m={m} s={s} screen t={t} frame {n}: camera {:?}, shift {:?}, Game {game:?}, UI {ui:?} (x{:.3}); C \
                          world ({}, {}) {c_ok} picture {c_pic} moved into the world {moved:?}; A map ({:.1}, {:.1}) z 101 {a_ok}, \
                          its picture in {a_runs} squares; B map ({:.1}, {:.1}) z 1 {b_ok} picture {b_pic} at ({:.1}, {:.1}); F ui \
                          ({:.1}, {:.1}); G picture {g_pic}; the list starts [{}] #{k}",
                         v.camera, v.shift, f_at.2, c.0, c.1, am.0, am.1, bm.0, bm.1, bp.0, bp.1, f_at.0, f_at.1,
                         world::head(ctx, 3).join(" | ")));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_switch_is_a_line_of_the_settings_file() {
        assert!(wanted("elder_buff_seconds = 90\nworld_probe = 1\n"));
        assert!(wanted("\u{feff}world_probe=1 # the calibration squares"));
        assert!(!wanted("world_probe = 0") && !wanted("# world_probe = 1") && !wanted("world_probes = 1") && !wanted(""));
    }

    /// The numbers of the user's screenshot (2026-11-11, 0.4.3): the red square pushed at map (844, 902) showed with its
    /// left edge at screen x 600 and its top at 292 - two screen pixels a world pixel, the camera's centre the screen's.
    #[test]
    fn a_world_pixel_is_two_of_the_screens() {
        let v = View { scale: (1.0, 1.0), shift: (904.0, 85.0), z: 1, ground: -1, sprites: true,
                       camera: Some((512.0, 512.0, 1024.0, 1024.0)) };
        let (game, ui) = (2048.0, (1920.0, 1080.0));
        // the camera's centre in the world: (1024 - 904, 1024 - 85)
        assert_eq!(to_ui(&v, game, ui, (120.0, 939.0)), Some((960.0, 540.0, 2.0)));
        // that square: world (844 - 904, 902 - 85)
        assert_eq!(to_ui(&v, game, ui, (-60.0, 817.0)), Some((600.0, 296.0, 2.0)));
        // the squares in a row over the centre, the pictures' feet under them
        assert_eq!(place(&v, 0), Some((120.0 - 12.0, 939.0 - 120.0 - 12.0)));
        assert_eq!(place(&v, -2).unwrap().0, 120.0 - 160.0 - 12.0);
        assert_eq!(place(&View { camera: None, ..v }, 0), None);
        assert!(picture().is_some());
    }
}
