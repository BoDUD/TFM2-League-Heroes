//! 完整变身：变身后凯隐站着、跑着、挨打、阵亡也是形态的样子（主包只能换出招的动作，游戏按名字自动播的
//! idle / run / hit / dead 数据换不了）。只在游戏 0.6.4（Windows）上生效，别的版本什么都不做，退回半变身。
//!
//! 游戏的显示世界每帧调用一张显示处理表里的更新函数（rva 0x23312a0）：原版恶魔就在这里把正在播的动画名 run 换成
//! archfiend_run（两套都在恶魔自己的图里）。函数指针在 .rdata 的槽 rva 0x3c82db8 里（群里的变身前置
//! tfm2_transform_core 也挂在这里）。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用槽里原来的函数（原版的，
//! 或先装好的变身前置），再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始）：
//! 值 +0x38 是名字（String：+0x40 指针、+0x48 长度），+0x68 / +0x70 / +0x78 是正在播的动画名（String），
//! +0xb8 / +0xc0 是 buff 列表（每个 0x28 字节，名字指针 +8、长度 +0x10）。名字是 `league_kayn` 的实体按身上的 buff
//! 换动画名：形态 buff `league_kayn_form_d` / `_s` → `rh_idle` / `sh_idle` ……，墙里的暗影雾 `league_kayn_in_wall*`
//! → `w_run` / `rw_run` / `hw_run` ……（这些都在凯隐自己的图里：tools/art/import_native.py 的 FORM_INTO_BASE /
//! WALL_INTO_BASE）。新名字用游戏同一个堆（GetProcessHeap）分配，旧的照游戏的做法释放。
//! 画面实体的 buff 就是屏幕上这一刻的，不用对比赛时钟；两个凯隐各管各的。形态是永久的：阵亡时 buff 清掉，尸体按
//! 记下的形态画。
//! 2026-10-08 先试过照 0.6.2 改名字的最后一个字母（league_kayd ……）：日志里换上了，战场上的身体没跟着换
//! （「不行还是会变回来」）——0.6.3 画身体不再每帧按名字取图。
//! 开发过程：0.6.2 侦察 mod v1–v8（2026-10-06）；0.6.3 探针 v9–v11 + 静态分析（2026-10-08，C:/tfm2/scratch/view_probe*）。
//! 0.6.4（2026-10-14）：同一个函数（开头 48 字节和 0.6.3 一样）搬到 0x23312a0，槽在 0x3c82db8，实体表和值的字段没变
//! （league_main/src/build.rs 的说明）；0.6.3 的地址（0x2808e30 / 0x3c31358）不再认。
//! 0.3.2（2026-10-19，用户：「凯隐变身的时候中途有一段突然变回去」，那一局的日志里形态一直在）：有形态时正在播的动画名
//! 不在 `FORM_TAGS` 里（游戏播了一个形态没有自己一套的动作，身体就画成原样），每个凯隐每个名字记一行
//! `... plays "<name>" with no form frames`。

use std::sync::{Mutex, Once};

use super::{wlog, FORM_D, FORM_S};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。
/// 被动在墙里挂的暗影雾（本体 / 暗裔 / 影流）。
const IN_WALL: &[u8] = b"league_kayn_in_wall";

/// 凯隐在画面实体里的名字。
pub const NAME: &[u8] = b"league_kayn";

/// 形态有自己一套的动作（凯隐图里的 `rh_*` / `sh_*`）和墙里有暗影剪影的动作（`w_*` / `rw_*` / `hw_*`）。
pub const FORM_TAGS: [&str; 12] =
    ["idle", "run", "hit", "dead", "ult", "ult_fx1", "transform", "skill2_fx1", "attack", "skill", "skill2", "ult_exit"];
pub const WALL_TAGS: [&str; 4] = ["idle", "run", "hit", "skill"];
const PREFIXES: [&str; 5] = ["rw_", "hw_", "w_", "rh_", "sh_"];

