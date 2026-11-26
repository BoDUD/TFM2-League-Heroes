//! 海克斯大乱斗（用户 2026-11-26：「分析一下这个项目能做海克斯乱斗那种模式对局里选海克斯吗」「海克斯可以让玩家自己选 AI就自动选」
//! 「这游戏最高等级都没15级吧」→ 方案的第 1 步「规则 + AI 自动选 + 20 个属性类海克斯 + 文字卡」）。单独的 mod，模组列表里开关。
//!
//! - **规则**（[`rules`]）：每个英雄一局 4 次选择：开局、6 级、9 级、12 级（本游戏最高 12 级；第 10 分钟还没拿满的补齐，
//!   [`settings`] 可改）。每次 3 张卡，每张能刷新一次（同一档），三选一。档位（银 / 金 / 棱彩）每次随机、全场同一档，前两次不会
//!   都是银；同一个人不拿重复的。随机全按模拟的种子：同一小局的两份预演和屏幕上那份选得一模一样。
//! - **谁来选**：第 1 步全员由 AI 选（[`rules::choose`]）：按英雄的分类和标签（[`kit`]）、拿过的、当时的比分打分，分低的卡先刷新
//!   一次再选。玩家自己给自己的队伍选（BP 阶段）是第 2 步。
//! - **效果**（[`augments`]）：0.1.0 的 20 个都是属性：拿到时给英雄挂一个永久 buff（`league_hextech_a:<key>`），复活（新实体）后补上。
//!   0.3.0（第 3 步）加 27 个触发类（[`procs`]：打中、放技能、参与击杀、残血、控住敌人、定时），每 [`procs::EVERY`] tick 看一次场上；
//!   战场特效（[`fx`]，画法 [`world`]）、身体变大（[`hd`]）只在屏幕上。都只加效果，不碰 AI 的走位和出手。
//!
//! 每份模拟的状态按 `SIM_TAG`（`league_hextech_sim:<编号>`，挂在两边的水晶上，水晶不收时挂在防御塔上；league.dll 的分叉校验
//! 不看带 `_sim:` 的 buff）各记各的，照大小龙的做法：服务器同一局并排跑两份预演，种子、来历、实体编号全都一样，只按这些记会串。
//! 玩法只读模拟、只按模拟的 tick 和种子（还有加载时读一次的设置、进生涯时填一次的英雄特性表），预演和画面一样。
//!
//! 屏幕（[`screen`]）：屏幕放的那场模拟里每次选择、每次触发记一条（[`feed`]，模拟从来不读它），客户端扩展按屏幕上的比赛时钟到了
//! 那一刻画。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_hextech.log`，每次启动游戏重写，上一次的留在 .prev.log。屏幕上那一场
//! 每行都记，预演、后台比赛每种前 40 行、之后每 100 行一行：`MATCH`（档位、每人的特性）、`PICK`、`KEEP`（复活后补回）、`PROC`
//! （触发类海克斯出效果，屏幕那一场前 80 行、之后每 40 行一行）、`END`（每个人拿了什么、每种触发了几次）；`PERF` 每 100 份模拟
//! 一行（钩子一共花了多少时间：过日快不快就看它）；`FX`、`WORLD`（特效第一次画出来、比赛世界认出来没有）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};
use std::time::Instant;

use mod_api_stable::*;

pub mod augments;
pub mod bp;
pub mod feed;
pub mod fx;
pub mod fx_atlas;
pub mod hd;
pub mod kit;
pub mod kj;
pub mod pending;
pub mod procs;
pub mod rules;
pub mod screen;
pub mod settings;
pub mod words;
pub mod world;

use augments::{Ev, Tier, Traits, AUGS};
use rules::{Rng, Screen, SCREENS};

const ID: &str = "league_hextech";
/// 本包的版本（mod.mod_info 的）：和大小龙一样，league_addons 的 build.rs 给每个 league_* 文件夹 ADDON_VERSION_<id>
/// （合集的测试 every_add_on_prints_its_own_version 认这个写法），单独编译时用 Cargo 的。
const VERSION: &str = match option_env!("ADDON_VERSION_league_hextech") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 这份模拟的编号，挂在水晶和防御塔上。
pub const SIM_TAG: &str = "league_hextech_sim:";

/// 状态最多留这么多份（最久没跑的先丢）。
const MOST: usize = 512;
/// 开局后这么久以内找不到水晶和塔：过一会儿再找，不记日志；过了才按 `RETRY` 找、记 `NO ANCHOR`。
const LATE: usize = 120;
const RETRY: usize = 600;
/// 每这么多 tick 看一次等级（选海克斯晚不了 1/6 秒）。
pub const STEP: usize = 10;
/// 开局那一次在第几 tick 选（开场第 0 tick 读到的血量是 0，等英雄站好）。
pub const OPEN_AT: usize = 30;
/// 多久对一次英雄身上的海克斯 buff（复活是新的实体，buff 要补）。
const KEEP_EVERY: usize = 30;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_HEXTECH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_hextech.log");
        }
    }
    PathBuf::from("league_hextech.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    if cfg!(test) {
        return;
    }
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || n.is_multiple_of(LOG_EVERY)).then_some(*n)
}

