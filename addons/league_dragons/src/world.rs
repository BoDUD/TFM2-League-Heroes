//! 画在比赛世界里的东西（0.4.0，用户 2026-11-11：「拿了龙魂没有特效的 都要补 还有远古龙斩杀特效的」）：本包没有英雄，
//! 局内特效的名字（`play_view_effect`）却只认选上场的英雄数据里登记的那些，所以特效由客户端扩展自己画——接口给的绘图命令
//! 可以画进比赛自己的渲染层 `"Game"`（draw.rs：2048 x 2048 的比赛世界）。
//!
//! 难处是镜头。游戏每帧往 `"Game"` 推的命令是：镜头（永远看着 (1024, 1024)，宽高是缩放）、**平移**（1024 − 镜头中心）、
//! 世界里的所有东西（世界像素坐标，1 像素 = 模拟的 1000 个单位）、恢复。模组的命令排在这一对之外，平移管不到，接口也不给
//! 镜头在哪。所以 `post_render` 里先把游戏这一帧已经推进去的命令读出来（宿主的帧在它的状态 +0x80，帧 +0x78 是
//! 「渲染层名字 -> 命令表」），找到那条平移，自己加上去。这些是游戏内部的布局（0.7.2 的 EXE 里逐条指令核对过：宿主的
//! `draw_rect` / `draw_sprite` / `draw_set_camera` 和比赛画面的渲染函数），所以：
//!
//! - 全部用 `ReadProcessMemory` 读自己的进程，地址不对只是读不到，不会崩；
//! - 每一步都验（表头像不像哈希表、名字是不是 `Game`、命令表的长度、平移是不是正常的数、缩放是不是 1）；
//! - 认不出来就什么都不画，日志一行 `WORLD off`（写明卡在哪一步、看到了什么），玩法、公告、HUD 不受影响；
//! - 游戏自己的贴图命令的名字不是 `asset/…` 的样子时不画贴图（改成一格一格画）。
//!
//! 每场比赛日志两段 `WORLD`（第一帧、2 分钟时）：镜头、平移、世界里每个 z 上画的是什么（哪种命令几条、头一个名字）、头几条
//! 贴图命令、认不得的命令的原样，以后改画法、定层级照着它。本包的特效画在游戏世界里最高的 z 上面一层；躺在地上的东西
//! （[`View::ground`]）画在地图的墙那一层——同一个 z 上后推的画在上面，所以在墙和草丛上面、z 更高的单位下面。
//!
//! 0.4.1（用户 2026-11-11 装了 0.4.0 打的第一局，league_dragons.log 的 `WORLD`）：读是读对了——镜头 (512, 512, 1024, 1024)、
//! 平移 (904.0, 78.8)——但世界的范围认短了。有缩放的单位（防御塔、水晶、变大的英雄）在世界里各自再套一对平移 / 恢复
//! （比赛渲染函数 0x2809a22：单位的命令表头上插一条、尾上加一条），0.4.0 把头一个恢复当成了世界的结束，302 条命令只数了
//! 地图那 6 张图（z −3…1），于是特效画在 z 2、贴图也因为「没见到 `#sheet` 结尾的名字」关着。现在恢复按层数配对；z 按命令的
//! 种类取（[`z_at`]）；贴图不再要求见到 `#sheet`（地图的图名本来就没有这个结尾，引擎取图时自己补），名字找不到时引擎
//! 改按矢量图去找、不崩（0x24e7d0 / 0x24f590）。
//!
//! 0.4.2（同一天装了 0.4.1 的那一局，`WORLD first` / `WORLD later`）：范围对了（302 条全在里面）。世界的层：白底 −10、
//! 背景和草丛的影子 −3、墙的影子和单位脚下的圆影 −2、**墙、草丛、塔的影子、回城特效的后半 −1**、**单位（英雄、塔、小兵）0**、
//! **墙的前脸、塔的宝珠、技能特效（`asset/league/effects/…`）、回城特效的前半 1**、血条 3、增益图标 4–5、四个矩形 100。
//! 所以本包的特效照游戏自己的技能特效画在墙的前脸那一层（单位上面、血条下面），不再画到所有东西上面；躺在地上的画在
//! 墙那一层（和回城特效的后半一样）。另外有的贴图命令不是按名字指图的（血条里的色块：名字的位置上不是 String），0.4.1 把
//! 它们算成「名字不像样」又把贴图关了——现在读不出名字的不算。

use std::sync::Mutex;

use mod_api_stable::*;

use super::fx_atlas::{Anim, SHEET};
use super::{counted, wlog};

/// 比赛世界的渲染层。
pub const GAME: &str = "Game";
/// 一个世界像素是模拟的多少个单位。
pub const UNITS_PER_PX: f32 = 1000.0;
/// 本包的特效图（`effects/league_dragons_fx#sheet.png`，tools/art/dragons_soul_fx.py）。
pub const SHEET_TEX: &str = "asset/league_dragons/effects/league_dragons_fx#sheet";
pub const SHEET_FILE: &str = "league_dragons_fx#sheet.png";

// ---- 宿主的帧（游戏 0.7.2）
/// 宿主状态 -> 正在攒的这一帧（渲染钩子之外是 0）。
const STATE_FRAME: usize = 0x80;
/// 帧 -> `HashMap<String, Vec<命令>>`（hashbrown：控制字节指针、掩码、还能放几个、元素数）。
const FRAME_LISTS: usize = 0x78;
/// 一格：名字 String {容量, 指针, 长度}、命令表 Vec {容量, 指针, 长度}。
const BUCKET: usize = 0x30;
/// 一条命令。
pub const CMD: usize = 0xd0;
pub const TAG_CAMERA: u64 = 0x8000_0000_0000_0000;
pub const TAG_SPRITE: u64 = 0x8000_0000_0000_0003;
pub const TAG_RECT: u64 = 0x8000_0000_0000_000a;
pub const TAG_PUSH: u64 = 0x8000_0000_0000_0012;
pub const TAG_POP: u64 = 0x8000_0000_0000_0013;
/// 命令里的位置：镜头 / 平移的两个数，平移的缩放，贴图命令的名字、UV、坐标（z：[`z_at`]）。
const AT_XY: usize = 0x08;
const AT_WH: usize = 0x10;
const AT_PUSH_SCALE: usize = 0x24;
const AT_SPRITE_NAME: usize = 0x08;
const AT_SPRITE_UV: usize = 0x68;
const AT_SPRITE_XY: usize = 0x78;
/// 第一个字不带最高位的命令是「文字」（它的第一个字段是 String，别的种类的标记占着 String 容量取不到的值）：算第 7 种。
pub const KIND_TEXT: u8 = 0x07;
/// 认得的种类（镜头、贴图、平移、恢复、文字）：别的头两条（矩形头四条）原样写进日志。
const KNOWN: [u8; 5] = [0x00, 0x03, 0x12, 0x13, KIND_TEXT];
const KIND_RECT: u8 = 0x0a;
/// 名字也在 +8 的种类（矢量图、单位的图……）：写日志时读出来。
const NAMED: [u8; 3] = [0x02, 0x04, 0x06];
/// 地图的墙那张图、墙的前脸那张图的文件名（`wall_5v5`、`wall_5v5_front`；别的地图照这个样子起名的也认）。
pub fn is_wall(name: &str) -> bool {
    let file = name.rsplit('/').next().unwrap_or("");
    file.starts_with("wall_") && !file.ends_with("_front") && !file.contains("shadow")
}

pub fn is_wall_front(name: &str) -> bool {
    let file = name.rsplit('/').next().unwrap_or("");
    file.starts_with("wall_") && file.ends_with("_front")
}

/// 英雄的图（`…/champions/<英雄>#sheet`）。
pub fn is_champion(name: &str) -> bool {
    name.contains("/champions/")
}
/// 日志里最多记这么多个不同的 z。
const LAYERS: usize = 40;

/// 一条命令是哪一种：标记的最低一个字节；文字是 [`KIND_TEXT`]。
pub fn kind(tag: u64) -> u8 {
    if tag >> 63 == 0 {
        KIND_TEXT
    } else {
        tag as u8
    }
}

