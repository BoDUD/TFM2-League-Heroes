//! 用一个最小的模拟宿主（只实现 SimVtableV1 里本 mod 用到的槽位）驱动乙骨 mod：
//! 同一进程里同时/交错跑「屏幕对局 + 服务器预模拟 + 回放」等多份模拟，检查每份模拟里
//! 里香都正常出现、归属正确。宿主是按 SDK 契约写的近似（不走路、不打架），不代表
//! 游戏引擎的全部细节——它验证的是 mod 自己的状态管理。
//!
//! 运行：`cargo test --release -- --test-threads=1`（多线程用例自己开线程）。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};
use std::sync::OnceLock;

use mod_api_stable::*;

const RIKA_TAG: &str = "yuta_rika_tag";
const CRIT_AURA: &str = "yuta_crit_aura";
const GROWTH_BUFF: &str = "yuta_growth";
/// 开局召唤：on_spawn/on_match_start 在 tick 0，30 tick 延迟后第 31 tick 出生。
const FIRST_SPAWN_TICK: usize = 31;

// ---------------------------------------------------------------------------
// 模拟世界
// ---------------------------------------------------------------------------

#[derive(Clone)]
struct Ent {
    team: usize,
    champion: bool,
    minion: bool,
    alive: bool,
    level: usize,
    hp: usize,
    max_hp: usize,
    x: u64,
    y: u64,
    stat: StatV1,
    buffs: Vec<BuffV1>,
    name: String,
    shield: usize,
    hidden_until: usize,
}

impl Ent {
    fn champion(team: usize, name: &str, x: u64) -> Self {
        Self {
            team,
            champion: true,
            minion: false,
            alive: true,
            level: 1,
            hp: 3_000,
            max_hp: 3_000,
            x,
            y: 50_000,
            stat: StatV1 { attack: 60, hp: 3_000, ..StatV1::default() },
            buffs: Vec::new(),
            name: name.to_string(),
            shield: 0,
            hidden_until: 0,
        }
    }

    fn minion(team: usize, x: u64) -> Self {
        Self { champion: false, minion: true, name: "minion".into(), ..Self::champion(team, "", x) }
    }

    fn count(&self, name: &str) -> usize {
        self.buffs.iter().filter(|b| b.name() == name).count()
    }
}

struct World {
    tick: usize,
    seed: u64,
    origin: SimOriginV1,
    end: bool,
    ents: Vec<Ent>,
    /// (单位 id, 召唤者, tick)
    spawns: Vec<(usize, usize, usize)>,
    /// (施法者, 被放逐者)
    banishes: Vec<(usize, usize)>,
    /// (攻击者, 目标, 真伤数值)
    fixed_hits: Vec<(usize, usize, usize)>,
}

impl World {
    /// 10 个英雄（0-4 蓝方，5-9 红方）+ 4 个小兵；`yutas` 里的 id 是乙骨。
    fn new(kind: SimOriginKindV1, match_id: u64, seed: u64, yutas: &[usize]) -> Self {
        let mut ents = Vec::new();
        for i in 0..10 {
            let team = i / 5;
            let x = if team == 0 { 40_000 + i as u64 * 1_000 } else { 52_000 + (i as u64 - 5) * 1_000 };
            let name = if yutas.contains(&i) { "yuta".to_string() } else { format!("champ{i}") };
            ents.push(Ent::champion(team, &name, x));
        }
        for i in 0..4 {
            ents.push(Ent::minion(i % 2, 46_000 + i as u64 * 500));
        }
        let origin = SimOriginV1 { kind: kind.code(), match_id, set_index: 0, ..SimOriginV1::default() };
        Self { tick: 0, seed, origin, end: false, ents, spawns: Vec::new(), banishes: Vec::new(), fixed_hits: Vec::new() }
    }

    /// 存活的里香（带归属标记的单位）。
    fn rikas(&self) -> Vec<usize> {
        (0..self.ents.len()).filter(|&i| self.ents[i].alive && self.ents[i].count(RIKA_TAG) > 0).collect()
    }

    fn rikas_of_team(&self, team: usize) -> Vec<usize> {
        self.rikas().into_iter().filter(|&i| self.ents[i].team == team).collect()
    }

