//! 显示更新槽上的只读探测（游戏 0.6.3）：和凯隐附加包（league_kayn_form/src/view.rs）挂在同一个槽，先调用槽里原来的函数
//! （原版的，或先装好的凯隐 / 佛耶戈附加包、变身前置，一个接一个），再走一遍显示世界的实体表，什么都不写。
//!
//! 每个实体记：英雄 id（+0x40 / +0x48）、资源名（+0x58 / +0x60）、正在播的动画（+0x70 / +0x78）、+0x1b4（绘制缩放）和
//! 它前后的 +0x17c +0x180 +0x18c +0x1b0 +0x1b8；同一个实体这些变了才记一行（最多 400 行），每 10 秒一行汇总
//! （调用次数、显示世界、实体数、缩放不是 1 的实体数）。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Mutex, Once};

use super::wlog;

/// 显示处理表里的更新函数（0.6.3）和存它的槽（凯隐附加包同一处）。
const FN_RVA: usize = 0x2808e30;
const SLOT_RVA: usize = 0x3c31358;
/// push r15; push r14; push r13; push r12; push rsi; push rdi; push rbp; push rbx; sub rsp, 0x88; movdqa [rsp+..], xmm7
const FN_HEAD: [u8; 24] = [0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x55, 0x53, 0x48, 0x81, 0xec, 0x88,
    0x00, 0x00, 0x00, 0x66, 0x0f, 0x7f, 0x7c, 0x24];
/// 战场实体绘制函数里读绘制缩放的那条指令（rva 0x231fb80：movss xmm1, [r13 + 0x1b4]），只核对、不改。
const DRAW_RVA: usize = 0x231fb80;
const DRAW_HEAD: [u8; 9] = [0xf3, 0x41, 0x0f, 0x10, 0x8d, 0xb4, 0x01, 0x00, 0x00];
/// 显示世界：实体表（hashbrown：控制字节指针、掩码、元素数）。
const TABLE: usize = 0x138;
const TABLE_MASK: usize = 0x140;
const TABLE_ITEMS: usize = 0x150;
const ELEM: usize = 0x1d0;
const VALUE: usize = 8;
const NAME_PTR: usize = 0x40;
const NAME_LEN: usize = 0x48;
const RES_PTR: usize = 0x58;
const RES_LEN: usize = 0x60;
const ANIM_PTR: usize = 0x70;
const ANIM_LEN: usize = 0x78;
/// 绘制缩放和它前后几个数。
const SCALE: usize = 0x1b4;
const NEAR: [usize; 6] = [0x17c, 0x180, 0x18c, 0x1b0, 0x1b4, 0x1b8];
const MAX_LINES: usize = 400;

struct Stats {
    calls: u64,
    worlds: Vec<usize>,
    entities: u64,
    scaled: u64,
    last: Option<std::time::Instant>,
    seen: Vec<(usize, u64, String)>, // (world, entity, what was logged)
    lines: usize,
}

static STATS: Mutex<Stats> =
    Mutex::new(Stats { calls: 0, worlds: Vec::new(), entities: 0, scaled: 0, last: None, seen: Vec::new(), lines: 0 });
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
    let _ = std::panic::catch_unwind(|| unsafe { probe(world) });
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

unsafe fn f(addr: usize) -> f32 {
    std::ptr::read_unaligned(addr as *const f32)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// A String {cap, ptr, len} field at `at` (ptr at `ptr`, len at `len`) as text, if it looks like one.
unsafe fn text(ptr_at: usize, len_at: usize) -> Option<String> {
    let (p, n) = (q(ptr_at), q(len_at));
    if n == 0 || n > 200 || !plausible(p) {
        return None;
    }
    std::str::from_utf8(std::slice::from_raw_parts(p as *const u8, n)).ok().map(str::to_string)
}

unsafe fn probe(world: usize) {
    if !plausible(world) {
        return;
    }
    let ctrl = q(world + TABLE);
    let mask = q(world + TABLE_MASK);
    let items = q(world + TABLE_ITEMS);
    if items == 0 || !plausible(ctrl) || mask >= 1 << 16 || (mask + 1) & mask != 0 || items > mask + 1 {
        return;
    }
    let mut st = match STATS.try_lock() {
        Ok(s) => s,
        Err(_) => return,
    };
    st.calls += 1;
    if !st.worlds.contains(&world) && st.worlds.len() < 8 {
        st.worlds.push(world);
    }
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.entities > 0 {
            wlog(format!("10 s: {} display calls, worlds {:x?}, {} entity visits, {} with a draw scale other than 1",
                st.calls, st.worlds, st.entities, st.scaled));
        }
        st.last = Some(now);
        st.calls = 0;
        st.entities = 0;
        st.scaled = 0;
        st.worlds.clear();
    }
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue; // empty or deleted
        }
        let elem = ctrl - (i + 1) * ELEM;
        let v = elem + VALUE;
        st.entities += 1;
        let scale = f(v + SCALE);
        if (scale - 1.0).abs() > 0.001 {
            st.scaled += 1;
        }
        if st.lines >= MAX_LINES {
            continue;
        }
        let key = q(elem) as u64;
        let name = text(v + NAME_PTR, v + NAME_LEN).unwrap_or_else(|| "?".into());
        let res = text(v + RES_PTR, v + RES_LEN).unwrap_or_else(|| "?".into());
        let anim = text(v + ANIM_PTR, v + ANIM_LEN).unwrap_or_else(|| "?".into());
        let near: Vec<String> = NEAR.iter().map(|&o| format!("+{o:#x}={:.3}", f(v + o))).collect();
        // one line per change of what matters (the animation changes all the time: only its first one)
        let what = format!("{name} | {res} | {}", near.join(" "));
        if st.seen.iter().any(|s| s.0 == world && s.1 == key && s.2 == what) {
            continue;
        }
        st.seen.retain(|s| !(s.0 == world && s.1 == key));
        st.seen.push((world, key, what.clone()));
        if st.seen.len() > 256 {
            st.seen.remove(0);
        }
        st.lines += 1;
        wlog(format!("world {world:#x} #{key}: {what} (playing {anim})"));
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
    match read(module + DRAW_RVA, DRAW_HEAD.len()) {
        Some(b) if b == DRAW_HEAD => wlog("the draw-scale read at rva 0x231fb80 is the game's own (movss xmm1, [r13+0x1b4])"),
        Some(b) => wlog(format!("the draw-scale read at rva 0x231fb80 is patched by another mod: {b:02x?}")),
        None => wlog("the draw-scale read at rva 0x231fb80 is unreadable"),
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
                "probe on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if prev == module + FN_RVA { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("probe off ({e})")),
        }
    });
}
