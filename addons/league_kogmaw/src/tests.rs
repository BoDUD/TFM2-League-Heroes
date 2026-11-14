//! Unit tests and the mock world (league_shaco_backstab's summon_mock.rs: our guess of the host, to check this side's logic -
//! it does not say how the game moves or draws a unit).

use super::mock::{champion, unit, MPlayer, World};
use super::*;

// ===================== rules =====================

#[test]
fn the_burst_is_the_main_packs_splash() {
    assert_eq!(burst_damage(0), 80);
    assert_eq!(burst_damage(106), 186, "his level-1 attack");
    assert_eq!(burst_damage(250), 330);
    assert_eq!(reach(0), 12_000.0);
    assert_eq!(reach(3_000), 15_000.0, "a unit's radius counts, as in the engine's circles");
}

#[test]
fn a_step_is_the_pace_and_never_past_the_prey() {
    let (to, s) = step_toward((0.0, 0.0), (10_000.0, 0.0), 1_000.0);
    assert_eq!((to, s), ((1_000.0, 0.0), 1_000.0));
    let (to, s) = step_toward((0.0, 0.0), (300.0, 400.0), 1_000.0);
    assert_eq!((to, s), ((300.0, 400.0), 500.0), "stops on the prey");
    let (to, s) = step_toward((5.0, 5.0), (5.0, 5.0), 1_000.0);
    assert_eq!((to, s), ((5.0, 5.0), 0.0));
    let (to, _) = step_toward((0.0, 0.0), (-3_000.0, 4_000.0), 1_000.0);
    assert!((to.0 + 600.0).abs() < 1e-9 && (to.1 - 800.0).abs() < 1e-9);
}

#[test]
fn the_form_is_his_body_without_a_walk_or_an_attack_of_its_own() {
    let s = form_spec(950, 20, 15);
    assert_eq!((s.name.as_str(), s.life), (UNIT, FORM_T + LIFE_SLACK));
    assert_eq!(s.stat, StatV1 { attack: 0, magic_power: 0, hp: 950, defence: 20, magic_resistance: 15, move_speed: 1, hp_regen: 0,
                                stack: 0, crit_chance: 0 });
    let a = s.attack;
    assert_eq!((a.attack, a.attack_ratio, a.range), (0, 0, 1), "it never swings at anyone");
    assert_eq!(form_spec(0, 0, 0).stat.hp, 1);
    let g = guard(10);
    assert_eq!((g.name(), g.damaged_reduce, g.undying, g.ignore_wall, g.cc_immune), (GUARD, 100, true, true, false),
               "not crowd-control immune: the hook clears its crowd control itself and taunts it");
    assert_eq!(g.duration_tick, 10);
}

#[test]
fn the_names_fit_and_the_tag_reads_back() {
    for name in [UNIT, GUARD, GO, VOID_VIEW, HIT_VIEW, BOOM, FORM_PROJ, &sim_tag(u64::MAX)] {
        assert!(name.starts_with("league_kogmaw_") && name.len() <= BUFF_NAME_CAP, "{name}");
    }
    assert!(sim_tag(7).contains("_sim:"), "league.dll's divergence check leaves it out");
    assert_eq!(parse_tag(&sim_tag(42)), Some(42));
    assert_eq!(parse_tag("league_karthus_sim:42"), None);
    assert_eq!(parse_tag("league_kogmaw_sim:x"), None);
}

#[test]
fn the_numbers_match_the_kit() {
    let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_kogmaw.py");
    let src = std::fs::read_to_string(path).expect("build_kogmaw.py");
    for (key, v) in [("p_dmg", P_DMG), ("p_ratio", P_RATIO), ("p_r", P_R), ("p_speed", P_SPEED), ("p_seek", P_SEEK)] {
        assert!(src.contains(&format!("\"{key}\": {v},")), "{key} is not {v} in build_kogmaw.P");
    }
}

