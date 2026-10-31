//! 一个游戏进程里只有一个 DLL 挂钩（2026-10-31：tft 包要单独上创意工坊——只订阅 tft 包也要有高清帧，只订阅英雄联盟包的不受
//! 影响，两个都订阅时不管 Mods 菜单里谁先加载都不冲突、两边的英雄都是高清帧）。
//!
//! 钩子是改函数开头 12 个字节的跳转（src/lookup.rs 先核对开头是不是游戏原来的 PROLOGUE）：两个 DLL 都去挂，后挂的核对不上，
//! tft.dll 先加载的话 league.dll 的高清帧就全没了。所以第一个调用 [`crate::start`] 的 DLL 当**主**（host）：认版本、挂钩
//! （和原来 league.dll 一模一样），再把自己的「门」（[`Door`]：一个 C ABI 的登记函数）写进进程环境变量 [`HOST_ENV`]；后来的
//! DLL 看到主就当**客**（guest）：把自己的表写成文本（[`Table::to_text`]）从门交过去，自己一个钩子都不挂。主收到就解析、
//! 复制、登记（src/hd.rs 的 [`Registry`]：钩子无锁读的快照，登记一次换一份）。
//!
//! 环境变量的值：`<进程标记>:<协议版本>:<门的地址>:<主的名字>`。game_places::ENV 的值带着 EXE 的标记，这里带的是进程的：
//! 进程 id 加创建时间——从启动这个进程的进程继承来的值标记不同，当作没有主。协议版本不一样的主：客写一行日志，不挂钩、不交
//! 表，它的英雄画 1 倍帧。认不出版本、钩子挂不上的 DLL 不写环境变量（后加载的 DLL 会遇到一样的情况，也画 1 倍帧，日志里
//! 写明）。主的 DLL 和它的钩子一样一直留在进程里，门的地址一直有效；客交表前还确认这个地址在一个加载着的模块里。
//!
//! 前提：游戏启动时按顺序一个一个初始化 mod（目前看到的都是这样），两个 DLL 不会同时走到「看有没有主」和「写环境变量」之间。

use crate::hd::{Registry, Table, REGISTRY};
use crate::wlog;

/// The process environment variable the host publishes: `<process tag>:<protocol>:<its door, hex>:<its name>`.
pub const HOST_ENV: &str = "TFM2_HD_HOST";
/// What the door and the table's text speak. A format change bumps it: a guest of another protocol hands nothing over.
pub const PROTOCOL: u32 = 1;
/// The text's first word (then the protocol).
const MAGIC: &str = "tfm2-hd-table";

/// The host's door: a guest's table as UTF-8 text ([`Table::to_text`]: pointer, length in bytes) -> how many of its
/// heroes the host registered (>= 0), or a refusal ([`REFUSED_TEXT`], [`REFUSED_PROTOCOL`], [`REFUSED_PANIC`]). The
/// host copies what it keeps before it returns.
pub type Door = extern "C" fn(*const u8, usize) -> i32;
/// not UTF-8, or not a table
pub const REFUSED_TEXT: i32 = -1;
/// a table of another protocol
pub const REFUSED_PROTOCOL: i32 = -2;
/// the host panicked reading it
pub const REFUSED_PANIC: i32 = -3;

/// What a DLL is to the dense frames once [`crate::start`] returns.
#[derive(Clone, Debug, PartialEq)]
pub enum Role {
    /// it hooked the game: its own table's heroes and every guest's are drawn dense
    Host,
    /// another DLL of the process (`host`, its name) hooked the game; this one handed it its table (`heroes` rows,
    /// effects included) and hooks nothing
    Guest { host: String, heroes: usize },
    /// no hooks, nothing handed over (why): this table's heroes draw their 1x frames
    Off(String),
}

/// One line of the text and the .fanim blobs after a row's line.
struct Cursor<'a> {
    rest: &'a str,
}

impl<'a> Cursor<'a> {
    fn line(&mut self) -> Result<&'a str, String> {
        let (l, r) = self.rest.split_once('\n').ok_or("the text ends inside a line")?;
        self.rest = r;
        Ok(l)
    }

    /// The next `n` bytes, then a line end.
    fn blob(&mut self, n: usize) -> Result<&'a str, String> {
        if n > self.rest.len() || !self.rest.is_char_boundary(n) {
            return Err(format!("a .fanim of {n} bytes: the text is cut short"));
        }
        let (b, r) = self.rest.split_at(n);
        self.rest = r.strip_prefix('\n').ok_or("no line end after a .fanim")?;
        Ok(b)
    }
}