/// 正在播的动画名 + 形态 + 在不在墙里 → 该播的名字（不用换就是 None）。本包和数据换上去的前缀先去掉，再按现在的
/// 样子重新加：出墙后 `w_run` 回到 `run`，暗裔里数据播的 `rh_attack` 不动；别的动作（`r_hidden` ……）不碰。
pub fn anim_for(cur: &str, darkin: bool, shadow: bool, in_wall: bool) -> Option<String> {
    let base = PREFIXES.iter().find_map(|p| cur.strip_prefix(p)).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if in_wall && WALL_TAGS.contains(&base) {
        format!("{}{base}", if darkin { "rw_" } else if shadow { "hw_" } else { "w_" })
    } else if darkin {
        format!("rh_{base}")
    } else if shadow {
        format!("sh_{base}")
    } else {
        base.to_string()
    };
    (want != cur).then_some(want)
}

/// 有形态却换不了的动画名（形态没有自己一套，画面会画原样）：`r_hidden`（R 里藏起来，什么都不画）不算。
pub fn undressed(cur: &str, darkin: bool, shadow: bool) -> bool {
    let base = PREFIXES.iter().find_map(|p| cur.strip_prefix(p)).unwrap_or(cur);
    (darkin || shadow) && !FORM_TAGS.contains(&base) && cur != "r_hidden"
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

/// 记下的形态：(显示世界, 实体号) → 暗裔 / 影流（阵亡时 buff 清掉，尸体仍是那个形态）。不按世界整张清掉：
/// 这个函数可能被不止一个显示世界轮流调用。
#[derive(Default)]
pub struct Forms {
    seen: Vec<(usize, u64, bool, bool)>,
}

impl Forms {
    /// 这一帧的 buff → 要画的 (暗裔, 影流)：有形态 buff 就记下，没有就用记下的。
    pub fn form(&mut self, world: usize, key: u64, darkin: bool, shadow: bool) -> (bool, bool) {
        match self.seen.iter_mut().find(|e| e.0 == world && e.1 == key) {
            Some(e) if darkin || shadow => {
                e.2 = darkin;
                e.3 = shadow;
                (darkin, shadow)
            }
            Some(e) => (e.2, e.3),
            None if darkin || shadow => {
                self.seen.push((world, key, darkin, shadow));
                if self.seen.len() > 64 {
                    self.seen.remove(0);
                }
                (darkin, shadow)
            }
            None => (false, false),
        }
    }
}

/// 诊断：调用次数、见过的显示世界、换动画名的次数（每 10 秒一行），每个凯隐的样子（形态、墙里）一变就记一行。
struct Stats {
    calls: u64,
    worlds: Vec<usize>,
    kayns: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    looks: Vec<(usize, u64, bool, bool, bool)>, // (world, entity, darkin, shadow, in wall) last logged
    bare: Vec<(u64, String)>,                   // (entity, animation) logged as having no form frames
}

static STATS: Mutex<Stats> =
    Mutex::new(Stats { calls: 0, worlds: Vec::new(), kayns: 0, writes: 0, last: None, looks: Vec::new(), bare: Vec::new() });
static FORMS: Mutex<Forms> = Mutex::new(Forms { seen: Vec::new() });
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

/// 显示世界里每个凯隐：按身上的 buff 换正在播的动画名。
unsafe fn dress_kayn(world: usize, ents: &[Ent]) {
    let mut forms = match FORMS.try_lock() {
        Ok(f) => f,
        Err(_) => return,
    };
    let mut st = match STATS.try_lock() {
        Ok(s) => s,
        Err(_) => return,
    };
    st.calls += 1;
    if !st.worlds.contains(&world) && st.worlds.len() < 8 {
        st.worlds.push(world);
    }
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.kayns > 0 {
            wlog(format!("display handler: {} calls, worlds {:x?}, Kayn seen {} times, {} animation names swapped in 10 s",
                st.calls, st.worlds, st.kayns, st.writes));
        }
        st.last = Some(now);
        st.calls = 0;
        st.kayns = 0;
        st.writes = 0;
        st.worlds.clear();
    }
    for e in ents {
        let elem = e.elem;
        let v = elem + VALUE;
        if q(v + NAME_LEN_AT) != NAME.len() {
            continue;
        }
        let ptr = q(v + NAME_PTR);
        if !plausible(ptr) || std::slice::from_raw_parts(ptr as *const u8, NAME.len()) != NAME {
            continue;
        }
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
        st.kayns += 1;
        let (bd, bs, w) = read_buffs(buffs.iter().copied());
        let key = q(elem) as u64;
        let (d, s) = forms.form(world, key, bd, bs);
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let look = (world, key, d, s, w);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            let mine: Vec<String> =
                buffs.iter().filter(|b| b.starts_with(b"league_kayn")).map(|b| String::from_utf8_lossy(b).into_owned()).collect();
            wlog(format!("world {world:#x} Kayn #{key}: {}{} (playing {cur}; {}buffs {mine:?})",
                if d { "Darkin" } else if s { "Shadow Assassin" } else { "Kayn" }, if w { ", in the wall" } else { "" },
                if (d, s) != (bd, bs) { "form remembered, " } else { "" }));
        }
        if undressed(cur, d, s) && !st.bare.iter().any(|b| b.0 == key && b.1 == cur) {
            st.bare.push((key, cur.to_string()));
            if st.bare.len() > 64 {
                st.bare.remove(0);
            }
            wlog(format!("world {world:#x} Kayn #{key}: {} plays \"{cur}\" with no form frames (drawn as plain Kayn)",
                if d { "Darkin" } else { "Shadow Assassin" }));
        }
        let Some(want) = anim_for(cur, d, s, w) else { continue };
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

/// 加载时换槽（一个进程只换一次）。
pub fn install_once() {
    HOOK.call_once(|| {
        match game_places::hook::add("league_kayn_form", dress_kayn) {
            Ok((slot, prev)) => wlog(format!(
                "full transform on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("full transform off ({e}): Kayn keeps the data pack's half transform")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_formed_kayn_without_form_frames_is_noted() {
        assert!(undressed("stun", true, false));
        assert!(undressed("rh_stun", true, false));
        assert!(!undressed("idle", true, false)); // swapped to rh_idle
        assert!(!undressed("rh_attack", true, false));
        assert!(!undressed("r_hidden", false, true)); // inside his target in R: nothing drawn
        assert!(!undressed("stun", false, false)); // no form: the base body is right
    }

    #[test]
    fn the_playing_animation_follows_the_look() {
        let a = |c: &str, d, s, w| anim_for(c, d, s, w);
        assert_eq!(a("idle", true, false, false).as_deref(), Some("rh_idle"));
        assert_eq!(a("run", false, true, false).as_deref(), Some("sh_run"));
        assert_eq!(a("dead", true, false, false).as_deref(), Some("rh_dead"));
        assert_eq!(a("rh_attack", true, false, false), None); // the data's own form cast
        assert_eq!(a("attack", true, false, false).as_deref(), Some("rh_attack")); // the action's first tick
        assert_eq!(a("idle", false, false, false), None); // not formed: the base body
        assert_eq!(a("run", false, false, true).as_deref(), Some("w_run"));
        assert_eq!(a("run", true, false, true).as_deref(), Some("rw_run"));
        assert_eq!(a("sh_run", false, true, true).as_deref(), Some("hw_run"));
        assert_eq!(a("w_run", false, false, false).as_deref(), Some("run")); // out of the wall
        assert_eq!(a("rw_run", true, false, false).as_deref(), Some("rh_run"));
        assert_eq!(a("dead", false, true, true).as_deref(), Some("sh_dead")); // no in-wall death: the form's
        assert_eq!(a("r_hidden", true, false, false), None);
        assert_eq!(a("rh_skill2_fx1", true, false, false), None);
    }

    #[test]
    fn the_buffs_pick_the_look() {
        let b = |v: &[&'static str]| read_buffs(v.iter().map(|s| s.as_bytes()));
        assert_eq!(b(&["league_kayn_form_d", "x"]), (true, false, false));
        assert_eq!(b(&["league_kayn_form_s", "league_kayn_in_wall_s"]), (false, true, true));
        assert_eq!(b(&["league_kayn_in_wall"]), (false, false, true));
    }

    #[test]
    fn the_form_outlives_its_buff() {
        let mut f = Forms::default();
        assert_eq!(f.form(1, 7, false, false), (false, false)); // not formed yet
        assert_eq!(f.form(1, 7, true, false), (true, false)); // transformed
        assert_eq!(f.form(1, 7, false, false), (true, false)); // dead: buffs gone, still Darkin
        assert_eq!(f.form(1, 8, false, false), (false, false)); // another Kayn
        assert_eq!(f.form(2, 7, false, false), (false, false)); // another display world
        assert_eq!(f.form(1, 7, false, false), (true, false)); // the first world's corpse is still Darkin
    }
}
