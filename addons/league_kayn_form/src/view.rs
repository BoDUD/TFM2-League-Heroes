//! 完整变身：变身后凯隐站着、跑着、挨打、阵亡也是形态的样子（主包只能换出招的动作，游戏按名字自动播的
//! idle / run / hit / dead 数据换不了）。只在游戏 0.6.2（Windows）上生效，别的版本什么都不做，退回半变身。
//!
//! 游戏每一帧画单位时，用单位显示数据里的名字现拼精灵：`asset/base/aseprite_resources/champions/{名字}#sheet`
//! / `#anim`，再经过资源重定向表找到 mod 的图（game-view\src\view\entity.rs，rva 0x1fbecb0；拼路径的函数 rva
//! 0x1fbaa80，名字是显示数据 +0x50 处的字符串：指针 +0x58、长度 +0x60）。凯隐的名字缓冲区一局里不变，
//! 把 `league_kayn` 的最后一个字母改成 `d` / `s`，画出来的就是 `league_kayd` / `league_kays`：本包的
//! `mod.override_info` 把这两个名字的精灵送到主包的 `league_kayn_darkin` / `league_kayn_shadow`（凯隐全部的动作，
//! idle / run / hit / dead 换成形态的，tools/art/rig_kayn_forms.py）。
//!
//! 怎么找到那份名字：加载时给 rva 0x1fbaa80 装一个钩子（入口 20 个字节核对无误才装，跳板把每次调用的显示
//! 数据地址记进 256 格的环形表，再执行原来那 20 个字节、跳回去）。客户端扩展每 0.1 秒看一次：被动在画面那一侧的
//! 模拟世界（实况、观战、回放；服务器提前模拟的不算）里写下凯隐现在的形态，和画的不一样就从环形表里找出
//! 名字是 `league_kay?` 的那些（每 0.1 秒从正在画的记录里重新取，旧地址可能已释放），核对 11 个字节后改最后一个字母。
//! 换的时刻跟着屏幕：画面那一侧的模拟比屏幕跑得快（整局先算完再回放），被动记下每次换样子的 tick，扩展读界面上
//! 比赛时钟（ingame.header.game_time.value；死斗是记分板的倒数），时钟走到那个 tick 才换。
//! 开发过程（2026-10-06）：侦察 mod v1–v8，C:\tfm2\scratch\view_probe；第 8 版第一次让凯隐变红。

use std::ffi::c_void;
use std::sync::atomic::{AtomicU8, AtomicUsize, Ordering};
use std::sync::{Mutex, Once};
use std::time::Instant;

use mod_api_stable::*;

use super::wlog;

const RVA: usize = 0x1fbaa80;
/// push rbp; push rsi; push rdi; sub rsp, 0x70; lea rbp, [rsp+0x70]; mov qword [rbp-8], -2 (game 0.6.2)
const ORIG: [u8; 20] = [0x55, 0x56, 0x57, 0x48, 0x83, 0xec, 0x70, 0x48, 0x8d, 0x6c, 0x24, 0x70, 0x48, 0xc7, 0x45, 0xf8,
    0xfe, 0xff, 0xff, 0xff];
/// 凯隐在显示数据里的名字（长度 11），最后一个字母：n 本体、d 暗裔、s 影流。
pub const STEM: &[u8] = b"league_kay";
pub const NAME_LEN: usize = 11;

/// 被动写、扩展读：画面那一侧的模拟里凯隐每次换样子的时刻（tick, 字母）。那一侧的模拟比屏幕快得多——游戏先在
/// 后台把整局算完，屏幕再回放（2026-10-06 日志：真实时间 8 秒里它从 0:00 算到 7:38，凯隐 10 级攒满时屏幕上他才
/// 2 级：「看到没又2级变身了」）——所以不能算到就换，要等屏幕的比赛时钟走到那个 tick。
static TIMELINE: Mutex<Timeline> = Mutex::new(Timeline { key: (u64::MAX, u64::MAX), changes: Vec::new() });

struct Timeline {
    key: (u64, u64), // (对局, 第几场)
    changes: Vec<(usize, u8)>,
}

