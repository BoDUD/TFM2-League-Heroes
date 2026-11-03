//! 每份模拟一个编号（`SIM_TAG`，tft_loris、tft_syfen 和 league_galio 的做法，2026-11-03 抽成这个包共用的小工具，
//! tft 0.46.0；洛里斯、赛芬还是各用自己的一份）：被动在单位第一次出生时抽一个编号，每次出生挂在单位身上（buff
//! `<前缀><编号>`，没有数值、没有画面；死了再出生是新的实体，所以每次出生都挂），效果手边没有被动，就从施法者身上读回来
//! （死了的施法者身上的 buff 留到他重生）。全局表按（编号, 实体）记（[`Key`]）：服务器同一局并排跑两份预模拟，种子、来历
//! （种类、比赛、局）和实体编号全都一样，只按实体编号、或按（种子、来历、实体）记的表两份共用，一份会拿走、改掉、清掉另一份
//! 的东西；同时跑的几场比赛实体编号也会撞上。

use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Mutex;

use mod_api_stable::*;

/// A row of global state: (the simulation's number, the entity it is about). 0 is no number: a unit without its tag.
pub type Key = (u64, usize);

/// 等着到点的东西，按 [`Key`] 一行一行记：(到点的 tick, 那个东西)。2026-11-04（11-03 夜里的日志，tft 0.50.0）：排队效果的
/// 输入只带回种类和目标（指向单位）或位置（x、y），塞进 dir_x / dir_y / target_id 的数排一拍就丢了（希尔科的畸变体一口没咬，
/// league_graves 的撞墙标记没到，tft_loris 10-27 遇到过）——希尔科的畸变体和毒雾、诺拉的琐物和毛线球改记在这里，排的效果只带
/// 位置，到点时把这一行里到点的都拿出来处理。
pub type Rows<T> = Mutex<HashMap<Key, Vec<(usize, T)>>>;

/// More rows than this in a table are finished simulations' (one that ended with things still waiting): all cleared.
pub const MOST_ROWS: usize = 4096;

/// `x` waits in `row` for tick `due`.
pub fn wait<T>(rows: &Rows<T>, row: Key, due: usize, x: T) {
    rows.lock().unwrap_or_else(|e| e.into_inner()).entry(row).or_default().push((due, x));
}

/// What waits in `row` for a tick up to `now`, taken off (the rest stays; an emptied row goes).
pub fn due<T: Copy>(rows: &Rows<T>, row: Key, now: usize) -> Vec<T> {
    let mut rows = rows.lock().unwrap_or_else(|e| e.into_inner());
    let Some(list) = rows.get_mut(&row) else { return Vec::new() };
    let ready = list.iter().filter(|w| w.0 <= now).map(|w| w.1).collect();
    list.retain(|w| w.0 > now);
    if list.is_empty() {
        rows.remove(&row);
    }
    ready
}

/// The rows of the unit numbered `no` cleared (its new life: what the last one left stopped with it), and all of them past
/// [`MOST_ROWS`].
pub fn forget<T>(rows: &Rows<T>, no: u64) {
    let mut rows = rows.lock().unwrap_or_else(|e| e.into_inner());
    rows.retain(|k, _| k.0 != no);
    if rows.len() > MOST_ROWS {
        rows.clear();
    }
}

/// The numbers drawn so far, one counter for every unit of the pack (0 is never drawn).
static NEXT: AtomicU64 = AtomicU64::new(1);

/// One unit's tag: the buff `<prefix><number>` its passive hangs on it (`tft_<unit>_sim:`).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct SimTag(pub &'static str);

impl SimTag {
    /// The buff that carries `no`.
    pub fn name(&self, no: u64) -> String {
        format!("{}{no}", self.0)
    }

    /// The number in a buff name of this tag (None: another buff).
    pub fn parse(&self, buff: &str) -> Option<u64> {
        buff.strip_prefix(self.0).and_then(|v| v.parse().ok())
    }

