//! 替身 (`abysspact_effigy`) · 咒偶师 · 中路法师
//!
//! - 被动「扎针」：技能打中的敌人插一根针（最多 3 根，留 5 秒 = 300 tick），头顶显示 `needles_1/2/3`。
//! - W「同命线」：数据打中目标、扎一根针、挂 `link_ask`；本包从目标身边 4.5 万内找最近的另一个敌方英雄，连 4 秒：
//!   * 两人头上各一个线团（`knot`），中间每 tick 画一段红线（`thread`：特效图集里那段红绳当弹道图用，弹道图跟着
//!     飞行方向转，所以绳子总是从一个人指向另一个人）；
//!   * 一个掉血，另一个跟着吃 40%（魔法伤害，算替身打的）。补的这一下引擎下一 tick 才结算，补完马上从记下的血量里
//!     先扣掉预计会掉的那一截（按对方魔抗），下一次就不会把它当成新伤害再弹回去；
//!   * 两人走开超过 4.5 万线就崩：一起眩晕 1 秒，各吃 80 + 50% 法强；
//!   * 身边找不到第二个敌方英雄：这一下只有伤害和一根针，W 的冷却退回一半。
//! - R「拆线」：7 万内插着针的敌人，每根针 90 + 45% 法强，拔针时减速 50% 1.5 秒（3 根就是 270 + 135%）。
//!   数据只对最近被己方打过的敌方英雄按（`EnemyChampionRecentlyAttacked`）；一根针都没拔到时冷却退到只剩 8 秒。

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
/// 红线：弹道图的名字（数据 view_projectiles 里有），和打中时什么都不做的原生效果。
pub const THREAD: &str = "abysspact_effigy_thread";
pub const NOOP: &str = "abysspact_effigy:noop";
/// 拆线时针飞回娃娃手里的弹道图（数据 view_projectiles 的 r_return）和速度。
pub const RETURN: &str = "abysspact_effigy_r_return";
pub const RETURN_SPEED: u64 = 7_800;

pub const NEEDLE_TICKS: usize = 300; // 5.0s
pub const LINK_TICKS: usize = 240; // 4.0s
pub const SNAP_DIST: u64 = 45_000; // 4.5万
pub const UNPICK_RANGE: u64 = 70_000; // 7.0万
pub const SHARE_PCT: usize = 40;
pub const SNAP_STUN: u64 = 60; // 1.0s
/// 一段红线每 tick 飞多远（飞两步：第一步正好落在两人中间，下一 tick 才到头，那时下一段已经接上）。
pub const THREAD_STEP: f64 = 500.0;
/// 红线画在胸口的高度（往屏幕上方挪）。
pub const THREAD_LIFT: f64 = 9_000.0;
/// 没连上第二个人：W 冷却退回这么多 %。
pub const W_REFUND_PCT: usize = 50;
/// 一根针都没拔到：R 的冷却退到只剩这么多 tick。
pub const R_RETRY: usize = 480;

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

/// 魔法伤害打到身上大约掉多少血（魔抗按 100 / (100 + 魔抗) 算）。
pub fn mitigated(amount: usize, mr: usize) -> usize {
    amount.saturating_mul(100) / (100 + mr)
}

