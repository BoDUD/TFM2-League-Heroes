//! AI 钩子 `league_orianna:combo`：Q+R 连招（0.3.0，用户 2026-11-02：「奥莉安娜的大招让人感觉不够爽快，即使是团战也主要只对
//! 单体使用。很明显是因为 AI 的缘故，目标总是第一个攻击她的人，因为他们离魔偶最近。有没有可能把它改成 Q+R 的主动连招，而不是像个
//! 陷阱一样等着别人走进去？」）。
//!
//! 以前：league_ult_press 在她身边 60000 内有敌方英雄时替 AI 按 R「待命」`r_arm` tick，数据在待命期间球附近（`r_r`）一有敌方
//! 英雄就放（主包 r_rule 2）。球多半在她身边、或在 Q 随机扔到的那个人脚下，第一个走进来的（多半是贴上来打她的）吃满一发。
//! 现在本包的副本：
//! - 数据只在球附近有 2 个敌方英雄、或冲击波打得死 1 个（`:r_kill`）时放，单个打不死的不放；待命没用上照旧退还冷却，所以
//!   league_ult_press 照旧替 AI 按 R 待命也不会浪费在一个人身上；
//! - Q 扔给脚下敌方英雄最多的那个（`:q_seen` / `:q_pick`，`crowd_pick`），不再随机；
//! - 本钩子在 league_ult_press（100）、`farm`（105）之后（`PRIORITY`），R 好着或待命着时 `plan` 看这一 tick：
//!   - 球（她身边、队友身上、地上，或 Q 的球正飞向的落点，`ball_point`）`CROWD` 内有 2 个敌方英雄、或 1 个冲击波打得死的：
//!     R 好着就按 R（`Plan::Blast`），数据下一次看球时就放（她身边每 3 tick、队友身上每 4 tick、地上每 30 tick、Q 的球落地那一下）；
//!     已经待命就等数据放；
//!   - 否则 Q 好着、她生命不低于 `MIN_HP`、`Q_REACH` 内有个敌方英雄脚下 `CROWD` 内有 2 个以上（或冲击波打得死他）、AI 也没在
//!     带她远离他（`AWAY`）：R 还没待命先按 R 待命，待命了按 Q 扔给他（`Plan::Throw`）——球一落地数据就放；
//!   - 别的都交给 AI 和 league_ult_press。
//! 正在回城、放技能或被位移（`farm::busy`，R 待命的 3 tick 动作也算）时不管；AI（或 league_ult_press）这一 tick 已经按了同一个格子
//! 也不管（Q 扔给谁由数据问 `:q_pick`）。日志 `COMBO`。

use mod_api_stable::*;

use super::farm::{at, busy};
use super::{ball_at, counted, crowd_at, crowd_pick, dist, foes_of, has_buff, head, on, pt, who, wlog, Ball, Foe, Where, CROWD, ID};

/// league_ult_press（100）、`farm`（105）之后。
pub const PRIORITY: i32 = 110;
/// Q 的射程（主包 build_orianna.P 的 q_range）。连招只扔给 `Q_REACH` 内的：数据在 Q 出手那一 tick（按下去 `q_st` tick 以后）
/// 才找 `q_range` 内的人，他们还会走几步。
pub const Q_RANGE: f64 = 70_000.0;
pub const Q_REACH: f64 = 64_000.0;
/// 还没待命时只为 `ARM_REACH` 内的人堆先按 R（0.3.1，11-02 的日志：4 次待命全在 63071-63190，正是人堆刚进 `Q_REACH` 的那一 tick，
/// 4 次里只有 1 次把 Q 扔进了人堆——R 的 3 tick 动作加 Q 的 6 tick 起手，人早走出 `q_range` 了）；待命以后照旧到 `Q_REACH`。
pub const ARM_REACH: f64 = 52_000.0;
/// 她自己的 Q（q_dur）、R（待命的 3 tick）动作还在播：这时按的输入游戏不收（0.3.1，11-02：Q 的球还在飞时连按 3 tick R，
/// 一次都没放出来，两次能击杀的冲击波都错过了）。冷却从满开始走了不到这么多 tick 就算还在播。
pub const Q_ACT: usize = 20;
pub const R_ACT: usize = 3;
/// R 格的射程（r_slot）：按 R 要有个这么近的敌方英雄当目标。
pub const R_SLOT: f64 = 90_000.0;
/// 冲击波的半径（r_r），`CROWD` 比它小一点。
pub const R_R: f64 = 42_000.0;
/// 她生命比例低于这个不扔 Q 开连招（Q 的施法动作里她站着不动）；R 照按。
pub const MIN_HP: f64 = 0.3;
/// AI 让她走到比她现在离目标还远这么多的地方：在撤，不扔 Q。
pub const AWAY: f64 = 10_000.0;
/// 连招的 Q 之后这么多 tick 内按的 R 在日志里算「Q 之后」。
pub const AFTER_Q: usize = 90;

