//! 骸弦 (`abysspact_bonebow`) · 骨弓手 · 下路射手
//!
//! 招牌机制「亡兵」真实骷髅兵召唤 + W「葬礼」全军冲锋自爆 + R「亡军」5 骷髅列阵:
//! - 每第 4 支箭（普攻与 Q 穿骨均计数）或 Q 穿骨每命中一个敌方英雄，在目标身边通过 `sim.spawn_unit("abysspact_skeleton", ...)`
//!   拉起一名真实骷髅兵：继承骸弦 30% 攻击力，持续 6 秒（360 ticks），常规上限 3 个。
//! - R「亡军」落地直接爬出 5 名骷髅兵，持续 8 秒（480 ticks），不计入 3 个常规上限。
//! - W「葬礼」触发时，场上所有活着的骷髅兵（常规 + 大招）齐齐冲向她的目标并自爆：
//!   每个在落点 1.5 万内造成 `40 + 50% AD` 物理伤害并减速 30% 1 秒。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_bonebow";
pub const UNIT_NAME: &str = "abysspact_skeleton";
pub const Q_HIT_ASK: &str = "abysspact_bonebow_q_hit_ask";
pub const W_CMD: &str = "abysspact_bonebow_w_cmd";
pub const W_MARK: &str = "abysspact_bonebow_w_mark";
pub const W_SLOW: &str = "abysspact_bonebow_w_slow";
pub const R_ASK: &str = "abysspact_bonebow_r_ask";
pub const R_CAST_VOICE: &str = "abysspact_bonebow_r_voice";

pub const NORMAL_CAP: usize = 3;
pub const NORMAL_LIFE: u64 = 360; // 6.0s
pub const ULT_LIFE: u64 = 480;    // 8.0s
pub const ULT_COUNT: usize = 5;
pub const FUNERAL_RADIUS: u64 = 15_000; // 1.5万
pub const FUNERAL_BASE: usize = 40;
pub const FUNERAL_AD_PCT: usize = 50;

pub fn skeleton_stat(ad: usize, owner_max_hp: usize) -> StatV1 {
    StatV1 {
        attack: (ad.saturating_mul(30) / 100).max(20),
        magic_power: 0,
        hp: (owner_max_hp.saturating_mul(24) / 100).max(180),
        defence: 16,
        magic_resistance: 16,
        move_speed: 1120,
        hp_regen: 0,
        stack: 0,
        crit_chance: 0,
    }
}

pub fn skeleton_attack() -> UnitAttackV1 {
    UnitAttackV1 {
        attack_ratio: 100,
        attack: 0,
        range: 14_000,
        cooltime: 54,
        duration: 28,
        start_timing: 14,
        cancelable: false,
        attack_type: AttackTypeV1::BaseAttack.code(),
    }
}

pub fn funeral_damage(ad: usize) -> usize {
    FUNERAL_BASE + ad.saturating_mul(FUNERAL_AD_PCT) / 100
}

/// 5 offsets around a point (radius 13_000) for R「亡军」skeleton formation.
pub fn ring_offsets(idx: usize) -> (i64, i64) {
    const OFF: [(i64, i64); 5] = [
        (13_000, 0),
        (4_000, 12_400),
        (-10_500, 7_600),
        (-10_500, -7_600),
        (4_000, -12_400),
    ];
    OFF[idx % OFF.len()]
}

fn shift_pos(p: (u64, u64), off: (i64, i64)) -> (u64, u64) {
    let x = (p.0 as i64).saturating_add(off.0).max(10_000) as u64;
    let y = (p.1 as i64).saturating_add(off.1).max(10_000) as u64;
    (x, y)
}

#[derive(Clone, Default)]
struct BonebowPassive {
    voice: Voice,
    shot_count: usize,
    last_target: Option<usize>,
    /// Live normal skeletons (capped at 3, oldest despawned when overflowing).
    normal_skels: Vec<usize>,
    /// Live ult skeletons (uncapped, live 8s).
    ult_skels: Vec<usize>,
}

