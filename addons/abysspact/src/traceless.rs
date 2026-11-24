//! 无痕 (`abysspact_traceless`) · 白衣剑客 · 中路物理刺客
//!
//! 招牌机制「无痕锋 + 脱战隐身 + 一沾就散」:
//! - 每次命中敌方英雄（普攻、Q、R）且期间自身未掉一滴血：叠 1 层「锋」（上限 8 层，每层攻击力 +7%，满层 +56%），
//!   点亮头顶 1–8 刻度 `abysspact_traceless_edge_{1..8}` 与剑光 `blade_glow`。
//! - 1.5 秒（90 ticks）未出手且未受击自动进入隐身（`entity_set_invisible`）；
//!   隐身后的第一剑必定叠锋并额外造成 +50% 物理伤害！
//! - 代价「一沾就散」：只要实际生命值下降哪怕 1 点（护盾挡下不算掉血），锋瞬间全部清零，
//!   白衣溅开 `ink` 黑墨并播放 `quench` 剑光熄灭特效！
//! - Q「一线」击杀敌方英雄立刻刷新冷却。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::consume_buff;

pub const HERO: &str = "abysspact_traceless";
pub const NATIVE_MARK: &str = "abysspact_traceless_native";
pub const EDGE_STAT: &str = "abysspact_traceless_edge_stat";
pub const BLADE_GLOW: &str = "abysspact_traceless_blade_glow";
pub const STEALTH_BUFF: &str = "abysspact_traceless_stealth";
pub const HIT_ASK: &str = "abysspact_traceless_hit_ask";
pub const Q_CAST_ASK: &str = "abysspact_traceless_q_cast";
pub const W_ASK: &str = "abysspact_traceless_w_ask";
pub const R_CAST_VOICE: &str = "abysspact_traceless_r_voice";

pub const EDGE_CAP: u8 = 8;
pub const EDGE_PCT_PER_STACK: i32 = 7;
pub const OOC_STEALTH_TICKS: usize = 90; // 1.5s out of combat -> stealth
pub const Q_RESET_WINDOW: usize = 45;    // 0.75s kill window after Q cast

pub fn edge_attack_mult(stacks: u8) -> i32 {
    (stacks.min(EDGE_CAP) as i32) * EDGE_PCT_PER_STACK
}

#[derive(Clone, Default)]
struct TracelessPassive {
    voice: Voice,
    native_marked: bool,
    edge: u8,
    shown_edge: u8,
    last_hp: usize,
    last_combat_tick: usize,
    stealthed: bool,
    ambush_ready: bool,
    q_cast_tick: usize,
}

impl TracelessPassive {
    fn sync_edge(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if self.shown_edge == self.edge {
            return;
        }
        sim.entity_remove_buff(entity, EDGE_STAT);
        sim.entity_remove_buff(entity, BLADE_GLOW);
        for k in 1..=EDGE_CAP {
            sim.entity_remove_buff(entity, &format!("abysspact_traceless_edge_{k}"));
        }
        if self.edge > 0 {
            let mut st = BuffV1::named(EDGE_STAT);
            st.attack_mult = edge_attack_mult(self.edge);
            sim.add_buff(entity, &st);
            sim.add_buff(entity, &BuffV1::named(BLADE_GLOW));
            sim.add_buff(entity, &BuffV1::named(&format!("abysspact_traceless_edge_{}", self.edge)));
        }
        self.shown_edge = self.edge;
    }

    fn gain_edge(&mut self, sim: &mut StableSim<'_>, entity: usize, amount: u8) {
        let next = self.edge.saturating_add(amount).min(EDGE_CAP);
        if next != self.edge {
            self.edge = next;
            self.sync_edge(sim, entity);
            sim.play_sfx("abysspact_traceless_stack", entity, &InputTargetV1::target(entity));
        }
    }

