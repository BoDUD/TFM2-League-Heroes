//! 米利欧附加包的规则本身（不碰 SDK）：`lib.rs` 用它，离线模拟器（经典 SDK 的 game_core 0.5.1）也直接编进同一份文件，
//! 两边按同一套规则算——被动烧多少、友方这一下打中了谁、谁快要阵亡要不要放 R。

// ===================== 热情洋溢！ =====================

/// TFM2 英雄的等级上限（game_setting 的 need_exp 11 级台阶，凯尔的升阶也按 12 级换算）。
pub const TOP_LEVEL: usize = 12;

/// 被动的数字（英雄数据 `passive.params`，`make_override.py` 写进去）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 灼烧总伤害：1 级 `burn_lo`、满级 `burn_hi`（英雄联盟 1-18 级 20-100，按 TFM2 的 1-12 级线性换算）。
    pub burn_lo: usize,
    pub burn_hi: usize,
    /// 灼烧持续 `burn_t` tick（1.5 秒），每 `burn_p` tick 一段。
    pub burn_t: usize,
    pub burn_p: usize,
    /// 对野怪（野区营地、大小龙）一次灼烧最多这么多（英雄联盟 MaxMonsterDamage 100）。
    pub mon_cap: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { burn_lo: 20, burn_hi: 100, burn_t: 90, burn_p: 15, mon_cap: 100 }
    }
}

/// 英雄数据 `passive.params` 的 JSON（键排好序、值是整数）。缺的键用默认值。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k.trim().trim_matches('"') {
            "burn_lo" => p.burn_lo = v,
            "burn_hi" => p.burn_hi = v,
            "burn_t" => p.burn_t = v,
            "burn_p" => p.burn_p = v.max(1),
            "mon_cap" => p.mon_cap = v,
            _ => {}
        }
    }
    p
}

/// 米利欧 `level` 级时一次灼烧的总伤害（魔法伤害，减免前）。
pub fn burn_total(p: &Params, level: usize) -> usize {
    let lv = level.clamp(1, TOP_LEVEL);
    p.burn_lo + p.burn_hi.saturating_sub(p.burn_lo) * (lv - 1) / (TOP_LEVEL - 1)
}

/// 一次灼烧的各段：(命中后第几 tick, 伤害)。分 `burn_t / burn_p` 段，除不尽的零头加在最后一段；对野怪总量不超过 `mon_cap`。
pub fn burn_parts(p: &Params, level: usize, monster: bool) -> Vec<(usize, usize)> {
    let mut total = burn_total(p, level);
    if monster {
        total = total.min(p.mon_cap);
    }
    let n = (p.burn_t / p.burn_p.max(1)).max(1);
    let each = total / n;
    let rest = total - each * n;
    (1..=n)
        .map(|k| (k * p.burn_p.max(1), each + if k == n { rest } else { 0 }))
        .filter(|part| part.1 > 0)
        .collect()
}

// ===================== 友方这一下打中了谁 =====================

/// 友方的冷却计数比上一 tick 跳高了：这个栏位刚用掉（布隆附加包看友军普攻的办法）。
pub fn used(was: usize, now: usize) -> bool {
    now > was + 5
}

/// 一次普攻 / 技能开始后最多等多久看它打中谁（经典引擎里普攻的目标 40 tick 内都掉了血）。
pub const ATTACK_WAIT: usize = 45;
pub const SKILL_WAIT: usize = 60;
/// 友方这么远以内掉血的敌人才可能是它打的。
pub const REACH: f64 = 95_000.0;
/// 友方的投射物离掉血的敌人这么近，就算是它打中的。
pub const SHOT_NEAR: f64 = 15_000.0;
/// 没有命令目标时，掉的血（加护盾）至少是友方攻击力的这么多 % 才算它这一下（小兵、塔的零碎伤害不算）。
pub const MIN_SHARE: usize = 25;

/// 正在等结果的一次出手。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Swing {
    pub start: usize,
    pub until: usize,
    /// AI 下令打的那个敌人（观察钩子记下的）；`None` = 不知道，按掉血猜。
    pub target: Option<usize>,
    /// 普攻（`false` = 技能）。
    pub attack: bool,
}

