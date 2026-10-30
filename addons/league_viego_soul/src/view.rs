//! 整身附身：附身时佛耶戈整个身体（站、跑、出招、挨打）画成被附身的那个英雄。只在游戏 0.6.4 起的 Windows 版上生效（地址由 game_places 运行时找，0.6.5 核对过），别的版本
//! 什么都不做，附身就只有数据里的亡魂黑雾。
//!
//! 和凯隐附加包（league_kayn_form/src/view.rs）挂在同一个地方：游戏的显示世界每帧调用显示处理表里的更新函数
//! （rva 0x23312a0；0.6.3 时 0x2808e30），函数指针在 .rdata 的槽 rva 0x3c82db8 里（0.6.3 时 0x3c31358）。加载时核对函数开头 24 个字节，把槽换成本包的函数：先调用
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
//!
//! 0.1.3：显示世界里有数据加的 buff（他的 `league_viego_q_cd`），却从来没有本包原生加的（外形标记、`league_viego_p_on`），
//! 所以附身改由数据加的 `league_viego_shape` 来认（附加包副本里，播吸魂时加、附身结束 / 大招时去掉）；附身的是谁，
//! 由被动在附身时记下（`note_possess`）。
//!
//! 0.1.4：屏幕放的那场模拟（ClientMatchView）几秒钟就把整局跑完，屏幕几分钟后才放到附身那一刻（上一局：模拟里 11:38 附身
//! 格温，屏幕三分多钟以后才放到），0.1.3 只取 20 秒内记下的附身，所以永远取不到。现在每条记下模拟的场次、佛耶戈的实体号
//! （和画面实体的 key 是同一个号）和 tick；屏幕上这个佛耶戈每开始一次附身（播附身动作 `possess`，或 shape buff 出现），就取
//! 那场模拟里记给他的下一条。

use std::sync::{Mutex, Once};

use super::{souls, wlog, HERO, LOOK};
use mod_api_stable::{StableClient, StableExtension};
use game_places::hook::{Ent, VALUE, NAME_PTR, NAME_LEN_AT, ANIM_CAP, BUFFS_PTR, BUFFS_LEN, BUFF_SIZE};

/// 显示更新函数和它的槽：游戏版本不同地址不同，由 game_places::display() 在加载时找（2026-10-20，以前写死 0.6.4 的
/// rva 0x23312a0 / 0x3c82db8 和函数开头 24 个字节）。
/// Strings {cap, ptr, len}: the body's resource name at +0x50 / +0x58 / +0x60, the playing animation at +0x68 / +0x70 / +0x78.
const RES_CAP: usize = 0x50;

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
const BUFF_LINES: usize = 400;

/// The data's possession buff on his display entity (the add-on copy adds it with the possession's pictures).
const SHAPE: &[u8] = b"league_viego_shape";
/// The data's possession pose (the show plays it with the shape buff, again on a soul taken while possessed).
const POSSESS_ANIM: &[u8] = b"possess";

/// One possession the passive started in a sim the screen replays: the sim's match and set, Viego's entity id there
/// (the display entity's key is the same id), the tick, the victim's champion id.
#[derive(Clone, Debug, PartialEq)]
pub struct Taken {
    pub m: u64,
    pub s: u64,
    pub id: usize,
    pub tick: usize,
    pub name: String,
}

/// Possessions noted by the sims the screen replays, oldest first (the same one noted twice - a match watched again -
/// once).
static TAKEN: Mutex<Vec<Taken>> = Mutex::new(Vec::new());
/// The match and set of the last sim the screen replays that has a Viego (noted on its first update).
static LATEST: Mutex<Option<(u64, u64)>> = Mutex::new(None);

/// The passive took a soul in a sim the screen replays: remembered for the display hook.
pub fn note_possess(m: u64, s: u64, id: usize, tick: usize, name: &str) {
    if let Ok(mut t) = TAKEN.lock() {
        let e = Taken { m, s, id, tick, name: name.to_string() };
        if !t.contains(&e) {
            t.push(e);
            if t.len() > 256 {
                t.remove(0);
            }
        }
    }
}

