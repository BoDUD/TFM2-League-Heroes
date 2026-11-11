//! A small simulation of one's own for the tests (league_eggs' mock grown for the drakes): buildings, champions,
//! minions and the two epic camps with a kind, a team, a place, health, shields, stats, a name and buffs; players with a
//! team, a lane, cooldowns and the statistics the hook reads (`deal`, `serpen_secure`, `epic_secure`); damage, heals and
//! shields through the engine slots, recorded; the clock and the simulation's origin. Only the slots the hook uses.

use std::ffi::c_void;
use std::mem::{size_of, zeroed};

use mod_api_stable::*;

use super::rules;

#[derive(Clone)]
pub struct Unit {
    pub kind: EntityKindV1,
    pub team: usize,
    pub at: (u64, u64),
    pub alive: bool,
    pub name: String,
    pub buffs: Vec<BuffV1>,
    pub hp: usize,
    pub max: usize,
    pub shield: usize,
    pub stat: StatV1,
    /// Hidden from the other team until this tick (`entity_set_invisible`); hidden by something of its own (a skill).
    pub unseen_until: usize,
    pub stealth: bool,
}

impl Unit {
    pub fn new(kind: EntityKindV1, team: usize, at: (u64, u64), name: &str, max: usize) -> Unit {
        let stat = StatV1 { attack: 100, magic_power: 50, hp: max, ..StatV1::default() };
        Unit { kind, team, at, alive: true, name: name.to_string(), buffs: Vec::new(), hp: max, max, shield: 0, stat,
               unseen_until: 0, stealth: false }
    }
}

#[derive(Clone)]
pub struct Player {
    pub team: usize,
    pub lane: u32,
    pub champ: usize,
    pub deal: u64,
    pub serpen_secure: u64,
    pub epic_secure: u64,
    /// Remaining cooldowns: attack, skill, skill2, ult.
    pub cds: [usize; 4],
}

/// One hit through the engine: (attacker, target, amount, damage type code, attack type code).
pub type Hit = (usize, usize, usize, u32, u32);

#[derive(Clone, Default)]
pub struct World {
    pub tick: usize,
    pub seed: u64,
    pub origin: Option<SimOriginV1>,
    pub units: Vec<Unit>,
    pub players: Vec<Player>,
    pub end: bool,
    /// Entities of these kinds take no buffs.
    pub refuse: Vec<EntityKindV1>,
    /// The host has no statistics slot (the hook falls back to the native buff and to the cooldowns).
    pub no_stats: bool,
    /// The native drake buff the camp gives (the 2027 season patch's numbers by default).
    pub native: Option<BuffV1>,
    pub hits: Vec<Hit>,
    pub heals: Vec<(usize, usize)>,
    pub shields: Vec<(usize, usize, usize)>,
}

pub const SERPEN_AT: (u64, u64) = (700_000, 300_000);
pub const EPIC_AT: (u64, u64) = (300_000, 700_000);

impl World {
    /// Two nexuses, two towers, then one champion a player: team 0 lanes 0-4 are players 0-4, team 1 players 5-9, all
    /// in a row 100000 apart (player i at (100000 i, 100000)).
    pub fn new(seed: u64, kind: SimOriginKindV1, heroes: [&str; 10]) -> World {
        let mut w = World { seed, ..World::default() };
        w.origin = Some(SimOriginV1 { kind: kind.code(), match_id: 77, set_index: 2, ..SimOriginV1::default() });
        for (team, kind, name) in [(0, EntityKindV1::Nexus, "nexus"), (1, EntityKindV1::Nexus, "nexus"),
                                   (0, EntityKindV1::Tower, "tower"), (1, EntityKindV1::Tower, "tower")] {
            w.units.push(Unit::new(kind, team, (0, 0), name, 5000));
        }
        for (i, h) in heroes.iter().enumerate() {
            let team = i / 5;
            w.units.push(Unit::new(EntityKindV1::Champion, team, (100_000 * i as u64, 100_000), h, 1000));
            w.players.push(Player { team, lane: (i % 5) as u32, champ: w.units.len() - 1, deal: 0, serpen_secure: 0,
                                    epic_secure: 0, cds: [0; 4] });
        }
        let mut n = BuffV1::named(rules::NATIVE);
        (n.attack_mult, n.magic_power_mult, n.defence_mult, n.magic_resistance_mult, n.move_speed_mult) = (4, 4, 4, 4, 1);
        w.native = Some(n);
        w
    }