/// 一条命令的 z（i32）在哪：游戏排一张渲染层的命令时按种类到这些位置上取（0.7.2 的 0x1e6d90 里的跳转表 0x405004c，逐项
/// 抄的；贴图 0x80、矩形 0x68 和宿主的 `draw_sprite` / `draw_rect` 写的位置对得上）。没有 z 的种类（镜头、平移、恢复……）：None。
pub fn z_at(tag: u64) -> Option<usize> {
    match kind(tag) {
        0x02 | 0x04 => Some(0x88),
        0x03 | 0x06 => Some(0x80),
        0x05 => Some(0xa8),
        KIND_TEXT => Some(0xb8),
        0x08 => Some(0x3c),
        0x09 | 0x0d => Some(0x30),
        0x0a => Some(0x68),
        0x0b => Some(0x44),
        0x0c => Some(0x6c),
        0x0e => Some(0x64),
        _ => None,
    }
}
/// 一次读多少条命令；一张命令表最多认这么多条（再多就不是命令表了）。
const BLOCK: usize = 64;
/// 平时数的时候只读头这么多条贴图命令的名字（看游戏的贴图名长什么样、地图的墙在哪一层）。
const NAMES: usize = 48;
/// 写日志时别的有名字的种类最多读这么多条的名字。
const NAMES_FOR_LOG: usize = 600;
/// 每帧找平移只看命令表的头这么多条（别的模组在游戏之前推的再多也不会有这么多）。
const HEAD: usize = 4096;
const MOST: usize = 1 << 20;

/// 读内存（游戏进程里是 `ReadProcessMemory`，测试里是一块假的）。
pub trait Peek {
    fn read(&self, addr: usize, buf: &mut [u8]) -> bool;
}

/// 自己的进程。
pub struct Process;

#[cfg(windows)]
impl Peek for Process {
    fn read(&self, addr: usize, buf: &mut [u8]) -> bool {
        #[link(name = "kernel32")]
        extern "system" {
            fn GetCurrentProcess() -> isize;
            fn ReadProcessMemory(process: isize, base: *const std::ffi::c_void, buf: *mut std::ffi::c_void, size: usize,
                                 read: *mut usize) -> i32;
        }
        if buf.is_empty() {
            return true;
        }
        let mut got = 0usize;
        let ok = unsafe { ReadProcessMemory(GetCurrentProcess(), addr as *const _, buf.as_mut_ptr() as *mut _, buf.len(), &mut got) };
        ok != 0 && got == buf.len()
    }
}

#[cfg(not(windows))]
impl Peek for Process {
    fn read(&self, _addr: usize, _buf: &mut [u8]) -> bool {
        false
    }
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

fn bytes(p: &dyn Peek, addr: usize, n: usize) -> Option<Vec<u8>> {
    if !plausible(addr) || n > 64 << 20 {
        return None;
    }
    let mut v = vec![0u8; n];
    p.read(addr, &mut v).then_some(v)
}

fn u64_in(b: &[u8], at: usize) -> u64 {
    u64::from_le_bytes(b[at..at + 8].try_into().unwrap())
}

fn f32_in(b: &[u8], at: usize) -> f32 {
    f32::from_le_bytes(b[at..at + 4].try_into().unwrap())
}

fn i32_in(b: &[u8], at: usize) -> i32 {
    i32::from_le_bytes(b[at..at + 4].try_into().unwrap())
}

fn sane(v: f32, most: f32) -> bool {
    v.is_finite() && v.abs() <= most
}

/// 帧里 `"Game"` 那张命令表：(第一条的地址, 条数)。认不出来：卡在哪。
pub fn game_list(p: &dyn Peek, frame: usize) -> Result<(usize, usize), String> {
    let head = bytes(p, frame + FRAME_LISTS, 0x20).ok_or("the frame's table of render maps cannot be read")?;
    let (ctrl, mask, items) = (u64_in(&head, 0) as usize, u64_in(&head, 8) as usize, u64_in(&head, 0x18) as usize);
    if !plausible(ctrl) || mask >= 1 << 12 || (mask + 1) & mask != 0 || items == 0 || items > mask + 1 {
        return Err(format!("the frame's table of render maps looks wrong (ctrl {ctrl:#x}, mask {mask:#x}, {items} items)"));
    }
    let flags = bytes(p, ctrl, mask + 1).ok_or("the table's control bytes cannot be read")?;
    let mut names = Vec::new();
    for (i, f) in flags.iter().enumerate() {
        if f & 0x80 != 0 {
            continue;
        }
        let Some(b) = ctrl.checked_sub((i + 1) * BUCKET).and_then(|at| bytes(p, at, BUCKET)) else { continue };
        let (key, key_len) = (u64_in(&b, 8) as usize, u64_in(&b, 0x10) as usize);
        let (cap, list, n) = (u64_in(&b, 0x18) as usize, u64_in(&b, 0x20) as usize, u64_in(&b, 0x28) as usize);
        let Some(name) = (key_len <= 32).then(|| bytes(p, key, key_len)).flatten() else { continue };
        if name == GAME.as_bytes() {
            if n > cap || n > MOST || (n > 0 && !plausible(list)) {
                return Err(format!("the \"Game\" map's command list looks wrong ({n} of {cap} at {list:#x})"));
            }
            return Ok((list, n));
        }
        names.push(String::from_utf8_lossy(&name).into_owned());
    }
    Err(format!("no \"Game\" map among this frame's {} render maps {names:?}", names.len()))
}

/// 游戏这一帧的世界：平移那条命令在第几条、它的缩放和平移（世界像素 × 缩放 + 平移 = `"Game"` 里的坐标）、镜头的矩形
/// （左上角和宽高）、和它配对的恢复在第几条。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Scope {
    pub n: usize,
    pub push_at: usize,
    pub pop_at: Option<usize>,
    pub scale: (f32, f32),
    pub shift: (f32, f32),
    pub camera: Option<(f32, f32, f32, f32)>,
}

/// 在 `n` 条命令里找游戏的平移（第一条）；`to_pop`：接着找到**和它配对的**恢复（要数里面的命令时才用：那是整张表）。
/// 世界里面有缩放的单位各自再套一对平移 / 恢复，所以恢复按层数配。找不到、数不像样：说明看到了什么。
pub fn find_scope(p: &dyn Peek, list: usize, n: usize, to_pop: bool) -> Result<Scope, String> {
    let mut camera = None;
    let mut seen: Vec<u64> = Vec::new();
    let mut found: Option<Scope> = None;
    // transforms open inside the world's
    let mut depth = 0usize;
    let mut at = 0;
    while at < n {
        // every frame only the list's head is looked at: the game's transform is among its first commands
        if !to_pop && at >= HEAD {
            break;
        }
        let take = BLOCK.min(n - at);
        let block = bytes(p, list + at * CMD, take * CMD).ok_or_else(|| format!("commands {at}.. of {n} cannot be read"))?;
        for k in 0..take {
            let c = &block[k * CMD..(k + 1) * CMD];
            let tag = u64_in(c, 0);
            if seen.len() < 12 {
                seen.push(tag);
            }
            match (tag, &mut found) {
                (TAG_CAMERA, None) => {
                    let r = (f32_in(c, AT_XY), f32_in(c, AT_XY + 4), f32_in(c, AT_WH), f32_in(c, AT_WH + 4));
                    camera = [r.0, r.1, r.2, r.3].iter().all(|v| sane(*v, 1.0e5)).then_some(r);
                }
                (TAG_PUSH, None) => {
                    let shift = (f32_in(c, AT_XY), f32_in(c, AT_XY + 4));
                    let scale = (f32_in(c, AT_PUSH_SCALE), f32_in(c, AT_PUSH_SCALE + 4));
                    if !sane(shift.0, 1.0e5) || !sane(shift.1, 1.0e5) || !sane(scale.0, 64.0) || !sane(scale.1, 64.0) {
                        return Err(format!("the world's transform at command {} is no transform (shift {shift:?}, scale {scale:?})",
                                           at + k));
                    }
                    found = Some(Scope { n, push_at: at + k, pop_at: None, scale, shift, camera });
                    if !to_pop {
                        return Ok(found.unwrap());
                    }
                }
                (TAG_PUSH, Some(_)) => depth += 1,
                (TAG_POP, Some(s)) => {
                    if depth == 0 {
                        s.pop_at = Some(at + k);
                        return Ok(*s);
                    }
                    depth -= 1;
                }
                _ => {}
            }
        }
        at += take;
    }
    found.ok_or_else(|| {
        let tags: Vec<String> = seen.iter().map(|t| format!("{t:#x}")).collect();
        format!("no world transform among the \"Game\" map's {n} commands (they start {})", tags.join(" "))
    })
}

/// 世界里同一个 z 上的命令：几条、各种各几条、头一条有名字的命令的名字（写日志时才读）。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Layer {
    pub z: i32,
    pub n: usize,
    pub kinds: Vec<(u8, usize)>,
    pub name: Option<String>,
}

/// 一条贴图命令：名字、坐标、z、UV 的宽高。
pub type SpriteLine = (String, f32, f32, i32, f32, f32);

