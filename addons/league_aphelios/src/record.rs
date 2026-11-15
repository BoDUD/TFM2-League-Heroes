//! 记录器（0.2.4）。用户 2026-11-15：「不知道为什么厄斐琉斯打架就站着不动 从满血被周围2 3个打死 查一查这是我们的问题还是
//! 官方AI的问题」。以前的日志只记普攻刚好就绪的那几 tick（league_ai_watch）和钩子每 50 次抽 1 次，两次普攻之间他站着的那段
//! 没人记。AI 钩子现在每一 tick 记下他：走着、钉在原地（站着，或在普攻 / 技能的动作里）、被控（击飞、眩晕、定身、嘲讽、恐惧、
//! 魅惑、被击退），以及他手上的命令是谁下的什么——游戏 AI（或排在前面的钩子，如 league_ult_press 的补 A）的普攻 / 走路 /
//! 技能 / 回城，还是本包否决 Q / W 后改成的普攻、本包替 AI 按的 Q。游戏 AI 只在它做决定的 tick 下命令，别的 tick 照着上一道做，
//! 所以记的是「手上的那道」。
//!
//! - 每次阵亡一行 `DEATH`：死前 5 秒走了多久、钉在原地多久（按命令分）、被控多久，最长一次钉了多久、多半是谁的命令，普攻和 Q
//!   各出手几次，这 5 秒里本包否决了几次 Q / W、打架时放行了几次（0.2.3 会否决的）。你看着的那场全写，预模拟先写
//!   [`DEATH_FIRST`] 行、之后每 [`DEATH_EVERY`] 次一行。
//! - 每 [`SUM_EVERY`] 次阵亡一行 `SUM`（这次启动的所有比赛）：所有阵亡前 5 秒、所有打架时（[`CROWD_R`] 以内两个以上看得见的
//!   敌方英雄）各种样子的比例。
//!
//! 只读：不改输入，也不改模拟。

use std::collections::VecDeque;
use std::sync::Mutex;

use mod_api_stable::*;

use super::{at_of, brain, hp_share, origin_name, wlog, VETO_HOLD};

/// 游戏一秒 60 tick。
pub const TICKS_PER_S: usize = 60;
/// 阵亡前看多久（tick）。
pub const WINDOW: usize = 5 * TICKS_PER_S;
/// 「被围着打」：这以内两个以上看得见的敌方英雄。
pub const CROWD_R: f64 = 60_000.0;
/// 阵亡前 5 秒开头的生命不低于这个比例，算「从满血被打死」。
pub const FULL: f32 = 0.8;
/// 死前 5 秒在本包否决改成的普攻下钉了这么久以上，算一次「否决钉死」。
pub const VETO_PLANT: usize = TICKS_PER_S;
/// 每这么多次阵亡写一行 SUM。
pub const SUM_EVERY: usize = 100;
/// 预模拟的 DEATH 行：先写这么多，之后每 `DEATH_EVERY` 次写一行（看着的那场全写）。
pub const DEATH_FIRST: usize = 300;
pub const DEATH_EVERY: usize = 10;

/// 被控：动不了、或不由他自己走（被击退的 ForceMove 也算——他自己没有位移技能）。
const HELD: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
    CcKindV1::Charm, CcKindV1::ForceMove];

/// 他手上的命令：谁下的、什么。
#[derive(Clone, Copy, Debug, PartialEq, Eq, Default)]
pub enum Order {
    /// 这条命还没有命令
    #[default]
    None,
    /// 游戏 AI（或排在前面的钩子）的普攻
    AiAttack,
    /// 游戏 AI 的走路（走到脚下、被挡住时人不动）
    AiMove,
    /// 游戏 AI 的技能、大招（放行了的）
    AiCast,
    /// 回城读条
    AiRecall,
    /// 本包把 AI 的 Q / W 否决后改成的普攻
    OurVeto,
    /// 本包替 AI 按的 Q
    OurPress,
}

