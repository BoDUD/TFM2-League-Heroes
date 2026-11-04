//! 英雄联盟音效（用户 2026-10-30：「游戏内BP界面的音乐 还有对局内的音乐 一血 双杀 三杀 四杀 五杀都能改成和英雄联盟一样的吗
//! 单独做个启动mod」）。
//!
//! BP 音乐、对局里的声音、双杀到五杀都是数据：`mod.override_info` 把游戏自己的 `sound/bgm/*` 和四个连杀音效
//! （dual_takedown / triple_takedown / devastation / annihilation，就是 kill2..kill5 的横幅）换成 `build_audio.py`
//! 从本机英雄联盟客户端取出的音频。游戏没有的播报由这个 DLL 的比赛钩子每 tick 看着放（英雄联盟中文女声播报员）：
//!
//! - **一血**：一局里第一条英雄击杀（击杀记录里凶手是一名玩家的英雄，死的是对面的英雄）。塔、小兵、野怪杀的不算；
//!   打开时第一滴血已经过去 `FRESH` tick 以上的（中途观战）不补放。
//! - **被处决**（0.1.3）：英雄死了，死前死后 `WAIT` tick 的击杀记录里找不到一条杀的是他、凶手又是对面英雄的。
//!   同一 tick `MASS` 个以上没有凶手的阵亡不播（像比赛在收尾）。
//! - 0.2.0（用户 2026-11-04：「播报补全 … 可以先把这个补全」）：
//!   - **连杀**：一名英雄这条命连续击杀 3..8 个及以上：大杀特杀、杀人如麻、势不可挡、横扫千军、接近神了、超神
//!     （英雄联盟的 KillingSpree / Rampage / Unstoppable / Dominating / Godlike / Legendary）。这一杀离他上一杀不到
//!     `MULTI` tick 的不播：游戏自己在放双杀..五杀，英雄联盟也是多杀优先。
//!   - **终结**：杀掉一名已经连杀 3 个及以上的英雄（Shutdown）。
//!   - **团灭**：一队的英雄全部倒下（Ace）。
//!   - **防御塔被摧毁**：游戏的塔（含水晶前的双塔）倒下。
//!   - **巨龙 / 纳什男爵**：游戏的双角巨蛇（Serpen）、莫尔加德（Epic）被击杀。谁拿的：击杀后 `DECIDE` tick 里哪一队的
//!     英雄或小兵整队多了一个新增益（双角巨蛇给英雄、莫尔加德给小兵），或者整队金钱多涨了；都看不出时算离它最近的英雄
//!     那一队。日志 `OBJECTIVE` 行写着是怎么认出来的。
//!   - **胜利 / 失败**：水晶枢纽倒下（比赛结束时没看到枢纽倒下，就比两边枢纽剩下的生命）。
//!
//! **我方 / 敌方**：游戏的比赛画面顶上写着蓝色方、红色方的队名（`ingame.header.blue_info.team_name` /
//! `red_info.team_name`，选人界面的 `main.blue_picks` / `red_picks` 也有），客户端扩展拿它和你的队名
//! （`player_team_id` → `team_name`）比，认出你是哪一边（游戏的 team 0 = 蓝色方）。认出来了：连杀分「我方 / 敌方」
//! 两种说法，防御塔说「我方防御塔被摧毁」或「摧毁了敌方防御塔」，比赛结束说「胜利」或「失败」；没认出来（看别的队的
//! 比赛）用中立或蓝色方 / 红色方的说法。巨龙、男爵在英雄联盟的语音包里只有「蓝色方 / 红色方 / 中立」三种
//! （`KillDragonBlue/Red/purple`、`KillWormBlue/Red/purple`），按拿下的那一队的颜色放。
//!
//! 播报排队放：一条放完（`GAP` tick）才放下一条，等了 `EXPIRE` tick 还没轮到的扔掉（胜负那句插到最前面、清掉别的）。
//!
//! 只在看得见、听得见的比赛里放（观看、观战、回放）；后台预演的比赛（`ServerPresim`）和别的队伍在后台打的比赛
//! （kind 0）跳过。游戏把屏幕上的每一局用同一个来历（来历 + 比赛 + 第几局 + 回放）跑两遍：第一遍是屏幕上的，第二遍在
//! 这一局快结束时从 0 tick 再快跑一遍。所以每个来历记下见过的最大 tick，tick 一比它小就是第二遍，这一遍整个不管。
//! 记最近 `KEEP` 局。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\lol_audio.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! 每句播报一行 `SAY`（放了没有、放在谁身上），`SIDE` 行（认出你是哪一边），`OBJECTIVE` 行（巨龙 / 男爵是谁拿的、怎么
//! 认的），`EXECUTED` 行（被处决的那次死前死后的击杀记录）；每局一行 `SET`（比赛结束或第二遍开始时，先到的那次）。

use std::collections::{BTreeMap, HashMap};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};
use std::time::{Duration, Instant};

use mod_api_stable::*;

const ID: &str = "lol_audio";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// A first kill older than this when the view first sees it is not announced (spectating or a replay opened mid-match).
pub const FRESH: usize = 30;
/// A kill-log entry this many ticks before or after a death can be that death's; a death waits this long for it.
pub const WAIT: usize = 6;
/// This many deaths in one tick with no killer are not executions (a match being wound up): not announced.
pub const MASS: usize = 3;
/// A gap of more ticks than this between two calls (a replay skipped ahead): no deaths are taken across it.
pub const JUMP: usize = 30;
/// How long (ticks) kill-log entries are kept for the deaths waiting on them.
const RECENT: usize = 60;
/// How many matches are remembered.
const KEEP: usize = 64;
const LOG_CAP: usize = 4_000;
/// A kill this soon (ticks) after the killer's last one is part of a multi-kill the game announces itself: no spree line.
pub const MULTI: usize = 600;
/// Kills in one life from which on the spree lines play (League: three).
pub const SPREE: usize = 3;
/// Ticks between two announcer lines (a line is 2.4-4.3 s after its tail is cut; 60 ticks a second).
pub const GAP: usize = 240;
/// A line still waiting after this many ticks is dropped.
pub const EXPIRE: usize = 480;
/// Ticks after an epic monster's death at which the team that took it is decided.
pub const DECIDE: usize = 30;
/// A team's median gold gain over the other's from which the gold tells who took a monster.
pub const GOLD_EDGE: usize = 25;
/// Entities of one team that must have gained the same new buff for it to tell who took a monster.
pub const BUFF_MIN: usize = 2;
/// Team 0 is the blue side (the classic map's blue nexus is team 0's).
pub const BLUE: usize = 0;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);

fn log_path() -> PathBuf {
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("lol_audio.log");
        }
    }
    PathBuf::from("lol_audio.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);
static START: LazyLock<Instant> = LazyLock::new(Instant::now);

fn wlog(msg: impl AsRef<str>) {
    if LINES.fetch_add(1, Ordering::Relaxed) >= LOG_CAP {
        return;
    }
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        // seconds since the add-on loaded: tells the game's two runs of a match apart
        let _ = f.write_all(format!("[{:9.3}s] {}\n", START.elapsed().as_secs_f64(), msg.as_ref()).as_bytes());
    }
}

// ===================== 播报 =====================

/// One announcer line.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Say {
    FirstBlood,
    Executed,
    Ace,
    Shutdown,
    /// `kills` in one life (3..), by a champion of `team`.
    Spree { kills: usize, team: usize },
    /// A tower of `owner` fell.
    Turret { owner: usize },
    /// Serpen (dragon) or Morgard (baron, `epic`) killed by `team` (`None`: not told).
    Objective { epic: bool, team: Option<usize> },
    /// The match is won by `winner`.
    Victory { winner: usize },
}

