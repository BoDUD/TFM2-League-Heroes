//! 窃法巧手的召唤师技能（0.2.0，用户 2026-10-20：「可以改成召唤师技能那种效果吗 随机的」「能做成智能释放吗」）：每次
//! 窃法巧手发动（大招射飞弹的那一刻、捡起碎片时），先按局面挑一个召唤师技能，局面里没有该用的就随机一个。纯逻辑，单元测试。
//!
//! 按先后：
//! 1. 被控住（眩晕、定身、击飞……）：**净化**；
//! 2. 残血（`LOW`）、敌方英雄贴脸（`CLOSE`）：**闪现**躲开；
//! 3. 残血，或身边有快死的队友（`ALLY_LOW`）：**治疗**；
//! 4. 身边有快死的敌方英雄（`KILL`）：**点燃**他；
//! 5. 敌方英雄贴脸：**虚弱**他；
//! 6. 掉了不少血（`HURT`）、身边有敌方英雄：**屏障**；
//! 7. 附近没有敌方英雄：**幽灵疾步**（赶路、追人）；
//! 8. 都不是：点燃 / 虚弱 / 屏障 / 幽灵疾步里随机一个（比赛的种子定的，两份模拟一样）。

/// 七个召唤师技能。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Spell {
    Cleanse,
    Flash,
    Heal,
    Ignite,
    Exhaust,
    Barrier,
    Ghost,
}

impl Spell {
    pub fn name(self) -> &'static str {
        match self {
            Spell::Cleanse => "Cleanse",
            Spell::Flash => "Flash",
            Spell::Heal => "Heal",
            Spell::Ignite => "Ignite",
            Spell::Exhaust => "Exhaust",
            Spell::Barrier => "Barrier",
            Spell::Ghost => "Ghost",
        }
    }
}

/// 残血：生命比例低于这个。
pub const LOW: f64 = 0.35;
/// 掉了不少血。
pub const HURT: f64 = 0.6;
/// 队友快死了。
pub const ALLY_LOW: f64 = 0.3;
/// 敌方英雄快死了（点燃收人头）。
pub const KILL: f64 = 0.3;
/// 贴脸。
pub const CLOSE: u64 = 30_000;
/// 治疗队友、点燃、屏障看的范围。
pub const NEAR: u64 = 65_000;
/// 这以内没有敌方英雄就幽灵疾步。
pub const FAR: u64 = 90_000;

/// 一个英雄：(实体号, 距离, 生命比例)。
pub type Unit = (usize, u64, f64);

/// 挑哪个召唤师技能、对谁（点燃 / 虚弱的目标，治疗顺带的队友，闪现躲开的那个），为什么。
pub fn pick(me_hp: f64, controlled: bool, foes: &[Unit], allies: &[Unit], roll: u64) -> (Spell, Option<usize>, &'static str) {
    let nearest = foes.iter().min_by_key(|f| f.1).copied();
    let close = nearest.filter(|f| f.1 <= CLOSE);
    if controlled {
        return (Spell::Cleanse, None, "controlled");
    }
    if me_hp < LOW {
        if let Some(f) = close {
            return (Spell::Flash, Some(f.0), "low with a champion on her");
        }
    }
    let ally_low = allies.iter().filter(|a| a.1 <= NEAR && a.2 < ALLY_LOW).min_by(|a, b| a.2.total_cmp(&b.2)).copied();
    if me_hp < LOW || ally_low.is_some() {
        return (Spell::Heal, ally_low.map(|a| a.0), if me_hp < LOW { "low" } else { "an ally nearly dead" });
    }
    if let Some(f) = foes.iter().filter(|f| f.1 <= NEAR && f.2 < KILL).min_by(|a, b| a.2.total_cmp(&b.2)) {
        return (Spell::Ignite, Some(f.0), "a champion nearly dead");
    }
    if let Some(f) = close {
        return (Spell::Exhaust, Some(f.0), "a champion on her");
    }
    if me_hp < HURT && nearest.is_some_and(|f| f.1 <= NEAR) {
        return (Spell::Barrier, None, "hurt in a fight");
    }
    if nearest.is_none_or(|f| f.1 > FAR) {
        return (Spell::Ghost, None, "nobody near");
    }
    let target = nearest.map(|f| f.0);
    match roll % 4 {
        0 => (Spell::Ignite, target, "random"),
        1 => (Spell::Exhaust, target, "random"),
        2 => (Spell::Barrier, None, "random"),
        _ => (Spell::Ghost, None, "random"),
    }
}

/// 比赛种子、tick、实体号 -> 随机数（splitmix64）：服务端预模拟和画面那份算出同一个。
pub fn roll(seed: u64, tick: usize, me: usize) -> u64 {
    let mut z = seed ^ (tick as u64).wrapping_mul(0x9e37_79b9_7f4a_7c15) ^ (me as u64).rotate_left(32);
    z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    z ^ (z >> 31)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn controlled_first() {
        assert_eq!(pick(0.2, true, &[(1, 10_000, 1.0)], &[], 0).0, Spell::Cleanse);
    }

    #[test]
    fn low_and_dived_flashes_low_alone_heals() {
        assert_eq!(pick(0.2, false, &[(1, 20_000, 1.0)], &[], 0), (Spell::Flash, Some(1), "low with a champion on her"));
        assert_eq!(pick(0.2, false, &[(1, 50_000, 1.0)], &[], 0).0, Spell::Heal);
    }

    #[test]
    fn a_dying_ally_gets_the_heal() {
        assert_eq!(pick(0.9, false, &[(1, 50_000, 1.0)], &[(7, 40_000, 0.2), (8, 30_000, 0.25)], 0),
                   (Spell::Heal, Some(7), "an ally nearly dead"));
        // too far to heal
        assert_ne!(pick(0.9, false, &[(1, 50_000, 1.0)], &[(7, 90_000, 0.2)], 0).0, Spell::Heal);
    }

    #[test]
    fn a_dying_enemy_gets_ignited_a_diver_exhausted() {
        assert_eq!(pick(0.9, false, &[(1, 50_000, 0.25), (2, 40_000, 0.9)], &[], 0), (Spell::Ignite, Some(1), "a champion nearly dead"));
        assert_eq!(pick(0.9, false, &[(2, 20_000, 0.9)], &[], 0), (Spell::Exhaust, Some(2), "a champion on her"));
    }

    #[test]
    fn hurt_in_a_fight_shields_alone_runs() {
        assert_eq!(pick(0.5, false, &[(2, 50_000, 0.9)], &[], 0).0, Spell::Barrier);
        assert_eq!(pick(0.9, false, &[(2, 120_000, 0.9)], &[], 0).0, Spell::Ghost);
        assert_eq!(pick(0.9, false, &[], &[], 0).0, Spell::Ghost);
    }

    #[test]
    fn otherwise_the_roll_decides_and_both_sims_agree() {
        let foes = [(2, 50_000, 0.9)];
        let got: Vec<Spell> = (0..4).map(|r| pick(0.9, false, &foes, &[], r).0).collect();
        assert_eq!(got, vec![Spell::Ignite, Spell::Exhaust, Spell::Barrier, Spell::Ghost]);
        assert_eq!(roll(42, 1000, 7), roll(42, 1000, 7));
        assert_ne!(roll(42, 1000, 7), roll(42, 1001, 7));
    }
}
