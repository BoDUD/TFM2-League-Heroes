//! 游戏的 GPU 图片缓存从 256 MiB 改成 [`LIMIT`]（用户 2026-10-30：「能强制改缓存吗 游戏的」「先收尾，再扩缓存」）。
//!
//! 游戏用 Skia（Ganesh GPU 后端）画图：贴图上传后放在 Skia 的 `GrResourceCache` 里，预算是 Skia 默认的
//! `kDefaultMaxBudget` = 256 MiB（构造函数里 `fMaxBytes = 0x10000000`，0.7.0 在 rva 0x3716120，写在对象 +0x70）。
//! 一屏要用的贴图超过预算，每次刷新 `purgeAsNeeded` 都把最久没用的清掉，下一帧再重新上传（Rin 的 PPU Core 0.2.16
//! 把它提到 512 MiB 治「多张大型精灵图共用原生 256 MiB 缓存时的重复解码」）。src/ui.rs 的小图集让 BP 和英雄界面装得下，
//! 但 tools/ci/ui_sheets.py 为它留的 192 MiB 预算已经满了（2026-10-30 石傲玉：191.7 MiB），所以把缓存本身放大。
//!
//! 做法：游戏的 GPU 上下文在 mod 加载前就建好了，改构造函数来不及，所以改正在用的那个缓存对象。挂在
//! `GrResourceCache::insertResource`（每个新贴图 / 缓冲区进缓存时调用，this 在 rcx）的开头：一小段机器码，不调 Rust、
//! 只动标志位，看到 `fMaxBytes` 还是 256 MiB 就改成 [`LIMIT`]，并记下缓存对象的地址；之后照常执行原来的开头。
//! Skia 自己每次刷新按新的上限判断要不要清（`fBudgetedBytes` +0x88 > `fMaxBytes` +0x70）。游戏或别的 mod 自己设过
//! 上限（不是 256 MiB）就不动。
//!
//! 找函数：[`INSERT`] 特征码（0.7.0 的开头 64 字节，call 的位移挖空），在 `.text` 里必须唯一；还要能找到构造函数里
//! `fMaxBytes = 256 MiB` 那两句（[`CTOR`]，证明字段布局还是 +0x70 / +0x78）。任一个找不到或不唯一就不挂，日志写原因，
//! 游戏照旧用 256 MiB。
//!
//! 日志：后台线程读缓存对象（ReadProcessMemory，对象没了也不会崩），把用量到过的新高写进 league.log（`GPU cache`）。
//!
//! 0.9.14（2026-11-06）：1 GiB → 1.5 GiB。11-06 的日志里 2297 s 时缓存用到 969 / 1024 MiB（上一次 1805 s 时 960），而所有英雄
//! 的图集加起来约 1415 MiB（凯隐一张 2048×8514，66.5 MiB），到了上限 Skia 就清掉最久没画的、下次画时再上传。[`LIMIT`] =
//! 0x6000_0000 仍在 imm32 里（`mov qword [rcx+0x70], imm32` 符号扩展：低于 2 GiB 才是正数），Skia 里把它当 32 位整数的地方也
//! 还是正数；物理内存不到 [`ROOMY`] 的机器（集显的贴图就在内存里）照旧 1 GiB（[`budget_for`]）。预算是 Skia 留着不清的上限，
//! 不是一下子占用的内存。日志：用量到 90% 写一行（降回 80% 以下再到 90% 再写），到了预算附近又掉下去（清掉了图）写一行，
//! 预算被别人改了写一行。

use std::ffi::c_void;
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use std::sync::Once;

use super::wlog;

/// Skia's kDefaultMaxBudget.
pub const DEFAULT: u64 = 256 << 20;
/// The budget the game's GPU cache gets: 1.5 GiB (0.9.14, was 1 GiB) - an imm32 in the stub, sign-extended, so it
/// must stay below 2 GiB (and is positive wherever Skia keeps it in a 32-bit int).
pub const LIMIT: u64 = 3 << 29;
/// The budget on a machine with less than [`ROOMY`] of physical memory (0.8.16's): an integrated GPU's images live
/// in that memory.
pub const FALLBACK: u64 = 1 << 30;
/// Physical memory from which the cache gets [`LIMIT`].
pub const ROOMY: u64 = 8 << 30;
/// The budget the stub writes (set by [`install_once`]; [`LIMIT`] until then).
static BUDGET: AtomicU64 = AtomicU64::new(LIMIT);