/// 球在哪里能放冲击波：她身边（没有记录也算）、队友身上、地上，或 Q 的球正飞向的落点；E 送出去、飞回来的半路不算。
pub fn ball_point(ball: Option<Ball>, me: (f64, f64)) -> Option<(f64, f64)> {
    let Some(b) = ball else { return Some(me) };
    match b.w {
        Where::Home => Some(me),
        Where::Flying { to, .. } => Some(to),
        Where::Lying | Where::Riding { .. } => Some(b.at),
        Where::Sent { .. } | Where::Back => None,
    }
}

/// 她这一 tick 看到的。
pub struct Scene<'a> {
    pub me: (f64, f64),
    /// 生命比例。
    pub hp: f64,
    /// `ball_point`。
    pub ball: Option<(f64, f64)>,
    pub foes: &'a [Foe],
    /// R 好了（冷却好、已解锁）、R 待命着（`league_orianna_r_arm`）、Q 好了。
    pub r_ready: bool,
    pub armed: bool,
    pub q_ready: bool,
    /// AI 这一 tick 让她走到哪（没下走路命令就是 None）。
    pub walk: Option<(f64, f64)>,
    /// 控球的守望在跑（`league_orianna_polling`，她普攻时挂上）：没在跑时 Q 的球扔出去就直接飞回来，扔不进人堆。
    pub controller: bool,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Plan {
    /// 球那里人堆里有 `n` 个敌方英雄（`kill`：有冲击波打得死的）：按 R，数据下一次看球时就放。
    Blast { n: usize, kill: bool },
    /// `target` 脚下有 `n` 个（`kill`：冲击波打得死他）：`arm` = R 还没待命，先按 R；否则 Q 扔给他。
    Throw { target: usize, n: usize, kill: bool, arm: bool },
}

/// 这一 tick 替她按什么（None = 交给 AI 和 league_ult_press）。
pub fn plan(s: &Scene<'_>) -> Option<Plan> {
    if !s.r_ready && !s.armed {
        return None;
    }
    if let Some(b) = s.ball {
        let (n, kill) = crowd_at(b, s.foes);
        if n >= 2 || kill {
            // armed: the data fires at its next look at the ball
            return (!s.armed).then_some(Plan::Blast { n, kill });
        }
    }
    if !s.q_ready || s.hp < MIN_HP || !s.controller {
        return None;
    }
    let reach = if s.armed { Q_REACH } else { ARM_REACH };
    let cands: Vec<Foe> = s.foes.iter().filter(|f| dist(s.me, f.at) <= reach).copied().collect();
    let (target, n) = crowd_pick(&cands, s.foes)?;
    let f = cands.iter().find(|f| f.id == target)?;
    if n < 2 && !f.dies {
        return None;
    }
    if s.walk.is_some_and(|to| dist(to, f.at) > dist(s.me, f.at) + AWAY) {
        return None;
    }
    Some(Plan::Throw { target, n, kill: f.dies, arm: !s.armed })
}

// ===================== 钩子 =====================

#[derive(Clone, Default)]
pub struct Combo {
    /// 正在回城（`farm::Farm` 的一样）。
    recalling: bool,
    /// 上一次连招的 Q 按下去的 tick（日志：R 在 Q 之后多久按的）。
    q_at: Option<usize>,
}

