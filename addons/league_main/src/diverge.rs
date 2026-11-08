//! 对局校验和（0.9.12；0.9.14 重写了配对、存储和比较）：屏幕上的比赛和服务器为它预演的两份模拟该一模一样，可 2026-11-05 的
//! 日志里三份走到一半就分道扬镳，游戏自己的 log.log 也写 `server/live simulation diverged`。11-06 的日志（g1）：每个看了的
//! 小局，画面都在 4200～18600 tick 之间和预演分开、再没合上，第一处不同都赶上画面里一阵 AI 回城；而金币、等级、装备、冷却、
//! 属性都不在哈希里——真正的第一处不同可能更早。这里要让下一局的日志说出预演和画面「第一处哪里不一样」。
//!
//! 比赛钩子（`StableMatchHook`，一个模块只能设一个）每 `EVERY` 个 tick 和第 1 个 tick 给每份模拟拍一张快照：
//! - 每个玩家一行：金币、等级、复活倒计时、死活、击杀 / 死亡 / 助攻 / 补刀、四个冷却（普攻、技能、技能 2、大招）、装备、
//!   英雄的属性（StatV1 九项）；
//! - 每个活着的单位一行：名字、种类、阵营、位置、血量、护盾、身上的控制数、可不可选、buff 名（附加包按模拟编号挂的
//!   `xxx_sim:N` 除外，它们本来就每份不同）；
//! 都按 id 排好算一个 FNV-1a 64 位哈希。快照按（比赛、种类、小局、种子、线程）归到一次「run」（tick 倒回去就是新的一次）。
//!
//! 配对（0.9.14）：同一小局的几份模拟第一个 tick 的 rng 一样（g1 实测：两份预演、画面的两次都同一个值），不同小局不一样。
//! 只有第一张快照 rng 相同的 run 才互相比——预演的小局号是 `s=-`，以前同一场比赛里所有 run 两两比，11-06 的 394 行 DIVERGE
//! 里 358 行是拿不同小局比出来的「第 1 tick 就不同」。没有比赛号的模拟（启动时成对跑的原版 `[unknown m=- s=-]`）一样按 rng
//! 配对、一样比——它们只有原版英雄，分开了就不是我们的英雄。
//!
//! 比较：同一小局的两份走到同一个 tick 就对哈希。不同时写 DIVERGE：第一处不同的行（玩家先、再英雄、再其他单位，任何种类都算：
//! 小兵、野怪、塔），哪个字段、两边的值，buff 不同就写哪些名字只在哪边；再列后面几处、各类不同的行数、两边的玩家汇总。之后
//! 接着比：又一样了写 EQUAL「equal again at T」，又不一样再写 DIVERGE（每对最多 `PAIR_LINES` 行，其余记进 END）。
//!
//! 存储：最多 `MAX_MATCHES` 场比赛；新比赛进来时先扔没有任何配对的、最久没更新的那场（11-06：服务器一个系列的第一小局同时
//! 预演 7～10 场，旧版只记 3 场，看着的那场被挤掉、run 被重新编号，8/20 个小局没有 DIVERGE、END 错或没有）。每张快照的行
//! 按名字表压缩存着，好在另一份后来走到同一 tick 时逐行对比：配上对的 run 全留，没配上的只留第一张和最近 `WINDOW` 张；总量
//! （行、细哈希、名字表）超过 `DETAIL_BUDGET` 时先扔没配对的、再扔最久没更新的 run 的行（哈希一直留着）。
//!
//! 日志（league.log），只写有配对的 run（11-06：SYNC 占 8.95 MB 里的 8.2 MB，93% 是没人看的单份预演）：
//! - `SET [view m=2853 s=1 run 3 thr 39] same set as presim run 1, presim run 2 (rng … at its first tick; seed …)`：第一次配上时；
//!   之前没写的 SYNC 行这时补上。
//! - `SYNC [view m=2853 s=1 run 3 thr 39] t=600 rng=… n=93 h=…`（第一张带 `seed=`；t ≤ 1 和每 `SUMMARY_EVERY` tick 带
//!   `| 玩家汇总`：`zed#18 L7 g1234 812/1000 (189901,96150) b5`，死了的 `zed dead r540 L7 g1234`）。
//! - `DIVERGE [view …] vs [presim …] first seen at tick 4800 (agreed at 4200); first differs between t 4560 and t 4620,
//!   player 3 zed: player 3 zed (view run 3 vs presim run 1): gold 1300 vs 1234, items [...] vs [...] | also: zed#18
//!   champion (view run 3 vs presim run 1): pos (…) vs (…), buffs only in view run 3: [...] | structures: nexus#0 nexus (…):
//!   buffs only in view run 3: [...] | 6 rows differ: 1 player, 2 champion, 1 nexus, 2 minion | n 93 vs 93, rng same |
//!   view run 3: … | presim run 1: …`（之后再分开写 `again at tick T (equal again since E); first differs …`）
//! - `EQUAL [view …] vs [presim …] equal again at tick 9000 (apart from 4800, 7 of 15 compared ticks differ so far)`
//! - `END [view …] t=46800 n=… blue score diff=+5 (kills 12:7): vs presim run 1 agreed through 4200, diverged at 4800,
//!   apart at 70 of 78 compared ticks, equal again 1x (first at 9000), apart at the end; vs …`
//! - `RNG [a] vs [b] …`：状态一样而钩子给的 rng 不同（每对只说一次，不算分开）。
//! 开销：每 600 tick 把一两百个单位和十个玩家读一遍，有配对的 run 每 60 tick 再读一遍（600 tick 的快照之外只算细哈希、
//! 不存行；没配对的后台预演不算）——可以忽略；存的行有总量上限。
//!
//! 0.9.21（2026-11-08 的日志）：
//! - 名字表跟着行走：以前名字表只增不减、全局最多 65536 个，每份模拟（一次启动约 780 份没人看的后台预演）每张快照都往里
//!   加，第三方 buff 名里还带着变化的数字（`tfm2_b2:2:1f7:0`、`sed_timer1:…`），开局 15 分钟就满了——之后的新名字都读
//!   「?」：7 行 DIVERGE 写成「the kept rows agree - a name past the kept ones differs」，SYNC 汇总里英雄成了 `?#18`。现在每个
//!   名字记着有几处留着的行用它，行扔掉时减一、到零就把名字连同编号放掉（编号再给新名字用），名字的字节也算进
//!   `DETAIL_BUDGET`：只要行还留着，名字就在、而且是对的。
//! - 细括号：除了每 600 tick 的快照，有配对的 run 每 `FINE`（60）tick 给每个玩家算一个细哈希（玩家那一行加他英雄那一行），
//!   再加一个「其他单位」的；跟着下一张快照存（行扔掉时一起扔，算进 `DETAIL_BUDGET`）。两份在 600 tick 上第一次（或又一次）对不上时，在上一个对得上的
//!   tick 之后逐个比细哈希：DIVERGE 写 `first differs between t 4260 and t 4320, player 0 akali, other units`——第一处不同在
//!   哪 60 tick 之间、是哪些玩家。
//! - 塔和水晶：不同的行按玩家、英雄、大型野怪、建筑……排，前 1 + `ALSO` 行常被玩家和英雄占满，建筑的不同（11-08 唯一的线索：
//!   水晶上第三方插件的 buff，画面 `tfm2_b2:2:1f7:0` 对预演 `tfm2_b2:2:80:0`）就看不到了。现在没列出的塔 / 水晶的不同行
//!   （连同 buff 差别）总是接在后面：`| structures: …`（最多 `STRUCTURES` 行）。
//! - END 的比分：`blue score diff` 是模拟自己的比分差（score_diff），英雄每阵亡一次都给对方记一分，处决（被塔 / 小兵 / 野怪
//!   杀死、没有玩家拿到人头）也算；游戏 log.log `[GamePlayDone]` 的 server_score 就是这个分（11-08 预演的 END 9/9 都对上），
//!   live_score 却是两队玩家的击杀数之和（画面的 END 7/9 对上；差一分的 m=4152 s2「+14 对 17:4」和 m=4166 s1「+0 对
//!   11:12」两局，全场阵亡数都比击杀数多一，正好一次处决）。所以 END 两个都写：`blue score diff=+14 (kills 17:4)`，括号里
//!   是同一 tick 两队玩家的击杀数，和 live_score 比。读的时刻照旧是第一个 `is_end` 的 tick：9 局算上处决都对得上，看不出
//!   游戏记比分的时刻和它不一样（找不到更准的时刻——两种比分的差别在定义，不在时刻）。

use std::collections::{HashMap, VecDeque};
use std::sync::{Arc, LazyLock, Mutex};

use mod_api_stable::*;

use crate::wlog;

/// Ticks between snapshots.
pub const EVERY: usize = 600;
/// Ticks between snapshots whose SYNC line carries the per-player summary.
pub const SUMMARY_EVERY: usize = 3000;
/// Snapshots kept per run (256 x 600 = 153 600 ticks: the longest set of 11-06 ran 120 600, and the view's second run of
/// a set, minutes after the presims, still finds their early ticks).
pub const KEEP: usize = 256;
/// Matches remembered (a series' first set has the server presim 7-10 matches at once).
pub const MAX_MATCHES: usize = 16;
/// Runs remembered per match (2 presims + a view or two per set, across a series).
pub const MAX_RUNS: usize = 48;
/// Snapshots whose rows an unpaired run keeps besides its first (a partner starting a few seconds later still finds them).
pub const WINDOW: usize = 32;
/// Bytes of kept rows (estimated) in all; past it the rows of unpaired, then of the least recently updated runs go.
pub const DETAIL_BUDGET: usize = 16 << 20;
/// DIVERGE / EQUAL lines a pair (one flipping back and forth says the rest in its END line).
pub const PAIR_LINES: u32 = 8;
/// Differing rows named after the first.
pub const ALSO: usize = 4;
/// Differing tower / nexus rows appended after those (`| structures: ...`) when they are not among them.
pub const STRUCTURES: usize = 8;
/// Distinct names (units, buffs, items) the kept rows can name at once - a safety cap far past what the budget lets
/// them reach (a name goes with the last kept row naming it, and the names count in `DETAIL_BUDGET`); past it "?".
pub const MAX_NAMES: usize = 1 << 20;
/// What one name costs in the budget besides its text: its allocation, the map's entry, its slot.
const NAME_COST: usize = 64;
/// Ticks between the fine records (each player's row hash): a DIVERGE line brackets the first difference to these.
pub const FINE: usize = 60;
/// Players named in a fine bracket (the rest counted).
const BRACKET_PLAYERS: usize = 4;

/// One living entity as read from the simulation.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Unit {
    pub id: usize,
    pub name: String,
    /// EntityKindV1 code (u32::MAX: unknown)
    pub kind: u32,
    pub team: usize,
    pub pos: (u64, u64),
    /// (current, max)
    pub hp: (usize, usize),
    pub shield: usize,
    /// crowd-control effects on it
    pub cc: usize,
    pub targetable: bool,
    /// its buffs' names in its own order, the simulation tags left out
    pub buffs: Vec<String>,
}

/// One player as read from the simulation.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Player {
    pub id: usize,
    pub team: usize,
    /// the champion entity (usize::MAX: none) and its name
    pub champ: usize,
    pub name: String,
    pub gold: usize,
    pub level: usize,
    pub respawn: usize,
    pub alive: bool,
    /// kills, deaths, assists, cs
    pub kda: [usize; 4],
    /// remaining cooldown ticks: attack, skill, skill2, ult
    pub cds: [usize; 4],
    pub items: Vec<String>,
    /// the champion's stats ([`STATS`] order), zeros without one
    pub stat: [usize; 9],
}

/// StatV1's fields, in [`Player::stat`]'s order.
pub const STATS: [&str; 9] =
    ["attack", "magic_power", "hp", "defence", "magic_resistance", "move_speed", "hp_regen", "stack", "crit_chance"];

/// One snapshot of a simulation: its rows sorted by id and their hash.
#[derive(Clone, Debug)]
pub struct Snapshot {
    pub tick: usize,
    pub hash: u64,
    /// the hook's rng seed this tick
    pub rng: u64,
    /// living entities
    pub count: usize,
    pub players: Vec<Player>,
    pub units: Vec<Unit>,
}

impl Snapshot {
    /// The rows sorted by id and hashed.
    pub fn new(tick: usize, rng: u64, mut players: Vec<Player>, mut units: Vec<Unit>) -> Self {
        let hash = hash_rows(&mut players, &mut units);
        Snapshot { tick, hash, rng, count: units.len(), players, units }
    }
}