/// The spree lines from three kills in a life on, League's names (the last one repeats).
const SPREES: [&str; 6] = ["killing_spree", "rampage", "unstoppable", "dominating", "godlike", "legendary"];

/// The sound event of a line (`lol_audio_<name>`, sound/sfx/lol_audio_<name>.sound_info). `side`: the user's team in
/// this match, when told.
pub fn sfx(say: Say, side: Option<usize>) -> String {
    let colour = |team: usize| if team == BLUE { "blue" } else { "red" };
    let name = match say {
        Say::FirstBlood => "first_blood".to_string(),
        Say::Executed => "executed".to_string(),
        Say::Ace => "ace".to_string(),
        Say::Shutdown => "shutdown".to_string(),
        Say::Spree { kills, team } => {
            let line = SPREES[kills.saturating_sub(SPREE).min(SPREES.len() - 1)];
            match side {
                Some(s) if s != team => format!("{line}_enemy"),
                _ => line.to_string(),
            }
        }
        Say::Turret { owner } => match side {
            Some(s) if s == owner => "turret_ours".to_string(),
            Some(_) => "turret_theirs".to_string(),
            None => "turret".to_string(),
        },
        Say::Objective { epic, team } => {
            let what = if epic { "baron" } else { "dragon" };
            match team {
                Some(t) => format!("{what}_{}", colour(t)),
                None => what.to_string(),
            }
        }
        Say::Victory { winner } => match side {
            Some(s) if s == winner => "victory".to_string(),
            Some(_) => "defeat".to_string(),
            None => format!("victory_{}", colour(winner)),
        },
    };
    format!("lol_audio_{name}")
}

/// A line waiting its turn: where it plays (`on`, else the living champion nearest to `at`) and since when it waits.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Line {
    pub say: Say,
    pub on: Option<usize>,
    pub at: (u64, u64),
    pub since: usize,
}

/// The lines waiting, one at a time `GAP` ticks apart.
#[derive(Debug, Default)]
pub struct Queue {
    lines: Vec<Line>,
    free_at: usize,
}

impl Queue {
    pub fn push(&mut self, line: Line) {
        if matches!(line.say, Say::Victory { .. }) {
            // the last word: before everything, and nothing after it
            self.lines.clear();
            self.free_at = 0;
        }
        self.lines.push(line);
    }

    /// The line to play now, if its turn has come; lines waiting longer than `EXPIRE` are dropped (returned second).
    pub fn next(&mut self, now: usize) -> (Option<Line>, Vec<Line>) {
        let (stale, keep): (Vec<_>, Vec<_>) = std::mem::take(&mut self.lines)
            .into_iter()
            .partition(|l| now > l.since + EXPIRE && !matches!(l.say, Say::Victory { .. }));
        self.lines = keep;
        if now < self.free_at || self.lines.is_empty() {
            return (None, stale);
        }
        self.free_at = now + GAP;
        (Some(self.lines.remove(0)), stale)
    }
}

// ===================== 哪一遍 =====================

/// One match as the view sees it: origin kind, match id, set index, replay id.
pub type Key = (u32, u64, u64, u64);

/// Which run of a match a tick belongs to.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Pass {
    /// The first run, the one on screen: its ticks never go down.
    Live,
    /// A run from below the first run's top tick (the game's second run from tick 0, or a replay rewound): ignored
    /// entirely. `first`: its first tick.
    Again { first: bool },
}

// ===================== 看比赛 =====================

/// What to do with a match's first blood.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Call {
    /// Announce it now.
    Play,
    /// Seen too late (spectating mid-match): stay quiet.
    Skip,
}

/// One player's champion this tick, as the death check sees it.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Champ {
    pub player: usize,
    /// The champion entity, the sound's place: a new one each life (`usize::MAX` while the player has none).
    pub id: usize,
    pub team: usize,
    /// [`LaneV1`] code: the kill log names players by team and lane.
    pub lane: u32,
    /// The player is alive, and so is his champion entity.
    pub alive: bool,
    /// Where the champion stands.
    pub pos: (u64, u64),
}

/// A tower or a nexus standing this tick.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Building {
    pub id: usize,
    pub team: usize,
    pub nexus: bool,
    pub pos: (u64, u64),
    /// Hit points out of 1000.
    pub hp: usize,
}

/// A Serpen or Morgard alive this tick.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Monster {
    pub id: usize,
    pub epic: bool,
    pub pos: (u64, u64),
}

/// One tick of the match as the hook reads it.
#[derive(Clone, Debug, Default)]
pub struct Frame {
    /// Every player's champion (the players with a lane).
    pub champs: Vec<Champ>,
    /// The kill-log entries added since the last tick.
    pub new_kills: Vec<KillLogV1>,
    /// The match has ended.
    pub over: bool,
    /// The towers and nexuses standing, and the nexuses' hit points (fallen ones too: 0).
    pub buildings: Vec<Building>,
    /// The epic monsters alive.
    pub monsters: Vec<Monster>,
}

/// What tells who took an epic monster, read when it died and `DECIDE` ticks later.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Evidence {
    /// Each team's players' gold.
    pub gold: [Vec<usize>; 2],
    /// (team, buff name) -> how many of that team's champions and minions have it.
    pub buffs: BTreeMap<(usize, String), usize>,
}

fn median(v: &[usize]) -> usize {
    let mut v = v.to_vec();
    v.sort_unstable();
    v.get(v.len() / 2).copied().unwrap_or(0)
}

/// Who took the monster, and by what: a buff new on `BUFF_MIN` entities of one team only, else a team's median gold
/// gain `GOLD_EDGE` over the other's, else the team of the champion nearest to where it fell.
pub fn decide(before: &Evidence, after: &Evidence, nearest: Option<usize>) -> (Option<usize>, String) {
    let new_buffs = |team: usize| -> Vec<String> {
        after
            .buffs
            .iter()
            .filter(|((t, name), n)| *t == team && **n >= BUFF_MIN && !before.buffs.contains_key(&(team, name.clone())))
            .map(|((_, name), n)| format!("{name} x{n}"))
            .collect()
    };
    let (b0, b1) = (new_buffs(0), new_buffs(1));
    match (b0.is_empty(), b1.is_empty()) {
        (false, true) => return (Some(0), format!("buff on team 0: {}", b0.join(", "))),
        (true, false) => return (Some(1), format!("buff on team 1: {}", b1.join(", "))),
        _ => {}
    }
    let gain = |t: usize| -> usize {
        let d: Vec<usize> = after.gold[t]
            .iter()
            .zip(&before.gold[t])
            .map(|(a, b)| a.saturating_sub(*b))
            .collect();
        median(&d)
    };
    let (g0, g1) = (gain(0), gain(1));
    let why = format!("buffs {}/{} new, gold +{g0}/+{g1}", b0.len(), b1.len());
    if g0 >= g1 + GOLD_EDGE {
        return (Some(0), format!("gold: {why}"));
    }
    if g1 >= g0 + GOLD_EDGE {
        return (Some(1), format!("gold: {why}"));
    }
    match nearest {
        Some(t) => (Some(t), format!("nearest champion: {why}")),
        None => (None, format!("not told: {why}")),
    }
}

/// A kill-log entry made by one player's champion on a champion of the other team. `champs`: every player.
pub fn by_champion(k: &KillLogV1, champs: &[Champ]) -> bool {
    champs.iter().any(|c| c.team == k.killer_team && c.lane == k.killer_position)
        && champs.iter().any(|c| c.team != k.killer_team && c.lane == k.killed_position)
}

