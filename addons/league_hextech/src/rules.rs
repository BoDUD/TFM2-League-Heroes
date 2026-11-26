//! 规则：一局 4 次选择，每次 3 张卡（每张能刷新一次，同一档），档位每次随机、全场同一档，前两次不会都是银，同一个人不拿重复的
//! （英雄联盟海克斯大乱斗的规矩，等级按本游戏最高 12 级改成开局 / 6 / 9 / 12 级，[`super::settings`]）。
//!
//! 随机全从模拟的种子来（splitmix64，大小龙 rules.rs 的做法）：档位按 (种子)，每个人的卡按 (种子, 座位, 第几次)，同一小局的
//! 每一份模拟都一样。AI 怎么选（[`choose`]）：每张卡打分（[`score`]：英雄特性 × 海克斯的权重、和拿过的同类加一点、落后时偏保命、
//! 领先时偏输出，再加一点按种子的抖动），分低的（[`reroll_bar`]、[`worth_reroll`]）先刷新一次，最后拿分最高的。

use super::augments::{meta_aug, pool, Tier, Traits, AUGS};

/// 一局几次选择。
pub const SCREENS: usize = 4;
/// AI 把分低于这个的卡刷新掉（每张一次）……
pub const REROLL_BELOW: f32 = 0.40;
/// ……或者低于这一档里对他最好的那张的这么多（他知道这一档有什么：坦克看见法强卡就刷新，射手留着攻击力卡）。
pub const REROLL_SHARE: f32 = 0.6;
/// 打分的抖动上限（差不多好的几张里不总拿同一张）。
pub const JITTER: f32 = 0.06;
/// 拿过同一类的再拿一个加多少分。
pub const SYNERGY: f32 = 0.08;

pub fn splitmix(mut x: u64) -> u64 {
    x = x.wrapping_add(0x9e37_79b9_7f4a_7c15);
    let mut z = x;
    z = (z ^ (z >> 30)).wrapping_mul(0xbf58_476d_1ce4_e5b9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94d0_49bb_1331_11eb);
    z ^ (z >> 31)
}

/// 按种子走的随机数。
#[derive(Clone, Debug)]
pub struct Rng(u64);

impl Rng {
    pub fn new(seed: u64) -> Rng {
        Rng(splitmix(seed))
    }

    pub fn next_u64(&mut self) -> u64 {
        self.0 = splitmix(self.0);
        self.0
    }

    /// 0..n
    pub fn below(&mut self, n: usize) -> usize {
        if n == 0 {
            return 0;
        }
        (self.next_u64() % n as u64) as usize
    }

    /// [0, 1)
    pub fn unit(&mut self) -> f32 {
        (self.next_u64() >> 40) as f32 / (1u64 << 24) as f32
    }
}

/// 档位的种子。
const TIER_SALT: u64 = 0x6865_7874_6563_6801;
/// 每个人每一次的卡的种子。
const PICK_SALT: u64 = 0x6175_676d_656e_7402;

pub fn pick_seed(seed: u64, seat: usize, screen: usize) -> u64 {
    splitmix(seed ^ PICK_SALT ^ ((seat as u64) << 8) ^ screen as u64)
}

/// 按权重抽一个档位（权重全是 0 时当作各一份）。
fn draw_tier(rng: &mut Rng, weights: [u32; 3], allowed: &[Tier]) -> Tier {
    let ws: Vec<(Tier, u32)> = allowed.iter().map(|&t| (t, weights[t.code() as usize])).collect();
    let total: u32 = ws.iter().map(|x| x.1).sum();
    if total == 0 {
        return allowed[rng.below(allowed.len())];
    }
    let mut r = (rng.next_u64() % total as u64) as u32;
    for (t, wt) in ws {
        if r < wt {
            return t;
        }
        r -= wt;
    }
    allowed[allowed.len() - 1]
}

