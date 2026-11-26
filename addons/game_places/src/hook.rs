//! 一个显示钩子给所有整身变身的英雄用（2026-10-20，把 15 个附加包各自换槽、各自每帧走一遍实体表合成一个）。
//!
//! 每个 DLL（附加包合集、league.dll、龙包，或单独装的一个附加包）在显示更新槽（[`crate::display`]）上挂一层：先调用槽里
//! 原来的函数（游戏的、我们别的 DLL 的或别的 mod 的），再把显示世界的实体表走一遍，收成 [`Ent`] 列表，交给每个登记过的
//! 英雄（[`add`]）——每个英雄各自 `catch_unwind`，一个出错不影响别的。
//!
//! 什么时候挂（2026-11-21，用户：「那按你的建议改吧」——和别的 mod 共存不能看谁先加载）：
//! - 晚挂：DLL 在登记英雄之前调 [`defer`]，之后 [`add`] 只登记英雄、先把显示函数和槽找好（这时后面的 mod 还没换过槽），
//!   真正换槽等这个 DLL 的客户端扩展第一次 post_update 调 [`tick`]。那时所有 mod 都加载完了：只认「槽里还是游戏原函数」
//!   才肯挂的 mod（10 月的 transform_core 就是这样）不管排在我们前面还是后面都已经挂好，我们接在它后面，两边的英雄都变身。
//!   没调 [`defer`] 的 DLL（单独装的一个附加包）照旧在 [`add`] 时就换槽。
//! - 被跳过就接回来：[`tick`] 每帧看一眼。比赛的屏幕时钟（[`crate::clock`]，这个 DLL 的客户端扩展喂）走了 3 秒，我们这层
//!   一次也没被调用，就从槽顺着往下找：我们自己各个 DLL 的层看得穿（环境变量 [`HOOKS_ENV`] 记着每层的「原来的函数」放在
//!   哪），找到这个 DLL 自己的层，说明还在链上（只是这会儿画面没更新），不动；碰到别人的函数（看不进去），或者一路到了
//!   游戏原函数，就是后来的谁换了槽却不接着调用我们——在槽的最上面再挂一层，先调用它，再做我们的。一个 DLL 最多挂
//!   [`LAYERS`] 层。
//! - 同一次显示更新里我们的几层可能都被调到（别人又调回我们旧的那层）：只有最外面那层把英雄过一遍，里面的只往下调。
//!
//! 显示世界和实体值的布局（0.6.3 / 0.6.4 / 0.6.5 一样，各附加包以前各抄一份）只在这里：
//! 显示世界 +0x138 的 hashbrown 表（控制字节指针、+0x140 掩码、+0x150 元素数），每格 0x1d0 字节，键是 8 字节实体号，
//! 值从 +8 开始：+0x40 / +0x48 名字（String 指针、长度），+0x68 / +0x70 / +0x78 正在播的动画名（String：容量、指针、
//! 长度），+0xb8 / +0xc0 buff 列表（每个 0x28 字节，名字指针 +8、长度 +0x10）。
//!
//! 身体是怎么画的（0.7.3 的 EXE 反汇编，2026-11-21，查奎因后空翻、拉莫斯滚球时读的）：
//! - 身体绘制（rva 0x2751f90，league.dll 也挂在这里）每帧拿实体值里的动画名和**动画时间**（+0x170，f32 秒）去取帧
//!   （rva 0x2789460：表里按名字找到动作，再按时间数帧）。名字以 `idle`、`run`、`loop` 结尾的循环播，别的播到最后一帧就
//!   停在那一帧。所以钩子换了名字，身体下一帧就照新名字画；换上去的名字循不循环也只看它自己的结尾（`b_run` 循环，
//!   `e_flip_3` 不循环）。
//! - 实体更新（rva 0x2756ae0）每帧 `动画时间 += 播放速度（+0x174，f32）x dt`。
//! - 画在哪：位置 +0x17c / +0x180（f32，千分之一模拟单位），离地 +0x18c。位置只跟着走路和强制位移的事件走；原生代码直接
//!   改坐标（`entity_set_pos`）画面不跟，要等她下一次走路 / 出手才一下跳过去（奎因 0.7.1 的日志：模拟里退了 48000，画面上
//!   整个后空翻都钉在原地）。要画面上连着挪，用强制位移（`CcKindV1::ForceMove`）。

use std::cell::Cell;
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::Mutex;

pub const TABLE: usize = 0x138;
pub const TABLE_MASK: usize = 0x140;
pub const TABLE_ITEMS: usize = 0x150;
pub const ELEM: usize = 0x1d0;
pub const VALUE: usize = 8;
pub const NAME_PTR: usize = 0x40;
pub const NAME_LEN_AT: usize = 0x48;
/// 动画时间（f32 秒）和播放速度（f32）：0.7.3 身体绘制 / 实体更新的反汇编，别的版本没核对过，只拿来读（日志）。
pub const ANIM_TIME: usize = 0x170;
pub const ANIM_SPEED: usize = 0x174;
/// 画在哪（f32，千分之一模拟单位）。
pub const POS_X: usize = 0x17c;
pub const POS_Y: usize = 0x180;
pub const ANIM_CAP: usize = 0x68;
pub const ANIM_PTR: usize = 0x70;
pub const ANIM_LEN: usize = 0x78;
pub const BUFFS_PTR: usize = 0xb8;
pub const BUFFS_LEN: usize = 0xc0;
pub const BUFF_SIZE: usize = 0x28;

