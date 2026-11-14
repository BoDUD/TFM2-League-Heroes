//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间
//! 就没）里长一株植物：按名字取到注册的被动和原生效果，被动每 tick 调一次，排队的效果到点从注册表里取出来调。检查这条线接得上：
//! 计时掉下的种子 + 副本的 Q 挂在目标身上的 `q_aim` → 种子长成荆棘喷射者 → 被动排 `:spitter` → 一次 `spawn_unit`（身体：移速 1、
//! 攻击 0）→ 婕拉身上有 `P_UNIT`（副本的数据在 Q、E 落点读它）→ 本包照旧吐刺、魔法伤害打在目标身上；日志开头两行写着版本、
//! 身体开没开、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_zyra::{P_UNIT, SPITTER};
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
fn a_plant_grown_on_a_seed_gets_a_body() {
    let log = std::env::temp_dir().join(format!("league_zyra_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_ZYRA_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_zyra::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_zyra:garden"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        for name in ["noop", "spitter", "lasher"] {
            assert!(fx.contains_key(&format!("league_zyra:{name}")), "{name} not registered");
        }
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let params = r#"{"s_cd":600,"s_life":1800,"t_life":300,"t_per":60}"#;
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, params.as_ptr(), params.len());

        // Zyra #0, Garen #1 40000 east of her, Darius #2 far off (the field round them all)
        let mut w = World::default();
        w.units = vec![champion("league_zyra", 0, 300_000.0, 300_000.0), champion("league_garen", 1, 340_000.0, 300_000.0),
                       champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        w.units[1].hp = 50_000;
        w.units[1].max = 50_000;
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        // the timer's seed (600 ticks), halfway to Garen
        for _ in 0..602 {
            tick(&mut w, &fx, &passive);
        }
        assert!(w.spawns.is_empty());
        // the copy's Q at Garen: the mark where it lands, within reach of the seed
        w.units[1].buffs.push((BuffV1::timed("league_zyra_q_aim", 2), 2));
        for _ in 0..4 {
            tick(&mut w, &fx, &passive);
        }
        let bodies: Vec<usize> = w.spawns.iter().filter(|s| s.name == SPITTER).filter_map(|s| s.gave).collect();
        assert_eq!(bodies.len(), 1);
        assert_eq!(w.spawns[0].stat.move_speed, 1);
        assert!(w.has(0, P_UNIT), "no flag on her: the data would grow its own plants where Q and E land");
        for _ in 0..100 {
            tick(&mut w, &fx, &passive);
        }
        assert!(w.damage.iter().any(|d| d.1 == 0 && d.2 == 1 && d.4 == DamageTypeV1::Ap.code()), "no spit of hers reached Garen");
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_zyra v{} (Zyra's seeds on the ground", env!("CARGO_PKG_VERSION"))), "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("PLANTS: her plants have bodies of their own ('league_zyra_spitter' / 'league_zyra_lasher', \
                                    spawn_unit"), "{second}");
        assert!(second.contains(" - ON;") && second.ends_with(".cfg): none"), "{second}");
        for what in ["SEED #1 (timer)", "GROW #1: a Spitter on a seed", "its body asked for", "PLANT SPAWN #1: a Spitter's body",
                     "PLANT #1 LOOK #1", "PLANT UNITS ON #1", "STRIKE #1: Spitter -> #1 (champion)"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}
