//! 缓刑 (`abysspact_reprieve`) · 囚徒 · 上路坦克
//!
//! 招牌机制「缓刑」：受到的伤害只有一半当场扣，另一半记成「刑期」（W 认罪嘲讽的那 1.25 秒里记七成），
//! 在接下来 4 秒里一点点扣完；刑期最多记到最大生命的 60%，再多的当场扣。他或 6 万内的队友拿到人头
//! （击杀、助攻，或者 6 万内有敌方英雄倒下）时刑期一笔勾销，没拿到就一点不少地扣回来。
//!
//! - `on_damaged` 在这一下扣血之前调：先把要缓的那截加回去，扣完正好少挨这么多。满血、快满血时加不上去的那截
//!   等这一下扣完再补（`owed`，league_braum 0.1.3 的写法）；这一下本来会打死他、缓刑后本该活着，就先挂
//!   2 tick 不死。账本按要缓的全额记。
//! - 还债：每 0.2 秒扣一次。不致死的用 `entity_set_hp` 直接扣，不借任何人的名义（借了会触发对方的命中效果，
//!   对方死了、复活成新单位时还会扣不出去）；只有会把他扣死的那一下记给还在的最后一个攻击者（没有就记他自己）。
//!   这一下排进效果队列、下一 tick 才落地（league_milio 的发现），所以记下 (tick, 攻击者, 金额)，它落地时
//!   （`on_damaged`）不再记账。
//! - 缓刑后本该活着的那一下：挂 1 tick 不死，下一 tick 补血时摘掉，不挡同一 tick 里别的致死伤害太久。

use std::collections::HashSet;
use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff, refund_hit};

pub const HERO: &str = "abysspact_reprieve";
pub const NATIVE_MARK: &str = "abysspact_reprieve_native";
pub const GUILT_BUFF: &str = "abysspact_reprieve_guilt";
pub const TALLY_LIGHT: &str = "abysspact_reprieve_tally_light";
pub const HOLD: &str = "abysspact_reprieve_hold";
pub const R_CAST_VOICE: &str = "abysspact_reprieve_r_voice";

pub const BASE_DEFER_PCT: usize = 50;
pub const GUILT_DEFER_PCT: usize = 70;
pub const CAP_MAX_HP_PCT: usize = 60;
pub const PAY_TICKS: usize = 240;     // 4 秒还清
pub const PAY_STEP: usize = 12;       // 每 0.2 秒还一次
pub const ABSOLVE_RANGE: u64 = 60_000;

pub fn defer_amount(incoming: usize, guilty: bool, current_pool: usize, max_hp: usize) -> usize {
    let pct = if guilty { GUILT_DEFER_PCT } else { BASE_DEFER_PCT };
    let cap = max_hp.saturating_mul(CAP_MAX_HP_PCT) / 100;
    let room = cap.saturating_sub(current_pool);
    (incoming.saturating_mul(pct) / 100).min(room)
}

#[derive(Clone, Copy)]
struct DebtBucket {
    remaining: usize,
    per_step: usize,
    attacker: usize,
}

#[derive(Clone, Default)]
struct ReprievePassive {
    voice: Voice,
    native_marked: bool,
    buckets: Vec<DebtBucket>,
    in_payback: bool,
    /// 记给攻击者的那一笔还债：(打出去的 tick, 攻击者, 金额)，它下一 tick 落地时别再记账。
    payback_echo: Option<(usize, usize, usize)>,
    last_pay_tick: usize,
    last_tally_vfx: usize,
    tally_shown: bool,
    alive_enemies: HashSet<usize>,
    /// 这一下扣完以后要加回去的血（满血附近加不上去的那截）。
    owed: usize,
}

impl ReprievePassive {
    fn total_pool(&self) -> usize {
        self.buckets.iter().map(|b| b.remaining).sum()
    }

    fn sync_tally_visual(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        let has_debt = self.total_pool() > 0;
        if has_debt && !self.tally_shown {
            sim.add_buff(entity, &BuffV1::named(TALLY_LIGHT));
            self.tally_shown = true;
        } else if !has_debt && self.tally_shown {
            sim.entity_remove_buff(entity, TALLY_LIGHT);
            self.tally_shown = false;
        }
    }