#[test]
fn the_copy_wakes_the_form_instead_of_the_comet() {
    let copy = include_str!("../override/league_kogmaw.data_champion").replace("\r\n", "\n");
    let main = include_str!("../../../league/champion/league_kogmaw.data_champion").replace("\r\n", "\n");
    // every slot's watch: the Native in place of the comet's RandomTarget, the wake's light and sounds kept
    assert_eq!(copy.matches(&format!("\"effect_ref\": \"{VOID_FX}\"")).count(), 4);
    assert_eq!(main.matches("\"name\": \"league_kogmaw_p_burst\"").count(), 4);
    assert_eq!(copy.matches("\"name\": \"league_kogmaw_p_burst\"").count(), 0, "the hidden splash is the add-on's now");
    assert_eq!(copy.matches("\"type\": \"TargetProjectile\",\n").count() + 4,
               main.matches("\"type\": \"TargetProjectile\",\n").count(), "only the four comets went");
    for kept in ["\"name\": \"league_kogmaw_p_wake\"", "\"name\": \"league_kogmaw_vo_p\"", "\"name\": \"league_kogmaw_p_watch\""] {
        assert_eq!(copy.matches(kept).count(), main.matches(kept).count(), "{kept}");
    }
    // the pictures the add-on plays: the burst (new), the comet's for the fallback, the hit
    for view in [VOID_VIEW, FORM_PROJ, BOOM, HIT_VIEW] {
        assert!(copy.contains(&format!("\"name\": \"{view}\"")), "{view} has no view in the copy");
    }
    assert!(copy.contains("\"anim\": \"asset/league/effects/league_kogmaw_burst\""));
    assert!(copy.contains(&format!("\"passive_ref\": \"{PASSIVE}\"")));
}

// ===================== the mock world =====================

fn log_file() -> std::path::PathBuf {
    static SET: std::sync::Once = std::sync::Once::new();
    let path = std::env::temp_dir().join(format!("league_kogmaw_test_{}.log", std::process::id()));
    SET.call_once(|| {
        std::env::set_var("LEAGUE_KOGMAW_LOG", &path);
        let _ = std::fs::remove_file(&path);
        let _ = std::fs::remove_file(path.with_extension("cfg"));
    });
    path
}

const KOG: usize = 0;
const GAREN: usize = 1;
const DARIUS: usize = 2;
const AHRI: usize = 3;
const MINION: usize = 6;

/// Kog'Maw #0 (team 0, attack 106, 950 health) at (300000, 300000); Garen #1 (team 1) 60000 east of him, Darius #2 far
/// south-east, Ahri #3 (his ally) far north-west; the nexuses #4 / #5 in the corners (the simulation's number hangs on them),
/// a red minion #6 beside Garen, on his near side. A player for each champion.
fn world() -> World {
    log_file();
    let mut w = World::default();
    let mut kog = champion("league_kogmaw", 0, 300_000.0, 300_000.0);
    (kog.hp, kog.max, kog.stat.attack, kog.stat.hp, kog.stat.defence, kog.stat.magic_resistance) = (950, 950, 106, 950, 20, 15);
    let mut garen = champion("league_garen", 1, 360_000.0, 300_000.0);
    (garen.hp, garen.max) = (5_000, 5_000);
    w.units = vec![kog, garen, champion("league_darius", 1, 700_000.0, 700_000.0), champion("league_ahri", 0, 50_000.0, 50_000.0),
                   unit("nexus", EntityKindV1::Nexus, 0, 20_000.0, 20_000.0, 5_000),
                   unit("nexus", EntityKindV1::Nexus, 1, 900_000.0, 900_000.0, 5_000),
                   unit("melee_minion", EntityKindV1::Minion, 1, 354_000.0, 306_000.0, 500)];
    w.players = vec![MPlayer { team: 0, champion: KOG, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() },
                     MPlayer { team: 1, champion: DARIUS, ..Default::default() }, MPlayer { team: 0, champion: AHRI, ..Default::default() }];
    w
}

