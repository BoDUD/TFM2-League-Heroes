//! 回城记录器（用户 2026-10-15：「按你的建议开pr合并吧」——修了维克托 / 辛德拉 / 卡兹克的等级探针之后，用一个只读的记录器在
//! 平时的对局里收集「金克丝单独在场时对面也回城」的证据，不用专门打测试局）。
//!
//! 游戏 0.6.x 的对线 AI 在算出自己快死时回城：`my_die = (血量 − nuke) × 60 / dps`，nuke / dps 是 15 万以内可见、血量 40% 以上的
//! 敌方英雄的估算之和（champion-data 第 8 节）。AI 回城前多半先走到安全处，按下回城时身边常常已经没人，所以这里记的是回城前
//! `WINDOW` tick 里进过 `NEAR` 以内的敌方英雄（最近多近、多久以前）和这段时间自己的最低血量。
//!
//! 观察钩子 `league_recall_log:watch` 挂在所有玩家上，优先级最低，**永远不改 AI 的输入**（think 一律返回 None）。每 `SCAN`
//! tick 看一次身边的敌方英雄；AI 下回城命令（`InputKindV1::Return`，一次回城的第一道命令）时写一行：
//! `RECALL [来历 m=比赛 s=第几局] t=分:秒 <英雄> T<队> <位置> hp=<现在>% low=<窗口里最低>% near=[<敌方英雄> <最近距离>k <几秒前>, ...]`，
//! 窗口里有敌方英雄、而且血量一直没低于 `SUSPECT_HP`% 的回城再标 `SUSPECT`（不像是被打残了回家）。
//!
//! 0.1.2（用户 2026-11-08「还是有卡回城的BUG啊」）：每次回城还记它怎么结束（`RECALL END`）——传送回家了没有（一 tick 挪了
//! `TELEPORT` 以上），到家 `SHOP_WAIT` tick 后金币和装备有没有变（买了东西没有）；回家前游戏的 AI 自己下了别的命令（它改主意）；
//! AI 一直没下别的命令、`GIVE_UP` tick 还没到家（中间有没有被挪开 `MOVED_R` 以上：回城要站着，挪开就是钩子的走路或位移）；
//! 半路阵亡。每结束 `COUNT_EVERY` 次一行 `COUNT` 累计。`RECALL` 行加上那一刻的金币、装备数。
//!
//! 0.1.3（同一晚的日志：12 万次回城里「到家」69%、「被游戏 AI 取消」31%、「阵亡」0）：传送回家的那一 tick 常常同时带着 AI 的下一个
//! 命令（走出泉水），0.1.2 先看命令、把这些算成了「取消」——现在先看传送；阵亡时拿不到英雄、钩子直接返回，一次都没记到——现在
//! 按玩家的存活和英雄的实体编号（复活是新实体）看；读条里 AI 又按了几次回城也记下（重按会不会让 120 tick 的读条重来：
//! 决定能不能用「再按一次回城」顶掉 AI 半路改主意的走路）；取消的那一刻最近的敌方英雄多远；`RECALL` 行加上离自家水晶多远。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_recall_log.log`，每次启动游戏重写，上一次的留在 .prev.log；
//! 你看的那场全记，其余（服务端的预模拟）一次启动最多 `LOG_CAP` 行。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_recall_log";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_recall_log") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 观察钩子的优先级：最低（只看不改）。
const WATCH_PRIORITY: i32 = -2_000_000;
/// 「身边」：引擎算 nuke / dps 的范围。
pub const NEAR: u64 = 150_000;
/// 回城前看多久（tick，10 秒）。
pub const WINDOW: usize = 600;
/// 多久看一次身边（tick）。
const SCAN: usize = 10;
/// 血量一直在这以上的回城算可疑。
pub const SUSPECT_HP: usize = 60;
/// 一次启动最多写多少行不在屏幕上的（服务端的预模拟；你看的那场不算）：2 万行在 10-30 一次启动的第 4 分钟就满了，2.3 MB。
const LOG_CAP: usize = 2_000;
/// 一次回城走完没有（0.1.2）：一 tick 挪了这么远 = 传送回家了（回城读完）……
pub const TELEPORT: f64 = 60_000.0;
/// ……回城期间离按下回城的地方超过这么远 = 有别的东西让他走开了（钩子的走路、位移）：回城引导要站着……
pub const MOVED_R: f64 = 3_000.0;
/// ……按下回城这么多 tick（20 秒）还没到家、游戏的 AI 也没下别的命令 = 回城没读完。
pub const GIVE_UP: usize = 1_200;
/// 到家后这么多 tick 再看金币和装备（买了没有）。
pub const SHOP_WAIT: usize = 60;
/// 每结束多少次回城写一行累计。
const COUNT_EVERY: usize = 100;

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);
/// 到家的回城里：读条中 AI 又按过回城的、其中读条超过 120 tick 的，以及所有读条超过 120 tick 的（0.1.3：重按会不会重来）。
static PRESSED: AtomicUsize = AtomicUsize::new(0);
static PRESSED_LONG: AtomicUsize = AtomicUsize::new(0);
static LONG: AtomicUsize = AtomicUsize::new(0);
/// 读条的长度（tick）：多过这么多算「重来过」。
pub const CHANNEL: usize = 125;
/// 回城怎么结束的，各几次（`End` 的顺序；只管日志）。
static ENDS: [AtomicUsize; 6] =
    [AtomicUsize::new(0), AtomicUsize::new(0), AtomicUsize::new(0), AtomicUsize::new(0), AtomicUsize::new(0), AtomicUsize::new(0)];

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_RECALL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_recall_log.log");
        }
    }
    PathBuf::from("league_recall_log.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

/// One more line: whether it is to be written - every one from the match on screen (watched, spectated or replayed),
/// the rest the first LOG_CAP of the launch.
fn room(sim: &StableSim<'_>) -> bool {
    let on_screen = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    on_screen || LINES.fetch_add(1, Ordering::Relaxed) < LOG_CAP
}

fn wlog(msg: impl AsRef<str>) {
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (memory log-open-once)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

fn head(sim: &StableSim<'_>) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    let t = sim.tick();
    format!("[{kind} m={} s={}] t={}:{:02}", m(o.match_id), m(o.set_index), t / 3600, t / 60 % 60)
}

fn lane_name(lane: Option<LaneV1>) -> &'static str {
    match lane {
        Some(LaneV1::Top) => "Top",
        Some(LaneV1::Jungle) => "Jungle",
        Some(LaneV1::Mid) => "Mid",
        Some(LaneV1::Bottom) => "Bottom",
        Some(LaneV1::Support) => "Support",
        None => "?",
    }
}

fn percent((now, max): (usize, usize)) -> usize {
    if max == 0 {
        100
    } else {
        now * 100 / max
    }
}

// ===================== 窗口 =====================

/// An enemy champion seen near: when last, how close at the closest.
#[derive(Clone, Debug, PartialEq)]
pub struct Seen {
    pub id: usize,
    pub name: String,
    pub last: usize,
    pub closest: u64,
}

/// What one player saw over the last `WINDOW` ticks.
#[derive(Clone, Debug, Default)]
pub struct Recent {
    pub seen: Vec<Seen>,
    /// (tick, hp %) samples, oldest first.
    pub hp: Vec<(usize, usize)>,
}

impl Recent {
    pub fn note_hp(&mut self, tick: usize, hp: usize) {
        self.hp.push((tick, hp));
        self.forget(tick);
    }

    pub fn note_enemy(&mut self, tick: usize, id: usize, name: &str, dist: u64) {
        match self.seen.iter_mut().find(|s| s.id == id) {
            Some(s) => {
                // a fresh sighting after the window starts the closest distance over
                if tick.saturating_sub(s.last) > WINDOW {
                    s.closest = dist;
                }
                s.last = tick;
                s.closest = s.closest.min(dist);
            }
            None => self.seen.push(Seen { id, name: name.to_string(), last: tick, closest: dist }),
        }
    }

    fn forget(&mut self, tick: usize) {
        self.seen.retain(|s| tick.saturating_sub(s.last) <= WINDOW);
        self.hp.retain(|(t, _)| tick.saturating_sub(*t) <= WINDOW);
    }

    /// Lowest hp % in the window (100 when nothing was sampled).
    pub fn low(&self) -> usize {
        self.hp.iter().map(|(_, h)| *h).min().unwrap_or(100)
    }

    /// Enemies in the window, closest first.
    pub fn near(&self, tick: usize) -> Vec<&Seen> {
        let mut v: Vec<&Seen> = self.seen.iter().filter(|s| tick.saturating_sub(s.last) <= WINDOW).collect();
        v.sort_by_key(|s| s.closest);
        v
    }

    /// An enemy champion was near and the health never fell below `SUSPECT_HP`%: not a trip home to heal.
    pub fn suspect(&self, tick: usize, hp_now: usize) -> bool {
        !self.near(tick).is_empty() && self.low().min(hp_now) >= SUSPECT_HP
    }
}

// ===================== 回城怎么结束 =====================

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// How a recall ended (0.1.2).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum End {
    /// home (teleported) and something bought
    Bought,
    /// home, nothing bought
    Nothing,
    /// the game's AI gave another order before he got home
    Broken,
    /// not home in `GIVE_UP` ticks though the AI never gave another order, after something moved him off the spot
    Moved,
    /// the same, never moved off the spot (damage, a stun, or an order that kept him busy)
    Stuck,
    Died,
}