/// 游戏在世界里画的东西（平移和它配对的恢复之间的所有命令，套在里面的也算）。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Census {
    /// 有 z 的命令一共几条、z 的范围。
    pub drawn: usize,
    pub z: Option<(i32, i32)>,
    /// 每个 z 上有什么（z 从小到大，最多 [`LAYERS`] 个；再多的 z 上的命令只记条数）。
    pub layers: Vec<Layer>,
    pub beyond: usize,
    /// 各种命令各几条。
    pub kinds: Vec<(u8, usize)>,
    /// 世界里面又套的平移：几个、头几个的 (平移, 缩放)。
    pub pushes: usize,
    pub inner: Vec<((f32, f32), (f32, f32))>,
    /// 贴图命令（本包画贴图用的就是这一种）几条；其中不是按名字指图的几条（名字的位置上不是 String：血条里的色块）；
    /// 读得出的名字都以 `asset/` 开头（一个都读不出：false）。
    pub sprites: usize,
    pub nameless: usize,
    pub asset_names: bool,
    /// 地图的墙那张图（[`is_wall`]）、墙的前脸那张图（[`is_wall_front`]）、头一个英雄（[`is_champion`]）的 z。
    pub ground: Option<i32>,
    pub front: Option<i32>,
    pub units: Option<i32>,
    /// 头几条、最后几条贴图命令。
    pub first: Vec<SpriteLine>,
    pub last: Vec<SpriteLine>,
    /// 认不得的种类头两条的原样。
    pub raw: Vec<String>,
}

fn widen(r: &mut Option<(i32, i32)>, z: i32) {
    *r = Some(r.map_or((z, z), |(a, b)| (a.min(z), b.max(z))));
}

fn bump(v: &mut Vec<(u8, usize)>, kd: u8, most: usize) {
    match v.iter().position(|o| o.0 == kd) {
        Some(i) => v[i].1 += 1,
        None if v.len() < most => v.push((kd, 1)),
        None => {}
    }
}

/// `3 x6, 4 x140, text x2`。
pub fn kinds_text(v: &[(u8, usize)]) -> String {
    let all: Vec<String> = v.iter().map(|(k, n)| if *k == KIND_TEXT { format!("text x{n}") } else { format!("{k:x} x{n}") }).collect();
    all.join(", ")
}

/// 命令里 `at` 上的 String {容量, 指针, 长度} 读成字（不像 String、不是能看的字：None）。借来的字（容量位置上是标记）也认。
fn name_at(p: &dyn Peek, c: &[u8], at: usize) -> Option<String> {
    let (cap, ptr, len) = (u64_in(c, at), u64_in(c, at + 8) as usize, u64_in(c, at + 16) as usize);
    if len == 0 || len > 200 || (cap >> 63 == 0 && (cap as usize) < len) {
        return None;
    }
    let s = String::from_utf8(bytes(p, ptr, len)?).ok()?;
    s.chars().all(|ch| !ch.is_control()).then_some(s)
}

/// 一条认不得的命令的原样：26 个字（十六进制）和里面像 String 的东西。
fn raw_line(p: &dyn Peek, c: &[u8], kd: u8, i: usize, z: Option<i32>) -> String {
    let words: Vec<String> = (0..CMD / 8).map(|w| format!("{:x}", u64_in(c, w * 8))).collect();
    let strings: Vec<String> = (8..=CMD - 24).step_by(8)
        .filter_map(|at| name_at(p, c, at).map(|s| format!("+{at:#x} {s:?}")))
        .collect();
    format!("kind {kd:#x} #{i} (z {z:?}): words [{}]; strings [{}]", words.join(" "), strings.join(", "))
}

/// 数一遍世界里的命令（`keep`：头这么多条贴图命令留下来、每个 z 的头一个名字和认不得的命令的原样也读——写日志时用）。
pub fn census(p: &dyn Peek, list: usize, scope: &Scope, keep: usize) -> Census {
    let mut out = Census { asset_names: true, ..Census::default() };
    let end = scope.pop_at.unwrap_or(scope.n).min(scope.n);
    let mut raw_seen: Vec<(u8, usize)> = Vec::new();
    let mut named = 0usize;
    let mut named_sprites = 0usize;
    let mut at = scope.push_at + 1;
    while at < end {
        let take = BLOCK.min(end - at);
        let Some(block) = bytes(p, list + at * CMD, take * CMD) else { break };
        for k in 0..take {
            let c = &block[k * CMD..(k + 1) * CMD];
            let tag = u64_in(c, 0);
            let kd = kind(tag);
            bump(&mut out.kinds, kd, 24);
            if tag == TAG_PUSH {
                out.pushes += 1;
                if out.inner.len() < 4 {
                    out.inner.push(((f32_in(c, AT_XY), f32_in(c, AT_XY + 4)),
                                    (f32_in(c, AT_PUSH_SCALE), f32_in(c, AT_PUSH_SCALE + 4))));
                }
            }
            let z = z_at(tag).map(|o| i32_in(c, o));
            // the sprite commands' names tell how the game names its textures and where the map's walls are (each a read of
            // its own: the first ones, all of them for the log); the other named kinds' only for the log
            let wanted = if tag == TAG_SPRITE {
                keep > 0 || out.sprites < NAMES
            } else {
                keep > 0 && NAMED.contains(&kd) && named < NAMES_FOR_LOG
            };
            let name = if wanted { name_at(p, c, AT_SPRITE_NAME) } else { None };
            if tag == TAG_SPRITE {
                out.sprites += 1;
                if wanted {
                    match &name {
                        Some(n) => {
                            named_sprites += 1;
                            out.asset_names &= n.starts_with("asset/");
                            if out.ground.is_none() && is_wall(n) {
                                out.ground = z;
                            }
                            if out.front.is_none() && is_wall_front(n) {
                                out.front = z;
                            }
                            if out.units.is_none() && is_champion(n) {
                                out.units = z;
                            }
                        }
                        // a texture that is no name (a block of colour in a gauge): says nothing about the names
                        None => {
                            out.nameless += 1;
                            if keep > 0 && out.nameless <= 2 && out.raw.len() < 16 {
                                out.raw.push(raw_line(p, c, kd, out.nameless - 1, z));
                            }
                        }
                    }
                }
                if keep > 0 {
                    let line = (name.clone().unwrap_or_else(|| "?".into()), f32_in(c, AT_SPRITE_XY), f32_in(c, AT_SPRITE_XY + 4),
                                z.unwrap_or(0), f32_in(c, AT_SPRITE_UV + 8), f32_in(c, AT_SPRITE_UV + 12));
                    if out.first.len() < keep {
                        out.first.push(line);
                    } else {
                        if out.last.len() >= keep / 3 {
                            out.last.remove(0);
                        }
                        out.last.push(line);
                    }
                }
            } else if name.is_some() {
                named += 1;
            }
            if keep > 0 && !KNOWN.contains(&kd) {
                bump(&mut raw_seen, kd, 24);
                let nth = raw_seen.iter().find(|r| r.0 == kd).map_or(usize::MAX, |r| r.1);
                if nth <= (if kd == KIND_RECT { 4 } else { 2 }) && out.raw.len() < 16 {
                    out.raw.push(raw_line(p, c, kd, nth - 1, z));
                }
            }
            if let Some(z) = z {
                out.drawn += 1;
                widen(&mut out.z, z);
                match out.layers.iter().position(|l| l.z == z) {
                    Some(i) => {
                        let l = &mut out.layers[i];
                        l.n += 1;
                        bump(&mut l.kinds, kd, 8);
                        if l.name.is_none() {
                            l.name = name;
                        }
                    }
                    None if out.layers.len() < LAYERS => out.layers.push(Layer { z, n: 1, kinds: vec![(kd, 1)], name }),
                    None => out.beyond += 1,
                }
            }
        }
        at += take;
    }
    out.layers.sort_by_key(|l| l.z);
    out.asset_names &= named_sprites > 0;
    out
}

/// 这一帧怎么把世界里的一点画进 `"Game"`：缩放、平移，本包画在哪个 z，贴图画不画。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct View {
    pub scale: (f32, f32),
    pub shift: (f32, f32),
    /// 特效画在哪个 z：墙的前脸那一层——游戏自己的技能特效也在这一层，单位上面、血条下面（本包的命令排在游戏的
    /// 后面，同一个 z 上后推的画在上面）。认不出墙的前脸：英雄上面一层；也认不出英雄：世界里最高的上面一层。
    pub z: i32,
    /// 躺在地上的东西画在哪个 z：地图的墙那一层（墙和草丛上面、单位下面；游戏的回城特效的后半也在这一层）；
    /// 认不出墙：同 `z`。
    pub ground: i32,
    pub sprites: bool,
    /// 镜头这一帧看着的矩形（`"Game"` 里的左上角和宽高；游戏没推镜头命令：None）。
    pub camera: Option<(f32, f32, f32, f32)>,
}

