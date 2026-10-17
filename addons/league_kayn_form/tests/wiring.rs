//! 走真实的导出入口，在一个迷你模拟里跑凯隐的被动 `orbs`：主包副本在被打中的敌方英雄身上挂
//! `league_kayn_tag`（每次命中一层），被动按英雄的攻击距离数——近战攒暗裔、远程攒影流，查不到的英雄按离凯隐
//! 多远猜——先满的那边给凯隐挂准备标记（下一次普攻变身）；形态定下以后整局保留：阵亡清掉 buff 后，复活时
//! 和之后每 tick 补回永久的形态 buff，有准备标记时不补（等主包的变身）。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use league_kayn_form::{FORM_D, FORM_S, READY_D, READY_S, TAG};
use mod_api_stable::*;

#[derive(Clone)]
struct Unit {
    name: &'static str,
    team: usize,
    x: f64,
    alive: bool,
    buffs: Vec<(BuffV1, usize)>,
}

fn unit(name: &'static str, team: usize, x: f64) -> Unit {
    Unit { name, team, x, alive: true, buffs: vec![] }
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
    *out = SimOriginV1 { kind: SimOriginKindV1::ClientMatchView.code(), match_id: 7, set_index: 1, ..Default::default() };
    true
}
unsafe extern "C" fn count(s: *const c_void) -> usize {
    w(s).units.len()
}
unsafe extern "C" fn at(s: *const c_void, i: usize) -> EntityHandleV1 {
    if i < w(s).units.len() { EntityHandleV1::from_id(i) } else { EntityHandleV1::NULL }
}
unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
}
unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.alive)
}
unsafe extern "C" fn champion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
}
unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.team)
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*x, *y) = (e.x as u64, 500_000);
    true
}
unsafe extern "C" fn name(s: *const c_void, h: EntityHandleV1, buf: *mut u8, cap: usize, len: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    *len = e.name.len();
    if !buf.is_null() {
        std::ptr::copy_nonoverlapping(e.name.as_ptr(), buf, e.name.len().min(cap));
    }
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
    if let Some(e) = w(s).units.get_mut(id) {
        let ticks = if (*b).duration_kind == BuffDurationV1::Time.code() { (*b).duration_tick } else { usize::MAX };
        e.buffs.push((*b, ticks));
    }
}
unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, n: *const u8, len: usize) -> usize {
    let name = text(n, len);
    let Some(e) = u(s, h) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.0.name() != name);
    before - e.buffs.len()
}
unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

fn vtable() -> SimVtableV1 {
    let mut vt: SimVtableV1 = unsafe { zeroed() };
    vt.size = size_of::<SimVtableV1>();
    vt.tick = Some(tick);
    vt.sim_origin = Some(origin);
    vt.entity_count = Some(count);
    vt.entity_at = Some(at);
    vt.entity_is_valid = Some(valid);
    vt.entity_is_alive = Some(alive);
    vt.entity_is_champion = Some(champion);
    vt.entity_team = Some(team);
    vt.entity_pos = Some(pos);
    vt.entity_name = Some(name);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt
}

fn ctx(world: &mut World, vt: &SimVtableV1) -> SimCtxV1 {
    SimCtxV1 { size: size_of::<SimCtxV1>(), sim: vt, frame: std::ptr::null(), state: world as *mut World as *mut c_void }
}

/// `n` tick：每 tick 先调凯隐（#0）的被动，再让 buff 走时间。
unsafe fn run(world: &mut World, reg: &PassiveRegV1, n: usize) {
    for _ in 0..n {
        let vt = vtable();
        let mut c = ctx(world, &vt);
        ((*reg.vtable).on_update.unwrap())(reg.userdata, &mut c, 0, 0, 0);
        for e in world.units.iter_mut() {
            e.buffs.iter_mut().for_each(|b| b.1 = b.1.saturating_sub(1));
            e.buffs.retain(|b| b.1 > 0);
        }
        world.tick += 1;
    }
}

unsafe fn spawn(world: &mut World, reg: &PassiveRegV1) {
    let vt = vtable();
    let mut c = ctx(world, &vt);
    ((*reg.vtable).on_spawn.unwrap())(reg.userdata, &mut c, 0, 0);
}

/// 主包副本：凯隐打中 `id` 一次（标记一层，30 tick）。
fn hit(world: &mut World, id: usize) {
    world.units[id].buffs.push((BuffV1::timed(TAG, 30), 30));
}

fn has(world: &World, id: usize, name: &str) -> bool {
    world.units[id].buffs.iter().any(|b| b.0.name() == name)
}

