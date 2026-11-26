//! 触发类海克斯在假模拟上（[`super::mock`]）：打中、放技能、参与击杀、残血、控住敌人、定时，各出一次效果、该停的停；
//! 同一场跑两遍做的事一模一样；特效只给屏幕那一场记。

use mod_api_stable::*;

use super::augments::Ev;
use super::mock::{with_sim, World};
use super::augments::EvSet;
use super::procs::{self, Procs, Show, Who};

const HEROES: [&str; 10] = ["league_garen", "league_leesin", "league_ahri", "league_jinx", "league_leona", "league_darius",
                            "league_elise", "league_syndra", "league_caitlyn", "league_lulu"];

struct Bench {
    w: World,
    p: Procs,
    who: Vec<Who>,
    held: Vec<EvSet>,
    names: Vec<String>,
    screen: bool,
}

impl Bench {
    fn new(evs: &[(usize, &[Ev])]) -> Bench {
        let w = World::new(5, SimOriginKindV1::ServerPresim, HEROES);
        let who = (0..10).map(|i| Who { player: i, team: i / 5, lane: (i % 5) as u8, ranged: false, traits: Default::default() }).collect();
        let mut held = vec![0 as EvSet; 10];
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

    /// `h` 出了一次普攻（普攻的冷却涨上去：下一步认出来）。
    fn attack(&mut self, h: usize) {
        self.w.players[h].cds[0] += 50;
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

/// 0.4.0 对齐：烈焰烙印只认普攻，燃烧 5 秒（10 下），每层每下目标最大生命千分之 2，再打叠一层、刷新时间。
#[test]
fn a_basic_attack_burns_the_champion_and_its_own_burn_never_counts_as_a_hit() {
    let mut b = Bench::new(&[(3, &[Ev::Firebrand])]);
    b.near(8, 3, 60_000);
    b.go(2);
    b.strike(3, 8, 150);
    b.go(4);
    assert!(b.w.hits_on(8).is_empty(), "a hit that is no basic attack burns nothing");
    b.go(40);
    b.attack(3);
    b.strike(3, 8, 150);
    b.go(42);
    let burns = b.w.hits_on(8);
    assert_eq!(burns.len(), 1, "the first pulse at once");
    assert_eq!(burns[0], (b.w.ent(3), b.w.ent(8), procs::firebrand_per(2000, 1), AP, DOT));
    b.go(42 + 30 * procs::FIREBRAND_PULSES as usize + 40);
    let burns = b.w.hits_on(8);
    assert_eq!(burns.len(), procs::FIREBRAND_PULSES as usize, "ten pulses, never more (the burn is no hit): {burns:?}");
    assert!(b.w.hits_on(7).is_empty());
    assert_eq!(b.p.summary(), "firebrand 1");
    // a second basic attack while it burns: two stacks, the time refreshed
    let mut c = Bench::new(&[(3, &[Ev::Firebrand])]);
    c.near(8, 3, 60_000);
    c.go(2);
    c.attack(3);
    c.strike(3, 8, 150);
    c.go(4);
    c.go(60);
    c.attack(3);
    c.strike(3, 8, 150);
    c.go(62);
    c.go(100);
    let amounts: Vec<usize> = c.w.hits_on(8).iter().map(|x| x.2).collect();
    assert!(amounts.contains(&procs::firebrand_per(2000, 2)), "{amounts:?}");
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
    assert_eq!(stack.hp_mult, 6 * procs::TANK_HP_PCT);
    assert_eq!(b.w.has(0, procs::G_TANK[2]), 1, "three size steps at six");
    assert_eq!(b.w.has(0, procs::G_TANK[0]), 0, "only the one step");
    assert_eq!(b.w.has(1, procs::E_EXCITED), 1, "the killer gets excited");
    // a red kill gives blue nothing
    b.w.kills.push(KillLogV1 { tick: 0, killer_team: 1, killer_position: 0, killed_position: 0, ..KillLogV1::default() });
    b.go(6);
    assert_eq!(b.p.stacks(0), (6, 0));
    // he dies (keeping 35%: 6 -> 2) and comes back: what is left comes back on his new body
    b.w.die(0);
    b.go(8);
    assert_eq!(b.p.stacks(0), (2, 0));
    b.w.respawn(0);
    b.go(10);
    assert_eq!(b.w.has(0, procs::S_TANK), 1);
    assert_eq!(b.w.has(0, procs::G_TANK[0]), 1);
}

#[test]
fn casts_punch_the_cooldowns_fire_missiles_and_take_the_final_form() {
    let mut b = Bench::new(&[(3, &[Ev::MysticPunch, Ev::MagicMissile, Ev::FinalForm])]);
    b.near(8, 3, 60_000);
    b.go(2);
    // a basic attack: all three slots, ultimate too (0.4.0)
    b.w.players[3].cds[0] = 50;
    b.go(4);
    let r = |k| (b.w.ent(3), k, procs::PUNCH_TICKS);
    assert_eq!(b.w.reduced, vec![r(1), r(2), r(3)]);
    // a skill that hits a champion: three true-damage missiles fly at him and land one after another
    b.w.players[3].cds[1] = 300;
    b.go(6);
    b.strike(3, 8, 100);
    b.go(8);
    assert!(b.w.hits.is_empty(), "still flying");
    b.go(8 + procs::MISSILE_MIN_T + 30);
    let each = 2000 * procs::missile_permille(1) / 1000;
    assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), each, FIXED, 1); procs::MISSILE_N]);
    // the same skill again at once: not within 6 s
    b.w.players[3].cds[1] = 600;
    b.go(50);
    b.strike(3, 8, 100);
    b.go(52);
    b.go(100);
    assert_eq!(b.w.hits_on(8).len(), procs::MISSILE_N);
    // the ultimate
    b.w.players[3].cds[3] = 3000;
    b.go(110);
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
    assert_eq!(b.w.shields, vec![(b.w.ent(2), procs::colossus_shield(2000, 1), procs::COLOSSUS_T)]);
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

