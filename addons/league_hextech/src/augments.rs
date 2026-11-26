//! 海克斯表。0.1.0 的 20 个都是属性类：拿到时给英雄挂一个永久 buff（`league_hextech_a:<key>`），数值照游戏自己的装备定
//! （游戏的四级装备：攻击 +100、法强 +200、攻速 +60%、暴击 25%、穿甲 20%、韧性 50%）——银档大约半件装备，金档一件，棱彩快两件。
//! 百分比的字段（`attack_mult` 之类）20 就是 +20%；`skill_cooldown_mult` / `ult_cooldown_mult` 像英雄联盟的技能急速：冷却 ×
//! 100 / (100 + 数)，15 是 -13%、25 是 -20%、100 是减半（格纳尔变身时用 270000 让大招立刻好）；`base_attack_enemy_max_hp_damage`
//! 3 是普攻附带目标最大生命 3%（克格莫的 W 用 5）。
//!
//! 0.3.0（第 3 步，用户 2026-11-26：「做第 3 步」「还有触发特效也要做吧」）加 27 个触发类（`ev` 不是 [`Ev::Stat`]）：打中英雄、
//! 放技能、普攻、参与击杀、残血、控住敌人、定时，效果在 [`super::procs`]，数值也在那里（这里的说明照着它写）。它们身上挂的
//! 海克斯 buff 只是个记号（没有属性；歌利亚巨人例外，它的属性照旧在 `stats` 里，体型由高清帧引擎按这个 buff 放大）。
//!
//! `fit` 是 AI 打分的权重（[`super::rules::fit`]）：和英雄的特性（[`Traits`]，[`super::kit`] 从游戏的分类、标签算出来）逐项乘起来
//! 再除以权重的绝对值之和；负数是不适合（坦克拿玻璃大炮）。

use mod_api_stable::BuffV1;

/// 档位：银、金、棱彩。
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Tier {
    Silver,
    Gold,
    Prismatic,
}

impl Tier {
    pub const ALL: [Tier; 3] = [Tier::Silver, Tier::Gold, Tier::Prismatic];

    pub fn code(self) -> u8 {
        self as u8
    }

    pub fn from_code(c: u8) -> Option<Tier> {
        Tier::ALL.get(c as usize).copied()
    }

    pub fn key(self) -> &'static str {
        match self {
            Tier::Silver => "silver",
            Tier::Gold => "gold",
            Tier::Prismatic => "prismatic",
        }
    }
}

/// 英雄的特性（0..=1，[`super::kit::traits`]），同一个结构也当海克斯的打分权重用（可以是负数）。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Traits {
    /// 物理伤害
    pub ad: f32,
    /// 法术伤害
    pub ap: f32,
    /// 靠普攻（射手、战士）
    pub attacker: f32,
    /// 靠技能（法师、辅助）
    pub caster: f32,
    pub tank: f32,
    /// 近战战士
    pub bruiser: f32,
    pub assassin: f32,
    pub support: f32,
    pub melee: f32,
    pub ranged: f32,
    /// 带控制（眩晕、击飞、定身……：「控住敌方英雄时」那几个看它，0.3.0）
    pub cc: f32,
}

impl Traits {
    pub const ZERO: Traits = Traits {
        ad: 0.0,
        ap: 0.0,
        attacker: 0.0,
        caster: 0.0,
        tank: 0.0,
        bruiser: 0.0,
        assassin: 0.0,
        support: 0.0,
        melee: 0.0,
        ranged: 0.0,
        cc: 0.0,
    };

    pub fn arr(&self) -> [f32; 11] {
        [self.ad, self.ap, self.attacker, self.caster, self.tank, self.bruiser, self.assassin, self.support, self.melee,
         self.ranged, self.cc]
    }

    /// 同样的权重，再看带不带控制。
    pub const fn with_cc(mut self, cc: f32) -> Traits {
        self.cc = cc;
        self
    }
}

/// 一类海克斯（拿过同一类的再拿，AI 稍微加分）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Theme {
    Ad,
    Ap,
    Crit,
    Speed,
    Tank,
    Haste,
    Hybrid,
    Sustain,
    /// 打中英雄时附带点什么
    OnHit,
    /// 护盾、免死
    Guard,
}

/// 海克斯在比赛里怎么起作用：`Stat` 只有 buff 上的属性，别的是 [`super::procs`] 里的一种触发效果（每种一个海克斯）。
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum Ev {
    Stat,
    // 银
    Firebrand,
    IceCold,
    LightEmUp,
    EscapePlan,
    TankEngine,
    MysticPunch,
    HeavyHitter,
    MagicMissile,
    // 金
    ChainLightning,
    Vulnerability,
    EtherealWeapon,
    Colossus,
    Executioner,
    Dawnbringer,
    GetExcited,
    Guardian,
    PhenomenalEvil,
    // 棱彩
    Goliath,
    OrbitalLaser,
    Cruelty,
    FinalForm,
    Snowball,
    Quantum,
    UndyingWill,
    Immolate,
    Typhoon,
    SacredWard,
}

/// 一共几种（[`Ev::Stat`] 也算一种）。
pub const EV_N: usize = Ev::SacredWard as usize + 1;

impl Ev {
    /// 一个人拿着的种类记成一个 u64 的位。
    pub const fn bit(self) -> u64 {
        1 << (self as u32)
    }
}

