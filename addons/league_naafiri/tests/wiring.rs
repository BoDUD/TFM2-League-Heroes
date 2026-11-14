//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间
//! 就没）里让纳亚菲利出生：按名字取到注册的被动和原生效果，被动每 tick 调一次，排队的效果到点从注册表里取出来调。检查这条线
//! 接得上：出生 → 被动排两次 `:hound` → 两只伙伴单位 → 她身上有 `SOLO`（副本的数据读它，显示钩子换成 solo_*）→ 暴吼时再来
//! 两只（`:call`）→ 她阵亡时伙伴被放逐；日志开头写着版本、伙伴开没开、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_naafiri::{CALL_N, HOUND_LIFE, PACK4, PACKMATE, PACK_N, ROAR_T, SOLO};
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
fn her_packmates_are_units() {
    let log = std::env::temp_dir().join(format!("league_naafiri_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_NAAFIRI_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_naafiri::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_naafiri:pack"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        for name in ["q2", "hound", "call"] {
            assert!(fx.contains_key(&format!("league_naafiri:{name}")), "{name} not registered");
        }
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let params = r#"{"q2_dmg":35,"q2_ratio":55,"q_exec":100,"r_recast":720,"r_win":420}"#;
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, params.as_ptr(), params.len());

        // Naafiri #0, Garen #1 60000 east of her; two more far off (the field round them all)
        let mut w = World::default();
        w.units = vec![champion("league_naafiri", 0, 300_000.0, 300_000.0), champion("league_garen", 1, 360_000.0, 300_000.0),
                       champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        (w.units[1].hp, w.units[1].max) = (50_000, 50_000);
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        for _ in 0..5 {
            tick(&mut w, &fx, &passive);
        }
        let pack: Vec<usize> = w.spawns.iter().filter(|s| s.name == PACKMATE).filter_map(|s| s.gave).collect();
        assert_eq!(pack.len(), PACK_N);
        assert!(w.spawns.iter().all(|s| s.life as usize == HOUND_LIFE));
        assert!(w.has(0, SOLO), "no SOLO on her: the drawn pack would show and bite beside the units");
        // the roar
        w.units[0].buffs.push((BuffV1::timed(PACK4, ROAR_T), ROAR_T));
        for _ in 0..5 {
            tick(&mut w, &fx, &passive);
        }
        assert_eq!(w.spawns.iter().filter(|s| s.life as usize == ROAR_T).count(), CALL_N);
        for _ in 0..200 {
            tick(&mut w, &fx, &passive);
        }
        assert!(w.damage.iter().any(|d| pack.contains(&d.1) && d.2 == 1), "no packmate bit Garen");
        // she dies: her packmates go with her
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.ctx(|ctx| ((*passive.vtable).on_dead.unwrap())(passive.userdata, ctx, 0));
        assert_eq!(w.banishes.len(), PACK_N + CALL_N);
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_naafiri v{} (Naafiri: the second dagger's execute", env!("CARGO_PKG_VERSION"))),
                "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("HOUNDS: her packmates are units ('league_naafiri_packmate', spawn_unit) - ON; 2 for 3600 ticks"),
                "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["HOUND ASK #1", "HOUND SPAWN #1 (her pack, the queued effect)", "HOUND SOLO ON", "HOUND #1 LOOK #1 (her pack)",
                     "(the call, the queued effect)", "HOUND BANISH #1: Naafiri died"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}
