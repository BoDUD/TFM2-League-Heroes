//! The hook on small simulations of one's own (`mock.rs`): whole matches, twin presims run side by side, the souls, the
//! Elder Dragon's burn and execute, Baron Nashor, the Workshop mod, a lost state rebuilt from the nexus, the screen's feed.

use std::sync::Mutex;

use super::mock::{self, Unit, World};
use super::rules::{self, Element, Ev, Record};
use super::*;

/// Tests that touch the screen's feed (one per process) take this lock.
pub(crate) static GLOBALS: Mutex<()> = Mutex::new(());

const CAST: [&str; 10] = [
    "league_garen", "league_leesin", "league_ahri", "league_jinx", "league_thresh",
    "league_darius", "league_viego", "league_syndra", "league_caitlyn", "league_lux",
];

fn log_to_temp() {
    std::env::set_var("LEAGUE_DRAGONS_LOG", std::env::temp_dir().join("league_dragons_test.log"));
}

fn tick(w: &mut World) {
    mock::with_sim(w, |sim| Dragons.on_match_tick(sim, 0));
    w.tick += 1;
}

fn start(w: &mut World) {
    mock::with_sim(w, |sim| Dragons.on_match_start(sim));
}

fn run_to(w: &mut World, t: usize) {
    while w.tick < t {
        tick(w);
    }
}

fn advance(w: &mut World, ticks: usize) {
    let t = w.tick + ticks;
    run_to(w, t);
}

fn number(w: &World) -> u64 {
    w.units[0].buffs.iter().find_map(|b| parse_tag(b.name())).expect("a tag on the nexus")
}

fn state<R>(w: &World, f: impl FnOnce(&mut Sim) -> R) -> R {
    let mut book = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    f(book.sims.get_mut(&number(w)).expect("its state"))
}

fn record(w: &World, unit: usize) -> Record {
    w.units[unit].buffs.iter().find_map(|b| Record::parse(b.name())).expect("a state record")
}

fn events(w: &World) -> Vec<Ev> {
    let mut v: Vec<(u8, usize, Ev)> = w.units[0].buffs.iter().filter_map(|b| rules::parse_event(b.name())).collect();
    v.sort_by_key(|e| e.0);
    v.into_iter().map(|e| e.2).collect()
}

/// A seed whose rift (the soul's element) is `e`.
fn seed_for(e: Element, from: u64) -> u64 {
    (from..).find(|s| rules::order(*s)[2] == e).expect("a seed")
}

/// The camp spawns, the hook's scan (every SCAN ticks) marks it.
fn spawn_serpen(w: &mut World) -> usize {
    let s = w.spawn_serpen();
    let t = w.tick + SCAN + 1;
    run_to(w, t);
    s
}

fn spawn_epic(w: &mut World) -> usize {
    let e = w.spawn_epic();
    let t = w.tick + SCAN + 1;
    run_to(w, t);
    e
}

/// Player `p`'s champion moved to `at`.
fn place(w: &mut World, p: usize, at: (u64, u64)) {
    w.champ_mut(p).at = at;
}

fn ent(w: &World, p: usize) -> usize {
    w.players[p].champ
}

