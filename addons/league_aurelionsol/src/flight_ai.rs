//! 飞行中的龙息（AI 钩子 `league_aurelionsol:flight_ai`）。用户 2026-11-04：「龙王是不是不能边飞行边放Q」。
//!
//! 以前的星穹流丽（主包：击杀后起飞 4 秒）几乎从来不边飞边喷：经典引擎模拟 7 局 24 次起飞，22 次起飞时龙息还在冷却
//! （起飞不重置冷却，击杀往往就是龙息打出来的），只有 11 次飞行里喷过一口，都在起飞 53–233 tick 后（冷却走完），而且龙息
//! 的施法动作把他钉在原地 90 tick——飞行的移速一点用不上。现在被动起飞时去掉 `q_cd`，飞行中主包副本的龙息没有冷却；这个
//! 钩子保证他真的喷：飞着（身上有本包的 `w_fly`）、没在喷（没有主包的 `q_ch` / `q_live`）、没在出招时，对龙息够得着、
//! 看得见的敌方英雄按技能 1——先对这次飞向的那个（`w_at:<id>`），没有就挑生命最低的；逃生的飞行（`w_esc`）只喷生命不到
//! [`ESC_BURN`] 的追兵（喷着飞速度减半，逃得慢）。喷不了的时候，游戏的 AI 让他走路或普攻就改成朝落点（`w_to:<x>,<y>`）
//! 飞——身体朝着飞的方向，不停下来打一下。大招、黑洞照游戏的 AI 放（英雄联盟：飞行中什么技能都能放）。
//! 日志 `FLY AI`（按了谁）、`FLY AI REFUSED`（游戏没收这个输入）。

use mod_api_stable::*;

use super::flight::{self, dist, Pt};
use super::{counted, head, on_screen, wlog, who, ID, Q_CD, Q_CH, Q_LIVE, W_AT, W_ESC, W_FLY, W_TO};

/// 在 league_ult_press（100）、league_quinn（110）之后。
pub const PRIORITY: i32 = 115;
/// 逃生时只对生命不到这么多的追兵喷。
pub const ESC_BURN: f64 = 0.25;
/// 龙息的施法距离之外再算两个身体（游戏收不收这个输入由它自己判断）。
pub const BODIES: f64 = 20_000.0;

/// 正在出招（游戏记成 `Animation`）或被强制位移：不替 AI 按，按了会打断。
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];

fn busy(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| BUSY.iter().any(|k| k.code() == c.kind)))
}

/// 一个看得见的敌方英雄：实体、离他多远、生命比例。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub d: f64,
    pub hp: f64,
}

/// 飞行中对谁喷：这次飞向的那个（在 `foes` 里），不然生命最低的（一样就近的）；逃生时只喷生命不到 [`ESC_BURN`] 的。
pub fn breath_target(foes: &[Foe], aim: Option<usize>, escape: bool) -> Option<Foe> {
    aim.and_then(|a| foes.iter().find(|f| f.id == a))
        .or_else(|| foes.iter().min_by(|a, b| a.hp.total_cmp(&b.hp).then(a.d.total_cmp(&b.d))))
        .copied()
        .filter(|f| !escape || f.hp <= ESC_BURN)
}

/// 这一 tick 钩子要做的。
enum Todo {
    /// 对 `target` 按技能 1（龙息）。
    Breathe { target: usize, line: String },
    /// 朝落点飞（游戏的 AI 想走开或普攻）。
    Steer(Pt),
}

#[derive(Clone, Default)]
pub struct FlightAi;

