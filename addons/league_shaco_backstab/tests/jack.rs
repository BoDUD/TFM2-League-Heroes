//! 惊吓魔盒有了身体（0.3.0，src/jack.rs）在测试用的小世界（`src/summon_mock.rs`：假宿主）里：落地生成身体、弹开前放逐、标记撑过
//! 等待、弹开后按主包的节奏打 W_SHOTS 轮、身体被打掉就停、萨科先死了剩下的几轮排成效果接着打、宿主不给单位时不挂标记也不打。
//! 单独一个测试进程：日志写到它自己的临时文件，不碰幻像那边的测试日志。

use league_shaco_backstab::jack::*;
use league_shaco_backstab::summon;
use mod_api_stable::*;

#[path = "../src/summon_mock.rs"]
mod mock;

use mock::{champion, MPlayer, World};

fn log_once() {
    static SET: std::sync::Once = std::sync::Once::new();
    SET.call_once(|| {
        let path = std::env::temp_dir().join(format!("league_shaco_backstab_jack_{}.log", std::process::id()));
        std::env::set_var("LEAGUE_SHACO_BACKSTAB_LOG", &path);
        let _ = std::fs::remove_file(&path);
        let _ = std::fs::remove_file(path.with_extension("cfg"));
    });
}
const GAREN: usize = 1;

#[test]
fn the_box_is_built_from_his_numbers() {
    log_once();
    let his = StatV1 { attack: 100, magic_power: 80, hp: 1200, defence: 40, magic_resistance: 30, move_speed: 1100, hp_regen: 2,
                       stack: 0, crit_chance: 0 };
    let b = jack_spec(&his, 2000);
    assert_eq!((b.name.as_str(), b.life), (JACK, W_WAIT + W_TIME + 2));
    assert_eq!(b.stat, StatV1 { attack: 0, magic_power: 80, hp: 500, defence: 40, magic_resistance: 57, move_speed: 1, hp_regen: 0,
                                stack: 0, crit_chance: 0 });
    assert_eq!((b.attack.attack, b.attack.attack_ratio, b.attack.range, b.attack.cooltime), (0, 0, W_R, W_EVERY));
    assert_eq!((b.attack.duration, b.attack.start_timing), (JACK_ACT, JACK_LANDS));
    assert_eq!(volley_damage(80), 10 + 9);
    assert_eq!(W_SHOTS, (W_FIRST..W_TIME).step_by(W_EVERY).count());
    for name in [W_UNIT, &summon::handoff(W_UID, usize::MAX)] {
        assert!(name.starts_with("league_shaco_") && name.len() <= BUFF_NAME_CAP, "{name}");
    }
}

#[test]
fn the_copy_leaves_the_spring_to_the_body() {
    let copy = include_str!("../override/league_shaco.data_champion");
    assert_eq!(copy.matches(&format!("\"buff_name\": \"{W_UNIT}\"")).count(), 2, "the spring's picture and its shooting zone");
    assert_eq!(copy.matches("\"effect_ref\": \"league_shaco_backstab:jack\"").count(), 1);
}

/// Shaco #0 (team 0, 2000 health, 80 ability power) at (300000, 300000); Garen #1 20000 east of him; two more far off.
fn world() -> (World, Jacks) {
    log_once();
    let mut w = World::default();
    let mut shaco = champion("league_shaco", 0, 300_000.0, 300_000.0);
    (shaco.hp, shaco.max, shaco.stat.magic_power) = (2000, 2000, 80);
    let mut garen = champion("league_garen", 1, 320_000.0, 300_000.0);
    (garen.hp, garen.max) = (50_000, 50_000);
    w.units = vec![shaco, garen, champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
    w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() }];
    (w, Jacks::default())
}

fn tick(w: &mut World, j: &mut Jacks) {
    for (name, caster, input) in w.due() {
        w.sim(|sim| match name.as_str() {
            "league_shaco_backstab:jack_shot" => ShotFx.apply(sim, 0, caster, input),
            other => panic!("an effect nobody registered: {other}"),
        });
    }
    if w.units[0].hp > 0 {
        w.sim(|sim| j.tick(sim, 0, 0, 0, (300_000.0, 300_000.0)));
    }
    w.step();
}

