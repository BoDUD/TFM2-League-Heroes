//! 打架记录器（用户 2026-11-08：「其他逻辑呢 比如lol那种 坦克保护adc 现在游戏里也很糟糕吧 其他问题也挺多吧」→
//! 「先做打架记录器」）。比赛 AI 改造第 3 步（打架）的第 0 步：先量，再改。
//!
//! 只读的比赛钩子（`StableMatchHook`，附加包合集里由 league_addons 的 `BundleMatch` 转发），**不改游戏里的任何东西**。
//! 和运营记录器（league_macro_log）一样每场只看服务器预演那一次（`ServerPresim`），每 `SAMPLE` tick 取一次样：每个
//! 选手的位置（`LaneV1`：上单 / 打野 / 中单 / 射手（下路）/ 辅助）、英雄活没活、在哪、血量，活着的防御塔，以及游戏的
//! 击杀记录（`kill_log_at`：杀人的一方和位置、被杀的位置、几个助攻）。比赛结束写一行 `MATCH`：
//!
//! - **谁在死**（`deaths` / `early`）：各位置的阵亡，10:00（`EARLY`）前的另记。阵亡时（他最后活着的位置）在自己的塔
//!   `TOWER_NEAR` 以内算「被越塔」（`dived`），在对面的塔下算 `enemy_tower`；身边 `NEAR` 以内对面活着的英雄比自己这边
//!   （算上他自己）多算「被多打少」（`outnumbered`）；英雄杀的、没有助攻算「单杀」（`solo`）。
//! - **打架**（`fights` / `teamfights`）：阵亡按时间（上一个死的 `FIGHT_GAP` 以内）和地点（离第一个死的 `FIGHT_R` 以内）
//!   串成一场架；第一个死的时候双方各有 3 个以上英雄在 `FIGHT_R` 以内（算上死的）算团战。团战记双方一共死几个
//!   （`tf_kills`）、第一个死的是什么位置（`tf_first`）。
//! - **射手被贴脸**（`dives`）：敌方英雄走进我方射手 `DIVE_R` 以内（近战的普攻距离，league_ult_press 的 `MELEE_RANGE`）
//!   算一次，`DIVE_GAP` 内没人贴着才算下一次。记那一刻辅助在不在 `SUPPORT_NEAR` 以内（`support_near`）；`PEEL_WINDOW`
//!   内有没有上单 / 打野 / 辅助（`GUARDS`）走到贴脸的人 `PEEL_R` 以内（`peeled`，来救了）；`DIVE_LEN` 内射手死没死
//!   （`adc_died`，括号里是来救了还死的）。
//! - **贴脸时间**（`contact`）：各位置活着、`DIVE_R` 以内有敌方英雄的秒数（射手、中单这些远程该拉开距离）。
//! - **谁在挨打**（`damage%`）：各位置掉的血（两次取样之间少了的，不算回血）占双方一共掉的多少。
//!
//! 每 `SUMMARY_EVERY` 场再写一行 `SUM`（这一批的平均：阵亡按位置、10:00 前、死在哪的比例，团战和第一个死的位置，射手被
//! 贴脸后辅助在旁边 / 来救 / 死了的比例，各位置贴着敌人的时间占活着时间的比例，挨打的比例），也追加到
//! `league_fight_log.sum.log`（不随启动重写；每次启动的第一行前先写时间和版本）。
//!
//! 两张 5v5 地图（2026-11-10）：「在场」的上限按这一场的地图（`game_places::terrain::Map::limit`，每次取样看
//! `map_of_sim`）：游戏自己的地图照旧 `MAP_MAX`（1200000），Rin 的召唤师峡谷 1.25 x 1614545——以前一律 1200000，峡谷上
//! 红方半边的英雄都不算在场（没有贴脸、没有交火、阵亡没有位置）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_fight_log.log`，每次启动游戏重写，上一次的留在 .prev.log；
//! 一次启动最多 `LOG_CAP` 行。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{map_of_sim, rift_status, Map};
use mod_api_stable::*;

