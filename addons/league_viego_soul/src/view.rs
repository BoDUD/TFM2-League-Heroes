//! 整身附身：附身时佛耶戈整个身体（站、跑、出招、挨打）画成被附身的那个英雄。只在游戏 0.6.3（Windows）上生效，别的版本
//! 什么都不做，附身就只有数据里的亡魂黑雾。
//!
//! 和凯隐附加包（league_kayn_form/src/view.rs）挂在同一个地方：游戏的显示世界每帧调用显示处理表里的更新函数
//! （rva 0x2808e30），函数指针在 .rdata 的槽 rva 0x3c31358 里。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用
//! 槽里原来的函数（原版的，或先装好的凯隐附加包 / 变身前置，一个接一个），再走一遍显示世界的实体表（+0x138 的哈希表，每格
//! 0x1d0 字节，值从 +8 开始）：值 +0x38 是英雄 id（String：+0x40 指针、+0x48 长度），**+0x50 / +0x58 / +0x60 是身体用哪套
//! 图的资源名**（String），+0x68 / +0x70 / +0x78 是正在播的动画名，+0xb8 / +0xc0 是 buff 列表（每个 0x28 字节，名字指针 +8、
//! 长度 +0x10，原生代码挂的 buff 也在）。
//!
//! 名字是 `league_viego`、身上有 `league_viego_soul:<英雄 id>` 的实体：把那个英雄的实体的资源名抄到佛耶戈的 +0x50（新字符串
//! 用游戏同一个堆分配，旧的照游戏的做法释放），正在播的动画名对不上那个英雄的图（src/souls.rs 的动作表）就换成他有的那个
//! （skill2 → skill → attack → idle），佛耶戈自己才有的动作（附身、大招）画成 idle。没有附身 buff 就把记下的原资源名写回去。
//! 查不到动作表的英雄（别的 mod）不换外形：名字对不上图会让游戏 panic（「animation info not found」）。
//! 资源名这个字段是从工坊 Rin 的佛耶戈（3812835762，viego.dll 的显示函数）读出来的；第一次进游戏要看日志确认。

use std::ffi::c_void;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Mutex, Once};

use super::{souls, wlog, HERO, LOOK};

const FN_RVA: usize = 0x2808e30;
const SLOT_RVA: usize = 0x3c31358;
/// push r15; push r14; push r13; push r12; push rsi; push rdi; push rbp; push rbx; sub rsp, 0x88; movdqa [rsp+..], xmm7
const FN_HEAD: [u8; 24] = [0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x55, 0x53, 0x48, 0x81, 0xec, 0x88,
    0x00, 0x00, 0x00, 0x66, 0x0f, 0x7f, 0x7c, 0x24];
const TABLE: usize = 0x138;
const TABLE_MASK: usize = 0x140;
const TABLE_ITEMS: usize = 0x150;
const ELEM: usize = 0x1d0;
const VALUE: usize = 8;
const NAME_PTR: usize = 0x40;
const NAME_LEN_AT: usize = 0x48;
/// Strings {cap, ptr, len}: the body's resource name at +0x50 / +0x58 / +0x60, the playing animation at +0x68 / +0x70 / +0x78.
const RES_CAP: usize = 0x50;
const ANIM_CAP: usize = 0x68;
const BUFFS_PTR: usize = 0xb8;
const BUFFS_LEN: usize = 0xc0;
const BUFF_SIZE: usize = 0x28;

/// 被附身英雄的图里没有正在播的这个名字时换成哪个（按顺序找第一个他有的）。
pub fn anim_for(cur: &str, tags: &[&str]) -> Option<&'static str> {
    if tags.contains(&cur) {
        return None;
    }
    let chain: &[&'static str] = match cur {
        "skill2" => &["skill2", "skill", "attack", "idle"],
        "skill" => &["skill", "attack", "idle"],
        "attack" => &["attack", "idle"],
        "run" => &["run", "idle"],
        "hit" => &["hit", "idle"],
        "dead" => &["dead", "hit", "idle"],
        _ => &["idle"],
    };
    chain.iter().copied().find(|t| tags.contains(t))
}

/// 身上的 buff → 附身的英雄 id（没有附身就是 None）。
pub fn victim<'a>(names: impl Iterator<Item = &'a [u8]>) -> Option<&'a [u8]> {
    names.into_iter().find_map(|n| n.strip_prefix(LOOK.as_bytes()).filter(|v| !v.is_empty()))
}

/// 附身英雄的动作表（src/souls.rs）。
pub fn tags_of(id: &[u8]) -> Option<&'static [&'static str]> {
    let id = std::str::from_utf8(id).ok()?;
    souls::SOULS.binary_search_by(|s| s.0.cmp(id)).ok().map(|i| souls::SOULS[i].2)
}

