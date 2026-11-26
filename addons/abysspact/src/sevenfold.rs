//! 七弹 (`abysspact_sevenfold`) · 魔弹射手 · 下路射手
//!
//! 招牌机制「第七颗」：一轮 7 发，头顶 `count_0..7` 显示这一轮还剩几发。
//! - 只数真正的普攻（`on_base_attack`，一下普攻来一次）；Q「连发」看数据挂的 `q_shots` 算 3 发；R 的齐射不算。
//!   以前在 `on_attack` 里数，Q 的三枪、R 的六枪、魔弹自己、装备附加的伤害每一下都算一发：Q 一次算 6 发，
//!   R 打到一半还会多冒出一颗魔弹、多扣一次血。
//! - 只剩最后一发时给他挂 `seventh`。数据的普攻看到它，这一发不打瞄的人，换成深渊魔弹：身后睁开深渊之眼，
//!   9 万内随机一个敌方英雄，追踪弹拐着弯飞过去，真实伤害；同时挂 `fired7`。本包看到 `fired7`：9 万内有敌方英雄
//!   （魔弹真的出膛了）就扣他自己 8% 当前生命（不致死），然后装弹 1.2 秒（不能普攻），装完 7 发。
//! - W「装弹」：数据挂 `w_load`，下一发直接换成第七颗。
//! - R「七发齐射」：最后一发走同一份魔弹数据，挂 `r_fired7`：扣 8% 当前生命，不装弹，不动这一轮的计数。

use mod_api_stable::*;

use crate::oathbreaker::hp_after_burn;
use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_sevenfold";
pub const NATIVE_MARK: &str = "abysspact_sevenfold_native";
pub const Q_SHOTS_ASK: &str = "abysspact_sevenfold_q_shots";
pub const W_LOAD_ASK: &str = "abysspact_sevenfold_w_load";
pub const R_CAST_VOICE: &str = "abysspact_sevenfold_r_voice";
pub const RELOADING_BUFF: &str = "abysspact_sevenfold_reloading";
/// 下一发是第七颗（本包挂，数据的普攻看它、出膛时摘掉）。
pub const SEVENTH: &str = "abysspact_sevenfold_seventh";
/// 普攻的第七颗出膛了（数据挂）。
pub const FIRED7: &str = "abysspact_sevenfold_fired7";
/// R 的第七发出膛了（数据挂）。
pub const R_FIRED7: &str = "abysspact_sevenfold_r_fired7";

pub const CLIP_SIZE: u8 = 7;
pub const CURSE_RANGE: u64 = 90_000; // 9.0万
pub const RELOAD_TICKS: usize = 72; // 1.2s reload
pub const SELF_BURN_PCT: usize = 8;
/// Q「连发」算几发。
pub const Q_SHOTS: u8 = 3;

pub fn count_buff_name(n: u8) -> &'static str {
    match n {
        0 => "abysspact_sevenfold_count_0",
        1 => "abysspact_sevenfold_count_1",
        2 => "abysspact_sevenfold_count_2",
        3 => "abysspact_sevenfold_count_3",
        4 => "abysspact_sevenfold_count_4",
        5 => "abysspact_sevenfold_count_5",
        6 => "abysspact_sevenfold_count_6",
        _ => "abysspact_sevenfold_count_7",
    }
}

/// 打出 `shots` 发以后这一轮还剩几发：最后一发留给第七颗，所以最少剩 1。
pub fn after_shots(left: u8, shots: u8) -> u8 {
    left.saturating_sub(shots).max(1)
}

#[derive(Clone)]
struct SevenfoldPassive {
    voice: Voice,
    /// 这一轮还剩几发（7..=1，1 = 下一发是第七颗；装弹时是 0）。
    left: u8,
    reload_until: usize,
    shown_count: Option<u8>,
}

impl Default for SevenfoldPassive {
    fn default() -> Self {
        Self { voice: Voice::default(), left: CLIP_SIZE, reload_until: 0, shown_count: None }
    }
}

impl SevenfoldPassive {
    fn sync_count(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if self.shown_count == Some(self.left) {
            return;
        }
        for k in 0..=CLIP_SIZE {
            sim.entity_remove_buff(entity, count_buff_name(k));
        }
        sim.add_buff(entity, &BuffV1::named(count_buff_name(self.left)));
        self.shown_count = Some(self.left);
    }

    /// 打掉几发；剩最后一发就把第七颗装上。
    fn spend(&mut self, sim: &mut StableSim<'_>, entity: usize, shots: u8) {
        self.left = after_shots(self.left, shots);
        if self.left == 1 && !has_buff(sim, entity, SEVENTH) {
            sim.add_buff(entity, &BuffV1::named(SEVENTH));
            sim.play_sfx("abysspact_sevenfold_charge_ping", entity, &InputTargetV1::target(entity));
        }
        self.sync_count(sim, entity);
    }