/// The kill-log entry of a champion killing `victim`, who died at tick `at`: within `WAIT` ticks of the death, naming
/// his lane on his team (an entry's victim is on the team that is not the killer's), made by a player's champion.
pub fn champion_kill<'k>(victim: &Champ, at: usize, kills: &'k [KillLogV1], champs: &[Champ]) -> Option<&'k KillLogV1> {
    kills.iter().find(|k| {
        k.tick + WAIT >= at
            && k.tick <= at + WAIT
            && k.killed_position == victim.lane
            && k.killer_team != victim.team
            && by_champion(k, champs)
    })
}

/// The players alive in `before` and dead in `now`, as they were last seen alive (that life's entity, that place).
pub fn died(before: &[Champ], now: &[Champ]) -> Vec<Champ> {
    now.iter()
        .filter(|c| !c.alive)
        .filter_map(|c| before.iter().find(|b| b.player == c.player && b.alive))
        .map(|b| Champ { alive: false, ..*b })
        .collect()
}

/// Counts for the SET line.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Tally {
    /// Champions who died (alive one tick, dead the next).
    pub deaths: usize,
    /// Of those: a champion kill in the log.
    pub by_champions: usize,
    /// Of those: executed.
    pub executed: usize,
    /// Of those: no killer, but too many in one tick to be executions.
    pub at_once: usize,
    /// Kill-log entries.
    pub entries: usize,
    /// Of those: the killer is not a player's champion.
    pub odd: usize,
    /// Towers fallen, epic monsters killed, lines queued, lines played, lines dropped.
    pub towers: usize,
    pub monsters: usize,
    pub queued: usize,
    pub played: usize,
    pub dropped: usize,
}

/// A monster that died, waiting `DECIDE` ticks for who took it.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Pending {
    pub monster: Monster,
    pub at: usize,
    pub before: Evidence,
}

/// What one tick of the first run brings besides the lines it queued.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Step {
    /// The first blood, on the tick it shows up.
    pub first_blood: Option<(Call, KillLogV1)>,
    /// Executed champions, (tick of death, champion).
    pub executed: Vec<(usize, Champ)>,
    /// Deaths with no killer, too many in one tick to be executions: not announced.
    pub at_once: Vec<(usize, Champ)>,
    /// Monsters that died this tick: the hook reads their `before` evidence and calls [`Watch::pend`].
    pub monsters_died: Vec<Monster>,
}

/// What one match (origin key) has seen.
#[derive(Debug, Default)]
pub struct Watch {
    /// The highest tick seen: the first run's.
    top: usize,
    /// A second run began: nothing more is announced for this match.
    again: bool,
    /// The first blood came (played, or seen too late).
    first_blood: bool,
    /// Kill-log entries read so far.
    pub read: usize,
    /// The kill-log entries of the last `RECENT` ticks, for the deaths waiting on them.
    pub recent: Vec<KillLogV1>,
    /// The champions on the last tick, and that tick.
    last: Option<(usize, Vec<Champ>)>,
    /// Deaths waiting `WAIT` ticks for their kill-log entry: (tick of death, champion).
    pending: Vec<(usize, Champ)>,
    /// (team, lane) -> kills in this life, and the tick of the last one.
    streak: HashMap<(usize, u32), (usize, usize)>,
    /// Teams wholly dead now (their ace was said, or they were dead when first seen).
    aced: [bool; 2],
    /// The towers and nexuses standing on the last tick.
    standing: Option<Vec<Building>>,
    /// The monsters alive on the last tick.
    monsters: Option<Vec<Monster>>,
    /// Monsters waiting for who took them.
    pub objectives: Vec<Pending>,
    /// The match's result was said.
    won: bool,
    pub queue: Queue,
    pub tally: Tally,
    /// The SET line was written.
    summed: bool,
}

impl Watch {
    /// The run filter: `Live` while the ticks never go down, `Again` from the first tick below the top on (for good:
    /// the second run's ticks pass the first run's top too, and stay ignored).
    pub fn pass(&mut self, tick: usize) -> Pass {
        if self.again {
            return Pass::Again { first: false };
        }
        if tick < self.top {
            self.again = true;
            return Pass::Again { first: true };
        }
        self.top = tick;
        Pass::Live
    }

    fn say(&mut self, now: usize, say: Say, on: Option<usize>, at: (u64, u64)) {
        self.tally.queued += 1;
        self.queue.push(Line { say, on, at, since: now });
    }

    /// The champion of (team, lane), if any.
    fn champ(champs: &[Champ], team: usize, lane: u32) -> Option<&Champ> {
        champs.iter().find(|c| c.team == team && c.lane == lane)
    }

    /// One tick of the first run: queues its lines.
    pub fn step(&mut self, now: usize, f: Frame) -> Step {
        let mut step = Step::default();
        let Frame { champs, new_kills, over, buildings, monsters } = f;
        let jumped = self.last.as_ref().is_some_and(|(then, _)| now > then + JUMP);
        self.tally.entries += new_kills.len();
        self.tally.odd += new_kills.iter().filter(|k| !by_champion(k, &champs)).count();
        self.recent.extend_from_slice(&new_kills);
        self.recent.retain(|k| k.tick + RECENT >= now);

        // champion kills: first blood, sprees, shutdowns
        for k in new_kills.iter().filter(|k| by_champion(k, &champs)) {
            let fresh = now.saturating_sub(k.tick) <= FRESH;
            let killer = Self::champ(&champs, k.killer_team, k.killer_position).copied();
            let victim = Self::champ(&champs, k.killer_team ^ 1, k.killed_position).copied();
            let (on, at) = (killer.map(|c| c.id), killer.map_or((0, 0), |c| c.pos));
            if !self.first_blood {
                self.first_blood = true;
                let call = if fresh { Call::Play } else { Call::Skip };
                step.first_blood = Some((call, *k));
                if call == Call::Play && !over {
                    self.say(now, Say::FirstBlood, on, at);
                }
            }
            let victim_streak = self.streak.remove(&(k.killer_team ^ 1, k.killed_position)).map_or(0, |s| s.0);
            let (kills, last) = self.streak.get(&(k.killer_team, k.killer_position)).copied().unwrap_or((0, 0));
            let multi = kills > 0 && k.tick < last + MULTI;
            let kills = kills + 1;
            self.streak.insert((k.killer_team, k.killer_position), (kills, k.tick));
            if !fresh || over {
                continue;
            }
            if victim_streak >= SPREE {
                self.say(now, Say::Shutdown, on, victim.map_or(at, |v| v.pos));
            }
            if kills >= SPREE && !multi {
                self.say(now, Say::Spree { kills, team: k.killer_team }, on, at);
            }
        }

        // deaths: alive on the last tick, dead now (none after the end, none across a jump)
        let mut fell = [false; 2];
        if let Some((_, before)) = &self.last {
            if !over && !jumped {
                for c in died(before, &champs) {
                    self.tally.deaths += 1;
                    fell[c.team & 1] = true;
                    self.pending.push((now, c));
                }
            }
        }
        // the deaths that waited `WAIT` ticks for their kill-log entry
        let (due, wait): (Vec<_>, Vec<_>) =
            std::mem::take(&mut self.pending).into_iter().partition(|(at, _)| now >= at + WAIT);
        self.pending = wait;
        let mut lone = Vec::new();
        for (at, c) in due {
            if champion_kill(&c, at, &self.recent, &champs).is_some() {
                self.tally.by_champions += 1;
            } else {
                lone.push((at, c));
            }
        }
        for &(at, c) in &lone {
            // no champion took the kill: the streak ends without a shutdown
            self.streak.remove(&(c.team, c.lane));
            if lone.iter().filter(|(t, _)| *t == at).count() >= MASS {
                self.tally.at_once += 1;
                step.at_once.push((at, c));
            } else {
                self.tally.executed += 1;
                step.executed.push((at, c));
                if !over {
                    self.say(now, Say::Executed, Some(c.id), c.pos);
                }
            }
        }

        // ace: every champion of a team down (once, until one of them is back)
        for team in 0..2 {
            let mine: Vec<&Champ> = champs.iter().filter(|c| c.team == team).collect();
            let all_down = !mine.is_empty() && mine.iter().all(|c| !c.alive);
            if !all_down {
                self.aced[team] = false;
            } else if !self.aced[team] {
                self.aced[team] = true;
                // a wipe seen as it happens (not dead from the first look, not the end of the match)
                if fell[team] && !over {
                    let at = self.last.as_ref().and_then(|(_, b)| b.iter().find(|c| c.team == team)).map_or((0, 0), |c| c.pos);
                    self.say(now, Say::Ace, None, at);
                }
            }
        }

        // towers and nexuses
        if let Some(before) = self.standing.take() {
            if !jumped && !self.won {
                for b in before.iter().filter(|b| b.hp > 0) {
                    let stands = buildings.iter().any(|n| n.id == b.id && n.hp > 0);
                    if stands {
                        continue;
                    }
                    if b.nexus {
                        self.won = true;
                        self.say(now, Say::Victory { winner: b.team ^ 1 }, None, b.pos);
                    } else if !over {
                        self.tally.towers += 1;
                        self.say(now, Say::Turret { owner: b.team }, None, b.pos);
                    }
                }
            }
        }
        if over && !self.won && !jumped {
            // the end came without a nexus seen falling: the side with more of its nexus left won
            self.won = true;
            let left = |t: usize| buildings.iter().filter(|b| b.nexus && b.team == t).map(|b| b.hp).max();
            if let (Some(a), Some(b)) = (left(0), left(1)) {
                if a != b {
                    self.say(now, Say::Victory { winner: if a > b { 0 } else { 1 } }, None, (0, 0));
                }
            }
        }
        self.standing = Some(buildings);

        // epic monsters
        if let Some(before) = self.monsters.take() {
            if !over && !jumped {
                for m in before.iter().filter(|m| !monsters.iter().any(|n| n.id == m.id)) {
                    step.monsters_died.push(*m);
                }
            }
        }
        self.monsters = Some(monsters);

        self.last = Some((now, champs));
        step
    }

