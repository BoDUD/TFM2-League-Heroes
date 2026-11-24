//! 入殓 (`abysspact_undertaker`) · 抬棺人 · 打野坦克
//!
//! 招牌机制「棺盾」+ R「入殓」把敌方英雄装进棺材扛着走 2 秒再摔出来:
//! - 被动「棺盾」：常驻受到的普攻伤害 -15%；每 8 秒（480 ticks）充能一层技能护盾，令下一次受到的技能伤害 -30% 并播 `guard` 闪光。
//! - 大招「入殓」：将一名敌方英雄塞进棺材 2 秒（120 ticks）——期间目标被眩晕且实时跟随入殓移动（入殓移速 +20% 扛回自家阵地）；
//!   2 秒结束把棺材往地上一摔：造成 `150 + 8% 目标最大生命` 物理伤害并眩晕 1 秒（60 ticks）！

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, has_buff};

pub const HERO: &str = "abysspact_undertaker";
pub const COFFIN_SHIELD: &str = "abysspact_undertaker_coffin_shield";
pub const SKILL_GUARD: &str = "abysspact_undertaker_skill_guard";
pub const COFFIN_ASK: &str = "abysspact_undertaker_coffin_ask";
pub const IN_COFFIN: &str = "abysspact_undertaker_in_coffin";
pub const CARRYING: &str = "abysspact_undertaker_carrying";
pub const R_CAST_VOICE: &str = "abysspact_undertaker_r_voice";

pub const GUARD_CD: usize = 480;   // 8.0s
pub const CARRY_TICKS: usize = 120; // 2.0s carry
pub const SLAM_STUN: u64 = 60;      // 1.0s post-slam stun
pub const SLAM_BASE: usize = 150;
pub const SLAM_HP_PCT: usize = 8;

pub fn slam_damage(target_max_hp: usize) -> usize {
    SLAM_BASE + target_max_hp.saturating_mul(SLAM_HP_PCT) / 100
}

#[derive(Clone, Default)]
struct UndertakerPassive {
    voice: Voice,
    shield_applied: bool,
    guard_ready_at: usize,
    guard_armed: bool,
    last_hp: usize,
    /// Currently abducted enemy: (victim_entity_id, end_tick).
    abducted: Option<(usize, usize)>,
}

impl UndertakerPassive {
    fn finish_carry(&mut self, sim: &mut StableSim<'_>, entity: usize, slam: bool) {
        let Some((vid, _)) = self.abducted.take() else { return };
        sim.entity_remove_buff(entity, CARRYING);
        sim.entity_remove_buff(vid, IN_COFFIN);
        if !slam {
            return;
        }
        let Some((alive, max_hp)) = sim.get_entity(vid).map(|e| (e.is_alive(), e.hp().1)) else {
            return;
        };
        if !alive {
            return;
        }
        sim.play_view_effect("abysspact_undertaker_drop", entity, &InputTargetV1::target(vid), 0, 0, 0);
        sim.play_sfx("abysspact_undertaker_coffin_drop", entity, &InputTargetV1::target(vid));
        sim.deal_damage_typed(entity, vid, slam_damage(max_hp), DamageTypeV1::Ad, AttackTypeV1::Skill);
        sim.apply_cc(vid, &CcV1::stun(SLAM_STUN));
    }
}

impl StablePassive for UndertakerPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.shield_applied = false;
        self.guard_ready_at = 0;
        self.guard_armed = false;
        self.last_hp = sim.get_entity(entity).map(|e| e.hp().0).unwrap_or(0);
        self.abducted = None;
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
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.abducted = None;
        self.shield_applied = false;
        self.guard_armed = false;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, cur_hp)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.hp().0))
        else {
            return;
        };
        if !alive {
            self.finish_carry(sim, entity, false);
            return;
        }
        let tick = sim.tick();

        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 1. Passive「棺盾」: permanent -15% basic attack damage + 8s rechargeable -30% skill damage guard
        if !self.shield_applied {
            let mut base = BuffV1::named(COFFIN_SHIELD);
            base.base_attack_damaged_reduce = 15;
            sim.add_buff(entity, &base);
            self.shield_applied = true;
        }
        if !self.guard_armed && tick >= self.guard_ready_at {
            let mut g = BuffV1::named(SKILL_GUARD);
            g.skill_damaged_reduce = 30;
            sim.add_buff(entity, &g);
            self.guard_armed = true;
        } else if self.guard_armed && cur_hp + 25 < self.last_hp {
            // Consumed the 8s skill-guard charge on incoming burst
            sim.entity_remove_buff(entity, SKILL_GUARD);
            self.guard_armed = false;
            self.guard_ready_at = tick + GUARD_CD;
            sim.play_view_effect("abysspact_undertaker_guard", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_sfx("abysspact_undertaker_guard", entity, &InputTargetV1::target(entity));
        }
        self.last_hp = cur_hp;

        // 2. Check new R「入殓」coffin abduct marker on enemy champions
        if self.abducted.is_none() {
            let mut found = None;
            let n = sim.entity_count();
            for i in 0..n {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_champion() && e.is_alive() && e.team() != my_team && has_buff(sim, e.id(), COFFIN_ASK) {
                    found = Some(e.id());
                    break;
                }
            }
            if let Some(vid) = found {
                sim.entity_remove_buff(vid, COFFIN_ASK);
                self.abducted = Some((vid, tick + CARRY_TICKS));
                let mut speed = BuffV1::timed(CARRYING, CARRY_TICKS);
                speed.move_speed_mult = 20;
                sim.add_buff(entity, &speed);
                sim.add_buff(vid, &BuffV1::timed(IN_COFFIN, CARRY_TICKS));
                sim.apply_cc(vid, &CcV1::stun(12));
                sim.play_sfx("abysspact_undertaker_coffin_close", entity, &InputTargetV1::target(vid));
            }
        }

        // 3. Maintain active 2.0s coffin abduction: haul victim alongside Undertaker, then slam!
        if let Some((vid, end_tick)) = self.abducted {
            let v_alive = sim.get_entity(vid).is_some_and(|e| e.is_alive());
            if !v_alive {
                self.finish_carry(sim, entity, false);
            } else if tick >= end_tick {
                self.finish_carry(sim, entity, true);
            } else if tick % 4 == 0 {
                // Keep enemy trapped inside the coffin moving with Undertaker
                sim.entity_set_pos(vid, my_pos.0.saturating_add(4_000), my_pos.1);
                sim.apply_cc(vid, &CcV1::stun(8));
                if tick % 32 == 0 {
                    sim.play_sfx("abysspact_undertaker_coffin_leak", entity, &InputTargetV1::target(entity));
                }
            }
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_undertaker:coffin", UndertakerPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn coffin_slam_scales_with_8pct_target_max_hp() {
        assert_eq!(slam_damage(1000), 230);
        assert_eq!(slam_damage(2500), 350);
    }
}
