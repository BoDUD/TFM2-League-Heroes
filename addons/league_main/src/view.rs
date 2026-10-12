//! 战场上的高清帧（游戏 0.6.3，Windows）：和凯隐 / 佛耶戈附加包（league_kayn_form、league_viego_soul 的 view.rs）挂在
//! 同一个显示更新槽（rva 0x3c31358，函数 0x2808e30，加载时核对开头 24 个字节）。先调用槽里原来的函数（原版的，或别的
//! mod 先挂上的，一个接一个），再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始）。
//!
//! 英雄 id（值 +0x40 / +0x48）在 hd::HEROES 里的实体：正在播的动画名（+0x68 / +0x70 / +0x78 的 String）换成 `hd_<tag>`
//! （同一张图里 PPU 倍密的那份），**绘制缩放（值 +0x1b4）写成「游戏的值 ÷ PPU」**：工坊 Rin 的 tfm2_ppu_core 改的就是
//! 战场实体绘制函数（rva 0x231f310）里 0x231fb80 那条 `movss xmm1, [r13 + 0x1b4]` 读的这个数，|缩放 − 1| > 0.001 时游戏
//! 走带缩放的那条路，把它写进绘制命令的 x、y 缩放。本包不改游戏的指令，只写这个字段；游戏自己的值每帧记下来
//! （hd::next_scale：是我们上一帧写的就沿用记下的，不是就当作游戏的新值），不会除两次。动画没有高清份的（别的 mod 换上
//! 的名字）就换回游戏的值。卡牌、图鉴、头像画的是 `idle`（另一条路），还是 1 倍。
//!
//! 日志 `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league.log`：每个实体第一次出现记一行（id、资源名、动画、+0x1b4 和
//! 它前后几个数，最多 MAX_SEEN 行，看缩放平时是不是 1、别的东西会不会动它），高清英雄每次换动画 / 缩放变化记一行，
//! 每 10 秒一行汇总。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex, Once};

use super::hd::{self, Hero, Scale};
use super::wlog;

const FN_RVA: usize = 0x2808e30;
const SLOT_RVA: usize = 0x3c31358;
/// push r15; push r14; push r13; push r12; push rsi; push rdi; push rbp; push rbx; sub rsp, 0x88; movdqa [rsp+..], xmm7
const FN_HEAD: [u8; 24] = [0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x55, 0x53, 0x48, 0x81, 0xec, 0x88,
    0x00, 0x00, 0x00, 0x66, 0x0f, 0x7f, 0x7c, 0x24];
/// The battlefield draw function's read of the scale (only checked: another mod may have patched it).
const DRAW_RVA: usize = 0x231fb80;
const DRAW_HEAD: [u8; 9] = [0xf3, 0x41, 0x0f, 0x10, 0x8d, 0xb4, 0x01, 0x00, 0x00];
const TABLE: usize = 0x138;
const TABLE_MASK: usize = 0x140;
const TABLE_ITEMS: usize = 0x150;
const ELEM: usize = 0x1d0;
const VALUE: usize = 8;
const NAME_PTR: usize = 0x40;
const NAME_LEN_AT: usize = 0x48;
const RES_CAP: usize = 0x50;
const ANIM_CAP: usize = 0x68;
const SCALE: usize = 0x1b4;
const NEAR: [usize; 6] = [0x17c, 0x180, 0x18c, 0x1b0, 0x1b4, 0x1b8];
const MAX_SEEN: usize = 300;
const MAX_HD_LINES: usize = 600;

static HEROES: LazyLock<Vec<Hero>> = LazyLock::new(hd::heroes);

/// (display world, entity key) -> the scale bookkeeping of a dense hero.
struct State {
    scales: Vec<(usize, u64, Scale)>,
    seen: Vec<(usize, u64)>,
    seen_lines: usize,
    hd_lines: usize,
    last_anim: Vec<(usize, u64, String)>,
    calls: u64,
    dense: u64,
    swaps: u64,
    last: Option<std::time::Instant>,
}

static STATE: Mutex<State> = Mutex::new(State {
    scales: Vec::new(),
    seen: Vec::new(),
    seen_lines: 0,
    hd_lines: 0,
    last_anim: Vec::new(),
    calls: 0,
    dense: 0,
    swaps: 0,
    last: None,
});
static PREV: AtomicUsize = AtomicUsize::new(0);
static HOOK: Once = Once::new();

