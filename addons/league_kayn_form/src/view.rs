//! 完整变身：变身后凯隐站着、跑着、挨打、阵亡也是形态的样子（主包只能换出招的动作，游戏按名字自动播的
//! idle / run / hit / dead 数据换不了）。只在游戏 0.6.3（Windows）上生效，别的版本什么都不做，退回半变身。
//!
//! 游戏每一帧画单位时，用画面实体里的名字现拼精灵：`asset/base/aseprite_resources/champions/{名字}#sheet` / `#anim`
//! （0.6.3 小地图 rva 0x231f310 里看得到这一步），再经过资源重定向表找到 mod 的图。凯隐的名字缓冲区一局里不变，
//! 把 `league_kayn` 的最后一个字母改成 `d` / `s`，画出来的就是 `league_kayd` / `league_kays`：本包的
//! `mod.override_info` 把这两个名字的精灵送到主包的 `league_kayn_darkin` / `league_kayn_shadow`（凯隐全部的动作，
//! idle / run / hit / dead 换成形态的，tools/art/rig_kayn_forms.py）；在墙里是 `w` / `r` / `h`（暗影剪影）。
//!
//! 怎么找到那份名字（0.6.3，2026-10-08）：游戏的显示世界每帧调用一张显示处理表里的更新函数（rva 0x2808e30，原版
//! 恶魔变身 run → archfiend_run 用的就是它；函数指针在 .rdata 的槽 rva 0x3c31358 里，群里的变身前置
//! tfm2_transform_core 也挂在这里）。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用槽里原来的
//! 函数（原版的，或者先装好的变身前置），再看显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始）：
//! 值 +0x38 是名字（String：+0x40 指针、+0x48 长度），+0xb8 / +0xc0 是 buff 列表（每个 0x28 字节，名字指针 +8、
//! 长度 +0x10）。名字是 `league_kay?` 的实体按身上的 buff 选字母：形态 buff `league_kayn_form_d` / `_s`，在墙里的
//! 暗影雾 `league_kayn_in_wall*`（被动挂的）。画面实体的 buff 就是屏幕上这一刻的，不用再对比赛时钟；两个凯隐各管各的。
//! 形态是永久的：阵亡时 buff 清掉，那具尸体仍按记下的形态画（实体换局才清）。
//! 开发过程：0.6.2 侦察 mod v1–v8（2026-10-06）；0.6.3 探针 v9–v11 + 静态分析（2026-10-08，C:\tfm2\scratch\view_probe*）。

use std::ffi::c_void;
use std::sync::atomic::{AtomicU8, AtomicUsize, Ordering};
use std::sync::{Mutex, Once};

use super::{wlog, FORM_D, FORM_S};

/// 显示处理表里的更新函数（0.6.3）和存它的槽。
const FN_RVA: usize = 0x2808e30;
const SLOT_RVA: usize = 0x3c31358;
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
const BUFFS_PTR: usize = 0xb8;
const BUFFS_LEN: usize = 0xc0;
const BUFF_SIZE: usize = 0x28;
/// 被动在墙里挂的暗影雾（本体 / 暗裔 / 影流）。
const IN_WALL: &[u8] = b"league_kayn_in_wall";

/// 凯隐在显示数据里的名字（长度 11），最后一个字母：n 本体、d 暗裔、s 影流。
pub const STEM: &[u8] = b"league_kay";
pub const NAME_LEN: usize = 11;

/// 名字的最后一个字母：本体 n、暗裔 d、影流 s；在墙格里（掠影步穿墙）是它们的暗影剪影 w、r、h（英雄联盟里凯隐
/// 钻进地形时只剩一团暗影；用户：「穿墙的效果要模仿LOL里面」），各自送到 `league_kayn{,_darkin,_shadow}_wall`。
pub const LETTERS: [u8; 6] = [b'n', b'd', b's', b'w', b'r', b'h'];

/// 名字是 `league_kay` + 上面的一个字母时，那个字母。
pub fn form_letter(name: &[u8]) -> Option<u8> {
    (name.len() == NAME_LEN && name.starts_with(STEM) && LETTERS.contains(&name[NAME_LEN - 1]))
        .then(|| name[NAME_LEN - 1])
}

/// 形态和在不在墙里 → 名字的最后一个字母。
pub fn letter_for(darkin: bool, shadow: bool, in_wall: bool) -> u8 {
    match (darkin, shadow, in_wall) {
        (true, _, false) => b'd',
        (true, _, true) => b'r',
        (false, true, false) => b's',
        (false, true, true) => b'h',
        (false, false, false) => b'n',
        (false, false, true) => b'w',
    }
}

/// 一个画面实体身上的 buff 名 → (暗裔, 影流, 在墙里)。
pub fn read_buffs<'a>(names: impl Iterator<Item = &'a [u8]>) -> (bool, bool, bool) {
    let (mut d, mut s, mut w) = (false, false, false);
    for n in names {
        d |= n == FORM_D.as_bytes();
        s |= n == FORM_S.as_bytes();
        w |= n.starts_with(IN_WALL);
    }
    (d, s, w)
}

/// 记下的形态：(显示世界, 实体号) → 暗裔 / 影流（阵亡时 buff 清掉，尸体仍是那个形态）。
#[derive(Default)]
pub struct Forms {
    world: usize,
    seen: Vec<(u64, bool, bool)>,
}

