//! 蜕甲 (`abysspact_carapace`) · 蜕壳甲虫骑士 · 上路战士
//!
//! 招牌机制「蜕壳」一条命三次形态（甲 → 虫 → 羽）+ 原地空壳嘲讽自爆:
//! - 第一形态「甲」（2 层壳）：护甲 +30、不死拦截（血归 1 立刻蜕壳）；头顶 `shells_2`。
//! - 第二形态「虫」（1 层壳）：最大生命 -20%、攻速 +15%、移速 +10%、不死拦截；显示钩子切 `bg_*`；头顶 `shells_1`。
//! - 第三形态「羽」（0 层壳）：最大生命 -40%、攻速 +30%、移速 +20%，Q 射程 2.5 万 → 4 万飞扑、R 3 万 → 6 万飞扑
//!   （`q_range` / `r_range` 两个官方 range_adjust）；显示钩子切 `wg_*`；头顶 `shells_0`；再死就是真的阵亡，复活重穿全甲。
//! - 被打死蜕壳：回到 40% 最大生命，0.5 秒免伤免控；旧壳立在原地（`shell_rattle`，图集排成 1.5 秒），嘲讽 3 万内的
//!   敌人 1.25 秒——嘲讽要有个嘲讽的人，壳不是单位，嘲讽到他本人（刚从壳里钻出来，就站在壳那儿）；1.5 秒后壳炸开，
//!   `100 + 8% 最大生命` 物理伤害。炸开排进效果队列（`abysspact_carapace:husk`），他这 1.5 秒里死了也照炸
//!   （死人的被动不跑，以前挂在被动里的壳就不炸了）；伤害记在他身上的 `husk:<炸开的 tick>:<伤害>` 记号里。
//! - R「羽化」：未到第三形态时主动蜕壳（保留生命比例），旧壳当场炸开 3 万击飞 0.75 秒 + `150 + 100% AD`，
//!   4 秒 +40% 攻速；第三形态时张翅 6 万飞扑落地击飞（数据）。
//! - W「甲鸣」：数据在出手那一下挂 3 tick 的 `w_heal`，这期间打出的每一下伤害按 30% 回血。

use mod_api_stable::*;
// 写死的技能距离在大地图版跟着乘 1.3
use game_places::skill_scale::sk;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_carapace";
pub const NATIVE_MARK: &str = "abysspact_carapace_native";
pub const FORM1_BUFF: &str = "abysspact_carapace_form1";
pub const FORM2_BUFF: &str = "abysspact_carapace_form2";
pub const FORM3_BUFF: &str = "abysspact_carapace_form3";
pub const INVULN_BUFF: &str = "abysspact_carapace_molt_inv";
pub const R_HASTE_BUFF: &str = "abysspact_carapace_r_haste";
pub const R_MOLT_ASK: &str = "abysspact_carapace_r_molt";
pub const R_CAST_VOICE: &str = "abysspact_carapace_r_voice";
/// 甲鸣出手时数据挂的标记：挂着的时候打出的伤害按 W_VAMP_PCT 回血。
pub const W_HEAL: &str = "abysspact_carapace_w_heal";
/// 空壳炸开的原生效果、记着伤害的记号前缀。
pub const HUSK_FX: &str = "abysspact_carapace:husk";
pub const HUSK_MARK: &str = "abysspact_carapace_husk";

pub const SHELL_RADIUS: u64 = 30_000;
pub const SHELL_EXPLODE_TICKS: usize = 90; // 1.5s
pub const SHELL_TAUNT_TICKS: u64 = 75; // 1.25s
pub const MOLT_INVULN_TICKS: usize = 30; // 0.5s
pub const R_AIRBORNE_TICKS: u64 = 45; // 0.75s
pub const R_HASTE_TICKS: usize = 240; // 4.0s
pub const W_VAMP_PCT: usize = 30;

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

pub fn husk_name(explode_at: usize, dmg: usize) -> String {
    format!("{HUSK_MARK}:{explode_at}:{dmg}")
}