    /// A monster that just died, with the evidence of that tick.
    pub fn pend(&mut self, monster: Monster, at: usize, before: Evidence) {
        self.objectives.push(Pending { monster, at, before });
    }

    /// The monsters whose `DECIDE` ticks have passed.
    pub fn due_objectives(&mut self, now: usize) -> Vec<Pending> {
        let (due, wait): (Vec<_>, Vec<_>) =
            std::mem::take(&mut self.objectives).into_iter().partition(|p| now >= p.at + DECIDE);
        self.objectives = wait;
        due
    }

    /// Who took a monster is decided: its line.
    pub fn objective(&mut self, now: usize, p: &Pending, team: Option<usize>) {
        self.tally.monsters += 1;
        if !self.won {
            self.say(now, Say::Objective { epic: p.monster.epic, team }, None, p.monster.pos);
        }
    }
}

/// The matches seen lately, oldest first (the last `KEEP`).
#[derive(Debug, Default)]
pub struct Book {
    keys: Vec<(Key, Watch)>,
}

impl Book {
    /// The match's record; a new one for a match not seen yet (the oldest is forgotten past `KEEP`).
    pub fn watch(&mut self, key: Key) -> &mut Watch {
        let i = match self.keys.iter().position(|(k, _)| *k == key) {
            Some(i) => i,
            None => {
                if self.keys.len() >= KEEP {
                    self.keys.remove(0);
                }
                self.keys.push((key, Watch::default()));
                self.keys.len() - 1
            }
        };
        &mut self.keys[i].1
    }
}

static BOOK: Mutex<Book> = Mutex::new(Book { keys: Vec::new() });

// ===================== 你是哪一边 =====================

/// The user's team in the match on screen (0 blue, 1 red), as the client extension last read it.
static SIDE: Mutex<Option<usize>> = Mutex::new(None);

/// A side label ("Azubu Frost #4": the name, then the standing) shows the team named `name`.
pub fn label_names(label: &str, name: &str) -> bool {
    let (label, name) = (label.trim(), name.trim());
    if name.is_empty() {
        return false;
    }
    label == name || label.strip_prefix(name).is_some_and(|rest| rest.trim_start().starts_with('#'))
}

/// The user's side from the two labels: only when exactly one names his team.
pub fn side_of(blue: Option<&str>, red: Option<&str>, mine: &str) -> Option<usize> {
    let b = blue.is_some_and(|l| label_names(l, mine));
    let r = red.is_some_and(|l| label_names(l, mine));
    match (b, r) {
        (true, false) => Some(0),
        (false, true) => Some(1),
        _ => None,
    }
}

const LABELS: [(&str, &str); 2] = [
    ("ingame.header.blue_info.team_name", "ingame.header.red_info.team_name"),
    ("main.blue_picks.pick_slot_0.popup.header.team_name", "main.red_picks.pick_slot_0.popup.header.team_name"),
];
const READ_EVERY: Duration = Duration::from_millis(500);

struct Sides {
    last: Mutex<(Option<Instant>, String)>,
}

impl StableExtension for Sides {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        let mut last = self.last.lock().unwrap_or_else(|e| e.into_inner());
        if last.0.is_some_and(|t| t.elapsed() < READ_EVERY) {
            return;
        }
        last.0 = Some(Instant::now());
        let scene = ctx.is_in_game().then(|| ctx.client_scene_kind()).flatten();
        let mut side = None;
        let mut what = format!("scene {scene:?}");
        if matches!(scene, Some(ClientSceneKindV1::InGame | ClientSceneKindV1::Match)) {
            // a default team's name may be an i18n key ("#asset/...")
            let mine = ctx.player_team_id().and_then(|id| ctx.team_name(id)).map(|n| {
                let key = n.strip_prefix('#').map(str::to_string);
                key.and_then(|k| ctx.i18n(&k)).unwrap_or(n)
            });
            let labels = LABELS.iter().find_map(|(b, r)| {
                let (b, r) = (ctx.ui_text(b), ctx.ui_text(r));
                (b.is_some() || r.is_some()).then_some((b, r))
            });
            match (&mine, &labels) {
                (Some(m), Some((b, r))) => {
                    side = side_of(b.as_deref(), r.as_deref(), m);
                    what = format!("you {m:?}, blue {b:?}, red {r:?}");
                }
                _ => {
                    // labels not up this frame: keep what was read
                    if labels.is_none() {
                        return;
                    }
                    what = format!("you {mine:?}, labels {labels:?}");
                }
            }
        }
        let line = match side {
            Some(s) => format!("SIDE you are {} (team {s}): {what}", if s == BLUE { "blue" } else { "red" }),
            None => format!("SIDE not told: {what}"),
        };
        *SIDE.lock().unwrap_or_else(|e| e.into_inner()) = side;
        if line != last.1 {
            wlog(&line);
            last.1 = line;
        }
    }
}

// ===================== 比赛钩子 =====================

/// Every player with a lane, this tick. Dead: the player (waiting to respawn) or his champion entity (the tick it
/// falls); a champion entity is made anew each life, and a player with none for a tick is no death.
fn champs(sim: &StableSim<'_>) -> Vec<Champ> {
    (0..sim.player_count())
        .filter_map(|i| sim.player_at(i))
        .filter_map(|p| {
            let lane = p.lane()?.code();
            let e = p.champion();
            let alive = p.is_alive() && e.as_ref().is_none_or(|e| e.is_alive());
            let (id, pos) = e.map_or((usize::MAX, (0, 0)), |e| (e.id(), e.pos()));
            Some(Champ { player: p.id(), id, team: p.team(), lane, alive, pos })
        })
        .collect()
}

