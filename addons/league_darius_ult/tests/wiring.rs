//! 走真实的导出入口：在一个迷你模拟里让诺手的 AI 钩子想几 tick，检查 R 只在一刀砍得死人时放出（诺克萨斯之力期间也是）；
//! 层数和攻击力从诺手身上的 buff、属性读，护盾和免死算进去；砍不死时 AI 的 R 换成普攻（打不到就走过去）；
//! R 冷却中不主动放；放出后看那一刀的结果写日志。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use league_darius_ult::plan::{HEMO, MIGHT, R_LAND, R_RANGE};
use mod_api_stable::*;

/// 普攻距离（主包诺手的 attack.range）。
const ATTACK_RANGE: f64 = 25_000.0;

struct Unit {
    x: f64,
    y: f64,
    team: usize,
    hp: usize,
    shield: usize,
    attack: usize,
    alive: bool,
    /// 队伍刚打过他（R 的施放目标 EnemyChampionRecentlyAttacked）。
    hit_lately: bool,
    buffs: Vec<BuffV1>,
}

#[derive(Default)]
struct World {
    tick: usize,
    units: Vec<Unit>,
    level: usize,
    ult_cd: usize,
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
unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.alive)
}
unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.team)
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*x, *y) = (e.x as u64, e.y as u64);
    true
}
unsafe extern "C" fn hp(s: *const c_void, h: EntityHandleV1, now: *mut usize, max: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*now, *max) = (e.hp, 2000);
    true
}
unsafe extern "C" fn shield(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.shield)
}
unsafe extern "C" fn stat(s: *const c_void, h: EntityHandleV1, out: *mut StatV1) -> bool {
    let Some(e) = u(s, h) else { return false };
    *out = StatV1 { attack: e.attack, hp: 2000, ..Default::default() };
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
unsafe extern "C" fn dist2(s: *const c_void, a: usize, b: usize) -> u64 {
    let (Some(a), Some(b)) = (w(s).units.get(a), w(s).units.get(b)) else { return u64::MAX };
    ((a.x - b.x).powi(2) + (a.y - b.y).powi(2)) as u64
}
// 玩家 k 的英雄就是单位 k；只有诺手（玩家 0）有等级和冷却
unsafe extern "C" fn player_is_valid(s: *const c_void, h: PlayerHandleV1) -> bool {
    h.id().is_some_and(|k| k < w(s).units.len())
}
unsafe extern "C" fn player_champion(_: *const c_void, h: PlayerHandleV1) -> EntityHandleV1 {
    h.id().map_or(EntityHandleV1::NULL, EntityHandleV1::from_id)
}
unsafe extern "C" fn player_level(s: *const c_void, _: PlayerHandleV1) -> usize {
    w(s).level
}
unsafe extern "C" fn cooldowns(
    s: *const c_void,
    _: PlayerHandleV1,
    a: *mut usize,
    q: *mut usize,
    e: *mut usize,
    r: *mut usize,
) -> bool {
    (*a, *q, *e, *r) = (0, 0, 0, w(s).ult_cd);
    true
}

fn vtable() -> SimVtableV1 {
    let mut vt: SimVtableV1 = unsafe { zeroed() };
    vt.size = size_of::<SimVtableV1>();
    vt.tick = Some(tick);
    vt.sim_origin = Some(origin);
    vt.entity_count = Some(count);
    vt.entity_at = Some(at);
    vt.entity_is_valid = Some(valid);
    vt.entity_is_alive = Some(alive);
    vt.entity_is_champion = Some(valid);
    vt.entity_is_targetable = Some(alive);
    vt.entity_team = Some(team);
    vt.entity_pos = Some(pos);
    vt.entity_hp = Some(hp);
    vt.entity_shield = Some(shield);
    vt.entity_stat = Some(stat);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.distance_sq = Some(dist2);
    vt.player_is_valid = Some(player_is_valid);
    vt.player_champion = Some(player_champion);
    vt.player_level = Some(player_level);
    vt.player_cooldowns = Some(cooldowns);
    vt
}

unsafe extern "C" fn host_log(_: u32, _: *const u8, _: usize) {}

/// AI 钩子看到的「这个玩家」：诺手（玩家 0，蓝方），和他所在的模拟（判断输入合不合法要看）。
struct Me {
    world: *mut World,
}
unsafe extern "C" fn ai_player(_: *const c_void) -> usize {
    0
}
unsafe extern "C" fn ai_team(_: *const c_void) -> usize {
    0
}
unsafe extern "C" fn ai_tick(s: *const c_void) -> usize {
    (*(*(s as *const Me)).world).tick
}
/// 引擎的「输入合法」：R 要点在射程内、队伍刚打过的活着的敌方英雄上，普攻要在普攻距离内（不看冷却，同游戏）。
unsafe extern "C" fn ai_valid(s: *const c_void, input: *const InputV1) -> bool {
    let world = &*(*(s as *const Me)).world;
    let input = &*input;
    let Some(t) = world.units.get(input.target.target_id).filter(|t| t.alive && t.team != 0) else { return false };
    let d = ((t.x - world.units[0].x).powi(2) + (t.y - world.units[0].y).powi(2)).sqrt();
    match InputKindV1::from_code(input.kind) {
        Some(InputKindV1::Ult) => t.hit_lately && d <= R_RANGE as f64,
        Some(InputKindV1::Attack) => d <= ATTACK_RANGE,
        _ => true,
    }
}

/// 让导出的 AI 钩子替诺手想一 tick：返回替换后的输入（`None` = 照原样）。
unsafe fn think(world: &mut World, ai: &PlayerAiRegV1, base: Option<InputV1>) -> Option<InputV1> {
    let vt = vtable();
    let mut avt: AiVtableV1 = zeroed();
    avt.size = size_of::<AiVtableV1>();
    avt.player_id = Some(ai_player);
    avt.team = Some(ai_team);
    avt.tick = Some(ai_tick);
    avt.is_valid_input = Some(ai_valid);
    let mut me = Me { world: world as *mut World };
    let mut ctx = AiCtxV1 {
        size: size_of::<AiCtxV1>(),
        vtable: &avt,
        state: &mut me as *mut Me as *mut c_void,
        sim: &vt,
        sim_state: world as *mut World as *mut c_void,
    };
    let mut out = InputV1::default();
    let base_ptr = base.as_ref().map_or(std::ptr::null(), |b| b as *const InputV1);
    let code = ((*ai.vtable).think.unwrap())(ai.userdata, &mut ctx, base_ptr, &mut out);
    (code == AiDecisionKindV1::Replace.code()).then_some(out)
}

fn buff(name: &str, left: usize) -> BuffV1 {
    BuffV1::timed(name, left)
}

/// 诺手 #0（攻击 200，9 级，R 好了）和队友 #1；敌人 #2（贴身，900）、#3（4 万外，800）、#4（10 万外、射程外，100）。
fn world() -> World {
    let unit = |x: f64, team: usize, hp: usize| Unit {
        x,
        y: 400_000.0,
        team,
        hp,
        shield: 0,
        attack: 200,
        alive: true,
        hit_lately: true,
        buffs: vec![],
    };
    World {
        tick: 1000,
        units: vec![unit(400_000.0, 0, 1500), unit(380_000.0, 0, 1500), unit(420_000.0, 1, 900), unit(440_000.0, 1, 800), unit(500_000.0, 1, 100)],
        level: 9,
        ult_cd: 0,
    }
}

/// The add-on resolves its log path once per process (a LazyLock), so every test logs to the same file: one at a time
/// (the lock), the file cleared first, so each test reads only its own lines.
fn test_log() -> (std::sync::MutexGuard<'static, ()>, std::path::PathBuf) {
    static SERIAL: std::sync::Mutex<()> = std::sync::Mutex::new(());
    let guard = SERIAL.lock().unwrap_or_else(|e| e.into_inner());
    let log = std::env::temp_dir().join("league_darius_ult_test.log");
    std::env::set_var("LEAGUE_DARIUS_ULT_LOG", &log);
    let _ = std::fs::remove_file(&log);
    (guard, log)
}

#[test]
fn r_only_for_a_kill() {
    let (_serial, log) = test_log();
    unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = &*league_darius_ult::tfm2_mod_entry_stable(&host);
        let _ = std::panic::take_hook();
        let ais = std::slice::from_raw_parts(ex.player_ai_ptr, ex.player_ai_len);
        assert_eq!(ais.len(), 1, "one player AI hook");
        let ai = &ais[0];

        let ult = |id: usize| InputV1::action(InputKindV1::Ult, InputTargetV1::target(id));
        let attack = |id: usize| InputV1::action(InputKindV1::Attack, InputTargetV1::target(id));
        let walk_to = |w: &World, id: usize| InputV1::move_to(w.units[id].x as u64, w.units[id].y as u64);

        // 0 层、攻击 200：R 300 真实伤害，谁都砍不死。AI 想砍贴身的 #2：改成普攻；想砍 4 万外的 #3：走过去
        let mut w = world();
        assert_eq!(think(&mut w, ai, Some(ult(2))), Some(attack(2)));
        assert_eq!(think(&mut w, ai, Some(ult(3))), Some(walk_to(&w, 3)));
        assert_eq!(think(&mut w, ai, Some(attack(2))), None, "nothing to execute: the AI's attack stays");

        // #3 只剩 250：AI 想砍 #2 改砍 #3；AI 在普攻也放；10 万外的 #4（100）不在射程里
        w.units[3].hp = 250;
        assert_eq!(think(&mut w, ai, Some(ult(2))), Some(ult(3)));
        assert_eq!(think(&mut w, ai, Some(attack(2))), Some(ult(3)));
        assert_eq!(think(&mut w, ai, Some(ult(3))), None, "the AI's own R on a kill goes through");
        // 在放别的技能、回城：不抢
        assert_eq!(think(&mut w, ai, Some(InputV1::action(InputKindV1::Skill, InputTargetV1::NONE))), None);
        assert_eq!(think(&mut w, ai, Some(InputV1::return_home())), None);
        // R 冷却中、或不到 5 级：不主动放（往后走几 tick：冷却跳起来不算刚才那次放行的 R 放出去了）
        w.tick += 10;
        w.ult_cd = 500;
        assert_eq!(think(&mut w, ai, Some(attack(2))), None);
        w.ult_cd = 0;
        w.level = 4;
        assert_eq!(think(&mut w, ai, Some(attack(2))), None);
        w.level = 9;
        // 队伍没打过他（不是 R 的施放目标）：不主动放
        w.units[3].hit_lately = false;
        assert_eq!(think(&mut w, ai, Some(attack(2))), None);
        w.units[3].hit_lately = true;

        // 护盾 150：生命 + 护盾 400 > 300，砍不死
        w.units[3].shield = 150;
        assert_eq!(think(&mut w, ai, Some(ult(2))), Some(attack(2)));
        // 2 层出血（落刀时都还在）：140 + 280 = 420，砍得死（日志每类至少隔 120 tick 记一次：往后走）
        w.tick += 200;
        w.units[0].buffs = vec![buff(HEMO[0], 200), buff(HEMO[1], 250)];
        assert_eq!(think(&mut w, ai, Some(ult(2))), Some(ult(3)));
        // 第 2 层落刀前就没了：按 1 层，120 + 240 = 360，砍不死
        w.units[0].buffs = vec![buff(HEMO[0], 200), buff(HEMO[1], R_LAND)];
        assert_eq!(think(&mut w, ai, Some(ult(2))), Some(attack(2)));

        // 免死：只剩 10 也砍不死
        w.units[0].buffs.clear();
        w.units[3].shield = 0;
        w.units[3].hp = 10;
        let mut undying = buff("someone_else_undying", 300);
        undying.undying = true;
        w.units[3].buffs = vec![undying];
        assert_eq!(think(&mut w, ai, Some(ult(3))), Some(walk_to(&w, 3)));
        w.units[3].buffs.clear();

        // 受到伤害降低 30%（R 的真实伤害也降：300 只剩 210）：250 血砍不死，AI 想砍 #3 就走过去
        w.tick += 200;
        w.units[3].hp = 250;
        let mut guard = buff("someone_else_guard", 300);
        guard.damaged_reduce = 30;
        w.units[3].buffs = vec![guard];
        assert_eq!(think(&mut w, ai, Some(ult(3))), Some(walk_to(&w, 3)));
        assert_eq!(think(&mut w, ai, Some(attack(2))), None);
        // 只剩 200：210 砍得死
        w.units[3].hp = 200;
        assert_eq!(think(&mut w, ai, Some(attack(2))), Some(ult(3)));
        w.units[3].buffs.clear();
        w.units[3].hp = 800;

        // 诺克萨斯之力（读到的攻击 280 已含 40%）：200 + 560 = 760，谁都砍不死就不放（0.1.1 及以前这时也放）：
        // AI 想砍 #2 改成普攻，AI 没想放也不主动放；#3 掉到 700，760 砍得死，主动放
        w.tick += 200;
        w.units[0].attack = 280;
        w.units[0].buffs = vec![buff(MIGHT, 200)];
        assert_eq!(think(&mut w, ai, Some(ult(2))), Some(attack(2)));
        assert_eq!(think(&mut w, ai, Some(attack(2))), None);
        w.units[3].hp = 700;
        assert_eq!(think(&mut w, ai, Some(attack(2))), Some(ult(3)));
        // 诺克萨斯之力落刀前就没了：0 层、攻击 200，300 砍不死，不放
        w.units[0].buffs = vec![buff(MIGHT, R_LAND - 1)];
        assert_eq!(think(&mut w, ai, Some(ult(2))), Some(attack(2)));
        assert_eq!(think(&mut w, ai, Some(attack(2))), None);

        // 放出去以后：冷却跳起来，落刀砍死 #3，主包的刷新把冷却削到 29 tick；34 tick 后看结果 -> 日志
        w.tick += 200;
        let t0 = w.tick;
        w.units[0].attack = 200;
        w.units[0].buffs.clear();
        w.units[3].hp = 250;
        assert_eq!(think(&mut w, ai, Some(attack(2))), Some(ult(3)));
        w.tick += 1;
        w.ult_cd = 2950;
        assert_eq!(think(&mut w, ai, Some(attack(2))), None, "R on cooldown");
        w.units[3].alive = false;
        for _ in 0..R_LAND + 8 {
            w.tick += 1;
            if w.tick == t0 + R_LAND + 5 {
                w.ult_cd = 29;
            } else if w.tick > t0 + R_LAND + 5 {
                w.ult_cd -= 1;
            } else if w.tick > t0 + 1 {
                w.ult_cd -= 1;
            }
            think(&mut w, ai, Some(attack(2)));
        }

        let text = std::fs::read_to_string(&log).expect("log written");
        if std::env::var_os("KEEP_LOG").is_none() {
            let _ = std::fs::remove_file(&log);
        }
        assert!(text.starts_with(&format!("=== league_darius_ult v{}", env!("CARGO_PKG_VERSION"))), "{text}");
        assert!(text.contains("R HELD: #2 hp + shield 900 > 300 (0 stacks, attack 200), attacking instead"), "{text}");
        assert!(text.contains("R KILL: #3 hp + shield 250 vs 300 (0 stacks, attack 200), retargeted from #2 (hp + shield 900)"), "{text}");
        assert!(text.contains("R KILL: #3 hp + shield 400 vs 420 (2 stacks, attack 200)"), "{text}");
        assert!(text.contains("R HELD: #3 hp + shield 250 > 210 (300 before his damage taken changes) (0 stacks, attack 200)"), "{text}");
        assert!(text.contains("R KILL: #3 hp + shield 200 vs 210 (300 before his damage taken changes) (0 stacks, attack 200)"), "{text}");
        assert!(text.contains("R HELD: #2 hp + shield 900 > 760 (5 stacks, attack 280), attacking instead"), "{text}");
        assert!(text.contains("R KILL: #3 hp + shield 700 vs 760 (5 stacks, attack 280), the AI had not cast it"), "{text}");
        assert!(!text.contains("R MIGHT"), "{text}");
        assert!(
            text.contains("R LANDED on #3: he died, R refreshed (cast for a kill: 300 damage at 0 stacks vs 250 hp + shield, a kill expected)"),
            "{text}"
        );
    }
}
