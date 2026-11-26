//! 玩家可调的（本包文件夹里的 `settings.ini`，记事本改：每行 `名字 = 数`，`#` 后面是说明）：本包加载时（游戏启动）读一次，所有
//! 模拟都用这一份——预演和屏幕上一样。没有这个文件、某一行写错、超出范围：那一项用默认值，日志 `SETTINGS` 一行写明用的是什么。
//!
//! - 第 2、3、4 次选择在几级（默认 6、9、12；本游戏最高 12 级。第 1 次是开局）。
//! - 第几分钟还没拿满 4 个的补齐（默认 10，0 = 不补）。
//! - 三档各占多少（默认银 35、金 45、棱彩 20）。
//! - 屏幕上画不画开局面板和每次选择的提示（默认画；头像上的小色块总是画）。只管画面，模拟不读它。
//! - 战场上的触发特效怎么画（0.3.0，`battlefield_effects`，大小龙同名的那一项）：0 不画、1 只一格一格画、2（默认）能画贴图时
//!   画贴图。也只管画面。

use std::path::{Path, PathBuf};
use std::sync::OnceLock;

pub const FILE: &str = "settings.ini";
/// 一秒几个 tick。
pub const TPS: usize = 60;
/// 本游戏最高几级。
pub const MAX_LEVEL: usize = 12;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Settings {
    /// 第 2、3、4 次在几级
    pub levels: [usize; 3],
    /// 第几分钟补齐（0：不补）
    pub catch_up_min: usize,
    /// 银、金、棱彩的权重
    pub weights: [u32; 3],
    /// 画不画开局面板和提示
    pub show: bool,
    /// 画不画开局的对阵面板（0.3.3 起默认不画：用户「游戏内开局海克斯那个显示提示不需要 太占屏幕了」）
    pub opening: bool,
    /// 战场特效：[`EFFECTS_OFF`] / [`EFFECTS_SQUARES`] / [`EFFECTS_AUTO`]
    pub effects: usize,
}

/// `battlefield_effects`：不画、只一格一格画、能画贴图时画贴图。
pub const EFFECTS_OFF: usize = 0;
pub const EFFECTS_SQUARES: usize = 1;
pub const EFFECTS_AUTO: usize = 2;

impl Default for Settings {
    fn default() -> Self {
        Settings { levels: [6, 9, 12], catch_up_min: 10, weights: [35, 45, 20], show: true, opening: false,
                   effects: EFFECTS_AUTO }
    }
}

struct Key {
    name: &'static str,
    lo: usize,
    hi: usize,
    set: fn(&mut Settings, usize),
}

const KEYS: [Key; 10] = [
    Key { name: "level_2", lo: 2, hi: MAX_LEVEL, set: |s, v| s.levels[0] = v },
    Key { name: "level_3", lo: 2, hi: MAX_LEVEL, set: |s, v| s.levels[1] = v },
    Key { name: "level_4", lo: 2, hi: MAX_LEVEL, set: |s, v| s.levels[2] = v },
    Key { name: "catch_up_minute", lo: 0, hi: 60, set: |s, v| s.catch_up_min = v },
    Key { name: "silver_weight", lo: 0, hi: 100, set: |s, v| s.weights[0] = v as u32 },
    Key { name: "gold_weight", lo: 0, hi: 100, set: |s, v| s.weights[1] = v as u32 },
    Key { name: "prismatic_weight", lo: 0, hi: 100, set: |s, v| s.weights[2] = v as u32 },
    Key { name: "show_picks", lo: 0, hi: 1, set: |s, v| s.show = v != 0 },
    Key { name: "show_opening", lo: 0, hi: 1, set: |s, v| s.opening = v != 0 },
    Key { name: "battlefield_effects", lo: EFFECTS_OFF, hi: EFFECTS_AUTO, set: |s, v| s.effects = v },
];

/// 文件里的设置，和每一行没用上的原因（写进日志）。
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
            Err(_) => notes.push(format!("line {}: {k} = {v:?} is not a whole number - the default kept", i + 1)),
        }
    }
    // 等级要一次比一次高：不是的话排一下序（同一级的两次就在同一级一起给）
    if s.levels.windows(2).any(|w| w[0] > w[1]) {
        notes.push(format!("levels {:?} not rising - sorted", s.levels));
        s.levels.sort();
    }
    if s.weights.iter().all(|&w| w == 0) {
        notes.push("every tier's weight is 0 - the defaults".into());
        s.weights = Settings::default().weights;
    }
    (s, notes)
}

