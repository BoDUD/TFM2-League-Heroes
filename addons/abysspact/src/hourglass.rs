//! 返照 (`abysspact_hourglass`) · 沙漏女巫 · 辅助
//!
//! - 被动记下全队每个活着的友方英雄最近 3 秒（`rewind_t`）的位置和血量，每 6 tick 一笔。
//! - Q「回光」、R「倒流」都不再冷却一好就放：数据里这两格在原生模式下是 3 tick 的 idle 动作，只挂一个待命
//!   标记（Q 待命 `q_arm`，R 待命 `r_arm`）。待命期间被动每 tick 看：
//!   * R：`r_range` 内友方英雄 3 秒内掉的血（按各自最大生命的 %）加起来到 `r_trig` 才倒流；
//!   * Q：`q_range` 内 3 秒内掉血最多的那个队友（含她自己），掉到 `q_trig`% 才给他打回光印记；
//!   出手时被动自己播施法动作（`animate`）、音效，动作播到 `q_go` / `r_go` tick 时生效。待命到点没用上，
//!   就把那一格的冷却退到只剩 `keep`。被控、正在放别的动作时不出手。
//! - 回光印记：3 秒后把血倒回打印记那一刻（只往回倒，不会变少）；期间要被打死（`undying` 卡在 1 血）就立刻倒回，
//!   每个印记只救一次。她自己死了：快死的那个当场倒回，其余的印记摘掉（不能留着白给的不死）。
//! - R：`r_range` 内活着的友方英雄（含她自己）回到 3 秒前的位置和血量（只往回倒），这 3 秒里死掉的不回来。
//! - 代价「老去」：Q 一次老 1 层，R 一次老 3 层，最多 10 层，每层最大生命 -2.5%、移速 -2%；0–3 层黑发，
//!   4–7 层灰白（`hair_grey`），8–10 层全白（`hair_white`）。死了就退回年轻（复活时 0 层）。

use std::collections::{HashMap, VecDeque};
use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{animate, can_cast, consume_buff, dist_sq, has_buff, kit_param, refund_cooldown};

pub const HERO: &str = "abysspact_hourglass";
pub const NATIVE_MARK: &str = "abysspact_hourglass_native";
pub const AGE_BUFF: &str = "abysspact_hourglass_age";
pub const HAIR_GREY: &str = "abysspact_hourglass_hair_grey";
pub const HAIR_WHITE: &str = "abysspact_hourglass_hair_white";
pub const Q_ARM: &str = "abysspact_hourglass_q_arm";
pub const R_ARM: &str = "abysspact_hourglass_r_arm";
pub const CLOCK_BUFF: &str = "abysspact_hourglass_clock";

pub const AGE_CAP: u8 = 10;
pub const SNAP_INTERVAL: usize = 6; // 0.1 秒一笔

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub rewind_t: usize,
    pub q_trig: usize,
    pub q_arm: usize,
    pub q_range: usize,
    pub q_go: usize,
    pub q_dur: usize,
    pub r_trig: usize,
    pub r_arm: usize,
    pub r_range: usize,
    pub r_go: usize,
    pub r_dur: usize,
    pub keep: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            rewind_t: 180, q_trig: 15, q_arm: 300, q_range: 70_000, q_go: 13, q_dur: 36,
            r_trig: 60, r_arm: 900, r_range: 100_000, r_go: 16, r_dur: 44, keep: 60,
        }
    }
}

impl Params {
    pub fn parse(json: &str) -> Self {
        let d = Self::default();
        let g = |k: &str, v: usize| kit_param(json, k).unwrap_or(v);
        Self {
            rewind_t: g("rewind_t", d.rewind_t), q_trig: g("q_trig", d.q_trig), q_arm: g("q_arm", d.q_arm),
            q_range: g("q_range", d.q_range), q_go: g("q_go", d.q_go), q_dur: g("q_dur", d.q_dur),
            r_trig: g("r_trig", d.r_trig), r_arm: g("r_arm", d.r_arm), r_range: g("r_range", d.r_range),
            r_go: g("r_go", d.r_go), r_dur: g("r_dur", d.r_dur), keep: g("keep", d.keep),
        }
    }
}

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

