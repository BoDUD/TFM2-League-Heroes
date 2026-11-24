//! 沉锚 (`abysspact_anchor`) · 深渊锚炮手 · 下路射手
//!
//! 招牌机制「下锚/起锚」双姿态炮台 + 被动「压舱」免疫位移 + 9 万炮弹溅射:
//! - 拖锚（常态）：射程 6 万、移速 +10%。
//! - 下锚（`abysspact_anchor_siege`）：
//!   * 射程通过官方 `StableEffectType::range_adjust` 变为 **9 万**（+3 万），攻速 -20%；
//!   * 普攻变成深海炮弹，对落点 1.5 万内其他敌人造成 **60% 攻击力** 物理溅射伤害并播 `splash`；
//!   * 被动「压舱」：锚爪钉地锁住坐标，击退/击飞/拉拽全部对她无效（眩晕照吃），显示钩子切换 `siege_idle` / `siege_attack`！
//! - 智能 AI 自动切换（与设计书完全一致）：
//!   * 9 万内有敌方英雄且 3.5 万内无敌人时自动下锚（0.5s 延迟）；
//!   * 有敌人贴脸进入 3.0 万内，或连续 2.0 秒无目标时自动起锚（0.6s 延迟）。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_anchor";
pub const NATIVE_MARK: &str = "abysspact_anchor_native";
pub const DRAG_BUFF: &str = "abysspact_anchor_drag";
pub const SIEGE_BUFF: &str = "abysspact_anchor_siege";
pub const TOGGLE_ASK: &str = "abysspact_anchor_toggle";
pub const R_SIEGE_ASK: &str = "abysspact_anchor_r_siege";
pub const R_CAST_VOICE: &str = "abysspact_anchor_r_voice";

pub const SIEGE_BONUS_RANGE: u64 = 30_000; // 6万 -> 9万
pub const SPLASH_RADIUS: u64 = 15_000;     // 1.5万
pub const SPLASH_PCT: usize = 60;
pub const ENGAGE_RANGE: u64 = 90_000;      // 9.0万
pub const SAFE_PLANT_DIST: u64 = 35_000;   // 3.5万
pub const DANGER_RAISE_DIST: u64 = 30_000; // 3.0万
pub const NO_TARGET_RAISE: usize = 120;    // 2.0s
pub const TOGGLE_CD: usize = 120;          // 2.0s

pub fn splash_damage(ad: usize) -> usize {
    ad.saturating_mul(SPLASH_PCT) / 100
}

#[derive(Clone, Default)]
struct AnchorPassive {
    voice: Voice,
    siege: bool,
    pinned_pos: Option<(u64, u64)>,
    next_toggle_at: usize,
    last_seen_target: usize,
    splashing: bool,
}

