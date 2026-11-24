//! 蜕甲 (`abysspact_carapace`) · 蜕壳甲虫骑士 · 上路战士
//!
//! 招牌机制「蜕壳」一条命三次形态（甲 → 虫 → 羽）+ 原地空壳嘲讽自爆:
//! - 第一形态「甲」（2 层壳）：护甲 +30、不死拦截（血归 1 立刻蜕壳）；头顶 `shells_2`。
//! - 第二形态「虫」（1 层壳）：最大生命 -20%、攻速 +15%、移速 +10%、不死拦截；显示钩子切 `bg_*`；头顶 `shells_1`。
//! - 第三形态「羽」（0 层壳）：最大生命 -40%、攻速 +30%、移速 +20%，Q 射程 2.5万 → 4.0万飞扑；显示钩子切 `wg_*` 四片虫翼；头顶 `shells_0`；再死即真阵亡，复活重穿全甲。
//! - 每次蜕壳：回至 40% 最大生命 + 0.5 秒不可选中免疫，原地留下空壳嘲讽 3 万内敌人 1.25 秒，1.5 秒后炸开 `100 + 8% 最大生命` 物理伤害！
//! - R「羽化」：未到第三形态时主动蜕壳（保留血量比例），旧壳当场炸开 3 万击飞 0.75s + `150 + 100% AD`，并获得 4 秒 +40% 攻速；第三形态时张翅 6 万飞扑落地击飞。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq};

pub const HERO: &str = "abysspact_carapace";
pub const NATIVE_MARK: &str = "abysspact_carapace_native";
pub const FORM1_BUFF: &str = "abysspact_carapace_form1";
pub const FORM2_BUFF: &str = "abysspact_carapace_form2";
pub const FORM3_BUFF: &str = "abysspact_carapace_form3";
pub const INVULN_BUFF: &str = "abysspact_carapace_molt_inv";
pub const R_HASTE_BUFF: &str = "abysspact_carapace_r_haste";
pub const R_MOLT_ASK: &str = "abysspact_carapace_r_molt";
pub const R_CAST_VOICE: &str = "abysspact_carapace_r_voice";

pub const SHELL_RADIUS: u64 = 30_000;
pub const SHELL_EXPLODE_TICKS: usize = 90; // 1.5s
pub const SHELL_TAUNT_TICKS: u64 = 75;     // 1.25s
pub const MOLT_INVULN_TICKS: usize = 30;   // 0.5s
pub const R_AIRBORNE_TICKS: u64 = 45;      // 0.75s
pub const R_HASTE_TICKS: usize = 240;      // 4.0s

pub fn shell_explosion_damage(max_hp: usize) -> usize {
    100 + max_hp.saturating_mul(8) / 100
}

pub fn r_burst_damage(ad: usize) -> usize {
    195 + ad.saturating_mul(127) / 100
}

pub fn shells_buff_name(shells: u8) -> &'static str {
    match shells {
        2 => "abysspact_carapace_shells_2",
        1 => "abysspact_carapace_shells_1",
        _ => "abysspact_carapace_shells_0",
    }
}

#[derive(Clone, Copy)]
struct HuskBomb {
    pos: (u64, u64),
    explode_at: usize,
    dmg: usize,
}

#[derive(Clone)]
struct CarapacePassive {
    voice: Voice,
    shells: u8,
    synced: bool,
    husks: Vec<HuskBomb>,
}

impl Default for CarapacePassive {
    fn default() -> Self {
        Self { voice: Voice::default(), shells: 2, synced: false, husks: Vec::new() }
    }
}

impl CarapacePassive {
    fn sync_form(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        for b in [FORM1_BUFF, FORM2_BUFF, FORM3_BUFF,
                  "abysspact_carapace_shells_0", "abysspact_carapace_shells_1", "abysspact_carapace_shells_2"] {
            sim.entity_remove_buff(entity, b);
        }
        match self.shells {
            2 => {
                let mut f = BuffV1::named(FORM1_BUFF);
                f.defence = 30;
                f.undying = true;
                sim.add_buff(entity, &f);
            }
            1 => {
                let mut f = BuffV1::named(FORM2_BUFF);
                f.hp_mult = -20;
                f.attack_speed_mult = 15;
                f.move_speed_mult = 10;
                f.undying = true;
                sim.add_buff(entity, &f);
            }
            _ => {
                let mut f = BuffV1::named(FORM3_BUFF);
                f.hp_mult = -40;
                f.attack_speed_mult = 30;
                f.move_speed_mult = 20;
                sim.add_buff(entity, &f);
            }
        }
        sim.add_buff(entity, &BuffV1::named(shells_buff_name(self.shells)));
        self.synced = true;
    }

