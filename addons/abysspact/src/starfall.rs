//! 陨夜 (`abysspact_starfall`) · 观星少女 · 下路法术射手
//!
//! 招牌机制「坠星」延迟落点黑星 + 3 万最小射程盲区:
//! - 普攻不在身边直出，而是 0.5 秒（30 ticks）后从天落下黑星砸中 1.5 万范围（主目标 100%，溅射 60%）。
//! - 代价「落不到脚边」：当敌方英雄贴到 3.0 万以内时，黑星无法落在自己脚边——贴脸普攻直接落空并削减伤害，
//!   迫使陨夜立刻用 W「遁星」后撤 4 万并把近身敌人击退 1.5 万！
//! - 斗篷星图与星盘法杖环常驻闪烁 (`star_ring`)，语音随交手/大招/击杀/复活/倒地触发。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq};

pub const HERO: &str = "abysspact_starfall";
pub const NATIVE_MARK: &str = "abysspact_starfall_native";
pub const STAR_RING: &str = "abysspact_starfall_star_ring";
pub const R_CAST_VOICE: &str = "abysspact_starfall_r_voice";

pub const MIN_ATTACK_RANGE: u64 = 30_000; // 3.0万 deadzone

pub fn in_deadzone(my_pos: (u64, u64), target_pos: (u64, u64)) -> bool {
    dist_sq(my_pos, target_pos) < MIN_ATTACK_RANGE * MIN_ATTACK_RANGE
}

#[derive(Clone, Default)]
struct StarfallPassive {
    voice: Voice,
    native_marked: bool,
}

impl StablePassive for StarfallPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.native_marked = false;
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
        let Some((my_pos, t_info)) = sim.get_entity(entity).and_then(|me| {
            sim.get_entity(target)
                .map(|te| (me.pos(), (te.is_champion(), te.pos())))
        }) else {
            return;
        };
        let (is_champ, t_pos) = t_info;
        if is_champ {
            self.voice.play(sim, HERO, entity, Cue::Start);
            // Cost: stars cannot fall within 3.0万 of Starfall's own feet -> point-blank basic hits whiff!
            if in_deadzone(my_pos, t_pos) {
                *damage = 0;
            }
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some(alive) = sim.get_entity(entity).map(|e| e.is_alive()) else {
            return;
        };
        if !alive {
            return;
        }
        if !self.native_marked {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
            sim.add_buff(entity, &BuffV1::named(STAR_RING));
            self.native_marked = true;
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_starfall:starfall", StarfallPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn deadzone_enforces_three_wan_minimum_range() {
        assert!(in_deadzone((100_000, 100_000), (120_000, 100_000)));
        assert!(!in_deadzone((100_000, 100_000), (135_000, 100_000)));
    }
}