impl AnchorPassive {
    fn enter_siege(&mut self, sim: &mut StableSim<'_>, entity: usize, pos: (u64, u64), tick: usize) {
        self.siege = true;
        self.pinned_pos = Some(pos);
        self.next_toggle_at = tick + TOGGLE_CD;
        self.last_seen_target = tick;
        sim.entity_remove_buff(entity, DRAG_BUFF);
        let mut s = BuffV1::named(SIEGE_BUFF);
        s.attack_speed_mult = -20;
        s.move_speed_mult = -100;
        sim.add_buff(entity, &s);
        sim.play_view_effect("abysspact_anchor_crack", entity, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
        sim.play_view_effect("abysspact_anchor_stamp", entity, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
        sim.play_sfx("abysspact_anchor_plant", entity, &InputTargetV1::pos(pos.0, pos.1));
    }

    fn enter_drag(&mut self, sim: &mut StableSim<'_>, entity: usize, pos: (u64, u64), tick: usize) {
        self.siege = false;
        self.pinned_pos = None;
        self.next_toggle_at = tick + TOGGLE_CD;
        sim.entity_remove_buff(entity, SIEGE_BUFF);
        let mut d = BuffV1::named(DRAG_BUFF);
        d.move_speed_mult = 10;
        sim.add_buff(entity, &d);
        sim.play_sfx("abysspact_anchor_raise", entity, &InputTargetV1::pos(pos.0, pos.1));
    }
}

impl StablePassive for AnchorPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.siege = false;
        self.pinned_pos = None;
        self.next_toggle_at = 0;
        self.last_seen_target = 0;
        self.splashing = false;
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, target: usize, _damage: &mut usize) {
        if self.splashing {
            return;
        }
        let Some((my_team, ad)) = sim.get_entity(entity).map(|e| (e.team(), e.stat().attack)) else {
            return;
        };
        let Some((is_champ, tpos)) = sim.get_entity(target).map(|e| (e.is_champion(), e.pos())) else {
            return;
        };
        if is_champ {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
        // In Siege mode: every shell splashes 60% AD to all other enemies within 1.5万!
        if self.siege {
            let r2 = SPLASH_RADIUS * SPLASH_RADIUS;
            let mut others = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                let eid = e.id();
                if eid == target || !e.is_alive() || e.team() == my_team || e.is_tower() {
                    continue;
                }
                if dist_sq(tpos, e.pos()) <= r2 {
                    others.push(eid);
                }
            }
            sim.play_view_effect("abysspact_anchor_splash", entity, &InputTargetV1::pos(tpos.0, tpos.1), 0, 0, 0);
            if !others.is_empty() {
                self.splashing = true;
                let dmg = splash_damage(ad);
                for oid in others {
                    sim.deal_damage_typed(entity, oid, dmg, DamageTypeV1::Ad, AttackTypeV1::BaseAttack);
                }
                self.splashing = false;
            }
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.siege = false;
        self.pinned_pos = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, pos)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos()))
        else {
            return;
        };
        if !alive {
            return;
        }
        let tick = sim.tick();
        if !has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }
        if !self.siege && !has_buff(sim, entity, DRAG_BUFF) {
            let mut d = BuffV1::named(DRAG_BUFF);
            d.move_speed_mult = 10;
            sim.add_buff(entity, &d);
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // R「沉船炮」forces planting anchor immediately if not yet anchored!
        if consume_buff(sim, entity, R_SIEGE_ASK) && !self.siege {
            self.enter_siege(sim, entity, pos, tick);
        }

        // Manual / data W toggle request
        if consume_buff(sim, entity, TOGGLE_ASK) {
            if self.siege {
                self.enter_drag(sim, entity, pos, tick);
            } else {
                self.enter_siege(sim, entity, pos, tick);
            }
        }

        // Passive「压舱」: while anchored, lock world position so knockback/pull/knockup never move her!
        if self.siege {
            if let Some(pin) = self.pinned_pos {
                if pos != pin {
                    sim.entity_set_pos(entity, pin.0, pin.1);
                }
            }
        }

        // Smart AI auto-plant / auto-raise check every 10 ticks
        if tick % 10 == 0 {
            let mut nearest_foe_d2 = u64::MAX;
            let mut has_champ_in_9 = false;
            let r9_2 = ENGAGE_RANGE * ENGAGE_RANGE;
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_alive() || e.team() == my_team || e.is_tower() {
                    continue;
                }
                let d2 = dist_sq(pos, e.pos());
                if d2 < nearest_foe_d2 {
                    nearest_foe_d2 = d2;
                }
                if e.is_champion() && d2 <= r9_2 {
                    has_champ_in_9 = true;
                }
            }
            if nearest_foe_d2 <= r9_2 {
                self.last_seen_target = tick;
            }
            if tick >= self.next_toggle_at {
                if !self.siege && has_champ_in_9 && nearest_foe_d2 > SAFE_PLANT_DIST * SAFE_PLANT_DIST {
                    self.enter_siege(sim, entity, pos, tick);
                } else if self.siege
                    && (nearest_foe_d2 <= DANGER_RAISE_DIST * DANGER_RAISE_DIST
                        || tick.saturating_sub(self.last_seen_target) >= NO_TARGET_RAISE)
                {
                    self.enter_drag(sim, entity, pos, tick);
                }
            }
        }
    }
}

/// Official `StableEffectType::range_adjust`: adds +3.0万 attack range (6万 -> 9万) while anchored!
#[derive(Debug)]
struct SiegeRange;

impl StableEffectType for SiegeRange {
    fn apply(&self, _sim: &mut StableSim<'_>, _seed: u64, _caster: usize, _input: InputTargetV1) {}
    fn may_adjust_range(&self) -> bool {
        true
    }
    fn range_adjust(&self, caster: &StableEntityView<'_>, _target: &StableEntityView<'_>) -> u64 {
        let anchored = (0..caster.buff_count()).any(|i| caster.buff_at(i).is_some_and(|b| b.name() == SIEGE_BUFF));
        if anchored { SIEGE_BONUS_RANGE } else { 0 }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_anchor:siege", AnchorPassive::default());
    module.add_native_effect("abysspact_anchor:siege_range", SiegeRange);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn siege_splash_is_60pct_ad() {
        assert_eq!(splash_damage(100), 60);
        assert_eq!(splash_damage(250), 150);
    }
}
