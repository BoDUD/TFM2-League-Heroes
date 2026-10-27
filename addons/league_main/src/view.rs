//! 战场上的大小（游戏 0.6.4 起，Windows；这里写的是 0.6.4 的地址，0.6.5 的在 src/build.rs）：战场画身体的 0x2aaf630 只给绘制命令 UV，不给大小——Skia 按「UV × 图的真实像素」
//! 画，锚点按帧的宽高算。所以战场取到的是真实的高清帧（src/lookup.rs 的战场影子表），画出来 PPU 倍大；这里把实体的
//! 绘制缩放（显示世界实体值 +0x1b4，战场绘制函数 0x2abfdc0 读的那个数，绕实体位置缩放整套命令）写成「游戏的值 ÷ PPU」，
//! 大小、锚点都回到 1 倍（0.4.3 没有这一步：「游戏里变成了巨人」）。
//!
//! 和凯隐 / 佛耶戈附加包挂在同一个显示更新槽（rva 0x3c82db8，函数 0x23312a0，核对开头 24 个字节）：先调用槽里原来的
//! 函数，再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始），英雄 id（+0x40 / +0x48）登记了的
//! 实体写缩放。游戏自己的值每帧记下（[`Scale`]：是我们上一帧写的就沿用记下的，不是就当作游戏的新值），不会除两次。
//! 不改动作名：战场影子表里每个动作都是高清帧，眩晕之类不按动作名画的时候也一样（「被宝石打中后模型突然变小」）。
//!
//! 认英雄按身体用哪套图（值 +0x50 / +0x58 / +0x60 的资源名，每个实体平时就是自己的英雄 id），读不到才看英雄 id：佛耶戈
//! 附加包附身时把被附身英雄的资源名抄到佛耶戈的这里，id 还是 league_viego——附身亚索 / 泽丽 / 弗拉基米尔 / 卡尔玛时画的是
//! 他们的高清帧，按 id 认就不缩，画出来 2～3 倍大（用户 2026-10-12「Ppu的英雄佛爷戈不会变身失败吧？」）。不再是高清英雄的
//! 实体（附身结束）把游戏的值写回去。
//!
//! 画身体的那一刻再认一次（0.6.50，用户：「佛耶戈变身高清英雄的时候 还是会变的超级大」）：佛耶戈附加包也挂在这个显示更新槽，
//! 装得比这个包晚，链在我们前面——每帧是游戏的更新 → 我们的缩放 → 它换身体，这一帧我们看到的还是 league_viego，
//! 不缩，接着画出被附身英雄的高清帧（别人的佛耶戈 0.6.3 时在战场绘制里 0x231f990 抄资源名，也在我们之后）。战场绘制先调画身体的
//! 0x2aaf630（0x2abfcd5），之后才在 0x2abfdc0 读 +0x1b4：所以 0x2aaf630 的钩子先按此刻的资源名再算一遍，是高清英雄、
//! 而这一帧的更新没缩过（佛耶戈），就在这里写 ÷ PPU（另记一份「画时」的记录，附身结束时写回游戏的值）；更新已经缩过的
//! 照旧不动，不会除两次。下一帧更新看到的已是被附身英雄、自己还没有记录：从「画时」的记录接着算（0.7.1，用户：「佛耶戈
//! 不能变身PPU英雄？」）——游戏没把 +0x1b4 写回自己的值时，否则会把画时写的 ÷ PPU 当成游戏的值再除一次，附身后小 PPU 倍。
//!
//! 只缩身体（0.6.30，用户：「回城时脚下的特效会被遮挡」「英雄脚下的阴影也被遮挡了」）：+0x1b4 套在战场画身体的函数
//! 0x2aaf630 交出的整组绘制命令外面（0x2abfdc0：组头插一条缩放命令 0x…11、组尾一条恢复 0x…12），组里除了身体还有阴影、
//! 脚下的圆圈、眩晕 / 嘲讽标记、读条——跟着缩成 1/PPU（艾希 1/5.5），看着像被身体挡住了。所以在 0x2aaf630 的入口挂钩：
//! 它照常画完，组里不是这个英雄自己那张图（`…/league_<英雄>#sheet`）的命令，连着的一段段各套一对「放大 PPU 倍」的
//! 缩放 / 恢复命令（和游戏自己的一样：绕同一个点、平移 (1 - k) × 点、x y 都乘 k），外面那层 ÷ PPU 一抵消，就是游戏
//! 原来的大小；身体照旧 ÷ PPU。别处读 +0x1b4 的画法不受影响。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex, Once};

use super::build::Build;
use super::hd::{self, Hero};
use super::wlog;

const TABLE: usize = 0x138;
const TABLE_MASK: usize = 0x140;
const TABLE_ITEMS: usize = 0x150;
const ELEM: usize = 0x1d0;
const VALUE: usize = 8;
const NAME_PTR: usize = 0x40;
const NAME_LEN_AT: usize = 0x48;
/// The body's resource name String {cap, ptr, len} (the sprite set it is drawn with; league_viego_soul's RES_CAP).
const RES_PTR: usize = 0x58;
const RES_LEN_AT: usize = 0x60;
const SCALE: usize = 0x1b4;
/// The entity's buffs: {ptr, len} (0x28 bytes an entry, the name's String {cap, ptr, len} at +0).
const BUFFS_PTR: usize = 0xb8;
const BUFFS_LEN: usize = 0xc0;
const BUFF_SIZE: usize = 0x28;
/// Growth lines a session (one for each change of a growing hero's stacks on screen).
const GROW_LINES: usize = 400;

