//! 英雄联盟的大小龙（用户 2026-11-09：订阅的创意工坊「Elemental Drakes & Baron」「没效果 不像lol 击杀后名字也不对」
//! 「改到完美 … 我要明显的感受到小龙有属性加成 大龙能加强兵线之类的 还有龙魂的效果 远古龙的斩杀」→ 做我们自己的，玩家关掉
//! 创意工坊那个）。本包是玩法那一半，全在一个比赛钩子里（[`Dragons`]，每份模拟每 tick 跑一次）；屏幕上的公告、HUD、名字、
//! 小龙的皮肤是画面那一半，读本包给的接口（README「给画面的接口」）。
//!
//! - **元素和刷新顺序**（英雄联盟的规矩，[`rules::order`]）：第一条随机，第二条随机且不同，第二条被拿下后峡谷变成第三种元素，
//!   之后到龙魂为止都是它。种子是模拟的种子：同一小局的预演和屏幕上的两遍都一样。小龙（游戏里的 `Serpen`，`serpen_jungle`）
//!   还是游戏自己刷的（时间也是游戏的规则设定），本包在它出生时挂上元素标记 `league_dragons_el_<元素>`。
//! - **每层亚龙**（整队、永久、叠加，死了复活补回）：炼狱攻击力法强 +8%，山脉双抗 +10%，海洋每 5 秒回 3% 已损生命，云端移速
//!   +8%，海克斯攻速 +10% 和技能冷却 -8%，化学科技韧性 +10% 和生命偷取 +3%。游戏自己的小龙 buff（`serpen_permanent_buff`，
//!   2027 赛季补丁后四项各 +4%、移速 +1%）每层都被中和掉：按英雄身上实际挂着的数值取负（`league_dragons_nat`），赛季补丁改了
//!   数也跟着。
//! - **龙魂**：第一个拿到 4 条元素亚龙的队伍拿到峡谷元素的龙魂（另一队之后再拿到 4 条也没有），之后每次刷新都是远古巨龙。
//!   炼狱：每 3 秒下一次伤害在目标身上爆炸；山脉：5 秒没挨打给护盾；海洋：打到英雄后 4 秒里回血；云端：移速 +15%，放大招后
//!   +50% 6 秒；海克斯：每 2.5 秒下一次命中放连锁闪电（减速）；化学科技：生命低于一半时韧性、伤害、减伤。
//! - **远古巨龙**：拿下它的一方当时活着的英雄 90 秒的远古龙之力（死了就没）：打英雄点燃（真实伤害），着火的英雄生命低于 20%
//!   被处决（击杀算处决他的人）。
//! - **纳什男爵**（游戏里的莫甘德，`Epic`）：拿下它的一方当时活着的英雄 120 秒的纳什男爵之手（死了就没）：攻击力法强 +20%，
//!   身边 140000 以内的己方小兵受到的伤害 -40%、攻击力 +30%（游戏自己给兵线的大龙 buff 照旧）。
//!
//! 谁拿下的：读每个玩家的统计 `serpen_secure` / `epic_secure`（游戏的数据，两队各加起来，哪队涨了就是哪队）；读不到时看游戏
//! 自己的小龙 buff 挂到了哪队身上，再不行看龙死时谁站在旁边。谁打到了谁：每 tick 读英雄的生命和护盾，掉了的敌方英雄在
//! 拿着效果的英雄 85000 以内，而他这一 tick 的统计 `deal`（打出的伤害）涨了（读不到统计时：他刚出过手）。
//!
//! 每份模拟的状态按 `SIM_TAG`（`league_dragons_sim:<编号>`，挂在两边的水晶上，水晶不收时挂在防御塔上；league.dll 的分叉校验
//! 不看带 `_sim:` 的 buff）记：服务器同一局并排跑两份预演，种子、来历、实体编号全都一样，只按这些记会串。玩法只读模拟、只按
//! 模拟的 tick 和种子，没有只在画面里走的分支、没有按 HashMap 顺序做的决定、没有墙上的时钟，预演和画面一模一样。
//!
//! 创意工坊的「Elemental Drakes & Baron」也开着时（水晶上有它的 `sed_*` 记录）本包什么都不做，记一行 `CONFLICT`，水晶上的状态
//! 记录带着冲突的标记、放一件 `C`（画面请玩家关掉它）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_dragons.log`，每次启动游戏重写，上一次的留在 .prev.log。屏幕上那一场
//! 每行都记，预演、后台比赛每种前 40 行、之后每 100 行一行：`MATCH`（顺序）、`SPAWN`（元素、实体名）、`KILL`、`SOUL`、`ELDER ON`
//! / `ELDER OFF` / `EXECUTE`、`BARON ON` / `BARON OFF` / `BOOST`（加强的小兵数）、`NEUTRALIZE`、`PROC`（龙魂）、`CONFLICT`、`END`。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod feed;
pub mod rules;
// 画面那一半（客户端扩展里画，只读 feed）：公告、HUD 和它们的字
pub mod hud;
pub mod notice;
pub mod screen;
pub mod words;

use rules::{Element, Ev, HoldRec, Record, DRAKES};

const ID: &str = "league_dragons";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_dragons") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 这份模拟的编号，挂在水晶和防御塔上（league.dll 的分叉校验不看带 `_sim:` 的 buff）。
pub const SIM_TAG: &str = "league_dragons_sim:";

/// 状态最多留这么多份（最久没跑的先丢）。
const MOST: usize = 512;
/// 开局后这么久以内找不到水晶和塔：下一 tick 再找，不记日志；过了才按 `RETRY` 找、记 `NO ANCHOR`（league_eggs 0.1.1）。
const LATE: usize = 120;
const RETRY: usize = 600;
/// 没有活着的小龙 / 纳什男爵时多久找一次。
const SCAN: usize = 10;
/// 龙死了以后最多等统计这么久，再按旁边站着谁算。
const PENDING_T: usize = 30;
/// 龙死时离它这么近的英雄算在场。
const NEAR: u64 = 80_000;
/// 拿着效果的英雄打得到这么远的敌方英雄（远程普攻 60000 加两个身体）。
const REACH: u64 = 85_000;
/// 读不到统计时：出手（冷却涨上去）后这么久里掉血的敌方英雄算他打的。
const ACTION_WINDOW: usize = 45;
/// 每个英雄身上本包的 buff 多久对一次（拿龙时马上对）。
const REFRESH: usize = 120;
/// 多久看一次每个玩家的英雄换没换（复活是新的实体）、死没死（拿着远古龙之力 / 纳什男爵之手的人死了就没了）；队伍的版本变了
/// 马上看。
const KEEP_EVERY: usize = 6;
/// 创意工坊那个 mod 的记录：开局 `CONFLICT_EARLY` tick 里每 30 tick 看一次水晶，之后每 600 tick。
const CONFLICT_EARLY: usize = 1_800;
/// 龙魂触发的日志一份模拟前这么多行、之后每这么多行一行。
const PROC_FIRST: usize = 30;
const PROC_EVERY: usize = 25;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_DRAGONS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_dragons.log");
        }
    }
    PathBuf::from("league_dragons.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// 屏幕上那一场每行都记，别的（预演、后台比赛）限条数。
fn say(screen: bool, kind: &'static str, line: String) {
    if screen {
        wlog(line);
    } else if let Some(k) = counted(kind) {
        wlog(format!("{line} #{k}"));
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
    format!("[{kind} m={} s={}] t={}", m(o.match_id), m(o.set_index), sim.tick())
}

/// 屏幕放的那些模拟（自己的比赛、观战、回放）：它们的事进 [`feed`]。
fn screen_of(o: &SimOriginV1) -> Option<(u64, u64)> {
    matches!(SimOriginKindV1::from_code(o.kind),
        Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay))
        .then_some((o.match_id, o.set_index))
}

const SIDE: [&str; 2] = ["blue", "red"];

fn side(team: usize) -> &'static str {
    SIDE[team.min(1)]
}

// ===================== 模拟里的小工具 =====================