#[link(name = "kernel32")]
extern "system" {
    fn ReadProcessMemory(h: isize, base: *const c_void, buf: *mut c_void, size: usize, read: *mut usize) -> i32;
    fn GetCurrentProcess() -> isize;
    fn GetModuleHandleW(name: *const u16) -> usize;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
    fn GetProcessHeap() -> isize;
    fn HeapAlloc(heap: isize, flags: u32, bytes: usize) -> *mut u8;
    fn HeapFree(heap: isize, flags: u32, mem: *mut u8) -> i32;
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
    let _ = std::panic::catch_unwind(|| unsafe { densify(world) });
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

/// A String {cap, ptr, len} at `at` as text (None when it does not look like one).
unsafe fn string_at<'a>(at: usize, max: usize) -> Option<&'a str> {
    let (cap, ptr, len) = (q(at), q(at + 8), q(at + 16));
    if len == 0 || len > max || cap < len || !plausible(ptr) {
        return None;
    }
    std::str::from_utf8(std::slice::from_raw_parts(ptr as *const u8, len)).ok()
}

/// Replace the String {cap, ptr, len} at `at` with `want` (the game's heap, the old buffer freed like the game does).
unsafe fn put_string(at: usize, want: &[u8]) -> bool {
    let (cap, ptr) = (q(at), q(at + 8));
    let heap = GetProcessHeap();
    let fresh = HeapAlloc(heap, 0, want.len().max(1));
    if fresh.is_null() {
        return false;
    }
    std::ptr::copy_nonoverlapping(want.as_ptr(), fresh, want.len());
    std::ptr::write_unaligned(at as *mut usize, want.len());
    std::ptr::write_unaligned((at + 8) as *mut usize, fresh as usize);
    std::ptr::write_unaligned((at + 16) as *mut usize, want.len());
    if cap > 0 && plausible(ptr) {
        HeapFree(heap, 0, ptr as *mut u8);
    }
    true
}

unsafe fn near(v: usize) -> String {
    NEAR.iter().map(|&o| format!("+{o:#x}={:.3}", f(v + o))).collect::<Vec<_>>().join(" ")
}

unsafe fn densify(world: usize) {
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
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.dense > 0 {
            wlog(format!("10 s: {} display calls, dense heroes drawn {} times, {} animation names swapped",
                st.calls, st.dense, st.swaps));
        }
        st.last = Some(now);
        st.calls = 0;
        st.dense = 0;
        st.swaps = 0;
    }
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue; // empty or deleted
        }
        let elem = ctrl - (i + 1) * ELEM;
        let v = elem + VALUE;
        let key = q(elem) as u64;
        let (n, p) = (q(v + NAME_LEN_AT), q(v + NAME_PTR));
        if !(1..=64).contains(&n) || !plausible(p) {
            continue;
        }
        let Ok(name) = std::str::from_utf8(std::slice::from_raw_parts(p as *const u8, n)) else { continue };
        if !st.seen.contains(&(world, key)) {
            st.seen.push((world, key));
            if st.seen.len() > 4096 {
                st.seen.remove(0);
            }
            if st.seen_lines < MAX_SEEN {
                st.seen_lines += 1;
                wlog(format!("world {world:#x} #{key} {name}: resource {}, playing {}, {}",
                    string_at(v + RES_CAP, 64).unwrap_or("?"), string_at(v + ANIM_CAP, 64).unwrap_or("?"), near(v)));
            }
        }
        let Some(hero) = HEROES.iter().find(|h| h.id == name) else { continue };
        st.dense += 1;
        let Some(cur) = string_at(v + ANIM_CAP, 64) else { continue };
        let cur = cur.to_string();
        let want = hd::anim_for(&cur, &hero.tags);
        let playing = want.clone().unwrap_or_else(|| cur.clone());
        if let Some(w) = &want {
            if put_string(v + ANIM_CAP, w.as_bytes()) {
                st.swaps += 1;
            }
        }
        let dense = playing.starts_with(hd::PREFIX);
        let s_now = f(v + SCALE);
        let at = st.scales.iter().position(|e| e.0 == world && e.1 == key);
        let prev = at.map(|k| st.scales[k].2);
        let wrote = if dense {
            let s = hd::next_scale(prev, s_now, hero.ppu);
            std::ptr::write_unaligned((v + SCALE) as *mut f32, s.wrote);
            match at {
                Some(k) => st.scales[k].2 = s,
                None => {
                    st.scales.push((world, key, s));
                    if st.scales.len() > 256 {
                        st.scales.remove(0);
                    }
                }
            }
            Some(s)
        } else {
            // a name without a dense copy: the game's own scale back
            if let (Some(k), Some(p)) = (at, prev) {
                if (s_now - p.wrote).abs() <= 1e-6 {
                    std::ptr::write_unaligned((v + SCALE) as *mut f32, p.base);
                }
                st.scales.remove(k);
            }
            None
        };
        // a line per animation change of each dense hero (and any scale the game itself changed)
        let line = format!("{playing} {}", wrote.map_or("plain".into(), |s| format!("base {:.3}", s.base)));
        let changed = match st.last_anim.iter().position(|e| e.0 == world && e.1 == key) {
            Some(k) if st.last_anim[k].2 == line => false,
            Some(k) => {
                st.last_anim[k].2 = line.clone();
                true
            }
            None => {
                st.last_anim.push((world, key, line.clone()));
                if st.last_anim.len() > 256 {
                    st.last_anim.remove(0);
                }
                true
            }
        };
        if changed && st.hd_lines < MAX_HD_LINES {
            st.hd_lines += 1;
            wlog(format!("world {world:#x} #{key} {name}: game played {cur} -> {playing}, scale read {s_now:.3} -> {}",
                wrote.map_or("left".into(), |s| format!("{:.3} (base {:.3})", s.wrote, s.base))));
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
        let list: Vec<String> = HEROES.iter().map(|h| format!("{} x{} ({} tags)", h.id, h.ppu, h.tags.len())).collect();
        match install() {
            Ok((slot, prev)) => wlog(format!(
                "dense frames on for {}: display slot {slot:#x} now calls this pack, then {} ({prev:#x})",
                list.join(", "),
                if prev == module + FN_RVA { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("dense frames off ({e}): every hero draws its 1x frames")),
        }
    });
}
