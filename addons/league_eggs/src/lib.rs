//! 英雄联盟彩蛋（用户 2026-11-05：「另外英雄联盟的彩蛋也可以做了吧？现在只有霞洛联动 狮子狗螳螂的 把剩下的做完吧」「我说的是
//! 这种彩蛋 不是加语音包」）：英雄之间的小互动，全在一个比赛钩子里（`Eggs`，每份模拟每 tick 跑一次）。
//!
//! 一、宿命对决（只算对面两队）：
//! - **狩猎开始**（雷恩加尔 vs 卡兹克）：两个都到 11 级（英雄联盟 18 级里的 16 级换到 TFM2 的 12 级）时大字公告「狩猎开始！」，
//!   之后第一个击杀或助攻击杀对方的赢，公告「狩猎结束！」。奖励照旧是主包数据里的（雷恩加尔的战利品、卡兹克多一次进化）。
//! - **弗雷尔卓德之战**（艾希、瑟庄妮、丽桑卓里至少两个在对面两队）：全场击杀 + 助攻到 20 时公告；之后第一个击杀或助攻击杀
//!   对面女王的成为「弗雷尔卓德的女王」：公告，头上挂 `league_eggs_crown_<她>`（死了复活再挂上，整局都在；画面要主包数据里的
//!   view_buffs 条目，见 README），玩家栏里她的头像上画一个冰冠冕。
//! - **警察抓小偷**（金克丝 vs 凯特琳 / 蔚）：每次击杀或助攻对面 +1 金币；玩家栏里头像上的数字是「抓捕的罪犯」「甩掉的条子」。
//! - **钓鱼执法**（锤石 vs 赛娜 / 卢锡安）：锤石击杀赛娜吸收她的灵魂（护甲、法强），赛娜击杀锤石解放灵魂（暴击、射程），
//!   卢锡安击杀锤石也算（少一半）；各最多 3 层，整局都在。
//! - **时光老头与装甲熊**（基兰 vs 沃利贝尔）：开局各挂一个只有名字的 buff（「装甲熊异见分子」「时光老头的仇恨」），击杀对方 +11 金币。
//!
//! 二、趣味属性互动：婕拉 / 赛恩互杀 +2 金币；婕拉和茂凯同队离得近各 +1% 移速；同队每多一个忍者（慎、凯南、阿卡丽、劫）每个
//! 忍者最大生命 −1；美洲狮形态的奈德丽身边等级比她低的队友每 5 秒 +5（经验写不进去，给金币）；戴墨镜的英雄身上每层莱昂娜的
//! 烈阳配一层 `league_leona_shades`（少受 1%：太阳镜防晒）；菲兹的鲨鱼咬死的小约德尔人尸体 15 tick 后被吞掉（放逐，鲨鱼吃小
//! 矮子）——这两个的数据那一半在主包的莱昂娜、菲兹里，钩子这一半在 `shades_shark.rs`。
//!
//! 三、玩法在别处、本包只放提示的（0.2.0，用户 2026-11-09：「我需要所有彩蛋都要有提示 你看看哪些没有的补进去」）：雷恩加尔 /
//! 卡兹克第一次看见对方、战利品和额外进化（主包他们的数据挂的 buff）；光合作用（league_zyra 挂在婕拉身上的标记）；蛇女不需要鞋
//! （开局：主包和 league_cassiopeia）；霞洛联动（开局，洛第一次分到霞的 W、他的 E 第一次落在霞身上：主包的数据挂的 buff）；
//! 6、9 也各有提示。别的附加包不用自己画提示：本包从 buff、击杀记录、阵容里认出来。
//!
//! 谁杀了谁读游戏的击杀记录（league_akshan 的读法：位置就是分路）。每份模拟的状态按 `SIM_TAG`（`league_eggs_sim:<编号>`，挂在
//! 两边的水晶上，水晶不收时挂在防御塔上；阵容里没有彩蛋英雄的那一场什么都不挂）记：服务器同一局并排跑两份预演，种子、来历、实体
//! 编号全都一样，只按这些记会串。屏幕上的公告和头像上的计数见 `notice.rs`。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_eggs.log`，每次启动游戏重写，上一次的留在 .prev.log。屏幕上那一场
//! 每行都记，预演限了条数：`EGGS`（开局有哪些彩蛋）、`HUNT ON` / `HUNT WON`、`QUEENS ON` / `QUEEN`、`COPS`、`SOUL`、`BOUNTY`、
//! `BUFF`（第一次挂上）/ `KEEP`（复活后补回）、`PLANTS`、`CHARM`、`SHADES`（墨镜层数涨了）/ `SHADES REFUSED`、`EATEN`
//! （吞掉一具尸体；宿主不收放逐时带 `REFUSED by the host`）、`SIGHT`（第一次看见对方）、`TROPHY` / `EVOLVED`、`SUNLIT`、
//! `DUO W` / `DUO E`、`END`（一局的汇总），屏幕上的 `VIEW`、`NOTE`、`BADGE`。

use std::collections::{BTreeMap, HashMap};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod notice;
pub mod rules;
pub mod shades_shark;

use notice::{Badge, BadgeKind, Note, What};
use rules::{Active, Hero, Near, Seat, Soul, Takedown};

const ID: &str = "league_eggs";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_eggs") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

// ---- buff 的名字
/// 这份模拟的编号，挂在水晶和防御塔上（league.dll 的分叉校验不看带 `_sim:` 的 buff）。
pub const SIM_TAG: &str = "league_eggs_sim:";
/// 冰雪女王的冠冕：`league_eggs_crown_ashe` / `_sejuani` / `_lissandra`（每个女王一个，画面按她的头顶高度）。
pub const CROWN: &str = "league_eggs_crown_";
/// 锤石吸收的灵魂；赛娜 / 卢锡安解放的灵魂。
pub const SOUL: &str = "league_eggs_soul";
pub const FREED: &str = "league_eggs_freed";
/// 基兰的「装甲熊异见分子」、沃利贝尔的「时光老头的仇恨」：只有名字。
pub const DISSIDENT: &str = "league_eggs_bear_dissident";
pub const GRUDGE: &str = "league_eggs_old_grudge";
/// 婕拉和茂凯结伴；忍者的孤独。
pub const PLANTS: &str = "league_eggs_plants";
pub const NINJA: &str = "league_eggs_ninja";
/// 主包奈德丽的美洲狮形态（tools/kit/build_nidalee.py 的 `cg`）。
pub const COUGAR: &str = "league_nidalee_cg";

// ---- 别处挂的 buff，本包只读，认出来放提示（0.2.0；测试 `the_buffs_read_from_elsewhere_are_there` 核对它们还在）
/// 1 第一次碰面：主包雷恩加尔 / 卡兹克看见对方时自己挂上的 `met`（永久，每条命一次：愤怒标记和台词，tools/kit/build_rengar.py /
/// build_khazix.py 的 `rival`）。
pub const RENGAR_MET: &str = "league_rengar_met";
pub const KHAZIX_MET: &str = "league_khazix_met";
/// 1 的奖励（主包的数据，每条命一次）：雷恩加尔击杀卡兹克的战利品（攻击力 `t_bonus`%）、卡兹克击杀雷恩加尔的额外进化
/// （攻击力 `rv_bonus`%，还有下一阶的进化）。
pub const TROPHY: &str = "league_rengar_trophy";
pub const RIVAL_EVO: &str = "league_khazix_rv_evo";
/// 7 光合作用：league_zyra（0.1.6 起）的 sun.rs 让一株植物变大时挂在婕拉身上的标记（只有名字，60 tick）。
pub const SUN_GREW: &str = "league_zyra_sun_grew";
/// 霞洛联动（主包，tools/fix/rakan_xayah_duo.py）：洛带着霞 W 的标记普攻时挂上的 W 加成；洛的 E 给护盾时挂在目标身上的标记。
pub const RAKAN_DUO_W: &str = "league_rakan_duo_w";
pub const RAKAN_E: &str = "league_rakan_e_on";

/// 第一次读到时已经过去这么久的击杀不算（状态中途重建时不把旧的再给一遍）。
const RECENT: usize = 120;
/// 状态最多留这么多份（最久没跑的先丢）。
const MOST: usize = 512;
/// 开局后这么久以内找不到水晶和塔（它们在第 0 tick 之后才出现）：下一 tick 再找，不记日志；过了才按 `RETRY` 找、记 `NO ANCHOR`
/// （0.1.1：0.1.0 在第 0 tick 一个都没找到就等 `RETRY`，每份有彩蛋的模拟都在第 600 tick 才编号、算作中途重建，开局公告一条都没放）。
const LATE: usize = 120;
/// 开局公告放在开局后这么久（屏幕时钟过了 0:01 才走）。
const START_NOTE: usize = 120;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_EGGS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_eggs.log");
        }
    }
    PathBuf::from("league_eggs.log")
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

const LOG_FIRST: usize = 60;
const LOG_EVERY: usize = 200;

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

/// 屏幕放的那些模拟（自己的比赛、观战、回放）：它们的事画到屏幕上。
fn screen_of(o: &SimOriginV1) -> Option<(u64, u64)> {
    matches!(SimOriginKindV1::from_code(o.kind),
        Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay))
        .then_some((o.match_id, o.set_index))
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

fn tag_on(sim: &StableSim<'_>, id: usize) -> Option<u64> {
    let e = sim.get_entity(id)?;
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find_map(|b| parse_tag(b.name()))
}

/// 挂编号的地方：两边的水晶（整局都在）；(水晶, 防御塔)，水晶不收 buff 时才挂到塔上。
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

/// 阵容里有没有彩蛋（还有玩家没有英雄：None，下一 tick 再看）：没有彩蛋的模拟一个 buff 都不挂。
fn has_eggs(sim: &StableSim<'_>) -> Option<bool> {
    let mut cast = Vec::new();
    for i in 0..sim.player_count() {
        let p = sim.player_at(i)?;
        let name = p.champion().and_then(|c| c.name())?;
        if let Some(hero) = Hero::of(&name) {
            cast.push(Seat { player: p.id(), team: p.team(), hero });
        }
    }
    (sim.player_count() > 0).then(|| Active::of(&cast).any())
}

