//! 大地图版技能距离（用户 2026-11-27：「少数写在我们代码里的特殊技能距离这次没改，比如佐伊 Q 的飞星。这个也处理一下」）。
//!
//! 玩 Rin 的大地图时，用户关掉游戏双击 D:/TFM2-Workshop/切到大地图版.cmd：英雄数据里的技能距离、被动参数里的距离由那个
//! 脚本（D:/TFM2-Workshop/rift_skill/rift_skill.py）直接乘 1.3，同时在游戏目录写一个标记文件 [`FLAG`]；切回小地图版时删掉。
//! 这里管附加包代码里写死的技能距离和速度：标记在就乘 1.3，不在就原样，跟数据一起切。标记只在第一次用到时读一次
//! （切换脚本要求游戏关着，开着的游戏里它不会变）。
//!
//! 只给技能用：普攻距离、身体大小、塔、地图边界、墙格、画面上的偏移都不要套它。数和脚本一样算：整数四舍五入，
//! 「整张图」那么大的数（≥ 90 万，原版地图边长 96 万）按两张图的边长之比放大。

use std::path::PathBuf;
use std::sync::OnceLock;

/// 大地图版的倍数：英雄按英雄联盟 ×100 换算，Rin 的大地图是召唤师峡谷的 1.3 倍大。
pub const BIG: f64 = 1.3;
/// 标记文件名，放在游戏目录（TeamfightManager2.exe 旁边）。
pub const FLAG: &str = "rift_skill_big.flag";
/// 这么大的数是「整张图」。
pub const MAP_WIDE: f64 = 900_000.0;
/// 大地图边长 / 原版地图边长。
pub const MAP_RATIO: f64 = 1_937_454.0 / 960_000.0;

static FACTOR: OnceLock<f64> = OnceLock::new();

fn flag_path() -> Option<PathBuf> {
    std::env::current_exe().ok()?.parent().map(|d| d.join(FLAG))
}

/// 现在的倍数：标记在是 [`BIG`]，不在是 1。
pub fn factor() -> f64 {
    *FACTOR.get_or_init(|| if flag_path().is_some_and(|p| p.is_file()) { BIG } else { 1.0 })
}

/// 现在是不是大地图版。
pub fn big() -> bool {
    factor() != 1.0
}

/// 按倍数 `f` 乘一个距离或速度（不取整）。
pub fn scale_with(v: f64, f: f64) -> f64 {
    if f == 1.0 || v == 0.0 {
        return v;
    }
    if v.abs() >= MAP_WIDE {
        v * MAP_RATIO
    } else {
        v * f
    }
}

/// 能按大地图版乘的数。
pub trait Dist: Copy {
    fn sk(self) -> Self;
}

macro_rules! int_dist {
    ($($t:ty),*) => {$(
        impl Dist for $t {
            fn sk(self) -> Self {
                let f = factor();
                if f == 1.0 {
                    self
                } else {
                    scale_with(self as f64, f).round() as $t
                }
            }
        }
    )*};
}
int_dist!(u64, i64, usize, isize, u32, i32);

impl Dist for f64 {
    fn sk(self) -> Self {
        scale_with(self, factor())
    }
}

impl Dist for f32 {
    fn sk(self) -> Self {
        scale_with(self as f64, factor()) as f32
    }
}

/// 一个写死的技能距离 / 速度在现在这一版里的值：`sk(R_RANGE)`。
pub fn sk<T: Dist>(v: T) -> T {
    v.sk()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn scaling_matches_the_switch_script() {
        assert_eq!(scale_with(64_000.0, BIG), 83_200.0);
        assert_eq!(scale_with(6_000.0, BIG), 7_800.0);
        assert_eq!(scale_with(960_000.0, BIG).round(), 1_937_454.0);
        assert_eq!(scale_with(-9_500.0, BIG), -12_350.0);
        assert_eq!(scale_with(95_000.0, 1.0), 95_000.0);
    }

    #[test]
    fn no_flag_next_to_the_test_binary_means_the_small_map() {
        assert_eq!(factor(), 1.0);
        assert!(!big());
        assert_eq!(sk(95_000u64), 95_000);
        assert_eq!(sk(4_000.5f64), 4_000.5);
        assert_eq!(sk(-12_000i64), -12_000);
    }
}
