//! 走真实的导出入口，在一个迷你模拟里放剑魔的 W：排队的效果到点触发，buff 按 tick 过期，强制位移按
//! 方向和速度每 tick 挪人（`tenacity` 的单位只走一半的 tick），剑魔的锁链停在场上（投射物列表）。
//! 检查 League 的规则（v0.2：本包只判断、只挪人，画面和伤害由数据读剑魔身上的标记来打）：只锁打中的那个人，
//! 圈心是锁链停下的地方；待在圈里 1.5 秒后被拉回圈心，剑魔身上挂 `w_pull`（英雄再挂 `w_pull_c`），数据层在
//! READ_AT 读得到；走出圈、闪现出圈锁链就断，不挂；小兵挂 `w_minion`，不锁；野怪锁、拉，不挂 `w_pull_c`；
//! 被韧性截短的拉回会补推；剑魔死了照样拉（不挂标记）；同一个人不锁两次；数据层给的是位置时找刚被减速的那个人；
//! 找不到锁链时圈心往剑魔那边挪 3000；锁链节贴地飞（两头往下挪 LINK_DROP）。

use std::collections::HashMap;
use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use league_aatrox_chain::{
    AREA, CHAMP, HOLD, LINK_DROP, LINK_EVERY, MINION, ON, PULL, PULL_C, READ_AT, STAGES, TETHER,
};
use mod_api_stable::*;

#[derive(Clone)]
struct Unit {
    name: &'static str,
    team: usize,
    x: f64,
    y: f64,
    alive: bool,
    champion: bool,
    minion: bool,
    buffs: Vec<(BuffV1, usize)>,
    ccs: Vec<(CcV1, usize)>,
    tenacity: bool,
}

fn unit(name: &'static str, team: usize, x: f64) -> Unit {
    Unit {
        name,
        team,
        x,
        y: 0.0,
        alive: true,
        champion: true,
        minion: false,
        buffs: vec![],
        ccs: vec![],
        tenacity: false,
    }
}

