//! 断誓 (`abysspact_oathbreaker`) · 诅咒骑士 · 上路战士
//!
//! 招牌机制「血誓」:
//! - 每放一个技能（数据层挂 `abysspact_oathbreaker_burn_ask`），烧掉 6% 当前生命（最低保留 1 血，永不自杀）。
//! - 每损失 10% 最大生命，攻击力 +4%、攻速 +5%（最多 9 档 = +36% / +45%），并按血量切换三档黑紫火光环
//!   `oath_low`（>65%）、`oath_mid`（35%–65%）、`oath_high`（<35%）。
//! - 大招「断誓」6 秒不死期间：若拿到击杀或助攻，结束时回复 25% 最大生命；若未拿到，再烧掉 15% 当前生命。
//!
//! 大招什么时候开（蛮王附加包的做法）：数据读不到生命，AI 一看到敌方英雄就按 R，满血开掉的 6 秒不死白白浪费。
//! 现在 R 只是「待命」：数据给他挂 `r_armed`，本被动每 tick 看：生命掉到 `ERUPT_HP_PCT`% 以下、`ERUPT_NEAR` 内有
//! 敌方英雄、自己没被控住（塔、小兵打残的不算，被眩晕时也放不出），才真正断誓——烧 6% 当前生命（放技能的血誓，
//! 待命那一下不烧）、6 秒不死、40% 吸血、播大招动作（插剑仰头，用动画控制播）、脚下黑火和一圈黑火伤害；待命时间过了
//! 还没用上，退还冷却，只剩 `REARM_LEFT` tick，下一架再待命。塞拉斯偷到的 R 身上没有 `p_self`，数据照旧当场断誓。

use mod_api_stable::*;
// 写死的技能距离在大地图版跟着乘 1.3
use game_places::skill_scale::sk;

use crate::voice::{Cue, Voice};
use crate::{buffs_present, can_cast, consume_buff, dist_sq, foe_champions, has_buff};

pub const HERO: &str = "abysspact_oathbreaker";
pub const BURN_ASK: &str = "abysspact_oathbreaker_burn_ask";
pub const R_BUFF: &str = "abysspact_oathbreaker_r_undying";
pub const R_ARMED: &str = "abysspact_oathbreaker_r_armed";
/// 本被动挂在他身上的记号：数据的 R 看见它就只待命（塞拉斯没有它，偷到的 R 当场断誓）。
pub const P_SELF: &str = "abysspact_oathbreaker_p_self";
pub const BLOOD_BUFF: &str = "abysspact_oathbreaker_blood";
pub const AURA_LOW: &str = "abysspact_oathbreaker_oath_low";
pub const AURA_MID: &str = "abysspact_oathbreaker_oath_mid";
pub const AURA_HIGH: &str = "abysspact_oathbreaker_oath_high";

const CHECK_EVERY: usize = 6;
const SKILL_BURN_PCT: usize = 6;
const ULT_PENALTY_PCT: usize = 15;
const ULT_REWARD_PCT: usize = 25;

/// 待命里生命掉到这个百分比以下就断誓。
pub const ERUPT_HP_PCT: usize = 40;
/// 断誓还要这么近有敌方英雄（蛮王附加包的 `near`）。
pub const ERUPT_NEAR: u64 = 50_000;
/// 断誓：不死的 tick、吸血 %、攻速 %（同数据版）。
pub const R_TICKS: usize = 360;
pub const R_VAMP: i32 = 40;
pub const R_AS: i32 = 15;
/// 脚下一圈黑火：半径、48 + 42% 攻击力（同数据版的 r_burst）。
pub const R_BURST_R: u64 = 28_000;
pub const R_BURST_DMG: usize = 48;
pub const R_BURST_AD: usize = 42;
/// 大招动作（插剑仰头）的 tick 数：和他图里 `ult` 动画一样长。
pub const R_ANIM_TICKS: u64 = 42;
/// 待命没用上：冷却退到只剩这么多 tick。
pub const REARM_LEFT: usize = 300;

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