/// 本包给的护盾还在时，屏幕那一场每一步在他身上记一圈光、跟着他走；盾打没了、时间到了就灭，屏幕外的模拟一条都不记
/// （0.3.3，用户：「现在有些海克斯比如什么加护盾我是看不到特效的」「或者是不明显？」）。
#[test]
fn a_shield_glows_on_its_holder_while_it_holds() {
    let grant = |screen: bool| {
        let mut b = Bench::new(&[(2, &[Ev::Colossus])]);
        b.screen = screen;
        b.near(7, 2, 50_000);
        b.go(2);
        b.w.players[2].cds[1] = 400;
        b.go(4);
        b.w.champ_mut(7).cc.push(CcV1::stun(60));
        b.go(10);
        assert_eq!(b.w.shields.len(), 1, "the colossus's shield");
        b
    };
    let glows = |b: &Bench| -> Vec<(usize, (u64, u64))> {
        b.p.out.iter().filter(|o| o.show == Show::ShieldGlow).map(|o| (o.tick, o.at)).collect()
    };
    // every step from the one it was given on, where he is, a step long
    let mut b = grant(true);
    let g = glows(&b);
    let from = g[0].0;
    assert!(g.iter().enumerate().all(|(i, x)| x.0 == from + i * procs::EVERY && x.1 == b.w.champ(2).pos), "{g:?}");
    assert!(b.p.out.iter().filter(|o| o.show == Show::ShieldGlow).all(|o| o.dur as usize == procs::EVERY));
    // it follows him
    b.w.champ_mut(2).pos.0 += 30_000;
    b.go(20);
    assert_eq!(glows(&b).last().copied(), Some((20, b.w.champ(2).pos)));
    // broken: the next look sees no shield, no more glow
    b.w.champ_mut(2).shield = 0;
    b.go(40);
    assert_eq!(glows(&b).last().map(|x| x.0), Some(20));
    // left alone it lasts as long as the shield
    let mut c = grant(true);
    c.go(400);
    let g = glows(&c);
    assert_eq!(g.len(), procs::COLOSSUS_T / procs::EVERY, "{g:?}");
    assert!(g.iter().all(|x| x.0 < from + procs::COLOSSUS_T));
    // off the screen: nothing
    let mut d = grant(false);
    d.go(100);
    assert!(glows(&d).is_empty());
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
            b.attack(3);
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

// ===================== 0.4.0 第二批 =====================

/// 亡命之徒：打中 10 次叠满以后一直挂着「不会死」；挨了致命的一下（被它留在 1 点生命）倒下 4 秒（无敌，自己眩晕），然后回到
/// 35% 最大生命（1 级）、拿 15 秒的加成；90 秒的冷却里再叠满也不挂。
#[test]
fn hellbent_holds_off_the_lethal_hit_and_gets_back_up() {
    use procs::b2::*;
    let mut b = Bench::new(&[(3, &[Ev::Hellbent])]);
    b.near(8, 3, 30_000);
    b.go(2);
    for i in 0..HELL_MOST {
        b.strike(3, 8, 10);
        b.go(4 + (i + 1) * 24);
        assert_eq!(b.w.has(3, E_HELL_GUARD), (i + 1 == HELL_MOST) as usize, "{} hits", i + 1);
    }
    let t = b.w.tick;
    b.w.champ_mut(3).hp = 1;
    b.go(t + 2);
    assert_eq!(b.w.has(3, E_HELL_DOWN), 1, "down");
    assert_eq!(b.w.has(3, E_HELL_GUARD), 0);
    let me = b.w.ent(3);
    assert!(b.w.ccs.iter().any(|(e, c)| *e == me && c.kind == CcKindV1::Stun.code()), "{:?}", b.w.ccs);
    assert!(b.w.heals.is_empty());
    b.go(t + 2 + HELL_DOWN + 2);
    let up: usize = b.w.heals.iter().filter(|h| h.1 == me).map(|h| h.2).sum();
    assert_eq!(up, 2000 * hell_hp_pct(1) / 100 - 1, "back up at 35% max health");
    let buff = b.w.champ(3).buffs.iter().find(|x| x.name() == E_HELL).copied().expect("the 15 s buff");
    // 攻击力 200、法强 300：给法强
    assert_eq!((buff.attack, buff.magic_power), (0, hell_ap(1) as i32));
    let t = b.w.tick;
    for i in 0..HELL_MOST {
        b.strike(3, 8, 10);
        b.go(t + (i + 1) * 24);
    }
    assert_eq!(b.w.has(3, E_HELL_GUARD), 0, "on cooldown: no guard");
}

/// 史莱姆时间：在战斗中、身边有敌方英雄时炸一圈，打中的人和自己中间留一团黏液；自己走过去吃掉回血，敌人先踩到就没了。
#[test]
fn slime_time_bursts_and_its_blobs_go_to_whoever_gets_there_first() {
    use procs::b2::*;
    let mut b = Bench::new(&[(3, &[Ev::SlimeTime])]);
    b.near(8, 3, 30_000);
    b.go(2);
    assert!(b.w.hits_on(8).is_empty(), "not in combat yet");
    b.strike(3, 8, 10);
    b.go(6);
    let each = slime_damage(1, 2000, 200, 300);
    assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), each, AP, 1)]);
    let (a, v) = (b.w.champ(3).pos, b.w.champ(8).pos);
    let mid = ((a.0 + v.0) / 2, a.1);
    b.w.champ_mut(3).pos = mid;
    b.go(10);
    let me = b.w.ent(3);
    assert_eq!(b.w.heals, vec![(me, me, blob_heal(1, 2000))]);
    b.go(40);
    assert_eq!(b.w.heals.len(), 1, "eaten once");
    // the next burst: the enemy steps on the blob first
    b.w.champ_mut(3).pos = a;
    b.strike(3, 8, 10);
    b.go(6 + SLIME_CD + 4);
    assert_eq!(b.w.hits_on(8).len(), 2);
    b.w.champ_mut(8).pos = mid;
    b.go(6 + SLIME_CD + 8);
    b.w.champ_mut(3).pos = mid;
    b.go(6 + SLIME_CD + 12);
    assert_eq!(b.w.heals.len(), 1, "crushed: nothing to eat");
}