/// buff 里的一个字段。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Field {
    Attack,
    AttackMult,
    MagicPowerMult,
    Defence,
    DefenceMult,
    Hp,
    HpMult,
    MagicResistance,
    MagicResistanceMult,
    Vamp,
    MoveSpeedMult,
    AttackSpeedMult,
    SkillCooldownMult,
    UltCooldownMult,
    CritChance,
    DefencePenetration,
    MagicResistancePenetration,
    Toughness,
    SkillDamagedReduce,
    BaseAttackEnemyMaxHpDamage,
}

impl Field {
    /// 引擎里这个字段是无符号的（不能写负数）。
    pub fn unsigned(self) -> bool {
        matches!(self, Field::DefencePenetration | Field::MagicResistancePenetration | Field::Toughness
            | Field::SkillDamagedReduce | Field::BaseAttackEnemyMaxHpDamage)
    }
}

pub struct Aug {
    /// 名字（buff 名、日志、存档里用；只用小写英文和下划线）
    pub key: &'static str,
    pub tier: Tier,
    /// 简体、繁体、英文
    pub name: [&'static str; 3],
    pub desc: [&'static str; 3],
    pub stats: &'static [(Field, i32)],
    pub fit: Traits,
    pub theme: Theme,
    pub ev: Ev,
}

#[allow(clippy::too_many_arguments)]
const fn w(ad: f32, ap: f32, attacker: f32, caster: f32, tank: f32, bruiser: f32, assassin: f32, support: f32, melee: f32,
           ranged: f32) -> Traits {
    Traits { ad, ap, attacker, caster, tank, bruiser, assassin, support, melee, ranged, cc: 0.0 }
}

use Ev as E;
use Field::*;
use Theme as T;
use Tier::*;

/// 0.1.0 的 20 个（银 8、金 7、棱彩 5），0.3.0 的 27 个（银 8、金 9、棱彩 10）接在后面。顺序就是编号（日志、画面用；存档里存的
/// 是 key，不是编号，所以以后只往后加）。
pub const AUGS: [Aug; 47] = [
    // ---------------- 银 ----------------
    Aug { key: "blunt_force", tier: Silver, name: ["钝器", "鈍器", "Blunt Force"],
          desc: ["攻击力 +20%", "攻擊力 +20%", "+20% attack damage"],
          stats: &[(AttackMult, 20)],
          fit: w(1.0, 0.0, 0.4, 0.0, 0.0, 0.3, 0.3, 0.0, 0.0, 0.0), theme: T::Ad, ev: E::Stat },
    Aug { key: "witchful_thinking", tier: Silver, name: ["巫术思维", "巫術思維", "Witchful Thinking"],
          desc: ["法术强度 +20%", "法術強度 +20%", "+20% ability power"],
          stats: &[(MagicPowerMult, 20)],
          fit: w(0.0, 1.0, 0.0, 0.4, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), theme: T::Ap, ev: E::Stat },
    Aug { key: "deft", tier: Silver, name: ["灵巧", "靈巧", "Deft"],
          desc: ["攻击速度 +30%", "攻擊速度 +30%", "+30% attack speed"],
          stats: &[(AttackSpeedMult, 30)],
          fit: w(0.4, 0.0, 1.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.3), theme: T::Speed, ev: E::Stat },
    Aug { key: "hearty", tier: Silver, name: ["强健体魄", "強健體魄", "Hearty"],
          desc: ["最大生命 +350", "最大生命 +350", "+350 max health"],
          stats: &[(Hp, 350)],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.6, 0.0, 0.3, 0.2, 0.0), theme: T::Tank, ev: E::Stat },
    Aug { key: "ironclad", tier: Silver, name: ["铁甲", "鐵甲", "Ironclad"],
          desc: ["护甲 +40，魔抗 +40", "護甲 +40，魔抗 +40", "+40 armor, +40 magic resist"],
          stats: &[(Defence, 40), (MagicResistance, 40)],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0, 0.0, 0.3, 0.0), theme: T::Tank, ev: E::Stat },
    Aug { key: "mind_focus", tier: Silver, name: ["心灵专注", "心靈專注", "Mind Focus"],
          desc: ["技能和大招冷却 -13%", "技能和大招冷卻 -13%", "-13% skill and ultimate cooldowns"],
          stats: &[(SkillCooldownMult, 15), (UltCooldownMult, 15)],
          fit: w(0.0, 0.3, 0.0, 0.8, 0.0, 0.0, 0.3, 0.6, 0.0, 0.0), theme: T::Haste, ev: E::Stat },
    Aug { key: "swift_feet", tier: Silver, name: ["疾风步", "疾風步", "Swift Feet"],
          desc: ["移动速度 +10%，韧性 +15%", "移動速度 +10%，韌性 +15%", "+10% move speed, +15% tenacity"],
          stats: &[(MoveSpeedMult, 10), (Toughness, 15)],
          fit: w(0.0, 0.0, 0.0, 0.0, 0.3, 0.4, 0.4, 0.3, 0.5, 0.0), theme: T::Speed, ev: E::Stat },
    Aug { key: "bloodthirst", tier: Silver, name: ["嗜血", "嗜血", "Bloodthirst"],
          desc: ["生命偷取 +10%", "生命偷取 +10%", "+10% life steal"],
          stats: &[(Vamp, 10)],
          fit: w(0.7, 0.0, 0.5, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0), theme: T::Sustain, ev: E::Stat },
    // ---------------- 金 ----------------
    Aug { key: "celestial_body", tier: Gold, name: ["天体", "天體", "Celestial Body"],
          desc: ["最大生命 +900，攻击力和法强 -10%", "最大生命 +900，攻擊力和法強 -10%",
                 "+900 max health, -10% attack damage and ability power"],
          stats: &[(Hp, 900), (AttackMult, -10), (MagicPowerMult, -10)],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.3, -0.6, 0.5, 0.0, 0.0), theme: T::Tank, ev: E::Stat },
    Aug { key: "glass_cannon", tier: Gold, name: ["玻璃大炮", "玻璃大砲", "Glass Cannon"],
          desc: ["最大生命 -20%，攻击力和法强 +30%", "最大生命 -20%，攻擊力和法強 +30%",
                 "-20% max health, +30% attack damage and ability power"],
          stats: &[(HpMult, -20), (AttackMult, 30), (MagicPowerMult, 30)],
          fit: w(0.4, 0.4, 0.0, 0.3, -1.0, 0.0, 0.8, -0.4, 0.0, 0.4), theme: T::Hybrid, ev: E::Stat },
    Aug { key: "lethal_precision", tier: Gold, name: ["致命精准", "致命精準", "Lethal Precision"],
          desc: ["暴击率 +25%，攻击力 +10%", "暴擊率 +25%，攻擊力 +10%", "+25% crit chance, +10% attack damage"],
          stats: &[(CritChance, 25), (AttackMult, 10)],
          fit: w(0.8, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3), theme: T::Crit, ev: E::Stat },
    Aug { key: "thread_the_needle", tier: Gold, name: ["穿针引线", "穿針引線", "Thread the Needle"],
          desc: ["护甲穿透和魔抗穿透 +25%", "護甲穿透和魔抗穿透 +25%", "+25% armor and magic penetration"],
          stats: &[(DefencePenetration, 25), (MagicResistancePenetration, 25)],
          fit: w(0.5, 0.5, 0.3, 0.3, 0.0, 0.0, 0.6, 0.0, 0.0, 0.0), theme: T::Hybrid, ev: E::Stat },
    Aug { key: "unwavering", tier: Gold, name: ["坚定不移", "堅定不移", "Unwavering"],
          desc: ["韧性 +40%，受到的技能伤害 -15%", "韌性 +40%，受到的技能傷害 -15%",
                 "+40% tenacity, -15% damage taken from skills"],
          stats: &[(Toughness, 40), (SkillDamagedReduce, 15)],
          fit: w(0.0, 0.0, 0.0, 0.0, 0.8, 0.8, 0.0, 0.0, 0.4, 0.0), theme: T::Tank, ev: E::Stat },
    Aug { key: "giant_slayer", tier: Gold, name: ["巨人杀手", "巨人殺手", "Giant Slayer"],
          desc: ["普攻附带目标最大生命 3% 的伤害，攻击速度 +15%", "普攻附帶目標最大生命 3% 的傷害，攻擊速度 +15%",
                 "Basic attacks deal 3% of the target's max health, +15% attack speed"],
          stats: &[(BaseAttackEnemyMaxHpDamage, 3), (AttackSpeedMult, 15)],
          fit: w(0.0, 0.0, 1.0, 0.0, 0.0, 0.3, 0.0, 0.0, 0.0, 0.3), theme: T::Speed, ev: E::Stat },
    Aug { key: "arcane_surge", tier: Gold, name: ["奥术洪流", "奧術洪流", "Arcane Surge"],
          desc: ["法术强度 +30%，技能冷却 -13%", "法術強度 +30%，技能冷卻 -13%", "+30% ability power, -13% skill cooldowns"],
          stats: &[(MagicPowerMult, 30), (SkillCooldownMult, 15)],
          fit: w(0.0, 1.0, 0.0, 0.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), theme: T::Ap, ev: E::Stat },
    // ---------------- 棱彩 ----------------
    Aug { key: "slayer", tier: Prismatic, name: ["屠戮者", "屠戮者", "Slayer"],
          desc: ["攻击力 +40%，暴击率 +30%", "攻擊力 +40%，暴擊率 +30%", "+40% attack damage, +30% crit chance"],
          stats: &[(AttackMult, 40), (CritChance, 30)],
          fit: w(1.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0), theme: T::Crit, ev: E::Stat },
    Aug { key: "archmage", tier: Prismatic, name: ["大法师", "大法師", "Archmage"],
          desc: ["法术强度 +60%，技能和大招冷却 -20%", "法術強度 +60%，技能和大招冷卻 -20%",
                 "+60% ability power, -20% skill and ultimate cooldowns"],
          stats: &[(MagicPowerMult, 60), (SkillCooldownMult, 25), (UltCooldownMult, 25)],
          fit: w(0.0, 1.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), theme: T::Ap, ev: E::Stat },
    Aug { key: "immortal_colossus", tier: Prismatic, name: ["不朽巨像", "不朽巨像", "Immortal Colossus"],
          desc: ["最大生命 +35%，护甲和魔抗 +35%，韧性 +30%", "最大生命 +35%，護甲和魔抗 +35%，韌性 +30%",
                 "+35% max health, +35% armor and magic resist, +30% tenacity"],
          stats: &[(HpMult, 35), (DefenceMult, 35), (MagicResistanceMult, 35), (Toughness, 30)],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.8, 0.0, 0.2, 0.0, 0.0), theme: T::Tank, ev: E::Stat },
    Aug { key: "storm_fury", tier: Prismatic, name: ["风暴之怒", "風暴之怒", "Storm Fury"],
          desc: ["攻击速度 +70%，移动速度 +15%", "攻擊速度 +70%，移動速度 +15%", "+70% attack speed, +15% move speed"],
          stats: &[(AttackSpeedMult, 70), (MoveSpeedMult, 15)],
          fit: w(0.4, 0.0, 1.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.2), theme: T::Speed, ev: E::Stat },
    Aug { key: "ultimate_awakening", tier: Prismatic, name: ["终极觉醒", "終極覺醒", "Ultimate Awakening"],
          desc: ["大招冷却减半，攻击力和法强 +15%", "大招冷卻減半，攻擊力和法強 +15%",
                 "Ultimate cooldown halved, +15% attack damage and ability power"],
          stats: &[(UltCooldownMult, 100), (AttackMult, 15), (MagicPowerMult, 15)],
          fit: w(0.0, 0.0, 0.0, 0.5, 0.4, 0.3, 0.4, 0.5, 0.0, 0.0), theme: T::Haste, ev: E::Stat },
    // ================ 0.3.0：触发类 ================
    // ---------------- 银 ----------------
    Aug { key: "firebrand", tier: Silver, name: ["烈焰烙印", "烈焰烙印", "Firebrand"],
          desc: ["命中英雄时点燃 3 秒：共 30 + 目标最大生命 3% + 10% 攻击力 + 10% 法强 的魔法伤害",
                 "命中英雄時點燃 3 秒：共 30 + 目標最大生命 3% + 10% 攻擊力 + 10% 法強 的魔法傷害",
                 "Hits burn champions for 3 s: 30 + 3% of their max HP + 10% AD + 10% AP magic damage in all"],
          stats: &[],
          fit: w(0.4, 0.5, 0.4, 0.5, 0.0, 0.3, 0.2, 0.0, 0.0, 0.0), theme: T::OnHit, ev: E::Firebrand },
    Aug { key: "ice_cold", tier: Silver, name: ["彻骨冰寒", "徹骨冰寒", "Ice Cold"],
          desc: ["命中英雄时使其减速 20%，持续 1.5 秒", "命中英雄時使其減速 20%，持續 1.5 秒",
                 "Hits slow champions by 20% for 1.5 s"],
          stats: &[],
          fit: w(0.0, 0.2, 0.6, 0.3, 0.3, 0.4, 0.0, 0.5, 0.0, 0.3), theme: T::OnHit, ev: E::IceCold },
    Aug { key: "light_em_up", tier: Silver, name: ["点亮他们！", "點亮他們！", "Light 'em Up!"],
          desc: ["每第 4 次命中英雄，额外造成 25 + 40% 攻击力 的物理伤害", "每第 4 次命中英雄，額外造成 25 + 40% 攻擊力 的物理傷害",
                 "Every 4th hit on a champion deals 25 + 40% AD bonus physical damage"],
          stats: &[],
          fit: w(0.8, 0.0, 1.0, 0.0, 0.0, 0.2, 0.2, 0.0, 0.0, 0.3), theme: T::OnHit, ev: E::LightEmUp },
    Aug { key: "escape_plan", tier: Silver, name: ["逃跑计划", "逃跑計畫", "Escape Plan"],
          desc: ["生命低于 35% 时：100 + 12% 最大生命的护盾（3 秒），移动速度 +40%（2 秒）。冷却 45 秒",
                 "生命低於 35% 時：100 + 12% 最大生命的護盾（3 秒），移動速度 +40%（2 秒）。冷卻 45 秒",
                 "Below 35% HP: a 100 + 12% max HP shield (3 s), +40% move speed (2 s). 45 s cooldown"],
          stats: &[],
          fit: w(0.0, 0.0, 0.3, 0.4, -0.5, 0.0, 0.4, 0.3, 0.0, 0.4), theme: T::Guard, ev: E::EscapePlan },
    Aug { key: "tank_engine", tier: Silver, name: ["坦克引擎", "坦克引擎", "Tank Engine"],
          desc: ["每次参与击杀：最大生命 +30，护甲和魔抗 +3（最多 12 层；6 层、12 层时体型变大）",
                 "每次參與擊殺：最大生命 +30，護甲和魔抗 +3（最多 12 層；6 層、12 層時體型變大）",
                 "Each takedown: +30 max HP, +3 armor and magic resist (up to 12; bigger at 6 and 12)"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0, 0.3, 0.3, 0.0), theme: T::Tank, ev: E::TankEngine },
    Aug { key: "mystic_punch", tier: Silver, name: ["秘术冲拳", "秘術衝拳", "Mystic Punch"],
          desc: ["每次普攻，两个技能的冷却各缩短 0.4 秒", "每次普攻，兩個技能的冷卻各縮短 0.4 秒",
                 "Each basic attack takes 0.4 s off both skills' cooldowns"],
          stats: &[],
          fit: w(0.3, 0.0, 1.0, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0, 0.0), theme: T::Haste, ev: E::MysticPunch },
    Aug { key: "heavy_hitter", tier: Silver, name: ["重击手", "重擊手", "Heavy Hitter"],
          desc: ["命中英雄时额外造成自身最大生命 3% 的物理伤害（每个目标 0.5 秒一次）",
                 "命中英雄時額外造成自身最大生命 3% 的物理傷害（每個目標 0.5 秒一次）",
                 "Hits on champions deal 3% of your max HP as bonus physical damage (0.5 s per target)"],
          stats: &[],
          fit: w(0.3, 0.0, 0.4, 0.0, 0.8, 0.8, 0.0, 0.0, 0.5, 0.0), theme: T::OnHit, ev: E::HeavyHitter },
    Aug { key: "magic_missile", tier: Silver, name: ["魔法飞弹", "魔法飛彈", "Magic Missile"],
          desc: ["放技能时向最近的敌方英雄射出飞弹：30 + 25% 法强 + 10% 攻击力 的魔法伤害（2 秒一次）",
                 "放技能時向最近的敵方英雄射出飛彈：30 + 25% 法強 + 10% 攻擊力 的魔法傷害（2 秒一次）",
                 "Casting a skill fires a missile at the nearest enemy champion: 30 + 25% AP + 10% AD magic (every 2 s)"],
          stats: &[],
          fit: w(0.0, 0.8, 0.0, 1.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.0), theme: T::Ap, ev: E::MagicMissile },
    // ---------------- 金 ----------------
    Aug { key: "chain_lightning", tier: Gold, name: ["连锁闪电", "連鎖閃電", "Chain Lightning"],
          desc: ["每 3 秒，下一次命中放出闪电打至多 3 个敌方英雄：40 + 25% 攻击力 + 30% 法强 的魔法伤害并减速",
                 "每 3 秒，下一次命中放出閃電打至多 3 個敵方英雄：40 + 25% 攻擊力 + 30% 法強 的魔法傷害並減速",
                 "Every 3 s your next hit chains lightning to up to 3 enemy champions: 40 + 25% AD + 30% AP magic and a slow"],
          stats: &[],
          fit: w(0.3, 0.6, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.3), theme: T::OnHit, ev: E::ChainLightning },
    Aug { key: "vulnerability", tier: Gold, name: ["弱点暴露", "弱點暴露", "Vulnerability"],
          desc: ["命中的英雄 3 秒内受到的伤害 +10%", "命中的英雄 3 秒內受到的傷害 +10%",
                 "Champions you hit take 10% more damage for 3 s"],
          stats: &[],
          fit: w(0.3, 0.3, 0.3, 0.3, 0.2, 0.3, 0.3, 0.6, 0.0, 0.0), theme: T::OnHit, ev: E::Vulnerability },
    Aug { key: "ethereal_weapon", tier: Gold, name: ["以太武器", "以太武器", "Ethereal Weapon"],
          desc: ["放技能后 3 秒内的下一次命中，额外造成 40 + 35% 法强 + 25% 攻击力 的魔法伤害",
                 "放技能後 3 秒內的下一次命中，額外造成 40 + 35% 法強 + 25% 攻擊力 的魔法傷害",
                 "After a cast, your next hit within 3 s deals 40 + 35% AP + 25% AD bonus magic damage"],
          stats: &[],
          fit: w(0.3, 0.7, 0.0, 0.8, 0.0, 0.4, 0.4, 0.0, 0.0, 0.0), theme: T::Ap, ev: E::EtherealWeapon },
    Aug { key: "courage_of_the_colossus", tier: Gold, name: ["巨像的勇气", "巨像的勇氣", "Courage of the Colossus"],
          desc: ["控住敌方英雄时，获得 80 + 10% 最大生命的护盾（2.5 秒）。冷却 5 秒",
                 "控住敵方英雄時，獲得 80 + 10% 最大生命的護盾（2.5 秒）。冷卻 5 秒",
                 "Immobilizing an enemy champion shields you for 80 + 10% max HP (2.5 s). 5 s cooldown"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.3, 0.8, 0.5, 0.0, 0.5, 0.3, 0.0).with_cc(1.0), theme: T::Guard, ev: E::Colossus },
    Aug { key: "executioner", tier: Gold, name: ["处刑人", "處刑人", "Executioner"],
          desc: ["命中生命低于 30% 的英雄时，额外造成其最大生命 5% 的真实伤害",
                 "命中生命低於 30% 的英雄時，額外造成其最大生命 5% 的真實傷害",
                 "Hits on champions below 30% HP deal 5% of their max HP as bonus true damage"],
          stats: &[],
          fit: w(0.6, 0.3, 0.6, 0.0, 0.0, 0.3, 1.0, 0.0, 0.0, 0.0), theme: T::Ad, ev: E::Executioner },
    Aug { key: "dawnbringers_resolve", tier: Gold, name: ["黎明使者的决心", "黎明使者的決心", "Dawnbringer's Resolve"],
          desc: ["生命低于 40% 时，2 秒内回复 30% 已损失生命。冷却 50 秒", "生命低於 40% 時，2 秒內回復 30% 已損失生命。冷卻 50 秒",
                 "Below 40% HP: heal 30% of your missing HP over 2 s. 50 s cooldown"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.0, 0.7, 1.0, 0.0, 0.2, 0.5, 0.0), theme: T::Sustain, ev: E::Dawnbringer },
    Aug { key: "get_excited", tier: Gold, name: ["兴奋起来！", "興奮起來！", "Get Excited!"],
          desc: ["参与击杀后 5 秒：攻击速度 +50%，移动速度 +25%", "參與擊殺後 5 秒：攻擊速度 +50%，移動速度 +25%",
                 "A takedown gives +50% attack speed and +25% move speed for 5 s"],
          stats: &[],
          fit: w(0.5, 0.0, 0.8, 0.0, 0.0, 0.4, 0.8, 0.0, 0.0, 0.0), theme: T::Speed, ev: E::GetExcited },
    Aug { key: "guardian", tier: Gold, name: ["守护者", "守護者", "Guardian"],
          desc: ["身边的队友生命低于 40% 时，你和他各获得 80 + 8% 你最大生命的护盾（2.5 秒）。冷却 12 秒",
                 "身邊的隊友生命低於 40% 時，你和他各獲得 80 + 8% 你最大生命的護盾（2.5 秒）。冷卻 12 秒",
                 "A nearby ally dropping below 40% HP shields you both for 80 + 8% of your max HP (2.5 s). 12 s cooldown"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.3, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0), theme: T::Guard, ev: E::Guardian },
    Aug { key: "phenomenal_evil", tier: Gold, name: ["惊世邪恶", "驚世邪惡", "Phenomenal Evil"],
          desc: ["命中英雄时永久获得 2 法强（每秒最多一次，最多 +150）", "命中英雄時永久獲得 2 法強（每秒最多一次，最多 +150）",
                 "Hits on champions give 2 ability power for good (once a second, up to +150)"],
          stats: &[],
          fit: w(0.0, 1.0, 0.0, 0.8, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0), theme: T::Ap, ev: E::PhenomenalEvil },
    // ---------------- 棱彩 ----------------
    Aug { key: "goliath", tier: Prismatic, name: ["歌利亚巨人", "歌利亞巨人", "Goliath"],
          desc: ["体型变大 15%，最大生命 +30%，攻击力和法强 +15%", "體型變大 15%，最大生命 +30%，攻擊力和法強 +15%",
                 "15% bigger, +30% max HP, +15% attack damage and ability power"],
          stats: &[(HpMult, 30), (AttackMult, 15), (MagicPowerMult, 15)],
          fit: w(0.2, 0.2, 0.0, 0.0, 1.0, 0.8, 0.0, 0.2, 0.4, 0.0), theme: T::Tank, ev: E::Goliath },
    Aug { key: "orbital_laser", tier: Prismatic, name: ["轨道激光", "軌道雷射", "Orbital Laser"],
          desc: ["每 10 秒锁定附近一个敌方英雄，0.75 秒后激光轰击那里：100 + 40% 法强 + 30% 攻击力 + 6% 最大生命 的魔法伤害",
                 "每 10 秒鎖定附近一個敵方英雄，0.75 秒後雷射轟擊那裡：100 + 40% 法強 + 30% 攻擊力 + 6% 最大生命 的魔法傷害",
                 "Every 10 s a laser marks a nearby enemy champion and strikes 0.75 s later: 100 + 40% AP + 30% AD + 6% max HP magic"],
          stats: &[],
          fit: w(0.2, 0.6, 0.2, 0.6, 0.0, 0.0, 0.0, 0.3, 0.0, 0.4), theme: T::Ap, ev: E::OrbitalLaser },
    Aug { key: "cruelty", tier: Prismatic, name: ["残忍", "殘忍", "Cruelty"],
          desc: ["控住敌方英雄时，彗星砸向他：80 + 35% 法强 + 25% 攻击力 + 4% 最大生命 的魔法伤害。冷却 4 秒",
                 "控住敵方英雄時，彗星砸向他：80 + 35% 法強 + 25% 攻擊力 + 4% 最大生命 的魔法傷害。冷卻 4 秒",
                 "Immobilizing an enemy champion drops a comet on them: 80 + 35% AP + 25% AD + 4% max HP magic. 4 s cooldown"],
          stats: &[],
          fit: w(0.2, 0.5, 0.0, 0.5, 0.3, 0.2, 0.0, 0.4, 0.0, 0.0).with_cc(1.0), theme: T::Ap, ev: E::Cruelty },
    Aug { key: "final_form", tier: Prismatic, name: ["最终形态", "最終形態", "Final Form"],
          desc: ["放大招后 5 秒：攻击速度 +30%，移动速度 +20%，受到的伤害 -20%，韧性 +80%，体型变大",
                 "放大招後 5 秒：攻擊速度 +30%，移動速度 +20%，受到的傷害 -20%，韌性 +80%，體型變大",
                 "After your ultimate, 5 s of +30% attack speed, +20% move speed, -20% damage taken, +80% tenacity, bigger"],
          stats: &[],
          fit: w(0.4, 0.3, 0.3, 0.3, 0.2, 0.8, 0.8, 0.0, 0.5, 0.0), theme: T::Speed, ev: E::FinalForm },
    Aug { key: "giant_snowball", tier: Prismatic, name: ["超级雪球", "超級雪球", "Giant Snowball"],
          desc: ["每 12 秒向一个敌方英雄扔大雪球：落点附近的敌方英雄被击飞 0.75 秒，受到 60 + 30% 攻击力 + 20% 法强 + 4% 最大生命 的物理伤害",
                 "每 12 秒向一個敵方英雄扔大雪球：落點附近的敵方英雄被擊飛 0.75 秒，受到 60 + 30% 攻擊力 + 20% 法強 + 4% 最大生命 的物理傷害",
                 "Every 12 s hurl a snowball at an enemy champion: those it lands near are knocked up 0.75 s and take 60 + 30% AD + 20% AP + 4% max HP physical"],
          stats: &[],
          fit: w(0.3, 0.3, 0.3, 0.3, 0.4, 0.5, 0.3, 0.4, 0.0, 0.0), theme: T::Hybrid, ev: E::Snowball },
    Aug { key: "quantum_computing", tier: Prismatic, name: ["量子计算", "量子計算", "Quantum Computing"],
          desc: ["每 8 秒挥出一圈斩击：40 + 45% 攻击力 + 目标最大生命 6% 的物理伤害，每打中一个英雄回复 4% 最大生命",
                 "每 8 秒揮出一圈斬擊：40 + 45% 攻擊力 + 目標最大生命 6% 的物理傷害，每打中一個英雄回復 4% 最大生命",
                 "Every 8 s a ring slash: 40 + 45% AD + 6% of their max HP physical, healing 4% max HP per champion hit"],
          stats: &[],
          fit: w(0.6, 0.0, 0.3, 0.0, 0.4, 1.0, 0.3, 0.0, 0.8, 0.0), theme: T::Sustain, ev: E::Quantum },
    Aug { key: "undying_will", tier: Prismatic, name: ["不灭意志", "不滅意志", "Undying Will"],
          desc: ["生命低于 15% 时，2 秒内不会死亡，并回复 20% 最大生命。冷却 90 秒",
                 "生命低於 15% 時，2 秒內不會死亡，並回復 20% 最大生命。冷卻 90 秒",
                 "Below 15% HP you cannot die for 2 s and heal 20% max HP. 90 s cooldown"],
          stats: &[],
          fit: w(0.0, 0.0, 0.2, 0.0, 0.5, 0.9, 0.4, 0.0, 0.4, 0.0), theme: T::Guard, ev: E::UndyingWill },
    Aug { key: "immolate", tier: Prismatic, name: ["献祭光环", "獻祭光環", "Immolate"],
          desc: ["每秒灼烧身边的敌方英雄：15 + 1.5% 你的最大生命 的魔法伤害", "每秒灼燒身邊的敵方英雄：15 + 1.5% 你的最大生命 的魔法傷害",
                 "Every second, burn enemy champions around you for 15 + 1.5% of your max HP magic damage"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.6, 0.0, 0.2, 0.6, 0.0), theme: T::Tank, ev: E::Immolate },
    Aug { key: "typhoon", tier: Prismatic, name: ["台风", "颱風", "Typhoon"],
          desc: ["命中英雄时，向身边另外 2 个敌方英雄射出风刃：25% 攻击力 + 10% 法强 的物理伤害（约 0.7 秒一次）",
                 "命中英雄時，向身邊另外 2 個敵方英雄射出風刃：25% 攻擊力 + 10% 法強 的物理傷害（約 0.7 秒一次）",
                 "Hits also fire wind blades at 2 other nearby enemy champions: 25% AD + 10% AP physical (about every 0.7 s)"],
          stats: &[],
          fit: w(0.6, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.6), theme: T::OnHit, ev: E::Typhoon },
    Aug { key: "sacred_ward", tier: Prismatic, name: ["圣光庇佑", "聖光庇佑", "Sacred Ward"],
          desc: ["每 8 秒给身边生命比例最低的友方英雄（含自己）100 + 25% 法强 + 8% 其最大生命 的护盾（3 秒）和 20% 移动速度",
                 "每 8 秒給身邊生命比例最低的友方英雄（含自己）100 + 25% 法強 + 8% 其最大生命 的護盾（3 秒）和 20% 移動速度",
                 "Every 8 s the nearby ally with the lowest HP (you too) gets a 100 + 25% AP + 8% max HP shield (3 s) and +20% speed"],
          stats: &[],
          fit: w(0.0, 0.4, 0.0, 0.5, 0.2, 0.0, 0.0, 1.0, 0.0, 0.0), theme: T::Guard, ev: E::SacredWard },
];

