//! 窃法巧手的召唤师技能（0.2.0，用户 2026-10-20：「可以改成召唤师技能那种效果吗 随机的」「能做成智能释放吗」）：每次
//! 窃法巧手发动（大招射飞弹的那一刻、捡起碎片时），先按局面挑一个召唤师技能，局面里没有该用的就随机一个。纯逻辑，单元测试。
//!
//! 按先后：
//! 1. 被控住（眩晕、定身、击飞……）：**净化**；
//! 2. 残血（`LOW`）、敌方英雄贴脸（`CLOSE`）：**闪现**躲开（大招里不闪：半秒后传送门就把她送回原地，闪了也白闪，
//!    用户 2026-11-01「闪现现在怎么看不出效果」；落到下一条的治疗）；
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
    /// 地上的法术碎片轮流闪的次序（`ss_<key>`）。
    pub const ALL: [Spell; 7] =
        [Spell::Flash, Spell::Ignite, Spell::Exhaust, Spell::Heal, Spell::Barrier, Spell::Ghost, Spell::Cleanse];

    /// 画面的名字：`league_zoe_sg_<key>`（放的时候地上亮的图标）、`league_zoe_ss_<key>`（碎片上的图标）。
    pub fn key(self) -> &'static str {
        match self {
            Spell::Cleanse => "cleanse",
            Spell::Flash => "flash",
            Spell::Heal => "heal",
            Spell::Ignite => "ignite",
            Spell::Exhaust => "exhaust",
            Spell::Barrier => "barrier",
            Spell::Ghost => "ghost",
        }
    }

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

