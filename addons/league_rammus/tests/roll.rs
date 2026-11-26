//! 走真实的导出入口，在假宿主里试滚球（0.2.1，用户 2026-11-21：「改，滚久一点」）：
//! - 滚向英雄（Q 的目标挂着 q_aim）：一路碰到的小兵不算撞上，碰到那个英雄才挂 q_go；他身上挂着 `league_rammus_q_at:<号>`，
//!   滚完摘掉；
//! - 滚向小兵（游戏的 AI 拿 Q 清兵）：碰到小兵就撞；
//! - AI 钩子：滚向英雄时 AI 让他打小兵、往别处走，改成普攻那个英雄；本来就在打他、没在滚，不管；
//! - AI 钩子从 100000 外开球，目标在敌方防御塔下不开。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

struct Unit {
    x: f64,
    y: f64,
    team: usize,
    kind: EntityKindV1,
    alive: bool,
    buffs: Vec<BuffV1>,
}

fn unit(kind: EntityKindV1, team: usize, x: f64, y: f64) -> Unit {
    Unit { x, y, team, kind, alive: true, buffs: vec![] }
}

#[derive(Default)]
struct World {
    tick: usize,
    units: Vec<Unit>,
    q_left: usize,
}

unsafe fn w<'a>(s: *const c_void) -> &'a mut World {
    &mut *(s as *mut World)
}
unsafe fn u<'a>(s: *const c_void, h: EntityHandleV1) -> Option<&'a mut Unit> {
    w(s).units.get_mut(h.id()?)
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
unsafe extern "C" fn at(_: *const c_void, i: usize) -> EntityHandleV1 {
    EntityHandleV1::from_id(i)
}
unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
    h.id().is_some_and(|i| i < w(s).units.len())
}
unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.alive)
}
unsafe extern "C" fn yes(_: *const c_void, _: EntityHandleV1) -> bool {
    true
}
unsafe extern "C" fn is_champion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.kind == EntityKindV1::Champion)
}
unsafe extern "C" fn is_tower(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.kind == EntityKindV1::Tower)
}
unsafe extern "C" fn is_minion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.kind == EntityKindV1::Minion)
}
unsafe extern "C" fn kind(s: *const c_void, h: EntityHandleV1) -> u32 {
    u(s, h).map_or(0, |e| e.kind.code())
}
unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.team)
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*x, *y) = (e.x.round() as u64, e.y.round() as u64);
    true
}
unsafe extern "C" fn hp(_: *const c_void, _: EntityHandleV1, now: *mut usize, max: *mut usize) -> bool {
    (*now, *max) = (1000, 1000);
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
unsafe extern "C" fn cc_count(_: *const c_void, _: EntityHandleV1) -> usize {
    0
}
unsafe extern "C" fn add_buff(s: *mut c_void, id: usize, b: *const BuffV1) {
    if let Some(e) = w(s).units.get_mut(id) {
        e.buffs.push(*b);
    }
}
unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, n: *const u8, len: usize) -> usize {
    let name = std::str::from_utf8(std::slice::from_raw_parts(n, len)).unwrap();
    let Some(e) = u(s, h) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.name() != name);
    before - e.buffs.len()
}
unsafe extern "C" fn visible(_: *const c_void, _: usize, _: usize) -> bool {
    true
}
unsafe extern "C" fn distance_sq(s: *const c_void, a: usize, b: usize) -> u64 {
    let units = &w(s).units;
    let (p, q) = (&units[a], &units[b]);
    ((p.x - q.x).powi(2) + (p.y - q.y).powi(2)).round() as u64
}
unsafe extern "C" fn player_valid(_: *const c_void, h: PlayerHandleV1) -> bool {
    h.id() == Some(0)
}
unsafe extern "C" fn player_champion(_: *const c_void, _: PlayerHandleV1) -> EntityHandleV1 {
    EntityHandleV1::from_id(0)
}
unsafe extern "C" fn champion_count(s: *const c_void) -> usize {
    w(s).units.iter().filter(|e| e.kind == EntityKindV1::Champion).count()
}
unsafe extern "C" fn champion_id_at(s: *const c_void, i: usize) -> usize {
    w(s).units.iter().enumerate().filter(|(_, e)| e.kind == EntityKindV1::Champion).nth(i).map_or(usize::MAX, |(k, _)| k)
}
unsafe extern "C" fn cooldown(s: *const c_void, h: EntityHandleV1, slot: u32, out: *mut CooldownV1) -> bool {
    if h.id() != Some(0) || slot != SkillSlotV1::Skill.code() {
        return false;
    }
    *out = CooldownV1 { remaining: w(s).q_left, cooltime: 420, unlocked: true, ..Default::default() };
    true
}
unsafe extern "C" fn ai_player(_: *const c_void) -> usize {
    0
}
unsafe extern "C" fn ai_tick(s: *const c_void) -> usize {
    w(s).tick
}
unsafe extern "C" fn ai_lane(_: *const c_void) -> u32 {
    LaneV1::Jungle.code()
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
    vt.entity_is_targetable = Some(yes);
    vt.entity_is_champion = Some(is_champion);
    vt.entity_is_tower = Some(is_tower);
    vt.entity_is_minion = Some(is_minion);
    vt.entity_kind = Some(kind);
    vt.entity_team = Some(team);
    vt.entity_pos = Some(pos);
    vt.entity_hp = Some(hp);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.entity_cc_count = Some(cc_count);
    vt.entity_cooldown = Some(cooldown);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.is_visible = Some(visible);
    vt.distance_sq = Some(distance_sq);
    vt.player_is_valid = Some(player_valid);
    vt.player_champion = Some(player_champion);
    vt.champion_count = Some(champion_count);
    vt.champion_id_at = Some(champion_id_at);
    vt
}