/// One entity's draw scale: the game's own value (base) and what the hook last wrote over it.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Scale {
    pub base: f32,
    pub wrote: f32,
}

/// The scale to write this frame. `cur` is what the entity holds now: the hook's own last value (the game left it
/// alone - keep the base) or a fresh one from the game (a new base). Never divides twice.
pub fn next_scale(prev: Option<Scale>, cur: f32, ppu: f32) -> Scale {
    let base = match prev {
        Some(p) if (cur - p.wrote).abs() <= 1e-6 => p.base,
        _ => cur,
    };
    Scale { base, wrote: base / ppu }
}

/// The record the display update divides from: its own for this entity, else the body draw's. A body swapped after
/// the update (league_viego_soul: the update saw league_viego) was first divided at the body draw; the next update sees
/// the victim's name with no record of its own, and if the game left the body draw's value in +0x1b4 that value would
/// be taken for the game's own and divided again (the possessed hero drawn PPU times too small).
pub fn update_prev(own: Option<Scale>, drawn: Option<Scale>) -> Option<Scale> {
    own.or(drawn)
}

/// The registered hero an entity is drawn as: by its body's resource name (`.../league_zeri#anim` or the bare id) when
/// that is readable, else by its id.
pub fn drawn_as<'a>(heroes: &'a hd::Heroes, res: Option<&str>, id: Option<&str>) -> Option<&'a Hero> {
    heroes.of_name(res.or(id)?)
}

/// What the body draw does with an entity's scale, `cur` being what +0x1b4 holds as it starts.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum AtDraw {
    /// drawn with dense frames: write `wrote` (the display update's own value when it shrank it this frame)
    Write(Scale),
    /// no longer dense and the value is still the one written here: the game's own value back
    Restore(f32),
    Leave,
}

/// The scale at the body draw. `shrunk`: the display update's record for this entity, `drawn`: the body draw's own,
/// `shown`: PPU / size of the hero it is drawn as now (None: not a dense hero). Never divides twice.
pub fn at_draw(shrunk: Option<Scale>, drawn: Option<Scale>, cur: f32, shown: Option<f32>) -> AtDraw {
    let ours = |s: &Scale| (cur - s.wrote).abs() <= 1e-6;
    match shown {
        Some(k) => {
            let prev = match shrunk {
                Some(s) if ours(&s) => Some(s), // shrunk by the display update this frame: its base
                _ => drawn,
            };
            // No record at all and the value already at or under a base of 1 divided: a copy of an entity the
            // display update had shrunk (the match-result screen draws the heroes from copies carrying the divided
            // scale: Zeri 0.350 -> 0.122, Mordekaiser 0.550 -> 0.303, a dot each, 2026-10-15) - taken as divided.
            // The game never scales a unit under 1 / PPU on its own; a growth effect (1.5) still comes out above.
            if prev.is_none() && cur <= 1.0 / k + 1e-4 {
                return AtDraw::Write(Scale { base: cur * k, wrote: cur });
            }
            AtDraw::Write(next_scale(prev, cur, k))
        }
        None => match drawn {
            Some(d) if ours(&d) => AtDraw::Restore(d.base),
            _ => AtDraw::Leave,
        },
    }
}

static HEROES: LazyLock<hd::Heroes> = LazyLock::new(hd::Heroes::new);

struct State {
    scales: Vec<(usize, u64, Scale)>,
    /// the same scales by the entity value's address (what the body draw gets in rdx)
    by_value: Vec<(usize, Scale)>,
    /// the scales the body draw wrote itself, by the entity value's address (a body swapped after the display update)
    drawn: Vec<(usize, Scale)>,
    lines: usize,
    /// heroes whose first command list was logged
    seen: Vec<&'static str>,
    /// "id > hero" pairs whose first body-draw scale was logged
    noted: Vec<String>,
    /// (entity value, stacks) of the growing heroes, the last logged
    grows: Vec<(usize, usize)>,
    /// growth lines written: their own budget, so the draw-scale lines of a long session never silence them (2026-10-23:
    /// the 200 shared lines ran out a second after Cho'Gath came on screen, before his first stack)
    grow_lines: usize,
}

static STATE: Mutex<State> = Mutex::new(State { scales: Vec::new(), by_value: Vec::new(), drawn: Vec::new(), lines: 0,
                                                seen: Vec::new(), noted: Vec::new(), grows: Vec::new(),
                                                grow_lines: 0 });
static PREV: AtomicUsize = AtomicUsize::new(0);
static HOOK: Once = Once::new();

#[link(name = "kernel32")]
extern "system" {
    fn ReadProcessMemory(h: isize, base: *const c_void, buf: *mut c_void, size: usize, read: *mut usize) -> i32;
    fn GetCurrentProcess() -> isize;
    fn GetModuleHandleW(name: *const u16) -> usize;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
}

