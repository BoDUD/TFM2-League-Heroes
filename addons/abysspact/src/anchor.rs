//! 沉锚 (`abysspact_anchor`) · 深渊锚炮手 · 下路射手
//!
//! 拖锚（平时）射程 6 万、移速 +10%；下锚是一座炮台：射程 9 万（`StableEffectType::range_adjust`，+3 万）、
//! 攻速 -20%、走不了，每发炮弹在命中的人身边 `a_splash_r` 内溅 `a_splash`% 攻击力。
//!
//! - 下锚 / 起锚只有一个决定（`want`）：9 万（`engage`）内有敌方英雄、最近的敌方英雄在 `safe` 外就下锚；
//!   敌方英雄摸到 `danger` 内，或者 9 万内 `no_target` tick 没有任何能打的东西就起锚。小兵野怪不算「贴脸」。
//!   被动每 10 tick 判断一次（两次切换至少隔 `toggle_cd`）；AI 按 W 只是让它马上判断一次，不该切就把 W 的冷却
//!   退到只剩 `w_keep`。数据里的 W 在原生模式下是一个 3 tick 的 idle 动作，只挂一个标记。
//! - 下锚要 `w_plant` tick（播 `skill2`：锚砸进地里），起锚要 `w_raise` tick（播 `anchor_raise`），这段时间
//!   不能打也不能走——被人贴脸时要么硬扛，要么先花 0.6 秒拔锚。大招会先下锚（不另播动作，大招动作盖着）。
//! - 被动「压舱」：锚在地上时（含下锚、起锚的那几下），击飞和强制位移（击退、拉、拽）直接去掉，眩晕、沉默这些
//!   照吃（清掉全部控制再把其余的按剩下的时间挂回去，league_lillia 的写法），位置钉死。
//! - 溅射只来自她自己的炮弹：数据里炮弹命中时调本包的 `abysspact_anchor:splash`，不再走 `on_attack`
//!   （`on_attack` 连技能、别人借她名义打的伤害都会触发）。
//!
//! 数字从技能数据的 `passive.params` 来（参数表 PARAMS["anchor"]）。

use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{animate, consume_buff, dist_sq, has_buff, kit_param, refund_cooldown};

pub const HERO: &str = "abysspact_anchor";
pub const NATIVE_MARK: &str = "abysspact_anchor_native";
pub const DRAG_BUFF: &str = "abysspact_anchor_drag";
pub const SIEGE_BUFF: &str = "abysspact_anchor_siege";
pub const TOGGLE_ASK: &str = "abysspact_anchor_toggle";
pub const R_SIEGE_ASK: &str = "abysspact_anchor_r_siege";
pub const R_CAST_VOICE: &str = "abysspact_anchor_r_voice";

pub const SIEGE_BONUS_RANGE: u64 = 30_000; // 6万 -> 9万
pub const CHECK_EVERY: usize = 10;

/// 炮弹溅射的比例和半径。溅射是一个效果对象，建在 configure 之前，所以数放在这里，由被动的 configure
/// 写进来（每个沉锚读的是同一份技能数据）。
static SPLASH_PCT: AtomicUsize = AtomicUsize::new(60);
static SPLASH_R: AtomicUsize = AtomicUsize::new(15_000);

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub a_splash: usize,
    pub a_splash_r: usize,
    pub w_plant: usize,
    pub w_raise: usize,
    pub w_keep: usize,
    pub engage: usize,
    pub safe: usize,
    pub danger: usize,
    pub no_target: usize,
    pub toggle_cd: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            a_splash: 60, a_splash_r: 15_000, w_plant: 30, w_raise: 36, w_keep: 300,
            engage: 90_000, safe: 35_000, danger: 30_000, no_target: 120, toggle_cd: 120,
        }
    }
}

impl Params {
    pub fn parse(json: &str) -> Self {
        let d = Self::default();
        let g = |k: &str, v: usize| kit_param(json, k).unwrap_or(v);
        Self {
            a_splash: g("a_splash", d.a_splash), a_splash_r: g("a_splash_r", d.a_splash_r), w_plant: g("w_plant", d.w_plant),
            w_raise: g("w_raise", d.w_raise), w_keep: g("w_keep", d.w_keep), engage: g("engage", d.engage),
            safe: g("safe", d.safe), danger: g("danger", d.danger), no_target: g("no_target", d.no_target),
            toggle_cd: g("toggle_cd", d.toggle_cd),
        }
    }
}

pub fn splash_damage(ad: usize, pct: usize) -> usize {
    ad.saturating_mul(pct) / 100
}

