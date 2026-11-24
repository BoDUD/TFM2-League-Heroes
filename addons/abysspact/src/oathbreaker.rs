//! 断誓 (`abysspact_oathbreaker`) · 诅咒骑士 · 上路战士
//!
//! 招牌机制「血誓」:
//! - 每放一个技能（数据层挂 `abysspact_oathbreaker_burn_ask`），烧掉 6% 当前生命（最低保留 1 血，永不自杀）。
//! - 每损失 10% 最大生命，攻击力 +4%、攻速 +5%（最多 9 档 = +36% / +45%），并按血量切换三档黑紫火光环
//!   `oath_low`（>65%）、`oath_mid`（35%–65%）、`oath_high`（<35%）。
//! - 大招「断誓」6 秒不死期间：若拿到击杀或助攻，结束时回复 25% 最大生命；若未拿到，再烧掉 15% 当前生命。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, has_buff};

pub const HERO: &str = "abysspact_oathbreaker";
pub const BURN_ASK: &str = "abysspact_oathbreaker_burn_ask";
pub const R_BUFF: &str = "abysspact_oathbreaker_r_undying";
pub const BLOOD_BUFF: &str = "abysspact_oathbreaker_blood";
pub const AURA_LOW: &str = "abysspact_oathbreaker_oath_low";
pub const AURA_MID: &str = "abysspact_oathbreaker_oath_mid";
pub const AURA_HIGH: &str = "abysspact_oathbreaker_oath_high";

const CHECK_EVERY: usize = 6;
const SKILL_BURN_PCT: usize = 6;
const ULT_PENALTY_PCT: usize = 15;
const ULT_REWARD_PCT: usize = 25;

/// Missing-HP tier in 0..=9 (one step per full 10% missing HP, capped at 9 -> +36% AD / +45% AS).
pub fn blood_tier(cur: usize, max: usize) -> usize {
    if max == 0 || cur >= max {
        return 0;
    }
    let missing_pct = (max - cur).saturating_mul(100) / max;
    (missing_pct / 10).min(9)
}

/// Visual aura tier: 0 = none (full HP), 1 = low (>65%), 2 = mid (35..=65%), 3 = high (<35%).
pub fn aura_tier(cur: usize, max: usize) -> u8 {
    if max == 0 {
        return 0;
    }
    let pct = cur.saturating_mul(100) / max;
    if pct >= 95 {
        0
    } else if pct > 65 {
        1
    } else if pct >= 35 {
        2
    } else {
        3
    }
}

/// Apply `pct`% current-HP burn, always keeping at least 1 HP.
pub fn hp_after_burn(cur: usize, pct: usize) -> usize {
    if cur <= 1 {
        return cur;
    }
    let cost = (cur.saturating_mul(pct) / 100).max(1);
    cur.saturating_sub(cost).max(1)
}

#[derive(Clone, Default)]
struct OathbreakerPassive {
    voice: Voice,
    last_tier: usize,
    last_aura: u8,
    ult_active: bool,
    ult_takedown: bool,
}

impl OathbreakerPassive {
    fn sync_blood(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        let Some(e) = sim.get_entity(entity) else { return };
        if !e.is_alive() {
            return;
        }
        let (cur, max) = e.hp();
        let tier = blood_tier(cur, max);
        if tier != self.last_tier {
            self.last_tier = tier;
            sim.entity_remove_buff(entity, BLOOD_BUFF);
            if tier > 0 {
                let mut b = BuffV1::named(BLOOD_BUFF);
                b.attack_mult = (tier * 4) as i32;
                b.attack_speed_mult = (tier * 5) as i32;
                sim.add_buff(entity, &b);
            }
        }
        let aura = aura_tier(cur, max);
        if aura != self.last_aura {
            self.last_aura = aura;
            sim.entity_remove_buff(entity, AURA_LOW);
            sim.entity_remove_buff(entity, AURA_MID);
            sim.entity_remove_buff(entity, AURA_HIGH);
            let want = match aura {
                1 => Some(AURA_LOW),
                2 => Some(AURA_MID),
                3 => Some(AURA_HIGH),
                _ => None,
            };
            if let Some(name) = want {
                sim.add_buff(entity, &BuffV1::named(name));
            }
        }
    }
}

impl StablePassive for OathbreakerPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.last_tier = 0;
        self.last_aura = 0;
        self.ult_active = false;
        self.ult_takedown = false;
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
            if self.ult_active {
                self.ult_takedown = true;
            }
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_assist(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        if self.ult_active {
            self.ult_takedown = true;
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.ult_active = false;
        self.ult_takedown = false;
        self.last_tier = 0;
        self.last_aura = 0;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, cur, max)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.hp().0, e.hp().1)) else {
            return;
        };
        if !alive {
            self.ult_active = false;
            return;
        }

        // 1. Skill 6% current-HP self-burn (never lethal)
        if consume_buff(sim, entity, BURN_ASK) {
            let next_hp = hp_after_burn(cur, SKILL_BURN_PCT);
            if next_hp < cur {
                sim.entity_set_hp(entity, next_hp);
            }
        }

        // 2. Track 6s Undying ult start & end judgment
        let in_r = has_buff(sim, entity, R_BUFF);
        if in_r && !self.ult_active {
            self.ult_active = true;
            self.ult_takedown = false;
            self.voice.play(sim, HERO, entity, Cue::Ult);
        } else if !in_r && self.ult_active {
            self.ult_active = false;
            let got = self.ult_takedown;
            self.ult_takedown = false;
            if got {
                let heal_amt = (max.saturating_mul(ULT_REWARD_PCT) / 100).max(1);
                sim.heal(entity, entity, heal_amt);
                sim.play_sfx("abysspact_oathbreaker_oath_pulse", entity, &InputTargetV1::target(entity));
            } else {
                let (now_hp, _) = sim.get_entity(entity).map(|e| e.hp()).unwrap_or((cur, max));
                let next_hp = hp_after_burn(now_hp, ULT_PENALTY_PCT);
                if next_hp < now_hp {
                    sim.entity_set_hp(entity, next_hp);
                }
            }
        }

        // 3. Periodic missing-HP AD/AS scaling & 3-tier aura update
        if sim.tick() % CHECK_EVERY == 0 {
            self.sync_blood(sim, entity);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_oathbreaker:blood", OathbreakerPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn blood_tier_scales_per_10pct_missing_up_to_9() {
        assert_eq!(blood_tier(1000, 1000), 0);
        assert_eq!(blood_tier(910, 1000), 0);
        assert_eq!(blood_tier(900, 1000), 1);
        assert_eq!(blood_tier(500, 1000), 5);
        assert_eq!(blood_tier(100, 1000), 9);
        assert_eq!(blood_tier(1, 1000), 9);
    }

    #[test]
    fn aura_tier_matches_three_bands() {
        assert_eq!(aura_tier(1000, 1000), 0);
        assert_eq!(aura_tier(800, 1000), 1);
        assert_eq!(aura_tier(500, 1000), 2);
        assert_eq!(aura_tier(200, 1000), 3);
    }

    #[test]
    fn skill_burn_never_kills_oathbreaker() {
        assert_eq!(hp_after_burn(1000, 6), 940);
        assert_eq!(hp_after_burn(5, 6), 4);
        assert_eq!(hp_after_burn(1, 6), 1);
    }
}