/// 小蜜蜂：技能命中英雄扔一个蜂巢，1.1 秒后落地，周围的敌方英雄 4 下魔法伤害（每 0.5 秒）、减速；冷却里的技能命中不扔。
#[test]
fn bees_swarm_where_the_hive_lands() {
    use procs::b2::*;
    let mut b = Bench::new(&[(3, &[Ev::Bees])]);
    b.near(8, 3, 30_000);
    b.go(2);
    b.w.players[3].cds[1] = 300;
    b.go(4);
    b.strike(3, 8, 10);
    b.go(6);
    assert!(b.w.hits_on(8).is_empty(), "still flying");
    b.go(6 + BEES_FLIGHT + 2);
    let sting = bees_sting(1, 200, 300);
    assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), sting, AP, DOT)]);
    assert_eq!(b.w.has(8, E_BEES), 1, "slowed");
    b.go(6 + BEES_FLIGHT + 2 + 3 * BEES_EVERY + 4);
    assert_eq!(b.w.hits_on(8).len(), BEES_STINGS as usize);
    b.w.players[3].cds[1] = 600;
    let t = b.w.tick;
    b.go(t + 2);
    b.strike(3, 8, 10);
    b.go(t + 4 + BEES_FLIGHT + 4 * BEES_EVERY);
    assert_eq!(b.w.hits_on(8).len(), BEES_STINGS as usize, "on cooldown: no second hive");
}

