//! 一帧里的单位名单（2026-11-27 合集自己加的，官方 SDK 里没有；重新拷官方 SDK 时这个文件、lib.rs 里的 `mod entity_list`
//! 和 sim.rs 里 entity_count / entity_at 调它的两处要留着）。
//!
//! 为什么：游戏的 entity_at(i) 每次都新建一个迭代器、往后数 i 步才给出第 i 个单位（0.7.3 EXE 的 0x3513f70，11-27 拆过），
//! entity_count 也是从头数一遍。附加包里到处是 `for i in 0..sim.entity_count() { sim.entity_at(i) }`，一圈就是 n²/2 步。
//! 峡谷地图上单位多（塔、兵、野怪），11-27 那次过日里合集四成的时间耗在这上面。
//!
//! 怎么做：每条线程记最多 [`SLOTS`] 份名单，一份对一个「state 指针 + 这场比赛的随机种子」。英雄 AI 的回调拿到的 state 和
//! 比赛钩子的不是同一个（AI 那边是游戏给的另一份只读视图），一帧里两种回调交替来；只记一份的话每次切换都当成换了比赛，
//! 名单清空重数（11-27 第一次装上后 PERF：完整数 1460 万次、修补 72 万次）。种子防的是两场比赛在同一条线程上碰巧用到同一个
//! state 地址。同一份名单、同一帧、单位数和上次问的一样，entity_at(i) 直接查表。
//! - 名单按编号排序：第 i 个是谁只看这一帧有哪些单位，和哪条线程、之前查过什么都无关（模拟的结果要每次一样）。
//! - 换了帧或者单位数变了就重做名单：拿上一份名单留下还有效的，再从最大编号往后找新单位（新单位的编号往上加）；
//!   凑够 entity_count 个就用——个个有效、互不相同、个数相等，就是这一帧全部的单位。凑不够就照游戏的数法完整数一遍。
//! - 每条线程每做 [`CHECK_EVERY`] 次名单（含第一次）照游戏的数法核一遍，对不上就这条线程不再修补、只完整数，记一次数。
//! - 只记句柄：单位的数据（位置、血量、buff）每次还是现取。同一帧里死了一个、又生成一个（个数没变）的话，
//!   新的那个这一帧剩下的时间里列不出来，下一帧就有了；死了的那个句柄失效，`StableSim::entity` 照旧给 None。

use std::cell::{Cell, RefCell};
use std::sync::atomic::{AtomicU64, Ordering};

use crate::EntityHandleV1;

/// 往最大编号后面最多连着找几个没有的编号（两次重做之间生成又移除了的单位会空出编号）。
pub const PROBE: usize = 256;
/// 每做多少次名单照游戏的数法核一遍。
pub const CHECK_EVERY: u32 = 64;
/// 每条线程最多记几份名单（比赛钩子一份、英雄 AI 的视图一份，再留些给同一条线程上前后脚的别的比赛）。
pub const SLOTS: usize = 8;

#[derive(Default)]
struct Listed {
    state: usize,
    seed: u64,
    tick: usize,
    count: usize,
    /// handles 是这一帧、这个单位数的完整名单
    ready: bool,
    handles: Vec<EntityHandleV1>,
    builds: u32,
    /// 最后一次用到它时 Lists::clock 的值（名单满了，换掉最久没用的）
    used: u64,
}

#[derive(Default)]
struct Lists {
    slots: Vec<Listed>,
    clock: u64,
}

impl Lists {
    /// 这个 state + 种子的名单；没有就新开一份（满了换掉最久没用的那份）。
    fn slot(&mut self, state: usize, seed: u64) -> &mut Listed {
        self.clock += 1;
        let i = match self.slots.iter().position(|l| l.state == state && l.seed == seed) {
            Some(i) => i,
            None => {
                NEW_LISTS.fetch_add(1, Ordering::Relaxed);
                let i = if self.slots.len() < SLOTS {
                    self.slots.push(Listed::default());
                    self.slots.len() - 1
                } else {
                    (0..self.slots.len()).min_by_key(|&i| self.slots[i].used).unwrap_or(0)
                };
                self.slots[i] = Listed { state, seed, count: usize::MAX, ..Listed::default() };
                i
            }
        };
        let l = &mut self.slots[i];
        l.used = self.clock;
        l
    }
}

