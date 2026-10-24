//! 盖伦 R 放不放、放给谁、落剑时补多少：纯计算，不碰游戏接口。
//!
//! 英雄联盟的「德玛西亚正义」是斩杀：150/300/450 + 已损失生命 25/30/35% 的真实伤害。主包读不到生命，只能写成
//! 150 + 120% 攻击力 + 12% 最大生命，AI 一好就放。副本（`make_override.py`）去掉 12% 最大生命，落剑时本包按目标那时的
//! 已损失生命补 `R_MISSING`% 的真实伤害；AI 钩子只在这一剑砍得死人时放。数字和主包核对见 `make_override.py`。

/// 盖伦的英雄 id。
pub const HERO: &str = "league_garen";
/// 主包 R 的固定伤害和攻击力 %（FixedAttack 的 damage / attack_ratio）。
pub const R_BASE: usize = 150;
pub const R_AD: usize = 120;
/// 本包落剑时补的已损失生命 %（英雄联盟 25/30/35%，取中间一档）。
pub const R_MISSING: usize = 30;
/// R 的施放距离。
pub const R_RANGE: usize = 45_000;
/// 从放出 R 到落剑的 tick（start_timing 10 + Delayed 10）。
pub const R_LAND: usize = 20;
/// 副本在 R 出手（start_timing）时给目标挂的标记：本包看到它，再过 `MARK_TO_LAND` tick 补伤害。
pub const MARK: &str = "league_garen_ult_mark";
pub const MARK_TICKS: usize = 14;
pub const MARK_TO_LAND: usize = 10;

/// 一个敌方英雄：id、当前生命、最大生命、护盾，身上有没有免死，和他身上 buff 的受到伤害增减（%，各自加总）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Foe {
    pub id: usize,
    pub hp: usize,
    pub max: usize,
    pub shield: usize,
    pub undying: bool,
    pub reduce: usize,
    pub amplify: usize,
    pub skill_reduce: usize,
}

impl Foe {
    pub fn ehp(&self) -> usize {
        self.hp + self.shield
    }

    /// 真实伤害 `d` 落到他身上是多少（league_darius_ult 在经典 SDK 的引擎里量的折算）。
    pub fn damage_from(&self, d: usize) -> usize {
        let taken = (100 + self.amplify).saturating_sub(self.reduce);
        d * taken / 100 * 100usize.saturating_sub(self.skill_reduce) / 100
    }

    /// 落剑时补的那一份：已损失生命的 `R_MISSING`%（按现在的生命算）。
    pub fn missing_part(&self) -> usize {
        self.max.saturating_sub(self.hp) * R_MISSING / 100
    }

    /// 攻击力 `attack` 的盖伦这一剑的真实伤害（数据那份加上本包补的那份，落到他身上之前）。
    pub fn r_damage(&self, attack: usize) -> usize {
        R_BASE + attack * R_AD / 100 + self.missing_part()
    }

    /// 这一剑砍得死他。
    pub fn dies_to(&self, attack: usize) -> bool {
        !self.undying && self.damage_from(self.r_damage(attack)) >= self.ehp()
    }
}

/// 砍得死的人里生命 + 护盾最少的。
pub fn best_kill(foes: &[Foe], attack: usize) -> Option<Foe> {
    foes.iter().copied().filter(|f| f.dies_to(attack)).min_by_key(|f| (f.ehp(), f.id))
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Plan {
    /// 照 AI 原来的输入。
    Keep,
    /// 放 R，砍这个人。
    Ult(usize),
    /// AI 想对这个人放 R，但砍不死：改成打他。
    Hold(usize),
}

/// `ai`：AI 原来的输入是 R 时它的目标；`ai_foe`：那个目标现在的样子；`foes`：射程内能被 R 选中的敌方英雄；
/// `ready`：R 好了、AI 没在放别的技能或回城。
pub fn plan(ai: Option<usize>, ai_foe: Option<Foe>, foes: &[Foe], attack: usize, ready: bool) -> Plan {
    let kill = best_kill(foes, attack);
    match ai {
        Some(x) => {
            if ai_foe.is_some_and(|f| f.dies_to(attack)) {
                Plan::Keep
            } else if let Some(k) = kill {
                Plan::Ult(k.id)
            } else {
                Plan::Hold(x)
            }
        }
        None if !ready => Plan::Keep,
        None => kill.map_or(Plan::Keep, |k| Plan::Ult(k.id)),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn f(id: usize, hp: usize, max: usize) -> Foe {
        Foe { id, hp, max, ..Foe::default() }
    }

    #[test]
    fn the_blow_grows_with_missing_health() {
        // 攻击 200：150 + 240 = 390，已损失 1000 的 30% = 300
        assert_eq!(f(1, 500, 1500).r_damage(200), 690);
        assert_eq!(f(1, 1500, 1500).r_damage(200), 390);
        assert!(f(1, 600, 1500).dies_to(200));
        assert!(!f(1, 800, 1500).dies_to(200));
    }

    #[test]
    fn shields_undying_and_reductions_count() {
        let shielded = Foe { shield: 200, ..f(1, 600, 1500) };
        assert!(!shielded.dies_to(200));
        let undying = Foe { undying: true, ..f(2, 10, 1500) };
        assert!(!undying.dies_to(200));
        let tough = Foe { reduce: 50, ..f(3, 400, 1500) };
        // 150 + 240 + 330 = 720，减伤 50% 剩 360 < 400
        assert!(!tough.dies_to(200));
    }

    #[test]
    fn r_only_for_a_kill() {
        let foes = [f(1, 1400, 1500), f(2, 500, 1500), f(3, 600, 1500)];
        // AI 想砍 1：砍不死，改砍 2（生命最少的砍得死的）
        assert_eq!(plan(Some(1), Some(foes[0]), &foes, 200, true), Plan::Ult(2));
        assert_eq!(plan(Some(3), Some(foes[2]), &foes, 200, true), Plan::Keep);
        let thick = [f(1, 1400, 1500), f(2, 1300, 1500)];
        assert_eq!(plan(Some(1), Some(thick[0]), &thick, 200, true), Plan::Hold(1));
        assert_eq!(plan(None, None, &foes, 200, true), Plan::Ult(2));
        assert_eq!(plan(None, None, &thick, 200, true), Plan::Keep);
        assert_eq!(plan(None, None, &foes, 200, false), Plan::Keep);
    }
}