pub const ORDERS: [Order; 7] =
    [Order::None, Order::AiAttack, Order::AiMove, Order::AiCast, Order::AiRecall, Order::OurVeto, Order::OurPress];

impl Order {
    pub fn name(self) -> &'static str {
        match self {
            Order::None => "no order",
            Order::AiAttack => "AI attack",
            Order::AiMove => "AI walk",
            Order::AiCast => "AI cast",
            Order::AiRecall => "recall",
            Order::OurVeto => "our Q/W veto",
            Order::OurPress => "our Q press",
        }
    }

    pub fn index(self) -> usize {
        ORDERS.iter().position(|o| *o == self).unwrap_or(0)
    }

    /// 游戏 AI（或前面的钩子）这一 tick 下的命令是哪一类。
    pub fn of_input(kind: u32) -> Option<Order> {
        Some(match InputKindV1::from_code(kind)? {
            InputKindV1::Attack => Order::AiAttack,
            InputKindV1::Move => Order::AiMove,
            InputKindV1::Return => Order::AiRecall,
            InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Ult => Order::AiCast,
        })
    }
}

/// 一 tick 的样子。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum State {
    /// 位置变了
    Moved,
    /// 没动：站着，或在普攻 / 技能的动作里
    Planted,
    /// 被控（[`HELD`]）
    Controlled,
}

pub fn state_of(moved: bool, controlled: bool) -> State {
    if controlled {
        State::Controlled
    } else if moved {
        State::Moved
    } else {
        State::Planted
    }
}

/// 记下的一 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Rec {
    pub state: State,
    /// 这一 tick 他手上的命令（这一 tick 新下的命令从下一 tick 算起）
    pub order: Order,
    pub hp: f32,
    /// `CROWD_R` 以内看得见的敌方英雄
    pub crowd: u8,
    /// 普攻出手（普攻冷却重新开始走）
    pub attack: bool,
    /// Q 出手
    pub q: bool,
    /// 这一 tick 本包否决了 AI 的 Q / W
    pub veto: bool,
    /// 这一 tick AI 的 Q / W 在打架时放行了（0.2.3 会否决）
    pub pass: bool,
}

/// 这一 tick 看到的他。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Seen {
    pub id: usize,
    pub pos: (u64, u64),
    pub hp: f32,
    pub controlled: bool,
    pub attack_cd: usize,
    pub q_cd: usize,
    pub crowd: u8,
}

/// 这一 tick：模拟的 tick、来源（种类码、比赛、第几局）、他（阵亡了是 None）。
pub struct Look {
    pub tick: usize,
    pub origin: (u32, u64, u64),
    pub me: Option<Seen>,
}

/// 只读地看一眼 `player` 的英雄。
pub fn look(sim: &StableSim<'_>, player: usize) -> Look {
    let o = sim.sim_origin().unwrap_or_default();
    let me = sim.get_player(player).and_then(|p| p.champion()).filter(|e| e.is_alive()).map(|e| {
        let (team, at) = (e.team(), at_of(&e));
        let crowd = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_champion() && u.is_alive() && sim.is_visible(team, u.id()))
            .filter(|u| brain::dist(at, at_of(u)) <= CROWD_R)
            .count()
            .min(u8::MAX as usize) as u8;
        let cd = |s: SkillSlotV1| e.cooldown(s).map_or(0, |c| c.remaining);
        Seen {
            id: e.id(),
            pos: e.pos(),
            hp: hp_share(&e) as f32,
            controlled: (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HELD.iter().any(|k| k.code() == c.kind))),
            attack_cd: cd(SkillSlotV1::Attack),
            q_cd: cd(SkillSlotV1::Skill),
            crowd,
        }
    });
    Look { tick: sim.tick(), origin: (o.kind, o.match_id, o.set_index), me }
}

/// 各种样子的 tick 数：钉在原地的按命令分（`ORDERS` 的顺序）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Counts {
    pub moved: usize,
    pub controlled: usize,
    pub planted: [usize; 7],
}

