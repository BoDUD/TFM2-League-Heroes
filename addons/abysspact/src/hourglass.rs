//! 返照 (`abysspact_hourglass`) · 沙漏女巫 · 辅助
//!
//! 招牌机制「回光」3 秒倒血救死 + R「倒流」全队 3 秒前位置与血量倒回 + 代价「老去」黑发→灰白→全白:
//! - 记录全队每名存活友方英雄最近 3 秒（180 ticks）的位置与血量快照。
//! - Q「回光」：给 7 万内一名友军打上 3 秒回光印记（含 `undying = true` 保命拦截），返照老去 +1 层；
//!   * 3 秒内若被打至致命伤（HP <= 1），立刻把血量倒回打印记时的高值、免死并撤掉印记！
//!   * 3 秒到期则把血量倒回打印记时的高值（只增不减，连断誓/七弹自己烧掉的血也一并倒回！）。
//! - R「倒流」：返照老去 +3 层；10 万内所有存活友方英雄瞬间倒回 3 秒前的位置与血量（只增不减，已阵亡者不回来）！
//! - 代价「老去」（上限 10 层，死亡复活清零返老还童）：每层最大生命 -2.5%、移速 -2%；
//!   0–3 层黑发，4–7 层灰白（`abysspact_hourglass_hair_grey`），8–10 层全白（`abysspact_hourglass_hair_white`）。

use std::collections::{HashMap, VecDeque};
use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_hourglass";
pub const NATIVE_MARK: &str = "abysspact_hourglass_native";
pub const AGE_BUFF: &str = "abysspact_hourglass_age";
pub const HAIR_GREY: &str = "abysspact_hourglass_hair_grey";
pub const HAIR_WHITE: &str = "abysspact_hourglass_hair_white";
pub const Q_MARK_ASK: &str = "abysspact_hourglass_q_ask";
pub const CLOCK_BUFF: &str = "abysspact_hourglass_clock";
pub const R_REWIND_ASK: &str = "abysspact_hourglass_r_ask";
pub const R_CAST_VOICE: &str = "abysspact_hourglass_r_voice";

pub const AGE_CAP: u8 = 10;
pub const REWIND_TICKS: usize = 180; // 3.0s
pub const SNAP_INTERVAL: usize = 6;  // sample every 0.1s (30 samples)
pub const R_RANGE: u64 = 100_000;    // 10.0万

pub fn age_penalties(stacks: u8) -> (i32, i32) {
    let s = stacks.min(AGE_CAP) as i32;
    (-(s * 25 / 10), -(s * 2))
}

pub fn hair_tier(stacks: u8) -> Option<&'static str> {
    match stacks.min(AGE_CAP) {
        0..=3 => None,
        4..=7 => Some(HAIR_GREY),
        _ => Some(HAIR_WHITE),
    }
}

#[derive(Clone, Copy)]
struct Snap {
    tick: usize,
    pos: (u64, u64),
    hp: usize,
}

#[derive(Clone, Copy)]
struct ActiveMark {
    saved_hp: usize,
    end_tick: usize,
}

#[derive(Clone, Default)]
struct HourglassPassive {
    voice: Voice,
    age: u8,
    history: HashMap<usize, VecDeque<Snap>>,
    marks: HashMap<usize, ActiveMark>,
}

impl HourglassPassive {
    fn sync_age(&self, sim: &mut StableSim<'_>, entity: usize) {
        sim.entity_remove_buff(entity, AGE_BUFF);
        sim.entity_remove_buff(entity, HAIR_GREY);
        sim.entity_remove_buff(entity, HAIR_WHITE);
        if self.age > 0 {
            let (hp_m, ms_m) = age_penalties(self.age);
            let mut ab = BuffV1::named(AGE_BUFF);
            ab.hp_mult = hp_m;
            ab.move_speed_mult = ms_m;
            sim.add_buff(entity, &ab);
        }
        if let Some(hair) = hair_tier(self.age) {
            sim.add_buff(entity, &BuffV1::named(hair));
        }
    }

    fn add_age(&mut self, sim: &mut StableSim<'_>, entity: usize, delta: u8) {
        let next = self.age.saturating_add(delta).min(AGE_CAP);
        if next != self.age {
            self.age = next;
            self.sync_age(sim, entity);
            sim.play_sfx("abysspact_hourglass_age_tick", entity, &InputTargetV1::target(entity));
        }
    }

    fn rewind_ally_hp(sim: &mut StableSim<'_>, caster: usize, ally_id: usize, target_hp: usize) {
        let Some((alive, cur_hp, max_hp)) = sim
            .get_entity(ally_id)
            .map(|e| (e.is_alive(), e.hp().0, e.hp().1))
        else {
            return;
        };
        if !alive {
            return;
        }
        let want = target_hp.max(cur_hp).min(max_hp).max(1);
        if want > cur_hp {
            sim.entity_set_hp(ally_id, want);
        }
        sim.play_view_effect("abysspact_hourglass_rewind", caster, &InputTargetV1::target(ally_id), 0, 0, 0);
        sim.play_sfx("abysspact_hourglass_rewind_snap", caster, &InputTargetV1::target(ally_id));
    }
}

