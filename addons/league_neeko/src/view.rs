//! 假扮的外形：屏幕上的妮蔻在假扮期间整个身体画成那名队友（league_viego_soul/src/view.rs 0.1.7 的做法，同一个显示钩子
//! game_places::hook）。
//!
//! 显示世界的实体值 +0x40 / +0x48 是英雄 id，**+0x50 / +0x58 / +0x60 是身体用哪套图的资源名**，+0x68 / +0x70 / +0x78 是
//! 正在播的动画名。名字是 `league_neeko` 的实体：屏幕时钟（game_places::clock）对上被动在屏幕放的那场模拟里记下的变身
//! 时段时，把那名队友的显示实体的资源名抄到她的 +0x50（新字符串用游戏同一个堆分配，旧的照游戏的做法释放），正在播的动画
//! 名他图里没有就换成他有的（souls.rs 的动作表；`hd_` / `lo_` 前缀照留）；时段外把记下的原资源名写回去。
//! 显示世界收不到原生加的 buff（佛耶戈 0.1.3 / 0.1.6 的教训），所以只按时钟。

use std::sync::{Mutex, Once};

use super::{souls, wlog, HERO};
use game_places::hook::{Ent, ANIM_CAP, NAME_LEN_AT, NAME_PTR, VALUE};

/// Strings {cap, ptr, len}: the body's resource name at +0x50.
const RES_CAP: usize = 0x50;

/// 她图里的这个动作队友图里没有时，按顺序换成第一个他有的（前缀 `hd_` / `lo_` 先带着找，再不带）。
pub fn anim_for(cur: &str, tags: &[&str]) -> Option<String> {
    if tags.contains(&cur) {
        return None;
    }
    let (pre, base) = ["hd_", "lo_"].iter().find_map(|p| cur.strip_prefix(p).map(|b| (*p, b))).unwrap_or(("", cur));
    let chain: &[&str] = match base {
        "skill2" => &["skill2", "skill", "attack", "idle"],
        "skill" => &["skill", "attack", "idle"],
        "ult" | "ult_b" => &["ult", "skill2", "skill", "attack", "idle"],
        "attack" | "attack_w" => &["attack", "idle"],
        "run" => &["run", "idle"],
        "hit" => &["hit", "idle"],
        "dead" => &["dead", "hit", "idle"],
        _ => &["idle"],
    };
    for t in chain {
        let with = format!("{pre}{t}");
        if tags.contains(&with.as_str()) {
            return Some(with);
        }
        if tags.contains(t) {
            return Some(t.to_string());
        }
    }
    None
}

/// 队友的动作表。
pub fn tags_of(id: &[u8]) -> Option<&'static [&'static str]> {
    let id = std::str::from_utf8(id).ok()?;
    souls::SOULS.binary_search_by(|s| s.0.cmp(id)).ok().map(|i| souls::SOULS[i].2)
}

/// One disguise the passive started in a sim the screen replays: the match and set, Neeko's entity id there (the
/// display entity's key is the same id), the tick, the ally's champion id.
#[derive(Clone, Debug, PartialEq)]
pub struct Worn {
    pub m: u64,
    pub s: u64,
    pub id: usize,
    pub tick: usize,
    pub name: String,
}

static WORN: Mutex<Vec<Worn>> = Mutex::new(Vec::new());
static OFFS: Mutex<Vec<(u64, u64, usize, usize)>> = Mutex::new(Vec::new());
/// The match and set of the last sim the screen replays that has a Neeko.
static LATEST: Mutex<Option<(u64, u64)>> = Mutex::new(None);

pub fn note_on(m: u64, s: u64, id: usize, tick: usize, name: &str) {
    if let Ok(mut w) = WORN.lock() {
        let e = Worn { m, s, id, tick, name: name.to_string() };
        if !w.contains(&e) {
            w.push(e);
            if w.len() > 512 {
                w.remove(0);
            }
        }
    }
}

