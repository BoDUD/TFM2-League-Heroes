//! 比赛钩子在假模拟上跑（[`super::mock`]）：开局和到级选、复活补回、并排的两份预演选得一样、屏幕那一场进 feed、
//! 英雄特性表让 AI 选对路子、水晶和塔都不收 buff 时什么都不做。

use std::sync::Mutex;

use mod_api_stable::*;

use super::augments::{self, Tier, AUGS};
use super::kit::{self, Kit};
use super::mock::{with_sim, World};
use super::{feed, Hextech, KEEP_EVERY, OPEN_AT, SIM_TAG};

/// 动全局（模拟的表、feed、英雄特性表）的测试一个一个来。
pub(crate) static GLOBALS: Mutex<()> = Mutex::new(());

const HEROES: [&str; 10] = ["league_garen", "league_leesin", "league_ahri", "league_jinx", "league_leona", "league_darius",
                            "league_elise", "league_syndra", "league_caitlyn", "league_lulu"];

fn start(w: &mut World) {
    with_sim(w, |sim| Hextech.on_match_start(sim));
}

fn run_to(w: &mut World, to: usize) {
    while w.tick < to {
        w.tick += 1;
        with_sim(w, |sim| Hextech.on_match_tick(sim, 0));
    }
}

fn world(seed: u64, kind: SimOriginKindV1, m: u64) -> World {
    let mut w = World::new(seed, kind, HEROES);
    if let Some(o) = w.origin.as_mut() {
        o.match_id = m;
    }
    w
}

fn tags_on_nexus(w: &World) -> Vec<String> {
    w.units[0].buffs.iter().map(|b| b.name().to_string()).filter(|n| n.starts_with(SIM_TAG)).collect()
}

#[test]
fn picks_come_at_the_start_then_by_level_then_all_by_the_catch_up_minute() {
    let _g = GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
    kit::reset_for_test(Vec::new());
    let mut w = world(1234, SimOriginKindV1::ServerPresim, 9001);
    start(&mut w);
    run_to(&mut w, OPEN_AT - 1);
    assert!((0..10).all(|p| w.augs(p).is_empty()), "nothing before the opening pick");
    run_to(&mut w, OPEN_AT);
    assert!((0..10).all(|p| w.augs(p).len() == 1), "everyone's opening pick at tick {OPEN_AT}");
    assert_eq!(tags_on_nexus(&w).len(), 1);
    // Jinx (player 3) levels: 6, 9, 12 - one pick each, never a fifth
    for (lv, n) in [(5, 1), (6, 2), (8, 2), (9, 3), (12, 4)] {
        w.players[3].level = lv;
        let t = w.tick + 10;
        run_to(&mut w, t);
        assert_eq!(w.augs(3).len(), n, "level {lv}");
    }
    let t = w.tick + 100;
    run_to(&mut w, t);
    assert_eq!(w.augs(3).len(), 4);
    let mut mine = w.augs(3);
    mine.sort();
    mine.dedup();
    assert_eq!(mine.len(), 4, "no augment twice: {:?}", w.augs(3));
    // the others are still on their first one; at the catch-up minute everyone gets the rest
    assert!((0..10).filter(|&p| p != 3).all(|p| w.augs(p).len() == 1));
    run_to(&mut w, 10 * 3600);
    assert!((0..10).all(|p| w.augs(p).len() == 4), "{:?}", (0..10).map(|p| w.augs(p).len()).collect::<Vec<_>>());
}

#[test]
fn twin_presims_pick_the_same_and_keep_their_own_numbers() {
    let _g = GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
    kit::reset_for_test(Vec::new());
    let mut a = world(777, SimOriginKindV1::ServerPresim, 9002);
    let mut b = world(777, SimOriginKindV1::ServerPresim, 9002);
    start(&mut a);
    start(&mut b);
    for t in 1..=4000 {
        if t == 1500 {
            for w in [&mut a, &mut b] {
                w.players[0].level = 7;
                w.players[7].level = 9;
            }
        }
        if t == 3000 {
            for w in [&mut a, &mut b] {
                w.players[0].level = 12;
                w.diff = -9;
            }
        }
        run_to(&mut a, t);
        run_to(&mut b, t);
    }
    for p in 0..10 {
        assert_eq!(a.augs(p), b.augs(p), "player {p}");
    }
    assert_eq!(a.augs(0).len(), 4);
    assert_eq!(a.augs(7).len(), 3);
    // each has its own number on its nexus
    let (ta, tb) = (tags_on_nexus(&a), tags_on_nexus(&b));
    assert_eq!((ta.len(), tb.len()), (1, 1));
    assert_ne!(ta, tb);
    // another seed: another match (some pick differs)
    let mut c = world(778, SimOriginKindV1::ServerPresim, 9003);
    start(&mut c);
    run_to(&mut c, 100);
    assert!((0..10).any(|p| c.augs(p) != a.augs(p)[..1].to_vec()));
}