/// Which simulation a snapshot comes from.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Origin {
    pub kind: u32,
    pub match_id: u64,
    pub set: u64,
    pub seed: u64,
    pub thread: u64,
}

/// A buff the add-ons hang on a champion to number its simulation (`league_azir_sim:17`, `league_drmundo_sim:3` ...):
/// different in every simulation by design, so never part of the hash.
pub fn is_sim_tag(buff: &str) -> bool {
    buff.contains("_sim:")
}

/// FNV-1a 64, fed field by field (each field closed by an 0xff byte): stable across builds and platforms, unlike
/// `DefaultHasher`.
struct Fnv(u64);

impl Fnv {
    fn new() -> Self {
        Fnv(0xcbf2_9ce4_8422_2325)
    }

    fn feed(&mut self, bytes: &[u8]) {
        for b in bytes {
            self.0 ^= *b as u64;
            self.0 = self.0.wrapping_mul(0x0000_0100_0000_01b3);
        }
        self.0 ^= 0xff;
        self.0 = self.0.wrapping_mul(0x0000_0100_0000_01b3);
    }

    fn player(&mut self, p: &Player) {
        for v in [p.id, p.team, p.champ, p.gold, p.level, p.respawn, p.alive as usize] {
            self.feed(&v.to_le_bytes());
        }
        self.feed(p.name.as_bytes());
        for v in p.kda.iter().chain(p.cds.iter()).chain(p.stat.iter()) {
            self.feed(&v.to_le_bytes());
        }
        self.feed(&p.items.len().to_le_bytes());
        for i in &p.items {
            self.feed(i.as_bytes());
        }
    }

    fn unit(&mut self, u: &Unit) {
        self.feed(&u.id.to_le_bytes());
        self.feed(u.name.as_bytes());
        self.feed(&u.kind.to_le_bytes());
        for v in [u.team, u.hp.0, u.hp.1, u.shield, u.cc, u.targetable as usize] {
            self.feed(&v.to_le_bytes());
        }
        self.feed(&u.pos.0.to_le_bytes());
        self.feed(&u.pos.1.to_le_bytes());
        for b in u.buffs.iter().filter(|b| !is_sim_tag(b)) {
            self.feed(b.as_bytes());
        }
    }

    /// The hash folded to 32 bits (the fine records').
    fn short(&self) -> u32 {
        (self.0 ^ (self.0 >> 32)) as u32
    }
}

/// FNV-1a 64 over every player then every unit in id order.
pub fn hash_rows(players: &mut [Player], units: &mut [Unit]) -> u64 {
    players.sort_by_key(|p| p.id);
    units.sort_by_key(|u| u.id);
    let mut h = Fnv::new();
    for p in players.iter() {
        h.player(p);
    }
    for u in units.iter() {
        h.unit(u);
    }
    h.0
}

/// One fine record (every `FINE` ticks): a hash of each player's row with his champion's, and one of every other
/// unit - enough to tell between which ticks and in whose rows two runs first differ.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Fine {
    pub tick: u32,
    /// the units that are no player's champion
    pub rest: u32,
    /// (player id, the hash of his row and his champion's), in player id order
    pub players: Box<[(u32, u32)]>,
}

impl Fine {
    /// The fine record of a snapshot (its rows sorted by id, as `Snapshot::new` leaves them).
    pub fn of(s: &Snapshot) -> Fine {
        let players = s.players.iter().map(|p| {
            let mut h = Fnv::new();
            h.player(p);
            if let Some(u) = s.units.iter().find(|u| u.id == p.champ) {
                h.unit(u);
            }
            (p.id as u32, h.short())
        }).collect();
        let mut rest = Fnv::new();
        for u in s.units.iter().filter(|u| !s.players.iter().any(|p| p.champ == u.id)) {
            rest.unit(u);
        }
        Fine { tick: s.tick as u32, rest: rest.short(), players }
    }

    /// What it takes, about (the budget's unit).
    fn bytes(&self) -> usize {
        std::mem::size_of::<Fine>() + 16 + std::mem::size_of_val(&*self.players)
    }
}

/// Each team's kills by its players (blue = team 0): what the game's log.log calls the live score.
pub fn team_kills(players: &[Player]) -> (usize, usize) {
    players.iter().fold((0, 0), |(b, r), p| if p.team == 0 { (b + p.kda[0], r) } else { (b, r + p.kda[0]) })
}

fn short(name: &str) -> &str {
    name.strip_prefix("league_").unwrap_or(name)
}

pub fn kind_name(kind: u32) -> &'static str {
    match SimOriginKindV1::from_code(kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    }
}

/// An entity kind's name (EntityKindV1).
pub fn unit_kind(kind: u32) -> &'static str {
    match EntityKindV1::from_code(kind) {
        Some(EntityKindV1::Champion) => "champion",
        Some(EntityKindV1::Minion) => "minion",
        Some(EntityKindV1::Jungle) => "monster",
        Some(EntityKindV1::Epic) => "epic",
        Some(EntityKindV1::Serpen) => "serpent",
        Some(EntityKindV1::Tower) => "tower",
        Some(EntityKindV1::Nexus) => "nexus",
        Some(EntityKindV1::Summon) => "summon",
        None => "unit",
    }
}

/// The order differing rows are named in: players, champions, epic monsters, structures, summons, camps, minions.
fn unit_rank(kind: u32) -> u8 {
    match EntityKindV1::from_code(kind) {
        Some(EntityKindV1::Champion) => 1,
        Some(EntityKindV1::Epic) | Some(EntityKindV1::Serpen) => 2,
        Some(EntityKindV1::Tower) | Some(EntityKindV1::Nexus) => 3,
        Some(EntityKindV1::Summon) => 4,
        Some(EntityKindV1::Jungle) => 5,
        Some(EntityKindV1::Minion) => 6,
        None => 7,
    }
}

fn none_dash(v: u64) -> String {
    if v == SimOriginV1::NONE { "-".into() } else { v.to_string() }
}

// ---- the kept rows: names in a table, numbers as they are ----

/// The names the kept rows refer to, each kept once with the number of kept references to it: a name goes with the
/// last kept row naming it, and its id serves a new name (0.9.21 - the table only grew before, and was full 15 minutes
/// into 11-08's launch).
#[derive(Default)]
struct Names {
    ids: HashMap<Arc<str>, u32>,
    /// by id: the name and its kept references (None: a free id)
    list: Vec<Option<(Arc<str>, u32)>>,
    free: Vec<u32>,
    /// what the table takes, about (part of the budget)
    bytes: usize,
}

const UNNAMED: u32 = u32::MAX;

impl Names {
    /// The id of `s`, one more kept reference to it.
    fn id(&mut self, s: &str) -> u32 {
        if let Some(&k) = self.ids.get(s) {
            if let Some((_, n)) = self.list[k as usize].as_mut() {
                *n += 1;
            }
            return k;
        }
        if self.ids.len() >= MAX_NAMES {
            return UNNAMED;
        }
        let name: Arc<str> = Arc::from(s);
        let k = match self.free.pop() {
            Some(k) => {
                self.list[k as usize] = Some((name.clone(), 1));
                k
            }
            None => {
                self.list.push(Some((name.clone(), 1)));
                (self.list.len() - 1) as u32
            }
        };
        self.bytes += NAME_COST + name.len();
        self.ids.insert(name, k);
        k
    }

    /// One kept reference to `k` gone (the name with the last).
    fn release(&mut self, k: u32) {
        let Some(slot) = self.list.get_mut(k as usize) else { return };
        let Some((_, n)) = slot.as_mut() else { return };
        *n -= 1;
        if *n == 0 {
            if let Some((name, _)) = slot.take() {
                self.ids.remove(&*name);
                self.bytes -= NAME_COST + name.len();
            }
            self.free.push(k);
        }
    }

    /// The references of rows that are no longer kept.
    fn release_rows(&mut self, rows: &Rows) {
        for p in &rows.players {
            self.release(p.name);
            for &i in p.items.iter() {
                self.release(i);
            }
        }
        for u in &rows.units {
            self.release(u.name);
            for &b in u.buffs.iter() {
                self.release(b);
            }
        }
    }

    fn get(&self, k: u32) -> &str {
        self.list.get(k as usize).and_then(Option::as_ref).map_or("?", |s| &s.0)
    }

