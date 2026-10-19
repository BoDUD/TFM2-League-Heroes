//! 0.2.0（用户 2026-10-19：「厄斐琉斯能做的像英雄联盟里面高手一样的逻辑吗」，选了全做：「Q 看武器和局面放、W 换到合适的武器、
//! 开大前先换好主手、通碧标记换手引爆」）：看局面的判断，纯逻辑（单元测试）。AI 钩子（`lib.rs` 的 `Hands`）按这里决定
//! Q 放不放、放给谁，W 换不换；被动（`Moon`）按这里决定直接换手。
//!
//! 距离都是中心距离（引擎判范围时还加两边的体积，所以这里比数据的射程宽一点）。

/// 五把武器的编号（`lib.rs` 的 WEAPONS 顺序）。
pub const CAL: usize = 0;
pub const SEV: usize = 1;
pub const GRAV: usize = 2;
pub const INF: usize = 3;
pub const CRE: usize = 4;

/// Q 的施放距离（数据 s_range 55000）加一点体积：按 Q 时目标要在这以内。
pub const Q_REACH: f64 = 65_000.0;
/// 断魄 Q 自动射击的范围（q_s_r）。
pub const SEV_R: f64 = 50_000.0;
/// 荧焰 Q 的扇形：半径（q_i_r）和半角的余弦（q_i_cone 600 = 53 度）。
pub const INF_R: f64 = 45_000.0;
pub const INF_COS: f64 = 0.6;
/// 折镜 Q：哨卫放在目标脚下，打它身边 q_r_r 以内；英雄在这以内才值得放。
pub const CRE_R: f64 = 45_000.0;
pub const CRE_SHOOT: f64 = 35_000.0;
/// 清线：这以内没有敌方英雄才拿 Q 打兵。
pub const LANE_CLEAR: f64 = 80_000.0;
/// 被贴脸：敌方英雄进到这以内。
pub const DIVE: f64 = 25_000.0;
/// 开大前看的范围（数据 r_range 90000）。
pub const R_LOOK: f64 = 90_000.0;
/// 被动自己换手的间隔（数据 W 的冷却 s2_cd 90）。
pub const SWAP_CD: usize = 90;

/// 一个敌方单位（防御塔不算）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: (f64, f64),
    pub champion: bool,
    /// 生命比例 0..1
    pub hp: f64,
    /// 身上有坠明的减速（`league_aphelios_g_slow` / `r_slow`）：标记还在（标记 150 tick，减速 60–90 tick）。
    pub marked: bool,
}

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn nearest<'a>(me: (f64, f64), foes: impl Iterator<Item = &'a Foe>) -> Option<&'a Foe> {
    foes.min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at)))
}

fn champs_within(me: (f64, f64), foes: &[Foe], r: f64) -> Vec<&Foe> {
    foes.iter().filter(|f| f.champion && dist(me, f.at) <= r).collect()
}

/// 朝 `toward` 的扇形（半径 r、半角余弦 cos）里有几个满足 `pick` 的单位。
fn in_cone(me: (f64, f64), toward: (f64, f64), foes: &[Foe], r: f64, cos: f64, pick: impl Fn(&Foe) -> bool) -> usize {
    let d = dist(me, toward);
    if d < 1.0 {
        return foes.iter().filter(|f| pick(f) && dist(me, f.at) <= r).count();
    }
    let dir = ((toward.0 - me.0) / d, (toward.1 - me.1) / d);
    foes.iter()
        .filter(|f| pick(f))
        .filter(|f| {
            let e = dist(me, f.at);
            e <= r && (e < 1.0 || ((f.at.0 - me.0) * dir.0 + (f.at.1 - me.1) * dir.1) / e >= cos)
        })
        .count()
}

