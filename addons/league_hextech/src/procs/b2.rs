//! 0.4.0 的触发类海克斯（用户 2026-11-26：「还有没有其他的海克斯可以做的」，选了「对齐+数值触发」）：英雄联盟 26.23 海克斯大乱斗里
//! 本游戏能做的那些，外加对齐的四个（玻璃大炮、巨人杀手、大法师、终极觉醒）和八个随场上情况变的属性。看的东西都在
//! [`super`]：打中（[`super::Hit`]，分普攻、技能）、放技能、参与击杀、残血、控住、阵亡 / 复活、位移、获得护盾、回复、受伤。
//!
//! 英雄联盟的数值按装备的比例换成本游戏的（攻击约 ×1.7、法强 ×2），「X～Y」按 1 到 12 级（[`super::by_level`]）。做不到的地方：
//! 「免疫控制」用韧性 90%（`cc_immune` 会连英雄自己放技能的动作一起挡掉，最终形态同样的理由）；「无敌」是受到的伤害 -100%；
//! 「变小」做不了（高清帧引擎只放大）。

use super::*;
use crate::rules::splitmix;

// ===================== 数值（说明照这些写） =====================

/// 位移：这一步挪的距离超过走路的这么多倍（/10），而且至少这么远，而且刚放过技能（被别人击退的不算）。
pub const DASH_X10: u64 = 25;
pub const DASH_MIN: u64 = 6_000;
pub const DASH_WINDOW: usize = 30;

// 对齐的四个
pub const GLASS_MELEE_PCT: u64 = 25;
pub const GLASS_RANGED_PCT: u64 = 15;
/// 巨人杀手：他的最大生命是你的这么多（%）起，额外这么多（%）。
pub const SLAYER_STEPS: [(usize, u64); 4] = [(200, 30), (150, 25), (125, 15), (101, 10)];
pub const ARCHMAGE_PCT: usize = 30;
pub const AWAKE_CD: usize = 1_200;
pub const AWAKE_T: usize = 900;
pub const AWAKE_HASTE: i32 = 300;
/// 「立刻转好」：冷却一次缩短这么多 tick（比任何技能的冷却都长）。
pub const RESET: usize = 100_000;

// 随场上变的属性
pub const LICH_PCT: usize = 4;
pub const HOME_IDLE: usize = 360;
pub const HOME_MS: i32 = 40;
pub const LONELY_R: u64 = 45_000;
pub const LONELY_MOST: usize = 5;
pub const LONELY_AS: i32 = 6;
pub const LONELY_RES: i32 = 6;
pub const KILLSEC_R: u64 = 90_000;
pub const KILLSEC_PCT: usize = 40;
pub const KILLSEC_MS: i32 = 35;
pub const STEAD_PCT: usize = 40;
pub const STILL_AS: i32 = 10;
pub const STILL_VAMP: i32 = 2;
/// 尤里卡：每 100 法强这么多技能急速（按 5 一档）。
pub const EUREKA_PER_100: usize = 15;
pub const RECUR_EACH: i32 = 3;
pub const RECUR_MOST: u16 = 20;

// 银
pub const DIVE_R: u64 = 40_000;
pub const DIVE_PCT: usize = 15;
pub const EROSION_PCT: i32 = 2;
pub const EROSION_T: usize = 240;
pub const EROSION_MOST: usize = 15;
pub const GUILTY_CD: usize = 300;
pub fn guilty_heal(level: usize, max: usize) -> usize {
    by_level(40, 300, level) + max * 15 / 1000
}
pub const SLAP_CD: usize = 300;
pub const SLAP_AD: i32 = 10;
pub const SLAP_AP: i32 = 20;
pub const SLAP_MOST: u16 = 30;
pub const UNSTOP_T: usize = 180;
pub const UNSTOP_CD: usize = 480;
pub const UNSTOP_TENACITY: usize = 90;
pub const MIGHTY_T: usize = 180;
pub const MIGHTY_CD: usize = 300;
pub const FOX_CD: usize = 420;
pub const FOX_R: u64 = 50_000;
pub const FOX_N: usize = 3;
pub const FOX_MS: i32 = 25;
pub const FOX_MS_T: usize = 90;
pub fn fox_damage(level: usize, ad: usize, ap: usize) -> usize {
    by_level(25, 100, level) + ad * 10 / 100 + ap * 15 / 100
}
pub const SHADOW_MS: i32 = 60;
pub const SHADOW_T: usize = 120;
/// 双生火焰（对齐英雄联盟）：1 枚，暴击率每 33% 多 1 枚（`crit` 是百分数），最多 4 枚。
pub const TWIN_CD: usize = 300;
pub const TWIN_MOST: usize = 4;
pub fn twin_n(crit: usize) -> usize {
    (1 + crit * 3 / 100).min(TWIN_MOST)
}
pub fn twin_damage(level: usize, ad: usize, ap: usize) -> usize {
    by_level(10, 30, level) + ad * 7 / 100 + ap * 7 / 100
}
pub const SAFE_CD: usize = 300;
pub const SAFE_T: usize = 120;
pub fn safe_shield(level: usize, ad: usize, ap: usize) -> usize {
    by_level(60, 280, level) + ad * 50 / 100 + ap * 25 / 100
}

// 金
pub const AXIOM_PCT: usize = 20;
pub const BRAIN_PCT: usize = 150;
pub const BRAIN_EVERY: usize = 4_200;
pub const DIVINE_R: u64 = 50_000;
pub const DIVINE_PCT: usize = 35;
pub const DIVINE_DELAY: usize = 60;
pub const DIVINE_T: usize = 150;
pub const DIVINE_CD: usize = 2_100;
pub const MARKSMAGE_PCT: usize = 45;
pub const NIGHT_T: usize = 90;
pub const NIGHT_MS: i32 = 40;
pub const BOOM_CD: usize = 600;
pub const BOOM_RANGE: u64 = 100_000;
/// 回旋刃一 tick 飞多远、沿途多宽算打到。
pub const BOOM_SPEED: u64 = 3_000;
pub const BOOM_WIDTH: u64 = 15_000;
pub fn boom_damage(level: usize, ad: usize, ap: usize) -> usize {
    by_level(30, 150, level) + ad * 40 / 100 + ap * 30 / 100
}
pub const GRIT_T: usize = 900;
pub const GRIT_RES: i32 = 10;
pub const GRIT_MOST: usize = 5;
pub fn porcupine_store(level: usize) -> usize {
    by_level(400, 3_000, level)
}
pub const PORC_R: u64 = 30_000;
pub const PORC_SLOW: i32 = 30;
pub const PORC_SLOW_T: usize = 90;
pub fn porcupine_damage(level: usize, armor: usize, mr: usize) -> usize {
    by_level(75, 200, level) + armor * 60 / 100 + mr * 60 / 100
}
pub const SALV_PCT: usize = 50;
pub const SALV_R: u64 = 80_000;
pub const SALV_CD: usize = 4_200;
pub const SAP_CD: usize = 1_200;
pub const SAP_CAST_CUT: usize = 180;
pub const SHARK_PCT: usize = 10;
pub const SHARK_T: usize = 210;
pub const SHARK_CD: usize = 5_400;
pub const SHARK_R: u64 = 30_000;
pub const SHARK_MISSING_PCT: usize = 30;
pub const SOUL_CD: usize = 300;
pub const SOUL_HP: i32 = 40;
pub const SOUL_MOST: u16 = 40;
pub const TAKE_N: u8 = 5;
pub const TAKE_T: usize = 300;
pub const TAKE_GAP: usize = 20;
pub const TAKE_PCT: usize = 12;
pub const TAKE_HEAL_PCT: usize = 50;
pub const SNIPER_FAR: u64 = 60_000;
pub const SNIPER_PCT: usize = 80;
pub const MARK_T: usize = 300;
pub const MARK_RANGE: u64 = 90_000;
pub const MARK_PCT: usize = 30;
pub const SONATA_CD: usize = 600;
pub const SONATA_R: u64 = 50_000;
pub const SONATA_MS: i32 = 30;
pub const SONATA_MS_T: usize = 120;
pub fn sonata_heal(level: usize, ap: usize) -> usize {
    by_level(40, 200, level) + ap * 20 / 100
}