/// 这一局 4 次的档位（全场同一档）：按权重抽，前两次不会都是银。
pub fn tiers(seed: u64, weights: [u32; 3]) -> [Tier; SCREENS] {
    let mut rng = Rng::new(seed ^ TIER_SALT);
    let mut out = [Tier::Gold; SCREENS];
    for k in 0..SCREENS {
        let mut t = draw_tier(&mut rng, weights, &Tier::ALL);
        if k == 1 && t == Tier::Silver && out[0] == Tier::Silver {
            t = draw_tier(&mut rng, weights, &[Tier::Gold, Tier::Prismatic]);
        }
        out[k] = t;
    }
    out
}

/// 从 `tier` 里抽一张没出现过（`seen`）、没拿过（`banned`）的。`borrow`：这一档抽空了就从别的档补（先低一档再高一档）——
/// 只有发牌时用（一个人拿了好几个棱彩以后，棱彩不够三张）；刷新只出同一档，抽空了就不刷新。
pub fn draw_card(rng: &mut Rng, tier: Tier, seen: &[usize], banned: &[usize], borrow: bool) -> Option<usize> {
    let order: &[Tier] = match (tier, borrow) {
        (_, false) => std::slice::from_ref(match tier {
            Tier::Silver => &Tier::Silver,
            Tier::Gold => &Tier::Gold,
            Tier::Prismatic => &Tier::Prismatic,
        }),
        (Tier::Silver, true) => &[Tier::Silver, Tier::Gold, Tier::Prismatic],
        (Tier::Gold, true) => &[Tier::Gold, Tier::Silver, Tier::Prismatic],
        (Tier::Prismatic, true) => &[Tier::Prismatic, Tier::Gold, Tier::Silver],
    };
    for &t in order {
        let left: Vec<usize> = pool(t).into_iter().filter(|i| !seen.contains(i) && !banned.contains(i)).collect();
        if !left.is_empty() {
            return Some(left[rng.below(left.len())]);
        }
    }
    None
}

/// 质变、潘朵拉的盒子随机给的一个（0.5.0）：`tier` 这一档（None：哪一档都行），不在 `avoid` 里，也不是会再随机给海克斯的那几种。
pub fn random_aug(rng: &mut Rng, tier: Option<Tier>, avoid: &[usize]) -> Option<usize> {
    let left: Vec<usize> = (0..AUGS.len())
        .filter(|&a| tier.is_none_or(|t| AUGS[a].tier == t) && !avoid.contains(&a) && !meta_aug(AUGS[a].ev))
        .collect();
    (!left.is_empty()).then(|| left[rng.below(left.len())])
}

/// 海克斯的权重和英雄特性的吻合度：逐项相乘的和除以权重绝对值之和（-1..=1）。
pub fn fit(weights: &Traits, t: &Traits) -> f32 {
    let (w, t) = (weights.arr(), t.arr());
    let norm: f32 = w.iter().map(|x| x.abs()).sum();
    if norm <= 0.0 {
        return 0.0;
    }
    w.iter().zip(t.iter()).map(|(a, b)| a * b).sum::<f32>() / norm
}

/// 一张卡的分（不含抖动）。`mood`：-1（落后很多）..=1（领先很多）。
pub fn score(aug: usize, t: &Traits, taken: &[usize], mood: f32) -> f32 {
    let a = &AUGS[aug];
    let mut s = fit(&a.fit, t);
    if taken.iter().any(|&x| AUGS[x].theme == a.theme) {
        s += SYNERGY;
    }
    if mood < 0.0 {
        s += -mood * 0.20 * a.fit.tank.max(0.0);
    } else if mood > 0.0 {
        s += mood * 0.10 * a.fit.ad.max(a.fit.ap).max(0.0);
    }
    s
}

/// 比分差 -> 心情：差 8 分以上算到头。
pub fn mood(score_diff: i32) -> f32 {
    (score_diff as f32 / 8.0).clamp(-1.0, 1.0)
}

