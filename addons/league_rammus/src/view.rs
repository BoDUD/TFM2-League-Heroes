//! 整身换形态：动力冲刺滚着的时候（副本的 Q 给他挂 `league_rammus_q_ball`）站着、走着、挨打都是滚动的刺球（图里的 `b_idle` /
//! `b_run` / `b_hit`），尖刺防御开着的时候（`league_rammus_w_on`）是蜷着的防御姿势（`c_idle` / `c_run` / `c_hit`）。主包只能用
//! `CasterAnimation` 换出招的动作，游戏按名字自动播的 idle / run / hit 数据换不了。只在游戏 0.6.4（Windows）上生效，别的版本什么都
//! 不做：滚球照样加速、撞人，画面是主包那样站着的他。
//!
//! 照 league_reksai 的 view.rs（雷克塞的遁地整身，源自 league_rell / league_jayce / league_nidalee / league_kayn_form）：游戏的显示世界
//! 每帧调用显示处理表里的更新函数（rva 0x23312a0），函数指针在 .rdata 的槽 rva 0x3c82db8（凯隐、佛耶戈、奈德丽、杰斯、伊莉丝、厄斐
//! 琉斯、芮尔、雷克塞附加包也挂在这里，一个接一个调用）。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用槽里原来的函数，
//! 再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始：+0x40 名字，+0x68 / +0x70 / +0x78 正在播的动画名，
//! +0xb8 / +0xc0 buff 列表）。名字是 `league_rammus` 的实体身上有滚球 / 防御 buff 时，正在播的 idle / run / hit 换成 `b_*` / `c_*`
//! （滚球优先；新名字用游戏同一个堆分配，旧的照游戏的做法释放）。高清帧不用另管：league.dll 把登记英雄动画表里每个动作（b_idle 也
//! 在内）就地换成它的 hd_ 帧（addons/league_main/src/lookup.rs）。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Mutex, Once};

use super::{wlog, BALL, CURL};

/// 显示处理表里的更新函数（0.6.4）和存它的槽。
const FN_RVA: usize = 0x23312a0;
const SLOT_RVA: usize = 0x3c82db8;
/// push r15; push r14; push r13; push r12; push rsi; push rdi; push rbp; push rbx; sub rsp, 0x88; movdqa [rsp+..], xmm7
const FN_HEAD: [u8; 24] = [0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x55, 0x53, 0x48, 0x81, 0xec, 0x88,
    0x00, 0x00, 0x00, 0x66, 0x0f, 0x7f, 0x7c, 0x24];
/// 显示世界：实体表（hashbrown：控制字节指针、掩码、元素数）。
const TABLE: usize = 0x138;
const TABLE_MASK: usize = 0x140;
const TABLE_ITEMS: usize = 0x150;
const ELEM: usize = 0x1d0;
/// 值在元素里的位置（键是 8 字节的实体号）和值里的字段。
const VALUE: usize = 8;
const NAME_PTR: usize = 0x40;
const NAME_LEN_AT: usize = 0x48;
const ANIM_CAP: usize = 0x68;
const ANIM_PTR: usize = 0x70;
const ANIM_LEN: usize = 0x78;
const BUFFS_PTR: usize = 0xb8;
const BUFFS_LEN: usize = 0xc0;
const BUFF_SIZE: usize = 0x28;

/// 拉莫斯在画面实体里的名字。
pub const NAME: &[u8] = b"league_rammus";

/// 游戏按名字自动播、两种形态各有一套的动作：待机、走、挨打。普攻、技能、阵亡不换（出招时他已经撞上 / 收起了球）。
pub const FORM_TAGS: [&str; 3] = ["idle", "run", "hit"];
const PREFIXES: [&str; 2] = ["b_", "c_"];

/// 形态：滚球（`b_`）、防御（`c_`）或都不是。
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Form {
    Stand,
    Ball,
    Curl,
}

/// 正在播的动画名 + 形态 → 该播的名字（不用换就是 None）。形态结束后把本包换上去的 `b_idle` 等换回来。
pub fn anim_for(cur: &str, form: Form) -> Option<String> {
    let base = PREFIXES.iter().find_map(|p| cur.strip_prefix(p)).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = match form {
        Form::Stand => base.to_string(),
        Form::Ball => format!("b_{base}"),
        Form::Curl => format!("c_{base}"),
    };
    (want != cur).then_some(want)
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的形态：变了才记一行 FORM。
    looks: Vec<(usize, u64, Form)>,
}

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, seen: 0, writes: 0, last: None, looks: Vec::new() });
static PREV: AtomicUsize = AtomicUsize::new(0);
static HOOK: Once = Once::new();