impl Timeline {
    fn note(&mut self, key: (u64, u64), tick: usize, letter: u8) {
        if key != self.key || self.changes.last().is_some_and(|&(t, _)| tick < t) {
            self.key = key;
            self.changes.clear();
        }
        if self.changes.last().map(|&(_, l)| l) != Some(letter) {
            self.changes.push((tick, letter));
        }
    }

    /// 屏幕时钟走到 `tick` 时的字母（这之前没记过就是 None）。
    fn at(&self, tick: usize) -> Option<u8> {
        self.changes.iter().take_while(|&&(t, _)| t <= tick).last().map(|&(_, l)| l)
    }
}

/// 比赛时钟的文字（"07:38"）→ 秒。
pub fn clock_secs(text: &str) -> Option<usize> {
    let (m, s) = text.trim().split_once(':')?;
    let (m, s): (usize, usize) = (m.trim().parse().ok()?, s.trim().parse().ok()?);
    (s < 60).then_some(m * 60 + s)
}
/// slot 0: 调用次数；1..=256：最近的显示数据地址
static RING: [AtomicUsize; 257] = [const { AtomicUsize::new(0) }; 257];
static HOOK: Once = Once::new();
static HOOKED: AtomicU8 = AtomicU8::new(0);

#[link(name = "kernel32")]
extern "system" {
    fn ReadProcessMemory(h: isize, base: *const c_void, buf: *mut c_void, size: usize, read: *mut usize) -> i32;
    fn WriteProcessMemory(h: isize, base: *mut c_void, buf: *const c_void, size: usize, written: *mut usize) -> i32;
    fn GetCurrentProcess() -> isize;
    fn GetModuleHandleW(name: *const u16) -> usize;
    fn VirtualAlloc(addr: *mut c_void, size: usize, typ: u32, protect: u32) -> *mut c_void;
    fn VirtualProtect(addr: *mut c_void, size: usize, new: u32, old: *mut u32) -> i32;
    fn FlushInstructionCache(h: isize, addr: *const c_void, size: usize) -> i32;
}

fn read(addr: usize, len: usize) -> Option<Vec<u8>> {
    let mut buf = vec![0u8; len];
    let mut got = 0usize;
    let ok = unsafe {
        ReadProcessMemory(GetCurrentProcess(), addr as *const c_void, buf.as_mut_ptr() as *mut c_void, len, &mut got)
    };
    (ok != 0 && got == len).then_some(buf)
}

fn write_byte(addr: usize, b: u8) -> bool {
    let mut n = 0usize;
    unsafe { WriteProcessMemory(GetCurrentProcess(), addr as *mut c_void, &b as *const u8 as *const c_void, 1, &mut n) != 0 && n == 1 }
}

/// 名字的最后一个字母：本体 n、暗裔 d、影流 s；在墙格里（掠影步穿墙）是它们的暗影剪影 w、r、h（英雄联盟里凯隐
/// 钻进地形时只剩一团暗影；用户：「穿墙的效果要模仿LOL里面」），各自送到 `league_kayn{,_darkin,_shadow}_wall`。
pub const LETTERS: [u8; 6] = [b'n', b'd', b's', b'w', b'r', b'h'];

/// 名字是 `league_kay` + 上面的一个字母时，那个字母。
pub fn form_letter(name: &[u8]) -> Option<u8> {
    (name.len() == NAME_LEN && name.starts_with(STEM) && LETTERS.contains(&name[NAME_LEN - 1]))
        .then(|| name[NAME_LEN - 1])
}

/// 形态 buff 和在不在墙里 → 名字的最后一个字母。
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

/// 显示数据的名字缓冲区（是 `league_kay?` 的话）。
fn kayn_name_buffer(rec: usize) -> Option<(usize, u8)> {
    let b = read(rec + 0x58, 16)?;
    let ptr = usize::from_le_bytes(b[0..8].try_into().unwrap());
    let len = usize::from_le_bytes(b[8..16].try_into().unwrap());
    if len != NAME_LEN {
        return None;
    }
    let name = read(ptr, NAME_LEN)?;
    form_letter(&name).map(|l| (ptr, l))
}

