//! 保护射手（peel）：比赛 AI 改进的第一步，依据逆向出来的游戏 AI 结构（docs/native_ai.md）。
//!
//! 游戏自己的团战 AI（game-ai：big_plan/battle 的 FOCUS-SEL 选目标、sub_plan/battle 的 Peel 战术、support_target）
//! 让每个人各打各的：对面英雄贴到我方射手身上时，辅助常常还在打前排或小兵（用户 2026-11-08「坦克保护adc
//! 现在游戏里也很糟糕吧」）。这个钩子只改这一种情况：
//!
//! - 我方射手（Bottom）身边 `DIVE_R` 以内有看得见的敌方英雄 = 贴脸的人（离射手最近的那个）；
//! - 保镖：辅助（血量 ≥ `SUPPORT_HP`%），以及离射手 `GUARD_NEAR` 以内的上单、打野（血量 ≥ `GUARD_HP`%），
//!   离贴脸的人 `REACH` 以内才管；
//! - 游戏 AI 给保镖的普攻目标不是他 → 改打他；往前走（不是撤退，血量 ≥ `MOVE_HP`%）→ 改打他；对着别的敌方英雄放的
//!   指向技能 → 改指向他（游戏认这个指令才改）；没有指令 → 打他。撤退、回城、给自己 / 队友的技能、方向 / 位置技能、
//!   已经在打他的，都不动。
//!
//! 0.2.0（用户 2026-11-08「这两个也一起修一修」）：1189 场里射手每场被「贴脸」14 次，可对线时敌人站在射手 30k 内是平常的
//! 站位，辅助被拉去打人；射手被贴脸时辅助在 60k 内的只有 35%。现在
//!
//! - 贴脸还要射手真的在挨打：最近 `HURT_WINDOW` tick 里掉了 `HURT_PCT`% 以上的血（`Peel::hurt`）；
//! - **射手挨打时辅助赶过去**（`escort`，0.2.1）：射手在挨打（同上）、身边 `ESCORT_THREAT` 内有敌方英雄，辅助离射手
//!   `ESCORT_NEAR` 到 `ESCORT_REACH` 之间、自己生命 `ESCORT_HP`% 以上、`ESCORT_CALM` 内没有自己的对手时，走到射手身边；
//!   回城、走回自家基地（目的地离自家基地 `HOME_NEAR` 以内）、在打敌方英雄、已经往射手那边走的不动。
//!   0.2.0 是辅助离射手 70k 以上、身边没敌人就拉回去：413 场里改了 1322 万 tick 的指令，辅助三分之一的时间被拴在射手身边，
//!   想游走、想走回家都被拉回（用户 2026-11-08「辅助想回家 想游走全被限制住了」）。现在射手不挨打时辅助随便走。
//!
//! 优先级 `PRIORITY` 在 league_macro（大龙后抱团 / 推基地 / 抢龙）之后、英雄附加包之前：英雄的钩子（替 AI 放大招之类）
//! 还能在它之后改。只看比赛状态，没有随机数：服务器预演和客户端重演走的一样。每个选手自己的钩子实例，不共用状态。
//!
//! 0.2.2（用户 2026-11-08「还是有卡回城的BUG啊」）：回城引导时游戏的 AI 大多数 tick 不下指令，那些空 tick 被当成「没事干」，射手挨打时把正在
//! 回城的辅助拉去射手身边，回城断掉、AI 再按。现在从回城命令到 AI 下别的命令为止都不管（`still_recalling`）。
//!
//! 两张 5v5 地图（2026-11-10）：按这一场的地图（每份模拟看一次 `game_places::terrain::map_of_sim`）：「在地图上」的上限是
//! `Map::limit`（游戏自己的地图照旧 `MAP_MAX` 1200000，Rin 的召唤师峡谷 1.25 x 1614545；以前一律 1200000，峡谷上红方半边的
//! 射手、敌人全看不见），「走回家」的 `HOME_NEAR` 跟着地图放大（`Map::scale`：峡谷的基地大 1.68 倍，泉水离基地更远）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_peel.log`（每次启动重写，上一次的留在 .prev.log）。
//! 只记服务器预演：射手每被贴脸一次（同一个保镖 `GAP` 内算一次）记下游戏 AI 原本让保镖做什么——这就是看游戏 AI 自己
//! 会不会保护射手；前 `DETAIL_LINES` 次各一行，每 `SUM_EVERY` 次一行汇总，汇总也追加到不随启动重写的 league_peel.sum.log。
//! 保护的效果看 league_fight_log 的 SUM 行（射手被贴脸后有没有人来、射手死了没有）。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{map_of_sim, rift_status, Map};
use mod_api_stable::*;

