//! 替身 (`abysspact_effigy`) · 咒偶师 · 中路法师
//!
//! 招牌机制「扎针」+ W「同命线」伤害互传 40% & 拉断双晕 + R「拆线」全图拔针:
//! - 被动「扎针」：技能命中敌人插 1 根银针（最多 3 根，持续 5 秒 = 300 ticks），头顶显示 `needles_1/2/3`。
//! - W「同命线」：用红线连起目标与 4.5 万内最近另一名敌方英雄，持续 4 秒（240 ticks）：
//!   * 任意一方掉血时，另一方同步承受 40% 魔法伤害（带递归防护不会死循环）；
//!   * 两人拉开超过 4.5 万红线当场崩断：双双眩晕 1 秒（60 ticks）并各受 `80 + 50% AP` 魔法伤害！
//! - R「拆线」：猛扯 7 万内所有插着针的敌人，每根针造成 `90 + 45% AP` 魔法伤害（3 根 = `270 + 135% AP`）并减速 50% 1.5 秒。

use std::collections::HashMap;
use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_effigy";
pub const NATIVE_MARK: &str = "abysspact_effigy_native";
pub const NEEDLE_ASK: &str = "abysspact_effigy_needle_ask";
pub const LINK_ASK: &str = "abysspact_effigy_link_ask";
pub const UNPICK_ASK: &str = "abysspact_effigy_unpick_ask";
pub const R_CAST_VOICE: &str = "abysspact_effigy_r_voice";
pub const VIS_N1: &str = "abysspact_effigy_needles_1";
pub const VIS_N2: &str = "abysspact_effigy_needles_2";
pub const VIS_N3: &str = "abysspact_effigy_needles_3";
pub const VIS_KNOT: &str = "abysspact_effigy_knot";
pub const R_SLOW: &str = "abysspact_effigy_r_slow";

pub const NEEDLE_TICKS: usize = 300; // 5.0s
pub const LINK_TICKS: usize = 240;   // 4.0s
pub const SNAP_DIST: u64 = 45_000;   // 4.5万
pub const UNPICK_RANGE: u64 = 70_000; // 7.0万
pub const SHARE_PCT: usize = 40;
pub const SNAP_STUN: u64 = 60;       // 1.0s

pub fn snap_damage(ap: usize) -> usize {
    80 + ap.saturating_mul(50) / 100
}

pub fn unpick_damage(needles: u8, ap: usize) -> usize {
    let per = 90 + ap.saturating_mul(45) / 100;
    per.saturating_mul(needles as usize)
}

pub fn shared_damage(lost_hp: usize) -> usize {
    lost_hp.saturating_mul(SHARE_PCT) / 100
}

#[derive(Clone, Copy)]
struct FateLink {
    a: usize,
    b: usize,
    end_tick: usize,
    last_hp_a: usize,
    last_hp_b: usize,
}

#[derive(Clone, Default)]
struct EffigyPassive {
    voice: Voice,
    /// Enemy entity id -> (needle count 1..=3, expire_tick).
    needles: HashMap<usize, (u8, usize)>,
    link: Option<FateLink>,
}

impl EffigyPassive {
    fn sync_needles(sim: &mut StableSim<'_>, target: usize, count: u8, dur: usize) {
        sim.entity_remove_buff(target, VIS_N1);
        sim.entity_remove_buff(target, VIS_N2);
        sim.entity_remove_buff(target, VIS_N3);
        let name = match count {
            1 => Some(VIS_N1),
            2 => Some(VIS_N2),
            3 => Some(VIS_N3),
            _ => None,
        };
        if let Some(n) = name {
            sim.add_buff(target, &BuffV1::timed(n, dur.max(1)));
        }
    }

    fn pin_needle(&mut self, sim: &mut StableSim<'_>, caster: usize, target: usize, tick: usize) {
        let cur = self
            .needles
            .get(&target)
            .filter(|&&(_, exp)| exp > tick)
            .map(|&(n, _)| n)
            .unwrap_or(0);
        let next = cur.saturating_add(1).min(3);
        self.needles.insert(target, (next, tick + NEEDLE_TICKS));
        Self::sync_needles(sim, target, next, NEEDLE_TICKS);
        sim.play_sfx("abysspact_effigy_needle_mark", caster, &InputTargetV1::target(target));
    }

    fn clear_link(&mut self, sim: &mut StableSim<'_>) {
        if let Some(lk) = self.link.take() {
            sim.entity_remove_buff(lk.a, VIS_KNOT);
            sim.entity_remove_buff(lk.b, VIS_KNOT);
        }
    }
}