const ID: &str = "league_fight_log";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_fight_log") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 多久取一次样（tick，0.25 秒：打架比运营快）。
pub const SAMPLE: usize = 15;
/// 早期：10:00。
pub const EARLY: usize = 36_000;
/// 「在塔下」：离活着的防御塔多近。
pub const TOWER_NEAR: f64 = 80_000.0;
/// 阵亡时数身边双方英雄的距离。
pub const NEAR: f64 = 100_000.0;
/// 一场架里两个阵亡最多隔多久（tick，10 秒）。
pub const FIGHT_GAP: usize = 600;
/// 一场架的阵亡离第一个死的最远多少；也是数在场英雄的距离。
pub const FIGHT_R: f64 = 150_000.0;
/// 贴脸：敌方英雄离我方射手多近（近战的普攻距离）。
pub const DIVE_R: f64 = 30_000.0;
/// 来救：队友离贴脸的敌人多近。
pub const PEEL_R: f64 = 35_000.0;
/// 贴脸那一刻辅助离射手多近算在旁边。
pub const SUPPORT_NEAR: f64 = 60_000.0;
/// 贴脸后多久内来救才算（tick，3 秒）。
pub const PEEL_WINDOW: usize = 180;
/// 一次贴脸看多久（tick，5 秒）：这期间射手死了算死在这次贴脸里。
pub const DIVE_LEN: usize = 300;
/// 两次贴脸之间至少隔多久（tick，2 秒）。
pub const DIVE_GAP: usize = 120;
/// 每多少场写一行平均。
pub const SUMMARY_EVERY: usize = 50;
/// 游戏自己的地图的大小上限：比这远的坐标（被放逐、藏起来的英雄）不算在场（= `Map::Native.limit()`；这一场的看
/// `Map::limit`）。
pub const MAP_MAX: f64 = 1_200_000.0;
/// 位置（`LaneV1` 的编号）的简写：上单、打野、中单、射手（下路）、辅助。
pub const ROLES: [&str; 5] = ["T", "J", "M", "B", "S"];
const BOTTOM: usize = 3;
const SUPPORT: usize = 4;
/// 会来救射手的位置：上单、打野、辅助。
pub const GUARDS: [usize; 3] = [0, 1, 4];
/// 同时跟着的比赛最多几场（没结束就被丢掉的比赛不会一直占着）。
const RUNS_KEPT: usize = 64;
/// 一次启动最多写多少行。
const LOG_CAP: usize = 20_000;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_FIGHT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_fight_log.log");
        }
    }
    PathBuf::from("league_fight_log.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    if LINES.fetch_add(1, Ordering::Relaxed) >= LOG_CAP {
        return;
    }
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (memory log-open-once)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Whether this launch's first SUM line already went to the summary file (after its header).
static SUM_HEADER: AtomicBool = AtomicBool::new(false);

/// Appends a SUM line to `league_fight_log.sum.log` beside the log (never rewritten); a launch's first comes after a
/// line with the time and the version.
fn sum_log(line: &str) {
    let Ok(mut f) = OpenOptions::new().create(true).append(true).open(LOG_PATH.with_extension("sum.log")) else { return };
    let mut text = String::new();
    if !SUM_HEADER.swap(true, Ordering::Relaxed) {
        let secs = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map_or(0, |d| d.as_secs());
        let (y, m, d) = civil(secs / 86_400);
        text.push_str(&format!(
            "=== {y}-{m:02}-{d:02} {:02}:{:02} UTC: {ID} v{VERSION}, league_macro v{} ===\n",
            secs / 3600 % 24,
            secs / 60 % 60,
            option_env!("ADDON_VERSION_league_macro").unwrap_or("?")
        ));
    }
    text.push_str(line);
    text.push('\n');
    let _ = f.write_all(text.as_bytes());
}

/// The date (year, month, day) of a count of days since 1970-01-01.
pub fn civil(days: u64) -> (i64, u32, u32) {
    let z = days as i64 + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z.rem_euclid(146_097);
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = (if mp < 10 { mp + 3 } else { mp - 9 }) as u32;
    (yoe + era * 400 + i64::from(m <= 2), m, d)
}

fn clock(t: usize) -> String {
    format!("{}:{:02}", t / 3600, t / 60 % 60)
}

// ===================== 一场比赛 =====================

pub type Pos = (f64, f64);

fn dist(a: Pos, b: Pos) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// One player at a sample.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Seat {
    pub team: usize,
    /// The `LaneV1` code (0..5) of the player's position.
    pub role: Option<usize>,
    pub alive: bool,
    pub pos: Pos,
    pub hp: usize,
}

/// Whether the seat's champion is alive and on the map (not past `limit`: `Map::limit`, `MAP_MAX` on the game's own).
fn here_on(s: &Seat, limit: f64) -> bool {
    s.alive && s.pos.0 <= limit && s.pos.1 <= limit
}

/// A kill-log entry: the killer's team (2 and up: not a team) and position, the victim's position.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Kill {
    pub tick: usize,
    pub killer_team: usize,
    pub killer_role: Option<usize>,
    pub victim_role: Option<usize>,
    pub assists: u32,
}

/// One sample of a match: every player (by player index), the standing towers (team, position), the kill-log
/// entries since the last sample and the map they are on (its `limit`: past it a champion is off the map).
#[derive(Clone, Debug)]
pub struct Sample {
    pub tick: usize,
    pub seats: Vec<Seat>,
    pub towers: Vec<(usize, Pos)>,
    pub kills: Vec<Kill>,
    pub map: Map,
}

impl Default for Sample {
    /// Nothing seen, on the game's own map.
    fn default() -> Self {
        Sample { tick: 0, seats: Vec::new(), towers: Vec::new(), kills: Vec::new(), map: Map::Native }
    }
}

