//! 小菊落地那几帧的兜底（0.3.0）：附加包生成小菊单位时给她挂动画定身 `drop`（她图里那 5 帧，daisy.rs 的 `start_drop`）和
//! 标记 `D_DROPPING`。引擎要是不给召唤物播定身里的动作名，这里接着：显示世界里名字是 `league_ivern_daisy`、身上有那个标记的
//! 单位，正在播的不是 `drop`（也不是倒下）就换成 `drop`——新名字用游戏同一个堆（GetProcessHeap）分配，旧的照游戏的做法释放，
//! 和奈德丽的 view.rs 一样。每个小菊第一次看到时记一行：引擎自己播的是什么（`drop` 就是定身管用，这里什么都不用做）。
//!
//! 挂在 game_places 的显示钩子上（合集晚挂：所有 mod 加载完的第一帧才换槽）。

use std::sync::{Mutex, Once};

use game_places::hook::{Ent, ANIM_CAP, ANIM_LEN, ANIM_PTR, BUFFS_LEN, BUFFS_PTR, BUFF_SIZE, NAME_LEN_AT, NAME_PTR, VALUE};

use super::daisy::{D_DROPPING, D_DROP_TAG, D_NAME};
use super::wlog;

/// 看到过的小菊（显示世界, 实体号）：每个记一行。
static SEEN: Mutex<Vec<(usize, u64)>> = Mutex::new(Vec::new());
static HOOK: Once = Once::new();

#[link(name = "kernel32")]
extern "system" {
    fn GetProcessHeap() -> isize;
    fn HeapAlloc(heap: isize, flags: u32, bytes: usize) -> *mut u8;
    fn HeapFree(heap: isize, flags: u32, mem: *mut u8) -> i32;
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// 正在播的动画名该不该换成 `drop`：落地标记还在、播的不是 `drop` 也不是倒下。
pub fn wants_drop(dropping: bool, cur: &str) -> bool {
    dropping && cur != D_DROP_TAG && cur != "dead"
}

/// 显示世界里每个正在落地的小菊：播的不是 `drop` 就换成 `drop`。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut seen) = SEEN.try_lock() else { return };
    for e in ents {
        let v = e.elem + VALUE;
        if q(v + NAME_LEN_AT) != D_NAME.len() {
            continue;
        }
        let np = q(v + NAME_PTR);
        if !plausible(np) || std::slice::from_raw_parts(np as *const u8, D_NAME.len()) != D_NAME.as_bytes() {
            continue;
        }
        let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
        let dropping = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == D_DROPPING.len() && std::slice::from_raw_parts(p as *const u8, n) == D_DROPPING.as_bytes()
        });
        if !dropping {
            continue;
        }
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = (world, q(e.elem) as u64);
        if !seen.contains(&key) {
            seen.push(key);
            if seen.len() > 64 {
                seen.remove(0);
            }
            wlog(format!("DAISY DROP on screen: unit #{} plays '{cur}'{}", key.1,
                         if cur == D_DROP_TAG { " - the engine plays her drop itself" } else { " -> 'drop' (swapped by the display hook)" }));
        }
        if !wants_drop(dropping, cur) {
            continue;
        }
        let heap = GetProcessHeap();
        let fresh = HeapAlloc(heap, 0, D_DROP_TAG.len());
        if fresh.is_null() {
            continue;
        }
        std::ptr::copy_nonoverlapping(D_DROP_TAG.as_ptr(), fresh, D_DROP_TAG.len());
        std::ptr::write_unaligned((v + ANIM_CAP) as *mut usize, D_DROP_TAG.len());
        std::ptr::write_unaligned((v + ANIM_PTR) as *mut usize, fresh as usize);
        std::ptr::write_unaligned((v + ANIM_LEN) as *mut usize, D_DROP_TAG.len());
        if acap > 0 {
            HeapFree(heap, 0, aptr as *mut u8);
        }
    }
}

/// 登记到显示钩子（一个进程一次）。
pub fn install_once() {
    HOOK.call_once(|| match game_places::hook::add("league_ivern", dress, |m: &str| wlog(m)) {
        Ok(p) => wlog(format!("DAISY DROP display hook on: {p}")),
        Err(e) => wlog(format!("DAISY DROP display hook off ({e}): her drop shows only if the engine plays her Animation CC")),
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn only_a_dropping_daisy_is_swapped() {
        assert!(wants_drop(true, "idle"));
        assert!(wants_drop(true, "run"));
        assert!(wants_drop(true, "hit"));
        assert!(!wants_drop(true, "drop")); // the engine plays it already
        assert!(!wants_drop(true, "dead")); // killed in her drop
        assert!(!wants_drop(false, "idle")); // landed
    }
}