    /// The number hung on `id` (0: none - not hung, or no such unit).
    pub fn of(&self, sim: &StableSim<'_>, id: usize) -> u64 {
        sim.get_entity(id).map_or(0, |e| {
            (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find_map(|b| self.parse(b.name())).unwrap_or(0)
        })
    }

    /// A passive's spawn: its number (`no`, drawn at the first spawn and kept for the whole simulation) hung on `me`
    /// afresh - a respawn is a new entity without it.
    pub fn spawn(&self, sim: &mut StableSim<'_>, me: usize, no: &mut u64) {
        if *no == 0 {
            *no = NEXT.fetch_add(1, Ordering::Relaxed);
        }
        let tag = self.name(*no);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
    }

    /// The row of `id` in the simulation of `me` (by the number hung on `me`): for an effect, which has no passive at
    /// hand. A passive uses its own number.
    pub fn key(&self, sim: &StableSim<'_>, me: usize, id: usize) -> Key {
        (self.of(sim, me), id)
    }
}

/// A small simulation of one's own for the pack's tests (2026-11-04): units with a team, a place, a body, life and buffs;
/// a queue that hands an input back the game's way - its kind and its target or its position, nothing more; the hits and
/// the projectiles spawned.
#[cfg(test)]
pub mod mock {
    use std::ffi::c_void;
    use std::mem::{size_of, zeroed};

    use mod_api_stable::*;

    #[derive(Clone)]
    pub struct Unit {
        pub team: usize,
        pub at: (u64, u64),
        pub radius: usize,
        pub alive: bool,
        pub champion: bool,
        pub buffs: Vec<BuffV1>,
    }

    impl Unit {
        /// A champion of `team` at `at`, alive, body 4000.
        pub fn new(team: usize, at: (u64, u64)) -> Unit {
            Unit { team, at, radius: 4_000, alive: true, champion: true, buffs: Vec::new() }
        }
    }

    #[derive(Default)]
    pub struct World {
        pub tick: usize,
        pub units: Vec<Unit>,
        /// (the tick it fires, the effect, the caster, the input as the queue hands it back).
        pub queue: Vec<(usize, String, usize, InputTargetV1)>,
        /// (target, amount) of every hit.
        pub hits: Vec<(usize, usize)>,
        /// (the projectile's effect, where it flies) of every projectile spawned.
        pub shots: Vec<(String, (u64, u64))>,
    }

    unsafe fn w<'a>(s: *const c_void) -> &'a mut World {
        &mut *(s as *mut World)
    }
    unsafe fn u<'a>(s: *const c_void, h: EntityHandleV1) -> Option<&'a mut Unit> {
        w(s).units.get_mut(h.id()?)
    }
    unsafe fn text(p: *const u8, n: usize) -> String {
        std::str::from_utf8(std::slice::from_raw_parts(p, n)).unwrap_or("").to_string()
    }
    unsafe extern "C" fn tick(s: *const c_void) -> usize {
        w(s).tick
    }
    unsafe extern "C" fn count(s: *const c_void) -> usize {
        w(s).units.len()
    }
    unsafe extern "C" fn at(s: *const c_void, i: usize) -> EntityHandleV1 {
        if i < w(s).units.len() { EntityHandleV1::from_id(i) } else { EntityHandleV1::NULL }
    }
    unsafe extern "C" fn champion_count(s: *const c_void) -> usize {
        w(s).units.iter().filter(|e| e.champion).count()
    }
    unsafe extern "C" fn champion_id_at(s: *const c_void, i: usize) -> usize {
        w(s).units.iter().enumerate().filter(|e| e.1.champion).nth(i).map_or(usize::MAX, |e| e.0)
    }
    unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
        u(s, h).is_some()
    }
    unsafe extern "C" fn alive(s: *const c_void, h: EntityHandleV1) -> bool {
        u(s, h).is_some_and(|e| e.alive)
    }
    unsafe extern "C" fn champion(s: *const c_void, h: EntityHandleV1) -> bool {
        u(s, h).is_some_and(|e| e.champion)
    }
    unsafe extern "C" fn team(s: *const c_void, h: EntityHandleV1) -> usize {
        u(s, h).map_or(0, |e| e.team)
    }
    unsafe extern "C" fn radius(s: *const c_void, h: EntityHandleV1) -> usize {
        u(s, h).map_or(0, |e| e.radius)
    }
    unsafe extern "C" fn pos(s: *const c_void, h: EntityHandleV1, x: *mut u64, y: *mut u64) -> bool {
        let Some(e) = u(s, h) else { return false };
        (*x, *y) = e.at;
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
    unsafe extern "C" fn add_buff(s: *mut c_void, id: usize, b: *const BuffV1) {
        if let Some(e) = w(s).units.get_mut(id) {
            e.buffs.push(*b);
        }
    }
    unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, name: *const u8, len: usize) -> usize {
        let name = text(name, len);
        let Some(e) = u(s, h) else { return 0 };
        let before = e.buffs.len();
        e.buffs.retain(|b| b.name() != name);
        before - e.buffs.len()
    }
    unsafe extern "C" fn queue_effect(s: *mut c_void, name: *const u8, len: usize, _: u32, caster: usize,
                                      input: *const InputTargetV1, delay: usize) -> bool {
        let i = *input;
        let kept = match InputTargetKindV1::from_code(i.kind) {
            Some(InputTargetKindV1::Target) => InputTargetV1::target(i.target_id),
            Some(InputTargetKindV1::Pos) => InputTargetV1::pos(i.x, i.y),
            _ => InputTargetV1::NONE,
        };
        let world = w(s);
        world.queue.push((world.tick + delay, text(name, len), caster, kept));
        true
    }
    unsafe extern "C" fn damage(s: *mut c_void, _: usize, target: usize, amount: usize, _: u32, _: u32) -> bool {
        w(s).hits.push((target, amount));
        true
    }
    unsafe extern "C" fn projectile(s: *mut c_void, _: *const u8, _: usize, fx: *const u8, fx_len: usize,
                                    spec: *const ProjectileSpawnV1) -> bool {
        w(s).shots.push((text(fx, fx_len), ((*spec).target_x, (*spec).target_y)));
        true
    }