    pub fn champ(&self, player: usize) -> &Unit {
        &self.units[self.players[player].champ]
    }

    pub fn champ_mut(&mut self, player: usize) -> &mut Unit {
        let c = self.players[player].champ;
        &mut self.units[c]
    }

    pub fn has(&self, player: usize, buff: &str) -> Option<BuffV1> {
        self.champ(player).buffs.iter().find(|b| b.name() == buff).copied()
    }

    pub fn count(&self, player: usize, buff: &str) -> usize {
        self.champ(player).buffs.iter().filter(|b| b.name() == buff).count()
    }

    pub fn names(&self, unit: usize) -> Vec<String> {
        self.units[unit].buffs.iter().map(|b| b.name().to_string()).collect()
    }

    /// A unit appears (a camp, a minion): its index.
    pub fn spawn(&mut self, u: Unit) -> usize {
        self.units.push(u);
        self.units.len() - 1
    }

    pub fn spawn_serpen(&mut self) -> usize {
        self.spawn(Unit::new(EntityKindV1::Serpen, 2, SERPEN_AT, "serpen_jungle", 5000))
    }

    pub fn spawn_epic(&mut self) -> usize {
        self.spawn(Unit::new(EntityKindV1::Epic, 2, EPIC_AT, "epic_jungle", 10000))
    }

    /// `by` secures the camp: it dies, the player's secure statistic counts it and - the serpent - every living champion of
    /// his team gets one more native drake buff (as the game does).
    pub fn secure(&mut self, camp: usize, by: usize) {
        self.units[camp].alive = false;
        self.units[camp].hp = 0;
        let team = self.players[by].team;
        if self.units[camp].kind == EntityKindV1::Serpen {
            self.players[by].serpen_secure += 1;
            let n = self.native.expect("the native buff");
            for p in 0..self.players.len() {
                if self.players[p].team == team && self.champ(p).alive {
                    self.champ_mut(p).buffs.push(n);
                }
            }
        } else {
            self.players[by].epic_secure += 1;
        }
    }

    /// `attacker` hits `victim` for `amount` as the engine would: shields first, his `deal` statistic counts it.
    pub fn hit(&mut self, attacker: usize, victim: usize, amount: usize) {
        let c = self.players[victim].champ;
        damage(&mut self.units[c], amount, false);
        self.players[attacker].deal += amount as u64;
    }

    /// The player's champion dies where he stands (the body keeps its buffs).
    pub fn die(&mut self, player: usize) {
        let u = self.champ_mut(player);
        u.alive = false;
        u.hp = 0;
    }

    /// The player comes back as a new entity at full health: a mod's buffs go with the old one, the native drake buffs
    /// stay (the game keeps them through deaths).
    pub fn respawn(&mut self, player: usize) {
        let old = self.players[player].champ;
        let mut fresh = self.units[old].clone();
        self.units[old].alive = false;
        fresh.buffs.retain(|b| b.name() == rules::NATIVE);
        (fresh.alive, fresh.hp, fresh.shield) = (true, fresh.max, 0);
        self.units.push(fresh);
        self.players[player].champ = self.units.len() - 1;
    }

    /// Hits dealt to `unit`.
    pub fn hits_on(&self, unit: usize) -> Vec<Hit> {
        self.hits.iter().filter(|h| h.1 == unit).copied().collect()
    }
}

