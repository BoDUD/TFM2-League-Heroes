//! 奇亚娜的 AI 钩子 `league_qiyana:ai`（2026-11-04，照英雄联盟 V26.21）。游戏的 AI 见到射程里有敌方英雄就按 R、见到射程里
//! 有敌人就按 Q，可本包的 R 只有冲击波打到地形旁边的人才伤害、才晕，Q 的动作距离又是元素之怒的（扔出去的环刃）：
//!
//! - **R TERRAIN**：R 好了、没被控，地图读得到：朝每个 R 够得着（引擎也认可）的敌方英雄吹一次风（[`super::ult::best`]：风路上的人
//!   先按击退挪过去），冲击波打得到敌方英雄就放，挑打到最多的（一样多时 AI 想打的那个、再挑残血的）。AI 没想放 R 时，打得到
//!   `R_SELF_MIN` 个以上也放（游戏的 AI 不一定在好时机按）。
//! - **R HELD**：AI 想放 R，谁都打不到：不放，改成对它想打的人放 Q（好了、够得着）、E（好了），再不然普攻（打不到就走过去）——
//!   AI 每 tick 都还想放 R，只换成普攻的话 Q、E 就一直放不出来。读不到地图时不管（照主包，见人就放）。
//! - **Q HELD**：AI 想放 Q，她手上没元素（直线的 Q），目标还在直线够不着的地方（`q_len` + `q_hw` + 身体 - `Q_MARGIN`）：不放，
//!   改成 E（好了就突进过去，落地接 W、Q），再不然普攻（打不到就走过去）；有元素时照放（扔环刃，够得着 `q2_range`）。
//!
//! 回城时不管。一次按键（引擎接下之前钩子每 tick 都再按）只记一行（`PRESS_FRESH`）。

use mod_api_stable::*;

use super::terrain::MapGrids;
use super::{counted, current_map, dist, foe_of, has_buff, has_cc, head, on_screen, params_of, qy, ult, wlog, Foe, Params, HERO, ID};

/// 排在 league_ult_press（100）之后，同别的连招钩子。
pub const PRIORITY: i32 = 110;
/// 同一个人、同一类按键，离上一次不到这么多 tick 算同一次（league_ult_press 的 ORDER_FRESH）。
pub const PRESS_FRESH: usize = 30;
/// 直线的 Q 等目标进来这么深才放（出手要 9 tick，他会走）。
pub const Q_MARGIN: f64 = 3_000.0;
/// AI 没想放 R 时，冲击波打得到这么多敌方英雄也放。
pub const R_SELF_MIN: usize = 2;
/// AI 没想放 R 时隔这么多 tick 看一次。
pub const R_LOOK: usize = 3;

/// 放不了技能的状态。
const STOP: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
    CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

/// AI 这一 tick 想要的。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Want {
    Q(Option<usize>),
    R(Option<usize>),
    Attack(Option<usize>),
    Other,
}

pub fn want_of(base: Option<InputV1>) -> Want {
    let Some(b) = base else { return Want::Other };
    let target = (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id);
    match InputKindV1::from_code(b.kind) {
        Some(InputKindV1::Skill) => Want::Q(target),
        Some(InputKindV1::Ult) => Want::R(target),
        Some(InputKindV1::Attack) => Want::Attack(target),
        _ => Want::Other,
    }
}

/// The AI is still recalling (league_ornn's combo): its last order was a Return, and any other order ends it.
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// 这一 tick 怎么办。
#[derive(Clone, Debug, PartialEq)]
pub enum Call {
    /// 对他放 R：冲击波打得到的敌方英雄、是不是 AI 自己想放的。
    R(usize, Vec<usize>, bool),
    /// AI 想放 R（对这个人），谁都打不到：不放。
    RHeld(usize),
    /// AI 想放直线的 Q（对这个人），他还在多远：不放。
    QHeld(usize, f64),
}

/// 直线的 Q 够得着 `t` 吗（中心之间）：`q_len` + `q_hw` + 他的身体 - `Q_MARGIN`。
pub fn line_reach(p: &Params, t: &Foe) -> f64 {
    (p.q_len + p.q_hw) as f64 + t.r - Q_MARGIN
}

/// 这一 tick 的决定（纯计算）。`cands`：R 够得着（引擎认可）的敌方英雄；`champs`：看得见的敌方英雄（数冲击波打到几个）；
/// `q_target`：AI 想放 Q 的目标；`el_on`：她手上有元素。
#[allow(clippy::too_many_arguments)]
pub fn decide(map: Option<&MapGrids>, me: (f64, f64), r_ready: bool, look: bool, el_on: bool, want: Want, cands: &[Foe],
              champs: &[Foe], q_target: Option<&Foe>, p: &Params) -> Option<Call> {
    if let (true, Some(m)) = (r_ready, map) {
        let ai_r = match want {
            Want::R(t) => Some(t),
            _ => None,
        };
        if ai_r.is_some() || look {
            let plan = ult::best(m, me, cands, champs, ai_r.flatten(), p);
            match (plan, ai_r) {
                (Some(plan), Some(_)) => return Some(Call::R(plan.target, plan.caught, true)),
                (Some(plan), None) if plan.caught.len() >= R_SELF_MIN => return Some(Call::R(plan.target, plan.caught, false)),
                (None, Some(Some(t))) => return Some(Call::RHeld(t)),
                _ => {}
            }
        }
    }
    if let (Want::Q(Some(t)), false, Some(f)) = (want, el_on, q_target) {
        let d = dist(me, f.at);
        if f.id == t && d > line_reach(p, f) {
            return Some(Call::QHeld(t, d));
        }
    }
    None
}

