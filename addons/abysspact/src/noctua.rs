//! 千蛾 (`abysspact_noctua`) · 蛾身少女 · 中路法师
//!
//! - 被动「散身」：1 秒内掉血超过最大生命的 `p_pct`%（`p_cd` 冷却）时碎成蛾群：先放逐自己 `p_t` tick
//!   （谁也选不中，这段时间她自己也放不了技能、打不了人），放逐结束那一刻才在背离最近敌方英雄 `p_dist`
//!   远的地方聚回来，代价「聚身」：再禁技能 `p_reform` tick（普攻可以）。落点夹在地图里（`map_box`）。
//! - 鳞粉：Q 的飞蛾和 R 的风暴每打中一次加一层，最多 3 层，每层减速 `scale_slow`%，持续 `scale_t`。
//! - R「万蛾」：施法动作碎完（数据里 `r_go`）以后整个人化成风暴 `r_t` tick：放逐自己（选不中、不能普攻放技能），
//!   每 tick 往 `r_seek` 内敌方英雄的中心挪（没有就去最近的敌方英雄），速度是她的移速（风暴另加 30%），
//!   每 `r_p` tick 对 `r_r` 内的敌人造成 `r_tick_dmg + r_tick_ap% 法强` 魔法伤害并加一层鳞粉；
//!   结束时原地聚身，`r_shock` 内的敌人沉默 `r_sil`，她自己也禁技能 `r_sil`。
//!   人被放逐时身上的东西看不见，所以风暴的画面每 20 tick 在她的位置补一朵。
//!
//! 数字都从技能数据的 `passive.params` 来（生成脚本照参数表 PARAMS["noctua"] 写进去），这里的默认值和参数表一样。

use std::collections::{HashMap, VecDeque};
use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff, kit_param, map_box, onto_map};

pub const HERO: &str = "abysspact_noctua";
pub const NATIVE_MARK: &str = "abysspact_noctua_native";
pub const SCALE_ASK: &str = "abysspact_noctua_scale_ask";
pub const Q_LIVE: &str = "abysspact_noctua_q_live";
pub const DISPERSE_BUFF: &str = "abysspact_noctua_disperse";
pub const STORM_BUFF: &str = "abysspact_noctua_storm";
pub const R_STORM_ASK: &str = "abysspact_noctua_r_storm";
pub const R_CAST_VOICE: &str = "abysspact_noctua_r_voice";
pub const STORM_CLOUD: &str = "abysspact_noctua_storm_cloud";

/// 统计掉血的窗口（1 秒）。
pub const BURST_WINDOW: usize = 60;
/// 风暴画面多久补一朵。
pub const CLOUD_EVERY: usize = 20;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub p_pct: usize,
    pub p_cd: usize,
    pub p_t: usize,
    pub p_dist: usize,
    pub p_reform: usize,
    pub scale_slow: usize,
    pub scale_t: usize,
    pub r_t: usize,
    pub r_p: usize,
    pub r_r: usize,
    pub r_tick_dmg: usize,
    pub r_tick_ap: usize,
    pub r_sil: usize,
    pub r_shock: usize,
    pub r_seek: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_pct: 12, p_cd: 720, p_t: 36, p_dist: 25_000, p_reform: 75,
            scale_slow: 10, scale_t: 240,
            r_t: 210, r_p: 30, r_r: 28_000, r_tick_dmg: 39, r_tick_ap: 16, r_sil: 75, r_shock: 32_000, r_seek: 70_000,
        }
    }
}

impl Params {
    pub fn parse(json: &str) -> Self {
        let d = Self::default();
        let g = |k: &str, v: usize| kit_param(json, k).unwrap_or(v);
        Self {
            p_pct: g("p_pct", d.p_pct), p_cd: g("p_cd", d.p_cd), p_t: g("p_t", d.p_t), p_dist: g("p_dist", d.p_dist),
            p_reform: g("p_reform", d.p_reform), scale_slow: g("scale_slow", d.scale_slow), scale_t: g("scale_t", d.scale_t),
            r_t: g("r_t", d.r_t), r_p: g("r_p", d.r_p), r_r: g("r_r", d.r_r), r_tick_dmg: g("r_tick_dmg", d.r_tick_dmg),
            r_tick_ap: g("r_tick_ap", d.r_tick_ap), r_sil: g("r_sil", d.r_sil), r_shock: g("r_shock", d.r_shock),
            r_seek: g("r_seek", d.r_seek),
        }
    }
}