/// Possession ends noted by the sims the screen replays: (match, set, Viego's id, tick).
static ENDS: Mutex<Vec<(u64, u64, usize, usize)>> = Mutex::new(Vec::new());

/// The passive's possession ended (time, Heartbreaker, death, a new soul) in a sim the screen replays.
pub fn note_end(m: u64, s: u64, id: usize, tick: usize) {
    if let Ok(mut e) = ENDS.lock() {
        if !e.contains(&(m, s, id, tick)) {
            e.push((m, s, id, tick));
            if e.len() > 256 {
                e.remove(0);
            }
        }
    }
}

/// The victim Viego `id` wears at sim tick `t` of (m, s): the last possession started at or before `t` and not ended
/// by then (no end noted: `p_t` after its start).
pub fn wearing(all: &[Taken], ends: &[(u64, u64, usize, usize)], m: u64, s: u64, id: usize, t: usize, p_t: usize)
               -> Option<String> {
    let start = all.iter().filter(|e| e.m == m && e.s == s && e.id == id && e.tick <= t).max_by_key(|e| e.tick)?;
    let end = ends.iter().filter(|e| e.0 == m && e.1 == s && e.2 == id && e.3 >= start.tick).map(|e| e.3).min()
        .unwrap_or(start.tick + p_t);
    (t < end).then(|| start.name.clone())
}

/// The screen's match clock (ingame.header.game_time.value, league_kayn_form 0.2's): its last whole second, when it
/// turned to it, and the match ticks a real second (the playback speed) from its last step.
struct Clock {
    secs: Option<(usize, std::time::Instant)>,
    rate: f64,
    ticking: bool,
    minute: Option<usize>,
}

static CLOCK: Mutex<Clock> = Mutex::new(Clock { secs: None, rate: 60.0, ticking: false, minute: None });
const CLOCK_PATH: &str = "ingame.header.game_time.value";

/// "12:34" -> 754.
pub fn clock_secs(text: &str) -> Option<usize> {
    let (m, s) = text.trim().split_once(':')?;
    Some(m.trim().parse::<usize>().ok()? * 60 + s.trim().parse::<usize>().ok()?)
}

/// The screen's sim tick now (None until the clock has stepped once this match).
fn screen_tick() -> Option<usize> {
    let c = CLOCK.lock().ok()?;
    let (secs, at) = c.secs?;
    c.ticking.then(|| secs * 60 + ((at.elapsed().as_secs_f64() * c.rate) as usize).min(59))
}

/// The client extension that reads the screen's clock (registered once in lib.rs).
pub struct ClockReader;

impl StableExtension for ClockReader {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        let Ok(mut c) = CLOCK.lock() else { return };
        if !ctx.is_in_game() {
            game_places::clock::observe(false, None);
            c.secs = None;
            c.ticking = false;
            c.minute = None;
            return;
        }
        let shown = {
            let parts: Vec<&str> = CLOCK_PATH.split('.').collect();
            (1..=parts.len()).all(|n| ctx.ui_visible(&parts[..n].join(".")) == Some(true))
        };
        let text = shown.then(|| ctx.ui_text(CLOCK_PATH)).flatten();
        // the shared clock (game_places::clock) for the other display hooks in the same DLL (league_neeko's disguise)
        game_places::clock::observe(true, text.as_deref());
        let Some(secs) = text.as_deref().and_then(clock_secs) else { return };
        let now = std::time::Instant::now();
        match c.secs {
            Some((s, _)) if s == secs => {}
            Some((s, at)) => {
                if secs == s + 1 {
                    c.rate = (60.0 / now.duration_since(at).as_secs_f64()).clamp(10.0, 1200.0);
                    c.ticking = true;
                } else if secs < s {
                    c.ticking = false; // another match
                }
                c.secs = Some((secs, now));
            }
            None => c.secs = Some((secs, now)),
        }
        if c.ticking && c.minute != Some(secs / 60) {
            c.minute = Some(secs / 60);
            wlog(format!("screen clock {:02}:{:02} ({:.0} ticks a second)", secs / 60, secs % 60, c.rate));
        }
    }
}

