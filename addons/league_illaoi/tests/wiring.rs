//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间
//! 就没）里长一条触手：按名字取到注册的被动和原生效果，被动每 tick 调一次，排队的效果到点从注册表里取出来调。检查这条线接得上：
//! 被动的冷却到了 → 长一条（冒出来的画面）→ 排 `:tentacle` → 一次 `spawn_unit`（身体：移速 1、攻击够不着人）→ 冒出来的那几
//! tick 放逐着 → 接到这条触手上、不再放摆动的画面；日志开头两行写着版本、身体开没开、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_illaoi::{RISE_T, TENTACLE_BODY};
use mod_api_stable::*;

#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

use mock::{champion, MPlayer, World};

unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

type Effects<'a> = HashMap<String, &'a NativeEffectRegV1>;

unsafe fn tick(w: &mut World, fx: &Effects, passive: &PassiveRegV1) {
    for (name, caster, input) in w.due() {
        let e = fx.get(&name).unwrap_or_else(|| panic!("effect {name} is not registered")).effect;
        w.ctx(|ctx| ((*e.vtable).apply.unwrap())(e.userdata, ctx, 0, caster, &input));
    }
    w.ctx(|ctx| ((*passive.vtable).on_update.unwrap())(passive.userdata, ctx, 0, 0, 0));
    w.step();
}

#[test]
fn a_tentacle_grown_on_its_time_gets_a_body() {
    let log = std::env::temp_dir().join(format!("league_illaoi_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_ILLAOI_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_illaoi::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_illaoi:prophet"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        for name in ["noop", "tentacle"] {
            assert!(fx.contains_key(&format!("league_illaoi:{name}")), "{name} not registered");
        }
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let params = r#"{"p_cd_1":600,"p_cd_18":600}"#;
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, params.as_ptr(), params.len());

        // Illaoi #0, Garen #1 20000 east of her, Darius #2 far off (the field round them all)
        let mut w = World::default();
        w.units = vec![champion("league_illaoi", 0, 300_000.0, 300_000.0), champion("league_garen", 1, 320_000.0, 300_000.0),
                       champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        w.units[1].hp = 50_000;
        w.units[1].max = 50_000;
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        // half a cooldown: the first tentacle
        for _ in 0..310 {
            tick(&mut w, &fx, &passive);
        }
        let bodies: Vec<usize> = w.spawns.iter().filter(|s| s.name == TENTACLE_BODY).filter_map(|s| s.gave).collect();
        assert_eq!(bodies.len(), 1, "no body for the first tentacle");
        assert_eq!(w.spawns[0].stat.move_speed, 1);
        assert!(w.banishes.iter().any(|b| b.2 == bodies[0] && b.3 == RISE_T - 1), "not hidden while it rises");
        assert_eq!(w.views.iter().filter(|v| v.1 == "league_illaoi_tentacle_rise").count(), 1);
        for _ in 0..200 {
            tick(&mut w, &fx, &passive);
        }
        assert_eq!(w.views.iter().filter(|v| v.1 == "league_illaoi_tentacle_sway").count(), 0, "a sway picture over the body");
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_illaoi v{} (Illaoi: tentacles on the walls", env!("CARGO_PKG_VERSION"))), "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("TENTACLES: her tentacles have bodies of their own ('league_illaoi_tentacle_body', spawn_unit"),
                "{second}");
        assert!(second.contains(" - ON;") && second.ends_with(".cfg): none"), "{second}");
        for what in ["GROW #1 (its time)", "TENTACLE SPAWN #1: unit #4", "banished while it rises: yes", "TENTACLE #1 LOOK #1"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}
