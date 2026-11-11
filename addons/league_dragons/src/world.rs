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
//! - 游戏自己的贴图名长得不像本包预想的（`asset/…#sheet`）时不画贴图（引擎找不到贴图会怎样没试过，不冒这个险）。
//!
//! 每场比赛第一次读成功时日志一段 `WORLD`：镜头、平移、游戏自己的贴图命令的 z 范围和头几条（贴图名、坐标），以后改画法、
//! 定层级照着它。本包的东西画在游戏世界里最高的 z 上面一层。

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
/// 命令里的位置：镜头 / 平移的两个数，平移的缩放，贴图命令的名字、UV、坐标、z，矩形的 z。
const AT_XY: usize = 0x08;
const AT_WH: usize = 0x10;
const AT_PUSH_SCALE: usize = 0x24;
const AT_SPRITE_NAME: usize = 0x08;
const AT_SPRITE_UV: usize = 0x68;
const AT_SPRITE_XY: usize = 0x78;
const AT_SPRITE_Z: usize = 0x80;
const AT_RECT_Z: usize = 0x68;
/// 一次读多少条命令；一张命令表最多认这么多条（再多就不是命令表了）。
const BLOCK: usize = 64;
/// 平时数的时候只读头这么多条贴图命令的名字（看游戏的贴图名长什么样）。
const NAMES: usize = 48;
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
/// （左上角和宽高）、恢复那条在第几条。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Scope {
    pub n: usize,
    pub push_at: usize,
    pub pop_at: Option<usize>,
    pub scale: (f32, f32),
    pub shift: (f32, f32),
    pub camera: Option<(f32, f32, f32, f32)>,
}

/// 在 `n` 条命令里找游戏的平移（第一条）；`to_pop`：接着找到它的恢复（要数里面的命令时才用：那是整张表）。找不到、数不
/// 像样：说明看到了什么。
pub fn find_scope(p: &dyn Peek, list: usize, n: usize, to_pop: bool) -> Result<Scope, String> {
    let mut camera = None;
    let mut seen: Vec<u64> = Vec::new();
    let mut found: Option<Scope> = None;
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
                (TAG_POP, Some(s)) => {
                    s.pop_at = Some(at + k);
                    return Ok(*s);
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

/// 游戏在世界里画的贴图命令：几条、z 的范围、贴图名都是 `asset/…` 的样子没有，头几条（名字、坐标、z、UV 的宽高）。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Census {
    pub sprites: usize,
    pub rects: usize,
    pub others: Vec<(u64, usize)>,
    pub z: Option<(i32, i32)>,
    pub rect_z: Option<(i32, i32)>,
    /// 贴图名都以 `asset/` 开头（一条都没有：false）。
    pub asset_names: bool,
    /// 有以 `#sheet` 结尾的贴图名。
    pub sheet_names: bool,
    pub first: Vec<(String, f32, f32, i32, f32, f32)>,
    /// 最后几条（画在最上面的）。
    pub last: Vec<(String, f32, f32, i32, f32, f32)>,
}

fn widen(r: &mut Option<(i32, i32)>, z: i32) {
    *r = Some(r.map_or((z, z), |(a, b)| (a.min(z), b.max(z))));
}

/// 数一遍平移和恢复之间的命令（`keep`：头几条贴图命令留下来写日志）。
pub fn census(p: &dyn Peek, list: usize, scope: &Scope, keep: usize) -> Census {
    let mut out = Census { asset_names: true, ..Census::default() };
    let end = scope.pop_at.unwrap_or(scope.n).min(scope.n);
    let mut at = scope.push_at + 1;
    while at < end {
        let take = BLOCK.min(end - at);
        let Some(block) = bytes(p, list + at * CMD, take * CMD) else { break };
        for k in 0..take {
            let c = &block[k * CMD..(k + 1) * CMD];
            match u64_in(c, 0) {
                TAG_SPRITE => {
                    out.sprites += 1;
                    let z = i32_in(c, AT_SPRITE_Z);
                    widen(&mut out.z, z);
                    // the names of the first ones tell how the game names its textures (each is a read of its own);
                    // all of them only when they are kept for the log
                    if keep == 0 && out.sprites > NAMES {
                        continue;
                    }
                    let (ptr, len) = (u64_in(c, AT_SPRITE_NAME + 8) as usize, u64_in(c, AT_SPRITE_NAME + 16) as usize);
                    let name = (len <= 200).then(|| bytes(p, ptr, len)).flatten().map(|b| String::from_utf8_lossy(&b).into_owned());
                    match &name {
                        Some(n) => {
                            out.asset_names &= n.starts_with("asset/");
                            out.sheet_names |= n.ends_with("#sheet");
                        }
                        None => out.asset_names = false,
                    }
                    if keep > 0 {
                        let line = (name.unwrap_or_else(|| "?".into()), f32_in(c, AT_SPRITE_XY), f32_in(c, AT_SPRITE_XY + 4), z,
                                    f32_in(c, AT_SPRITE_UV + 8), f32_in(c, AT_SPRITE_UV + 12));
                        if out.first.len() < keep {
                            out.first.push(line);
                        } else {
                            if out.last.len() >= keep / 3 {
                                out.last.remove(0);
                            }
                            out.last.push(line);
                        }
                    }
                }
                TAG_RECT => {
                    out.rects += 1;
                    widen(&mut out.rect_z, i32_in(c, AT_RECT_Z));
                }
                tag => match out.others.iter().position(|o| o.0 == tag) {
                    Some(i) => out.others[i].1 += 1,
                    None if out.others.len() < 24 => out.others.push((tag, 1)),
                    None => {}
                },
            }
        }
        at += take;
    }
    out.asset_names &= out.sprites > 0;
    out
}

/// 这一帧怎么把世界里的一点画进 `"Game"`：缩放、平移，本包画在哪个 z，贴图画不画。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct View {
    pub scale: (f32, f32),
    pub shift: (f32, f32),
    pub z: i32,
    pub sprites: bool,
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
}

