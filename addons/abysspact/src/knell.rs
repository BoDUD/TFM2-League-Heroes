//! 丧钟 (`abysspact_knell`) · 守钟人 · 辅助坦克
//!
//! - 被动「钟壳」：钟背在背上时受到的伤害 -`shell_dr`%；钟扣在地上的时候没有。
//! - R「丧钟」：数据里 R 在原生模式下是 3 tick 的 idle 动作，只挂待命 `r_arm`。待命期间被动每 tick 看：自己血量
//!   ≥ `r_min_hp`%，`r_range` 内有一个敌方英雄身边 `r_r` 内（含他自己）站着 `r_min_foes` 个以上敌方英雄，才放——
//!   挑扣得住最多人的那个：播 `ult` 动作（钟甩上天），`r_go` tick 后跳过去（`r_leap` tick），落地扣钟。
//!   待命到点没用上就把 R 的冷却退到只剩 `keep`。
//! - 扣钟照莫德凯撒的死亡之国写：他和 `r_r` 内的敌方英雄都被放逐（一段 24 tick、每 12 tick 续一次，提前结束时
//!   人能马上出来），钟里钟外互相打不着；放逐不上的（免控之类）不算关进去。钟每 `r_p` tick 响一次，一共响满
//!   `r_t / r_p` 声，每声对钟里的敌人造成 `r_tick_dmg + r_tick_hp% 他最大生命` 魔法伤害；钟里的人按各自攻速普攻他，
//!   他也挥锤还手。`r_t` tick 后掀钟，钟里还活着的敌人击飞 `r_air`。他死在钟里（不管是钟里打的还是钟外的持续
//!   伤害、塔打的）立刻掀钟放人。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{animate, can_cast, consume_buff, dist_sq, kit_param, map_box, onto_map, refund_cooldown};

pub const HERO: &str = "abysspact_knell";
pub const NATIVE_MARK: &str = "abysspact_knell_native";
pub const SHELL_BUFF: &str = "abysspact_knell_shell";
pub const R_ARM: &str = "abysspact_knell_r_arm";

pub const BANISH_STEP: usize = 24;
pub const BANISH_RENEW: usize = 12;
pub const DEFAULT_SWING: usize = 60;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub shell_dr: usize,
    pub r_r: usize,
    pub r_t: usize,
    pub r_p: usize,
    pub r_tick_dmg: usize,
    pub r_tick_hp: usize,
    pub r_air: usize,
    pub r_min_foes: usize,
    pub r_min_hp: usize,
    pub r_arm: usize,
    pub r_range: usize,
    pub r_go: usize,
    pub r_dur: usize,
    pub r_leap: usize,
    pub keep: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            shell_dr: 15, r_r: 25_000, r_t: 150, r_p: 30, r_tick_dmg: 53, r_tick_hp: 4, r_air: 50,
            r_min_foes: 2, r_min_hp: 50, r_arm: 600, r_range: 50_000, r_go: 14, r_dur: 42, r_leap: 8, keep: 60,
        }
    }
}

impl Params {
    pub fn parse(json: &str) -> Self {
        let d = Self::default();
        let g = |k: &str, v: usize| kit_param(json, k).unwrap_or(v);
        Self {
            shell_dr: g("shell_dr", d.shell_dr), r_r: g("r_r", d.r_r), r_t: g("r_t", d.r_t), r_p: g("r_p", d.r_p),
            r_tick_dmg: g("r_tick_dmg", d.r_tick_dmg), r_tick_hp: g("r_tick_hp", d.r_tick_hp), r_air: g("r_air", d.r_air),
            r_min_foes: g("r_min_foes", d.r_min_foes), r_min_hp: g("r_min_hp", d.r_min_hp), r_arm: g("r_arm", d.r_arm),
            r_range: g("r_range", d.r_range), r_go: g("r_go", d.r_go), r_dur: g("r_dur", d.r_dur), r_leap: g("r_leap", d.r_leap),
            keep: g("keep", d.keep),
        }
    }
}

pub fn chime_damage(p: &Params, knell_max_hp: usize) -> usize {
    p.r_tick_dmg + knell_max_hp.saturating_mul(p.r_tick_hp) / 100
}

/// 一共响几声：钟扣下后每 r_p 响一声，掀钟那一刻响最后一声。
pub fn chimes(p: &Params) -> usize {
    p.r_t / p.r_p.max(1)
}

