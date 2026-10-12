//! 卡牌上的高清帧（游戏 0.6.3，Windows）：用户 2026-10-12「待机图没更新啊」，选了「B：卡牌、图鉴、头像也加钩子」。
//!
//! 卡牌、图鉴里会动的英雄精灵由 rva 0x22edc70 画（一个 UI 精灵控件，第一个参数是它的对象：开头是资源路径 String，
//! +0x20 偏移，+0x28 是否裁到格子里）。它先调用 0x23305e0（唯一的调用点 0x22ede3e）按控件状态生成动作名（`idle`、
//! `dead` 或控件自己的名字）写进栈上 [rbp+0x288] 的 String，再按「路径#anim」取动画表、按名字取帧、按时间挑一帧，
//! 绘制大小 = 帧的宽高 × 2.2（0x22ee187：movaps xmm0, [2.2, 2.2, 0, 0]），位置 = 格子底边中点 + (偏移 − (宽/2, 高)) × 2.2。
//! 工坊 Rin 的 tfm2_ppu_core 改的是它前面 0x22ee171..0x22ee187 那一段；本包只改下面两处，和它不重叠：
//!
//! 1. 0x22ede3e 的 `call 0x23305e0` 改成调用本包的 [`card_anim`]（经 EXE 附近的一小段跳板，顺带把控件对象 rbx 传进来）：
//!    先调用原函数，控件路径是登记的高清英雄、名字是它有高清份的动作，就把名字换成 `hd_<动作>`（新字符串用游戏同一个堆）；
//! 2. 0x22ee187 那条 7 字节的 movaps 改成 `call` 跳板 + 2 个 nop：跳板保存易失寄存器，调用 [`card_scale`] 取得这一次
//!    的缩放（动作名是 `hd_` 开头的：2.2 ÷ PPU，否则原来的 2.2），放进 xmm0 的低两格。
//!
//! 两处都先核对原指令的字节，不对（别的版本、别的 mod 改过）就什么都不改，卡牌照旧画 1 倍的 idle。头像（0x24b44b0 按
//! `idle` 第一帧裁脸）还没有接：那里的名字是内联比较的。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex, Once};

use super::hd::{self, Hero};
use super::wlog;

const CALL_RVA: usize = 0x22ede3e; // call 0x23305e0
const ANIM_FN_RVA: usize = 0x23305e0;
const SCALE_RVA: usize = 0x22ee187; // movaps xmm0, [rip + 0x197f1d2]
const SCALE_BYTES: [u8; 7] = [0x0f, 0x28, 0x05, 0xd2, 0xf1, 0x97, 0x01];
const SCALE_CONST_RVA: usize = 0x3c6d360; // (2.2, 2.2, 0, 0)
/// The anim-name String on 0x22edc70's frame: [rbp + 0x288] cap, + 0x290 ptr, + 0x298 len.
const ANIM_PTR: usize = 0x290;
const ANIM_LEN: usize = 0x298;
const MAX_LINES: usize = 80;

static HEROES: LazyLock<Vec<Hero>> = LazyLock::new(hd::heroes);
static MODULE: AtomicUsize = AtomicUsize::new(0);
static HOOK: Once = Once::new();
static SEEN: Mutex<(Vec<String>, usize)> = Mutex::new((Vec::new(), 0));

#[link(name = "kernel32")]
extern "system" {
    fn ReadProcessMemory(h: isize, base: *const c_void, buf: *mut c_void, size: usize, read: *mut usize) -> i32;
    fn GetCurrentProcess() -> isize;
    fn GetModuleHandleW(name: *const u16) -> usize;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
    fn VirtualAlloc(addr: *mut c_void, size: usize, kind: u32, protect: u32) -> *mut c_void;
    fn FlushInstructionCache(h: isize, base: *const c_void, size: usize) -> i32;
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

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

/// A String {cap, ptr, len} at `at` as text.
unsafe fn string_at<'a>(at: usize) -> Option<&'a str> {
    let (cap, ptr, len) = (q(at), q(at + 8), q(at + 16));
    if len == 0 || len > 512 || cap < len || !plausible(ptr) {
        return None;
    }
    std::str::from_utf8(std::slice::from_raw_parts(ptr as *const u8, len)).ok()
}

/// The registered hero a sprite path belongs to (its last path part is the champion id).
fn hero_of(path: &str) -> Option<&'static Hero> {
    let last = path.rsplit('/').next()?;
    let last = last.split('#').next()?;
    HEROES.iter().find(|h| h.id == last)
}

fn note(line: String) {
    if let Ok(mut s) = SEEN.lock() {
        if s.1 < MAX_LINES && !s.0.contains(&line) {
            s.0.push(line.clone());
            s.1 += 1;
            wlog(line);
        }
    }
}

type AnimFn = unsafe extern "system" fn(usize, usize) -> usize;

