//! 英雄联盟音效（用户 2026-10-30：「游戏内BP界面的音乐 还有对局内的音乐 一血 双杀 三杀 四杀 五杀都能改成和英雄联盟一样的吗
//! 单独做个启动mod」）。
//!
//! BP 音乐、对局里的声音、双杀到五杀都是数据：`mod.override_info` 把游戏自己的 `sound/bgm/*` 和四个连杀音效
//! （dual_takedown / triple_takedown / devastation / annihilation，就是 kill2..kill5 的横幅）换成 `build_audio.py`
//! 从本机英雄联盟客户端取出的音频。游戏没有的两句播报由这个 DLL 的比赛钩子每 tick 看着放：
//!
//! - **一血**：一局里第一条英雄击杀（击杀记录里凶手是一名玩家的英雄，死的是对面的英雄）出现时，在凶手身上放
//!   `lol_audio_first_blood`（sound/sfx/lol_audio_first_blood.sound_info）。塔、小兵、野怪杀的不算一血（英雄联盟一样）；
//!   打开时第一滴血已经过去 `FRESH` tick 以上的（中途观战）不补放。
//! - **被处决**（0.1.3，用户 2026-11-02：「还有被塔杀没有音效 我发现了 可以补一补」）：英雄联盟里英雄死于防御塔、小兵、
//!   野怪时播报「被处决」（sound/sfx/lol_audio_executed.sound_info）。不知道塔杀进不进击杀记录、记成谁，所以直接看死活：
//!   每 tick 和上一 tick 比各玩家的死活（玩家在等复活，或他这条命的英雄实体倒下；英雄实体每条命换一个新的），刚死的人
//!   在死前死后 `WAIT` tick 的击杀记录里找不到一条杀的是他（他那一队、他的分路）、凶手又是对面一名玩家的英雄的，就是
//!   被处决，在他（这条命的实体）身上放 `lol_audio_executed`，游戏不肯放就放在离他倒下的地方最近的活着的英雄身上。
//!   同一 tick `MASS` 个以上没有凶手的阵亡不播（不像被处决，像比赛在收尾）；比赛结束（`is_end`）以后、两 tick 之间
//!   跳过 `JUMP` 以上（回放快进）时不算新的阵亡。
//!
//! 只在看得见、听得见的比赛里放（观看、观战、回放）；后台预演的比赛（`ServerPresim`）和别的队伍在后台打的比赛
//! （0.7.0 里没有来历，kind 0）跳过。游戏把屏幕上的每一局用同一个来历（来历 + 比赛 + 第几局 + 回放）跑两遍：第一遍是屏幕
//! 上的，第二遍在这一局快结束时从 0 tick 再快跑一遍（0.1.2 两遍都放，一血听到两次）。所以每个来历记下见过的最大 tick，
//! tick 一比它小就是第二遍，这一遍整个不管：不放一血，也不放被处决（回放倒回去也算第二遍，倒回去以后不出声）。
//! 记最近 `KEEP` 局。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\lol_audio.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `FIRST BLOOD ... played`、`EXECUTED ... played`（带上死前死后的击杀记录）；每局一行 `SET`（比赛结束或第二遍开始时，
//! 先到的那次）：阵亡几次、几次是英雄杀的、几次被处决，击杀记录几条、几条的凶手不是玩家的英雄（塔杀进不进击杀记录
//! 看这个数）；`SET` 写在比赛结束时的，第二遍开始再写一行 `AGAIN`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "lol_audio";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// The first-blood announcer line (sound/sfx/lol_audio_first_blood.sound_info).
const SFX_FIRST_BLOOD: &str = "lol_audio_first_blood";
/// The executed announcer line (sound/sfx/lol_audio_executed.sound_info).
const SFX_EXECUTED: &str = "lol_audio_executed";
/// A first kill older than this when the view first sees it is not announced (spectating or a replay opened mid-match).
pub const FRESH: usize = 30;
/// A kill-log entry this many ticks before or after a death can be that death's; a death waits this long for it (0.1 s:
/// the entry is seen in the death's own tick in the 11-01 logs, the margin keeps a late one from reading as an execution).
pub const WAIT: usize = 6;
/// This many deaths in one tick with no killer are not executions (a match being wound up): not announced.
pub const MASS: usize = 3;
/// A gap of more ticks than this between two calls (a replay skipped ahead): no deaths are taken across it.
pub const JUMP: usize = 30;
/// How long (ticks) kill-log entries are kept for the deaths waiting on them.
const RECENT: usize = 60;
/// How many matches are remembered.
const KEEP: usize = 64;
const LOG_CAP: usize = 2_000;

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
static START: LazyLock<std::time::Instant> = LazyLock::new(std::time::Instant::now);

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