const RAMMUS: usize = 0;
const FOE: usize = 1;
const MINION: usize = 2;
const TOWER: usize = 3;

/// 拉莫斯 #0 在 (400000, 400000)；敌方英雄 #1 在右边 80000；敌方小兵 #2 在两人中间；敌方防御塔 #3 远在别处。
fn map() -> World {
    let mut w = World { tick: 3000, ..Default::default() };
    w.units = vec![
        unit(EntityKindV1::Champion, 0, 400_000.0, 400_000.0),
        unit(EntityKindV1::Champion, 1, 480_000.0, 400_000.0),
        unit(EntityKindV1::Minion, 1, 440_000.0, 400_000.0),
        unit(EntityKindV1::Tower, 1, 800_000.0, 100_000.0),
    ];
    w
}

fn has(world: &World, id: usize, name: &str) -> bool {
    world.units[id].buffs.iter().any(|b| b.name() == name)
}

fn expire(world: &mut World) {
    for e in world.units.iter_mut() {
        for b in e.buffs.iter_mut() {
            b.duration_tick = b.duration_tick.saturating_sub(1);
        }
        e.buffs.retain(|b| b.duration_tick > 0);
    }
    world.tick += 1;
}

#[test]
fn rolling_at_a_champion_it_rolls_past_minions_and_the_ai_follows_him() {
    let log = std::env::temp_dir().join(format!("league_rammus_roll_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    std::env::set_var("LEAGUE_RAMMUS_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_rammus::tfm2_mod_entry_stable(&host);
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        assert_eq!(passives.iter().map(|p| p.name.as_str()).collect::<Vec<_>>(), ["league_rammus:shell"]);
        let proto = &passives[0].passive;
        let fresh = || PassiveRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let update = |p: &PassiveRegV1, world: &mut World| {
            let vt = vtable();
            let mut ctx = SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(), state: world as *mut World as *mut c_void };
            ((*p.vtable).on_update.unwrap())(p.userdata, &mut ctx, 0, 0, RAMMUS);
        };
        let ais = std::slice::from_raw_parts(ex.player_ai_ptr, ex.player_ai_len);
        assert_eq!(ais.len(), 1);
        let ai = ais[0];
        let mut ai_vt: AiVtableV1 = zeroed();
        ai_vt.size = size_of::<AiVtableV1>();
        ai_vt.player_id = Some(ai_player);
        ai_vt.tick = Some(ai_tick);
        ai_vt.lane = Some(ai_lane);
        ai_vt.is_valid_input = Some(ai_valid);
        let think = |world: &mut World, base: InputV1| -> Option<InputV1> {
            let vt = vtable();
            let mut ctx = AiCtxV1 {
                size: size_of::<AiCtxV1>(),
                vtable: &ai_vt,
                state: world as *mut World as *mut c_void,
                sim: &vt,
                sim_state: world as *mut World as *mut c_void,
            };
            let mut out: InputV1 = zeroed();
            let code = ((*ai.vtable).think.unwrap())(ai.userdata, &mut ctx, &base, &mut out);
            (code == AiDecisionKindV1::Replace.code()).then_some(out)
        };
        let at_foe = league_rammus::at_buff(FOE);
        let attack = |id: usize| InputV1::action(InputKindV1::Attack, InputTargetV1::target(id));
        let is_attack_at = |out: Option<InputV1>, id: usize| {
            out.is_some_and(|o| o.kind == InputKindV1::Attack.code() && o.target.target_id == id)
        };

        // 1. AI 钩子从 80000 外开球（0.2.0 只到 45000）：AI 想走路，改成对他放 Q
        let mut world = map();
        let out = think(&mut world, InputV1::move_to(420_000, 400_000));
        assert!(out.is_some_and(|o| o.kind == InputKindV1::Skill.code() && o.target.target_id == FOE), "no Q from 80000 away");

        // 目标在敌方塔下（塔挪到他旁边）：不开
        let mut world = map();
        (world.units[TOWER].x, world.units[TOWER].y) = (480_000.0, 340_000.0);
        assert!(think(&mut world, InputV1::move_to(420_000, 400_000)).is_none(), "rolled into a tower");

        // 2. 滚向英雄：Q 的目标挂着 q_aim，他缩成球
        let shell = fresh();
        let mut world = map();
        world.units[FOE].buffs.push(BuffV1::timed(league_rammus::AIM, 14));
        world.units[RAMMUS].buffs.push(BuffV1::timed(league_rammus::BALL, 360));
        update(&shell, &mut world);
        assert!(has(&world, RAMMUS, &at_foe), "no q_at mark for the champion he rolls at");
        expire(&mut world);
        // 滚到小兵身上：不撞
        world.units[RAMMUS].x = 440_000.0 - 8_000.0;
        update(&shell, &mut world);
        assert!(!has(&world, RAMMUS, league_rammus::GO), "the ball stopped on a minion while rolling at a champion");
        // 滚着 AI 想打小兵、往别处走：改成打那个英雄；本来就在打他：不管
        assert!(is_attack_at(think(&mut world, attack(MINION)), FOE), "the AI's attack on the minion was not turned to the champion");
        assert!(is_attack_at(think(&mut world, InputV1::move_to(300_000, 400_000)), FOE));
        assert!(think(&mut world, attack(FOE)).is_none());
        expire(&mut world);
        // 滚到英雄身上：撞
        world.units[RAMMUS].x = 480_000.0 - 8_000.0;
        update(&shell, &mut world);
        assert!(has(&world, RAMMUS, league_rammus::GO), "no hit on the champion");
        // 球没了（撞上了）：q_at 摘掉，AI 钩子不再管他打谁
        world.units[RAMMUS].buffs.retain(|b| b.name() != league_rammus::BALL);
        expire(&mut world);
        update(&shell, &mut world);
        assert!(!has(&world, RAMMUS, &at_foe), "q_at stayed after the roll");
        assert!(think(&mut world, attack(MINION)).is_none());

        // 3. 滚向小兵（游戏的 AI 拿 Q 清兵）：碰到小兵就撞，也不挂 q_at
        let shell = fresh();
        let mut world = map();
        world.units[MINION].buffs.push(BuffV1::timed(league_rammus::AIM, 14));
        world.units[RAMMUS].buffs.push(BuffV1::timed(league_rammus::BALL, 360));
        update(&shell, &mut world);
        assert!(!world.units[RAMMUS].buffs.iter().any(|b| b.name().starts_with(league_rammus::AT)));
        expire(&mut world);
        world.units[RAMMUS].x = 440_000.0 - 8_000.0;
        update(&shell, &mut world);
        assert!(has(&world, RAMMUS, league_rammus::GO), "no hit on the minion it rolled at");
    }
    let text = std::fs::read_to_string(&log).unwrap();
    for want in [
        "OPEN: Powerball at #1 from 80000 away",
        "OPEN NOT: #1 80000 away is under a tower",
        "ROLL curled up at champion #1",
        "STEER: rolling at #1",
        "ROLL hit #1 (champion) after 2 ticks",
        "1 minions rolled past",
        "ROLL hit #2 (unit) after 1 ticks",
    ] {
        assert!(text.contains(want), "no line `{want}` in\n{text}");
    }
}
