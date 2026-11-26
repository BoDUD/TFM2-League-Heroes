//! 走真实的导出入口，在测试用的小世界（萨科附加包的 `src/summon_mock.rs`：假宿主，buff 和控制按 tick 过期）里跑薇古丝的被动：
//! 副本数据挂的标记（终焉的等待、暮气、打中、恐惧、E 的落点、愁煞的标记）照游戏里的时机放上去，看被动做的事接得上——
//! 终焉的冷却按等级、暮气引爆（对英雄 / 小兵的伤害和缩短）、突进挂暮气（被击退的不算）、恐惧的方向 / 时长 / 减速、
//! E 落地打死人缩短终焉、愁煞能杀才冲、被标记的人死了刷新、复活时终焉回来；日志开头写着版本。

use std::mem::{size_of, zeroed};

use league_vex::{doom_cd, fear_slow, fear_ticks, gloom_damage, parse_params};
use mod_api_stable::*;

#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

use mock::{champion, unit, MPlayer, World};

unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

const PARAMS: &str = r#"{"p_cd1":1200,"p_fear":45,"p_fear4":90,"p_fs_lo":60,"p_fs_hi":99,"p_fs_d":80000,"p_dash_r":160000,
"g_t":360,"g_lo":26,"g_hi":107,"g_ratio":25,"g_u_lo":40,"g_u_hi":60,"g_cut":25,"g_cut_u":10,"e_cut":10,"e_cut_c":25,
"e_r":25000,"e_fly":18,"r_reset":480,"r_free":30,"r_wait":8,"r_kill":100,"r_crowd":1,"r2_dmg":164,"r2_ratio":50,
"w_dmg":105,"w_ratio":30}"#;

fn vx(x: &str) -> String {
    format!("league_vex_{x}")
}

fn timed(name: &str, ticks: usize) -> (BuffV1, usize) {
    (BuffV1::timed(&vx(name), ticks), ticks)
}

fn left(w: &World, id: usize, name: &str) -> Option<usize> {
    w.units[id].buffs.iter().find(|b| b.0.name() == vx(name)).map(|b| b.1)
}

/// One tick: the passive (alive or dead: it runs every tick in the game), then the world's own step.
unsafe fn tick(w: &mut World, passive: &PassiveRegV1) {
    w.ctx(|ctx| ((*passive.vtable).on_update.unwrap())(passive.userdata, ctx, 0, 0, 0));
    w.step();
}

