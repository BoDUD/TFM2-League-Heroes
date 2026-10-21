//! 维克兹的连招（用户 2026-10-20：「有连招要做连招」）：AI 钩子 `league_velkoz:combo` 替游戏的 AI 按 E、Q、R 和普攻，像英雄联盟
//! 里会玩的人那样（判断在 `call`，纯计算、单元测试；数字是主包的，被动的 `params` 带过来）。主包数据里已经有连招的窗口：
//! E 击飞英雄打开 `e_combo`（窗口里放的 Q 快速飞向被控的英雄，普攻马上开裂隙），Q 打中英雄打开 `q_combo`（窗口里普攻开
//! 两道裂隙）；钩子负责按的顺序和打谁：
//!
//! 1. **E -> Q**：AI 想用 Q 打一名敌方英雄、E 好了、他在 E 的施放距离内：先替它按 E（击飞），下一下 Q 落进窗口。
//! 2. **击飞后马上 Q**：`e_combo` 开着、Q 好了：替 AI 朝施放距离内的敌方英雄按 Q（数据会把它送到被击飞的那个人身上）。
//! 3. **裂隙打英雄**：`q_combo` / `e_combo` 开着、AI 想普攻小兵或野怪、普攻距离内有敌方英雄：改成普攻那名英雄（裂隙从他
//!    朝目标撕开，打在英雄身上）。
//! 4. **层数 -> R**：R 好了、他研究着英雄（`p_res`，没有它 R 的格子是空的、按了白白进冷却）：
//!    - 施放距离内有叠了 2 层的敌方英雄：替 AI 朝他按 R（射线第一波就引爆，之后全是真实伤害）；
//!    - AI 想朝一名没被研究的英雄放 R、而施放距离内有被研究的英雄：改朝被研究的那个（层数最多、生命比例最低）。
//!
//! 被控住、正在放技能（施法动作 `Animation`）或被强制位移时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。

use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

use super::{counted, dist, head, params_of, research_name, stacks_name, vk, who, wlog, Params, Pt, ID};

/// 排在 league_ult_press（100）之后：引擎按优先级从小到大跑 AI 钩子，每个拿到前一个的决定。
pub const COMBO_PRIORITY: i32 = 110;

/// 连招按过几次（所有对局合计，诊断用）。
pub static TOTAL: AtomicUsize = AtomicUsize::new(0);

/// 维克兹自己这一 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub r: f64,
    pub q_ready: bool,
    pub e_ready: bool,
    pub r_ready: bool,
    /// E 击飞了英雄（`e_combo`）、Q 打中了英雄（`q_combo`）、他研究着英雄（`p_res`）。
    pub e_combo: bool,
    pub q_combo: bool,
    pub p_res: bool,
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
    /// 他身上这个维克兹的层数、被他研究着。
    pub stacks: usize,
    pub studied: bool,
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
    Attack(usize, &'static str, &'static str),
    PressQ(usize, &'static str, &'static str),
    PressE(usize, &'static str, &'static str),
    PressR(usize, &'static str, &'static str),
}

fn within(me: &Me, u: &Unit, reach: usize) -> bool {
    dist(me.at, u.at) <= reach as f64 + me.r + u.r
}

/// `reach` 内最近的敌方英雄。
fn nearest<'a>(me: &Me, foes: &'a [Unit], reach: usize) -> Option<&'a Unit> {
    foes.iter()
        .filter(|u| u.champion && within(me, u, reach))
        .min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at)))
}

/// R 先射谁：被研究的英雄里层数最多、生命比例最低的。
fn best_studied<'a>(me: &Me, foes: &'a [Unit], reach: usize) -> Option<&'a Unit> {
    foes.iter()
        .filter(|u| u.champion && u.studied && within(me, u, reach))
        .min_by(|a, b| b.stacks.cmp(&a.stacks).then(a.share().total_cmp(&b.share())))
}

