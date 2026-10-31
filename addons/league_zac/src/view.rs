//! 一滩整身替换：细胞分裂化成一滩时，扎克站着、挨打都画成那一滩（图里的 `split_idle` / `split_hit`）。主包没有复活（数据读不到
//! 当前生命，也没有「受到致命伤害」的时机）；本包的数据副本用 `CasterAnimation` 播化开、一滩（每 30 tick 续一次）和重新聚起，
//! 这里再把游戏按名字自动播的 idle / hit 换掉，两次续播之间、挨打时也不会闪回站着的样子。只在游戏 0.6.4 起的 Windows 版上生效
//! （地址由 game_places 运行时找），别的版本什么都不做。
//!
//! 照 league_anivia 的 view.rs（源自 league_nasus / league_swain / league_rell）：显示世界每帧调用显示处理表里的更新函数，函数
//! 指针在 game_places 找到的槽里（别的附加包也挂在这里，一个接一个调用）。名字是 `league_zac` 的实体身上有一滩的标记
//! （主包的 `league_zac_split_on` 或本包的 `league_zac_split_form`）时，正在播的 idle / hit 换成 `split_idle` / `split_hit`；
//! 标记没了换回来。

use std::sync::{Mutex, Once};

use super::{wlog, FORMS};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。

/// 扎克在画面实体里的名字。
pub const NAME: &[u8] = b"league_zac";

/// 游戏按名字自动播、一滩有自己一套的动作：待机、挨打（一滩不走；阵亡时 buff 已经没了）。
pub const FORM_TAGS: [&str; 2] = ["idle", "hit"];
const PREFIX: &str = "split_";
/// BUFFS lines per game start.
const DUMP_CAP: usize = 30;

/// 正在播的动画名 + 是不是一滩 → 该播的名字（不用换就是 None）。聚起后把本包换上去的 `split_idle` 等换回来。
pub fn anim_for(cur: &str, foot: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if foot { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的形态：变了才记一行 FORM。
    looks: Vec<(usize, u64, bool)>,
    /// BUFFS lines written and when the last one was.
    dumped: usize,
    last_dump: Option<std::time::Instant>,
}

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, seen: 0, writes: 0, last: None, looks: Vec::new(), dumped: 0, last_dump: None });
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

/// 显示世界里每个扎克：按身上的一滩 buff 换正在播的动画名。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Zac seen {} times, {} animation names swapped in 10 s",
                st.calls, st.seen, st.writes));
        }
        st.last = Some(now);
        st.calls = 0;
        st.seen = 0;
        st.writes = 0;
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
        let foot = plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && FORMS.iter().any(|f| n == f.len() && std::slice::from_raw_parts(p as *const u8, n) == f.as_bytes())
        });
        st.seen += 1;
        // what the display world holds on him (once every 10 s while the form is off, at most DUMP_CAP lines; league_swain's
        // first game never saw its form buff here, 2026-10-17, so the names say why if it happens again)
        if !foot && st.dumped < DUMP_CAP && st.last_dump.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
            st.last_dump = Some(now);
            st.dumped += 1;
            let names: Vec<String> = if plausible(bp) && bn <= 256 {
                (0..bn).map(|k| {
                    let b = bp + k * BUFF_SIZE;
                    let (p, n) = (q(b + 8), q(b + 0x10));
                    if plausible(p) && (1..=64).contains(&n) {
                        String::from_utf8_lossy(std::slice::from_raw_parts(p as *const u8, n)).into_owned()
                    } else {
                        format!("?{p:#x}/{n}")
                    }
                }).collect()
            } else {
                Vec::new()
            };
            wlog(format!("BUFFS display world {world:#x} Zac: {bn} buffs [{}]", names.join(", ")));
        }
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let key = q(elem) as u64;
        let look = (world, key, foot);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            if let Some(k) = super::counted("form_view") {
                wlog(format!("FORM display world {world:#x} Zac #{key}: {} (playing {cur}) #{k}",
                    if foot { "SPLIT - idle/hit drawn as split_*" } else { "Zac" }));
            }
        }
        let Some(want) = anim_for(cur, foot) else { continue };
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
        match game_places::hook::add("league_zac", dress) {
            Ok((slot, prev)) => wlog(format!(
                "FORM whole-body puddle on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM whole-body puddle off ({e}): between the puddle's loops he may flash back standing")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_puddle() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("split_idle"));
        assert_eq!(anim_for("hit", true).as_deref(), Some("split_hit"));
        assert_eq!(anim_for("run", true), None);
        assert_eq!(anim_for("reform", true), None);
        assert_eq!(anim_for("dead", true), None);
        assert_eq!(anim_for("split_idle", false).as_deref(), Some("idle"));
        assert_eq!(anim_for("split_hit", false).as_deref(), Some("hit"));
        assert_eq!(anim_for("idle", false), None);
    }
}
