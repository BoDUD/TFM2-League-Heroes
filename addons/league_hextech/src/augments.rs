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
//! 0.4.0（用户 2026-11-26：「还有没有其他的海克斯可以做的」，选了「对齐+数值触发」）：照英雄联盟 26.23 的海克斯大乱斗
//! （Wiki 的 ARAM: Mayhem/Augments，244 个）再加 53 个——数值类 16 个（8 个是随场上情况变的，也走触发），触发类 37 个；
//! 已有的 10 个对齐它现在的效果和档位：大法师（放技能返还另一个技能的冷却）、终极觉醒（大招重置技能）、玻璃大炮、巨人杀手
//! 改成它的做法（巨人杀手不能变小），秘术冲拳、巨像的勇气、台风、烈焰烙印、坦克引擎、魔法飞弹换档位和效果。弱点暴露照旧
//! （它现在是「物品和持续伤害能暴击」，本游戏做不了）。英雄联盟的数值是它自己的单位，这里照上面的装备比例换算（攻击约 ×1.7、
//! 法强 ×2，按等级的「X～Y」从 1 级到 12 级）。第二批（用户：「现在是能做的海克斯都做了 这个理解对吗」）补上同一份列表里
//! 漏掉的 9 个：双生火焰、渴血、物理转魔法、魔法转物理、史莱姆时间、王冠之重、无尽收割、小蜜蜂、亡命之徒（中文名照
//! arammayhem.com 的简体页和游民星空转的官网公告）。两个「转」读不到「额外攻击力」，按比开局多出来的算，而且不扣原来的（扣成
//! 负数会出事）。一共 109 个：银 35、金 40、棱彩 34。
//!
//! 0.5.0（用户 2026-11-26：「接着做」）：同一份列表里剩下的三类里本游戏能做的 31 个——金币 / 随机 / 任务 10 个（捐赠、夺金、
//! 三个属性铁砧、两个质变、潘朵拉的盒子、超远狙击、高压锻炉），龙魂 6 个（四种龙魂、全能龙魂、男爵之手，效果照大小龙 mod 的
//! 龙魂在本包里做一份，不装大小龙也能用），技能海克斯 15 个（作用在选定的技能上：BP 面板里选，AI 默认技能，过载默认技能 2；
//! 面包和黄油 / 果酱固定技能 / 技能 2；嗜血束缚认哪个技能控的人都算）。一共 140 个：银 45、金 54、棱彩 41。
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
    // ---- 0.4.0：照英雄联盟 26.23 对齐的四个（以前是属性类）
    GlassCannon,
    GiantSlayer,
    Archmage,
    UltAwakening,
    // ---- 0.4.0：随场上情况变的属性
    LichBrain,
    Homeguard,
    LonelyWarrior,
    KillSecured,
    Steadfast,
    StillHere,
    Eureka,
    InfRecursion,
    // ---- 0.4.0：触发类（银）
    DiveBomber,
    Erosion,
    GuiltyPleasure,
    SlapAround,
    UltUnstoppable,
    MightyShield,
    Firefox,
    ShadowRunner,
    SwiftSafe,
    // ---- 0.4.0：触发类（金）
    ArcaneAxiom,
    BigBrain,
    Divine,
    Marksmage,
    Nightstalking,
    Boomerang,
    OutlawsGrit,
    Porcupine,
    Salvation,
    SapMagic,
    SharkBait,
    SoulEater,
    TakeEmDown,
    SkilledSniper,
    KillingTime,
    Sonata,
    // ---- 0.4.0：触发类（棱彩）
    CantTouch,
    Duality,
    MoshMonster,
    PromQueen,
    Grab,
    ThirdTime,
    TitansResolve,
    UltRevolution,
    FeyMagic,
    CircleOfDeath,
    DualWield,
    Earthwake,
    /// 0.4.0：银，双生火焰（技能命中时按暴击率发火焰）
    TwinFire,
    /// 0.4.0 第二批：26.23 列表里还有的八个
    Goredrink,
    Adapt,
    Escapade,
    SlimeTime,
    HeavyCrown,
    Decimation,
    Bees,
    Hellbent,
    /// 0.5.0：金币 / 随机 / 任务、龙魂、技能海克斯
    Donation,
    Goldrend,
    Stats1,
    Stats2,
    Stats3,
    TransmuteChaos,
    TransmutePrismatic,
    Pandora,
    FromDowntown,
    PressureCooker,
    InfernalSoul,
    HextechSoul,
    MountainSoul,
    OceanSoul,
    OmniSoul,
    HandOfBaron,
    AdaptiveWard,
    CrimsonCobalt,
    FlowOfSpirit,
    MercysStrike,
    Overloaded,
    RavenousBind,
    Rejuvenation,
    Siphon,
    StayResolute,
    Terror,
    TrustyWeapon,
    BreadButter,
    BreadJam,
    PursuitHaste,
    PursuitPower,
}

/// 一共几种（[`Ev::Stat`] 也算一种）。
pub const EV_N: usize = Ev::PursuitPower as usize + 1;

/// 一个人拿着的种类：每种一个位（0.4.0 起超过 64 种，用 u128）。
pub type EvSet = u128;

