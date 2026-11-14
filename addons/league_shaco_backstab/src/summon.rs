//! 召唤物做成真的单位（试点，2026-11-14；用户看了「和英雄联盟不一样的地方」的清单后说「全改吧」，其中十几位英雄共同的
//! 一条是「召唤物不会走、不会打、打不掉」）：稳定 mod API 的 `spawn_unit`——「生成一个有时限的战斗单位，会追、会打附近的敌人」。
//! 这个文件是两个试点共用的部分：萨科的幻像（league_shaco_backstab）和安妮的提伯斯（league_annie_q 用 `#[path]` 引进来）。
//!
//! 游戏里还没跑过，所以这里的东西一半是为了让**一局**测试对局把话说清楚：
//!
//! - [`spawn`]：调 `spawn_unit`，返回的 id 当场核对（不是召唤者自己、读得到）。宿主没有这个槽、或者返回失败，都是 `None`
//!   ——调用的一方照旧放它原来「挂在目标身上」的那套。
//! - [`Unit`]：召唤者的被动每 tick 看一眼自己的单位（[`Unit::step`]）：还在不在（id 可能被别的单位重用，所以连名字、阵营、
//!   种类一起认）、在哪、多少血；每秒一行（走了多远、离召唤者多远、身边最近的敌人各是什么）；没了的那一 tick 给出
//!   [`End`]：被打死还是到时间、最后的位置、死的时候身边有谁、敌方玩家那一 tick 的金币 / 补刀 / 击杀涨了多少、击杀记录多没多。
//! - [`Wake`]：单位没了以后再看一小会儿：尸体留多久（引擎放不放 `dead` 动作）、之后几 tick 敌方的金币。
//! - [`Knobs`]：测试开关，加载时从日志旁边的 `<附加包>.cfg` 读一次（没有这个文件就是默认）：`unit=off` 不生成（回到原来的
//!   做法）、`still=1` 移速给 1（几乎不动：试「炮台」；不给 0，怕引擎拿它做除数）、`name=<名字>` 换一个单位名（试「名字是不是
//!   随便起」）。日志第一行会写读到了什么。
//! - 交接（[`handoff`]）：`spawn_unit` 在原生效果里调（别人的 mod 已经这样用过），效果没有自己的状态，就在召唤者身上挂一个
//!   几 tick 的 buff，名字末尾是单位 id，被动读到就接手。状态都在被动实例里，预演和画面各是各的。
//! - 好几个单位（第二轮，2026-11-14，[`Flock`]）：一个召唤者同时有几个单位时（雾行者、虚空蜂、狗群），被动里的一本有上限的账：
//!   要了几批、交接过来几个（一 tick 的交接一起取，[`take_handoffs`]）、活着的每 tick 看一眼，事情一件件交给调用的一方
//!   （[`Event`]）。上面这些单个单位的函数没改，两个试点照旧用。
//!
//! 引擎自己的召唤物（食尸鬼、熊、幻影）在 `EntityKindV1::Summon` 里；它们的图有 idle / run / attack / hit / dead 五个动作。

use mod_api_stable::*;

pub type Pt = (f64, f64);

/// Ticks between a unit's lines in the log (one a second).
pub const LINE_EVERY: usize = 60;
/// How far round the unit the log looks for enemies.
pub const NEAR: f64 = 90_000.0;
/// A unit gone this close to its time is "timed out", not "killed".
pub const TIME_SLACK: usize = 3;
/// Ticks a gone unit's wake is watched (its body, the purses).
pub const WAKE_TICKS: usize = 180;
/// Ticks after its end at which the enemy purses are read again.
pub const WAKE_PURSE: usize = 3;
/// Bytes of a name kept in a log line.
const NAME_SHOWN: usize = 28;

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

pub fn pt(p: Pt) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

pub fn at_of(e: &StableEntity<'_, '_>) -> Pt {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

fn short(name: &str) -> &str {
    let mut end = name.len().min(NAME_SHOWN);
    while end > 0 && !name.is_char_boundary(end) {
        end -= 1;
    }
    &name[..end]
}

// ===================== 测试开关 =====================

/// The test knobs of one add-on (see the module's notes). Read once at load: the same for every simulation.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Knobs {
    /// `unit=off`: never spawn (the add-on plays what it played before).
    pub off: bool,
    /// `still=1`: the unit's move speed is 1 (all but stationary).
    pub still: bool,
    /// `name=<unit name>`: spawn under this name instead.
    pub name: Option<String>,
}

impl Knobs {
    /// `key=value` lines; `#` starts a comment; anything else is ignored.
    pub fn parse(text: &str) -> Knobs {
        let mut k = Knobs::default();
        for line in text.lines() {
            let line = line.split('#').next().unwrap_or("").trim();
            let Some((key, value)) = line.split_once('=') else { continue };
            let (key, value) = (key.trim().to_ascii_lowercase(), value.trim());
            let on = matches!(value.to_ascii_lowercase().as_str(), "1" | "on" | "yes" | "true");
            match key.as_str() {
                "unit" => k.off = matches!(value.to_ascii_lowercase().as_str(), "off" | "0" | "no" | "false"),
                "still" => k.still = on,
                "name" => k.name = unit_name(value),
                _ => {}
            }
        }
        k
    }