/// 海克斯 buff 名的前缀，后面接 key。
pub const BUFF_PREFIX: &str = "league_hextech_a:";

pub fn buff_name(i: usize) -> String {
    format!("{BUFF_PREFIX}{}", AUGS[i].key)
}

/// 这个 buff 名是哪个海克斯的（不是本包的：None）。
pub fn of_buff(name: &str) -> Option<usize> {
    let key = name.strip_prefix(BUFF_PREFIX)?;
    AUGS.iter().position(|a| a.key == key)
}

pub fn by_key(key: &str) -> Option<usize> {
    AUGS.iter().position(|a| a.key == key)
}

/// 这一档有哪些（编号）。
pub fn pool(tier: Tier) -> Vec<usize> {
    (0..AUGS.len()).filter(|&i| AUGS[i].tier == tier).collect()
}

/// 这种触发效果是哪个海克斯（`Stat`：None）。
pub fn of_ev(ev: Ev) -> Option<usize> {
    (ev != Ev::Stat).then(|| AUGS.iter().position(|a| a.ev == ev)).flatten()
}

/// 拿到这个海克斯时挂的永久 buff（触发类的没有属性：只是个记号，复活后补、状态丢了从它读回来）。
pub fn buff(i: usize) -> BuffV1 {
    let mut b = BuffV1::named(&buff_name(i));
    for &(f, v) in AUGS[i].stats {
        set(&mut b, f, v);
    }
    b
}