/// 模拟的一个坐标落在第几个世界像素上（四舍五入）。
pub fn whole_px(sim: u64) -> i32 {
    ((sim + 500) / 1000).min(i32::MAX as u64) as i32
}

/// 本包画在游戏世界里最高的 z 上面一层；游戏一条贴图都没画时画在这一层。
pub const Z_ALONE: i32 = 100;

/// 数出来的东西 -> 本包的 z 和贴图画不画（`settings.ini` 的 `battlefield_effects` 是 2、游戏的贴图名是 `asset/…` 而且有
/// `…#sheet` 的、本包的图也在盘上）。
pub fn plan(census: &Census, sheet_on_disk: bool, mode: usize) -> (i32, bool) {
    let top = [census.z, census.rect_z].iter().flatten().map(|r| r.1).max();
    let sprites = mode == super::settings::EFFECTS_AUTO && sheet_on_disk && census.asset_names && census.sheet_names;
    (top.map_or(Z_ALONE, |z| z.saturating_add(1)), sprites)
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

struct Seen {
    /// 上次说过的话（认不出来的原因、认出来了）：变了才记日志。
    told: String,
    /// 写过 `WORLD` 那一段的比赛。
    dumped: Option<(u64, u64)>,
    plan: Option<(i32, bool)>,
    age: u32,
    sheet: Option<bool>,
}

static SEEN: Mutex<Seen> = Mutex::new(Seen { told: String::new(), dumped: None, plan: None, age: 0, sheet: None });

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

/// 这一帧的世界怎么画（渲染钩子里调）。认不出来：None，日志 `WORLD off`（原因变了才再记）。
pub fn view(ctx: &StableClient<'_>, m: u64, s: u64, t: usize) -> Option<View> {
    let mode = super::settings::effects();
    if mode == super::settings::EFFECTS_OFF || !ctx.can_draw() {
        return None;
    }
    let Ok(mut seen) = SEEN.lock() else { return None };
    let p = Process;
    // the first frame of a match and every CENSUS_EVERY frames: the whole world counted (its z, its texture names)
    let first = seen.dumped != Some((m, s));
    let count = first || seen.plan.is_none() || seen.age >= CENSUS_EVERY;
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
    if count {
        let c = census(&p, list, &scope, if first { 24 } else { 0 });
        let made = plan(&c, sheet, mode);
        seen.plan = Some(made);
        seen.age = 0;
        if first {
            seen.dumped = Some((m, s));
            if let Some(k) = counted("world dump") {
                let others: Vec<String> = c.others.iter().map(|(t, n)| format!("{t:#x} x{n}")).collect();
                wlog(format!("WORLD m={m} s={s} screen t={t}: the match's render map \"Game\" (size {:?}) holds {} commands; \
                              camera rect {:?}; the game's world from command {} to {:?}, shifted by {:?} (scale {:?}); in it \
                              {} sprites z {:?}, {} rects z {:?}, others [{}]; texture names asset/.. {}, ..#sheet {}; this \
                              mod's sheet on disk {sheet}, battlefield_effects {mode}; this mod draws at z {} with sprites {} #{k}",
                             ctx.draw_map_size(GAME), scope.n, scope.camera, scope.push_at, scope.pop_at, scope.shift,
                             scope.scale, c.sprites, c.z, c.rects, c.rect_z, others.join(", "), c.asset_names, c.sheet_names,
                             made.0, if made.1 { "on" } else { "OFF" }));
                for (what, list) in [("first", &c.first), ("last", &c.last)] {
                    for (i, (name, x, y, z, w, h)) in list.iter().enumerate() {
                        wlog(format!("WORLD   {what} sprite {i}: {name:?} at ({x:.1}, {y:.1}) z {z}, uv size ({w:.4}, {h:.4})"));
                    }
                }
            }
        }
    }
    seen.age += 1;
    let (z, sprites) = seen.plan.unwrap_or((Z_ALONE, false));
    tell(&mut seen, format!("WORLD on: this mod's effects are drawn in the match world (sprites {})",
                            if sprites { "on" } else { "OFF: only what is drawn square by square" }));
    Some(View { scale: scope.scale, shift: scope.shift, z, sprites })
}

/// 画一帧动画：`frame` 那一帧的锚点放在模拟里的 `at` 上。
pub fn sprite(ctx: &mut StableClient<'_>, v: &View, a: &Anim, frame: usize, at: (u64, u64)) -> bool {
    if !v.sprites {
        return false;
    }
    let (uv, pivot) = uv_of(a, frame);
    let (x, y) = v.map(at);
    ctx.draw_sprite(GAME, SHEET_TEX, &StableSpriteParams {
        x,
        y,
        z: v.z,
        pivot_x: pivot.0,
        pivot_y: pivot.1,
        uv,
        sample_nearest: true,
        ..StableSpriteParams::default()
    })
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
        c[AT_SPRITE_Z..AT_SPRITE_Z + 4].copy_from_slice(&z.to_le_bytes());
        put32f(&mut c, AT_SPRITE_UV + 8, 0.25);
        put32f(&mut c, AT_SPRITE_UV + 12, 0.5);
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
        let v = View { scale: sc.scale, shift: sc.shift, z: 7, sprites: true };
        assert_eq!(v.map((672_000, 672_000)), (672.0 + 544.0, 672.0 + 380.5));
        // on the world's whole pixels like the game's own pictures, the camera's fraction of a pixel on top
        assert_eq!(v.map((672_400, 671_600)), (672.0 + 544.0, 672.0 + 380.5));
        assert_eq!(v.px((10.0, 20.0)), (554.0, 400.5));
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
    fn the_census_gives_the_layer_and_whether_sprites_are_safe() {
        let (map, jinx) = ("asset/base/aseprite_resources/ingame/5v5/map#sheet", "asset/league/champion/league_jinx#sheet");
        let names = [map.as_bytes(), jinx.as_bytes()].concat();
        let (a, b) = (map.len(), jinx.len());
        let base = 0x50_0000;
        let cmds = vec![camera(0.0, 0.0, 1.0, 1.0), push(544.0, 544.0, 1.0), sprite_cmd(base, a, 0.0, 0.0, -50),
                        sprite_cmd(base + a, b, 300.0, 410.0, 410), tagged(TAG_RECT), tagged(0x8000_0000_0000_0007),
                        tagged(TAG_POP), sprite_cmd(base, a, 9.0, 9.0, 99_999)];
        let mut fake = frame(&[("Game", cmds)]);
        fake.regions.push((base, names));
        let (list, n) = game_list(&fake, FRAME).unwrap();
        let sc = find_scope(&fake, list, n, true).unwrap();
        let c = census(&fake, list, &sc, 8);
        assert_eq!((c.sprites, c.rects, c.z, c.rect_z), (2, 1, Some((-50, 410)), Some((0, 0))), "what follows the pop is not the world");
        assert_eq!(c.others, vec![(0x8000_0000_0000_0007, 1)]);
        assert!(c.asset_names && c.sheet_names);
        assert_eq!(c.first[1], ("asset/league/champion/league_jinx#sheet".to_string(), 300.0, 410.0, 410, 0.25, 0.5));
        // above the game's highest; sprites only with the sheet on disk
        use super::super::settings::{EFFECTS_AUTO, EFFECTS_SQUARES};
        assert_eq!(plan(&c, true, EFFECTS_AUTO), (411, true));
        assert_eq!(plan(&c, false, EFFECTS_AUTO), (411, false));
        // the player asked for squares only (settings.ini): no sprites
        assert_eq!(plan(&c, true, EFFECTS_SQUARES), (411, false));
        // texture names of another shape: no sprites
        assert_eq!(plan(&Census { asset_names: false, ..c.clone() }, true, EFFECTS_AUTO), (411, false));
        assert_eq!(plan(&Census { sheet_names: false, ..c.clone() }, true, EFFECTS_AUTO), (411, false));
        // nothing drawn by the game: this mod's own layer, no sprites
        assert_eq!(plan(&Census::default(), true, EFFECTS_AUTO), (Z_ALONE, false));
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
        // every cell inside the sheet, every anchor inside its cell
        for a in ANIMS {
            let lines = (a.frames as usize).div_ceil(a.per_row as usize);
            assert!(a.x as usize + a.per_row as usize * a.w as usize <= SHEET.0 as usize, "{}", a.name);
            assert!(a.y as usize + lines * a.h as usize <= SHEET.1 as usize, "{}", a.name);
            assert!(a.ax < a.w && a.ay < a.h && a.frames > 0 && a.ticks > 0, "{}", a.name);
        }
    }
}
