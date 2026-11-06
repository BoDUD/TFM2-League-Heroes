//! 运营记录器（用户 2026-11-06：「现在游戏的AI逻辑非常差 非常不像LOL那种顶级的处理方式 对线 打团 拉扯 大龙打完后该干嘛
//! 还有不推基地之类的」，先量再改：「开始第 0+1 步」）。
//!
//! 只读的比赛钩子（`StableMatchHook`，附加包合集里由 league_addons 的 `BundleMatch` 转发），**不改游戏里的任何东西**。
//! 每场比赛只看服务器预演那一次（`ServerPresim`：每场都有，AI 之间的比赛也有；客户端重演、回放是同一场的重放，不再算），
//! 每 `SAMPLE` tick 取一次样：双方英雄在不在、在哪，防御塔、大龙（`Epic`）、小龙（`Serpen`）、基地。比赛结束时写一行 `MATCH`：
//!
//! - 时长、谁赢、双方击杀、推掉的塔、一塔的时间、10:00 前的击杀；
//! - 每条大龙 / 小龙谁拿的（死时 `TAKE_NEAR` 内哪边活着的英雄多）；
//! - 大龙之后 `CONV` tick（90 秒）拿龙的一方做了什么（`EPIC` 段）：推了几座塔、击杀 / 阵亡、平均几个人抱在一起
//!   （离本队活着英雄的中心 `GROUP` 以内）；
//! - 到了对面基地又走掉（`NEXUS`）：一方 3 个以上英雄在对面基地 `NEAR_NEXUS` 内待了 `VISIT` tick 以上，又散开了、
//!   基地还在——「不推基地」；
//! - 5:00 以后双方活着的英雄离本队中心的平均距离（`spread`，越小越抱团）。
//!
//! 每 `SUMMARY_EVERY` 场再写一行 `SUM`（这一批的平均），对比改动前后看这一行。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_macro_log.log`，每次启动游戏重写，上一次的留在 .prev.log；
//! 一次启动最多 `LOG_CAP` 行。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_macro_log";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_macro_log") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 多久取一次样（tick，0.5 秒）。
pub const SAMPLE: usize = 30;
/// 大龙之后看多久（tick，90 秒）。
pub const CONV: usize = 5400;
/// 抱团：离本队活着英雄的中心多近。
pub const GROUP: f64 = 120_000.0;
/// 龙死的时候这么近的英雄算在场（谁拿的）。
pub const TAKE_NEAR: f64 = 150_000.0;
/// 「到了对面基地」：离对面基地多近。
pub const NEAR_NEXUS: f64 = 200_000.0;
/// 在对面基地至少待多久才算一次（tick，3 秒）。
pub const VISIT: usize = 180;
/// 早期：10:00。
pub const EARLY: usize = 36_000;
/// 抱团从 5:00 起算。
pub const SPREAD_FROM: usize = 18_000;
/// 每多少场写一行平均。
pub const SUMMARY_EVERY: usize = 50;
/// 同时跟着的比赛最多几场（没结束就被丢掉的比赛不会一直占着）。
const RUNS_KEPT: usize = 64;
/// 一次启动最多写多少行。
const LOG_CAP: usize = 20_000;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_MACRO_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_macro_log.log");
        }
    }
    PathBuf::from("league_macro_log.log")
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

fn clock(t: usize) -> String {
    format!("{}:{:02}", t / 3600, t / 60 % 60)
}

const SIDE: [&str; 2] = ["blue", "red"];

// ===================== 一场比赛 =====================

/// What one sample saw of a champion.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Champ {
    pub team: usize,
    pub x: f64,
    pub y: f64,
}

/// An epic monster or a serpent seen alive.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Monster {
    pub id: usize,
    pub epic: bool,
    pub x: f64,
    pub y: f64,
}

/// One sample of a match: the living champions, the standing towers (id, team), the living monsters and the nexuses
/// (team, x, y, alive).
#[derive(Clone, Debug, Default)]
pub struct Sample {
    pub tick: usize,
    pub champs: Vec<Champ>,
    pub towers: Vec<(usize, usize)>,
    pub monsters: Vec<Monster>,
    pub nexus: Vec<(usize, f64, f64, bool)>,
}

/// After an epic monster: what the team that took it did in the next `CONV` ticks.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct After {
    pub team: usize,
    pub from: usize,
    pub towers: u32,
    pub grouped_sum: f64,
    pub samples: u32,
    /// The team's kills / the other team's kills when the window opened (kills and deaths come from the ends).
    pub kills_from: [usize; 2],
    pub kills_to: [usize; 2],
}

