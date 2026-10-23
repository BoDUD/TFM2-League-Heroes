//! 阿兹尔的大招判断（用户 2026-10-23：「沙皇不会主动R大招反推回来 不像盲僧 没有那种感觉」「沙皇大招逻辑太差了」）：AI 钩子
//! `league_azir:shurima`。游戏的 AI 见到射程里有英雄就放 R，推的方向全凭运气；主包数据的 R 有两种推法——刚用 E 冲到英雄
//! 身上（`r_win` 开着）时绕到他身后、把他推回阿兹尔的队友那边（反推，盲僧的回旋踢），否则把人推离自己（正推）。本钩子替 AI
//! 挑时机（判断在 `call`，纯计算、单元测试）：
//!
//! 1. **R INSEC**：反推窗口 `r_win` 开着、R 好了：对他刚冲到的那个英雄（R 射程里最近的）按 R。
//! 2. **R PEEL**：R 好了、`PEEL_R` 内有敌方英雄贴着他，而且他生命不到 `PEEL_HP` 或身边 `CROWD_R` 内有两个以上敌方英雄：
//!    对贴得最近的那个按 R，正推出去。
//! 3. **E INSEC**：R 和 E 都好、场上有沙兵（E 要冲向沙兵）、`ALLY_R` 内有我方英雄（推回去有人接）、他生命不低于
//!    `INSEC_HP`：E 射程里、离他 `e_self` 以外（再近 E 是后跳）、不在敌方塔下、身边 `CROWD_R` 内敌方英雄不超过两个的英雄，
//!    选生命比例最低的，按 E 冲过去；数据随即打开 `r_win`，下一刻第 1 条接 R。
//! 4. **R HELD**：AI 自己想按 R，以上都不成立：不放（改成普攻它的目标，打不到就走过去）。
//!
//! 回城时（游戏 0.6.5 的 AI 自己决定回城）、被控住或正在放技能时不管。

use mod_api_stable::*;

use super::{az, counted, dist, head, wlog, ID};

/// 排在 league_ult_press（100）之后。
pub const PRIORITY: i32 = 110;
/// 贴脸：这么近的敌方英雄。
pub const PEEL_R: f64 = 22_000.0;
/// 自保：他的生命比例不到这个。
pub const PEEL_HP: f64 = 0.5;
/// 身边多少范围内的敌方英雄算一堆。
pub const CROWD_R: f64 = 30_000.0;
/// 反推要有队友接：这么近有我方英雄。
pub const ALLY_R: f64 = 60_000.0;
/// 主动开反推：他的生命比例不低于这个。
pub const INSEC_HP: f64 = 0.5;
/// 敌方塔的攻击范围（大约）。
pub const TOWER_REACH: f64 = 75_000.0;
/// 主包数据：E 的射程、再近 E 就是后跳（e_self）、R 的射程（build_azir.P，单元测试核对）。
pub const E_RANGE: f64 = 55_000.0;
pub const E_SELF: f64 = 25_000.0;
pub const R_RANGE: f64 = 40_000.0;
/// 两个单位的身体（射程算到身体边上，大约）。
pub const BODIES: f64 = 12_000.0;

pub type Pt = (f64, f64);

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub hp: f64,
    pub r_ready: bool,
    pub e_ready: bool,
    pub soldier: bool,
    pub r_win: bool,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: Pt,
    pub hp: f64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Call {
    /// (target, kind for the log)
    R(usize, &'static str),
    E(usize),
    /// the AI's R held: attack / walk to its target
    Hold(Option<usize>),
}

fn nearest(me: Pt, foes: &[Unit], within: f64) -> Option<&Unit> {
    foes.iter().filter(|u| dist(me, u.at) <= within).min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at)))
}