thread_local! {
    static LISTED: RefCell<Lists> = RefCell::new(Lists::default());
    /// 这条线程核对时对不上过：之后只完整数
    static NO_REPAIR: Cell<bool> = const { Cell::new(false) };
}

static LOOKUPS: AtomicU64 = AtomicU64::new(0);
static REPAIRED: AtomicU64 = AtomicU64::new(0);
static EXACT: AtomicU64 = AtomicU64::new(0);
static CHECKED: AtomicU64 = AtomicU64::new(0);
static MISMATCHES: AtomicU64 = AtomicU64::new(0);
static NEW_LISTS: AtomicU64 = AtomicU64::new(0);
static FOR_FRAME: AtomicU64 = AtomicU64::new(0);
static FOR_COUNT: AtomicU64 = AtomicU64::new(0);

/// 整个进程里名单的用法（给日志看）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct EntityListStats {
    /// entity_at 查表的次数
    pub lookups: u64,
    /// 接着上一份名单修补成的
    pub repaired: u64,
    /// 照游戏的数法完整数的
    pub exact: u64,
    /// 修补成了以后又完整数一遍核对的
    pub checked: u64,
    /// 核对对不上的（对不上的那条线程从此只完整数）
    pub mismatches: u64,
    /// 新开的名单（新的 state + 种子）
    pub new_lists: u64,
    /// 因为换了帧重做的
    pub for_frame: u64,
    /// 同一帧里单位数变了重做的
    pub for_count: u64,
}

pub fn entity_list_stats() -> EntityListStats {
    EntityListStats {
        lookups: LOOKUPS.load(Ordering::Relaxed),
        repaired: REPAIRED.load(Ordering::Relaxed),
        exact: EXACT.load(Ordering::Relaxed),
        checked: CHECKED.load(Ordering::Relaxed),
        mismatches: MISMATCHES.load(Ordering::Relaxed),
        new_lists: NEW_LISTS.load(Ordering::Relaxed),
        for_frame: FOR_FRAME.load(Ordering::Relaxed),
        for_count: FOR_COUNT.load(Ordering::Relaxed),
    }
}

/// 刚问过游戏 entity_count：记下这一帧的单位数，和名单对不上（换了帧、个数变了）名单就作废（句柄留着修补用）。
pub(crate) fn counted(state: usize, seed: u64, tick: usize, n: usize) {
    LISTED.with(|l| {
        if let Ok(mut lists) = l.try_borrow_mut() {
            renew(lists.slot(state, seed), tick, n);
        }
    });
}

fn renew(l: &mut Listed, tick: usize, n: usize) {
    if l.tick != tick || l.count != n {
        if l.ready {
            if l.tick != tick {
                FOR_FRAME.fetch_add(1, Ordering::Relaxed);
            } else {
                FOR_COUNT.fetch_add(1, Ordering::Relaxed);
            }
        }
        l.tick = tick;
        l.count = n;
        l.ready = false;
    }
}

/// entity_at(index) 该给的句柄。`count` / `at` / `valid` 是游戏的 entity_count / entity_at / entity_is_valid。
pub(crate) fn handle_at(
    state: usize,
    seed: u64,
    tick: usize,
    index: usize,
    count: impl Fn() -> usize,
    at: impl Fn(usize) -> EntityHandleV1,
    valid: impl Fn(EntityHandleV1) -> bool,
) -> EntityHandleV1 {
    LISTED.with(|l| {
        // 游戏这几个函数不会回头调 mod，借不到只可能是哪里重入了：那就照旧问游戏
        let Ok(mut lists) = l.try_borrow_mut() else { return at(index) };
        let l = lists.slot(state, seed);
        if l.tick != tick || l.count == usize::MAX {
            let n = count();
            renew(l, tick, n);
        }
        if !l.ready {
            build(l, &at, &valid);
        }
        LOOKUPS.fetch_add(1, Ordering::Relaxed);
        l.handles.get(index).copied().unwrap_or(EntityHandleV1::NULL)
    })
}

