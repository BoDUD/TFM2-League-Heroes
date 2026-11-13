//! 推人、拉人的共用规则。
//!
//! **强制位移不吃韧性（2026-11-13 晚，量出来的）。** 当天下午按「引擎把每种控制的时长按目标的韧性缩短，强制位移也一样」
//! （`.claude/skills/tfm2-hero-mod/references/champion-data.md` 里读 0.5.1 game_core 的那句）把附加包的推、拉都按韧性放长了，
//! 合集还每 tick「补齐」没放长过的强制位移（#763）。装进游戏以后阿兹尔的日志（`league_azir.log` 的 `LANDED`，70 次带人）
//! 说明这是错的：没被打断的带人，实际走的路 / 计划的路 = 1 / (1 - 韧性)，一分不差——韧性 10 是 1.13，30 是 1.45，
//! 50 是 2.00，65 是 2.84，70 是 3.31：放长多少就多走多少，引擎（0.7.2，`apply_cc` 的 ForceMove）根本不按韧性缩短。
//! 所以放长和「补齐」都撤掉了：带韧性的人被推过头，数据里的击退、英雄自己的冲刺也被多推一截。剑魔 W、李青 W 防「被韧性
//! 截短」的补推在日志里一次也没触发过，是同一个事实。
//!
//! 这里留下的只是查状态的小工具：
//! - [`HELD`] / [`held`]：眩晕、定身、击飞、嘲讽、恐惧、魅惑。
//! - [`moving`]：还在强制位移。
//! - [`toughness`]：他身上所有效果的韧性加起来（只给日志用）。
//!
//! 推人的附加包靠「到点就算到了」的（撞墙晕）先看他是不是真的到了（[`moving`] / 各包自己的落点）。

use mod_api_stable::*;

/// 按住一个单位的控制（硬控）。
pub const HELD: [CcKindV1; 6] =
    [CcKindV1::Bind, CcKindV1::Stun, CcKindV1::Airborne, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];

/// 他身上所有效果的韧性加起来（4+6 的装备、符文、技能的 buff）。只给日志用：强制位移不吃韧性。
pub fn toughness(u: &StableEntity<'_, '_>) -> usize {
    (0..u.buff_count()).filter_map(|i| u.buff_at(i)).map(|b| b.toughness).sum()
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