/// 实体表的一格：元素地址（键在开头）和实体号。值在 `elem + VALUE`。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Ent {
    pub elem: usize,
    pub key: u64,
}

/// 登记的英雄：每帧拿到显示世界和它的实体列表。
pub type Dresser = unsafe fn(world: usize, ents: &[Ent]);

/// 英雄自己的日志：这个 DLL 的层什么时候挂上、被谁跳过又挂回去，写进每个登记过的英雄的日志。
pub type Log = fn(&str);

struct Hero {
    id: &'static str,
    dress: Dresser,
    log: Log,
}

static HEROES: Mutex<Vec<Hero>> = Mutex::new(Vec::new());

/// 一个 DLL 最多在槽上挂几层：第一层，加上被跳过以后最多再挂回去三次。
pub const LAYERS: usize = 4;

#[allow(clippy::declare_interior_mutable_const)]
const NO_PREV: AtomicUsize = AtomicUsize::new(0);
/// 每层记的「槽里原来的函数」。
static PREVS: [AtomicUsize; LAYERS] = [NO_PREV; LAYERS];
/// 挂进槽里的层数。
static USED: AtomicUsize = AtomicUsize::new(0);
/// 这个 DLL 的英雄被过了几遍（最外面那层每过一遍加一）。
static CALLS: AtomicU64 = AtomicU64::new(0);
/// 晚挂（[`defer`]）。
static DEFER: AtomicBool = AtomicBool::new(false);
/// 显示函数和槽（找一次；[`use_pair`] 可以给）。
static PAIR: Mutex<Option<Result<(usize, usize), String>>> = Mutex::new(None);
/// 第一层挂了没有：(槽, 槽里原来的函数)，或者为什么没挂上。
static FIRST: Mutex<Option<Result<(usize, usize), String>>> = Mutex::new(None);
static WATCH: Mutex<Watch> = Mutex::new(Watch::new());

