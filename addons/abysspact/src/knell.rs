//! 丧钟 (`abysspact_knell`) · 守钟人 · 辅助坦克
//!
//! 招牌机制「钟壳 + 扣钟（多目标隔离黑钟空间）」:
//! - 被动「钟壳」：巨钟背在背上时受到的所有伤害 -15%；放大招把钟扣在地上期间失去钟壳减伤。
//! - R「丧钟」：跳向目标点把巨钟从天扣下，把**自己与 2.5 万内的全部敌方英雄**一起关进黑钟 2.5 秒（150 ticks）：
//!   * 照莫德凯撒死亡之国短步续放逐写法：钟里钟外互相无法选中、队友进不来也奶不到；
//!   * 钟内每 0.5 秒（30 ticks）震响一次，对钟内所有敌人造成 `40 + 3% 丧钟最大生命` 魔法伤害并播 `bell_chime`；
//!   * 钟内敌人全程沉默，按各自真实攻速普攻围殴丧钟一人（丧钟同时挥锤还击）；
//!   * 2.5 秒后巨钟掀开（`bell_lift` + `bell_open_wave`），钟内所有存活敌人被击飞 0.75 秒（45 ticks）；
//!   * 若丧钟提前倒在钟里，巨钟立刻掀开释放全部被关敌人，绝不卡放逐！

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq};

pub const HERO: &str = "abysspact_knell";
pub const NATIVE_MARK: &str = "abysspact_knell_native";
pub const SHELL_BUFF: &str = "abysspact_knell_shell";
pub const R_ASK: &str = "abysspact_knell_r_ask";
pub const R_CAST_VOICE: &str = "abysspact_knell_r_voice";

pub const BELL_RADIUS: u64 = 25_000;   // 2.5万
pub const BELL_TICKS: usize = 150;     // 2.5s
pub const CHIME_EVERY: usize = 30;     // 0.5s (5 chimes total)
pub const BANISH_STEP: usize = 24;
pub const BANISH_RENEW: usize = 12;
pub const CHIME_BASE_DMG: usize = 53;
pub const CHIME_HP_PCT: usize = 4;
pub const LIFT_AIRBORNE: u64 = 45;     // 0.75s knockup on bell lift
pub const DEFAULT_SWING: usize = 60;

pub fn chime_damage(knell_max_hp: usize) -> usize {
    CHIME_BASE_DMG + knell_max_hp.saturating_mul(CHIME_HP_PCT) / 100
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
    next_knell_swing: usize,
    prisoners: Vec<Prisoner>,
}

#[derive(Clone, Default)]
struct KnellPassive {
    voice: Voice,
    native_marked: bool,
    shell_on: bool,
    realm: Option<BellRealm>,
}

impl KnellPassive {
    fn set_shell(&mut self, sim: &mut StableSim<'_>, entity: usize, want: bool) {
        if self.shell_on == want {
            return;
        }
        if want {
            let mut b = BuffV1::named(SHELL_BUFF);
            b.base_attack_damaged_reduce = 15;
            b.skill_damaged_reduce = 15;
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
                    sim.apply_cc(p.id, &CcV1::of_kind(CcKindV1::Airborne, LIFT_AIRBORNE));
                }
            }
        }
    }

    fn open_realm(&mut self, sim: &mut StableSim<'_>, entity: usize, my_team: usize, center: (u64, u64)) {
        let tick = sim.tick();
        let lim = BELL_RADIUS * BELL_RADIUS;
        let mut prisoners = Vec::new();
        let n = sim.entity_count();
        for i in 0..n {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_champion() && e.is_alive() && e.team() != my_team && dist_sq(center, e.pos()) <= lim {
                let iv = e.attack_interval();
                prisoners.push(Prisoner {
                    id: e.id(),
                    next_swing: tick + if iv > 0 { iv } else { DEFAULT_SWING } / 2,
                });
            }
        }

        let pos = InputTargetV1::pos(center.0, center.1);
        sim.play_view_effect("abysspact_knell_bell_drop", entity, &pos, 0, 0, 0);
        sim.play_view_effect("abysspact_knell_bell_dust", entity, &pos, 0, 0, 0);
        sim.play_sfx("abysspact_knell_giant_drop", entity, &pos);

        if prisoners.is_empty() {
            return;
        }

        // Remove backpack shell DR while bell is dropped on the ground!
        self.set_shell(sim, entity, false);
        let until = tick + BELL_TICKS;
        let step = BANISH_STEP.min(BELL_TICKS);
        sim.entity_banish(entity, entity, step, "", "");
        for p in &prisoners {
            sim.entity_banish(entity, p.id, step, "", "");
        }
        let my_iv = sim.get_entity(entity).map(|e| e.attack_interval()).unwrap_or(DEFAULT_SWING);
        self.realm = Some(BellRealm {
            at: center,
            until,
            next_renew: tick + BANISH_RENEW,
            next_chime: tick + CHIME_EVERY,
            next_knell_swing: tick + if my_iv > 0 { my_iv } else { DEFAULT_SWING } / 2,
            prisoners,
        });
    }
}