impl Ev {
    /// 一个人拿着的种类记成一个 [`EvSet`] 的位。
    pub const fn bit(self) -> EvSet {
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
    /// 法术强度（加一个数，0.4.0）
    MagicPower,
    /// 普攻射程（0.4.0）：远程英雄加这么多；近战英雄加 [`Field::MeleeRange`] 那么多（近战约 25000、远程约 60000）
    Range,
    MeleeRange,
}

impl Field {
    /// 引擎里这个字段是无符号的（不能写负数）。
    pub fn unsigned(self) -> bool {
        matches!(self, Field::DefencePenetration | Field::MagicResistancePenetration | Field::Toughness
            | Field::SkillDamagedReduce | Field::BaseAttackEnemyMaxHpDamage | Field::Range | Field::MeleeRange)
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

/// 作用在选定的那个技能上的（BP 面板里选技能 / 技能 2 / 大招）。
pub fn skill_aug(ev: Ev) -> bool {
    matches!(ev, Ev::AdaptiveWard | Ev::CrimsonCobalt | Ev::FlowOfSpirit | Ev::MercysStrike | Ev::Overloaded
        | Ev::Rejuvenation | Ev::Siphon | Ev::StayResolute | Ev::Terror | Ev::TrustyWeapon | Ev::PursuitHaste
        | Ev::PursuitPower)
}

/// 技能海克斯没选技能时用哪个格子（1 技能、2 技能 2、3 大招）：过载放在技能 2（放在大招上，大招差不多一直是好的），别的放在
/// 技能；面包和黄油 / 果酱固定技能 / 技能 2。不是技能海克斯：0。
pub fn ai_slot(ev: Ev) -> u8 {
    match ev {
        Ev::BreadButter => 1,
        Ev::BreadJam | Ev::Overloaded => 2,
        e if skill_aug(e) => 1,
        _ => 0,
    }
}

/// 拿到时随机给别的海克斯的（随机抽的时候不抽它们自己）。
pub fn meta_aug(ev: Ev) -> bool {
    matches!(ev, Ev::TransmuteChaos | Ev::TransmutePrismatic | Ev::Pandora)
}

/// 0.1.0 的 20 个，0.3.0 的 27 个，0.4.0 的 62 个，0.5.0 的 31 个接在后面。顺序就是编号（日志、画面用；存档里存的是 key，不是编号，所以以后
/// 只往后加）。0.4.0 对齐时改的是档位、说明、效果，位置不动。
pub static AUGS: [Aug; 140] = [
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
    // 0.4.0 对齐：英雄联盟的玻璃大炮是棱彩，最大生命封顶 70%，造成的伤害附带一部分真实伤害
    Aug { key: "glass_cannon", tier: Prismatic, name: ["玻璃大炮", "玻璃大砲", "Glass Cannon"],
          desc: ["最大生命 -30%；对英雄造成伤害时，额外造成其中 25%（近战）/ 15%（远程）的真实伤害",
                 "最大生命 -30%；對英雄造成傷害時，額外造成其中 25%（近戰）/ 15%（遠程）的真實傷害",
                 "-30% max health; damage to champions deals another 25% (melee) / 15% (ranged) of it as true damage"],
          stats: &[(HpMult, -30)],
          fit: w(0.5, 0.5, 0.4, 0.3, -1.0, 0.0, 0.8, -0.4, 0.0, 0.3), theme: T::Hybrid, ev: E::GlassCannon },
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
    // 0.4.0 对齐：英雄联盟的巨人杀手是棱彩，自己变小、打体型大的伤害高（本游戏不能变小，按最大生命比）
    Aug { key: "giant_slayer", tier: Prismatic, name: ["巨人杀手", "巨人殺手", "Giant Slayer"],
          desc: ["移动速度 +15%；打最大生命比你高的英雄时额外造成 10%～30% 的真实伤害（比你高 25%、50%、一倍起分别 15%、25%、30%）",
                 "移動速度 +15%；打最大生命比你高的英雄時額外造成 10%～30% 的真實傷害（比你高 25%、50%、一倍起分別 15%、25%、30%）",
                 "+15% move speed; hits on champions with more max HP than you deal 10-30% more as true damage (15%, 25%, 30% from 25%, 50%, 100% more)"],
          stats: &[(MoveSpeedMult, 15)],
          fit: w(0.6, 0.3, 0.6, 0.2, -0.3, 0.3, 0.8, 0.0, 0.0, 0.2), theme: T::Ad, ev: E::GiantSlayer },
    Aug { key: "arcane_surge", tier: Gold, name: ["奥术洪流", "奧術洪流", "Arcane Surge"],
          desc: ["法术强度 +30%，技能冷却 -13%", "法術強度 +30%，技能冷卻 -13%", "+30% ability power, -13% skill cooldowns"],
          stats: &[(MagicPowerMult, 30), (SkillCooldownMult, 15)],
          fit: w(0.0, 1.0, 0.0, 0.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), theme: T::Ap, ev: E::Stat },
    // ---------------- 棱彩 ----------------
    Aug { key: "slayer", tier: Prismatic, name: ["屠戮者", "屠戮者", "Slayer"],
          desc: ["攻击力 +40%，暴击率 +30%", "攻擊力 +40%，暴擊率 +30%", "+40% attack damage, +30% crit chance"],
          stats: &[(AttackMult, 40), (CritChance, 30)],
          fit: w(1.0, 0.0, 0.8, 0.0, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0), theme: T::Crit, ev: E::Stat },
    // 0.4.0 对齐：英雄联盟现在的大法师是「放一个技能，返还另一个随机技能的冷却」
    Aug { key: "archmage", tier: Prismatic, name: ["大法师", "大法師", "Archmage"],
          desc: ["放技能或大招时，随机另一个技能的冷却缩短这次冷却的 30%",
                 "放技能或大招時，隨機另一個技能的冷卻縮短這次冷卻的 30%",
                 "Casting a skill or your ultimate takes 30% of that cooldown off another random one"],
          stats: &[],
          fit: w(0.0, 0.7, 0.0, 1.0, 0.0, 0.0, 0.3, 0.4, 0.0, 0.0), theme: T::Haste, ev: E::Archmage },
    Aug { key: "immortal_colossus", tier: Prismatic, name: ["不朽巨像", "不朽巨像", "Immortal Colossus"],
          desc: ["最大生命 +35%，护甲和魔抗 +35%，韧性 +30%", "最大生命 +35%，護甲和魔抗 +35%，韌性 +30%",
                 "+35% max health, +35% armor and magic resist, +30% tenacity"],
          stats: &[(HpMult, 35), (DefenceMult, 35), (MagicResistanceMult, 35), (Toughness, 30)],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.8, 0.0, 0.2, 0.0, 0.0), theme: T::Tank, ev: E::Stat },
    Aug { key: "storm_fury", tier: Prismatic, name: ["风暴之怒", "風暴之怒", "Storm Fury"],
          desc: ["攻击速度 +70%，移动速度 +15%", "攻擊速度 +70%，移動速度 +15%", "+70% attack speed, +15% move speed"],
          stats: &[(AttackSpeedMult, 70), (MoveSpeedMult, 15)],
          fit: w(0.4, 0.0, 1.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.2), theme: T::Speed, ev: E::Stat },
    // 0.4.0 对齐：英雄联盟的终极觉醒是「放大招重置技能、之后一段时间技能急速很高」，外加大招急速
    Aug { key: "ultimate_awakening", tier: Prismatic, name: ["终极觉醒", "終極覺醒", "Ultimate Awakening"],
          desc: ["大招冷却 -23%；放大招时两个技能立刻转好，之后 15 秒技能冷却 -75%（20 秒一次）",
                 "大招冷卻 -23%；放大招時兩個技能立刻轉好，之後 15 秒技能冷卻 -75%（20 秒一次）",
                 "-23% ultimate cooldown; your ultimate readies both skills and cuts their cooldowns by 75% for 15 s (every 20 s)"],
          stats: &[(UltCooldownMult, 30)],
          fit: w(0.2, 0.5, 0.0, 1.0, 0.2, 0.3, 0.4, 0.4, 0.0, 0.0), theme: T::Haste, ev: E::UltAwakening },
    // ================ 0.3.0：触发类 ================
    // ---------------- 银 ----------------
    // 0.4.0 对齐：英雄联盟的烈焰烙印是金，普攻叠的燃烧
    Aug { key: "firebrand", tier: Gold, name: ["烈焰烙印", "烈焰烙印", "Firebrand"],
          desc: ["普攻命中英雄时点燃 5 秒：每秒造成目标最大生命 0.4% 的魔法伤害，可叠加（最多 5 层），再命中刷新时间",
                 "普攻命中英雄時點燃 5 秒：每秒造成目標最大生命 0.4% 的魔法傷害，可疊加（最多 5 層），再命中刷新時間",
                 "Basic attacks burn champions for 5 s: 0.4% of their max HP as magic damage a second, stacking up to 5, each hit refreshing it"],
          stats: &[],
          fit: w(0.6, 0.2, 1.0, 0.0, 0.2, 0.4, 0.2, 0.0, 0.0, 0.2), theme: T::OnHit, ev: E::Firebrand },
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
    // 0.4.0 对齐：英雄联盟的坦克引擎是金，每层最大生命 +5%、体型变大，不封顶，阵亡掉 65%
    Aug { key: "tank_engine", tier: Gold, name: ["坦克引擎", "坦克引擎", "Tank Engine"],
          desc: ["每次参与击杀叠一层：最大生命 +5%，每 2 层体型大一档（最多 4 档）；阵亡时失去 65% 的层数",
                 "每次參與擊殺疊一層：最大生命 +5%，每 2 層體型大一檔（最多 4 檔）；陣亡時失去 65% 的層數",
                 "Each takedown adds a stack: +5% max HP, a size step every 2 stacks (up to 4); dying loses 65% of the stacks"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.6, 0.0, 0.3, 0.3, 0.0), theme: T::Tank, ev: E::TankEngine },
    // 0.4.0 对齐：英雄联盟的秘术冲拳是棱彩，每次普攻所有技能（含大招）冷却 -1.25 秒
    Aug { key: "mystic_punch", tier: Prismatic, name: ["秘术冲拳", "秘術衝拳", "Mystic Punch"],
          desc: ["每次普攻，技能、技能 2 和大招的冷却各缩短 1.25 秒", "每次普攻，技能、技能 2 和大招的冷卻各縮短 1.25 秒",
                 "Each basic attack takes 1.25 s off both skills' and your ultimate's cooldowns"],
          stats: &[],
          fit: w(0.4, 0.2, 1.0, 0.3, 0.0, 0.5, 0.2, 0.0, 0.0, 0.0), theme: T::Haste, ev: E::MysticPunch },
    Aug { key: "heavy_hitter", tier: Silver, name: ["重击手", "重擊手", "Heavy Hitter"],
          desc: ["命中英雄时额外造成自身最大生命 3% 的物理伤害（每个目标 0.5 秒一次）",
                 "命中英雄時額外造成自身最大生命 3% 的物理傷害（每個目標 0.5 秒一次）",
                 "Hits on champions deal 3% of your max HP as bonus physical damage (0.5 s per target)"],
          stats: &[],
          fit: w(0.3, 0.0, 0.4, 0.0, 0.8, 0.8, 0.0, 0.0, 0.5, 0.0), theme: T::OnHit, ev: E::HeavyHitter },
    // 0.4.0 对齐：英雄联盟的魔法飞弹是金，技能命中时 3 枚按目标最大生命的真实伤害飞弹
    Aug { key: "magic_missile", tier: Gold, name: ["魔法飞弹", "魔法飛彈", "Magic Missile"],
          desc: ["技能命中英雄时，向他射出 3 枚飞弹，每枚造成目标最大生命 0.4%～1%（随等级）的真实伤害（每个技能 6 秒一次）",
                 "技能命中英雄時，向他射出 3 枚飛彈，每枚造成目標最大生命 0.4%～1%（隨等級）的真實傷害（每個技能 6 秒一次）",
                 "Skill hits on champions fire 3 missiles at them, each dealing 0.4-1% (by level) of their max HP as true damage (once per 6 s per skill)"],
          stats: &[],
          fit: w(0.0, 0.7, 0.0, 1.0, 0.0, 0.0, 0.3, 0.3, 0.0, 0.0), theme: T::Ap, ev: E::MagicMissile },
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
    // 0.4.0 对齐：英雄联盟的巨像的勇气是棱彩，护盾 150～450 + 4% 最大生命
    Aug { key: "courage_of_the_colossus", tier: Prismatic, name: ["巨像的勇气", "巨像的勇氣", "Courage of the Colossus"],
          desc: ["控住敌方英雄时，获得 150～450（随等级）+ 4% 最大生命的护盾（3 秒）。冷却 5 秒",
                 "控住敵方英雄時，獲得 150～450（隨等級）+ 4% 最大生命的護盾（3 秒）。冷卻 5 秒",
                 "Immobilizing an enemy champion shields you for 150-450 (by level) + 4% max HP (3 s). 5 s cooldown"],
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
    // 0.4.0 对齐：英雄联盟的台风是银，普攻多射一个目标
    Aug { key: "typhoon", tier: Silver, name: ["台风", "颱風", "Typhoon"],
          desc: ["普攻命中英雄时，向身边另一个敌方英雄射出风刃：30% 攻击力 的物理伤害（约 0.7 秒一次）",
                 "普攻命中英雄時，向身邊另一個敵方英雄射出風刃：30% 攻擊力 的物理傷害（約 0.7 秒一次）",
                 "Basic attacks on champions fire a wind blade at another nearby enemy champion: 30% AD physical (about every 0.7 s)"],
          stats: &[],
          fit: w(0.7, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2), theme: T::OnHit, ev: E::Typhoon },
    Aug { key: "sacred_ward", tier: Prismatic, name: ["圣光庇佑", "聖光庇佑", "Sacred Ward"],
          desc: ["每 8 秒给身边生命比例最低的友方英雄（含自己）100 + 25% 法强 + 8% 其最大生命 的护盾（3 秒）和 20% 移动速度",
                 "每 8 秒給身邊生命比例最低的友方英雄（含自己）100 + 25% 法強 + 8% 其最大生命 的護盾（3 秒）和 20% 移動速度",
                 "Every 8 s the nearby ally with the lowest HP (you too) gets a 100 + 25% AP + 8% max HP shield (3 s) and +20% speed"],
          stats: &[],
          fit: w(0.0, 0.4, 0.0, 0.5, 0.2, 0.0, 0.0, 1.0, 0.0, 0.0), theme: T::Guard, ev: E::SacredWard },
    // ================ 0.4.0：英雄联盟 26.23 的海克斯大乱斗 ================
    // ---------------- 银：属性 ----------------
    Aug { key: "fortified", tier: Silver, name: ["坚固", "堅固", "Fortified"],
          desc: ["护甲 +20，再 +25%", "護甲 +20，再 +25%", "+20 armor, then +25% armor"],
          stats: &[(Defence, 20), (DefenceMult, 25)],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.6, 0.0, 0.2, 0.4, 0.0), theme: T::Tank, ev: E::Stat },
    Aug { key: "mystic_guard", tier: Silver, name: ["秘术守护", "秘術守護", "Mystic Guard"],
          desc: ["魔抗 +20，再 +25%", "魔抗 +20，再 +25%", "+20 magic resist, then +25% magic resist"],
          stats: &[(MagicResistance, 20), (MagicResistanceMult, 25)],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.6, 0.0, 0.3, 0.3, 0.0), theme: T::Tank, ev: E::Stat },
    Aug { key: "zealot", tier: Silver, name: ["狂热", "狂熱", "Zealot"],
          desc: ["攻击速度 +25%，暴击率 +15%", "攻擊速度 +25%，暴擊率 +15%", "+25% attack speed, +15% crit chance"],
          stats: &[(AttackSpeedMult, 25), (CritChance, 15)],
          fit: w(0.7, 0.0, 1.0, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.2), theme: T::Crit, ev: E::Stat },
    Aug { key: "scoped_weapons", tier: Silver, name: ["瞄准镜武器", "瞄準鏡武器", "Scoped Weapons"],
          desc: ["普攻射程增加：近战约 +50%，远程约 +8%", "普攻射程增加：近戰約 +50%，遠程約 +8%",
                 "Longer basic attack range: about +50% for melee, +8% for ranged"],
          stats: &[(Range, 5_000), (MeleeRange, 12_000)],
          fit: w(0.6, 0.0, 1.0, 0.0, 0.0, 0.5, 0.2, 0.0, 0.5, 0.2), theme: T::Ad, ev: E::Stat },
    // ---------------- 银：随场上变的属性 ----------------
    Aug { key: "lich_brain", tier: Silver, name: ["巫妖之脑", "巫妖之腦", "Lich Brain"],
          desc: ["法术强度 +40，另外获得 4% 最大生命的法术强度", "法術強度 +40，另外獲得 4% 最大生命的法術強度",
                 "+40 ability power, plus ability power equal to 4% of your max HP"],
          stats: &[(MagicPower, 40)],
          fit: w(0.0, 1.0, 0.0, 0.5, 0.4, 0.2, 0.0, 0.2, 0.0, 0.0), theme: T::Ap, ev: E::LichBrain },
    Aug { key: "homeguard", tier: Silver, name: ["家园卫士", "家園衛士", "Homeguard"],
          desc: ["6 秒没受到伤害时移动速度 +40%（受到伤害就没了）", "6 秒沒受到傷害時移動速度 +40%（受到傷害就沒了）",
                 "+40% move speed after 6 s without taking damage (lost when hit)"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.5, 0.5, 0.2, 0.0), theme: T::Speed, ev: E::Homeguard },
    Aug { key: "lonely_warrior", tier: Silver, name: ["孤勇者", "孤勇者", "Lonely Warrior"],
          desc: ["身边每有一个敌方英雄：攻击速度 +6%，护甲和魔抗 +6", "身邊每有一個敵方英雄：攻擊速度 +6%，護甲和魔抗 +6",
                 "For each enemy champion near you: +6% attack speed, +6 armor and magic resist"],
          stats: &[],
          fit: w(0.2, 0.0, 0.3, 0.0, 0.5, 1.0, 0.2, 0.0, 0.8, -0.4), theme: T::Tank, ev: E::LonelyWarrior },
    Aug { key: "kill_secured", tier: Silver, name: ["收割在望", "收割在望", "Kill Secured"],
          desc: ["身边有生命低于 40% 的敌方英雄时，移动速度 +35%", "身邊有生命低於 40% 的敵方英雄時，移動速度 +35%",
                 "+35% move speed while an enemy champion below 40% HP is near"],
          stats: &[],
          fit: w(0.2, 0.2, 0.1, 0.0, 0.0, 0.4, 1.0, 0.0, 0.5, -0.2), theme: T::Speed, ev: E::KillSecured },
    // ---------------- 银：触发 ----------------
    Aug { key: "dive_bomber", tier: Silver, name: ["俯冲轰炸", "俯衝轟炸", "Dive Bomber"],
          desc: ["阵亡时爆炸：身边的敌方英雄受到其最大生命 15% 的真实伤害", "陣亡時爆炸：身邊的敵方英雄受到其最大生命 15% 的真實傷害",
                 "Dying explodes: enemy champions around you take 15% of their max HP as true damage"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.0, 0.6, 0.6, 0.6, 0.2, 0.6, 0.0), theme: T::Hybrid, ev: E::DiveBomber },
    Aug { key: "erosion", tier: Silver, name: ["侵蚀", "侵蝕", "Erosion"],
          desc: ["命中英雄时使其护甲和魔抗 -2%（4 秒），可叠加，最多 -30%", "命中英雄時使其護甲和魔抗 -2%（4 秒），可疊加，最多 -30%",
                 "Hits cut a champion's armor and magic resist by 2% (4 s), stacking to 30%"],
          stats: &[],
          fit: w(0.5, 0.5, 0.6, 0.4, 0.0, 0.3, 0.3, 0.2, 0.0, 0.2), theme: T::OnHit, ev: E::Erosion },
    Aug { key: "guilty_pleasure", tier: Silver, name: ["罪恶快感", "罪惡快感", "Guilty Pleasure"],
          desc: ["控住敌方英雄时回复 40～300（随等级）+ 1.5% 最大生命。冷却 5 秒",
                 "控住敵方英雄時回復 40～300（隨等級）+ 1.5% 最大生命。冷卻 5 秒",
                 "Immobilizing an enemy champion heals you 40-300 (by level) + 1.5% max HP. 5 s cooldown"],
          stats: &[],
          fit: w(0.0, 0.2, 0.0, 0.3, 0.7, 0.6, 0.0, 0.5, 0.3, 0.0).with_cc(1.0), theme: T::Sustain, ev: E::GuiltyPleasure },
    Aug { key: "slap_around", tier: Silver, name: ["左右开弓", "左右開弓", "Slap Around"],
          desc: ["控住敌方英雄时永久获得 10 攻击力或 20 法术强度（哪个高给哪个），阵亡时失去一半。冷却 5 秒",
                 "控住敵方英雄時永久獲得 10 攻擊力或 20 法術強度（哪個高給哪個），陣亡時失去一半。冷卻 5 秒",
                 "Immobilizing an enemy champion grants 10 AD or 20 AP for good (whichever is higher); dying loses half. 5 s cooldown"],
          stats: &[],
          fit: w(0.2, 0.2, 0.0, 0.2, 0.2, 0.3, 0.1, 0.2, 0.1, 0.0).with_cc(1.0), theme: T::Hybrid, ev: E::SlapAround },
    Aug { key: "ultimate_unstoppable", tier: Silver, name: ["终极不可阻挡", "終極不可阻擋", "Ultimate Unstoppable"],
          desc: ["放大招后 3 秒内韧性 +90%，几乎不受控制（冷却 8 秒）", "放大招後 3 秒內韌性 +90%，幾乎不受控制（冷卻 8 秒）",
                 "Casting your ultimate gives +90% tenacity for 3 s, shrugging off nearly all crowd control (8 s cooldown)"],
          stats: &[],
          fit: w(0.2, 0.2, 0.0, 0.3, 0.5, 0.8, 0.6, 0.2, 0.5, 0.0), theme: T::Guard, ev: E::UltUnstoppable },
    Aug { key: "mighty_shield", tier: Silver, name: ["强力护盾", "強力護盾", "Mighty Shield"],
          desc: ["获得护盾时，3 秒内攻击力 +30～80 或法术强度 +60～160（随等级，哪个高给哪个）。冷却 5 秒",
                 "獲得護盾時，3 秒內攻擊力 +30～80 或法術強度 +60～160（隨等級，哪個高給哪個）。冷卻 5 秒",
                 "Gaining a shield gives +30-80 AD or +60-160 AP (by level, whichever is higher) for 3 s. 5 s cooldown"],
          stats: &[],
          fit: w(0.3, 0.2, 0.0, 0.1, 0.6, 0.5, 0.0, 0.6, 0.0, 0.0), theme: T::Guard, ev: E::MightyShield },
    Aug { key: "firefox", tier: Silver, name: ["狐火", "狐火", "Firefox"],
          desc: ["每 7 秒，身边有敌方英雄时放出 3 团狐火打最近的敌方英雄：每团 25～100（随等级）+ 10% 攻击力 + 15% 法强 的魔法伤害；移动速度 +25%（1.5 秒）",
                 "每 7 秒，身邊有敵方英雄時放出 3 團狐火打最近的敵方英雄：每團 25～100（隨等級）+ 10% 攻擊力 + 15% 法強 的魔法傷害；移動速度 +25%（1.5 秒）",
                 "Every 7 s with an enemy champion near, 3 fox-fires strike the nearest: 25-100 (by level) + 10% AD + 15% AP magic each; +25% move speed (1.5 s)"],
          stats: &[],
          fit: w(0.2, 0.7, 0.0, 0.7, 0.0, 0.0, 0.6, 0.2, 0.0, 0.0), theme: T::Ap, ev: E::Firefox },
    Aug { key: "shadow_runner", tier: Silver, name: ["暗影疾奔", "暗影疾奔", "Shadow Runner"],
          desc: ["冲刺、闪现之后 2 秒内移动速度 +60%", "衝刺、閃現之後 2 秒內移動速度 +60%",
                 "+60% move speed for 2 s after a dash or blink"],
          stats: &[],
          fit: w(0.3, 0.0, 0.2, 0.0, 0.0, 0.4, 1.0, 0.0, 0.4, 0.0), theme: T::Speed, ev: E::ShadowRunner },
    Aug { key: "swift_and_safe", tier: Silver, name: ["快速安全", "快速安全", "Swift and Safe"],
          desc: ["冲刺、闪现之后获得 60～280（随等级）+ 50% 攻击力 + 25% 法强 的护盾（2 秒）。冷却 5 秒",
                 "衝刺、閃現之後獲得 60～280（隨等級）+ 50% 攻擊力 + 25% 法強 的護盾（2 秒）。冷卻 5 秒",
                 "A dash or blink shields you for 60-280 (by level) + 50% AD + 25% AP (2 s). 5 s cooldown"],
          stats: &[],
          fit: w(0.3, 0.1, 0.2, 0.0, 0.2, 0.6, 0.8, 0.0, 0.4, 0.0), theme: T::Guard, ev: E::SwiftSafe },
    // ---------------- 金：属性 ----------------
    Aug { key: "its_critical", tier: Gold, name: ["致命一击", "致命一擊", "It's Critical"],
          desc: ["暴击率 +40%", "暴擊率 +40%", "+40% crit chance"],
          stats: &[(CritChance, 40)],
          fit: w(0.8, 0.0, 1.0, 0.0, 0.0, 0.1, 0.2, 0.0, 0.0, 0.4), theme: T::Crit, ev: E::Stat },
    Aug { key: "recursion", tier: Gold, name: ["递归", "遞迴", "Recursion"],
          desc: ["技能和大招冷却 -31%", "技能和大招冷卻 -31%", "-31% skill and ultimate cooldowns"],
          stats: &[(SkillCooldownMult, 45), (UltCooldownMult, 45)],
          fit: w(0.0, 0.5, 0.0, 1.0, 0.2, 0.2, 0.3, 0.6, 0.0, 0.0), theme: T::Haste, ev: E::Stat },
    Aug { key: "scopier_weapons", tier: Gold, name: ["高倍瞄准镜", "高倍瞄準鏡", "Scopier Weapons"],
          desc: ["普攻射程增加：近战约 +100%，远程约 +17%", "普攻射程增加：近戰約 +100%，遠程約 +17%",
                 "Longer basic attack range: about +100% for melee, +17% for ranged"],
          stats: &[(Range, 10_000), (MeleeRange, 25_000)],
          fit: w(0.6, 0.0, 1.0, 0.0, 0.0, 0.5, 0.2, 0.0, 0.5, 0.2), theme: T::Ad, ev: E::Stat },
    // ---------------- 金：随场上变的属性 ----------------
    Aug { key: "steadfaster_presence", tier: Gold, name: ["坚定之姿", "堅定之姿", "Steadfaster Presence"],
          desc: ["韧性 +20%，护甲和魔抗 +16%；生命低于 40% 时再加一倍", "韌性 +20%，護甲和魔抗 +16%；生命低於 40% 時再加一倍",
                 "+20% tenacity, +16% armor and magic resist; doubled below 40% HP"],
          stats: &[(Toughness, 20), (DefenceMult, 16), (MagicResistanceMult, 16)],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.8, 0.0, 0.2, 0.4, 0.0), theme: T::Tank, ev: E::Steadfast },
    Aug { key: "still_here", tier: Gold, name: ["还在这里", "還在這裡", "Still Here"],
          desc: ["每损失 10% 生命：攻击速度 +10%，生命偷取 +2%", "每損失 10% 生命：攻擊速度 +10%，生命偷取 +2%",
                 "For every 10% of health missing: +10% attack speed, +2% life steal"],
          stats: &[],
          fit: w(0.7, 0.0, 1.0, 0.0, 0.0, 0.8, 0.2, 0.0, 0.4, 0.0), theme: T::Sustain, ev: E::StillHere },
    // ---------------- 金：触发 ----------------
    Aug { key: "arcane_axiom", tier: Gold, name: ["奥术公理", "奧術公理", "Arcane Axiom"],
          desc: ["参与击杀英雄时，大招冷却缩短其总冷却的 20%", "參與擊殺英雄時，大招冷卻縮短其總冷卻的 20%",
                 "Champion takedowns take 20% of its total cooldown off your ultimate"],
          stats: &[],
          fit: w(0.3, 0.5, 0.0, 0.8, 0.0, 0.3, 0.8, 0.2, 0.0, 0.0), theme: T::Haste, ev: E::ArcaneAxiom },
    Aug { key: "big_brain", tier: Gold, name: ["大聪明", "大聰明", "Big Brain"],
          desc: ["获得 150% 法强的护盾，直到被打破；每 70 秒和复活时重新获得", "獲得 150% 法強的護盾，直到被打破；每 70 秒和復活時重新獲得",
                 "A shield of 150% AP that lasts until broken; it comes back every 70 s and on respawn"],
          stats: &[],
          fit: w(0.0, 1.0, 0.0, 0.8, -0.3, 0.0, 0.0, 0.2, 0.0, 0.2), theme: T::Guard, ev: E::BigBrain },
    Aug { key: "divine_intervention", tier: Gold, name: ["神圣干预", "神聖干預", "Divine Intervention"],
          desc: ["身边的友方英雄（含自己）生命低于 35% 时，1 秒后你身边的友方英雄无敌 2.5 秒。冷却 35 秒",
                 "身邊的友方英雄（含自己）生命低於 35% 時，1 秒後你身邊的友方英雄無敵 2.5 秒。冷卻 35 秒",
                 "When an ally near you (or you) drops below 35% HP, allies around you become invulnerable for 2.5 s after 1 s. 35 s cooldown"],
          stats: &[],
          fit: w(0.0, 0.2, 0.0, 0.4, 0.6, 0.2, 0.0, 1.0, 0.2, 0.0), theme: T::Guard, ev: E::Divine },
    Aug { key: "marksmage", tier: Gold, name: ["法师射手", "法師射手", "Marksmage"],
          desc: ["普攻命中时额外造成 45% 法强 的物理伤害", "普攻命中時額外造成 45% 法強 的物理傷害",
                 "Basic attacks deal 45% AP bonus physical damage"],
          stats: &[],
          fit: w(-0.6, 1.0, 0.5, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2), theme: T::OnHit, ev: E::Marksmage },
    Aug { key: "nightstalking", tier: Gold, name: ["暗夜潜行", "暗夜潛行", "Nightstalking"],
          desc: ["参与击杀英雄后隐身 1.5 秒，移动速度 +40%", "參與擊殺英雄後隱身 1.5 秒，移動速度 +40%",
                 "A champion takedown makes you invisible for 1.5 s with +40% move speed"],
          stats: &[],
          fit: w(0.3, 0.3, 0.0, 0.2, 0.0, 0.2, 1.0, 0.0, 0.4, -0.2), theme: T::Speed, ev: E::Nightstalking },
    Aug { key: "ok_boomerang", tier: Gold, name: ["好的回旋镖", "好的迴旋鏢", "OK Boomerang"],
          desc: ["每 10 秒向最近的敌方英雄掷出回旋刃，去程、回程各打一次沿途的敌方英雄：30～150（随等级）+ 40% 攻击力 + 30% 法强 的物理伤害",
                 "每 10 秒向最近的敵方英雄擲出迴旋刃，去程、回程各打一次沿途的敵方英雄：30～150（隨等級）+ 40% 攻擊力 + 30% 法強 的物理傷害",
                 "Every 10 s a boomerang flies at the nearest enemy champion and back, hitting champions in its path each way: 30-150 (by level) + 40% AD + 30% AP physical"],
          stats: &[],
          fit: w(0.6, 0.3, 0.5, 0.3, 0.0, 0.2, 0.2, 0.0, 0.0, 0.5), theme: T::Hybrid, ev: E::Boomerang },
    Aug { key: "outlaws_grit", tier: Gold, name: ["亡命之徒的胆量", "亡命之徒的膽量", "Outlaw's Grit"],
          desc: ["冲刺、闪现之后护甲和魔抗 +10（15 秒），最多叠 5 层", "衝刺、閃現之後護甲和魔抗 +10（15 秒），最多疊 5 層",
                 "Dashes and blinks give +10 armor and magic resist for 15 s, stacking 5 times"],
          stats: &[],
          fit: w(0.3, 0.0, 0.2, 0.0, 0.4, 0.8, 0.6, 0.0, 0.6, 0.0), theme: T::Tank, ev: E::OutlawsGrit },
    Aug { key: "porcupine", tier: Gold, name: ["刺猬", "刺蝟", "Porcupine"],
          desc: ["累计受到 400～3000（随等级）点伤害后爆发：身边的敌方英雄受到 75～200 + 60% 护甲 + 60% 魔抗 的物理伤害，减速 30%（1.5 秒）",
                 "累計受到 400～3000（隨等級）點傷害後爆發：身邊的敵方英雄受到 75～200 + 60% 護甲 + 60% 魔抗 的物理傷害，減速 30%（1.5 秒）",
                 "After taking 400-3000 (by level) damage, burst: enemy champions near you take 75-200 + 60% armor + 60% MR physical and a 30% slow (1.5 s)"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.0, 1.0, 0.6, 0.0, 0.2, 0.6, 0.0), theme: T::Tank, ev: E::Porcupine },
    Aug { key: "salvation", tier: Gold, name: ["救赎", "救贖", "Salvation"],
          desc: ["生命低于 50% 时放出冲击波：身边的敌方英雄受到 100～500（随等级）的魔法伤害，你和身边的友方英雄回复 150～450。冷却 70 秒",
                 "生命低於 50% 時放出衝擊波：身邊的敵方英雄受到 100～500（隨等級）的魔法傷害，你和身邊的友方英雄回復 150～450。冷卻 70 秒",
                 "Dropping below 50% HP sends a shockwave: 100-500 (by level) magic to enemy champions around, and you and allies near heal 150-450. 70 s cooldown"],
          stats: &[],
          fit: w(0.0, 0.3, 0.0, 0.3, 0.6, 0.4, 0.0, 0.8, 0.2, 0.0), theme: T::Sustain, ev: E::Salvation },
    Aug { key: "sap_magic", tier: Gold, name: ["汲取魔力", "汲取魔力", "Sap Magic"],
          desc: ["每 20 秒，下一次普攻额外造成 80～300（随等级）的物理伤害，回复 50～250 + 8% 最大生命；每放一次技能这个冷却缩短 3 秒",
                 "每 20 秒，下一次普攻額外造成 80～300（隨等級）的物理傷害，回復 50～250 + 8% 最大生命；每放一次技能這個冷卻縮短 3 秒",
                 "Every 20 s your next basic attack deals 80-300 (by level) bonus physical and heals 50-250 + 8% max HP; each cast takes 3 s off"],
          stats: &[],
          fit: w(0.6, 0.0, 0.8, 0.2, 0.2, 0.8, 0.2, 0.0, 0.4, 0.0), theme: T::Sustain, ev: E::SapMagic },
    Aug { key: "shark_bait", tier: Gold, name: ["鲨鱼饵", "鯊魚餌", "Shark Bait"],
          desc: ["生命低于 10% 时变成鲨鱼饵 3.5 秒（期间不会死），结束时咬向身边的敌方英雄：120～350（随等级）+ 30% 目标已损失生命 的魔法伤害。冷却 90 秒",
                 "生命低於 10% 時變成鯊魚餌 3.5 秒（期間不會死），結束時咬向身邊的敵方英雄：120～350（隨等級）+ 30% 目標已損失生命 的魔法傷害。冷卻 90 秒",
                 "Below 10% HP you become shark bait for 3.5 s (you cannot die), then a shark bites enemy champions near: 120-350 (by level) + 30% of their missing HP magic. 90 s cooldown"],
          stats: &[],
          fit: w(0.2, 0.2, 0.2, 0.2, 0.4, 0.8, 0.5, 0.0, 0.5, 0.0), theme: T::Guard, ev: E::SharkBait },
    Aug { key: "soul_eater", tier: Gold, name: ["噬魂者", "噬魂者", "Soul Eater"],
          desc: ["控住敌方英雄时永久获得 40 最大生命。冷却 5 秒", "控住敵方英雄時永久獲得 40 最大生命。冷卻 5 秒",
                 "Immobilizing an enemy champion gives 40 max HP for good. 5 s cooldown"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.2, 1.0, 0.6, 0.0, 0.4, 0.3, 0.0).with_cc(1.0), theme: T::Tank, ev: E::SoulEater },
    Aug { key: "take_em_down", tier: Gold, name: ["拿下他们", "拿下他們", "Take 'em Down"],
          desc: ["命中同一个英雄叠层（5 秒），第 5 层引爆：造成其已损失生命 12% 的魔法伤害，并回复其中的 50%",
                 "命中同一個英雄疊層（5 秒），第 5 層引爆：造成其已損失生命 12% 的魔法傷害，並回復其中的 50%",
                 "Hits stack on a champion (5 s); the 5th detonates for 12% of their missing HP as magic damage and heals you 50% of it"],
          stats: &[],
          fit: w(0.5, 0.4, 0.8, 0.3, 0.0, 0.6, 0.6, 0.0, 0.3, 0.0), theme: T::OnHit, ev: E::TakeEmDown },
    Aug { key: "skilled_sniper", tier: Gold, name: ["神射手", "神射手", "Skilled Sniper"],
          desc: ["技能命中远处（超过一个远程射程）的英雄时，这个技能的冷却缩短 80%", "技能命中遠處（超過一個遠程射程）的英雄時，這個技能的冷卻縮短 80%",
                 "Skill hits on champions far away (beyond a ranged attack's reach) take 80% off that skill's cooldown"],
          stats: &[],
          fit: w(0.0, 0.8, 0.0, 1.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.4), theme: T::Haste, ev: E::SkilledSniper },
    Aug { key: "its_killing_time", tier: Gold, name: ["杀戮时刻", "殺戮時刻", "It's Killing Time"],
          desc: ["放大招时给最近的敌方英雄打上死亡印记，5 秒后引爆：这 5 秒里他损失的生命的 30%（真实伤害）",
                 "放大招時給最近的敵方英雄打上死亡印記，5 秒後引爆：這 5 秒裡他損失的生命的 30%（真實傷害）",
                 "Your ultimate marks the nearest enemy champion; 5 s later it detonates for 30% of the health they lost meanwhile (true damage)"],
          stats: &[],
          fit: w(0.6, 0.4, 0.2, 0.4, 0.0, 0.3, 1.0, 0.0, 0.2, 0.0), theme: T::Ad, ev: E::KillingTime },
    Aug { key: "sonata", tier: Gold, name: ["奏鸣曲", "奏鳴曲", "Sonata"],
          desc: ["每 10 秒轮流：给身边的友方英雄（含自己）回复 40～200（随等级）+ 20% 法强，或移动速度 +30%（2 秒）",
                 "每 10 秒輪流：給身邊的友方英雄（含自己）回復 40～200（隨等級）+ 20% 法強，或移動速度 +30%（2 秒）",
                 "Every 10 s, in turn: heal allies near you (you too) for 40-200 (by level) + 20% AP, or give them +30% move speed (2 s)"],
          stats: &[],
          fit: w(0.0, 0.5, 0.0, 0.6, 0.0, 0.0, 0.0, 1.0, 0.0, 0.2), theme: T::Sustain, ev: E::Sonata },
    // ---------------- 棱彩：属性 ----------------
    Aug { key: "scopiest_weapons", tier: Prismatic, name: ["超远瞄准镜", "超遠瞄準鏡", "Scopiest Weapons"],
          desc: ["普攻射程增加：近战约 +140%，远程约 +27%", "普攻射程增加：近戰約 +140%，遠程約 +27%",
                 "Longer basic attack range: about +140% for melee, +27% for ranged"],
          stats: &[(Range, 16_000), (MeleeRange, 35_000)],
          fit: w(0.6, 0.0, 1.0, 0.0, 0.0, 0.5, 0.2, 0.0, 0.5, 0.2), theme: T::Ad, ev: E::Stat },
    // ---------------- 棱彩：随场上变的属性 ----------------
    Aug { key: "eureka", tier: Prismatic, name: ["尤里卡", "尤里卡", "Eureka"],
          desc: ["法术强度越高冷却越短：每 100 法强，技能和大招的技能急速 +15", "法術強度越高冷卻越短：每 100 法強，技能和大招的技能急速 +15",
                 "Ability power shortens cooldowns: every 100 AP gives your skills and ultimate 15 ability haste"],
          stats: &[],
          fit: w(0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.3, 0.0, 0.0), theme: T::Haste, ev: E::Eureka },
    Aug { key: "infinite_recursion", tier: Prismatic, name: ["无限递归", "無限遞迴", "Infinite Recursion"],
          desc: ["技能和大招冷却 -29%；每次参与击杀英雄，技能急速再 +3（最多 +60）", "技能和大招冷卻 -29%；每次參與擊殺英雄，技能急速再 +3（最多 +60）",
                 "-29% skill and ultimate cooldowns; each champion takedown adds 3 ability haste (up to 60)"],
          stats: &[(SkillCooldownMult, 40), (UltCooldownMult, 40)],
          fit: w(0.2, 0.6, 0.0, 1.0, 0.2, 0.3, 0.5, 0.5, 0.0, 0.0), theme: T::Haste, ev: E::InfRecursion },
    // ---------------- 棱彩：触发 ----------------
    Aug { key: "cant_touch_this", tier: Prismatic, name: ["碰不到我", "碰不到我", "Can't Touch This"],
          desc: ["放大招后 2 秒无敌（冷却 8 秒）", "放大招後 2 秒無敵（冷卻 8 秒）", "Casting your ultimate makes you invulnerable for 2 s (8 s cooldown)"],
          stats: &[],
          fit: w(0.3, 0.3, 0.0, 0.4, 0.3, 0.8, 0.8, 0.2, 0.5, 0.0), theme: T::Guard, ev: E::CantTouch },
    Aug { key: "master_of_duality", tier: Prismatic, name: ["二元大师", "二元大師", "Master of Duality"],
          desc: ["普攻命中时法术强度 +10～30，技能命中时攻击力 +6～18（随等级；5 秒，可叠加，最多 10 层）",
                 "普攻命中時法術強度 +10～30，技能命中時攻擊力 +6～18（隨等級；5 秒，可疊加，最多 10 層）",
                 "Basic attacks give 10-30 AP, skill hits give 6-18 AD (by level; 5 s, stacking 10 times)"],
          stats: &[],
          fit: w(0.6, 0.6, 0.8, 0.6, 0.0, 0.4, 0.3, 0.0, 0.2, 0.2), theme: T::Hybrid, ev: E::Duality },
    Aug { key: "mosh_monster", tier: Prismatic, name: ["狂舞怪兽", "狂舞怪獸", "Mosh Monster"],
          desc: ["放大招时 8 秒内最大生命 +300～750（随等级）、体型变大，身边的敌方英雄减速 50%（1.5 秒）；每次参与击杀永久 +20 最大生命",
                 "放大招時 8 秒內最大生命 +300～750（隨等級）、體型變大，身邊的敵方英雄減速 50%（1.5 秒）；每次參與擊殺永久 +20 最大生命",
                 "Your ultimate gives 300-750 (by level) max HP and a bigger body for 8 s and slows enemy champions near by 50% (1.5 s); takedowns add 20 max HP for good"],
          stats: &[],
          fit: w(0.0, 0.0, 0.0, 0.3, 1.0, 0.8, 0.0, 0.3, 0.6, 0.0), theme: T::Tank, ev: E::MoshMonster },
    Aug { key: "prom_queen", tier: Prismatic, name: ["舞会女王", "舞會女王", "Prom Queen"],
          desc: ["身边有敌方英雄时冲刺 4 秒：移动速度 +50%，碰到的敌方英雄被魅惑 1.25 秒（每人一次）。冷却 35 秒",
                 "身邊有敵方英雄時衝刺 4 秒：移動速度 +50%，碰到的敵方英雄被魅惑 1.25 秒（每人一次）。冷卻 35 秒",
                 "With an enemy champion near, sprint for 4 s at +50% move speed, charming each enemy champion you touch for 1.25 s. 35 s cooldown"],
          stats: &[],
          fit: w(0.0, 0.3, 0.0, 0.4, 0.5, 0.5, 0.3, 0.8, 0.6, 0.0), theme: T::Speed, ev: E::PromQueen },
    Aug { key: "squishy_slappy_grab", tier: Prismatic, name: ["软软抓抓", "軟軟抓抓", "Squishy Slappy Grab"],
          desc: ["每 16 秒牵住身边的敌方英雄（4 秒）；下一次普攻把他们全部拉过来，眩晕 0.75 秒，各造成 50～150（随等级）的魔法伤害，每拉一个获得 80 护盾",
                 "每 16 秒牽住身邊的敵方英雄（4 秒）；下一次普攻把他們全部拉過來，暈眩 0.75 秒，各造成 50～150（隨等級）的魔法傷害，每拉一個獲得 80 護盾",
                 "Every 16 s you tether enemy champions near (4 s); your next basic attack pulls them all in, stuns them 0.75 s for 50-150 (by level) magic each, and shields you 80 per champion"],
          stats: &[],
          fit: w(0.2, 0.3, 0.6, 0.2, 0.6, 0.6, 0.0, 0.4, 0.8, 0.0), theme: T::Tank, ev: E::Grab },
    Aug { key: "third_times_the_harm", tier: Prismatic, name: ["事不过三", "事不過三", "Third Times the Harm"],
          desc: ["每第 3 次普攻命中同一个英雄，额外造成其最大生命 6%（近战）/ 3%（远程）的真实伤害",
                 "每第 3 次普攻命中同一個英雄，額外造成其最大生命 6%（近戰）/ 3%（遠程）的真實傷害",
                 "Every 3rd basic attack on the same champion deals 6% (melee) / 3% (ranged) of their max HP as true damage"],
          stats: &[],
          fit: w(0.6, 0.0, 1.0, 0.0, 0.2, 0.6, 0.3, 0.0, 0.3, 0.2), theme: T::OnHit, ev: E::ThirdTime },
    Aug { key: "titans_resolve", tier: Prismatic, name: ["泰坦的坚决", "泰坦的堅決", "Titan's Resolve"],
          desc: ["造成或受到伤害时叠层（6 秒），叠满 7 层：攻击力和法强 +15%，护甲和魔抗 +20，韧性 +10%，体型变大",
                 "造成或受到傷害時疊層（6 秒），疊滿 7 層：攻擊力和法強 +15%，護甲和魔抗 +20，韌性 +10%，體型變大",
                 "Dealing or taking damage stacks (6 s); at 7 stacks: +15% AD and AP, +20 armor and MR, +10% tenacity, a bigger body"],
          stats: &[],
          fit: w(0.4, 0.3, 0.4, 0.2, 0.6, 1.0, 0.2, 0.0, 0.6, 0.0), theme: T::Tank, ev: E::TitansResolve },
    Aug { key: "ultimate_revolution", tier: Prismatic, name: ["终极革命", "終極革命", "Ultimate Revolution"],
          desc: ["放大招 1 秒后大招冷却立刻转好（75 秒一次）", "放大招 1 秒後大招冷卻立刻轉好（75 秒一次）",
                 "1 s after your ultimate, its cooldown resets (once per 75 s)"],
          stats: &[],
          fit: w(0.3, 0.5, 0.0, 0.8, 0.3, 0.4, 0.5, 0.4, 0.0, 0.0), theme: T::Haste, ev: E::UltRevolution },
    Aug { key: "fey_magic", tier: Prismatic, name: ["仙灵魔法", "仙靈魔法", "Fey Magic"],
          desc: ["大招打中的敌方英雄变成小动物 2 秒：不能普攻，移动速度 -40%（每人 15 秒一次）",
                 "大招打中的敵方英雄變成小動物 2 秒：不能普攻，移動速度 -40%（每人 15 秒一次）",
                 "Enemy champions your ultimate hits turn into critters for 2 s: no basic attacks, -40% move speed (15 s per champion)"],
          stats: &[],
          fit: w(0.2, 0.6, 0.0, 0.7, 0.2, 0.2, 0.2, 0.6, 0.0, 0.0), theme: T::Ap, ev: E::FeyMagic },
    Aug { key: "circle_of_death", tier: Prismatic, name: ["死亡之环", "死亡之環", "Circle of Death"],
          desc: ["你回复的生命的 70% 变成魔法伤害，打向最近的敌方英雄（每 0.5 秒结算一次）",
                 "你回復的生命的 70% 變成魔法傷害，打向最近的敵方英雄（每 0.5 秒結算一次）",
                 "70% of the health you regain becomes magic damage to the nearest enemy champion (settled every 0.5 s)"],
          stats: &[],
          fit: w(0.3, 0.3, 0.2, 0.2, 0.5, 0.8, 0.0, 0.4, 0.4, 0.0), theme: T::Sustain, ev: E::CircleOfDeath },
    Aug { key: "dual_wield", tier: Prismatic, name: ["双持", "雙持", "Dual Wield"],
          desc: ["攻击速度 +10%；普攻命中后 0.2 秒再射一发：40% 攻击力 的物理伤害", "攻擊速度 +10%；普攻命中後 0.2 秒再射一發：40% 攻擊力 的物理傷害",
                 "+10% attack speed; 0.2 s after each basic attack hit, a second bolt deals 40% AD physical"],
          stats: &[(AttackSpeedMult, 10)],
          fit: w(0.8, 0.0, 1.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.6), theme: T::OnHit, ev: E::DualWield },
    Aug { key: "earthwake", tier: Prismatic, name: ["地裂", "地裂", "Earthwake"],
          desc: ["冲刺、闪现留下一道裂痕，0.6 秒后爆开：沿途的敌方英雄受到 90～250（随等级）+ 80% 攻击力 + 40% 法强 的魔法伤害",
                 "衝刺、閃現留下一道裂痕，0.6 秒後爆開：沿途的敵方英雄受到 90～250（隨等級）+ 80% 攻擊力 + 40% 法強 的魔法傷害",
                 "Dashes and blinks leave a crack that bursts 0.6 s later: 90-250 (by level) + 80% AD + 40% AP magic to enemy champions along it"],
          stats: &[],
          fit: w(0.5, 0.4, 0.2, 0.4, 0.2, 0.6, 0.8, 0.0, 0.5, 0.0), theme: T::Hybrid, ev: E::Earthwake },
    // ---------------- 0.4.0：银，补给法师 ----------------
    Aug { key: "twin_fire", tier: Silver, name: ["双生火焰", "雙生火焰", "Twin Fire"],
          desc: ["暴击率 +25%。技能命中英雄时朝他射出 1 枚火焰，暴击率每 33% 多 1 枚（最多 4 枚），每枚 10～30（随等级）+ 7% 攻击力 + 7% 法强 的魔法伤害。冷却 5 秒",
                 "暴擊率 +25%。技能命中英雄時朝他射出 1 枚火焰，暴擊率每 33% 多 1 枚（最多 4 枚），每枚 10～30（隨等級）+ 7% 攻擊力 + 7% 法強 的魔法傷害。冷卻 5 秒",
                 "+25% crit chance. Skill hits on champions fire 1 flame at them, +1 per 33% crit chance (up to 4): 10-30 (by level) + 7% AD + 7% AP magic damage each. 5 s cooldown"],
          stats: &[(CritChance, 25)],
          fit: w(0.5, 0.6, 0.4, 0.8, 0.0, 0.0, 0.3, 0.2, 0.0, 0.3), theme: T::Crit, ev: E::TwinFire },
    // ---------------- 0.4.0 第二批：26.23 列表里还有的 ----------------
    Aug { key: "goredrink", tier: Silver, name: ["渴血", "渴血", "Goredrink"],
          desc: ["对敌方英雄造成伤害时，回复伤害的 15%（普攻和技能都算）",
                 "對敵方英雄造成傷害時，回復傷害的 15%（普攻和技能都算）",
                 "Damage to enemy champions heals you for 15% of it (attacks and skills alike)"],
          stats: &[],
          fit: w(0.5, 0.2, 0.4, 0.1, 0.2, 0.7, 0.4, 0.0, 0.3, 0.0), theme: T::Sustain, ev: E::Goredrink },
    Aug { key: "adapt", tier: Silver, name: ["物理转魔法", "物理轉魔法", "ADAPt"],
          desc: ["按比开局多出来的攻击力加法术强度（每 0.6 点加 1 点，攻击力不扣），另外法术强度 +15%",
                 "按比開局多出來的攻擊力加法術強度（每 0.6 點加 1 點，攻擊力不扣），另外法術強度 +15%",
                 "Gain ability power from the attack damage gained since the start (1 AP per 0.6 AD, no AD lost), plus +15% ability power"],
          stats: &[],
          fit: w(-0.4, 1.0, 0.0, 0.6, 0.0, 0.0, 0.2, 0.2, 0.0, 0.0), theme: T::Ap, ev: E::Adapt },
    Aug { key: "escapade", tier: Silver, name: ["魔法转物理", "魔法轉物理", "EscAPADe"],
          desc: ["按法术强度加攻击力（每 1.66 点加 1 点，法强不扣），另外攻击力 +15%",
                 "按法術強度加攻擊力（每 1.66 點加 1 點，法強不扣），另外攻擊力 +15%",
                 "Gain attack damage from ability power (1 AD per 1.66 AP, no AP lost), plus +15% attack damage"],
          stats: &[],
          fit: w(1.0, -0.4, 0.6, 0.0, 0.0, 0.4, 0.3, 0.0, 0.0, 0.0), theme: T::Ad, ev: E::Escapade },
    Aug { key: "slime_time", tier: Silver, name: ["史莱姆时间", "史萊姆時間", "Slime Time"],
          desc: ["身边有敌方英雄时每 6 秒炸开一圈黏液：40～80（随等级）+ 目标 3%～8%（随等级）最大生命 的魔法伤害，每 100 攻击力、每 100 法强再 +1.5%。每打中一个英雄留下一团黏液，走过去吃掉回复 6%～15%（随等级）最大生命，敌人踩到就没了",
                 "身邊有敵方英雄時每 6 秒炸開一圈黏液：40～80（隨等級）+ 目標 3%～8%（隨等級）最大生命 的魔法傷害，每 100 攻擊力、每 100 法強再 +1.5%。每打中一個英雄留下一團黏液，走過去吃掉回復 6%～15%（隨等級）最大生命，敵人踩到就沒了",
                 "Every 6 s near enemy champions, slime bursts for 40-80 (by level) + 3-8% (by level) of their max HP as magic damage (+1.5% per 100 AD and per 100 AP). Each hit drops a blob: eat it to heal 6-15% (by level) max HP; enemies crush it"],
          stats: &[],
          fit: w(0.2, 0.3, 0.0, 0.3, 0.8, 0.8, 0.0, 0.3, 0.7, -0.2), theme: T::Tank, ev: E::SlimeTime },
    Aug { key: "heavy_is_the_crown", tier: Gold, name: ["王冠之重", "王冠之重", "Heavy Is The Crown"],
          desc: ["攻击力 +17、法术强度 +50，攻击力、法强、攻速再 +10%，但战斗中移动速度 -5%。每参与击杀一名英雄叠一层：攻击力、法强、攻速再 +5%（最多 +50%），战斗中移动速度再 -2.5%；阵亡掉一半层数",
                 "攻擊力 +17、法術強度 +50，攻擊力、法強、攻速再 +10%，但戰鬥中移動速度 -5%。每參與擊殺一名英雄疊一層：攻擊力、法強、攻速再 +5%（最多 +50%），戰鬥中移動速度再 -2.5%；陣亡掉一半層數",
                 "+17 AD, +50 AP and +10% AD, AP and attack speed, but -5% move speed in combat. Each champion takedown stacks another +5% of each (up to +50%) and -2.5% move speed in combat; dying loses half the stacks"],
          stats: &[],
          fit: w(0.7, 0.7, 0.7, 0.4, -0.2, 0.3, 0.3, 0.0, 0.0, 0.2), theme: T::Hybrid, ev: E::HeavyCrown },
    Aug { key: "endless_decimation", tier: Gold, name: ["无尽收割", "無盡收割", "Endless Decimation"],
          desc: ["身边有敌方英雄时每 8 秒挥斧一圈（蓄力 1.25 秒）：外圈的敌方英雄受到 100～400（随等级）+ 60% 攻击力 + 40% 法强 的物理伤害，内圈的一半。外圈每打中一个英雄回复 18% 已损失生命，下一次冷却 -10%（最少 3 秒）",
                 "身邊有敵方英雄時每 8 秒揮斧一圈（蓄力 1.25 秒）：外圈的敵方英雄受到 100～400（隨等級）+ 60% 攻擊力 + 40% 法強 的物理傷害，內圈的一半。外圈每打中一個英雄回復 18% 已損失生命，下一次冷卻 -10%（最少 3 秒）",
                 "Every 8 s near enemy champions, spin an axe (1.25 s wind-up): 100-400 (by level) + 60% AD + 40% AP physical damage on the outer ring, half inside. Each outer-ring hit heals 18% missing HP and cuts the next cooldown by 10% (3 s at least)"],
          stats: &[],
          fit: w(0.7, 0.3, 0.2, 0.3, 0.6, 1.0, 0.2, 0.0, 0.8, -0.4), theme: T::Hybrid, ev: E::Decimation },
    Aug { key: "bees", tier: Gold, name: ["小蜜蜂！！！", "小蜜蜂！！！", "BEES!!!"],
          desc: ["技能命中英雄时朝他扔一个蜂巢（1.1 秒后落地）：落点周围的敌方英雄被蜂群缠住 2 秒，一共受到 75～140（随等级）+ 150% 攻击力 + 70% 法强 的魔法伤害（每 0.5 秒一下），移动速度 -20%。冷却 15～10 秒（随等级）",
                 "技能命中英雄時朝他扔一個蜂巢（1.1 秒後落地）：落點周圍的敵方英雄被蜂群纏住 2 秒，一共受到 75～140（隨等級）+ 150% 攻擊力 + 70% 法強 的魔法傷害（每 0.5 秒一下），移動速度 -20%。冷卻 15～10 秒（隨等級）",
                 "Skill hits on champions lob a beehive at them (lands in 1.1 s): enemy champions around it are swarmed for 2 s, taking 75-140 (by level) + 150% AD + 70% AP magic damage in all (every 0.5 s) and -20% move speed. 15-10 s cooldown (by level)"],
          stats: &[],
          fit: w(0.3, 0.8, 0.0, 1.0, 0.0, 0.2, 0.2, 0.3, 0.0, 0.2), theme: T::Ap, ev: E::Bees },
    Aug { key: "hellbent", tier: Prismatic, name: ["亡命之徒", "亡命之徒", "Hellbent"],
          desc: ["每打中一个敌方英雄叠一层（6 秒，最多 10 层）。叠满时挨了致命伤害不会死：倒下 4 秒（无敌）后以 35%～75% 最大生命起身，之后 15 秒攻击力 +25～200 或法强 +50～400（看哪个高）、移动速度 +20%～40%、生命偷取 +15%～30%（都随等级）。冷却 90 秒",
                 "每打中一個敵方英雄疊一層（6 秒，最多 10 層）。疊滿時挨了致命傷害不會死：倒下 4 秒（無敵）後以 35%～75% 最大生命起身，之後 15 秒攻擊力 +25～200 或法強 +50～400（看哪個高）、移動速度 +20%～40%、生命偷取 +15%～30%（都隨等級）。冷卻 90 秒",
                 "Champion hits stack (6 s, max 10). At full stacks lethal damage downs you for 4 s (invulnerable) instead: rise at 35-75% max HP, then 15 s of +25-200 AD or +50-400 AP, +20-40% move speed, +15-30% life steal (by level). 90 s cooldown"],
          stats: &[],
          fit: w(0.6, 0.4, 0.4, 0.2, 0.3, 1.0, 0.7, 0.0, 0.6, 0.0), theme: T::Guard, ev: E::Hellbent },
    // ---------------- 0.5.0：金币 / 随机 / 任务、龙魂、技能海克斯 ----------------
    Aug { key: "donation", tier: Gold, name: ["捐赠", "捐贈", "Donation"],
          desc: ["拿到时获得 1750 金币",
                 "拿到時獲得 1750 金幣",
                 "Gain 1750 gold on pick"],
          stats: &[],
          fit: w(0.4, 0.4, 0.3, 0.3, 0.3, 0.3, 0.3, 0.2, 0.2, 0.2), theme: T::Hybrid, ev: E::Donation },
    Aug { key: "goldrend", tier: Prismatic, name: ["夺金", "奪金", "Goldrend"],
          desc: ["对敌方英雄造成伤害时，额外 50～150（随等级）+ 40% 攻击力 + 20% 法强 的魔法伤害，再得 30 金币、1.5 秒移动速度 +25%（每个英雄 30 秒一次）",
                 "對敵方英雄造成傷害時，額外 50～150（隨等級）+ 40% 攻擊力 + 20% 法強 的魔法傷害，再得 30 金幣、1.5 秒移動速度 +25%（每個英雄 30 秒一次）",
                 "Damaging an enemy champion deals 50-150 (by level) + 40% AD + 20% AP bonus magic damage and grants 30 gold and +25% move speed for 1.5 s (each champion every 30 s)"],
          stats: &[],
          fit: w(0.6, 0.6, 0.5, 0.5, 0.0, 0.4, 0.5, 0.0, 0.0, 0.2), theme: T::OnHit, ev: E::Goldrend },
    Aug { key: "stats", tier: Silver, name: ["属性！", "屬性！", "Stats!"],
          desc: ["获得 2 个属性铁砧：每个从 3 项随机属性里挑最合适的一项（多是银色铁砧）",
                 "獲得 2 個屬性鐵砧：每個從 3 項隨機屬性裡挑最合適的一項（多是銀色鐵砧）",
                 "Gain 2 stat anvils: each offers 3 random stats and takes the best fit (mostly Silver anvils)"],
          stats: &[],
          fit: w(0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3), theme: T::Hybrid, ev: E::Stats1 },
    Aug { key: "stats_on_stats", tier: Gold, name: ["属性叠属性！", "屬性疊屬性！", "Stats on Stats!"],
          desc: ["获得 3 个属性铁砧：每个从 3 项随机属性里挑最合适的一项（金色、棱彩铁砧的机会更大）",
                 "獲得 3 個屬性鐵砧：每個從 3 項隨機屬性裡挑最合適的一項（金色、稜彩鐵砧的機會更大）",
                 "Gain 3 stat anvils: each offers 3 random stats and takes the best fit (better odds of Gold and Prismatic anvils)"],
          stats: &[],
          fit: w(0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3), theme: T::Hybrid, ev: E::Stats2 },
    Aug { key: "stats_on_stats_on_stats", tier: Prismatic, name: ["属性叠属性叠属性！", "屬性疊屬性疊屬性！", "Stats on Stats on Stats!"],
          desc: ["获得 4 个属性铁砧：每个从 3 项随机属性里挑最合适的一项（金色、棱彩铁砧的机会更大）",
                 "獲得 4 個屬性鐵砧：每個從 3 項隨機屬性裡挑最合適的一項（金色、稜彩鐵砧的機會更大）",
                 "Gain 4 stat anvils: each offers 3 random stats and takes the best fit (better odds of Gold and Prismatic anvils)"],
          stats: &[],
          fit: w(0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3), theme: T::Hybrid, ev: E::Stats3 },
    Aug { key: "transmute_chaos", tier: Prismatic, name: ["质变：混沌", "質變：混沌", "Transmute: Chaos"],
          desc: ["随机获得 2 个海克斯（哪一档都可能，不会是这一次的另外两张）",
                 "隨機獲得 2 個海克斯（哪一檔都可能，不會是這一次的另外兩張）",
                 "Gain 2 random augments of any tier (never the other two cards of this pick)"],
          stats: &[],
          fit: w(0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3), theme: T::Hybrid, ev: E::TransmuteChaos },
    Aug { key: "transmute_prismatic", tier: Gold, name: ["质变：棱彩阶", "質變：稜彩階", "Transmute: Prismatic"],
          desc: ["随机获得 1 个棱彩海克斯",
                 "隨機獲得 1 個稜彩海克斯",
                 "Gain 1 random Prismatic augment"],
          stats: &[],
          fit: w(0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3), theme: T::Hybrid, ev: E::TransmutePrismatic },
    Aug { key: "pandoras_box", tier: Prismatic, name: ["潘朵拉的盒子", "潘朵拉的盒子", "Pandora's Box"],
          desc: ["随机获得 1 个棱彩海克斯；之前拿到的海克斯也各换成一个随机的棱彩海克斯",
                 "隨機獲得 1 個稜彩海克斯；之前拿到的海克斯也各換成一個隨機的稜彩海克斯",
                 "Gain 1 random Prismatic augment; each augment you already have turns into a random Prismatic one"],
          stats: &[],
          fit: w(0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25), theme: T::Hybrid, ev: E::Pandora },
    Aug { key: "from_downtown", tier: Gold, name: ["超远狙击", "超遠狙擊", "From Downtown"],
          desc: ["任务：技能在 60000 以外命中英雄 15 次。之后这样的命中召来流星：75～200（随等级）+ 50% 攻击力 + 20% 法强 的魔法伤害，越远伤害越高、范围越大（同一个人 8 秒一次）",
                 "任務：技能在 60000 以外命中英雄 15 次。之後這樣的命中召來流星：75～200（隨等級）+ 50% 攻擊力 + 20% 法強 的魔法傷害，越遠傷害越高、范圍越大（同一個人 8 秒一次）",
                 "Quest: hit champions with abilities from beyond 60000 15 times. Then such hits call a meteor: 75-200 (by level) + 50% AD + 20% AP magic damage, more and wider the farther (each champion every 8 s)"],
          stats: &[],
          fit: w(0.4, 0.6, 0.0, 0.8, 0.0, 0.0, 0.0, 0.2, -0.5, 1.0), theme: T::Ap, ev: E::FromDowntown },
    Aug { key: "pressure_cooker", tier: Gold, name: ["高压锻炉", "高壓鍛爐", "Pressure Cooker"],
          desc: ["身边 30000 以内的敌方英雄每秒受到你最大生命 0.5% 的魔法伤害。任务：烧够 1500 伤害范围到 50000，13500 每秒伤害翻倍，28500 范围到 60000",
                 "身邊 30000 以內的敵方英雄每秒受到你最大生命 0.5% 的魔法傷害。任務：燒夠 1500 傷害范圍到 50000，13500 每秒傷害翻倍，28500 范圍到 60000",
                 "Enemy champions within 30000 take 0.5% of your max HP as magic damage each second. Quests: 1500 burned widens it to 50000, 13500 doubles the rate, 28500 widens it to 60000"],
          stats: &[],
          fit: w(0.0, 0.2, 0.0, 0.0, 1.0, 0.7, 0.0, 0.2, 0.7, -0.3), theme: T::Tank, ev: E::PressureCooker },
    Aug { key: "infernal_soul", tier: Silver, name: ["炼狱龙魂", "煉獄龍魂", "Infernal Soul"],
          desc: ["获得炼狱龙魂（已经有了就换一种）：每 3 秒，对敌方英雄的下一次伤害在他身上爆炸，100 + 25% 攻击力 + 15% 法强 的魔法伤害，波及他身边的敌方英雄",
                 "獲得煉獄龍魂（已經有了就換一種）：每 3 秒，對敵方英雄的下一次傷害在他身上爆炸，100 + 25% 攻擊力 + 15% 法強 的魔法傷害，波及他身邊的敵方英雄",
                 "Gain the Infernal Soul (another one if you have it): every 3 s your next damage to an enemy champion explodes on him for 100 + 25% AD + 15% AP magic damage to enemies around him"],
          stats: &[],
          fit: w(0.6, 0.6, 0.4, 0.4, 0.0, 0.3, 0.3, 0.0, 0.0, 0.2), theme: T::OnHit, ev: E::InfernalSoul },
    Aug { key: "hextech_soul", tier: Silver, name: ["海克斯科技龙魂", "海克斯科技龍魂", "Hextech Soul"],
          desc: ["获得海克斯科技龙魂（已经有了就换一种）：每 2.5 秒，下一次命中放出连锁闪电，打他和身边另外 2 个敌方英雄：40 + 30% 攻击力 + 20% 法强 的魔法伤害，减速 90%（0.25 秒）",
                 "獲得海克斯科技龍魂（已經有了就換一種）：每 2.5 秒，下一次命中放出連鎖閃電，打他和身邊另外 2 個敵方英雄：40 + 30% 攻擊力 + 20% 法強 的魔法傷害，減速 90%（0.25 秒）",
                 "Gain the Hextech Soul (another one if you have it): every 2.5 s your next hit chains lightning to him and 2 more enemy champions nearby: 40 + 30% AD + 20% AP magic damage and a 90% slow (0.25 s)"],
          stats: &[],
          fit: w(0.5, 0.5, 0.6, 0.3, 0.0, 0.2, 0.2, 0.2, 0.0, 0.3), theme: T::OnHit, ev: E::HextechSoul },
    Aug { key: "mountain_soul", tier: Silver, name: ["山脉龙魂", "山脈龍魂", "Mountain Soul"],
          desc: ["获得山脉龙魂（已经有了就换一种）：5 秒没受到伤害时，获得 200 + 15% 攻击力 + 10% 法强 + 8% 最大生命 的护盾",
                 "獲得山脈龍魂（已經有了就換一種）：5 秒沒受到傷害時，獲得 200 + 15% 攻擊力 + 10% 法強 + 8% 最大生命 的護盾",
                 "Gain the Mountain Soul (another one if you have it): after 5 s without taking damage, gain a 200 + 15% AD + 10% AP + 8% max HP shield"],
          stats: &[],
          fit: w(0.2, 0.2, 0.0, 0.0, 0.8, 0.6, 0.2, 0.4, 0.4, 0.0), theme: T::Guard, ev: E::MountainSoul },
    Aug { key: "ocean_soul", tier: Silver, name: ["海洋龙魂", "海洋龍魂", "Ocean Soul"],
          desc: ["获得海洋龙魂（已经有了就换一种）：对敌方英雄造成伤害后，4 秒内回复 100 + 30% 攻击力 + 20% 法强 + 8% 最大生命（冷却 4 秒）",
                 "獲得海洋龍魂（已經有了就換一種）：對敵方英雄造成傷害後，4 秒內回復 100 + 30% 攻擊力 + 20% 法強 + 8% 最大生命（冷卻 4 秒）",
                 "Gain the Ocean Soul (another one if you have it): damaging an enemy champion heals you 100 + 30% AD + 20% AP + 8% max HP over 4 s (4 s cooldown)"],
          stats: &[],
          fit: w(0.4, 0.4, 0.3, 0.3, 0.4, 0.6, 0.2, 0.2, 0.3, 0.0), theme: T::Sustain, ev: E::OceanSoul },
    Aug { key: "omni_soul", tier: Prismatic, name: ["全能龙魂", "全能龍魂", "Omni Soul"],
          desc: ["随机获得 3 种龙魂（炼狱、山脉、海洋、云端、海克斯科技、化学科技里挑，已经有的不重复）",
                 "隨機獲得 3 種龍魂（煉獄、山脈、海洋、雲端、海克斯科技、化學科技裡挑，已經有的不重複）",
                 "Gain 3 random Dragon Souls (Infernal, Mountain, Ocean, Cloud, Hextech or Chemtech; none you already have)"],
          stats: &[],
          fit: w(0.5, 0.5, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3), theme: T::Hybrid, ev: E::OmniSoul },
    Aug { key: "hand_of_baron", tier: Prismatic, name: ["男爵之手", "男爵之手", "Hand of Baron"],
          desc: ["攻击力或法术强度 +25%（哪个高给哪个）；身边的己方小兵受到的伤害 -40%、攻击力 +30%",
                 "攻擊力或法術強度 +25%（哪個高給哪個）；身邊的己方小兵受到的傷害 -40%、攻擊力 +30%",
                 "+25% attack damage or ability power (whichever is higher); allied minions near you take 40% less damage and gain 30% attack damage"],
          stats: &[],
          fit: w(0.6, 0.6, 0.4, 0.4, 0.2, 0.4, 0.3, 0.2, 0.2, 0.2), theme: T::Hybrid, ev: E::HandOfBaron },
    Aug { key: "adaptive_ward", tier: Silver, name: ["自适应防护", "自適應防護", "Adaptive Ward"],
          desc: ["选定的技能命中英雄时，护甲和魔抗里低的那项 +7～12（随等级，6 秒，冷却 4 秒，能叠）",
                 "選定的技能命中英雄時，護甲和魔抗裡低的那項 +7～12（隨等級，6 秒，冷卻 4 秒，能疊）",
                 "Your chosen ability hitting a champion gives +7-12 (by level) to the lower of your armor and magic resist for 6 s (4 s cooldown, stacks)"],
          stats: &[],
          fit: w(0.0, 0.2, 0.0, 0.5, 0.6, 0.6, 0.2, 0.3, 0.4, 0.0), theme: T::Tank, ev: E::AdaptiveWard },
    Aug { key: "crimson_cobalt", tier: Gold, name: ["深红钴蓝闪光", "深紅鈷藍閃光", "CRIMSON COBALT"],
          desc: ["选定的技能打中的英雄被标记 4 秒；普攻打到被标记的人额外造成 100～250（随等级）+ 70% 攻击力 + 35% 法强 的魔法伤害，这个技能的冷却减少总冷却的 65%",
                 "選定的技能打中的英雄被標記 4 秒；普攻打到被標記的人額外造成 100～250（隨等級）+ 70% 攻擊力 + 35% 法強 的魔法傷害，這個技能的冷卻減少總冷卻的 65%",
                 "Your chosen ability marks the champions it damages for 4 s; a basic attack on a marked one deals 100-250 (by level) + 70% AD + 35% AP bonus magic damage and cuts that ability's cooldown by 65% of its total"],
          stats: &[],
          fit: w(0.6, 0.5, 0.8, 0.6, 0.0, 0.4, 0.4, 0.0, 0.0, 0.2), theme: T::OnHit, ev: E::CrimsonCobalt },
    Aug { key: "flow_of_spirit", tier: Gold, name: ["灵魂乐流", "靈魂樂流", "Flow of Spirit"],
          desc: ["放选定的技能后 4 秒内攻击速度 +60%～120%（随等级）",
                 "放選定的技能後 4 秒內攻擊速度 +60%～120%（隨等級）",
                 "Casting your chosen ability gives +60-120% (by level) attack speed for 4 s"],
          stats: &[],
          fit: w(0.6, 0.2, 1.0, 0.4, 0.0, 0.3, 0.2, 0.0, 0.0, 0.2), theme: T::Speed, ev: E::FlowOfSpirit },
    Aug { key: "mercys_strike", tier: Gold, name: ["仁慈打击", "仁慈打擊", "Mercy's Strike"],
          desc: ["放选定的技能后的下一次普攻：射程 +30000、攻击速度 +75%，额外造成目标 3% 最大生命 的魔法伤害",
                 "放選定的技能後的下一次普攻：射程 +30000、攻擊速度 +75%，額外造成目標 3% 最大生命 的魔法傷害",
                 "After casting your chosen ability, your next basic attack has +30000 range and +75% attack speed and deals 3% of the target's max HP as bonus magic damage"],
          stats: &[],
          fit: w(0.6, 0.3, 1.0, 0.3, 0.0, 0.3, 0.3, 0.0, 0.2, 0.2), theme: T::OnHit, ev: E::MercysStrike },
    Aug { key: "overloaded", tier: Prismatic, name: ["过载", "過載", "Overloaded"],
          desc: ["放别的技能时，选定技能的冷却立刻转好",
                 "放別的技能時，選定技能的冷卻立刻轉好",
                 "Casting a different ability resets your chosen ability's cooldown"],
          stats: &[],
          fit: w(0.2, 0.6, 0.0, 1.0, 0.0, 0.2, 0.3, 0.3, 0.0, 0.0), theme: T::Haste, ev: E::Overloaded },
    Aug { key: "ravenous_bind", tier: Gold, name: ["嗜血束缚", "嗜血束縛", "Ravenous Bind"],
          desc: ["技能控住敌方英雄时：对他 15～90（随等级）+ 10% 法强 + 0.5% 最大生命 的魔法伤害，回复 75～300（随等级）+ 5% 法强 + 12% 额外生命，技能冷却越长越多（最多 +50%；冷却 5 秒）",
                 "技能控住敵方英雄時：對他 15～90（隨等級）+ 10% 法強 + 0.5% 最大生命 的魔法傷害，回復 75～300（隨等級）+ 5% 法強 + 12% 額外生命，技能冷卻越長越多（最多 +50%；冷卻 5 秒）",
                 "Immobilizing an enemy champion with an ability deals 15-90 (by level) + 10% AP + 0.5% max HP magic damage and heals you 75-300 (by level) + 5% AP + 12% bonus HP, up to +50% for long cooldowns (5 s cooldown)"],
          stats: &[],
          fit: w(0.0, 0.3, 0.0, 0.4, 0.7, 0.5, 0.0, 0.5, 0.3, 0.0).with_cc(1.0), theme: T::Sustain, ev: E::RavenousBind },
    Aug { key: "rejuvenation", tier: Gold, name: ["复苏", "復甦", "Rejuvenation"],
          desc: ["放选定的技能时回复 30～100（随等级）+ 25% 攻击力 + 15% 法强 + 5% 最大生命，技能冷却越长越多（最多 +50%）",
                 "放選定的技能時回復 30～100（隨等級）+ 25% 攻擊力 + 15% 法強 + 5% 最大生命，技能冷卻越長越多（最多 +50%）",
                 "Casting your chosen ability heals 30-100 (by level) + 25% AD + 15% AP + 5% max HP, up to +50% for long cooldowns"],
          stats: &[],
          fit: w(0.3, 0.3, 0.0, 0.6, 0.5, 0.6, 0.2, 0.3, 0.3, 0.0), theme: T::Sustain, ev: E::Rejuvenation },
    Aug { key: "siphon", tier: Silver, name: ["虹吸", "虹吸", "Siphon"],
          desc: ["选定的技能对英雄造成伤害时，回复伤害的 30%",
                 "選定的技能對英雄造成傷害時，回復傷害的 30%",
                 "Your chosen ability heals you for 30% of the damage it deals to champions"],
          stats: &[],
          fit: w(0.3, 0.5, 0.0, 0.8, 0.2, 0.6, 0.3, 0.0, 0.2, 0.0), theme: T::Sustain, ev: E::Siphon },
    Aug { key: "stay_resolute", tier: Silver, name: ["坚定意志", "堅定意志", "Stay Resolute"],
          desc: ["选定的技能每打中一个英雄，护甲或魔抗永久 +2～3（随等级，轮流加；同一个人 5 秒一次）；不是第 1 个海克斯时再给护甲和魔抗各 +20",
                 "選定的技能每打中一個英雄，護甲或魔抗永久 +2～3（隨等級，輪流加；同一個人 5 秒一次）；不是第 1 個海克斯時再給護甲和魔抗各 +20",
                 "Each champion your chosen ability hits gives +2-3 (by level) armor or magic resist for good (in turn; each champion every 5 s); +20 armor and magic resist if it is not your 1st augment"],
          stats: &[],
          fit: w(0.0, 0.2, 0.0, 0.5, 0.8, 0.7, 0.0, 0.3, 0.5, 0.0), theme: T::Tank, ev: E::StayResolute },
    Aug { key: "terror", tier: Silver, name: ["恐惧", "恐懼", "Terror"],
          desc: ["放选定的技能时，身边的敌方英雄恐惧 1.75 秒（冷却 30 秒）",
                 "放選定的技能時，身邊的敵方英雄恐懼 1.75 秒（冷卻 30 秒）",
                 "Casting your chosen ability fears enemy champions around you for 1.75 s (30 s cooldown)"],
          stats: &[],
          fit: w(0.2, 0.3, 0.0, 0.5, 0.6, 0.6, 0.4, 0.5, 0.6, 0.0), theme: T::Guard, ev: E::Terror },
    Aug { key: "trusty_weapon", tier: Silver, name: ["可靠武器", "可靠武器", "Trusty Weapon"],
          desc: ["选定的技能每打中一次英雄叠一层（6 秒，不封顶），每层伤害 +5%",
                 "選定的技能每打中一次英雄疊一層（6 秒，不封頂），每層傷害 +5%",
                 "Each champion hit by your chosen ability adds a stack (6 s, no cap): +5% damage each"],
          stats: &[],
          fit: w(0.5, 0.6, 0.2, 0.8, 0.0, 0.3, 0.3, 0.0, 0.0, 0.0), theme: T::Hybrid, ev: E::TrustyWeapon },
    Aug { key: "bread_and_butter", tier: Gold, name: ["面包和黄油", "麵包和黃油", "Bread And Butter"],
          desc: ["技能（第一个小技能）的技能急速 +100：冷却减半",
                 "技能（第一個小技能）的技能急速 +100：冷卻減半",
                 "+100 ability haste on your first ability: half its cooldown"],
          stats: &[],
          fit: w(0.2, 0.5, 0.0, 1.0, 0.2, 0.3, 0.3, 0.4, 0.0, 0.0), theme: T::Haste, ev: E::BreadButter },
    Aug { key: "bread_and_jam", tier: Gold, name: ["面包和果酱", "麵包和果醬", "Bread And Jam"],
          desc: ["技能 2 的技能急速 +100：冷却减半",
                 "技能 2 的技能急速 +100：冷卻減半",
                 "+100 ability haste on your second ability: half its cooldown"],
          stats: &[],
          fit: w(0.2, 0.5, 0.0, 1.0, 0.2, 0.3, 0.3, 0.4, 0.0, 0.0), theme: T::Haste, ev: E::BreadJam },
    Aug { key: "pursuit_of_haste", tier: Gold, name: ["急速追加", "急速追加", "Pursuit of Haste"],
          desc: ["任务：选定的技能命中英雄 10 次，它的技能急速 +80；再命中 20 次（一共 30 次）变成 +160",
                 "任務：選定的技能命中英雄 10 次，它的技能急速 +80；再命中 20 次（一共 30 次）變成 +160",
                 "Quest: hit champions 10 times with your chosen ability for +80 ability haste on it; 20 more (30 in all) for +160"],
          stats: &[],
          fit: w(0.2, 0.5, 0.0, 1.0, 0.1, 0.3, 0.3, 0.3, 0.0, 0.0), theme: T::Haste, ev: E::PursuitHaste },
    Aug { key: "pursuit_of_power", tier: Gold, name: ["力量追寻", "力量追尋", "Pursuit of Power"],
          desc: ["任务：选定的技能命中英雄 10 次，之后它的伤害 +30%",
                 "任務：選定的技能命中英雄 10 次，之後它的傷害 +30%",
                 "Quest: hit champions 10 times with your chosen ability; it then deals 30% more damage"],
          stats: &[],
          fit: w(0.4, 0.7, 0.0, 1.0, 0.0, 0.2, 0.3, 0.0, 0.0, 0.1), theme: T::Ap, ev: E::PursuitPower },
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

/// 拿到这个海克斯时挂的永久 buff（触发类的多半没有属性：只是个记号，复活后补、状态丢了从它读回来）。远程英雄的射程。
pub fn buff(i: usize) -> BuffV1 {
    buff_for(i, false)
}

/// 同上，`melee` 是近战英雄（射程类给近战的那个数）。
pub fn buff_for(i: usize, melee: bool) -> BuffV1 {
    let mut b = BuffV1::named(&buff_name(i));
    for &(f, v) in AUGS[i].stats {
        match f {
            Range if melee => {}
            MeleeRange if !melee => {}
            _ => set(&mut b, f, v),
        }
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
        MagicPower => b.magic_power += v,
        Range | MeleeRange => b.range += u,
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
            // range augments have both numbers, melee's the larger
            let r = |f: Field| a.stats.iter().find(|s| s.0 == f).map(|s| s.1);
            assert_eq!(r(Range).is_some(), r(MeleeRange).is_some(), "{}", a.key);
            if let (Some(ranged), Some(melee)) = (r(Range), r(MeleeRange)) {
                assert!(melee > ranged, "{}", a.key);
                assert_eq!((buff_for(i, false).range, buff_for(i, true).range), (ranged as usize, melee as usize));
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
        assert_eq!((pool(Silver).len(), pool(Gold).len(), pool(Prismatic).len()), (45, 54, 41));
    }

    /// Every triggered effect belongs to exactly one augment; the old augments keep their numbers (the saved picks and
    /// the logs name them by key, the screens by number).
    #[test]
    fn every_effect_has_one_augment() {
        for e in 1..EV_N {
            let n = AUGS.iter().filter(|a| a.ev as usize == e).count();
            assert_eq!(n, 1, "effect #{e}");
        }
        assert_eq!(AUGS.iter().filter(|a| a.ev == Ev::Stat).count(), 16 + 8, "0.1.0's sixteen left + 0.4.0's eight");
        let old = ["blunt_force", "glass_cannon", "arcane_surge", "slayer", "ultimate_awakening", "firebrand", "magic_missile",
                   "chain_lightning", "phenomenal_evil", "goliath", "sacred_ward"];
        let at = [0, 9, 14, 15, 19, 20, 27, 28, 36, 37, 46];
        for (k, i) in old.iter().zip(at) {
            assert_eq!(by_key(k), Some(i), "{k} keeps its number");
        }
        assert_eq!(of_ev(Ev::Goliath).map(|i| AUGS[i].key), Some("goliath"));
        assert_eq!(of_ev(Ev::Earthwake).map(|i| AUGS[i].key), Some("earthwake"));
        assert_eq!(of_ev(Ev::Stat), None);
        const { assert!(EV_N <= 128, "an effect set is a u128") };
    }

    #[test]
    fn the_numbers_reach_the_buff() {
        let gc = by_key("glass_cannon").unwrap();
        assert_eq!(buff(gc).hp_mult, -30);
        let gs = by_key("giant_slayer").unwrap();
        assert_eq!(buff(gs).move_speed_mult, 15);
        let ua = by_key("ultimate_awakening").unwrap();
        assert_eq!(buff(ua).ult_cooldown_mult, 30);
        let go = by_key("goliath").unwrap();
        assert_eq!((buff(go).hp_mult, buff(go).attack_mult), (30, 15));
        let lb = by_key("lich_brain").unwrap();
        assert_eq!(buff(lb).magic_power, 40);
        let sw = by_key("scoped_weapons").unwrap();
        assert_eq!((buff_for(sw, false).range, buff_for(sw, true).range), (5_000, 12_000));
    }
}
