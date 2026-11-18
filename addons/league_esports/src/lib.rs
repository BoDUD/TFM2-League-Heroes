//! 英雄联盟赛事（用户 2026-11-18：「能不能做个赛事mod啊 现在比赛赛事不像英雄联盟 每年也太固定了」；选了「换成英雄联盟的
//! 名字」「每年赛制会变」「赛程日期和赛事每年浮动」，淘汰阶段「固定按我的 BO7」，赛程「挪日期 + 有年份不办洲际赛」；
//! 无畏征召用游戏自带的）。
//!
//! 生涯里的赛事是游戏自己的：6 个赛区各一个一级、二级联赛（春季、夏季，季后赛、升降级），4 个国际赛（东 / 西挑战者杯、
//! 大师赛、冠军赛：16 队瑞士轮进 8 队双败淘汰），每年的日程（`YearSchedule`：一串（日期，事件））和赛制都一样。
//! 存档里看到的（0.0.1 的探测，2028 年的生涯）：
//! - 比赛在抽签时整届建好，各带日期；主赛事（大师赛 / 冠军赛）的日期就是日程里 `TournamentGroupMatch {index, round}` /
//!   `TournamentMatch` 的日子，挑战者杯的小组赛早 4 天、淘汰赛早 3 天（[`LEAD`]）。
//! - 瑞士轮游戏自己定局数：BO1，决定晋级、淘汰的场次 BO3（2027 年秋天起；2026 年还是全程 BO3）。
//! - 每个杯赛每届一条 `TournamentCompetition`，抽签时才有；春天没有冠军赛那一届，游戏照样走日程。
//!
//! - **名字**（0.0.1，`text/ui.i18n`）：LCK / LPL / LEC / LCS / CBLOL / LJL，二级联赛 LCK CL / LDL / ERL / NACL /
//!   CBLOL 学院 / LJL 学院，季中冠军赛 MSI，全球总决赛，洲际赛（东部 / 西部）。
//! - **每年的规则**（0.1.0，[`Rules`]，[`roll`]：新的一年第一次有比赛等着打时定，存进存档，读档不变；随机种子每个存档一个）：
//!   - 各联赛常规赛 BO1 或 BO3（一级联赛三成 BO1，二级联赛一半一半）；
//!   - 瑞士轮不随年份变：全程 BO1（用户 11-18 看到「瑞士轮全程 BO3」的公告后：「瑞士轮应该改成BO1吧？淘汰赛BO7就行」）；
//!     settings.ini `swiss_bo1 = 0` 回到游戏自己的（BO1，决定晋级、淘汰的场次 BO3）。0.1.0 存下的规则里还有每年的瑞士轮
//!     赛制（`swiss_bo3`）：[`migrate`] 去掉它，公告过「全程 BO3」而瑞士轮还没打的，补发一条赛制调整的新闻；
//!   - 洲际赛（东 / 西挑战者杯）上半年、下半年各自办不办（三成停办）；
//!   - 上半年、下半年国际赛的赛程前后挪几天（[`room`]：前面不早于升降级赛之后，后面不晚于下个赛季开始 / 赛季补丁）；
//!   - MSI、全球总决赛的主办赛区（不连着两年同一个赛区，两项不在同一个赛区）和奖金池（Tournament 记录的 `prize_money`）。
//!   - 第一次装上时那一年已经开打：常规赛和上半年都照原版，只定下半年，下半年的赛程一定挪（这次的试验）。
//!   - 淘汰阶段（季后赛、决赛、升降级赛、国际赛淘汰赛）不归本包：用户的 series_length（BO7）管；本包只改常规赛和瑞士轮。
//! - **赛程**：抽签之前改日程（[`plan_a`]：瑞士轮挪 k 天，往后挪时淘汰赛一起挪；洲际赛停办就去掉它的两次抽签）。
//!   抽签后核对主赛事的小组赛是不是落在挪过的日子上（[`plan_b`]）：是，往前挪的淘汰赛这时跟上；不是（游戏没按改过的日程
//!   排），挪过的事件放回原来的日子，发一条说明。改之前的日程存进存档（`orig_schedule:<年>`）。
//! - **赛制公告**：定下一年的规则时，往用户队伍的新闻里发一条（`news_push`）。
//! - **局数**（[`target`]）：每 10 秒（或者比赛表变了）看一遍还没打的比赛（`running_state` = `Wait`），常规赛按这一年的
//!   规则、瑞士轮按 `swiss_bo1` 改 `need_win`。
//! - **探测**（0.0.1）：载入生涯后写一次 `league_esports_probe.json`（只读）。
//! - 日志 `league_esports.log`：规则、公告、改日程（写之后再读一遍对照）、抽签后的核对、改了多少场局数、赛季切换。
//!
//! 设置：本包文件夹的 `settings.ini`：`yearly_formats`（每年变赛制）、`schedule_float`（赛程浮动、洲际赛停办）、
//! `swiss_bo1`（瑞士轮全程 BO1）、`probe`（探测），1 开 0 关。

use std::collections::{BTreeMap, BTreeSet};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex, OnceLock, PoisonError};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use mod_api_stable::*;

const ID: &str = "league_esports";
const VERSION: &str = env!("CARGO_PKG_VERSION");

// ===================== 文件、日志 =====================

fn data_dir() -> PathBuf {
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir;
        }
    }
    PathBuf::from(".")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(|| match std::env::var_os("LEAGUE_ESPORTS_LOG") {
    Some(p) => PathBuf::from(p),
    None => data_dir().join("league_esports.log"),
});
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn wlog(msg: impl AsRef<str>) {
    let mut file = LOG_FILE.lock().unwrap_or_else(PoisonError::into_inner);
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

static DIR: OnceLock<PathBuf> = OnceLock::new();

/// This mod's folder (the DLL's).
fn mod_dir() -> PathBuf {
    DIR.get_or_init(|| {
        module_path().and_then(|dll| dll.parent().map(|p| p.to_path_buf())).unwrap_or_else(|| PathBuf::from("mods").join(ID))
    })
    .clone()
}

fn anchor() {}

#[cfg(windows)]
fn module_path() -> Option<PathBuf> {
    use std::ffi::{c_void, OsString};
    use std::os::windows::ffi::OsStringExt;

    #[link(name = "kernel32")]
    extern "system" {
        fn GetModuleHandleExW(flags: u32, name: *const u16, module: *mut *mut c_void) -> i32;
        fn GetModuleFileNameW(module: *mut c_void, filename: *mut u16, size: u32) -> u32;
    }
    const FROM_ADDRESS: u32 = 0x4;
    const UNCHANGED_REFCOUNT: u32 = 0x2;
    let mut module: *mut c_void = std::ptr::null_mut();
    // SAFETY: FROM_ADDRESS takes any address inside the module; the handle keeps no reference to release.
    let ok = unsafe { GetModuleHandleExW(FROM_ADDRESS | UNCHANGED_REFCOUNT, anchor as *const u16, &mut module) };
    if ok == 0 || module.is_null() {
        return None;
    }
    let mut buf = vec![0u16; 32768];
    // SAFETY: the buffer holds buf.len() UTF-16 units.
    let len = unsafe { GetModuleFileNameW(module, buf.as_mut_ptr(), buf.len() as u32) } as usize;
    (len > 0 && len < buf.len()).then(|| PathBuf::from(OsString::from_wide(&buf[..len])))
}

#[cfg(not(windows))]
fn module_path() -> Option<PathBuf> {
    None
}

// ===================== 设置 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Config {
    /// every year's formats (regular seasons, Swiss stages, hosts, prize pools, the announcement)
    pub yearly_formats: bool,
    /// the international stages' dates move and Rift Rivals is sometimes not held
    pub schedule_float: bool,
    /// every Swiss match BO1 (off: as the game has them - BO1, the matches that decide advancing or going out BO3)
    pub swiss_bo1: bool,
    /// the read-only probe file at each load
    pub probe: bool,
}

impl Default for Config {
    fn default() -> Config {
        Config { yearly_formats: true, schedule_float: true, swiss_bo1: true, probe: true }
    }
}

/// `key = 0 / 1` lines of settings.ini (`;` / `#` comments); unknown or missing keys keep the defaults.
pub fn parse_config(text: &str) -> Config {
    let mut c = Config::default();
    for line in text.trim_start_matches('\u{feff}').lines() {
        let line = line.split([';', '#']).next().unwrap_or("").trim();
        let Some((k, v)) = line.split_once('=') else { continue };
        let on = v.trim() != "0";
        match k.trim() {
            "yearly_formats" => c.yearly_formats = on,
            "schedule_float" => c.schedule_float = on,
            "swiss_bo1" => c.swiss_bo1 = on,
            "probe" => c.probe = on,
            _ => {}
        }
    }
    c
}

fn load_config() -> Config {
    std::fs::read_to_string(mod_dir().join("settings.ini")).map(|t| parse_config(&t)).unwrap_or_default()
}

// ===================== 日期 =====================

/// Days since 1970-01-01 of a civil date.
pub fn days_from_civil(y: i64, m: i64, d: i64) -> i64 {
    let y = if m <= 2 { y - 1 } else { y };
    let era = if y >= 0 { y } else { y - 399 } / 400;
    let yoe = y - era * 400;
    let mp = (m + 9) % 12;
    let doy = (153 * mp + 2) / 5 + d - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146_097 + doe - 719_468
}

/// The civil date of a day number.
pub fn civil_from_days(z: i64) -> (i64, i64, i64) {
    let z = z + 719_468;
    let era = if z >= 0 { z } else { z - 146_096 } / 146_097;
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    (if m <= 2 { y + 1 } else { y }, m, d)
}