/// 下锚 / 起锚的决定：`Some(true)` 该下锚，`Some(false)` 该起锚，`None` 不动。
/// `nearest_champ`：最近的敌方英雄的距离平方；`champ_in_engage`：9 万内有没有敌方英雄；`idle`：多久没东西可打。
pub fn want(p: &Params, siege: bool, nearest_champ: u64, champ_in_engage: bool, idle: usize) -> Option<bool> {
    let sq = |v: usize| (v as u64).saturating_mul(v as u64);
    if !siege {
        (champ_in_engage && nearest_champ > sq(p.safe)).then_some(true)
    } else {
        (nearest_champ <= sq(p.danger) || idle >= p.no_target).then_some(false)
    }
}

#[derive(Clone, Default)]
struct AnchorPassive {
    p: Params,
    voice: Voice,
    /// 锚在地上（正在下锚、正在起锚也算）。
    siege: bool,
    pinned: Option<(u64, u64)>,
    /// 正在起锚：到这一 tick 才拔出来。
    raise_done: Option<usize>,
    next_toggle_at: usize,
    last_seen_target: usize,
}

impl AnchorPassive {
    fn plant(&mut self, sim: &mut StableSim<'_>, me: usize, pos: (u64, u64), tick: usize, with_anim: bool) {
        self.siege = true;
        self.pinned = Some(pos);
        self.raise_done = None;
        self.next_toggle_at = tick + self.p.toggle_cd;
        self.last_seen_target = tick;
        sim.entity_remove_buff(me, DRAG_BUFF);
        sim.entity_remove_buff(me, SIEGE_BUFF);
        let mut s = BuffV1::named(SIEGE_BUFF);
        s.attack_speed_mult = -20;
        s.move_speed_mult = -100;
        sim.add_buff(me, &s);
        if with_anim {
            animate(sim, me, "skill2", self.p.w_plant);
            sim.play_sfx("abysspact_anchor_foley_w", me, &InputTargetV1::target(me));
        }
        let at = InputTargetV1::pos(pos.0, pos.1);
        sim.play_view_effect("abysspact_anchor_taut", me, &InputTargetV1::target(me), 0, 0, 0);
        sim.play_view_effect("abysspact_anchor_crack", me, &at, 0, 0, 0);
        sim.play_view_effect("abysspact_anchor_stamp", me, &at, 0, 0, 0);
        sim.play_sfx("abysspact_anchor_plant", me, &at);
    }

    fn start_raise(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        self.raise_done = Some(tick + self.p.w_raise);
        self.next_toggle_at = tick + self.p.toggle_cd;
        animate(sim, me, "anchor_raise", self.p.w_raise);
        sim.play_sfx("abysspact_anchor_raise", me, &InputTargetV1::target(me));
    }

    fn finish_raise(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.siege = false;
        self.pinned = None;
        self.raise_done = None;
        sim.entity_remove_buff(me, SIEGE_BUFF);
        sim.entity_remove_buff(me, DRAG_BUFF);
        let mut d = BuffV1::named(DRAG_BUFF);
        d.move_speed_mult = 10;
        sim.add_buff(me, &d);
    }

    /// 压舱：去掉击飞和强制位移（击退、拉、拽），别的控制照旧；位置钉死。
    fn hold_ground(&self, sim: &mut StableSim<'_>, me: usize, pos: (u64, u64)) {
        let displaced = |c: &CcV1| c.kind == CcKindV1::Airborne.code() || c.kind == CcKindV1::ForceMove.code();
        let ccs: Vec<CcV1> = sim
            .get_entity(me)
            .map(|e| (0..e.cc_count()).filter_map(|i| e.cc_at(i)).collect())
            .unwrap_or_default();
        if ccs.iter().any(displaced) {
            sim.entity_clear_cc(me);
            for c in ccs.iter().filter(|c| !displaced(c)) {
                sim.apply_cc(me, c);
            }
        }
        if let Some(pin) = self.pinned {
            if pos != pin {
                sim.entity_set_pos(me, pin.0, pin.1);
            }
        }
    }

    /// (最近的敌方英雄的距离平方, 9 万内有没有敌方英雄, 9 万内有没有任何能打的敌人)。
    fn look(&self, sim: &StableSim<'_>, team: usize, pos: (u64, u64)) -> (u64, bool, bool) {
        let engage2 = (self.p.engage as u64).saturating_mul(self.p.engage as u64);
        let (mut nearest, mut champ_in, mut any_in) = (u64::MAX, false, false);
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() || e.team() == team {
                continue;
            }
            let d2 = dist_sq(pos, e.pos());
            if d2 <= engage2 {
                any_in = true;
            }
            if e.is_champion() {
                nearest = nearest.min(d2);
                champ_in |= d2 <= engage2;
            }
        }
        (nearest, champ_in, any_in)
    }

    /// 按决定切换；`forced` 是 AI 按了 W：不看两次切换的间隔。返回切了没有。
    fn decide(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (u64, u64), tick: usize, forced: bool) -> bool {
        let (nearest, champ_in, any_in) = self.look(sim, team, pos);
        if any_in {
            self.last_seen_target = tick;
        }
        if self.raise_done.is_some() || (!forced && tick < self.next_toggle_at) {
            return false;
        }
        match want(&self.p, self.siege, nearest, champ_in, tick.saturating_sub(self.last_seen_target)) {
            Some(true) => {
                self.plant(sim, me, pos, tick, true);
                true
            }
            Some(false) => {
                self.start_raise(sim, me, tick);
                true
            }
            None => false,
        }
    }
}