impl StablePassive for KnellPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.native_marked = false;
        self.shell_on = false;
        self.realm = None;
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
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.shell_on = false;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, my_max_hp, my_atk, my_iv)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.hp().1, e.stat().attack, e.attack_interval()))
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
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // Trigger R「丧钟」multi-enemy Bell Realm
        if consume_buff(sim, entity, R_ASK) && self.realm.is_none() {
            self.open_realm(sim, entity, my_team, my_pos);
        }

        // Tick active Bell Realm
        let Some(mut realm) = self.realm.take() else { return };
        realm.prisoners.retain(|p| sim.get_entity(p.id).is_some_and(|e| e.is_alive()));

        if realm.prisoners.is_empty() || tick >= realm.until {
            self.realm = Some(realm);
            self.end_realm(sim, entity, true);
            return;
        }

        // Renew short-step banishes so early exit always frees everyone cleanly
        if tick >= realm.next_renew {
            let left = realm.until.saturating_sub(tick).min(BANISH_STEP).max(1);
            sim.entity_banish(entity, entity, left, "", "");
            for p in &realm.prisoners {
                sim.entity_banish(entity, p.id, left, "", "");
            }
            realm.next_renew = tick + BANISH_RENEW;
        }

        // Chime every 0.5s: AoE magic damage + shaking bell VFX/SFX!
        if tick >= realm.next_chime {
            let dmg = chime_damage(my_max_hp);
            let pos = InputTargetV1::pos(realm.at.0, realm.at.1);
            sim.play_view_effect("abysspact_knell_bell_chime", entity, &pos, 0, 0, 0);
            sim.play_sfx("abysspact_knell_giant_chime", entity, &pos);
            for p in &realm.prisoners {
                sim.deal_damage_typed(entity, p.id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            }
            realm.next_chime = tick + CHIME_EVERY;
        }

        // Knell basic-attacks the first trapped enemy
        if tick >= realm.next_knell_swing {
            if let Some(p0) = realm.prisoners.first() {
                sim.deal_damage_typed(entity, p0.id, my_atk, DamageTypeV1::Ad, AttackTypeV1::BaseAttack);
            }
            realm.next_knell_swing = tick + if my_iv > 0 { my_iv } else { DEFAULT_SWING };
        }

        // Trapped enemies (silenced) can only basic-attack Knell inside the bell!
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

        // Check if Knell died from the trapped enemies' swings!
        let still_alive = sim.get_entity(entity).is_some_and(|e| e.is_alive());
        self.realm = Some(realm);
        if !still_alive {
            self.end_realm(sim, entity, false);
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
    fn chime_damage_scales_with_knell_max_hp() {
        assert_eq!(chime_damage(1000), 93);
        assert_eq!(chime_damage(2500), 153);
    }
}
