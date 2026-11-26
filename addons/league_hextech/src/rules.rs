//! 规则：一局 4 次选择，每次 3 张卡（每张能刷新一次，同一档），档位每次随机、全场同一档，前两次不会都是银，同一个人不拿重复的
//! （英雄联盟海克斯大乱斗的规矩，等级按本游戏最高 12 级改成开局 / 6 / 9 / 12 级，[`super::settings`]）。
//!
//! 随机全从模拟的种子来（splitmix64，大小龙 rules.rs 的做法）：档位按 (种子)，每个人的卡按 (种子, 座位, 第几次)，同一小局的
//! 每一份模拟都一样。AI 怎么选（[`choose`]）：每张卡打分（[`score`]：英雄特性 × 海克斯的权重、和拿过的同类加一点、落后时偏保命、
//! 领先时偏输出，再加一点按种子的抖动），分低的（[`reroll_bar`]）先刷新一次，最后拿分最高的。

use super::augments::{pool, Tier, Traits, AUGS};

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

/// 刷新的门槛：[`REROLL_BELOW`]，或这一档（没拿过的）里对他最好的那张的 [`REROLL_SHARE`]，取高的；但不高过这一档的平均分
/// （0.3.0：刷出来的那张平均就这么好，比它好的卡留着。47 个里一类英雄合适的只有几张，法师把 0.47 分的烈焰烙印刷成灵巧的时候比
/// 刷出奥术卡多）。
pub fn reroll_bar(t: &Traits, taken: &[usize], mood: f32, tier: Tier) -> f32 {
    let scores: Vec<f32> = pool(tier).into_iter().filter(|a| !taken.contains(a)).map(|a| score(a, t, taken, mood)).collect();
    let best = scores.iter().copied().fold(f32::MIN, f32::max);
    let mean = if scores.is_empty() { 0.0 } else { scores.iter().sum::<f32>() / scores.len() as f32 };
    REROLL_BELOW.max(best * REROLL_SHARE).min(mean)
}

/// AI 的一次选择：发三张，分低的（[`reroll_bar`]）各刷新一次（换成这一次没出现过的同档卡），拿分最高的（一样高拿靠前的）。
pub fn choose(t: &Traits, taken: &[usize], mood: f32, rng: &mut Rng, tier: Tier) -> Option<Screen> {
    let first = deal(rng, tier, taken)?;
    let bar = reroll_bar(t, taken, mood, tier);
    let mut cards = first;
    let mut seen: Vec<usize> = first.to_vec();
    let mut rerolled = [false; 3];
    let mut scores = [0f32; 3];
    for i in 0..3 {
        scores[i] = score(cards[i], t, taken, mood) + rng.unit() * JITTER;
        if scores[i] < bar {
            let mut avoid = seen.clone();
            avoid.extend(cards.iter().copied());
            if let Some(c) = draw_card(rng, AUGS[cards[i]].tier, &avoid, taken, false) {
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
    pub(crate) const DAMAGE: [&str; 18] = ["blunt_force", "deft", "bloodthirst", "lethal_precision", "giant_slayer", "slayer",
                                           "storm_fury", "glass_cannon", "thread_the_needle", "light_em_up", "mystic_punch",
                                           "chain_lightning", "get_excited", "typhoon", "executioner", "firebrand", "ice_cold",
                                           "orbital_laser"];
    pub(crate) const TANKY: [&str; 21] = ["hearty", "ironclad", "celestial_body", "unwavering", "immortal_colossus",
                                          "swift_feet", "ultimate_awakening", "mind_focus", "tank_engine", "heavy_hitter",
                                          "dawnbringers_resolve", "guardian", "goliath", "immolate", "undying_will",
                                          "quantum_computing", "sacred_ward", "courage_of_the_colossus", "giant_snowball",
                                          "ice_cold", "vulnerability"];
    pub(crate) const MAGIC: [&str; 17] = ["witchful_thinking", "mind_focus", "arcane_surge", "archmage", "thread_the_needle",
                                          "glass_cannon", "ultimate_awakening", "magic_missile", "firebrand", "chain_lightning",
                                          "ethereal_weapon", "phenomenal_evil", "orbital_laser", "sacred_ward", "escape_plan",
                                          "cruelty", "ice_cold"];

    /// The AI takes what fits the kit: a marksman attack damage / speed / crit, a tank health and resists, a mage ability
    /// power and cooldowns. Not every time - three cards and their rerolls may hold nothing that fits, and then the best
    /// of what is there is taken - but nearly: at least 9 picks in 10; of the 15 prismatic ones only 4 fit a marksman
    /// (since 0.3.0), and six draws miss all four about one time in eleven, so there 85 in 100.
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
                let least = if tier == Tier::Prismatic { 0.85 } else { 0.9 };
                assert!(hits as f64 >= least * n as f64,
                        "{who} took a fitting {tier:?} augment {hits} times in {n}, else {seen:?}");
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
}
