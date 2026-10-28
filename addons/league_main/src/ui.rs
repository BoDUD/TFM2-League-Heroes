//! 界面画英雄改用小图集（2026-10-24，用户：「PPU导致页面卡 特别是英雄界面 还有BP界面非常的卡」「BP卡 但是局内不卡」）。
//!
//! BP 格子、图鉴 / 头像、选人位、选中特写、记分板头像这五处画英雄，都按名字取英雄整张的战斗图集
//! （`asset/base/aseprite_resources/champions/<id>#sheet`）：自己先取一次算 UV，再把名字交给绘制命令 / 图片节点，真正画的
//! 时候游戏按这个名字再取一次。BP 和英雄界面一屏画出全部英雄：167 张图集解码后 589 MiB（PPU 英雄 493），游戏的图片缓存
//! 只有 256 MiB（Rin 的 PPU Core 0.2.16 / 0.2.18 查到的也是它），于是每一帧都在重新解码；局内只有十个英雄，装得下。
//!
//! 这里让这五处改画小图集。tools/package_mod.py 给每个英雄打出两张，只有界面要画的帧、像素原样：
//! `asset/<包>/ui_sheets/idle/<id>`（图鉴、头像、选人位、选中特写、记分板画的 idle：PPU 英雄是 lo_idle）和
//! `.../ui_sheets/bp/<id>`（BP 格子的 reel 和被禁时的 dead：PPU 英雄是 hd_bp / hd_dead）。全部英雄合起来解码后 idle
//! 28 MiB、bp 137 MiB。
//!
//! - 这五处取动画表（src/lookup.rs after_anim）：给游戏那张表的一份拷贝，每个动作的帧换成小图集里的帧（BP 格子每个动作
//!   是 reel、dead 是 dead；别处每个动作是 idle），矩形除以它原来的除数——画出来的大小、锚点和以前一样；
//! - 紧接着它们自己取图（src/build.rs ui_sheet_ret）：给小图集的条目（PPU 英雄照样报 ÷ 除数的宽高），UV 落在小图集上；
//! - 它们把名字交出去的两个函数（cmd_by_name / node_image）：入口挂一段保存寄存器的跳板，名字正是刚才换过图的那个，
//!   就换成小图集的名字——画的时候游戏取到的就是小图集。别的调用原样放过。
//!
//! 战场不动（它画整张图集里的高清帧）。没有小图集的英雄（别的模组的、还没打包的）、找不到这些地址的游戏版本：照旧画整张
//! 图集。

use std::cell::RefCell;
use std::collections::HashMap;
use std::ffi::c_void;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use super::build::Build;
use super::hd::Hero;
use super::lookup::{self, bucket_of, plausible, q, BUCKET, FRAME};
use super::wlog;

/// tools/package_mod.py UI_DIR and UI_KINDS: the idle's sheet (every drawer but the BP grid) and the reel's (the BP grid).
const DIR: &str = "ui_sheets";
const KINDS: [&str; 2] = ["idle", "bp"];
const IDLE: usize = 0;
const REEL: usize = 1;

/// The length of the sinks' first whole instructions the trampoline runs before it jumps back: pushes and `sub rsp`
/// (no rip-relative operand) until the 12 bytes the jump overwrites are covered - push r64 (50..57, 41 50..57), sub
/// rsp imm8 / imm32 (48 83 ec ib / 48 81 ec id). 0.6.5's draw command: push rbp / r14 / rsi / rdi / rbx, sub rsp 0xc0
/// (13 bytes); 0.7.0's pushes r15 too, sub rsp 0xc8 (15); the image node's: push r15 / r14 / r12 / rsi / rdi / rbx,
/// sub rsp 0x28 (13) in both. A sink starting otherwise gets no hook (and the UI no UI sheets).
pub fn prologue_len(code: &[u8]) -> Option<usize> {
    let mut i = 0;
    while i < 12 {
        match code.get(i..)? {
            [0x50..=0x57, ..] => i += 1,
            [0x41, 0x50..=0x57, ..] => i += 2,
            [0x48, 0x83, 0xec, _, ..] => i += 4,
            [0x48, 0x81, 0xec, _, _, _, _, ..] => i += 7,
            _ => return None,
        }
    }
    Some(i)
}
/// which sink called [`swap`]: the draw command (name ptr in rdx, len in r8), the image node (&String in rdx)
const CMD: u32 = 0;
const NODE: u32 = 1;
const MAX_LINES: usize = 600;
/// after this many UI sheet lookups by a drawer, the log says how many of them reached a sink
const TALLY: usize = 300;

