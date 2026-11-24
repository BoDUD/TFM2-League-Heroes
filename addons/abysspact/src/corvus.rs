//! 鸦医 (`abysspact_corvus`) · 瘟疫医生 · 辅助
//!
//! 招牌机制「传染」疫雾蔓延 + 病人光环回血 + W「渡鸦」肩头啄击:
//! - 技能（Q 瘴瓶、W 渡鸦啄击、R 隔离区）给敌人种下 4 秒（240 ticks）疫病：每秒掉 2% 最大生命（魔法伤害）。
//! - 每秒每名染病敌人向 1.5 万内最近的一名未染病敌人传染疫病，播 `transmit` 绿泡特效与音效。
//! - 友方英雄每靠近一名染病敌人（2 万内），每秒回复 1% 最大生命（最多计 3 名 = 3%/秒）。
//! - W「渡鸦」飞到友方英雄肩头停留 4 秒（带 `abysspact_corvus_raven_perch` buff 显示乌鸦贴图）：
//!   每秒啄一下该队友身边 3.2 万内最近的敌人，造成 `20 + 15% AP` 魔法伤害并令其染病。

use std::collections::{HashMap, HashSet};
use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_corvus";
pub const PLAGUE_ASK: &str = "abysspact_corvus_plague_ask";
pub const PLAGUE_VIS: &str = "abysspact_corvus_plague";
pub const RAVEN_PERCH: &str = "abysspact_corvus_raven_perch";
pub const R_CAST_VOICE: &str = "abysspact_corvus_r_voice";

pub const PLAGUE_TICKS: usize = 240; // 4.0s
pub const TICK_PERIOD: usize = 60;   // 1.0s pulse
pub const SPREAD_RADIUS: u64 = 15_000; // 1.5万
pub const HEAL_RADIUS: u64 = 20_000;   // 2.0万
pub const PECK_RADIUS: u64 = 32_000;   // 3.2万
pub const PLAGUE_PCT: usize = 2;       // 2% max HP / s
pub const MAX_HEAL_SICK: usize = 3;    // up to 3% max HP / s

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

#[derive(Clone, Default)]
struct CorvusPassive {
    voice: Voice,
    /// Infected enemy entity id -> expire_tick.
    plagued: HashMap<usize, usize>,
    last_pulse_tick: usize,
}

impl CorvusPassive {
    fn infect(&mut self, sim: &mut StableSim<'_>, target: usize, tick: usize) {
        self.plagued.insert(target, tick + PLAGUE_TICKS);
        sim.entity_remove_buff(target, PLAGUE_VIS);
        sim.add_buff(target, &BuffV1::timed(PLAGUE_VIS, PLAGUE_TICKS));
    }

    fn pulse(&mut self, sim: &mut StableSim<'_>, caster: usize, my_team: usize, ap: usize, tick: usize) {
        // Snapshot currently living infected enemies
        let mut sick: Vec<(usize, (u64, u64), usize)> = Vec::new();
        self.plagued.retain(|&eid, &mut exp| {
            if exp <= tick {
                return false;
            }
            if let Some(e) = sim.get_entity(eid) {
                if e.is_alive() {
                    sick.push((eid, e.pos(), e.hp().1));
                    return true;
                }
            }
            false
        });

        let mut already_sick: HashSet<usize> = sick.iter().map(|&(id, _, _)| id).collect();
        let spread_r2 = SPREAD_RADIUS * SPREAD_RADIUS;
        let heal_r2 = HEAL_RADIUS * HEAL_RADIUS;
        let peck_r2 = PECK_RADIUS * PECK_RADIUS;

        // 1. Plague 2% max-HP/s magic DoT + 1.5万 contagion to nearest uninfected enemy
        let mut newly_infected: Vec<(usize, usize)> = Vec::new();
        let n_ent = sim.entity_count();
        for &(sid, spos, smax_hp) in &sick {
            sim.deal_damage_typed(caster, sid, plague_dot(smax_hp), DamageTypeV1::Ap, AttackTypeV1::Skill);

            // Pick nearest uninfected enemy within 1.5万 (champions prioritized)
            let mut best: Option<(u64, usize)> = None;
            for i in 0..n_ent {
                let Some(e) = sim.entity_at(i) else { continue };
                let eid = e.id();
                if !e.is_alive() || e.team() == my_team || e.is_tower() || already_sick.contains(&eid) {
                    continue;
                }
                let d2 = dist_sq(spos, e.pos());
                if d2 <= spread_r2 {
                    let score = if e.is_champion() { d2 / 4 } else { d2 };
                    if best.is_none_or(|(bd, _)| score < bd) {
                        best = Some((score, eid));
                    }
                }
            }
            if let Some((_, next_id)) = best {
                already_sick.insert(next_id);
                newly_infected.push((sid, next_id));
            }
        }

        let mut played_spread_sfx = false;
        for (_, next_id) in newly_infected {
            self.infect(sim, next_id, tick);
            sim.play_view_effect("abysspact_corvus_transmit", caster, &InputTargetV1::target(next_id), 0, 0, 0);
            if !played_spread_sfx {
                sim.play_sfx("abysspact_corvus_transmit", caster, &InputTargetV1::target(next_id));
                played_spread_sfx = true;
            }
        }

        // 2. Ally aura heal: 1% max HP per sick enemy within 2.0万 (max 3%)
        let mut allies: Vec<(usize, (u64, u64), usize, bool)> = Vec::new();
        for i in 0..n_ent {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_alive() && e.team() == my_team && e.is_champion() {
                let aid = e.id();
                let has_raven = has_buff(sim, aid, RAVEN_PERCH);
                allies.push((aid, e.pos(), e.hp().1, has_raven));
            }
        }

        let mut played_heal_sfx = false;
        for &(aid, apos, amax_hp, _) in &allies {
            let near = sick.iter().filter(|&&(_, spos, _)| dist_sq(apos, spos) <= heal_r2).count();
            let amt = ally_heal_amount(amax_hp, near);
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
        for &(_aid, apos, _, has_raven) in &allies {
            if !has_raven {
                continue;
            }
            let mut best: Option<(u64, usize)> = None;
            let n = sim.entity_count();
            for i in 0..n {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_alive() || e.team() == my_team || e.is_tower() {
                    continue;
                }
                let d2 = dist_sq(apos, e.pos());
                if d2 <= peck_r2 {
                    let score = if e.is_champion() { d2 / 4 } else { d2 };
                    if best.is_none_or(|(bd, _)| score < bd) {
                        best = Some((score, e.id()));
                    }
                }
            }
            if let Some((_, target_id)) = best {
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

        // Collect immediate plague applications from Q / R data layer
        let mut to_infect = Vec::new();
        let n_ent = sim.entity_count();
        for i in 0..n_ent {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_alive() && e.team() != my_team && !e.is_tower() && has_buff(sim, e.id(), PLAGUE_ASK) {
                to_infect.push(e.id());
            }
        }
        for eid in to_infect {
            sim.entity_remove_buff(eid, PLAGUE_ASK);
            self.infect(sim, eid, tick);
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
}
