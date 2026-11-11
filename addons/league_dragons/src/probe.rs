//! 画法校准（`settings.ini` 里加一行 `world_probe = 1`；每场比赛头 30 秒）。
//!
//! 往比赛世界里画东西是照反汇编推出来的，哪一种画法在这个版本的游戏里真的显示得出来，只有看画面才知道：2026-11-11
//! 装了 0.4.1 的那一局，日志里四种特效都「画了」（`draw_rect` 都返回 true，坐标都在镜头里），玩家：「没看到特效啊」。
//! 所以把几种画法各画一个颜色不同的方块，排在镜头中心上面一排，玩家截一张图就知道哪一种看得见、位置对不对：
//!
//! | 方块 | 画法 |
//! |---|---|
//! | A 红 | `"Game"`，post_render，排在游戏的命令后面（世界的平移外面，自己加平移），z 101——0.4.1 的画法 |
//! | B 橙 | 同 A，z 1（游戏自己的技能特效那一层）——0.4.2 的画法 |
//! | C 黄 | `"Game"`，post_render，推进去之后把世界的「恢复」挪到它后面：它就在世界的平移里面，和游戏自己的命令一样 |
//! | D 绿 | `"Game"`，pre_render（排在游戏的命令前面），用上一帧的平移 |
//! | E 青 | 同 D，前面先推一条和游戏一样的镜头命令 |
//! | F 蓝 | `"UI"`（模组画得出来的那一层），自己把世界坐标换成屏幕坐标 |
//!
//! B、C、D 下面各有一张本包特效图里的贴图（看贴图画不画得出来）；`"UI"` 上还有一张（图例右边）。白框是按 F 的换算每个
//! 方块应该在的位置，白十字是屏幕中心，两个大白框是两边的水晶（看换算对不对）。日志 `PROBE` 行写下每个数。

use std::sync::{Mutex, OnceLock};

use mod_api_stable::*;

use super::fx_atlas::ANIMS;
use super::screen::{draw_text_in, FONT, UI};
use super::world::{self, View, GAME};
use super::{counted, wlog};

/// 每场比赛头这么多 tick 画（30 秒）。
pub const PROBE_T: usize = 1800;
/// 方块的边、相邻两个的间隔、在镜头中心上面多高、贴图在方块下面多远（世界像素）。
const SIDE: f32 = 24.0;
const GAP: f32 = 56.0;
const UP: f32 = 110.0;
const BELOW: f32 = 84.0;

const RED: u32 = 0xff_28_28_ff;
const ORANGE: u32 = 0xff_96_20_ff;
const YELLOW: u32 = 0xff_f0_30_ff;
const GREEN: u32 = 0x30_e0_50_ff;
const CYAN: u32 = 0x30_e0_ff_ff;
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

/// 上一帧 post_render 读到的世界（pre_render 用）和这一帧 pre_render 画了什么（日志用）。
static LAST: Mutex<Option<((u64, u64), View)>> = Mutex::new(None);
static BEFORE: Mutex<String> = Mutex::new(String::new());
static FRAMES: Mutex<((u64, u64), usize)> = Mutex::new(((0, 0), 0));

/// 第 `k` 个方块左上角的世界像素：镜头中心上面一排，`k` = 0 在正中。
pub fn place(v: &View, k: i32) -> Option<(f32, f32)> {
    let cam = v.camera?;
    let centre = (cam.0 + cam.2 / 2.0 - v.shift.0, cam.1 + cam.3 / 2.0 - v.shift.1);
    Some(((centre.0 + k as f32 * GAP - SIDE / 2.0).round(), (centre.1 - UP - SIDE / 2.0).round()))
}

/// 世界像素 -> `"UI"` 里的坐标：镜头看着的那一块按宽铺满屏幕，上下居中裁掉（`ui` 是 `"UI"` 的大小）。
pub fn to_ui(v: &View, ui: (f32, f32), world: (f32, f32)) -> Option<(f32, f32, f32)> {
    let cam = v.camera.filter(|c| c.2 > 0.0)?;
    let k = ui.0 / cam.2;
    let map = v.px(world);
    Some(((map.0 - cam.0) * k, ui.1 / 2.0 + (map.1 - (cam.1 + cam.3 / 2.0)) * k, k))
}

/// 本包特效图里的一帧（拿到龙魂的光柱）：(UV, 锚点)。
fn picture() -> Option<((f32, f32, f32, f32), (f32, f32))> {
    let a = ANIMS.iter().find(|a| a.name == "soul_infernal")?;
    Some(world::uv_of(a, a.frames as usize / 2))
}