    fn buff_names(&self, id: usize) -> Vec<String> {
        self.ents[id].buffs.iter().map(|b| b.name().to_string()).collect()
    }
}

fn hurt(w: &mut World, target: usize, amount: usize) {
    if let Some(e) = w.ents.get_mut(target) {
        if !e.alive {
            return;
        }
        let soaked = e.shield.min(amount);
        e.shield -= soaked;
        e.hp = e.hp.saturating_sub(amount - soaked);
        if e.hp == 0 {
            e.alive = false;
            e.buffs.clear();
        }
    }
}

// ---------------------------------------------------------------------------
// SimVtableV1 槽位
// ---------------------------------------------------------------------------

unsafe fn w<'a>(s: *const c_void) -> &'a World {
    &*(s as *const World)
}
unsafe fn wm<'a>(s: *mut c_void) -> &'a mut World {
    &mut *(s as *mut World)
}
unsafe fn ent<'a>(s: *const c_void, h: EntityHandleV1) -> Option<&'a Ent> {
    w(s).ents.get(h.id()?)
}
unsafe fn ent_mut<'a>(s: *mut c_void, h: EntityHandleV1) -> Option<&'a mut Ent> {
    wm(s).ents.get_mut(h.id()?)
}
unsafe fn name_of(p: *const u8, len: usize) -> String {
    String::from_utf8_lossy(std::slice::from_raw_parts(p, len)).into_owned()
}