/// (显示世界, 实体号) → 佛耶戈原来的资源名。
#[derive(Default)]
pub struct Originals {
    seen: Vec<(usize, u64, Vec<u8>)>,
}

impl Originals {
    pub fn get_or_keep(&mut self, world: usize, key: u64, cur: &[u8]) -> Vec<u8> {
        if let Some(e) = self.seen.iter().find(|e| e.0 == world && e.1 == key) {
            return e.2.clone();
        }
        self.seen.push((world, key, cur.to_vec()));
        if self.seen.len() > 64 {
            self.seen.remove(0);
        }
        cur.to_vec()
    }
}

struct Stats {
    calls: u64,
    viegos: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    looks: Vec<(usize, u64, Vec<u8>)>,
    /// the buff names last logged per Viego, and how many such lines were written (at most BUFF_LINES a run)
    buffsets: Vec<(usize, u64, Vec<u8>)>,
    buff_lines: usize,
}

/// Lines listing a Viego's display buffs when they change (the check that the look buff reaches the display world).
const BUFF_LINES: usize = 60;

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, viegos: 0, writes: 0, last: None, looks: Vec::new(),
    buffsets: Vec::new(), buff_lines: 0 });
static ORIG: Mutex<Originals> = Mutex::new(Originals { seen: Vec::new() });
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

unsafe extern "system" fn update(this: usize, a2: usize, world: usize, dt: f32) {
    let prev = PREV.load(Ordering::Acquire);
    if prev != 0 {
        let f: Update = std::mem::transmute(prev);
        f(this, a2, world, dt);
    }
    let _ = std::panic::catch_unwind(|| unsafe { dress_viego(world) });
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// A String {cap, ptr, len} at `at` as bytes (None when it does not look like one).
unsafe fn string_at<'a>(at: usize, max: usize) -> Option<&'a [u8]> {
    let (cap, ptr, len) = (q(at), q(at + 8), q(at + 16));
    (len >= 1 && len <= max && cap >= len && plausible(ptr)).then(|| std::slice::from_raw_parts(ptr as *const u8, len))
}

/// Replace the String {cap, ptr, len} at `at` with `want` (the game's heap, the old buffer freed like the game does).
unsafe fn put_string(at: usize, want: &[u8]) -> bool {
    let (cap, ptr) = (q(at), q(at + 8));
    let heap = GetProcessHeap();
    let fresh = HeapAlloc(heap, 0, want.len().max(1));
    if fresh.is_null() {
        return false;
    }
    std::ptr::copy_nonoverlapping(want.as_ptr(), fresh, want.len());
    std::ptr::write_unaligned(at as *mut usize, want.len());
    std::ptr::write_unaligned((at + 8) as *mut usize, fresh as usize);
    std::ptr::write_unaligned((at + 16) as *mut usize, want.len());
    if cap > 0 && plausible(ptr) {
        HeapFree(heap, 0, ptr as *mut u8);
    }
    true
}

unsafe fn dress_viego(world: usize) {
    if !plausible(world) {
        return;
    }
    let ctrl = q(world + TABLE);
    let mask = q(world + TABLE_MASK);
    let items = q(world + TABLE_ITEMS);
    if items == 0 || !plausible(ctrl) || mask >= 1 << 16 || (mask + 1) & mask != 0 || items > mask + 1 {
        return;
    }
    let (Ok(mut orig), Ok(mut st)) = (ORIG.try_lock(), STATS.try_lock()) else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.viegos > 0 {
            wlog(format!("display handler: {} calls, Viego seen {} times, {} strings swapped in 10 s",
                st.calls, st.viegos, st.writes));
        }
        st.last = Some(now);
        st.calls = 0;
        st.viegos = 0;
        st.writes = 0;
    }
    // every record: (key, value address, champion id)
    let mut recs: Vec<(u64, usize, &[u8])> = Vec::new();
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue;
        }
        let elem = ctrl - (i + 1) * ELEM;
        let v = elem + VALUE;
        let n = q(v + NAME_LEN_AT);
        let p = q(v + NAME_PTR);
        if !(1..=64).contains(&n) || !plausible(p) {
            continue;
        }
        recs.push((q(elem) as u64, v, std::slice::from_raw_parts(p as *const u8, n)));
    }
    for &(key, v, name) in &recs {
        if name != HERO.as_bytes() {
            continue;
        }
        st.viegos += 1;
        let Some(res) = string_at(v + RES_CAP, 64) else { continue };
        let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
        let buffs: Vec<&[u8]> = if plausible(bp) && bn <= 256 {
            (0..bn)
                .filter_map(|k| {
                    let b = bp + k * BUFF_SIZE;
                    let (p, n) = (q(b + 8), q(b + 0x10));
                    (plausible(p) && n <= 64).then(|| std::slice::from_raw_parts(p as *const u8, n))
                })
                .collect()
        } else {
            Vec::new()
        };
        // the soul's buffs are logged whenever they change (the first BUFF_LINES other changes too)
        let soulish = buffs.iter().any(|b| b.starts_with(b"league_viego_soul") || b.starts_with(b"league_viego_p_"));
        if st.buff_lines < BUFF_LINES || soulish {
            let joined = buffs.join(&b", "[..]);
            if !st.buffsets.iter().any(|b| b.0 == world && b.1 == key && b.2 == joined) {
                st.buffsets.retain(|b| !(b.0 == world && b.1 == key));
                st.buffsets.push((world, key, joined.clone()));
                st.buff_lines += 1;
                wlog(format!("world {world:#x} Viego #{key} display buffs: [{}]", String::from_utf8_lossy(&joined)));
            }
        }
        let original = orig.get_or_keep(world, key, res);
        let soul = victim(buffs.iter().copied());
        // the victim's body: its display entity's resource name while it is still in the display world; a soul is
        // taken from a corpse the game may already have dropped, so else the champion id itself (every display entity
        // seen - Viego's own "league_viego" - carries its id as the resource name)
        let target: Option<(Vec<u8>, &'static [&'static str])> = soul.and_then(|id| {
            let tags = tags_of(id)?;
            let live = recs.iter().find(|r| r.2 == id && r.0 != key).and_then(|rec| string_at(rec.1 + RES_CAP, 64));
            Some((live.unwrap_or(id).to_vec(), tags))
        });
        let want_res: &[u8] = match &target {
            Some((r, _)) => r,
            None => &original,
        };
        let look = (world, key, want_res.to_vec());
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            wlog(format!("world {world:#x} Viego #{key}: drawn as {} (soul {})", String::from_utf8_lossy(want_res),
                soul.map_or("none".into(), |s| String::from_utf8_lossy(s).into_owned())));
        }
        if res != want_res && put_string(v + RES_CAP, want_res) {
            st.writes += 1;
        }
        if let Some((_, tags)) = target {
            let Some(cur) = string_at(v + ANIM_CAP, 32) else { continue };
            let Ok(cur) = std::str::from_utf8(cur) else { continue };
            if let Some(want) = anim_for(cur, tags) {
                if put_string(v + ANIM_CAP, want.as_bytes()) {
                    st.writes += 1;
                }
            }
        }
    }
}