impl Counts {
    pub fn add(&mut self, r: &Rec) {
        match r.state {
            State::Moved => self.moved += 1,
            State::Controlled => self.controlled += 1,
            State::Planted => self.planted[r.order.index()] += 1,
        }
    }

    pub fn planted_all(&self) -> usize {
        self.planted.iter().sum()
    }

    pub fn all(&self) -> usize {
        self.moved + self.controlled + self.planted_all()
    }

    fn merge(&mut self, o: &Counts) {
        self.moved += o.moved;
        self.controlled += o.controlled;
        for (a, b) in self.planted.iter_mut().zip(o.planted) {
            *a += b;
        }
    }
}

/// 阵亡前那几秒的总结。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Summary {
    pub ticks: usize,
    pub counts: Counts,
    /// 最长一次连着钉在原地的 tick 数，和那段时间里最多的命令
    pub longest: usize,
    pub longest_by: Order,
    pub attacks: usize,
    pub qs: usize,
    pub vetoes: usize,
    pub passes: usize,
    pub hp_start: f32,
    /// 身边（`CROWD_R`）两个以上敌方英雄的 tick
    pub crowd2: usize,
}

pub fn summarize(recs: &VecDeque<Rec>) -> Summary {
    let mut s = Summary { ticks: recs.len(), hp_start: recs.front().map_or(0.0, |r| r.hp), ..Summary::default() };
    let mut run = (0usize, [0usize; 7]);
    let close = |run: &mut (usize, [usize; 7]), s: &mut Summary| {
        if run.0 > s.longest {
            s.longest = run.0;
            let best = (0..ORDERS.len()).max_by_key(|&i| run.1[i]).unwrap_or(0);
            s.longest_by = ORDERS[best];
        }
        *run = (0, [0; 7]);
    };
    for r in recs {
        s.counts.add(r);
        s.attacks += r.attack as usize;
        s.qs += r.q as usize;
        s.vetoes += r.veto as usize;
        s.passes += r.pass as usize;
        s.crowd2 += (r.crowd >= 2) as usize;
        if r.state == State::Planted {
            run.0 += 1;
            run.1[r.order.index()] += 1;
        } else {
            close(&mut run, &mut s);
        }
    }
    close(&mut run, &mut s);
    s
}

fn secs(ticks: usize) -> f64 {
    ticks as f64 / TICKS_PER_S as f64
}

/// 钉在原地按命令分：多的在前，没有的不写。
fn planted_by(c: &Counts, unit: impl Fn(usize) -> String) -> String {
    let mut v: Vec<(usize, Order)> =
        ORDERS.iter().map(|o| (c.planted[o.index()], *o)).filter(|(n, _)| *n > 0).collect();
    v.sort_by_key(|(n, _)| std::cmp::Reverse(*n));
    v.iter().map(|(n, o)| format!("{} {}", o.name(), unit(*n))).collect::<Vec<_>>().join(", ")
}

pub fn death_line(head: &str, alive: usize, s: &Summary, n: usize) -> String {
    let c = &s.counts;
    format!(
        "{head} DEATH after {:.1} s alive: the last {:.1} s from {:.0}% hp ({:.1} s of them with 2+ enemy champions within \
         {CROWD_R:.0}): moved {:.1} s, planted {:.1} s ({}), controlled {:.1} s; longest plant {:.1} s ({}); attacks {}, \
         Q casts {}, Q/W vetoes {}, Q/W let through in a fight {} #{n}",
        secs(alive),
        secs(s.ticks),
        s.hp_start * 100.0,
        secs(s.crowd2),
        secs(c.moved),
        secs(c.planted_all()),
        planted_by(c, |t| format!("{:.1}", secs(t))),
        secs(c.controlled),
        secs(s.longest),
        s.longest_by.name(),
        s.attacks,
        s.qs,
        s.vetoes,
        s.passes
    )
}