thread_local! {
    /// 这个线程正在我们几层里面：嵌套进来的里层只往下调，不过英雄。
    static DEPTH: Cell<u32> = const { Cell::new(0) };
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

/// 显示世界实体表里有东西的格子（表的头不像样就是空的）。
///
/// # Safety
/// `world` must be the display world the game handed its display handler.
pub unsafe fn ents(world: usize) -> Vec<Ent> {
    if !plausible(world) {
        return Vec::new();
    }
    let ctrl = q(world + TABLE);
    let mask = q(world + TABLE_MASK);
    let items = q(world + TABLE_ITEMS);
    if items == 0 || !plausible(ctrl) || mask >= 1 << 16 || (mask + 1) & mask != 0 || items > mask + 1 {
        return Vec::new();
    }
    let mut out = Vec::with_capacity(items);
    for i in 0..=mask {
        if *(ctrl as *const u8).add(i) & 0x80 != 0 {
            continue; // empty or deleted
        }
        let elem = ctrl - (i + 1) * ELEM;
        out.push(Ent { elem, key: q(elem) as u64 });
    }
    out
}

type Update = unsafe extern "system" fn(usize, usize, usize, f32);

unsafe extern "system" fn layer0(this: usize, a2: usize, world: usize, dt: f32) {
    run(0, this, a2, world, dt)
}

unsafe extern "system" fn layer1(this: usize, a2: usize, world: usize, dt: f32) {
    run(1, this, a2, world, dt)
}

unsafe extern "system" fn layer2(this: usize, a2: usize, world: usize, dt: f32) {
    run(2, this, a2, world, dt)
}

unsafe extern "system" fn layer3(this: usize, a2: usize, world: usize, dt: f32) {
    run(3, this, a2, world, dt)
}

/// 各层的函数：每层一个，各记各的原函数（[`PREVS`]），所以挂了几层也不会自己调自己转圈。
const LAYER_FNS: [Update; LAYERS] = [layer0, layer1, layer2, layer3];

unsafe fn run(i: usize, this: usize, a2: usize, world: usize, dt: f32) {
    let prev = PREVS[i].load(Ordering::Acquire);
    let outer = DEPTH.try_with(|d| {
        let n = d.get();
        d.set(n + 1);
        n == 0
    })
    .unwrap_or(true);
    if prev != 0 {
        let f: Update = std::mem::transmute(prev);
        f(this, a2, world, dt);
    }
    let _ = DEPTH.try_with(|d| d.set(d.get().saturating_sub(1)));
    if outer {
        CALLS.fetch_add(1, Ordering::Relaxed);
        dress_all(world);
    }
}

fn dress_all(world: usize) {
    let Ok(list) = HEROES.try_lock() else { return };
    if list.is_empty() {
        return;
    }
    let all = match std::panic::catch_unwind(|| unsafe { ents(world) }) {
        Ok(v) => v,
        Err(_) => return,
    };
    for h in list.iter() {
        let f = h.dress;
        let _ = std::panic::catch_unwind(|| unsafe { f(world, &all) });
    }
}

#[cfg(windows)]
unsafe fn write_slot(slot: usize, value: usize) -> Result<(), String> {
    #[link(name = "kernel32")]
    extern "system" {
        fn VirtualProtect(addr: *mut std::ffi::c_void, size: usize, new: u32, old: *mut u32) -> i32;
    }
    let mut old = 0u32;
    if VirtualProtect(slot as *mut std::ffi::c_void, 8, 0x04, &mut old) == 0 {
        return Err("VirtualProtect failed".into());
    }
    std::ptr::write_volatile(slot as *mut usize, value);
    let mut tmp = 0u32;
    VirtualProtect(slot as *mut std::ffi::c_void, 8, old, &mut tmp);
    Ok(())
}

#[cfg(not(windows))]
unsafe fn write_slot(slot: usize, value: usize) -> Result<(), String> {
    std::ptr::write_volatile(slot as *mut usize, value);
    Ok(())
}

/// 在槽上挂这个 DLL 的第 `i` 层：记下槽里原来的函数，槽换成第 `i` 层的函数。返回原来的函数。
unsafe fn put_layer(slot: usize, i: usize) -> Result<usize, String> {
    let cur = q(slot);
    if !plausible(cur) {
        return Err(format!("the slot holds {cur:#x}"));
    }
    publish();
    PREVS[i].store(cur, Ordering::Release);
    write_slot(slot, LAYER_FNS[i] as usize)?;
    USED.store(i + 1, Ordering::Release);
    Ok(cur)
}

/// 进程环境变量：我们各个 DLL 的每一层，`<层的函数>:<它记的原函数放在哪>`（十六进制），用 `;` 隔开。顺着槽往下找自己时
/// 靠它看穿我们自己的层；别人的函数看不穿。
pub const HOOKS_ENV: &str = "LEAGUE_DISPLAY_HOOKS";

static PUBLISHED: std::sync::Once = std::sync::Once::new();

/// 这个 DLL 的各层写进 [`HOOKS_ENV`]（第一次挂层之前，一个 DLL 一次）。
fn publish() {
    PUBLISHED.call_once(|| {
        let mut all = std::env::var(HOOKS_ENV).unwrap_or_default();
        for i in 0..LAYERS {
            let me = format!("{:x}:{:x}", LAYER_FNS[i] as usize, &PREVS[i] as *const AtomicUsize as usize);
            if !all.split(';').any(|e| e == me) {
                if !all.is_empty() {
                    all.push(';');
                }
                all.push_str(&me);
            }
        }
        std::env::set_var(HOOKS_ENV, all);
    });
}

/// 函数 `f` 是我们哪个 DLL 的一层（[`HOOKS_ENV`]），就读出那层记的原函数。
fn prev_of_ours(f: usize) -> Option<usize> {
    let all = std::env::var(HOOKS_ENV).ok()?;
    for e in all.split(';') {
        let Some((a, b)) = e.split_once(':') else { continue };
        let (Ok(a), Ok(b)) = (usize::from_str_radix(a, 16), usize::from_str_radix(b, 16)) else { continue };
        if a == f && plausible(b) {
            return Some(unsafe { (*(b as *const AtomicUsize)).load(Ordering::Acquire) });
        }
    }
    None
}

/// 顺着槽往下找到哪儿为止（[`walk`]）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Chain {
    /// 找到这个 DLL 自己挂着的一层：还在链上。
    Mine,
    /// 到了游戏自己的显示函数，没碰到这个 DLL 的层：被换下去了。
    Game,
    /// 碰到一个别人的函数，看不进去。
    Foreign(usize),
}

/// 从槽里现在的函数 `top` 往下找：`prev_of` 认得我们各个 DLL 的层（给出那层记的原函数），`mine` 是这个 DLL 挂着的层，
/// `game` 是游戏自己的显示函数。
pub fn walk(top: usize, prev_of: &dyn Fn(usize) -> Option<usize>, mine: &[usize], game: usize) -> Chain {
    let mut f = top;
    for _ in 0..64 {
        if mine.contains(&f) {
            return Chain::Mine;
        }
        if f == game {
            return Chain::Game;
        }
        match prev_of(f) {
            Some(p) => f = p,
            None => return Chain::Foreign(f),
        }
    }
    Chain::Foreign(f) // 转圈了：当成看不进去
}

/// 屏幕时钟走了多少 tick（一秒 60）我们一次没被调用，才去查有没有被跳过：3 秒。
pub const QUIET_TICKS: usize = 180;

/// 看我们这层有没有一直被调用。
#[derive(Debug)]
pub struct Watch {
    calls: u64,
    from: Option<usize>,
    full: bool,
}

