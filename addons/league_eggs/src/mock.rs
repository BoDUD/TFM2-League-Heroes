//! A small simulation of one's own for the tests (tft's sim_tag::mock way): buildings and champions with a team, a place,
//! life, a name and buffs; players with a team, a lane, a level, takedowns and gold; the kill log; the clock and the
//! simulation's origin; stacked buffs, banishes and their clearing (Leona's shades, Fizz's shark). Only the slots the eggs
//! use.

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

#[derive(Clone)]
pub struct Unit {
    pub kind: EntityKindV1,
    pub team: usize,
    pub at: (u64, u64),
    pub alive: bool,
    pub name: String,
    pub buffs: Vec<BuffV1>,
    /// Banished for this many ticks (0: not), by `entity_banish`, with this lock picture.
    pub banished: usize,
    pub lock: String,
}

#[derive(Clone)]
pub struct Player {
    pub team: usize,
    pub lane: u32,
    pub champ: usize,
    pub level: usize,
    pub alive: bool,
    pub kills: usize,
    pub assists: usize,
    pub gold: i64,
}

#[derive(Clone, Default)]
pub struct World {
    pub tick: usize,
    pub seed: u64,
    pub origin: Option<SimOriginV1>,
    pub units: Vec<Unit>,
    pub players: Vec<Player>,
    pub kills: Vec<KillLogV1>,
    pub end: bool,
    /// Entities of these kinds take no buffs (a mode where the tag cannot be hung there).
    pub refuse: Vec<EntityKindV1>,
    /// The host refuses every banish.
    pub refuse_banish: bool,
}

impl World {
    /// Two nexuses, two towers, then one champion a player: team 0 lanes 0-4 are players 0-4, team 1 players 5-9.
    pub fn new(seed: u64, kind: SimOriginKindV1, heroes: [&str; 10]) -> World {
        let mut w = World { seed, ..World::default() };
        w.origin = Some(SimOriginV1 { kind: kind.code(), match_id: 77, set_index: 2, ..SimOriginV1::default() });
        for (team, kind) in [(0, EntityKindV1::Nexus), (1, EntityKindV1::Nexus), (0, EntityKindV1::Tower), (1, EntityKindV1::Tower)] {
            w.units.push(Unit { kind, team, at: (0, 0), alive: true, name: String::new(), buffs: Vec::new(), banished: 0,
                                lock: String::new() });
        }
        for (i, h) in heroes.iter().enumerate() {
            let team = i / 5;
            w.units.push(Unit { kind: EntityKindV1::Champion, team, at: (100_000 * i as u64, 100_000), alive: true,
                                name: h.to_string(), buffs: Vec::new(), banished: 0, lock: String::new() });
            w.players.push(Player { team, lane: (i % 5) as u32, champ: w.units.len() - 1, level: 1, alive: true,
                                    kills: 0, assists: 0, gold: 0 });
        }
        w
    }

    pub fn champ(&self, player: usize) -> &Unit {
        &self.units[self.players[player].champ]
    }

    pub fn has(&self, player: usize, buff: &str) -> Option<BuffV1> {
        self.champ(player).buffs.iter().find(|b| b.name() == buff).copied()
    }

    /// `victim` taken down by `killer` with `assists` (players), as the game's kill log has it.
    pub fn kill(&mut self, victim: usize, killer: usize, assists: &[usize]) {
        let (k, v) = (&self.players[killer], &self.players[victim]);
        let mut e = KillLogV1 { tick: self.tick, killer_team: k.team, killer_position: k.lane, killed_position: v.lane,
                                assist_count: assists.len() as u32, ..KillLogV1::default() };
        for (i, a) in assists.iter().enumerate() {
            e.assist_positions[i] = self.players[*a].lane;
        }
        self.kills.push(e);
        self.players[killer].kills += 1;
        for a in assists {
            self.players[*a].assists += 1;
        }
    }

    /// The player dies (his champion's buffs go with it) and comes back as a new entity.
    pub fn respawn(&mut self, player: usize) {
        let old = self.players[player].champ;
        let mut fresh = self.units[old].clone();
        self.units[old].alive = false;
        fresh.buffs.clear();
        (fresh.banished, fresh.lock) = (0, String::new());
        self.units.push(fresh);
        self.players[player].champ = self.units.len() - 1;
    }

