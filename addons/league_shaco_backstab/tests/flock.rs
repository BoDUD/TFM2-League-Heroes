//! 第二轮（2026-11-14，用户：「召唤物的全做啊」）公用模块里的 `Flock`：一个召唤者同时有好几个单位时的账。在测试用的小世界
//! （`src/summon_mock.rs`：假宿主）里走一遍：一个原生效果一次生成三个单位、各挂一个交接 buff；被动要了一批、下一 tick 一起
//! 接手；活着的每秒一行；到时间 / 被打死各自结束；账满了先放掉最老的；宿主不给单位、给的 id 读不成单位、只给了一部分；召唤者
//! 死了一次全交出来。萨科和安妮的试点不用它（他们的测试一个字没改）。

use league_shaco_backstab::summon::{self, Event, Fate, Flock, Spec, FLOCK_LOOKS, FLOCK_WAIT};
use mod_api_stable::*;

#[path = "../src/summon_mock.rs"]
mod mock;

use mock::{champion, MPlayer, World};

const PREFIX: &str = "league_test_uid";
const LIFE: usize = 300;

/// The summoner #0 (team 0) at (300000, 300000), an enemy champion #1 50000 east of him; a player each.
fn world() -> World {
    let mut w = World::default();
    w.units = vec![champion("league_yorick", 0, 300_000.0, 300_000.0), champion("league_garen", 1, 350_000.0, 300_000.0)];
    w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
    w
}

fn spec() -> Spec {
    Spec { name: "league_test_walker".into(), life: LIFE,
           stat: StatV1 { attack: 20, hp: 150, move_speed: 1000, ..Default::default() },
           attack: UnitAttackV1 { attack: 5, attack_ratio: 100, range: 15_000, cooltime: 60, duration: 20, start_timing: 8,
                                  ..Default::default() } }
}

/// What a hero's native effect does: `n` units round `at`, each handed over by its own buff on the summoner. -> how
/// many came.
fn effect(w: &mut World, n: usize, at: (f64, f64)) -> usize {
    w.sim(|sim| {
        let ids: Vec<usize> = summon::spread(at, 8_000.0, n, 0.0).into_iter()
            .filter_map(|p| summon::spawn(sim, 0, 0, p, &spec()))
            .collect();
        for id in &ids {
            sim.add_buff(0, &BuffV1::timed(&summon::handoff(PREFIX, *id), 6));
        }
        ids.len()
    })
}

/// A tick of the flock, then the world's own step. -> the events.
fn tick(w: &mut World, f: &mut Flock<u32>) -> Vec<Event<u32>> {
    let ev = w.sim(|sim| f.tick(sim, 0, 0, 0, Some((300_000.0, 300_000.0))));
    w.step();
    ev
}

fn looks(ev: &[Event<u32>]) -> Vec<usize> {
    ev.iter().filter_map(|e| match e { Event::Look { id, .. } => Some(*id), _ => None }).collect()
}

#[test]
fn three_units_of_one_ask_come_together_live_and_time_out() {
    let mut w = world();
    let mut f: Flock<u32> = Flock::new(PREFIX, 6, LIFE);
    let t0 = w.tick;
    f.ask(t0, LIFE, 7);
    assert_eq!(f.waiting(), 1);
    assert_eq!(effect(&mut w, 3, (350_000.0, 300_000.0)), 3);
    let ev = tick(&mut w, &mut f);
    // all three handed over in one tick, read as units at once, numbered 1-3, the ask's `what` on each
    assert_eq!(looks(&ev).len(), 3, "{ev:?}");
    assert_eq!(f.live.iter().map(|m| (m.unit.n, m.extra, m.unit.born, m.unit.life)).collect::<Vec<_>>(),
               vec![(1, 7, t0, LIFE), (2, 7, t0, LIFE), (3, 7, t0, LIFE)]);
    assert_eq!((f.waiting(), f.out(), f.room(), f.count), (0, 3, 3, 3));
    assert!(!w.units[0].buffs.iter().any(|b| b.0.name().starts_with(PREFIX)), "a handoff left on him");
    // a line a second each while they live; they fight Garen
    let mut lines = 0;
    let mut over = Vec::new();
    for _ in 0..LIFE + 10 {
        for e in tick(&mut w, &mut f) {
            match e {
                Event::Line { .. } => lines += 1,
                Event::Over { member, end } => over.push((member.unit.n, end.fate, end.age)),
                Event::Look { .. } | Event::LetGo { .. } | Event::Lost { .. } | Event::NoUnit { .. } => panic!("{e:?}"),
                Event::Wake { .. } => {}
            }
        }
    }
    assert!(lines >= 3 * (LIFE / summon::LINE_EVERY - 1), "{lines} lines");
    assert_eq!(over.len(), 3);
    assert!(over.iter().all(|o| o.1 == Fate::TimedOut && o.2 >= LIFE && o.2 <= LIFE + 3), "{over:?}");
    assert!(w.damage.iter().any(|d| d.2 == 1 && d.1 > 1), "no unit hit Garen");
    for _ in 0..summon::WAKE_TICKS + 5 {
        tick(&mut w, &mut f);
    }
    assert!(f.is_empty(), "{f:?}");
}

