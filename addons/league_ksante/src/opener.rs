//! 开大的时机（0.1.2，用户 2026-11-18：「奎桑提为什么总是喜欢大招起手 很奇怪啊 高手的奎桑提不会这样打啊」）。
//!
//! 游戏的 AI 只要敌方英雄进了 R 的射程就放傲岸雄姿：看的那场（m=6622）他射程里有敌方英雄、普攻也好着的时候，AI 的命令有
//! 两成左右是 R，10 分钟放了 7 次，几乎都是一好就放、开团第一下。英雄联盟的高手不这样打：全盛把生命压在最大生命的 65%
//! （本包的 [`super::Cap`]），满血开等于白丢三成多的血；坦克形态先顶住、用 Q / W 开团，血掉下来、能收人头，或者要把扑向
//! 残血队友的人踢开时才开大。
//!
//! 本包的 AI 钩子 [`Opener`] 在 AI 要放 R 时看一眼（[`call`]），下面任一条成立就照放：
//! - 他自己的生命在最大生命的 [`LET_HP`]% 以下（全盛压到 65%，这时开几乎不亏）；
//! - 目标的生命在 [`FINISH`]% 以下（收人头）；
//! - 目标身边 [`PEEL_R`] 以内有生命不到 [`PEEL_HP`]% 的我方英雄（把扑上来的人踢开）；
//! - 这一波 AI 已经连着要了 [`HOLD_MAX`] tick（打久了，大招不能一直憋着）。
//!
//! 都不成立就改成普攻这个目标（够不着就走过去），Q、W 和普攻先上；AI 下一次还可以再要。日志 `R HELD` / `R LET`。

use mod_api_stable::*;

use super::{counted, wlog, ALL_OUT, ID};

/// After league_ult_press (100), before league_camille_wall's arena (120).
pub const PRIORITY: i32 = 110;
/// R goes out when his health is at or below this share of his maximum (All Out holds him at 65%).
pub const LET_HP: usize = 70;
/// ... or on a target at or below this share of its maximum.
pub const FINISH: usize = 35;
/// ... or on one standing this close to an ally champion below [`PEEL_HP`]% (a diver on a weakened ally).
pub const PEEL_R: f64 = 30_000.0;
pub const PEEL_HP: usize = 50;
/// ... or once the AI has asked for it this many ticks in a row (a long fight).
pub const HOLD_MAX: usize = 240;
/// The AI's asks this far apart are two fights: the run of asks starts over.
pub const GAP: usize = 90;

/// Why R goes out.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Why {
    /// his own health is down to the All Out line
    Hurt,
    /// the target is low
    Finish,
    /// the target is on a weakened ally
    Peel,
    /// the AI has wanted it for a while
    Long,
}

/// Whether R goes out (and why), from his health share, the target's, whether the target is on a weakened ally and how
/// long the AI has been asking; None holds it.
pub fn call(my_pct: usize, target_pct: usize, peel: bool, asked_for: usize) -> Option<Why> {
    if my_pct <= LET_HP {
        Some(Why::Hurt)
    } else if target_pct <= FINISH {
        Some(Why::Finish)
    } else if peel {
        Some(Why::Peel)
    } else if asked_for >= HOLD_MAX {
        Some(Why::Long)
    } else {
        None
    }
}

/// `hp` as a share of `max`, in %.
pub fn pct(hp: usize, max: usize) -> usize {
    if max == 0 {
        100
    } else {
        hp * 100 / max
    }
}

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn dist(a: (u64, u64), b: (u64, u64)) -> f64 {
    ((a.0 as f64 - b.0 as f64).powi(2) + (a.1 as f64 - b.1 as f64).powi(2)).sqrt()
}

/// The AI hook: holds the game AI's R until [`call`] lets it go.
#[derive(Clone, Default)]
pub struct Opener {
    /// the first and the last tick of the AI's current run of R asks
    run: Option<(usize, usize)>,
}

impl StablePlayerAi for Opener {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:opener")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let b = base?;
        if InputKindV1::from_code(b.kind) != Some(InputKindV1::Ult) {
            return None;
        }
        let player = ctx.player_id();
        let (t, why, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() || has(&me, ALL_OUT) {
                return None;
            }
            let t = (b.target.kind == InputTargetKindV1::Target.code()).then_some(b.target.target_id)?;
            let target = sim.get_entity(t)?;
            let tick = sim.tick();
            let start = match self.run {
                Some((s, last)) if tick >= last && tick - last <= GAP => s,
                _ => tick,
            };
            self.run = Some((start, tick));
            let (hp, max) = me.hp();
            let (thp, tmax) = target.hp();
            let at = target.pos();
            let team = me.team();
            let peel = (0..sim.champion_count())
                .filter_map(|i| sim.get_entity(sim.champion_id_at(i)))
                .filter(|a| a.team() == team && a.id() != me.id() && a.is_alive())
                .any(|a| {
                    let (ah, am) = a.hp();
                    pct(ah, am) < PEEL_HP && dist(a.pos(), at) <= PEEL_R
                });
            let (mine, theirs) = (pct(hp, max), pct(thp, tmax));
            let why = call(mine, theirs, peel, tick - start);
            let line = format!(
                "t={tick} #{} R on #{t} {}: his health {mine}%, the target's {theirs}%{}, asked for {} ticks",
                me.id(),
                target.name().unwrap_or_default(),
                if peel { ", on a weakened ally" } else { "" },
                tick - start
            );
            (t, why, line)
        };
        if let Some(why) = why {
            // R goes out: the next ask starts a new run
            self.run = None;
            if let Some(k) = counted("let") {
                wlog(format!("{line} - R LET ({why:?}) #{k}"));
            }
            return None;
        }
        let input = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(k) = counted("held") {
            wlog(format!("{line} - R HELD: attack him instead #{k}"));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn r_waits_for_a_reason() {
        // full health, a healthy target, nobody to peel for, a fresh ask: held
        assert_eq!(call(100, 100, false, 0), None);
        assert_eq!(call(71, 36, false, HOLD_MAX - 1), None);
        // his own health down to the All Out line
        assert_eq!(call(70, 100, false, 0), Some(Why::Hurt));
        // a low target
        assert_eq!(call(100, 35, false, 0), Some(Why::Finish));
        // a diver on a weakened ally
        assert_eq!(call(100, 100, true, 0), Some(Why::Peel));
        // a long fight
        assert_eq!(call(100, 100, false, HOLD_MAX), Some(Why::Long));
        // his own health first
        assert_eq!(call(50, 10, true, HOLD_MAX), Some(Why::Hurt));
    }

    #[test]
    fn shares_round_down() {
        assert_eq!(pct(1300, 2000), 65);
        assert_eq!(pct(1399, 2000), 69);
        assert_eq!(pct(5, 0), 100);
    }

    #[test]
    fn it_lets_him_cast_before_all_out_costs_much() {
        // R lets go at LET_HP, a little above the All Out cap: entering costs at most LET_HP - CAP_PCT % of his health
        assert!(LET_HP >= super::super::CAP_PCT && LET_HP - super::super::CAP_PCT <= 5);
    }
}