pub fn parse_husk(name: &str) -> Option<(usize, usize)> {
    let (t, d) = name.strip_prefix(HUSK_MARK)?.strip_prefix(':')?.split_once(':')?;
    Some((t.parse().ok()?, d.parse().ok()?))
}

/// 甲鸣这一下伤害回多少血。
pub fn w_heal_amount(damage: usize) -> usize {
    damage.saturating_mul(W_VAMP_PCT) / 100
}

/// 圆心 `at`、半径 `r` 的圆碰到这个单位的身体（和数据里的圆一样，对方的半径算进去）。
fn touches(at: (u64, u64), r: u64, e: &StableEntity<'_, '_>) -> bool {
    let reach = r.saturating_add(e.radius() as u64);
    dist_sq(at, e.pos()) <= reach.saturating_mul(reach)
}

/// `at` 周围 `r` 内活着的敌人（不算塔）。
fn foes_in(sim: &StableSim<'_>, team: usize, at: (u64, u64), r: u64) -> Vec<usize> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.is_alive() && e.team() != team && !e.is_tower() && touches(at, r, e))
        .map(|e| e.id())
        .collect()
}

#[derive(Clone)]
struct CarapacePassive {
    voice: Voice,
    shells: u8,
    synced: bool,
}

impl Default for CarapacePassive {
    fn default() -> Self {
        Self { voice: Voice::default(), shells: 2, synced: false }
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

    #[allow(clippy::too_many_arguments)]
    fn perform_molt(&mut self, sim: &mut StableSim<'_>, entity: usize, pos: (u64, u64), my_team: usize,
                    cur_hp: usize, old_max_hp: usize, ad: usize, active_r: bool) {
        if self.shells == 0 {
            return;
        }
        let ratio_pct = if old_max_hp > 0 { (cur_hp.saturating_mul(100) / old_max_hp).clamp(1, 100) } else { 40 };
        self.shells -= 1;
        self.sync_form(sim, entity);

        // 钻出来的 0.5 秒：免伤免控
        let mut inv = BuffV1::timed(INVULN_BUFF, MOLT_INVULN_TICKS);
        inv.damaged_reduce = 100;
        inv.cc_immune = true;
        sim.add_buff(entity, &inv);

        // 被打死蜕壳回到新最大生命的 40%；R 主动蜕壳保留生命比例
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

        if active_r {
            // R「羽化」：旧壳当场炸开，3 万击飞 0.75 秒 + 150 + 100% AD，4 秒 +40% 攻速
            let mut haste = BuffV1::timed(R_HASTE_BUFF, R_HASTE_TICKS);
            haste.attack_speed_mult = 40;
            sim.entity_remove_buff(entity, R_HASTE_BUFF);
            sim.add_buff(entity, &haste);
            sim.play_view_effect("abysspact_carapace_molt_burst", entity, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
            sim.play_sfx("abysspact_carapace_shell_burst", entity, &InputTargetV1::pos(pos.0, pos.1));
            let dmg = r_burst_damage(ad);
            for vid in foes_in(sim, my_team, pos, sk(SHELL_RADIUS)) {
                sim.deal_damage_typed(entity, vid, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
                sim.apply_cc(vid, &CcV1::of_kind(CcKindV1::Airborne, R_AIRBORNE_TICKS));
            }
        } else {
            // 被打死蜕壳：空壳立 1.5 秒，嘲讽 3 万内的敌人 1.25 秒（嘲讽到他本人），然后炸开
            sim.play_view_effect("abysspact_carapace_shell_rattle", entity, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
            sim.play_view_effect("abysspact_carapace_taunt_glint", entity, &InputTargetV1::pos(pos.0, pos.1), 0, 0, 0);
            sim.play_sfx("abysspact_carapace_shell_rattle", entity, &InputTargetV1::pos(pos.0, pos.1));
            let mut taunt = CcV1::of_kind(CcKindV1::Taunt, SHELL_TAUNT_TICKS);
            taunt.target = entity;
            for vid in foes_in(sim, my_team, pos, sk(SHELL_RADIUS)) {
                sim.apply_cc(vid, &taunt);
            }
            let explode_at = sim.tick() + SHELL_EXPLODE_TICKS;
            sim.add_buff(entity, &BuffV1::timed(&husk_name(explode_at, shell_explosion_damage(old_max_hp)),
                                                SHELL_EXPLODE_TICKS + 30));
            sim.queue_effect(HUSK_FX, AttackTypeV1::Skill, entity, &InputTargetV1::pos(pos.0, pos.1), SHELL_EXPLODE_TICKS);
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
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, target: usize, damage: &mut usize) {
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
        // 甲鸣：这一下伤害按 30% 回血
        if has_buff(sim, entity, W_HEAL) {
            let heal = w_heal_amount(*damage);
            if heal > 0 {
                sim.heal(entity, entity, heal);
            }
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
        if !alive {
            return;
        }
        if !has_buff(sim, entity, NATIVE_MARK) {
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
        // 致命一击被 undying 拦下（生命停在 1）：蜕壳
        if self.shells > 0 && cur_hp <= 2 {
            self.perform_molt(sim, entity, pos, my_team, cur_hp, max_hp, ad, false);
        }
    }
}

/// 空壳炸开：排进效果队列 1.5 秒后跑（他死了也照跑），伤害从他身上的记号里读。
#[derive(Debug)]
struct HuskBlast;

impl StableEffectType for HuskBlast {
    fn apply(&self, sim: &mut StableSim<'_>, _seed: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Pos) {
            return;
        }
        let at = (input.x, input.y);
        let tick = sim.tick();
        let Some((team, alive, max_hp, marks)) = sim.get_entity(caster).map(|e| {
            let marks: Vec<(String, (usize, usize))> = (0..e.buff_count())
                .filter_map(|i| e.buff_at(i))
                .filter_map(|b| parse_husk(b.name()).map(|h| (b.name().to_string(), h)))
                .collect();
            (e.team(), e.is_alive(), e.hp().1, marks)
        }) else {
            return;
        };
        // 这一 tick 该炸的那个壳；找不到（记号被清了）就按他现在的最大生命算
        let found = marks.iter().filter(|(_, (t, _))| *t <= tick).min_by_key(|(_, (t, _))| tick - *t);
        let dmg = found.map_or_else(|| shell_explosion_damage(max_hp), |(_, (_, d))| *d);
        if alive {
            if let Some((name, _)) = found {
                sim.entity_remove_buff(caster, name);
            }
        }
        sim.play_view_effect("abysspact_carapace_shell_explode", caster, &input, 0, 0, 0);
        sim.play_sfx("abysspact_carapace_shell_burst", caster, &input);
        for vid in foes_in(sim, team, at, sk(SHELL_RADIUS)) {
            sim.deal_damage_typed(caster, vid, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
        }
    }
}

/// 第三形态的射程（官方的 range_adjust）：Q 飞扑 +1.5 万（到 4 万），R 飞扑 +3 万（到 6 万）。
#[derive(Debug)]
struct Form3Range(u64);

impl StableEffectType for Form3Range {
    fn apply(&self, _sim: &mut StableSim<'_>, _seed: u64, _caster: usize, _input: InputTargetV1) {}
    fn may_adjust_range(&self) -> bool {
        true
    }
    fn range_adjust(&self, caster: &StableEntityView<'_>, _target: &StableEntityView<'_>) -> u64 {
        if caster.has_buff(FORM3_BUFF) { self.0 } else { 0 }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_carapace:molt", CarapacePassive::default());
    module.add_native_effect("abysspact_carapace:q_range", Form3Range(15_000));
    module.add_native_effect("abysspact_carapace:r_range", Form3Range(30_000));
    module.add_native_effect(HUSK_FX, HuskBlast);
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

    #[test]
    fn the_husk_mark_carries_its_tick_and_damage() {
        let name = husk_name(123_456, 260);
        assert!(name.len() <= BUFF_NAME_CAP, "{name}");
        assert_eq!(parse_husk(&name), Some((123_456, 260)));
        assert_eq!(parse_husk("abysspact_carapace_shells_0"), None);
    }

    #[test]
    fn the_resonate_heals_thirty_percent_of_each_hit() {
        assert_eq!(w_heal_amount(200), 60);
        assert_eq!(w_heal_amount(0), 0);
    }
}
