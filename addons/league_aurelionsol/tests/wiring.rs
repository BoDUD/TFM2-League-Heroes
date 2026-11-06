//! 走真实的导出入口，在一个迷你模拟里试星穹流丽（league_leesin_hop 的做法）：被动每 tick 调一次（挪人、挂 buff），AI 钩子按
//! 一个基础输入想一次。检查：队友在打的敌方英雄在龙息外时起飞进场（挂上飞行、落点、目标、起飞星云，去掉龙息冷却，放音效和
//! 台词），每 tick 飞 2000、停在他前面 50000；够得着时钩子对他按龙息、够不着时把走路改成朝落点飞；喷龙息（主包的 `q_ch`）
//! 时飞得减半；飞向的那个倒下时龙息停、姿势清掉、全速飞完；落地后飞行中开始的龙息照地面的上限收、进冷却；残血时背离敌人飞满
//! 全程（逃生时不喷满血的追兵）；被晕住就落地；击杀返还剩下冷却的 90%；冷却里不再飞。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

struct Unit {
    x: f64,
    y: f64,
    team: usize,
    minion: bool,
    hp: usize,
    buffs: Vec<(BuffV1, usize)>,
    ccs: Vec<(CcV1, u64)>,
}

fn unit(x: f64, y: f64, team: usize) -> Unit {
    Unit { x, y, team, minion: false, hp: 1000, buffs: vec![], ccs: vec![] }
}