/// His passive's life: on_spawn and `n` ticks of on_update, the world stepping.
fn live(w: &mut World, me: usize, n: usize) -> LifeWatch {
    let mut p = LifeWatch::default();
    w.sim(|sim| p.on_spawn(sim, me, me));
    for _ in 0..n {
        w.sim(|sim| p.on_update(sim, 0, me, me));
        w.sim(step_forms);
        w.step();
    }
    p
}

/// He falls: in the game his entity is gone at once (`champion()` reads none, the revive is a new one).
fn fall(w: &mut World, me: usize) {
    let tick = w.tick;
    let u = &mut w.units[me];
    (u.hp, u.died, u.valid) = (0, Some(tick), false);
}

/// The copy's watch lands and finds him gone: `:void` at the spot (his body).
fn wake_at(w: &mut World, me: usize, at: (f64, f64)) {
    w.sim(|sim| VoidFx.apply(sim, 0, me, at_input(at)));
}

/// One tick: the queued effects due (none here), the match hook, the world's own step.
fn tick(w: &mut World) {
    for (name, caster, input) in w.due() {
        w.sim(|sim| match name.as_str() {
            "league_kogmaw:burst" => BurstFx.apply(sim, 0, caster, input),
            other => panic!("an effect nobody registered: {other}"),
        });
    }
    w.sim(step_forms);
    w.step();
}

fn forms(w: &World) -> Vec<usize> {
    w.spawns.iter().filter(|s| s.name == UNIT).filter_map(|s| s.gave).collect()
}

fn true_damage(w: &World, target: usize) -> Vec<(usize, usize, usize)> {
    w.damage.iter().filter(|d| d.2 == target && d.4 == DamageTypeV1::Fixed.code()).map(|d| (d.0, d.1, d.3)).collect()
}

/// Ticks until the form's banish (its burst), at most `most`: the tick it came.
fn until_burst(w: &mut World, id: usize, most: usize) -> Option<usize> {
    for _ in 0..most {
        if let Some(b) = w.banishes.iter().find(|b| b.2 == id) {
            return Some(b.0);
        }
        tick(w);
    }
    w.banishes.iter().find(|b| b.2 == id).map(|b| b.0)
}

#[test]
fn the_form_runs_at_the_nearest_champion_and_bursts_on_it() {
    let mut w = world();
    live(&mut w, KOG, 10);
    fall(&mut w, KOG);
    assert!(w.sim(|sim| sim.get_player(0).and_then(|p| p.champion()).is_none()), "dead: no champion entity");
    let t0 = w.tick;
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    let ids = forms(&w);
    assert_eq!(ids.len(), 1);
    let s = &w.spawns[0];
    assert_eq!((s.name.as_str(), s.summoner, s.team, s.at, s.life as usize), (UNIT, KOG, 0, (300_000, 300_000), FORM_T + LIFE_SLACK));
    assert_eq!((s.stat.move_speed, s.stat.hp, s.attack.attack, s.attack.attack_ratio, s.attack.range), (1, 950, 0, 0, 1));
    let id = ids[0];
    assert!(w.has(id, GUARD), "guarded from its first tick");
    // a tick on: it has walked toward Garen, one pace
    tick(&mut w);
    let (x, y) = (w.units[id].x, w.units[id].y);
    assert!((x - 301_000.0).abs() <= 2.0 && (y - 300_000.0).abs() <= 2.0, "({x}, {y})");
    assert!(w.has(id, GO), "walking: the display flag is on");
    // Garen 60000 east, the burst within 12000 + his radius (10000 here): 38 paces
    let at = until_burst(&mut w, id, 100).expect("no burst");
    assert!((t0 + 36..=t0 + 39).contains(&at), "burst at {} ticks", at - t0);
    let hits = true_damage(&w, GAREN);
    assert_eq!(hits.len(), 1, "{hits:?}");
    assert_eq!((hits[0].1, hits[0].2), (KOG, 186), "his name, 80 + 100% of his 106");
    assert_eq!(true_damage(&w, MINION).len(), 1, "the minion beside Garen too");
    for spared in [DARIUS, AHRI, 4, 5] {
        assert!(true_damage(&w, spared).is_empty(), "#{spared}");
    }
    assert_eq!(w.viewed(VOID_VIEW), 1);
    assert_eq!(w.viewed(HIT_VIEW), 2);
    assert_eq!(w.heard(BOOM), 1);
    let b = w.banishes.iter().find(|b| b.2 == id).unwrap();
    assert!(b.3 >= 1 && b.0 + b.3 > t0 + FORM_T + LIFE_SLACK, "banished for the rest of its life: {b:?}");
    // off the books, nothing more
    for _ in 0..300 {
        tick(&mut w);
    }
    assert_eq!(true_damage(&w, GAREN).len(), 1);
    assert_eq!(w.viewed(VOID_VIEW), 1);
}