unsafe extern "C" fn s_tick(s: *const c_void) -> usize {
    w(s).tick
}
unsafe extern "C" fn s_seed(s: *const c_void) -> u64 {
    w(s).seed
}
unsafe extern "C" fn s_is_end(s: *const c_void) -> bool {
    w(s).end
}
unsafe extern "C" fn s_entity_count(s: *const c_void) -> usize {
    w(s).ents.len()
}
unsafe extern "C" fn s_entity_at(s: *const c_void, i: usize) -> EntityHandleV1 {
    if i < w(s).ents.len() {
        EntityHandleV1::from_id(i)
    } else {
        EntityHandleV1::NULL
    }
}
unsafe extern "C" fn s_entity_is_valid(s: *const c_void, h: EntityHandleV1) -> bool {
    ent(s, h).is_some()
}
unsafe extern "C" fn s_entity_stat(s: *const c_void, h: EntityHandleV1, out: *mut StatV1) -> bool {
    match ent(s, h) {
        Some(e) if !out.is_null() => {
            *out = e.stat;
            true
        }
        _ => false,
    }
}
unsafe extern "C" fn s_entity_pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    match ent(s, h) {
        Some(e) => {
            *x = e.x;
            *y = e.y;
            true
        }
        None => false,
    }
}
unsafe extern "C" fn s_entity_hp(s: *const c_void, h: EntityHandleV1, cur: *mut usize, max: *mut usize) -> bool {
    match ent(s, h) {
        Some(e) => {
            *cur = e.hp;
            *max = e.max_hp;
            true
        }
        None => false,
    }
}
unsafe extern "C" fn s_entity_team(s: *const c_void, h: EntityHandleV1) -> usize {
    ent(s, h).map_or(0, |e| e.team)
}
unsafe extern "C" fn s_entity_level(s: *const c_void, h: EntityHandleV1) -> usize {
    ent(s, h).map_or(1, |e| e.level)
}
unsafe extern "C" fn s_entity_is_alive(s: *const c_void, h: EntityHandleV1) -> bool {
    ent(s, h).is_some_and(|e| e.alive)
}
unsafe extern "C" fn s_entity_is_champion(s: *const c_void, h: EntityHandleV1) -> bool {
    ent(s, h).is_some_and(|e| e.champion)
}
unsafe extern "C" fn s_entity_is_tower(_s: *const c_void, _h: EntityHandleV1) -> bool {
    false
}
unsafe extern "C" fn s_entity_is_minion(s: *const c_void, h: EntityHandleV1) -> bool {
    ent(s, h).is_some_and(|e| e.minion)
}
unsafe extern "C" fn s_entity_shield(s: *const c_void, h: EntityHandleV1) -> usize {
    ent(s, h).map_or(0, |e| e.shield)
}
unsafe extern "C" fn s_entity_is_targetable(s: *const c_void, h: EntityHandleV1) -> bool {
    let tick = w(s).tick;
    ent(s, h).is_some_and(|e| e.alive && tick >= e.hidden_until)
}
unsafe extern "C" fn s_entity_buff_count(s: *const c_void, h: EntityHandleV1) -> usize {
    ent(s, h).map_or(0, |e| e.buffs.len())
}
unsafe extern "C" fn s_entity_buff_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut BuffV1) -> bool {
    match ent(s, h).and_then(|e| e.buffs.get(i)) {
        Some(b) if !out.is_null() => {
            *out = *b;
            true
        }
        _ => false,
    }
}
unsafe extern "C" fn s_entity_name(
    s: *const c_void,
    h: EntityHandleV1,
    buf: *mut u8,
    cap: usize,
    out_len: *mut usize,
) -> bool {
    let Some(e) = ent(s, h) else { return false };
    let bytes = e.name.as_bytes();
    if !out_len.is_null() {
        *out_len = bytes.len();
    }
    if !buf.is_null() {
        let n = bytes.len().min(cap);
        std::ptr::copy_nonoverlapping(bytes.as_ptr(), buf, n);
    }
    true
}
unsafe extern "C" fn s_deal_damage(s: *mut c_void, _a: usize, target: usize, ad: usize, ap: usize, _t: u32) {
    hurt(wm(s), target, ad + ap);
}
unsafe extern "C" fn s_deal_damage_typed(s: *mut c_void, a: usize, target: usize, amount: usize, d: u32, _t: u32) -> bool {
    if d == DamageTypeV1::Fixed.code() {
        wm(s).fixed_hits.push((a, target, amount));
    }
    hurt(wm(s), target, amount);
    true
}
unsafe extern "C" fn s_heal(s: *mut c_void, _c: usize, target: usize, amount: usize) {
    if let Some(e) = wm(s).ents.get_mut(target) {
        if e.alive {
            e.hp = (e.hp + amount).min(e.max_hp);
        }
    }
}
unsafe extern "C" fn s_add_buff(s: *mut c_void, target: usize, b: *const BuffV1) {
    if let Some(e) = wm(s).ents.get_mut(target) {
        if e.alive && !b.is_null() {
            e.buffs.push(*b);
        }
    }
}
unsafe extern "C" fn s_apply_cc(_s: *mut c_void, _t: usize, _cc: *const CcV1) {}
unsafe extern "C" fn s_spawn_unit(
    s: *mut c_void,
    name: *const u8,
    len: usize,
    summoner: usize,
    team: usize,
    x: u64,
    y: u64,
    _duration: u64,
    stat: *const StatV1,
    _attack: *const UnitAttackV1,
) -> usize {
    let world = wm(s);
    let stat = *stat;
    let mut unit = Ent::champion(team, &name_of(name, len), x);
    unit.champion = false;
    unit.y = y;
    unit.stat = stat;
    unit.hp = stat.hp;
    unit.max_hp = stat.hp;
    world.ents.push(unit);
    let id = world.ents.len() - 1;
    world.spawns.push((id, summoner, world.tick));
    id
}
unsafe extern "C" fn s_entity_remove_buff(s: *mut c_void, h: EntityHandleV1, name: *const u8, len: usize) -> usize {
    let name = name_of(name, len);
    let Some(e) = ent_mut(s, h) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.name() != name);
    before - e.buffs.len()
}
unsafe extern "C" fn s_entity_add_shield(s: *mut c_void, h: EntityHandleV1, amount: usize, _d: usize) -> bool {
    match ent_mut(s, h) {
        Some(e) => {
            e.shield += amount;
            true
        }
        None => false,
    }
}
unsafe extern "C" fn s_entity_clear_shield(s: *mut c_void, h: EntityHandleV1) -> usize {
    ent_mut(s, h).map_or(0, |e| std::mem::take(&mut e.shield).min(1))
}
unsafe extern "C" fn s_entity_attack_interval(_s: *const c_void, _h: EntityHandleV1) -> usize {
    60
}
unsafe extern "C" fn s_play_view_effect(
    _s: *mut c_void,
    _n: *const u8,
    _l: usize,
    _c: usize,
    _i: *const InputTargetV1,
    _r: u64,
    _rad: u64,
    _t: u64,
) -> bool {
    true
}
unsafe extern "C" fn s_play_sfx(_s: *mut c_void, _n: *const u8, _l: usize, _c: usize, _i: *const InputTargetV1) -> bool {
    true
}
unsafe extern "C" fn s_entity_set_invisible(s: *mut c_void, h: EntityHandleV1, ticks: usize) -> bool {
    let tick = wm(s).tick;
    match ent_mut(s, h) {
        Some(e) => {
            e.hidden_until = tick + ticks;
            true
        }
        None => false,
    }
}
unsafe extern "C" fn s_entity_banish(
    s: *mut c_void,
    caster: usize,
    h: EntityHandleV1,
    ticks: usize,
    _a: *const u8,
    _al: usize,
    _b: *const u8,
    _bl: usize,
) -> bool {
    let tick = wm(s).tick;
    let Some(id) = h.id() else { return false };
    wm(s).banishes.push((caster, id));
    match ent_mut(s, h) {
        Some(e) => {
            e.hidden_until = tick + ticks;
            true
        }
        None => false,
    }
}
unsafe extern "C" fn s_sim_origin(s: *const c_void, out: *mut SimOriginV1) -> bool {
    if out.is_null() {
        return false;
    }
    *out = w(s).origin;
    true
}
unsafe extern "C" fn s_entity_stack_buff(s: *mut c_void, h: EntityHandleV1, b: *const BuffV1, max: usize, _r: u32) -> usize {
    let Some(e) = ent_mut(s, h) else { return 0 };
    let name = (*b).name().to_string();
    if max == 0 || e.count(&name) < max {
        e.buffs.push(*b);
    }
    e.count(&name)
}