/// A fight being put together: its last death, where its first death fell, the kills of each team, the first victim's
/// position and the champions of each side there at the first death.
#[derive(Clone, Debug, Default, PartialEq)]
struct Fight {
    last: usize,
    centre: Pos,
    kills: [u32; 2],
    first: Option<usize>,
    sides: [usize; 2],
}

/// An ADC dived: since when, by whom (players), the support's distance then, whether a guard came, whether the ADC died.
#[derive(Clone, Debug, Default, PartialEq)]
struct Dive {
    start: usize,
    divers: Vec<usize>,
    support: Option<f64>,
    peeled: bool,
    adc_died: bool,
}

/// What a match adds up to (both teams; by `ROLES` where an array).
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Counts {
    pub deaths: [u32; 5],
    pub early: [u32; 5],
    pub dived: u32,
    pub enemy_tower: u32,
    pub outnumbered: u32,
    pub solo: u32,
    /// Deaths placed (the victim's seat and last position known): the base of `dived` .. `outnumbered`.
    pub placed: u32,
    pub fights: u32,
    pub teamfights: u32,
    pub tf_kills: u32,
    pub tf_first: [u32; 5],
    pub dives: u32,
    pub support_near: u32,
    pub peeled: u32,
    pub adc_died: u32,
    pub adc_died_peeled: u32,
    /// Ticks alive with an enemy champion within `DIVE_R`, and ticks alive.
    pub contact: [u64; 5],
    pub alive: [u64; 5],
    /// Health lost.
    pub damage: [u64; 5],
}

/// A match being watched.
#[derive(Clone, Debug, Default)]
pub struct Tracker {
    pub last_tick: usize,
    pub c: Counts,
    /// Kill-log entries already read.
    pub kills_seen: usize,
    /// Both nexuses seen standing (a mode without them never ends a match by a missing one).
    pub nexus_seen: bool,
    last_pos: Vec<Option<Pos>>,
    last_hp: Vec<Option<usize>>,
    fight: Option<Fight>,
    dives: Vec<Option<Dive>>,
    dive_end: Vec<Option<usize>>,
}

impl Tracker {
    /// One sample.
    pub fn step(&mut self, s: &Sample) {
        self.last_tick = s.tick;
        let lim = s.map.limit();
        let here = |x: &Seat| here_on(x, lim);
        let n = s.seats.len();
        if self.last_pos.len() < n {
            self.last_pos.resize(n, None);
            self.last_hp.resize(n, None);
            self.dives.resize(n, None);
            self.dive_end.resize(n, None);
        }
        // deaths since the last sample, placed where the victim last stood alive
        for k in &s.kills {
            self.death(k, s);
        }
        // time next to an enemy, time alive, health lost
        for (i, seat) in s.seats.iter().enumerate() {
            let (Some(r), true) = (seat.role, here(seat)) else { continue };
            self.c.alive[r] += SAMPLE as u64;
            if s.seats.iter().any(|e| e.team != seat.team && here(e) && dist(e.pos, seat.pos) <= DIVE_R) {
                self.c.contact[r] += SAMPLE as u64;
            }
            if let Some(prev) = self.last_hp[i] {
                self.c.damage[r] += prev.saturating_sub(seat.hp) as u64;
            }
        }
        self.watch_dives(s);
        for (i, seat) in s.seats.iter().enumerate() {
            if here(seat) {
                self.last_pos[i] = Some(seat.pos);
                self.last_hp[i] = Some(seat.hp);
            } else if !seat.alive {
                self.last_hp[i] = None;
            }
        }
        // a fight with no death for FIGHT_GAP is over
        if self.fight.as_ref().is_some_and(|f| s.tick > f.last + FIGHT_GAP) {
            self.close_fight();
        }
    }

    fn death(&mut self, k: &Kill, s: &Sample) {
        let lim = s.map.limit();
        let here = |x: &Seat| here_on(x, lim);
        if let Some(r) = k.victim_role {
            self.c.deaths[r] += 1;
            if k.tick <= EARLY {
                self.c.early[r] += 1;
            }
        }
        if k.assists == 0 && k.killer_role.is_some() && k.killer_team < 2 {
            self.c.solo += 1;
        }
        // the victim: the other team's player of that position
        if k.killer_team > 1 {
            return;
        }
        let team = 1 - k.killer_team;
        let Some(i) = s.seats.iter().position(|x| x.team == team && x.role.is_some() && x.role == k.victim_role) else { return };
        let Some(at) = self.last_pos.get(i).copied().flatten() else { return };
        self.c.placed += 1;
        if s.towers.iter().any(|t| t.0 == team && dist(t.1, at) <= TOWER_NEAR) {
            self.c.dived += 1;
        }
        if s.towers.iter().any(|t| t.0 != team && t.0 < 2 && dist(t.1, at) <= TOWER_NEAR) {
            self.c.enemy_tower += 1;
        }
        let near = |side: usize| s.seats.iter().enumerate().filter(|(j, x)| *j != i && x.team == side && here(x) && dist(x.pos, at) <= NEAR).count();
        if near(1 - team) > near(team) + 1 {
            self.c.outnumbered += 1;
        }
        if let Some(Some(d)) = self.dives.get_mut(i) {
            d.adc_died = true;
        }
        // the fight it belongs to, or a new one
        let joins = self.fight.as_ref().is_some_and(|f| k.tick <= f.last + FIGHT_GAP && dist(f.centre, at) <= FIGHT_R);
        if !joins {
            self.close_fight();
            let side = |t: usize| s.seats.iter().filter(|x| x.team == t && here(x) && dist(x.pos, at) <= FIGHT_R).count();
            let mut sides = [side(0), side(1)];
            sides[team] += 1;
            self.fight = Some(Fight { last: k.tick, centre: at, kills: [0, 0], first: k.victim_role, sides });
        }
        if let Some(f) = self.fight.as_mut() {
            f.last = f.last.max(k.tick);
            f.kills[k.killer_team] += 1;
        }
    }