/// 屏幕上那一场每行都记，别的（预演、后台比赛）限条数。
fn say(screen: bool, kind: &'static str, line: String) {
    if screen {
        wlog(line);
    } else if let Some(k) = counted(kind) {
        wlog(format!("{line} #{k}"));
    }
}

fn kind_name(kind: u32) -> &'static str {
    match SimOriginKindV1::from_code(kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    }
}

fn head(sim: &StableSim<'_>) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{} m={} s={}] t={}", kind_name(o.kind), m(o.match_id), m(o.set_index), sim.tick())
}

/// 屏幕放的那些模拟（自己的比赛、观战、回放）：它们的事进 [`feed`]。
fn screen_of(o: &SimOriginV1) -> Option<(u64, u64)> {
    matches!(SimOriginKindV1::from_code(o.kind),
        Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay))
        .then_some((o.match_id, o.set_index))
}

fn side(team: usize) -> &'static str {
    if team == 0 {
        "blue"
    } else {
        "red"
    }
}

// ===================== 每份模拟的编号和状态 =====================

/// (种类, 比赛, 局, 回放, 种子)：并排的两份预演一样，所以只用来缩小范围，最后认挂着的编号。
type Origin = (u32, u64, u64, u64, u64);
/// 同来历的一份：(编号, 挂编号的水晶 / 塔, 上次在哪个实体的第几个 buff 找到)。
type Cand = (u64, Vec<usize>, Option<(usize, usize)>);

pub fn tag(no: u64) -> String {
    format!("{SIM_TAG}{no}")
}

pub fn parse_tag(buff: &str) -> Option<u64> {
    buff.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())
}

/// 这份模拟在 `id` 身上挂的编号和它在 buff 表里的位置。
fn tag_on(sim: &StableSim<'_>, id: usize) -> Option<(u64, usize)> {
    let e = sim.get_entity(id)?;
    (0..e.buff_count()).find_map(|i| e.buff_at(i).and_then(|b| parse_tag(b.name())).map(|no| (no, i)))
}

fn buff_name_at(sim: &StableSim<'_>, id: usize, i: usize) -> Option<String> {
    sim.get_entity(id)?.buff_at(i).map(|b| b.name().to_string())
}

/// 挂编号的地方：(水晶, 防御塔)，水晶不收 buff 时才挂到塔上。
fn anchors(sim: &StableSim<'_>) -> (Vec<usize>, Vec<usize>) {
    let mut nexus = Vec::new();
    for i in 0..sim.entity_count() {
        if let Some(e) = sim.entity_at(i) {
            if matches!(e.kind(), Some(EntityKindV1::Nexus)) && e.is_alive() {
                nexus.push(e.id());
            }
        }
    }
    let towers = (0..sim.tower_count())
        .map(|i| sim.tower_id_at(i))
        .filter(|id| !nexus.contains(id) && sim.get_entity(*id).is_some_and(|e| e.is_alive()))
        .collect();
    (nexus, towers)
}

#[derive(Default)]
struct Book {
    sims: HashMap<u64, Sim>,
    by_origin: HashMap<Origin, Vec<u64>>,
}

static BOOK: LazyLock<Mutex<Book>> = LazyLock::new(|| Mutex::new(Book::default()));
static NEXT: AtomicU64 = AtomicU64::new(1);
static STAMP: AtomicU64 = AtomicU64::new(1);
/// 来历 -> 到这一 tick 前不再找（没有水晶和塔：每 `RETRY` tick 再找；挂不上去：usize::MAX，这份不跑）。
static WAIT: LazyLock<Mutex<HashMap<Origin, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// 还在等（挂不上去：一直等；差不到 `RETRY` 的：这份；更早的 tick 是同来历的另一份模拟，自己找自己的）。
fn waiting(until: usize, now: usize) -> bool {
    until == usize::MAX || (now < until && until - now <= RETRY)
}

fn wait(origin: Origin, until: usize) {
    let mut w = WAIT.lock().unwrap_or_else(|e| e.into_inner());
    if w.len() > 4 * MOST {
        w.clear();
    }
    w.insert(origin, until);
}

