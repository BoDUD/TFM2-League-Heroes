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
//! - 它们把名字交出去的函数（cmd_by_name / node_image / cmd_uv）：入口挂一段保存寄存器的跳板，名字正是刚才换过图的那个，
//!   就换成小图集的名字——画的时候游戏取到的就是小图集。别的调用原样放过。
//!
//! 游戏 0.7.2（2026-11-11）：图鉴 / 头像和选人位不再调图片节点，自己拼一条贴图绘制命令（标签 0x…03，名字复制一份放在
//! +8 的 String 里）交给设置 UV 的函数（cmd_uv，rdx = 这条命令，它把命令连同 String 整个搬进输出）。这里在它入口把
//! String 里的名字原地换成小图集的（小图集的名字比整张图集的短，直接写进原来的缓冲；更长时用和游戏同一个进程堆
//! 重新分配，旧的释放）。
//!
//! 保护：一处画英雄的地方取了 40 次小图集、一次都没把名字交到这几个函数（游戏又改了交名字的地方），就不再给它小图集——
//! 不然它会用小图集的 UV 去画整张图集。0.7.1 实测每 300 次有 297~299 次交到。
//!
//! 战场不动（它画整张图集里的高清帧）。没有小图集的英雄（别的模组的、还没打包的）、找不到这些地址的游戏版本：照旧画整张
//! 图集。

use std::alloc::{GlobalAlloc, Layout, System};
use std::cell::RefCell;
use std::collections::HashMap;
use std::ffi::c_void;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use super::build::Build;
use super::hd::{self, Hero};
use super::lookup::{self, bucket_of, plausible, q, BUCKET, FRAME};
use super::wlog;

/// tools/package_mod.py UI_DIR and UI_KINDS: the idle's sheet (every drawer but the BP grid) and the reel's (the BP grid).
const DIR: &str = "ui_sheets";
const KINDS: [&str; 2] = ["idle", "bp"];
const IDLE: usize = 0;
const REEL: usize = 1;

/// The length of the sinks' first whole instructions the trampoline runs before it jumps back: pushes, `sub rsp` and
/// `movabs` (no rip-relative operand) until the 12 bytes the jump overwrites are covered - push r64 (50..57, 41 50..57),
/// sub rsp imm8 / imm32 (48 83 ec ib / 48 81 ec id), movabs r64, imm64 (48 / 49 b8..bf). 0.6.5's draw command: push
/// rbp / r14 / rsi / rdi / rbx, sub rsp 0xc0 (13 bytes); 0.7.0's pushes r15 too, sub rsp 0xc8 (15); the image node's:
/// push r15 / r14 / r12 / rsi / rdi / rbx, sub rsp 0x28 (13); 0.7.2's UV setter: push rsi, sub rsp 0x20, movabs rax,
/// 0x8000000000000000 (15). A sink starting otherwise gets no hook (and the UI no UI sheets).
pub fn prologue_len(code: &[u8]) -> Option<usize> {
    let mut i = 0;
    while i < 12 {
        match code.get(i..)? {
            [0x50..=0x57, ..] => i += 1,
            [0x41, 0x50..=0x57, ..] => i += 2,
            [0x48, 0x83, 0xec, _, ..] => i += 4,
            [0x48, 0x81, 0xec, _, _, _, _, ..] => i += 7,
            [0x48 | 0x49, 0xb8..=0xbf, _, _, _, _, _, _, _, _, ..] => i += 10,
            _ => return None,
        }
    }
    Some(i)
}
/// which sink called [`swap`]: the draw command (name ptr in rdx, len in r8), the image node (&String in rdx), the UV
/// setter (rdx = &draw command: its tag at +0, the name String {cap, ptr, len} at +8)
const CMD: u32 = 0;
const NODE: u32 = 1;
const UV: u32 = 2;
const SINKS: [&str; 3] = ["draw command", "image node", "UV command"];
const MAX_LINES: usize = 600;
/// after this many UI sheet lookups by a drawer, the log says how many of them reached a sink
const TALLY: usize = 300;
/// after this many UI sheet lookups by a drawer none of which reached a sink, the drawer gets no UI sheets any more
const GUARD: usize = 40;

/// The sinks hooked: the drawers draw from the UI sheets.
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