/// 一段红线：从两人中间往回一步放出，朝另一个人飞两步。返回 (起点, 终点)；两人重在一起时不画。
pub fn thread_flight(a: (u64, u64), b: (u64, u64)) -> Option<((f64, f64), (f64, f64))> {
    let (ax, ay) = (a.0 as f64, a.1 as f64 - THREAD_LIFT);
    let (bx, by) = (b.0 as f64, b.1 as f64 - THREAD_LIFT);
    let (dx, dy) = (bx - ax, by - ay);
    let d = (dx * dx + dy * dy).sqrt();
    if d < 1_000.0 {
        return None;
    }
    let (ux, uy) = (dx / d, dy / d);
    let mid = ((ax + bx) / 2.0, (ay + by) / 2.0);
    Some((
        (mid.0 - ux * THREAD_STEP, mid.1 - uy * THREAD_STEP),
        (mid.0 + ux * THREAD_STEP, mid.1 + uy * THREAD_STEP),
    ))
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
    /// 敌人的实体编号 -> (身上几根针 1..=3, 针到哪一 tick 掉)。
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

    /// 两人中间画一段红线（活两 tick 的弹道，每 tick 一段接着一段）。
    fn draw_thread(sim: &mut StableSim<'_>, entity: usize, team: usize, a: (u64, u64), b: (u64, u64)) {
        let Some((from, to)) = thread_flight(a, b) else { return };
        let spec = ProjectileSpawnV1 {
            caster_id: entity,
            team,
            x: from.0.round().max(0.0) as u64,
            y: from.1.round().max(0.0) as u64,
            radius: 1_000,
            speed: THREAD_STEP as u64,
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: to.0.round().max(0.0) as u64,
            target_y: to.1.round().max(0.0) as u64,
            penetrate: true,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Position.code(),
            casting_target: CastingTargetV1::None.code(),
        };
        sim.spawn_projectile(THREAD, NOOP, &spec);
    }

    /// 退冷却：`slot` 剩下的冷却减掉 `ticks`。
    fn refund(sim: &mut StableSim<'_>, entity: usize, slot: SkillSlotV1, ticks: usize) {
        if ticks > 0 {
            sim.entity_reduce_cooldown(entity, slot, ticks);
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
        self.clear_link(sim);
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

        // 1. 技能打中挂的扎针请求、W 的同命线请求
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

        // 2. W 打中的人（它的针数据已经扎了）和身边 4.5 万内最近的另一个敌方英雄连起来
        if let Some((a, apos, ahp)) = link_primary {
            sim.entity_remove_buff(a, LINK_ASK);
            let max_r2 = SNAP_DIST * SNAP_DIST;
            let mut best: Option<(u64, usize, usize)> = None;
            for i in 0..n_ent {
                let Some(e) = sim.entity_at(i) else { continue };
                let eid = e.id();
                if eid == a || !e.is_alive() || !e.is_champion() || e.team() == my_team || !e.is_targetable() {
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
            } else {
                // 身边没有第二个人：这次只是一下伤害，冷却退回一半
                let half = sim
                    .get_entity(entity)
                    .and_then(|e| e.cooldown(SkillSlotV1::Skill2))
                    .map_or(0, |c| c.cooltime.saturating_mul(W_REFUND_PCT) / 100);
                Self::refund(sim, entity, SkillSlotV1::Skill2, half);
            }
        }

        // 3. 同命线：40% 互传、画线、走远崩断
        if let Some(mut lk) = self.link {
            let ea = sim.get_entity(lk.a).map(|e| (e.is_alive(), e.pos(), e.hp().0, e.stat().magic_resistance));
            let eb = sim.get_entity(lk.b).map(|e| (e.is_alive(), e.pos(), e.hp().0, e.stat().magic_resistance));
            match (ea, eb) {
                (Some((true, pa, ha, mra)), Some((true, pb, hb, mrb))) if tick < lk.end_tick => {
                    if dist_sq(pa, pb) > SNAP_DIST * SNAP_DIST {
                        // 线崩了：两人一起眩晕，各吃一下
                        let dmg = snap_damage(ap);
                        for t in [lk.a, lk.b] {
                            sim.deal_damage_typed(entity, t, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                            sim.apply_cc(t, &CcV1::stun(SNAP_STUN));
                            sim.play_view_effect("abysspact_effigy_snap", entity, &InputTargetV1::target(t), 0, 0, 0);
                        }
                        sim.play_sfx("abysspact_effigy_thread_snap", entity, &InputTargetV1::target(lk.a));
                        self.clear_link(sim);
                    } else {
                        Self::draw_thread(sim, entity, my_team, pa, pb);
                        if tick % 3 == 0 {
                            let share_to_b = shared_damage(lk.last_hp_a.saturating_sub(ha));
                            let share_to_a = shared_damage(lk.last_hp_b.saturating_sub(hb));
                            let mut expect_a = 0;
                            let mut expect_b = 0;
                            if share_to_b >= 4 {
                                sim.deal_damage_typed(entity, lk.b, share_to_b, DamageTypeV1::Ap, AttackTypeV1::Skill);
                                expect_b = mitigated(share_to_b, mrb);
                            }
                            if share_to_a >= 4 {
                                sim.deal_damage_typed(entity, lk.a, share_to_a, DamageTypeV1::Ap, AttackTypeV1::Skill);
                                expect_a = mitigated(share_to_a, mra);
                            }
                            // 补的伤害下一 tick 才扣：先从记下的血量里扣掉，下一次就不会再弹回去
                            lk.last_hp_a = ha.saturating_sub(expect_a);
                            lk.last_hp_b = hb.saturating_sub(expect_b);
                            self.link = Some(lk);
                        }
                    }
                }
                _ => self.clear_link(sim),
            }
        }

        // 4. R「拆线」：拔出 7 万内所有的针
        if consume_buff(sim, entity, UNPICK_ASK) {
            let r2 = UNPICK_RANGE * UNPICK_RANGE;
            let targets: Vec<(usize, u8, (u64, u64))> = self
                .needles
                .iter()
                .filter_map(|(&eid, &(cnt, exp))| {
                    if exp <= tick || cnt == 0 {
                        return None;
                    }
                    let e = sim.get_entity(eid)?;
                    (e.is_alive() && dist_sq(my_pos, e.pos()) <= r2).then_some((eid, cnt, e.pos()))
                })
                .collect();
            if targets.is_empty() {
                // 一根针都没有：冷却退到只剩 R_RETRY
                let left = sim
                    .get_entity(entity)
                    .and_then(|e| e.cooldown(SkillSlotV1::Ult))
                    .map_or(0, |c| c.remaining.saturating_sub(R_RETRY));
                Self::refund(sim, entity, SkillSlotV1::Ult, left);
            }
            for (eid, cnt, at) in targets {
                self.needles.remove(&eid);
                Self::sync_needles(sim, eid, 0, 0);
                let dmg = unpick_damage(cnt, ap);
                sim.deal_damage_typed(entity, eid, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                let mut slow = BuffV1::timed(R_SLOW, 90);
                slow.move_speed_mult = -50;
                sim.add_buff(eid, &slow);
                sim.play_view_effect("abysspact_effigy_withdraw", entity, &InputTargetV1::target(eid), 0, 0, 0);
                sim.play_sfx("abysspact_effigy_unpick_return", entity, &InputTargetV1::target(eid));
                // 针拖着红线从他身上飞回娃娃手里
                let back = ProjectileSpawnV1 {
                    caster_id: entity,
                    team: my_team,
                    x: at.0,
                    y: at.1.saturating_sub(THREAD_LIFT as u64),
                    radius: 1_000,
                    speed: RETURN_SPEED,
                    move_kind: ProjectileMoveKindV1::Target.code(),
                    target_id: entity,
                    target_x: my_pos.0,
                    target_y: my_pos.1,
                    penetrate: false,
                    attack_type: AttackTypeV1::Skill.code(),
                    casting_type: CastingTypeV1::Targeting.code(),
                    casting_target: CastingTargetV1::AllyChampion.code(),
                };
                sim.spawn_projectile(RETURN, NOOP, &back);
            }
        }
    }
}

/// 红线弹道打中时什么都不做。
#[derive(Debug)]
struct Noop;

impl StableEffectType for Noop {
    fn apply(&self, _sim: &mut StableSim<'_>, _seed: u64, _caster: usize, _input: InputTargetV1) {}
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_effigy:needles", EffigyPassive::default());
    module.add_native_effect(NOOP, Noop);
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

    #[test]
    fn a_share_does_not_bounce_back() {
        // A 掉 250：B 补 100；B 魔抗 25，预计掉 80。下一次 B 真掉了 80：算出来没有新伤害，不再弹回 A
        let share = shared_damage(250);
        let expect = mitigated(share, 25);
        assert_eq!(expect, 80);
        let (hb, last_b) = (1_000usize, 1_000usize - expect);
        let actual_after = hb - 80;
        assert_eq!(shared_damage(last_b.saturating_sub(actual_after)), 0);
    }

    #[test]
    fn the_thread_lies_between_the_two() {
        let (from, to) = thread_flight((0, 20_000), (40_000, 20_000)).expect("drawn");
        // 中间是 (20000, 20000 - 抬高)，往回一步放出，朝 B 飞
        assert!((from.0 - (20_000.0 - THREAD_STEP)).abs() < 1e-6);
        assert!((to.0 - (20_000.0 + THREAD_STEP)).abs() < 1e-6);
        assert!((from.1 - (20_000.0 - THREAD_LIFT)).abs() < 1e-6);
        assert_eq!(thread_flight((5, 5), (5, 5)), None);
    }
}