// 棱彩
pub const TOUCH_T: usize = 120;
pub const TOUCH_CD: usize = 480;
pub const DUAL_T: usize = 300;
pub const DUAL_MOST: usize = 10;
pub const DUAL_GAP: usize = 20;
pub const MOSH_T: usize = 480;
pub const MOSH_R: u64 = 30_000;
pub const MOSH_SLOW: i32 = 50;
pub const MOSH_SLOW_T: usize = 90;
pub const MOSH_EACH: i32 = 20;
pub const MOSH_MOST: u16 = 30;
pub const PROM_CD: usize = 2_100;
pub const PROM_R: u64 = 60_000;
pub const PROM_T: usize = 240;
pub const PROM_MS: i32 = 50;
pub const PROM_TOUCH: u64 = 15_000;
pub const PROM_CHARM: u64 = 75;
pub const GRAB_CD: usize = 960;
pub const GRAB_R: u64 = 60_000;
pub const GRAB_T: usize = 240;
pub const GRAB_PULL: usize = 12;
pub const GRAB_STUN: u64 = 45;
pub const GRAB_SHIELD: usize = 80;
pub const GRAB_SHIELD_T: usize = 120;
pub const THIRD_MELEE_PCT: usize = 6;
pub const THIRD_RANGED_PCT: usize = 3;
pub const THIRD_GAP: usize = 20;
pub const TITAN_T: usize = 360;
pub const TITAN_FULL: usize = 7;
pub const TITAN_GAP: usize = 20;
pub const REVO_DELAY: usize = 60;
pub const REVO_CD: usize = 4_500;
pub const FEY_T: u64 = 120;
pub const FEY_SLOW: i32 = 40;
pub const FEY_GAP: usize = 900;
pub const CIRCLE_PCT: usize = 70;
pub const CIRCLE_EVERY: usize = 30;
pub const CIRCLE_RANGE: u64 = 100_000;
pub const DUALW_DELAY: usize = 12;
pub const DUALW_PCT: usize = 40;
// 第二批
/// 渴血：回复伤害的这么多（%）。
pub const GORE_PCT: u64 = 15;
/// 物理转魔法：每 0.6 攻击力加 1 法强（×10）、法强 +15%；魔法转物理：每 1.66 法强加 1 攻击力（×100）、攻击力 +15%。
pub const ADAPT_AD_X10: usize = 6;
pub const ADAPT_AP_MULT: i32 = 15;
pub const ESC_AP_X100: usize = 166;
pub const ESC_AD_MULT: i32 = 15;
/// 史莱姆时间：6 秒一次，炸开的半径，黏液留 6 秒、走到这么近算吃到（敌人：踩到）。
pub const SLIME_CD: usize = 360;
pub const SLIME_R: u64 = 45_000;
pub const BLOB_T: usize = 360;
pub const BLOB_R: u64 = 9_000;
/// 40～80 + 目标最大生命的 3%～8%，每 100 攻击力、每 100 法强再 +1.5%（千分之 15）。
pub fn slime_damage(level: usize, max: usize, ad: usize, ap: usize) -> usize {
    let permille = by_level(30, 80, level) + (ad + ap) * 15 / 100;
    by_level(40, 80, level) + max * permille / 1000
}
pub fn blob_heal(level: usize, max: usize) -> usize {
    max * by_level(60, 150, level) / 1000
}
/// 王冠之重：攻击力 +17、法强 +50，三样 +10%，每层再 +5%、最多 +50%（8 层）；战斗中移动速度 -5%，每层再 -2.5%（×10）。
pub const CROWN_AD: i32 = 17;
pub const CROWN_AP: i32 = 50;
pub const CROWN_PCT: i32 = 10;
pub const CROWN_EACH: i32 = 5;
pub const CROWN_MOST: u8 = 8;
pub const CROWN_MS_X10: i32 = 50;
pub const CROWN_MS_EACH_X10: i32 = 25;
/// 「战斗中」：这么多 tick 里打中过英雄或者挨过打（英雄联盟离开战斗 7 秒）。
pub const COMBAT_T: usize = 420;
/// 无尽收割：8 秒一次、蓄力 1.25 秒，外圈半径、内圈半径，外圈每打中一个回复 18% 已损失生命、冷却 -10%（最少 3 秒）。
pub const DECI_CD: usize = 480;
pub const DECI_WINDUP: usize = 75;
pub const DECI_MIN_CD: usize = 180;
pub const DECI_R: u64 = 46_000;
pub const DECI_INNER: u64 = 24_000;
pub const DECI_HEAL_PCT: usize = 18;
pub const DECI_CUT_PCT: usize = 10;
pub fn deci_damage(level: usize, ad: usize, ap: usize) -> usize {
    by_level(100, 400, level) + ad * 60 / 100 + ap * 40 / 100
}
/// 小蜜蜂：蜂巢飞 1.1 秒，落点半径，叮 4 下、每 0.5 秒一下，减速 20%（2 秒），冷却 15～10 秒。
pub const BEES_FLIGHT: usize = 66;
pub const BEES_R: u64 = 42_500;
pub const BEES_STINGS: u8 = 4;
pub const BEES_EVERY: usize = 30;
pub const BEES_SLOW: i32 = 20;
pub const BEES_SLOW_T: usize = 120;
pub fn bees_cd(level: usize) -> usize {
    900 - by_level(0, 300, level)
}
/// 一下：一共 75～140 + 150% 攻击力 + 70% 法强，分 4 下。
pub fn bees_sting(level: usize, ad: usize, ap: usize) -> usize {
    (by_level(75, 140, level) + ad * 150 / 100 + ap * 70 / 100) / BEES_STINGS as usize
}
/// 亡命之徒：每打中一个英雄一层（6 秒，最多 10 层；同一个人 1/3 秒算一次），倒下 4 秒，之后 15 秒的加成，冷却 90 秒。
pub const HELL_MOST: usize = 10;
pub const HELL_STACK_T: usize = 360;
pub const HELL_GAP: usize = 20;
pub const HELL_DOWN: usize = 240;
pub const HELL_BUFF_T: usize = 900;
pub const HELL_CD: usize = 5_400;
/// 叠满以后剩这么多生命（%）就算挨了致命的一下（「不会死」那层 buff 把他留在 1 点生命）。
pub const HELL_LOW_PCT: usize = 1;
pub fn hell_hp_pct(level: usize) -> usize {
    by_level(35, 75, level)
}
pub fn hell_ad(level: usize) -> usize {
    by_level(25, 200, level)
}
pub fn hell_ap(level: usize) -> usize {
    by_level(50, 400, level)
}
pub fn hell_ms(level: usize) -> usize {
    by_level(20, 40, level)
}
pub fn hell_vamp(level: usize) -> usize {
    by_level(15, 30, level)
}
pub const WAKE_DELAY: usize = 36;
pub const WAKE_WIDTH: u64 = 12_000;
pub fn wake_damage(level: usize, ad: usize, ap: usize) -> usize {
    by_level(90, 250, level) + ad * 80 / 100 + ap * 40 / 100
}

// ===================== buff 名 =====================

pub const D_LICH: &str = "league_hextech_d:lich_brain";
pub const D_HOME: &str = "league_hextech_d:homeguard";
pub const D_LONELY: &str = "league_hextech_d:lonely_warrior";
pub const D_KILLSEC: &str = "league_hextech_d:kill_secured";
pub const D_STEAD: &str = "league_hextech_d:steadfast";
pub const D_STILL: &str = "league_hextech_d:still_here";
pub const D_EUREKA: &str = "league_hextech_d:eureka";
/// 泰坦的坚决叠满（高清帧引擎按这个名字放大身体）。
pub const D_TITAN: &str = "league_hextech_d:titans_resolve";
pub const S_RECUR: &str = "league_hextech_s:inf_recursion";
pub const S_SLAP: &str = "league_hextech_s:slap_around";
pub const S_SOUL: &str = "league_hextech_s:soul_eater";
pub const S_MOSH: &str = "league_hextech_s:mosh_monster";
pub const E_AWAKE: &str = "league_hextech_e:ult_awakening";
pub const E_EROSION: &str = "league_hextech_e:erosion";
pub const E_UNSTOP: &str = "league_hextech_e:ult_unstoppable";
pub const E_MIGHTY: &str = "league_hextech_e:mighty_shield";
pub const E_FOX: &str = "league_hextech_e:firefox";
pub const E_SHADOW: &str = "league_hextech_e:shadow_runner";
pub const E_DIVINE: &str = "league_hextech_e:divine";
pub const E_NIGHT: &str = "league_hextech_e:nightstalking";
pub const E_GRIT: &str = "league_hextech_e:outlaws_grit";
pub const E_PORC: &str = "league_hextech_e:porcupine_slow";
pub const E_SHARK: &str = "league_hextech_e:shark_bait";
pub const E_SONATA: &str = "league_hextech_e:sonata";
pub const E_TOUCH: &str = "league_hextech_e:cant_touch";
pub const E_DUAL_AP: &str = "league_hextech_e:duality_ap";
pub const E_DUAL_AD: &str = "league_hextech_e:duality_ad";
/// 狂舞怪兽放大招后的那几秒（高清帧引擎按这个名字放大身体）。
pub const E_MOSH: &str = "league_hextech_e:mosh_monster";
pub const E_MOSH_SLOW: &str = "league_hextech_e:mosh_slow";
pub const E_PROM: &str = "league_hextech_e:prom_queen";
pub const E_FEY: &str = "league_hextech_e:fey_magic";
pub const D_ADAPT: &str = "league_hextech_d:adapt";
pub const D_ESCAPADE: &str = "league_hextech_d:escapade";
pub const D_CROWN: &str = "league_hextech_d:heavy_crown";
pub const E_BEES: &str = "league_hextech_e:bees_slow";
pub const E_HELL_GUARD: &str = "league_hextech_e:hellbent_guard";
pub const E_HELL_DOWN: &str = "league_hextech_e:hellbent_down";
pub const E_HELL: &str = "league_hextech_e:hellbent";

pub const BUFFS: [&str; 38] = [D_LICH, D_HOME, D_LONELY, D_KILLSEC, D_STEAD, D_STILL, D_EUREKA, D_TITAN, S_RECUR, S_SLAP,
                                S_SOUL, S_MOSH, E_AWAKE, E_EROSION, E_UNSTOP, E_MIGHTY, E_FOX, E_SHADOW, E_DIVINE, E_NIGHT,
                                E_GRIT, E_PORC, E_SHARK, E_SONATA, E_TOUCH, E_DUAL_AP, E_DUAL_AD, E_MOSH, E_MOSH_SLOW,
                                E_PROM, E_FEY, D_ADAPT, D_ESCAPADE, D_CROWN, E_BEES, E_HELL_GUARD, E_HELL_DOWN, E_HELL];

/// 打中英雄时要看的（0.4.0 的；后三个看「战斗中」）。
pub const ON_HIT: [Ev; 19] = [Ev::GlassCannon, Ev::GiantSlayer, Ev::Erosion, Ev::Marksmage, Ev::SapMagic, Ev::TakeEmDown,
                              Ev::SkilledSniper, Ev::Duality, Ev::Grab, Ev::ThirdTime, Ev::FeyMagic, Ev::DualWield,
                              Ev::TwinFire, Ev::Goredrink, Ev::Bees, Ev::Hellbent, Ev::SlimeTime, Ev::Decimation,
                              Ev::HeavyCrown];
/// 控住敌人时要看的（0.4.0 的）。
pub const ON_CC: [Ev; 3] = [Ev::GuiltyPleasure, Ev::SlapAround, Ev::SoulEater];

pub(super) fn timed(name: &str, ticks: usize, f: impl FnOnce(&mut BuffV1)) -> BuffV1 {
    super::timed(name, ticks, f)
}

pub(super) fn named(name: &str, f: impl FnOnce(&mut BuffV1)) -> BuffV1 {
    let mut b = BuffV1::named(name);
    f(&mut b);
    b
}

/// 技能格的编号（1 技能、2 技能 2、3 大招）对应的格子。
pub(super) fn slot(k: usize) -> SkillSlotV1 {
    match k {
        1 => SkillSlotV1::Skill,
        2 => SkillSlotV1::Skill2,
        _ => SkillSlotV1::Ult,
    }
}

/// 点到线段的距离的平方（模拟单位）。
pub fn seg_d2(p: (u64, u64), a: (u64, u64), b: (u64, u64)) -> u64 {
    let (px, py, ax, ay, bx, by) = (p.0 as f64, p.1 as f64, a.0 as f64, a.1 as f64, b.0 as f64, b.1 as f64);
    let (dx, dy) = (bx - ax, by - ay);
    let len2 = dx * dx + dy * dy;
    let t = if len2 <= 0.0 { 0.0 } else { (((px - ax) * dx + (py - ay) * dy) / len2).clamp(0.0, 1.0) };
    let (qx, qy) = (ax + t * dx, ay + t * dy);
    ((px - qx).powi(2) + (py - qy).powi(2)) as u64
}

