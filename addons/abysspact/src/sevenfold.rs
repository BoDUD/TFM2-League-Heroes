//! 七弹 (`abysspact_sevenfold`) · 魔弹射手 · 下路射手
//!
//! 招牌机制「第七颗」魔弹契约:
//! - 一轮 7 发子弹，头顶实时显示 `count_0..7` 计数；普攻消耗 1 发，Q「连发」消耗 3 发，W「装弹」翻滚直接将下一发换成第 7 颗。
//! - 每轮第 7 颗（以及 R「七发齐射」的最后一发）听深渊的：在 9 万内随机挑一名敌方英雄拐弯必中，
//!   造成 `160 + 140% AD` 真实伤害（`DamageTypeV1::Fixed`），同时七弹自己失去 8% 当前生命（保底 1 血），
//!   并进入 1.2 秒（72 ticks）装弹停火，随后装满 7 发开启下一轮。

use mod_api_stable::*;

use crate::oathbreaker::hp_after_burn;
use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_sevenfold";
pub const NATIVE_MARK: &str = "abysspact_sevenfold_native";
pub const Q_SHOTS_ASK: &str = "abysspact_sevenfold_q_shots";
pub const W_LOAD_ASK: &str = "abysspact_sevenfold_w_load";
pub const R_CURSE_ASK: &str = "abysspact_sevenfold_r_curse";
pub const R_CAST_VOICE: &str = "abysspact_sevenfold_r_voice";
pub const RELOADING_BUFF: &str = "abysspact_sevenfold_reloading";

pub const CLIP_SIZE: u8 = 7;
pub const CURSE_RANGE: u64 = 90_000; // 9.0万
pub const RELOAD_TICKS: usize = 72;  // 1.2s reload
pub const SELF_BURN_PCT: usize = 8;

pub fn seventh_true_damage(ad: usize) -> usize {
    135 + ad.saturating_mul(120) / 100
}

pub fn count_buff_name(n: u8) -> &'static str {
    match n {
        0 => "abysspact_sevenfold_count_0",
        1 => "abysspact_sevenfold_count_1",
        2 => "abysspact_sevenfold_count_2",
        3 => "abysspact_sevenfold_count_3",
        4 => "abysspact_sevenfold_count_4",
        5 => "abysspact_sevenfold_count_5",
        6 => "abysspact_sevenfold_count_6",
        _ => "abysspact_sevenfold_count_7",
    }
}

#[derive(Clone)]
struct SevenfoldPassive {
    voice: Voice,
    remaining: u8,
    reload_until: usize,
    shown_count: Option<u8>,
}

impl Default for SevenfoldPassive {
    fn default() -> Self {
        Self {
            voice: Voice::default(),
            remaining: CLIP_SIZE,
            reload_until: 0,
            shown_count: None,
        }
    }
}

impl SevenfoldPassive {
    fn sync_count(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if self.shown_count == Some(self.remaining) {
            return;
        }
        for k in 0..=CLIP_SIZE {
            sim.entity_remove_buff(entity, count_buff_name(k));
        }
        sim.add_buff(entity, &BuffV1::named(count_buff_name(self.remaining)));
        self.shown_count = Some(self.remaining);
    }

