//! 战场上的大小（游戏 0.6.4 起，Windows；这里写的是 0.6.4 的地址，0.6.5 的在 src/build.rs）：战场画身体的 0x2aaf630 只给绘制命令 UV，不给大小——Skia 按「UV × 图的真实像素」
//! 画，锚点按帧的宽高算。所以战场取到的是真实的高清帧（src/lookup.rs 的战场影子表），画出来 PPU 倍大；这里把实体的
//! 绘制缩放（显示世界实体值 +0x1b4，战场绘制函数 0x2abfdc0 读的那个数，绕实体位置缩放整套命令）写成「游戏的值 ÷ PPU」，
//! 大小、锚点都回到 1 倍（0.4.3 没有这一步：「游戏里变成了巨人」）。
//!
//! 和凯隐 / 佛耶戈附加包挂在同一个显示更新槽（rva 0x3c82db8，函数 0x23312a0，核对开头 24 个字节）：先调用槽里原来的
//! 函数，再走一遍显示世界的实体表（+0x138 的哈希表，每格 0x1d0 字节，值从 +8 开始），英雄 id（+0x40 / +0x48）登记了的
//! 实体写缩放。游戏自己的值每帧记下（[`Scale`]：是我们上一帧写的就沿用记下的，不是就当作游戏的新值），不会除两次。
//! 不改动作名：战场影子表里每个动作都是高清帧，眩晕之类不按动作名画的时候也一样（「被宝石打中后模型突然变小」）。
//!
//! 认英雄按身体用哪套图（值 +0x50 / +0x58 / +0x60 的资源名，每个实体平时就是自己的英雄 id），读不到才看英雄 id：佛耶戈
//! 附加包附身时把被附身英雄的资源名抄到佛耶戈的这里，id 还是 league_viego——附身亚索 / 泽丽 / 弗拉基米尔 / 卡尔玛时画的是
//! 他们的高清帧，按 id 认就不缩，画出来 2～3 倍大（用户 2026-10-12「Ppu的英雄佛爷戈不会变身失败吧？」）。不再是高清英雄的
//! 实体（附身结束）把游戏的值写回去。
//!
//! 画身体的那一刻再认一次（0.6.50，用户：「佛耶戈变身高清英雄的时候 还是会变的超级大」）：佛耶戈附加包也挂在这个显示更新槽，
//! 装得比这个包晚，链在我们前面——每帧是游戏的更新 → 我们的缩放 → 它换身体，这一帧我们看到的还是 league_viego，
//! 不缩，接着画出被附身英雄的高清帧（别人的佛耶戈 0.6.3 时在战场绘制里 0x231f990 抄资源名，也在我们之后）。战场绘制先调画身体的
//! 0x2aaf630（0x2abfcd5），之后才在 0x2abfdc0 读 +0x1b4：所以 0x2aaf630 的钩子先按此刻的资源名再算一遍，是高清英雄、
//! 而这一帧的更新没缩过（佛耶戈），就在这里写 ÷ PPU（另记一份「画时」的记录，附身结束时写回游戏的值）；更新已经缩过的
//! 照旧不动，不会除两次。下一帧更新看到的已是被附身英雄、自己还没有记录：从「画时」的记录接着算（0.7.1，用户：「佛耶戈
//! 不能变身PPU英雄？」）——游戏没把 +0x1b4 写回自己的值时，否则会把画时写的 ÷ PPU 当成游戏的值再除一次，附身后小 PPU 倍。
//!
//! 更新按「谁写的这个值」认记录（league.dll 0.9.21，2026-11-08 日志：妮蔻假扮时 `league_neeko 0.400 -> 0.160`、扮金克丝 /
//! 阿狸 `0.455 -> 0.207`、扮纳尔 / 李青 `0.667 -> 0.444`）：妮蔻附加包和佛耶戈一样在更新之后换身体资源名，可她（和 0.8.39 起
//! 也是高清英雄的佛耶戈）换之前就有自己的记录，记的是换之前那个英雄的 ÷ PPU；以前更新先用自己的记录，画时按新英雄写的
//! 值对不上，就当成游戏的新值再除一次。现在自己的（按实体号）、按地址的、「画时」的三份记录里，哪份写的正是 +0x1b4 现在的
//! 值就按哪份的游戏值算（[`update_prev`]）；都不是才当作游戏的新值。三份都没有、值又已经不大于 1 ÷ PPU 的，和画时一样
//! 当作已经除过（[`at_update`]）。照这样认的那一帧记一行「is the body draw's ... kept」（每个「实体 id > 画成的英雄」一次）。
//!
//! 只缩身体（0.6.30，用户：「回城时脚下的特效会被遮挡」「英雄脚下的阴影也被遮挡了」）：+0x1b4 套在战场画身体的函数
//! 0x2aaf630 交出的整组绘制命令外面（0x2abfdc0：组头插一条缩放命令 0x…11、组尾一条恢复 0x…12），组里除了身体还有阴影、
//! 脚下的圆圈、眩晕 / 嘲讽标记、读条——跟着缩成 1/PPU（艾希 1/5.5），看着像被身体挡住了。所以在 0x2aaf630 的入口挂钩：
//! 它照常画完，组里不是这个英雄自己那张图（`…/league_<英雄>#sheet`）的命令，连着的一段段各套一对「放大 PPU 倍」的
//! 缩放 / 恢复命令（和游戏自己的一样：绕同一个点、平移 (1 - k) × 点、x y 都乘 k），外面那层 ÷ PPU 一抵消，就是游戏
//! 原来的大小；身体照旧 ÷ PPU。别处读 +0x1b4 的画法不受影响。
//!
//! 特效图的绘制日志（league.dll 0.9.16，用户 2026-11-07「永恩的灵体现在在游戏里好像不显示了」：0.9.14 把 league_yone 列进
//! DRAWN_EFFECTS 以后，E 留在原地的身体看不见，而游戏的代码看绕左上角缩小是对的）：league.log 里 `PIC` 开头的行。列进
//! DRAWN_EFFECTS 的图每出现一次，记它头两次和一秒后的一次绘制——世界的特效节点画的，还是某个单位的身体绘制里画的；节点；
//! 游戏要执行的每条命令——消失时记画了多少次、多久；每分钟一行这些图和同一英雄别的特效动画各出现了几次（永恩 E 回来了却
//! 没有身体，在这里看得出）。每张图、整个日志各有行数上限，用完就不再读节点。

use std::cell::Cell;
use std::ffi::c_void;
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::{Mutex, Once};
use std::time::Instant;

use super::build::Build;
use super::hd::{self, Hero};
use super::wlog;

const TABLE: usize = 0x138;
const TABLE_MASK: usize = 0x140;
const TABLE_ITEMS: usize = 0x150;
const ELEM: usize = 0x1d0;
const VALUE: usize = 8;
const NAME_PTR: usize = 0x40;
const NAME_LEN_AT: usize = 0x48;
/// The body's resource name String {cap, ptr, len} (the sprite set it is drawn with; league_viego_soul's RES_CAP).
const RES_PTR: usize = 0x58;
const RES_LEN_AT: usize = 0x60;
const SCALE: usize = 0x1b4;
/// The entity's buffs: {ptr, len} (0x28 bytes an entry, the name's String {cap, ptr, len} at +0).
const BUFFS_PTR: usize = 0xb8;
const BUFFS_LEN: usize = 0xc0;
const BUFF_SIZE: usize = 0x28;
/// Growth lines a session (one for each change of a growing hero's stacks on screen).
const GROW_LINES: usize = 400;
/// Draw-scale lines a session: the display update's "draw scale" (one per hero and base, [`note_scale`]) and "drawn as
/// ... again" lines.
const SCALE_LINES: usize = 200;
/// Body-draw lines a session, a budget of their own: each hero's first command list and each "drawn as ... at the body
/// draw" pair. (2026-11-06: the 200 lines all three kinds shared were spent by 1858 s - every respawn is a new entity
/// key, and a scale line went with each - and the heroes that came on screen later logged nothing.)
const BODY_LINES: usize = 200;

/// One entity's draw scale: the game's own value (base) and what the hook last wrote over it.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Scale {
    pub base: f32,
    pub wrote: f32,
}

/// The scale to write this frame. `cur` is what the entity holds now: the hook's own last value (the game left it
/// alone - keep the base) or a fresh one from the game (a new base). Never divides twice.
pub fn next_scale(prev: Option<Scale>, cur: f32, ppu: f32) -> Scale {
    let base = match prev {
        Some(p) if (cur - p.wrote).abs() <= 1e-6 => p.base,
        _ => cur,
    };
    Scale { base, wrote: base / ppu }
}

/// Whether +0x1b4 holding `cur` is the value the record `s` wrote.
fn wrote_it(s: &Scale, cur: f32) -> bool {
    (cur - s.wrote).abs() <= 1e-6
}

/// The record the display update divides from: whichever of its own for this entity (by key), the same by the entity
/// value's address and the body draw's wrote the value +0x1b4 holds now (`cur`); None when none did - `cur` is the
/// game's own value then. A body swapped after the update (league_viego_soul, league_neeko: the update saw the hero
/// drawn before) is divided at the body draw for the hero it is drawn as now; the next update finds that value, and
/// its own record's `wrote` is for the hero drawn before. Taking its own record whatever it wrote (league.dll 0.9.20
/// and before) read the body draw's value as the game's and divided it again: 2026-11-08 Neeko 0.400 -> 0.160 back as
/// herself, 0.455 -> 0.207 disguised as Jinx / Ahri, 0.667 -> 0.444 as Gnar / Lee Sin (the disguise drawn PPU times too
/// small until the game wrote its own value again) - a dense Viego possessing a dense hero the same.
pub fn update_prev(own: Option<Scale>, by_value: Option<Scale>, drawn: Option<Scale>, cur: f32) -> Option<Scale> {
    [own, drawn, by_value].into_iter().flatten().find(|s| wrote_it(s, cur))
}

/// The scale the display update writes for a dense entity, `cur` being what +0x1b4 holds and `k` the divisor of the
/// hero it is drawn as: from the record that wrote `cur` ([`update_prev`]), else from `cur` as the game's own value -
/// but with no record at all and `cur` at or under a base of 1 divided, a copy of an entity shrunk before, taken as
/// divided (the body draw's guard, [`at_draw`]; the game never scales a unit under 1 / PPU on its own). Never divides
/// twice.
pub fn at_update(own: Option<Scale>, by_value: Option<Scale>, drawn: Option<Scale>, cur: f32, k: f32) -> Scale {
    let prev = update_prev(own, by_value, drawn, cur);
    if prev.is_none() && own.is_none() && by_value.is_none() && drawn.is_none() && cur <= 1.0 / k + 1e-4 {
        return Scale { base: cur * k, wrote: cur };
    }
    next_scale(prev, cur, k)
}

/// The registered hero an entity is drawn as: by its body's resource name (`.../league_zeri#anim` or the bare id) when
/// that is readable, else by its id.
pub fn drawn_as<'a>(heroes: &'a hd::Heroes, res: Option<&str>, id: Option<&str>) -> Option<&'a Hero> {
    heroes.of_name(res.or(id)?)
}

