//! 召唤师峡谷（Rin 的地图，1614545 见方）上走真实的导出入口（tests/wiring.rs 的迷你模拟，另一个测试程序：日志和计数不和它
//! 混）：一座塔站在 1000000 以外，`game_places::terrain::map_of_sim` 判断是峡谷（它只看塔和水晶），星穹流丽用峡谷的墙——
//! 测试里没有墙体文件，峡谷上只有地图外算墙，所以英雄在峡谷的远半边照常起飞、飞到他前面（以前拿游戏自己的地图：那里全是
//! 地图外，一次也飞不起来）；日志第一次遇到峡谷时记一行 `== Rift: ... ==`。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

struct Unit {
    x: f64,
    y: f64,
    team: usize,
    tower: bool,
    hp: usize,
    buffs: Vec<(BuffV1, usize)>,
}

fn unit(x: f64, y: f64, team: usize) -> Unit {
    Unit { x, y, team, tower: false, hp: 1000, buffs: vec![] }
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
    *out = SimOriginV1 { kind: SimOriginKindV1::ClientMatchView.code(), match_id: 7, set_index: 0, ..Default::default() };
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
    u(s, h).is_some_and(|e| e.hp > 0)
}
unsafe extern "C" fn no(_: *const c_void, _: EntityHandleV1) -> bool {
    false
}
unsafe extern "C" fn is_tower(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.tower)
}
unsafe extern "C" fn is_champion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| !e.tower)
}
unsafe extern "C" fn kind(s: *const c_void, h: EntityHandleV1) -> u32 {
    u(s, h).map_or(0, |e| if e.tower { EntityKindV1::Tower.code() } else { EntityKindV1::Champion.code() })
}
unsafe extern "C" fn tower_count(s: *const c_void) -> usize {
    w(s).units.iter().filter(|e| e.tower).count()
}
unsafe extern "C" fn tower_id_at(s: *const c_void, i: usize) -> usize {
    w(s).units.iter().enumerate().filter(|(_, e)| e.tower).nth(i).map_or(usize::MAX, |(id, _)| id)
}
unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.team)
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*x, *y) = (e.x.round() as u64, e.y.round() as u64);
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
unsafe extern "C" fn cc_count(_: *const c_void, _: EntityHandleV1) -> usize {
    0
}
unsafe extern "C" fn add_buff(s: *mut c_void, id: usize, b: *const BuffV1) {
    if let Some(e) = w(s).units.get_mut(id) {
        e.buffs.push((*b, (*b).duration_tick));
    }
}
unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, n: *const u8, len: usize) -> usize {
    let name = text(n, len).to_string();
    let Some(e) = u(s, h) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.0.name() != name);
    before - e.buffs.len()
}
unsafe extern "C" fn sfx(_: *mut c_void, _: *const u8, _: usize, _: usize, _: *const InputTargetV1) -> bool {
    true
}
unsafe extern "C" fn set_pos(s: *mut c_void, h: EntityHandleV1, x: u64, y: u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (e.x, e.y) = (x as f64, y as f64);
    true
}
unsafe extern "C" fn visible(_: *const c_void, _: usize, _: usize) -> bool {
    true
}
unsafe extern "C" fn yes(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
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
    vt.entity_is_champion = Some(is_champion);
    vt.entity_is_tower = Some(is_tower);
    vt.entity_is_minion = Some(no);
    vt.tower_count = Some(tower_count);
    vt.tower_id_at = Some(tower_id_at);
    vt.entity_is_targetable = Some(yes);
    vt.entity_kind = Some(kind);
    vt.entity_team = Some(team);
    vt.entity_pos = Some(pos);
    vt.entity_hp = Some(hp);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.entity_cc_count = Some(cc_count);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.play_sfx = Some(sfx);
    vt.entity_set_pos = Some(set_pos);
    vt.is_visible = Some(visible);
    vt
}

/// n ticks of the passive (Aurelion Sol is unit #0), then buffs run down.
unsafe fn run(world: &mut World, passive: &PassiveRegV1, n: usize) {
    for _ in 0..n {
        let vt = vtable();
        let mut ctx = SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(),
                                 state: world as *mut World as *mut c_void };
        ((*passive.vtable).on_update.unwrap())(passive.userdata, &mut ctx, 0, 0, 0);
        for e in world.units.iter_mut() {
            e.buffs.iter_mut().for_each(|b| b.1 = b.1.saturating_sub(1));
            e.buffs.retain(|b| b.1 > 0);
        }
        world.tick += 1;
    }
}

fn named(world: &World, prefix: &str) -> Option<String> {
    world.units[0].buffs.iter().map(|b| b.0.name().to_string()).find(|n| n.starts_with(prefix))
}

#[test]
fn on_summoners_rift_astral_flight_flies_in_its_far_half() {
    // a developer pointing at the real walls file (`LEAGUE_RIFT_WALLS`) has the Rift's real walls here: not this test's
    if std::env::var_os("LEAGUE_RIFT_WALLS").is_some() {
        return;
    }
    let log = std::env::temp_dir().join("league_aurelionsol_rift_test.log");
    let _ = std::fs::remove_file(&log);
    std::env::set_var("LEAGUE_AURELIONSOL_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_aurelionsol::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        let proto = &passives[0].passive;
        let wing = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        // the Rift's far half: him, an enemy 120000 east of him with an ally of his on that one (an engage), and an
        // enemy tower far off (the map is read from the towers)
        let mut foe = unit(1_420_000.0, 1_200_000.0, 1);
        foe.hp = 800;
        let mut tower = unit(1_550_000.0, 300_000.0, 1);
        tower.tower = true;
        let mut world = World { tick: 1000, units: vec![unit(1_300_000.0, 1_200_000.0, 0), foe,
                                                        unit(1_440_000.0, 1_210_000.0, 0), tower] };
        // without the tower (no structure: not a 5v5 match) the game's own map's walls: past 960000 no flight
        let mut bare = World { tick: 1000, units: vec![unit(1_300_000.0, 1_200_000.0, 0), unit(1_420_000.0, 1_200_000.0, 1),
                                                       unit(1_440_000.0, 1_210_000.0, 0)] };
        let still = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        run(&mut bare, &still, 6);
        assert_eq!(named(&bare, "league_aurelionsol_w_to:"), None, "flew off the game's own map");
        run(&mut world, &wing, 3);
        assert_eq!(named(&world, "league_aurelionsol_w_to:").as_deref(), Some("league_aurelionsol_w_to:1370000,1200000"),
                   "no take-off on the Rift");
        run(&mut world, &wing, 40);
        assert_eq!((world.units[0].x, world.units[0].y), (1_370_000.0, 1_200_000.0), "did not fly to the landing");
        let text = std::fs::read_to_string(&log).expect("log written");
        assert_eq!(text.matches("== Rift: Astral Flight").count(), 1, "the Rift's line once:\n{text}");
        assert!(text.contains("Rift walls not found"), "the line says the walls are unknown here:\n{text}");
        assert!(text.contains("FLY #1: engage #1"), "{text}");
    }
}