/// The whole hook over a match on a presim: League's order, the stacks and the neutralized native buff, the soul at the
/// first team's fourth drake, the Elder Dragon after it with its burn and execute, Baron Nashor with its minions, the
/// state record and the events on the nexuses.
#[test]
fn a_whole_match_on_a_mock() {
    log_to_temp();
    let seed = seed_for(Element::Infernal, 7_000);
    let o = rules::order(seed);
    let mut w = World::new(seed, SimOriginKindV1::ServerPresim, CAST);
    start(&mut w);
    tick(&mut w);
    // numbered on both nexuses; the record there from the start, the first drake's element next
    assert!(w.units[1].buffs.iter().any(|b| parse_tag(b.name()) == Some(number(&w))));
    let r = record(&w, 0);
    assert_eq!((r.order, r.cur, r.seq), ([o[0].code(), o[1].code(), o[2].code()], o[0].code(), 0));
    assert_eq!(record(&w, 1), r, "the same record on both nexuses");

    // ---- drake 1: blue
    let s1 = spawn_serpen(&mut w);
    assert!(w.names(s1).contains(&rules::marker(o[0])), "{:?}", w.names(s1));
    assert!(record(&w, 0).serpen_alive);
    w.secure(s1, 1);
    tick(&mut w);
    for p in 0..5 {
        let n = w.has(p, rules::NAT).expect("the neutralizer");
        assert_eq!((n.attack_mult, n.magic_power_mult, n.defence_mult, n.magic_resistance_mult, n.move_speed_mult),
                   (-4, -4, -4, -4, -1), "player {p}");
        assert!(rules::same_stats(&w.has(p, &rules::drake_name(o[0])).unwrap(), &rules::drake_buff(o[0], 1)));
    }
    for p in 5..10 {
        assert!(w.has(p, rules::NAT).is_none() && w.has(p, &rules::drake_name(o[0])).is_none(), "red has nothing");
    }
    let r = record(&w, 0);
    assert_eq!(r.stacks[0][o[0].slot().unwrap()], 1);
    assert_eq!((r.cur, r.serpen_alive), (o[1].code(), false), "the second drake's element next");

    // ---- drake 2: red; the rift's element after it
    let s2 = spawn_serpen(&mut w);
    assert!(w.names(s2).contains(&rules::marker(o[1])));
    w.secure(s2, 6);
    tick(&mut w);
    assert_eq!(w.has(6, rules::NAT).map(|n| n.attack_mult), Some(-4));
    assert!(w.has(8, &rules::drake_name(o[1])).is_some());
    assert_eq!(record(&w, 0).cur, o[2].code());

    // ---- drakes 3-5: blue - its fourth claims the rift's soul (Infernal)
    for k in 0..3 {
        let s = spawn_serpen(&mut w);
        assert!(w.names(s).contains(&rules::marker(o[2])), "drake {} is the rift's", k + 3);
        w.secure(s, 1);
        tick(&mut w);
    }
    let r = record(&w, 0);
    assert_eq!(r.soul, Some((0, Element::Infernal.code())));
    assert_eq!(r.stacks[0].iter().sum::<u8>(), 4);
    assert_eq!(r.cur, Element::Elder.code(), "the Elder Dragon from now on");
    for p in 0..5 {
        assert!(w.has(p, &rules::soul_name(Element::Infernal)).is_some());
        // four native buffs on each, all four neutralized
        assert_eq!(w.count(p, rules::NATIVE), 4);
        assert_eq!(w.has(p, rules::NAT).map(|n| n.attack_mult), Some(-16));
        assert_eq!(w.count(p, rules::NAT), 1, "one neutralizer, replaced as the stacks grow");
    }
    let ev = events(&w);
    assert!(ev.contains(&Ev::Soul { team: 0, element: Element::Infernal }));
    assert_eq!(ev.iter().filter(|e| matches!(e, Ev::Drake { .. })).count(), 5);

    // ---- the Elder Dragon: red takes it
    let s6 = spawn_serpen(&mut w);
    assert!(w.names(s6).contains(&rules::marker(Element::Elder)));
    assert!(events(&w).contains(&Ev::ElderSpawn));
    w.secure(s6, 6);
    tick(&mut w);
    let taken = w.tick - 1;
    for p in 5..10 {
        assert!(w.has(p, rules::ELDER).is_some(), "player {p} holds the Aspect of the Dragon");
    }
    let r = record(&w, 0);
    assert_eq!(r.elder, Some(rules::HoldRec { team: 1, lanes: 0b11111, until: taken + rules::ELDER_T }));
    assert_eq!(r.stacks[1].iter().sum::<u8>(), 1, "the Elder gives no drake stack");
    assert!(events(&w).contains(&Ev::ElderKilled { team: 1, lanes: 0b11111 }));

    // a holder (red jungle, player 6) beside blue's top (player 0) at 15%: his hit executes, the kill his
    place(&mut w, 6, (20_000, 100_000));
    tick(&mut w);
    w.champ_mut(0).hp = 150;
    w.hit(6, 0, 10);
    tick(&mut w);
    let blue_top = ent(&w, 0);
    let hits = w.hits_on(blue_top);
    assert_eq!(hits.len(), 1, "{hits:?}");
    assert_eq!(hits[0], (ent(&w, 6), blue_top, rules::execute_damage(140, 0, 1000), DamageTypeV1::Fixed.code(),
                         AttackTypeV1::Skill.code()));
    assert!(!w.units[blue_top].alive);
    assert!(w.units[blue_top].buffs.iter().any(|b| b.name() == rules::EXECUTED));
    assert!(events(&w).contains(&Ev::Execute { team: 1, lane: 1, victim_lane: 0 }));

    // blue's mid (player 2) at 80%: burnt, three ticks of true damage over 1.5 s, no execute
    place(&mut w, 2, (30_000, 120_000));
    tick(&mut w);
    w.hit(6, 2, 200);
    tick(&mut w);
    let mid = ent(&w, 2);
    assert!(w.units[mid].buffs.iter().any(|b| b.name() == rules::BURN));
    let t = w.tick + rules::BURN_T + 5;
    run_to(&mut w, t);
    let burns: Vec<_> = w.hits_on(mid).into_iter().filter(|h| h.4 == AttackTypeV1::Dot.code()).collect();
    assert_eq!(burns.len(), 3, "{burns:?}");
    assert!(burns.iter().all(|h| h.2 == rules::burn_total(100) / 3 && h.3 == DamageTypeV1::Fixed.code()));
    assert!(w.units[mid].alive, "80% is no execute");

    // a holder dies: his Aspect ends, his next life has none
    // (the champions are looked at every KEEP_EVERY ticks)
    w.die(7);
    advance(&mut w, KEEP_EVERY);
    assert_eq!(record(&w, 0).elder.map(|h| h.lanes), Some(0b11011), "lane 2 is gone");
    w.respawn(7);
    advance(&mut w, KEEP_EVERY);
    assert!(w.has(7, rules::ELDER).is_none());
    assert!(w.has(7, &rules::drake_name(o[1])).is_some(), "his drake stack is back on his next life");
    // the game gives its drake buff for the Elder Dragon too: two on red (drake 2, the Elder), both still cancelled
    assert_eq!(w.count(7, rules::NATIVE), 2);
    assert_eq!(w.has(7, rules::NAT).map(|n| n.attack_mult), Some(-8), "the native buffs the game kept are cancelled");
    // the Aspect runs out
    run_to(&mut w, taken + rules::ELDER_T + 2);
    assert!(w.has(5, rules::ELDER).is_none() && w.has(9, rules::ELDER).is_none());
    assert_eq!(record(&w, 0).elder, None);

    // ---- Baron Nashor: blue's bottom (player 3) secures it
    let e = spawn_epic(&mut w);
    assert!(record(&w, 0).epic_alive);
    w.secure(e, 3);
    tick(&mut w);
    let baron_at = w.tick - 1;
    assert!(events(&w).contains(&Ev::BaronKilled { team: 0, lanes: 0b11110 }), "blue's top was executed: not a holder");
    let b = w.has(3, rules::BARON).expect("Hand of Baron");
    assert_eq!((b.attack_mult, b.magic_power_mult), (20, 20));
    assert!(w.has(0, rules::BARON).is_none(), "dead when it fell");
    // minions: blue's beside him and far from every holder, red's beside him
    let at3 = w.champ(3).at;
    let near = w.spawn(Unit::new(EntityKindV1::Minion, 0, (at3.0 + 50_000, at3.1), "melee_minion", 400));
    let far = w.spawn(Unit::new(EntityKindV1::Minion, 0, (at3.0 + 900_000, at3.1 + 900_000), "melee_minion", 400));
    let foe = w.spawn(Unit::new(EntityKindV1::Minion, 1, (at3.0 + 40_000, at3.1), "melee_minion", 400));
    let t = (w.tick / rules::BOOST_EVERY + 1) * rules::BOOST_EVERY + 1;
    run_to(&mut w, t);
    let boost = w.units[near].buffs.iter().find(|b| b.name() == rules::MINION_BOOST).copied().expect("boosted");
    assert_eq!((boost.damaged_reduce, boost.attack_mult), (40, 30));
    assert!(w.names(far).is_empty() && w.names(foe).is_empty());
    assert_eq!(w.units[near].buffs.iter().filter(|b| b.name() == rules::MINION_BOOST).count(), 1, "refreshed, not stacked");
    // it runs out after 120 s
    run_to(&mut w, baron_at + rules::BARON_T + 2);
    assert!((1..5).all(|p| w.has(p, rules::BARON).is_none()));
    assert_eq!(record(&w, 0).baron, None);

    // ---- the end
    w.end = true;
    tick(&mut w);
    state(&w, |s| {
        assert!(s.ended);
        assert_eq!((s.executes, s.drakes, s.soul), (1, 5, Some((0, Element::Infernal))));
        assert_eq!(s.stats, StatsWay::Path, "the statistics read by path");
        assert_eq!(s.deal_way, DealWay::Stats);
        assert!(s.boosts >= 2);
    });
}

