//! 赊命 (`abysspact_debtor`) · 赊命剑客 · 打野战士
//!
//! 招牌机制「欠条 + 换命」:
//! - Q「讨债」/ W「利息」命中敌方英雄留 6 秒（360 ticks）「欠条」(`abysspact_debtor_debt_note`)；
//!   Q 命中 30% 血以下敌方英雄额外追加 +50% 物理伤害。
//! - 胸口玻璃坠命火随当前血量档位切换 (`flame_100` / `flame_50` / `flame_25`)。
//! - R「换命」：选中带欠条的敌方英雄（优先选血量比例更高者），立刻**对调双方血量比例**，并在两人头顶挂 6 秒倒计时环：
//!   * 6 秒内对方死亡：赊命永久保留这条命，播放 `absorb` 命火入坠特效；
//!   * 6 秒到期双方仍存活：按 6 秒后**当时的血量比例**再对调一次（把对方打残却没打死，换回时自己反而更残！）。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_debtor";
pub const NATIVE_MARK: &str = "abysspact_debtor_native";
pub const DEBT_NOTE: &str = "abysspact_debtor_debt_note";
pub const Q_HIT_ASK: &str = "abysspact_debtor_q_hit";
pub const R_ASK: &str = "abysspact_debtor_r_ask";
pub const TIMER_RING: &str = "abysspact_debtor_timer_ring";
pub const FLAME_100: &str = "abysspact_debtor_flame_100";
pub const FLAME_50: &str = "abysspact_debtor_flame_50";
pub const FLAME_25: &str = "abysspact_debtor_flame_25";
pub const R_CAST_VOICE: &str = "abysspact_debtor_r_voice";

pub const SWAP_TICKS: usize = 360;   // 6.0s
pub const R_RANGE: u64 = 65_000;     // 6.5万
pub const Q_EXEC_PCT: usize = 30;
pub const Q_BONUS_BASE: usize = 51;   // +50% of base 102
pub const Q_BONUS_AD_PCT: usize = 61; // +50% of 122% AD

pub fn swapped_hp(my_hp: usize, my_max: usize, foe_hp: usize, foe_max: usize) -> (usize, usize) {
    if my_max == 0 || foe_max == 0 {
        return (my_hp, foe_hp);
    }
    let new_my = ((my_max as u128 * foe_hp as u128 + (foe_max as u128 / 2)) / foe_max as u128)
        .clamp(1, my_max as u128) as usize;
    let new_foe = ((foe_max as u128 * my_hp as u128 + (my_max as u128 / 2)) / my_max as u128)
        .clamp(1, foe_max as u128) as usize;
    (new_my, new_foe)
}

pub fn flame_tier(cur_hp: usize, max_hp: usize) -> &'static str {
    if max_hp == 0 || cur_hp.saturating_mul(100) <= max_hp.saturating_mul(30) {
        FLAME_25
    } else if cur_hp.saturating_mul(100) <= max_hp.saturating_mul(65) {
        FLAME_50
    } else {
        FLAME_100
    }
}

#[derive(Clone, Copy)]
struct ActiveSwap {
    target: usize,
    end_tick: usize,
}

#[derive(Clone, Default)]
struct DebtorPassive {
    voice: Voice,
    native_marked: bool,
    flame_shown: Option<&'static str>,
    active_swap: Option<ActiveSwap>,
}

impl DebtorPassive {
    fn sync_flame(&mut self, sim: &mut StableSim<'_>, entity: usize, cur: usize, max: usize) {
        let want = flame_tier(cur, max);
        if self.flame_shown == Some(want) {
            return;
        }
        for f in [FLAME_100, FLAME_50, FLAME_25] {
            sim.entity_remove_buff(entity, f);
        }
        sim.add_buff(entity, &BuffV1::named(want));
        self.flame_shown = Some(want);
    }

    fn execute_swap(&mut self, sim: &mut StableSim<'_>, entity: usize, target: usize, is_return: bool) {
        let Some((my_alive, my_hp, my_max)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.hp().0, e.hp().1))
        else {
            return;
        };
        let Some((foe_alive, foe_hp, foe_max)) = sim
            .get_entity(target)
            .map(|e| (e.is_alive(), e.hp().0, e.hp().1))
        else {
            return;
        };
        if !my_alive || !foe_alive || my_max == 0 || foe_max == 0 {
            return;
        }
        let (new_my, new_foe) = swapped_hp(my_hp, my_max, foe_hp, foe_max);
        sim.entity_set_hp(entity, new_my);
        sim.entity_set_hp(target, new_foe);