/// `len` bytes of the game EXE at `rva` (None when unreadable).
/// The game EXE's base in this process.
pub fn module_base() -> usize {
    unsafe { GetModuleHandleW(std::ptr::null()) }
}

pub fn read_rva(rva: usize, len: usize) -> Option<Vec<u8>> {
    let module = unsafe { GetModuleHandleW(std::ptr::null()) };
    if module == 0 {
        return None;
    }
    read(module + rva, len)
}

fn read(addr: usize, len: usize) -> Option<Vec<u8>> {
    let mut buf = vec![0u8; len];
    let mut got = 0usize;
    let ok = unsafe {
        ReadProcessMemory(GetCurrentProcess(), addr as *const c_void, buf.as_mut_ptr() as *mut c_void, len, &mut got)
    };
    (ok != 0 && got == len).then_some(buf)
}

type Update = unsafe extern "system" fn(usize, usize, usize, f32);

unsafe extern "system" fn update(this: usize, a2: usize, world: usize, dt: f32) {
    let prev = PREV.load(Ordering::Acquire);
    if prev != 0 {
        let f: Update = std::mem::transmute(prev);
        f(this, a2, world, dt);
    }
    let _ = std::panic::catch_unwind(|| unsafe { shrink(world) });
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// A String's text from its pointer and length fields (None when it does not look like a name).
unsafe fn string_at<'a>(ptr_at: usize, len_at: usize) -> Option<&'a str> {
    let (n, p) = (q(len_at), q(ptr_at));
    if !(1..=128).contains(&n) || !plausible(p) {
        return None;
    }
    std::str::from_utf8(std::slice::from_raw_parts(p as *const u8, n)).ok()
}

unsafe fn shrink(world: usize) {
    if !plausible(world) {
        return;
    }
    let ctrl = q(world + TABLE);
    let mask = q(world + TABLE_MASK);
    let items = q(world + TABLE_ITEMS);
    if items == 0 || !plausible(ctrl) || mask >= 1 << 16 || (mask + 1) & mask != 0 || items > mask + 1 {
        return;
    }
    let Ok(mut st) = STATE.try_lock() else { return };
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue; // empty or deleted
        }
        let elem = ctrl - (i + 1) * ELEM;
        let v = elem + VALUE;
        let id = string_at(v + NAME_PTR, v + NAME_LEN_AT);
        let res = string_at(v + RES_PTR, v + RES_LEN_AT);
        let key = q(elem) as u64;
        let at = st.scales.iter().position(|e| e.0 == world && e.1 == key);
        let Some(hero) = drawn_as(&HEROES, res, id) else {
            // no longer drawn with dense frames (a possession ended): the game's own value back
            st.by_value.retain(|e| e.0 != v);
            if let Some(k) = at {
                let p = st.scales.remove(k).2;
                let cur = std::ptr::read_unaligned((v + SCALE) as *const f32);
                if (cur - p.wrote).abs() <= 1e-6 {
                    std::ptr::write_unaligned((v + SCALE) as *mut f32, p.base);
                }
                if st.lines < 200 {
                    st.lines += 1;
                    wlog(format!("world {world:#x} #{key} {}: drawn as {} again, draw scale back to {:.3}",
                        id.unwrap_or("?"), res.unwrap_or("?"), p.base));
                }
            }
            continue;
        };
        let name = res.unwrap_or(hero.id);
        let cur = std::ptr::read_unaligned((v + SCALE) as *const f32);
        let s = next_scale(update_prev(at.map(|k| st.scales[k].2), st.drawn.iter().find(|e| e.0 == v).map(|e| e.1)),
                           cur, hero.shown());
        std::ptr::write_unaligned((v + SCALE) as *mut f32, s.wrote);
        match st.by_value.iter().position(|e| e.0 == v) {
            Some(k) => st.by_value[k].1 = s,
            None => {
                st.by_value.push((v, s));
                if st.by_value.len() > 256 {
                    st.by_value.remove(0);
                }
            }
        }
        let changed = match at {
            Some(k) => {
                let b = st.scales[k].2.base != s.base;
                st.scales[k].2 = s;
                b
            }
            None => {
                st.scales.push((world, key, s));
                if st.scales.len() > 256 {
                    st.scales.remove(0);
                }
                true
            }
        };
        if changed && st.lines < 200 {
            st.lines += 1;
            wlog(format!("world {world:#x} #{key} {name}: draw scale {cur:.3} -> {:.3} (base {:.3})", s.wrote, s.base));
        }
    }
}

/// Draw command tags (the enum's niche values at +0) and layout (0xd0 bytes each).
const CMD: usize = 0xd0;
const CMD_SPRITE: u64 = 0x8000_0000_0000_0003;
const CMD_SCALE: u64 = 0x8000_0000_0000_0011;
const CMD_RESTORE: u64 = 0x8000_0000_0000_0012;
/// The mark on a scale / restore command this pack puts round an effect's sprite: the last 8 bytes (+0xc8), which a
/// scale or restore command leaves unread ([`cmd_kind`]).
const OURS_AT: usize = 0xc8;
const OURS: u64 = 0x5846_4555_4741_454c; // "LEAGUEFX"
/// The entity's position (x at +0x17c, y at +0x180 less +0x18c): the point the game scales its commands round.
const POS_X: usize = 0x17c;
const POS_Y: usize = 0x180;
const POS_LIFT: usize = 0x18c;