/// 0x23305e0's place at 0x22ede3e: the original, then `<tag>` -> `hd_<tag>` on a registered hero's card.
unsafe extern "system" fn card_anim(out: usize, state: usize, card: usize) -> usize {
    let f: AnimFn = std::mem::transmute(MODULE.load(Ordering::Acquire) + ANIM_FN_RVA);
    let r = f(out, state);
    let _ = std::panic::catch_unwind(|| unsafe {
        let path = if plausible(card) { string_at(card) } else { None };
        let Some(path) = path else { return };
        let Some(name) = string_at(out) else { return };
        let Some(hero) = hero_of(path) else {
            note(format!("card: {path} plays {name}"));
            return;
        };
        let Some(want) = hd::anim_for(name, &hero.tags) else { return };
        if !want.starts_with(hd::PREFIX) {
            return;
        }
        let heap = GetProcessHeap();
        let fresh = HeapAlloc(heap, 0, want.len());
        if fresh.is_null() {
            return;
        }
        std::ptr::copy_nonoverlapping(want.as_ptr(), fresh, want.len());
        let (cap, ptr) = (q(out), q(out + 8));
        std::ptr::write_unaligned(out as *mut usize, want.len());
        std::ptr::write_unaligned((out + 8) as *mut usize, fresh as usize);
        std::ptr::write_unaligned((out + 16) as *mut usize, want.len());
        if cap > 0 && plausible(ptr) {
            HeapFree(heap, 0, ptr as *mut u8);
        }
        note(format!("card: {path} plays {want} (offset {:?})",
            (std::ptr::read_unaligned((card + 0x20) as *const f32), std::ptr::read_unaligned((card + 0x24) as *const f32))));
    });
    r
}

/// The card's sprite scale this time (0x22ee187): 2.2 / PPU for an `hd_` animation of a registered hero, else 2.2.
unsafe extern "system" fn card_scale(card: usize, rbp: usize) -> f32 {
    let base = std::ptr::read_unaligned((MODULE.load(Ordering::Acquire) + SCALE_CONST_RVA) as *const f32);
    std::panic::catch_unwind(|| unsafe {
        let (p, n) = (q(rbp + ANIM_PTR), q(rbp + ANIM_LEN));
        if !(1..=64).contains(&n) || !plausible(p) {
            return base;
        }
        let name = std::slice::from_raw_parts(p as *const u8, n);
        if !name.starts_with(hd::PREFIX.as_bytes()) || !plausible(card) {
            return base;
        }
        match string_at(card).and_then(hero_of) {
            Some(h) => base / h.ppu,
            None => base,
        }
    })
    .unwrap_or(base)
}

/// A page within ±2 GB of the EXE for the two trampolines.
unsafe fn near_page(module: usize) -> Option<usize> {
    const MEM_COMMIT_RESERVE: u32 = 0x3000;
    const PAGE_EXECUTE_READWRITE: u32 = 0x40;
    for k in 1..4096usize {
        let at = module.checked_sub(k * 0x10000)?;
        let p = VirtualAlloc(at as *mut c_void, 0x1000, MEM_COMMIT_RESERVE, PAGE_EXECUTE_READWRITE);
        if !p.is_null() {
            return Some(p as usize);
        }
    }
    None
}

unsafe fn patch(at: usize, bytes: &[u8]) -> bool {
    let mut old = 0u32;
    if VirtualProtect(at as *mut c_void, bytes.len(), 0x40, &mut old) == 0 {
        return false;
    }
    std::ptr::copy_nonoverlapping(bytes.as_ptr(), at as *mut u8, bytes.len());
    let mut tmp = 0u32;
    VirtualProtect(at as *mut c_void, bytes.len(), old, &mut tmp);
    FlushInstructionCache(GetCurrentProcess(), at as *const c_void, bytes.len());
    true
}

fn rel32(from_next: usize, to: usize) -> Option<[u8; 4]> {
    let d = to as i64 - from_next as i64;
    i32::try_from(d).ok().map(|v| v.to_le_bytes())
}