pub fn call(me: &Me, foes: &[Unit], p: &Params, want: Want) -> Option<Call> {
    // 4a. two stacks on a champion in reach: the ray bursts them at once and burns true damage after
    if me.r_ready && me.p_res && !matches!(want, Want::R(_)) {
        if let Some(u) = foes.iter().find(|u| u.champion && u.stacks >= 2 && within(me, u, p.r_range)) {
            return Some(Call::PressR(u.id, "r on stacks", "R ON STACKS: a champion with two stacks - the ray bursts him"));
        }
    }
    match want {
        // 4b. the ray at a researched champion rather than a fresh one
        Want::R(Some(t)) if me.p_res => {
            let target = foes.iter().find(|u| u.id == t)?;
            if !target.studied {
                if let Some(u) = best_studied(me, foes, p.r_range) {
                    return Some(Call::PressR(u.id, "r researched", "R RESEARCHED: the ray at the champion he studied"));
                }
            }
            None
        }
        // 1. E -> Q: the knock-up first, the bolt into its window
        Want::Q(Some(t)) => {
            let target = foes.iter().find(|u| u.id == t)?;
            if target.champion && me.e_ready && !me.e_combo && within(me, target, p.e_range) {
                return Some(Call::PressE(t, "e first", "E FIRST: the knock-up before the bolt"));
            }
            None
        }
        // 3. the rift onto the champion the combo caught
        Want::Attack(Some(t)) if me.q_combo || me.e_combo => {
            let target = foes.iter().find(|u| u.id == t)?;
            if target.champion {
                return None;
            }
            nearest(me, foes, p.atk_range).map(|u| Call::Attack(u.id, "rift on champion", "RIFT: the attack after the combo goes to the champion"))
        }
        _ => {
            // 2. knocked up: the bolt follows at once
            if me.e_combo && me.q_ready && !matches!(want, Want::Q(_) | Want::E(_) | Want::R(_)) {
                return nearest(me, foes, p.q_range).map(|u| Call::PressQ(u.id, "q after e", "Q AFTER E: the bolt at the airborne champion"));
            }
            None
        }
    }
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

/// 这一 tick的维克兹和看得见的敌人；被控住、正在放技能时 None。
fn read(sim: &StableSim<'_>, me: usize) -> Option<(Me, Vec<Unit>)> {
    let e = sim.get_entity(me)?;
    if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
        return None;
    }
    let has = |name: &str| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name);
    let (x, y) = e.pos();
    let team = e.team();
    let m = Me { at: (x as f64, y as f64), r: e.radius() as f64, q_ready: ready(&e, SkillSlotV1::Skill),
                 e_ready: ready(&e, SkillSlotV1::Skill2), r_ready: ready(&e, SkillSlotV1::Ult),
                 e_combo: has(&vk("e_combo")), q_combo: has(&vk("q_combo")), p_res: has(&vk("p_res")) };
    let (stacks, research) = (stacks_name(me), research_name(me));
    let mut foes = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || u.is_tower() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
            continue;
        }
        let (hp, max) = u.hp();
        let (x, y) = u.pos();
        let buffs: Vec<_> = (0..u.buff_count()).filter_map(|j| u.buff_at(j)).collect();
        foes.push(Unit { id: u.id(), at: (x as f64, y as f64), r: u.radius() as f64, hp, max, champion: u.is_champion(),
                         stacks: buffs.iter().filter(|b| b.name() == stacks).count(),
                         studied: buffs.iter().any(|b| b.name() == research) });
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
            // the channel at a champion the AI walks away from (a retreat, 0.6.5's disperse): not
            if let Call::PressR(t, ..) = &c {
                if foes.iter().find(|u| u.id == *t).is_some_and(|u| walking_away(base, m.at, u.at)) {
                    return None;
                }
            }
            let t = match &c {
                Call::Attack(t, ..) | Call::PressQ(t, ..) | Call::PressE(t, ..) | Call::PressR(t, ..) => *t,
            };
            (c, head(&sim, me), who(&sim, t))
        };
        let (kind, slot, t, kind_log, why) = match call {
            Call::Attack(t, k, w) => ("attack", InputKindV1::Attack, t, k, w),
            Call::PressQ(t, k, w) => ("q", InputKindV1::Skill, t, k, w),
            Call::PressE(t, k, w) => ("e", InputKindV1::Skill2, t, k, w),
            Call::PressR(t, k, w) => ("r", InputKindV1::Ult, t, k, w),
        };
        let input = InputV1::action(slot, InputTargetV1::target(t));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        TOTAL.fetch_add(1, Ordering::Relaxed);
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
        Me { at: (0.0, 0.0), r: 3000.0, q_ready: true, e_ready: true, r_ready: true, e_combo: false, q_combo: false,
             p_res: false }
    }

    fn champ(id: usize, x: f64, stacks: usize, studied: bool) -> Unit {
        Unit { id, at: (x, 0.0), r: 3000.0, hp: 800, max: 1000, champion: true, stacks, studied }
    }

    fn minion(id: usize, x: f64) -> Unit {
        Unit { id, at: (x, 0.0), r: 3000.0, hp: 300, max: 300, champion: false, stacks: 0, studied: false }
    }

    #[test]
    fn e_goes_before_the_bolt() {
        let p = Params::default();
        let foes = [champ(1, 50_000.0, 0, false)];
        assert!(matches!(call(&me(), &foes, &p, Want::Q(Some(1))), Some(Call::PressE(1, ..))));
        let mut cool = me();
        cool.e_ready = false;
        assert_eq!(call(&cool, &foes, &p, Want::Q(Some(1))), None);
        // out of E's reach, or a minion: Q goes through
        assert_eq!(call(&me(), &[champ(1, 84_000.0, 0, false)], &p, Want::Q(Some(1))), None);
        assert_eq!(call(&me(), &[minion(5, 40_000.0)], &p, Want::Q(Some(5))), None);
    }

    #[test]
    fn the_bolt_follows_the_knock_up() {
        let p = Params::default();
        let mut up = me();
        up.e_combo = true;
        let foes = [minion(5, 20_000.0), champ(1, 60_000.0, 1, true)];
        assert!(matches!(call(&up, &foes, &p, Want::Attack(Some(1))), None));
        assert!(matches!(call(&up, &foes, &p, Want::Move), Some(Call::PressQ(1, ..))));
        up.q_ready = false;
        assert_eq!(call(&up, &foes, &p, Want::Move), None);
    }

    #[test]
    fn the_rift_goes_onto_the_champion() {
        let p = Params::default();
        let mut slowed = me();
        slowed.q_combo = true;
        let foes = [minion(5, 20_000.0), champ(1, 40_000.0, 1, true)];
        assert!(matches!(call(&slowed, &foes, &p, Want::Attack(Some(5))), Some(Call::Attack(1, ..))));
        // no window: the minion
        assert_eq!(call(&me(), &foes, &p, Want::Attack(Some(5))), None);
        // the champion out of attack range: the minion
        assert_eq!(call(&slowed, &[minion(5, 20_000.0), champ(1, 80_000.0, 1, true)], &p, Want::Attack(Some(5))), None);
    }

    #[test]
    fn the_ray_waits_for_research() {
        let p = Params::default();
        let foes = [champ(1, 60_000.0, 2, true)];
        // no research: the slot is empty - never pressed
        assert_eq!(call(&me(), &foes, &p, Want::Move), None);
        let mut studied = me();
        studied.p_res = true;
        assert!(matches!(call(&studied, &foes, &p, Want::Move), Some(Call::PressR(1, ..))));
        // the AI's R at a fresh champion goes to the studied one
        let two = [champ(2, 30_000.0, 0, false), champ(1, 60_000.0, 1, true)];
        assert!(matches!(call(&studied, &two, &p, Want::R(Some(2))), Some(Call::PressR(1, ..))));
        assert_eq!(call(&studied, &two, &p, Want::R(Some(1))), None);
    }
}
