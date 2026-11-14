//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间
//! 就没）里放一次唤醒和一次海屿悼词：按名字取到注册的被动和两个原生效果，被动每 tick 调一次，排队的效果到点从注册表里取出来
//! 调。检查这条线接得上：副本的数据挂的 `K_ASK` → 被动排 `:walkers` → 三次 `spawn_unit` → 约里克身上有 `K_UNIT`（副本的数据在
//! 这一铲落地时读它）→ 雾行者到时间；`M_ASK` → `:maiden` → 室女和两只雾行者、`M_UNIT`；日志开头两行写着版本、单位开没开、
//! 读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_yorick::{K_ASK, K_UNIT, MAID_LIFE, MAIDEN_UNIT, M_ASK, M_UNIT, Q_HIT, R_N, R_REL, WALKER, WALK_LIFE};
use mod_api_stable::*;

#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

use mock::{champion, MPlayer, World};

unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

type Effects<'a> = HashMap<String, &'a NativeEffectRegV1>;

/// One tick: the queued effects due (from the registry), the passive, the world's own step.
unsafe fn tick(w: &mut World, fx: &Effects, passive: &PassiveRegV1) {
    for (name, caster, input) in w.due() {
        let e = fx.get(&name).unwrap_or_else(|| panic!("effect {name} is not registered")).effect;
        w.ctx(|ctx| ((*e.vtable).apply.unwrap())(e.userdata, ctx, 0, caster, &input));
    }
    if w.units[0].hp > 0 {
        w.ctx(|ctx| ((*passive.vtable).on_update.unwrap())(passive.userdata, ctx, 0, 0, 0));
    }
    w.step();
}

#[test]
fn the_awakening_and_the_ult_spawn_units() {
    let log = std::env::temp_dir().join(format!("league_yorick_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_YORICK_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_yorick::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_yorick:shepherd"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        for name in ["walkers", "maiden"] {
            assert!(fx.contains_key(&format!("league_yorick:{name}")), "{name} not registered");
        }
        assert_eq!(fx.len(), 2);
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let params = r#"{"g_t":1800,"r_pct":3}"#;
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, params.as_ptr(), params.len());

        // Yorick #0, Garen #1 40000 east of him, Darius #2 far off (the field round them all)
        let mut w = World::default();
        w.units = vec![champion("league_yorick", 0, 300_000.0, 300_000.0), champion("league_garen", 1, 340_000.0, 300_000.0),
                       champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        w.units[1].hp = 5_000;
        w.units[1].max = 5_000;
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        // the copy's Awakening: the ask on Garen
        w.units[1].buffs.push((BuffV1::timed(K_ASK, 3), 3));
        let t0 = w.tick;
        for _ in 0..=Q_HIT {
            tick(&mut w, &fx, &passive);
        }
        let walkers: Vec<usize> = w.spawns.iter().filter(|s| s.name == WALKER).filter_map(|s| s.gave).collect();
        assert_eq!(walkers.len(), 3);
        assert!(w.spawns.iter().all(|s| s.life as usize == WALK_LIFE && s.tick <= t0 + 3));
        assert!(w.has(0, K_UNIT), "no flag on him when the blow lands: the data's walkers would ride too");
        // the copy's R a while later: the ask on Garen
        for _ in 0..60 {
            tick(&mut w, &fx, &passive);
        }
        w.units[1].buffs.push((BuffV1::timed(M_ASK, 3), 3));
        for _ in 0..=R_REL {
            tick(&mut w, &fx, &passive);
        }
        assert_eq!(w.spawns.iter().filter(|s| s.name == MAIDEN_UNIT).count(), 1);
        assert_eq!(w.spawns.iter().filter(|s| s.name == WALKER).count(), 3 + R_N);
        assert!(w.spawns.iter().filter(|s| s.name == MAIDEN_UNIT).all(|s| s.life as usize == MAID_LIFE));
        assert!(w.has(0, M_UNIT), "no flag on him when the Maiden rises: the data's would ride too");
        // their whole time
        for _ in 0..MAID_LIFE + 200 {
            tick(&mut w, &fx, &passive);
        }
        assert!(walkers.iter().all(|id| !w.units[*id].valid || w.units[*id].died.is_some()));
        assert!(w.damage.iter().any(|d| walkers.contains(&d.1) && d.2 == 1), "no walker bit Garen");
        assert!(w.queue.is_empty());
        w.ctx(|ctx| ((*passive.vtable).on_dead.unwrap())(passive.userdata, ctx, 0));
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_yorick v{} (graves from kills", env!("CARGO_PKG_VERSION"))), "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("UNITS: the Mist Walkers ('league_yorick_walker') and the Maiden of the Mist ('league_yorick_maiden') \
                                    are units (spawn_unit) - ON; the Awakening 3 walkers for 600 ticks"), "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["SPAWN: the add-on's Yorick (player 0", "WALKERS ASK #1", "WALKERS SPAWN #1 (the queued effect): 3 of 3 units",
                     "WALKER #1 LOOK #1 (the Awakening's)", "MAIDEN ASK #1", "MAIDEN SPAWN #1 (the queued effect)",
                     "MAIDEN #1 LOOK #1", "MAIDEN #1 DRESS #1", "WALKER #4 LOOK #4 (the Maiden's escort)", "WALKER #1 OVER #1 (the \
                     Awakening's): TIMED OUT", "MAIDEN #1 OVER #1: TIMED OUT", "WALKER #1 WAKE #"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
        assert!(text.contains(&format!("t={t0} #0 WALKERS ASK")));
    }
}
