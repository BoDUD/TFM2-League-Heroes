//! 约里克附加包的单元测试（0.3.0 起单独一个文件）：数字、墙的几何，和萨科附加包的假宿主（summon_mock.rs）上走一遍的被动。

use super::mock::{champion, unit, MPlayer, World};
use super::wall::{self, Hold, Ring};
use super::*;

#[test]
fn params_come_from_the_champion_data() {
    let p = parse_params(r#"{"g_t":1200,"r_pct":5,"w_delay":40,"w_half":9000,"w_r":28000,"w_t":200,"x":1}"#);
    assert_eq!(p, Params { r_pct: 5, g_t: 1200, w_r: 28000, w_half: 9000, w_t: 200, w_delay: 40 });
    assert_eq!(parse_params("{}"), Params::default());
}

#[test]
fn the_numbers_go_by_level_as_in_league() {
    // graves: one more each dig, at most four; the count is the highest rung
    assert_eq!((graves_after(0), graves_after(2), graves_after(3), graves_after(4)), (1, 3, 4, 4));
    assert_eq!(graves_of([false; 4]), 0);
    assert_eq!(graves_of([true, true, true, false]), 3);
    assert_eq!(graves_of([true, true, true, true]), 4);
    // every 8th death near him at level 1, every 2nd at 12
    assert_eq!((deaths_per_grave(1), deaths_per_grave(6), deaths_per_grave(12), deaths_per_grave(30)), (8, 5, 2, 2));
    // Last Rites: 10-76 + 6-10% of the missing health, half on a unit
    assert_eq!(q_heal(1, 500, 1000, true), 10 + 30);
    assert_eq!(q_heal(1, 500, 1000, false), 20);
    assert_eq!(q_heal(12, 1000, 3000, true), 76 + 200);
    assert_eq!(q_heal(5, 2000, 2000, true), 34);
    // the haste toward the marked, 18-30%
    assert_eq!((haste(1), haste(12)), (18, 30));
    // R's rank, her escort, her mark (r_pct 3: 2 / 2.5 / 3%)
    assert_eq!((r_rank(5), r_rank(8), r_rank(11)), (1, 2, 3));
    assert_eq!((escort(5), escort(9), escort(12)), (2, 3, 4));
    let p = Params::default();
    assert_eq!((mark_per_mille(&p, 6), mark_per_mille(&p, 9), mark_per_mille(&p, 12)), (20, 25, 30));
    // toward: within 60 degrees of the line to it
    assert!(toward((0.0, 0.0), (1000.0, 0.0), (50_000.0, 10_000.0)));
    assert!(!toward((0.0, 0.0), (1000.0, 0.0), (1000.0, 50_000.0)));
    assert!(!toward((0.0, 0.0), (-1000.0, 0.0), (50_000.0, 0.0)));
    assert!(!toward((0.0, 0.0), (0.0, 0.0), (50_000.0, 0.0)), "standing still is going nowhere");
    // her spot: MAID_BACK from him on her side, up the screen when she is on him
    assert_eq!(follow_spot((100_000.0, 100_000.0), (100_000.0, 200_000.0)), (100_000.0, 100_000.0 + MAID_BACK));
    assert_eq!(follow_spot((100_000.0, 100_000.0), (100_000.0, 100_000.0)), (100_000.0, 100_000.0 - MAID_BACK));
}

const C: Pt = (500_000.0, 400_000.0);

fn ring() -> Ring {
    Ring::new(C, &Params::default(), 0)
}

#[test]
fn the_ring_keeps_each_side_to_its_own() {
    let r = ring();
    // it falls as the data's last piece (the fall, 15 + 30 x 7 ticks in) is half played
    assert_eq!((r.line, r.inner, r.outer, r.until), (30_000.0, 20_000.0, 40_000.0, 235));
    // on the wall at the rise: within 210/225 of the line pulled in, the rest pushed out; clear of it left alone
    assert_eq!(wall::at_rise(&r, (C.0 + 10_000.0, C.1)), (true, None));
    assert_eq!(wall::at_rise(&r, (C.0 + 45_000.0, C.1)), (false, None));
    assert_eq!(wall::at_rise(&r, (C.0 + 25_000.0, C.1)), (true, Some((C.0 + 19_999.0, C.1))));
    assert_eq!(wall::at_rise(&r, (C.0, C.1 + 29_000.0)), (false, Some((C.0, C.1 + 40_001.0))));
    let (dx, dy, speed, ticks) = wall::push((C.0 + 25_000.0, C.1), (C.0 + 19_999.0, C.1)).unwrap();
    assert_eq!((dx, dy, ticks), (-5_001, 0, wall::PUSH_TICKS));
    assert!(speed * ticks >= 5_001);
    // walking out from inside: slid back onto the inner face along the ray, the sideways part kept
    assert_eq!(wall::hold(&r, true, Some((C.0 + 19_000.0, C.1)), (C.0 + 20_500.0, C.1), false), Hold::Slide((C.0 + 19_999.0, C.1)));
    // walking about inside: free
    assert_eq!(wall::hold(&r, true, Some((C.0, C.1)), (C.0 + 900.0, C.1 + 900.0), false), Hold::Free);
    // a dash out: back where it stood
    assert_eq!(wall::hold(&r, true, Some((C.0 + 18_000.0, C.1)), (C.0 + 23_000.0, C.1), false), Hold::Back((C.0 + 18_000.0, C.1)));
    // walking in from outside: held on the outer face
    assert_eq!(wall::hold(&r, false, Some((C.0, C.1 - 41_000.0)), (C.0, C.1 - 39_000.0), false), Hold::Slide((C.0, C.1 - 40_001.0)));
    // a Flash out (more than BLINK in a tick): let through, outside from now on; and in
    assert_eq!(wall::hold(&r, true, Some((C.0 + 10_000.0, C.1)), (C.0 + 60_000.0, C.1), false), Hold::Leapt(false));
    assert_eq!(wall::hold(&r, false, Some((C.0 + 45_000.0, C.1)), (C.0 + 5_000.0, C.1), false), Hold::Leapt(true));
    // ignoring terrain: through, on whichever side of the line it stands
    assert_eq!(wall::hold(&r, true, Some((C.0 + 19_000.0, C.1)), (C.0 + 21_000.0, C.1), true), Hold::Ghost(true));
    assert_eq!(wall::hold(&r, true, Some((C.0 + 29_000.0, C.1)), (C.0 + 31_000.0, C.1), true), Hold::Ghost(false));
    // only his enemies, only units that walk
    assert!(wall::blocks(Some(EntityKindV1::Champion), 1, 0));
    assert!(wall::blocks(Some(EntityKindV1::Minion), 2, 0));
    assert!(!wall::blocks(Some(EntityKindV1::Champion), 0, 0), "his own team walks through");
    assert!(!wall::blocks(Some(EntityKindV1::Tower), 1, 0));
    assert!(!wall::blocks(None, 1, 0));
}

#[test]
fn names_are_the_data_s() {
    for n in [Q_WIN, Q_HL, Q_CH, HIT, K_ASK, K_ASK4, K_UNIT, M_ASK, M_UNIT, E_ASK, W_ASK, W_UP, W_DOWN, R_ON, E_MARK, E_MS, R_MKV, R_BOLT,
              R_CLAW, R_MARK_VIEW, Q_GRAVE].iter().chain(GRAVES.iter()) {
        assert!(n.starts_with("league_yorick_"), "{n}");
        assert!(n.len() <= BUFF_NAME_CAP, "{n}");
    }
    for name in [summon::handoff(W_UID, usize::MAX), summon::handoff(M_UID, usize::MAX)] {
        assert!(name.len() <= BUFF_NAME_CAP, "{name}");
    }
}

/// 0.1.1 (2026-11-03 night logs: 6 lives, 0 GRAVE): the copy raised `q_win` from a Delayed 2 after the blow, and the
/// homing blow lands - and kills - on the next tick. Every blow (the slot's and the controller's) raises it in its own
/// Combine, ahead of the projectile, and no late one is left; 0.3.0: `q_hl` beside it (no data heal in the copy).
#[test]
fn every_blow_raises_q_win_and_q_hl_before_it_lands() {
    let copy = include_str!("../override/league_yorick.data_champion");
    let parts: Vec<&str> = copy.split("\"name\": \"league_yorick_q_blow\"").collect();
    assert!(parts.len() > 1, "no Last Rites blow in the copy");
    for (i, before) in parts[..parts.len() - 1].iter().enumerate() {
        for flag in [Q_WIN, Q_HL] {
            let at = before.rfind(flag).unwrap_or_else(|| panic!("blow {i}: no {flag} before it"));
            assert!(!before[at..].contains("\"Delayed\""), "blow {i}: its {flag} waits in a Delayed");
        }
    }
    assert!(!copy.contains("\"type\": \"Heal\""), "a data heal left in the copy: the add-on heals");
}

/// The copy asks for the units and lets the riding pictures play only without the flags; the wall's ask and flag; the
/// marks for her (tools/kit/build_yorick.py native=1 writes them; here the copy as shipped is read back).
#[test]
fn the_copy_asks_for_the_units_the_wall_and_the_marks() {
    let copy = include_str!("../override/league_yorick.data_champion");
    let count = |s: String| copy.matches(&s).count();
    // the Awakening: in the slot's Q and the two controllers' (hung by the attack and the ult)
    assert_eq!(count(format!("\"name\": \"{K_ASK}\"")), 3);
    assert_eq!(count(format!("\"name\": \"{K_ASK4}\"")), 3);
    assert_eq!(count(format!("\"buff_name\": \"{K_UNIT}\"")), 6, "three and four walkers, three Qs");
    assert_eq!(count(format!("\"name\": \"{K_UNIT}\"")), 3);
    assert_eq!(count(format!("\"name\": \"{E_ASK}\"")), 3);
    assert_eq!(count(format!("\"name\": \"{M_ASK}\"")), 1);
    assert_eq!(count(format!("\"buff_name\": \"{M_UNIT}\"")), 1);
    assert_eq!(count(format!("\"name\": \"{M_UNIT}\"")), 1);
    // W: cast by the controllers only
    assert_eq!(count(format!("\"name\": \"{W_ASK}\"")), 2);
    assert_eq!(count(format!("\"name\": \"{W_UP}\"")), 4, "added and taken off (refresh), two controllers");
    assert!(!copy.contains("league_yorick_w_band") && !copy.contains("\"Pull\""), "the main pack's slow band in the copy");
    // the marks: the attack and the mist lay `hit`
    assert_eq!(count(format!("\"name\": \"{HIT}\"")), 4, "the attack's twin, three mists");
    assert!(copy.contains("\"passive_ref\": \"league_yorick:shepherd\""));
    assert!(!copy.contains("league_yorick_e_ms"), "the data's haste in the copy: the add-on hastens by direction");
}

#[test]
fn the_units_are_built_from_his_numbers() {
    let his = StatV1 { attack: 150, magic_power: 30, hp: 900, defence: 80, magic_resistance: 40, move_speed: 1080,
                       hp_regen: 5, stack: 1, crit_chance: 10 };
    let w = walker_spec(&his, 2000, WALK_LIFE);
    assert_eq!((w.name.as_str(), w.life), ("league_yorick_walker", 600));
    assert_eq!(w.stat, StatV1 { attack: 150, magic_power: 0, hp: 300, defence: 0, magic_resistance: 0, move_speed: 1080,
                                hp_regen: 0, stack: 0, crit_chance: 0 });
    let a = w.attack;
    assert_eq!(a.attack + w.stat.attack * a.attack_ratio / 100, 28);
    assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (18_000, 60, 23, 10));
    // the Maiden: she does not walk or claw by herself (the add-on moves her and shoots her bolts)
    let m = maiden_spec(&his, 2000);
    assert_eq!((m.name.as_str(), m.life), ("league_yorick_maiden", 900));
    assert_eq!((m.stat.hp, m.stat.defence, m.stat.magic_resistance, m.stat.move_speed), (2400, 68, 68, 1));
    assert_eq!((m.attack.range, m.attack.cooltime), (1, 60));
    assert_eq!(walker_spec(&StatV1::default(), 0, 1).stat.hp, 1);
    assert_eq!((leap_damage(150), bolt_damage(150)), (65, 87));
}