#[link(name = "kernel32")]
extern "system" {
    fn ReadProcessMemory(h: isize, base: *const c_void, buf: *mut c_void, size: usize, read: *mut usize) -> i32;
    fn GetCurrentProcess() -> isize;
    fn GetModuleHandleW(name: *const u16) -> usize;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
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

type Update = unsafe extern "system" fn(usize, usize, usize, f32);

/// 槽里换上的函数：先做原来的事，再给拉莫斯换动作。
unsafe extern "system" fn update(this: usize, a2: usize, world: usize, dt: f32) {
    let prev = PREV.load(Ordering::Acquire);
    if prev != 0 {
        let f: Update = std::mem::transmute(prev);
        f(this, a2, world, dt);
    }
    let _ = std::panic::catch_unwind(|| unsafe { dress(world) });
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// 显示世界里每个拉莫斯：按身上的滚球 / 防御 buff 换正在播的动画名。
unsafe fn dress(world: usize) {
    if !plausible(world) {
        return;
    }
    let ctrl = q(world + TABLE);
    let mask = q(world + TABLE_MASK);
    let items = q(world + TABLE_ITEMS);
    if items == 0 || !plausible(ctrl) || mask >= 1 << 16 || (mask + 1) & mask != 0 || items > mask + 1 {
        return;
    }
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Rammus seen {} times, {} animation names swapped in 10 s",
                st.calls, st.seen, st.writes));
        }
        st.last = Some(now);
        st.calls = 0;
        st.seen = 0;
        st.writes = 0;
    }
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue; // empty or deleted
        }
        let elem = ctrl - (i + 1) * ELEM;
        let v = elem + VALUE;
        if q(v + NAME_LEN_AT) != NAME.len() {
            continue;
        }
        let ptr = q(v + NAME_PTR);
        if !plausible(ptr) || std::slice::from_raw_parts(ptr as *const u8, NAME.len()) != NAME {
            continue;
        }
        let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
        let has = |name: &str| plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == name.len() && std::slice::from_raw_parts(p as *const u8, n) == name.as_bytes()
        });
        let form = if has(BALL) { Form::Ball } else if has(CURL) { Form::Curl } else { Form::Stand };
        st.seen += 1;
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let look = (world, key, form);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            if let Some(k) = super::counted("form_view") {
                wlog(format!("FORM display world {world:#x} Rammus #{key}: {} (playing {cur}) #{k}", match form {
                    Form::Ball => "the BALL - idle/run/hit drawn as b_*",
                    Form::Curl => "CURLED - idle/run/hit drawn as c_*",
                    Form::Stand => "standing",
                }));
            }
        }
        let Some(want) = anim_for(cur, form) else { continue };
        let heap = GetProcessHeap();
        let fresh = HeapAlloc(heap, 0, want.len());
        if fresh.is_null() {
            continue;
        }
        std::ptr::copy_nonoverlapping(want.as_ptr(), fresh, want.len());
        std::ptr::write_unaligned((v + ANIM_CAP) as *mut usize, want.len());
        std::ptr::write_unaligned((v + ANIM_PTR) as *mut usize, fresh as usize);
        std::ptr::write_unaligned((v + ANIM_LEN) as *mut usize, want.len());
        if acap > 0 {
            HeapFree(heap, 0, aptr as *mut u8);
        }
        st.writes += 1;
    }
}

fn install() -> Result<(usize, usize), String> {
    let module = unsafe { GetModuleHandleW(std::ptr::null()) };
    if module == 0 {
        return Err("no module handle".into());
    }
    let func = module + FN_RVA;
    if read(func, FN_HEAD.len()).as_deref() != Some(&FN_HEAD[..]) {
        return Err("not game 0.6.4 (the display handler differs)".into());
    }
    let slot = module + SLOT_RVA;
    let cur = read(slot, 8).map(|b| usize::from_le_bytes(b.try_into().unwrap())).ok_or("the slot is unreadable")?;
    if !plausible(cur) {
        return Err(format!("the slot holds {cur:#x}"));
    }
    PREV.store(cur, Ordering::Release);
    let mut old = 0u32;
    if unsafe { VirtualProtect(slot as *mut c_void, 8, 0x04, &mut old) } == 0 {
        return Err("VirtualProtect failed".into());
    }
    unsafe { std::ptr::write_volatile(slot as *mut usize, update as Update as usize) };
    let mut tmp = 0u32;
    unsafe { VirtualProtect(slot as *mut c_void, 8, old, &mut tmp) };
    Ok((slot, cur))
}

/// 加载时换槽（一个进程只换一次）。
pub fn install_once() {
    HOOK.call_once(|| {
        let module = unsafe { GetModuleHandleW(std::ptr::null()) };
        match install() {
            Ok((slot, prev)) => wlog(format!(
                "FORM ball / curl bodies on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if prev == module + FN_RVA { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM ball / curl bodies off ({e}): he stands on screen while rolling (the main pack's look)")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_form() {
        assert_eq!(anim_for("idle", Form::Ball).as_deref(), Some("b_idle"));
        assert_eq!(anim_for("run", Form::Ball).as_deref(), Some("b_run"));
        assert_eq!(anim_for("hit", Form::Curl).as_deref(), Some("c_hit"));
        assert_eq!(anim_for("c_run", Form::Ball).as_deref(), Some("b_run")); // the curl ends in a roll
        assert_eq!(anim_for("b_run", Form::Stand).as_deref(), Some("run")); // the ball is over
        assert_eq!(anim_for("c_idle", Form::Stand).as_deref(), Some("idle"));
        assert_eq!(anim_for("attack", Form::Ball), None);
        assert_eq!(anim_for("skill_roll", Form::Ball), None); // the main pack's own roll
        assert_eq!(anim_for("idle", Form::Stand), None);
    }

    #[test]
    fn every_swapped_tag_is_in_his_sheet() {
        let fanim = include_str!("../../../league/champions/league_rammus#anim.fanim");
        for t in FORM_TAGS {
            for p in ["", "b_", "c_", "hd_", "hd_b_", "hd_c_"] {
                let name = format!("{p}{t}");
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_rammus#anim.fanim");
            }
        }
    }
}