/// 一次选择的经过：这一次的档位，最先发的三张，刷新了哪几张，最后的三张，各自的分（含抖动），拿了哪一张。
#[derive(Clone, Debug, PartialEq)]
pub struct Screen {
    pub tier: Tier,
    pub first: [usize; 3],
    pub rerolled: [bool; 3],
    pub cards: [usize; 3],
    pub scores: [f32; 3],
    pub chosen: usize,
}

/// 发三张卡（同一档、互不相同、不是拿过的）。
pub fn deal(rng: &mut Rng, tier: Tier, banned: &[usize]) -> Option<[usize; 3]> {
    let mut cards = Vec::with_capacity(3);
    for _ in 0..3 {
        let c = draw_card(rng, tier, &cards, banned, true)?;
        cards.push(c);
    }
    Some([cards[0], cards[1], cards[2]])
}

/// 刷新线：[`REROLL_BELOW`]，或这一档（没拿过的）里对他最好的那张的 [`REROLL_SHARE`]，取高的。低于它的才考虑刷新，刷不刷
/// 看 [`worth_reroll`]。
pub fn reroll_bar(t: &Traits, taken: &[usize], mood: f32, tier: Tier) -> f32 {
    let best = pool(tier).into_iter().filter(|a| !taken.contains(a)).map(|a| score(a, t, taken, mood)).fold(f32::MIN, f32::max);
    REROLL_BELOW.max(best * REROLL_SHARE)
}

/// 刷新能刷出来的卡的分：`tier` 这一档里不在 `avoid`、没拿过的。
pub fn left_scores(t: &Traits, taken: &[usize], mood: f32, tier: Tier, avoid: &[usize]) -> Vec<f32> {
    pool(tier).into_iter().filter(|c| !avoid.contains(c) && !taken.contains(c)).map(|c| score(c, t, taken, mood)).collect()
}

/// 分 `s` 的这张刷不刷：先得低于刷新线 `bar`。桌上另外两张里有比它高的（`other`），刷了拿到的也不会更差，刷；它是桌上最高的，
/// 刷出来的（`left`，[`left_scores`]）和 `other` 取高的，平均比它好才刷。
///
/// 0.4.0：0.3.0 是低于这一档的平均分才刷（法师把 0.47 分的烈焰烙印刷成灵巧的时候比刷出奥术卡多）。100 个海克斯以后银档 31 个里
/// 适合法师的只有 8 个，平均分只有 0.22，法师拿着 0.28 分的左右开弓不刷、桌上第二张不合适的也不刷；其实刷第二张不吃亏，刷最高的
/// 那张也还有另外两张垫着。
pub fn worth_reroll(s: f32, other: f32, bar: f32, left: &[f32]) -> bool {
    if s >= bar || left.is_empty() {
        return false;
    }
    if s < other {
        return true;
    }
    left.iter().map(|&x| x.max(other)).sum::<f32>() / left.len() as f32 > s
}

/// AI 的一次选择：发三张，分低的（[`reroll_bar`]、[`worth_reroll`]）各刷新一次（换成这一次没出现过的同档卡；先刷分最低的，
/// 桌上最高的那张最后决定），拿分最高的（一样高拿靠前的）。
pub fn choose(t: &Traits, taken: &[usize], mood: f32, rng: &mut Rng, tier: Tier) -> Option<Screen> {
    let first = deal(rng, tier, taken)?;
    let bar = reroll_bar(t, taken, mood, tier);
    let mut cards = first;
    let mut seen: Vec<usize> = first.to_vec();
    let mut rerolled = [false; 3];
    let mut scores = [0f32; 3];
    for i in 0..3 {
        scores[i] = score(cards[i], t, taken, mood) + rng.unit() * JITTER;
    }
    let mut order = [0usize, 1, 2];
    order.sort_by(|&a, &b| scores[a].total_cmp(&scores[b]));
    for i in order {
        let other = (0..3).filter(|&j| j != i).map(|j| scores[j]).fold(f32::MIN, f32::max);
        let ctier = AUGS[cards[i]].tier;
        if worth_reroll(scores[i], other, bar, &left_scores(t, taken, mood, ctier, &seen)) {
            if let Some(c) = draw_card(rng, ctier, &seen, taken, false) {
                cards[i] = c;
                seen.push(c);
                rerolled[i] = true;
                scores[i] = score(c, t, taken, mood) + rng.unit() * JITTER;
            }
        }
    }
    let mut best = 0;
    for i in 1..3 {
        if scores[i] > scores[best] {
            best = i;
        }
    }
    Some(Screen { tier, first, rerolled, cards, scores, chosen: cards[best] })
}