#[test]
fn the_walkers_rise_round_the_target_and_leap_beside_their_prey() {
    let (at, here) = ((500_000.0, 300_000.0), (450_000.0, 300_000.0));
    for n in [3, 4] {
        let p = walker_points(at, here, n);
        assert_eq!(p.len(), n);
        for q in &p {
            assert!((summon::dist(*q, at) - WALK_SPREAD).abs() < 1.0);
            assert!(!(q.0 < at.0 && (q.1 - at.1).abs() < 1.0), "{q:?} between him and the target");
        }
    }
    assert_eq!(leap_spot((100_000.0, 100_000.0), (100_000.0, 160_000.0)), (100_000.0, 109_000.0));
    assert_eq!(leap_spot((100_000.0, 100_000.0), (104_000.0, 100_000.0)), (104_000.0, 100_000.0));
}

// ---- on the mock world (summon_mock.rs: our guess of the host, to check this side's logic) ----

const GAREN: usize = 1;
const DARIUS: usize = 2;
const MINION: usize = 3;

fn log_file() -> PathBuf {
    static SET: std::sync::Once = std::sync::Once::new();
    let path = std::env::temp_dir().join(format!("league_yorick_test_{}.log", std::process::id()));
    SET.call_once(|| {
        std::env::set_var("LEAGUE_YORICK_LOG", &path);
        let _ = std::fs::remove_file(&path);
        let _ = std::fs::remove_file(path.with_extension("cfg"));
    });
    path
}

