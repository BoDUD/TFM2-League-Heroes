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
//!
//! 0.4.2（11-03 夜里的日志：一次启动 8 场、她骑了 14 次，`RIDE AI` / `CHASE` 0 次——全是游戏的 AI 自己按的 R，
//! `RIDE over after 1 ticks, 0 ridden`，别的 6 / 7 / 7 tick 就落地，打着打着就按）：
//! - 赶路的 R 对着**看得见的**敌方英雄按（游戏的 AI 自己按 R 时就用它的目标）：0.4.1 取实体表里第一个活着的敌方英雄，
//!   赶路时他多半在战争迷雾里，引擎不收这个输入，钩子一声不响地放弃了；引擎不收、或者一个看得见的都没有，记一行
//!   `RIDE REFUSED`（一串只记一行）。
//! - 游戏的 AI 自己按的 R 只在 `plan` 说该骑时放出去（照钩子的目标骑），不然不放（`R HELD`，tryndamere_rage 的
//!   `UltPlan::Hold`）：AI 的目标在 `FIGHT_R` 内就打他，不然接着走 AI 上一次让她走的路，再不然打 AI 的目标（走过去），
//!   都没有就站一下。

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
/// 追残血至少要这么远（0.4.1）：上鸟要引导半秒，近一点的走两步就打得到。11-03 13:05 那局她对 57475 外的残血上鸟，引导完人已
/// 进了射程，骑上 3 tick 就普攻落地放了鹰翼天翔，一步没骑，大招白交（用户：「奎因大招正常了吗」）。
pub const CHASE_MIN: f64 = 100_000.0;

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
            .filter(|f| f.1 >= CHASE_MIN && f.1 <= CHASE_R)
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

/// 一串连着的只记一行（league_ult_press 的 `ORDER_FRESH`）：游戏的 AI 每 4 tick 下一次命令，留着的 R 它每次都再按。
pub const ORDER_FRESH: usize = 30;

/// A line at `tick` starts a burst: none of its kind in the `ORDER_FRESH` ticks before (`last`: that kind's last tick;
/// a tick before it is another match).
pub fn new_burst(last: Option<usize>, tick: usize) -> bool {
    last.is_none_or(|t0| tick < t0 || tick > t0 + ORDER_FRESH)
}

/// 赶路的 R 按给谁（0.4.2）：游戏的 AI 自己按 R 时它的目标（它只点看得见的），不然离她最近的看得见的敌方英雄
/// （`foes` 只收看得见、选得中的）；一个都没有就按不出来。
pub fn travel_target(me: Pt, ai_target: Option<usize>, foes: &[Foe]) -> Option<usize> {
    ai_target
        .filter(|t| foes.iter().any(|f| f.id == *t))
        .or_else(|| foes.iter().min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at))).map(|f| f.id))
}

/// 游戏的 AI 自己按 R、`plan` 又不骑时她改做什么（0.4.2）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Instead {
    Attack(usize),
    Walk(Pt),
    Stand,
}