fn build(l: &mut Listed, at: &impl Fn(usize) -> EntityHandleV1, valid: &impl Fn(EntityHandleV1) -> bool) {
    let n = l.count;
    l.builds = l.builds.wrapping_add(1);
    let check = l.builds % CHECK_EVERY == 1;
    let repaired = if NO_REPAIR.with(Cell::get) || l.handles.is_empty() { None } else { repair(&l.handles, n, valid) };
    let list = match repaired {
        Some(r) if !check => {
            REPAIRED.fetch_add(1, Ordering::Relaxed);
            r
        }
        repaired => {
            let exact = exact(n, at);
            EXACT.fetch_add(1, Ordering::Relaxed);
            if let Some(r) = repaired {
                CHECKED.fetch_add(1, Ordering::Relaxed);
                if r != exact {
                    MISMATCHES.fetch_add(1, Ordering::Relaxed);
                    NO_REPAIR.with(|c| c.set(true));
                }
            }
            exact
        }
    };
    l.handles = list;
    l.ready = true;
}

/// 照游戏的数法：第 0 到 n-1 个，按编号排好。
pub fn exact(n: usize, at: impl Fn(usize) -> EntityHandleV1) -> Vec<EntityHandleV1> {
    let mut v: Vec<EntityHandleV1> = (0..n).map(at).filter(|h| !h.is_null()).collect();
    v.sort_unstable_by_key(|h| h.raw());
    v.dedup();
    v
}

