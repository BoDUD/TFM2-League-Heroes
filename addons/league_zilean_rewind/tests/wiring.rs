//! 走真实的导出入口，在一个迷你模拟里放基兰的时光符文：排队的效果到点触发，buff 按 tick 过期，
//! 伤害按「不死」把生命停在 1、按 `damaged_reduce` 100 免掉。检查致命伤害触发倒流（放逐、免伤、
//! 到时回血）、符文到期不回血、基兰死了照样倒流；以及索拉卡、凯尔不受影响：他们自己的「不死」
//! （索拉卡 W 的 `league_soraka_w_guard`、凯尔的 `league_kayle_probe_undying`）没有基兰符文时
//! 本包什么都不做，和符文叠在一起时等他们的「不死」结束才倒流。再跑被动 `guard`：R 待命时给快死的
//! 己方英雄（身边有敌人、残血或刚被打掉一大截）挂符文、播施法动作，没待命、没危险、敌人不在身边都不挂。

use std::collections::HashMap;
use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use league_zilean_rewind::{ARMED, HEAL, REWIND_T, RUNE, RUNE_T};
use mod_api_stable::*;

#[derive(Clone)]
struct Unit {
    name: &'static str,
    team: usize,
    x: f64,
    y: f64,
    alive: bool,
    hp: usize,
    ap: usize,
    buffs: Vec<(BuffV1, usize)>,
    cleared: usize,
}

fn unit(name: &'static str, team: usize) -> Unit {
    Unit { name, team, x: 0.0, y: 0.0, alive: true, hp: 1000, ap: 100, buffs: vec![], cleared: 0 }
}

#[derive(Default)]
struct World {
    tick: usize,
    units: Vec<Unit>,
    queue: Vec<(usize, String, usize, InputTargetV1)>,
    banished: Vec<(usize, usize, usize, String, String)>,
    heals: Vec<(usize, usize, usize)>,
    views: Vec<String>,
    sounds: Vec<String>,
    anims: Vec<String>,
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
    *out = SimOriginV1 { kind: SimOriginKindV1::ClientMatchView.code(), match_id: 3, set_index: 1, ..Default::default() };
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
unsafe extern "C" fn hp(s: *const c_void, h: EntityHandleV1, now: *mut usize, max: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*now, *max) = (e.hp, 1000);
    true
}
unsafe extern "C" fn stat(s: *const c_void, h: EntityHandleV1, out: *mut StatV1) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*out).magic_power = e.ap;
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
unsafe extern "C" fn clear_cc(s: *mut c_void, h: EntityHandleV1) -> usize {
    let Some(e) = u(s, h) else { return 0 };
    e.cleared += 1;
    1
}
#[allow(clippy::too_many_arguments)]
unsafe extern "C" fn banish(
    s: *mut c_void,
    caster: usize,
    h: EntityHandleV1,
    ticks: usize,
    lock: *const u8,
    lock_len: usize,
    end: *const u8,
    end_len: usize,
) -> bool {
    let world = w(s);
    world.banished.push((caster, h.id().unwrap(), ticks, text(lock, lock_len).into(), text(end, end_len).into()));
    true
}
unsafe extern "C" fn heal(s: *mut c_void, caster: usize, target: usize, amount: usize) {
    let world = w(s);
    world.heals.push((caster, target, amount));
    if let Some(e) = world.units.get_mut(target) {
        e.hp = (e.hp + amount).min(1000);
    }
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
    w(s).views.push(text(n, len).into());
    true
}
unsafe extern "C" fn sfx(s: *mut c_void, n: *const u8, len: usize, _: usize, _: *const InputTargetV1) -> bool {
    w(s).sounds.push(text(n, len).into());
    true
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*x, *y) = (e.x as u64, e.y as u64);
    true
}
unsafe extern "C" fn apply_cc(s: *mut c_void, _: usize, cc: *const CcV1) {
    let cc = *cc;
    if cc.kind == CcKindV1::Animation.code() {
        w(s).anims.push(cc.name().to_string());
    }
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
    vt.entity_is_targetable = Some(alive);
    vt.entity_pos = Some(pos);
    vt.apply_cc = Some(apply_cc);
    vt.entity_team = Some(team);
    vt.entity_hp = Some(hp);
    vt.entity_stat = Some(stat);
    vt.entity_name = Some(name);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.queue_effect = Some(queue_effect);
    vt.entity_clear_cc = Some(clear_cc);
    vt.entity_banish = Some(banish);
    vt.heal = Some(heal);
    vt.play_view_effect = Some(view_effect);
    vt.play_sfx = Some(sfx);
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

unsafe fn run(world: &mut World, fx: &Effects, n: usize) {
    run_with(world, fx, None, n);
}

/// 同上，每 tick 先调一次基兰（#0）的被动。
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
        for e in world.units.iter_mut() {
            e.buffs.iter_mut().for_each(|b| b.1 = b.1.saturating_sub(1));
            e.buffs.retain(|b| b.1 > 0);
        }
        world.tick += 1;
    }
}

