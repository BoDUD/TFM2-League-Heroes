//! 按名字取资源的两个函数上的钩子（游戏 0.6.3）：0x20fc10 取 `<路径>#anim` 动画表，0x16d040 取 `<路径>#sheet` 贴图。
//! 入口那 12 个字节（push rbp … push rbx）换成 `mov rax, 跳板; jmp rax`；跳板把栈顶的地址（返回地址在那里）放进 r9
//! 交给本包的函数，原函数照常执行（原来的 12 个字节 + 跳回入口 + 12）。
//!
//! 用户：「选完英雄的一瞬间 脸部还是会回到之前那样」「还有头像也没变」「被宝石打中后模型突然变小」——卡牌、图鉴、头像、
//! 选人槽位、战场上眩晕时的画法各走各的代码，逐处改名字、改缩放改不完。所以在这两处一次做完（0.4.0 起）：
//!
//! - 取登记英雄的动画表：**就地**把表里每个动作（`idle`、`run` … 和 `hd_*`）的帧换成它的 `hd_` 帧，帧矩形 x、y、
//!   宽、高全部除以 PPU（新帧在游戏同一个堆上分配，跟表一起由游戏释放；一张表只改一次）。0.4.0 交出去的是一张影子
//!   表和贴图条目的副本：亚索整个不见了（「亚索消失」）——有人绕过这两次查找、拿着原表或原条目，1 倍尺寸配 ÷ PPU 的
//!   矩形，UV 落到空白处。现在两边都就地改，谁读到的都是同一套；
//! - 取它的图（`#sheet`）：贴图条目就地换虚表——虚表抄一份，取宽（+0x28）、取高（+0x30）两项换成「原值 ÷ PPU」，
//!   别的（析构在内）照旧。
//!
//! UV = 矩形 ÷ 贴图大小，正好落在高清那一块上；画出来的大小 = 矩形宽高 × 各自的缩放，和 1 倍的一样。所以任何按名字
//! 取帧、按帧大小画的地方都画高清帧，大小、锚点不变，不用再改动作名、写 +0x1b4、改卡牌的指令。绘制命令按名字引用
//! 贴图（0x22edc70 把「…#sheet」交给 0x1c7880），执行时再取一次——同一个条目，宽高一致。
//!
//! 另记诊断：每个调用处第一次取英雄图记一行，登记英雄的每个（调用处，名字）也记一行。

use std::collections::HashMap;
use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex, Once};

use super::hd::{self, Hero};
use super::wlog;

const PROLOGUE: [u8; 12] = [0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53];
const ANIM_RVA: usize = 0x20fc10;
/// The anim tables' hash (&hasher, key ptr, len -> u64), for the self-test.
const HASH_RVA: usize = 0x58170;
const SHEET_RVA: usize = 0x16d040;
/// The anim table (hashbrown): ctrl, bucket mask, growth left, items, hasher (0x30 bytes); 0x30-byte buckets below
/// ctrl: key String {cap, ptr, len}, frames Vec {cap, ptr, len}.
const BUCKET: usize = 0x30;
const MAX_LINES: usize = 400;
/// A frame: x, y, w, h, duration (f32).
const FRAME: usize = 20;
/// vtable entries copied for a texture proxy (drop, size, align and the methods).
const VTABLE: usize = 48;

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
/// texture entry -> (its data, its own vtable, our vtable); texture data -> (width fn, height fn, PPU)
static PROXIES: LazyLock<Mutex<HashMap<usize, (usize, usize, usize)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static SIZES: LazyLock<Mutex<HashMap<usize, (usize, usize, f32)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// anim tables already changed: (table, ctrl)
static DONE: Mutex<Vec<(usize, usize)>> = Mutex::new(Vec::new());
/// (caller rva, 0 width / 1 height) already logged
static CALLERS: Mutex<Vec<(usize, usize)>> = Mutex::new(Vec::new());
static STUBS: Mutex<Option<(usize, usize)>> = Mutex::new(None);

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

/// The game's hash of a key for the anim table at `t` (0x58170: &hasher, ptr, len -> u64), and its probe of the table
/// (hashbrown, 16-byte groups) - the self-test that the game itself finds `key` there.
type Hash = unsafe extern "system" fn(usize, usize, usize) -> u64;

