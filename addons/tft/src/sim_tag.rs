//! 每份模拟一个编号（`SIM_TAG`，tft_loris、tft_syfen 和 league_galio 的做法，2026-11-03 抽成这个包共用的小工具，
//! tft 0.46.0；洛里斯、赛芬还是各用自己的一份）：被动在单位第一次出生时抽一个编号，每次出生挂在单位身上（buff
//! `<前缀><编号>`，没有数值、没有画面；死了再出生是新的实体，所以每次出生都挂），效果手边没有被动，就从施法者身上读回来
//! （死了的施法者身上的 buff 留到他重生）。全局表按（编号, 实体）记（[`Key`]）：服务器同一局并排跑两份预模拟，种子、来历
//! （种类、比赛、局）和实体编号全都一样，只按实体编号、或按（种子、来历、实体）记的表两份共用，一份会拿走、改掉、清掉另一份
//! 的东西；同时跑的几场比赛实体编号也会撞上。

use std::sync::atomic::{AtomicU64, Ordering};

use mod_api_stable::*;

/// A row of global state: (the simulation's number, the entity it is about). 0 is no number: a unit without its tag.
pub type Key = (u64, usize);

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

#[cfg(test)]
mod tests {
    use std::collections::HashMap;
    use std::ffi::c_void;
    use std::mem::{size_of, zeroed};

    use super::*;

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