/// 待命里该不该断誓：生命不高于 `ERUPT_HP_PCT`%。
pub fn should_erupt(cur: usize, max: usize) -> bool {
    max > 0 && cur.saturating_mul(100) <= max.saturating_mul(ERUPT_HP_PCT)
}

/// 待命里这一刻断不断誓：生命够低、身边有敌方英雄、没被控住。
pub fn erupt_due(cur: usize, max: usize, foe_near: bool, free: bool) -> bool {
    should_erupt(cur, max) && foe_near && free
}

/// 待命过期没用上：要从剩余冷却里退掉多少 tick（剩 `REARM_LEFT`）。
pub fn rearm_refund(remaining: usize) -> usize {
    remaining.saturating_sub(REARM_LEFT)
}

#[derive(Clone, Default)]
struct OathbreakerPassive {
    voice: Voice,
    last_tier: usize,
    last_aura: u8,
    ult_active: bool,
    ult_takedown: bool,
    /// 上一 tick 身上有没有待命。
    armed: bool,
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

    /// 断誓：去掉待命，烧 6% 当前生命，6 秒不死 + 吸血 + 攻速，插剑仰头的大招动作，脚下黑火和一圈黑火伤害。
    fn erupt(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        sim.entity_remove_buff(entity, R_ARMED);
        self.armed = false;
        if let Some(cur) = sim.get_entity(entity).map(|e| e.hp().0) {
            let next = hp_after_burn(cur, SKILL_BURN_PCT);
            if next < cur {
                sim.entity_set_hp(entity, next);
            }
        }
        let mut r = BuffV1::timed(R_BUFF, R_TICKS);
        r.undying = true;
        r.vamp = R_VAMP;
        r.attack_speed_mult = R_AS;
        sim.entity_remove_buff(entity, R_BUFF);
        sim.add_buff(entity, &r);
        let mut anim = CcV1::of_kind(CcKindV1::Animation, R_ANIM_TICKS);
        anim.set_name("ult");
        sim.apply_cc(entity, &anim);
        let me = InputTargetV1::target(entity);
        sim.play_sfx("abysspact_oathbreaker_r_plant", entity, &me);
        sim.play_sfx("abysspact_oathbreaker_r_erupt", entity, &me);
        sim.play_view_effect("abysspact_oathbreaker_footfire", entity, &me, 0, 0, 0);
        let Some((team, pos, ad)) = sim.get_entity(entity).map(|e| (e.team(), e.pos(), e.stat().attack.max(0) as usize))
        else {
            return;
        };
        let dmg = R_BURST_DMG + ad * R_BURST_AD / 100;
        let r2 = sk(R_BURST_R) * sk(R_BURST_R);
        // 选不中的（放逐、隐身、无敌）、塔和水晶不挨这一圈
        let foes: Vec<usize> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| {
                u.is_alive()
                    && u.team() != team
                    && u.is_targetable()
                    && !u.is_tower()
                    && u.kind() != Some(EntityKindV1::Nexus)
                    && dist_sq(u.pos(), pos) <= r2
            })
            .map(|u| u.id())
            .collect();
        for id in foes {
            sim.deal_damage_typed(entity, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
            sim.play_view_effect("abysspact_oathbreaker_impact", entity, &InputTargetV1::target(id), 0, 0, 0);
        }
    }

