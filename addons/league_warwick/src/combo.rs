//! 沃里克的连招（用户 2026-10-20：「有连招要做连招」）：AI 钩子 `league_warwick:combo` 替游戏的 AI 按 E、Q、R，像英雄联盟里
//! 会玩的人那样（判断在 `call`，纯计算、单元测试；数字是主包的，被动的 `params` 带过来）。
//!
//! 1. **R → Q**：无尽束缚压住英雄、连抓三下（这期间他在 `ult_hold` 动作里，钩子不动），动作一结束、Q 好了，就替 AI 朝那名
//!    英雄（`q_range` 内生命比例最低的敌方英雄）按 Q——英雄联盟里压制完马上接一口撕咬。R 放出后 `r_dur` + `r_sup` +
//!    `AFTER_R` tick 内算。
//! 2. **E → Q**：AI 想用 Q 扑一个敌方英雄、E 好了、远祖嗥叫没开着、那名英雄在 E 的施放距离内：先替它按 E（减伤开着扑进去）；
//!    下一下 AI 再按 Q，主包数据里 Q 咬中时远祖嗥叫开着就立刻嚎叫——恐惧落在他扑到的地方（英雄联盟里 E、Q、再按 E）。
//! 3. **鲜血追猎**：
//!    - R 好了、`r_cast` 内有生命低于 `w_quarter`% 的敌方英雄、往他扑过去路上第一个英雄就是他：替 AI 按 R（追残血）；
//!    - AI 想用 Q 咬小兵 / 野怪，而 `q_range` 内有生命低于 `w_half`% 的敌方英雄：改成咬那名英雄。
//!
//! 被控住、正在放技能（施法动作 `Animation`）或被强制位移时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。

use mod_api_stable::*;

use super::{counted, head, params_of, sn, who, wlog, Params, ID};

/// 排在 league_ult_press（100）之后：引擎按优先级从小到大跑 AI 钩子，每个拿到前一个的决定。
pub const COMBO_PRIORITY: i32 = 110;
/// R 的动作和压制结束后这么多 tick 内还算「刚放完 R」（R → Q）。
pub const AFTER_R: usize = 40;

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 沃里克自己这一 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub r: f64,
    pub hp: f64,
    pub q_ready: bool,
    pub e_ready: bool,
    pub r_ready: bool,
    /// 远祖嗥叫的减伤开着（`e_on`）。
    pub e_on: bool,
    /// R 放出后过了几 tick（R 在冷却时 = 冷却总长 - 剩余；R 好了是 None）。
    pub since_r: Option<usize>,
}

/// 一个敌方单位。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: Pt,
    pub r: f64,
    pub hp: usize,
    pub max: usize,
    pub champion: bool,
}

impl Unit {
    pub fn share(&self) -> f64 {
        if self.max == 0 {
            1.0
        } else {
            self.hp as f64 / self.max as f64
        }
    }
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

/// 替 AI 按的：哪个格子、打谁、为什么（日志的种类和说明）。
#[derive(Clone, Debug, PartialEq)]
pub enum Call {
    PressQ(usize, &'static str, &'static str),
    PressE(usize, &'static str, &'static str),
    PressR(usize, &'static str, &'static str),
}

fn within(me: &Me, u: &Unit, reach: usize) -> bool {
    dist(me.at, u.at) <= reach as f64 + me.r + u.r
}

/// `reach` 内生命比例最低的敌方英雄（比例低于 `below` 才算）。
fn weakest<'a>(me: &Me, foes: &'a [Unit], reach: usize, below: f64) -> Option<&'a Unit> {
    foes.iter()
        .filter(|u| u.champion && within(me, u, reach) && u.share() < below)
        .min_by(|a, b| a.share().total_cmp(&b.share()))
}