#[test]
fn no_champion_to_reach_it_waits_out_its_four_seconds() {
    let mut w = world();
    live(&mut w, KOG, 5);
    for id in [GAREN, DARIUS] {
        w.units[id].hp = 0;
        w.units[id].died = Some(w.tick);
    }
    fall(&mut w, KOG);
    let t0 = w.tick;
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    let id = forms(&w)[0];
    let at = until_burst(&mut w, id, FORM_T + 20).expect("no burst at its time");
    assert_eq!(at, t0 + FORM_T);
    assert!((w.units[id].x - 300_000.0).abs() < 300.0, "it stood where he fell");
    assert!(w.damage.iter().all(|d| d.4 != DamageTypeV1::Fixed.code()), "nobody within reach");
    assert_eq!(w.viewed(VOID_VIEW), 1, "it still bursts where it stands");
}

#[test]
fn no_unit_from_the_host_flies_the_comet_as_before() {
    for case in 0..3 {
        let mut w = world();
        live(&mut w, KOG, 5);
        fall(&mut w, KOG);
        match case {
            0 => w.has_spawn = false,
            1 => w.spawn_ok = false,
            _ => w.spawn_never = true,
        }
        let t0 = w.tick;
        wake_at(&mut w, KOG, (300_000.0, 300_000.0));
        for _ in 0..LOOKS + 2 {
            tick(&mut w);
        }
        // the mock has no spawn_projectile (the host refuses the comet): the burst lands on Garen at once
        let hits = true_damage(&w, GAREN);
        assert_eq!(hits.len(), 1, "case {case}: {hits:?}");
        assert_eq!(hits[0].2, 186);
        assert!(hits[0].0 <= t0 + LOOKS + 1, "case {case}: at {}", hits[0].0 - t0);
        assert_eq!(w.viewed(BOOM), 1, "case {case}: the comet's own burst picture");
        assert_eq!(w.viewed(VOID_VIEW), 0, "case {case}");
        for _ in 0..300 {
            tick(&mut w);
        }
        assert_eq!(true_damage(&w, GAREN).len(), 1, "case {case}: once");
    }
    // Garen out of the comet's sight (70000): nothing, as the main pack's RandomTarget
    let mut w = world();
    w.units[GAREN].x = 380_000.0;
    w.units[MINION].x = 390_000.0;
    w.units[MINION].y = 300_000.0;
    live(&mut w, KOG, 5);
    fall(&mut w, KOG);
    w.has_spawn = false;
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    for _ in 0..20 {
        tick(&mut w);
    }
    assert!(w.damage.iter().all(|d| d.4 != DamageTypeV1::Fixed.code()));
}