const ID: &str = "league_peel";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时合集的 build.rs 给 ADDON_VERSION_<id>。
const VERSION: &str = match option_env!("ADDON_VERSION_league_peel") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 钩子的优先级：league_macro（-500_000）之后，英雄附加包（1_000_000 上下）之前。
pub const PRIORITY: i32 = -400_000;
/// 敌方英雄离我方射手多近算贴脸（和 league_fight_log 的 DIVE_R 一样）。
pub const DIVE_R: f64 = 30_000.0;
/// 上单、打野离射手多近才当保镖（辅助不管远近）。
pub const GUARD_NEAR: f64 = 60_000.0;
/// 保镖离贴脸的人多远以内才去打他。
pub const REACH: f64 = 80_000.0;
/// 辅助的血量下限（%）。
pub const SUPPORT_HP: usize = 25;
/// 上单、打野的血量下限（%）。
pub const GUARD_HP: usize = 40;
/// 游戏 AI 让保镖往前走时，血量到这么多（%）才改成去打贴脸的人。
pub const MOVE_HP: usize = 50;
/// 移动的终点比现在离贴脸的人远这么多 = 撤退，不动。
pub const RETREAT: f64 = 10_000.0;
/// 同一个保镖两次贴脸隔这么久（tick，2 秒）以上才算新的一次。
pub const GAP: usize = 120;
/// 射手在挨打：这么多 tick 里（1 秒）……
pub const HURT_WINDOW: usize = 60;
/// ……掉了这么多（% 最大生命）以上的血。
pub const HURT_PCT: usize = 5;
/// 射手挨打时，这么近有敌方英雄（打它的人）辅助才赶过去……
pub const ESCORT_THREAT: f64 = 70_000.0;
/// ……辅助离射手这么近就不用赶了……
pub const ESCORT_NEAR: f64 = 40_000.0;
/// ……这么远（游走去了）也不拉回来。
pub const ESCORT_REACH: f64 = 150_000.0;
/// 辅助赶过去时自己的生命下限（%）。
pub const ESCORT_HP: usize = 40;
/// 辅助这么近有看得见的敌方英雄就在打自己的架：不拉它走。
pub const ESCORT_CALM: f64 = 60_000.0;
/// 走路的目的地离自家基地这么近 = 回家（补给、回城路上）：不拦。游戏自己的地图上的；峡谷上乘 `Map::scale`（基地跟着地图大）。
pub const HOME_NEAR: f64 = 120_000.0;
/// 游戏自己的地图外的坐标（死了、在泉水外面之类）不算（= `Map::Native.limit()`；这一场的看 `Map::limit`）。
pub const MAP_MAX: f64 = 1_200_000.0;
const TOP: u32 = 0;
const JUNGLE: u32 = 1;
const BOTTOM: u32 = 3;
const SUPPORT: u32 = 4;
/// 每这么多次贴脸写一行汇总。
pub const SUM_EVERY: usize = 500;
const DETAIL_LINES: usize = 60;
const LOG_CAP: usize = 5_000;

pub type Pos = (f64, f64);

pub fn dist(a: Pos, b: Pos) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 在地图上：0..=`limit`（`Map::limit`：游戏自己的地图 `MAP_MAX`）。
fn on_map(p: Pos, limit: f64) -> bool {
    (0.0..=limit).contains(&p.0) && (0.0..=limit).contains(&p.1)
}

/// 这次启动已经在日志里说过峡谷了。
static RIFT_TOLD: AtomicBool = AtomicBool::new(false);

/// 这个钩子实例所在那份模拟的地图：每份模拟看一次（按种子和来处认：实例可能跨场），第一次碰到峡谷（一次启动）时日志写一行。
#[derive(Clone, Copy, Default)]
struct MapOf(Option<(SimKey, Map)>);

/// 一份模拟：种子和来处（kind、match、replay、set）。
type SimKey = (u64, u32, u64, u64, u64);

impl MapOf {
    fn get(&mut self, sim: &StableSim<'_>) -> Map {
        let o = sim.sim_origin().unwrap_or_default();
        let key = (sim.seed(), o.kind, o.match_id, o.replay_id, o.set_index);
        match self.0 {
            Some((k, map)) if k == key => map,
            _ => {
                let map = map_of_sim(sim);
                if map == Map::Rift && !RIFT_TOLD.swap(true, Ordering::Relaxed) {
                    wlog(format!("== Rift: champions count as on the map up to {:.0} (1.25 x the Rift's side, not the game's \
                                  own {MAP_MAX:.0}), a walk home is one within {:.0} of our nexus (HOME_NEAR x {:.2}); {} ==",
                                 map.limit(), HOME_NEAR * map.scale(), map.scale(), rift_status()));
                }
                self.0 = Some((key, map));
                map
            }
        }
    }
}