/// 挑落点：`reach` 是射程里的 (敌方英雄, 位置, 离他的距离平方)；数每个人身边 `r` 内有几个敌方英雄（含他自己，
/// 在 `all` 里数，射程外的也算），挑人最多的，一样多挑近的。返回 (英雄, 位置, 扣得住几个)。
pub fn best_spot(reach: &[(usize, (u64, u64), u64)], all: &[(u64, u64)], r: usize) -> Option<(usize, (u64, u64), usize)> {
    let r2 = (r as u64).saturating_mul(r as u64);
    reach
        .iter()
        .map(|&(id, at, d2)| (id, at, all.iter().filter(|&&o| dist_sq(at, o) <= r2).count(), d2))
        .max_by(|a, b| a.2.cmp(&b.2).then(b.3.cmp(&a.3)))
        .map(|(id, at, n, _)| (id, at, n))
}

fn let_out(sim: &mut StableSim<'_>, id: usize) {
    sim.entity_clear_cc(id);
    sim.entity_banish(id, id, 1, "", "");
}

#[derive(Clone)]
struct Prisoner {
    id: usize,
    next_swing: usize,
}

#[derive(Clone)]
struct BellRealm {
    at: (u64, u64),
    until: usize,
    next_renew: usize,
    next_chime: usize,
    chimes_left: usize,
    next_knell_swing: usize,
    prisoners: Vec<Prisoner>,
}

#[derive(Clone, Copy)]
struct Leap {
    target: usize,
    start_at: usize,
    from: Option<(u64, u64)>,
    to: (u64, u64),
}

#[derive(Clone, Default)]
struct KnellPassive {
    p: Params,
    voice: Voice,
    me: usize,
    native_marked: bool,
    shell_on: bool,
    realm: Option<BellRealm>,
    armed: Option<usize>,
    leap: Option<Leap>,
}

impl KnellPassive {
    fn set_shell(&mut self, sim: &mut StableSim<'_>, entity: usize, want: bool) {
        if self.shell_on == want {
            return;
        }
        if want {
            let mut b = BuffV1::named(SHELL_BUFF);
            b.base_attack_damaged_reduce = self.p.shell_dr;
            b.skill_damaged_reduce = self.p.shell_dr;
            sim.add_buff(entity, &b);
        } else {
            sim.entity_remove_buff(entity, SHELL_BUFF);
        }
        self.shell_on = want;
    }

    fn end_realm(&mut self, sim: &mut StableSim<'_>, entity: usize, completed: bool) {
        let Some(realm) = self.realm.take() else { return };
        let pos = InputTargetV1::pos(realm.at.0, realm.at.1);
        sim.play_view_effect("abysspact_knell_bell_lift", entity, &pos, 0, 0, 0);
        sim.play_sfx("abysspact_knell_lift", entity, &pos);
        if completed {
            sim.play_view_effect("abysspact_knell_bell_open_wave", entity, &pos, 0, 0, 0);
            sim.play_sfx("abysspact_knell_open_wave", entity, &pos);
        }
        if sim.get_entity(entity).is_some_and(|e| e.is_alive()) {
            let_out(sim, entity);
            self.set_shell(sim, entity, true);
        }
        for p in realm.prisoners {
            if sim.get_entity(p.id).is_some_and(|e| e.is_alive()) {
                let_out(sim, p.id);
                if completed {
                    sim.apply_cc(p.id, &CcV1::of_kind(CcKindV1::Airborne, self.p.r_air as u64));
                }
            }
        }
    }

    fn open_realm(&mut self, sim: &mut StableSim<'_>, entity: usize, my_team: usize, center: (u64, u64)) {
        let tick = sim.tick();
        let p = self.p;
        let lim = (p.r_r as u64).saturating_mul(p.r_r as u64);
        let inside: Vec<(usize, usize)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| e.is_champion() && e.is_alive() && e.team() != my_team && e.is_targetable())
            .filter(|e| dist_sq(center, e.pos()) <= lim)
            .map(|e| (e.id(), e.attack_interval()))
            .collect();

