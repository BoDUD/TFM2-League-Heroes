//! 0.5.0 的海克斯（用户 2026-11-26：「接着做」）：英雄联盟 26.23 海克斯大乱斗里剩下三类本游戏能做的——金币 / 随机 / 任务、
//! 龙魂和男爵（效果照大小龙 mod 的龙魂在这里做一份，不装大小龙也能用；英雄身上已经有大小龙给的同一种龙魂时这一种不再算）、
//! 技能海克斯（作用在选定的那个技能上：玩家在 BP 面板里选，AI 默认技能，过载默认技能 2，见 [`crate::augments::ai_slot`]）。
//! 质变、潘朵拉的盒子在选的那一刻换海克斯，在 lib.rs 的 `picks_due` 里；这里是比赛里的效果。
//!
//! 和英雄联盟不一样的地方：读不到「额外生命」，嗜血束缚按比第一次看到他时多出来的最大生命算；「伤害 +x%」用攻击力和法强 +x%
//! （可靠武器）或者按这一下实际打出的伤害补一份真实伤害（力量追寻）；某个技能的技能急速用放完以后再缩短它的冷却来做。

use super::b2::{named, slot, timed, RESET};
use super::*;
use crate::augments::{ai_slot, Traits};
use crate::rules::{splitmix, Rng};

// ===================== 数值（说明照这些写） =====================

pub const DONATION_GOLD: i64 = 1_750;

/// 夺金：每个英雄 30 秒一次。
pub const GOLDREND_GOLD: i64 = 30;
pub const GOLDREND_GAP: usize = 1_800;
pub const GOLDREND_MS: i32 = 25;
pub const GOLDREND_MS_T: usize = 90;
pub fn goldrend_damage(level: usize, ad: usize, ap: usize) -> usize {
    by_level(50, 150, level) + ad * 40 / 100 + ap * 20 / 100
}

/// 属性铁砧：三个海克斯各给几个、银 / 金 / 棱彩铁砧的机会（%）。
pub const ANVILS: [(Ev, usize, [u32; 3]); 3] =
    [(Ev::Stats1, 2, [70, 25, 5]), (Ev::Stats2, 3, [40, 45, 15]), (Ev::Stats3, 4, [30, 45, 25])];
pub const S_ANVIL: [&str; 3] = ["league_hextech_s:anvil_1", "league_hextech_s:anvil_2", "league_hextech_s:anvil_3"];

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stat {
    Attack,
    MagicPower,
    Hp,
    AttackSpeed,
    Defence,
    MagicResistance,
    Haste,
    Crit,
    MoveSpeed,
}

/// 每种属性在银 / 金 / 棱彩铁砧上给多少（攻速、暴击、移速是 %，急速是技能和大招的冷却字段）：银铁砧大约半个银档海克斯。
pub const ANVIL_STATS: [(Stat, [i32; 3]); 9] = [
    (Stat::Attack, [18, 29, 43]),
    (Stat::MagicPower, [36, 58, 86]),
    (Stat::Hp, [175, 280, 420]),
    (Stat::AttackSpeed, [15, 24, 36]),
    (Stat::Defence, [20, 32, 48]),
    (Stat::MagicResistance, [20, 32, 48]),
    (Stat::Haste, [8, 13, 19]),
    (Stat::Crit, [12, 19, 29]),
    (Stat::MoveSpeed, [5, 8, 12]),
];
const ANVIL_SALT: u64 = 0x616e_7669_6c73_0005;

/// 超远狙击：这么远（以外）的技能命中算数，15 次完成；流星 0.5 秒后落下，同一个人 8 秒一次；再远 40000 伤害 +50%、半径到 25000。
pub const DOWNTOWN_FAR: u64 = 60_000;
pub const DOWNTOWN_QUEST: u32 = 15;
pub const DOWNTOWN_GAP: usize = 480;
pub const DOWNTOWN_HIT_GAP: usize = 20;
pub const METEOR_T: usize = 30;
pub const METEOR_R: u64 = 15_000;
pub const DOWNTOWN_MORE: u64 = 40_000;
pub fn downtown_damage(level: usize, ad: usize, ap: usize, dist: u64) -> usize {
    let extra = dist.saturating_sub(DOWNTOWN_FAR).min(DOWNTOWN_MORE);
    (by_level(75, 200, level) + ad * 50 / 100 + ap * 20 / 100) * (80_000 + extra as usize) / 80_000
}
pub fn meteor_r(dist: u64) -> u64 {
    METEOR_R + dist.saturating_sub(DOWNTOWN_FAR).min(DOWNTOWN_MORE) / 4
}

/// 高压锻炉：每秒你最大生命的千分之 5；烧够这么多以后范围、伤害变。
pub const COOKER_EVERY: usize = 60;
pub const COOKER_PERMILLE: usize = 5;
pub const COOKER_STEPS: [(usize, u64, usize); 4] = [(0, 30_000, 1), (1_500, 50_000, 1), (13_500, 50_000, 2), (28_500, 60_000, 2)];
pub fn cooker(burned: usize) -> (u64, usize) {
    let s = COOKER_STEPS.iter().rev().find(|s| burned >= s.0).unwrap_or(&COOKER_STEPS[0]);
    (s.1, s.2)
}

// 龙魂（大小龙 mod 的数，海洋龙魂照英雄联盟的海克斯改成 100 起）
pub const INFERNAL_CD: usize = 180;
pub const INFERNAL_R: u64 = 25_000;
pub fn infernal_damage(ad: usize, ap: usize) -> usize {
    100 + ad * 25 / 100 + ap * 15 / 100
}
pub const HEXSOUL_CD: usize = 150;
pub const HEXSOUL_R: u64 = 40_000;
pub const HEXSOUL_TARGETS: usize = 3;
pub const HEXSOUL_SLOW: i32 = 90;
pub const HEXSOUL_SLOW_T: usize = 15;
pub fn hexsoul_damage(ad: usize, ap: usize) -> usize {
    40 + ad * 30 / 100 + ap * 20 / 100
}
pub const OCEAN_CD: usize = 240;
pub const OCEAN_PULSES: u8 = 8;
pub fn ocean_heal(ad: usize, ap: usize, max: usize) -> usize {
    100 + ad * 30 / 100 + ap * 20 / 100 + max * 8 / 100
}
pub const MOUNTAIN_IDLE: usize = 300;
pub const MOUNTAIN_T: usize = 3_600;
pub const MOUNTAIN_CHECK: usize = 30;
pub fn mountain_shield(ad: usize, ap: usize, max: usize) -> usize {
    200 + ad * 15 / 100 + ap * 10 / 100 + max * 8 / 100
}
pub const CLOUD_MS: i32 = 15;
pub const CLOUD_ULT_MS: i32 = 50;
pub const CLOUD_ULT_T: usize = 360;
pub const CHEM_PCT: usize = 50;
const SOUL_SALT: u64 = 0x736f_756c_7300_0005;

