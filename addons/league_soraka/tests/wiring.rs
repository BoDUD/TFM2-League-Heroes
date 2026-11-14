//! 走真实的导出入口，在一个迷你模拟里跑索拉卡的被动「拯救」：每 tick 先调被动，再让 buff 过一 tick。她朝附近生命低于 40% 的
//! 友方英雄走就挂上 `league_soraka_salvation_run`（移速 +90%，一份、每次看到就续），转身、站住、那人回血、那人死了、那人是
//! 敌人、她自己死了、一下子闪过去都没有；两边都选了索拉卡时各看各的队友；主包 W 施放后的 +30%（`league_soraka_salvation`）
//! 和它互不干扰。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use league_soraka::{HOLD, LOOK, MS, PASSIVE, SALVATION, W_HASTE};
use mod_api_stable::*;

#[derive(Clone)]
struct Unit {
    team: usize,
    x: f64,
    y: f64,
    alive: bool,
    hp: usize,
    /// (buff, ticks left)
    buffs: Vec<(BuffV1, usize)>,
}

fn unit(team: usize, x: f64, hp: usize) -> Unit {
    Unit { team, x, y: 500_000.0, alive: true, hp, buffs: vec![] }
}

#[derive(Default)]
struct World {
    tick: usize,
    units: Vec<Unit>,
}

unsafe fn w<'a>(s: *const c_void) -> &'a mut World {
    &mut *(s as *mut World)
}
unsafe fn u<'a>(s: *const c_void, h: EntityHandleV1) -> Option<&'a mut Unit> {
    w(s).units.get_mut(h.id()?)
}
fn text<'a>(p: *const u8, n: usize) -> &'a str {
    unsafe { std::str::from_utf8(std::slice::from_raw_parts(p, n)).unwrap() }
}

unsafe extern "C" fn tick(s: *const c_void) -> usize {
    w(s).tick
}
unsafe extern "C" fn origin(_: *const c_void, out: *mut SimOriginV1) -> bool {
    *out = SimOriginV1 { kind: SimOriginKindV1::ServerPresim.code(), match_id: 5, set_index: 0, ..Default::default() };
    true
}
unsafe extern "C" fn count(s: *const c_void) -> usize {
    w(s).units.len()
}
unsafe extern "C" fn at(s: *const c_void, i: usize) -> EntityHandleV1 {
    if i < w(s).units.len() { EntityHandleV1::from_id(i) } else { EntityHandleV1::NULL }
}
unsafe extern "C" fn champion_id_at(s: *const c_void, i: usize) -> usize {
    if i < w(s).units.len() { i } else { usize::MAX }
}
unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
}
unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.alive)
}
unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.team)
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*x, *y) = (e.x as u64, e.y as u64);
    true
}
unsafe extern "C" fn hp(s: *const c_void, h: EntityHandleV1, now: *mut usize, max: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*now, *max) = (e.hp, 1000);
    true
}
unsafe extern "C" fn buff_count(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.buffs.len())
}
unsafe extern "C" fn buff_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut BuffV1) -> bool {
    let Some(b) = u(s, h).and_then(|e| e.buffs.get(i)) else { return false };
    *out = b.0;
    true
}
unsafe extern "C" fn add_buff(s: *mut c_void, id: usize, b: *const BuffV1) {
    if let Some(e) = w(s).units.get_mut(id).filter(|e| e.alive) {
        e.buffs.push((*b, (*b).duration_tick));
    }
}
unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, n: *const u8, len: usize) -> usize {
    let name = text(n, len);
    let Some(e) = u(s, h) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.0.name() != name);
    before - e.buffs.len()
}
/// The engine's stacking: same-name copies are the stacks; `refresh` rewrites their time, one more unless at the cap.
unsafe extern "C" fn stack_buff(s: *mut c_void, h: EntityHandleV1, b: *const BuffV1, max: usize, refresh: u32) -> usize {
    let Some(e) = u(s, h).filter(|e| e.alive) else { return 0 };
    let b = *b;
    if refresh != 0 {
        e.buffs.iter_mut().filter(|x| x.0.name() == b.name()).for_each(|x| x.1 = b.duration_tick);
    }
    let n = e.buffs.iter().filter(|x| x.0.name() == b.name()).count();
    if max == 0 || n < max {
        e.buffs.push((b, b.duration_tick));
    }
    e.buffs.iter().filter(|x| x.0.name() == b.name()).count()
}
unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