/// Baron Nashor: the Hand of Baron ends for a holder who dies (his next life has none, the minions only he stood by are
/// no longer kept up) and for everyone after 120 s (no more minion boosts).
#[test]
fn the_hand_of_baron_ends_on_death_and_on_time() {
    log_to_temp();
    let mut w = World::new(81, SimOriginKindV1::ServerPresim, CAST);
    start(&mut w);
    tick(&mut w);
    let e = spawn_epic(&mut w);
    w.secure(e, 2);
    tick(&mut w);
    let taken = w.tick - 1;
    assert!((0..5).all(|p| w.has(p, rules::BARON).is_some()) && (5..10).all(|p| w.has(p, rules::BARON).is_none()));
    assert_eq!(record(&w, 0).baron, Some(rules::HoldRec { team: 0, lanes: 0b11111, until: taken + rules::BARON_T }));
    // a minion only blue's support (player 4, at 400000) stands by: 120000 from him, 156000 from player 3
    let at4 = w.champ(4).at;
    let m = w.spawn(Unit::new(EntityKindV1::Minion, 0, (at4.0, at4.1 + 120_000), "range_minion", 250));
    let next = |w: &World| (w.tick / rules::BOOST_EVERY + 1) * rules::BOOST_EVERY + 1;
    let t = next(&w);
    run_to(&mut w, t);
    assert!(w.names(m).contains(&rules::MINION_BOOST.to_string()));
    // he dies: his hand is gone, the record drops lane 4; the minion's boost runs out (the mock keeps buffs: take it off)
    // and nobody renews it
    w.die(4);
    advance(&mut w, KEEP_EVERY);
    assert_eq!(record(&w, 0).baron.map(|h| h.lanes), Some(0b01111));
    w.units[m].buffs.clear();
    let t = next(&w);
    run_to(&mut w, t);
    assert!(w.names(m).is_empty(), "no holder near it");
    w.respawn(4);
    advance(&mut w, KEEP_EVERY);
    assert!(w.has(4, rules::BARON).is_none(), "not on his next life");
    assert!(w.has(3, rules::BARON).is_some());
    // 120 s: over for everyone, the minions beside them no longer renewed
    let near0 = w.spawn(Unit::new(EntityKindV1::Minion, 0, (10_000, 100_000), "melee_minion", 400));
    run_to(&mut w, taken + rules::BARON_T + 2);
    assert!((0..5).all(|p| w.has(p, rules::BARON).is_none()));
    assert_eq!(record(&w, 0).baron, None);
    w.units[near0].buffs.clear();
    advance(&mut w, 2 * rules::BOOST_EVERY);
    assert!(w.names(near0).is_empty());
    state(&w, |s| assert!(s.baron.iter().all(|h| h.is_none())));
}