/// One recall under way: when the game's AI pressed it, his entity and name (a respawn is a new entity: he died on the way),
/// where he stood, his gold and items then, the first time he was found `MOVED_R` from there while the AI still recalled
/// (tick, how far), when he got home, and the AI's Returns after the first while it ran (0.1.3).
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Trip {
    pub start: usize,
    pub who: usize,
    pub name: String,
    pub at: (f64, f64),
    pub gold: usize,
    pub items: usize,
    pub moved: Option<(usize, f64)>,
    pub home_at: Option<usize>,
    pub presses: usize,
}

/// What one tick tells about the recall `t`: how it ended and the line to write, if it did. `who`: his living champion's
/// entity now (None: dead); `last_at`: where he stood the tick before; `order`: the game's AI's order this tick (None:
/// none); `near_now`: the nearest enemy champion now (looked up only for an order that breaks it off).
#[allow(clippy::too_many_arguments)]
pub fn follow(
    t: &mut Trip,
    tick: usize,
    who: Option<usize>,
    at: (f64, f64),
    last_at: Option<(f64, f64)>,
    order: Option<InputKindV1>,
    gold: usize,
    items: usize,
    near_now: Option<u64>,
) -> Option<(End, String)> {
    let n = tick.saturating_sub(t.start);
    let moved = |t: &Trip| {
        t.moved.map_or_else(
            || "never moved off the spot".to_string(),
            |(k, d)| format!("moved {:.0}k off the spot at +{} ticks", d / 1000.0, k.saturating_sub(t.start)),
        )
    };
    // dead, or a new entity (he respawned): he died on the way (0.1.3; 0.1.2 never saw one)
    if who != Some(t.who) {
        return Some((End::Died, format!("died after {n} ticks ({})", moved(t))));
    }
    if let Some(h) = t.home_at {
        if tick < h + SHOP_WAIT {
            return None;
        }
        let bought = items > t.items || gold + 100 < t.gold;
        return Some((
            if bought { End::Bought } else { End::Nothing },
            format!(
                "home after {} ticks{}: gold {} -> {gold}, items {} -> {items}{}",
                h.saturating_sub(t.start),
                if t.presses > 0 { format!(" ({} more Returns on the way)", t.presses) } else { String::new() },
                t.gold,
                t.items,
                if bought { "" } else { " - nothing bought" }
            ),
        ));
    }
    // home first: the teleport's tick often carries the AI's next order too (0.1.2 counted those as broken off)
    if last_at.is_some_and(|p| dist(p, at) >= TELEPORT) {
        t.home_at = Some(tick);
        return None;
    }
    match order {
        Some(InputKindV1::Return) => t.presses += 1,
        Some(k) => {
            let near = near_now.map_or_else(|| "none alive".to_string(), |d| format!("{}k", d / 1000));
            return Some((
                End::Broken,
                format!("broken off by the game's AI after {n} ticks (its order: {k:?}; nearest enemy champion {near}; {})", moved(t)),
            ));
        }
        None => {}
    }
    if t.moved.is_none() && dist(t.at, at) > MOVED_R {
        t.moved = Some((tick, dist(t.at, at)));
    }
    if n >= GIVE_UP {
        let end = if t.moved.is_some() { End::Moved } else { End::Stuck };
        return Some((end, format!("not home after {n} ticks though the game's AI never ordered anything else ({})", moved(t))));
    }
    None
}