/// 男爵之手：攻击力或法强 +25%；身边的己方小兵（和大小龙 mod 同一个 buff 名，两边一起挂也只有一份）。
pub const BARON_PCT: i32 = 25;
pub const MINION_BOOST: &str = "league_dragons_baron_minion";
pub const MINION_R: u64 = 140_000;
pub const MINION_REDUCE: usize = 40;
pub const MINION_ATTACK: i32 = 30;
pub const MINION_EVERY: usize = 30;
pub const MINION_T: usize = 45;

// 技能海克斯
pub const WARD_CD: usize = 240;
pub const WARD_T: usize = 360;
pub const WARD_MOST: usize = 5;
pub const COBALT_T: usize = 240;
pub const COBALT_CUT_PCT: usize = 65;
pub fn cobalt_damage(level: usize, ad: usize, ap: usize) -> usize {
    by_level(100, 250, level) + ad * 70 / 100 + ap * 35 / 100
}
pub const FLOW_T: usize = 240;
pub const MERCY_T: usize = 300;
pub const MERCY_RANGE: usize = 30_000;
pub const MERCY_AS: i32 = 75;
pub const MERCY_PERMILLE: usize = 30;
pub const BIND_CD: usize = 300;
/// 冷却这么长（tick）以上的技能，嗜血束缚、复苏多 50%（短的按比例）。
pub const LONG_CD: usize = 1_200;
pub fn by_cooldown(amount: usize, full: usize) -> usize {
    amount * (200 + full.min(LONG_CD) * 100 / LONG_CD) / 200
}
pub fn bind_damage(level: usize, ap: usize, max: usize) -> usize {
    by_level(15, 90, level) + ap * 10 / 100 + max * 5 / 1000
}
pub fn bind_heal(level: usize, ap: usize, bonus_hp: usize) -> usize {
    by_level(75, 300, level) + ap * 5 / 100 + bonus_hp * 12 / 100
}
pub fn rejuv_heal(level: usize, ad: usize, ap: usize, max: usize) -> usize {
    by_level(30, 100, level) + ad * 25 / 100 + ap * 15 / 100 + max * 5 / 100
}
pub const SIPHON_PCT: u64 = 30;
pub const RESOLUTE_GAP: usize = 300;
pub const RESOLUTE_BONUS: i32 = 20;
pub const TERROR_CD: usize = 1_800;
pub const TERROR_R: u64 = 45_000;
pub const TERROR_T: u64 = 105;
pub const TRUSTY_T: usize = 360;
pub const TRUSTY_PCT: i32 = 5;
pub const TRUSTY_MOST: usize = 60;
/// 面包：技能急速 +100；急速追加：10 次 +80、30 次 +160。
pub const BREAD_HASTE: usize = 100;
pub const PURSUIT_FIRST: u32 = 10;
pub const PURSUIT_ALL: u32 = 30;
pub const PURSUIT_HIT_GAP: usize = 20;
pub fn pursuit_haste(hits: u32) -> usize {
    if hits >= PURSUIT_ALL {
        160
    } else if hits >= PURSUIT_FIRST {
        80
    } else {
        0
    }
}
pub const POWER_PCT: u64 = 30;
/// 技能急速 `haste`：放完以后冷却还要缩短多少（冷却 × 100 / (100 + 急速)）。
pub fn haste_cut(full: usize, haste: usize) -> usize {
    full - full * 100 / (100 + haste)
}

// ===================== buff 名 =====================

pub const D_CLOUD: &str = "league_hextech_d:cloud_soul";
pub const D_CHEM: &str = "league_hextech_d:chemtech_soul";
pub const D_BARON: &str = "league_hextech_d:hand_of_baron";
pub const S_RESOLUTE: &str = "league_hextech_s:stay_resolute";
pub const E_GOLDREND: &str = "league_hextech_e:goldrend";
pub const E_HEX_SLOW: &str = "league_hextech_e:hextech_soul_slow";
pub const E_CLOUD: &str = "league_hextech_e:cloud_soul";
pub const E_WARD_AR: &str = "league_hextech_e:adaptive_ward_armor";
pub const E_WARD_MR: &str = "league_hextech_e:adaptive_ward_mr";
pub const E_FLOW: &str = "league_hextech_e:flow_of_spirit";
pub const E_MERCY: &str = "league_hextech_e:mercys_strike";
pub const E_TRUSTY: &str = "league_hextech_e:trusty_weapon";

pub const BUFFS: [&str; 15] = [S_ANVIL[0], S_ANVIL[1], S_ANVIL[2], D_CLOUD, D_CHEM, D_BARON, S_RESOLUTE, E_GOLDREND, E_HEX_SLOW,
                               E_CLOUD, E_WARD_AR, E_WARD_MR, E_FLOW, E_MERCY, E_TRUSTY];

/// 打中英雄时要看的、控住敌人时要看的。
pub const ON_HIT: [Ev; 14] = [Ev::Goldrend, Ev::FromDowntown, Ev::InfernalSoul, Ev::HextechSoul, Ev::OceanSoul, Ev::OmniSoul,
                              Ev::AdaptiveWard, Ev::CrimsonCobalt, Ev::MercysStrike, Ev::Siphon, Ev::StayResolute,
                              Ev::TrustyWeapon, Ev::PursuitHaste, Ev::PursuitPower];
pub const ON_CC: [Ev; 1] = [Ev::RavenousBind];

// ===================== 龙魂 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Element {
    Infernal,
    Mountain,
    Ocean,
    Cloud,
    Hextech,
    Chemtech,
}

impl Element {
    pub const ALL: [Element; 6] =
        [Element::Infernal, Element::Mountain, Element::Ocean, Element::Cloud, Element::Hextech, Element::Chemtech];

    pub fn key(self) -> &'static str {
        match self {
            Element::Infernal => "infernal",
            Element::Mountain => "mountain",
            Element::Ocean => "ocean",
            Element::Cloud => "cloud",
            Element::Hextech => "hextech",
            Element::Chemtech => "chemtech",
        }
    }

    /// 大小龙 mod 整队拿到这种龙魂时挂的标记（它的 rules.rs 的 `soul_name`）。
    pub fn dragons_mark(self) -> String {
        format!("league_dragons_soul_{}", self.key())
    }
}