    fn shatter_edge(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if self.edge == 0 {
            return;
        }
        self.edge = 0;
        self.sync_edge(sim, entity);
        sim.play_view_effect("abysspact_traceless_ink", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_view_effect("abysspact_traceless_quench", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_traceless_ink", entity, &InputTargetV1::target(entity));
        sim.play_sfx("abysspact_traceless_quench", entity, &InputTargetV1::target(entity));
    }

    fn break_stealth(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if self.stealthed {
            self.stealthed = false;
            sim.entity_remove_buff(entity, STEALTH_BUFF);
        }
    }
}

impl StablePassive for TracelessPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.native_marked = false;
        self.edge = 0;
        self.shown_edge = 0;
        self.last_hp = sim.get_entity(entity).map(|e| e.hp().0).unwrap_or(0);
        self.last_combat_tick = sim.tick();
        self.stealthed = false;
        self.ambush_ready = false;
        self.q_cast_tick = 0;
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(
        &mut self,
        sim: &mut StableSim<'_>,
        _player: usize,
        entity: usize,
        target: usize,
        damage: &mut usize,
    ) {
        self.last_combat_tick = sim.tick();
        if !sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            self.break_stealth(sim, entity);
            self.ambush_ready = false;
            return;
        }
        self.voice.play(sim, HERO, entity, Cue::Start);
        let cur_hp = sim.get_entity(entity).map(|e| e.hp().0).unwrap_or(0);
        if self.ambush_ready || self.stealthed {
            // First strike out of stealth: guaranteed +1 Edge & +50% damage!
            self.break_stealth(sim, entity);
            self.ambush_ready = false;
            *damage = damage.saturating_add(*damage / 2);
            self.gain_edge(sim, entity, 1);
            self.last_hp = cur_hp;
        } else if cur_hp >= self.last_hp {
            self.gain_edge(sim, entity, 1);
        }
    }

    fn on_damaged(
        &mut self,
        sim: &mut StableSim<'_>,
        _player: usize,
        entity: usize,
        _attacker: usize,
        damage: usize,
    ) {
        if damage == 0 {
            return;
        }
        self.last_combat_tick = sim.tick();
        self.break_stealth(sim, entity);
        self.ambush_ready = false;
        let cur_hp = sim.get_entity(entity).map(|e| e.hp().0).unwrap_or(0);
        // Shield-only hits do not drop cur_hp -> Edge preserved!
        if cur_hp < self.last_hp {
            self.shatter_edge(sim, entity);
        }
        self.last_hp = cur_hp;
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
            // Q「一线」kill immediately resets Q cooldown!
            if sim.tick() <= self.q_cast_tick + Q_RESET_WINDOW {
                sim.entity_reduce_cooldown(entity, SkillSlotV1::Skill, 10_000);
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.edge = 0;
        self.shown_edge = 0;
        self.stealthed = false;
        self.ambush_ready = false;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, cur_hp)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.hp().0)) else {
            return;
        };
        if !alive {
            self.edge = 0;
            self.shown_edge = 0;
            self.stealthed = false;
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
        if consume_buff(sim, entity, Q_CAST_ASK) {
            self.q_cast_tick = tick;
            self.last_combat_tick = tick;
        }
        if consume_buff(sim, entity, W_ASK) {
            // W「残影」grants 0.75s untargetable banish + 1.0s stealth!
            self.stealthed = true;
            self.ambush_ready = true;
            sim.entity_set_invisible(entity, 105);
            sim.add_buff(entity, &BuffV1::timed(STEALTH_BUFF, 105));
        }

        // Check real HP loss (shield hits leave cur_hp unchanged!)
        if cur_hp < self.last_hp {
            self.last_combat_tick = tick;
            self.break_stealth(sim, entity);
            self.ambush_ready = false;
            self.shatter_edge(sim, entity);
        }
        self.last_hp = cur_hp;

        // Skill hits (Q / R) stack Edge if unblemished!
        if consume_buff(sim, entity, HIT_ASK) {
            self.last_combat_tick = tick;
            self.break_stealth(sim, entity);
            self.ambush_ready = false;
            self.gain_edge(sim, entity, 1);
        }

        // 1.5s out of combat -> stealth
        if !self.stealthed && tick >= self.last_combat_tick + OOC_STEALTH_TICKS {
            self.stealthed = true;
            self.ambush_ready = true;
            sim.add_buff(entity, &BuffV1::named(STEALTH_BUFF));
        }
        if self.stealthed && tick % 12 == 0 {
            sim.entity_set_invisible(entity, 18);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_traceless:spotless", TracelessPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn edge_scales_seven_percent_up_to_eight_stacks() {
        assert_eq!(edge_attack_mult(0), 0);
        assert_eq!(edge_attack_mult(4), 28);
        assert_eq!(edge_attack_mult(8), 56);
        assert_eq!(edge_attack_mult(12), 56);
    }
}
