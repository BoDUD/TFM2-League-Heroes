//! 走真实的导出入口，在一个小世界里试骑行的 AI 钩子（0.6.0，用户 2026-11-20：「一般来说有大招后都开了大招去线上的 现在没有
//! 这种逻辑的 还有开大招赶路救队友之类的」）：原版图的两座水晶和几座塔，奎因是蓝方的上单。检查：
//! - 大招好着、AI 带她出泉水一步只走 30000：第一步就按 R（以前要 AI 一步走 200000 才骑）；
//! - 大招在冷却时出门不骑，出了基地记一行 `OUT ON FOOT`（还要冷却多久）；路上大招好了、离上路一塔还够远就按 R；
//! - 队友在 300000 外打架就按 R 去救；骑着时 AI 让她打小兵、往回走都改成朝他走，朝他走、打敌方英雄照放；到了就交还给 AI；
//! - 你看的那场（画面）每一行都记。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

struct Unit {
    x: f64,
    y: f64,
    team: usize,
    kind: EntityKindV1,
    buffs: Vec<BuffV1>,
}

fn unit(kind: EntityKindV1, team: usize, x: f64, y: f64) -> Unit {
    Unit { x, y, team, kind, buffs: vec![] }
}

#[derive(Default)]
struct World {
    tick: usize,
    units: Vec<Unit>,
    /// 奎因大招的冷却：还剩几 tick、解锁了没有。
    r_left: usize,
    r_unlocked: bool,
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
unsafe extern "C" fn at(s: *const c_void, i: usize) -> EntityHandleV1 {
    if i < w(s).units.len() { EntityHandleV1::from_id(i) } else { EntityHandleV1::NULL }
}
unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
}
unsafe extern "C" fn yes(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
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
    u(s, h).map_or(u32::MAX, |e| e.kind.code())
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
    if u(s, h).is_none() {
        return false;
    }
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
unsafe extern "C" fn visible(_: *const c_void, _: usize, _: usize) -> bool {
    true
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
    if h.id() != Some(0) || slot != SkillSlotV1::Ult.code() {
        return false;
    }
    let world = w(s);
    *out = CooldownV1 { remaining: world.r_left, cooltime: 2400, unlocked: world.r_unlocked, ..Default::default() };
    true
}
unsafe extern "C" fn ai_player(_: *const c_void) -> usize {
    0
}
unsafe extern "C" fn ai_tick(s: *const c_void) -> usize {
    w(s).tick
}
unsafe extern "C" fn ai_lane(_: *const c_void) -> u32 {
    LaneV1::Top.code()
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
    vt.entity_is_alive = Some(yes);
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
    vt.is_visible = Some(visible);
    vt.player_is_valid = Some(player_valid);
    vt.player_champion = Some(player_champion);
    vt.champion_count = Some(champion_count);
    vt.champion_id_at = Some(champion_id_at);
    vt
}

const QUINN: usize = 0;
const ALLY: usize = 7;
const FOE: usize = 8;
const MINION: usize = 9;

/// 原版图（league_macro_log 11-19 的 MAP 行）：蓝方水晶 #1、红方水晶 #2，蓝方的上路一塔 #3、二塔 #4、中路一塔 #5，红方的上路
/// 一塔 #6；奎因 #0 在蓝方泉水，队友 #7 在中路，敌方英雄 #8 在红方上路，敌方小兵 #9。
fn map() -> World {
    let mut w = World { tick: 9_000, r_unlocked: true, ..Default::default() };
    w.units = vec![
        unit(EntityKindV1::Champion, 0, 24_000.0, 936_000.0),
        unit(EntityKindV1::Nexus, 0, 96_000.0, 864_000.0),
        unit(EntityKindV1::Nexus, 1, 864_000.0, 96_000.0),
        unit(EntityKindV1::Tower, 0, 48_000.0, 272_000.0),
        unit(EntityKindV1::Tower, 0, 48_000.0, 528_000.0),
        unit(EntityKindV1::Tower, 0, 368_000.0, 592_000.0),
        unit(EntityKindV1::Tower, 1, 272_000.0, 48_000.0),
        unit(EntityKindV1::Champion, 0, 368_000.0, 560_000.0),
        unit(EntityKindV1::Champion, 1, 272_000.0, 100_000.0),
        unit(EntityKindV1::Minion, 1, 300_000.0, 100_000.0),
    ];
    w
}

fn put(world: &mut World, id: usize, at: (f64, f64)) {
    (world.units[id].x, world.units[id].y) = at;
}

fn is_r(out: Option<InputV1>) -> bool {
    out.is_some_and(|o| o.kind == InputKindV1::Ult.code() && o.target.kind == InputTargetKindV1::None.code())
}

#[test]
fn she_rides_out_to_her_lane_and_to_an_ally_in_a_fight() {
    let log = std::env::temp_dir().join(format!("league_quinn_wiring_{}.log", std::process::id()));
    let _ = std::fs::remove_file(&log);
    std::env::set_var("LEAGUE_QUINN_LOG", &log);
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_quinn::tfm2_mod_entry_stable(&host);
        let ais = std::slice::from_raw_parts(ex.player_ai_ptr, ex.player_ai_len);
        assert_eq!(ais.len(), 1);
        let proto = ais[0];
        let fresh = || PlayerAiRegV1 { userdata: ((*proto.vtable).clone.unwrap())(proto.userdata), vtable: proto.vtable };
        let mut ai_vt: AiVtableV1 = zeroed();
        ai_vt.size = size_of::<AiVtableV1>();
        ai_vt.player_id = Some(ai_player);
        ai_vt.tick = Some(ai_tick);
        ai_vt.lane = Some(ai_lane);
        ai_vt.is_valid_input = Some(ai_valid);
        let think = |ai: &PlayerAiRegV1, world: &mut World, base: Option<InputV1>| -> Option<InputV1> {
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
            world.tick += 1;
            (code == AiDecisionKindV1::Replace.code()).then_some(out)
        };
        let walk = |x: u64, y: u64| Some(InputV1::move_to(x, y));

        // 1. 复活 / 回城后在泉水里，大招好着：AI 一步只走 30000（0.5.x 不骑），第一步就骑
        let ai = fresh();
        let mut world = map();
        assert!(is_r(think(&ai, &mut world, walk(24_000, 906_000))), "no ride out of the fountain");

        // 2. 大招在冷却：出门不骑，出了基地记一行；路上好了，离上路一塔还有 428000，骑
        let ai = fresh();
        let mut world = map();
        world.r_left = 600;
        assert!(think(&ai, &mut world, walk(24_000, 906_000)).is_none(), "pressed a cooling R");
        put(&mut world, QUINN, (40_000.0, 760_000.0));
        assert!(think(&ai, &mut world, None).is_none());
        put(&mut world, QUINN, (48_000.0, 700_000.0));
        assert!(think(&ai, &mut world, walk(48_000, 670_000)).is_none());
        world.r_left = 0;
        assert!(is_r(think(&ai, &mut world, walk(48_000, 670_000))), "no ride once R was back on the way");
        // past the outer tower, in lane: on foot
        let ai = fresh();
        let mut world = map();
        put(&mut world, QUINN, (48_000.0, 200_000.0));
        assert!(think(&ai, &mut world, walk(48_000, 170_000)).is_none(), "rode in lane");

        // 3. 队友在 300000 外和敌方英雄打架：骑过去
        let ai = fresh();
        let mut world = map();
        put(&mut world, QUINN, (100_000.0, 600_000.0));
        put(&mut world, ALLY, (400_000.0, 600_000.0));
        put(&mut world, FOE, (430_000.0, 600_000.0));
        assert!(is_r(think(&ai, &mut world, None)), "no ride to the ally");
        world.units[QUINN].buffs.push(BuffV1::timed("league_quinn_r_ride", 360));
        // on Valor: a minion on the way or a walk back would land her - a walk to him instead
        let on_minion = Some(InputV1::action(InputKindV1::Attack, InputTargetV1::target(MINION)));
        let out = think(&ai, &mut world, on_minion).expect("the attack on a minion went out");
        assert_eq!((out.kind, out.x, out.y), (InputKindV1::Move.code(), 400_000, 600_000));
        let out = think(&ai, &mut world, walk(50_000, 600_000)).expect("the walk back went out");
        assert_eq!((out.kind, out.x, out.y), (InputKindV1::Move.code(), 400_000, 600_000));
        // the AI's own walk his way, its attack on the enemy champion: as they are
        assert!(think(&ai, &mut world, walk(150_000, 600_000)).is_none());
        let on_him = Some(InputV1::action(InputKindV1::Attack, InputTargetV1::target(FOE)));
        assert!(think(&ai, &mut world, on_him).is_none());
        // there (50000 from him): the game's AI fights, a minion and all
        put(&mut world, QUINN, (350_000.0, 600_000.0));
        assert!(think(&ai, &mut world, on_minion).is_none(), "steered after she got there");
        assert!(think(&ai, &mut world, on_minion).is_none());
    }
    let text = std::fs::read_to_string(&log).unwrap();
    for want in [
        "RIDE AI: to lane out of the base: 664434 to the Top front (48000, 272000), the AI's walk 30000",
        "OUT ON FOOT: out of the base without Valor - R cooling 600 more ticks",
        "RIDE AI: to lane: 428000 to the Top front (48000, 272000), the AI's walk 30000",
        "RIDE AI: to help #7 300000 away (100% hp, 1 enemy champions on him)",
        "HELP: on Valor to #7 300000 away - the AI's attack or cast on something else turned into a walk to him",
        "HELP OVER: there (#7 50000 away)",
    ] {
        assert!(text.contains(want), "no line `{want}` in\n{text}");
    }
    assert!(text.lines().filter(|l| l.contains("RIDE AI")).all(|l| l.starts_with("[view m=7 s=0]")), "{text}");
}
