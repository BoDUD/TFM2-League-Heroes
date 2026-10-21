//! 梅尔的连招（用户 2026-10-20：「有连招要做连招」）：AI 钩子 `league_mel:combo` 替游戏的 AI 按 Q、E、R，像英雄联盟里会玩的
//! 人那样（判断在 `call`，纯计算、单元测试；数字是主包的，被动的 `params` 带过来）。
//!
//! 1. **E → Q**：AI 想用 Q 砸一个敌方英雄、E 好了、那名英雄在 E 的施放距离内：先替它按 E（阳炎涡旋的中心禁锢他）。
//! 2. **禁锢住了接 Q**：E 的法球禁锢了英雄（她身上开着 `e_combo`）、Q 好了、`q_range` 内有被禁锢（`e_bound`）的敌方英雄：
//!    替 AI 朝他按 Q——主包数据里这时的 Q 快速落在被控住的英雄身上，六次爆炸全打在他身上。
//! 3. **残影 → R**：鎏金蚀日打所有带残影的敌方英雄，伤害按层数算，所以 R 要等残影叠起来：
//!    - **R KILL**：有一名敌方英雄身上的残影（本包的 `m_mark` 层数 × (`r_st` + `r_ratio`% 法强)）够打掉他的生命 + 护盾：按 R；
//!    - **R MANY**：两名以上敌方英雄的残影都够打掉他们 `MANY_SHARE` 的生命：按 R；
//!    - **R HELD**：AI 自己想按 R，但两样都不够：不放，改成普攻它的目标（打不到就走过去），残影接着叠。
//!    R 的施放要点一名 `r_range` 内的敌方英雄（伤害是全图的，点谁都一样），选离她最近的。
//!
//! 被控住、正在放技能（施法动作 `Animation`）或被强制位移时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。

use mod_api_stable::*;

use super::{count_buff, counted, head, params_of, sn, stacks_worth, who, wlog, Params, ID};

/// 排在 league_ult_press（100）之后：引擎按优先级从小到大跑 AI 钩子，每个拿到前一个的决定。
pub const COMBO_PRIORITY: i32 = 110;
/// R MANY：两名以上英雄的残影都够打掉他们这么多的生命。
pub const MANY_SHARE: f64 = 0.4;
/// R HELD 的日志隔多久写一条。
pub const HOLD_LOG_EVERY: usize = 120;

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 梅尔自己这一 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub r: f64,
    pub hp: f64,
    pub ap: usize,
    pub q_ready: bool,
    pub e_ready: bool,
    pub r_ready: bool,
    /// E 的法球刚禁锢了英雄（`e_combo`）。
    pub e_combo: bool,
}

/// 一个敌方单位。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: Pt,
    pub r: f64,
    pub hp: usize,
    pub shield: usize,
    pub champion: bool,
    /// 本包的残影层数（`m_mark`）。
    pub stacks: usize,
    /// 被 E 禁锢着（`e_bound`）。
    pub rooted: bool,
}

/// AI 这一 tick 想做的（钩子拿到的决定）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Want {
    Attack(Option<usize>),
    Move,
    Q(Option<usize>),
    E(Option<usize>),
    R(Option<usize>),
    Other,
}

/// 替 AI 按的：哪个格子、打谁、为什么（日志的种类和说明）；或者不放 R、改成普攻。
#[derive(Clone, Debug, PartialEq)]
pub enum Call {
    PressQ(usize, &'static str, &'static str),
    PressE(usize, &'static str, &'static str),
    PressR(usize, &'static str, &'static str),
    HoldR(Option<usize>),
}

fn within(me: &Me, u: &Unit, reach: usize) -> bool {
    dist(me.at, u.at) <= reach as f64 + me.r + u.r
}

fn worth(me: &Me, u: &Unit, p: &Params) -> usize {
    stacks_worth(u.stacks, p.r_st, p.r_ratio, me.ap)
}

