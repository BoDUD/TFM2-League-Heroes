//! 走真实的导出入口，在一个迷你模拟里试盲僧的手游式 W：强制位移每 tick 按速度挪人，单位按自己的速度走路，
//! 排队的效果到点触发，被动每 tick 调一次。检查 R 的 W 绕后让李青落到目标身后（宿主不挪人时直接放过去）；
//! 残血、正在逃的时候 W 顺着逃的方向冲走（站着打不冲），追着残血逃跑的敌人时 W 追上（他走过来、李青往回走
//! 都不冲），冷却内不再冲，冲的时候播跑步动作；W 的光亮在李青身上（不插眼）。

use std::collections::HashMap;
use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

struct Unit {
    x: f64,
    y: f64,
    /// 自己走路的速度（每 tick），被强制位移时不走。
    walk: (f64, f64),
    team: usize,
    /// 防御塔（不是英雄）。
    tower: bool,
    /// 小兵（不是英雄）。
    minion: bool,
    hp: usize,
    buffs: Vec<(BuffV1, usize)>,
    ccs: Vec<(CcV1, u64)>,
}

fn unit(x: f64, y: f64, team: usize) -> Unit {
    Unit { x, y, walk: (0.0, 0.0), team, tower: false, minion: false, hp: 1000, buffs: vec![], ccs: vec![] }
}

#[derive(Default)]
struct World {
    tick: usize,
    /// 李青的冷却（普攻、Q、E、R），被动从这里读。
    cooldowns: (usize, usize, usize, usize),
    units: Vec<Unit>,
    queue: Vec<(usize, String, usize, InputTargetV1)>,
    views: Vec<(String, u32, usize)>,
    sounds: Vec<String>,
    force_move_works: bool,
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
    *out = SimOriginV1 { kind: SimOriginKindV1::ClientMatchView.code(), match_id: 5, set_index: 0, ..Default::default() };
    true
}
unsafe extern "C" fn count(s: *const c_void) -> usize {
    w(s).units.len()
}
unsafe extern "C" fn at(s: *const c_void, i: usize) -> EntityHandleV1 {
    if i < w(s).units.len() { EntityHandleV1::from_id(i) } else { EntityHandleV1::NULL }
}
unsafe extern "C" fn yes(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
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
unsafe extern "C" fn cc_count(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.ccs.len())
}
unsafe extern "C" fn cc_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut CcV1) -> bool {
    let Some(c) = u(s, h).and_then(|e| e.ccs.get(i)) else { return false };
    *out = c.0;
    true
}
unsafe extern "C" fn add_buff(s: *mut c_void, id: usize, b: *const BuffV1) {
    if let Some(e) = w(s).units.get_mut(id) {
        e.buffs.push((*b, (*b).duration_tick));
    }
}
unsafe extern "C" fn apply_cc(s: *mut c_void, id: usize, cc: *const CcV1) {
    let cc = *cc;
    let world = w(s);
    if cc.kind == CcKindV1::ForceMove.code() && !world.force_move_works {
        return;
    }
    if let Some(e) = world.units.get_mut(id) {
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
unsafe extern "C" fn view_effect(
    s: *mut c_void,
    n: *const u8,
    len: usize,
    _: usize,
    input: *const InputTargetV1,
    _: u64,
    _: u64,
    _: u64,
) -> bool {
    w(s).views.push((text(n, len).into(), (*input).kind, (*input).target_id));
    true
}
unsafe extern "C" fn sfx(s: *mut c_void, n: *const u8, len: usize, _: usize, _: *const InputTargetV1) -> bool {
    w(s).sounds.push(text(n, len).into());
    true
}
unsafe extern "C" fn set_pos(s: *mut c_void, h: EntityHandleV1, x: u64, y: u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (e.x, e.y) = (x as f64, y as f64);
    true
}
unsafe extern "C" fn cooldowns(
    s: *const c_void,
    _: PlayerHandleV1,
    a: *mut usize,
    b: *mut usize,
    c: *mut usize,
    d: *mut usize,
) -> bool {
    (*a, *b, *c, *d) = w(s).cooldowns;
    true
}
unsafe extern "C" fn player_valid(_: *const c_void, h: PlayerHandleV1) -> bool {
    h.id() == Some(0)
}
unsafe extern "C" fn is_tower(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.tower)
}
unsafe extern "C" fn is_champion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| !e.tower && !e.minion)
}
unsafe extern "C" fn is_minion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.minion)
}
unsafe extern "C" fn player_champion(_: *const c_void, h: PlayerHandleV1) -> EntityHandleV1 {
    EntityHandleV1::from_id(h.id().unwrap_or(0))
}
// ---------- 选手 AI 的上下文 ----------
unsafe extern "C" fn ai_player(_: *const c_void) -> usize {
    0
}
unsafe extern "C" fn ai_tick(s: *const c_void) -> usize {
    w(s).tick
}
unsafe extern "C" fn ai_valid(_: *const c_void, _: *const InputV1) -> bool {
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
    vt.entity_is_valid = Some(yes);
    vt.entity_is_alive = Some(yes);
    vt.entity_is_champion = Some(is_champion);
    vt.entity_is_tower = Some(is_tower);
    vt.entity_is_minion = Some(is_minion);
    vt.player_champion = Some(player_champion);
    vt.entity_is_targetable = Some(yes);
    vt.entity_team = Some(team);
    vt.entity_pos = Some(pos);
    vt.entity_hp = Some(hp);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.entity_cc_count = Some(cc_count);
    vt.entity_cc_at = Some(cc_at);
    vt.add_buff = Some(add_buff);
    vt.apply_cc = Some(apply_cc);
    vt.queue_effect = Some(queue_effect);
    vt.play_view_effect = Some(view_effect);
    vt.play_sfx = Some(sfx);
    vt.entity_set_pos = Some(set_pos);
    vt.player_cooldowns = Some(cooldowns);
    vt.player_is_valid = Some(player_valid);
    vt
}