/// 这份模拟的编号：先看同来历的那些编号挂在不在它们的水晶 / 塔上（上次的位置先看，一次就中）；都不在就在这份模拟里找水晶
/// 和塔，有编号用它（状态丢了：从头再排座位，身上的海克斯从 buff 读回来），没有就抽一个新的挂上。
fn find(sim: &mut StableSim<'_>, origin: Origin) -> Option<u64> {
    let now = sim.tick();
    let cands: Vec<Cand> = {
        let book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
        book.by_origin
            .get(&origin)
            .map(|v| v.iter().filter_map(|no| book.sims.get(no).map(|s| (*no, s.anchors.clone(), s.hint))).collect())
            .unwrap_or_default()
    };
    for (no, _, hint) in &cands {
        if let Some((a, i)) = hint {
            if buff_name_at(sim, *a, *i).is_some_and(|n| parse_tag(&n) == Some(*no)) {
                return Some(*no);
            }
        }
    }
    for (no, anchors, _) in &cands {
        for &a in anchors {
            if let Some((n, i)) = tag_on(sim, a) {
                if n == *no {
                    if let Some(s) = BOOK.lock().unwrap_or_else(|e| e.into_inner()).sims.get_mut(no) {
                        s.hint = Some((a, i));
                    }
                    return Some(*no);
                }
            }
        }
    }
    if WAIT.lock().unwrap_or_else(|e| e.into_inner()).get(&origin).is_some_and(|&until| waiting(until, now)) {
        return None;
    }
    let (nexus, towers) = anchors(sim);
    let all: Vec<usize> = nexus.iter().chain(&towers).copied().collect();
    if all.is_empty() {
        if now < LATE {
            return None;
        }
        wait(origin, now + RETRY);
        if let Some(k) = counted("no anchor") {
            wlog(format!("{} NO ANCHOR: no nexus and no tower to number this simulation - no augments, again in {RETRY} \
                          ticks #{k}", head(sim)));
        }
        return None;
    }
    let (no, fresh) = match all.iter().find_map(|&a| tag_on(sim, a)) {
        Some((no, _)) => (no, false),
        None => (NEXT.fetch_add(1, Ordering::Relaxed), true),
    };
    let mut anchors: Vec<usize> = all.iter().copied().filter(|&a| tag_on(sim, a).is_some_and(|t| t.0 == no)).collect();
    if fresh {
        for group in [&nexus, &towers] {
            for &a in group.iter() {
                sim.add_buff(a, &BuffV1::named(&tag(no)));
            }
            anchors = all.iter().copied().filter(|&a| tag_on(sim, a).is_some_and(|t| t.0 == no)).collect();
            if !anchors.is_empty() {
                break;
            }
        }
        if anchors.is_empty() {
            wait(origin, usize::MAX);
            if let Some(k) = counted("refused") {
                wlog(format!("{} TAG REFUSED: none of {} nexus / towers took the buff - no augments in this simulation #{k}",
                             head(sim), all.len()));
            }
            return None;
        }
    }
    let hint = anchors.first().and_then(|&a| tag_on(sim, a).map(|t| (a, t.1)));
    let seed = sim.seed();
    let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    let made = !book.sims.contains_key(&no);
    let s = book.sims.entry(no).or_insert_with(|| Sim::new(no, origin, seed, !fresh));
    s.hint = hint;
    s.anchors = anchors;
    let ids = book.by_origin.entry(origin).or_default();
    if !ids.contains(&no) {
        ids.push(no);
    }
    if made {
        evict(&mut book);
        perf_sim(origin.0);
    }
    Some(no)
}

/// 超过 `MOST` 份时丢掉最久没跑的那些（打完的、没跑完就扔了的预演）。
fn evict(book: &mut Book) {
    while book.sims.len() > MOST {
        let Some(old) = book.sims.values().min_by_key(|s| s.stamp).map(|s| s.no) else { break };
        if let Some(s) = book.sims.remove(&old) {
            if let Some(v) = book.by_origin.get_mut(&s.origin) {
                v.retain(|&n| n != old);
                if v.is_empty() {
                    book.by_origin.remove(&s.origin);
                }
            }
        }
    }
}

// ===================== 花了多少时间 =====================

struct Perf {
    /// 一共多少份模拟（按来历的种类）、钩子一共跑了几次、花了多少纳秒
    sims: [u64; 6],
    calls: u64,
    ns: u128,
}

static PERF: Mutex<Perf> = Mutex::new(Perf { sims: [0; 6], calls: 0, ns: 0 });
/// 每多少份模拟记一行 PERF。
const PERF_EVERY: u64 = 100;

fn perf_sim(kind: u32) {
    let Ok(mut p) = PERF.lock() else { return };
    p.sims[(kind as usize).min(5)] += 1;
    let total: u64 = p.sims.iter().sum();
    if total.is_multiple_of(PERF_EVERY) {
        let (calls, ns) = (p.calls.max(1), p.ns);
        wlog(format!("PERF {total} simulations so far (presim {}, view {}, spectate {}, replay {}, other {}): the hook ran \
                      {} times for {:.1} ms in all - {:.2} µs a run, {:.2} ms a simulation",
                     p.sims[1], p.sims[2], p.sims[3], p.sims[4], p.sims[0] + p.sims[5], p.calls, ns as f64 / 1e6,
                     ns as f64 / 1e3 / calls as f64, ns as f64 / 1e6 / total as f64));
    }
}

fn perf_add(ns: u128) {
    if let Ok(mut p) = PERF.lock() {
        p.calls += 1;
        p.ns += ns;
    }
}