    fn absolve(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if self.buckets.is_empty() {
            return;
        }
        self.buckets.clear();
        self.sync_tally_visual(sim, entity);
        sim.play_view_effect("abysspact_reprieve_absolve", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_reprieve_absolve", entity, &InputTargetV1::target(entity));
    }

    /// 上一下已经扣完了：把那时加不上去的血补上。
    fn pay_owed(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if self.owed == 0 {
            return;
        }
        let owed = std::mem::take(&mut self.owed);
        // 缓刑后本该活着的那一下已经落地：不死只为它挂，摘掉
        sim.entity_remove_buff(me, HOLD);
        let Some((now, max)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        let hp = now.saturating_add(owed).min(max);
        if hp > now {
            sim.entity_set_hp(me, hp);
        }
    }

    /// 致死的那一下记给谁：账本里最近一个还在场上的攻击者，没有就记他自己。
    fn credit(&self, sim: &StableSim<'_>, me: usize) -> usize {
        self.buckets
            .iter()
            .rev()
            .map(|b| b.attacker)
            .find(|&a| a != me && sim.get_entity(a).is_some())
            .unwrap_or(me)
    }
}

impl StablePassive for ReprievePassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.native_marked = false;
        self.buckets.clear();
        self.in_payback = false;
        self.last_pay_tick = 0;
        self.last_tally_vfx = 0;
        self.tally_shown = false;
        self.alive_enemies.clear();
        self.owed = 0;
        self.payback_echo = None;
        sim.entity_remove_buff(entity, TALLY_LIGHT);
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, target: usize, _damage: &mut usize) {
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, attacker: usize, damage: usize) {
        // 同一 tick 前面那一下已经扣完了
        self.pay_owed(sim, entity);
        if self.in_payback || damage == 0 {
            return;
        }
        // 自己那一笔还债落地了：不再记账
        if let Some((t, a, amt)) = self.payback_echo {
            let tick = sim.tick();
            if tick > t + 2 {
                self.payback_echo = None;
            } else if attacker == a && damage <= amt + amt / 5 + 1 {
                self.payback_echo = None;
                return;
            }
        }
        let Some((alive, cur_hp, max_hp)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.hp().0, e.hp().1)) else {
            return;
        };
        if !alive || max_hp == 0 {
            return;
        }
        let guilty = has_buff(sim, entity, GUILT_BUFF);
        let defer = defer_amount(damage, guilty, self.total_pool(), max_hp);
        if defer == 0 {
            return;
        }
        let (set, owed, lethal) = refund_hit(cur_hp, max_hp, defer, damage);
        if set != cur_hp {
            sim.entity_set_hp(entity, set);
        }
        if lethal {
            let mut hold = BuffV1::timed(HOLD, 1);
            hold.undying = true;
            sim.add_buff(entity, &hold);
        }
        self.owed += owed;
        let pulses = (PAY_TICKS / PAY_STEP).max(1);
        self.buckets.push(DebtBucket {
            remaining: defer,
            per_step: defer.div_ceil(pulses).max(1),
            attacker,
        });
        self.sync_tally_visual(sim, entity);
        let tick = sim.tick();
        if tick >= self.last_tally_vfx + 30 {
            self.last_tally_vfx = tick;
            sim.play_view_effect("abysspact_reprieve_tally", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_sfx("abysspact_reprieve_tally", entity, &InputTargetV1::target(entity));
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
            self.absolve(sim, entity);
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.absolve(sim, entity);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.buckets.clear();
        self.owed = 0;
        self.payback_echo = None;
        self.tally_shown = false;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        self.pay_owed(sim, entity);
        let Some((alive, my_team, my_pos)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.team(), e.pos())) else {
            return;
        };
        if !alive {
            return;
        }
        let tick = sim.tick();

        if !self.native_marked {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
            self.native_marked = true;
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 6 万内有敌方英雄倒下（不管谁杀的）：刑期勾销
        let mut now_alive = HashSet::new();
        let mut absolved = false;
        let lim = ABSOLVE_RANGE * ABSOLVE_RANGE;
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_champion() && e.team() != my_team {
                if e.is_alive() {
                    now_alive.insert(e.id());
                } else if self.alive_enemies.contains(&e.id()) && dist_sq(my_pos, e.pos()) <= lim {
                    absolved = true;
                }
            }
        }
        self.alive_enemies = now_alive;
        if absolved {
            self.absolve(sim, entity);
        }

        // 每 0.2 秒还一次账
        if !self.buckets.is_empty() && tick >= self.last_pay_tick + PAY_STEP {
            self.last_pay_tick = tick;
            let credit = self.credit(sim, entity);
            let mut due: usize = 0;
            for b in &mut self.buckets {
                let take = b.per_step.min(b.remaining);
                b.remaining -= take;
                due = due.saturating_add(take);
            }
            self.buckets.retain(|b| b.remaining > 0);
            if due > 0 {
                let cur = sim.get_entity(entity).map_or(0, |e| e.hp().0);
                if cur > due {
                    sim.entity_set_hp(entity, cur - due);
                } else {
                    // 这一下要扣死他：记给最后一个攻击者
                    self.in_payback = true;
                    let ok = sim.deal_damage_typed(credit, entity, due, DamageTypeV1::Fixed, AttackTypeV1::DotIgnoreShield);
                    let by = if ok {
                        credit
                    } else {
                        sim.deal_damage_typed(entity, entity, due, DamageTypeV1::Fixed, AttackTypeV1::DotIgnoreShield);
                        entity
                    };
                    self.in_payback = false;
                    self.payback_echo = Some((tick, by, due));
                }
            }
            self.sync_tally_visual(sim, entity);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_reprieve:sentence", ReprievePassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::refund_hit;

    #[test]
    fn sentence_defers_half_or_seventy_up_to_sixty_cap() {
        assert_eq!(defer_amount(200, false, 0, 1000), 100);
        assert_eq!(defer_amount(200, true, 0, 1000), 140);
        assert_eq!(defer_amount(500, true, 550, 1000), 50);
        assert_eq!(defer_amount(500, false, 600, 1000), 0);
    }

    #[test]
    fn full_health_still_defers_and_a_deferred_lethal_hit_is_survived() {
        // 满血 2000 吃 400：先设回 2000，扣完 1600，再补 200 = 1800（缓了一半）
        let (set, owed, lethal) = refund_hit(2000, 2000, 200, 400);
        assert_eq!((set, owed, lethal), (2000, 200, false));
        assert_eq!(set - 400 + owed, 1800);
        // 600 血吃 1000：缓 500 后本该剩 100
        let (set, owed, lethal) = refund_hit(600, 2000, 500, 1000);
        assert_eq!(set, 1100);
        assert!(!lethal);
        assert_eq!(set - 1000 + owed, 100);
        // 满血 2000 吃 2600：缓 1300 后本该剩 700；设成 2000 会被打死，所以挂不死、剩 1 血、再补 699
        let (set, owed, lethal) = refund_hit(2000, 2000, 1300, 2600);
        assert!(lethal);
        assert_eq!((set, owed), (2000, 699));
        // 缓了也活不了：照死
        let (_, _, lethal) = refund_hit(300, 2000, 400, 1000);
        assert!(!lethal);
    }
}
