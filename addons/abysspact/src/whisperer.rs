//! 呓语 (`abysspact_whisperer`) · 疯语者 · 中路法师
//!
//! 招牌机制「疯狂」连锁发狂:
//! - 技能命中敌人时由数据层挂上 `abysspact_whisperer_mad_ask1`（+1 层）或 `abysspact_whisperer_mad_ask3`（大招直接叠满 3 层）。
//! - 只有敌方英雄会疯：每人独立记 1–2 层疯狂（持续 4 秒 = 240 ticks），头顶同步显示 `madness_1` / `madness_2` / `madness_3`
//!   紫色漩涡。小兵、野怪身上的请求标记不理（以前小兵也叠层、也发狂，一个 W 砸在兵线上整线一起炸，旁边的英雄吃好几下）。
//! - 叠满 3 层时当场「发狂」：恐惧乱跑 1.5 秒（90 ticks），并以自己为中心向周围 1.5 万内的他的队友炸开 `80 + 60% AP` 魔法伤害
//!   （小兵、野怪也挨炸，但不叠层）；每个被炸到的英雄再叠 +1 层疯狂，人挤在一起时会一个传一个地连锁发狂。

use std::collections::{HashMap, HashSet, VecDeque};
use mod_api_stable::*;
// 写死的技能距离在大地图版跟着乘 1.3
use game_places::skill_scale::sk;

use crate::voice::{Cue, Voice};
use crate::{buffs_present, consume_buff, dist_sq, foe_champions};

pub const HERO: &str = "abysspact_whisperer";
pub const ASK_1: &str = "abysspact_whisperer_mad_ask1";
pub const ASK_3: &str = "abysspact_whisperer_mad_ask3";
pub const R_CAST_VOICE: &str = "abysspact_whisperer_r_voice";
pub const VIS_1: &str = "abysspact_whisperer_madness_1";
pub const VIS_2: &str = "abysspact_whisperer_madness_2";
pub const VIS_3: &str = "abysspact_whisperer_madness_3";
pub const VIS_RUNES: &str = "abysspact_whisperer_mad_runes";

pub const MADNESS_TICKS: usize = 240; // 4.0s stack duration
pub const FEAR_TICKS: u64 = 90;       // 1.5s fear
pub const BURST_RADIUS: u64 = 15_000; // 1.5万
pub const BURST_BASE: usize = 80;
pub const BURST_AP_PCT: usize = 60;

pub fn burst_damage(ap: usize) -> usize {
    BURST_BASE + ap.saturating_mul(BURST_AP_PCT) / 100
}

/// Pure stack accumulator used by both live passive and unit tests.
/// Returns `true` if `target` just reached 3 stacks and should erupt.
pub fn add_madness_stack(
    stacks: &mut HashMap<usize, (u8, usize)>,
    target: usize,
    add: u8,
    tick: usize,
) -> bool {
    let cur = stacks
        .get(&target)
        .filter(|&&(_, exp)| exp > tick)
        .map(|&(n, _)| n)
        .unwrap_or(0);
    let next = cur.saturating_add(add);
    if next >= 3 {
        stacks.remove(&target);
        true
    } else {
        stacks.insert(target, (next, tick + MADNESS_TICKS));
        false
    }
}

/// 一次发狂炸到的人里，哪些要再叠一层（只有英雄，已经在这一 tick 发过狂的不算）。
pub fn spread_to(neighbors: &[(usize, bool)], erupted: &HashSet<usize>) -> Vec<usize> {
    neighbors.iter().filter(|(id, champ)| *champ && !erupted.contains(id)).map(|(id, _)| *id).collect()
}

#[derive(Clone, Default)]
struct WhispererPassive {
    voice: Voice,
    /// Enemy champion entity id -> (stacks in 1..=2, expire_tick).
    stacks: HashMap<usize, (u8, usize)>,
}

impl WhispererPassive {
    fn sync_visual(sim: &mut StableSim<'_>, target: usize, count: u8, dur: usize) {
        sim.entity_remove_buff(target, VIS_1);
        sim.entity_remove_buff(target, VIS_2);
        sim.entity_remove_buff(target, VIS_3);
        let name = match count {
            1 => Some(VIS_1),
            2 => Some(VIS_2),
            3 => Some(VIS_3),
            _ => None,
        };
        if let Some(n) = name {
            sim.add_buff(target, &BuffV1::timed(n, dur));
        }
    }

