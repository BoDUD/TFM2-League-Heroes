//! 赊命 (`abysspact_debtor`) · 赊命剑客 · 打野战士
//!
//! - 欠条：Q「讨债」、W「利息」打中敌方英雄时在他身上留 6 秒（`swap_t`）欠条 `debt_note`。
//! - Q 打在 `q_exec`% 血以下的人身上伤害 +`q_exec_bonus`%：数据在这一下伤害之前给目标挂 `q_hit`，
//!   `on_attack` 看到它就按挨打前的血量判断、直接加在这一下上（一个伤害数字）。
//! - R「换命」：数据里 R 在原生模式下是 3 tick 的 idle 动作，只挂待命标记 `r_arm`（`r_arm` tick）。待命期间
//!   被动每 tick 看：自己血量比例 ≤ `r_hp_max`%，`r_range` 内有欠条、血量比例 ≥ `r_foe_min`% 而且比他高的
//!   敌方英雄，才换（挑比例最高的那个）：播 `ult` 动作，`r_go` tick 后两人血量比例对调，两人头顶挂 6 秒倒计时。
//!   对方比例不比他高绝不换。待命到点没用上就把 R 的冷却退到只剩 `keep`。
//!   * 6 秒内对方死了，这条命就归他；没死就按 6 秒后两人当时的比例再对调一次（打残没打死，自己反而更残）。
//! - 胸口坠子里的命火随血量换档（`flame_100` / `flame_50` / `flame_25`）。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{animate, can_cast, consume_buff, dist_sq, has_buff, kit_param, refund_cooldown};

pub const HERO: &str = "abysspact_debtor";
pub const NATIVE_MARK: &str = "abysspact_debtor_native";
pub const DEBT_NOTE: &str = "abysspact_debtor_debt_note";
pub const Q_HIT_ASK: &str = "abysspact_debtor_q_hit";
pub const R_ARM: &str = "abysspact_debtor_r_arm";
pub const TIMER_RING: &str = "abysspact_debtor_timer_ring";
pub const FLAME_100: &str = "abysspact_debtor_flame_100";
pub const FLAME_50: &str = "abysspact_debtor_flame_50";
pub const FLAME_25: &str = "abysspact_debtor_flame_25";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub swap_t: usize,
    pub r_hp_max: usize,
    pub r_foe_min: usize,
    pub r_arm: usize,
    pub r_range: usize,
    pub r_go: usize,
    pub r_dur: usize,
    pub q_exec: usize,
    pub q_exec_bonus: usize,
    pub keep: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            swap_t: 360, r_hp_max: 35, r_foe_min: 60, r_arm: 600, r_range: 65_000, r_go: 14, r_dur: 40,
            q_exec: 30, q_exec_bonus: 50, keep: 60,
        }
    }
}

impl Params {
    pub fn parse(json: &str) -> Self {
        let d = Self::default();
        let g = |k: &str, v: usize| kit_param(json, k).unwrap_or(v);
        Self {
            swap_t: g("swap_t", d.swap_t), r_hp_max: g("r_hp_max", d.r_hp_max), r_foe_min: g("r_foe_min", d.r_foe_min),
            r_arm: g("r_arm", d.r_arm), r_range: g("r_range", d.r_range), r_go: g("r_go", d.r_go), r_dur: g("r_dur", d.r_dur),
            q_exec: g("q_exec", d.q_exec), q_exec_bonus: g("q_exec_bonus", d.q_exec_bonus), keep: g("keep", d.keep),
        }
    }
}

pub fn swapped_hp(my_hp: usize, my_max: usize, foe_hp: usize, foe_max: usize) -> (usize, usize) {
    if my_max == 0 || foe_max == 0 {
        return (my_hp, foe_hp);
    }
    let new_my = ((my_max as u128 * foe_hp as u128 + (foe_max as u128 / 2)) / foe_max as u128)
        .clamp(1, my_max as u128) as usize;
    let new_foe = ((foe_max as u128 * my_hp as u128 + (my_max as u128 / 2)) / my_max as u128)
        .clamp(1, foe_max as u128) as usize;
    (new_my, new_foe)
}

/// 血量比例（千分之几）。
pub fn ratio(hp: usize, max: usize) -> usize {
    if max == 0 { 0 } else { hp.saturating_mul(1000) / max }
}

