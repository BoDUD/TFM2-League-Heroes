//! 血月 (`abysspact_bloodmoon`) · 狼人猎魔人 · 上路战士
//!
//! 招牌机制「月相」双形态切换 + 大招 1.3 倍血月巨狼:
//! - 人形（默认）：远程银弩 4.5 万 + Q 三连银矢；狼形（挂 `abysspact_bloodmoon_wolf`）：近战 2.6 万 +30% 攻速 +10% 吸血 + Q 扑杀。
//! - 显示钩子 (`game_places::hook::add`) 在 `wolf` 或 `giant` 状态把动作无缝切成同图集里的 `wf_*` 狼形动画；
//!   大招 `abysspact_bloodmoon_giant` 同时通过 `hd.rs` `FORMS` 放大至 1.3 倍巨狼体型！
//! - 巨狼期间（8 秒）：每次普攻对目标周围 1.5 万内其余敌人造成 100% 攻击力顺劈伤害并播 `giant_claw` 爪痕与 `giant_sweep` 音效。
//! - 语音规范：人形说人话（配音），狼形不说话只发低吼/巨狼长嚎。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_bloodmoon";
pub const WOLF_BUFF: &str = "abysspact_bloodmoon_wolf";
pub const GIANT_BUFF: &str = "abysspact_bloodmoon_giant";
pub const R_CAST_VOICE: &str = "abysspact_bloodmoon_r_voice";
pub const CLEAVE_RADIUS: u64 = 15_000;

/// Animation tag mapper for Bloodmoon's Human <-> Wolf dual-body sheet.
pub fn anim_for(cur: &str, is_wolf: bool) -> Option<&'static str> {
    if is_wolf {
        match cur {
            "idle" => Some("wf_idle"),
            "run" => Some("wf_run"),
            "attack" => Some("wf_attack"),
            "skill" => Some("wf_skill"),
            "skill2" => Some("wf_skill2"),
            "ult" => Some("wf_ult"),
            "hit" => Some("wf_hit"),
            "dead" => Some("wf_dead"),
            _ => None,
        }
    } else {
        match cur {
            "wf_idle" => Some("idle"),
            "wf_run" => Some("run"),
            "wf_attack" => Some("attack"),
            "wf_skill" => Some("skill"),
            "wf_skill2" => Some("skill2"),
            "wf_ult" => Some("ult"),
            "wf_hit" => Some("hit"),
            "wf_dead" => Some("dead"),
            _ => None,
        }
    }
}

#[derive(Clone, Default)]
struct BloodmoonPassive {
    voice: Voice,
    cleaving: bool,
}

impl BloodmoonPassive {
    fn is_wolf_form(sim: &StableSim<'_>, entity: usize) -> bool {
        has_buff(sim, entity, WOLF_BUFF) || has_buff(sim, entity, GIANT_BUFF)
    }
}

impl StablePassive for BloodmoonPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.cleaving = false;
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
        if self.cleaving {
            return;
        }
        let Some((my_team, ad)) = sim.get_entity(entity).map(|e| (e.team(), e.stat().attack)) else {
            return;
        };
        let Some((tpos, is_champ)) = sim.get_entity(target).map(|e| (e.pos(), e.is_champion())) else {
            return;
        };
        if is_champ {
            if Self::is_wolf_form(sim, entity) {
                // Wolf form growls instead of speaking human lines
                if sim.tick() % 180 < 60 {
                    sim.play_sfx("abysspact_bloodmoon_wolf_growl", entity, &InputTargetV1::target(entity));
                }
            } else {
                self.voice.play(sim, HERO, entity, Cue::Start);
            }
        }

        // Giant Blood Moon 8s: auto-attacks cleave ALL other enemies within 1.5万!
        if has_buff(sim, entity, GIANT_BUFF) {
            let r2 = CLEAVE_RADIUS * CLEAVE_RADIUS;
            let mut others = Vec::new();
            let n = sim.entity_count();
            for i in 0..n {
                let Some(e) = sim.entity_at(i) else { continue };
                let eid = e.id();
                if eid == target || !e.is_alive() || e.team() == my_team || e.is_tower() {
                    continue;
                }
                if dist_sq(tpos, e.pos()) <= r2 {
                    others.push(eid);
                }
            }
            if !others.is_empty() {
                self.cleaving = true;
                sim.play_view_effect("abysspact_bloodmoon_giant_claw", entity, &InputTargetV1::target(target), 0, 0, 0);
                sim.play_sfx("abysspact_bloodmoon_giant_sweep", entity, &InputTargetV1::target(target));
                for oid in others {
                    sim.deal_damage_typed(entity, oid, ad, DamageTypeV1::Ad, AttackTypeV1::BaseAttack);
                }
                self.cleaving = false;
            }
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            if Self::is_wolf_form(sim, entity) {
                sim.play_sfx("abysspact_bloodmoon_wolf_growl", entity, &InputTargetV1::target(entity));
            } else {
                self.voice.play(sim, HERO, entity, Cue::Kill);
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_bloodmoon:phases", BloodmoonPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wolf_and_human_anim_tags_roundtrip() {
        for base in ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"] {
            let wf = anim_for(base, true).expect("human -> wolf");
            assert_eq!(wf, format!("wf_{base}"));
            assert_eq!(anim_for(wf, false), Some(base));
            assert_eq!(anim_for(wf, true), None);
            assert_eq!(anim_for(base, false), None);
        }
    }
}
