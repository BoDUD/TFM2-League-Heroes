//! 奥恩的连招（用户 2026-10-21：「有连招要做连招」）：AI 钩子 `league_ornn:combo` 替游戏的 AI 决定 Q、E 什么时候按、普攻打谁，
//! 像英雄联盟里会玩的人那样（判断在 `call`，纯计算、单元测试）。
//!
//! 1. **Q → E 撞柱**：AI 想放 E、柱子还没立、Q 好了、E 的目标（没有就最近的敌方英雄）在 Q 的射程里：先替它按 Q，朝那人立柱
//!    （裂隙朝他裂过去，柱子立在裂隙的尽头：他身后，离奥恩 `q_len`）。Q 没好就照放 E（不为等柱子把 E 憋着）。
//! 2. **柱子旁边的人**：柱子立着、E 好了、有敌方英雄在 E 的射程里而且离柱子不到 `NEAR_PILLAR`：替 AI 按 E 撞过去（撞上的那一刻
//!    柱子够近就地震）。几个人都行时挑离柱子最近的。
//! 3. **易碎优先**：AI 普攻小兵 / 野怪、或者没打易碎的英雄，而普攻够得着的地方有带易碎的敌方英雄：改打他（引爆）。
//!
//! 被控住、正在放技能（施法动作 `Animation`）或被强制位移时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。
//! 大招两段在一次施法里（主包数据：公羊回到身边就头槌），这里不管。

use mod_api_stable::*;

use super::{counted, dist, has_buff, head, n, pillars_of, pos, who, wlog, Pt, E_QUAKE_R, E_RANGE, ID, PILLAR_R, Q_RANGE};

/// 排在 league_ult_press（100）之后：引擎按优先级从小到大跑 AI 钩子，每个拿到前一个的决定。
pub const COMBO_PRIORITY: i32 = 110;
/// 敌方英雄离柱子这么近（中心距离），冲过去撞他就撞得到柱子。
pub const NEAR_PILLAR: f64 = E_QUAKE_R as f64 + PILLAR_R - 4_000.0;
/// 他的普攻射程（主包 atk_range）。
pub const ATK_RANGE: f64 = 25_000.0;

/// 奥恩自己这一 tick。
#[derive(Clone, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub r: f64,
    pub q_ready: bool,
    pub e_ready: bool,
    pub pillars: Vec<Pt>,
}

/// 一个敌方单位。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: Pt,
    pub r: f64,
    pub champion: bool,
    pub brittle: bool,
}

/// AI 这一 tick 想做的（钩子拿到的决定）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Want {
    Attack(Option<usize>),
    Move,
    Q,
    E(Option<usize>),
    R,
    Other,
}

#[derive(Clone, Debug, PartialEq)]
pub enum Call {
    /// 替 AI 按 Q：落点（目标站的地方）、目标、为什么。
    PressQ(Pt, usize, &'static str),
    /// 替 AI 按 E：目标、为什么。
    PressE(usize, &'static str),
    /// 普攻改打这个人：为什么。
    Attack(usize, &'static str),
}

fn reach(me: &Me, u: &Unit, range: f64) -> bool {
    dist(me.at, u.at) <= range + me.r + u.r
}

fn nearest<'a>(me: &Me, foes: &'a [Unit], f: impl Fn(&Unit) -> bool) -> Option<&'a Unit> {
    foes.iter().filter(|u| f(u)).min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at)))
}

/// 柱子旁边、E 够得着的敌方英雄（离柱子最近的那个）。
pub fn by_pillar<'a>(me: &Me, foes: &'a [Unit]) -> Option<&'a Unit> {
    let near = |u: &Unit| me.pillars.iter().map(|&p| dist(p, u.at)).fold(f64::INFINITY, f64::min);
    foes.iter()
        .filter(|u| u.champion && reach(me, u, E_RANGE as f64) && near(u) <= NEAR_PILLAR)
        .min_by(|a, b| near(a).total_cmp(&near(b)))
}

pub fn call(me: &Me, foes: &[Unit], want: Want) -> Option<Call> {
    // 2. a pillar stands and a champion is beside it: charge him into it
    if me.e_ready && !me.pillars.is_empty() && !matches!(want, Want::Q | Want::R) {
        if let Some(u) = by_pillar(me, foes) {
            if want != Want::E(Some(u.id)) {
                return Some(Call::PressE(u.id, "a champion beside the pillar"));
            }
            return None;
        }
    }
    // 1. E wanted with no pillar up and Q ready: the pillar first
    if let Want::E(t) = want {
        if me.pillars.is_empty() && me.q_ready {
            let aim = t.and_then(|t| foes.iter().find(|u| u.id == t))
                .filter(|u| reach(me, u, Q_RANGE as f64))
                .or_else(|| nearest(me, foes, |u| u.champion && reach(me, u, Q_RANGE as f64)));
            if let Some(u) = aim {
                return Some(Call::PressQ(u.at, u.id, "Q first: the pillar for the charge"));
            }
        }
        return None;
    }
    // 3. a Brittle champion in reach: hit him
    if let Want::Attack(t) = want {
        let on = t.and_then(|t| foes.iter().find(|u| u.id == t));
        if on.is_some_and(|u| u.brittle) {
            return None;
        }
        if let Some(u) = nearest(me, foes, |u| u.champion && u.brittle && reach(me, u, ATK_RANGE)) {
            return Some(Call::Attack(u.id, "a Brittle champion in reach"));
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
        Some(InputKindV1::Skill) => Want::Q,
        Some(InputKindV1::Skill2) => Want::E(target),
        Some(InputKindV1::Ult) => Want::R,
        _ => Want::Other,
    }
}

/// 这一 tick 的奥恩和看得见的敌人；被控住、正在放技能时 None。
fn read(sim: &StableSim<'_>, me: usize) -> Option<(Me, Vec<Unit>)> {
    let e = sim.get_entity(me)?;
    if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
        return None;
    }
    let team = e.team();
    let m = Me { at: pos(sim, me)?, r: e.radius() as f64, q_ready: ready(&e, SkillSlotV1::Skill),
                 e_ready: ready(&e, SkillSlotV1::Skill2), pillars: pillars_of(sim, me).into_iter().map(|(_, p)| p).collect() };
    let brittle = n("brittle");
    let mut foes = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || u.is_tower() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
            continue;
        }
        let id = u.id();
        foes.push(Unit { id, at: (u.pos().0 as f64, u.pos().1 as f64), r: u.radius() as f64, champion: u.is_champion(),
                         brittle: u.is_champion() && has_buff(sim, id, &brittle) });
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