        let pos = InputTargetV1::pos(center.0, center.1);
        sim.play_view_effect("abysspact_knell_bell_drop", entity, &pos, 0, 0, 0);
        sim.play_view_effect("abysspact_knell_bell_dust", entity, &pos, 0, 0, 0);
        sim.play_sfx("abysspact_knell_giant_drop", entity, &pos);
        if inside.is_empty() {
            return;
        }
        let step = BANISH_STEP.min(p.r_t).max(1);
        // 他自己进不去钟（被拒）就不扣了
        if !sim.entity_banish(entity, entity, step, "", "") {
            return;
        }
        let mut prisoners = Vec::new();
        for (id, iv) in inside {
            // 放逐不上的（免控之类）不算关进去
            if sim.entity_banish(entity, id, step, "", "") {
                prisoners.push(Prisoner { id, next_swing: tick + if iv > 0 { iv } else { DEFAULT_SWING } / 2 });
            }
        }
        if prisoners.is_empty() {
            let_out(sim, entity);
            return;
        }
        // 钟扣在地上：没有钟壳的减伤
        self.set_shell(sim, entity, false);
        let my_iv = sim.get_entity(entity).map(|e| e.attack_interval()).unwrap_or(DEFAULT_SWING);
        self.realm = Some(BellRealm {
            at: center,
            until: tick + p.r_t,
            next_renew: tick + BANISH_RENEW,
            next_chime: tick + p.r_p.max(1),
            chimes_left: chimes(&p),
            next_knell_swing: tick + if my_iv > 0 { my_iv } else { DEFAULT_SWING } / 2,
            prisoners,
        });
    }

    /// 待命中：血够、扣得住够多的人就跳。
    fn try_fire(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (u64, u64), hp: (usize, usize), tick: usize) {
        let p = self.p;
        if hp.1 == 0 || hp.0.saturating_mul(100) < hp.1.saturating_mul(p.r_min_hp) || !can_cast(sim, me) {
            return;
        }
        let reach = (p.r_range as u64).saturating_mul(p.r_range as u64);
        let cands: Vec<(usize, (u64, u64), u64)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| e.is_champion() && e.is_alive() && e.team() != team && e.is_targetable())
            .map(|e| (e.id(), e.pos(), dist_sq(pos, e.pos())))
            .collect();
        // 落点只在射程里挑，数人时射程外的也算
        let all: Vec<(u64, u64)> = cands.iter().map(|&(_, at, _)| at).collect();
        let in_reach: Vec<(usize, (u64, u64), u64)> = cands.iter().copied().filter(|&(_, _, d2)| d2 <= reach).collect();
        let Some((target, at, _)) = best_spot(&in_reach, &all, p.r_r).filter(|&(_, _, n)| n >= p.r_min_foes) else {
            return;
        };
        self.armed = None;
        self.leap = Some(Leap { target, start_at: tick + p.r_go, from: None, to: at });
        animate(sim, me, "ult", p.r_dur);
        self.voice.play(sim, HERO, me, Cue::Ult);
        let here = InputTargetV1::pos(at.0, at.1);
        sim.play_sfx("abysspact_knell_foley_r", me, &InputTargetV1::target(me));
        sim.play_sfx("abysspact_knell_r_shadow", me, &here);
        sim.play_view_effect("abysspact_knell_bell_shadow", me, &here, 0, 0, 0);
    }

    /// 跳过去：`r_leap` tick 里从起跳点挪到目标（目标走了就追着他），落地扣钟。
    fn run_leap(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (u64, u64), tick: usize) {
        let Some(mut lp) = self.leap else { return };
        if tick < lp.start_at {
            return;
        }
        if let Some(t) = sim.get_entity(lp.target).filter(|e| e.is_alive()).map(|e| e.pos()) {
            lp.to = t;
        }
        let from = *lp.from.get_or_insert(pos);
        let n = self.p.r_leap.max(1);
        let k = (tick - lp.start_at + 1).min(n);
        let f = k as f64 / n as f64;
        let x = from.0 as f64 + (lp.to.0 as f64 - from.0 as f64) * f;
        let y = from.1 as f64 + (lp.to.1 as f64 - from.1 as f64) * f;
        let now = onto_map(map_box(sim), x, y);
        sim.entity_set_pos(me, now.0, now.1);
        if k >= n {
            self.leap = None;
            if self.realm.is_none() {
                self.open_realm(sim, me, team, now);
            }
        } else {
            self.leap = Some(lp);
        }
    }

    fn run_realm(&mut self, sim: &mut StableSim<'_>, entity: usize, my_max_hp: usize, my_atk: usize, my_iv: usize, tick: usize) {
        let Some(mut realm) = self.realm.take() else { return };
        realm.prisoners.retain(|p| sim.get_entity(p.id).is_some_and(|e| e.is_alive()));

        // 续放逐（一段一段给，提前结束时人能马上出来）
        if tick >= realm.next_renew && tick < realm.until {
            let left = realm.until.saturating_sub(tick).min(BANISH_STEP).max(1);
            sim.entity_banish(entity, entity, left, "", "");
            for p in &realm.prisoners {
                sim.entity_banish(entity, p.id, left, "", "");
            }
            realm.next_renew = tick + BANISH_RENEW;
        }

        // 钟响：掀钟那一刻也响，一共响满
        if tick >= realm.next_chime && realm.chimes_left > 0 && !realm.prisoners.is_empty() {
            let dmg = chime_damage(&self.p, my_max_hp);
            let pos = InputTargetV1::pos(realm.at.0, realm.at.1);
            sim.play_view_effect("abysspact_knell_bell_chime", entity, &pos, 0, 0, 0);
            sim.play_sfx("abysspact_knell_giant_chime", entity, &pos);
            for p in &realm.prisoners {
                sim.deal_damage_typed(entity, p.id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            }
            realm.next_chime = tick + self.p.r_p.max(1);
            realm.chimes_left -= 1;
            realm.prisoners.retain(|p| sim.get_entity(p.id).is_some_and(|e| e.is_alive()));
        }

        if realm.prisoners.is_empty() || tick >= realm.until {
            self.realm = Some(realm);
            self.end_realm(sim, entity, true);
            return;
        }

        // 他挥锤打第一个关进来的人
        if tick >= realm.next_knell_swing {
            if let Some(p0) = realm.prisoners.first() {
                sim.deal_damage_typed(entity, p0.id, my_atk, DamageTypeV1::Ad, AttackTypeV1::BaseAttack);
            }
            realm.next_knell_swing = tick + if my_iv > 0 { my_iv } else { DEFAULT_SWING };
        }
        // 钟里的人只能普攻他
        for p in &mut realm.prisoners {
            if tick >= p.next_swing {
                if let Some((e_atk, e_iv)) = sim
                    .get_entity(p.id)
                    .filter(|e| e.is_alive())
                    .map(|e| (e.stat().attack, e.attack_interval()))
                {
                    sim.deal_damage_typed(p.id, entity, e_atk, DamageTypeV1::Ad, AttackTypeV1::BaseAttack);
                    p.next_swing = tick + if e_iv > 0 { e_iv } else { DEFAULT_SWING };
                }
            }
        }

        let still_alive = sim.get_entity(entity).is_some_and(|e| e.is_alive());
        self.realm = Some(realm);
        if !still_alive {
            self.end_realm(sim, entity, false);
        }
    }
}