fn vtable() -> &'static SimVtableV1 {
    static VT: OnceLock<SimVtableV1> = OnceLock::new();
    VT.get_or_init(|| {
        // 全部槽位先置 None（Option<fn> 的零值），再填本 mod 用到的。
        let mut vt: SimVtableV1 = unsafe { zeroed() };
        vt.size = size_of::<SimVtableV1>();
        vt.tick = Some(s_tick);
        vt.seed = Some(s_seed);
        vt.is_end = Some(s_is_end);
        vt.entity_count = Some(s_entity_count);
        vt.entity_at = Some(s_entity_at);
        vt.entity_is_valid = Some(s_entity_is_valid);
        vt.entity_stat = Some(s_entity_stat);
        vt.entity_pos = Some(s_entity_pos);
        vt.entity_hp = Some(s_entity_hp);
        vt.entity_team = Some(s_entity_team);
        vt.entity_level = Some(s_entity_level);
        vt.entity_is_alive = Some(s_entity_is_alive);
        vt.entity_is_champion = Some(s_entity_is_champion);
        vt.entity_is_tower = Some(s_entity_is_tower);
        vt.entity_is_minion = Some(s_entity_is_minion);
        vt.entity_shield = Some(s_entity_shield);
        vt.entity_is_targetable = Some(s_entity_is_targetable);
        vt.entity_buff_count = Some(s_entity_buff_count);
        vt.entity_buff_at = Some(s_entity_buff_at);
        vt.entity_name = Some(s_entity_name);
        vt.deal_damage = Some(s_deal_damage);
        vt.deal_damage_typed = Some(s_deal_damage_typed);
        vt.heal = Some(s_heal);
        vt.add_buff = Some(s_add_buff);
        vt.apply_cc = Some(s_apply_cc);
        vt.spawn_unit = Some(s_spawn_unit);
        vt.entity_remove_buff = Some(s_entity_remove_buff);
        vt.entity_add_shield = Some(s_entity_add_shield);
        vt.entity_clear_shield = Some(s_entity_clear_shield);
        vt.entity_attack_interval = Some(s_entity_attack_interval);
        vt.play_view_effect = Some(s_play_view_effect);
        vt.play_sfx = Some(s_play_sfx);
        vt.entity_set_invisible = Some(s_entity_set_invisible);
        vt.entity_banish = Some(s_entity_banish);
        vt.sim_origin = Some(s_sim_origin);
        vt.entity_stack_buff = Some(s_entity_stack_buff);
        vt
    })
}

fn ctx(world: &mut World) -> SimCtxV1 {
    SimCtxV1 {
        size: size_of::<SimCtxV1>(),
        sim: vtable(),
        frame: std::ptr::null(),
        state: world as *mut World as *mut c_void,
    }
}