/// A sim the screen replays has started with a Viego in it: its possessions are the ones the screen will show.
pub fn note_view(m: u64, s: u64) {
    if let Ok(mut l) = LATEST.lock() {
        *l = Some((m, s));
    }
}

/// The k-th (from 0) possession of Viego `id` in the sim (m, s), by tick; past the last one noted, the last one.
pub fn nth_taken(all: &[Taken], m: u64, s: u64, id: usize, k: usize) -> Option<String> {
    let mut his: Vec<&Taken> = all.iter().filter(|t| t.m == m && t.s == s && t.id == id).collect();
    his.sort_by_key(|t| t.tick);
    his.get(k).or(his.last()).map(|t| t.name.clone())
}

/// A Viego on the screen: the possessions started there so far, and last frame's pose and shape buff.
struct Track {
    world: usize,
    key: u64,
    view: Option<(u64, u64)>,
    used: usize,
    in_possess: bool,
    shaped: bool,
    last_start: Option<std::time::Instant>,
    victim: Option<Vec<u8>>,
    /// The body last written to the log (`possession ...` lines only when it changes).
    logged: Option<Vec<u8>>,
}

static TRACKS: Mutex<Vec<Track>> = Mutex::new(Vec::new());

static STATS: Mutex<Stats> = Mutex::new(Stats { calls: 0, viegos: 0, writes: 0, last: None, looks: Vec::new(),
    buffsets: Vec::new(), buff_lines: 0 });
static ORIG: Mutex<Originals> = Mutex::new(Originals { seen: Vec::new() });
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