// ===================== 一份模拟 =====================

#[derive(Clone, Debug)]
struct Seat {
    player: usize,
    team: usize,
    lane: u8,
    name: String,
    traits: Traits,
    by_kit: bool,
}

#[derive(Clone, Debug, Default)]
struct Pl {
    /// 选过几次
    done: usize,
    /// 拿到的海克斯（编号）
    taken: Vec<usize>,
    /// 上次对 buff 时他的英雄实体（变了就是复活了或换了身体）
    ent: Option<usize>,
}

struct Sim {
    no: u64,
    origin: Origin,
    stamp: u64,
    seed: u64,
    /// 找到时这份模拟已经有编号了（本包的状态丢过：身上的海克斯从 buff 读回来）
    late: bool,
    anchors: Vec<usize>,
    hint: Option<(usize, usize)>,
    tiers: [Tier; SCREENS],
    seats: Vec<Seat>,
    pls: Vec<Pl>,
    keep_at: usize,
    ended: bool,
    /// 玩家在 BP 阶段给自己队伍选的（这一局对得上的那份记录，排座位时抄一份）
    user: Option<pending::Record>,
    /// 触发类海克斯（0.3.0）：每个座位是谁、日志里的名字、拿着哪几种（[`Ev::bit`] 的位）、它们的状态
    whos: Vec<procs::Who>,
    names: Vec<String>,
    held: Vec<augments::EvSet>,
    procs: procs::Procs,
    /// 这一份的签名（[`run_sig`]，0.5.1）：屏幕上的这一局现在放的不是这一份时，它不往屏幕上记东西
    sig: u64,
}

impl Sim {
    fn new(no: u64, origin: Origin, seed: u64, late: bool) -> Sim {
        Sim { no, origin, stamp: 0, seed, late, anchors: Vec::new(), hint: None,
              tiers: rules::tiers(seed, settings::get().weights), seats: Vec::new(), pls: Vec::new(), keep_at: 0,
              ended: false, user: None, whos: Vec::new(), names: Vec::new(), held: Vec::new(),
              procs: procs::Procs::default(), sig: 0 }
    }

    /// 玩家给这个座位第 `k` 次选的，和这个英雄按没按「确定」（不是玩家那边、记录里没有这个英雄、拿过了：None，AI 选）。
    fn user_pick(&self, i: usize, k: usize) -> Option<(pending::Choice, bool)> {
        let rec = self.user.as_ref()?;
        let seat = &self.seats[i];
        if seat.team != rec.side {
            return None;
        }
        let m = rec.mine_of(&seat.name)?;
        let c = m.picks.get(k)?.clone();
        (!self.pls[i].taken.contains(&(c.chosen as usize))).then_some((c, m.confirmed))
    }

    fn who(&self, i: usize) -> String {
        self.seats.get(i).map_or_else(|| format!("seat{i}"), |s| {
            format!("{}(p{} {} lane{})", s.name.trim_start_matches("league_"), s.player, side(s.team), s.lane)
        })
    }

    /// 排座位：每个玩家的队伍、分路、英雄，抄一份特性。玩家还没齐、英雄还没出来：下次再排。
    fn seat(&mut self, sim: &StableSim<'_>, screen: Option<(u64, u64)>) -> bool {
        let n = sim.player_count();
        if n == 0 {
            return false;
        }
        let mut seats = Vec::with_capacity(n);
        for i in 0..n {
            let Some(p) = sim.player_at(i) else { return false };
            let Some(name) = p.champion().and_then(|c| c.name()) else { return false };
            let lane = p.lane();
            let k = kit::get(&name);
            let (traits, by_kit) = kit::traits(k.as_ref(), lane);
            seats.push(Seat { player: p.id(), team: p.team().min(1), lane: lane.map_or(i % 5, |l| l.code() as usize) as u8,
                              name, traits, by_kit });
        }
        self.pls = vec![Pl::default(); seats.len()];
        self.seats = seats;
        self.whos = self.seats.iter()
            .map(|s| procs::Who { player: s.player, team: s.team, lane: s.lane, ranged: !melee(&s.traits), traits: s.traits })
            .collect();
        self.names = (0..self.seats.len()).map(|i| self.who(i)).collect();
        self.held = vec![0; self.seats.len()];
        // 玩家在 BP 阶段选过的：按两边的英雄认这一局（预演只知道比赛，屏幕上的知道第几局）
        let names = |team: usize| -> Vec<String> {
            self.seats.iter().filter(|s| s.team == team).map(|s| s.name.clone()).collect()
        };
        let o = sim.sim_origin().unwrap_or_default();
        let m = (o.match_id != SimOriginV1::NONE).then_some(o.match_id);
        if let Some(rec) = pending::for_sim(&names(0), &names(1), m, screen) {
            self.tiers = rec.tiers;
            say(screen.is_some(), "user", format!("{} USER sim #{} uses the pick screen's record #{}: the player is {}, {} \
                                                   heroes, {} with picks of the player's own",
                                                  head(sim), self.no, rec.id, side(rec.side), rec.mine.len(), rec.touched()));
            self.user = Some(rec);
        }
        if self.late {
            self.restore(sim);
        }
        self.sig = run_sig(self.seed, &self.tiers, &self.seats);
        if let Some((m, s)) = screen {
            if feed::run(m, s, self.sig, sim.tick()) {
                say(true, "run", format!("{} RUN sim #{} m={m} s={s}: another match under the same match / set number - the                                           screen's notes of the old one dropped", head(sim), self.no));
            }
            feed::tiers(m, s, self.tiers);
        }
        let tiers: Vec<&str> = self.tiers.iter().map(|t| t.key()).collect();
        let people: Vec<String> = (0..self.seats.len())
            .map(|i| format!("{} [{}{}]", self.who(i), kit::short(&self.seats[i].traits),
                             if self.seats[i].by_kit { "" } else { " by lane" }))
            .collect();
        say(screen.is_some(), "match", format!("{} MATCH sim #{} tiers {}{}; {}", head(sim), self.no, tiers.join(" / "),
                                               if self.late { " (late: picks read back from the buffs)" } else { "" },
                                               people.join("; ")));
        true
    }