/// The day number of a `YYYY-MM-DD…` string.
pub fn day_of(s: &str) -> Option<i64> {
    let y = s.get(0..4)?.parse().ok()?;
    let m = s.get(5..7)?.parse().ok()?;
    let d = s.get(8..10)?.parse().ok()?;
    Some(days_from_civil(y, m, d))
}

pub fn date_str(day: i64) -> String {
    let (y, m, d) = civil_from_days(day);
    format!("{y:04}-{m:02}-{d:02}")
}

/// `s` moved `k` days, its time of day (if any) kept.
pub fn shift_date(s: &str, k: i64) -> Option<String> {
    Some(format!("{}{}", date_str(day_of(s)? + k), s.get(10..).unwrap_or("")))
}

/// 「5 月 14 日」.
pub fn md(day: i64) -> String {
    let (_, m, d) = civil_from_days(day);
    format!("{m} 月 {d} 日")
}

// ===================== 随机 =====================

/// xorshift64*: every year's rules from the save's salt and the year.
pub struct Rng(u64);

impl Rng {
    pub fn new(seed: u64) -> Rng {
        let mut r = Rng((seed ^ 0x9E37_79B9_7F4A_7C15) | 1);
        for _ in 0..4 {
            r.next();
        }
        r
    }

    pub fn next(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x >> 12;
        x ^= x << 25;
        x ^= x >> 27;
        self.0 = x;
        x.wrapping_mul(0x2545_F491_4F6C_DD1D)
    }

    pub fn below(&mut self, n: u64) -> u64 {
        (self.next() >> 11) % n.max(1)
    }

    pub fn range(&mut self, lo: i64, hi: i64) -> i64 {
        lo + self.below((hi - lo + 1).max(1) as u64) as i64
    }

    pub fn chance(&mut self, pct: u64) -> bool {
        self.below(100) < pct
    }
}

// ===================== 每年的规则 =====================

/// The leagues in the League records' order (id 0-5 TACK … TACJ, 6-11 their second divisions), as this mod names them.
pub const LEAGUES: [&str; 12] =
    ["LCK", "LPL", "LEC", "LCS", "CBLOL", "LJL", "LCK CL", "LDL", "ERL", "NACL", "CBLOL 学院", "LJL 学院"];
/// Host regions (region_id 0-5) with a host city each.
pub const HOSTS: [&str; 6] = ["韩国首尔", "中国上海", "德国柏林", "美国洛杉矶", "巴西圣保罗", "日本东京"];
/// Each half's main event (its `ty`) and its name here.
pub const MAIN: [&str; 2] = ["Masters", "Champions"];
pub const CUP: [&str; 2] = ["季中冠军赛 MSI", "全球总决赛"];

/// One year's formats.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Rules {
    pub year: i64,
    /// regular-season series length per league (1 or 3; 0 = the game's own)
    pub regular: [u8; 12],
    /// Rift Rivals (the Challengers cups) held - spring, autumn
    pub rivals: [bool; 2],
    /// days the half's international stage moves - spring, autumn (after [`settle`]: the move applied)
    pub shift: [i64; 2],
    /// host regions - MSI, Worlds
    pub host: [usize; 2],
    /// prize pools in % of the game's own - MSI, Worlds
    pub prize: [u32; 2],
    /// set up after the year's league season started: the regular seasons and the spring stay the game's
    pub from_autumn: bool,
}

/// The year's rules, rolled from the save's `salt` (and kept apart from `last` year's hosts).
pub fn roll(year: i64, salt: u64, last: Option<&Rules>, from_autumn: bool) -> Rules {
    let mut r = Rng::new(salt ^ (year as u64).wrapping_mul(0x0000_0100_0000_01B3));
    let regular: [u8; 12] = std::array::from_fn(|i| {
        let bo1 = r.chance(if i < 6 { 30 } else { 50 });
        if from_autumn {
            0
        } else if bo1 {
            1
        } else {
            3
        }
    });
    let rivals = [r.chance(70), r.chance(70)];
    let mut shift = [r.range(-3, 0), r.range(-3, 2)];
    if from_autumn {
        // the first year's autumn is the test: its stage always moves
        shift = [0, [-3, -2, -1, 1, 2][r.below(5) as usize]];
    }
    let mut host = [r.below(6) as usize, r.below(6) as usize];
    for _ in 0..64 {
        let repeat = last.is_some_and(|l| l.host[0] == host[0] || l.host[1] == host[1]);
        if !repeat && host[0] != host[1] {
            break;
        }
        host = [r.below(6) as usize, r.below(6) as usize];
    }
    let prize = [r.range(90, 130) as u32, r.range(90, 140) as u32];
    let mut rules = Rules { year, regular, rivals, shift, host, prize, from_autumn };
    if from_autumn {
        rules.rivals[0] = true;
    }
    rules
}

fn join<T: ToString>(xs: &[T]) -> String {
    xs.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",")
}

impl Rules {
    /// `key=v,v;…` for the save.
    pub fn to_text(&self) -> String {
        let b = |x: bool| if x { "1" } else { "0" };
        format!(
            "year={};regular={};rivals={},{};shift={};host={};prize={};from_autumn={}",
            self.year,
            join(&self.regular),
            b(self.rivals[0]),
            b(self.rivals[1]),
            join(&self.shift),
            join(&self.host),
            join(&self.prize),
            b(self.from_autumn)
        )
    }

    pub fn from_text(s: &str) -> Option<Rules> {
        let mut m = BTreeMap::new();
        for part in s.split(';') {
            let (k, v) = part.split_once('=')?;
            m.insert(k, v);
        }
        let nums = |k: &str| -> Option<Vec<i64>> { m.get(k)?.split(',').map(|x| x.parse().ok()).collect() };
        let two = |k: &str| -> Option<[i64; 2]> {
            let v = nums(k)?;
            (v.len() == 2).then(|| [v[0], v[1]])
        };
        let regular = nums("regular")?;
        if regular.len() != 12 {
            return None;
        }
        Some(Rules {
            year: m.get("year")?.parse().ok()?,
            regular: std::array::from_fn(|i| regular[i] as u8),
            rivals: two("rivals")?.map(|x| x != 0),
            shift: two("shift")?,
            host: two("host")?.map(|x| x as usize),
            prize: two("prize")?.map(|x| x as u32),
            from_autumn: *m.get("from_autumn")? != "0",
        })
    }
}

// ===================== 日程 =====================

/// The Challengers cups play their Swiss stage this many days before the main event's (their knockouts 3 days before).
pub const LEAD: i64 = 4;

/// One schedule entry: its date and its event as compact JSON (`"StartRecruit"`, `{"LeagueMatch":{"index":0,"round":0}}` …).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Entry {
    pub date: String,
    pub event: String,
}

/// JSON without the whitespace outside its strings.
pub fn compact(json: &str) -> String {
    let mut out = String::with_capacity(json.len());
    let (mut in_str, mut esc) = (false, false);
    for c in json.chars() {
        if in_str {
            out.push(c);
            if esc {
                esc = false;
            } else if c == '\\' {
                esc = true;
            } else if c == '"' {
                in_str = false;
            }
        } else if !c.is_whitespace() {
            in_str = c == '"';
            out.push(c);
        }
    }
    out
}

/// The raw top-level elements of a JSON array.
pub fn elements(json: &str) -> Option<Vec<&str>> {
    let inner = json.trim().strip_prefix('[')?.strip_suffix(']')?;
    let mut out = Vec::new();
    let (mut depth, mut start, mut in_str, mut esc) = (0i32, 0usize, false, false);
    for (i, c) in inner.char_indices() {
        if in_str {
            if esc {
                esc = false;
            } else if c == '\\' {
                esc = true;
            } else if c == '"' {
                in_str = false;
            }
            continue;
        }
        match c {
            '"' => in_str = true,
            '[' | '{' => depth += 1,
            ']' | '}' => depth -= 1,
            ',' if depth == 0 => {
                out.push(inner[start..i].trim());
                start = i + 1;
            }
            _ => {}
        }
    }
    let last = inner[start..].trim();
    if !last.is_empty() {
        out.push(last);
    }
    Some(out)
}

fn unquote(s: &str) -> String {
    s.trim().trim_matches('"').to_string()
}

/// A `schedules` array (`[[date, event], …]`).
pub fn parse_schedule(json: &str) -> Option<Vec<Entry>> {
    elements(json)?
        .into_iter()
        .map(|e| {
            let pair = elements(e)?;
            (pair.len() == 2).then(|| Entry { date: unquote(pair[0]), event: compact(pair[1]) })
        })
        .collect()
}

/// The JSON array of a schedule.
pub fn schedule_json(list: &[Entry]) -> String {
    let items: Vec<String> = list.iter().map(|e| format!("[\"{}\",{}]", e.date, e.event)).collect();
    format!("[{}]", items.join(","))
}

/// An event's kind and its `ty` (`Masters`, `Spring` …) if it has one.
pub fn kind(event: &str) -> (String, Option<String>) {
    let s = compact(event);
    if let Some(body) = s.strip_prefix("{\"") {
        let key = body.split('"').next().unwrap_or("").to_string();
        let ty = s.split("\"ty\":\"").nth(1).and_then(|t| t.split('"').next()).map(String::from);
        (key, ty)
    } else {
        (s.trim_matches('"').to_string(), None)
    }
}

/// The international stage's own events (what moves).
pub fn is_stage(kind: &str) -> bool {
    matches!(kind, "TournamentGroupMatch" | "DrawingTournament" | "TournamentMatch")
}

fn is_challengers_draw(kind: &str, ty: Option<&str>) -> bool {
    kind.starts_with("Drawing") && ty.is_some_and(|t| t.starts_with("Challengers"))
}

