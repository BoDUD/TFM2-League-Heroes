//! 触发类海克斯在假模拟上（[`super::mock`]）：打中、放技能、参与击杀、残血、控住敌人、定时，各出一次效果、该停的停；
//! 同一场跑两遍做的事一模一样；特效只给屏幕那一场记。

use mod_api_stable::*;

use super::augments::Ev;
use super::mock::{with_sim, World};
use super::procs::{self, Procs, Show, Who};

const HEROES: [&str; 10] = ["league_garen", "league_leesin", "league_ahri", "league_jinx", "league_leona", "league_darius",
                            "league_elise", "league_syndra", "league_caitlyn", "league_lulu"];

struct Bench {
    w: World,
    p: Procs,
    who: Vec<Who>,
    held: Vec<u64>,
    names: Vec<String>,
    screen: bool,
}

impl Bench {
    fn new(evs: &[(usize, &[Ev])]) -> Bench {
        let w = World::new(5, SimOriginKindV1::ServerPresim, HEROES);
        let who = (0..10).map(|i| Who { player: i, team: i / 5, lane: (i % 5) as u8 }).collect();
        let mut held = vec![0u64; 10];
        for &(seat, list) in evs {
            for e in list {
                held[seat] |= e.bit();
            }
        }
        let names = HEROES.iter().map(|h| h.to_string()).collect();
        Bench { w, p: Procs::default(), who, held, names, screen: false }
    }

    /// 走到第 `to` tick（每 [`procs::EVERY`] tick 看一次）。
    fn go(&mut self, to: usize) {
        while self.w.tick < to {
            self.w.tick += 1;
            if self.w.tick.is_multiple_of(procs::EVERY) {
                let (p, who, held, names, screen) = (&mut self.p, &self.who, &self.held, &self.names, self.screen);
                with_sim(&mut self.w, |sim| {
                    let now = sim.tick();
                    p.step(sim, now, who, held, names, screen)
                });
            }
        }
    }

    /// 把 `who` 挪到 `to` 旁边（x 差 `dx`，同一个 y）。
    fn near(&mut self, who: usize, to: usize, dx: u64) {
        let at = self.w.champ(to).pos;
        self.w.champ_mut(who).pos = (at.0 + dx, at.1);
    }

    /// `h` 打了 `v` 一下（他的伤害统计涨，`v` 掉生命）。
    fn strike(&mut self, h: usize, v: usize, amount: usize) {
        self.w.players[h].deal = self.w.players[h].deal.map(|d| d + amount as u64);
        self.w.hurt(v, amount);
    }
}

const AP: u32 = 1;
const AD: u32 = 0;
const FIXED: u32 = 2;
const DOT: u32 = 2;

#[test]
fn a_hit_burns_the_champion_six_times_and_its_own_burn_never_counts_as_a_hit() {
    let mut b = Bench::new(&[(3, &[Ev::Firebrand])]);
    b.near(8, 3, 60_000);
    b.go(2);
    b.strike(3, 8, 150);
    b.go(4);
    let burns = b.w.hits_on(8);
    assert_eq!(burns.len(), 1, "the first pulse at once");
    let per = procs::firebrand_total(2000, 200, 300) / 6;
    assert_eq!(burns[0], (b.w.ent(3), b.w.ent(8), per, AP, DOT));
    b.go(4 + 30 * 5 + 40);
    let burns = b.w.hits_on(8);
    assert_eq!(burns.len(), 6, "six pulses, never more (the burn's own damage is no hit): {burns:?}");
    assert!(b.w.hits_on(7).is_empty());
    assert_eq!(b.p.summary(), "firebrand 1");
}

#[test]
fn a_hurt_champion_far_away_is_not_his_hit() {
    let mut b = Bench::new(&[(3, &[Ev::Firebrand, Ev::HeavyHitter])]);
    b.near(8, 3, 120_000);
    b.go(2);
    b.strike(3, 8, 150);
    b.go(10);
    assert!(b.w.hits.is_empty(), "{:?}", b.w.hits);
}