static ORIG_BODY: AtomicUsize = AtomicUsize::new(0);
static GROW: AtomicUsize = AtomicUsize::new(0);

type BodyDraw = unsafe extern "system" fn(usize, usize, usize, usize, usize, usize, usize, usize) -> usize;
type Grow = unsafe extern "system" fn(usize);

/// 0x2aaf630 (out Vec, entity value, r8, -, -, stack args 6-8; r9 and the 5th are never read): the scale for the body
/// it is drawn with now, the game's body draw, then the extras brought back to the game's size.
unsafe extern "system" fn body_detour(out: usize, ent: usize, a3: usize, _sp: usize, a5: usize, a6: usize, a7: usize,
                                      a8: usize) -> usize {
    let f: BodyDraw = std::mem::transmute(ORIG_BODY.load(Ordering::Acquire));
    let sc = std::panic::catch_unwind(|| unsafe { scale_at_draw(ent) }).ok().flatten();
    let r = f(out, ent, a3, 0, a5, a6, a7, a8);
    if let Some((s, hero)) = sc {
        let _ = std::panic::catch_unwind(|| unsafe { unshrink_extras(out, ent, s, hero) });
    }
    r
}

/// +0x1b4 of the entity value `ent` set for the hero its body is drawn as at this moment (a body swapper renames it
/// after the display update: league_viego_soul) -> its scale and hero when that is a dense hero.
unsafe fn scale_at_draw(ent: usize) -> Option<(Scale, &'static Hero)> {
    if !plausible(ent) {
        return None;
    }
    let id = string_at(ent + NAME_PTR, ent + NAME_LEN_AT);
    let res = string_at(ent + RES_PTR, ent + RES_LEN_AT);
    let hero = drawn_as(&HEROES, res, id);
    let mut st = STATE.try_lock().ok()?;
    let shrunk = st.by_value.iter().find(|e| e.0 == ent).map(|e| e.1);
    let at = st.drawn.iter().position(|e| e.0 == ent);
    let cur = std::ptr::read_unaligned((ent + SCALE) as *const f32);
    match at_draw(shrunk, at.map(|k| st.drawn[k].1), cur, hero.map(|h| h.shown())) {
        AtDraw::Write(s) => {
            let hero = hero?;
            std::ptr::write_unaligned((ent + SCALE) as *mut f32, s.wrote);
            match at {
                Some(k) => st.drawn[k].1 = s,
                None => {
                    st.drawn.push((ent, s));
                    if st.drawn.len() > 256 {
                        st.drawn.remove(0);
                    }
                }
            }
            let updated = shrunk.is_some_and(|p| (cur - p.wrote).abs() <= 1e-6);
            // the pair's String only for a body the update did not shrink (not every dense body every frame)
            let pair = if updated || st.lines >= 200 { None } else { Some(format!("{} > {}", id.unwrap_or("?"), hero.id)) };
            if let Some(pair) = pair.filter(|p| !st.noted.contains(p)) {
                st.lines += 1;
                wlog(format!("{}: drawn as {} at the body draw (the display update saw {}) - draw scale {cur:.3} -> {:.3}",
                    id.unwrap_or("?"), hero.id, res.unwrap_or("?"), s.wrote));
                st.noted.push(pair);
            }
            Some((s, hero))
        }
        AtDraw::Restore(base) => {
            std::ptr::write_unaligned((ent + SCALE) as *mut f32, base);
            st.drawn.retain(|e| e.0 != ent);
            None
        }
        AtDraw::Leave => {
            if at.is_some() {
                st.drawn.retain(|e| e.0 != ent);
            }
            None
        }
    }
}

/// The texture name of a sprite command (its String {cap, ptr, len} at +8).
unsafe fn sprite_name<'a>(cmd: usize) -> Option<&'a str> {
    if q(cmd) as u64 != CMD_SPRITE {
        return None;
    }
    string_at(cmd + 0x10, cmd + 0x18)
}

/// Whether a texture name is the hero's own sheet (`asset/.../league_ashe#sheet`).
pub fn is_body(name: &str, hero: &str) -> bool {
    name.rsplit('/').next().and_then(|n| n.split('#').next()) == Some(hero)
}

/// [first, last] runs of the commands that are neither the body (1) nor a scale / restore command (2).
pub fn extra_runs(kinds: &[u8]) -> Vec<(usize, usize)> {
    let mut runs = Vec::new();
    let mut i = 0;
    while i < kinds.len() {
        if kinds[i] != 0 {
            i += 1;
            continue;
        }
        let s = i;
        while i < kinds.len() && kinds[i] == 0 {
            i += 1;
        }
        runs.push((s, i - 1));
    }
    runs
}