fn number(s: &str) -> Result<f32, String> {
    s.parse().map_err(|_| format!("not a number: {s:?}"))
}

fn length(s: &str) -> Result<usize, String> {
    s.parse().map_err(|_| format!("not a length: {s:?}"))
}

fn id(s: &str) -> Result<&str, String> {
    if s.is_empty() { Err("an empty id".into()) } else { Ok(s) }
}

/// The protocol a table's text says it speaks (its first line).
pub fn protocol_of(text: &str) -> Option<u32> {
    text.split('\n').next()?.strip_prefix(MAGIC)?.strip_prefix(' ')?.parse().ok()
}

impl<'a> Table<'a> {
    /// The table as the text a guest hands the host: a header line (`tfm2-hd-table <protocol>`), `pack <id>`, one line
    /// a row, `end`. A hero's or an effect's line ends with its .fanim's length in bytes and the .fanim follows it as it
    /// is, then a line end. Numbers are Rust's shortest form of the f32, read back the same.
    pub fn to_text(&self) -> String {
        let mut s = format!("{MAGIC} {PROTOCOL}\npack {}\n", self.pack);
        for (kind, rows) in [("hero", &self.heroes), ("effect", &self.effects)] {
            for (id, ppu, fanim) in rows {
                s += &format!("{kind} {id} {ppu} {}\n", fanim.len());
                s += fanim;
                s.push('\n');
            }
        }
        for (id, size) in &self.sizes {
            s += &format!("size {id} {size}\n");
        }
        for (id, buff, per) in &self.growth {
            s += &format!("growth {id} {buff} {per}\n");
        }
        for id in &self.drawn_effects {
            s += &format!("drawn {id}\n");
        }
        for (id, size) in &self.ui_sizes {
            s += &format!("ui_size {id} {size}\n");
        }
        s + "end\n"
    }

    /// [`Table::to_text`]'s text read back (borrowing from it): Err when it is not one, or of another protocol.
    pub fn parse(text: &'a str) -> Result<Table<'a>, String> {
        let mut c = Cursor { rest: text };
        let head = c.line()?;
        match protocol_of(head) {
            Some(PROTOCOL) => {}
            Some(p) => return Err(format!("a table of protocol {p}, this DLL reads {PROTOCOL}")),
            None => return Err("not a dense-frame table".into()),
        }
        let mut t = Table::default();
        loop {
            let line = c.line()?;
            let f: Vec<&str> = line.split(' ').collect();
            match f[..] {
                ["pack", p] => t.pack = id(p)?,
                ["hero", h, ppu, n] => t.heroes.push((id(h)?, number(ppu)?, c.blob(length(n)?)?)),
                ["effect", e, ppu, n] => t.effects.push((id(e)?, number(ppu)?, c.blob(length(n)?)?)),
                ["size", h, size] => t.sizes.push((id(h)?, number(size)?)),
                ["growth", h, buff, per] => t.growth.push((id(h)?, id(buff)?, number(per)?)),
                ["drawn", e] => t.drawn_effects.push(id(e)?),
                ["ui_size", h, size] => t.ui_sizes.push((id(h)?, number(size)?)),
                ["end"] => break,
                _ => return Err(format!("not a row: {:?}", line.chars().take(80).collect::<String>())),
            }
        }
        if t.pack.is_empty() {
            return Err("no pack".into());
        }
        Ok(t)
    }
}

/// This DLL's door, when it is the host (its address goes into [`HOST_ENV`]).
pub(crate) extern "C" fn door(ptr: *const u8, len: usize) -> i32 {
    std::panic::catch_unwind(|| unsafe { receive(&REGISTRY, ptr, len) }).unwrap_or(REFUSED_PANIC)
}

/// A guest's table text (`ptr`, `len`) read and registered in `reg` (the names it keeps copied) -> how many heroes
/// came in, or a refusal.
///
/// # Safety
/// `ptr` must point at `len` readable bytes (or be null).
pub(crate) unsafe fn receive(reg: &Registry, ptr: *const u8, len: usize) -> i32 {
    if ptr.is_null() || len > 1 << 30 {
        return REFUSED_TEXT;
    }
    let Ok(text) = std::str::from_utf8(std::slice::from_raw_parts(ptr, len)) else {
        wlog("dense frames: a guest's table is not UTF-8 - refused");
        return REFUSED_TEXT;
    };
    let t = match Table::parse(text) {
        Ok(t) => t,
        Err(e) => {
            wlog(format!("dense frames: a guest's table refused ({e})"));
            return if protocol_of(text).is_some_and(|p| p != PROTOCOL) { REFUSED_PROTOCOL } else { REFUSED_TEXT };
        }
    };
    let came = reg.add(&t);
    let now = reg.heroes();
    let list: Vec<String> = came.iter().filter_map(|id| now.get(id)).map(|h| format!("{} x{}", h.id, h.ppu)).collect();
    wlog(format!("dense frames: the {} table came in from a guest, {} heroes and effect sheets registered: {}", t.pack,
                 came.len(), list.join(", ")));
    let rows = t.heroes.len() + t.effects.len();
    if came.len() < rows {
        wlog(format!("dense frames: {} of its {rows} rows left out - their ids were registered already", rows - came.len()));
    }
    i32::try_from(came.len()).unwrap_or(i32::MAX)
}

/// Where the host is published: the process environment (one for every DLL of the game process), or a stand-in (the
/// tests).
pub(crate) trait Env {
    fn get(&self) -> Option<String>;
    fn set(&self, value: &str);
}

pub(crate) struct ProcessEnv;

impl Env for ProcessEnv {
    fn get(&self) -> Option<String> {
        std::env::var(HOST_ENV).ok()
    }