impl Watch {
    pub const fn new() -> Self {
        Watch { calls: 0, from: None, full: false }
    }

    /// 这一帧：`calls` 我们被调用的总次数，`screen` 屏幕时钟的 tick（不在比赛画面、时钟没走是 None）。屏幕时钟走了
    /// [`QUIET_TICKS`]、我们一次也没被调用 -> true，然后重新计。
    pub fn quiet(&mut self, calls: u64, screen: Option<usize>) -> bool {
        if calls != self.calls {
            self.calls = calls;
            self.from = None;
            return false;
        }
        let Some(t) = screen else {
            self.from = None;
            return false;
        };
        match self.from {
            Some(f) if t >= f => {
                if t - f >= QUIET_TICKS {
                    self.from = None;
                    return true;
                }
                false
            }
            _ => {
                self.from = Some(t); // 头一回，或者换了一场（时钟往回走）
                false
            }
        }
    }
}

impl Default for Watch {
    fn default() -> Self {
        Self::new()
    }
}

/// 槽里原来的函数是谁（日志用）。
fn whom(prev: usize, game: usize) -> String {
    if prev == game {
        format!("the game's own handler ({prev:#x})")
    } else if prev_of_ours(prev).is_some() {
        format!("another of our DLLs' display hook (chained) ({prev:#x})")
    } else {
        format!("another mod's handler (chained) ({prev:#x})")
    }
}

/// [`tick`] 的一帧（槽 `slot`、游戏的显示函数 `game`、屏幕时钟 `screen`）：要写进日志的行。
unsafe fn step(slot: usize, game: usize, screen: Option<usize>) -> Vec<String> {
    let used = USED.load(Ordering::Acquire);
    if used == 0 {
        let mut first = FIRST.lock().unwrap_or_else(|e| e.into_inner());
        // 立刻挂的 DLL 在 add 时挂；晚挂的第一层挂不上也不每帧再试；没有英雄登记就不挂
        if !DEFER.load(Ordering::Acquire) || first.is_some() || count() == 0 {
            return Vec::new();
        }
        let r = put_layer(slot, 0).map(|prev| (slot, prev));
        *first = Some(r.clone());
        return vec![match r {
            Ok((slot, prev)) => format!(
                "display hook in at this DLL's first frame (every mod loaded by now): display slot {slot:#x} now calls it, then {}",
                whom(prev, game)
            ),
            Err(e) => format!("display hook not in at this DLL's first frame ({e})"),
        }];
    }
    let mut w = WATCH.lock().unwrap_or_else(|e| e.into_inner());
    if !w.quiet(CALLS.load(Ordering::Relaxed), screen) {
        return Vec::new();
    }
    let mine: Vec<usize> = LAYER_FNS[..used].iter().map(|f| *f as usize).collect();
    let by = match walk(q(slot), &prev_of_ours, &mine, game) {
        Chain::Mine => return Vec::new(), // 还在链上：只是这会儿画面没更新
        Chain::Game => "the slot leads to the game's own handler without this DLL's layer".to_string(),
        Chain::Foreign(f) => format!("another mod's handler {f:#x} took the slot and does not call this DLL's layer"),
    };
    if used >= LAYERS {
        if w.full {
            return Vec::new();
        }
        w.full = true;
        return vec![format!("display hook skipped ({by}): all {LAYERS} layers are in already, not hooking again")];
    }
    vec![match put_layer(slot, used) {
        Ok(prev) => format!(
            "display hook skipped for {} s of the match clock ({by}): hooked again on top (layer {}), then {}",
            QUIET_TICKS / 60,
            used + 1,
            whom(prev, game)
        ),
        Err(e) => format!("display hook skipped ({by}); hooking again failed ({e})"),
    }]
}

/// 显示函数和槽（找一次）。
fn pair() -> Result<(usize, usize), String> {
    PAIR.lock().unwrap_or_else(|e| e.into_inner()).get_or_insert_with(crate::display).clone()
}

/// 显示函数和槽由调用方给（高清帧引擎按游戏版本的指纹认得它们）：自己没找到（或者还没找）时用这一对。
pub fn use_pair(func: usize, slot: usize) {
    let mut p = PAIR.lock().unwrap_or_else(|e| e.into_inner());
    if !matches!(*p, Some(Ok(_))) {
        *p = Some(Ok((func, slot)));
    }
}

/// 这个 DLL 晚挂：在它登记任何英雄（[`add`]）之前调一次（DLL 的 init 里），它的客户端扩展每帧调 [`tick`]。显示函数和
/// 槽这时就找好（发进环境变量给后面的 DLL：槽一被换就搜不到原指针了）。
pub fn defer() {
    DEFER.store(true, Ordering::Release);
    let _ = pair();
}

/// [`add`] 之后这个 DLL 的层在哪儿（写进日志）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Placed {
    /// 已经挂上：槽、槽里原来的函数、游戏的显示函数。
    Now { slot: usize, prev: usize, game: usize },
    /// 晚挂：等这个 DLL 的第一帧（那时写一行 "display hook in"）。
    Waiting { slot: usize },
}