pub fn note_off(m: u64, s: u64, id: usize, tick: usize) {
    if let Ok(mut o) = OFFS.lock() {
        if !o.contains(&(m, s, id, tick)) {
            o.push((m, s, id, tick));
            if o.len() > 512 {
                o.remove(0);
            }
        }
    }
}

pub fn note_view(m: u64, s: u64) {
    if let Ok(mut l) = LATEST.lock() {
        *l = Some((m, s));
    }
}

/// The ally Neeko `id` wears at sim tick `t` of (m, s): the last disguise started at or before `t` and not ended by
/// then (a disguise with no end noted lasts to the match's end).
pub fn wearing(all: &[Worn], offs: &[(u64, u64, usize, usize)], m: u64, s: u64, id: usize, t: usize) -> Option<String> {
    let start = all.iter().filter(|e| e.m == m && e.s == s && e.id == id && e.tick <= t).max_by_key(|e| e.tick)?;
    let end = offs.iter().filter(|e| e.0 == m && e.1 == s && e.2 == id && e.3 >= start.tick).map(|e| e.3).min();
    end.is_none_or(|end| t < end).then(|| start.name.clone())
}

/// Her own DLL's client extension (not the bundle's: there Viego's reader feeds the shared clock).
pub struct ClockFeed;

impl mod_api_stable::StableExtension for ClockFeed {
    fn post_update(&self, ctx: &mut mod_api_stable::StableClient<'_>, _dt: u64) {
        if !ctx.is_in_game() {
            game_places::clock::observe(false, None);
            return;
        }
        let path = game_places::clock::CLOCK_PATH;
        let parts: Vec<&str> = path.split('.').collect();
        let shown = (1..=parts.len()).all(|n| ctx.ui_visible(&parts[..n].join(".")) == Some(true));
        let text = shown.then(|| ctx.ui_text(path)).flatten();
        game_places::clock::observe(true, text.as_deref());
    }
}

/// (display world, key) -> her own resource name.
static ORIG: Mutex<Vec<(usize, u64, Vec<u8>)>> = Mutex::new(Vec::new());
/// (display world, key) -> what she was last drawn as (logged when it changes).
static LOOKS: Mutex<Vec<(usize, u64, Vec<u8>)>> = Mutex::new(Vec::new());
static HOOK: Once = Once::new();

use game_places::heap::{GetProcessHeap, HeapAlloc, HeapFree};

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