    /// 待命里看一眼：生命够低、身边有敌方英雄、没被控住就断誓。
    fn check_erupt(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if !self.armed {
            return;
        }
        let Some((alive, cur, max, team, pos)) =
            sim.get_entity(entity).map(|e| (e.is_alive(), e.hp().0, e.hp().1, e.team(), e.pos()))
        else {
            return;
        };
        if !alive || !should_erupt(cur, max) {
            return;
        }
        let near2 = sk(ERUPT_NEAR) * sk(ERUPT_NEAR);
        let foe_near = foe_champions(sim, team).iter().any(|(_, p)| dist_sq(*p, pos) <= near2);
        if erupt_due(cur, max, foe_near, can_cast(sim, entity)) {
            self.erupt(sim, entity);
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
        self.armed = false;
        sim.add_buff(entity, &BuffV1::named(P_SELF));
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

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, _attacker: usize, _damage: usize) {
        // 挨打的这一下当场再看一次（不用等下一 tick）
        self.check_erupt(sim, entity);
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
        self.armed = false;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        self.voice.observe(entity);
        let Some((alive, cur, max)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.hp().0, e.hp().1)) else {
            return;
        };
        if !alive {
            self.ult_active = false;
            return;
        }
        let [p_self, armed] = buffs_present(sim, entity, [P_SELF, R_ARMED]);
        // 阵亡清掉了全部 buff：新的一条命补回记号
        if !p_self {
            sim.add_buff(entity, &BuffV1::named(P_SELF));
        }

        // 1. Skill 6% current-HP self-burn (never lethal)
        let mut cur = cur;
        if consume_buff(sim, entity, BURN_ASK) {
            let next_hp = hp_after_burn(cur, SKILL_BURN_PCT);
            if next_hp < cur {
                sim.entity_set_hp(entity, next_hp);
                cur = next_hp;
            }
        }

        // 2. 待命：生命够低、身边有敌方英雄、没被控住就断誓；待命时间过了没用上，退还冷却
        if armed {
            self.armed = true;
            self.check_erupt(sim, entity);
        } else if self.armed {
            self.armed = false;
            if !has_buff(sim, entity, R_BUFF) {
                let left = sim.get_entity(entity).and_then(|e| e.cooldown(SkillSlotV1::Ult)).map_or(0, |c| c.remaining);
                sim.entity_reduce_cooldown(entity, SkillSlotV1::Ult, rearm_refund(left));
            }
        }

        // 3. Track 6s Undying ult start & end judgment
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

        // 4. Periodic missing-HP AD/AS scaling & 3-tier aura update
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

    #[test]
    fn the_armed_ult_waits_for_low_health() {
        assert!(!should_erupt(1000, 1000));
        assert!(!should_erupt(401, 1000));
        assert!(should_erupt(400, 1000));
        assert!(should_erupt(1, 1000));
        assert!(!should_erupt(0, 0));
    }

    #[test]
    fn the_eruption_needs_a_champion_near_and_free_hands() {
        assert!(erupt_due(300, 1000, true, true));
        // 塔、小兵打残的：身边没有敌方英雄
        assert!(!erupt_due(300, 1000, false, true));
        // 被眩晕着放不出
        assert!(!erupt_due(300, 1000, true, false));
        assert!(!erupt_due(500, 1000, true, true));
    }

    #[test]
    fn an_unused_window_gives_most_of_the_cooldown_back() {
        // 70 秒的冷却待命了 10 秒没用上：剩 3600，退到 300
        assert_eq!(rearm_refund(3600), 3300);
        assert_eq!(rearm_refund(200), 0);
    }

    #[test]
    fn the_eruption_animation_is_the_ult_sheet_length() {
        let anim = include_str!("../../../abysspact/champions/abysspact_oathbreaker#anim.fanim");
        assert_eq!(crate::fanim_ticks(anim, "ult"), Some(R_ANIM_TICKS as usize));
    }

    #[test]
    fn the_kit_arms_the_ult_and_keeps_the_stolen_copy_whole() {
        let kit = include_str!("../../../abysspact/champion/abysspact_oathbreaker.data_champion");
        assert!(kit.contains(R_ARMED) && kit.contains(P_SELF), "the R arms only behind p_self");
        // 待命不烧血：R 里没有 burn_ask（烧血在断誓那一刻）
        let r = &kit[kit.find("\"ult\"").expect("R")..];
        assert!(!r.contains(BURN_ASK), "arming the R must not burn health");
        assert!(kit.contains("\"undying\": true"), "Sylas's copy (no p_self) still gets the undying");
    }
}