type Effects<'a> = HashMap<String, &'a NativeEffectRegV1>;

unsafe fn ctx_of(world: &mut World, vt: &SimVtableV1) -> SimCtxV1 {
    SimCtxV1 { size: size_of::<SimCtxV1>(), sim: vt, frame: std::ptr::null(), state: world as *mut World as *mut c_void }
}

unsafe fn call(world: &mut World, fx: &Effects, name: &str, caster: usize, input: InputTargetV1) {
    let vt = vtable();
    let mut ctx = ctx_of(world, &vt);
    let e = fx[name].effect;
    ((*e.vtable).apply.unwrap())(e.userdata, &mut ctx, 0, caster, &input);
}

/// 跑 n 个 tick：被动（#0 李青的）、到点的效果、强制位移、buff/控制过期。
unsafe fn run(world: &mut World, fx: &Effects, passive: Option<&PassiveRegV1>, n: usize) {
    for _ in 0..n {
        if let Some(reg) = passive {
            let vt = vtable();
            let mut ctx = ctx_of(world, &vt);
            ((*reg.vtable).on_update.unwrap())(reg.userdata, &mut ctx, 0, 0, 0);
        }
        while let Some(i) = world.queue.iter().position(|q| q.0 <= world.tick) {
            let (_, name, caster, input) = world.queue.remove(i);
            call(world, fx, &name, caster, input);
        }
        for e in world.units.iter_mut() {
            if !e.ccs.iter().any(|c| c.0.kind == CcKindV1::ForceMove.code()) {
                e.x += e.walk.0;
                e.y += e.walk.1;
            }
            for (cc, _) in e.ccs.iter() {
                let len = ((cc.dx as f64).powi(2) + (cc.dy as f64).powi(2)).sqrt();
                if cc.kind == CcKindV1::ForceMove.code() && len > 0.0 {
                    e.x += cc.dx as f64 / len * cc.speed as f64;
                    e.y += cc.dy as f64 / len * cc.speed as f64;
                }
            }
            e.ccs.iter_mut().for_each(|c| c.1 -= 1);
            e.ccs.retain(|c| c.1 > 0);
            e.buffs.iter_mut().for_each(|b| b.1 = b.1.saturating_sub(1));
            e.buffs.retain(|b| b.1 > 0);
        }
        world.tick += 1;
    }
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn me(world: &World) -> (f64, f64) {
    (world.units[0].x, world.units[0].y)
}

#[test]
fn w_dashes_for_the_insec_the_escape_and_the_chase() {
    let log = std::env::temp_dir().join("league_leesin_hop_test.log");
    std::env::set_var("LEAGUE_LEESIN_HOP_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_leesin_hop::tfm2_mod_entry_stable(&host);
        let _ = std::panic::take_hook();
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_leesin_hop:hop"]);
        let proto = &passives[0].passive;
        let passive = || PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };

        // 1. W 绕后回旋踢：李青在目标西边 40000，W 冲到目标东边 15000
        for works in [true, false] {
            let mut world = World { units: vec![unit(440_000.0, 480_000.0, 0), unit(480_000.0, 480_000.0, 1)], force_move_works: works, ..Default::default() };
            call(&mut world, &fx, "league_leesin_hop:insec", 0, InputTargetV1::target(1));
            assert_eq!(world.views, [("league_leesin_shield".to_string(), InputTargetKindV1::Target.code(), 0)]);
            assert!(world.sounds.contains(&"league_leesin_w_shield".to_string()));
            assert!(world.units[0].ccs.is_empty(), "the insec put a CC on him (it would cut his R)");
            run(&mut world, &fx, None, 12);
            assert!(dist(me(&world), (495_000.0, 480_000.0)) < 1_500.0, "ForceMove works {works}: {:?}", me(&world));
        }
        // 0. 选手 AI：李青按 Q 时——对走动的英雄往预判的位置打，对小兵不放（改成平 A 它）
        let ais = std::slice::from_raw_parts(ex.player_ai_ptr, ex.player_ai_len);
        assert_eq!(ais.len(), 1);
        let ai = ais[0];
        let mut world = World { units: vec![unit(400_000.0, 480_000.0, 0), unit(450_000.0, 480_000.0, 1)], force_move_works: true, ..Default::default() };
        world.units[1].walk = (0.0, -1_000.0);
        let mut ai_vt: AiVtableV1 = zeroed();
        ai_vt.size = size_of::<AiVtableV1>();
        ai_vt.player_id = Some(ai_player);
        ai_vt.tick = Some(ai_tick);
        ai_vt.is_valid_input = Some(ai_valid);
        let think = |world: &mut World, base: Option<InputV1>| -> Option<InputV1> {
            let vt = vtable();
            let mut ctx = AiCtxV1 {
                size: size_of::<AiCtxV1>(),
                vtable: &ai_vt,
                state: world as *mut World as *mut c_void,
                sim: &vt,
                sim_state: world as *mut World as *mut c_void,
            };
            let mut out: InputV1 = zeroed();
            let base_ptr = base.as_ref().map_or(std::ptr::null(), |b| b as *const InputV1);
            let code = ((*ai.vtable).think.unwrap())(ai.userdata, &mut ctx, base_ptr, &mut out);
            (code == AiDecisionKindV1::Replace.code()).then_some(out)
        };
        // 看他走几 tick（算出速度），再按 Q（内置 AI 瞄着他现在的位置）
        for _ in 0..6 {
            assert!(think(&mut world, None).is_none());
            run(&mut world, &fx, None, 1);
        }
        let q_at_him = InputV1::action(InputKindV1::Skill, InputTargetV1::dir(50_000, 0));
        let out = think(&mut world, Some(q_at_him)).expect("re-aimed");
        assert_eq!(out.kind, InputKindV1::Skill.code());
        assert!(out.target.dir_y < -15_000 && out.target.dir_x > 45_000, "aimed {:?}", (out.target.dir_x, out.target.dir_y));
        // 不按 Q 时不管
        assert!(think(&mut world, Some(InputV1::move_to(1, 1))).is_none());
        // 对小兵按 Q：改成平 A 它
        world.units[1].minion = true;
        let out = think(&mut world, Some(q_at_him)).expect("skipped");
        assert_eq!((out.kind, out.target.target_id), (InputKindV1::Attack.code(), 1));

        // 1c. 队友在他西边（往西踢），李青已经在他东边（背后）：不 W，直接贴上去（40000 → 15000）踢
        let ally = |x: f64, y: f64| unit(x, y, 0);
        let mut world = World {
            units: vec![unit(520_000.0, 480_000.0, 0), unit(480_000.0, 480_000.0, 1), ally(390_000.0, 470_000.0), ally(390_000.0, 490_000.0)],
            force_move_works: true,
            ..Default::default()
        };
        call(&mut world, &fx, "league_leesin_hop:insec", 0, InputTargetV1::target(1));
        assert!(world.views.is_empty() && world.sounds.is_empty(), "W'd although he stood behind him");
        run(&mut world, &fx, None, 12);
        assert!(dist(me(&world), (495_000.0, 480_000.0)) < 1_500.0, "direct kick from {:?}", me(&world));
        // 踢完就停：再跑 20 tick，李青不会被放回别的地方
        let at_kick = me(&world);
        run(&mut world, &fx, None, 20);
        assert!(dist(me(&world), at_kick) < 1.0, "moved after the kick: {at_kick:?} -> {:?}", me(&world));
        // 1d. 队友在西边，李青也在西边：W 到他东边（背后），往西踢
        let mut world = World {
            units: vec![unit(440_000.0, 480_000.0, 0), unit(480_000.0, 480_000.0, 1), ally(390_000.0, 480_000.0)],
            force_move_works: true,
            ..Default::default()
        };
        call(&mut world, &fx, "league_leesin_hop:insec", 0, InputTargetV1::target(1));
        assert_eq!(world.views.len(), 1);
        run(&mut world, &fx, None, 12);
        assert!(dist(me(&world), (495_000.0, 480_000.0)) < 1_500.0, "{:?}", me(&world));
        // 1e. 附近没有队友，己方塔在他南边：往南踢，W 到他北边
        let mut tower = unit(480_000.0, 700_000.0, 0);
        tower.tower = true;
        let mut world = World { units: vec![unit(440_000.0, 480_000.0, 0), unit(480_000.0, 480_000.0, 1), tower], force_move_works: true, ..Default::default() };
        call(&mut world, &fx, "league_leesin_hop:insec", 0, InputTargetV1::target(1));
        run(&mut world, &fx, None, 12);
        assert!(dist(me(&world), (480_000.0, 465_000.0)) < 1_500.0, "{:?}", me(&world));
        // 1b. 他边走边被绕后（往东走开 / 往北走）：李青一路跟着，踢的那一刻（10 tick 后）还在他身后 15000
        for walk in [(900.0, 0.0), (0.0, -900.0), (-700.0, 600.0)] {
            let mut world = World { units: vec![unit(440_000.0, 480_000.0, 0), unit(480_000.0, 480_000.0, 1)], force_move_works: true, ..Default::default() };
            world.units[1].walk = walk;
            call(&mut world, &fx, "league_leesin_hop:insec", 0, InputTargetV1::target(1));
            run(&mut world, &fx, None, 10);
            let him = (world.units[1].x, world.units[1].y);
            let want = (him.0 + 15_000.0, him.1);
            assert!(dist(me(&world), want) < 2_500.0, "walk {walk:?}: Lee {:?}, him {him:?}", me(&world));
            assert!(world.units[0].ccs.is_empty());
        }

        let ran = |world: &World| world.units[0].ccs.iter().any(|c| c.0.kind == CcKindV1::Animation.code() && c.0.name() == "run");
        // 两个人：李青 #0、敌人 #1，各自按 walk 走
        let pair = |lee: (f64, f64), lee_walk: (f64, f64), him: (f64, f64), him_walk: (f64, f64)| {
            let mut world = World { units: vec![unit(lee.0, lee.1, 0), unit(him.0, him.1, 1)], force_move_works: true, ..Default::default() };
            world.units[0].walk = lee_walk;
            world.units[1].walk = him_walk;
            world
        };

        // 2. 残血、往东逃、敌人在西边追：W 往东冲走（跑步动作）；冷却内不再冲
        let mut world = pair((480_000.0, 480_000.0), (900.0, 0.0), (450_000.0, 480_000.0), (900.0, 0.0));
        world.units[0].hp = 200;
        let hop = passive();
        run(&mut world, &fx, Some(&hop), 8);
        assert_eq!(world.views.len(), 1);
        assert!(ran(&world), "no run animation on the escape dash");
        run(&mut world, &fx, Some(&hop), 22);
        let foe = (world.units[1].x, world.units[1].y);
        assert!(me(&world).0 > foe.0 + 45_000.0, "{:?} vs {foe:?}", me(&world));
        run(&mut world, &fx, Some(&hop), 600);
        assert_eq!(world.views.len(), 1, "dashed again within the cooldown");
        // 残血但站着打（没在逃）：不 W
        let mut world = pair((480_000.0, 480_000.0), (0.0, 0.0), (450_000.0, 480_000.0), (0.0, 0.0));
        world.units[0].hp = 200;
        run(&mut world, &fx, Some(&passive()), 60);
        assert!(world.views.is_empty(), "escaped while he stood and fought");

        // 3. 敌人残血往东逃、李青往东追、离 50000：W 追到他身前 8000（跑步动作）
        let mut world = pair((480_000.0, 480_000.0), (900.0, 0.0), (530_000.0, 480_000.0), (900.0, 0.0));
        world.units[1].hp = 150;
        let hop = passive();
        run(&mut world, &fx, Some(&hop), 8);
        assert_eq!(world.views.len(), 1);
        assert!(ran(&world));
        run(&mut world, &fx, Some(&hop), 8);
        let him = (world.units[1].x, world.units[1].y);
        assert!(dist(me(&world), him) < 16_000.0, "{:?} vs {him:?}", me(&world));
        // 残血的敌人朝李青走过来 / 李青往回走：不 W
        for (lee_walk, him_walk) in [((900.0, 0.0), (-900.0, 0.0)), ((-900.0, 0.0), (900.0, 0.0))] {
            let mut world = pair((480_000.0, 480_000.0), lee_walk, (530_000.0, 480_000.0), him_walk);
            world.units[1].hp = 150;
            run(&mut world, &fx, Some(&passive()), 30);
            assert!(world.views.is_empty(), "chased with {lee_walk:?} / {him_walk:?}");
        }

        // 4. 刚放完 Q（冷却刚跳起来）：80 tick 内不 W，之后照常追
        let mut world = pair((480_000.0, 480_000.0), (900.0, 0.0), (520_000.0, 480_000.0), (900.0, 0.0));
        let hop = passive();
        run(&mut world, &fx, Some(&hop), 3);
        world.cooldowns = (0, 360, 0, 0);
        world.units[1].hp = 150;
        run(&mut world, &fx, Some(&hop), 45);
        assert!(world.views.is_empty(), "W right after a Q");
        // Q1 打中后 12 tick 才飞踢（Q2），整个过程约 76 tick：80 tick 内都不 W
        run(&mut world, &fx, Some(&hop), 30);
        assert!(world.views.is_empty(), "W during the Q2 flying kick");
        run(&mut world, &fx, Some(&hop), 20);
        assert_eq!(world.views.len(), 1);

        // 5. 都满血：不冲
        let mut world = pair((480_000.0, 480_000.0), (900.0, 0.0), (530_000.0, 480_000.0), (900.0, 0.0));
        let hop = passive();
        run(&mut world, &fx, Some(&hop), 60);
        assert!(world.views.is_empty());

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        assert!(text.starts_with("=== league_leesin_hop v1.6"), "{text}");
        assert!(!text.contains(": OFF"), "{text}");
        assert!(!text.contains("placed on the spot"), "{text}");
        for line in [
            "INSEC W behind him: kick #1 at (480000,480000) toward back; Lee (440000,480000) (40000 from him) -> (495000,480000)",
            "INSEC DIRECT: already behind him: kick #1 at (480000,480000) toward allies",
            "INSEC W behind him: kick #1 at (480000,480000) toward tower",
            "0 deg off the planned way: on target",
            "ESCAPE W to",
            "CHASE W to (527400,480000)",
            "running 900/tick",
            "Q AIM at #1 Champion at (450000,474000) walking 1000/tick: thrown at (450000,",
            "Q SKIP #1 Minion at (450000,474000): no Q on minions",
        ] {
            assert!(text.contains(line), "missing {line:?} in the log:\n{text}");
        }
    }
}