impl View {
    /// 模拟里的一点 -> `"Game"` 里的坐标：先落到整的世界像素上（[`whole_px`]，游戏自己的图也是），再加游戏这一帧的平移——镜头慢慢移时
    /// 平移带小数，本包的图和游戏的图一起动，不各走各的半个像素。
    pub fn map(&self, sim: (u64, u64)) -> (f32, f32) {
        self.px((whole_px(sim.0) as f32, whole_px(sim.1) as f32))
    }

    /// 世界像素 -> `"Game"` 里的坐标。
    pub fn px(&self, world: (f32, f32)) -> (f32, f32) {
        (world.0 * self.scale.0 + self.shift.0, world.1 * self.scale.1 + self.shift.1)
    }

    /// 同一帧，画在地上那一层（[`View::ground`]）：元素峡谷躺在地上的东西。
    pub fn on_ground(&self) -> View {
        View { z: self.ground, ..*self }
    }
}

/// 模拟的一个坐标落在第几个世界像素上（四舍五入）。
pub fn whole_px(sim: u64) -> i32 {
    ((sim + 500) / 1000).min(i32::MAX as u64) as i32
}

/// 本包画在游戏世界里最高的 z 上面一层；游戏什么都没画时画在这一层。
pub const Z_ALONE: i32 = 100;

/// 本包画在哪：特效的 z、躺在地上的东西的 z、贴图画不画。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Layers {
    pub fx: i32,
    pub ground: i32,
    pub sprites: bool,
}

/// 数出来的东西 -> 本包的层和贴图画不画（`settings.ini` 的 `battlefield_effects` 是 2、游戏的贴图命令的名字是 `asset/…`、
/// 本包的图也在盘上）。特效：墙的前脸那一层，没有就英雄上面一层，再没有就世界里最高的上面一层。
pub fn plan(census: &Census, sheet_on_disk: bool, mode: usize) -> Layers {
    let top = census.z.map_or(Z_ALONE, |z| z.1.saturating_add(1));
    let fx = census.front.or(census.units.map(|z| z.saturating_add(1))).unwrap_or(top);
    let sprites = mode == super::settings::EFFECTS_AUTO && sheet_on_disk && census.asset_names;
    Layers { fx, ground: census.ground.unwrap_or(fx), sprites }
}

/// 一帧动画在图上的位置：(UV 的 x, y, 宽, 高)、(锚点 x, y)，都按比例。
pub fn uv_of(a: &Anim, frame: usize) -> ((f32, f32, f32, f32), (f32, f32)) {
    let f = frame.min(a.frames.saturating_sub(1) as usize);
    let (col, row) = (f % a.per_row.max(1) as usize, f / a.per_row.max(1) as usize);
    let (sw, sh) = (SHEET.0 as f32, SHEET.1 as f32);
    let (x, y) = (a.x as f32 + (col * a.w as usize) as f32, a.y as f32 + (row * a.h as usize) as f32);
    ((x / sw, y / sh, a.w as f32 / sw, a.h as f32 / sh), (a.ax as f32 / a.w as f32, a.ay as f32 / a.h as f32))
}

// ===================== 游戏里：读这一帧、画 =====================

/// 上一次数的结果留多少帧（z 和贴图名的样子不会一帧一变）。
const CENSUS_EVERY: u32 = 30;
/// 比赛到了这么多 tick 再写一段 `WORLD`（小兵、技能、血条都有了：它们的 z）。
const LATER_T: usize = 7200;

struct Seen {
    /// 上次说过的话（认不出来的原因、认出来了）：变了才记日志。
    told: String,
    /// 写过 `WORLD` 第一段、第二段的比赛。
    dumped: Option<(u64, u64)>,
    later: Option<(u64, u64)>,
    plan: Option<Layers>,
    age: u32,
    sheet: Option<bool>,
    /// 这一场贴图画不画（看过游戏的贴图名之后就定下来，一场里不来回变）。
    sprites: Option<((u64, u64), bool)>,
}

static SEEN: Mutex<Seen> = Mutex::new(Seen { told: String::new(), dumped: None, later: None, plan: None, age: 0, sheet: None,
                                             sprites: None });