fn vtable() -> SimVtableV1 {
    let mut vt: SimVtableV1 = unsafe { zeroed() };
    vt.size = size_of::<SimVtableV1>();
    vt.tick = Some(tick);
    vt.sim_origin = Some(origin);
    vt.entity_count = Some(count);
    vt.entity_at = Some(at);
    vt.champion_count = Some(count);
    vt.champion_id_at = Some(champion_id_at);
    vt.entity_is_valid = Some(valid);
    vt.entity_is_alive = Some(alive);
    vt.entity_is_champion = Some(valid);
    vt.entity_is_targetable = Some(alive);
    vt.entity_team = Some(team);
    vt.entity_pos = Some(pos);
    vt.entity_hp = Some(hp);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.entity_stack_buff = Some(stack_buff);
    vt
}

/// One tick: each (passive, its Soraka) looks, the walkers step (dx a tick each), the buffs age.
unsafe fn run(world: &mut World, souls: &[(&PassiveRegV1, usize)], walk: &[(usize, f64)], n: usize) {
    for _ in 0..n {
        let vt = vtable();
        for (reg, me) in souls {
            let mut ctx = SimCtxV1 {
                size: size_of::<SimCtxV1>(),
                sim: &vt,
                frame: std::ptr::null(),
                state: world as *mut World as *mut c_void,
            };
            ((*reg.vtable).on_update.unwrap())(reg.userdata, &mut ctx, 0, 0, *me);
        }
        for &(id, dx) in walk {
            if world.units[id].alive {
                world.units[id].x += dx;
            }
        }
        for e in world.units.iter_mut() {
            e.buffs.iter_mut().for_each(|b| b.1 = b.1.saturating_sub(1));
            e.buffs.retain(|b| b.1 > 0);
        }
        world.tick += 1;
    }
}

fn haste(world: &World, id: usize) -> Vec<i32> {
    world.units[id].buffs.iter().filter(|b| b.0.name() == SALVATION).map(|b| b.0.move_speed_mult).collect()
}

/// The add-on's log goes to a file of its own for the test.
fn quiet_log() {
    std::env::set_var("LEAGUE_SORAKA_LOG", std::env::temp_dir().join("league_soraka_test.log"));
}

