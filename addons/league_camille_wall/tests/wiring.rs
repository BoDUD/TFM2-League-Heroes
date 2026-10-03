//! 走真实的导出入口，在一个迷你模拟里把 E 从头放到尾：宿主的强制位移每 tick 按速度
//! 挪人、撞墙停下，排队的效果到点触发，buff 和控制按 tick 过期，被动每 tick 调一次。检查上路
//! 打架时她钩路边的墙、拉过去、挂一下、扑上去，伤害/眩晕/攻速都到位；被动不等武装自己出 E、
//! 冷却中不再出；宿主不挪人（忽略 ForceMove）时靠逐 tick 设位置也能走完；逃跑（被围、血少）
//! 钩远离敌人的墙；空地上不出手，有塔就钩塔；拉过去的路上目标跑远了也追着扑出去；靠地图边
//! 打架时钩石堆。只验证 mod 这边的逻辑和接线。

use std::collections::HashMap;
use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use league_camille_wall::{Grid, CLING, CONTACT};
use mod_api_stable::*;

// ---------- 地图自定义钩子用的 JSON 文档 ----------

struct Doc(HashMap<&'static str, String>);

unsafe extern "C" fn doc_get(
    s: *const c_void,
    path: *const u8,
    len: usize,
    buf: *mut u8,
    cap: usize,
    out_len: *mut usize,
) -> bool {
    let doc = &*(s as *const Doc);
    let path = std::str::from_utf8(std::slice::from_raw_parts(path, len)).unwrap();
    let Some(v) = doc.0.get(path) else { return false };
    *out_len = v.len();
    if !buf.is_null() {
        std::ptr::copy_nonoverlapping(v.as_ptr(), buf, v.len().min(cap));
    }
    true
}

// ---------- 迷你模拟 ----------

#[derive(Clone)]
struct Unit {
    x: f64,
    y: f64,
    team: usize,
    champion: bool,
    tower: bool,
    attack: usize,
    buffs: Vec<(BuffV1, usize)>,
    ccs: Vec<(CcV1, u64)>,
    damage: usize,
    stunned: bool,
    hp: usize,
}

fn unit(x: f64, y: f64, team: usize, champion: bool) -> Unit {
    Unit { x, y, team, champion, tower: false, attack: 100, buffs: vec![], ccs: vec![], damage: 0, stunned: false, hp: 1000 }
}

struct World {
    tick: usize,
    units: Vec<Unit>,
    queue: Vec<(usize, String, usize, InputTargetV1)>,
    hooks: Vec<(String, String, ProjectileSpawnV1)>,
    views: Vec<String>,
    sounds: Vec<String>,
    anims: Vec<String>,
    added: Vec<String>,
    force_move_works: bool,
    grid: Grid,
    trace: Vec<(f64, f64)>,
}

impl World {
    fn new(units: Vec<Unit>) -> World {
        World {
            tick: 0,
            units,
            queue: vec![],
            hooks: vec![],
            views: vec![],
            sounds: vec![],
            anims: vec![],
            added: vec![],
            force_move_works: true,
            grid: Grid::builtin(GameModeKindV1::Moba),
            trace: vec![],
        }
    }
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
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    *x = e.x.round() as u64;
    *y = e.y.round() as u64;
    true
}
unsafe extern "C" fn stat(s: *const c_void, h: EntityHandleV1, out: *mut StatV1) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*out).attack = e.attack;
    true
}
unsafe extern "C" fn hp(s: *const c_void, h: EntityHandleV1, now: *mut usize, max: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*now, *max) = (e.hp, 1000);
    true
}
unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.team)
}
unsafe extern "C" fn champion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.champion)
}
unsafe extern "C" fn tower(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.tower)
}
unsafe extern "C" fn yes(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
}
unsafe extern "C" fn radius(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| if e.champion { 10_000 } else { 5_000 })
}
unsafe extern "C" fn buff_count(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.buffs.len())
}
unsafe extern "C" fn buff_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut BuffV1) -> bool {
    let Some(b) = u(s, h).and_then(|e| e.buffs.get(i)) else { return false };
    *out = b.0;
    true
}
unsafe extern "C" fn cc_count(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.ccs.len())
}
unsafe extern "C" fn cc_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut CcV1) -> bool {
    let Some(c) = u(s, h).and_then(|e| e.ccs.get(i)) else { return false };
    *out = c.0;
    true
}
unsafe extern "C" fn champion_count(s: *const c_void) -> usize {
    w(s).units.iter().filter(|e| e.champion).count()
}
unsafe extern "C" fn add_buff(s: *mut c_void, id: usize, b: *const BuffV1) {
    let b = *b;
    w(s).added.push(b.name().to_string());
    if let Some(e) = w(s).units.get_mut(id) {
        e.buffs.push((b, b.duration_tick));
    }
}
unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, n: *const u8, len: usize) -> usize {
    let name = text(n, len);
    let Some(e) = u(s, h) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.0.name() != name);
    before - e.buffs.len()
}
unsafe extern "C" fn apply_cc(s: *mut c_void, id: usize, cc: *const CcV1) {
    let cc = *cc;
    let world = w(s);
    if cc.kind == CcKindV1::ForceMove.code() && !world.force_move_works {
        return;
    }
    if cc.kind == CcKindV1::Animation.code() {
        world.anims.push(cc.name().to_string());
    }
    if let Some(e) = world.units.get_mut(id) {
        e.stunned |= cc.kind == CcKindV1::Stun.code() && cc.tick == 45;
        e.ccs.push((cc, cc.tick));
    }
}
unsafe extern "C" fn queue_effect(
    s: *mut c_void,
    n: *const u8,
    len: usize,
    _: u32,
    caster: usize,
    input: *const InputTargetV1,
    delay: usize,
) -> bool {
    let world = w(s);
    world.queue.push((world.tick + delay, text(n, len).to_string(), caster, *input));
    true
}
unsafe extern "C" fn spawn_projectile(
    s: *mut c_void,
    n: *const u8,
    nl: usize,
    e: *const u8,
    el: usize,
    spec: *const ProjectileSpawnV1,
) -> bool {
    w(s).hooks.push((text(n, nl).to_string(), text(e, el).to_string(), *spec));
    true
}
unsafe extern "C" fn view_effect(
    s: *mut c_void,
    n: *const u8,
    len: usize,
    _: usize,
    _: *const InputTargetV1,
    _: u64,
    _: u64,
    _: u64,
) -> bool {
    w(s).views.push(text(n, len).to_string());
    true
}
unsafe extern "C" fn sfx(s: *mut c_void, n: *const u8, len: usize, _: usize, _: *const InputTargetV1) -> bool {
    w(s).sounds.push(text(n, len).to_string());
    true
}
unsafe extern "C" fn damage(s: *mut c_void, _: usize, target: usize, ad: usize, _: usize, _: u32) {
    if let Some(e) = w(s).units.get_mut(target) {
        e.damage += ad;
    }
}
unsafe extern "C" fn set_pos(s: *mut c_void, h: EntityHandleV1, x: u64, y: u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    e.x = x as f64;
    e.y = y as f64;
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
    vt.entity_is_valid = Some(valid);
    vt.entity_pos = Some(pos);
    vt.entity_stat = Some(stat);
    vt.entity_hp = Some(hp);
    vt.entity_team = Some(team);
    vt.entity_is_champion = Some(champion);
    vt.entity_is_tower = Some(tower);
    vt.entity_is_alive = Some(yes);
    vt.entity_is_targetable = Some(yes);
    vt.entity_radius = Some(radius);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.entity_cc_count = Some(cc_count);
    vt.entity_cc_at = Some(cc_at);
    vt.champion_count = Some(champion_count);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.apply_cc = Some(apply_cc);
    vt.queue_effect = Some(queue_effect);
    vt.spawn_projectile = Some(spawn_projectile);
    vt.play_view_effect = Some(view_effect);
    vt.play_sfx = Some(sfx);
    vt.deal_damage = Some(damage);
    vt.entity_set_pos = Some(set_pos);
    vt
}