/// 双生火焰（对齐英雄联盟）：技能命中时 1 枚，暴击率每 33% 多 1 枚，最多 4 枚。
#[test]
fn twin_fire_fires_more_flames_with_more_crit() {
    use procs::b2::*;
    for (crit, n) in [(0usize, 1usize), (40, 2), (70, 3), (100, 4)] {
        let mut b = Bench::new(&[(3, &[Ev::TwinFire])]);
        b.near(8, 3, 30_000);
        b.w.champ_mut(3).stat.crit_chance = crit;
        b.go(2);
        b.w.players[3].cds[1] = 300;
        b.go(4);
        b.strike(3, 8, 10);
        b.go(80);
        let each = twin_damage(1, 200, 300);
        assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), each, AP, 1); n], "crit {crit}");
    }
}

/// 无尽收割：在战斗中、身边有敌方英雄时蓄力 1.25 秒挥一圈：外圈全额、内圈一半；外圈打中的回复 18% 已损失生命。
#[test]
fn endless_decimation_hits_the_outer_ring_hardest_and_heals() {
    use procs::b2::*;
    let mut b = Bench::new(&[(3, &[Ev::Decimation])]);
    b.near(8, 3, 30_000);
    b.near(9, 3, 10_000);
    b.w.champ_mut(3).hp = 1000;
    b.go(2);
    b.strike(3, 8, 10);
    b.go(6);
    assert!(b.w.hits.is_empty(), "winding up");
    b.go(6 + DECI_WINDUP + 2);
    let full = deci_damage(1, 200, 300);
    assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), full, AD, 1)]);
    assert_eq!(b.w.hits_on(9), vec![(b.w.ent(3), b.w.ent(9), full / 2, AD, 1)]);
    let me = b.w.ent(3);
    assert_eq!(b.w.heals, vec![(me, me, 1000 * DECI_HEAL_PCT / 100)]);
}

/// 渴血：打中英雄回复这一下伤害的 15%。
#[test]
fn goredrink_heals_a_share_of_the_damage() {
    use procs::b2::*;
    let mut b = Bench::new(&[(3, &[Ev::Goredrink])]);
    b.near(8, 3, 30_000);
    b.w.champ_mut(3).hp = 1000;
    b.go(2);
    b.strike(3, 8, 400);
    b.go(4);
    let me = b.w.ent(3);
    assert_eq!(b.w.heals, vec![(me, me, 400 * GORE_PCT as usize / 100)]);
}