fn shares(c: &Counts) -> String {
    let all = c.all().max(1) as f64;
    let pct = |t: usize| format!("{:.0}%", t as f64 * 100.0 / all);
    format!("moved {}, planted {} ({}), controlled {}", pct(c.moved), pct(c.planted_all()), planted_by(c, pct),
        pct(c.controlled))
}

/// 这次启动的总数（所有比赛、所有厄斐琉斯）。
#[derive(Clone, Copy, Debug, Default)]
pub struct Totals {
    pub deaths: usize,
    pub from_full: usize,
    pub veto_plants: usize,
    pub passes_before_death: usize,
    pub last5: Counts,
    pub fights: Counts,
    pub passes_fight: usize,
    pub passes_no_target: usize,
    pub vetoes: usize,
    pub released: usize,
}

impl Totals {
    /// 记进一次阵亡，返回这是第几次。
    pub fn add_death(&mut self, s: &Summary) -> usize {
        self.deaths += 1;
        self.from_full += (s.hp_start >= FULL) as usize;
        self.veto_plants += (s.counts.planted[Order::OurVeto.index()] >= VETO_PLANT) as usize;
        self.passes_before_death += s.passes;
        self.last5.merge(&s.counts);
        self.deaths
    }

    pub fn sum_line(&self) -> String {
        format!(
            "SUM {} deaths (every match since the launch): the last 5 s before them: {}; {} from {:.0}%+ hp; {} with {:.0} s+ \
             planted under our Q/W veto; Q/W let through in a fight in those 5 s: {} | in fights (2+ enemy champions within \
             {CROWD_R:.0}) {:.1} min: {} | the AI's Q/W let through: in a fight {}, nothing to attack instead {}; vetoes {}, \
             released after {:.0} s of asking {}",
            self.deaths,
            shares(&self.last5),
            self.from_full,
            FULL * 100.0,
            self.veto_plants,
            secs(VETO_PLANT),
            self.passes_before_death,
            self.fights.all() as f64 / (60 * TICKS_PER_S) as f64,
            shares(&self.fights),
            self.passes_fight,
            self.passes_no_target,
            self.vetoes,
            secs(VETO_HOLD),
            self.released
        )
    }
}

static TOTALS: Mutex<Option<Totals>> = Mutex::new(None);

fn totals<R>(f: impl FnOnce(&mut Totals) -> R) -> R {
    let mut g = TOTALS.lock().unwrap_or_else(|e| e.into_inner());
    f(g.get_or_insert_with(Totals::default))
}

/// AI 的 Q / W 放行了（打架时 `fight`，否则是没有能改打的目标）。
pub fn note_pass(fight: bool) {
    totals(|t| if fight { t.passes_fight += 1 } else { t.passes_no_target += 1 });
}

pub fn note_veto() {
    totals(|t| t.vetoes += 1);
}

pub fn note_release() {
    totals(|t| t.released += 1);
}

fn on_screen(kind: u32) -> bool {
    matches!(
        SimOriginKindV1::from_code(kind),
        Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    )
}

/// 预模拟的第 `n` 次阵亡写不写（看着的那场全写）。
pub fn death_logged(on_screen: bool, n: usize) -> bool {
    on_screen || n <= DEATH_FIRST || n.is_multiple_of(DEATH_EVERY)
}

fn head(origin: (u32, u64, u64), tick: usize, id: usize) -> String {
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{} m={} s={}] t={tick} #{id}", origin_name(origin.0), m(origin.1), m(origin.2))
}

/// 一位选手的厄斐琉斯在一场模拟里：这条命的记录。
#[derive(Clone, Debug, Default)]
pub struct Life {
    id: Option<usize>,
    origin: (u32, u64, u64),
    last_tick: Option<usize>,
    last_pos: Option<(u64, u64)>,
    last_attack_cd: usize,
    last_q_cd: usize,
    order: Order,
    alive: usize,
    recs: VecDeque<Rec>,
}