impl BonebowPassive {
    fn prune_dead(&mut self, sim: &StableSim<'_>) {
        self.normal_skels.retain(|&id| sim.get_entity(id).is_some_and(|e| e.is_alive()));
        self.ult_skels.retain(|&id| sim.get_entity(id).is_some_and(|e| e.is_alive()));
    }

    fn spawn_one(
        &mut self,
        sim: &mut StableSim<'_>,
        owner: usize,
        team: usize,
        at: (u64, u64),
        ad: usize,
        owner_max_hp: usize,
        is_ult: bool,
    ) {
        self.prune_dead(sim);
        if !is_ult {
            while self.normal_skels.len() >= NORMAL_CAP {
                let oldest = self.normal_skels.remove(0);
                sim.entity_set_hp(oldest, 0);
            }
        }
        let stat = skeleton_stat(ad, owner_max_hp);
        let atk = skeleton_attack();
        let life = if is_ult { ULT_LIFE } else { NORMAL_LIFE };
        if let Some(uid) = sim.spawn_unit(UNIT_NAME, owner, team, at.0, at.1, life, &stat, &atk) {
            if is_ult {
                self.ult_skels.push(uid);
            } else {
                self.normal_skels.push(uid);
            }
            sim.play_view_effect("abysspact_bonebow_crypt", owner, &InputTargetV1::pos(at.0, at.1), 0, 0, 0);
            sim.play_sfx("abysspact_bonebow_skeleton_rise", owner, &InputTargetV1::pos(at.0, at.1));
        }
    }

