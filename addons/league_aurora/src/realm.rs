//! 阿萝拉的大招判断（用户 2026-10-24：「阿罗拉大招逻辑怎么和LOL里面高手的不太一样」）：AI 钩子 `league_aurora:realm`。
//! 游戏的 AI 见到射程里有敌方英雄就按 R，于是她跳到第一个看见的人身上——满血的坦克、敌方塔下、对面五个人中间都跳。
//! 英雄联盟里会玩的阿萝拉把「双界合一」留着做三件事：把一堆人关进领域里开团、关住想跑的残血收掉、被人贴脸时砸在他身上
//! （落地的冲击波接怪奇喷涌，喷完后跳，领域减着他的速）。本钩子替 AI 挑时机（判断在 `call`，纯计算、单元测试）：
//!
//! 1. **R PEEL**：`PEEL_R` 内有敌方英雄贴着她、她生命不到 `PEEL_HP`：对贴得最近的那个按 R（落地接 E 后跳，领域留下减速）。
//! 2. **R TRAP**：她生命不低于 `TRAP_HP`；R 射程里的敌方英雄，身边 `R_ZONE`（领域的半径）内有两个以上敌方英雄（含他），
//!    不在敌方塔下，他身边 `ALLY_R` 内至少有一个我方英雄，那一堆敌方英雄不比这些我方英雄（含她）多一个以上：按 R，挑领域里
//!    人最多的，一样多挑生命比例最低的。
//! 3. **R KILL**：她生命不低于 `KILL_SELF_HP`；R 射程里生命比例不到 `KILL_HP` 的敌方英雄，身边 `CROWD_R` 内的敌方英雄不超过
//!    两个，不在敌方塔下（生命不到 `DIVE_HP` 的除外）：按 R，挑生命比例最低的。
//! 4. **R HELD**：AI 自己想按 R，以上都不成立：不放（改成普攻它的目标，打不到就走过去）。
//!
//! 第 1–3 条在 AI 没想按 R 时也按（游戏的 AI 不一定在好时机按）。回城时、被控住或正在放技能时不管。

use mod_api_stable::*;

use super::{counted, dist, head, wlog, ID};

/// 排在 league_ult_press（100）之后。
pub const PRIORITY: i32 = 110;
/// 贴脸：这么近的敌方英雄。
pub const PEEL_R: f64 = 22_000.0;
/// 自保：她的生命比例不到这个。
pub const PEEL_HP: f64 = 0.5;
/// 开团：她的生命比例不低于这个。
pub const TRAP_HP: f64 = 0.4;
/// 我方英雄算在场：离目标这么近。
pub const ALLY_R: f64 = 60_000.0;
/// 收人头：目标的生命比例不到这个。
pub const KILL_HP: f64 = 0.4;
/// 收人头：她的生命比例不低于这个。
pub const KILL_SELF_HP: f64 = 0.3;
/// 收人头时目标身边多少范围内的敌方英雄算一堆（超过两个不去）。
pub const CROWD_R: f64 = 30_000.0;
/// 敌方塔下也去收：目标的生命比例不到这个。
pub const DIVE_HP: f64 = 0.2;
/// 敌方塔的攻击范围（大约）。
pub const TOWER_REACH: f64 = 75_000.0;
/// 主包数据：R 的射程、领域的半径（build_aurora.P，单元测试核对）。
pub const R_RANGE: f64 = 60_000.0;
pub const R_ZONE: f64 = 38_000.0;
/// 两个单位的身体（射程算到身体边上，大约）。
pub const BODIES: f64 = 12_000.0;

pub type Pt = (f64, f64);

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub hp: f64,
    pub r_ready: bool,
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
    /// the AI's R held: attack / walk to its target
    Hold(Option<usize>),
}

fn near(at: Pt, units: &[Unit], within: f64) -> usize {
    units.iter().filter(|u| dist(at, u.at) <= within).count()
}

fn towered(at: Pt, towers: &[Pt]) -> bool {
    towers.iter().any(|&w| dist(w, at) <= TOWER_REACH)
}

/// What to press (None: leave the AI's input).
pub fn call(me: &Me, foes: &[Unit], allies: &[Unit], towers: &[Pt], ai_wants_r: Option<Option<usize>>) -> Option<Call> {
    if me.r_ready {
        // 1. someone on her and she is hurt: slam him (the landing's E hops her back)
        let close = foes.iter().filter(|u| dist(me.at, u.at) <= PEEL_R).min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at)));
        if let (Some(t), true) = (close, me.hp < PEEL_HP) {
            return Some(Call::R(t.id, "peel"));
        }
        let reach: Vec<&Unit> = foes.iter().filter(|u| dist(me.at, u.at) <= R_RANGE + BODIES).collect();
        // 2. two or more inside the realm, a friend there, not more of them than of us (+1), not under their tower
        if me.hp >= TRAP_HP {
            let t = reach
                .iter()
                .map(|u| (*u, near(u.at, foes, R_ZONE)))
                .filter(|&(u, n)| {
                    let ours = 1 + near(u.at, allies, ALLY_R);
                    n >= 2 && ours >= 2 && n <= ours + 1 && !towered(u.at, towers)
                })
                .max_by(|a, b| a.1.cmp(&b.1).then(b.0.hp.total_cmp(&a.0.hp)));
            if let Some((t, _)) = t {
                return Some(Call::R(t.id, "trap"));
            }
        }
        // 3. a low one in reach, not deep in his team
        if me.hp >= KILL_SELF_HP {
            let t = reach
                .iter()
                .filter(|u| u.hp < KILL_HP && near(u.at, foes, CROWD_R) <= 2 && (u.hp < DIVE_HP || !towered(u.at, towers)))
                .min_by(|a, b| a.hp.total_cmp(&b.hp));
            if let Some(t) = t {
                return Some(Call::R(t.id, "kill"));
            }
        }
    }
    // 4. the AI's own R, none of the above: hold it
    ai_wants_r.map(Call::Hold)
}

