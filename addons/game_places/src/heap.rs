//! The heap the display hooks put their animation names on: the game frees an entity's old name with its own
//! allocator (Rust's System allocator: the process heap on Windows), so a name swapped in must come from the same heap.
//! Every add-on's view.rs uses these instead of declaring kernel32 itself (2026-10-31, the Mac build: 「想个办法主包和
//! 附加包能兼容mac吧」) - a `#[link(name = "kernel32")]` in any add-on stops league_addons.dylib from linking.
//! Off Windows they are malloc / free (the System allocator there); nothing calls them, because [`crate::hook::add`]
//! never swaps the display slot off Windows.

#[cfg(windows)]
#[link(name = "kernel32")]
extern "system" {
    pub fn GetProcessHeap() -> isize;
    pub fn HeapAlloc(heap: isize, flags: u32, bytes: usize) -> *mut u8;
    pub fn HeapFree(heap: isize, flags: u32, mem: *mut u8) -> i32;
}

#[cfg(not(windows))]
extern "C" {
    fn malloc(bytes: usize) -> *mut u8;
    fn free(mem: *mut u8);
}

/// # Safety
/// Same contract as kernel32's GetProcessHeap.
#[cfg(not(windows))]
#[allow(non_snake_case)]
pub unsafe fn GetProcessHeap() -> isize {
    1
}

/// # Safety
/// Same contract as kernel32's HeapAlloc (`flags` must be 0).
#[cfg(not(windows))]
#[allow(non_snake_case)]
pub unsafe fn HeapAlloc(_heap: isize, _flags: u32, bytes: usize) -> *mut u8 {
    malloc(bytes)
}

/// # Safety
/// `mem` came from [`HeapAlloc`] or the game's allocator and is not used again.
#[cfg(not(windows))]
#[allow(non_snake_case)]
pub unsafe fn HeapFree(_heap: isize, _flags: u32, mem: *mut u8) -> i32 {
    free(mem);
    1
}