/// Which entries are a half's (after its main group draw - or on its day - until the next season's creation or the year's
/// season patch), and that draw's index. Half 0: the Masters draw; half 1: the Champions draw.
pub fn window(list: &[Entry], half: usize) -> Option<(usize, Vec<bool>)> {
    let main = (String::from("DrawingTournamentGroup"), Some(String::from(MAIN[half])));
    let draw = list.iter().position(|e| kind(&e.event) == main)?;
    let draw_day = day_of(&list[draw].date)?;
    let end = (draw + 1..list.len())
        .find(|&i| matches!(kind(&list[i].event).0.as_str(), "LeagueScheduleCreate" | "SeasonPatch"))
        .unwrap_or(list.len());
    let inside = (0..list.len()).map(|i| i != draw && i < end && (i > draw || day_of(&list[i].date) == Some(draw_day))).collect();
    Some((draw, inside))
}

/// A half's stage in a schedule and the room it has to move.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Room {
    pub draw_day: i64,
    /// the first day the main event's Swiss stage may start: after the promotion series, with the Challengers' lead
    pub lo: i64,
    /// the last day the stage may end: before the next season's creation (or the year's season patch)
    pub hi: i64,
    /// the main event's first Swiss day, its first knockout day and the final's day
    pub first: i64,
    pub knockout: i64,
    pub last: i64,
}

pub fn room(list: &[Entry], half: usize) -> Option<Room> {
    let (draw, inside) = window(list, half)?;
    let draw_day = day_of(&list[draw].date)?;
    let (mut first, mut knockout, mut last, mut promo) = (None::<i64>, None::<i64>, None::<i64>, draw_day);
    let mut end_day = None;
    for (i, e) in list.iter().enumerate() {
        let (kd, _) = kind(&e.event);
        let d = day_of(&e.date)?;
        if i > draw && end_day.is_none() && matches!(kd.as_str(), "LeagueScheduleCreate" | "SeasonPatch") {
            end_day = Some(d);
        }
        if !inside[i] {
            continue;
        }
        match kd.as_str() {
            "TournamentGroupMatch" => first = Some(first.map_or(d, |f| f.min(d))),
            "TournamentMatch" => knockout = Some(knockout.map_or(d, |f| f.min(d))),
            "LeaguePromotion" => promo = promo.max(d),
            _ => {}
        }
        if is_stage(&kd) {
            last = Some(last.map_or(d, |l| l.max(d)));
        }
    }
    let (first, knockout, last) = (first?, knockout?, last?);
    let hi = match end_day {
        Some(d) => d - 1,
        None => days_from_civil(civil_from_days(first).0, 12, 30),
    };
    Some(Room { draw_day, lo: promo + 1 + LEAD, hi, first, knockout, last })
}

/// The move `k` inside the room (0 when the stage has none).
pub fn clamp_shift(room: &Room, k: i64) -> i64 {
    let (min, max) = (room.lo - room.first, room.hi - room.last);
    if min > 0 || max < 0 {
        0
    } else {
        k.clamp(min, max)
    }
}

/// `list` with the half's entries that `pick` chooses moved `k` days and those `drop` chooses gone; still in date order.
fn rebuild(
    list: &[Entry],
    half: usize,
    k: i64,
    pick: impl Fn(&str, Option<&str>) -> bool,
    drop: impl Fn(&str, Option<&str>) -> bool,
) -> Option<Vec<Entry>> {
    let (_, inside) = window(list, half)?;
    let mut out = Vec::with_capacity(list.len());
    for (i, e) in list.iter().enumerate() {
        let (kd, ty) = kind(&e.event);
        if inside[i] && drop(&kd, ty.as_deref()) {
            continue;
        }
        if inside[i] && k != 0 && pick(&kd, ty.as_deref()) {
            out.push(Entry { date: shift_date(&e.date, k)?, event: e.event.clone() });
        } else {
            out.push(e.clone());
        }
    }
    out.sort_by_key(|e| day_of(&e.date).unwrap_or(i64::MAX));
    Some(out)
}

/// Before the half's group draw: its Swiss days move `k` (clamped to the room; moving later, the knockout draw and the
/// knockouts come along), and without Rift Rivals the Challengers cups' group and knockout draws go. Returns the new
/// schedule and the move applied.
pub fn plan_a(list: &[Entry], half: usize, k: i64, rivals: bool) -> Option<(Vec<Entry>, i64)> {
    let k = clamp_shift(&room(list, half)?, k);
    let pick = |kd: &str, _: Option<&str>| if k < 0 { kd == "TournamentGroupMatch" } else { is_stage(kd) };
    let drop = |kd: &str, ty: Option<&str>| !rivals && is_challengers_draw(kd, ty);
    Some((rebuild(list, half, k, pick, drop)?, k))
}

/// After the half's group draw. The main event's group matches on the moved days (`moved`): an earlier stage's knockout
/// draw and knockouts move too. Not on them (the game drew from its own days): every moved event goes back to its day in
/// `orig`. A Challengers cup the game drew anyway (its `ty` in `drawn`) gets its knockout draw back.
pub fn plan_b(list: &[Entry], orig: &[Entry], half: usize, k: i64, moved: bool, drawn: &[&str]) -> Option<Vec<Entry>> {
    let mut out = if moved && k < 0 {
        rebuild(list, half, k, |kd, _| kd == "DrawingTournament" || kd == "TournamentMatch", |_, _| false)?
    } else if !moved && k != 0 {
        restore(list, orig, half)?
    } else {
        list.to_vec()
    };
    let (_, inside) = window(&out, half)?;
    let (_, orig_inside) = window(orig, half)?;
    for ty in drawn {
        let want = (String::from("DrawingTournament"), Some(String::from(*ty)));
        if out.iter().zip(&inside).any(|(e, &i)| i && kind(&e.event) == want) {
            continue;
        }
        if let Some(e) = orig.iter().zip(&orig_inside).find(|(e, &i)| i && kind(&e.event) == want).map(|(e, _)| e) {
            out.push(e.clone());
        }
    }
    out.sort_by_key(|e| day_of(&e.date).unwrap_or(i64::MAX));
    Some(out)
}

/// The half's stage events back on their days in `orig` (each is one of a kind there: `{index, round}` / `{ty}`).
fn restore(list: &[Entry], orig: &[Entry], half: usize) -> Option<Vec<Entry>> {
    let (_, orig_inside) = window(orig, half)?;
    let days: BTreeMap<&str, &str> = orig
        .iter()
        .zip(&orig_inside)
        .filter(|(e, &i)| i && is_stage(&kind(&e.event).0))
        .map(|(e, _)| (e.event.as_str(), e.date.as_str()))
        .collect();
    let (_, inside) = window(list, half)?;
    let mut out: Vec<Entry> = list
        .iter()
        .zip(&inside)
        .map(|(e, &i)| match days.get(e.event.as_str()) {
            Some(d) if i => Entry { date: d.to_string(), event: e.event.clone() },
            _ => e.clone(),
        })
        .collect();
    out.sort_by_key(|e| day_of(&e.date).unwrap_or(i64::MAX));
    Some(out)
}

/// How many Challengers draws a half has.
pub fn challengers_draws(list: &[Entry], half: usize) -> usize {
    let Some((_, inside)) = window(list, half) else { return 0 };
    list.iter().zip(&inside).filter(|(e, &i)| i && { let (kd, ty) = kind(&e.event); is_challengers_draw(&kd, ty.as_deref()) }).count()
}

/// Whether `now` still carries [`plan_a`]'s changes to `orig` (true when it cannot tell: leave it then).
pub fn floated(now: &[Entry], orig: &[Entry], half: usize, k: i64, rivals: bool) -> bool {
    let (Some(a), Some(b)) = (room(now, half), room(orig, half)) else { return true };
    a.first == b.first + k && (rivals || challengers_draws(now, half) == 0)
}

// ===================== 局数 =====================

/// What a match is to this mod.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stage {
    /// a league's regular season (its index in [`LEAGUES`])
    Regular(usize),
    /// a Swiss stage match of a half (the main event's or that half's Challengers cups')
    Swiss(usize),
}

/// The need_win the year's rules (and `swiss_bo1`) give a match (None: leave it as the game has it).
pub fn target(rules: &Rules, stage: Stage, swiss_bo1: bool) -> Option<i64> {
    match stage {
        Stage::Regular(league) => match rules.regular.get(league)? {
            1 => Some(1),
            3 => Some(2),
            _ => None,
        },
        Stage::Swiss(half) => (swiss_bo1 && half < 2 && !(rules.from_autumn && half == 0)).then_some(1),
    }
}

// ===================== 公告 =====================

fn bo(n: u8) -> &'static str {
    match n {
        1 => "BO1",
        3 => "BO3",
        _ => "原版",
    }
}

/// The Swiss stages' format in words.
pub fn swiss_words(swiss_bo1: bool) -> &'static str {
    if swiss_bo1 {
        "全程 BO1"
    } else {
        "照原版（BO1，决定晋级、淘汰的场次 BO3）"
    }
}

/// The year's announcement: (title, content). `days`: each half's main event, its first Swiss day and its final.
pub fn announcement(rules: &Rules, days: [Option<(i64, i64)>; 2], swiss_bo1: bool) -> (String, String) {
    let y = rules.year;
    let when = |d: Option<(i64, i64)>| d.map_or(String::new(), |(a, b)| format!("，{}开打、{}决赛", md(a), md(b)));
    let rivals = |held: bool| if held { "照常举办" } else { "停办，没进国际赛的队伍休整" };
    let mut lines = Vec::new();
    if !rules.from_autumn {
        let lg: Vec<String> = (0..12).map(|i| format!("{} {}", LEAGUES[i], bo(rules.regular[i]))).collect();
        lines.push(format!("联赛常规赛：{}。季后赛、决赛、升降级赛照你的局数设置。", lg.join("、")));
    }
    for half in [0, 1] {
        if half == 0 && rules.from_autumn {
            continue;
        }
        lines.push(format!(
            "{}：{}主办，瑞士轮{}{}；奖金池为原版的 {}%。",
            CUP[half],
            HOSTS[rules.host[half] % HOSTS.len()],
            swiss_words(swiss_bo1),
            when(days[half]),
            rules.prize[half]
        ));
        lines.push(format!("{}洲际赛：{}。", if half == 0 { "上半年" } else { "下半年" }, rivals(rules.rivals[half])));
    }
    let title = if rules.from_autumn { format!("{y} 下半年国际赛公告") } else { format!("{y} 赛季赛制公告") };
    (title, lines.join("\n"))
}

