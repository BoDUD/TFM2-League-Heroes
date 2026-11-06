//! AI 钩子 `league_zed_mark:combo`：劫的连招（0.2.0，用户 2026-11-03：「劫：他不会打连招，而且他的Q技能根本看不见。」，照
//! 「参考LOL高手」的打法）。
//!
//! 以前：游戏 0.6.4 起的 AI 自己按 Q（好了就扔）和 R（很少：射程里有人也常常不按），W 几乎不按——W 一次放出 W-E-Q，主包的 Q、E
//! 标记（`league_zed_q_cd`、`league_zed_e_cd`）在的时候 AI 读到的那一支没有伤害；league_ult_press 在 Q 好着、不以少打多时替它按 W。
//! 主包大招印记期间 W 好着时 Q 的格子是空分支、等 W，谁都不按 W 就三秒没有 Q（主包同一天起只等冲刺后 `r_wq` tick）。
//! 现在本钩子替 AI 按（排在 league_ult_press（100）之后，`PRIORITY`；劫的 W 从 league_ult_press 挪到这里），每 tick 按下面的先后
//! 挑第一个引擎接的（`plan`，纯计算、单元测试）：
//!
//! 1. **印记期间甩影子**（R-W-E-Q 的 W）：印记在（他身上 `league_zed_r_on`）、W 好了：W 甩到带印记（`league_zed_r_mark`）的那个人
//!    脚下，以少打多也甩（大招影子是退路）；主包接着鬼斩、诸刃，影子跟着放。
//! 2. **R 起手**：R 好了、他生命不低于 `ENGAGE_HP`；`R_REACH` 内的敌方英雄，不在敌方塔下（生命 `DIVE_HP` 以下的除外），那里的
//!    敌方英雄最多比他身边的我方英雄（含他）多一个；而且值得：W、Q 都好、目标生命不到 `R_LOW`（R-W-E-Q 打得死），或目标生命不到
//!    `R_SOLO`（R 的爆发补刀），或我方有人 `FIGHT_CONTACT` 内贴着他在打（进场接团）。生命比例最低的先；引擎只接最近被我方打过的
//!    英雄（`EnemyChampionRecentlyAttacked`，`is_valid_input`）。
//! 3. **W-E-Q 起手**（league_ult_press 原来的规则）：W 好了、Q 好着、他生命不低于 `ENGAGE_HP`；`W_REACH` 内、不在敌方塔下（残血
//!    除外）、那里不以少打多的敌方英雄，生命比例最低的。
//! 4. **影子在场补 Q**：影子在（`league_zed_w_live` / `w_live2` / `r_live`）、Q 好着：`Q_REACH` 内的敌方英雄（带印记的先，再生命
//!    比例最低的），影子在下一个检查点跟着扔。
//!
//! 别的交给 AI。「Q 好着」= Q 的格子好了、主包标记 `league_zed_q_cd` 不在（W 的连招扔过诸刃只挂标记、不走格子的冷却），而且主包
//! 这时 Q 的格子不是空分支（冲刺后 `r_wq` tick 内、`league_zed_w_cd` 不在时是）：空分支按下去只会白白进冷却。印记在、W 好着时
//! 不按 Q（先 W）。正在回城、放技能或被位移（`BUSY`）、被控（`NO_CAST`）、他自己的 W / Q / R 动作还在播时不管；AI 这一 tick
//! 已经按了排在第一的那个格子也不管，AI 自己按的 R 照放（接着第 1 条甩影子）；进攻的（R、起手的 W）在 AI 正带他远离目标
//! （`AWAY`）时不按。日志 `COMBO`（`counted` 限条数），一串连按只记第一下。
//!
//! 0.2.1（2026-11-06 的日志：`COMBO R on league_anivia` 连着 11 tick 每 tick 一行，一次都没放出去，也没有 MARK）：同一个键连按
//! `PRESS_MAX` tick 还没放出去（放出去了冷却就走、`playing` 拦住下一次）就歇 `BACKOFF` tick，交给 AI，记一行「not taken」写出
//! 他身上的控制、各格冷却和目标的状态（league_orianna 0.3.2 的做法）。同一天主包修好了印记（tools/kit/build_zed.py：`r_on` 从
//! 冲刺一直在到爆发，以前落地那一下就爆、`r_on` 跟着没了），第 1 条的 R-W-E-Q 甩影子这才看得到印记；「印记在」现在是 `r_on` 而且
//! 看得见的敌方英雄里有人带着印记（`mark_holds`）：被标记的人提前死了，`r_on` 还挂到原定的爆发，不该拦着别的起手和影子的 Q。

