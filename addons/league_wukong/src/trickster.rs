//! 悟空的 W（真假猴王）替 AI 按（用户 2026-10-29：「你确定会放分身吗现在 我怎么一次没见过」→「加上」）：AI 钩子
//! `league_wukong:trickster`。游戏的 AI 一次只按一个技能，几乎总先按冷却 8 秒、对小兵野怪也能放的 E；W 只能对英雄放、冷却
//! 20 秒，经典引擎模拟里一局 10 分钟只放 4 次（第一次在 4 分 21 秒），分身难得一见。本钩子：W 解锁并好了、`W_RANGE` +
//! `BODIES` 内有敌方英雄（不在敌方塔下，除非他自己已经在塔下）、他没被控、不在回城、不在转大招（`r_on`）时，对最近的那个按 W——
//! 英雄联盟里 W 用来开团、接大招（有分身时分身也跟着转）。这一拍 AI 自己要按技能或大招（league_ult_press 替他按的大招也是）
//! 时不管。判断在 `call`（纯计算、单元测试）。
//!
//! 按 W 前一定查 W 解锁了：游戏 0.6.4 起，钩子在技能解锁前按 skill2 / ult 会让游戏的 AI 卡死、一天过不完
//! （champion-data.md；league_unlock_guard 也会兜底）。

use mod_api_stable::*;

use super::{dist, head, noted, on_screen, wlog, Pt, ID, R_ON};

/// 排在 league_ult_press（100）之后。
pub const PRIORITY: i32 = 110;
/// 主包数据：W 的射程（build_wukong.P w_range，单元测试核对）；两个单位的身体（射程算到身体边上，大约）。
pub const W_RANGE: f64 = 45_000.0;
pub const BODIES: f64 = 12_000.0;
/// 敌方塔的攻击范围（大约）：W 冲到目标身后，别冲进塔下。
pub const TOWER_REACH: f64 = 75_000.0;

/// 被控、在放技能（施法动作）时不按。
const STOP: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                             CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

/// 按 W 打谁：W 好了、没在转大招时，`W_RANGE` + `BODIES` 内最近的敌方英雄（他不在敌方塔下时，不挑塔下的）。
pub fn call(me: Pt, w_ready: bool, spinning: bool, foes: &[(usize, Pt)], towers: &[Pt]) -> Option<usize> {
    if !w_ready || spinning {
        return None;
    }
    let under = |p: Pt| towers.iter().any(|&t| dist(t, p) <= TOWER_REACH);
    let me_under = under(me);
    foes.iter()
        .filter(|(_, p)| dist(me, *p) <= W_RANGE + BODIES)
        .filter(|(_, p)| me_under || !under(*p))
        .min_by(|a, b| dist(me, a.1).total_cmp(&dist(me, b.1)))
        .map(|(id, _)| *id)
}

fn pt(e: &StableEntity<'_, '_>) -> Pt {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

#[derive(Clone, Default)]
pub struct Trickster {
    recalling: bool,
}

impl StablePlayerAi for Trickster {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:trickster")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        self.recalling = match base {
            Some(b) => b.kind == InputKindV1::Return.code(),
            None => self.recalling,
        };
        if self.recalling {
            return None;
        }
        // the AI (or league_ult_press) presses a skill or the ult this tick: its own
        if base.is_some_and(|b| [InputKindV1::Skill, InputKindV1::Skill2, InputKindV1::Ult].iter().any(|k| k.code() == b.kind)) {
            return None;
        }
        let player = ctx.player_id();
        let (target, line, shown) = {
            let sim = ctx.sim()?;
            let e = sim.get_player(player)?.champion()?;
            if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
                return None;
            }
            // unlocked first: a skill2 pressed before it unlocks stops the game's AI
            let w_ready = e.cooldown(SkillSlotV1::Skill2).is_some_and(|c| c.unlocked && (c.remaining == 0 || c.charges > 0));
            let spinning = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == R_ON);
            let (id, team, me) = (e.id(), e.team(), pt(&e));
            let (mut foes, mut towers) = (Vec::new(), Vec::new());
            for i in 0..sim.entity_count() {
                let Some(u) = sim.entity_at(i) else { continue };
                if !u.is_alive() || u.team() == team {
                    continue;
                }
                if u.is_tower() {
                    towers.push(pt(&u));
                } else if u.is_champion() && u.is_targetable() {
                    foes.push((u.id(), pt(&u)));
                }
            }
            let t = call(me, w_ready, spinning, &foes, &towers)?;
            let away = foes.iter().find(|f| f.0 == t).map_or(0.0, |f| dist(me, f.1));
            (t, format!("{} W PRESS on #{t}, {away:.0} away", head(&sim, id)), on_screen(&sim))
        };
        let input = InputV1::action(InputKindV1::Skill2, InputTargetV1::target(target));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(n) = noted("w press", shown) {
            wlog(format!("{line} #{n}"));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_nearest_champion_in_reach() {
        let foes = [(1, (50_000.0, 0.0)), (2, (30_000.0, 0.0)), (3, (70_000.0, 0.0))];
        assert_eq!(call((0.0, 0.0), true, false, &foes, &[]), Some(2));
        // out of reach: nothing
        assert_eq!(call((0.0, 0.0), true, false, &[(3, (70_000.0, 0.0))], &[]), None);
    }

    #[test]
    fn not_before_it_is_ready_nor_while_he_spins() {
        let foes = [(1, (20_000.0, 0.0))];
        assert_eq!(call((0.0, 0.0), false, false, &foes, &[]), None);
        assert_eq!(call((0.0, 0.0), true, true, &foes, &[]), None);
    }

    #[test]
    fn no_dash_under_their_tower_unless_he_is_there() {
        let foes = [(1, (40_000.0, 0.0))];
        let tower = [(100_000.0, 0.0)];
        assert_eq!(call((0.0, 0.0), true, false, &foes, &tower), None);
        assert_eq!(call((60_000.0, 0.0), true, false, &foes, &tower), Some(1));
    }

    #[test]
    fn the_range_is_the_kit_s() {
        let src = include_str!("../../../tools/kit/build_wukong.py");
        assert!(src.contains(&format!("\"w_range\": {}", W_RANGE as usize)));
    }
}