#[derive(Clone, Default)]
pub struct QiyanaAi {
    recalling: bool,
    /// the last press: its kind, target, tick (one log line a burst)
    last: Option<(&'static str, usize, usize)>,
}

impl StablePlayerAi for QiyanaAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ai")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        self.recalling = still_recalling(self.recalling, base);
        if self.recalling {
            return None;
        }
        let want = want_of(base);
        let player = ctx.player_id();
        let (here, tick, line, map, champs, q_target, el_on, r_ready, p, q_up, e_up) = {
            let sim = ctx.sim()?;
            let e = sim.get_player(player)?.champion()?;
            if !e.is_alive() {
                return None;
            }
            let (me, team, tick) = (e.id(), e.team(), sim.tick());
            let r_ready = !has_cc(&sim, me, &STOP) && e.cooldown(SkillSlotV1::Ult).is_some_and(|c| c.unlocked && c.remaining == 0);
            let look = r_ready && tick % R_LOOK == 0;
            if !matches!(want, Want::R(_) | Want::Q(Some(_))) && !look {
                return None;
            }
            let here = (e.pos().0 as f64, e.pos().1 as f64);
            let champs: Vec<Foe> = (0..sim.champion_count())
                .map(|i| sim.champion_id_at(i))
                .filter(|&id| sim.get_entity(id).is_some_and(|u| u.team() != team) && sim.is_visible(team, id))
                .filter_map(|id| foe_of(&sim, id))
                .collect();
            let q_target = match want {
                Want::Q(Some(t)) => foe_of(&sim, t),
                _ => None,
            };
            let map = if r_ready { current_map(&sim) } else { None };
            // the slots' own cooldowns are the data's flags (the actions' are 1 s)
            let (q_up, e_up) = (!has_buff(&sim, me, &qy("q_cd")), !has_buff(&sim, me, &qy("e_cd")));
            (here, tick, head(&sim, me), map, champs, q_target, has_buff(&sim, me, &qy("el_on")), r_ready, params_of(&sim, me),
             q_up, e_up)
        };
        // the engine has the last word on the range: R only at those it takes
        let cands: Vec<Foe> = champs
            .iter()
            .filter(|f| ctx.is_valid_input(&InputV1::action(InputKindV1::Ult, InputTargetV1::target(f.id))))
            .copied()
            .collect();
        let look = r_ready && tick % R_LOOK == 0;
        let call = decide(map.as_deref(), here, r_ready, look, el_on, want, &cands, &champs, q_target.as_ref(), &p)?;
        let at_of = |id: usize| champs.iter().chain(q_target.iter()).find(|f| f.id == id).map(|f| f.at);
        // what she does instead of a held press: the AI keeps asking for it every tick, so the next of her moves the engine
        // takes on that target (Q, E when ready), else an attack, else a walk up to him
        let line_ok = |t: usize| {
            el_on || champs.iter().chain(q_target.iter()).find(|f| f.id == t).is_some_and(|f| dist(here, f.at) <= line_reach(&p, f))
        };
        let instead = |ctx: &StableAiContext<'_>, t: usize, kinds: &[InputKindV1]| {
            kinds
                .iter()
                .filter(|k| match k {
                    InputKindV1::Skill => q_up && line_ok(t),
                    InputKindV1::Skill2 => e_up,
                    _ => true,
                })
                .map(|k| InputV1::action(*k, InputTargetV1::target(t)))
                .find(|i| ctx.is_valid_input(i))
                .or_else(|| at_of(t).map(|at| InputV1::move_to(at.0.max(0.0) as u64, at.1.max(0.0) as u64)))
        };
        let what = |i: &InputV1| match InputKindV1::from_code(i.kind) {
            Some(InputKindV1::Skill) => "Q",
            Some(InputKindV1::Skill2) => "E",
            Some(InputKindV1::Attack) => "an attack",
            _ => "a walk up",
        };
        let (input, kind, t, text) = match &call {
            Call::R(t, caught, own) => {
                let from = match want {
                    Want::R(Some(a)) if a != *t => format!(" (the AI aimed at #{a})"),
                    _ => String::new(),
                };
                (InputV1::action(InputKindV1::Ult, InputTargetV1::target(*t)), if *own { "r terrain" } else { "r self" }, *t,
                 format!("R TERRAIN{} at #{t}{from}: the shockwave catches {} champions {caught:?}",
                         if *own { "" } else { " (on her own)" }, caught.len()))
            }
            Call::RHeld(t) => {
                let i = instead(ctx, *t, &[InputKindV1::Skill, InputKindV1::Skill2, InputKindV1::Attack])?;
                (i, "r held", *t,
                 format!("R HELD: the AI's R at #{t}, but no wind of hers reaches terrain beside an enemy champion - {} instead", what(&i)))
            }
            Call::QHeld(t, d) => {
                let i = instead(ctx, *t, &[InputKindV1::Skill2, InputKindV1::Attack])?;
                (i, "q held", *t, format!("Q HELD: no element, #{t} is {d:.0} off - beyond the plain line; {} instead", what(&i)))
            }
        };
        let burst = self.last.is_some_and(|(k, at, t0)| k == kind && at == t && tick >= t0 && tick <= t0 + PRESS_FRESH);
        self.last = Some((kind, t, tick));
        if !burst {
            let shown = ctx.sim().is_some_and(|sim| on_screen(&sim));
            if let Some(n) = counted(kind, shown) {
                wlog(format!("{line} {text} #{n}"));
            }
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::terrain::{Grid, CELL};

    fn map(walls: &[(usize, usize)]) -> MapGrids {
        let rows: Vec<String> = (0..30).map(|y| (0..30).map(|x| if walls.contains(&(x, y)) { '#' } else { '.' }).collect()).collect();
        let empty: Vec<String> = (0..30).map(|_| ".".repeat(30)).collect();
        MapGrids {
            mode: GameModeKindV1::Moba.code(),
            walls: Some(Grid::from_rows(&rows.iter().map(|s| s.as_str()).collect::<Vec<_>>())),
            bushes: Some(Grid::from_rows(&empty.iter().map(|s| s.as_str()).collect::<Vec<_>>())),
            river: None,
        }
    }

    fn champ(id: usize, at: (f64, f64)) -> Foe {
        Foe { id, at, r: 10_000.0, champion: true, monster: false, hp: 800, max: 1000, immune: false }
    }

    fn input(kind: InputKindV1, t: usize) -> Option<InputV1> {
        Some(InputV1::action(kind, InputTargetV1::target(t)))
    }

    #[test]
    fn r_only_where_the_shockwave_finds_a_champion() {
        let m = map(&[(15, 1), (15, 2), (15, 3), (15, 4), (15, 5)]);
        let p = Params::default();
        let me = (13.2 * CELL, 3.5 * CELL);
        let by_wall = champ(1, (14.0 * CELL, 3.5 * CELL));
        let open = champ(2, (10.0 * CELL, 3.5 * CELL));
        let all = [by_wall, open];
        // the AI's R at the one in the open: turned toward the one by the wall
        assert_eq!(decide(Some(&m), me, true, false, false, want_of(input(InputKindV1::Ult, 2)), &all, &all, None, &p),
                   Some(Call::R(1, vec![1], true)));
        // nobody by any terrain: held
        assert_eq!(decide(Some(&m), me, true, false, false, want_of(input(InputKindV1::Ult, 2)), &[open], &[open], None, &p),
                   Some(Call::RHeld(2)));
        // one champion only: not cast on her own; two: cast
        assert_eq!(decide(Some(&m), me, true, true, false, Want::Other, &all, &all, None, &p), None);
        let second = champ(3, (14.2 * CELL, 4.2 * CELL));
        let three = [by_wall, open, second];
        assert!(matches!(decide(Some(&m), me, true, true, false, Want::Other, &three, &three, None, &p),
                         Some(Call::R(_, ref c, false)) if c.len() == 2));
        // no map read: the AI's own R as in the main pack
        assert_eq!(decide(None, me, true, false, false, want_of(input(InputKindV1::Ult, 2)), &all, &all, None, &p), None);
        // R not ready: nothing
        assert_eq!(decide(Some(&m), me, false, false, false, want_of(input(InputKindV1::Ult, 1)), &all, &all, None, &p), None);
    }

    #[test]
    fn a_plain_q_waits_for_the_line() {
        let p = Params::default();
        let me = (100_000.0, 100_000.0);
        let far = champ(5, (160_000.0, 100_000.0));
        let near = champ(6, (140_000.0, 100_000.0));
        let q = |t: &Foe, el_on: bool| decide(None, me, false, false, el_on, want_of(input(InputKindV1::Skill, t.id)), &[], &[], Some(t), &p);
        // 60000 off: beyond the line (31500 + 7000 + 10000 - 3000), held; with an element the blade goes
        assert_eq!(q(&far, false), Some(Call::QHeld(5, 60_000.0)));
        assert_eq!(q(&far, true), None);
        // 40000 off: in reach
        assert_eq!(q(&near, false), None);
    }

    #[test]
    fn the_ai_wants_and_recalls() {
        assert_eq!(want_of(input(InputKindV1::Skill, 4)), Want::Q(Some(4)));
        assert_eq!(want_of(input(InputKindV1::Ult, 4)), Want::R(Some(4)));
        assert_eq!(want_of(None), Want::Other);
        assert!(still_recalling(false, Some(InputV1::return_home())));
        assert!(still_recalling(true, None));
        assert!(!still_recalling(true, input(InputKindV1::Attack, 1)));
    }
}