unsafe fn game_find(t: usize, key: &[u8]) -> Option<usize> {
    if MODULE.load(Ordering::Relaxed) == 0 {
        return bucket_of(t, key); // not in the game (tests)
    }
    let hash: Hash = std::mem::transmute(MODULE.load(Ordering::Relaxed) + HASH_RVA);
    let h = hash(t + 0x20, key.as_ptr() as usize, key.len());
    let (ctrl, mask) = (q(t), q(t + 8));
    let h2 = (h >> 57) as u8;
    let mut pos = (h as usize) & mask;
    let mut stride = 0;
    loop {
        let mut empty = false;
        for k in 0..16 {
            let c = *(ctrl as *const u8).add(pos + k);
            if c == h2 {
                let i = (pos + k) & mask;
                let b = ctrl - (i + 1) * BUCKET;
                let (p, n) = (q(b + 8), q(b + 16));
                if n == key.len() && plausible(p) && std::slice::from_raw_parts(p as *const u8, n) == key {
                    return Some(b);
                }
            }
            empty |= c == 0xff;
        }
        if empty {
            return None;
        }
        stride += 16;
        pos = (pos + stride) & mask;
        if stride > mask + 16 {
            return None;
        }
    }
}

unsafe fn rect_of(b: usize) -> String {
    let fp = q(b + 0x20);
    if !plausible(fp) || q(b + 0x28) == 0 {
        return "no frames".into();
    }
    let f: Vec<f32> = (0..5).map(|k| std::ptr::read_unaligned((fp + 4 * k) as *const f32)).collect();
    format!("{} frames, first {:?}", q(b + 0x28), f)
}

/// The anim table at `t` (of `hero`) changed in place, once: every tag's frames Vec becomes a new one holding its
/// `hd_` frames with x, y, w, h divided by PPU (allocated on the process heap like the game's own, so the game frees
/// it with the table; the old buffers are left alone). Everyone who reads the table - through this lookup or a pointer
/// kept from before - sees the same frames as the texture's divided size (0.4.0's copy: 「亚索消失」).
unsafe fn densify_table(t: usize, hero: &Hero) -> bool {
    let ctrl = q(t);
    if let Ok(s) = DONE.lock() {
        if s.contains(&(t, ctrl)) {
            return true;
        }
    }
    let mask = q(t + 8);
    if !plausible(ctrl) || mask >= 1 << 20 || (mask + 1) & mask != 0 {
        return false;
    }
    // first everything new, read from the untouched table; then all written at once
    let mut plan: Vec<(usize, usize, usize)> = Vec::new(); // (bucket, new ptr, len)
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue;
        }
        let b = ctrl - (i + 1) * BUCKET;
        let (p, n) = (q(b + 8), q(b + 16));
        if !plausible(p) || n > 64 {
            return false;
        }
        let Ok(key) = std::str::from_utf8(std::slice::from_raw_parts(p as *const u8, n)) else { return false };
        let dense = if key.starts_with(hd::PREFIX) { key.to_string() } else { format!("{}{key}", hd::PREFIX) };
        let Some(src) = bucket_of(t, dense.as_bytes()) else {
            wlog(format!("{}: tag {key} has no {dense}: left at 1x - the whole table left alone", hero.id));
            return false;
        };
        let (fp, fl) = (q(src + 0x20), q(src + 0x28));
        if !plausible(fp) || fl == 0 || fl > 4096 {
            return false;
        }
        let mut frames = vec![0u8; fl * FRAME].into_boxed_slice();
        std::ptr::copy_nonoverlapping(fp as *const u8, frames.as_mut_ptr(), fl * FRAME);
        for f in 0..fl {
            for k in 0..4 {
                let at = frames.as_mut_ptr().add(f * FRAME + 4 * k) as *mut f32;
                std::ptr::write_unaligned(at, std::ptr::read_unaligned(at) / hero.ppu);
            }
        }
        plan.push((b, Box::into_raw(frames) as *mut u8 as usize, fl));
    }
    for &(b, p, n) in &plan {
        std::ptr::write_unaligned((b + 0x18) as *mut usize, n);
        std::ptr::write_unaligned((b + 0x20) as *mut usize, p);
        std::ptr::write_unaligned((b + 0x28) as *mut usize, n);
    }
    if let Ok(mut s) = DONE.lock() {
        s.push((t, ctrl));
    }
    let check = match game_find(t, b"idle") {
        Some(b) => format!("the game finds idle: {}", rect_of(b)),
        None => "the game does NOT find idle".into(),
    };
    wlog(format!("{}: anim table {t:#x}: {} tags on their dense frames, rects / {}; {check}", hero.id, plan.len(),
        hero.ppu));
    true
}