fn sprite(ctx: &mut StableClient<'_>, map: &str, at: (f32, f32), z: i32) -> bool {
    let Some((uv, pivot)) = picture() else { return false };
    ctx.draw_sprite(map, world::SHEET_TEX, &StableSpriteParams {
        x: at.0,
        y: at.1,
        z,
        pivot_x: pivot.0,
        pivot_y: pivot.1,
        uv,
        sample_nearest: true,
        ..StableSpriteParams::default()
    })
}

/// 一个空心的框（`"UI"`）。
fn outline(ctx: &mut StableClient<'_>, r: (f32, f32, f32, f32), z: i32, colour: u32) {
    let t = 2.0;
    ctx.draw_rect(UI, r.0, r.1, r.2, t, z, 0.0, colour);
    ctx.draw_rect(UI, r.0, r.1 + r.3 - t, r.2, t, z, 0.0, colour);
    ctx.draw_rect(UI, r.0, r.1, t, r.3, z, 0.0, colour);
    ctx.draw_rect(UI, r.0 + r.2 - t, r.1, t, r.3, z, 0.0, colour);
}

/// pre_render 里：D、E 两个方块（上一帧的世界）。
pub fn before(ctx: &mut StableClient<'_>, m: u64, s: u64, t: usize) {
    if !on() || t >= PROBE_T {
        return;
    }
    let Some(v) = LAST.lock().ok().and_then(|l| l.filter(|x| x.0 == (m, s)).map(|x| x.1)) else { return };
    let (Some(d), Some(e), Some(cam)) = (place(&v, 0), place(&v, 1), v.camera) else { return };
    let (dm, em) = (v.px(d), v.px(e));
    let d_ok = ctx.draw_rect(GAME, dm.0, dm.1, SIDE, SIDE, 1, 0.0, GREEN);
    let d_pic = sprite(ctx, GAME, (dm.0 + SIDE / 2.0, dm.1 + SIDE + BELOW), 1);
    let cam_ok = ctx.draw_set_camera(GAME, cam.0 + cam.2 / 2.0, cam.1 + cam.3 / 2.0, cam.2, cam.3);
    let e_ok = ctx.draw_rect(GAME, em.0, em.1, SIDE, SIDE, 1, 0.0, CYAN);
    if let Ok(mut b) = BEFORE.lock() {
        *b = format!("D map ({:.1}, {:.1}) {d_ok} picture {d_pic}; camera {cam_ok}; E map ({:.1}, {:.1}) {e_ok}", dm.0, dm.1, em.0,
                     em.1);
    }
}

