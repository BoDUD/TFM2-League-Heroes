//! 走真实的导出入口：在一个迷你模拟里放魔腾的 R，检查黑暗期间每 tick 隐身的是「身边没有敌方英雄」的
//! 己方英雄、贴近的看得见、到时结束；地图暗色是在模拟里播的特效（地图中心，叠 3 层、错开几 tick），
//! 服务端预模拟和你看的那场一样（播不播由游戏决定），没开 R 时一层也不播；不再注册客户端扩展。

use std::collections::HashMap;
use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use league_nocturne_dark::{DARK_T, MAP_CENTER, VEIL, VEIL_LAYERS, VEIL_STEP};
use mod_api_stable::*;

struct Unit {
    x: f64,
    y: f64,
    team: usize,
    buffs: Vec<(BuffV1, usize)>,
}

#[derive(Default)]
struct World {
    tick: usize,
    view: bool,
    units: Vec<Unit>,
    queue: Vec<(usize, String, usize, InputTargetV1)>,
    /// 每 tick 隐身了谁。
    hidden: HashMap<usize, Vec<usize>>,
    /// 播过的特效：(tick, 名字, 施放者, 目标)。
    views: Vec<(usize, String, usize, InputTargetV1)>,
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
unsafe extern "C" fn origin(s: *const c_void, out: *mut SimOriginV1) -> bool {
    let kind = if w(s).view { SimOriginKindV1::ClientMatchView } else { SimOriginKindV1::ServerPresim };
    *out = SimOriginV1 { kind: kind.code(), match_id: 9, set_index: 0, ..Default::default() };
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
    (*x, *y) = (e.x as u64, e.y as u64);
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
unsafe extern "C" fn invisible(s: *mut c_void, h: EntityHandleV1, ticks: usize) -> bool {
    assert_eq!(ticks, 2);
    let world = w(s);
    world.hidden.entry(world.tick).or_default().push(h.id().unwrap());
    true
}
unsafe extern "C" fn view_effect(
    s: *mut c_void,
    n: *const u8,
    len: usize,
    caster: usize,
    input: *const InputTargetV1,
    _: u64,
    _: u64,
    _: u64,
) -> bool {
    let world = w(s);
    world.views.push((world.tick, text(n, len).to_string(), caster, *input));
    true
}
unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}
// 玩家 k 的英雄就是单位 k
unsafe extern "C" fn player_is_valid(s: *const c_void, h: PlayerHandleV1) -> bool {
    h.id().is_some_and(|k| k < w(s).units.len())
}
unsafe extern "C" fn player_champion(_: *const c_void, h: PlayerHandleV1) -> EntityHandleV1 {
    h.id().map_or(EntityHandleV1::NULL, EntityHandleV1::from_id)
}

fn vtable() -> SimVtableV1 {
    let mut vt: SimVtableV1 = unsafe { zeroed() };
    vt.size = size_of::<SimVtableV1>();
    vt.tick = Some(tick);
    vt.sim_origin = Some(origin);
    vt.entity_count = Some(count);
    vt.entity_at = Some(at);
    vt.entity_is_valid = Some(yes);
    vt.entity_is_alive = Some(yes);
    vt.entity_is_champion = Some(yes);
    vt.entity_team = Some(team);
    vt.entity_pos = Some(pos);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.queue_effect = Some(queue_effect);
    vt.entity_set_invisible = Some(invisible);
    vt.play_view_effect = Some(view_effect);
    vt.player_is_valid = Some(player_is_valid);
    vt.player_champion = Some(player_champion);
    vt
}

type Effects<'a> = HashMap<String, &'a NativeEffectRegV1>;

unsafe fn call(world: &mut World, fx: &Effects, name: &str, caster: usize) {
    let vt = vtable();
    let mut ctx =
        SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(), state: world as *mut World as *mut c_void };
    let e = fx[name].effect;
    ((*e.vtable).apply.unwrap())(e.userdata, &mut ctx, 0, caster, &InputTargetV1::target(caster));
}

unsafe fn run(world: &mut World, fx: &Effects, n: usize) {
    for _ in 0..n {
        while let Some(i) = world.queue.iter().position(|q| q.0 <= world.tick) {
            let (_, name, caster, _) = world.queue.remove(i);
            call(world, fx, &name, caster);
        }
        for e in world.units.iter_mut() {
            e.buffs.iter_mut().for_each(|b| b.1 = b.1.saturating_sub(1));
            e.buffs.retain(|b| b.1 > 0);
        }
        world.tick += 1;
    }
}