/// The towers, nexuses (with hit points, fallen ones at 0) and live epic monsters.
fn world(sim: &StableSim<'_>) -> (Vec<Building>, Vec<Monster>) {
    let (mut buildings, mut monsters) = (Vec::new(), Vec::new());
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        let kind = e.kind();
        let alive = e.is_alive();
        match kind {
            Some(k @ (EntityKindV1::Tower | EntityKindV1::Nexus)) => {
                let (hp, max) = e.hp();
                let hp = if alive { (hp * 1000 / max.max(1)).max(1) } else { 0 };
                buildings.push(Building { id: e.id(), team: e.team(), nexus: k == EntityKindV1::Nexus, pos: e.pos(), hp });
            }
            Some(k @ (EntityKindV1::Epic | EntityKindV1::Serpen)) if alive => {
                monsters.push(Monster { id: e.id(), epic: k == EntityKindV1::Epic, pos: e.pos() });
            }
            _ => {}
        }
    }
    (buildings, monsters)
}

fn buff_name(b: &BuffV1) -> String {
    String::from_utf8_lossy(&b.name_buf[..b.name_len.min(b.name_buf.len())]).into_owned()
}

/// Gold of each team's players, buffs of each team's champions and minions.
fn evidence(sim: &StableSim<'_>) -> Evidence {
    let mut ev = Evidence::default();
    for p in (0..sim.player_count()).filter_map(|i| sim.player_at(i)) {
        if p.lane().is_some() && p.team() < 2 {
            ev.gold[p.team()].push(p.gold());
        }
    }
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if !matches!(e.kind(), Some(EntityKindV1::Champion | EntityKindV1::Minion)) || !e.is_alive() || e.team() >= 2 {
            continue;
        }
        let mut names: Vec<String> = (0..e.buff_count()).filter_map(|j| e.buff_at(j)).map(|b| buff_name(&b)).collect();
        names.sort();
        names.dedup();
        for n in names {
            *ev.buffs.entry((e.team(), n)).or_default() += 1;
        }
    }
    ev
}

/// Squared distance between two map points.
fn dist2(a: (u64, u64), b: (u64, u64)) -> u64 {
    let (dx, dy) = (a.0.abs_diff(b.0), a.1.abs_diff(b.1));
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

fn head(o: &SimOriginV1) -> String {
    format!("[kind {} m={} s={}]", o.kind, o.match_id, o.set_index)
}

/// Minutes:seconds of a tick.
fn clock(t: usize) -> String {
    format!("{}:{:02}", t / 3600, t / 60 % 60)
}

fn entry(k: &KillLogV1) -> String {
    format!("t={} team {} lane {} -> lane {}", k.tick, k.killer_team, k.killer_position, k.killed_position)
}

fn set_line(o: &SimOriginV1, w: &Watch, why: &str) -> String {
    let t = w.tally;
    format!(
        "SET {} {why}: first run to t={} ({}), {} deaths: {} by champions, {} executed, {} at once; \
         kill log {} entries, {} without a champion killer; {} towers, {} epic monsters; lines {} queued, {} played, \
         {} dropped",
        head(o),
        w.top,
        clock(w.top),
        t.deaths,
        t.by_champions,
        t.executed,
        t.at_once,
        t.entries,
        t.odd,
        t.towers,
        t.monsters,
        t.queued,
        t.played,
        t.dropped
    )
}

/// Plays `name` on `on` if it stands, else on the living champion nearest to `at`, else on any champion.
fn play(sim: &mut StableSim<'_>, name: &str, on: Option<usize>, at: (u64, u64), living: &[(usize, (u64, u64))]) -> String {
    if let Some(e) = on.filter(|&e| sim.get_entity(e).is_some_and(|x| x.is_alive())) {
        if sim.play_sfx(name, e, &InputTargetV1::target(e)) {
            return format!("played on #{e}");
        }
    }
    let nearest = living.iter().min_by_key(|(_, p)| dist2(*p, at)).map(|&(e, _)| e);
    if let Some(e) = nearest {
        if sim.play_sfx(name, e, &InputTargetV1::target(e)) {
            return format!("played on #{e} (nearest)");
        }
    }
    let any = (sim.champion_count() > 0).then(|| sim.champion_id_at(0));
    match any {
        Some(e) if sim.play_sfx(name, e, &InputTargetV1::target(e)) => format!("played on #{e} (any)"),
        _ => format!("NOT played (on {on:?}, nearest {nearest:?})"),
    }
}

struct Announcer;

impl StableMatchHook for Announcer {
    fn on_match_tick(&self, sim: &mut StableSim<'_>, _rng_seed: u64) {
        let o = sim.sim_origin().unwrap_or_default();
        // only the match on screen: the background matches have no origin (kind 0)
        if !matches!(
            SimOriginKindV1::from_code(o.kind),
            Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
        ) {
            return;
        }
        let now = sim.tick();
        let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
        let w = book.watch((o.kind, o.match_id, o.set_index, o.replay_id));
        match w.pass(now) {
            Pass::Live => {}
            Pass::Again { first: true } => {
                let line = if w.summed {
                    format!("AGAIN {} second run from t={now}: ignored", head(&o))
                } else {
                    w.summed = true;
                    set_line(&o, w, &format!("second run from t={now} ignored"))
                };
                drop(book);
                wlog(line);
                return;
            }
            Pass::Again { first: false } => return,
        }
        let champs = champs(sim);
        let living: Vec<(usize, (u64, u64))> =
            champs.iter().filter(|c| c.alive && c.id != usize::MAX).map(|c| (c.id, c.pos)).collect();
        let n = sim.kill_log_count();
        let from = if n < w.read { 0 } else { w.read };
        w.read = n;
        let new_kills: Vec<KillLogV1> = (from..n).filter_map(|i| sim.kill_log_at(i)).collect();
        let over = sim.is_end();
        let (buildings, monsters) = world(sim);
        let step = w.step(now, Frame { champs, new_kills, over, buildings, monsters });
        let mut logs = Vec::new();

        // epic monsters: the evidence when they fall, the decision `DECIDE` ticks later
        if !step.monsters_died.is_empty() {
            let ev = evidence(sim);
            for m in &step.monsters_died {
                w.pend(*m, now, ev.clone());
            }
        }
        let due = w.due_objectives(now);
        if !due.is_empty() {
            let after = evidence(sim);
            for p in &due {
                let nearest = w
                    .last_champs()
                    .iter()
                    .filter(|c| c.alive)
                    .min_by_key(|c| dist2(c.pos, p.monster.pos))
                    .map(|c| c.team);
                let (team, why) = decide(&p.before, &after, nearest);
                logs.push(format!(
                    "OBJECTIVE {} t={} {} #{} died t={} -> {} ({why})",
                    head(&o),
                    clock(now),
                    if p.monster.epic { "Morgard (baron)" } else { "Serpen (dragon)" },
                    p.monster.id,
                    p.at,
                    team.map_or("nobody told".to_string(), |t| format!("team {t}")),
                ));
                w.objective(now, p, team);
            }
        }
        for (&(at, c), near) in step.executed.iter().zip(step.executed.iter().map(|&(at, _)| {
            w.recent.iter().filter(|k| k.tick + WAIT >= at && k.tick <= at + WAIT).map(entry).collect::<Vec<_>>().join(", ")
        })) {
            logs.push(format!(
                "EXECUTED {} t={} #{} (player {} team {} lane {}) died t={at}, kill log then: [{near}]",
                head(&o),
                clock(now),
                c.id,
                c.player,
                c.team,
                c.lane
            ));
        }
        if let Some((Call::Skip, k)) = step.first_blood {
            logs.push(format!("FIRST BLOOD {} t={} kill {}: late, skipped", head(&o), clock(now), entry(&k)));
        }
        if !step.at_once.is_empty() {
            let who: Vec<String> =
                step.at_once.iter().map(|(at, c)| format!("#{} (team {} lane {}) t={at}", c.id, c.team, c.lane)).collect();
            logs.push(format!(
                "AT ONCE {} t={} {} deaths in one tick with no killer, not announced: {}",
                head(&o),
                clock(now),
                who.len(),
                who.join(", ")
            ));
        }
        let (line, stale) = w.queue.next(now);
        w.tally.dropped += stale.len();
        for l in &stale {
            logs.push(format!("DROPPED {} t={} {:?} (waited since t={})", head(&o), clock(now), l.say, l.since));
        }
        if line.is_some() {
            w.tally.played += 1;
        }
        let mut set = None;
        if over && !w.summed && w.queue.lines.is_empty() {
            w.summed = true;
            set = Some(set_line(&o, w, "match over"));
        }
        drop(book);

        if let Some(l) = line {
            let side = *SIDE.lock().unwrap_or_else(|e| e.into_inner());
            let name = sfx(l.say, side);
            let how = play(sim, &name, l.on, l.at, &living);
            logs.push(format!(
                "SAY {} t={} {:?} -> {name} (side {side:?}, queued t={}) {how}",
                head(&o),
                clock(now),
                l.say,
                l.since
            ));
        }
        for line in logs {
            wlog(line);
        }
        if let Some(line) = set {
            wlog(line);
        }
    }
}

impl Watch {
    /// The champions as the last tick saw them.
    pub fn last_champs(&self) -> &[Champ] {
        self.last.as_ref().map_or(&[], |(_, c)| c)
    }
}

// ===================== 注册 =====================

fn init(host: &StableHost) -> StableMod {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!("=== {ID} v{VERSION} loaded: game {}.{}.{} abi {} ===", v.major, v.minor, v.patch, host.abi_level()));
    let mut module = StableMod::new(ID);
    module.set_match_hook(Announcer);
    module.set_extension(Sides { last: Mutex::new((None, String::new())) });
    host.log(LogLevel::Info, "lol_audio loaded (League announcer).");
    module
}

declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    /// Ten champions: players 0-4 on team 0 and 5-9 on team 1, in lanes 0-4; `dead`: the players who are dead.
    fn ten(dead: &[usize]) -> Vec<Champ> {
        (0..10)
            .map(|p| Champ {
                player: p,
                id: 100 + p,
                team: p / 5,
                lane: (p % 5) as u32,
                alive: !dead.contains(&p),
                pos: (1000 * p as u64, 500),
            })
            .collect()
    }

    fn kill(tick: usize, killer_team: usize, killer_lane: u32, victim_lane: u32) -> KillLogV1 {
        let (killer_position, killed_position) = (killer_lane, victim_lane);
        KillLogV1 { tick, killer_team, killer_position, killed_position, ..KillLogV1::default() }
    }

    fn frame(champs: Vec<Champ>, kills: &[KillLogV1]) -> Frame {
        Frame { champs, new_kills: kills.to_vec(), ..Frame::default() }
    }

    /// Every line the queue holds now (without waiting for their turn).
    fn queued(w: &Watch) -> Vec<Say> {
        w.queue.lines.iter().map(|l| l.say).collect()
    }

    /// Player 3 (team 0, lane 3), dead from tick 101 on.
    fn three() -> Champ {
        ten(&[3])[3]
    }

    /// Ticks `from..=to` with player 3 dying at 101 and the entries `kills` landing on their own ticks: the executed.
    fn dies_at_101(kills: &[KillLogV1], from: usize, to: usize) -> (Vec<(usize, Champ)>, Tally) {
        let mut w = Watch::default();
        let mut out = Vec::new();
        for t in from..=to {
            let dead: &[usize] = if t >= 101 { &[3] } else { &[] };
            let new: Vec<KillLogV1> = kills.iter().filter(|k| k.tick == t).copied().collect();
            out.extend(w.step(t, frame(ten(dead), &new)).executed);
        }
        (out, w.tally)
    }

    #[test]
    fn the_second_run_is_ignored_entirely() {
        let mut w = Watch::default();
        for t in 0..=500 {
            assert_eq!(w.pass(t), Pass::Live);
        }
        assert_eq!(w.pass(500), Pass::Live);
        assert_eq!(w.pass(0), Pass::Again { first: true });
        for t in 1..=900 {
            assert_eq!(w.pass(t), Pass::Again { first: false });
        }
    }

    #[test]
    fn first_blood_plays_once_a_match() {
        let mut w = Watch::default();
        assert_eq!(w.step(100, frame(ten(&[]), &[])).first_blood, None);
        let fb = kill(500, 1, 0, 0);
        assert_eq!(w.step(500, frame(ten(&[0]), &[fb])).first_blood, Some((Call::Play, fb)));
        assert_eq!(w.step(501, frame(ten(&[0]), &[])).first_blood, None);
        assert_eq!(w.step(900, frame(ten(&[0, 7]), &[kill(900, 0, 2, 2)])).first_blood, None);
        assert_eq!(queued(&w), [Say::FirstBlood]);
    }

    #[test]
    fn a_first_blood_seen_late_stays_quiet() {
        let fb = kill(500, 1, 0, 0);
        let mut w = Watch::default();
        let first = w.step(500 + FRESH + 1, frame(ten(&[]), &[fb, kill(520, 0, 1, 1)])).first_blood;
        assert_eq!(first, Some((Call::Skip, fb)));
        assert!(queued(&w).is_empty());
    }

    #[test]
    fn first_blood_is_a_champion_kill() {
        let mut w = Watch::default();
        assert_eq!(w.step(400, frame(ten(&[]), &[kill(400, 1, 7, 0)])).first_blood, None);
        assert_eq!(w.step(401, frame(ten(&[]), &[kill(401, 2, 0, 0)])).first_blood, None);
        let fb = kill(500, 1, 0, 0);
        assert_eq!(w.step(500, frame(ten(&[]), &[fb])).first_blood, Some((Call::Play, fb)));
        assert_eq!((w.tally.entries, w.tally.odd), (3, 2));
    }

    #[test]
    fn a_death_with_no_champion_kill_is_executed_once_after_wait() {
        let mut w = Watch::default();
        assert_eq!(w.step(100, frame(ten(&[]), &[])), Step::default());
        assert_eq!(w.step(101, frame(ten(&[3]), &[])), Step::default());
        assert_eq!(w.step(101 + WAIT - 1, frame(ten(&[3]), &[])), Step::default());
        assert_eq!(w.step(101 + WAIT, frame(ten(&[3]), &[])).executed, [(101, three())]);
        assert_eq!(w.step(101 + WAIT + 1, frame(ten(&[3]), &[])), Step::default());
        assert_eq!((w.tally.deaths, w.tally.executed), (1, 1));
        assert_eq!(queued(&w), [Say::Executed]);
    }

    #[test]
    fn a_champion_kill_near_the_death_is_no_execution() {
        for at in 101 - WAIT..=101 + WAIT {
            let (executed, tally) = dies_at_101(&[kill(at, 1, 2, 3)], 95, 110);
            assert!(executed.is_empty(), "entry at {at}");
            assert_eq!((tally.deaths, tally.by_champions, tally.executed), (1, 1, 0), "entry at {at}");
        }
    }

    #[test]
    fn entries_that_are_not_his_champion_kill() {
        for (why, k) in [
            ("too late", kill(101 + WAIT + 1, 1, 2, 3)),
            ("too early", kill(101 - WAIT - 1, 1, 2, 3)),
            ("lane 3 of the other team", kill(101, 0, 2, 3)),
            ("someone else", kill(101, 1, 2, 4)),
            ("no player in the killer's lane", kill(101, 1, 7, 3)),
            ("no player on the killer's team", kill(101, 2, 0, 3)),
        ] {
            let (executed, _) = dies_at_101(&[k], 95, 110);
            assert_eq!(executed, [(101, three())], "{why}");
        }
    }

    #[test]
    fn many_deaths_in_one_tick_with_no_killer_are_not_executions() {
        let mut w = Watch::default();
        w.step(100, frame(ten(&[]), &[]));
        w.step(101, frame(ten(&[1, 2, 3]), &[]));
        w.step(102, frame(ten(&[1, 2, 3]), &[]));
        let s = w.step(101 + WAIT, frame(ten(&[1, 2, 3]), &[]));
        assert!(s.executed.is_empty());
        assert_eq!(s.at_once.len(), MASS);
    }

    #[test]
    fn no_deaths_across_a_jump_or_after_the_end() {
        let mut w = Watch::default();
        w.step(100, frame(ten(&[]), &[]));
        for t in 101 + JUMP..=110 + JUMP {
            assert_eq!(w.step(t, frame(ten(&[3]), &[])), Step::default());
        }
        let mut w = Watch::default();
        w.step(100, frame(ten(&[]), &[]));
        for t in 101..=110 {
            w.step(t, Frame { over: true, ..frame(ten(&[3]), &[]) });
        }
        assert_eq!(w.tally.deaths, 0);
    }

    #[test]
    fn a_death_is_the_life_that_ended() {
        let before = ten(&[]);
        let mut now = ten(&[3]);
        (now[3].id, now[3].pos) = (usize::MAX, (0, 0));
        assert_eq!(died(&before, &now), [Champ { alive: false, ..before[3] }]);
        let mut back = ten(&[]);
        back[3].id = 999;
        assert!(died(&now, &back).is_empty());
    }

    /// Team 1's mid (player 7) kills team 0's lanes `victims` at the ticks given; returns the lines queued.
    fn mid_kills(kills: &[(usize, u32)]) -> Vec<Say> {
        let mut w = Watch::default();
        w.step(1, frame(ten(&[]), &[]));
        let mut dead = Vec::new();
        for &(t, lane) in kills {
            dead.push(lane as usize);
            w.step(t, frame(ten(&dead), &[kill(t, 1, 2, lane)]));
        }
        queued(&w)
    }

    #[test]
    fn sprees_from_the_third_kill_in_a_life() {
        let lines = mid_kills(&[(1000, 0), (3000, 1), (5000, 2), (7000, 3), (9000, 4)]);
        assert_eq!(
            lines,
            [
                Say::FirstBlood,
                Say::Spree { kills: 3, team: 1 },
                Say::Spree { kills: 4, team: 1 },
                Say::Spree { kills: 5, team: 1 },
            ]
        );
    }

    #[test]
    fn a_kill_in_a_multi_kill_says_no_spree() {
        // kills 2 and 3 within MULTI: the game's double kill; the 4th alone again
        let lines = mid_kills(&[(1000, 0), (3000, 1), (3000 + MULTI - 1, 2), (9000, 3)]);
        assert_eq!(lines, [Say::FirstBlood, Say::Spree { kills: 4, team: 1 }]);
    }

    #[test]
    fn legendary_repeats_from_the_eighth_kill() {
        assert_eq!(sfx(Say::Spree { kills: 8, team: 0 }, None), "lol_audio_legendary");
        assert_eq!(sfx(Say::Spree { kills: 12, team: 0 }, None), "lol_audio_legendary");
        assert_eq!(sfx(Say::Spree { kills: 3, team: 0 }, None), "lol_audio_killing_spree");
        assert_eq!(sfx(Say::Spree { kills: 7, team: 1 }, Some(0)), "lol_audio_godlike_enemy");
        assert_eq!(sfx(Say::Spree { kills: 7, team: 1 }, Some(1)), "lol_audio_godlike");
    }

    #[test]
    fn killing_a_spree_is_a_shutdown_and_ends_it() {
        let mut w = Watch::default();
        w.step(1, frame(ten(&[]), &[]));
        for (i, t) in [1000, 3000, 5000].into_iter().enumerate() {
            w.step(t, frame(ten(&[i]), &[kill(t, 1, 2, i as u32)]));
        }
        // team 0's mid kills team 1's mid (lane 2)
        w.step(7000, frame(ten(&[0, 1, 2, 7]), &[kill(7000, 0, 2, 2)]));
        assert_eq!(queued(&w).last(), Some(&Say::Shutdown));
        // his streak is gone: a kill by him later is his first
        w.step(9000, frame(ten(&[0, 1, 2]), &[kill(9000, 1, 2, 3)]));
        assert_eq!(queued(&w).iter().filter(|s| matches!(s, Say::Spree { .. })).count(), 1);
    }

    #[test]
    fn an_execution_ends_a_streak_without_a_shutdown() {
        let mut w = Watch::default();
        w.step(1, frame(ten(&[]), &[]));
        for (i, t) in [1000, 3000, 5000].into_iter().enumerate() {
            w.step(t, frame(ten(&[i]), &[kill(t, 1, 2, i as u32)]));
        }
        // player 7 dies to a tower (the tick before seen: no jump)
        w.step(6999, frame(ten(&[0, 1, 2]), &[]));
        for t in 7000..=7000 + WAIT {
            w.step(t, frame(ten(&[0, 1, 2, 7]), &[]));
        }
        assert_eq!(queued(&w).last(), Some(&Say::Executed));
        assert!(!queued(&w).contains(&Say::Shutdown));
        assert!(!w.streak.contains_key(&(1, 2)));
    }

    #[test]
    fn a_team_wiped_is_an_ace_once() {
        let mut w = Watch::default();
        w.step(1, frame(ten(&[]), &[]));
        w.step(2, frame(ten(&[0, 1, 2, 3]), &[]));
        w.step(3, frame(ten(&[0, 1, 2, 3, 4]), &[]));
        w.step(4, frame(ten(&[0, 1, 2, 3, 4]), &[]));
        assert_eq!(queued(&w).iter().filter(|s| **s == Say::Ace).count(), 1);
        // one back, all down again: another ace
        w.step(5, frame(ten(&[0, 1, 2, 3]), &[]));
        w.step(6, frame(ten(&[0, 1, 2, 3, 4]), &[]));
        assert_eq!(queued(&w).iter().filter(|s| **s == Say::Ace).count(), 2);
        // dead from the first look: no ace
        let mut w = Watch::default();
        w.step(1, frame(ten(&[5, 6, 7, 8, 9]), &[]));
        w.step(2, frame(ten(&[5, 6, 7, 8, 9]), &[]));
        assert!(!queued(&w).contains(&Say::Ace));
    }

    fn tower(id: usize, team: usize, hp: usize) -> Building {
        Building { id, team, nexus: false, pos: (id as u64, 0), hp }
    }

    fn nexus(id: usize, team: usize, hp: usize) -> Building {
        Building { nexus: true, ..tower(id, team, hp) }
    }

    #[test]
    fn a_fallen_tower_and_nexus() {
        let mut w = Watch::default();
        let all = vec![tower(1, 0, 1000), tower(2, 1, 500), nexus(3, 1, 1000), nexus(4, 0, 1000)];
        w.step(1, Frame { buildings: all.clone(), ..frame(ten(&[]), &[]) });
        // tower 2 (team 1) gone from the list, tower 1 at 0 hp
        let next = vec![tower(1, 0, 0), nexus(3, 1, 1000), nexus(4, 0, 1000)];
        w.step(2, Frame { buildings: next.clone(), ..frame(ten(&[]), &[]) });
        assert_eq!(queued(&w), [Say::Turret { owner: 0 }, Say::Turret { owner: 1 }]);
        w.step(3, Frame { buildings: next, ..frame(ten(&[]), &[]) });
        assert_eq!(w.tally.towers, 2);
        // team 1's nexus falls: team 0 wins, the rest is cleared
        let end = vec![tower(1, 0, 0), nexus(3, 1, 0), nexus(4, 0, 1000)];
        w.step(4, Frame { buildings: end.clone(), over: true, ..frame(ten(&[]), &[]) });
        assert_eq!(queued(&w), [Say::Victory { winner: 0 }]);
        w.step(5, Frame { buildings: end, over: true, ..frame(ten(&[]), &[]) });
        assert_eq!(queued(&w).len(), 1);
    }

    #[test]
    fn an_end_without_a_nexus_seen_falling_goes_to_the_fuller_nexus() {
        let mut w = Watch::default();
        w.step(1, Frame { buildings: vec![nexus(3, 1, 400), nexus(4, 0, 900)], ..frame(ten(&[]), &[]) });
        w.step(2, Frame { buildings: vec![nexus(3, 1, 400), nexus(4, 0, 900)], over: true, ..frame(ten(&[]), &[]) });
        assert_eq!(queued(&w), [Say::Victory { winner: 0 }]);
    }

    #[test]
    fn a_monster_that_dies_waits_for_who_took_it() {
        let mut w = Watch::default();
        let m = Monster { id: 50, epic: true, pos: (5, 5) };
        w.step(1, Frame { monsters: vec![m], ..frame(ten(&[]), &[]) });
        let s = w.step(2, frame(ten(&[]), &[]));
        assert_eq!(s.monsters_died, [m]);
        w.pend(m, 2, Evidence::default());
        assert!(w.due_objectives(2 + DECIDE - 1).is_empty());
        let due = w.due_objectives(2 + DECIDE);
        assert_eq!(due.len(), 1);
        w.objective(2 + DECIDE, &due[0], Some(1));
        assert_eq!(queued(&w), [Say::Objective { epic: true, team: Some(1) }]);
    }

    fn ev(gold: [&[usize]; 2], buffs: &[(usize, &str, usize)]) -> Evidence {
        Evidence {
            gold: [gold[0].to_vec(), gold[1].to_vec()],
            buffs: buffs.iter().map(|(t, n, c)| ((*t, n.to_string()), *c)).collect(),
        }
    }

    #[test]
    fn who_took_it_by_buff_then_gold_then_nearest() {
        let before = ev([&[100; 5], &[100; 5]], &[(0, "shield", 1)]);
        // a buff new on three of team 1's
        let (t, why) = decide(&before, &ev([&[110; 5], &[110; 5]], &[(1, "serpen_buff", 3), (0, "shield", 1)]), Some(0));
        assert_eq!(t, Some(1), "{why}");
        // a buff on one only does not count; team 0's gold went up 150 more
        let (t, why) = decide(&before, &ev([&[260; 5], &[110; 5]], &[(1, "w", 1)]), Some(1));
        assert_eq!(t, Some(0), "{why}");
        // nothing tells: the nearest champion's team
        let (t, why) = decide(&before, &ev([&[110; 5], &[110; 5]], &[]), Some(1));
        assert_eq!((t, why.starts_with("nearest")), (Some(1), true));
        assert_eq!(decide(&before, &before, None).0, None);
    }

    #[test]
    fn the_lines_by_side() {
        assert_eq!(sfx(Say::Turret { owner: 0 }, Some(0)), "lol_audio_turret_ours");
        assert_eq!(sfx(Say::Turret { owner: 1 }, Some(0)), "lol_audio_turret_theirs");
        assert_eq!(sfx(Say::Turret { owner: 1 }, None), "lol_audio_turret");
        assert_eq!(sfx(Say::Victory { winner: 1 }, Some(1)), "lol_audio_victory");
        assert_eq!(sfx(Say::Victory { winner: 1 }, Some(0)), "lol_audio_defeat");
        assert_eq!(sfx(Say::Victory { winner: 1 }, None), "lol_audio_victory_red");
        assert_eq!(sfx(Say::Objective { epic: false, team: Some(0) }, Some(1)), "lol_audio_dragon_blue");
        assert_eq!(sfx(Say::Objective { epic: true, team: None }, None), "lol_audio_baron");
    }

    #[test]
    fn lines_play_one_at_a_time_and_go_stale() {
        let mut q = Queue::default();
        let l = |say, since| Line { say, on: None, at: (0, 0), since };
        q.push(l(Say::FirstBlood, 10));
        q.push(l(Say::Ace, 10));
        q.push(l(Say::Shutdown, 10));
        assert_eq!(q.next(10).0.map(|l| l.say), Some(Say::FirstBlood));
        assert_eq!(q.next(10 + GAP - 1).0, None);
        assert_eq!(q.next(10 + GAP).0.map(|l| l.say), Some(Say::Ace));
        // the shutdown waited too long
        let (next, stale) = q.next(10 + EXPIRE + 1);
        assert_eq!((next, stale.len()), (None, 1));
        // the result goes first and alone
        q.push(l(Say::Ace, 1000));
        q.push(l(Say::Victory { winner: 0 }, 1000));
        assert_eq!(q.next(1000).0.map(|l| l.say), Some(Say::Victory { winner: 0 }));
        assert_eq!(q.next(5000), (None, vec![]));
    }

    #[test]
    fn the_side_labels() {
        assert!(label_names("Azubu Frost #4", "Azubu Frost"));
        assert!(label_names("Azubu Frost", "Azubu Frost"));
        assert!(!label_names("Azubu Frost Blue #4", "Azubu Frost"));
        assert!(!label_names("Azubu", "Azubu Frost"));
        assert!(!label_names("X #1", ""));
        assert_eq!(side_of(Some("A #1"), Some("B #2"), "B"), Some(1));
        assert_eq!(side_of(Some("A #1"), Some("B #2"), "A"), Some(0));
        assert_eq!(side_of(Some("A #1"), Some("B #2"), "C"), None);
        assert_eq!(side_of(Some("A"), Some("A"), "A"), None);
        assert_eq!(side_of(None, Some("A"), "A"), Some(1));
    }

    #[test]
    fn matches_are_apart() {
        let mut b = Book::default();
        let (set1, set2) = ((2, 7, 1, u64::MAX), (2, 7, 2, u64::MAX));
        assert_eq!(b.watch(set1).pass(5000), Pass::Live);
        assert_eq!(b.watch(set2).pass(0), Pass::Live);
        assert_eq!(b.watch(set1).pass(0), Pass::Again { first: true });
        assert_eq!(b.watch(set2).pass(1), Pass::Live);
    }

    #[test]
    fn the_book_forgets_the_oldest_match() {
        let mut b = Book::default();
        for m in 0..=KEEP as u64 {
            b.watch((2, m, 1, 0)).pass(1000);
        }
        assert_eq!(b.keys.len(), KEEP);
        assert_eq!(b.watch((2, 0, 1, 0)).pass(0), Pass::Live);
        assert_eq!(b.watch((2, 2, 1, 0)).pass(0), Pass::Again { first: true });
    }
}