    /// `f` run on a simulation of `world`.
    pub fn with_sim<R>(world: &mut World, f: impl FnOnce(&mut StableSim<'_>) -> R) -> R {
        let mut vt: SimVtableV1 = unsafe { zeroed() };
        vt.size = size_of::<SimVtableV1>();
        vt.tick = Some(tick);
        vt.entity_count = Some(count);
        vt.entity_at = Some(at);
        vt.champion_count = Some(champion_count);
        vt.champion_id_at = Some(champion_id_at);
        vt.entity_is_valid = Some(valid);
        vt.entity_is_alive = Some(alive);
        vt.entity_is_targetable = Some(alive);
        vt.entity_is_champion = Some(champion);
        vt.entity_team = Some(team);
        vt.entity_radius = Some(radius);
        vt.entity_pos = Some(pos);
        vt.entity_buff_count = Some(buff_count);
        vt.entity_buff_at = Some(buff_at);
        vt.add_buff = Some(add_buff);
        vt.entity_remove_buff = Some(remove_buff);
        vt.queue_effect = Some(queue_effect);
        vt.deal_damage_typed = Some(damage);
        vt.spawn_projectile = Some(projectile);
        let mut ctx = SimCtxV1 {
            size: size_of::<SimCtxV1>(),
            sim: &vt,
            frame: std::ptr::null(),
            state: world as *mut World as *mut c_void,
        };
        let mut sim = unsafe { StableSim::from_raw(&mut ctx) }.expect("a simulation context");
        f(&mut sim)
    }

    /// One tick: the queued effects due now fire (`fire` runs one: the simulation, its name, the caster, the input), then
    /// the clock moves on.
    pub fn step(world: &mut World, fire: impl Fn(&mut StableSim<'_>, &str, usize, InputTargetV1)) {
        while let Some(i) = world.queue.iter().position(|q| q.0 <= world.tick) {
            let (_, name, caster, input) = world.queue.remove(i);
            with_sim(world, |sim| fire(sim, &name, caster, input));
        }
        world.tick += 1;
    }
}

#[cfg(test)]
mod tests {
    use std::collections::HashMap;
    use std::ffi::c_void;
    use std::mem::{size_of, zeroed};

    use super::*;

    #[test]
    fn things_wait_in_their_own_row() {
        let rows: Rows<char> = Mutex::new(HashMap::new());
        // twin presims: the same unit #20, two numbers
        let (a, b) = ((7, 20), (8, 20));
        wait(&rows, a, 18, 'x');
        wait(&rows, a, 63, 'y');
        wait(&rows, b, 18, 'z');
        assert!(due(&rows, a, 17).is_empty());
        assert_eq!(due(&rows, a, 18), vec!['x']);
        assert!(due(&rows, a, 18).is_empty(), "taken off");
        assert_eq!(due(&rows, b, 100), vec!['z']);
        assert!(!rows.lock().unwrap().contains_key(&b), "an emptied row goes");
        // a's next life: what the last one left goes, b's rows stay
        wait(&rows, b, 200, 'w');
        forget(&rows, 7);
        assert!(due(&rows, a, 1_000).is_empty());
        assert_eq!(due(&rows, b, 1_000), vec!['w']);
    }

    /// A simulation of one's own: each unit's buffs, by its id.
    type World = HashMap<usize, Vec<BuffV1>>;

    unsafe fn world<'a>(s: *const c_void) -> &'a mut World {
        &mut *(s as *mut World)
    }
    unsafe extern "C" fn valid(s: *const c_void, h: EntityHandleV1) -> bool {
        h.id().is_some_and(|id| world(s).contains_key(&id))
    }
    unsafe extern "C" fn buff_count(s: *const c_void, h: EntityHandleV1) -> usize {
        h.id().and_then(|id| world(s).get(&id)).map_or(0, Vec::len)
    }
    unsafe extern "C" fn buff_at(s: *const c_void, h: EntityHandleV1, i: usize, out: *mut BuffV1) -> bool {
        let Some(b) = h.id().and_then(|id| world(s).get(&id)).and_then(|v| v.get(i)) else { return false };
        *out = *b;
        true
    }
    unsafe extern "C" fn add_buff(s: *mut c_void, id: usize, b: *const BuffV1) {
        if let Some(v) = world(s).get_mut(&id) {
            v.push(*b);
        }
    }
    unsafe extern "C" fn remove_buff(s: *mut c_void, h: EntityHandleV1, name: *const u8, len: usize) -> usize {
        let name = std::str::from_utf8(std::slice::from_raw_parts(name, len)).unwrap_or("");
        let Some(v) = h.id().and_then(|id| world(s).get_mut(&id)) else { return 0 };
        let before = v.len();
        v.retain(|b| b.name() != name);
        before - v.len()
    }

    /// `f` run on a simulation of `w` (the slots the tag uses; the others are absent).
    fn with_sim<R>(w: &mut World, f: impl FnOnce(&mut StableSim<'_>) -> R) -> R {
        let mut vt: SimVtableV1 = unsafe { zeroed() };
        vt.size = size_of::<SimVtableV1>();
        vt.entity_is_valid = Some(valid);
        vt.entity_buff_count = Some(buff_count);
        vt.entity_buff_at = Some(buff_at);
        vt.add_buff = Some(add_buff);
        vt.entity_remove_buff = Some(remove_buff);
        let mut ctx = SimCtxV1 {
            size: size_of::<SimCtxV1>(),
            sim: &vt,
            frame: std::ptr::null(),
            state: w as *mut World as *mut c_void,
        };
        let mut sim = unsafe { StableSim::from_raw(&mut ctx) }.expect("a simulation context");
        f(&mut sim)
    }

    const T: SimTag = SimTag("tft_test_sim:");

    #[test]
    fn twin_presims_get_their_own_rows() {
        // the server's two presims of one set: the unit is #3 in both
        let mut a = World::from([(3, vec![BuffV1::named("tft_test_p")])]);
        let mut b = a.clone();
        let (mut na, mut nb) = (0, 0);
        let ka = with_sim(&mut a, |sim| {
            T.spawn(sim, 3, &mut na);
            T.key(sim, 3, 3)
        });
        let kb = with_sim(&mut b, |sim| {
            T.spawn(sim, 3, &mut nb);
            T.key(sim, 3, 3)
        });
        assert!(na > 0 && nb > 0 && na != nb, "{na} {nb}");
        assert_eq!((ka, kb), ((na, 3), (nb, 3)));
        // a row about another unit (a patient, a burning target) goes by the caster's number too
        assert_eq!(with_sim(&mut a, |sim| T.key(sim, 3, 9)), (na, 9));
        // the next spawn hangs the same number, once
        let again = na;
        with_sim(&mut a, |sim| T.spawn(sim, 3, &mut na));
        assert_eq!(na, again);
        assert_eq!(a[&3].iter().filter(|x| T.parse(x.name()).is_some()).count(), 1);
        assert_eq!(with_sim(&mut a, |sim| T.of(sim, 3)), na);
    }

    #[test]
    fn no_tag_no_number() {
        let mut w = World::from([(1, vec![BuffV1::named("tft_test_p")]), (2, vec![BuffV1::named("tft_other_sim:5")])]);
        with_sim(&mut w, |sim| {
            assert_eq!(T.of(sim, 1), 0);
            assert_eq!(T.of(sim, 2), 0);   // another unit's tag is not ours
            assert_eq!(T.of(sim, 7), 0);   // no such unit
            assert_eq!(T.key(sim, 7, 7), (0, 7));
        });
    }

    #[test]
    fn names() {
        assert_eq!(T.name(12), "tft_test_sim:12");
        assert_eq!(T.parse("tft_test_sim:12"), Some(12));
        assert_eq!(T.parse("tft_test_simx"), None);
        assert_eq!(T.parse("tft_test_sim:"), None);
        assert_eq!(T.parse(&T.name(u64::MAX)), Some(u64::MAX));
    }
}
