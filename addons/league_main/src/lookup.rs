//! 按名字取资源的两个函数上的钩子（游戏 0.6.3）：0x20fc10 取 `<路径>#anim` 动画表，0x16d040 取 `<路径>#sheet` 贴图。
//! 入口那 12 个字节（push rbp … push rbx）换成 `mov rax, 跳板; jmp rax`；跳板把栈顶的地址（返回地址在那里）放进 r9
//! 交给本包的函数，原函数照常执行（原来的 12 个字节 + 跳回入口 + 12）。
//!
//! 1. 诊断：每个调用处（rva）第一次取英雄图时记一行，登记的高清英雄的每个（调用处，名字）也记一行——用来找卡牌、
//!    图鉴、头像各是哪段代码画的（BP 卡牌改好后用户：「游戏百科里面的不对」「选完英雄后又不对了」）。
//! 2. 游戏百科的英雄格子和头像：rva 0x24b44b0 按 `idle` 第 0 帧、以帧中心加 champion_view 的脸点为准裁一块
//!    （格子宽高 ÷ s），画成 min(格子, 帧 × s) 大小；动作名 `idle` 是内联比较的，改不了名字。所以从这里（返回地址
//!    0x24b4574）取登记英雄的动画表时，交回一份**影子表**：把表的桶整块复制一份，副本里 `idle` 和 `hd_idle` 两项
//!    的帧互换（帧数据不复制，原表照旧归游戏所有，影子表永不释放）；再把它栈上还没读的三个参数改成高清帧的：
//!    脸点 x、y 乘 PPU，s 除以 PPU——裁出的是同一块画面，像素细 PPU 倍。

use std::collections::HashMap;
use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex, Once};

use super::hd::{self, Hero};
use super::wlog;

const PROLOGUE: [u8; 12] = [0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53];
const ANIM_RVA: usize = 0x20fc10;
const SHEET_RVA: usize = 0x16d040;
/// 0x24b44b0's anim lookup returns here; its frame: rbp = rsp + 0x80 and the stack arguments face x, face y and the
/// scale at rbp + 0x110, + 0x118, + 0x120 (read only after this lookup).
const ICON_RET: usize = 0x24b4574;
const ICON_RBP: usize = 0x80;
const ICON_FACE_X: usize = 0x110;
const ICON_FACE_Y: usize = 0x118;
const ICON_SCALE: usize = 0x120;
/// The anim table (hashbrown): ctrl, bucket mask, growth left, items, hasher (0x30 bytes); 0x30-byte buckets below
/// ctrl: key String {cap, ptr, len}, frames Vec {cap, ptr, len}.
const BUCKET: usize = 0x30;
const MAX_LINES: usize = 400;

static HEROES: LazyLock<Vec<Hero>> = LazyLock::new(hd::heroes);
static MODULE: AtomicUsize = AtomicUsize::new(0);
static ORIG_ANIM: AtomicUsize = AtomicUsize::new(0);
static ORIG_SHEET: AtomicUsize = AtomicUsize::new(0);
static HOOK: Once = Once::new();

struct Probe {
    rvas: Vec<(usize, usize)>, // (kind 0 anim / 1 sheet, rva)
    dense: Vec<(usize, String)>,
    lines: usize,
}
static PROBE: Mutex<Probe> = Mutex::new(Probe { rvas: Vec::new(), dense: Vec::new(), lines: 0 });
/// original table -> (its ctrl when copied, the shadow table)
static SHADOWS: LazyLock<Mutex<HashMap<usize, (usize, usize)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

#[link(name = "kernel32")]
extern "system" {
    fn ReadProcessMemory(h: isize, base: *const c_void, buf: *mut c_void, size: usize, read: *mut usize) -> i32;
    fn GetCurrentProcess() -> isize;
    fn GetModuleHandleW(name: *const u16) -> usize;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
    fn VirtualAlloc(addr: *mut c_void, size: usize, kind: u32, protect: u32) -> *mut c_void;
    fn FlushInstructionCache(h: isize, base: *const c_void, size: usize) -> i32;
}

