//! 测试用的小世界（只在 `cfg(test)` 里编进来；league_annie_q 的测试用 `#[path]` 引同一份）：在稳定 API 的 `SimVtableV1`
//! 后面放一个假宿主，让被动和原生效果照真的调用走一遍——`spawn_unit` 生成的单位会朝最近的敌人走、够得着就打、到时间就没
//! （「尸体」留不留、单位是不是要到下一 tick 才读得到、有没有这个槽、给不给单位，都可以调），排队的效果到点触发，buff 和
//! 控制按 tick 过期，伤害按「受到的伤害提高」算。这是我们对引擎的**猜想**，只用来检查自己这一边的逻辑（什么时候爆炸、
//! 爆炸几次、标记在不在、日志有没有），不说明游戏里单位真的这样动。

#![allow(dead_code)] // each test crate uses its own part of it

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

/// A timed buff's ticks left; `usize::MAX` for a permanent one.
pub type Left = usize;

#[derive(Clone)]
pub struct MUnit {
    pub name: String,
    pub team: usize,
    pub kind: EntityKindV1,
    pub x: f64,
    pub y: f64,
    pub hp: usize,
    pub max: usize,
    pub stat: StatV1,
    /// An entity is readable under this id.
    pub valid: bool,
    pub targetable: bool,
    pub buffs: Vec<(BuffV1, Left)>,
    pub ccs: Vec<(CcV1, u64)>,
    /// A spawned unit's: its summoner, the tick its time is up, its attack, the tick it may attack again.
    pub summoner: Option<usize>,
    pub until: usize,
    pub attack: Option<UnitAttackV1>,
    pub next_attack: usize,
    /// The tick it died (a spawned unit's body goes `World::body_ticks` later).
    pub died: Option<usize>,
    /// The tick a late spawn becomes readable.
    pub from: usize,
    /// Ticks it is banished for (untargetable, unseen, doing nothing).
    pub banished: usize,
}

pub fn champion(name: &str, team: usize, x: f64, y: f64) -> MUnit {
    MUnit {
        name: name.to_string(),
        team,
        kind: EntityKindV1::Champion,
        x,
        y,
        hp: 1000,
        max: 1000,
        stat: StatV1 { attack: 100, magic_power: 30, hp: 1000, defence: 20, magic_resistance: 20, move_speed: 1100, ..Default::default() },
        valid: true,
        targetable: true,
        buffs: vec![],
        ccs: vec![],
        summoner: None,
        until: usize::MAX,
        attack: None,
        next_attack: 0,
        died: None,
        from: 0,
        banished: 0,
    }
}

pub fn unit(name: &str, kind: EntityKindV1, team: usize, x: f64, y: f64, hp: usize) -> MUnit {
    MUnit { kind, hp, max: hp, ..champion(name, team, x, y) }
}

#[derive(Clone, Copy, Default)]
pub struct MPlayer {
    pub team: usize,
    pub champion: usize,
    pub gold: usize,
    pub cs: usize,
    pub kills: usize,
    /// The `deal` statistic: the damage asked for by his champion and (this world's guess) by the units it summoned.
    pub deal: usize,
}

/// A `spawn_unit` call as the host got it.
#[derive(Clone)]
pub struct SpawnCall {
    pub tick: usize,
    pub name: String,
    pub summoner: usize,
    pub team: usize,
    pub at: (u64, u64),
    pub life: u64,
    pub stat: StatV1,
    pub attack: UnitAttackV1,
    pub gave: Option<usize>,
}

pub struct World {
    pub tick: usize,
    pub units: Vec<MUnit>,
    pub players: Vec<MPlayer>,
    pub queue: Vec<(usize, String, usize, InputTargetV1)>,
    pub views: Vec<(usize, String, InputTargetV1)>,
    pub sounds: Vec<(usize, String)>,
    /// (tick, attacker, target, the amount asked, the damage type's code)
    pub damage: Vec<(usize, usize, usize, usize, u32)>,
    pub fears: Vec<(usize, usize, CcV1)>,
    pub spawns: Vec<SpawnCall>,
    pub kill_log: usize,
    /// The host's ways: has the slot at all, gives a unit, the unit readable only from the next tick, takes queued
    /// effects, how long a dead spawned unit's body stays readable, what kind and name a spawned unit reads back as.
    pub has_spawn: bool,
    pub spawn_ok: bool,
    pub spawn_late: bool,
    /// ... or never (an id that is no unit).
    pub spawn_never: bool,
    pub queue_ok: bool,
    pub body_ticks: usize,
    pub spawn_kind: EntityKindV1,
    pub origin: SimOriginKindV1,
    /// Units the host still gives (None: no end) - a host that runs out of room part-way through several spawns.
    pub spawn_left: Option<usize>,
    /// `entity_set_pos` calls (tick, entity, where) and `entity_banish` calls (tick, caster, target, ticks).
    pub moves: Vec<(usize, usize, (u64, u64))>,
    pub banishes: Vec<(usize, usize, usize, usize)>,
}

