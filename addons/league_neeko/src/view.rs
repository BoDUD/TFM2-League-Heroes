//! 假扮的外形：屏幕上的妮蔻在假扮期间整个身体画成那名队友（league_viego_soul/src/view.rs 0.1.7 的做法，同一个显示钩子
//! game_places::hook）。
//!
//! 显示世界的实体值 +0x40 / +0x48 是英雄 id，**+0x50 / +0x58 / +0x60 是身体用哪套图的资源名**，+0x68 / +0x70 / +0x78 是
//! 正在播的动画名。名字是 `league_neeko` 的实体：屏幕时钟（game_places::clock）对上被动在屏幕放的那场模拟里记下的变身
//! 时段时，把那名队友的显示实体的资源名抄到她的 +0x50（新字符串用游戏同一个堆分配，旧的照游戏的做法释放），正在播的动画
//! 名他图里没有就换成他有的（souls.rs 的动作表；`hd_` / `lo_` 前缀照留）；时段外把记下的原资源名写回去。
//! 显示世界收不到原生加的 buff（佛耶戈 0.1.3 / 0.1.6 的教训），所以只按时钟。
//!
//! 0.2.0：W 的分身（`src/split.rs`）是一个**也叫 `league_neeko`** 的单位，显示世界里就有两个这个名字的实体。每个实体按
//! 自己的实体号认时段（[`wearing`]），分身只有被动在它出生时替它记了时段（她正在假扮：英雄联盟的分身照她当时的样子）才
//! 画成那名队友；原资源名按（显示世界，实体号）各记各的，记满了先丢**这一帧不在画面上**的（[`trim`]：以前丢最老的一条，
//! 一局里来几十个分身时可能丢掉她自己那条，现形后就一直画成队友）。判断都在 [`plan`]（纯计算、单元测试），钩子只读写内存。

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

/// [`wearing`] on what the passive noted so far (None when the notes are locked).
pub fn worn_at(m: u64, s: u64, id: usize, t: usize) -> Option<String> {
    let (Ok(w), Ok(o)) = (WORN.lock(), OFFS.lock()) else { return None };
    wearing(&w, &o, m, s, id, t)
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

/// (display world, key) records kept of her bodies: her own resource name ([`ORIG`]) and what she was last drawn as
/// ([`LOOKS`]) - one each for her and for every clone of hers that came on screen.
pub const KEPT: usize = 64;

/// One display entity named `league_neeko` (she, or a clone of hers) as the hook read it this frame: its key, its
/// body's resource name, the animation playing (None: not readable).
#[derive(Clone, Copy, Debug)]
pub struct Her<'a> {
    pub key: u64,
    pub res: &'a [u8],
    pub anim: Option<&'a str>,
}

/// What the hook writes into `hers[i]` this frame.
#[derive(Clone, Debug, PartialEq)]
pub struct Put {
    pub i: usize,
    pub res: Option<Vec<u8>>,
    pub anim: Option<String>,
}

/// `list` back under `KEPT`: the oldest entry first, but never one of an entity of `world` drawn this frame (`shown`)
/// while another can go (0.2.0: before, simply the oldest - with tens of clones in a match that could be her own, and
/// her original resource name lost while she was disguised kept her drawn as the ally after the reveal).
pub fn trim(list: &mut Vec<(usize, u64, Vec<u8>)>, world: usize, shown: &[u64]) {
    while list.len() > KEPT {
        let i = list.iter().position(|e| !(e.0 == world && shown.contains(&e.1))).unwrap_or(0);
        list.remove(i);
    }
}

/// The frame's work for every entity named like her in display world `world` (pure: the hook reads, this decides, the
/// hook writes). `wears(key)`: the ally whose body that entity wears at the screen's tick, by its own key (only the
/// entities the passive noted - her, and a clone made while she was disguised); `body_of(id)`: the resource name of
/// that ally's display entity (None: none on screen - his champion id is used); `drawn(key, res)`: a change of look, for
/// the log. Her own resource name is kept per (world, key) the first time it is seen and written back outside her
/// disguises; a clone's is kept the same way, so neither can take the other's.
pub fn plan(world: usize, hers: &[Her<'_>], orig: &mut Vec<(usize, u64, Vec<u8>)>, looks: &mut Vec<(usize, u64, Vec<u8>)>,
            wears: &dyn Fn(u64) -> Option<String>, body_of: &dyn Fn(&str) -> Option<Vec<u8>>,
            drawn: &mut dyn FnMut(u64, &[u8])) -> Vec<Put> {
    let shown: Vec<u64> = hers.iter().map(|h| h.key).collect();
    let mut out = Vec::new();
    for (i, h) in hers.iter().enumerate() {
        let original = match orig.iter().find(|o| o.0 == world && o.1 == h.key) {
            Some(o) => o.2.clone(),
            None => {
                orig.push((world, h.key, h.res.to_vec()));
                trim(orig, world, &shown);
                h.res.to_vec()
            }
        };
        // the ally's body: his display entity's resource name (an HD hero's sheet), else his champion id
        let target: Option<(Vec<u8>, &'static [&'static str])> = wears(h.key).and_then(|id| {
            let tags = tags_of(id.as_bytes())?;
            Some((body_of(&id).unwrap_or_else(|| id.clone().into_bytes()), tags))
        });
        let want: Vec<u8> = target.as_ref().map_or_else(|| original.clone(), |t| t.0.clone());
        if !looks.iter().any(|l| l.0 == world && l.1 == h.key && l.2 == want) {
            looks.retain(|l| !(l.0 == world && l.1 == h.key));
            looks.push((world, h.key, want.clone()));
            trim(looks, world, &shown);
            drawn(h.key, &want);
        }
        let res = (h.res != want.as_slice()).then(|| want.clone());
        let anim = target.as_ref().and_then(|(_, tags)| anim_for(h.anim?, tags));
        if res.is_some() || anim.is_some() {
            out.push(Put { i, res, anim });
        }
    }
    out
}

