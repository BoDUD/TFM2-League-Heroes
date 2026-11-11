//! 特效预览（`settings.ini` 里加一行 `world_probe = 1`；每场比赛头 30 秒）：本包的每一种战场特效在镜头中心排成两排循环
//! 播放，下面写着名字——不用等到有队伍拿龙魂就能看到它们长什么样、位置对不对。默认不开。
//!
//! 这个开关原来是**画法校准**。往比赛世界里画东西是照反汇编推出来的，哪一种画法真的显示得出来、位置对不对，只有看
//! 画面才知道，所以 0.4.3 把几种画法各画一个颜色不同的方块、各带一张本包的图，让玩家截图。两张截图（2026-11-11）定下来的：
//!
//! - **排在游戏的命令后面、自己加平移的画法没有问题**：z 101 和 z 1 的方块都显示、位置都对。把世界的「恢复」挪到刚推进去
//!   的命令后面（它们就在世界的平移里面，和游戏自己的命令一样）也行，用不着。pre_render 里画的排在游戏的镜头命令前面，
//!   按另一个镜头画（1 : 1、不放大），前面先推一条和游戏一样的镜头命令就对了。
//! - **1 个世界像素 = 2 个屏幕像素**：`"Game"` 那张 2048 × 2048 的图按原大小居中放在屏幕上，镜头看着的 1024 × 1024 铺满
//!   它，屏幕上看得到镜头中心周围 960 × 540 个世界像素（推在 (852, 892.3) 的方块左上角正好在屏幕的 (616, 276.6)）。
//!   [`to_ui`] 就是这个换算。
//! - **贴图画得出来**（`"Game"` 和 `"UI"` 上都是），但 `pivot` 不是接口文档说的「x、y 指的那一点」：给了锚点的比例，图的
//!   左上角落在 x、y **加**锚点的地方，整张图往右下偏两个锚点。锚点自己减、`pivot` 给 0（[`world::sprite_top_left`]）之后，
//!   第二张截图里三张图的脚都踩在该在的十字上。
//! - **一格一格画（横条）也显示得好好的**：第二张截图里同一帧用 701 条横条画出来，和贴图一样实。（0.4.4 的说明里猜过
//!   「1 个世界像素高的横条几乎是透明的」，错了。）所以装了 0.4.1 的那一局玩家「没看到特效啊」不是画不出来——四种特效
//!   日志里都画了，位置也在镜头里；是没注意到（每个不到一秒），还是别的原因，没有定论。

use std::sync::{Mutex, OnceLock};

use mod_api_stable::*;

use super::fx_atlas::{Anim, ANIMS};
use super::screen::{draw_text_in, FONT, UI};
use super::world::{self, View, GAME};
use super::{counted, fx, wlog};

/// 每场比赛头这么多 tick 画（30 秒）。
pub const PROBE_T: usize = 1800;
/// 一段动画放完后歇这么多 tick 再放。
const REST: usize = 36;
/// 两排：(动画, 名字)。上面一排是拿到龙魂时每个英雄脚下的光柱，下面一排是龙魂触发和远古龙之力。
const SOULS: [(&str, &str); 6] = [("soul_infernal", "炼狱龙魂"), ("soul_mountain", "山脉龙魂"), ("soul_ocean", "海洋龙魂"),
                                  ("soul_cloud", "云端龙魂"), ("soul_hextech", "海克斯龙魂"), ("soul_chemtech", "化学科技龙魂")];
const PROCS: [(&str, &str); 8] = [("infernal_blast", "炼狱：爆炸"), ("mountain_shield", "山脉：护盾"), ("ocean_heal", "海洋：回血"),
                                  ("cloud_gust", "云端：加速"), ("hex_spark", "海克斯：闪电"), ("chem_rage", "化学：残血"),
                                  ("elder_burn", "远古龙：点燃"), ("elder_execute", "远古龙：斩杀")];
/// 一排里相邻两个隔多远、两排的脚各在镜头中心上面 / 下面多远（世界像素）。
const GAP: f32 = 84.0;
const SOULS_UP: f32 = 50.0;
const PROCS_DOWN: f32 = 118.0;

const WHITE: u32 = 0xff_ff_ff_ff;

/// `text`（settings.ini）里有没有 `world_probe = 1`（`#` 后面是说明）。
pub fn wanted(text: &str) -> bool {
    text.lines().any(|raw| {
        let line = raw.trim_start_matches('\u{feff}').split('#').next().unwrap_or("").trim();
        let mut kv = line.splitn(2, '=');
        kv.next().map(str::trim) == Some("world_probe") && kv.next().map(str::trim) == Some("1")
    })
}

/// 预览开着没有（加载后第一次问时读一次 settings.ini）。
pub fn on() -> bool {
    static ON: OnceLock<bool> = OnceLock::new();
    *ON.get_or_init(|| {
        let on = super::settings::dll_dir()
            .and_then(|d| std::fs::read(d.join("settings.ini")).ok())
            .is_some_and(|b| wanted(&String::from_utf8_lossy(&b)));
        if on {
            wlog("PROBE on: settings.ini has world_probe = 1 - the first 30 s of every match show every effect of this mod in \
                  two rows (take the line out to stop it)");
        }
        on
    })
}