impl Life {
    /// 这一 tick：看到的他、这一 tick 出去的命令（本包换的或 AI 自己的；None = 没有新命令）、本包否决了没有、打架时放行了没有。
    pub fn step(&mut self, look: &Look, went: Option<Order>, veto: bool, pass: bool) {
        let Some(me) = look.me else {
            self.end(look.tick);
            return;
        };
        if self.id != Some(me.id) {
            self.end(look.tick);
            *self = Life { id: Some(me.id), origin: look.origin, ..Life::default() };
        }
        if self.last_tick == Some(look.tick) {
            return;
        }
        if let Some(p) = self.last_pos {
            let rec = Rec {
                state: state_of(p != me.pos, me.controlled),
                order: self.order,
                hp: me.hp,
                crowd: me.crowd,
                attack: me.attack_cd > self.last_attack_cd,
                q: me.q_cd > self.last_q_cd,
                veto,
                pass,
            };
            if rec.crowd >= 2 {
                totals(|t| t.fights.add(&rec));
            }
            if self.recs.len() >= WINDOW {
                self.recs.pop_front();
            }
            self.recs.push_back(rec);
        }
        if let Some(o) = went {
            self.order = o;
        }
        self.last_tick = Some(look.tick);
        self.last_pos = Some(me.pos);
        self.last_attack_cd = me.attack_cd;
        self.last_q_cd = me.q_cd;
        self.alive += 1;
    }

    /// 这条命结束了（阵亡，或下一 tick 已经是新的实体）：写 DEATH，记进总数。
    fn end(&mut self, tick: usize) {
        let Some(id) = self.id.take() else { return };
        if self.recs.is_empty() {
            return;
        }
        let s = summarize(&self.recs);
        let (n, sum) = totals(|t| {
            let n = t.add_death(&s);
            (n, n.is_multiple_of(SUM_EVERY).then(|| t.sum_line()))
        });
        if death_logged(on_screen(self.origin.0), n) {
            wlog(death_line(&head(self.origin, tick, id), self.alive, &s, n));
        }
        if let Some(line) = sum {
            wlog(line);
        }
        self.recs.clear();
    }

    #[cfg(test)]
    pub fn recs(&self) -> &VecDeque<Rec> {
        &self.recs
    }

