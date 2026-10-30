//! 卡住不动的保险（0.2.13）。玩家反馈（用户 2026-10-28：「佛耶戈是不是bug还在 … 2技能的问题 3级之前不会出问题
//! 被击飞后才会恢复」）：W 的冲刺在 2026-10-25 已从 `MoveTo` 换成 `RushTime`，他还是会在出招后一整局站着不动，被击飞
//! 或被杀才恢复。经典模拟（游戏 0.5.1）复现不了：游戏 0.6.5 里一个冲刺 / 动作停不下来时，他身上留着 `ForceMove` 或
//! `Animation`，击飞（硬控）把它打断。R 的 `MoveToTarget` 同时换成了 `RushTime`；这里兜底：
//!
//! - 强制位移连续 `FORCE_MAX` tick、施法动作连续 `ANIM_MAX` tick（他最长的冲刺、动作都远短于此），或
//! - 身边 `NEAR` 内有敌方英雄，他却连续 `STILL_MAX` tick 没挪过一步、普攻和三个技能的冷却都没往上跳（没出过手）：
//!
//! 就清掉他身上的控制（`entity_clear_cc`），再给他 `KICK` tick 的击飞（玩家说的「被击飞后才会恢复」），日志记一行
//! `STUCK`（为什么、他身上的控制、buff、刚放过的招）。判断在 [`Watch::step`]（纯计算、单元测试）。

/// 连续这么多 tick 有强制位移算卡住（W 6、R 12、附身扑向灵魂最多 23、被击退 30 以内）。
pub const FORCE_MAX: usize = 90;
/// 连续这么多 tick 在施法动作里算卡住（W 46、R 36）。守护天使的复活（`STASIS`，241 tick 的施法动作）和放逐（不可选中）
/// 不算（2026-10-30 的日志：590 次 STUCK 全是这两种，把复活截短、把莫德凯撒的领域解开）。
pub const ANIM_MAX: usize = 240;
/// 游戏的守护天使复活时挂的 buff。
pub const STASIS: &str = "guardian_angel_stasis";
/// 敌方英雄在这么近、他这么多 tick 没动也没出手算卡住。
pub const STILL_MAX: usize = 300;
pub const NEAR: f64 = 50_000.0;
/// 补的击飞多长。
pub const KICK: u64 = 2;

/// 这一 tick 看到的他。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Obs {
    pub alive: bool,
    pub pos: (u64, u64),
    /// 身上有强制位移 / 施法动作
    pub force: bool,
    pub anim: bool,
    /// 普攻或某个技能的冷却比上一 tick 高了（出手了）
    pub acted: bool,
    /// `NEAR` 内有看得见的敌方英雄
    pub foe_near: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Why {
    Force(usize),
    Anim(usize),
    Still(usize),
}

#[derive(Clone, Debug, Default)]
pub struct Watch {
    force: usize,
    anim: usize,
    still: usize,
    last_pos: Option<(u64, u64)>,
}

impl Watch {
    /// One tick: Some(why) when he is to be freed (the counters start over then).
    pub fn step(&mut self, o: Obs) -> Option<Why> {
        if !o.alive {
            *self = Watch::default();
            return None;
        }
        self.force = if o.force { self.force + 1 } else { 0 };
        self.anim = if o.anim { self.anim + 1 } else { 0 };
        let moved = self.last_pos.is_some_and(|p| p != o.pos);
        self.last_pos = Some(o.pos);
        self.still = if moved || o.acted || !o.foe_near { 0 } else { self.still + 1 };
        let why = if self.force >= FORCE_MAX {
            Some(Why::Force(self.force))
        } else if self.anim >= ANIM_MAX {
            Some(Why::Anim(self.anim))
        } else if self.still >= STILL_MAX {
            Some(Why::Still(self.still))
        } else {
            None
        };
        if why.is_some() {
            self.force = 0;
            self.anim = 0;
            self.still = 0;
        }
        why
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn o(pos: u64, force: bool, anim: bool, acted: bool, foe: bool) -> Obs {
        Obs { alive: true, pos: (pos, 0), force, anim, acted, foe_near: foe }
    }

    #[test]
    fn his_own_dashes_and_casts_are_left_alone() {
        let mut w = Watch::default();
        // R: 12 ticks of dash in a 36-tick cast, then walking
        for t in 0..36 {
            assert_eq!(w.step(o(t * 5000, t < 12, true, t == 0, true)), None);
        }
        for t in 0..400 {
            assert_eq!(w.step(o(200_000 + t, false, false, false, true)), None);
        }
    }

    #[test]
    fn a_dash_that_never_ends_is_broken() {
        let mut w = Watch::default();
        let mut hit = None;
        for t in 0..200 {
            if let Some(why) = w.step(o(1000, true, t < 46, false, true)) {
                hit = Some((t, why));
                break;
            }
        }
        assert_eq!(hit, Some((FORCE_MAX - 1, Why::Force(FORCE_MAX))));
    }

    #[test]
    fn a_cast_that_never_ends_is_broken() {
        let mut w = Watch::default();
        // still and near an enemy too, but the attack lands every 60 ticks: only the animation counts
        let hit = (0..1000).find_map(|t| w.step(o(1000, false, true, t % 60 == 0, true)));
        assert_eq!(hit, Some(Why::Anim(ANIM_MAX)));
    }

    #[test]
    fn standing_by_an_enemy_doing_nothing_is_broken() {
        let mut w = Watch::default();
        let hit = (0..1000).find_map(|_| w.step(o(1000, false, false, false, true)));
        assert_eq!(hit, Some(Why::Still(STILL_MAX)));
        // with nobody near, or swinging, he may stand
        let mut w = Watch::default();
        assert!((0..1000).all(|_| w.step(o(1000, false, false, false, false)).is_none()));
        let mut w = Watch::default();
        assert!((0..1000).all(|t| w.step(o(1000, false, false, t % 70 == 0, true)).is_none()));
    }

    #[test]
    fn death_starts_over() {
        let mut w = Watch::default();
        for _ in 0..80 {
            w.step(o(1000, true, false, false, true));
        }
        w.step(Obs::default());
        assert!((0..80).all(|_| w.step(o(1000, true, false, false, true)).is_none()));
    }
}