impl Default for World {
    fn default() -> World {
        World { tick: 1000, units: vec![], players: vec![], queue: vec![], views: vec![], sounds: vec![], damage: vec![],
                fears: vec![], spawns: vec![], kill_log: 0, has_spawn: true, spawn_ok: true, spawn_late: false, spawn_never: false, queue_ok: true,
                body_ticks: 0, spawn_kind: EntityKindV1::Summon, origin: SimOriginKindV1::ClientMatchView, spawn_left: None,
                moves: vec![], banishes: vec![] }
    }
}

unsafe fn w<'a>(s: *const c_void) -> &'a mut World {
    &mut *(s as *mut World)
}
unsafe fn u<'a>(s: *const c_void, h: EntityHandleV1) -> Option<&'a mut MUnit> {
    w(s).units.get_mut(h.id()?).filter(|e| e.valid)
}
unsafe fn p<'a>(s: *const c_void, h: PlayerHandleV1) -> Option<&'a mut MPlayer> {
    w(s).players.get_mut(h.id()?)
}
fn text<'a>(ptr: *const u8, n: usize) -> &'a str {
    unsafe { std::str::from_utf8(std::slice::from_raw_parts(ptr, n)).unwrap() }
}

unsafe extern "C" fn tick(s: *const c_void) -> usize {
    w(s).tick
}
unsafe extern "C" fn origin(s: *const c_void, out: *mut SimOriginV1) -> bool {
    *out = SimOriginV1 { kind: w(s).origin.code(), match_id: 7, set_index: 1, ..Default::default() };
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
    u(s, h).is_some_and(|e| e.hp > 0 && e.died.is_none())
}
unsafe extern "C" fn is_champion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.kind == EntityKindV1::Champion)
}
unsafe extern "C" fn is_minion(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.kind == EntityKindV1::Minion)
}
unsafe extern "C" fn is_tower(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.kind == EntityKindV1::Tower)
}
unsafe extern "C" fn targetable(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.targetable && e.banished == 0)
}
unsafe extern "C" fn kind(s: *const c_void, h: EntityHandleV1) -> u32 {
    u(s, h).map_or(u32::MAX, |e| e.kind.code())
}
unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.team)
}
unsafe extern "C" fn radius(_: *const c_void, _: EntityHandleV1) -> usize {
    10_000
}
unsafe extern "C" fn interval(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).and_then(|e| e.attack).map_or(0, |a| a.cooltime)
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
    (*x, *y) = (e.x.round().max(0.0) as u64, e.y.round().max(0.0) as u64);
    true
}
unsafe extern "C" fn hp(s: *const c_void, h: EntityHandleV1, now: *mut usize, max: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*now, *max) = (e.hp, e.max);
    true
}
unsafe extern "C" fn stat(s: *const c_void, h: EntityHandleV1, out: *mut StatV1) -> bool {
    let Some(e) = u(s, h) else { return false };
    *out = e.stat;
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
    if let Some(e) = w(s).units.get_mut(id).filter(|e| e.valid) {
        let left = if (*b).duration_kind == BuffDurationV1::Time.code() { (*b).duration_tick } else { usize::MAX };
        e.buffs.push((*b, left));
    }
}
unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, n: *const u8, len: usize) -> usize {
    let name = text(n, len).to_string();
    let Some(e) = u(s, h) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.0.name() != name);
    before - e.buffs.len()
}
unsafe extern "C" fn apply_cc(s: *mut c_void, id: usize, cc: *const CcV1) {
    let world = w(s);
    let tick = world.tick;
    if (*cc).kind == CcKindV1::Fear.code() {
        world.fears.push((tick, id, *cc));
    }
    if let Some(e) = world.units.get_mut(id).filter(|e| e.valid) {
        e.ccs.push((*cc, (*cc).tick));
    }
}
unsafe extern "C" fn queue_effect(s: *mut c_void, n: *const u8, len: usize, _: u32, caster: usize, input: *const InputTargetV1,
                                  delay: usize) -> bool {
    let world = w(s);
    if !world.queue_ok {
        return false;
    }
    world.queue.push((world.tick + delay, text(n, len).to_string(), caster, *input));
    true
}
unsafe extern "C" fn damage_typed(s: *mut c_void, attacker: usize, target: usize, amount: usize, dtype: u32, _: u32) -> bool {
    let world = w(s);
    let tick = world.tick;
    world.damage.push((tick, attacker, target, amount, dtype));
    world.credit(attacker, amount);
    world.hurt(target, amount);
    true
}
unsafe extern "C" fn view_effect(s: *mut c_void, n: *const u8, len: usize, _: usize, input: *const InputTargetV1, _: u64, _: u64,
                                 _: u64) -> bool {
    let world = w(s);
    let tick = world.tick;
    world.views.push((tick, text(n, len).into(), *input));
    true
}
unsafe extern "C" fn sfx(s: *mut c_void, n: *const u8, len: usize, _: usize, _: *const InputTargetV1) -> bool {
    let world = w(s);
    let tick = world.tick;
    world.sounds.push((tick, text(n, len).into()));
    true
}
unsafe extern "C" fn set_hp(s: *mut c_void, h: EntityHandleV1, hp: usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    e.hp = hp.min(e.max);
    true
}
#[allow(clippy::too_many_arguments)]
unsafe extern "C" fn spawn_unit(s: *mut c_void, n: *const u8, len: usize, summoner: usize, team: usize, x: u64, y: u64, life: u64,
                                stat: *const StatV1, attack: *const UnitAttackV1) -> usize {
    let world = w(s);
    let mut call = SpawnCall { tick: world.tick, name: text(n, len).to_string(), summoner, team, at: (x, y), life, stat: *stat,
                               attack: *attack, gave: None };
    if !world.spawn_ok || world.spawn_left == Some(0) {
        world.spawns.push(call);
        return usize::MAX;
    }
    if let Some(n) = world.spawn_left.as_mut() {
        *n -= 1;
    }
    let id = world.units.len();
    call.gave = Some(id);
    world.spawns.push(call);
    let mut e = unit(text(n, len), world.spawn_kind, team, x as f64, y as f64, (*stat).hp);
    (e.stat, e.summoner, e.until, e.attack) = (*stat, Some(summoner), world.tick + life as usize, Some(*attack));
    if world.spawn_never {
        e.valid = false;
    } else if world.spawn_late {
        (e.valid, e.from) = (false, world.tick + 1);
    }
    world.units.push(e);
    id
}
unsafe extern "C" fn set_pos(s: *mut c_void, h: EntityHandleV1, x: u64, y: u64) -> bool {
    let world = w(s);
    let tick = world.tick;
    let Some(id) = h.id() else { return false };
    let Some(e) = world.units.get_mut(id).filter(|e| e.valid) else { return false };
    (e.x, e.y) = (x as f64, y as f64);
    world.moves.push((tick, id, (x, y)));
    true
}
#[allow(clippy::too_many_arguments)]
unsafe extern "C" fn banish(s: *mut c_void, caster: usize, h: EntityHandleV1, ticks: usize, _: *const u8, _: usize, _: *const u8,
                            _: usize) -> bool {
    let world = w(s);
    let tick = world.tick;
    let Some(id) = h.id() else { return false };
    let Some(e) = world.units.get_mut(id).filter(|e| e.valid) else { return false };
    e.banished = ticks;
    world.banishes.push((tick, caster, id, ticks));
    true
}
unsafe extern "C" fn champion_count(s: *const c_void) -> usize {
    w(s).units.iter().filter(|e| e.kind == EntityKindV1::Champion).count()
}
unsafe extern "C" fn champion_id_at(s: *const c_void, i: usize) -> usize {
    w(s).units.iter().enumerate().filter(|(_, e)| e.kind == EntityKindV1::Champion).nth(i).map_or(usize::MAX, |(k, _)| k)
}
unsafe extern "C" fn player_count(s: *const c_void) -> usize {
    w(s).players.len()
}
unsafe extern "C" fn player_at(s: *const c_void, i: usize) -> PlayerHandleV1 {
    if i < w(s).players.len() { PlayerHandleV1::from_id(i) } else { PlayerHandleV1::NULL }
}
unsafe extern "C" fn player_valid(s: *const c_void, h: PlayerHandleV1) -> bool {
    p(s, h).is_some()
}
unsafe extern "C" fn player_champion(s: *const c_void, h: PlayerHandleV1) -> EntityHandleV1 {
    p(s, h).map_or(EntityHandleV1::NULL, |pl| EntityHandleV1::from_id(pl.champion))
}
unsafe extern "C" fn player_team(s: *const c_void, h: PlayerHandleV1) -> usize {
    p(s, h).map_or(0, |pl| pl.team)
}
unsafe extern "C" fn player_gold(s: *const c_void, h: PlayerHandleV1) -> usize {
    p(s, h).map_or(0, |pl| pl.gold)
}
unsafe extern "C" fn player_cs(s: *const c_void, h: PlayerHandleV1) -> usize {
    p(s, h).map_or(0, |pl| pl.cs)
}
unsafe extern "C" fn player_kills(s: *const c_void, h: PlayerHandleV1) -> usize {
    p(s, h).map_or(0, |pl| pl.kills)
}
unsafe extern "C" fn kill_log_count(s: *const c_void) -> usize {
    w(s).kill_log
}
unsafe extern "C" fn statistics(s: *const c_void, h: PlayerHandleV1, path: *const u8, path_len: usize, buf: *mut u8, cap: usize,
                                len: *mut usize) -> bool {
    let Some(pl) = p(s, h) else { return false };
    if text(path, path_len) != "deal" {
        return false;
    }
    let out = pl.deal.to_string();
    *len = out.len();
    if !buf.is_null() {
        std::ptr::copy_nonoverlapping(out.as_ptr(), buf, out.len().min(cap));
    }
    true
}