    /// The player's champion dies where he stands (his body keeps its buffs, as the game's dead units do).
    pub fn die(&mut self, player: usize) {
        let c = self.players[player].champ;
        self.units[c].alive = false;
        self.players[player].alive = false;
    }

    pub fn count(&self, player: usize, buff: &str) -> usize {
        self.champ(player).buffs.iter().filter(|b| b.name() == buff).count()
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
unsafe extern "C" fn tick(s: *const c_void) -> usize {
    w(s).tick
}
unsafe extern "C" fn seed(s: *const c_void) -> u64 {
    w(s).seed
}
unsafe extern "C" fn is_end(s: *const c_void) -> bool {
    w(s).end
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
unsafe extern "C" fn kind(s: *const c_void, h: EntityHandleV1) -> u32 {
    u(s, h).map_or(u32::MAX, |e| e.kind.code())
}
unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
    u(s, h).is_some_and(|e| e.alive)
}
unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.team)
}
unsafe extern "C" fn buff_count(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.buffs.len())
}
unsafe extern "C" fn buff_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut BuffV1) -> bool {
    let Some(b) = u(s, h).and_then(|e| e.buffs.get(i)) else { return false };
    *out = *b;
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
    let name = std::str::from_utf8(std::slice::from_raw_parts(name, len)).unwrap_or("").to_string();
    let Some(e) = u(s, h) else { return 0 };
    let before = e.buffs.len();
    e.buffs.retain(|b| b.name() != name);
    before - e.buffs.len()
}
unsafe extern "C" fn name(s: *const c_void, h: EntityHandleV1, buf: *mut u8, cap: usize, out: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    let b = e.name.as_bytes();
    *out = b.len();
    if !buf.is_null() {
        std::ptr::copy_nonoverlapping(b.as_ptr(), buf, b.len().min(cap));
    }
    true
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*x, *y) = e.at;
    true
}
unsafe extern "C" fn stack_buff(s: *mut c_void, h: EntityHandleV1, b: *const BuffV1, max: usize, refresh: u32) -> usize {
    let Some(e) = u(s, h) else { return 0 };
    let b = *b;
    if refresh != 0 {
        for x in e.buffs.iter_mut().filter(|x| x.name() == b.name()) {
            (x.duration_kind, x.duration_tick) = (b.duration_kind, b.duration_tick);
        }
    }
    let n = e.buffs.iter().filter(|x| x.name() == b.name()).count();
    if max == 0 || n < max {
        e.buffs.push(b);
        return n + 1;
    }
    n
}
unsafe extern "C" fn banish(s: *mut c_void, _caster: usize, h: EntityHandleV1, ticks: usize, lock: *const u8, lock_len: usize,
                            _end: *const u8, _end_len: usize) -> bool {
    if w(s).refuse_banish {
        return false;
    }
    let lock = std::str::from_utf8(std::slice::from_raw_parts(lock, lock_len)).unwrap_or("").to_string();
    let Some(e) = u(s, h) else { return false };
    (e.banished, e.lock) = (ticks, lock);
    true
}
unsafe extern "C" fn clear_cc(s: *mut c_void, h: EntityHandleV1) -> usize {
    let Some(e) = u(s, h) else { return 0 };
    let was = e.banished > 0;
    (e.banished, e.lock) = (0, String::new());
    was as usize
}
unsafe extern "C" fn champions(s: *const c_void) -> usize {
    w(s).units.iter().filter(|e| e.kind == EntityKindV1::Champion).count()
}
unsafe extern "C" fn champion_at(s: *const c_void, i: usize) -> usize {
    w(s).units.iter().enumerate().filter(|e| e.1.kind == EntityKindV1::Champion).nth(i).map_or(usize::MAX, |e| e.0)
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
    if i < w(s).players.len() { PlayerHandleV1::from_id(i) } else { PlayerHandleV1::NULL }
}
unsafe extern "C" fn player_valid(s: *const c_void, h: PlayerHandleV1) -> bool {
    p(s, h).is_some()
}
unsafe extern "C" fn player_champion(s: *const c_void, h: PlayerHandleV1) -> EntityHandleV1 {
    p(s, h).map_or(EntityHandleV1::NULL, |x| EntityHandleV1::from_id(x.champ))
}
unsafe extern "C" fn player_level(s: *const c_void, h: PlayerHandleV1) -> usize {
    p(s, h).map_or(1, |x| x.level)
}
unsafe extern "C" fn player_lane(s: *const c_void, h: PlayerHandleV1) -> u32 {
    p(s, h).map_or(u32::MAX, |x| x.lane)
}
unsafe extern "C" fn player_team(s: *const c_void, h: PlayerHandleV1) -> usize {
    p(s, h).map_or(0, |x| x.team)
}
unsafe extern "C" fn player_alive(s: *const c_void, h: PlayerHandleV1) -> bool {
    p(s, h).is_some_and(|x| x.alive)
}
unsafe extern "C" fn player_kills(s: *const c_void, h: PlayerHandleV1) -> usize {
    p(s, h).map_or(0, |x| x.kills)
}
unsafe extern "C" fn player_assists(s: *const c_void, h: PlayerHandleV1) -> usize {
    p(s, h).map_or(0, |x| x.assists)
}
unsafe extern "C" fn add_gold(s: *mut c_void, h: PlayerHandleV1, delta: i64) -> bool {
    let Some(x) = p(s, h) else { return false };
    x.gold = (x.gold + delta).max(0);
    true
}
unsafe extern "C" fn kill_count(s: *const c_void) -> usize {
    w(s).kills.len()
}
unsafe extern "C" fn kill_at(s: *const c_void, i: usize, out: *mut KillLogV1) -> bool {
    let Some(k) = w(s).kills.get(i) else { return false };
    *out = *k;
    true
}
unsafe extern "C" fn distance_sq(s: *const c_void, a: usize, b: usize) -> u64 {
    let (Some(x), Some(y)) = (w(s).units.get(a), w(s).units.get(b)) else { return u64::MAX };
    let (dx, dy) = (x.at.0.abs_diff(y.at.0), x.at.1.abs_diff(y.at.1));
    dx * dx + dy * dy
}
unsafe extern "C" fn origin(s: *const c_void, out: *mut SimOriginV1) -> bool {
    match w(s).origin {
        Some(o) if !out.is_null() => {
            *out = o;
            true
        }
        _ => false,
    }
}

