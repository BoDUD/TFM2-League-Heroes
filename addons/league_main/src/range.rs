//! `league:range`（0.9.15，2026-11-07）：带攻击距离的 buff 用官方的办法加射程。
//!
//! 游戏的 AI 按「普攻射程 + 身上 `range` buff」给英雄站位，自己却只在普攻动作本身的射程内出手，所以 `range` buff 一开
//! 英雄就停在够不着的地方不打（league_ult_press.log 两次启动：大嘴开 W 被停住时最常见正好 78000 = 55000 + 18000 + 两人体积，
//! 82 次里 60 次在射程外；图奇开 R 停在 90000 左右；赛娜 130 次里 81 次；没有射程 buff 的射手一次也没有）。官方英雄加射程从来
//! 不用 `range` buff：动作的 `growth_range`（按等级），或动作效果的 `range_adjust`（稳定 API 0.6.4 起：「每一处射程判断都读它，
//! AI 的也是」；原版的毒镖猎手、弩手就这样加射程，`Combine` 取它各个效果里最大的 `range_adjust`）。
//!
//! 这个原生效果的 `range_adjust` = 施放者身上每一个标记 buff 在 [`RANGE_BUFFS`] 里的射程之和（同名叠几层算几层：赛娜的黑雾、
//! 千珏的印记），`apply` 什么也不做。主包的这些 buff 不再带 `range`（只是标记），普攻最外层的 `Combine` 里多一个
//! `{"type": "Native", "effect_ref": "league:range"}`（tools/kit/range_buffs.py；表也从那里生成：src/range_table.rs）。
//! 每种标记第一次在游戏里加上射程时 league.log 记一行 `RANGE`，核对引擎确实读了它。

use std::sync::atomic::{AtomicBool, Ordering};

use mod_api_stable::*;

pub use crate::range_table::RANGE_BUFFS;

/// 原生效果的名字（数据里 `effect_ref` 写它）。
pub const NODE: &str = "league:range";

/// 一个 buff 名在表里的位置（不是标记就 `None`）。
pub fn index_of(name: &str) -> Option<usize> {
    RANGE_BUFFS.iter().position(|(n, _)| *n == name)
}

/// 一个 buff 名给的射程（不是标记就 0）。
pub fn bonus_of(name: &str) -> u64 {
    index_of(name).map_or(0, |k| RANGE_BUFFS[k].1)
}

/// 这些 buff 名一共给的射程：每个实例都算。
pub fn bonus<'a>(names: impl IntoIterator<Item = &'a str>) -> u64 {
    names.into_iter().map(bonus_of).sum()
}

/// 每种标记有没有在日志里记过（记一次：引擎读到了它）。`range_adjust` 每一处射程判断都调，这里不加锁。
#[allow(clippy::declare_interior_mutable_const)]
const UNSEEN: AtomicBool = AtomicBool::new(false);
static SEEN: [AtomicBool; RANGE_BUFFS.len()] = [UNSEEN; RANGE_BUFFS.len()];

#[derive(Debug)]
pub struct Range;

impl StableEffectType for Range {
    fn apply(&self, _sim: &mut StableSim<'_>, _seed: u64, _caster: usize, _input: InputTargetV1) {}

    fn may_adjust_range(&self) -> bool {
        true
    }

    fn range_adjust(&self, caster: &StableEntityView<'_>, _target: &StableEntityView<'_>) -> u64 {
        let mut total = 0;
        for i in 0..caster.buff_count() {
            let Some(b) = caster.buff_at(i) else { continue };
            let Some(k) = index_of(b.name()) else { continue };
            total += RANGE_BUFFS[k].1;
            if !SEEN[k].swap(true, Ordering::Relaxed) {
                crate::wlog(format!("RANGE +{} from {} (entity #{}) - the engine reads {NODE}", RANGE_BUFFS[k].1,
                                    RANGE_BUFFS[k].0, caster.id()));
            }
        }
        total
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn each_marker_adds_its_range_and_stacks_count() {
        assert_eq!(bonus_of("league_twitch_r_on"), 30000);
        assert_eq!(bonus_of("league_twitch_r_armed"), 0, "not a marker");
        assert_eq!(bonus(["league_kayle_rank5", "league_kayle_rank12", "league_kayle_life"]), 37500);
        assert_eq!(bonus(["league_senna_mist"; 40]), 4000, "every Mist counts");
        assert_eq!(bonus(std::iter::empty::<&str>()), 0);
    }

    #[test]
    fn the_table_is_sorted_and_without_doubles() {
        let names: Vec<&str> = RANGE_BUFFS.iter().map(|(n, _)| *n).collect();
        let mut sorted = names.clone();
        sorted.sort();
        sorted.dedup();
        assert_eq!(names, sorted);
        assert!(RANGE_BUFFS.iter().all(|(n, r)| n.starts_with("league_") && *r > 0));
    }
}