/// The clones the passive made in the sims the screen replays (match, set, the unit's id): only the log tells them
/// from her (`Neeko's clone #key`).
static CLONES: Mutex<Vec<(u64, u64, usize)>> = Mutex::new(Vec::new());

pub fn note_clone(m: u64, s: u64, id: usize) {
    if let Ok(mut c) = CLONES.lock() {
        if !c.contains(&(m, s, id)) {
            c.push((m, s, id));
            if c.len() > 256 {
                c.remove(0);
            }
        }
    }
}

fn is_clone(view: Option<(u64, u64)>, key: u64) -> bool {
    view.is_some_and(|(m, s)| CLONES.lock().is_ok_and(|c| c.contains(&(m, s, key as usize))))
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
    // her display entities (and her clones'), each with its value's address; one whose body is not readable is left alone
    let mine: Vec<(usize, Her<'_>)> = recs.iter().filter(|r| r.2 == HERO.as_bytes())
        .filter_map(|&(key, v, _)| {
            let res = string_at(v + RES_CAP, 64)?;
            let anim = string_at(v + ANIM_CAP, 32).and_then(|a| std::str::from_utf8(a).ok());
            Some((v, Her { key, res, anim }))
        })
        .collect();
    let hers: Vec<Her<'_>> = mine.iter().map(|m| m.1).collect();
    let wears = |key: u64| match (tick, view) {
        (Some(t), Some((m, s))) => worn_at(m, s, key as usize, t),
        _ => None,
    };
    let body_of = |id: &str| {
        recs.iter().find(|r| r.2 == id.as_bytes()).and_then(|r| string_at(r.1 + RES_CAP, 64)).map(<[u8]>::to_vec)
    };
    let mut drawn = |key: u64, res: &[u8]| {
        wlog(format!("world {world:#x} Neeko{} #{key}: drawn as {} (screen tick {tick:?}, sim {view:?})",
                     if is_clone(view, key) { "'s clone" } else { "" }, String::from_utf8_lossy(res)));
    };
    for p in plan(world, &hers, &mut orig, &mut looks, &wears, &body_of, &mut drawn) {
        let v = mine[p.i].0;
        if let Some(res) = &p.res {
            put_string(v + RES_CAP, res);
        }
        if let Some(anim) = &p.anim {
            put_string(v + ANIM_CAP, anim.as_bytes());
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

    type Books = Vec<(usize, u64, Vec<u8>)>;

    /// One frame of the hook for the entities named like her (key, body, animation): what it writes (key, body,
    /// animation) and the looks it logs. `worn`: who wears whom now; `bodies`: the allies' display bodies.
    fn frame(hers: &[(u64, &str, &str)], orig: &mut Books, looks: &mut Books, worn: &[(u64, &str)], bodies: &[(&str, &str)])
             -> (Vec<(u64, Option<String>, Option<String>)>, Vec<(u64, String)>) {
        let list: Vec<Her<'_>> = hers.iter().map(|(key, res, anim)| Her { key: *key, res: res.as_bytes(), anim: Some(anim) }).collect();
        let wears = |key: u64| worn.iter().find(|w| w.0 == key).map(|w| w.1.to_string());
        let body_of = |id: &str| bodies.iter().find(|b| b.0 == id).map(|b| b.1.as_bytes().to_vec());
        let mut drawn = Vec::new();
        let puts = plan(0x1000, &list, orig, looks, &wears, &body_of, &mut |key, res: &[u8]| {
            drawn.push((key, String::from_utf8_lossy(res).to_string()))
        });
        let puts = puts.into_iter().map(|p| (list[p.i].key, p.res.map(|r| String::from_utf8(r).unwrap()), p.anim)).collect();
        (puts, drawn)
    }

    const GAREN: &[(&str, &str)] = &[("league_garen", "league_garen")];

    #[test]
    fn a_clone_named_like_her_keeps_its_own_body() {
        let (mut orig, mut looks) = (Books::new(), Books::new());
        // she (key 30) and her clone (key 77): both her sheet, neither disguised - nothing written
        let (puts, drawn) = frame(&[(30, HERO, "idle"), (77, HERO, "run")], &mut orig, &mut looks, &[], GAREN);
        assert!(puts.is_empty());
        assert_eq!(drawn, [(30, HERO.to_string()), (77, HERO.to_string())]);
        // she wears Garen: her body and the attack she plays become his; the clone, not noted, stays hers
        let (puts, _) = frame(&[(30, HERO, "attack_w"), (77, HERO, "run")], &mut orig, &mut looks, &[(30, "league_garen")], GAREN);
        assert_eq!(puts, [(30, Some("league_garen".into()), Some("attack".into()))]);
        let (puts, _) = frame(&[(30, "league_garen", "idle"), (77, HERO, "run")], &mut orig, &mut looks, &[(30, "league_garen")], GAREN);
        assert!(puts.is_empty(), "{puts:?}");
        // her reveal: her own body back, from her own record (not the clone's, not Garen's)
        let (puts, _) = frame(&[(30, "league_garen", "idle"), (77, HERO, "run")], &mut orig, &mut looks, &[], GAREN);
        assert_eq!(puts, [(30, Some(HERO.into()), None)]);
    }

    #[test]
    fn a_clone_made_in_her_disguise_wears_it_and_keeps_it() {
        let (mut orig, mut looks) = (Books::new(), Books::new());
        frame(&[(30, HERO, "idle")], &mut orig, &mut looks, &[(30, "league_garen")], GAREN);
        // the clone comes while she wears Garen and is noted with him: drawn as Garen from its first frame
        let worn = [(30, "league_garen"), (77, "league_garen")];
        let (puts, drawn) = frame(&[(30, "league_garen", "run"), (77, HERO, "idle")], &mut orig, &mut looks, &worn, GAREN);
        assert_eq!(puts, [(77, Some("league_garen".into()), None)]);
        assert_eq!(drawn, [(77, "league_garen".to_string())]);
        // she is hit through, the clone keeps the disguise (League: it cannot lose it)
        let worn = [(77, "league_garen")];
        let (puts, _) = frame(&[(30, "league_garen", "run"), (77, "league_garen", "idle")], &mut orig, &mut looks, &worn, GAREN);
        assert_eq!(puts, [(30, Some(HERO.into()), None)]);
        // the clone gone: nothing of it is written any more
        let (puts, _) = frame(&[(30, HERO, "run")], &mut orig, &mut looks, &[], GAREN);
        assert!(puts.is_empty());
        // its record was its own sheet, never hers
        assert!(orig.iter().all(|o| o.2 == HERO.as_bytes()), "{orig:?}");
    }

    #[test]
    fn tens_of_clones_never_cost_her_her_own_body() {
        let (mut orig, mut looks) = (Books::new(), Books::new());
        frame(&[(30, HERO, "idle")], &mut orig, &mut looks, &[(30, "league_garen")], GAREN);
        // a long disguise and 3 x KEPT clones coming and going, each seen while she is drawn as Garen
        for k in 0..3 * KEPT as u64 {
            let key = 1000 + k;
            frame(&[(30, "league_garen", "idle"), (key, HERO, "run")], &mut orig, &mut looks, &[(30, "league_garen")], GAREN);
            assert!(orig.len() <= KEPT && looks.len() <= KEPT);
        }
        assert!(orig.iter().any(|o| o.1 == 30 && o.2 == HERO.as_bytes()), "her own body was dropped from the books");
        // the reveal writes her own sheet back (0.1.x's oldest-first trim lost it: she stayed Garen)
        let (puts, _) = frame(&[(30, "league_garen", "idle")], &mut orig, &mut looks, &[], GAREN);
        assert_eq!(puts, [(30, Some(HERO.into()), None)]);
    }

    #[test]
    fn the_books_drop_what_is_not_on_screen_first() {
        let e = |world: usize, key: u64| (world, key, vec![b'x']);
        let mut list: Books = (0..KEPT as u64).map(|k| e(1, k)).collect();
        list.insert(0, e(2, 5));
        // over by one: the oldest, another world's (nothing of it on screen in this one)
        trim(&mut list, 1, &[0, 1]);
        assert_eq!(list.len(), KEPT);
        assert!(list.iter().all(|x| x.0 == 1));
        // over again: the oldest not shown now (key 2: keys 0 and 1 are on screen)
        list.push(e(1, 999));
        trim(&mut list, 1, &[0, 1]);
        assert!(list.iter().any(|x| x.1 == 0) && list.iter().any(|x| x.1 == 1) && !list.iter().any(|x| x.1 == 2));
        // every one shown: the oldest after all
        let mut all: Books = (0..=KEPT as u64).map(|k| e(1, k)).collect();
        let shown: Vec<u64> = (0..=KEPT as u64).collect();
        trim(&mut all, 1, &shown);
        assert_eq!(all.len(), KEPT);
        assert!(!all.iter().any(|x| x.1 == 0));
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