    /// 本包的状态丢过（找到的模拟已经挂着编号）：每个人拿过的海克斯从他身上的 buff 读回来。
    fn restore(&mut self, sim: &StableSim<'_>) {
        for (i, seat) in self.seats.iter().enumerate() {
            let Some(e) = sim.get_player(seat.player).and_then(|p| p.champion()) else { continue };
            let taken: Vec<usize> =
                (0..e.buff_count()).filter_map(|j| e.buff_at(j).and_then(|b| augments::of_buff(b.name()))).collect();
            self.pls[i].done = taken.len().min(SCREENS);
            self.held[i] = taken.iter().fold(0, |h, &a| h | ev_bit(a));
            // 0.5.0：技能海克斯选的技能（玩家选过的照记录，别的 AI 默认）
            for (k, &a) in taken.iter().enumerate() {
                let slot = self.user.as_ref()
                    .and_then(|r| r.mine_of(&seat.name))
                    .and_then(|m| m.picks.iter().find(|c| c.chosen as usize == a))
                    .map_or(0, |c| c.slot);
                self.procs.picked(i, AUGS[a].ev, k.min(SCREENS - 1), slot);
            }
            self.pls[i].taken = taken;
        }
    }

    fn step(&mut self, sim: &mut StableSim<'_>, screen: Option<(u64, u64)>) {
        let now = sim.tick();
        if self.seats.is_empty() && !self.seat(sim, screen) {
            return;
        }
        // 屏幕上这一局放的已经是别的一份（编号重复的另一场、读档重打）：这一份当预演跑，不往屏幕上记
        let screen = screen.filter(|&(m, s)| feed::is_current(m, s, self.sig));
        // 选海克斯、对 buff：每 STEP tick 一次（和 0.2 一样的时刻）
        if now.is_multiple_of(STEP) {
            let s = settings::get();
            for i in 0..self.seats.len() {
                self.picks_due(sim, i, now, &s, screen);
            }
            if now >= self.keep_at {
                self.keep_at = now + KEEP_EVERY;
                self.keep(sim, screen);
            }
        }
        // 触发类：每 procs::EVERY tick 一次
        if now.is_multiple_of(procs::EVERY) {
            self.procs.step(sim, now, &self.whos, &self.held, &self.names, screen.is_some());
            for line in std::mem::take(&mut self.procs.log) {
                wlog(format!("{} {line}", head(sim)));
            }
            let out = std::mem::take(&mut self.procs.out);
            if let Some((m, s)) = screen {
                for o in out {
                    feed::fx(feed::Fx { m, s, tick: o.tick, show: o.show, at: o.at, to: o.to, dur: o.dur });
                }
            }
        }
        if sim.is_end() && !self.ended {
            self.ended = true;
            self.end(sim, screen);
        }
    }