// ===================== 决定 =====================

/// 贴脸开始时游戏 AI 原本让保镖做的事。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Native {
    Nothing = 0,
    AttackDiver = 1,
    AttackOther = 2,
    MoveIn = 3,
    MoveOut = 4,
    SkillDiver = 5,
    SkillOther = 6,
    Recall = 7,
}

pub const NATIVE: [&str; 8] =
    ["no order", "hit the diver", "hit something else", "walk in", "walk away", "skill on the diver", "skill elsewhere", "recall"];

/// 移动的终点比现在离贴脸的人远 `RETREAT` 以上。
pub fn retreat(me: Pos, to: Pos, diver: Pos) -> bool {
    dist(to, diver) > dist(me, diver) + RETREAT
}

fn on_target(b: &InputV1, id: usize) -> bool {
    b.target.kind == InputTargetKindV1::Target.code() && b.target.target_id == id
}

pub fn classify(base: Option<&InputV1>, diver: usize, diver_at: Pos, me: Pos) -> Native {
    let Some(b) = base else { return Native::Nothing };
    match InputKindV1::from_code(b.kind) {
        Some(InputKindV1::Attack) if on_target(b, diver) => Native::AttackDiver,
        Some(InputKindV1::Attack) => Native::AttackOther,
        Some(InputKindV1::Move) if retreat(me, (b.x as f64, b.y as f64), diver_at) => Native::MoveOut,
        Some(InputKindV1::Move) => Native::MoveIn,
        Some(InputKindV1::Return) => Native::Recall,
        Some(_) if on_target(b, diver) => Native::SkillDiver,
        Some(_) => Native::SkillOther,
        None => Native::Nothing,
    }
}

/// 这一 tick 场上和这个保镖有关的东西。
#[derive(Clone, Debug, PartialEq)]
pub struct View {
    /// 这一场的地图（`HOME_NEAR` 跟着它的 `scale`）。
    pub map: Map,
    pub me: Pos,
    pub hp_pct: usize,
    /// 自己的位置（LaneV1 代码）。
    pub lane: u32,
    /// 我方射手（活着、在地图上）。
    pub carry: Option<Pos>,
    /// 射手的生命（%）。
    pub carry_hp: usize,
    /// 射手最近在挨打（钩子按它的生命记录填）。
    pub hurt: bool,
    /// 贴脸的人：离射手最近、`DIVE_R` 以内、看得见的敌方英雄。
    pub diver: Option<(usize, Pos)>,
    /// 看得见的敌方英雄（实体 id，位置）。
    pub enemies: Vec<(usize, Pos)>,
    /// 自家基地。
    pub home: Option<Pos>,
}

impl Default for View {
    /// 什么都没看到，在游戏自己的地图上。
    fn default() -> Self {
        View {
            map: Map::Native,
            me: (0.0, 0.0),
            hp_pct: 0,
            lane: 0,
            carry: None,
            carry_hp: 0,
            hurt: false,
            diver: None,
            enemies: Vec::new(),
            home: None,
        }
    }
}

/// 保镖这次要管就给出贴脸的人：射手在挨打、位置对、血量够、够得着。
pub fn guarding(v: &View) -> Option<(usize, Pos)> {
    let carry = v.carry?;
    let diver = v.diver?;
    if !v.hurt {
        return None;
    }
    let floor = match v.lane {
        SUPPORT => SUPPORT_HP,
        TOP | JUNGLE if dist(v.me, carry) <= GUARD_NEAR => GUARD_HP,
        _ => return None,
    };
    (v.hp_pct >= floor && dist(v.me, diver.1) <= REACH).then_some(diver)
}

/// 这一 tick 的保护指令：`Some` 换掉游戏 AI 的指令，`None` 照旧。
pub fn order(v: &View, base: Option<&InputV1>, valid: &dyn Fn(&InputV1) -> bool) -> Option<InputV1> {
    let (diver, at) = guarding(v)?;
    let hit = InputV1::action(InputKindV1::Attack, InputTargetV1::target(diver));
    let out = match classify(base, diver, at, v.me) {
        Native::AttackDiver | Native::SkillDiver | Native::MoveOut | Native::Recall => return None,
        Native::Nothing | Native::AttackOther => hit,
        Native::MoveIn if v.hp_pct >= MOVE_HP => hit,
        Native::MoveIn => return None,
        Native::SkillOther => {
            let b = base?;
            // 只改对着别的敌方英雄放的指向技能：给自己、队友、小兵的和方向 / 位置技能都不动
            if b.target.kind != InputTargetKindV1::Target.code() || !v.enemies.iter().any(|e| e.0 == b.target.target_id) {
                return None;
            }
            InputV1 { target: InputTargetV1::target(diver), ..*b }
        }
    };
    valid(&out).then_some(out)
}