#[test]
fn a_killed_unit_ends_alone_and_the_others_fight_on() {
    let mut w = world();
    let mut f: Flock<u32> = Flock::new(PREFIX, 6, LIFE);
    f.ask(w.tick, LIFE, 0);
    effect(&mut w, 3, (330_000.0, 300_000.0));
    tick(&mut w, &mut f);
    for _ in 0..50 {
        tick(&mut w, &mut f);
    }
    let ids = f.ids();
    w.hurt(ids[1], 100_000);
    let ev = tick(&mut w, &mut f);
    let over: Vec<(usize, Fate)> = ev.iter().filter_map(|e| match e {
        Event::Over { member, end } => Some((member.unit.id, end.fate)),
        _ => None,
    }).collect();
    assert_eq!(over, vec![(ids[1], Fate::Killed)]);
    assert_eq!(f.ids(), vec![ids[0], ids[2]]);
}

#[test]
fn a_full_book_lets_the_oldest_go() {
    let mut w = world();
    let mut f: Flock<u32> = Flock::new(PREFIX, 4, LIFE);
    f.ask(w.tick, LIFE, 1);
    effect(&mut w, 3, (340_000.0, 300_000.0));
    tick(&mut w, &mut f);
    let first = f.ids();
    for _ in 0..10 {
        tick(&mut w, &mut f);
    }
    f.ask(w.tick, LIFE, 2);
    effect(&mut w, 3, (340_000.0, 300_000.0));
    let ev = tick(&mut w, &mut f);
    let gone: Vec<usize> = ev.iter().filter_map(|e| match e { Event::LetGo { member } => Some(member.unit.id), _ => None }).collect();
    assert_eq!(gone, first[..2].to_vec(), "the two oldest let go");
    assert_eq!(f.live.len(), 4);
    assert_eq!(f.live.iter().map(|m| m.extra).collect::<Vec<_>>(), vec![1, 2, 2, 2]);
    assert_eq!(f.room(), 0);
    // let go is not killed: they are still out there
    assert!(first[..2].iter().all(|id| w.units[*id].hp > 0 && w.units[*id].died.is_none()));
}

#[test]
fn no_unit_an_unreadable_one_and_a_host_out_of_room() {
    // no slot: nothing comes, the ask is given up after FLOCK_WAIT ticks
    let mut w = world();
    w.has_spawn = false;
    let mut f: Flock<u32> = Flock::new(PREFIX, 6, LIFE);
    let t0 = w.tick;
    f.ask(t0, LIFE, 9);
    assert_eq!(effect(&mut w, 3, (340_000.0, 300_000.0)), 0);
    let mut none = Vec::new();
    for _ in 0..FLOCK_WAIT + 3 {
        for e in tick(&mut w, &mut f) {
            if let Event::NoUnit { asked, what } = e {
                none.push((asked, what, w.tick));
            }
        }
    }
    assert_eq!(none.len(), 1);
    assert_eq!((none[0].0, none[0].1), (t0, 9));
    assert!(none[0].2 > t0 + FLOCK_WAIT && none[0].2 <= t0 + FLOCK_WAIT + 2);
    assert!(f.is_empty());
    // ids that never read as units: each given up after FLOCK_LOOKS looks
    let mut w = world();
    w.spawn_never = true;
    let mut f: Flock<u32> = Flock::new(PREFIX, 6, LIFE);
    f.ask(w.tick, LIFE, 0);
    effect(&mut w, 2, (340_000.0, 300_000.0));
    let mut lost = 0;
    for _ in 0..FLOCK_LOOKS + 3 {
        lost += tick(&mut w, &mut f).iter().filter(|e| matches!(e, Event::Lost { .. })).count();
    }
    assert_eq!(lost, 2);
    assert!(f.is_empty());
    // readable only a tick late: looked at again, then kept
    let mut w = world();
    w.spawn_late = true;
    let mut f: Flock<u32> = Flock::new(PREFIX, 6, LIFE);
    f.ask(w.tick, LIFE, 0);
    effect(&mut w, 2, (340_000.0, 300_000.0));
    let n: usize = (0..3).map(|_| looks(&tick(&mut w, &mut f)).len()).sum();
    assert_eq!((n, f.live.len()), (2, 2));
    // a host with room for two of three: two come, nothing is given up
    let mut w = world();
    w.spawn_left = Some(2);
    let mut f: Flock<u32> = Flock::new(PREFIX, 6, LIFE);
    f.ask(w.tick, LIFE, 0);
    assert_eq!(effect(&mut w, 3, (340_000.0, 300_000.0)), 2);
    let ev: Vec<Event<u32>> = (0..FLOCK_WAIT + 3).flat_map(|_| tick(&mut w, &mut f)).collect();
    assert_eq!(looks(&ev).len(), 2);
    assert!(!ev.iter().any(|e| matches!(e, Event::NoUnit { .. } | Event::Lost { .. })));
    assert_eq!(w.spawns.len(), 3);
}