use mod_api_stable::*;

use super::{counted, head, wlog, ID};

/// league_ult_press（100）之后。
pub const PRIORITY: i32 = 110;
/// 劫（只给他用）。
pub const HERO: &str = "league_zed";
/// 主包挂在他身上的标记（`zd(..)`，单元测试核对），按这个顺序读：Q、W 的冷却标记（`q_cd`、`w_cd`），大招冲刺后 Q 等 W 的
/// `r_wq`，印记期间的 `r_on`，W 影子（换过位置的是 `w_live2`）、大招影子在场。
const FLAGS: [&str; 7] = ["league_zed_q_cd", "league_zed_w_cd", "league_zed_r_wq", "league_zed_r_on", "league_zed_w_live",
                          "league_zed_w_live2", "league_zed_r_live"];
/// 印记（主包挂在被 R 突进的那个人身上，`r_pop` tick）。
const MARK: &str = "league_zed_r_mark";
/// 主包的射程（build_zed.P 的 w_range、q_range、r_range，单元测试核对）。
pub const W_RANGE: f64 = 55_000.0;
pub const Q_RANGE: f64 = 55_000.0;
pub const R_RANGE: f64 = 60_000.0;
/// 起手 W、补的 Q、R 只给这么近的：按下到出手之间人还会走几步。
pub const W_REACH: f64 = 50_000.0;
pub const Q_REACH: f64 = 50_000.0;
pub const R_REACH: f64 = 55_000.0;
/// 冲上去的：他生命比例不低于这个；目标在敌方塔下也冲的残血线（league_ult_press 的 ENGAGE_HP / DIVE_HP）。
pub const ENGAGE_HP: f64 = 0.4;
pub const DIVE_HP: f64 = 0.25;
/// R-W-E-Q：目标生命比例不到这个（W、Q 都好着）；R 单独补刀：不到这个。
pub const R_LOW: f64 = 0.6;
pub const R_SOLO: f64 = 0.3;
/// 目标身边这么近的敌方英雄、他身边这么近的我方英雄比人数（league_ult_press 的 CROWD_R）。
pub const CROWD_R: f64 = 60_000.0;
/// 敌方塔的攻击范围（大约）。
pub const TOWER_REACH: f64 = 75_000.0;
/// 在打架：我方英雄离那个敌方英雄这么近。
pub const FIGHT_CONTACT: f64 = 40_000.0;
/// AI 让他走到比他现在离目标还远这么多的地方：在撤，不起手。
pub const AWAY: f64 = 10_000.0;
/// 他自己的动作还在播（这时按的输入游戏不收）：冷却从满开始走了不到这么多 tick。W：甩影子 6 tick，连招里的诸刃动作从第 5 tick
/// 播 26 tick；Q：26 tick（q_dur）；R：24 tick（r_dur）。
pub const W_ACT: usize = 31;
pub const Q_ACT: usize = 26;
pub const R_ACT: usize = 24;
/// 同一个键连着按了这么多 tick 还没放出去：有东西挡着，歇 `BACKOFF` tick 再看（0.2.1，league_orianna 0.3.2 的数）。
pub const PRESS_MAX: usize = 3;
pub const BACKOFF: usize = 30;

/// 连按的记录：哪种、第一下、上一下、连着几下（league_orianna 的 `Presses`）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Presses {
    pub kind: &'static str,
    pub first: usize,
    pub last: usize,
    pub n: usize,
}

impl Presses {
    /// One more press of `kind` at `tick`: how many in a row (the tick after the last of the same kind), 1 for a new run.
    pub fn press(&mut self, kind: &'static str, tick: usize) -> usize {
        if self.kind == kind && self.n > 0 && tick == self.last + 1 {
            self.n += 1;
        } else {
            *self = Presses { kind, first: tick, last: tick, n: 1 };
        }
        self.last = tick;
        self.n
    }
}

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一个看得见的敌方英雄：位置、生命比例、带着他的印记吗。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub hp: f64,
    pub marked: bool,
}

