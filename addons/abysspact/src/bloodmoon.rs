//! 血月 (`abysspact_bloodmoon`) · 狼人猎魔人 · 上路战士
//!
//! 招牌机制「月相」：人形 / 狼形两套身体，W 来回切换；R 血月化成 1.3 倍巨狼 8 秒。
//! - 普攻的射程是狼形的近战 2.6 万；人形时本包的 `abysspact_bloodmoon:human_range` 再加 1.9 万（官方的
//!   range_adjust，AI 和各处的射程判断都认），人形就是 4.5 万的银弩。
//! - 狼形（挂 `abysspact_bloodmoon_wolf`）：攻速 +30%、吸血 10%，Q 换成扑杀；显示钩子把动作换成同图集里的 `wf_*`。
//! - 巨狼（`abysspact_bloodmoon_giant`，8 秒，`hd.rs` 的 FORMS 放大到 1.3 倍）：真正的普攻打中时，他身边 1.5 万内
//!   （两边的身体都算）其余的敌人各吃一下 100% 攻击力，播 `giant_claw` 爪痕和 `giant_sweep`。
//!   只认普攻：`on_base_attack` 记下「出手了」，接下来的那一下命中才劈；技能的命中不劈。劈出去的伤害引擎下一 tick
//!   才结算，结算时也会回到 `on_attack`——记下自己排的那几下，回来时直接跳过（以前会被当成新的普攻接着劈，
//!   两个挨得近的敌人互相劈个不停）。
//! - 狼形不说人话，只有低吼。

use mod_api_stable::*;
// 写死的技能距离在大地图版跟着乘 1.3
use game_places::skill_scale::sk;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_bloodmoon";
pub const WOLF_BUFF: &str = "abysspact_bloodmoon_wolf";
pub const GIANT_BUFF: &str = "abysspact_bloodmoon_giant";
pub const R_CAST_VOICE: &str = "abysspact_bloodmoon_r_voice";
/// 人形加射程的原生效果（普攻最外层 Combine 的最后一项）。
pub const HUMAN_RANGE: &str = "abysspact_bloodmoon:human_range";
/// 巨狼顺劈的半径：他身边 1.5 万，两边的身体另算（和数据里的圆一样）。
pub const CLEAVE_RADIUS: u64 = 15_000;
/// 人形比狼形多的射程：狼形近战 2.6 万，人形 4.5 万。
pub const HUMAN_BONUS_RANGE: u64 = 19_000;
/// 普攻出手后多少 tick 内的第一下命中算这一下普攻（出手点在 17 tick，攻速再慢也够）。
pub const AUTO_WINDOW: usize = 24;
/// 自己排下的劈砍：排下后这么多 tick 内回到 `on_attack` 的都算自己的。
pub const OWN_HIT_WINDOW: usize = 3;

/// 人形 / 狼形两套身体的动作名对照：狼形时 `idle` 换成 `wf_idle`，变回人形时换回来。
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

/// 这一下命中是不是自己前几个 tick 排下的劈砍。
fn is_own_hit(own: &[(usize, usize)], target: usize, tick: usize) -> bool {
    own.iter().any(|&(t, id)| id == target && tick >= t && tick - t <= OWN_HIT_WINDOW)
}

/// 普攻刚出手（`auto_at` 是出手的 tick），这一下命中算它的。
fn auto_fresh(auto_at: Option<usize>, tick: usize) -> bool {
    auto_at.is_some_and(|t| tick >= t && tick - t <= AUTO_WINDOW)
}

/// 两个身体边缘之间不超过 `r`（中心距离减去两边的半径）。
fn within(a: (u64, u64), ar: u64, b: (u64, u64), br: u64, r: u64) -> bool {
    let reach = r.saturating_add(ar).saturating_add(br);
    dist_sq(a, b) <= reach.saturating_mul(reach)
}

#[derive(Clone, Default)]
struct BloodmoonPassive {
    voice: Voice,
    /// 最近一次普攻出手的 tick，等它的命中来劈。
    auto_at: Option<usize>,
    /// 同一 tick 里引擎先报了命中、后报出手时，先记下这一下：(tick, 目标)。
    early_hit: Option<(usize, usize)>,
    /// 自己排下的劈砍：(排下的 tick, 目标)。
    own_hits: Vec<(usize, usize)>,
}

impl BloodmoonPassive {
    fn is_wolf_form(sim: &StableSim<'_>, entity: usize) -> bool {
        has_buff(sim, entity, WOLF_BUFF) || has_buff(sim, entity, GIANT_BUFF)
    }

    fn reset(&mut self) {
        self.auto_at = None;
        self.early_hit = None;
        self.own_hits.clear();
    }

