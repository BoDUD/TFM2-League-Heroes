//! 射手的 AI 观察（只读）。用户 2026-11-11：「卡莎是真有点问题 你看这局的对局」「也不平A」。那局（m=4189 第 2 局，红方下路）
//! 卡莎 11 分钟一次都没引爆过被动（league_marks 没有一行 KAISA POP），站桩规则（league_ult_press）也只替她补按了 13 次普攻；
//! 电竞大脑的两轮平衡补丁都给她加强（她的胜率低），同一版却削了金克丝、泽丽、赛娜、千珏。旧版 AI（经典 SDK 0.5.1 的模拟）里
//! 她 10 分钟普攻英雄 47–58 次，和韦鲁斯一样；现在的 AI 那时让她干什么，现有的日志都看不出来。
//!
//! 观察钩子 `league_ai_watch:watch` 挂在所有玩家上，优先级最低，**永远不改 AI 的输入**（think 一律返回 None），只看射手
//! （[`RANGES`]：主包 category 为 Range 的英雄）。游戏的 AI 只在它做决定的 tick 下命令，别的 tick 没有命令、英雄照着上一道
//! 命令做（league_recall_log 0.1.3 的发现），所以这里按「她手上的命令」（AI 最近下的那一道）分类。
//!
//! 她活着的每一 tick：
//! - 最近的、看得见、选得中的敌方英雄有多远；在她的普攻距离内（中心到中心）算「够得着」；
//! - 够得着、普攻好了（冷却 0）、没在放技能或被位移（`Animation` / `ForceMove`）、没被控的 tick 里，她手上的命令是什么：
//!   普攻英雄、普攻别的（小兵、野怪、塔）、往敌人走、往回撤、横着走、站在原地（走到她脚下 [`HERE`] 以内）、Q / W / R、回城、
//!   没有命令；人在不在动；
//! - 普攻出手几次（普攻冷却从 0 开始走），打的是英雄还是别的（出手前最近那道普攻命令的目标）；Q / W / R 各放了几次。
//!
//! 一连 [`IDLE_MIN`] tick 够得着、普攻好了却没出手，结束时写一行 `IDLE`：多久、那段时间她手上的命令、敌人多远、她离敌方
//! 的塔多远、血量、Q / W 好没好、怎么结束的。每 [`SUM_EVERY`] tick 每个射手写一行 `SUM`：这一局到这时的累计（一局的最后一行
//! 就是整局）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ai_watch.log`，每次启动游戏重写，上一次的留在 .prev.log；
//! 你看的那场全记，其余（服务端的预模拟）一次启动最多 [`LOG_CAP`] 行。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_ai_watch";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_ai_watch") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 观察钩子的优先级：最低（只看不改）。
const WATCH_PRIORITY: i32 = -2_000_000;

/// 主包的射手（数据里 category 为 Range）和她们的普攻距离（attack.range；测试拿数据对）。引擎的接口在运行时读不到普攻距离。
pub const RANGES: [(&str, u64); 29] = [
    ("league_akshan", 55000),
    ("league_aphelios", 55000),
    ("league_ashe", 60000),
    ("league_caitlyn", 65000),
    ("league_corki", 55000),
    ("league_draven", 55000),
    ("league_ezreal", 55000),
    ("league_graves", 46000),
    ("league_jhin", 55000),
    ("league_jinx", 64500),
    ("league_kaisa", 55000),
    ("league_kalista", 52500),
    ("league_kindred", 55000),
    ("league_kogmaw", 55000),
    ("league_lucian", 55000),
    ("league_missfortune", 55000),
    ("league_nilah", 30000),
    ("league_quinn", 52500),
    ("league_samira", 55000),
    ("league_senna", 62000),
    ("league_sivir", 55000),
    ("league_smolder", 55000),
    ("league_tristana", 55000),
    ("league_twitch", 55000),
    ("league_varus", 57500),
    ("league_vayne", 55000),
    ("league_xayah", 57500),
    ("league_yunara", 57500),
    ("league_zeri", 60000),
];