    /// 魔弹出膛的代价：9 万内有敌方英雄（真的打出去了）就扣 8% 当前生命；普攻的第七颗还要装弹 1.2 秒。
    fn pay(&mut self, sim: &mut StableSim<'_>, entity: usize, reload: bool) {
        let Some((team, at, my_r, cur_hp)) =
            sim.get_entity(entity).map(|e| (e.team(), e.pos(), e.radius() as u64, e.hp().0))
        else {
            return;
        };
        let mut fired = false;
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() || !e.is_champion() || e.team() == team {
                continue;
            }
            let reach = CURSE_RANGE + my_r + e.radius() as u64;
            if dist_sq(at, e.pos()) <= reach.saturating_mul(reach) {
                fired = true;
                break;
            }
        }
        if fired {
            let next_hp = hp_after_burn(cur_hp, SELF_BURN_PCT);
            if next_hp < cur_hp {
                sim.entity_set_hp(entity, next_hp);
            }
        }
        if reload {
            sim.entity_remove_buff(entity, SEVENTH);
            self.left = 0;
            self.reload_until = sim.tick() + RELOAD_TICKS;
            sim.add_buff(entity, &BuffV1::timed(RELOADING_BUFF, RELOAD_TICKS));
            sim.apply_cc(entity, &CcV1::of_kind(CcKindV1::BlockAttack, RELOAD_TICKS as u64));
            self.sync_count(sim, entity);
        }
    }
}

impl StablePassive for SevenfoldPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.left = CLIP_SIZE;
        self.reload_until = 0;
        self.shown_count = None;
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_base_attack(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        if self.reload_until > sim.tick() {
            return;
        }
        // 第七颗自己出膛的这一下（数据摘 seventh、挂 fired7，两边谁先到都认得出）不再算一发
        if has_buff(sim, entity, SEVENTH) || has_buff(sim, entity, FIRED7) {
            return;
        }
        self.spend(sim, entity, 1);
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
        self.left = CLIP_SIZE;
        self.reload_until = 0;
        self.shown_count = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let alive = sim.get_entity(entity).is_some_and(|e| e.is_alive());
        if !alive {
            return;
        }
        let tick = sim.tick();
        if !has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }
        if self.shown_count.is_none() {
            self.sync_count(sim, entity);
        }

        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 第七颗出膛了：付代价
        if consume_buff(sim, entity, FIRED7) {
            self.pay(sim, entity, true);
        }
        if consume_buff(sim, entity, R_FIRED7) {
            self.pay(sim, entity, false);
        }

        // 装弹 1.2 秒到：装满 7 发
        if self.reload_until > 0 && tick >= self.reload_until {
            self.reload_until = 0;
            self.left = CLIP_SIZE;
            sim.entity_remove_buff(entity, RELOADING_BUFF);
            self.sync_count(sim, entity);
        }

        // Q「连发」：算 3 发
        if consume_buff(sim, entity, Q_SHOTS_ASK) && self.reload_until == 0 {
            self.spend(sim, entity, Q_SHOTS);
        }

        // W「装弹」：下一发直接是第七颗
        if consume_buff(sim, entity, W_LOAD_ASK) {
            self.reload_until = 0;
            sim.entity_remove_buff(entity, RELOADING_BUFF);
            self.left = 1;
            if !has_buff(sim, entity, SEVENTH) {
                sim.add_buff(entity, &BuffV1::named(SEVENTH));
            }
            self.sync_count(sim, entity);
            sim.play_sfx("abysspact_sevenfold_charge_ping", entity, &InputTargetV1::target(entity));
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_sevenfold:bullets", SevenfoldPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn six_shots_bring_the_seventh() {
        let mut left = CLIP_SIZE;
        for _ in 0..6 {
            left = after_shots(left, 1);
        }
        assert_eq!(left, 1, "第七发");
        // 再打也停在最后一发上（第七颗由数据打出，不在这里数）
        assert_eq!(after_shots(left, 1), 1);
    }

    #[test]
    fn the_volley_counts_three_and_never_skips_the_seventh() {
        assert_eq!(after_shots(CLIP_SIZE, Q_SHOTS), 4);
        assert_eq!(after_shots(4, Q_SHOTS), 1);
        assert_eq!(after_shots(2, Q_SHOTS), 1);
        // 一轮：两次 Q 加一下普攻 = 7 发里的前 6 发
        assert_eq!(after_shots(after_shots(after_shots(CLIP_SIZE, Q_SHOTS), Q_SHOTS), 1), 1);
    }

    #[test]
    fn count_names() {
        assert_eq!(count_buff_name(0), "abysspact_sevenfold_count_0");
        assert_eq!(count_buff_name(7), "abysspact_sevenfold_count_7");
    }
}