fn read(addr: usize, len: usize) -> Option<Vec<u8>> {
    let mut buf = vec![0u8; len];
    let mut got = 0usize;
    let ok = unsafe {
        ReadProcessMemory(GetCurrentProcess(), addr as *const c_void, buf.as_mut_ptr() as *mut c_void, len, &mut got)
    };
    (ok != 0 && got == len).then_some(buf)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

/// The registered hero a resource name is of: `.../league_yasuo#anim` -> league_yasuo.
pub fn hero_of_name(name: &str) -> Option<&'static Hero> {
    let last = name.rsplit('/').next()?.split('#').next()?;
    HEROES.iter().find(|h| h.id == last)
}

fn note(kind: usize, rva: usize, name: &str, got: usize) {
    let dense = hero_of_name(name).is_some();
    if !dense && !name.contains("champions") {
        return;
    }
    let Ok(mut p) = PROBE.try_lock() else { return };
    if p.lines >= MAX_LINES {
        return;
    }
    let new_rva = !p.rvas.contains(&(kind, rva));
    let new_dense = dense && !p.dense.iter().any(|d| d.0 == rva && d.1 == name);
    if new_rva {
        p.rvas.push((kind, rva));
    }
    if new_dense {
        p.dense.push((rva, name.to_string()));
    }
    if new_rva || new_dense {
        p.lines += 1;
        wlog(format!("lookup {} from rva {rva:#x}: {name} -> {got:#x}", if kind == 0 { "anim" } else { "sheet" }));
    }
}

/// The bucket (its address) whose key is `key` in the table at `t`.
unsafe fn bucket_of(t: usize, key: &[u8]) -> Option<usize> {
    let (ctrl, mask) = (q(t), q(t + 8));
    if !plausible(ctrl) || mask >= 1 << 20 || (mask + 1) & mask != 0 {
        return None;
    }
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue;
        }
        let b = ctrl - (i + 1) * BUCKET;
        let (p, n) = (q(b + 8), q(b + 16));
        if n == key.len() && plausible(p) && std::slice::from_raw_parts(p as *const u8, n) == key {
            return Some(b);
        }
    }
    None
}

/// A copy of the anim table at `t` whose `idle` holds `hd_idle`'s frames and the other way round.
unsafe fn shadow_of(t: usize) -> Option<usize> {
    let ctrl = q(t);
    if let Ok(s) = SHADOWS.lock() {
        if let Some(&(c, sh)) = s.get(&t) {
            if c == ctrl {
                return Some(sh);
            }
        }
    }
    let mask = q(t + 8);
    if !plausible(ctrl) || mask >= 1 << 20 || (mask + 1) & mask != 0 {
        return None;
    }
    let buckets = mask + 1;
    let data = ctrl - buckets * BUCKET;
    let size = buckets * BUCKET + buckets + 16;
    let idle_at = bucket_of(t, b"idle")? - data;
    let hd_at = bucket_of(t, format!("{}idle", hd::PREFIX).as_bytes())? - data;
    let mem: &'static mut [u8] = Box::leak(vec![0u8; size].into_boxed_slice());
    std::ptr::copy_nonoverlapping(data as *const u8, mem.as_mut_ptr(), size);
    let base = mem.as_mut_ptr() as usize;
    // swap the two frames Vecs {cap, ptr, len} at bucket + 0x18
    for k in 0..3 {
        let (a, b) = (base + idle_at + 0x18 + 8 * k, base + hd_at + 0x18 + 8 * k);
        let (va, vb) = (q(a), q(b));
        std::ptr::write_unaligned(a as *mut usize, vb);
        std::ptr::write_unaligned(b as *mut usize, va);
    }
    let head: &'static mut [usize; 6] = Box::leak(Box::new([0usize; 6]));
    for (k, h) in head.iter_mut().enumerate() {
        *h = q(t + 8 * k);
    }
    head[0] = base + buckets * BUCKET;
    let sh = head.as_ptr() as usize;
    if let Ok(mut s) = SHADOWS.lock() {
        s.insert(t, (ctrl, sh));
    }
    wlog(format!("shadow anim table {sh:#x} for {t:#x} ({} buckets): idle <-> hd_idle", buckets));
    Some(sh)
}