/// 射手挨打时辅助赶过去：射手在掉血、身边有敌方英雄，辅助不远不近、没在打自己的架时走到射手身边。射手不挨打时不管。
pub fn escort(v: &View, base: Option<&InputV1>) -> Option<InputV1> {
    let carry = v.carry?;
    if v.lane != SUPPORT || !v.hurt || v.hp_pct < ESCORT_HP {
        return None;
    }
    if !v.enemies.iter().any(|e| dist(e.1, carry) <= ESCORT_THREAT) || v.enemies.iter().any(|e| dist(e.1, v.me) <= ESCORT_CALM) {
        return None;
    }
    let d = dist(v.me, carry);
    if d <= ESCORT_NEAR || d > ESCORT_REACH {
        return None;
    }
    if let Some(b) = base {
        // recalling, walking home, already walking to the ADC, or hitting an enemy champion: its own
        let to = (b.x as f64, b.y as f64);
        let moving = b.kind == InputKindV1::Move.code();
        let walking_to = moving && dist(to, carry) <= ESCORT_NEAR;
        let home = moving && v.home.is_some_and(|h| dist(to, h) <= HOME_NEAR * v.map.scale());
        let fighting = b.target.kind == InputTargetKindV1::Target.code() && v.enemies.iter().any(|e| e.0 == b.target.target_id);
        if b.kind == InputKindV1::Return.code() || walking_to || home || fighting {
            return None;
        }
    }
    Some(InputV1::move_to(carry.0 as u64, carry.1 as u64))
}

/// Our nexus (it never moves: looked up once a match).
fn own_nexus(sim: &StableSim<'_>, team: usize) -> Option<Pos> {
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).find(|e| e.kind() == Some(EntityKindV1::Nexus) && e.team() == team).map(|e| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

/// One look from `player`'s guard on `map` (champions past its `limit` are off the map).
fn look(sim: &StableSim<'_>, player: usize, team: usize, map: Map) -> Option<View> {
    let me_p = sim.get_player(player)?;
    let champ = me_p.champion()?;
    if !champ.is_alive() {
        return None;
    }
    let (hp, max) = champ.hp();
    let (x, y) = champ.pos();
    let mut v = View {
        map,
        me: (x as f64, y as f64),
        hp_pct: if max > 0 { hp * 100 / max } else { 0 },
        lane: me_p.lane()?.code(),
        ..View::default()
    };
    let limit = map.limit();
    let mut enemies: Vec<(usize, Pos)> = Vec::new();
    for i in 0..sim.player_count() {
        let Some(p) = sim.player_at(i) else { continue };
        let Some(c) = p.champion() else { continue };
        if !c.is_alive() {
            continue;
        }
        let (x, y) = c.pos();
        let at = (x as f64, y as f64);
        if !on_map(at, limit) {
            continue;
        }
        if p.team() == team {
            if p.lane().map(|l| l.code()) == Some(BOTTOM) {
                v.carry = Some(at);
                let (hp, max) = c.hp();
                v.carry_hp = if max > 0 { hp * 100 / max } else { 0 };
            }
        } else if sim.is_visible(team, c.id()) {
            enemies.push((c.id(), at));
        }
    }
    if let Some(carry) = v.carry {
        v.diver = enemies
            .iter()
            .filter(|(_, at)| dist(*at, carry) <= DIVE_R)
            .min_by(|a, b| dist(a.1, carry).total_cmp(&dist(b.1, carry)))
            .copied();
    }
    v.enemies = enemies;
    Some(v)
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static LINES: AtomicUsize = AtomicUsize::new(0);
static SUM_HEADER: AtomicBool = AtomicBool::new(false);
/// 服务器预演里的统计：贴脸次数按 [保镖位置][游戏 AI 原本的指令]，改过指令的 tick 按保镖位置。
static BOOK: Mutex<Book> = Mutex::new(Book { episodes: [[0; 8]; 5], changed: [0; 5], total: 0, escorts: 0, escort_ticks: 0 });

struct Book {
    episodes: [[usize; 8]; 5],
    changed: [usize; 5],
    total: usize,
    /// Supports that started walking back to the ADC, and the ticks they did.
    escorts: usize,
    escort_ticks: usize,
}

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_PEEL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_peel.log");
        }
    }
    PathBuf::from("league_peel.log")
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