#[cfg(test)]
pub(crate) mod tests {
    use super::super::augments::by_key;
    use super::*;

    fn marksman() -> Traits {
        Traits { ad: 1.0, attacker: 1.0, ranged: 1.0, caster: 0.2, ..Traits::ZERO }
    }

    fn tank() -> Traits {
        Traits { ap: 0.4, tank: 1.0, bruiser: 0.4, caster: 0.3, attacker: 0.2, support: 0.7, melee: 1.0, ..Traits::ZERO }
    }

    fn mage() -> Traits {
        Traits { ap: 1.0, caster: 1.0, ranged: 1.0, attacker: 0.1, assassin: 0.2, ..Traits::ZERO }
    }

    #[test]
    fn the_same_seed_gives_the_same_match() {
        for seed in [1u64, 42, 0xdead_beef, u64::MAX] {
            assert_eq!(tiers(seed, [35, 45, 20]), tiers(seed, [35, 45, 20]));
            let a = choose(&marksman(), &[], 0.0, &mut Rng::new(pick_seed(seed, 3, 1)), Tier::Gold);
            let b = choose(&marksman(), &[], 0.0, &mut Rng::new(pick_seed(seed, 3, 1)), Tier::Gold);
            assert_eq!(a, b);
        }
        // seats and screens draw their own cards
        let s = 7u64;
        let a = deal(&mut Rng::new(pick_seed(s, 0, 0)), Tier::Silver, &[]);
        let others: Vec<_> = (1..10).map(|seat| deal(&mut Rng::new(pick_seed(s, seat, 0)), Tier::Silver, &[])).collect();
        assert!(others.iter().any(|o| *o != a));
    }

    #[test]
    fn the_first_two_are_never_both_silver() {
        let mut tiers_seen = [0usize; 3];
        for seed in 0..5000u64 {
            let t = tiers(seed, [35, 45, 20]);
            assert!(!(t[0] == Tier::Silver && t[1] == Tier::Silver), "seed {seed}: {t:?}");
            for x in t {
                tiers_seen[x.code() as usize] += 1;
            }
        }
        // every tier comes up, roughly by its weight
        assert!(tiers_seen.iter().all(|&n| n > 1500), "{tiers_seen:?}");
        // only silver allowed by the weights: still not both silver at the start
        let t = tiers(9, [100, 0, 0]);
        assert_eq!(t[0], Tier::Silver);
        assert_ne!(t[1], Tier::Silver);
    }

    #[test]
    fn cards_are_distinct_new_and_of_the_screens_tier() {
        for seed in 0..2000u64 {
            let taken = vec![by_key("deft").unwrap(), by_key("glass_cannon").unwrap()];
            for tier in Tier::ALL {
                let mut rng = Rng::new(seed);
                let s = choose(&mage(), &taken, 0.0, &mut rng, tier).expect("cards");
                let mut c = s.cards.to_vec();
                c.sort();
                c.dedup();
                assert_eq!(c.len(), 3, "{s:?}");
                assert!(s.cards.iter().all(|x| !taken.contains(x)), "{s:?}");
                assert!(s.cards.iter().all(|&x| AUGS[x].tier == tier), "{s:?}");
                assert!(s.cards.contains(&s.chosen));
                // a reroll brings a card that was not on the table before
                for i in 0..3 {
                    if s.rerolled[i] {
                        assert!(!s.first.contains(&s.cards[i]), "{s:?}");
                    } else {
                        assert_eq!(s.first[i], s.cards[i]);
                    }
                }
            }
        }
    }

