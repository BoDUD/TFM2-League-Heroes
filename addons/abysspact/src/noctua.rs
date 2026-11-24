//! 千蛾 (`abysspact_noctua`) · 蛾身少女 · 中路法师
//!
//! 招牌机制「散身」吃爆发自动碎成蛾群瞬移躲避 + 代价「聚身」1.25 秒禁技能 + 鳞粉三层 + R「万蛾」3.5 秒风暴沉默:
//! - 被动「散身」：1 秒内累计掉血 > 12% 最大生命（12 秒冷却）时自动碎成飞蛾：
//!   * 0.6 秒不可选中（`damaged_reduce = 100, cc_immune = true`），朝背离最近敌人的方向瞬移 2.5 万；
//!   * 0.6 秒后聚回人形并触发**代价「聚身」**：1.25 秒（75 ticks）`BlockSkill` 放不了技能（可普攻）。
//! - 鳞粉：Q「蛾群」与 R「万蛾」叠 1–3 层鳞粉（持续 4 秒，每层 -10% 移速，头顶显示 `scales_1..3`）。
//! - R「万蛾」：整个人化成 3.5 秒（210 ticks）不可选中的蛾群风暴（+30% 移速、穿人），
//!   每 0.25 秒对 2.5 万内敌人造成 `25 + 10% AP` 法伤并叠 1 层鳞粉；
//!   结束时在原地聚身爆开鳞粉冲击波，**沉默 3 万内敌人 1.25 秒**，她自己也照常聚身 1.25 秒。

use std::collections::{HashMap, VecDeque};
use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_noctua";
pub const NATIVE_MARK: &str = "abysspact_noctua_native";
pub const SCALE_ASK: &str = "abysspact_noctua_scale_ask";
pub const DISPERSE_BUFF: &str = "abysspact_noctua_disperse";
pub const STORM_BUFF: &str = "abysspact_noctua_storm";
pub const R_STORM_ASK: &str = "abysspact_noctua_r_storm";
pub const R_CAST_VOICE: &str = "abysspact_noctua_r_voice";

pub const BURST_WINDOW: usize = 60;      // 1.0s rolling damage window
pub const BURST_PCT: usize = 12;         // >12% max HP triggers scatter
pub const SCATTER_CD: usize = 720;       // 12.0s cooldown
pub const SCATTER_TICKS: usize = 36;     // 0.6s untargetable
pub const REFORM_SILENCE: u64 = 75;      // 1.25s post-reform BlockSkill
pub const SCATTER_DIST: i64 = 25_000;    // 2.5万 away from nearest enemy
pub const SCALE_TICKS: usize = 240;      // 4.0s scales duration
pub const STORM_TICKS: usize = 210;      // 3.5s moth storm
pub const STORM_PERIOD: usize = 15;      // 0.25s pulse
pub const STORM_RADIUS: u64 = 25_000;
pub const SHOCK_RADIUS: u64 = 30_000;

pub fn storm_tick_damage(ap: usize) -> usize {
    25 + ap.saturating_mul(10) / 100
}

pub fn scale_buff_name(k: u8) -> Option<&'static str> {
    match k {
        1 => Some("abysspact_noctua_scales_1"),
        2 => Some("abysspact_noctua_scales_2"),
        3 => Some("abysspact_noctua_scales_3"),
        _ => None,
    }
}

#[derive(Clone, Default)]
struct NoctuaPassive {
    voice: Voice,
    last_hp: usize,
    dmg_win: VecDeque<(usize, usize)>,
    scatter_ready_at: usize,
    reform_at: Option<usize>,
    storm_end: Option<(usize, usize)>, // (end_tick, next_pulse)
    scales: HashMap<usize, (u8, usize)>,
}

impl NoctuaPassive {
    fn sync_scales(sim: &mut StableSim<'_>, eid: usize, stacks: u8, dur: usize) {
        for k in 1..=3 {
            if let Some(n) = scale_buff_name(k) {
                sim.entity_remove_buff(eid, n);
            }
        }
        if let Some(n) = scale_buff_name(stacks) {
            let mut b = BuffV1::timed(n, dur.max(1));
            b.move_speed_mult = -10 * (stacks as i32);
            sim.add_buff(eid, &b);
        }
    }

