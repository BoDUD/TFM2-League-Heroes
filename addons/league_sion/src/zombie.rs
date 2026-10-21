//! 亡灵不回城（用户 2026-10-21：「还有塞恩的僵尸 死了还能跑回城的？」）：AI 钩子 `league_sion:zombie`。
//!
//! 死亡荣耀把他复活成亡灵后，生命每 tick 均匀流失（lib.rs `Glory`），游戏的 AI 看到生命一路往下掉，就照平时残血的做法
//! 往回跑、回城——英雄联盟里亡灵塞恩不会回城，只会扑向敌人打到倒下。所以他身上有 `league_sion_p_zombie` 时，AI 要
//! **回城**（`Return`）或**走动**（`Move`：撤退也是走动）就改成**普攻最近的敌人**：先找 `CHAMP_REACH` 内最近的敌方英雄，
//! 没有就找最近的其他敌方单位（小兵、野怪、防御塔都行）；一个都看不见时回城改成原地不动（往回走也没用，亡灵时间一到就倒下）。
//! AI 要普攻（亡灵放不了技能）时不动它。被控住时什么都不做。判断在 `call`，纯计算、单元测试。

use mod_api_stable::*;

use super::{counted, head, sn, who, wlog, ID};

/// 排在 league_ult_press（100）和各英雄的连招钩子（110）之后：引擎按优先级从小到大跑 AI 钩子，最后一个说了算。
pub const ZOMBIE_PRIORITY: i32 = 130;
/// 这么远内有敌方英雄就先扑英雄。
pub const CHAMP_REACH: f64 = 90_000.0;

pub type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一个看得见的敌方单位。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub champion: bool,
}

/// AI 这一 tick 想做的。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Want {
    Return,
    Move,
    Attack,
    Other,
}

/// 替 AI 做的。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Call {
    Attack(usize),
    Stay,
}

pub fn call(me: Pt, foes: &[Foe], want: Want) -> Option<Call> {
    if !matches!(want, Want::Return | Want::Move) {
        return None;
    }
    let near = |f: &&Foe| dist(me, f.at);
    let champ = foes.iter().filter(|f| f.champion && dist(me, f.at) <= CHAMP_REACH)
        .min_by(|a, b| near(a).total_cmp(&near(b)));
    let any = || foes.iter().min_by(|a, b| near(a).total_cmp(&near(b)));
    match champ.or_else(any) {
        Some(f) => Some(Call::Attack(f.id)),
        None if want == Want::Return => Some(Call::Stay),
        None => None,
    }
}

/// 放不出普攻的控制、被强制位移时不动。
const STOP: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm,
    CcKindV1::Animation, CcKindV1::ForceMove];

fn want_of(base: Option<InputV1>) -> Want {
    let Some(b) = base else { return Want::Other };
    match InputKindV1::from_code(b.kind) {
        Some(InputKindV1::Return) => Want::Return,
        Some(InputKindV1::Move) => Want::Move,
        Some(InputKindV1::Attack) => Want::Attack,
        _ => Want::Other,
    }
}

#[derive(Clone, Default)]
pub struct Zombie;

impl StablePlayerAi for Zombie {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:zombie")
    }

    fn priority(&self) -> i32 {
        ZOMBIE_PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let want = want_of(base);
        let (c, line, at) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?.id();
            let e = sim.get_entity(me)?;
            let zombie = sn("p_zombie");
            if !e.is_alive() || !(0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == zombie) {
                return None;
            }
            if (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
                return None;
            }
            let (x, y) = e.pos();
            let team = e.team();
            let mut foes = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(u) = sim.entity_at(i) else { continue };
                if u.team() == team || !u.is_alive() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
                    continue;
                }
                let (ux, uy) = u.pos();
                foes.push(Foe { id: u.id(), at: (ux as f64, uy as f64), champion: u.is_champion() });
            }
            let c = call((x as f64, y as f64), &foes, want)?;
            let on = match c {
                Call::Attack(t) => who(&sim, t),
                Call::Stay => "-".to_string(),
            };
            (c, format!("{} ZOMBIE: the AI wanted {want:?} - {c:?} ({on})", head(&sim, me)), (x, y))
        };
        let input = match c {
            Call::Attack(t) => InputV1::action(InputKindV1::Attack, InputTargetV1::target(t)),
            Call::Stay => InputV1::move_to(at.0, at.1),          // where he stands: no recall
        };
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(n) = counted("zombie") {
            wlog(format!("{line} #{n}"));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn foe(id: usize, x: f64, champion: bool) -> Foe {
        Foe { id, at: (x, 0.0), champion }
    }

    #[test]
    fn the_zombie_never_goes_home() {
        let foes = [foe(1, 20_000.0, false), foe(2, 60_000.0, true)];
        // recalling or retreating: at the champion in reach
        assert_eq!(call((0.0, 0.0), &foes, Want::Return), Some(Call::Attack(2)));
        assert_eq!(call((0.0, 0.0), &foes, Want::Move), Some(Call::Attack(2)));
        // no champion in reach: the nearest unit
        assert_eq!(call((0.0, 0.0), &[foe(1, 20_000.0, false), foe(2, 200_000.0, true)], Want::Move), Some(Call::Attack(1)));
        // attacking already: left alone
        assert_eq!(call((0.0, 0.0), &foes, Want::Attack), None);
        // nobody seen: no recall, a walk is left alone
        assert_eq!(call((0.0, 0.0), &[], Want::Return), Some(Call::Stay));
        assert_eq!(call((0.0, 0.0), &[], Want::Move), None);
    }
}