/// `cmd` put in the command Vec {cap, ptr, len} at `out` before index `at` (grown by the game's own grow_one).
unsafe fn insert(out: usize, at: usize, cmd: &[u8; CMD]) {
    let len = q(out + 0x10);
    if len == q(out) {
        let g: Grow = std::mem::transmute(GROW.load(Ordering::Acquire));
        g(out);
    }
    let ptr = q(out + 8);
    std::ptr::copy((ptr + at * CMD) as *const u8, (ptr + (at + 1) * CMD) as *mut u8, (len - at) * CMD);
    std::ptr::copy_nonoverlapping(cmd.as_ptr(), (ptr + at * CMD) as *mut u8, CMD);
    std::ptr::write_unaligned((out + 0x10) as *mut usize, len + 1);
}

/// The commands of the body draw that are not the hero's own sheet (shadow, rings, marks) wrapped back to the game's
/// size: `sc` is the scale written for this draw, `hero` the dense hero the body is drawn as.
unsafe fn unshrink_extras(out: usize, ent: usize, sc: Scale, hero: &Hero) {
    if !plausible(out) || !plausible(ent) {
        return;
    }
    let Ok(mut st) = STATE.try_lock() else { return };
    let cur = std::ptr::read_unaligned((ent + SCALE) as *const f32);
    if (cur - sc.wrote).abs() > 1e-6 || sc.wrote <= 0.0 {
        return; // not shrunk this frame: everything is at the game's size already
    }
    let k = sc.base / sc.wrote;
    let (cap, ptr, len) = (q(out), q(out + 8), q(out + 0x10));
    if len == 0 || len > 256 || cap < len || !plausible(ptr) {
        return;
    }
    let kinds: Vec<u8> = (0..len)
        .map(|i| {
            let c = ptr + i * CMD;
            cmd_kind(q(c) as u64, q(c + OURS_AT) as u64, sprite_name(c).is_some_and(|n| is_body(n, hero.id)))
        })
        .collect();
    let runs = extra_runs(&kinds);
    if !st.seen.contains(&hero.id) && st.lines < 200 {
        st.seen.push(hero.id);
        st.lines += 1;
        let list: Vec<String> = (0..len)
            .map(|i| {
                let c = ptr + i * CMD;
                let tag = (q(c) as u64) & 0xff;
                match sprite_name(c) {
                    Some(n) => format!("{tag}:{}", n.rsplit('/').next().unwrap_or(n)),
                    None => format!("{tag}"),
                }
            })
            .collect();
        wlog(format!("{}: body draw commands [{}], the extras back to the game's size in {} runs (x{k:.3})",
            hero.id, list.join(", "), runs.len()));
    }
    if !kinds.contains(&1) {
        return; // no body found: leave the list as the game made it
    }
    let px = std::ptr::read_unaligned((ent + POS_X) as *const f32);
    let py = std::ptr::read_unaligned((ent + POS_Y) as *const f32)
        - std::ptr::read_unaligned((ent + POS_LIFT) as *const f32);
    let grow = scale_cmd(k, px, py, false);
    let back = restore_cmd(false);
    for &(a, b) in runs.iter().rev() {
        insert(out, b + 1, &back);
        insert(out, a, &grow);
    }
    // a hero that grows with a stack (hd::GROWTH, Cho'Gath's Feast): his body's own commands once more, about his soles
    let Some(&(_, buff, per)) = hd::GROWTH.iter().find(|g| g.0 == hero.id) else { return };
    let n = stacks(ent, buff);
    let g = hd::grown(per, n);
    if !st.grows.iter().any(|e| e.0 == ent && e.1 == n) && st.grow_lines < GROW_LINES {
        st.grows.retain(|e| e.0 != ent);
        st.grows.push((ent, n));
        if st.grows.len() > 64 {
            st.grows.remove(0);
        }
        st.grow_lines += 1;
        wlog(format!("{}: {n} x {buff} - body drawn x{g:.2} about the soles", hero.id));
    }
    if n == 0 {
        return;
    }
    let (sx, sy) = soles(px, py, hero.ppu);
    let up = scale_cmd(g, sx, sy, false);
    let (ptr, len) = (q(out + 8), q(out + 0x10));
    let body: Vec<u8> = (0..len)
        .map(|i| u8::from(sprite_name(ptr + i * CMD).is_some_and(|nm| is_body(nm, hero.id))))
        .collect();
    for (a, b) in body_runs(&body).into_iter().rev() {
        insert(out, b + 1, &back);
        insert(out, a, &up);
    }
}

/// What a command is to the body draw's extras: 2 a game scale / restore, 1 the body's own sheet, 0 anything else - a
/// scale / restore pair this pack put round an effect's sprite (`mark` == [`OURS`]) too: it belongs to that effect, so
/// the extras' own "back to the game's size" pair goes round it, and the effect is shrunk from the game's size.
pub fn cmd_kind(tag: u64, mark: u64, body: bool) -> u8 {
    match tag {
        CMD_SCALE | CMD_RESTORE if mark != OURS => 2,
        _ if body => 1,
        _ => 0,
    }
}