// ===================== 读写记录 =====================

/// The integers of a JSON fragment, in order (a match list's ids; nested lists come out flat).
pub fn ints(json: &str) -> Vec<usize> {
    let mut out = Vec::new();
    let mut cur: Option<usize> = None;
    for ch in json.chars() {
        match ch.to_digit(10) {
            Some(d) => cur = Some(cur.unwrap_or(0).saturating_mul(10).saturating_add(d as usize)),
            None => out.extend(cur.take()),
        }
    }
    out.extend(cur);
    out
}

/// The numbers of a JSON array (a prize list).
pub fn floats(json: &str) -> Vec<f64> {
    elements(json).unwrap_or_default().into_iter().filter_map(|v| v.parse().ok()).collect()
}

fn ids_at(ctx: &StableServerCtx<'_>, kind: RecordKindV1, id: usize, path: &str) -> Vec<usize> {
    ctx.record_get_json(kind, id, path).map(|s| ints(&s)).unwrap_or_default()
}

fn finalized(ctx: &StableServerCtx<'_>, kind: RecordKindV1, id: usize) -> bool {
    ctx.record_get_json(kind, id, "finalized").is_some_and(|v| v.trim() == "true")
}

/// The year schedules: year → record id.
fn year_schedules(ctx: &StableServerCtx<'_>) -> BTreeMap<i64, usize> {
    let mut out = BTreeMap::new();
    for id in ctx.record_ids(RecordKindV1::YearSchedule) {
        if let Some(year) = ctx.record_get_json(RecordKindV1::YearSchedule, id, "year").and_then(|y| y.trim().parse().ok()) {
            out.insert(year, id);
        }
    }
    out
}

fn read_schedule(ctx: &StableServerCtx<'_>, id: usize) -> Option<Vec<Entry>> {
    parse_schedule(&ctx.record_get_json(RecordKindV1::YearSchedule, id, "schedules")?)
}

/// Writes a year's schedule; (accepted, reads back the same).
fn write_schedule(ctx: &mut StableServerCtx<'_>, id: usize, list: &[Entry]) -> (bool, bool) {
    let ok = ctx.record_set_json(RecordKindV1::YearSchedule, id, "schedules", &schedule_json(list));
    (ok, read_schedule(ctx, id).as_deref() == Some(list))
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum Run {
    Wait,
    Over,
    Other,
}

fn run_state(ctx: &StableServerCtx<'_>, m: usize) -> Run {
    match ctx.record_get_json(RecordKindV1::Match, m, "running_state").map(|s| compact(&s)) {
        None => Run::Over,
        Some(s) if s == "null" => Run::Over,
        Some(s) if s == "\"Wait\"" => Run::Wait,
        Some(_) => Run::Other,
    }
}

fn match_day(ctx: &StableServerCtx<'_>, m: usize) -> Option<i64> {
    day_of(&ctx.record_get_string(RecordKindV1::Match, m, "date")?)
}

/// A tournament competition (one edition of a cup).
struct Cup {
    id: usize,
    ty: String,
    finalized: bool,
    year: Option<i64>,
    half: usize,
    group: Vec<usize>,
    first_group: Option<i64>,
    first_knockout: Option<i64>,
}

fn cups(ctx: &StableServerCtx<'_>) -> Vec<Cup> {
    let kind = RecordKindV1::TournamentCompetition;
    ctx.record_ids(kind)
        .into_iter()
        .map(|id| {
            let ty = ctx.record_get_string(kind, id, "ty").unwrap_or_default();
            let group = ids_at(ctx, kind, id, "group_matches");
            let first_group = group.first().and_then(|&m| match_day(ctx, m));
            let first_knockout = ids_at(ctx, kind, id, "tournament_matches").first().and_then(|&m| match_day(ctx, m));
            let half = match ty.as_str() {
                "Masters" => 0,
                "Champions" => 1,
                _ => usize::from(first_group.is_some_and(|d| civil_from_days(d).1 > 7)),
            };
            Cup {
                id,
                finalized: finalized(ctx, kind, id),
                year: first_group.map(|d| civil_from_days(d).0),
                ty,
                half,
                group,
                first_group,
                first_knockout,
            }
        })
        .collect()
}

/// The open league competitions: (id, its league's index in [`LEAGUES`]).
fn open_leagues(ctx: &StableServerCtx<'_>) -> Vec<(usize, usize)> {
    let mut league_of = BTreeMap::new();
    for l in ctx.record_ids(RecordKindV1::League) {
        if l < LEAGUES.len() {
            for c in ids_at(ctx, RecordKindV1::League, l, "competitions") {
                league_of.insert(c, l);
            }
        }
    }
    ctx.record_ids(RecordKindV1::LeagueCompetition)
        .into_iter()
        .filter(|&id| !finalized(ctx, RecordKindV1::LeagueCompetition, id))
        .filter_map(|id| Some((id, *league_of.get(&id)?)))
        .collect()
}

/// The teams the players run (news goes to them).
fn player_teams(ctx: &StableServerCtx<'_>) -> Vec<usize> {
    let mut out: Vec<usize> = (0..4).filter_map(|p| ctx.player_team_id(p)).collect();
    out.sort();
    out.dedup();
    out
}

fn news(ctx: &mut StableServerCtx<'_>, title: &str, content: &str) {
    let teams = player_teams(ctx);
    let mut sent = Vec::new();
    for &t in &teams {
        sent.push(ctx.news_push(t, title, content, "英雄联盟电竞"));
    }
    wlog(format!("NEWS to teams {teams:?} (sent {sent:?}): {title}\n{content}"));
}

// ===================== 服务端 =====================

const SALT_KEY: &str = "salt";
const RESCAN: Duration = Duration::from_secs(10);

#[derive(Default)]
struct State {
    probed: bool,
    seq: u64,
    cfg: Option<Config>,
    match_count: usize,
    scanned: Option<Instant>,
    /// matches known to be over: never looked at again
    done: BTreeSet<usize>,
    /// (year, half) whose changed schedule was already reported as left alone
    noted: BTreeSet<(i64, usize)>,
}

static STATE: Mutex<Option<State>> = Mutex::new(None);

fn salt(ctx: &mut StableServerCtx<'_>) -> u64 {
    if let Some(s) = ctx.save_get_string(SALT_KEY).and_then(|s| s.parse().ok()) {
        return s;
    }
    let s = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_nanos() as u64).unwrap_or(0x5EED);
    let kept = ctx.save_set_string(SALT_KEY, &s.to_string());
    wlog(format!("SALT new for this save: {s} (kept in the save: {kept})"));
    s
}

fn rules_key(year: i64) -> String {
    format!("rules:{year}")
}

fn orig_key(year: i64) -> String {
    format!("orig_schedule:{year}")
}

fn load_rules(ctx: &StableServerCtx<'_>, year: i64) -> Option<Rules> {
    ctx.save_get_string(&rules_key(year)).and_then(|s| Rules::from_text(&s))
}

fn load_orig(ctx: &StableServerCtx<'_>, year: i64) -> Option<Vec<Entry>> {
    ctx.save_get_string(&orig_key(year)).and_then(|s| parse_schedule(&s))
}

/// The next match day: the earliest waiting match of the open competitions.
fn next_match_day(ctx: &StableServerCtx<'_>, st: &mut State, leagues: &[(usize, usize)], cups: &[Cup]) -> Option<i64> {
    let mut lists = Vec::new();
    for &(id, _) in leagues {
        for path in ["matches", "playoffs", "promotion_series"] {
            lists.push(ids_at(ctx, RecordKindV1::LeagueCompetition, id, path));
        }
    }
    for c in cups.iter().filter(|c| !c.finalized) {
        lists.push(c.group.clone());
        lists.push(ids_at(ctx, RecordKindV1::TournamentCompetition, c.id, "tournament_matches"));
    }
    let mut best: Option<i64> = None;
    for m in lists.into_iter().flatten() {
        if st.done.contains(&m) {
            continue;
        }
        match run_state(ctx, m) {
            Run::Over => {
                st.done.insert(m);
            }
            Run::Wait => {
                if let Some(d) = match_day(ctx, m) {
                    best = Some(best.map_or(d, |b| b.min(d)));
                }
            }
            Run::Other => {}
        }
    }
    best
}

/// The prize pools of MSI and Worlds: the game's own (kept in the save; when the pool is not what this mod last wrote,
/// the game or another mod set it - that is the new base) times the year's %.
fn set_prizes(ctx: &mut StableServerCtx<'_>, rules: &Rules) {
    let kind = RecordKindV1::Tournament;
    for id in ctx.record_ids(kind) {
        let ty = ctx.record_get_string(kind, id, "ty").unwrap_or_default();
        let pct = match ty.as_str() {
            "Masters" if !rules.from_autumn => rules.prize[0],
            "Champions" => rules.prize[1],
            _ => continue,
        };
        let Some(now) = ctx.record_get_json(kind, id, "prize_money") else { continue };
        let (base_key, set_key) = (format!("prize_base:{id}"), format!("prize_set:{id}"));
        let same = |a: &[f64], b: &[f64]| a.len() == b.len() && a.iter().zip(b).all(|(x, y)| (x - y).abs() < 1e-6);
        let base = match (ctx.save_get_string(&base_key), ctx.save_get_string(&set_key)) {
            (Some(b), Some(s)) if same(&floats(&s), &floats(&now)) => b,
            _ => now.clone(),
        };
        let vals: Vec<String> = floats(&base).iter().map(|v| format!("{:.3}", v * pct as f64 / 100.0)).collect();
        if vals.is_empty() {
            continue;
        }
        let json = format!("[{}]", vals.join(","));
        let ok = ctx.record_set_json(kind, id, "prize_money", &json);
        if ok {
            let back = ctx.record_get_json(kind, id, "prize_money").unwrap_or_default();
            ctx.save_set_string(&base_key, &base);
            ctx.save_set_string(&set_key, &back);
        }
        wlog(format!("PRIZE {ty}: base {} x {pct}% -> {json} ({})", compact(&base), if ok { "set" } else { "REFUSED" }));
    }
}