pub fn range_of(name: &str) -> Option<u64> {
    RANGES.iter().find(|(n, _)| *n == name).map(|&(_, r)| r)
}

/// 一连这么多 tick 够得着、普攻好了却没出手，写一行 `IDLE`（半秒）。
pub const IDLE_MIN: usize = 30;
/// 多久写一行 `SUM`（tick，30 秒）。
pub const SUM_EVERY: usize = 1_800;
/// 「走到她脚下」：走路命令的目的地离她这么近，算让她站着。
pub const HERE: f64 = 3_000.0;
/// 走路命令的目的地离敌人比她现在近（远）这么多以上，算往敌人走（往回撤）；之间算横着走。
pub const MOVE_SLACK: f64 = 2_000.0;
/// 普攻出手时，往回看这么多 tick 内最近的普攻命令定它打的是谁。
pub const ATTACK_LOOKBACK: usize = 60;
/// `SUM` 里「最近的敌方英雄」的第一档：她的普攻距离再加这么多。
pub const NEAR_PAD: u64 = 10_000;
/// 一次启动最多写多少行不在屏幕上的（服务端的预模拟）。
pub const LOG_CAP: usize = 40_000;

/// 放技能（施法动作还在播）或被强制位移：这时不算「普攻好了却不出手」。
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];
/// 被控住、出不了普攻（定身 `Bind` 还能打，不算）。
const CONTROLLED: [CcKindV1; 6] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::BlockAttack, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AI_WATCH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ai_watch.log");
        }
    }
    PathBuf::from("league_ai_watch.log")
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

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn at(e: &StableEntity<'_, '_>) -> (f64, f64) {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn percent((now, max): (usize, usize)) -> usize {
    if max == 0 {
        100
    } else {
        now * 100 / max
    }
}

fn has_cc(e: &StableEntity<'_, '_>, kinds: &[CcKindV1]) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
}

// ===================== 分类 =====================

/// 她手上的命令，对着最近的敌方英雄看。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    AtkChamp,
    AtkOther,
    Toward,
    Away,
    Aside,
    Here,
    Q,
    W,
    R,
    Home,
    NoOrder,
}

pub const KINDS: usize = 11;
pub const LABELS: [&str; KINDS] = ["A champ", "A other", "toward", "away", "aside", "stand", "Q", "W", "R", "home", "none"];

/// What her order `order` (the AI's last input to her, and whether its target is a champion) has her do, she at `me`, the
/// nearest enemy champion at `foe`.
pub fn kind_of(order: Option<(InputV1, bool)>, me: (f64, f64), foe: (f64, f64)) -> Kind {
    let Some((o, champ)) = order else { return Kind::NoOrder };
    match InputKindV1::from_code(o.kind) {
        Some(InputKindV1::Attack) if champ => Kind::AtkChamp,
        Some(InputKindV1::Attack) => Kind::AtkOther,
        Some(InputKindV1::Skill) => Kind::Q,
        Some(InputKindV1::Skill2) => Kind::W,
        Some(InputKindV1::Ult) => Kind::R,
        Some(InputKindV1::Return) => Kind::Home,
        Some(InputKindV1::Move) => {
            let to = (o.x as f64, o.y as f64);
            if dist(to, me) <= HERE {
                return Kind::Here;
            }
            let (now, then) = (dist(me, foe), dist(to, foe));
            if then < now - MOVE_SLACK {
                Kind::Toward
            } else if then > now + MOVE_SLACK {
                Kind::Away
            } else {
                Kind::Aside
            }
        }
        None => Kind::NoOrder,
    }
}

/// `[label n%, ...]` of the non-zero counts, the share of `of`.
pub fn shares(counts: &[usize; KINDS], of: usize) -> String {
    let pct = |n: usize| if of == 0 { 0 } else { n * 100 / of };
    let v: Vec<String> =
        (0..KINDS).filter(|&k| counts[k] > 0).map(|k| format!("{} {}%", LABELS[k], pct(counts[k]))).collect();
    v.join(", ")
}

// ===================== 累计 =====================