/// Yorick #0 (team 0, attack 150, 2000 health) at (300000, 300000); Garen #1 40000 east of him, Darius #2 far south-east,
/// an enemy minion #3 far north; a player each for the champions. The host's heal, projectiles and levels on.
fn world() -> (World, Shepherd) {
    log_file();
    let mut w = World { heal_on: true, shots_on: true, levels_on: true, ..World::default() };
    let mut yorick = champion("league_yorick", 0, 300_000.0, 300_000.0);
    (yorick.hp, yorick.max, yorick.stat.attack, yorick.stat.defence) = (2000, 2000, 150, 80);
    let mut garen = champion("league_garen", 1, 340_000.0, 300_000.0);
    (garen.hp, garen.max) = (5000, 5000);
    let mut darius = champion("league_darius", 1, 600_000.0, 500_000.0);
    (darius.hp, darius.max) = (5000, 5000);
    w.units = vec![yorick, garen, darius, unit("melee_minion", EntityKindV1::Minion, 1, 300_000.0, 50_000.0, 300)];
    w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() },
                     MPlayer { team: 1, champion: DARIUS, ..Default::default() }];
    let mut me = Shepherd::default();
    w.sim(|sim| me.on_spawn(sim, 0, 0));
    (w, me)
}

fn tick(w: &mut World, me: &mut Shepherd) {
    for (name, caster, input) in w.due() {
        w.sim(|sim| match name.as_str() {
            "league_yorick:walkers" => WalkersFx.apply(sim, 0, caster, input),
            "league_yorick:maiden" => MaidenFx.apply(sim, 0, caster, input),
            "league_yorick:raise" => RaiseFx.apply(sim, 0, caster, input),
            "league_yorick:bolt" => BoltFx.apply(sim, 0, caster, input),
            "league_yorick:fade" => FadeFx.apply(sim, 0, caster, input),
            other => panic!("an effect nobody registered: {other}"),
        });
    }
    if w.units[0].hp > 0 {
        w.sim(|sim| me.on_update(sim, 0, 0, 0));
    }
    w.step();
}