/// What the body draw does with an entity's scale, `cur` being what +0x1b4 holds as it starts.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum AtDraw {
    /// drawn with dense frames: write `wrote` (the display update's own value when it shrank it this frame)
    Write(Scale),
    /// no longer dense and the value is still the one written here: the game's own value back
    Restore(f32),
    Leave,
}

/// The scale at the body draw. `shrunk`: the display update's record for this entity, `drawn`: the body draw's own,
/// `shown`: PPU / size of the hero it is drawn as now (None: not a dense hero). Never divides twice.
pub fn at_draw(shrunk: Option<Scale>, drawn: Option<Scale>, cur: f32, shown: Option<f32>) -> AtDraw {
    let ours = |s: &Scale| wrote_it(s, cur);
    match shown {
        Some(k) => {
            let prev = match shrunk {
                Some(s) if ours(&s) => Some(s), // shrunk by the display update this frame: its base
                _ => drawn,
            };
            // No record at all and the value already at or under a base of 1 divided: a copy of an entity the
            // display update had shrunk (the match-result screen draws the heroes from copies carrying the divided
            // scale: Zeri 0.350 -> 0.122, Mordekaiser 0.550 -> 0.303, a dot each, 2026-10-15) - taken as divided.
            // The game never scales a unit under 1 / PPU on its own; a growth effect (1.5) still comes out above.
            if prev.is_none() && cur <= 1.0 / k + 1e-4 {
                return AtDraw::Write(Scale { base: cur * k, wrote: cur });
            }
            AtDraw::Write(next_scale(prev, cur, k))
        }
        // not drawn dense now: the value back if it is still one written here - by the body draw (a possession over),
        // or by this frame's display update (league_viego has dense frames since league.dll 0.8.39: the update divided
        // by Viego's PPU, then league_viego_soul swapped in a plain victim's body)
        None => match drawn.filter(|d| ours(d)).or(shrunk.filter(|s| ours(s))) {
            Some(d) => AtDraw::Restore(d.base),
            None => AtDraw::Leave,
        },
    }
}

struct State {
    scales: Vec<(usize, u64, Scale)>,
    /// the same scales by the entity value's address (what the body draw gets in rdx)
    by_value: Vec<(usize, Scale)>,
    /// the scales the body draw wrote itself, by the entity value's address (a body swapped after the display update)
    drawn: Vec<(usize, Scale)>,
    /// draw-scale lines written ([`SCALE_LINES`])
    scale_lines: usize,
    /// (hero, base in hundredths) whose draw scale was logged
    scaled: Vec<(&'static str, i32)>,
    /// body-draw lines written ([`BODY_LINES`])
    body_lines: usize,
    /// heroes whose first command list was logged
    seen: Vec<&'static str>,
    /// "id > hero" pairs whose first body-draw scale was logged
    noted: Vec<String>,
    /// (entity value, stacks) of the growing heroes, the last logged
    grows: Vec<(usize, usize)>,
    /// growth lines written: their own budget, so the draw-scale lines of a long session never silence them (2026-10-23:
    /// the 200 shared lines ran out a second after Cho'Gath came on screen, before his first stack)
    grow_lines: usize,
    /// (entity value, size drawn, when) of the form rows' heroes (hd::Table::forms), eased from frame to frame
    forms: Vec<(usize, f32, std::time::Instant)>,
    /// "id > hero" pairs whose update kept the body draw's value (a body swapped after the update) was logged
    kept: Vec<String>,
}

/// What the display update did with one dense entity ([`State::update_dense`]).
#[derive(Clone, Copy, Debug, PartialEq)]
struct Updated {
    s: Scale,
    /// the base differs from the entity's last record (or it had none)
    changed: bool,
    /// +0x1b4 held the body draw's value, not the update's own last one: a body swapped after the update
    kept_drawn: bool,
}

/// The records' length cap (each of [`State::scales`], [`State::by_value`], [`State::drawn`]).
const RECORDS: usize = 256;

impl State {
    const fn new() -> Self {
        State { scales: Vec::new(), by_value: Vec::new(), drawn: Vec::new(), scale_lines: 0, scaled: Vec::new(),
                body_lines: 0, seen: Vec::new(), noted: Vec::new(), grows: Vec::new(), grow_lines: 0, forms: Vec::new(),
                kept: Vec::new() }
    }

    /// The display update for the dense entity (`world`, `key`) whose value is at `v`, +0x1b4 holding `cur`, drawn as
    /// a hero of divisor `k`: the scale to write ([`at_update`]), its records brought up to date.
    fn update_dense(&mut self, world: usize, key: u64, v: usize, cur: f32, k: f32) -> Updated {
        let at = self.scales.iter().position(|e| e.0 == world && e.1 == key);
        let own = at.map(|i| self.scales[i].2);
        let by_value = self.by_value.iter().find(|e| e.0 == v).map(|e| e.1);
        let drawn = self.drawn.iter().find(|e| e.0 == v).map(|e| e.1);
        let s = at_update(own, by_value, drawn, cur, k);
        let kept_drawn = own.is_some_and(|o| !wrote_it(&o, cur)) && drawn.is_some_and(|d| wrote_it(&d, cur));
        match self.by_value.iter().position(|e| e.0 == v) {
            Some(i) => self.by_value[i].1 = s,
            None => {
                self.by_value.push((v, s));
                if self.by_value.len() > RECORDS {
                    self.by_value.remove(0);
                }
            }
        }
        let changed = match at {
            Some(i) => {
                let b = self.scales[i].2.base != s.base;
                self.scales[i].2 = s;
                b
            }
            None => {
                self.scales.push((world, key, s));
                if self.scales.len() > RECORDS {
                    self.scales.remove(0);
                }
                true
            }
        };
        Updated { s, changed, kept_drawn }
    }

    /// The display update for an entity that is not drawn dense (any more: a possession over): its records go, and the
    /// game's own value comes back (Some) while +0x1b4 still holds the one the update wrote.
    fn update_plain(&mut self, world: usize, key: u64, v: usize, cur: f32) -> Option<f32> {
        self.by_value.retain(|e| e.0 != v);
        let at = self.scales.iter().position(|e| e.0 == world && e.1 == key)?;
        let p = self.scales.remove(at).2;
        wrote_it(&p, cur).then_some(p.base)
    }

    /// The body draw of the entity value `ent`, +0x1b4 holding `cur`, drawn as a dense hero of divisor `shown` (None:
    /// not dense now): what to do ([`at_draw`]) and the display update's record it went by, the body draw's own record
    /// brought up to date.
    fn body(&mut self, ent: usize, cur: f32, shown: Option<f32>) -> (AtDraw, Option<Scale>) {
        let shrunk = self.by_value.iter().find(|e| e.0 == ent).map(|e| e.1);
        let at = self.drawn.iter().position(|e| e.0 == ent);
        let d = at_draw(shrunk, at.map(|i| self.drawn[i].1), cur, shown);
        match d {
            AtDraw::Write(s) => match at {
                Some(i) => self.drawn[i].1 = s,
                None => {
                    self.drawn.push((ent, s));
                    if self.drawn.len() > RECORDS {
                        self.drawn.remove(0);
                    }
                }
            },
            AtDraw::Restore(_) => self.drawn.retain(|e| e.0 != ent),
            AtDraw::Leave => {
                if at.is_some() {
                    self.drawn.retain(|e| e.0 != ent);
                }
            }
        }
        (d, shrunk)
    }
}

static STATE: Mutex<State> = Mutex::new(State::new());
static PREV: AtomicUsize = AtomicUsize::new(0);
static HOOK: Once = Once::new();

#[link(name = "kernel32")]
extern "system" {
    fn ReadProcessMemory(h: isize, base: *const c_void, buf: *mut c_void, size: usize, read: *mut usize) -> i32;
    fn GetCurrentProcess() -> isize;
    fn GetModuleHandleW(name: *const u16) -> usize;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
}

/// The game EXE's base in this process.
pub fn module_base() -> usize {
    unsafe { GetModuleHandleW(std::ptr::null()) }
}

/// `len` bytes of the game EXE at `rva` (None when unreadable).
pub fn read_rva(rva: usize, len: usize) -> Option<Vec<u8>> {
    let module = unsafe { GetModuleHandleW(std::ptr::null()) };
    if module == 0 {
        return None;
    }
    read(module + rva, len)
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
    let _ = std::panic::catch_unwind(|| unsafe { shrink(world) });
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// A String's text from its pointer and length fields (None when it does not look like a name).
unsafe fn string_at<'a>(ptr_at: usize, len_at: usize) -> Option<&'a str> {
    let (n, p) = (q(len_at), q(ptr_at));
    if !(1..=128).contains(&n) || !plausible(p) {
        return None;
    }
    std::str::from_utf8(std::slice::from_raw_parts(p as *const u8, n)).ok()
}

/// Drops the scale records of `world` whose entity was not in this walk of its table (`seen`): a set over, the next one
/// numbers its entities from #18 again, and a record left from the last set (2026-11-01 log: a minion "drawn as range_minion
/// again, draw scale back to 1.150" - Cho'Gath's base from the set before) is not the new entity's.
pub fn keep_seen(scales: &mut Vec<(usize, u64, Scale)>, world: usize, seen: &[u64]) {
    scales.retain(|e| e.0 != world || seen.contains(&e.1));
}

unsafe fn shrink(world: usize) {
    if !plausible(world) {
        return;
    }
    let ctrl = q(world + TABLE);
    let mask = q(world + TABLE_MASK);
    let items = q(world + TABLE_ITEMS);
    if items == 0 || !plausible(ctrl) || mask >= 1 << 16 || (mask + 1) & mask != 0 || items > mask + 1 {
        return;
    }
    let Ok(mut st) = STATE.try_lock() else { return };
    let heroes = hd::heroes();
    let mut seen = Vec::with_capacity(items);
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue; // empty or deleted
        }
        let elem = ctrl - (i + 1) * ELEM;
        let v = elem + VALUE;
        let id = string_at(v + NAME_PTR, v + NAME_LEN_AT);
        let res = string_at(v + RES_PTR, v + RES_LEN_AT);
        let key = q(elem) as u64;
        seen.push(key);
        let cur = std::ptr::read_unaligned((v + SCALE) as *const f32);
        let Some(hero) = drawn_as(heroes, res, id) else {
            // no longer drawn with dense frames (a possession ended): the game's own value back
            if let Some(base) = st.update_plain(world, key, v, cur) {
                std::ptr::write_unaligned((v + SCALE) as *mut f32, base);
                if st.scale_lines < SCALE_LINES {
                    st.scale_lines += 1;
                    wlog(format!("world {world:#x} #{key} {}: drawn as {} again, draw scale back to {base:.3}",
                        id.unwrap_or("?"), res.unwrap_or("?")));
                }
            }
            continue;
        };
        let name = res.unwrap_or(hero.id);
        let u = st.update_dense(world, key, v, cur, hero.shown());
        let s = u.s;
        std::ptr::write_unaligned((v + SCALE) as *mut f32, s.wrote);
        if u.changed && note_scale(&mut st, hero.id, s.base) {
            wlog(format!("world {world:#x} #{key} {name}: draw scale {cur:.3} -> {:.3} (base {:.3})", s.wrote, s.base));
        }
        // a body swapped after the update (league_neeko, league_viego_soul): one line an "id > hero" pair a session
        if u.kept_drawn && st.scale_lines < SCALE_LINES {
            let pair = format!("{} > {}", id.unwrap_or("?"), hero.id);
            if !st.kept.contains(&pair) {
                st.scale_lines += 1;
                wlog(format!("world {world:#x} #{key} {}: drawn as {name} - draw scale {cur:.3} is the body draw's \
                              (base {:.3}), kept, not divided again", id.unwrap_or("?"), s.base));
                st.kept.push(pair);
            }
        }
    }
    keep_seen(&mut st.scales, world, &seen);
}

