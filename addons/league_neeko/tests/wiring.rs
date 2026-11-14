//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间就没；
//! 这里照游戏 0.7.2 的预模拟日志，新单位头两拍的数字读成 1）里放一次妮蔻的 W：按名字取到注册的被动和原生效果，被动每 tick
//! 调一次，排队的效果到点从注册表里取出来调。检查这条线接得上：她挨了一大口（`on_damaged`）→ 被动排 `:split` → 她隐身、加速，
//! `spawn_unit`（名字、位置、属性）→ 分身读成单位后生命设成她的 → 挨打 0.5 秒后放逐 → 到时间结束；日志开头两行写着版本、
//! W 是不是开着、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_neeko::split::{W_FADE, W_GO, W_INVIS, W_LIFE};
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
fn a_big_hit_casts_shapesplitter_and_its_clone_is_a_unit_through_the_export() {
    let log = std::env::temp_dir().join(format!("league_neeko_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_NEEKO_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_neeko::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_neeko:glamour"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        assert_eq!(fx.keys().map(|k| k.as_str()).collect::<Vec<_>>(), ["league_neeko:split"]);
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };

        // Neeko #0 (960 health), Garen #1 of the other team 40000 east of her; new units unsettled for 2 ticks
        let mut w = World { settle: 2, ..World::default() };
        let mut nk = champion("league_neeko", 0, 300_000.0, 300_000.0);
        (nk.hp, nk.max, nk.stat.hp) = (960, 960, 960);
        w.units = vec![nk, champion("league_garen", 1, 340_000.0, 300_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        for _ in 0..5 {
            tick(&mut w, &fx, &passive);
        }
        assert!(w.spawns.is_empty());
        // Garen's burst: 300 of her 960 in a tick
        w.ctx(|ctx| ((*passive.vtable).on_damaged.unwrap())(passive.userdata, ctx, 0, 0, 1, 300));
        w.hurt(0, 300);
        for _ in 0..6 {
            tick(&mut w, &fx, &passive);
        }
        assert!(w.invisibles.iter().any(|v| v.1 == 0 && v.2 == W_INVIS), "she was not unseen");
        assert!(w.has(0, W_GO), "she is not faster");
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life as usize, s.at), ("league_neeko", 0, 0, W_LIFE, (300_000, 300_000)));
        assert_eq!((s.attack.attack, s.attack.attack_ratio, s.stat.attack), (0, 0, 0), "the clone deals damage");
        let clone = s.gave.unwrap();
        assert_eq!(w.units[clone].hp, 660, "the clone does not have her health");
        // hurt: gone 30 ticks later (banished to its time), then timed out
        w.hurt(clone, 7);
        for _ in 0..W_FADE + 2 {
            tick(&mut w, &fx, &passive);
        }
        assert_eq!(w.banishes.len(), 1);
        assert_eq!(w.banishes[0].2, clone);
        for _ in 0..W_LIFE {
            tick(&mut w, &fx, &passive);
        }
        assert!(!w.units[clone].valid, "the clone outlived its time");
        assert!(w.damage.iter().filter(|d| d.1 == clone).all(|d| d.3 == 0), "the clone dealt damage");
        assert!(w.queue.is_empty());
        w.ctx(|ctx| ((*passive.vtable).on_dead.unwrap())(passive.userdata, ctx, 0));
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_neeko v{} (Neeko: Inherent Glamour, drawn as an ally; W Shapesplitter",
                                           env!("CARGO_PKG_VERSION"))), "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("SPLIT: Shapesplitter's active (W) is the add-on's own: 15% of her max health lost within 60 \
                                    ticks with an enemy champion within 90000 casts it (840 ticks cooldown from the clone's end)"),
                "{second}");
        assert!(second.contains("a clone 'league_neeko' (spawn_unit) comes on her for 180 ticks, no damage, fading 30 ticks after it \
                                 is hurt - ON. Test knobs ("), "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["SPLIT #1 CAST #", "SPLIT SPAWN #", "SPLIT #1 LOOK #", "SPLIT #1 DRESS #", "SPLIT #1 HURT #", "SPLIT #1 FADE #",
                     "SPLIT #1 OVER #", "TIMED OUT after", "SPLIT #1 WAKE #"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}