/// 清线：附近没有敌方英雄时，离自己 `r` 以内（以某个兵为中心 `around` 以内）的小兵野怪够 `n` 个就给出最近的那个。
fn lane_target(me: (f64, f64), foes: &[Foe], r: f64, around: f64, n: usize) -> Option<usize> {
    if !champs_within(me, foes, LANE_CLEAR).is_empty() {
        return None;
    }
    let minions: Vec<&Foe> = foes.iter().filter(|f| !f.champion && dist(me, f.at) <= r).collect();
    minions
        .iter()
        .filter(|m| minions.iter().filter(|o| dist(m.at, o.at) <= around).count() >= n)
        .min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at)))
        .map(|m| m.id)
}

/// 主手是 `main`（副手 `off`）时 Q 该不该放、放给谁、为什么。英雄联盟高手的用法：
/// - 通碧·狙杀：只打英雄（远程消耗，打中的标记会被引爆），不拿来打兵；
/// - 断魄·恒月强袭：和英雄打起来时（自己掉血、对面残血或两个英雄在身边）放，回血加移速；清线要一大波兵；
/// - 坠明·引力枷锁：有英雄带着标记就放（定住所有带标记的），没有就留着；
/// - 荧焰·余晖波：扇形里两个英雄，或一个英雄而副手是折镜 / 通碧（每个打中的再吃一发副手）、或他残血；清线三个兵；
/// - 折镜·驻灵哨卫：英雄在身边才放（哨卫在他脚下打 35000 以内），清线要一堆兵。
pub fn q_plan(main: usize, off: usize, me: (f64, f64), my_hp: f64, foes: &[Foe]) -> Option<(usize, &'static str)> {
    let near = |r: f64| nearest(me, foes.iter().filter(|f| f.champion && dist(me, f.at) <= r));
    match main {
        CAL => near(Q_REACH).map(|f| (f.id, "Moonshot at a champion")),
        SEV => {
            let champs = champs_within(me, foes, SEV_R);
            let fight = !champs.is_empty() && (my_hp < 0.7 || champs.len() >= 2 || champs.iter().any(|f| f.hp < 0.5));
            if fight {
                return near(SEV_R).map(|f| (f.id, "Onslaught in a fight"));
            }
            lane_target(me, foes, SEV_R, SEV_R, 4).map(|t| (t, "Onslaught on a wave"))
        }
        GRAV => {
            // the root takes every marked unit wherever it is; the cast needs some enemy in reach
            foes.iter().any(|f| f.champion && f.marked && dist(me, f.at) <= R_LOOK).then_some(())?;
            let t = nearest(me, foes.iter().filter(|f| f.champion && f.marked && dist(me, f.at) <= Q_REACH))
                .or_else(|| nearest(me, foes.iter().filter(|f| dist(me, f.at) <= Q_REACH)))?;
            Some((t.id, "Binding Eclipse on a marked champion"))
        }
        INF => {
            let mut best: Option<(&Foe, usize)> = None;
            for c in champs_within(me, foes, INF_R) {
                let n = in_cone(me, c.at, foes, INF_R, INF_COS, |f| f.champion);
                if best.is_none_or(|b| n > b.1) {
                    best = Some((c, n));
                }
            }
            if let Some((c, n)) = best {
                if n >= 2 {
                    return Some((c.id, "Duskwave through two champions"));
                }
                if off == CRE || off == CAL || c.hp < 0.5 {
                    return Some((c.id, "Duskwave with the off hand's follow-ups"));
                }
                return None;
            }
            let t = lane_target(me, foes, INF_R, INF_R, 3)?;
            let at = foes.iter().find(|f| f.id == t)?.at;
            (in_cone(me, at, foes, INF_R, INF_COS, |f| !f.champion) >= 3).then_some((t, "Duskwave on a wave"))
        }
        CRE => near(CRE_R)
            .map(|f| (f.id, "Sentry at a champion close"))
            .or_else(|| lane_target(me, foes, Q_REACH, CRE_SHOOT, 4).map(|t| (t, "Sentry on a wave"))),
        _ => None,
    }
}