type Effects<'a> = HashMap<String, &'a NativeEffectRegV1>;

/// 调一个效果（像数据层那样，以她自己为输入目标）。
unsafe fn call(world: &mut World, fx: &Effects, name: &str, caster: usize, input: InputTargetV1) {
    let vt = vtable();
    let mut ctx = SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(), state: world as *mut World as *mut c_void };
    let e = fx.get(name).unwrap_or_else(|| panic!("effect {name} is not registered")).effect;
    ((*e.vtable).apply.unwrap())(e.userdata, &mut ctx, 0, caster, &input);
}

/// 跑 n 个 tick：到点的效果、强制位移（撞墙停）、buff/控制过期。
unsafe fn run(world: &mut World, fx: &Effects, n: usize) {
    run_with(world, fx, None, n);
}

/// 同上，每 tick 先调一次她（#0）的被动。
unsafe fn run_with(world: &mut World, fx: &Effects, passive: Option<&PassiveRegV1>, n: usize) {
    for _ in 0..n {
        if let Some(reg) = passive {
            let vt = vtable();
            let mut ctx = SimCtxV1 {
                size: size_of::<SimCtxV1>(),
                sim: &vt,
                frame: std::ptr::null(),
                state: world as *mut World as *mut c_void,
            };
            ((*reg.vtable).on_update.unwrap())(reg.userdata, &mut ctx, 0, 0, 0);
        }
        while let Some(i) = world.queue.iter().position(|q| q.0 <= world.tick) {
            let (_, name, caster, input) = world.queue.remove(i);
            call(world, fx, &name, caster, input);
        }
        let grid = world.grid.clone();
        for e in world.units.iter_mut() {
            for (cc, left) in e.ccs.iter_mut() {
                let len = ((cc.dx as f64).powi(2) + (cc.dy as f64).powi(2)).sqrt();
                if cc.kind == CcKindV1::ForceMove.code() && len > 0.0 {
                    let next = (e.x + cc.dx as f64 / len * cc.speed as f64, e.y + cc.dy as f64 / len * cc.speed as f64);
                    if grid.is_wall(next.0, next.1) {
                        *left = 1;
                    } else {
                        (e.x, e.y) = next;
                    }
                }
            }
            e.ccs.iter_mut().for_each(|c| c.1 -= 1);
            e.ccs.retain(|c| c.1 > 0);
            e.buffs.iter_mut().for_each(|b| b.1 = b.1.saturating_sub(1));
            e.buffs.retain(|b| b.1 > 0 || b.0.duration_kind == BuffDurationV1::Permanent.code());
        }
        world.trace.push((world.units[0].x, world.units[0].y));
        world.tick += 1;
    }
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn has(world: &World, id: usize, name: &str) -> bool {
    world.units[id].buffs.iter().any(|b| b.0.name() == name)
}

fn me(world: &World) -> (f64, f64) {
    (world.units[0].x, world.units[0].y)
}

/// 日志里第一行含 `what` 的 tick。
fn tick_of(log: &str, what: &str) -> Option<usize> {
    let line = log.lines().find(|l| l.contains(what))?;
    line.split(" t=").nth(1)?.split(' ').next()?.parse().ok()
}

/// 上路一塔的位置有座敌方塔（离战场很远，不在射程里，也让地图认得出是 5v5）。
fn far_tower() -> Unit {
    let mut t = unit(48_000.0, 272_000.0, 1, false);
    t.tower = true;
    t
}

/// 上路打架：她在 (80000, 600000)，敌方英雄 #1 在北边 50000 的路上，他身边一个敌方小兵 #2，
/// 远处一座敌方塔 #3。路东边第 3 列第 15-21 行是墙（x 96000-128000）。
fn lane_world() -> World {
    let mut camille = unit(80_000.0, 600_000.0, 0, true);
    camille.buffs.push((BuffV1::timed("league_camille_e_armed", 240), 240));
    World::new(vec![camille, unit(80_000.0, 550_000.0, 1, true), unit(86_000.0, 546_000.0, 1, false), far_tower()])
}

unsafe fn check_lane_engage(world: &World) {
    // E 交了
    assert!(has(world, 0, "league_camille_e_cd") && !has(world, 0, "league_camille_e_armed"));
    assert_eq!(world.anims, ["skill2", "skill2_dash", "skill2_dash"]);
    // 钩子咬在路边的墙上，她被拉到墙边
    let [(name, effect, spec)] = &world.hooks[..] else { panic!("one hook: {:?}", world.hooks.len()) };
    assert_eq!((name.as_str(), effect.as_str()), ("league_camille_e_hook", "league_camille_wall:noop"));
    let tip = (spec.target_x as f64, spec.target_y as f64);
    assert!(world.grid.solid(tip.0, tip.1), "the hook bites into the wall: {tip:?}");
    assert!(world.trace.iter().any(|p| dist(*p, tip) <= 4_500.0), "never reached the wall at {tip:?}");
    assert!(world.trace.iter().all(|p| !world.grid.is_wall(p.0, p.1)));
    // 扑上去：贴着他落地，60 + 70% 攻击力，眩晕他，她加攻速；塔不受伤
    let target = (world.units[1].x, world.units[1].y);
    assert!(dist(me(world), target) <= CONTACT + 2_500.0, "E2 stopped {:.0} from him", dist(me(world), target));
    assert_eq!(world.units[1].damage, 130);
    assert_eq!(world.units[3].damage, 0);
    assert!(world.units[1].stunned);
    let haste = world.units[0].buffs.iter().find(|b| b.0.name() == "league_camille_e_as").expect("attack speed");
    assert_eq!(haste.0.attack_speed_mult, 50);
    for s in ["league_camille_e_cast", "league_camille_e_pull", "league_camille_e_land"] {
        assert!(world.sounds.iter().any(|x| x == s), "{s}");
    }
    for v in ["league_camille_e_land", "league_camille_e_hit", "league_camille_e_stun"] {
        assert!(world.views.iter().any(|x| x == v), "{v}");
    }
}

#[test]
fn hookshot_from_cast_to_landing() {
    let log = std::env::temp_dir().join("league_camille_wall_test.log");
    std::env::set_var("LEAGUE_CAMILLE_WALL_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_camille_wall::tfm2_mod_entry_stable(&host);
        let _ = std::panic::take_hook();
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        assert!(fx.contains_key("league_camille_wall:engage") && fx.contains_key("league_camille_wall:escape"));

        // 建图：给 5v5 的真墙，和内置的一样
        let moba = Grid::builtin(GameModeKindV1::Moba);
        let rows: Vec<String> = moba
            .cells
            .iter()
            .map(|r| format!("[{}]", r.iter().map(|v| v.to_string()).collect::<Vec<_>>().join(",")))
            .collect();
        let mut doc = Doc(HashMap::from([
            ("walls", format!("[{}]", rows.join(","))),
            ("nexus_pos", "[[96000,864000],[864000,96000]]".to_string()),
        ]));
        let mut doc_vt: JsonDocVtableV1 = zeroed();
        doc_vt.size = size_of::<JsonDocVtableV1>();
        doc_vt.get_json = Some(doc_get);
        let mut doc_ctx =
            JsonDocCtxV1 { size: size_of::<JsonDocCtxV1>(), vtable: &doc_vt, state: &mut doc as *mut Doc as *mut c_void };
        let mc = ex.map_customizer;
        ((*mc.vtable).customize.unwrap())(mc.userdata, GameModeKindV1::Moba.code(), &mut doc_ctx);

        // 1. 上路突进：宿主的强制位移正常
        let mut world = lane_world();
        call(&mut world, &fx, "league_camille_wall:engage", 0, InputTargetV1::target(0));
        run(&mut world, &fx, 150);
        check_lane_engage(&world);

        // 2. 同上，但宿主忽略 ForceMove：逐 tick 设位置也能走完
        let mut world = lane_world();
        world.force_move_works = false;
        call(&mut world, &fx, "league_camille_wall:engage", 0, InputTargetV1::target(0));
        run(&mut world, &fx, 150);
        check_lane_engage(&world);
        assert!(world.added.iter().any(|b| b == "league_camille_wall_manual"));

        // 3. 被两个人围（主包判断的逃跑）：钩远离他们的墙
        let mut world = World::new(vec![
            unit(80_000.0, 600_000.0, 0, true),
            unit(80_000.0, 570_000.0, 1, true),
            unit(95_000.0, 575_000.0, 1, true),
            far_tower(),
        ]);
        let near = |w: &World| dist(me(w), (80_000.0, 570_000.0)).min(dist(me(w), (95_000.0, 575_000.0)));
        let before = near(&world);
        call(&mut world, &fx, "league_camille_wall:escape", 0, InputTargetV1::target(0));
        run(&mut world, &fx, 150);
        assert!(world.added.iter().any(|b| b == "league_camille_e_fled"));
        assert!(near(&world) > before + 20_000.0, "ran from {before:.0} to {:.0}", near(&world));
        assert!(world.units.iter().all(|e| e.damage == 0));
        assert!(world.trace.iter().all(|p| !world.grid.is_wall(p.0, p.1)));

        // 4. 血只剩 20%、敌人就在身边：突进改成逃跑
        let mut world =
            World::new(vec![unit(80_000.0, 600_000.0, 0, true), unit(80_000.0, 570_000.0, 1, true), far_tower()]);
        world.units[0].hp = 200;
        call(&mut world, &fx, "league_camille_wall:engage", 0, InputTargetV1::target(0));
        run(&mut world, &fx, 150);
        assert!(world.added.iter().any(|b| b == "league_camille_e_fled"));
        assert_eq!(world.units[1].damage, 0);
        assert!(dist(me(&world), (80_000.0, 570_000.0)) > 50_000.0);

        // 5. 地图中央的空地（60000 内没有墙、树林和塔）：不出手，E 不交
        let mut world = World::new(vec![
            unit(480_000.0, 480_000.0, 0, true),
            unit(500_000.0, 490_000.0, 1, true),
            unit(48_000.0, 272_000.0, 0, false),
        ]);
        call(&mut world, &fx, "league_camille_wall:engage", 0, InputTargetV1::target(0));
        run(&mut world, &fx, 30);
        assert!(world.added.is_empty() && world.hooks.is_empty() && world.anims.is_empty());

        // 6. 空地上有座我方塔 #1：钩塔，拉到贴着塔，再扑英雄 #2（敌人站在他们塔下的不扑，见 7）
        let mut tower = unit(525_000.0, 480_000.0, 0, false);
        tower.tower = true;
        let mut world = World::new(vec![
            unit(480_000.0, 480_000.0, 0, true),
            tower,
            unit(535_000.0, 495_000.0, 1, true),
            unit(48_000.0, 272_000.0, 0, false),
        ]);
        call(&mut world, &fx, "league_camille_wall:engage", 0, InputTargetV1::target(0));
        run(&mut world, &fx, 150);
        let [(_, _, spec)] = &world.hooks[..] else { panic!("one hook") };
        assert_eq!((spec.target_x, spec.target_y), (520_000, 480_000), "the hook lands on the tower's edge");
        assert!(world.trace.iter().any(|p| dist(*p, (510_000.0, 480_000.0)) <= 1_500.0), "pulled next to the tower");
        assert_eq!((world.units[1].damage, world.units[2].damage), (0, 130));
        assert!(world.units[2].stunned);

        // 7. 被动：没人武装 E（没有 e_armed），E 一好就自己出；冷却中不再出
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        let names: Vec<&str> = passives.iter().map(|p| p.name.as_str()).collect();
        assert_eq!(names, ["league_camille_wall:e"]);
        let proto = &passives[0].passive;
        let mine = PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let mut world = lane_world();
        world.units[0].buffs.clear();
        run_with(&mut world, &fx, Some(&mine), 300);
        check_lane_engage(&world);
        assert_eq!(world.hooks.len(), 1, "one E per cooldown");
        // 他站在他们自己的塔下：不扑
        let mut world = lane_world();
        world.units[0].buffs.clear();
        world.units[3] = Unit { x: 80_000.0, y: 520_000.0, ..far_tower() };
        run_with(&mut world, &fx, Some(&mine), 60);
        assert!(world.hooks.is_empty() && world.units[1].damage == 0, "dived under his tower");

        // 8. 她的 R 场地还在（r_on）：被动不突进（钩出去场地就没了）；血只剩 20%、敌人就在身边：照样钩出去逃；
        //    E 拉人途中 R 跃起：停掉，不再拉
        let mut world = lane_world();
        world.units[0].buffs.clear();
        world.units[0].buffs.push((BuffV1::timed("league_camille_r_on", 180), 180));
        run_with(&mut world, &fx, Some(&mine), 60);
        assert!(world.hooks.is_empty(), "engaged out of her own R");
        let mut world =
            World::new(vec![unit(80_000.0, 600_000.0, 0, true), unit(80_000.0, 570_000.0, 1, true), far_tower()]);
        world.units[0].hp = 200;
        world.units[0].buffs.push((BuffV1::timed("league_camille_r_on", 180), 180));
        call(&mut world, &fx, "league_camille_wall:engage", 0, InputTargetV1::target(0));
        run(&mut world, &fx, 150);
        assert!(world.added.iter().any(|b| b == "league_camille_e_fled"), "no escape inside her R");
        assert!(dist(me(&world), (80_000.0, 570_000.0)) > 50_000.0);
        let mut world = lane_world();
        call(&mut world, &fx, "league_camille_wall:engage", 0, InputTargetV1::target(0));
        run(&mut world, &fx, 22);
        world.units[0].buffs.push((BuffV1::timed("league_camille_r_leap", 60), 60));
        let at = me(&world);
        run(&mut world, &fx, 40);
        assert_eq!(world.units[1].damage, 0, "dived during her R");
        assert!(dist(me(&world), at) < 8_000.0, "kept pulling during her R: {at:?} -> {:?}", me(&world));

        // 9. 拉过去的路上他跑远了（E2 够不着）：不挂在墙上干等，追着他扑出去
        let mut world = lane_world();
        call(&mut world, &fx, "league_camille_wall:engage", 0, InputTargetV1::target(0));
        run(&mut world, &fx, 12);
        (world.units[1].x, world.units[1].y) = (80_000.0, 470_000.0);
        let mut wall = (0.0, 0.0);
        for _ in 0..80 {
            run(&mut world, &fx, 1);
            if wall == (0.0, 0.0) && world.anims.len() == 2 {
                wall = me(&world);
            }
        }
        assert_eq!(world.anims, ["skill2", "skill2_dash", "skill2_dash"], "no dive from the wall");
        let him = (80_000.0, 470_000.0);
        assert!(dist(me(&world), him) < dist(wall, him) - 30_000.0, "did not dive after him: {wall:?} -> {:?}", me(&world));
        assert!(!world.units[1].stunned && world.units[1].damage == 0);

        // 10. 靠地图左边打架（附近没有他们的塔）：他在北边石堆边上，她从南边过去——钩左边的石堆（地图边），
        //     钩子咬进石堆，拐个弯扑他
        let mut world = World::new(vec![unit(60_000.0, 360_000.0, 0, true), unit(40_000.0, 300_000.0, 1, true)]);
        call(&mut world, &fx, "league_camille_wall:engage", 0, InputTargetV1::target(0));
        run(&mut world, &fx, 120);
        let [(_, _, spec)] = &world.hooks[..] else { panic!("one hook") };
        let tip = (spec.target_x as f64, spec.target_y as f64);
        assert!(tip.0 < 22_500.0 && !world.grid.is_wall(tip.0, tip.1) && world.grid.solid(tip.0, tip.1), "{tip:?}");
        assert!(world.trace.iter().any(|p| p.0 < 25_000.0), "never reached the rocks");
        assert!(world.units[1].stunned && world.units[1].damage == 130);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        for line in [
            "== map mode=Moba ==",
            "same as built-in",
            "ENGAGE map=Moba from (80000,600000) hook wall -> (",
            "at the wall (",
            "E2 at #1",
            "LAND at (",
            "130 damage to",
            "stepping with entity_set_pos",
            "ESCAPE map=Moba from (80000,600000)",
            "ESCAPE (hp 20%) map=Moba",
            "nothing to hook",
            "ENGAGE map=Moba from (480000,480000) hook tower #1",
            "E stopped: her R started",
            "out of reach: dives after him",
            "ENGAGE map=Moba from (60000,360000) hook map edge -> (",
        ] {
            assert!(text.contains(line), "missing {line:?} in the log:\n{text}");
        }
        assert!(text.starts_with("=== league_camille_wall v4.2"), "{text}");
        assert!(!text.contains("stays at the wall") || !text.contains("E2:"), "E2 waited on the wall:
{text}");
        // 挂在墙上 CLING tick 再扑
        let (at_wall, e2) = (tick_of(&text, "at the wall").unwrap(), tick_of(&text, "E2 at #1").unwrap());
        assert!(e2 >= at_wall + CLING, "clung {} ticks", e2 - at_wall);
    }
}