#[test]
fn the_comet_spec_homes_on_the_champion() {
    let s = comet_spec(26, 1, (1234.4, 5678.6), 31);
    assert_eq!((s.caster_id, s.team, s.x, s.y, s.target_id, s.speed), (26, 1, 1234, 5679, 31, P_SPEED as u64));
    assert_eq!(s.move_kind, ProjectileMoveKindV1::Target.code());
    assert_eq!(s.casting_target, CastingTargetV1::EnemyChampion.code());
}

#[test]
fn the_comets_hit_bursts_with_his_numbers() {
    let mut w = world();
    live(&mut w, KOG, 5);
    fall(&mut w, KOG);
    w.sim(|sim| BurstFx.apply(sim, 0, KOG, InputTargetV1::target(GAREN)));
    assert_eq!(true_damage(&w, GAREN), vec![(w.tick, KOG, 186)]);
    assert_eq!(true_damage(&w, MINION).len(), 1);
    assert_eq!(w.viewed(BOOM), 1);
}

#[test]
fn a_form_gone_before_its_burst_bursts_where_it_stood() {
    let mut w = world();
    live(&mut w, KOG, 5);
    fall(&mut w, KOG);
    wake_at(&mut w, KOG, (334_000.0, 300_000.0));
    let id = forms(&w)[0];
    tick(&mut w);
    // taken off the field by something the add-on does not know of, 25000 short of Garen
    w.units[id].valid = false;
    tick(&mut w);
    assert_eq!(true_damage(&w, MINION).len(), 1, "the minion 20000 off the spot: within the burst");
    assert!(true_damage(&w, GAREN).is_empty(), "Garen 25000 off: out of it");
    assert_eq!(w.viewed(VOID_VIEW), 1);
    assert!(w.banishes.iter().all(|b| b.2 != id), "nothing to banish");
}

#[test]
fn both_kogmaws_burst_on_the_other_team() {
    let mut w = world();
    // the red Kog'Maw #7 beside Garen; Ahri (blue) 50000 west of him
    let mut red = champion("league_kogmaw", 1, 370_000.0, 320_000.0);
    red.stat.attack = 200;
    w.units.push(red);
    w.players.push(MPlayer { team: 1, champion: 7, ..Default::default() });
    w.units[AHRI].x = 320_000.0;
    w.units[AHRI].y = 320_000.0;
    let mut blue = LifeWatch::default();
    let mut redp = LifeWatch::default();
    w.sim(|sim| blue.on_spawn(sim, 0, KOG));
    w.sim(|sim| redp.on_spawn(sim, 4, 7));
    for _ in 0..5 {
        w.sim(|sim| blue.on_update(sim, 0, 0, KOG));
        w.sim(|sim| redp.on_update(sim, 0, 4, 7));
        tick(&mut w);
    }
    fall(&mut w, KOG);
    fall(&mut w, 7);
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    wake_at(&mut w, 7, (370_000.0, 320_000.0));
    let ids = forms(&w);
    assert_eq!(ids.len(), 2);
    assert_eq!((w.units[ids[0]].team, w.units[ids[1]].team), (0, 1));
    for _ in 0..120 {
        tick(&mut w);
    }
    // blue's form at Garen (186 each), red's at Ahri (80 + 200 = 280); neither form hurts its own side or the other form
    assert_eq!(true_damage(&w, GAREN).iter().map(|d| (d.1, d.2)).collect::<Vec<_>>(), vec![(KOG, 186)]);
    assert_eq!(true_damage(&w, AHRI).iter().map(|d| (d.1, d.2)).collect::<Vec<_>>(), vec![(7, 280)]);
    for id in &ids {
        assert!(true_damage(&w, *id).is_empty(), "a void form is no one's target");
    }
    assert_eq!(w.viewed(VOID_VIEW), 2);
}