/// 这一 tick 掉了血或护盾的一个敌人。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Drop {
    pub id: usize,
    /// 离友方多远。
    pub dist: f64,
    /// 掉了多少（生命 + 护盾）。
    pub amount: usize,
    /// 友方的一个投射物就在它身边（`SHOT_NEAR` 以内）。
    pub by_shot: bool,
}

/// 这一 tick 友方这次出手打中了谁：知道命令目标时，就看它掉没掉血；不知道时，在 `REACH` 以内、掉得够多（`min_amount`）的
/// 敌人里，先看身边有它投射物的，再取离它最近的。经典引擎里量过（10 分钟一局，基础英雄混战）：只取出手时最近的敌人
/// 对 66% / 72%（目标是英雄 / 其他），这样猜 80-84% / 90-91%；有命令目标时 98%。
pub fn hit_of(target: Option<usize>, drops: &[Drop], min_amount: usize) -> Option<usize> {
    if let Some(t) = target {
        return drops.iter().any(|d| d.id == t).then_some(t);
    }
    let pool: Vec<&Drop> = drops.iter().filter(|d| d.amount >= min_amount && d.dist <= REACH).collect();
    let shot: Vec<&Drop> = pool.iter().copied().filter(|d| d.by_shot).collect();
    let from = if shot.is_empty() { pool } else { shot };
    from.into_iter().min_by(|a, b| a.dist.total_cmp(&b.dist).then(a.id.cmp(&b.id))).map(|d| d.id)
}

/// 没有命令目标时，掉多少血才算友方这一下：普攻 `MIN_SHARE`% 攻击力；技能按攻击力和法强里大的那个。
pub fn min_amount(attack: bool, atk: usize, ap: usize) -> usize {
    MIN_SHARE * if attack { atk } else { atk.max(ap) } / 100
}

// ===================== 他自己的灼烧不算谁打中的 =====================
// 游戏 0.6.4 的 deal_damage_typed 只把伤害排进效果队列（2026-10-17 反汇编）：打出去以后马上读生命还是原来的，下一 tick 才扣血，
// 也是那时才触发他的 on_attack（0.1.1 的日志：同一个目标上他的「own hit」22 次都正好在上一次点燃后 15k+1 tick，友方「ordered at
// it」打在烧着的目标上的 9 次里 6 次也是）。所以被动记下上一次 on_update 打给每个目标的灼烧，看掉血、看他的 on_attack 时先认出它。

/// 他的一跳灼烧最多让目标掉多少：减免前的伤害再加一半。魔抗只会让它变小；让人多受伤害的 `damaged_amplify`（主包里一层 10-15%）
/// 几个叠在一起也到不了一半。
pub fn burn_cap(burned: usize) -> usize {
    burned + burned / 2
}

/// 一个敌方单位从上一 tick 到这一 tick 掉了多少（生命 + 护盾；`now` 为 `None` = 它死了，剩的全算掉了），扣掉他上一 tick 打给它的
/// 灼烧 `burned`（减免前，按 `burn_cap` 扣足）。被灼烧这一跳烧死的也不算掉血。
pub fn lost(was: usize, now: Option<usize>, burned: usize) -> usize {
    was.saturating_sub(now.unwrap_or(0)).saturating_sub(burn_cap(burned))
}

/// 主包米利欧 1 级的攻击力（build_milio 的 atk）：他自己最弱的一下真打（普攻 100% 攻击力；Q 120 起）。
pub const HIS_ATTACK: usize = 85;

/// 他的 on_attack 收到的这一下是不是他自己的灼烧（上一次 on_update 打给这个目标的共 `burned`，减免前）。他自己真的打中都比一跳
/// 灼烧大得多（`HIS_ATTACK` 起，灼烧一跳最多 20）。
pub fn own_burn(damage: usize, burned: usize) -> bool {
    burned > 0 && damage <= burn_cap(burned)
}

// ===================== 生生不息：什么时候放 =====================

