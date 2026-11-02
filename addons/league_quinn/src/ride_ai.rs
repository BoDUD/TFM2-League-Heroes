//! 深入敌后什么时候骑（0.4.0，用户 2026-11-03：「奎因参考LOL高手啊 这个要修的」）：11-02 夜里她唯一的一场 8 条命一次都没骑过——
//! 副本的大招只叫来华洛骑上，游戏的 AI 读不到这一招有什么用（数据里只有一个 buff），从来不按。照英雄联盟高手的用法，钩子
//! `league_quinn:ride_ai` 替 AI 按：
//!
//! - **赶路**：游戏的 AI 让她走去 `TRAVEL` 以外的地方（回城后回线上、去别的路游走、去支援打团），身边 `FIGHT_R` 内又没有敌方
//!   英雄（骑着挨一下打就会落地，交战中不骑）；
//! - **追残血**：`CHASE_R` 内有生命不到 `CHASE_LOW` 的敌方英雄，他在她的攻击距离外，她自己生命不低于 `MIN_HP`，身边没有别的
//!   敌方英雄：骑过去，骑着时游戏的 AI 想走开或打别人就改成打他，落地（这一下普攻）施放鹰翼天翔。
//!
//! 回城时、已经骑着、正在出招、大招没好（冷却或没解锁）时不按。副本的大招射程是全图（build_quinn 的 `r_ride_range`），
//! 哪里都按得出来；按的目标只是让游戏收下这个输入（骑乘不朝它冲）。日志 `RIDE AI`（赶路 / 追谁）、`CHASE`（骑着改打他）。

use mod_api_stable::*;

use super::{counted, dist, head, wlog, Pt, ID, RIDE, R_RIDE_T};

/// 在 league_ult_press（100）之后。
pub const PRIORITY: i32 = 110;
/// 游戏的 AI 让她走去这么远以外：骑上华洛赶路（6 秒、移速 +80%，比走过去快一倍）。
pub const TRAVEL: f64 = 200_000.0;
/// 这么近以内有敌方英雄就是在交战：不骑（骑着挨一下就落地）。
pub const FIGHT_R: f64 = 70_000.0;
/// 追残血：这么远以内、生命不到 `CHASE_LOW` 的敌方英雄，她自己生命不低于 `MIN_HP`。
pub const CHASE_R: f64 = 180_000.0;
pub const CHASE_LOW: f64 = 0.35;
pub const MIN_HP: f64 = 0.5;
/// 她的攻击距离（build_quinn.P 的 atk_range，测试核对）：够得着的就不用骑。
pub const ATTACK_R: f64 = 52_500.0;

/// 看得见的一个敌方英雄：位置和生命比例。
#[derive(Clone, Copy, Debug)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub hp: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Plan {
    /// 赶路：游戏的 AI 要她走 `far` 那么远。
    Travel { far: f64 },
    /// 追残血：骑去打他。
    Chase { target: usize, d: f64 },
}

/// 这一 tick 该不该骑、为什么。`hp`：她的生命比例；`walk_to`：游戏的 AI 最近一次让她走去的地方。
pub fn plan(me: Pt, hp: f64, walk_to: Option<Pt>, foes: &[Foe]) -> Option<Plan> {
    if hp >= MIN_HP {
        let low = foes
            .iter()
            .filter(|f| f.hp <= CHASE_LOW)
            .map(|f| (f.id, dist(me, f.at)))
            .filter(|f| f.1 > ATTACK_R && f.1 <= CHASE_R)
            .min_by(|a, b| a.1.total_cmp(&b.1));
        if let Some((target, d)) = low {
            if foes.iter().all(|o| o.id == target || dist(me, o.at) > FIGHT_R) {
                return Some(Plan::Chase { target, d });
            }
        }
    }
    if foes.iter().any(|f| dist(me, f.at) <= FIGHT_R) {
        return None;
    }
    let far = dist(me, walk_to?);
    (far >= TRAVEL).then_some(Plan::Travel { far })
}

/// 游戏的 AI 是不是正在让她回城（league_graves 的写法）：下了回城命令，之后没有新命令时回城还在走。
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// 正在出招（游戏记成 `Animation`）或被强制位移：不替 AI 按，按了会打断。
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];

fn busy(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| BUSY.iter().any(|k| k.code() == c.kind)))
}

fn riding(e: &StableEntity<'_, '_>) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == RIDE)
}