/// The texture entry at `got` ({data, vtable, ...}) made to report its size divided by PPU, in place: its vtable
/// pointer moved to a copy of the vtable whose width (+0x28) and height (+0x30) entries are [`tex_width`] /
/// [`tex_height`]. (0.4.0 handed out a copy of the entry instead: the encyclopedia then drew nothing - 「亚索消失」 -
/// the renderer needs the game's own entry.) Every other entry, drop included, is the original's.
unsafe fn proxy_of(got: usize, hero: &Hero) -> Option<usize> {
    let (data, vt) = (q(got), q(got + 8));
    if !plausible(data) || !plausible(vt) {
        return None;
    }
    if let Ok(p) = PROXIES.lock() {
        if p.values().any(|&(d, _, fake)| d == data && fake == vt) {
            return Some(got);
        }
    }
    let table: &'static mut [usize; VTABLE] = Box::leak(Box::new([0usize; VTABLE]));
    for (k, e) in table.iter_mut().enumerate() {
        *e = read(vt + 8 * k, 8).map(|b| usize::from_le_bytes(b.try_into().unwrap())).unwrap_or(0);
    }
    if let Ok(mut s) = SIZES.lock() {
        s.insert(data, (table[5], table[6], hero.ppu));
    }
    let (sw, sh) = size_stubs()?;
    table[5] = sw;
    table[6] = sh;
    let fake = table.as_ptr() as usize;
    if let Ok(mut p) = PROXIES.lock() {
        p.insert(got, (data, vt, fake));
    }
    std::ptr::write_volatile((got + 8) as *mut usize, fake);
    wlog(format!("{}: texture {got:#x} reports its size / {} (vtable {vt:#x} -> {fake:#x})", hero.id, hero.ppu));
    Some(got)
}

type Size = unsafe extern "system" fn(usize) -> f32;

unsafe fn size_of(data: usize, ret: usize, which: usize) -> f32 {
    let e = SIZES.lock().ok().and_then(|s| s.get(&data).copied());
    let (f, ppu) = match e {
        Some((w, h, ppu)) => (if which == 0 { w } else { h }, ppu),
        None => (0, 1.0),
    };
    let real = if f != 0 { std::mem::transmute::<usize, Size>(f)(data) } else { f32::NAN };
    let out = if f != 0 { real / ppu } else { 1.0 };
    let rva = ret.wrapping_sub(MODULE.load(Ordering::Relaxed));
    if let Ok(mut c) = CALLERS.try_lock() {
        if c.len() < 64 && !c.contains(&(rva, which)) {
            c.push((rva, which));
            wlog(format!("texture {} asked from rva {rva:#x}: {real} -> {out}", if which == 0 { "width" } else { "height" }));
        }
    }
    out
}

unsafe extern "system" fn tex_width(data: usize, ret: usize) -> f32 {
    std::panic::catch_unwind(|| unsafe { size_of(data, ret, 0) }).unwrap_or(1.0)
}

unsafe extern "system" fn tex_height(data: usize, ret: usize) -> f32 {
    std::panic::catch_unwind(|| unsafe { size_of(data, ret, 1) }).unwrap_or(1.0)
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
    note(0, q(sp).wrapping_sub(MODULE.load(Ordering::Relaxed)), name, got);
    if !name.ends_with("#anim") || !plausible(got) {
        return got;
    }
    if let Some(hero) = hero_of_name(name) {
        densify_table(got, hero);
    }
    got
}

unsafe extern "system" fn sheet_detour(ctx: usize, ptr: usize, len: usize, sp: usize) -> usize {
    let f: Lookup = std::mem::transmute(ORIG_SHEET.load(Ordering::Acquire));
    let got = f(ctx, ptr, len);
    std::panic::catch_unwind(|| unsafe {
        if len == 0 || len > 300 || !plausible(ptr) {
            return got;
        }
        let Ok(name) = std::str::from_utf8(std::slice::from_raw_parts(ptr as *const u8, len)) else { return got };
        note(1, q(sp).wrapping_sub(MODULE.load(Ordering::Relaxed)), name, got);
        if !name.ends_with("#sheet") || !plausible(got) {
            return got;
        }
        match hero_of_name(name) {
            Some(hero) => proxy_of(got, hero).unwrap_or(got),
            None => got,
        }
    })
    .unwrap_or(got)
}