impl std::fmt::Display for Placed {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match *self {
            Placed::Now { slot, prev, game } => {
                write!(f, "display slot {slot:#x} now calls this DLL's display hook, then {}", whom(prev, game))
            }
            Placed::Waiting { slot } => write!(
                f,
                "display slot {slot:#x}, hooked at this DLL's first frame once every mod has loaded (a \"display hook in\" line follows)"
            ),
        }
    }
}

/// 登记一个英雄（`id` 只用来避免重复登记，`log` 是它自己的日志）。立刻挂的 DLL 第一次登记时换槽；晚挂的（[`defer`]）
/// 等第一帧（[`tick`]）。返回挂得怎么样，或者为什么挂不上。
pub fn add(id: &'static str, f: Dresser, log: Log) -> Result<Placed, String> {
    {
        let mut list = HEROES.lock().unwrap_or_else(|e| e.into_inner());
        if !list.iter().any(|h| h.id == id) {
            list.push(Hero { id, dress: f, log });
        }
    }
    let (game, slot) = pair()?;
    let mut first = FIRST.lock().unwrap_or_else(|e| e.into_inner());
    if DEFER.load(Ordering::Acquire) {
        return Ok(match first.as_ref() {
            Some(Ok((slot, prev))) => Placed::Now { slot: *slot, prev: *prev, game }, // 第一帧过了才登记：已经挂着
            _ => Placed::Waiting { slot },
        });
    }
    first
        .get_or_insert_with(|| unsafe { put_layer(slot, 0) }.map(|prev| (slot, prev)))
        .clone()
        .map(|(slot, prev)| Placed::Now { slot, prev, game })
}

/// 每帧从这个 DLL 的客户端扩展 post_update 调（喂过 [`crate::clock`] 以后）：晚挂的 DLL 第一次调时换槽，之后看有没有被
/// 跳过（见模块说明）。要记的行写进每个登记过的英雄的日志。
pub fn tick() {
    let pair = PAIR.lock().unwrap_or_else(|e| e.into_inner()).get_or_insert_with(crate::display).as_ref().ok().copied();
    let Some((game, slot)) = pair else { return };
    let lines = unsafe { step(slot, game, crate::clock::screen_tick()) };
    if lines.is_empty() {
        return;
    }
    let logs: Vec<Log> = HEROES.lock().map(|l| l.iter().map(|h| h.log).collect()).unwrap_or_default();
    for line in &lines {
        for log in &logs {
            log(line);
        }
    }
}

/// 登记了几个英雄（日志用）。
pub fn count() -> usize {
    HEROES.lock().map(|l| l.len()).unwrap_or(0)
}

