//! 走真实的导出入口，在一个迷你模拟里放剑魔的 W：排队的效果到点触发，buff 按 tick 过期，强制位移按
//! 方向和速度每 tick 挪人（`tenacity` 的单位只走一半的 tick）。检查 League 的规则：只锁打中的那个人；
//! 待在圈里 1.5 秒后被拉回圈心（比原地稍微靠近剑魔）、再受一次伤害，剑魔吸血、记被动；走出圈、闪现出圈
//! 锁链就断，什么都不发生；小兵当场再受一次伤害（双倍），不锁；野怪锁、拉，不吸血；大灭期间第二下打死人记击杀；
//! 被韧性截短的拉回会补推；剑魔死了照样拉；同一个人不锁两次；数据层给的是位置时找刚被减速的那个人。

use std::collections::HashMap;
use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use league_aatrox_chain::{AREA, CENTER_IN, HOLD, LINK_EVERY, ON, PC_HOLD};
use mod_api_stable::*;

#[derive(Clone)]
struct Unit {
    name: &'static str,
    team: usize,
    x: f64,
    y: f64,
    alive: bool,
    hp: usize,
    attack: usize,
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
        hp: 1000,
        attack: 100,
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
    queue: Vec<(usize, String, usize, InputTargetV1)>,
    damage: Vec<(usize, usize, usize, usize)>,
    heals: Vec<(usize, usize, usize)>,
    views: Vec<(String, InputTargetV1)>,
    sounds: Vec<String>,
    links: Vec<(usize, (u64, u64), (u64, u64))>,
    pulls: Vec<(usize, CcV1)>,
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
unsafe extern "C" fn hp(s: *const c_void, h: EntityHandleV1, now: *mut usize, max: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*now, *max) = (e.hp, 1000);
    true
}
unsafe extern "C" fn stat(s: *const c_void, h: EntityHandleV1, out: *mut StatV1) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*out).attack = e.attack;
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
unsafe extern "C" fn heal(s: *mut c_void, caster: usize, target: usize, amount: usize) {
    let world = w(s);
    world.heals.push((caster, target, amount));
}
unsafe extern "C" fn deal_damage(s: *mut c_void, attacker: usize, target: usize, ad: usize, _: usize, _: u32) {
    let world = w(s);
    let tick = world.tick;
    world.damage.push((tick, attacker, target, ad));
    if let Some(e) = world.units.get_mut(target) {
        if ad >= e.hp {
            e.hp = 0;
            e.alive = false;
        } else {
            e.hp -= ad;
        }
    }
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
    vt.entity_hp = Some(hp);
    vt.entity_stat = Some(stat);
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

/// `n` tick：每 tick `walk` 里的人先走一步，再跑到点的效果、强制位移挪人、buff 和控制过期。
unsafe fn run_walking(world: &mut World, fx: &Effects, n: usize, walk: &[(usize, f64)]) {
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
            e.ccs.iter_mut().for_each(|c| c.1 = c.1.saturating_sub(1));
            e.ccs.retain(|c| c.1 > 0);
            e.buffs.iter_mut().for_each(|b| b.1 = b.1.saturating_sub(1));
            e.buffs.retain(|b| b.1 > 0);
        }
        world.tick += 1;
    }
}

unsafe fn run(world: &mut World, fx: &Effects, n: usize) {
    run_walking(world, fx, n, &[]);
}

/// 主包的锁链打中 `target`：第一下的伤害、1.5 秒减速，然后调本包的 chain（目标是被打中的单位）。
unsafe fn chain_hits(world: &mut World, fx: &Effects, target: usize, input: InputTargetV1) {
    let tick = world.tick;
    world.damage.push((tick, 0, target, 80));
    world.units[target].buffs.push((BuffV1::timed("league_aatrox_w_slowed", HOLD), HOLD));
    call(world, fx, "league_aatrox_chain:chain", 0, input);
}

fn has(world: &World, id: usize, prefix: &str) -> bool {
    world.units[id].buffs.iter().any(|b| b.0.name().starts_with(prefix))
}

fn hits_on(world: &World, id: usize) -> Vec<(usize, usize)> {
    world.damage.iter().filter(|d| d.2 == id).map(|d| (d.0, d.3)).collect()
}

fn viewed(world: &World, name: &str) -> usize {
    world.views.iter().filter(|v| v.0 == name).count()
}