    fn add_scale(&mut self, sim: &mut StableSim<'_>, eid: usize, tick: usize) {
        let cur = self.scales.get(&eid).map(|&(c, exp)| if exp > tick { c } else { 0 }).unwrap_or(0);
        let next = (cur + 1).min(3);
        self.scales.insert(eid, (next, tick + SCALE_TICKS));
        Self::sync_scales(sim, eid, next, SCALE_TICKS);
    }

    fn retreat_pos(sim: &StableSim<'_>, my_team: usize, my_pos: (u64, u64)) -> (u64, u64) {
        let mut nearest: Option<((u64, u64), u64)> = None;
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_champion() && e.is_alive() && e.team() != my_team {
                let d2 = dist_sq(my_pos, e.pos());
                if nearest.is_none_or(|(_, b)| d2 < b) {
                    nearest = Some((e.pos(), d2));
                }
            }
        }
        let (dx, dy) = match nearest {
            Some((ep, _)) => (my_pos.0 as i64 - ep.0 as i64, my_pos.1 as i64 - ep.1 as i64),
            None => (-1, 0),
        };
        let len = ((dx as f64).hypot(dy as f64)).max(1.0);
        let nx = (my_pos.0 as i64 + ((dx as f64 / len) * SCATTER_DIST as f64) as i64).clamp(10_000, 390_000) as u64;
        let ny = (my_pos.1 as i64 + ((dy as f64 / len) * SCATTER_DIST as f64) as i64).clamp(10_000, 390_000) as u64;
        (nx, ny)
    }
}