fn buffs_on(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

/// 这个玩家现在的英雄（死了还没复活时是他的尸体）：(实体, 活着没有)。
fn champ_of(sim: &StableSim<'_>, player: usize) -> Option<(usize, bool)> {
    let e = sim.get_player(player)?.champion()?;
    Some((e.id(), e.is_alive()))
}

fn d2(a: (u64, u64), b: (u64, u64)) -> u64 {
    let (dx, dy) = (a.0.abs_diff(b.0), a.1.abs_diff(b.1));
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

/// 攻击力、法强（buff 算在内）。
fn ad_ap(sim: &StableSim<'_>, id: usize) -> (usize, usize) {
    sim.get_entity(id).map_or((0, 0), |e| {
        let s = e.stat();
        (s.attack, s.magic_power)
    })
}

/// 统计里的一个数（`12`、`12.0`）。
fn parse_num(s: &str) -> Option<u64> {
    let t = s.trim();
    t.parse::<u64>().ok().or_else(|| t.parse::<f64>().ok().filter(|v| v.is_finite() && *v >= 0.0).map(|v| v as u64))
}

/// 整份统计里 `"key":` 后面的数。
fn find_num(doc: &str, key: &str) -> Option<u64> {
    let at = doc.find(&format!("\"{key}\""))? + key.len() + 2;
    let rest = doc[at..].trim_start().strip_prefix(':')?.trim_start();
    let end = rest.find(|c: char| !(c.is_ascii_digit() || c == '.' || c == '-' || c == 'e' || c == 'E' || c == '+'))
        .unwrap_or(rest.len());
    parse_num(&rest[..end])
}

// ===================== 每份模拟的编号和状态 =====================

/// (种类, 比赛, 局, 回放, 种子)：并排的两份预演一样，所以只用来缩小范围，最后认挂着的编号。
type Origin = (u32, u64, u64, u64, u64);

pub fn tag(no: u64) -> String {
    format!("{SIM_TAG}{no}")
}

/// 一个 buff 名里的编号（不是本包的编号：None）。
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

/// Still waiting at `now` for `until`: refused for good (usize::MAX), or within `RETRY` ticks before it - a tick further
/// back is another simulation of the same origin (a presim twin, the view's second run), which looks for itself.
pub fn waiting(until: usize, now: usize) -> bool {
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
/// 和塔，有编号用它（状态丢了：从水晶上的状态记录重建），没有就抽一个新的挂上。
fn find(sim: &mut StableSim<'_>, origin: Origin) -> Option<u64> {
    let now = sim.tick();
    let cands: Vec<(u64, Vec<usize>, Option<(usize, usize)>)> = {
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
            wlog(format!("{} NO ANCHOR: no nexus and no tower to number this simulation - no drakes, again in {RETRY} ticks #{k}",
                         head(sim)));
        }
        return None;
    }
    let (no, fresh) = match all.iter().find_map(|&a| tag_on(sim, a)) {
        Some((no, _)) => (no, false),
        None => (NEXT.fetch_add(1, Ordering::Relaxed), true),
    };
    let mut anchors: Vec<usize> = all.iter().copied().filter(|&a| tag_on(sim, a).is_some_and(|t| t.0 == no)).collect();
    if fresh {
        // the nexuses; the towers only when no nexus takes it
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
                wlog(format!("{} TAG REFUSED: none of {} nexus / towers took the buff - no drakes in this simulation #{k}",
                             head(sim), all.len()));
            }
            return None;
        }
    }
    let late = !fresh;
    let hint = anchors.first().and_then(|&a| tag_on(sim, a).map(|t| (a, t.1)));
    let seed = sim.seed();
    let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    let made = !book.sims.contains_key(&no);
    let s = book.sims.entry(no).or_insert_with(|| Sim::new(no, origin, now, late, seed));
    s.hint = hint;
    s.anchors = anchors;
    s.nexus = nexus;
    let ids = book.by_origin.entry(origin).or_default();
    if !ids.contains(&no) {
        ids.push(no);
    }
    if made {
        evict(&mut book);
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

fn run(sim: &mut StableSim<'_>) {
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
    let Some(no) = find(sim, origin) else { return };
    // out of the book while it runs (another simulation on another thread can look its own up meanwhile)
    let Some(mut st) = BOOK.lock().unwrap_or_else(|e| e.into_inner()).sims.remove(&no) else { return };
    st.stamp = STAMP.fetch_add(1, Ordering::Relaxed);
    if !st.ended {
        st.step(sim, screen);
    }
    BOOK.lock().unwrap_or_else(|e| e.into_inner()).sims.insert(no, st);
}

// ===================== 一份模拟 =====================

#[derive(Clone, Debug)]
struct Seat {
    player: usize,
    team: usize,
    lane: u8,
    name: String,
}

/// 一个玩家这边记着的。`ent` 换了就是新的一条命：带 `*` 的一条命一份，其余跟着玩家。
#[derive(Clone, Debug, Default)]
struct Pl {
    ent: Option<usize>,
    alive: bool,
    /// 对过的队伍版本、下次定时对 buff 的 tick、日志里说过的游戏小龙 buff 层数。
    ver: u64,
    refresh_at: usize,
    nat_told: usize,
    // * 上一次读到的生命、护盾、位置和那个 tick（只和上一 tick 的比）
    seen: Option<usize>,
    hp: usize,
    max: usize,
    shield: usize,
    pos: (u64, u64),
    // * 山脉龙魂：最后一次挨打、下次看护盾；化学科技龙魂：挂着残血 buff；云端龙魂：上一 tick 的大招冷却
    last_hurt: usize,
    shield_at: usize,
    chem_low: bool,
    ult_prev: Option<usize>,
    // * 读不到统计时：上一 tick 的四个冷却、最后一次出手
    cds_prev: Option<(usize, [usize; 4])>,
    last_action: Option<usize>,
    // * 海洋龙魂的回血：(还剩几次, 每次多少, 下一次的 tick)
    ocean: Option<(u8, usize, usize)>,
    /// 本包替他打出的伤害在这一 tick 结算：这一 tick 他统计里涨的不算他打的。
    quiet_at: Option<usize>,
    /// 炼狱 / 海洋 / 海克斯龙魂下次能触发的 tick。
    cd: [usize; 3],
    /// 统计 `deal` 上次读到的数和那个 tick（跟着玩家，不跟着命）。
    deal: Option<(u64, usize)>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Camp {
    Serpen,
    Epic,
}

impl Camp {
    fn index(self) -> usize {
        self as usize
    }

    fn stat(self) -> &'static str {
        match self {
            Camp::Serpen => "serpen_secure",
            Camp::Epic => "epic_secure",
        }
    }
}

/// 一只活着的龙：实体、元素（小龙的）、在哪、什么时候看见的。
#[derive(Clone, Copy, Debug)]
struct Alive {
    ent: usize,
    element: Option<Element>,
    pos: (u64, u64),
    born: usize,
}

/// 死了、还没认出是谁拿下的龙。
#[derive(Clone, Copy, Debug)]
struct Pending {
    camp: Camp,
    /// 看见它活着的 tick、它死的 tick。
    born: usize,
    died: usize,
    element: Option<Element>,
    /// 死的那一 tick 离它 `NEAR` 以内两队活着的英雄。
    near: [usize; 2],
}

/// 远古龙之力 / 纳什男爵之手在一队身上。
#[derive(Clone, Debug)]
struct Hold {
    team: usize,
    start: usize,
    until: usize,
    /// (座位, 那时的英雄实体)：死了、复活了（新的实体）就不在了。
    holders: Vec<(usize, usize)>,
    executes: u32,
    boosted: usize,
    scans: u32,
}

/// 远古龙之力的点燃：谁烧谁、下一次、还剩几次、每次多少。
#[derive(Clone, Copy, Debug)]
struct Burn {
    victim: usize,
    vent: usize,
    holder: usize,
    hent: usize,
    next: usize,
    left: u8,
    per: usize,
}

/// 读统计的办法（每份模拟第一次读时定下，同一个游戏程序每份都一样）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum StatsWay {
    Unknown,
    /// `statistics_json("serpen_secure")` 读得到。
    Path,
    /// 只有整份读得到。
    Whole,
    Missing,
}

/// 「他这一 tick 打到人没有」怎么认：统计的 `deal`，或者读不到统计时看他刚出没出手。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum DealWay {
    Unknown,
    Stats,
    Cooldowns,
}

/// 战斗里每个座位这一 tick 的样子。
#[derive(Clone, Copy, Debug, Default)]
struct Look {
    ent: usize,
    alive: bool,
    hp: usize,
    max: usize,
    shield: usize,
    pos: (u64, u64),
    hurt: bool,
}