/// What to press (None: leave the AI's input).
pub fn call(me: &Me, foes: &[Unit], allies: &[Unit], towers: &[Pt], ai_wants_r: Option<Option<usize>>) -> Option<Call> {
    if me.r_ready {
        // 1. the window E opened: the kick back
        if me.r_win {
            if let Some(t) = nearest(me.at, foes, R_RANGE + BODIES) {
                return Some(Call::R(t.id, "insec"));
            }
        }
        // 2. someone on him and he is in trouble: push him off
        if let Some(t) = nearest(me.at, foes, PEEL_R) {
            let crowd = foes.iter().filter(|u| dist(me.at, u.at) <= CROWD_R).count();
            if me.hp < PEEL_HP || crowd >= 2 {
                return Some(Call::R(t.id, "peel"));
            }
        }
        // 3. dash onto one with a friend behind him: E now, R next
        if me.e_ready && me.soldier && me.hp >= INSEC_HP && allies.iter().any(|a| dist(me.at, a.at) <= ALLY_R) {
            let t = foes
                .iter()
                .filter(|u| {
                    let d = dist(me.at, u.at);
                    d > E_SELF && d <= E_RANGE + BODIES
                })
                .filter(|u| !towers.iter().any(|&w| dist(w, u.at) <= TOWER_REACH))
                .filter(|u| foes.iter().filter(|v| dist(u.at, v.at) <= CROWD_R).count() <= 2)
                .min_by(|a, b| a.hp.total_cmp(&b.hp));
            if let Some(t) = t {
                return Some(Call::E(t.id));
            }
        }
    }
    // 4. the AI's own R, none of the above: hold it
    ai_wants_r.map(Call::Hold)
}

// ===================== 游戏里 =====================

const STOP: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                             CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn ready(e: &StableEntity<'_, '_>, slot: SkillSlotV1) -> bool {
    e.cooldown(slot).is_some_and(|c| c.unlocked && (c.remaining == 0 || c.charges > 0))
}

fn share(hp: (usize, usize)) -> f64 {
    if hp.1 == 0 { 0.0 } else { hp.0 as f64 / hp.1 as f64 }
}