/// 王冠之重：参与击杀叠层，战斗中才减移动速度，阵亡掉一半；物理转魔法按比开局多出来的攻击力加法强，魔法转物理按法强加攻击力
/// （都不扣原来的）。
#[test]
fn the_crown_stacks_on_takedowns_and_the_converters_add_without_taking() {
    use procs::b2::*;
    let mut b = Bench::new(&[(1, &[Ev::HeavyCrown]), (2, &[Ev::Adapt]), (4, &[Ev::Escapade])]);
    b.near(8, 1, 30_000);
    b.go(2);
    let find = |b: &Bench, seat: usize, name: &str| {
        b.w.champ(seat).buffs.iter().find(|x| x.name() == name).copied().unwrap_or_else(|| panic!("{name}"))
    };
    let c = find(&b, 1, D_CROWN);
    assert_eq!((c.attack, c.magic_power, c.attack_mult, c.move_speed_mult), (CROWN_AD, CROWN_AP, CROWN_PCT, 0));
    for _ in 0..3 {
        b.w.kills.push(KillLogV1 { tick: 0, killer_team: 0, killer_position: 1, killed_position: 2,
                                   ..KillLogV1::default() });
    }
    b.go(4);
    assert_eq!(find(&b, 1, D_CROWN).attack_mult, CROWN_PCT + 3 * CROWN_EACH);
    // in combat: slower
    b.strike(1, 8, 10);
    b.go(8);
    assert_eq!(find(&b, 1, D_CROWN).move_speed_mult, -(CROWN_MS_X10 + 3 * CROWN_MS_EACH_X10) / 10);
    // dies: half the stacks (3 -> 1), back on the new body
    b.w.die(1);
    b.go(10);
    b.w.respawn(1);
    b.go(12);
    assert_eq!(find(&b, 1, D_CROWN).attack_mult, CROWN_PCT + CROWN_EACH);
    let a = find(&b, 2, D_ADAPT);
    assert_eq!((a.magic_power, a.magic_power_mult, a.attack), (0, ADAPT_AP_MULT, 0), "nothing gained yet");
    b.w.champ_mut(2).stat.attack = 260;
    b.go(14);
    assert_eq!(find(&b, 2, D_ADAPT).magic_power, (60 * 10 / ADAPT_AD_X10) as i32);
    let e = find(&b, 4, D_ESCAPADE);
    assert_eq!((e.attack, e.attack_mult, e.magic_power), ((300 * 100 / ESC_AP_X100) as i32, ESC_AD_MULT, 0));
}

// ===================== 0.5.0 =====================

/// 捐赠拿到时给一次 1750 金币；夺金打中英雄额外魔法伤害、30 金币，同一个人 30 秒一次。
#[test]
fn donation_pays_once_and_goldrend_pays_per_champion() {
    use procs::b3::*;
    let mut b = Bench::new(&[(3, &[Ev::Donation, Ev::Goldrend])]);
    b.near(8, 3, 30_000);
    b.go(2);
    b.go(40);
    assert_eq!(b.w.golds, vec![(3, DONATION_GOLD)], "once");
    b.strike(3, 8, 10);
    b.go(44);
    assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), goldrend_damage(1, 200, 300), AP, 1)]);
    assert_eq!(b.w.golds, vec![(3, DONATION_GOLD), (3, GOLDREND_GOLD)]);
    b.strike(3, 8, 10);
    b.go(80);
    assert_eq!(b.w.hits_on(8).len(), 1, "30 s per champion");
}

/// 属性铁砧：拿到时挑好、挂成一个 buff，复活后补回。
#[test]
fn stat_anvils_go_on_and_come_back_after_a_respawn() {
    use procs::b3::*;
    let mut b = Bench::new(&[(3, &[Ev::Stats2])]);
    b.go(2);
    let want = anvils(b.w.seed, 3, Ev::Stats2, &Default::default()).unwrap().0;
    assert_eq!(b.w.champ(3).buffs.iter().find(|x| x.name() == S_ANVIL[1]), Some(&want));
    b.w.die(3);
    b.go(4);
    b.w.respawn(3);
    b.go(6);
    assert_eq!(b.w.has(3, S_ANVIL[1]), 1, "back on the new body");
}

