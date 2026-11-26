//! 无面 (`abysspact_faceless`) 整身夺面显示钩子：
//! 复用 `league_viego_soul/src/souls.rs` 全库英雄动画标签表与 `game_places::hook::add`，
//! 当无面处于「夺面」10 秒期间，实时把游戏显示实体资源名替换成被杀英雄的整套图，
//! 缺失动作安全回退，时间到或阵亡后自动还原回 `abysspact_faceless`。

use std::sync::{Mutex, Once};

use mod_api_stable::StableClient;

use crate::faceless::{HERO, MASK_TICKS, SHAPE};

#[path = "../../league_viego_soul/src/souls.rs"]
pub mod souls;

#[cfg(windows)]
use game_places::hook::{Ent, ANIM_CAP, BUFFS_LEN, BUFFS_PTR, BUFF_SIZE, NAME_LEN_AT, NAME_PTR, VALUE};

#[cfg(windows)]
const RES_CAP: usize = 0x50;
const CLOCK_PATH: &str = "ingame.header.game_time.value";

pub fn category_of(id: &str) -> Option<&'static str> {
    souls::SOULS.binary_search_by(|s| s.0.cmp(id)).ok().map(|i| souls::SOULS[i].1)
}

pub fn tags_of(id: &[u8]) -> Option<&'static [&'static str]> {
    let id = std::str::from_utf8(id).ok()?;
    souls::SOULS.binary_search_by(|s| s.0.cmp(id)).ok().map(|i| souls::SOULS[i].2)
}

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

#[derive(Clone, Debug, PartialEq)]
pub struct Stolen {
    pub m: u64,
    pub s: u64,
    pub id: usize,
    pub tick: usize,
    pub name: String,
}

static STOLEN: Mutex<Vec<Stolen>> = Mutex::new(Vec::new());
static ENDS: Mutex<Vec<(u64, u64, usize, usize)>> = Mutex::new(Vec::new());
static LATEST: Mutex<Option<(u64, u64)>> = Mutex::new(None);
static HOOK: Once = Once::new();

pub fn note_view(m: u64, s: u64) {
    if let Ok(mut l) = LATEST.lock() {
        *l = Some((m, s));
    }
}

pub fn note_steal(m: u64, s: u64, id: usize, tick: usize, name: &str) {
    if let Ok(mut list) = STOLEN.lock() {
        let entry = Stolen { m, s, id, tick, name: name.to_string() };
        if !list.contains(&entry) {
            list.push(entry);
            if list.len() > 256 {
                list.remove(0);
            }
        }
    }
}

pub fn note_end(m: u64, s: u64, id: usize, tick: usize) {
    if let Ok(mut list) = ENDS.lock() {
        let entry = (m, s, id, tick);
        if !list.contains(&entry) {
            list.push(entry);
            if list.len() > 256 {
                list.remove(0);
            }
        }
    }
}

/// 无面 `id` 在 (m, s) 的第 `t` tick 戴着谁的脸：最后一张在 `t` 以前戴上、还没结束的。
/// 结束要在开始**之后**才算这一张的：换脸那一 tick 记下的结束是上一张的（以前用 `>=`，连杀换上的第二张脸当场就被关掉）。
pub fn wearing(all: &[Stolen], ends: &[(u64, u64, usize, usize)], m: u64, s: u64, id: usize, t: usize) -> Option<String> {
    let start = all.iter().filter(|e| e.m == m && e.s == s && e.id == id && e.tick <= t).max_by_key(|e| e.tick)?;
    let end = ends
        .iter()
        .filter(|e| e.0 == m && e.1 == s && e.2 == id && e.3 > start.tick)
        .map(|e| e.3)
        .min()
        .unwrap_or(start.tick + MASK_TICKS);
    (t < end).then(|| start.name.clone())
}

/// 画成受害者用的资源名：他的显示单位还在就用它的（抄一份），不在就用英雄 id。
pub fn victim_resource(live: Option<&[u8]>, id: &[u8]) -> Vec<u8> {
    live.unwrap_or(id).to_vec()
}

pub fn observe_clock(ctx: &StableClient<'_>) {
    if !ctx.is_in_game() {
        game_places::clock::observe(false, None);
        return;
    }
    let parts: Vec<&str> = CLOCK_PATH.split('.').collect();
    let shown = (1..=parts.len()).all(|n| ctx.ui_visible(&parts[..n].join(".")) == Some(true));
    let text = shown.then(|| ctx.ui_text(CLOCK_PATH)).flatten();
    game_places::clock::observe(true, text.as_deref());
}

#[cfg(windows)]
mod win {
    use super::*;