/// 剑魔 #0 在 (100000, 0)，攻击 100；敌方英雄 #1 盖伦在 (160000, 0)，小兵 #2、野怪 #3、敌方英雄 #4 诺手。
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
        for stage in league_aatrox_chain::STAGES {
            assert!(fx.contains_key(&format!("league_aatrox_chain:{stage}")), "{stage} not registered");
        }
        let center = 160_000.0 - CENTER_IN;

        // 1. 锁住盖伦，他站着不动：圈心在他往剑魔那边 3000；第 90 tick 再受 80（40 + 40% 攻击 100），
        //    被拉回圈心，剑魔回 14（80 的 18%），欠被动一次（pc1）；旁边的诺手什么都没有
        let mut w = world();
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        assert!(has(&w, 1, &format!("{ON}:{}:0:0:{HOLD}", center as u64)), "no chain mark on Garen");
        assert_eq!(viewed(&w, "league_aatrox_w_ring_in"), 1);
        assert!(w.sounds.contains(&"league_aatrox_w_ring".to_string()));
        run(&mut w, &fx, HOLD);
        assert_eq!(hits_on(&w, 1), [(0, 80)], "hit again before 1.5 s");
        run(&mut w, &fx, 1);
        assert_eq!(hits_on(&w, 1), [(0, 80), (HOLD, 80)]);
        assert!(hits_on(&w, 4).is_empty(), "Darius next to him was hit");
        // 两下都打中英雄：各回 14（7 + 7% 攻击 100），各欠被动一次（pc1、pc2）
        assert_eq!(w.heals, [(0, 0, 14), (0, 0, 14)]);
        assert!(has(&w, 0, "league_aatrox_pc1") && has(&w, 0, "league_aatrox_pc2"));
        // 欠条 900 tick（加上的那一 tick 末已经走了 1）
        assert_eq!(w.units[0].buffs.iter().find(|b| b.0.name() == "league_aatrox_pc2").unwrap().1, PC_HOLD - 1);
        assert_eq!(viewed(&w, "league_aatrox_w_snap"), 1);
        assert_eq!(viewed(&w, "league_aatrox_w_yank"), 1);
        assert!(w.sounds.contains(&"league_aatrox_w_yank".to_string()));
        run(&mut w, &fx, 10);
        assert!((w.units[1].x - center).abs() <= 1_500.0, "not pulled to the centre: {}", w.units[1].x);
        assert!(!has(&w, 1, ON));
        // 锁链一节节飞：每 LINK_EVERY tick 一节，从他脚下飞向圈心；圈 4 次补播
        assert_eq!(w.links.len(), HOLD / LINK_EVERY + 1);
        assert!(w.links.iter().all(|l| l.2 == (center as u64, 0)));
        assert_eq!(viewed(&w, "league_aatrox_w_ring_beat"), 4);

        // 2. 盖伦往外走（每 tick 500，圈半径 33000）：走出圈锁链就断——不拉、不再打，碎链的画面和声音
        let mut w = world();
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        run_walking(&mut w, &fx, HOLD + 20, &[(1, 500.0)]);
        assert_eq!(hits_on(&w, 1), [(0, 80)], "the chain held although he left the ring");
        assert!(w.heals == [(0, 0, 14)] && !has(&w, 1, ON) && !has(&w, 0, "league_aatrox_pc2"));
        assert_eq!(viewed(&w, "league_aatrox_w_hit"), 1);
        assert_eq!(viewed(&w, "league_aatrox_w_snap"), 0);
        // 断在走出圈的那一 tick：(33000 - 3000) / 500 = 60
        let broke = w.links.last().unwrap().0;
        assert!((56..=61).contains(&broke), "links until {broke}");

        // 3. 往剑魔那边走（每 tick 300，1.5 秒 27000 < 圈的另一边 36000）：还在圈里，照样拉回圈心
        let mut w = world();
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        run_walking(&mut w, &fx, HOLD + 12, &[(1, -300.0)]);
        assert_eq!(hits_on(&w, 1).len(), 2);
        assert!((w.units[1].x - center).abs() <= 1_500.0, "not pulled back to the centre: {}", w.units[1].x);

        // 4. 第 40 tick 闪现出圈（瞬移 40000）：下一 tick 断
        let mut w = world();
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        run(&mut w, &fx, 40);
        w.units[1].x += 40_000.0;
        run(&mut w, &fx, HOLD);
        assert_eq!(hits_on(&w, 1).len(), 1);
        assert_eq!(viewed(&w, "league_aatrox_w_hit"), 1);

        // 5. 小兵：当场再受一次（双倍），不锁、不拉
        let mut w = world();
        chain_hits(&mut w, &fx, 2, InputTargetV1::target(2));
        assert_eq!(hits_on(&w, 2), [(0, 80), (0, 80)]);
        assert!(!has(&w, 2, ON) && w.queue.is_empty());
        run(&mut w, &fx, HOLD + 5);
        assert_eq!(hits_on(&w, 2).len(), 2);

        // 6. 野怪：锁、拉、再打，但不吸血、不记被动（主包只对英雄）
        let mut w = world();
        chain_hits(&mut w, &fx, 3, InputTargetV1::target(3));
        run(&mut w, &fx, HOLD + 12);
        assert_eq!(hits_on(&w, 3), [(0, 80), (HOLD, 80)]);
        assert!(w.heals.is_empty() && !has(&w, 0, "league_aatrox_pc"));
        assert!((w.units[3].x - (170_000.0 - CENTER_IN)).abs() <= 1_500.0);

        // 7. 大灭期间（攻击 125）第二下打死残血盖伦：吸血 ×1.5，记击杀（k_b 在、k_a 不在）
        let mut w = world();
        w.units[0].attack = 125;
        w.units[0].buffs.push((BuffV1::timed("league_aatrox_r", 600), 600));
        w.units[0].buffs.push((BuffV1::timed("league_aatrox_k_a", 2), 2));
        w.units[1].hp = 150;
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        w.units[1].hp = 60;
        run(&mut w, &fx, HOLD + 1);
        assert!(!w.units[1].alive);
        assert_eq!(hits_on(&w, 1).last(), Some(&(HOLD, 90)));
        assert_eq!(w.heals, [(0, 0, 22), (0, 0, 22)]);
        assert!(has(&w, 0, "league_aatrox_k_b") && !has(&w, 0, "league_aatrox_k_a"));
        // 没打死：不记击杀
        let mut w = world();
        w.units[0].buffs.push((BuffV1::timed("league_aatrox_r", 600), 600));
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        run(&mut w, &fx, HOLD + 3);
        assert!(!has(&w, 0, "league_aatrox_k_b"));

        // 8. 韧性把拉回截短一半：结束后补推剩下的路，照样到圈心
        let mut w = world();
        w.units[1].tenacity = true;
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        run_walking(&mut w, &fx, 60, &[(1, 400.0)]);
        run(&mut w, &fx, HOLD);
        assert_eq!(hits_on(&w, 1).len(), 2);
        let pushes = w.pulls.iter().filter(|p| p.0 == 1 && p.1.kind == CcKindV1::ForceMove.code()).count();
        assert!(pushes >= 2, "no second push ({pushes})");
        assert!(!has(&w, 1, "league_aatrox_chain_drag"));
        assert!((w.units[1].x - center).abs() <= 1_500.0, "the drag did not finish: {}", w.units[1].x);

        // 9. 剑魔挂了：照样拉、照样打（伤害算剑魔的），第二下不回血
        let mut w = world();
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        w.units[0].alive = false;
        run(&mut w, &fx, HOLD + 2);
        assert_eq!(hits_on(&w, 1).len(), 2);
        assert_eq!(w.heals, [(0, 0, 14)]);

        // 10. 盖伦在 1.5 秒内死了：什么都不再发生
        let mut w = world();
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        run(&mut w, &fx, 30);
        w.units[1].alive = false;
        run(&mut w, &fx, HOLD);
        assert_eq!(hits_on(&w, 1).len(), 1);
        assert!(w.queue.is_empty());

        // 11. 同一下又调一次 chain：不锁第二次
        let mut w = world();
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        call(&mut w, &fx, "league_aatrox_chain:chain", 0, InputTargetV1::target(1));
        assert_eq!(w.units[1].buffs.iter().filter(|b| b.0.name().starts_with(ON)).count(), 1);
        assert_eq!(w.queue.len(), 1);

        // 12. 数据层给的是位置：找那附近刚被 W 减速的人（诺手没被减速，不算）
        let mut w = world();
        chain_hits(&mut w, &fx, 1, InputTargetV1::pos(161_000, 0));
        assert!(has(&w, 1, ON) && !has(&w, 4, ON));

        // 13. 第一下就打死了（大灭期间）：照样吸血、记击杀，不锁
        let mut w = world();
        w.units[0].buffs.push((BuffV1::timed("league_aatrox_r", 600), 600));
        w.units[1].alive = false;
        w.units[1].hp = 0;
        chain_hits(&mut w, &fx, 1, InputTargetV1::target(1));
        assert_eq!(w.heals, [(0, 0, 20)]);
        assert!(has(&w, 0, "league_aatrox_k_b") && !has(&w, 1, ON) && w.queue.is_empty());

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        assert!(text.starts_with("=== league_aatrox_chain v0.1"), "{text}");
        for line in [
            "TETHER Champion #1 league_garen at (160000,0) ring (157000,0) (Aatrox (100000,0))",
            "TETHER Monster #3 rhino_monster",
            "PULL: 3000 from the centre, pulled in 2 ticks, hit 80 (1000 -> 920/1000), Aatrox heals 14, passive cut pc2",
            "chain hit killed #1 league_garen, Aatrox heals 20, passive cut pc1, KILL in World Ender",
            "BREAK: ",
            "KILL in World Ender",
            "DRAG: stopped",
            "died while chained",
        ] {
            assert!(text.contains(line), "missing {line:?} in the log:\n{text}");
        }
        assert!(AREA > 30_000.0);
    }
}