/// 龙魂：炼狱龙魂打中时爆炸（3 秒一次）；英雄身上已经有大小龙给的炼狱龙魂时换成别的一种；山脉龙魂没挨打时给护盾。
#[test]
fn souls_work_and_never_double_the_dragons_own() {
    use procs::b3::*;
    let mut b = Bench::new(&[(3, &[Ev::InfernalSoul])]);
    b.near(8, 3, 30_000);
    b.go(2);
    assert_eq!(b.p.souls_of(3), vec![Element::Infernal]);
    b.strike(3, 8, 10);
    b.go(6);
    assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), infernal_damage(200, 300), AP, 1)]);
    b.strike(3, 8, 10);
    b.go(40);
    assert_eq!(b.w.hits_on(8).len(), 1, "3 s cooldown");
    let mut c = Bench::new(&[(3, &[Ev::InfernalSoul])]);
    c.w.champ_mut(3).buffs.push(BuffV1::named("league_dragons_soul_infernal"));
    c.go(2);
    let s = c.p.souls_of(3);
    assert_eq!(s.len(), 1);
    assert_ne!(s[0], Element::Infernal, "the dragons' own is not doubled");
    let mut m = Bench::new(&[(3, &[Ev::MountainSoul])]);
    m.go(2);
    let me = m.w.ent(3);
    assert_eq!(m.w.shields, vec![(me, mountain_shield(200, 300, 2000), MOUNTAIN_T)]);
    m.w.hurt(3, 5_000);
    m.w.champ_mut(3).hp = 1500;
    m.go(100);
    assert_eq!(m.w.shields.len(), 1, "hit: no shield for 5 s");
    m.go(100 + MOUNTAIN_IDLE + 40);
    assert_eq!(m.w.shields.len(), 2);
}

/// 男爵之手：法强高给法强 +25%；身边的己方小兵挂上男爵的 buff，远的、对面的不挂。
#[test]
fn the_hand_of_baron_powers_up_and_boosts_nearby_minions() {
    use procs::b3::*;
    let mut b = Bench::new(&[(3, &[Ev::HandOfBaron])]);
    let at = b.w.champ(3).pos;
    let near = b.w.minion(0, (at.0 + 50_000, at.1));
    let far = b.w.minion(0, (at.0 + 300_000, at.1));
    let theirs = b.w.minion(1, (at.0 + 20_000, at.1));
    b.go(2);
    let d = b.w.champ(3).buffs.iter().find(|x| x.name() == D_BARON).copied().expect("the hand");
    assert_eq!((d.attack_mult, d.magic_power_mult), (0, BARON_PCT));
    let boosted = |u: usize| b.w.units[u].buffs.iter().any(|x| x.name() == MINION_BOOST);
    assert!(boosted(near) && !boosted(far) && !boosted(theirs));
}

/// 技能海克斯照选的技能：虹吸选技能 2 就只认技能 2；过载选大招，放别的技能时大招转好；面包和黄油放技能时冷却减半；恐惧选技能 2，
/// 放的时候吓跑身边的人。
#[test]
fn skill_augments_follow_the_chosen_ability() {
    let mut b = Bench::new(&[(3, &[Ev::Siphon, Ev::Overloaded, Ev::BreadButter, Ev::Terror])]);
    b.p.picked(3, Ev::Siphon, 0, 2);
    b.p.picked(3, Ev::Overloaded, 1, 3);
    b.p.picked(3, Ev::Terror, 2, 2);
    b.near(8, 3, 30_000);
    b.go(2);
    b.w.players[3].cds[1] = 600;
    b.go(4);
    b.strike(3, 8, 100);
    b.go(6);
    let me = b.w.ent(3);
    assert!(b.w.reduced.contains(&(me, 1, 300)), "bread: half of 600 {:?}", b.w.reduced);
    assert!(b.w.reduced.contains(&(me, 3, procs::b2::RESET)), "overloaded: the ultimate is ready again {:?}", b.w.reduced);
    assert!(b.w.heals.is_empty(), "siphon is on skill 2");
    b.w.players[3].cds[2] = 900;
    b.go(8);
    b.strike(3, 8, 100);
    b.go(10);
    assert_eq!(b.w.heals, vec![(me, me, 30)]);
    let them = b.w.ent(8);
    assert!(b.w.ccs.iter().any(|(e, c)| *e == them && c.kind == CcKindV1::Fear.code()), "{:?}", b.w.ccs);
}

