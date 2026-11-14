//! 走真实的导出入口，在一个迷你模拟里（游戏自己的 5v5 图：league_camille_wall 的墙格）跑流涡种的滚动：种子落地没打中人，
//! 副本调 `league_lillia:e_roll`——本包从落点发一颗直线投射物（往右滚 `e_roll`、往左滚 `e_roll_l`），滚到第一面墙前停下，
//! 到头后 1 tick 排 `e_wall`；滚着碰到敌人（`e_roll_hit`）就在他那里炸：周围的敌方单位（防御塔不算）吃伤害、减速、主包的
//! 梦尘（排好的 `e_dust` 跳）、英雄另外挂本包的梦尘，她回血、续 `d_on`、挂 `e_boom`，滚到头就不再炸；没打中人滚到头在那里炸。
//! 她死了不滚；滚着时她死了，打中照样炸、不回血，滚到头不炸。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use league_lillia::roll::{BOOM, ROLL, ROLL_L, SEED_R};
use mod_api_stable::*;

#[derive(Clone)]
struct Unit {
    kind: EntityKindV1,
    team: usize,
    x: f64,
    y: f64,
    alive: bool,
    radius: usize,
    buffs: Vec<BuffV1>,
}

fn unit(kind: EntityKindV1, team: usize, x: f64, y: f64) -> Unit {
    let radius = if kind == EntityKindV1::Champion { 10_000 } else { 8_000 };
    Unit { kind, team, x, y, alive: true, radius, buffs: vec![] }
}

#[derive(Default)]
struct World {
    tick: usize,
    units: Vec<Unit>,
    /// (picture, effect on hit, spec)
    spawned: Vec<(String, String, ProjectileSpawnV1)>,
    /// (tick, effect, caster, input, attack type)
    queue: Vec<(usize, String, usize, InputTargetV1, u32)>,
    /// (attacker, target, amount, damage type, attack type)
    hits: Vec<(usize, usize, usize, u32, u32)>,
    heals: Vec<(usize, usize, usize)>,
    /// (picture, where: a unit or a point)
    views: Vec<(String, InputTargetV1)>,
    sounds: Vec<String>,
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
    *out = SimOriginV1 { kind: SimOriginKindV1::ServerPresim.code(), match_id: 9, set_index: 0, ..Default::default() };
    true
}
unsafe extern "C" fn count(s: *const c_void) -> usize {
    w(s).units.len()
}
unsafe extern "C" fn at(s: *const c_void, i: usize) -> EntityHandleV1 {
    if i < w(s).units.len() { EntityHandleV1::from_id(i) } else { EntityHandleV1::NULL }
}
unsafe extern "C" fn zero(_: *const c_void) -> usize {
    0
}
unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
}
unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.alive)
}
unsafe extern "C" fn champion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.kind == EntityKindV1::Champion)
}
unsafe extern "C" fn tower(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.kind == EntityKindV1::Tower)
}
unsafe extern "C" fn kind(s: *const c_void, h: EntityHandleV1) -> u32 {
    u(s, h).map_or(u32::MAX, |e| e.kind.code())
}
unsafe extern "C" fn radius(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.radius)
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
    if u(s, h).is_none() {
        return false;
    }
    (*now, *max) = (1000, 1000);
    true
}
unsafe extern "C" fn stat(s: *const c_void, h: EntityHandleV1, out: *mut StatV1) -> bool {
    if u(s, h).is_none() {
        return false;
    }
    (*out).magic_power = 100;
    true
}
unsafe extern "C" fn buff_count(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.buffs.len())
}
unsafe extern "C" fn buff_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut BuffV1) -> bool {
    let Some(b) = u(s, h).and_then(|e| e.buffs.get(i)) else { return false };
    *out = *b;
    true
}
/// A dead unit's buffs are frozen: nothing added or taken (champion-data "A dead caster").
unsafe extern "C" fn add_buff(s: *mut c_void, id: usize, b: *const BuffV1) {
    if let Some(e) = w(s).units.get_mut(id).filter(|e| e.alive) {
        e.buffs.push(*b);
    }
}
unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, n: *const u8, len: usize) -> usize {
    let name = text(n, len);
    let Some(e) = u(s, h).filter(|e| e.alive) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.name() != name);
    before - e.buffs.len()
}
unsafe extern "C" fn queue_effect(
    s: *mut c_void,
    n: *const u8,
    len: usize,
    atype: u32,
    caster: usize,
    input: *const InputTargetV1,
    delay: usize,
) -> bool {
    let world = w(s);
    world.queue.push((world.tick + delay, text(n, len).to_string(), caster, *input, atype));
    true
}
unsafe extern "C" fn spawn(
    s: *mut c_void,
    n: *const u8,
    len: usize,
    e: *const u8,
    elen: usize,
    spec: *const ProjectileSpawnV1,
) -> bool {
    w(s).spawned.push((text(n, len).to_string(), text(e, elen).to_string(), *spec));
    true
}
unsafe extern "C" fn damage(s: *mut c_void, a: usize, t: usize, amount: usize, dt: u32, at: u32) -> bool {
    w(s).hits.push((a, t, amount, dt, at));
    true
}
unsafe extern "C" fn heal(s: *mut c_void, caster: usize, target: usize, amount: usize) {
    w(s).heals.push((caster, target, amount));
}
#[allow(clippy::too_many_arguments)]
unsafe extern "C" fn view(
    s: *mut c_void,
    n: *const u8,
    len: usize,
    _: usize,
    at: *const InputTargetV1,
    _: u64,
    _: u64,
    _: u64,
) -> bool {
    w(s).views.push((text(n, len).into(), *at));
    true
}
unsafe extern "C" fn sfx(s: *mut c_void, n: *const u8, len: usize, _: usize, _: *const InputTargetV1) -> bool {
    w(s).sounds.push(text(n, len).into());
    true
}
unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