#[test]
fn two_twins_of_one_match_keep_their_own_forms() {
    // the server runs two presims of one set side by side: same seed, same origin, same entity ids
    let (mut a, mut b) = (world(), world());
    live(&mut a, KOG, 5);
    live(&mut b, KOG, 5);
    let (na, nb) = (a.sim(|sim| sim_no(sim, false)), b.sim(|sim| sim_no(sim, false)));
    assert!(na != 0 && nb != 0 && na != nb, "each twin its own number: {na} {nb}");
    // the twins part: in b Garen stands further off
    b.units[GAREN].x = 380_000.0;
    b.units[MINION].x = 374_000.0;
    fall(&mut a, KOG);
    fall(&mut b, KOG);
    wake_at(&mut a, KOG, (300_000.0, 300_000.0));
    wake_at(&mut b, KOG, (300_000.0, 300_000.0));
    let (ia, ib) = (forms(&a)[0], forms(&b)[0]);
    assert_eq!(ia, ib, "the same entity id in both");
    let (mut ta, mut tb) = (None, None);
    for _ in 0..80 {
        tick(&mut a);
        tick(&mut b);
        ta = ta.or(a.banishes.iter().find(|x| x.2 == ia).map(|x| x.0));
        tb = tb.or(b.banishes.iter().find(|x| x.2 == ib).map(|x| x.0));
    }
    let (ta, tb) = (ta.expect("a"), tb.expect("b"));
    assert!((19..=21).contains(&(tb - ta)), "b's Garen 20000 further: 20 ticks later, not {}", tb - ta);
    // every move in a twin is a pace of that twin's own form (none stepped twice a tick, none left behind)
    for w in [&a, &b] {
        let mut moves: Vec<usize> = w.moves.iter().filter(|m| m.1 == ia).map(|m| m.0).collect();
        let n = moves.len();
        moves.dedup();
        assert_eq!(moves.len(), n, "one move a tick");
    }
    assert_eq!(true_damage(&a, GAREN).len(), 1);
    assert_eq!(true_damage(&b, GAREN).len(), 1);
}

#[test]
fn one_death_wakes_one_form() {
    let mut w = world();
    live(&mut w, KOG, 5);
    fall(&mut w, KOG);
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    for _ in 0..5 {
        tick(&mut w);
    }
    // a second watch lob in the air lands 6 ticks after the first
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    assert_eq!(forms(&w).len(), 1);
    // ... but a death long after is another
    for _ in 0..WAKE_GAP + 300 {
        tick(&mut w);
    }
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    assert_eq!(forms(&w).len(), 2);
}

#[test]
fn a_revive_lying_untargetable_wakes_a_form_from_his_body() {
    let mut w = world();
    live(&mut w, KOG, 5);
    // a guardian angel: he lies untargetable, his entity still there (the watch's lob finds no one)
    w.units[KOG].targetable = false;
    w.units[KOG].stat.attack = 150;
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    let id = forms(&w)[0];
    until_burst(&mut w, id, 100).expect("no burst");
    assert_eq!(true_damage(&w, GAREN), vec![(true_damage(&w, GAREN)[0].0, KOG, 230)], "his attack read off his body: 80 + 150");
}

#[test]
fn a_kogmaw_never_noted_wakes_nothing() {
    let mut w = world();
    live(&mut w, KOG, 5);
    // #9: no entity, never noted in this simulation (not a Kog'Maw of this match)
    wake_at(&mut w, 9, (300_000.0, 300_000.0));
    assert!(w.spawns.is_empty());
    for _ in 0..10 {
        tick(&mut w);
    }
    assert!(w.damage.iter().all(|d| d.4 != DamageTypeV1::Fixed.code()));
}