/// 主包 R 的施放距离（r_arm_range）：这么近有敌方英雄才放得出（R 的施放目标是 `EnemyChampion`）。
pub const R_CAST_RANGE: f64 = 75_000.0;
/// 主包 R 的半径（r_r）、放出后第几 tick 生效（r_rel）。
pub const R_RADIUS: f64 = 75_000.0;
pub const R_REL: usize = 20;
/// 他这么近的友方英雄算在 R 里（比半径小一圈：生效前那 `R_REL` tick 人还会走）。
pub const IN_CIRCLE: f64 = 65_000.0;
/// 危险：这么近有敌方英雄，而且被控制着（还剩 `CC_MIN` tick 以上）、生命比例不到 `DANGER_HP`，或 `BURST_T` tick 内掉了
/// `BURST` 以上、只剩 `BURST_LEFT` 以下。
pub const DANGER_NEAR: f64 = 45_000.0;
pub const DANGER_HP: f64 = 0.30;
pub const BURST: f64 = 0.30;
pub const BURST_LEFT: f64 = 0.60;
pub const BURST_T: usize = 60;
/// 控制还要这么久才值得解（R 生效时还没结束）。
pub const CC_MIN: usize = R_REL + 10;
/// 放出后隔多少 tick 看结果。
pub const CHECK_AT: usize = R_REL + 10;
/// R 从这一级起能放（同 league_kindred、league_darius_ult）。
pub const ULT_LEVEL: usize = 5;
/// 他的普攻射程（主包 atk_range）：AI 想放 R 又没人危险时，这么近的敌方英雄改成普攻它。
pub const ATTACK_RANGE: f64 = 53_000.0;

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一个友方英雄（含他自己）：id、位置、生命比例、`BURST_T` tick 内最多掉了多少（比例）、身上有没有别人给的不死、
/// 身上最长的硬控还剩几 tick（0 = 没有）。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Ally {
    pub id: usize,
    pub at: (f64, f64),
    pub hp: f64,
    pub drop: f64,
    pub undying: bool,
    pub cc: usize,
}

/// 为什么救他。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Why {
    /// 生命不到 `DANGER_HP`。
    Low,
    /// `BURST_T` tick 内被打掉一大截。
    Burst,
    /// 被控制着。
    Cc,
}

impl Why {
    pub fn word(self) -> &'static str {
        match self {
            Why::Low => "LOW HP",
            Why::Burst => "BURST",
            Why::Cc => "CC",
        }
    }
}

/// 他危险吗：`DANGER_NEAR` 内有敌方英雄，且生命低 / 刚被打掉一大截 / 被控制着；别人的不死在身上时不算。
pub fn danger(a: &Ally, enemies: &[(f64, f64)]) -> Option<Why> {
    if a.undying || !enemies.iter().any(|e| dist(a.at, *e) <= DANGER_NEAR) {
        return None;
    }
    if a.hp <= DANGER_HP {
        Some(Why::Low)
    } else if a.drop >= BURST && a.hp <= BURST_LEFT {
        Some(Why::Burst)
    } else if a.cc >= CC_MIN {
        Some(Why::Cc)
    } else {
        None
    }
}

/// 他在 `me`：`IN_CIRCLE` 内危险的友方英雄（含他自己）里生命比例最低的那个，和原因。
pub fn pick_save(me: (f64, f64), allies: &[Ally], enemies: &[(f64, f64)]) -> Option<(Ally, Why)> {
    allies
        .iter()
        .filter(|a| dist(me, a.at) <= IN_CIRCLE)
        .filter_map(|a| danger(a, enemies).map(|w| (*a, w)))
        .min_by(|a, b| a.0.hp.total_cmp(&b.0.hp).then(a.0.id.cmp(&b.0.id)))
}