fn vtable() -> SimVtableV1 {
    let mut vt: SimVtableV1 = unsafe { zeroed() };
    vt.size = size_of::<SimVtableV1>();
    vt.tick = Some(tick);
    vt.sim_origin = Some(origin);
    vt.entity_count = Some(count);
    vt.entity_at = Some(at);
    vt.tower_count = Some(zero);
    vt.entity_is_valid = Some(valid);
    vt.entity_is_alive = Some(alive);
    vt.entity_is_champion = Some(champion);
    vt.entity_is_tower = Some(tower);
    vt.entity_kind = Some(kind);
    vt.entity_radius = Some(radius);
    vt.entity_is_targetable = Some(alive);
    vt.entity_team = Some(team);
    vt.entity_pos = Some(pos);
    vt.entity_hp = Some(hp);
    vt.entity_stat = Some(stat);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.queue_effect = Some(queue_effect);
    vt.spawn_projectile = Some(spawn);
    vt.deal_damage_typed = Some(damage);
    vt.heal = Some(heal);
    vt.play_view_effect = Some(view);
    vt.play_sfx = Some(sfx);
    vt
}

type Effects<'a> = std::collections::HashMap<String, &'a NativeEffectRegV1>;

unsafe fn call(world: &mut World, fx: &Effects, name: &str, caster: usize, input: InputTargetV1) {
    let vt = vtable();
    let mut ctx =
        SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(), state: world as *mut World as *mut c_void };
    let e = fx.get(name).unwrap_or_else(|| panic!("effect {name} is not registered")).effect;
    ((*e.vtable).apply.unwrap())(e.userdata, &mut ctx, 0, caster, &input);
}

/// Runs what is queued up to and including `until`, earliest first.
unsafe fn run_queue(world: &mut World, fx: &Effects, until: usize) {
    while let Some(i) = world.queue.iter().enumerate().filter(|(_, q)| q.0 <= until).min_by_key(|(_, q)| q.0).map(|(i, _)| i) {
        let (t, name, caster, input, _) = world.queue.remove(i);
        world.tick = t;
        call(world, fx, &name, caster, input);
    }
    world.tick = until;
}

fn has(w: &World, id: usize, name: &str) -> Option<BuffV1> {
    w.units[id].buffs.iter().find(|b| b.name() == name).copied()
}

/// Lillia #0 (blue) at `me`; row 3 of the 5v5 grid has wall cells x 15-16 (480000-544000), y 96000-128000.
fn world(me: (f64, f64)) -> World {
    World { units: vec![unit(EntityKindV1::Champion, 0, me.0, me.1)], ..World::default() }
}

const LAND: (f64, f64) = (300_000.0, 110_000.0);

fn land() -> InputTargetV1 {
    InputTargetV1::pos(LAND.0 as u64, LAND.1 as u64)
}