fn install() -> Result<usize, String> {
    let module = unsafe { GetModuleHandleW(std::ptr::null()) };
    if module == 0 {
        return Err("no module handle".into());
    }
    let target = module + RVA;
    let cur = read(target, ORIG.len()).ok_or("the game's code is unreadable there")?;
    if cur != ORIG {
        return Err("not game 0.6.2 (the drawing code differs)".into());
    }
    let tramp = unsafe { VirtualAlloc(std::ptr::null_mut(), 4096, 0x3000, 0x40) } as usize;
    if tramp == 0 {
        return Err("VirtualAlloc failed".into());
    }
    let ring = RING.as_ptr() as usize;
    let mut code: Vec<u8> = Vec::new();
    code.extend_from_slice(&[0x48, 0xB8]); // mov rax, ring
    code.extend_from_slice(&ring.to_le_bytes());
    code.extend_from_slice(&[0x41, 0xBB, 0x01, 0x00, 0x00, 0x00]); // mov r11d, 1
    code.extend_from_slice(&[0xF0, 0x4C, 0x0F, 0xC1, 0x18]); // lock xadd [rax], r11
    code.extend_from_slice(&[0x41, 0x81, 0xE3, 0xFF, 0x00, 0x00, 0x00]); // and r11d, 0xff
    code.extend_from_slice(&[0x4A, 0x89, 0x54, 0xD8, 0x08]); // mov [rax + r11*8 + 8], rdx
    code.extend_from_slice(&ORIG); // the 20 bytes moved here
    code.extend_from_slice(&[0xFF, 0x25, 0x00, 0x00, 0x00, 0x00]); // jmp [rip+0]
    code.extend_from_slice(&(target + ORIG.len()).to_le_bytes());
    unsafe { std::ptr::copy_nonoverlapping(code.as_ptr(), tramp as *mut u8, code.len()) };
    unsafe { FlushInstructionCache(GetCurrentProcess(), tramp as *const c_void, code.len()) };
    let mut patch = vec![0xFF, 0x25, 0x00, 0x00, 0x00, 0x00];
    patch.extend_from_slice(&tramp.to_le_bytes());
    patch.resize(ORIG.len(), 0x90);
    let mut old = 0u32;
    if unsafe { VirtualProtect(target as *mut c_void, ORIG.len(), 0x40, &mut old) } == 0 {
        return Err("VirtualProtect failed".into());
    }
    unsafe { std::ptr::copy_nonoverlapping(patch.as_ptr(), target as *mut u8, patch.len()) };
    let mut tmp = 0u32;
    unsafe { VirtualProtect(target as *mut c_void, ORIG.len(), old, &mut tmp) };
    unsafe { FlushInstructionCache(GetCurrentProcess(), target as *const c_void, ORIG.len()) };
    Ok(target)
}

/// 加载时装钩子（一个进程只装一次）。
pub fn install_once() {
    HOOK.call_once(|| match install() {
        Ok(t) => {
            HOOKED.store(1, Ordering::Relaxed);
            wlog(format!("full transform on: drawing hook at {t:#x}"));
        }
        Err(e) => wlog(format!("full transform off ({e}): Kayn keeps the data pack's half transform")),
    });
}

/// 被动在每个模拟世界里调用：只有画面那一侧的才算数。
pub fn report(sim: &StableSim<'_>, darkin: bool, shadow: bool, in_wall: bool) {
    let o = sim.sim_origin().unwrap_or_default();
    let shown = matches!(SimOriginKindV1::from_code(o.kind),
        Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay));
    if shown {
        TIMELINE.lock().unwrap_or_else(|e| e.into_inner()).note((o.match_id, o.set_index), sim.tick(),
            letter_for(darkin, shadow, in_wall));
    }
}

#[derive(Default)]
struct State {
    t0: Option<Instant>,
    last: f64,
    buffers: Vec<usize>, // the name buffers seen drawn (logged when new)
    told: bool,
    shown: u8,
    minute: Option<usize>, // the clock's minute last logged
    clock: Option<(usize, f64)>, // the screen clock's last second and when (add-on time) it turned to it
    rate: f64,           // match ticks per real second, from the clock's last whole-second step (speed setting)
    dm_start: usize,     // deathmatch: the countdown's first (largest) second this match
    ticking: bool,       // the clock has been seen stepping a second this match (not the layout's "12:34" yet)
    key: (u64, u64),     // the match the above belong to
}

