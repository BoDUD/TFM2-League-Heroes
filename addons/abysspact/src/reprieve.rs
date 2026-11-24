//! 缓刑 (`abysspact_reprieve`) · 囚徒 · 上路坦克
//!
//! 招牌机制「缓刑」暂扣伤害 + 击杀/助攻一笔勾销:
//! - 受到的伤害有 50%（W「认罪」嘲讽期间 1.25 秒提升至 70%）暂不立即扣血，记入「刑期池」（上限最大生命的 60%），
//!   在接下来 4 秒（240 ticks）内平滑还清。
//! - 缓刑或 6 万范围内的友军击杀/助攻敌方英雄时，当前全部「刑期池」一笔勾销并爆开 `absolve` 刑印金光！
//! - 刑期池 > 0 时挂上 `abysspact_reprieve_tally_light` 胸口刻痕亮片特效。

use std::collections::HashSet;
use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_reprieve";
pub const NATIVE_MARK: &str = "abysspact_reprieve_native";
pub const GUILT_BUFF: &str = "abysspact_reprieve_guilt";
pub const TALLY_LIGHT: &str = "abysspact_reprieve_tally_light";
pub const R_CAST_VOICE: &str = "abysspact_reprieve_r_voice";

pub const BASE_DEFER_PCT: usize = 50;
pub const GUILT_DEFER_PCT: usize = 70;
pub const CAP_MAX_HP_PCT: usize = 60;
pub const PAY_TICKS: usize = 240;     // 4.0s
pub const PAY_STEP: usize = 12;       // 0.2s per payback pulse (20 pulses over 4s)
pub const ABSOLVE_RANGE: u64 = 60_000; // 6.0万

pub fn defer_amount(incoming: usize, guilty: bool, current_pool: usize, max_hp: usize) -> usize {
    let pct = if guilty { GUILT_DEFER_PCT } else { BASE_DEFER_PCT };
    let cap = max_hp.saturating_mul(CAP_MAX_HP_PCT) / 100;
    let room = cap.saturating_sub(current_pool);
    (incoming.saturating_mul(pct) / 100).min(room)
}

#[derive(Clone, Copy)]
struct DebtBucket {
    remaining: usize,
    per_step: usize,
    attacker: usize,
}

#[derive(Clone, Default)]
struct ReprievePassive {
    voice: Voice,
    native_marked: bool,
    buckets: Vec<DebtBucket>,
    in_payback: bool,
    last_pay_tick: usize,
    last_tally_vfx: usize,
    tally_shown: bool,
    alive_enemies: HashSet<usize>,
}

impl ReprievePassive {
    fn total_pool(&self) -> usize {
        self.buckets.iter().map(|b| b.remaining).sum()
    }

    fn sync_tally_visual(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        let has_debt = self.total_pool() > 0;
        if has_debt && !self.tally_shown {
            sim.add_buff(entity, &BuffV1::named(TALLY_LIGHT));
            self.tally_shown = true;
        } else if !has_debt && self.tally_shown {
            sim.entity_remove_buff(entity, TALLY_LIGHT);
            self.tally_shown = false;
        }
    }

    fn absolve(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if self.buckets.is_empty() {
            return;
        }
        self.buckets.clear();
        self.sync_tally_visual(sim, entity);
        sim.play_view_effect("abysspact_reprieve_absolve", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_reprieve_absolve", entity, &InputTargetV1::target(entity));
    }
}

impl StablePassive for ReprievePassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.native_marked = false;
        self.buckets.clear();
        self.in_payback = false;
        self.last_pay_tick = 0;
        self.last_tally_vfx = 0;
        self.tally_shown = false;
        self.alive_enemies.clear();
        sim.entity_remove_buff(entity, TALLY_LIGHT);
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

    fn on_damaged(
        &mut self,
        sim: &mut StableSim<'_>,
        _player: usize,
        entity: usize,
        attacker: usize,
        damage: usize,
    ) {
        if self.in_payback || damage == 0 {
            return;
        }
        let Some((alive, cur_hp, max_hp)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.hp().0, e.hp().1))
        else {
            return;
        };
        if !alive || max_hp == 0 {
            return;
        }
        let guilty = has_buff(sim, entity, GUILT_BUFF);
        let pool = self.total_pool();
        let defer = defer_amount(damage, guilty, pool, max_hp);
        if defer == 0 {
            return;
        }
        // Refund deferred portion immediately (never overhealing max_hp) and spread repayment over 4s
        let restored = cur_hp.saturating_add(defer).min(max_hp);
        if restored > cur_hp {
            let actual = restored - cur_hp;
            sim.entity_set_hp(entity, restored);
            let pulses = (PAY_TICKS / PAY_STEP).max(1);
            let per_step = (actual + pulses - 1) / pulses;
            self.buckets.push(DebtBucket {
                remaining: actual,
                per_step: per_step.max(1),
                attacker: if attacker > 0 { attacker } else { entity },
            });
            self.sync_tally_visual(sim, entity);
            let tick = sim.tick();
            if tick >= self.last_tally_vfx + 30 {
                self.last_tally_vfx = tick;
                sim.play_view_effect("abysspact_reprieve_tally", entity, &InputTargetV1::target(entity), 0, 0, 0);
                sim.play_sfx("abysspact_reprieve_tally", entity, &InputTargetV1::target(entity));
            }
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
            self.absolve(sim, entity);
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.absolve(sim, entity);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.buckets.clear();
        self.tally_shown = false;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos()))
        else {
            return;
        };
        if !alive {
            self.buckets.clear();
            self.tally_shown = false;
            return;
        }
        let tick = sim.tick();

        if !self.native_marked {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
            self.native_marked = true;
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // Check nearby enemy champion deaths within 6.0万 (ally kill/takedown absolves all deferred debt!)
        let mut now_alive = HashSet::new();
        let mut absolved = false;
        let lim = ABSOLVE_RANGE * ABSOLVE_RANGE;
        let n = sim.entity_count();
        for i in 0..n {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_champion() && e.team() != my_team {
                if e.is_alive() {
                    now_alive.insert(e.id());
                } else if self.alive_enemies.contains(&e.id()) && dist_sq(my_pos, e.pos()) <= lim {
                    absolved = true;
                }
            }
        }
        self.alive_enemies = now_alive;
        if absolved {
            self.absolve(sim, entity);
        }

        // Smooth deferred repayment every 0.2s (12 ticks)
        if !self.buckets.is_empty() && tick >= self.last_pay_tick + PAY_STEP {
            self.last_pay_tick = tick;
            let mut due_total: usize = 0;
            let mut credit_attacker: usize = entity;
            for b in &mut self.buckets {
                let take = b.per_step.min(b.remaining);
                b.remaining -= take;
                due_total = due_total.saturating_add(take);
                if b.attacker != entity {
                    credit_attacker = b.attacker;
                }
            }
            self.buckets.retain(|b| b.remaining > 0);

            if due_total > 0 {
                self.in_payback = true;
                sim.deal_damage_typed(
                    credit_attacker,
                    entity,
                    due_total,
                    DamageTypeV1::Fixed,
                    AttackTypeV1::DotIgnoreShield,
                );
                self.in_payback = false;
            }
            self.sync_tally_visual(sim, entity);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_reprieve:sentence", ReprievePassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sentence_defers_half_or_seventy_up_to_sixty_cap() {
        assert_eq!(defer_amount(200, false, 0, 1000), 100);
        assert_eq!(defer_amount(200, true, 0, 1000), 140);
        assert_eq!(defer_amount(500, true, 550, 1000), 50);
        assert_eq!(defer_amount(500, false, 600, 1000), 0);
    }
}