type Lookup = unsafe extern "system" fn(usize, usize, usize) -> usize;

unsafe extern "system" fn anim_detour(ctx: usize, ptr: usize, len: usize, sp: usize) -> usize {
    let f: Lookup = std::mem::transmute(ORIG_ANIM.load(Ordering::Acquire));
    let got = f(ctx, ptr, len);
    std::panic::catch_unwind(|| unsafe { after_anim(ptr, len, sp, got) }).unwrap_or(got)
}

unsafe fn after_anim(ptr: usize, len: usize, sp: usize, got: usize) -> usize {
    if len == 0 || len > 300 || !plausible(ptr) {
        return got;
    }
    let Ok(name) = std::str::from_utf8(std::slice::from_raw_parts(ptr as *const u8, len)) else { return got };
    let rva = q(sp).wrapping_sub(MODULE.load(Ordering::Relaxed));
    note(0, rva, name, got);
    if rva != ICON_RET || !plausible(got) {
        return got;
    }
    let Some(hero) = hero_of_name(name) else { return got };
    let Some(sh) = shadow_of(got) else { return got };
    let rbp = sp + 8 + ICON_RBP;
    for (off, mul) in [(ICON_FACE_X, hero.ppu), (ICON_FACE_Y, hero.ppu), (ICON_SCALE, 1.0 / hero.ppu)] {
        let at = (rbp + off) as *mut f32;
        std::ptr::write_unaligned(at, std::ptr::read_unaligned(at) * mul);
    }
    sh
}

unsafe extern "system" fn sheet_detour(ctx: usize, ptr: usize, len: usize, sp: usize) -> usize {
    let f: Lookup = std::mem::transmute(ORIG_SHEET.load(Ordering::Acquire));
    let got = f(ctx, ptr, len);
    let _ = std::panic::catch_unwind(|| unsafe {
        if len > 0 && len <= 300 && plausible(ptr) {
            if let Ok(name) = std::str::from_utf8(std::slice::from_raw_parts(ptr as *const u8, len)) {
                note(1, q(sp).wrapping_sub(MODULE.load(Ordering::Relaxed)), name, got);
            }
        }
    });
    got
}

/// At `page`: the entry stub (`mov r9, rsp; mov rax, detour; jmp rax`) and the original (12 bytes + jmp back).
fn stubs(page: usize, func: usize, detour: usize) -> (Vec<u8>, usize, usize) {
    let mut c = Vec::new();
    let entry = page;
    c.extend_from_slice(&[0x49, 0x89, 0xe1]); // mov r9, rsp
    c.extend_from_slice(&[0x48, 0xb8]);
    c.extend_from_slice(&detour.to_le_bytes());
    c.extend_from_slice(&[0xff, 0xe0]); // jmp rax
    while c.len() % 16 != 0 {
        c.push(0xcc);
    }
    let orig = page + c.len();
    c.extend_from_slice(&PROLOGUE);
    c.extend_from_slice(&[0xff, 0x25, 0, 0, 0, 0]); // jmp [rip + 0]
    c.extend_from_slice(&(func + PROLOGUE.len()).to_le_bytes());
    while c.len() % 16 != 0 {
        c.push(0xcc);
    }
    (c, entry, orig)
}