    /// The file's knobs, or the defaults when it is not there.
    pub fn read(path: &std::path::Path) -> Knobs {
        match std::fs::read(path) {
            // a file somebody left: 4 KiB of it is plenty
            Ok(bytes) => Knobs::parse(&String::from_utf8_lossy(&bytes[..bytes.len().min(4096)])),
            Err(_) => Knobs::default(),
        }
    }

    pub fn shown(&self) -> String {
        if *self == Knobs::default() {
            return "none".to_string();
        }
        let mut v = Vec::new();
        if self.off {
            v.push("unit=off (no unit is spawned)".to_string());
        }
        if self.still {
            v.push("still=1 (move speed 1)".to_string());
        }
        if let Some(n) = &self.name {
            v.push(format!("name={n}"));
        }
        v.join(", ")
    }
}

/// A unit name a knob may give: letters, digits and `_`, 1 to 48 of them.
pub fn unit_name(s: &str) -> Option<String> {
    (!s.is_empty() && s.len() <= 48 && s.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'_')).then(|| s.to_string())
}

// ===================== 生成 =====================

/// What a unit of ours is to be.
#[derive(Clone, Debug)]
pub struct Spec {
    pub name: String,
    /// Ticks it lives.
    pub life: usize,
    pub stat: StatV1,
    pub attack: UnitAttackV1,
}

impl Spec {
    /// The knobs applied: another name, a move speed of 1.
    pub fn with(mut self, knobs: &Knobs) -> Spec {
        if let Some(n) = &knobs.name {
            self.name = n.clone();
        }
        if knobs.still {
            self.stat.move_speed = 1;
        }
        self
    }

    pub fn shown(&self) -> String {
        let (s, a) = (&self.stat, &self.attack);
        format!("'{}' for {} ticks, attack {} ap {} hp {} def {} mr {} speed {}; hits {} + {}% of its attack, range {}, every {} \
                 ticks ({} long, lands at {})",
                self.name, self.life, s.attack, s.magic_power, s.hp, s.defence, s.magic_resistance, s.move_speed, a.attack,
                a.attack_ratio, a.range, a.cooltime, a.duration, a.start_timing)
    }
}

/// `spawn_unit` for `summoner` at `at`: the new unit's id. `None` when the host has no such slot or refuses (or hands
/// back the summoner himself). Whether the id reads as a unit is for [`Unit::look`] a tick later: the host may add it
/// only when the tick ends.
pub fn spawn(sim: &mut StableSim<'_>, summoner: usize, team: usize, at: Pt, spec: &Spec) -> Option<usize> {
    let (x, y) = (at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64);
    let id = sim.spawn_unit(&spec.name, summoner, team, x, y, spec.life as u64, &spec.stat, &spec.attack)?;
    (id != summoner).then_some(id)
}

/// The box round every entity the simulation holds now, ((least x, least y), (most x, most y)): ground the engine
/// itself keeps units on. `None` with no entity.
pub fn field(sim: &StableSim<'_>) -> Option<(Pt, Pt)> {
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).map(|e| at_of(&e)).fold(None, |b: Option<(Pt, Pt)>, p| {
        Some(match b {
            None => (p, p),
            Some((lo, hi)) => ((lo.0.min(p.0), lo.1.min(p.1)), (hi.0.max(p.0), hi.1.max(p.1))),
        })
    })
}

/// `at` moved into `field` (with none: only never off the top or left edge). A spawn point worked out sideways from
/// somebody can lie off the map's grid; what the engine does with a unit out there is not known, so none is asked
/// for. The walls inside the field are not known here.
pub fn inside(field: Option<(Pt, Pt)>, at: Pt) -> Pt {
    let at = (at.0.max(0.0), at.1.max(0.0));
    match field {
        Some((lo, hi)) => (at.0.max(lo.0).min(hi.0), at.1.max(lo.1).min(hi.1)),
        None => at,
    }
}

/// The name of the short buff on the summoner that hands a new unit's id to his passive.
pub fn handoff(prefix: &str, id: usize) -> String {
    format!("{prefix}:{id}")
}

pub fn parse_handoff(prefix: &str, name: &str) -> Option<usize> {
    name.strip_prefix(prefix)?.strip_prefix(':')?.parse().ok()
}

/// The handed-over unit id on `me`, taken off him.
pub fn take_handoff(sim: &mut StableSim<'_>, me: usize, prefix: &str) -> Option<usize> {
    let (name, id) = {
        let e = sim.get_entity(me)?;
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find_map(|b| Some((b.name().to_string(), parse_handoff(prefix, b.name())?)))?
    };
    sim.entity_remove_buff(me, &name);
    Some(id)
}

pub fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

// ===================== 身边有谁、敌方的钱 =====================

pub fn kind_name(kind: Option<EntityKindV1>, champion: bool, minion: bool, tower: bool) -> &'static str {
    match kind {
        Some(EntityKindV1::Champion) => "champion",
        Some(EntityKindV1::Minion) => "minion",
        Some(EntityKindV1::Jungle) => "jungle",
        Some(EntityKindV1::Epic) => "epic",
        Some(EntityKindV1::Serpen) => "serpen",
        Some(EntityKindV1::Tower) => "tower",
        Some(EntityKindV1::Nexus) => "nexus",
        Some(EntityKindV1::Summon) => "summon",
        None if champion => "champion",
        None if minion => "minion",
        None if tower => "tower",
        None => "unit",
    }
}