/// 3 秒内掉了最大生命的百分之几（回了血就是 0）。
pub fn loss_pct(old_hp: usize, now_hp: usize, max_hp: usize) -> usize {
    if max_hp == 0 {
        return 0;
    }
    old_hp.saturating_sub(now_hp).saturating_mul(100) / max_hp
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

#[derive(Clone, Copy)]
enum Cast {
    Mark(usize),
    Rewind,
}

#[derive(Clone, Default)]
struct HourglassPassive {
    p: Params,
    voice: Voice,
    age: u8,
    history: HashMap<usize, VecDeque<Snap>>,
    marks: HashMap<usize, ActiveMark>,
    q_armed: Option<usize>,
    r_armed: Option<usize>,
    /// 已经开始播动作，到这一 tick 生效。
    pending: Option<(Cast, usize)>,
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
        let Some((alive, cur_hp, max_hp)) = sim.get_entity(ally_id).map(|e| (e.is_alive(), e.hp().0, e.hp().1)) else {
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

    /// (队友, 位置, 3 秒内掉了百分之几)：每个活着、离她 `range` 内、有历史的友方英雄。
    fn losses(&self, sim: &StableSim<'_>, team: usize, at: (u64, u64), range: usize) -> Vec<(usize, usize)> {
        let r2 = (range as u64).saturating_mul(range as u64);
        let mut out = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || !e.is_alive() || e.team() != team || dist_sq(at, e.pos()) > r2 {
                continue;
            }
            let (now, max) = e.hp();
            let old = self.history.get(&e.id()).and_then(|q| q.front()).map_or(now, |s| s.hp);
            out.push((e.id(), loss_pct(old, now, max)));
        }
        out
    }

    fn place_mark(&mut self, sim: &mut StableSim<'_>, me: usize, aid: usize, tick: usize) {
        let Some(hp) = sim.get_entity(aid).filter(|e| e.is_alive()).map(|e| e.hp().0) else { return };
        self.marks.insert(aid, ActiveMark { saved_hp: hp, end_tick: tick + self.p.rewind_t });
        sim.entity_remove_buff(aid, CLOCK_BUFF);
        let mut clk = BuffV1::timed(CLOCK_BUFF, self.p.rewind_t);
        clk.undying = true;
        sim.add_buff(aid, &clk);
        sim.play_view_effect("abysspact_hourglass_sand_rise", me, &InputTargetV1::target(me), 0, 0, 0);
        sim.play_sfx("abysspact_hourglass_q_mark", me, &InputTargetV1::target(aid));
        self.add_age(sim, me, 1);
    }

    fn rewind_all(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, at: (u64, u64)) {
        self.add_age(sim, me, 3);
        sim.play_view_effect("abysspact_hourglass_hourglass", me, &InputTargetV1::target(me), 0, 0, 0);
        sim.play_sfx("abysspact_hourglass_flip", me, &InputTargetV1::target(me));
        let r2 = (self.p.r_range as u64).saturating_mul(self.p.r_range as u64);
        let allies: Vec<(usize, (u64, u64), usize)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| e.is_champion() && e.is_alive() && e.team() == team && dist_sq(at, e.pos()) <= r2)
            .map(|e| (e.id(), e.pos(), e.hp().0))
            .collect();
        for (aid, cur_pos, cur_hp) in allies {
            let snap = self.history.get(&aid).and_then(|q| q.front().copied());
            let (dest_pos, old_hp) = snap.map(|s| (s.pos, s.hp)).unwrap_or((cur_pos, cur_hp));
            sim.play_view_effect("abysspact_hourglass_echo", me, &InputTargetV1::pos(cur_pos.0, cur_pos.1), 0, 0, 0);
            sim.entity_set_pos(aid, dest_pos.0, dest_pos.1);
            Self::rewind_ally_hp(sim, me, aid, old_hp);
            sim.play_view_effect("abysspact_hourglass_sand_burst", me, &InputTargetV1::pos(dest_pos.0, dest_pos.1), 0, 0, 0);
        }
    }
}