impl StablePlayerAi for Combo {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:combo")
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
        let walk = base.filter(|b| b.kind == InputKindV1::Move.code()).map(|b| (b.x as f64, b.y as f64));
        let player = ctx.player_id();
        let q_at = self.q_at;
        let (input, kind, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() || busy(&me) {
                return None;
            }
            // her own Q or R still playing: a press now is dropped (the engine takes none until it ends)
            let playing = |s: SkillSlotV1, act: usize| {
                me.cooldown(s).is_some_and(|c| c.remaining > 0 && c.cooltime.saturating_sub(c.remaining) < act)
            };
            if playing(SkillSlotV1::Skill, Q_ACT) || playing(SkillSlotV1::Ult, R_ACT) {
                return None;
            }
            let (my_id, here, tick) = (me.id(), at(&me), sim.tick());
            let ready = |s: SkillSlotV1| me.cooldown(s).is_some_and(|c| c.unlocked && c.remaining == 0);
            let (r_ready, q_ready) = (ready(SkillSlotV1::Ult), ready(SkillSlotV1::Skill));
            let armed = has_buff(&sim, my_id, &on("r_arm"));
            if !r_ready && !armed {
                return None;
            }
            let (hp, max) = me.hp();
            let foes = foes_of(&sim, my_id);
            let ball = ball_at(&sim, my_id);
            let point = ball_point(ball, here);
            let controller = has_buff(&sim, my_id, &on("polling"));
            let scene = Scene { me: here, hp: hp as f64 / max.max(1) as f64, ball: point, foes: &foes, r_ready, armed, q_ready, walk,
                                controller };
            let p = plan(&scene)?;
            let place = ball.map_or("beside her", |b| b.w.label());
            let (input, kind, what) = match p {
                Plan::Blast { n, kill } => {
                    // the slot wants an enemy champion within its range: the nearest
                    let t = foes.iter().filter(|f| dist(here, f.at) <= R_SLOT)
                        .min_by(|a, b| dist(here, a.at).total_cmp(&dist(here, b.at)))?.id;
                    let after = match q_at {
                        Some(t0) if tick <= t0 + AFTER_Q => format!(", {} ticks after the combo's Q", tick - t0),
                        _ => String::new(),
                    };
                    (InputV1::action(InputKindV1::Ult, InputTargetV1::target(t)), "combo r",
                     format!("R: the ball {place} at {}, {n} enemy champions within {CROWD:.0}{}{after}",
                             point.map_or_else(|| "?".to_string(), pt), if kill { " (the shockwave kills one)" } else { "" }))
                }
                Plan::Throw { target, n, kill, arm } => {
                    let far = foes.iter().find(|f| f.id == target).map_or(f64::NAN, |f| dist(here, f.at));
                    let about = format!("{} {far:.0} away, {n} enemy champions within {CROWD:.0} of him{}", who(&sim, target),
                                        if kill { ", the shockwave kills him" } else { "" });
                    if arm {
                        (InputV1::action(InputKindV1::Ult, InputTargetV1::target(target)), "combo arm",
                         format!("arm R for a Q at {about} (the ball {place})"))
                    } else {
                        (InputV1::action(InputKindV1::Skill, InputTargetV1::target(target)), "combo q",
                         format!("Q at {about} (R armed, the ball {place})"))
                    }
                }
            };
            (input, kind, format!("{} COMBO {what}", head(&sim, my_id)))
        };
        // the same slot pressed already (the AI's, or league_ult_press's R): it goes - the data asks :q_pick for Q's champion
        if base.is_some_and(|b| b.kind == input.kind) {
            if kind == "combo q" {
                self.q_at = Some(ctx.tick());
            }
            return None;
        }
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if kind == "combo q" {
            self.q_at = Some(ctx.tick());
        }
        if let Some(k) = counted(kind) {
            wlog(format!("{line} #{k}"));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn foe(id: usize, x: f64, y: f64) -> Foe {
        Foe { id, at: (x, y), hp: 1.0, dies: false }
    }

    fn scene(foes: &[Foe], ball: Option<(f64, f64)>) -> Scene<'_> {
        Scene { me: (0.0, 0.0), hp: 1.0, ball, foes, r_ready: true, armed: false, q_ready: true, walk: None, controller: true }
    }

    #[test]
    fn two_at_the_ball_r_at_once() {
        let foes = [foe(1, 10_000.0, 0.0), foe(2, 20_000.0, 10_000.0)];
        assert_eq!(plan(&scene(&foes, Some((0.0, 0.0)))), Some(Plan::Blast { n: 2, kill: false }));
        // a pair round the ball on an ally or on the ground, she is far off
        assert_eq!(plan(&scene(&foes, Some((15_000.0, 30_000.0)))), Some(Plan::Blast { n: 2, kill: false }));
        // armed: the data fires it
        let mut s = scene(&foes, Some((0.0, 0.0)));
        s.armed = true;
        s.r_ready = false;
        assert_eq!(plan(&s), None);
        // R down and not armed: nothing at all
        let mut s = scene(&foes, Some((0.0, 0.0)));
        s.r_ready = false;
        assert_eq!(plan(&s), None);
    }

    #[test]
    fn one_alone_waits_unless_the_shockwave_kills_him() {
        // the one on her, nobody else near: no R (the old trap fired here) and no crowd for Q
        let foes = [foe(1, 10_000.0, 0.0)];
        assert_eq!(plan(&scene(&foes, Some((0.0, 0.0)))), None);
        let low = [Foe { dies: true, ..foe(1, 10_000.0, 0.0) }];
        assert_eq!(plan(&scene(&low, Some((0.0, 0.0)))), Some(Plan::Blast { n: 1, kill: true }));
        // the killable one is 50k off: arm, then Q at him
        let low = [Foe { dies: true, ..foe(1, 50_000.0, 0.0) }];
        assert_eq!(plan(&scene(&low, Some((0.0, 0.0)))), Some(Plan::Throw { target: 1, n: 1, kill: true, arm: true }));
    }

