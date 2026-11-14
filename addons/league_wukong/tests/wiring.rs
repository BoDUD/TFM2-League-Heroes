//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间就没）
//! 里放一次悟空的 W：按名字取到注册的被动和原生效果，副本的数据在施放时调的 `league_wukong:clone` 从注册表里取出来调，被动每
//! tick 调一次。检查这条线接得上：`:clone` → `spawn_unit`（名字、位置、属性）→ 他身上有 `W_UNIT`（副本的数据下一拍读它）→
//! 分身打人、他转大招时分身也转 → 到时间结束；日志开头两行写着版本、分身是不是单位、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_wukong::{spin_damage, SPIN_EVERY, SPIN_T, W_LIFE, W_UNIT};
use mod_api_stable::*;

#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

use mock::{champion, MPlayer, World};

unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

type Effects<'a> = HashMap<String, &'a NativeEffectRegV1>;

/// One tick: the passive while he lives, the world's own step (this add-on queues nothing).
unsafe fn tick(w: &mut World, passive: &PassiveRegV1) {
    assert!(w.due().is_empty(), "an effect was queued");
    if w.units[0].hp > 0 {
        w.ctx(|ctx| ((*passive.vtable).on_update.unwrap())(passive.userdata, ctx, 0, 0, 0));
    }
    w.step();
}

#[test]
fn warrior_trickster_spawns_its_clone_as_a_unit_through_the_export() {
    let log = std::env::temp_dir().join(format!("league_wukong_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_WUKONG_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_wukong::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_wukong:stone"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        assert_eq!(fx.keys().map(|k| k.as_str()).collect::<Vec<_>>(), ["league_wukong:clone"]);
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let params = r#"{"pct":35,"every":30,"w_t":240,"w_slot":20,"w_period":60}"#;
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, params.as_ptr(), params.len());

        // Wukong #0 at (300000, 300000), Garen #1 15000 east of him
        let mut w = World::default();
        w.units = vec![champion("league_wukong", 0, 300_000.0, 300_000.0), champion("league_garen", 1, 315_000.0, 300_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        for _ in 0..10 {
            tick(&mut w, &passive);
        }
        // the copy's W: the clone's flag, then league_wukong:clone from the registry
        w.units[0].buffs.push((BuffV1::timed("league_wukong_w_live", 240), 240));
        let clone_fx = fx["league_wukong:clone"].effect;
        w.ctx(|ctx| ((*clone_fx.vtable).apply.unwrap())(clone_fx.userdata, ctx, 0, 0, &InputTargetV1::NONE));
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life as usize, s.at), ("league_wukong", 0, 0, W_LIFE, (300_000, 300_000)));
        assert_eq!(s.stat.move_speed, 1);
        let clone = s.gave.unwrap();
        assert!(w.has(0, W_UNIT), "no flag on him when the data's anchor first looks: the data's clone would strike too");
        for _ in 0..60 {
            tick(&mut w, &passive);
        }
        // his R with the clone out: it spins and pulses round itself
        w.units[0].buffs.push((BuffV1::timed("league_wukong_r_on", SPIN_T), SPIN_T));
        for _ in 0..W_LIFE {
            tick(&mut w, &passive);
        }
        assert!(w.damage.iter().any(|d| d.1 == clone && d.2 == 1), "the clone never hit Garen");
        let pulses = w.dealt(0, DamageTypeV1::Ad).iter().filter(|d| **d == (1, spin_damage(100))).count();
        assert_eq!(pulses, SPIN_T / SPIN_EVERY, "the clone's spin pulses");
        assert!(!w.units[clone].valid, "the clone outlived its time");
        assert_eq!(w.views.iter().filter(|v| v.1.starts_with("league_wukong_w_clone")).count(), 0, "the drawn clone played too");
        // his death is told through the export too: nothing is out, nothing is queued
        w.ctx(|ctx| ((*passive.vtable).on_dead.unwrap())(passive.userdata, ctx, 0));
        assert!(w.queue.is_empty());
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_wukong v{} (Wukong: Stone Skin regenerates % max health, W's clone a unit",
                                           env!("CARGO_PKG_VERSION"))), "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("UNIT: Warrior Trickster's clone is a unit ('league_wukong', spawn_unit) - ON; 240 ticks where he \
                                    cast W (move speed 1), his health then, 0 + 50% of his attack a hit every 60 ticks within 30000; \
                                    it spins with his R: 5 + 17% of his attack every 20 ticks within 28000, the first knocking up 36 \
                                    ticks. Test knobs ("), "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["MARK #", "UNIT SPAWN #", "UNIT #1 LOOK #", "UNIT #1 DRESS #", "UNIT #1 SPIN #", "UNIT #1 PULSE #",
                     "UNIT #1 OVER #", "TIMED OUT after 2", "UNIT #1 WAKE #"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}