// ===================== 游戏里 =====================

const STOP: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                             CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

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
pub struct Realm {
    recalling: bool,
}

impl StablePlayerAi for Realm {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:realm")
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
            let me = Me { at: pt(&e), hp: share(e.hp()), r_ready: ready(&e, SkillSlotV1::Ult) };
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
                Call::R(t, _) | Call::Hold(Some(t)) => Some(t),
                Call::Hold(None) => None,
            };
            let target = on.and_then(|t| foes.iter().find(|u| u.id == t));
            let spot = target.map(|u| (u.at.0.max(0.0) as u64, u.at.1.max(0.0) as u64));
            let crowd = target.map_or(0, |u| near(u.at, &foes, R_ZONE));
            (c, format!("{} [hp {:.0}%] on #{} ({crowd} in the realm, hp {:.0}%)", head(&sim, id), me.hp * 100.0,
                        on.map_or("-".to_string(), |t| t.to_string()), target.map_or(0.0, |u| u.hp * 100.0)),
             (spot, (me.at.0 as u64, me.at.1 as u64)))
        };
        let (input, kind, why) = match c {
            Call::R(t, k) => (InputV1::action(InputKindV1::Ult, InputTargetV1::target(t)), k, match k {
                "peel" => "R PEEL: slammed the diver",
                "trap" => "R TRAP: the realm over a crowd",
                _ => "R KILL: the low one trapped",
            }),
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
                    wlog(format!("{line} R HELD: no crowd, no kill, no peel - the AI's R kept #{n}"));
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
        Me { at: (0.0, 0.0), hp, r_ready: true }
    }

    fn u(id: usize, x: f64, hp: f64) -> Unit {
        Unit { id, at: (x, 0.0), hp }
    }

    #[test]
    fn a_diver_on_a_hurt_aurora_is_slammed() {
        assert_eq!(call(&me(0.4), &[u(1, 15_000.0, 1.0)], &[], &[], None), Some(Call::R(1, "peel")));
        // healthy, one full champion in front of her: the AI's R is held
        assert_eq!(call(&me(0.9), &[u(1, 15_000.0, 1.0)], &[], &[], Some(Some(1))), Some(Call::Hold(Some(1))));
        assert_eq!(call(&me(0.9), &[u(1, 40_000.0, 1.0)], &[], &[], None), None);
    }

    #[test]
    fn the_realm_goes_over_the_biggest_crowd() {
        let allies = [u(10, 20_000.0, 1.0)];
        let foes = [u(1, 50_000.0, 1.0), u(2, 60_000.0, 0.7), u(3, 90_000.0, 1.0), u(4, 200_000.0, 1.0)];
        // #2 has #1 and #3 in its realm (3), #1 has #2 (2)
        assert_eq!(call(&me(0.9), &foes, &allies, &[], None), Some(Call::R(2, "trap")));
        // no friend of hers there: no engage
        assert_eq!(call(&me(0.9), &foes, &[], &[], None), None);
        // under their tower: no
        assert_eq!(call(&me(0.9), &foes, &allies, &[(60_000.0, 0.0)], None), None);
        // she is low: no engage
        assert_eq!(call(&me(0.35), &foes, &allies, &[], None), None);
    }

    #[test]
    fn a_low_one_is_trapped_unless_he_is_deep_in_his_team() {
        assert_eq!(call(&me(0.9), &[u(1, 50_000.0, 0.3)], &[], &[], None), Some(Call::R(1, "kill")));
        let deep = [u(1, 50_000.0, 0.3), u(2, 60_000.0, 1.0), u(3, 65_000.0, 1.0)];
        assert_eq!(call(&me(0.9), &deep, &[], &[], Some(Some(1))), Some(Call::Hold(Some(1))));
        // under the tower only when nearly dead
        let tower = [(60_000.0, 0.0)];
        assert_eq!(call(&me(0.9), &[u(1, 50_000.0, 0.3)], &[], &tower, None), None);
        assert_eq!(call(&me(0.9), &[u(1, 50_000.0, 0.15)], &[], &tower, None), Some(Call::R(1, "kill")));
        // out of reach
        assert_eq!(call(&me(0.9), &[u(1, 90_000.0, 0.1)], &[], &[], None), None);
    }

    #[test]
    fn nothing_without_the_ult() {
        let m = Me { r_ready: false, ..me(0.3) };
        assert_eq!(call(&m, &[u(1, 10_000.0, 0.1)], &[], &[], None), None);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let src = include_str!("../../../tools/kit/build_aurora.py");
        assert!(src.contains(&format!("\"r_range\": {}", R_RANGE as usize)));
        assert!(src.contains(&format!("\"r_zone\": {}", R_ZONE as usize)));
    }
}
