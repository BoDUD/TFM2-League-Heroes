//! 鸦医 (`abysspact_corvus`) · 瘟疫医生 · 辅助
//!
//! 招牌机制「传染」疫雾蔓延 + 病人光环回血 + W「渡鸦」肩头啄击:
//! - 技能（Q 瘴瓶、W 渡鸦啄击、R 隔离区）给敌人种下 4 秒（240 ticks）疫病：每秒掉 2% 最大生命（魔法伤害）。
//! - 每秒每名染病敌人向 1.5 万内最近的一名没病的敌人传染疫病（英雄优先），播 `transmit` 绿泡特效与音效。
//!   病好了的人 `IMMUNE_TICKS` 内不会再被传染（技能照样能种）：以前好了马上又被旁边的人传回去，两个人、一线兵
//!   就能把疫病一直传下去，旁边的英雄一直掉血。
//! - 友方英雄每靠近一名染病的敌方**英雄**（2 万内），每秒回复 1% 最大生命（最多计 3 名 = 3%/秒）。病的小兵不算
//!   （以前算，兵线一染上，下路两人一直 3%/秒回血）。
//! - W「渡鸦」飞到身边一名友方英雄（没有就是自己）肩头停留 4 秒（带 `abysspact_corvus_raven_perch` buff 显示乌鸦贴图）：
//!   每秒啄一下该队友身边 3.2 万内最近的敌人，造成 `20 + 15% AP` 魔法伤害并令其染病。
//! - 只在 Q、R 的瓶子 / 圈子还在的时候走一遍全部单位找疫病请求：数据在出手时给他挂 `scan`（瓶子飞行 + 20 tick、
//!   圈子 5 秒 + 20 tick），平时不走。（以前看冷却跳起来认出放了技能，可冷却要等动作结束才开始走，Q 的请求那时早没了。）

use std::collections::{HashMap, HashSet};
use mod_api_stable::*;
// 写死的技能距离在大地图版跟着乘 1.3
use game_places::skill_scale::sk;

use crate::voice::{Cue, Voice};
use crate::{buffs_present, consume_buff, dist_sq};

pub const HERO: &str = "abysspact_corvus";
pub const PLAGUE_ASK: &str = "abysspact_corvus_plague_ask";
pub const PLAGUE_VIS: &str = "abysspact_corvus_plague";
pub const RAVEN_PERCH: &str = "abysspact_corvus_raven_perch";
pub const R_CAST_VOICE: &str = "abysspact_corvus_r_voice";
/// Q、R 出手时数据挂在他身上：挂着的时候才找疫病请求。
pub const SCAN: &str = "abysspact_corvus_scan";

pub const PLAGUE_TICKS: usize = 240; // 4.0s
pub const TICK_PERIOD: usize = 60;   // 1.0s pulse
pub const SPREAD_RADIUS: u64 = 15_000; // 1.5万
pub const HEAL_RADIUS: u64 = 20_000;   // 2.0万
pub const PECK_RADIUS: u64 = 32_000;   // 3.2万
pub const PLAGUE_PCT: usize = 2;       // 2% max HP / s
pub const MAX_HEAL_SICK: usize = 3;    // up to 3% max HP / s
/// 病好了以后这么多 tick 内不会再被传染。
pub const IMMUNE_TICKS: usize = 240;

pub fn plague_dot(max_hp: usize) -> usize {
    (max_hp.saturating_mul(PLAGUE_PCT) / 100).max(12)
}

pub fn ally_heal_amount(max_hp: usize, sick_nearby: usize) -> usize {
    let n = sick_nearby.min(MAX_HEAL_SICK);
    if n == 0 {
        0
    } else {
        (max_hp.saturating_mul(n) / 100).max(1)
    }
}

pub fn raven_peck_damage(ap: usize) -> usize {
    20 + ap.saturating_mul(15) / 100
}

/// 传染能不能落到 `id` 身上：没病，也不在病好后的免疫期里。
pub fn can_catch(id: usize, tick: usize, plagued: &HashMap<usize, usize>, immune: &HashMap<usize, usize>) -> bool {
    !plagued.get(&id).is_some_and(|&exp| exp > tick) && !immune.get(&id).is_some_and(|&until| until > tick)
}

/// 一名友方英雄身边 2 万内有几个染病的敌方英雄（`sick` 是 (位置, 是不是英雄)）。
pub fn sick_champions_near(ally: (u64, u64), sick: &[((u64, u64), bool)]) -> usize {
    let r2 = sk(HEAL_RADIUS) * sk(HEAL_RADIUS);
    sick.iter().filter(|(p, champ)| *champ && dist_sq(ally, *p) <= r2).count()
}

#[derive(Clone, Default)]
struct CorvusPassive {
    voice: Voice,
    /// Infected enemy entity id -> expire_tick.
    plagued: HashMap<usize, usize>,
    /// 病好了的人 -> 到哪一 tick 之前不会再被传染。
    immune: HashMap<usize, usize>,
    last_pulse_tick: usize,
}