#[test]
fn the_seed_rolls_from_its_landing_on_to_a_wall_or_an_enemy() {
    std::env::set_var("LEAGUE_LILLIA_LOG", std::env::temp_dir().join("league_lillia_test.log"));
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_lillia::tfm2_mod_entry_stable(&host);
        let _ = std::panic::take_hook();
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        for n in ["e_roll", "e_roll_hit", "e_wall", "e_dust"] {
            assert!(fx.contains_key(&format!("league_lillia:{n}")), "{n} registered");
        }
        let p = league_lillia::Params::default();

        // 1. thrown east from (200000, 110000), nobody where it landed: it rolls east from the landing point to the wall
        //    at 480000 (stopping a seed short of it), clockwise; the wall's blast is queued a tick after it gets there
        let mut wd = world((200_000.0, 110_000.0));
        call(&mut wd, &fx, "league_lillia:e_roll", 0, land());
        assert_eq!(wd.spawned.len(), 1);
        let (pic, on_hit, spec) = wd.spawned[0].clone();
        assert_eq!((pic.as_str(), on_hit.as_str()), (ROLL, "league_lillia:e_roll_hit"));
        let len = 480_000.0 - 1_000.0 - SEED_R - LAND.0;
        assert_eq!((spec.x, spec.y, spec.target_x, spec.target_y), (300_000, 110_000, (LAND.0 + len) as u64, 110_000));
        assert_eq!((spec.radius, spec.speed, spec.move_kind, spec.penetrate, spec.team, spec.caster_id),
                   (p.e_roll_r as u64, p.e_roll_speed as u64, ProjectileMoveKindV1::Linear.code(), false, 0, 0));
        assert_eq!(spec.casting_target, CastingTargetV1::EnemyWithoutTower.code(), "towers are not hit");
        let ticks = (len / p.e_roll_speed as f64).ceil() as usize;
        assert_eq!(wd.queue.len(), 1);
        assert_eq!((wd.queue[0].0, wd.queue[0].1.as_str()), (ticks + 1, "league_lillia:e_wall"));
        assert_eq!((wd.queue[0].3.x, wd.queue[0].3.y), ((LAND.0 + len) as u64, 110_000));
        // nobody on the way: at the wall it blows up (its picture there), hurting nobody
        run_queue(&mut wd, &fx, ticks + 1);
        assert_eq!(wd.views.iter().map(|v| v.0.as_str()).collect::<Vec<_>>(), ["league_lillia_e_land"]);
        assert_eq!(wd.views[0].1.x, (LAND.0 + len) as u64);
        assert!(wd.hits.is_empty() && wd.heals.is_empty());

        // 2. thrown west: the counter-clockwise picture, on to the map's drawn left edge (22500)
        let mut wd = world((400_000.0, 110_000.0));
        call(&mut wd, &fx, "league_lillia:e_roll", 0, land());
        let (pic, _, spec) = wd.spawned[0].clone();
        assert_eq!(pic, ROLL_L);
        assert_eq!(spec.target_x, (23_000.0 + SEED_R) as u64, "the last open look past the edge face, less a seed");

        // 3. an enemy champion #1 rolled into, a minion #2 beside him, an ally #3 and an enemy tower #4 near: the blast
        //    is the landing's - on the enemies (not the ally, not the tower): damage, slow, the data dust's runs; on the
        //    champion her dust too; she heals once a champion, d_on and e_boom on her; the wall's blast then does nothing
        let mut wd = world((200_000.0, 110_000.0));
        wd.units.push(unit(EntityKindV1::Champion, 1, 360_000.0, 112_000.0));
        wd.units.push(unit(EntityKindV1::Minion, 1, 365_000.0, 118_000.0));
        wd.units.push(unit(EntityKindV1::Champion, 0, 362_000.0, 108_000.0));
        wd.units.push(unit(EntityKindV1::Tower, 1, 355_000.0, 112_000.0));
        call(&mut wd, &fx, "league_lillia:e_roll", 0, land());
        wd.tick = 26;
        call(&mut wd, &fx, "league_lillia:e_roll_hit", 0, InputTargetV1::target(1));
        let dmg = p.e_dmg + p.e_ratio * 100 / 100;
        let mut got: Vec<_> = wd.hits.clone();
        got.sort();
        assert_eq!(got, vec![(0, 1, dmg, DamageTypeV1::Ap.code(), AttackTypeV1::Skill.code()),
                             (0, 2, dmg, DamageTypeV1::Ap.code(), AttackTypeV1::Skill.code())]);
        for id in [1, 2] {
            let slow = has(&wd, id, "league_lillia_e_slow").expect("slowed");
            assert_eq!((slow.move_speed_mult, slow.duration_tick), (-(p.e_slow as i32), p.e_slow_t));
        }
        assert_eq!(has(&wd, 1, "league_lillia_dust").map(|b| b.duration_tick), Some(p.d_t), "her dust on the champion");
        assert!(has(&wd, 2, "league_lillia_dust").is_none(), "not on the minion (the data dust runs on it)");
        assert!(has(&wd, 3, "league_lillia_e_slow").is_none() && has(&wd, 4, "league_lillia_e_slow").is_none());
        assert_eq!(wd.heals, vec![(0, 0, p.d_heal + p.d_heal_ratio)]);
        assert!(has(&wd, 0, "league_lillia_d_on").is_some() && has(&wd, 0, BOOM).is_some());
        let runs: Vec<_> = wd.queue.iter().filter(|q| q.1 == "league_lillia:e_dust").map(|q| (q.0 - 26, q.3.target_id, q.4)).collect();
        assert_eq!(runs.len(), 10, "five runs on each of the two");
        assert!(runs.iter().all(|r| r.2 == AttackTypeV1::Dot.code()));
        assert_eq!(runs.iter().filter(|r| r.1 == 1).map(|r| r.0).collect::<Vec<_>>(), vec![1, 46, 91, 136, 181]);
        let seen: Vec<&str> = wd.views.iter().map(|v| v.0.as_str()).collect();
        assert_eq!(seen, ["league_lillia_e_land", "league_lillia_e_hit", "league_lillia_e_hit"]);
        assert_eq!(wd.sounds, ["league_lillia_e_hit", "league_lillia_e_hit"]);
        // a second contact the same roll: nothing more
        call(&mut wd, &fx, "league_lillia:e_roll_hit", 0, InputTargetV1::target(2));
        assert_eq!(wd.hits.len(), 2);
        // its dust runs: the data dust's magic, as damage over time
        let n = wd.hits.len();
        run_queue(&mut wd, &fx, 26 + 1);
        assert_eq!(wd.hits[n..].to_vec(), vec![(0, 1, p.d_dmg + p.d_ratio, DamageTypeV1::Ap.code(), AttackTypeV1::Dot.code()),
                                               (0, 2, p.d_dmg + p.d_ratio, DamageTypeV1::Ap.code(), AttackTypeV1::Dot.code())]);
        // the wall: it went off already - no second blast, the flag cleared for the next seed
        let views = wd.views.len();
        run_queue(&mut wd, &fx, 400);
        assert_eq!(wd.views.len(), views, "no blast at the wall after one on the way");
        assert!(has(&wd, 0, BOOM).is_none());
        // a dust run on a unit that died meanwhile: nothing
        let mut wd2 = world((200_000.0, 110_000.0));
        wd2.units.push(unit(EntityKindV1::Minion, 1, 1.0, 1.0));
        wd2.units[1].alive = false;
        call(&mut wd2, &fx, "league_lillia:e_dust", 0, InputTargetV1::target(1));
        assert!(wd2.hits.is_empty());

        // 4. she is dead when it lands: no roll; she stands on the landing point: no direction, no roll
        let mut wd = world((200_000.0, 110_000.0));
        wd.units[0].alive = false;
        call(&mut wd, &fx, "league_lillia:e_roll", 0, land());
        assert!(wd.spawned.is_empty() && wd.queue.is_empty());
        let mut wd = world(LAND);
        call(&mut wd, &fx, "league_lillia:e_roll", 0, land());
        assert!(wd.spawned.is_empty());

        // 5. she dies while it rolls: a hit still blows up (no heal, no flag on the dead), the wall then does not
        let mut wd = world((200_000.0, 110_000.0));
        wd.units.push(unit(EntityKindV1::Champion, 1, 360_000.0, 112_000.0));
        call(&mut wd, &fx, "league_lillia:e_roll", 0, land());
        wd.units[0].alive = false;
        call(&mut wd, &fx, "league_lillia:e_roll_hit", 0, InputTargetV1::target(1));
        assert_eq!(wd.hits.len(), 1, "the seed is out of her hands");
        assert!(wd.heals.is_empty() && has(&wd, 0, BOOM).is_none());
        let views = wd.views.len();
        run_queue(&mut wd, &fx, 400);
        assert_eq!(wd.views.len(), views, "no blast at the wall from a dead Lillia");

        // 6. landing right in front of a wall (2000 short of it, heading into it): nothing to roll
        let mut wd = world((400_000.0, 110_000.0));
        call(&mut wd, &fx, "league_lillia:e_roll", 0, InputTargetV1::pos(478_000, 110_000));
        assert!(wd.spawned.is_empty() && wd.queue.is_empty());
    }
}