    /// 巨狼的普攻打中了 `target`：他身边其余的敌人各吃一下 100% 攻击力。
    fn cleave(&mut self, sim: &mut StableSim<'_>, entity: usize, target: usize) {
        if !has_buff(sim, entity, GIANT_BUFF) {
            return;
        }
        let Some((team, at, my_r, ad)) =
            sim.get_entity(entity).map(|e| (e.team(), e.pos(), e.radius() as u64, e.stat().attack))
        else {
            return;
        };
        let tick = sim.tick();
        let mut others = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            let id = e.id();
            if id == target || id == entity || !e.is_alive() || e.team() == team || e.is_tower() || !e.is_targetable() {
                continue;
            }
            if within(at, my_r, e.pos(), e.radius() as u64, sk(CLEAVE_RADIUS)) {
                others.push(id);
            }
        }
        sim.play_view_effect("abysspact_bloodmoon_giant_claw", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_bloodmoon_giant_sweep", entity, &InputTargetV1::target(entity));
        for id in others {
            if sim.deal_damage_typed(entity, id, ad, DamageTypeV1::Ad, AttackTypeV1::BaseAttack) {
                self.own_hits.push((tick, id));
            }
        }
    }
}

impl StablePassive for BloodmoonPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.reset();
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_base_attack(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let tick = sim.tick();
        if let Some((t, target)) = self.early_hit.take() {
            if t == tick {
                self.auto_at = None;
                self.cleave(sim, entity, target);
                return;
            }
        }
        self.auto_at = Some(tick);
    }

    fn on_attack(
        &mut self,
        sim: &mut StableSim<'_>,
        _player: usize,
        entity: usize,
        target: usize,
        _damage: &mut usize,
    ) {
        let tick = sim.tick();
        self.own_hits.retain(|&(t, _)| tick <= t + OWN_HIT_WINDOW);
        if is_own_hit(&self.own_hits, target, tick) {
            return;
        }
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            if Self::is_wolf_form(sim, entity) {
                // 狼形不说话，只有低吼
                if tick % 180 < 60 {
                    sim.play_sfx("abysspact_bloodmoon_wolf_growl", entity, &InputTargetV1::target(entity));
                }
            } else {
                self.voice.play(sim, HERO, entity, Cue::Start);
            }
        }
        if auto_fresh(self.auto_at, tick) {
            self.auto_at = None;
            self.cleave(sim, entity, target);
        } else {
            self.early_hit = Some((tick, target));
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
        self.reset();
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }
    }
}

/// 人形的银弩：狼形、巨狼都不在身上时，普攻的射程加 1.9 万。
#[derive(Debug)]
struct HumanRange;

impl StableEffectType for HumanRange {
    fn apply(&self, _sim: &mut StableSim<'_>, _seed: u64, _caster: usize, _input: InputTargetV1) {}

    fn may_adjust_range(&self) -> bool {
        true
    }

    fn range_adjust(&self, caster: &StableEntityView<'_>, _target: &StableEntityView<'_>) -> u64 {
        if caster.has_buff(WOLF_BUFF) || caster.has_buff(GIANT_BUFF) {
            0
        } else {
            HUMAN_BONUS_RANGE
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_bloodmoon:phases", BloodmoonPassive::default());
    module.add_native_effect(HUMAN_RANGE, HumanRange);
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

    #[test]
    fn own_cleave_hits_are_recognised_for_a_few_ticks_only() {
        let own = [(100, 7), (100, 9)];
        // 下一 tick 结算回来：是自己的
        assert!(is_own_hit(&own, 7, 101));
        assert!(is_own_hit(&own, 9, 100 + OWN_HIT_WINDOW));
        // 别的目标、太久以后的同一个目标：不是
        assert!(!is_own_hit(&own, 8, 101));
        assert!(!is_own_hit(&own, 7, 101 + OWN_HIT_WINDOW));
        assert!(!is_own_hit(&[], 7, 101));
    }

    #[test]
    fn only_a_hit_right_after_an_attack_counts_as_the_attack() {
        assert!(auto_fresh(Some(500), 500));
        assert!(auto_fresh(Some(500), 500 + AUTO_WINDOW));
        assert!(!auto_fresh(Some(500), 501 + AUTO_WINDOW));
        assert!(!auto_fresh(Some(500), 499));
        assert!(!auto_fresh(None, 500));
    }

    #[test]
    fn the_cleave_counts_both_bodies() {
        // 中心相距 2.7 万：1.5 万 + 他 6000 + 对方 6000 正好够到
        assert!(within((0, 0), 6_000, (27_000, 0), 6_000, CLEAVE_RADIUS));
        assert!(!within((0, 0), 6_000, (27_001, 0), 6_000, CLEAVE_RADIUS));
    }

    #[test]
    fn the_kit_attack_is_wolf_reach_plus_the_human_bonus() {
        // 生成好的技能文件：普攻射程是狼形近战 2.6 万，普攻最外层带着 human_range；人形加上本包的 1.9 万正好是设计的 4.5 万
        let kit = include_str!("../../../abysspact/champion/abysspact_bloodmoon.data_champion");
        let attack = &kit[kit.find("\"attack\": {").expect("attack action")..];
        let attack = &attack[..attack.find("\"skill\": {").expect("skill action after attack")];
        let range: u64 = attack
            .split("\"range\": ")
            .nth(1)
            .and_then(|r| r.split(|c: char| !c.is_ascii_digit()).next())
            .and_then(|n| n.parse().ok())
            .expect("attack range");
        assert_eq!(range, 26_000, "狼形的近战射程");
        assert!(attack.contains(&format!("\"effect_ref\": \"{HUMAN_RANGE}\"")), "普攻带着人形加射程的原生效果");
        assert_eq!(range + HUMAN_BONUS_RANGE, 45_000, "人形银弩 4.5 万");
    }
}