/// The budget for a machine with `ram` bytes of physical memory (None: unknown - the full [`LIMIT`]).
pub fn budget_for(ram: Option<u64>) -> u64 {
    match ram {
        Some(r) if r < ROOMY => FALLBACK,
        _ => LIMIT,
    }
}
/// GrResourceCache fields (0.7.0, checked by [`CTOR`]): fMaxBytes, fBytes, fBudgetedCount, fBudgetedBytes.
const MAX_BYTES: usize = 0x70;
const BYTES: usize = 0x78;
const BUDGETED_BYTES: usize = 0x88;

/// GrResourceCache::insertResource(GrGpuResource*): push rsi / rdi / rbx, sub rsp 0x20, mov rdi, rdx, mov rsi, rcx (the
/// 13 bytes the hook runs in its trampoline), call getNextTimestamp, ... fBytes += size, if budgeted fBudgetedCount++ /
/// fBudgetedBytes += size, then a tail jump to purgeAsNeeded.
const INSERT: game_places::Pattern = game_places::Pattern {
    bytes: &[0x56, 0x57, 0x53, 0x48, 0x83, 0xec, 0x20, 0x48, 0x89, 0xd7, 0x48, 0x89, 0xce, 0xe8, 0, 0, 0, 0,
             0x89, 0x47, 0x14, 0x48, 0x8d, 0x4e, 0x30, 0x8b, 0x5e, 0x44, 0xe8, 0, 0, 0, 0,
             0x48, 0x8b, 0x46, 0x38, 0x48, 0x63, 0x4e, 0x44, 0x48, 0x89, 0x7c, 0xc8, 0xf8, 0x89, 0x5f, 0x10,
             0x48, 0x8b, 0x87, 0x88, 0x00, 0x00, 0x00, 0x48, 0x83, 0xf8, 0xff, 0x74, 0, 0x48, 0x01, 0x46, 0x78],
    mask: &[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
};
/// The prologue the hook moves into its trampoline (no rip-relative operand).
const PROLOGUE: usize = 13;
/// GrResourceCache's constructor: fMaxBytes = 256 MiB (+0x70), fBytes = 0 (+0x78).
const CTOR: game_places::Pattern = game_places::Pattern {
    bytes: &[0x48, 0xc7, 0x47, 0x70, 0x00, 0x00, 0x00, 0x10, 0x48, 0xc7, 0x47, 0x78, 0x00, 0x00, 0x00, 0x00],
    mask: &[1; 16],
};

/// Where the stub writes the cache object's address (an 8-byte slot in the stub's page).
static SLOT: AtomicUsize = AtomicUsize::new(0);
static ONCE: Once = Once::new();

/// GlobalMemoryStatusEx's MEMORYSTATUSEX.
#[repr(C)]
#[derive(Default)]
struct MemoryStatus {
    length: u32,
    load: u32,
    total_phys: u64,
    avail_phys: u64,
    total_page_file: u64,
    avail_page_file: u64,
    total_virtual: u64,
    avail_virtual: u64,
    avail_extended_virtual: u64,
}

#[link(name = "kernel32")]
extern "system" {
    fn GetCurrentProcess() -> isize;
    fn VirtualAlloc(addr: *mut c_void, size: usize, kind: u32, protect: u32) -> *mut c_void;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
    fn FlushInstructionCache(process: isize, addr: *const c_void, size: usize) -> i32;
    fn GlobalMemoryStatusEx(status: *mut MemoryStatus) -> i32;
}

/// The machine's physical memory in bytes.
fn physical_memory() -> Option<u64> {
    let mut m = MemoryStatus { length: std::mem::size_of::<MemoryStatus>() as u32, ..Default::default() };
    (unsafe { GlobalMemoryStatusEx(&mut m) } != 0 && m.total_phys > 0).then_some(m.total_phys)
}

/// `limit` as the stub's imm32 - None when the sign extension would not give it back (2 GiB or more).
pub fn imm32(limit: u64) -> Option<[u8; 4]> {
    let v = i32::try_from(limit).ok()?;
    (v as i64 as u64 == limit).then_some(v.to_le_bytes())
}

/// The stub at `page` (`slot` = page + its returned offset): store rcx in the slot; if [rcx + 0x70] is 256 MiB make it
/// `limit`; run the moved prologue; jump back to `back`.
pub fn stub(page: usize, prologue: &[u8], back: usize, limit: u64) -> (Vec<u8>, usize) {
    let mut c = Vec::new();
    let store_at = c.len();
    c.extend_from_slice(&[0x48, 0x89, 0x0d, 0, 0, 0, 0]); // mov [rip + slot], rcx
    c.extend_from_slice(&[0x48, 0x81, 0x79, MAX_BYTES as u8]); // cmp qword [rcx + 0x70], DEFAULT
    c.extend_from_slice(&(DEFAULT as u32).to_le_bytes());
    c.extend_from_slice(&[0x75, 0x08]); // jne over the store
    c.extend_from_slice(&[0x48, 0xc7, 0x41, MAX_BYTES as u8]); // mov qword [rcx + 0x70], limit (imm32, sign-extended)
    c.extend_from_slice(&imm32(limit).unwrap_or_else(|| imm32(FALLBACK).unwrap()));
    c.extend_from_slice(prologue);
    c.extend_from_slice(&[0xff, 0x25, 0, 0, 0, 0]); // jmp [rip + 0]
    c.extend_from_slice(&(back as u64).to_le_bytes());
    while c.len() % 8 != 0 {
        c.push(0xcc);
    }
    let slot = c.len();
    c.extend_from_slice(&[0; 8]);
    let rel = (slot as i64 - (store_at as i64 + 7)) as i32;
    c[store_at + 3..store_at + 7].copy_from_slice(&rel.to_le_bytes());
    let _ = page;
    (c, slot)
}

/// insertResource and the constructor's fields found, the hook put in -> insertResource's address.
unsafe fn hook(module: usize) -> Result<usize, String> {
    let img = game_places::Image::from_module_light(module)?;
    let ins = img.find(&INSERT);
    let ctor = img.find(&CTOR);
    if ins.len() != 1 || ctor.len() != 1 {
        return Err(format!("GrResourceCache not recognised: insertResource {} match(es), its constructor's 256 MiB {} \
                            (need one each)", ins.len(), ctor.len()));
    }
    let func = module + ins[0];
    let head = hd_engine::read(func, PROLOGUE).ok_or("insertResource unreadable")?;
    let page = VirtualAlloc(std::ptr::null_mut(), 0x1000, 0x3000, 0x40) as usize;
    if page == 0 {
        return Err("VirtualAlloc failed".into());
    }
    let (code, slot) = stub(page, &head, func + PROLOGUE, BUDGET.load(Ordering::Relaxed));
    std::ptr::copy_nonoverlapping(code.as_ptr(), page as *mut u8, code.len());
    SLOT.store(page + slot, Ordering::Release);
    let mut jump = vec![0x48, 0xb8]; // mov rax, page; jmp rax (rax is free at a function's entry)
    jump.extend_from_slice(&(page as u64).to_le_bytes());
    jump.extend_from_slice(&[0xff, 0xe0]);
    jump.resize(PROLOGUE, 0xcc);
    let mut old = 0u32;
    if VirtualProtect(func as *mut c_void, jump.len(), 0x40, &mut old) == 0 {
        return Err("VirtualProtect failed".into());
    }
    std::ptr::copy_nonoverlapping(jump.as_ptr(), func as *mut u8, jump.len());
    let mut tmp = 0u32;
    VirtualProtect(func as *mut c_void, jump.len(), old, &mut tmp);
    FlushInstructionCache(GetCurrentProcess(), func as *const c_void, jump.len());
    Ok(ins[0])
}

fn u64_at(addr: usize) -> Option<u64> {
    hd_engine::read(addr, 8).map(|b| u64::from_le_bytes(b.try_into().unwrap()))
}

const MIB: u64 = 1 << 20;
/// a log line each time the budgeted bytes pass a new STEP, at most LINES of them
const STEP: u64 = 64 * MIB;
const LINES: usize = 40;
/// "90 % full" lines a session (said again only after the use fell under 80 %)
const FULL_LINES: usize = 20;
/// eviction lines a session: the use fell by EVICTED or more in one sample from within 10 % of the budget
const EVICT_LINES: usize = 40;
const EVICTED: u64 = 16 * MIB;

/// What the watcher has said of one cache: its lines come back from [`Watch::sample`] (tests).
#[derive(Default)]
pub struct Watch {
    peak: u64,
    lines: usize,
    /// the budget at the last sample (0: none yet)
    max: u64,
    /// the budgeted bytes at the last sample
    last: u64,
    /// at 90 % since the last "full" line (back under 80 % clears it)
    full: bool,
    full_lines: usize,
    evict_lines: usize,
    /// samples that found the use fallen from the budget (all of them, logged or not)
    pub evictions: usize,
}

impl Watch {
    /// One sample of the cache (budget `max`, all `bytes`, the `budgeted` part) -> the lines to log.
    pub fn sample(&mut self, max: u64, bytes: u64, budgeted: u64) -> Vec<String> {
        let mut out = Vec::new();
        if self.max != 0 && max != self.max {
            out.push(format!("GPU cache: budget now {} MiB (was {} MiB) - set by the game or another mod", max / MIB,
                             self.max / MIB));
        }
        if budgeted >= self.peak + STEP && self.lines < LINES {
            self.peak = budgeted / STEP * STEP;
            self.lines += 1;
            out.push(format!("GPU cache: {} MiB budgeted of {} MiB ({} MiB with the unbudgeted)", budgeted / MIB,
                             max / MIB, bytes / MIB));
        }
        if max > 0 {
            if !self.full && budgeted * 10 >= max * 9 {
                self.full = true;
                if self.full_lines < FULL_LINES {
                    self.full_lines += 1;
                    out.push(format!("GPU cache 90% full: {} MiB of {} MiB ({} MiB with the unbudgeted) - past the \
                                      budget Skia drops the images drawn longest ago and uploads them again when next drawn",
                                     budgeted / MIB, max / MIB, bytes / MIB));
                }
            } else if self.full && budgeted * 10 < max * 8 {
                self.full = false;
            }
            // the use fell from within 10 % of the budget and stayed near it (70 % or more): Skia evicting to make
            // room; a fall far under the budget is the game letting go of images, not counted
            let at_budget = self.last * 10 >= self.max.max(1) * 9;
            let near = budgeted * 10 >= max * 7;
            if self.max == max && at_budget && near && budgeted + EVICTED <= self.last {
                self.evictions += 1;
                if self.evict_lines < EVICT_LINES {
                    self.evict_lines += 1;
                    out.push(format!("GPU cache: {} -> {} MiB of {} MiB in 2 s at the budget (eviction {}: those images \
                                      are uploaded again when next drawn)", self.last / MIB, budgeted / MIB, max / MIB,
                                     self.evictions));
                }
            }
        }
        self.max = max;
        self.last = budgeted;
        out
    }
}

/// Every 2 s: the cache's budget and use ([`Watch`]); a line the first time each cache object is seen.
fn watch() {
    std::thread::spawn(|| {
        let mut seen = 0usize;
        let mut w = Watch::default();
        loop {
            std::thread::sleep(std::time::Duration::from_secs(2));
            let slot = SLOT.load(Ordering::Acquire);
            let Some(cache) = u64_at(slot).map(|c| c as usize).filter(|c| hd_engine::plausible(*c)) else { continue };
            let (Some(max), Some(bytes), Some(budgeted)) =
                (u64_at(cache + MAX_BYTES), u64_at(cache + BYTES), u64_at(cache + BUDGETED_BYTES)) else { continue };
            if cache != seen {
                seen = cache;
                w = Watch { peak: w.peak, lines: w.lines, full_lines: w.full_lines, evict_lines: w.evict_lines,
                            evictions: w.evictions, ..Watch::default() };
                wlog(format!("GPU cache {cache:#x}: budget {} MiB (Skia's default {} MiB), {} MiB in use",
                             max / MIB, DEFAULT / MIB, budgeted / MIB));
            }
            for line in w.sample(max, bytes, budgeted) {
                wlog(line);
            }
        }
    });
}

/// The hook and the watcher, once (lib.rs init, before the game builds).
pub fn install_once(module: usize) {
    ONCE.call_once(|| {
        let ram = physical_memory();
        let budget = budget_for(ram);
        BUDGET.store(budget, Ordering::Relaxed);
        match unsafe { hook(module) } {
            Ok(rva) => {
                wlog(format!("GPU cache: GrResourceCache::insertResource {rva:#x} hooked - the game's {} MiB GPU image \
                              cache becomes {} MiB ({} of physical memory)", DEFAULT / MIB, budget / MIB,
                             ram.map_or("unknown".to_string(), |r| format!("{} MiB", r / MIB))));
                watch();
            }
            Err(e) => wlog(format!("GPU cache left at {} MiB: {e}", DEFAULT / MIB)),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_stub_stores_the_cache_raises_the_default_and_goes_back() {
        let prologue = [0x56, 0x57, 0x53, 0x48, 0x83, 0xec, 0x20, 0x48, 0x89, 0xd7, 0x48, 0x89, 0xce];
        let (c, slot) = stub(0x10000, &prologue, 0x1403716b4d, LIMIT);
        // mov [rip + rel], rcx lands on the slot
        let rel = i32::from_le_bytes(c[3..7].try_into().unwrap()) as i64;
        assert_eq!(7 + rel, slot as i64);
        assert_eq!(slot % 8, 0);
        assert_eq!(c.len(), slot + 8);
        // cmp qword [rcx+0x70], 0x10000000; jne +8; mov qword [rcx+0x70], 0x60000000 (1.5 GiB)
        assert_eq!(&c[7..15], &[0x48, 0x81, 0x79, 0x70, 0x00, 0x00, 0x00, 0x10]);
        assert_eq!(&c[15..17], &[0x75, 0x08]);
        assert_eq!(&c[17..25], &[0x48, 0xc7, 0x41, 0x70, 0x00, 0x00, 0x00, 0x60]);
        // the prologue, then jmp [rip+0] to the instruction after it
        assert_eq!(&c[25..38], &prologue);
        assert_eq!(&c[38..44], &[0xff, 0x25, 0, 0, 0, 0]);
        assert_eq!(u64::from_le_bytes(c[44..52].try_into().unwrap()), 0x1403716b4d);
        // a machine short of memory: 0.8.16's 1 GiB
        let (c, _) = stub(0x10000, &prologue, 0x1403716b4d, FALLBACK);
        assert_eq!(&c[17..25], &[0x48, 0xc7, 0x41, 0x70, 0x00, 0x00, 0x00, 0x40]);
    }

    /// `mov qword [rcx+0x70], imm32` sign-extends: 1.5 GiB comes back as itself, 2 GiB and more would not (a negative
    /// 64-bit budget) and never reach the stub.
    #[test]
    fn the_limit_fits_the_stubs_imm32() {
        assert_eq!(LIMIT, 0x6000_0000);
        assert!(LIMIT > FALLBACK && FALLBACK > DEFAULT && LIMIT < 1 << 31);
        for limit in [LIMIT, FALLBACK, DEFAULT] {
            let b = imm32(limit).unwrap();
            assert_eq!(i32::from_le_bytes(b) as i64 as u64, limit);
        }
        assert_eq!(imm32(2 << 30), None);
        assert_eq!(imm32(1 << 31 | 1 << 29), None);
        assert_eq!(INSERT.bytes.len(), INSERT.mask.len());
        assert_eq!(&INSERT.bytes[..PROLOGUE], &[0x56, 0x57, 0x53, 0x48, 0x83, 0xec, 0x20, 0x48, 0x89, 0xd7, 0x48, 0x89, 0xce]);
        assert!(INSERT.mask[..PROLOGUE].iter().all(|m| *m == 1));
    }

    #[test]
    fn a_machine_short_of_memory_keeps_one_gib() {
        assert_eq!(budget_for(Some(32 << 30)), LIMIT);
        assert_eq!(budget_for(Some(ROOMY)), LIMIT);
        assert_eq!(budget_for(Some(ROOMY - 1)), FALLBACK);
        assert_eq!(budget_for(Some(4 << 30)), FALLBACK);
        assert_eq!(budget_for(None), LIMIT);
        // this machine's memory is read
        assert!(physical_memory().is_some_and(|r| r > 1 << 30));
    }

    /// The watcher's lines: new highs in 64 MiB steps as before, then 90 % full (once until the use falls under 80 %),
    /// a fall from the budget (Skia evicting), and a budget someone else changed.
    #[test]
    fn the_watcher_tells_the_budget_filling_and_evicting() {
        let max = LIMIT;
        let mut w = Watch::default();
        let lines = w.sample(max, 300 * MIB, 200 * MIB);
        assert_eq!(lines.len(), 1, "{lines:?}");
        assert!(lines[0].contains("192 MiB budgeted") || lines[0].contains("200 MiB budgeted"), "{lines:?}");
        assert!(w.sample(max, 300 * MIB, 210 * MIB).is_empty());
        // 90 %: 1383 MiB of 1536
        let lines = w.sample(max, 1500 * MIB, 1390 * MIB);
        assert!(lines.iter().any(|l| l.starts_with("GPU cache 90% full: 1390 MiB of 1536 MiB")), "{lines:?}");
        assert!(w.sample(max, 1500 * MIB, 1500 * MIB).iter().all(|l| !l.contains("90% full")), "said once");
        // evicting at the budget: 1500 -> 1450
        let lines = w.sample(max, 1500 * MIB, 1450 * MIB);
        assert!(lines.iter().any(|l| l.contains("1500 -> 1450 MiB of 1536 MiB in 2 s at the budget (eviction 1")),
                "{lines:?}");
        assert_eq!(w.evictions, 1);
        // a small dip is no eviction; a fall far under the budget (the game letting go of images) neither
        assert!(w.sample(max, 1500 * MIB, 1440 * MIB).is_empty());
        assert!(w.sample(max, 900 * MIB, 800 * MIB).is_empty(), "far under the budget: freed, not evicted");
        assert!(w.sample(max, 900 * MIB, 700 * MIB).is_empty());
        assert_eq!(w.evictions, 1);
        // under 80 % since: the next 90 % is said again
        let lines = w.sample(max, 1500 * MIB, 1400 * MIB);
        assert!(lines.iter().any(|l| l.contains("90% full")), "{lines:?}");
        // another mod set the budget
        let lines = w.sample(2 << 30, 1500 * MIB, 1400 * MIB);
        assert!(lines.iter().any(|l| l.contains("budget now 2048 MiB (was 1536 MiB)")), "{lines:?}");
    }

    /// The game's EXE (when it is installed here): insertResource and the constructor each found once, at 0.7.0's places.
    #[test]
    fn the_installed_exe_has_one_grresourcecache() {
        let exe = r"D:\steam\steamapps\common\Teamfight Manager2\TeamfightManager2.exe";
        let Ok(data) = std::fs::read(exe) else { return };
        let img = game_places::Image::from_file(&data).unwrap();
        let (ins, ctor) = (img.find(&INSERT), img.find(&CTOR));
        assert_eq!(ins.len(), 1, "{ins:x?}");
        assert_eq!(ctor.len(), 1, "{ctor:x?}");
        if ins[0] == 0x3716b40 {
            assert_eq!(ctor[0], 0x3716171); // 0.7.0
        }
    }
}