/// 一个座位 0.4.0 的状态（跟着玩家：死了不清）。
#[derive(Clone, Debug, Default)]
pub struct Seat {
    /// 随场上变的属性现在挂着的：(名字, 挂在哪个实体上, 档)
    dyn_on: Vec<(&'static str, usize, i64)>,
    /// 叠层：左右开弓的攻击力层、法强层，噬魂者，狂舞怪兽的永久生命，无限递归
    slap_ad: u16,
    slap_ap: u16,
    soul: u16,
    mosh: u16,
    recur: u16,
    /// 上次挂叠层 buff 时：(实体, 上面五个数)
    applied: Option<(usize, [u16; 5])>,
    /// 刺猬存的伤害
    porcupine: usize,
    /// 拿下他们：(目标座位, 层数, 到这个 tick)
    takes: Vec<(usize, u8, usize)>,
    /// 事不过三：(目标座位, 普攻命中几次)
    thirds: Vec<(usize, u32)>,
    /// 泰坦的坚决：每层到哪个 tick
    titan: Vec<usize>,
    /// 奏鸣曲：下一次是加速（不是：治疗）
    sonata_speed: bool,
    /// 软软抓抓：牵住的 (座位, 实体) 和到哪个 tick
    tethers: Vec<(usize, usize)>,
    tether_until: usize,
    /// 舞会女王：冲刺到哪个 tick、这一次魅惑过的座位
    prom_until: usize,
    prom_hit: Vec<usize>,
    /// 死亡之环攒下的回复
    circle: usize,
    // ---- 第二批
    /// 第一次看到他时的攻击力（物理转魔法按比它多出来的算）
    ad0: Option<usize>,
    /// 王冠之重的层数
    crown: u8,
    /// 最后一次打中英雄或者挨打的 tick（「战斗中」）
    fought: Option<usize>,
    /// 亡命之徒：每层到哪个 tick；倒下了：到哪个 tick 站起来
    hell: Vec<usize>,
    hell_down: Option<usize>,
    /// 史莱姆时间留在地上的黏液：(在哪, 到哪个 tick)
    blobs: Vec<((u64, u64), usize)>,
}

/// 过一会儿才发生的。
#[derive(Clone, Debug)]
pub enum Later {
    /// 神圣干预：到时给 `holder` 身边的友方英雄无敌
    Divine { holder: usize, hent: usize, at: usize },
    /// 鲨鱼饵：到时咬
    Shark { holder: usize, hent: usize, at: usize, base: usize },
    /// 杀戮时刻：到时引爆（打印记时他的生命）
    Mark { holder: usize, hent: usize, v: usize, vent: usize, hp0: usize, at: usize },
    /// 终极革命：到时大招转好
    Revolution { holder: usize, hent: usize, at: usize },
    /// 回旋刃：到时沿 `from`-`to` 打一次（`back`：回程）
    Boomerang { holder: usize, hent: usize, from: (u64, u64), to: (u64, u64), at: usize, back: bool, base: usize },
    /// 裂痕：到时爆开
    Crack { holder: usize, hent: usize, from: (u64, u64), to: (u64, u64), at: usize, base: usize },
    /// 软软抓抓拉过来以后眩晕
    Stun { holder: usize, v: usize, vent: usize, at: usize },
    /// 无尽收割：蓄完力挥斧
    Decimate { holder: usize, hent: usize, at: usize, base: usize },
    /// 小蜜蜂：蜂巢落到 `pos`
    Hive { holder: usize, hent: usize, pos: (u64, u64), at: usize, sting: usize },
    /// 小蜜蜂：蜂群再叮一下（还剩 `left` 下）
    Sting { holder: usize, hent: usize, v: usize, vent: usize, at: usize, left: u8, sting: usize },
    /// 亡命之徒：倒下 4 秒后站起来
    Revive { holder: usize, hent: usize, at: usize },
}

impl Later {
    fn at(&self) -> usize {
        match *self {
            Later::Divine { at, .. } | Later::Shark { at, .. } | Later::Mark { at, .. } | Later::Revolution { at, .. }
            | Later::Boomerang { at, .. } | Later::Crack { at, .. } | Later::Stun { at, .. }
            | Later::Decimate { at, .. } | Later::Hive { at, .. } | Later::Sting { at, .. } | Later::Revive { at, .. } => at,
        }
    }
}

impl Procs {
    /// 这一步他位移了没有：(从哪, 到哪)。
    fn dashed(&self, now: usize, h: usize, looks: &[L]) -> Option<((u64, u64), (u64, u64))> {
        let p = &self.pls[h];
        let from = p.prev_pos?;
        let to = looks[h].pos;
        let d = (d2(from, to) as f64).sqrt() as u64;
        let walk = p.speed.max(500) as u64 * EVERY as u64;
        let cast = p.cast[1..].iter().flatten().any(|&t| now <= t + DASH_WINDOW);
        (cast && d * 10 > walk * DASH_X10 && d >= DASH_MIN).then_some((from, to))
    }

    pub(super) fn ready_at(&self, h: usize, ev: Ev, now: usize) -> bool {
        now >= self.pls[h].ready[ev as usize]
    }

    pub(super) fn arm(&mut self, h: usize, ev: Ev, until: usize) {
        self.pls[h].ready[ev as usize] = until;
    }

    /// 一个随场上变的属性：档变了（或者换了身体）才重挂；档是 0 就摘掉。-> 这一次挂上了（不是 0 的档）没有（0.5.2：算一次触发）
    pub(super) fn dyn_set(&mut self, sim: &mut StableSim<'_>, h: usize, ent: usize, name: &'static str, key: i64,
               build: impl FnOnce(i64) -> BuffV1) -> bool {
        let on = &mut self.pls[h].b2.dyn_on;
        let at = on.iter().position(|x| x.0 == name);
        if let Some(i) = at {
            if on[i].1 == ent && on[i].2 == key {
                return false;
            }
            if on[i].1 == ent {
                sim.entity_remove_buff(ent, name);
            }
            on.remove(i);
        } else if key == 0 {
            return false;
        }
        if key != 0 {
            sim.add_buff(ent, &build(key));
        }
        self.pls[h].b2.dyn_on.push((name, ent, key));
        key != 0
    }

    /// 叠一层限时的（`most` 层封顶，再叠刷新时间）。
    pub(super) fn stack_timed(sim: &mut StableSim<'_>, ent: usize, b: &BuffV1, most: usize) {
        if sim.entity_stack_buff(ent, b, most, true) == 0 {
            sim.add_buff(ent, b);
        }
    }