/// 凯隐 #0 在 x=100000；敌方 #1 战士（近战，23000）、#2 弓箭手（远程）、#3 金克丝（本包远程）、
/// #4 别的 mod 的英雄（查不到）在 x=140000；队友 #5 也被标了（不该算）。
fn world() -> World {
    World {
        units: vec![
            unit("league_kayn", 0, 100_000.0),
            unit("fighter", 1, 110_000.0),
            unit("archer", 1, 150_000.0),
            unit("league_jinx", 1, 160_000.0),
            unit("someone_elses_hero", 1, 140_000.0),
            unit("league_garen", 0, 105_000.0),
        ],
        ..Default::default()
    }
}

#[test]
fn melee_hits_make_the_darkin_ranged_hits_the_shadow_and_the_form_stays() {
    let log = std::env::temp_dir().join("league_kayn_form_test.log");
    std::env::set_var("LEAGUE_KAYN_FORM_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_kayn_form::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        let names: Vec<&str> = passives.iter().map(|p| p.name.as_str()).collect();
        assert_eq!(names, ["league_kayn_form:orbs"]);
        let proto = &passives[0].passive;
        let fresh = |params: &str| {
            let reg = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
            let configure = (*proto.vtable).configure.expect("configure");
            configure(reg.userdata, params.as_ptr(), params.len());
            reg
        };

        // 1. 打战士 3 次、弓箭手 2 次（门槛 3 / 3）：暗裔先满，挂准备标记；标记都被数完去掉；队友身上的不算
        let k = fresh(r#"{"darkin_need":3,"shadow_need":3}"#);
        let mut w = world();
        hit(&mut w, 5);
        hit(&mut w, 1);
        hit(&mut w, 2);
        run(&mut w, &k, 1);
        assert!(!has(&w, 1, TAG) && !has(&w, 2, TAG) && has(&w, 5, TAG));
        assert!(!has(&w, 0, READY_D) && !has(&w, 0, READY_S));
        hit(&mut w, 1);
        hit(&mut w, 2);
        run(&mut w, &k, 1);
        assert!(!has(&w, 0, READY_D) && !has(&w, 0, READY_S));
        hit(&mut w, 1); // 战士第 3 次：暗裔满
        run(&mut w, &k, 1);
        assert!(has(&w, 0, READY_D) && !has(&w, 0, READY_S), "Darkin not ready");
        // 定下以后再打远程也不变
        for _ in 0..5 {
            hit(&mut w, 3);
        }
        run(&mut w, &k, 1);
        assert!(!has(&w, 0, READY_S));

        // 2. 主包的普攻播变身：去掉准备标记、加永久的形态 buff；之后不补第二层
        w.units[0].buffs.retain(|b| b.0.name() != READY_D);
        w.units[0].buffs.push((BuffV1::named(FORM_D), usize::MAX));
        run(&mut w, &k, 5);
        assert_eq!(w.units[0].buffs.iter().filter(|b| b.0.name() == FORM_D).count(), 1);

        // 3. 阵亡（buff 全清），复活：on_spawn 补回形态 buff
        w.units[0].buffs.clear();
        w.units[0].alive = false;
        run(&mut w, &k, 3);
        assert!(!has(&w, 0, FORM_D), "a dead Kayn got the buff");
        w.units[0].alive = true;
        spawn(&mut w, &k);
        assert!(has(&w, 0, FORM_D), "form not back after the respawn");

        // 4. 主包的变身没播成（准备标记过期）也补上
        let k = fresh(r#"{"darkin_need":3,"shadow_need":2}"#);
        let mut w = world();
        hit(&mut w, 2);
        hit(&mut w, 3); // 一 tick 里两层（两个远程英雄）：影流满
        run(&mut w, &k, 1);
        assert!(has(&w, 0, READY_S));
        assert!(!has(&w, 0, FORM_S));
        w.units[0].buffs.retain(|b| b.0.name() != READY_S);
        run(&mut w, &k, 1);
        assert!(has(&w, 0, FORM_S), "form not restored without the ready flag");

        // 5. 查不到的英雄：离凯隐 40000 算远程，10000 算近战
        let k = fresh(r#"{"darkin_need":2,"shadow_need":2}"#);
        let mut w = world();
        hit(&mut w, 4);
        hit(&mut w, 4);
        run(&mut w, &k, 1);
        assert!(has(&w, 0, READY_S), "a far unknown champion did not count as ranged");
        let k = fresh(r#"{"darkin_need":2,"shadow_need":2}"#);
        let mut w = world();
        w.units[4].x = 110_000.0;
        hit(&mut w, 4);
        hit(&mut w, 4);
        run(&mut w, &k, 1);
        assert!(has(&w, 0, READY_D), "a near unknown champion did not count as melee");

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        for line in ["DARKIN ready: darkin 3/3 shadow 2/3 (last hit #1 fighter, range Some(23000))", "DARKIN form restored (respawn)",
                     "SHADOW ready: darkin 0/3 shadow 2/2", "SHADOW form restored (no form buff)"] {
            assert!(text.contains(line), "missing {line:?} in the log:\n{text}");
        }
    }
}