/// A match being watched.
#[derive(Clone, Debug, Default)]
pub struct Tracker {
    towers: HashMap<usize, usize>,
    monsters: HashMap<usize, Monster>,
    pub destroyed: [u32; 2],
    pub first_tower: Option<(usize, usize)>,
    /// (taker team or 2 when unclear, epic, tick)
    pub takes: Vec<(usize, bool, usize)>,
    pub after: Vec<After>,
    at_nexus: [usize; 2],
    pub visits: [u32; 2],
    pub left: [u32; 2],
    spread_sum: [f64; 2],
    spread_n: [u32; 2],
    pub kills: [usize; 2],
    pub early_kills: [usize; 2],
    pub last_tick: usize,
}

fn centroid(ps: &[Champ]) -> Option<(f64, f64)> {
    if ps.is_empty() {
        return None;
    }
    let n = ps.len() as f64;
    Some((ps.iter().map(|p| p.x).sum::<f64>() / n, ps.iter().map(|p| p.y).sum::<f64>() / n))
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

impl Tracker {
    /// One sample; `kills` the teams' kill counts now.
    pub fn step(&mut self, s: &Sample, kills: [usize; 2]) {
        self.last_tick = s.tick;
        self.kills = kills;
        if s.tick <= EARLY {
            self.early_kills = kills;
        }
        // towers that stood last time and are gone now
        let standing: HashMap<usize, usize> = s.towers.iter().copied().collect();
        for (id, team) in &self.towers {
            if !standing.contains_key(id) && *team < 2 {
                let by = 1 - team;
                self.destroyed[by] += 1;
                self.first_tower.get_or_insert((by, s.tick));
                for a in self.after.iter_mut().filter(|a| a.team == by && s.tick < a.from + CONV) {
                    a.towers += 1;
                }
            }
        }
        self.towers = standing;
        // monsters that were alive last time and are gone: who stood there
        let alive: HashMap<usize, Monster> = s.monsters.iter().map(|m| (m.id, *m)).collect();
        for (id, m) in &self.monsters {
            if alive.contains_key(id) {
                continue;
            }
            let near = |team: usize| s.champs.iter().filter(|c| c.team == team && dist((c.x, c.y), (m.x, m.y)) <= TAKE_NEAR).count();
            let (b, r) = (near(0), near(1));
            let team = if b > r { 0 } else if r > b { 1 } else { 2 };
            self.takes.push((team, m.epic, s.tick));
            if m.epic && team < 2 {
                self.after.push(After { team, from: s.tick, kills_from: kills, kills_to: kills, ..After::default() });
            }
        }
        self.monsters = alive;
        for team in 0..2 {
            let mine: Vec<Champ> = s.champs.iter().copied().filter(|c| c.team == team).collect();
            let Some(c) = centroid(&mine) else {
                self.leave_nexus(team, s);
                continue;
            };
            let spread = mine.iter().map(|p| dist((p.x, p.y), c)).sum::<f64>() / mine.len() as f64;
            if s.tick >= SPREAD_FROM && mine.len() >= 3 {
                self.spread_sum[team] += spread;
                self.spread_n[team] += 1;
            }
            let grouped = mine.iter().filter(|p| dist((p.x, p.y), c) <= GROUP).count() as f64;
            for a in self.after.iter_mut().filter(|a| a.team == team && s.tick < a.from + CONV) {
                a.grouped_sum += grouped;
                a.samples += 1;
                a.kills_to = kills;
            }
            // at the enemy nexus
            match s.nexus.iter().find(|n| n.0 == 1 - team && n.3) {
                Some(&(_, nx, ny, _)) if mine.iter().filter(|p| dist((p.x, p.y), (nx, ny)) <= NEAR_NEXUS).count() >= 3 => {
                    self.at_nexus[team] += SAMPLE;
                }
                _ => self.leave_nexus(team, s),
            }
        }
    }

    fn leave_nexus(&mut self, team: usize, s: &Sample) {
        if self.at_nexus[team] >= VISIT {
            self.visits[team] += 1;
            if s.nexus.iter().any(|n| n.0 == 1 - team && n.3) {
                self.left[team] += 1;
            }
        }
        self.at_nexus[team] = 0;
    }

    /// The `MATCH` line (`head`: where it came from); `winner` the team whose nexus stands.
    pub fn line(&self, head: &str, winner: Option<usize>) -> String {
        let takes = |epic: bool| -> String {
            let v: Vec<String> = self
                .takes
                .iter()
                .filter(|t| t.1 == epic)
                .map(|t| format!("{}@{}", ["B", "R", "?"][t.0], clock(t.2)))
                .collect();
            v.join(",")
        };
        let after: Vec<String> = self
            .after
            .iter()
            .map(|a| {
                format!(
                    "{} towers {} kills {} deaths {} grouped {:.1}",
                    ["B", "R"][a.team],
                    a.towers,
                    a.kills_to[a.team] - a.kills_from[a.team],
                    a.kills_to[1 - a.team] - a.kills_from[1 - a.team],
                    a.grouped_sum / a.samples.max(1) as f64
                )
            })
            .collect();
        let spread = |t: usize| self.spread_sum[t] / self.spread_n[t].max(1) as f64 / 1000.0;
        format!(
            "MATCH {head} len={} win={} kills={}-{} early_kills={}-{} towers={}-{} first_tower={} epics=[{}] serpens=[{}] after_epic=[{}] nexus_visits={}-{} nexus_left={}-{} spread={:.0}k-{:.0}k",
            clock(self.last_tick),
            winner.map_or("-", |w| SIDE[w]),
            self.kills[0],
            self.kills[1],
            self.early_kills[0],
            self.early_kills[1],
            self.destroyed[0],
            self.destroyed[1],
            self.first_tower.map_or("-".to_string(), |(t, at)| format!("{}@{}", ["B", "R"][t], clock(at))),
            takes(true),
            takes(false),
            after.join("; "),
            self.visits[0],
            self.visits[1],
            self.left[0],
            self.left[1],
            spread(0),
            spread(1)
        )
    }
}

// ===================== 平均 =====================

/// What the `SUM` line averages over a batch of matches.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Batch {
    pub matches: u32,
    pub ticks: u64,
    pub kills: u64,
    pub early_kills: u64,
    pub towers: u64,
    pub first_tower: u64,
    pub first_towers: u32,
    pub epics: u32,
    pub epic_towers: u64,
    pub epic_kills: u64,
    pub epic_deaths: u64,
    pub epic_grouped: f64,
    pub visits: u32,
    pub left: u32,
    pub spread: f64,
}