/// 汇总行也追加到 league_peel.sum.log（每次启动先写一行日期和版本）。
fn sum_log(line: &str) {
    let Ok(mut f) = OpenOptions::new().create(true).append(true).open(LOG_PATH.with_extension("sum.log")) else { return };
    let mut text = String::new();
    if !SUM_HEADER.swap(true, Ordering::Relaxed) {
        let secs = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map_or(0, |d| d.as_secs());
        let (y, m, d) = civil(secs / 86_400);
        text.push_str(&format!("=== {y}-{m:02}-{d:02} {:02}:{:02} UTC: {ID} v{VERSION} ===\n", secs / 3600 % 24, secs / 60 % 60));
    }
    text.push_str(line);
    text.push('\n');
    let _ = f.write_all(text.as_bytes());
}

/// 1970-01-01 起的天数 -> (年, 月, 日)。
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

fn pct(n: usize, of: usize) -> String {
    if of == 0 {
        "-".to_string()
    } else {
        format!("{:.0}%", 100.0 * n as f64 / of as f64)
    }
}

fn lane_name(lane: u32) -> &'static str {
    ["top", "jungle", "mid", "bottom", "support"].get(lane as usize).copied().unwrap_or("?")
}

/// 汇总：游戏 AI 原本让保镖做什么（各位置），我们改了多少 tick。
pub fn sum_line(episodes: &[[usize; 8]; 5], changed: &[usize; 5], total: usize, escorts: (usize, usize)) -> String {
    let all: Vec<usize> = (0..8).map(|k| episodes.iter().map(|r| r[k]).sum()).collect();
    let n: usize = all.iter().sum();
    let whole = NATIVE.iter().zip(&all).map(|(name, c)| format!("{name} {}", pct(*c, n))).collect::<Vec<_>>().join(", ");
    let lanes = [SUPPORT, TOP, JUNGLE]
        .iter()
        .map(|&l| {
            let row = &episodes[l as usize];
            let m: usize = row.iter().sum();
            format!("{} {m} (on the diver {})", lane_name(l), pct(row[Native::AttackDiver as usize] + row[Native::SkillDiver as usize], m))
        })
        .collect::<Vec<_>>()
        .join(", ");
    format!(
        "SUM {total} dives (a guard in reach when an enemy came within {}k of our ADC and hurt it): the game's AI had the guard {whole} | by guard: {lanes} | ticks we changed: support {}, top {}, jungle {} | supports back to the ADC {} ({} ticks)",
        DIVE_R / 1000.0,
        changed[SUPPORT as usize],
        changed[TOP as usize],
        changed[JUNGLE as usize],
        escorts.0,
        escorts.1
    )
}

fn clock(tick: usize) -> String {
    let s = tick / 60;
    format!("{}:{:02}", s / 60, s % 60)
}

/// 服务器预演里一次新的贴脸：记下游戏 AI 原本的指令。
fn note_dive(lane: u32, native: Native, detail: impl FnOnce() -> String) {
    let (total, sum) = {
        let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
        if let Some(row) = book.episodes.get_mut(lane as usize) {
            row[native as usize] += 1;
        }
        book.total += 1;
        let total = book.total;
        let sum = (total % SUM_EVERY == 0).then(|| sum_line(&book.episodes, &book.changed, total, (book.escorts, book.escort_ticks)));
        (total, sum)
    };
    if total <= DETAIL_LINES {
        wlog(detail());
    }
    if let Some(line) = sum {
        wlog(&line);
        sum_log(&line);
    }
}

fn note_escort(started: bool) {
    let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    book.escort_ticks += 1;
    if started {
        book.escorts += 1;
    }
}

fn note_change(lane: u32) {
    let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(c) = book.changed.get_mut(lane as usize) {
        *c += 1;
    }
}

// ===================== 钩子 =====================

#[derive(Clone, Default)]
struct Peel {
    /// 上次看到要保护射手的 tick（新的一次贴脸 = 隔了 `GAP` 以上，或者比赛重开、tick 倒回去了）。
    last_dive: Option<usize>,
    /// 射手最近的生命（tick，%），最长 `HURT_WINDOW`。
    carry_hp: std::collections::VecDeque<(usize, usize)>,
    /// 辅助正在赶去射手身边。
    escorting: bool,
    /// 自家基地，和上次看的 tick（tick 倒回去 = 新的一场，重找）。
    home: Option<Pos>,
    last_tick: usize,
    /// 游戏的 AI 正在回城（[`still_recalling`]，0.2.2）。
    recalling: bool,
    /// 这份模拟的地图（`MapOf`）。
    map: MapOf,
}

