//! 战场上的大小（游戏 0.6.3，Windows）：战场画身体的 0x230ec30 只给绘制命令 UV，不给大小——Skia 按「UV × 图的真实像素」
//! 画，锚点按帧的宽高算。所以战场取到的是真实的高清帧（src/lookup.rs 的战场影子表），画出来 PPU 倍大；这里把实体的
//! 绘制缩放（显示世界实体值 +0x1b4，战场绘制函数 0x231fb80 读的那个数，绕实体位置缩放整套命令）写成「游戏的值 ÷ PPU」，
//! 大小、锚点都回到 1 倍（0.4.3 没有这一步：「游戏里变成了巨人」）。
//!
//! 和凯隐 / 佛耶戈附加包挂在同一个显示更新槽（rva 0x3c31358，函数 0x2808e30，核对开头 24 个字节）：先调用槽里原来的
//! 函数，再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始），英雄 id（+0x40 / +0x48）登记了的
//! 实体写缩放。游戏自己的值每帧记下（[`Scale`]：是我们上一帧写的就沿用记下的，不是就当作游戏的新值），不会除两次。
//! 不改动作名：战场影子表里每个动作都是高清帧，眩晕之类不按动作名画的时候也一样（「被宝石打中后模型突然变小」）。
//!
//! 认英雄按身体用哪套图（值 +0x50 / +0x58 / +0x60 的资源名，每个实体平时就是自己的英雄 id），读不到才看英雄 id：佛耶戈
//! 附加包附身时把被附身英雄的资源名抄到佛耶戈的这里，id 还是 league_viego——附身亚索 / 泽丽 / 弗拉基米尔 / 卡尔玛时画的是
//! 他们的高清帧，按 id 认就不缩，画出来 2～3 倍大（用户 2026-10-12「Ppu的英雄佛爷戈不会变身失败吧？」）。不再是高清英雄的
//! 实体（附身结束）把游戏的值写回去。
//!
//! 只缩身体（0.6.30，用户：「回城时脚下的特效会被遮挡」「英雄脚下的阴影也被遮挡了」）：+0x1b4 套在战场画身体的函数
//! 0x230ec30 交出的整组绘制命令外面（0x231fb80：组头插一条缩放命令 0x…11、组尾一条恢复 0x…12），组里除了身体还有阴影、
//! 脚下的圆圈、眩晕 / 嘲讽标记、读条——跟着缩成 1/PPU（艾希 1/5.5），看着像被身体挡住了。所以在 0x230ec30 的入口挂钩：
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

/// The registered hero an entity is drawn as: by its body's resource name (`.../league_zeri#anim` or the bare id) when
/// that is readable, else by its id.
pub fn drawn_as<'a>(heroes: &'a [Hero], res: Option<&str>, id: Option<&str>) -> Option<&'a Hero> {
    let name = res.or(id)?;
    let last = name.rsplit('/').next()?.split('#').next()?;
    heroes.iter().find(|h| h.id == last)
}

static HEROES: LazyLock<Vec<Hero>> = LazyLock::new(hd::heroes);

struct State {
    scales: Vec<(usize, u64, Scale)>,
    /// the same scales by the entity value's address (what the body draw gets in rdx)
    by_value: Vec<(usize, Scale)>,
    lines: usize,
    /// heroes whose first command list was logged
    seen: Vec<&'static str>,
}

static STATE: Mutex<State> =
    Mutex::new(State { scales: Vec::new(), by_value: Vec::new(), lines: 0, seen: Vec::new() });
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
        let s = next_scale(at.map(|k| st.scales[k].2), cur, hero.shown());
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
/// The entity's position (x at +0x17c, y at +0x180 less +0x18c): the point the game scales its commands round.
const POS_X: usize = 0x17c;
const POS_Y: usize = 0x180;
const POS_LIFT: usize = 0x18c;

static ORIG_BODY: AtomicUsize = AtomicUsize::new(0);
static GROW: AtomicUsize = AtomicUsize::new(0);

type BodyDraw = unsafe extern "system" fn(usize, usize, usize, usize, usize, usize, usize, usize) -> usize;
type Grow = unsafe extern "system" fn(usize);