#[test]
fn a_respawned_champion_gets_his_augments_back_once() {
    let _g = GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
    kit::reset_for_test(Vec::new());
    let mut w = world(55, SimOriginKindV1::ServerPresim, 9004);
    start(&mut w);
    w.players[2].level = 9;
    run_to(&mut w, 200);
    let before = w.augs(2);
    assert_eq!(before.len(), 3);
    w.die(2);
    let t = w.tick + 2 * KEEP_EVERY;
    run_to(&mut w, t);
    w.respawn(2);
    assert!(w.augs(2).is_empty());
    let t = w.tick + KEEP_EVERY + 10;
    run_to(&mut w, t);
    assert_eq!(w.augs(2), before, "put back after the respawn");
    let t = w.tick + 5 * KEEP_EVERY;
    run_to(&mut w, t);
    assert_eq!(w.augs(2), before, "exactly once");
    // a pick that comes while he is dead goes on at the respawn
    w.die(2);
    w.players[2].level = 12;
    let t = w.tick + 20;
    run_to(&mut w, t);
    w.respawn(2);
    let t = w.tick + KEEP_EVERY + 10;
    run_to(&mut w, t);
    assert_eq!(w.augs(2).len(), 4);
}

#[test]
fn the_screens_match_feeds_the_picks() {
    let _g = GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
    kit::reset_for_test(Vec::new());
    feed::clear();
    let mut w = world(4321, SimOriginKindV1::ClientMatchView, 9005);
    start(&mut w);
    run_to(&mut w, 100);
    assert_eq!(feed::current(), Some((9005, 2)));
    let ev = feed::events(9005, 2);
    assert_eq!(ev.len(), 10);
    let tiers = feed::tiers_of(9005, 2).expect("tiers");
    for e in &ev {
        assert_eq!((e.tick, e.pick.screen, e.pick.tier), (OPEN_AT, 0, tiers[0]));
        assert!(e.pick.cards.contains(&e.pick.chosen));
        assert_eq!(AUGS[e.pick.chosen as usize].tier, tiers[0]);
        let p = e.pick.team * 5 + e.pick.lane as usize;
        assert_eq!(w.augs(p), vec![augments::buff_name(e.pick.chosen as usize)]);
        assert_eq!(e.pick.hero, HEROES[p]);
    }
    w.players[8].level = 6;
    run_to(&mut w, 300);
    let ev = feed::events(9005, 2);
    let late: Vec<_> = ev.iter().filter(|e| e.pick.screen == 1).collect();
    assert_eq!(late.len(), 1);
    assert_eq!((late[0].pick.team, late[0].pick.lane, late[0].pick.level, late[0].pick.tier), (1, 3, 6, tiers[1]));
    // the screen's simulation run again (its second run, the same match tick for tick): nothing recorded twice
    let mut again = world(4321, SimOriginKindV1::ClientMatchView, 9005);
    start(&mut again);
    run_to(&mut again, 100);
    again.players[8].level = 6;
    run_to(&mut again, 300);
    assert_eq!(feed::events(9005, 2), ev);
    // a run that went otherwise (he was 6 already at the start): its picks are its own, the screen's kept apart by tick
    // and level
    let mut other = world(4321, SimOriginKindV1::ClientMatchView, 9005);
    other.players[8].level = 6;
    start(&mut other);
    run_to(&mut other, 300);
    assert_eq!(feed::events(9005, 2).len(), ev.len() + 2);
    // the end
    w.end = true;
    let t = w.tick + 1;
    run_to(&mut w, t);
    assert_eq!(feed::ended_at(9005, 2), Some(t));
    // 0.5.1：另一场比赛用了同一个编号（游戏的场次编号会重复，用户 2026-11-26 两场不同的比赛都是 m=101 第 1 局）：上一场
    // 记着的选择、结束的 tick、档位都扔掉，只有这一场的
    let mut next = world(9999, SimOriginKindV1::ClientMatchView, 9005);
    start(&mut next);
    run_to(&mut next, 100);
    let fresh = feed::events(9005, 2);
    assert_eq!(fresh.len(), 10, "only the new match's opening picks: {fresh:?}");
    assert_eq!(feed::ended_at(9005, 2), None, "the old match's end dropped too");
    let tiers = feed::tiers_of(9005, 2).expect("the new match's tiers");
    for e in &fresh {
        let p = e.pick.team * 5 + e.pick.lane as usize;
        assert_eq!(next.augs(p), vec![augments::buff_name(e.pick.chosen as usize)]);
        assert_eq!(e.pick.tier, tiers[0]);
    }
    // and its second run (the same seed, the same heroes) keeps them
    let mut twice = world(9999, SimOriginKindV1::ClientMatchView, 9005);
    start(&mut twice);
    run_to(&mut twice, 100);
    assert_eq!(feed::events(9005, 2), fresh);
    // the old match's simulation still running on: its picks no longer go on the screen
    again.players[3].level = 9;
    let t = again.tick + 100;
    run_to(&mut again, t);
    assert!(again.augs(3).len() > 1, "it still picks for itself");
    assert_eq!(feed::events(9005, 2), fresh, "but nothing of it on the screen");
    feed::clear();
}