// ---------------------------------------------------------------------------
// 加载 mod，扮演宿主调用它
// ---------------------------------------------------------------------------

struct Mod {
    hook: MatchHookRegV1,
    passive: PassiveRegV1,
    effects: Vec<(String, EffectTypeRegV1)>,
}
// 宿主侧持有 mod 对象；mod 自己的全局状态用 Mutex 保护。
unsafe impl Send for Mod {}
unsafe impl Sync for Mod {}

unsafe extern "C" fn host_log(_level: u32, _msg: *const u8, _len: usize) {}

fn the_mod() -> &'static Mod {
    static M: OnceLock<Mod> = OnceLock::new();
    M.get_or_init(|| unsafe {
        let mut host: HostApiV1 = zeroed();
        host.size = size_of::<HostApiV1>();
        host.host_abi_level = ABI_LEVEL;
        host.log = Some(host_log);
        let ex = yuta::tfm2_mod_entry_stable(&host);
        assert!(!ex.is_null(), "mod entry failed");
        // mod 的 init 会装自己的 panic 钩子（写日志文件）；测试里换回默认钩子，断言信息才看得见。
        let _ = std::panic::take_hook();
        let ex = &*ex;
        let passives = std::slice::from_raw_parts(ex.native_passives_ptr, ex.native_passives_len);
        let passive = passives
            .iter()
            .find(|p| p.name.as_str() == "yuta:yuta_passive")
            .expect("passive registered")
            .passive;
        let effects = std::slice::from_raw_parts(ex.native_effects_ptr, ex.native_effects_len)
            .iter()
            .map(|e| (e.name.as_str().to_string(), e.effect))
            .collect();
        Mod { hook: ex.match_hook, passive, effects }
    })
}

impl Mod {
    /// 英雄出生：宿主给每个英雄克隆一份被动，调 on_spawn。返回这份被动。
    fn spawn(&self, world: &mut World, entity: usize) -> *mut c_void {
        unsafe {
            let vt = &*self.passive.vtable;
            let ud = (vt.clone.unwrap())(self.passive.userdata);
            if let Some(configure) = vt.configure {
                configure(ud, b"{}".as_ptr(), 2);
            }
            let mut c = ctx(world);
            (vt.on_spawn.unwrap())(ud, &mut c, entity, entity);
            ud
        }
    }

    fn respawn(&self, world: &mut World, ud: *mut c_void, entity: usize) {
        world.ents[entity].alive = true;
        world.ents[entity].hp = world.ents[entity].max_hp;
        unsafe {
            let mut c = ctx(world);
            ((*self.passive.vtable).on_spawn.unwrap())(ud, &mut c, entity, entity);
        }
    }

    fn on_kill(&self, world: &mut World, ud: *mut c_void, entity: usize, victim: usize) {
        unsafe {
            let mut c = ctx(world);
            ((*self.passive.vtable).on_kill_ex.unwrap())(ud, &mut c, entity, entity, victim);
        }
    }

    fn match_start(&self, world: &mut World) {
        unsafe {
            let mut c = ctx(world);
            ((*self.hook.vtable).on_match_start.unwrap())(self.hook.userdata, &mut c);
        }
    }

    fn tick(&self, world: &mut World) {
        world.tick += 1;
        let rng = world.seed ^ world.tick as u64;
        unsafe {
            let vt = &*self.hook.vtable;
            let mut c = ctx(world);
            (vt.on_match_tick.unwrap())(self.hook.userdata, &mut c, rng);
            let mut blue = false;
            (vt.check_match_end.unwrap())(self.hook.userdata, &mut c, &mut blue);
        }
    }

    fn ticks(&self, world: &mut World, n: usize) {
        for _ in 0..n {
            self.tick(world);
        }
    }

    fn end(&self, world: &mut World) {
        world.end = true;
        self.tick(world);
    }

    fn effect(&self, world: &mut World, name: &str, caster: usize, input: InputTargetV1) {
        let (_, reg) = self.effects.iter().find(|(n, _)| n == name).expect("effect registered");
        unsafe {
            let mut c = ctx(world);
            ((*reg.vtable).apply.unwrap())(reg.userdata, &mut c, 7, caster, &input);
        }
    }
}

