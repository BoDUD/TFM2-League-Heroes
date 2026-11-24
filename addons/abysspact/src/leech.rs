//! 附骨 (`abysspact_leech`) · 深渊寄生者 · 打野法术刺客
//!
//! 招牌机制「附骨之疽」寄生敌方英雄后背 3 秒吸血 + 宿主死跳下一目标 + R「万蛭」裂成 5 只小水蛭群吸:
//! - Q「扑附」命中敌方英雄后附着其后背 3 秒（180 ticks）：
//!   * 不可选中（常规伤害减免 100%）、实时贴在宿主背后，显示钩子切换 `attach` 附着动作；
//!   * 每 0.5 秒（30 ticks）吸取宿主 2.5% 最大生命（魔法伤害）并等量治疗自己，宿主移速 -30%；
//!   * **代价「附骨之疽」**：宿主受到外部伤害时，附骨同步承受 25% 伤害并闪品红 `shared_hit`！
//!   * 宿主阵亡时立刻跳到 5 万内最近另一名敌方英雄身上再附 2 秒（每次最多跳一次）。
//! - R「万蛭」：裂成 5 只小水蛭扑向 9 万内敌方英雄各附 3 秒（人少时多余水蛭扑向血最少目标），
//!   每 0.5 秒吸 2% 最大生命，3 秒结束小水蛭聚回本体并把累计吸取血量全部回给自己；期间每个宿主受伤他分担 10%。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_leech";
pub const NATIVE_MARK: &str = "abysspact_leech_native";
pub const ATTACH_ASK: &str = "abysspact_leech_attach_ask";
pub const ATTACHED_BUFF: &str = "abysspact_leech_attached";
pub const HOST_MARK: &str = "abysspact_leech_host_mark";
pub const MINI_CLING: &str = "abysspact_leech_mini_cling";
pub const R_SPLIT_ASK: &str = "abysspact_leech_r_split";
pub const R_SWARM_BUFF: &str = "abysspact_leech_swarm";
pub const R_CAST_VOICE: &str = "abysspact_leech_r_voice";

pub const ATTACH_TICKS: usize = 180;      // 3.0s
pub const JUMP_TICKS: usize = 120;        // 2.0s on host death jump
pub const JUMP_RANGE: u64 = 50_000;       // 5.0万
pub const DRAIN_PERIOD: usize = 30;       // 0.5s
pub const DRAIN_PCT_X10: usize = 25;      // 2.5% max HP per 0.5s
pub const SHARED_PAIN_PCT: usize = 25;    // 25% of host's external damage
pub const SWARM_RANGE: u64 = 90_000;      // 9.0万
pub const SWARM_TICKS: usize = 180;       // 3.0s
pub const SWARM_DRAIN_PCT: usize = 2;     // 2% max HP per 0.5s per leech
pub const SWARM_SHARED_PCT: usize = 10;   // 10% shared pain per host

pub fn drain_amount(host_max_hp: usize) -> usize {
    host_max_hp.saturating_mul(DRAIN_PCT_X10) / 1000
}

pub fn shared_pain(host_lost: usize, pct: usize) -> usize {
    host_lost.saturating_mul(pct) / 100
}

#[derive(Clone, Copy)]
struct HostAttach {
    host_id: usize,
    end_tick: usize,
    next_drain: usize,
    last_host_hp: usize,
    jumped: bool,
}

#[derive(Clone)]
struct SwarmState {
    /// (host_id, leech_count, last_host_hp)
    hosts: Vec<(usize, usize, usize)>,
    end_tick: usize,
    next_drain: usize,
    banked_heal: usize,
}

#[derive(Clone, Default)]
struct LeechPassive {
    voice: Voice,
    attach: Option<HostAttach>,
    swarm: Option<SwarmState>,
}

impl LeechPassive {
    fn clear_attach(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if let Some(a) = self.attach.take() {
            sim.entity_remove_buff(a.host_id, HOST_MARK);
        }
        sim.entity_remove_buff(entity, ATTACHED_BUFF);
    }

    fn start_attach(&mut self, sim: &mut StableSim<'_>, entity: usize, host_id: usize, dur: usize, jumped: bool) {
        let Some(host_hp) = sim.get_entity(host_id).filter(|e| e.is_alive()).map(|e| e.hp().0) else {
            return;
        };
        let tick = sim.tick();
        self.attach = Some(HostAttach {
            host_id,
            end_tick: tick + dur,
            next_drain: tick + DRAIN_PERIOD,
            last_host_hp: host_hp,
            jumped,
        });
        let mut att = BuffV1::timed(ATTACHED_BUFF, dur);
        att.damaged_reduce = 100;
        att.cc_immune = true;
        sim.add_buff(entity, &att);

        let mut hm = BuffV1::timed(HOST_MARK, dur);
        hm.move_speed_mult = -30;
        sim.add_buff(host_id, &hm);
    }

