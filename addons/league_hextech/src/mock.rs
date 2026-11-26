//! 测试用的一份小模拟（大小龙 mock.rs 的缩小版）：两个水晶、两座塔、十个英雄（一个玩家一个），玩家有队伍、分路、等级；
//! 英雄有名字、buff、死活；比分差、时钟、种子、来历。0.3.0 加上触发类海克斯要读写的：生命、护盾、位置、属性、控制、选不选得中，
//! 玩家的伤害统计、四个冷却，击杀记录；本包打出的伤害、回血、护盾、控制、减冷却都记下来（测试看），伤害和回血也真的改生命。

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

#[derive(Clone)]
pub struct Unit {
    pub kind: EntityKindV1,
    /// 本包不按实体读队伍（按玩家读），留着让这份假模拟像真的
    #[allow(dead_code)]
    pub team: usize,
    pub alive: bool,
    pub name: String,
    pub buffs: Vec<BuffV1>,
    pub hp: usize,
    pub max: usize,
    pub shield: usize,
    pub pos: (u64, u64),
    pub stat: StatV1,
    pub cc: Vec<CcV1>,
    pub targetable: bool,
}

impl Unit {
    fn new(kind: EntityKindV1, team: usize, name: &str) -> Unit {
        Unit { kind, team, alive: true, name: name.into(), buffs: Vec::new(), hp: 2000, max: 2000, shield: 0, pos: (0, 0),
               stat: StatV1 { attack: 200, magic_power: 300, hp: 2000, ..StatV1::default() }, cc: Vec::new(),
               targetable: true }
    }
}

#[derive(Clone)]
pub struct Player {
    pub team: usize,
    pub lane: u32,
    pub champ: usize,
    pub level: usize,
    /// 伤害统计 `deal`（None：读不到）
    pub deal: Option<u64>,
    /// 普攻、技能、技能 2、大招还剩几 tick
    pub cds: [usize; 4],
}

/// 本包打出的一下：(打的人, 被打的, 多少, 伤害种类, 攻击种类)。
pub type Hit = (usize, usize, usize, u32, u32);

#[derive(Clone, Default)]
pub struct World {
    pub tick: usize,
    pub seed: u64,
    pub origin: Option<SimOriginV1>,
    pub units: Vec<Unit>,
    pub players: Vec<Player>,
    pub end: bool,
    /// 蓝色方的比分差
    pub diff: i32,
    /// 这些种类的实体不收 buff
    pub refuse: Vec<EntityKindV1>,
    pub kills: Vec<KillLogV1>,
    // 本包做了什么
    pub hits: Vec<Hit>,
    pub heals: Vec<(usize, usize, usize)>,
    pub shields: Vec<(usize, usize, usize)>,
    pub ccs: Vec<(usize, CcV1)>,
    pub reduced: Vec<(usize, u32, usize)>,
}

impl World {
    /// 两个水晶、两座塔，然后一个玩家一个英雄：蓝色方 0-4 号是分路 0-4，红色方 5-9 号。英雄站成两排：蓝色方在 y 500000，
    /// 红色方在 y 600000，x 从 100000 起每人隔 200000（隔得很远：测试自己把要打的人挪近）。
    pub fn new(seed: u64, kind: SimOriginKindV1, heroes: [&str; 10]) -> World {
        let mut w = World { seed, ..World::default() };
        w.origin = Some(SimOriginV1 { kind: kind.code(), match_id: 77, set_index: 2, ..SimOriginV1::default() });
        for (team, kind) in [(0, EntityKindV1::Nexus), (1, EntityKindV1::Nexus), (0, EntityKindV1::Tower),
                             (1, EntityKindV1::Tower)] {
            w.units.push(Unit::new(kind, team, "structure"));
        }
        for (i, h) in heroes.iter().enumerate() {
            let team = i / 5;
            let mut u = Unit::new(EntityKindV1::Champion, team, h);
            u.pos = (100_000 + (i % 5) as u64 * 200_000, 500_000 + team as u64 * 100_000);
            w.units.push(u);
            w.players.push(Player { team, lane: (i % 5) as u32, champ: w.units.len() - 1, level: 1, deal: Some(0),
                                    cds: [0; 4] });
        }
        w
    }

    pub fn champ(&self, player: usize) -> &Unit {
        &self.units[self.players[player].champ]
    }

    pub fn champ_mut(&mut self, player: usize) -> &mut Unit {
        let c = self.players[player].champ;
        &mut self.units[c]
    }