/// The year's rules, the first time a match of the year waits: rolled, the floats for the halves still ahead written,
/// the prize pools, the announcement.
fn settle(
    ctx: &mut StableServerCtx<'_>,
    st: &mut State,
    cfg: Config,
    year: i64,
    sched: usize,
    leagues: &[(usize, usize)],
    all: &[Cup],
) -> Option<Rules> {
    let today = next_match_day(ctx, st, leagues, all)?;
    if civil_from_days(today).0 != year {
        return None;
    }
    let now = read_schedule(ctx, sched)?;
    let orig = match load_orig(ctx, year) {
        Some(o) => o,
        None => {
            ctx.save_set_string(&orig_key(year), &schedule_json(&now));
            now.clone()
        }
    };
    let first_league = orig.iter().find(|e| kind(&e.event).0 == "LeagueMatch").and_then(|e| day_of(&e.date));
    let from_autumn = first_league.is_some_and(|f| today > f);
    let salt = salt(ctx);
    let last = load_rules(ctx, year - 1);
    let mut rules = roll(year, salt, last.as_ref(), from_autumn);
    if !cfg.schedule_float {
        rules.shift = [0; 2];
        rules.rivals = [true; 2];
    }
    let mut list = orig.clone();
    let mut days = [None, None];
    for half in [0, 1] {
        let Some(r) = room(&orig, half) else {
            rules.shift[half] = 0;
            rules.rivals[half] = true;
            continue;
        };
        if (half == 0 && from_autumn) || r.draw_day <= today {
            if half == 1 || !from_autumn {
                wlog(format!("FLOAT {year} half {half}: its draw ({}) is not ahead of the next match day ({}) - as it is",
                             date_str(r.draw_day), date_str(today)));
            }
            rules.shift[half] = 0;
            rules.rivals[half] = true;
            days[half] = Some((r.first, r.last));
            continue;
        }
        match plan_a(&list, half, rules.shift[half], rules.rivals[half]) {
            Some((new, k)) => {
                rules.shift[half] = k;
                list = new;
            }
            None => {
                rules.shift[half] = 0;
                rules.rivals[half] = true;
            }
        }
        days[half] = Some((r.first + rules.shift[half], r.last + rules.shift[half]));
    }
    if list != now {
        let (ok, same) = write_schedule(ctx, sched, &list);
        wlog(format!(
            "FLOAT A {year}: moves {:?} (spring, autumn), Rift Rivals held {:?}; {} events -> {}; write {}, read back {}",
            rules.shift,
            rules.rivals,
            now.len(),
            list.len(),
            if ok { "accepted" } else { "REFUSED" },
            if same { "the same" } else { "DIFFERENT" }
        ));
        if !(ok && same) {
            if ok {
                let (back, _) = write_schedule(ctx, sched, &now);
                wlog(format!("FLOAT A {year}: the schedule put back as it was (write {back})"));
            }
            for half in [0, 1] {
                rules.shift[half] = 0;
                rules.rivals[half] = true;
                days[half] = room(&orig, half).map(|r| (r.first, r.last));
            }
        }
    }
    ctx.save_set_string(&rules_key(year), &rules.to_text());
    wlog(format!("RULES {year} (today {}): {}", date_str(today), rules.to_text()));
    set_prizes(ctx, &rules);
    let (title, content) = announcement(&rules, days, cfg.swiss_bo1);
    news(ctx, &title, &content);
    Some(rules)
}

/// Rules kept by 0.1.0 carry the yearly Swiss format (`swiss_bo3`, all BO3 some halves) the user dropped on 11-18
/// (「瑞士轮应该改成BO1吧？淘汰赛BO7就行」): the year is written again without it, and a half announced as all BO3 whose
/// Swiss stage is not over gets a news item with the format it has now.
fn migrate(ctx: &mut StableServerCtx<'_>, cfg: Config, year: i64, all: &[Cup]) {
    let Some(text) = ctx.save_get_string(&rules_key(year)) else { return };
    let Some(old) = old_swiss(&text) else { return };
    let Some(rules) = Rules::from_text(&text) else { return };
    let halves = changed_halves(&rules, old, |half| {
        all.iter().any(|c| c.ty == MAIN[half] && c.year == Some(year) && c.finalized)
    });
    if !halves.is_empty() {
        let (title, content) = correction(year, &halves, cfg.swiss_bo1);
        news(ctx, &title, &content);
    }
    let kept = ctx.save_set_string(&rules_key(year), &rules.to_text());
    wlog(format!(
        "RULES {year} written again without the yearly Swiss format (was swiss_bo3={},{}; kept {kept}): {}",
        u8::from(old[0]),
        u8::from(old[1]),
        rules.to_text()
    ));
}

/// The yearly Swiss format of a 0.1.0 rules text (`swiss_bo3=a,b`), if it has one.
pub fn old_swiss(text: &str) -> Option<[bool; 2]> {
    let v: Vec<bool> =
        text.split(';').find_map(|p| p.strip_prefix("swiss_bo3="))?.split(',').map(|x| x.trim() == "1").collect();
    (v.len() == 2).then(|| [v[0], v[1]])
}

/// The halves announced as all BO3 whose Swiss stage is still to come (`over`: the half's main event finished).
pub fn changed_halves(rules: &Rules, old: [bool; 2], over: impl Fn(usize) -> bool) -> Vec<usize> {
    [0, 1].into_iter().filter(|&h| old[h] && !(h == 0 && rules.from_autumn) && !over(h)).collect()
}

/// The news for the halves whose Swiss format changed after the announcement.
pub fn correction(year: i64, halves: &[usize], swiss_bo1: bool) -> (String, String) {
    let names: Vec<String> =
        halves.iter().map(|&h| format!("{}和{}洲际赛", CUP[h], if h == 0 { "上半年" } else { "下半年" })).collect();
    (format!("{year} 国际赛赛制调整"), format!("{}的瑞士轮改为{}，淘汰赛不变。", names.join("、"), swiss_words(swiss_bo1)))
}

/// Each half's checks once its draws are done (see [`plan_b`]), and before them that the floated schedule still stands.
fn phases(ctx: &mut StableServerCtx<'_>, st: &mut State, rules: &Rules, sched: usize, all: &[Cup]) {
    let year = rules.year;
    for half in [0, 1] {
        let (k, rivals) = (rules.shift[half], rules.rivals[half]);
        if (half == 0 && rules.from_autumn) || (k == 0 && rivals) {
            continue;
        }
        let (b_key, c_key) = (format!("float_b:{year}:{half}"), format!("float_c:{year}:{half}"));
        if ctx.save_contains_key(&c_key) {
            continue;
        }
        let Some(orig) = load_orig(ctx, year) else { continue };
        let Some(r) = room(&orig, half) else { continue };
        let Some(now) = read_schedule(ctx, sched) else { continue };
        let main = all.iter().find(|c| c.ty == MAIN[half] && c.year == Some(year));
        match main {
            None => {
                // the draw still ahead: the game may have rebuilt its schedule
                if !floated(&now, &orig, half, k, rivals) {
                    let unmoved = room(&now, half).is_some_and(|n| n.first == r.first);
                    match plan_a(&now, half, k, rivals) {
                        Some((new, k2)) if unmoved && k2 == k && new != now => {
                            let (ok, same) = write_schedule(ctx, sched, &new);
                            wlog(format!("FLOAT A {year} half {half}: the schedule lost the changes - applied again \
                                          (write {ok}, read back the same {same})"));
                        }
                        _ => {
                            if st.noted.insert((year, half)) {
                                wlog(format!("FLOAT A {year} half {half}: the schedule changed and is not the floated one - left"));
                            }
                        }
                    }
                }
            }
            Some(c) if c.finalized => {
                ctx.save_set_string(&c_key, "over before the checks");
            }
            Some(c) if !ctx.save_contains_key(&b_key) => {
                let expected = r.first + k;
                let moved = c.first_group == Some(expected);
                let drawn: Vec<&str> = all
                    .iter()
                    .filter(|x| x.ty.starts_with("Challengers") && x.year == Some(year) && x.half == half)
                    .map(|x| x.ty.as_str())
                    .collect();
                let Some(new) = plan_b(&now, &orig, half, k, moved, &drawn) else { continue };
                let (ok, same) = if new != now { write_schedule(ctx, sched, &new) } else { (true, true) };
                let line = format!(
                    "CHECK B {year} half {half}: {}'s first group match on {} (the floated schedule: {}) - {}; \
                     Challengers drawn {drawn:?} (Rift Rivals held: {rivals}); schedule {} -> {} events, write {ok}, read back the same {same}",
                    MAIN[half],
                    c.first_group.map(date_str).unwrap_or_default(),
                    date_str(expected),
                    if moved { "MOVED" } else { "NOT MOVED (the game drew on its own days: the events go back)" },
                    now.len(),
                    new.len()
                );
                wlog(&line);
                let mut fixes = Vec::new();
                if !moved && k != 0 {
                    fixes.push(format!("{}的赛程调整没有生效，比赛照原来的日子打", CUP[half]));
                }
                if !rivals && !drawn.is_empty() {
                    fixes.push(String::from("洲际赛照常举办"));
                }
                if !fixes.is_empty() {
                    news(ctx, &format!("{year} {}赛程说明", CUP[half]), &format!("{}。", fixes.join("；")));
                }
                ctx.save_set_string(&format!("float_k:{year}:{half}"), &(if moved { k } else { 0 }).to_string());
                ctx.save_set_string(&b_key, &line);
            }
            Some(c) => {
                if let Some(ko) = c.first_knockout {
                    let k = ctx.save_get_string(&format!("float_k:{year}:{half}")).and_then(|v| v.parse().ok()).unwrap_or(k);
                    let expected = r.knockout + k;
                    let line = format!(
                        "CHECK C {year} half {half}: {}'s first knockout match on {} (the floated schedule: {}) - {}",
                        MAIN[half],
                        date_str(ko),
                        date_str(expected),
                        if ko == expected { "on it" } else { "NOT on it" }
                    );
                    wlog(&line);
                    ctx.save_set_string(&c_key, &line);
                }
            }
        }
    }
}