    fn apply_stacks(
        &mut self,
        sim: &mut StableSim<'_>,
        caster: usize,
        my_team: usize,
        caster_pos: (u64, u64),
        ap: usize,
        initial: Vec<(usize, u8)>,
    ) {
        let tick = sim.tick();
        let mut queue: VecDeque<(usize, u8)> = initial.into_iter().collect();
        let mut erupted_this_tick: HashSet<usize> = HashSet::new();
        let rad_sq = sk(BURST_RADIUS) * sk(BURST_RADIUS);
        let dmg = burst_damage(ap);

        while let Some((victim, add)) = queue.pop_front() {
            if erupted_this_tick.contains(&victim) {
                continue;
            }
            let Some((alive, vpos)) = sim.get_entity(victim).map(|e| (e.is_alive(), e.pos())) else {
                continue;
            };
            if !alive {
                self.stacks.remove(&victim);
                continue;
            }

            if add_madness_stack(&mut self.stacks, victim, add, tick) {
                erupted_this_tick.insert(victim);
                // 1. Visuals & 1.5s Fear running away from Whisperer
                Self::sync_visual(sim, victim, 3, FEAR_TICKS as usize);
                sim.entity_remove_buff(victim, VIS_RUNES);
                sim.add_buff(victim, &BuffV1::timed(VIS_RUNES, FEAR_TICKS as usize));
                let mut fear = CcV1::of_kind(CcKindV1::Fear, FEAR_TICKS);
                fear.dx = (vpos.0 as i64).saturating_sub(caster_pos.0 as i64);
                fear.dy = (vpos.1 as i64).saturating_sub(caster_pos.1 as i64);
                if fear.dx == 0 && fear.dy == 0 {
                    fear.dx = 1000;
                }
                sim.apply_cc(victim, &fear);

                sim.play_view_effect("abysspact_whisperer_burst", caster, &InputTargetV1::target(victim), 0, 0, 0);
                sim.play_sfx("abysspact_whisperer_madness_burst", caster, &InputTargetV1::target(victim));

                // 2. 身边 1.5 万内他的队友（发狂一次才走一遍全部单位）
                let mut neighbors = Vec::new();
                let n_ent = sim.entity_count();
                for i in 0..n_ent {
                    let Some(e) = sim.entity_at(i) else { continue };
                    let eid = e.id();
                    if eid == victim || !e.is_alive() || e.team() == my_team || e.is_tower() {
                        continue;
                    }
                    if dist_sq(vpos, e.pos()) <= rad_sq {
                        neighbors.push((eid, e.is_champion()));
                    }
                }

                // 3. 都挨炸；英雄再叠一层（连锁）
                for &(nid, _) in &neighbors {
                    sim.deal_damage_typed(caster, nid, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                }
                for nid in spread_to(&neighbors, &erupted_this_tick) {
                    queue.push_back((nid, 1));
                }
            } else if let Some(&(cnt, exp)) = self.stacks.get(&victim) {
                Self::sync_visual(sim, victim, cnt, exp.saturating_sub(tick).max(1));
                sim.play_sfx("abysspact_whisperer_madness_stack", caster, &InputTargetV1::target(victim));
            }
        }
    }
}

impl StablePassive for WhispererPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.stacks.clear();
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(
        &mut self,
        sim: &mut StableSim<'_>,
        _player: usize,
        entity: usize,
        target: usize,
        _damage: &mut usize,
    ) {
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        self.stacks.remove(&victim);
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        self.voice.observe(entity);
        let Some((alive, my_team, my_pos, ap)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.stat().magic_power))
        else {
            return;
        };
        let tick = sim.tick();

        // Expire stale madness records
        self.stacks.retain(|&eid, &mut (_, exp)| {
            exp > tick && sim.get_entity(eid).is_some_and(|e| e.is_alive())
        });

        if !alive {
            return;
        }

        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 只看敌方英雄身上的请求标记（小兵、野怪的四 tick 后自己没了）
        let mut triggers: Vec<(usize, u8)> = Vec::new();
        for (eid, _) in foe_champions(sim, my_team) {
            let [ask3, ask1] = buffs_present(sim, eid, [ASK_3, ASK_1]);
            if ask3 {
                triggers.push((eid, 3));
            } else if ask1 {
                triggers.push((eid, 1));
            }
        }
        for &(eid, _) in &triggers {
            sim.entity_remove_buff(eid, ASK_3);
            sim.entity_remove_buff(eid, ASK_1);
        }
        if !triggers.is_empty() {
            self.apply_stacks(sim, entity, my_team, my_pos, ap, triggers);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_whisperer:madness", WhispererPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn madness_erupts_on_third_stack_and_expires_after_4s() {
        let mut m = HashMap::new();
        assert!(!add_madness_stack(&mut m, 10, 1, 100));
        assert_eq!(m.get(&10), Some(&(1, 100 + MADNESS_TICKS)));
        assert!(!add_madness_stack(&mut m, 10, 1, 200));
        assert_eq!(m.get(&10), Some(&(2, 200 + MADNESS_TICKS)));
        // 3rd stack erupts and clears
        assert!(add_madness_stack(&mut m, 10, 1, 300));
        assert!(!m.contains_key(&10));

        // Stack expires cleanly after 240 ticks
        assert!(!add_madness_stack(&mut m, 20, 2, 100));
        assert!(!add_madness_stack(&mut m, 20, 1, 100 + MADNESS_TICKS));
        assert_eq!(m.get(&20), Some(&(1, 100 + MADNESS_TICKS * 2)));
    }

    #[test]
    fn burst_damage_scales_with_60pct_ap() {
        assert_eq!(burst_damage(0), 80);
        assert_eq!(burst_damage(100), 140);
        assert_eq!(burst_damage(250), 230);
    }

    #[test]
    fn only_champions_catch_the_madness_from_a_burst() {
        let erupted: HashSet<usize> = [5].into_iter().collect();
        // 7、9 是英雄，8 是小兵，5 这一 tick 已经发过狂
        let near = [(7, true), (8, false), (9, true), (5, true)];
        assert_eq!(spread_to(&near, &erupted), vec![7, 9]);
    }

    #[test]
    fn the_eyes_slow_does_not_double_up() {
        // 睁眼每 60 tick 叠一次减速，减速要正好 60 tick，不然重叠的那几 tick 减速翻倍
        let kit = include_str!("../../../abysspact/champion/abysspact_whisperer.data_champion");
        let at = kit.find("\"abysspact_whisperer_w_slow\"").expect("the eye's slow");
        let rest = &kit[at..];
        let t = rest.find("\"tick\":").expect("the slow's ticks") + "\"tick\":".len();
        let ticks: String = rest[t..].trim_start().chars().take_while(|c| c.is_ascii_digit()).collect();
        assert_eq!(ticks, "60", "the eye's slow lasts its 60-tick period");
    }
}