/// The two trampolines: (1) `mov r8, rbx; mov rax, card_anim; jmp rax`; (2) save the volatile registers, call
/// card_scale(rbx, rbp), put the result in xmm0's two low lanes, restore, ret.
fn trampolines(page: usize) -> (Vec<u8>, usize, usize) {
    let mut c = Vec::new();
    let t1 = page;
    c.extend_from_slice(&[0x49, 0x89, 0xd8]); // mov r8, rbx
    c.extend_from_slice(&[0x48, 0xb8]); // mov rax, imm64
    c.extend_from_slice(&(card_anim as unsafe extern "system" fn(usize, usize, usize) -> usize as usize).to_le_bytes());
    c.extend_from_slice(&[0xff, 0xe0]); // jmp rax
    while c.len() % 16 != 0 {
        c.push(0xcc);
    }
    let t2 = page + c.len();
    // push rax, rcx, rdx, r8, r9, r10, r11  (7 pushes after the call's return address: rsp is 16-aligned)
    c.extend_from_slice(&[0x50, 0x51, 0x52, 0x41, 0x50, 0x41, 0x51, 0x41, 0x52, 0x41, 0x53]);
    c.extend_from_slice(&[0x48, 0x83, 0xec, 0x70]); // sub rsp, 0x70
    for (i, off) in [(1u8, 0x20u8), (2, 0x30), (3, 0x40), (4, 0x50), (5, 0x60)] {
        // movdqu [rsp + off], xmm_i  = f3 0f 7f /r with modrm 01 iii 100, sib 0x24, disp8
        c.extend_from_slice(&[0xf3, 0x0f, 0x7f, 0x44 | (i << 3), 0x24, off]);
    }
    c.extend_from_slice(&[0x48, 0x89, 0xd9]); // mov rcx, rbx
    c.extend_from_slice(&[0x48, 0x89, 0xea]); // mov rdx, rbp
    c.extend_from_slice(&[0x48, 0xb8]); // mov rax, imm64
    c.extend_from_slice(&(card_scale as unsafe extern "system" fn(usize, usize) -> f32 as usize).to_le_bytes());
    c.extend_from_slice(&[0xff, 0xd0]); // call rax
    c.extend_from_slice(&[0x0f, 0xc6, 0xc0, 0x00]); // shufps xmm0, xmm0, 0
    c.extend_from_slice(&[0xf3, 0x0f, 0x7e, 0xc0]); // movq xmm0, xmm0 (upper lanes zero)
    for (i, off) in [(1u8, 0x20u8), (2, 0x30), (3, 0x40), (4, 0x50), (5, 0x60)] {
        c.extend_from_slice(&[0xf3, 0x0f, 0x6f, 0x44 | (i << 3), 0x24, off]); // movdqu xmm_i, [rsp + off]
    }
    c.extend_from_slice(&[0x48, 0x83, 0xc4, 0x70]); // add rsp, 0x70
    c.extend_from_slice(&[0x41, 0x5b, 0x41, 0x5a, 0x41, 0x59, 0x41, 0x58, 0x5a, 0x59, 0x58]); // pop r11..rax
    c.push(0xc3); // ret
    (c, t1, t2)
}

fn install() -> Result<String, String> {
    let module = unsafe { GetModuleHandleW(std::ptr::null()) };
    if module == 0 {
        return Err("no module handle".into());
    }
    MODULE.store(module, Ordering::Release);
    let call_at = module + CALL_RVA;
    let mut want_call = vec![0xe8];
    want_call.extend_from_slice(&rel32(call_at + 5, module + ANIM_FN_RVA).ok_or("rel32")?);
    if read(call_at, 5).as_deref() != Some(&want_call[..]) {
        return Err(format!("the card's anim-name call at rva {CALL_RVA:#x} is not the game's own"));
    }
    let scale_at = module + SCALE_RVA;
    if read(scale_at, 7).as_deref() != Some(&SCALE_BYTES[..]) {
        return Err(format!("the card's scale load at rva {SCALE_RVA:#x} is not the game's own"));
    }
    let page = unsafe { near_page(module) }.ok_or("no page near the EXE")?;
    let (code, t1, t2) = trampolines(page);
    unsafe { std::ptr::copy_nonoverlapping(code.as_ptr(), page as *mut u8, code.len()) };
    let mut call1 = vec![0xe8];
    call1.extend_from_slice(&rel32(call_at + 5, t1).ok_or("trampoline 1 out of reach")?);
    let mut call2 = vec![0xe8];
    call2.extend_from_slice(&rel32(scale_at + 5, t2).ok_or("trampoline 2 out of reach")?);
    call2.extend_from_slice(&[0x66, 0x90]); // 2-byte nop
    unsafe {
        if !patch(call_at, &call1) {
            return Err("VirtualProtect failed (anim call)".into());
        }
        if !patch(scale_at, &call2) {
            patch(call_at, &want_call);
            return Err("VirtualProtect failed (scale load)".into());
        }
    }
    Ok(format!("trampolines at {page:#x}"))
}

/// 加载时改两处（一个进程只改一次）。
pub fn install_once() {
    HOOK.call_once(|| match install() {
        Ok(at) => wlog(format!("dense card frames on: rva {CALL_RVA:#x} (anim name) and {SCALE_RVA:#x} (scale), {at}")),
        Err(e) => wlog(format!("dense card frames off ({e}): the cards draw the 1x idle")),
    });
}

#[cfg(test)]
mod tests {
    #[test]
    fn trampolines_dump() {
        let (code, t1, t2) = super::trampolines(0x10000);
        assert_eq!(t1, 0x10000);
        assert!(t2 > t1 && code.len() < 0x1000);
        let hex: String = code.iter().map(|b| format!("{b:02x}")).collect();
        println!("TRAMP {hex} {:#x}", t2 - t1);
    }
}