fn set(b: &mut BuffV1, f: Field, v: i32) {
    let u = v.max(0) as usize;
    match f {
        Attack => b.attack += v,
        AttackMult => b.attack_mult += v,
        MagicPowerMult => b.magic_power_mult += v,
        Defence => b.defence += v,
        DefenceMult => b.defence_mult += v,
        Hp => b.hp += v,
        HpMult => b.hp_mult += v,
        MagicResistance => b.magic_resistance += v,
        MagicResistanceMult => b.magic_resistance_mult += v,
        Vamp => b.vamp += v,
        MoveSpeedMult => b.move_speed_mult += v,
        AttackSpeedMult => b.attack_speed_mult += v,
        SkillCooldownMult => b.skill_cooldown_mult += v,
        UltCooldownMult => b.ult_cooldown_mult += v,
        CritChance => b.crit_chance += v,
        DefencePenetration => b.defence_penetration += u,
        MagicResistancePenetration => b.magic_resistance_penetration += u,
        Toughness => b.toughness += u,
        SkillDamagedReduce => b.skill_damaged_reduce += u,
        BaseAttackEnemyMaxHpDamage => b.base_attack_enemy_max_hp_damage += u,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_augment_is_well_formed() {
        let mut keys: Vec<&str> = AUGS.iter().map(|a| a.key).collect();
        keys.sort();
        keys.dedup();
        assert_eq!(keys.len(), AUGS.len(), "two augments share a key");
        for (i, a) in AUGS.iter().enumerate() {
            assert!(a.key.bytes().all(|c| c.is_ascii_lowercase() || c == b'_'), "{}", a.key);
            assert!(buff_name(i).len() <= mod_api_stable::BUFF_NAME_CAP, "{}", a.key);
            assert_eq!(of_buff(&buff_name(i)), Some(i));
            assert_eq!(by_key(a.key), Some(i));
            for s in a.name.iter().chain(a.desc.iter()) {
                assert!(!s.trim().is_empty(), "{}", a.key);
            }
            // a stat augment changes stats; a triggered one may carry some too (Goliath)
            assert!(!a.stats.is_empty() || a.ev != Ev::Stat, "{}", a.key);
            for &(f, v) in a.stats {
                assert!(v != 0, "{} {f:?}", a.key);
                assert!(!f.unsigned() || v > 0, "{} {f:?} is unsigned in the engine", a.key);
            }
            let b = buff(i);
            assert_eq!(b.name(), buff_name(i));
            let bare = BuffV1 { name_buf: b.name_buf, name_len: b.name_len, ..BuffV1::default() };
            assert_eq!(bare == b, a.stats.is_empty(), "{}: the buff changes something exactly when it has stats", a.key);
            // somebody wants it
            assert!(a.fit.arr().iter().any(|&x| x > 0.0), "{}", a.key);
        }
    }

    /// Every screen can show three cards and reroll each once without running dry.
    #[test]
    fn each_tier_has_enough() {
        assert!(pool(Silver).len() >= 7);
        assert!(pool(Gold).len() >= 7);
        assert!(pool(Prismatic).len() >= 5);
        assert_eq!(pool(Silver).len() + pool(Gold).len() + pool(Prismatic).len(), AUGS.len());
        assert_eq!((pool(Silver).len(), pool(Gold).len(), pool(Prismatic).len()), (16, 16, 15));
    }

    /// Every triggered effect belongs to exactly one augment, and the 20 of 0.1.0 keep their numbers (the saved picks and
    /// the logs name them by key, the screens by number).
    #[test]
    fn every_effect_has_one_augment() {
        for e in 1..EV_N {
            let n = AUGS.iter().filter(|a| a.ev as usize == e).count();
            assert_eq!(n, 1, "effect #{e}");
        }
        assert_eq!(AUGS.iter().filter(|a| a.ev == Ev::Stat).count(), 20);
        assert!(AUGS[..20].iter().all(|a| a.ev == Ev::Stat), "the stat augments stay first");
        assert_eq!(of_ev(Ev::Goliath).map(|i| AUGS[i].key), Some("goliath"));
        assert_eq!(of_ev(Ev::Stat), None);
        const { assert!(EV_N <= 64, "an effect set is a u64") };
    }

    #[test]
    fn the_numbers_reach_the_buff() {
        let gc = by_key("glass_cannon").unwrap();
        let b = buff(gc);
        assert_eq!((b.hp_mult, b.attack_mult, b.magic_power_mult), (-20, 30, 30));
        let gs = by_key("giant_slayer").unwrap();
        let b = buff(gs);
        assert_eq!((b.base_attack_enemy_max_hp_damage, b.attack_speed_mult), (3, 15));
        let ua = by_key("ultimate_awakening").unwrap();
        assert_eq!(buff(ua).ult_cooldown_mult, 100);
        let go = by_key("goliath").unwrap();
        assert_eq!((buff(go).hp_mult, buff(go).attack_mult), (30, 15));
    }
}