/// Two presims of one set (the same seed, origin and entity ids) run interleaved: each has its own number, its own
/// stacks and its own record - and the same element order.
#[test]
fn twin_presims_keep_their_own_drakes() {
    log_to_temp();
    let seed = 91_337;
    let base = World::new(seed, SimOriginKindV1::ServerPresim, CAST);
    let (mut a, mut b) = (base.clone(), base.clone());
    start(&mut a);
    start(&mut b);
    tick(&mut a);
    tick(&mut b);
    assert_ne!(number(&a), number(&b));
    let (sa, sb) = (a.spawn_serpen(), b.spawn_serpen());
    assert_eq!(sa, sb, "the same entity id in both");
    for _ in 0..=SCAN {
        tick(&mut a);
        tick(&mut b);
    }
    let first = rules::marker(rules::order(seed)[0]);
    assert!(a.names(sa).contains(&first) && b.names(sb).contains(&first), "the same element in both");
    // blue takes it in a only
    a.secure(sa, 1);
    tick(&mut a);
    tick(&mut b);
    tick(&mut a);
    assert_eq!(record(&a, 0).stacks[0].iter().sum::<u8>(), 1);
    assert_eq!(record(&b, 0).stacks[0].iter().sum::<u8>(), 0);
    assert!(a.has(0, rules::NAT).is_some() && b.has(0, rules::NAT).is_none());
    // red takes it in b: a is untouched
    b.secure(sb, 7);
    for _ in 0..3 {
        tick(&mut b);
        tick(&mut a);
    }
    assert_eq!(record(&b, 0).stacks[1].iter().sum::<u8>(), 1);
    assert_eq!(record(&a, 0).stacks[1].iter().sum::<u8>(), 0);
    assert!(b.has(9, &rules::drake_name(rules::order(seed)[0])).is_some());
    assert!(a.has(9, &rules::drake_name(rules::order(seed)[0])).is_none());
}