#[test]
fn chain_lightning_jumps_to_three_and_waits_three_seconds() {
    let mut b = Bench::new(&[(3, &[Ev::ChainLightning])]);
    b.near(8, 3, 60_000);
    b.near(7, 8, 20_000);
    b.near(9, 8, 30_000);
    b.near(6, 8, 39_000);
    b.go(2);
    b.strike(3, 8, 100);
    b.go(4);
    let hit: Vec<usize> = b.w.hits.iter().map(|h| h.1).collect();
    let amount = procs::chain_damage(200, 300);
    assert_eq!(hit.len(), 3, "the first and the two nearest to him");
    assert_eq!(hit, vec![b.w.ent(8), b.w.ent(7), b.w.ent(9)]);
    assert!(b.w.hits.iter().all(|h| h.2 == amount && h.3 == AP));
    assert_eq!(b.w.has(7, procs::E_CHAIN), 1);
    // again a second later: still waiting
    b.go(64);
    b.strike(3, 8, 100);
    b.go(66);
    assert_eq!(b.w.hits.len(), 3);
    // three seconds on: again
    b.go(186);
    b.strike(3, 8, 100);
    b.go(188);
    assert_eq!(b.w.hits.len(), 6);
}

#[test]
fn light_em_up_every_fourth_hit_and_heavy_hitter_per_target() {
    let mut b = Bench::new(&[(3, &[Ev::LightEmUp, Ev::HeavyHitter])]);
    b.near(8, 3, 50_000);
    b.go(2);
    let mut t = 2;
    for _ in 0..4 {
        b.strike(3, 8, 100);
        t += 40;
        b.go(t);
    }
    let light = procs::light_damage(200);
    let heavy = 2000 * procs::HEAVY_PCT / 100;
    let lights = b.w.hits.iter().filter(|h| h.2 == light).count();
    let heavies = b.w.hits.iter().filter(|h| h.2 == heavy).count();
    assert_eq!((lights, heavies), (1, 4), "{:?}", b.w.hits);
}

#[test]
fn escape_plan_once_below_the_line_then_waits() {
    let mut b = Bench::new(&[(3, &[Ev::EscapePlan])]);
    b.go(2);
    b.w.hurt(3, 1400);
    b.go(4);
    assert_eq!(b.w.shields, vec![(b.w.ent(3), procs::escape_shield(2000), procs::ESCAPE_SHIELD_T)]);
    assert_eq!(b.w.has(3, procs::E_ESCAPE), 1);
    // healed up and down again within the cooldown: nothing
    b.w.champ_mut(3).hp = 2000;
    b.go(100);
    b.w.hurt(3, 1500);
    b.go(102);
    assert_eq!(b.w.shields.len(), 1);
    // after it: again
    b.w.champ_mut(3).hp = 2000;
    b.go(4 + procs::ESCAPE_CD + 2);
    b.w.hurt(3, 1500);
    b.go(4 + procs::ESCAPE_CD + 4);
    assert_eq!(b.w.shields.len(), 2);
}

#[test]
fn dawnbringer_and_undying_will_heal_over_two_seconds() {
    let mut b = Bench::new(&[(0, &[Ev::Dawnbringer]), (1, &[Ev::UndyingWill])]);
    b.go(2);
    b.w.hurt(0, 1400);
    b.w.hurt(1, 1800);
    b.go(4);
    assert_eq!(b.w.has(1, procs::E_UNDYING), 1);
    b.go(4 + 30 * 4);
    let to = |p: usize| b.w.heals.iter().filter(|h| h.1 == b.w.ent(p)).map(|h| h.2).collect::<Vec<_>>();
    // Dawnbringer: 30% of the 1400 missing; Undying Will: 20% of the max
    assert_eq!(to(0), vec![105; 4]);
    assert_eq!(to(1), vec![100; 4]);
}