fn install() -> Result<(usize, usize), String> {
    let module = unsafe { GetModuleHandleW(std::ptr::null()) };
    if module == 0 {
        return Err("no module handle".into());
    }
    let func = module + FN_RVA;
    if read(func, FN_HEAD.len()).as_deref() != Some(&FN_HEAD[..]) {
        return Err("not game 0.6.3 (the display handler differs)".into());
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
                "whole-body possession on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if prev == module + FN_RVA { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("whole-body possession off ({e}): the possession shows only the data's mist")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn names_the_victim_lacks_fall_back() {
        let t = &["idle", "run", "attack", "skill", "hit", "dead"];
        assert_eq!(anim_for("idle", t), None);
        assert_eq!(anim_for("skill2", t), Some("skill"));
        assert_eq!(anim_for("possess", t), Some("idle"));
        assert_eq!(anim_for("ult", t), Some("idle"));
        let u = &["idle", "run", "attack", "hit", "dead"];
        assert_eq!(anim_for("skill2", u), Some("attack"));
        assert_eq!(anim_for("skill", u), Some("attack"));
    }

    #[test]
    fn the_look_buff_names_the_victim() {
        let b = |v: &[&'static str]| victim(v.iter().map(|s| s.as_bytes())).map(|s| s.to_vec());
        assert_eq!(b(&["league_viego_p_on", "league_viego_soul:league_jinx"]), Some(b"league_jinx".to_vec()));
        assert_eq!(b(&["league_viego_soul_range"]), None);
        assert_eq!(b(&["league_viego_soul:"]), None);
    }

    #[test]
    fn the_original_is_kept_per_viego() {
        let mut o = Originals::default();
        assert_eq!(o.get_or_keep(1, 7, b"league_viego"), b"league_viego".to_vec());
        assert_eq!(o.get_or_keep(1, 7, b"league_jinx"), b"league_viego".to_vec());
        assert_eq!(o.get_or_keep(2, 7, b"x"), b"x".to_vec());
    }

    #[test]
    fn known_heroes_have_their_tags() {
        let t = tags_of(b"league_garen").expect("garen in the table");
        assert!(t.contains(&"idle") && t.contains(&"run"));
        assert!(tags_of(b"someone_elses_hero").is_none());
    }
}
