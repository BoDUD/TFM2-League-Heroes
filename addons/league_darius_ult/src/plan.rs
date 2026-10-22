//! 诺手 R 放不放、放给谁：纯计算，不碰游戏接口（附加包的 AI 钩子和经典 SDK 的模拟器共用这一份）。
//!
//! 数字全是主包 league/champion/league_darius.data_champion 里的；`make_override.py` 生成副本前逐个核对，不一致就停。

/// 诺手的英雄 id。
pub const HERO: &str = "league_darius";
/// 诺克萨斯之力（第 5 次命中英雄时加在诺手身上）。
pub const MIGHT: &str = "league_darius_might";
/// 出血层数：诺手 5 秒内命中英雄的次数，记在诺手自己身上（每层各 300 tick，数最高的那层）。
pub const HEMO: [&str; 4] = ["league_darius_hemo_1", "league_darius_hemo_2", "league_darius_hemo_3", "league_darius_hemo_4"];
/// R 的真实伤害：(固定值, 攻击力 %)，下标是落刀时的出血层数（0-4），5 是诺克萨斯之力。
pub const R_TIERS: [(usize, usize); 6] = [(100, 100), (120, 120), (140, 140), (160, 160), (180, 180), (200, 200)];
/// `R_TIERS` 里诺克萨斯之力那一档。
pub const MIGHT_TIER: usize = 5;
/// 诺克萨斯之力的攻击力加成 %（might 的 attack_mult）。
pub const MIGHT_ATTACK_MULT: usize = 40;
/// R 的施放距离。
pub const R_RANGE: usize = 46_000;
/// 从放出 R 到落刀的 tick（start_timing 4 + Delayed 22）：层数要撑到这时才算数。
pub const R_LAND: usize = 26;

/// 主包落刀那一下加在诺手身上的击杀标记（落刀前没有）。
pub const R_KILL: &str = "league_darius_r_kill";
/// 副本里 R 出手时给目标挂的标记（被动认大招目标用），挂 `MARK_TICKS` tick。
pub const MARK: &str = "league_darius_ult_mark";
pub const MARK_TICKS: usize = 40;

/// 诺手拿到人头（`on_kill`）时要不要把 R 还给他：R 在 `cast` tick 放出，死的是大招目标，还没落刀（`landed` = 身上已有
/// 主包的击杀标记，那一刀自己会刷新），离放出不超过 `R_LAND` tick。队友抢的人头游戏不算他的，不会走到这里。
pub fn own_kill_refund(now: usize, cast: Option<usize>, is_target: bool, landed: bool) -> bool {
    cast.is_some_and(|t| now >= t && now <= t + R_LAND) && is_target && !landed
}

/// 诺手自己：攻击力（读到的当前值）、诺克萨斯之力和每层出血还剩几 tick（没有就是 None）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Me {
    pub attack: usize,
    pub might_left: Option<usize>,
    pub hemo_left: [Option<usize>; 4],
}

impl Me {
    /// 落刀时还在的层数：诺克萨斯之力撑得到落刀就是 `MIGHT_TIER`，否则是撑得到的最高一层出血。
    pub fn stacks_at_blow(&self) -> usize {
        let lasts = |left: Option<usize>| left.is_some_and(|t| t > R_LAND);
        if lasts(self.might_left) {
            return MIGHT_TIER;
        }
        (1..=HEMO.len()).rev().find(|&k| lasts(self.hemo_left[k - 1])).unwrap_or(0)
    }

    /// 落刀时的攻击力：诺克萨斯之力撑不到落刀，就去掉它的加成。
    pub fn attack_at_blow(&self) -> usize {
        match self.might_left {
            Some(t) if t <= R_LAND => self.attack * 100 / (100 + MIGHT_ATTACK_MULT),
            _ => self.attack,
        }
    }

    /// 现在放 R，落刀时的真实伤害。
    pub fn r_damage(&self) -> usize {
        r_damage(self.stacks_at_blow(), self.attack_at_blow())
    }
}

/// `stacks` 层（`MIGHT_TIER` = 诺克萨斯之力）、攻击力 `attack` 时 R 的真实伤害（同引擎：固定值 + 攻击力 × % / 100）。
pub fn r_damage(stacks: usize, attack: usize) -> usize {
    let (base, ratio) = R_TIERS[stacks.min(MIGHT_TIER)];
    base + attack * ratio / 100
}

/// 一个敌方英雄：id、当前生命、护盾，身上有没有免死（R 砍不死他），和他身上 buff 的受到伤害增减（%，各自加总）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Foe {
    pub id: usize,
    pub hp: usize,
    pub shield: usize,
    pub undying: bool,
    /// `damaged_reduce` 之和：受到的伤害降低（R 的真实伤害也降）。
    pub reduce: usize,
    /// `damaged_amplify` 之和：受到的伤害提高（和 `reduce` 相加后一起乘）。
    pub amplify: usize,
    /// `skill_damaged_reduce` 之和：受到的技能伤害降低（R 是技能，再乘一次）。
    pub skill_reduce: usize,
}