/// A scale command: x and y times `k` about (`px`, `py`) - the game's own layout (translation (1 - k) x the point at
/// +8 / +0xc, the factors at +0x24 / +0x28); `ours` marks it ([`cmd_kind`]).
pub fn scale_cmd(k: f32, px: f32, py: f32, ours: bool) -> [u8; CMD] {
    let mut c = restore_cmd(ours);
    c[..8].copy_from_slice(&CMD_SCALE.to_le_bytes());
    c[8..12].copy_from_slice(&((1.0 - k) * px).to_le_bytes());
    c[12..16].copy_from_slice(&((1.0 - k) * py).to_le_bytes());
    c[0x24..0x28].copy_from_slice(&k.to_le_bytes());
    c[0x28..0x2c].copy_from_slice(&k.to_le_bytes());
    c
}

pub fn restore_cmd(ours: bool) -> [u8; CMD] {
    let mut c = [0u8; CMD];
    c[..8].copy_from_slice(&CMD_RESTORE.to_le_bytes());
    if ours {
        c[OURS_AT..OURS_AT + 8].copy_from_slice(&OURS.to_le_bytes());
    }
    c
}

static ORIG_EFFECT: AtomicUsize = AtomicUsize::new(0);
static EFFECTS_SEEN: Mutex<Vec<&'static str>> = Mutex::new(Vec::new());

type EffectDraw = unsafe extern "system" fn(usize, usize, usize, usize) -> usize;

/// The view node draw (Build::effect_draw: the command Vec it returns in rcx, the node in rdx, r8 / r9 its own): as the
/// game draws it, then every sprite command of a [`hd::DRAWN_EFFECTS`] sheet wrapped in a 1 / PPU scale about the
/// sprite's top-left corner (+0x78 / +0x7c). The game places that corner with the frame's size divided by PPU (the
/// anim table, src/lookup.rs) but draws the picture UV x the texture's real pixels - a square a game pixel, PPU times
/// too big, hanging right and down from the corner; shrunk about the corner it covers its frame at 1 / PPU.
unsafe extern "system" fn effect_detour(out: usize, node: usize, a3: usize, a4: usize) -> usize {
    let f: EffectDraw = std::mem::transmute(ORIG_EFFECT.load(Ordering::Acquire));
    let r = f(out, node, a3, a4);
    let _ = std::panic::catch_unwind(|| unsafe { shrink_effects(out) });
    r
}

unsafe fn shrink_effects(out: usize) {
    if !plausible(out) {
        return;
    }
    let (cap, len) = (q(out), q(out + 0x10));
    // cap usize::MAX: the caller's None (0x1b2c388 checks it)
    if cap == usize::MAX || len == 0 || len > 256 || cap < len || !plausible(q(out + 8)) {
        return;
    }
    let mut i = 0;
    while i < q(out + 0x10) {
        let c = q(out + 8) + i * CMD;
        let hero = sprite_name(c).and_then(|n| HEROES.of_name(n)).filter(|h| hd::DRAWN_EFFECTS.contains(&h.id));
        let Some(hero) = hero else {
            i += 1;
            continue;
        };
        let (x, y) = (std::ptr::read_unaligned((c + 0x78) as *const f32), std::ptr::read_unaligned((c + 0x7c) as *const f32));
        let k = 1.0 / hero.ppu;
        insert(out, i + 1, &restore_cmd(true));
        insert(out, i, &scale_cmd(k, x, y, true));
        i += 3;
        if let Ok(mut seen) = EFFECTS_SEEN.try_lock() {
            if !seen.contains(&hero.id) {
                seen.push(hero.id);
                wlog(format!("{}: effect picture drawn x{k:.3} about its corner ({x:.1}, {y:.1})", hero.id));
            }
        }
    }
}

/// The instances of the buff `name` on the entity value `ent` (its buff list: {ptr, len} at +0xb8, 0x28 bytes an entry,
/// the name's String at +8; league_nasus reads its form the same way).
unsafe fn stacks(ent: usize, name: &str) -> usize {
    let (bp, bn) = (q(ent + BUFFS_PTR), q(ent + BUFFS_LEN));
    if !plausible(bp) || bn > 4096 {
        return 0;
    }
    (0..bn)
        .filter(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == name.len() && std::slice::from_raw_parts(p as *const u8, n) == name.as_bytes()
        })
        .count()
}

/// The point a growing body is scaled about: its soles, hd::FEET game pixels under the unit's position - in the body
/// draw's own coordinates, where the dense frame is still PPU times its shown size.
pub fn soles(px: f32, py: f32, ppu: f32) -> (f32, f32) {
    (px, py + hd::FEET * ppu)
}

/// [first, last] runs of the body's own commands (1).
pub fn body_runs(kinds: &[u8]) -> Vec<(usize, usize)> {
    let flipped: Vec<u8> = kinds.iter().map(|&k| u8::from(k != 1)).collect();
    extra_runs(&flipped)
}