/// 挑哪个召唤师技能、对谁（点燃 / 虚弱的目标，治疗顺带的队友，闪现躲开的那个），为什么。`in_ult`：大招里发动的（不闪现）。
pub fn pick(me_hp: f64, controlled: bool, in_ult: bool, foes: &[Unit], allies: &[Unit], roll: u64)
            -> (Spell, Option<usize>, &'static str) {
    let nearest = foes.iter().min_by_key(|f| f.1).copied();
    let close = nearest.filter(|f| f.1 <= CLOSE);
    if controlled {
        return (Spell::Cleanse, None, "controlled");
    }
    if me_hp < LOW && !in_ult {
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

/// 闪现的距离（创意工坊 Summoner Spells 的 4.5 格；英雄联盟 400，她射程 550 的七成多）。
pub const FLASH_D: f64 = 45_000.0;

/// 闪现的落点：从 `me` 背着贴脸的人 `from` 闪 [`FLASH_D`]（和英雄联盟一样能越过墙）；落在墙里或地图外就依次转
/// ±30°、±60°、±90° 再试，都不行再缩到一半距离试一遍；还不行就不闪（`None`）。墙是 5v5 的格子（`maps.rs`）。
pub fn flash_spot(me: (u64, u64), from: (u64, u64)) -> Option<(u64, u64)> {
    let (mx, my) = (me.0 as f64, me.1 as f64);
    let (dx, dy) = (mx - from.0 as f64, my - from.1 as f64);
    let l = (dx * dx + dy * dy).sqrt();
    let base = if l > 1.0 { dy.atan2(dx) } else { 0.0 };
    for d in [FLASH_D, FLASH_D / 2.0] {
        for turn in [0.0, 30.0, -30.0, 60.0, -60.0, 90.0, -90.0f64] {
            let a = base + turn.to_radians();
            let (x, y) = (mx + d * a.cos(), my + d * a.sin());
            if !is_wall(x, y) {
                return Some((x.round() as u64, y.round() as u64));
            }
        }
    }
    None
}

/// 5v5 的碰撞墙：`MOBA[y]` 第 x 个字符是 `#` 为墙，每格 32000；地图外也算墙（league_corki 的读法）。
pub fn is_wall(x: f64, y: f64) -> bool {
    const MAP: f64 = 960_000.0;
    const CELL: f64 = 32_000.0;
    if x < 0.0 || y < 0.0 || x >= MAP || y >= MAP {
        return true;
    }
    let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
    super::maps::MOBA.get(cy).and_then(|row| row.as_bytes().get(cx)).is_none_or(|c| *c == b'#')
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn controlled_first() {
        assert_eq!(pick(0.2, true, false, &[(1, 10_000, 1.0)], &[], 0).0, Spell::Cleanse);
    }

    #[test]
    fn low_and_dived_flashes_low_alone_heals() {
        assert_eq!(pick(0.2, false, false, &[(1, 20_000, 1.0)], &[], 0), (Spell::Flash, Some(1), "low with a champion on her"));
        // in the ult the portal takes her home half a second later: no Flash, the heal instead
        assert_eq!(pick(0.2, false, true, &[(1, 20_000, 1.0)], &[], 0), (Spell::Heal, None, "low"));
    }

    #[test]
    fn flash_jumps_away_from_the_one_on_her_and_never_into_a_wall() {
        // open ground in the middle of the map: straight away, the whole distance
        let me = (480_000, 470_000);
        let to = flash_spot(me, (460_000, 470_000)).unwrap();
        assert_eq!(to, (525_000, 470_000));
        // every spot it gives is on open ground
        for y in (40_000..920_000).step_by(37_000) {
            for x in (40_000..920_000).step_by(41_000) {
                if is_wall(x as f64, y as f64) {
                    continue;
                }
                if let Some(t) = flash_spot((x, y), (x + 10_000, y + 3_000)) {
                    assert!(!is_wall(t.0 as f64, t.1 as f64), "{x},{y} -> {t:?}");
                }
            }
        }
        // the map's corner: away from it is off the map, so it turns
        let t = flash_spot((30_000, 30_000), (60_000, 60_000)).unwrap();
        assert!(t.0 < 960_000 && t.1 < 960_000);
        assert_eq!(pick(0.2, false, false, &[(1, 50_000, 1.0)], &[], 0).0, Spell::Heal);
    }

    #[test]
    fn a_dying_ally_gets_the_heal() {
        assert_eq!(pick(0.9, false, false, &[(1, 50_000, 1.0)], &[(7, 40_000, 0.2), (8, 30_000, 0.25)], 0),
                   (Spell::Heal, Some(7), "an ally nearly dead"));
        // too far to heal
        assert_ne!(pick(0.9, false, false, &[(1, 50_000, 1.0)], &[(7, 90_000, 0.2)], 0).0, Spell::Heal);
    }

    #[test]
    fn a_dying_enemy_gets_ignited_a_diver_exhausted() {
        assert_eq!(pick(0.9, false, false, &[(1, 50_000, 0.25), (2, 40_000, 0.9)], &[], 0), (Spell::Ignite, Some(1), "a champion nearly dead"));
        assert_eq!(pick(0.9, false, false, &[(2, 20_000, 0.9)], &[], 0), (Spell::Exhaust, Some(2), "a champion on her"));
    }

    #[test]
    fn hurt_in_a_fight_shields_alone_runs() {
        assert_eq!(pick(0.5, false, false, &[(2, 50_000, 0.9)], &[], 0).0, Spell::Barrier);
        assert_eq!(pick(0.9, false, false, &[(2, 120_000, 0.9)], &[], 0).0, Spell::Ghost);
        assert_eq!(pick(0.9, false, false, &[], &[], 0).0, Spell::Ghost);
    }

    #[test]
    fn otherwise_the_roll_decides_and_both_sims_agree() {
        let foes = [(2, 50_000, 0.9)];
        let got: Vec<Spell> = (0..4).map(|r| pick(0.9, false, false, &foes, &[], r).0).collect();
        assert_eq!(got, vec![Spell::Ignite, Spell::Exhaust, Spell::Barrier, Spell::Ghost]);
        assert_eq!(roll(42, 1000, 7), roll(42, 1000, 7));
        assert_ne!(roll(42, 1000, 7), roll(42, 1001, 7));
    }
}