impl Foe {
    /// 生命 + 护盾：真实伤害要先打穿护盾。
    pub fn ehp(&self) -> usize {
        self.hp + self.shield
    }

    /// R 的 `d` 点真实伤害落到他身上是多少（经典 SDK 的引擎里量的：减伤 50% 砍一半，减伤 50% + 增伤 50% 不变，
    /// 减伤 30% + 技能减伤 30% 剩 49%；两步各自取整）。
    pub fn damage_from(&self, d: usize) -> usize {
        let taken = (100 + self.amplify).saturating_sub(self.reduce);
        d * taken / 100 * 100usize.saturating_sub(self.skill_reduce) / 100
    }

    /// 伤害 `d` 的 R 砍得死他。
    pub fn dies_to(&self, d: usize) -> bool {
        !self.undying && self.damage_from(d) >= self.ehp()
    }
}

/// 砍得死的人里生命 + 护盾最少的。
pub fn best_kill(foes: &[Foe], d: usize) -> Option<Foe> {
    foes.iter().copied().filter(|f| f.dies_to(d)).min_by_key(|f| (f.ehp(), f.id))
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Plan {
    /// 照 AI 原来的输入（AI 想放的 R 能斩杀）。
    Keep,
    /// 放 R，砍这个人。
    Ult(usize),
    /// AI 想对这个人放 R，但砍不死（诺克萨斯之力期间也一样）：改成打他，继续叠层。
    Hold(usize),
}

/// 为什么放 / 不放（日志用）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Why {
    /// 砍得死。
    Kill,
    /// 砍不死。
    Wait,
    /// AI 的输入照旧（不是 R，或 R 好不了）。
    Pass,
}

