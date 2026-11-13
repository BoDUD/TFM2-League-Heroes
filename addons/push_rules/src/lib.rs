//! 推人、拉人的共用规则（2026-11-13，用户：「沙皇的反推 好像推不到人 整体检查一下各个推的逻辑」）。
//!
//! - **韧性**：引擎把每种控制的时长按目标的韧性缩短，x (100 - 韧性) / 100，强制位移（击退、拉人、拖人都是 ForceMove）也一样
//!   （`.claude/skills/tfm2-hero-mod/references/champion-data.md`，读的 game_core）。强制位移走的是「速度 x tick」，tick 短了
//!   路就短：带 30% 韧性的人只被推出七成（4+6 的出装里 66 个英雄有 20%～30% 韧性的装备）。英雄联盟的位移不吃韧性：这里按
//!   目标的韧性把时长放长，缩短以后正好走满（[`full_ticks`]），附加包的强制位移、击退、抓、拉都走这里（[`force_move_full`]、
//!   [`knockback_full`]、[`grab_full`]、[`pull_full`]）。
//! - **击飞打断位移**（同一份笔记）：给正在位移的单位上击飞，位移就停了——要一起上，先击飞再推。
//! - **被按住的不挪**：眩晕、定身、击飞、嘲讽、恐惧、魅惑（[`HELD`]，李青 W 的 `HELD`）时宿主停下他的强制位移。
//!
//! 推人的附加包靠「到点就算到了」的（撞墙晕）现在先看他是不是真的到了（[`moving`] / 各包自己的落点）。

use mod_api_stable::*;

/// 按住一个单位、宿主停下他的强制位移的控制。
pub const HELD: [CcKindV1; 6] =
    [CcKindV1::Bind, CcKindV1::Stun, CcKindV1::Airborne, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];

/// 他身上所有效果的韧性加起来（4+6 的装备、符文、技能的 buff）。
pub fn toughness(u: &StableEntity<'_, '_>) -> usize {
    (0..u.buff_count()).filter_map(|i| u.buff_at(i)).map(|b| b.toughness).sum()
}

/// `id` 的韧性（找不到他就是 0）。
pub fn toughness_of(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |u| toughness(&u))
}

/// 要一个控制在目标身上留满 `ticks`，按他的韧性 `toughness` 放长到的时长：引擎乘 (100 - 韧性) / 100，放长到
/// ceil(ticks x 100 / (100 - 韧性))，缩短以后不少于 `ticks`。韧性到 100 的什么控制都留不住：None。
pub fn full_ticks(ticks: usize, toughness: usize) -> Option<usize> {
    let keep = 100usize.saturating_sub(toughness);
    (keep > 0).then(|| (ticks * 100).div_ceil(keep))
}

/// 强制位移 `cc`（ForceMove：`dx`/`dy` 定方向，速度 x tick 是路），按 `id` 的韧性放长时长；韧性到 100 的不推，返回 false。
pub fn force_move_full(sim: &mut StableSim<'_>, id: usize, mut cc: CcV1) -> bool {
    let Some(ticks) = full_ticks(cc.tick as usize, toughness_of(sim, id)) else { return false };
    cc.tick = ticks as u64;
    sim.apply_cc(id, &cc);
    true
}

/// 引擎的击退（从 `caster` 往外推 `speed` x `ticks`），按 `target` 的韧性放长。
pub fn knockback_full(sim: &mut StableSim<'_>, caster: usize, target: usize, speed: usize, ticks: usize) -> bool {
    let Some(t) = full_ticks(ticks, toughness_of(sim, target)) else { return false };
    sim.entity_knockback(caster, target, speed, t)
}

/// 引擎的抓（往 `caster` 拽，`ticks` 是 0 就一直拽到），按 `target` 的韧性放长；拽到为止的不用放长。
pub fn grab_full(sim: &mut StableSim<'_>, caster: usize, target: usize, speed: usize, ticks: usize) -> bool {
    let t = if ticks == 0 { Some(0) } else { full_ticks(ticks, toughness_of(sim, target)) };
    let Some(t) = t else { return false };
    sim.entity_grab(caster, target, speed, t)
}

/// 引擎的拉（往 `caster` 拉 `speed` x `ticks`），按 `target` 的韧性放长。
pub fn pull_full(sim: &mut StableSim<'_>, caster: usize, target: usize, speed: usize, ticks: usize) -> bool {
    let Some(t) = full_ticks(ticks, toughness_of(sim, target)) else { return false };
    sim.entity_pull(caster, target, speed, t)
}

fn has_kind(u: &StableEntity<'_, '_>, kinds: &[CcKindV1]) -> bool {
    (0..u.cc_count()).any(|i| u.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
}

/// 被按住（[`HELD`]）。
pub fn held(u: &StableEntity<'_, '_>) -> bool {
    has_kind(u, &HELD)
}

/// 还在强制位移。
pub fn moving(u: &StableEntity<'_, '_>) -> bool {
    has_kind(u, &[CcKindV1::ForceMove])
}

/// `id` 还在强制位移（找不到他就不是）。
pub fn moving_id(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|u| moving(&u))
}

/// `id` 被按住（找不到他就不是）。
pub fn held_id(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|u| held(&u))
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The engine cuts every crowd control by the target's toughness, x (100 - toughness) / 100, forced moves too:
    /// lengthened by that much a push still goes its whole way, and no further.
    #[test]
    fn a_forced_move_outlasts_the_targets_tenacity() {
        let cut = |ticks: usize, t: usize| ticks * (100 - t) / 100;
        assert_eq!(full_ticks(19, 0), Some(19));
        assert_eq!(full_ticks(19, 30), Some(28));
        assert_eq!(full_ticks(0, 30), Some(0));
        for t in [0, 5, 20, 30, 35, 50, 65, 80, 99] {
            for ticks in 1..=60 {
                let long = full_ticks(ticks, t).unwrap();
                assert!(cut(long, t) >= ticks && cut(long - 1, t) < ticks, "{ticks} ticks, toughness {t}: {long}");
            }
        }
        // from 100 on nothing holds him
        assert_eq!(full_ticks(10, 100), None);
        assert_eq!(full_ticks(10, 130), None);
    }

    #[test]
    fn held_is_the_hard_crowd_control() {
        let has = |k: CcKindV1| HELD.iter().any(|h| h.code() == k.code());
        for k in [CcKindV1::Bind, CcKindV1::Stun, CcKindV1::Airborne, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm] {
            assert!(has(k));
        }
        for k in [CcKindV1::ForceMove, CcKindV1::BlockSkill, CcKindV1::BlockMoveSkill, CcKindV1::Animation] {
            assert!(!has(k));
        }
    }
}