/// 坚定意志：选定的技能打中英雄永久 +2 护甲（下一层魔抗），不是第 1 个海克斯再 +20；深红钴蓝：技能标记、普攻引爆、冷却减总冷却的
/// 65%；仁慈打击：放技能后的下一次普攻多打目标 3% 最大生命。
#[test]
fn resolute_stacks_cobalt_marks_and_mercy_waits_for_the_next_attack() {
    use procs::b3::*;
    let mut b = Bench::new(&[(3, &[Ev::StayResolute, Ev::CrimsonCobalt, Ev::MercysStrike])]);
    b.p.picked(3, Ev::StayResolute, 1, 1);
    b.near(8, 3, 30_000);
    b.go(2);
    b.w.players[3].cds[1] = 600;
    b.go(4);
    b.strike(3, 8, 100);
    b.go(6);
    let r = b.w.champ(3).buffs.iter().find(|x| x.name() == S_RESOLUTE).copied().expect("resolute");
    assert_eq!((r.defence, r.magic_resistance), (2 + RESOLUTE_BONUS, RESOLUTE_BONUS));
    assert_eq!(b.w.has(3, E_MERCY), 1, "armed by the cast");
    b.attack(3);
    b.strike(3, 8, 100);
    b.go(8);
    let (me, them) = (b.w.ent(3), b.w.ent(8));
    let hits = b.w.hits_on(8);
    assert!(hits.contains(&(me, them, cobalt_damage(1, 200, 300), AP, 1)), "{hits:?}");
    assert!(hits.contains(&(me, them, 2000 * MERCY_PERMILLE / 1000, AP, 1)), "{hits:?}");
    assert!(b.w.reduced.contains(&(me, 1, 600 * COBALT_CUT_PCT / 100)), "{:?}", b.w.reduced);
    assert_eq!(b.w.has(3, E_MERCY), 0, "used up");
}

/// 高压锻炉：身边 30000 以内的敌方英雄每秒受你最大生命 0.5%；超远狙击：60000 以外的技能命中 15 次以后召来流星。
#[test]
fn the_cooker_burns_around_and_downtown_calls_meteors_after_its_quest() {
    use procs::b3::*;
    let mut b = Bench::new(&[(3, &[Ev::PressureCooker])]);
    b.near(8, 3, 20_000);
    b.near(9, 3, 45_000);
    b.go(2);
    b.go(2 + COOKER_EVERY * 2 + 2);
    assert_eq!(b.w.hits_on(8), vec![(b.w.ent(3), b.w.ent(8), 2000 * COOKER_PERMILLE / 1000, AP, DOT); 3]);
    assert!(b.w.hits_on(9).is_empty(), "out of reach");
    let mut d = Bench::new(&[(3, &[Ev::FromDowntown])]);
    d.near(8, 3, 70_000);
    d.go(2);
    for i in 0..DOWNTOWN_QUEST as usize {
        d.w.players[3].cds[1] += 600;
        d.strike(3, 8, 10);
        d.go(4 + (i + 1) * 24);
    }
    assert!(d.w.hits_on(8).is_empty(), "the quest first");
    let t = d.w.tick;
    d.w.players[3].cds[1] += 600;
    d.strike(3, 8, 10);
    d.go(t + 4 + METEOR_T + 4);
    let want = downtown_damage(1, 200, 300, 70_000);
    assert_eq!(d.w.hits_on(8), vec![(d.w.ent(3), d.w.ent(8), want, AP, 1)]);
}

/// 潘朵拉的盒子换掉一个海克斯：它叠的层、随场上变的属性一起摘掉。
#[test]
fn forgetting_an_augment_takes_its_stacks_off() {
    let mut b = Bench::new(&[(0, &[Ev::TankEngine, Ev::LichBrain])]);
    b.go(2);
    for _ in 0..2 {
        b.w.kills.push(KillLogV1 { tick: 0, killer_team: 0, killer_position: 0, killed_position: 2, assist_count: 0,
                                   assist_positions: [0, 0, 0, 0] });
    }
    b.go(4);
    assert_eq!(b.w.has(0, procs::S_TANK), 1);
    assert_eq!(b.w.has(0, procs::b2::D_LICH), 1);
    let e = b.w.ent(0);
    let (p, w) = (&mut b.p, &mut b.w);
    with_sim(w, |sim| {
        p.forget(sim, 0, Some(e), Ev::TankEngine);
        p.forget(sim, 0, Some(e), Ev::LichBrain);
    });
    assert_eq!(b.w.has(0, procs::S_TANK), 0);
    assert_eq!(b.w.has(0, procs::b2::D_LICH), 0);
    assert_eq!(b.p.stacks(0), (0, 0));
}