#[test]
fn the_passive_does_league_s_vex_through_the_export() {
    let log = std::env::temp_dir().join(format!("league_vex_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    std::env::set_var("LEAGUE_VEX_LOG", &log);
    let p = parse_params(PARAMS);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_vex::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_vex:gloom"]);
        let proto = &passives[0].passive;
        let passive = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        ((*proto.vtable).configure.expect("configure"))(passive.userdata, PARAMS.as_ptr(), PARAMS.len());

        // 薇古丝 #0（8 级、100 法强）；盖伦 #1 在她东边 50000，小兵 #2 东边 30000，阿狸 #3 更远，德莱厄斯 #4、野怪 #5 在别处
        let mut w = World::default();
        w.levels_on = true;
        w.cd_on = true;
        let mut vex = champion("league_vex", 0, 300_000.0, 300_000.0);
        vex.stat.magic_power = 100;
        vex.level = 8;
        let mut garen = champion("league_garen", 1, 350_000.0, 300_000.0);
        garen.stat.move_speed = 0;
        let minion = unit("minion", EntityKindV1::Minion, 1, 330_000.0, 300_000.0, 400);
        let mut ahri = champion("league_ahri", 1, 420_000.0, 300_000.0);
        ahri.stat.move_speed = 0;
        let mut darius = champion("league_darius", 1, 700_000.0, 700_000.0);
        darius.stat.move_speed = 0;
        let camp = unit("krug", EntityKindV1::Jungle, 2, 900_000.0, 900_000.0, 900);
        w.units = vec![vex, garen, minion, ahri, darius, camp];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: 1, ..Default::default() },
                         MPlayer { team: 1, champion: 3, ..Default::default() }, MPlayer { team: 1, champion: 4, ..Default::default() }];
        w.cds = vec![(0, [0, 0, 0, 2000])];
        w.ctx(|ctx| ((*passive.vtable).on_spawn.unwrap())(passive.userdata, ctx, 0, 0));
        tick(&mut w, &passive);

        // ---- 8 级用掉终焉：数据挂的 1200 tick 改成英雄联盟的 19 / 25
        w.units[0].buffs.push(timed("p_wait", 1200));
        tick(&mut w, &passive);
        assert_eq!(doom_cd(&p, 8), 912);
        let wait = left(&w, 0, "p_wait").unwrap();
        assert!((910..=912).contains(&wait), "{wait}");

        // ---- E 给盖伦和小兵挂上暮气，然后 Q 打中他们俩
        w.units[1].buffs.push(timed("g_mark", 360));
        w.units[2].buffs.push(timed("g_mark", 360));
        tick(&mut w, &passive);
        w.units[1].buffs.push(timed("v_hit", 2));
        w.units[2].buffs.push(timed("v_hit", 2));
        let before = left(&w, 0, "p_wait").unwrap();
        tick(&mut w, &passive);
        let pops = w.dealt(0, DamageTypeV1::Ap);
        assert_eq!(pops, vec![(1, gloom_damage(&p, 8, 100, true)), (2, gloom_damage(&p, 8, 100, false))]);
        assert_eq!(gloom_damage(&p, 8, 100, true), p.g_lo + (p.g_hi - p.g_lo) * 7 / 11 + p.g_ratio);
        assert!(!w.has(1, &vx("g_mark")) && !w.has(2, &vx("g_mark")));
        // 英雄缩短 25%，小兵再缩短 10%（假宿主的 buff_at 读的是挂上时的时长，这里是 912；游戏里读剩下的）
        let after = left(&w, 0, "p_wait").unwrap();
        assert!(before <= 912);
        assert_eq!(after, 912 * 75 / 100 * 90 / 100 - 1, "{before} -> {after}");
        assert_eq!(w.viewed(&vx("g_pop")), 2);
        // 再打一下不会再引爆
        w.units[1].buffs.push(timed("v_hit", 2));
        tick(&mut w, &passive);
        assert_eq!(w.dealt(0, DamageTypeV1::Ap).len(), 2);

        // ---- Q 带终焉打中盖伦：背着她跑，8 级 75 tick，减速按他离她的远近
        w.units[1].buffs.push(timed("f_q", 2));
        tick(&mut w, &passive);
        let (_, who, cc) = *w.fears.last().unwrap();
        assert_eq!((who, cc.tick as usize), (1, fear_ticks(&p, 8)));
        assert!(cc.dx > 0 && cc.dy == 0, "{cc:?}");
        let slow = w.units[1].buffs.iter().find(|b| b.0.name() == vx("f_slow")).unwrap().0.move_speed_mult;
        assert_eq!(slow, -(fear_slow(&p, 50_000.0) as i32));
        assert!(!w.has(1, &vx("f_q")));

        // ---- 黑盾（免控）不吃恐惧
        let mut shield = BuffV1::timed("league_morgana_e_cc", 60);
        shield.cc_immune = true;
        w.units[3].buffs.push((shield, 60));
        w.units[3].buffs.push(timed("f_q", 2));
        let fears = w.fears.len();
        tick(&mut w, &passive);
        assert_eq!(w.fears.len(), fears, "a cc-immune champion was feared");
        assert!(!w.has(3, &vx("f_q")));
        w.units[3].buffs.retain(|b| !b.0.cc_immune);

        // ---- E 落在盖伦脚下：落点西边的小兵往西跑（背着落点，不是背着她）
        w.units[1].buffs.push(timed("e_aim", 2));
        tick(&mut w, &passive);
        w.units[2].buffs.push(timed("f_e", 2));
        tick(&mut w, &passive);
        let (_, who, cc) = *w.fears.last().unwrap();
        assert_eq!(who, 2);
        assert!(cc.dx < 0, "the minion ran toward her: {cc:?}");
        // 影子落地（出手后 18 tick）时小兵死了：终焉等待缩短 10%
        for _ in 0..15 {
            tick(&mut w, &passive);
        }
        let added = w.units[0].buffs.iter().find(|b| b.0.name() == vx("p_wait")).unwrap().0.duration_tick;
        w.units[2].hp = 0;
        for _ in 0..6 {
            tick(&mut w, &passive);
        }
        let after = w.units[0].buffs.iter().find(|b| b.0.name() == vx("p_wait")).unwrap().0.duration_tick;
        assert_eq!(after, added * 90 / 100, "{added} -> {after}");

        // ---- 突进：阿狸朝她闪现 40000（挂暮气），盖伦自己冲 40000（强制位移带着施法动作：挂），德莱厄斯被击退 40000（不挂）
        w.units[3].x -= 40_000.0;
        w.units[1].ccs.push((CcV1::of_kind(CcKindV1::ForceMove, 5), 5));
        w.units[1].ccs.push((CcV1::of_kind(CcKindV1::Animation, 5), 5));
        w.units[1].x -= 40_000.0;
        w.units[4].ccs.push((CcV1::of_kind(CcKindV1::ForceMove, 5), 5));
        w.units[4].x = 380_000.0;
        w.units[4].y = 300_000.0;
        tick(&mut w, &passive);
        w.units[4].x -= 40_000.0;
        tick(&mut w, &passive);
        assert!(w.has(3, &vx("g_mark")), "Ahri's blink");
        assert!(w.has(1, &vx("g_mark")), "Garen's own dash");
        assert!(!w.has(4, &vx("g_mark")), "Darius was knocked, not dashing");
        assert_eq!(w.heard(&vx("e_hit")), 2);

        // ---- 愁煞打中只剩 200 血的盖伦：冲击 164 + 50 加生人勿近 105 + 30，过了 20 魔抗也杀得死，他身边只有阿狸：冲到身上；
        //      再打满血的阿狸：停在外面
        w.units[4].x = 700_000.0;
        w.units[1].hp = 200;
        w.units[1].buffs.push(timed("r_mark", 38));
        tick(&mut w, &passive);
        assert!(w.has(0, &vx("r_in")), "a kill: onto him");
        w.units[0].buffs.retain(|b| b.0.name() != vx("r_in"));
        w.units[3].buffs.push(timed("r_mark", 38));
        tick(&mut w, &passive);
        assert!(!w.has(0, &vx("r_in")), "Ahri at full health: outside");
        // 20 tick 后盖伦死了：30 tick 后愁煞能再放
        for _ in 0..20 {
            tick(&mut w, &passive);
        }
        w.units[1].hp = 0;
        tick(&mut w, &passive);
        assert_eq!(w.cds[0].1[3], 30);

        // ---- 飞弹自己打死德莱厄斯（之前没被标记过；标记先挂再扣血）：也刷新
        w.cds[0].1[3] = 1500;
        w.units[4].hp = 0;
        w.units[4].buffs.push(timed("r_mark", 38));
        tick(&mut w, &passive);
        assert_eq!(w.cds[0].1[3], 30, "a kill by the missile resets too");

        // ---- 她死了又复活：终焉就绪
        assert!(w.has(0, &vx("p_wait")));
        w.units[0].hp = 0;
        tick(&mut w, &passive);
        w.units[0].hp = 1000;
        tick(&mut w, &passive);
        assert!(!w.has(0, &vx("p_wait")), "Doom resets on respawn");
        ((*passive.vtable).destroy.unwrap())(passive.userdata);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        let first = text.lines().next().unwrap();
        assert!(first.starts_with(&format!("=== league_vex v{} (Vex as in League V26.13", env!("CARGO_PKG_VERSION"))), "{first}");
        for what in ["SPAWN: the add-on's Vex (player 0", "DOOM: spent at level 8, back in 912 ticks", "GLOOM #1: #1 (champion) popped for",
                     "GLOOM #2: #2 (unit) popped for", "FEAR #1: #1 75 ticks at level 8, away from her", "FEAR #2: #2 75 ticks at level 8, away from the E spot",
                     "EKILL #1: #2 (unit) died under Looming Darkness", "DASH #1: #1 moved 40000", "DASH #2: #3 moved 40000", "SURGE #1: #1 hp 200", "-> onto him",
                     "SURGE #2: #3 hp 1000", "-> stop outside", "RESET #1: #1 died", "RESET #2: #4 died", "DOOM: back on respawn"] {
            assert!(text.contains(what), "missing {what:?} in the log:\n{text}");
        }
    }
}