static FRAMES: Mutex<((u64, u64), usize)> = Mutex::new(((0, 0), 0));

/// 镜头中心的世界像素。
pub fn centre(v: &View) -> Option<(f32, f32)> {
    let cam = v.camera?;
    Some((cam.0 + cam.2 / 2.0 - v.shift.0, cam.1 + cam.3 / 2.0 - v.shift.1))
}

/// 一排 `n` 个里第 `i` 个的脚：镜头中心左右排开，`dy` 是在中心下面多远。
pub fn slot(centre: (f32, f32), i: usize, n: usize, dy: f32) -> (f32, f32) {
    ((centre.0 + (i as f32 - (n as f32 - 1.0) / 2.0) * GAP).round(), (centre.1 + dy).round())
}

/// 世界像素 -> `"UI"` 里的坐标和一个世界像素是几个 `"UI"` 像素：`"Game"` 那张图（宽 `game`）按原大小居中放在屏幕上，镜头
/// 看着的那一块铺满它（`ui` 是 `"UI"` 的大小）。
pub fn to_ui(v: &View, game: f32, ui: (f32, f32), world: (f32, f32)) -> Option<(f32, f32, f32)> {
    let cam = v.camera.filter(|c| c.2 > 0.0)?;
    let k = game / cam.2;
    let map = v.px(world);
    Some((ui.0 / 2.0 + (map.0 - (cam.0 + cam.2 / 2.0)) * k, ui.1 / 2.0 + (map.1 - (cam.1 + cam.3 / 2.0)) * k, k))
}

/// 循环播放的动画在 tick `t` 是第几帧（第 `i` 个错开一点，不一起闪）；放完到再放之间：None。
pub fn looping(a: &Anim, t: usize, i: usize) -> Option<usize> {
    let period = a.frames as usize * a.ticks.max(1) as usize + REST;
    fx::frame_at(a, (t + i * 11) % period)
}

/// 一帧画在世界像素 `feet`（它的锚点）：贴图画得了就一条贴图命令，不然一条条横条。
fn picture(ctx: &mut StableClient<'_>, v: &View, a: &'static Anim, fr: usize, feet: (f32, f32)) -> bool {
    if v.sprites {
        let (x, y) = world::corner(a, v.px(feet));
        return world::sprite_top_left(ctx, GAME, v.z, a, fr, x, y);
    }
    let Some(list) = ANIMS.iter().position(|x| x.name == a.name)
        .and_then(|i| fx::runs().and_then(|r| r.frames.get(i).and_then(|f| f.get(fr)).map(|l| (l, &r.colours))))
    else {
        return false;
    };
    let (bx, by) = (feet.0.round() as i32 - a.ax as i32, feet.1.round() as i32 - a.ay as i32);
    let mut drawn = false;
    for r in list.0 {
        drawn |= world::run(ctx, v, bx + r[0] as i32, by + r[1] as i32, r[2] as i32, list.1[r[3] as usize]);
    }
    drawn
}

