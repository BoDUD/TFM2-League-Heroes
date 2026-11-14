//! 走真实的导出入口，在测试用的小世界（`src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间就没）里放一次
//! 萨科的 R：按名字取到注册的被动和四个原生效果，被动每 tick 调一次，排队的效果到点从注册表里取出来调。检查这条线接得上：
//! 副本的数据挂的 `R_ASK` → 被动排 `:clone` → `spawn_unit` → 萨科身上有 `R_UNIT`（副本的数据在第 12 tick 读它）→ 幻像到时间
//! → `:burst` 一次、`:box` 五次；日志开头两行写着版本、幻像是不是单位、读到的测试开关。

use std::collections::HashMap;

use std::mem::{size_of, zeroed};

use league_shaco_backstab::{box_damage, boom_damage, BOX_SHOTS, CLONE_BUFF, CLONE_LIFE, R_ASK, R_UNIT};
use mod_api_stable::*;

#[path = "../src/summon_mock.rs"]
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
fn hallucinate_spawns_a_unit_and_bursts_it() {
    let log = std::env::temp_dir().join(format!("league_shaco_backstab_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_SHACO_BACKSTAB_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_shaco_backstab::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_shaco_backstab:backstab"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        for name in ["clone", "burst", "box", "end"] {
            assert!(fx.contains_key(&format!("league_shaco_backstab:{name}")), "{name} not registered");
        }
        assert_eq!(fx.len(), 7); // the clone's four; from 0.3.0 Jack in the Box's :jack and :jack_shot; from 0.3.1 the shiv's :shiv
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let params = r#"{"ad":25,"base":15}"#;
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, params.as_ptr(), params.len());

        // Shaco #0 walks right for half a second, Garen #1 stands 50000 east of where he stops
        let mut w = World::default();
        w.units = vec![champion("league_shaco", 0, 267_000.0, 300_000.0), champion("league_garen", 1, 350_000.0, 300_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        for _ in 0..30 {
            w.units[0].x += 1_100.0;
            tick(&mut w, &fx, &passive);
        }
        // the copy's R: the ask on him
        w.units[0].buffs.push((BuffV1::timed(R_ASK, 3), 3));
        let t0 = w.tick;
        for _ in 0..12 {
            tick(&mut w, &fx, &passive);
        }
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life as usize), ("league_shaco", 0, 0, CLONE_LIFE));
        let clone = s.gave.unwrap();
        assert!(w.has(0, R_UNIT), "no flag on him 12 ticks after the cast: the data's clone would play too");
        assert!(w.has(clone, CLONE_BUFF));
        // its whole time and the boxes' shots after it
        for _ in 0..CLONE_LIFE + 140 {
            tick(&mut w, &fx, &passive);
        }
        let magic = w.dealt(0, DamageTypeV1::Ap);
        assert_eq!(magic.iter().filter(|d| **d == (1, boom_damage(30))).count(), 1, "{magic:?}");
        assert_eq!(magic.iter().filter(|d| **d == (1, box_damage(30))).count(), BOX_SHOTS, "{magic:?}");
        assert!(w.queue.is_empty());
        assert!(w.damage.iter().any(|d| d.1 == clone && d.2 == 1), "the clone never hit Garen");
        // his death is told through the export too: nothing is out, nothing is queued
        w.ctx(|ctx| ((*passive.vtable).on_dead.unwrap())(passive.userdata, ctx, 0));
        assert!(w.queue.is_empty());
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_shaco_backstab v{} (Shaco's Backstab from behind", env!("CARGO_PKG_VERSION"))),
                "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("CLONE: Hallucinate's clone is a unit ('league_shaco', spawn_unit) - ON; 312 ticks, 10 + 40% of \
                                    his attack a hit, +50% damage taken, the blast 150 + 100% of his ability power. Test knobs ("),
                "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["SPAWN: the add-on's Shaco (player 0), [(\"ad\", 25), (\"base\", 15)]", "CLONE ASK #1", "CLONE SPAWN #1 (the queued effect)",
                     "CLONE #1 LOOK #1", "CLONE #1 DRESS #1", "CLONE #1 OVER #1: TIMED OUT", "CLONE BURST #1", "CLONE BOX #5",
                     "CLONE #1 WAKE #1"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
        assert!(t0 >= 1030 && text.contains(&format!("t={t0} #0 CLONE ASK")));
    }
}
