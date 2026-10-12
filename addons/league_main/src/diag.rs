//! 只读诊断（游戏 0.6.3）：卡牌钩子装上了，可卡牌没变（「没变」，日志里一次都没调用）——那张卡不是 0x22edc70 画的。
//! 这里在两个按名字取资源的函数入口挂钩：0x20fc10（取 `<路径>#anim` 动画表）和 0x16d040（取 `<路径>#sheet` 贴图），
//! 什么都不改，只把（调用处 rva，资源名）记进日志（去重，只记含 `champions` 或 `league_` 的名字，最多 MAX_LINES 行），
//! 好知道卡牌、图鉴、头像各是哪段代码画的。
//!
//! 入口那 12 个字节（push rbp … push rbx）换成 `mov rax, 跳板; jmp rax`；跳板先把返回地址放进 r9（第 4 个参数），再
//! 跳到本包的函数；原函数照常执行：原来的 12 个字节 + 跳回入口 + 12。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Mutex, Once};

use super::wlog;

const PROLOGUE: [u8; 12] = [0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53];
const ANIM_RVA: usize = 0x20fc10;
const SHEET_RVA: usize = 0x16d040;
const MAX_LINES: usize = 300;

static MODULE: AtomicUsize = AtomicUsize::new(0);
static ORIG_ANIM: AtomicUsize = AtomicUsize::new(0);
static ORIG_SHEET: AtomicUsize = AtomicUsize::new(0);
static SEEN: Mutex<(Vec<(usize, String)>, usize)> = Mutex::new((Vec::new(), 0));
static HOOK: Once = Once::new();

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

type Lookup = unsafe extern "system" fn(usize, usize, usize) -> usize;

fn note(kind: &str, ret: usize, ptr: usize, len: usize, got: usize) {
    if len == 0 || len > 300 || !(0x10000..0x7fff_ffff_ffff).contains(&ptr) {
        return;
    }
    let name = unsafe { std::slice::from_raw_parts(ptr as *const u8, len) };
    let Ok(name) = std::str::from_utf8(name) else { return };
    if !name.contains("champions") && !name.contains("league_") {
        return;
    }
    let module = MODULE.load(Ordering::Relaxed);
    let rva = ret.wrapping_sub(module);
    let Ok(mut s) = SEEN.try_lock() else { return };
    if s.1 >= MAX_LINES || s.0.iter().any(|e| e.0 == rva && e.1 == name) {
        return;
    }
    s.0.push((rva, name.to_string()));
    s.1 += 1;
    wlog(format!("lookup {kind} from rva {rva:#x}: {name} -> {got:#x}"));
}

unsafe extern "system" fn anim_detour(ctx: usize, ptr: usize, len: usize, ret: usize) -> usize {
    let f: Lookup = std::mem::transmute(ORIG_ANIM.load(Ordering::Acquire));
    let got = f(ctx, ptr, len);
    let _ = std::panic::catch_unwind(|| note("anim", ret, ptr, len, got));
    got
}

unsafe extern "system" fn sheet_detour(ctx: usize, ptr: usize, len: usize, ret: usize) -> usize {
    let f: Lookup = std::mem::transmute(ORIG_SHEET.load(Ordering::Acquire));
    let got = f(ctx, ptr, len);
    let _ = std::panic::catch_unwind(|| note("sheet", ret, ptr, len, got));
    got
}

/// At `page`: the entry stub (`mov r9, [rsp]; mov rax, detour; jmp rax`) and the original (12 bytes + jmp back).
fn stubs(page: usize, func: usize, detour: usize) -> (Vec<u8>, usize, usize) {
    let mut c = Vec::new();
    let entry = page;
    c.extend_from_slice(&[0x4c, 0x8b, 0x0c, 0x24]); // mov r9, [rsp]
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
        wlog(format!("lookup probe: anim {:?}, sheet {:?}", a, s));
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
}