/// The game's AI recalling (league_ult_press 0.5.0's rule): a Return starts it, the ticks it gives no order go on with it
/// (while the recall runs it orders only now and then), any other order ends it.
pub fn still_recalling(was: bool, base: Option<&InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

impl Peel {
    /// Notes the ADC's health now and tells whether it lost `HURT_PCT`% or more in the last `HURT_WINDOW` ticks.
    fn hurt(&mut self, tick: usize, carry: Option<usize>) -> bool {
        let Some(hp) = carry else {
            self.carry_hp.clear();
            return false;
        };
        // a match started over (the tick went back): a new record
        if self.carry_hp.back().is_some_and(|b| b.0 > tick) {
            self.carry_hp.clear();
        }
        self.carry_hp.push_back((tick, hp));
        while self.carry_hp.front().is_some_and(|f| f.0 + HURT_WINDOW < tick) {
            self.carry_hp.pop_front();
        }
        let top = self.carry_hp.iter().map(|e| e.1).max().unwrap_or(hp);
        top >= hp + HURT_PCT
    }
}

impl StablePlayerAi for Peel {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:peel")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        // 中单、射手从不当保镖：不看场上
        if !matches!(ctx.lane().map(|l| l.code()), Some(TOP | JUNGLE | SUPPORT)) {
            return None;
        }
        // the game's AI recalling: all of it is left alone, its ticks without an order too (0.2.2)
        self.recalling = still_recalling(self.recalling, base.as_ref());
        if self.recalling {
            self.escorting = false;
            return None;
        }
        let tick = ctx.tick();
        let (player, team) = (ctx.player_id(), ctx.team());
        let (mut v, presim) = {
            let sim = ctx.sim()?;
            let presim = sim
                .sim_origin()
                .is_some_and(|o| SimOriginKindV1::from_code(o.kind) == Some(SimOriginKindV1::ServerPresim));
            if self.home.is_none() || tick < self.last_tick {
                self.home = own_nexus(&sim, team);
            }
            self.last_tick = tick;
            let map = self.map.get(&sim);
            (look(&sim, player, team, map)?, presim)
        };
        v.home = self.home;
        v.hurt = self.hurt(tick, v.carry.map(|_| v.carry_hp));
        let Some((diver, at)) = guarding(&v) else {
            // no dive: the support comes over when the ADC is being hit nearby
            let out = escort(&v, base.as_ref());
            let started = out.is_some() && !self.escorting;
            self.escorting = out.is_some();
            if out.is_some() && presim {
                note_escort(started);
            }
            return out;
        };
        self.escorting = false;
        let fresh = self.last_dive.is_none_or(|t| tick < t || tick > t + GAP);
        self.last_dive = Some(tick);
        if fresh && presim {
            // the champion's name only for the log line, not every tick
            let head = ctx.sim().and_then(|s| s.get_player(player).and_then(|p| p.champion()).and_then(|c| c.name()));
            let native = classify(base.as_ref(), diver, at, v.me);
            note_dive(v.lane, native, || {
                format!(
                    "DIVE t={} {} ({}) T{team}: enemy #{diver} {:.0}k from our ADC, guard {:.0}k from it at {}% hp - the game's AI: {}",
                    clock(tick),
                    head.unwrap_or_default(),
                    lane_name(v.lane),
                    v.carry.map_or(0.0, |c| dist(c, at) / 1000.0),
                    dist(v.me, at) / 1000.0,
                    v.hp_pct,
                    NATIVE[native as usize]
                )
            });
        }
        let out = order(&v, base.as_ref(), &|i| ctx.is_valid_input(i))?;
        if presim {
            note_change(v.lane);
        }
        Some(out)
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (peel: the support and nearby top / jungle hit whoever dives our ADC) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(Peel::default());
    host.log(LogLevel::Info, "league_peel loaded (peel the ADC).");
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

    #[test]
    fn a_recall_lasts_until_the_ai_orders_something_else() {
        let ret = InputV1::return_home();
        assert!(still_recalling(false, Some(&ret)));
        // the ticks between its orders: still recalling
        assert!(still_recalling(true, None));
        assert!(!still_recalling(false, None));
        assert!(!still_recalling(true, Some(&InputV1::move_to(1, 1))));
        assert!(!still_recalling(true, Some(&InputV1::action(InputKindV1::Attack, InputTargetV1::target(3)))));
    }

    const CARRY: Pos = (500_000.0, 700_000.0);
    const DIVER: usize = 77;

    fn view(lane: u32) -> View {
        View {
            map: Map::Native,
            me: (520_000.0, 700_000.0),
            hp_pct: 80,
            lane,
            carry: Some(CARRY),
            carry_hp: 70,
            hurt: true,
            diver: Some((DIVER, (510_000.0, 690_000.0))),
            enemies: vec![(DIVER, (510_000.0, 690_000.0)), (78, (530_000.0, 680_000.0)), (79, (900_000.0, 100_000.0))],
            home: Some((100_000.0, 860_000.0)),
        }
    }

    fn yes(_: &InputV1) -> bool {
        true
    }

    fn attack(id: usize) -> InputV1 {
        InputV1::action(InputKindV1::Attack, InputTargetV1::target(id))
    }

    #[test]
    fn the_support_hits_the_diver_instead() {
        let v = view(SUPPORT);
        for base in [Some(attack(78)), Some(attack(5_000)), None, Some(InputV1::move_to(505_000, 695_000))] {
            let out = order(&v, base.as_ref(), &yes).expect("peels");
            assert_eq!((out.kind, out.target.target_id), (InputKindV1::Attack.code(), DIVER));
        }
        // already on him, walking away, recalling: left alone
        assert_eq!(order(&v, Some(&attack(DIVER)), &yes), None);
        assert_eq!(order(&v, Some(&InputV1::move_to(700_000, 700_000)), &yes), None, "a retreat stays");
        assert_eq!(order(&v, Some(&InputV1::return_home()), &yes), None);
        // the game refuses the attack: keep its order
        assert_eq!(order(&v, Some(&attack(78)), &|_| false), None);
    }

    #[test]
    fn skills_on_other_champions_turn_on_the_diver() {
        let v = view(SUPPORT);
        let stun = InputV1::action(InputKindV1::Skill, InputTargetV1::target(78));
        let out = order(&v, Some(&stun), &yes).unwrap();
        assert_eq!((out.kind, out.target.target_id), (InputKindV1::Skill.code(), DIVER));
        // a heal on an ally, a skillshot by direction, a skill on a minion: left alone
        let heal = InputV1::action(InputKindV1::Skill2, InputTargetV1::target(3));
        assert_eq!(order(&v, Some(&heal), &yes), None);
        let shot = InputV1::action(InputKindV1::Ult, InputTargetV1::dir(1, 0));
        assert_eq!(order(&v, Some(&shot), &yes), None);
        assert_eq!(order(&v, Some(&InputV1::action(InputKindV1::Skill, InputTargetV1::target(5_000))), &yes), None);
    }

    #[test]
    fn who_guards() {
        // top / jungle only near the ADC, mid and the ADC never
        assert!(guarding(&view(TOP)).is_some());
        assert!(guarding(&View { me: (585_000.0, 700_000.0), ..view(JUNGLE) }).is_none(), "85k from the ADC");
        assert!(guarding(&View { me: (585_000.0, 700_000.0), ..view(SUPPORT) }).is_some(), "the support comes from farther");
        assert!(guarding(&view(2)).is_none() && guarding(&view(BOTTOM)).is_none());
        // hp floors and reach
        assert!(guarding(&View { hp_pct: 30, ..view(SUPPORT) }).is_some());
        assert!(guarding(&View { hp_pct: 20, ..view(SUPPORT) }).is_none());
        assert!(guarding(&View { hp_pct: 35, ..view(TOP) }).is_none());
        assert!(guarding(&View { me: (600_000.0, 690_000.0), ..view(SUPPORT) }).is_none(), "90k from the diver");
        // no diver or no ADC: nothing
        assert!(guarding(&View { diver: None, ..view(SUPPORT) }).is_none());
        assert!(guarding(&View { carry: None, ..view(SUPPORT) }).is_none());
        // an enemy that close but the ADC not hurt (lane spacing): nothing
        assert!(guarding(&View { hurt: false, ..view(SUPPORT) }).is_none());
    }

    #[test]
    fn hurt_is_a_drop_in_the_last_second() {
        let mut p = Peel::default();
        assert!(!p.hurt(0, Some(80)));
        assert!(!p.hurt(30, Some(78)), "2% is a scratch");
        assert!(p.hurt(50, Some(74)), "6% in under a second");
        assert!(!p.hurt(200, Some(74)), "the drop is old now");
        assert!(!p.hurt(210, None) && p.carry_hp.is_empty(), "no ADC: forgotten");
        assert!(!p.hurt(5, Some(50)), "a new match: a new record");
    }

    #[test]
    fn the_support_comes_only_when_its_adc_is_being_hit() {
        // the ADC hurt with an enemy 50k from it, the support 100k away and nobody near the support: it comes
        let far = View {
            me: (400_000.0, 760_000.0),
            diver: None,
            hurt: true,
            enemies: vec![(79, (540_000.0, 670_000.0))],
            ..view(SUPPORT)
        };
        let go = escort(&far, None).expect("comes over");
        assert_eq!((go.kind, go.x, go.y), (InputKindV1::Move.code(), 500_000, 700_000));
        // the ADC not hurt (laning, roaming, shopping): the support goes where it likes
        assert_eq!(escort(&View { hurt: false, ..far.clone() }, None), None);
        // nobody near the ADC, the support close already, or off roaming beyond ESCORT_REACH: no
        assert_eq!(escort(&View { enemies: vec![(79, (900_000.0, 100_000.0))], ..far.clone() }, None), None);
        assert_eq!(escort(&View { me: (520_000.0, 710_000.0), ..far.clone() }, None), None);
        assert_eq!(escort(&View { me: (300_000.0, 900_000.0), ..far.clone() }, None), None, "220k away: roaming");
        // recalling, walking home, walking to the ADC, fighting, its own foe near, hurt itself, not the support: left alone
        assert_eq!(escort(&far, Some(&InputV1::return_home())), None);
        assert_eq!(escort(&far, Some(&InputV1::move_to(150_000, 820_000))), None, "on its way home");
        assert_eq!(escort(&far, Some(&InputV1::move_to(510_000, 700_000))), None);
        assert_eq!(escort(&far, Some(&attack(79))), None);
        assert_eq!(escort(&View { enemies: vec![(79, (540_000.0, 670_000.0)), (78, (410_000.0, 750_000.0))], ..far.clone() }, None), None);
        assert_eq!(escort(&View { hp_pct: 30, ..far.clone() }, None), None);
        assert_eq!(escort(&View { lane: TOP, ..far.clone() }, None), None);
        // walking somewhere else while its ADC is being hit: comes instead
        assert!(escort(&far, Some(&InputV1::move_to(450_000, 450_000))).is_some());
    }

    #[test]
    fn on_the_rift_the_map_and_the_walk_home_follow_its_size() {
        let (native, rift) = (Map::Native.limit(), Map::Rift.limit());
        // red's half of the Rift (past 1200000): on the map there, never on the game's own
        assert!(on_map((1_450_000.0, 160_000.0), rift) && !on_map((1_450_000.0, 160_000.0), native));
        assert!(on_map((0.0, MAP_MAX), native) && !on_map((-1.0, 5.0), rift) && !on_map((3_000_000.0, 5.0), rift));
        // red's support walks to red's fountain on the Rift, 170k from its nexus: a walk home there (HOME_NEAR x 1.68)
        let nexus = (1_450_000.0, 160_000.0);
        let far = View {
            map: Map::Rift,
            me: (1_250_000.0, 360_000.0),
            carry: Some((1_150_000.0, 420_000.0)),
            diver: None,
            enemies: vec![(79, (1_110_000.0, 450_000.0))],
            home: Some(nexus),
            ..view(SUPPORT)
        };
        let fountain = InputV1::move_to(1_570_000, 40_000);
        assert!(dist((1_570_000.0, 40_000.0), nexus) > HOME_NEAR && dist((1_570_000.0, 40_000.0), nexus) < HOME_NEAR * Map::Rift.scale());
        assert_eq!(escort(&far, Some(&fountain)), None, "on its way home");
        // the game's own map's 120k would have pulled it back to the ADC
        assert!(escort(&View { map: Map::Native, ..far.clone() }, Some(&fountain)).is_some());
        // anywhere else it still comes over
        assert!(escort(&far, Some(&InputV1::move_to(1_300_000, 600_000))).is_some());
    }

    #[test]
    fn a_hurt_guard_does_not_walk_in() {
        let v = View { hp_pct: 45, ..view(SUPPORT) };
        assert_eq!(order(&v, Some(&InputV1::move_to(505_000, 695_000)), &yes), None);
        assert!(order(&v, Some(&attack(78)), &yes).is_some(), "but switches its attack");
    }

    #[test]
    fn the_summary_and_dates() {
        let mut e = [[0usize; 8]; 5];
        e[SUPPORT as usize][Native::AttackOther as usize] = 3;
        e[SUPPORT as usize][Native::AttackDiver as usize] = 1;
        e[TOP as usize][Native::MoveIn as usize] = 1;
        let line = sum_line(&e, &[2, 0, 0, 0, 7], 5, (3, 40));
        assert!(line.starts_with("SUM 5 dives"), "{line}");
        assert!(line.contains("hit the diver 20%") && line.contains("hit something else 60%"), "{line}");
        assert!(line.contains("support 4 (on the diver 25%)") && line.contains("top 1 (on the diver 0%)"), "{line}");
        assert!(line.contains("support 7, top 2, jungle 0") && line.ends_with("supports back to the ADC 3 (40 ticks)"), "{line}");
        assert_eq!(civil(20_400), (2025, 11, 8));
        assert_eq!(classify(None, DIVER, CARRY, CARRY), Native::Nothing);
        assert_eq!(clock(3_660), "1:01");
    }
}