    fn perform_molt(&mut self, sim: &mut StableSim<'_>, entity: usize, pos: (u64, u64), my_team: usize,
                    cur_hp: usize, old_max_hp: usize, ad: usize, active_r: bool) {
        if self.shells == 0 {
            return;
        }
        let ratio_pct = if old_max_hp > 0 { (cur_hp.saturating_mul(100) / old_max_hp).clamp(1, 100) } else { 40 };
        self.shells -= 1;
        self.sync_form(sim, entity);

        // Brief 0.5s untargetable/immune molt emerge window
        let mut inv = BuffV1::timed(INVULN_BUFF, MOLT_INVULN_TICKS);
        inv.damaged_reduce = 100;
        inv.cc_immune = true;
        sim.add_buff(entity, &inv);

        // Recompute HP: death-molt heals to 40% new max HP; R active molt preserves HP ratio!
        let new_max = sim.get_entity(entity).map(|e| e.hp().1).unwrap_or(old_max_hp).max(1);
        let target_hp = if active_r {
            new_max.saturating_mul(ratio_pct) / 100
        } else {
            new_max.saturating_mul(40) / 100
        };
        sim.entity_set_hp(entity, target_hp.max(1).min(new_max));

        let fx = if self.shells == 1 { "abysspact_carapace_molt_steel" } else { "abysspact_carapace_molt_light" };
        sim.play_view_effect(fx, entity, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
        sim.play_sfx("abysspact_carapace_molt_crack", entity, &InputTargetV1::pos(pos.0, pos.1));
        sim.play_sfx("abysspact_carapace_molt_rise", entity, &InputTargetV1::target(entity));

        let r2 = SHELL_RADIUS * SHELL_RADIUS;
        if active_r {
            // R「羽化」: old shell bursts immediately with 0.75s knockup + 150 + 100% AD + 4s +40% AS!
            let mut haste = BuffV1::timed(R_HASTE_BUFF, R_HASTE_TICKS);
            haste.attack_speed_mult = 40;
            sim.add_buff(entity, &haste);
            sim.play_view_effect("abysspact_carapace_molt_burst", entity, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
            sim.play_sfx("abysspact_carapace_shell_burst", entity, &InputTargetV1::pos(pos.0, pos.1));
            let dmg = r_burst_damage(ad);
            let mut victims = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_alive() && e.team() != my_team && !e.is_tower() && dist_sq(pos, e.pos()) <= r2 {
                    victims.push(e.id());
                }
            }
            for vid in victims {
                sim.deal_damage_typed(entity, vid, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
                sim.apply_cc(vid, &CcV1::of_kind(CcKindV1::Airborne, R_AIRBORNE_TICKS));
            }
        } else {
            // Passive death-molt: empty shell stands 1.5s, taunts 3万 foes 1.25s, then explodes!
            sim.play_view_effect("abysspact_carapace_shell_rattle", entity, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
            sim.play_view_effect("abysspact_carapace_taunt_glint", entity, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
            sim.play_sfx("abysspact_carapace_shell_rattle", entity, &InputTargetV1::pos(pos.0, pos.1));
            let mut victims = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_alive() && e.team() != my_team && !e.is_tower() && dist_sq(pos, e.pos()) <= r2 {
                    victims.push(e.id());
                }
            }
            for vid in victims {
                sim.apply_cc(vid, &CcV1::of_kind(CcKindV1::Taunt, SHELL_TAUNT_TICKS));
            }
            self.husks.push(HuskBomb {
                pos,
                explode_at: sim.tick() + SHELL_EXPLODE_TICKS,
                dmg: shell_explosion_damage(old_max_hp),
            });
        }
    }
}

impl StablePassive for CarapacePassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.shells = 2;
        self.synced = false;
        self.husks.clear();
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
        self.shells = 2;
        self.synced = false;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, pos, cur_hp, max_hp, ad)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.hp().0, e.hp().1, e.stat().attack))
        else {
            return;
        };
        let tick = sim.tick();

        // Detonate mature empty shells even if Carapace moved on
        let mut due = Vec::new();
        self.husks.retain(|h| {
            if tick >= h.explode_at {
                due.push(*h);
                false
            } else {
                true
            }
        });
        let r2 = SHELL_RADIUS * SHELL_RADIUS;
        for h in due {
            sim.play_view_effect("abysspact_carapace_shell_explode", entity, &InputTargetV1::pos(h.pos.0, h.pos.1), 0, 0, 0);
            sim.play_sfx("abysspact_carapace_shell_burst", entity, &InputTargetV1::pos(h.pos.0, h.pos.1));
            let mut victims = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_alive() && e.team() != my_team && !e.is_tower() && dist_sq(h.pos, e.pos()) <= r2 {
                    victims.push(e.id());
                }
            }
            for vid in victims {
                sim.deal_damage_typed(entity, vid, h.dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
            }
        }

        if !alive {
            return;
        }
        if !crate::has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }
        if !self.synced {
            self.sync_form(sim, entity);
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }
        if consume_buff(sim, entity, R_MOLT_ASK) && self.shells > 0 {
            self.perform_molt(sim, entity, pos, my_team, cur_hp, max_hp, ad, true);
            return;
        }
        // Lethal blow intercepted by undying while shells > 0 -> immediate automatic Molt!
        if self.shells > 0 && cur_hp <= 2 {
            self.perform_molt(sim, entity, pos, my_team, cur_hp, max_hp, ad, false);
        }
    }
}

/// Official `StableEffectType::range_adjust` for Form 3 Q dive (+1.5万 -> 4万) and R dive (+3万 -> 6万).
#[derive(Debug)]
struct Form3Range(u64);

impl StableEffectType for Form3Range {
    fn apply(&self, _sim: &mut StableSim<'_>, _seed: u64, _caster: usize, _input: InputTargetV1) {}
    fn may_adjust_range(&self) -> bool {
        true
    }
    fn range_adjust(&self, caster: &StableEntityView<'_>, _target: &StableEntityView<'_>) -> u64 {
        let is_f3 = (0..caster.buff_count()).any(|i| caster.buff_at(i).is_some_and(|b| b.name() == FORM3_BUFF));
        if is_f3 { self.0 } else { 0 }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_carapace:molt", CarapacePassive::default());
    module.add_native_effect("abysspact_carapace:q_range", Form3Range(15_000));
    module.add_native_effect("abysspact_carapace:r_range", Form3Range(30_000));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn shell_explosion_and_form_indicators_match_spec() {
        assert_eq!(shell_explosion_damage(1000), 180);
        assert_eq!(shell_explosion_damage(2000), 260);
        assert_eq!(r_burst_damage(100), 322);
        assert_eq!(shells_buff_name(2), "abysspact_carapace_shells_2");
        assert_eq!(shells_buff_name(0), "abysspact_carapace_shells_0");
    }
}