    fn close_fight(&mut self) {
        let Some(f) = self.fight.take() else { return };
        self.c.fights += 1;
        if f.sides[0] >= 3 && f.sides[1] >= 3 {
            self.c.teamfights += 1;
            self.c.tf_kills += f.kills[0] + f.kills[1];
            if let Some(r) = f.first {
                self.c.tf_first[r] += 1;
            }
        }
    }

    fn watch_dives(&mut self, s: &Sample) {
        let lim = s.map.limit();
        let here = |x: &Seat| here_on(x, lim);
        for (i, adc) in s.seats.iter().enumerate() {
            if adc.role != Some(BOTTOM) {
                continue;
            }
            let divers_now: Vec<usize> = s
                .seats
                .iter()
                .enumerate()
                .filter(|(_, e)| e.team != adc.team && here(e) && here(adc) && dist(e.pos, adc.pos) <= DIVE_R)
                .map(|(j, _)| j)
                .collect();
            // a guard (top, jungle, support of the ADC's team) next to one of the divers
            let guarded = |divers: &[usize]| {
                divers.iter().any(|&j| {
                    let e = &s.seats[j];
                    here(e)
                        && s.seats.iter().any(|g| {
                            g.team == adc.team && here(g) && g.role.is_some_and(|r| GUARDS.contains(&r)) && dist(g.pos, e.pos) <= PEEL_R
                        })
                })
            };
            if let Some(mut d) = self.dives[i].take() {
                if d.adc_died || !adc.alive || s.tick >= d.start + DIVE_LEN {
                    self.close_dive(d);
                    self.dive_end[i] = Some(s.tick);
                    continue;
                }
                for j in divers_now {
                    if !d.divers.contains(&j) {
                        d.divers.push(j);
                    }
                }
                if !d.peeled && s.tick <= d.start + PEEL_WINDOW {
                    d.peeled = guarded(&d.divers);
                }
                self.dives[i] = Some(d);
                continue;
            }
            if divers_now.is_empty() || self.dive_end[i].is_some_and(|end| s.tick < end + DIVE_GAP) {
                continue;
            }
            let support = s
                .seats
                .iter()
                .filter(|g| g.team == adc.team && here(g) && g.role == Some(SUPPORT))
                .map(|g| dist(g.pos, adc.pos))
                .reduce(f64::min);
            let peeled = guarded(&divers_now);
            self.dives[i] = Some(Dive { start: s.tick, divers: divers_now, support, peeled, adc_died: false });
        }
    }

    fn close_dive(&mut self, d: Dive) {
        self.c.dives += 1;
        if d.support.is_some_and(|x| x <= SUPPORT_NEAR) {
            self.c.support_near += 1;
        }
        if d.peeled {
            self.c.peeled += 1;
        }
        if d.adc_died {
            self.c.adc_died += 1;
            if d.peeled {
                self.c.adc_died_peeled += 1;
            }
        }
    }

    /// The match is over: the open fight and dives count as they are.
    pub fn finish(&mut self) {
        self.close_fight();
        for i in 0..self.dives.len() {
            if let Some(d) = self.dives[i].take() {
                self.close_dive(d);
            }
        }
    }