/// The waiting matches' series lengths by their year's rules: (changed, waiting ones looked at).
fn apply_need_win(
    ctx: &mut StableServerCtx<'_>,
    st: &mut State,
    cfg: Config,
    leagues: &[(usize, usize)],
    all: &[Cup],
) -> (usize, usize) {
    let mut cache: BTreeMap<i64, Option<Rules>> = BTreeMap::new();
    let mut jobs: Vec<(Vec<usize>, i64)> = Vec::new();
    for &(id, league) in leagues {
        let list = ids_at(ctx, RecordKindV1::LeagueCompetition, id, "matches");
        let Some(year) = list.first().and_then(|&m| match_day(ctx, m)).map(|d| civil_from_days(d).0) else { continue };
        let rules = cache.entry(year).or_insert_with(|| load_rules(ctx, year));
        if let Some(want) = rules.as_ref().and_then(|r| target(r, Stage::Regular(league), cfg.swiss_bo1)) {
            jobs.push((list, want));
        }
    }
    for c in all.iter().filter(|c| !c.finalized) {
        let Some(year) = c.year else { continue };
        let rules = cache.entry(year).or_insert_with(|| load_rules(ctx, year));
        if let Some(want) = rules.as_ref().and_then(|r| target(r, Stage::Swiss(c.half), cfg.swiss_bo1)) {
            jobs.push((c.group.clone(), want));
        }
    }
    let (mut changed, mut seen) = (0, 0);
    for (list, want) in jobs {
        for m in list {
            if st.done.contains(&m) {
                continue;
            }
            match run_state(ctx, m) {
                Run::Over => {
                    st.done.insert(m);
                    continue;
                }
                Run::Other => continue,
                Run::Wait => {}
            }
            seen += 1;
            let now = ctx.record_get_json(RecordKindV1::Match, m, "need_win").and_then(|v| v.trim().parse::<i64>().ok());
            if now != Some(want) {
                if ctx.record_set_json(RecordKindV1::Match, m, "need_win", &want.to_string()) {
                    changed += 1;
                } else {
                    wlog(format!("NEED_WIN match {m}: {now:?} -> {want} REFUSED"));
                }
            }
        }
    }
    (changed, seen)
}

fn scan(ctx: &mut StableServerCtx<'_>, st: &mut State, cfg: Config) {
    if !cfg.yearly_formats {
        return;
    }
    let years = year_schedules(ctx);
    let Some((&year, &sched)) = years.iter().next_back() else { return };
    let leagues = open_leagues(ctx);
    let all = cups(ctx);
    for &y in years.keys().rev().take(2) {
        migrate(ctx, cfg, y, &all);
    }
    if load_rules(ctx, year).is_none() {
        settle(ctx, st, cfg, year, sched, &leagues, &all);
    }
    if cfg.schedule_float {
        for (&y, &id) in years.iter().rev().take(2) {
            if let Some(rules) = load_rules(ctx, y) {
                phases(ctx, st, &rules, id, &all);
            }
        }
    }
    let (changed, seen) = apply_need_win(ctx, st, cfg, &leagues, &all);
    if changed > 0 {
        wlog(format!("NEED_WIN {changed} matches changed ({seen} waiting ones looked at)"));
    }
}

// ===================== 探测（0.0.1） =====================

/// `"name": value,` for the probe document (value is JSON already).
pub fn field(out: &mut String, name: &str, value: &str) {
    if out.len() > 2 {
        out.push_str(",\n");
    }
    out.push_str(&format!("\"{name}\": {value}"));
}

/// `[a, b, ...]` of JSON values.
pub fn array(items: &[String]) -> String {
    format!("[\n{}\n]", items.join(",\n"))
}

/// A few of a list: the first `n` and the last one.
pub fn sample(list: &[usize], n: usize) -> Vec<usize> {
    let mut out: Vec<usize> = list.iter().copied().take(n).collect();
    if let Some(&last) = list.last() {
        if !out.contains(&last) {
            out.push(last);
        }
    }
    out
}

fn all_records(ctx: &StableServerCtx<'_>, kind: RecordKindV1) -> Vec<String> {
    ctx.record_ids(kind)
        .into_iter()
        .map(|id| format!("{{\"id\": {id}, \"record\": {}}}", ctx.record_get_json(kind, id, "").unwrap_or_else(|| "null".into())))
        .collect()
}

/// The read-only probe (0.0.1): the year schedules, leagues, tournaments, a few matches of each stage and the game rules.
fn probe(ctx: &StableServerCtx<'_>) -> std::io::Result<(PathBuf, String)> {
    let mut out = String::from("{\n");
    field(&mut out, "probe", &format!("\"{ID} v{VERSION}\""));
    let kinds = [
        ("teams", RecordKindV1::Team),
        ("athletes", RecordKindV1::Athlete),
        ("leagues", RecordKindV1::League),
        ("tournaments", RecordKindV1::Tournament),
        ("league_competitions", RecordKindV1::LeagueCompetition),
        ("tournament_competitions", RecordKindV1::TournamentCompetition),
        ("year_schedules", RecordKindV1::YearSchedule),
        ("matches", RecordKindV1::Match),
    ];
    let counts: Vec<String> = kinds.iter().map(|(n, k)| format!("\"{n}\": {}", ctx.record_ids(*k).len())).collect();
    field(&mut out, "counts", &format!("{{{}}}", counts.join(", ")));
    field(&mut out, "game_setting", &ctx.setting_get_json(SettingTargetV1::GameSetting, "").unwrap_or_else(|| "null".into()));
    for (name, kind) in [
        ("year_schedules", RecordKindV1::YearSchedule),
        ("leagues", RecordKindV1::League),
        ("tournaments", RecordKindV1::Tournament),
        ("tournament_competitions", RecordKindV1::TournamentCompetition),
        ("league_competitions", RecordKindV1::LeagueCompetition),
    ] {
        field(&mut out, name, &array(&all_records(ctx, kind)));
    }
    let mut picked: Vec<(String, usize)> = Vec::new();
    for id in ctx.record_ids(RecordKindV1::TournamentCompetition) {
        for path in ["group_matches", "tournament_matches"] {
            for m in sample(&ids_at(ctx, RecordKindV1::TournamentCompetition, id, path), 3) {
                picked.push((format!("tournament_competition {id} {path}"), m));
            }
        }
    }
    for &id in ctx.record_ids(RecordKindV1::LeagueCompetition).iter().rev().take(12) {
        for (path, n) in [("matches", 2), ("playoffs", 2), ("promotion_series", 1)] {
            for m in sample(&ids_at(ctx, RecordKindV1::LeagueCompetition, id, path), n) {
                picked.push((format!("league_competition {id} {path}"), m));
            }
        }
    }
    let matches: Vec<String> = picked
        .iter()
        .map(|(from, m)| {
            format!(
                "{{\"from\": \"{from}\", \"id\": {m}, \"record\": {}}}",
                ctx.record_get_json(RecordKindV1::Match, *m, "").unwrap_or_else(|| "null".into())
            )
        })
        .collect();
    field(&mut out, "matches_sample", &array(&matches));
    let keys: Vec<String> = ctx.save_keys().iter().map(|k| format!("\"{k}\"")).collect();
    field(&mut out, "save_keys", &format!("[{}]", keys.join(", ")));
    out.push_str("\n}\n");
    let path = data_dir().join("league_esports_probe.json");
    std::fs::write(&path, &out)?;
    Ok((path, format!("{} bytes; {}; {} sample matches", out.len(), counts.join(", "), matches.len())))
}

struct ServerExt;

impl StableServerExtension for ServerExt {
    fn on_server_start(&self, _ctx: &mut StableServerCtx<'_>) {
        *STATE.lock().unwrap_or_else(PoisonError::into_inner) = None;
        wlog("server start (a save is loading)");
    }

    fn before_management_tick(&self, ctx: &mut StableServerCtx<'_>) {
        let mut guard = STATE.lock().unwrap_or_else(PoisonError::into_inner);
        let st = guard.get_or_insert_with(State::default);
        if ctx.record_ids(RecordKindV1::YearSchedule).is_empty() {
            return;
        }
        let cfg = *st.cfg.get_or_insert_with(|| {
            let c = load_config();
            wlog(format!("SETTINGS {c:?} (settings.ini in {})", mod_dir().display()));
            c
        });
        if cfg.probe && !st.probed {
            st.probed = true;
            match probe(ctx) {
                Ok((path, summary)) => wlog(format!("PROBE written to {}: {summary}", path.display())),
                Err(e) => wlog(format!("PROBE failed: {e}")),
            }
        }
        for ev in ctx.management_events_after(st.seq) {
            st.seq = ev.seq;
            if ev.kind == Some(ManagementEventKindV1::SeasonRollover) {
                wlog(format!("SEASON ROLLOVER #{}: {}", ev.seq, ev.payload_json));
                st.scanned = None;
            }
        }
        let count = ctx.record_ids(RecordKindV1::Match).len();
        let due = st.scanned.map_or(true, |t| t.elapsed() >= RESCAN);
        if count == st.match_count && !due {
            return;
        }
        st.match_count = count;
        st.scanned = Some(Instant::now());
        scan(ctx, st, cfg);
    }
}