impl StablePassive for KnellPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = Params::parse(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.me = entity;
        self.native_marked = false;
        self.shell_on = false;
        self.realm = None;
        self.armed = None;
        self.leap = None;
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
        // 死了以后被动不跑：钟这会儿就要掀开放人（不击飞）
        if self.realm.is_some() {
            self.end_realm(sim, self.me, false);
        }
        self.shell_on = false;
        self.armed = None;
        self.leap = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        self.me = entity;
        let Some((alive, my_team, my_pos, hp, my_atk, my_iv)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.hp(), e.stat().attack, e.attack_interval()))
        else {
            return;
        };
        if !alive {
            if self.realm.is_some() {
                self.end_realm(sim, entity, false);
            }
            self.shell_on = false;
            return;
        }
        let tick = sim.tick();

        if !self.native_marked {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
            self.native_marked = true;
        }
        if self.realm.is_none() {
            self.set_shell(sim, entity, true);
        }

        // AI 按了 R：待命
        if consume_buff(sim, entity, R_ARM) {
            self.armed = Some(tick + self.p.r_arm);
        }
        if tick % 3 == 0 && self.armed.is_some() && self.leap.is_none() && self.realm.is_none() {
            self.try_fire(sim, entity, my_team, my_pos, hp, tick);
        }
        if self.armed.is_some_and(|t| tick >= t) {
            self.armed = None;
            refund_cooldown(sim, entity, SkillSlotV1::Ult, self.p.keep);
        }
        if self.leap.is_some() {
            self.run_leap(sim, entity, my_team, my_pos, tick);
        }
        if self.realm.is_some() {
            self.run_realm(sim, entity, hp.1, my_atk, my_iv, tick);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_knell:bell_shell", KnellPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn chimes_ring_full_and_scale_with_knell_max_hp() {
        let p = Params::default();
        assert_eq!(chime_damage(&p, 1000), 93);
        assert_eq!(chime_damage(&p, 2500), 153);
        assert_eq!(chimes(&p), 5);
    }

    #[test]
    fn the_bell_goes_where_it_catches_the_most() {
        let r = 25_000;
        // 两个人挨着、一个人落单（离他最近）：挑挨着的里近的那个
        let cands = [(1, (100_000, 100_000), 10), (2, (110_000, 100_000), 20), (3, (300_000, 100_000), 5)];
        let all: Vec<(u64, u64)> = cands.iter().map(|c| c.1).collect();
        assert_eq!(best_spot(&cands, &all, r), Some((1, (100_000, 100_000), 2)));
        // 射程里只有落单的那个：只扣得住一个（不够两个，不放）
        assert_eq!(best_spot(&cands[2..], &all, r).unwrap().2, 1);
        assert!(best_spot(&[], &all, r).is_none());
    }

    #[test]
    fn params_come_from_the_kit_file() {
        assert_eq!(Params::parse(&crate::kit_params_of(include_str!(
            "../../../abysspact/champion/abysspact_knell.data_champion"
        ))), Params::default());
    }
}