impl CorvusPassive {
    /// 技能种下的疫病：不管免疫期。
    fn infect(&mut self, sim: &mut StableSim<'_>, target: usize, tick: usize) {
        self.plagued.insert(target, tick + PLAGUE_TICKS);
        self.immune.remove(&target);
        sim.entity_remove_buff(target, PLAGUE_VIS);
        sim.add_buff(target, &BuffV1::timed(PLAGUE_VIS, PLAGUE_TICKS));
    }

    fn pulse(&mut self, sim: &mut StableSim<'_>, caster: usize, my_team: usize, ap: usize, tick: usize) {
        // 病好了的记进免疫期；免疫期过了的忘掉
        let immune = &mut self.immune;
        immune.retain(|_, until| *until > tick);
        let mut sick: Vec<(usize, (u64, u64), usize, bool)> = Vec::new();
        self.plagued.retain(|&eid, &mut exp| {
            let Some(e) = sim.get_entity(eid).filter(|e| e.is_alive()) else { return false };
            if exp <= tick {
                immune.insert(eid, exp + IMMUNE_TICKS);
                return false;
            }
            sick.push((eid, e.pos(), e.hp().1, e.is_champion()));
            true
        });

        // 敌人、友方英雄各走一遍（不在每个病人身上再走全部单位）
        let mut foes: Vec<(usize, (u64, u64), bool)> = Vec::new();
        let mut allies: Vec<(usize, (u64, u64), usize)> = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() || e.is_tower() {
                continue;
            }
            if e.team() == my_team {
                if e.is_champion() {
                    allies.push((e.id(), e.pos(), e.hp().1));
                }
            } else {
                foes.push((e.id(), e.pos(), e.is_champion()));
            }
        }

        // 1. Plague 2% max-HP/s magic DoT + 1.5万 contagion to nearest uninfected enemy
        let spread_r2 = sk(SPREAD_RADIUS) * sk(SPREAD_RADIUS);
        let mut taken: HashSet<usize> = HashSet::new();
        let mut newly_infected: Vec<usize> = Vec::new();
        for &(sid, spos, smax_hp, _) in &sick {
            sim.deal_damage_typed(caster, sid, plague_dot(smax_hp), DamageTypeV1::Ap, AttackTypeV1::Skill);
            let best = foes
                .iter()
                .filter(|(id, pos, _)| {
                    !taken.contains(id) && can_catch(*id, tick, &self.plagued, &self.immune) && dist_sq(spos, *pos) <= spread_r2
                })
                .min_by_key(|(_, pos, champ)| {
                    let d2 = dist_sq(spos, *pos);
                    if *champ { d2 / 4 } else { d2 }
                })
                .map(|(id, _, _)| *id);
            if let Some(next_id) = best {
                taken.insert(next_id);
                newly_infected.push(next_id);
            }
        }

        let mut played_spread_sfx = false;
        for next_id in newly_infected {
            self.plagued.insert(next_id, tick + PLAGUE_TICKS);
            sim.entity_remove_buff(next_id, PLAGUE_VIS);
            sim.add_buff(next_id, &BuffV1::timed(PLAGUE_VIS, PLAGUE_TICKS));
            sim.play_view_effect("abysspact_corvus_transmit", caster, &InputTargetV1::target(next_id), 0, 0, 0);
            if !played_spread_sfx {
                sim.play_sfx("abysspact_corvus_transmit", caster, &InputTargetV1::target(next_id));
                played_spread_sfx = true;
            }
        }

        // 2. Ally aura heal: 1% max HP per sick enemy champion within 2.0万 (max 3%)
        let sick_spots: Vec<((u64, u64), bool)> = sick.iter().map(|s| (s.1, s.3)).collect();
        let mut played_heal_sfx = false;
        for &(aid, apos, amax_hp) in &allies {
            let amt = ally_heal_amount(amax_hp, sick_champions_near(apos, &sick_spots));
            if amt > 0 {
                sim.heal(caster, aid, amt);
                sim.play_view_effect("abysspact_corvus_heal", caster, &InputTargetV1::target(aid), 0, 0, 0);
                if !played_heal_sfx {
                    sim.play_sfx("abysspact_corvus_heal_lift", caster, &InputTargetV1::target(aid));
                    played_heal_sfx = true;
                }
            }
        }

        // 3. W「渡鸦」shoulder-perched Raven pecks nearest enemy within 3.2万 once/s & infects
        let peck_dmg = raven_peck_damage(ap);
        let peck_r2 = sk(PECK_RADIUS) * sk(PECK_RADIUS);
        for &(aid, apos, _) in &allies {
            let [perched] = buffs_present(sim, aid, [RAVEN_PERCH]);
            if !perched {
                continue;
            }
            let target = foes
                .iter()
                .filter(|(_, pos, _)| dist_sq(apos, *pos) <= peck_r2)
                .min_by_key(|(_, pos, champ)| {
                    let d2 = dist_sq(apos, *pos);
                    if *champ { d2 / 4 } else { d2 }
                })
                .map(|(id, _, _)| *id);
            if let Some(target_id) = target {
                sim.deal_damage_typed(caster, target_id, peck_dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                self.infect(sim, target_id, tick);
                sim.play_sfx("abysspact_corvus_raven_peck", caster, &InputTargetV1::target(target_id));
            }
        }
    }
}