/// 屏幕上的比赛时钟：MOBA 的 ingame.header.game_time.value（往上数），死斗的 ingame.header.dm_scoreboard.timer
/// （倒数）。第一版在界面里找名叫 timer 的标签，找到的是死斗记分板那个——MOBA 里它藏着、一直是 02:00，凯隐一整局
/// 都按 2:00 画成本体，只有出招（数据里本来就是形态的动作）时像变身：「凯隐变身后又会变回去了」（2026-10-06）。
pub const CLOCK: &str = "ingame.header.game_time.value";
pub const DM_CLOCK: &str = "ingame.header.dm_scoreboard.timer";

/// 这个节点和它上面每一层都显示着（藏起来的父节点下面的标签自己可能还标着显示）。
fn on_screen(ctx: &StableClient<'_>, path: &str) -> bool {
    let parts: Vec<&str> = path.split('.').collect();
    (1..=parts.len()).all(|n| ctx.ui_visible(&parts[..n].join(".")) == Some(true))
}

/// 屏幕上比赛走到的秒数（死斗：开局读到的倒数最大值往回算），读不到就是 None。
fn screen_secs(ctx: &StableClient<'_>, dm_start: &mut usize) -> Option<(usize, &'static str)> {
    if on_screen(ctx, CLOCK) {
        return ctx.ui_text(CLOCK).as_deref().and_then(clock_secs).map(|s| (s, CLOCK));
    }
    if on_screen(ctx, DM_CLOCK) {
        let left = ctx.ui_text(DM_CLOCK).as_deref().and_then(clock_secs)?;
        *dm_start = (*dm_start).max(left);
        return Some((*dm_start - left, DM_CLOCK));
    }
    None
}

/// 屏幕上的 tick：时钟的整秒，加上这一秒里按播放速度走过的部分（不到一秒的变化——穿墙一下——不提前也不漏掉）。
pub fn screen_tick(secs: usize, since: f64, rate: f64) -> usize {
    secs * 60 + ((since.max(0.0) * rate) as usize).min(59)
}

/// Every 0.1 s.
const EVERY: f64 = 0.1;

/// 客户端扩展：画的名字和想要的形态不一样就改。
pub struct Swap {
    st: Mutex<State>,
}

impl Swap {
    pub fn new() -> Self {
        Swap { st: Mutex::new(State::default()) }
    }
}