/// post_render 里（本包别的东西之前）：两排特效、它们的名字、标题，日志。
pub fn after(ctx: &mut StableClient<'_>, m: u64, s: u64, t: usize) {
    if !on() || t >= PROBE_T {
        return;
    }
    let Some(v) = world::view(ctx, m, s, t) else { return };
    let (Some(c), Some(ui), Some(game)) = (centre(&v), ctx.draw_map_size(UI).filter(|s| s.0 > 0.0 && s.1 > 0.0), ctx.draw_map_size(GAME))
    else {
        return;
    };
    let mut drawn = 0usize;
    let rows: [(&[(&str, &str)], f32); 2] = [(&SOULS, -SOULS_UP), (&PROCS, PROCS_DOWN)];
    for (row, dy) in rows {
        for (i, (name, label)) in row.iter().enumerate() {
            let Some(a) = ANIMS.iter().find(|a| a.name == *name) else { continue };
            let feet = slot(c, i, row.len(), dy);
            // the Hextech soul's bolt runs into its spark from the left, a new shape every 3 ticks
            if *name == "hex_spark" && looping(a, t, i).is_some() {
                let (x, y) = (feet.0 as i32, feet.1 as i32 - 14);
                fx::bolt(ctx, &v, &fx::bolt_path((x - 64, y - 26), (x, y), (t / 3) as u64), true);
            }
            if let Some(fr) = looping(a, t, i) {
                drawn += picture(ctx, &v, a, fr, feet) as usize;
            }
            if let Some(p) = to_ui(&v, game.0, ui, feet) {
                ctx.draw_rect(UI, p.0 - 58.0, p.1 + 8.0, 116.0, 24.0, 948, 6.0, 0x10_14_22_c8);
                draw_text_in(ctx, label, FONT, (p.0 - 58.0, p.1 + 8.0, 116.0, 24.0), 949, 15.0, WHITE, TextAlignXV1::Center);
            }
        }
    }
    let (lx, ly, lw) = (ui.0 / 2.0 - 400.0, 100.0, 800.0);
    ctx.draw_rect(UI, lx, ly, lw, 64.0, 948, 8.0, 0x10_14_22_e6);
    draw_text_in(ctx, "大小龙 · 特效预览（每局开头 30 秒）", FONT, (lx + 14.0, ly + 2.0, lw - 28.0, 30.0), 949, 20.0, WHITE, TextAlignXV1::Center);
    draw_text_in(ctx, "上排：拿到龙魂时每个英雄脚下升起的光柱　下排：龙魂触发、远古龙之力", FONT, (lx + 14.0, ly + 32.0, lw - 28.0, 26.0), 949,
                 16.0, 0xd8_e0_f0_ff, TextAlignXV1::Center);
    // the log: the first frames of a match, then now and then
    let n = FRAMES.lock().map_or(0, |mut fr| {
        if fr.0 != (m, s) {
            *fr = ((m, s), 0);
        }
        fr.1 += 1;
        fr.1
    });
    if n <= 2 || n % 300 == 0 {
        if let Some(k) = counted("probe") {
            wlog(format!("PROBE m={m} s={s} screen t={t} frame {n}: the preview - {drawn} of {} effects on show this frame (sprites \
                          {}), z {}; camera {:?}, shift {:?}, its centre in the world ({:.1}, {:.1}); Game {game:?}, UI {ui:?} #{k}",
                         SOULS.len() + PROCS.len(), if v.sprites { "on" } else { "OFF: square by square" }, v.z, v.camera, v.shift,
                         c.0, c.1));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_switch_is_a_line_of_the_settings_file() {
        assert!(wanted("elder_buff_seconds = 90\nworld_probe = 1\n"));
        assert!(wanted("\u{feff}world_probe=1 # the preview"));
        assert!(!wanted("world_probe = 0") && !wanted("# world_probe = 1") && !wanted("world_probes = 1") && !wanted(""));
    }

    /// The numbers of the user's screenshots (2026-11-11): a square pushed at map (852, 892.3) showed with its corner at
    /// screen (616, 276.6) - two screen pixels a world pixel, the camera's centre the screen's.
    #[test]
    fn a_world_pixel_is_two_of_the_screens() {
        let v = View { scale: (1.0, 1.0), shift: (904.0, 118.3), z: 1, ground: -1, sprites: true,
                       camera: Some((512.0, 512.0, 1024.0, 1024.0)) };
        let (game, ui) = (2048.0, (1920.0, 1080.0));
        let c = centre(&v).unwrap();
        assert_eq!(c, (120.0, 1024.0 - 118.3));
        assert_eq!(to_ui(&v, game, ui, c), Some((960.0, 540.0, 2.0)));
        let p = to_ui(&v, game, ui, (852.0 - 904.0, 892.3 - 118.3)).unwrap();
        assert!((p.0 - 616.0).abs() < 0.01 && (p.1 - 276.6).abs() < 0.01 && p.2 == 2.0, "{p:?}");
        assert_eq!(centre(&View { camera: None, ..v }), None);
    }

    #[test]
    fn every_effect_has_its_place_in_the_two_rows() {
        // every animation of an effect is on show, each once
        let mut names: Vec<&str> = SOULS.iter().chain(PROCS.iter()).map(|x| x.0).collect();
        for n in &names {
            assert!(ANIMS.iter().any(|a| a.name == *n), "{n}");
        }
        names.sort_unstable();
        names.dedup();
        assert_eq!(names.len(), SOULS.len() + PROCS.len(), "an effect twice");
        // the six souls' pillars and every effect a soul or the Elder's fire plays
        for a in ANIMS.iter().filter(|a| a.name.starts_with("soul_")) {
            assert!(SOULS.iter().any(|x| x.0 == a.name), "{}", a.name);
        }
        for n in ["infernal_blast", "mountain_shield", "ocean_heal", "cloud_gust", "hex_spark", "chem_rage", "elder_burn", "elder_execute"] {
            assert!(PROCS.iter().any(|x| x.0 == n), "{n}");
        }
        // the rows are centred on the camera and fit between the side panels (the screen shows 960 world pixels, the
        // panels leave about 650 of them)
        let c = (500.0, 400.0);
        assert_eq!(slot(c, 0, 6, -SOULS_UP), (500.0 - 2.5 * GAP, 350.0));
        assert_eq!(slot(c, 7, 8, PROCS_DOWN), (500.0 + 3.5 * GAP, 518.0));
        assert!(7.0 * GAP + 96.0 < 700.0);
        // an animation plays, rests, plays again; its neighbours not in step
        let a = ANIMS.iter().find(|a| a.name == "soul_ocean").unwrap();
        let len = a.frames as usize * a.ticks as usize;
        assert_eq!((looping(a, 0, 0), looping(a, len - 1, 0), looping(a, len, 0)), (Some(0), Some(a.frames as usize - 1), None));
        assert_eq!(looping(a, len + REST, 0), Some(0));
        assert_ne!(looping(a, 0, 0), looping(a, 0, 1));
    }
}