impl StablePassive for AnchorPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = Params::parse(params_json);
        SPLASH_PCT.store(self.p.a_splash, Ordering::Relaxed);
        SPLASH_R.store(self.p.a_splash_r, Ordering::Relaxed);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.siege = false;
        self.pinned = None;
        self.raise_done = None;
        self.next_toggle_at = 0;
        self.last_seen_target = 0;
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
        self.siege = false;
        self.pinned = None;
        self.raise_done = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, pos)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.team(), e.pos())) else {
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

        // 起锚放完
        if self.raise_done.is_some_and(|t| tick >= t) {
            self.finish_raise(sim, entity);
        }
        // 大招：没下锚就先下锚（大招自己的动作盖着，不另播）
        if consume_buff(sim, entity, R_SIEGE_ASK) && !self.siege {
            self.plant(sim, entity, pos, tick, false);
        }
        // AI 按了 W：马上判断一次，不该切就退冷却
        if consume_buff(sim, entity, TOGGLE_ASK) && !self.decide(sim, entity, my_team, pos, tick, true) {
            refund_cooldown(sim, entity, SkillSlotV1::Skill2, self.p.w_keep);
        }
        // 平时每 10 tick 判断一次
        if tick % CHECK_EVERY == 0 {
            self.decide(sim, entity, my_team, pos, tick, false);
        }
        if self.siege {
            self.hold_ground(sim, entity, pos);
        }
    }
}

/// 下锚时射程 +3 万（官方的 `range_adjust`，AI 也读）。
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

/// 炮弹命中时调：命中的那个人身边的其他敌人吃溅射（防御塔不吃）。
#[derive(Debug)]
struct ShellSplash;

impl StableEffectType for ShellSplash {
    fn apply(&self, sim: &mut StableSim<'_>, _seed: u64, caster: usize, input: InputTargetV1) {
        let Some((team, ad)) = sim.get_entity(caster).map(|e| (e.team(), e.stat().attack)) else { return };
        let hit = (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id);
        let center = match hit.and_then(|h| sim.get_entity(h)).map(|e| e.pos()) {
            Some(p) => p,
            None => (input.x, input.y),
        };
        let r = SPLASH_R.load(Ordering::Relaxed) as u64;
        let others: Vec<usize> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| Some(e.id()) != hit && e.is_alive() && e.team() != team && !e.is_tower())
            .filter(|e| dist_sq(center, e.pos()) <= r.saturating_mul(r))
            .map(|e| e.id())
            .collect();
        sim.play_view_effect("abysspact_anchor_splash", caster, &InputTargetV1::pos(center.0, center.1), 0, 0, 0);
        let dmg = splash_damage(ad, SPLASH_PCT.load(Ordering::Relaxed));
        for oid in others {
            sim.deal_damage_typed(caster, oid, dmg, DamageTypeV1::Ad, AttackTypeV1::BaseAttack);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_anchor:siege", AnchorPassive::default());
    module.add_native_effect("abysspact_anchor:siege_range", SiegeRange);
    module.add_native_effect("abysspact_anchor:splash", ShellSplash);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn siege_splash_follows_the_kit() {
        let p = Params::parse(&crate::kit_params_of(include_str!(
            "../../../abysspact/champion/abysspact_anchor.data_champion"
        )));
        assert_eq!(p, Params::default());
        assert_eq!(splash_damage(100, p.a_splash), 60);
        assert_eq!(splash_damage(250, p.a_splash), 150);
    }

    #[test]
    fn one_decision_for_planting_and_raising() {
        let p = Params::default();
        let sq = |v: u64| v * v;
        // 9 万内有英雄、3.5 万内没有：下锚
        assert_eq!(want(&p, false, sq(50_000), true, 0), Some(true));
        // 有英雄贴到 3.5 万内：不下
        assert_eq!(want(&p, false, sq(34_000), true, 0), None);
        // 9 万内没有英雄：不下
        assert_eq!(want(&p, false, sq(120_000), false, 0), None);
        // 下着锚：英雄摸到 3 万内起锚，3 万外照打
        assert_eq!(want(&p, true, sq(29_000), true, 0), Some(false));
        assert_eq!(want(&p, true, sq(40_000), true, 0), None);
        // 下着锚 2 秒没东西打：起锚
        assert_eq!(want(&p, true, u64::MAX, false, 120), Some(false));
    }
}
