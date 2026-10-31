//! 附身时整身不画：骑在队友头上的时候（本包给她挂 `league_yuumi_w_on`），她自己的动作（站着、走、挨打、出招、阵亡）全换成图里
//! 空白的 `a_*`，头上的小猫由队友身上的 buff 画面 `league_yuumi_w_ride` 画。平时她被放逐（谁都看不见）；本包只在她出招的那一小段
//! 解除放逐，这时她站在队友的位置上——不换的话会在队友脚下多出一只猫。只在游戏 0.6.4 起的 Windows 版上生效（地址由 game_places 运行时找，0.6.5 核对过），别的版本什么都不做：出招的
//! 那一小段她照常画在队友脚下。
//!
//! 照 league_rammus 的 view.rs（源自 league_reksai / league_rell / league_jayce / league_nidalee / league_kayn_form）：游戏的显示世界
//! 每帧调用显示处理表里的更新函数（rva 0x23312a0），函数指针在 .rdata 的槽 rva 0x3c82db8（凯隐、佛耶戈、奈德丽、杰斯、伊莉丝、厄斐
//! 琉斯、芮尔、雷克塞、拉莫斯附加包也挂在这里，一个接一个调用）。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用槽里原来的
//! 函数，再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始：+0x40 名字，+0x68 / +0x70 / +0x78 正在播的动画名，
//! +0xb8 / +0xc0 buff 列表）。名字是 `league_yuumi` 的实体身上有附身 buff 时，正在播的动作换成 `a_*`（新名字用游戏同一个堆分配，旧的
//! 照游戏的做法释放）；附身结束后换回来。高清帧不用另管：league.dll 把登记英雄动画表里每个动作（a_idle 也在内）就地换成它的 hd_ 帧
//! （addons/league_main/src/lookup.rs）。
//!
//! 名字跟着队友走（用户 2026-11-01：「猫附身后 选手ID会留在原地」）：她头上的选手名画在她显示实体的位置（+0x17c / +0x180，league.dll
//! view.rs 的 POS_X / POS_Y），游戏不挪被放逐单位的这个位置——附身时她一直被放逐，名字就停在她跳上去的地方。附身期间每帧把她的位置
//! 摆到头上有小猫的队友（身上的 buff 以 `league_yuumi_w_ride` 开头）的位置、再抬高 [`LABEL_LIFT`]，名字就浮在队友的名字上方跟着走；
//! 附身结束、她现身后游戏自己又会更新这个位置。

use std::sync::{Mutex, Once};

use super::{wlog, RIDING};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, ANIM_PTR, ANIM_LEN, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。

/// 悠米在画面实体里的名字。
pub const NAME: &[u8] = b"league_yuumi";

/// 附身时换成空白 `a_*` 的动作：她的每一个动作。
pub const FORM_TAGS: [&str; 9] = ["idle", "run", "hit", "attack", "skill", "skill2", "w_off", "ult", "dead"];
const PREFIX: &str = "a_";

/// 队友头上小猫的 buff：`league_yuumi_w_ride` 或按他的头高抬过的副本（`_u4`、`_d2`，lib.rs 的 ride_buff）。
pub const RIDE_PREFIX: &str = "league_yuumi_w_ride";
/// 显示实体的位置（游戏像素）：x 在 +0x17c，y 在 +0x180（league.dll view.rs 的 POS_X / POS_Y）。
const POS_X: usize = 0x17c;
const POS_Y: usize = 0x180;
/// 附身时她的位置比队友的高这么多游戏像素：她的选手名画在队友的选手名上方，不叠在一起。
pub const LABEL_LIFT: f32 = 12.0;

/// 骑在位置 `host` 的队友头上时她的位置：他的位置抬高 [`LABEL_LIFT`]。
pub fn follow_point(host: (f32, f32)) -> (f32, f32) {
    (host.0, host.1 - LABEL_LIFT)
}

/// 读得通的位置（显示实体的格子不对时读到的是垃圾）。
fn sane(p: (f32, f32)) -> bool {
    p.0.is_finite() && p.1.is_finite() && p.0.abs() < 1.0e6 && p.1.abs() < 1.0e6
}

/// 正在播的动画名 + 是否附身 → 该播的名字（不用换就是 None）。附身结束后把本包换上去的 `a_idle` 等换回来。
pub fn anim_for(cur: &str, riding: bool) -> Option<String> {
    let base = cur.strip_prefix(PREFIX).filter(|b| FORM_TAGS.contains(b)).unwrap_or(cur);
    if !FORM_TAGS.contains(&base) {
        return None;
    }
    let want = if riding { format!("{PREFIX}{base}") } else { base.to_string() };
    (want != cur).then_some(want)
}

struct Stats {
    calls: u64,
    seen: u64,
    writes: u64,
    /// 附身时把她的位置摆到队友上方的帧数（名字跟着队友走）。
    follows: u64,
    last: Option<std::time::Instant>,
    /// 每个（显示世界, 实体号）上次记下的附身与否：变了才记一行 FORM。
    looks: Vec<(usize, u64, bool)>,
    /// 这次附身已经记过 FOLLOW 的（显示世界, 实体号）。
    followed: Vec<(usize, u64)>,
}

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, seen: 0, writes: 0, follows: 0, last: None, looks: Vec::new(),
                                               followed: Vec::new() });
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