unsafe fn string_at<'a>(at: usize, max: usize) -> Option<&'a [u8]> {
    let (cap, ptr, len) = (q(at), q(at + 8), q(at + 16));
    (len >= 1 && len <= max && cap >= len && plausible(ptr)).then(|| std::slice::from_raw_parts(ptr as *const u8, len))
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

unsafe fn dress_neeko(world: usize, ents: &[Ent]) {
    let mut recs: Vec<(u64, usize, &[u8])> = Vec::new();
    for e in ents {
        let v = e.elem + VALUE;
        let (n, p) = (q(v + NAME_LEN_AT), q(v + NAME_PTR));
        if (1..=64).contains(&n) && plausible(p) {
            recs.push((q(e.elem) as u64, v, std::slice::from_raw_parts(p as *const u8, n)));
        }
    }
    if !recs.iter().any(|r| r.2 == HERO.as_bytes()) {
        return;
    }
    let (Ok(mut orig), Ok(mut looks)) = (ORIG.try_lock(), LOOKS.try_lock()) else { return };
    let view = LATEST.lock().ok().and_then(|l| *l);
    let tick = game_places::clock::screen_tick();
    for &(key, v, name) in &recs {
        if name != HERO.as_bytes() {
            continue;
        }
        let Some(res) = string_at(v + RES_CAP, 64) else { continue };
        let original = match orig.iter().find(|o| o.0 == world && o.1 == key) {
            Some(o) => o.2.clone(),
            None => {
                orig.push((world, key, res.to_vec()));
                if orig.len() > 64 {
                    orig.remove(0);
                }
                res.to_vec()
            }
        };
        let ally: Option<Vec<u8>> = match (tick, view, WORN.lock(), OFFS.lock()) {
            (Some(t), Some((m, s)), Ok(w), Ok(o)) => wearing(&w, &o, m, s, key as usize, t).map(String::into_bytes),
            _ => None,
        };
        // the ally's body: his display entity's resource name (an HD hero's sheet), else his champion id
        let target: Option<(Vec<u8>, &'static [&'static str])> = ally.as_deref().and_then(|id| {
            let tags = tags_of(id)?;
            let live = recs.iter().find(|r| r.2 == id).and_then(|rec| string_at(rec.1 + RES_CAP, 64));
            Some((live.unwrap_or(id).to_vec(), tags))
        });
        let want_res: &[u8] = target.as_ref().map_or(&original, |t| &t.0);
        if !looks.iter().any(|l| l.0 == world && l.1 == key && l.2 == want_res) {
            looks.retain(|l| !(l.0 == world && l.1 == key));
            looks.push((world, key, want_res.to_vec()));
            if looks.len() > 64 {
                looks.remove(0);
            }
            wlog(format!("world {world:#x} Neeko #{key}: drawn as {} (screen tick {tick:?}, sim {view:?})",
                         String::from_utf8_lossy(want_res)));
        }
        if res != want_res {
            put_string(v + RES_CAP, want_res);
        }
        if let Some((_, tags)) = target {
            let Some(cur) = string_at(v + ANIM_CAP, 32) else { continue };
            let Ok(cur) = std::str::from_utf8(cur) else { continue };
            if let Some(want) = anim_for(cur, tags) {
                put_string(v + ANIM_CAP, want.as_bytes());
            }
        }
    }
}

/// 加载时挂上显示钩子（一个进程只挂一次）。
pub fn install_once() {
    HOOK.call_once(|| match game_places::hook::add("league_neeko", dress_neeko) {
        Ok((slot, prev)) => wlog(format!(
            "disguise look on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
            if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
        )),
        Err(e) => wlog(format!("disguise look off ({e}): she keeps her own body")),
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn her_moves_map_to_the_allys() {
        let t = &["idle", "run", "attack", "skill", "hit", "dead", "ult"];
        assert_eq!(anim_for("idle", t), None);
        assert_eq!(anim_for("attack_w", t).as_deref(), Some("attack"));
        assert_eq!(anim_for("skill2", t).as_deref(), Some("skill"));
        assert_eq!(anim_for("ult_b", t).as_deref(), Some("ult"));
        let hd = &["idle", "run", "hd_idle", "hd_run", "hd_attack"];
        assert_eq!(anim_for("hd_run", hd), None);
        assert_eq!(anim_for("hd_skill", hd).as_deref(), Some("hd_attack"));
        assert_eq!(anim_for("hd_hit", t).as_deref(), Some("hit"));
    }

    #[test]
    fn the_clock_finds_whom_she_wears() {
        let w = |id, tick, n: &str| Worn { m: 7, s: 1, id, tick, name: n.into() };
        let all = vec![w(30, 1000, "league_garen"), w(30, 5000, "league_jinx")];
        let offs = vec![(7, 1, 30, 1300)];
        assert_eq!(wearing(&all, &offs, 7, 1, 30, 999), None);
        assert_eq!(wearing(&all, &offs, 7, 1, 30, 1000).as_deref(), Some("league_garen"));
        assert_eq!(wearing(&all, &offs, 7, 1, 30, 1300), None);
        assert_eq!(wearing(&all, &offs, 7, 1, 30, 9000).as_deref(), Some("league_jinx"));
        assert_eq!(wearing(&all, &offs, 7, 2, 30, 1100), None);
    }
}