/// 知道游戏的分类和标签以后，AI 拿合适的：金克丝拿输出，蕾欧娜拿坦度，辛德拉拿法术，50 局、每局 4 次里至少八成。0.4.0 一共
/// 109 个，每一档里适合一类英雄的只有三四成，桌上和刷新出来的都不合适时拿最好的那张（辛德拉漏的是十几种各一两次）；闭着眼拿
/// 只有三成多。
#[test]
fn the_kit_steers_the_ai() {
    let _g = GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
    use super::rules::tests::{DAMAGE, MAGIC, TANKY};
    use ChampionCategoryV1 as C;
    use ChampionTagV1 as G;
    kit::reset_for_test(vec![
        ("league_jinx".into(), Kit { category: Some(C::Range), tags: vec![G::Ad, G::Range, G::Cc] }),
        ("league_leona".into(), Kit { category: Some(C::Tank), tags: vec![G::Ap, G::Magic, G::Melee, G::Tank, G::Cc] }),
        ("league_syndra".into(), Kit { category: Some(C::Magician), tags: vec![G::Ap, G::Magic, G::Range, G::Cc] }),
    ]);
    let mut hits = [0usize; 3];
    let mut picks = [0usize; 3];
    for seed in 0..50u64 {
        let mut w = world(10_000 + seed, SimOriginKindV1::ServerPresim, 20_000 + seed);
        start(&mut w);
        for p in [3, 4, 7] {
            w.players[p].level = 12;
        }
        run_to(&mut w, 120);
        let keys = |p: usize| -> Vec<String> {
            w.augs(p).iter().map(|n| n.trim_start_matches(augments::BUFF_PREFIX).to_string()).collect()
        };
        // 0.5.0：质变、潘朵拉会多给（拿到的海克斯可能多于 4 个），都算进去
        assert!([3, 4, 7].iter().all(|&p| keys(p).len() >= 4));
        for (n, (p, list)) in [(3usize, &DAMAGE[..]), (4, &TANKY[..]), (7, &MAGIC[..])].into_iter().enumerate() {
            let k = keys(p);
            picks[n] += k.len();
            hits[n] += k.iter().filter(|k| list.contains(&k.as_str())).count();
        }
    }
    for ((who, h), n) in ["Jinx", "Leona", "Syndra"].iter().zip(hits).zip(picks) {
        assert!(h as f64 >= 0.8 * n as f64, "{who}: {h} fitting of {n}");
    }
    kit::reset_for_test(Vec::new());
}

#[test]
fn nothing_happens_where_no_building_takes_the_number() {
    let _g = GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
    kit::reset_for_test(Vec::new());
    let mut w = world(99, SimOriginKindV1::ServerPresim, 9006);
    w.refuse = vec![EntityKindV1::Nexus, EntityKindV1::Tower];
    start(&mut w);
    run_to(&mut w, 1000);
    assert!((0..10).all(|p| w.augs(p).is_empty()));
}