/// 显示实体值 `v` 身上有没有名字满足 `pred` 的 buff。
unsafe fn buff_where(v: usize, pred: impl Fn(&[u8]) -> bool) -> bool {
    let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
    plausible(bp) && bn <= 256 && (0..bn).any(|k| {
        let b = bp + k * BUFF_SIZE;
        let (p, n) = (q(b + 8), q(b + 0x10));
        plausible(p) && n <= 64 && pred(std::slice::from_raw_parts(p as *const u8, n))
    })
}

unsafe fn point(v: usize) -> (f32, f32) {
    (std::ptr::read_unaligned((v + POS_X) as *const f32), std::ptr::read_unaligned((v + POS_Y) as *const f32))
}

/// 这个显示世界里头上有小猫的队友（不是悠米自己 `me`）：(实体号, 位置)。
unsafe fn host_of(ents: &[Ent], me: usize) -> Option<(u64, (f32, f32))> {
    ents.iter()
        .filter(|e| e.elem + VALUE != me)
        .find(|e| buff_where(e.elem + VALUE, |s| s.starts_with(RIDE_PREFIX.as_bytes())))
        .map(|e| (q(e.elem) as u64, point(e.elem + VALUE)))
        .filter(|h| sane(h.1))
}

/// 显示世界里每个悠米：按身上的附身 buff 换正在播的动画名；附身时她的位置跟着队友（名字不留在原地）。
unsafe fn dress(world: usize, ents: &[Ent]) {
    let Ok(mut st) = STATS.try_lock() else { return };
    st.calls += 1;
    let now = std::time::Instant::now();
    if st.last.is_none_or(|t| now.duration_since(t).as_secs_f64() >= 10.0) {
        if st.last.is_some() && st.seen > 0 {
            wlog(format!("display handler: {} calls, Yuumi seen {} times, {} animation names swapped, {} frames her \
                          name kept over the ally in 10 s", st.calls, st.seen, st.writes, st.follows));
        }
        st.last = Some(now);
        st.calls = 0;
        st.seen = 0;
        st.writes = 0;
        st.follows = 0;
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
        let form = buff_where(v, |s| s == RIDING.as_bytes());
        st.seen += 1;
        let key = q(elem) as u64;
        if !form {
            st.followed.retain(|f| *f != (world, key));
        } else if let Some((host, at)) = host_of(ents, v) {
            // the game leaves a banished unit's point where it was: keep hers over the host, so her name rides with him
            let (x, y) = follow_point(at);
            std::ptr::write_unaligned((v + POS_X) as *mut f32, x);
            std::ptr::write_unaligned((v + POS_Y) as *mut f32, y);
            st.follows += 1;
            if !st.followed.contains(&(world, key)) {
                st.followed.push((world, key));
                if st.followed.len() > 64 {
                    st.followed.remove(0);
                }
                if let Some(k) = super::counted("follow_view") {
                    wlog(format!("FOLLOW display world {world:#x} Yuumi #{key}: her point (so her name) kept {LABEL_LIFT} px \
                                  over the ally #{host} at ({:.0}, {:.0}) #{k}", at.0, at.1));
                }
            }
        }
        let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
        if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
            continue;
        }
        let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else { continue };
        let look = (world, key, form);
        if !st.looks.contains(&look) {
            st.looks.retain(|l| !(l.0 == world && l.1 == key));
            st.looks.push(look);
            if st.looks.len() > 64 {
                st.looks.remove(0);
            }
            if let Some(k) = super::counted("form_view") {
                wlog(format!("FORM display world {world:#x} Yuumi #{key}: {} (playing {cur}) #{k}",
                             if form { "RIDING - every action drawn as the blank a_*" } else { "on her own feet" }));
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

/// 加载时换槽（一个进程只换一次）。
pub fn install_once() {
    HOOK.call_once(|| {
        match game_places::hook::add("league_yuumi", dress) {
            Ok((slot, prev)) => wlog(format!(
                "FORM riding body on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("FORM riding body off ({e}): while she casts from the ally she is drawn at his feet")),
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_playing_animation_follows_the_ride() {
        assert_eq!(anim_for("idle", true).as_deref(), Some("a_idle"));
        assert_eq!(anim_for("skill", true).as_deref(), Some("a_skill"));
        assert_eq!(anim_for("ult", true).as_deref(), Some("a_ult"));
        assert_eq!(anim_for("a_run", false).as_deref(), Some("run")); // off his head again
        assert_eq!(anim_for("a_skill", true), None);
        assert_eq!(anim_for("idle", false), None);
        assert_eq!(anim_for("lo_idle", true), None); // the UI's frames are not hers on the battlefield
    }

    #[test]
    fn her_point_rides_over_the_host() {
        assert_eq!(follow_point((300.0, 200.0)), (300.0, 200.0 - LABEL_LIFT));
        assert!(sane((300.0, 200.0)));
        assert!(!sane((f32::NAN, 1.0)));
        assert!(!sane((1.0e9, 1.0)));
        // every ride picture buff (lib.rs ride_buff) is found by the prefix
        for k in [-6, -2, 0, 4, 16] {
            assert!(super::super::ride_buff(k).starts_with(RIDE_PREFIX));
        }
    }

    #[test]
    fn every_swapped_tag_is_in_her_sheet() {
        let fanim = include_str!("../../../league/champions/league_yuumi#anim.fanim");
        for t in FORM_TAGS {
            for p in ["", "a_", "hd_", "hd_a_"] {
                let name = format!("{p}{t}");
                assert!(fanim.contains(&format!("\"{name}\"")), "{name} is not in league_yuumi#anim.fanim");
            }
        }
    }
}