fn run(w: &mut World, me: &mut Shepherd, n: usize) {
    for _ in 0..n {
        tick(w, me);
    }
}

/// A flag or ask as the data lays it (3 ticks).
fn lay(w: &mut World, on: usize, name: &str) -> usize {
    w.units[on].buffs.push((BuffV1::timed(name, 3), 3));
    w.tick
}

fn spawned(w: &World, name: &str) -> Vec<usize> {
    w.spawns.iter().filter(|s| s.name == name).filter_map(|s| s.gave).collect()
}

fn graves(w: &World) -> usize {
    graves_of([w.has(0, GRAVES[0]), w.has(0, GRAVES[1]), w.has(0, GRAVES[2]), w.has(0, GRAVES[3])])
}

fn forced(w: &World, id: usize) -> Option<CcV1> {
    w.units[id].ccs.iter().map(|c| c.0).find(|c| c.kind == CcKindV1::ForceMove.code())
}

fn moved_to(w: &World, id: usize, since: usize) -> Option<(u64, u64)> {
    w.moves.iter().filter(|m| m.1 == id && m.0 >= since).map(|m| m.2).last()
}

#[test]
fn the_wall_rises_where_the_mist_landed_and_holds_his_enemies_only() {
    let (mut w, mut me) = world();
    let c = (340_000.0, 300_000.0);
    // the copy's W lands under Garen: the centre is where he stands
    lay(&mut w, GAREN, W_ASK);
    run(&mut w, &mut me, 2);
    assert!(!w.has(GAREN, W_ASK) && me.walls.pending.len() == 1);
    // on the line at the rise: Darius within 210/225 of it, the minion beyond it; an ally of his on it; Garen inside
    (w.units[DARIUS].x, w.units[DARIUS].y) = (c.0 + 25_000.0, c.1);
    (w.units[MINION].x, w.units[MINION].y) = (c.0, c.1 - 33_000.0);
    w.units.push(champion("league_braum", 0, c.0 - 25_000.0, c.1));
    let ally = w.units.len() - 1;
    (w.units[GAREN].x, w.units[GAREN].y) = (c.0 + 18_000.0, c.1);
    let t0 = lay(&mut w, 0, W_UP);
    run(&mut w, &mut me, 1);
    assert_eq!(me.walls.live.len(), 1);
    let darius = forced(&w, DARIUS).expect("Darius not pulled in");
    assert_eq!((darius.dx, darius.dy), (-5_001, 0));
    let minion = forced(&w, MINION).expect("the minion not pushed out");
    assert_eq!((minion.dx, minion.dy), (0, -7_001));
    assert!(forced(&w, ally).is_none() && forced(&w, GAREN).is_none() && forced(&w, 0).is_none());
    // Garen walks out (1500 a tick): free inside, then slid back onto the inner face
    let mut kept = false;
    for k in 1..=3 {
        w.units[GAREN].x = c.0 + 18_000.0 + 1_500.0 * k as f64;
        let t = w.tick;
        tick(&mut w, &mut me);
        if let Some(to) = moved_to(&w, GAREN, t) {
            assert_eq!(to, ((c.0 + 19_999.0) as u64, c.1 as u64));
            kept = true;
        }
    }
    assert!(kept, "Garen walked through the wall");
    // the ally walks across the line: never moved
    for k in 1..=10 {
        w.units[ally].x = c.0 - 25_000.0 - 2_000.0 * k as f64;
        tick(&mut w, &mut me);
    }
    assert!(w.moves.iter().all(|m| m.1 != ally && m.1 != 0), "the wall held one of his own");
    // Darius was being pulled (no forced move in this world): once the push is over he is set on the inner face
    assert!(moved_to(&w, DARIUS, t0).is_some_and(|p| summon::dist((p.0 as f64, p.1 as f64), c) <= 20_000.0));
    // a Flash out: let through, and from then on kept out
    let t = w.tick;
    w.units[GAREN].x = c.0 + 60_000.0;
    tick(&mut w, &mut me);
    assert!(moved_to(&w, GAREN, t).is_none(), "the Flash was held");
    // ... and walking back in (2000 a tick) he is held on the outer face
    let t = w.tick;
    for _ in 0..12 {
        w.units[GAREN].x -= 2_000.0;
        tick(&mut w, &mut me);
    }
    assert_eq!(moved_to(&w, GAREN, t), Some(((c.0 + 40_001.0) as u64, c.1 as u64)));
    // its time over: down, nothing held any more
    run(&mut w, &mut me, 240);
    assert!(me.walls.live.is_empty());
    let t = w.tick;
    w.units[GAREN].x = c.0 + 20_000.0;
    run(&mut w, &mut me, 3);
    assert!(moved_to(&w, GAREN, t).is_none());
    let text = std::fs::read_to_string(log_file()).expect("the log");
    for what in ["WALL ASK #", "WALL #", "ring at (340000,300000) line 30000 (inside within 20000, outside beyond 40000), 240 ticks",
                 "PUSHED #", "league_darius#2 IN on the wall line 25000", "melee_minion#3 OUT", "KEPT IN #", "league_garen#1 held at",
                 "LEAPT OUT #", "KEPT OUT #", "WALL DOWN #"] {
        assert!(text.contains(what), "missing {what:?} in the log");
    }
}