        if is_return {
            sim.play_view_effect("abysspact_debtor_swap_return", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_view_effect("abysspact_debtor_swap_return", entity, &InputTargetV1::target(target), 0, 0, 0);
            sim.play_sfx("abysspact_debtor_swap_return", entity, &InputTargetV1::target(entity));
        } else {
            sim.play_view_effect("abysspact_debtor_swap", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_view_effect("abysspact_debtor_swap", entity, &InputTargetV1::target(target), 0, 0, 0);
            sim.play_view_effect("abysspact_debtor_life_flame", entity, &InputTargetV1::target(target), 0, 0, 0);
            sim.play_sfx("abysspact_debtor_swap", entity, &InputTargetV1::target(entity));
            sim.add_buff(entity, &BuffV1::timed(TIMER_RING, SWAP_TICKS));
            sim.add_buff(target, &BuffV1::timed(TIMER_RING, SWAP_TICKS));
        }
    }
}

impl StablePassive for DebtorPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.native_marked = false;
        self.flame_shown = None;
        self.active_swap = None;
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
        if let Some(sw) = self.active_swap {
            if sw.target == victim {
                self.active_swap = None;
                sim.entity_remove_buff(entity, TIMER_RING);
                sim.play_view_effect("abysspact_debtor_absorb", entity, &InputTargetV1::target(entity), 0, 0, 0);
                sim.play_sfx("abysspact_debtor_absorb", entity, &InputTargetV1::target(entity));
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.active_swap = None;
        self.flame_shown = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, cur_hp, max_hp, my_atk)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.hp().0, e.hp().1, e.stat().attack))
        else {
            return;
        };
        if !alive {
            self.active_swap = None;
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
        self.sync_flame(sim, entity, cur_hp, max_hp);

        // 1. Q「讨债」execute bonus (+50% on targets <= 30% HP) & R「换命」trigger scan
        let mut q_hits = Vec::new();
        let mut r_direct = None;
        let mut best_noted: Option<(usize, u64)> = None; // (id, hp_pct_milli)
        let lim = R_RANGE * R_RANGE;
        let n = sim.entity_count();
        for i in 0..n {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || !e.is_alive() || e.team() == my_team {
                continue;
            }
            let eid = e.id();
            if has_buff(sim, eid, Q_HIT_ASK) {
                q_hits.push((eid, e.hp().0, e.hp().1));
            }
            if has_buff(sim, eid, R_ASK) {
                r_direct = Some(eid);
            }
            if has_buff(sim, eid, DEBT_NOTE) && dist_sq(my_pos, e.pos()) <= lim {
                let (eh, em) = e.hp();
                let pct = if em > 0 { (eh as u64) * 1000 / (em as u64) } else { 0 };
                if best_noted.is_none_or(|(_, bp)| pct > bp) {
                    best_noted = Some((eid, pct));
                }
            }
        }
        for (eid, eh, em) in q_hits {
            sim.entity_remove_buff(eid, Q_HIT_ASK);
            if em > 0 && eh.saturating_mul(100) <= em.saturating_mul(Q_EXEC_PCT) {
                let bonus = Q_BONUS_BASE + my_atk.saturating_mul(Q_BONUS_AD_PCT) / 100;
                sim.deal_damage_typed(entity, eid, bonus, DamageTypeV1::Ad, AttackTypeV1::Skill);
            }
        }

        if let Some(direct_id) = r_direct {
            sim.entity_remove_buff(direct_id, R_ASK);
            // Pick highest-HP% IOU-marked enemy if available and better, else the direct target
            let my_pct = if max_hp > 0 { (cur_hp as u64) * 1000 / (max_hp as u64) } else { 1000 };
            let chosen = match best_noted {
                Some((nid, npct)) if npct > my_pct => nid,
                _ => direct_id,
            };
            // Always stamp debt_note on chosen so the narrative matches even if R fires first
            sim.add_buff(chosen, &BuffV1::timed(DEBT_NOTE, SWAP_TICKS));
            self.execute_swap(sim, entity, chosen, false);
            self.active_swap = Some(ActiveSwap { target: chosen, end_tick: tick + SWAP_TICKS });
        }

        // 2. Active 6-second borrowed-life settlement
        if let Some(sw) = self.active_swap {
            let target_alive = sim.get_entity(sw.target).is_some_and(|e| e.is_alive());
            if !target_alive {
                // Enemy died within 6s: Debtor permanently keeps the borrowed life!
                self.active_swap = None;
                sim.entity_remove_buff(entity, TIMER_RING);
                sim.play_view_effect("abysspact_debtor_absorb", entity, &InputTargetV1::target(entity), 0, 0, 0);
                sim.play_sfx("abysspact_debtor_absorb", entity, &InputTargetV1::target(entity));
            } else if tick >= sw.end_tick {
                // 6s expired and target lived: swap current ratios back!
                self.active_swap = None;
                sim.entity_remove_buff(entity, TIMER_RING);
                sim.entity_remove_buff(sw.target, TIMER_RING);
                self.execute_swap(sim, entity, sw.target, true);
            }
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_debtor:ledger", DebtorPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ratio_swap_preserves_percentages_and_nonzero_floor() {
        // 20% of 1000 vs 90% of 2000 -> 900 vs 400
        assert_eq!(swapped_hp(200, 1000, 1800, 2000), (900, 400));
        // Even 1 HP floors cleanly at >= 1
        assert_eq!(swapped_hp(1, 1000, 1000, 1000).1, 1);
    }
}