    /// 这个玩家英雄的实体编号。
    pub fn ent(&self, player: usize) -> usize {
        self.players[player].champ
    }

    /// 这个玩家英雄身上本包的海克斯 buff（名字）。
    pub fn augs(&self, player: usize) -> Vec<String> {
        self.champ(player)
            .buffs
            .iter()
            .filter(|b| b.name().starts_with(crate::augments::BUFF_PREFIX))
            .map(|b| b.name().to_string())
            .collect()
    }

    /// 这个玩家英雄身上叫这个名字的 buff 有几个。
    pub fn has(&self, player: usize, name: &str) -> usize {
        self.champ(player).buffs.iter().filter(|b| b.name() == name).count()
    }

    pub fn die(&mut self, player: usize) {
        let c = self.players[player].champ;
        self.units[c].alive = false;
    }

    /// 复活成一个新的实体：mod 挂的 buff 都跟着旧的走了。
    pub fn respawn(&mut self, player: usize) {
        let old = self.players[player].champ;
        let mut fresh = self.units[old].clone();
        self.units[old].alive = false;
        fresh.buffs.clear();
        fresh.alive = true;
        fresh.hp = fresh.max;
        fresh.shield = 0;
        fresh.cc.clear();
        self.units.push(fresh);
        self.players[player].champ = self.units.len() - 1;
    }

    /// 别人打了 `player` 的英雄一下（掉生命，不记在本包的伤害里）。
    pub fn hurt(&mut self, player: usize, amount: usize) {
        let u = self.champ_mut(player);
        let from_shield = amount.min(u.shield);
        u.shield -= from_shield;
        u.hp = u.hp.saturating_sub(amount - from_shield);
    }

    /// 本包打出的、打在这个玩家英雄身上的伤害。
    pub fn hits_on(&self, player: usize) -> Vec<Hit> {
        let e = self.ent(player);
        self.hits.iter().copied().filter(|h| h.1 == e).collect()
    }
}