fn damage(u: &mut Unit, amount: usize, through_shield: bool) {
    let mut left = amount;
    if !through_shield {
        let s = u.shield.min(left);
        u.shield -= s;
        left -= s;
    }
    u.hp = u.hp.saturating_sub(left);
    if u.hp == 0 {
        u.alive = false;
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
/// The two-call string output.
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
unsafe extern "C" fn hp(s: *const c_void, h: EntityHandleV1, cur: *mut usize, max: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*cur, *max) = (e.hp, e.max);
    true
}
unsafe extern "C" fn shield(s: *const c_void, h: EntityHandleV1) -> usize {
    u(s, h).map_or(0, |e| e.shield)
}
unsafe extern "C" fn stat(s: *const c_void, h: EntityHandleV1, o: *mut StatV1) -> bool {
    let Some(e) = u(s, h) else { return false };
    *o = e.stat;
    true
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
unsafe extern "C" fn stack_buff(s: *mut c_void, h: EntityHandleV1, b: *const BuffV1, max: usize, refresh: u32) -> usize {
    let refuse = w(s).refuse.clone();
    let Some(e) = u(s, h) else { return 0 };
    if refuse.contains(&e.kind) {
        return 0;
    }
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
unsafe extern "C" fn name(s: *const c_void, h: EntityHandleV1, buf: *mut u8, cap: usize, len: *mut usize) -> bool {
    let Some(e) = u(s, h) else { return false };
    out(&e.name.clone(), buf, cap, len)
}
unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    (*x, *y) = e.at;
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
    if i < w(s).players.len() { PlayerHandleV1::from_id(i) } else { PlayerHandleV1::NULL }
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
unsafe extern "C" fn player_alive(s: *const c_void, h: PlayerHandleV1) -> bool {
    let Some(c) = p(s, h).map(|x| x.champ) else { return false };
    w(s).units.get(c).is_some_and(|e| e.alive)
}
unsafe extern "C" fn player_level(_s: *const c_void, _h: PlayerHandleV1) -> usize {
    9
}
unsafe extern "C" fn cooldowns(s: *const c_void, h: PlayerHandleV1, a: *mut usize, b: *mut usize, c: *mut usize,
                               d: *mut usize) -> bool {
    let Some(x) = p(s, h) else { return false };
    (*a, *b, *c, *d) = (x.cds[0], x.cds[1], x.cds[2], x.cds[3]);
    true
}
unsafe extern "C" fn statistics(s: *const c_void, h: PlayerHandleV1, path: *const u8, path_len: usize, buf: *mut u8,
                                cap: usize, len: *mut usize) -> bool {
    if w(s).no_stats {
        return false;
    }
    let Some(x) = p(s, h).cloned() else { return false };
    let v = match text(path, path_len).as_str() {
        "deal" => x.deal.to_string(),
        "serpen_secure" => x.serpen_secure.to_string(),
        "epic_secure" => x.epic_secure.to_string(),
        "" => format!("{{\"kill\":0,\"deal\":{},\"epic_secure\":{},\"serpen_secure\":{},\"obj_steal\":0}}", x.deal,
                      x.epic_secure, x.serpen_secure),
        _ => return false,
    };
    out(&v, buf, cap, len)
}
unsafe extern "C" fn distance_sq(s: *const c_void, a: usize, b: usize) -> u64 {
    let (Some(x), Some(y)) = (w(s).units.get(a), w(s).units.get(b)) else { return u64::MAX };
    let (dx, dy) = (x.at.0.abs_diff(y.at.0), x.at.1.abs_diff(y.at.1));
    dx * dx + dy * dy
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
fn credit(world: &mut World, attacker: usize, amount: usize) {
    if let Some(pl) = world.players.iter_mut().find(|p| p.champ == attacker) {
        pl.deal += amount as u64;
    }
}
unsafe extern "C" fn deal_typed(s: *mut c_void, attacker: usize, target: usize, amount: usize, dtype: u32, atype: u32) -> bool {
    let world = w(s);
    let Some(t) = world.units.get_mut(target) else { return false };
    damage(t, amount, atype == AttackTypeV1::DotIgnoreShield.code());
    world.hits.push((attacker, target, amount, dtype, atype));
    credit(world, attacker, amount);
    true
}
unsafe extern "C" fn deal(s: *mut c_void, attacker: usize, target: usize, ad: usize, ap: usize, atype: u32) {
    let dtype = if ap > 0 { DamageTypeV1::Ap } else { DamageTypeV1::Ad };
    deal_typed(s, attacker, target, ad + ap, dtype.code(), atype);
}
unsafe extern "C" fn heal(s: *mut c_void, _caster: usize, target: usize, amount: usize) {
    let world = w(s);
    if let Some(t) = world.units.get_mut(target) {
        t.hp = (t.hp + amount).min(t.max);
        world.heals.push((target, amount));
    }
}
unsafe extern "C" fn add_shield(s: *mut c_void, h: EntityHandleV1, amount: usize, ticks: usize) -> bool {
    let Some(id) = h.id() else { return false };
    let world = w(s);
    let Some(t) = world.units.get_mut(id) else { return false };
    t.shield += amount;
    world.shields.push((id, amount, ticks));
    true
}
unsafe extern "C" fn kill_count(_s: *const c_void) -> usize {
    0
}
unsafe extern "C" fn set_pos(s: *mut c_void, h: EntityHandleV1, x: u64, y: u64) -> bool {
    let Some(e) = u(s, h) else { return false };
    e.at = (x, y);
    true
}
unsafe extern "C" fn set_invisible(s: *mut c_void, h: EntityHandleV1, ticks: usize) -> bool {
    let now = w(s).tick;
    let Some(e) = u(s, h) else { return false };
    e.unseen_until = now + ticks;
    true
}
unsafe extern "C" fn is_visible(s: *const c_void, team: usize, id: usize) -> bool {
    let now = w(s).tick;
    w(s).units.get(id).is_some_and(|e| e.alive && (e.team == team || (now >= e.unseen_until && !e.stealth)))
}
unsafe extern "C" fn radius(_s: *const c_void, _h: EntityHandleV1) -> usize {
    8_000
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
    vt.entity_hp = Some(hp);
    vt.entity_shield = Some(shield);
    vt.entity_stat = Some(stat);
    vt.entity_buff_count = Some(buff_count);
    vt.entity_buff_at = Some(buff_at);
    vt.add_buff = Some(add_buff);
    vt.entity_remove_buff = Some(remove_buff);
    vt.entity_stack_buff = Some(stack_buff);
    vt.entity_name = Some(name);
    vt.entity_pos = Some(pos);
    vt.tower_count = Some(towers);
    vt.tower_id_at = Some(tower_at);
    vt.player_count = Some(players);
    vt.player_at = Some(player_at);
    vt.player_is_valid = Some(player_valid);
    vt.player_champion = Some(player_champion);
    vt.player_lane = Some(player_lane);
    vt.player_team = Some(player_team);
    vt.player_is_alive = Some(player_alive);
    vt.player_level = Some(player_level);
    vt.player_cooldowns = Some(cooldowns);
    vt.player_statistics_json = Some(statistics);
    vt.distance_sq = Some(distance_sq);
    vt.sim_origin = Some(origin);
    vt.deal_damage = Some(deal);
    vt.deal_damage_typed = Some(deal_typed);
    vt.heal = Some(heal);
    vt.entity_add_shield = Some(add_shield);
    vt.kill_log_count = Some(kill_count);
    vt.entity_set_pos = Some(set_pos);
    vt.entity_set_invisible = Some(set_invisible);
    vt.is_visible = Some(is_visible);
    vt.entity_radius = Some(radius);
    let mut ctx = SimCtxV1 {
        size: size_of::<SimCtxV1>(),
        sim: &vt,
        frame: std::ptr::null(),
        state: world as *mut World as *mut c_void,
    };
    let mut sim = unsafe { StableSim::from_raw(&mut ctx) }.expect("a simulation context");
    f(&mut sim)
}