unsafe fn hook(func: usize, detour: usize, orig_slot: &AtomicUsize) -> Result<(), String> {
    if read(func, PROLOGUE.len()).as_deref() != Some(&PROLOGUE[..]) {
        return Err(format!("{func:#x}: not the game's own prologue"));
    }
    let page = VirtualAlloc(std::ptr::null_mut(), 0x1000, 0x3000, 0x40) as usize;
    if page == 0 {
        return Err("VirtualAlloc failed".into());
    }
    let (code, entry, orig) = stubs(page, func, detour);
    std::ptr::copy_nonoverlapping(code.as_ptr(), page as *mut u8, code.len());
    orig_slot.store(orig, Ordering::Release);
    let mut jump = vec![0x48, 0xb8];
    jump.extend_from_slice(&entry.to_le_bytes());
    jump.extend_from_slice(&[0xff, 0xe0]); // 12 bytes: mov rax, entry; jmp rax
    let mut old = 0u32;
    if VirtualProtect(func as *mut c_void, jump.len(), 0x40, &mut old) == 0 {
        return Err("VirtualProtect failed".into());
    }
    std::ptr::copy_nonoverlapping(jump.as_ptr(), func as *mut u8, jump.len());
    let mut tmp = 0u32;
    VirtualProtect(func as *mut c_void, jump.len(), old, &mut tmp);
    FlushInstructionCache(GetCurrentProcess(), func as *const c_void, jump.len());
    Ok(())
}

pub fn install_once() {
    HOOK.call_once(|| {
        let module = unsafe { GetModuleHandleW(std::ptr::null()) };
        MODULE.store(module, Ordering::Release);
        let a = unsafe {
            hook(module + ANIM_RVA,
                 anim_detour as unsafe extern "system" fn(usize, usize, usize, usize) -> usize as usize, &ORIG_ANIM)
        };
        let s = unsafe {
            hook(module + SHEET_RVA,
                 sheet_detour as unsafe extern "system" fn(usize, usize, usize, usize) -> usize as usize, &ORIG_SHEET)
        };
        wlog(format!("resource lookups hooked: anim {a:?}, sheet {s:?} (encyclopedia / face icons: shadow idle)"));
    });
}

#[cfg(test)]
mod tests {
    #[test]
    fn stubs_dump() {
        let (code, entry, orig) = super::stubs(0x20000, 0x140000000 + super::ANIM_RVA, 0x7ff6_0000_1234);
        assert_eq!(entry, 0x20000);
        let hex: String = code.iter().map(|b| format!("{b:02x}")).collect();
        println!("STUBS {hex} {:#x}", orig - entry);
    }

    #[test]
    fn shadow_swaps_idle_frames() {
        // a 4-bucket table with "idle" in bucket 1 and "hd_idle" in bucket 3
        let mut mem = vec![0u8; 4 * super::BUCKET + 4 + 16];
        let ctrl = 4 * super::BUCKET;
        mem[ctrl..ctrl + 4].copy_from_slice(&[0x80, 0x01, 0x80, 0x02]);
        mem[ctrl + 4..].fill(0x80);
        let base = mem.as_mut_ptr() as usize;
        let k1 = b"idle".to_vec();
        let k3 = b"hd_idle".to_vec();
        unsafe {
            let put = |b: usize, key: &Vec<u8>, frames: usize| {
                let w = |o: usize, v: usize| std::ptr::write_unaligned((b + o) as *mut usize, v);
                w(0, key.len());
                w(8, key.as_ptr() as usize);
                w(16, key.len());
                w(24, 7);
                w(32, frames);
                w(40, 7);
            };
            put(base + ctrl - 2 * super::BUCKET, &k1, 0x1111_0000);
            put(base + ctrl - 4 * super::BUCKET, &k3, 0x3333_0000);
            let head = [base + ctrl, 3usize, 0, 2, 0, 0];
            let t = head.as_ptr() as usize;
            let sh = super::shadow_of(t).expect("shadow");
            let b1 = super::bucket_of(sh, b"idle").unwrap();
            let b3 = super::bucket_of(sh, b"hd_idle").unwrap();
            assert_eq!(super::q(b1 + 32), 0x3333_0000);
            assert_eq!(super::q(b3 + 32), 0x1111_0000);
            // the original is untouched
            assert_eq!(super::q(super::bucket_of(t, b"idle").unwrap() + 32), 0x1111_0000);
        }
    }
}
