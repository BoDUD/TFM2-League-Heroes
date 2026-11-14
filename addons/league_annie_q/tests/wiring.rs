//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间就没）
//! 里放一次安妮的 R：按名字取到注册的被动和三个原生效果，被动每 tick 调一次，排队的效果到点从注册表里取出来调。检查这条线
//! 接得上：副本的数据给目标挂的 `TIB_MARK` → 落地画面放完时被动排 `:tibbers` → `spawn_unit`（名字、位置、属性）→ 每秒灼烧 →
//! 到时间化烟；日志开头两行写着版本、提伯斯是不是单位、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_annie_q::{aura_damage, aura_ticks, TIB_BYE, TIB_FIRST, TIB_MARK, TIB_UNIT, TIB_UNIT_LIFE};
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
fn tibbers_is_spawned_as_a_unit_through_the_export() {
    let log = std::env::temp_dir().join(format!("league_annie_q_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_ANNIE_Q_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_annie_q::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_annie_q:tibbers"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        for name in ["refund", "tibbers", "aura"] {
            assert!(fx.contains_key(&format!("league_annie_q:{name}")), "{name} not registered");
        }
        assert_eq!(fx.len(), 3);
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };

        // Annie #0 with 100 ability power, Garen #1 60000 east of her
        let mut w = World::default();
        let mut annie = champion("league_annie", 0, 300_000.0, 300_000.0);
        annie.stat.magic_power = 100;
        let mut garen = champion("league_garen", 1, 360_000.0, 300_000.0);
        (garen.hp, garen.max) = (5000, 5000);
        w.units = vec![annie, garen];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        // the copy's R: the mark on its target
        w.units[1].buffs.push((BuffV1::timed(TIB_MARK, 3 + TIB_FIRST), 3 + TIB_FIRST));
        let t0 = w.tick;
        for _ in 0..TIB_FIRST + 3 {
            tick(&mut w, &fx, &passive);
        }
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life as usize, s.at), (TIB_UNIT, 0, 0, TIB_UNIT_LIFE, (360_000, 290_000)));
        assert_eq!(s.tick, t0 + TIB_FIRST);
        let bear = s.gave.unwrap();
        for _ in 0..TIB_UNIT_LIFE + 10 {
            tick(&mut w, &fx, &passive);
        }
        // 8 pulses of 7 + 4 % of 100 on Garen, his claws on him too, one puff at his end
        let burns = w.dealt(0, DamageTypeV1::Ap);
        assert_eq!(burns, vec![(1, aura_damage(100)); aura_ticks().len()]);
        assert_eq!(aura_damage(100), 11);
        assert!(w.damage.iter().any(|d| d.1 == bear && d.2 == 1 && d.3 == 12 + 7), "he never hit Garen");
        assert_eq!(w.viewed(TIB_BYE), 1);
        assert!(w.queue.is_empty());
        w.ctx(|ctx| ((*passive.vtable).on_dead.unwrap())(passive.userdata, ctx, 0));
        assert!(w.queue.is_empty());
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_annie_q v{} (Annie's Disintegrate refunds on a kill, Tibbers a unit of his own)",
                                           env!("CARGO_PKG_VERSION"))), "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("TIBBERS: a unit of his own ('league_annie_tibbers', spawn_unit) - ON; 480 ticks, 12 + 7% of her \
                                    ability power a hit every 96 ticks, the aura 7 + 4% every 60 ticks within 30000. Test knobs ("),
                "{second}");
        assert!(second.ends_with(".cfg): none"), "{second}");
        for what in ["SPAWN: the add-on's Annie (player 0)", "TIBBERS #1 on #1", "TIBBERS #1 ASK #1", "TIBBERS SPAWN #1 (the queued effect)",
                     "TIBBERS #1 LOOK #1", "TIBBERS #1 AURA #8: pulse 8", "TIBBERS #1 OVER #1: TIMED OUT",
                     "his aura: 8 pulses, 8 burned someone, 8 burns, 88 magic in all before resistance", "TIBBERS #1 WAKE #1"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}