/// 一下打 `dmg`：`damaged_reduce` 100 全免，有「不死」时生命停在 1，否则可能阵亡。
fn hit(world: &mut World, id: usize, dmg: usize) {
    let e = &mut world.units[id];
    if e.buffs.iter().any(|b| b.0.damaged_reduce >= 100) {
        return;
    }
    if e.buffs.iter().any(|b| b.0.undying) {
        e.hp = e.hp.saturating_sub(dmg).max(1);
    } else if dmg >= e.hp {
        e.hp = 0;
        e.alive = false;
    } else {
        e.hp -= dmg;
    }
}

/// 主包挂符文：AddBuff 符文（不死，300 tick），然后调本包的 rune（目标是被保护者）。
unsafe fn place_rune(world: &mut World, fx: &Effects, zilean: usize, target: usize) {
    let mut rune = BuffV1::timed(RUNE, RUNE_T);
    rune.undying = true;
    world.units[target].buffs.push((rune, RUNE_T));
    call(world, fx, "league_zilean_rewind:rune", zilean, InputTargetV1::target(target));
}

fn undying(name: &str, ticks: usize) -> (BuffV1, usize) {
    let mut b = BuffV1::timed(name, ticks);
    b.undying = true;
    (b, ticks)
}

fn has(world: &World, id: usize, prefix: &str) -> bool {
    world.units[id].buffs.iter().any(|b| b.0.name().starts_with(prefix))
}

/// 基兰 #0（法强 100），队友 #1 盖伦、#2 索拉卡、#3 凯尔，敌人 #4。
fn world() -> World {
    World {
        units: vec![
            unit("league_zilean", 0),
            unit("league_garen", 0),
            unit("league_soraka", 0),
            unit("league_kayle", 0),
            unit("league_darius", 1),
        ],
        ..Default::default()
    }
}