/// The hero a drawer's resource name is of - `.../champions/<id>#anim` or `#sheet` - and its pack, when it is one of
/// `packs`' (`<pack>_...`: league_*, tft_*, the packs whose tables are registered - src/hd.rs Heroes::packs): only they
/// have UI sheets.
fn hero_id<'a>(name: &'a str, packs: &[&'static str]) -> Option<(&'a str, &'static str)> {
    let (path, _) = name.rsplit_once('#')?;
    let id = path.rsplit('/').next()?;
    let pack = packs.iter().find(|p| id.strip_prefix(**p).is_some_and(|rest| rest.starts_with('_')))?;
    Some((id, pack))
}

/// Hero `id`'s UI sheets in `pack` (`asset/<pack>/ui_sheets/...`).
fn names_of(id: &str, pack: &str) -> Option<&'static Names> {
    let mut m = NAMES.lock().ok()?;
    if let Some(n) = m.get(id) {
        return Some(n);
    }
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

/// (the game's table, drawer) -> (its ctrl, the UI table, its ctrl, the divisor's bits, the copy). The divisor is in
/// the key: a hero whose pack registered after its first lookup (src/share.rs) is divided by its own from then on.
static COPIES: LazyLock<Mutex<HashMap<(usize, usize), (usize, usize, usize, u32, usize)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