unsafe fn dress_viego(world: usize, ents: &[Ent]) {
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
    for e in ents {
        let elem = e.elem;
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
        // the soul's buffs are logged whenever they change (the first BUFF_LINES other changes too) - not his sim tag,
        // which he carries all game: with it every buff change was a line (2026-10-30: 1876 lines in two sets)
        let soulish = buffs.iter().any(|b| b.starts_with(b"league_viego_soul") || b.starts_with(b"league_viego_p_")
            || *b == SHAPE);
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
        let shaped = buffs.iter().any(|b| *b == SHAPE);
        // the pose the game set this frame (read before it is swapped for the victim's below)
        let posing = string_at(v + ANIM_CAP, 32) == Some(POSSESS_ANIM);
        // The sim the screen replays ran the whole match ahead of it (the possession was noted minutes before the screen
        // gets there): each possession that starts on the screen - the possess pose, or the shape buff coming on - is
        // the next one noted for this Viego (his entity id is the display key) in that sim.
        let chosen: Option<Vec<u8>> = {
            let Ok(mut tracks) = TRACKS.try_lock() else { continue };
            let view = LATEST.lock().ok().and_then(|l| *l);
            let i = match tracks.iter().position(|t| t.world == world && t.key == key) {
                Some(i) => i,
                None => {
                    tracks.push(Track { world, key, view, used: 0, in_possess: false, shaped: false, last_start: None,
                                        victim: None, logged: None });
                    if tracks.len() > 64 {
                        tracks.remove(0);
                    }
                    tracks.len() - 1
                }
            };
            let tr = &mut tracks[i];
            if tr.view != view {
                // another match: the same display world and key start over
                *tr = Track { world, key, view, used: 0, in_possess: false, shaped: false, last_start: None,
                              victim: None, logged: None };
            }
            // the pose and the shape buff of one show arrive together: a second signal within 0.25 s is the same start
            let fresh = (posing && !tr.in_possess) || (shaped && !tr.shaped);
            if fresh && !tr.last_start.is_some_and(|t| now.duration_since(t).as_secs_f64() < 0.25) {
                tr.last_start = Some(now);
                tr.used += 1;
                let k = tr.used - 1;
                let (noted, next) = match (TAKEN.lock(), view) {
                    (Ok(t), Some((m, s))) => (t.iter().filter(|e| (e.m, e.s) == (m, s) && e.id as u64 == key).count(),
                                              nth_taken(&t, m, s, key as usize, k)),
                    _ => (0, None),
                };
                tr.victim = next.map(String::into_bytes);
                wlog(format!("world {world:#x} Viego #{key}: possession {} starts on the screen ({} noted for him in \
                    the sim it replays, {:?}) -> {}", tr.used, noted, view,
                    tr.victim.as_deref().map_or("nobody".into(), |n| String::from_utf8_lossy(n).into_owned())));
            }
            tr.in_possess = posing;
            tr.shaped = shaped;
            // 0.1.7: the screen's clock against the sim's own possession ticks - the body is the victim's from the
            // tick the sim possessed to the tick it ended, whatever buffs reach the screen
            let by_clock = match (screen_tick(), view) {
                (Some(t), Some((m, s))) => Some(match (TAKEN.lock(), ENDS.lock()) {
                    (Ok(a), Ok(e)) => wearing(&a, &e, m, s, key as usize, t, 600).map(String::into_bytes),
                    _ => None,
                }),
                _ => None,
            };
            let now_victim = if let Some(id) = victim(buffs.iter().copied()) {
                Some(id.to_vec())
            } else if let Some(v) = by_clock {
                v
            } else if shaped {
                tr.victim.clone()
            } else {
                None
            };
            // against what was logged last, not the noted victim: the body can come from the clock or the buffs, and the
            // line repeated every frame (2026-10-30: runs of 129 lines)
            if now_victim != tr.logged {
                wlog(format!("world {world:#x} Viego #{key}: possession {} (shape buff {})",
                    now_victim.as_deref().map_or("over".into(), |n| String::from_utf8_lossy(n).into_owned()),
                    if shaped { "on" } else { "off" }));
                tr.logged = now_victim.clone();
            }
            now_victim
        };
        let soul = chosen.as_deref();
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

/// 加载时换槽（一个进程只换一次）。
pub fn install_once() {
    HOOK.call_once(|| {
        match game_places::hook::add("league_viego_soul", dress_viego) {
            Ok((slot, prev)) => wlog(format!(
                "whole-body possession on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x})",
                if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
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
    fn the_screen_takes_his_possessions_in_order() {
        let t = |m, id, tick, n: &str| Taken { m, s: 1, id, tick, name: n.into() };
        let all = vec![t(592, 796, 50_000, "league_jinx"), t(592, 796, 41_934, "league_gwen"), t(592, 24, 9_000, "league_lux"),
                       t(588, 796, 1_000, "league_teemo")];
        assert_eq!(nth_taken(&all, 592, 1, 796, 0).as_deref(), Some("league_gwen"));
        assert_eq!(nth_taken(&all, 592, 1, 796, 1).as_deref(), Some("league_jinx"));
        assert_eq!(nth_taken(&all, 592, 1, 796, 5).as_deref(), Some("league_jinx"));
        assert_eq!(nth_taken(&all, 592, 1, 24, 0).as_deref(), Some("league_lux"));
        assert_eq!(nth_taken(&all, 592, 2, 796, 0), None);
        assert_eq!(nth_taken(&all, 1, 1, 796, 0), None);
    }

    #[test]
    fn the_clock_finds_what_he_wears() {
        let t = |id, tick, n: &str| Taken { m: 592, s: 1, id, tick, name: n.into() };
        let all = vec![t(24, 1000, "league_lux"), t(24, 5000, "league_jinx")];
        let ends = vec![(592, 1, 24, 1300)];
        assert_eq!(wearing(&all, &ends, 592, 1, 24, 999, 600), None);
        assert_eq!(wearing(&all, &ends, 592, 1, 24, 1000, 600).as_deref(), Some("league_lux"));
        assert_eq!(wearing(&all, &ends, 592, 1, 24, 1300, 600), None);
        assert_eq!(wearing(&all, &ends, 592, 1, 24, 5599, 600).as_deref(), Some("league_jinx"));
        assert_eq!(wearing(&all, &ends, 592, 1, 24, 5600, 600), None);
        assert_eq!(clock_secs("15:48"), Some(948));
        assert_eq!(clock_secs("x"), None);
    }

    #[test]
    fn known_heroes_have_their_tags() {
        let t = tags_of(b"league_garen").expect("garen in the table");
        assert!(t.contains(&"idle") && t.contains(&"run"));
        assert!(tags_of(b"someone_elses_hero").is_none());
    }
}