/// 魔腾 #0 和队友 #1（身边 30000 有敌人 #3）、#2（附近没人）；敌人 #3、#4。
fn world(view: bool) -> World {
    let unit = |x: f64, y: f64, team: usize| Unit { x, y, team, buffs: vec![] };
    World {
        view,
        units: vec![
            unit(100_000.0, 800_000.0, 0),
            unit(400_000.0, 400_000.0, 0),
            unit(800_000.0, 200_000.0, 0),
            unit(430_000.0, 400_000.0, 1),
            unit(600_000.0, 600_000.0, 1),
        ],
        ..Default::default()
    }
}

/// The add-on resolves its log path once per process (a LazyLock), so every test logs to the same file: one at a time
/// (the lock), the file cleared first, so each test reads only its own lines.
fn test_log() -> (std::sync::MutexGuard<'static, ()>, std::path::PathBuf) {
    static SERIAL: std::sync::Mutex<()> = std::sync::Mutex::new(());
    let guard = SERIAL.lock().unwrap_or_else(|e| e.into_inner());
    let log = std::env::temp_dir().join("league_nocturne_dark_test.log");
    std::env::set_var("LEAGUE_NOCTURNE_DARK_LOG", &log);
    let _ = std::fs::remove_file(&log);
    (guard, log)
}

#[test]
fn paranoia_hides_the_team_and_veils_the_map_in_the_sim() {
    let (_serial, log) = test_log();
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_nocturne_dark::tfm2_mod_entry_stable(&host);
        let _ = std::panic::take_hook();
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        assert!(ex.extension.vtable.is_null(), "v2 draws nothing from the client");

        for view in [false, true] {
            // 没开 R：一层暗色也不播
            let mut idle = world(view);
            run(&mut idle, &fx, 400);
            assert!(idle.views.is_empty() && idle.hidden.is_empty(), "darkness without the R");

            // 开 R：#0、#2 每 tick 隐身，#1 身边有敌人看得见；DARK_T 后结束
            let mut w = world(view);
            call(&mut w, &fx, "league_nocturne_dark:start", 0);
            for t in 0..DARK_T {
                run(&mut w, &fx, 1);
                assert_eq!(w.hidden.get(&t).cloned().unwrap_or_default(), [0, 2], "tick {t}");
            }
            run(&mut w, &fx, 30);
            assert!((DARK_T + 2..DARK_T + 30).all(|t| !w.hidden.contains_key(&t)), "still hidden after the darkness");
            assert!(w.queue.is_empty());

            // 地图暗色：地图中心，叠 VEIL_LAYERS 层、每层隔 VEIL_STEP tick，之后不再播
            let ticks: Vec<usize> = w.views.iter().map(|v| v.0).collect();
            assert_eq!(ticks, (0..VEIL_LAYERS).map(|k| k * VEIL_STEP).collect::<Vec<_>>());
            for (_, name, caster, at) in &w.views {
                assert_eq!((name.as_str(), *caster), (VEIL, 0));
                assert_eq!(at.kind, InputTargetKindV1::Pos.code());
                assert_eq!((at.x, at.y), MAP_CENTER);
            }
        }

        // 黑暗中再开一次 R（重置时长）：重新叠一遍暗色，黑暗从第二次算起
        let mut w = world(true);
        call(&mut w, &fx, "league_nocturne_dark:start", 0);
        run(&mut w, &fx, 100);
        call(&mut w, &fx, "league_nocturne_dark:start", 0);
        run(&mut w, &fx, DARK_T - 2);
        assert!(w.hidden.contains_key(&(100 + DARK_T - 3)), "the second R did not reset the darkness");
        assert_eq!(w.views.len(), 2 * VEIL_LAYERS);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        assert!(text.starts_with(&format!("=== league_nocturne_dark v{}", env!("CARGO_PKG_VERSION"))), "{text}");
        assert!(text.contains("DARKNESS for 180 ticks: 2 of 3 allies unseen"), "{text}");
        assert!(text.contains("darkness over"), "{text}");
    }
}

// ===================== 鬼影重重：AI 钩子 =====================

/// AI 钩子看到的「这个玩家」：玩家 id 和队伍。
struct Me {
    player: usize,
    team: usize,
}
unsafe extern "C" fn ai_player(s: *const c_void) -> usize {
    (*(s as *const Me)).player
}
unsafe extern "C" fn ai_team(s: *const c_void) -> usize {
    (*(s as *const Me)).team
}