fn vtable(world: &World) -> SimVtableV1 {
    let mut vt: SimVtableV1 = unsafe { zeroed() };
    vt.size = size_of::<SimVtableV1>();
    vt.tick = Some(tick);
    vt.sim_origin = Some(origin);
    vt.entity_count = Some(count);
    vt.entity_at = Some(at);
    vt.entity_is_valid = Some(valid);
    vt.entity_is_alive = Some(alive);
    vt.entity_is_champion = Some(is_champion);
    vt.entity_is_minion = Some(is_minion);
    vt.entity_is_tower = Some(is_tower);
    vt.entity_is_targetable = Some(targetable);
    vt.entity_kind = Some(kind);
    vt.entity_team = Some(team);
    vt.entity_radius = Some(radius);
    vt.entity_attack_interval = Some(interval);
    vt.entity_name = Some(name);
    vt.entity_pos = Some(pos);
    vt.entity_hp = Some(hp);
    vt.entity_stat = Some(stat);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.entity_cc_count = Some(cc_count);
    vt.entity_cc_at = Some(cc_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.apply_cc = Some(apply_cc);
    vt.queue_effect = Some(queue_effect);
    vt.deal_damage_typed = Some(damage_typed);
    vt.play_view_effect = Some(view_effect);
    vt.play_sfx = Some(sfx);
    vt.entity_set_hp = Some(set_hp);
    vt.spawn_unit = if world.has_spawn { Some(spawn_unit) } else { None };
    vt.entity_set_pos = Some(set_pos);
    vt.entity_banish = Some(banish);
    vt.champion_count = Some(champion_count);
    vt.champion_id_at = Some(champion_id_at);
    vt.player_count = Some(player_count);
    vt.player_at = Some(player_at);
    vt.player_is_valid = Some(player_valid);
    vt.player_champion = Some(player_champion);
    vt.player_team = Some(player_team);
    vt.player_gold = Some(player_gold);
    vt.player_cs = Some(player_cs);
    vt.player_kills = Some(player_kills);
    vt.kill_log_count = Some(kill_log_count);
    vt.player_statistics_json = Some(statistics);
    vt
}

fn far(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

impl World {
    /// A call into the code under test with this world behind the stable API: the raw context (the exported vtables
    /// take it) ...
    pub fn ctx<R>(&mut self, f: impl FnOnce(*mut SimCtxV1) -> R) -> R {
        let vt = vtable(self);
        let mut ctx = SimCtxV1 { size: size_of::<SimCtxV1>(), sim: &vt, frame: std::ptr::null(), state: self as *mut World as *mut c_void };
        f(&mut ctx)
    }

    /// ... or the wrapper the traits take.
    pub fn sim<R>(&mut self, f: impl FnOnce(&mut StableSim<'_>) -> R) -> R {
        self.ctx(|ctx| {
            let mut sim = unsafe { StableSim::from_raw(ctx) }.expect("a simulation context");
            f(&mut sim)
        })
    }

    /// The queued effects due now, oldest first (taken off the queue).
    pub fn due(&mut self) -> Vec<(String, usize, InputTargetV1)> {
        let mut out = Vec::new();
        while let Some(i) = self.queue.iter().position(|q| q.0 <= self.tick) {
            let (_, name, caster, input) = self.queue.remove(i);
            out.push((name, caster, input));
        }
        out
    }

    /// The `deal` statistic of the player whose champion is `unit`.
    pub fn credit(&mut self, unit: usize, amount: usize) {
        if let Some(pl) = self.players.iter_mut().find(|pl| pl.champion == unit) {
            pl.deal += amount;
        }
    }

    /// Damage as the engine would take it off: `damaged_amplify` of the unit's buffs added, nothing else.
    pub fn hurt(&mut self, id: usize, amount: usize) {
        let tick = self.tick;
        let Some(e) = self.units.get_mut(id).filter(|e| e.valid && e.died.is_none()) else { return };
        let more: usize = e.buffs.iter().map(|b| b.0.damaged_amplify).sum();
        e.hp = e.hp.saturating_sub(amount * (100 + more) / 100);
        if e.hp == 0 {
            e.died = Some(tick);
        }
    }

    /// The end of a tick: the spawned units act (walk to the nearest enemy, hit it in reach, go at their time), buffs
    /// and crowd control run down, bodies go, late spawns appear. Then the next tick.
    pub fn step(&mut self) {
        let tick = self.tick;
        for i in 0..self.units.len() {
            let me = self.units[i].clone();
            let Some(attack) = me.attack else { continue };
            if !me.valid || me.died.is_some() {
                continue;
            }
            if tick >= me.until {
                self.units[i].died = Some(tick);
                continue;
            }
            if me.banished > 0 {
                continue;
            }
            let foe = self.units.iter().enumerate()
                .filter(|(_, o)| o.valid && o.died.is_none() && o.hp > 0 && o.team != me.team && o.kind != EntityKindV1::Tower
                                 && o.banished == 0)
                .map(|(k, o)| (k, far((o.x, o.y), (me.x, me.y))))
                .min_by(|a, b| a.1.total_cmp(&b.1));
            let Some((k, d)) = foe else { continue };
            if d <= attack.range as f64 + 5_000.0 {
                if tick >= me.next_attack {
                    self.units[i].next_attack = tick + attack.cooltime;
                    let amount = attack.attack + me.stat.attack * attack.attack_ratio / 100;
                    self.damage.push((tick, i, k, amount, DamageTypeV1::Ad.code()));
                    self.credit(me.summoner.unwrap_or(i), amount);
                    self.hurt(k, amount);
                }
            } else if d > 0.0 {
                let (ox, oy) = (self.units[k].x, self.units[k].y);
                let s = (me.stat.move_speed as f64).min(d);
                self.units[i].x += (ox - me.x) / d * s;
                self.units[i].y += (oy - me.y) / d * s;
            }
        }
        let body = self.body_ticks;
        for e in self.units.iter_mut() {
            e.buffs.iter_mut().for_each(|b| {
                if b.1 != usize::MAX {
                    b.1 = b.1.saturating_sub(1);
                }
            });
            e.buffs.retain(|b| b.1 > 0);
            e.ccs.iter_mut().for_each(|c| c.1 = c.1.saturating_sub(1));
            e.ccs.retain(|c| c.1 > 0);
            e.banished = e.banished.saturating_sub(1);
            if e.summoner.is_some() {
                if !e.valid && e.died.is_none() && e.from != 0 && tick + 1 >= e.from {
                    e.valid = true;
                }
                if e.died.is_some_and(|d| tick >= d + body) {
                    e.valid = false;
                }
            }
        }
        self.tick += 1;
    }

    pub fn has(&self, id: usize, name: &str) -> bool {
        self.units[id].buffs.iter().any(|b| b.0.name() == name)
    }

    pub fn viewed(&self, name: &str) -> usize {
        self.views.iter().filter(|v| v.1 == name).count()
    }

    pub fn heard(&self, name: &str) -> usize {
        self.sounds.iter().filter(|v| v.1 == name).count()
    }

    /// The damage dealt by `attacker` of the damage type `dtype`: (target, amount) in order.
    pub fn dealt(&self, attacker: usize, dtype: DamageTypeV1) -> Vec<(usize, usize)> {
        self.damage.iter().filter(|d| d.1 == attacker && d.4 == dtype.code()).map(|d| (d.2, d.3)).collect()
    }
}