#[test]
fn no_ask_no_wall() {
    let (mut w, mut me) = world();
    lay(&mut w, 0, W_UP);
    run(&mut w, &mut me, 2);
    assert!(me.walls.live.is_empty() && w.moves.is_empty() && w.units.iter().all(|u| u.ccs.is_empty()));
}

#[test]
fn graves_from_last_rites_kills_and_from_every_nth_death_near_him() {
    let (mut w, mut me) = world();
    // Last Rites kills a minion: a grave, and its death is not counted again
    let m = w.units.len();
    w.units.push(unit("melee_minion", EntityKindV1::Minion, 1, 310_000.0, 300_000.0, 100));
    run(&mut w, &mut me, 1);
    lay(&mut w, 0, Q_WIN);
    w.hurt(m, 1000);
    w.sim(|sim| me.on_unit_kill(sim, 0, 0, m));
    run(&mut w, &mut me, 2);
    assert_eq!((graves(&w), me.deaths), (1, 0));
    // eight more die near him at level 1 (no Q): the eighth digs one
    for k in 0..8 {
        let id = w.units.len();
        w.units.push(unit("caster_minion", EntityKindV1::Minion, 1, 320_000.0, 290_000.0 + 1000.0 * k as f64, 100));
        run(&mut w, &mut me, 1);
        w.hurt(id, 1000);
        run(&mut w, &mut me, 1);
        assert_eq!(graves(&w), if k < 7 { 1 } else { 2 }, "after {} deaths", k + 1);
    }
    // far ones do not count; at level 12 every second near one does, up to four, then it stays four
    let far = w.units.len();
    w.units.push(unit("caster_minion", EntityKindV1::Minion, 1, 900_000.0, 900_000.0, 100));
    run(&mut w, &mut me, 1);
    w.hurt(far, 1000);
    run(&mut w, &mut me, 1);
    assert_eq!(me.deaths, 0);
    w.units[0].level = 12;
    for _ in 0..8 {
        let id = w.units.len();
        w.units.push(unit("caster_minion", EntityKindV1::Minion, 1, 320_000.0, 300_000.0, 100));
        run(&mut w, &mut me, 1);
        w.hurt(id, 1000);
        run(&mut w, &mut me, 1);
    }
    assert_eq!(graves(&w), 4);
    assert!(GRAVES.iter().all(|g| w.has(0, g)), "the rungs below the top run out with it");
    let text = std::fs::read_to_string(log_file()).expect("the log");
    assert!(text.contains("died to Last Rites - 1 grave(s) now"));
    assert!(text.contains("the 8th death since the last such grave (level 1)"));
}

#[test]
fn the_awakening_raises_a_walker_a_grave() {
    for (ask, n) in [(K_ASK, 3), (K_ASK4, 4)] {
        let (mut w, mut me) = world();
        let t0 = lay(&mut w, GAREN, ask);
        run(&mut w, &mut me, Q_HIT + 1);
        let walkers = spawned(&w, WALKER);
        assert_eq!(walkers.len(), n, "{ask}");
        assert!(w.spawns.iter().all(|s| s.tick <= t0 + 3 && s.life as usize == WALK_LIFE));
        assert!(w.has(0, K_UNIT), "no flag on him when the data looks: the riding walkers would play too");
        assert_eq!(me.walkers.live.len(), n);
        assert!(!w.has(GAREN, ask));
    }
}

#[test]
fn no_unit_from_the_host_leaves_the_data_its_walkers() {
    // no slot, a refusal, an id that never reads as a unit, units gone at once
    for case in 0..4 {
        let (mut w, mut me) = world();
        match case {
            0 => w.has_spawn = false,
            1 => w.spawn_ok = false,
            2 => w.spawn_never = true,
            _ => {}
        }
        let t0 = lay(&mut w, GAREN, K_ASK);
        if case == 3 {
            run(&mut w, &mut me, 3);
            assert!(w.has(0, K_UNIT) && me.walkers.live.len() == 3, "case {case}");
            for id in spawned(&w, WALKER) {
                w.units[id].valid = false;
            }
        }
        while w.tick < t0 + Q_HIT + 1 {
            tick(&mut w, &mut me);
        }
        assert!(!w.has(0, K_UNIT), "case {case}: the flag is on him when the data looks - no walkers at all");
        run(&mut w, &mut me, 200);
        assert!(me.walkers.is_empty() && w.queue.is_empty(), "case {case}");
    }
}