/// `f` run on a simulation of `world`.
pub fn with_sim<R>(world: &mut World, f: impl FnOnce(&mut StableSim<'_>) -> R) -> R {
    let mut vt: SimVtableV1 = unsafe { zeroed() };
    vt.size = size_of::<SimVtableV1>();
    vt.tick = Some(tick);
    vt.seed = Some(seed);
    vt.is_end = Some(is_end);
    vt.entity_count = Some(count);
    vt.entity_at = Some(at);
    vt.entity_is_valid = Some(valid);
    vt.entity_kind = Some(kind);
    vt.entity_is_alive = Some(alive);
    vt.entity_team = Some(team);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.entity_name = Some(name);
    vt.entity_pos = Some(pos);
    vt.entity_stack_buff = Some(stack_buff);
    vt.entity_banish = Some(banish);
    vt.entity_clear_cc = Some(clear_cc);
    vt.champion_count = Some(champions);
    vt.champion_id_at = Some(champion_at);
    vt.tower_count = Some(towers);
    vt.tower_id_at = Some(tower_at);
    vt.player_count = Some(players);
    vt.player_at = Some(player_at);
    vt.player_is_valid = Some(player_valid);
    vt.player_champion = Some(player_champion);
    vt.player_level = Some(player_level);
    vt.player_lane = Some(player_lane);
    vt.player_team = Some(player_team);
    vt.player_is_alive = Some(player_alive);
    vt.player_kills = Some(player_kills);
    vt.player_assists = Some(player_assists);
    vt.player_add_gold = Some(add_gold);
    vt.kill_log_count = Some(kill_count);
    vt.kill_log_at = Some(kill_at);
    vt.distance_sq = Some(distance_sq);
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