/// The width / height entries of our vtable: `mov rdx, [rsp]; mov rax, tex_*; jmp rax` (the caller's address as the
/// second argument).
unsafe fn size_stubs() -> Option<(usize, usize)> {
    if let Ok(s) = STUBS.lock() {
        if let Some(p) = *s {
            return Some(p);
        }
    }
    let page = VirtualAlloc(std::ptr::null_mut(), 0x1000, 0x3000, 0x40) as usize;
    if page == 0 {
        return None;
    }
    let mut c = Vec::new();
    for f in [tex_width as unsafe extern "system" fn(usize, usize) -> f32 as usize,
              tex_height as unsafe extern "system" fn(usize, usize) -> f32 as usize] {
        c.extend_from_slice(&[0x48, 0x8b, 0x14, 0x24]); // mov rdx, [rsp]
        c.extend_from_slice(&[0x48, 0xb8]);
        c.extend_from_slice(&f.to_le_bytes());
        c.extend_from_slice(&[0xff, 0xe0]); // jmp rax
        while c.len() % 16 != 0 {
            c.push(0xcc);
        }
    }
    std::ptr::copy_nonoverlapping(c.as_ptr(), page as *mut u8, c.len());
    let p = (page, page + 16);
    if let Ok(mut s) = STUBS.lock() {
        *s = Some(p);
    }
    Some(p)
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
        let list: Vec<String> = HEROES.iter().map(|h| format!("{} x{}", h.id, h.ppu)).collect();
        wlog(format!("resource lookups hooked: anim {a:?}, sheet {s:?}: dense frames everywhere for {}", list.join(", ")));
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

    fn frames(v: &[[f32; 5]]) -> Vec<u8> {
        v.iter().flat_map(|f| f.iter().flat_map(|x| x.to_le_bytes())).collect()
    }

    #[test]
    fn every_tag_holds_its_dense_frames_at_1x_size() {
        // a 4-bucket table with "idle" in bucket 1 and "hd_idle" in bucket 3
        let mut mem = vec![0u8; 4 * super::BUCKET + 4 + 16];
        let ctrl = 4 * super::BUCKET;
        mem[ctrl..ctrl + 4].copy_from_slice(&[0x80, 0x01, 0x80, 0x02]);
        mem[ctrl + 4..].fill(0x80);
        let base = mem.as_mut_ptr() as usize;
        let k1 = b"idle".to_vec();
        let k3 = b"hd_idle".to_vec();
        let f1 = frames(&[[0.0, 0.0, 10.0, 20.0, 0.1]]);
        let f3 = frames(&[[30.0, 60.0, 30.0, 60.0, 0.1]]);
        let hero = super::Hero { id: "league_test", ppu: 3.0, tags: vec!["idle".into()] };
        unsafe {
            let put = |b: usize, key: &Vec<u8>, fr: &Vec<u8>| {
                let w = |o: usize, v: usize| std::ptr::write_unaligned((b + o) as *mut usize, v);
                w(0, key.len());
                w(8, key.as_ptr() as usize);
                w(16, key.len());
                w(24, 1);
                w(32, fr.as_ptr() as usize);
                w(40, 1);
            };
            put(base + ctrl - 2 * super::BUCKET, &k1, &f1);
            put(base + ctrl - 4 * super::BUCKET, &k3, &f3);
            let head = [base + ctrl, 3usize, 0, 2, 0, 0];
            let t = head.as_ptr() as usize;
            assert!(super::densify_table(t, &hero));
            for key in [&b"idle"[..], b"hd_idle"] {
                let b = super::bucket_of(t, key).unwrap();
                let fp = super::q(b + 32);
                let got: Vec<f32> = (0..5).map(|k| std::ptr::read_unaligned((fp + 4 * k) as *const f32)).collect();
                assert_eq!(got, vec![10.0, 20.0, 10.0, 20.0, 0.1]);
            }
            // once only: a second lookup divides nothing again
            assert!(super::densify_table(t, &hero));
            let b = super::bucket_of(t, b"idle").unwrap();
            assert_eq!(std::ptr::read_unaligned(super::q(b + 32) as *const f32), 10.0);
        }
    }
}