/// R 该不该放：(为什么, 日志的种类)；不该是 None。
pub fn r_reason(me: &Me, foes: &[Unit], p: &Params) -> Option<(&'static str, &'static str)> {
    let champs = foes.iter().filter(|u| u.champion && u.stacks > 0);
    if champs.clone().any(|u| worth(me, u, p) >= u.hp + u.shield) {
        return Some(("r kill", "R KILL: the stacks on a champion are worth his health"));
    }
    let many = champs.filter(|u| worth(me, u, p) as f64 >= MANY_SHARE * (u.hp + u.shield) as f64).count();
    (many >= 2).then_some(("r many", "R MANY: two champions carry stacks worth a good share of their health"))
}

/// R 点谁：`r_range` 内最近的敌方英雄。
fn r_target(me: &Me, foes: &[Unit], p: &Params) -> Option<usize> {
    foes.iter()
        .filter(|u| u.champion && within(me, u, p.r_range))
        .min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at)))
        .map(|u| u.id)
}

pub fn call(me: &Me, foes: &[Unit], p: &Params, want: Want) -> Option<Call> {
    // 3. stacks -> R
    if me.r_ready {
        if let (Some((kind, why)), Some(t)) = (r_reason(me, foes, p), r_target(me, foes, p)) {
            return Some(Call::PressR(t, kind, why));
        }
        if let Want::R(t) = want {
            return Some(Call::HoldR(t));
        }
    }
    // 2. the orb rooted a champion: the volley on him
    if me.q_ready && me.e_combo {
        if let Some(u) = foes.iter().find(|u| u.champion && u.rooted && within(me, u, p.q_range)) {
            return Some(Call::PressQ(u.id, "q on root", "Q ON ROOT: the volley on the champion the orb rooted"));
        }
    }
    // 1. E before Q at a champion
    if let Want::Q(Some(t)) = want {
        let target = foes.iter().find(|u| u.id == t)?;
        if target.champion && me.e_ready && within(me, target, p.e_range) {
            return Some(Call::PressE(t, "e first", "E FIRST: the orb roots him before the volley"));
        }
    }
    None
}

// ===================== 游戏里 =====================

/// 放不出技能的控制，和正在放技能 / 被强制位移。
const STOP: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
    CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

fn ready(e: &StableEntity<'_, '_>, slot: SkillSlotV1) -> bool {
    e.cooldown(slot).is_some_and(|c| c.unlocked && c.remaining == 0)
}

fn want_of(base: Option<InputV1>) -> Want {
    let Some(b) = base else { return Want::Move };
    let target = (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id);
    match InputKindV1::from_code(b.kind) {
        Some(InputKindV1::Attack) => Want::Attack(target),
        Some(InputKindV1::Move) => Want::Move,
        Some(InputKindV1::Skill) => Want::Q(target),
        Some(InputKindV1::Skill2) => Want::E(target),
        Some(InputKindV1::Ult) => Want::R(target),
        _ => Want::Other,
    }
}

/// 这一 tick的梅尔和看得见的敌人；被控住、正在放技能时 None。
fn read(sim: &StableSim<'_>, me: usize) -> Option<(Me, Vec<Unit>)> {
    let e = sim.get_entity(me)?;
    if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
        return None;
    }
    let combo = sn("e_combo");
    let (mark, bound) = (sn("m_mark"), sn("e_bound"));
    let (hp, max) = e.hp();
    let (x, y) = e.pos();
    let team = e.team();
    let m = Me { at: (x as f64, y as f64), r: e.radius() as f64, hp: if max > 0 { hp as f64 / max as f64 } else { 1.0 },
                 ap: e.stat().magic_power, q_ready: ready(&e, SkillSlotV1::Skill),
                 e_ready: ready(&e, SkillSlotV1::Skill2), r_ready: ready(&e, SkillSlotV1::Ult),
                 e_combo: count_buff(&e, &combo) > 0 };
    let mut foes = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || u.is_tower() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
            continue;
        }
        let (hp, _) = u.hp();
        let (x, y) = u.pos();
        let champion = u.is_champion();
        let (stacks, rooted) = if champion { (count_buff(&u, &mark), count_buff(&u, &bound) > 0) } else { (0, false) };
        foes.push(Unit { id: u.id(), at: (x as f64, y as f64), r: u.radius() as f64, hp, shield: u.shield(), champion,
                         stacks, rooted });
    }
    Some((m, foes))
}