    fn fire_seventh(&mut self, sim: &mut StableSim<'_>, entity: usize, rng: u64, enter_reload: bool) {
        let Some((my_team, my_pos, ad, cur_hp)) = sim
            .get_entity(entity)
            .map(|e| (e.team(), e.pos(), e.stat().attack, e.hp().0))
        else {
            return;
        };

        // Pick a RANDOM living enemy champion within 9万 (the Abyss chooses!)
        let r2 = CURSE_RANGE * CURSE_RANGE;
        let mut cands = Vec::new();
        let n = sim.entity_count();
        for i in 0..n {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_alive() && e.is_champion() && e.team() != my_team && dist_sq(my_pos, e.pos()) <= r2 {
                cands.push(e.id());
            }
        }

        if !cands.is_empty() {
            let idx = (rng.wrapping_add(sim.tick() as u64) as usize) % cands.len();
            let victim = cands[idx];
            sim.play_view_effect("abysspact_sevenfold_abyss_eye", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_view_effect("abysspact_sevenfold_curse_hit", entity, &InputTargetV1::target(victim), 0, 0, 0);
            sim.play_sfx("abysspact_sevenfold_abyss_eye", entity, &InputTargetV1::target(entity));
            sim.play_sfx("abysspact_sevenfold_curse_burst", entity, &InputTargetV1::target(victim));
            sim.deal_damage_typed(entity, victim, seventh_true_damage(ad), DamageTypeV1::Fixed, AttackTypeV1::Skill);

            // Pay the Abyss's price: lose 8% current HP (never lethal)
            let next_hp = hp_after_burn(cur_hp, SELF_BURN_PCT);
            if next_hp < cur_hp {
                sim.entity_set_hp(entity, next_hp);
            }
        }

        if enter_reload {
            self.remaining = 0;
            self.reload_until = sim.tick() + RELOAD_TICKS;
            sim.add_buff(entity, &BuffV1::timed(RELOADING_BUFF, RELOAD_TICKS));
            sim.apply_cc(entity, &CcV1::of_kind(CcKindV1::BlockAttack, RELOAD_TICKS as u64));
            self.sync_count(sim, entity);
        }
    }

    fn spend(&mut self, sim: &mut StableSim<'_>, entity: usize, shots: u8, rng: u64) {
        if self.reload_until > sim.tick() || self.remaining == 0 {
            return;
        }
        if shots >= self.remaining {
            self.fire_seventh(sim, entity, rng, true);
        } else {
            self.remaining -= shots;
            if self.remaining == 1 {
                sim.play_sfx("abysspact_sevenfold_charge_ping", entity, &InputTargetV1::target(entity));
            }
            self.sync_count(sim, entity);
        }
    }
}

impl StablePassive for SevenfoldPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.remaining = CLIP_SIZE;
        self.reload_until = 0;
        self.shown_count = None;
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
        let seed = sim.seed().wrapping_add(target as u64);
        self.spend(sim, entity, 1, seed);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.remaining = CLIP_SIZE;
        self.reload_until = 0;
        self.shown_count = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, rng: u64, _player: usize, entity: usize) {
        let alive = sim.get_entity(entity).is_some_and(|e| e.is_alive());
        if !alive {
            return;
        }
        let tick = sim.tick();
        if !has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }
        if self.shown_count.is_none() {
            self.sync_count(sim, entity);
        }

        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // Finish 1.2s reload -> refill clip to 7
        if self.reload_until > 0 && tick >= self.reload_until {
            self.reload_until = 0;
            self.remaining = CLIP_SIZE;
            sim.entity_remove_buff(entity, RELOADING_BUFF);
            self.sync_count(sim, entity);
        }

        // Q「连发」: counts as 3 bullets toward the 7th!
        if consume_buff(sim, entity, Q_SHOTS_ASK) {
            self.spend(sim, entity, 3, rng);
        }

        // W「装弹」: immediately loads the 7th Abyss bullet as the very next shot!
        if consume_buff(sim, entity, W_LOAD_ASK) {
            self.reload_until = 0;
            sim.entity_remove_buff(entity, RELOADING_BUFF);
            self.remaining = 1;
            self.sync_count(sim, entity);
            sim.play_sfx("abysspact_sevenfold_charge_ping", entity, &InputTargetV1::target(entity));
        }

        // R「七发齐射」: the 7th round of the salvo is also a guaranteed Abyss bullet!
        if consume_buff(sim, entity, R_CURSE_ASK) {
            self.fire_seventh(sim, entity, rng, false);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_sevenfold:bullets", SevenfoldPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn seventh_bullet_true_damage_and_count_names() {
        assert_eq!(seventh_true_damage(100), 255);
        assert_eq!(seventh_true_damage(200), 375);
        assert_eq!(count_buff_name(0), "abysspact_sevenfold_count_0");
        assert_eq!(count_buff_name(7), "abysspact_sevenfold_count_7");
    }
}