    #[test]
    fn a_tier_running_dry_borrows_from_the_next() {
        // every prismatic taken: the cards come from gold, then silver
        let all_prismatic = pool(Tier::Prismatic);
        let s = choose(&tank(), &all_prismatic, 0.0, &mut Rng::new(3), Tier::Prismatic).expect("cards");
        assert!(s.cards.iter().all(|&x| AUGS[x].tier != Tier::Prismatic), "{s:?}");
    }

    // 0.3.0 起每一类也算上合适的触发类
    pub(crate) const DAMAGE: [&str; 53] = ["blunt_force", "deft", "bloodthirst", "lethal_precision", "giant_slayer", "slayer",
                                           "storm_fury", "glass_cannon", "thread_the_needle", "light_em_up", "mystic_punch",
                                           "chain_lightning", "get_excited", "typhoon", "executioner", "firebrand", "ice_cold",
                                           "orbital_laser",
                                           // 0.4.0
                                           "zealot", "scoped_weapons", "erosion", "its_critical", "scopier_weapons",
                                           "scopiest_weapons", "still_here", "sap_magic", "take_em_down", "third_times_the_harm",
                                           "dual_wield", "ok_boomerang", "master_of_duality", "its_killing_time", "arcane_axiom",
                                           // 控住人加攻击力 / 法强，带控制的英雄拿
                                           "slap_around",
                                           // 第二批
                                           "goredrink", "escapade", "heavy_is_the_crown", "twin_fire",
                                           // 脆皮射手的保命海克斯，英雄联盟里射手也常拿
                                           "escape_plan",
                                          // 0.5.0
                                          "donation", "goldrend", "stats", "stats_on_stats", "stats_on_stats_on_stats", "infernal_soul", "hextech_soul", "omni_soul", "hand_of_baron", "crimson_cobalt", "flow_of_spirit", "mercys_strike", "trusty_weapon", "pursuit_of_power"];
    pub(crate) const TANKY: [&str; 62] = ["hearty", "ironclad", "celestial_body", "unwavering", "immortal_colossus",
                                          "swift_feet", "ultimate_awakening", "mind_focus", "tank_engine", "heavy_hitter",
                                          "dawnbringers_resolve", "guardian", "goliath", "immolate", "undying_will",
                                          "quantum_computing", "sacred_ward", "courage_of_the_colossus", "giant_snowball",
                                          "ice_cold", "vulnerability",
                                          // 0.4.0
                                          "fortified", "mystic_guard", "steadfaster_presence", "porcupine", "soul_eater",
                                          "guilty_pleasure", "salvation", "mosh_monster", "titans_resolve", "divine_intervention",
                                          "mighty_shield", "ultimate_unstoppable", "squishy_slappy_grab", "prom_queen",
                                          "lonely_warrior", "dive_bomber", "circle_of_death", "sonata", "slap_around",
                                          "cant_touch_this", "recursion", "outlaws_grit", "shark_bait",
                                          // 第二批
                                          "goredrink", "slime_time", "endless_decimation", "hellbent",
                                          // 0.5.0
                                          "donation", "stats", "stats_on_stats", "stats_on_stats_on_stats", "pressure_cooker", "mountain_soul", "ocean_soul", "omni_soul", "adaptive_ward", "ravenous_bind", "rejuvenation", "siphon", "stay_resolute", "terror"];
    pub(crate) const MAGIC: [&str; 55] = ["witchful_thinking", "mind_focus", "arcane_surge", "archmage", "thread_the_needle",
                                          "glass_cannon", "ultimate_awakening", "magic_missile", "firebrand", "chain_lightning",
                                          "ethereal_weapon", "phenomenal_evil", "orbital_laser", "sacred_ward", "escape_plan",
                                          "cruelty", "ice_cold",
                                          // 0.4.0
                                          "lich_brain", "firefox", "recursion", "arcane_axiom", "big_brain", "skilled_sniper",
                                          "eureka", "infinite_recursion", "fey_magic", "ultimate_revolution", "sonata",
                                          "master_of_duality", "erosion", "its_killing_time", "twin_fire", "slap_around",
                                          // 普攻带法强伤害：这个游戏里法师技能转好之前一直在普攻
                                          "marksmage",
                                          // 第二批
                                          "adapt", "heavy_is_the_crown", "bees",
                                          // 0.5.0
                                          "donation", "goldrend", "stats", "stats_on_stats", "stats_on_stats_on_stats", "from_downtown", "infernal_soul", "hextech_soul", "omni_soul", "hand_of_baron", "crimson_cobalt", "overloaded", "siphon", "trusty_weapon", "bread_and_butter", "bread_and_jam", "pursuit_of_haste", "pursuit_of_power"];