#[test]
fn the_log_tells_the_whole_chase() {
    let mut w = world();
    live(&mut w, KOG, 5);
    fall(&mut w, KOG);
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    let id = forms(&w)[0];
    until_burst(&mut w, id, 100).expect("no burst");
    let text = std::fs::read_to_string(log_file()).expect("the log");
    let mine: Vec<&str> = text.lines().filter(|l| l.contains(&format!("#{id} VOID")) || l.contains("#0 VOID SPAWN")).collect();
    let has = |what: &str| mine.iter().any(|l| l.contains(what));
    for what in [
        "VOID SPAWN #", "of Kog'Maw #0 (his entity gone, team 0) woke at (300000,300000): unit #", "his own id",
        "'league_kogmaw_void' for 243 ticks, attack 0 ap 0 hp 950 def 20 mr 15 speed 1", "his attack 106", "the burst 186 true damage",
        "VOID LOOK #", "reads back as name 'league_kogmaw_void' kind summon team 0", "its guard (no damage, undying, through walls) is on it",
        "VOID STEP #", "chasing league_garen#1", "it bursts within 22000",
        "VOID BURST #", "REACHED league_garen#1 after", "from where he fell (walked", "2 hit for 186 true damage each (his): league_garen#1, melee_minion#6",
        "the burst picture played", "the form banished for its last",
    ] {
        assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
    }
    assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
}

#[test]
fn a_fallen_body_that_still_reads_is_not_trusted_for_his_attack() {
    let mut w = world();
    live(&mut w, KOG, 5);
    // the SDK keeps a corpse readable; what he wore may be gone from it
    let tick = w.tick;
    (w.units[KOG].hp, w.units[KOG].died, w.units[KOG].stat.attack) = (0, Some(tick), 0);
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    let id = forms(&w)[0];
    until_burst(&mut w, id, 100).expect("no burst");
    assert_eq!(true_damage(&w, GAREN).iter().map(|d| d.2).collect::<Vec<_>>(), vec![186], "his noted 106, not the body's 0");
}

/// The mock's own slot table but for `entity_set_pos` (refused: the slot is gone) and an `entity_set_base_stat` that takes
/// the unit's new stat block - a host that will not teleport a unit.
unsafe extern "C" fn take_base_stat(s: *mut std::ffi::c_void, h: EntityHandleV1, stat: *const StatV1) -> bool {
    let w = &mut *(s as *mut World);
    match h.id().and_then(|i| w.units.get_mut(i)) {
        Some(u) if u.valid => {
            u.stat = *stat;
            true
        }
        _ => false,
    }
}

fn tick_without_set_pos(w: &mut World) {
    w.ctx(|ctx| unsafe {
        let mut vt: SimVtableV1 = std::ptr::read((*ctx).sim);
        vt.entity_set_pos = None;
        vt.entity_set_base_stat = Some(take_base_stat);
        let mut c2 = SimCtxV1 { size: std::mem::size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(), state: (*ctx).state };
        let mut sim = StableSim::from_raw(&mut c2).expect("a simulation context");
        step_forms(&mut sim);
    });
    w.step();
}

#[test]
fn a_host_that_will_not_teleport_a_unit_lets_the_engine_walk_it() {
    let mut w = world();
    live(&mut w, KOG, 5);
    fall(&mut w, KOG);
    let t0 = w.tick;
    wake_at(&mut w, KOG, (300_000.0, 300_000.0));
    let id = forms(&w)[0];
    for _ in 0..80 {
        if w.banishes.iter().any(|b| b.2 == id) {
            break;
        }
        tick_without_set_pos(&mut w);
    }
    assert_eq!(w.units[id].stat.move_speed, P_SPEED, "its pace given to the engine");
    assert!(w.moves.iter().all(|m| m.1 != id), "never teleported");
    let at = w.banishes.iter().find(|b| b.2 == id).expect("no burst").0;
    // the mock's engine walks it at the nearest foe (Garen) 1000 a tick from the look on: the same 38 paces
    assert!((t0 + 36..=t0 + 40).contains(&at), "burst {} ticks after the wake", at - t0);
    assert_eq!(true_damage(&w, GAREN).iter().map(|d| d.2).collect::<Vec<_>>(), vec![186]);
    let text = std::fs::read_to_string(log_file()).expect("the log");
    assert!(text.contains(&format!("#{id} VOID WALK #")) && text.contains("the engine walks it"), "no VOID WALK line");
}