    fn apply_self_pain(sim: &mut StableSim<'_>, entity: usize, pain: usize) {
        if pain < 4 {
            return;
        }
        let Some(cur) = sim.get_entity(entity).filter(|e| e.is_alive()).map(|e| e.hp().0) else {
            return;
        };
        sim.entity_set_hp(entity, cur.saturating_sub(pain));
        sim.play_view_effect("abysspact_leech_shared_hit", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_leech_shared_pain", entity, &InputTargetV1::target(entity));
    }

    fn start_swarm(&mut self, sim: &mut StableSim<'_>, entity: usize, my_team: usize, my_pos: (u64, u64)) {
        self.clear_attach(sim, entity);
        let r2 = SWARM_RANGE * SWARM_RANGE;
        let mut foes: Vec<(usize, usize)> = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_champion() && e.is_alive() && e.team() != my_team && dist_sq(my_pos, e.pos()) <= r2 {
                foes.push((e.id(), e.hp().0));
            }
        }
        if foes.is_empty() {
            return;
        }
        // Sort by lowest HP so extra leeches (when < 5 enemies) pile onto the lowest-HP enemy!
        foes.sort_by_key(|&(_, hp)| hp);
        let mut counts: Vec<(usize, usize, usize)> = foes.iter().map(|&(id, hp)| (id, 1, hp)).collect();
        if counts.len() > 5 {
            counts.truncate(5);
        } else {
            let extra = 5usize.saturating_sub(counts.len());
            counts[0].1 += extra;
        }
        let tick = sim.tick();
        for &(hid, _, _) in &counts {
            sim.add_buff(hid, &BuffV1::timed(MINI_CLING, SWARM_TICKS));
        }
        let mut sw = BuffV1::timed(R_SWARM_BUFF, SWARM_TICKS);
        sw.damaged_reduce = 100;
        sw.cc_immune = true;
        sim.add_buff(entity, &sw);
        sim.apply_cc(entity, &CcV1::of_kind(CcKindV1::BlockAttack, SWARM_TICKS as u64));
        sim.play_view_effect("abysspact_leech_split", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_leech_split", entity, &InputTargetV1::target(entity));

        self.swarm = Some(SwarmState {
            hosts: counts,
            end_tick: tick + SWARM_TICKS,
            next_drain: tick + DRAIN_PERIOD,
            banked_heal: 0,
        });
    }
}

impl StablePassive for LeechPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.attach = None;
        self.swarm = None;
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, target: usize, _damage: &mut usize) {
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
        self.attach = None;
        self.swarm = None;
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
            self.clear_attach(sim, entity);
            self.swarm = None;
            return;
        }
        let tick = sim.tick();
        if !has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 1. Check R「万蛭」cast
        if consume_buff(sim, entity, R_SPLIT_ASK) {
            self.start_swarm(sim, entity, my_team, my_pos);
        }

        // 2. Maintain R「万蛭」5-leech swarm
        if let Some(mut sw) = self.swarm.take() {
            if tick >= sw.end_tick {
                for &(hid, _, _) in &sw.hosts {
                    sim.entity_remove_buff(hid, MINI_CLING);
                }
                sim.entity_remove_buff(entity, R_SWARM_BUFF);
                if sw.banked_heal > 0 {
                    sim.heal(entity, entity, sw.banked_heal);
                }
                sim.play_view_effect("abysspact_leech_rejoin", entity, &InputTargetV1::target(entity), 0, 0, 0);
                sim.play_sfx("abysspact_leech_rejoin", entity, &InputTargetV1::target(entity));
            } else {
                let do_drain = tick >= sw.next_drain;
                if do_drain {
                    sw.next_drain = tick + DRAIN_PERIOD;
                }
                let mut total_pain = 0usize;
                for (hid, cnt, last_hp) in &mut sw.hosts {
                    let Some((h_alive, cur_hp, max_hp)) = sim
                        .get_entity(*hid)
                        .map(|e| (e.is_alive(), e.hp().0, e.hp().1))
                    else {
                        continue;
                    };
                    if !h_alive {
                        continue;
                    }
                    if tick % 3 == 0 {
                        let lost = (*last_hp).saturating_sub(cur_hp);
                        total_pain = total_pain.saturating_add(shared_pain(lost, SWARM_SHARED_PCT));
                    }
                    if do_drain {
                        let amt = max_hp.saturating_mul(SWARM_DRAIN_PCT * (*cnt)) / 100;
                        if amt > 0 {
                            sim.deal_damage_typed(entity, *hid, amt, DamageTypeV1::Ap, AttackTypeV1::Skill);
                            sw.banked_heal = sw.banked_heal.saturating_add(amt);
                            sim.play_view_effect("abysspact_leech_drain", entity, &InputTargetV1::target(*hid), 0, 0, 0);
                        }
                    }
                    *last_hp = sim.get_entity(*hid).map(|e| e.hp().0).unwrap_or(cur_hp);
                }
                if total_pain > 0 {
                    Self::apply_self_pain(sim, entity, total_pain);
                }
                if sim.get_entity(entity).is_some_and(|e| e.is_alive()) {
                    self.swarm = Some(sw);
                }
            }
            return;
        }

        // 3. Check Q「扑附」new attach target
        if self.attach.is_none() {
            let mut target = None;
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_champion() && e.is_alive() && e.team() != my_team && has_buff(sim, e.id(), ATTACH_ASK) {
                    target = Some(e.id());
                    break;
                }
            }
            if let Some(hid) = target {
                sim.entity_remove_buff(hid, ATTACH_ASK);
                self.start_attach(sim, entity, hid, ATTACH_TICKS, false);
            }
        }

        // 4. Maintain Q「扑附」single-host clinging + 25% shared pain + host-death jump
        if let Some(mut att) = self.attach {
            let host_info = sim.get_entity(att.host_id).map(|e| (e.is_alive(), e.pos(), e.hp().0, e.hp().1));
            match host_info {
                Some((true, hpos, cur_hp, max_hp)) if tick < att.end_tick => {
                    // Cling right behind host every 3 ticks
                    if tick % 3 == 0 {
                        sim.entity_set_pos(entity, hpos.0.saturating_sub(2_500), hpos.1);
                        let ext_lost = att.last_host_hp.saturating_sub(cur_hp);
                        let pain = shared_pain(ext_lost, SHARED_PAIN_PCT);
                        if pain > 0 {
                            Self::apply_self_pain(sim, entity, pain);
                        }
                    }
                    // Drain 2.5% max HP every 0.5s
                    if tick >= att.next_drain {
                        att.next_drain = tick + DRAIN_PERIOD;
                        let amt = drain_amount(max_hp);
                        if amt > 0 {
                            sim.deal_damage_typed(entity, att.host_id, amt, DamageTypeV1::Ap, AttackTypeV1::Skill);
                            sim.heal(entity, entity, amt);
                            sim.play_view_effect("abysspact_leech_drain", entity, &InputTargetV1::target(att.host_id), 0, 0, 0);
                            sim.play_sfx("abysspact_leech_drain", entity, &InputTargetV1::target(att.host_id));
                        }
                    }
                    att.last_host_hp = sim.get_entity(att.host_id).map(|e| e.hp().0).unwrap_or(cur_hp);
                    self.attach = Some(att);
                }
                Some((false, dead_pos, _, _)) if !att.jumped => {
                    // Host died -> jump to nearest enemy champion within 5万 for 2s!
                    self.clear_attach(sim, entity);
                    let r2 = JUMP_RANGE * JUMP_RANGE;
                    let mut next_host: Option<(usize, u64)> = None;
                    for i in 0..sim.entity_count() {
                        let Some(e) = sim.entity_at(i) else { continue };
                        if e.is_champion() && e.is_alive() && e.team() != my_team {
                            let d2 = dist_sq(dead_pos, e.pos());
                            if d2 <= r2 && next_host.is_none_or(|(_, best)| d2 < best) {
                                next_host = Some((e.id(), d2));
                            }
                        }
                    }
                    if let Some((nh, _)) = next_host {
                        sim.play_view_effect("abysspact_leech_jump", entity, &InputTargetV1::target(nh), 0, 0, 0);
                        sim.play_sfx("abysspact_leech_jump", entity, &InputTargetV1::target(nh));
                        self.start_attach(sim, entity, nh, JUMP_TICKS, true);
                    }
                }
                _ => {
                    self.clear_attach(sim, entity);
                }
            }
        }
    }
}

/// While attached, W「蚀髓」reaches host effortlessly (+2.5万).
#[derive(Debug)]
struct AttachedWRange;

impl StableEffectType for AttachedWRange {
    fn apply(&self, _sim: &mut StableSim<'_>, _seed: u64, _caster: usize, _input: InputTargetV1) {}
    fn may_adjust_range(&self) -> bool {
        true
    }
    fn range_adjust(&self, caster: &StableEntityView<'_>, _target: &StableEntityView<'_>) -> u64 {
        let on = (0..caster.buff_count()).any(|i| caster.buff_at(i).is_some_and(|b| b.name() == ATTACHED_BUFF));
        if on { 25_000 } else { 0 }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_leech:parasite", LeechPassive::default());
    module.add_native_effect("abysspact_leech:w_range", AttachedWRange);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn drain_and_shared_pain_math() {
        assert_eq!(drain_amount(2000), 50);
        assert_eq!(shared_pain(400, SHARED_PAIN_PCT), 100);
        assert_eq!(shared_pain(400, SWARM_SHARED_PCT), 40);
    }
}