/// Whether the draw scale of `hero` from the game's value `base` is new to the log: one line per hero and base (to a
/// hundredth) a session, within [`SCALE_LINES`] - not one per entity, which every respawn makes anew.
fn note_scale(st: &mut State, hero: &'static str, base: f32) -> bool {
    let key = (hero, (base * 100.0).round() as i32);
    if st.scale_lines >= SCALE_LINES || st.scaled.contains(&key) {
        return false;
    }
    st.scaled.push(key);
    st.scale_lines += 1;
    true
}

/// Draw command tags (the enum's niche values at +0) and layout (0xd0 bytes each). The sprite's tag stayed 0x…03; the
/// scale / restore ones are the build's ([`Build::cmd_scale`]: 0.6.5 0x…11 / 0x…12, 0.7.0 0x…12 / 0x…13), set by
/// [`install_once`] - 0 until then: the listed build's (the tests).
const CMD: usize = 0xd0;
const CMD_SPRITE: u64 = 0x8000_0000_0000_0003;
static CMD_SCALE: AtomicU64 = AtomicU64::new(0);
static CMD_RESTORE: AtomicU64 = AtomicU64::new(0);

fn scale_tag() -> u64 {
    match CMD_SCALE.load(Ordering::Relaxed) {
        0 => super::build::BUILDS[0].cmd_scale,
        t => t,
    }
}

fn restore_tag() -> u64 {
    match CMD_RESTORE.load(Ordering::Relaxed) {
        0 => super::build::BUILDS[0].cmd_restore,
        t => t,
    }
}
/// The mark on a scale / restore command this pack puts round an effect's sprite: the last 8 bytes (+0xc8), which a
/// scale or restore command leaves unread ([`cmd_kind`]).
const OURS_AT: usize = 0xc8;
const OURS: u64 = 0x5846_4555_4741_454c; // "LEAGUEFX"
/// The entity's position (x at +0x17c, y at +0x180 less +0x18c): the point the game scales its commands round.
const POS_X: usize = 0x17c;
const POS_Y: usize = 0x180;
const POS_LIFT: usize = 0x18c;

static ORIG_BODY: AtomicUsize = AtomicUsize::new(0);
static GROW: AtomicUsize = AtomicUsize::new(0);

type BodyDraw = unsafe extern "system" fn(usize, usize, usize, usize, usize, usize, usize, usize) -> usize;
type Grow = unsafe extern "system" fn(usize);

/// 0x2aaf630 (out Vec, entity value, r8, -, -, stack args 6-8; r9 and the 5th are never read): the scale for the body
/// it is drawn with now, the game's body draw, then the extras brought back to the game's size.
unsafe extern "system" fn body_detour(out: usize, ent: usize, a3: usize, _sp: usize, a5: usize, a6: usize, a7: usize,
                                      a8: usize) -> usize {
    let f: BodyDraw = std::mem::transmute(ORIG_BODY.load(Ordering::Acquire));
    let sc = std::panic::catch_unwind(|| unsafe { scale_at_draw(ent) }).ok().flatten();
    let was = IN_BODY.with(|c| c.replace(ent));
    let r = f(out, ent, a3, 0, a5, a6, a7, a8);
    IN_BODY.with(|c| c.set(was));
    // the buffs' dense pictures (before the extras go back to the game's size round them, as the effects' pairs do)
    let _ = std::panic::catch_unwind(|| unsafe { shrink_buffs(out, ent) });
    if let Some((s, hero)) = sc {
        let _ = std::panic::catch_unwind(|| unsafe { unshrink_extras(out, ent, s, hero) });
    }
    r
}

/// +0x1b4 of the entity value `ent` set for the hero its body is drawn as at this moment (a body swapper renames it
/// after the display update: league_viego_soul) -> its scale and hero when that is a dense hero.
unsafe fn scale_at_draw(ent: usize) -> Option<(Scale, &'static Hero)> {
    if !plausible(ent) {
        return None;
    }
    let id = string_at(ent + NAME_PTR, ent + NAME_LEN_AT);
    let res = string_at(ent + RES_PTR, ent + RES_LEN_AT);
    let hero = drawn_as(hd::heroes(), res, id);
    let mut st = STATE.try_lock().ok()?;
    let cur = std::ptr::read_unaligned((ent + SCALE) as *const f32);
    match st.body(ent, cur, hero.map(|h| h.shown())) {
        (AtDraw::Write(s), shrunk) => {
            let hero = hero?;
            std::ptr::write_unaligned((ent + SCALE) as *mut f32, s.wrote);
            let updated = shrunk.is_some_and(|p| wrote_it(&p, cur));
            // the pair's String only for a body the update did not shrink (not every dense body every frame)
            let pair =
                if updated || st.body_lines >= BODY_LINES { None } else { Some(format!("{} > {}", id.unwrap_or("?"), hero.id)) };
            if let Some(pair) = pair.filter(|p| !st.noted.contains(p)) {
                st.body_lines += 1;
                wlog(format!("{}: drawn as {} at the body draw (the display update saw {}) - draw scale {cur:.3} -> {:.3}",
                    id.unwrap_or("?"), hero.id, res.unwrap_or("?"), s.wrote));
                st.noted.push(pair);
            }
            Some((s, hero))
        }
        (AtDraw::Restore(base), _) => {
            std::ptr::write_unaligned((ent + SCALE) as *mut f32, base);
            None
        }
        (AtDraw::Leave, _) => None,
    }
}

/// The texture name of a sprite command (its String {cap, ptr, len} at +8).
unsafe fn sprite_name<'a>(cmd: usize) -> Option<&'a str> {
    if q(cmd) as u64 != CMD_SPRITE {
        return None;
    }
    string_at(cmd + 0x10, cmd + 0x18)
}

/// Whether a texture name is the hero's own sheet (`asset/.../league_ashe#sheet`).
pub fn is_body(name: &str, hero: &str) -> bool {
    name.rsplit('/').next().and_then(|n| n.split('#').next()) == Some(hero)
}

/// [first, last] runs of the commands that are neither the body (1) nor a scale / restore command (2).
pub fn extra_runs(kinds: &[u8]) -> Vec<(usize, usize)> {
    let mut runs = Vec::new();
    let mut i = 0;
    while i < kinds.len() {
        if kinds[i] != 0 {
            i += 1;
            continue;
        }
        let s = i;
        while i < kinds.len() && kinds[i] == 0 {
            i += 1;
        }
        runs.push((s, i - 1));
    }
    runs
}

/// `cmd` put in the command Vec {cap, ptr, len} at `out` before index `at` (grown by the game's own grow_one).
unsafe fn insert(out: usize, at: usize, cmd: &[u8; CMD]) {
    let len = q(out + 0x10);
    if len == q(out) {
        let g: Grow = std::mem::transmute(GROW.load(Ordering::Acquire));
        g(out);
    }
    let ptr = q(out + 8);
    std::ptr::copy((ptr + at * CMD) as *const u8, (ptr + (at + 1) * CMD) as *mut u8, (len - at) * CMD);
    std::ptr::copy_nonoverlapping(cmd.as_ptr(), (ptr + at * CMD) as *mut u8, CMD);
    std::ptr::write_unaligned((out + 0x10) as *mut usize, len + 1);
}

/// The commands of the body draw that are not the hero's own sheet (shadow, rings, marks) wrapped back to the game's
/// size: `sc` is the scale written for this draw, `hero` the dense hero the body is drawn as.
unsafe fn unshrink_extras(out: usize, ent: usize, sc: Scale, hero: &Hero) {
    if !plausible(out) || !plausible(ent) {
        return;
    }
    let Ok(mut st) = STATE.try_lock() else { return };
    let cur = std::ptr::read_unaligned((ent + SCALE) as *const f32);
    if (cur - sc.wrote).abs() > 1e-6 || sc.wrote <= 0.0 {
        return; // not shrunk this frame: everything is at the game's size already
    }
    let k = sc.base / sc.wrote;
    let (cap, ptr, len) = (q(out), q(out + 8), q(out + 0x10));
    if len == 0 || len > 256 || cap < len || !plausible(ptr) {
        return;
    }
    let kinds: Vec<u8> = (0..len)
        .map(|i| {
            let c = ptr + i * CMD;
            cmd_kind(q(c) as u64, q(c + OURS_AT) as u64, sprite_name(c).is_some_and(|n| is_body(n, hero.id)))
        })
        .collect();
    let runs = extra_runs(&kinds);
    // the draw log: an effect of this unit drawn in its body draw, with the pair this pack put round it
    if !PIC_DONE.load(Ordering::Relaxed) {
        let ours: Vec<bool> = (0..len).map(|i| q(ptr + i * CMD + OURS_AT) as u64 == OURS).collect();
        if ours.contains(&true) {
            note_body_list(hero.id, &kinds, &ours, &runs, k);
        }
    }
    if !st.seen.contains(&hero.id) && st.body_lines < BODY_LINES {
        st.seen.push(hero.id);
        st.body_lines += 1;
        let list: Vec<String> = (0..len)
            .map(|i| {
                let c = ptr + i * CMD;
                let tag = (q(c) as u64) & 0xff;
                match sprite_name(c) {
                    Some(n) => format!("{tag}:{}", n.rsplit('/').next().unwrap_or(n)),
                    None => format!("{tag}"),
                }
            })
            .collect();
        wlog(format!("{}: body draw commands [{}], the extras back to the game's size in {} runs (x{k:.3})",
            hero.id, list.join(", "), runs.len()));
    }
    if !kinds.contains(&1) {
        return; // no body found: leave the list as the game made it
    }
    let px = std::ptr::read_unaligned((ent + POS_X) as *const f32);
    let py = std::ptr::read_unaligned((ent + POS_Y) as *const f32)
        - std::ptr::read_unaligned((ent + POS_LIFT) as *const f32);
    let grow = scale_cmd(k, px, py, false);
    let back = restore_cmd(false);
    for &(a, b) in runs.iter().rev() {
        insert(out, b + 1, &back);
        insert(out, a, &grow);
    }
    // a hero drawn bigger, with a stack (a table's growth rows, Cho'Gath's Feast) or while his form's buff is on (a table's form
    // rows, Volibear's Stormbringer, eased in and out): his body's own commands once more, about his soles
    let g = if let Some(&(_, buff, per)) = hd::heroes().growth.iter().find(|g| g.0 == hero.id) {
        let n = hd::grow_count(buff_names(ent).iter().map(String::as_str), buff);
        let g = hd::grown(per, n);
        if note_grow(&mut st, ent, n) {
            wlog(format!("{}: {n} x {buff} - body drawn x{g:.2} about the soles", hero.id));
        }
        g
    } else if let Some(&(_, buffs, size, secs)) = hd::heroes().forms.iter().find(|f| f.0 == hero.id) {
        let on = buffs.iter().find(|b| stacks(ent, b) > 0);
        let now = std::time::Instant::now();
        let prev = st.forms.iter().find(|f| f.0 == ent).map(|f| (f.1, now.duration_since(f.2).as_secs_f32()));
        let g = hd::eased(prev, if on.is_some() { size } else { 1.0 }, size, secs);
        st.forms.retain(|f| f.0 != ent);
        st.forms.push((ent, g, now));
        if st.forms.len() > 64 {
            st.forms.remove(0);
        }
        if note_grow(&mut st, ent, usize::from(on.is_some())) {
            match on {
                Some(b) => wlog(format!("{}: {b} on - body growing to x{size:.2} about the soles over {secs} s", hero.id)),
                None => wlog(format!("{}: no form buff - body x{g:.2}, back to x1.00 over {secs} s", hero.id)),
            }
        }
        g
    } else {
        return;
    };
    if (g - 1.0).abs() < 1e-4 {
        return;
    }
    let (sx, sy) = soles(px, py, hero.ppu);
    let up = scale_cmd(g, sx, sy, false);
    let (ptr, len) = (q(out + 8), q(out + 0x10));
    let body: Vec<u8> = (0..len)
        .map(|i| u8::from(sprite_name(ptr + i * CMD).is_some_and(|nm| is_body(nm, hero.id))))
        .collect();
    for (a, b) in body_runs(&body).into_iter().rev() {
        insert(out, b + 1, &back);
        insert(out, a, &up);
    }
}