/// 一份模拟里的大小龙。
struct Sim {
    no: u64,
    origin: Origin,
    anchors: Vec<usize>,
    nexus: Vec<usize>,
    /// 编号上次在哪（实体, buff 表里的位置）：每 tick 先看这一个。
    hint: Option<(usize, usize)>,
    stamp: u64,
    born: usize,
    late: bool,
    ended: bool,
    order: [Element; 3],
    seats: Vec<Seat>,
    pls: Vec<Pl>,
    conflict: bool,
    conflict_at: usize,
    serpen: Option<Alive>,
    epic: Option<Alive>,
    scan_at: usize,
    pending: Vec<Pending>,
    /// [小龙 / 纳什男爵][队伍]：统计里上次读到的和、算给这队的次数（远古巨龙也是小龙）。
    secure: [[u64; 2]; 2],
    caps: [[u32; 2]; 2],
    stats: StatsWay,
    deal_way: DealWay,
    stacks: [[u8; 6]; 2],
    drakes: u32,
    soul: Option<(usize, Element)>,
    elder: [Option<Hold>; 2],
    baron: [Option<Hold>; 2],
    /// 每队的版本：拿龙、龙魂、远古龙之力 / 纳什男爵之手开始结束时涨，英雄身上的 buff 跟着对一遍。
    ver: [u64; 2],
    burns: Vec<Burn>,
    /// 处决过的实体和 tick（`undying` 撑住的过一秒再来）。
    executed: Vec<(usize, usize)>,
    record_name: Option<String>,
    dirty: bool,
    seq: u8,
    events: Vec<(usize, Ev)>,
    // ---- END 的统计
    procs: [usize; 6],
    executes: usize,
    burnt: usize,
    ocean_healed: usize,
    shields: usize,
    boosts: usize,
    neutralized: usize,
    proc_lines: usize,
    rebuilt: bool,
}

impl Sim {
    fn new(no: u64, origin: Origin, now: usize, late: bool, seed: u64) -> Sim {
        Sim {
            no,
            origin,
            anchors: Vec::new(),
            nexus: Vec::new(),
            hint: None,
            stamp: STAMP.fetch_add(1, Ordering::Relaxed),
            born: now,
            late,
            ended: false,
            order: rules::order(seed),
            seats: Vec::new(),
            pls: Vec::new(),
            conflict: false,
            conflict_at: 0,
            serpen: None,
            epic: None,
            scan_at: 0,
            pending: Vec::new(),
            secure: [[0; 2]; 2],
            caps: [[0; 2]; 2],
            stats: StatsWay::Unknown,
            deal_way: DealWay::Unknown,
            stacks: [[0; 6]; 2],
            drakes: 0,
            soul: None,
            elder: [None, None],
            baron: [None, None],
            ver: [1, 1],
            burns: Vec::new(),
            executed: Vec::new(),
            record_name: None,
            dirty: true,
            seq: 0,
            events: Vec::new(),
            procs: [0; 6],
            executes: 0,
            burnt: 0,
            ocean_healed: 0,
            shields: 0,
            boosts: 0,
            neutralized: 0,
            proc_lines: 0,
            rebuilt: false,
        }
    }

    fn who(&self, seat: usize) -> String {
        self.seats.get(seat).map_or_else(|| format!("seat{seat}"), |s| {
            format!("{}(p{} {})", s.name.trim_start_matches("league_"), s.player, side(s.team))
        })
    }

    fn id(&self, seat: usize) -> String {
        self.seats.get(seat).map_or_else(String::new, |s| s.name.clone())
    }

    fn step(&mut self, sim: &mut StableSim<'_>, screen: Option<(u64, u64)>) {
        let now = sim.tick();
        if self.seats.is_empty() && !self.read_cast(sim, screen) {
            return;
        }
        if self.late && !self.rebuilt {
            self.rebuilt = true;
            self.restore(sim, now, screen);
        }
        if !self.conflict && now >= self.conflict_at {
            self.check_conflict(sim, now, screen);
        }
        if !self.conflict {
            self.camps(sim, now, screen);
            self.resolve(sim, now, screen);
            self.keep(sim, now, screen);
            self.ocean(sim, now);
            self.combat(sim, now, screen);
            self.boost(sim, now, screen);
        }
        self.flush(sim, now, screen);
        if sim.is_end() {
            self.ended = true;
            self.end(sim, screen);
        }
    }

    /// 阵容：每个玩家的队伍、分路、英雄。全部玩家都有英雄时才算读好。
    fn read_cast(&mut self, sim: &mut StableSim<'_>, screen: Option<(u64, u64)>) -> bool {
        let n = sim.player_count();
        if n == 0 {
            return false;
        }
        let mut seats = Vec::new();
        for i in 0..n {
            let Some(p) = sim.player_at(i) else { return false };
            let Some(name) = p.champion().and_then(|c| c.name()) else { return false };
            let lane = p.lane().map_or(i % 5, |l| l.code() as usize) as u8;
            seats.push(Seat { player: p.id(), team: p.team().min(1), lane, name });
        }
        self.pls = vec![Pl::default(); seats.len()];
        self.seats = seats;
        let order: Vec<&str> = self.order.iter().map(|e| e.key()).collect();
        say(screen.is_some(), "match", format!("{} MATCH sim #{} drakes in this order: {}, {}, then the rift's {} until the soul{}",
                                               head(sim), self.no, order[0], order[1], order[2],
                                               if self.late { " (late)" } else { "" }));
        true
    }

    /// 状态丢了（编号还在水晶上）：从水晶上的状态记录拿回层数、龙魂、远古龙之力 / 纳什男爵之手（拿着的人按分路找回现在的英雄）。
    fn restore(&mut self, sim: &mut StableSim<'_>, now: usize, screen: Option<(u64, u64)>) {
        let found = self.anchors.iter().find_map(|&a| {
            buffs_on(sim, a).iter().find_map(|b| Record::parse(b.name()).map(|r| (b.name().to_string(), r)))
        });
        let Some((name, r)) = found else {
            say(screen.is_some(), "rebuilt", format!("{} REBUILT sim #{}: no state record on the nexus - from scratch", head(sim), self.no));
            return;
        };
        self.stacks = r.stacks;
        self.drakes = r.stacks.iter().flatten().map(|&n| n as u32).sum();
        for t in 0..2 {
            self.caps[0][t] = r.stacks[t].iter().map(|&n| n as u32).sum();
        }
        self.soul = r.soul.and_then(|(t, e)| Element::from_code(e).map(|e| (t.min(1), e)));
        self.conflict = r.conflict;
        self.seq = r.seq;
        self.record_name = Some(name);
        for (rec, elder) in [(r.elder, true), (r.baron, false)] {
            let Some(h) = rec else { continue };
            if h.until <= now {
                continue;
            }
            let holders: Vec<(usize, usize)> = (0..self.seats.len())
                .filter(|&i| self.seats[i].team == h.team && h.lanes & (1 << self.seats[i].lane) != 0)
                .filter_map(|i| champ_of(sim, self.seats[i].player).filter(|c| c.1).map(|c| (i, c.0)))
                .collect();
            let hold = Hold { team: h.team, start: now, until: h.until, holders, executes: 0, boosted: 0, scans: 0 };
            if elder {
                self.elder[h.team.min(1)] = Some(hold);
            } else {
                self.baron[h.team.min(1)] = Some(hold);
            }
        }
        self.ver = [self.ver[0] + 1, self.ver[1] + 1];
        say(screen.is_some(), "rebuilt", format!("{} REBUILT sim #{} from the nexus record: blue {:?} red {:?} soul {:?}{}",
                                                 head(sim), self.no, r.stacks[0], r.stacks[1], self.soul,
                                                 if r.conflict { " CONFLICT" } else { "" }));
    }

    // ---------- 创意工坊的大小龙 mod ----------

    fn check_conflict(&mut self, sim: &mut StableSim<'_>, now: usize, screen: Option<(u64, u64)>) {
        self.conflict_at = now + if now < CONFLICT_EARLY { 30 } else { 600 };
        let found = self.nexus.iter().chain(self.anchors.iter()).find_map(|&a| {
            buffs_on(sim, a).into_iter().map(|b| b.name().to_string()).find(|n| rules::workshop_record(n))
        });
        let Some(name) = found else { return };
        self.conflict = true;
        // nothing of ours stays (a record the Workshop mod hung late: ours off the champions and the serpent)
        let mut off = 0;
        for i in 0..self.seats.len() {
            if let Some((ent, _)) = champ_of(sim, self.seats[i].player) {
                for b in buffs_on(sim, ent) {
                    let n = b.name();
                    if n.starts_with("league_dragons_") {
                        off += sim.entity_remove_buff(ent, n);
                    }
                }
            }
        }
        if let Some(s) = self.serpen {
            if let Some(e) = s.element {
                off += sim.entity_remove_buff(s.ent, &rules::marker(e));
            }
        }
        self.holds_clear();
        self.burns.clear();
        say(screen.is_some(), "conflict", format!(
            "{} CONFLICT sim #{}: the Workshop mod \"Elemental Drakes & Baron\" is on ({name} on the nexus) - league_dragons applies nothing in this match ({off} of its buffs taken off); disable that mod",
            head(sim), self.no));
        self.emit(sim, now, Ev::Conflict, feed::What::Conflict, screen);
    }