    fn set(&self, value: &str) {
        std::env::set_var(HOST_ENV, value);
    }
}

/// What [`HOST_ENV`] says to a DLL of the process tagged `me`.
#[derive(Debug, PartialEq)]
pub(crate) enum Seen {
    /// nothing, or another process's value (inherited from the process that started this one): no host here yet
    Nobody,
    /// this process's host: its door and its name
    Host { door: usize, name: String },
    /// this process's host, speaking another protocol (or with no door this DLL can read)
    Other { protocol: String, name: String },
}

pub(crate) fn seen(value: Option<&str>, me: &str) -> Seen {
    let Some(v) = value else { return Seen::Nobody };
    let mut f = v.splitn(4, ':');
    let (Some(tag), Some(protocol), Some(door), Some(name)) = (f.next(), f.next(), f.next(), f.next()) else {
        return Seen::Nobody; // not a host's value at all
    };
    if tag != me {
        return Seen::Nobody;
    }
    let door = usize::from_str_radix(door, 16).ok().filter(|d| *d != 0);
    match (protocol.parse::<u32>(), door) {
        (Ok(PROTOCOL), Some(door)) => Seen::Host { door, name: name.to_string() },
        _ => Seen::Other { protocol: protocol.to_string(), name: name.to_string() },
    }
}

/// The host's value of [`HOST_ENV`].
pub(crate) fn host_value(me: &str, door: usize, who: &str) -> String {
    format!("{me}:{PROTOCOL}:{door:x}:{who}")
}

/// This process as no other: its id and its creation time (100 ns ticks). A value inherited from the process that
/// started this one carries that one's, so it is not taken for a host here.
pub(crate) fn process_tag() -> String {
    #[cfg(windows)]
    {
        #[link(name = "kernel32")]
        extern "system" {
            fn GetCurrentProcess() -> isize;
            fn GetProcessTimes(h: isize, created: *mut u64, exited: *mut u64, kernel: *mut u64, user: *mut u64) -> i32;
        }
        let (mut created, mut exited, mut kernel, mut user) = (0u64, 0u64, 0u64, 0u64);
        unsafe { GetProcessTimes(GetCurrentProcess(), &mut created, &mut exited, &mut kernel, &mut user) };
        format!("{:x}.{created:x}", std::process::id())
    }
    #[cfg(not(windows))]
    format!("{:x}", std::process::id())
}

/// Whether `addr` lies in a module loaded in this process (a door of a DLL still here).
fn in_a_module(addr: usize) -> bool {
    #[cfg(windows)]
    {
        #[link(name = "kernel32")]
        extern "system" {
            fn GetModuleHandleExW(flags: u32, name: *const u16, module: *mut usize) -> i32;
        }
        const FROM_ADDRESS: u32 = 0x4;
        const UNCHANGED_REFCOUNT: u32 = 0x2;
        let mut m = 0usize;
        unsafe { GetModuleHandleExW(FROM_ADDRESS | UNCHANGED_REFCOUNT, addr as *const u16, &mut m) != 0 && m != 0 }
    }
    #[cfg(not(windows))]
    {
        addr != 0
    }
}

/// [`crate::start`] for the DLL `who` of the process tagged `me`, its host published in `env`, the heroes registered
/// in `reg`, `door` the one it publishes when it hooks the game itself (`install`: Err why when it does not).
///
/// Mod inits run one after another at startup (as far as we know): no other DLL gets between this one reading `env` and
/// writing it.
pub(crate) fn start_with(env: &dyn Env, reg: &Registry, me: &str, table: &Table<'_>, who: &str, door: Door,
                         install: impl FnOnce() -> Result<(), String>) -> Role {
    let rows = table.heroes.len() + table.effects.len();
    match seen(env.get().as_deref(), me) {
        Seen::Host { door: d, name } if in_a_module(d) => {
            let text = table.to_text();
            // SAFETY: a door this process's host published (its tag), in a module still loaded
            let host: Door = unsafe { std::mem::transmute::<usize, Door>(d) };
            let n = host(text.as_ptr(), text.len());
            if n < 0 {
                wlog(format!("dense frames: {name} (the host) refused the {} table ({n}) - {who} hooks nothing, its \
                              heroes draw their 1x frames", table.pack));
                return Role::Off(format!("{name} refused the table ({n})"));
            }
            wlog(format!("dense frames: the {} table ({} heroes, {} effect sheets) handed to {name}, the host ({n} \
                          registered there) - {who} hooks nothing", table.pack, table.heroes.len(), table.effects.len()));
            Role::Guest { host: name, heroes: rows }
        }
        Seen::Host { door: d, name } => {
            wlog(format!("dense frames: the host {name}'s door {d:#x} is in no loaded module - {who} hooks nothing, \
                          the {} heroes draw their 1x frames", table.pack));
            Role::Off(format!("{name}'s door is gone"))
        }
        Seen::Other { protocol, name } => {
            wlog(format!("dense frames: the host {name} speaks protocol {protocol}, {who} {PROTOCOL} - nothing handed \
                          over, no hooks: the {} heroes draw their 1x frames (update both packs)", table.pack));
            Role::Off(format!("{name} speaks dense-frame protocol {protocol}, {who} {PROTOCOL}"))
        }
        Seen::Nobody => {
            reg.add(table);
            match install() {
                Ok(()) => {
                    env.set(&host_value(me, door as usize, who));
                    wlog(format!("dense frames: {who} is the host ({HOST_ENV} published, protocol {PROTOCOL}) - a \
                                  pack's DLL loading after it hands its table here"));
                    Role::Host
                }
                Err(why) => {
                    wlog(format!("dense frames: no hooks, no host published - a pack's DLL loading after {who} meets \
                                  the same game and draws 1x too"));
                    Role::Off(why)
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::hd::tests::{fanim, table};
    use std::cell::{Cell, RefCell};

    /// A process environment of its own.
    #[derive(Default)]
    struct TestEnv(RefCell<Option<String>>);

    impl Env for TestEnv {
        fn get(&self) -> Option<String> {
            self.0.borrow().clone()
        }

        fn set(&self, value: &str) {
            *self.0.borrow_mut() = Some(value.to_string());
        }
    }

    /// A test host's registry and its door (the DLL's own door is bound to the process's registry); one pair a test,
    /// so the tests running side by side do not see each other's tables.
    macro_rules! host {
        ($reg:ident, $door:ident) => {
            static $reg: Registry = Registry::new();
            extern "C" fn $door(ptr: *const u8, len: usize) -> i32 {
                std::panic::catch_unwind(|| unsafe { receive(&$reg, ptr, len) }).unwrap_or(REFUSED_PANIC)
            }
        };
    }
    host!(HOST, host_door);
    host!(OLD_HOST, old_host_door);
    host!(UNUSED, unused_door);

    fn league() -> Table<'static> {
        let mut t = table("league", &[("league_yasuo", 2.2), ("league_chogath", 2.0)]);
        t.growth.push(("league_chogath", "league_chogath_r_stack", 0.30));
        t.effects.push(("league_ivern_daisy_drop", 1.333, Box::leak(fanim(1.333, false).into_boxed_str())));
        t.drawn_effects.push("league_ivern_daisy_drop");
        t
    }

    fn tft() -> Table<'static> {
        let mut t = table("tft", &[("tft_powder", 1.75), ("tft_alune", 2.0)]);
        t.sizes.push(("tft_powder", 0.90));
        t.ui_sizes.push(("tft_alune", 0.85));
        t
    }

    #[test]
    fn a_table_goes_through_the_text_and_back() {
        for t in [league(), tft()] {
            let text = t.to_text();
            assert_eq!(protocol_of(&text), Some(PROTOCOL));
            assert_eq!(Table::parse(&text), Ok(t.clone()));
        }
        // a .fanim with line ends, spaces and non-ASCII in it, numbers that print long
        let mut t = Table { pack: "tft", ..Table::default() };
        t.heroes.push(("tft_odd", 2.935, "{\"anims\": {\n \"idle\" : 1}}\n「爆爆」 end\n"));
        t.sizes.push(("tft_odd", 1.0 / 3.0));
        assert_eq!(Table::parse(&t.to_text()), Ok(t.clone()));
        // what is not a table
        let text = t.to_text();
        assert!(Table::parse(&text[..text.len() - 4]).is_err()); // cut short
        assert!(Table::parse(&text.replacen(&format!("{MAGIC} {PROTOCOL}"), &format!("{MAGIC} 99"), 1))
            .unwrap_err().contains("protocol 99"));
        assert!(Table::parse(&text.replacen("size tft_odd", "size  tft_odd", 1)).is_err());
        assert!(Table::parse("hello\n").is_err());
        assert!(Table::parse(&format!("{MAGIC} {PROTOCOL}\nend\n")).unwrap_err().contains("no pack"));
    }

    #[test]
    fn the_hosts_value_is_this_processs_alone() {
        let me = process_tag();
        assert!(me.starts_with(&format!("{:x}", std::process::id())));
        let v = host_value(&me, 0x7ff6_1234_5670, "league.dll 0.9.0");
        assert_eq!(seen(Some(&v), &me), Seen::Host { door: 0x7ff6_1234_5670, name: "league.dll 0.9.0".into() });
        // inherited from the process that started this one: another tag
        assert_eq!(seen(Some(&host_value("1.2", 0x7ff6_1234_5670, "league.dll 0.9.0")), &me), Seen::Nobody);
        assert_eq!(seen(None, &me), Seen::Nobody);
        assert_eq!(seen(Some("garbage"), &me), Seen::Nobody);
        // this process's, another protocol: a host all the same
        let v2 = v.replacen(&format!(":{PROTOCOL}:"), ":2:", 1);
        assert_eq!(seen(Some(&v2), &me), Seen::Other { protocol: "2".into(), name: "league.dll 0.9.0".into() });
        // a name may hold the separator
        assert_eq!(seen(Some(&host_value(&me, 0x10, "a:b")), &me), Seen::Host { door: 0x10, name: "a:b".into() });
    }

    #[test]
    fn the_first_dll_hosts_and_the_next_one_hands_it_its_table() {
        let env = TestEnv::default();
        let me = process_tag();
        // no host: this one hooks the game and publishes its door
        let hooked = Cell::new(0);
        let r = start_with(&env, &HOST, &me, &league(), "league.dll 0.9.0", host_door, || {
            hooked.set(hooked.get() + 1);
            Ok(())
        });
        assert_eq!(r, Role::Host);
        assert_eq!(hooked.get(), 1);
        let v = env.get().expect("published");
        assert_eq!(seen(Some(&v), &me), Seen::Host { door: host_door as Door as usize, name: "league.dll 0.9.0".into() });
        assert!(HOST.heroes().get("league_yasuo").is_some() && HOST.heroes().get("tft_powder").is_none());
        // the host there: the next DLL hooks nothing and its heroes join the host's
        let mine = Registry::new();
        let r = start_with(&env, &mine, &me, &tft(), "tft.dll 0.29.0", host_door, || panic!("a guest hooks nothing"));
        assert_eq!(r, Role::Guest { host: "league.dll 0.9.0".into(), heroes: 2 });
        assert_eq!(env.get().as_deref(), Some(v.as_str()), "the host's value stays");
        let h = HOST.heroes();
        for id in ["league_yasuo", "league_chogath", "league_ivern_daisy_drop", "tft_powder", "tft_alune"] {
            assert!(h.get(id).is_some(), "{id}");
        }
        assert_eq!(h.get("tft_powder").map(|x| x.size), Some(0.90));
        assert!((h.get("tft_alune").unwrap().ui - crate::hd::UI_PPU / 0.85).abs() < 1e-6);
        assert_eq!(h.packs, vec!["league", "tft"]);
        assert_eq!(h.growth, vec![("league_chogath", "league_chogath_r_stack", 0.30)]);
        assert_eq!(h.drawn_effects, vec!["league_ivern_daisy_drop"]);
        assert!(mine.heroes().list.is_empty(), "the guest keeps no table of its own");
    }

    #[test]
    fn a_host_of_another_protocol_gets_nothing() {
        let me = process_tag();
        let env = TestEnv::default();
        let v = host_value(&me, old_host_door as Door as usize, "league.dll 9.0.0");
        env.set(&v.replacen(&format!(":{PROTOCOL}:"), ":7:", 1));
        let r = start_with(&env, &Registry::new(), &me, &tft(), "tft.dll 0.29.0", unused_door, || panic!("no hooks"));
        assert!(matches!(&r, Role::Off(why) if why.contains("protocol 7")), "{r:?}");
        assert!(OLD_HOST.heroes().list.is_empty(), "nothing handed over");
        // and a host refuses a table of another protocol at its door, and what is not a table
        let text = tft().to_text().replacen(&format!("{MAGIC} {PROTOCOL}"), &format!("{MAGIC} 7"), 1);
        assert_eq!(old_host_door(text.as_ptr(), text.len()), REFUSED_PROTOCOL);
        assert_eq!(old_host_door(b"\xff\xfe".as_ptr(), 2), REFUSED_TEXT);
        assert_eq!(old_host_door(b"hello\n".as_ptr(), 6), REFUSED_TEXT);
        assert_eq!(old_host_door(std::ptr::null(), 0), REFUSED_TEXT);
        assert!(OLD_HOST.heroes().list.is_empty());
        // a guest's text that is a table: in
        let text = tft().to_text();
        assert_eq!(old_host_door(text.as_ptr(), text.len()), 2);
        assert_eq!(old_host_door(text.as_ptr(), text.len()), 0, "registered already");
    }

    #[test]
    fn another_processs_host_is_ignored() {
        let me = process_tag();
        let env = TestEnv::default();
        env.set(&host_value("4d2.1dc0ffee", unused_door as Door as usize, "league.dll 0.9.0"));
        let reg = Registry::new();
        let hooked = Cell::new(false);
        let r = start_with(&env, &reg, &me, &tft(), "tft.dll 0.29.0", unused_door, || {
            hooked.set(true);
            Ok(())
        });
        assert_eq!(r, Role::Host);
        assert!(hooked.get());
        let now = seen(env.get().as_deref(), &me);
        assert_eq!(now, Seen::Host { door: unused_door as Door as usize, name: "tft.dll 0.29.0".into() });
        assert!(reg.heroes().get("tft_powder").is_some());
        assert!(UNUSED.heroes().list.is_empty());
    }

    #[test]
    fn no_hooks_no_host() {
        let env = TestEnv::default();
        let r = start_with(&env, &Registry::new(), &process_tag(), &league(), "league.dll 0.9.0", unused_door,
                           || Err("game build unknown".into()));
        assert_eq!(r, Role::Off("game build unknown".into()));
        assert_eq!(env.get(), None, "nothing published: a later DLL tries (and fails) the same");
    }
}