/// 他这一 tick：位置、生命比例，W / Q / R 能不能按（Q 见上面「Q 好着」），印记在不在、影子在不在。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub hp: f64,
    pub w: bool,
    pub q: bool,
    pub r: bool,
    pub mark_on: bool,
    pub shadow: bool,
}

/// 他看到的：他、敌方英雄、我方英雄（不含他）、敌方的塔、AI 这一 tick 让他走到哪（没下走路命令就是 None）。
pub struct Scene<'a> {
    pub me: Me,
    pub foes: &'a [Foe],
    pub allies: &'a [Pt],
    pub towers: &'a [Pt],
    pub walk: Option<Pt>,
}

impl Scene<'_> {
    fn foes_within(&self, p: Pt, r: f64) -> usize {
        self.foes.iter().filter(|f| dist(p, f.at) <= r).count()
    }

    /// 他这边的人：他身边 `CROWD_R` 内的我方英雄，含他。
    fn ours(&self) -> usize {
        1 + self.allies.iter().filter(|&&a| dist(self.me.at, a) <= CROWD_R).count()
    }

    /// 能冲：目标不在敌方塔下，或已经残血。
    fn diveable(&self, f: &Foe) -> bool {
        f.hp <= DIVE_HP || self.towers.iter().all(|&t| dist(t, f.at) > TOWER_REACH)
    }

    /// 我方有人贴着他在打。
    fn fought(&self, f: &Foe) -> bool {
        self.allies.iter().any(|&a| dist(a, f.at) <= FIGHT_CONTACT)
    }

    /// AI 正带他远离这个人。
    fn away_from(&self, f: &Foe) -> bool {
        self.walk.is_some_and(|to| dist(to, f.at) > dist(self.me.at, f.at) + AWAY)
    }

    /// `r` 内、`ok` 的敌方英雄，生命比例最低的先（一样的近的先，再编号小的）。
    fn pick(&self, r: f64, ok: impl Fn(&Foe) -> bool) -> Vec<&Foe> {
        let mut v: Vec<&Foe> = self.foes.iter().filter(|f| dist(self.me.at, f.at) <= r && ok(f)).collect();
        v.sort_by(|a, b| {
            a.hp.total_cmp(&b.hp).then(dist(self.me.at, a.at).total_cmp(&dist(self.me.at, b.at))).then(a.id.cmp(&b.id))
        });
        v
    }
}

/// 一次要按的。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Plan {
    /// 印记期间：W 甩到带印记的人脚下（R-W-E-Q 的 W）。
    MarkW(usize),
    /// R 起手；`full`：W、Q 都好（R-W-E-Q）。
    R { target: usize, full: bool },
    /// W-E-Q 起手。
    Open(usize),
    /// 影子在场：Q（影子跟着扔）。
    Echo(usize),
}

impl Plan {
    pub fn slot(&self) -> SkillSlotV1 {
        match self {
            Plan::MarkW(_) | Plan::Open(_) => SkillSlotV1::Skill,
            Plan::R { .. } => SkillSlotV1::Ult,
            Plan::Echo(_) => SkillSlotV1::Skill2,
        }
    }

    pub fn target(&self) -> usize {
        match *self {
            Plan::MarkW(t) | Plan::Open(t) | Plan::Echo(t) => t,
            Plan::R { target, .. } => target,
        }
    }

    /// 日志里的种类（`counted` 按它分开数）。
    pub fn kind(&self) -> &'static str {
        match self {
            Plan::MarkW(_) => "combo w mark",
            Plan::R { .. } => "combo r",
            Plan::Open(_) => "combo w open",
            Plan::Echo(_) => "combo q shadow",
        }
    }
}