    /// 这个人该选了的都选掉（一般一次一个；补齐的那一分钟可能一次几个）。
    fn picks_due(&mut self, sim: &mut StableSim<'_>, i: usize, now: usize, s: &settings::Settings,
                 screen: Option<(u64, u64)>) {
        let (player, team) = (self.seats[i].player, self.seats[i].team);
        let Some(level) = sim.get_player(player).map(|p| p.level()) else { return };
        while self.pls[i].done < SCREENS && settings::due(s, self.pls[i].done, level, now) {
            let k = self.pls[i].done;
            let blue = sim.score_diff(0);
            let mood = rules::mood(if team == 0 { blue } else { -blue });
            // 玩家在 BP 阶段选的就用它（by：2 玩家点的或按了确定的、1 面板上没动的 AI 推荐），不然 AI 在这一刻选（by 0）
            let (pick, by, slot) = match self.user_pick(i, k) {
                Some((c, confirmed)) => {
                    let u = |a: [u16; 3]| [a[0] as usize, a[1] as usize, a[2] as usize];
                    let rerolled = [c.cards[0] != c.first[0], c.cards[1] != c.first[1], c.cards[2] != c.first[2]];
                    (Screen { tier: self.tiers[k], first: u(c.first), rerolled, cards: u(c.cards), scores: [0.0; 3],
                              chosen: c.chosen as usize },
                     if c.by_user || confirmed { 2 } else { 1 }, c.slot)
                }
                None => {
                    let mut rng = Rng::new(rules::pick_seed(self.seed, i, k));
                    let Some(p) = rules::choose(&self.seats[i].traits, &self.pls[i].taken, mood, &mut rng, self.tiers[k]) else {
                        self.pls[i].done = SCREENS;
                        say(screen.is_some(), "dry", format!("{} DRY {}: no card left to deal", head(sim), self.who(i)));
                        return;
                    };
                    (p, 0, 0)
                }
            };
            self.pls[i].taken.push(pick.chosen);
            self.pls[i].done += 1;
            self.held[i] |= ev_bit(pick.chosen);
            let ev = AUGS[pick.chosen].ev;
            self.procs.picked(i, ev, k, slot);
            let shown_slot = if augments::skill_aug(ev) { self.procs.slot_of(i, ev) } else { 0 };
            let on = self.put_on(sim, i, pick.chosen);
            // 歌利亚巨人一拿到就变大：脚下放一圈「长大」
            if on && AUGS[pick.chosen].ev == Ev::Goliath {
                if let (Some((m, sx)), Some(e)) = (screen, sim.get_player(player).and_then(|p| p.champion())) {
                    feed::fx(feed::Fx { m, s: sx, tick: now, show: procs::Show::Grow, at: e.pos(), to: Vec::new(), dur: 0 });
                }
            }
            self.log_pick(sim, i, k, level, mood, &pick, by, on, screen);
            if let Some((m, sx)) = screen {
                let c = |a: [usize; 3]| [a[0] as u16, a[1] as u16, a[2] as u16];
                feed::push(feed::Event {
                    m,
                    s: sx,
                    tick: now,
                    pick: feed::Pick { team, lane: self.seats[i].lane, hero: self.seats[i].name.clone(), screen: k as u8,
                                       level: level.min(255) as u8, tier: pick.tier, cards: c(pick.cards),
                                       first: c(pick.first), chosen: pick.chosen as u16, by, slot: shown_slot },
                });
            }
            if augments::meta_aug(ev) {
                self.transmute(sim, i, k, &pick, level, screen);
            }
        }
    }

    /// 质变：混沌 / 质变：棱彩阶 / 潘朵拉的盒子（0.5.0）：拿到的那一刻按种子随机给海克斯（不给这一次的另外两张、拿过的、它们自己
    /// 这几种）；潘朵拉还把之前的换成随机的棱彩（摘掉 buff、清掉状态）。屏幕上：得到的记 by 3，换掉的记 by 4。
    #[allow(clippy::too_many_arguments)]
    fn transmute(&mut self, sim: &mut StableSim<'_>, i: usize, k: usize, pick: &Screen, level: usize,
                 screen: Option<(u64, u64)>) {
        let ev = AUGS[pick.chosen].ev;
        let mut rng = Rng::new(rules::splitmix(self.seed ^ TRANSMUTE_SALT ^ ((i as u64) << 8) ^ k as u64));
        let mut avoid: Vec<usize> = self.pls[i].taken.clone();
        avoid.extend(pick.cards);
        let old: Vec<usize> = self.pls[i].taken.iter().copied().filter(|&a| a != pick.chosen).collect();
        let (n, tier, lost) = match ev {
            Ev::TransmuteChaos => (2, None, Vec::new()),
            Ev::TransmutePrismatic => (1, Some(Tier::Prismatic), Vec::new()),
            _ => (old.len() + 1, Some(Tier::Prismatic), old),
        };
        let mut gained = Vec::new();
        for _ in 0..n {
            if let Some(a) = rules::random_aug(&mut rng, tier, &avoid) {
                avoid.push(a);
                gained.push(a);
            }
        }
        let ent = sim.get_player(self.seats[i].player).and_then(|p| p.champion()).map(|e| e.id());
        for &a in &lost {
            self.pls[i].taken.retain(|&x| x != a);
            if let Some(e) = ent {
                sim.entity_remove_buff(e, &augments::buff_name(a));
            }
            self.procs.forget(sim, i, ent, AUGS[a].ev);
        }
        for &a in &gained {
            self.pls[i].taken.push(a);
            self.put_on(sim, i, a);
            self.procs.picked(i, AUGS[a].ev, k, 0);
        }
        self.held[i] = self.pls[i].taken.iter().fold(0, |h, &a| h | ev_bit(a));
        let keys = |v: &[usize]| v.iter().map(|&a| AUGS[a].key).collect::<Vec<_>>().join(", ");
        say(screen.is_some(), "pick", format!("{} TRANSMUTE {} {}: gained [{}], lost [{}]", head(sim), self.who(i),
                                              AUGS[pick.chosen].key, keys(&gained), keys(&lost)));
        if let Some((m, sx)) = screen {
            let (team, lane, hero) = (self.seats[i].team, self.seats[i].lane, self.seats[i].name.clone());
            let now = sim.tick();
            for (list, by) in [(&lost, 4u8), (&gained, 3u8)] {
                for &a in list.iter() {
                    let slot = if augments::skill_aug(AUGS[a].ev) { self.procs.slot_of(i, AUGS[a].ev) } else { 0 };
                    feed::push(feed::Event {
                        m,
                        s: sx,
                        tick: now,
                        pick: feed::Pick { team, lane, hero: hero.clone(), screen: k as u8, level: level.min(255) as u8,
                                           tier: AUGS[a].tier, cards: [a as u16; 3], first: [a as u16; 3], chosen: a as u16, by,
                                           slot },
                    });
                }
            }
        }
    }