/// 该不该换命：自己比例 ≤ r_hp_max%，对方 ≥ r_foe_min% 而且比自己高。
pub fn worth_swapping(p: &Params, my: usize, foe: usize) -> bool {
    my <= p.r_hp_max * 10 && foe >= p.r_foe_min * 10 && foe > my
}

pub fn flame_tier(cur_hp: usize, max_hp: usize) -> &'static str {
    if max_hp == 0 || cur_hp.saturating_mul(100) <= max_hp.saturating_mul(30) {
        FLAME_25
    } else if cur_hp.saturating_mul(100) <= max_hp.saturating_mul(65) {
        FLAME_50
    } else {
        FLAME_100
    }
}

#[derive(Clone, Copy)]
struct ActiveSwap {
    target: usize,
    end_tick: usize,
}

#[derive(Clone, Default)]
struct DebtorPassive {
    p: Params,
    voice: Voice,
    native_marked: bool,
    flame_shown: Option<&'static str>,
    active_swap: Option<ActiveSwap>,
    armed: Option<usize>,
    /// 换命动作已经开始：(对方, 到这一 tick 对调)。
    pending: Option<(usize, usize)>,
}

impl DebtorPassive {
    fn sync_flame(&mut self, sim: &mut StableSim<'_>, entity: usize, cur: usize, max: usize) {
        let want = flame_tier(cur, max);
        if self.flame_shown == Some(want) {
            return;
        }
        for f in [FLAME_100, FLAME_50, FLAME_25] {
            sim.entity_remove_buff(entity, f);
        }
        sim.add_buff(entity, &BuffV1::named(want));
        self.flame_shown = Some(want);
    }

    fn execute_swap(&mut self, sim: &mut StableSim<'_>, entity: usize, target: usize, is_return: bool) -> bool {
        let Some((my_alive, my_hp, my_max)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.hp().0, e.hp().1)) else {
            return false;
        };
        let Some((foe_alive, foe_hp, foe_max)) = sim.get_entity(target).map(|e| (e.is_alive(), e.hp().0, e.hp().1)) else {
            return false;
        };
        if !my_alive || !foe_alive || my_max == 0 || foe_max == 0 {
            return false;
        }
        let (new_my, new_foe) = swapped_hp(my_hp, my_max, foe_hp, foe_max);
        sim.entity_set_hp(entity, new_my);
        sim.entity_set_hp(target, new_foe);
        if is_return {
            sim.play_view_effect("abysspact_debtor_swap_return", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_view_effect("abysspact_debtor_swap_return", entity, &InputTargetV1::target(target), 0, 0, 0);
            sim.play_sfx("abysspact_debtor_swap_return", entity, &InputTargetV1::target(entity));
        } else {
            sim.play_view_effect("abysspact_debtor_swap", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_view_effect("abysspact_debtor_swap", entity, &InputTargetV1::target(target), 0, 0, 0);
            sim.play_view_effect("abysspact_debtor_life_flame", entity, &InputTargetV1::target(target), 0, 0, 0);
            sim.play_sfx("abysspact_debtor_swap", entity, &InputTargetV1::target(entity));
            sim.add_buff(entity, &BuffV1::timed(TIMER_RING, self.p.swap_t));
            sim.add_buff(target, &BuffV1::timed(TIMER_RING, self.p.swap_t));
        }
        true
    }

    /// 待命中找值得换的人：有欠条、在 r_range 内、比例 ≥ r_foe_min 而且比他高；挑比例最高的。
    fn pick(&self, sim: &StableSim<'_>, team: usize, at: (u64, u64), my: usize) -> Option<usize> {
        let r2 = (self.p.r_range as u64).saturating_mul(self.p.r_range as u64);
        let mut best: Option<(usize, usize)> = None;
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || !e.is_alive() || e.team() == team || dist_sq(at, e.pos()) > r2 {
                continue;
            }
            if !has_buff(sim, e.id(), DEBT_NOTE) {
                continue;
            }
            let (h, m) = e.hp();
            let pct = ratio(h, m);
            if worth_swapping(&self.p, my, pct) && best.is_none_or(|(_, b)| pct > b) {
                best = Some((e.id(), pct));
            }
        }
        best.map(|(id, _)| id)
    }
}

