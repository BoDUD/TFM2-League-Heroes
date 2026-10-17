//! 音频预读（0.7.27，用户 2026-10-17：「做方案：音频放 sound/bgm（package_mod.py）+ league.dll 后台预读，开 PR」）。
//!
//! 主包的 2088 个音频打包在 `sound/bgm/`（tools/package_mod.py）：游戏启动时把 mod 的每个文件读进内存，只有
//! `/sound/bgm/` 下的 .mp3 / .wav 播放时才打开，启动要开的文件少了四成（docs/perf.md 第 7 节）。代价是音频第一次播放时
//! 游戏在主线程里打开、读这个文件：不在系统缓存里时，机械盘上一个要等 15–30 ms，同时第一次响 6 个就有一帧超过 100 ms；
//! 在缓存里时和读进内存的音频一样快（实测首次播放的停顿中位 5.5 ms，原版音效 6.7 ms）。
//!
//! 所以标题画面出来以后（DLL 本身在 `asset loading done!` 之后才初始化，管不了启动），一个后台线程把这个文件夹的文件
//! 按在盘上的先后（每个文件第一个簇的位置）读一遍，进系统缓存：那块机械盘上 2088 个、37 MB 冷读 2.4 秒，比按名字读的
//! 每个十几毫秒快得多。线程的 CPU 优先级最低，每个文件按低 I/O 优先级读，游戏自己读盘总是先走；不用线程的后台模式：
//! 它连读进来的页也标成最低的内存优先级，内存一紧最先被拿走（测试那台电脑上几秒钟就又冷了）。只读，读完在 league.log
//! 记一行。内存很紧时系统缓存还是可能把它们挤出去，那时第一次播放照旧等盘。

use std::ffi::OsString;
use std::os::windows::ffi::OsStringExt;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::Instant;

use mod_api_stable::*;

static STARTED: AtomicBool = AtomicBool::new(false);

#[link(name = "kernel32")]
extern "system" {
    fn GetCurrentThread() -> isize;
    fn SetThreadPriority(thread: isize, priority: i32) -> i32;
    fn SetFileInformationByHandle(file: isize, class: i32, info: *const u32, size: u32) -> i32;
    fn GetModuleHandleExW(flags: u32, name: *const u16, module: *mut usize) -> i32;
    fn GetModuleFileNameW(module: usize, buf: *mut u16, len: u32) -> u32;
    fn DeviceIoControl(device: isize, code: u32, input: *const u8, input_len: u32, output: *mut u8, output_len: u32,
                       returned: *mut u32, overlapped: *mut u8) -> i32;
}
const THREAD_PRIORITY_LOWEST: i32 = -2;
const FILE_IO_PRIORITY_HINT_INFO: i32 = 12;
const IO_PRIORITY_HINT_LOW: u32 = 1;
const FROM_ADDRESS: u32 = 0x4;
const UNCHANGED_REFCOUNT: u32 = 0x2;
const FSCTL_GET_RETRIEVAL_POINTERS: u32 = 0x0009_0073;

/// The folder league.dll was loaded from: `mods/league`, or the Workshop item's folder.
fn dll_dir() -> Option<PathBuf> {
    let mut module = 0usize;
    let mut buf = vec![0u16; 32_768];
    unsafe {
        if GetModuleHandleExW(FROM_ADDRESS | UNCHANGED_REFCOUNT, dll_dir as *const () as *const u16, &mut module) == 0 {
            return None;
        }
        let n = GetModuleFileNameW(module, buf.as_mut_ptr(), buf.len() as u32) as usize;
        if n == 0 || n >= buf.len() {
            return None;
        }
        PathBuf::from(OsString::from_wide(&buf[..n])).parent().map(Path::to_path_buf)
    }
}

