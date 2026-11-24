//! 无面 (`abysspact_faceless`) · 无面者 · 打野刺客
//!
//! 招牌机制「夺面」+ R「撕面」25% 生命斩杀:
//! - R「撕面」命中敌方英雄后挂短标记 `abysspact_faceless_r_exec_ask`：若目标当前生命 <= 25% 最大生命，
//!   立即施加高额真实斩杀伤害撕死目标并当场触发夺面。
//! - 参与击杀任意敌方英雄（击杀或 6 秒内助攻）立即触发 10 秒（600 ticks）「夺面」：
//!   * 通知显示层钩子 (`faceless_view::note_steal`) 把无面整身替换成被杀英雄的外观；
//!   * 模拟层挂上 `abysspact_faceless_shape`（10s）、黑影 `shroud`、白瓷裂纹 `cracks`、受害者定位套件
//!     (`abysspact_faceless_cls_{melee,range,mage,util,assassin}`) 与一次可释放的借用大招标记 `r_stolen`；
//!   * 10 秒到期时播放 `shards` 面具碎裂特效并恢复无面本体。

use std::collections::HashMap;
use mod_api_stable::*;

use crate::faceless_view;
use crate::voice::{Cue, Voice};
use crate::{consume_buff, has_buff};

pub const HERO: &str = "abysspact_faceless";
pub const SHAPE: &str = "abysspact_faceless_shape";
pub const SHROUD: &str = "abysspact_faceless_shroud";
pub const CRACKS: &str = "abysspact_faceless_cracks";
pub const R_STOLEN: &str = "abysspact_faceless_r_stolen";
pub const R_EXEC_ASK: &str = "abysspact_faceless_r_exec_ask";
pub const R_CAST_VOICE: &str = "abysspact_faceless_r_voice";

pub const MASK_TICKS: usize = 600; // 10 seconds
pub const MARK_WINDOW: usize = 360; // 6s assist window
pub const EXEC_PCT: usize = 25;

pub fn should_execute(cur: usize, max: usize) -> bool {
    max > 0 && cur > 0 && cur.saturating_mul(100) <= max.saturating_mul(EXEC_PCT)
}

pub fn victim_category(champ_id: &str) -> &'static str {
    faceless_view::category_of(champ_id).unwrap_or("melee")
}

#[derive(Clone, Default)]
struct FacelessPassive {
    voice: Voice,
    /// Enemy champion entity id -> (champion_name, last_touched_tick).
    touched: HashMap<usize, (String, usize)>,
    /// Tick when current Face-Steal expires (0 = not masked).
    mask_until: usize,
    mask_cat: Option<&'static str>,
    noted_view: bool,
}