    #[test]
    fn q_into_the_crowd_then_r() {
        // one diving her, a pair 45k off: arm R first, then Q at the pair
        let foes = [foe(1, 5_000.0, -10_000.0), foe(2, 40_000.0, 24_000.0), foe(3, 44_000.0, 8_000.0)];
        let s = scene(&foes, Some((0.0, 0.0)));
        assert_eq!(plan(&s), Some(Plan::Throw { target: 2, n: 2, kill: false, arm: true }));
        let armed = Scene { r_ready: false, armed: true, ..scene(&foes, Some((0.0, 0.0))) };
        assert_eq!(plan(&armed), Some(Plan::Throw { target: 2, n: 2, kill: false, arm: false }));
        // the ball on its way to them: wait for the landing (or R now when it is not armed)
        let flying = Scene { ball: Some((40_000.0, 24_000.0)), ..armed };
        assert_eq!(plan(&flying), None);
        assert_eq!(plan(&scene(&foes, Some((40_000.0, 24_000.0)))), Some(Plan::Blast { n: 2, kill: false }));
        // the ball sent to an ally or flying back: not a place for the shockwave, Q still goes
        assert_eq!(plan(&scene(&foes, None)), Some(Plan::Throw { target: 2, n: 2, kill: false, arm: true }));
    }

    #[test]
    fn no_q_out_of_reach_low_or_walking_away() {
        let foes = [foe(2, 40_000.0, 24_000.0), foe(3, 44_000.0, 8_000.0)];
        // Q down
        assert_eq!(plan(&Scene { q_ready: false, ..scene(&foes, Some((0.0, 0.0))) }), None);
        // low
        assert_eq!(plan(&Scene { hp: 0.2, ..scene(&foes, Some((0.0, 0.0))) }), None);
        // the AI walks her away from them / toward them
        assert_eq!(plan(&Scene { walk: Some((-50_000.0, 0.0)), ..scene(&foes, Some((0.0, 0.0))) }), None);
        assert!(plan(&Scene { walk: Some((20_000.0, 0.0)), ..scene(&foes, Some((0.0, 0.0))) }).is_some());
        // beyond Q_REACH
        let far = [foe(2, 70_000.0, 0.0), foe(3, 75_000.0, 10_000.0)];
        assert_eq!(plan(&scene(&far, Some((0.0, 0.0)))), None);
        // the ball's controller off: the Q would fly straight back
        assert_eq!(plan(&Scene { controller: false, ..scene(&foes, Some((0.0, 0.0))) }), None);
    }

    #[test]
    fn r_is_armed_only_for_a_crowd_well_inside_q() {
        // 11-02: every arm came the tick the crowd crossed Q_REACH, 63k off, and the Q mostly missed them
        let edge = [foe(2, 58_000.0, 10_000.0), foe(3, 60_000.0, -8_000.0)];
        assert_eq!(plan(&scene(&edge, Some((0.0, 0.0)))), None);
        // armed already (by league_ult_press, say): the Q still goes that far
        let armed = Scene { r_ready: false, armed: true, ..scene(&edge, Some((0.0, 0.0))) };
        assert_eq!(plan(&armed), Some(Plan::Throw { target: 2, n: 2, kill: false, arm: false }));
    }

    #[test]
    fn where_the_ball_can_blow() {
        let me = (1.0, 2.0);
        assert_eq!(ball_point(None, me), Some(me));
        let b = |w| Some(Ball { at: (5.0, 6.0), w });
        assert_eq!(ball_point(b(Where::Home), me), Some(me));
        assert_eq!(ball_point(b(Where::Flying { to: (9.0, 9.0), speed: 1.0 }), me), Some((9.0, 9.0)));
        assert_eq!(ball_point(b(Where::Lying), me), Some((5.0, 6.0)));
        assert_eq!(ball_point(b(Where::Riding { ally: 3 }), me), Some((5.0, 6.0)));
        assert_eq!(ball_point(b(Where::Sent { ally: 3, speed: 1.0 }), me), None);
        assert_eq!(ball_point(b(Where::Back), me), None);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_orianna.py");
        let src = std::fs::read_to_string(path).expect("build_orianna.py");
        for (key, v) in [("q_range", Q_RANGE as usize), ("r_slot", R_SLOT as usize), ("r_r", R_R as usize)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_orianna.P");
        }
        assert!(CROWD < R_R && Q_REACH < Q_RANGE && Q_RANGE <= R_SLOT);
    }

    #[test]
    fn after_league_ult_press_and_farm() {
        // (below the unlock gate's top one: league_unlock_guard's test reads every add-on's sources)
        assert!(PRIORITY > 100 && PRIORITY > super::super::farm::PRIORITY);
    }
}