fn at(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

/// 骑着追的人：(实体, 到这个 tick 为止)。
type Chase = Option<(usize, usize)>;

#[derive(Clone, Default)]
pub struct RideAi {
    /// 游戏的 AI 最近一次让她走去的地方（这条命里）。
    walk_to: Option<Pt>,
    recalling: bool,
    chase: Chase,
    alive: bool,
}

impl StablePlayerAi for RideAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ride_ai")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let was = base.and_then(|b| InputKindV1::from_code(b.kind));
        self.recalling = still_recalling(self.recalling, base);
        if let Some(b) = base.filter(|_| was == Some(InputKindV1::Move)) {
            self.walk_to = Some((b.x as f64, b.y as f64));
        }
        let (input, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                self.alive = false;
                return None;
            }
            if !self.alive {
                // a new life: the last walk and chase belonged to the old one
                self.alive = true;
                self.walk_to = None;
                self.chase = None;
            }
            if self.recalling || busy(&me) {
                return None;
            }
            let here = at(&me);
            let line = head(&sim, me.id());
            if riding(&me) {
                // on Valor after a low one: what the game's AI wants elsewhere becomes an attack on him (the landing's
                // Skystrike comes with it)
                let (t, until) = self.chase?;
                let prey = sim.get_entity(t).filter(|e| e.is_alive() && e.is_targetable() && sim.is_visible(me.team(), t));
                if tick > until || prey.is_none() {
                    self.chase = None;
                    return None;
                }
                let on_him = base.is_some_and(|b| was == Some(InputKindV1::Attack) && b.target.target_id == t);
                if base.is_none() || on_him {
                    return None;
                }
                let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                (attack, format!("{line} CHASE: on Valor after #{t}"))
            } else {
                let ready = me.cooldown(SkillSlotV1::Ult).is_some_and(|c| c.unlocked && c.remaining == 0);
                if !ready {
                    return None;
                }
                let foes: Vec<Foe> = (0..sim.entity_count())
                    .filter_map(|i| sim.entity_at(i))
                    .filter(|u| {
                        u.team() != me.team() && u.is_champion() && u.is_alive() && u.is_targetable()
                            && sim.is_visible(me.team(), u.id())
                    })
                    .map(|u| Foe { id: u.id(), at: at(&u), hp: u.hp().0 as f64 / u.hp().1.max(1) as f64 })
                    .collect();
                let hp = me.hp().0 as f64 / me.hp().1.max(1) as f64;
                let plan = plan(here, hp, self.walk_to, &foes)?;
                // the ride's input needs an enemy champion as its target (the cast reaches the whole map): the prey, or any
                let target = match plan {
                    Plan::Chase { target, .. } => Some(target),
                    Plan::Travel { .. } => (0..sim.entity_count())
                        .filter_map(|i| sim.entity_at(i))
                        .find(|u| u.team() != me.team() && u.is_champion() && u.is_alive() && u.is_targetable())
                        .map(|u| u.id()),
                }?;
                let why = match plan {
                    Plan::Travel { far } => format!("a walk of {far:.0} (to {:?})", self.walk_to),
                    Plan::Chase { target, d } => {
                        self.chase = Some((target, tick + R_RIDE_T + 40));
                        format!("after #{target}, {d:.0} away and low")
                    }
                };
                (InputV1::action(InputKindV1::Ult, InputTargetV1::target(target)), format!("{line} RIDE AI: {why}"))
            }
        };
        if !ctx.is_valid_input(&input) {
            return None;
        }
        let kind = if line.contains("CHASE:") { "chase" } else { "ride_ai" };
        if let Some(k) = counted(kind) {
            wlog(format!("{line} #{k}"));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn foe(id: usize, at: Pt, hp: f64) -> Foe {
        Foe { id, at, hp }
    }

    #[test]
    fn a_long_walk_out_of_a_fight_is_ridden() {
        let me = (100_000.0, 100_000.0);
        // back to lane from the fountain: 400000 to walk, nobody near
        assert_eq!(plan(me, 1.0, Some((500_000.0, 100_000.0)), &[foe(1, (600_000.0, 600_000.0), 1.0)]),
                   Some(Plan::Travel { far: 400_000.0 }));
        // a short walk: on foot
        assert_eq!(plan(me, 1.0, Some((150_000.0, 100_000.0)), &[]), None);
        // an enemy champion close: in a fight, no ride
        assert_eq!(plan(me, 1.0, Some((500_000.0, 100_000.0)), &[foe(1, (150_000.0, 100_000.0), 1.0)]), None);
        // no walk known yet: nothing
        assert_eq!(plan(me, 1.0, None, &[]), None);
    }

    #[test]
    fn a_low_one_beyond_her_reach_is_chased() {
        let me = (100_000.0, 100_000.0);
        let low = foe(7, (220_000.0, 100_000.0), 0.2);
        assert_eq!(plan(me, 0.8, None, &[low]), Some(Plan::Chase { target: 7, d: 120_000.0 }));
        // within her attack: no need
        assert_eq!(plan(me, 0.8, None, &[foe(7, (140_000.0, 100_000.0), 0.2)]), None);
        // she is low herself: no chase
        assert_eq!(plan(me, 0.3, None, &[low]), None);
        // someone else beside her: no chase (and no ride)
        assert_eq!(plan(me, 0.8, Some((600_000.0, 100_000.0)), &[low, foe(8, (130_000.0, 100_000.0), 1.0)]), None);
        // too far to catch
        assert_eq!(plan(me, 0.8, None, &[foe(7, (400_000.0, 100_000.0), 0.2)]), None);
    }

    #[test]
    fn a_recall_runs_until_another_order() {
        assert!(still_recalling(false, Some(InputV1::return_home())));
        assert!(still_recalling(true, None));
        assert!(!still_recalling(true, Some(InputV1::move_to(1, 1))));
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_quinn.py")).unwrap();
        assert!(src.contains(&format!("\"atk_range\": {}", ATTACK_R as usize)), "atk_range is not {ATTACK_R}");
        assert!(src.contains("\"r_ride_range\": 960000"), "the copy's R must reach the whole map");
    }

    #[test]
    fn the_hook_comes_after_ult_press() {
        assert!(PRIORITY > 100);
    }
}