fn kind_of(e: &StableEntity<'_, '_>) -> &'static str {
    kind_name(e.kind(), e.is_champion(), e.is_minion(), e.is_tower())
}

/// Something an enemy of ours can be hit by: no tower, no nexus.
pub fn hittable(e: &StableEntity<'_, '_>) -> bool {
    !e.is_tower() && !matches!(e.kind(), Some(EntityKindV1::Tower | EntityKindV1::Nexus))
}

/// An enemy near one of our units.
#[derive(Clone, Debug, PartialEq)]
pub struct Near {
    pub id: usize,
    pub name: String,
    pub kind: &'static str,
    pub d: f64,
    pub hp: usize,
}

/// The living enemies of `team` within `reach` of `at`, nearest first.
pub fn foes_near(sim: &StableSim<'_>, team: usize, at: Pt, reach: f64) -> Vec<Near> {
    let mut v: Vec<Near> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive())
        .filter_map(|u| {
            let d = dist(at_of(&u), at);
            (d <= reach).then(|| Near { id: u.id(), name: u.name().unwrap_or_default(), kind: kind_of(&u), d, hp: u.hp().0 })
        })
        .collect();
    v.sort_by(|a, b| a.d.total_cmp(&b.d));
    v
}

/// The nearest of each kind, at most `most` of them: `champion #7 league_garen 9000 away hp 812`.
pub fn near_text(foes: &[Near], most: usize) -> String {
    let mut kinds: Vec<&'static str> = Vec::new();
    let mut out = Vec::new();
    for f in foes {
        if kinds.contains(&f.kind) {
            continue;
        }
        kinds.push(f.kind);
        out.push(format!("{} #{} {} {:.0} away hp {}", f.kind, f.id, short(&f.name), f.d, f.hp));
        if out.len() >= most {
            break;
        }
    }
    if out.is_empty() { "nobody".to_string() } else { out.join("; ") }
}

/// One enemy player's counters.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Purse {
    pub player: usize,
    pub gold: usize,
    pub cs: usize,
    pub kills: usize,
}

/// The players not of `team` (ten players a match; 16 kept at most).
pub fn purses(sim: &StableSim<'_>, team: usize) -> Vec<Purse> {
    (0..sim.player_count().min(32)).filter_map(|i| sim.player_at(i))
        .filter(|p| p.team() != team)
        .map(|p| Purse { player: p.id(), gold: p.gold(), cs: p.cs(), kills: p.kills() })
        .take(16)
        .collect()
}

/// What the enemy players gained from `before` to `after`: `p7 gold +37 cs +1; p8 gold +2`, or `nothing`.
pub fn purse_gain(before: &[Purse], after: &[Purse]) -> String {
    let mut out = Vec::new();
    for a in after {
        let Some(b) = before.iter().find(|b| b.player == a.player) else { continue };
        let (g, c, k) = (a.gold as i64 - b.gold as i64, a.cs as i64 - b.cs as i64, a.kills as i64 - b.kills as i64);
        if g == 0 && c == 0 && k == 0 {
            continue;
        }
        let mut s = format!("p{}", a.player);
        if g != 0 {
            s += &format!(" gold {g:+}");
        }
        if c != 0 {
            s += &format!(" cs {c:+}");
        }
        if k != 0 {
            s += &format!(" kills {k:+}");
        }
        out.push(s);
    }
    if out.is_empty() { "nothing".to_string() } else { out.join("; ") }
}

// ===================== 一个活着的单位 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Fate {
    /// Gone before its time.
    Killed,
    /// Gone at its time.
    TimedOut,
}

/// A unit's end: when its summoner's passive saw it gone.
#[derive(Clone, Debug)]
pub struct End {
    pub fate: Fate,
    /// Where it last stood.
    pub at: Pt,
    /// Ticks it lived.
    pub age: usize,
    /// A dead body is still readable under its id (the engine may be playing its death).
    pub body: bool,
    /// The log line's body.
    pub text: String,
}

pub enum Step {
    /// Still there; a line for the log once a second.
    Alive(Option<String>),
    Over(End),
}

/// One unit of ours, as its summoner's passive knows it.
#[derive(Clone, Debug)]
pub struct Unit {
    pub id: usize,
    /// Which of this passive's units (for the log).
    pub n: usize,
    /// The tick it was spawned.
    pub born: usize,
    /// The ticks asked for.
    pub life: usize,
    /// Its summoner's team: whose enemies are its enemies.
    pub team: usize,
    /// What its team, name and kind read back as when first looked at: how it is told from whatever may get its id
    /// afterwards.
    pub own_team: usize,
    pub name: String,
    pub kind: Option<EntityKindV1>,
    pub at: Pt,
    pub hp: usize,
    pub max: usize,
    /// The lowest health seen.
    pub low: usize,
    line_tick: usize,
    line_at: Pt,
    line_hp: usize,
    walked: f64,
    purse: Vec<Purse>,
    purse_before: Vec<Purse>,
    kill_log: usize,
    /// Its summoner's player and his damage statistic: at the first look, at the last line.
    player: usize,
    deal_first: Option<u64>,
    deal_line: Option<u64>,
}