/// An enemy tower this close to a champion: he stands under it (league_ult_press's `TOWER_REACH`).
pub const TOWER_REACH: f64 = 75_000.0;

/// `p` is under a living enemy tower of `me`'s.
fn under_tower(sim: &StableSim<'_>, me: usize, p: Pt) -> bool {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return false };
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).any(|u| {
        u.is_tower() && u.is_alive() && u.team() != team && {
            let (x, y) = u.pos();
            dist((x as f64, y as f64), p) <= TOWER_REACH
        }
    })
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
            let c = call(&m, &foes, want_of(base))?;
            // a charge at a champion the AI walks away from, or under an enemy tower: not (0.6.5's retreats and dives)
            if let Call::PressE(t, _) = &c {
                if foes.iter().find(|u| u.id == *t).is_some_and(|u| walking_away(base, m.at, u.at) || under_tower(&sim, me, u.at)) {
                    return None;
                }
            }
            let t = match &c {
                Call::PressQ(_, t, _) | Call::PressE(t, _) | Call::Attack(t, _) => *t,
            };
            (c, head(&sim, me), who(&sim, t))
        };
        let (input, kind, label, why) = match call {
            Call::PressQ(at, _, why) => (InputV1::action(InputKindV1::Skill, InputTargetV1::pos(at.0.max(0.0) as u64, at.1.max(0.0) as u64)),
                                         "q first", "Q FIRST", why),
            Call::PressE(t, why) => (InputV1::action(InputKindV1::Skill2, InputTargetV1::target(t)), "e pillar", "E PILLAR", why),
            Call::Attack(t, why) => (InputV1::action(InputKindV1::Attack, InputTargetV1::target(t)), "brittle", "BRITTLE", why),
        };
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(k) = counted(kind) {
            wlog(format!("{line} {label} on {on}: {why} #{k}"));
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

    fn me(pillars: Vec<Pt>, q: bool, e: bool) -> Me {
        Me { at: (0.0, 0.0), r: 6000.0, q_ready: q, e_ready: e, pillars }
    }

    fn champ(id: usize, x: f64, y: f64, brittle: bool) -> Unit {
        Unit { id, at: (x, y), r: 6000.0, champion: true, brittle }
    }

    fn minion(id: usize, x: f64) -> Unit {
        Unit { id, at: (x, 0.0), r: 4000.0, champion: false, brittle: false }
    }

    #[test]
    fn the_pillar_comes_before_the_charge() {
        let foes = [champ(1, 50_000.0, 0.0, false)];
        // E wanted, no pillar, Q ready: Q at the champion's spot
        assert!(matches!(call(&me(vec![], true, true), &foes, Want::E(Some(1))), Some(Call::PressQ((x, _), 1, _)) if x == 50_000.0));
        // Q not ready: E goes as the AI wants
        assert_eq!(call(&me(vec![], false, true), &foes, Want::E(Some(1))), None);
        // out of Q's range: E goes too
        let far = [champ(1, 120_000.0, 0.0, false)];
        assert_eq!(call(&me(vec![], true, true), &far, Want::E(Some(1))), None);
    }

    #[test]
    fn a_champion_beside_the_pillar_is_charged() {
        let foes = [champ(1, 40_000.0, 0.0, false), champ(2, 30_000.0, 30_000.0, false)];
        let m = me(vec![(45_000.0, 0.0)], false, true);
        assert_eq!(call(&m, &foes, Want::Attack(Some(2))), Some(Call::PressE(1, "a champion beside the pillar")));
        // the AI already charges him: nothing to change
        assert_eq!(call(&m, &foes, Want::E(Some(1))), None);
        // E not ready: nothing
        assert_eq!(call(&me(vec![(45_000.0, 0.0)], false, false), &foes, Want::Attack(Some(2))), None);
        // the pillar far from everyone: no press
        assert_eq!(call(&me(vec![(-200_000.0, 0.0)], false, true), &foes, Want::Attack(Some(2))), None);
    }

    #[test]
    fn brittle_champions_are_hit_first() {
        let foes = [minion(3, 20_000.0), champ(4, 25_000.0, 5_000.0, true)];
        assert_eq!(call(&me(vec![], false, false), &foes, Want::Attack(Some(3))), Some(Call::Attack(4, "a Brittle champion in reach")));
        assert_eq!(call(&me(vec![], false, false), &foes, Want::Attack(Some(4))), None);
        let out = [minion(3, 20_000.0), champ(4, 80_000.0, 0.0, true)];
        assert_eq!(call(&me(vec![], false, false), &out, Want::Attack(Some(3))), None);
    }
}