    /// 给他现在的英雄挂上这个海克斯（死着的、还没出来的：下次对 buff 时补）。-> 挂上了没有
    fn put_on(&mut self, sim: &mut StableSim<'_>, i: usize, aug: usize) -> bool {
        let Some(e) = sim.get_player(self.seats[i].player).and_then(|p| p.champion()) else { return false };
        if !e.is_alive() {
            return false;
        }
        let id = e.id();
        let name = augments::buff_name(aug);
        let have = (0..e.buff_count()).filter_map(|j| e.buff_at(j)).filter(|b| b.name() == name).count();
        if have == 0 {
            sim.add_buff(id, &augments::buff_for(aug, melee(&self.seats[i].traits)));
        }
        self.pls[i].ent = Some(id);
        true
    }

    #[allow(clippy::too_many_arguments)]
    fn log_pick(&self, sim: &StableSim<'_>, i: usize, k: usize, level: usize, mood: f32, p: &Screen, by: u8, on: bool,
                screen: Option<(u64, u64)>) {
        let cards: Vec<String> = (0..3)
            .map(|c| {
                let r = if p.rerolled[c] { format!("{}->", AUGS[p.first[c]].key) } else { String::new() };
                format!("{r}{} {:.2}", AUGS[p.cards[c]].key, p.scores[c])
            })
            .collect();
        let who = match by {
            2 => " by the player",
            1 => " by the pick screen's AI default",
            _ => "",
        };
        say(screen.is_some(), "pick", format!("{} PICK {} #{} at level {level} ({:?}, mood {mood:+.2}): {} -> {}{who}{}",
                                              head(sim), self.who(i), k + 1, p.tier, cards.join(", "),
                                              AUGS[p.chosen].key, if on { "" } else { " (dead: put on at respawn)" }));
    }

    /// 每个人现在的英雄身上，他拿过的海克斯每个正好一份（复活是新的实体：补上；多出来的：去掉多的）。
    fn keep(&mut self, sim: &mut StableSim<'_>, screen: Option<(u64, u64)>) {
        for i in 0..self.seats.len() {
            if self.pls[i].taken.is_empty() {
                continue;
            }
            let Some(e) = sim.get_player(self.seats[i].player).and_then(|p| p.champion()) else { continue };
            if !e.is_alive() {
                continue;
            }
            let id = e.id();
            let names: Vec<String> = (0..e.buff_count()).filter_map(|j| e.buff_at(j)).map(|b| b.name().to_string()).collect();
            let mut added = Vec::new();
            for &a in &self.pls[i].taken {
                let name = augments::buff_name(a);
                let n = names.iter().filter(|x| **x == name).count();
                if n == 1 {
                    continue;
                }
                if n > 1 {
                    sim.entity_remove_buff(id, &name);
                }
                sim.add_buff(id, &augments::buff_for(a, melee(&self.seats[i].traits)));
                added.push(AUGS[a].key);
            }
            let moved = self.pls[i].ent.is_some_and(|old| old != id);
            self.pls[i].ent = Some(id);
            if !added.is_empty() {
                say(screen.is_some(), "keep", format!("{} KEEP {}: {} put back on #{id}{}", head(sim), self.who(i),
                                                      added.join(", "), if moved { " (respawned)" } else { "" }));
            }
        }
    }

    fn end(&self, sim: &StableSim<'_>, screen: Option<(u64, u64)>) {
        let o = sim.sim_origin().unwrap_or_default();
        let rows: Vec<String> = (0..self.seats.len())
            .map(|i| {
                let keys: Vec<&str> = self.pls[i].taken.iter().map(|&a| AUGS[a].key).collect();
                format!("{}: {}", self.who(i), if keys.is_empty() { "-".into() } else { keys.join(" ") })
            })
            .collect();
        say(screen.is_some(), "end", format!("{} END sim #{} ({}): {}; procs: {}", head(sim), self.no, kind_name(o.kind),
                                             rows.join("; "), self.procs.summary()));
        if let Some((m, s)) = screen {
            feed::ended(m, s, sim.tick());
        }
    }
}