pub fn storm_tick_damage(p: &Params, ap: usize) -> usize {
    p.r_tick_dmg + ap.saturating_mul(p.r_tick_ap) / 100
}

pub fn scale_buff_name(k: u8) -> Option<&'static str> {
    match k {
        1 => Some("abysspact_noctua_scales_1"),
        2 => Some("abysspact_noctua_scales_2"),
        3 => Some("abysspact_noctua_scales_3"),
        _ => None,
    }
}

/// 从 `from` 朝 `to` 走 `step`，不走过头。
pub fn step_toward(from: (u64, u64), to: (f64, f64), step: f64) -> (f64, f64) {
    let (fx, fy) = (from.0 as f64, from.1 as f64);
    let (dx, dy) = (to.0 - fx, to.1 - fy);
    let d = dx.hypot(dy);
    if d <= step || d < 1.0 {
        to
    } else {
        (fx + dx / d * step, fy + dy / d * step)
    }
}

/// 背离 `foe` 走 `dist` 的落点（没有敌人就原地）。
pub fn away_from(me: (u64, u64), foe: Option<(u64, u64)>, dist: f64) -> (f64, f64) {
    let (mx, my) = (me.0 as f64, me.1 as f64);
    let Some(f) = foe else { return (mx, my) };
    let (dx, dy) = (mx - f.0 as f64, my - f.1 as f64);
    let len = dx.hypot(dy);
    if len < 1.0 {
        return (mx - dist, my);
    }
    (mx + dx / len * dist, my + dy / len * dist)
}

#[derive(Clone, Copy)]
struct Storm {
    end: usize,
    next_pulse: usize,
    next_cloud: usize,
}

#[derive(Clone, Default)]
struct NoctuaPassive {
    p: Params,
    voice: Voice,
    last_hp: usize,
    dmg_win: VecDeque<(usize, usize)>,
    scatter_ready_at: usize,
    /// 散开中：到这一 tick 聚身。
    reform_at: Option<usize>,
    storm: Option<Storm>,
    scales: HashMap<usize, (u8, usize)>,
}

impl NoctuaPassive {
    fn sync_scales(&self, sim: &mut StableSim<'_>, eid: usize, stacks: u8) {
        for k in 1..=3 {
            if let Some(n) = scale_buff_name(k) {
                sim.entity_remove_buff(eid, n);
            }
        }
        if let Some(n) = scale_buff_name(stacks) {
            let mut b = BuffV1::timed(n, self.p.scale_t.max(1));
            b.move_speed_mult = -(self.p.scale_slow as i32) * (stacks as i32);
            sim.add_buff(eid, &b);
        }
    }

    fn add_scale(&mut self, sim: &mut StableSim<'_>, eid: usize, tick: usize) {
        let cur = self.scales.get(&eid).map(|&(c, exp)| if exp > tick { c } else { 0 }).unwrap_or(0);
        let next = (cur + 1).min(3);
        self.scales.insert(eid, (next, tick + self.p.scale_t));
        self.sync_scales(sim, eid, next);
    }