impl StablePassive for HourglassPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.age = 0;
        self.marks.clear();
        self.sync_age(sim, entity);
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
        // Death returns her youth completely!
        self.age = 0;
        self.marks.clear();
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos()))
        else {
            return;
        };
        let tick = sim.tick();

        // 1. Sample 3-second rolling (pos, hp) history for all alive allied champions
        if tick % SNAP_INTERVAL == 0 {
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_champion() && e.team() == my_team {
                    let eid = e.id();
                    if e.is_alive() {
                        let q = self.history.entry(eid).or_default();
                        q.push_back(Snap { tick, pos: e.pos(), hp: e.hp().0 });
                        while q.len() > 36 || q.front().is_some_and(|s| tick.saturating_sub(s.tick) > REWIND_TICKS + 12) {
                            q.pop_front();
                        }
                    } else {
                        self.history.remove(&eid);
                    }
                }
            }
        }

        // 2. Process active Q「回光」marks (lethal save OR 3s completion!)
        let mut finished = Vec::new();
        for (&aid, &mk) in &self.marks {
            match sim.get_entity(aid).map(|e| (e.is_alive(), e.hp().0)) {
                Some((true, cur_hp)) if cur_hp <= 2 || tick >= mk.end_tick => {
                    finished.push((aid, mk.saved_hp, true));
                }
                Some((false, _)) | None => {
                    finished.push((aid, mk.saved_hp, false));
                }
                _ => {}
            }
        }
        for (aid, saved_hp, do_rewind) in finished {
            self.marks.remove(&aid);
            sim.entity_remove_buff(aid, CLOCK_BUFF);
            if do_rewind {
                Self::rewind_ally_hp(sim, entity, aid, saved_hp);
            }
        }

        if !alive {
            return;
        }
        if !has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 3. Collect new Q「回光」marks on allies
        let mut new_marks = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_champion() && e.is_alive() && e.team() == my_team && has_buff(sim, e.id(), Q_MARK_ASK) {
                new_marks.push((e.id(), e.hp().0));
            }
        }
        for (aid, saved_hp) in new_marks {
            sim.entity_remove_buff(aid, Q_MARK_ASK);
            self.marks.insert(aid, ActiveMark { saved_hp, end_tick: tick + REWIND_TICKS });
            let mut clk = BuffV1::timed(CLOCK_BUFF, REWIND_TICKS);
            clk.undying = true;
            sim.add_buff(aid, &clk);
            self.add_age(sim, entity, 1);
        }

        // 4. Handle R「倒流」: rewind EVERY alive ally within 10万 to their 3s-ago position & HP!
        if consume_buff(sim, entity, R_REWIND_ASK) {
            self.add_age(sim, entity, 3);
            sim.play_view_effect("abysspact_hourglass_hourglass", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_sfx("abysspact_hourglass_flip", entity, &InputTargetV1::target(entity));
            let r2 = R_RANGE * R_RANGE;
            let mut allies = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_champion() && e.is_alive() && e.team() == my_team && dist_sq(my_pos, e.pos()) <= r2 {
                    allies.push((e.id(), e.pos(), e.hp().0));
                }
            }
            for (aid, cur_pos, cur_hp) in allies {
                let snap = self.history.get(&aid).and_then(|q| q.front().copied());
                let (dest_pos, old_hp) = snap.map(|s| (s.pos, s.hp)).unwrap_or((cur_pos, cur_hp));
                sim.play_view_effect("abysspact_hourglass_echo", entity, &InputTargetV1::pos(cur_pos.0, cur_pos.1), 0, 0, 0);
                sim.entity_set_pos(aid, dest_pos.0, dest_pos.1);
                Self::rewind_ally_hp(sim, entity, aid, old_hp);
                sim.play_view_effect("abysspact_hourglass_sand_burst", entity, &InputTargetV1::pos(dest_pos.0, dest_pos.1), 0, 0, 0);
            }
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_hourglass:sands", HourglassPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn aging_penalties_and_hair_tiers_match_spec() {
        assert_eq!(age_penalties(0), (0, 0));
        assert_eq!(age_penalties(4), (-10, -8));
        assert_eq!(age_penalties(10), (-25, -20));
        assert_eq!(hair_tier(0), None);
        assert_eq!(hair_tier(3), None);
        assert_eq!(hair_tier(4), Some(HAIR_GREY));
        assert_eq!(hair_tier(7), Some(HAIR_GREY));
        assert_eq!(hair_tier(8), Some(HAIR_WHITE));
        assert_eq!(hair_tier(10), Some(HAIR_WHITE));
    }
}