#[test]
fn the_mist_makes_the_walkers_leap_and_pounce_once() {
    let (mut w, mut me) = world();
    lay(&mut w, GAREN, K_ASK);
    run(&mut w, &mut me, 30);
    let walkers = spawned(&w, WALKER);
    // the mist strikes Darius far south-east: only walkers within LEAP_REACH leap - none here
    lay(&mut w, DARIUS, E_ASK);
    run(&mut w, &mut me, 2);
    assert!(w.moves.is_empty());
    // Darius steps in, 100000 from the walkers: they leap to his side, the pounce (20 + 30 % of 150 = 65) once
    (w.units[DARIUS].x, w.units[DARIUS].y) = (440_000.0, 300_000.0);
    lay(&mut w, DARIUS, E_ASK);
    run(&mut w, &mut me, 2);
    assert_eq!(w.moves.len(), 3, "{:?}", w.moves);
    for (_, id, at) in &w.moves {
        assert!(walkers.contains(id));
        let d = summon::dist((at.0 as f64, at.1 as f64), (440_000.0, 300_000.0));
        assert!(d <= LEAP_SIDE + 1.0, "{d}");
    }
    assert_eq!(w.dealt(0, DamageTypeV1::Ad), vec![(DARIUS, 65)]);
    assert_eq!(w.viewed(K_LEAP_VIEW), 1);
}

#[test]
fn the_maiden_follows_him_shoots_and_her_mark_is_spent_on_her_target() {
    let (mut w, mut me) = world();
    w.units[0].level = 9;
    lay(&mut w, GAREN, M_ASK);
    run(&mut w, &mut me, R_REL + 1);
    let her = spawned(&w, MAIDEN_UNIT);
    assert_eq!(her.len(), 1);
    let s = w.spawns.iter().find(|s| s.name == MAIDEN_UNIT).unwrap().clone();
    assert_eq!((s.at, s.life as usize, s.stat.move_speed, s.attack.range), ((340_000, 289_000), MAID_LIFE, 1, 1));
    assert_eq!(spawned(&w, WALKER).len(), escort(9), "level 9: three walkers with her");
    assert!(w.has(0, M_UNIT) && w.has(0, R_ON));
    // her bolts: at Garen (the nearest champion), a projectile with the bolt's effect; it lands, magic and her mark
    run(&mut w, &mut me, 40);
    let shot = w.shots.first().expect("no bolt").clone();
    assert_eq!((shot.1.as_str(), shot.2.as_str(), shot.3.target_id, shot.3.caster_id), (R_BOLT, "league_yorick:bolt", GAREN, 0));
    assert!(summon::dist((shot.3.x as f64, shot.3.y as f64), (340_000.0, 289_000.0)) < 100.0, "the bolt leaves from her");
    assert!(w.dealt(0, DamageTypeV1::Ap).contains(&(GAREN, 87)), "{:?}", w.dealt(0, DamageTypeV1::Ap));
    assert!(w.has(GAREN, R_MKV));
    // his attack strikes Garen (the copy's `hit`): the mark spent, 25 per mille of 5000 at level 9
    lay(&mut w, GAREN, HIT);
    run(&mut w, &mut me, 1);
    assert!(w.dealt(0, DamageTypeV1::Ap).contains(&(GAREN, 125)));
    assert!(!w.has(GAREN, R_MKV) && !w.has(GAREN, HIT));
    // a `hit` on a champion without her mark: nothing
    let before = w.damage.len();
    lay(&mut w, DARIUS, HIT);
    run(&mut w, &mut me, 1);
    assert_eq!(w.damage.iter().skip(before).filter(|d| d.2 == DARIUS).count(), 0);
    // she glided to her spot behind him already (this world does not carry out forced moves: put her there); he walks
    // off: she glides after him (a forced move toward her new spot)
    let spot = follow_spot((w.units[0].x, w.units[0].y), (w.units[her[0]].x, w.units[her[0]].y));
    (w.units[her[0]].x, w.units[her[0]].y) = spot;
    w.units[her[0]].ccs.clear();
    w.units[0].x += 120_000.0;
    run(&mut w, &mut me, 1);
    let mv = forced(&w, her[0]).expect("she stayed behind");
    assert!(mv.dx > 0, "{mv:?}");
    // killed: Q's halved cooldown goes with her
    w.hurt(her[0], 1_000_000);
    run(&mut w, &mut me, 3);
    assert!(!w.has(0, R_ON) && me.maiden.live.is_empty());
}

#[test]
fn her_army_raises_walkers_from_bodies_near_her() {
    let (mut w, mut me) = world();
    lay(&mut w, GAREN, M_ASK);
    run(&mut w, &mut me, R_REL + 4);
    let before = spawned(&w, WALKER).len();
    assert_eq!(before, R_N);
    // a minion dies 20000 from her: a walker rises from it
    let m = w.units.len();
    w.units.push(unit("melee_minion", EntityKindV1::Minion, 1, 340_000.0, 270_000.0, 100));
    run(&mut w, &mut me, 1);
    w.hurt(m, 1000);
    run(&mut w, &mut me, 4);
    let raised: Vec<_> = w.spawns.iter().filter(|s| s.name == WALKER && s.gave.is_some()).skip(before).collect();
    assert_eq!(raised.len(), 1);
    assert_eq!(raised[0].at, (340_000, 270_000));
    assert!(me.walkers.live.iter().filter(|m| m.extra.kind == Walk::Escort).count() == before + 1);
}