/// 生命历史 `(tick, 比例)`（旧的在前）-> 现在的比例往前 `BURST_T` tick 内掉了多少。
pub fn drop_of(history: &[(usize, f64)], now_tick: usize, now_hp: f64) -> f64 {
    history.iter().filter(|(t, _)| t + BURST_T >= now_tick).map(|p| p.1).fold(now_hp, f64::max) - now_hp
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_burn_grows_with_his_level() {
        let p = Params::default();
        assert_eq!(burn_total(&p, 1), 20);
        assert_eq!(burn_total(&p, 12), 100);
        assert_eq!(burn_total(&p, 6), 20 + 80 * 5 / 11);
        assert_eq!(burn_total(&p, 0), 20);
        assert_eq!(burn_total(&p, 30), 100);
    }

    #[test]
    fn the_burn_comes_in_six_parts_over_90_ticks() {
        let p = Params::default();
        let parts = burn_parts(&p, 12, false);
        assert_eq!(parts.len(), 6);
        assert_eq!(parts.iter().map(|x| x.1).sum::<usize>(), 100);
        assert_eq!(parts.first().unwrap().0, 15);
        assert_eq!(parts.last().unwrap().0, 90);
        // 23 at level 1.5-ish: 3 each and the remainder at the end
        let p2 = Params { burn_lo: 23, ..p };
        let parts = burn_parts(&p2, 1, false);
        assert_eq!(parts.iter().map(|x| x.1).sum::<usize>(), 23);
        assert_eq!(parts.last().unwrap().1, 3 + 5);
        // monsters: never more than mon_cap in all
        let big = Params { burn_hi: 300, ..p };
        assert_eq!(burn_parts(&big, 12, true).iter().map(|x| x.1).sum::<usize>(), 100);
        assert_eq!(burn_parts(&big, 12, false).iter().map(|x| x.1).sum::<usize>(), 300);
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"burn_hi":100,"burn_lo":20,"burn_p":15,"burn_t":90,"mon_cap":100}"#);
        assert_eq!(p, Params::default());
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"burn_p":0}"#).burn_p, 1);
    }

    fn drop(id: usize, dist: f64, amount: usize, by_shot: bool) -> Drop {
        Drop { id, dist, amount, by_shot }
    }

    #[test]
    fn an_order_target_is_hit_when_it_drops() {
        let drops = [drop(4, 20_000.0, 50, false), drop(9, 60_000.0, 80, false)];
        assert_eq!(hit_of(Some(9), &drops, 0), Some(9));
        assert_eq!(hit_of(Some(7), &drops, 0), None); // the ordered one did not drop yet
    }

    #[test]
    fn without_an_order_the_shot_then_the_nearest_wins() {
        let drops = [drop(4, 20_000.0, 50, false), drop(9, 60_000.0, 80, true), drop(5, 10_000.0, 5, false)];
        assert_eq!(hit_of(None, &drops, 20), Some(9)); // its projectile was next to #9
        let no_shot = [drop(4, 20_000.0, 50, false), drop(9, 60_000.0, 80, false), drop(5, 10_000.0, 5, false)];
        assert_eq!(hit_of(None, &no_shot, 20), Some(4)); // #5 lost too little
        assert_eq!(hit_of(None, &no_shot, 0), Some(5));
        assert_eq!(hit_of(None, &[drop(3, REACH + 1.0, 500, true)], 0), None);
        assert_eq!(min_amount(true, 200, 900), 50);
        assert_eq!(min_amount(false, 200, 900), 225);
        assert!(used(0, 60) && !used(30, 33) && !used(60, 59));
    }

    #[test]
    fn his_burn_landing_is_no_drop() {
        // the tick after a 12 burn part was dealt: magic resistance shrinks it, damaged_amplify grows it, still his
        assert_eq!(lost(500, Some(490), 12), 0);
        assert_eq!(lost(500, Some(486), 12), 0);
        assert_eq!(lost(500, Some(482), 12), 0);
        // an ally's hit landed on the same tick: past the burn, it is still a drop
        assert_eq!(lost(500, Some(430), 12), 70 - 18);
        // the burn finished it off: no drop; a hit finished it: a drop
        assert_eq!(lost(9, None, 12), 0);
        assert_eq!(lost(60, None, 12), 60 - 18);
        // nothing of his burning on it: every drop counts, as before
        assert_eq!(lost(500, Some(490), 0), 10);
        assert_eq!(lost(80, None, 0), 80);
        assert_eq!(lost(500, Some(520), 0), 0);
    }

    #[test]
    fn an_ally_ordered_at_a_burning_target_waits_for_its_own_hit() {
        // 0.1.1 compared health only (`burned` 0): the burn's own tick passed for the ally's hit and spent its mark early
        let drops = |burned: usize| -> Vec<Drop> {
            [(7, lost(500, Some(490), burned))].iter().filter(|d| d.1 > 0).map(|&(id, amount)| drop(id, 30_000.0, amount, false)).collect()
        };
        assert_eq!(hit_of(Some(7), &drops(0), 0), Some(7));
        assert_eq!(hit_of(Some(7), &drops(12), 0), None);
        assert_eq!(hit_of(None, &drops(12), 0), None);
        // its own hit, on that tick or a later one, still counts
        let hit = [drop(7, 30_000.0, lost(500, Some(420), 12), false)];
        assert_eq!(hit_of(Some(7), &hit, 0), Some(7));
    }

    #[test]
    fn his_on_attack_knows_his_burn() {
        // the part as dealt, after magic resistance, amplified
        assert!(own_burn(12, 12) && own_burn(9, 12) && own_burn(18, 12));
        assert!(!own_burn(19, 12));
        // nothing of his burning on that target
        assert!(!own_burn(12, 0));
        // two parts due on one tick (an update came late): both his
        assert!(own_burn(16, 36) && own_burn(20, 36));
        // his weakest real hit (a level-1 attack) never passes for the biggest part (level 12)
        let top = burn_parts(&Params::default(), TOP_LEVEL, false).iter().map(|x| x.1).max().unwrap();
        assert!(top <= 20 && !own_burn(HIS_ATTACK, top));
    }

    fn ally(id: usize, x: f64, hp: f64, drop: f64, cc: usize) -> Ally {
        Ally { id, at: (x, 0.0), hp, drop, undying: false, cc }
    }

    #[test]
    fn danger_needs_an_enemy_and_low_health_a_burst_or_cc() {
        let near = [(30_000.0, 0.0)];
        assert_eq!(danger(&ally(1, 0.0, 0.25, 0.0, 0), &near), Some(Why::Low));
        assert_eq!(danger(&ally(1, 0.0, 0.25, 0.0, 0), &[(60_000.0, 0.0)]), None); // nobody close
        assert_eq!(danger(&ally(1, 0.0, 0.45, 0.0, 0), &near), None);
        assert_eq!(danger(&ally(1, 0.0, 0.55, 0.35, 0), &near), Some(Why::Burst));
        assert_eq!(danger(&ally(1, 0.0, 0.65, 0.35, 0), &near), None); // a burst, still above 60 %
        assert_eq!(danger(&ally(1, 0.0, 0.90, 0.0, 60), &near), Some(Why::Cc));
        assert_eq!(danger(&ally(1, 0.0, 0.90, 0.0, CC_MIN - 1), &near), None); // over before R lands
        assert_eq!(danger(&Ally { undying: true, ..ally(1, 0.0, 0.10, 0.0, 90) }, &near), None);
    }

    #[test]
    fn the_lowest_in_his_circle_is_saved() {
        let enemies = [(10_000.0, 0.0), (80_000.0, 0.0)];
        let allies = [ally(1, 0.0, 0.28, 0.0, 0), ally(2, 20_000.0, 0.12, 0.0, 0), ally(3, 90_000.0, 0.05, 0.0, 0)];
        // #3 is lower but outside his circle
        assert_eq!(pick_save((0.0, 0.0), &allies, &enemies).map(|a| (a.0.id, a.1)), Some((2, Why::Low)));
        let fine = [ally(1, 0.0, 0.9, 0.0, 0), ally(2, 20_000.0, 0.7, 0.1, 0)];
        assert_eq!(pick_save((0.0, 0.0), &fine, &enemies), None);
        let stunned = [ally(1, 0.0, 0.9, 0.0, 0), ally(2, 20_000.0, 0.8, 0.0, 70)];
        assert_eq!(pick_save((0.0, 0.0), &stunned, &enemies).map(|a| (a.0.id, a.1)), Some((2, Why::Cc)));
    }

    #[test]
    fn the_burst_looks_back_burst_t_ticks() {
        let h = [(100, 0.95), (130, 0.80), (150, 0.70)];
        assert!((drop_of(&h, 160, 0.50) - 0.45).abs() < 1e-9);
        assert!((drop_of(&h, 170, 0.50) - 0.30).abs() < 1e-9);
        assert_eq!(drop_of(&[], 10, 0.4), 0.0);
    }
}