/// The cast's fingerprint: every player's champion in player order (None while a player has none yet). The same for every
/// simulation of one match's set (the presim twins, the screen's two runs); `DefaultHasher::new()` hashes alike in every run.
fn cast_print(sim: &StableSim<'_>) -> Option<u64> {
    use std::hash::{Hash, Hasher};
    let mut h = std::collections::hash_map::DefaultHasher::new();
    let n = sim.player_count();
    for i in 0..n {
        sim.player_at(i)?.champion()?.name()?.hash(&mut h);
    }
    (n > 0).then(|| h.finish())
}

fn hush(origin: Origin, cast: u64) {
    let mut q = QUIET.lock().unwrap_or_else(|e| e.into_inner());
    if q.len() > 4 * MOST {
        q.clear();
    }
    q.insert(origin, cast);
}

/// Quiet: its origin was found without eggs (`found`: that cast's print) with this very cast (0.1.1, 11-06's audit: the
/// origin alone - a presim carries no set, so another set of the match differs only by its seed - could have silenced a
/// simulation with eggs).
pub fn quiet_for(found: Option<u64>, cast: Option<u64>) -> bool {
    found.is_some() && found == cast
}

#[derive(Default)]
struct Book {
    sims: HashMap<u64, Sim>,
    by_origin: HashMap<Origin, Vec<u64>>,
}

static BOOK: LazyLock<Mutex<Book>> = LazyLock::new(|| Mutex::new(Book::default()));
static NEXT: AtomicU64 = AtomicU64::new(1);
static STAMP: AtomicU64 = AtomicU64::new(1);
/// 来历 -> 到这一 tick 前不再找（没有水晶和塔可挂编号的模式：每 `RETRY` tick 才再找一次；挂不上去：usize::MAX，这份不跑）。
static WAIT: LazyLock<Mutex<HashMap<Origin, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
const RETRY: usize = 600;

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