impl StablePassive for CorvusPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.plagued.clear();
        self.immune.clear();
        self.last_pulse_tick = 0;
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
        self.plagued.remove(&victim);
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        self.voice.observe(entity);
        let Some((alive, my_team, ap)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.stat().magic_power))
        else {
            return;
        };
        if !alive {
            return;
        }
        let tick = sim.tick();

        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // Q 的瓶子、R 的圈子还在（他身上挂着数据给的 scan）才找疫病请求（W 的啄击是本被动自己种的）
        let [scan] = buffs_present(sim, entity, [SCAN]);
        if scan {
            let mut to_infect = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_alive() && e.team() != my_team && !e.is_tower() {
                    let id = e.id();
                    if buffs_present(sim, id, [PLAGUE_ASK])[0] {
                        to_infect.push(id);
                    }
                }
            }
            for eid in to_infect {
                sim.entity_remove_buff(eid, PLAGUE_ASK);
                self.infect(sim, eid, tick);
            }
        }

        // 1.0s periodic Plague DoT, contagion spread, ally aura heal, and W Raven pecks
        if tick.saturating_sub(self.last_pulse_tick) >= TICK_PERIOD {
            self.last_pulse_tick = tick;
            self.pulse(sim, entity, my_team, ap, tick);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_corvus:plague", CorvusPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn plague_dot_and_ally_heal_scale_as_designed() {
        assert_eq!(plague_dot(1000), 20);
        assert_eq!(plague_dot(2500), 50);
        assert_eq!(plague_dot(300), 12);
        assert_eq!(ally_heal_amount(1000, 0), 0);
        assert_eq!(ally_heal_amount(1000, 1), 10);
        assert_eq!(ally_heal_amount(1000, 3), 30);
        assert_eq!(ally_heal_amount(1000, 5), 30);
    }

    #[test]
    fn raven_peck_scales_with_15pct_ap() {
        assert_eq!(raven_peck_damage(0), 20);
        assert_eq!(raven_peck_damage(100), 35);
        assert_eq!(raven_peck_damage(200), 50);
    }

    #[test]
    fn a_cured_enemy_does_not_catch_it_back_at_once() {
        let mut plagued = HashMap::new();
        let mut immune = HashMap::new();
        assert!(can_catch(7, 100, &plagued, &immune));
        plagued.insert(7, 340);
        assert!(!can_catch(7, 200, &plagued, &immune), "still sick");
        // 340 病好了：免疫到 580
        plagued.remove(&7);
        immune.insert(7, 340 + IMMUNE_TICKS);
        assert!(!can_catch(7, 341, &plagued, &immune));
        assert!(!can_catch(7, 579, &plagued, &immune));
        assert!(can_catch(7, 580, &plagued, &immune));
    }

    #[test]
    fn only_sick_champions_count_for_the_heal() {
        let sick = [((10_000, 0), true), ((5_000, 0), false), ((9_000, 9_000), false), ((50_000, 0), true)];
        // 身边一个病的英雄（另一个太远）、两个病的小兵不算
        assert_eq!(sick_champions_near((0, 0), &sick), 1);
    }

    #[test]
    fn the_bottle_and_the_ring_open_the_scan_on_him() {
        // 冷却要等动作放完才走，认不出刚放了 Q / R：两招出手时数据给他挂 scan（两个活着的分支各一份）
        let kit = include_str!("../../../abysspact/champion/abysspact_corvus.data_champion");
        let q = &kit[kit.find("\"skill\"").expect("Q")..kit.find("\"skill2\"").expect("W")];
        let r = &kit[kit.find("\"ult\"").expect("R")..];
        assert_eq!(q.matches(&format!("\"name\": \"{SCAN}\"")).count(), 2);
        assert_eq!(r.matches(&format!("\"name\": \"{SCAN}\"")).count(), 2);
    }

    #[test]
    fn the_raven_goes_out_only_in_a_fight_and_lands_beside_him() {
        let kit = include_str!("../../../abysspact/champion/abysspact_corvus.data_champion");
        let w = &kit[kit.find("\"skill2\"").expect("W")..kit.find("\"ult\"").expect("R")];
        assert!(w.contains("\"casting_target\": \"EnemyChampion\""), "W waits for an enemy champion in reach");
        assert!(w.contains("\"AllyNotSelf\""), "the raven flies to an ally beside him");
        assert!(w.contains(RAVEN_PERCH));
    }
}