/// The AI is still recalling (game 0.6.5 decides when to go home and buy; the combos leave it be): its last order was a
/// Return - it orders only on its judgement ticks, again a Return while the recall lasts, nothing in between - and any
/// other order ends it (league_ult_press 0.5.0's rule).
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// How much farther from a champion the AI's walk must end to be a retreat (league_ult_press's `HOLD_AWAY`).
pub const AWAY: f64 = 10_000.0;

/// The AI walks away from `to` this tick (a retreat, a disperse from a lost objective): its Move ends more than `AWAY`
/// farther from it than he stands now.
pub fn walking_away(base: Option<InputV1>, me: Pt, to: Pt) -> bool {
    base.is_some_and(|b| b.kind == InputKindV1::Move.code() && dist((b.x as f64, b.y as f64), to) > dist(me, to) + AWAY)
}

#[derive(Clone, Default)]
pub struct Combo {
    /// the AI is recalling (`still_recalling`)
    recalling: bool,
    last_hold: Option<usize>,
}

impl StablePlayerAi for Combo {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:combo")
    }

    fn priority(&self) -> i32 {
        COMBO_PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        // game 0.6.5's AI decides when to recall (and buy): nothing pressed while it does
        self.recalling = still_recalling(self.recalling, base);
        if self.recalling {
            return None;
        }
        let player = ctx.player_id();
        let (call, line, tick, stacks) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?.id();
            let (m, foes) = read(&sim, me)?;
            let p = params_of(&sim, me);
            let c = call(&m, &foes, &p, want_of(base))?;
            let t = match &c {
                Call::PressQ(t, ..) | Call::PressE(t, ..) | Call::PressR(t, ..) => Some(*t),
                Call::HoldR(t) => *t,
            };
            let stacks: Vec<String> = foes.iter().filter(|u| u.champion && u.stacks > 0)
                .map(|u| format!("{} {}x (hp {})", who(&sim, u.id), u.stacks, u.hp)).collect();
            let on = t.map_or_else(|| "-".to_string(), |t| who(&sim, t));
            (c, format!("{} [hp {:.0}%] on {on}", head(&sim, me), m.hp * 100.0), sim.tick(), stacks.join(", "))
        };
        let (slot, t, kind_log, why) = match call {
            Call::PressQ(t, k, w) => (InputKindV1::Skill, t, k, w),
            Call::PressE(t, k, w) => (InputKindV1::Skill2, t, k, w),
            Call::PressR(t, k, w) => (InputKindV1::Ult, t, k, w),
            Call::HoldR(t) => {
                if self.last_hold.is_none_or(|t0| tick >= t0 + HOLD_LOG_EVERY) {
                    self.last_hold = Some(tick);
                    if let Some(n) = counted("r held") {
                        wlog(format!("{line} R HELD: the stacks are not worth it yet [{stacks}] - attacking instead #{n}"));
                    }
                }
                let t = t?;
                let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                return ctx.is_valid_input(&attack).then_some(attack);
            }
        };
        let input = InputV1::action(slot, InputTargetV1::target(t));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(n) = counted(kind_log) {
            wlog(format!("{line} {why} [{stacks}] #{n}"));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_recall_or_a_retreat_is_the_ais() {
        // game 0.6.5: a recall lasts over the ticks without an order; a walk ending far from the target is a retreat
        assert!(still_recalling(false, Some(InputV1::return_home())) && still_recalling(true, None));
        assert!(!still_recalling(true, Some(InputV1::move_to(0, 0))) && !still_recalling(false, None));
        assert!(walking_away(Some(InputV1::move_to(0, 0)), (20_000.0, 0.0), (60_000.0, 0.0)));
        assert!(!walking_away(Some(InputV1::move_to(50_000, 0)), (20_000.0, 0.0), (60_000.0, 0.0)));
        assert!(!walking_away(None, (20_000.0, 0.0), (60_000.0, 0.0)));
    }

    fn me() -> Me {
        Me { at: (0.0, 0.0), r: 3000.0, hp: 1.0, ap: 200, q_ready: true, e_ready: true, r_ready: true, e_combo: false }
    }

    fn champ(id: usize, x: f64, hp: usize, stacks: usize) -> Unit {
        Unit { id, at: (x, 0.0), r: 3000.0, hp, shield: 0, champion: true, stacks, rooted: false }
    }

    fn minion(id: usize, x: f64) -> Unit {
        Unit { id, at: (x, 0.0), r: 2000.0, hp: 300, shield: 0, champion: false, stacks: 0, rooted: false }
    }

    #[test]
    fn r_waits_for_the_stacks() {
        let p = Params::default();
        // 20 + 8% of 200 = 36 a stack: 10 stacks = 360
        let kill = [champ(1, 40_000.0, 250, 10)];
        assert!(matches!(call(&me(), &kill, &p, Want::Move), Some(Call::PressR(1, "r kill", _))));
        // not enough: the AI's R is held
        let few = [champ(1, 40_000.0, 900, 3)];
        assert_eq!(call(&me(), &few, &p, Want::R(Some(1))), Some(Call::HoldR(Some(1))));
        assert_eq!(call(&me(), &few, &p, Want::Move), None);
        // two champions worth 40% of their health
        let two = [champ(1, 40_000.0, 600, 10), champ(2, 50_000.0, 500, 8)];
        assert!(matches!(call(&me(), &two, &p, Want::Move), Some(Call::PressR(1, "r many", _))));
        // a killable champion far away: R points at the nearest one in range
        let far = [champ(1, 300_000.0, 100, 10), champ(2, 30_000.0, 2000, 0)];
        assert!(matches!(call(&me(), &far, &p, Want::Move), Some(Call::PressR(2, "r kill", _))));
        // nobody in R's range: nothing to point at, the AI goes on
        let none = [champ(1, 300_000.0, 100, 10)];
        assert_eq!(call(&me(), &none, &p, Want::Move), None);
    }

    #[test]
    fn e_goes_before_q_at_a_champion() {
        let p = Params::default();
        let mut cool = me();
        cool.r_ready = false;
        let foes = [champ(1, 60_000.0, 900, 0)];
        assert!(matches!(call(&cool, &foes, &p, Want::Q(Some(1))), Some(Call::PressE(1, ..))));
        // E cooling: Q goes through
        cool.e_ready = false;
        assert_eq!(call(&cool, &foes, &p, Want::Q(Some(1))), None);
        // a minion: no E for it
        let mut ready = me();
        ready.r_ready = false;
        let wave = [minion(5, 30_000.0)];
        assert_eq!(call(&ready, &wave, &p, Want::Q(Some(5))), None);
    }

    #[test]
    fn q_follows_the_root() {
        let p = Params::default();
        let mut m = me();
        m.r_ready = false;
        m.e_combo = true;
        let mut rooted = champ(1, 50_000.0, 900, 1);
        rooted.rooted = true;
        let foes = [minion(5, 20_000.0), rooted];
        assert!(matches!(call(&m, &foes, &p, Want::Attack(Some(5))), Some(Call::PressQ(1, "q on root", _))));
        m.e_combo = false;
        assert_eq!(call(&m, &foes, &p, Want::Attack(Some(5))), None);
    }
}