    #[cfg(test)]
    pub fn order(&self) -> Order {
        self.order
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn rec(state: State, order: Order) -> Rec {
        Rec { state, order, hp: 1.0, crowd: 2, attack: false, q: false, veto: false, pass: false }
    }

    fn seen(id: usize, x: u64) -> Seen {
        Seen { id, pos: (x, 0), hp: 1.0, controlled: false, attack_cd: 0, q_cd: 0, crowd: 0 }
    }

    fn at(tick: usize, me: Option<Seen>) -> Look {
        Look { tick, origin: (SimOriginKindV1::ServerPresim.code(), 7, SimOriginV1::NONE), me }
    }

    #[test]
    fn the_inputs_map_to_their_orders() {
        assert_eq!(Order::of_input(InputKindV1::Attack.code()), Some(Order::AiAttack));
        assert_eq!(Order::of_input(InputKindV1::Move.code()), Some(Order::AiMove));
        assert_eq!(Order::of_input(InputKindV1::Skill2.code()), Some(Order::AiCast));
        assert_eq!(Order::of_input(InputKindV1::Return.code()), Some(Order::AiRecall));
        assert_eq!(Order::of_input(99), None);
        for (i, o) in ORDERS.iter().enumerate() {
            assert_eq!(o.index(), i);
        }
    }

    #[test]
    fn controlled_beats_moved_beats_planted() {
        assert_eq!(state_of(true, true), State::Controlled);
        assert_eq!(state_of(true, false), State::Moved);
        assert_eq!(state_of(false, false), State::Planted);
    }

    #[test]
    fn the_summary_finds_the_longest_plant_and_whose_it_was() {
        let mut recs = VecDeque::new();
        recs.extend(std::iter::repeat_n(rec(State::Moved, Order::AiMove), 30));
        recs.extend(std::iter::repeat_n(rec(State::Planted, Order::OurVeto), 50));
        recs.extend(std::iter::repeat_n(rec(State::Planted, Order::AiAttack), 10));
        recs.extend(std::iter::repeat_n(rec(State::Controlled, Order::AiAttack), 20));
        recs.extend(std::iter::repeat_n(rec(State::Planted, Order::AiAttack), 40));
        let s = summarize(&recs);
        assert_eq!((s.ticks, s.counts.moved, s.counts.controlled, s.counts.planted_all()), (150, 30, 20, 100));
        assert_eq!(s.counts.planted[Order::OurVeto.index()], 50);
        // the first plant (60 ticks, mostly the veto's) is longer than the last (40)
        assert_eq!((s.longest, s.longest_by), (60, Order::OurVeto));
        assert_eq!(s.crowd2, 150);
        let line = death_line("[view m=1 s=1] t=900 #21", 600, &s, 3);
        assert!(line.contains("DEATH after 10.0 s alive"), "{line}");
        // a tie keeps ORDERS' order
        assert!(line.contains("planted 1.7 s (AI attack 0.8, our Q/W veto 0.8)"), "{line}");
        assert!(line.contains("longest plant 1.0 s (our Q/W veto)"), "{line}");
    }

    #[test]
    fn a_life_keeps_the_last_five_seconds_and_the_order_in_hand() {
        let mut life = Life::default();
        // spawn: the first tick has no position before it, nothing recorded
        life.step(&at(1, Some(seen(21, 0))), Some(Order::AiAttack), false, false);
        assert!(life.recs().is_empty());
        // the order given on tick 1 is the one in hand on tick 2 (he stood: same spot)
        life.step(&at(2, Some(seen(21, 0))), None, true, false);
        assert_eq!(life.recs()[0], Rec { veto: true, crowd: 0, ..rec(State::Planted, Order::AiAttack) });
        life.step(&at(2, Some(seen(21, 0))), None, false, false); // the same tick twice: once
        assert_eq!(life.recs().len(), 1);
        for t in 3..(3 + WINDOW + 10) {
            life.step(&at(t, Some(seen(21, t as u64))), Some(Order::OurVeto), false, false);
        }
        assert_eq!(life.recs().len(), WINDOW);
        assert_eq!(life.order(), Order::OurVeto);
        assert!(life.recs().iter().all(|r| r.state == State::Moved));
        // dead: the life ends (its records go into the totals), a new entity starts a new one
        life.step(&at(400, None), None, false, false);
        assert!(life.recs().is_empty());
        life.step(&at(900, Some(seen(300, 5))), None, false, false);
        assert_eq!(life.order(), Order::None);
    }

    #[test]
    fn every_death_on_screen_and_a_sample_of_the_rest_is_written() {
        assert!(death_logged(true, 12345));
        assert!(death_logged(false, DEATH_FIRST));
        assert!(!death_logged(false, DEATH_FIRST + 1));
        assert!(death_logged(false, DEATH_FIRST + DEATH_EVERY - (DEATH_FIRST % DEATH_EVERY)));
    }

    #[test]
    fn the_totals_count_deaths_from_full_and_the_veto_plants() {
        let mut t = Totals::default();
        let mut recs = VecDeque::new();
        recs.extend(std::iter::repeat_n(rec(State::Planted, Order::OurVeto), VETO_PLANT));
        let s = summarize(&recs);
        assert_eq!(t.add_death(&s), 1);
        recs.iter_mut().for_each(|r| {
            r.hp = 0.5;
            r.order = Order::AiAttack;
        });
        assert_eq!(t.add_death(&summarize(&recs)), 2);
        assert_eq!((t.from_full, t.veto_plants), (1, 1));
        let line = t.sum_line();
        assert!(line.starts_with("SUM 2 deaths"), "{line}");
        assert!(line.contains("planted 100% (AI attack 50%, our Q/W veto 50%)") || line.contains("planted 100% (our Q/W veto 50%, AI attack 50%)"), "{line}");
    }
}
