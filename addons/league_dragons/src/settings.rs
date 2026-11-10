//! 玩家可调的持续时间（0.3.8，用户 2026-11-10：「远古龙的刷新时间和持续时间在哪调 玩家要调的话」「加配置文件」「就改持续时间」）：
//! 本包文件夹里的 `settings.ini`（记事本改：每行 `名字 = 秒数`，`#` 后面是说明），本包加载时（游戏启动）读一次，所有模拟都用
//! 这一份——预演和屏幕上一样。没有这个文件、某一行写错、超出范围：那一项用默认值，日志 `SETTINGS` 一行写明用的是什么。
//!
//! 刷新时间不在这里：远古巨龙就是游戏的小龙营地刷的，和元素亚龙共用游戏数据库编辑器里「元素亚龙」的刷新时间（文件里写明）。
//! 游戏自己的文字（`text/`，百科、增益说明）是写死的文件，还写默认的秒数；本包的公告、HUD、说明框写这里的。
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

/// The file's name, in this mod's folder.
pub const FILE: &str = "settings.ini";
/// Ticks a second.
pub const TPS: usize = 60;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Settings {
    /// 远古龙之力持续多少秒
    pub elder_buff_s: usize,
    /// 纳什男爵之手持续多少秒
    pub baron_buff_s: usize,
}

impl Default for Settings {
    fn default() -> Self {
        Settings { elder_buff_s: super::rules::ELDER_T / TPS, baron_buff_s: super::rules::BARON_T / TPS }
    }
}

/// A key of the file: its name, the range it takes, where it goes.
struct Key {
    name: &'static str,
    lo: usize,
    hi: usize,
    set: fn(&mut Settings, usize),
}

const KEYS: [Key; 2] = [
    Key { name: "elder_buff_seconds", lo: 10, hi: 600, set: |s, v| s.elder_buff_s = v },
    Key { name: "baron_buff_seconds", lo: 10, hi: 600, set: |s, v| s.baron_buff_s = v },
];

/// The settings in `text` (the file's), and a note for every line not taken (the log's).
pub fn parse(text: &str) -> (Settings, Vec<String>) {
    let mut s = Settings::default();
    let mut notes = Vec::new();
    for (i, raw) in text.lines().enumerate() {
        let line = raw.trim_start_matches('\u{feff}').split('#').next().unwrap_or("").trim();
        if line.is_empty() || line.starts_with('[') {
            continue;
        }
        let Some((k, v)) = line.split_once('=') else {
            notes.push(format!("line {}: no '=' - {line:?} left out", i + 1));
            continue;
        };
        let (k, v) = (k.trim(), v.trim());
        let Some(key) = KEYS.iter().find(|key| key.name.eq_ignore_ascii_case(k)) else {
            notes.push(format!("line {}: unknown name {k:?} - left out", i + 1));
            continue;
        };
        match v.parse::<usize>() {
            Ok(n) if (key.lo..=key.hi).contains(&n) => (key.set)(&mut s, n),
            Ok(n) => notes.push(format!("line {}: {k} = {n} is outside {}-{} - the default kept", i + 1, key.lo, key.hi)),
            Err(_) => notes.push(format!("line {}: {k} = {v:?} is not a whole number of seconds - the default kept", i + 1)),
        }
    }
    (s, notes)
}

static SETTINGS: OnceLock<Settings> = OnceLock::new();

/// The settings in use: the file's once [`init`] read it, else the defaults (the tests, the bundle).
pub fn get() -> Settings {
    *SETTINGS.get_or_init(Settings::default)
}

/// 远古龙之力、纳什男爵之手持续多少 tick。
pub fn elder_t() -> usize {
    get().elder_buff_s * TPS
}

pub fn baron_t() -> usize {
    get().baron_buff_s * TPS
}

/// Read `dir`/settings.ini once (at load, before any match): -> the log line.
pub fn init(dir: Option<PathBuf>) -> String {
    let path = dir.map(|d| d.join(FILE));
    let (s, mut notes) = match path.as_deref().map(std::fs::read) {
        Some(Ok(bytes)) => parse(&String::from_utf8_lossy(&bytes)),
        Some(Err(e)) => (Settings::default(), vec![format!("not read ({e}) - the defaults")]),
        None => (Settings::default(), vec!["this mod's folder not found - the defaults".to_string()]),
    };
    if SETTINGS.set(s).is_err() {
        notes.push("already set - kept as it was".into());
    }
    let s = get();
    format!("SETTINGS {}: elder_buff_seconds {} (default {}), baron_buff_seconds {} (default {}){}",
            path.as_deref().map_or_else(|| "-".into(), |p: &Path| p.display().to_string()), s.elder_buff_s,
            Settings::default().elder_buff_s, s.baron_buff_s, Settings::default().baron_buff_s,
            if notes.is_empty() { String::new() } else { format!("; {}", notes.join("; ")) })
}

/// The folder this DLL was loaded from: `mods/league_dragons` (league_main warm.rs).
#[cfg(windows)]
pub fn dll_dir() -> Option<PathBuf> {
    use std::ffi::OsString;
    use std::os::windows::ffi::OsStringExt;
    #[link(name = "kernel32")]
    extern "system" {
        fn GetModuleHandleExW(flags: u32, name: *const u16, module: *mut usize) -> i32;
        fn GetModuleFileNameW(module: usize, buf: *mut u16, len: u32) -> u32;
    }
    const FROM_ADDRESS: u32 = 0x4;
    const UNCHANGED_REFCOUNT: u32 = 0x2;
    let mut module = 0usize;
    let mut buf = vec![0u16; 32_768];
    unsafe {
        if GetModuleHandleExW(FROM_ADDRESS | UNCHANGED_REFCOUNT, dll_dir as *const () as *const u16, &mut module) == 0 {
            return None;
        }
        let n = GetModuleFileNameW(module, buf.as_mut_ptr(), buf.len() as u32) as usize;
        if n == 0 || n >= buf.len() {
            return None;
        }
        PathBuf::from(OsString::from_wide(&buf[..n])).parent().map(Path::to_path_buf)
    }
}

#[cfg(not(windows))]
pub fn dll_dir() -> Option<PathBuf> {
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_file_sets_the_two_durations() {
        let d = Settings::default();
        assert_eq!((d.elder_buff_s, d.baron_buff_s), (90, 120));
        let (s, notes) = parse("\u{feff}# comment\n[远古巨龙]\nelder_buff_seconds = 150   # 远古龙之力\nBARON_BUFF_SECONDS=180\n");
        assert_eq!((s.elder_buff_s, s.baron_buff_s), (150, 180));
        assert!(notes.is_empty(), "{notes:?}");
    }

    #[test]
    fn a_bad_line_keeps_the_default_and_says_why() {
        let (s, notes) = parse("elder_buff_seconds = 5\nbaron_buff_seconds = 2分钟\nelder_buff_seconds\nsoul = 3\n");
        assert_eq!(s, Settings::default());
        assert_eq!(notes.len(), 4, "{notes:?}");
        assert!(notes[0].contains("outside 10-600") && notes[1].contains("not a whole number"), "{notes:?}");
        assert!(notes[2].contains("no '='") && notes[3].contains("unknown name"), "{notes:?}");
    }

    /// The file shipped in the mod parses to the defaults with no note (src/../settings.ini).
    #[test]
    fn the_shipped_file_is_the_defaults() {
        let (s, notes) = parse(include_str!("../settings.ini"));
        assert_eq!(s, Settings::default());
        assert!(notes.is_empty(), "{notes:?}");
    }
}
