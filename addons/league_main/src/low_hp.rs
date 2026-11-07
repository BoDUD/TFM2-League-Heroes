//! `league:low_hp`（0.9.17，2026-11-07）：数据读不到当前生命值（champion-data 第 3 节「nothing reads current health」），
//! 这个原生效果替它看一眼：施放者生命低于 [`LOW_PCT`]% 就给他挂 [`FLAG_TICKS`] tick 的 [`FLAG`]，数据用 `SwitchByBuff` 分支。
//!
//! 用户 2026-11-07：「瑞兹的大招逻辑有问题吧」——该逃时不逃、传进敌人堆里送死。league_ult_press 在瑞兹生命不到 35%、身边
//! 60000 内有敌方英雄时替他按 R，可主包的 R 不知道为什么被按：它只在 30000 内有两个敌方英雄（或 15000 内一个、身边没队友）
//! 时逃，否则不动，甚至判断成「去追远处的敌人」把残血的他传过去。瑞兹的待命检查（tools/kit/build_ryze.py）每次先放这个
//! 效果，下一 tick 有 `league_low_hp` 就只逃不追。
//!
//! 没有这个 DLL 时（Mac / Linux）这个效果找不到，经典 SDK 的引擎对此只记一条警告，标记永远不出现，数据照旧走原来的分支。

use std::sync::atomic::{AtomicBool, Ordering};

use mod_api_stable::*;

/// 原生效果的名字（数据里 `effect_ref` 写它）。
pub const NODE: &str = "league:low_hp";
/// 挂上的标记（数据的 `SwitchByBuff` 读它）。
pub const FLAG: &str = "league_low_hp";
/// 生命低于这个百分比算残血：league_ult_press 替瑞兹按 R 逃命的线（`RYZE_FLEE` 0.35）。
pub const LOW_PCT: usize = 35;
/// 标记挂几 tick：数据在下一 tick 读（n tick 的标记只在其中 n - 1 tick 读得到，champion-data 第 8 节），多留一 tick。
pub const FLAG_TICKS: usize = 3;

/// 生命 `hp` / `max` 算不算残血（`max` 为 0：读不到，不算）。
pub fn is_low(hp: usize, max: usize) -> bool {
    max > 0 && hp.saturating_mul(100) < max.saturating_mul(LOW_PCT)
}

/// 第一次挂上标记时 league.log 记一行（核对游戏真的跑了这个效果）。
static LOGGED: AtomicBool = AtomicBool::new(false);

#[derive(Debug)]
pub struct LowHp;

impl StableEffectType for LowHp {
    fn apply(&self, sim: &mut StableSim<'_>, _seed: u64, caster: usize, _input: InputTargetV1) {
        let Some(e) = sim.get_entity(caster) else { return };
        let (hp, max) = e.hp();
        if !is_low(hp, max) {
            return;
        }
        let name = e.name().unwrap_or_default();
        sim.entity_remove_buff(caster, FLAG);
        sim.add_buff(caster, &BuffV1::timed(FLAG, FLAG_TICKS));
        if !LOGGED.swap(true, Ordering::Relaxed) {
            crate::wlog(format!("LOW_HP {name} #{caster} at {hp} / {max} - {FLAG} set for {FLAG_TICKS} ticks ({NODE} runs)"));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn low_is_under_the_line() {
        assert!(is_low(349, 1000));
        assert!(!is_low(350, 1000), "35% itself is not low (league_ult_press: hp < 0.35)");
        assert!(!is_low(1000, 1000));
        assert!(is_low(0, 1000));
        assert!(!is_low(0, 0), "no max read: not low");
        assert_eq!(FLAG_TICKS, 3);
    }
}