/// `ai`：AI 原来的输入是 R 时它的目标；`ai_foe`：那个目标现在的样子（不论远近；不是活着的敌方英雄就是 None）；
/// `foes`：射程内现在能被 R 选中的敌方英雄；`ready`：R 好了、AI 没在放别的技能或回城（主动放 R 的前提）。
///
/// 只为斩杀放：诺克萨斯之力不单独放行，只是让这一刀伤害更高、更容易砍死人（用户：「改成只在能斩杀时放大，血怒不再单独
/// 放行」；放行时诺手常对着八九成血的人起手，日志里 67 刀只砍死 2 个）。
pub fn plan(ai: Option<usize>, ai_foe: Option<Foe>, foes: &[Foe], me: &Me, ready: bool) -> (Plan, Why) {
    let d = me.r_damage();
    let kill = best_kill(foes, d);
    match ai {
        Some(x) => {
            if ai_foe.is_some_and(|f| f.dies_to(d)) {
                (Plan::Keep, Why::Kill)
            } else if let Some(k) = kill {
                (Plan::Ult(k.id), Why::Kill)
            } else {
                (Plan::Hold(x), Why::Wait)
            }
        }
        None if !ready => (Plan::Keep, Why::Pass),
        None => match kill {
            Some(k) => (Plan::Ult(k.id), Why::Kill),
            None => (Plan::Keep, Why::Pass),
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn f(id: usize, hp: usize) -> Foe {
        Foe { id, hp, ..Foe::default() }
    }

    fn me(attack: usize, might_left: Option<usize>, top: usize) -> Me {
        let mut hemo_left = [None; 4];
        for (k, left) in hemo_left.iter_mut().enumerate().take(top) {
            *left = Some(100 + 60 * k);
        }
        Me { attack, might_left, hemo_left }
    }

    #[test]
    fn the_tiers_are_the_main_packs() {
        // 攻击 200：0 层 100 + 200 = 300，4 层 180 + 360 = 540，诺克萨斯之力 200 + 400 = 600
        assert_eq!(r_damage(0, 200), 300);
        assert_eq!(r_damage(4, 200), 540);
        assert_eq!(r_damage(MIGHT_TIER, 200), 600);
        assert_eq!(me(200, None, 3).r_damage(), 160 + 320);
    }

    #[test]
    fn stacks_must_last_until_the_blow() {
        assert_eq!(me(200, Some(300), 0).stacks_at_blow(), MIGHT_TIER);
        // 诺克萨斯之力落刀前就没了：0 层，攻击力去掉 40%
        let fading = me(280, Some(R_LAND), 0);
        assert_eq!(fading.stacks_at_blow(), 0);
        assert_eq!(fading.attack_at_blow(), 200);
        assert_eq!(fading.r_damage(), 300);
        // 第 3 层落刀前没了、第 2 层还在：按 2 层（层数按各自剩的时间算）
        let mut m = me(200, None, 0);
        m.hemo_left = [None, Some(200), Some(10), None];
        assert_eq!(m.stacks_at_blow(), 2);
        assert_eq!(me(200, None, 4).stacks_at_blow(), 4);
    }

    #[test]
    fn shields_and_undying_count() {
        let shielded = Foe { id: 1, hp: 250, shield: 100, ..Foe::default() };
        assert!(!shielded.dies_to(300));
        assert!(shielded.dies_to(350));
        let undying = Foe { id: 2, hp: 10, undying: true, ..Foe::default() };
        assert!(!undying.dies_to(10_000));
        assert_eq!(best_kill(&[shielded, undying, f(3, 400)], 500).map(|f| f.id), Some(1));
        // 减伤 50% 的 310 血：600 落到他身上只剩 300，砍不死；砍没减伤的 550 血
        let tough = Foe { id: 5, hp: 310, reduce: 50, ..Foe::default() };
        assert_eq!(best_kill(&[f(3, 550), tough], 600).map(|f| f.id), Some(3));
    }

    #[test]
    fn damage_taken_changes_follow_the_engine() {
        // 经典 SDK 的引擎里量到的（R 的真实伤害落到挂着测试 buff 的盖伦身上）
        let with = |reduce, amplify, skill_reduce| Foe { id: 1, hp: 1, reduce, amplify, skill_reduce, ..Foe::default() };
        assert_eq!(with(50, 0, 0).damage_from(424), 212);
        assert_eq!(with(80, 0, 0).damage_from(462), 92);
        assert_eq!(with(0, 0, 50).damage_from(524), 262);
        assert_eq!(with(50, 50, 0).damage_from(680), 680);
        assert_eq!(with(30, 0, 30).damage_from(392), 191);
        assert_eq!(with(30, 0, 30).damage_from(314), 153);
        assert_eq!(with(0, 50, 0).damage_from(300), 450);
        // 减到 0 以下按 0 算
        assert_eq!(with(150, 0, 0).damage_from(500), 0);
        assert_eq!(with(0, 0, 120).damage_from(500), 0);
        // 减伤 30%：300 只剩 210，250 血砍不死
        assert!(!Foe { id: 3, hp: 250, reduce: 30, ..Foe::default() }.dies_to(300));
        assert!(Foe { id: 3, hp: 210, reduce: 30, ..Foe::default() }.dies_to(300));
    }

    #[test]
    fn his_own_kill_before_the_blow_gives_r_back() {
        // 放出后 10 tick 他的流血把大招目标流死：还
        assert!(own_kill_refund(110, Some(100), true, false));
        // 落刀那一下砍死的：主包自己刷新，不重复
        assert!(!own_kill_refund(126, Some(100), true, true));
        // 死的不是大招目标、没在放 R、早过了落刀：不还
        assert!(!own_kill_refund(110, Some(100), false, false));
        assert!(!own_kill_refund(110, None, true, false));
        assert!(!own_kill_refund(100 + R_LAND + 1, Some(100), true, false));
    }

    #[test]
    fn r_only_for_a_kill() {
        let foes = [f(1, 900), f(2, 400), f(3, 280)];
        let none = me(200, None, 0); // 300 伤害
        // AI 想砍 1（砍不死）：改砍砍得死的 3
        assert_eq!(plan(Some(1), Some(foes[0]), &foes, &none, true), (Plan::Ult(3), Why::Kill));
        // AI 想砍 3（砍得死）：照旧
        assert_eq!(plan(Some(3), Some(foes[2]), &foes, &none, true), (Plan::Keep, Why::Kill));
        // 没人砍得死、层数不满：不放，改打他
        let tough = [f(1, 900), f(2, 400)];
        assert_eq!(plan(Some(1), Some(tough[0]), &tough, &none, true), (Plan::Hold(1), Why::Wait));
        // 4 层（540）就砍得死 2
        assert_eq!(plan(Some(1), Some(tough[0]), &tough, &me(200, None, 4), true), (Plan::Ult(2), Why::Kill));
        // 诺克萨斯之力（600）砍得死 2：改砍 2；谁都砍不死：不放，改打 AI 选的人
        let might = me(200, Some(200), 0);
        assert_eq!(plan(Some(1), Some(tough[0]), &tough, &might, true), (Plan::Ult(2), Why::Kill));
        let thick = [f(1, 900), f(2, 700)];
        assert_eq!(plan(Some(1), Some(thick[0]), &thick, &might, true), (Plan::Hold(1), Why::Wait));
        // AI 想砍的人有免死：诺克萨斯之力期间也不放
        let guarded = Foe { id: 1, hp: 900, undying: true, ..Foe::default() };
        assert_eq!(plan(Some(1), Some(guarded), &[guarded, f(2, 700)], &might, true), (Plan::Hold(1), Why::Wait));
        // AI 的目标不是活着的敌方英雄（已经死了）：没人砍得死就改打 / 走过去，不让 R 白放
        assert_eq!(plan(Some(9), None, &tough, &none, true), (Plan::Hold(9), Why::Wait));
        // AI 没想放：R 好了、有人砍得死就放；诺克萨斯之力期间没人砍得死不放
        assert_eq!(plan(None, None, &foes, &none, true), (Plan::Ult(3), Why::Kill));
        assert_eq!(plan(None, None, &thick, &might, true), (Plan::Keep, Why::Pass));
        assert_eq!(plan(None, None, &tough, &none, true), (Plan::Keep, Why::Pass));
        assert_eq!(plan(None, None, &foes, &none, false), (Plan::Keep, Why::Pass));
    }
}