/// Both sinks hooked: the drawers draw from the UI sheets.
pub static ON: AtomicBool = AtomicBool::new(false);

#[link(name = "kernel32")]
extern "system" {
    fn GetCurrentProcess() -> isize;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
    fn VirtualAlloc(addr: *mut c_void, size: usize, kind: u32, protect: u32) -> *mut c_void;
    fn FlushInstructionCache(h: isize, base: *const c_void, size: usize) -> i32;
}

/// A hero's UI sheets' names, by kind ([`IDLE`], [`REEL`]).
struct Names {
    anim: [String; 2],
    sheet: [String; 2],
    /// each sheet name as a String {cap, ptr, len}: the image node's setter takes &String and copies it
    string: [[usize; 3]; 2],
}

static NAMES: LazyLock<Mutex<HashMap<String, &'static Names>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// The hero a drawer's resource name is of - `.../champions/<id>#anim` or `#sheet` - when it is one of this repo's packs'
/// (league_*, tft_*): only they have UI sheets.
fn hero_id(name: &str) -> Option<&str> {
    let (path, _) = name.rsplit_once('#')?;
    let id = path.rsplit('/').next()?;
    (id.starts_with("league_") || id.starts_with("tft_")).then_some(id)
}

fn names_of(id: &str) -> Option<&'static Names> {
    let mut m = NAMES.lock().ok()?;
    if let Some(n) = m.get(id) {
        return Some(n);
    }
    let pack = if id.starts_with("tft_") { "tft" } else { "league" };
    let base = |k: usize| format!("asset/{pack}/{DIR}/{}/{id}", KINDS[k]);
    let sheet = [format!("{}#sheet", base(IDLE)), format!("{}#sheet", base(REEL))];
    // the Strings' buffers stay where they are when the Names box takes them
    let string = [IDLE, REEL].map(|k| [sheet[k].len(), sheet[k].as_ptr() as usize, sheet[k].len()]);
    let anim = [format!("{}#anim", base(IDLE)), format!("{}#anim", base(REEL))];
    let n: &'static Names = Box::leak(Box::new(Names { anim, sheet, string }));
    m.insert(id.to_string(), n);
    Some(n)
}

/// Drawer `k` (its place in Build::ui_anim_ret) draws the reel (the BP grid) or the idle (the others).
fn kind(b: &Build, k: usize) -> usize {
    if b.ui_anim_ret[k] == b.bp_grid().0 { REEL } else { IDLE }
}

/// What drawer `k` divides the UI sheet's frame pixels by: what it divided the battle sheet's by (src/lookup.rs
/// ui_table, the dense table) - a 1x hero 1; a dense hero with lo_ frames the BP grid's hd divisor or the UI's; one
/// without them its shown PPU.
fn divisor(b: &Build, k: usize, hero: Option<&Hero>) -> f32 {
    match hero {
        None => 1.0,
        Some(h) if !h.lo => h.shown(),
        Some(h) if kind(b, k) == REEL => h.bp_hd(),
        Some(h) => h.ui_for(b.ui_sized_anim_ret.contains(&b.ui_anim_ret[k])),
    }
}

/// The frames of bucket `b` (x, y, w, h, duration each) with x, y, w, h divided by `div`, leaked (the copies share them).
unsafe fn frames(b: usize, div: f32) -> Option<(usize, usize)> {
    let (fp, fl) = (q(b + 0x20), q(b + 0x28));
    if !plausible(fp) || fl == 0 || fl > 4096 {
        return None;
    }
    let out: &'static mut [u8] = Box::leak(vec![0u8; fl * FRAME].into_boxed_slice());
    std::ptr::copy_nonoverlapping(fp as *const u8, out.as_mut_ptr(), fl * FRAME);
    for f in 0..fl {
        for k in 0..4 {
            let at = out.as_mut_ptr().add(f * FRAME + 4 * k) as *mut f32;
            at.write_unaligned(at.read_unaligned() / div);
        }
    }
    Some((out.as_ptr() as usize, fl))
}