/// 这个海克斯给哪种龙魂（全能龙魂：随机三种，None）。
pub fn soul_of(ev: Ev) -> Option<Element> {
    match ev {
        Ev::InfernalSoul => Some(Element::Infernal),
        Ev::HextechSoul => Some(Element::Hextech),
        Ev::MountainSoul => Some(Element::Mountain),
        Ev::OceanSoul => Some(Element::Ocean),
        _ => None,
    }
}

pub const SOUL_EVS: [Ev; 5] = [Ev::InfernalSoul, Ev::HextechSoul, Ev::MountainSoul, Ev::OceanSoul, Ev::OmniSoul];

/// `have` 里没有的龙魂：单种的先给它自己那种，有了就随机换一种；全能龙魂随机三种。
pub fn pick_souls(ev: Ev, have: &[Element], rng: &mut Rng) -> Vec<Element> {
    let mut have = have.to_vec();
    let mut out = Vec::new();
    let n = if ev == Ev::OmniSoul { 3 } else { 1 };
    for _ in 0..n {
        let e = match soul_of(ev) {
            Some(e) if !have.contains(&e) => e,
            _ => {
                let left: Vec<Element> = Element::ALL.into_iter().filter(|e| !have.contains(e)).collect();
                if left.is_empty() {
                    break;
                }
                left[rng.below(left.len())]
            }
        };
        have.push(e);
        out.push(e);
    }
    out
}

// ===================== 铁砧 =====================

/// 这项属性合不合这个英雄（和海克斯的权重一个算法）。
pub fn stat_fit(s: Stat, t: &Traits) -> f32 {
    let w = match s {
        Stat::Attack => Traits { ad: 1.0, attacker: 0.5, bruiser: 0.3, ..Traits::ZERO },
        Stat::MagicPower => Traits { ap: 1.0, caster: 0.5, ..Traits::ZERO },
        Stat::Hp => Traits { tank: 1.0, bruiser: 0.6, support: 0.3, melee: 0.3, ..Traits::ZERO },
        Stat::AttackSpeed => Traits { attacker: 1.0, ad: 0.4, ..Traits::ZERO },
        Stat::Defence | Stat::MagicResistance => Traits { tank: 0.8, bruiser: 0.5, melee: 0.3, ..Traits::ZERO },
        Stat::Haste => Traits { caster: 1.0, support: 0.5, ap: 0.3, ..Traits::ZERO },
        Stat::Crit => Traits { ad: 0.8, attacker: 0.8, ranged: 0.3, ..Traits::ZERO },
        Stat::MoveSpeed => Traits { assassin: 0.6, bruiser: 0.3, support: 0.3, ..Traits::ZERO },
    };
    crate::rules::fit(&w, t)
}

fn add_stat(b: &mut BuffV1, s: Stat, v: i32) {
    match s {
        Stat::Attack => b.attack += v,
        Stat::MagicPower => b.magic_power += v,
        Stat::Hp => b.hp += v,
        Stat::AttackSpeed => b.attack_speed_mult += v,
        Stat::Defence => b.defence += v,
        Stat::MagicResistance => b.magic_resistance += v,
        Stat::Haste => {
            b.skill_cooldown_mult += v;
            b.ult_cooldown_mult += v;
        }
        Stat::Crit => b.crit_chance += v,
        Stat::MoveSpeed => b.move_speed_mult += v,
    }
}

/// 一个座位拿到 `ev`（三个属性海克斯之一）的铁砧：每个先按机会抽档（0 银、1 金、2 棱彩），再抽 3 项不同的属性，挑最合适的。
/// 加起来一个 buff；第二个是挑了哪些（日志、测试）。
pub fn anvils(seed: u64, seat: usize, ev: Ev, t: &Traits) -> Option<(BuffV1, Vec<(Stat, usize)>)> {
    let i = ANVILS.iter().position(|a| a.0 == ev)?;
    let (_, n, odds) = ANVILS[i];
    let mut rng = Rng::new(splitmix(seed ^ ANVIL_SALT ^ ((seat as u64) << 16) ^ ev as u64));
    let mut b = named(S_ANVIL[i], |_| {});
    let mut got = Vec::new();
    for _ in 0..n {
        let roll = rng.below(100) as u32;
        let tier = if roll < odds[0] { 0 } else if roll < odds[0] + odds[1] { 1 } else { 2 };
        let mut offer: Vec<usize> = Vec::new();
        while offer.len() < 3 {
            let s = rng.below(ANVIL_STATS.len());
            if !offer.contains(&s) {
                offer.push(s);
            }
        }
        let best = offer.iter().copied().fold(offer[0], |a, x| {
            if stat_fit(ANVIL_STATS[x].0, t) > stat_fit(ANVIL_STATS[a].0, t) { x } else { a }
        });
        let (s, v) = (ANVIL_STATS[best].0, ANVIL_STATS[best].1[tier]);
        add_stat(&mut b, s, v);
        got.push((s, tier));
    }
    Some((b, got))
}

// ===================== 一个座位的状态 =====================

/// 一个座位 0.5.0 的状态（跟着玩家：死了不清）。
#[derive(Clone, Debug, Default)]
pub struct Seat {
    /// 拿到的：(种类, 第几次拿到的, 技能格 1–3；不是技能海克斯：0)
    picks: Vec<(Ev, u8, u8)>,
    donated: bool,
    /// 铁砧：(种类, 加起来的 buff)；上次挂在哪个实体上
    anvils: Vec<(Ev, BuffV1)>,
    /// 龙魂：(哪个海克斯给的, 哪种)；算过的海克斯
    souls: Vec<(Ev, Element)>,
    souls_done: Vec<Ev>,
    /// 炼狱、海克斯科技、海洋龙魂下次能触发的 tick，山脉龙魂下次看护盾的 tick
    soul_cd: [usize; 3],
    mountain_at: usize,
    /// 超远狙击：远处命中了几次
    downtown: u32,
    /// 高压锻炉：烧了多少、下一下
    burned: usize,
    cooker_next: usize,
    /// 深红钴蓝：(被标记的座位, 到哪个 tick)
    marks: Vec<(usize, usize)>,
    /// 仁慈打击：从哪个 tick 起、到哪个 tick 的下一次普攻
    mercy: Option<(usize, usize)>,
    /// 坚定意志：永久的护甲、魔抗，下一层加魔抗
    resolute: (u16, u16),
    resolute_mr: bool,
    /// 急速追加、力量追寻：选定的技能命中了几次
    haste_hits: u32,
    power_hits: u32,
    /// 第一次看到他时的最大生命（嗜血束缚的「额外生命」）
    max0: Option<usize>,
    /// 男爵之手：下次给小兵挂 buff 的 tick
    minions_at: usize,
    /// 上次对永久 buff 时：(实体, 坚定意志两项)
    applied: Option<(usize, (u16, u16))>,
    /// 铁砧上次挂在哪个实体上
    anvil_on: Option<usize>,
}