impl StablePassive for HourglassPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = Params::parse(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.age = 0;
        self.marks.clear();
        self.q_armed = None;
        self.r_armed = None;
        self.pending = None;
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
        // 她死了以后被动不跑：印记这会儿就要了结。快死的（被不死卡在 1、2 血）当场倒回，其余摘掉印记，
        // 不能留着她死后还管用的不死。
        let marks: Vec<(usize, ActiveMark)> = self.marks.drain().collect();
        for (aid, mk) in marks {
            let low = sim.get_entity(aid).is_some_and(|e| e.is_alive() && e.hp().0 <= 2);
            sim.entity_remove_buff(aid, CLOCK_BUFF);
            if low {
                let Some(hp) = sim.get_entity(aid).map(|e| e.hp().1) else { continue };
                sim.entity_set_hp(aid, mk.saved_hp.min(hp).max(1));
            }
        }
        // 深渊把押上的年岁退回来
        self.age = 0;
        self.q_armed = None;
        self.r_armed = None;
        self.pending = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.team(), e.pos())) else {
            return;
        };
        let tick = sim.tick();

        // 1. 每 0.1 秒记一笔全队的位置和血量（只留 3 秒多一点）
        if tick % SNAP_INTERVAL == 0 {
            let keep = self.p.rewind_t + 12;
            let cap = keep / SNAP_INTERVAL + 2;
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_champion() || e.team() != my_team {
                    continue;
                }
                let eid = e.id();
                if e.is_alive() {
                    let q = self.history.entry(eid).or_default();
                    q.push_back(Snap { tick, pos: e.pos(), hp: e.hp().0 });
                    while q.len() > cap || q.front().is_some_and(|s| tick.saturating_sub(s.tick) > keep) {
                        q.pop_front();
                    }
                } else {
                    self.history.remove(&eid);
                }
            }
        }

        // 2. 回光印记：被打到要死（不死卡着）立刻倒回；3 秒到点倒回
        let mut finished = Vec::new();
        for (&aid, &mk) in &self.marks {
            match sim.get_entity(aid).map(|e| (e.is_alive(), e.hp().0)) {
                Some((true, cur_hp)) if cur_hp <= 2 || tick >= mk.end_tick => finished.push((aid, mk.saved_hp, true)),
                Some((false, _)) | None => finished.push((aid, mk.saved_hp, false)),
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

        // 3. AI 按了 Q / R：待命
        if consume_buff(sim, entity, Q_ARM) {
            self.q_armed = Some(tick + self.p.q_arm);
        }
        if consume_buff(sim, entity, R_ARM) {
            self.r_armed = Some(tick + self.p.r_arm);
        }

        // 4. 动作播到出手那一帧
        if let Some((cast, at)) = self.pending {
            if tick >= at {
                self.pending = None;
                match cast {
                    Cast::Mark(aid) => self.place_mark(sim, entity, aid, tick),
                    Cast::Rewind => self.rewind_all(sim, entity, my_team, my_pos),
                }
            }
        }

        // 5. 待命中：看有没有人需要（每 3 tick 看一次就够，血量历史 6 tick 才记一笔）
        if tick % 3 == 0
            && self.pending.is_none()
            && (self.q_armed.is_some() || self.r_armed.is_some())
            && can_cast(sim, entity)
        {
            let p = self.p;
            if self.r_armed.is_some() {
                let total: usize = self.losses(sim, my_team, my_pos, p.r_range).iter().map(|&(_, l)| l).sum();
                if total >= p.r_trig {
                    self.r_armed = None;
                    self.pending = Some((Cast::Rewind, tick + p.r_go));
                    animate(sim, entity, "ult", p.r_dur);
                    sim.play_sfx("abysspact_hourglass_foley_r", entity, &InputTargetV1::target(entity));
                    self.voice.play(sim, HERO, entity, Cue::Ult);
                }
            }
            if self.pending.is_none() && self.q_armed.is_some() {
                let worst = self.losses(sim, my_team, my_pos, p.q_range).into_iter().max_by_key(|&(_, l)| l);
                if let Some((aid, _)) = worst.filter(|&(_, l)| l >= p.q_trig) {
                    self.q_armed = None;
                    self.pending = Some((Cast::Mark(aid), tick + p.q_go));
                    animate(sim, entity, "skill", p.q_dur);
                    sim.play_sfx("abysspact_hourglass_foley_q", entity, &InputTargetV1::target(entity));
                }
            }
        }

        // 6. 待命到点没用上：退冷却
        if self.q_armed.is_some_and(|t| tick >= t) {
            self.q_armed = None;
            refund_cooldown(sim, entity, SkillSlotV1::Skill, self.p.keep);
        }
        if self.r_armed.is_some_and(|t| tick >= t) {
            self.r_armed = None;
            refund_cooldown(sim, entity, SkillSlotV1::Ult, self.p.keep);
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

    #[test]
    fn only_real_losses_count() {
        assert_eq!(loss_pct(1000, 800, 1000), 20);
        // 回了血不算掉
        assert_eq!(loss_pct(800, 1000, 1000), 0);
        assert_eq!(loss_pct(500, 100, 0), 0);
    }

    #[test]
    fn params_come_from_the_kit_file() {
        assert_eq!(Params::parse(&crate::kit_params_of(include_str!(
            "../../../abysspact/champion/abysspact_hourglass.data_champion"
        ))), Params::default());
    }
}