/// The Workshop mod's records on the nexus: nothing applied, one CONFLICT, the record and the event say so.
#[test]
fn the_workshop_mod_makes_it_stand_aside() {
    log_to_temp();
    let mut w = World::new(5_150, SimOriginKindV1::ServerPresim, CAST);
    start(&mut w);
    tick(&mut w);
    // its records come a few ticks in (and the native drake buff it would strip anyway)
    w.units[0].buffs.push(BuffV1::named("sed_timer1:3840:8ca0:3840:4650:f"));
    w.units[0].buffs.push(BuffV1::named("sed_env_sites:8"));
    run_to(&mut w, 40);
    assert!(record(&w, 0).conflict);
    assert_eq!(events(&w), vec![Ev::Conflict]);
    let s = w.spawn_serpen();
    run_to(&mut w, 60);
    assert!(w.names(s).iter().all(|n| !n.starts_with("league_dragons_")), "no marker");
    w.secure(s, 1);
    run_to(&mut w, 200);
    for p in 0..10 {
        assert!(w.champ(p).buffs.iter().all(|b| !b.name().starts_with("league_dragons_")), "player {p}");
    }
    assert_eq!(record(&w, 0).stacks, [[0; 6]; 2]);
    assert_eq!(events(&w), vec![Ev::Conflict], "said once");
    state(&w, |s| assert!(s.conflict));
}

/// Gives team 0 `soul` straight in its state (as if it had its four drakes) and puts red's 5, 6, 7 next to blue's top.
fn soul_match(seed: u64, soul: Element) -> World {
    log_to_temp();
    let mut w = World::new(seed, SimOriginKindV1::ServerPresim, CAST);
    start(&mut w);
    tick(&mut w);
    state(&w, |s| {
        s.soul = Some((0, soul));
        s.ver[0] += 1;
    });
    place(&mut w, 5, (20_000, 100_000));
    place(&mut w, 6, (30_000, 110_000));
    place(&mut w, 7, (40_000, 90_000));
    place(&mut w, 8, (75_000, 100_000));
    tick(&mut w);
    w
}

#[test]
fn the_infernal_soul_blasts_every_three_seconds() {
    let mut w = soul_match(31, Element::Infernal);
    assert!(w.has(0, &rules::soul_name(Element::Infernal)).is_some());
    w.hit(0, 5, 30);
    tick(&mut w);
    let amount = rules::infernal_soul_damage(100, 50);
    let blasted: Vec<usize> = w.hits.iter().filter(|h| h.2 == amount && h.3 == DamageTypeV1::Ap.code()).map(|h| h.1).collect();
    // 5 (the one hit), 6 (14142 from him) and 7 (22360); 8 (55000) is out of the blast
    assert_eq!(blasted, vec![ent(&w, 5), ent(&w, 6), ent(&w, 7)]);
    // a second hit a second later: still cooling down; 3 s later: again
    advance(&mut w, 60);
    w.hit(0, 5, 30);
    tick(&mut w);
    assert_eq!(w.hits.iter().filter(|h| h.2 == amount).count(), 3);
    advance(&mut w, rules::INFERNAL_SOUL_CD);
    w.hit(0, 5, 30);
    tick(&mut w);
    assert_eq!(w.hits.iter().filter(|h| h.2 == amount).count(), 6);
    // its own blast is no hit of his (the tick it settles): no blast chains from it
    advance(&mut w, rules::INFERNAL_SOUL_CD + 30);
    assert_eq!(w.hits.iter().filter(|h| h.2 == amount).count(), 6);
}

