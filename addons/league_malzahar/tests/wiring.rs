//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间
//! 就没）里放一次 E：按名字取到注册的被动和两个原生效果，被动每 tick 调一次，排队的效果到点从注册表里取出来调。检查这条线
//! 接得上：副本的数据挂的 `V_ASK` → 被动排 `:voidlings` → 两次 `spawn_unit` → 玛尔扎哈身上有 `V_UNIT`（副本的数据在幻象打中时
//! 读它）→ 虚空蜂咬人、到时间；日志开头两行写着版本、虚空蜂开没开、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_malzahar::{E_LAG, VOIDLING, VOID_LIFE, V_ASK, V_UNIT};
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
fn e_spawns_two_voidlings() {
    let log = std::env::temp_dir().join(format!("league_malzahar_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_MALZAHAR_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_malzahar::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_malzahar:void"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        for name in ["vision", "voidlings"] {
            assert!(fx.contains_key(&format!("league_malzahar:{name}")), "{name} not registered");
        }
        assert_eq!(fx.len(), 2);
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let params = r#"{"e_ap":80,"e_dmg":170,"e_jump":40000,"e_p":15,"e_t":240,"p_cd":720,"p_dr":90,"p_linger":15}"#;
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, params.as_ptr(), params.len());

        // Malzahar #0, Garen #1 40000 east of him; two more far off (the field round them all)
        let mut w = World::default();
        w.units = vec![champion("league_malzahar", 0, 300_000.0, 300_000.0), champion("league_garen", 1, 340_000.0, 300_000.0),
                       champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        (w.units[1].hp, w.units[1].max) = (5_000, 5_000);
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        // the copy's E: the ask on Garen
        w.units[1].buffs.push((BuffV1::timed(V_ASK, 3), 3));
        let t0 = w.tick;
        for _ in 0..=E_LAG {
            tick(&mut w, &fx, &passive);
        }
        let ids: Vec<usize> = w.spawns.iter().filter(|s| s.name == VOIDLING).filter_map(|s| s.gave).collect();
        assert_eq!(ids.len(), 2);
        assert!(w.spawns.iter().all(|s| s.life as usize == VOID_LIFE && s.tick <= t0 + 3));
        assert!(w.has(0, V_UNIT), "no flag on him when the vision lands: the data's swarm would bite too");
        for _ in 0..VOID_LIFE + 200 {
            tick(&mut w, &fx, &passive);
        }
        assert!(ids.iter().all(|id| !w.units[*id].valid || w.units[*id].died.is_some()));
        assert!(w.damage.iter().any(|d| ids.contains(&d.1) && d.2 == 1), "no voidling bit Garen");
        assert!(w.queue.is_empty());
        w.ctx(|ctx| ((*passive.vtable).on_dead.unwrap())(passive.userdata, ctx, 0));
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_malzahar v{} (Malzahar: Void Shift as in League", env!("CARGO_PKG_VERSION"))),
                "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("VOIDLINGS: Void Swarm's voidlings are units ('league_malzahar_voidling', spawn_unit) - ON; 2 an E for \
                                    480 ticks, 14 + 8% of his ability power a bite every 60 ticks"), "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["VOIDLINGS ASK #1", "VOIDLINGS SPAWN #1 (the queued effect): 2 of 2 units", "VOIDLING #1 LOOK #1",
                     "VOIDLING #1 OVER #1: TIMED OUT", "VOIDLING #1 WAKE #"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
        assert!(text.contains(&format!("t={t0} #0 VOIDLINGS ASK")));
    }
}