impl StablePlayerAi for FlightAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:flight_ai")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let (todo, shown) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let names: Vec<String> = (0..me.buff_count()).filter_map(|i| me.buff_at(i)).map(|b| b.name().to_string()).collect();
            let has = |n: &str| names.iter().any(|x| x == n);
            if !has(W_FLY) || has(Q_CH) || has(Q_LIVE) || busy(&me) {
                // not flying, or breathing already (its pose holds the game's AI), or casting: as it is
                return None;
            }
            let here = (me.pos().0 as f64, me.pos().1 as f64);
            let to = names.iter().find_map(|n| flight::parse_to(W_TO, n));
            let aim = names.iter().find_map(|n| n.strip_prefix(W_AT).and_then(|v| v.parse::<usize>().ok()));
            let escape = has(W_ESC);
            let ready = !has(Q_CD) && me.cooldown(SkillSlotV1::Skill).is_none_or(|c| c.unlocked && c.remaining == 0);
            let reach = super::params_of(&sim, me.id()).q_range as f64 + BODIES;
            let foes: Vec<Foe> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|u| {
                    u.team() != me.team() && u.is_champion() && u.is_alive() && u.is_targetable()
                        && sim.is_visible(me.team(), u.id())
                })
                .map(|u| Foe { id: u.id(), d: dist(here, (u.pos().0 as f64, u.pos().1 as f64)),
                               hp: u.hp().0 as f64 / u.hp().1.max(1) as f64 })
                .filter(|f| f.d <= reach)
                .collect();
            let shown = on_screen(&sim);
            let todo = match ready.then(|| breath_target(&foes, aim, escape)).flatten() {
                Some(f) => Todo::Breathe {
                    target: f.id,
                    line: format!("{} FLY AI: Breath of Light on {} ({:.0} away, {:.0}% hp){}", head(&sim, me.id()),
                                  who(&sim, f.id), f.d, f.hp * 100.0,
                                  if aim == Some(f.id) { ", the one he flies at" } else { "" }),
                },
                None => {
                    let kind = base.and_then(|b| InputKindV1::from_code(b.kind));
                    match (kind, to) {
                        (Some(InputKindV1::Move | InputKindV1::Attack), Some(t)) if dist(here, t) > 2_000.0 => Todo::Steer(t),
                        _ => return None,
                    }
                }
            };
            (todo, shown)
        };
        match todo {
            Todo::Breathe { target, line } => {
                let input = InputV1::action(InputKindV1::Skill, InputTargetV1::target(target));
                if !ctx.is_valid_input(&input) {
                    if let Some(k) = counted("fly_ai_refused", shown) {
                        wlog(format!("{line} - FLY AI REFUSED #{k}: the game took no Breath of Light on #{target}"));
                    }
                    return None;
                }
                if let Some(k) = counted("fly_ai", shown) {
                    wlog(format!("{line} #{k}"));
                }
                Some(input)
            }
            Todo::Steer(t) => Some(InputV1::move_to(t.0.max(0.0) as u64, t.1.max(0.0) as u64)),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn f(id: usize, d: f64, hp: f64) -> Foe {
        Foe { id, d, hp }
    }

    #[test]
    fn the_breath_goes_at_the_one_he_flies_at_first() {
        let foes = [f(3, 60_000.0, 0.9), f(4, 40_000.0, 0.5), f(5, 70_000.0, 0.5)];
        assert_eq!(breath_target(&foes, Some(3), false).map(|f| f.id), Some(3));
        // nobody he flies at (or out of reach): the lowest, then the nearest
        assert_eq!(breath_target(&foes, None, false).map(|f| f.id), Some(4));
        assert_eq!(breath_target(&foes, Some(9), false).map(|f| f.id), Some(4));
        assert_eq!(breath_target(&[], None, false), None);
    }

    #[test]
    fn running_away_he_burns_only_a_low_chaser() {
        let foes = [f(3, 30_000.0, 0.6)];
        assert_eq!(breath_target(&foes, None, true), None, "a healthy chaser: fly on at full speed");
        let foes = [f(3, 30_000.0, 0.2)];
        assert_eq!(breath_target(&foes, None, true).map(|f| f.id), Some(3));
    }

    #[test]
    fn the_hook_comes_after_ult_press_and_quinn() {
        assert!(PRIORITY > 110);
    }
}