static SETTINGS: OnceLock<Settings> = OnceLock::new();

pub fn get() -> Settings {
    *SETTINGS.get_or_init(Settings::default)
}

/// 战场特效怎么画（[`EFFECTS_OFF`] / [`EFFECTS_SQUARES`] / [`EFFECTS_AUTO`]）。
pub fn effects() -> usize {
    get().effects
}

/// 第 `screen` 次（0 起）该不该给了：开局那一次到了 [`super::OPEN_AT`] 就给，之后按等级，到了补齐的那一分钟没拿满的都给。
pub fn due(s: &Settings, screen: usize, level: usize, tick: usize) -> bool {
    if screen == 0 {
        return tick >= super::OPEN_AT;
    }
    let Some(&need) = s.levels.get(screen - 1) else { return false };
    level >= need || (s.catch_up_min > 0 && tick >= s.catch_up_min * 60 * TPS)
}

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
    let d = Settings::default();
    format!("SETTINGS {}: picks at the start and at levels {:?} (default {:?}), all four by minute {} (default {}; 0 off), \
             tier weights silver / gold / prismatic {:?} (default {:?}), show_picks {} (default 1), \
             show_opening {} (default 0), battlefield_effects {} (default 2){}",
            path.as_deref().map_or_else(|| "-".into(), |p: &Path| p.display().to_string()), s.levels, d.levels,
            s.catch_up_min, d.catch_up_min, s.weights, d.weights, s.show as u8, s.opening as u8, s.effects,
            if notes.is_empty() { String::new() } else { format!("; {}", notes.join("; ")) })
}

/// 本包 DLL 所在的文件夹（settings.ini 就在旁边）。
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
    fn the_shipped_file_reads_as_the_defaults() {
        let text = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/settings.ini")).expect("settings.ini");
        let (s, notes) = parse(&text);
        assert_eq!(s, Settings::default());
        assert!(notes.is_empty(), "{notes:?}");
    }

    #[test]
    fn bad_lines_keep_the_defaults() {
        let (s, notes) = parse("level_2 = 5\nlevel_3 = 99\nlevel_4 = x\nfoo = 1\nno equals\nsilver_weight = 0\n");
        assert_eq!(s.levels, [5, 9, 12]);
        assert_eq!(s.weights, [0, 45, 20]);
        assert_eq!(notes.len(), 4, "{notes:?}");
        // levels out of order are sorted; all weights 0 fall back
        let (s, notes) = parse("level_2 = 11\nlevel_3 = 4\nsilver_weight = 0\ngold_weight = 0\nprismatic_weight = 0\n");
        assert_eq!(s.levels, [4, 11, 12]);
        assert_eq!(s.weights, Settings::default().weights);
        assert_eq!(notes.len(), 2, "{notes:?}");
    }

    #[test]
    fn when_each_pick_comes() {
        let s = Settings::default();
        assert!(!due(&s, 0, 1, super::super::OPEN_AT - 1));
        assert!(due(&s, 0, 1, super::super::OPEN_AT));
        assert!(!due(&s, 1, 5, 9_000) && due(&s, 1, 6, 9_000));
        assert!(!due(&s, 3, 11, 10 * 3600 - 1) && due(&s, 3, 11, 10 * 3600) && due(&s, 3, 12, 100));
        assert!(!due(&s, 4, 12, 100_000), "only four");
        let off = Settings { catch_up_min: 0, ..s };
        assert!(!due(&off, 3, 11, 50 * 3600));
    }

    #[test]
    fn the_opening_panel_is_off_unless_asked_for() {
        assert!(!Settings::default().opening);
        assert!(parse("show_opening = 1").0.opening);
        assert!(!parse("show_opening = 0").0.opening);
    }

    #[test]
    fn the_effects_are_drawn_as_the_file_says() {
        assert_eq!(Settings::default().effects, EFFECTS_AUTO);
        assert_eq!(parse("battlefield_effects = 1").0.effects, EFFECTS_SQUARES);
        assert_eq!(parse("battlefield_effects = 0").0.effects, EFFECTS_OFF);
        let (s, notes) = parse("battlefield_effects = 3");
        assert!(s.effects == EFFECTS_AUTO && notes[0].contains("outside 0-2"), "{notes:?}");
    }
}