/// 过一会儿才发生的。
#[derive(Clone, Debug)]
pub enum Late {
    /// 超远狙击：流星落到 `pos`
    Meteor { holder: usize, hent: usize, pos: (u64, u64), at: usize, base: usize, r: u64 },
}

fn has_buff(sim: &StableSim<'_>, ent: usize, name: &str) -> bool {
    sim.get_entity(ent).is_some_and(|e| (0..e.buff_count()).filter_map(|j| e.buff_at(j)).any(|b| b.name() == name))
}

impl Procs {
    /// 这个座位拿到了第 `k` 次的 `ev`（质变、潘朵拉给的算在拿到它们的那一次），技能海克斯选的是 `slot`。
    pub fn picked(&mut self, seat: usize, ev: Ev, k: usize, slot: u8) {
        if self.pls.len() <= seat {
            self.pls.resize(seat + 1, Pp::default());
        }
        let s = &mut self.pls[seat].b3;
        s.picks.retain(|p| p.0 != ev);
        s.picks.push((ev, k.min(255) as u8, slot));
    }

    /// 他这个技能海克斯选的格子（没登记过：AI 默认的）。
    pub fn slot_of(&self, seat: usize, ev: Ev) -> u8 {
        self.pls.get(seat).and_then(|p| p.b3.picks.iter().find(|x| x.0 == ev)).map_or(ai_slot(ev), |x| {
            if x.2 == 0 { ai_slot(ev) } else { x.2 }
        })
    }

    /// 测试、日志看的：选的格子、铁砧、龙魂。
    pub fn souls_of(&self, seat: usize) -> Vec<Element> {
        self.pls.get(seat).map_or(Vec::new(), |p| p.b3.souls.iter().map(|x| x.1).collect())
    }

    /// 0.5.0 的这一种不再有了（潘朵拉的盒子换掉了）：它的状态清掉、它挂的 buff 摘掉。
    pub(super) fn b3_forget(&mut self, sim: &mut StableSim<'_>, seat: usize, ent: Option<usize>, ev: Ev) {
        let Some(p) = self.pls.get_mut(seat) else { return };
        let s = &mut p.b3;
        let mut names: Vec<&str> = Vec::new();
        match ev {
            Ev::Stats1 | Ev::Stats2 | Ev::Stats3 => {
                s.anvils.retain(|a| a.0 != ev);
                if let Some(i) = ANVILS.iter().position(|a| a.0 == ev) {
                    names.push(S_ANVIL[i]);
                }
            }
            Ev::InfernalSoul | Ev::HextechSoul | Ev::MountainSoul | Ev::OceanSoul | Ev::OmniSoul => {
                s.souls.retain(|x| x.0 != ev);
                s.souls_done.retain(|&x| x != ev);
                names.extend([D_CLOUD, D_CHEM]);
            }
            Ev::HandOfBaron => names.push(D_BARON),
            Ev::StayResolute => {
                s.resolute = (0, 0);
                names.push(S_RESOLUTE);
                s.applied = None;
            }
            Ev::TrustyWeapon => names.push(E_TRUSTY),
            Ev::AdaptiveWard => names.extend([E_WARD_AR, E_WARD_MR]),
            Ev::FlowOfSpirit => names.push(E_FLOW),
            Ev::MercysStrike => {
                s.mercy = None;
                names.push(E_MERCY);
            }
            _ => {}
        }
        s.picks.retain(|x| x.0 != ev);
        let dyn_names: Vec<&str> = names.iter().copied().filter(|n| n.starts_with("league_hextech_d:")).collect();
        for n in &dyn_names {
            self.b2_drop_dyn(seat, n);
        }
        if let Some(e) = ent {
            for n in names {
                sim.entity_remove_buff(e, n);
            }
        }
    }