impl StablePassive for EffigyPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.needles.clear();
        self.link = None;
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
        self.needles.remove(&victim);
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, ap)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.stat().magic_power))
        else {
            return;
        };
        let tick = sim.tick();
        self.needles.retain(|&eid, &mut (_, exp)| {
            exp > tick && sim.get_entity(eid).is_some_and(|e| e.is_alive())
        });
        if !alive {
            self.clear_link(sim);
            return;
        }
        if !has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }

        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 1. Collect needle applications & W「同命线」targets
        let mut needle_hits = Vec::new();
        let mut link_primary = None;
        let n_ent = sim.entity_count();
        for i in 0..n_ent {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() || e.team() == my_team || e.is_tower() {
                continue;
            }
            let eid = e.id();
            if has_buff(sim, eid, NEEDLE_ASK) {
                needle_hits.push(eid);
            }
            if link_primary.is_none() && e.is_champion() && has_buff(sim, eid, LINK_ASK) {
                link_primary = Some((eid, e.pos(), e.hp().0));
            }
        }
        for eid in needle_hits {
            sim.entity_remove_buff(eid, NEEDLE_ASK);
            self.pin_needle(sim, entity, eid, tick);
        }

        // 2. Establish W「同命线」between primary enemy champion and nearest partner within 4.5万
        if let Some((a, apos, ahp)) = link_primary {
            sim.entity_remove_buff(a, LINK_ASK);
            self.pin_needle(sim, entity, a, tick);
            let max_r2 = SNAP_DIST * SNAP_DIST;
            let mut best: Option<(u64, usize, usize)> = None;
            for i in 0..n_ent {
                let Some(e) = sim.entity_at(i) else { continue };
                let eid = e.id();
                if eid == a || !e.is_alive() || !e.is_champion() || e.team() == my_team {
                    continue;
                }
                let d2 = dist_sq(apos, e.pos());
                if d2 <= max_r2 && best.is_none_or(|(bd, _, _)| d2 < bd) {
                    best = Some((d2, eid, e.hp().0));
                }
            }
            if let Some((_, b, bhp)) = best {
                self.clear_link(sim);
                self.pin_needle(sim, entity, b, tick);
                sim.add_buff(a, &BuffV1::timed(VIS_KNOT, LINK_TICKS));
                sim.add_buff(b, &BuffV1::timed(VIS_KNOT, LINK_TICKS));
                sim.play_sfx("abysspact_effigy_thread_knot", entity, &InputTargetV1::target(a));
                self.link = Some(FateLink { a, b, end_tick: tick + LINK_TICKS, last_hp_a: ahp, last_hp_b: bhp });
            }
        }

        // 3. Maintain active W「同命线」: 40% mutual damage sharing + >4.5万 snap double-stun!
        if let Some(mut lk) = self.link {
            let ea = sim.get_entity(lk.a).map(|e| (e.is_alive(), e.pos(), e.hp().0));
            let eb = sim.get_entity(lk.b).map(|e| (e.is_alive(), e.pos(), e.hp().0));
            match (ea, eb) {
                (Some((true, pa, ha)), Some((true, pb, hb))) if tick < lk.end_tick => {
                    if dist_sq(pa, pb) > SNAP_DIST * SNAP_DIST {
                        // Thread snaps! Both enemies stunned 1.0s + burst magic damage!
                        let dmg = snap_damage(ap);
                        for t in [lk.a, lk.b] {
                            sim.deal_damage_typed(entity, t, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                            sim.apply_cc(t, &CcV1::stun(SNAP_STUN));
                            sim.play_view_effect("abysspact_effigy_snap", entity, &InputTargetV1::target(t), 0, 0, 0);
                        }
                        sim.play_sfx("abysspact_effigy_thread_snap", entity, &InputTargetV1::target(lk.a));
                        self.clear_link(sim);
                    } else if tick % 3 == 0 {
                        let lost_a = lk.last_hp_a.saturating_sub(ha);
                        let lost_b = lk.last_hp_b.saturating_sub(hb);
                        let share_to_b = shared_damage(lost_a);
                        let share_to_a = shared_damage(lost_b);
                        if share_to_b >= 4 {
                            sim.deal_damage_typed(entity, lk.b, share_to_b, DamageTypeV1::Ap, AttackTypeV1::Skill);
                        }
                        if share_to_a >= 4 {
                            sim.deal_damage_typed(entity, lk.a, share_to_a, DamageTypeV1::Ap, AttackTypeV1::Skill);
                        }
                        // Read updated HP AFTER our own shared damage so echoes never bounce back!
                        lk.last_hp_a = sim.get_entity(lk.a).map(|e| e.hp().0).unwrap_or(ha);
                        lk.last_hp_b = sim.get_entity(lk.b).map(|e| e.hp().0).unwrap_or(hb);
                        self.link = Some(lk);
                    }
                }
                _ => self.clear_link(sim),
            }
        }

        // 4. R「拆线」: rip all needles within 7万 simultaneously!
        if consume_buff(sim, entity, UNPICK_ASK) {
            let r2 = UNPICK_RANGE * UNPICK_RANGE;
            let targets: Vec<(usize, u8)> = self
                .needles
                .iter()
                .filter_map(|(&eid, &(cnt, exp))| {
                    if exp <= tick || cnt == 0 {
                        return None;
                    }
                    let e = sim.get_entity(eid)?;
                    (e.is_alive() && dist_sq(my_pos, e.pos()) <= r2).then_some((eid, cnt))
                })
                .collect();
            for (eid, cnt) in targets {
                self.needles.remove(&eid);
                Self::sync_needles(sim, eid, 0, 0);
                let dmg = unpick_damage(cnt, ap);
                sim.deal_damage_typed(entity, eid, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                let mut slow = BuffV1::timed(R_SLOW, 90);
                slow.move_speed_mult = -50;
                sim.add_buff(eid, &slow);
                sim.play_view_effect("abysspact_effigy_withdraw", entity, &InputTargetV1::target(eid), 0, 0, 0);
                sim.play_sfx("abysspact_effigy_unpick_return", entity, &InputTargetV1::target(eid));
            }
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_effigy:needles", EffigyPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn snap_unpick_and_shared_damage_match_spec() {
        assert_eq!(snap_damage(100), 130);
        assert_eq!(unpick_damage(1, 100), 135);
        assert_eq!(unpick_damage(3, 100), 405);
        assert_eq!(shared_damage(250), 100);
    }
}