#[test]
fn the_mountain_soul_shields_after_five_quiet_seconds() {
    let mut w = soul_match(32, Element::Mountain);
    let want = rules::mountain_soul_shield(100, 50, 1000);
    run_to(&mut w, rules::MOUNTAIN_SOUL_IDLE + 10);
    let top = ent(&w, 0);
    assert_eq!(w.units[top].shield, want);
    assert_eq!(w.shields.iter().filter(|s| s.0 == top).count(), 1);
    // hit through part of it: no top-up for 5 s, then back up to the full amount (not stacked past it)
    w.hit(5, 0, 120);
    tick(&mut w);
    advance(&mut w, rules::MOUNTAIN_SOUL_IDLE - 20);
    assert_eq!(w.units[top].shield, want - 120);
    advance(&mut w, 60);
    assert_eq!(w.units[top].shield, want);
    // red has no soul
    assert_eq!(w.units[ent(&w, 5)].shield, 0);
}

#[test]
fn the_ocean_soul_heals_over_four_seconds() {
    let mut w = soul_match(33, Element::Ocean);
    w.hit(0, 5, 30);
    tick(&mut w);
    advance(&mut w, 300);
    let per = rules::ocean_soul_heal(100, 50, 1000) / 8;
    let top = ent(&w, 0);
    let heals: Vec<usize> = w.heals.iter().filter(|h| h.0 == top).map(|h| h.1).collect();
    assert_eq!(heals, vec![per; 8]);
}

#[test]
fn the_cloud_soul_hastes_after_the_ultimate() {
    let mut w = soul_match(34, Element::Cloud);
    assert_eq!(w.has(2, &rules::soul_name(Element::Cloud)).map(|b| b.move_speed_mult), Some(15));
    w.players[2].cds[3] = 3000;
    tick(&mut w);
    let haste = w.has(2, rules::CLOUD_HASTE).expect("the haste");
    assert_eq!((haste.move_speed_mult, haste.duration_tick), (50, 360));
    // counting down is no cast
    w.players[2].cds[3] = 2900;
    tick(&mut w);
    assert_eq!(w.count(2, rules::CLOUD_HASTE), 1);
}

#[test]
fn the_hextech_soul_chains_to_three() {
    let mut w = soul_match(35, Element::Hextech);
    w.hit(0, 5, 30);
    tick(&mut w);
    let amount = rules::hextech_soul_damage(100, 50);
    let chained: Vec<usize> = w.hits.iter().filter(|h| h.2 == amount).map(|h| h.1).collect();
    // 5, then the two nearest within 40000 of 5: 6 (14142), 7 (22360); 8 (55000) is out
    assert_eq!(chained, vec![ent(&w, 5), ent(&w, 6), ent(&w, 7)]);
    for p in [5, 6, 7] {
        assert_eq!(w.has(p, rules::HEX_SLOW).map(|b| b.move_speed_mult), Some(-90));
    }
    assert!(w.has(8, rules::HEX_SLOW).is_none());
}

#[test]
fn the_chemtech_soul_holds_on_below_half() {
    let mut w = soul_match(36, Element::Chemtech);
    w.champ_mut(1).hp = 400;
    tick(&mut w);
    let b = w.has(1, rules::CHEM_LOW).expect("below half");
    assert_eq!((b.toughness, b.damaged_reduce, b.attack_mult, b.magic_power_mult), (15, 12, 12, 12));
    w.champ_mut(1).hp = 600;
    tick(&mut w);
    assert!(w.has(1, rules::CHEM_LOW).is_none());
}

/// Puts the Aspect of the Dragon on red straight in its state (taken at tick `w.tick`).
fn elder_match(seed: u64) -> World {
    log_to_temp();
    let mut w = World::new(seed, SimOriginKindV1::ServerPresim, CAST);
    start(&mut w);
    tick(&mut w);
    mock::with_sim(&mut w, |sim| {
        let now = sim.tick();
        let mut book = BOOK.lock().unwrap();
        let no = *book.by_origin.values().flatten().find(|no| {
            book.sims.get(no).is_some_and(|s| s.origin.4 == seed && s.anchors.contains(&0))
        }).unwrap();
        let s = book.sims.get_mut(&no).unwrap();
        s.start_hold(sim, now, true, 1);
    });
    place(&mut w, 6, (20_000, 100_000));
    tick(&mut w);
    w
}