    /// The `MATCH` line (`head`: where it came from).
    pub fn line(&self, head: &str) -> String {
        let c = &self.c;
        let by = |v: &[u32; 5]| ROLES.iter().zip(v).map(|(r, n)| format!("{r}{n}")).collect::<Vec<_>>().join(" ");
        let secs = ROLES.iter().zip(&c.contact).map(|(r, t)| format!("{r}{}", t / 60)).collect::<Vec<_>>().join(" ");
        let total: u64 = c.damage.iter().sum::<u64>().max(1);
        let hurt = ROLES.iter().zip(&c.damage).map(|(r, d)| format!("{r}{}", d * 100 / total)).collect::<Vec<_>>().join(" ");
        format!(
            "MATCH {head} len={} deaths=[{}] early=[{}] dived={} enemy_tower={} outnumbered={} solo={} fights={} teamfights={} tf_kills={} tf_first=[{}] dives={} support_near={} peeled={} adc_died={} ({} peeled) contact_s=[{}] damage%=[{}]",
            clock(self.last_tick),
            by(&c.deaths),
            by(&c.early),
            c.dived,
            c.enemy_tower,
            c.outnumbered,
            c.solo,
            c.fights,
            c.teamfights,
            c.tf_kills,
            by(&c.tf_first),
            c.dives,
            c.support_near,
            c.peeled,
            c.adc_died,
            c.adc_died_peeled,
            secs,
            hurt
        )
    }
}

// ===================== 平均 =====================

/// What the `SUM` line averages over a batch of matches.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Batch {
    pub matches: u32,
    pub ticks: u64,
    pub c: Counts,
}

fn add<const N: usize, T: Copy + std::ops::AddAssign>(to: &mut [T; N], from: &[T; N]) {
    for (a, b) in to.iter_mut().zip(from) {
        *a += *b;
    }
}

impl Batch {
    pub fn add(&mut self, t: &Tracker) {
        self.matches += 1;
        self.ticks += t.last_tick as u64;
        let (a, b) = (&mut self.c, &t.c);
        add(&mut a.deaths, &b.deaths);
        add(&mut a.early, &b.early);
        add(&mut a.tf_first, &b.tf_first);
        add(&mut a.contact, &b.contact);
        add(&mut a.alive, &b.alive);
        add(&mut a.damage, &b.damage);
        for (x, y) in [
            (&mut a.dived, b.dived),
            (&mut a.enemy_tower, b.enemy_tower),
            (&mut a.outnumbered, b.outnumbered),
            (&mut a.solo, b.solo),
            (&mut a.placed, b.placed),
            (&mut a.fights, b.fights),
            (&mut a.teamfights, b.teamfights),
            (&mut a.tf_kills, b.tf_kills),
            (&mut a.dives, b.dives),
            (&mut a.support_near, b.support_near),
            (&mut a.peeled, b.peeled),
            (&mut a.adc_died, b.adc_died),
            (&mut a.adc_died_peeled, b.adc_died_peeled),
        ] {
            *x += y;
        }
    }

    pub fn line(&self) -> String {
        let c = &self.c;
        let m = self.matches.max(1) as f64;
        let pct = |a: u64, b: u64| if b == 0 { 0.0 } else { 100.0 * a as f64 / b as f64 };
        let per = |v: &[u32; 5]| ROLES.iter().zip(v).map(|(r, n)| format!("{r} {:.1}", *n as f64 / m)).collect::<Vec<_>>().join(" ");
        let share = |v: &[u32; 5]| {
            let total: u64 = v.iter().map(|n| *n as u64).sum();
            ROLES.iter().zip(v).map(|(r, n)| format!("{r} {:.0}%", pct(*n as u64, total))).collect::<Vec<_>>().join(" ")
        };
        let deaths: u64 = c.deaths.iter().map(|n| *n as u64).sum();
        let placed = c.placed as u64;
        let near_time = ROLES
            .iter()
            .enumerate()
            .map(|(i, r)| format!("{r} {:.1}%", pct(c.contact[i], c.alive[i])))
            .collect::<Vec<_>>()
            .join(" ");
        let damage: u64 = c.damage.iter().sum();
        let hurt = ROLES.iter().zip(&c.damage).map(|(r, d)| format!("{r} {:.0}%", pct(*d, damage))).collect::<Vec<_>>().join(" ");
        let unpeeled = (c.dives - c.peeled) as u64;
        format!(
            "SUM {} matches: len {} | deaths a match {} ({}), before 10:00 {} | of the deaths: under their own tower {:.0}%, under the enemy's {:.0}%, outnumbered {:.0}%, solo kills {:.0}% | fights {:.1} a match, teamfights {:.1} with {:.1} deaths each, first to die in a teamfight {} | ADC dived {:.1} a match: support within 60k {:.0}%, helped in 3 s {:.0}%, ADC died {:.0}% (helped {:.0}%, not helped {:.0}%) | next to an enemy (of the time alive) {} | damage taken {}",
            self.matches,
            clock((self.ticks as f64 / m) as usize),
            per(&c.deaths),
            share(&c.deaths),
            per(&c.early),
            pct(c.dived as u64, placed),
            pct(c.enemy_tower as u64, placed),
            pct(c.outnumbered as u64, placed),
            pct(c.solo as u64, deaths),
            c.fights as f64 / m,
            c.teamfights as f64 / m,
            c.tf_kills as f64 / c.teamfights.max(1) as f64,
            share(&c.tf_first),
            c.dives as f64 / m,
            pct(c.support_near as u64, c.dives as u64),
            pct(c.peeled as u64, c.dives as u64),
            pct(c.adc_died as u64, c.dives as u64),
            pct(c.adc_died_peeled as u64, c.peeled as u64),
            pct((c.adc_died - c.adc_died_peeled) as u64, unpeeled),
            near_time,
            hurt
        )
    }
}