// ---------------------------------------------------------------------------
// 用例
// ---------------------------------------------------------------------------

/// 屏幕对局刚开局时，服务器在后台把另一场赛程（对面也有乙骨）预模拟完。
/// 旧版：预模拟开局重置、逐 tick 用别的世界推进、收场清空了屏幕对局的大脑 → 屏幕上没有里香。
#[test]
fn presim_of_another_fixture_does_not_touch_the_match_on_screen() {
    let m = the_mod();
    let mut view = World::new(SimOriginKindV1::ClientMatchView, 101, 0x1001, &[2]);
    let mut presim = World::new(SimOriginKindV1::ServerPresim, 102, 0x1002, &[7]);
    m.spawn(&mut view, 2);
    m.match_start(&mut view);
    m.ticks(&mut view, 5);

    m.spawn(&mut presim, 7);
    m.match_start(&mut presim);
    m.ticks(&mut presim, 120);
    m.end(&mut presim);

    m.ticks(&mut view, 200);
    let own: Vec<_> = view.spawns.iter().filter(|s| s.1 == 2).collect();
    assert_eq!(view.rikas_of_team(0).len(), 1, "screen: Rika on Yuta's team; spawns {:?}", view.spawns);
    assert_eq!(own.len(), 1, "screen: exactly one Rika summoned by Yuta; spawns {:?}", view.spawns);
    assert_eq!(own[0].2, FIRST_SPAWN_TICK, "screen: Rika on schedule");
    assert!(
        presim.spawns.iter().all(|s| s.1 == 7),
        "presim: only its own Yuta (id 7) summons; spawns {:?}",
        presim.spawns
    );
    m.end(&mut view);
}

/// 没有乙骨的后台预模拟（绝大多数赛程）：什么都不召唤，也不影响同时进行的屏幕对局。
#[test]
fn presim_without_yuta_is_left_alone() {
    let m = the_mod();
    let mut view = World::new(SimOriginKindV1::ClientMatchView, 110, 0x1010, &[4]);
    let mut presim = World::new(SimOriginKindV1::ServerPresim, 111, 0x1011, &[]);
    m.spawn(&mut view, 4);
    m.match_start(&mut view);
    m.match_start(&mut presim);
    for _ in 0..200 {
        m.tick(&mut presim);
        m.tick(&mut view);
    }
    m.end(&mut presim);
    assert!(presim.spawns.is_empty(), "presim spawns {:?}", presim.spawns);
    assert_eq!(view.spawns.len(), 1, "view spawns {:?}", view.spawns);
    assert_eq!(view.spawns[0].1, 4);
    m.end(&mut view);
}

/// 同一赛程的预模拟和屏幕对局（同种子、来源不同）逐 tick 交错推进，两边必须算出完全一样的结果，
/// 否则屏幕上看到的和后台定下的胜负不一致。
#[test]
fn presim_and_view_of_the_same_fixture_stay_identical() {
    let m = the_mod();
    let mut presim = World::new(SimOriginKindV1::ServerPresim, 103, 0x1003, &[2]);
    let mut view = World::new(SimOriginKindV1::ClientMatchView, 103, 0x1003, &[2]);
    m.spawn(&mut presim, 2);
    m.spawn(&mut view, 2);
    m.match_start(&mut presim);
    m.match_start(&mut view);
    for _ in 0..800 {
        m.tick(&mut presim);
        m.tick(&mut view);
    }
    assert_eq!(view.spawns.len(), 1, "view spawns {:?}", view.spawns);
    assert_eq!(view.spawns, presim.spawns);
    assert_eq!(view.buff_names(2), presim.buff_names(2), "Yuta's marks diverged");
    m.end(&mut presim);
    m.end(&mut view);
}