impl Unit {
    /// The first look at unit `id` of `player`'s champion, spawned at tick `born` for `life` ticks: the unit and its
    /// line, or why it is none.
    pub fn look(sim: &StableSim<'_>, id: usize, n: usize, born: usize, life: usize, team: usize, player: usize)
                -> Result<(Unit, String), String> {
        let Some(e) = sim.get_entity(id) else { return Err(format!("#{id} is no entity")) };
        if !e.is_alive() {
            return Err(format!("#{id} is not alive"));
        }
        let (name, kind, at, (hp, max), stat) = (e.name().unwrap_or_default(), e.kind(), at_of(&e), e.hp(), e.stat());
        let own_team = e.team();
        let line = format!(
            "#{id} reads back as name '{}' kind {} team {own_team}{} champion={} minion={} targetable={} radius {} at {} hp \
             {hp}/{max} attack {} def {} mr {} speed {} attack interval {} buffs {}",
            short(&name), kind_of(&e), if own_team == team { String::new() } else { format!(" (asked for {team})") },
            e.is_champion(), e.is_minion(), e.is_targetable(), e.radius(), pt(at), stat.attack, stat.defence,
            stat.magic_resistance, stat.move_speed, e.attack_interval(), e.buff_count());
        let (purse, deal) = (purses(sim, team), deal_stat(sim, player));
        Ok((Unit { id, n, born, life, team, own_team, name, kind, at, hp, max, low: hp, line_tick: sim.tick(), line_at: at,
                   line_hp: hp, walked: 0.0, purse_before: purse.clone(), purse, kill_log: sim.kill_log_count(), player,
                   deal_first: deal, deal_line: deal }, line))
    }

    /// Its summoner has just set its health (the lines count from there).
    pub fn health_set(&mut self, hp: usize) {
        (self.hp, self.low, self.line_hp) = (hp, hp, hp);
    }

    /// Ticks since it was spawned.
    pub fn age(&self, tick: usize) -> usize {
        tick.saturating_sub(self.born)
    }

    /// Ticks it has left.
    pub fn left(&self, tick: usize) -> usize {
        (self.born + self.life).saturating_sub(tick)
    }

    /// Is the entity under its id still this unit, alive?
    fn there(&self, e: &StableEntity<'_, '_>) -> bool {
        e.is_alive() && self.same(e)
    }

    /// The entity under its id is this unit (alive or its body), not another that got the id.
    fn same(&self, e: &StableEntity<'_, '_>) -> bool {
        e.team() == self.own_team && e.kind() == self.kind && e.name().unwrap_or_default() == self.name
    }

    /// This tick's look. `summoner`: where its summoner stands, for the line.
    pub fn step(&mut self, sim: &StableSim<'_>, summoner: Option<Pt>) -> Step {
        let tick = sim.tick();
        let seen = sim.get_entity(self.id).map(|e| (self.there(&e), e.is_alive(), at_of(&e), e.hp()));
        if let Some((true, _, at, (hp, max))) = seen {
            self.walked += dist(at, self.at);
            (self.at, self.hp, self.max, self.low) = (at, hp, max, self.low.min(hp));
            self.purse_before = std::mem::replace(&mut self.purse, purses(sim, self.team));
            self.kill_log = sim.kill_log_count();
            if tick < self.line_tick + LINE_EVERY {
                return Step::Alive(None);
            }
            let foes = foes_near(sim, self.team, at, NEAR);
            let deal = deal_stat(sim, self.player);
            let line = format!(
                "{} of {} ticks, at {} (walked {:.0}, {:.0} from where it stood a second ago), hp {hp}/{max} ({:+} in the second){}; \
                 near it: {}; its summoner's damage statistic {}",
                self.age(tick), self.life, pt(at), self.walked, dist(at, self.line_at), hp as i64 - self.line_hp as i64,
                summoner.map(|s| format!(", {:.0} from its summoner", dist(s, at))).unwrap_or_default(), near_text(&foes, 4),
                gain_text(self.deal_line, deal, "in the second"));
            (self.line_tick, self.line_at, self.line_hp, self.walked, self.deal_line) = (tick, at, hp, 0.0, deal);
            return Step::Alive(Some(line));
        }
        // gone: no entity under the id, a dead one (its body), or another unit that got the id
        let body = matches!(seen, Some((false, false, _, _))) && sim.get_entity(self.id).is_some_and(|e| self.same(&e));
        let fate = if tick + TIME_SLACK >= self.born + self.life { Fate::TimedOut } else { Fate::Killed };
        let foes = foes_near(sim, self.team, self.at, NEAR);
        let kills = sim.kill_log_count().saturating_sub(self.kill_log);
        let text = format!(
            "{} after {} of {} ticks at {}, last seen with hp {}/{} (lowest {}); {}; near it: {}; the enemy players in its last \
             tick: {}; kill log {:+}; its summoner's damage statistic {}",
            match fate { Fate::Killed => "KILLED", Fate::TimedOut => "TIMED OUT" }, self.age(tick), self.life, pt(self.at), self.hp,
            self.max, self.low,
            match seen {
                None => "no entity under its id any more",
                Some(_) if body => "its dead body is still there",
                Some(_) => "another unit has its id",
            },
            near_text(&foes, 5), purse_gain(&self.purse_before, &purses(sim, self.team)), kills,
            gain_text(self.deal_first, deal_stat(sim, self.player), "over its life"));
        Step::Over(End { fate, at: self.at, age: self.age(tick), body, text })
    }

    /// A hook of its summoner's passive (on_attack, on_kill, on_unit_kill) fired while it is out: whom the engine names
    /// as the one who did it, to whom, and how far the unit and its summoner stand from that one - which of the two
    /// it was, when the engine names the summoner for both.
    pub fn hook_text(&self, sim: &StableSim<'_>, entity: usize, other: usize, summoner: usize) -> String {
        let who = if entity == self.id {
            "the unit itself"
        } else if entity == summoner {
            "its summoner"
        } else {
            "neither of the two"
        };
        let from = sim.get_entity(summoner).map(|e| at_of(&e));
        match sim.get_entity(other).map(|e| (e.name().unwrap_or_default(), kind_of(&e), at_of(&e))) {
            Some((name, kind, at)) => format!(
                "entity #{entity} ({who}) -> {kind} #{other} {}, {:.0} from the unit{}", short(&name), dist(at, self.at),
                from.map(|f| format!(", {:.0} from its summoner", dist(at, f))).unwrap_or_default()),
            None => format!("entity #{entity} ({who}) -> #{other} (no entity)"),
        }
    }

    /// What to watch once it is gone.
    pub fn wake(&self, sim: &StableSim<'_>, end: &End) -> Wake {
        Wake { id: self.id, n: self.n, ended: sim.tick(), team: self.team, own_team: self.own_team, name: self.name.clone(),
               body: end.body, purse: self.purse_before.clone(), purse_told: false }
    }
}

/// A gone unit watched a little longer: how long its body stays, what the enemy players got for it.
#[derive(Clone, Debug)]
pub struct Wake {
    pub id: usize,
    pub n: usize,
    pub ended: usize,
    team: usize,
    own_team: usize,
    name: String,
    body: bool,
    purse: Vec<Purse>,
    purse_told: bool,
}

impl Wake {
    /// This tick's lines (at most two in all), and whether the watch is over.
    pub fn step(&mut self, sim: &StableSim<'_>) -> (Vec<String>, bool) {
        let since = sim.tick().saturating_sub(self.ended);
        let mut lines = Vec::new();
        if self.body {
            let still = sim.get_entity(self.id).is_some_and(|e| {
                !e.is_alive() && e.team() == self.own_team && e.name().unwrap_or_default() == self.name
            });
            if !still {
                self.body = false;
                lines.push(format!("its body was there for {since} ticks after its end"));
            }
        }
        if !self.purse_told && since >= WAKE_PURSE {
            self.purse_told = true;
            lines.push(format!("the enemy players from the tick before its end to {since} ticks after: {}",
                               purse_gain(&self.purse, &purses(sim, self.team))));
        }
        let over = since >= WAKE_TICKS || (self.purse_told && !self.body);
        if over && self.body {
            lines.push(format!("its body is still there {since} ticks after its end (not watched further)"));
        }
        (lines, over)
    }
}

/// A player's damage-dealt statistic (`deal` of his statistics document), when the host tells it. It rising while
/// only a unit of his fights says the unit's damage counts as its summoner's.
pub fn deal_stat(sim: &StableSim<'_>, player: usize) -> Option<u64> {
    number(&sim.get_player(player)?.statistics_json("deal")?)
}

/// A JSON number (a statistic read by its path) as a whole number.
pub fn number(text: &str) -> Option<u64> {
    let v = text.trim().trim_matches('"').parse::<f64>().ok()?;
    (v.is_finite() && v >= 0.0).then_some(v as u64)
}

fn gain_text(before: Option<u64>, now: Option<u64>, over: &str) -> String {
    match (before, now) {
        (Some(b), Some(n)) => format!("{:+} {over} (now {n})", n as i64 - b as i64),
        (None, Some(n)) => format!("now {n}"),
        _ => "not readable".to_string(),
    }
}

// ===================== 一个召唤者的好几个单位（第二轮，2026-11-14） =====================
//
// 用户：「召唤物的全做啊 剩下的一批英雄也做了啊」。约里克的雾行者和迷雾少女、玛尔扎哈的虚空蜂、纳亚菲利的狗群……一个召唤者
// 同时有好几个单位。[`Flock`] 是被动里记这些单位的一本账，每样都有上限：要了还没来的（[`Flock::ask`]，等原生效果交接）、
// 交接过来还没读成单位的、活着的、没了以后再看一会儿的（[`Wake`]）。被动每 tick 调一次 [`Flock::tick`]，它返回这一 tick
// 发生的事（[`Event`]）；写日志、给单位穿衣服（buff、生命）、它没了以后做什么，都由调用的一方做。上面那些单个单位的函数
// 一个字没改：萨科的幻像和安妮的提伯斯照旧用它们。

/// Ticks a flock waits for an ask's handoff, and looks a handed-over unit gets to read as one (the pilots' ASK_WAIT and
/// LOOK_TRIES).
pub const FLOCK_WAIT: usize = 4;
pub const FLOCK_LOOKS: usize = 5;
/// Asks kept waiting at once, and gone units whose wake is watched at once (the oldest goes first).
pub const FLOCK_ASKS: usize = 8;
pub const FLOCK_WAKES: usize = 8;

/// Every handed-over unit id on `me` (units spawned in one go each lay their own `<prefix>:<id>`), taken off him; at
/// most `most` of them kept (the rest are taken off too).
pub fn take_handoffs(sim: &mut StableSim<'_>, me: usize, prefix: &str, most: usize) -> Vec<usize> {
    let found: Vec<(String, usize)> = match sim.get_entity(me) {
        Some(e) => (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .filter_map(|b| Some((b.name().to_string(), parse_handoff(prefix, b.name())?)))
            .collect(),
        None => return Vec::new(),
    };
    let mut ids = Vec::new();
    for (name, id) in found {
        sim.entity_remove_buff(me, &name);
        if !ids.contains(&id) && ids.len() < most {
            ids.push(id);
        }
    }
    ids
}

/// `n` points `r` round `at`, evenly spaced, the first `first` radians round from the east (x right, y down the screen).
pub fn spread(at: Pt, r: f64, n: usize, first: f64) -> Vec<Pt> {
    (0..n).map(|k| {
        let a = first + k as f64 * std::f64::consts::TAU / n.max(1) as f64;
        (at.0 + r * a.cos(), at.1 + r * a.sin())
    }).collect()
}

/// One unit of a flock: summon.rs's watch on it and what the caller keeps with it.
#[derive(Clone, Debug)]
pub struct Member<T> {
    pub unit: Unit,
    /// Given with its ask; the caller may change it at will.
    pub extra: T,
}

/// What became of a flock's units in a tick, in this order: the asks given up, the handed-over looked at, the living
/// stepped, the wakes watched.
#[derive(Debug)]
pub enum Event<T> {
    /// No unit came within `FLOCK_WAIT` ticks of the ask made at tick `asked`.
    NoUnit { asked: usize, what: T },
    /// Unit `id` read as one and is on the books now (`line`: what it read back as): the caller dresses it. Its stepping
    /// starts next tick.
    Look { id: usize, n: usize, line: String },
    /// The id a handoff named never read as a unit in `FLOCK_LOOKS` ticks.
    Lost { id: usize, why: String, what: T },
    /// A living unit's line, once a second.
    Line { id: usize, n: usize, line: String },
    /// A unit gone - killed or timed out (`end`), off the books; its wake is watched.
    Over { member: Member<T>, end: End },
    /// A unit let go to keep the books under the cap: still out there, no longer watched (nothing ends it early).
    LetGo { member: Member<T> },
    /// A line about a gone unit's body or the enemy purses after it.
    Wake { n: usize, line: String },
}

#[derive(Clone, Debug)]
struct FlockAsk<T> {
    tick: usize,
    life: usize,
    what: T,
}

#[derive(Clone, Debug)]
struct FlockFresh<T> {
    id: usize,
    born: usize,
    life: usize,
    tries: usize,
    what: T,
}

/// Several units of one summoner, as his passive keeps them (state of the passive instance: the presims and the match
/// on screen each have their own).
#[derive(Clone, Debug)]
pub struct Flock<T> {
    /// The handoff buffs' prefix: `<prefix>:<unit id>` on the summoner.
    pub prefix: String,
    /// Most units on the books at once (handed over or alive); more read as units let the oldest go.
    pub cap: usize,
    /// The ticks a unit lives when a handoff comes with no ask waiting (one spawned by the passive itself).
    pub life: usize,
    asks: Vec<FlockAsk<T>>,
    fresh: Vec<FlockFresh<T>>,
    /// The living units, oldest first.
    pub live: Vec<Member<T>>,
    wakes: Vec<Wake>,
    /// Units read as one so far: the last one's `n`.
    pub count: usize,
}

impl<T: Clone + Default> Flock<T> {
    pub fn new(prefix: &str, cap: usize, life: usize) -> Flock<T> {
        Flock { prefix: prefix.to_string(), cap: cap.max(1), life, asks: Vec::new(), fresh: Vec::new(), live: Vec::new(),
                wakes: Vec::new(), count: 0 }
    }

    /// Units are on their way: a native effect that spawns them and lays their handoffs is queued (or has run) now.
    /// Each unit it brings gets `life` (the ticks asked for: when it times out) and a copy of `what`.
    pub fn ask(&mut self, tick: usize, life: usize, what: T) {
        if self.asks.len() >= FLOCK_ASKS {
            self.asks.remove(0);
        }
        self.asks.push(FlockAsk { tick, life, what });
    }

    /// Asks still waiting for their units.
    pub fn waiting(&self) -> usize {
        self.asks.len()
    }

    /// Units on the books: handed over or alive.
    pub fn out(&self) -> usize {
        self.fresh.len() + self.live.len()
    }

    /// Units that still fit under the cap (the waiting asks not counted: the caller knows what each brings).
    pub fn room(&self) -> usize {
        self.cap.saturating_sub(self.out())
    }

    /// Nothing asked, handed over, alive or watched.
    pub fn is_empty(&self) -> bool {
        self.asks.is_empty() && self.fresh.is_empty() && self.live.is_empty() && self.wakes.is_empty()
    }

    pub fn get(&self, id: usize) -> Option<&Member<T>> {
        self.live.iter().find(|m| m.unit.id == id)
    }

    pub fn get_mut(&mut self, id: usize) -> Option<&mut Member<T>> {
        self.live.iter_mut().find(|m| m.unit.id == id)
    }

    /// The living units' ids, oldest first.
    pub fn ids(&self) -> Vec<usize> {
        self.live.iter().map(|m| m.unit.id).collect()
    }

    /// This tick's look at the flock (see [`Event`]). The handoffs on `me` are taken: all of one tick go to the oldest
    /// waiting ask (one native effect spawned them). `team` / `player`: the summoner's; `summoner`: where he stands.
    pub fn tick(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, player: usize, summoner: Option<Pt>) -> Vec<Event<T>> {
        let now = sim.tick();
        let mut ev = Vec::new();
        let ids = take_handoffs(sim, me, &self.prefix, self.cap * 2);
        if !ids.is_empty() {
            let (born, life, what) = if self.asks.is_empty() {
                (now, self.life, T::default())
            } else {
                let a = self.asks.remove(0);
                (a.tick, a.life, a.what)
            };
            for id in ids {
                // a unit's id is given once by the host; one already on the books is not taken twice
                if self.fresh.iter().any(|f| f.id == id) || self.get(id).is_some() {
                    continue;
                }
                if self.fresh.len() >= self.cap * 2 {
                    break;
                }
                self.fresh.push(FlockFresh { id, born, life, tries: 0, what: what.clone() });
            }
        }
        let mut i = 0;
        while i < self.asks.len() {
            if now > self.asks[i].tick + FLOCK_WAIT {
                let a = self.asks.remove(i);
                ev.push(Event::NoUnit { asked: a.tick, what: a.what });
            } else {
                i += 1;
            }
        }
        let mut looked = Vec::new();
        for mut f in std::mem::take(&mut self.fresh) {
            match Unit::look(sim, f.id, self.count + 1, f.born, f.life, team, player) {
                Ok((unit, line)) => {
                    self.count += 1;
                    if self.live.len() >= self.cap {
                        let member = self.live.remove(0);
                        ev.push(Event::LetGo { member });
                    }
                    ev.push(Event::Look { id: f.id, n: unit.n, line });
                    looked.push(f.id);
                    self.live.push(Member { unit, extra: f.what });
                }
                Err(why) if f.tries + 1 >= FLOCK_LOOKS => ev.push(Event::Lost { id: f.id, why, what: f.what }),
                Err(_) => {
                    f.tries += 1;
                    self.fresh.push(f);
                }
            }
        }
        let mut i = 0;
        while i < self.live.len() {
            if looked.contains(&self.live[i].unit.id) {
                i += 1;
                continue;
            }
            let (id, n) = (self.live[i].unit.id, self.live[i].unit.n);
            match self.live[i].unit.step(sim, summoner) {
                Step::Alive(line) => {
                    if let Some(line) = line {
                        ev.push(Event::Line { id, n, line });
                    }
                    i += 1;
                }
                Step::Over(end) => {
                    let member = self.live.remove(i);
                    if self.wakes.len() >= FLOCK_WAKES {
                        self.wakes.remove(0);
                    }
                    self.wakes.push(member.unit.wake(sim, &end));
                    ev.push(Event::Over { member, end });
                }
            }
        }
        let mut wakes = std::mem::take(&mut self.wakes);
        wakes.retain_mut(|w| {
            let (lines, over) = w.step(sim);
            ev.extend(lines.into_iter().map(|line| Event::Wake { n: w.n, line }));
            !over
        });
        self.wakes = wakes;
        ev
    }

    /// Everything off the books at once (the summoner died, or a new life of his began): the living, for the caller to
    /// see to; the asks, the handed-over and the wakes are dropped.
    pub fn orphans(&mut self) -> Vec<Member<T>> {
        self.asks.clear();
        self.fresh.clear();
        self.wakes.clear();
        std::mem::take(&mut self.live)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_spawn_point_stays_in_the_field() {
        let field = Some(((100.0, 200.0), (900.0, 800.0)));
        assert_eq!(inside(field, (500.0, 500.0)), (500.0, 500.0));
        assert_eq!(inside(field, (50.0, 900.0)), (100.0, 800.0));
        assert_eq!(inside(field, (1_000.0, 100.0)), (900.0, 200.0));
        assert_eq!(inside(field, (-5.0, f64::NAN)), (100.0, 200.0));
        // a field of one point; no field at all: only the top and left edges
        assert_eq!(inside(Some(((7.0, 9.0), (7.0, 9.0))), (500.0, -3.0)), (7.0, 9.0));
        assert_eq!(inside(None, (-5.0, 12.0)), (0.0, 12.0));
    }

    #[test]
    fn the_knobs_are_off_unless_the_file_says_so() {
        assert_eq!(Knobs::parse(""), Knobs::default());
        assert_eq!(Knobs::default().shown(), "none");
        let k = Knobs::parse("# test\r\nunit = off\r\nstill=1 # a turret\nname=ghoul\nwhatever\nother=3\n");
        assert_eq!(k, Knobs { off: true, still: true, name: Some("ghoul".into()) });
        assert!(k.shown().contains("unit=off") && k.shown().contains("still=1") && k.shown().contains("name=ghoul"));
        assert_eq!(Knobs::parse("unit=on\nstill=0\nname=\n"), Knobs::default());
        // a name is letters, digits and _ only: nothing else reaches spawn_unit
        assert_eq!(Knobs::parse("name=../x").name, None);
        assert_eq!(Knobs::parse("name=a b").name, None);
        assert_eq!(unit_name(&"a".repeat(49)), None);
        assert_eq!(unit_name("league_shaco").as_deref(), Some("league_shaco"));
        assert_eq!(Knobs::read(std::path::Path::new("no such folder/no such file.cfg")), Knobs::default());
    }

    #[test]
    fn a_knob_changes_the_spec() {
        let spec = Spec { name: "league_shaco".into(), life: 312, stat: StatV1 { move_speed: 1100, hp: 900, ..Default::default() },
                          attack: UnitAttackV1::default() };
        let same = spec.clone().with(&Knobs::default());
        assert_eq!((same.name.as_str(), same.stat.move_speed), ("league_shaco", 1100));
        let turned = spec.with(&Knobs { off: false, still: true, name: Some("ghoul".into()) });
        assert_eq!((turned.name.as_str(), turned.stat.move_speed, turned.stat.hp), ("ghoul", 1, 900));
        assert!(turned.shown().starts_with("'ghoul' for 312 ticks"));
    }

    #[test]
    fn the_handoff_carries_the_unit_id() {
        let name = handoff("league_shaco_r_uid", 1234);
        assert_eq!(name, "league_shaco_r_uid:1234");
        assert!(name.len() < BUFF_NAME_CAP);
        assert_eq!(parse_handoff("league_shaco_r_uid", &name), Some(1234));
        assert_eq!(parse_handoff("league_shaco_r_uid", "league_shaco_r_uid"), None);
        assert_eq!(parse_handoff("league_shaco_r_uid", "league_shaco_r_uid:x"), None);
        assert_eq!(parse_handoff("league_shaco_r_uid", "league_shaco_r_unit"), None);
        assert_eq!(parse_handoff("league_shaco_r_uid", "league_shaco_r_uid_more:7"), None);
    }

    #[test]
    fn the_purses_tell_what_a_kill_paid() {
        let before = [Purse { player: 5, gold: 1000, cs: 30, kills: 1 }, Purse { player: 6, gold: 500, cs: 10, kills: 0 }];
        assert_eq!(purse_gain(&before, &before), "nothing");
        let after = [Purse { player: 5, gold: 1037, cs: 31, kills: 1 }, Purse { player: 6, gold: 502, cs: 10, kills: 1 },
                     Purse { player: 9, gold: 1, cs: 1, kills: 1 }];
        assert_eq!(purse_gain(&before, &after), "p5 gold +37 cs +1; p6 gold +2 kills +1");
    }

    #[test]
    fn the_nearest_of_each_kind_is_named() {
        let f = |id, kind, d| Near { id, name: format!("u{id}"), kind, d, hp: 100 };
        let foes = [f(3, "minion", 5_000.0), f(4, "minion", 6_000.0), f(7, "champion", 9_000.0), f(8, "tower", 50_000.0)];
        assert_eq!(near_text(&foes, 4), "minion #3 u3 5000 away hp 100; champion #7 u7 9000 away hp 100; tower #8 u8 50000 away hp 100");
        assert_eq!(near_text(&foes, 1), "minion #3 u3 5000 away hp 100");
        assert_eq!(near_text(&[], 4), "nobody");
        assert_eq!(kind_name(None, false, true, false), "minion");
        assert_eq!(kind_name(Some(EntityKindV1::Summon), false, false, false), "summon");
    }

    #[test]
    fn a_statistic_reads_as_a_whole_number() {
        assert_eq!(number("1234"), Some(1234));
        assert_eq!(number(" 56.9 "), Some(56));
        assert_eq!(number("\"7\""), Some(7));
        assert_eq!(number("-3"), None);
        assert_eq!(number("null"), None);
        assert_eq!(number(""), None);
        assert_eq!(gain_text(Some(100), Some(180), "in the second"), "+80 in the second (now 180)");
        assert_eq!(gain_text(None, Some(180), "in the second"), "now 180");
        assert_eq!(gain_text(Some(1), None, "over its life"), "not readable");
    }

    #[test]
    fn long_names_are_cut_on_a_character() {
        assert_eq!(short("league_shaco"), "league_shaco");
        assert_eq!(short(&"长".repeat(20)).chars().count(), NAME_SHOWN / 3);
    }

    #[test]
    fn a_flocks_spawn_points_lie_round_the_spot() {
        let at = (500_000.0, 400_000.0);
        let p = spread(at, 9_000.0, 3, 0.0);
        assert_eq!(p.len(), 3);
        assert!((p[0].0 - 509_000.0).abs() < 1e-6 && (p[0].1 - 400_000.0).abs() < 1e-6);
        for q in &p {
            assert!((dist(*q, at) - 9_000.0).abs() < 1e-6);
        }
        // evenly: every two neighbours the same distance apart
        let (a, b, c) = (dist(p[0], p[1]), dist(p[1], p[2]), dist(p[2], p[0]));
        assert!((a - b).abs() < 1e-6 && (b - c).abs() < 1e-6);
        assert_eq!(spread(at, 9_000.0, 0, 0.0).len(), 0);
        assert_eq!(spread(at, 0.0, 2, 1.0), vec![at, at]);
        // a flock's books start empty, with room for its cap
        let f: Flock<u8> = Flock::new("league_x_uid", 4, 300);
        assert!(f.is_empty() && f.room() == 4 && f.out() == 0 && f.waiting() == 0);
        assert_eq!(Flock::<u8>::new("league_x_uid", 0, 300).cap, 1);
    }
}