    /// 三张加三次刷新一共见到六张，一档 `n` 张里合适的有 `g` 张时六张全不合适的概率（C(n-g, 6) / C(n, 6)）。
    fn miss_all_six(n: usize, g: usize) -> f64 {
        (0..6).map(|i| ((n - g) as f64 - i as f64).max(0.0) / (n - i) as f64).product()
    }

    /// AI 拿合适的：射手拿攻击力 / 攻速 / 暴击，坦克拿生命和抗性，法师拿法强和冷却。三张和刷新出来的也可能一张合适的都没有
    /// （那就拿桌上最好的），所以要求的是离「见到合适的就拿」（1 - [`miss_all_six`]）差不到 5 个百分点，最多要九成。0.4.0 的
    /// 银档 31 张里适合法师的只有 8 张，六张都不合适有 14%，那一档要 81%；以前棱彩 15 张里适合射手的 4 张，那时是 85%。
    #[test]
    fn the_ai_takes_what_fits() {
        for (who, t, good) in [("marksman", marksman(), &DAMAGE[..]), ("tank", tank(), &TANKY[..]), ("mage", mage(), &MAGIC[..])] {
            for tier in Tier::ALL {
                let n = 600u64;
                let mut misses: Vec<&str> = Vec::new();
                let hits = (0..n)
                    .filter(|&seed| {
                        let key = AUGS[choose(&t, &[], 0.0, &mut Rng::new(seed), tier).unwrap().chosen].key;
                        let ok = good.contains(&key);
                        if !ok {
                            misses.push(key);
                        }
                        ok
                    })
                    .count();
                misses.sort();
                let mut seen: Vec<(&str, usize)> = Vec::new();
                for m in misses {
                    match seen.last_mut() {
                        Some(x) if x.0 == m => x.1 += 1,
                        _ => seen.push((m, 1)),
                    }
                }
                let g = pool(tier).into_iter().filter(|&a| good.contains(&AUGS[a].key)).count();
                let least = (1.0 - miss_all_six(pool(tier).len(), g) - 0.05).min(0.9);
                assert!(hits as f64 >= least * n as f64,
                        "{who} took a fitting {tier:?} augment {hits} times in {n} (least {least:.3}), else {seen:?}");
            }
        }
    }

    /// What it keeps is the best of the three on the table (after the rerolls), and a reroll only hits a card under the
    /// bar.
    #[test]
    fn the_ai_takes_the_best_on_the_table() {
        for seed in 0..300u64 {
            for t in [marksman(), tank(), mage()] {
                for tier in Tier::ALL {
                    let s = choose(&t, &[], 0.0, &mut Rng::new(seed), tier).unwrap();
                    let best = (0..3).max_by(|&a, &b| s.scores[a].partial_cmp(&s.scores[b]).unwrap()).unwrap();
                    assert_eq!(s.chosen, s.cards[best]);
                    let bar = reroll_bar(&t, &[], 0.0, tier);
                    for i in 0..3 {
                        if s.rerolled[i] {
                            assert!(score(s.first[i], &t, &[], 0.0) < bar, "{s:?}");
                        }
                    }
                }
            }
        }
    }