/// A copy of the game's anim table `t` - every tag it has - whose frames are the UI table `ut`'s: for the BP grid
/// (`reel`) every tag's are the reel (`bp`) and `dead`'s the dead pose when `ut` has one; elsewhere every tag's are the
/// idle. x, y, w, h divided by `div`. None when `ut` lacks them or `t` does not look like a table. Kept, never freed
/// (like src/lookup.rs's copies).
unsafe fn copy_from(t: usize, ut: usize, reel: bool, div: f32) -> Option<usize> {
    let ctrl = q(t);
    let mask = q(t + 8);
    if !plausible(ctrl) || mask >= 1 << 20 || (mask + 1) & mask != 0 {
        return None;
    }
    let buckets = mask + 1;
    for i in 0..buckets {
        if *(ctrl as *const u8).add(i) & 0x80 == 0 {
            let b = ctrl - (i + 1) * BUCKET;
            if !plausible(q(b + 8)) || q(b + 16) > 64 {
                return None;
            }
        }
    }
    let main = frames(bucket_of(ut, if reel { b"bp" } else { b"idle" })?, div)?;
    let dead = match reel.then(|| bucket_of(ut, b"dead")).flatten() {
        Some(d) => Some(frames(d, div)?),
        None => None,
    };
    let data = ctrl - buckets * BUCKET;
    let size = buckets * BUCKET + buckets + 16;
    let mem: &'static mut [u8] = Box::leak(vec![0u8; size].into_boxed_slice());
    std::ptr::copy_nonoverlapping(data as *const u8, mem.as_mut_ptr(), size);
    let base = mem.as_mut_ptr() as usize;
    for i in 0..buckets {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue;
        }
        let b = ctrl - (i + 1) * BUCKET;
        let key = std::slice::from_raw_parts(q(b + 8) as *const u8, q(b + 16));
        let (fp, fl) = match dead {
            Some(d) if key == b"dead" => d,
            _ => main,
        };
        let nb = base + (b - data);
        std::ptr::write_unaligned((nb + 0x18) as *mut usize, fl);
        std::ptr::write_unaligned((nb + 0x20) as *mut usize, fp);
        std::ptr::write_unaligned((nb + 0x28) as *mut usize, fl);
    }
    let head: &'static mut [usize; 6] = Box::leak(Box::new([0usize; 6]));
    for (k, h) in head.iter_mut().enumerate() {
        *h = q(t + 8 * k);
    }
    head[0] = base + buckets * BUCKET;
    Some(head.as_ptr() as usize)
}

/// (the game's table, drawer) -> (its ctrl, the UI table, its ctrl, the copy)
static COPIES: LazyLock<Mutex<HashMap<(usize, usize), (usize, usize, usize, usize)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

unsafe fn copy_of(t: usize, ut: usize, k: usize, reel: bool, div: f32) -> Option<usize> {
    let (ctrl, uctrl) = (q(t), q(ut));
    if let Ok(c) = COPIES.lock() {
        if let Some(&(c0, u0, uc0, copy)) = c.get(&(t, k)) {
            if (c0, u0, uc0) == (ctrl, ut, uctrl) {
                return Some(copy);
            }
        }
    }
    let copy = copy_from(t, ut, reel, div)?;
    if let Ok(mut c) = COPIES.lock() {
        c.insert((t, k), (ctrl, ut, uctrl, copy));
    }
    Some(copy)
}

