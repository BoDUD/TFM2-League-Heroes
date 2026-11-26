//! 本包战场特效在 `effects/league_hextech_fx#sheet.png` 上的位置。
//! tools/art/hextech_fx.py 生成，别手改。

/// 一段动画：帧从 (`x`, `y`) 往右排，一行 `per_row` 帧，每帧 `w` x `h`；(`ax`, `ay`) 是放在发生地点（英雄脚下）的那一点；
/// 一帧停 `ticks` 个模拟 tick。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Anim {
    pub name: &'static str,
    pub x: u16,
    pub y: u16,
    pub w: u16,
    pub h: u16,
    pub frames: u8,
    pub per_row: u8,
    pub ax: u16,
    pub ay: u16,
    pub ticks: u8,
}

/// 图的大小（像素）。
pub const SHEET: (u16, u16) = (704, 1328);

pub const ANIMS: [Anim; 29] = [
    Anim { name: "burn", x: 0, y: 0, w: 20, h: 26, frames: 6, per_row: 6, ax: 10, ay: 24, ticks: 4 },
    Anim { name: "frost", x: 0, y: 26, w: 34, h: 34, frames: 6, per_row: 6, ax: 17, ay: 30, ticks: 4 },
    Anim { name: "light_pop", x: 0, y: 60, w: 32, h: 32, frames: 5, per_row: 5, ax: 16, ay: 26, ticks: 3 },
    Anim { name: "escape", x: 0, y: 92, w: 40, h: 48, frames: 8, per_row: 8, ax: 20, ay: 44, ticks: 4 },
    Anim { name: "grow", x: 0, y: 140, w: 44, h: 52, frames: 8, per_row: 8, ax: 22, ay: 48, ticks: 4 },
    Anim { name: "punch", x: 0, y: 192, w: 24, h: 24, frames: 5, per_row: 5, ax: 12, ay: 20, ticks: 3 },
    Anim { name: "heavy", x: 0, y: 216, w: 34, h: 30, frames: 5, per_row: 5, ax: 17, ay: 25, ticks: 3 },
    Anim { name: "missile", x: 0, y: 246, w: 16, h: 16, frames: 4, per_row: 4, ax: 8, ay: 8, ticks: 3 },
    Anim { name: "missile_pop", x: 0, y: 262, w: 28, h: 28, frames: 5, per_row: 5, ax: 14, ay: 22, ticks: 3 },
    Anim { name: "spark", x: 0, y: 290, w: 30, h: 30, frames: 5, per_row: 5, ax: 15, ay: 23, ticks: 3 },
    Anim { name: "crack", x: 0, y: 320, w: 24, h: 50, frames: 6, per_row: 6, ax: 12, ay: 46, ticks: 4 },
    Anim { name: "ether", x: 0, y: 370, w: 36, h: 32, frames: 5, per_row: 5, ax: 18, ay: 27, ticks: 3 },
    Anim { name: "stone", x: 0, y: 402, w: 40, h: 46, frames: 7, per_row: 7, ax: 20, ay: 42, ticks: 4 },
    Anim { name: "execute", x: 0, y: 448, w: 32, h: 32, frames: 5, per_row: 5, ax: 16, ay: 27, ticks: 3 },
    Anim { name: "dawn", x: 0, y: 480, w: 36, h: 72, frames: 8, per_row: 8, ax: 18, ay: 67, ticks: 4 },
    Anim { name: "excited", x: 0, y: 552, w: 40, h: 48, frames: 7, per_row: 7, ax: 20, ay: 44, ticks: 4 },
    Anim { name: "guard", x: 0, y: 600, w: 30, h: 44, frames: 7, per_row: 7, ax: 15, ay: 40, ticks: 4 },
    Anim { name: "wisp", x: 0, y: 644, w: 16, h: 32, frames: 6, per_row: 6, ax: 8, ay: 29, ticks: 4 },
    Anim { name: "laser_mark", x: 0, y: 676, w: 48, h: 26, frames: 9, per_row: 9, ax: 24, ay: 13, ticks: 5 },
    Anim { name: "laser", x: 0, y: 702, w: 44, h: 160, frames: 8, per_row: 8, ax: 22, ay: 151, ticks: 3 },
    Anim { name: "comet", x: 0, y: 862, w: 64, h: 120, frames: 11, per_row: 11, ax: 32, ay: 106, ticks: 5 },
    Anim { name: "final_form", x: 0, y: 982, w: 56, h: 64, frames: 8, per_row: 8, ax: 28, ay: 59, ticks: 4 },
    Anim { name: "snowball", x: 0, y: 1046, w: 22, h: 22, frames: 4, per_row: 4, ax: 11, ay: 11, ticks: 4 },
    Anim { name: "snow_burst", x: 0, y: 1068, w: 60, h: 48, frames: 7, per_row: 7, ax: 30, ay: 38, ticks: 4 },
    Anim { name: "quantum", x: 0, y: 1116, w: 68, h: 40, frames: 6, per_row: 6, ax: 34, ay: 24, ticks: 3 },
    Anim { name: "undying", x: 0, y: 1156, w: 56, h: 60, frames: 8, per_row: 8, ax: 28, ay: 54, ticks: 5 },
    Anim { name: "immolate", x: 0, y: 1216, w: 56, h: 34, frames: 5, per_row: 5, ax: 28, ay: 22, ticks: 3 },
    Anim { name: "gust", x: 0, y: 1250, w: 26, h: 26, frames: 4, per_row: 4, ax: 13, ay: 20, ticks: 3 },
    Anim { name: "ward", x: 0, y: 1276, w: 44, h: 50, frames: 8, per_row: 8, ax: 22, ay: 46, ticks: 4 },
];
