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

/// 这个 buff 算不算「杀不死」：带「不死」，但别的附加包一直挂着的被动护身（名字以 `_p_guard` / `_rv_guard` 结尾：死歌、塞恩、
/// 艾尼维亚、扎克、扎恩、tft 的石甲虫）不算——英雄联盟里处决他们照样算击杀，他们死进自己的被动里（2026-11-05 复查：死歌被动
/// 好着就一直「杀不死」）。千珏的大招、基兰的符文、凯尔的大招等真的杀不死，照样等。league_renata 的救难也是这个顺序。
pub fn holds_execute(name: &str, undying: bool) -> bool {
    undying && !name.ends_with("_p_guard") && !name.ends_with("_rv_guard")
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

/// While he casts (E's 3-second spin: the cast animation, game 0.6.4's `Animation`), is moved (`ForceMove`) or held by
/// crowd control that stops a cast, the engine takes no R (0.1.2; the 11-06 log: one press pressed for 120+ ticks): the hook
/// presses none of its own. The AI's own R is still held when it would not kill: `Ult` of another becomes a hold of the
/// AI's target.
pub fn quiet(p: Plan, ai: Option<usize>) -> Plan {
    match p {
        Plan::Ult(_) => ai.map_or(Plan::Keep, Plan::Hold),
        p => p,
    }
}

/// A press of R the engine has not taken for this many ticks gets its line (0.1.2).
pub const NOT_TAKEN: usize = 30;

/// The hook's press of R (0.1.2): since when, at whom, whether its `R NOT TAKEN` line is out.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Press {
    pub since: usize,
    pub target: usize,
    pub told: bool,
}

/// One think of the press watch: `pressing` = the hook presses R at this champion now, `cooling` = R's cooldown runs (the
/// press was taken). Some(ticks pressed) once a press has gone `NOT_TAKEN` ticks untaken - its line, once.
pub fn watch_press(press: &mut Option<Press>, pressing: Option<usize>, cooling: bool, now: usize) -> Option<usize> {
    let Some(t) = pressing.filter(|_| !cooling) else {
        *press = None;
        return None;
    };
    let p = press.get_or_insert(Press { since: now, target: t, told: false });
    if p.target != t {
        *p = Press { since: now, target: t, told: false };
    }
    if !p.told && now >= p.since + NOT_TAKEN {
        p.told = true;
        return Some(now - p.since);
    }
    None
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

    #[test]
    fn no_press_while_he_spins_and_an_untaken_press_is_told() {
        // 11-06's logs: R KILL at t=16698 and again at 16818 (LOG_EVERY 120), R still ready - not taken for 120+ ticks,
        // likely inside E's 180-tick spin
        assert_eq!(quiet(Plan::Ult(2), None), Plan::Keep, "nothing of his own pressed");
        assert_eq!(quiet(Plan::Ult(2), Some(1)), Plan::Hold(1), "the AI's R at one it would not kill: still held");
        assert_eq!(quiet(Plan::Keep, Some(1)), Plan::Keep, "the AI's R that kills goes");
        assert_eq!(quiet(Plan::Hold(1), Some(1)), Plan::Hold(1));
        let mut p = None;
        assert_eq!(watch_press(&mut p, Some(21), false, 16_698), None);
        assert_eq!(watch_press(&mut p, Some(21), false, 16_698 + NOT_TAKEN - 1), None);
        assert_eq!(watch_press(&mut p, Some(21), false, 16_698 + NOT_TAKEN), Some(NOT_TAKEN), "told once");
        assert_eq!(watch_press(&mut p, Some(21), false, 16_818), None);
        // taken: R's cooldown runs - the watch ends
        assert_eq!(watch_press(&mut p, None, true, 16_819), None);
        assert_eq!(p, None);
        // another target starts a new press; a tick without a press ends it
        assert_eq!(watch_press(&mut p, Some(21), false, 20_000), None);
        assert_eq!(watch_press(&mut p, Some(454), false, 20_010), None);
        assert_eq!(p.map(|x| (x.since, x.target)), Some((20_010, 454)));
        assert_eq!(watch_press(&mut p, None, false, 20_011), None);
        assert_eq!(p, None);
    }

    #[test]
    fn a_passive_guard_does_not_make_him_unkillable() {
        // 11-05 review: Karthus / Sion / Anivia / Zac / Zaahen / Krug keep a permanent *_p_guard / *_rv_guard; League
        // counts an execute on them as a kill (they die into the passive)
        for g in ["league_karthus_p_guard", "league_sion_p_guard", "league_anivia_p_guard", "league_zac_p_guard",
                  "league_zaahen_rv_guard", "tft_krug_p_guard"] {
            assert!(!holds_execute(g, true), "{g}");
        }
        assert!(holds_execute("league_kindred_r_on", true));
        assert!(holds_execute("league_zilean_r_rune", true));
        assert!(holds_execute("league_karthus_p_spirit", true));
        assert!(!holds_execute("league_kindred_r_on", false));
    }
}