/// The running count of how recalls ended, every `COUNT_EVERY` ends.
fn count_line() -> Option<String> {
    let e: Vec<usize> = ENDS.iter().map(|c| c.load(Ordering::Relaxed)).collect();
    let total: usize = e.iter().sum();
    (total > 0 && total.is_multiple_of(COUNT_EVERY)).then(|| {
        format!(
            "COUNT recalls ended {total}: home {} (bought {}, nothing bought {}), broken off by the game's AI {}, not home though \
             the AI kept recalling {} (moved off the spot {}, never moved {}), died {} | home trips with more Returns on the way {} \
             (longer than {CHANNEL} ticks {}), all home trips longer than {CHANNEL} ticks {}",
            e[0] + e[1],
            e[0],
            e[1],
            e[2],
            e[3] + e[4],
            e[3],
            e[4],
            e[5],
            PRESSED.load(Ordering::Relaxed),
            PRESSED_LONG.load(Ordering::Relaxed),
            LONG.load(Ordering::Relaxed)
        )
    })
}

// ===================== 观察钩子 =====================

#[derive(Clone, Default)]
struct Watch {
    recent: Recent,
    next_scan: usize,
    /// The AI is in a recall order (no new line until it gives another order).
    returning: bool,
    /// The recall under way, and where he stood the tick before (0.1.2).
    trip: Option<Trip>,
    last_at: Option<(f64, f64)>,
    /// Our nexus, and when to look for it again while none is found (0.1.3).
    home: Option<(f64, f64)>,
    home_next: usize,
}