/// 让导出的 AI 钩子替玩家 `player` 想一 tick：返回替换后的输入（`None` = 照原样）。
unsafe fn think(world: &mut World, ai: &PlayerAiRegV1, player: usize, base: InputV1) -> Option<InputV1> {
    let vt = vtable();
    let mut avt: AiVtableV1 = zeroed();
    avt.size = size_of::<AiVtableV1>();
    avt.player_id = Some(ai_player);
    avt.team = Some(ai_team);
    let mut me = Me { player, team: world.units[player].team };
    let mut ctx = AiCtxV1 {
        size: size_of::<AiCtxV1>(),
        vtable: &avt,
        state: &mut me as *mut Me as *mut c_void,
        sim: &vt,
        sim_state: world as *mut World as *mut c_void,
    };
    let mut out = InputV1::default();
    let code = ((*ai.vtable).think.unwrap())(ai.userdata, &mut ctx, &base, &mut out);
    (code == AiDecisionKindV1::Replace.code()).then_some(out)
}

#[test]
fn in_the_dark_enemies_hit_only_what_is_near() {
    let (_serial, log) = test_log();
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_nocturne_dark::tfm2_mod_entry_stable(&host);
        let _ = std::panic::take_hook();
        let regs = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len);
        let fx: Effects = regs.iter().map(|e| (e.name.as_str().to_string(), e)).collect();
        let ais = std::slice::from_raw_parts(ex.player_ai_ptr, ex.player_ai_len);
        assert_eq!(ais.len(), 1, "one player AI hook");
        let ai = &ais[0];

        let attack = |id: usize| InputV1::action(InputKindV1::Attack, InputTargetV1::target(id));
        let walk_to = |id: usize, w: &World| InputV1::move_to(w.units[id].x as u64, w.units[id].y as u64);
        let mut w = world(true);
        // 没开 R：敌人 #4 打 28 万外的 #1 照常
        assert_eq!(think(&mut w, ai, 4, attack(1)), None);

        call(&mut w, &fx, "league_nocturne_dark:start", 0);
        run(&mut w, &fx, 1);
        // 黑暗里：#4 离 #1 28 万，看不见 -> 改成走过去；#3 离 #1 3 万，照常打
        assert_eq!(think(&mut w, ai, 4, attack(1)), Some(walk_to(1, &w)));
        assert_eq!(think(&mut w, ai, 3, attack(1)), None);
        // 指向 #1 旁边一个点的技能、指着 #2 方向的技能：也走过去
        let at_point = InputV1::action(InputKindV1::Skill, InputTargetV1::pos(402_000, 401_000));
        assert_eq!(think(&mut w, ai, 4, at_point), Some(walk_to(1, &w)));
        // (#4 走到离 #2 约 11.7 万的地方，朝 #2 甩；15 万外的不算瞄着)
        let home = (w.units[4].x, w.units[4].y);
        (w.units[4].x, w.units[4].y) = (700_000.0, 260_000.0);
        let mut toward = InputV1::action(InputKindV1::Skill2, InputTargetV1::NONE);
        toward.target.kind = InputTargetKindV1::Dir.code();
        (toward.target.dir_x, toward.target.dir_y) = (100_000, -60_000);
        assert_eq!(think(&mut w, ai, 4, toward), Some(walk_to(2, &w)));
        (w.units[4].x, w.units[4].y) = home;
        (toward.target.dir_x, toward.target.dir_y) = (200_000, -400_000);
        assert_eq!(think(&mut w, ai, 4, toward), None, "a direction toward a unit 45 万 away aims at nothing");
        // 走路、回城、打别的队伍的不管；魔腾一方自己的玩家也不管
        assert_eq!(think(&mut w, ai, 4, InputV1::move_to(1, 2)), None);
        assert_eq!(think(&mut w, ai, 4, InputV1::return_home()), None);
        assert_eq!(think(&mut w, ai, 4, attack(3)), None);
        assert_eq!(think(&mut w, ai, 1, attack(4)), None);

        // 黑暗过去：照常
        run(&mut w, &fx, DARK_T + 5);
        assert_eq!(think(&mut w, ai, 4, attack(1)), None);

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        assert!(text.contains("PARANOIA: player 4 Attack out of sight"), "{text}");
    }
}