/// 上一份名单（按编号排好的）里还有效的，加上最大编号后面新出来的，正好 n 个就是这一帧的名单（还是按编号排好的）。
pub fn repair(old: &[EntityHandleV1], n: usize, valid: impl Fn(EntityHandleV1) -> bool) -> Option<Vec<EntityHandleV1>> {
    let mut v: Vec<EntityHandleV1> = old.iter().copied().filter(|&h| valid(h)).collect();
    if v.len() > n {
        return None;
    }
    let mut next = old.last().map_or(1, |h| h.raw() + 1);
    let mut misses = 0;
    while v.len() < n && misses < PROBE {
        let h = EntityHandleV1::from_raw(next);
        next += 1;
        if valid(h) {
            v.push(h);
            misses = 0;
        } else {
            misses += 1;
        }
    }
    (v.len() == n).then_some(v)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;

    /// 假的游戏：单位编号表（游戏自己的顺序，不一定按编号）；数一遍、取第 i 个各走多少步都记下来。
    #[derive(Default)]
    struct World {
        ids: Vec<usize>,
        steps: usize,
        at_calls: usize,
    }

    impl World {
        fn count(&mut self) -> usize {
            self.steps += self.ids.len() + 1;
            self.ids.len()
        }
        fn at(&mut self, i: usize) -> EntityHandleV1 {
            self.at_calls += 1;
            self.steps += i + 1;
            self.ids.get(i).map_or(EntityHandleV1::NULL, |&id| EntityHandleV1::from_id(id))
        }
        fn valid(&self, h: EntityHandleV1) -> bool {
            h.id().is_some_and(|id| self.ids.contains(&id))
        }
    }

    /// 附加包常见的写法：数一下，再一个个取（种子 0：测试里一个 state 就是一场比赛）。
    fn listed(w: &RefCell<World>, state: usize, tick: usize) -> Vec<usize> {
        listed_in(w, state, 0, tick)
    }

    fn listed_in(w: &RefCell<World>, state: usize, seed: u64, tick: usize) -> Vec<usize> {
        let n = w.borrow_mut().count();
        counted(state, seed, tick, n);
        (0..n)
            .filter_map(|i| {
                handle_at(state, seed, tick, i, || w.borrow_mut().count(), |j| w.borrow_mut().at(j), |h| w.borrow().valid(h))
                    .id()
            })
            .collect()
    }

    fn sorted(ids: &[usize]) -> Vec<usize> {
        let mut v = ids.to_vec();
        v.sort();
        v
    }

    #[test]
    fn a_loop_lists_every_unit_in_id_order() {
        let w = RefCell::new(World { ids: vec![4, 0, 9, 2, 7], ..Default::default() });
        assert_eq!(listed(&w, 1, 10), vec![0, 2, 4, 7, 9]);
    }

    #[test]
    fn later_loops_in_the_frame_ask_the_game_nothing_more() {
        let w = RefCell::new(World { ids: (0..120).rev().collect(), ..Default::default() });
        let first = listed(&w, 2, 5);
        let calls = w.borrow().at_calls;
        assert_eq!(calls, 120, "the first loop counts the game's way once");
        for _ in 0..30 {
            assert_eq!(listed(&w, 2, 5), first);
        }
        assert_eq!(w.borrow().at_calls, calls, "30 more loops, no more entity_at calls");
    }

    #[test]
    fn the_next_frame_is_repaired_without_counting_again() {
        let w = RefCell::new(World { ids: (0..60).collect(), ..Default::default() });
        listed(&w, 3, 1);
        let calls = w.borrow().at_calls;
        // one unit gone, two new (their ids after the largest), one id skipped in between (made and removed)
        w.borrow_mut().ids.retain(|&id| id != 17);
        w.borrow_mut().ids.extend([61, 62]);
        let next = listed(&w, 3, 2);
        assert_eq!(next, sorted(&w.borrow().ids));
        assert_eq!(w.borrow().at_calls, calls, "repaired from the old list, no entity_at calls");
    }

    #[test]
    fn a_reused_id_falls_back_to_counting_the_games_way() {
        let w = RefCell::new(World { ids: (0..40).collect(), ..Default::default() });
        listed(&w, 4, 1);
        // a unit gone and a new one under an OLD id: the repair finds 39 + nothing above -> counts the game's way
        w.borrow_mut().ids.retain(|&id| id != 5);
        w.borrow_mut().ids.push(3_000);
        let next = listed(&w, 4, 2);
        assert_eq!(next, sorted(&w.borrow().ids));
    }

    #[test]
    fn a_count_change_inside_a_frame_renews_the_list() {
        let w = RefCell::new(World { ids: vec![0, 1, 2], ..Default::default() });
        assert_eq!(listed(&w, 5, 7), vec![0, 1, 2]);
        w.borrow_mut().ids.push(3);
        assert_eq!(listed(&w, 5, 7), vec![0, 1, 2, 3], "a unit made in the same frame shows at the next count");
    }

    #[test]
    fn another_sim_on_the_thread_never_borrows_the_old_list() {
        let a = RefCell::new(World { ids: (0..10).collect(), ..Default::default() });
        let b = RefCell::new(World { ids: (100..110).collect(), ..Default::default() });
        assert_eq!(listed(&a, 6, 1), (0..10).collect::<Vec<_>>());
        assert_eq!(listed(&b, 7, 1), (100..110).collect::<Vec<_>>());
        assert_eq!(listed(&a, 6, 2), (0..10).collect::<Vec<_>>());
    }

    #[test]
    fn out_of_range_is_null_like_the_game() {
        let w = RefCell::new(World { ids: vec![1, 2], ..Default::default() });
        listed(&w, 8, 1);
        let h = handle_at(8, 0, 1, 5, || w.borrow_mut().count(), |j| w.borrow_mut().at(j), |h| w.borrow().valid(h));
        assert!(h.is_null());
    }

    #[test]
    fn every_64th_list_is_checked_and_a_mismatch_stops_repairs() {
        let w = RefCell::new(World { ids: (0..20).collect(), ..Default::default() });
        for tick in 1..=CHECK_EVERY as usize + 1 {
            assert_eq!(listed(&w, 9, tick), (0..20).collect::<Vec<_>>());
        }
        // the 65th list was checked against the game's own count (20 more entity_at calls than the first list)
        assert_eq!(w.borrow().at_calls, 40);
        // a lying validity check (the game's view and its by-id lookup disagree): the check catches it
        NO_REPAIR.with(|c| assert!(!c.get()));
        let old: Vec<EntityHandleV1> = (0..20).map(EntityHandleV1::from_id).collect();
        let fake_valid = |h: EntityHandleV1| h.id().is_some_and(|id| id < 21);       // claims id 20 exists
        let mut l = Listed { state: 10, tick: 1, count: 20, handles: old, ..Listed::default() };
        build(&mut l, &|j| w.borrow_mut().at(j), &fake_valid);                         // the 1st build is a check
        assert_eq!(l.handles, (0..20).map(EntityHandleV1::from_id).collect::<Vec<_>>(), "the game's own count wins");
        // the repair with the lying check kept 0..20 (20 valid of the old) = same set: no mismatch; make it differ
        let mut l = Listed { state: 11, tick: 1, count: 20, handles: (1..21).map(EntityHandleV1::from_id).collect(), ..Listed::default() };
        build(&mut l, &|j| w.borrow_mut().at(j), &fake_valid);
        assert_eq!(l.handles, (0..20).map(EntityHandleV1::from_id).collect::<Vec<_>>());
        NO_REPAIR.with(|c| assert!(c.get(), "the mismatch turned repairs off on this thread"));
    }

    #[test]
    fn the_match_hooks_and_the_ai_views_keep_their_own_lists() {
        // one game, two state pointers (the match hook's and the AI view's) taking turns inside every frame
        let w = RefCell::new(World { ids: (0..80).collect(), ..Default::default() });
        for tick in 1..=20 {
            for _ in 0..5 {
                assert_eq!(listed_in(&w, 20, 7, tick), (0..80).collect::<Vec<_>>());
                assert_eq!(listed_in(&w, 21, 7, tick), (0..80).collect::<Vec<_>>());
            }
        }
        // each counted the game's way once (their first frame), repaired after that
        assert_eq!(w.borrow().at_calls, 2 * 80);
    }

    #[test]
    fn two_games_on_one_state_address_never_share_a_list() {
        // the same address in two matches one after the other (the same frame number in both)
        let a = RefCell::new(World { ids: (0..30).collect(), ..Default::default() });
        let b = RefCell::new(World { ids: (5..35).collect(), ..Default::default() });
        assert_eq!(listed_in(&a, 30, 1, 9), (0..30).collect::<Vec<_>>());
        assert_eq!(listed_in(&b, 30, 2, 9), (5..35).collect::<Vec<_>>());
        assert_eq!(listed_in(&a, 30, 1, 9), (0..30).collect::<Vec<_>>());
    }

    #[test]
    fn more_contexts_than_slots_stay_right() {
        let w = RefCell::new(World { ids: (0..12).collect(), ..Default::default() });
        for tick in 1..=4 {
            for state in 40..40 + 2 * SLOTS {
                assert_eq!(listed_in(&w, state, 3, tick), (0..12).collect::<Vec<_>>());
            }
        }
    }

    #[test]
    fn the_work_drops_from_square_to_line() {
        // 100 units, 30 loops a frame, 10 frames: the game's own way is 30 * 10 * (1 + 2 + ... + 100) steps
        let w = RefCell::new(World { ids: (0..100).collect(), ..Default::default() });
        for tick in 1..=10 {
            for _ in 0..30 {
                listed(&w, 12, tick);
            }
        }
        let steps = w.borrow().steps;
        let old_way = 10 * 30 * (100 * 101 / 2 + 101);
        assert!(steps * 10 < old_way, "{steps} steps vs {old_way}");
    }
}
