//! 战场上的大小（游戏 0.6.3，Windows）：战场画身体的 0x230ec30 只给绘制命令 UV，不给大小——Skia 按「UV × 图的真实像素」
//! 画，锚点按帧的宽高算。所以战场取到的是真实的高清帧（src/lookup.rs 的战场影子表），画出来 PPU 倍大；这里把实体的
//! 绘制缩放（显示世界实体值 +0x1b4，战场绘制函数 0x231fb80 读的那个数，绕实体位置缩放整套命令）写成「游戏的值 ÷ PPU」，
//! 大小、锚点都回到 1 倍（0.4.3 没有这一步：「游戏里变成了巨人」）。
//!
//! 和凯隐 / 佛耶戈附加包挂在同一个显示更新槽（rva 0x3c31358，函数 0x2808e30，核对开头 24 个字节）：先调用槽里原来的
//! 函数，再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始），英雄 id（+0x40 / +0x48）登记了的
//! 实体写缩放。游戏自己的值每帧记下（[`Scale`]：是我们上一帧写的就沿用记下的，不是就当作游戏的新值），不会除两次。
//! 不改动作名：战场影子表里每个动作都是高清帧，眩晕之类不按动作名画的时候也一样（「被宝石打中后模型突然变小」）。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex, Once};

use super::hd::{self, Hero};
use super::wlog;

const FN_RVA: usize = 0x2808e30;
const SLOT_RVA: usize = 0x3c31358;
/// push r15; push r14; push r13; push r12; push rsi; push rdi; push rbp; push rbx; sub rsp, 0x88; movdqa [rsp+..], xmm7
const FN_HEAD: [u8; 24] = [0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x55, 0x53, 0x48, 0x81, 0xec, 0x88,
    0x00, 0x00, 0x00, 0x66, 0x0f, 0x7f, 0x7c, 0x24];
const TABLE: usize = 0x138;
const TABLE_MASK: usize = 0x140;
const TABLE_ITEMS: usize = 0x150;
const ELEM: usize = 0x1d0;
const VALUE: usize = 8;
const NAME_PTR: usize = 0x40;
const NAME_LEN_AT: usize = 0x48;
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

static HEROES: LazyLock<Vec<Hero>> = LazyLock::new(hd::heroes);

struct State {
    scales: Vec<(usize, u64, Scale)>,
    lines: usize,
}

static STATE: Mutex<State> = Mutex::new(State { scales: Vec::new(), lines: 0 });
static PREV: AtomicUsize = AtomicUsize::new(0);
static HOOK: Once = Once::new();

#[link(name = "kernel32")]
extern "system" {
    fn ReadProcessMemory(h: isize, base: *const c_void, buf: *mut c_void, size: usize, read: *mut usize) -> i32;
    fn GetCurrentProcess() -> isize;
    fn GetModuleHandleW(name: *const u16) -> usize;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
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
        let (n, p) = (q(v + NAME_LEN_AT), q(v + NAME_PTR));
        if !(1..=64).contains(&n) || !plausible(p) {
            continue;
        }
        let Ok(name) = std::str::from_utf8(std::slice::from_raw_parts(p as *const u8, n)) else { continue };
        let Some(hero) = HEROES.iter().find(|h| h.id == name) else { continue };
        let key = q(elem) as u64;
        let cur = std::ptr::read_unaligned((v + SCALE) as *const f32);
        let at = st.scales.iter().position(|e| e.0 == world && e.1 == key);
        let s = next_scale(at.map(|k| st.scales[k].2), cur, hero.ppu);
        std::ptr::write_unaligned((v + SCALE) as *mut f32, s.wrote);
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

fn install() -> Result<(usize, usize), String> {
    let module = unsafe { GetModuleHandleW(std::ptr::null()) };
    if module == 0 {
        return Err("no module handle".into());
    }
    if read(module + FN_RVA, FN_HEAD.len()).as_deref() != Some(&FN_HEAD[..]) {
        return Err("not game 0.6.3 (the display handler differs)".into());
    }
    let slot = module + SLOT_RVA;
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
pub fn install_once() {
    HOOK.call_once(|| {
        let module = unsafe { GetModuleHandleW(std::ptr::null()) };
        match install() {
            Ok((slot, prev)) => wlog(format!(
                "battlefield scale on: display slot {slot:#x} now calls this pack, then {} ({prev:#x})",
                if prev == module + FN_RVA { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("battlefield scale off ({e})")),
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
}
