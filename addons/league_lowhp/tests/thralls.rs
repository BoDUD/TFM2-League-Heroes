//! 丽桑卓的冰仆是真的单位（0.3.1，src/thralls.rs）：走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：
//! 假宿主，`spawn_unit` 生成的单位会走、到时间就没）里让一个敌方英雄死在她身边：按名字取到注册的被动和原生效果，被动每 tick
//! 调一次。检查这条线接得上：他倒下 → 排 `league_lowhp:thrall` → 一次 `spawn_unit`（移速是她的、攻击够不着人）→ 尸体处不再放
//! 冰仆的画面 → 读成单位时挂上 `ICE`（打不死）→ 它朝敌人走 → 到时间从它走到的地方扑向最近的敌方英雄碎裂（伤害打在他身上）；
//! 宿主不给单位时照旧放画面、从尸体处扑。单独一个测试进程，日志写到自己的临时文件。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_lowhp::thralls::{ICE, THRALL_UNIT};
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

/// Lissandra #0 at (300000, 300000); Darius #1 dying 20000 east of her; Garen #2 60000 east of her (where the thrall
/// walks to, and whom it lunges at); Ahri #3 her ally far off.
unsafe fn run(host_gives: bool) -> (World, String) {
    let log = std::env::temp_dir().join(format!("league_lowhp_thralls_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    std::env::set_var("LEAGUE_LOWHP_LOG", &log);
    let mut host: HostApiV1 = zeroed();
    host.size = size_of::<HostApiV1>();
    host.host_abi_level = ABI_LEVEL;
    host.log = Some(host_log);
    let ex = &*league_lowhp::tfm2_mod_entry_stable(&host);
    let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
    let lissandra = passives.iter().find(|p| p.name.as_str() == "league_lowhp:lissandra").expect("the Lissandra passive");
    let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
    let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
    assert!(fx.contains_key("league_lowhp:thrall"), "league_lowhp:thrall not registered");
    let proto = &lissandra.passive;
    let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };

    let mut w = World::default();
    w.has_spawn = host_gives;
    w.units = vec![champion("league_lissandra", 0, 300_000.0, 300_000.0), champion("league_darius", 1, 320_000.0, 300_000.0),
                   champion("league_garen", 1, 360_000.0, 300_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
    (w.units[2].hp, w.units[2].max) = (50_000, 50_000);
    w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() },
                     MPlayer { team: 1, champion: 2, ..Default::default() }];
    w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
    for _ in 0..5 {
        tick(&mut w, &fx, &passive);
    }
    // Darius falls beside her
    (w.units[1].hp, w.units[1].died) = (0, Some(w.tick));
    for _ in 0..120 {
        tick(&mut w, &fx, &passive);
    }
    ((*passive.vtable).destroy.unwrap())(passive.userdata);
    let text = std::fs::read_to_string(&log).expect("log written");
    (w, text)
}

/// One test (the two runs one after the other): each load renames the log, and the log path is the process's.
#[test]
fn thralls_walk_as_units_or_stay_pictures() {
    a_fallen_champion_rises_as_a_walking_thrall_that_shatters_where_it_walked();
    no_unit_from_the_host_keeps_the_picture_and_the_lunge_from_the_corpse();
}

fn a_fallen_champion_rises_as_a_walking_thrall_that_shatters_where_it_walked() {
    unsafe {
        let (w, text) = run(true);
        let thralls: Vec<usize> = w.spawns.iter().filter(|s| s.name == THRALL_UNIT).filter_map(|s| s.gave).collect();
        assert_eq!(thralls.len(), 1, "no thrall unit:\n{text}");
        assert_eq!(w.spawns[0].at, (320_000, 300_000), "not where Darius fell");
        assert_eq!(w.spawns[0].stat.move_speed, 1100, "not her pace");
        assert_eq!(w.viewed("league_lissandra_p_thrall"), 0, "the rise picture under a unit");
        assert!(w.units[thralls[0]].buffs.iter().any(|b| b.0.name() == ICE) || w.units[thralls[0]].died.is_some(), "no ice on it");
        // it walked toward Garen and shattered near him: her magic damage on Garen
        assert!(w.damage.iter().any(|d| d.1 == 0 && d.2 == 2 && d.4 == DamageTypeV1::Ap.code()), "the shatter missed Garen:\n{text}");
        assert!(w.damage.iter().filter(|d| d.1 == thralls[0]).all(|d| d.3 == 0), "the thrall struck someone");
        for what in ["THRALLS: Lissandra's thralls are units ('league_lissandra_thrall'", " - ON;", "THRALL UNIT SPAWN: unit #4",
                     "THRALL UNIT #1 LOOK: ", "the ice (no damage, undying, no crowd control) is on it", "THRALL #1 rose at (320000, 300000)",
                     ", walked "] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}

fn no_unit_from_the_host_keeps_the_picture_and_the_lunge_from_the_corpse() {
    unsafe {
        let (w, text) = run(false);
        assert!(w.spawns.is_empty());
        assert_eq!(w.viewed("league_lissandra_p_thrall"), 1, "no rise picture:\n{text}");
        assert!(text.contains("walked 0, lunged "), "{text}");
    }
}