impl StableExtension for Swap {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        if HOOKED.load(Ordering::Relaxed) == 0 {
            return;
        }
        let mut st = self.st.lock().unwrap_or_else(|e| e.into_inner());
        if !ctx.is_in_game() {
            st.buffers.clear();
            st.clock = None;
            st.told = false;
            return;
        }
        let now = st.t0.get_or_insert_with(Instant::now).elapsed().as_secs_f64();
        if now - st.last < EVERY {
            return;
        }
        st.last = now;
        let tl = TIMELINE.lock().unwrap_or_else(|e| e.into_inner());
        if tl.changes.is_empty() {
            return; // no match with Kayn on screen
        }
        if tl.key != st.key {
            st.key = tl.key;
            st.clock = None;
            st.dm_start = 0;
            st.minute = None;
            st.ticking = false;
        }
        // the screen's time (the view's own sim is far ahead of it)
        let mut dm_start = st.dm_start;
        let read = screen_secs(ctx, &mut dm_start);
        st.dm_start = dm_start;
        let Some((secs, which)) = read else {
            if !st.told {
                st.told = true;
                wlog(format!("no match clock on screen ({CLOCK} / {DM_CLOCK}): Kayn is left as he is drawn"));
            }
            return; // keep what is drawn: no going back to the base look on a clock that cannot be read
        };
        match st.clock {
            Some((s, _)) if s == secs => {}
            Some((s, at)) => {
                if secs == s + 1 && now > at {
                    st.rate = (60.0 / (now - at)).clamp(10.0, 1200.0);
                    st.ticking = true;
                }
                st.clock = Some((secs, now));
            }
            None => st.clock = Some((secs, now)),
        }
        if st.rate == 0.0 {
            st.rate = 60.0;
        }
        if !st.ticking {
            return; // until the clock steps once: the label's placeholder could read as 12:34
        }
        let since = st.clock.map_or(0.0, |(_, at)| now - at);
        if st.minute != Some(secs / 60) {
            st.minute = Some(secs / 60);
            wlog(format!("screen clock {:02}:{:02} ({which}, {:.0} ticks a second)", secs / 60, secs % 60, st.rate));
        }
        let Some(want) = tl.at(screen_tick(secs, since, st.rate)) else { return };
        drop(tl);
        if want != st.shown {
            st.shown = want;
            wlog(format!("on screen at {:02}:{:02}: league_kay{}", secs / 60, secs % 60, want as char));
        }
        // always the buffers of the records being drawn now: a buffer found before may have been freed with its
        // bytes still reading league_kay? while Kayn's record got a new name (in game he went back to his base look
        // until the match ended: 「完美变身了 然后又变回去了」)
        let mut recs: Vec<usize> = (1..RING.len()).map(|i| RING[i].load(Ordering::Relaxed)).filter(|&r| r != 0).collect();
        recs.sort_unstable();
        recs.dedup();
        let mut found: Vec<(usize, u8)> = recs.into_iter().filter_map(kayn_name_buffer).collect();
        found.sort_unstable();
        found.dedup();
        for (buf, letter) in found {
            if !st.buffers.contains(&buf) {
                wlog(format!("Kayn's drawn name at {buf:#x} ({})", letter as char));
                st.buffers.push(buf);
                if st.buffers.len() > 64 {
                    st.buffers.remove(0);
                }
            }
            if letter != want && write_byte(buf + NAME_LEN - 1, want) {
                wlog(format!("{buf:#x} drawn as league_kay{} ({})", want as char,
                    match want { b'd' => "Darkin", b's' => "Shadow Assassin", b'n' => "Kayn", _ => "in the wall" }));
            }
        }
    }
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
    fn the_screen_clock_picks_the_form_of_its_time() {
        assert_eq!(clock_secs("07:38"), Some(458));
        assert_eq!(clock_secs(" 0:05 "), Some(5));
        assert_eq!(clock_secs("02:61"), None);
        assert_eq!(clock_secs("Overtime"), None);
        let mut tl = Timeline { key: (0, 0), changes: Vec::new() };
        for (t, l) in [(0, b'n'), (60, b'n'), (27516, b'd'), (27600, b'd'), (41901, b'r'), (41925, b'd')] {
            tl.note((591, 1), t, l);
        }
        assert_eq!(tl.changes.len(), 4);
        assert_eq!(tl.at(2 * 60 * 60), Some(b'n')); // 2:00 on screen: the view's own sim is long past 7:38
        assert_eq!(tl.at(458 * 60 + 59), Some(b'd'));
        assert_eq!(tl.at(41910), Some(b'r'));
        // the clock: 7:38 on screen, 0.5 s into that second at 1x (60 ticks a second) and at 4x
        assert_eq!(screen_tick(458, 0.5, 60.0), 458 * 60 + 30);
        assert_eq!(screen_tick(458, 0.5, 240.0), 458 * 60 + 59);
        assert_eq!(screen_tick(458, 9.0, 60.0), 458 * 60 + 59); // paused: no further than that second
        tl.note((592, 1), 0, b'n'); // the next match starts afresh
        assert_eq!(tl.changes, vec![(0, b'n')]);
    }

    #[test]
    fn the_form_buff_picks_the_letter() {
        assert_eq!(letter_for(true, false, false), b'd');
        assert_eq!(letter_for(false, true, false), b's');
        assert_eq!(letter_for(false, false, false), b'n');
        assert_eq!(letter_for(true, false, true), b'r');
        assert_eq!(letter_for(false, true, true), b'h');
        assert_eq!(letter_for(false, false, true), b'w');
    }
}
