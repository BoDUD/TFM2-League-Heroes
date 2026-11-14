//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间
//! 就没）里变一次蜘蛛：按名字取到注册的被动和原生效果，被动每 tick 调一次，排队的效果到点从注册表里取出来调。检查这条线接得上：
//! 主包的小蜘蛛计数（两只）+ 蜘蛛形态 → 被动排两次 `:spiderling` → 两次 `spawn_unit` → 伊莉丝身上有 `SL_UNIT`（副本的数据在
//! 蜘蛛普攻打中时读它）→ 小蜘蛛咬人 → 变回人形时放逐、`SL_UNIT` 去掉；日志开头两行写着版本、单位开没开、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_elise::{FORM, SL_FLAGS, SL_LIFE, SL_UNIT, SPIDERLING};
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
fn spider_form_spawns_her_spiderlings_and_human_form_puts_them_away() {
    let log = std::env::temp_dir().join(format!("league_elise_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_ELISE_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_elise::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_elise:queen"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        assert_eq!(fx.keys().map(|k| k.as_str()).collect::<Vec<_>>(), ["league_elise:spiderling"]);
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let params = r#"{"ce_r":50000,"e_range":75000,"e_w":2500,"r_range":75000}"#;
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, params.as_ptr(), params.len());

        // Elise #0 with two stored spiderlings, Garen #1 30000 east of her, Darius #2 far off (the field round them all)
        let mut w = World::default();
        w.units = vec![champion("league_elise", 0, 300_000.0, 300_000.0), champion("league_garen", 1, 330_000.0, 300_000.0),
                       champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        w.units[1].hp = 5_000;
        w.units[1].max = 5_000;
        w.units[0].buffs = vec![(BuffV1::named(SL_FLAGS[0]), usize::MAX), (BuffV1::named(SL_FLAGS[1]), usize::MAX)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        for _ in 0..10 {
            tick(&mut w, &fx, &passive);
        }
        assert!(w.spawns.is_empty(), "human: no spiderling");
        // the data turns her into the spider
        w.units[0].buffs.push((BuffV1::named(FORM), usize::MAX));
        let t0 = w.tick;
        for _ in 0..4 {
            tick(&mut w, &fx, &passive);
        }
        let lings: Vec<usize> = w.spawns.iter().filter(|s| s.name == SPIDERLING).filter_map(|s| s.gave).collect();
        assert_eq!(lings.len(), 2);
        assert!(w.spawns.iter().all(|s| s.life as usize == SL_LIFE && s.tick <= t0 + 2));
        assert!(w.has(0, SL_UNIT), "no flag on her: the data's riding bites would play too");
        for _ in 0..200 {
            tick(&mut w, &fx, &passive);
        }
        assert!(w.damage.iter().any(|d| lings.contains(&d.1) && d.2 == 1), "no spiderling bit Garen");
        // Human Form
        w.units[0].buffs.retain(|b| b.0.name() != FORM);
        for _ in 0..3 {
            tick(&mut w, &fx, &passive);
        }
        assert_eq!(w.banishes.len(), 2);
        assert!(!w.has(0, SL_UNIT));
        w.ctx(|ctx| ((*passive.vtable).on_dead.unwrap())(passive.userdata, ctx, 0));
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_elise v{} (Elise: the whole-body spider", env!("CARGO_PKG_VERSION"))), "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("SPIDERLINGS: her stored spiderlings are units in Spider Form ('league_elise_spiderling', spawn_unit) \
                                    - ON;"), "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["SPIDERLING ASK #1", "SPIDERLING SPAWN #1 (the queued effect)", "SPIDERLING UNITS ON #1", "SPIDERLING #1 LOOK #1",
                     "SPIDERLING #1 #1: 61 of 900 ticks", "SPIDERLING BANISH #1: Human Form"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
        assert!(text.contains(&format!("t={t0} #0 SPIDERLING ASK")));
    }
}