/// 0x230ec30 (out Vec, entity value, r8, -, -, stack args 6-8; r9 and the 5th are never read): the game's body draw,
/// then the extras brought back to the game's size.
unsafe extern "system" fn body_detour(out: usize, ent: usize, a3: usize, _sp: usize, a5: usize, a6: usize, a7: usize,
                                      a8: usize) -> usize {
    let f: BodyDraw = std::mem::transmute(ORIG_BODY.load(Ordering::Acquire));
    let r = f(out, ent, a3, 0, a5, a6, a7, a8);
    let _ = std::panic::catch_unwind(|| unsafe { unshrink_extras(out, ent) });
    r
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

unsafe fn unshrink_extras(out: usize, ent: usize) {
    if !plausible(out) || !plausible(ent) {
        return;
    }
    let Ok(mut st) = STATE.try_lock() else { return };
    let Some(sc) = st.by_value.iter().find(|e| e.0 == ent).map(|e| e.1) else {
        // a dense hero the display update never shrank under this address: say so once (the hook then does nothing)
        let res = string_at(ent + RES_PTR, ent + RES_LEN_AT);
        if let Some(h) = drawn_as(&HEROES, res, string_at(ent + NAME_PTR, ent + NAME_LEN_AT)) {
            if !st.seen.contains(&h.id) && st.lines < 200 {
                st.seen.push(h.id);
                st.lines += 1;
                wlog(format!("{}: body draw of entity value {ent:#x} with no scale record ({} recorded) - extras left as they are",
                    h.id, st.by_value.len()));
            }
        }
        return;
    };
    let cur = std::ptr::read_unaligned((ent + SCALE) as *const f32);
    if (cur - sc.wrote).abs() > 1e-6 || sc.wrote <= 0.0 {
        return; // not shrunk this frame: everything is at the game's size already
    }
    let k = sc.base / sc.wrote;
    let res = string_at(ent + RES_PTR, ent + RES_LEN_AT);
    let Some(hero) = drawn_as(&HEROES, res, string_at(ent + NAME_PTR, ent + NAME_LEN_AT)) else { return };
    let (cap, ptr, len) = (q(out), q(out + 8), q(out + 0x10));
    if len == 0 || len > 256 || cap < len || !plausible(ptr) {
        return;
    }
    let kinds: Vec<u8> = (0..len)
        .map(|i| {
            let c = ptr + i * CMD;
            match q(c) as u64 {
                CMD_SCALE | CMD_RESTORE => 2,
                _ if sprite_name(c).is_some_and(|n| is_body(n, hero.id)) => 1,
                _ => 0,
            }
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
    let mut grow = [0u8; CMD];
    grow[..8].copy_from_slice(&CMD_SCALE.to_le_bytes());
    grow[8..12].copy_from_slice(&((1.0 - k) * px).to_le_bytes());
    grow[12..16].copy_from_slice(&((1.0 - k) * py).to_le_bytes());
    grow[0x24..0x28].copy_from_slice(&k.to_le_bytes());
    grow[0x28..0x2c].copy_from_slice(&k.to_le_bytes());
    let mut back = [0u8; CMD];
    back[..8].copy_from_slice(&CMD_RESTORE.to_le_bytes());
    for &(a, b) in runs.iter().rev() {
        insert(out, b + 1, &back);
        insert(out, a, &grow);
    }
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
    fn only_the_heros_own_sheet_is_the_body() {
        assert!(is_body("asset/league/champions/league_ashe#sheet", "league_ashe"));
        assert!(is_body("asset/base/aseprite_resources/champions/league_ashe#sheet", "league_ashe"));
        assert!(!is_body("asset/base/sprite/circle", "league_ashe"));
        assert!(!is_body("asset/base/aseprite_resources/skill_effect/stun_effect#sheet", "league_ashe"));
        assert!(!is_body("asset/league/champions/league_ashe_fx#sheet", "league_ashe"));
    }

    #[test]
    fn the_extras_are_wrapped_in_runs() {
        assert_eq!(extra_runs(&[0, 0, 1, 0]), vec![(0, 1), (3, 3)]);
        assert_eq!(extra_runs(&[1]), vec![]);
        assert_eq!(extra_runs(&[0, 2, 0, 1, 1, 0, 0]), vec![(0, 0), (2, 2), (5, 6)]);
    }

    #[test]
    fn a_possessing_viego_is_shrunk_as_his_victim() {
        let h = hd::heroes();
        let as_ = |res, id| drawn_as(&h, res, id).map(|h| h.id);
        assert_eq!(as_(Some("league_zeri"), Some("league_viego")), Some("league_zeri"));
        assert_eq!(as_(Some("champions/league_yasuo#anim"), Some("league_viego")), Some("league_yasuo"));
        assert_eq!(as_(Some("league_viego"), Some("league_viego")), None); // the possession over
        assert_eq!(as_(Some("league_darius"), Some("league_viego")), None); // a plain victim
        assert_eq!(as_(None, Some("league_karma")), Some("league_karma")); // no resource name read: the id
        assert_eq!(as_(Some("league_karma"), Some("league_karma")), Some("league_karma"));
    }
}