#[test]
fn takedowns_stack_the_tank_engine_and_the_stacks_follow_him_after_a_respawn() {
    let mut b = Bench::new(&[(0, &[Ev::TankEngine]), (1, &[Ev::GetExcited])]);
    b.go(2);
    for _ in 0..6 {
        // the jungler kills, the top laner assists
        b.w.kills.push(KillLogV1 { tick: 0, killer_team: 0, killer_position: 1, killed_position: 2, assist_count: 1,
                                   assist_positions: [0, 0, 0, 0] });
    }
    b.go(4);
    assert_eq!(b.p.stacks(0), (6, 0));
    let stack = b.w.champ(0).buffs.iter().find(|x| x.name() == procs::S_TANK).copied().expect("the stacks");
    assert_eq!(stack.hp, 6 * procs::TANK_HP);
    assert_eq!(b.w.has(0, procs::G_TANK[0]), 1, "bigger at six");
    assert_eq!(b.w.has(1, procs::E_EXCITED), 1, "the killer gets excited");
    // a red kill gives blue nothing
    b.w.kills.push(KillLogV1 { tick: 0, killer_team: 1, killer_position: 0, killed_position: 0, ..KillLogV1::default() });
    b.go(6);
    assert_eq!(b.p.stacks(0), (6, 0));
    // he dies and comes back: the stacks come back on his new body
    b.w.die(0);
    b.go(8);
    b.w.respawn(0);
    b.go(10);
    assert_eq!(b.w.has(0, procs::S_TANK), 1);
    assert_eq!(b.w.has(0, procs::G_TANK[0]), 1);
}

#[test]
fn casts_punch_the_cooldowns_fire_a_missile_and_take_the_final_form() {
    let mut b = Bench::new(&[(3, &[Ev::MysticPunch, Ev::MagicMissile, Ev::FinalForm])]);
    b.near(8, 3, 60_000);
    b.go(2);
    // a basic attack
    b.w.players[3].cds[0] = 50;
    b.go(4);
    assert_eq!(b.w.reduced, vec![(b.w.ent(3), 1, procs::PUNCH_TICKS), (b.w.ent(3), 2, procs::PUNCH_TICKS)]);
    // a skill: a missile flies at the nearest enemy and lands
    b.w.players[3].cds[1] = 300;
    b.go(6);
    assert!(b.w.hits.is_empty(), "still flying");
    b.go(6 + procs::MISSILE_MIN_T + 14);
    assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), procs::missile_damage(300, 200), AP, 1)]);
    // the ultimate
    b.w.players[3].cds[3] = 3000;
    b.go(40);
    assert_eq!(b.w.has(3, procs::E_FINAL), 1);
}

#[test]
fn immobilizing_an_enemy_drops_a_comet_and_raises_a_shield() {
    let mut b = Bench::new(&[(2, &[Ev::Cruelty, Ev::Colossus])]);
    b.near(7, 2, 50_000);
    b.go(2);
    b.w.players[2].cds[1] = 400;
    b.go(4);
    // stunned a moment later by him
    b.w.champ_mut(7).cc.push(CcV1::stun(60));
    b.go(10);
    assert_eq!(b.w.shields, vec![(b.w.ent(2), procs::colossus_shield(2000), procs::COLOSSUS_T)]);
    b.go(10 + procs::COMET_DELAY + 2);
    let comet = procs::comet_base(300, 200) + 2000 * procs::COMET_HP_PCT / 100;
    assert_eq!(b.w.hits_on(7), vec![(b.w.ent(2), b.w.ent(7), comet, AP, 1)]);
    // a stun with no cast of his before it: nobody's
    let mut c = Bench::new(&[(2, &[Ev::Cruelty])]);
    c.near(7, 2, 50_000);
    c.go(2);
    c.w.champ_mut(7).cc.push(CcV1::stun(60));
    c.go(100);
    assert!(c.w.hits.is_empty());
}