#[test]
fn his_death_takes_his_walkers_and_fades_the_maiden() {
    let (mut w, mut me) = world();
    lay(&mut w, GAREN, K_ASK);
    run(&mut w, &mut me, 20);
    lay(&mut w, GAREN, M_ASK);
    run(&mut w, &mut me, 30);
    let walkers = spawned(&w, WALKER);
    let her = spawned(&w, MAIDEN_UNIT)[0];
    (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
    w.sim(|sim| me.on_dead(sim, 0));
    assert!(walkers.iter().all(|id| w.units[*id].hp == 0), "a walker lived on");
    assert!(w.units[her].hp > 0, "she goes within 3 s, not at once");
    let mut seen = Vec::new();
    for _ in 0..(FADE_STEPS + 2) * FADE_EVERY {
        tick(&mut w, &mut me);
        seen.push(w.units[her].hp);
    }
    assert_eq!(w.units[her].hp, 0, "she stood on");
    assert!(seen.windows(2).all(|p| p[1] <= p[0]), "her health went up while fading");
}

#[test]
fn last_rites_heals_by_his_missing_health() {
    for champion_hit in [true, false] {
        let (mut w, mut me) = world();
        w.units[0].hp = 1000;
        lay(&mut w, 0, Q_HL);
        if champion_hit {
            lay(&mut w, 0, Q_CH);
        }
        run(&mut w, &mut me, 4);
        let want = q_heal(1, 1000, 2000, champion_hit);
        assert_eq!(w.heals.iter().map(|h| (h.1, h.2, h.3)).collect::<Vec<_>>(), vec![(0, 0, want)], "champion {champion_hit}");
        assert_eq!(want, if champion_hit { 70 } else { 35 });
    }
}

#[test]
fn the_mist_s_mark_hastens_them_toward_it() {
    let (mut w, mut me) = world();
    w.units[GAREN].buffs.push((BuffV1::timed(E_MARK, 240), 240));
    let speed = |w: &World| w.units[0].buffs.iter().filter(|b| b.0.name() == E_MS).map(|b| b.0.move_speed_mult).sum::<i32>();
    // toward Garen (east): +18% at level 1
    for _ in 0..3 {
        w.units[0].x += 800.0;
        tick(&mut w, &mut me);
    }
    assert_eq!(speed(&w), 18);
    // away from him: it runs out
    for _ in 0..5 {
        w.units[0].x -= 800.0;
        tick(&mut w, &mut me);
    }
    assert_eq!(speed(&w), 0);
}

#[test]
fn the_log_tells_the_units_whole_lives() {
    let (mut w, mut me) = world();
    lay(&mut w, GAREN, K_ASK);
    run(&mut w, &mut me, 100);
    let walkers = spawned(&w, WALKER);
    let mut dealt = 28;
    w.sim(|sim| me.on_attack(sim, 0, walkers[0], GAREN, &mut dealt));
    w.players[1].gold += 14;
    w.hurt(walkers[1], 100_000);
    lay(&mut w, GAREN, M_ASK);
    run(&mut w, &mut me, 100);
    (w.units[DARIUS].x, w.units[DARIUS].y) = (400_000.0, 300_000.0);
    lay(&mut w, DARIUS, E_ASK);
    run(&mut w, &mut me, 600);
    let text = std::fs::read_to_string(log_file()).expect("the log");
    let mine: Vec<&str> = text.lines().filter(|l| l.contains(" WALKER") || l.contains(" MAIDEN ") || l.contains(" HOOK ")).collect();
    let has = |what: &str| mine.iter().any(|l| l.contains(what));
    for what in [
        "WALKERS ASK #", "the Awakening on #1 league_garen at (340000,300000): 3 walkers asked for round it",
        "WALKERS SPAWN #", "3 of 3 units [4, 5, 6] for team 0 round (340000,300000): 'league_yorick_walker' for 600 ticks",
        "WALKER #1 LOOK #", "(the Awakening's): #4 reads back as name 'league_yorick_walker' kind summon team 0",
        " of 600 ticks, at (", "KILLED after ", "p1 gold +14",
        "HOOK #", "on_attack: entity #4 (the walker #1) -> #1 league_garen, damage 28",
        "MAIDEN ASK #", "Eulogy of the Isles on #1 league_garen at (", "the Maiden asked for 11000 behind it, 2 walkers round her",
        "MAIDEN SPAWN #", "'league_yorick_maiden' for 900 ticks", "her escort: 2 of 2 walkers",
        "MAIDEN #1 LOOK #", "league_yorick_r_on on Yorick for her 899 ticks", "MAIDEN #1 DRESS #", "league_yorick_r_on is on Yorick",
        "(the Maiden's escort)", "WALKERS LEAP #", "the mist struck #2 league_darius at (400000,300000): ",
        "MAIDEN #1 BOLT #", "TIMED OUT after ", "WAKE #",
    ] {
        assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
    }
    assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
    let longest = mine.iter().map(|l| l.len()).max().unwrap();
    assert!(longest < 700, "a line of {longest} bytes");
}

/// The books when an ask's units never come and another ask follows while it waits (summon::Flock gives all handoffs
/// of a tick to the oldest waiting ask): the Awakening's walkers refused, the Maiden asked for 2 ticks later - her
/// escort must read as hers (Escort, MAID_LIFE from her ask), not as the Awakening's (Awake, WALK_LIFE); and the
/// other way round, her escort refused and the Awakening asked for 2 ticks later.
#[test]
fn an_ask_made_while_the_walkers_last_one_waits_keeps_its_own_units() {
    for maiden_first in [false, true] {
        let (mut w, mut me) = world();
        w.spawn_ok = false;
        lay(&mut w, GAREN, if maiden_first { M_ASK } else { K_ASK });
        run(&mut w, &mut me, 2);
        assert!(spawned(&w, WALKER).is_empty() && spawned(&w, MAIDEN_UNIT).is_empty());
        w.spawn_ok = true;
        let t1 = lay(&mut w, GAREN, if maiden_first { K_ASK } else { M_ASK });
        let (read, flag) = if maiden_first { (Q_HIT, K_UNIT) } else { (R_REL, M_UNIT) };
        while w.tick < t1 + read {
            tick(&mut w, &mut me);
        }
        assert!(w.has(0, flag), "maiden_first {maiden_first}: no {flag} when the data reads it");
        run(&mut w, &mut me, summon::FLOCK_LOOKS);
        let (kind, life, n) = if maiden_first { (Walk::Awake, WALK_LIFE, K_N) } else { (Walk::Escort, MAID_LIFE, R_N) };
        assert_eq!(spawned(&w, WALKER).len(), n, "maiden_first {maiden_first}");
        assert!(w.spawns.iter().filter(|s| s.name == WALKER && s.gave.is_some()).all(|s| s.life as usize == life && s.tick >= t1));
        assert_eq!(me.walkers.live.len(), n, "maiden_first {maiden_first}");
        for m in &me.walkers.live {
            assert_eq!((m.extra.kind, m.unit.life), (kind, life), "maiden_first {maiden_first}: {m:?}");
            assert!(m.unit.born >= t1, "maiden_first {maiden_first}: born {} before its ask at {t1}", m.unit.born);
        }
        assert_eq!(me.maiden.live.len(), usize::from(!maiden_first));
    }
}

#[test]
fn the_flags_are_up_before_the_data_reads_them_and_a_lost_unit_is_told_before_it() {
    assert!(3 + summon::FLOCK_WAIT + summon::FLOCK_LOOKS < Q_HIT + 1);
    assert!(3 + LOST_AGE < Q_HIT + 1);
    assert!(R_REL >= Q_HIT);
    assert!(FLAG_TICKS > R_REL + 1 && FLAG_TICKS < WALK_LIFE);
    assert!(UID_TICKS > 2);
    // the wall's centre waits for its flag a little longer than the data's delay
    assert!(wall::PEND_SLACK > 2);
}

#[test]
fn champions_pressing_the_wall_break_it_with_the_picture_s_next_piece() {
    let (mut w, mut me) = world();
    let c = (340_000.0, 300_000.0);
    lay(&mut w, GAREN, W_ASK);
    run(&mut w, &mut me, 1);
    (w.units[GAREN].x, w.units[GAREN].y) = (c.0 + 10_000.0, c.1);
    lay(&mut w, 0, W_UP);
    run(&mut w, &mut me, 1);
    let from = me.walls.live[0].ring.from;
    assert_eq!((wall::next_piece(from, from), wall::next_piece(from, from + 15), wall::next_piece(from, from + 44)),
               (from + 15, from + 45, from + 45));
    // Garen keeps walking into the wall: at level 1 two blows (his attack interval unread: one a BLOW_EVERY ticks)
    let need = (2 * wall::BLOW_EVERY) as usize;
    let mut broke = None;
    for k in 0..need + 40 {
        w.units[GAREN].x = c.0 + 21_500.0;
        tick(&mut w, &mut me);
        if broke.is_none() && w.has(0, W_DOWN) {
            broke = Some(k);
        }
        if me.walls.live.is_empty() {
            break;
        }
    }
    let k = broke.expect("never broke");
    assert!((need - 2..=need + 1).contains(&k), "broke after {k} pressed ticks, not about {need}");
    assert!(me.walls.live.is_empty(), "still standing past its next piece");
    // fallen: walking out is free now
    let t = w.tick;
    w.units[GAREN].x = c.0 + 23_000.0;
    run(&mut w, &mut me, 2);
    assert!(moved_to(&w, GAREN, t).is_none());
    let text = std::fs::read_to_string(log_file()).expect("the log");
    assert!(text.contains("BROKEN #") && text.contains("(2 needed at level 1)") && text.contains("(broken, struck "),
            "no BROKEN / WALL DOWN (broken) line");
}
