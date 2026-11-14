//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位读得回来、到时间就没）
//! 里死一次克格莫：按名字取到注册的被动、两个原生效果和比赛钩子，被动每 tick 调一次（他活着时），他倒下后实体没了（游戏里
//! `champion()` 读不到），副本的看守醒来调 `league_kogmaw:void`，之后只有比赛钩子在跑：形态朝加里奥走、够得着就炸（他攻击力
//! 的真实伤害、以他的名义）、放逐；日志开头两行写着版本、形态开没开、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_kogmaw::{BURST_FX, FORM_T, LIFE_SLACK, PASSIVE, UNIT, VOID_FX, VOID_VIEW};
use mod_api_stable::*;

#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

use mock::{champion, unit, MPlayer, World};

unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

#[test]
fn he_falls_and_his_void_form_runs_at_galio_and_bursts() {
    let log = std::env::temp_dir().join(format!("league_kogmaw_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_KOGMAW_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_kogmaw::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), [PASSIVE]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: HashMap<String, &NativeEffectRegV1> = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        assert_eq!(fx.len(), 2);
        let void = fx.get(VOID_FX).expect(":void not registered").effect;
        assert!(fx.contains_key(BURST_FX), ":burst not registered");
        let hook = ex.match_hook;
        assert!(!hook.vtable.is_null(), "no match hook: a dead Kog'Maw's form would never move");
        let on_tick = (*hook.vtable).on_match_tick.expect("on_match_tick");
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, "{}".as_ptr(), 2);

        // Kog'Maw #0 (attack 120) at (300000, 300000); Galio #1 50000 east; the nexuses #2 / #3 the simulation's number
        // hangs on; Ahri #4 his ally
        let mut w = World::default();
        let mut kog = champion("league_kogmaw", 0, 300_000.0, 300_000.0);
        kog.stat.attack = 120;
        let mut galio = champion("league_galio", 1, 350_000.0, 300_000.0);
        (galio.hp, galio.max) = (3_000, 3_000);
        w.units = vec![kog, galio, unit("nexus", EntityKindV1::Nexus, 0, 20_000.0, 20_000.0, 5_000),
                       unit("nexus", EntityKindV1::Nexus, 1, 900_000.0, 900_000.0, 5_000),
                       champion("league_ahri", 0, 100_000.0, 500_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() },
                         MPlayer { team: 0, champion: 4, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        for _ in 0..30 {
            w.ctx(|ctx| ((*passive.vtable).on_update.unwrap())(passive.userdata, ctx, 0, 0, 0));
            w.ctx(|ctx| on_tick(hook.userdata, ctx, 0));
            w.step();
        }
        // he falls: his entity gone (the passive no longer runs); the copy's watch lands on his spot
        let t0 = w.tick;
        (w.units[0].hp, w.units[0].died, w.units[0].valid) = (0, Some(t0), false);
        w.ctx(|ctx| ((*void.vtable).apply.unwrap())(void.userdata, ctx, 0, 0, &InputTargetV1::pos(300_000, 300_000)));
        let ids: Vec<usize> = w.spawns.iter().filter(|s| s.name == UNIT).filter_map(|s| s.gave).collect();
        assert_eq!(ids.len(), 1);
        assert_eq!(w.spawns[0].life as usize, FORM_T + LIFE_SLACK);
        let id = ids[0];
        for _ in 0..FORM_T + 20 {
            w.ctx(|ctx| on_tick(hook.userdata, ctx, 0));
            w.step();
        }
        // 50000 to Galio, the burst within 12000 + his radius (10000 in the mock): 28 paces
        let burst = w.banishes.iter().find(|b| b.2 == id).expect("the form never burst").0;
        assert!((t0 + 26..=t0 + 29).contains(&burst), "burst {} ticks after the wake", burst - t0);
        let hits: Vec<(usize, usize)> = w.damage.iter().filter(|d| d.4 == DamageTypeV1::Fixed.code()).map(|d| (d.1, d.2)).collect();
        assert_eq!(hits, vec![(0, 1)], "Galio, under Kog'Maw's name");
        assert_eq!(w.damage.iter().find(|d| d.4 == DamageTypeV1::Fixed.code()).unwrap().3, 200, "80 + 100% of 120");
        assert_eq!(w.viewed(VOID_VIEW), 1);
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_kogmaw v{} (Kog'Maw: Icathian Surprise as in League", env!("CARGO_PKG_VERSION"))),
                "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("VOID: the form is a unit ('league_kogmaw_void', spawn_unit) - ON; it runs 1000 a tick"), "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["SPAWN #1: the add-on's Kog'Maw (player 0, team 0, attack 120)", "VOID SPAWN #1", "VOID LOOK #1", "VOID STEP #1",
                     "VOID BURST #1", "REACHED league_galio#1", "1 hit for 200 true damage each (his): league_galio#1"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}