#[test]
fn a_unit_is_taken_on_once_it_has_settled() {
    // game 0.7.2: a new unit reads max health 1 and every stat 1 on its spawn tick and the next (World::settle)
    let mut w = world();
    w.settle = 2;
    let mut f: Flock<u32> = Flock::new(PREFIX, 6, LIFE);
    f.ask(w.tick, LIFE, 5);
    assert_eq!(effect(&mut w, 2, (340_000.0, 300_000.0)), 2);
    let spawned = w.tick;
    // the spawn tick and the next: handed over, not on the books yet (nothing for the caller to dress)
    for _ in 0..2 {
        let ev = tick(&mut w, &mut f);
        assert!(looks(&ev).is_empty() && f.live.is_empty(), "{ev:?}");
        assert_eq!((f.waiting(), f.out()), (0, 2));
    }
    // settled: both taken on, their numbers their own
    let ev = tick(&mut w, &mut f);
    assert_eq!(looks(&ev).len(), 2, "{ev:?}");
    assert_eq!(w.tick - 1, spawned + 2);
    for e in &ev {
        if let Event::Look { line, .. } = e {
            assert!(line.contains("hp 150/150 attack 20") && !line.contains("still reads"), "{line}");
        }
    }
    assert!(f.live.iter().all(|m| m.unit.settled() && m.unit.max == 150 && m.extra == 5));
    // one that never settles in FLOCK_LOOKS looks is taken on all the same, and the line says so
    let mut w = world();
    w.settle = 1_000;
    let mut f: Flock<u32> = Flock::new(PREFIX, 6, LIFE);
    f.ask(w.tick, LIFE, 0);
    effect(&mut w, 1, (340_000.0, 300_000.0));
    let ev: Vec<Event<u32>> = (0..FLOCK_LOOKS + 2).flat_map(|_| tick(&mut w, &mut f)).collect();
    let lines: Vec<&String> = ev.iter().filter_map(|e| match e { Event::Look { line, .. } => Some(line), _ => None }).collect();
    assert_eq!(lines.len(), 1, "{ev:?}");
    assert!(lines[0].ends_with(&format!(" (its health cap still reads 1 after {FLOCK_LOOKS} looks)")), "{}", lines[0]);
    assert!(!ev.iter().any(|e| matches!(e, Event::Lost { .. } | Event::NoUnit { .. })));
}

#[test]
fn the_summoners_death_hands_over_every_living_unit() {
    let mut w = world();
    let mut f: Flock<u32> = Flock::new(PREFIX, 6, LIFE);
    f.ask(w.tick, LIFE, 3);
    effect(&mut w, 3, (340_000.0, 300_000.0));
    tick(&mut w, &mut f);
    f.ask(w.tick, LIFE, 4);
    let orphans = f.orphans();
    assert_eq!(orphans.len(), 3);
    assert!(orphans.iter().all(|m| m.extra == 3));
    assert!(f.is_empty() && f.waiting() == 0);
    // a stray handoff (no ask waiting) still comes on the books, with the flock's own life
    effect(&mut w, 1, (340_000.0, 300_000.0));
    let ev = tick(&mut w, &mut f);
    assert_eq!(looks(&ev).len(), 1);
    assert_eq!((f.live[0].unit.life, f.live[0].extra, f.live[0].unit.n), (LIFE, 0, 4));
}