/// What a command is to the body draw's extras: 2 a game scale / restore, 1 the body's own sheet, 0 anything else - a
/// scale / restore pair this pack put round an effect's sprite (`mark` == [`OURS`]) too: it belongs to that effect, so
/// the extras' own "back to the game's size" pair goes round it, and the effect is shrunk from the game's size.
pub fn cmd_kind(tag: u64, mark: u64, body: bool) -> u8 {
    match tag {
        t if (t == scale_tag() || t == restore_tag()) && mark != OURS => 2,
        _ if body => 1,
        _ => 0,
    }
}

/// A scale command: x and y times `k` about (`px`, `py`) - the game's own layout (translation (1 - k) x the point at
/// +8 / +0xc, the factors at +0x24 / +0x28); `ours` marks it ([`cmd_kind`]).
pub fn scale_cmd(k: f32, px: f32, py: f32, ours: bool) -> [u8; CMD] {
    let mut c = restore_cmd(ours);
    c[..8].copy_from_slice(&scale_tag().to_le_bytes());
    c[8..12].copy_from_slice(&((1.0 - k) * px).to_le_bytes());
    c[12..16].copy_from_slice(&((1.0 - k) * py).to_le_bytes());
    c[0x24..0x28].copy_from_slice(&k.to_le_bytes());
    c[0x28..0x2c].copy_from_slice(&k.to_le_bytes());
    c
}

pub fn restore_cmd(ours: bool) -> [u8; CMD] {
    let mut c = [0u8; CMD];
    c[..8].copy_from_slice(&restore_tag().to_le_bytes());
    if ours {
        c[OURS_AT..OURS_AT + 8].copy_from_slice(&OURS.to_le_bytes());
    }
    c
}

static ORIG_EFFECT: AtomicUsize = AtomicUsize::new(0);
/// The drawn effects shrunk so far, each once a draw it was shrunk in (the log's first line for each).
static EFFECTS_SEEN: Mutex<Vec<(&'static str, Pic)>> = Mutex::new(Vec::new());

type EffectDraw = unsafe extern "system" fn(usize, usize, usize, usize) -> usize;

/// The view node draw (Build::effect_draw: the command Vec it returns in rcx, the node in rdx, r8 / r9 its own): as the
/// game draws it, then every sprite command of a drawn effect's sheet ([`hd::Table::drawn_effects`]) wrapped in a
/// 1 / PPU scale about the sprite's top-left corner (+0x78 / +0x7c). The game places that corner with the frame's size
/// divided by PPU (the anim table, src/lookup.rs) but draws the picture UV x the texture's real pixels - a square a game
/// pixel, PPU times too big, hanging right and down from the corner; shrunk about the corner it covers its frame at
/// 1 / PPU.
unsafe extern "system" fn effect_detour(out: usize, node: usize, a3: usize, a4: usize) -> usize {
    let f: EffectDraw = std::mem::transmute(ORIG_EFFECT.load(Ordering::Acquire));
    let r = f(out, node, a3, a4);
    let _ = std::panic::catch_unwind(|| unsafe { shrink_sprites(out, None, Pic::Effect) });
    if !PIC_DONE.load(Ordering::Relaxed) {
        let _ = std::panic::catch_unwind(|| unsafe { note_picture(out, node) });
    }
    r
}

/// Which draw a dense picture was shrunk in (the log's word for it).
#[derive(Clone, Copy, Debug, PartialEq)]
enum Pic {
    /// a kit's view effect (the view node draw)
    Effect,
    /// a buff's view (the body draw appends each buff's sprite to its own list)
    Buff,
    /// a projectile's view (its own render)
    Projectile,
}

impl Pic {
    fn word(self) -> &'static str {
        match self {
            Pic::Effect => "effect",
            Pic::Buff => "buff",
            Pic::Projectile => "projectile",
        }
    }
}

/// Every sprite command of a drawn effect's sheet ([`hd::Table::drawn_effects`]) in the command Vec at `out` wrapped in a
/// 1 / PPU scale about the sprite's top-left corner (+0x78 / +0x7c): the game placed that corner with the frame's size
/// divided by PPU (the anim table, src/lookup.rs) but draws the picture UV x the texture's real pixels - a square a game
/// pixel, PPU times too big, hanging right and down from the corner; shrunk about the corner it covers its frame at
/// 1 / PPU. The renderer applies the sprite's own pivot, flips and rotation inside that (a turned projectile too:
/// 0.7.1's per-command draw scales everything after the corner with the drawn size). Left alone: a sprite this pack
/// wrapped already (the node draw's, inside the body draw) and, in a body draw, the unit's own body (`body`: the last
/// part of its body resource, the sheet's id). A full effect ([`hd::Table::full_effects`]) only while it is dense.
unsafe fn shrink_sprites(out: usize, body: Option<&str>, what: Pic) {
    if !plausible(out) {
        return;
    }
    let (cap, len) = (q(out), q(out + 0x10));
    // cap usize::MAX: the node draw's None (its caller checks it); a projectile's render returns {0, 8, 0} for none
    if cap == usize::MAX || len == 0 || len > 256 || cap < len || !plausible(q(out + 8)) {
        return;
    }
    let heroes = hd::heroes();
    if heroes.drawn_effects.is_empty() {
        return;
    }
    let mut i = 0;
    while i < q(out + 0x10) {
        let c = q(out + 8) + i * CMD;
        let Some(name) = sprite_name(c) else {
            i += 1;
            continue;
        };
        let wrapped = i > 0 && {
            let p = c - CMD;
            q(p) as u64 == scale_tag() && q(p + OURS_AT) as u64 == OURS
        };
        let hero = heroes.dense_of_name(name).filter(|h| heroes.drawn_effects.contains(&h.id));
        let Some(hero) = hero.filter(|_| !wrapped && !body.is_some_and(|b| is_body(name, b))) else {
            i += 1;
            continue;
        };
        let (x, y) = (std::ptr::read_unaligned((c + 0x78) as *const f32), std::ptr::read_unaligned((c + 0x7c) as *const f32));
        let k = 1.0 / hero.ppu;
        insert(out, i + 1, &restore_cmd(true));
        insert(out, i, &scale_cmd(k, x, y, true));
        i += 3;
        if let Ok(mut seen) = EFFECTS_SEEN.try_lock() {
            if !seen.iter().any(|s| s.0 == hero.id && s.1 == what) {
                seen.push((hero.id, what));
                wlog(format!("{}: {} picture drawn x{k:.3} about its corner ({x:.1}, {y:.1})", hero.id, what.word()));
            }
        }
    }
}

/// The body draw's own list after the game made it: the buffs' pictures among it shrunk (src/build.rs: the body draw
/// renders each buff's view and appends its sprite) - not the unit's body, nor its view effects the node draw shrank
/// inside it already.
unsafe fn shrink_buffs(out: usize, ent: usize) {
    if !plausible(ent) || hd::heroes().drawn_effects.is_empty() {
        return;
    }
    let res = string_at(ent + RES_PTR, ent + RES_LEN_AT).or_else(|| string_at(ent + NAME_PTR, ent + NAME_LEN_AT));
    let Some(body) = res.and_then(|r| r.rsplit('/').next()).and_then(|r| r.split('#').next()) else { return };
    shrink_sprites(out, Some(body), Pic::Buff);
}

static ORIG_PROJ: AtomicUsize = AtomicUsize::new(0);
static ORIG_PROJ3: AtomicUsize = AtomicUsize::new(0);

/// A projectile view's render (rcx = the command Vec it returns, rdx = the system, r8 = the projectiles, r9 = the assets,
/// the 5th on the stack = the projectile's id): {0, 8, 0} when the projectile is gone, else one sprite.
type ProjRender = unsafe extern "system" fn(usize, usize, usize, usize, usize) -> usize;

/// The Animated projectiles' render (Build::proj_render): as the game draws it, then its dense sprite shrunk.
unsafe extern "system" fn proj_detour(out: usize, sys: usize, list: usize, assets: usize, id: usize) -> usize {
    let f: ProjRender = std::mem::transmute(ORIG_PROJ.load(Ordering::Acquire));
    let r = f(out, sys, list, assets, id);
    let _ = std::panic::catch_unwind(|| unsafe { shrink_sprites(out, None, Pic::Projectile) });
    r
}

/// The ThreePhase projectiles' render (Build::proj_render3), the same way.
unsafe extern "system" fn proj3_detour(out: usize, sys: usize, list: usize, assets: usize, id: usize) -> usize {
    let f: ProjRender = std::mem::transmute(ORIG_PROJ3.load(Ordering::Acquire));
    let r = f(out, sys, list, assets, id);
    let _ = std::panic::catch_unwind(|| unsafe { shrink_sprites(out, None, Pic::Projectile) });
    r
}

/// The drawn effects' draw log, `PIC` lines (league.dll 0.9.16; the module's notes say why): lines in all a session.
const PIC_LINES: usize = 600;
/// Appearances of one drawn effect logged in full (their first two draws and the first a second in), and summed up
/// (draws, seconds) when they are gone.
const PIC_FULL: usize = 6;
const PIC_SUMS: usize = 16;
/// A picture not drawn for this long has gone: its next draw starts a new appearance.
const PIC_GAP: f64 = 0.5;
/// The tally of appearances: at most once a minute, written when one of them is drawn.
const PIC_TALLY: f64 = 60.0;
/// Body-draw command lists with an effect's own pair inside, logged a session (one line a new shape).
const PIC_BODY_LISTS: usize = 24;
/// Commands shown of one node's list.
const PIC_CMDS: usize = 16;