impl Forms {
    /// 这一帧的 buff → 要画的 (暗裔, 影流)：有形态 buff 就记下，没有就用记下的。
    pub fn form(&mut self, world: usize, key: u64, darkin: bool, shadow: bool) -> (bool, bool) {
        if world != self.world {
            self.world = world;
            self.seen.clear();
        }
        match self.seen.iter_mut().find(|e| e.0 == key) {
            Some(e) if darkin || shadow => {
                e.1 = darkin;
                e.2 = shadow;
                (darkin, shadow)
            }
            Some(e) => (e.1, e.2),
            None if darkin || shadow => {
                self.seen.push((key, darkin, shadow));
                if self.seen.len() > 64 {
                    self.seen.remove(0);
                }
                (darkin, shadow)
            }
            None => (false, false),
        }
    }
}

static FORMS: Mutex<Forms> = Mutex::new(Forms { world: 0, seen: Vec::new() });
static PREV: AtomicUsize = AtomicUsize::new(0);
static HOOK: Once = Once::new();
static HOOKED: AtomicU8 = AtomicU8::new(0);
/// 最近一次写下的字母（换了才记日志）。
static SHOWN: AtomicU8 = AtomicU8::new(0);

#[link(name = "kernel32")]
extern "system" {
    fn ReadProcessMemory(h: isize, base: *const c_void, buf: *mut c_void, size: usize, read: *mut usize) -> i32;
    fn GetCurrentProcess() -> isize;
    fn GetModuleHandleW(name: *const u16) -> usize;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
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

/// 槽里换上的函数：先做原来的事，再给凯隐选样子。
unsafe extern "system" fn update(this: usize, a2: usize, world: usize, dt: f32) {
    let prev = PREV.load(Ordering::Acquire);
    if prev != 0 {
        let f: Update = std::mem::transmute(prev);
        f(this, a2, world, dt);
    }
    let _ = std::panic::catch_unwind(|| unsafe { dress_kayn(world) });
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// 显示世界里每个名字是 `league_kay?` 的实体：按身上的 buff 改名字的最后一个字母。
unsafe fn dress_kayn(world: usize) {
    if !plausible(world) {
        return;
    }
    let ctrl = q(world + TABLE);
    let mask = q(world + TABLE_MASK);
    let items = q(world + TABLE_ITEMS);
    if items == 0 || !plausible(ctrl) || mask >= 1 << 16 || (mask + 1) & mask != 0 || items > mask + 1 {
        return;
    }
    let mut forms = match FORMS.try_lock() {
        Ok(f) => f,
        Err(_) => return,
    };
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue; // empty or deleted
        }
        let elem = ctrl - (i + 1) * ELEM;
        let v = elem + VALUE;
        if q(v + NAME_LEN_AT) != NAME_LEN {
            continue;
        }
        let ptr = q(v + NAME_PTR);
        if !plausible(ptr) {
            continue;
        }
        let name = std::slice::from_raw_parts(ptr as *const u8, NAME_LEN);
        let Some(letter) = form_letter(name) else { continue };
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
        let (d, s, w) = read_buffs(buffs.into_iter());
        let (d, s) = forms.form(world, q(elem) as u64, d, s);
        let want = letter_for(d, s, w);
        if letter != want {
            *(ptr as *mut u8).add(NAME_LEN - 1) = want;
            if SHOWN.swap(want, Ordering::Relaxed) != want {
                wlog(format!("{ptr:#x} drawn as league_kay{} ({})", want as char, match want {
                    b'd' => "Darkin",
                    b's' => "Shadow Assassin",
                    b'n' => "Kayn",
                    _ => "in the wall",
                }));
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
            Ok((slot, prev)) => {
                HOOKED.store(1, Ordering::Relaxed);
                wlog(format!("full transform on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                    if prev == module + FN_RVA { "the game's own handler".to_string() } else { "another mod's handler (chained)".to_string() }));
            }
            Err(e) => wlog(format!("full transform off ({e}): Kayn keeps the data pack's half transform")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn only_kayns_names_are_touched() {
        assert_eq!(form_letter(b"league_kayn"), Some(b'n'));
        assert_eq!(form_letter(b"league_kayr"), Some(b'r'));
        assert_eq!(form_letter(b"league_kayd"), Some(b'd'));
        assert_eq!(form_letter(b"league_kays"), Some(b's'));
        assert_eq!(form_letter(b"league_kayle"), None);
        assert_eq!(form_letter(b"league_kayx"), None);
        assert_eq!(form_letter(b"league_kay"), None);
    }

    #[test]
    fn the_buffs_pick_the_letter() {
        let b = |v: &[&'static str]| read_buffs(v.iter().map(|s| s.as_bytes()));
        assert_eq!(b(&["league_kayn_form_d", "x"]), (true, false, false));
        assert_eq!(b(&["league_kayn_form_s", "league_kayn_in_wall_s"]), (false, true, true));
        assert_eq!(b(&["league_kayn_in_wall"]), (false, false, true));
        assert_eq!(letter_for(true, false, false), b'd');
        assert_eq!(letter_for(false, true, false), b's');
        assert_eq!(letter_for(false, false, false), b'n');
        assert_eq!(letter_for(true, false, true), b'r');
        assert_eq!(letter_for(false, true, true), b'h');
        assert_eq!(letter_for(false, false, true), b'w');
    }

    #[test]
    fn the_form_outlives_its_buff() {
        let mut f = Forms::default();
        assert_eq!(f.form(1, 7, false, false), (false, false)); // not formed yet
        assert_eq!(f.form(1, 7, true, false), (true, false)); // transformed
        assert_eq!(f.form(1, 7, false, false), (true, false)); // dead: buffs gone, still Darkin
        assert_eq!(f.form(1, 8, false, false), (false, false)); // another Kayn
        assert_eq!(f.form(2, 7, false, false), (false, false)); // a new display world
    }
}