fn land(w: &mut World) {
    let input = InputTargetV1::pos(318_000, 300_000);
    w.sim(|sim| JackFx.apply(sim, 0, 0, input));
}

fn boxes(w: &World) -> Vec<usize> {
    w.spawns.iter().filter(|s| s.name == JACK).filter_map(|s| s.gave).collect()
}

#[test]
fn the_box_lands_hidden_springs_and_fires_its_volleys() {
    let (mut w, mut j) = world();
    land(&mut w);
    let ids = boxes(&w);
    assert_eq!(ids.len(), 1);
    assert_eq!((w.spawns[0].at, w.spawns[0].stat.move_speed), ((318_000, 300_000), 1));
    assert!(w.has(0, W_UNIT), "no flag on him at the spring: the data's box would spring too");
    assert!(w.banishes.iter().any(|b| b.2 == ids[0] && b.3 == W_WAIT - 1), "not hidden until it springs");
    for _ in 0..W_WAIT {
        tick(&mut w, &mut j);
    }
    assert!(w.has(0, W_UNIT), "the flag must outlast the spring's wait");
    for _ in 0..W_TIME + 20 {
        tick(&mut w, &mut j);
    }
    // its volleys: his magic damage on Garen, W_SHOTS of them
    let v: Vec<_> = w.dealt(0, DamageTypeV1::Ap).into_iter().filter(|d| d.0 == GAREN).collect();
    assert_eq!(v.len(), W_SHOTS, "{v:?}");
    assert!(v.iter().all(|d| d.1 == volley_damage(80)));
    assert!(w.damage.iter().filter(|d| d.1 == ids[0]).all(|d| d.3 == 0), "the body's own shot harmed someone");
}

#[test]
fn a_broken_box_stops_and_a_dead_shaco_s_box_fires_on() {
    let (mut w, mut j) = world();
    land(&mut w);
    let ids = boxes(&w);
    for _ in 0..W_WAIT + 40 {
        tick(&mut w, &mut j);
    }
    let fired = w.dealt(0, DamageTypeV1::Ap).len();
    assert_eq!(fired, 2);
    w.hurt(ids[0], 1_000_000);
    for _ in 0..200 {
        tick(&mut w, &mut j);
    }
    assert_eq!(w.dealt(0, DamageTypeV1::Ap).len(), fired, "a broken box fired on");
    // a new box, then Shaco dies after its first volley: the rest are queued and fire for his dead self
    land(&mut w);
    for _ in 0..W_WAIT + 3 {
        tick(&mut w, &mut j);
    }
    let before = w.dealt(0, DamageTypeV1::Ap).len();
    (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
    w.sim(|sim| j.on_dead(sim, 0));
    assert_eq!(w.queue.len(), W_SHOTS - 1);
    for _ in 0..W_TIME + 10 {
        tick(&mut w, &mut j);
    }
    assert_eq!(w.dealt(0, DamageTypeV1::Ap).len(), before + W_SHOTS - 1);
}

#[test]
fn no_body_from_the_host_keeps_the_main_pack_s_box() {
    for case in 0..2 {
        let (mut w, mut j) = world();
        if case == 0 {
            w.has_spawn = false;
        } else {
            w.spawn_ok = false;
        }
        land(&mut w);
        assert!(!w.has(0, W_UNIT), "case {case}");
        for _ in 0..100 {
            tick(&mut w, &mut j);
        }
        assert!(w.dealt(0, DamageTypeV1::Ap).is_empty(), "case {case}: the add-on fired for a box it has no body of");
    }
    // an id that never reads as a unit: the flag goes again
    let (mut w, mut j) = world();
    w.spawn_never = true;
    land(&mut w);
    for _ in 0..8 {
        tick(&mut w, &mut j);
    }
    assert!(!w.has(0, W_UNIT));
}