fn install(b: &Build) -> Result<(usize, usize), String> {
    let module = unsafe { GetModuleHandleW(std::ptr::null()) };
    if module == 0 {
        return Err("no module handle".into());
    }
    let slot = module + b.display_slot;
    let cur = read(slot, 8).map(|b| usize::from_le_bytes(b.try_into().unwrap())).ok_or("the slot is unreadable")?;
    if !plausible(cur) {
        return Err(format!("the slot holds {cur:#x}"));
    }
    PREV.store(cur, Ordering::Release);
    let mut old = 0u32;
    if unsafe { VirtualProtect(slot as *mut c_void, 8, 0x04, &mut old) } == 0 {
        return Err("VirtualProtect failed".into());
    }
    unsafe { std::ptr::write_volatile(slot as *mut usize, update as Update as usize) };
    let mut tmp = 0u32;
    unsafe { VirtualProtect(slot as *mut c_void, 8, old, &mut tmp) };
    Ok((slot, cur))
}

/// 加载时换槽（一个进程只换一次）。
pub fn install_once(b: &'static Build) {
    HOOK.call_once(|| {
        let module = unsafe { GetModuleHandleW(std::ptr::null()) };
        match install(b) {
            Ok((slot, prev)) => wlog(format!(
                "battlefield scale on: display slot {slot:#x} now calls this pack, then {} ({prev:#x})",
                if prev == module + b.display_fn { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("battlefield scale off ({e})")),
        }
        GROW.store(module + b.cmd_grow, Ordering::Release);
        let r = unsafe {
            super::lookup::hook(module + b.body_draw,
                body_detour as unsafe extern "system" fn(usize, usize, usize, usize, usize, usize, usize, usize) -> usize
                    as usize, &ORIG_BODY)
        };
        wlog(format!("body draw hooked ({r:?}): shadows, rings and marks round a dense hero at the game's size"));
        if b.effect_draw != 0 {
            let r = unsafe {
                super::lookup::hook_keeping_r9(module + b.effect_draw,
                    effect_detour as EffectDraw as usize, &ORIG_EFFECT)
            };
            wlog(format!("effect draw hooked ({r:?}): {} at 1 / PPU", hd::DRAWN_EFFECTS.join(", ")));
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_scale_is_divided_once() {
        let s = next_scale(None, 1.0, 3.0);
        assert_eq!(s, Scale { base: 1.0, wrote: 1.0 / 3.0 });
        let s = next_scale(Some(s), 1.0 / 3.0, 3.0); // the game left our value
        assert_eq!(s.base, 1.0);
        let s = next_scale(Some(s), 1.0, 3.0); // the game wrote its own again
        assert_eq!(s.base, 1.0);
        let s = next_scale(Some(s), 1.5, 3.0); // a new base (a growth effect)
        assert_eq!(s, Scale { base: 1.5, wrote: 0.5 });
    }

    #[test]
    fn an_effects_own_scale_pair_is_part_of_the_extras() {
        let ours = scale_cmd(0.75, 10.0, -20.0, true);
        let mark = u64::from_le_bytes(ours[OURS_AT..].try_into().unwrap());
        assert_eq!(cmd_kind(CMD_SCALE, mark, false), 0);
        let back = restore_cmd(true);
        assert_eq!(cmd_kind(CMD_RESTORE, u64::from_le_bytes(back[OURS_AT..].try_into().unwrap()), false), 0);
        // the game's own scale commands and the body's sheet as before
        assert_eq!(cmd_kind(CMD_SCALE, 0, false), 2);
        assert_eq!(cmd_kind(CMD_RESTORE, 0, false), 2);
        assert_eq!(cmd_kind(CMD_SPRITE, 0, true), 1);
        assert_eq!(cmd_kind(CMD_SPRITE, 0, false), 0);
        // body, [ours: scale, effect, restore], shadow: one run of extras round the effect and its pair
        assert_eq!(extra_runs(&[1, 0, 0, 0, 0]), vec![(1, 4)]);
        // x' = k x + (1 - k) p: the corner stays where it is
        let f = |at: usize| f32::from_le_bytes(ours[at..at + 4].try_into().unwrap());
        assert_eq!((f(8), f(12), f(0x24), f(0x28)), (2.5, -5.0, 0.75, 0.75));
        assert_eq!(&scale_cmd(2.0, 1.0, 1.0, false)[OURS_AT..], &[0u8; 8]);
    }

    #[test]
    fn only_the_heros_own_sheet_is_the_body() {
        assert!(is_body("asset/league/champions/league_ashe#sheet", "league_ashe"));
        assert!(is_body("asset/base/aseprite_resources/champions/league_ashe#sheet", "league_ashe"));
        assert!(!is_body("asset/base/sprite/circle", "league_ashe"));
        assert!(!is_body("asset/base/aseprite_resources/skill_effect/stun_effect#sheet", "league_ashe"));
        assert!(!is_body("asset/league/champions/league_ashe_fx#sheet", "league_ashe"));
    }

    #[test]
    fn a_growing_body_is_scaled_about_its_soles() {
        assert_eq!(body_runs(&[0, 1, 1, 0, 2, 1]), vec![(1, 2), (5, 5)]);
        assert_eq!(body_runs(&[0, 2, 0]), vec![]);
        assert_eq!(soles(100.0, 50.0, 1.2), (100.0, 50.0 + 11.5 * 1.2));
        assert_eq!(hd::grown(0.05, 0), 1.0);
        assert!((hd::grown(0.05, 6) - 1.3).abs() < 1e-6);
        // Cho'Gath (2026-10-26): 30 % a bite, twice his size at most
        assert!((hd::grown(0.30, 1) - 1.3).abs() < 1e-6);
        assert!((hd::grown(0.30, 3) - 1.9).abs() < 1e-6);
        assert_eq!(hd::grown(0.30, 4), hd::GROW_CAP);
        assert_eq!(hd::grown(0.30, 12), hd::GROW_CAP);
        assert!(hd::GROWTH.iter().any(|g| g.0 == "league_chogath" && g.1 == "league_chogath_r_stack"));
    }

    #[test]
    fn the_extras_are_wrapped_in_runs() {
        assert_eq!(extra_runs(&[0, 0, 1, 0]), vec![(0, 1), (3, 3)]);
        assert_eq!(extra_runs(&[1]), vec![]);
        assert_eq!(extra_runs(&[0, 2, 0, 1, 1, 0, 0]), vec![(0, 0), (2, 2), (5, 6)]);
    }

    #[test]
    fn the_body_draw_shrinks_a_body_swapped_after_the_update() {
        let k = 2.2;
        // a dense hero the display update shrank this frame: its value kept, no second division
        let up = Scale { base: 1.0, wrote: 1.0 / k };
        assert_eq!(at_draw(Some(up), None, 1.0 / k, Some(k)), AtDraw::Write(up));
        // Viego renamed after the update (it saw league_viego): divided here, from the game's value
        let s = match at_draw(None, None, 1.0, Some(k)) {
            AtDraw::Write(s) => s,
            other => panic!("{other:?}"),
        };
        assert_eq!(s, Scale { base: 1.0, wrote: 1.0 / k });
        // the next frame, the game left our value: the same, not divided again
        assert_eq!(at_draw(None, Some(s), 1.0 / k, Some(k)), AtDraw::Write(s));
        // the game wrote its own value again
        assert_eq!(at_draw(None, Some(s), 1.0, Some(k)), AtDraw::Write(s));
        // possessing another dense hero (another PPU / size) while our value is still there
        assert_eq!(at_draw(None, Some(s), 1.0 / k, Some(3.0)), AtDraw::Write(Scale { base: 1.0, wrote: 1.0 / 3.0 }));
        // a copy with the divided value and no record (the match-result screen): taken as divided, not divided again
        assert_eq!(at_draw(None, None, 1.0 / k, Some(k)), AtDraw::Write(Scale { base: 1.0, wrote: 1.0 / k }));
        assert_eq!(at_draw(None, None, 0.55 / 2.0, Some(2.0)), AtDraw::Write(Scale { base: 0.55, wrote: 0.275 }));
        // a growth effect's value with no record: divided
        assert_eq!(at_draw(None, None, 1.5, Some(k)), AtDraw::Write(Scale { base: 1.5, wrote: 1.5 / k }));
        // the possession over: our value goes, the game's comes back; nothing to do once the game rewrote it
        assert_eq!(at_draw(None, Some(s), 1.0 / k, None), AtDraw::Restore(1.0));
        assert_eq!(at_draw(None, Some(s), 1.0, None), AtDraw::Leave);
        assert_eq!(at_draw(None, None, 1.0, None), AtDraw::Leave);
    }

    #[test]
    fn a_swapped_body_is_divided_once_frame_after_frame() {
        let k = 2.2;
        // frame 1: the update saw league_viego (nothing), the add-on swapped the body, the body draw divided
        let AtDraw::Write(first) = at_draw(None, None, 1.0, Some(k)) else { panic!() };
        // frame 2, the game left the body draw's value: the update sees the victim with no record of its own
        let s = next_scale(update_prev(None, Some(first)), 1.0 / k, k);
        assert_eq!(s, Scale { base: 1.0, wrote: 1.0 / k });
        assert_ne!(next_scale(None, 1.0 / k, k).wrote, s.wrote); // without the body draw's record: divided twice
        // frame 2, the game wrote its own value again: the same
        assert_eq!(next_scale(update_prev(None, Some(first)), 1.0, k), s);
        // the body draw of frame 2 keeps the update's value
        assert_eq!(at_draw(Some(s), Some(first), 1.0 / k, Some(k)), AtDraw::Write(s));
        // from frame 3 the update has its own record
        assert_eq!(next_scale(update_prev(Some(s), Some(first)), 1.0 / k, k), s);
    }

    #[test]
    fn a_possessing_viego_is_shrunk_as_his_victim() {
        let h = hd::Heroes::new();
        let as_ = |res, id| drawn_as(&h, res, id).map(|h| h.id);
        assert_eq!(as_(Some("league_zeri"), Some("league_viego")), Some("league_zeri"));
        assert_eq!(as_(Some("champions/league_yasuo#anim"), Some("league_viego")), Some("league_yasuo"));
        assert_eq!(as_(Some("league_viego"), Some("league_viego")), None); // the possession over
        assert_eq!(as_(Some("league_amumu"), Some("league_viego")), None); // a plain victim (Darius has dense frames since league.dll 0.7.48, Annie since 0.7.150)
        assert_eq!(as_(None, Some("league_karma")), Some("league_karma")); // no resource name read: the id
        assert_eq!(as_(Some("league_karma"), Some("league_karma")), Some("league_karma"));
    }
}