// ===================== 钩子 =====================

type RunKey = (u32, u64, u64, u64);

#[derive(Default)]
struct Book {
    runs: HashMap<RunKey, (u64, Tracker)>,
    clock: u64,
    batch: Batch,
}

static BOOK: LazyLock<Mutex<Book>> = LazyLock::new(|| Mutex::new(Book::default()));

fn lane(code: u32) -> Option<usize> {
    (code < 5).then_some(code as usize)
}

/// This launch's log has told the Rift already.
static RIFT_TOLD: AtomicBool = AtomicBool::new(false);

/// The map `sim` plays on; the first Rift a launch, a line in the log.
fn map_here(sim: &StableSim<'_>) -> Map {
    let map = map_of_sim(sim);
    if map == Map::Rift && !RIFT_TOLD.swap(true, Ordering::Relaxed) {
        wlog(format!("== Rift: champions count as on the map up to {:.0} (1.25 x the Rift's side, not the game's own \
                      {MAP_MAX:.0}); {} ==", map.limit(), rift_status()));
    }
    map
}

/// A sample of the match (kill-log entries from `kills_from` on), whether a nexus fell (one down or gone after both
/// were seen) and the kill-log length.
fn sample(sim: &StableSim<'_>, kills_from: usize) -> (Sample, usize, usize) {
    let mut s = Sample { tick: sim.tick(), map: map_here(sim), ..Sample::default() };
    for i in 0..sim.player_count() {
        let Some(p) = sim.player_at(i) else {
            s.seats.push(Seat { team: usize::MAX, ..Seat::default() });
            continue;
        };
        let mut seat = Seat { team: p.team(), role: p.lane().and_then(|l| lane(l.code())), ..Seat::default() };
        if let Some(c) = p.champion() {
            let (x, y) = c.pos();
            seat.alive = c.is_alive();
            seat.pos = (x as f64, y as f64);
            seat.hp = c.hp().0;
        }
        s.seats.push(seat);
    }
    let mut nexus = 0;
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        match e.kind() {
            Some(EntityKindV1::Tower) if e.is_alive() => {
                let (x, y) = e.pos();
                s.towers.push((e.team(), (x as f64, y as f64)));
            }
            Some(EntityKindV1::Nexus) if e.is_alive() && e.hp().0 > 0 => nexus += 1,
            _ => {}
        }
    }
    let count = sim.kill_log_count();
    for k in kills_from..count {
        if let Some(e) = sim.kill_log_at(k) {
            s.kills.push(Kill {
                tick: e.tick,
                killer_team: e.killer_team,
                killer_role: lane(e.killer_position),
                victim_role: lane(e.killed_position),
                assists: e.assist_count,
            });
        }
    }
    (s, nexus, count)
}

fn head(o: SimOriginV1) -> String {
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[m={} s={}]", m(o.match_id), m(o.set_index))
}

/// Watches a presim run; writes its line when a nexus falls or the match ends.
fn watch(sim: &StableSim<'_>) {
    let Some(o) = sim.sim_origin() else { return };
    if SimOriginKindV1::from_code(o.kind) != Some(SimOriginKindV1::ServerPresim) {
        return;
    }
    let tick = sim.tick();
    let end = sim.is_end();
    if tick % SAMPLE != 0 && !end {
        return;
    }
    let key: RunKey = (o.kind, o.match_id, o.replay_id, o.set_index);
    // the kill-log entries already read (none when the run is new or started over)
    let from = {
        let book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
        book.runs.get(&key).map_or(0, |(_, t)| if tick < t.last_tick { 0 } else { t.kills_seen })
    };
    let (s, nexus, seen) = sample(sim, from);
    let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    book.clock += 1;
    let now = book.clock;
    let entry = book.runs.entry(key).or_insert_with(|| (now, Tracker::default()));
    // a run that starts over (the tick went back) is a new match
    if tick < entry.1.last_tick {
        entry.1 = Tracker::default();
    }
    entry.0 = now;
    entry.1.kills_seen = seen;
    entry.1.nexus_seen |= nexus == 2;
    let fallen = entry.1.nexus_seen && nexus < 2;
    entry.1.step(&s);
    if end || fallen {
        let Some((_, mut t)) = book.runs.remove(&key) else { return };
        t.finish();
        let line = t.line(&head(o));
        book.batch.add(&t);
        let sum = (book.batch.matches as usize >= SUMMARY_EVERY).then(|| std::mem::take(&mut book.batch).line());
        drop(book);
        wlog(line);
        if let Some(sum) = sum {
            sum_log(&sum);
            wlog(sum);
        }
        return;
    }
    if book.runs.len() > RUNS_KEPT {
        if let Some(old) = book.runs.iter().min_by_key(|(_, v)| v.0).map(|(k, _)| *k) {
            book.runs.remove(&old);
        }
    }
}