static PIC_DONE: AtomicBool = AtomicBool::new(false);
static PICS: Mutex<PicLog> = Mutex::new(PicLog::new());

thread_local! {
    /// The entity value whose body the game is drawing on this thread (0 outside the body draw): an effect drawn inside
    /// it is one of that unit's own view nodes.
    static IN_BODY: Cell<usize> = const { Cell::new(0) };
}

/// One picture's (or animation's) appearances: `key` is `<sheet>:<tag>`.
#[derive(Debug)]
struct Shown {
    key: String,
    shows: usize,
    first: f64,
    last: f64,
    draws: usize,
    in_body: usize,
    /// the draw a second in was met in this appearance
    mid: bool,
    /// this appearance is logged in full
    full: bool,
    /// appearances since the last tally
    tally: usize,
}

/// What a draw is to its picture's appearances.
#[derive(Debug, PartialEq)]
enum Step {
    /// the first draw of appearance `show`; `gone`: the last appearance's (show, draws, of them in a body draw, seconds)
    New { show: usize, gone: Option<(usize, usize, usize, f64)> },
    /// the `draw`-th draw of appearance `show`; `mid`: the first a second or more in
    Again { show: usize, draw: usize, mid: bool },
}

/// A draw of `key` at `now` (seconds) in the list of appearances -> its entry and what the draw is.
fn step(list: &mut Vec<Shown>, key: &str, now: f64, in_body: bool) -> (usize, Step) {
    let i = match list.iter().position(|s| s.key == key) {
        Some(i) => i,
        None => {
            list.push(Shown { key: key.to_string(), shows: 0, first: now, last: f64::NEG_INFINITY, draws: 0, in_body: 0,
                              mid: false, full: false, tally: 0 });
            list.len() - 1
        }
    };
    let s = &mut list[i];
    let what = if now - s.last > PIC_GAP {
        let gone = (s.shows > 0).then_some((s.shows, s.draws, s.in_body, s.last - s.first));
        s.shows += 1;
        s.tally += 1;
        (s.first, s.draws, s.in_body, s.mid, s.full) = (now, 0, 0, false, false);
        Step::New { show: s.shows, gone }
    } else {
        let mid = !s.mid && now - s.first >= 1.0;
        s.mid |= mid;
        Step::Again { show: s.shows, draw: s.draws + 1, mid }
    };
    s.draws += 1;
    s.in_body += usize::from(in_body);
    s.last = now;
    (i, what)
}

struct PicLog {
    t0: Option<Instant>,
    lines: usize,
    shown: Vec<Shown>,
    /// (drawn effect, appearances logged in full, summed up)
    budget: Vec<(&'static str, usize, usize)>,
    tallied: f64,
    /// body-draw list shapes logged
    lists: Vec<String>,
}

impl PicLog {
    const fn new() -> Self {
        PicLog { t0: None, lines: 0, shown: Vec::new(), budget: Vec::new(), tallied: 0.0, lists: Vec::new() }
    }

    /// `line` in the log while the budget lasts (false once it is spent: the log is over).
    fn write(&mut self, line: String) -> bool {
        if self.lines >= PIC_LINES {
            PIC_DONE.store(true, Ordering::Relaxed);
            return false;
        }
        self.lines += 1;
        wlog(line);
        if self.lines == PIC_LINES {
            wlog(format!("PIC: the draw log's {PIC_LINES} lines are spent for this session"));
            PIC_DONE.store(true, Ordering::Relaxed);
        }
        true
    }
}

/// The drawn effect a sheet or sprite name is (`asset/league/champions/league_yone#sheet` -> league_yone).
fn drawn_of(heroes: &hd::Heroes, name: &str) -> Option<&'static str> {
    heroes.dense_of_name(name).filter(|h| heroes.drawn_effects.contains(&h.id)).map(|h| h.id)
}

/// Whether an effect sheet goes with a drawn effect's hero (`league_yone_sym` with `league_yone`): the tally's other
/// animations.
pub fn related(drawn: &[&str], sheet: &str) -> bool {
    drawn.iter().any(|d| sheet.len() > d.len() + 1 && sheet.starts_with(d) && sheet.as_bytes()[d.len()] == b'_')
}

unsafe fn rf(addr: usize) -> f32 {
    std::ptr::read_unaligned(addr as *const f32)
}

/// The command Vec {cap, ptr, len} at `out` as (ptr, len); None for the caller's None (cap usize::MAX) or a list that
/// does not look like one.
unsafe fn cmd_list(out: usize) -> Option<(usize, usize)> {
    if !plausible(out) {
        return None;
    }
    let (cap, ptr, len) = (q(out), q(out + 8), q(out + 0x10));
    (cap != usize::MAX && len <= 256 && cap >= len && plausible(ptr)).then_some((ptr, len))
}

/// A command as the log shows it (`c`: its 0xd0 bytes, `name` the sprite's texture): a sprite's sheet, top-left corner
/// (+0x78 / +0x7c), layer (+0x80, the node's) and the four numbers before the corner; a scale's translation (+8 / +0xc),
/// factors (+0x24 / +0x28) and what lies between; `*` marks the pair this pack put round an effect.
pub fn cmd_text(c: &[u8], name: Option<&str>) -> String {
    let u = |at: usize| u64::from_le_bytes(c[at..at + 8].try_into().unwrap());
    let f = |at: usize| f32::from_le_bytes(c[at..at + 4].try_into().unwrap());
    let ours = if u(OURS_AT) == OURS { "*" } else { "" };
    match u(0) {
        CMD_SPRITE => format!("sprite {} corner ({:.1}, {:.1}) layer {} [{:.3} {:.3} {:.3} {:.3}]{ours}",
            name.and_then(|n| n.rsplit('/').next()).unwrap_or("?"), f(0x78), f(0x7c),
            i32::from_le_bytes(c[0x80..0x84].try_into().unwrap()), f(0x68), f(0x6c), f(0x70), f(0x74)),
        t if t == scale_tag() => format!("scale{ours} +({:.1}, {:.1}) x({:.3}, {:.3}) [{:.3} {:.3} {:.3} {:.3} {:.3}]",
            f(8), f(0xc), f(0x24), f(0x28), f(0x10), f(0x14), f(0x18), f(0x1c), f(0x20)),
        t if t == restore_tag() => format!("restore{ours}"),
        t => format!("cmd {:#x}{ours}", t & 0xff),
    }
}

/// Where a node is drawn: the world's view nodes, or the body draw of the entity value `ent`.
unsafe fn path_text(ent: usize) -> String {
    if ent == 0 || !plausible(ent) {
        return "world's view nodes".to_string();
    }
    format!("in the body draw of {} (drawn as {}) at ({:.1}, {:.1}), draw scale {:.3}",
        string_at(ent + NAME_PTR, ent + NAME_LEN_AT).unwrap_or("?"), string_at(ent + RES_PTR, ent + RES_LEN_AT).unwrap_or("?"),
        rf(ent + POS_X), rf(ent + POS_Y) - rf(ent + POS_LIFT), rf(ent + SCALE))
}

/// A node draw for the draw log: `out` the commands the game made (shrink_effects's pair already round a drawn
/// effect), `node` the view node (0.7.1: the kind at +0; a delayed one (2) holds its node at +8 and draws nothing while
/// +4 > 0; an Animation (3, 4) has its flip at +1, point at +4 / +8, time at +0xc, layer at +0x10, sheet String at
/// +0x18 and tag String at +0x30).
unsafe fn note_picture(out: usize, node: usize) {
    if !plausible(node) {
        return;
    }
    let heroes = hd::heroes();
    if heroes.drawn_effects.is_empty() {
        return;
    }
    let (mut n, mut waits) = (node, false);
    for _ in 0..4 {
        if *(n as *const u8) != 2 {
            break;
        }
        if rf(n + 4) > 0.0 {
            waits = true;
            break;
        }
        let inner = q(n + 8);
        if !plausible(inner) {
            return;
        }
        n = inner;
    }
    let kind = *(n as *const u8);
    let animation = !waits && (kind == 3 || kind == 4);
    let anim = if animation { string_at(n + 0x20, n + 0x28) } else { None };
    let list = cmd_list(out);
    // the picture: a drawn effect's sprite among the commands, else the node's own sheet
    let picture = list
        .and_then(|(p, len)| (0..len).find_map(|i| sprite_name(p + i * CMD).and_then(|nm| drawn_of(heroes, nm))))
        .or_else(|| anim.and_then(|a| drawn_of(heroes, a)));
    let sheet = anim.and_then(|a| a.rsplit('/').next()).and_then(|l| l.split('#').next());
    if picture.is_none() && !sheet.is_some_and(|s| related(&heroes.drawn_effects, s)) {
        return;
    }
    let Ok(mut pl) = PICS.try_lock() else { return };
    let now = pl.t0.get_or_insert_with(Instant::now).elapsed().as_secs_f64();
    let ent = IN_BODY.with(Cell::get);
    let tag = if animation { string_at(n + 0x38, n + 0x40) } else { None };
    let key = format!("{}:{}", picture.or(sheet).unwrap_or("?"), tag.unwrap_or("?"));
    let (i, what) = step(&mut pl.shown, &key, now, ent != 0);
    let mut lines = Vec::new();
    if let Some(id) = picture {
        let b = match pl.budget.iter().position(|b| b.0 == id) {
            Some(b) => b,
            None => {
                pl.budget.push((id, 0, 0));
                pl.budget.len() - 1
            }
        };
        let label = match what {
            Step::New { show, gone } => {
                if let Some((s, d, inb, secs)) = gone {
                    if pl.budget[b].2 < PIC_SUMS {
                        pl.budget[b].2 += 1;
                        lines.push(format!("PIC {key} #{s} gone: drawn {d} times over {secs:.2} s, {inb} of them in a body draw"));
                    }
                }
                let full = pl.budget[b].1 < PIC_FULL;
                pl.budget[b].1 += usize::from(full);
                pl.shown[i].full = full;
                full.then(|| format!("#{show} first draw"))
            }
            Step::Again { show, draw, mid } if pl.shown[i].full && (draw == 2 || mid) => {
                Some(format!("#{show} draw {draw}{}", if mid { ", a second in" } else { "" }))
            }
            Step::Again { .. } => None,
        };
        if let Some(label) = label {
            let node_text = if waits {
                "node delayed, nothing drawn yet".to_string()
            } else if animation {
                format!("node kind {kind} flip {} at ({:.1}, {:.1}) time {:.2} layer {}", *((n + 1) as *const u8), rf(n + 4),
                    rf(n + 8), rf(n + 0xc), std::ptr::read_unaligned((n + 0x10) as *const i32))
            } else {
                format!("node kind {kind}")
            };
            let cmds = match list {
                Some((p, len)) => {
                    let shown: Vec<String> = (0..len.min(PIC_CMDS))
                        .map(|j| {
                            let c = p + j * CMD;
                            cmd_text(std::slice::from_raw_parts(c as *const u8, CMD), sprite_name(c))
                        })
                        .collect();
                    format!("{len} commands [{}]", shown.join(", "))
                }
                None => "no commands".to_string(),
            };
            lines.push(format!("PIC {key} {label}: {} | {node_text} | {cmds}", path_text(ent)));
        }
    }
    if now - pl.tallied >= PIC_TALLY {
        let since = now - pl.tallied;
        let counts: Vec<String> = pl.shown.iter_mut().filter(|s| s.tally > 0)
            .map(|s| {
                let c = format!("{} x{}", s.key, s.tally);
                s.tally = 0;
                c
            })
            .collect();
        pl.tallied = now;
        if !counts.is_empty() {
            lines.push(format!("PIC appearances in the last {since:.0} s: {}", counts.join(", ")));
        }
    }
    for l in lines {
        if !pl.write(l) {
            break;
        }
    }
}