/// 这一 tick 替他按什么，先后顺序（引擎接哪个就是哪个；空的 = 交给 AI）。
pub fn plan(s: &Scene<'_>) -> Vec<Plan> {
    let me = s.me;
    let mut out = Vec::new();
    // 1. the mark's W: on the marked one, outnumbered or not (the R shadow is the way out)
    if me.mark_on && me.w {
        out.extend(s.pick(W_RANGE, |f| f.marked).into_iter().map(|f| Plan::MarkW(f.id)));
    }
    let engage = me.hp >= ENGAGE_HP && !me.mark_on;
    // 2. R: a kill or a fight worth the ult, not into a crowd, not under their tower
    if me.r && engage {
        let ours = s.ours();
        let worth = |f: &Foe| (me.w && me.q && f.hp < R_LOW) || f.hp < R_SOLO || (s.fought(f) && (me.w || me.q));
        let ok = |f: &Foe| {
            s.diveable(f) && s.foes_within(f.at, CROWD_R) <= ours + 1 && worth(f) && !s.away_from(f)
        };
        out.extend(s.pick(R_REACH, ok).into_iter().map(|f| Plan::R { target: f.id, full: me.w && me.q }));
    }
    // 3. W-E-Q: league_ult_press's rule (not outnumbered where it lands)
    if me.w && me.q && engage {
        let ours = s.ours();
        let ok = |f: &Foe| s.diveable(f) && s.foes_within(f.at, CROWD_R) <= ours && !s.away_from(f);
        out.extend(s.pick(W_REACH, ok).into_iter().map(|f| Plan::Open(f.id)));
    }
    // 4. a shadow standing: Q, the marked one first - never while the mark waits for W
    if me.shadow && me.q && !(me.mark_on && me.w) {
        let mut v = s.pick(Q_REACH, |_| true);
        v.sort_by_key(|f| !f.marked);
        out.extend(v.into_iter().map(|f| Plan::Echo(f.id)));
    }
    out
}

/// 印记在：他身上的 `r_on`，而且看得见的敌方英雄里有人带着印记（0.2.1：主包的 `r_on` 起从冲刺一直挂到爆发；被标记的人提前
/// 死了、印记就没了，`r_on` 还要挂到原定的爆发——这时不该再拦着 W-E-Q 起手和影子的 Q）。
pub fn mark_holds(r_on: bool, foes: &[Foe]) -> bool {
    r_on && foes.iter().any(|f| f.marked)
}

/// 主包这一 tick Q 的格子是空分支吗：标记 `q_cd` 在（W 的连招扔过诸刃），或冲刺后 `r_wq` 在、W 的标记 `w_cd` 不在（等 W）。
pub fn q_empty(q_cd: bool, r_wq: bool, w_cd: bool) -> bool {
    q_cd || (r_wq && !w_cd)
}

// ===================== 钩子 =====================

/// 放不出技能的控制（league_ult_press 的 NO_CAST）。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];
/// 正在放技能（施法动作还在播，游戏 0.6.4 记成 `Animation`）或被强制位移（R 的冲刺）。
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];

fn has_cc(e: &StableEntity<'_, '_>, kinds: &[CcKindV1]) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
}