    #[derive(Default)]
    struct Originals {
        seen: Vec<(usize, u64, Vec<u8>)>,
    }
    impl Originals {
        fn get_or_keep(&mut self, world: usize, key: u64, cur: &[u8]) -> Vec<u8> {
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

    static ORIG: Mutex<Originals> = Mutex::new(Originals { seen: Vec::new() });

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

    unsafe fn string_at<'a>(at: usize, max: usize) -> Option<&'a [u8]> {
        let (cap, ptr, len) = (q(at), q(at + 8), q(at + 16));
        (len >= 1 && len <= max && cap >= len && plausible(ptr))
            .then(|| std::slice::from_raw_parts(ptr as *const u8, len))
    }

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

    pub unsafe fn dress_faceless(world: usize, ents: &[Ent]) {
        let Ok(mut orig) = ORIG.try_lock() else { return };
        let mut recs: Vec<(u64, usize, &[u8])> = Vec::new();
        for e in ents {
            let v = e.elem + VALUE;
            let n = q(v + NAME_LEN_AT);
            let p = q(v + NAME_PTR);
            if !(1..=64).contains(&n) || !plausible(p) {
                continue;
            }
            recs.push((q(e.elem) as u64, v, std::slice::from_raw_parts(p as *const u8, n)));
        }

        let view = LATEST.lock().ok().and_then(|l| *l);
        let sim_t = game_places::clock::screen_tick();

        for &(key, v, name) in &recs {
            if name != HERO.as_bytes() {
                continue;
            }
            let Some(res) = string_at(v + RES_CAP, 96) else { continue };
            let original = orig.get_or_keep(world, key, res);

            let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
            let shaped = if plausible(bp) && bn <= 256 {
                (0..bn).any(|k| {
                    let b = bp + k * BUFF_SIZE;
                    let (p, n) = (q(b + 8), q(b + 0x10));
                    plausible(p) && n <= 64 && std::slice::from_raw_parts(p as *const u8, n) == SHAPE.as_bytes()
                })
            } else {
                false
            };

            let victim_id: Option<Vec<u8>> = if let (Some(t), Some((m, s))) = (sim_t, view) {
                match (STOLEN.lock(), ENDS.lock()) {
                    (Ok(a), Ok(e)) => wearing(&a, &e, m, s, key as usize, t).map(String::into_bytes),
                    _ => None,
                }
            } else if shaped {
                if let (Ok(a), Some((m, s))) = (STOLEN.lock(), view) {
                    a.iter().rev().find(|x| x.m == m && x.s == s && x.id as u64 == key).map(|x| x.name.as_bytes().to_vec())
                } else {
                    None
                }
            } else {
                None
            };

            if let Some(vid) = victim_id {
                if let Some(tags) = tags_of(&vid) {
                    // 受害者在这个显示世界里还有单位就抄他的资源名；尸体已经没了（阵亡的英雄很快就从显示世界里拿掉）
                    // 就用英雄 id 本身——每个显示单位的资源名就是它的 id（佛耶戈附加包 view.rs 同样的退路）
                    let live = recs
                        .iter()
                        .find(|r| r.2 == vid.as_slice() && r.0 != key)
                        .and_then(|r| string_at(r.1 + RES_CAP, 96));
                    let vres = victim_resource(live, &vid);
                    if res != vres.as_slice() {
                        let _ = put_string(v + RES_CAP, &vres);
                    }
                    if let Some(cur_anim) = string_at(v + ANIM_CAP, 48).and_then(|b| std::str::from_utf8(b).ok()) {
                        if let Some(fb) = anim_for(cur_anim, tags) {
                            let _ = put_string(v + ANIM_CAP, fb.as_bytes());
                        }
                    }
                    continue;
                }
            }

            // Restore original Faceless sprite when not masked
            if res != original.as_slice() {
                let _ = put_string(v + RES_CAP, &original);
            }
        }
    }
}

pub fn install() {
    HOOK.call_once(|| {
        #[cfg(windows)]
        {
            let _ = game_places::hook::add("abysspact_faceless", win::dress_faceless, |m| crate::wlog(m));
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wearing_window_tracks_start_and_end() {
        let s = vec![Stolen { m: 1, s: 0, id: 7, tick: 100, name: "league_jinx".into() }];
        let e = vec![(1, 0, 7, 450)];
        assert_eq!(wearing(&s, &e, 1, 0, 7, 99), None);
        assert_eq!(wearing(&s, &e, 1, 0, 7, 100).as_deref(), Some("league_jinx"));
        assert_eq!(wearing(&s, &e, 1, 0, 7, 449).as_deref(), Some("league_jinx"));
        assert_eq!(wearing(&s, &e, 1, 0, 7, 450), None);
    }

    #[test]
    fn a_face_put_on_as_the_last_one_ends_is_drawn() {
        // 连杀：300 tick 换上第二张脸，同一 tick 记下了第一张的结束
        let st = |tick, name: &str| Stolen { m: 1, s: 0, id: 7, tick, name: name.into() };
        let s = vec![st(100, "league_jinx"), st(300, "league_lux")];
        let e = vec![(1, 0, 7, 300)];
        assert_eq!(wearing(&s, &e, 1, 0, 7, 299).as_deref(), Some("league_jinx"));
        assert_eq!(wearing(&s, &e, 1, 0, 7, 300).as_deref(), Some("league_lux"));
        assert_eq!(wearing(&s, &e, 1, 0, 7, 899).as_deref(), Some("league_lux"));
        assert_eq!(wearing(&s, &e, 1, 0, 7, 900), None);
    }

    #[test]
    fn a_corpse_gone_from_the_screen_still_lends_its_face() {
        assert_eq!(victim_resource(Some(b"league_jinx_hd".as_slice()), b"league_jinx"), b"league_jinx_hd".to_vec());
        assert_eq!(victim_resource(None, b"league_jinx"), b"league_jinx".to_vec());
    }

    #[test]
    fn anim_fallback_never_returns_unknown_tag() {
        let tags = &["idle", "run", "attack", "skill"];
        assert_eq!(anim_for("skill", tags), None);
        assert_eq!(anim_for("skill2", tags), Some("skill"));
        assert_eq!(anim_for("ult", tags), Some("idle"));
    }
}