/// 宿主的状态（每个接口函数的第一个参数）：`StableClient` 里就一个指向 `ClientCtxV1` 的指针。
fn host_state(ctx: &StableClient<'_>) -> Option<usize> {
    const _: () = assert!(std::mem::size_of::<StableClient<'static>>() == std::mem::size_of::<usize>());
    let raw = unsafe { *(ctx as *const StableClient<'_> as *const *const ClientCtxV1) };
    if raw.is_null() {
        return None;
    }
    let c = unsafe { &*raw };
    let end = std::mem::offset_of!(ClientCtxV1, state) + std::mem::size_of::<usize>();
    (c.size >= end).then_some(c.state as usize).filter(|s| plausible(*s))
}

fn tell(seen: &mut Seen, line: String) {
    if seen.told != line {
        seen.told.clone_from(&line);
        if let Some(k) = counted("world") {
            wlog(format!("{line} #{k}"));
        }
    }
}

/// 日志的 `WORLD` 那一段：这一帧游戏的世界长什么样、本包画在哪。
fn dump(what: &str, at: (u64, u64, usize), size: Option<(f32, f32)>, scope: &Scope, c: &Census, v: &View, on_disk: (bool, usize)) {
    let Some(k) = counted("world dump") else { return };
    let (m, s, t) = at;
    wlog(format!("WORLD {what} m={m} s={s} screen t={t}: the match's render map \"Game\" (size {size:?}) holds {} commands; camera \
                  rect {:?}; the game's world from command {} to {:?}, shifted by {:?} (scale {:?}); in it {} commands with a z \
                  {:?} ({} more on further z), {} transforms of its own (the first {:?}); kinds [{}]; {} sprite commands ({} \
                  without a name), their names asset/.. {}; the map's walls at z {:?}, their fronts at z {:?}, the champions \
                  at z {:?}; this mod's sheet on disk {}, battlefield_effects {}; this mod draws its effects at z {}, what \
                  lies on the ground at z {}, with sprites {} #{k}",
                 scope.n, v.camera, scope.push_at, scope.pop_at, scope.shift, scope.scale, c.drawn, c.z, c.beyond, c.pushes,
                 c.inner, kinds_text(&c.kinds), c.sprites, c.nameless, c.asset_names, c.ground, c.front, c.units, on_disk.0,
                 on_disk.1, v.z, v.ground, if v.sprites { "on" } else { "OFF" }));
    for l in &c.layers {
        wlog(format!("WORLD   z {}: {} commands [{}]{}", l.z, l.n, kinds_text(&l.kinds),
                     l.name.as_ref().map_or(String::new(), |n| format!(" e.g. {n:?}"))));
    }
    for (what, list) in [("first", &c.first), ("last", &c.last)] {
        for (i, (name, x, y, z, w, h)) in list.iter().enumerate() {
            wlog(format!("WORLD   {what} sprite {i}: {name:?} at ({x:.1}, {y:.1}) z {z}, uv size ({w:.4}, {h:.4})"));
        }
    }
    for r in &c.raw {
        wlog(format!("WORLD   {r}"));
    }
}

/// 这一帧的世界怎么画（渲染钩子里调）。认不出来：None，日志 `WORLD off`（原因变了才再记）。
pub fn view(ctx: &StableClient<'_>, m: u64, s: u64, t: usize) -> Option<View> {
    let mode = super::settings::effects();
    if mode == super::settings::EFFECTS_OFF || !ctx.can_draw() {
        return None;
    }
    let Ok(mut seen) = SEEN.lock() else { return None };
    let p = Process;
    // the first frame of a match, once more two minutes in, and every CENSUS_EVERY frames: the whole world counted
    let first = seen.dumped != Some((m, s));
    let later = !first && t >= LATER_T && seen.later != Some((m, s));
    let count = first || later || seen.plan.is_none() || seen.age >= CENSUS_EVERY;
    let found = host_state(ctx)
        .ok_or_else(|| "the host's state is not where it was".to_string())
        .and_then(|state| {
            bytes(&p, state + STATE_FRAME, 8).map(|b| u64_in(&b, 0) as usize).filter(|f| plausible(*f))
                .ok_or_else(|| "no frame in the host's state".to_string())
        })
        .and_then(|frame| game_list(&p, frame))
        .and_then(|(list, n)| find_scope(&p, list, n, count).map(|sc| (list, sc)));
    let (list, scope) = match found {
        Ok(v) => v,
        Err(why) => {
            tell(&mut seen, format!("WORLD off: {why} - nothing of this mod is drawn in the match world (notices and HUD as ever)"));
            return None;
        }
    };
    if (scope.scale.0 - 1.0).abs() > 0.001 || (scope.scale.1 - 1.0).abs() > 0.001 {
        tell(&mut seen, format!("WORLD off: the game draws its world at scale {:?} - this mod's pictures are made for 1", scope.scale));
        return None;
    }
    let sheet = *seen.sheet.get_or_insert_with(|| {
        super::settings::dll_dir().is_some_and(|d| d.join("effects").join(SHEET_FILE).is_file())
    });
    let at = |l: Layers| View { scale: scope.scale, shift: scope.shift, z: l.fx, ground: l.ground, sprites: l.sprites,
                                camera: scope.camera };
    if count {
        let c = census(&p, list, &scope, if first || later { 24 } else { 0 });
        let mut made = plan(&c, sheet, mode);
        // sprites or squares: settled by the first frame that has the game's own sprite commands (the map's pictures come
        // first), then kept for the match - 0.4.0 went back and forth with what happened to be in the frame
        made.sprites = match seen.sprites {
            Some((of, yes)) if of == (m, s) => yes,
            _ => {
                if c.sprites > c.nameless {
                    seen.sprites = Some(((m, s), made.sprites));
                }
                made.sprites
            }
        };
        seen.plan = Some(made);
        seen.age = 0;
        if first || later {
            // a match joined late: one piece is enough
            seen.later = (later || t >= LATER_T).then_some((m, s));
            seen.dumped = Some((m, s));
            dump(if first { "first" } else { "later" }, (m, s, t), ctx.draw_map_size(GAME), &scope, &c, &at(made), (sheet, mode));
        }
    }
    seen.age += 1;
    let made = seen.plan.unwrap_or(Layers { fx: Z_ALONE, ground: Z_ALONE, sprites: false });
    tell(&mut seen, format!("WORLD on: this mod's effects are drawn in the match world (sprites {})",
                            if made.sprites { "on" } else { "OFF: only what is drawn square by square" }));
    Some(at(made))
}

/// 宿主正在攒的这一帧（渲染钩子里）。
pub fn frame_of(ctx: &StableClient<'_>) -> Result<usize, String> {
    let state = host_state(ctx).ok_or_else(|| "the host's state is not where it was".to_string())?;
    bytes(&Process, state + STATE_FRAME, 8).map(|b| u64_in(&b, 0) as usize).filter(|f| plausible(*f))
        .ok_or_else(|| "no frame in the host's state".to_string())
}

/// 往自己的进程里写（地址不对只是写不进去，不会崩）。
#[cfg(windows)]
pub fn poke(addr: usize, data: &[u8]) -> bool {
    #[link(name = "kernel32")]
    extern "system" {
        fn GetCurrentProcess() -> isize;
        fn WriteProcessMemory(process: isize, base: *mut std::ffi::c_void, buf: *const std::ffi::c_void, size: usize,
                              written: *mut usize) -> i32;
    }
    if data.is_empty() || !plausible(addr) {
        return false;
    }
    let mut done = 0usize;
    let ok = unsafe { WriteProcessMemory(GetCurrentProcess(), addr as *mut _, data.as_ptr() as *const _, data.len(), &mut done) };
    ok != 0 && done == data.len()
}

#[cfg(not(windows))]
pub fn poke(_addr: usize, _data: &[u8]) -> bool {
    false
}

/// `[恢复, c1 … ck]` -> `[c1 … ck, 恢复]`（每条 [`CMD`] 字节）。
pub fn pop_last(block: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(block.len());
    out.extend_from_slice(&block[CMD.min(block.len())..]);
    out.extend_from_slice(&block[..CMD.min(block.len())]);
    out
}

/// 把刚推进 `"Game"` 的 `k` 条命令（世界的「恢复」后面紧跟着的那 `k` 条，表里再没有别的）挪进世界里：恢复挪到它们后面，
/// 它们就和游戏自己的命令一样在世界的平移里面（坐标直接用世界像素）。-> (恢复原来在第几条, 表里一共几条)。
pub fn move_into_world(ctx: &StableClient<'_>, k: usize) -> Result<(usize, usize), String> {
    let p = Process;
    let (list, n) = game_list(&p, frame_of(ctx)?)?;
    let pop = find_scope(&p, list, n, true)?.pop_at.ok_or_else(|| "the world's pop is not in the list".to_string())?;
    if k == 0 || pop + 1 + k != n {
        return Err(format!("{} commands after the world's pop (at {pop} of {n}), {k} expected", n - pop - 1));
    }
    let block = bytes(&p, list + pop * CMD, (k + 1) * CMD).ok_or_else(|| "the list's tail cannot be read".to_string())?;
    if u64_in(&block, 0) != TAG_POP {
        return Err("the command at the pop's place is no pop".to_string());
    }
    if poke(list + pop * CMD, &pop_last(&block)) {
        Ok((pop, n))
    } else {
        Err("the list's tail cannot be written".to_string())
    }
}

/// `"Game"` 那张表头 `n` 条命令：种类和 +8 起的四个数（镜头、平移的参数）——校准的日志用。
pub fn head(ctx: &StableClient<'_>, n: usize) -> Vec<String> {
    let p = Process;
    let Ok((list, len)) = frame_of(ctx).and_then(|f| game_list(&p, f)) else { return vec!["?".to_string()] };
    let take = n.min(len);
    let Some(block) = bytes(&p, list, take * CMD) else { return vec![format!("{len} commands, not read")] };
    let mut out: Vec<String> = (0..take)
        .map(|i| {
            let c = &block[i * CMD..(i + 1) * CMD];
            format!("{:x}: {:.1} {:.1} {:.1} {:.1}", kind(u64_in(c, 0)), f32_in(c, AT_XY), f32_in(c, AT_XY + 4), f32_in(c, AT_WH),
                    f32_in(c, AT_WH + 4))
        })
        .collect();
    out.push(format!("{len} in all"));
    out
}

/// 画一帧动画，它的**左上角**放在渲染层 `map` 的 `(x, y)`。
///
/// 引擎的 `pivot` 不是接口文档说的「x、y 指的那一点」：2026-11-11 的校准截图里，给了锚点的比例（脚在图里的位置），图的
/// 左上角落在 x、y **加**锚点的地方——整张图往右下偏了两个锚点（60 × 84 的光柱偏了 (60, 144)，`"Game"` 和 `"UI"` 上一样）。
/// 所以锚点自己减，`pivot` 给 0：不管引擎怎么用它，0 就是左上角。
pub fn sprite_top_left(ctx: &mut StableClient<'_>, map: &str, z: i32, a: &Anim, frame: usize, x: f32, y: f32) -> bool {
    let (uv, _) = uv_of(a, frame);
    ctx.draw_sprite(map, SHEET_TEX, &StableSpriteParams {
        x,
        y,
        z,
        pivot_x: 0.0,
        pivot_y: 0.0,
        uv,
        sample_nearest: true,
        ..StableSpriteParams::default()
    })
}

/// 一帧动画的左上角在哪：它的锚点（脚）放在 `"Game"` 里的 `feet` 上。
pub fn corner(a: &Anim, feet: (f32, f32)) -> (f32, f32) {
    (feet.0 - a.ax as f32, feet.1 - a.ay as f32)
}

/// 画一帧动画：`frame` 那一帧的锚点放在模拟里的 `at` 上。
pub fn sprite(ctx: &mut StableClient<'_>, v: &View, a: &Anim, frame: usize, at: (u64, u64)) -> bool {
    if !v.sprites {
        return false;
    }
    let (x, y) = corner(a, v.map(at));
    sprite_top_left(ctx, GAME, v.z, a, frame, x, y)
}

/// 画一帧动画，锚点放在 `"Game"` 里的 `at`（不跟着世界走的东西：海洋峡谷的雨铺在镜头看着的那一块上）。
pub fn sprite_on_map(ctx: &mut StableClient<'_>, v: &View, a: &Anim, frame: usize, at: (f32, f32)) -> bool {
    if !v.sprites {
        return false;
    }
    let (x, y) = corner(a, at);
    sprite_top_left(ctx, GAME, v.z, a, frame, x, y)
}

/// 世界里的一横条像素（`x`、`y` 是世界像素，`w` 条宽）：`0xRRGGBBAA`。
pub fn run(ctx: &mut StableClient<'_>, v: &View, x: i32, y: i32, w: i32, colour: u32) -> bool {
    let (mx, my) = v.px((x as f32, y as f32));
    ctx.draw_rect(GAME, mx, my, w as f32 * v.scale.0, v.scale.1, v.z, 0.0, colour)
}

#[cfg(test)]
pub(crate) mod tests {
    use super::*;
    use super::super::fx_atlas::ANIMS;

    /// A piece of memory of one's own: regions by their base address.
    #[derive(Default)]
    pub struct Fake {
        pub regions: Vec<(usize, Vec<u8>)>,
    }

    impl Peek for Fake {
        fn read(&self, addr: usize, buf: &mut [u8]) -> bool {
            for (base, data) in &self.regions {
                if addr >= *base && addr + buf.len() <= base + data.len() {
                    buf.copy_from_slice(&data[addr - base..addr - base + buf.len()]);
                    return true;
                }
            }
            false
        }
    }

    pub fn put64(b: &mut [u8], at: usize, v: u64) {
        b[at..at + 8].copy_from_slice(&v.to_le_bytes());
    }

    pub fn put32f(b: &mut [u8], at: usize, v: f32) {
        b[at..at + 4].copy_from_slice(&v.to_le_bytes());
    }

    pub fn camera(x: f32, y: f32, w: f32, h: f32) -> Vec<u8> {
        let mut c = vec![0u8; CMD];
        put64(&mut c, 0, TAG_CAMERA);
        for (i, v) in [x, y, w, h].into_iter().enumerate() {
            put32f(&mut c, AT_XY + 4 * i, v);
        }
        c
    }

    pub fn push(tx: f32, ty: f32, scale: f32) -> Vec<u8> {
        let mut c = vec![0u8; CMD];
        put64(&mut c, 0, TAG_PUSH);
        put32f(&mut c, AT_XY, tx);
        put32f(&mut c, AT_XY + 4, ty);
        put32f(&mut c, AT_PUSH_SCALE, scale);
        put32f(&mut c, AT_PUSH_SCALE + 4, scale);
        c
    }

    pub fn tagged(tag: u64) -> Vec<u8> {
        let mut c = vec![0u8; CMD];
        put64(&mut c, 0, tag);
        c
    }

    /// A sprite command whose texture name sits at `name_at` in the fake memory.
    pub fn sprite_cmd(name_at: usize, name_len: usize, x: f32, y: f32, z: i32) -> Vec<u8> {
        let mut c = vec![0u8; CMD];
        put64(&mut c, 0, TAG_SPRITE);
        put64(&mut c, AT_SPRITE_NAME, name_len as u64);
        put64(&mut c, AT_SPRITE_NAME + 8, name_at as u64);
        put64(&mut c, AT_SPRITE_NAME + 16, name_len as u64);
        put32f(&mut c, AT_SPRITE_XY, x);
        put32f(&mut c, AT_SPRITE_XY + 4, y);
        let at = z_at(TAG_SPRITE).unwrap();
        c[at..at + 4].copy_from_slice(&z.to_le_bytes());
        put32f(&mut c, AT_SPRITE_UV + 8, 0.25);
        put32f(&mut c, AT_SPRITE_UV + 12, 0.5);
        c
    }

    /// A rect command at layer `z`.
    pub fn rect_cmd(z: i32) -> Vec<u8> {
        let mut c = tagged(TAG_RECT);
        let at = z_at(TAG_RECT).unwrap();
        c[at..at + 4].copy_from_slice(&z.to_le_bytes());
        c
    }

    /// A text command: a String's capacity where the other kinds have their tag.
    pub fn text_cmd(z: i32) -> Vec<u8> {
        let mut c = tagged(24);
        let at = z_at(24).unwrap();
        c[at..at + 4].copy_from_slice(&z.to_le_bytes());
        c
    }

    /// A command of kind `tag` with a name where the sprite's is (the units' pictures).
    pub fn named(tag: u64, name_at: usize, name_len: usize, z: i32) -> Vec<u8> {
        let mut c = tagged(tag);
        put64(&mut c, AT_SPRITE_NAME, name_len as u64);
        put64(&mut c, AT_SPRITE_NAME + 8, name_at as u64);
        put64(&mut c, AT_SPRITE_NAME + 16, name_len as u64);
        let at = z_at(tag).unwrap();
        c[at..at + 4].copy_from_slice(&z.to_le_bytes());
        c
    }

    pub const FRAME: usize = 0x10_0000;
    const CTRL: usize = 0x20_0000;
    const NAMES: usize = 0x30_0000;
    const LISTS: usize = 0x40_0000;

    /// A frame whose render maps are `maps` (name, commands), laid out as the host's: the table's header in the frame,
    /// the buckets below the control bytes, the names and the command lists elsewhere.
    pub fn frame(maps: &[(&str, Vec<Vec<u8>>)]) -> Fake {
        let slots = 8usize;
        let mut fake = Fake::default();
        let mut head = vec![0u8; FRAME_LISTS + 0x20];
        put64(&mut head, FRAME_LISTS, CTRL as u64);
        put64(&mut head, FRAME_LISTS + 8, slots as u64 - 1);
        put64(&mut head, FRAME_LISTS + 0x18, maps.len() as u64);
        fake.regions.push((FRAME, head));
        // buckets grow down from CTRL, the control bytes up from it
        let mut table = vec![0u8; slots * BUCKET + slots];
        for i in 0..slots {
            table[slots * BUCKET + i] = 0xff;
        }
        let mut names = Vec::new();
        for (i, (name, cmds)) in maps.iter().enumerate() {
            let slot = (i * 3 + 1) % slots; // not in order, as a hash table's are not
            table[slots * BUCKET + slot] = 0x11;
            let b = slots * BUCKET - (slot + 1) * BUCKET;
            put64(&mut table, b, name.len() as u64);
            put64(&mut table, b + 8, (NAMES + names.len()) as u64);
            put64(&mut table, b + 0x10, name.len() as u64);
            names.extend_from_slice(name.as_bytes());
            let list = LISTS + i * 0x10_0000;
            put64(&mut table, b + 0x18, cmds.len() as u64 + 3);
            put64(&mut table, b + 0x20, list as u64);
            put64(&mut table, b + 0x28, cmds.len() as u64);
            fake.regions.push((list, cmds.concat()));
        }
        fake.regions.push((CTRL - slots * BUCKET, table));
        fake.regions.push((NAMES, names));
        fake
    }

    #[test]
    fn the_games_shift_is_read_from_its_own_commands() {
        // a mod's own command first (pre_render), then the game's: camera, transform, its sprites, the pop, a mod's after
        let mut cmds = vec![tagged(TAG_RECT), camera(1024.0 - 320.0, 1024.0 - 180.0, 640.0, 360.0), push(544.0, 380.5, 1.0)];
        cmds.extend((0..150).map(|_| tagged(TAG_RECT)));
        cmds.push(tagged(TAG_POP));
        cmds.push(tagged(TAG_RECT));
        let fake = frame(&[("UI", vec![tagged(TAG_RECT)]), ("Game", cmds), ("Default", vec![])]);
        let (list, n) = game_list(&fake, FRAME).expect("the Game list");
        assert_eq!(n, 155);
        let sc = find_scope(&fake, list, n, true).expect("the scope");
        assert_eq!((sc.push_at, sc.pop_at, sc.shift, sc.scale), (2, Some(153), (544.0, 380.5), (1.0, 1.0)));
        // every frame only as far as the transform (the first block), the same numbers
        let quick = find_scope(&fake, list, n, false).unwrap();
        assert_eq!(Scope { pop_at: sc.pop_at, ..quick }, sc);
        assert_eq!(sc.camera, Some((704.0, 844.0, 640.0, 360.0)));
        // a point of the simulation lands where the game draws it: 1000 units a pixel, then the game's shift
        let v = View { scale: sc.scale, shift: sc.shift, z: 7, ground: -1, sprites: true, camera: sc.camera };
        assert_eq!(v.map((672_000, 672_000)), (672.0 + 544.0, 672.0 + 380.5));
        // on the world's whole pixels like the game's own pictures, the camera's fraction of a pixel on top
        assert_eq!(v.map((672_400, 671_600)), (672.0 + 544.0, 672.0 + 380.5));
        assert_eq!(v.px((10.0, 20.0)), (554.0, 400.5));
        // what lies on the ground: the same frame, the walls' layer
        assert_eq!(v.on_ground(), View { z: -1, ..v });
    }

    #[test]
    fn a_frame_that_is_not_as_expected_is_told_and_nothing_crashes() {
        // no frame memory at all
        assert!(game_list(&Fake::default(), FRAME).unwrap_err().contains("cannot be read"));
        // no "Game" map this frame (a menu): its names are told
        let fake = frame(&[("UI", vec![tagged(TAG_RECT)])]);
        let e = game_list(&fake, FRAME).unwrap_err();
        assert!(e.contains("no \"Game\" map") && e.contains("UI"), "{e}");
        // a table header that is no table
        let mut bad = frame(&[("Game", vec![])]);
        put64(&mut bad.regions[0].1, FRAME_LISTS + 8, 6); // a mask that is no power of two less one
        assert!(game_list(&bad, FRAME).unwrap_err().contains("looks wrong"));
        // the "Game" map without a transform (another build's commands): the first tags are told
        let fake = frame(&[("Game", vec![tagged(0x8000_0000_0000_0005), tagged(TAG_RECT)])]);
        let (list, n) = game_list(&fake, FRAME).unwrap();
        let e = find_scope(&fake, list, n, false).unwrap_err();
        assert!(e.contains("no world transform") && e.contains("0x8000000000000005"), "{e}");
        // a transform whose numbers are no numbers
        let fake = frame(&[("Game", vec![push(f32::NAN, 0.0, 1.0)])]);
        let (list, n) = game_list(&fake, FRAME).unwrap();
        assert!(find_scope(&fake, list, n, false).unwrap_err().contains("no transform"));
        // a list longer than its memory
        let mut fake = frame(&[("Game", vec![camera(0.0, 0.0, 1.0, 1.0)])]);
        let at = fake.regions.iter().position(|r| r.0 == CTRL - 8 * BUCKET).unwrap();
        let table = &mut fake.regions[at].1;
        let slot = 1;
        put64(table, 8 * BUCKET - (slot + 1) * BUCKET + 0x18, 900);
        put64(table, 8 * BUCKET - (slot + 1) * BUCKET + 0x28, 900);
        let (list, n) = game_list(&fake, FRAME).unwrap();
        assert!(find_scope(&fake, list, n, true).unwrap_err().contains("cannot be read"));
    }

    #[test]
    fn the_census_gives_the_layers_and_whether_sprites_are_safe() {
        let (map, jinx) = ("asset/base/aseprite_resources/ingame/5v5/map", "asset/league/champion/league_jinx#sheet");
        let names = [map.as_bytes(), jinx.as_bytes()].concat();
        let (a, b) = (map.len(), jinx.len());
        let base = 0x50_0000;
        let cmds = vec![camera(0.0, 0.0, 1.0, 1.0), push(544.0, 544.0, 1.0), sprite_cmd(base, a, 0.0, 0.0, -50),
                        sprite_cmd(base + a, b, 300.0, 410.0, 410), rect_cmd(0), tagged(0x8000_0000_0000_000f),
                        tagged(TAG_POP), sprite_cmd(base, a, 9.0, 9.0, 99_999)];
        let mut fake = frame(&[("Game", cmds)]);
        fake.regions.push((base, names));
        let (list, n) = game_list(&fake, FRAME).unwrap();
        let sc = find_scope(&fake, list, n, true).unwrap();
        let c = census(&fake, list, &sc, 8);
        assert_eq!((c.sprites, c.drawn, c.z), (2, 3, Some((-50, 410))), "what follows the pop is not the world");
        assert_eq!(c.kinds, vec![(0x03, 2), (0x0a, 1), (0x0f, 1)]);
        assert!(c.asset_names, "the map's own pictures have no '#sheet' in their names");
        assert_eq!((c.ground, c.front, c.units, c.nameless), (None, None, None, 0), "no map with walls, no champion here");
        assert_eq!(c.first[1], (jinx.to_string(), 300.0, 410.0, 410, 0.25, 0.5));
        // the rects and a kind that is not known: as they stand, for the log
        assert_eq!(c.raw.len(), 2);
        assert!(c.raw[0].starts_with("kind 0xa #0 (z Some(0)): words [800000000000000a 0 "), "{}", c.raw[0]);
        assert!(c.raw[1].starts_with("kind 0xf #0 (z None): words [800000000000000f 0 "), "{}", c.raw[1]);
        // nothing known of the game's layers: above its highest; sprites only with the sheet on disk
        use super::super::settings::{EFFECTS_AUTO, EFFECTS_SQUARES};
        let top = Layers { fx: 411, ground: 411, sprites: true };
        assert_eq!(plan(&c, true, EFFECTS_AUTO), top);
        assert_eq!(plan(&c, false, EFFECTS_AUTO), Layers { sprites: false, ..top });
        // the player asked for squares only (settings.ini): no sprites
        assert_eq!(plan(&c, true, EFFECTS_SQUARES), Layers { sprites: false, ..top });
        // texture names of another shape: no sprites
        assert_eq!(plan(&Census { asset_names: false, ..c.clone() }, true, EFFECTS_AUTO), Layers { sprites: false, ..top });
        // the map's walls known: what lies on the ground goes to their layer
        assert_eq!(plan(&Census { ground: Some(-1), ..c.clone() }, true, EFFECTS_AUTO), Layers { ground: -1, ..top });
        // the champions known: the effects one layer over them; the walls' fronts known: on that layer, as the game's own
        assert_eq!(plan(&Census { units: Some(0), ..c.clone() }, true, EFFECTS_AUTO), Layers { fx: 1, ground: 1, sprites: true });
        assert_eq!(plan(&Census { units: Some(0), front: Some(2), ground: Some(-1), ..c.clone() }, true, EFFECTS_AUTO),
                   Layers { fx: 2, ground: -1, sprites: true });
        // nothing drawn by the game: this mod's own layer, no sprites
        assert_eq!(plan(&Census::default(), true, EFFECTS_AUTO), Layers { fx: Z_ALONE, ground: Z_ALONE, sprites: false });
        // between two pieces of the log (every 30 frames): the same layers, nothing kept
        let quick = census(&fake, list, &sc, 0);
        assert_eq!((quick.z, quick.drawn, quick.asset_names, quick.raw.len(), quick.first.len()), (c.z, 3, true, 0, 0));
    }

    /// The frame of the user's first matches with 0.4.0 / 0.4.1 (2026-11-11, league_dragons.log): scaled units have a
    /// transform pair of their own inside the world's, so the world ends at the pop that matches its push - 0.4.0 took the
    /// first pop and counted the map's six pictures only (z -3..1), drew at z 2 and kept the sprites off. A gauge's block of
    /// colour is a sprite command without a name - 0.4.1 took that for a name of another shape and kept the sprites off.
    #[test]
    fn the_world_ends_at_the_pop_that_matches_its_push() {
        let dir = "asset/base/aseprite_resources/ingame/5v5/";
        let names: Vec<String> = ["background_5v5", "wall_shadow_5v5", "bush_shadow_5v5", "wall_5v5", "bush_5v5", "wall_5v5_front"]
            .iter().map(|n| format!("{dir}{n}"))
            .chain(["asset/base/sprite/circle".to_string(), "asset/base/sprite/white".to_string(),
                    "asset/base/aseprite_resources/champions/league_ornn#sheet".to_string()])
            .collect();
        let base = 0x50_0000;
        let mut blob = Vec::new();
        let mut at = Vec::new();
        for n in &names {
            at.push((base + blob.len(), n.len()));
            blob.extend_from_slice(n.as_bytes());
        }
        let unit = 0x8000_0000_0000_0004;
        let mut cmds = vec![camera(512.0, 512.0, 1024.0, 1024.0), push(904.0, 78.83197, 1.0)];
        for (i, z) in [-3, -2, -3, -1, -1, 1].into_iter().enumerate() {
            cmds.push(sprite_cmd(at[i].0, at[i].1, -160.0, -160.0, z));
        }
        // two scaled units' shadows, each in a transform pair of its own
        for _ in 0..2 {
            cmds.extend([push(-12.5, -80.0, 1.25), named(unit, at[6].0, at[6].1, -2), tagged(TAG_POP)]);
        }
        // a gauge's back, a champion, the gauge's block of colour (a sprite without a name), a rect, a text; the world's
        // own pop; then a mod's rect
        cmds.extend([named(unit, at[7].0, at[7].1, 3), sprite_cmd(at[8].0, at[8].1, 200.0, -1.0, 0), sprite_cmd(0, 0, 231.0, 66.0, 3),
                     rect_cmd(100), text_cmd(0), tagged(TAG_POP), rect_cmd(900)]);
        let mut fake = frame(&[("Game", cmds)]);
        fake.regions.push((base, blob));
        let (list, n) = game_list(&fake, FRAME).unwrap();
        let sc = find_scope(&fake, list, n, true).unwrap();
        assert_eq!((sc.push_at, sc.pop_at, sc.shift), (1, Some(n - 2), (904.0, 78.83197)));
        let c = census(&fake, list, &sc, 24);
        assert_eq!((c.drawn, c.z, c.sprites, c.nameless, c.pushes, c.beyond), (13, Some((-3, 100)), 8, 1, 2, 0));
        assert_eq!(c.inner, vec![((-12.5, -80.0), (1.25, 1.25)); 2]);
        assert_eq!(c.kinds, vec![(0x03, 8), (0x12, 2), (0x04, 3), (0x13, 2), (0x0a, 1), (KIND_TEXT, 1)]);
        assert_eq!(kinds_text(&c.kinds), "3 x8, 12 x2, 4 x3, 13 x2, a x1, text x1");
        // the layers from the lowest: the map and the shadows, the units between its walls and their fronts, the gauges
        let layers: Vec<(i32, usize)> = c.layers.iter().map(|l| (l.z, l.n)).collect();
        assert_eq!(layers, vec![(-3, 2), (-2, 3), (-1, 2), (0, 2), (1, 1), (3, 2), (100, 1)]);
        assert_eq!((c.layers[1].kinds.clone(), c.layers[1].name.as_deref()), (vec![(0x03, 1), (0x04, 2)], Some(names[1].as_str())));
        assert_eq!((c.layers[3].kinds.clone(), c.layers[3].name.as_deref()), (vec![(0x03, 1), (KIND_TEXT, 1)], Some(names[8].as_str())));
        assert_eq!(c.layers[5].name.as_deref(), Some("asset/base/sprite/white"));
        // what this mod does not know as it stands: the other kind of picture (its first two, with the names found in
        // them), the sprite without a name, the rect
        let of = |k: &str| c.raw.iter().filter(|r| r.starts_with(k)).count();
        assert_eq!((c.raw.len(), of("kind 0x4 "), of("kind 0x3 "), of("kind 0xa ")), (4, 2, 1, 1));
        assert!(c.raw[0].starts_with("kind 0x4 #0 (z Some(-2)): words [8000000000000004 18 ")
                && c.raw[0].ends_with("strings [+0x8 \"asset/base/sprite/circle\"]"), "{}", c.raw[0]);
        // the sprite without a name says nothing about the names: the sheet is drawn
        assert!(c.asset_names);
        // the map's walls give the ground's layer, their fronts the effects' - where the game's own skill effects are,
        // over the units and under the gauges
        assert_eq!((c.ground, c.front, c.units), (Some(-1), Some(1), Some(0)));
        use super::super::settings::EFFECTS_AUTO;
        assert_eq!(plan(&c, true, EFFECTS_AUTO), Layers { fx: 1, ground: -1, sprites: true });
        // only sprites without a name (no name read at all): no sheet
        let blind = frame(&[("Game", vec![push(0.0, 0.0, 1.0), sprite_cmd(0, 0, 1.0, 1.0, 3), tagged(TAG_POP)])]);
        let (bl, bn) = game_list(&blind, FRAME).unwrap();
        let bc = census(&blind, bl, &find_scope(&blind, bl, bn, true).unwrap(), 0);
        assert_eq!((bc.sprites, bc.nameless, bc.asset_names), (1, 1, false));
        // every frame only the transform is looked for: the same push
        assert_eq!(find_scope(&fake, list, n, false).unwrap().push_at, 1);
        // a world whose pop never comes (a list cut short): to the list's end
        let open = frame(&[("Game", vec![push(1.0, 2.0, 1.0), push(0.0, 0.0, 2.0), rect_cmd(3), tagged(TAG_POP), rect_cmd(4)])]);
        let (list, n) = game_list(&open, FRAME).unwrap();
        let sc = find_scope(&open, list, n, true).unwrap();
        assert_eq!((sc.push_at, sc.pop_at), (0, None));
        assert_eq!(census(&open, list, &sc, 0).z, Some((3, 4)));
        // the map's pictures by their file names
        assert!(is_wall("asset/base/aseprite_resources/ingame/5v5/wall_5v5") && is_wall("a/wall_3v3"));
        assert!(!is_wall("a/wall_5v5_front") && !is_wall("a/wall_shadow_5v5") && !is_wall("a/tower_shadow") && !is_wall("a/bush_5v5"));
        assert!(is_wall_front("a/wall_5v5_front") && !is_wall_front("a/wall_5v5") && !is_wall_front("a/red_tower_front"));
        assert!(is_champion("asset/base/aseprite_resources/champions/league_ornn#sheet") && !is_champion("asset/league/effects/x#sheet"));
    }

    /// Where each kind of command keeps its z - as the game's own renderer reads them (0.7.2, 0x1e6d90).
    #[test]
    fn every_kind_of_command_has_its_z_where_the_game_reads_it() {
        let top = 1u64 << 63;
        assert_eq!((z_at(TAG_SPRITE), z_at(TAG_RECT), z_at(top | 4), z_at(top | 2)), (Some(0x80), Some(0x68), Some(0x88), Some(0x88)));
        // a text's first word is its String's capacity
        assert_eq!((kind(24), z_at(24), kind(0), z_at(0)), (KIND_TEXT, Some(0xb8), KIND_TEXT, Some(0xb8)));
        // the camera, the transforms and the kinds between them have none
        for k in [0u64, 1, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x14, 0xff] {
            assert_eq!(z_at(top | k), None, "{k:#x}");
        }
        let with: Vec<u64> = (0..0x20).filter(|k| z_at(top | k).is_some()).collect();
        // (7 is the text's place among the kinds: no command carries it as a tag)
        assert_eq!(with, vec![2, 3, 4, 5, 6, 7, 8, 9, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e]);
        for k in with {
            assert!(z_at(top | k).unwrap() + 4 <= CMD);
        }
        assert_eq!((kind(TAG_PUSH), kind(TAG_POP), kind(TAG_CAMERA)), (0x12, 0x13, 0x00));
    }

    /// Commands pushed after the world's pop go into the world when the pop is moved behind them.
    #[test]
    fn the_pop_moves_behind_what_was_pushed_after_it() {
        let block = [tagged(TAG_POP), rect_cmd(1), rect_cmd(2)].concat();
        let out = pop_last(&block);
        assert_eq!(out.len(), block.len());
        assert_eq!(out[..CMD], rect_cmd(1)[..]);
        assert_eq!(out[CMD..2 * CMD], rect_cmd(2)[..]);
        assert_eq!(out[2 * CMD..], tagged(TAG_POP)[..]);
        // the list as the game then reads it: the world ends after them
        let mut cmds = vec![camera(512.0, 512.0, 1024.0, 1024.0), push(904.0, 126.0, 1.0), rect_cmd(0)];
        cmds.extend(out.chunks(CMD).map(|c| c.to_vec()));
        let fake = frame(&[("Game", cmds)]);
        let (list, n) = game_list(&fake, FRAME).unwrap();
        let sc = find_scope(&fake, list, n, true).unwrap();
        assert_eq!((sc.push_at, sc.pop_at, census(&fake, list, &sc, 0).z), (1, Some(5), Some((0, 2))));
    }

    /// The sheet ships with the add-on, at the size its table says, where the mod looks for it.
    #[test]
    fn the_sheet_is_in_the_add_ons_folder_at_the_tables_size() {
        let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("..").join("league_dragons").join("effects");
        let png = std::fs::read(dir.join(SHEET_FILE)).expect("effects/league_dragons_fx#sheet.png");
        assert_eq!(png[..8], [0x89, b'P', b'N', b'G', 0x0d, 0x0a, 0x1a, 0x0a]);
        let dim = |at: usize| u32::from_be_bytes(png[at..at + 4].try_into().unwrap());
        assert_eq!((dim(16), dim(20)), (SHEET.0 as u32, SHEET.1 as u32), "run tools/art/dragons_soul_fx.py");
        // the name the mod draws it by: its file under asset/<this mod's folder>/, without the extension
        assert_eq!(SHEET_TEX, format!("asset/league_dragons/effects/{}", SHEET_FILE.trim_end_matches(".png")));
        // like the dragons' own sheets the game already loads from there
        let ov = include_str!("../mod.override_info");
        assert!(ov.contains("\"asset/league_dragons/effects/league_drake_infernal#sheet\""));
    }

    #[test]
    fn a_frame_of_an_animation_is_its_cell_of_the_sheet() {
        let a = ANIMS.iter().find(|a| a.name == "elder_execute").unwrap();
        let (uv, pivot) = uv_of(a, 3);
        let (sw, sh) = (SHEET.0 as f32, SHEET.1 as f32);
        assert_eq!(uv, ((a.x + 3 * a.w) as f32 / sw, a.y as f32 / sh, a.w as f32 / sw, a.h as f32 / sh));
        assert_eq!(pivot, (a.ax as f32 / a.w as f32, a.ay as f32 / a.h as f32));
        // past the last frame: the last one
        assert_eq!(uv_of(a, 999), uv_of(a, a.frames as usize - 1));
        // drawn by its top left corner: the feet at (500, 300) put the 96 x 136 picture's corner its anchor up and left
        assert_eq!(corner(a, (500.0, 300.0)), (500.0 - a.ax as f32, 300.0 - a.ay as f32));
        assert_eq!((a.ax, a.ay), (48, 116));
        // every cell inside the sheet, every anchor inside its cell
        for a in ANIMS {
            let lines = (a.frames as usize).div_ceil(a.per_row as usize);
            assert!(a.x as usize + a.per_row as usize * a.w as usize <= SHEET.0 as usize, "{}", a.name);
            assert!(a.y as usize + lines * a.h as usize <= SHEET.1 as usize, "{}", a.name);
            assert!(a.ax < a.w && a.ay < a.h && a.frames > 0 && a.ticks > 0, "{}", a.name);
        }
    }
}