// ===================== 一血、被处决 =====================

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

/// A kill-log entry made by one player's champion on a champion of the other team: not a tower's, a minion's or a
/// monster's, should the game log those. `champs`: every player.
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
}

/// What one tick of the first run brings.
#[derive(Debug, Default, PartialEq, Eq)]
pub struct Step {
    /// The first blood, on the tick it shows up.
    pub first_blood: Option<(Call, KillLogV1)>,
    /// Executed champions, (tick of death, champion): announce them.
    pub executed: Vec<(usize, Champ)>,
    /// Deaths with no killer, too many in one tick to be executions: not announced.
    pub at_once: Vec<(usize, Champ)>,
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
    read: usize,
    /// The kill-log entries of the last `RECENT` ticks, for the deaths waiting on them.
    recent: Vec<KillLogV1>,
    /// The champions on the last tick, and that tick.
    last: Option<(usize, Vec<Champ>)>,
    /// Deaths waiting `WAIT` ticks for their kill-log entry: (tick of death, champion).
    pending: Vec<(usize, Champ)>,
    tally: Tally,
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

    /// One tick of the first run. `champs`: every player's champion now (the players with a lane); `new_kills`: the
    /// kill-log entries added since the last tick; `over`: the match has ended.
    pub fn step(&mut self, now: usize, champs: Vec<Champ>, new_kills: &[KillLogV1], over: bool) -> Step {
        let mut step = Step::default();
        self.tally.entries += new_kills.len();
        self.tally.odd += new_kills.iter().filter(|k| !by_champion(k, &champs)).count();
        self.recent.extend_from_slice(new_kills);
        self.recent.retain(|k| k.tick + RECENT >= now);
        // first blood: the first champion kill, once a match
        if !self.first_blood {
            if let Some(k) = new_kills.iter().find(|k| by_champion(k, &champs)) {
                self.first_blood = true;
                let call = if now.saturating_sub(k.tick) <= FRESH { Call::Play } else { Call::Skip };
                step.first_blood = Some((call, *k));
            }
        }
        // deaths: alive on the last tick, dead now (none after the end, none across a jump)
        if let Some((then, before)) = &self.last {
            if !over && now <= then + JUMP {
                for c in died(before, &champs) {
                    self.tally.deaths += 1;
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
            if lone.iter().filter(|(t, _)| *t == at).count() >= MASS {
                self.tally.at_once += 1;
                step.at_once.push((at, c));
            } else {
                self.tally.executed += 1;
                step.executed.push((at, c));
            }
        }
        self.last = Some((now, champs));
        step
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

// ===================== 比赛钩子 =====================

/// The killer's champion (kill-log positions are lanes), else any champion: the entity the first blood plays on.
fn source(sim: &StableSim<'_>, k: &KillLogV1) -> Option<usize> {
    let killer = (0..sim.player_count())
        .filter_map(|i| sim.player_at(i))
        .find(|p| p.team() == k.killer_team && p.lane().map(|l| l.code()) == Some(k.killer_position))
        .and_then(|p| p.champion())
        .map(|e| e.id());
    killer.or_else(|| (sim.champion_count() > 0).then(|| sim.champion_id_at(0)))
}

/// Every player with a lane, this tick. Dead: the player (waiting to respawn) or his champion entity (the tick it
/// falls); a champion entity is made anew each life (Cho'Gath #18 -> #825 in the 11-01 logs), and a player with none
/// for a tick is no death.
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
         kill log {} entries, {} without a champion killer",
        head(o),
        w.top,
        clock(w.top),
        t.deaths,
        t.by_champions,
        t.executed,
        t.at_once,
        t.entries,
        t.odd
    )
}

struct Announcer;

impl StableMatchHook for Announcer {
    fn on_match_tick(&self, sim: &mut StableSim<'_>, _rng_seed: u64) {
        let o = sim.sim_origin().unwrap_or_default();
        // only the match on screen: the background matches have no origin (kind 0) in game 0.7.0
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
        let step = w.step(now, champs, &new_kills, over);
        let near: Vec<String> = step
            .executed
            .iter()
            .map(|&(at, _)| {
                let near = w.recent.iter().filter(|k| k.tick + WAIT >= at && k.tick <= at + WAIT);
                near.map(entry).collect::<Vec<_>>().join(", ")
            })
            .collect();
        let mut set = None;
        if over && !w.summed {
            w.summed = true;
            set = Some(set_line(&o, w, "match over"));
        }
        drop(book);

        if let Some((call, k)) = step.first_blood {
            let at = source(sim, &k);
            let played = call == Call::Play
                && at.is_some_and(|e| sim.play_sfx(SFX_FIRST_BLOOD, e, &InputTargetV1::target(e)));
            wlog(format!(
                "FIRST BLOOD {} t={} kill t={} team {} lane {} -> {}",
                head(&o),
                clock(now),
                k.tick,
                k.killer_team,
                k.killer_position,
                match (call, played) {
                    (Call::Play, true) => "played".to_string(),
                    (Call::Play, false) => format!("NOT played (entity {at:?})"),
                    (Call::Skip, _) => "late, skipped".to_string(),
                }
            ));
        }
        for (&(at, c), near) in step.executed.iter().zip(&near) {
            // on him (the entity of the life that just ended, while it is still there); if the game will not play it
            // there, on the living champion nearest to where he fell
            let on_him = sim.get_entity(c.id).is_some()
                && sim.play_sfx(SFX_EXECUTED, c.id, &InputTargetV1::target(c.id));
            let nearest = living.iter().min_by_key(|(_, p)| dist2(*p, c.pos)).map(|&(e, _)| e);
            let other = if on_him {
                None
            } else {
                nearest.filter(|&e| sim.play_sfx(SFX_EXECUTED, e, &InputTargetV1::target(e)))
            };
            let name = sim
                .get_entity(c.id)
                .or_else(|| sim.get_player(c.player).and_then(|p| p.champion()))
                .and_then(|e| e.name())
                .unwrap_or_else(|| "?".to_string());
            wlog(format!(
                "EXECUTED {} t={} {name}#{} (player {} team {} lane {}) died t={at}, kill log then: [{near}] -> {}",
                head(&o),
                clock(now),
                c.id,
                c.player,
                c.team,
                c.lane,
                match (on_him, other) {
                    (true, _) => "played".to_string(),
                    (false, Some(e)) => format!("played on #{e} near him (not on him)"),
                    (false, None) => format!("NOT played (nearest {nearest:?})"),
                }
            ));
        }
        if !step.at_once.is_empty() {
            let who: Vec<String> = step
                .at_once
                .iter()
                .map(|(at, c)| format!("#{} (team {} lane {}) t={at}", c.id, c.team, c.lane))
                .collect();
            wlog(format!(
                "AT ONCE {} t={} {} deaths in one tick with no killer, not announced: {}",
                head(&o),
                clock(now),
                who.len(),
                who.join(", ")
            ));
        }
        if let Some(line) = set {
            wlog(line);
        }
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
    host.log(LogLevel::Info, "lol_audio loaded (first blood and executed announcer).");
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
            out.extend(w.step(t, ten(dead), &new, false).executed);
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
        // even where it runs past the first run's last tick
        for t in 1..=900 {
            assert_eq!(w.pass(t), Pass::Again { first: false });
        }
    }

    #[test]
    fn the_second_run_announces_nothing() {
        let mut w = Watch::default();
        let fb = kill(500, 1, 0, 0);
        let mut heard = Vec::new();
        for run in 0..2 {
            for t in 0..=600 {
                if w.pass(t) != Pass::Live {
                    continue;
                }
                // player 3 dies to a tower at 300 and is back at 400; player 0 is first blood at 500
                let dead: Vec<usize> = [(3, 300..400), (0, 500..601)]
                    .into_iter()
                    .filter(|(_, ticks)| ticks.contains(&t))
                    .map(|(p, _)| p)
                    .collect();
                let new: Vec<KillLogV1> = if t == fb.tick { vec![fb] } else { vec![] };
                let s = w.step(t, ten(&dead), &new, false);
                heard.extend(s.first_blood.map(|(c, k)| format!("run {run}: first blood {c:?} t={}", k.tick)));
                for (at, c) in &s.executed {
                    heard.push(format!("run {run}: executed player {} t={at}", c.player));
                }
            }
        }
        assert_eq!(heard, ["run 0: executed player 3 t=300", "run 0: first blood Play t=500"]);
    }

    #[test]
    fn first_blood_plays_once_a_match() {
        let mut w = Watch::default();
        assert_eq!(w.step(100, ten(&[]), &[], false).first_blood, None);
        let fb = kill(500, 1, 0, 0);
        assert_eq!(w.step(500, ten(&[0]), &[fb], false).first_blood, Some((Call::Play, fb)));
        assert_eq!(w.step(501, ten(&[0]), &[], false).first_blood, None);
        assert_eq!(w.step(900, ten(&[0, 7]), &[kill(900, 0, 2, 2)], false).first_blood, None);
    }

    #[test]
    fn a_first_blood_seen_late_stays_quiet() {
        let fb = kill(500, 1, 0, 0);
        let mut w = Watch::default();
        let first = w.step(500 + FRESH + 1, ten(&[]), &[fb, kill(520, 0, 1, 1)], false).first_blood;
        assert_eq!(first, Some((Call::Skip, fb)));
        assert_eq!(w.step(2000, ten(&[]), &[kill(2000, 1, 2, 2)], false).first_blood, None);
        let mut w = Watch::default();
        assert_eq!(w.step(500 + FRESH, ten(&[]), &[fb], false).first_blood, Some((Call::Play, fb)));
    }

    #[test]
    fn first_blood_is_a_champion_kill() {
        let mut w = Watch::default();
        // a tower's kill, should the game log one: no player in the killer's lane, or no player on the killer's team
        assert_eq!(w.step(400, ten(&[]), &[kill(400, 1, 7, 0)], false).first_blood, None);
        assert_eq!(w.step(401, ten(&[]), &[kill(401, 2, 0, 0)], false).first_blood, None);
        let fb = kill(500, 1, 0, 0);
        assert_eq!(w.step(500, ten(&[]), &[fb], false).first_blood, Some((Call::Play, fb)));
        assert_eq!((w.tally.entries, w.tally.odd), (3, 2));
    }

    #[test]
    fn a_death_with_no_champion_kill_is_executed_once_after_wait() {
        let mut w = Watch::default();
        assert_eq!(w.step(100, ten(&[]), &[], false), Step::default()); // the first tick: only looked at
        assert_eq!(w.step(101, ten(&[3]), &[], false), Step::default()); // died: waits for a kill-log entry
        assert_eq!(w.step(101 + WAIT - 1, ten(&[3]), &[], false), Step::default());
        assert_eq!(w.step(101 + WAIT, ten(&[3]), &[], false).executed, [(101, three())]);
        assert_eq!(w.step(101 + WAIT + 1, ten(&[3]), &[], false), Step::default());
        assert_eq!((w.tally.deaths, w.tally.executed), (1, 1));
    }

    #[test]
    fn a_champion_kill_near_the_death_is_no_execution() {
        for at in 101 - WAIT..=101 + WAIT {
            // player 3 (team 0, lane 3) killed by team 1's mid
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
        w.step(100, ten(&[]), &[], false);
        w.step(101, ten(&[1, 2, 3]), &[], false);
        w.step(102, ten(&[1, 2, 3]), &[], false);
        let s = w.step(101 + WAIT, ten(&[1, 2, 3]), &[], false);
        assert!(s.executed.is_empty());
        assert_eq!(s.at_once.len(), MASS);
        // two at once with no killer, and a third killed by a champion: the two are executed
        let mut w = Watch::default();
        w.step(100, ten(&[]), &[], false);
        w.step(101, ten(&[1, 6, 3]), &[kill(101, 1, 2, 3)], false);
        w.step(102, ten(&[1, 6, 3]), &[], false);
        let s = w.step(101 + WAIT, ten(&[1, 6, 3]), &[], false);
        assert_eq!(s.executed.iter().map(|(_, c)| c.player).collect::<Vec<_>>(), [1, 6]);
        assert!(s.at_once.is_empty());
    }

    #[test]
    fn no_deaths_across_a_jump_or_after_the_end() {
        let mut w = Watch::default();
        w.step(100, ten(&[]), &[], false);
        for t in 101 + JUMP..=110 + JUMP {
            assert_eq!(w.step(t, ten(&[3]), &[], false), Step::default());
        }
        let mut w = Watch::default();
        w.step(100, ten(&[]), &[], false);
        for t in 101..=110 {
            assert_eq!(w.step(t, ten(&[3]), &[], true), Step::default());
        }
        assert_eq!(w.tally.deaths, 0);
    }

    #[test]
    fn dead_from_the_first_look_is_no_death_and_each_life_ends_once() {
        let mut w = Watch::default();
        let mut out = Vec::new();
        // dead when first seen, back at 110, dies at 120 and 140 (back at 130)
        for t in 100..=150 {
            let dead: &[usize] = if t < 110 || (120..130).contains(&t) || t >= 140 { &[3] } else { &[] };
            out.extend(w.step(t, ten(dead), &[], false).executed);
        }
        assert_eq!(out, [(120, three()), (140, three())]);
    }

    #[test]
    fn a_death_is_the_life_that_ended() {
        // a champion entity is made anew each life and a dead player may have none: the death keeps the last living
        // entity and place
        let before = ten(&[]);
        let mut now = ten(&[3]);
        (now[3].id, now[3].pos) = (usize::MAX, (0, 0));
        assert_eq!(died(&before, &now), [Champ { alive: false, ..before[3] }]);
        // back with a new entity: no death
        let mut back = ten(&[]);
        back[3].id = 999;
        assert!(died(&now, &back).is_empty());
        assert!(died(&back, &ten(&[])).is_empty());
    }

    #[test]
    fn a_player_missing_for_a_tick_is_no_death() {
        let mut w = Watch::default();
        w.step(100, ten(&[]), &[], false);
        let mut without = ten(&[]);
        without.remove(3);
        w.step(101, without, &[], false);
        for t in 102..=110 {
            w.step(t, ten(&[]), &[], false);
        }
        assert_eq!(w.tally.deaths, 0);
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
        // match 0 was forgotten (a run from tick 0 is a first run again), match 2 is still known
        assert_eq!(b.watch((2, 0, 1, 0)).pass(0), Pass::Live);
        assert_eq!(b.watch((2, 2, 1, 0)).pass(0), Pass::Again { first: true });
    }
}