/// 大招打出去时主手给的「礼物」在团战里的分（越大越好）：荧焰的大范围伤害、残血时断魄的回血、坠明的减速加标记（接 Q
/// 定身）、通碧的补枪、折镜的飞轮（近身才用得上）。
pub fn r_score(w: usize, my_hp: f64) -> u32 {
    match w {
        INF => 5,
        SEV if my_hp < 0.5 => 6,
        GRAV => 4,
        SEV => 3,
        CAL => 2,
        _ => 1,
    }
}

/// 被动这一刻要不要直接换手（主手和副手互换），为什么。按先后：
/// 1. 大招准备好了（`r_armed`）、附近有敌方英雄：副手的礼物更好就先换上；
/// 2. 通碧的 Q 刚射出去（`cal_cast`）：换上副手，标记被引爆时带副手的命中效果，接着放副手的 Q（坠明定身、荧焰……）；
/// 3. 主手 Q 在冷却、副手 Q 好了、而且副手的 Q 现在正合适：换手接 Q；
/// 4. 被英雄贴脸：副手是折镜（Q 好了）或坠明（有带标记的英雄、Q 好了），主手不是这几把、也不是断魄，就换。
pub struct Swap {
    pub main: usize,
    pub off: usize,
    pub main_q: bool,
    pub off_q: bool,
    pub r_armed: bool,
    pub cal_cast: bool,
}