/// One marksman's totals in one match.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Tally {
    pub alive: usize,
    /// ticks with an enemy champion within her attack range ...
    pub reach: usize,
    /// ... and of them, her attack ready, she not casting, moved or controlled
    pub ready: usize,
    /// her order in the `ready` ticks
    pub kinds: [usize; KINDS],
    /// the `ready` ticks she moved
    pub moving: usize,
    pub atk_champ: usize,
    pub atk_other: usize,
    /// Q, W, R
    pub casts: [usize; 3],
    /// alive ticks with the nearest enemy champion within her range + NEAR_PAD, 100000, 150000
    pub near: [usize; 3],
    pub idle_runs: usize,
    pub idle_ticks: usize,
    pub idle_longest: usize,
}

impl Tally {
    pub fn line(&self, range: u64) -> String {
        let pct = |n: usize, of: usize| if of == 0 { 0 } else { n * 100 / of };
        format!(
            "alive {}s | enemy champion in reach {}s, attack ready then {}s: orders [{}], moving {}% | attacks at champions {}, \
             at others {} | casts Q {} W {} R {} | nearest enemy champion within {}k {}%, 100k {}%, 150k {}% of alive | idle \
             runs {} ({}s, longest {:.1}s)",
            self.alive / 60,
            self.reach / 60,
            self.ready / 60,
            shares(&self.kinds, self.ready),
            pct(self.moving, self.ready),
            self.atk_champ,
            self.atk_other,
            self.casts[0],
            self.casts[1],
            self.casts[2],
            (range + NEAR_PAD) / 1000,
            pct(self.near[0], self.alive),
            pct(self.near[1], self.alive),
            pct(self.near[2], self.alive),
            self.idle_runs,
            self.idle_ticks / 60,
            self.idle_longest as f64 / 60.0
        )
    }
}

/// A run of ticks with an enemy champion in reach and her attack ready, no attack out.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Run {
    pub start: usize,
    pub len: usize,
    pub kinds: [usize; KINDS],
    pub moving: usize,
    pub foe: String,
    pub d0: f64,
    pub d_min: f64,
    pub d_max: f64,
    pub hp: usize,
    pub q_ready: bool,
    pub w_ready: bool,
    /// her distance to the nearest standing enemy tower at the start
    pub tower: Option<f64>,
    /// how old her order was at the start (ticks)
    pub order_age: Option<usize>,
}

impl Run {
    pub fn line(&self, why: &str) -> String {
        format!(
            "{:.1}s from t={}:{:02}, ended: {why} | orders [{}], moving {}% (her order {} at the start) | {} {:.0}k -> \
             {:.0}-{:.0}k | hp {}% | Q {} W {} | nearest enemy tower {}",
            self.len as f64 / 60.0,
            self.start / 3600,
            self.start / 60 % 60,
            shares(&self.kinds, self.len),
            if self.len == 0 { 0 } else { self.moving * 100 / self.len },
            self.order_age.map_or_else(|| "none".to_string(), |a| format!("{a} ticks old")),
            self.foe,
            self.d0 / 1000.0,
            self.d_min / 1000.0,
            self.d_max / 1000.0,
            self.hp,
            if self.q_ready { "ready" } else { "cooling" },
            if self.w_ready { "ready" } else { "cooling" },
            self.tower.map_or_else(|| "none".to_string(), |d| format!("{:.0}k", d / 1000.0))
        )
    }
}

// ===================== 观察钩子 =====================

#[derive(Clone, Default)]
struct Watch {
    /// her champion's id and attack range (0: not a marksman, nothing to watch); `checked` once she was seen
    name: String,
    range: u64,
    checked: bool,
    /// the tick last seen: a lower one is a new sim on this hook object (start over)
    last_tick: Option<usize>,
    tally: Tally,
    next_sum: usize,
    /// her order: the AI's last input, whether its target was a champion, its tick
    order: Option<(InputV1, bool, usize)>,
    /// the last Attack order: at a champion or not, its tick
    last_attack: Option<(bool, usize)>,
    /// attack, Q, W, R ready the tick before; her entity and spot the tick before
    prev_ready: [bool; 4],
    prev_id: Option<usize>,
    prev_at: Option<(f64, f64)>,
    run: Option<Run>,
    /// this match's enemy towers (entity, spot), found once
    towers: Option<Vec<(usize, (f64, f64))>>,
}