    fn holds_clear(&mut self) {
        self.elder = [None, None];
        self.baron = [None, None];
    }

    // ---------- 大小龙出生、死 ----------

    fn camps(&mut self, sim: &mut StableSim<'_>, now: usize, screen: Option<(u64, u64)>) {
        for camp in [Camp::Serpen, Camp::Epic] {
            let known = match camp {
                Camp::Serpen => self.serpen,
                Camp::Epic => self.epic,
            };
            let Some(a) = known else { continue };
            // alive and still that camp (a slot handed to another unit the tick it died is not it)
            let kind = match camp {
                Camp::Serpen => EntityKindV1::Serpen,
                Camp::Epic => EntityKindV1::Epic,
            };
            if sim.get_entity(a.ent).is_some_and(|e| e.is_alive() && e.kind().is_none_or(|k| k == kind)) {
                continue;
            }
            let mut near = [0usize; 2];
            for s in &self.seats {
                if let Some(e) = sim.get_player(s.player).and_then(|p| p.champion()).filter(|e| e.is_alive()) {
                    if d2(e.pos(), a.pos) <= NEAR * NEAR {
                        near[s.team] += 1;
                    }
                }
            }
            self.pending.push(Pending { camp, born: a.born, died: now, element: a.element, near });
            match camp {
                Camp::Serpen => self.serpen = None,
                Camp::Epic => self.epic = None,
            }
            self.dirty = true;
        }
        if (self.serpen.is_some() && self.epic.is_some()) || now < self.scan_at {
            return;
        }
        self.scan_at = now + SCAN;
        let mut found: Vec<(Camp, usize, (u64, u64), String)> = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            let camp = match e.kind() {
                Some(EntityKindV1::Serpen) => Camp::Serpen,
                Some(EntityKindV1::Epic) => Camp::Epic,
                Some(_) => continue,
                // a host without kinds: the camps' names
                None => match e.name() {
                    Some(n) if n.contains("serpen") => Camp::Serpen,
                    Some(n) if n.contains("epic") || n.contains("morgard") => Camp::Epic,
                    _ => continue,
                },
            };
            if e.is_alive() {
                found.push((camp, e.id(), e.pos(), e.name().unwrap_or_default()));
            }
        }
        for (camp, ent, pos, name) in found {
            match camp {
                Camp::Serpen if self.serpen.is_none() => {
                    let element = rules::next_element(&self.order, self.drakes, self.soul.is_some());
                    sim.add_buff(ent, &BuffV1::named(&rules::marker(element)));
                    self.serpen = Some(Alive { ent, element: Some(element), pos, born: now });
                    let n = self.drakes + 1;
                    say(screen.is_some(), "spawn", format!("{} SPAWN sim #{} serpent #{ent} '{name}': {} ({})", head(sim), self.no,
                                                           element.key(), if element == Element::Elder {
                                                               "the Elder Dragon".to_string()
                                                           } else {
                                                               format!("drake {n}")
                                                           }));
                    if element == Element::Elder {
                        self.emit(sim, now, Ev::ElderSpawn, feed::What::ElderSpawn, screen);
                    } else {
                        self.emit(sim, now, Ev::DrakeSpawn { element }, feed::What::DrakeSpawn { element }, screen);
                    }
                }
                Camp::Epic if self.epic.is_none() => {
                    self.epic = Some(Alive { ent, element: None, pos, born: now });
                    self.dirty = true;
                    say(screen.is_some(), "spawn", format!("{} SPAWN sim #{} Baron Nashor #{ent} '{name}'", head(sim), self.no));
                }
                _ => {}
            }
        }
    }

    /// 统计里这一项两队各自的和（读不到：None）。
    fn secure_sums(&mut self, sim: &StableSim<'_>, key: &str) -> Option<[u64; 2]> {
        if self.stats == StatsWay::Missing {
            return None;
        }
        let mut sums = [0u64; 2];
        for s in &self.seats {
            let p = sim.get_player(s.player)?;
            let v = match self.stats {
                StatsWay::Path => p.statistics_json(key).as_deref().and_then(parse_num),
                StatsWay::Whole => p.statistics_json("").and_then(|d| find_num(&d, key)),
                _ => match p.statistics_json(key).as_deref().and_then(parse_num) {
                    Some(v) => {
                        self.stats = StatsWay::Path;
                        Some(v)
                    }
                    None => match p.statistics_json("").and_then(|d| find_num(&d, key)) {
                        Some(v) => {
                            self.stats = StatsWay::Whole;
                            Some(v)
                        }
                        None => {
                            self.stats = StatsWay::Missing;
                            None
                        }
                    },
                },
            };
            sums[s.team] += v?;
        }
        Some(sums)
    }

    /// 谁拿下的：统计涨了的那队；读不到或还没涨：小龙看游戏的小龙 buff 多挂到了哪队身上。都认不出：None（再等）。
    fn attribute(&mut self, sim: &StableSim<'_>, p: &Pending) -> Option<(usize, &'static str)> {
        let k = p.camp.index();
        if let Some(sums) = self.secure_sums(sim, p.camp.stat()) {
            let up: Vec<usize> = (0..2).filter(|&t| sums[t] > self.secure[k][t]).collect();
            if up.len() == 1 {
                self.secure[k] = sums;
                return Some((up[0], "stats"));
            }
        }
        if p.camp == Camp::Serpen {
            let mut up = Vec::new();
            for t in 0..2 {
                let most = self.seats.iter().filter(|s| s.team == t)
                    .filter_map(|s| champ_of(sim, s.player).filter(|c| c.1))
                    .map(|(ent, _)| buffs_on(sim, ent).iter().filter(|b| b.name() == rules::NATIVE).count())
                    .max()
                    .unwrap_or(0);
                if most > self.caps[0][t] as usize {
                    up.push(t);
                }
            }
            if up.len() == 1 {
                return Some((up[0], "native buff"));
            }
        }
        None
    }

    fn resolve(&mut self, sim: &mut StableSim<'_>, now: usize, screen: Option<(u64, u64)>) {
        if self.pending.is_empty() {
            return;
        }
        for p in std::mem::take(&mut self.pending) {
            match self.attribute(sim, &p) {
                Some((team, how)) => self.capture(sim, now, &p, team, how, screen),
                None if now >= p.died + PENDING_T => {
                    let team = match p.near[0].cmp(&p.near[1]) {
                        std::cmp::Ordering::Greater => Some(0),
                        std::cmp::Ordering::Less => Some(1),
                        std::cmp::Ordering::Equal => None,
                    };
                    match team {
                        Some(t) => self.capture(sim, now, &p, t, "near", screen),
                        None => say(screen.is_some(), "kill", format!(
                            "{} KILL sim #{} {:?} died at t={} but nobody can be told as its taker (near {:?}) - no reward",
                            head(sim), self.no, p.camp, p.died, p.near)),
                    }
                }
                None => self.pending.push(p),
            }
        }
    }

    fn capture(&mut self, sim: &mut StableSim<'_>, now: usize, p: &Pending, team: usize, how: &str, screen: Option<(u64, u64)>) {
        let k = p.camp.index();
        self.caps[k][team] += 1;
        if how != "stats" {
            // the statistics in step for the next capture (they may come a tick late: the next one then sees two)
            if let Some(sums) = self.secure_sums(sim, p.camp.stat()) {
                self.secure[k] = sums;
            }
        }
        let late = format!(", up {} s{}", (p.died - p.born.min(p.died)) / 60,
                           if now > p.died { format!(", told {} ticks after it died", now - p.died) } else { String::new() });
        match p.camp {
            Camp::Serpen => {
                let element = p.element.unwrap_or_else(|| rules::next_element(&self.order, self.drakes, self.soul.is_some()));
                if element == Element::Elder {
                    let lanes = self.start_hold(sim, now, true, team);
                    let holders = self.holder_names(true, team);
                    say(screen.is_some(), "elder", format!("{} ELDER ON sim #{} {} took the Elder Dragon (by {how}{late}): Aspect of the Dragon on [{}] until t={}",
                                                           head(sim), self.no, side(team), holders.join(", "), now + rules::ELDER_T));
                    let ids = self.holder_ids(true, team);
                    self.emit(sim, now, Ev::ElderKilled { team, lanes }, feed::What::ElderKilled { team, holders: ids }, screen);
                } else {
                    let slot = element.slot().unwrap_or(0);
                    self.stacks[team][slot] = (self.stacks[team][slot] + 1).min(15);
                    self.drakes += 1;
                    let total: u8 = self.stacks[team].iter().sum();
                    self.ver[team] += 1;
                    let list: Vec<String> = DRAKES.iter().filter_map(|e| {
                        let n = self.stacks[team][e.slot().unwrap_or(0)];
                        (n > 0).then(|| format!("{} {n}", e.key()))
                    }).collect();
                    say(screen.is_some(), "kill", format!("{} KILL sim #{} {} took the {} drake (by {how}{late}): {} drake{} [{}]",
                                                          head(sim), self.no, side(team), element.key(), total,
                                                          if total == 1 { "" } else { "s" }, list.join(", ")));
                    self.emit(sim, now, Ev::Drake { team, element, total }, feed::What::Drake { team, element, total }, screen);
                    if rules::soul_claimed(total, self.soul.is_some()) {
                        let soul = self.order[2];
                        self.soul = Some((team, soul));
                        say(screen.is_some(), "soul", format!("{} SOUL sim #{} {} claims the {} soul with {total} drakes - every dragon from now on is the Elder",
                                                              head(sim), self.no, side(team), soul.key()));
                        self.emit(sim, now, Ev::Soul { team, element: soul }, feed::What::Soul { team, element: soul }, screen);
                    }
                }
            }
            Camp::Epic => {
                let lanes = self.start_hold(sim, now, false, team);
                let holders = self.holder_names(false, team);
                say(screen.is_some(), "baron", format!("{} BARON ON sim #{} {} took Baron Nashor (by {how}{late}): Hand of Baron on [{}] until t={} (minions within {} of them stronger)",
                                                       head(sim), self.no, side(team), holders.join(", "), now + rules::BARON_T, rules::MINION_R));
                let ids = self.holder_ids(false, team);
                self.emit(sim, now, Ev::BaronKilled { team, lanes }, feed::What::BaronKilled { team, holders: ids }, screen);
            }
        }
        self.dirty = true;
    }

    /// 一队当时活着的英雄拿到远古龙之力（`elder`）/ 纳什男爵之手。-> 他们的分路位。
    fn start_hold(&mut self, sim: &StableSim<'_>, now: usize, elder: bool, team: usize) -> u8 {
        let holders: Vec<(usize, usize)> = (0..self.seats.len())
            .filter(|&i| self.seats[i].team == team)
            .filter_map(|i| champ_of(sim, self.seats[i].player).filter(|c| c.1).map(|c| (i, c.0)))
            .collect();
        let lanes = holders.iter().fold(0u8, |m, &(i, _)| m | 1 << self.seats[i].lane);
        let t = if elder { rules::ELDER_T } else { rules::BARON_T };
        let hold = Hold { team, start: now, until: now + t, holders, executes: 0, boosted: 0, scans: 0 };
        if elder {
            self.elder[team] = Some(hold);
        } else {
            self.baron[team] = Some(hold);
        }
        self.ver[team] += 1;
        lanes
    }

    fn hold(&self, elder: bool, team: usize) -> Option<&Hold> {
        if elder { self.elder[team].as_ref() } else { self.baron[team].as_ref() }
    }

    fn holder_names(&self, elder: bool, team: usize) -> Vec<String> {
        self.hold(elder, team).map_or_else(Vec::new, |h| h.holders.iter().map(|&(i, _)| self.who(i)).collect())
    }

    fn holder_ids(&self, elder: bool, team: usize) -> Vec<String> {
        self.hold(elder, team).map_or_else(Vec::new, |h| h.holders.iter().map(|&(i, _)| self.id(i)).collect())
    }

    /// 这个座位现在拿着远古龙之力（`elder`）/ 纳什男爵之手：到哪个 tick。
    fn holding(&self, elder: bool, seat: usize, ent: usize, now: usize) -> Option<usize> {
        let team = self.seats.get(seat)?.team;
        self.hold(elder, team).filter(|h| now < h.until && h.holders.contains(&(seat, ent))).map(|h| h.until)
    }

    // ---------- 英雄身上的 buff ----------

    /// 每个英雄：新的一条命、队伍的版本变了、定时，就把本包该在他身上的 buff 对一遍；拿着远古龙之力 / 纳什男爵之手的人死了就
    /// 不再拿着，到时间的结束。
    fn keep(&mut self, sim: &mut StableSim<'_>, now: usize, screen: Option<(u64, u64)>) {
        for elder in [true, false] {
            for team in 0..2 {
                let ended = self.hold(elder, team).is_some_and(|h| now >= h.until);
                if ended {
                    let h = if elder { self.elder[team].take() } else { self.baron[team].take() };
                    if let Some(h) = h {
                        self.hold_off(sim, elder, &h, "time is up", screen);
                    }
                }
            }
        }
        let moved = (0..self.seats.len()).any(|i| self.pls[i].ver != self.ver[self.seats[i].team] && self.pls[i].alive);
        if now % KEEP_EVERY != 0 && !moved {
            return;
        }
        for i in 0..self.seats.len() {
            let (player, team) = (self.seats[i].player, self.seats[i].team);
            let Some((ent, alive)) = champ_of(sim, player) else { continue };
            if self.pls[i].ent != Some(ent) {
                let old = std::mem::take(&mut self.pls[i]);
                self.pls[i] = Pl { ent: Some(ent), alive, last_hurt: now, nat_told: old.nat_told, cd: old.cd, deal: old.deal,
                                   ..Pl::default() };
            }
            self.pls[i].alive = alive;
            for elder in [true, false] {
                let lost = self.hold(elder, team).is_some_and(|h| h.holders.iter().any(|&(s, e)| s == i && (e != ent || !alive)));
                if !lost {
                    continue;
                }
                let empty = {
                    let h = if elder { self.elder[team].as_mut() } else { self.baron[team].as_mut() };
                    let h = h.expect("the hold");
                    h.holders.retain(|&(s, _)| s != i);
                    h.holders.is_empty()
                };
                self.ver[team] += 1;
                self.dirty = true;
                say(screen.is_some(), if elder { "elder" } else { "baron" }, format!(
                    "{} {} OFF sim #{} {} died - {} left", head(sim), if elder { "ELDER" } else { "BARON" }, self.no, self.who(i),
                    if empty { "nobody".to_string() } else { format!("{}", self.hold(elder, team).map_or(0, |h| h.holders.len())) }));
                if empty {
                    let h = if elder { self.elder[team].take() } else { self.baron[team].take() };
                    if let Some(h) = h {
                        self.hold_off(sim, elder, &h, "every holder died", screen);
                    }
                }
            }
            if !alive {
                continue;
            }
            if self.pls[i].ver != self.ver[team] || now >= self.pls[i].refresh_at {
                self.refresh(sim, i, ent, now, screen);
                self.pls[i].ver = self.ver[team];
                self.pls[i].refresh_at = now + REFRESH;
            }
        }
    }

    fn hold_off(&mut self, sim: &StableSim<'_>, elder: bool, h: &Hold, why: &str, screen: Option<(u64, u64)>) {
        self.ver[h.team] += 1;
        self.dirty = true;
        let extra = if elder {
            format!("{} executes", h.executes)
        } else {
            format!("{} minion boosts in {} scans", h.boosted, h.scans)
        };
        say(screen.is_some(), if elder { "elder" } else { "baron" }, format!(
            "{} {} OFF sim #{} {}'s {} ended: {why} (from t={}, {extra})", head(sim), if elder { "ELDER" } else { "BARON" },
            self.no, side(h.team), if elder { "Aspect of the Dragon" } else { "Hand of Baron" }, h.start));
    }

    /// 本包该在这个英雄身上的：中和游戏小龙 buff 的、每种元素的层数、龙魂的标记、远古龙之力、纳什男爵之手。多的拿掉，少的补上，
    /// 数值不对的换掉。
    fn refresh(&mut self, sim: &mut StableSim<'_>, seat: usize, ent: usize, now: usize, screen: Option<(u64, u64)>) {
        let team = self.seats[seat].team;
        let buffs = buffs_on(sim, ent);
        let natives: Vec<BuffV1> = buffs.iter().filter(|b| b.name() == rules::NATIVE).copied().collect();
        let (nat, left) = rules::neutralizer(&natives);
        let mut want: Vec<BuffV1> = Vec::new();
        if let Some(n) = nat {
            want.push(n);
        }
        for e in DRAKES {
            let n = self.stacks[team][e.slot().unwrap_or(0)];
            if n > 0 {
                want.push(rules::drake_buff(e, n));
            }
        }
        if let Some((t, e)) = self.soul {
            if t == team {
                want.push(rules::soul_buff(e));
            }
        }
        if let Some(until) = self.holding(true, seat, ent, now) {
            want.push(rules::elder_buff(until - now));
        }
        if let Some(until) = self.holding(false, seat, ent, now) {
            want.push(rules::baron_buff(until - now));
        }
        let mut nat_put = false;
        for w in &want {
            let have: Vec<&BuffV1> = buffs.iter().filter(|b| b.name() == w.name()).collect();
            if have.len() == 1 && rules::same_stats(have[0], w) {
                continue;
            }
            if !have.is_empty() {
                sim.entity_remove_buff(ent, w.name());
            }
            sim.add_buff(ent, w);
            nat_put |= w.name() == rules::NAT;
        }
        let mut gone: Vec<String> = Vec::new();
        for b in &buffs {
            let n = b.name();
            let ours = n == rules::NAT || n.starts_with(rules::DK) || n.starts_with(rules::SOUL) || n == rules::ELDER
                || n == rules::BARON;
            if ours && !want.iter().any(|w| w.name() == n) && !gone.iter().any(|g| g == n) {
                sim.entity_remove_buff(ent, n);
                gone.push(n.to_string());
            }
        }
        if nat_put {
            self.neutralized += 1;
        }
        if nat_put && natives.len() != self.pls[seat].nat_told {
            self.pls[seat].nat_told = natives.len();
            let each = natives.first().map_or_else(String::new, rules::stats_text);
            let mut line = format!("{} NEUTRALIZE sim #{} {} #{ent}: x{} {} ({each} each) -> {} ({})", head(sim), self.no,
                                   self.who(seat), natives.len(), rules::NATIVE, rules::NAT,
                                   nat.as_ref().map_or_else(String::new, rules::stats_text));
            if !left.is_empty() {
                line.push_str(&format!("; left on, cannot be negated: {}", left.join(", ")));
            }
            say(screen.is_some(), "neutralize", line);
        }
    }

    // ---------- 海洋亚龙 ----------

    fn ocean(&mut self, sim: &mut StableSim<'_>, now: usize) {
        if now == 0 || now % rules::OCEAN_EVERY != 0 {
            return;
        }
        let slot = Element::Ocean.slot().unwrap_or(2);
        for i in 0..self.seats.len() {
            let n = self.stacks[self.seats[i].team][slot];
            let Some(ent) = self.pls[i].ent.filter(|_| n > 0 && self.pls[i].alive) else { continue };
            let Some((hp, max)) = sim.get_entity(ent).filter(|e| e.is_alive()).map(|e| e.hp()) else { continue };
            let amount = rules::ocean_heal(hp, max, n);
            if amount > 0 {
                sim.heal(ent, ent, amount);
                self.ocean_healed += amount;
            }
        }
    }

    // ---------- 龙魂、远古龙之力：谁打到了谁 ----------

    fn combat(&mut self, sim: &mut StableSim<'_>, now: usize, screen: Option<(u64, u64)>) {
        let elder_on = self.elder.iter().flatten().any(|h| !h.holders.is_empty());
        if self.soul.is_none() && !elder_on && self.burns.is_empty() {
            return;
        }
        // every champion this tick: health, shields, where; hurt = health + shields went down on the same life
        let mut looks = vec![Look::default(); self.seats.len()];
        for (i, look) in looks.iter_mut().enumerate() {
            let pl = &mut self.pls[i];
            let Some(ent) = pl.ent.filter(|_| pl.alive) else { continue };
            let Some(e) = sim.get_entity(ent).filter(|e| e.is_alive()) else { continue };
            let ((hp, max), shield, pos) = (e.hp(), e.shield(), e.pos());
            let hurt = pl.seen.is_some_and(|t| t + 1 == now) && hp + shield < pl.hp + pl.shield;
            (pl.seen, pl.hp, pl.max, pl.shield, pl.pos) = (Some(now), hp, max, shield, pos);
            if hurt {
                pl.last_hurt = now;
            }
            *look = Look { ent, alive: true, hp, max, shield, pos, hurt };
        }
        if let Some((team, soul)) = self.soul {
            self.soul_upkeep(sim, now, team, soul, &looks, screen);
        }
        // the holders' hits
        for h in 0..self.seats.len() {
            if !looks[h].alive {
                continue;
            }
            let team = self.seats[h].team;
            let elder = self.holding(true, h, looks[h].ent, now).is_some();
            let soul = self.soul.filter(|s| s.0 == team).map(|s| s.1)
                .filter(|e| matches!(e, Element::Infernal | Element::Ocean | Element::Hextech));
            if !elder && soul.is_none() {
                continue;
            }
            let mut near: Vec<(u64, usize)> = (0..self.seats.len())
                .filter(|&v| self.seats[v].team != team && looks[v].alive)
                .map(|v| (d2(looks[h].pos, looks[v].pos), v))
                .filter(|&(d, _)| d <= REACH * REACH)
                .collect();
            if near.is_empty() {
                // out of reach of every enemy champion: his `deal` reading goes stale (read again when one comes near)
                self.pls[h].deal = self.pls[h].deal.map(|(v, _)| (v, usize::MAX));
                continue;
            }
            let dealt = self.dealt(sim, h, now);
            near.retain(|&(_, v)| looks[v].hurt);
            if !dealt || near.is_empty() {
                continue;
            }
            near.sort();
            let victims: Vec<usize> = near.iter().map(|&(_, v)| v).collect();
            if elder {
                for &v in &victims {
                    self.burn(sim, h, v, &looks, now, screen);
                }
            }
            match soul {
                Some(Element::Infernal) if now >= self.pls[h].cd[0] => self.infernal(sim, h, victims[0], &looks, now, screen),
                Some(Element::Ocean) if now >= self.pls[h].cd[1] => self.ocean_soul(sim, h, &looks, now, screen),
                Some(Element::Hextech) if now >= self.pls[h].cd[2] => self.hextech(sim, h, victims[0], &looks, now, screen),
                _ => {}
            }
        }
        self.burns_tick(sim, &looks, now, screen);
    }

    /// 他这一 tick 打出伤害没有：统计 `deal` 比上一 tick 涨了（上一 tick 也读过；本包替他打的那一 tick 不算）；读不到统计时
    /// 看他 `ACTION_WINDOW` 里出没出手（冷却涨上去）。
    fn dealt(&mut self, sim: &StableSim<'_>, h: usize, now: usize) -> bool {
        let player = self.seats[h].player;
        let quiet = self.pls[h].quiet_at == Some(now);
        if self.deal_way != DealWay::Cooldowns {
            let v = sim.get_player(player).and_then(|p| p.statistics_json("deal")).as_deref().and_then(parse_num);
            match v {
                Some(v) => {
                    self.deal_way = DealWay::Stats;
                    let before = self.pls[h].deal;
                    self.pls[h].deal = Some((v, now));
                    return match before {
                        Some((b, at)) => at.checked_add(1) == Some(now) && v > b && !quiet,
                        None => false,
                    };
                }
                None => self.deal_way = DealWay::Cooldowns,
            }
        }
        let cds = sim.get_player(player).and_then(|p| p.cooldowns()).map(|c| [c.0, c.1, c.2, c.3]);
        if let Some(c) = cds {
            if let Some((at, prev)) = self.pls[h].cds_prev {
                if at + 1 == now && (0..4).any(|k| c[k] > prev[k]) {
                    self.pls[h].last_action = Some(now);
                }
            }
            self.pls[h].cds_prev = Some((now, c));
        }
        !quiet && self.pls[h].last_action.is_some_and(|t| now <= t + ACTION_WINDOW)
    }

    /// 龙魂的常驻部分：山脉的护盾、化学科技的残血 buff、云端放大招后的加速、海洋龙魂的回血。
    fn soul_upkeep(&mut self, sim: &mut StableSim<'_>, now: usize, team: usize, soul: Element, looks: &[Look],
                   screen: Option<(u64, u64)>) {
        for i in 0..self.seats.len() {
            if self.seats[i].team != team || !looks[i].alive {
                continue;
            }
            let l = looks[i];
            match soul {
                Element::Mountain => {
                    let pl = &mut self.pls[i];
                    if now >= pl.last_hurt + rules::MOUNTAIN_SOUL_IDLE && now >= pl.shield_at {
                        pl.shield_at = now + rules::MOUNTAIN_SOUL_CHECK;
                        let (ad, ap) = ad_ap(sim, l.ent);
                        let want = rules::mountain_soul_shield(ad, ap, l.max);
                        if l.shield < want && sim.entity_add_shield(l.ent, want - l.shield, rules::MOUNTAIN_SOUL_T) {
                            self.pls[i].shield = want;
                            self.shields += 1;
                            self.procs[1] += 1;
                            self.proc_say(screen, format!("{} PROC mountain soul {}: shield up to {want} (5 s untouched)",
                                                                  head(sim), self.who(i)));
                        }
                    }
                }
                Element::Chemtech => {
                    let low = rules::chem_low(l.hp, l.max);
                    if low != self.pls[i].chem_low {
                        self.pls[i].chem_low = low;
                        sim.entity_remove_buff(l.ent, rules::CHEM_LOW);
                        if low {
                            sim.add_buff(l.ent, &rules::chem_low_buff());
                            self.procs[5] += 1;
                            self.proc_say(screen, format!("{} PROC chemtech soul {}: below half health ({}/{}) - tenacity, damage and less damage taken",
                                                                  head(sim), self.who(i), l.hp, l.max));
                        }
                    }
                }
                Element::Cloud => {
                    let ult = sim.get_player(self.seats[i].player).and_then(|p| p.cooldowns()).map(|c| c.3);
                    if let (Some(u), Some(prev)) = (ult, self.pls[i].ult_prev) {
                        if u > prev + rules::ULT_JUMP {
                            sim.entity_remove_buff(l.ent, rules::CLOUD_HASTE);
                            sim.add_buff(l.ent, &rules::cloud_haste());
                            self.procs[3] += 1;
                            self.proc_say(screen, format!("{} PROC cloud soul {}: ultimate cast - +{}% move speed for 6 s",
                                                                  head(sim), self.who(i), rules::CLOUD_HASTE_MS));
                        }
                    }
                    self.pls[i].ult_prev = ult;
                }
                _ => {}
            }
            // Ocean soul's heal over 4 s
            if let Some((left, per, next)) = self.pls[i].ocean {
                if now >= next {
                    sim.heal(l.ent, l.ent, per);
                    self.ocean_healed += per;
                    self.pls[i].ocean = (left > 1).then_some((left - 1, per, next + rules::OCEAN_SOUL_EVERY));
                }
            }
        }
    }

    fn quiet(&mut self, seat: usize, now: usize) {
        self.pls[seat].quiet_at = Some(now + 1);
    }

    /// 龙魂触发的日志：一份模拟前 `PROC_FIRST` 行，之后每 `PROC_EVERY` 行一行（屏幕上那一场也是：团战里每几秒一次）。
    fn proc_say(&mut self, screen: Option<(u64, u64)>, line: String) {
        self.proc_lines += 1;
        let n = self.proc_lines;
        if n <= PROC_FIRST || n % PROC_EVERY == 0 {
            say(screen.is_some(), "proc", format!("{line} (proc line {n} of this match)"));
        }
    }

    /// 炼狱龙魂：在 `v` 身上爆炸，波及他身边的敌方英雄。
    fn infernal(&mut self, sim: &mut StableSim<'_>, h: usize, v: usize, looks: &[Look], now: usize, screen: Option<(u64, u64)>) {
        self.pls[h].cd[0] = now + rules::INFERNAL_SOUL_CD;
        let (ad, ap) = ad_ap(sim, looks[h].ent);
        let amount = rules::infernal_soul_damage(ad, ap);
        let team = self.seats[h].team;
        let mut hit = Vec::new();
        for x in 0..self.seats.len() {
            if self.seats[x].team != team && looks[x].alive
                && d2(looks[x].pos, looks[v].pos) <= rules::INFERNAL_SOUL_R * rules::INFERNAL_SOUL_R {
                sim.deal_damage_typed(looks[h].ent, looks[x].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                hit.push(self.who(x));
            }
        }
        self.quiet(h, now);
        self.procs[0] += 1;
        self.proc_say(screen, format!("{} PROC infernal soul {} on {}: {amount} magic damage to [{}]", head(sim),
                                              self.who(h), self.who(v), hit.join(", ")));
    }

    /// 海洋龙魂：4 秒里回血。
    fn ocean_soul(&mut self, sim: &mut StableSim<'_>, h: usize, looks: &[Look], now: usize, screen: Option<(u64, u64)>) {
        self.pls[h].cd[1] = now + rules::OCEAN_SOUL_CD;
        let (ad, ap) = ad_ap(sim, looks[h].ent);
        let total = rules::ocean_soul_heal(ad, ap, looks[h].max);
        let per = (total / rules::OCEAN_SOUL_PULSES as usize).max(1);
        self.pls[h].ocean = Some((rules::OCEAN_SOUL_PULSES, per, now + rules::OCEAN_SOUL_EVERY));
        self.procs[2] += 1;
        self.proc_say(screen, format!("{} PROC ocean soul {}: {total} health over 4 s", head(sim), self.who(h)));
    }

    /// 海克斯龙魂：从 `v` 起的连锁闪电，最多 3 个敌方英雄，减速。
    fn hextech(&mut self, sim: &mut StableSim<'_>, h: usize, v: usize, looks: &[Look], now: usize, screen: Option<(u64, u64)>) {
        self.pls[h].cd[2] = now + rules::HEXTECH_SOUL_CD;
        let (ad, ap) = ad_ap(sim, looks[h].ent);
        let amount = rules::hextech_soul_damage(ad, ap);
        let team = self.seats[h].team;
        let mut others: Vec<(u64, usize)> = (0..self.seats.len())
            .filter(|&x| x != v && self.seats[x].team != team && looks[x].alive)
            .map(|x| (d2(looks[x].pos, looks[v].pos), x))
            .filter(|&(d, _)| d <= rules::HEXTECH_SOUL_R * rules::HEXTECH_SOUL_R)
            .collect();
        others.sort();
        let chain: Vec<usize> = std::iter::once(v).chain(others.into_iter().map(|o| o.1)).take(rules::HEXTECH_SOUL_TARGETS).collect();
        for &x in &chain {
            sim.deal_damage_typed(looks[h].ent, looks[x].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
            if sim.entity_stack_buff(looks[x].ent, &rules::hex_slow(), 1, true) == 0 {
                sim.entity_remove_buff(looks[x].ent, rules::HEX_SLOW);
                sim.add_buff(looks[x].ent, &rules::hex_slow());
            }
        }
        self.quiet(h, now);
        self.procs[4] += 1;
        let names: Vec<String> = chain.iter().map(|&x| self.who(x)).collect();
        self.proc_say(screen, format!("{} PROC hextech soul {}: lightning {amount} magic damage and a slow on [{}]",
                                              head(sim), self.who(h), names.join(", ")));
    }

    /// 远古龙之力：点燃 `v`（再打到就重新烧 1.5 秒）；他已经低于 20% 就处决。
    fn burn(&mut self, sim: &mut StableSim<'_>, h: usize, v: usize, looks: &[Look], now: usize, screen: Option<(u64, u64)>) {
        let (ad, _) = ad_ap(sim, looks[h].ent);
        let per = (rules::burn_total(ad) / rules::BURN_PULSES as usize).max(1);
        self.burns.retain(|b| b.vent != looks[v].ent);
        self.burns.push(Burn { victim: v, vent: looks[v].ent, holder: h, hent: looks[h].ent, next: now + rules::BURN_EVERY,
                               left: rules::BURN_PULSES, per });
        if sim.entity_stack_buff(looks[v].ent, &BuffV1::timed(rules::BURN, rules::BURN_T), 1, true) == 0 {
            sim.entity_remove_buff(looks[v].ent, rules::BURN);
            sim.add_buff(looks[v].ent, &BuffV1::timed(rules::BURN, rules::BURN_T));
        }
        if rules::executable(looks[v].hp, looks[v].max) {
            self.execute(sim, h, v, looks, now, screen);
        }
    }

    /// 点燃的每一下；着火的英雄生命低于 20%、点火的人还拿着远古龙之力：处决。
    fn burns_tick(&mut self, sim: &mut StableSim<'_>, looks: &[Look], now: usize, screen: Option<(u64, u64)>) {
        self.executed.retain(|&(_, t)| now < t + 60);
        let burns = std::mem::take(&mut self.burns);
        for mut b in burns {
            let victim_on = looks.get(b.victim).is_some_and(|l| l.alive && l.ent == b.vent);
            let holder_on = looks.get(b.holder).is_some_and(|l| l.alive && l.ent == b.hent);
            if !victim_on || !holder_on {
                continue;
            }
            if now >= b.next {
                sim.deal_damage_typed(b.hent, b.vent, b.per, DamageTypeV1::Fixed, AttackTypeV1::Dot);
                self.burnt += b.per;
                self.quiet(b.holder, now);
                b.left -= 1;
                b.next += rules::BURN_EVERY;
            }
            let v = looks[b.victim];
            if self.holding(true, b.holder, b.hent, now).is_some() && rules::executable(v.hp, v.max) {
                self.execute(sim, b.holder, b.victim, looks, now, screen);
            }
            if b.left > 0 && !self.executed.iter().any(|e| e.0 == b.vent) {
                self.burns.push(b);
            }
        }
    }

    /// 处决（真实伤害，护盾一起打穿，击杀算 `h` 的）。给足量：护盾先扣，减伤 buff 也按比例缩真实伤害（league_pyke 的做法再
    /// 多给几倍）；`undying` 撑住的（无敌、不死）不死，一秒后还着火、还低于 20% 再来。
    fn execute(&mut self, sim: &mut StableSim<'_>, h: usize, v: usize, looks: &[Look], now: usize, screen: Option<(u64, u64)>) {
        let (hent, vent) = (looks[h].ent, looks[v].ent);
        if self.executed.iter().any(|e| e.0 == vent) {
            return;
        }
        let l = looks[v];
        sim.deal_damage_typed(hent, vent, rules::execute_damage(l.hp, l.shield, l.max), DamageTypeV1::Fixed, AttackTypeV1::Skill);
        sim.add_buff(vent, &BuffV1::timed(rules::EXECUTED, rules::EXECUTED_T));
        self.executed.push((vent, now));
        self.executes += 1;
        self.quiet(h, now);
        let team = self.seats[h].team;
        if let Some(hold) = self.elder[team].as_mut() {
            hold.executes += 1;
        }
        say(screen.is_some(), "execute", format!("{} EXECUTE sim #{} {} executes {} at {}/{} health ({}%) - Aspect of the Dragon",
                                                 head(sim), self.no, self.who(h), self.who(v), l.hp, l.max, l.hp * 100 / l.max.max(1)));
        let (lane, victim_lane) = (self.seats[h].lane, self.seats[v].lane);
        self.emit(sim, now, Ev::Execute { team, lane, victim_lane },
                  feed::What::Execute { team, killer: self.id(h), victim: self.id(v) }, screen);
    }

    // ---------- 纳什男爵之手：兵线 ----------

    /// 每 `BOOST_EVERY` tick：拿着纳什男爵之手的人身边 `MINION_R` 以内的己方小兵续上加强。
    fn boost(&mut self, sim: &mut StableSim<'_>, now: usize, screen: Option<(u64, u64)>) {
        if now % rules::BOOST_EVERY != 0 {
            return;
        }
        for team in 0..2 {
            let Some(h) = self.baron[team].as_ref() else { continue };
            let holders: Vec<(u64, u64)> = h.holders.iter()
                .filter_map(|&(_, ent)| sim.get_entity(ent).filter(|e| e.is_alive()).map(|e| e.pos()))
                .collect();
            if holders.is_empty() {
                continue;
            }
            let mut minions = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.team() != team || !e.is_alive() || !matches!(e.kind(), Some(EntityKindV1::Minion)) {
                    continue;
                }
                let at = e.pos();
                if holders.iter().any(|&p| d2(p, at) <= rules::MINION_R * rules::MINION_R) {
                    minions.push(e.id());
                }
            }
            for &m in &minions {
                if sim.entity_stack_buff(m, &rules::minion_boost(), 1, true) == 0 {
                    sim.entity_remove_buff(m, rules::MINION_BOOST);
                    sim.add_buff(m, &rules::minion_boost());
                }
            }
            self.boosts += minions.len();
            let Some(h) = self.baron[team].as_mut() else { continue };
            h.boosted += minions.len();
            h.scans += 1;
            if h.scans == 1 || h.scans % 20 == 0 {
                let line = format!("{} BOOST sim #{} {}'s Hand of Baron: {} minions near {} holders (scan {}, {} boosts so far)",
                                   head(sim), self.no, side(team), minions.len(), holders.len(), h.scans, h.boosted);
                say(screen.is_some(), "boost", line);
            }
        }
    }

    // ---------- 给画面的接口 ----------

    fn record(&self, now: usize) -> Record {
        let cur = match self.serpen {
            Some(Alive { element: Some(e), .. }) => e,
            _ => rules::next_element(&self.order, self.drakes, self.soul.is_some()),
        };
        let latest = |holds: &[Option<Hold>; 2]| -> Option<HoldRec> {
            holds.iter().flatten().filter(|h| !h.holders.is_empty()).max_by_key(|h| h.start).map(|h| HoldRec {
                team: h.team,
                lanes: h.holders.iter().fold(0u8, |m, &(i, _)| m | 1 << self.seats.get(i).map_or(0, |s| s.lane)),
                until: h.until,
            })
        };
        Record {
            tick: now,
            cur: cur.code(),
            order: [self.order[0].code(), self.order[1].code(), self.order[2].code()],
            stacks: self.stacks,
            soul: self.soul.map(|(t, e)| (t, e.code())),
            elder: latest(&self.elder),
            baron: latest(&self.baron),
            conflict: self.conflict,
            serpen_alive: self.serpen.is_some(),
            epic_alive: self.epic.is_some(),
            seq: self.seq,
        }
    }

    /// 状态变了：换掉水晶上的状态记录。
    fn flush(&mut self, sim: &mut StableSim<'_>, now: usize, screen: Option<(u64, u64)>) {
        if !self.dirty {
            return;
        }
        self.dirty = false;
        let rec = self.record(now);
        let name = rec.name();
        for &a in &self.anchors {
            if let Some(old) = &self.record_name {
                sim.entity_remove_buff(a, old);
            }
            sim.add_buff(a, &BuffV1::named(&name));
        }
        self.record_name = Some(name);
        if let Some((m, s)) = screen {
            feed::record(m, s, rec);
        }
    }

    /// 一件事：水晶上挂一个 `EV_T` tick 的事件 buff、屏幕那一场进 [`feed`]、状态记录的序号加一。
    fn emit(&mut self, sim: &mut StableSim<'_>, now: usize, ev: Ev, what: feed::What, screen: Option<(u64, u64)>) {
        self.seq = self.seq.wrapping_add(1);
        let name = rules::event_name(self.seq, now, &ev);
        for &a in &self.anchors {
            sim.add_buff(a, &BuffV1::timed(&name, rules::EV_T));
        }
        self.events.push((now, ev));
        if let Some((m, s)) = screen {
            feed::push(feed::Event { m, s, tick: now, what });
        }
        self.dirty = true;
    }

    fn end(&mut self, sim: &StableSim<'_>, screen: Option<(u64, u64)>) {
        let stacks = |t: usize| -> String {
            let v: Vec<String> = DRAKES.iter().filter_map(|e| {
                let n = self.stacks[t][e.slot().unwrap_or(0)];
                (n > 0).then(|| format!("{} {n}", e.key()))
            }).collect();
            format!("[{}]", v.join(", "))
        };
        let count = |c: char| self.events.iter().filter(|e| e.1.code() == c).count();
        say(screen.is_some(), "end", format!(
            "{} END sim #{} (from t={}): order {}/{}/{}{}; blue {} red {}; soul {}; elders {} barons {} executes {}; procs infernal {} mountain {} ocean {} cloud {} hextech {} chemtech {}; burn damage {}, ocean heals {}, shields {}, minion boosts {}, neutralizers hung {}; stats {:?} / hits by {:?}",
            head(sim), self.no, self.born, self.order[0].key(), self.order[1].key(), self.order[2].key(),
            if self.conflict { " CONFLICT (nothing applied)" } else { "" }, stacks(0), stacks(1),
            self.soul.map_or("none".to_string(), |(t, e)| format!("{} {}", side(t), e.key())), count('K'), count('B'),
            self.executes, self.procs[0], self.procs[1], self.procs[2], self.procs[3], self.procs[4], self.procs[5], self.burnt,
            self.ocean_healed, self.shields, self.boosts, self.neutralized, self.stats, self.deal_way));
    }
}

// ===================== 比赛钩子 =====================

/// 每份模拟每 tick 跑一次大小龙。游戏一个 mod 只有一个比赛钩子：单独装时本包自己设；附加包合集里由 league_addons 的
/// `BundleMatch` 转发（和卡尔萨斯的 `Respawns`、彩蛋的 `Eggs`、卢锡安的 `Aim` 一起）。
pub struct Dragons;

impl StableMatchHook for Dragons {
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
    wlog(format!(
        "=== {ID} v{VERSION} (League's elemental drakes in League's order with stacks that replace the game's drake buff, Dragon Soul, the Elder Dragon's burn and execute, Baron Nashor's hand and empowered minions; notices and a HUD on screen) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    // one match hook and one client extension a mod: league_addons forwards to Dragons and calls screen::draw itself
    #[cfg(not(league_bundle))]
    {
        module.set_match_hook(Dragons);
        module.set_extension(screen::Overlay);
    }
    #[cfg(league_bundle)]
    let _ = &module;
    host.log(LogLevel::Info, "league_dragons loaded (League's drakes, soul, Elder Dragon and Baron).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod mock;

#[cfg(test)]
pub(crate) mod tests;

#[cfg(test)]
mod texts;
