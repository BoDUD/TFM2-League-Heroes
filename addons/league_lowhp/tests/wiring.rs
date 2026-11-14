//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间就没）
//! 里放一次乐芙兰的镜花水月：按名字取到注册的被动和原生效果，被动每 tick 调一次，排队的效果到点从注册表里取出来调。检查这条线
//! 接得上：被动挂着 `P_UNIT`（副本的数据看到它就不放画面）→ 数据挂上 40 秒的冷却 → 被动排 `:mirror` → `spawn_unit`（名字、
//! 位置、属性）→ 到时间结束；日志开头两行写着版本、幻像是不是单位、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_lowhp::mirror::{M_LIFE, P_CD, P_UNIT, P_VIEW};
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
fn mirror_image_spawns_its_clone_as_a_unit_through_the_export() {
    let log = std::env::temp_dir().join(format!("league_lowhp_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_LOWHP_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_lowhp::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(),
                   ["league_lowhp:blitzcrank", "league_lowhp:leblanc", "league_lowhp:lissandra"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        assert_eq!(fx.keys().map(|k| k.as_str()).collect::<Vec<_>>(), ["league_lowhp:mirror"]);
        let proto = &passives[1].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };

        // LeBlanc #0 at 300 of 1000 health, Garen #1 30000 east of her
        let mut w = World::default();
        let mut lb = champion("league_leblanc", 0, 300_000.0, 300_000.0);
        (lb.hp, lb.max) = (300, 1000);
        w.units = vec![lb, champion("league_garen", 1, 330_000.0, 300_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        for _ in 0..5 {
            tick(&mut w, &fx, &passive);
        }
        // the passive holds both flags: low health (the data's trigger) and the unit's (the data leaves its picture out)
        assert!(w.has(0, "league_leblanc_low") && w.has(0, P_UNIT));
        // the copy's Mirror Image: its 40 s cooldown, the dash back
        w.units[0].buffs.push((BuffV1::timed(P_CD, 2400), 2400));
        w.units[0].x -= 6_000.0;
        for _ in 0..4 {
            tick(&mut w, &fx, &passive);
        }
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life as usize, s.at), ("league_leblanc", 0, 0, M_LIFE, (300_000, 300_000)));
        let clone = s.gave.unwrap();
        assert_eq!(w.units[clone].hp, 300, "the clone does not have her health");
        for _ in 0..M_LIFE + 20 {
            tick(&mut w, &fx, &passive);
        }
        assert!(!w.units[clone].valid, "the clone outlived its time");
        assert!(w.damage.iter().filter(|d| d.1 == clone).all(|d| d.3 == 0), "the clone dealt damage");
        assert_eq!(w.viewed(P_VIEW), 0, "the picture played beside the unit");
        assert!(w.queue.is_empty());
        w.ctx(|ctx| ((*passive.vtable).on_dead.unwrap())(passive.userdata, ctx, 0));
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_lowhp v{} (Blitzcrank's Mana Barrier, LeBlanc's Mirror Image", env!("CARGO_PKG_VERSION"))),
                "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("MIRROR: Mirror Image's clone is a unit ('league_leblanc', spawn_unit) - ON; 320 ticks, no damage, \
                                    her health then. Test knobs ("), "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["MIRROR ASK #", "MIRROR SPAWN #", "MIRROR #1 LOOK #", "MIRROR #1 DRESS #", "MIRROR #1 OVER #", "TIMED OUT after",
                     "MIRROR #1 WAKE #"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}