impl Watch {
    fn end_run(&mut self, sim: &StableSim<'_>, team: usize, why: &str) {
        let Some(run) = self.run.take() else { return };
        if run.len < IDLE_MIN {
            return;
        }
        self.tally.idle_runs += 1;
        self.tally.idle_ticks += run.len;
        self.tally.idle_longest = self.tally.idle_longest.max(run.len);
        if room(sim) {
            wlog(format!("IDLE {} {} T{team}: {}", head(sim), self.name, run.line(why)));
        }
    }

    fn nearest_tower(&mut self, sim: &StableSim<'_>, team: usize, me: (f64, f64)) -> Option<f64> {
        let towers = self.towers.get_or_insert_with(|| {
            (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|e| e.is_tower() && e.team() != team)
                .map(|e| (e.id(), at(&e)))
                .collect()
        });
        towers
            .iter()
            .filter(|(id, _)| sim.get_entity(*id).is_some_and(|e| e.is_alive()))
            .map(|(_, p)| dist(*p, me))
            .min_by(|a, b| a.total_cmp(b))
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
        if self.last_tick.is_some_and(|t| tick < t) {
            *self = Watch::default();
        }
        self.last_tick = Some(tick);
        if self.checked && self.range == 0 {
            return None;
        }
        let (player, team, lane) = (ctx.player_id(), ctx.team(), ctx.lane());
        let sim = ctx.sim()?;
        let pl = sim.get_player(player)?;
        let Some(me) = pl.champion().filter(|c| pl.is_alive() && c.is_alive()) else {
            self.end_run(&sim, team, "she died");
            self.prev_id = None;
            return None;
        };
        if !self.checked {
            self.checked = true;
            self.name = me.name().unwrap_or_default();
            self.range = range_of(&self.name).unwrap_or(0);
            self.next_sum = tick + SUM_EVERY;
            if self.range == 0 {
                return None;
            }
        }
        let (me_id, my_at) = (me.id(), at(&me));
        let ready_of = |s: SkillSlotV1| me.cooldown(s).is_some_and(|c| c.unlocked && c.remaining == 0);
        let ready = [SkillSlotV1::Attack, SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult].map(ready_of);
        let fresh = self.prev_id == Some(me_id);
        if !fresh {
            // a new life: her old order, cooldowns and spot are gone
            self.order = None;
            self.last_attack = None;
            self.prev_at = None;
        }
        // the AI's order this tick, if it gave one
        if let Some(b) = base {
            let champ = b.kind == InputKindV1::Attack.code()
                && InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)
                && sim.get_entity(b.target.target_id).is_some_and(|t| t.is_champion());
            self.order = Some((b, champ, tick));
            if b.kind == InputKindV1::Attack.code() {
                self.last_attack = Some((champ, tick));
            }
        }
        // what went out: an attack when its cooldown starts (at whom: the last Attack order), Q / W / R the same
        let mut attacked = None;
        if fresh {
            if self.prev_ready[0] && !ready[0] {
                let champ = self.last_attack.is_some_and(|(c, t)| c && tick.saturating_sub(t) <= ATTACK_LOOKBACK);
                if champ {
                    self.tally.atk_champ += 1;
                } else {
                    self.tally.atk_other += 1;
                }
                attacked = Some(champ);
            }
            for k in 1..4 {
                if self.prev_ready[k] && !ready[k] {
                    self.tally.casts[k - 1] += 1;
                }
            }
        }
        // the nearest enemy champion she can see and target
        let mut best: Option<(f64, usize, (f64, f64))> = None;
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(e) = sim.get_entity(id) else { continue };
            if e.team() == team || !e.is_alive() || !e.is_targetable() || !sim.is_visible(team, id) {
                continue;
            }
            let p = at(&e);
            let d = dist(my_at, p);
            if best.map_or(true, |b| d < b.0) {
                best = Some((d, id, p));
            }
        }
        self.tally.alive += 1;
        if let Some((d, _, _)) = best {
            for (k, r) in [(self.range + NEAR_PAD) as f64, 100_000.0, 150_000.0].into_iter().enumerate() {
                if d <= r {
                    self.tally.near[k] += 1;
                }
            }
        }
        let in_reach = best.filter(|b| b.0 <= self.range as f64);
        let moving = self.prev_at.is_some_and(|p| dist(p, my_at) > 1.0);
        let open = in_reach.is_some() && ready[0] && !has_cc(&me, &BUSY) && !has_cc(&me, &CONTROLLED);
        if in_reach.is_some() {
            self.tally.reach += 1;
        }
        match (open, in_reach) {
            (true, Some((d, id, p))) => {
                let k = kind_of(self.order.map(|(o, c, _)| (o, c)), my_at, p) as usize;
                self.tally.ready += 1;
                self.tally.kinds[k] += 1;
                if moving {
                    self.tally.moving += 1;
                }
                if self.run.is_none() {
                    let foe = sim.get_entity(id).and_then(|e| e.name()).unwrap_or_else(|| format!("#{id}"));
                    let tower = self.nearest_tower(&sim, team, my_at);
                    self.run = Some(Run {
                        start: tick,
                        foe,
                        d0: d,
                        d_min: d,
                        d_max: d,
                        hp: percent(me.hp()),
                        q_ready: ready[1],
                        w_ready: ready[2],
                        tower,
                        order_age: self.order.map(|(_, _, t)| tick.saturating_sub(t)),
                        ..Run::default()
                    });
                }
                if let Some(run) = self.run.as_mut() {
                    run.len += 1;
                    run.kinds[k] += 1;
                    if moving {
                        run.moving += 1;
                    }
                    run.d_min = run.d_min.min(d);
                    run.d_max = run.d_max.max(d);
                }
            }
            _ => {
                let why = match (attacked, in_reach.is_some()) {
                    (Some(true), _) => "she attacked a champion",
                    (Some(false), _) => "she attacked something else",
                    (None, false) => "no enemy champion in reach",
                    (None, true) if has_cc(&me, &CONTROLLED) => "she was controlled",
                    (None, true) if has_cc(&me, &BUSY) => "she cast or was moved",
                    (None, true) => "her attack not ready",
                };
                self.end_run(&sim, team, why);
            }
        }
        if tick >= self.next_sum {
            self.next_sum = tick + SUM_EVERY;
            if room(&sim) {
                wlog(format!("SUM {} {} T{team} {} {}", head(&sim), self.name, lane_name(lane), self.tally.line(self.range)));
            }
        }
        self.prev_ready = ready;
        self.prev_id = Some(me_id);
        self.prev_at = Some(my_at);
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
        "=== {ID} v{VERSION} (read-only: what the game's AI has each marksman do while an enemy champion is in reach and her \
         attack is ready) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Watch::default());
    host.log(LogLevel::Info, "league_ai_watch loaded (read-only marksman AI log).");
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

    fn order(kind: InputKindV1, x: u64, y: u64) -> InputV1 {
        InputV1 { kind: kind.code(), x, y, ..InputV1::default() }
    }

    #[test]
    fn ranges_are_the_marksmen_of_the_data() {
        // every main-pack hero of category Range with her attack range, and nothing else: a new marksman fails this until
        // she is added to RANGES (the engine's API cannot read an attack range at run time)
        let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../league/champion");
        let mut found = Vec::new();
        for entry in std::fs::read_dir(&dir).expect("league/champion") {
            let path = entry.unwrap().path();
            if path.extension().and_then(|x| x.to_str()) != Some("data_champion") {
                continue;
            }
            let raw = std::fs::read_to_string(&path).unwrap().replace("\r\n", "\n");
            let raw = raw.trim_start_matches('\u{feff}');
            let field = |name: &str| {
                raw.lines()
                    .find_map(|l| l.strip_prefix(&format!("  \"{name}\": \"")))
                    .map(|r| r.trim_end_matches(',').trim_end_matches('"').to_string())
            };
            if field("category").as_deref() != Some("Range") {
                continue;
            }
            let range: u64 = raw
                .lines()
                .skip_while(|l| *l != "  \"attack\": {")
                .skip(1)
                .take_while(|l| !l.starts_with("  }"))
                .find_map(|l| l.strip_prefix("    \"range\": "))
                .map(|r| r.trim_end_matches(',').parse().unwrap())
                .unwrap_or_else(|| panic!("no attack range in {}", path.display()));
            found.push((field("id").expect("id"), range));
        }
        found.sort();
        let listed: Vec<(String, u64)> = RANGES.iter().map(|&(n, r)| (n.to_string(), r)).collect();
        assert!(found.len() >= 25, "read only {} marksmen from {}", found.len(), dir.display());
        assert_eq!(listed, found);
    }

    #[test]
    fn her_order_is_read_against_the_nearest_enemy() {
        let me = (500_000.0, 500_000.0);
        let foe = (550_000.0, 500_000.0);
        assert_eq!(kind_of(None, me, foe), Kind::NoOrder);
        let atk = order(InputKindV1::Attack, 0, 0);
        assert_eq!(kind_of(Some((atk, true)), me, foe), Kind::AtkChamp);
        assert_eq!(kind_of(Some((atk, false)), me, foe), Kind::AtkOther);
        assert_eq!(kind_of(Some((order(InputKindV1::Move, 501_000, 500_500), false)), me, foe), Kind::Here);
        assert_eq!(kind_of(Some((order(InputKindV1::Move, 530_000, 500_000), false)), me, foe), Kind::Toward);
        assert_eq!(kind_of(Some((order(InputKindV1::Move, 450_000, 500_000), false)), me, foe), Kind::Away);
        // 30k straight up: 58.3k from him against 50k now - away; 10k up: 51k - aside
        assert_eq!(kind_of(Some((order(InputKindV1::Move, 500_000, 530_000), false)), me, foe), Kind::Away);
        assert_eq!(kind_of(Some((order(InputKindV1::Move, 500_000, 510_000), false)), me, foe), Kind::Aside);
        assert_eq!(kind_of(Some((order(InputKindV1::Skill2, 0, 0), false)), me, foe), Kind::W);
        assert_eq!(kind_of(Some((order(InputKindV1::Skill, 0, 0), false)), me, foe), Kind::Q);
        assert_eq!(kind_of(Some((order(InputKindV1::Ult, 0, 0), false)), me, foe), Kind::R);
        assert_eq!(kind_of(Some((order(InputKindV1::Return, 0, 0), false)), me, foe), Kind::Home);
    }

    #[test]
    fn the_lines_read() {
        let mut t = Tally { alive: 6000, reach: 1200, ready: 600, moving: 300, atk_champ: 4, atk_other: 50, ..Tally::default() };
        t.kinds[Kind::Away as usize] = 300;
        t.kinds[Kind::NoOrder as usize] = 300;
        t.casts = [3, 2, 0];
        t.near = [1500, 3000, 4500];
        let s = t.line(55_000);
        assert!(s.contains("in reach 20s, attack ready then 10s: orders [away 50%, none 50%], moving 50%"), "{s}");
        assert!(s.contains("attacks at champions 4, at others 50 | casts Q 3 W 2 R 0"), "{s}");
        assert!(s.contains("within 65k 25%, 100k 50%, 150k 75% of alive"), "{s}");
        let mut r = Run { start: 2520, len: 90, foe: "league_varus".into(), d0: 54_000.0, d_min: 50_000.0, d_max: 55_000.0, hp: 40, ..Run::default() };
        r.kinds[Kind::Toward as usize] = 90;
        let s = r.line("she attacked a champion");
        assert!(s.starts_with("1.5s from t=0:42, ended: she attacked a champion | orders [toward 100%]"), "{s}");
        assert!(s.contains("league_varus 54k -> 50-55k | hp 40% | Q cooling W cooling | nearest enemy tower none"), "{s}");
    }
}