/// AI 的目标（`target`：实体和位置，看不见就没有）在 `FIGHT_R` 内就打他；不然接着走 AI 上一次让她走的路（`walk_to`，
/// 已经走到了不算）；再不然打 AI 的目标（走过去）；都没有就站一下。
pub fn instead(me: Pt, target: Option<(usize, Pt)>, walk_to: Option<Pt>) -> Instead {
    match (target, walk_to) {
        (Some((t, at)), _) if dist(me, at) <= FIGHT_R => Instead::Attack(t),
        (_, Some(w)) if dist(me, w) > 1_000.0 => Instead::Walk(w),
        (Some((t, _)), _) => Instead::Attack(t),
        _ => Instead::Stand,
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
    /// 每种行最近一次的 tick（`new_burst`：一串只记一行）。
    lines: Vec<(&'static str, usize)>,
}

/// 这一 tick 钩子要做的。
enum Todo {
    /// 骑上华洛（对 `target` 按 R）；`chase`：追谁、追到哪一 tick。
    Ride { target: usize, line: String, chase: Chase },
    /// 骑着追残血：改成打他。
    Chase(InputV1, String),
    /// 游戏的 AI 自己按的 R 不放：改做 `Instead`（`line` 说为什么）。
    Hold(Instead, String),
    /// 骑不成又没有 AI 的 R 要留：只记一行（为什么按不出来）。
    Refused(String),
    /// 该骑、钩子却没有看得见的目标：游戏的 AI 自己按的 R（它的目标它看得见）照放。
    Keep,
}

impl RideAi {
    /// One more line of `kind` at `tick`: true when it starts a burst (`new_burst`), the line to be written.
    fn burst(&mut self, kind: &'static str, tick: usize) -> bool {
        let last = self.lines.iter().find(|(k, _)| *k == kind).map(|&(_, t)| t);
        self.lines.retain(|(k, _)| *k != kind);
        self.lines.push((kind, tick));
        new_burst(last, tick)
    }

    /// `line` (a `kind` line) once a burst, through the launch-wide count.
    fn note(&mut self, kind: &'static str, tick: usize, line: &str) {
        if self.burst(kind, tick) {
            if let Some(k) = counted(kind) {
                wlog(format!("{line} #{k}"));
            }
        }
    }
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
        // the game's AI pressing this R itself (0.4.2): it goes out only when plan() says ride
        let ai_ult = was == Some(InputKindV1::Ult);
        let ai_target = base.filter(|_| ai_ult).and_then(|b| {
            (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
        });
        self.recalling = still_recalling(self.recalling, base);
        if let Some(b) = base.filter(|_| was == Some(InputKindV1::Move)) {
            self.walk_to = Some((b.x as f64, b.y as f64));
        }
        let (todo, here) = {
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
            let here = at(&me);
            let line = head(&sim, me.id());
            // the AI's target where she can see it (an attack on it, if the AI's R is held)
            let ai_seen = ai_target
                .and_then(|t| sim.get_entity(t))
                .filter(|e| e.is_alive() && e.is_targetable() && sim.is_visible(me.team(), e.id()))
                .map(|e| (e.id(), at(&e)));
            let todo = if riding(&me) {
                if self.recalling || busy(&me) {
                    return None;
                }
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
                Todo::Chase(attack, format!("{line} CHASE: on Valor after #{t}"))
            } else {
                let ready = me.cooldown(SkillSlotV1::Ult).is_some_and(|c| c.unlocked && c.remaining == 0);
                let foes: Vec<Foe> = (0..sim.entity_count())
                    .filter_map(|i| sim.entity_at(i))
                    .filter(|u| {
                        u.team() != me.team() && u.is_champion() && u.is_alive() && u.is_targetable()
                            && sim.is_visible(me.team(), u.id())
                    })
                    .map(|u| Foe { id: u.id(), at: at(&u), hp: u.hp().0 as f64 / u.hp().1.max(1) as f64 })
                    .collect();
                let hp = me.hp().0 as f64 / me.hp().1.max(1) as f64;
                let free = ready && !self.recalling && !busy(&me);
                match free.then(|| plan(here, hp, self.walk_to, &foes)).flatten() {
                    Some(plan) => {
                        // the ride's input needs an enemy champion as its target (the cast reaches the whole map): the prey,
                        // else one she can see - 0.4.1 took the first one in the entity list, mostly in the fog, and the
                        // game took no R on him (11-03 night logs: 0 RIDE AI in 8 matches)
                        let target = match plan {
                            Plan::Chase { target, .. } => Some(target),
                            Plan::Travel { .. } => travel_target(here, ai_target, &foes),
                        };
                        let (why, chase) = match plan {
                            Plan::Travel { far } => (format!("a walk of {far:.0} (to {:?})", self.walk_to), None),
                            Plan::Chase { target, d } => {
                                (format!("after #{target}, {d:.0} away and low"), Some((target, tick + R_RIDE_T + 40)))
                            }
                        };
                        match target {
                            Some(target) => Todo::Ride { target, line: format!("{line} RIDE AI: {why}"), chase },
                            None if ai_ult => Todo::Keep,
                            None => Todo::Refused(format!("{line} RIDE REFUSED: {why}, but no enemy champion in sight to \
                                                           press it on")),
                        }
                    }
                    None if ai_ult => {
                        let near = foes.iter().map(|f| dist(here, f.at)).fold(f64::INFINITY, f64::min);
                        let walk = self.walk_to.map_or("none".to_string(), |w| format!("{:.0}", dist(here, w)));
                        let why = if !ready {
                            "R not ready".to_string()
                        } else if self.recalling || busy(&me) {
                            "recalling or casting".to_string()
                        } else {
                            format!("no ride planned (nearest enemy champion {near:.0}, the walk {walk})")
                        };
                        Todo::Hold(instead(here, ai_seen, self.walk_to), format!("{line} R HELD: the AI's own R, {why}"))
                    }
                    None => return None,
                }
            };
            (todo, here)
        };
        match todo {
            Todo::Chase(input, line) => {
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                self.note("chase", tick, &line);
                Some(input)
            }
            Todo::Ride { target, line, chase } => {
                let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(target));
                if !ctx.is_valid_input(&input) {
                    // the game took no R on that target: the AI's own R (a ride all the same) goes out, else nothing
                    self.note("refused", tick, &format!("{} -> RIDE REFUSED: the game took no R on #{target}{}", line,
                                                        if ai_ult { ", the AI's own R kept" } else { "" }));
                    return None;
                }
                if chase.is_some() {
                    self.chase = chase;
                }
                self.note("ride_ai", tick, &line);
                Some(input)
            }
            Todo::Refused(line) => {
                self.note("refused", tick, &line);
                None
            }
            Todo::Keep => None,
            Todo::Hold(what, line) => {
                let stand = InputV1::move_to(here.0.max(0.0) as u64, here.1.max(0.0) as u64);
                let walk = |w: Pt| InputV1::move_to(w.0.max(0.0) as u64, w.1.max(0.0) as u64);
                let (input, did) = match what {
                    Instead::Attack(t) => {
                        let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                        match (ctx.is_valid_input(&attack), self.walk_to) {
                            (true, _) => (attack, format!("attacking #{t} instead")),
                            (false, Some(w)) => (walk(w), "walking on instead".to_string()),
                            (false, None) => (stand, "standing instead".to_string()),
                        }
                    }
                    Instead::Walk(w) => (walk(w), "walking on instead".to_string()),
                    Instead::Stand => (stand, "standing instead".to_string()),
                };
                self.note("r_held", tick, &format!("{line} - {did}"));
                Some(input)
            }
        }
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
        // just past it (11-03: 57475 away, in range by the time she sat on Valor, Skystrike after 3 ticks): on foot
        assert_eq!(plan(me, 0.8, None, &[foe(7, (157_475.0, 100_000.0), 0.2)]), None);
        assert!(CHASE_MIN > ATTACK_R * 1.5);
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
    fn the_travel_ride_is_pressed_on_a_champion_she_can_see() {
        // 11-03 night logs: 0.4.1 pressed it on the first enemy champion in the entity list, in the fog - never taken
        let me = (100_000.0, 100_000.0);
        let seen = [foe(4, (700_000.0, 700_000.0), 1.0), foe(9, (300_000.0, 100_000.0), 1.0)];
        assert_eq!(travel_target(me, None, &seen), Some(9), "the nearest one in sight");
        assert_eq!(travel_target(me, Some(4), &seen), Some(4), "the game's AI pressed R on one in sight: that one");
        assert_eq!(travel_target(me, Some(5), &seen), Some(9), "the AI's target out of sight: the nearest seen");
        assert_eq!(travel_target(me, None, &[]), None, "nobody in sight: no press (RIDE REFUSED)");
    }

    #[test]
    fn the_ais_own_r_turns_into_a_fight_or_the_walk() {
        // 11-03 night logs: the game's AI rode in fights (`RIDE over after 1 ticks, 0 ridden`): held unless plan() rides
        let me = (100_000.0, 100_000.0);
        let lane = Some((400_000.0, 100_000.0));
        assert_eq!(instead(me, Some((7, (150_000.0, 100_000.0))), lane), Instead::Attack(7), "its target in the fight");
        assert_eq!(instead(me, Some((7, (300_000.0, 100_000.0))), lane), Instead::Walk((400_000.0, 100_000.0)),
                   "its target far: on with the walk");
        assert_eq!(instead(me, Some((7, (300_000.0, 100_000.0))), Some(me)), Instead::Attack(7), "walked already");
        assert_eq!(instead(me, None, None), Instead::Stand);
    }

    #[test]
    fn a_burst_of_presses_is_one_line() {
        assert!(new_burst(None, 5000));
        assert!(!new_burst(Some(5000), 5000 + ORDER_FRESH));
        assert!(new_burst(Some(5000), 5001 + ORDER_FRESH), "the next press");
        assert!(new_burst(Some(5000), 100), "another match");
        let mut ai = RideAi::default();
        assert!(ai.burst("r_held", 5000));
        assert!((5004..5030).step_by(4).all(|t| !ai.burst("r_held", t)), "the AI's R held every 4 ticks: one line");
        assert!(ai.burst("refused", 5010), "kinds apart");
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