/// A body draw's command list with an effect's own pair inside (`ours`), as unshrink_extras sorted it: one line for
/// each new shape (0 an extra, 1 the hero's sheet, 2 the game's scale or restore, o this pack's pair).
fn note_body_list(hero: &str, kinds: &[u8], ours: &[bool], runs: &[(usize, usize)], k: f32) {
    let shape: String = kinds.iter().zip(ours).map(|(&kd, &o)| if o { 'o' } else { char::from(b'0' + kd) }).collect();
    let Ok(mut pl) = PICS.try_lock() else { return };
    let key = format!("{hero} {shape}");
    if pl.lists.len() >= PIC_BODY_LISTS || pl.lists.contains(&key) {
        return;
    }
    pl.lists.push(key);
    pl.write(format!("PIC {hero}: body draw commands {shape} (0 extra, 1 his sheet, 2 the game's scale, o this pack's pair \
                      round an effect), the extras back to the game's size in runs {runs:?} (x{k:.3})"));
}

/// The instances of the buff `name` on the entity value `ent` (its buff list: {ptr, len} at +0xb8, 0x28 bytes an entry,
/// the name's String at +8; league_nasus reads its form the same way).
unsafe fn stacks(ent: usize, name: &str) -> usize {
    let (bp, bn) = (q(ent + BUFFS_PTR), q(ent + BUFFS_LEN));
    if !plausible(bp) || bn > 4096 {
        return 0;
    }
    (0..bn)
        .filter(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            plausible(p) && n == name.len() && std::slice::from_raw_parts(p as *const u8, n) == name.as_bytes()
        })
        .count()
}

/// The names of the buffs on the entity value `ent` (its buff list, as `stacks` reads it).
unsafe fn buff_names(ent: usize) -> Vec<String> {
    let (bp, bn) = (q(ent + BUFFS_PTR), q(ent + BUFFS_LEN));
    if !plausible(bp) || bn > 4096 {
        return Vec::new();
    }
    (0..bn)
        .filter_map(|k| {
            let b = bp + k * BUFF_SIZE;
            let (p, n) = (q(b + 8), q(b + 0x10));
            (plausible(p) && n <= 256).then(|| String::from_utf8_lossy(std::slice::from_raw_parts(p as *const u8, n)).into_owned())
        })
        .collect()
}

/// Whether a growing body's state `n` (its stacks; 1 / 0 for a form on / off) is new for the entity value `ent`: one
/// line a change, within the growth lines' own budget.
fn note_grow(st: &mut State, ent: usize, n: usize) -> bool {
    if st.grows.iter().any(|e| e.0 == ent && e.1 == n) || st.grow_lines >= GROW_LINES {
        return false;
    }
    st.grows.retain(|e| e.0 != ent);
    st.grows.push((ent, n));
    if st.grows.len() > 64 {
        st.grows.remove(0);
    }
    st.grow_lines += 1;
    true
}

/// The point a growing body is scaled about: its soles, hd::FEET game pixels under the unit's position - in the body
/// draw's own coordinates, where the dense frame is still PPU times its shown size.
pub fn soles(px: f32, py: f32, ppu: f32) -> (f32, f32) {
    (px, py + hd::FEET * ppu)
}

/// [first, last] runs of the body's own commands (1).
pub fn body_runs(kinds: &[u8]) -> Vec<(usize, usize)> {
    let flipped: Vec<u8> = kinds.iter().map(|&k| u8::from(k != 1)).collect();
    extra_runs(&flipped)
}