impl StablePassive for NoctuaPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.last_hp = sim.get_entity(entity).map(|e| e.hp().0).unwrap_or(0);
        self.dmg_win.clear();
        self.scatter_ready_at = 0;
        self.reform_at = None;
        self.storm_end = None;
        self.scales.clear();
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
        self.dmg_win.clear();
        self.reform_at = None;
        self.storm_end = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, cur_hp, max_hp, ap)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.hp().0, e.hp().1, e.stat().magic_power))
        else {
            return;
        };
        let tick = sim.tick();
        self.scales.retain(|&eid, &mut (_, exp)| exp > tick && sim.get_entity(eid).is_some_and(|e| e.is_alive()));
        if !alive {
            return;
        }
        if !has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 1. Collect Scales marks from Q hits
        let mut scale_hits = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_alive() && e.team() != my_team && !e.is_tower() && has_buff(sim, e.id(), SCALE_ASK) {
                scale_hits.push(e.id());
            }
        }
        for eid in scale_hits {
            sim.entity_remove_buff(eid, SCALE_ASK);
            self.add_scale(sim, eid, tick);
        }

        // 2. Finish passive scatter reform -> 1.25s BlockSkill cost
        if let Some(rat) = self.reform_at {
            if tick >= rat {
                self.reform_at = None;
                sim.entity_remove_buff(entity, DISPERSE_BUFF);
                sim.play_view_effect("abysspact_noctua_reform", entity, &InputTargetV1::target(entity), 0, 0, 0);
                sim.play_sfx("abysspact_noctua_reform", entity, &InputTargetV1::target(entity));
                sim.apply_cc(entity, &CcV1::of_kind(CcKindV1::BlockSkill, REFORM_SILENCE));
            }
        }

        // 3. Check R「万蛾」cast -> 3.5s untargetable Moth Storm!
        if consume_buff(sim, entity, R_STORM_ASK) {
            self.storm_end = Some((tick + STORM_TICKS, tick + STORM_PERIOD));
            let mut sb = BuffV1::timed(STORM_BUFF, STORM_TICKS);
            sb.damaged_reduce = 100;
            sb.cc_immune = true;
            sb.move_speed_mult = 30;
            sb.ignore_wall = true;
            sim.add_buff(entity, &sb);
            sim.play_view_effect("abysspact_noctua_disperse", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_sfx("abysspact_noctua_storm_start", entity, &InputTargetV1::target(entity));
        }

        // 4. Maintain R「万蛾」storm pulses -> end dust-shock 1.25s AoE silence + own 1.25s reform!
        if let Some((end_t, mut next_p)) = self.storm_end {
            if tick >= end_t {
                self.storm_end = None;
                sim.entity_remove_buff(entity, STORM_BUFF);
                sim.play_view_effect("abysspact_noctua_reform", entity, &InputTargetV1::target(entity), 0, 0, 0);
                sim.play_view_effect("abysspact_noctua_dust_shock", entity, &InputTargetV1::pos(my_pos.0, my_pos.1), 0, 0, 0);
                sim.play_sfx("abysspact_noctua_dust_shock", entity, &InputTargetV1::pos(my_pos.0, my_pos.1));
                let r2 = SHOCK_RADIUS * SHOCK_RADIUS;
                let mut foes = Vec::new();
                for i in 0..sim.entity_count() {
                    let Some(e) = sim.entity_at(i) else { continue };
                    if e.is_alive() && e.team() != my_team && !e.is_tower() && dist_sq(my_pos, e.pos()) <= r2 {
                        foes.push(e.id());
                    }
                }
                for fid in foes {
                    sim.apply_cc(fid, &CcV1::of_kind(CcKindV1::BlockSkill, REFORM_SILENCE));
                }
                sim.apply_cc(entity, &CcV1::of_kind(CcKindV1::BlockSkill, REFORM_SILENCE));
            } else {
                if tick >= next_p {
                    next_p = tick + STORM_PERIOD;
                    let r2 = STORM_RADIUS * STORM_RADIUS;
                    let dmg = storm_tick_damage(ap);
                    let mut foes = Vec::new();
                    for i in 0..sim.entity_count() {
                        let Some(e) = sim.entity_at(i) else { continue };
                        if e.is_alive() && e.team() != my_team && !e.is_tower() && dist_sq(my_pos, e.pos()) <= r2 {
                            foes.push(e.id());
                        }
                    }
                    for fid in foes {
                        sim.deal_damage_typed(entity, fid, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                        self.add_scale(sim, fid, tick);
                    }
                }
                self.storm_end = Some((end_t, next_p));
            }
        }

        // 5. Passive「散身」: >12% max HP damage in 1.0s -> scatter 0.6s & retreat 2.5万!
        let lost = self.last_hp.saturating_sub(cur_hp);
        self.last_hp = cur_hp;
        if lost > 0 {
            self.dmg_win.push_back((tick, lost));
        }
        while self.dmg_win.front().is_some_and(|&(t, _)| tick.saturating_sub(t) > BURST_WINDOW) {
            self.dmg_win.pop_front();
        }
        let sum_lost: usize = self.dmg_win.iter().map(|&(_, d)| d).sum();
        let threshold = max_hp.saturating_mul(BURST_PCT) / 100;
        if self.reform_at.is_none()
            && self.storm_end.is_none()
            && tick >= self.scatter_ready_at
            && threshold > 0
            && sum_lost >= threshold
        {
            self.dmg_win.clear();
            self.scatter_ready_at = tick + SCATTER_CD;
            self.reform_at = Some(tick + SCATTER_TICKS);
            let mut d = BuffV1::timed(DISPERSE_BUFF, SCATTER_TICKS);
            d.damaged_reduce = 100;
            d.cc_immune = true;
            sim.add_buff(entity, &d);
            sim.play_view_effect("abysspact_noctua_disperse", entity, &InputTargetV1::pos(my_pos.0, my_pos.1), 0, 0, 0);
            sim.play_sfx("abysspact_noctua_disperse", entity, &InputTargetV1::pos(my_pos.0, my_pos.1));
            let dest = Self::retreat_pos(sim, my_team, my_pos);
            sim.entity_set_pos(entity, dest.0, dest.1);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_noctua:scatter", NoctuaPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn storm_tick_and_scales_buffs_match_spec() {
        assert_eq!(storm_tick_damage(100), 35);
        assert_eq!(storm_tick_damage(250), 50);
        assert_eq!(scale_buff_name(0), None);
        assert_eq!(scale_buff_name(3), Some("abysspact_noctua_scales_3"));
    }
}