#[derive(Default)]
struct World {
    tick: usize,
    units: Vec<Unit>,
    projectiles: Vec<(f64, f64, usize)>,
    queue: Vec<(usize, String, usize, InputTargetV1)>,
    views: Vec<(String, InputTargetV1)>,
    sounds: Vec<String>,
    links: Vec<(usize, (u64, u64), (u64, u64))>,
    pulls: Vec<(usize, CcV1)>,
    damage: usize,
    heals: usize,
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
    u(s, h).is_some_and(|e| e.champion)
}
unsafe extern "C" fn minion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.minion)
}
unsafe extern "C" fn tower(_: *const c_void, _: EntityHandleV1) -> bool {
    false
}
unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.team)
}
unsafe extern "C" fn name(s: *const c_void, h: EntityHandleV1, buf: *mut u8, cap: usize, len: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    *len = e.name.len();
    if !buf.is_null() {
        std::ptr::copy_nonoverlapping(e.name.as_ptr(), buf, e.name.len().min(cap));
    }
    true
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*x, *y) = (e.x.round() as u64, e.y.round() as u64);
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
unsafe extern "C" fn cc_count(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.ccs.len())
}
unsafe extern "C" fn cc_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut CcV1) -> bool {
    let Some(c) = u(s, h).and_then(|e| e.ccs.get(i)) else { return false };
    *out = c.0;
    true
}
unsafe extern "C" fn apply_cc(s: *mut c_void, id: usize, cc: *const CcV1) {
    let world = w(s);
    let cc = *cc;
    world.pulls.push((id, cc));
    if let Some(e) = world.units.get_mut(id) {
        let ticks = if e.tenacity { cc.tick as usize / 2 } else { cc.tick as usize };
        e.ccs.push((cc, ticks));
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
unsafe extern "C" fn heal(s: *mut c_void, _: usize, _: usize, _: usize) {
    w(s).heals += 1;
}
unsafe extern "C" fn deal_damage(s: *mut c_void, _: usize, _: usize, _: usize, _: usize, _: u32) {
    w(s).damage += 1;
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
    w(s).views.push((text(n, len).into(), *input));
    true
}
unsafe extern "C" fn sfx(s: *mut c_void, n: *const u8, len: usize, _: usize, _: *const InputTargetV1) -> bool {
    w(s).sounds.push(text(n, len).into());
    true
}
unsafe extern "C" fn spawn_projectile(
    s: *mut c_void,
    n: *const u8,
    len: usize,
    fx: *const u8,
    fx_len: usize,
    spec: *const ProjectileSpawnV1,
) -> bool {
    assert_eq!(text(n, len), "league_aatrox_w_link");
    assert_eq!(text(fx, fx_len), "league_aatrox_chain:noop");
    let spec = *spec;
    assert_eq!(spec.move_kind, ProjectileMoveKindV1::Linear.code());
    assert_eq!(spec.casting_target, CastingTargetV1::None.code());
    let world = w(s);
    let tick = world.tick;
    world.links.push((tick, (spec.x, spec.y), (spec.target_x, spec.target_y)));
    true
}
unsafe extern "C" fn proj_count(s: *const c_void) -> usize {
    w(s).projectiles.len()
}
unsafe extern "C" fn proj_at(s: *const c_void, i: usize) -> ProjectileHandleV1 {
    if i < w(s).projectiles.len() { ProjectileHandleV1::from_id(i) } else { ProjectileHandleV1::NULL }
}
unsafe extern "C" fn proj_valid(s: *const c_void, h: ProjectileHandleV1) -> bool {
    h.id().is_some_and(|i| i < w(s).projectiles.len())
}
unsafe extern "C" fn proj_info(s: *const c_void, h: ProjectileHandleV1, out: *mut ProjectileInfoV1) -> bool {
    let Some(&(x, y, caster)) = h.id().and_then(|i| w(s).projectiles.get(i)) else { return false };
    *out = ProjectileInfoV1 { x: x as u64, y: y as u64, caster_id: caster, team: 0, is_end: false };
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
    vt.entity_is_alive = Some(alive);
    vt.entity_is_champion = Some(champion);
    vt.entity_is_minion = Some(minion);
    vt.entity_is_tower = Some(tower);
    vt.entity_is_targetable = Some(alive);
    vt.entity_pos = Some(pos);
    vt.entity_team = Some(team);
    vt.entity_name = Some(name);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.entity_cc_count = Some(cc_count);
    vt.entity_cc_at = Some(cc_at);
    vt.apply_cc = Some(apply_cc);
    vt.queue_effect = Some(queue_effect);
    vt.heal = Some(heal);
    vt.deal_damage = Some(deal_damage);
    vt.play_view_effect = Some(view_effect);
    vt.play_sfx = Some(sfx);
    vt.spawn_projectile = Some(spawn_projectile);
    vt.projectile_count = Some(proj_count);
    vt.projectile_at = Some(proj_at);
    vt.projectile_is_valid = Some(proj_valid);
    vt.projectile_info = Some(proj_info);
    vt
}

type Effects<'a> = HashMap<String, &'a NativeEffectRegV1>;

unsafe fn call(world: &mut World, fx: &Effects, name: &str, caster: usize, input: InputTargetV1) {
    let vt = vtable();
    let mut ctx =
        SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(), state: world as *mut World as *mut c_void };
    let e = fx.get(name).unwrap_or_else(|| panic!("effect {name} is not registered")).effect;
    ((*e.vtable).apply.unwrap())(e.userdata, &mut ctx, 0, caster, &input);
}

/// 一 tick 末的 (剑魔身上的标记) 快照，按 tick 记下来，测数据层读到的。
type Flags = Vec<(usize, Vec<String>)>;

/// `n` tick：每 tick `walk` 里的人先走一步，再跑到点的效果、强制位移挪人，记下剑魔的标记，buff 和控制过期。
unsafe fn run_walking(world: &mut World, fx: &Effects, n: usize, walk: &[(usize, f64)], flags: &mut Flags) {
    for _ in 0..n {
        for (id, dx) in walk {
            if world.units[*id].ccs.is_empty() {
                world.units[*id].x += dx;
            }
        }
        while let Some(i) = world.queue.iter().position(|q| q.0 <= world.tick) {
            let (_, name, caster, input) = world.queue.remove(i);
            call(world, fx, &name, caster, input);
        }
        for e in world.units.iter_mut() {
            if let Some((cc, _)) = e.ccs.first().copied() {
                if cc.kind == CcKindV1::ForceMove.code() {
                    let len = ((cc.dx * cc.dx + cc.dy * cc.dy) as f64).sqrt().max(1.0);
                    e.x += cc.dx as f64 / len * cc.speed as f64;
                    e.y += cc.dy as f64 / len * cc.speed as f64;
                }
            }
        }
        flags.push((world.tick, world.units[0].buffs.iter().map(|b| b.0.name().to_string()).collect()));
        for e in world.units.iter_mut() {
            e.ccs.iter_mut().for_each(|c| c.1 = c.1.saturating_sub(1));
            e.ccs.retain(|c| c.1 > 0);
            e.buffs.iter_mut().for_each(|b| b.1 = b.1.saturating_sub(1));
            e.buffs.retain(|b| b.1 > 0);
        }
        world.tick += 1;
    }
}

unsafe fn run(world: &mut World, fx: &Effects, n: usize, flags: &mut Flags) {
    run_walking(world, fx, n, &[], flags);
}

/// 主包的锁链打中 `target`：它停在 `stop`（剑魔的投射物），1.5 秒减速，然后调本包的 chain（目标是被打中的单位）。
unsafe fn chain_hits(world: &mut World, fx: &Effects, target: usize, stop: Option<(f64, f64)>, input: InputTargetV1) {
    world.projectiles.clear();
    world.projectiles.push((300_000.0, 300_000.0, 0)); // 剑魔别的投射物（远处的普攻）
    if let Some((x, y)) = stop {
        world.projectiles.push((x, y, 0));
    }
    world.projectiles.push((x_of(world, target) + 2_000.0, 0.0, 4)); // 诺手的投射物：不是剑魔的
    world.units[target].buffs.push((BuffV1::timed("league_aatrox_w_slowed", HOLD), HOLD));
    call(world, fx, "league_aatrox_chain:chain", 0, input);
    world.projectiles.retain(|p| p.2 != 0 || p.0 > 200_000.0);
}

fn x_of(world: &World, id: usize) -> f64 {
    world.units[id].x
}

fn has(world: &World, id: usize, prefix: &str) -> bool {
    world.units[id].buffs.iter().any(|b| b.0.name().starts_with(prefix))
}

/// 第 `t` tick 末剑魔身上有没有 `name`（数据层那一 tick 读得到）。
fn flagged(flags: &Flags, t: usize, name: &str) -> bool {
    flags.iter().any(|(tt, v)| *tt == t && v.iter().any(|n| n == name))
}

fn viewed(world: &World, name: &str) -> usize {
    world.views.iter().filter(|v| v.0 == name).count()
}

/// 剑魔 #0 在 (100000, 0)；敌方英雄 #1 盖伦在 (160000, 0)，小兵 #2、野怪 #3、敌方英雄 #4 诺手。
fn world() -> World {
    let mut minion = unit("melee_minion", 1, 150_000.0);
    (minion.champion, minion.minion) = (false, true);
    let mut monster = unit("rhino_monster", 2, 170_000.0);
    monster.champion = false;
    World {
        units: vec![
            unit("league_aatrox", 0, 100_000.0),
            unit("league_garen", 1, 160_000.0),
            minion,
            monster,
            unit("league_darius", 1, 165_000.0),
        ],
        ..Default::default()
    }
}

#[test]
fn infernal_chains_follow_league() {
    let log = std::env::temp_dir().join("league_aatrox_chain_test.log");
    std::env::set_var("LEAGUE_AATROX_CHAIN_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_aatrox_chain::tfm2_mod_entry_stable(&host);
        let _ = std::panic::take_hook();
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        for stage in STAGES {
            assert!(fx.contains_key(&format!("league_aatrox_chain:{stage}")), "{stage} not registered");
        }
        // 锁链碰到盖伦停在他前面 8000（往剑魔那边）
        let stop = (152_000.0, 0.0);
        let mut f = Flags::new();

        // 1. 锁住盖伦，他站着不动：圈心是锁链停下的地方；剑魔身上 w_tether、w_champ（数据当场和下一 tick 读）；
        //    第 90 tick 被拉回圈心，剑魔挂 w_pull、w_pull_c，数据在 READ_AT 读得到；本包不打伤害、不回血
        let mut w = world();
        chain_hits(&mut w, &fx, 1, Some(stop), InputTargetV1::target(1));
        assert!(has(&w, 1, &format!("{ON}:152000:0:0:{HOLD}")), "no chain mark on Garen at the chain's stop");
        assert!(has(&w, 0, TETHER) && has(&w, 0, CHAMP));
        run(&mut w, &fx, HOLD + 12, &mut f);
        assert!(flagged(&f, 1, TETHER), "the ring's flag is gone before the data reads it");
        assert!(!flagged(&f, HOLD - 1, PULL), "pulled before 1.5 s");
        for t in [HOLD, READ_AT] {
            assert!(flagged(&f, t, PULL) && flagged(&f, t, PULL_C), "no pull flags at tick {t}");
        }
        assert!((w.units[1].x - stop.0).abs() <= 1_500.0, "not pulled to the centre: {}", w.units[1].x);
        assert!(!has(&w, 1, ON));
        assert_eq!((w.damage, w.heals), (0, 0), "the add-on hit or healed itself (the data does it)");
        assert!(w.views.is_empty(), "the add-on played a picture itself (the data does them)");
        // 锁链一节节飞：每 LINK_EVERY tick 一节，从他脚下飞向圈心，两头都贴地（往下 LINK_DROP）
        assert_eq!(w.links.len(), HOLD / LINK_EVERY + 1);
        let drop = LINK_DROP as u64;
        assert!(w.links.iter().all(|l| l.2 == (stop.0 as u64, drop) && l.1 == (160_000, drop)));

        // 2. 盖伦往外走（每 tick 500，圈半径 33000）：走出圈锁链就断——不拉、不挂第二下的标记
        let mut w = world();
        let mut f = Flags::new();
        chain_hits(&mut w, &fx, 1, Some(stop), InputTargetV1::target(1));
        run_walking(&mut w, &fx, HOLD + 20, &[(1, 500.0)], &mut f);
        assert!(f.iter().all(|(_, v)| !v.iter().any(|n| n == PULL)), "the chain held although he left the ring");
        assert!(!has(&w, 1, ON) && w.pulls.is_empty());
        assert_eq!(viewed(&w, "league_aatrox_w_hit"), 1, "no chain-break picture");
        // 断在走出圈的那一 tick：圈心 152000，(185000 - 160000) / 500 = 50
        let broke = w.links.last().unwrap().0;
        assert!((44..=50).contains(&broke), "links until {broke}");
        assert!(AREA > 30_000.0);

        // 3. 往剑魔那边走（每 tick 300，1.5 秒 27000，圈心另一边还在圈里）：照样拉回圈心
        let mut w = world();
        let mut f = Flags::new();
        chain_hits(&mut w, &fx, 1, Some(stop), InputTargetV1::target(1));
        run_walking(&mut w, &fx, HOLD + 9, &[(1, -300.0)], &mut f);
        assert!(flagged(&f, READ_AT, PULL));
        assert!((w.units[1].x - stop.0).abs() <= 1_500.0, "not pulled back to the centre: {}", w.units[1].x);

        // 4. 第 40 tick 闪现出圈（瞬移 40000）：下一 tick 断
        let mut w = world();
        let mut f = Flags::new();
        chain_hits(&mut w, &fx, 1, Some(stop), InputTargetV1::target(1));
        run(&mut w, &fx, 40, &mut f);
        w.units[1].x += 40_000.0;
        run(&mut w, &fx, HOLD, &mut f);
        assert!(f.iter().all(|(_, v)| !v.iter().any(|n| n == PULL)));
        assert_eq!(viewed(&w, "league_aatrox_w_hit"), 1);

        // 5. 小兵：剑魔挂 w_minion（数据再打一下），不锁
        let mut w = world();
        chain_hits(&mut w, &fx, 2, Some((146_000.0, 0.0)), InputTargetV1::target(2));
        assert!(has(&w, 0, MINION) && !has(&w, 0, TETHER) && !has(&w, 0, CHAMP));
        assert!(!has(&w, 2, ON) && w.queue.is_empty());

        // 6. 野怪：锁、拉，挂 w_pull，不挂 w_champ / w_pull_c（吸血等只对英雄）
        let mut w = world();
        let mut f = Flags::new();
        chain_hits(&mut w, &fx, 3, Some((163_000.0, 0.0)), InputTargetV1::target(3));
        assert!(has(&w, 0, TETHER) && !has(&w, 0, CHAMP));
        run(&mut w, &fx, HOLD + 10, &mut f);
        assert!(flagged(&f, READ_AT, PULL) && !flagged(&f, READ_AT, PULL_C));
        assert!((w.units[3].x - 163_000.0).abs() <= 1_500.0);

        // 7. 韧性把拉回截短一半：结束后补推剩下的路，照样到圈心
        let mut w = world();
        let mut f = Flags::new();
        w.units[1].tenacity = true;
        chain_hits(&mut w, &fx, 1, Some(stop), InputTargetV1::target(1));
        run_walking(&mut w, &fx, 60, &[(1, 400.0)], &mut f);
        run(&mut w, &fx, HOLD, &mut f);
        let pushes = w.pulls.iter().filter(|p| p.0 == 1 && p.1.kind == CcKindV1::ForceMove.code()).count();
        assert!(pushes >= 2, "no second push ({pushes})");
        assert!((w.units[1].x - stop.0).abs() <= 1_500.0, "the drag did not finish: {}", w.units[1].x);
        assert!(!has(&w, 1, "league_aatrox_chain_drag"));

        // 8. 剑魔挂了：照样拉回，但不挂第二下的标记（数据的 Delayed 也跟着剑魔没了）
        let mut w = world();
        let mut f = Flags::new();
        chain_hits(&mut w, &fx, 1, Some(stop), InputTargetV1::target(1));
        w.units[0].alive = false;
        w.units[1].x += 10_000.0;
        run(&mut w, &fx, HOLD + 8, &mut f);
        assert!(!flagged(&f, READ_AT, PULL));
        assert!((w.units[1].x - stop.0).abs() <= 1_500.0);

        // 9. 盖伦在 1.5 秒内死了：什么都不再发生
        let mut w = world();
        let mut f = Flags::new();
        chain_hits(&mut w, &fx, 1, Some(stop), InputTargetV1::target(1));
        run(&mut w, &fx, 30, &mut f);
        w.units[1].alive = false;
        run(&mut w, &fx, HOLD, &mut f);
        assert!(w.queue.is_empty() && w.pulls.is_empty());

        // 10. 同一下又调一次 chain：不锁第二次
        let mut w = world();
        chain_hits(&mut w, &fx, 1, Some(stop), InputTargetV1::target(1));
        call(&mut w, &fx, "league_aatrox_chain:chain", 0, InputTargetV1::target(1));
        assert_eq!(w.units[1].buffs.iter().filter(|b| b.0.name().starts_with(ON)).count(), 1);
        assert_eq!(w.queue.len(), 1);

        // 11. 数据层给的是位置：找那附近刚被 W 减速的人（诺手没被减速，不算）
        let mut w = world();
        chain_hits(&mut w, &fx, 1, Some(stop), InputTargetV1::pos(161_000, 0));
        assert!(has(&w, 1, ON) && !has(&w, 4, ON));

        // 12. 场上找不到剑魔的锁链（已经没了）：圈心在他脚下往剑魔那边挪 3000
        let mut w = world();
        chain_hits(&mut w, &fx, 1, None, InputTargetV1::target(1));
        assert!(has(&w, 1, &format!("{ON}:157000:0:0:{HOLD}")));

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        assert!(text.starts_with("=== league_aatrox_chain v0.2"), "{text}");
        for line in [
            "TETHER Champion #1 league_garen at (160000,0) ring (152000,0) (the chain's stop; Aatrox (100000,0))",
            "TETHER Monster #3 rhino_monster",
            "PULL: 8000 from the centre, pulled in 4 ticks; the second hit flagged on Aatrox",
            "Aatrox is dead: no second hit",
            "BREAK: ",
            "DRAG: stopped",
            "died while chained",
            "no chain found: 3000 toward Aatrox",
        ] {
            assert!(text.contains(line), "missing {line:?} in the log:\n{text}");
        }
    }
}
