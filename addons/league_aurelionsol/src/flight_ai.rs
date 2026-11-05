//! 飞行中的龙息（AI 钩子 `league_aurelionsol:flight_ai`）。用户 2026-11-04：「龙王是不是不能边飞行边放Q」。
//!
//! 以前的星穹流丽（主包：击杀后起飞 4 秒）几乎从来不边飞边喷：经典引擎模拟 7 局 24 次起飞，22 次起飞时龙息还在冷却
//! （起飞不重置冷却，击杀往往就是龙息打出来的），只有 11 次飞行里喷过一口，都在起飞 53–233 tick 后（冷却走完），而且龙息
//! 的施法动作把他钉在原地 90 tick——飞行的移速一点用不上。现在被动起飞时去掉 `q_cd`，飞行中主包副本的龙息没有冷却；这个
//! 钩子保证他真的喷：飞着（身上有本包的 `w_fly`）、没在喷（没有主包的 `q_ch` / `q_live`）、没在出招时，对龙息够得着、
//! 看得见的敌方英雄按技能 1——先对这次飞向的那个（`w_at:<id>`），没有就挑生命最低的；逃生的飞行（`w_esc`）只喷生命不到
//! [`ESC_BURN`] 的追兵（喷着飞速度减半，逃得慢）。喷不了的时候，游戏的 AI 让他走路、普攻**或者按龙息**（0.3.1）就改成朝落点
//! （`w_to:<x>,<y>`）飞——身体朝着飞的方向，不停下来打一下。大招、黑洞照游戏的 AI 放（英雄联盟：飞行中什么技能都能放）。
//! 日志 `FLY AI`（按了谁）、`FLY AI REFUSED`（游戏没收这个输入）、`FLY AI STEER`（游戏 AI 自己的龙息改成飞，一串记一行）。
//!
//! 0.3.1（11-04 夜里的日志）：游戏的 AI 自己按的龙息原样过了钩子（只有走路、普攻改成飞）——逃生时对着不残血的追兵喷
//! （FLY #885：28% 逃生，143 tick 里喷了 136 tick，全速 75 tick 就到），进场时对着够不着的人喷（FLY #702：149 tick 对着
//! 75000 内一个都没有的空气）；7 次逃生 6 次被拖慢、多飞 227 tick。现在飞行中游戏 AI 的 Skill 输入也一样改成飞，被动的
//! [`super::Stardust`] 在龙息开始的那一 tick 再核对一次（[`breath_target`] 同一条规矩），不该喷的截掉。

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

/// 飞行中龙息够得着、看得见的敌方英雄（`reach`：龙息的施法距离加 [`BODIES`]）。
pub fn foes_in_reach(sim: &StableSim<'_>, me: &StableEntity<'_, '_>, reach: f64) -> Vec<Foe> {
    let here = (me.pos().0 as f64, me.pos().1 as f64);
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| {
            u.team() != me.team() && u.is_champion() && u.is_alive() && u.is_targetable() && sim.is_visible(me.team(), u.id())
        })
        .map(|u| Foe { id: u.id(), d: dist(here, (u.pos().0 as f64, u.pos().1 as f64)),
                       hp: u.hp().0 as f64 / u.hp().1.max(1) as f64 })
        .filter(|f| f.d <= reach)
        .collect()
}

/// 飞行中游戏 AI 的这种输入改成朝落点飞：走路、普攻，和它自己按的龙息（技能 1；0.3.1——以前它的龙息原样过了钩子，逃生时
/// 对着不残血的追兵喷、进场时对着够不着的人喷）。大招、黑洞、回城照放。
pub fn takes_over(kind: Option<InputKindV1>) -> bool {
    matches!(kind, Some(InputKindV1::Move | InputKindV1::Attack | InputKindV1::Skill))
}

/// 一串 `FLY AI STEER` 只记一行：上一行在这么多 tick 内就不记（游戏的 AI 每 4 tick 下一次命令）。
pub const STEER_FRESH: usize = 60;

/// 这一 tick 钩子要做的。
enum Todo {
    /// 对 `target` 按技能 1（龙息）。
    Breathe { target: usize, line: String },
    /// 朝落点飞（游戏的 AI 想走开、普攻或喷龙息；`breath`：它想喷的是龙息，记 `FLY AI STEER`）。
    Steer { to: Pt, breath: Option<String> },
}

#[derive(Clone, Default)]
pub struct FlightAi {
    /// 上一行 `FLY AI STEER` 的 tick（一串记一行）。
    steer_at: Option<usize>,
}

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
            let foes = foes_in_reach(&sim, &me, reach);
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
                    match to {
                        // the game's own breath (0.3.1): on an escape at a chaser not low, or at nobody in reach -
                        // the flight goes on at full speed instead (a short way left: let it be, the landing is a tick off)
                        Some(t) if takes_over(kind) && dist(here, t) > 2_000.0 => Todo::Steer {
                            to: t,
                            breath: (kind == Some(InputKindV1::Skill)).then(|| {
                                let near = foes.iter().map(|f| (f.d, f.hp)).min_by(|a, b| a.0.total_cmp(&b.0));
                                format!("{} FLY AI STEER: the game's own Breath of Light on the {} flight {} - flying on",
                                        head(&sim, me.id()), if escape { "escape" } else { "chase/engage" },
                                        match near {
                                            Some((d, hp)) => format!("(nearest enemy champion {d:.0} away, {:.0}% hp)", hp * 100.0),
                                            None => format!("(no enemy champion within {reach:.0})"),
                                        })
                            }),
                        },
                        _ => return None,
                    }
                }
            };
            (todo, shown)
        };
        let tick = ctx.tick();
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
            Todo::Steer { to, breath } => {
                if let Some(line) = breath {
                    if self.steer_at.is_none_or(|t0| tick < t0 || tick > t0 + STEER_FRESH) {
                        if let Some(k) = counted("fly_ai_steer", shown) {
                            wlog(format!("{line} #{k}"));
                        }
                    }
                    self.steer_at = Some(tick);
                }
                Some(InputV1::move_to(to.0.max(0.0) as u64, to.1.max(0.0) as u64))
            }
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

    #[test]
    fn the_games_own_breath_is_steered_like_a_walk() {
        // 11-04 night: the game AI's Skill input passed the hook - breaths at healthy chasers and at nobody
        for k in [InputKindV1::Move, InputKindV1::Attack, InputKindV1::Skill] {
            assert!(takes_over(Some(k)), "{k:?}");
        }
        // the black hole, the ult and a recall go out as the game's AI wants (League: any spell in flight)
        for k in [InputKindV1::Skill2, InputKindV1::Ult, InputKindV1::Return] {
            assert!(!takes_over(Some(k)), "{k:?}");
        }
        assert!(!takes_over(None));
    }

    #[test]
    fn the_passive_s_check_is_the_hook_s_rule() {
        // the breath the passive lets run at its start is the one the hook would press (lib.rs fly())
        let chaser = [f(3, 30_000.0, 0.6)];
        assert!(breath_target(&chaser, None, true).is_none(), "an escape with a healthy chaser: cut");
        assert!(breath_target(&chaser, None, false).is_some(), "a chase/engage with someone in reach: kept");
        assert!(breath_target(&[], Some(7), false).is_none(), "nobody within reach (FLY #702): cut");
    }
}