impl Batch {
    pub fn add(&mut self, t: &Tracker) {
        self.matches += 1;
        self.ticks += t.last_tick as u64;
        self.kills += (t.kills[0] + t.kills[1]) as u64;
        self.early_kills += (t.early_kills[0] + t.early_kills[1]) as u64;
        self.towers += (t.destroyed[0] + t.destroyed[1]) as u64;
        if let Some((_, at)) = t.first_tower {
            self.first_tower += at as u64;
            self.first_towers += 1;
        }
        for a in &t.after {
            self.epics += 1;
            self.epic_towers += a.towers as u64;
            self.epic_kills += (a.kills_to[a.team] - a.kills_from[a.team]) as u64;
            self.epic_deaths += (a.kills_to[1 - a.team] - a.kills_from[1 - a.team]) as u64;
            self.epic_grouped += a.grouped_sum / a.samples.max(1) as f64;
        }
        self.visits += t.visits[0] + t.visits[1];
        self.left += t.left[0] + t.left[1];
        let spread = |i: usize| t.spread_sum[i] / t.spread_n[i].max(1) as f64;
        self.spread += (spread(0) + spread(1)) / 2.0;
    }

    pub fn line(&self) -> String {
        let m = self.matches.max(1) as f64;
        let e = self.epics.max(1) as f64;
        format!(
            "SUM {} matches: len {} kills {:.1} (before 10:00 {:.1}) towers {:.1} first tower {} | epics {:.2} a match, in the 90 s after: towers {:.2} kills {:.2} deaths {:.2} grouped {:.2} | at the enemy nexus {:.2} a match, walked away {:.2} | spread {:.0}k",
            self.matches,
            clock((self.ticks as f64 / m) as usize),
            self.kills as f64 / m,
            self.early_kills as f64 / m,
            self.towers as f64 / m,
            clock((self.first_tower as f64 / self.first_towers.max(1) as f64) as usize),
            self.epics as f64 / m,
            self.epic_towers as f64 / e,
            self.epic_kills as f64 / e,
            self.epic_deaths as f64 / e,
            self.epic_grouped / e,
            self.visits as f64 / m,
            self.left as f64 / m,
            self.spread / m / 1000.0
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

fn sample(sim: &StableSim<'_>) -> (Sample, [usize; 2]) {
    let mut s = Sample { tick: sim.tick(), ..Sample::default() };
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        let (x, y) = e.pos();
        let (x, y) = (x as f64, y as f64);
        match e.kind() {
            Some(EntityKindV1::Champion) if e.is_alive() => s.champs.push(Champ { team: e.team(), x, y }),
            Some(EntityKindV1::Tower) if e.is_alive() => s.towers.push((e.id(), e.team())),
            Some(EntityKindV1::Epic) if e.is_alive() => s.monsters.push(Monster { id: e.id(), epic: true, x, y }),
            Some(EntityKindV1::Serpen) if e.is_alive() => s.monsters.push(Monster { id: e.id(), epic: false, x, y }),
            Some(EntityKindV1::Nexus) => s.nexus.push((e.team(), x, y, e.is_alive() && e.hp().0 > 0)),
            _ => {}
        }
    }
    let mut kills = [0usize; 2];
    for i in 0..sim.player_count() {
        if let Some(p) = sim.player_at(i) {
            if let Some(k) = kills.get_mut(p.team()) {
                *k += p.kills();
            }
        }
    }
    (s, kills)
}

fn head(o: SimOriginV1) -> String {
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[m={} s={}]", m(o.match_id), m(o.set_index))
}

/// Watches a presim run; writes its line when its nexus falls or the match ends.
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
    let (s, kills) = sample(sim);
    let fallen = s.nexus.iter().find(|n| !n.3).map(|n| n.0);
    let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    book.clock += 1;
    let now = book.clock;
    let entry = book.runs.entry(key).or_insert_with(|| (now, Tracker::default()));
    // a run that starts over (the tick went back) is a new match
    if tick < entry.1.last_tick {
        entry.1 = Tracker::default();
    }
    entry.0 = now;
    entry.1.step(&s, kills);
    if end || fallen.is_some() {
        let Some((_, t)) = book.runs.remove(&key) else { return };
        let line = t.line(&head(o), fallen.map(|f| 1 - f));
        book.batch.add(&t);
        let sum = (book.batch.matches as usize >= SUMMARY_EVERY).then(|| std::mem::take(&mut book.batch).line());
        drop(book);
        wlog(line);
        if let Some(sum) = sum {
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

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (read-only: what the teams do on the map, a MATCH line a match, a SUM line every {SUMMARY_EVERY}) loaded: game {}.{}.{} abi {} log={} ===",
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
    host.log(LogLevel::Info, "league_macro_log loaded (read-only macro log).");
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

    fn champs(team: usize, at: (f64, f64), n: usize) -> Vec<Champ> {
        (0..n).map(|i| Champ { team, x: at.0 + i as f64 * 1000.0, y: at.1 }).collect()
    }

    #[test]
    fn a_match_seen_through() {
        let mut t = Tracker::default();
        let nexus = vec![(0usize, 100_000.0, 860_000.0, true), (1usize, 860_000.0, 100_000.0, true)];
        let towers = vec![(10usize, 0usize), (11, 1), (12, 1)];
        let baron = Monster { id: 50, epic: true, x: 300_000.0, y: 300_000.0 };
        // red's champions at the baron, blue's away
        let mut s = Sample { tick: 30, champs: [champs(0, (100_000.0, 800_000.0), 5), champs(1, (300_000.0, 300_000.0), 5)].concat(), towers: towers.clone(), monsters: vec![baron], nexus: nexus.clone() };
        t.step(&s, [0, 0]);
        // the baron dies with red round it
        s.tick = 60;
        s.monsters.clear();
        t.step(&s, [0, 1]);
        assert_eq!(t.takes, vec![(1, true, 60)]);
        assert_eq!(t.after.len(), 1);
        // a blue tower falls in the next 90 s; red stands at blue's nexus for 10 s, then walks away
        s.tick = 90;
        s.towers = vec![(11, 1), (12, 1)];
        s.champs = [champs(0, (500_000.0, 500_000.0), 5), champs(1, (110_000.0, 850_000.0), 4)].concat();
        t.step(&s, [0, 2]);
        for k in 1..=20 {
            s.tick = 90 + k * SAMPLE;
            t.step(&s, [0, 2]);
        }
        s.tick += SAMPLE;
        s.champs = [champs(0, (500_000.0, 500_000.0), 5), champs(1, (400_000.0, 400_000.0), 4)].concat();
        t.step(&s, [0, 2]);
        assert_eq!((t.destroyed, t.first_tower), ([0, 1], Some((1, 90))));
        assert_eq!((t.visits, t.left), ([0, 1], [0, 1]), "at blue's nexus and away again, the nexus standing");
        let a = &t.after[0];
        assert_eq!((a.towers, a.kills_to[1] - a.kills_from[1]), (1, 1));
        assert!(a.grouped_sum / a.samples as f64 > 3.9, "red grouped: {a:?}");
        let line = t.line("[m=1 s=0]", None);
        assert!(line.contains("epics=[R@0:01]") && line.contains("towers=0-1") && line.contains("nexus_left=0-1"), "{line}");
        let mut b = Batch::default();
        b.add(&t);
        assert!(b.line().starts_with("SUM 1 matches"), "{}", b.line());
    }

    #[test]
    fn an_unclear_take_is_nobodys() {
        let mut t = Tracker::default();
        let m = Monster { id: 7, epic: false, x: 0.0, y: 0.0 };
        t.step(&Sample { tick: 0, monsters: vec![m], ..Sample::default() }, [0, 0]);
        t.step(&Sample { tick: 30, ..Sample::default() }, [0, 0]);
        assert_eq!(t.takes, vec![(2, false, 30)]);
        assert!(t.after.is_empty());
    }
}