unsafe fn copy_of(t: usize, ut: usize, k: usize, reel: bool, div: f32) -> Option<usize> {
    let (ctrl, uctrl) = (q(t), q(ut));
    if let Ok(c) = COPIES.lock() {
        if let Some(&(c0, u0, uc0, d0, copy)) = c.get(&(t, k)) {
            if (c0, u0, uc0, d0) == (ctrl, ut, uctrl, div.to_bits()) {
                return Some(copy);
            }
        }
    }
    let copy = copy_from(t, ut, reel, div)?;
    if let Ok(mut c) = COPIES.lock() {
        c.insert((t, k), (ctrl, ut, uctrl, div.to_bits(), copy));
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
static SWAPS: [AtomicUsize; 3] = [const { AtomicUsize::new(0) }; 3];
/// per drawer: its UI sheet lookups, and the names of them handed on to a sink (fewer: the BP grid's cards scrolled out of
/// sight and the pick moment's layout passes look the sheet up and draw nothing)
static LOOKED: [AtomicUsize; 8] = [const { AtomicUsize::new(0) }; 8];
static HANDED: [AtomicUsize; 8] = [const { AtomicUsize::new(0) }; 8];
/// per drawer: no UI sheets any more - its first GUARD UI sheet lookups reached no sink: it hands the name on somewhere
/// this build's places do not know, and would draw the battle sheet with the UI sheet's UV
static OFF: [AtomicBool; 8] = [const { AtomicBool::new(false) }; 8];

fn line(msg: impl FnOnce() -> String) {
    if LINES.fetch_add(1, Ordering::Relaxed) < MAX_LINES {
        wlog(msg());
    }
}

/// The in-game check of this module: after TALLY UI sheet lookups by drawer `k`, how many reached a sink; none of the
/// first GUARD (the drawer hands its name on somewhere else and draws the battle sheet with the UI sheet's UV): the
/// drawer is turned off ([`OFF`]) and keeps the battle sheet.
fn tally(k: usize) {
    let Some(n) = LOOKED.get(k).map(|c| c.fetch_add(1, Ordering::Relaxed) + 1) else { return };
    let handed = HANDED[k].load(Ordering::Relaxed);
    if n == GUARD && handed == 0 {
        OFF[k].store(true, Ordering::Relaxed);
        line(|| format!("UI drawer {k}: {GUARD} UI sheet lookups and none handed on to a hooked sink - no UI sheets for it \
                         from now on (it draws its battle sheet)"));
    }
    if n == TALLY {
        line(|| format!("UI drawer {k}: {TALLY} UI sheet lookups, {handed} of them handed on to be drawn"));
    }
}

/// The anim lookup of `name` from UI drawer `k` (src/lookup.rs after_anim) returned `got`: the copy drawing from the
/// hero's UI sheet, or None - no UI sheets for it: the drawer keeps the battle sheet's frames, as before.
pub(crate) unsafe fn anim(ctx: usize, name: &str, got: usize, k: usize, hero: Option<&Hero>) -> Option<usize> {
    if OFF.get(k).is_none_or(|o| o.load(Ordering::Relaxed)) {
        return None;
    }
    let b = lookup::build();
    let (id, pack) = hero_id(name, &hd::heroes().packs)?;
    let n = names_of(id, pack)?;
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
    let (id, pack) = hero_id(name, &hd::heroes().packs)?;
    let n = names_of(id, pack)?;
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

/// `len` bytes at `ptr` are `name`.
unsafe fn is_name(ptr: usize, len: usize, name: &[u8]) -> bool {
    len == name.len() && plausible(ptr) && std::slice::from_raw_parts(ptr as *const u8, len) == name
}

/// The UV setter's sink: `cmd` is a draw command whose tag is a niche value (0x80000000000000xx) and whose String at +8
/// ({cap, ptr, len}, the drawer's own copy, moved into the out command and freed by the game later) holds `name` - its
/// text becomes `new`: written into the same buffer when it fits (the UI sheets' names are shorter than the battle
/// sheets'), else into a buffer from the process heap (std's System allocator: HeapAlloc / HeapFree on the process heap,
/// as the game's own) with the old one freed. False (nothing written) for any other command.
unsafe fn swap_in_command(cmd: usize, name: &[u8], new: &str) -> bool {
    if !plausible(cmd) || q(cmd) & !0xff != 1 << 63 {
        return false;
    }
    let (cap, ptr, len) = (q(cmd + 8), q(cmd + 16), q(cmd + 24));
    if cap < len || cap > 1 << 20 || !is_name(ptr, len, name) {
        return false;
    }
    let n = new.len();
    if n <= cap {
        std::ptr::copy_nonoverlapping(new.as_ptr(), ptr as *mut u8, n);
    } else {
        let buf = System.alloc(Layout::from_size_align_unchecked(n, 1));
        if buf.is_null() {
            return false;
        }
        std::ptr::copy_nonoverlapping(new.as_ptr(), buf, n);
        std::ptr::write_unaligned((cmd + 8) as *mut usize, n);
        std::ptr::write_unaligned((cmd + 16) as *mut usize, buf as usize);
        System.dealloc(ptr as *mut u8, Layout::from_size_align_unchecked(cap, 1));
    }
    std::ptr::write_unaligned((cmd + 24) as *mut usize, n);
    true
}

/// Called by the sinks' stub with the caller's registers [r9, r8, rdx, rcx, return address]: the name handed on is the
/// one the last UI sheet lookup redirected - swapped for the UI sheet's (rdx / r8 rewritten; the UV setter's command
/// rewritten in place).
unsafe extern "system" fn swap(sink: u32, regs: *mut [usize; 5]) {
    let _ = std::panic::catch_unwind(|| unsafe {
        with_state(|s| {
            let Some((n, kd, k)) = s.swap else { return };
            let r = &mut *regs;
            let done = match sink {
                CMD if is_name(r[2], r[1], &s.name) => {
                    r[2] = n.sheet[kd].as_ptr() as usize;
                    r[1] = n.sheet[kd].len();
                    true
                }
                NODE if plausible(r[2]) && is_name(q(r[2] + 8), q(r[2] + 16), &s.name) => {
                    r[2] = n.string[kd].as_ptr() as usize;
                    true
                }
                UV => swap_in_command(r[2], &s.name, &n.sheet[kd]),
                _ => false,
            };
            if !done {
                return;
            }
            s.swap = None;
            if let Some(c) = HANDED.get(k) {
                c.fetch_add(1, Ordering::Relaxed);
            }
            if SWAPS.get(sink as usize).is_some_and(|c| c.fetch_add(1, Ordering::Relaxed) == 0) {
                line(|| format!("UI drawer {k}: {} handed on as {} ({})", String::from_utf8_lossy(&s.name), n.sheet[kd],
                                SINKS[sink as usize]));
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

/// The sinks hooked (src/lookup.rs install_once, after the lookups): on when the build knows the drawers' sheet lookups,
/// the draw command made from a name and the image node's setter or the UV setter (0.7.2), and every known one is in.
pub fn install(b: &Build, module: usize) {
    if b.ui_anim_ret.is_empty() || b.ui_sheet_ret.len() != b.ui_anim_ret.len() || b.cmd_by_name == 0
        || (b.node_image == 0 && b.cmd_uv == 0)
    {
        wlog("UI sheets off: this game build's UI sheet places are not known - the UI draws the battle sheets");
        return;
    }
    let hooks: Vec<(u32, usize, Result<(), String>)> = [(CMD, b.cmd_by_name), (NODE, b.node_image), (UV, b.cmd_uv)]
        .into_iter()
        .filter(|(_, rva)| *rva != 0)
        .map(|(sink, rva)| (sink, rva, unsafe { hook_sink(module + rva, sink) }))
        .collect();
    if hooks.iter().all(|h| h.2.is_ok()) {
        ON.store(true, Ordering::Release);
    }
    let said: Vec<String> = hooks.iter().map(|(sink, rva, r)| format!("{} {rva:#x} {r:?}", SINKS[*sink as usize])).collect();
    wlog(format!("UI sheets {}: {}; the encyclopedia / faces, pick slots, pick moment and scoreboard draw {DIR}/idle, the \
                  BP grid {DIR}/bp", if ON.load(Ordering::Relaxed) { "on" } else { "off" }, said.join(", ")));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_drawers_name_gives_the_hero_and_its_ui_sheets() {
        let both = ["league", "tft"];
        assert_eq!(hero_id("asset/base/aseprite_resources/champions/league_akshan#anim", &both), Some(("league_akshan", "league")));
        assert_eq!(hero_id("asset/base/aseprite_resources/champions/tft_powder#sheet", &both), Some(("tft_powder", "tft")));
        assert_eq!(hero_id("asset/base/aseprite_resources/champions/alchemist#sheet", &both), None);
        assert_eq!(hero_id("asset/base/aseprite_resources/champions/league_akshan", &both), None);
        assert_eq!(hero_id("asset/base/aseprite_resources/champions/leagueakshan#anim", &both), None);
        // a pack whose table is not registered (its DLL not loaded): no UI sheets for its heroes
        assert_eq!(hero_id("asset/base/aseprite_resources/champions/tft_powder#sheet", &["league"]), None);
        let n = names_of("league_akshan", "league").unwrap();
        assert_eq!(n.anim, ["asset/league/ui_sheets/idle/league_akshan#anim", "asset/league/ui_sheets/bp/league_akshan#anim"]);
        assert_eq!(n.sheet[REEL], "asset/league/ui_sheets/bp/league_akshan#sheet");
        assert_eq!(names_of("tft_powder", "tft").unwrap().sheet[IDLE], "asset/tft/ui_sheets/idle/tft_powder#sheet");
        for k in [IDLE, REEL] {
            let [cap, ptr, len] = n.string[k];
            assert_eq!((cap, len), (n.sheet[k].len(), n.sheet[k].len()));
            assert_eq!(unsafe { std::slice::from_raw_parts(ptr as *const u8, len) }, n.sheet[k].as_bytes());
        }
        assert!(std::ptr::eq(names_of("league_akshan", "league").unwrap(), n));
    }

    #[test]
    fn the_hooked_prologues_are_the_listed_builds() {
        for b in crate::build::BUILDS {
            let head = |rva: usize| b.sigs.iter().find(|s| s.0 == rva).map(|s| s.1).unwrap();
            // 0.7.0 to 0.7.2: push rbp / r15 / r14 / rsi / rdi / rbx, sub rsp 0xc8
            assert_eq!(prologue_len(head(b.cmd_by_name)), Some(15), "{}", b.name);
            // to 0.7.1: push r15 / r14 / r12 / rsi / rdi / rbx, sub rsp 0x28
            if b.node_image != 0 {
                assert_eq!(prologue_len(head(b.node_image)), Some(13), "{}", b.name);
            }
            // 0.7.2: push rsi, sub rsp 0x20, movabs rax, 0x8000000000000000
            if b.cmd_uv != 0 {
                assert_eq!(prologue_len(head(b.cmd_uv)), Some(15), "{}", b.name);
            }
        }
        // 0.6.5's draw command (push rbp / r14 / rsi / rdi / rbx, sub rsp 0xc0) and what the hook must not take
        assert_eq!(prologue_len(&[0x55, 0x41, 0x56, 0x56, 0x57, 0x53, 0x48, 0x81, 0xec, 0xc0, 0, 0, 0, 0x48]), Some(13));
        assert_eq!(prologue_len(&[0x55, 0x48, 0x8b, 0x05, 1, 2, 3, 4, 0x41, 0x56, 0x56, 0x57, 0x53]), None); // a rip load
        assert_eq!(prologue_len(&[0x55, 0x41, 0x56]), None); // cut short
        assert_eq!(prologue_len(&[0x56, 0x48, 0x83, 0xec, 0x20, 0x48, 0xb8, 0, 0, 0, 0, 0, 0]), None); // movabs cut short
    }

    /// A sprite command as a 0.7.2 drawer builds it: its tag, then the name copied into a buffer of `cap` bytes from the
    /// process heap (as the game's HeapAlloc).
    unsafe fn command(text: &str, cap: usize) -> [usize; 4] {
        let p = System.alloc(Layout::from_size_align(cap, 1).unwrap());
        std::ptr::copy_nonoverlapping(text.as_ptr(), p, text.len());
        [0x8000000000000003, cap, p as usize, text.len()]
    }

    unsafe fn text_of(c: &[usize; 4]) -> Vec<u8> {
        std::slice::from_raw_parts(c[2] as *const u8, c[3]).to_vec()
    }

    unsafe fn free(c: [usize; 4]) {
        System.dealloc(c[2] as *mut u8, Layout::from_size_align(c[1], 1).unwrap());
    }

    #[test]
    fn the_uv_setters_command_gets_the_ui_sheets_name() {
        let old = "asset/base/aseprite_resources/champions/league_akshan#sheet";
        let ui = "asset/league/ui_sheets/idle/league_akshan#sheet";
        unsafe {
            // shorter (every UI sheet's name is): written into the same buffer, the capacity kept
            let mut c = command(old, old.len());
            let p0 = c[2];
            assert!(swap_in_command(c.as_mut_ptr() as usize, old.as_bytes(), ui));
            assert_eq!((c[0], c[1], c[2], c[3]), (0x8000000000000003, old.len(), p0, ui.len()));
            assert_eq!(text_of(&c), ui.as_bytes());
            // another hero's name, a tag that is not a niche value: left as they were
            let mut d = command(old, old.len());
            let before = d;
            assert!(!swap_in_command(d.as_mut_ptr() as usize, b"asset/base/aseprite_resources/champions/league_zed#sheet", ui));
            d[0] = 7;
            assert!(!swap_in_command(d.as_mut_ptr() as usize, old.as_bytes(), ui));
            d[0] = before[0];
            assert_eq!(d, before);
            assert_eq!(text_of(&d), old.as_bytes());
            // longer than the copy's buffer: a buffer of its own from the process heap, the old one freed
            let short = "asset/x/league_akshan#sheet";
            let mut e = command(short, short.len());
            assert!(swap_in_command(e.as_mut_ptr() as usize, short.as_bytes(), ui));
            assert_eq!((e[1], e[3]), (ui.len(), ui.len()));
            assert_eq!(text_of(&e), ui.as_bytes());
            for x in [c, d, e] {
                free(x);
            }
        }
    }

    #[test]
    fn the_armed_name_is_swapped_once_by_whichever_sink_gets_it_first() {
        let old = "asset/base/aseprite_resources/champions/league_akshan#sheet";
        let n = names_of("league_akshan", "league").unwrap();
        let arm = || with_state(|s| {
            s.name = old.as_bytes().to_vec();
            s.swap = Some((n, IDLE, 0));
        });
        unsafe {
            // 0.7.2's encyclopedia: the UV setter gets its command
            arm();
            let mut c = command(old, old.len());
            let mut regs = [0, 0, c.as_mut_ptr() as usize, 0, 0];
            swap(UV, &mut regs);
            assert_eq!(text_of(&c), n.sheet[IDLE].as_bytes());
            // once: the next command with the same name (another drawing) keeps it
            let mut c2 = command(old, old.len());
            let mut regs = [0, 0, c2.as_mut_ptr() as usize, 0, 0];
            swap(UV, &mut regs);
            assert_eq!(text_of(&c2), old.as_bytes());
            // the BP grid: the draw command by name gets the UI sheet's ptr / len; the UV setter after it sees nothing armed
            arm();
            let mut regs = [9, old.len(), old.as_ptr() as usize, 1, 0];
            swap(CMD, &mut regs);
            assert_eq!(regs, [9, n.sheet[IDLE].len(), n.sheet[IDLE].as_ptr() as usize, 1, 0]);
            let mut regs = [0, 0, c2.as_mut_ptr() as usize, 0, 0];
            swap(UV, &mut regs);
            assert_eq!(text_of(&c2), old.as_bytes());
            // the image node (to 0.7.1): rdx = &String
            arm();
            let s = [old.len(), old.as_ptr() as usize, old.len()];
            let mut regs = [0, 0, s.as_ptr() as usize, 0, 0];
            swap(NODE, &mut regs);
            assert_eq!(regs[2], n.string[IDLE].as_ptr() as usize);
            for x in [c, c2] {
                free(x);
            }
        }
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