fn at(e: &StableEntity<'_, '_>) -> Pt {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

fn share((now, max): (usize, usize)) -> f64 {
    if max > 0 { now as f64 / max as f64 } else { 1.0 }
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

/// 一个单位身上的控制，日志用（`Stun, Animation`）。
fn cc_names(e: &StableEntity<'_, '_>) -> String {
    let v: Vec<String> = (0..e.cc_count()).filter_map(|i| e.cc_at(i))
        .map(|c| CcKindV1::from_code(c.kind).map_or_else(|| format!("kind {}", c.kind), |k| format!("{k:?}"))).collect();
    v.join(", ")
}

/// 「not taken」那一行写的：他身上的控制、各格冷却（剩下 / 满的），目标在不在、选不选得中、看不看得见、身上的控制和生命。
fn blocker(ctx: &mut StableAiContext<'_>, player: usize, target: usize) -> String {
    let Some(sim) = ctx.sim() else { return "no sim".to_string() };
    let Some(me) = sim.get_player(player).and_then(|p| p.champion()) else { return "no champion".to_string() };
    let cd = |s: SkillSlotV1| {
        me.cooldown(s).map_or("?".to_string(), |c| format!("{}/{}{}", c.remaining, c.cooltime, if c.unlocked { "" } else { " locked" }))
    };
    let him = format!("his cc [{}], W {} Q {} R {} attack {}", cc_names(&me), cd(SkillSlotV1::Skill), cd(SkillSlotV1::Skill2),
                      cd(SkillSlotV1::Ult), cd(SkillSlotV1::Attack));
    let it = match sim.get_entity(target) {
        Some(t) => format!("{}{}{}, cc [{}], hp {:.0}%", who(&sim, target), if t.is_targetable() { "" } else { " untargetable" },
                           if sim.is_visible(me.team(), target) { "" } else { " unseen" }, cc_names(&t), share(t.hp()) * 100.0),
        None => format!("#{target} gone"),
    };
    format!("{him}; target {it}")
}

#[derive(Clone, Default)]
pub struct Combo {
    /// 正在回城（回城命令开始、别的命令结束；AI 只在判断的那几 tick 下命令）。
    recalling: bool,
    /// 连按的记录和歇到哪个 tick（`PRESS_MAX` / `BACKOFF`，0.2.1）。
    presses: Presses,
    hold_until: usize,
}

impl StablePlayerAi for Combo {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:combo")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        self.recalling = match base {
            Some(b) => b.kind == InputKindV1::Return.code(),
            None => self.recalling,
        };
        if self.recalling {
            return None;
        }
        // backing off after a run of presses nothing took (0.2.1): the AI's own input goes
        if ctx.tick() < self.hold_until {
            return None;
        }
        let walk = base.filter(|b| b.kind == InputKindV1::Move.code()).map(|b| (b.x as f64, b.y as f64));
        let player = ctx.player_id();
        // the candidates in order: the press, its log kind, its line
        let cands: Vec<(InputV1, &'static str, String)> = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() || has_cc(&me, &BUSY) || has_cc(&me, &NO_CAST) {
                return None;
            }
            // his own W / Q / R still playing: a press now is dropped
            let playing = |s: SkillSlotV1, act: usize| {
                me.cooldown(s).is_some_and(|c| c.remaining > 0 && c.cooltime.saturating_sub(c.remaining) < act)
            };
            if playing(SkillSlotV1::Skill, W_ACT) || playing(SkillSlotV1::Skill2, Q_ACT) || playing(SkillSlotV1::Ult, R_ACT) {
                return None;
            }
            let ready = |s: SkillSlotV1| me.cooldown(s).is_some_and(|c| c.unlocked && c.remaining == 0);
            let mut on = [false; FLAGS.len()];
            for b in (0..me.buff_count()).filter_map(|i| me.buff_at(i)) {
                if let Some(k) = FLAGS.iter().position(|f| *f == b.name()) {
                    on[k] = true;
                }
            }
            let [q_cd, w_cd, r_wq, r_on, w_live, w_live2, r_live] = on;
            let (my_id, team, here) = (me.id(), me.team(), at(&me));
            let mut me_now = Me {
                at: here,
                hp: share(me.hp()),
                w: ready(SkillSlotV1::Skill),
                q: ready(SkillSlotV1::Skill2) && !q_empty(q_cd, r_wq, w_cd),
                r: ready(SkillSlotV1::Ult),
                mark_on: r_on,
                shadow: w_live || w_live2 || r_live,
            };
            if !me_now.w && !me_now.q && !me_now.r {
                return None;
            }
            let (mut foes, mut allies) = (Vec::new(), Vec::new());
            for i in 0..sim.champion_count() {
                let id = sim.champion_id_at(i);
                if id == my_id {
                    continue;
                }
                let Some(e) = sim.get_entity(id) else { continue };
                if !e.is_alive() {
                    continue;
                }
                if e.team() == team {
                    allies.push(at(&e));
                } else if e.is_targetable() && sim.is_visible(team, id) {
                    let marked = (0..e.buff_count()).filter_map(|k| e.buff_at(k)).any(|b| b.name() == MARK);
                    foes.push(Foe { id, at: at(&e), hp: share(e.hp()), marked });
                }
            }
            if foes.is_empty() {
                return None;
            }
            me_now.mark_on = mark_holds(r_on, &foes);
            let towers: Vec<Pt> = (0..sim.tower_count())
                .filter_map(|k| sim.get_entity(sim.tower_id_at(k)))
                .filter(|t| t.is_alive() && t.team() != team)
                .map(|t| at(&t))
                .collect();
            let scene = Scene { me: me_now, foes: &foes, allies: &allies, towers: &towers, walk };
            let plans = plan(&scene);
            if plans.is_empty() {
                return None;
            }
            let lead = head(&sim, my_id);
            plans
                .iter()
                .map(|p| {
                    let t = p.target();
                    let f = foes.iter().find(|f| f.id == t);
                    let about = format!("{} {:.0} away at {:.0}%", who(&sim, t), f.map_or(f64::NAN, |f| dist(here, f.at)),
                                        f.map_or(f64::NAN, |f| f.hp * 100.0));
                    let what = match p {
                        Plan::MarkW(_) => format!("W on the marked {about} (R-W-E-Q)"),
                        Plan::R { full: true, .. } => format!("R on {about}, W and Q ready (R-W-E-Q)"),
                        Plan::R { full: false, .. } => format!("R on {about}"),
                        Plan::Open(_) => format!("W on {about} (W-E-Q)"),
                        Plan::Echo(_) => format!("Q on {about}, the shadow throws too"),
                    };
                    let kind = match p.slot() {
                        SkillSlotV1::Skill => InputKindV1::Skill,
                        SkillSlotV1::Skill2 => InputKindV1::Skill2,
                        _ => InputKindV1::Ult,
                    };
                    (InputV1::action(kind, InputTargetV1::target(t)), p.kind(),
                     format!("{lead} COMBO {what}, his hp {:.0}%", me_now.hp * 100.0))
                })
                .collect()
        };
        // the AI's own R goes (the mark's W follows: R-W-E-Q), and so does its own press of the slot planned first
        if base.is_some_and(|b| b.kind == InputKindV1::Ult.code() || cands.first().is_some_and(|(i, _, _)| i.kind == b.kind)) {
            return None;
        }
        let (input, kind, line) = cands.into_iter().find(|(i, _, _)| ctx.is_valid_input(i))?;
        // a run of presses nothing took (a cast starts its cooldown and `playing` ends the run): back off, one line
        // naming what may block it (11-06: R on Anivia pressed 11 ticks running, never cast)
        let tick = ctx.tick();
        let n = self.presses.press(kind, tick);
        if n > PRESS_MAX {
            self.hold_until = tick + BACKOFF;
            if let Some(k) = counted("blocked") {
                let why = blocker(ctx, player, input.target.target_id);
                wlog(format!("{line}: pressed {} ticks running since t={} and not taken ({why}) - backing off {BACKOFF} ticks #{k}",
                             n - 1, self.presses.first));
            }
            return None;
        }
        // the first press of a run only (0.2.0 wrote every tick of it)
        if n == 1 {
            if let Some(k) = counted(kind) {
                wlog(format!("{line} #{k}"));
            }
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::super::zd;
    use super::*;

    fn foe(id: usize, x: f64, hp: f64) -> Foe {
        Foe { id, at: (x, 0.0), hp, marked: false }
    }

    fn me() -> Me {
        Me { at: (0.0, 0.0), hp: 1.0, w: true, q: true, r: true, mark_on: false, shadow: false }
    }

    fn scene<'a>(me: Me, foes: &'a [Foe], allies: &'a [Pt], towers: &'a [Pt]) -> Scene<'a> {
        Scene { me, foes, allies, towers, walk: None }
    }

    #[test]
    fn r_w_e_q_on_a_wounded_one_then_w_during_the_mark() {
        // two apart (70000: each alone where he stands)
        let foes = [foe(1, 40_000.0, 0.5), foe(2, -30_000.0, 0.9)];
        // R first on the wounded one (the full combo), then the plain W-E-Q openers
        assert_eq!(plan(&scene(me(), &foes, &[], &[])),
                   vec![Plan::R { target: 1, full: true }, Plan::Open(1), Plan::Open(2)]);
        // side by side: the opener would land among two, his side one - R only (one more than his side is fine)
        let pair = [foe(1, 40_000.0, 0.5), foe(2, 30_000.0, 0.9)];
        assert_eq!(plan(&scene(me(), &pair, &[], &[])), vec![Plan::R { target: 1, full: true }]);
        // the dash done: W on the marked one, outnumbered or not, and no Q before it
        let marked = [Foe { marked: true, ..foe(1, 10_000.0, 0.4) }, foe(2, 20_000.0, 0.9), foe(3, 25_000.0, 0.9)];
        let s = Me { r: false, mark_on: true, shadow: true, ..me() };
        assert_eq!(plan(&scene(s, &marked, &[], &[])), vec![Plan::MarkW(1)]);
        // W thrown: the shadows' Q, the marked one first
        let s = Me { r: false, w: false, mark_on: true, shadow: true, ..me() };
        assert_eq!(plan(&scene(s, &marked, &[], &[])), vec![Plan::Echo(1), Plan::Echo(2), Plan::Echo(3)]);
    }

    #[test]
    fn r_is_kept_for_a_kill_or_a_fight() {
        // a healthy one alone: no R, the W-E-Q opener
        let foes = [foe(1, 40_000.0, 0.9)];
        assert_eq!(plan(&scene(me(), &foes, &[], &[])), vec![Plan::Open(1)]);
        // an ally on him: R to join the fight
        assert_eq!(plan(&scene(me(), &foes, &[(60_000.0, 0.0)], &[]))[0], Plan::R { target: 1, full: true });
        // W or Q down: R only to finish (under R_SOLO)
        let low = [foe(1, 40_000.0, 0.5)];
        assert_eq!(plan(&scene(Me { w: false, ..me() }, &low, &[], &[])), vec![]);
        let dying = [foe(1, 40_000.0, 0.2)];
        assert_eq!(plan(&scene(Me { w: false, ..me() }, &dying, &[], &[])), vec![Plan::R { target: 1, full: false }]);
        // out of reach
        let far = [foe(1, 58_000.0, 0.2)];
        assert!(plan(&scene(me(), &far, &[], &[])).is_empty());
    }

    #[test]
    fn no_dive_into_a_crowd_or_a_tower_and_not_when_low() {
        // three round the wounded one, he alone: no R, no opener (the R rule lets one more stand there than his side)
        let crowd = [foe(1, 40_000.0, 0.5), foe(2, 50_000.0, 0.9), foe(3, 45_000.0, 0.9)];
        assert!(plan(&scene(me(), &crowd, &[], &[])).iter().all(|p| !matches!(p, Plan::R { target: 1, .. } | Plan::Open(1))));
        // two there: R yes (one more than his side), the opener no
        let pair = [foe(1, 40_000.0, 0.5), foe(2, 50_000.0, 0.9)];
        let got = plan(&scene(me(), &pair, &[], &[]));
        assert!(got.contains(&Plan::R { target: 1, full: true }) && !got.contains(&Plan::Open(1)));
        // under their tower: only the very low
        let tower = [(60_000.0, 0.0)];
        assert!(plan(&scene(me(), &[foe(1, 40_000.0, 0.5)], &[], &tower)).is_empty());
        assert_eq!(plan(&scene(me(), &[foe(1, 40_000.0, 0.2)], &[], &tower))[0], Plan::R { target: 1, full: true });
        // his own health under ENGAGE_HP: nothing offensive (the shadow's Q still goes)
        let s = Me { hp: 0.3, shadow: true, ..me() };
        assert_eq!(plan(&scene(s, &[foe(1, 40_000.0, 0.5)], &[], &[])), vec![Plan::Echo(1)]);
    }

    #[test]
    fn not_while_the_ai_walks_him_away() {
        let foes = [foe(1, 40_000.0, 0.5)];
        let mut s = scene(me(), &foes, &[], &[]);
        s.walk = Some((-30_000.0, 0.0));
        assert!(plan(&s).is_empty());
        s.walk = Some((30_000.0, 0.0));
        assert!(!plan(&s).is_empty());
    }

    #[test]
    fn the_q_slot_is_empty_while_the_mark_waits_for_w() {
        assert!(q_empty(true, false, false));
        assert!(q_empty(false, true, false));
        assert!(!q_empty(false, true, true));
        assert!(!q_empty(false, false, false));
        // no Q at all when it is not ready (the slot or its flag)
        let s = Me { q: false, w: false, r: false, shadow: true, ..me() };
        assert!(plan(&scene(s, &[foe(1, 20_000.0, 0.5)], &[], &[])).is_empty());
    }

    #[test]
    fn slots_and_kinds() {
        assert_eq!(Plan::MarkW(3).slot(), SkillSlotV1::Skill);
        assert_eq!(Plan::Open(3).slot(), SkillSlotV1::Skill);
        assert_eq!(Plan::Echo(3).slot(), SkillSlotV1::Skill2);
        assert_eq!(Plan::R { target: 3, full: false }.slot(), SkillSlotV1::Ult);
        assert_eq!(Plan::R { target: 3, full: true }.target(), 3);
        for p in [Plan::MarkW(1), Plan::Open(1), Plan::Echo(1), Plan::R { target: 1, full: true }] {
            assert!(p.kind().starts_with("combo "));
        }
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_zed.py");
        let src = std::fs::read_to_string(path).expect("build_zed.py");
        for (key, v) in [("w_range", W_RANGE as usize), ("q_range", Q_RANGE as usize), ("r_range", R_RANGE as usize),
                         ("q_dur", Q_ACT), ("r_dur", R_ACT), ("w_dur", 6)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_zed.P");
        }
        // the slot holds back Q for W after the dash (r_wq), with W's flag w_cd: the names q_empty reads
        for flag in ["\"r_wq\"", "sw(\"r_wq\", sw(\"w_cd\", q_cast, NONE), q_cast)", "flag(\"q_cd\"", "refresh(\"r_on\""] {
            assert!(src.contains(flag), "build_zed.py has no {flag}");
        }
        assert!(W_REACH < W_RANGE && Q_REACH < Q_RANGE && R_REACH < R_RANGE);
        // W's own action: the throw (w_dur) and the combo's Q strip from tick w_dur - 1 for q_dur
        assert_eq!(W_ACT, 6 - 1 + Q_ACT);
        // the flags in the order think() reads them, each one the data adds (build_zed.py names them by n(...))
        let short = ["q_cd", "w_cd", "r_wq", "r_on", "w_live", "w_live2", "r_live"];
        assert_eq!(FLAGS.map(String::from), short.map(zd));
        assert_eq!(MARK, zd("r_mark"));
        for x in short.iter().chain(&["r_mark"]) {
            assert!(zd(x).len() <= BUFF_NAME_CAP);
            assert!(src.contains(&format!("\"{x}\"")), "build_zed.py never names {x}");
        }
    }

    #[test]
    fn a_run_of_presses_nothing_took_is_counted() {
        // 11-06's logs: COMBO R on Anivia pressed t=6591..6601, 11 ticks running, never cast
        let mut p = Presses::default();
        assert_eq!(p.press("combo r", 6591), 1);
        assert_eq!((6592..=6594).map(|t| p.press("combo r", t)).last(), Some(4));
        assert!(p.n > PRESS_MAX && p.first == 6591);
        // another kind, or a gap (the cast went out and `playing` held the next ticks), starts a new run
        assert_eq!(p.press("combo w mark", 6595), 1);
        assert_eq!(p.press("combo w mark", 6630), 1);
        assert_eq!(p.press("combo w mark", 6631), 2);
    }

    #[test]
    fn the_mark_holds_while_a_marked_one_is_in_sight() {
        let marked = Foe { marked: true, ..foe(1, 10_000.0, 0.4) };
        assert!(mark_holds(true, &[foe(2, 5_000.0, 0.9), marked]));
        // the marked one died (or slipped out of sight) before the burst: r_on runs on, the W-E-Q opener is free again
        assert!(!mark_holds(true, &[foe(2, 5_000.0, 0.9)]));
        assert!(!mark_holds(false, &[marked]));
        let s = Me { r: false, mark_on: mark_holds(true, &[foe(2, 20_000.0, 0.5)]), ..me() };
        assert_eq!(plan(&scene(s, &[foe(2, 20_000.0, 0.5)], &[], &[])), vec![Plan::Open(2)]);
    }

    #[test]
    fn the_mark_is_on_from_the_dash_to_the_burst() {
        // 11-06: the burst's AddCasted ran on the landing tick (its first run) and took r_on away: 0 of 9 R-W-E-Q W's.
        // The copy arms on that run (r_set, r_on kept r_pop + 3) and bursts on the next; r_safe is a caster flag
        let copy = include_str!("../override/league_zed.data_champion").replace("\r\n", "\n");
        let at = copy.find("\"name\": \"league_zed_r_safe\"").expect("no r_safe in the copy");
        let kind = &copy[copy[..at].rfind("\"type\"").unwrap()..at];
        assert!(kind.contains("\"AddCasterBuff\""), "r_safe is not his: {kind}");
        assert_eq!(copy.matches("\"name\": \"league_zed_r_safe\"").count(), 1, "r_safe added more than once");
        let set = copy.find("\"buff_name\": \"league_zed_r_set\"").expect("the burst is not armed by r_set");
        assert!(copy[set..].find("\"name\": \"league_zed_r_on\"").is_some(), "no r_on after the arming switch");
        let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_zed.py")).unwrap();
        assert!(src.contains("flag(\"r_safe\"") && !src.contains("buff(\"r_safe\""), "build_zed.py puts r_safe on the target");
    }

    #[test]
    fn after_league_ult_press() {
        // (below the unlock gate's top one: league_unlock_guard's test reads every add-on's sources)
        assert!(PRIORITY > 100);
    }
}