    /// 一个活着的座位这一步的 0.5.0 效果。
    #[allow(clippy::too_many_arguments)]
    pub(super) fn b3_seat(&mut self, sim: &mut StableSim<'_>, now: usize, h: usize, who: &[Who], set: EvSet, looks: &[L],
                          hit: Option<&Hit>, cc: Option<usize>, names: &[String], screen: bool) {
        let me = looks[h];
        let has = |ev: Ev| set & ev.bit() != 0;
        let level = self.pls[h].level;
        let (ad, ap) = ad_ap(sim, me.ent);
        let cast = self.pls[h].cast;
        let at_now = |k: usize| cast[k] == Some(now);
        if self.pls[h].b3.max0.is_none() {
            self.pls[h].b3.max0 = Some(me.max);
        }

        // ---------- 拿到时一次 ----------
        if has(Ev::Donation) && !self.pls[h].b3.donated {
            self.pls[h].b3.donated = true;
            if sim.player_add_gold(who[h].player, DONATION_GOLD) {
                self.fire(Ev::Donation);
                self.say(screen, || format!("PROC donation {}: +{DONATION_GOLD} gold", names[h]));
                self.show(screen, now, Show::LightPop, me.pos, Vec::new(), 0);
            }
        }
        for (ev, _, _) in ANVILS {
            if has(ev) && !self.pls[h].b3.anvils.iter().any(|a| a.0 == ev) {
                if let Some((b, got)) = anvils(sim.seed(), h, ev, &who[h].traits) {
                    self.pls[h].b3.anvils.push((ev, b));
                    self.pls[h].b3.anvil_on = None;
                    self.fire(ev);
                    let list: Vec<String> = got.iter().map(|(s, t)| format!("{s:?}/{}", ["silver", "gold", "prismatic"][*t])).collect();
                    self.say(screen, || format!("PROC {:?} {}: anvils {}", ev, names[h], list.join(", ")));
                    self.show(screen, now, Show::Grow, me.pos, Vec::new(), 0);
                }
            }
        }
        for ev in SOUL_EVS {
            if has(ev) && !self.pls[h].b3.souls_done.contains(&ev) {
                let mut have: Vec<Element> =
                    Element::ALL.into_iter().filter(|e| has_buff(sim, me.ent, &e.dragons_mark())).collect();
                have.extend(self.pls[h].b3.souls.iter().map(|x| x.1));
                let mut rng = Rng::new(splitmix(sim.seed() ^ SOUL_SALT ^ ((h as u64) << 16) ^ ev as u64));
                let got = pick_souls(ev, &have, &mut rng);
                let s = &mut self.pls[h].b3;
                s.souls.extend(got.iter().map(|&e| (ev, e)));
                s.souls_done.push(ev);
                self.fire(ev);
                let keys: Vec<&str> = got.iter().map(|e| e.key()).collect();
                self.say(screen, || format!("PROC {:?} {}: souls {}", ev, names[h], keys.join(", ")));
            }
        }

        // ---------- 龙魂（英雄身上已经有大小龙给的同一种：这一种不算） ----------
        let souls: Vec<Element> = self.pls[h].b3.souls.iter().map(|x| x.1)
            .filter(|e| !has_buff(sim, me.ent, &e.dragons_mark()))
            .collect();
        let soul = |e: Element| souls.contains(&e);
        if let (Some(x), Some(v)) = (hit, hit.map(|x| x.victims[0])) {
            if soul(Element::Infernal) && now >= self.pls[h].b3.soul_cd[0] {
                self.pls[h].b3.soul_cd[0] = now + INFERNAL_CD;
                let amount = infernal_damage(ad, ap);
                let at = looks[v].pos;
                for u in enemies_near(looks, h, at, INFERNAL_R) {
                    self.hit(sim, now, h, me.ent, looks[u].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                }
                self.fire(Ev::InfernalSoul);
                self.show(screen, now, Show::RingRed, at, vec![(INFERNAL_R, 0)], 20);
                self.show(screen, now, Show::Burn, at, Vec::new(), 0);
            }
            if soul(Element::Hextech) && now >= self.pls[h].b3.soul_cd[1] {
                self.pls[h].b3.soul_cd[1] = now + HEXSOUL_CD;
                let amount = hexsoul_damage(ad, ap);
                let mut others: Vec<(u64, usize)> = enemies_near(looks, h, looks[v].pos, HEXSOUL_R)
                    .into_iter()
                    .filter(|&u| u != v)
                    .map(|u| (d2(looks[u].pos, looks[v].pos), u))
                    .collect();
                others.sort();
                let chain: Vec<usize> =
                    std::iter::once(v).chain(others.into_iter().map(|o| o.1)).take(HEXSOUL_TARGETS).collect();
                for &u in &chain {
                    self.hit(sim, now, h, me.ent, looks[u].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    put_timed(sim, looks[u].ent, &timed(E_HEX_SLOW, HEXSOUL_SLOW_T, |b| b.move_speed_mult = -HEXSOUL_SLOW));
                }
                self.fire(Ev::HextechSoul);
                self.show(screen, now, Show::Chain, me.pos, chain.iter().map(|&u| looks[u].pos).collect(), 0);
            }
            if soul(Element::Ocean) && now >= self.pls[h].b3.soul_cd[2] && x.delta > 0 {
                self.pls[h].b3.soul_cd[2] = now + OCEAN_CD;
                let per = (ocean_heal(ad, ap, me.max) / OCEAN_PULSES as usize).max(1);
                self.hots.push(Hot { seat: h, ent: me.ent, per, left: OCEAN_PULSES, next: now });
                self.fire(Ev::OceanSoul);
                self.show(screen, now, Show::RingBlue, me.pos, vec![(16_000, 0)], 24);
            }
        }
        if soul(Element::Mountain) && now >= self.pls[h].b3.mountain_at
            && self.pls[h].last_hurt.is_none_or(|t| now >= t + MOUNTAIN_IDLE)
        {
            self.pls[h].b3.mountain_at = now + MOUNTAIN_CHECK;
            let want = mountain_shield(ad, ap, me.max);
            let shield = self.pls[h].shield;
            if shield < want && sim.entity_add_shield(me.ent, want - shield, MOUNTAIN_T) {
                self.pls[h].shield = want;
                self.guarded(screen, h, me.ent, now, MOUNTAIN_T);
                self.fire(Ev::MountainSoul);
                self.show(screen, now, Show::Ward, me.pos, Vec::new(), 0);
            }
        }
        let cloud = soul(Element::Cloud);
        self.dyn_set(sim, h, me.ent, D_CLOUD, cloud as i64, |_| named(D_CLOUD, |b| b.move_speed_mult = CLOUD_MS));
        if cloud && at_now(3) {
            put_timed(sim, me.ent, &timed(E_CLOUD, CLOUD_ULT_T, |b| b.move_speed_mult = CLOUD_ULT_MS));
            self.show(screen, now, Show::RingCyan, me.pos, vec![(20_000, 0)], 24);
        }
        let chem = soul(Element::Chemtech) && below(me.hp, me.max, CHEM_PCT);
        self.dyn_set(sim, h, me.ent, D_CHEM, chem as i64, |_| {
            named(D_CHEM, |b| {
                b.toughness = 15;
                b.damaged_reduce = 12;
                b.attack_mult = 12;
                b.magic_power_mult = 12;
            })
        });

        // ---------- 男爵之手 ----------
        if has(Ev::HandOfBaron) {
            let key = if ad >= ap { 1 } else { 2 };
            if self.dyn_set(sim, h, me.ent, D_BARON, key, |k| {
                named(D_BARON, |b| if k == 1 { b.attack_mult = BARON_PCT } else { b.magic_power_mult = BARON_PCT })
            }) {
                self.fire(Ev::HandOfBaron);
            }
            if now >= self.pls[h].b3.minions_at {
                self.pls[h].b3.minions_at = now + MINION_EVERY;
                let mut minions = Vec::new();
                for i in 0..sim.entity_count() {
                    let Some(e) = sim.entity_at(i) else { continue };
                    if e.team() == me.team && e.is_alive() && matches!(e.kind(), Some(EntityKindV1::Minion))
                        && within(e.pos(), me.pos, MINION_R)
                    {
                        minions.push(e.id());
                    }
                }
                let boost = timed(MINION_BOOST, MINION_T, |b| {
                    b.damaged_reduce = MINION_REDUCE;
                    b.attack_mult = MINION_ATTACK;
                });
                if !minions.is_empty() {
                    self.fire(Ev::HandOfBaron);
                }
                for m in minions {
                    put_timed(sim, m, &boost);
                }
            }
        }

        // ---------- 打中英雄 ----------
        if let (Some(x), Some(v)) = (hit, hit.map(|x| x.victims[0])) {
            if has(Ev::Goldrend) {
                for &u in &x.victims {
                    if self.gate(h, Ev::Goldrend, u, now, GOLDREND_GAP) {
                        let amount = goldrend_damage(level, ad, ap);
                        self.hit(sim, now, h, me.ent, looks[u].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                        sim.player_add_gold(who[h].player, GOLDREND_GOLD);
                        put_timed(sim, me.ent, &timed(E_GOLDREND, GOLDREND_MS_T, |b| b.move_speed_mult = GOLDREND_MS));
                        self.fire(Ev::Goldrend);
                        self.show(screen, now, Show::Execute, looks[u].pos, Vec::new(), 0);
                    }
                }
            }
            if has(Ev::FromDowntown) && x.skill.is_some() {
                let dist = (d2(me.pos, looks[v].pos) as f64).sqrt() as u64;
                if dist >= DOWNTOWN_FAR {
                    if self.pls[h].b3.downtown < DOWNTOWN_QUEST {
                        if self.gate(h, Ev::FromDowntown, v, now, DOWNTOWN_HIT_GAP) {
                            self.pls[h].b3.downtown += 1;
                            if self.pls[h].b3.downtown == DOWNTOWN_QUEST {
                                self.say(screen, || format!("PROC from_downtown {}: quest done", names[h]));
                                self.show(screen, now, Show::LightPop, me.pos, Vec::new(), 0);
                            }
                        }
                    } else if self.gate(h, Ev::FromDowntown, v, now, DOWNTOWN_GAP) {
                        let pos = looks[v].pos;
                        let base = downtown_damage(level, ad, ap, dist);
                        self.later3.push(Late::Meteor { holder: h, hent: me.ent, pos, at: now + METEOR_T, base, r: meteor_r(dist) });
                        self.show(screen, now, Show::Comet, pos, Vec::new(), 0);
                    }
                }
            }
            let k_of = |p: &Procs, ev: Ev| p.slot_of(h, ev) as usize;
            if has(Ev::AdaptiveWard) && x.skill == Some(k_of(self, Ev::AdaptiveWard)) && self.ready_at(h, Ev::AdaptiveWard, now) {
                self.arm(h, Ev::AdaptiveWard, now + WARD_CD);
                let st = sim.get_entity(me.ent).map(|e| e.stat());
                let (ar, mr) = st.map_or((0, 0), |s| (s.defence, s.magic_resistance));
                let v = by_level(7, 12, level) as i32;
                let b = if ar <= mr {
                    timed(E_WARD_AR, WARD_T, |b| b.defence = v)
                } else {
                    timed(E_WARD_MR, WARD_T, |b| b.magic_resistance = v)
                };
                Self::stack_timed(sim, me.ent, &b, WARD_MOST);
                self.fire(Ev::AdaptiveWard);
                self.show(screen, now, Show::Guard, me.pos, vec![me.pos], 0);
            }
            if has(Ev::CrimsonCobalt) {
                let k = k_of(self, Ev::CrimsonCobalt);
                if x.basic {
                    let marked: Vec<usize> = x.victims.iter().copied()
                        .filter(|u| self.pls[h].b3.marks.iter().any(|m| m.0 == *u && m.1 > now))
                        .collect();
                    for u in marked {
                        let amount = cobalt_damage(level, ad, ap);
                        self.hit(sim, now, h, me.ent, looks[u].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                        let cut = self.pls[h].full[k] * COBALT_CUT_PCT / 100;
                        if cut > 0 {
                            sim.entity_reduce_cooldown(me.ent, slot(k), cut);
                        }
                        self.pls[h].b3.marks.retain(|m| m.0 != u);
                        self.fire(Ev::CrimsonCobalt);
                        self.show(screen, now, Show::Execute, looks[u].pos, Vec::new(), 0);
                    }
                }
                if x.skill == Some(k) {
                    let s = &mut self.pls[h].b3;
                    s.marks.retain(|m| m.1 > now);
                    for &u in &x.victims {
                        s.marks.retain(|m| m.0 != u);
                        s.marks.push((u, now + COBALT_T));
                    }
                    for &u in &x.victims {
                        self.show(screen, now, Show::RingPurple, looks[u].pos, vec![(12_000, 0)], 16);
                    }
                }
            }
            if has(Ev::MercysStrike) && x.basic {
                if let Some((from, until)) = self.pls[h].b3.mercy {
                    if now > from && now <= until {
                        self.pls[h].b3.mercy = None;
                        sim.entity_remove_buff(me.ent, E_MERCY);
                        let amount = looks[v].max * MERCY_PERMILLE / 1000;
                        self.hit(sim, now, h, me.ent, looks[v].ent, amount.max(1), DamageTypeV1::Ap, AttackTypeV1::Skill);
                        self.fire(Ev::MercysStrike);
                        self.show(screen, now, Show::Heavy, looks[v].pos, Vec::new(), 0);
                    }
                }
            }
            if has(Ev::Siphon) && x.skill == Some(k_of(self, Ev::Siphon)) && x.delta > 0 {
                let heal = (x.delta * SIPHON_PCT / 100) as usize;
                if heal > 0 {
                    sim.heal(me.ent, me.ent, heal);
                    self.fire(Ev::Siphon);
                }
            }
            if has(Ev::StayResolute) && x.skill == Some(k_of(self, Ev::StayResolute)) {
                for &u in &x.victims {
                    if self.gate(h, Ev::StayResolute, u, now, RESOLUTE_GAP) {
                        let add = by_level(2, 3, level) as u16;
                        let s = &mut self.pls[h].b3;
                        if s.resolute_mr {
                            s.resolute.1 = s.resolute.1.saturating_add(add);
                        } else {
                            s.resolute.0 = s.resolute.0.saturating_add(add);
                        }
                        s.resolute_mr = !s.resolute_mr;
                        self.fire(Ev::StayResolute);
                    }
                }
            }
            if has(Ev::TrustyWeapon) && x.skill == Some(k_of(self, Ev::TrustyWeapon)) {
                let b = timed(E_TRUSTY, TRUSTY_T, |b| {
                    b.attack_mult = TRUSTY_PCT;
                    b.magic_power_mult = TRUSTY_PCT;
                });
                for _ in &x.victims {
                    Self::stack_timed(sim, me.ent, &b, TRUSTY_MOST);
                }
                self.fire(Ev::TrustyWeapon);
            }
            if has(Ev::PursuitHaste) && x.skill == Some(k_of(self, Ev::PursuitHaste)) && self.pls[h].b3.haste_hits < PURSUIT_ALL
                && self.gate(h, Ev::PursuitHaste, v, now, PURSUIT_HIT_GAP)
            {
                self.pls[h].b3.haste_hits += 1;
                let n = self.pls[h].b3.haste_hits;
                if n == PURSUIT_FIRST || n == PURSUIT_ALL {
                    self.say(screen, || format!("PROC pursuit_of_haste {}: {n} hits - +{} haste", names[h], pursuit_haste(n)));
                    self.show(screen, now, Show::LightPop, me.pos, Vec::new(), 0);
                }
            }
            if has(Ev::PursuitPower) && x.skill == Some(k_of(self, Ev::PursuitPower)) {
                if self.pls[h].b3.power_hits < PURSUIT_FIRST {
                    if self.gate(h, Ev::PursuitPower, v, now, PURSUIT_HIT_GAP) {
                        self.pls[h].b3.power_hits += 1;
                        if self.pls[h].b3.power_hits == PURSUIT_FIRST {
                            self.say(screen, || format!("PROC pursuit_of_power {}: quest done", names[h]));
                            self.show(screen, now, Show::LightPop, me.pos, Vec::new(), 0);
                        }
                    }
                } else if x.delta > 0 {
                    let each = (x.delta * POWER_PCT / 100) as usize / x.victims.len().max(1);
                    for &u in &x.victims {
                        self.hit(sim, now, h, me.ent, looks[u].ent, each, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                    }
                    self.fire(Ev::PursuitPower);
                }
            }
        }

        // ---------- 控住敌人 ----------
        if let Some(v) = cc {
            if has(Ev::RavenousBind) && self.ready_at(h, Ev::RavenousBind, now) {
                self.arm(h, Ev::RavenousBind, now + BIND_CD);
                // 是哪个技能控的：最近放的那个
                let k = (1..4).filter(|&k| cast[k].is_some()).max_by_key(|&k| cast[k]).unwrap_or(1);
                let full = self.pls[h].full[k];
                let amount = bind_damage(level, ap, me.max);
                self.hit(sim, now, h, me.ent, looks[v].ent, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
                let bonus = me.max.saturating_sub(self.pls[h].b3.max0.unwrap_or(me.max));
                sim.heal(me.ent, me.ent, by_cooldown(bind_heal(level, ap, bonus), full));
                self.fire(Ev::RavenousBind);
                self.show(screen, now, Show::RingBlue, me.pos, vec![(14_000, 0)], 20);
            }
        }

        // ---------- 放技能 ----------
        for k in 1..4usize {
            if !at_now(k) {
                continue;
            }
            let full = self.pls[h].full[k];
            let chosen = |p: &Procs, ev: Ev| has(ev) && p.slot_of(h, ev) as usize == k;
            if chosen(self, Ev::FlowOfSpirit) {
                let pct = by_level(60, 120, level) as i32;
                put_timed(sim, me.ent, &timed(E_FLOW, FLOW_T, |b| b.attack_speed_mult = pct));
                self.fire(Ev::FlowOfSpirit);
                self.show(screen, now, Show::Excited, me.pos, Vec::new(), 0);
            }
            if chosen(self, Ev::MercysStrike) {
                self.pls[h].b3.mercy = Some((now, now + MERCY_T));
                put_timed(sim, me.ent, &timed(E_MERCY, MERCY_T, |b| {
                    b.range = MERCY_RANGE;
                    b.attack_speed_mult = MERCY_AS;
                }));
            }
            if chosen(self, Ev::Rejuvenation) {
                let heal = by_cooldown(rejuv_heal(level, ad, ap, me.max), full);
                sim.heal(me.ent, me.ent, heal);
                self.fire(Ev::Rejuvenation);
                self.show(screen, now, Show::Dawn, me.pos, Vec::new(), 0);
            }
            if chosen(self, Ev::Terror) && self.ready_at(h, Ev::Terror, now) {
                self.arm(h, Ev::Terror, now + TERROR_CD);
                let near = enemies_near(looks, h, me.pos, TERROR_R);
                for &u in &near {
                    sim.apply_cc(looks[u].ent, &CcV1::of_kind(CcKindV1::Fear, TERROR_T));
                    self.own_cc.push((looks[u].ent, now + EVERY * 2));
                }
                self.fire(Ev::Terror);
                let n = near.len();
                self.say(screen, || format!("PROC terror {}: {n} champions feared", names[h]));
                self.show(screen, now, Show::RingPurple, me.pos, vec![(TERROR_R, 0)], 30);
            }
            // 某个技能的技能急速：放完以后再缩短它的冷却
            let butter = has(Ev::BreadButter) && k == 1;
            let jam = has(Ev::BreadJam) && k == 2;
            let pursuit = if chosen(self, Ev::PursuitHaste) { pursuit_haste(self.pls[h].b3.haste_hits) } else { 0 };
            let mut haste = pursuit;
            if butter {
                haste += BREAD_HASTE;
            }
            if jam {
                haste += BREAD_HASTE;
            }
            if haste > 0 && full > 0 {
                sim.entity_reduce_cooldown(me.ent, slot(k), haste_cut(full, haste));
                // 0.5.2：这一下冷却缩短了，各算一次
                for (on, ev) in [(butter, Ev::BreadButter), (jam, Ev::BreadJam), (pursuit > 0, Ev::PursuitHaste)] {
                    if on {
                        self.fire(ev);
                    }
                }
            }
            // 过载：放了别的技能，选定的那个转好
            if has(Ev::Overloaded) {
                let o = self.slot_of(h, Ev::Overloaded) as usize;
                if o != k && (1..4).contains(&o) {
                    sim.entity_reduce_cooldown(me.ent, slot(o), RESET);
                    self.fire(Ev::Overloaded);
                }
            }
        }

        // ---------- 定时 ----------
        if has(Ev::PressureCooker) && now >= self.pls[h].b3.cooker_next {
            self.pls[h].b3.cooker_next = now + COOKER_EVERY;
            let (r, rate) = cooker(self.pls[h].b3.burned);
            let per = me.max * COOKER_PERMILLE * rate / 1000;
            let near = enemies_near(looks, h, me.pos, r);
            if !near.is_empty() && per > 0 {
                for &u in &near {
                    self.hit(sim, now, h, me.ent, looks[u].ent, per, DamageTypeV1::Ap, AttackTypeV1::Dot);
                }
                let before = cooker(self.pls[h].b3.burned);
                self.pls[h].b3.burned += per * near.len();
                let after = cooker(self.pls[h].b3.burned);
                if after != before {
                    let burned = self.pls[h].b3.burned;
                    self.say(screen, || format!("PROC pressure_cooker {}: {burned} burned - radius {} x{}", names[h], after.0, after.1));
                }
                self.fire(Ev::PressureCooker);
                self.show(screen, now, Show::Immolate, me.pos, Vec::new(), 0);
            }
        }
    }

    /// 0.5.0 过一会儿才发生的。
    pub(super) fn b3_later(&mut self, sim: &mut StableSim<'_>, now: usize, who: &[Who], looks: &[L], names: &[String],
                           screen: bool) {
        let all = std::mem::take(&mut self.later3);
        for x in all {
            match x {
                Late::Meteor { at, .. } if at > now => self.later3.push(x),
                Late::Meteor { holder, hent, pos, base, r, .. } => {
                    if !looks.get(holder).is_some_and(|l| l.alive && l.ent == hent) {
                        continue;
                    }
                    let team = who[holder].team;
                    let mut n = 0;
                    for u in looks {
                        if u.alive && u.team != team && within(u.pos, pos, r) {
                            self.hit(sim, now, holder, hent, u.ent, base, DamageTypeV1::Ap, AttackTypeV1::Skill);
                            n += 1;
                        }
                    }
                    self.fire(Ev::FromDowntown);
                    self.say(screen, || format!("PROC from_downtown {}: a meteor - {base} magic on {n}", names[holder]));
                    self.show(screen, now, Show::RingRed, pos, vec![(r, 0)], 20);
                }
            }
        }
    }

    /// 永久的：铁砧、坚定意志（复活后补回、数变了重挂）。
    pub(super) fn b3_keep(&mut self, sim: &mut StableSim<'_>, now: usize, who: &[Who], held: &[EvSet], looks: &[L]) {
        for h in 0..who.len().min(self.pls.len()) {
            if held[h] == 0 || !looks[h].alive {
                continue;
            }
            let ent = looks[h].ent;
            // 铁砧：换了身体、复活了、新拿到的，或者每 30 tick 看一眼还在不在
            let s = &self.pls[h].b3;
            if !s.anvils.is_empty() && (s.anvil_on != Some(ent) || self.pls[h].respawned || now.is_multiple_of(30)) {
                let list: Vec<BuffV1> = self.pls[h].b3.anvils.iter().map(|a| a.1).collect();
                for b in list {
                    if !has_buff(sim, ent, b.name()) {
                        sim.add_buff(ent, &b);
                    }
                }
                self.pls[h].b3.anvil_on = Some(ent);
            }
            let s = &self.pls[h].b3;
            let bonus = s.picks.iter().find(|p| p.0 == Ev::StayResolute).is_some_and(|p| p.1 > 0) as i32 * RESOLUTE_BONUS;
            let want = s.resolute;
            let on = held[h] & Ev::StayResolute.bit() != 0;
            if !on || (s.applied == Some((ent, want)) && !self.pls[h].respawned) {
                continue;
            }
            sim.entity_remove_buff(ent, S_RESOLUTE);
            sim.add_buff(ent, &named(S_RESOLUTE, |b| {
                b.defence = want.0 as i32 + bonus;
                b.magic_resistance = want.1 as i32 + bonus;
            }));
            self.pls[h].b3.applied = Some((ent, want));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_numbers_follow_the_cards() {
        assert_eq!(goldrend_damage(1, 100, 100), 50 + 40 + 20);
        assert_eq!(downtown_damage(1, 100, 100, 60_000), 75 + 50 + 20);
        assert_eq!(downtown_damage(1, 100, 100, 200_000), (75 + 50 + 20) * 3 / 2, "+50% at most");
        assert_eq!((meteor_r(50_000), meteor_r(200_000)), (15_000, 25_000));
        assert_eq!((cooker(0), cooker(1_500), cooker(13_500), cooker(28_500)), ((30_000, 1), (50_000, 1), (50_000, 2), (60_000, 2)));
        assert_eq!(infernal_damage(100, 100), 140);
        assert_eq!(ocean_heal(100, 100, 2000), 100 + 30 + 20 + 160);
        assert_eq!(mountain_shield(100, 100, 2000), 200 + 15 + 10 + 160);
        assert_eq!((by_cooldown(100, 0), by_cooldown(100, 600), by_cooldown(100, 5_000)), (100, 125, 150));
        assert_eq!(bind_heal(12, 100, 1000), 300 + 5 + 120);
        assert_eq!(rejuv_heal(1, 100, 100, 2000), 30 + 25 + 15 + 100);
        assert_eq!((haste_cut(600, 100), haste_cut(600, 80), haste_cut(600, 160)), (300, 267, 370));
        assert_eq!((pursuit_haste(9), pursuit_haste(10), pursuit_haste(30)), (0, 80, 160));
        let mut names = BUFFS.to_vec();
        names.sort();
        names.dedup();
        assert_eq!(names.len(), BUFFS.len(), "every buff name once");
    }

    #[test]
    fn anvils_are_the_same_for_the_same_seed_and_suit_the_hero() {
        let mage = Traits { ap: 1.0, caster: 1.0, ranged: 1.0, ..Traits::ZERO };
        let tank = Traits { tank: 1.0, bruiser: 0.4, melee: 1.0, support: 0.5, ..Traits::ZERO };
        for seed in 0..200u64 {
            let a = anvils(seed, 3, Ev::Stats2, &mage).unwrap();
            assert_eq!(a, anvils(seed, 3, Ev::Stats2, &mage).unwrap());
            assert_eq!(a.1.len(), 3);
            assert_eq!(anvils(seed, 3, Ev::Stats3, &tank).unwrap().1.len(), 4);
        }
        // a mage mostly gets ability power and haste, a tank health and resists
        let count = |t: &Traits, ok: &[Stat]| -> usize {
            (0..300u64).flat_map(|s| anvils(s, 1, Ev::Stats1, t).unwrap().1).filter(|(s, _)| ok.contains(s)).count()
        };
        // 600 个铁砧：三项里有法强或急速的约 58%，有生命、护甲、魔抗的约 76%
        assert!(count(&mage, &[Stat::MagicPower, Stat::Haste]) >= 300, "{}", count(&mage, &[Stat::MagicPower, Stat::Haste]));
        assert!(count(&tank, &[Stat::Hp, Stat::Defence, Stat::MagicResistance]) >= 400);
        assert!(anvils(1, 1, Ev::Donation, &mage).is_none());
    }

    #[test]
    fn souls_never_repeat_one_already_held() {
        let mut rng = Rng::new(5);
        assert_eq!(pick_souls(Ev::InfernalSoul, &[], &mut rng), vec![Element::Infernal]);
        let other = pick_souls(Ev::InfernalSoul, &[Element::Infernal], &mut rng);
        assert_eq!(other.len(), 1);
        assert_ne!(other[0], Element::Infernal);
        for seed in 0..100 {
            let mut rng = Rng::new(seed);
            let three = pick_souls(Ev::OmniSoul, &[Element::Ocean], &mut rng);
            assert_eq!(three.len(), 3);
            assert!(!three.contains(&Element::Ocean));
            assert!(three[0] != three[1] && three[1] != three[2] && three[0] != three[2], "{three:?}");
        }
        assert!(pick_souls(Ev::MountainSoul, &Element::ALL, &mut rng).is_empty(), "all six held: nothing left");
    }
}