#[test]
fn the_execute_waits_for_below_a_fifth() {
    let mut w = elder_match(41);
    assert!(w.has(6, rules::ELDER).is_some());
    // 211 hit for 1: 21% - burnt, not executed
    w.champ_mut(0).hp = 211;
    w.hit(6, 0, 1);
    tick(&mut w);
    let top = ent(&w, 0);
    assert!(w.units[top].alive && w.units[top].buffs.iter().any(|b| b.name() == rules::BURN));
    // exactly 20% is not below it either
    w.champ_mut(0).hp = 200;
    tick(&mut w);
    assert!(w.units[top].alive);
    // the burn's next tick takes it under: executed while burning
    advance(&mut w, rules::BURN_EVERY + 2);
    assert!(!w.units[top].alive);
    let exec: Vec<_> = w.hits_on(top).into_iter().filter(|h| h.4 == AttackTypeV1::Skill.code()).collect();
    assert_eq!(exec.len(), 1);
    assert_eq!(exec[0].0, ent(&w, 6), "the kill is the holder's");
    state(&w, |s| assert_eq!(s.executes, 1));
}

#[test]
fn a_hit_of_someone_else_is_no_holders_hit() {
    let mut w = elder_match(42);
    // blue's top hurt by somebody else (red's top, no holder... he is: the whole red team holds it) - take a blue victim
    // hurt by a minion: the holder beside him dealt nothing this tick
    w.champ_mut(0).hp -= 50;
    tick(&mut w);
    let top = ent(&w, 0);
    assert!(w.units[top].buffs.iter().all(|b| b.name() != rules::BURN), "no burn without his hit");
    // and one far from every holder is never his
    place(&mut w, 6, (900_000, 900_000));
    tick(&mut w);
    w.hit(6, 0, 50);
    tick(&mut w);
    assert!(w.units[top].buffs.iter().all(|b| b.name() != rules::BURN));
}

/// No statistics slot: the capture comes from the native buff the game hung, the holders' hits from their cooldowns.
#[test]
fn without_statistics_it_reads_the_native_buff_and_the_cooldowns() {
    log_to_temp();
    let mut w = World::new(51, SimOriginKindV1::ServerPresim, CAST);
    w.no_stats = true;
    start(&mut w);
    tick(&mut w);
    let s = spawn_serpen(&mut w);
    w.secure(s, 8);
    tick(&mut w);
    assert_eq!(record(&w, 0).stacks[1].iter().sum::<u8>(), 1, "red, by its native buffs");
    state(&w, |s| assert_eq!(s.stats, StatsWay::Missing));
    // the Aspect on red; player 6 next to blue's top attacks (his attack cooldown goes up) and blue's top is hurt
    mock::with_sim(&mut w, |sim| {
        let now = sim.tick();
        let mut book = BOOK.lock().unwrap();
        let no = *book.by_origin.values().flatten().find(|no| {
            book.sims.get(no).is_some_and(|s| s.origin.4 == 51 && s.anchors.contains(&0))
        }).unwrap();
        book.sims.get_mut(&no).unwrap().start_hold(sim, now, true, 1);
    });
    place(&mut w, 6, (20_000, 100_000));
    tick(&mut w);
    tick(&mut w);
    w.players[6].cds[0] = 60;
    w.champ_mut(0).hp -= 80;
    tick(&mut w);
    let top = ent(&w, 0);
    assert!(w.units[top].buffs.iter().any(|b| b.name() == rules::BURN));
    state(&w, |s| assert_eq!(s.deal_way, DealWay::Cooldowns));
}

/// Nobody can be told (no statistics, no native buff, the same number of champions near): no reward.
#[test]
fn a_kill_nobody_can_be_told_gives_nothing() {
    log_to_temp();
    let mut w = World::new(52, SimOriginKindV1::ServerPresim, CAST);
    w.no_stats = true;
    start(&mut w);
    tick(&mut w);
    let s = spawn_serpen(&mut w);
    w.units[s].alive = false;
    advance(&mut w, PENDING_T + 5);
    assert_eq!(record(&w, 0).stacks, [[0; 6]; 2]);
    state(&w, |s| assert!(s.pending.is_empty(), "given up"));
}