    fn run_funeral(&mut self, sim: &mut StableSim<'_>, owner: usize, team: usize, my_pos: (u64, u64), ad: usize) {
        self.prune_dead(sim);
        let mut all: Vec<usize> = Vec::with_capacity(self.normal_skels.len() + self.ult_skels.len());
        all.append(&mut self.normal_skels);
        all.append(&mut self.ult_skels);
        if all.is_empty() {
            return;
        }

        // Determine rally point: W-marked enemy -> last attacked live target -> nearest live enemy champion
        let mut rally: Option<(u64, u64)> = None;
        let n_ent = sim.entity_count();
        for i in 0..n_ent {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_alive() && e.team() != team && has_buff(sim, e.id(), W_MARK) {
                rally = Some(e.pos());
                sim.entity_remove_buff(e.id(), W_MARK);
                break;
            }
        }
        if rally.is_none() {
            if let Some(lt) = self.last_target {
                if let Some(e) = sim.get_entity(lt) {
                    if e.is_alive() && e.team() != team {
                        rally = Some(e.pos());
                    }
                }
            }
        }
        if rally.is_none() {
            let mut best: Option<(u64, (u64, u64))> = None;
            for i in 0..n_ent {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_alive() || e.team() == team || e.is_tower() {
                    continue;
                }
                let d2 = dist_sq(my_pos, e.pos());
                if d2 <= 80_000 * 80_000 {
                    // Prioritize champions slightly
                    let score = if e.is_champion() { d2 / 4 } else { d2 };
                    if best.is_none_or(|(bd, _)| score < bd) {
                        best = Some((score, e.pos()));
                    }
                }
            }
            rally = best.map(|(_, p)| p);
        }

        let target_pos = rally.unwrap_or(my_pos);
        let dmg = funeral_damage(ad);
        let rad_sq = FUNERAL_RADIUS * FUNERAL_RADIUS;

        for (idx, sid) in all.into_iter().enumerate() {
            // Rush skeleton into tight cluster at target and self-destruct
            let off = ring_offsets(idx);
            let burst_pos = shift_pos(target_pos, (off.0 / 3, off.1 / 3));
            sim.entity_set_pos(sid, burst_pos.0, burst_pos.1);
            sim.play_view_effect("abysspact_bonebow_bone_burst", owner, &InputTargetV1::pos(burst_pos.0, burst_pos.1), 0, 0, 0);
            if idx == 0 {
                sim.play_sfx("abysspact_bonebow_funeral_burst", owner, &InputTargetV1::pos(burst_pos.0, burst_pos.1));
            }

            let mut victims = Vec::new();
            let n = sim.entity_count();
            for i in 0..n {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_alive() || e.team() == team || e.is_tower() {
                    continue;
                }
                if dist_sq(burst_pos, e.pos()) <= rad_sq {
                    victims.push(e.id());
                }
            }
            for vid in victims {
                sim.deal_damage_typed(owner, vid, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
                let mut slow = BuffV1::timed(W_SLOW, 60);
                slow.move_speed_mult = -30;
                sim.add_buff(vid, &slow);
            }
            sim.entity_set_hp(sid, 0);
        }
    }
}

impl StablePassive for BonebowPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.shot_count = 0;
        self.last_target = None;
        self.normal_skels.clear();
        self.ult_skels.clear();
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
        let Some((my_team, ad, max_hp)) = sim
            .get_entity(entity)
            .map(|e| (e.team(), e.stat().attack, e.hp().1))
        else {
            return;
        };
        let Some((tpos, is_champ, is_tower)) = sim
            .get_entity(target)
            .map(|e| (e.pos(), e.is_champion(), e.is_tower()))
        else {
            return;
        };
        if is_champ {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
        if !is_tower {
            self.last_target = Some(target);
        }

        // Every 4th arrow raises a skeleton right beside the target
        self.shot_count += 1;
        if self.shot_count % 4 == 0 {
            let spawn_pos = shift_pos(tpos, (8_000, 0));
            self.spawn_one(sim, entity, my_team, spawn_pos, ad, max_hp, false);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, ad, max_hp)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.stat().attack, e.hp().1))
        else {
            return;
        };
        if !alive {
            return;
        }

        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 1. Q「穿骨」hits on enemy champions raise 1 normal skeleton each (and count toward passive)
        let mut q_hits = Vec::new();
        let mut r_center: Option<(u64, u64)> = None;
        let n_ent = sim.entity_count();
        for i in 0..n_ent {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() || e.team() == my_team {
                continue;
            }
            let eid = e.id();
            if has_buff(sim, eid, Q_HIT_ASK) {
                q_hits.push((eid, e.pos()));
            }
            if r_center.is_none() && has_buff(sim, eid, R_ASK) {
                r_center = Some(e.pos());
                sim.entity_remove_buff(eid, R_ASK);
            }
        }
        for (eid, pos) in q_hits {
            sim.entity_remove_buff(eid, Q_HIT_ASK);
            self.shot_count += 1;
            self.last_target = Some(eid);
            self.spawn_one(sim, entity, my_team, shift_pos(pos, (7_500, 0)), ad, max_hp, false);
        }

        // 2. R「亡军」spawns 5 uncapped 8s skeletons in a formation ring!
        if consume_buff(sim, entity, R_ASK) || r_center.is_some() {
            let center = r_center
                .or_else(|| self.last_target.and_then(|id| sim.get_entity(id)).filter(|e| e.is_alive()).map(|e| e.pos()))
                .unwrap_or(my_pos);
            for k in 0..ULT_COUNT {
                let pt = shift_pos(center, ring_offsets(k));
                self.spawn_one(sim, entity, my_team, pt, ad, max_hp, true);
            }
        }

        // 3. W「葬礼」orders all live skeletons to charge & self-destruct!
        if consume_buff(sim, entity, W_CMD) {
            self.run_funeral(sim, entity, my_team, my_pos, ad);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_bonebow:skeletons", BonebowPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn skeleton_inherits_30pct_ad_and_scaled_hp() {
        let s = skeleton_stat(200, 1500);
        assert_eq!(s.attack, 60);
        assert_eq!(s.hp, 360);
        let low = skeleton_stat(40, 500);
        assert_eq!(low.attack, 20);
        assert_eq!(low.hp, 180);
    }

    #[test]
    fn funeral_damage_scales_with_50pct_ad() {
        assert_eq!(funeral_damage(100), 90);
        assert_eq!(funeral_damage(260), 170);
    }
}