fn pt(e: &StableEntity<'_, '_>) -> Pt {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

#[derive(Clone, Default)]
pub struct Shurima {
    recalling: bool,
}

impl StablePlayerAi for Shurima {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:shurima")
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
        let player = ctx.player_id();
        let (c, line, spot) = {
            let sim = ctx.sim()?;
            let e = sim.get_player(player)?.champion()?;
            if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
                return None;
            }
            let (id, team) = (e.id(), e.team());
            let me = Me {
                at: pt(&e),
                hp: share(e.hp()),
                r_ready: ready(&e, SkillSlotV1::Ult) && !has(&e, &az("r_cd")),
                e_ready: ready(&e, SkillSlotV1::Skill2) && !has(&e, &az("e_cd")),
                soldier: ["ba", "bb", "bc"].iter().any(|s| has(&e, &az(s))),
                r_win: has(&e, &az("r_win")),
            };
            let (mut foes, mut allies, mut towers) = (Vec::new(), Vec::new(), Vec::new());
            for i in 0..sim.entity_count() {
                let Some(u) = sim.entity_at(i) else { continue };
                if !u.is_alive() || u.id() == id {
                    continue;
                }
                if u.is_tower() {
                    if u.team() != team {
                        towers.push(pt(&u));
                    }
                    continue;
                }
                if !u.is_champion() {
                    continue;
                }
                let unit = Unit { id: u.id(), at: pt(&u), hp: share(u.hp()) };
                if u.team() == team {
                    allies.push(unit);
                } else if u.is_targetable() {
                    foes.push(unit);
                }
            }
            let wants = base.filter(|b| b.kind == InputKindV1::Ult.code()).map(|b| {
                (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
            });
            let c = call(&me, &foes, &allies, &towers, wants)?;
            let on = match c {
                Call::R(t, _) | Call::E(t) | Call::Hold(Some(t)) => Some(t),
                Call::Hold(None) => None,
            };
            let spot = on.and_then(|t| foes.iter().find(|u| u.id == t)).map(|u| (u.at.0.max(0.0) as u64, u.at.1.max(0.0) as u64));
            let near = allies.iter().filter(|a| dist(me.at, a.at) <= ALLY_R).count();
            (c, format!("{} [hp {:.0}%, {near} allies near] on #{}", head(&sim, id), me.hp * 100.0,
                        on.map_or("-".to_string(), |t| t.to_string())), (spot, (me.at.0 as u64, me.at.1 as u64)))
        };
        let (input, kind, why) = match c {
            Call::R(t, k) => (InputV1::action(InputKindV1::Ult, InputTargetV1::target(t)), k,
                              if k == "insec" { "R INSEC: the kick back toward his team" } else { "R PEEL: pushed off him" }),
            Call::E(t) => (InputV1::action(InputKindV1::Skill2, InputTargetV1::target(t)), "e insec",
                           "E INSEC: onto him, the R to follow"),
            Call::Hold(t) => {
                let attack = t.map(|t| InputV1::action(InputKindV1::Attack, InputTargetV1::target(t)));
                let input = match attack.filter(|a| ctx.is_valid_input(a)) {
                    Some(a) => a,
                    None => {
                        let (x, y) = spot.0.unwrap_or(spot.1);
                        InputV1::move_to(x, y)
                    }
                };
                if let Some(n) = counted("r held") {
                    wlog(format!("{line} R HELD: no insec, no peel - the AI's R kept #{n}"));
                }
                return Some(input);
            }
        };
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(n) = counted(kind) {
            wlog(format!("{line} {why} #{n}"));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn me(hp: f64) -> Me {
        Me { at: (0.0, 0.0), hp, r_ready: true, e_ready: true, soldier: true, r_win: false }
    }

    fn u(id: usize, x: f64, hp: f64) -> Unit {
        Unit { id, at: (x, 0.0), hp }
    }

    #[test]
    fn the_window_kicks_back_at_once() {
        let m = Me { r_win: true, ..me(1.0) };
        assert_eq!(call(&m, &[u(1, 10_000.0, 1.0)], &[], &[], None), Some(Call::R(1, "insec")));
    }

    #[test]
    fn a_diver_on_a_hurt_azir_is_pushed_off() {
        assert_eq!(call(&me(0.4), &[u(1, 15_000.0, 1.0)], &[], &[], None), Some(Call::R(1, "peel")));
        // healthy and alone with him: no peel (and no ally for an insec: the AI's R is held)
        assert_eq!(call(&me(0.9), &[u(1, 15_000.0, 1.0)], &[], &[], Some(Some(1))), Some(Call::Hold(Some(1))));
    }

    #[test]
    fn an_insec_starts_with_e_onto_the_weakest_when_a_friend_is_behind() {
        let allies = [u(10, -30_000.0, 1.0)];
        let foes = [u(1, 45_000.0, 0.8), u(2, 50_000.0, 0.4)];
        assert_eq!(call(&me(0.9), &foes, &allies, &[], None), Some(Call::E(2)));
        // no friend near: nothing (the AI goes on)
        assert_eq!(call(&me(0.9), &foes, &[], &[], None), None);
        // too close for E's dash (it would hop back)
        assert_eq!(call(&me(0.9), &[u(1, 20_000.0, 0.5)], &allies, &[], None), None);
        // under an enemy tower: no
        assert_eq!(call(&me(0.9), &[u(1, 45_000.0, 0.5)], &allies, &[(80_000.0, 0.0)], None), None);
        // no soldier standing: E cannot dash
        let m = Me { soldier: false, ..me(0.9) };
        assert_eq!(call(&m, &foes, &allies, &[], None), None);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let src = include_str!("../../../tools/kit/build_azir.py");
        assert!(src.contains(&format!("\"e_range\": {}", E_RANGE as usize)));
        assert!(src.contains(&format!("\"e_self\": {}", E_SELF as usize)));
        assert!(src.contains(&format!("\"r_range\": {}", R_RANGE as usize)));
    }
}