/// The nearest living enemy champion to `me` (0.1.3).
fn nearest_enemy(sim: &StableSim<'_>, me: usize, team: usize) -> Option<u64> {
    (0..sim.champion_count())
        .map(|i| sim.champion_id_at(i))
        .filter(|&id| sim.get_entity(id).is_some_and(|e| e.team() != team && e.is_alive()))
        .map(|id| root(sim.distance_sq(me, id)))
        .min()
}

/// Distance in map units from a squared distance.
fn root(sq: u64) -> u64 {
    (sq as f64).sqrt() as u64
}

impl Watch {
    fn scan(&mut self, sim: &StableSim<'_>, me: usize, team: usize, tick: usize) {
        if let Some(e) = sim.get_entity(me) {
            self.recent.note_hp(tick, percent(e.hp()));
        }
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(e) = sim.get_entity(id) else { continue };
            if e.team() == team || !e.is_alive() {
                continue;
            }
            let d = root(sim.distance_sq(me, id));
            if d <= NEAR {
                let name = e.name().unwrap_or_else(|| format!("#{id}"));
                self.recent.note_enemy(tick, id, &name, d);
            }
        }
    }
}

impl StablePlayerAi for Watch {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:watch")
    }

    fn priority(&self) -> i32 {
        WATCH_PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let tick = ctx.tick();
        let (player, team, lane) = (ctx.player_id(), ctx.team(), ctx.lane());
        let sim = ctx.sim()?;
        let pl = sim.get_player(player)?;
        let order = base.and_then(|b| InputKindV1::from_code(b.kind));
        let (gold, items) = (pl.gold(), pl.item_count());
        let me = pl.champion().filter(|c| pl.is_alive() && c.is_alive());
        // the recall under way: how it ends (0.1.2; 0.1.3: a death seen, home before the order)
        let ended = match self.trip.as_mut() {
            Some(t) => {
                let who = me.as_ref().map(|m| m.id());
                let at = me.as_ref().map_or(t.at, |m| (m.pos().0 as f64, m.pos().1 as f64));
                let near_now = match (order, who) {
                    (Some(k), Some(id)) if k != InputKindV1::Return => nearest_enemy(&sim, id, team),
                    _ => None,
                };
                follow(t, tick, who, at, self.last_at, order, gold, items, near_now)
            }
            None => None,
        };
        if let Some((end, what)) = ended {
            let tr = self.trip.take().unwrap_or_default();
            ENDS[end as usize].fetch_add(1, Ordering::Relaxed);
            if matches!(end, End::Bought | End::Nothing) {
                let long = tr.home_at.is_some_and(|h| h > tr.start + CHANNEL);
                if tr.presses > 0 {
                    PRESSED.fetch_add(1, Ordering::Relaxed);
                    if long {
                        PRESSED_LONG.fetch_add(1, Ordering::Relaxed);
                    }
                }
                if long {
                    LONG.fetch_add(1, Ordering::Relaxed);
                }
            }
            if room(&sim) {
                wlog(format!("RECALL END {} {} T{team}: {what}", head(&sim), tr.name));
            }
            if let Some(line) = count_line() {
                wlog(line);
            }
        }
        let Some(me) = me else {
            self.last_at = None;
            return None;
        };
        let (me_id, me_name, hp_now) = (me.id(), me.name().unwrap_or_default(), percent(me.hp()));
        if tick >= self.next_scan {
            self.next_scan = tick + SCAN;
            self.scan(&sim, me_id, team, tick);
        }
        if self.home.is_none() && tick >= self.home_next {
            self.home_next = tick + 600;
            self.home = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .find(|e| e.team() == team && e.kind() == Some(EntityKindV1::Nexus))
                .map(|e| (e.pos().0 as f64, e.pos().1 as f64));
        }
        let at = (me.pos().0 as f64, me.pos().1 as f64);
        self.last_at = Some(at);
        let kind = order?;
        if kind != InputKindV1::Return {
            self.returning = false;
            return None;
        }
        if self.returning {
            return None;
        }
        self.returning = true;
        self.trip = Some(Trip { start: tick, who: me_id, name: me_name.clone(), at, gold, items, ..Trip::default() });
        if !room(&sim) {
            return None;
        }
        let near: Vec<String> = self
            .recent
            .near(tick)
            .iter()
            .map(|s| format!("{} {}k {:.1}s", s.name, s.closest / 1000, tick.saturating_sub(s.last) as f64 / 60.0))
            .collect();
        wlog(format!(
            "RECALL {} {me_name} T{team} {} hp={hp_now}% low={}% gold={gold} items={items} home={} near=[{}]{}",
            head(&sim),
            lane_name(lane),
            self.recent.low(),
            self.home.map_or_else(|| "?".to_string(), |h| format!("{:.0}k", dist(h, at) / 1000.0)),
            near.join(", "),
            if self.recent.suspect(tick, hp_now) { " SUSPECT" } else { "" }
        ));
        None
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (read-only recall log) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Watch::default());
    host.log(LogLevel::Info, "league_recall_log loaded (read-only recall log).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    const ME: Option<usize> = Some(7);

    fn trip(start: usize, at: (f64, f64), gold: usize, items: usize) -> Trip {
        Trip { start, who: 7, name: "league_jinx".to_string(), at, gold, items, ..Trip::default() }
    }

    #[test]
    fn a_recall_that_gets_home_and_buys() {
        let spot = (500_000.0, 500_000.0);
        let fountain = (60_000.0, 940_000.0);
        let mut t = trip(100, spot, 1300, 2);
        assert_eq!(follow(&mut t, 200, ME, spot, Some(spot), None, 1320, 2, None), None);
        // the AI presses recall again on the way: counted
        assert_eq!(follow(&mut t, 210, ME, spot, Some(spot), Some(InputKindV1::Return), 1320, 2, None), None);
        // the teleport home, with the AI's next order (a walk out) on the same tick: home, not broken off (0.1.3)
        assert_eq!(follow(&mut t, 220, ME, fountain, Some(spot), Some(InputKindV1::Move), 1350, 2, None), None);
        assert_eq!(t.home_at, Some(220));
        assert_eq!(follow(&mut t, 260, ME, fountain, Some(fountain), Some(InputKindV1::Move), 250, 3, None), None);
        let (end, line) = follow(&mut t, 280, ME, fountain, Some(fountain), Some(InputKindV1::Move), 250, 3, None).unwrap();
        assert_eq!(end, End::Bought);
        assert!(line.starts_with("home after 120 ticks (1 more Returns on the way): gold 1300 -> 250, items 2 -> 3"), "{line}");
        // home with nothing bought
        let mut t = Trip { home_at: Some(500), ..trip(0, spot, 300, 4) };
        let (end, line) = follow(&mut t, 560, ME, fountain, Some(fountain), None, 340, 4, None).unwrap();
        assert_eq!(end, End::Nothing);
        assert!(line.ends_with("nothing bought"), "{line}");
    }

    #[test]
    fn a_recall_broken_off_moved_stuck_or_cut_by_death() {
        let spot = (500_000.0, 500_000.0);
        let start = trip(100, spot, 500, 1);
        // the game's AI walks off: broken off by itself, with the nearest enemy then
        let mut t = start.clone();
        let (end, line) = follow(&mut t, 150, ME, spot, Some(spot), Some(InputKindV1::Move), 500, 1, Some(41_500)).unwrap();
        assert_eq!(end, End::Broken);
        assert!(line.contains("nearest enemy champion 41k"), "{line}");
        // walked off the spot while the AI still recalled (a hook's walk), then not home in time
        let mut t = start.clone();
        assert_eq!(follow(&mut t, 160, ME, (505_000.0, 500_000.0), Some((504_000.0, 500_000.0)), None, 500, 1, None), None);
        assert_eq!(t.moved, Some((160, 5_000.0)));
        let got = follow(&mut t, 100 + GIVE_UP, ME, (520_000.0, 500_000.0), Some((519_000.0, 500_000.0)), None, 520, 1, None);
        let (end, line) = got.unwrap();
        assert_eq!(end, End::Moved);
        assert!(line.contains("moved 5k off the spot at +60 ticks"), "{line}");
        // standing on the spot and never home
        let mut t = start.clone();
        let got = follow(&mut t, 100 + GIVE_UP, ME, spot, Some(spot), Some(InputKindV1::Return), 520, 1, None);
        assert_eq!(got.map(|e| e.0), Some(End::Stuck));
        // dead (no living champion), or back as a new entity after a respawn: died on the way
        let mut t = start.clone();
        assert_eq!(follow(&mut t, 300, None, spot, None, None, 520, 1, None).map(|e| e.0), Some(End::Died));
        let mut t = start;
        let fountain = (60_000.0, 940_000.0);
        assert_eq!(follow(&mut t, 900, Some(31), fountain, None, None, 520, 1, None).map(|e| e.0), Some(End::Died));
    }

    #[test]
    fn a_recall_with_an_enemy_near_at_full_health_is_suspect() {
        let mut r = Recent::default();
        for t in (0..300).step_by(10) {
            r.note_hp(t, 95);
        }
        r.note_enemy(100, 7, "league_jinx", 80_000);
        r.note_enemy(150, 7, "league_jinx", 60_000);
        assert!(r.suspect(300, 95));
        assert_eq!(r.near(300)[0].closest, 60_000);
        assert_eq!(r.near(300)[0].last, 150);
    }

    #[test]
    fn a_trip_home_after_losing_health_or_with_nobody_near_is_not() {
        let mut r = Recent::default();
        r.note_hp(0, 100);
        r.note_hp(100, 30);
        r.note_enemy(100, 7, "league_jinx", 50_000);
        assert!(!r.suspect(200, 45));
        let mut quiet = Recent::default();
        quiet.note_hp(0, 100);
        assert!(!quiet.suspect(100, 100));
    }

    #[test]
    fn sightings_older_than_the_window_are_dropped() {
        let mut r = Recent::default();
        r.note_enemy(0, 7, "league_jinx", 10_000);
        r.note_hp(WINDOW + 50, 100);
        assert!(r.near(WINDOW + 50).is_empty());
        r.note_enemy(WINDOW + 60, 7, "league_jinx", 90_000);
        assert_eq!(r.near(WINDOW + 60)[0].closest, 90_000);
    }
}