#[derive(Default)]
struct World {
    tick: usize,
    units: Vec<Unit>,
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
    *out = SimOriginV1 { kind: SimOriginKindV1::ClientMatchView.code(), match_id: 5, set_index: 0, ..Default::default() };
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
unsafe extern "C" fn yes(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
}
unsafe extern "C" fn no(_: *const c_void, _: EntityHandleV1) -> bool {
    false
}
unsafe extern "C" fn is_champion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| !e.minion)
}
unsafe extern "C" fn is_minion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.minion)
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
unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, n: *const u8, len: usize) -> usize {
    let name = text(n, len).to_string();
    let Some(e) = u(s, h) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.0.name() != name);
    before - e.buffs.len()
}
unsafe extern "C" fn clear_cc(s: *mut c_void, h: EntityHandleV1) -> usize {
    let Some(e) = u(s, h) else { return 0 };
    let n = e.ccs.len();
    e.ccs.clear();
    n
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
unsafe extern "C" fn visible(_: *const c_void, _: usize, _: usize) -> bool {
    true
}
unsafe extern "C" fn player_valid(_: *const c_void, h: PlayerHandleV1) -> bool {
    h.id() == Some(0)
}
unsafe extern "C" fn player_champion(_: *const c_void, h: PlayerHandleV1) -> EntityHandleV1 {
    EntityHandleV1::from_id(h.id().unwrap_or(0))
}
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
    vt.entity_is_valid = Some(valid);
    vt.entity_is_alive = Some(alive);
    vt.entity_is_champion = Some(is_champion);
    vt.entity_is_tower = Some(no);
    vt.entity_is_minion = Some(is_minion);
    vt.entity_is_targetable = Some(yes);
    vt.entity_team = Some(team);
    vt.entity_pos = Some(pos);
    vt.entity_hp = Some(hp);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.entity_cc_count = Some(cc_count);
    vt.entity_cc_at = Some(cc_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.entity_clear_cc = Some(clear_cc);
    vt.play_sfx = Some(sfx);
    vt.entity_set_pos = Some(set_pos);
    vt.is_visible = Some(visible);
    vt.player_is_valid = Some(player_valid);
    vt.player_champion = Some(player_champion);
    vt
}

unsafe fn ctx_of(world: &mut World, vt: &SimVtableV1) -> SimCtxV1 {
    SimCtxV1 { size: size_of::<SimCtxV1>(), sim: vt, frame: std::ptr::null(), state: world as *mut World as *mut c_void }
}

/// n ticks: the passive (Aurelion Sol is unit #0), then buffs and crowd control run down.
unsafe fn run(world: &mut World, passive: &PassiveRegV1, n: usize) {
    for _ in 0..n {
        let vt = vtable();
        let mut ctx = ctx_of(world, &vt);
        ((*passive.vtable).on_update.unwrap())(passive.userdata, &mut ctx, 0, 0, 0);
        for e in world.units.iter_mut() {
            e.ccs.iter_mut().for_each(|c| c.1 -= 1);
            e.ccs.retain(|c| c.1 > 0);
            e.buffs.iter_mut().for_each(|b| b.1 = b.1.saturating_sub(1));
            e.buffs.retain(|b| b.1 > 0);
        }
        world.tick += 1;
    }
}

fn me(world: &World) -> (f64, f64) {
    (world.units[0].x, world.units[0].y)
}

fn has(world: &World, name: &str) -> bool {
    world.units[0].buffs.iter().any(|b| b.0.name() == name)
}

fn named(world: &World, prefix: &str) -> Option<String> {
    world.units[0].buffs.iter().map(|b| b.0.name().to_string()).find(|n| n.starts_with(prefix))
}

fn timed(world: &mut World, name: &str, ticks: usize) {
    world.units[0].buffs.push((BuffV1::timed(name, ticks), ticks));
}

/// Aurelion Sol at (300000, 480000), an enemy champion 120000 east of him with an ally of his beside that one, and a
/// minion in a corner that is wall on the single-lane and death-match maps (so the 5v5 map's walls are picked).
fn fight() -> World {
    let mut corner = unit(64_000.0, 64_000.0, 1);
    corner.minion = true;
    let mut foe = unit(420_000.0, 480_000.0, 1);
    foe.hp = 800;
    World { tick: 1000, units: vec![unit(300_000.0, 480_000.0, 0), foe, unit(440_000.0, 490_000.0, 0), corner],
            ..Default::default() }
}

#[test]
fn astral_flight_flies_and_breathes() {
    let log = std::env::temp_dir().join("league_aurelionsol_test.log");
    let _ = std::fs::remove_file(&log);
    std::env::set_var("LEAGUE_AURELIONSOL_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_aurelionsol::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_aurelionsol:stardust"]);
        let proto = &passives[0].passive;
        let passive = || PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let ais = std::slice::from_raw_parts(ex.player_ai_ptr, ex.player_ai_len);
        assert_eq!(ais.len(), 1);
        let ai = ais[0];
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
        let walk = InputV1::move_to(100_000, 100_000);

        // 1. engage: the enemy he can't breathe at (120000 away), his ally on him - he takes off on the next look (tick
        //    1002), Breath of Light's cooldown taken off; nothing before 15 s into the game
        let mut world = fight();
        world.tick = 800;
        let wing = passive();
        run(&mut world, &wing, 60);
        assert!(!has(&world, "league_aurelionsol_w_fly"), "flew before w_start");
        let mut world = fight();
        timed(&mut world, "league_aurelionsol_q_cd", 200);
        let wing = passive();
        assert!(think(&mut world, Some(walk)).is_none(), "the hook acted on the ground");
        run(&mut world, &wing, 3);
        assert!(has(&world, "league_aurelionsol_w_fly"), "no take-off");
        let fly = world.units[0].buffs.iter().find(|b| b.0.name() == "league_aurelionsol_w_fly").unwrap().0;
        assert!(fly.ignore_wall && fly.move_speed_mult == 0);
        assert!(has(&world, "league_aurelionsol_w_up"), "no take-off swirl");
        assert!(!has(&world, "league_aurelionsol_q_cd"), "Breath of Light was not reset");
        assert_eq!(named(&world, "league_aurelionsol_w_to:").as_deref(), Some("league_aurelionsol_w_to:370000,480000"));
        assert_eq!(named(&world, "league_aurelionsol_w_at:").as_deref(), Some("league_aurelionsol_w_at:1"));
        assert_eq!(world.sounds, ["league_aurelionsol_w", "league_aurelionsol_vo_w"]);
        // 2000 a tick toward him
        let x0 = me(&world).0;
        run(&mut world, &wing, 5);
        assert!((me(&world).0 - x0 - 10_000.0).abs() < 1.0 && me(&world).1 == 480_000.0, "{:?}", me(&world));
        // out of the breath's reach (110000): the walk becomes the flight's way, no breath
        let out = think(&mut world, Some(walk)).expect("steered");
        assert_eq!((out.kind, out.x, out.y), (InputKindV1::Move.code(), 370_000, 480_000));
        // in reach (94000 after 8 more ticks): the breath on the one he flies at
        run(&mut world, &wing, 8);
        let out = think(&mut world, Some(walk)).expect("breathed");
        assert_eq!((out.kind, out.target.target_id), (InputKindV1::Skill.code(), 1));
        // the data's breath (its channel and its pose): half speed; the hook leaves it alone
        timed(&mut world, "league_aurelionsol_q_ch", 150);
        timed(&mut world, "league_aurelionsol_q_live", 151);
        world.units[0].ccs.push((CcV1::of_kind(CcKindV1::Animation, 150), 150));
        assert!(think(&mut world, Some(walk)).is_none(), "the hook pressed during the breath");
        let x1 = me(&world).0;
        run(&mut world, &wing, 10);
        assert!((me(&world).0 - x1 - 10_000.0).abs() < 1.0, "not half speed: {}", me(&world).0 - x1);
        // he lands 50000 short of him (70000 flown), the flight's buffs gone, the breath going on
        run(&mut world, &wing, 60);
        assert_eq!(me(&world), (370_000.0, 480_000.0));
        assert!(!has(&world, "league_aurelionsol_w_fly") && named(&world, "league_aurelionsol_w_to:").is_none());
        assert!(has(&world, "league_aurelionsol_q_ch"), "the breath stopped at the landing");
        // the breath begun in flight stops at the ground's longest (90 ticks from its start), its pose with it, and
        // Breath of Light's cooldown runs from there (300 - 90)
        run(&mut world, &wing, 25);
        assert!(!has(&world, "league_aurelionsol_q_ch"), "the breath ran past the ground's longest after the landing");
        assert!(world.units[0].ccs.is_empty(), "its pose stayed");
        let cd = world.units[0].buffs.iter().find(|b| b.0.name() == "league_aurelionsol_q_cd").map(|b| b.1);
        assert!(cd.is_some_and(|t| (195..=210).contains(&t)), "{cd:?}");
        // no other flight while it cools down (22 s at level 1), however the fight goes
        world.units[1].x = 520_000.0;
        run(&mut world, &wing, 600);
        assert!(!has(&world, "league_aurelionsol_w_fly"), "flew again within the cooldown");
        // a takedown: 90% of what is left back
        timed(&mut world, "league_aurelionsol_w_td", 6);
        run(&mut world, &wing, 1);
        assert!(!has(&world, "league_aurelionsol_w_td"));

        // 2. the one he flies at falls in his breath: the breath and its pose end, and he flies on at full speed
        let mut world = fight();
        let wing = passive();
        run(&mut world, &wing, 3 + 13);
        timed(&mut world, "league_aurelionsol_q_ch", 150);
        timed(&mut world, "league_aurelionsol_q_live", 151);
        world.units[0].ccs.push((CcV1::of_kind(CcKindV1::Animation, 150), 150));
        run(&mut world, &wing, 2);
        world.units[1].hp = 0;
        run(&mut world, &wing, 1);
        assert!(!has(&world, "league_aurelionsol_q_ch") && world.units[0].ccs.is_empty(), "the breath went on on nobody");
        assert!(has(&world, "league_aurelionsol_q_live"), "the next breath may come before the old one's pulses are gone");
        let x2 = me(&world).0;
        run(&mut world, &wing, 3);
        assert!((me(&world).0 - x2 - 6_000.0).abs() < 1.0, "not full speed after the fall");

        // 3. low with an enemy beside him: away from it, the whole way; a healthy chaser gets no breath
        let mut world = fight();
        world.units[0].hp = 250;
        world.units[1].x = 330_000.0;
        world.units[1].hp = 1000;
        world.units.remove(2);
        let wing = passive();
        run(&mut world, &wing, 3);
        assert!(has(&world, "league_aurelionsol_w_esc") && named(&world, "league_aurelionsol_w_at:").is_none());
        assert!(think(&mut world, Some(InputV1::action(InputKindV1::Attack, InputTargetV1::target(1))))
            .is_some_and(|o| o.kind == InputKindV1::Move.code()), "the attack was not turned into the flight's way");
        // 0.3.1: the game AI's own breath at the healthy chaser is turned into the flight's way too (11-04 night: FLY #885)
        assert!(think(&mut world, Some(InputV1::action(InputKindV1::Skill, InputTargetV1::target(1))))
            .is_some_and(|o| o.kind == InputKindV1::Move.code()), "the game's own breath passed the hook on an escape");
        // and a breath that begins all the same (the game took the Skill before the hook saw it) is cut at its start
        run(&mut world, &wing, 2);
        timed(&mut world, "league_aurelionsol_q_ch", 150);
        timed(&mut world, "league_aurelionsol_q_live", 151);
        world.units[0].ccs.push((CcV1::of_kind(CcKindV1::Animation, 150), 150));
        let x3 = me(&world).0;
        run(&mut world, &wing, 1);
        assert!(!has(&world, "league_aurelionsol_q_ch") && world.units[0].ccs.is_empty(), "the escape's breath ran on");
        assert!((x3 - me(&world).0 - 2_000.0).abs() < 1.0, "not full speed on the tick of the cut: {}", x3 - me(&world).0);
        run(&mut world, &wing, 77);
        assert!(me(&world).0 < 300_000.0 - 140_000.0, "did not fly away from him: {:?}", me(&world));

        // 4. stunned in flight: he lands where he is
        let mut world = fight();
        let wing = passive();
        run(&mut world, &wing, 6);
        world.units[0].ccs.push((CcV1::stun(30), 30));
        run(&mut world, &wing, 1);
        let stunned = me(&world);
        assert!(!has(&world, "league_aurelionsol_w_fly"), "flew on stunned");
        run(&mut world, &wing, 20);
        assert_eq!(me(&world), stunned);

        let text = std::fs::read_to_string(&log).expect("log written");
        assert!(text.starts_with(&format!("=== league_aurelionsol v{}", env!("CARGO_PKG_VERSION"))), "{text}");
        for line in [
            "FLY #1: engage #1 (80% hp, 120000 away) from (300000, 480000) 70000 to (370000, 480000); his hp 100%",
            "Breath of Light reset (its cooldown was running)",
            "FLY AI: Breath of Light on #1 (94000 away, 80% hp), the one he flies at",
            "BREATH #1: breathing in flight",
            "LAND #1: engage flight arrived after",
            "BREATH END #1: the breath begun in flight stopped (with its pose) at the ground's longest, 90 ticks after it began; Breath of Light's cooldown 210 ticks",
            "REFUND #1: a takedown, Astral Flight's cooldown",
            "BREATH CUT #1: #1, the one he flew at, fell - the breath ends with its pose, on at full speed",
            "FLY #3: escape from (300000, 480000) 150000 to (150000, 480000) over a wall",
            "BREATH CUT #2: the game's own breath on an escape (no chaser under 25% hp) - the breath ends with its pose, on at full speed (2 ticks into the escape flight)",
            "LAND #2: escape flight arrived after 75 ticks, 150000 of 150000 flown; breathing 0 ticks (0 breaths), 0 flown while breathing, 1 breaths cut",
            "flight cut by crowd control",
        ] {
            assert!(text.contains(line), "missing {line:?} in the log:\n{text}");
        }
    }
}