    /// 最近的敌方英雄的位置。
    fn nearest_foe(sim: &StableSim<'_>, team: usize, at: (u64, u64)) -> Option<(u64, u64)> {
        let mut best: Option<((u64, u64), u64)> = None;
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_champion() && e.is_alive() && e.team() != team {
                let d2 = dist_sq(at, e.pos());
                if best.is_none_or(|(_, b)| d2 < b) {
                    best = Some((e.pos(), d2));
                }
            }
        }
        best.map(|(p, _)| p)
    }

    /// 风暴往哪儿去：`r_seek` 内敌方英雄的中心，没有就最近的敌方英雄。
    fn storm_goal(&self, sim: &StableSim<'_>, team: usize, at: (u64, u64)) -> Option<(f64, f64)> {
        let seek2 = (self.p.r_seek as u64).saturating_mul(self.p.r_seek as u64);
        let (mut sx, mut sy, mut n) = (0.0, 0.0, 0.0);
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_champion() && e.is_alive() && e.team() != team && dist_sq(at, e.pos()) <= seek2 {
                sx += e.pos().0 as f64;
                sy += e.pos().1 as f64;
                n += 1.0;
            }
        }
        if n > 0.0 {
            return Some((sx / n, sy / n));
        }
        Self::nearest_foe(sim, team, at).map(|p| (p.0 as f64, p.1 as f64))
    }

    fn foes_within(sim: &StableSim<'_>, team: usize, at: (u64, u64), r: usize) -> Vec<usize> {
        let r2 = (r as u64).saturating_mul(r as u64);
        (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| e.is_alive() && e.team() != team && !e.is_tower() && dist_sq(at, e.pos()) <= r2)
            .map(|e| e.id())
            .collect()
    }

    fn start_storm(&mut self, sim: &mut StableSim<'_>, me: usize, at: (u64, u64), tick: usize) {
        let p = self.p;
        // 先放逐再挂免控：免控的人可能放逐不上
        sim.entity_banish(me, me, p.r_t, "", "");
        let mut sb = BuffV1::timed(STORM_BUFF, p.r_t);
        sb.damaged_reduce = 100;
        sb.cc_immune = true;
        sb.move_speed_mult = 30;
        sb.ignore_wall = true;
        sim.add_buff(me, &sb);
        self.storm = Some(Storm { end: tick + p.r_t, next_pulse: tick + p.r_p.max(1), next_cloud: tick });
        // 散身的事和风暴不叠
        self.reform_at = None;
        sim.entity_remove_buff(me, DISPERSE_BUFF);
        let here = InputTargetV1::pos(at.0, at.1);
        sim.play_view_effect("abysspact_noctua_disperse", me, &here, 0, 0, 0);
        sim.play_sfx("abysspact_noctua_storm_start", me, &here);
    }

    fn run_storm(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, at: (u64, u64), ap: usize, speed: usize, tick: usize) {
        let Some(mut st) = self.storm else { return };
        let p = self.p;
        if tick >= st.end {
            self.storm = None;
            sim.entity_remove_buff(me, STORM_BUFF);
            let here = InputTargetV1::pos(at.0, at.1);
            sim.play_view_effect("abysspact_noctua_reform", me, &InputTargetV1::target(me), 0, 0, 0);
            sim.play_view_effect("abysspact_noctua_dust_shock", me, &here, 0, 0, 0);
            sim.play_sfx("abysspact_noctua_dust_shock", me, &here);
            for fid in Self::foes_within(sim, team, at, p.r_shock) {
                sim.apply_cc(fid, &CcV1::of_kind(CcKindV1::BlockSkill, p.r_sil as u64));
            }
            sim.apply_cc(me, &CcV1::of_kind(CcKindV1::BlockSkill, p.r_sil as u64));
            return;
        }
        // 往敌人堆里扫
        let mut now = at;
        if let Some(goal) = self.storm_goal(sim, team, at) {
            let next = step_toward(at, goal, speed.max(1) as f64);
            now = onto_map(map_box(sim), next.0, next.1);
            if now != at {
                sim.entity_set_pos(me, now.0, now.1);
            }
        }
        if tick >= st.next_cloud {
            st.next_cloud = tick + CLOUD_EVERY;
            sim.play_view_effect(STORM_CLOUD, me, &InputTargetV1::pos(now.0, now.1), 0, 0, 0);
        }
        if tick >= st.next_pulse {
            st.next_pulse = tick + p.r_p.max(1);
            let dmg = storm_tick_damage(&p, ap);
            for fid in Self::foes_within(sim, team, now, p.r_r) {
                sim.deal_damage_typed(me, fid, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                self.add_scale(sim, fid, tick);
            }
        }
        self.storm = Some(st);
    }
}