/// Where the file starts on the disk (its first cluster); u64::MAX when unknown (a tiny file kept in the MFT, another
/// file system): those go last.
fn first_cluster(path: &Path) -> u64 {
    use std::os::windows::io::AsRawHandle;
    let Ok(file) = std::fs::File::open(path) else { return u64::MAX };
    let start = [0u8; 8]; // STARTING_VCN_INPUT_BUFFER: from the file's first cluster
    let mut out = [0u8; 32]; // RETRIEVAL_POINTERS_BUFFER: count, starting VCN, then the first extent (next VCN, LCN)
    let mut got = 0u32;
    let ok = unsafe {
        DeviceIoControl(file.as_raw_handle() as isize, FSCTL_GET_RETRIEVAL_POINTERS, start.as_ptr(), 8,
                        out.as_mut_ptr(), 32, &mut got, std::ptr::null_mut())
    };
    // a file in several pieces fails with ERROR_MORE_DATA after filling in the first extent
    if (ok == 0 && got < 32) || out[..4] == [0, 0, 0, 0] {
        return u64::MAX;
    }
    u64::from_le_bytes(out[24..32].try_into().unwrap())
}

/// One file's bytes, read at low I/O priority (the game's own reads of the disk go first).
fn read_low(path: &Path) -> Option<usize> {
    use std::io::Read;
    use std::os::windows::io::AsRawHandle;
    let mut file = std::fs::File::open(path).ok()?;
    let hint = IO_PRIORITY_HINT_LOW;
    unsafe { SetFileInformationByHandle(file.as_raw_handle() as isize, FILE_IO_PRIORITY_HINT_INFO, &hint, 4) };
    let mut bytes = Vec::new();
    file.read_to_end(&mut bytes).ok()
}

/// Reads every file of `dir` once, in disk order, so the OS keeps them cached. -> (files, bytes).
pub fn warm(dir: &Path) -> (usize, usize) {
    let Ok(entries) = std::fs::read_dir(dir) else { return (0, 0) };
    let mut files: Vec<(u64, PathBuf)> =
        entries.flatten().map(|e| e.path()).filter(|p| p.is_file()).map(|p| (first_cluster(&p), p)).collect();
    files.sort();
    let bytes = files.iter().filter_map(|(_, p)| read_low(p)).sum();
    (files.len(), bytes)
}

/// Starts the warm-up once, from the first client frame: by then the title is up and the game has read its files.
pub struct Warm;

impl StableExtension for Warm {
    fn post_update(&self, _ctx: &mut StableClient<'_>, _dt_micros: u64) {
        if STARTED.swap(true, Ordering::Relaxed) {
            return;
        }
        let Some(dir) = dll_dir().map(|d| d.join("sound").join("bgm")) else {
            crate::wlog("sound/bgm warm-up skipped: league.dll's folder is unknown");
            return;
        };
        std::thread::spawn(move || {
            // lowest CPU priority, low I/O priority per file (read_low) - but not the thread's background mode: that
            // also lowers the memory priority of the pages it reads, and Windows hands those out first when memory
            // is short (on a busy PC the clips were gone again within seconds)
            unsafe { SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_LOWEST) };
            let t = Instant::now();
            let (files, bytes) = warm(&dir);
            crate::wlog(format!("sound/bgm warmed: {files} clips, {:.1} MB in {:.1} s ({})", bytes as f64 / 1e6,
                                t.elapsed().as_secs_f64(), dir.display()));
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_file_of_the_folder_is_read_once() {
        let dir = std::env::temp_dir().join(format!("league_warm_test_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(dir.join("sub")).unwrap();
        for (i, size) in [5_000usize, 70_000, 12].into_iter().enumerate() {
            std::fs::write(dir.join(format!("clip{i}.mp3")), vec![7u8; size]).unwrap();
        }
        std::fs::write(dir.join("sub").join("not_read.mp3"), b"x").unwrap();
        assert_eq!(warm(&dir), (3, 75_012));
        assert_eq!(warm(&dir.join("missing")), (0, 0));
        std::fs::remove_dir_all(&dir).unwrap();
    }

    #[test]
    fn a_file_on_the_disk_has_a_cluster_and_a_missing_one_goes_last() {
        let p = std::env::temp_dir().join(format!("league_warm_lcn_{}.bin", std::process::id()));
        std::fs::write(&p, vec![1u8; 64 * 1024]).unwrap();
        assert_ne!(first_cluster(&p), u64::MAX);
        std::fs::remove_file(&p).unwrap();
        assert_eq!(first_cluster(&p), u64::MAX);
    }
}