unsafe fn w<'a>(s: *const c_void) -> &'a mut World {
    &mut *(s as *mut World)
}
unsafe fn u<'a>(s: *const c_void, h: EntityHandleV1) -> Option<&'a mut Unit> {
    w(s).units.get_mut(h.id()?)
}
unsafe fn p<'a>(s: *const c_void, h: PlayerHandleV1) -> Option<&'a mut Player> {
    w(s).players.get_mut(h.id()?)
}
unsafe fn text(ptr: *const u8, len: usize) -> String {
    std::str::from_utf8(std::slice::from_raw_parts(ptr, len)).unwrap_or("").to_string()
}
unsafe fn out(v: &str, buf: *mut u8, cap: usize, len: *mut usize) -> bool {
    let b = v.as_bytes();
    *len = b.len();
    if !buf.is_null() {
        std::ptr::copy_nonoverlapping(b.as_ptr(), buf, b.len().min(cap));
    }
    true
}
unsafe extern "C" fn tick(s: *const c_void) -> usize {
    w(s).tick
}
unsafe extern "C" fn seed(s: *const c_void) -> u64 {
    w(s).seed
}
unsafe extern "C" fn is_end(s: *const c_void) -> bool {
    w(s).end
}
unsafe extern "C" fn score_diff(s: *const c_void, team: usize) -> i32 {
    if team == 0 {
        w(s).diff
    } else {
        -w(s).diff
    }
}
unsafe extern "C" fn count(s: *const c_void) -> usize {
    w(s).units.len()
}
unsafe extern "C" fn at(s: *const c_void, i: usize) -> EntityHandleV1 {
    if i < w(s).units.len() {
        EntityHandleV1::from_id(i)
    } else {
        EntityHandleV1::NULL
    }
}
unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some()
}
unsafe extern "C" fn kind(s: *const c_void, h: EntityHandleV1) -> u32 {
    u(s, h).map_or(u32::MAX, |e| e.kind.code())
}
unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.alive)
}
unsafe extern "C" fn buff_count(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.buffs.len())
}
unsafe extern "C" fn buff_at(s: *const c_void, h: EntityHandleV1, i: usize, o: *mut BuffV1) -> bool {
    let Some(b) = u(s, h).and_then(|e| e.buffs.get(i)) else { return false };
    *o = *b;
    true
}
unsafe extern "C" fn add_buff(s: *mut c_void, id: usize, b: *const BuffV1) {
    let refuse = w(s).refuse.clone();
    if let Some(e) = w(s).units.get_mut(id) {
        if !refuse.contains(&e.kind) {
            e.buffs.push(*b);
        }
    }
}
unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, name: *const u8, len: usize) -> usize {
    let name = text(name, len);
    let Some(e) = u(s, h) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.name() != name);
    before - e.buffs.len()
}
unsafe extern "C" fn stack_buff(s: *mut c_void, h: EntityHandleV1, b: *const BuffV1, most: usize, refresh: u32) -> usize {
    let Some(e) = u(s, h) else { return 0 };
    let b = *b;
    if refresh != 0 {
        for x in e.buffs.iter_mut().filter(|x| x.name() == b.name()) {
            x.duration_tick = b.duration_tick;
        }
    }
    let n = e.buffs.iter().filter(|x| x.name() == b.name()).count();
    if most == 0 || n < most {
        e.buffs.push(b);
        n + 1
    } else {
        n
    }
}
unsafe extern "C" fn name(s: *const c_void, h: EntityHandleV1, buf: *mut u8, cap: usize, len: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    out(&e.name.clone(), buf, cap, len)
}
unsafe extern "C" fn hp(s: *const c_void, h: EntityHandleV1, cur: *mut usize, max: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    *cur = e.hp;
    *max = e.max;
    true
}
unsafe extern "C" fn shield(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.shield)
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    *x = e.pos.0;
    *y = e.pos.1;
    true
}
unsafe extern "C" fn stat(s: *const c_void, h: EntityHandleV1, o: *mut StatV1) -> bool {
    let Some(e) = u(s, h) else { return false };
    *o = e.stat;
    true
}
unsafe extern "C" fn targetable(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.targetable)
}
unsafe extern "C" fn cc_count(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.cc.len())
}
unsafe extern "C" fn cc_at(s: *const c_void, h: EntityHandleV1, i: usize, o: *mut CcV1) -> bool {
    let Some(c) = u(s, h).and_then(|e| e.cc.get(i)) else { return false };
    *o = *c;
    true
}
unsafe extern "C" fn deal_typed(s: *mut c_void, attacker: usize, target: usize, amount: usize, ty: u32, at: u32) -> bool {
    let world = w(s);
    world.hits.push((attacker, target, amount, ty, at));
    if let Some(t) = world.units.get_mut(target) {
        let from_shield = amount.min(t.shield);
        t.shield -= from_shield;
        t.hp = t.hp.saturating_sub(amount - from_shield);
    }
    // 统计算打的人的（游戏里也是）
    if let Some(pl) = world.players.iter_mut().find(|pl| pl.champ == attacker) {
        pl.deal = pl.deal.map(|d| d + amount as u64);
    }
    true
}
unsafe extern "C" fn heal(s: *mut c_void, caster: usize, target: usize, amount: usize) {
    let world = w(s);
    world.heals.push((caster, target, amount));
    if let Some(t) = world.units.get_mut(target) {
        t.hp = (t.hp + amount).min(t.max);
    }
}
unsafe extern "C" fn add_shield(s: *mut c_void, h: EntityHandleV1, amount: usize, ticks: usize) -> bool {
    let world = w(s);
    let Some(id) = h.id() else { return false };
    world.shields.push((id, amount, ticks));
    if let Some(t) = world.units.get_mut(id) {
        t.shield += amount;
    }
    true
}
unsafe extern "C" fn apply_cc(s: *mut c_void, target: usize, c: *const CcV1) {
    let world = w(s);
    world.ccs.push((target, *c));
    if let Some(t) = world.units.get_mut(target) {
        t.cc.push(*c);
    }
}
unsafe extern "C" fn reduce_cd(s: *mut c_void, h: EntityHandleV1, slot: u32, ticks: usize) -> bool {
    let Some(id) = h.id() else { return false };
    w(s).reduced.push((id, slot, ticks));
    true
}
unsafe extern "C" fn towers(s: *const c_void) -> usize {
    w(s).units.iter().filter(|e| e.kind == EntityKindV1::Tower).count()
}
unsafe extern "C" fn tower_at(s: *const c_void, i: usize) -> usize {
    w(s).units.iter().enumerate().filter(|e| e.1.kind == EntityKindV1::Tower).nth(i).map_or(usize::MAX, |e| e.0)
}
unsafe extern "C" fn players(s: *const c_void) -> usize {
    w(s).players.len()
}
unsafe extern "C" fn player_at(s: *const c_void, i: usize) -> PlayerHandleV1 {
    if i < w(s).players.len() {
        PlayerHandleV1::from_id(i)
    } else {
        PlayerHandleV1::NULL
    }
}
unsafe extern "C" fn player_valid(s: *const c_void, h: PlayerHandleV1) -> bool {
    p(s, h).is_some()
}
unsafe extern "C" fn player_champion(s: *const c_void, h: PlayerHandleV1) -> EntityHandleV1 {
    p(s, h).map_or(EntityHandleV1::NULL, |x| EntityHandleV1::from_id(x.champ))
}
unsafe extern "C" fn player_lane(s: *const c_void, h: PlayerHandleV1) -> u32 {
    p(s, h).map_or(u32::MAX, |x| x.lane)
}
unsafe extern "C" fn player_team(s: *const c_void, h: PlayerHandleV1) -> usize {
    p(s, h).map_or(0, |x| x.team)
}
unsafe extern "C" fn player_level(s: *const c_void, h: PlayerHandleV1) -> usize {
    p(s, h).map_or(1, |x| x.level)
}
unsafe extern "C" fn player_cds(s: *const c_void, h: PlayerHandleV1, a: *mut usize, b: *mut usize, c: *mut usize,
                                d: *mut usize) -> bool {
    let Some(x) = p(s, h) else { return false };
    (*a, *b, *c, *d) = (x.cds[0], x.cds[1], x.cds[2], x.cds[3]);
    true
}
unsafe extern "C" fn player_stats(s: *const c_void, h: PlayerHandleV1, path: *const u8, plen: usize, buf: *mut u8, cap: usize,
                                  len: *mut usize) -> bool {
    let Some(x) = p(s, h) else { return false };
    if text(path, plen) != "deal" {
        return false;
    }
    match x.deal {
        Some(d) => out(&format!("{d}.0"), buf, cap, len),
        None => false,
    }
}
unsafe extern "C" fn kill_count(s: *const c_void) -> usize {
    w(s).kills.len()
}
unsafe extern "C" fn kill_at(s: *const c_void, i: usize, o: *mut KillLogV1) -> bool {
    let Some(k) = w(s).kills.get(i) else { return false };
    *o = *k;
    true
}
unsafe extern "C" fn origin(s: *const c_void, o: *mut SimOriginV1) -> bool {
    match w(s).origin {
        Some(x) if !o.is_null() => {
            *o = x;
            true
        }
        _ => false,
    }
}