/// post_render 里（本包别的东西之前）：C（挪进世界里）、A、B、F，图例，日志。
pub fn after(ctx: &mut StableClient<'_>, m: u64, s: u64, t: usize) {
    if !on() || t >= PROBE_T {
        return;
    }
    let Some(v) = world::view(ctx, m, s, t) else { return };
    if let Ok(mut l) = LAST.lock() {
        *l = Some(((m, s), v));
    }
    let (Some(a), Some(b), Some(c), Some(f)) = (place(&v, -3), place(&v, -2), place(&v, -1), place(&v, 2)) else { return };
    // C first - straight after the world's pop - in the world's own coordinates, then the pop moved behind it
    let c_ok = ctx.draw_rect(GAME, c.0, c.1, SIDE, SIDE, 1, 0.0, YELLOW);
    let c_pic = sprite(ctx, GAME, (c.0 + SIDE / 2.0, c.1 + SIDE + BELOW), 1);
    let moved = match (c_ok, c_pic) {
        (true, true) => world::move_into_world(ctx, 2),
        (true, false) => world::move_into_world(ctx, 1),
        _ => Err("the square was not taken".to_string()),
    };
    // A, B after the pop: the game's shift added
    let (am, bm) = (v.px(a), v.px(b));
    let a_ok = ctx.draw_rect(GAME, am.0, am.1, SIDE, SIDE, 101, 0.0, RED);
    let b_ok = ctx.draw_rect(GAME, bm.0, bm.1, SIDE, SIDE, 1, 0.0, ORANGE);
    let b_pic = sprite(ctx, GAME, (bm.0 + SIDE / 2.0, bm.1 + SIDE + BELOW), 1);
    // the UI map: F, where every square should be, the screen's centre, the two nexuses, the legend
    let Some(ui) = ctx.draw_map_size(UI).filter(|s| s.0 > 0.0 && s.1 > 0.0) else { return };
    let mut f_at = (0.0, 0.0, 0.0);
    if let Some(p) = to_ui(&v, ui, f) {
        f_at = p;
        ctx.draw_rect(UI, p.0, p.1, SIDE * p.2, SIDE * p.2, 950, 0.0, BLUE);
    }
    for k in -3..=1 {
        if let Some(p) = place(&v, k).and_then(|w| to_ui(&v, ui, w)) {
            outline(ctx, (p.0 - 4.0, p.1 - 4.0, SIDE * p.2 + 8.0, SIDE * p.2 + 8.0), 951, WHITE);
        }
    }
    ctx.draw_rect(UI, ui.0 / 2.0 - 30.0, ui.1 / 2.0 - 1.0, 60.0, 2.0, 951, 0.0, WHITE);
    ctx.draw_rect(UI, ui.0 / 2.0 - 1.0, ui.1 / 2.0 - 30.0, 2.0, 60.0, 951, 0.0, WHITE);
    for nexus in [(96.0, 864.0), (864.0, 96.0)] {
        if let Some(p) = to_ui(&v, ui, nexus) {
            outline(ctx, (p.0 - 50.0, p.1 - 50.0, 100.0, 100.0), 951, WHITE);
        }
    }
    let (lx, ly, lw) = (ui.0 / 2.0 - 380.0, 100.0, 760.0);
    ctx.draw_rect(UI, lx, ly, lw, 78.0, 948, 8.0, 0x10_14_22_e6);
    draw_text_in(ctx, "大小龙 · 画法校准（每局开头 30 秒）：请把这一屏截图发给 Claude", FONT, (lx + 14.0, ly + 4.0, lw - 28.0, 30.0), 949, 20.0,
                 WHITE, TextAlignXV1::Left);
    let chips = [("A", RED), ("B", ORANGE), ("C", YELLOW), ("D", GREEN), ("E", CYAN), ("F", BLUE)];
    for (i, (name, colour)) in chips.iter().enumerate() {
        let x = lx + 14.0 + i as f32 * 70.0;
        ctx.draw_rect(UI, x, ly + 44.0, 20.0, 20.0, 949, 0.0, *colour);
        draw_text_in(ctx, name, FONT, (x + 26.0, ly + 40.0, 30.0, 28.0), 949, 20.0, WHITE, TextAlignXV1::Left);
    }
    draw_text_in(ctx, "白框 = 方块该在的位置　G →", FONT, (lx + 440.0, ly + 40.0, 250.0, 28.0), 949, 18.0, WHITE, TextAlignXV1::Left);
    let g_pic = sprite(ctx, UI, (lx + lw - 40.0, ly + 74.0), 949);
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
            let before = BEFORE.lock().map(|b| b.clone()).unwrap_or_default();
            wlog(format!("PROBE m={m} s={s} screen t={t} frame {n}: camera {:?}, shift {:?}, UI {ui:?} (x{:.4}); C world ({}, {}) \
                          {c_ok} picture {c_pic} moved into the world {moved:?}; A map ({:.1}, {:.1}) z 101 {a_ok}; B map ({:.1}, \
                          {:.1}) z 1 {b_ok} picture {b_pic}; before the game's commands: [{before}]; F ui ({:.1}, {:.1}); G picture \
                          {g_pic}; the list starts [{}] #{k}",
                         v.camera, v.shift, f_at.2, c.0, c.1, am.0, am.1, bm.0, bm.1, f_at.0, f_at.1,
                         world::head(ctx, 5).join(" | ")));
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

    #[test]
    fn the_squares_sit_in_a_row_over_the_cameras_centre() {
        // the frame of the user's match: camera rect (512, 512, 1024, 1024), the world shifted by (904, 126)
        let v = View { scale: (1.0, 1.0), shift: (904.0, 126.0), z: 1, ground: -1, sprites: true,
                       camera: Some((512.0, 512.0, 1024.0, 1024.0)) };
        // the camera's centre in the world: (1024 - 904, 1024 - 126)
        assert_eq!(place(&v, 0), Some((120.0 - 12.0, 898.0 - 110.0 - 12.0)));
        assert_eq!(place(&v, -3).unwrap().0, 120.0 - 3.0 * 56.0 - 12.0);
        // on the UI map (1920 x 1080): the centre of the camera is the centre of the screen, a world pixel 1.875 of its
        let ui = (1920.0, 1080.0);
        assert_eq!(to_ui(&v, ui, (120.0, 898.0)), Some((960.0, 540.0, 1.875)));
        assert_eq!(to_ui(&v, ui, (120.0 + 64.0, 898.0 - 32.0)), Some((960.0 + 120.0, 540.0 - 60.0, 1.875)));
        // no camera read: no place
        assert_eq!(place(&View { camera: None, ..v }, 0), None);
        assert!(picture().is_some());
    }
}