impl StablePassive for NoctuaPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = Params::parse(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.last_hp = sim.get_entity(entity).map(|e| e.hp().0).unwrap_or(0);
        self.dmg_win.clear();
        self.scatter_ready_at = 0;
        self.reform_at = None;
        self.storm = None;
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
        self.storm = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, cur_hp, max_hp, stat)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.hp().0, e.hp().1, e.stat()))
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

        // 1. Q 的飞蛾在路上时才去找打中的人（数据给她挂 q_live）
        if has_buff(sim, entity, Q_LIVE) {
            let hits: Vec<usize> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|e| e.is_alive() && e.team() != my_team && e.is_champion())
                .map(|e| e.id())
                .collect();
            for eid in hits {
                if consume_buff(sim, eid, SCALE_ASK) {
                    self.add_scale(sim, eid, tick);
                }
            }
        }

        // 2. 散开到点：聚身，背离最近的敌方英雄，落点夹在地图里
        if let Some(at) = self.reform_at {
            if tick >= at {
                self.reform_at = None;
                sim.entity_remove_buff(entity, DISPERSE_BUFF);
                let foe = Self::nearest_foe(sim, my_team, my_pos);
                let goal = away_from(my_pos, foe, self.p.p_dist as f64);
                let dest = onto_map(map_box(sim), goal.0, goal.1);
                sim.entity_set_pos(entity, dest.0, dest.1);
                let there = InputTargetV1::pos(dest.0, dest.1);
                sim.play_view_effect("abysspact_noctua_reform", entity, &there, 0, 0, 0);
                sim.play_sfx("abysspact_noctua_reform", entity, &there);
                sim.apply_cc(entity, &CcV1::of_kind(CcKindV1::BlockSkill, self.p.p_reform as u64));
            }
        }

        // 3. R：化成风暴
        if consume_buff(sim, entity, R_STORM_ASK) && self.storm.is_none() {
            self.start_storm(sim, entity, my_pos, tick);
        }
        if self.storm.is_some() {
            self.run_storm(sim, entity, my_team, my_pos, stat.magic_power, stat.move_speed, tick);
        }

        // 4. 被动散身：1 秒内掉血超过门槛
        let lost = self.last_hp.saturating_sub(cur_hp);
        self.last_hp = cur_hp;
        if lost > 0 {
            self.dmg_win.push_back((tick, lost));
        }
        while self.dmg_win.front().is_some_and(|&(t, _)| tick.saturating_sub(t) > BURST_WINDOW) {
            self.dmg_win.pop_front();
        }
        let sum_lost: usize = self.dmg_win.iter().map(|&(_, d)| d).sum();
        let threshold = max_hp.saturating_mul(self.p.p_pct) / 100;
        if self.reform_at.is_none()
            && self.storm.is_none()
            && tick >= self.scatter_ready_at
            && threshold > 0
            && sum_lost >= threshold
        {
            self.dmg_win.clear();
            self.scatter_ready_at = tick + self.p.p_cd;
            self.reform_at = Some(tick + self.p.p_t);
            sim.entity_banish(entity, entity, self.p.p_t, "", "");
            let mut d = BuffV1::timed(DISPERSE_BUFF, self.p.p_t);
            d.damaged_reduce = 100;
            d.cc_immune = true;
            sim.add_buff(entity, &d);
            let here = InputTargetV1::pos(my_pos.0, my_pos.1);
            sim.play_view_effect("abysspact_noctua_disperse", entity, &here, 0, 0, 0);
            sim.play_sfx("abysspact_noctua_disperse", entity, &here);
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
    fn storm_tick_and_scales_buffs_match_the_kit() {
        let p = Params::default();
        assert_eq!(storm_tick_damage(&p, 100), 39 + 16);
        assert_eq!(scale_buff_name(0), None);
        assert_eq!(scale_buff_name(3), Some("abysspact_noctua_scales_3"));
    }

    #[test]
    fn params_come_from_the_kit_file() {
        // 生成好的技能数据里写着参数表的数，和这里的默认值一样
        assert_eq!(Params::parse(&crate::kit_params_of(include_str!(
            "../../../abysspact/champion/abysspact_noctua.data_champion"
        ))), Params::default());
    }

    #[test]
    fn the_storm_steps_without_overshooting_and_scatter_runs_away() {
        assert_eq!(step_toward((0, 0), (300.0, 400.0), 1000.0), (300.0, 400.0));
        let (x, y) = step_toward((0, 0), (3000.0, 4000.0), 500.0);
        assert!((x - 300.0).abs() < 1e-6 && (y - 400.0).abs() < 1e-6);
        assert_eq!(away_from((100_000, 100_000), Some((90_000, 100_000)), 25_000.0), (125_000.0, 100_000.0));
        assert_eq!(away_from((100_000, 100_000), None, 25_000.0), (100_000.0, 100_000.0));
    }
}