fn install(b: &Build) -> Result<(usize, usize), String> {
    let module = unsafe { GetModuleHandleW(std::ptr::null()) };
    if module == 0 {
        return Err("no module handle".into());
    }
    let slot = module + b.display_slot;
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
pub fn install_once(b: &'static Build) {
    HOOK.call_once(|| {
        let module = unsafe { GetModuleHandleW(std::ptr::null()) };
        match install(b) {
            Ok((slot, prev)) => wlog(format!(
                "battlefield scale on: display slot {slot:#x} now calls this pack, then {} ({prev:#x})",
                if prev == module + b.display_fn { "the game's own handler" } else { "another mod's handler (chained)" }
            )),
            Err(e) => wlog(format!("battlefield scale off ({e})")),
        }
        GROW.store(module + b.cmd_grow, Ordering::Release);
        CMD_SCALE.store(b.cmd_scale, Ordering::Relaxed);
        CMD_RESTORE.store(b.cmd_restore, Ordering::Relaxed);
        let r = unsafe {
            super::lookup::hook(module + b.body_draw,
                body_detour as unsafe extern "system" fn(usize, usize, usize, usize, usize, usize, usize, usize) -> usize
                    as usize, &ORIG_BODY)
        };
        wlog(format!("body draw hooked ({r:?}): shadows, rings and marks round a dense hero at the game's size"));
        let body_ok = r.is_ok();
        let mut effect_ok = false;
        if b.effect_draw != 0 {
            let r = unsafe {
                super::lookup::hook_keeping_r9(module + b.effect_draw,
                    effect_detour as EffectDraw as usize, &ORIG_EFFECT)
            };
            effect_ok = r.is_ok();
            // the host's own table's (a guest's come in later and are shrunk the same)
            let drawn = &hd::heroes().drawn_effects;
            wlog(format!("effect draw hooked ({r:?}): {} at 1 / PPU",
                         if drawn.is_empty() { "the drawn effects".to_string() } else { drawn.join(", ") }));
        }
        // the projectiles' pictures (2026-11-09, the effects PPU): the renders the data's view_projectiles play, each
        // reading r9 (the assets) and a fifth argument
        let mut proj_ok = false;
        for (rva, detour, orig, what) in [(b.proj_render, proj_detour as ProjRender, &ORIG_PROJ, "Animated"),
                                          (b.proj_render3, proj3_detour as ProjRender, &ORIG_PROJ3, "ThreePhase")] {
            if rva == 0 {
                wlog(format!("{what} projectiles' render not known: their dense pictures are not shrunk"));
                continue;
            }
            let r = unsafe { super::lookup::hook_keeping_r9(module + rva, detour as usize, orig) };
            proj_ok |= what == "Animated" && r.is_ok();
            wlog(format!("{what} projectiles' render hooked ({r:?})"));
        }
        // the full effects (a hero's whole effect sheets dense: view effects, buffs and projectiles) only with all three
        let on = body_ok && effect_ok && proj_ok;
        hd::set_full_on(on);
        let full = &hd::heroes().full_effects;
        if !full.is_empty() {
            wlog(format!("full effects {}: {}", if on { "dense (buff and projectile pictures shrunk too)" } else {
                "at 1x (a draw they need was not hooked)" }, full.join(", ")));
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_scale_is_divided_once() {
        let s = next_scale(None, 1.0, 3.0);
        assert_eq!(s, Scale { base: 1.0, wrote: 1.0 / 3.0 });
        let s = next_scale(Some(s), 1.0 / 3.0, 3.0); // the game left our value
        assert_eq!(s.base, 1.0);
        let s = next_scale(Some(s), 1.0, 3.0); // the game wrote its own again
        assert_eq!(s.base, 1.0);
        let s = next_scale(Some(s), 1.5, 3.0); // a new base (a growth effect)
        assert_eq!(s, Scale { base: 1.5, wrote: 0.5 });
    }

    #[test]
    fn an_effects_own_scale_pair_is_part_of_the_extras() {
        let ours = scale_cmd(0.75, 10.0, -20.0, true);
        let mark = u64::from_le_bytes(ours[OURS_AT..].try_into().unwrap());
        assert_eq!(cmd_kind(scale_tag(), mark, false), 0);
        let back = restore_cmd(true);
        assert_eq!(cmd_kind(restore_tag(), u64::from_le_bytes(back[OURS_AT..].try_into().unwrap()), false), 0);
        // the game's own scale commands and the body's sheet as before
        assert_eq!(cmd_kind(scale_tag(), 0, false), 2);
        assert_eq!(cmd_kind(restore_tag(), 0, false), 2);
        assert_eq!(cmd_kind(CMD_SPRITE, 0, true), 1);
        assert_eq!(cmd_kind(CMD_SPRITE, 0, false), 0);
        // body, [ours: scale, effect, restore], shadow: one run of extras round the effect and its pair
        assert_eq!(extra_runs(&[1, 0, 0, 0, 0]), vec![(1, 4)]);
        // x' = k x + (1 - k) p: the corner stays where it is
        let f = |at: usize| f32::from_le_bytes(ours[at..at + 4].try_into().unwrap());
        assert_eq!((f(8), f(12), f(0x24), f(0x28)), (2.5, -5.0, 0.75, 0.75));
        assert_eq!(&scale_cmd(2.0, 1.0, 1.0, false)[OURS_AT..], &[0u8; 8]);
    }

    /// The draw log (league.dll 0.9.16): a picture's appearances told apart by a gap, each counted on its own.
    #[test]
    fn a_pictures_appearances_are_told_apart() {
        let mut l = Vec::new();
        let body = "league_yone:e_body";
        assert_eq!(step(&mut l, body, 10.0, false), (0, Step::New { show: 1, gone: None }));
        assert_eq!(step(&mut l, body, 10.016, false).1, Step::Again { show: 1, draw: 2, mid: false });
        assert_eq!(step(&mut l, body, 10.5, false).1, Step::Again { show: 1, draw: 3, mid: false });
        assert_eq!(step(&mut l, body, 11.0, true).1, Step::Again { show: 1, draw: 4, mid: true });
        assert_eq!(step(&mut l, body, 11.4, false).1, Step::Again { show: 1, draw: 5, mid: false }, "one line a second in");
        // not drawn for more than PIC_GAP: a new appearance, with the last one's numbers
        match step(&mut l, body, 14.0, false).1 {
            Step::New { show: 2, gone: Some((1, 5, 1, secs)) } => assert!((secs - 1.4).abs() < 1e-9, "{secs}"),
            other => panic!("{other:?}"),
        }
        assert_eq!(step(&mut l, body, 14.4, false).1, Step::Again { show: 2, draw: 2, mid: false });
        assert_eq!(step(&mut l, body, 14.8, false).1, Step::Again { show: 2, draw: 3, mid: false });
        assert_eq!(step(&mut l, body, 15.1, false).1, Step::Again { show: 2, draw: 4, mid: true });
        // another picture keeps its own count; the tally counts appearances
        assert_eq!(step(&mut l, "league_leblanc_clone:idle", 15.1, false), (1, Step::New { show: 1, gone: None }));
        assert_eq!(l.iter().map(|s| s.tally).collect::<Vec<_>>(), vec![2, 1]);
    }

    #[test]
    fn the_draw_log_shows_the_commands() {
        assert_eq!(cmd_text(&scale_cmd(0.5, 10.0, 20.0, true), None),
                   "scale* +(5.0, 10.0) x(0.500, 0.500) [0.000 0.000 0.000 0.000 0.000]");
        assert_eq!(cmd_text(&restore_cmd(true), None), "restore*");
        assert_eq!(cmd_text(&restore_cmd(false), None), "restore");
        let mut c = [0u8; CMD];
        c[..8].copy_from_slice(&CMD_SPRITE.to_le_bytes());
        c[0x78..0x7c].copy_from_slice(&279.21f32.to_le_bytes());
        c[0x7c..0x80].copy_from_slice(&664.73f32.to_le_bytes());
        c[0x80..0x84].copy_from_slice(&1i32.to_le_bytes());
        assert_eq!(cmd_text(&c, Some("asset/league/champions/league_yone#sheet")),
                   "sprite league_yone#sheet corner (279.2, 664.7) layer 1 [0.000 0.000 0.000 0.000]");
        // the tally's other animations: the hero's other effect sheets
        let drawn = ["league_yone", "league_azir_soldier"];
        assert!(related(&drawn, "league_yone_sym") && related(&drawn, "league_yone_fx"));
        assert!(!related(&drawn, "league_yone") && !related(&drawn, "league_yonex") && !related(&drawn, "league_yon"));
        assert!(!related(&drawn, "league_yone_"));
    }

    #[test]
    fn only_the_heros_own_sheet_is_the_body() {
        assert!(is_body("asset/league/champions/league_ashe#sheet", "league_ashe"));
        assert!(is_body("asset/base/aseprite_resources/champions/league_ashe#sheet", "league_ashe"));
        assert!(!is_body("asset/base/sprite/circle", "league_ashe"));
        assert!(!is_body("asset/base/aseprite_resources/skill_effect/stun_effect#sheet", "league_ashe"));
        assert!(!is_body("asset/league/champions/league_ashe_fx#sheet", "league_ashe"));
    }

    #[test]
    fn a_set_over_drops_its_entities_scale_records() {
        let s = Scale { base: 1.15, wrote: 0.958 };
        let mut scales = vec![(1, 18, s), (1, 939, s), (2, 939, s)];
        keep_seen(&mut scales, 1, &[18, 20]);
        assert_eq!(scales, vec![(1, 18, s), (2, 939, s)], "world 1's #939 is gone; another world's stays");
    }

    #[test]
    fn a_growing_body_is_scaled_about_its_soles() {
        assert_eq!(body_runs(&[0, 1, 1, 0, 2, 1]), vec![(1, 2), (5, 5)]);
        assert_eq!(body_runs(&[0, 2, 0]), vec![]);
        assert_eq!(soles(100.0, 50.0, 1.2), (100.0, 50.0 + 11.5 * 1.2));
        assert_eq!(hd::grown(0.05, 0), 1.0);
        assert!((hd::grown(0.05, 4) - 1.2).abs() < 1e-6);
        // Cho'Gath: 30 % a bite (2026-10-26), with no cap (2026-10-31); half that from the 5th bite (2026-11-03: 「大虫子在
        // 局内后期变的有点太大了」 - 9 bites were 3.7x)
        assert!((hd::grown(0.30, 1) - 1.3).abs() < 1e-6);
        assert!((hd::grown(0.30, 3) - 1.9).abs() < 1e-6);
        assert!((hd::grown(0.30, 4) - 2.2).abs() < 1e-6);
        assert!((hd::grown(0.30, 5) - 2.35).abs() < 1e-6);
        assert!((hd::grown(0.30, 9) - 2.95).abs() < 1e-6);
        assert!((hd::grown(0.30, 10) - 3.1).abs() < 1e-6);
        // Cho'Gath's growth row is league.dll's data: league_main/src/hd.rs tests it
    }

    #[test]
    fn stacks_on_screen_are_the_add_ons_marks() {
        let s = "league_chogath_r_stack";
        // the display keeps one entry a name: 3 stacks show as one, plus league_chogath's marks for the 2nd and 3rd
        assert_eq!(hd::grow_count([s, "league_chogath_r_stack_2", "league_chogath_r_stack_3", "league_chogath_r_cd"], s), 3);
        assert_eq!(hd::grow_count([s], s), 1);
        // no stack: a stale mark alone draws nothing; other buffs that share the start do not count
        assert_eq!(hd::grow_count(["league_chogath_r_stack_2"], s), 0);
        assert_eq!(hd::grow_count([s, "league_chogath_r_stacked", "league_chogath_r_stack_x"], s), 1);
        // a display that keeps every entry: the entries themselves
        assert_eq!(hd::grow_count([s, s, s, "league_chogath_r_stack_2"], s), 3);
    }

    #[test]
    fn a_form_body_eases_in_and_out() {
        let (size, secs) = (1.35, 1.25);
        // never drawn or stale: straight at the size (a match view opened in the middle of his form)
        assert_eq!(hd::eased(None, size, size, secs), size);
        assert_eq!(hd::eased(Some((1.0, hd::FORM_STALE + 0.1)), size, size, secs), size);
        // a 60 fps frame: 0.35 / 1.25 / 60 of the way
        let one = hd::eased(Some((1.0, 1.0 / 60.0)), size, size, secs);
        assert!((one - (1.0 + 0.35 / 1.25 / 60.0)).abs() < 1e-6, "{one}");
        // frame by frame, the whole way in 1.25 s, and no further
        let mut g = 1.0;
        for _ in 0..74 {
            g = hd::eased(Some((g, 1.0 / 60.0)), size, size, secs);
        }
        assert!(g < size && g > 1.34, "{g}");
        for _ in 0..3 {
            g = hd::eased(Some((g, 1.0 / 60.0)), size, size, secs);
        }
        assert_eq!(g, size);
        // the form over: back down at the same pace
        let down = hd::eased(Some((size, 0.25)), 1.0, size, secs);
        assert!((down - (size - 0.07)).abs() < 1e-6, "{down}");
        assert_eq!(hd::eased(Some((1.01, 0.1)), 1.0, size, secs), 1.0);
        // Volibear's form row is league.dll's data: league_main/src/hd.rs tests it
    }

    /// One draw-scale line per hero and base, not per entity (each respawn is a new one: 2026-11-06 the 200 lines were
    /// gone by 1858 s); the body-draw lines keep a budget of their own.
    #[test]
    fn a_draw_scale_is_logged_once_per_hero_and_base() {
        let mut st = State::new();
        assert!(note_scale(&mut st, "league_karthus", 1.0));
        for _ in 0..18 {
            assert!(!note_scale(&mut st, "league_karthus", 1.0), "a respawn: the same hero and base");
        }
        assert!(!note_scale(&mut st, "league_karthus", 1.0001), "the same to a hundredth");
        assert!(note_scale(&mut st, "league_karthus", 1.5), "a growth effect's base");
        assert!(note_scale(&mut st, "tft_brock", 1.12) && note_scale(&mut st, "tft_brock", 1.13));
        assert_eq!(st.scale_lines, 4);
        // the budget runs out for new pairs only, and leaves the body-draw lines theirs
        st.scale_lines = SCALE_LINES;
        assert!(!note_scale(&mut st, "league_alistar", 1.0));
        assert_eq!(st.body_lines, 0);
    }

    #[test]
    fn the_extras_are_wrapped_in_runs() {
        assert_eq!(extra_runs(&[0, 0, 1, 0]), vec![(0, 1), (3, 3)]);
        assert_eq!(extra_runs(&[1]), vec![]);
        assert_eq!(extra_runs(&[0, 2, 0, 1, 1, 0, 0]), vec![(0, 0), (2, 2), (5, 6)]);
    }

    #[test]
    fn the_body_draw_shrinks_a_body_swapped_after_the_update() {
        let k = 2.2;
        // a dense hero the display update shrank this frame: its value kept, no second division
        let up = Scale { base: 1.0, wrote: 1.0 / k };
        assert_eq!(at_draw(Some(up), None, 1.0 / k, Some(k)), AtDraw::Write(up));
        // Viego renamed after the update (it saw league_viego): divided here, from the game's value
        let s = match at_draw(None, None, 1.0, Some(k)) {
            AtDraw::Write(s) => s,
            other => panic!("{other:?}"),
        };
        assert_eq!(s, Scale { base: 1.0, wrote: 1.0 / k });
        // the next frame, the game left our value: the same, not divided again
        assert_eq!(at_draw(None, Some(s), 1.0 / k, Some(k)), AtDraw::Write(s));
        // the game wrote its own value again
        assert_eq!(at_draw(None, Some(s), 1.0, Some(k)), AtDraw::Write(s));
        // possessing another dense hero (another PPU / size) while our value is still there
        assert_eq!(at_draw(None, Some(s), 1.0 / k, Some(3.0)), AtDraw::Write(Scale { base: 1.0, wrote: 1.0 / 3.0 }));
        // a copy with the divided value and no record (the match-result screen): taken as divided, not divided again
        assert_eq!(at_draw(None, None, 1.0 / k, Some(k)), AtDraw::Write(Scale { base: 1.0, wrote: 1.0 / k }));
        assert_eq!(at_draw(None, None, 0.55 / 2.0, Some(2.0)), AtDraw::Write(Scale { base: 0.55, wrote: 0.275 }));
        // a growth effect's value with no record: divided
        assert_eq!(at_draw(None, None, 1.5, Some(k)), AtDraw::Write(Scale { base: 1.5, wrote: 1.5 / k }));
        // the possession over: our value goes, the game's comes back; nothing to do once the game rewrote it
        assert_eq!(at_draw(None, Some(s), 1.0 / k, None), AtDraw::Restore(1.0));
        assert_eq!(at_draw(None, Some(s), 1.0, None), AtDraw::Leave);
        assert_eq!(at_draw(None, None, 1.0, None), AtDraw::Leave);
        // Viego (dense) divided by the update, then a plain victim's body swapped in: the game's value back at once
        let v = Scale { base: 1.0, wrote: 1.0 / 2.447 };
        assert_eq!(at_draw(Some(v), None, 1.0 / 2.447, None), AtDraw::Restore(1.0));
        assert_eq!(at_draw(Some(v), None, 1.0, None), AtDraw::Leave);
    }

    #[test]
    fn a_swapped_body_is_divided_once_frame_after_frame() {
        let k = 2.2;
        // frame 1: the update saw league_viego (nothing), the add-on swapped the body, the body draw divided
        let AtDraw::Write(first) = at_draw(None, None, 1.0, Some(k)) else { panic!() };
        // frame 2, the game left the body draw's value: the update sees the victim with no record of its own
        let s = at_update(None, None, Some(first), 1.0 / k, k);
        assert_eq!(s, Scale { base: 1.0, wrote: 1.0 / k });
        assert_ne!(next_scale(None, 1.0 / k, k).wrote, s.wrote); // without the body draw's record: divided twice
        // frame 2, the game wrote its own value again: the same
        assert_eq!(at_update(None, None, Some(first), 1.0, k), s);
        // the body draw of frame 2 keeps the update's value
        assert_eq!(at_draw(Some(s), Some(first), 1.0 / k, Some(k)), AtDraw::Write(s));
        // from frame 3 the update has its own record
        assert_eq!(at_update(Some(s), Some(s), Some(first), 1.0 / k, k), s);
    }

    /// 2026-11-08 (league.log:2900-2905, m=4152 s3): Neeko's disguise divided twice - `league_neeko 0.400 -> 0.160`,
    /// `league_jinx 0.455 -> 0.207`, `league_gnar 0.667 -> 0.444`. Her own record held the hero drawn before the swap,
    /// and the update took it whatever it wrote.
    #[test]
    fn the_update_divides_from_the_record_that_wrote_the_value() {
        let (neeko, jinx) = (2.5, 2.2);
        let own = Scale { base: 1.0, wrote: 1.0 / neeko }; // the update, as herself
        let drawn = Scale { base: 1.0, wrote: 1.0 / jinx }; // the body draw, disguised as Jinx after the update
        assert_eq!(update_prev(Some(own), Some(own), Some(drawn), 1.0 / jinx), Some(drawn));
        assert_eq!(at_update(Some(own), Some(own), Some(drawn), 1.0 / jinx, jinx), drawn);
        // the old way (its own record first): 0.455 taken for the game's value
        let old = next_scale(Some(own), 1.0 / jinx, jinx);
        assert!((old.base - 0.4545).abs() < 1e-3 && (old.wrote - 0.2066).abs() < 1e-3, "{old:?}");
        // back as herself: the body draw's 0.400 kept (the old way: 0.400 -> 0.160)
        let own = drawn;
        let drawn = Scale { base: 1.0, wrote: 1.0 / neeko };
        assert_eq!(at_update(Some(own), Some(own), Some(drawn), 1.0 / neeko, neeko), drawn);
        // a value none of them wrote is the game's own: a new base
        assert_eq!(update_prev(Some(own), Some(own), Some(drawn), 1.0), None);
        assert_eq!(at_update(Some(own), Some(own), Some(drawn), 1.5, neeko), Scale { base: 1.5, wrote: 0.6 });
        // its own record first when two wrote it (a hero drawn as itself: the body draw kept the update's value)
        let same = Scale { base: 1.0, wrote: 1.0 / neeko };
        assert_eq!(update_prev(Some(same), None, Some(same), 1.0 / neeko), Some(same));
        // the body draw's guard: no record at all and a value at or under a base of 1 divided - a copy, taken as divided
        assert_eq!(at_update(None, None, None, 0.4, neeko), Scale { base: 1.0, wrote: 0.4 });
        assert_eq!(at_update(None, None, None, 1.0, neeko), Scale { base: 1.0, wrote: 0.4 });
        assert_eq!(at_update(None, None, None, 1.5, neeko), Scale { base: 1.5, wrote: 0.6 });
        // with a record (a hero on screen since its first frame) a fresh value is divided, as before
        assert_eq!(at_update(Some(own), None, None, 0.3, neeko).base, 0.3);
    }

    const W: usize = 0x229c_2ce1_f48;
    const V: usize = 0x7000_0000;

    /// One entity frame after frame as the game runs it: the game's update (now and then writing its own value), the
    /// display update (this pack), a body swapper chained after it (league_neeko and league_viego_soul rename the
    /// body's resource), then the body draw - the battlefield draws with what +0x1b4 holds after the body draw.
    struct Screen {
        st: State,
        cur: f32,
    }

    impl Screen {
        fn new(game: f32) -> Self {
            Screen { st: State::new(), cur: game }
        }

        /// One frame: `game` the value the game writes (None: it leaves +0x1b4 alone), `seen` the divisor of the hero
        /// the display update sees (None: no dense frames), `drawn` the one the body draw sees after the swapper ->
        /// what the body is drawn with.
        fn frame(&mut self, game: Option<f32>, seen: Option<f32>, drawn: Option<f32>) -> f32 {
            if let Some(g) = game {
                self.cur = g;
            }
            match seen {
                Some(k) => self.cur = self.st.update_dense(W, 22, V, self.cur, k).s.wrote,
                None => {
                    if let Some(base) = self.st.update_plain(W, 22, V, self.cur) {
                        self.cur = base;
                    }
                }
            }
            match self.st.body(V, self.cur, drawn).0 {
                AtDraw::Write(s) => self.cur = s.wrote,
                AtDraw::Restore(base) => self.cur = base,
                AtDraw::Leave => {}
            }
            self.cur
        }
    }

    #[track_caller]
    fn at(got: f32, want: f32) {
        assert!((got - want).abs() < 1e-5, "drawn at {got}, want {want}");
    }

    /// A body resource swapped after the display update, frame after frame: always the game's value / the PPU of the
    /// hero drawn - Neeko's disguise (2026-11-08), Viego's possession (dense since league.dll 0.8.39), and a plain
    /// dense hero as before.
    #[test]
    fn a_body_swapped_after_the_update_is_drawn_at_one_over_its_ppu() {
        let (neeko, jinx, gnar, ahri) = (2.5, 2.2, 1.5, 2.2);
        let mut sc = Screen::new(1.0);
        for _ in 0..3 {
            at(sc.frame(None, Some(neeko), Some(neeko)), 1.0 / neeko);
        }
        // the disguise starts: the update still sees league_neeko, her add-on renames the body to Jinx's
        at(sc.frame(None, Some(neeko), Some(jinx)), 1.0 / jinx);
        // then both see Jinx; the game leaves the body draw's value (was 0.455 -> 0.207) or writes its own now and then
        for g in [None, None, Some(1.0), None, None] {
            at(sc.frame(g, Some(jinx), Some(jinx)), 1.0 / jinx);
        }
        // back as herself (was 0.400 -> 0.160)
        at(sc.frame(None, Some(jinx), Some(neeko)), 1.0 / neeko);
        for g in [None, Some(1.0), None] {
            at(sc.frame(g, Some(neeko), Some(neeko)), 1.0 / neeko);
        }
        // as Gnar (was 0.667 -> 0.444), then Ahri straight from Gnar, then a hero with no dense frames and back
        at(sc.frame(None, Some(neeko), Some(gnar)), 1.0 / gnar);
        at(sc.frame(None, Some(gnar), Some(gnar)), 1.0 / gnar);
        at(sc.frame(None, Some(gnar), Some(ahri)), 1.0 / ahri);
        at(sc.frame(None, Some(ahri), Some(ahri)), 1.0 / ahri);
        at(sc.frame(None, Some(ahri), None), 1.0);
        at(sc.frame(None, None, None), 1.0);
        at(sc.frame(None, None, Some(neeko)), 1.0 / neeko);
        at(sc.frame(None, Some(neeko), Some(neeko)), 1.0 / neeko);
        // a growth value of the game's own in the middle of it: its own base, divided once
        at(sc.frame(Some(1.1), Some(neeko), Some(jinx)), 1.1 / jinx);
        at(sc.frame(None, Some(jinx), Some(jinx)), 1.1 / jinx);
        at(sc.frame(None, Some(jinx), Some(neeko)), 1.1 / neeko);
        at(sc.frame(None, Some(neeko), Some(neeko)), 1.1 / neeko);

        // Viego (dense) possessing a dense Yasuo, then a plain Amumu, then himself again
        let (viego, yasuo) = (2.447, 2.2);
        let mut sc = Screen::new(1.0);
        at(sc.frame(None, Some(viego), Some(viego)), 1.0 / viego);
        at(sc.frame(None, Some(viego), Some(yasuo)), 1.0 / yasuo);
        for g in [None, Some(1.0), None] {
            at(sc.frame(g, Some(yasuo), Some(yasuo)), 1.0 / yasuo);
        }
        at(sc.frame(None, Some(yasuo), None), 1.0); // Amumu swapped in after the update: the game's value back
        at(sc.frame(None, None, None), 1.0);
        at(sc.frame(None, None, Some(viego)), 1.0 / viego); // the possession over, renamed after the update
        at(sc.frame(None, Some(viego), Some(viego)), 1.0 / viego);

        // a dense hero drawn as itself: as before, whatever the game writes
        let mut sc = Screen::new(1.0);
        for (g, want) in [(None, 1.0), (None, 1.0), (Some(1.0), 1.0), (Some(1.05), 1.05), (None, 1.05), (Some(1.5), 1.5),
                          (None, 1.5), (Some(1.0), 1.0)] {
            at(sc.frame(g, Some(jinx), Some(jinx)), want / jinx);
        }
    }

    /// The update notes a swap (a line in the log, once a pair) only when +0x1b4 held the body draw's value and not its
    /// own: never for a dense hero drawn as itself.
    #[test]
    fn only_a_swapped_body_is_noted() {
        let mut st = State::new();
        let k = 2.2;
        let u = st.update_dense(W, 22, V, 1.0, k);
        assert!(u.changed && !u.kept_drawn);
        let (d, _) = st.body(V, u.s.wrote, Some(k));
        assert_eq!(d, AtDraw::Write(u.s));
        let u2 = st.update_dense(W, 22, V, u.s.wrote, k);
        assert!(!u2.changed && !u2.kept_drawn, "{u2:?}");
        // swapped to a hero of another PPU at the body draw: the next update keeps the body draw's value
        let (d, _) = st.body(V, u.s.wrote, Some(2.5));
        let AtDraw::Write(s) = d else { panic!("{d:?}") };
        let u3 = st.update_dense(W, 22, V, s.wrote, 2.5);
        assert!(!u3.changed && u3.kept_drawn && u3.s == s, "{u3:?}");
    }

    #[test]
    fn a_possessing_viego_is_shrunk_as_his_victim() {
        // league.dll's dense heroes among them (its table: league_main/src/hd.rs; Viego since league.dll 0.8.39), Amumu
        // not
        let league = hd::tests::table("league", &[("league_zeri", 3.0), ("league_yasuo", 2.2), ("league_karma", 2.2),
                                                  ("league_viego", 2.447)]);
        let h = hd::Heroes::of(&[&league]);
        let as_ = |res, id| drawn_as(&h, res, id).map(|h| h.id);
        assert_eq!(as_(Some("league_zeri"), Some("league_viego")), Some("league_zeri"));
        assert_eq!(as_(Some("champions/league_yasuo#anim"), Some("league_viego")), Some("league_yasuo"));
        // the possession over: Viego himself, dense since league.dll 0.8.39
        assert_eq!(as_(Some("league_viego"), Some("league_viego")), Some("league_viego"));
        assert_eq!(as_(Some("league_amumu"), Some("league_viego")), None); // a plain victim (Darius has dense frames since league.dll 0.7.48, Annie since 0.7.150)
        assert_eq!(as_(None, Some("league_karma")), Some("league_karma")); // no resource name read: the id
        assert_eq!(as_(Some("league_karma"), Some("league_karma")), Some("league_karma"));
    }
}