/// 近战英雄（0.4.0：射程类海克斯给近战的那个数；玻璃大炮、事不过三按近战 / 远程）。
fn melee(t: &augments::Traits) -> bool {
    t.melee >= t.ranged
}

/// 这个海克斯是不是触发类：是的话它那一种的位（[`Ev::bit`]），不是 0。
/// 屏幕上这一局是哪一份（[`feed::run`]，0.5.1）：种子、4 次的档位、每个座位的队伍 / 分路 / 英雄。游戏自己把同一局再跑一遍、
/// 回放：一样；读档重打、编号重复的另一场比赛：不一样。
fn run_sig(seed: u64, tiers: &[Tier; SCREENS], seats: &[Seat]) -> u64 {
    let mut h = rules::splitmix(seed ^ RUN_SALT);
    for t in tiers {
        h = rules::splitmix(h ^ t.code() as u64);
    }
    for s in seats {
        h = rules::splitmix(h ^ ((s.team as u64) << 8) ^ s.lane as u64);
        for b in s.name.bytes() {
            h = rules::splitmix(h ^ b as u64);
        }
    }
    h
}
const RUN_SALT: u64 = 0x7275_6e73_6967_0051;

/// 质变、潘朵拉随机给海克斯的种子。
const TRANSMUTE_SALT: u64 = 0x7472_616e_736d_0005;

fn ev_bit(aug: usize) -> augments::EvSet {
    AUGS.get(aug).filter(|a| a.ev != Ev::Stat).map_or(0, |a| a.ev.bit())
}

fn run(sim: &mut StableSim<'_>) {
    let now = sim.tick();
    if !now.is_multiple_of(procs::EVERY) && !sim.is_end() {
        return;
    }
    let started = Instant::now();
    let o = sim.sim_origin().unwrap_or_default();
    let origin: Origin = (o.kind, o.match_id, o.set_index, o.replay_id, sim.seed());
    let screen = screen_of(&o);
    if let Some((m, s)) = screen {
        if feed::view(m, s) {
            if let Some(k) = counted("view") {
                wlog(format!("VIEW m={m} s={s} on screen #{k}"));
            }
        }
    }
    if let Some(no) = find(sim, origin) {
        // 跑的时候从表里拿出来（别的线程上的模拟同时能找自己的）
        let st = BOOK.lock().unwrap_or_else(|e| e.into_inner()).sims.remove(&no);
        if let Some(mut st) = st {
            st.stamp = STAMP.fetch_add(1, Ordering::Relaxed);
            if !st.ended {
                st.step(sim, screen);
            }
            BOOK.lock().unwrap_or_else(|e| e.into_inner()).sims.insert(no, st);
        }
    }
    perf_add(started.elapsed().as_nanos());
}

// ===================== 比赛钩子 =====================

/// 每份模拟每 tick 进来一次，每 [`STEP`] tick 干一次活。
pub struct Hextech;

impl StableMatchHook for Hextech {
    fn on_match_start(&self, sim: &mut StableSim<'_>) {
        run(sim);
    }

    fn on_match_tick(&self, sim: &mut StableSim<'_>, _rng_seed: u64) {
        run(sim);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!("=== {ID} v{VERSION} (Hextech Mayhem: four augment picks a champion - the start and levels 6 / 9 / 12, one \
                  of three with a reroll each, the tier the same for everyone; picked by the AI from the champion's class and \
                  tags, or by the player on the pick screen; {} augments: 20 stat ones and 27 that trigger, with battlefield effects) \
                  loaded: game {}.{}.{} abi {} log={} ===",
                 AUGS.len(), v.major, v.minor, v.patch, host.abi_level(), LOG_PATH.display()));
    wlog(settings::init(settings::dll_dir()));
    // 身体变大（歌利亚巨人、最终形态、坦克引擎）：高清帧引擎的通配变身行；显示钩子晚挂（第一帧再换槽）
    game_places::hook::defer();
    match hd_engine::start(&hd::table(), &format!("league_hextech.dll {VERSION}"), |m: &str| wlog(m)) {
        hd_engine::Role::Host => wlog("HD: bodies grown by the augments' buffs, hooked here (no pack DLL before this one)"),
        hd_engine::Role::Guest { host: by, .. } => wlog(format!("HD: bodies grown by the augments' buffs, drawn by {by}")),
        hd_engine::Role::Off(why) => wlog(format!("HD: no body grows - {why}")),
    }
    module.set_match_hook(Hextech);
    module.set_extension(screen::Overlay);
    module.add_draft_score_hook(kit::Watch);
    host.log(LogLevel::Info, "league_hextech loaded (Hextech Mayhem augments).");
}

fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod mock;

#[cfg(test)]
mod procs_tests;

#[cfg(test)]
pub(crate) mod tests;
