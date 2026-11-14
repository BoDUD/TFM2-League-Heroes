//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，`spawn_unit` 生成的单位会走、会打、到时间
//! 就没）里放一次炮台：按名字取到注册的被动和原生效果，被动每 tick 调一次。检查这条线接得上：副本的 Q 跑 `:q` → 炮台站的地方
//! 一次 `spawn_unit`（身体：移速 1、攻击 0）→ 黑默丁格身上有 `T_UNIT`（副本的数据在隐形弹落地时读它，不画侧面的炮台）→
//! 本包照旧开炮、魔法伤害打在加里奥身上 → 身体被打掉、这座炮台停火；日志开头两行写着版本、身体开没开、读到的测试开关。

use std::collections::HashMap;
use std::mem::{size_of, zeroed};

use league_heimerdinger::{H28G, T_UNIT};
use mod_api_stable::*;

#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

use mock::{champion, MPlayer, World};

unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

type Effects<'a> = HashMap<String, &'a NativeEffectRegV1>;

unsafe fn tick(w: &mut World, passive: &PassiveRegV1) {
    w.ctx(|ctx| ((*passive.vtable).on_update.unwrap())(passive.userdata, ctx, 0, 0, 0));
    w.step();
}

#[test]
fn a_turret_put_down_gets_a_body() {
    let log = std::env::temp_dir().join(format!("league_heimerdinger_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    let _ = std::fs::remove_file(log.with_extension("cfg"));
    std::env::set_var("LEAGUE_HEIMERDINGER_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_heimerdinger::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_heimerdinger:affinity"]);
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        for name in ["noop", "q", "x"] {
            assert!(fx.contains_key(&format!("league_heimerdinger:{name}")), "{name} not registered");
        }
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let copy = include_str!("../override/league_heimerdinger.data_champion");
        let at = copy.find("\"params\": {").expect("the copy's passive params");
        let params: String = copy[at + 10..].chars().take_while(|c| *c != '}').chain(['}']).filter(|c| !c.is_whitespace()).collect();
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, params.as_ptr(), params.len());

        // Heimerdinger #0, Garen #1 40000 east of him, Darius #2 far off (the field round them all)
        let mut w = World::default();
        w.units = vec![champion("league_heimerdinger", 0, 300_000.0, 300_000.0), champion("league_garen", 1, 340_000.0, 300_000.0),
                       champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        w.units[1].hp = 50_000;
        w.units[1].max = 50_000;
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() }];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        tick(&mut w, &passive);
        // the copy's Q at Garen: the native put
        let q = fx["league_heimerdinger:q"].effect;
        let input = InputTargetV1::target(1);
        let t0 = w.tick;
        w.ctx(|ctx| ((*q.vtable).apply.unwrap())(q.userdata, ctx, 0, 0, &input));
        let bodies: Vec<usize> = w.spawns.iter().filter(|s| s.name == H28G).filter_map(|s| s.gave).collect();
        assert_eq!(bodies.len(), 1);
        assert_eq!((w.spawns[0].at, w.spawns[0].stat.move_speed), ((320_000, 300_000), 1));
        for _ in 0..5 {
            tick(&mut w, &passive);
        }
        assert!(w.has(0, T_UNIT), "no flag on him when the bolt lands: the data's side turret would be drawn too");
        for _ in 0..150 {
            tick(&mut w, &passive);
        }
        assert!(w.damage.iter().any(|d| d.1 == 0 && d.2 == 1 && d.4 == DamageTypeV1::Ap.code()), "no shot of his reached Garen");
        // destroyed
        w.hurt(bodies[0], 1_000_000);
        for _ in 0..3 {
            tick(&mut w, &passive);
        }
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let mut lines = text.lines();
        let first = lines.next().unwrap();
        assert!(first.starts_with(&format!("=== league_heimerdinger v{} (Heimerdinger's turrets firing visible shots",
                                           env!("CARGO_PKG_VERSION"))), "{first}");
        let second = lines.next().unwrap();
        assert!(second.starts_with("TURRETS: Q's turrets and the apex have bodies of their own ('league_heimerdinger_h28g' / \
                                    'league_heimerdinger_h28q', spawn_unit"), "{second}");
        assert!(second.contains(" - ON;") && second.ends_with(".cfg): none"), "{second}");
        for what in ["TURRET SPAWN #1: Turret's body", "PUT #1: Turret at (320000, 300000)", "TURRET #1 LOOK #1 (a turret's body)",
                     "SHOT #1: Turret -> #1 (champion) Cannon", "TURRET #1 OVER #1 (a turret's body): KILLED",
                     "Turret destroyed: it stops firing"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
        assert!(text.contains(&format!("t={t0} #0 TURRET SPAWN")));
    }
}