/// 在 `world` 上跑 `f`。
pub fn with_sim<R>(world: &mut World, f: impl FnOnce(&mut StableSim<'_>) -> R) -> R {
    let mut vt: SimVtableV1 = unsafe { zeroed() };
    vt.size = size_of::<SimVtableV1>();
    vt.tick = Some(tick);
    vt.seed = Some(seed);
    vt.is_end = Some(is_end);
    vt.score_diff = Some(score_diff);
    vt.entity_count = Some(count);
    vt.entity_at = Some(at);
    vt.entity_is_valid = Some(valid);
    vt.entity_kind = Some(kind);
    vt.entity_is_alive = Some(alive);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.entity_stack_buff = Some(stack_buff);
    vt.entity_name = Some(name);
    vt.entity_hp = Some(hp);
    vt.entity_shield = Some(shield);
    vt.entity_pos = Some(pos);
    vt.entity_stat = Some(stat);
    vt.entity_is_targetable = Some(targetable);
    vt.entity_cc_count = Some(cc_count);
    vt.entity_cc_at = Some(cc_at);
    vt.deal_damage_typed = Some(deal_typed);
    vt.heal = Some(heal);
    vt.entity_add_shield = Some(add_shield);
    vt.apply_cc = Some(apply_cc);
    vt.entity_reduce_cooldown = Some(reduce_cd);
    vt.tower_count = Some(towers);
    vt.tower_id_at = Some(tower_at);
    vt.player_count = Some(players);
    vt.player_at = Some(player_at);
    vt.player_is_valid = Some(player_valid);
    vt.player_champion = Some(player_champion);
    vt.player_lane = Some(player_lane);
    vt.player_team = Some(player_team);
    vt.player_level = Some(player_level);
    vt.player_cooldowns = Some(player_cds);
    vt.player_statistics_json = Some(player_stats);
    vt.kill_log_count = Some(kill_count);
    vt.kill_log_at = Some(kill_at);
    vt.sim_origin = Some(origin);
    let mut ctx = SimCtxV1 {
        size: size_of::<SimCtxV1>(),
        sim: &vt,
        frame: std::ptr::null(),
        state: world as *mut World as *mut c_void,
    };
    let mut sim = unsafe { StableSim::from_raw(&mut ctx) }.expect("a simulation context");
    f(&mut sim)
}