pub fn swap_plan(s: &Swap, me: (f64, f64), my_hp: f64, foes: &[Foe]) -> Option<&'static str> {
    let champs = |r: f64| champs_within(me, foes, r).len();
    if s.r_armed && champs(R_LOOK) > 0 && r_score(s.off, my_hp) > r_score(s.main, my_hp) {
        return Some("R armed: the better gift in the main hand");
    }
    if s.cal_cast && s.main == CAL && champs(Q_REACH + 20_000.0) > 0 {
        return Some("Moonshot away: the off hand pops the mark");
    }
    if !s.main_q && s.off_q && q_plan(s.off, s.main, me, my_hp, foes).is_some() {
        return Some("Q down: the off hand's Q fits now");
    }
    let marked = foes.iter().any(|f| f.champion && f.marked);
    let close = matches!(s.main, CRE | GRAV | SEV);
    if !close && champs(DIVE) > 0 && s.off_q && (s.off == CRE || (s.off == GRAV && marked)) {
        return Some("dived: the close weapon in hand");
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    fn champ(id: usize, x: f64, hp: f64) -> Foe {
        Foe { id, at: (x, 0.0), champion: true, hp, marked: false }
    }

    fn minion(id: usize, x: f64, y: f64) -> Foe {
        Foe { id, at: (x, y), champion: false, hp: 1.0, marked: false }
    }

    const ME: (f64, f64) = (0.0, 0.0);

    #[test]
    fn calibrum_only_at_champions() {
        assert_eq!(q_plan(CAL, SEV, ME, 1.0, &[minion(5, 20000.0, 0.0)]), None);
        assert_eq!(q_plan(CAL, SEV, ME, 1.0, &[minion(5, 20000.0, 0.0), champ(1, 60000.0, 1.0)]).map(|q| q.0), Some(1));
        assert_eq!(q_plan(CAL, SEV, ME, 1.0, &[champ(1, 90000.0, 1.0)]), None);
    }

    #[test]
    fn severum_in_a_fight_or_on_a_big_wave() {
        let full = [champ(1, 30000.0, 1.0)];
        assert_eq!(q_plan(SEV, CAL, ME, 1.0, &full), None); // a poke at full health: keep it
        assert_eq!(q_plan(SEV, CAL, ME, 0.6, &full).map(|q| q.0), Some(1));
        assert_eq!(q_plan(SEV, CAL, ME, 1.0, &[champ(1, 30000.0, 0.4)]).map(|q| q.0), Some(1));
        let wave: Vec<Foe> = (0..4).map(|i| minion(10 + i, 20000.0 + 3000.0 * i as f64, 0.0)).collect();
        assert_eq!(q_plan(SEV, CAL, ME, 1.0, &wave).map(|q| q.0), Some(10));
        assert_eq!(q_plan(SEV, CAL, ME, 1.0, &wave[..3]), None);
    }

    #[test]
    fn gravitum_waits_for_a_marked_champion() {
        let mut c = champ(1, 50000.0, 1.0);
        assert_eq!(q_plan(GRAV, CAL, ME, 1.0, &[c]), None);
        c.marked = true;
        assert_eq!(q_plan(GRAV, CAL, ME, 1.0, &[c]).map(|q| q.0), Some(1));
        // marked but out of reach: any enemy in reach carries the cast
        c.at = (80000.0, 0.0);
        assert_eq!(q_plan(GRAV, CAL, ME, 1.0, &[c, minion(7, 20000.0, 0.0)]).map(|q| q.0), Some(7));
    }

    #[test]
    fn infernum_through_two_or_with_follow_ups() {
        let two = [champ(1, 30000.0, 1.0), champ(2, 40000.0, 1.0)];
        assert_eq!(q_plan(INF, SEV, ME, 1.0, &two).map(|q| q.1), Some("Duskwave through two champions"));
        // the two on opposite sides: only one in the cone
        let apart = [champ(1, 30000.0, 1.0), champ(2, -30000.0, 1.0)];
        assert_eq!(q_plan(INF, SEV, ME, 1.0, &apart), None);
        assert!(q_plan(INF, CRE, ME, 1.0, &apart[..1]).is_some());
        assert!(q_plan(INF, SEV, ME, 1.0, &[champ(1, 30000.0, 0.3)]).is_some());
        let wave = [minion(5, 20000.0, 0.0), minion(6, 25000.0, 2000.0), minion(7, 30000.0, -2000.0)];
        assert_eq!(q_plan(INF, SEV, ME, 1.0, &wave).map(|q| q.0), Some(5));
    }

    #[test]
    fn the_sentry_close_or_on_a_crowd() {
        assert!(q_plan(CRE, SEV, ME, 1.0, &[champ(1, 40000.0, 1.0)]).is_some());
        assert_eq!(q_plan(CRE, SEV, ME, 1.0, &[champ(1, 60000.0, 1.0)]), None);
    }

    #[test]
    fn the_swaps_in_their_order() {
        let fight = [champ(1, 40000.0, 1.0), champ(2, 45000.0, 1.0)];
        let s = |main, off, main_q, off_q, r_armed, cal_cast| Swap { main, off, main_q, off_q, r_armed, cal_cast };
        assert_eq!(swap_plan(&s(CRE, INF, true, true, true, false), ME, 1.0, &fight), Some("R armed: the better gift in the main hand"));
        assert_eq!(swap_plan(&s(INF, CRE, true, true, true, false), ME, 1.0, &fight), None);
        assert_eq!(swap_plan(&s(CAL, GRAV, false, true, false, true), ME, 1.0, &[champ(1, 70000.0, 1.0)]),
                   Some("Moonshot away: the off hand pops the mark"));
        assert_eq!(swap_plan(&s(CAL, INF, false, true, false, false), ME, 1.0, &fight), Some("Q down: the off hand's Q fits now"));
        assert_eq!(swap_plan(&s(CAL, INF, false, false, false, false), ME, 1.0, &fight), None);
        assert_eq!(swap_plan(&s(CAL, CRE, true, true, false, false), ME, 1.0, &[champ(1, 20000.0, 1.0)]),
                   Some("dived: the close weapon in hand"));
        assert_eq!(swap_plan(&s(SEV, CRE, true, true, false, false), ME, 1.0, &[champ(1, 20000.0, 1.0)]), None);
    }

    #[test]
    fn low_health_wants_severum_in_the_ult() {
        assert!(r_score(SEV, 0.3) > r_score(INF, 0.3));
        assert!(r_score(INF, 0.9) > r_score(SEV, 0.9));
    }
}