impl FacelessPassive {
    fn clear_mask(&mut self, sim: &mut StableSim<'_>, entity: usize, play_shards: bool) {
        if self.mask_until == 0 {
            return;
        }
        self.mask_until = 0;
        sim.entity_remove_buff(entity, SHAPE);
        sim.entity_remove_buff(entity, SHROUD);
        sim.entity_remove_buff(entity, CRACKS);
        sim.entity_remove_buff(entity, R_STOLEN);
        for cat in ["melee", "range", "mage", "util", "assassin"] {
            sim.entity_remove_buff(entity, &format!("abysspact_faceless_cls_{cat}"));
        }
        self.mask_cat = None;
        if let Some((m, s)) = view_origin(sim) {
            faceless_view::note_end(m, s, entity, sim.tick());
        }
        if play_shards {
            sim.play_view_effect("abysspact_faceless_shards", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_sfx("abysspact_faceless_mask_crack", entity, &InputTargetV1::target(entity));
        }
    }

    fn steal_face(&mut self, sim: &mut StableSim<'_>, entity: usize, victim_name: &str) {
        if victim_name.is_empty() || victim_name == HERO {
            return;
        }
        self.clear_mask(sim, entity, false);
        let tick = sim.tick();
        self.mask_until = tick + MASK_TICKS;
        let cat = victim_category(victim_name);
        self.mask_cat = Some(cat);

        // Timed shape + shroud + cracks + class kit + 1 stolen ult charge
        sim.add_buff(entity, &BuffV1::timed(SHAPE, MASK_TICKS));
        let mut shroud = BuffV1::timed(SHROUD, MASK_TICKS);
        shroud.attack_mult = 15;
        shroud.attack_speed_mult = 20;
        shroud.move_speed_mult = 10;
        sim.add_buff(entity, &shroud);
        sim.add_buff(entity, &BuffV1::timed(CRACKS, MASK_TICKS));
        sim.add_buff(entity, &BuffV1::timed(&format!("abysspact_faceless_cls_{cat}"), MASK_TICKS));
        sim.add_buff(entity, &BuffV1::timed(R_STOLEN, MASK_TICKS));

        // Reset Q cooldown slightly for smooth kill-chain flow
        sim.entity_reduce_cooldown(entity, SkillSlotV1::Skill, 180);
        sim.play_sfx("abysspact_faceless_shroud_rise", entity, &InputTargetV1::target(entity));

        if let Some((m, s)) = view_origin(sim) {
            faceless_view::note_steal(m, s, entity, tick, victim_name);
        }
    }
}

fn view_origin(sim: &StableSim<'_>) -> Option<(u64, u64)> {
    let o = sim.sim_origin()?;
    let k = SimOriginKindV1::from_code(o.kind)?;
    matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
        .then_some((o.match_id, o.set_index))
}

impl StablePassive for FacelessPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.touched.clear();
        self.mask_until = 0;
        self.mask_cat = None;
        self.voice.on_spawn(sim, HERO, entity);
        if !self.noted_view {
            if let Some((m, s)) = view_origin(sim) {
                faceless_view::note_view(m, s);
                self.noted_view = true;
            }
        }
    }

    fn on_attack(
        &mut self,
        sim: &mut StableSim<'_>,
        _player: usize,
        entity: usize,
        target: usize,
        _damage: &mut usize,
    ) {
        let target_info = sim
            .get_entity(target)
            .and_then(|te| te.is_champion().then(|| te.name()));
        if let Some(maybe_name) = target_info {
            self.voice.play(sim, HERO, entity, Cue::Start);
            if let Some(name) = maybe_name {
                self.touched.insert(target, (name, sim.tick()));
            }
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        let name = sim.get_entity(victim).and_then(|e| e.is_champion().then(|| e.name()).flatten())
            .or_else(|| self.touched.get(&victim).map(|(n, _)| n.clone()));
        if let Some(vname) = name {
            self.touched.remove(&victim);
            self.voice.play(sim, HERO, entity, Cue::Kill);
            self.steal_face(sim, entity, &vname);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.touched.clear();
        self.mask_until = 0;
        self.mask_cat = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        if !self.noted_view {
            if let Some((m, s)) = view_origin(sim) {
                faceless_view::note_view(m, s);
                self.noted_view = true;
            }
        }
        let Some((alive, my_team)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.team())) else {
            return;
        };
        if !alive {
            if self.mask_until > 0 {
                self.clear_mask(sim, entity, false);
            }
            return;
        }
        let tick = sim.tick();

        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 1. Check R 25% HP execute marker on enemy champions
        let n_entities = sim.entity_count();
        let mut exec_targets = Vec::new();
        for i in 0..n_entities {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || e.team() == my_team || !e.is_alive() {
                continue;
            }
            let cid = e.id();
            if has_buff(sim, cid, R_EXEC_ASK) {
                let (cur, max) = e.hp();
                let name = e.name().unwrap_or_default();
                exec_targets.push((cid, cur, max, name));
            }
        }
        for (cid, cur, max, name) in exec_targets {
            sim.entity_remove_buff(cid, R_EXEC_ASK);
            if !name.is_empty() {
                self.touched.insert(cid, (name.clone(), tick));
            }
            if should_execute(cur, max) {
                // True-damage execute tearing off the victim's face immediately!
                sim.deal_damage_typed(entity, cid, max.max(9999), DamageTypeV1::Fixed, AttackTypeV1::Skill);
                self.touched.remove(&cid);
                self.voice.play(sim, HERO, entity, Cue::Kill);
                self.steal_face(sim, entity, &name);
            }
        }

        // 2. Check assist takedowns on recently touched enemies (6s window)
        let mut assist_victim: Option<(usize, String)> = None;
        self.touched.retain(|&vid, (vname, t0)| {
            if tick.saturating_sub(*t0) > MARK_WINDOW {
                return false;
            }
            let dead = sim.get_entity(vid).is_some_and(|e| !e.is_alive());
            if dead {
                if assist_victim.is_none() {
                    assist_victim = Some((vid, vname.clone()));
                }
                return false;
            }
            true
        });
        if let Some((_, vname)) = assist_victim {
            self.steal_face(sim, entity, &vname);
        }

        // 3. Expire 10s Face-Steal with shattering mask shards
        if self.mask_until > 0 && tick >= self.mask_until {
            self.clear_mask(sim, entity, true);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_faceless:mask", FacelessPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn execute_threshold_is_25_percent() {
        assert!(should_execute(250, 1000));
        assert!(should_execute(1, 1000));
        assert!(!should_execute(251, 1000));
        assert!(!should_execute(0, 1000));
    }
}