#[test]
fn salvation_hastes_her_toward_a_low_ally_only() {
    quiet_log();
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_soraka::tfm2_mod_entry_stable(&host);
        let _ = std::panic::take_hook();
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        let names: Vec<&str> = passives.iter().map(|p| p.name.as_str()).collect();
        assert_eq!(names, [PASSIVE]);
        let proto = &passives[0].passive;
        let params = include_str!("../override/league_soraka.data_champion").replace("\r\n", "\n");
        let params = {
            let at = params.find("\"params\": {").expect("the copy's passive params");
            params[at + 10..at + params[at..].find('}').unwrap() + 1].to_string()
        };
        let fresh = || {
            let reg = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
            ((*reg.vtable).configure.unwrap())(reg.userdata, params.as_ptr(), params.len());
            reg
        };

        // Soraka #0 at x 400000; a wounded ally #1 (30%) 100000 east; a healthy ally #2 east too; an enemy #3 (10%) west
        let base = || World {
            tick: 0,
            units: vec![unit(0, 400_000.0, 800), unit(0, 500_000.0, 300), unit(0, 520_000.0, 900), unit(1, 300_000.0, 100)],
        };

        // 1. walking east (1000 a tick) toward #1: on from the second look (the first has no step to read), one copy, +90%
        let s = fresh();
        let mut wd = base();
        run(&mut wd, &[(&s, 0)], &[(0, 1000.0)], LOOK + 1);
        assert_eq!(haste(&wd, 0), vec![MS as i32], "toward a 30% ally");
        run(&mut wd, &[(&s, 0)], &[(0, 1000.0)], 40);
        assert_eq!(haste(&wd, 0), vec![MS as i32], "kept on, one copy, while she heads for him");
        // 2. she turns round: gone by the first look that reads a whole step back (two looks at most), and it stays off
        run(&mut wd, &[(&s, 0)], &[(0, -1000.0)], 2 * LOOK);
        assert!(haste(&wd, 0).is_empty(), "walking away from him");
        run(&mut wd, &[(&s, 0)], &[(0, -1000.0)], 30);
        assert!(haste(&wd, 0).is_empty());
        // ...and it is back when she heads for him again
        run(&mut wd, &[(&s, 0)], &[(0, 1000.0)], 2 * LOOK);
        assert_eq!(haste(&wd, 0), vec![MS as i32]);
        // 3. standing (casting next to him): off by the second look
        run(&mut wd, &[(&s, 0)], &[], 2 * LOOK);
        assert!(haste(&wd, 0).is_empty(), "standing still");
        assert!(HOLD <= 2 * LOOK, "a lapsed refresh never outlives two looks");

        // 4. the ally healed to 40%: nobody to save
        let s = fresh();
        let mut wd = base();
        wd.units[1].hp = 400;
        run(&mut wd, &[(&s, 0)], &[(0, 1000.0)], 20);
        assert!(haste(&wd, 0).is_empty(), "40% is not below 40%");
        // 5. a wounded enemy ahead: not hers to save (walking west toward #3)
        let s = fresh();
        let mut wd = base();
        run(&mut wd, &[(&s, 0)], &[(0, -1000.0)], 20);
        assert!(haste(&wd, 0).is_empty(), "the enemy at 10%");
        // 6. the ally dies: off at once
        let s = fresh();
        let mut wd = base();
        run(&mut wd, &[(&s, 0)], &[(0, 1000.0)], 10);
        assert_eq!(haste(&wd, 0), vec![MS as i32]);
        wd.units[1].alive = false;
        run(&mut wd, &[(&s, 0)], &[(0, 1000.0)], LOOK);
        assert!(haste(&wd, 0).is_empty(), "the ally died");
        // 7. she is dead: the passive does nothing, even with the body "moving" toward him (a corpse carried, a respawn)
        let s = fresh();
        let mut wd = base();
        wd.units[0].alive = false;
        for _ in 0..10 {
            wd.units[0].x += 1000.0;
            run(&mut wd, &[(&s, 0)], &[], 1);
        }
        assert!(haste(&wd, 0).is_empty(), "dead");
        // ...alive again 3000 further east: the first look after it only measures (no step across her death)
        wd.units[0].alive = true;
        wd.units[0].x += 3000.0;
        run(&mut wd, &[(&s, 0)], &[], LOOK);
        assert!(haste(&wd, 0).is_empty(), "no step read across her death");
        // 8. too far (2500 units = 250000): no; the ally 260000 east
        let s = fresh();
        let mut wd = base();
        wd.units[1].x = 660_000.0;
        run(&mut wd, &[(&s, 0)], &[(0, 1000.0)], 6);
        assert!(haste(&wd, 0).is_empty(), "260000 away");
        // 9. a blink (30001 in one look) is not walking
        let s = fresh();
        let mut wd = base();
        run(&mut wd, &[(&s, 0)], &[], 1);
        wd.units[0].x += 30_001.0;
        run(&mut wd, &[(&s, 0)], &[], LOOK);
        assert!(haste(&wd, 0).is_empty(), "a blink toward him");

        // 10. both teams picked her: each Soraka reads her own team's wounded
        let blue = fresh();
        let red = fresh();
        let mut wd = base();
        wd.units.push(unit(1, 200_000.0, 900)); // #4: the red Soraka, west of the red #3 (10%) - walking east to it
        run(&mut wd, &[(&blue, 0), (&red, 4)], &[(0, 1000.0), (4, 1000.0)], 10);
        assert_eq!(haste(&wd, 0), vec![MS as i32], "blue toward #1");
        assert_eq!(haste(&wd, 4), vec![MS as i32], "red toward #3");
        wd.units[3].hp = 900;
        run(&mut wd, &[(&blue, 0), (&red, 4)], &[(0, 1000.0), (4, 1000.0)], LOOK);
        assert_eq!(haste(&wd, 0), vec![MS as i32], "blue keeps hers");
        assert!(haste(&wd, 4).is_empty(), "red's ally healed up");

        // 11. W's own +30% (the main pack's league_soraka_salvation, 120 ticks) and the passive's are two buffs: neither
        //     shortens nor removes the other
        let s = fresh();
        let mut wd = base();
        let mut w = BuffV1::timed(W_HASTE, 120);
        w.move_speed_mult = 30;
        wd.units[0].buffs.push((w, 120));
        run(&mut wd, &[(&s, 0)], &[(0, 1000.0)], 2 * LOOK);
        let left = |wd: &World| wd.units[0].buffs.iter().find(|b| b.0.name() == W_HASTE).map(|b| b.1);
        assert_eq!(haste(&wd, 0), vec![MS as i32]);
        assert_eq!(left(&wd), Some(120 - 2 * LOOK), "W's haste runs its own time");
        run(&mut wd, &[(&s, 0)], &[(0, -1000.0)], 2 * LOOK);
        assert!(haste(&wd, 0).is_empty());
        assert_eq!(left(&wd), Some(120 - 4 * LOOK), "turning away leaves W's haste on");
    }
}