/// 多份模拟在不同线程上同时跑（后台预模拟多个赛程 + 屏幕对局），长短不一、先后收场。
#[test]
fn simulations_on_threads_each_get_their_own_rika() {
    let m = the_mod();
    let yutas = [2usize, 7, 3, 8, 1, 6];
    let handles: Vec<_> = (0..yutas.len())
        .map(|i| {
            std::thread::spawn(move || {
                let kind = if i == 0 { SimOriginKindV1::ClientMatchView } else { SimOriginKindV1::ServerPresim };
                let yuta = yutas[i];
                let mut world = World::new(kind, 200 + i as u64, 0x2000 + i as u64, &[yuta]);
                m.spawn(&mut world, yuta);
                m.match_start(&mut world);
                for _ in 0..(120 + i * 37) {
                    m.tick(&mut world);
                    std::thread::yield_now();
                }
                let own = world.spawns.iter().filter(|s| s.1 == yuta).count();
                let foreign = world.spawns.iter().filter(|s| s.1 != yuta).count();
                let first = world.spawns.first().map(|s| s.2);
                let rikas = world.rikas().len();
                m.end(&mut world);
                (i, rikas, own, foreign, first)
            })
        })
        .collect();
    // 先等所有线程跑完再断言，失败时不留下还在跑的模拟去干扰后面的用例。
    let results: Vec<_> = handles.into_iter().map(|h| h.join().unwrap()).collect();
    for (i, rikas, own, foreign, first) in results {
        assert_eq!(
            (rikas, own, foreign, first),
            (1, 1, 0, Some(FIRST_SPAWN_TICK)),
            "sim {i}: (alive Rikas, own spawns, foreign spawns, first spawn tick)"
        );
    }
}

/// 双方各有一个乙骨（镜像）：各自的里香、大招只放逐自己的里香、联动真伤按自己里香的生命算。
#[test]
fn two_yutas_each_get_their_own_rika() {
    let m = the_mod();
    let mut world = World::new(SimOriginKindV1::ClientMatchView, 104, 0x1004, &[2, 7]);
    world.ents[7].level = 3; // 红方乙骨 3 级：他的里香生命更高，好区分
    m.spawn(&mut world, 2);
    m.spawn(&mut world, 7);
    m.match_start(&mut world);
    m.ticks(&mut world, 100);
    assert_eq!(world.rikas_of_team(0).len(), 1, "blue Rika; spawns {:?}", world.spawns);
    assert_eq!(world.rikas_of_team(1).len(), 1, "red Rika; spawns {:?}", world.spawns);

    m.effect(&mut world, "yuta:yuta_ult_open", 2, InputTargetV1::NONE);
    assert_eq!(world.banishes.len(), 1);
    let banished = world.banishes[0].1;
    assert_eq!(world.ents[banished].team, 0, "Yuta 2's ult must banish his own Rika");

    m.effect(&mut world, "yuta:yuta_rika_true", 2, InputTargetV1::target(6));
    m.effect(&mut world, "yuta:yuta_rika_true", 7, InputTargetV1::target(1));
    let blue_rika = world.rikas_of_team(0)[0];
    let red_rika = world.rikas_of_team(1)[0];
    let hits: Vec<_> = world.fixed_hits.iter().map(|h| (h.0, h.2)).collect();
    assert_eq!(
        hits,
        vec![(2, world.ents[blue_rika].max_hp / 10), (7, world.ents[red_rika].max_hp / 10)],
        "true damage must use each Yuta's own Rika"
    );
    m.end(&mut world);
}

/// 里香死后她的实体 id 被引擎分给同队新刷的小兵：大脑必须认出里香已经没了，5 秒后重召。
#[test]
fn rika_is_resummoned_when_her_id_is_reused() {
    let m = the_mod();
    let mut world = World::new(SimOriginKindV1::ClientMatchView, 105, 0x1005, &[2]);
    m.spawn(&mut world, 2);
    m.match_start(&mut world);
    m.ticks(&mut world, 60);
    let first = world.rikas_of_team(0);
    assert_eq!(first.len(), 1);
    world.ents[first[0]] = Ent::minion(0, 45_000);
    m.ticks(&mut world, 320);
    let now = world.rikas_of_team(0);
    assert_eq!(now.len(), 1, "a new Rika after the respawn timer; spawns {:?}", world.spawns);
    assert_ne!(now[0], first[0]);
    m.end(&mut world);
}