    fn list(&self, ks: &[u32]) -> String {
        format!("[{}]", ks.iter().map(|k| self.get(*k)).collect::<Vec<_>>().join(", "))
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct KeptUnit {
    id: usize,
    name: u32,
    kind: u32,
    team: usize,
    pos: (u64, u64),
    hp: (usize, usize),
    shield: usize,
    cc: usize,
    targetable: bool,
    buffs: Box<[u32]>,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct KeptPlayer {
    id: usize,
    team: usize,
    champ: usize,
    name: u32,
    gold: usize,
    level: usize,
    respawn: usize,
    alive: bool,
    kda: [usize; 4],
    cds: [usize; 4],
    items: Box<[u32]>,
    stat: [usize; 9],
}

/// A snapshot's rows as kept, sorted by id.
#[derive(Clone, Debug, Default)]
struct Rows {
    players: Vec<KeptPlayer>,
    units: Vec<KeptUnit>,
}

impl Rows {
    fn keep(snap: &Snapshot, names: &mut Names) -> Rows {
        let players = snap.players.iter().map(|p| KeptPlayer {
            id: p.id, team: p.team, champ: p.champ, name: names.id(&p.name), gold: p.gold, level: p.level,
            respawn: p.respawn, alive: p.alive, kda: p.kda, cds: p.cds,
            items: p.items.iter().map(|i| names.id(i)).collect(), stat: p.stat,
        }).collect();
        let units = snap.units.iter().map(|u| KeptUnit {
            id: u.id, name: names.id(&u.name), kind: u.kind, team: u.team, pos: u.pos, hp: u.hp, shield: u.shield,
            cc: u.cc, targetable: u.targetable,
            buffs: u.buffs.iter().filter(|b| !is_sim_tag(b)).map(|b| names.id(b)).collect(),
        }).collect();
        Rows { players, units }
    }

    /// What they take, about (the budget's unit).
    fn bytes(&self) -> usize {
        const BOX: usize = 16; // an allocation's overhead
        std::mem::size_of::<Rows>()
            + self.players.iter().map(|p| std::mem::size_of::<KeptPlayer>() + BOX + 4 * p.items.len()).sum::<usize>()
            + self.units.iter().map(|u| std::mem::size_of::<KeptUnit>() + BOX + 4 * u.buffs.len()).sum::<usize>()
    }

    fn unit(&self, id: usize) -> Option<&KeptUnit> {
        self.units.binary_search_by_key(&id, |u| u.id).ok().map(|k| &self.units[k])
    }
}

/// The players (or, with none, the champions) in one line: `zed#18 L7 g1234 812/1000 (189901,96150) b5; ...`.
fn summary(rows: &Rows, names: &Names) -> String {
    let mut parts: Vec<String> = rows.players.iter().map(|p| {
        let name = short(names.get(p.name));
        let name = if name.is_empty() { format!("player{}", p.id) } else { name.to_string() };
        match rows.unit(p.champ).filter(|_| p.alive) {
            Some(u) => format!("{name}#{} L{} g{} {}/{} ({},{}) b{}", u.id, p.level, p.gold, u.hp.0, u.hp.1, u.pos.0,
                               u.pos.1, u.buffs.len()),
            None => format!("{name} dead r{} L{} g{}", p.respawn, p.level, p.gold),
        }
    }).collect();
    if parts.is_empty() {
        parts = rows.units.iter().filter(|u| u.kind == EntityKindV1::Champion.code()).map(|u| {
            format!("{}#{} {}/{} ({},{}) b{}", short(names.get(u.name)), u.id, u.hp.0, u.hp.1, u.pos.0, u.pos.1,
                    u.buffs.len())
        }).collect();
    }
    if parts.is_empty() {
        parts.push("no champions".into());
    }
    parts.join("; ")
}

/// The buffs of two rows as a phrase when they differ: the names only on one side, else the order.
fn buff_change(x: &[u32], y: &[u32], names: &Names, la: &str, lb: &str) -> Option<String> {
    if x == y {
        return None;
    }
    let minus = |a: &[u32], b: &[u32]| -> Vec<u32> {
        let mut rest = b.to_vec();
        a.iter().filter(|k| match rest.iter().position(|r| r == *k) {
            Some(i) => {
                rest.swap_remove(i);
                false
            }
            None => true,
        }).copied().collect()
    };
    let (only_a, only_b) = (minus(x, y), minus(y, x));
    if only_a.is_empty() && only_b.is_empty() {
        return Some(format!("buffs in another order {} vs {}", names.list(x), names.list(y)));
    }
    let mut parts = Vec::new();
    if !only_a.is_empty() {
        parts.push(format!("buffs only in {la}: {}", names.list(&only_a)));
    }
    if !only_b.is_empty() {
        parts.push(format!("buffs only in {lb}: {}", names.list(&only_b)));
    }
    Some(parts.join("; "))
}

fn player_change(x: &KeptPlayer, y: &KeptPlayer, names: &Names, la: &str, lb: &str) -> String {
    let mut what = Vec::new();
    if x.name != y.name {
        what.push(format!("champion {} vs {}", short(names.get(x.name)), short(names.get(y.name))));
    }
    if x.team != y.team {
        what.push(format!("team {} vs {}", x.team, y.team));
    }
    if x.gold != y.gold {
        what.push(format!("gold {} vs {}", x.gold, y.gold));
    }
    if x.items != y.items {
        what.push(format!("items {} vs {}", names.list(&x.items), names.list(&y.items)));
    }
    if x.level != y.level {
        what.push(format!("level {} vs {}", x.level, y.level));
    }
    if x.alive != y.alive {
        what.push(format!("{} vs {}", if x.alive { "alive" } else { "dead" }, if y.alive { "alive" } else { "dead" }));
    }
    if x.respawn != y.respawn {
        what.push(format!("respawn {} vs {}", x.respawn, y.respawn));
    }
    if x.champ != y.champ {
        what.push(format!("champion entity #{} vs #{}", x.champ, y.champ));
    }
    if x.kda != y.kda {
        let f = |k: &[usize; 4]| format!("{}/{}/{}/{}", k[0], k[1], k[2], k[3]);
        what.push(format!("k/d/a/cs {} vs {}", f(&x.kda), f(&y.kda)));
    }
    if x.cds != y.cds {
        let f = |c: &[usize; 4]| format!("{}/{}/{}/{}", c[0], c[1], c[2], c[3]);
        what.push(format!("cooldowns attack/skill/skill2/ult {} vs {}", f(&x.cds), f(&y.cds)));
    }
    for (k, name) in STATS.iter().enumerate() {
        if x.stat[k] != y.stat[k] {
            what.push(format!("{name} {} vs {}", x.stat[k], y.stat[k]));
        }
    }
    let name = short(names.get(x.name));
    format!("player {} {name} ({la} vs {lb}): {}", x.id, what.join(", "))
}

fn unit_change(x: &KeptUnit, y: &KeptUnit, names: &Names, la: &str, lb: &str) -> String {
    let mut what = Vec::new();
    if x.name != y.name {
        what.push(format!("name {} vs {}", names.get(x.name), names.get(y.name)));
    }
    if x.kind != y.kind {
        what.push(format!("kind {} vs {}", unit_kind(x.kind), unit_kind(y.kind)));
    }
    if x.team != y.team {
        what.push(format!("team {} vs {}", x.team, y.team));
    }
    if x.pos != y.pos {
        what.push(format!("pos ({},{}) vs ({},{})", x.pos.0, x.pos.1, y.pos.0, y.pos.1));
    }
    if x.hp != y.hp {
        what.push(format!("hp {}/{} vs {}/{}", x.hp.0, x.hp.1, y.hp.0, y.hp.1));
    }
    if x.shield != y.shield {
        what.push(format!("shield {} vs {}", x.shield, y.shield));
    }
    if x.cc != y.cc {
        what.push(format!("cc {} vs {}", x.cc, y.cc));
    }
    if x.targetable != y.targetable {
        let t = |b: bool| if b { "targetable" } else { "untargetable" };
        what.push(format!("{} vs {}", t(x.targetable), t(y.targetable)));
    }
    if let Some(b) = buff_change(&x.buffs, &y.buffs, names, la, lb) {
        what.push(b);
    }
    format!("{}#{} {} ({la} vs {lb}): {}", short(names.get(x.name)), x.id, unit_kind(x.kind), what.join(", "))
}

fn unit_alone(u: &KeptUnit, names: &Names, side: &str) -> String {
    format!("{}#{} {} only in {side} (team {}, ({},{}), {}/{}, buffs {})", short(names.get(u.name)), u.id,
            unit_kind(u.kind), u.team, u.pos.0, u.pos.1, u.hp.0, u.hp.1, names.list(&u.buffs))
}

/// The differing rows by class, in the order they are named.
fn classes_of(found: &[(&'static str, String)]) -> Vec<(&'static str, usize)> {
    let mut classes: Vec<(&'static str, usize)> = Vec::new();
    for f in found {
        match classes.iter_mut().find(|c| c.0 == f.0) {
            Some(c) => c.1 += 1,
            None => classes.push((f.0, 1)),
        }
    }
    classes
}

/// Whether a row's class is a structure (a tower or a nexus).
fn is_structure(class: &str) -> bool {
    class == "tower" || class == "nexus"
}

/// Every row that differs between `a` (side `la`) and `b` (side `lb`) as (class, a phrase naming its fields), in the
/// order they are named: players first, then champions, epic monsters, structures, summons, camps and minions, each by
/// id.
fn differing_rows(a: &Rows, b: &Rows, names: &Names, la: &str, lb: &str) -> Vec<(&'static str, String)> {
    let mut found: Vec<(u8, usize, &'static str, String)> = Vec::new();
    let mut ids: Vec<usize> = a.players.iter().chain(b.players.iter()).map(|p| p.id).collect();
    ids.sort_unstable();
    ids.dedup();
    for id in ids {
        let x = a.players.iter().find(|p| p.id == id);
        let y = b.players.iter().find(|p| p.id == id);
        let phrase = match (x, y) {
            (Some(x), Some(y)) if x != y => player_change(x, y, names, la, lb),
            (Some(x), None) => format!("player {id} {} only in {la}", short(names.get(x.name))),
            (None, Some(y)) => format!("player {id} {} only in {lb}", short(names.get(y.name))),
            _ => continue,
        };
        found.push((0, id, "player", phrase));
    }
    let (mut i, mut j) = (0, 0);
    while i < a.units.len() || j < b.units.len() {
        let (x, y) = (a.units.get(i), b.units.get(j));
        let (row, phrase) = match (x, y) {
            (Some(x), Some(y)) if x.id == y.id => {
                i += 1;
                j += 1;
                if x == y {
                    continue;
                }
                (x, unit_change(x, y, names, la, lb))
            }
            (Some(x), Some(y)) if x.id < y.id => {
                i += 1;
                (x, unit_alone(x, names, la))
            }
            (Some(x), None) => {
                i += 1;
                (x, unit_alone(x, names, la))
            }
            (_, Some(y)) => {
                j += 1;
                (y, unit_alone(y, names, lb))
            }
            (None, None) => break,
        };
        found.push((unit_rank(row.kind), row.id, unit_kind(row.kind), phrase));
    }
    found.sort_by_key(|f| (f.0, f.1));
    found.into_iter().map(|f| (f.2, f.3)).collect()
}

// ---- runs, pairs and the store ----

/// How one pair of runs of the same set compares so far.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Pair {
    /// the last tick they agreed on before they first differed (all agreeing ticks while they never did)
    pub agreed: Option<usize>,
    /// the first tick they differed at
    pub diverged: Option<usize>,
    /// differing at the latest tick compared
    pub apart: bool,
    /// the first tick they were equal again after differing, and how many times they were
    pub again: Option<usize>,
    pub agains: u32,
    /// ticks compared, and of them differing
    pub compared: u32,
    pub differ: u32,
    /// the latest tick compared
    pub last: Option<usize>,
    /// DIVERGE / EQUAL lines written
    pub lines: u32,
    /// The hook's per-tick rng seed differed while the state agreed: said once per pair, never a divergence by itself.
    pub rng_noted: bool,
}

struct Snap {
    tick: usize,
    hash: u64,
    rng: u64,
    count: usize,
    /// the rows, while kept (the budget)
    rows: Option<Rows>,
    /// the fine records after the run's snapshot before this one, up to this tick - kept and dropped with the rows
    fine: Option<Box<[Fine]>>,
    /// what the rows and fine records take, while kept
    bytes: usize,
}

struct Run {
    origin: Origin,
    no: u32,
    /// its set: the rng of its first snapshot (tick 0 or 1); None when it started later - never paired
    key: Option<u64>,
    snaps: VecDeque<Snap>,
    last_tick: usize,
    ended: bool,
    /// the store's clock at its latest snapshot
    updated: u64,
    /// its SYNC lines are written: it has had a partner
    synced: bool,
    /// by the other run's number
    pairs: HashMap<u32, Pair>,
    /// the fine records since its latest snapshot (the next one takes them)
    pending: Vec<Fine>,
    /// (player id, the champion he was last seen with): the fine brackets name them
    champs: Vec<(usize, String)>,
}

impl Run {
    fn head(&self) -> String {
        format!("[{} m={} s={} run {} thr {}]", kind_name(self.origin.kind), none_dash(self.origin.match_id),
            none_dash(self.origin.set), self.no, self.origin.thread)
    }

    fn label(&self) -> String {
        format!("{} run {}", kind_name(self.origin.kind), self.no)
    }

    fn at(&self, tick: usize) -> Option<&Snap> {
        self.snaps.iter().rev().find(|s| s.tick == tick)
    }

    /// Drops the rows (and fine records) of the snapshots at `range`, their names' references with them -> the bytes
    /// freed.
    fn drop_rows(&mut self, range: std::ops::Range<usize>, names: &mut Names) -> usize {
        let mut freed = 0;
        for s in self.snaps.range_mut(range) {
            if let Some(rows) = s.rows.take() {
                names.release_rows(&rows);
            }
            s.fine = None;
            freed += s.bytes;
            s.bytes = 0;
        }
        freed
    }

    fn kept_bytes(&self) -> usize {
        self.snaps.iter().map(|s| s.bytes).sum()
    }

    /// Every kept row's references to the names given back (the run itself goes) -> the bytes it kept.
    fn forget(&self, names: &mut Names) -> usize {
        for rows in self.snaps.iter().filter_map(|s| s.rows.as_ref()) {
            names.release_rows(rows);
        }
        self.kept_bytes()
    }

    /// The fine records kept from just after `from` to `to`, in tick order.
    fn fines(&self, from: usize, to: usize) -> Vec<&Fine> {
        self.snaps.iter().filter(|s| s.tick > from).filter_map(|s| s.fine.as_deref()).flatten()
            .filter(|f| f.tick as usize > from && f.tick as usize <= to).collect()
    }

    fn champ(&self, player: usize) -> Option<&str> {
        self.champs.iter().find(|c| c.0 == player).map(|c| c.1.as_str())
    }
}

/// Between which fine records two runs first differ after `lo` (the last tick compared equal; None: none), up to
/// `tick`: `first differs between t 4260 and t 4320, player 0 akali, other units` - None when no fine record kept on
/// both sides differs.
fn bracket(mine: &Run, other: &Run, lo: Option<usize>, tick: usize) -> Option<String> {
    let from = lo.unwrap_or(0);
    let theirs = other.fines(from, tick);
    let mut last = lo;
    for x in mine.fines(from, tick) {
        let Some(y) = theirs.iter().find(|y| y.tick == x.tick) else { continue };
        if x == *y {
            last = Some(x.tick as usize);
            continue;
        }
        let mut ids: Vec<u32> = x.players.iter().chain(y.players.iter()).map(|p| p.0).collect();
        ids.sort_unstable();
        ids.dedup();
        let hash = |f: &Fine, id: u32| f.players.iter().find(|p| p.0 == id).map(|p| p.1);
        let differ: Vec<u32> = ids.into_iter().filter(|&id| hash(x, id) != hash(y, id)).collect();
        let mut who: Vec<String> = differ.iter().take(BRACKET_PLAYERS).map(|&id| {
            match mine.champ(id as usize).or_else(|| other.champ(id as usize)) {
                Some(c) => format!("player {id} {}", short(c)),
                None => format!("player {id}"),
            }
        }).collect();
        if differ.len() > BRACKET_PLAYERS {
            who.push(format!("{} more players", differ.len() - BRACKET_PLAYERS));
        }
        if x.rest != y.rest {
            who.push("other units".to_string());
        }
        let span = match last {
            Some(a) => format!("between t {a} and t {}", x.tick),
            None => format!("by t {}", x.tick),
        };
        return Some(format!("first differs {span}, {}", who.join(", ")));
    }
    None
}

struct Bucket {
    match_id: u64,
    runs: Vec<Run>,
    next_no: u32,
    updated: u64,
}

impl Bucket {
    /// The other runs of run `i`'s set.
    fn partners(&self, i: usize) -> Vec<usize> {
        let Some(key) = self.runs[i].key else { return Vec::new() };
        (0..self.runs.len()).filter(|&j| j != i && self.runs[j].key == Some(key)).collect()
    }

    fn has_partner(&self, i: usize) -> bool {
        !self.partners(i).is_empty()
    }

    /// Some set of it has two runs or more.
    fn paired(&self) -> bool {
        (0..self.runs.len()).any(|i| self.has_partner(i))
    }
}

/// Every match's runs; the lines to log come back from `record`, so the store itself never touches the log (tests).
#[derive(Default)]
pub struct Store {
    buckets: Vec<Bucket>,
    names: Names,
    /// a counter that goes up with every snapshot (least recently updated = smallest)
    clock: u64,
    /// bytes of kept rows in all
    bytes: usize,
    /// the next run number of a match whose record went (a match coming back keeps numbering)
    numbers: HashMap<u64, u32>,
}

impl Store {
    /// Files one snapshot and returns the lines to log.
    pub fn record(&mut self, origin: Origin, snap: Snapshot) -> Vec<String> {
        self.clock += 1;
        let now = self.clock;
        let bi = self.bucket_of(origin.match_id);
        let ri = self.run_of(bi, origin, snap.tick, snap.rng);
        let rows = Rows::keep(&snap, &mut self.names);
        let tick = snap.tick;
        {
            let b = &mut self.buckets[bi];
            b.updated = now;
            let run = &mut b.runs[ri];
            // the fine records since its last snapshot, and this tick's own
            let since = run.last_tick;
            let mut fine: Vec<Fine> = std::mem::take(&mut run.pending).into_iter()
                .filter(|f| f.tick as usize > since && (f.tick as usize) < tick).collect();
            fine.push(Fine::of(&snap));
            let bytes = rows.bytes() + fine.iter().map(Fine::bytes).sum::<usize>();
            self.bytes += bytes;
            for p in snap.players.iter().filter(|p| !p.name.is_empty()) {
                match run.champs.iter_mut().find(|c| c.0 == p.id) {
                    Some(c) if c.1 != p.name => c.1.clone_from(&p.name),
                    Some(_) => {}
                    None => run.champs.push((p.id, p.name.clone())),
                }
            }
            run.updated = now;
            run.last_tick = tick;
            if tick <= 1 {
                run.key = Some(snap.rng);
            }
            run.snaps.push_back(Snap { tick, hash: snap.hash, rng: snap.rng, count: snap.count, rows: Some(rows),
                                       fine: Some(fine.into_boxed_slice()), bytes });
            while run.snaps.len() > KEEP {
                if let Some(s) = run.snaps.pop_front() {
                    if let Some(rows) = &s.rows {
                        self.names.release_rows(rows);
                    }
                    self.bytes -= s.bytes;
                }
            }
        }
        let mut out = Vec::new();
        let partners = self.buckets[bi].partners(ri);
        if !partners.is_empty() {
            self.sync(bi, ri, &partners, &mut out);
            for &oi in &partners {
                self.compare(bi, ri, oi, tick, &mut out);
            }
        }
        self.keep_rows(bi, ri);
        out
    }

    /// The match's bucket (made, the least wanted one going when MAX_MATCHES are kept).
    fn bucket_of(&mut self, match_id: u64) -> usize {
        if let Some(i) = self.buckets.iter().position(|b| b.match_id == match_id) {
            return i;
        }
        while self.buckets.len() >= MAX_MATCHES {
            // first the matches without a pair, then by the last update
            let victim = (0..self.buckets.len()).min_by_key(|&i| (self.buckets[i].paired(), self.buckets[i].updated)).unwrap();
            let b = self.buckets.remove(victim);
            for r in &b.runs {
                self.bytes -= r.forget(&mut self.names);
            }
            if self.numbers.len() > 4096 {
                self.numbers.clear();
            }
            self.numbers.insert(b.match_id, b.next_no);
        }
        let next_no = self.numbers.remove(&match_id).unwrap_or(1);
        self.buckets.push(Bucket { match_id, runs: Vec::new(), next_no, updated: self.clock });
        self.buckets.len() - 1
    }

    /// The run of `origin` a snapshot at `tick` goes to: the latest one of this origin while its ticks still go up,
    /// else a new one (a set run again starts at tick 0 or 1).
    fn run_of(&mut self, bi: usize, origin: Origin, tick: usize, rng: u64) -> usize {
        let b = &mut self.buckets[bi];
        let latest = b.runs.iter().rposition(|r| r.origin == origin);
        if let Some(i) = latest.filter(|&i| b.runs[i].last_tick < tick && !b.runs[i].ended) {
            return i;
        }
        while b.runs.len() >= MAX_RUNS {
            let victim = (0..b.runs.len()).min_by_key(|&i| (b.has_partner(i), b.runs[i].updated)).unwrap();
            let r = b.runs.remove(victim);
            self.bytes -= r.forget(&mut self.names);
        }
        let no = b.next_no;
        b.next_no += 1;
        b.runs.push(Run { origin, no, key: (tick <= 1).then_some(rng), snaps: VecDeque::new(), last_tick: 0,
                          ended: false, updated: self.clock, synced: false, pairs: HashMap::new(), pending: Vec::new(),
                          champs: Vec::new() });
        b.runs.len() - 1
    }

    /// Whether the latest run of `origin` is going and has a partner (another run of its set): the hook makes fine
    /// records for those only - a background presim (most simulations, never paired) would only pay for them.
    pub fn paired(&self, origin: Origin) -> bool {
        self.buckets.iter().find(|b| b.match_id == origin.match_id).is_some_and(|b| {
            b.runs.iter().rposition(|r| r.origin == origin).is_some_and(|i| !b.runs[i].ended && b.has_partner(i))
        })
    }

    /// Files one fine record (every `FINE` ticks between the snapshots) with its run: the run's next snapshot keeps
    /// it. Nothing for a run not seen yet or ended.
    pub fn fine(&mut self, origin: Origin, fine: Fine) {
        let Some(b) = self.buckets.iter_mut().find(|b| b.match_id == origin.match_id) else { return };
        let Some(run) = b.runs.iter_mut().rev().find(|r| r.origin == origin) else { return };
        if run.ended || fine.tick as usize <= run.last_tick {
            return;
        }
        if run.pending.len() >= 2 * EVERY / FINE {
            run.pending.remove(0);
        }
        run.pending.push(fine);
    }

    fn sync_line(&self, run: &Run, s: &Snap) -> String {
        let mut line = format!("SYNC {} t={} rng={:016x} n={} h={:016x}", run.head(), s.tick, s.rng, s.count, s.hash);
        if s.tick <= 1 {
            line.push_str(&format!(" seed={:016x}", run.origin.seed));
        }
        if let Some(rows) = s.rows.as_ref().filter(|_| s.tick <= 1 || s.tick % SUMMARY_EVERY == 0) {
            line.push_str(" | ");
            line.push_str(&summary(rows, &self.names));
        }
        line
    }

    /// The SYNC lines of run `ri` (and of partners written for the first time, the snapshots they had so far).
    fn sync(&mut self, bi: usize, ri: usize, partners: &[usize], out: &mut Vec<String>) {
        let b = &self.buckets[bi];
        let run = &b.runs[ri];
        let mut late = Vec::new();
        if !run.synced {
            let seeds: Vec<String> = partners.iter().map(|&j| {
                let p = &b.runs[j];
                format!("{} (seed {:016x})", p.label(), p.origin.seed)
            }).collect();
            out.push(format!("SET {} same set as {} - rng {:016x} at its first tick, seed {:016x}", run.head(),
                             seeds.join(", "), run.key.unwrap_or(0), run.origin.seed));
            late.push(ri);
        }
        late.extend(partners.iter().copied().filter(|&j| !b.runs[j].synced));
        for &j in &late {
            let r = &b.runs[j];
            let upto = if j == ri { r.snaps.len() - 1 } else { r.snaps.len() };
            for s in r.snaps.iter().take(upto) {
                out.push(self.sync_line(r, s));
            }
        }
        let run = &self.buckets[bi].runs[ri];
        out.push(self.sync_line(run, run.snaps.back().unwrap()));
        for j in late {
            self.buckets[bi].runs[j].synced = true;
        }
    }

    /// Compares run `ri`'s snapshot at `tick` with run `oi`'s, if it has one.
    fn compare(&mut self, bi: usize, ri: usize, oi: usize, tick: usize, out: &mut Vec<String>) {
        let b = &self.buckets[bi];
        let (mine, other) = (&b.runs[ri], &b.runs[oi]);
        let (Some(a), Some(o)) = (mine.at(tick), other.at(tick)) else { return };
        let mut p = mine.pairs.get(&other.no).copied().unwrap_or_default();
        // the last tick compared equal (the fine bracket starts after it)
        let equal_at = if p.apart { None } else { p.last };
        p.compared += 1;
        p.last = Some(tick);
        let same = a.hash == o.hash && a.count == o.count;
        if same {
            if p.apart {
                p.apart = false;
                p.agains += 1;
                p.again.get_or_insert(tick);
                if p.lines < PAIR_LINES {
                    p.lines += 1;
                    out.push(format!("EQUAL {} vs {} equal again at tick {tick} (apart from {}, {} of {} compared ticks \
                                      differ so far)", mine.head(), other.head(),
                                     p.diverged.map_or("?".to_string(), |d| d.to_string()), p.differ, p.compared));
                }
            }
            if p.diverged.is_none() {
                p.agreed = Some(tick);
            }
            if a.rng != o.rng && !p.rng_noted {
                p.rng_noted = true;
                out.push(format!("RNG {} vs {} the hook's rng seed differs at tick {tick} ({:016x} vs {:016x}) while the \
                                  state agrees", mine.head(), other.head(), a.rng, o.rng));
            }
        } else {
            p.differ += 1;
            if !p.apart {
                p.apart = true;
                let when = match p.diverged {
                    None => {
                        p.diverged = Some(tick);
                        let agreed = p.agreed.map_or("never agreed".to_string(), |t| format!("agreed at {t}"));
                        format!("first seen at tick {tick} ({agreed})")
                    }
                    Some(_) => format!("again at tick {tick} (equal again since {})",
                                       p.again.map_or("?".to_string(), |t| t.to_string())),
                };
                if p.lines < PAIR_LINES {
                    p.lines += 1;
                    let when = match bracket(mine, other, equal_at, tick) {
                        Some(fine) => format!("{when}; {fine}"),
                        None => when,
                    };
                    out.push(self.diverge_line(mine, other, a, o, &when));
                }
            }
        }
        let (mine_no, other_no) = (mine.no, other.no);
        let b = &mut self.buckets[bi];
        b.runs[ri].pairs.insert(other_no, p);
        b.runs[oi].pairs.insert(mine_no, p);
    }

    fn diverge_line(&self, mine: &Run, other: &Run, a: &Snap, o: &Snap, when: &str) -> String {
        let (la, lb) = (mine.label(), other.label());
        let what = match (&a.rows, &o.rows) {
            (Some(x), Some(y)) => {
                let diffs = differing_rows(x, y, &self.names, &la, &lb);
                match diffs.split_first() {
                    Some((first, rest)) => {
                        let mut s = first.1.clone();
                        if !rest.is_empty() {
                            let also: Vec<&str> = rest.iter().take(ALSO).map(|d| d.1.as_str()).collect();
                            s.push_str(&format!(" | also: {}", also.join("; ")));
                        }
                        // the towers and nexuses that differ, not named yet: always (11-08's one lead was the nexus's
                        // third-party buffs, and players and champions fill the first rows)
                        let structures: Vec<&str> =
                            rest.iter().skip(ALSO).filter(|d| is_structure(d.0)).map(|d| d.1.as_str()).collect();
                        if !structures.is_empty() {
                            s.push_str(&format!(" | structures: {}", structures.iter().take(STRUCTURES).copied()
                                .collect::<Vec<_>>().join("; ")));
                            if structures.len() > STRUCTURES {
                                s.push_str(&format!(" (+{} more)", structures.len() - STRUCTURES));
                            }
                        }
                        let by: Vec<String> = classes_of(&diffs).iter().map(|(c, n)| format!("{n} {c}")).collect();
                        s.push_str(&format!(" | {} rows differ: {}", diffs.len(), by.join(", ")));
                        s
                    }
                    // the kept rows hold everything the hash sees, and a name goes only with the last row naming it:
                    // only a name past MAX_NAMES (read "?" on both sides) could leave them agreeing
                    None => "the kept rows agree - a name past the table's cap differs".to_string(),
                }
            }
            (Some(_), None) => format!("{lb}'s rows at this tick are no longer kept: the hashes differ"),
            (None, _) => format!("{la}'s rows at this tick are no longer kept: the hashes differ"),
        };
        let sum = |s: &Snap| s.rows.as_ref().map_or("(rows not kept)".to_string(), |r| summary(r, &self.names));
        format!("DIVERGE {} vs {} {when}: {what} | n {} vs {}, rng {} | {la}: {} | {lb}: {}", mine.head(), other.head(),
                a.count, o.count, if a.rng == o.rng { "same" } else { "differs" }, sum(a), sum(o))
    }

    /// The rows kept after a snapshot of run `ri`: an unpaired run keeps its first and its last WINDOW snapshots'; past
    /// the budget the rows of other runs go - unpaired before paired, the least recently updated first - but their
    /// first snapshot's.
    fn keep_rows(&mut self, bi: usize, ri: usize) {
        if !self.buckets[bi].has_partner(ri) {
            let run = &mut self.buckets[bi].runs[ri];
            let n = run.snaps.len();
            if n > WINDOW + 1 {
                self.bytes -= run.drop_rows(1..n - WINDOW, &mut self.names);
            }
        }
        while self.bytes + self.names.bytes > DETAIL_BUDGET {
            let mut victim: Option<((bool, u64), usize, usize)> = None;
            for (b, bucket) in self.buckets.iter().enumerate() {
                for (r, run) in bucket.runs.iter().enumerate() {
                    if (b, r) == (bi, ri) || !run.snaps.iter().skip(1).any(|s| s.rows.is_some()) {
                        continue;
                    }
                    let rank = (bucket.has_partner(r), run.updated);
                    if victim.is_none_or(|v| rank < v.0) {
                        victim = Some((rank, b, r));
                    }
                }
            }
            let Some((_, b, r)) = victim else { break };
            let run = &mut self.buckets[b].runs[r];
            let n = run.snaps.len();
            self.bytes -= run.drop_rows(1..n, &mut self.names);
        }
    }

    /// Marks the run ended and returns its END line (once, and only for a run with a partner): `blue_diff` the
    /// simulation's score difference for blue, `kills` each team's kills by its players (blue, red) - log.log's
    /// server_score and live_score respectively (the module's notes, 0.9.21).
    pub fn end(&mut self, origin: Origin, tick: usize, count: usize, blue_diff: i32, kills: (usize, usize))
               -> Option<String> {
        let bi = self.buckets.iter().position(|b| b.match_id == origin.match_id)?;
        let b = &mut self.buckets[bi];
        let ri = (0..b.runs.len()).filter(|&i| b.runs[i].origin == origin && !b.runs[i].ended)
            .max_by_key(|&i| b.runs[i].last_tick)?;
        b.runs[ri].ended = true;
        if !b.has_partner(ri) {
            return None;
        }
        let run = &b.runs[ri];
        let mut pairs: Vec<(&u32, &Pair)> = run.pairs.iter().collect();
        pairs.sort_by_key(|(no, _)| **no);
        let verdicts: Vec<String> = pairs.iter().map(|(no, p)| {
            let name = b.runs.iter().find(|r| r.no == **no).map_or_else(|| format!("run {no}"), Run::label);
            verdict(&name, p)
        }).collect();
        let verdict = if verdicts.is_empty() { "no other run of its set reached the same ticks".to_string() }
            else { verdicts.join("; ") };
        Some(format!("END {} t={tick} n={count} blue score diff={blue_diff:+} (kills {}:{}): {verdict}", run.head(),
                     kills.0, kills.1))
    }

    /// The pair record between two runs of a match (tests).
    pub fn pair(&self, match_id: u64, a: u32, b: u32) -> Option<Pair> {
        let m = self.buckets.iter().find(|m| m.match_id == match_id)?;
        m.runs.iter().find(|r| r.no == a)?.pairs.get(&b).copied()
    }

    /// The matches kept (tests).
    pub fn matches(&self) -> Vec<u64> {
        self.buckets.iter().map(|b| b.match_id).collect()
    }

    /// Snapshots of run `no` of a match whose rows are kept, by tick (tests).
    pub fn kept(&self, match_id: u64, no: u32) -> Vec<usize> {
        let Some(b) = self.buckets.iter().find(|b| b.match_id == match_id) else { return Vec::new() };
        b.runs.iter().find(|r| r.no == no)
            .map_or_else(Vec::new, |r| r.snaps.iter().filter(|s| s.rows.is_some()).map(|s| s.tick).collect())
    }

    /// Bytes of kept rows, fine records and names (tests).
    pub fn kept_bytes(&self) -> usize {
        self.bytes + self.names.bytes
    }

    /// The ticks of the fine records kept with run `no`'s snapshot at `tick` (tests).
    pub fn fine_ticks(&self, match_id: u64, no: u32, tick: usize) -> Vec<u32> {
        let Some(b) = self.buckets.iter().find(|b| b.match_id == match_id) else { return Vec::new() };
        b.runs.iter().find(|r| r.no == no).and_then(|r| r.at(tick)).and_then(|s| s.fine.as_deref())
            .map_or_else(Vec::new, |f| f.iter().map(|f| f.tick).collect())
    }

    /// Names in the table now, and its slots (tests).
    pub fn names_held(&self) -> (usize, usize) {
        (self.names.ids.len(), self.names.list.len())
    }

    /// Every kept reference to a name counted again from the kept rows: Err with the first name whose count is off, or
    /// a name kept with no row naming it (tests).
    pub fn check_names(&self) -> Result<(), String> {
        let mut refs: HashMap<u32, u32> = HashMap::new();
        let mut add = |k: u32| *refs.entry(k).or_default() += 1;
        for rows in self.buckets.iter().flat_map(|b| b.runs.iter()).flat_map(|r| r.snaps.iter())
            .filter_map(|s| s.rows.as_ref()) {
            for p in &rows.players {
                add(p.name);
                p.items.iter().for_each(|&i| add(i));
            }
            for u in &rows.units {
                add(u.name);
                u.buffs.iter().for_each(|&b| add(b));
            }
        }
        for (k, slot) in self.names.list.iter().enumerate() {
            let want = refs.get(&(k as u32)).copied().unwrap_or(0);
            match slot {
                Some((name, n)) if *n != want => return Err(format!("{name} (#{k}) counted {n}, named {want} times")),
                Some((name, _)) if self.names.ids.get(&**name) != Some(&(k as u32)) => {
                    return Err(format!("{name} (#{k}) is not in the map under its id"));
                }
                None if want > 0 => return Err(format!("#{k} is free and named {want} times")),
                _ => {}
            }
        }
        if refs.contains_key(&UNNAMED) {
            return Err("a kept row reads ?".to_string());
        }
        if self.names.ids.len() != self.names.list.iter().flatten().count() {
            return Err("the map and the slots disagree".to_string());
        }
        Ok(())
    }
}

/// How a pair went, for the END line.
fn verdict(name: &str, p: &Pair) -> String {
    match (p.agreed, p.diverged) {
        (_, None) if p.compared == 0 => format!("vs {name} never at the same tick"),
        (_, None) => format!("vs {name} agreed through {} ({} ticks compared)", p.last.unwrap_or(0), p.compared),
        (agreed, Some(d)) => {
            let agreed = agreed.map_or("never agreed".to_string(), |a| format!("agreed through {a}"));
            let after = match p.again {
                Some(e) => format!(", equal again {}x (first at {e}){}", p.agains,
                                   if p.apart { ", apart at the end" } else { ", equal at the end" }),
                None => ", never equal again".to_string(),
            };
            format!("vs {name} {agreed}, diverged at {d}, apart at {} of {} compared ticks{after}", p.differ, p.compared)
        }
    }
}

static STORE: LazyLock<Mutex<Store>> = LazyLock::new(|| Mutex::new(Store::default()));
static NO_ORIGIN: Mutex<bool> = Mutex::new(false);

fn thread_no() -> u64 {
    // ThreadId's Debug is `ThreadId(17)`; the number is all we show
    let s = format!("{:?}", std::thread::current().id());
    s.trim_start_matches(|c: char| !c.is_ascii_digit()).trim_end_matches(|c: char| !c.is_ascii_digit()).parse().unwrap_or(0)
}

/// Reads every player and living entity of the simulation into rows.
pub fn snapshot(sim: &StableSim<'_>, rng: u64) -> Snapshot {
    let tick = sim.tick();
    let mut units = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if !e.is_alive() || e.id() == usize::MAX {
            continue;
        }
        let buffs = (0..e.buff_count()).filter_map(|b| e.buff_at(b))
            .map(|b| b.name().to_string()).filter(|n| !is_sim_tag(n)).collect();
        units.push(Unit {
            id: e.id(), name: e.name().unwrap_or_default(), kind: e.kind().map_or(u32::MAX, |k| k.code()),
            team: e.team(), pos: e.pos(), hp: e.hp(), shield: e.shield(), cc: e.cc_count(), targetable: e.is_targetable(),
            buffs,
        });
    }
    let mut players = Vec::new();
    for i in 0..sim.player_count() {
        let Some(p) = sim.player_at(i) else { continue };
        let champ = p.champion();
        let stat = champ.as_ref().map_or([0; 9], |c| {
            let s = c.stat();
            [s.attack, s.magic_power, s.hp, s.defence, s.magic_resistance, s.move_speed, s.hp_regen, s.stack, s.crit_chance]
        });
        let cds = p.cooldowns().map_or([0; 4], |(a, q, w, r)| [a, q, w, r]);
        players.push(Player {
            id: p.id(), team: p.team(), champ: champ.as_ref().map_or(usize::MAX, |c| c.id()),
            name: champ.as_ref().and_then(|c| c.name()).unwrap_or_default(), gold: p.gold(), level: p.level(),
            respawn: p.respawn_time(), alive: p.is_alive(), kda: [p.kills(), p.deaths(), p.assists(), p.cs()], cds,
            items: p.item_keys(), stat,
        });
    }
    Snapshot::new(tick, rng, players, units)
}

/// The match hook: a snapshot every `EVERY` ticks (and on the first tick), compared with the other runs of its set,
/// and a fine record every `FINE` ticks between them.
pub struct Diverge;

impl StableMatchHook for Diverge {
    fn on_match_tick(&self, sim: &mut StableSim<'_>, rng_seed: u64) {
        let Some(o) = sim.sim_origin() else {
            let mut said = NO_ORIGIN.lock().unwrap_or_else(|e| e.into_inner());
            if !*said {
                *said = true;
                wlog("SYNC off: the host gives no sim_origin (ABI level < 6)");
            }
            return;
        };
        let tick = sim.tick();
        let ended = sim.is_end();
        let on_grid = tick % EVERY == 0 || tick <= 1;
        let fine = !on_grid && tick % FINE == 0;
        if !on_grid && !ended && !fine {
            return;
        }
        // matchless simulations (the vanilla pairs the game runs at startup, m=-) go to a bucket of their own, paired by
        // their first rng like the rest
        let origin = Origin { kind: o.kind, match_id: o.match_id, set: o.set_index, seed: sim.seed(), thread: thread_no() };
        // a fine record only for a run with a partner (it pairs when another run of its set files its first snapshot:
        // the twins and the view start within a second of each other; a background presim never pairs)
        if fine && !ended && !STORE.lock().unwrap_or_else(|e| e.into_inner()).paired(origin) {
            return;
        }
        let snap = snapshot(sim, rng_seed);
        let count = snap.count;
        let kills = team_kills(&snap.players);
        // between the snapshots only the fine record goes in (worked out before the lock)
        let between = fine.then(|| Fine::of(&snap));
        let lines = {
            let mut store = STORE.lock().unwrap_or_else(|e| e.into_inner());
            let mut lines = if on_grid { store.record(origin, snap) } else { Vec::new() };
            if let Some(f) = between {
                store.fine(origin, f);
            }
            if ended {
                if let Some(end) = store.end(origin, tick, count, sim.score_diff(0), kills) {
                    lines.push(end);
                }
            }
            lines
        };
        for line in lines {
            wlog(line);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn unit(id: usize, kind: EntityKindV1, hp: usize, buffs: &[&str]) -> Unit {
        Unit { id, name: format!("league_u{id}"), kind: kind.code(), team: id % 2, pos: (1000 * id as u64, 7), hp: (hp, 1000),
               shield: 0, cc: 0, targetable: true, buffs: buffs.iter().map(|s| s.to_string()).collect() }
    }

    fn player(id: usize, champ: usize, gold: usize) -> Player {
        Player { id, team: id % 2, champ, name: format!("league_c{champ}"), gold, level: 3, respawn: 0, alive: true,
                 kda: [0; 4], cds: [0, 120, 0, 600], items: vec!["boots".into()], stat: [60, 0, 1000, 30, 30, 330, 5, 0, 0] }
    }

    /// Two champions (#18, #23), their players, a minion (#300) and a tower (#40).
    fn world(hp18: usize, minion_buffs: &[&str], gold1: usize) -> (Vec<Player>, Vec<Unit>) {
        let players = vec![player(1, 18, gold1), player(2, 23, 500)];
        let units = vec![unit(18, EntityKindV1::Champion, hp18, &["a"]), unit(23, EntityKindV1::Champion, 500, &[]),
                         unit(300, EntityKindV1::Minion, 300, minion_buffs), unit(40, EntityKindV1::Tower, 3000, &[])];
        (players, units)
    }

    fn snap(tick: usize, rng: u64, hp18: usize, minion_buffs: &[&str], gold1: usize) -> Snapshot {
        let (p, u) = world(hp18, minion_buffs, gold1);
        Snapshot::new(tick, rng, p, u)
    }

    const PRESIM: u32 = 1;
    const VIEW: u32 = 2;
    const SET4: u64 = 0x5e4;

    fn origin(kind: u32, set: u64, thread: u64) -> Origin {
        Origin { kind, match_id: 2636, set, seed: 99, thread }
    }

    fn with<'a>(lines: &'a [String], start: &str) -> Vec<&'a String> {
        lines.iter().filter(|l| l.starts_with(start)).collect()
    }

    /// Change number `k` of one field of the state (false past the last).
    fn change(k: usize, p: &mut [Player], u: &mut Vec<Unit>) -> bool {
        match k {
            0 => u[0].hp.0 += 1,
            1 => u[1].pos.0 += 1,
            2 => u[2].buffs.push("x".into()),
            3 => u[0].buffs[0] = "b".into(),
            4 => u[3].shield = 5,
            5 => u[2].targetable = false,
            6 => u[0].cc = 1,
            7 => {
                u.pop();
            }
            8 => u[1].name = "league_other".into(),
            9 => p[0].gold += 1,
            10 => p[0].level += 1,
            11 => p[1].items.push("sword".into()),
            12 => p[0].cds[3] = 0,
            13 => p[1].stat[5] += 5,
            14 => p[0].respawn = 300,
            15 => p[0].alive = false,
            16 => p[0].kda[3] += 1,
            17 => p[0].champ = 1029,
            _ => return false,
        }
        true
    }

    #[test]
    fn hash_ignores_order_and_sim_tags_but_not_state() {
        let (mut p, mut u) = world(900, &[], 400);
        let h = hash_rows(&mut p, &mut u);
        // the order the game lists them in, and a simulation's own tag: the same
        p.reverse();
        u.reverse();
        assert_eq!(hash_rows(&mut p, &mut u), h);
        u[0].buffs.push("league_azir_sim:17".into());
        assert_eq!(hash_rows(&mut p, &mut u), h);
        // every field of the state: different
        for k in 0.. {
            let (mut p, mut u) = world(900, &[], 400);
            if !change(k, &mut p, &mut u) {
                assert!(k > 15);
                break;
            }
            assert_ne!(hash_rows(&mut p, &mut u), h, "change {k}");
        }
    }

    /// 11-06: the presims carry s=- and every run of a match was compared with every other - 358 of 394 DIVERGE lines
    /// were two different sets "first seen at tick 1". Only runs whose first rng is the same are a set.
    #[test]
    fn runs_of_other_sets_are_never_compared() {
        let mut store = Store::default();
        let (a, b) = (origin(PRESIM, SimOriginV1::NONE, 7), origin(PRESIM, SimOriginV1::NONE, 8));
        for t in [1, 600, 1200] {
            assert!(store.record(a, snap(t, 0xa, 900, &[], 400)).is_empty(), "a single presim: no line");
            assert!(store.record(b, snap(t, 0xb, 800, &["x"], 300)).is_empty(), "another set: never compared");
        }
        assert_eq!(store.pair(2636, 1, 2), None);
        assert_eq!(store.end(a, 1300, 4, 0, (0, 0)), None, "no END without a partner");
    }

    #[test]
    fn twins_and_view_name_the_first_row_and_keep_comparing() {
        let mut store = Store::default();
        let p1 = origin(PRESIM, SimOriginV1::NONE, 7);
        let p2 = origin(PRESIM, SimOriginV1::NONE, 8);
        let v = origin(VIEW, SET4, 1);
        // tick 1: the first presim alone writes nothing; its twin pairs them (the first's line comes then), then the view
        assert!(store.record(p1, snap(1, 5, 1000, &[], 400)).is_empty());
        let lines = store.record(p2, snap(1, 5, 1000, &[], 400));
        assert!(lines[0].starts_with("SET [presim m=2636 s=- run 2 thr 8] same set as presim run 1"), "{lines:?}");
        assert_eq!(with(&lines, "SYNC").len(), 2, "the twin's and the first presim's own: {lines:?}");
        assert!(lines.iter().any(|l| l.starts_with("SYNC [presim m=2636 s=- run 1 thr 7] t=1 ") && l.contains(" seed=")));
        assert!(lines.iter().any(|l| l.contains("c18#18 L3 g400 1000/1000 (18000,7) b1")), "{lines:?}");
        let lines = store.record(v, snap(1, 5, 1000, &[], 400));
        assert!(lines[0].contains("same set as presim run 1 (seed 0000000000000063), presim run 2"), "{lines:?}");
        assert_eq!(store.pair(2636, 3, 1), Some(Pair { agreed: Some(1), compared: 1, last: Some(1), ..Pair::default() }));
        // tick 600: the twins agree; the view's minion carries a buff the presims' does not
        store.record(p1, snap(600, 6, 900, &[], 400));
        assert_eq!(store.record(p2, snap(600, 6, 900, &[], 400)).len(), 1, "a SYNC line, no DIVERGE");
        let lines = store.record(v, snap(600, 6, 900, &["league_recall"], 400));
        let div = with(&lines, "DIVERGE");
        assert_eq!(div.len(), 2, "{lines:?}");
        assert!(div[0].contains("first seen at tick 600 (agreed at 1); first differs between t 1 and t 600, other units: \
                                 u300#300 minion (view run 3 vs presim run 1): buffs only in view run 3: [league_recall] | \
                                 1 rows differ: 1 minion"), "{}", div[0]);
        assert!(div[0].contains("rng same"), "{}", div[0]);
        assert_eq!(store.pair(2636, 1, 2).unwrap().diverged, None);
        // tick 1200: equal again
        store.record(p1, snap(1200, 7, 800, &[], 400));
        let lines = store.record(v, snap(1200, 7, 800, &[], 400));
        let eq = with(&lines, "EQUAL");
        assert_eq!(eq.len(), 1, "{lines:?}");
        assert!(eq[0].contains("vs [presim m=2636 s=- run 1 thr 7] equal again at tick 1200 (apart from 600"), "{}", eq[0]);
        // tick 1800: apart again - the player's gold and items this time, named first
        store.record(p1, snap(1800, 8, 700, &[], 400));
        let mut s = snap(1800, 8, 690, &[], 425);
        s.players[0].items.push("league_doran".into());
        s.units[0].pos = (1, 2);
        let s = Snapshot::new(s.tick, s.rng, s.players, s.units);
        let lines = store.record(v, s);
        let div = with(&lines, "DIVERGE");
        assert_eq!(div.len(), 1, "{lines:?}");
        assert!(div[0].contains("again at tick 1800 (equal again since 1200); first differs between t 1200 and t 1800, \
                                 player 1 c18: player 1 c18 (view run 3 vs presim run 1): \
                                 gold 425 vs 400, items [boots, league_doran] vs [boots] | also: u18#18 champion (view run 3 vs \
                                 presim run 1): pos (1,2) vs (18000,7), hp 690/1000 vs 700/1000 | 2 rows differ: 1 player, \
                                 1 champion"), "{}", div[0]);
        let p = store.pair(2636, 3, 1).unwrap();
        assert_eq!((p.agreed, p.diverged, p.again, p.agains, p.compared, p.differ, p.apart),
                   (Some(1), Some(600), Some(1200), 1, 4, 2, true));
        // the end line sums it up, once
        let end = store.end(v, 1900, 4, 3, (9, 6)).unwrap();
        assert!(end.contains("vs presim run 1 agreed through 1, diverged at 600, apart at 2 of 4 compared ticks, equal \
                              again 1x (first at 1200), apart at the end"), "{end}");
        assert!(end.contains("vs presim run 2 agreed through 1, diverged at 600"), "{end}");
        assert!(end.contains("blue score diff=+3 (kills 9:6): "), "{end}");
        assert!(store.end(v, 1901, 4, 3, (9, 6)).is_none(), "END once");
        let end = store.end(p1, 1900, 4, 3, (9, 6)).unwrap();
        assert!(end.contains("vs presim run 2 agreed through 600 (2 ticks compared)"), "{end}");
    }

    /// A partner that comes after the first run's start (the vanilla pairs at startup, a second view run minutes
    /// later): the first run's SYNC lines are written then, from its kept snapshots.
    #[test]
    fn a_late_partner_brings_the_first_runs_lines() {
        let mut store = Store::default();
        let none = |thread| Origin { kind: 0, match_id: SimOriginV1::NONE, set: SimOriginV1::NONE, seed: 3, thread };
        for t in [1, 600, 1200] {
            assert!(store.record(none(2), snap(t, 0x71, 900, &[], 400)).is_empty());
        }
        let lines = store.record(none(5), snap(1, 0x71, 900, &[], 400));
        assert!(lines[0].starts_with("SET [unknown m=- s=- run 2 thr 5] same set as unknown run 1"), "{lines:?}");
        let sync = with(&lines, "SYNC");
        assert_eq!(sync.len(), 4, "run 1's three, run 2's first: {lines:?}");
        assert!(sync[0].starts_with("SYNC [unknown m=- s=- run 1 thr 2] t=1 ") && sync[2].contains(" t=1200 "), "{sync:?}");
        // and they are compared like any set: the vanilla pairs too
        let lines = store.record(none(5), snap(600, 0x71, 900, &[], 401));
        assert!(with(&lines, "DIVERGE")[0].contains("player 1 c18 (unknown run 2 vs unknown run 1): gold 401 vs 400"),
                "{lines:?}");
    }

    /// 11-06: three matches kept, the oldest dropped - a series' first set has the server presim 7-10 matches at once,
    /// so the watched match went and its runs were numbered again. Now a match with a pair stays while unpaired ones
    /// come and go, the least recently updated first.
    #[test]
    fn a_match_with_a_pair_outlives_the_unwatched_ones() {
        let mut store = Store::default();
        let watched = |kind, thread| Origin { kind, match_id: 2853, set: 1, seed: 1, thread };
        store.record(watched(PRESIM, 31), snap(1, 0x90, 1000, &[], 0));
        store.record(watched(VIEW, 39), snap(1, 0x90, 1000, &[], 0));
        for m in 0..40u64 {
            let o = Origin { kind: PRESIM, match_id: 3000 + m, set: SimOriginV1::NONE, seed: m, thread: 26 };
            store.record(o, snap(1, m, 1000, &[], 0));
        }
        let kept = store.matches();
        assert_eq!(kept.len(), MAX_MATCHES);
        assert!(kept.contains(&2853), "{kept:?}");
        assert!(kept.contains(&3039) && !kept.contains(&3000), "the least recently updated go: {kept:?}");
        // the watched match's second view run, later: numbered on, compared with the first
        let lines = store.record(watched(VIEW, 40), snap(1, 0x90, 1000, &[], 0));
        assert!(lines[0].starts_with("SET [view m=2853 s=1 run 3 thr 40]"), "{lines:?}");
    }

    #[test]
    fn an_unpaired_run_keeps_its_first_and_last_rows_and_the_budget_holds() {
        let mut store = Store::default();
        let o = origin(PRESIM, SimOriginV1::NONE, 7);
        let n = WINDOW + 10;
        for k in 0..n {
            store.record(o, snap(if k == 0 { 1 } else { k * EVERY }, 3, 1000, &[], 0));
        }
        let kept = store.kept(2636, 1);
        assert_eq!(kept.len(), WINDOW + 1, "{kept:?}");
        assert_eq!(kept[0], 1);
        assert_eq!(kept[1], (n - WINDOW) * EVERY);
        // the budget: many paired runs' rows, the least recently updated go but their first snapshot's
        let mut store = Store::default();
        let big = |tick: usize, rng: u64| {
            let (p, mut u) = world(1000, &[], 0);
            for id in 1000..1400 {
                u.push(unit(id, EntityKindV1::Minion, 300, &["league_minion_buff_a", "league_minion_buff_b"]));
            }
            Snapshot::new(tick, rng, p, u)
        };
        for m in 0..6u64 {
            for thread in [1, 2] {
                let o = Origin { kind: PRESIM, match_id: 4000 + m, set: SimOriginV1::NONE, seed: m, thread };
                for k in 0..120 {
                    store.record(o, big(if k == 0 { 1 } else { k * EVERY }, m));
                }
            }
        }
        assert!(store.kept_bytes() <= DETAIL_BUDGET + DETAIL_BUDGET / 8, "{}", store.kept_bytes());
        assert_eq!(store.kept(4000, 1), vec![1], "the oldest run keeps only its first snapshot's rows");
        assert_eq!(store.kept(4005, 2).len(), 120, "the newest keeps all");
    }

    #[test]
    fn the_rows_say_every_kind_of_difference() {
        let mut names = Names::default();
        let (pa, ua) = world(900, &["a", "b", "c"], 400);
        let (mut pb, mut ub) = world(900, &["b", "a", "c"], 400);
        let a = Rows::keep(&Snapshot::new(600, 1, pa.clone(), ua.clone()), &mut names);
        let b = Rows::keep(&Snapshot::new(600, 1, pb.clone(), ub.clone()), &mut names);
        let d = differing_rows(&a, &b, &names, "view run 3", "presim run 1");
        assert_eq!(d, vec![("minion", "u300#300 minion (view run 3 vs presim run 1): buffs in another order [a, b, c] vs \
                                       [b, a, c]".to_string())]);
        assert_eq!(classes_of(&d), vec![("minion", 1)]);
        // a tower gone, a monster only on the other side, a player's level and stats
        ub.retain(|u| u.id != 40);
        ub.push(unit(55, EntityKindV1::Jungle, 700, &[]));
        pb[1].level = 4;
        pb[1].stat[0] = 66;
        pb[1].cds = [0, 0, 0, 600];
        let b = Rows::keep(&Snapshot::new(600, 1, pb, ub), &mut names);
        let d = differing_rows(&a, &b, &names, "x", "y");
        assert_eq!(d[0].1, "player 2 c23 (x vs y): level 3 vs 4, cooldowns attack/skill/skill2/ult 0/120/0/600 vs \
                            0/0/0/600, attack 60 vs 66");
        assert!(d[1].1.starts_with("u40#40 tower only in x (team 0, (40000,7), 3000/1000, buffs [])"), "{d:?}");
        assert!(d[2].1.starts_with("u55#55 monster only in y"), "{d:?}");
        assert_eq!(classes_of(&d), vec![("player", 1), ("tower", 1), ("monster", 1), ("minion", 1)]);
        let s = summary(&a, &names);
        assert_eq!(s, "c18#18 L3 g400 900/1000 (18000,7) b1; c23#23 L3 g500 500/1000 (23000,7) b0");
        let mut dead = pa;
        dead[0].alive = false;
        dead[0].respawn = 540;
        let r = Rows::keep(&Snapshot::new(600, 1, dead, ua), &mut names);
        assert!(summary(&r, &names).starts_with("c18 dead r540 L3 g400; "));
        assert!(is_sim_tag("league_drmundo_sim:3") && !is_sim_tag("league_drmundo_w_on"));
    }

    #[test]
    fn a_name_goes_with_its_last_reference_and_its_id_serves_the_next() {
        let mut n = Names::default();
        let a = n.id("league_akali");
        let b = n.id("tfm2_b2:2:80:0");
        assert_eq!(n.id("league_akali"), a, "a second reference");
        n.release(b);
        assert_eq!(n.get(b), "?", "its last reference gone");
        let c = n.id("tfm2_b2:2:1f7:0");
        assert_eq!(c, b, "the free id serves the next name");
        assert_eq!((n.get(a), n.get(c)), ("league_akali", "tfm2_b2:2:1f7:0"));
        n.release(a);
        assert_eq!(n.get(a), "league_akali", "one reference left");
        n.release(a);
        assert_eq!((n.get(a), n.ids.len()), ("?", 1));
        assert_eq!(n.bytes, NAME_COST + "tfm2_b2:2:1f7:0".len());
        n.release(UNNAMED);
        assert_eq!(n.ids.len(), 1);
    }

    /// 11-08: the names table only grew - every snapshot of every simulation (~780 background presims a launch) and
    /// third-party buffs with changing numbers - and was full 15 minutes in: 7 DIVERGE lines "the kept rows agree - a
    /// name past the kept ones differs", champions "?#18" in 259 of 554 summary lines. Now a name goes with the last kept
    /// row naming it: over a launch's worth of background presims (576 000 names; the old table held 65 536) the table
    /// stays small, and a match watched late names everything.
    #[test]
    fn names_stay_bounded_and_right_over_a_long_launch() {
        let mut store = Store::default();
        let background = |m: u64, tick: usize| {
            let units = (0..12usize).map(|i| Unit {
                id: 100 + i, name: format!("minion_{}", i % 3), kind: EntityKindV1::Minion.code(), team: i % 2,
                pos: (tick as u64, i as u64), hp: (300, 300), shield: 0, cc: 0, targetable: true,
                buffs: vec![format!("tfm2_b2:{i}:{:x}:0", tick as u64 * 7919 + m), format!("sed_timer1:{m}:{tick}")],
            }).collect();
            Snapshot::new(tick, 0x1000 + m, vec![player(1, 100, tick)], units)
        };
        let watched = |tick: usize, apart: bool| {
            let (p, mut u) = world(1000, &[], 400);
            u[3].buffs.push(format!("sed_timer1:w:{tick}"));
            let nexus = if apart { "tfm2_b2:2:1f7:0" } else { "tfm2_b2:2:80:0" };
            u.push(Unit { id: 0, name: "nexus".into(), kind: EntityKindV1::Nexus.code(), team: 0, pos: (5, 5),
                          hp: (5000, 5000), shield: 0, cc: 0, targetable: true, buffs: vec![nexus.into()] });
            if apart {
                u[0].pos.0 += 3;
            }
            Snapshot::new(tick, 0x77, p, u)
        };
        let w = |kind, thread| Origin { kind, match_id: 4156, set: if kind == VIEW { 1 } else { SimOriginV1::NONE },
                                        seed: 9, thread };
        let (p1, p2, v) = (w(PRESIM, 13), w(PRESIM, 18), w(VIEW, 25));
        let (mut lines, mut wt, mut most) = (Vec::new(), 0usize, (0usize, 0usize));
        for m in 0..800u64 {
            let o = Origin { kind: PRESIM, match_id: 10_000 + m, set: SimOriginV1::NONE, seed: m, thread: 30 };
            for k in 0..30 {
                assert!(store.record(o, background(m, if k == 0 { 1 } else { k * EVERY })).is_empty(), "unpaired: quiet");
            }
            // the watched match starts halfway, its names after 288 000 others
            if m >= 400 && m % 4 == 0 {
                let tick = if wt == 0 { 1 } else { wt * EVERY };
                for (o, view) in [(p1, false), (p2, false), (v, true)] {
                    lines.extend(store.record(o, watched(tick, view && wt >= 90)));
                }
                wt += 1;
            }
            let held = store.names_held();
            most = (most.0.max(held.0), most.1.max(held.1));
        }
        assert!(most.1 < 1 << 16, "never more slots than the old table had: {most:?}");
        assert!(store.kept_bytes() <= DETAIL_BUDGET, "{}", store.kept_bytes());
        store.check_names().unwrap();
        assert!(!lines.is_empty() && lines.iter().all(|l| !l.contains('?')), "{:?}", lines.iter().find(|l| l.contains('?')));
        assert!(lines.iter().any(|l| l.starts_with("SYNC [view m=4156 s=1 run 3 thr 25] t=1 ")
                                     && l.contains("c18#18 L3 g400 1000/1000 (18000,7) b1; c23#23")), "{lines:?}");
        let div = with(&lines, "DIVERGE");
        assert_eq!(div.len(), 2, "{div:?}");
        assert!(div[0].contains("first seen at tick 54000 (agreed at 53400); first differs between t 53400 and t 54000, \
                                 player 1 c18, other units: u18#18 champion (view run 3 vs presim run 1): pos (18003,7) vs \
                                 (18000,7) | also: nexus#0 nexus (view run 3 vs presim run 1): buffs only in view run 3: \
                                 [tfm2_b2:2:1f7:0]; buffs only in presim run 1: [tfm2_b2:2:80:0] | 2 rows differ: 1 \
                                 champion, 1 nexus"), "{}", div[0]);
    }

    /// 11-08: players and champions fill the first 1 + ALSO rows, and the one lead of the day - the nexus's third-party
    /// buffs - sat past them. The towers and nexuses not named yet are always appended.
    #[test]
    fn differing_structures_are_always_appended() {
        let three = |gold: usize, hp: usize, nexus: &str, tower: usize| {
            let players: Vec<Player> = (1..=3).map(|i| player(i, 17 + i, gold)).collect();
            let mut units: Vec<Unit> = (18..=20).map(|id| unit(id, EntityKindV1::Champion, hp, &[])).collect();
            units.push(Unit { id: 0, name: "nexus".into(), kind: EntityKindV1::Nexus.code(), team: 0, pos: (5, 5),
                              hp: (5000, 5000), shield: 0, cc: 0, targetable: true, buffs: vec![nexus.into()] });
            units.push(unit(40, EntityKindV1::Tower, tower, &[]));
            units.push(unit(300, EntityKindV1::Minion, 300, &[]));
            (players, units)
        };
        let snap = |(p, u): (Vec<Player>, Vec<Unit>), tick| Snapshot::new(tick, 3, p, u);
        let mut names = Names::default();
        let a = Rows::keep(&snap(three(400, 900, "tfm2_b2:2:1f7:0", 2900), 600), &mut names);
        let b = Rows::keep(&snap(three(410, 800, "tfm2_b2:2:80:0", 3000), 600), &mut names);
        let rows = differing_rows(&a, &b, &names, "view run 2", "presim run 1");
        assert_eq!(rows.iter().map(|r| r.0).collect::<Vec<_>>(),
                   vec!["player", "player", "player", "champion", "champion", "champion", "nexus", "tower"]);
        // through the store: the line names the first, ALSO more, then the structures not named yet
        let mut store = Store::default();
        let (p1, v) = (origin(PRESIM, SimOriginV1::NONE, 7), origin(VIEW, SET4, 1));
        store.record(p1, snap(three(400, 900, "tfm2_b2:2:80:0", 3000), 1));
        store.record(v, snap(three(400, 900, "tfm2_b2:2:80:0", 3000), 1));
        store.record(p1, snap(three(410, 800, "tfm2_b2:2:80:0", 3000), 600));
        let lines = store.record(v, snap(three(400, 900, "tfm2_b2:2:1f7:0", 2900), 600));
        let div = with(&lines, "DIVERGE");
        assert!(div[0].contains(" | structures: nexus#0 nexus (view run 2 vs presim run 1): buffs only in view run 2: \
                                 [tfm2_b2:2:1f7:0]; buffs only in presim run 1: [tfm2_b2:2:80:0]; u40#40 tower (view run 2 \
                                 vs presim run 1): hp 2900/1000 vs 3000/1000 | 8 rows differ: 3 player, 3 champion, 1 \
                                 nexus, 1 tower | "), "{}", div[0]);
        assert!(!div[0].contains("u20#20"), "the third champion is counted, not named: {}", div[0]);
        // a structure among the rows named already is not named twice
        let mut store = Store::default();
        store.record(p1, snap(three(400, 900, "tfm2_b2:2:80:0", 3000), 1));
        store.record(v, snap(three(400, 900, "tfm2_b2:2:80:0", 3000), 1));
        store.record(p1, snap(three(400, 900, "tfm2_b2:2:80:0", 3000), 600));
        let lines = store.record(v, snap(three(400, 900, "tfm2_b2:2:1f7:0", 3000), 600));
        let div = with(&lines, "DIVERGE");
        assert!(div[0].contains("(agreed at 1); first differs between t 1 and t 600, other units: nexus#0 nexus"), "{}", div[0]);
        assert!(!div[0].contains("structures:"), "{}", div[0]);
    }

    /// 11-08: EVERY (600 ticks) was all a DIVERGE line could say - the narrowest split (m=4160 s1) was "between 4200 and
    /// 4800". Each player's row hash every FINE ticks narrows it to 60 ticks and names whose rows.
    #[test]
    fn fine_records_bracket_the_first_difference_to_sixty_ticks() {
        let mut store = Store::default();
        let (p1, v) = (origin(PRESIM, SimOriginV1::NONE, 7), origin(VIEW, SET4, 1));
        // the view's champion #18 (player 1's) and a minion walk apart from tick 4320, are back by 5400; player 2's
        // champion #23 alone differs from 5700
        let state = |o: Origin, tick: usize| {
            let (p, mut u) = world(1000, &[], 400);
            if o == v && (4320..5400).contains(&tick) {
                u[0].pos.0 += 2;
                u[2].pos.1 += 1;
            }
            if o == v && tick >= 5700 {
                u[1].hp.0 -= 7;
            }
            Snapshot::new(tick, 5, p, u)
        };
        let mut lines = Vec::new();
        for o in [p1, v] {
            for tick in std::iter::once(1).chain((1..=110).map(|k| k * FINE)) {
                let s = state(o, tick);
                if tick == 1 || tick % EVERY == 0 {
                    lines.extend(store.record(o, s));
                } else {
                    store.fine(o, Fine::of(&s));
                }
            }
        }
        let div = with(&lines, "DIVERGE");
        assert_eq!(div.len(), 2, "{lines:?}");
        assert!(div[0].contains("first seen at tick 4800 (agreed at 4200); first differs between t 4260 and t 4320, player 1 \
                                 c18, other units: u18#18 champion"), "{}", div[0]);
        assert!(lines.iter().any(|l| l.starts_with("EQUAL") && l.contains("equal again at tick 5400")), "{lines:?}");
        assert!(div[1].contains("again at tick 6000 (equal again since 5400); first differs between t 5640 and t 5700, \
                                 player 2 c23: u23#23 champion"), "{}", div[1]);
        // what a snapshot keeps: the fine records since the one before, its own tick's last
        assert_eq!(store.fine_ticks(2636, 1, 600), (60..=600).step_by(60).collect::<Vec<u32>>());
        assert_eq!(store.fine_ticks(2636, 1, 1), vec![1]);
        // records waiting for a snapshot stay bounded; none for a run not seen yet or a tick its run has passed
        store.fine(Origin { thread: 99, ..p1 }, Fine::of(&state(p1, 60)));
        store.fine(p1, Fine::of(&state(p1, 6000)));
        let lone = origin(PRESIM, SimOriginV1::NONE, 50);
        let first = Snapshot { rng: 0xbad, ..state(lone, 1) };
        store.record(lone, first);
        // the hook makes them for runs with a partner only (a background presim never has one)
        assert!(store.paired(p1) && store.paired(v) && !store.paired(lone) && !store.paired(Origin { thread: 99, ..p1 }));
        for k in 1..100 {
            store.fine(lone, Fine::of(&state(lone, k * FINE)));
        }
        store.record(lone, Snapshot { rng: 0xbad, ..state(lone, 6000) });
        let kept = store.fine_ticks(2636, 3, 6000);
        assert_eq!(kept.len(), 2 * EVERY / FINE + 1, "{kept:?}");
        assert_eq!((kept[0], kept[kept.len() - 1]), (80 * FINE as u32, 6000), "the oldest went: {kept:?}");
        store.end(v, 6600, 4, 0, (0, 0));
        assert!(!store.paired(v), "an ended run makes no more");
        // the END line's kills: each team's players' (blue = team 0)
        let (mut p, _) = world(1000, &[], 400);
        p[0].kda[0] = 5;
        p[1].kda[0] = 3;
        assert_eq!(team_kills(&p), (3, 5), "player 2 is team 0 (blue)");
    }

    // ---- snapshot() through the stable API, on a fake simulation ----

    use std::ffi::c_void;
    use std::mem::{size_of, zeroed};

    #[derive(Clone)]
    struct FakeUnit {
        alive: bool,
        champion: bool,
        name: &'static str,
        hp: usize,
        buffs: Vec<&'static str>,
    }

    #[derive(Clone)]
    struct Fake {
        units: Vec<FakeUnit>,
        gold: usize,
    }

    unsafe fn fw<'a>(s: *const c_void) -> &'a Fake {
        &*(s as *const Fake)
    }
    unsafe fn fu<'a>(s: *const c_void, h: EntityHandleV1) -> Option<&'a FakeUnit> {
        fw(s).units.get(h.id()?)
    }
    unsafe extern "C" fn f_tick(_: *const c_void) -> usize {
        600
    }
    unsafe extern "C" fn f_count(s: *const c_void) -> usize {
        fw(s).units.len()
    }
    unsafe extern "C" fn f_at(s: *const c_void, i: usize) -> EntityHandleV1 {
        if i < fw(s).units.len() { EntityHandleV1::from_id(i) } else { EntityHandleV1::NULL }
    }
    unsafe extern "C" fn f_valid(s: *const c_void, h: EntityHandleV1) -> bool {
        fu(s, h).is_some()
    }
    unsafe extern "C" fn f_alive(s: *const c_void, h: EntityHandleV1) -> bool {
        fu(s, h).is_some_and(|u| u.alive)
    }
    unsafe extern "C" fn f_champion(s: *const c_void, h: EntityHandleV1) -> bool {
        fu(s, h).is_some_and(|u| u.champion)
    }
    unsafe extern "C" fn f_kind(s: *const c_void, h: EntityHandleV1) -> u32 {
        if fu(s, h).is_some_and(|u| u.champion) { EntityKindV1::Champion.code() } else { EntityKindV1::Minion.code() }
    }
    unsafe extern "C" fn f_hp(s: *const c_void, h: EntityHandleV1, cur: *mut usize, max: *mut usize) -> bool {
        let Some(u) = fu(s, h) else { return false };
        (*cur, *max) = (u.hp, 1000);
        true
    }
    unsafe extern "C" fn f_pos(_: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
        (*x, *y) = (h.id().unwrap_or(0) as u64 * 100, 5);
        true
    }
    unsafe extern "C" fn f_name(s: *const c_void, h: EntityHandleV1, buf: *mut u8, cap: usize, len: *mut usize) -> bool {
        let Some(u) = fu(s, h) else { return false };
        *len = u.name.len();
        if !buf.is_null() {
            std::ptr::copy_nonoverlapping(u.name.as_ptr(), buf, u.name.len().min(cap));
        }
        true
    }
    unsafe extern "C" fn f_buff_count(s: *const c_void, h: EntityHandleV1) -> usize {
        fu(s, h).map_or(0, |u| u.buffs.len())
    }
    unsafe extern "C" fn f_buff_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut BuffV1) -> bool {
        let Some(name) = fu(s, h).and_then(|u| u.buffs.get(i)) else { return false };
        *out = BuffV1::named(name);
        true
    }
    unsafe extern "C" fn f_stat(_: *const c_void, _: EntityHandleV1, out: *mut StatV1) -> bool {
        *out = StatV1 { attack: 77, move_speed: 345, ..Default::default() };
        true
    }
    unsafe extern "C" fn f_players(_: *const c_void) -> usize {
        1
    }
    unsafe extern "C" fn f_player_at(_: *const c_void, i: usize) -> PlayerHandleV1 {
        if i == 0 { PlayerHandleV1::from_id(4) } else { PlayerHandleV1::NULL }
    }
    unsafe extern "C" fn f_player_valid(_: *const c_void, h: PlayerHandleV1) -> bool {
        h.id() == Some(4)
    }
    unsafe extern "C" fn f_player_champion(_: *const c_void, _: PlayerHandleV1) -> EntityHandleV1 {
        EntityHandleV1::from_id(0)
    }
    unsafe extern "C" fn f_gold(s: *const c_void, _: PlayerHandleV1) -> usize {
        fw(s).gold
    }
    unsafe extern "C" fn f_level(_: *const c_void, _: PlayerHandleV1) -> usize {
        6
    }
    unsafe extern "C" fn f_respawn(_: *const c_void, _: PlayerHandleV1) -> usize {
        0
    }
    unsafe extern "C" fn f_palive(_: *const c_void, _: PlayerHandleV1) -> bool {
        true
    }
    unsafe extern "C" fn f_cds(_: *const c_void, _: PlayerHandleV1, a: *mut usize, q: *mut usize, w: *mut usize,
                               r: *mut usize) -> bool {
        (*a, *q, *w, *r) = (10, 20, 30, 40);
        true
    }
    unsafe extern "C" fn f_items(_: *const c_void, _: PlayerHandleV1) -> usize {
        2
    }
    unsafe extern "C" fn f_item_at(_: *const c_void, _: PlayerHandleV1, i: usize, buf: *mut u8, cap: usize,
                                   len: *mut usize) -> bool {
        let key = ["doran_blade", "boots"].get(i).copied().unwrap_or("");
        *len = key.len();
        if !buf.is_null() {
            std::ptr::copy_nonoverlapping(key.as_ptr(), buf, key.len().min(cap));
        }
        true
    }

    fn fake_snapshot(fake: &Fake) -> Snapshot {
        let mut vt: SimVtableV1 = unsafe { zeroed() };
        vt.size = size_of::<SimVtableV1>();
        vt.tick = Some(f_tick);
        vt.entity_count = Some(f_count);
        vt.entity_at = Some(f_at);
        vt.entity_is_valid = Some(f_valid);
        vt.entity_is_alive = Some(f_alive);
        vt.entity_is_champion = Some(f_champion);
        vt.entity_kind = Some(f_kind);
        vt.entity_hp = Some(f_hp);
        vt.entity_pos = Some(f_pos);
        vt.entity_name = Some(f_name);
        vt.entity_buff_count = Some(f_buff_count);
        vt.entity_buff_at = Some(f_buff_at);
        vt.entity_stat = Some(f_stat);
        vt.player_count = Some(f_players);
        vt.player_at = Some(f_player_at);
        vt.player_is_valid = Some(f_player_valid);
        vt.player_champion = Some(f_player_champion);
        vt.player_gold = Some(f_gold);
        vt.player_level = Some(f_level);
        vt.player_respawn_time = Some(f_respawn);
        vt.player_is_alive = Some(f_palive);
        vt.player_cooldowns = Some(f_cds);
        vt.player_item_count = Some(f_items);
        vt.player_item_key_at = Some(f_item_at);
        let mut ctx = SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(),
                                 state: fake as *const Fake as *mut c_void };
        let sim = unsafe { StableSim::from_raw(&mut ctx) }.unwrap();
        snapshot(&sim, 0x77)
    }

    #[test]
    fn a_snapshot_reads_gold_items_cooldowns_and_stats() {
        let fake = Fake {
            units: vec![FakeUnit { alive: true, champion: true, name: "league_zed", hp: 800,
                                   buffs: vec!["league_zed_mark", "league_azir_sim:4"] },
                        FakeUnit { alive: true, champion: false, name: "melee_minion", hp: 300, buffs: vec![] },
                        FakeUnit { alive: false, champion: false, name: "dead_minion", hp: 0, buffs: vec![] }],
            gold: 1234,
        };
        let s = fake_snapshot(&fake);
        assert_eq!((s.tick, s.rng, s.count), (600, 0x77, 2), "the dead minion is left out");
        assert_eq!(s.units[0].buffs, vec!["league_zed_mark".to_string()], "the simulation's tag is left out");
        assert_eq!(s.units[1].kind, EntityKindV1::Minion.code());
        let p = &s.players[0];
        assert_eq!((p.id, p.champ, p.name.as_str(), p.gold, p.level), (4, 0, "league_zed", 1234, 6));
        assert_eq!(p.cds, [10, 20, 30, 40]);
        assert_eq!(p.items, vec!["doran_blade".to_string(), "boots".to_string()]);
        assert_eq!((p.stat[0], p.stat[5]), (77, 345));
        // gold alone changes the hash
        let mut richer = fake.clone();
        richer.gold = 1235;
        assert_ne!(fake_snapshot(&richer).hash, s.hash);
        assert_eq!(fake_snapshot(&fake).hash, s.hash);
    }
}