#[test]
fn the_tiers_hold_for_every_player() {
    let _g = GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
    kit::reset_for_test(Vec::new());
    feed::clear();
    let mut w = world(31337, SimOriginKindV1::ClientMatchView, 9007);
    start(&mut w);
    for p in 0..10 {
        w.players[p].level = 12;
    }
    run_to(&mut w, 200);
    let tiers = feed::tiers_of(9007, 2).expect("tiers");
    let ev = feed::events(9007, 2);
    assert_eq!(ev.len(), 40);
    for e in &ev {
        assert_eq!(e.pick.tier, tiers[e.pick.screen as usize], "{e:?}");
    }
    assert!(!(tiers[0] == Tier::Silver && tiers[1] == Tier::Silver));
    feed::clear();
}

/// The pick screen's record for this set (the player blue): blue's heroes get exactly what the record says - what the
/// player clicked and the AI's defaults - at the levels, red's AI picks in the record's tiers; both presim twins and the
/// screen read the same record; the screen's events say who chose.
#[test]
fn the_players_pick_screen_record_drives_his_side() {
    let _g = GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
    use super::pending::{self, Record};
    kit::reset_for_test(Vec::new());
    feed::clear();
    pending::clear();
    let marksman = augments::Traits { ad: 1.0, attacker: 1.0, ranged: 1.0, ..augments::Traits::ZERO };
    let mut rec = Record::new(4242, 0, 4242, [35, 45, 20]);
    let v = |r: std::ops::Range<usize>| HEROES[r].iter().map(|s| s.to_string()).collect::<Vec<_>>();
    rec.set_lineup(v(0..5), v(5..10), |_| marksman);
    // the player clicks Jinx's second card at the start and her third at level 9
    assert!(rec.choose("league_jinx", 0, 1));
    assert!(rec.choose("league_jinx", 2, 2));
    let id = pending::open(rec.clone());
    let mut a = world(31, SimOriginKindV1::ServerPresim, 9100);
    let mut b = world(31, SimOriginKindV1::ServerPresim, 9100);
    let mut view = world(31, SimOriginKindV1::ClientMatchView, 9100);
    for w in [&mut a, &mut b, &mut view] {
        start(w);
        for p in 0..10 {
            w.players[p].level = 12;
        }
        run_to(w, 200);
    }
    assert!(pending::get(id).unwrap().used, "locked by the first simulation");
    let mine = |p: usize| -> Vec<String> {
        rec.mine_of(HEROES[p]).unwrap().picks.iter().map(|c| augments::buff_name(c.chosen as usize)).collect()
    };
    // 记录里的几张按顺序都在他身上（0.5.0：质变多给的夹在中间；潘朵拉的盒子把它前面的换掉了，从它起算）
    let in_order = |got: &[String], want: &[String]| -> bool {
        let mut it = got.iter();
        want.iter().all(|x| it.any(|g| g == x))
    };
    for w in [&a, &b, &view] {
        for p in 0..5 {
            let want = mine(p);
            let from = want.iter().rposition(|x| *x == augments::buff_name(augments::by_key("pandoras_box").unwrap())).unwrap_or(0);
            assert!(in_order(&w.augs(p), &want[from..]), "blue {p} as the record says: {:?} vs {want:?}", w.augs(p));
        }
    }
    for p in 5..10 {
        assert_eq!(a.augs(p), b.augs(p));
        assert_eq!(a.augs(p), view.augs(p));
        assert!(a.augs(p).len() >= 4);
    }
    // the record's tiers for everyone, and who chose on screen
    assert_eq!(feed::tiers_of(9100, 2), Some(rec.tiers));
    // 0.5.0：质变、潘朵拉随机给的、换掉的另记（by 3 / 4），选的还是 40 次
    let ev: Vec<feed::Event> = feed::events(9100, 2).into_iter().filter(|e| e.pick.by < 3).collect();
    assert_eq!(ev.len(), 40);
    for e in &ev {
        assert_eq!(e.pick.tier, rec.tiers[e.pick.screen as usize]);
        let want = match (e.pick.team, e.pick.hero.as_str(), e.pick.screen) {
            (1, _, _) => 0,
            (0, "league_jinx", 0 | 2) => 2,
            (0, _, _) => 1,
            _ => unreachable!(),
        };
        assert_eq!(e.pick.by, want, "{e:?}");
    }
    // the screen's simulation bound it to its set, for the save
    assert_eq!(pending::get(id).unwrap().bound, Some((9100, 2)));
    assert_eq!(pending::take_unsaved().len(), 1);
    pending::clear();
    feed::clear();
}