/// 一局没跑到收场就被放弃（跳过/退出），下一场里 id 2 是别的英雄、乙骨在 id 6。
/// 旧版：残留的大脑在新局被保留给 id 2 的英雄，给错误的英雄召唤里香，乙骨反而认领别人的。
#[test]
fn abandoned_match_never_gives_another_champion_a_rika() {
    let m = the_mod();
    let mut abandoned = World::new(SimOriginKindV1::ClientMatchView, 106, 0x1006, &[2]);
    m.spawn(&mut abandoned, 2);
    m.match_start(&mut abandoned);
    m.ticks(&mut abandoned, 100);
    // 没有 is_end：被放弃

    let mut next = World::new(SimOriginKindV1::ClientMatchView, 107, 0x1007, &[6]);
    m.spawn(&mut next, 6);
    m.match_start(&mut next);
    m.ticks(&mut next, 200);
    assert!(next.spawns.iter().all(|s| s.1 == 6), "only Yuta (6) summons; spawns {:?}", next.spawns);
    assert_eq!(next.rikas_of_team(1).len(), 1, "Yuta's team has its Rika; spawns {:?}", next.spawns);
    assert_eq!(next.rikas_of_team(0).len(), 0, "no Rika for the other team");
    m.end(&mut next);
}

/// 同一身份的模拟重跑（回放看到一半退出，再看一遍）：第二遍从头开始，时间表与第一遍一致。
#[test]
fn rerun_with_the_same_identity_starts_clean() {
    let m = the_mod();
    let replay = |world: &mut World| world.origin.replay_id = 9;
    let mut first = World::new(SimOriginKindV1::ClientReplay, 108, 0x1008, &[2]);
    replay(&mut first);
    m.spawn(&mut first, 2);
    m.match_start(&mut first);
    m.ticks(&mut first, 500);
    // 第一遍看到一半退出（没有 is_end）

    let mut second = World::new(SimOriginKindV1::ClientReplay, 108, 0x1008, &[2]);
    replay(&mut second);
    m.spawn(&mut second, 2);
    m.match_start(&mut second);
    m.ticks(&mut second, 100);
    assert_eq!(second.spawns.len(), 1, "spawns {:?}", second.spawns);
    assert_eq!(second.spawns[0].2, first.spawns[0].2, "same schedule as the first viewing");
    assert!(
        !second.buff_names(2).iter().any(|n| n.starts_with("yuta_mark_")),
        "no marks carried over: {:?}",
        second.buff_names(2)
    );
    m.end(&mut second);
}

/// 里香在场时乙骨真的有 +50% 暴击；里香死了光环撤掉；重召的里香继承乙骨的噬魂成长。
#[test]
fn crit_aura_and_growth_follow_rika() {
    let m = the_mod();
    let mut world = World::new(SimOriginKindV1::ClientMatchView, 109, 0x1009, &[2]);
    let yuta = m.spawn(&mut world, 2);
    m.match_start(&mut world);
    m.ticks(&mut world, 40);
    let rika = world.rikas_of_team(0)[0];
    let aura: Vec<_> = world.ents[2].buffs.iter().filter(|b| b.name() == CRIT_AURA).collect();
    assert_eq!(aura.len(), 1, "aura while Rika is up");
    assert_eq!(aura[0].crit_chance, 50, "aura gives +50 crit");

    m.on_kill(&mut world, yuta, 2, 6);
    m.on_kill(&mut world, yuta, 2, 7);
    assert_eq!(world.ents[2].count(GROWTH_BUFF), 2);
    assert_eq!(world.ents[rika].count(GROWTH_BUFF), 2);

    hurt(&mut world, rika, usize::MAX / 2);
    m.ticks(&mut world, 1);
    assert_eq!(world.ents[2].count(CRIT_AURA), 0, "aura removed once Rika is gone");

    m.ticks(&mut world, 310);
    let again = world.rikas_of_team(0);
    assert_eq!(again.len(), 1, "Rika back after 5 s; spawns {:?}", world.spawns);
    assert_eq!(world.ents[again[0]].count(GROWTH_BUFF), 2, "re-summoned Rika keeps Yuta's growth");

    // 乙骨阵亡（引擎清掉他的 buff）再复活：标记与成长按记录重建，里香不受影响。
    hurt(&mut world, 2, usize::MAX / 2);
    m.ticks(&mut world, 120);
    m.respawn(&mut world, yuta, 2);
    assert_eq!(world.ents[2].count(GROWTH_BUFF), 2, "growth rebuilt on respawn");
    m.ticks(&mut world, 2);
    assert_eq!(world.rikas_of_team(0), again, "Rika outlives Yuta's death");
    m.end(&mut world);
}