#[test]
fn the_timed_ones_fire_when_somebody_is_in_reach() {
    let mut b = Bench::new(&[(3, &[Ev::OrbitalLaser]), (0, &[Ev::Quantum]), (1, &[Ev::Immolate]), (4, &[Ev::SacredWard])]);
    b.go(2);
    assert!(b.w.hits.is_empty() && b.w.shields.is_empty(), "nobody in reach");
    b.near(8, 3, 60_000);
    b.near(5, 0, 20_000);
    b.near(6, 1, 15_000);
    b.near(2, 4, 40_000);
    b.w.hurt(2, 1000);
    b.go(4);
    // the laser marks first, strikes after its delay
    assert!(b.w.hits_on(8).is_empty());
    let quantum = procs::quantum_base(200) + 2000 * procs::QUANTUM_HP_PCT / 100;
    assert_eq!(b.w.hits_on(5), vec![(b.w.ent(0), b.w.ent(5), quantum, AD, 1)]);
    assert_eq!(b.w.heals, vec![(b.w.ent(0), b.w.ent(0), 2000 * procs::QUANTUM_HEAL_PCT / 100)]);
    // the immolation pulses every second from the first look (nobody was near at tick 2): the next one at 62
    assert!(b.w.hits_on(6).is_empty());
    assert_eq!(b.w.shields, vec![(b.w.ent(2), procs::ward_shield(300, 2000), procs::WARD_T)]);
    b.go(4 + procs::LASER_DELAY + 2);
    let laser = procs::laser_base(300, 200) + 2000 * procs::LASER_HP_PCT / 100;
    assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), laser, AP, 1)]);
    b.go(64);
    assert_eq!(b.w.hits_on(6), vec![(b.w.ent(1), b.w.ent(6), procs::immolate_damage(2000), AP, DOT)]);
    b.go(124);
    assert_eq!(b.w.hits_on(6).len(), 2);
}

#[test]
fn the_snowball_knocks_up_where_it_lands() {
    let mut b = Bench::new(&[(3, &[Ev::Snowball])]);
    b.near(8, 3, 70_000);
    b.near(9, 8, 10_000);
    b.go(2);
    assert!(b.w.ccs.is_empty(), "still flying");
    b.go(2 + procs::SNOW_T + 2);
    let up: Vec<usize> = b.w.ccs.iter().map(|c| c.0).collect();
    assert_eq!(up, vec![b.w.ent(8), b.w.ent(9)]);
    assert!(b.w.ccs.iter().all(|c| c.1.kind == CcKindV1::Airborne.code() && c.1.tick == procs::SNOW_AIR));
}

#[test]
fn executioner_only_on_the_low_and_guardian_shields_both() {
    let mut b = Bench::new(&[(3, &[Ev::Executioner]), (4, &[Ev::Guardian])]);
    b.near(8, 3, 50_000);
    b.near(2, 4, 30_000);
    b.go(2);
    b.strike(3, 8, 100);
    b.go(4);
    assert!(b.w.hits.is_empty(), "8 is not low");
    b.w.champ_mut(8).hp = 500;
    b.go(40);
    b.strike(3, 8, 10);
    b.go(42);
    assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), 2000 * procs::EXEC_DMG_PCT / 100, FIXED, 1)]);
    // the ally near the guardian falls under 40%
    b.w.hurt(2, 1300);
    b.go(44);
    let s = procs::guard_shield(2000);
    assert_eq!(b.w.shields, vec![(b.w.ent(2), s, procs::GUARD_T), (b.w.ent(4), s, procs::GUARD_T)]);
}

/// The same match run twice (the twin presims, the screen's second run) does the same things, and only the screen's run
/// records the battlefield effects.
#[test]
fn the_same_match_twice_does_the_same_and_only_the_screen_records_effects() {
    let play = |screen: bool| {
        let mut b = Bench::new(&[(3, &[Ev::Firebrand, Ev::ChainLightning, Ev::Typhoon]), (2, &[Ev::Vulnerability, Ev::IceCold])]);
        b.screen = screen;
        b.near(8, 3, 60_000);
        b.near(7, 8, 20_000);
        b.near(9, 3, 30_000);
        b.near(2, 3, 10_000);
        b.go(2);
        for k in 0..20 {
            b.strike(3, 8, 80);
            b.strike(2, 7, 60);
            b.go(4 + k * 20);
        }
        let shows: Vec<Show> = b.p.out.iter().map(|o| o.show).collect();
        (b.w.hits.clone(), b.w.units.iter().map(|u| u.buffs.len()).collect::<Vec<_>>(), shows)
    };
    let (a, b) = (play(false), play(false));
    assert_eq!(a, b);
    assert!(a.2.is_empty(), "no effects off the screen");
    let s = play(true);
    assert_eq!(s.0, a.0, "the screen's run plays the same");
    assert!(s.2.contains(&Show::Burn) && s.2.contains(&Show::Chain) && s.2.contains(&Show::Typhoon), "{:?}", s.2);
}