fn init(host: &StableHost) -> StableMod {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (League of Legends esports: League names, every year's formats, floating international stages) \
         loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    let mut module = StableMod::new(ID);
    module.set_server_extension(ServerExt);
    host.log(LogLevel::Info, "league_esports loaded (League names, yearly formats, floating international stages).");
    module
}

declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    fn e(date: &str, event: &str) -> Entry {
        Entry { date: date.into(), event: compact(event) }
    }

    fn ev(kind: &str, inner: &str) -> String {
        format!("{{\"{kind}\":{inner}}}")
    }

    fn on(list: &[Entry], kind_: &str, ty: Option<&str>) -> Vec<String> {
        list.iter()
            .filter(|x| {
                let (k, t) = kind(&x.event);
                k == kind_ && t.as_deref() == ty
            })
            .map(|x| x.date.clone())
            .collect()
    }

    /// One half shaped like the game's (2028's autumn): the draws, the promotion series 2 days later, the Swiss stage from
    /// 10 days after (rounds of 8 / 8 / 8 / 6 / 3, the first three over two days), the knockout draw 23 days after, the 14
    /// knockouts from 29 days after, the final 53 days after; two patches inside.
    fn half(l: &mut Vec<Entry>, main: &str, draw: i64) {
        let d = |n: i64| date_str(draw + n);
        l.push(e(&d(0), "\"MajorPatch\""));
        for ty in [main, "ChallengersEastern", "ChallengersWestern"] {
            l.push(e(&d(0), &ev("DrawingTournamentGroup", &format!("{{\"ty\":\"{ty}\"}}"))));
        }
        l.push(e(&d(2), "\"LeaguePromotion\""));
        let swiss = [(0, 10, 0..4), (0, 11, 4..8), (1, 13, 0..4), (1, 14, 4..8), (2, 16, 0..4), (2, 17, 4..8), (3, 19, 0..6), (4, 21, 0..3)];
        for (round, day, idx) in swiss {
            for i in idx {
                l.push(e(&d(day), &ev("TournamentGroupMatch", &format!("{{\"index\":{i},\"round\":{round}}}"))));
            }
        }
        l.push(e(&d(18), "\"MinorPatch\""));
        for ty in [main, "ChallengersEastern", "ChallengersWestern"] {
            l.push(e(&d(23), &ev("DrawingTournament", &format!("{{\"ty\":\"{ty}\"}}"))));
        }
        let ko = [(0, 0, 29), (0, 1, 30), (0, 2, 31), (0, 3, 32), (0, 4, 34), (0, 5, 35), (1, 0, 37), (1, 1, 38), (1, 2, 39),
                  (1, 3, 40), (2, 0, 45), (2, 1, 46), (3, 0, 48), (4, 0, 53)];
        for (round, i, day) in ko {
            l.push(e(&d(day), &ev("TournamentMatch", &format!("{{\"index\":{i},\"round\":{round}}}"))));
        }
        l.push(e(&d(39), "\"MinorPatch\""));
    }

    fn year() -> Vec<Entry> {
        let mut l = vec![
            e("2029-01-01", "\"StartRecruit\""),
            e("2029-01-01", &ev("LeagueScheduleCreate", "{\"ty\":\"Spring\"}")),
            e("2029-02-03", &ev("LeagueMatch", "{\"index\":0,\"round\":0}")),
        ];
        half(&mut l, "Masters", day_of("2029-05-01").unwrap());
        l.push(e("2029-06-24", "\"MajorPatch\""));
        l.push(e("2029-06-24", &ev("LeagueScheduleCreate", "{\"ty\":\"Summer\"}")));
        l.push(e("2029-06-24", "\"StartRecruit\""));
        half(&mut l, "Champions", day_of("2029-10-23").unwrap());
        l.push(e("2029-12-18", "\"SeasonPatch\""));
        l.sort_by_key(|x| day_of(&x.date));
        l
    }

    fn sorted(l: &[Entry]) -> bool {
        l.windows(2).all(|w| day_of(&w[0].date) <= day_of(&w[1].date))
    }

    #[test]
    fn dates_round_trip() {
        for (y, m, d) in [(2026, 1, 1), (2028, 2, 29), (2028, 12, 31), (1970, 1, 1)] {
            assert_eq!(civil_from_days(days_from_civil(y, m, d)), (y, m, d));
        }
        assert_eq!(shift_date("2028-11-05T13:00:00", -6).as_deref(), Some("2028-10-30T13:00:00"));
        assert_eq!(shift_date("2028-02-28", 1).as_deref(), Some("2028-02-29"));
        assert_eq!(md(day_of("2028-06-02").unwrap()), "6 月 2 日");
    }

    #[test]
    fn events_read_their_kind() {
        assert_eq!(kind("\"StartRecruit\""), ("StartRecruit".into(), None));
        assert_eq!(kind(r#"{"DrawingTournamentGroup":{"ty":"Masters"}}"#), ("DrawingTournamentGroup".into(), Some("Masters".into())));
        assert_eq!(kind("{\"LeagueMatch\": {\"index\": 0, \"round\": 3}}"), ("LeagueMatch".into(), None));
        assert_eq!(kind("{ \"LeagueScheduleCreate\": { \"ty\": \"Summer\" } }").1.as_deref(), Some("Summer"));
    }

    #[test]
    fn a_schedule_reads_and_writes_as_json() {
        let json = "[[\"2028-01-01\", \"StartRecruit\"], [\"2028-01-01\", {\"LeagueScheduleCreate\": {\"ty\": \"Spring\"}}],\n \
                    [\"2028-05-14\", {\"TournamentGroupMatch\": {\"index\": 3, \"round\": 0}}]]";
        let list = parse_schedule(json).unwrap();
        assert_eq!(list.len(), 3);
        assert_eq!(list[1], e("2028-01-01", r#"{"LeagueScheduleCreate":{"ty":"Spring"}}"#));
        let out = schedule_json(&list);
        assert_eq!(out, r#"[["2028-01-01","StartRecruit"],["2028-01-01",{"LeagueScheduleCreate":{"ty":"Spring"}}],["2028-05-14",{"TournamentGroupMatch":{"index":3,"round":0}}]]"#);
        assert_eq!(parse_schedule(&out), Some(list));
        // strings with commas, brackets and escapes stay one element
        assert_eq!(elements(r#"["a,b", "x\"]y", {"k":[1,2]}, 3]"#).unwrap().len(), 4);
        assert_eq!(elements("[]").unwrap().len(), 0);
        assert_eq!(compact("{ \"a b\" : [ 1 , 2 ] }"), "{\"a b\":[1,2]}");
        assert_eq!(floats("[25.0, 10.0, 5, 2.5, 1.2]"), vec![25.0, 10.0, 5.0, 2.5, 1.2]);
    }

    #[test]
    fn the_stage_has_its_room() {
        let l = year();
        // spring: promotion 05-03, + the Challengers' 4 days: the Swiss stage (05-11) may start from 05-08 - 3 earlier;
        // the final (06-23) is the day before the summer season: no later
        let s = room(&l, 0).unwrap();
        assert_eq!((date_str(s.lo), date_str(s.first), date_str(s.knockout), date_str(s.last), date_str(s.hi)),
                   ("2029-05-08".into(), "2029-05-11".into(), "2029-05-30".into(), "2029-06-23".into(), "2029-06-23".into()));
        assert_eq!((clamp_shift(&s, -9), clamp_shift(&s, 5)), (-3, 0));
        // autumn: 3 earlier, 2 later (the season patch on 12-18)
        let a = room(&l, 1).unwrap();
        assert_eq!((date_str(a.first), date_str(a.last), date_str(a.hi)), ("2029-11-02".into(), "2029-12-15".into(), "2029-12-17".into()));
        assert_eq!((clamp_shift(&a, -9), clamp_shift(&a, 9), clamp_shift(&a, -2)), (-3, 2, -2));
    }

    #[test]
    fn earlier_moves_the_swiss_days_first_and_rift_rivals_can_go() {
        let l = year();
        let (a, k) = plan_a(&l, 1, -3, false).unwrap();
        assert_eq!(k, -3);
        assert!(sorted(&a));
        // the autumn's Challengers group and knockout draws gone (4), the spring's kept
        assert_eq!(a.len(), l.len() - 4);
        assert_eq!(challengers_draws(&a, 1), 0);
        assert_eq!(challengers_draws(&a, 0), 4);
        // the Swiss days 3 earlier, the knockout draw and the knockouts not yet; the patches stay
        assert_eq!(room(&a, 1).unwrap().first, day_of("2029-10-30").unwrap());
        assert_eq!(on(&a, "DrawingTournament", Some("Champions")), vec!["2029-11-15"]);
        assert_eq!(room(&a, 1).unwrap().last, day_of("2029-12-15").unwrap());
        assert_eq!(on(&a, "MinorPatch", None), on(&l, "MinorPatch", None));
        assert!(floated(&a, &l, 1, -3, false) && !floated(&l, &l, 1, -3, false));
        // the spring untouched
        assert_eq!(room(&a, 0), room(&l, 0));

        // after the draw, the group matches on the moved days: the knockouts follow
        let b = plan_b(&a, &l, 1, -3, true, &[]).unwrap();
        assert_eq!(b.len(), a.len());
        assert_eq!(on(&b, "DrawingTournament", Some("Champions")), vec!["2029-11-12"]);
        let r = room(&b, 1).unwrap();
        assert_eq!((date_str(r.first), date_str(r.knockout), date_str(r.last)),
                   ("2029-10-30".into(), "2029-11-18".into(), "2029-12-12".into()));
        assert!(sorted(&b));

        // not on them, and the game drew the eastern cup anyway: everything back, its knockout draw back
        let c = plan_b(&a, &l, 1, -3, false, &["ChallengersEastern"]).unwrap();
        assert_eq!(room(&c, 1).unwrap(), room(&l, 1).unwrap());
        assert_eq!(on(&c, "DrawingTournament", Some("ChallengersEastern")), vec!["2029-05-24", "2029-11-15"]);
        assert!(on(&c, "DrawingTournament", Some("ChallengersWestern")).iter().all(|d| d.starts_with("2029-05")));
        assert_eq!(c.len(), a.len() + 1);
        assert!(sorted(&c));
    }

    #[test]
    fn later_moves_the_whole_stage_at_once() {
        let l = year();
        let (a, k) = plan_a(&l, 1, 2, true).unwrap();
        assert_eq!((k, a.len()), (2, l.len()));
        let r = room(&a, 1).unwrap();
        assert_eq!((date_str(r.first), date_str(r.knockout), date_str(r.last)),
                   ("2029-11-04".into(), "2029-11-23".into(), "2029-12-17".into()));
        assert_eq!(on(&a, "DrawingTournament", Some("Champions")), vec!["2029-11-17"]);
        assert_eq!(on(&a, "MinorPatch", None), on(&l, "MinorPatch", None));
        // nothing more after the draw when it worked; everything back when it did not
        assert_eq!(plan_b(&a, &l, 1, 2, true, &[]).unwrap(), a);
        assert_eq!(room(&plan_b(&a, &l, 1, 2, false, &[]).unwrap(), 1), room(&l, 1));
        // the spring has no room later: as it is
        assert_eq!(plan_a(&l, 0, 2, true).unwrap(), (l.clone(), 0));
    }

    #[test]
    fn a_challengers_draw_listed_before_the_main_one_still_goes() {
        let mut l = year();
        let i = l.iter().position(|x| kind(&x.event) == ("DrawingTournamentGroup".into(), Some("Champions".into()))).unwrap();
        l.swap(i, i + 1);
        let (a, _) = plan_a(&l, 1, 0, false).unwrap();
        assert_eq!(challengers_draws(&a, 1), 0);
        assert_eq!(a.len(), l.len() - 4);
    }

    #[test]
    fn rules_are_the_same_every_load_and_round_trip() {
        let a = roll(2029, 42, None, false);
        assert_eq!(a, roll(2029, 42, None, false));
        assert_eq!(Rules::from_text(&a.to_text()), Some(a.clone()));
        assert!(a.regular.iter().all(|&b| b == 1 || b == 3));
        assert_ne!(a.host[0], a.host[1]);
        assert!((90..=130).contains(&a.prize[0]) && (90..=140).contains(&a.prize[1]));
        assert!((-3..=0).contains(&a.shift[0]) && (-3..=2).contains(&a.shift[1]));
        let b = roll(2030, 42, Some(&a), false);
        assert!(b.host[0] != a.host[0] && b.host[1] != a.host[1], "a host two years running");
        // set up mid-year: the regular seasons and the spring stay the game's, the autumn always moves
        for salt in 0..50 {
            let f = roll(2028, salt, None, true);
            assert!(f.regular.iter().all(|&b| b == 0) && f.shift[0] == 0 && f.rivals[0]);
            assert!(f.shift[1] != 0 && (-3..=2).contains(&f.shift[1]));
        }
        // over many saves every choice shows up about as often as meant
        let n = 400;
        let bo1 = (0..n).filter(|s| roll(2029, *s, None, false).regular[2] == 1).count();
        let off = (0..n).filter(|s| !roll(2029, *s, None, false).rivals[1]).count();
        assert!((80..=160).contains(&bo1), "BO1 {bo1}");
        assert!((80..=160).contains(&off), "Rift Rivals off {off}");
    }

    #[test]
    fn need_win_follows_the_rules() {
        let mut r = roll(2029, 7, None, false);
        r.regular[0] = 1;
        r.regular[1] = 3;
        assert_eq!(target(&r, Stage::Regular(0), true), Some(1));
        assert_eq!(target(&r, Stage::Regular(1), true), Some(2));
        // every Swiss match BO1 (the user: 「瑞士轮应该改成BO1吧？淘汰赛BO7就行」), or as the game has them
        assert_eq!(target(&r, Stage::Swiss(0), true), Some(1));
        assert_eq!(target(&r, Stage::Swiss(1), true), Some(1));
        assert_eq!(target(&r, Stage::Swiss(1), false), None);
        r.regular[2] = 0;
        assert_eq!(target(&r, Stage::Regular(2), true), None);
        // the install year's spring is over before the mod: left alone
        r.from_autumn = true;
        assert_eq!(target(&r, Stage::Swiss(0), true), None);
        assert_eq!(target(&r, Stage::Swiss(1), true), Some(1));
    }

    #[test]
    fn rules_kept_by_0_1_0_lose_their_swiss_format() {
        // what 0.1.0 wrote into the user's save on 11-18 (announced: Worlds' Swiss stage all BO3)
        let text = "year=2028;regular=0,0,0,0,0,0,0,0,0,0,0,0;swiss_bo3=0,1;rivals=1,1;shift=0,1;host=5,4;prize=127,119;from_autumn=1";
        let r = Rules::from_text(text).unwrap();
        assert_eq!((r.shift, r.host, r.prize, r.from_autumn), ([0, 1], [5, 4], [127, 119], true));
        assert!(!r.to_text().contains("swiss"));
        assert_eq!(Rules::from_text(&r.to_text()), Some(r.clone()));
        assert_eq!(old_swiss(text), Some([false, true]));
        assert_eq!(old_swiss(&r.to_text()), None);
        // the autumn still to come: one news item; over, or the spring of the install year: none
        assert_eq!(changed_halves(&r, [false, true], |_| false), vec![1]);
        assert_eq!(changed_halves(&r, [false, true], |h| h == 1), Vec::<usize>::new());
        assert_eq!(changed_halves(&r, [true, false], |_| false), Vec::<usize>::new());
        let (title, body) = correction(2028, &[1], true);
        assert_eq!(title, "2028 国际赛赛制调整");
        assert_eq!(body, "全球总决赛和下半年洲际赛的瑞士轮改为全程 BO1，淘汰赛不变。");
    }

    #[test]
    fn the_announcement_says_it_all() {
        let mut r = roll(2029, 3, None, false);
        r.regular = [3, 3, 1, 1, 3, 3, 1, 3, 1, 1, 3, 3];
        r.rivals = [true, false];
        r.host = [3, 1];
        r.prize = [110, 125];
        let d = |a: &str, b: &str| Some((day_of(a).unwrap(), day_of(b).unwrap()));
        let (title, text) = announcement(&r, [d("2029-05-08", "2029-06-20"), d("2029-10-30", "2029-12-12")], true);
        assert_eq!(title, "2029 赛季赛制公告");
        for want in [
            "LCK BO3",
            "LEC BO1",
            "季中冠军赛 MSI：美国洛杉矶主办，瑞士轮全程 BO1，5 月 8 日开打、6 月 20 日决赛；奖金池为原版的 110%",
            "上半年洲际赛：照常举办",
            "全球总决赛：中国上海主办，瑞士轮全程 BO1，10 月 30 日开打、12 月 12 日决赛；奖金池为原版的 125%",
            "下半年洲际赛：停办",
        ] {
            assert!(text.contains(want), "{want} in {text}");
        }
        r.from_autumn = true;
        let (title, text) = announcement(&r, [None, d("2029-10-30", "2029-12-12")], false);
        assert_eq!(title, "2029 下半年国际赛公告");
        assert!(!text.contains("联赛常规赛") && !text.contains("季中冠军赛") && text.contains("全球总决赛"));
        assert!(text.contains("瑞士轮照原版（BO1，决定晋级、淘汰的场次 BO3）"));
    }

    #[test]
    fn settings_read_their_switches() {
        assert_eq!(parse_config(""), Config::default());
        let c = parse_config("\u{feff}; comment\nyearly_formats = 0\nschedule_float=1 ; on\nswiss_bo1 = 0\nprobe = 0\n");
        assert_eq!(c, Config { yearly_formats: false, schedule_float: true, swiss_bo1: false, probe: false });
        assert_eq!(parse_config(include_str!("../settings.ini")), Config::default());
    }

    #[test]
    fn ints_reads_a_match_list() {
        assert_eq!(ints("[12, 345,6]"), vec![12, 345, 6]);
        assert_eq!(ints("[[1,2],[30]]"), vec![1, 2, 30]);
    }

    #[test]
    fn sample_keeps_the_first_and_the_last() {
        assert_eq!(sample(&[1, 2, 3, 4, 5], 2), vec![1, 2, 5]);
        assert_eq!(sample(&[], 3), Vec::<usize>::new());
    }

    #[test]
    fn the_names_cover_every_league_and_cup() {
        let text = include_str!("../text/ui.i18n");
        for key in ["tack", "tacc", "tace", "taca", "tacs", "tacj", "tack2", "tacc2", "tace2", "taca2", "tacs2", "tacj2",
                    "masters", "champions", "challengers_east", "challengers_west"] {
            assert!(text.matches(&format!("\"{key}\":")).count() >= 3, "{key} in every language");
        }
    }
}