    /// 这一步死了的：坦克引擎留 35%、左右开弓掉一半；俯冲轰炸炸开。
    #[allow(clippy::too_many_arguments)]
    pub(super) fn b2_deaths(&mut self, sim: &mut StableSim<'_>, now: usize, who: &[Who], held: &[EvSet], looks: &[L],
                            names: &[String], screen: bool) {
        for h in 0..who.len() {
            let Some(at) = self.pls[h].died_at else { continue };
            let set = held[h];
            if set & Ev::TankEngine.bit() != 0 && self.pls[h].tank > 0 {
                self.pls[h].tank = self.pls[h].tank * TANK_KEEP_PCT / 100;
            }
            if set & Ev::SlapAround.bit() != 0 {
                let s = &mut self.pls[h].b2;
                (s.slap_ad, s.slap_ap) = (s.slap_ad / 2, s.slap_ap / 2);
            }
            {
                let s = &mut self.pls[h].b2;
                s.crown /= 2;
                s.hell.clear();
                s.hell_down = None;
            }
            if set & Ev::DiveBomber.bit() != 0 {
                let Some(dent) = self.pls[h].ent else { continue };
                let team = who[h].team;
                let hit: Vec<usize> = (0..looks.len())
                    .filter(|&v| looks[v].alive && looks[v].team != team && within(looks[v].pos, at, DIVE_R))
                    .collect();
                for &v in &hit {
                    let amount = looks[v].max * DIVE_PCT / 100;
                    self.hit(sim, now, h, dent, looks[v].ent, amount, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                }
                self.fire(Ev::DiveBomber);
                let n = hit.len();
                self.say(screen, || format!("PROC dive_bomber {} explodes on death: {n} champions hit", names[h]));
                self.show(screen, now, Show::RingRed, at, vec![(DIVE_R, 0)], 30);
                self.show(screen, now, Show::Heavy, at, Vec::new(), 0);
            }
        }
    }

    /// 一个活着的座位这一步的 0.4.0 效果。
    #[allow(clippy::too_many_arguments)]
    pub(super) fn b2_seat(&mut self, sim: &mut StableSim<'_>, now: usize, h: usize, who: &[Who], set: EvSet, looks: &[L],
                          hit: Option<&Hit>, cc: Option<usize>, names: &[String], screen: bool) {
        let me = looks[h];
        let level = self.pls[h].level;
        let (ad, ap) = ad_ap(sim, me.ent);
        let cast = self.pls[h].cast;
        let at_now = |k: usize| cast[k] == Some(now);
        let has = |ev: Ev| set & ev.bit() != 0;
        let takedowns = self.kills_now.iter().filter(|k| k.0.contains(&h)).count();
        let dash = self.dashed(now, h, looks);
        let first = hit.map(|x| x.victims[0]);
        if hit.is_some() || self.pls[h].taken > 0 {
            self.pls[h].b2.fought = Some(now);
        }
        let fighting = self.pls[h].b2.fought.is_some_and(|t| now < t + COMBAT_T);
        if self.pls[h].b2.ad0.is_none() {
            self.pls[h].b2.ad0 = Some(ad);
        }

        // ---------- 对齐的四个 ----------
        if let (Some(x), Some(v)) = (hit, first) {
            if has(Ev::GlassCannon) && x.delta > 0 {
                let pct = if who[h].ranged { GLASS_RANGED_PCT } else { GLASS_MELEE_PCT };
                let amount = (x.delta * pct / 100) as usize;
                self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                self.fire(Ev::GlassCannon);
                if self.gate(h, Ev::GlassCannon, v, now, 60) {
                    self.show(screen, now, Show::Execute, looks[v].pos, Vec::new(), 0);
                }
            }
            if has(Ev::GiantSlayer) && x.delta > 0 && me.max > 0 {
                let ratio = looks[v].max * 100 / me.max;
                if let Some(&(_, pct)) = SLAYER_STEPS.iter().find(|s| ratio >= s.0) {
                    let amount = (x.delta * pct / 100) as usize;
                    self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                    self.fire(Ev::GiantSlayer);
                    if self.gate(h, Ev::GiantSlayer, v, now, 60) {
                        self.show(screen, now, Show::Heavy, looks[v].pos, Vec::new(), 0);
                    }
                }
            }
        }
        if has(Ev::Archmage) {
            for k in 1..4 {
                if !at_now(k) || self.pls[h].full[k] == 0 {
                    continue;
                }
                let cds = self.pls[h].cds.map_or([0; 4], |c| c.1);
                let others: Vec<usize> = (1..4).filter(|&o| o != k && cds[o] > 0).collect();
                if others.is_empty() {
                    continue;
                }
                let o = others[(splitmix(now as u64 ^ ((h as u64) << 40) ^ k as u64) % others.len() as u64) as usize];
                let cut = self.pls[h].full[k] * ARCHMAGE_PCT / 100;
                sim.entity_reduce_cooldown(me.ent, slot(o), cut);
                self.fire(Ev::Archmage);
                if self.gate(h, Ev::Archmage, h, now, 60) {
                    self.show(screen, now, Show::Ether, me.pos, Vec::new(), 0);
                }
            }
        }
        if has(Ev::UltAwakening) && at_now(3) && self.ready_at(h, Ev::UltAwakening, now) {
            self.arm(h, Ev::UltAwakening, now + AWAKE_CD);
            sim.entity_reduce_cooldown(me.ent, SkillSlotV1::Skill, RESET);
            sim.entity_reduce_cooldown(me.ent, SkillSlotV1::Skill2, RESET);
            put_timed(sim, me.ent, &timed(E_AWAKE, AWAKE_T, |b| b.skill_cooldown_mult = AWAKE_HASTE));
            self.fire(Ev::UltAwakening);
            self.say(screen, || format!("PROC ultimate_awakening {}: skills ready, 15 s of haste", names[h]));
            self.show(screen, now, Show::RingCyan, me.pos, vec![(25_000, 0)], 30);
            self.show(screen, now, Show::LightPop, me.pos, Vec::new(), 0);
        }

        // ---------- 随场上变的属性 ----------
        if has(Ev::LichBrain) {
            let key = (me.max * LICH_PCT / 100 / 10 * 10) as i64;
            if self.dyn_set(sim, h, me.ent, D_LICH, key, |k| named(D_LICH, |b| b.magic_power = k as i32)) {
                self.fire(Ev::LichBrain);
            }
        }
        if has(Ev::Homeguard) {
            let on = self.pls[h].last_hurt.is_none_or(|t| now >= t + HOME_IDLE);
            if self.dyn_set(sim, h, me.ent, D_HOME, on as i64, |_| named(D_HOME, |b| b.move_speed_mult = HOME_MS)) {
                self.fire(Ev::Homeguard);
            }
        }
        if has(Ev::LonelyWarrior) {
            let n = enemies_near(looks, h, me.pos, LONELY_R).len().min(LONELY_MOST) as i64;
            if self.dyn_set(sim, h, me.ent, D_LONELY, n, |n| {
                named(D_LONELY, |b| {
                    b.attack_speed_mult = LONELY_AS * n as i32;
                    b.defence = LONELY_RES * n as i32;
                    b.magic_resistance = LONELY_RES * n as i32;
                })
            }) {
                self.fire(Ev::LonelyWarrior);
            }
        }
        if has(Ev::KillSecured) {
            let on = enemies_near(looks, h, me.pos, KILLSEC_R).iter().any(|&v| below(looks[v].hp, looks[v].max, KILLSEC_PCT));
            if self.dyn_set(sim, h, me.ent, D_KILLSEC, on as i64, |_| named(D_KILLSEC, |b| b.move_speed_mult = KILLSEC_MS)) {
                self.fire(Ev::KillSecured);
            }
        }
        if has(Ev::Steadfast) {
            let on = below(me.hp, me.max, STEAD_PCT);
            if self.dyn_set(sim, h, me.ent, D_STEAD, on as i64, |_| {
                named(D_STEAD, |b| {
                    b.toughness = 20;
                    b.defence_mult = 16;
                    b.magic_resistance_mult = 16;
                })
            }) {
                self.fire(Ev::Steadfast);
            }
        }
        if has(Ev::StillHere) && me.max > 0 {
            let tenths = (me.max.saturating_sub(me.hp) * 10 / me.max).min(9) as i64;
            if self.dyn_set(sim, h, me.ent, D_STILL, tenths, |k| {
                named(D_STILL, |b| {
                    b.attack_speed_mult = STILL_AS * k as i32;
                    b.vamp = STILL_VAMP * k as i32;
                })
            }) {
                self.fire(Ev::StillHere);
            }
        }
        if has(Ev::Eureka) {
            let haste = (ap * EUREKA_PER_100 / 100 / 5 * 5) as i64;
            if self.dyn_set(sim, h, me.ent, D_EUREKA, haste, |k| {
                named(D_EUREKA, |b| {
                    b.skill_cooldown_mult = k as i32;
                    b.ult_cooldown_mult = k as i32;
                })
            }) {
                self.fire(Ev::Eureka);
            }
        }
        if has(Ev::Adapt) {
            let bonus = ad.saturating_sub(self.pls[h].b2.ad0.unwrap_or(ad)) / 5 * 5;
            if self.dyn_set(sim, h, me.ent, D_ADAPT, bonus as i64 + 1, |k| {
                named(D_ADAPT, |b| {
                    b.magic_power = ((k - 1) as usize * 10 / ADAPT_AD_X10) as i32;
                    b.magic_power_mult = ADAPT_AP_MULT;
                })
            }) {
                self.fire(Ev::Adapt);
            }
        }
        if has(Ev::Escapade) {
            let key = (ap / 5 * 5) as i64 + 1;
            if self.dyn_set(sim, h, me.ent, D_ESCAPADE, key, |k| {
                named(D_ESCAPADE, |b| {
                    b.attack = ((k - 1) as usize * 100 / ESC_AP_X100) as i32;
                    b.attack_mult = ESC_AD_MULT;
                })
            }) {
                self.fire(Ev::Escapade);
            }
        }
        if has(Ev::HeavyCrown) {
            if takedowns > 0 && self.pls[h].b2.crown < CROWN_MOST {
                let s = &mut self.pls[h].b2;
                s.crown = (s.crown + takedowns as u8).min(CROWN_MOST);
                self.fire(Ev::HeavyCrown);
                self.show(screen, now, Show::Grow, me.pos, Vec::new(), 0);
            }
            let key = self.pls[h].b2.crown as i64 * 2 + fighting as i64 + 1;
            self.dyn_set(sim, h, me.ent, D_CROWN, key, |k| {
                let (n, fight) = (((k - 1) / 2) as i32, (k - 1) % 2 == 1);
                named(D_CROWN, |b| {
                    let pct = CROWN_PCT + CROWN_EACH * n;
                    b.attack = CROWN_AD;
                    b.magic_power = CROWN_AP;
                    b.attack_mult = pct;
                    b.magic_power_mult = pct;
                    b.attack_speed_mult = pct;
                    if fight {
                        b.move_speed_mult = -(CROWN_MS_X10 + CROWN_MS_EACH_X10 * n) / 10;
                    }
                })
            });
        }
        if has(Ev::InfRecursion) && takedowns > 0 {
            let s = &mut self.pls[h].b2;
            s.recur = (s.recur + takedowns as u16).min(RECUR_MOST);
            self.fire(Ev::InfRecursion);
            self.show(screen, now, Show::LightPop, me.pos, Vec::new(), 0);
        }

        // ---------- 打中英雄 ----------
        if let (Some(x), Some(v)) = (hit, first) {
            if has(Ev::Erosion) {
                for &u in &x.victims {
                    let b = timed(E_EROSION, EROSION_T, |b| {
                        b.defence_mult = -EROSION_PCT;
                        b.magic_resistance_mult = -EROSION_PCT;
                    });
                    Self::stack_timed(sim, looks[u].ent, &b, EROSION_MOST);
                    if self.gate(h, Ev::Erosion, u, now, 120) {
                        self.fire(Ev::Erosion);
                        self.show(screen, now, Show::Crack, looks[u].pos, Vec::new(), 0);
                    }
                }
            }
            if has(Ev::Marksmage) && x.basic {
                let amount = ap * MARKSMAGE_PCT / 100;
                self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
                self.fire(Ev::Marksmage);
                if self.gate(h, Ev::Marksmage, v, now, 30) {
                    self.show(screen, now, Show::Punch, looks[v].pos, Vec::new(), 0);
                }
            }
            if has(Ev::SapMagic) && x.basic && self.ready_at(h, Ev::SapMagic, now) {
                self.arm(h, Ev::SapMagic, now + SAP_CD);
                let amount = by_level(80, 300, level);
                self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
                let heal = by_level(50, 250, level) + me.max * 8 / 100;
                sim.heal(me.ent, me.ent, heal);
                self.fire(Ev::SapMagic);
                self.say(screen, || format!("PROC sap_magic {} -> {}: {amount} physical, healed {heal}", names[h], names[v]));
                self.show(screen, now, Show::Ether, looks[v].pos, Vec::new(), 0);
            }
            if has(Ev::TakeEmDown) && self.gate(h, Ev::TakeEmDown, v, now, TAKE_GAP) {
                let takes = &mut self.pls[h].b2.takes;
                takes.retain(|t| t.2 > now);
                let n = match takes.iter_mut().find(|t| t.0 == v) {
                    Some(t) => {
                        t.1 += 1;
                        t.2 = now + TAKE_T;
                        t.1
                    }
                    None => {
                        takes.push((v, 1, now + TAKE_T));
                        1
                    }
                };
                if n >= TAKE_N {
                    takes.retain(|t| t.0 != v);
                    let amount = looks[v].max.saturating_sub(looks[v].hp) * TAKE_PCT / 100;
                    self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    sim.heal(me.ent, me.ent, amount * TAKE_HEAL_PCT / 100);
                    self.fire(Ev::TakeEmDown);
                    self.say(screen, || format!("PROC take_em_down {} -> {}: {amount} magic", names[h], names[v]));
                    self.show(screen, now, Show::Execute, looks[v].pos, Vec::new(), 0);
                }
            }
            if has(Ev::SkilledSniper) {
                if let Some(k) = x.skill {
                    let far = d2(me.pos, looks[v].pos) >= SNIPER_FAR * SNIPER_FAR;
                    if far && self.pls[h].full[k] > 0 && self.gate(h, Ev::SkilledSniper, k, now, 60) {
                        let cut = self.pls[h].full[k] * SNIPER_PCT / 100;
                        sim.entity_reduce_cooldown(me.ent, slot(k), cut);
                        self.fire(Ev::SkilledSniper);
                        self.show(screen, now, Show::LightPop, me.pos, Vec::new(), 0);
                    }
                }
            }
            if has(Ev::Duality) {
                if x.basic && self.gate(h, Ev::Duality, 0, now, DUAL_GAP) {
                    let b = timed(E_DUAL_AP, DUAL_T, |b| b.magic_power = by_level(10, 30, level) as i32);
                    Self::stack_timed(sim, me.ent, &b, DUAL_MOST);
                    self.fire(Ev::Duality);
                }
                if x.skill.is_some() && self.gate(h, Ev::Duality, 1, now, DUAL_GAP) {
                    let b = timed(E_DUAL_AD, DUAL_T, |b| b.attack = by_level(6, 18, level) as i32);
                    Self::stack_timed(sim, me.ent, &b, DUAL_MOST);
                    self.fire(Ev::Duality);
                }
            }
            if has(Ev::Grab) && x.basic && !self.pls[h].b2.tethers.is_empty() && now < self.pls[h].b2.tether_until {
                let tethers = std::mem::take(&mut self.pls[h].b2.tethers);
                let mut pulled = 0;
                for (u, uent) in tethers {
                    if !looks.get(u).is_some_and(|l| l.alive && l.ent == uent) {
                        continue;
                    }
                    let (dx, dy) = (me.pos.0 as i64 - looks[u].pos.0 as i64, me.pos.1 as i64 - looks[u].pos.1 as i64);
                    let dist = ((d2(me.pos, looks[u].pos) as f64).sqrt() as u64).saturating_sub(12_000);
                    let pull = CcV1 { kind: CcKindV1::ForceMove.code(), tick: GRAB_PULL as u64, dx, dy,
                                      speed: dist / GRAB_PULL as u64, ..CcV1::default() };
                    sim.apply_cc(uent, &pull);
                    self.own_cc.push((uent, now + GRAB_PULL + GRAB_STUN as usize + EVERY));
                    self.later.push(Later::Stun { holder: h, v: u, vent: uent, at: now + GRAB_PULL });
                    let amount = by_level(50, 150, level);
                    self.hit(sim, now, h, me.ent, uent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    self.show(screen, now, Show::Heavy, looks[u].pos, Vec::new(), 0);
                    pulled += 1;
                }
                if pulled > 0 {
                    sim.entity_add_shield(me.ent, GRAB_SHIELD * pulled, GRAB_SHIELD_T);
                    self.guarded(screen, h, me.ent, now, GRAB_SHIELD_T);
                    self.fire(Ev::Grab);
                    self.say(screen, || format!("PROC squishy_slappy_grab {} pulls {pulled} champions", names[h]));
                }
            }
            if has(Ev::ThirdTime) && x.basic && self.gate(h, Ev::ThirdTime, v, now, THIRD_GAP) {
                let thirds = &mut self.pls[h].b2.thirds;
                let n = match thirds.iter_mut().find(|t| t.0 == v) {
                    Some(t) => {
                        t.1 += 1;
                        t.1
                    }
                    None => {
                        thirds.push((v, 1));
                        1
                    }
                };
                if n.is_multiple_of(3) {
                    let pct = if who[h].ranged { THIRD_RANGED_PCT } else { THIRD_MELEE_PCT };
                    let amount = looks[v].max * pct / 100;
                    self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                    self.fire(Ev::ThirdTime);
                    self.show(screen, now, Show::Execute, looks[v].pos, Vec::new(), 0);
                }
            }
            if has(Ev::FeyMagic) && x.skill == Some(3) {
                for &u in &x.victims {
                    if self.gate(h, Ev::FeyMagic, u, now, FEY_GAP) {
                        sim.apply_cc(looks[u].ent, &CcV1::of_kind(CcKindV1::BlockAttack, FEY_T));
                        put_timed(sim, looks[u].ent, &timed(E_FEY, FEY_T as usize, |b| b.move_speed_mult = -FEY_SLOW));
                        self.fire(Ev::FeyMagic);
                        self.show(screen, now, Show::Wisp, looks[u].pos, Vec::new(), 0);
                    }
                }
            }
            if has(Ev::TwinFire) && x.skill.is_some() && self.ready_at(h, Ev::TwinFire, now) {
                self.arm(h, Ev::TwinFire, now + TWIN_CD);
                let crit = sim.get_entity(me.ent).map_or(0, |e| e.stat().crit_chance);
                let base = twin_damage(level, ad, ap);
                let d = (d2(me.pos, looks[v].pos) as f64).sqrt() as u64;
                let t = ((d / MISSILE_SPEED) as usize).max(MISSILE_MIN_T);
                for j in 0..twin_n(crit) {
                    self.shots.push(Shot { kind: Kind::Fox, holder: h, hent: me.ent, team: me.team,
                                           target: Some((v, looks[v].ent)), at: looks[v].pos, land: now + t + j * MISSILE_GAP,
                                           base });
                    self.show(screen, now + j * MISSILE_GAP, Show::Missile, me.pos, vec![looks[v].pos], t);
                }
                self.fire(Ev::TwinFire);
            }
            if has(Ev::Goredrink) && x.delta > 0 {
                let heal = (x.delta * GORE_PCT / 100) as usize;
                if heal > 0 {
                    sim.heal(me.ent, me.ent, heal);
                    self.fire(Ev::Goredrink);
                }
            }
            if has(Ev::Hellbent) && self.pls[h].b2.hell_down.is_none() {
                for &u in &x.victims {
                    if self.gate(h, Ev::Hellbent, u, now, HELL_GAP) {
                        let s = &mut self.pls[h].b2;
                        s.hell.retain(|&t| t > now);
                        s.hell.push(now + HELL_STACK_T);
                        if s.hell.len() > HELL_MOST {
                            s.hell.remove(0);
                        }
                    }
                }
            }
            if has(Ev::Bees) && x.skill.is_some() && self.ready_at(h, Ev::Bees, now) {
                self.arm(h, Ev::Bees, now + bees_cd(level));
                let pos = looks[v].pos;
                self.later.push(Later::Hive { holder: h, hent: me.ent, pos, at: now + BEES_FLIGHT,
                                              sting: bees_sting(level, ad, ap).max(1) });
                self.fire(Ev::Bees);
                self.show(screen, now, Show::Hive, me.pos, vec![pos], BEES_FLIGHT);
            }
            if has(Ev::DualWield) && x.basic {
                let base = ad * DUALW_PCT / 100;
                self.shots.push(Shot { kind: Kind::Bolt, holder: h, hent: me.ent, team: me.team,
                                       target: Some((v, looks[v].ent)), at: looks[v].pos, land: now + DUALW_DELAY,
                                       base: base.max(1) });
                self.fire(Ev::DualWield);
                self.show(screen, now, Show::Missile, me.pos, vec![looks[v].pos], DUALW_DELAY);
            }
        }

        // ---------- 控住敌人 ----------
        if let Some(v) = cc {
            if has(Ev::GuiltyPleasure) && self.ready_at(h, Ev::GuiltyPleasure, now) {
                self.arm(h, Ev::GuiltyPleasure, now + GUILTY_CD);
                let heal = guilty_heal(level, me.max);
                sim.heal(me.ent, me.ent, heal);
                self.fire(Ev::GuiltyPleasure);
                self.say(screen, || format!("PROC guilty_pleasure {} immobilized {}: healed {heal}", names[h], names[v]));
                self.show(screen, now, Show::Dawn, me.pos, Vec::new(), 0);
            }
            if has(Ev::SlapAround) && self.ready_at(h, Ev::SlapAround, now) {
                self.arm(h, Ev::SlapAround, now + SLAP_CD);
                let s = &mut self.pls[h].b2;
                if s.slap_ad + s.slap_ap < SLAP_MOST {
                    if ad * 2 >= ap {
                        s.slap_ad += 1;
                    } else {
                        s.slap_ap += 1;
                    }
                }
                self.fire(Ev::SlapAround);
                self.show(screen, now, Show::Punch, me.pos, Vec::new(), 0);
            }
            if has(Ev::SoulEater) && self.ready_at(h, Ev::SoulEater, now) {
                self.arm(h, Ev::SoulEater, now + SOUL_CD);
                let s = &mut self.pls[h].b2;
                s.soul = (s.soul + 1).min(SOUL_MOST);
                self.fire(Ev::SoulEater);
                self.show(screen, now, Show::Grow, me.pos, Vec::new(), 0);
            }
        }

        // ---------- 放大招 ----------
        if at_now(3) {
            if has(Ev::UltUnstoppable) && self.ready_at(h, Ev::UltUnstoppable, now) {
                self.arm(h, Ev::UltUnstoppable, now + UNSTOP_CD);
                put_timed(sim, me.ent, &timed(E_UNSTOP, UNSTOP_T, |b| b.toughness = UNSTOP_TENACITY));
                self.fire(Ev::UltUnstoppable);
                self.show(screen, now, Show::RingGold, me.pos, vec![(20_000, 0)], 24);
            }
            if has(Ev::CantTouch) && self.ready_at(h, Ev::CantTouch, now) {
                self.arm(h, Ev::CantTouch, now + TOUCH_CD);
                put_timed(sim, me.ent, &timed(E_TOUCH, TOUCH_T, |b| b.damaged_reduce = 100));
                self.holy(screen, h, me.ent, now, TOUCH_T);
                self.fire(Ev::CantTouch);
                self.say(screen, || format!("PROC cant_touch_this {}: ultimate - 2 s invulnerable", names[h]));
                self.show(screen, now, Show::Ward, me.pos, Vec::new(), 0);
            }
            if has(Ev::MoshMonster) {
                put_timed(sim, me.ent, &timed(E_MOSH, MOSH_T, |b| b.hp = by_level(300, 750, level) as i32));
                for u in enemies_near(looks, h, me.pos, MOSH_R) {
                    put_timed(sim, looks[u].ent, &timed(E_MOSH_SLOW, MOSH_SLOW_T, |b| b.move_speed_mult = -MOSH_SLOW));
                }
                self.fire(Ev::MoshMonster);
                self.show(screen, now, Show::RingPurple, me.pos, vec![(MOSH_R, 0)], 30);
            }
            if has(Ev::KillingTime) {
                if let Some((_, v)) = nearest(looks, h, MARK_RANGE) {
                    self.later.push(Later::Mark { holder: h, hent: me.ent, v, vent: looks[v].ent, hp0: looks[v].hp,
                                                  at: now + MARK_T });
                    self.fire(Ev::KillingTime);
                    self.say(screen, || format!("PROC its_killing_time {} marks {}", names[h], names[v]));
                    self.show(screen, now, Show::Crack, looks[v].pos, Vec::new(), 0);
                }
            }
            if has(Ev::UltRevolution) && self.ready_at(h, Ev::UltRevolution, now) {
                self.arm(h, Ev::UltRevolution, now + REVO_CD);
                self.later.push(Later::Revolution { holder: h, hent: me.ent, at: now + REVO_DELAY });
            }
        }
        if has(Ev::SapMagic) && (1..4).any(at_now) {
            let r = &mut self.pls[h].ready[Ev::SapMagic as usize];
            *r = r.saturating_sub(SAP_CAST_CUT).max(now.min(*r));
        }

        // ---------- 参与击杀 ----------
        if takedowns > 0 {
            if has(Ev::ArcaneAxiom) {
                let full = self.pls[h].full[3];
                if full > 0 {
                    sim.entity_reduce_cooldown(me.ent, SkillSlotV1::Ult, full * AXIOM_PCT / 100 * takedowns);
                    self.fire(Ev::ArcaneAxiom);
                    self.show(screen, now, Show::LightPop, me.pos, Vec::new(), 0);
                }
            }
            if has(Ev::Nightstalking) {
                sim.entity_set_invisible(me.ent, NIGHT_T);
                put_timed(sim, me.ent, &timed(E_NIGHT, NIGHT_T, |b| b.move_speed_mult = NIGHT_MS));
                self.fire(Ev::Nightstalking);
                self.show(screen, now, Show::Wisp, me.pos, Vec::new(), 0);
            }
            if has(Ev::MoshMonster) {
                let s = &mut self.pls[h].b2;
                s.mosh = (s.mosh + takedowns as u16).min(MOSH_MOST);
            }
        }

        // ---------- 获得护盾、受伤、回复 ----------
        if has(Ev::MightyShield) && self.pls[h].shield_gain > 0 && self.ready_at(h, Ev::MightyShield, now) {
            self.arm(h, Ev::MightyShield, now + MIGHTY_CD);
            let b = timed(E_MIGHTY, MIGHTY_T, |b| {
                if ad * 2 >= ap {
                    b.attack = by_level(30, 80, level) as i32;
                } else {
                    b.magic_power = by_level(60, 160, level) as i32;
                }
            });
            put_timed(sim, me.ent, &b);
            self.fire(Ev::MightyShield);
            self.show(screen, now, Show::RingGold, me.pos, vec![(16_000, 0)], 20);
        }
        if has(Ev::Porcupine) {
            self.pls[h].b2.porcupine += self.pls[h].taken;
            if self.pls[h].b2.porcupine >= porcupine_store(level) {
                self.pls[h].b2.porcupine = 0;
                let st = sim.get_entity(me.ent).map(|e| e.stat());
                let amount = porcupine_damage(level, st.map_or(0, |s| s.defence), st.map_or(0, |s| s.magic_resistance));
                for u in enemies_near(looks, h, me.pos, PORC_R) {
                    self.hit(sim, now, h, me.ent, looks[u].ent, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
                    put_timed(sim, looks[u].ent, &timed(E_PORC, PORC_SLOW_T, |b| b.move_speed_mult = -PORC_SLOW));
                }
                self.fire(Ev::Porcupine);
                self.say(screen, || format!("PROC porcupine {} bursts: {amount} physical", names[h]));
                self.show(screen, now, Show::RingRed, me.pos, vec![(PORC_R, 0)], 24);
            }
        }
        if has(Ev::TitansResolve) && (hit.is_some() || self.pls[h].taken > 0) && self.gate(h, Ev::TitansResolve, h, now, TITAN_GAP) {
            let t = &mut self.pls[h].b2.titan;
            t.retain(|&x| x > now);
            if t.len() >= TITAN_FULL {
                t.remove(0);
            }
            t.push(now + TITAN_T);
            if t.len() == TITAN_FULL {
                self.fire(Ev::TitansResolve);
            }
        }
        if has(Ev::TitansResolve) {
            self.pls[h].b2.titan.retain(|&x| x > now);
            let full = (self.pls[h].b2.titan.len() >= TITAN_FULL) as i64;
            let was = self.pls[h].b2.dyn_on.iter().any(|x| x.0 == D_TITAN && x.2 == 1 && x.1 == me.ent);
            self.dyn_set(sim, h, me.ent, D_TITAN, full, |_| {
                named(D_TITAN, |b| {
                    b.attack_mult = 15;
                    b.magic_power_mult = 15;
                    b.defence = 20;
                    b.magic_resistance = 20;
                    b.toughness = 10;
                })
            });
            if full == 1 && !was {
                self.show(screen, now, Show::Grow, me.pos, Vec::new(), 0);
            }
        }
        if has(Ev::CircleOfDeath) {
            self.pls[h].b2.circle += self.pls[h].healed * CIRCLE_PCT / 100;
            if self.pls[h].b2.circle > 0 && self.ready_at(h, Ev::CircleOfDeath, now) {
                if let Some((_, v)) = nearest(looks, h, CIRCLE_RANGE) {
                    self.arm(h, Ev::CircleOfDeath, now + CIRCLE_EVERY);
                    let amount = std::mem::take(&mut self.pls[h].b2.circle);
                    self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    self.fire(Ev::CircleOfDeath);
                    self.show(screen, now, Show::Chain, me.pos, vec![looks[v].pos], 0);
                } else {
                    self.pls[h].b2.circle = 0;
                }
            }
        }

        // ---------- 残血 ----------
        if has(Ev::Salvation) && me.crossed & LOW_50 != 0 && self.ready_at(h, Ev::Salvation, now) {
            self.arm(h, Ev::Salvation, now + SALV_CD);
            let amount = by_level(100, 500, level);
            for u in enemies_near(looks, h, me.pos, SALV_R) {
                self.hit(sim, now, h, me.ent, looks[u].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
            }
            let heal = by_level(150, 450, level);
            for a in allies_near(looks, h, me.pos, SALV_R) {
                sim.heal(me.ent, looks[a].ent, heal);
                self.show(screen, now, Show::Dawn, looks[a].pos, Vec::new(), 0);
            }
            self.fire(Ev::Salvation);
            self.say(screen, || format!("PROC salvation {}: below {SALV_PCT}% - {amount} magic, {heal} healing", names[h]));
            self.show(screen, now, Show::RingGold, me.pos, vec![(SALV_R, 0)], 36);
        }
        if has(Ev::SharkBait) && me.crossed & LOW_10 != 0 && self.ready_at(h, Ev::SharkBait, now) {
            self.arm(h, Ev::SharkBait, now + SHARK_CD);
            put_timed(sim, me.ent, &timed(E_SHARK, SHARK_T, |b| b.undying = true));
            self.later.push(Later::Shark { holder: h, hent: me.ent, at: now + SHARK_T, base: by_level(120, 350, level) });
            self.fire(Ev::SharkBait);
            self.say(screen, || format!("PROC shark_bait {}: below {SHARK_PCT}% - 3.5 s of shark bait", names[h]));
            self.show(screen, now, Show::Undying, me.pos, Vec::new(), 0);
        }
        if has(Ev::Hellbent) && self.pls[h].b2.hell_down.is_none() && self.ready_at(h, Ev::Hellbent, now) {
            self.pls[h].b2.hell.retain(|&t| t > now);
            if self.pls[h].b2.hell.len() >= HELL_MOST {
                if me.max > 0 && me.hp * 100 <= me.max * HELL_LOW_PCT {
                    // 挨了致命的一下（「不会死」把他留在了 1 点生命）：倒下 4 秒，无敌、不能动
                    self.arm(h, Ev::Hellbent, now + HELL_CD);
                    let s = &mut self.pls[h].b2;
                    s.hell.clear();
                    s.hell_down = Some(now + HELL_DOWN);
                    sim.entity_remove_buff(me.ent, E_HELL_GUARD);
                    put_timed(sim, me.ent, &timed(E_HELL_DOWN, HELL_DOWN, |b| {
                        b.damaged_reduce = 100;
                        b.undying = true;
                    }));
                    sim.apply_cc(me.ent, &CcV1::stun(HELL_DOWN as u64));
                    self.own_cc.push((me.ent, now + HELL_DOWN + EVERY));
                    self.fire(Ev::Hellbent);
                    self.later.push(Later::Revive { holder: h, hent: me.ent, at: now + HELL_DOWN });
                    self.holy(screen, h, me.ent, now, HELL_DOWN);
                    self.say(screen, || format!("PROC hellbent {}: lethal damage at full stacks - down for 4 s", names[h]));
                    self.show(screen, now, Show::Undying, me.pos, Vec::new(), 0);
                } else {
                    // 叠满了：一直挂着「不会死」（每一步续上），挨了致命的一下才倒下
                    put_timed(sim, me.ent, &timed(E_HELL_GUARD, EVERY * 3, |b| b.undying = true));
                }
            }
        }
        if has(Ev::Divine) && self.ready_at(h, Ev::Divine, now) {
            let low = allies_near(looks, h, me.pos, DIVINE_R).into_iter().any(|a| looks[a].crossed & LOW_35 != 0);
            if low {
                self.arm(h, Ev::Divine, now + DIVINE_CD);
                self.later.push(Later::Divine { holder: h, hent: me.ent, at: now + DIVINE_DELAY });
                self.say(screen, || format!("PROC divine_intervention {}: an ally below {DIVINE_PCT}% - invulnerable in 1 s",
                                            names[h]));
                self.show(screen, now, Show::RingGold, me.pos, vec![(DIVINE_R, 0)], DIVINE_DELAY);
            }
        }

        // ---------- 位移 ----------
        if let Some((from, to)) = dash {
            if has(Ev::ShadowRunner) {
                put_timed(sim, me.ent, &timed(E_SHADOW, SHADOW_T, |b| b.move_speed_mult = SHADOW_MS));
                self.fire(Ev::ShadowRunner);
                if self.gate(h, Ev::ShadowRunner, h, now, 60) {
                    self.show(screen, now, Show::RingCyan, to, vec![(14_000, 0)], 20);
                }
            }
            if has(Ev::SwiftSafe) && self.ready_at(h, Ev::SwiftSafe, now) {
                self.arm(h, Ev::SwiftSafe, now + SAFE_CD);
                let amount = safe_shield(level, ad, ap);
                sim.entity_add_shield(me.ent, amount, SAFE_T);
                self.guarded(screen, h, me.ent, now, SAFE_T);
                self.fire(Ev::SwiftSafe);
                self.show(screen, now, Show::Escape, to, Vec::new(), 0);
            }
            if has(Ev::OutlawsGrit) {
                let b = timed(E_GRIT, GRIT_T, |b| {
                    b.defence = GRIT_RES;
                    b.magic_resistance = GRIT_RES;
                });
                Self::stack_timed(sim, me.ent, &b, GRIT_MOST);
                self.fire(Ev::OutlawsGrit);
                if self.gate(h, Ev::OutlawsGrit, h, now, 60) {
                    self.show(screen, now, Show::Guard, to, Vec::new(), 0);
                }
            }
            if has(Ev::Earthwake) {
                let base = wake_damage(level, ad, ap);
                self.later.push(Later::Crack { holder: h, hent: me.ent, from, to, at: now + WAKE_DELAY, base });
                self.fire(Ev::Earthwake);
                self.show(screen, now, Show::Trail, from, vec![to], WAKE_DELAY);
            }
        }

        // ---------- 定时 ----------
        if has(Ev::BigBrain) && (self.pls[h].respawned || self.ready_at(h, Ev::BigBrain, now)) {
            self.arm(h, Ev::BigBrain, now + BRAIN_EVERY);
            let amount = (ap * BRAIN_PCT / 100).max(1);
            sim.entity_add_shield(me.ent, amount, BRAIN_EVERY);
            self.guarded(screen, h, me.ent, now, BRAIN_EVERY);
            self.fire(Ev::BigBrain);
            self.say(screen, || format!("PROC big_brain {}: a {amount} shield", names[h]));
            self.show(screen, now, Show::Ward, me.pos, Vec::new(), 0);
        }
        if has(Ev::Firefox) && self.ready_at(h, Ev::Firefox, now) {
            let mut near: Vec<(u64, usize)> = enemies_near(looks, h, me.pos, FOX_R)
                .into_iter()
                .filter(|&v| looks[v].targetable)
                .map(|v| (d2(me.pos, looks[v].pos), v))
                .collect();
            if !near.is_empty() {
                near.sort();
                self.arm(h, Ev::Firefox, now + FOX_CD);
                let base = fox_damage(level, ad, ap);
                for j in 0..FOX_N {
                    let v = near[j % near.len()].1;
                    let d = (near[j % near.len()].0 as f64).sqrt() as u64;
                    let t = ((d / MISSILE_SPEED) as usize).max(MISSILE_MIN_T) + j * MISSILE_GAP;
                    self.shots.push(Shot { kind: Kind::Fox, holder: h, hent: me.ent, team: me.team,
                                           target: Some((v, looks[v].ent)), at: looks[v].pos, land: now + t, base });
                    self.show(screen, now + j * MISSILE_GAP, Show::Missile, me.pos, vec![looks[v].pos], t - j * MISSILE_GAP);
                }
                put_timed(sim, me.ent, &timed(E_FOX, FOX_MS_T, |b| b.move_speed_mult = FOX_MS));
                self.fire(Ev::Firefox);
            }
        }
        if has(Ev::SlimeTime) && fighting && self.ready_at(h, Ev::SlimeTime, now) {
            let hit: Vec<usize> =
                enemies_near(looks, h, me.pos, SLIME_R).into_iter().filter(|&v| looks[v].targetable).collect();
            if !hit.is_empty() {
                self.arm(h, Ev::SlimeTime, now + SLIME_CD);
                for &v in &hit {
                    let amount = slime_damage(level, looks[v].max, ad, ap);
                    self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    // 黏液落在两人中间
                    let pos = ((me.pos.0 + looks[v].pos.0) / 2, (me.pos.1 + looks[v].pos.1) / 2);
                    self.pls[h].b2.blobs.push((pos, now + BLOB_T));
                }
                self.fire(Ev::SlimeTime);
                let n = hit.len();
                self.say(screen, || format!("PROC slime_time {}: {n} champions hit, {n} blobs", names[h]));
                self.show(screen, now, Show::RingGreen, me.pos, vec![(SLIME_R, 0)], 24);
            }
        }
        if has(Ev::Decimation) && fighting && self.ready_at(h, Ev::Decimation, now)
            && enemies_near(looks, h, me.pos, DECI_R).into_iter().any(|v| looks[v].targetable)
        {
            self.arm(h, Ev::Decimation, now + DECI_WINDUP + DECI_CD);
            let base = deci_damage(level, ad, ap);
            self.later.push(Later::Decimate { holder: h, hent: me.ent, at: now + DECI_WINDUP, base });
            self.show(screen, now, Show::RingPurple, me.pos, vec![(DECI_R, 0)], DECI_WINDUP);
        }
        if has(Ev::Boomerang) && self.ready_at(h, Ev::Boomerang, now) {
            if let Some((d, v)) = nearest(looks, h, BOOM_RANGE) {
                self.arm(h, Ev::Boomerang, now + BOOM_CD);
                let d = (d as f64).sqrt() as u64;
                let half = ((d / BOOM_SPEED) as usize).max(8);
                let (from, to) = (me.pos, looks[v].pos);
                let base = boom_damage(level, ad, ap);
                self.later.push(Later::Boomerang { holder: h, hent: me.ent, from, to, at: now + half, back: false, base });
                self.later.push(Later::Boomerang { holder: h, hent: me.ent, from, to, at: now + 2 * half, back: true, base });
                self.fire(Ev::Boomerang);
                self.show(screen, now, Show::Boomerang, from, vec![to], 2 * half);
            }
        }
        if has(Ev::Sonata) && self.ready_at(h, Ev::Sonata, now) {
            self.arm(h, Ev::Sonata, now + SONATA_CD);
            let speed = self.pls[h].b2.sonata_speed;
            self.pls[h].b2.sonata_speed = !speed;
            let allies = allies_near(looks, h, me.pos, SONATA_R);
            if speed {
                for &a in &allies {
                    put_timed(sim, looks[a].ent, &timed(E_SONATA, SONATA_MS_T, |b| b.move_speed_mult = SONATA_MS));
                }
                self.show(screen, now, Show::RingCyan, me.pos, vec![(SONATA_R, 0)], 30);
            } else {
                let heal = sonata_heal(level, ap);
                for &a in &allies {
                    sim.heal(me.ent, looks[a].ent, heal);
                }
                self.show(screen, now, Show::RingBlue, me.pos, vec![(SONATA_R, 0)], 30);
            }
            self.fire(Ev::Sonata);
        }
        if has(Ev::PromQueen) {
            let s = &self.pls[h].b2;
            if now >= s.prom_until && self.ready_at(h, Ev::PromQueen, now) && nearest(looks, h, PROM_R).is_some() {
                self.arm(h, Ev::PromQueen, now + PROM_CD);
                let s = &mut self.pls[h].b2;
                s.prom_until = now + PROM_T;
                s.prom_hit.clear();
                put_timed(sim, me.ent, &timed(E_PROM, PROM_T, |b| b.move_speed_mult = PROM_MS));
                self.fire(Ev::PromQueen);
                self.say(screen, || format!("PROC prom_queen {}: a 4 s sprint", names[h]));
                self.show(screen, now, Show::Excited, me.pos, Vec::new(), 0);
            }
            if now < self.pls[h].b2.prom_until {
                for u in enemies_near(looks, h, me.pos, PROM_TOUCH) {
                    if self.pls[h].b2.prom_hit.contains(&u) {
                        continue;
                    }
                    self.pls[h].b2.prom_hit.push(u);
                    let (dx, dy) = (me.pos.0 as i64 - looks[u].pos.0 as i64, me.pos.1 as i64 - looks[u].pos.1 as i64);
                    let charm = CcV1 { kind: CcKindV1::Charm.code(), tick: PROM_CHARM, dx, dy, ..CcV1::default() };
                    sim.apply_cc(looks[u].ent, &charm);
                    self.own_cc.push((looks[u].ent, now + PROM_CHARM as usize + EVERY));
                    self.show(screen, now, Show::LightPop, looks[u].pos, Vec::new(), 0);
                }
            }
        }
        if has(Ev::Grab) {
            if self.pls[h].b2.tethers.is_empty() && self.ready_at(h, Ev::Grab, now) {
                let near: Vec<(usize, usize)> = enemies_near(looks, h, me.pos, GRAB_R)
                    .into_iter()
                    .filter(|&u| looks[u].targetable)
                    .map(|u| (u, looks[u].ent))
                    .collect();
                if !near.is_empty() {
                    self.arm(h, Ev::Grab, now + GRAB_CD);
                    let s = &mut self.pls[h].b2;
                    s.tethers = near;
                    s.tether_until = now + GRAB_T;
                }
            }
            if now >= self.pls[h].b2.tether_until {
                self.pls[h].b2.tethers.clear();
            }
            let tethers = self.pls[h].b2.tethers.clone();
            for (u, uent) in tethers {
                if looks.get(u).is_some_and(|l| l.alive && l.ent == uent) {
                    self.show(screen, now, Show::Tether, me.pos, vec![looks[u].pos], EVERY);
                }
            }
        }
    }

    /// 到时间的：无敌、鲨鱼咬、印记引爆、大招转好、回旋刃、裂痕、眩晕。
    pub(super) fn b2_later(&mut self, sim: &mut StableSim<'_>, now: usize, who: &[Who], looks: &[L], names: &[String],
                           screen: bool) {
        let all = std::mem::take(&mut self.later);
        for x in all {
            if x.at() > now {
                self.later.push(x);
                continue;
            }
            let alive = |s: usize, e: usize| looks.get(s).is_some_and(|l| l.alive && l.ent == e);
            match x {
                Later::Divine { holder, hent, .. } => {
                    if !alive(holder, hent) {
                        continue;
                    }
                    for a in allies_near(looks, holder, looks[holder].pos, DIVINE_R) {
                        put_timed(sim, looks[a].ent, &timed(E_DIVINE, DIVINE_T, |b| b.damaged_reduce = 100));
                        self.holy(screen, a, looks[a].ent, now, DIVINE_T);
                        self.show(screen, now, Show::Ward, looks[a].pos, Vec::new(), 0);
                    }
                    self.fire(Ev::Divine);
                }
                Later::Shark { holder, hent, base, .. } => {
                    if !alive(holder, hent) {
                        continue;
                    }
                    let at = looks[holder].pos;
                    for u in enemies_near(looks, holder, at, SHARK_R) {
                        let amount = base + looks[u].max.saturating_sub(looks[u].hp) * SHARK_MISSING_PCT / 100;
                        self.hit(sim, now, holder, hent, looks[u].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                        self.show(screen, now, Show::Execute, looks[u].pos, Vec::new(), 0);
                    }
                    self.say(screen, || format!("PROC shark_bait {}: the shark bites", names[holder]));
                    self.show(screen, now, Show::RingBlue, at, vec![(SHARK_R, 0)], 24);
                }
                Later::Mark { holder, hent, v, vent, hp0, .. } => {
                    if !alive(holder, hent) || !alive(v, vent) {
                        continue;
                    }
                    let lost = hp0.saturating_sub(looks[v].hp);
                    let amount = lost * MARK_PCT / 100;
                    if amount > 0 {
                        self.hit(sim, now, holder, hent, vent, amount, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                    }
                    self.say(screen, || format!("PROC its_killing_time {} -> {}: {amount} true", names[holder], names[v]));
                    self.show(screen, now, Show::Execute, looks[v].pos, Vec::new(), 0);
                    self.show(screen, now, Show::RingPurple, looks[v].pos, vec![(18_000, 0)], 24);
                }
                Later::Revolution { holder, hent, .. } => {
                    if !alive(holder, hent) {
                        continue;
                    }
                    sim.entity_reduce_cooldown(hent, SkillSlotV1::Ult, RESET);
                    self.fire(Ev::UltRevolution);
                    self.say(screen, || format!("PROC ultimate_revolution {}: the ultimate is ready again", names[holder]));
                    self.show(screen, now, Show::RingGold, looks[holder].pos, vec![(22_000, 0)], 24);
                }
                Later::Boomerang { holder, hent, from, to, back, base, .. } => {
                    if !alive(holder, hent) {
                        continue;
                    }
                    let (a, b) = if back { (to, looks[holder].pos) } else { (from, to) };
                    let team = who[holder].team;
                    for u in looks {
                        if u.alive && u.team != team && seg_d2(u.pos, a, b) <= BOOM_WIDTH * BOOM_WIDTH {
                            self.hit(sim, now, holder, hent, u.ent, base, DamageTypeV1::Ad, AttackTypeV1::Skill);
                            self.show(screen, now, Show::Heavy, u.pos, Vec::new(), 0);
                        }
                    }
                }
                Later::Crack { holder, hent, from, to, base, .. } => {
                    if !alive(holder, hent) {
                        continue;
                    }
                    let team = who[holder].team;
                    for u in looks {
                        if u.alive && u.team != team && seg_d2(u.pos, from, to) <= WAKE_WIDTH * WAKE_WIDTH {
                            self.hit(sim, now, holder, hent, u.ent, base, DamageTypeV1::Ap, AttackTypeV1::Skill);
                            self.show(screen, now, Show::RingRed, u.pos, vec![(14_000, 0)], 20);
                        }
                    }
                }
                Later::Stun { v, vent, .. } => {
                    if alive(v, vent) {
                        sim.apply_cc(vent, &CcV1::stun(GRAB_STUN));
                    }
                }
                Later::Decimate { holder, hent, base, .. } => {
                    if !alive(holder, hent) {
                        continue;
                    }
                    let me = looks[holder];
                    let mut outer = 0;
                    for u in enemies_near(looks, holder, me.pos, DECI_R) {
                        let far = !within(looks[u].pos, me.pos, DECI_INNER);
                        let amount = if far { base } else { base / 2 };
                        self.hit(sim, now, holder, hent, looks[u].ent, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
                        if far {
                            outer += 1;
                            self.show(screen, now, Show::Heavy, looks[u].pos, Vec::new(), 0);
                        }
                    }
                    if outer > 0 {
                        // 每个回复 18% 已损失生命（一个接一个算）
                        let missing = me.max.saturating_sub(me.hp);
                        let mut left = missing;
                        for _ in 0..outer {
                            left = left * (100 - DECI_HEAL_PCT) / 100;
                        }
                        sim.heal(hent, hent, missing - left);
                        let r = &mut self.pls[holder].ready[Ev::Decimation as usize];
                        *r = r.saturating_sub(DECI_CD * DECI_CUT_PCT / 100 * outer).max(now + DECI_MIN_CD);
                    }
                    self.fire(Ev::Decimation);
                    self.say(screen, || format!("PROC endless_decimation {}: {outer} on the outer ring", names[holder]));
                    self.show(screen, now, Show::RingRed, me.pos, vec![(DECI_R, 0)], 20);
                }
                Later::Hive { holder, hent, pos, sting, .. } => {
                    if !alive(holder, hent) {
                        continue;
                    }
                    let team = who[holder].team;
                    let hit: Vec<usize> = (0..looks.len())
                        .filter(|&u| looks[u].alive && looks[u].team != team && within(looks[u].pos, pos, BEES_R))
                        .collect();
                    for &u in &hit {
                        let vent = looks[u].ent;
                        put_timed(sim, vent, &timed(E_BEES, BEES_SLOW_T, |b| b.move_speed_mult = -BEES_SLOW));
                        self.hit(sim, now, holder, hent, vent, sting, DamageTypeV1::Ap, AttackTypeV1::Dot);
                        self.show(screen, now, Show::Bees, looks[u].pos, Vec::new(), BEES_EVERY);
                        self.later.push(Later::Sting { holder, hent, v: u, vent, at: now + BEES_EVERY, left: BEES_STINGS - 1,
                                                       sting });
                    }
                    let n = hit.len();
                    self.say(screen, || format!("PROC bees {}: the hive lands on {n} champions", names[holder]));
                    self.show(screen, now, Show::RingGold, pos, vec![(BEES_R, 0)], 20);
                }
                Later::Sting { holder, hent, v, vent, left, sting, .. } => {
                    if !alive(holder, hent) || !alive(v, vent) {
                        continue;
                    }
                    self.hit(sim, now, holder, hent, vent, sting, DamageTypeV1::Ap, AttackTypeV1::Dot);
                    self.show(screen, now, Show::Bees, looks[v].pos, Vec::new(), BEES_EVERY);
                    if left > 1 {
                        self.later.push(Later::Sting { holder, hent, v, vent, at: now + BEES_EVERY, left: left - 1, sting });
                    }
                }
                Later::Revive { holder, hent, .. } => {
                    self.pls[holder].b2.hell_down = None;
                    if !alive(holder, hent) {
                        continue;
                    }
                    let me = looks[holder];
                    let level = self.pls[holder].level;
                    let want = me.max * hell_hp_pct(level) / 100;
                    if want > me.hp {
                        sim.heal(hent, hent, want - me.hp);
                    }
                    let (ad, ap) = ad_ap(sim, hent);
                    put_timed(sim, hent, &timed(E_HELL, HELL_BUFF_T, |b| {
                        if ad >= ap {
                            b.attack = hell_ad(level) as i32;
                        } else {
                            b.magic_power = hell_ap(level) as i32;
                        }
                        b.move_speed_mult = hell_ms(level) as i32;
                        b.vamp = hell_vamp(level) as i32;
                    }));
                    self.say(screen, || format!("PROC hellbent {}: back up at {}% max health", names[holder],
                                                hell_hp_pct(level)));
                    self.show(screen, now, Show::Dawn, me.pos, Vec::new(), 0);
                    self.show(screen, now, Show::RingGold, me.pos, vec![(26_000, 0)], 30);
                }
            }
        }
        self.blobs_tick(sim, now, who, looks, screen);
    }

    /// 史莱姆时间的黏液：敌人踩到就没了；放的人（活着）走过去吃掉回复；到时间也没了。还在的每一步画一次。
    fn blobs_tick(&mut self, sim: &mut StableSim<'_>, now: usize, who: &[Who], looks: &[L], screen: bool) {
        for h in 0..self.pls.len().min(looks.len()).min(who.len()) {
            if self.pls[h].b2.blobs.is_empty() {
                continue;
            }
            let blobs = std::mem::take(&mut self.pls[h].b2.blobs);
            let me = looks[h];
            let team = who[h].team;
            for (pos, until) in blobs {
                if now >= until {
                    continue;
                }
                if looks.iter().any(|u| u.alive && u.team != team && within(u.pos, pos, BLOB_R)) {
                    self.show(screen, now, Show::RingGreen, pos, vec![(BLOB_R, 0)], 12);
                    continue;
                }
                if me.alive && within(me.pos, pos, BLOB_R) {
                    sim.heal(me.ent, me.ent, blob_heal(self.pls[h].level, me.max));
                    self.show(screen, now, Show::RingBlue, me.pos, vec![(BLOB_R, 0)], 16);
                    continue;
                }
                self.show(screen, now, Show::Blob, pos, Vec::new(), EVERY);
                self.pls[h].b2.blobs.push((pos, until));
            }
        }
    }

    /// 叠层的 buff（跟着玩家：复活后补回、层数变了重挂）。
    pub(super) fn b2_keep(&mut self, sim: &mut StableSim<'_>, _now: usize, who: &[Who], held: &[EvSet], looks: &[L]) {
        for h in 0..who.len() {
            if held[h] == 0 || !looks[h].alive {
                continue;
            }
            let ent = looks[h].ent;
            let s = &self.pls[h].b2;
            let now_stacks = [s.slap_ad, s.slap_ap, s.soul, s.mosh, s.recur];
            if s.applied == Some((ent, now_stacks)) || (now_stacks == [0; 5] && s.applied.is_none()) {
                continue;
            }
            for n in [S_SLAP, S_SOUL, S_MOSH, S_RECUR] {
                sim.entity_remove_buff(ent, n);
            }
            let [ad, ap, soul, mosh, recur] = now_stacks;
            if ad + ap > 0 {
                sim.add_buff(ent, &named(S_SLAP, |b| {
                    b.attack = SLAP_AD * ad as i32;
                    b.magic_power = SLAP_AP * ap as i32;
                }));
            }
            if soul > 0 {
                sim.add_buff(ent, &named(S_SOUL, |b| b.hp = SOUL_HP * soul as i32));
            }
            if mosh > 0 {
                sim.add_buff(ent, &named(S_MOSH, |b| b.hp = MOSH_EACH * mosh as i32));
            }
            if recur > 0 {
                sim.add_buff(ent, &named(S_RECUR, |b| {
                    b.skill_cooldown_mult = RECUR_EACH * recur as i32;
                    b.ult_cooldown_mult = RECUR_EACH * recur as i32;
                }));
            }
            self.pls[h].b2.applied = Some((ent, now_stacks));
        }
    }

    /// 0.4.0 的这一种不再有了（0.5.0 潘朵拉的盒子换掉了）：随场上变的属性摘掉，叠层清零（[`Procs::b2_keep`] 跟着摘）。
    pub(super) fn b2_forget(&mut self, sim: &mut StableSim<'_>, seat: usize, ent: Option<usize>, ev: Ev) {
        let Some(p) = self.pls.get_mut(seat) else { return };
        let s = &mut p.b2;
        let names: &[&str] = match ev {
            Ev::LichBrain => &[D_LICH],
            Ev::Homeguard => &[D_HOME],
            Ev::LonelyWarrior => &[D_LONELY],
            Ev::KillSecured => &[D_KILLSEC],
            Ev::Steadfast => &[D_STEAD],
            Ev::StillHere => &[D_STILL],
            Ev::Eureka => &[D_EUREKA],
            Ev::TitansResolve => {
                s.titan.clear();
                &[D_TITAN]
            }
            Ev::InfRecursion => {
                s.recur = 0;
                &[]
            }
            Ev::SlapAround => {
                (s.slap_ad, s.slap_ap) = (0, 0);
                &[]
            }
            Ev::SoulEater => {
                s.soul = 0;
                &[]
            }
            Ev::MoshMonster => {
                s.mosh = 0;
                &[]
            }
            Ev::Porcupine => {
                s.porcupine = 0;
                &[]
            }
            Ev::Adapt => &[D_ADAPT],
            Ev::Escapade => &[D_ESCAPADE],
            Ev::HeavyCrown => {
                s.crown = 0;
                &[D_CROWN]
            }
            Ev::Hellbent => {
                s.hell.clear();
                &[E_HELL_GUARD]
            }
            _ => &[],
        };
        s.dyn_on.retain(|x| !names.contains(&x.0));
        if let Some(e) = ent {
            for n in names {
                sim.entity_remove_buff(e, n);
            }
        }
    }

    /// 别处摘掉了这个随场上变的属性（0.5.0）：下次照新的挂。
    pub(super) fn b2_drop_dyn(&mut self, seat: usize, name: &str) {
        if let Some(p) = self.pls.get_mut(seat) {
            p.b2.dyn_on.retain(|x| x.0 != name);
        }
    }

    /// 测试看的：左右开弓、噬魂者、狂舞怪兽、无限递归的层数，刺猬存了多少。
    #[cfg(test)]
    pub fn b2_stacks(&self, seat: usize) -> ([u16; 5], usize) {
        self.pls.get(seat).map_or(([0; 5], 0), |p| {
            let s = &p.b2;
            ([s.slap_ad, s.slap_ap, s.soul, s.mosh, s.recur], s.porcupine)
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_numbers_follow_the_cards() {
        assert_eq!((guilty_heal(1, 2000), guilty_heal(12, 2000)), (40 + 30, 300 + 30));
        assert_eq!(fox_damage(1, 100, 200), 25 + 10 + 30);
        assert_eq!(safe_shield(12, 100, 200), 280 + 50 + 50);
        assert_eq!(boom_damage(1, 100, 100), 30 + 40 + 30);
        assert_eq!((porcupine_store(1), porcupine_store(12)), (400, 3_000));
        assert_eq!(porcupine_damage(1, 100, 50), 75 + 60 + 30);
        assert_eq!(sonata_heal(12, 100), 200 + 20);
        assert_eq!(wake_damage(1, 100, 100), 90 + 80 + 40);
        // a point beside the middle of a segment, one past its end
        assert_eq!(seg_d2((50, 10), (0, 0), (100, 0)), 100);
        assert_eq!(seg_d2((110, 0), (0, 0), (100, 0)), 100);
        assert_eq!(seg_d2((5, 5), (0, 0), (0, 0)), 50);
        // 第二批
        assert_eq!((twin_n(0), twin_n(25), twin_n(34), twin_n(67), twin_n(100), twin_n(250)), (1, 1, 2, 3, 4, 4));
        assert_eq!(twin_damage(1, 100, 100), 10 + 7 + 7);
        assert_eq!(slime_damage(1, 2000, 100, 100), 40 + 2000 * (30 + 30) / 1000);
        assert_eq!((blob_heal(1, 2000), blob_heal(12, 2000)), (120, 300));
        assert_eq!(deci_damage(12, 100, 100), 400 + 60 + 40);
        assert_eq!((bees_cd(1), bees_cd(12)), (900, 600));
        assert_eq!(bees_sting(1, 100, 100), (75 + 150 + 70) / 4);
        assert_eq!((hell_hp_pct(1), hell_hp_pct(12), hell_ad(12), hell_ap(1)), (35, 75, 200, 50));
        assert_eq!(BUFFS.len(), 38);
        let mut names = BUFFS.to_vec();
        names.sort();
        names.dedup();
        assert_eq!(names.len(), BUFFS.len(), "every buff name once");
    }
}