/// Its state lost (the book evicted it): rebuilt from the record on the nexus - the stacks and the soul stay.
#[test]
fn a_lost_state_comes_back_from_the_nexus_record() {
    log_to_temp();
    let mut w = World::new(61, SimOriginKindV1::ServerPresim, CAST);
    start(&mut w);
    tick(&mut w);
    for _ in 0..2 {
        let s = spawn_serpen(&mut w);
        w.secure(s, 1);
        tick(&mut w);
    }
    let before = record(&w, 0);
    let no = number(&w);
    BOOK.lock().unwrap().sims.remove(&no);
    tick(&mut w);
    assert_eq!(number(&w), no, "the same number");
    state(&w, |s| {
        assert!(s.late && s.rebuilt);
        assert_eq!(s.stacks, before.stacks);
        assert_eq!(s.drakes, 2);
    });
    // a third drake goes on top of them
    let s = spawn_serpen(&mut w);
    w.secure(s, 2);
    tick(&mut w);
    assert_eq!(record(&w, 0).stacks[0].iter().sum::<u8>(), 3);
}

/// The match on screen: its events and records go to the feed once - the screen's second run adds nothing, a presim of
/// the same match nothing at all.
#[test]
fn the_screen_feed_gets_each_event_once() {
    let _g = GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
    log_to_temp();
    feed::clear();
    let seed = 71;
    let o = rules::order(seed);
    let script = |w: &mut World| {
        start(w);
        tick(w);
        let s = spawn_serpen(w);
        w.secure(s, 4);
        tick(w);
        let e = spawn_epic(w);
        w.secure(e, 9);
        tick(w);
    };
    let base = World::new(seed, SimOriginKindV1::ClientMatchView, CAST);
    let mut a = base.clone();
    script(&mut a);
    let first = feed::events(77, 2);
    let whats: Vec<feed::What> = first.iter().map(|e| e.what.clone()).collect();
    assert_eq!(whats, vec![
        feed::What::DrakeSpawn { element: o[0] },
        feed::What::Drake { team: 0, element: o[0], total: 1 },
        feed::What::BaronKilled { team: 1, holders: CAST[5..].iter().map(|s| s.to_string()).collect() },
    ]);
    let r = feed::record_at(77, 2, a.tick).expect("a record");
    assert_eq!(r.baron.map(|h| h.team), Some(1));
    assert_eq!(feed::record_at(77, 2, 0).map(|r| r.stacks), Some([[0; 6]; 2]));
    // the screen's second run
    let mut b = base.clone();
    script(&mut b);
    assert_ne!(number(&a), number(&b));
    assert_eq!(feed::events(77, 2), first);
    // a presim of it
    let mut p = World::new(seed, SimOriginKindV1::ServerPresim, CAST);
    script(&mut p);
    assert_eq!(feed::events(77, 2), first);
    feed::clear();
}

#[test]
fn the_sim_tag_reads_back_and_is_skipped_by_the_divergence_check() {
    assert_eq!(parse_tag(&tag(42)), Some(42));
    assert_eq!(parse_tag("league_eggs_sim:3"), None);
    assert!(tag(7).contains("_sim:") && tag(u64::MAX).len() <= BUFF_NAME_CAP);
    // nothing else of ours carries a simulation's number: the record and the events are the same in every run
    assert!(!rules::ST.contains("_sim:") && !rules::EV.contains("_sim:"));
}

#[test]
fn a_simulation_without_anchors_is_looked_at_again_later() {
    assert!(waiting(100 + RETRY, 101) && waiting(100 + RETRY, 699));
    assert!(!waiting(100 + RETRY, 700));
    assert!(!waiting(5000 + RETRY, 0));
    assert!(waiting(usize::MAX, 0));
}

#[test]
fn statistics_numbers_parse() {
    assert_eq!(parse_num(" 12 "), Some(12));
    assert_eq!(parse_num("12.0"), Some(12));
    assert_eq!(parse_num("x"), None);
    assert_eq!(find_num("{\"deal\": 1534,\"epic_secure\":2}", "epic_secure"), Some(2));
    assert_eq!(find_num("{\"deal\":1534.5}", "deal"), Some(1534));
    assert_eq!(find_num("{\"deal_ad\":3}", "deal"), None);
}