impl StablePassive for DebtorPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = Params::parse(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.native_marked = false;
        self.flame_shown = None;
        self.active_swap = None;
        self.armed = None;
        self.pending = None;
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, target: usize, damage: &mut usize) {
        let Some((champ, hp, max)) = sim.get_entity(target).map(|e| (e.is_champion(), e.hp().0, e.hp().1)) else {
            return;
        };
        if champ {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
        // Q 的这一下：按挨打前的血量判断斩杀加成
        if consume_buff(sim, target, Q_HIT_ASK) && max > 0 && hp.saturating_mul(100) <= max.saturating_mul(self.p.q_exec) {
            *damage = damage.saturating_add(damage.saturating_mul(self.p.q_exec_bonus) / 100);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
        if self.active_swap.is_some_and(|sw| sw.target == victim) {
            self.active_swap = None;
            sim.entity_remove_buff(entity, TIMER_RING);
            sim.play_view_effect("abysspact_debtor_absorb", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_sfx("abysspact_debtor_absorb", entity, &InputTargetV1::target(entity));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.active_swap = None;
        self.flame_shown = None;
        self.armed = None;
        self.pending = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, cur_hp, max_hp)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.hp().0, e.hp().1))
        else {
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
        self.sync_flame(sim, entity, cur_hp, max_hp);

        // 1. AI 按了 R：待命
        if consume_buff(sim, entity, R_ARM) {
            self.armed = Some(tick + self.p.r_arm);
        }

        // 2. 换命动作播到出手那一帧：再看一次值不值得，值得才换
        if let Some((target, at)) = self.pending {
            if tick >= at {
                self.pending = None;
                let foe = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| ratio(e.hp().0, e.hp().1));
                let my = ratio(cur_hp, max_hp);
                if foe.is_some_and(|f| f > my) && self.execute_swap(sim, entity, target, false) {
                    self.active_swap = Some(ActiveSwap { target, end_tick: tick + self.p.swap_t });
                }
            }
        }

        // 3. 待命中：自己够残、身边有张够满的欠条才出手
        if tick % 3 == 0 && self.pending.is_none() && self.active_swap.is_none() && self.armed.is_some() && can_cast(sim, entity) {
            if let Some(target) = self.pick(sim, my_team, my_pos, ratio(cur_hp, max_hp)) {
                self.armed = None;
                self.pending = Some((target, tick + self.p.r_go));
                animate(sim, entity, "ult", self.p.r_dur);
                sim.play_sfx("abysspact_debtor_foley_r", entity, &InputTargetV1::target(entity));
                self.voice.play(sim, HERO, entity, Cue::Ult);
            }
        }
        if self.armed.is_some_and(|t| tick >= t) {
            self.armed = None;
            refund_cooldown(sim, entity, SkillSlotV1::Ult, self.p.keep);
        }

        // 4. 赊来的命：6 秒内对方死了就归他，没死按当时的比例换回去
        if let Some(sw) = self.active_swap {
            let target_alive = sim.get_entity(sw.target).is_some_and(|e| e.is_alive());
            if !target_alive {
                self.active_swap = None;
                sim.entity_remove_buff(entity, TIMER_RING);
                sim.play_view_effect("abysspact_debtor_absorb", entity, &InputTargetV1::target(entity), 0, 0, 0);
                sim.play_sfx("abysspact_debtor_absorb", entity, &InputTargetV1::target(entity));
            } else if tick >= sw.end_tick {
                self.active_swap = None;
                sim.entity_remove_buff(entity, TIMER_RING);
                sim.entity_remove_buff(sw.target, TIMER_RING);
                self.execute_swap(sim, entity, sw.target, true);
            }
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_debtor:ledger", DebtorPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ratio_swap_preserves_percentages_and_nonzero_floor() {
        // 20% of 1000 vs 90% of 2000 -> 900 vs 400
        assert_eq!(swapped_hp(200, 1000, 1800, 2000), (900, 400));
        assert_eq!(swapped_hp(1, 1000, 1000, 1000).1, 1);
    }

    #[test]
    fn only_a_low_debtor_swaps_with_a_healthier_note() {
        let p = Params::default();
        assert!(worth_swapping(&p, 200, 900));
        // 自己不够残
        assert!(!worth_swapping(&p, 500, 900));
        // 对方不够满
        assert!(!worth_swapping(&p, 200, 500));
        // 对方比例不比他高：绝不换
        assert!(!worth_swapping(&p, 350, 340));
    }

    #[test]
    fn params_come_from_the_kit_file() {
        assert_eq!(Params::parse(&crate::kit_params_of(include_str!(
            "../../../abysspact/champion/abysspact_debtor.data_champion"
        ))), Params::default());
    }
}