/// 这份模拟的编号：先看同来历的那些编号挂在不在它们的水晶 / 塔上；都不在就在这份模拟里找水晶和塔，有编号用它（状态丢了重建），
/// 没有就抽一个新的挂上。
fn find(sim: &mut StableSim<'_>, origin: Origin) -> Option<u64> {
    let now = sim.tick();
    let cands: Vec<(u64, Vec<usize>)> = {
        let book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
        book.by_origin
            .get(&origin)
            .map(|v| v.iter().filter_map(|no| book.sims.get(no).map(|s| (*no, s.anchors.clone()))).collect())
            .unwrap_or_default()
    };
    for (no, anchors) in &cands {
        if anchors.iter().any(|&a| tag_on(sim, a) == Some(*no)) {
            return Some(*no);
        }
    }
    if WAIT.lock().unwrap_or_else(|e| e.into_inner()).get(&origin).is_some_and(|&until| waiting(until, now)) {
        return None;
    }
    let (nexus, towers) = anchors(sim);
    let all: Vec<usize> = nexus.iter().chain(&towers).copied().collect();
    if all.is_empty() {
        // the buildings come after tick 0 (0.1.0's logs: NO ANCHOR at t=0 in every simulation, numbered at RETRY as
        // late): every tick until LATE, quietly
        if now < LATE {
            return None;
        }
        wait(origin, now + RETRY);
        if let Some(k) = counted("no anchor") {
            wlog(format!("{} NO ANCHOR: no nexus and no tower to number this simulation - no eggs, again in {RETRY} ticks #{k}",
                         head(sim)));
        }
        return None;
    }
    let (no, fresh, mut anchors) = match all.iter().find_map(|&a| tag_on(sim, a)) {
        Some(no) => (no, false, all.iter().copied().filter(|&a| tag_on(sim, a) == Some(no)).collect()),
        None => {
            // a new simulation: numbered only when it has eggs at all
            match has_eggs(sim) {
                None => return None,
                Some(false) => {
                    if let Some(cast) = cast_print(sim) {
                        hush(origin, cast);
                    }
                    return None;
                }
                Some(true) => {}
            }
            (NEXT.fetch_add(1, Ordering::Relaxed), true, Vec::new())
        }
    };
    if fresh {
        // the nexuses; the towers only when no nexus takes it
        for group in [&nexus, &towers] {
            for &a in group.iter() {
                sim.add_buff(a, &BuffV1::named(&tag(no)));
            }
            anchors = all.iter().copied().filter(|&a| tag_on(sim, a) == Some(no)).collect();
            if !anchors.is_empty() {
                break;
            }
        }
        if anchors.is_empty() {
            wait(origin, usize::MAX);
            if let Some(k) = counted("refused") {
                wlog(format!("{} TAG REFUSED: none of {} nexus / towers took the buff - no eggs in this simulation #{k}",
                             head(sim), all.len()));
            }
            return None;
        }
    }
    // late = its number was there and its state was lost (0.1.0 also counted a new number past LATE: every egg simulation)
    let late = !fresh;
    let read = if late { sim.kill_log_count() } else { 0 };
    let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    let made = !book.sims.contains_key(&no);
    let s = book.sims.entry(no).or_insert_with(|| Sim::new(no, origin, now, late, read));
    s.anchors = anchors;
    let ids = book.by_origin.entry(origin).or_default();
    if !ids.contains(&no) {
        ids.push(no);
    }
    if made {
        evict(&mut book);
    }
    drop(book);
    if made && late {
        if let Some(k) = counted("rebuilt") {
            wlog(format!("{} REBUILT sim #{no} (tag found, kill log from {read}) #{k}", head(sim)));
        }
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

/// 来历 -> 那时阵容的指纹（[`cast_print`]）：这场没有彩蛋里的英雄（同一来历的模拟阵容都一样：并排的预演、屏幕上的两遍）：不再找
/// 编号，每 tick 只看一眼来历和阵容。0.1.1（11-06 的审查）：阵容也要一样才算，来历撞上了的另一场阵容不会被当成没有彩蛋。
static QUIET: LazyLock<Mutex<HashMap<Origin, u64>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn run(sim: &mut StableSim<'_>) {
    let o = sim.sim_origin().unwrap_or_default();
    let origin: Origin = (o.kind, o.match_id, o.set_index, o.replay_id, sim.seed());
    let screen = screen_of(&o);
    // the screen's match, eggs or none: a match without them must not show the last one's notes (league_akshan 0.2.3)
    if let Some((m, s)) = screen {
        notice::note_view(m, s);
    }
    let quiet = QUIET.lock().unwrap_or_else(|e| e.into_inner()).get(&origin).copied();
    // (the cast is read only for an origin found quiet: every simulation without eggs, a glance at its champions a tick)
    if quiet.is_some() && quiet_for(quiet, cast_print(sim)) {
        return;
    }
    let Some(no) = find(sim, origin) else { return };
    // out of the book while it runs (another simulation on another thread can look its own up meanwhile)
    let Some(mut st) = BOOK.lock().unwrap_or_else(|e| e.into_inner()).sims.remove(&no) else { return };
    st.stamp = STAMP.fetch_add(1, Ordering::Relaxed);
    if !st.ended {
        st.step(sim, screen);
    }
    let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    if st.active.as_ref().is_some_and(|a| !a.any()) {
        // (numbered before the cast was read: a state rebuilt without eggs)
        if let Some(v) = book.by_origin.get_mut(&origin) {
            v.retain(|&n| n != no);
            if v.is_empty() {
                book.by_origin.remove(&origin);
            }
        }
        drop(book);
        if let Some(cast) = cast_print(sim) {
            hush(origin, cast);
        }
        return;
    }
    book.sims.insert(no, st);
}

/// 这个玩家现在的英雄（死了还没复活时是他的尸体）身上的这个 buff：(英雄的实体, 那个 buff)。
fn worn(sim: &StableSim<'_>, player: usize, name: &str) -> Option<(usize, BuffV1)> {
    let e = sim.get_player(player)?.champion()?;
    let id = e.id();
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == name).map(|b| (id, b))
}

/// 一份模拟里的彩蛋。
struct Sim {
    no: u64,
    origin: Origin,
    anchors: Vec<usize>,
    stamp: u64,
    born: usize,
    late: bool,
    ended: bool,
    /// 击杀记录读到第几条。
    read: usize,
    /// 彩蛋里的英雄；(队伍, 分路) -> 玩家；玩家 -> (队伍, 分路)；玩家 -> 他的英雄 id（每个玩家，彩蛋以外的也有：公告里的名字）。
    cast: Vec<Seat>,
    lanes: HashMap<(usize, u32), usize>,
    seat_of: HashMap<usize, (usize, u32)>,
    names: HashMap<usize, String>,
    active: Option<Active>,
    hunt_on: Option<usize>,
    hunt_won: Option<usize>,
    queens_on: Option<usize>,
    queen: Option<usize>,
    /// 警察抓小偷：玩家 -> 击杀 / 助攻对面的次数。
    counts: BTreeMap<usize, usize>,
    /// 钓鱼执法：玩家 -> (怎么得的, 层数)。
    souls: BTreeMap<usize, (Soul, usize)>,
    plants_met: bool,
    plants_on: bool,
    charmed: bool,
    /// 挂过的 (玩家, buff)：第一次记 BUFF，之后（复活）记 KEEP。
    hung: Vec<(usize, String)>,
    gold: i64,
    keeps: usize,
    /// 6 太阳镜防晒：一局里新挂上的墨镜层数；9 鲨鱼吃小矮子：这份模拟里的鲨鱼（排着要吞的尸体、吞掉的）。
    shades: usize,
    shark: shades_shark::Shark,
    /// 0.2.0 的提示：放过「太阳镜防晒」的戴墨镜的人；第一次碰面、光合作用、霞洛联动的 W / E 在哪个 tick（一局一条）；
    /// 放过的战利品 / 额外进化（英雄的实体, buff）：每条命一条。
    shaded: Vec<usize>,
    sighted: Option<usize>,
    sunlit: Option<usize>,
    duo_w: Option<usize>,
    duo_e: Option<usize>,
    rewards: Vec<(usize, &'static str)>,
}

impl Sim {
    fn new(no: u64, origin: Origin, now: usize, late: bool, read: usize) -> Sim {
        Sim {
            no,
            origin,
            anchors: Vec::new(),
            stamp: STAMP.fetch_add(1, Ordering::Relaxed),
            born: now,
            late,
            ended: false,
            read,
            cast: Vec::new(),
            lanes: HashMap::new(),
            seat_of: HashMap::new(),
            names: HashMap::new(),
            active: None,
            hunt_on: None,
            hunt_won: None,
            queens_on: None,
            queen: None,
            counts: BTreeMap::new(),
            souls: BTreeMap::new(),
            plants_met: false,
            plants_on: false,
            charmed: false,
            hung: Vec::new(),
            gold: 0,
            keeps: 0,
            shades: 0,
            shark: shades_shark::Shark::default(),
            shaded: Vec::new(),
            sighted: None,
            sunlit: None,
            duo_w: None,
            duo_e: None,
            rewards: Vec::new(),
        }
    }

    fn hero(&self, player: usize) -> Option<Hero> {
        self.cast.iter().find(|s| s.player == player).map(|s| s.hero)
    }

    /// The player's champion id: the egg hero's, else the one the simulation names (0.1.1: a non-egg ally in the cougar's
    /// note was `player8` on screen - notice.rs shows an id's champion name, and `player8` is none), else `player<n>`.
    fn id(&self, player: usize) -> String {
        match self.hero(player) {
            Some(h) => h.id().to_string(),
            None => self.names.get(&player).cloned().unwrap_or_else(|| format!("player{player}")),
        }
    }

    fn who(&self, player: usize) -> String {
        format!("{}(p{player})", self.id(player).trim_start_matches("league_"))
    }

    /// 屏幕上那一场的一条公告（别的模拟不记）。
    fn note(&self, screen: Option<(u64, u64)>, tick: usize, what: What) {
        if let Some((m, s)) = screen {
            notice::note(Note { m, s, tick, what });
        }
    }

    fn badge(&self, screen: Option<(u64, u64)>, tick: usize, player: usize, kind: BadgeKind, value: usize) {
        if let (Some((m, s)), Some(&(team, lane))) = (screen, self.seat_of.get(&player)) {
            notice::badge(Badge { m, s, tick, team, lane: lane as usize, kind, value });
        }
    }

    fn step(&mut self, sim: &mut StableSim<'_>, screen: Option<(u64, u64)>) {
        let now = sim.tick();
        if self.active.is_none() && !self.read_cast(sim, screen) {
            return;
        }
        let Some(active) = self.active.clone() else { return };
        if active.any() {
            self.read_kills(sim, &active, now, screen);
            self.stages(sim, &active, now, screen);
            self.keep(sim, &active, now, screen);
            self.charm(sim, &active, now, screen);
            if !active.shades.is_empty() {
                for (p, n) in shades_shark::shades_tick(sim, &active.shades, screen.is_some()) {
                    self.shades += n;
                    // 6: one toast a wearer a match, the first time his shades go on
                    if !self.shaded.contains(&p) {
                        self.shaded.push(p);
                        if let Some(l) = rules::leona_across(&self.cast, p) {
                            self.note(screen, now, What::Shades { wearer: self.id(p), leona: self.id(l) });
                        }
                    }
                }
            }
            if !active.prey.is_empty() {
                let before = self.shark.eaten.len();
                self.shark.tick(sim, screen.is_some());
                // 9: a toast for every body swallowed (a banish the host refused swallowed nothing)
                let gulped: Vec<String> = self.shark.eaten[before..].iter().filter(|e| e.1).map(|e| e.0.clone()).collect();
                for yordle in gulped {
                    self.note(screen, now, What::Swallowed { fizz: shades_shark::FIZZ.to_string(), yordle });
                }
            }
            self.watch(sim, &active, now, screen);
        }
        if sim.is_end() {
            self.ended = true;
            if active.any() {
                self.end(sim, screen);
            }
        }
    }

    /// 阵容：每个玩家的队伍、分路、英雄。全部玩家都有英雄时才算读好（-> true），定下开了哪些彩蛋。
    fn read_cast(&mut self, sim: &mut StableSim<'_>, screen: Option<(u64, u64)>) -> bool {
        let mut cast = Vec::new();
        let mut lanes = HashMap::new();
        let mut seat_of = HashMap::new();
        let mut names = HashMap::new();
        let n = sim.player_count();
        if n == 0 {
            return false;
        }
        for i in 0..n {
            let Some(p) = sim.player_at(i) else { return false };
            let Some(name) = p.champion().and_then(|c| c.name()) else { return false };
            if let Some(lane) = p.lane().map(|l| l.code()) {
                lanes.insert((p.team(), lane), p.id());
                seat_of.insert(p.id(), (p.team(), lane));
            }
            if let Some(hero) = Hero::of(&name) {
                cast.push(Seat { player: p.id(), team: p.team(), hero });
            }
            names.insert(p.id(), name);
        }
        let active = Active::of(&cast);
        (self.cast, self.lanes, self.seat_of, self.names) = (cast, lanes, seat_of, names);
        let now = sim.tick();
        if active.any() {
            let who: Vec<String> = self.cast.iter().map(|s| format!("{} t{}", self.who(s.player), s.team)).collect();
            say(screen.is_some(), "eggs", format!("{} EGGS sim #{} {:?}{}: {}", head(sim), self.no, active.names(),
                                                  if self.late { " (late)" } else { "" }, who.join(", ")));
            if !self.late {
                self.start_notes(&active, now, screen);
            }
        }
        self.active = Some(active);
        true
    }

    /// 开局的公告：一里的警察抓小偷、钓鱼执法、时光老头与装甲熊是大字，二里的忍者、三里的蛇女不需要鞋和霞洛联动是小提示
    /// （另外两个任务到了时候才公告）。开局 `START_NOTE` tick 后才放：屏幕时钟走过 0:01 才开始算（game_places::clock）。
    fn start_notes(&self, a: &Active, now: usize, screen: Option<(u64, u64)>) {
        if screen.is_none() {
            return;
        }
        let now = now + START_NOTE;
        let ids = |v: &[Seat]| v.iter().map(|s| s.hero.id().to_string()).collect::<Vec<_>>();
        if let Some(c) = &a.chase {
            self.note(screen, now, What::CopsStart { cops: ids(&c.cops), robbers: ids(&c.robbers) });
        }
        if let Some((t, o)) = &a.fishing {
            self.note(screen, now, What::FishStart { thresh: ids(t), others: ids(o) });
        }
        if let Some((z, v)) = a.bears {
            self.note(screen, now, What::BearsStart { zilean: self.id(z), volibear: self.id(v) });
        }
        // ninjas: one toast a team
        let mut teams: Vec<usize> = a.ninjas.iter().filter_map(|(p, _)| self.seat_of.get(p).map(|s| s.0)).collect();
        teams.sort();
        teams.dedup();
        for team in teams {
            let mine: Vec<&(usize, i32)> =
                a.ninjas.iter().filter(|(p, _)| self.seat_of.get(p).map(|s| s.0) == Some(team)).collect();
            if let Some(&&(_, hp)) = mine.first() {
                self.note(screen, now, What::Ninjas { ninjas: mine.iter().map(|(p, _)| self.id(*p)).collect(), hp });
            }
        }
        // 10 Cassiopeia's bare feet; Xayah and Rakan on one team
        for &c in &a.barefoot {
            self.note(screen, now, What::Barefoot { cassiopeia: self.id(c) });
        }
        if let Some((x, r)) = a.duo {
            self.note(screen, now, What::DuoStart { xayah: self.id(x), rakan: self.id(r) });
        }
    }

    /// 击杀记录的一条换成玩家：位置就是分路，死的那个在击杀者的对面。
    fn takedown(&self, k: &KillLogV1) -> Option<Takedown> {
        let killer_team = k.killer_team;
        let victim_team = 1 - killer_team.min(1);
        let victim = *self.lanes.get(&(victim_team, k.killed_position))?;
        let killer = self.lanes.get(&(killer_team, k.killer_position)).copied();
        let assists = k
            .assist_positions
            .iter()
            .take((k.assist_count as usize).min(4))
            .filter_map(|l| self.lanes.get(&(killer_team, *l)).copied())
            .collect();
        Some(Takedown { tick: k.tick, victim, killer, assists })
    }

    fn read_kills(&mut self, sim: &mut StableSim<'_>, a: &Active, now: usize, screen: Option<(u64, u64)>) {
        let n = sim.kill_log_count();
        if self.read > n {
            self.read = 0;
        }
        while self.read < n {
            let Some(k) = sim.kill_log_at(self.read) else { break };
            self.read += 1;
            if k.tick + RECENT < now {
                continue;
            }
            let Some(td) = self.takedown(&k) else {
                say(screen.is_some(), "no lane", format!("{} kill log #{}: no player in lane {} of the victim's team",
                                                         head(sim), self.read - 1, k.killed_position));
                continue;
            };
            self.on_takedown(sim, a, &td, now, screen);
        }
    }

    fn gold(&mut self, sim: &mut StableSim<'_>, player: usize, gold: i64) -> bool {
        let ok = sim.player_add_gold(player, gold);
        if ok {
            self.gold += gold;
        }
        ok
    }

    fn on_takedown(&mut self, sim: &mut StableSim<'_>, a: &Active, td: &Takedown, now: usize, screen: Option<(u64, u64)>) {
        let line = {
            let assists: Vec<String> = td.assists.iter().map(|&p| self.who(p)).collect();
            format!("{} {} down (killer {}, assists [{}])", head(sim), self.who(td.victim),
                    td.killer.map_or("-".to_string(), |p| self.who(p)), assists.join(", "))
        };
        // 1 the hunt, once both are at the stage
        if let (Some(pair), Some(_), None) = (a.hunt, self.hunt_on, self.hunt_won) {
            if let Some(w) = rules::hunt_winner(td, pair) {
                self.hunt_won = Some(w);
                let loser = if w == pair.0 { pair.1 } else { pair.0 };
                say(screen.is_some(), "hunt", format!("{line}: HUNT WON by {}", self.who(w)));
                self.note(screen, now, What::HuntWon { winner: self.id(w), loser: self.id(loser) });
            }
        }
        // 2 the Queen of the Freljord, once the war is on
        if let (Some(_), None) = (self.queens_on, self.queen) {
            if let Some(w) = rules::queen_winner(td, &a.queens) {
                self.queen = Some(w);
                say(screen.is_some(), "queen", format!("{line}: QUEEN {} - the ice crown", self.who(w)));
                self.note(screen, now, What::Queen { queen: self.id(w) });
                self.badge(screen, now, w, BadgeKind::Crown, 1);
            }
        }
        // 3 cops and robbers
        if let Some(c) = &a.chase {
            for p in rules::arrests(td, c) {
                let n = {
                    let n = self.counts.entry(p).or_insert(0);
                    *n += 1;
                    *n
                };
                let paid = self.gold(sim, p, rules::COP_GOLD);
                let robber = self.hero(p) == Some(Hero::Jinx);
                say(screen.is_some(), "cops", format!("{line}: COPS {} {} {n} (+{} gold {})", self.who(p),
                                                      if robber { "shook off cops" } else { "caught criminals" },
                                                      rules::COP_GOLD, if paid { "paid" } else { "REFUSED" }));
                let what = if robber {
                    What::Escaped { robber: self.id(p), n }
                } else {
                    What::Caught { cop: self.id(p), n }
                };
                self.note(screen, now, what);
                self.badge(screen, now, p, if robber { BadgeKind::Escapes } else { BadgeKind::Arrests }, n);
            }
        }
        // 4 souls
        if a.fishing.is_some() {
            if let Some((p, kind)) = rules::soul_event(td, &self.cast) {
                let n = {
                    let e = self.souls.entry(p).or_insert((kind, 0));
                    e.1 = (e.1 + 1).min(rules::SOUL_CAP);
                    e.1
                };
                let (d, ap, crit, range) = rules::soul_stats(kind, n);
                say(screen.is_some(), "soul", format!("{line}: SOUL {:?} by {} -> {n} (armor +{d}, ap +{ap}, crit +{crit}%, range +{range})",
                                                      kind, self.who(p)));
                let what = match kind {
                    Soul::Taken => What::SoulTaken { thresh: self.id(p), senna: self.id(td.victim), n },
                    _ => What::SoulsFreed { by: self.id(p), thresh: self.id(td.victim), n },
                };
                self.note(screen, now, what);
                self.badge(screen, now, p, if kind == Soul::Taken { BadgeKind::Souls } else { BadgeKind::Freed }, n);
            }
        }
        // 5 the old timer and the armored bear; 7 plants vs zombies
        for (on, x, y, gold, zombie) in [
            (a.bears.is_some(), Hero::Zilean, Hero::Volibear, rules::BEAR_GOLD, false),
            (a.zombies.is_some(), Hero::Zyra, Hero::Sion, rules::ZOMBIE_GOLD, true),
        ] {
            if !on {
                continue;
            }
            if let Some((p, g)) = rules::bounty(td, &self.cast, x, y, gold) {
                let paid = self.gold(sim, p, g);
                say(screen.is_some(), "bounty", format!("{line}: BOUNTY {} +{g} gold {}", self.who(p),
                                                        if paid { "paid" } else { "REFUSED" }));
                let (killer, victim) = (self.id(p), self.id(td.victim));
                self.note(screen, now, if zombie {
                    What::ZombieBounty { killer, victim }
                } else {
                    What::BearBounty { killer, victim }
                });
            }
        }
    }

    /// 任务的开始：雷恩加尔、卡兹克都到 11 级；全场击杀 + 助攻到 20。
    fn stages(&mut self, sim: &mut StableSim<'_>, a: &Active, now: usize, screen: Option<(u64, u64)>) {
        let quiet = self.late && now <= self.born + 1;
        if let (Some((r, k)), None) = (a.hunt, self.hunt_on) {
            let lv = |p: usize| sim.get_player(p).map_or(0, |x| x.level());
            let levels = (lv(r), lv(k));
            if rules::hunt_on(levels) {
                self.hunt_on = Some(now);
                say(screen.is_some(), "hunt", format!("{} HUNT ON: {} level {} and {} level {}{}", head(sim), self.who(r),
                                                      levels.0, self.who(k), levels.1, if quiet { " (late: no notice)" } else { "" }));
                if !quiet {
                    self.note(screen, now, What::HuntStart { rengar: self.id(r), khazix: self.id(k) });
                }
            }
        }
        if !a.queens.is_empty() && self.queens_on.is_none() {
            let total: usize =
                (0..sim.player_count()).filter_map(|i| sim.player_at(i)).map(|p| p.kills() + p.assists()).sum();
            if rules::queens_on(total) {
                self.queens_on = Some(now);
                let q: Vec<String> = a.queens.iter().map(|s| self.who(s.player)).collect();
                say(screen.is_some(), "queen", format!("{} QUEENS ON: kills + assists {total}, queens [{}]{}", head(sim),
                                                       q.join(", "), if quiet { " (late: no notice)" } else { "" }));
                if !quiet {
                    self.note(screen, now, What::QueensStart { queens: a.queens.iter().map(|s| self.id(s.player)).collect() });
                }
            }
        }
    }

    /// 这个玩家活着的英雄身上有没有这个 buff（属性也一样）；没有就挂上。-> 挂了（Some(英雄 id)）
    fn hang(&mut self, sim: &mut StableSim<'_>, player: usize, want: &BuffV1, screen: bool) -> Option<usize> {
        let p = sim.get_player(player).filter(|p| p.is_alive())?;
        let e = p.champion()?;
        let id = e.id();
        let have = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == want.name());
        let same = |b: &BuffV1| {
            (b.hp, b.defence, b.magic_power, b.crit_chance, b.range, b.move_speed_mult)
                == (want.hp, want.defence, want.magic_power, want.crit_chance, want.range, want.move_speed_mult)
        };
        match have {
            Some(b) if same(&b) => return None,
            Some(_) => {
                sim.entity_remove_buff(id, want.name());
            }
            None => {}
        }
        sim.add_buff(id, want);
        let key = (player, want.name().to_string());
        let first = !self.hung.contains(&key);
        if first {
            self.hung.push(key);
            say(screen, "buff", format!("{} BUFF {} on {} #{id} (hp {:+}, armor +{}, ap +{}, crit +{}%, range +{}, move speed +{}%)",
                                        head(sim), want.name(), self.who(player), want.hp, want.defence, want.magic_power,
                                        want.crit_chance, want.range, want.move_speed_mult));
        } else {
            self.keeps += 1;
            say(screen, "keep", format!("{} KEEP {} on {} #{id} (back after a death or changed)", head(sim), want.name(),
                                        self.who(player)));
        }
        Some(id)
    }

    fn drop_buff(&mut self, sim: &mut StableSim<'_>, player: usize, name: &str) -> usize {
        let Some(id) = sim.get_player(player).and_then(|p| p.champion()).map(|e| e.id()) else { return 0 };
        sim.entity_remove_buff(id, name)
    }

    /// 整局都在的 buff（死了复活就是新的英雄，补回去）：冠冕、灵魂、两个名字 buff、忍者；婕拉和茂凯离得近才有的移速。
    fn keep(&mut self, sim: &mut StableSim<'_>, a: &Active, now: usize, screen: Option<(u64, u64)>) {
        let on = screen.is_some();
        if let Some(q) = self.queen {
            if let Some(h) = self.hero(q) {
                let name = format!("{CROWN}{}", h.id().trim_start_matches("league_"));
                self.hang(sim, q, &BuffV1::named(&name), on);
            }
        }
        let souls: Vec<(usize, (Soul, usize))> = self.souls.iter().map(|(p, v)| (*p, *v)).collect();
        for (p, (kind, n)) in souls {
            let (d, ap, crit, range) = rules::soul_stats(kind, n);
            let mut b = BuffV1::named(if kind == Soul::Taken { SOUL } else { FREED });
            (b.defence, b.magic_power, b.crit_chance, b.range) = (d, ap, crit, range);
            self.hang(sim, p, &b, on);
        }
        if let Some((z, v)) = a.bears {
            self.hang(sim, z, &BuffV1::named(DISSIDENT), on);
            self.hang(sim, v, &BuffV1::named(GRUDGE), on);
        }
        for &(p, hp) in &a.ninjas {
            let mut b = BuffV1::named(NINJA);
            b.hp = hp;
            self.hang(sim, p, &b, on);
        }
        if let Some((z, m)) = a.plants {
            let alive = |p: usize| sim.get_player(p).is_some_and(|x| x.is_alive());
            let ids = |p: usize| sim.get_player(p).and_then(|x| x.champion()).map(|e| e.id());
            let near = match (ids(z), ids(m)) {
                (Some(i), Some(j)) => rules::plants_near((alive(z), alive(m)), sim.distance_sq(i, j)),
                _ => false,
            };
            if near {
                let mut b = BuffV1::named(PLANTS);
                b.move_speed_mult = rules::PLANTS_MS;
                self.hang(sim, z, &b, on);
                self.hang(sim, m, &b, on);
                if !self.plants_met {
                    self.plants_met = true;
                    self.note(screen, now, What::Plants { zyra: self.id(z), maokai: self.id(m) });
                }
                if !self.plants_on {
                    self.plants_on = true;
                    say(on, "plants", format!("{} PLANTS on: {} and {} together (+{}% move speed)", head(sim), self.who(z),
                                              self.who(m), rules::PLANTS_MS));
                }
            } else if self.plants_on {
                self.plants_on = false;
                let n = self.drop_buff(sim, z, PLANTS) + self.drop_buff(sim, m, PLANTS);
                say(on, "plants", format!("{} PLANTS off: {} and {} apart ({n} buffs off)", head(sim), self.who(z), self.who(m)));
            }
        }
    }

    /// 11 熟女的魅力：每 5 秒，美洲狮形态的奈德丽身边等级比她低的队友各 +5 金币（经验写不进去）。
    fn charm(&mut self, sim: &mut StableSim<'_>, a: &Active, now: usize, screen: Option<(u64, u64)>) {
        if a.nidalee.is_empty() || !rules::charm_due(now) {
            return;
        }
        for her in a.nidalee.clone() {
            let Some(p) = sim.get_player(her.player).filter(|p| p.is_alive()) else { continue };
            let level = p.level();
            let Some(me) = p.champion() else { continue };
            let id = me.id();
            let cougar = (0..me.buff_count()).filter_map(|i| me.buff_at(i)).any(|b| b.name() == COUGAR);
            if !cougar {
                continue;
            }
            let allies: Vec<Near> = (0..sim.player_count())
                .filter_map(|i| sim.player_at(i))
                .filter(|x| x.team() == her.team && x.id() != her.player)
                .map(|x| {
                    let e = x.champion().map(|c| c.id());
                    Near {
                        player: x.id(),
                        level: x.level(),
                        alive: x.is_alive() && e.is_some(),
                        dist_sq: e.map_or(u64::MAX, |e| sim.distance_sq(id, e)),
                    }
                })
                .collect();
            let lucky = rules::charmed(level, true, &allies);
            if lucky.is_empty() {
                continue;
            }
            let mut paid = Vec::new();
            for &q in &lucky {
                let ok = self.gold(sim, q, rules::CHARM_GOLD);
                paid.push(format!("{} lv{}{}", self.who(q), sim.get_player(q).map_or(0, |x| x.level()),
                                  if ok { "" } else { " REFUSED" }));
            }
            say(screen.is_some(), "charm", format!("{} CHARM {} (cougar, lv{level}): +{} gold each to [{}]", head(sim),
                                                   self.who(her.player), rules::CHARM_GOLD, paid.join(", ")));
            if !self.charmed {
                self.charmed = true;
                self.note(screen, now, What::Charm { nidalee: self.id(her.player),
                                                     allies: lucky.iter().map(|&q| self.id(q)).collect() });
            }
        }
    }

    /// 别处做的彩蛋（主包的数据、league_zyra）挂的 buff，第一次看见时放提示（0.2.0）：1 雷恩加尔 / 卡兹克第一次看见对方
    /// （先挂上 `met` 的那个看见了另一个；同一 tick 算雷恩加尔），战利品 / 额外进化（每条命一条）；7 婕拉身上 league_zyra 的
    /// 光合作用标记；霞洛联动：洛身上的 W 加成、霞身上洛的 E 的标记。状态中途重建（late）的第一眼看见的是以前的事：只记下、不提示。
    fn watch(&mut self, sim: &StableSim<'_>, a: &Active, now: usize, screen: Option<(u64, u64)>) {
        let quiet = self.late && now <= self.born + 1;
        let on = screen.is_some();
        let late = if quiet { " (late: no notice)" } else { "" };
        if let Some((r, k)) = a.hunt {
            if self.sighted.is_none() {
                let (rm, km) = (worn(sim, r, RENGAR_MET).is_some(), worn(sim, k, KHAZIX_MET).is_some());
                if rm || km {
                    self.sighted = Some(now);
                    let (seer, seen) = if rm { (r, k) } else { (k, r) };
                    say(on, "sight", format!("{} SIGHT {} spotted {} ({}){late}", head(sim), self.who(seer), self.who(seen),
                                             if rm && km { "both marks at once" } else { "the anger mark" }));
                    if !quiet {
                        self.note(screen, now, What::HuntSighted { seer: self.id(seer), seen: self.id(seen) });
                    }
                }
            }
            for (p, other, buff) in [(r, k, TROPHY), (k, r, RIVAL_EVO)] {
                let Some((e, b)) = worn(sim, p, buff) else { continue };
                if self.rewards.contains(&(e, buff)) {
                    continue;
                }
                self.rewards.push((e, buff));
                let pct = b.attack_mult;
                let trophy = buff == TROPHY;
                say(on, "reward", format!("{} {} {} #{e} on {}: attack +{pct}%{late}", head(sim),
                                          if trophy { "TROPHY" } else { "EVOLVED" }, self.who(p), self.who(other)));
                if !quiet {
                    let (me, them) = (self.id(p), self.id(other));
                    self.note(screen, now, if trophy {
                        What::Trophy { rengar: me, khazix: them, pct }
                    } else {
                        What::Evolved { khazix: me, rengar: them, pct }
                    });
                }
            }
        }
        if let (Some((z, l)), None) = (a.sun, self.sunlit) {
            if worn(sim, z, SUN_GREW).is_some() {
                self.sunlit = Some(now);
                say(on, "sunlit", format!("{} SUNLIT {}'s plant grew in {}'s sunlight ({SUN_GREW}){late}", head(sim),
                                          self.who(z), self.who(l)));
                if !quiet {
                    self.note(screen, now, What::Sunlit { leona: self.id(l), zyra: self.id(z) });
                }
            }
        }
        if let Some((x, r)) = a.duo {
            if self.duo_w.is_none() && worn(sim, r, RAKAN_DUO_W).is_some() {
                self.duo_w = Some(now);
                say(on, "duo", format!("{} DUO W {} shares {}'s Deadly Plumage ({RAKAN_DUO_W}){late}", head(sim), self.who(r),
                                       self.who(x)));
                if !quiet {
                    self.note(screen, now, What::DuoW { rakan: self.id(r), xayah: self.id(x) });
                }
            }
            if self.duo_e.is_none() && worn(sim, x, RAKAN_E).is_some() {
                self.duo_e = Some(now);
                say(on, "duo", format!("{} DUO E {}'s Battle Dance reached {} ({RAKAN_E}){late}", head(sim), self.who(r),
                                       self.who(x)));
                if !quiet {
                    self.note(screen, now, What::DuoE { rakan: self.id(r), xayah: self.id(x) });
                }
            }
        }
    }

    fn end(&mut self, sim: &StableSim<'_>, screen: Option<(u64, u64)>) {
        let a = self.active.clone().unwrap_or_default();
        let mut parts = vec![format!("eggs {:?}", a.names())];
        if a.hunt.is_some() {
            parts.push(format!("hunt on {:?} won by {}", self.hunt_on, self.hunt_won.map_or("-".into(), |p| self.who(p))));
        }
        if !a.queens.is_empty() {
            parts.push(format!("queens on {:?} queen {}", self.queens_on, self.queen.map_or("-".into(), |p| self.who(p))));
        }
        if a.chase.is_some() {
            let c: Vec<String> = self.counts.iter().map(|(p, n)| format!("{} {n}", self.who(*p))).collect();
            parts.push(format!("cops [{}]", c.join(", ")));
        }
        if a.fishing.is_some() {
            let c: Vec<String> = self.souls.iter().map(|(p, (k, n))| format!("{} {k:?} {n}", self.who(*p))).collect();
            parts.push(format!("souls [{}]", c.join(", ")));
        }
        if !a.shades.is_empty() {
            let w: Vec<String> = a.shades.iter().map(|&p| self.who(p)).collect();
            parts.push(format!("shades put on {} ([{}] against Leona)", self.shades, w.join(", ")));
        }
        if !a.prey.is_empty() {
            let e: Vec<String> = self.shark.eaten.iter()
                .map(|(n, ok)| format!("{}{}", n.trim_start_matches("league_"), if *ok { "" } else { " REFUSED" }))
                .collect();
            parts.push(format!("eaten [{}]", e.join(", ")));
        }
        if a.hunt.is_some() {
            let r: Vec<&str> = self.rewards.iter().map(|(_, b)| if *b == TROPHY { "trophy" } else { "evolution" }).collect();
            parts.push(format!("sighted {:?} rewards [{}]", self.sighted, r.join(", ")));
        }
        if a.sun.is_some() {
            parts.push(format!("photosynthesis {:?}", self.sunlit));
        }
        if a.duo.is_some() {
            parts.push(format!("duo W {:?} E {:?}", self.duo_w, self.duo_e));
        }
        parts.push(format!("gold given {}", self.gold));
        parts.push(format!("buffs put back {}", self.keeps));
        say(screen.is_some(), "end", format!("{} END sim #{}: {}", head(sim), self.no, parts.join("; ")));
    }
}

// ===================== 比赛钩子 =====================

/// 每份模拟每 tick 跑一次彩蛋。游戏一个 mod 只有一个比赛钩子：单独装时本包自己设；附加包合集里由 league_addons 的
/// `BundleMatch` 转发（和卡尔萨斯的 `Respawns` 一起）。
pub struct Eggs;

impl StableMatchHook for Eggs {
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
        "=== {ID} v{VERSION} (League easter eggs: rivalry quests, cops and robbers, souls, bounties, ninjas, plants, the cougar, Leona vs sunglasses, Fizz's shark; notices for every egg, also the hunt's first sight and rewards, photosynthesis, Cassiopeia's bare feet and Xayah and Rakan) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    // one match hook and one client extension a mod: league_addons forwards to Eggs and draws notice::draw itself
    #[cfg(not(league_bundle))]
    {
        module.set_match_hook(Eggs);
        module.set_extension(notice::Overlay);
    }
    #[cfg(league_bundle)]
    let _ = &module;
    host.log(LogLevel::Info, "league_eggs loaded (League easter eggs between our heroes).");
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
mod tests {
    use super::*;
    use mock::World;

    fn tick(w: &mut World) {
        mock::with_sim(w, |sim| Eggs.on_match_tick(sim, 0));
        w.tick += 1;
    }

    fn start(w: &mut World) {
        mock::with_sim(w, |sim| Eggs.on_match_start(sim));
    }

    fn number(w: &World) -> u64 {
        w.units[0].buffs.iter().find_map(|b| parse_tag(b.name())).expect("a tag on the nexus")
    }

    fn origin(w: &World) -> Origin {
        let o = w.origin.unwrap_or_default();
        (o.kind, o.match_id, o.set_index, o.replay_id, w.seed)
    }

    /// The whole hook on small simulations (one test: the book, the quiet origins and the screen's notes are globals).
    #[test]
    fn the_eggs_run_in_a_simulation() {
        std::env::set_var("LEAGUE_EGGS_LOG", std::env::temp_dir().join("league_eggs_test.log"));
        // ---- a presim: the hunt, the queens, cops and robbers, the bears, the cougar
        let base = World::new(9001, SimOriginKindV1::ServerPresim, [
            "league_rengar", "league_nidalee", "league_ashe", "league_jinx", "league_zilean",
            "league_khazix", "league_volibear", "league_sejuani", "league_caitlyn", "league_garen",
        ]);
        let mut a = base.clone();
        start(&mut a);
        let no = number(&a);
        let tagged = |w: &World| w.units[..4].iter().map(|u| u.buffs.iter().any(|b| parse_tag(b.name()).is_some())).collect::<Vec<_>>();
        assert_eq!(tagged(&a), vec![true, true, false, false], "both nexuses, no tower");
        assert!(a.has(4, DISSIDENT).is_some() && a.has(6, GRUDGE).is_some(), "the grudges from the start");
        tick(&mut a);
        // cops: Caitlyn takes Jinx down (Volibear helping: no cop), then Jinx Caitlyn
        a.kill(3, 8, &[6]);
        tick(&mut a);
        assert_eq!((a.players[8].gold, a.players[6].gold), (1, 0));
        a.kill(8, 3, &[]);
        // the bears: Zilean kills Volibear (Ashe's assist is no kill)
        a.kill(6, 4, &[2]);
        tick(&mut a);
        assert_eq!((a.players[3].gold, a.players[4].gold, a.players[2].gold), (1, 11, 0));
        // a presim twin: the same seed, origin and entity ids, run after it - its own number and its own gold
        let mut b = base.clone();
        start(&mut b);
        assert_ne!(number(&b), no);
        b.kill(3, 8, &[]);
        tick(&mut b);
        tick(&mut a);
        assert_eq!((b.players[8].gold, a.players[8].gold), (1, 1));
        // the hunt: Rengar's kill before level 11 wins nothing; at 11 Kha'Zix's assist on Rengar does
        a.kill(5, 0, &[]);
        tick(&mut a);
        (a.players[0].level, a.players[5].level) = (11, 11);
        tick(&mut a);
        a.kill(0, 7, &[5]);
        tick(&mut a);
        // the queens: kills + assists at 20, then Ashe kills Sejuani: the crown, through her death
        a.players[9].kills += 14;
        tick(&mut a);
        a.kill(7, 2, &[]);
        tick(&mut a);
        let crown = "league_eggs_crown_ashe";
        assert!(a.has(2, crown).is_some());
        a.respawn(2);
        assert!(a.has(2, crown).is_none());
        tick(&mut a);
        assert!(a.has(2, crown).is_some(), "the crown on her next life");
        // the cougar: Nidalee (level 8, cougar) beside Jinx (6) and Rengar (11): Jinx +5 at the next 5 s
        a.players[1].level = 8;
        a.players[3].level = 6;
        let her = a.players[1].champ;
        a.units[her].buffs.push(BuffV1::named(COUGAR));
        let her_at = a.units[her].at;
        let jinx = a.players[3].champ;
        let rengar = a.players[0].champ;
        a.units[jinx].at = (her_at.0 + 10_000, her_at.1);
        a.units[rengar].at = (her_at.0, her_at.1 + 10_000);
        let (jg, rg) = (a.players[3].gold, a.players[0].gold);
        while a.tick <= rules::CHARM_EVERY {
            tick(&mut a);
        }
        assert_eq!((a.players[3].gold, a.players[0].gold), (jg + 5, rg));
        {
            let book = BOOK.lock().unwrap();
            let s = book.sims.get(&no).expect("its state");
            assert_eq!((s.hunt_won, s.queen), (Some(5), Some(2)));
            assert_eq!(s.counts.get(&8), Some(&1));
            assert_eq!(s.counts.get(&3), Some(&1));
        }
        a.end = true;
        tick(&mut a);
        assert!(BOOK.lock().unwrap().sims.get(&no).is_some_and(|s| s.ended));

        // ---- no egg hero: quiet after the first look
        let mut q = World::new(9002, SimOriginKindV1::ServerPresim, ["league_garen"; 10]);
        start(&mut q);
        tick(&mut q);
        assert!(QUIET.lock().unwrap().contains_key(&origin(&q)));
        assert!(q.units.iter().all(|u| u.buffs.is_empty()), "not a single buff in a match without eggs");
        // ---- 0.1.1 (11-06's audit): the same origin with another cast (a presim carries no set: another set of the match
        // differs only by its seed) is not taken for quiet - its own eggs
        let mut q2 = World::new(9002, SimOriginKindV1::ServerPresim, [
            "league_zilean", "league_garen", "league_garen", "league_garen", "league_garen",
            "league_volibear", "league_garen", "league_garen", "league_garen", "league_garen",
        ]);
        assert_eq!(origin(&q2), origin(&q));
        start(&mut q2);
        tick(&mut q2);
        assert!(q2.has(0, DISSIDENT).is_some(), "the bears' grudge in the other cast");
        // and the quiet one stays quiet
        let mut q3 = World::new(9002, SimOriginKindV1::ServerPresim, ["league_garen"; 10]);
        start(&mut q3);
        tick(&mut q3);
        assert!(q3.units.iter().all(|u| u.buffs.is_empty()));
        assert!(!quiet_for(None, Some(1)) && !quiet_for(Some(1), None) && !quiet_for(Some(1), Some(2)) && quiet_for(Some(3), Some(3)));
        // ---- nexuses that take no buff: the towers carry the number
        let mut t = World::new(9005, SimOriginKindV1::ServerPresim, [
            "league_zilean", "league_garen", "league_garen", "league_garen", "league_garen",
            "league_volibear", "league_garen", "league_garen", "league_garen", "league_garen",
        ]);
        t.refuse = vec![EntityKindV1::Nexus];
        start(&mut t);
        tick(&mut t);
        assert_eq!(tagged(&t), vec![false, false, true, true]);
        assert!(t.has(0, DISSIDENT).is_some());
        // ---- buildings that take no buff: no eggs in that simulation
        let mut s = World::new(9003, SimOriginKindV1::ServerPresim, [
            "league_zilean", "league_garen", "league_garen", "league_garen", "league_garen",
            "league_volibear", "league_garen", "league_garen", "league_garen", "league_garen",
        ]);
        s.refuse = vec![EntityKindV1::Nexus, EntityKindV1::Tower];
        start(&mut s);
        tick(&mut s);
        assert!(s.has(0, DISSIDENT).is_none());
        assert_eq!(WAIT.lock().unwrap().get(&origin(&s)), Some(&usize::MAX));

        // ---- on screen: souls, plants and zombies, ninjas
        let mut v = World::new(9004, SimOriginKindV1::ClientMatchView, [
            "league_maokai", "league_zyra", "league_shen", "league_zed", "league_thresh",
            "league_akali", "league_sion", "league_kennen", "league_senna", "league_lucian",
        ]);
        start(&mut v);
        for p in [2, 3, 5, 7] {
            assert_eq!(v.has(p, NINJA).map(|b| b.hp), Some(-1), "ninja {p}");
        }
        // Zyra steps beside Maokai: +1% each; apart again: gone
        let mao = v.units[v.players[0].champ].at;
        let zyra = v.players[1].champ;
        v.units[zyra].at = (mao.0 + 30_000, mao.1);
        tick(&mut v);
        assert_eq!((v.has(0, PLANTS).map(|b| b.move_speed_mult), v.has(1, PLANTS).map(|b| b.move_speed_mult)),
                   (Some(1), Some(1)));
        v.units[zyra].at = (mao.0 + 300_000, mao.1);
        tick(&mut v);
        assert!(v.has(0, PLANTS).is_none() && v.has(1, PLANTS).is_none());
        // Thresh takes Senna's soul four times: three layers at most
        for _ in 0..4 {
            v.kill(8, 4, &[]);
            tick(&mut v);
        }
        let soul = v.has(4, SOUL).expect("Thresh's souls");
        assert_eq!((soul.defence, soul.magic_power), (3 * rules::SOUL_DEF, 3 * rules::SOUL_AP));
        // Lucian frees them (the smaller share); Zyra kills Sion: +2
        v.kill(4, 9, &[8]);
        v.kill(6, 1, &[]);
        tick(&mut v);
        let freed = v.has(9, FREED).expect("Lucian's freed souls");
        assert_eq!((freed.crit_chance, freed.range), (rules::LUCIAN_CRIT, rules::LUCIAN_RANGE));
        assert!(v.has(8, FREED).is_none(), "Senna only assisted");
        assert_eq!(v.players[1].gold, 2);
        // the screen got its notes and Thresh's badge
        let notes = notice::NOTES.lock().unwrap().clone();
        let mine: Vec<&notice::Note> = notes.iter().filter(|n| (n.m, n.s) == (77, 2)).collect();
        assert!(mine.iter().any(|n| matches!(n.what, What::FishStart { .. }) && n.tick == START_NOTE));
        assert!(mine.iter().any(|n| matches!(n.what, What::Ninjas { .. })));
        assert!(mine.iter().any(|n| matches!(n.what, What::Plants { .. })));
        assert_eq!(mine.iter().filter(|n| matches!(n.what, What::SoulTaken { .. })).count(), 4);
        assert!(mine.iter().any(|n| matches!(&n.what, What::ZombieBounty { killer, .. } if killer == "league_zyra")));
        let badges = notice::BADGES.lock().unwrap().clone();
        assert!(badges.iter().any(|b| b.kind == BadgeKind::Souls && (b.team, b.lane, b.value) == (0, 4, 3)));
        assert!(badges.iter().any(|b| b.kind == BadgeKind::Freed && (b.team, b.lane, b.value) == (1, 4, 1)));

        // ---- 0.1.1: the buildings come a few ticks after the start (0.1.0: NO ANCHOR at t=0 in every simulation, numbered
        // at RETRY 600 as late, no opening note on screen); the cougar's note names a non-egg ally by his champion (0.1.0:
        // 「熟女的魅力：奈德丽 带着 player8」)
        let mut c = World::new(9006, SimOriginKindV1::ClientMatchView, [
            "league_garen", "league_nidalee", "league_jinx", "league_garen", "league_garen",
            "league_caitlyn", "league_garen", "league_garen", "league_garen", "league_garen",
        ]);
        for u in &mut c.units[..4] {
            u.alive = false;
        }
        start(&mut c);
        for _ in 0..3 {
            tick(&mut c);
        }
        assert!(c.units.iter().all(|u| u.buffs.is_empty()), "no number before the buildings stand");
        assert!(WAIT.lock().unwrap().get(&origin(&c)).is_none(), "looked for again the next tick, quietly");
        for u in &mut c.units[..4] {
            u.alive = true;
        }
        tick(&mut c);
        let no_c = number(&c);
        assert!(BOOK.lock().unwrap().sims.get(&no_c).is_some_and(|s| !s.late && s.born == 3), "a new simulation, not a late one");
        // the cougar: Nidalee (8) beside Garen (6), Jinx (9) beside her too but not lower
        c.players[1].level = 8;
        c.players[0].level = 6;
        c.players[2].level = 9;
        let her = c.players[1].champ;
        c.units[her].buffs.push(BuffV1::named(COUGAR));
        let her_at = c.units[her].at;
        for (p, dx) in [(0, 10_000), (2, 20_000)] {
            let u = c.players[p].champ;
            c.units[u].at = (her_at.0 + dx, her_at.1);
        }
        while c.tick <= rules::CHARM_EVERY {
            tick(&mut c);
        }
        assert_eq!((c.players[0].gold, c.players[2].gold), (5, 0));
        let notes = notice::NOTES.lock().unwrap().clone();
        let mine: Vec<&notice::Note> = notes.iter().filter(|n| (n.m, n.s) == (77, 2)).collect();
        assert!(mine.iter().any(|n| matches!(n.what, What::CopsStart { .. }) && n.tick == 3 + START_NOTE),
                "the opening note {START_NOTE} ticks after the number");
        let charm = mine.iter().find_map(|n| match &n.what {
            What::Charm { nidalee, allies } => Some((nidalee.clone(), allies.clone())),
            _ => None,
        });
        assert_eq!(charm, Some(("league_nidalee".to_string(), vec!["league_garen".to_string()])));
        assert_eq!(BOOK.lock().unwrap().sims.get(&no_c).map(|s| s.who(0)), Some("garen(p0)".to_string()));
        // ---- no building at all past LATE: NO ANCHOR, looked for again RETRY ticks later
        let mut d = World::new(9007, SimOriginKindV1::ServerPresim, [
            "league_zilean", "league_garen", "league_garen", "league_garen", "league_garen",
            "league_volibear", "league_garen", "league_garen", "league_garen", "league_garen",
        ]);
        for u in &mut d.units[..4] {
            u.alive = false;
        }
        start(&mut d);
        while d.tick < LATE {
            tick(&mut d);
        }
        assert!(WAIT.lock().unwrap().get(&origin(&d)).is_none());
        tick(&mut d);
        assert_eq!(WAIT.lock().unwrap().get(&origin(&d)), Some(&(LATE + RETRY)));
    }

    /// Leona's shades and Fizz's shark through the whole hook, on presims only (the screen's notes are another test's).
    #[test]
    fn shades_follow_the_sunlight_and_the_shark_swallows_yordles() {
        use shades_shark::{EAT, GULP, GULP_AFTER, GULP_T, SHADES, SUNLIGHT};
        std::env::set_var("LEAGUE_EGGS_LOG", std::env::temp_dir().join("league_eggs_test.log"));
        let sun = || {
            let mut b = BuffV1::timed(SUNLIGHT, 90);
            b.damaged_amplify = 10;
            b
        };
        // Leona, Fizz and Vayne on one side; Lee Sin and Heimerdinger (shades), Tristana and Lulu (yordles) across
        let base = World::new(9101, SimOriginKindV1::ServerPresim, [
            "league_leona", "league_fizz", "league_vayne", "league_garen", "league_garen",
            "league_leesin", "league_tristana", "league_heimerdinger", "league_lulu", "league_garen",
        ]);
        let mut a = base.clone();
        start(&mut a);
        let no = number(&a);
        // two Sunlight on Lee Sin: two shades (1% less each); Vayne is Leona's ally: none
        for p in [5, 5, 2] {
            let c = a.players[p].champ;
            a.units[c].buffs.push(sun());
        }
        tick(&mut a);
        assert_eq!((a.count(5, SHADES), a.count(2, SHADES)), (2, 0));
        assert_eq!(a.has(5, SHADES).map(|b| (b.damaged_reduce, b.duration_tick)), Some((1, 2)));
        tick(&mut a);
        assert_eq!(a.count(5, SHADES), 2, "kept, not stacked again");
        // one runs out: one shade; all out: none
        let lee = a.players[5].champ;
        let i = a.units[lee].buffs.iter().position(|b| b.name() == SUNLIGHT).unwrap();
        a.units[lee].buffs.remove(i);
        tick(&mut a);
        assert_eq!(a.count(5, SHADES), 1);
        a.units[lee].buffs.retain(|b| b.name() != SUNLIGHT);
        tick(&mut a);
        assert_eq!(a.count(5, SHADES), 0);
        // the shark: Tristana dies bitten, Lulu dies unbitten, Heimerdinger bitten (his head is too big)
        for p in [6, 7] {
            let c = a.players[p].champ;
            a.units[c].buffs.push(BuffV1::timed(EAT, 2));
        }
        for p in [6, 7, 8] {
            a.die(p);
        }
        tick(&mut a);
        let tristana = a.players[6].champ;
        assert_eq!(a.units[tristana].banished, 0, "not before the shark dives");
        for _ in 0..GULP_AFTER {
            tick(&mut a);
        }
        assert_eq!((a.units[tristana].banished, a.units[tristana].lock.as_str()), (GULP_T, GULP));
        assert_eq!((a.champ(7).banished, a.champ(8).banished), (0, 0));
        // her next life is a new entity, not banished
        a.respawn(6);
        tick(&mut a);
        assert_eq!(a.champ(6).banished, 0);
        // a presim twin of the same origin and seed: its own shark, nobody eaten there
        let mut b = base.clone();
        start(&mut b);
        for _ in 0..=GULP_AFTER {
            tick(&mut b);
        }
        assert!(b.units.iter().all(|u| u.banished == 0));
        {
            let book = BOOK.lock().unwrap();
            let s = book.sims.get(&no).expect("its state");
            assert_eq!(s.shades, 2);
            assert_eq!(s.shark.eaten, vec![("league_tristana".to_string(), true)]);
            let twin = book.sims.get(&number(&b)).expect("the twin's state");
            assert!(twin.shark.eaten.is_empty());
        }
        // a host that refuses the banish: the body stays, the log says so
        let mut r = World::new(9102, SimOriginKindV1::ServerPresim, [
            "league_fizz", "league_garen", "league_garen", "league_garen", "league_garen",
            "league_annie", "league_garen", "league_garen", "league_garen", "league_garen",
        ]);
        r.refuse_banish = true;
        start(&mut r);
        let c = r.players[5].champ;
        r.units[c].buffs.push(BuffV1::timed(EAT, 2));
        r.die(5);
        for _ in 0..=GULP_AFTER {
            tick(&mut r);
        }
        assert_eq!(r.champ(5).banished, 0);
        let book = BOOK.lock().unwrap();
        assert_eq!(book.sims.get(&number(&r)).map(|s| s.shark.eaten.clone()),
                   Some(vec![("league_annie".to_string(), false)]));
    }

    /// 0.2.0's notices on the screen's match (77, 2, as every mock's view: another view would wipe the other screen
    /// test's notes): the eggs played elsewhere (the main pack's kits, league_zyra, league_cassiopeia) and shades_shark.rs
    /// each get their toast with the right names, once - the screen's second run adds nothing - and a presim draws none.
    #[test]
    fn every_egg_has_its_notice_once_on_screen() {
        use shades_shark::{EAT, GULP_AFTER, SUNLIGHT};
        std::env::set_var("LEAGUE_EGGS_LOG", std::env::temp_dir().join("league_eggs_test.log"));
        // Rengar vs Kha'Zix; Xayah and Rakan; Leona across Vayne; Fizz across Tristana; Zyra in Leona's match; Cassiopeia
        let cast = [
            "league_rengar", "league_xayah", "league_rakan", "league_leona", "league_fizz",
            "league_khazix", "league_vayne", "league_tristana", "league_zyra", "league_cassiopeia",
        ];
        let sun = || {
            let mut b = BuffV1::timed(SUNLIGHT, 90);
            b.damaged_amplify = 10;
            b
        };
        let reward = |name: &str, pct: i32| {
            let mut b = BuffV1::named(name);
            b.attack_mult = pct;
            b
        };
        // the same marks at the same ticks in every run
        let script = |w: &mut World| {
            start(w);
            tick(w);
            // Kha'Zix spots Rengar first (his kit's anger mark), Rengar him a tick later: one toast
            w.push(5, BuffV1::named(KHAZIX_MET));
            tick(w);
            w.push(0, BuffV1::named(RENGAR_MET));
            tick(w);
            tick(w);
            // Rengar takes Kha'Zix's head (kept on him: one toast), Kha'Zix evolves on Rengar
            w.push(0, reward(TROPHY, 15));
            tick(w);
            tick(w);
            w.push(5, reward(RIVAL_EVO, 10));
            tick(w);
            // two of Leona's Sunlight on Vayne: her shades go on; gone, then on again: no second toast
            w.push(6, sun());
            w.push(6, sun());
            tick(w);
            let v = w.players[6].champ;
            w.units[v].buffs.retain(|b| b.name() != SUNLIGHT);
            tick(w);
            w.push(6, sun());
            tick(w);
            // the shark: Tristana dies bitten and is swallowed
            w.push(7, BuffV1::timed(EAT, 2));
            w.die(7);
            for _ in 0..=GULP_AFTER {
                tick(w);
            }
            // league_zyra's photosynthesis marker on Zyra, twice: one toast
            w.push(8, BuffV1::timed(SUN_GREW, 60));
            tick(w);
            w.push(8, BuffV1::timed(SUN_GREW, 60));
            tick(w);
            // the duo: Rakan's share of her W, his E's shield on her
            w.push(2, BuffV1::timed(RAKAN_DUO_W, 90));
            tick(w);
            w.push(1, BuffV1::named(RAKAN_E));
            tick(w);
            tick(w);
            // Rengar's next life: nothing until he takes the head again
            w.respawn(0);
            tick(w);
            w.push(0, reward(TROPHY, 15));
            tick(w);
        };
        let ours = || -> Vec<Note> {
            notice::NOTES
                .lock()
                .unwrap()
                .iter()
                .filter(|n| {
                    (n.m, n.s) == (77, 2)
                        && matches!(n.what, What::HuntSighted { .. } | What::Trophy { .. } | What::Evolved { .. }
                            | What::Shades { .. } | What::Sunlit { .. } | What::Swallowed { .. } | What::Barefoot { .. }
                            | What::DuoStart { .. } | What::DuoW { .. } | What::DuoE { .. })
                })
                .cloned()
                .collect()
        };
        let base = World::new(9201, SimOriginKindV1::ClientMatchView, cast);
        let mut a = base.clone();
        script(&mut a);
        let first = ours();
        let s = |x: &str| x.to_string();
        assert_eq!(first.iter().map(|n| n.what.clone()).collect::<Vec<_>>(), vec![
            What::Barefoot { cassiopeia: s("league_cassiopeia") },
            What::DuoStart { xayah: s("league_xayah"), rakan: s("league_rakan") },
            What::HuntSighted { seer: s("league_khazix"), seen: s("league_rengar") },
            What::Trophy { rengar: s("league_rengar"), khazix: s("league_khazix"), pct: 15 },
            What::Evolved { khazix: s("league_khazix"), rengar: s("league_rengar"), pct: 10 },
            What::Shades { wearer: s("league_vayne"), leona: s("league_leona") },
            What::Swallowed { fizz: s("league_fizz"), yordle: s("league_tristana") },
            What::Sunlit { leona: s("league_leona"), zyra: s("league_zyra") },
            What::DuoW { rakan: s("league_rakan"), xayah: s("league_xayah") },
            What::DuoE { rakan: s("league_rakan"), xayah: s("league_xayah") },
            What::Trophy { rengar: s("league_rengar"), khazix: s("league_khazix"), pct: 15 },
        ]);
        // the opening toasts START_NOTE after the start, the sighting the tick Kha'Zix's mark was there
        assert_eq!((first[0].tick, first[1].tick, first[2].tick), (START_NOTE, START_NOTE, 1));
        assert!(first.iter().all(|n| !n.what.big()), "toasts, no banner");
        // the screen's second run: the same notes, kept once
        let mut a2 = base.clone();
        script(&mut a2);
        assert_ne!(number(&a2), number(&a));
        assert_eq!(ours(), first, "the second run adds nothing");
        // a presim of the same cast: the eggs are seen (the log), nothing is drawn
        let mut p = World::new(9202, SimOriginKindV1::ServerPresim, cast);
        script(&mut p);
        assert_eq!(ours(), first, "a presim draws nothing");
        let book = BOOK.lock().unwrap();
        let st = book.sims.get(&number(&p)).expect("the presim's state");
        assert_eq!((st.sighted, st.sunlit.is_some(), st.duo_w.is_some(), st.duo_e.is_some()), (Some(1), true, true, true));
        assert_eq!(st.rewards.iter().map(|r| r.1).collect::<Vec<_>>(), vec![TROPHY, RIVAL_EVO, TROPHY]);
        assert_eq!((st.shaded.clone(), st.shark.eaten.clone()), (vec![6], vec![("league_tristana".to_string(), true)]));
    }

    /// The marks 0.2.0's notices read are still put there: the main pack's kits (and the add-ons' copies of them) and
    /// league_zyra's photosynthesis.
    #[test]
    fn the_buffs_read_from_elsewhere_are_there() {
        let read = |path: &str| {
            std::fs::read_to_string(format!("{}/../{path}", env!("CARGO_MANIFEST_DIR"))).unwrap_or_else(|e| panic!("{path}: {e}"))
        };
        for (path, names) in [
            ("../league/champion/league_rengar.data_champion", [RENGAR_MET, TROPHY]),
            ("league_rengar_bush/override/league_rengar.data_champion", [RENGAR_MET, TROPHY]),
            ("../league/champion/league_khazix.data_champion", [KHAZIX_MET, RIVAL_EVO]),
            ("league_khazix/override/league_khazix.data_champion", [KHAZIX_MET, RIVAL_EVO]),
            ("../league/champion/league_rakan.data_champion", [RAKAN_DUO_W, RAKAN_E]),
        ] {
            let kit = read(path);
            for n in names {
                assert!(kit.contains(&format!("\"{n}\"")), "{n} not in {path}");
            }
        }
        // the rewards carry their attack bonus (the number in the toast)
        let rengar = read("../league/champion/league_rengar.data_champion");
        let at = rengar.find(&format!("\"name\": \"{TROPHY}\"")).expect("the trophy's buff");
        assert!(rengar[at..].chars().take(200).collect::<String>().contains("\"attack_mult\""));
        // league_zyra hangs the photosynthesis marker on her
        let sun = include_str!("../../league_zyra/src/sun.rs");
        assert!(sun.contains(&format!("pub const GREW: &str = \"{SUN_GREW}\";")), "league_zyra's marker");
        for n in [RENGAR_MET, KHAZIX_MET, TROPHY, RIVAL_EVO, SUN_GREW, RAKAN_DUO_W, RAKAN_E] {
            assert!(n.len() <= BUFF_NAME_CAP && !n.contains("_sim:"), "{n}");
        }
    }

    #[test]
    fn the_sim_tag_reads_back_and_is_skipped_by_the_divergence_check() {
        assert_eq!(parse_tag(&tag(42)), Some(42));
        assert_eq!(parse_tag("league_eggs_simx"), None);
        assert_eq!(parse_tag("league_azir_sim:3"), None);
        // league.dll's diverge.rs leaves out buffs naming a simulation
        assert!(tag(7).contains("_sim:"));
        assert!(tag(u64::MAX).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn a_simulation_without_anchors_is_looked_at_again_later() {
        // no nexus or tower at tick 100: looked at again from tick 700
        assert!(waiting(100 + RETRY, 101) && waiting(100 + RETRY, 699));
        assert!(!waiting(100 + RETRY, 700));
        // a twin of the same origin starting over at tick 0 looks for itself
        assert!(!waiting(5000 + RETRY, 0));
        // refused: never again
        assert!(waiting(usize::MAX, 0) && waiting(usize::MAX, 99_999));
    }

    #[test]
    fn buff_names_fit() {
        for name in [SOUL, FREED, DISSIDENT, GRUDGE, PLANTS, NINJA, "league_eggs_crown_lissandra", SUN_GREW, RAKAN_DUO_W] {
            assert!(name.len() <= BUFF_NAME_CAP && !name.contains("_sim:"), "{name}");
        }
        for q in rules::QUEENS {
            assert!(format!("{CROWN}{}", q.id().trim_start_matches("league_")).len() <= BUFF_NAME_CAP);
        }
    }

    fn sim(read: usize) -> Sim {
        let mut s = Sim::new(1, (0, 0, 0, 0, 0), 0, false, read);
        // (team, lane) -> player: bottom 3, support 4, jungle 1 on both sides
        for (team, lane, player) in [(0, 3, 3), (0, 4, 4), (0, 1, 1), (1, 3, 8), (1, 4, 9), (1, 1, 6)] {
            s.lanes.insert((team, lane), player);
            s.seat_of.insert(player, (team, lane));
        }
        s
    }

    #[test]
    fn a_kill_log_entry_becomes_players_by_lane() {
        let s = sim(0);
        let k = KillLogV1 { tick: 900, killer_team: 1, killer_position: 3, killed_position: 4, assist_count: 2,
                            assist_positions: [4, 1, 0, 0] };
        let td = s.takedown(&k).expect("a takedown");
        assert_eq!(td, Takedown { tick: 900, victim: 4, killer: Some(8), assists: vec![9, 6] });
        // an unknown lane on the victim's side: nothing
        let k2 = KillLogV1 { killed_position: 2, ..k };
        assert!(s.takedown(&k2).is_none());
        // assist_count past 4 is capped
        let k3 = KillLogV1 { assist_count: 9, assist_positions: [4, 4, 4, 4], ..k };
        assert_eq!(s.takedown(&k3).map(|t| t.assists.len()), Some(4));
    }
}