#[test]
fn chronoshift_rewinds_lethal_damage_and_leaves_soraka_and_kayle_alone() {
    let log = std::env::temp_dir().join("league_zilean_rewind_test.log");
    std::env::set_var("LEAGUE_ZILEAN_REWIND_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_zilean_rewind::tfm2_mod_entry_stable(&host);
        let _ = std::panic::take_hook();
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        let heal = HEAL + 100 * 150 / 100;

        // 1. 盖伦挂上符文，第 20 tick 吃到致命一击：生命停在 1，下一 tick 倒流——
        //    符文去掉、免伤不死、清控制、放逐 REWIND_T（倒流的画面）、到时回血 400 + 150% 法强
        let mut w = world();
        place_rune(&mut w, &fx, 0, 1);
        run(&mut w, &fx, 20);
        hit(&mut w, 1, 5000);
        assert!(w.units[1].alive && w.units[1].hp == 1);
        run(&mut w, &fx, 2);
        assert_eq!(w.banished, [(0, 1, REWIND_T, "league_zilean_r_rewind".into(), "league_zilean_r_cast".into())]);
        assert!(has(&w, 1, "league_zilean_rw_hold") && w.units[1].cleared == 1);
        hit(&mut w, 1, 5000);
        assert_eq!(w.units[1].hp, 1, "no damage while rewinding");
        assert!(w.heals.is_empty());
        run(&mut w, &fx, REWIND_T + 2);
        assert_eq!(w.heals, [(0, 1, heal)]);
        assert_eq!(w.units[1].hp, 1 + heal);
        assert!(!has(&w, 1, "league_zilean_rw_hold") && !has(&w, 1, RUNE));
        assert!(w.views.contains(&"league_zilean_r_rewind".to_string()));
        // 复活后就是普通状态：再吃致命一击就阵亡
        hit(&mut w, 1, 5000);
        assert!(!w.units[1].alive);

        // 2. 符文 5 秒没用上：到期什么都不发生，不回血（同 League）
        let mut w = world();
        place_rune(&mut w, &fx, 0, 1);
        run(&mut w, &fx, RUNE_T + 10);
        assert!(w.heals.is_empty() && w.banished.is_empty());
        assert!(!has(&w, 1, "league_zilean_rw"));

        // 3. 基兰挂完符文就阵亡了：倒流照样发生，回血按挂符文时的法强算，算盖伦自己的
        let mut w = world();
        place_rune(&mut w, &fx, 0, 1);
        w.units[0].alive = false;
        run(&mut w, &fx, 5);
        hit(&mut w, 1, 5000);
        run(&mut w, &fx, REWIND_T + 5);
        assert_eq!(w.heals, [(1, 1, heal)]);

        // 4. 索拉卡没有符文：她 W 自己的 3 tick「不死」把生命停在 1，本包什么都不做
        let mut w = world();
        w.units[2].buffs.push(undying("league_soraka_w_guard", 3));
        hit(&mut w, 2, 5000);
        run(&mut w, &fx, 30);
        assert!(w.banished.is_empty() && w.heals.is_empty() && w.queue.is_empty());
        assert!(w.units[2].alive && w.units[2].hp == 1 && w.units[2].buffs.is_empty());

        // 5. 凯尔没有符文：她的 2 tick「不死」探测同样不受影响
        let mut w = world();
        w.units[3].buffs.push(undying("league_kayle_probe_undying", 2));
        hit(&mut w, 3, 5000);
        run(&mut w, &fx, 30);
        assert!(w.banished.is_empty() && w.heals.is_empty() && w.units[3].alive);

        // 6. 符文和凯尔的「不死」叠在一起：凯尔的还在时不倒流（他本来就死不了），结束后才倒流
        let mut w = world();
        place_rune(&mut w, &fx, 0, 3);
        run(&mut w, &fx, 10);
        w.units[3].buffs.push(undying("league_kayle_probe_undying", 4));
        hit(&mut w, 3, 5000);
        run(&mut w, &fx, 3);
        assert!(w.banished.is_empty(), "rewound while Kayle's own undying still held");
        run(&mut w, &fx, 4);
        assert_eq!(w.banished.len(), 1);
        assert_eq!(w.banished[0].1, 3);

        // 7. 基兰给索拉卡挂符文 + 她 W 的「不死」：同上，等 W 的结束
        let mut w = world();
        place_rune(&mut w, &fx, 0, 2);
        run(&mut w, &fx, 10);
        w.units[2].buffs.push(undying("league_soraka_w_guard", 3));
        hit(&mut w, 2, 5000);
        run(&mut w, &fx, 2);
        assert!(w.banished.is_empty());
        run(&mut w, &fx, 4);
        assert_eq!(w.banished.len(), 1);
        run(&mut w, &fx, REWIND_T + 2);
        assert_eq!(w.heals, [(0, 2, heal)]);
        assert!(w.units[2].alive);

        // 9. 基兰给自己挂符文（被两个人贴身时）：自己倒流、自己回血
        let mut w = world();
        place_rune(&mut w, &fx, 0, 0);
        hit(&mut w, 0, 5000);
        run(&mut w, &fx, REWIND_T + 3);
        assert_eq!(w.banished[0].1, 0);
        assert_eq!(w.heals, [(0, 0, heal)]);

        // 8. 对同一人再调一次 rune：不开第二条链
        let mut w = world();
        place_rune(&mut w, &fx, 0, 1);
        call(&mut w, &fx, "league_zilean_rewind:rune", 0, InputTargetV1::target(1));
        assert_eq!(w.queue.len(), 1);

        // 10. 被动 guard：基兰 #0 在 (0,0)，盖伦 #1 在 (50000,0)，诺手 #4 在他身边 (80000,0)
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        let names: Vec<&str> = passives.iter().map(|p| p.name.as_str()).collect();
        assert_eq!(names, ["league_zilean_rewind:guard"]);
        let proto = &passives[0].passive;
        let fresh = || PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let fight = |garen_hp: usize, armed: bool| {
            let mut w = world();
            (w.units[1].x, w.units[4].x) = (50_000.0, 80_000.0);
            w.units[2].x = -200_000.0;
            w.units[3].x = -200_000.0;
            w.units[1].hp = garen_hp;
            if armed {
                w.units[0].buffs.push((BuffV1::timed(ARMED, 900), 900));
            }
            w
        };
        // 待命、盖伦 25%、敌人贴着他：挂符文，播施法，去掉待命；接着致命一击 → 倒流 → 复活
        let g = fresh();
        let mut w = fight(250, true);
        run_with(&mut w, &fx, Some(&g), 4);
        assert!(has(&w, 1, RUNE) && has(&w, 1, "league_zilean_rw_watch"), "no rune on Garen");
        assert!(!has(&w, 0, ARMED), "the armed R was not used up");
        assert_eq!(w.anims, ["skill"]);
        for snd in ["league_zilean_r_rune", "league_zilean_r_cast"] {
            assert!(w.sounds.iter().any(|x| x == snd), "{snd}");
        }
        assert!(w.views.iter().any(|x| x == "league_zilean_r_cast"));
        hit(&mut w, 1, 5000);
        run_with(&mut w, &fx, Some(&g), REWIND_T + 5);
        assert_eq!(w.banished.len(), 1);
        assert_eq!(w.heals, [(0, 1, heal)]);
        assert_eq!(w.anims, ["skill"], "a second R while the first was used");
        // 没待命（R 在冷却或 AI 还没放）：不挂
        let mut w = fight(250, false);
        run_with(&mut w, &fx, Some(&fresh()), 30);
        assert!(!has(&w, 1, RUNE) && w.anims.is_empty());
        // 盖伦满血：不挂；敌人离他 100000：不挂
        let mut w = fight(1000, true);
        run_with(&mut w, &fx, Some(&fresh()), 30);
        assert!(!has(&w, 1, RUNE) && has(&w, 0, ARMED));
        let mut w = fight(250, true);
        w.units[4].x = 150_000.0;
        run_with(&mut w, &fx, Some(&fresh()), 30);
        assert!(!has(&w, 1, RUNE));
        // 一秒内从 90% 被打到 50%：挂
        let g = fresh();
        let mut w = fight(900, true);
        run_with(&mut w, &fx, Some(&g), 12);
        assert!(!has(&w, 1, RUNE));
        w.units[1].hp = 500;
        run_with(&mut w, &fx, Some(&g), 4);
        assert!(has(&w, 1, RUNE), "missed the burst");
        // 基兰自己 20%、诺手贴着他：给自己挂
        let mut w = fight(1000, true);
        w.units[0].hp = 200;
        w.units[4].x = 20_000.0;
        run_with(&mut w, &fx, Some(&fresh()), 4);
        assert!(has(&w, 0, RUNE) && !has(&w, 1, RUNE));

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        assert!(text.starts_with("=== league_zilean_rewind v2"), "{text}");
        for line in [
            "RUNE from #0 league_zilean",
            "REWIND: lethal damage caught at 1 hp, banished",
            "REVIVE: healed 550",
            "rune ended unused: no heal",
            "GUARD: rune on #1 league_garen (hp 25%, lost 0% in 60 ticks, enemy champion 30000 away)",
            "GUARD: rune on #1 league_garen (hp 50%, lost 40% in 60 ticks",
            "GUARD: rune on #0 league_zilean (hp 20%",
        ] {
            assert!(text.contains(line), "missing {line:?} in the log:\n{text}");
        }
    }
}