/// R 往 `toward` 扑，停在谁身上：从他到 `toward` 这条线上、离线不超过半宽加半径、沿线最近的敌方英雄。
pub fn first_on_line(me: &Me, toward: Pt, champs: &[Unit], p: &Params) -> Option<Unit> {
    let d = dist(me.at, toward);
    if d < 1.0 {
        return None;
    }
    let (ux, uy) = ((toward.0 - me.at.0) / d, (toward.1 - me.at.1) / d);
    champs
        .iter()
        .filter(|c| c.champion)
        .filter_map(|c| {
            let (vx, vy) = (c.at.0 - me.at.0, c.at.1 - me.at.1);
            let along = vx * ux + vy * uy;
            let off = (vx * uy - vy * ux).abs();
            (along >= 0.0 && along <= p.r_range as f64 + c.r && off <= p.r_w as f64 + c.r).then_some((along, *c))
        })
        .min_by(|a, b| a.0.total_cmp(&b.0))
        .map(|(_, c)| c)
}

pub fn call(me: &Me, foes: &[Unit], p: &Params, want: Want) -> Option<Call> {
    let all = 2.0; // any share
    // 1. R -> Q: the suppression is over, the bite follows
    if me.q_ready && me.since_r.is_some_and(|t| t >= p.r_dur && t <= p.r_dur + p.r_sup + AFTER_R) {
        if let Some(u) = weakest(me, foes, p.q_range, all) {
            return Some(Call::PressQ(u.id, "r then q", "R THEN Q: the suppression is over - the bite follows"));
        }
    }
    // 3a. the hunt: R onto a champion under w_quarter, the first on the leap's line
    if me.r_ready && !matches!(want, Want::R(_) | Want::E(_)) {
        let low = p.w_quarter as f64 / 100.0;
        if let Some(u) = weakest(me, foes, p.r_cast, low) {
            if first_on_line(me, u.at, foes, p).is_some_and(|f| f.id == u.id) {
                return Some(Call::PressR(u.id, "r hunt", "R HUNT: a champion under a quarter of his health"));
            }
        }
    }
    if let Want::Q(Some(t)) = want {
        let target = foes.iter().find(|u| u.id == t)?;
        // 2. E -> Q: the guard up before the leap at a champion
        if target.champion && me.e_ready && !me.e_on && within(me, target, p.e_range) {
            return Some(Call::PressE(t, "e first", "E FIRST: the guard up before the bite (it howls as it lands)"));
        }
        // 3b. the hunt: the bite goes to a wounded champion instead of a minion or a monster
        if !target.champion {
            if let Some(u) = weakest(me, foes, p.q_range, p.w_half as f64 / 100.0) {
                return Some(Call::PressQ(u.id, "q to prey", "Q TO PREY: a wounded champion instead of a minion or monster"));
            }
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

/// 这一 tick 的沃里克和看得见的敌人；被控住、正在放技能时 None。
fn read(sim: &StableSim<'_>, me: usize) -> Option<(Me, Vec<Unit>)> {
    let e = sim.get_entity(me)?;
    if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
        return None;
    }
    let e_on = sn("e_on");
    let since_r = e.cooldown(SkillSlotV1::Ult)
        .filter(|c| c.unlocked && c.remaining > 0)
        .map(|c| c.cooltime.saturating_sub(c.remaining));
    let (hp, max) = e.hp();
    let (x, y) = e.pos();
    let team = e.team();
    let m = Me { at: (x as f64, y as f64), r: e.radius() as f64, hp: if max > 0 { hp as f64 / max as f64 } else { 1.0 },
                 q_ready: ready(&e, SkillSlotV1::Skill), e_ready: ready(&e, SkillSlotV1::Skill2),
                 r_ready: ready(&e, SkillSlotV1::Ult),
                 e_on: (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == e_on), since_r };
    let mut foes = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || u.is_tower() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
            continue;
        }
        let (hp, max) = u.hp();
        let (x, y) = u.pos();
        foes.push(Unit { id: u.id(), at: (x as f64, y as f64), r: u.radius() as f64, hp, max, champion: u.is_champion() });
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
        let (call, line, on) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?.id();
            let (m, foes) = read(&sim, me)?;
            let p = params_of(&sim, me);
            let c = call(&m, &foes, &p, want_of(base))?;
            // the leap at a champion the AI walks away from (a retreat, 0.6.5's disperse): not
            if let Call::PressR(t, ..) = &c {
                if foes.iter().find(|u| u.id == *t).is_some_and(|u| walking_away(base, m.at, u.at)) {
                    return None;
                }
            }
            let t = match &c {
                Call::PressQ(t, ..) | Call::PressE(t, ..) | Call::PressR(t, ..) => *t,
            };
            (c, format!("{} [hp {:.0}%]", head(&sim, me), m.hp * 100.0), who(&sim, t))
        };
        let (kind, slot, t, kind_log, why) = match call {
            Call::PressQ(t, k, w) => ("q", InputKindV1::Skill, t, k, w),
            Call::PressE(t, k, w) => ("e", InputKindV1::Skill2, t, k, w),
            Call::PressR(t, k, w) => ("r", InputKindV1::Ult, t, k, w),
        };
        let input = InputV1::action(slot, InputTargetV1::target(t));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(n) = counted(kind_log) {
            wlog(format!("{line} {why} - {kind} on {on} #{n}"));
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
        Me { at: (0.0, 0.0), r: 3000.0, hp: 1.0, q_ready: true, e_ready: true, r_ready: true, e_on: false, since_r: None }
    }

    fn champ(id: usize, x: f64, y: f64, hp: usize) -> Unit {
        Unit { id, at: (x, y), r: 3000.0, hp, max: 1000, champion: true }
    }

    fn camp(id: usize, x: f64) -> Unit {
        Unit { id, at: (x, 0.0), r: 4000.0, hp: 1200, max: 1200, champion: false }
    }

    #[test]
    fn e_goes_up_before_the_bite_at_a_champion() {
        let p = Params::default();
        let foes = [champ(1, 30_000.0, 0.0, 900)];
        assert!(matches!(call(&me(), &foes, &p, Want::Q(Some(1))), Some(Call::PressE(1, ..))));
        // the guard already up: Q goes through (and howls as it lands)
        let mut on = me();
        on.e_on = true;
        assert_eq!(call(&on, &foes, &p, Want::Q(Some(1))), None);
        // E cooling: Q goes through
        let mut cool = me();
        cool.e_ready = false;
        assert_eq!(call(&cool, &foes, &p, Want::Q(Some(1))), None);
        // out of E's reach: Q goes through
        let far = [champ(1, 45_000.0, 0.0, 900)];
        assert_eq!(call(&me(), &far, &p, Want::Q(Some(1))), None);
        // a camp: no E for it
        let jungle = [camp(5, 20_000.0)];
        assert_eq!(call(&me(), &jungle, &p, Want::Q(Some(5))), None);
    }

    #[test]
    fn q_follows_the_suppression() {
        let p = Params::default();
        let foes = [champ(1, 15_000.0, 0.0, 500), camp(5, 10_000.0)];
        let mut after = me();
        after.r_ready = false;
        after.since_r = Some(p.r_dur + p.r_sup + 5);
        assert!(matches!(call(&after, &foes, &p, Want::Attack(Some(5))), Some(Call::PressQ(1, ..))));
        // long after: nothing
        after.since_r = Some(p.r_dur + p.r_sup + AFTER_R + 1);
        assert_eq!(call(&after, &foes, &p, Want::Attack(Some(5))), None);
    }

    #[test]
    fn the_hunt_leaps_at_the_weak() {
        let p = Params::default();
        let low = [champ(1, 60_000.0, 0.0, 200)];
        assert!(matches!(call(&me(), &low, &p, Want::Move), Some(Call::PressR(1, ..))));
        // healthy: nothing
        let full = [champ(1, 60_000.0, 0.0, 900)];
        assert_eq!(call(&me(), &full, &p, Want::Move), None);
        // a healthy champion in front of the weak one on the line: the leap would stop on him - no
        let shield = [champ(2, 30_000.0, 0.0, 900), champ(1, 60_000.0, 0.0, 200)];
        assert_eq!(call(&me(), &shield, &p, Want::Move), None);
    }

    #[test]
    fn the_bite_goes_to_a_wounded_champion() {
        let p = Params::default();
        let mut cool = me();
        cool.r_ready = false;
        let foes = [camp(5, 20_000.0), champ(1, 30_000.0, 0.0, 400)];
        assert!(matches!(call(&cool, &foes, &p, Want::Q(Some(5))), Some(Call::PressQ(1, ..))));
        let healthy = [camp(5, 20_000.0), champ(1, 30_000.0, 0.0, 800)];
        assert_eq!(call(&cool, &healthy, &p, Want::Q(Some(5))), None);
    }
}