pub struct Watch;
impl StableMatchHook for Watch {
    fn on_match_tick(&self, sim: &mut StableSim<'_>, _rng_seed: u64) {
        watch(sim);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (read-only: how the teams fight, a MATCH line a match, a SUM line every {SUMMARY_EVERY}) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    // one match hook a mod: league_addons forwards to Watch
    #[cfg(not(league_bundle))]
    module.set_match_hook(Watch);
    #[cfg(league_bundle)]
    let _ = &module;
    host.log(LogLevel::Info, "league_fight_log loaded (read-only fight log).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    /// Blue (team 0) and red (team 1), positions top..support, all alive at these places.
    fn seats(blue: [Pos; 5], red: [Pos; 5]) -> Vec<Seat> {
        let mut v = Vec::new();
        for (team, side) in [blue, red].iter().enumerate() {
            for (r, p) in side.iter().enumerate() {
                v.push(Seat { team, role: Some(r), alive: true, pos: *p, hp: 1000 });
            }
        }
        v
    }

    #[test]
    fn a_dived_adc_and_a_teamfight() {
        let mut t = Tracker::default();
        // a bottom-lane brawl at (800k, 800k): blue's ADC (seat 3) dived by red's top laner (seat 5), blue's support
        // 50k away; four of each side within 150k; a blue tower right there
        let mut blue = [(790_000.0, 790_000.0), (760_000.0, 820_000.0), (840_000.0, 760_000.0), (800_000.0, 800_000.0), (850_000.0, 800_000.0)];
        let mut red = [(820_000.0, 800_000.0), (870_000.0, 870_000.0), (300_000.0, 300_000.0), (880_000.0, 820_000.0), (860_000.0, 860_000.0)];
        let towers = vec![(0usize, (780_000.0, 830_000.0)), (1usize, (100_000.0, 100_000.0))];
        t.step(&Sample { tick: 15, seats: seats(blue, red), towers: towers.clone(), kills: vec![], map: Map::Native });
        // the support comes next to the diver: helped
        blue[4] = (830_000.0, 810_000.0);
        let mut s = seats(blue, red);
        s[3].hp = 400;
        t.step(&Sample { tick: 30, seats: s.clone(), towers: towers.clone(), kills: vec![], map: Map::Native });
        // the ADC falls to red's top laner with one assist
        s[3].alive = false;
        s[3].hp = 0;
        let adc_down = Kill { tick: 40, killer_team: 1, killer_role: Some(0), victim_role: Some(3), assists: 1 };
        t.step(&Sample { tick: 45, seats: s.clone(), towers: towers.clone(), kills: vec![adc_down], map: Map::Native });
        // 2 s later blue's jungler kills red's top laner there, alone: the same fight
        red[0] = (815_000.0, 805_000.0);
        let mut s2 = seats(blue, red);
        s2[3].alive = false;
        t.step(&Sample { tick: 150, seats: s2.clone(), towers: towers.clone(), kills: vec![], map: Map::Native });
        s2[5].alive = false;
        let top_down = Kill { tick: 160, killer_team: 0, killer_role: Some(1), victim_role: Some(0), assists: 0 };
        t.step(&Sample { tick: 165, seats: s2, towers, kills: vec![top_down], map: Map::Native });
        t.finish();
        let c = &t.c;
        assert_eq!((c.deaths, c.early), ([1, 0, 0, 1, 0], [1, 0, 0, 1, 0]));
        assert_eq!(
            (c.placed, c.dived, c.enemy_tower, c.solo),
            (2, 1, 1, 1),
            "both fell by blue's tower: the ADC under his own (dived), red's top laner under the enemy's; the jungler's kill was solo"
        );
        assert_eq!((c.fights, c.teamfights, c.tf_kills, c.tf_first), (1, 1, 2, [0, 0, 0, 1, 0]), "one teamfight, the ADC first");
        assert_eq!((c.dives, c.support_near, c.peeled, c.adc_died, c.adc_died_peeled), (1, 1, 1, 1, 1));
        assert_eq!(c.damage[3], 600, "the ADC lost 600 before falling");
        assert!(c.contact[3] >= 30 && c.contact[0] >= 30, "the ADC and red's top laner next to each other: {:?}", c.contact);
        let line = t.line("[m=1 s=0]");
        assert!(line.contains("deaths=[T1 J0 M0 B1 S0]") && line.contains("tf_first=[T0 J0 M0 B1 S0]") && line.contains("adc_died=1 (1 peeled)"), "{line}");
        let mut b = Batch::default();
        b.add(&t);
        let sum = b.line();
        assert!(sum.starts_with("SUM 1 matches") && sum.contains("teamfights 1.0 with 2.0 deaths each"), "{sum}");
        assert!(sum.contains("ADC dived 1.0 a match: support within 60k 100%, helped in 3 s 100%, ADC died 100%"), "{sum}");
    }

    #[test]
    fn an_adc_dived_alone_and_a_gank() {
        let mut t = Tracker::default();
        // blue's ADC farms alone at mid map; red's jungler and mid laner jump him; blue's support is far away
        let blue = [(100_000.0, 100_000.0), (150_000.0, 700_000.0), (200_000.0, 500_000.0), (500_000.0, 500_000.0), (100_000.0, 900_000.0)];
        let red = [(900_000.0, 100_000.0), (520_000.0, 500_000.0), (500_000.0, 480_000.0), (900_000.0, 900_000.0), (950_000.0, 950_000.0)];
        t.step(&Sample { tick: 15, seats: seats(blue, red), towers: vec![], kills: vec![], map: Map::Native });
        let mut s = seats(blue, red);
        s[3].alive = false;
        let gank = Kill { tick: 20, killer_team: 1, killer_role: Some(1), victim_role: Some(3), assists: 1 };
        t.step(&Sample { tick: 30, seats: s.clone(), towers: vec![], kills: vec![gank], map: Map::Native });
        // a minion or a tower kill: no team, counted by position only
        let tower = Kill { tick: 40_000, killer_team: 9, killer_role: None, victim_role: Some(2), assists: 0 };
        t.step(&Sample { tick: 40_005, seats: s, towers: vec![], kills: vec![tower], map: Map::Native });
        t.finish();
        let c = &t.c;
        assert_eq!((c.deaths, c.early), ([0, 0, 1, 1, 0], [0, 0, 0, 1, 0]), "the mid death came after 10:00");
        assert_eq!((c.placed, c.outnumbered, c.solo, c.dived), (1, 1, 0, 0), "two red champions on him, none of his own");
        assert_eq!((c.fights, c.teamfights), (1, 0), "a gank, not a teamfight");
        assert_eq!((c.dives, c.support_near, c.peeled, c.adc_died), (1, 0, 0, 1));
        let mut b = Batch::default();
        b.add(&t);
        assert!(b.line().contains("helped 0%, not helped 100%"), "{}", b.line());
    }

    #[test]
    fn dives_need_a_gap_and_dates_read() {
        let mut t = Tracker::default();
        let blue = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (500_000.0, 500_000.0), (510_000.0, 500_000.0)];
        let red = [(510_000.0, 510_000.0), (900_000.0, 900_000.0), (900_000.0, 900_000.0), (900_000.0, 900_000.0), (900_000.0, 900_000.0)];
        // red's top laner stays next to blue's ADC for 8 s: one dive of 5 s, then a new one only after the gap
        for k in 1..=32 {
            t.step(&Sample { tick: k * SAMPLE, seats: seats(blue, red), towers: vec![], kills: vec![], map: Map::Native });
        }
        t.finish();
        assert_eq!(t.c.dives, 2, "{:?}", t.c);
        assert_eq!(t.c.peeled, 2, "the support stands next to the diver");
        assert_eq!(civil(0), (1970, 1, 1));
        assert_eq!(civil(20_765), (2026, 11, 8));
    }

    #[test]
    fn on_the_rift_red_s_half_is_on_the_map() {
        // a dive by red's top tower on the Rift (past 1200000): blue's ADC, red's top laner, blue's support beside him
        let blue = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (1_300_000.0, 400_000.0), (1_330_000.0, 410_000.0)];
        let red = [(1_320_000.0, 400_000.0), (1_450_000.0, 160_000.0), (1_450_000.0, 160_000.0), (1_450_000.0, 160_000.0), (1_450_000.0, 160_000.0)];
        let run = |map: Map| {
            let mut t = Tracker::default();
            for k in 1..=4 {
                t.step(&Sample { tick: k * SAMPLE, seats: seats(blue, red), towers: vec![], kills: vec![], map });
            }
            t.finish();
            t.c
        };
        let rift = run(Map::Rift);
        assert_eq!((rift.dives, rift.peeled), (1, 1), "{rift:?}");
        assert!(rift.contact[3] > 0 && rift.alive[3] > 0);
        // the game's own map's limit (1200000): nobody there, as before (nothing stands there on that map)
        let native = run(Map::Native);
        assert_eq!((native.dives, native.contact[3], native.alive[3]), (0, 0, 0));
        // parked far past the Rift too: off the map on both
        let parked = Seat { team: 0, role: Some(3), alive: true, pos: (3_000_000.0, 10.0), hp: 1 };
        assert!(!here_on(&parked, Map::Rift.limit()) && here_on(&Seat { pos: (1_300_000.0, 10.0), ..parked }, Map::Rift.limit()));
        assert_eq!(Sample::default().map, Map::Native);
    }
}