    #[test]
    fn a_tank_never_takes_the_glass_cannon_over_a_fitting_card() {
        let gc = by_key("glass_cannon").unwrap();
        let hearty = by_key("celestial_body").unwrap();
        assert!(score(gc, &tank(), &[], 0.0) < 0.0);
        assert!(score(hearty, &tank(), &[], 0.0) > score(gc, &tank(), &[], 0.0) + 0.5);
    }

    #[test]
    fn behind_leans_on_defence_ahead_on_damage() {
        let bruiser = Traits { ad: 1.0, bruiser: 1.0, tank: 0.3, attacker: 0.6, melee: 1.0, ..Traits::ZERO };
        let colossus = by_key("immortal_colossus").unwrap();
        let slayer = by_key("slayer").unwrap();
        let gap = |m: f32| score(colossus, &bruiser, &[], m) - score(slayer, &bruiser, &[], m);
        assert!(gap(-1.0) > gap(0.0) && gap(0.0) > gap(1.0));
        assert_eq!(mood(0), 0.0);
        assert_eq!(mood(-40), -1.0);
        assert_eq!(mood(4), 0.5);
    }

    /// 用户 2026-11-27：「海克斯乱斗确定全生效了吗」。AI 那几队的卡是 AI 自己在比赛里选的：游戏的六种分类 × 物理 / 法术 / 都有 ×
    /// 带不带控制 × 有没有治疗 × 五个分路，各打 40 局（落后、持平、领先轮着来），每个海克斯都得有人拿过——谁都不拿的，AI 那几队
    /// 里永远见不到。
    #[test]
    fn every_augment_gets_taken_by_somebody() {
        use super::super::kit::{from_kit, Kit};
        use mod_api_stable::{ChampionCategoryV1 as C, ChampionTagV1 as G, LaneV1};
        let mut got = vec![0usize; AUGS.len()];
        let mut n = 0u64;
        for cat in [C::Melee, C::Range, C::Magician, C::Util, C::Assassin, C::Tank] {
            for dmg in [&[G::Ad][..], &[G::Ap], &[G::Ad, G::Ap]] {
                for (cc, aid) in [(false, false), (true, false), (false, true), (true, true)] {
                    let mut tags = dmg.to_vec();
                    if cc {
                        tags.push(G::Cc);
                    }
                    if aid {
                        tags.push(G::Heal);
                    }
                    let kit = Kit { category: Some(cat), tags };
                    for lane in [LaneV1::Top, LaneV1::Jungle, LaneV1::Mid, LaneV1::Bottom, LaneV1::Support] {
                        let t = from_kit(&kit, Some(lane));
                        for game in 0..40u64 {
                            n += 1;
                            let seed = splitmix(n);
                            let m = [-0.5f32, 0.0, 0.5][(game % 3) as usize];
                            let mut taken = Vec::new();
                            for (k, &tier) in tiers(seed, [35, 45, 20]).iter().enumerate() {
                                let mut rng = Rng::new(pick_seed(seed, 3, k));
                                if let Some(s) = choose(&t, &taken, m, &mut rng, tier) {
                                    got[s.chosen] += 1;
                                    taken.push(s.chosen);
                                }
                            }
                        }
                    }
                }
            }
        }
        let mut order: Vec<usize> = (0..AUGS.len()).collect();
        order.sort_by_key(|&a| got[a]);
        let total: usize = got.iter().sum();
        for &a in order.iter().take(25) {
            eprintln!("TAKEN {:<26} {:?} {}", AUGS[a].key, AUGS[a].tier, got[a]);
        }
        eprintln!("TAKEN total {total} picks over {n} games");
        let never: Vec<&str> = order.iter().filter(|&&a| got[a] == 0).map(|&a| AUGS[a].key).collect();
        assert!(never.is_empty(), "nobody takes these: {never:?}");
    }
}
