//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间就没）
//! 里放一次艾翁的 R：按名字取到注册的被动和原生效果，被动每 tick 调一次，排队的效果到点从注册表里取出来调。检查这条线接得上：
//! 副本的数据给目标挂的 `D_MARK` → 落下的画面放完时被动排 `:daisy` → `spawn_unit`（名字、位置、属性）→ 艾翁身上有 `D_UNIT`
//! （副本挂在目标身上的那串拳读它）→ 每第三拳砸地 → 到时间结束；日志开头两行写着版本、小菊是不是单位、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_ivern::daisy::{slam_damage, D_FIRST, D_LIFE, D_MARK, D_UNIT};
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
fn daisy_is_spawned_as_a_unit_through_the_export() {
    let log = std::env::temp_dir().join(format!("league_ivern_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_IVERN_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_ivern::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_ivern:brush"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        assert_eq!(fx.keys().map(|k| k.as_str()).collect::<Vec<_>>(), ["league_ivern:daisy"]);
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let params = r#"{"w_r":26000,"w_t":240,"w_atk":15}"#;
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, params.as_ptr(), params.len());

        // Ivern #0 (100 ability power) at (300000, 300000), Garen #1 60000 east of him
        let mut w = World::default();
        let mut iv = champion("league_ivern", 0, 300_000.0, 300_000.0);
        iv.stat.magic_power = 100;
        let mut garen = champion("league_garen", 1, 360_000.0, 300_000.0);
        (garen.hp, garen.max) = (5000, 5000);
        w.units = vec![iv, garen];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        for _ in 0..5 {
            tick(&mut w, &fx, &passive);
        }
        // the copy's drop: the mark on Garen
        w.units[1].buffs.push((BuffV1::timed(D_MARK, 3), 3));
        for _ in 0..D_FIRST + 3 {
            tick(&mut w, &fx, &passive);
        }
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life as usize, s.at), ("league_ivern_daisy", 0, 0, D_LIFE, (360_000, 291_000)));
        let daisy = s.gave.unwrap();
        assert!(w.has(0, D_UNIT), "no flag on him: the riding punches would play too");
        for _ in 0..D_LIFE + 20 {
            tick(&mut w, &fx, &passive);
        }
        assert!(w.damage.iter().any(|d| d.1 == daisy && d.2 == 1), "Daisy never punched Garen");
        let slams = w.dealt(0, DamageTypeV1::Ap).iter().filter(|d| **d == (1, slam_damage(100))).count();
        assert_eq!(slams, 2, "the third punches");
        assert!(!w.units[daisy].valid, "Daisy outlived her time");
        assert!(w.queue.is_empty());
        w.ctx(|ctx| ((*passive.vtable).on_dead.unwrap())(passive.userdata, ctx, 0));
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_ivern v{} (Ivern: Brushmaker's brush a real brush", env!("CARGO_PKG_VERSION"))),
                "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("DAISY: Daisy is a unit of her own ('league_ivern_daisy', spawn_unit) - ON; 480 ticks, 25 + 20% \
                                    of his ability power a punch every 60 ticks, every third on the same champion 40 + 30% more and a \
                                    knock-up of 50 ticks. Test knobs ("), "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["DAISY #1 ASK #", "DAISY SPAWN #", "DAISY #1 LOOK #", "DAISY #1 SLAM #", "DAISY #1 OVER #", "TIMED OUT after",
                     "DAISY #1 WAKE #"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}