/// What the lookups just did on this thread: a drawer's anim lookup redirected (drawer, hero), then its sheet lookup -
/// whose name the next sink call that hands on the same name gets swapped for the UI sheet's.
#[derive(Default)]
struct State {
    anim: Option<(usize, usize)>,
    name: Vec<u8>,
    swap: Option<(&'static Names, usize, usize)>,
}

thread_local! {
    static STATE: RefCell<State> = RefCell::new(State::default());
}

fn with_state(f: impl FnOnce(&mut State)) {
    let _ = STATE.try_with(|s| {
        if let Ok(mut s) = s.try_borrow_mut() {
            f(&mut s);
        }
    });
}

/// Any anim lookup (src/lookup.rs after_anim, before it may redirect one) or any sheet lookup but a UI drawer's: a
/// drawing of something else begins - neither the next sheet lookup nor the next sink call is the redirected drawer's.
pub(crate) fn seen_lookup() {
    with_state(|s| {
        s.anim = None;
        s.swap = None;
    });
}

static LINES: AtomicUsize = AtomicUsize::new(0);
/// (hero names, drawer) logged; heroes without UI sheets logged
static SEEN: Mutex<Vec<(usize, usize)>> = Mutex::new(Vec::new());
static MISSING: Mutex<Vec<String>> = Mutex::new(Vec::new());
static SWAPS: [AtomicUsize; 2] = [AtomicUsize::new(0), AtomicUsize::new(0)];
/// per drawer: its UI sheet lookups, and the names of them handed on to a sink (fewer: the BP grid's cards scrolled out of
/// sight and the pick moment's layout passes look the sheet up and draw nothing)
static LOOKED: [AtomicUsize; 8] = [const { AtomicUsize::new(0) }; 8];
static HANDED: [AtomicUsize; 8] = [const { AtomicUsize::new(0) }; 8];

fn line(msg: impl FnOnce() -> String) {
    if LINES.fetch_add(1, Ordering::Relaxed) < MAX_LINES {
        wlog(msg());
    }
}

/// The in-game check of this module: after TALLY UI sheet lookups by drawer `k`, how many reached a sink (none would mean
/// the drawer hands its name on somewhere else and draws the battle sheet with the UI sheet's UV).
fn tally(k: usize) {
    if LOOKED.get(k).is_some_and(|c| c.fetch_add(1, Ordering::Relaxed) + 1 == TALLY) {
        line(|| format!("UI drawer {k}: {TALLY} UI sheet lookups, {} of them handed on to be drawn",
                        HANDED[k].load(Ordering::Relaxed)));
    }
}

/// The anim lookup of `name` from UI drawer `k` (src/lookup.rs after_anim) returned `got`: the copy drawing from the
/// hero's UI sheet, or None - no UI sheets for it: the drawer keeps the battle sheet's frames, as before.
pub(crate) unsafe fn anim(ctx: usize, name: &str, got: usize, k: usize, hero: Option<&Hero>) -> Option<usize> {
    let b = lookup::build();
    let id = hero_id(name)?;
    let n = names_of(id)?;
    let kd = kind(b, k);
    let (ut, ue) = (lookup::orig_anim(ctx, &n.anim[kd]), lookup::orig_sheet(ctx, &n.sheet[kd]));
    if !plausible(ut) || !plausible(ue) {
        if let Ok(mut m) = MISSING.lock() {
            if m.len() < 400 && !m.iter().any(|x| x == id) {
                m.push(id.to_string());
                line(|| format!("{id}: no UI sheets ({} {}): the UI draws its battle sheet", n.anim[kd],
                                if plausible(ut) { "found, its sheet not" } else { "not found" }));
            }
        }
        return None;
    }
    let div = divisor(b, k, hero);
    let t = copy_of(got, ut, k, kd == REEL, div)?;
    with_state(|s| s.anim = Some((k, n as *const Names as usize)));
    if let Ok(mut s) = SEEN.lock() {
        let key = (n as *const Names as usize, k);
        if s.len() < 2000 && !s.contains(&key) {
            s.push(key);
            line(|| format!("{id}: UI drawer {k} draws {} (frames / {div})", n.sheet[kd]));
        }
    }
    Some(t)
}

/// The sheet lookup of `name` from UI drawer `k` right after its redirected anim lookup: the UI sheet's entry - its
/// sizes divided as the hero's battle sheet's - and the next sink call handing on this name gets the UI sheet's name.
/// None (no redirected anim lookup before it, another hero): the battle sheet.
pub(crate) unsafe fn sheet(ctx: usize, name: &str, k: usize, hero: Option<&Hero>) -> Option<usize> {
    let mut from = None;
    with_state(|s| {
        from = s.anim.take();
        s.swap = None;
    });
    let n = names_of(hero_id(name)?)?;
    if from != Some((k, n as *const Names as usize)) {
        return None;
    }
    let kd = kind(lookup::build(), k);
    let ue = lookup::orig_sheet(ctx, &n.sheet[kd]);
    if !plausible(ue) {
        return None;
    }
    if let Some(h) = hero {
        lookup::proxy_of(ue, h);
    }
    with_state(|s| {
        s.name.clear();
        s.name.extend_from_slice(name.as_bytes());
        s.swap = Some((n, kd, k));
    });
    tally(k);
    Some(ue)
}

/// Called by the sinks' stub with the caller's registers [r9, r8, rdx, rcx, return address]: the name handed on is the
/// one the last UI sheet lookup redirected - swapped for the UI sheet's (rdx / r8 rewritten).
unsafe extern "system" fn swap(sink: u32, regs: *mut [usize; 5]) {
    let _ = std::panic::catch_unwind(|| unsafe {
        with_state(|s| {
            let Some((n, kd, k)) = s.swap else { return };
            let r = &mut *regs;
            let (ptr, len) = if sink == CMD { (r[2], r[1]) } else if plausible(r[2]) { (q(r[2] + 8), q(r[2] + 16)) } else { return };
            if len != s.name.len() || !plausible(ptr) || std::slice::from_raw_parts(ptr as *const u8, len) != s.name {
                return;
            }
            if sink == CMD {
                r[2] = n.sheet[kd].as_ptr() as usize;
                r[1] = n.sheet[kd].len();
            } else {
                r[2] = n.string[kd].as_ptr() as usize;
            }
            s.swap = None;
            if let Some(c) = HANDED.get(k) {
                c.fetch_add(1, Ordering::Relaxed);
            }
            if SWAPS[sink as usize].fetch_add(1, Ordering::Relaxed) == 0 {
                line(|| format!("UI drawer {k}: {} handed on as {} ({})", String::from_utf8_lossy(&s.name), n.sheet[kd],
                                if sink == CMD { "draw command" } else { "image node" }));
            }
        });
    });
}

/// The sinks' entry: saves the argument registers (rcx rdx r8 r9, xmm0-3), calls `detour(kind, &[r9, r8, rdx, rcx, return
/// address])` - which may rewrite rdx / r8 - and goes on into `orig` (the original's first instructions, then back) with
/// the registers as the detour left them; the stack arguments are untouched.
fn sink_stub(kind: u32, detour: usize, orig: usize) -> Vec<u8> {
    const XMM: [(u8, u8); 4] = [(0x44, 0x20), (0x4c, 0x30), (0x54, 0x40), (0x5c, 0x50)];
    let mut c = vec![0x51, 0x52, 0x41, 0x50, 0x41, 0x51]; // push rcx; push rdx; push r8; push r9
    c.extend_from_slice(&[0x48, 0x83, 0xec, 0x68]); // sub rsp, 0x68: 16-aligned at the call (8 + 0x20 + 0x68)
    for (m, d) in XMM {
        c.extend_from_slice(&[0xf3, 0x0f, 0x7f, m, 0x24, d]); // movdqu [rsp+d], xmmN
    }
    c.push(0xb9); // mov ecx, kind
    c.extend_from_slice(&kind.to_le_bytes());
    c.extend_from_slice(&[0x48, 0x8d, 0x54, 0x24, 0x68]); // lea rdx, [rsp+0x68]: the pushed registers
    c.extend_from_slice(&[0x48, 0xb8]); // mov rax, detour
    c.extend_from_slice(&detour.to_le_bytes());
    c.extend_from_slice(&[0xff, 0xd0]); // call rax
    for (m, d) in XMM {
        c.extend_from_slice(&[0xf3, 0x0f, 0x6f, m, 0x24, d]); // movdqu xmmN, [rsp+d]
    }
    c.extend_from_slice(&[0x48, 0x83, 0xc4, 0x68]); // add rsp, 0x68
    c.extend_from_slice(&[0x41, 0x59, 0x41, 0x58, 0x5a, 0x59]); // pop r9; pop r8; pop rdx; pop rcx
    c.extend_from_slice(&[0x48, 0xb8]); // mov rax, orig
    c.extend_from_slice(&orig.to_le_bytes());
    c.extend_from_slice(&[0xff, 0xe0]); // jmp rax
    c
}

/// `func`'s first instructions (`prologue`, at least 12 bytes) replaced by `mov rax, stub; jmp rax`; the stub
/// ([`sink_stub`]) calls [`swap`] and then the trampoline: the prologue and a jump back after it.
unsafe fn hook_sink(func: usize, sink: u32) -> Result<(), String> {
    let head = lookup::read(func, 24).ok_or(format!("{func:#x}: unreadable"))?;
    let Some(n) = prologue_len(&head) else {
        return Err(format!("{func:#x}: not a push / sub rsp prologue this hook can run ({:02x?})", &head[..12]));
    };
    let prologue = &head[..n];
    let page = VirtualAlloc(std::ptr::null_mut(), 0x1000, 0x3000, 0x40) as usize;
    if page == 0 {
        return Err("VirtualAlloc failed".into());
    }
    let orig = page + 0x100;
    let mut t = prologue.to_vec();
    t.extend_from_slice(&[0xff, 0x25, 0, 0, 0, 0]); // jmp [rip + 0]
    t.extend_from_slice(&(func + prologue.len()).to_le_bytes());
    std::ptr::copy_nonoverlapping(t.as_ptr(), orig as *mut u8, t.len());
    let stub = sink_stub(sink, swap as unsafe extern "system" fn(u32, *mut [usize; 5]) as usize, orig);
    std::ptr::copy_nonoverlapping(stub.as_ptr(), page as *mut u8, stub.len());
    let mut jump = vec![0x48, 0xb8];
    jump.extend_from_slice(&page.to_le_bytes());
    jump.extend_from_slice(&[0xff, 0xe0]);
    jump.resize(prologue.len(), 0xcc);
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

/// The sinks hooked (src/lookup.rs install_once, after the lookups): on when both are in and the build knows the drawers'
/// sheet lookups.
pub fn install(b: &Build, module: usize) {
    if b.ui_sheet_ret.len() != b.ui_anim_ret.len() || b.cmd_by_name == 0 || b.node_image == 0 {
        wlog("UI sheets off: this game build's UI sheet places are not known - the UI draws the battle sheets");
        return;
    }
    let (c, n) = unsafe {
        (hook_sink(module + b.cmd_by_name, CMD), hook_sink(module + b.node_image, NODE))
    };
    if c.is_ok() && n.is_ok() {
        ON.store(true, Ordering::Release);
    }
    wlog(format!("UI sheets {}: draw command {:#x} {c:?}, image node {:#x} {n:?}; the encyclopedia / faces, pick slots, pick \
                  moment and scoreboard draw {DIR}/idle, the BP grid {DIR}/bp",
                 if ON.load(Ordering::Relaxed) { "on" } else { "off" }, b.cmd_by_name, b.node_image));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_drawers_name_gives_the_hero_and_its_ui_sheets() {
        assert_eq!(hero_id("asset/base/aseprite_resources/champions/league_akshan#anim"), Some("league_akshan"));
        assert_eq!(hero_id("asset/base/aseprite_resources/champions/tft_powder#sheet"), Some("tft_powder"));
        assert_eq!(hero_id("asset/base/aseprite_resources/champions/alchemist#sheet"), None);
        assert_eq!(hero_id("asset/base/aseprite_resources/champions/league_akshan"), None);
        let n = names_of("league_akshan").unwrap();
        assert_eq!(n.anim, ["asset/league/ui_sheets/idle/league_akshan#anim", "asset/league/ui_sheets/bp/league_akshan#anim"]);
        assert_eq!(n.sheet[REEL], "asset/league/ui_sheets/bp/league_akshan#sheet");
        assert_eq!(names_of("tft_powder").unwrap().sheet[IDLE], "asset/tft/ui_sheets/idle/tft_powder#sheet");
        for k in [IDLE, REEL] {
            let [cap, ptr, len] = n.string[k];
            assert_eq!((cap, len), (n.sheet[k].len(), n.sheet[k].len()));
            assert_eq!(unsafe { std::slice::from_raw_parts(ptr as *const u8, len) }, n.sheet[k].as_bytes());
        }
        assert!(std::ptr::eq(names_of("league_akshan").unwrap(), n));
    }

    #[test]
    fn the_hooked_prologues_are_the_listed_builds() {
        for b in crate::build::BUILDS {
            let head = |rva: usize| b.sigs.iter().find(|s| s.0 == rva).map(|s| s.1).unwrap();
            // 0.7.0: push rbp / r15 / r14 / rsi / rdi / rbx, sub rsp 0xc8; push r15 / r14 / r12 / rsi / rdi / rbx, sub rsp 0x28
            assert_eq!(prologue_len(head(b.cmd_by_name)), Some(15), "{}", b.name);
            assert_eq!(prologue_len(head(b.node_image)), Some(13), "{}", b.name);
        }
        // 0.6.5's draw command (push rbp / r14 / rsi / rdi / rbx, sub rsp 0xc0) and what the hook must not take
        assert_eq!(prologue_len(&[0x55, 0x41, 0x56, 0x56, 0x57, 0x53, 0x48, 0x81, 0xec, 0xc0, 0, 0, 0, 0x48]), Some(13));
        assert_eq!(prologue_len(&[0x55, 0x48, 0x8b, 0x05, 1, 2, 3, 4, 0x41, 0x56, 0x56, 0x57, 0x53]), None); // a rip load
        assert_eq!(prologue_len(&[0x55, 0x41, 0x56]), None); // cut short
    }

    fn frames(v: &[[f32; 5]]) -> Vec<u8> {
        v.iter().flat_map(|f| f.iter().flat_map(|x| x.to_le_bytes())).collect()
    }

    /// A table at `mem` (8 buckets, ctrl after them) holding `entries` (bucket index, key, frames) -> its head.
    unsafe fn table(mem: &mut Vec<u8>, entries: &[(usize, &Vec<u8>, &Vec<u8>)]) -> [usize; 6] {
        let ctrl = 8 * BUCKET;
        mem[ctrl..].fill(0x80);
        let base = mem.as_mut_ptr() as usize;
        for &(i, key, fr) in entries {
            mem[ctrl + i] = 1;
            let b = base + ctrl - (i + 1) * BUCKET;
            let w = |o: usize, v: usize| std::ptr::write_unaligned((b + o) as *mut usize, v);
            w(0, key.len());
            w(8, key.as_ptr() as usize);
            w(16, key.len());
            w(24, fr.len() / FRAME);
            w(32, fr.as_ptr() as usize);
            w(40, fr.len() / FRAME);
        }
        [base + ctrl, 7usize, 0, entries.len(), 0, 0]
    }

    unsafe fn tag(t: usize, key: &[u8]) -> (usize, Vec<f32>) {
        let b = bucket_of(t, key).unwrap();
        let fp = q(b + 32);
        (q(b + 40), (0..5).map(|k| std::ptr::read_unaligned((fp + 4 * k) as *const f32)).collect())
    }

    #[test]
    fn every_tag_of_the_drawers_copy_holds_the_ui_sheets_frames() {
        let keys: Vec<Vec<u8>> = ["idle", "run", "dead", "hd_idle", "lo_idle", "bp"].iter().map(|k| k.as_bytes().to_vec()).collect();
        let own: Vec<Vec<u8>> = (0..6).map(|k| frames(&[[1.0 + k as f32, 0.0, 9.0, 9.0, 0.1]])).collect();
        let mut mem = vec![0u8; 8 * BUCKET + 8 + 16];
        // the UI sheets: the reel's (bp 2 frames, dead 1) and the idle's (idle 3 frames)
        let (k_bp, k_dead, k_idle) = (b"bp".to_vec(), b"dead".to_vec(), b"idle".to_vec());
        let f_bp = frames(&[[10.0, 20.0, 30.0, 40.0, 0.2], [50.0, 20.0, 30.0, 40.0, 0.1]]);
        let f_dead = frames(&[[90.0, 0.0, 60.0, 30.0, 0.3]]);
        let f_idle = frames(&[[2.0, 4.0, 6.0, 8.0, 0.1], [12.0, 4.0, 6.0, 8.0, 0.1], [22.0, 4.0, 6.0, 8.0, 0.4]]);
        let (mut m_reel, mut m_idle) = (vec![0u8; 8 * BUCKET + 8 + 16], vec![0u8; 8 * BUCKET + 8 + 16]);
        unsafe {
            let entries: Vec<(usize, &Vec<u8>, &Vec<u8>)> = (0..6).map(|i| (i, &keys[i], &own[i])).collect();
            let head = table(&mut mem, &entries);
            let t = head.as_ptr() as usize;
            let reel = table(&mut m_reel, &[(2, &k_bp, &f_bp), (5, &k_dead, &f_dead)]);
            let idle = table(&mut m_idle, &[(3, &k_idle, &f_idle)]);
            // the BP grid: every tag the reel, dead the dead pose, all / 2
            let grid = copy_from(t, reel.as_ptr() as usize, true, 2.0).expect("the grid's copy");
            for key in ["idle", "run", "hd_idle", "lo_idle", "bp"] {
                assert_eq!(tag(grid, key.as_bytes()), (2, vec![5.0, 10.0, 15.0, 20.0, 0.2]), "{key}");
            }
            assert_eq!(tag(grid, b"dead"), (1, vec![45.0, 0.0, 30.0, 15.0, 0.3]));
            // elsewhere: every tag the idle, dead too
            let face = copy_from(t, idle.as_ptr() as usize, false, 1.5).expect("the face's copy");
            for key in ["idle", "run", "dead", "lo_idle"] {
                let (n, f) = tag(face, key.as_bytes());
                assert_eq!(n, 3, "{key}");
                assert!((f[0] - 2.0 / 1.5).abs() < 1e-6 && (f[3] - 8.0 / 1.5).abs() < 1e-6 && f[4] == 0.1, "{key}: {f:?}");
            }
            // the game's own table is left as it was
            assert_eq!(tag(t, b"run"), (1, vec![2.0, 0.0, 9.0, 9.0, 0.1]));
            // a UI table without the frames a drawer needs: no copy
            assert!(copy_from(t, idle.as_ptr() as usize, true, 1.0).is_none());
            // a 1x hero's dead-less reel sheet: dead falls back to the reel
            let mut m_reel2 = vec![0u8; 8 * BUCKET + 8 + 16];
            let reel2 = table(&mut m_reel2, &[(1, &k_bp, &f_bp)]);
            let grid2 = copy_from(t, reel2.as_ptr() as usize, true, 1.0).unwrap();
            assert_eq!(tag(grid2, b"dead").0, 2);
        }
    }

    static SEEN_KIND: std::sync::atomic::AtomicU32 = std::sync::atomic::AtomicU32::new(0);

    unsafe extern "system" fn test_detour(kind: u32, regs: *mut [usize; 5]) {
        // clobber the float registers the stub must restore
        let x = std::hint::black_box([1.5f64, 2.5, 3.5, 4.5]);
        std::hint::black_box(x.iter().map(|v| v.sqrt()).sum::<f64>());
        SEEN_KIND.store(kind, Ordering::Relaxed);
        (*regs).swap(1, 2); // r8 <-> rdx
    }

    extern "system" fn target(a: usize, b: usize, c: usize, d: f64, e: usize, f: f64) -> f64 {
        a as f64 + 10.0 * b as f64 + 100.0 * c as f64 + 1000.0 * d + 10_000.0 * e as f64 + 100_000.0 * f
    }

    #[test]
    fn the_sink_stub_keeps_every_argument_but_the_ones_the_detour_swaps() {
        let stub = sink_stub(7, test_detour as unsafe extern "system" fn(u32, *mut [usize; 5]) as usize,
                             target as extern "system" fn(usize, usize, usize, f64, usize, f64) -> f64 as usize);
        unsafe {
            let page = VirtualAlloc(std::ptr::null_mut(), 0x1000, 0x3000, 0x40) as usize;
            assert_ne!(page, 0);
            std::ptr::copy_nonoverlapping(stub.as_ptr(), page as *mut u8, stub.len());
            let f: extern "system" fn(usize, usize, usize, f64, usize, f64) -> f64 = std::mem::transmute(page);
            // b and c swapped by the detour; a, d (xmm3) and the stack arguments e, f as given
            assert_eq!(f(1, 2, 3, 4.0, 5, 6.0), 1.0 + 30.0 + 200.0 + 4000.0 + 50_000.0 + 600_000.0);
            assert_eq!(SEEN_KIND.load(Ordering::Relaxed), 7);
        }
    }
}