/// 槽里原来是不是游戏自己的显示函数（日志用）。
pub fn chained_to_game(prev: usize) -> bool {
    pair().is_ok_and(|d| prev == d.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// 这些测试动的是同一套全局状态（一个 DLL 一套）：一个一个来，开头清空。
    static SERIAL: Mutex<()> = Mutex::new(());

    fn fresh() -> std::sync::MutexGuard<'static, ()> {
        let g = SERIAL.lock().unwrap_or_else(|e| e.into_inner());
        HEROES.lock().unwrap_or_else(|e| e.into_inner()).clear();
        for p in &PREVS {
            p.store(0, Ordering::Release);
        }
        USED.store(0, Ordering::Release);
        CALLS.store(0, Ordering::Release);
        DEFER.store(false, Ordering::Release);
        *FIRST.lock().unwrap_or_else(|e| e.into_inner()) = None;
        *WATCH.lock().unwrap_or_else(|e| e.into_inner()) = Watch::new();
        g
    }

    unsafe fn a(_: usize, _: &[Ent]) {}
    unsafe fn b(_: usize, _: &[Ent]) {}
    fn quiet_log(_: &str) {}

    #[test]
    fn a_hero_is_listed_once() {
        let _g = fresh();
        let _ = add("a", a, quiet_log);
        let _ = add("a", a, quiet_log);
        let _ = add("b", b, quiet_log);
        assert_eq!(count(), 2);
    }

    #[test]
    fn the_walk_sees_through_our_layers_only() {
        // 我们的层：10 -> 20（别的 DLL 的层）-> 30（这个 DLL 的层）-> 99（游戏）
        let ours = |f: usize| match f {
            10 => Some(20),
            20 => Some(30),
            30 => Some(99),
            _ => None,
        };
        assert_eq!(walk(10, &ours, &[30], 99), Chain::Mine);
        assert_eq!(walk(30, &ours, &[30], 99), Chain::Mine);
        // 这个 DLL 的层不在链上了：一路到游戏
        assert_eq!(walk(10, &ours, &[40], 99), Chain::Game);
        // 最上面是别人的函数：看不进去
        assert_eq!(walk(77, &ours, &[30], 99), Chain::Foreign(77));
        // 我们的层下面接着别人的函数
        let into_foreign = |f: usize| (f == 10).then_some(55);
        assert_eq!(walk(10, &into_foreign, &[30], 99), Chain::Foreign(55));
        // 转圈的链不会卡死
        let looped = |f: usize| Some(if f == 1 { 2 } else { 1 });
        assert!(matches!(walk(1, &looped, &[30], 99), Chain::Foreign(_)));
    }

    #[test]
    fn quiet_needs_the_match_clock_to_run_without_calls() {
        let mut w = Watch::new();
        // 不在比赛画面：不算
        for _ in 0..1000 {
            assert!(!w.quiet(0, None));
        }
        // 时钟在走、我们也一直被调用：不算
        for t in 0..1000 {
            assert!(!w.quiet(t as u64 + 1, Some(t)));
        }
        // 时钟走了 179 tick 没被调用：还不算；180：算，然后重新计
        let c = 1000;
        assert!(!w.quiet(c, Some(5000)));
        assert!(!w.quiet(c, Some(5179)));
        assert!(w.quiet(c, Some(5180)));
        assert!(!w.quiet(c, Some(5181)));
        // 换了一场（时钟往回走）：从头计
        assert!(!w.quiet(c, Some(10)));
        assert!(!w.quiet(c, Some(100)));
        assert!(w.quiet(c, Some(190)));
    }

    // 假的游戏：一个槽、游戏的显示函数、别的 mod 的几种挂法，每个函数被调用几次都记下来。
    static SLOT: AtomicUsize = AtomicUsize::new(0);
    static GAME_CALLS: AtomicU64 = AtomicU64::new(0);
    static DRESSED: AtomicU64 = AtomicU64::new(0);
    static STRICT_PREV: AtomicUsize = AtomicUsize::new(0);
    static STRICT_CALLS: AtomicU64 = AtomicU64::new(0);
    static CHAINER_PREV: AtomicUsize = AtomicUsize::new(0);
    static CHAINER_CALLS: AtomicU64 = AtomicU64::new(0);
    static BYPASS_CALLS: AtomicU64 = AtomicU64::new(0);

    unsafe extern "system" fn game(_: usize, _: usize, _: usize, _: f32) {
        GAME_CALLS.fetch_add(1, Ordering::Relaxed);
    }

    /// 只认槽里是游戏原函数才挂、挂了接着调用原来的（10 月 transform_core 的样子）。
    unsafe extern "system" fn strict(this: usize, a2: usize, world: usize, dt: f32) {
        STRICT_CALLS.fetch_add(1, Ordering::Relaxed);
        let f: Update = std::mem::transmute(STRICT_PREV.load(Ordering::Acquire));
        f(this, a2, world, dt);
    }

    fn strict_installs() -> bool {
        let cur = SLOT.load(Ordering::Acquire);
        if cur != game as Update as usize {
            return false;
        }
        STRICT_PREV.store(cur, Ordering::Release);
        SLOT.store(strict as Update as usize, Ordering::Release);
        true
    }

    /// 规矩的：接着调用槽里原来的函数。
    unsafe extern "system" fn chainer(this: usize, a2: usize, world: usize, dt: f32) {
        CHAINER_CALLS.fetch_add(1, Ordering::Relaxed);
        let f: Update = std::mem::transmute(CHAINER_PREV.load(Ordering::Acquire));
        f(this, a2, world, dt);
    }

    fn chainer_installs() {
        CHAINER_PREV.store(SLOT.load(Ordering::Acquire), Ordering::Release);
        SLOT.store(chainer as Update as usize, Ordering::Release);
    }

    /// 不规矩的：换了槽，直接调游戏原函数，跳过槽里原来的。
    unsafe extern "system" fn bypass(this: usize, a2: usize, world: usize, dt: f32) {
        BYPASS_CALLS.fetch_add(1, Ordering::Relaxed);
        game(this, a2, world, dt);
    }

    unsafe fn count_dress(_: usize, _: &[Ent]) {
        DRESSED.fetch_add(1, Ordering::Relaxed);
    }

    fn slot() -> usize {
        &SLOT as *const AtomicUsize as usize
    }

    fn game_fn() -> usize {
        game as Update as usize
    }

    /// 游戏画一帧：调槽里的函数。
    fn frame() {
        let f: Update = unsafe { std::mem::transmute(SLOT.load(Ordering::Acquire)) };
        unsafe { f(0, 0, 0, 0.016) };
    }

    fn reset_game() {
        SLOT.store(game_fn(), Ordering::Release);
        for c in [&GAME_CALLS, &DRESSED, &STRICT_CALLS, &CHAINER_CALLS, &BYPASS_CALLS] {
            c.store(0, Ordering::Release);
        }
    }

    fn counts() -> [u64; 5] {
        [&GAME_CALLS, &DRESSED, &STRICT_CALLS, &CHAINER_CALLS, &BYPASS_CALLS].map(|c| c.load(Ordering::Acquire))
    }

    /// 晚挂的 DLL 登记英雄：用假的槽。
    fn defer_with_fake_slot() {
        DEFER.store(true, Ordering::Release);
        HEROES.lock().unwrap().push(Hero { id: "count", dress: count_dress, log: quiet_log });
    }

    #[test]
    fn a_strict_mod_loaded_after_us_still_hooks() {
        let _g = fresh();
        reset_game();
        // 我们先加载：只登记，不换槽
        defer_with_fake_slot();
        assert_eq!(SLOT.load(Ordering::Acquire), game_fn());
        // 后加载的只认游戏原函数的 mod：照样挂上
        assert!(strict_installs());
        // 第一帧：我们接在它后面
        let lines = unsafe { step(slot(), game_fn(), None) };
        assert_eq!(lines.len(), 1, "{lines:?}");
        assert!(lines[0].contains("first frame") && lines[0].contains("another mod's handler (chained)"), "{lines:?}");
        frame();
        // 游戏、它、我们各一次
        assert_eq!(counts(), [1, 1, 1, 0, 0]);
        // 第二帧不再换槽
        assert!(unsafe { step(slot(), game_fn(), None) }.is_empty());
    }

    #[test]
    fn a_mod_that_skips_us_gets_us_back_on_top() {
        let _g = fresh();
        reset_game();
        defer_with_fake_slot();
        unsafe { step(slot(), game_fn(), None) };
        frame();
        assert_eq!(counts(), [1, 1, 0, 0, 0]);
        // 后来的 mod 换了槽、直接调游戏：我们没了
        SLOT.store(bypass as Update as usize, Ordering::Release);
        let mut t = 6000;
        let mut lines = Vec::new();
        for _ in 0..200 {
            frame();
            lines.extend(unsafe { step(slot(), game_fn(), Some(t)) });
            t += 1;
            if !lines.is_empty() {
                break;
            }
        }
        assert_eq!(lines.len(), 1, "{lines:?}");
        assert!(lines[0].contains("hooked again on top (layer 2)"), "{lines:?}");
        assert_eq!(USED.load(Ordering::Acquire), 2);
        // 现在每帧：我们一次、它一次、游戏一次
        let before = counts();
        frame();
        let after = counts();
        assert_eq!([after[0] - before[0], after[1] - before[1], after[4] - before[4]], [1, 1, 1]);
        // 一直被调用：不再挂
        for _ in 0..400 {
            frame();
            assert!(unsafe { step(slot(), game_fn(), Some(t)) }.is_empty());
            t += 1;
        }
    }

    #[test]
    fn a_mod_that_chains_is_left_alone() {
        let _g = fresh();
        reset_game();
        defer_with_fake_slot();
        unsafe { step(slot(), game_fn(), None) };
        // 后来的规矩 mod：接着调用我们
        chainer_installs();
        let mut t = 100;
        for _ in 0..600 {
            frame();
            assert!(unsafe { step(slot(), game_fn(), Some(t)) }.is_empty());
            t += 1;
        }
        assert_eq!(USED.load(Ordering::Acquire), 1);
        assert_eq!(counts(), [600, 600, 0, 600, 0]);
        // 我们在最上面、画面没更新（时钟在走、谁都没被调用）：顺着链头一个就是自己，不挂
        SLOT.store(layer0 as Update as usize, Ordering::Release);
        CHAINER_PREV.store(game_fn(), Ordering::Release);
        PREVS[0].store(chainer as Update as usize, Ordering::Release);
        for _ in 0..600 {
            assert!(unsafe { step(slot(), game_fn(), Some(t)) }.is_empty());
            t += 1;
        }
    }

    #[test]
    fn nested_layers_dress_once_a_frame() {
        let _g = fresh();
        reset_game();
        defer_with_fake_slot();
        unsafe { step(slot(), game_fn(), None) }; // 第一层：接游戏
        chainer_installs(); // 规矩的 mod 接着我们
        unsafe { put_layer(slot(), 1) }.unwrap(); // 我们又挂一层在它上面（比如误以为被跳过）
        frame();
        // 第二层 -> 它 -> 第一层 -> 游戏：英雄只过一遍
        assert_eq!(counts(), [1, 1, 0, 1, 0]);
        assert_eq!(DEPTH.with(|d| d.get()), 0);
    }

    #[test]
    fn layers_stop_at_the_limit() {
        let _g = fresh();
        reset_game();
        defer_with_fake_slot();
        unsafe { step(slot(), game_fn(), None) };
        let mut t = 1000;
        let mut all = Vec::new();
        for _ in 0..(LAYERS + 2) * 200 {
            // 每次挂上去都马上又被跳过
            SLOT.store(bypass as Update as usize, Ordering::Release);
            frame();
            all.extend(unsafe { step(slot(), game_fn(), Some(t)) });
            t += 1;
        }
        assert_eq!(USED.load(Ordering::Acquire), LAYERS);
        assert_eq!(all.iter().filter(|l| l.contains("hooked again")).count(), LAYERS - 1, "{all:?}");
        assert_eq!(all.iter().filter(|l| l.contains("not hooking again")).count(), 1, "{all:?}");
    }

    #[test]
    fn an_immediate_dll_does_nothing_at_the_frame() {
        let _g = fresh();
        reset_game();
        HEROES.lock().unwrap().push(Hero { id: "count", dress: count_dress, log: quiet_log });
        // 没 defer：第一层该在 add 时挂，tick 不挂
        assert!(unsafe { step(slot(), game_fn(), None) }.is_empty());
        assert_eq!(SLOT.load(Ordering::Acquire), game_fn());
    }

    #[test]
    fn our_other_dlls_layers_are_seen_through() {
        let _g = fresh();
        reset_game();
        defer_with_fake_slot();
        unsafe { step(slot(), game_fn(), None) };
        // 我们的另一个 DLL 后挂上来：它的层接着我们（环境变量里登记它的层和它记原函数的地方）
        static OTHER_PREV: AtomicUsize = AtomicUsize::new(0);
        unsafe extern "system" fn other(this: usize, a2: usize, world: usize, dt: f32) {
            let f: Update = std::mem::transmute(OTHER_PREV.load(Ordering::Acquire));
            f(this, a2, world, dt);
        }
        OTHER_PREV.store(SLOT.load(Ordering::Acquire), Ordering::Release);
        SLOT.store(other as Update as usize, Ordering::Release);
        let entry = format!("{:x}:{:x}", other as Update as usize, &OTHER_PREV as *const AtomicUsize as usize);
        let old = std::env::var(HOOKS_ENV).unwrap_or_default();
        std::env::set_var(HOOKS_ENV, format!("{old};{entry}"));
        // 时钟在走、画面没更新：顺着链看得到我们自己的层，不再挂
        let mut t = 0;
        for _ in 0..600 {
            assert!(unsafe { step(slot(), game_fn(), Some(t)) }.is_empty());
            t += 1;
        }
        assert_eq!(USED.load(Ordering::Acquire), 1);
        std::env::set_var(HOOKS_ENV, old);
    }

    /// Old way (15 hooks, each walking the table) against the shared walk, on a fake display world of 100 entities
    /// (128 slots): `cargo test --release -p game_places one_walk -- --ignored --nocapture`.
    #[test]
    #[ignore]
    fn one_walk_against_fifteen() {
        const SLOTS: usize = 128;
        let names: Vec<Vec<u8>> = (0..100).map(|i| format!("league_hero_{i:03}").into_bytes()).collect();
        let mut mem = vec![0u8; SLOTS * ELEM + SLOTS + 16];
        let ctrl = mem.as_mut_ptr() as usize + SLOTS * ELEM;
        for i in 0..SLOTS {
            let elem = ctrl - (i + 1) * ELEM;
            unsafe { *(ctrl as *mut u8).add(i) = if i < names.len() { 0 } else { 0x80 } };
            if i < names.len() {
                unsafe {
                    std::ptr::write_unaligned(elem as *mut u64, i as u64);
                    std::ptr::write_unaligned((elem + VALUE + NAME_PTR) as *mut usize, names[i].as_ptr() as usize);
                    std::ptr::write_unaligned((elem + VALUE + NAME_LEN_AT) as *mut usize, names[i].len());
                }
            }
        }
        let mut world = vec![0u8; 0x200];
        let w = world.as_mut_ptr() as usize;
        unsafe {
            std::ptr::write_unaligned((w + TABLE) as *mut usize, ctrl);
            std::ptr::write_unaligned((w + TABLE_MASK) as *mut usize, SLOTS - 1);
            std::ptr::write_unaligned((w + TABLE_ITEMS) as *mut usize, names.len());
        }
        let heroes: Vec<&[u8]> = (0..15).map(|k| names[k * 6].as_slice()).collect();
        let hit = |elem: usize, want: &[u8]| unsafe {
            let v = elem + VALUE;
            q(v + NAME_LEN_AT) == want.len() && std::slice::from_raw_parts(q(v + NAME_PTR) as *const u8, want.len()) == want
        };
        let frames = 20_000;
        let t0 = std::time::Instant::now();
        let mut found = 0;
        for _ in 0..frames {
            for h in &heroes {
                found += unsafe { ents(w) }.iter().filter(|e| hit(e.elem, h)).count();
            }
        }
        let old = t0.elapsed();
        let t1 = std::time::Instant::now();
        for _ in 0..frames {
            let all = unsafe { ents(w) };
            for h in &heroes {
                found += all.iter().filter(|e| hit(e.elem, h)).count();
            }
        }
        let new = t1.elapsed();
        assert_eq!(found, 2 * frames * 15);
        eprintln!("per frame: 15 walks {:.2} us, one walk {:.2} us",
                  old.as_secs_f64() * 1e6 / frames as f64, new.as_secs_f64() * 1e6 / frames as f64);
    }

    #[test]
    fn a_world_that_is_no_pointer_has_no_entities() {
        assert!(unsafe { ents(0) }.is_empty());
    }
}
