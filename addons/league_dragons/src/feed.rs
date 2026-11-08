//! 给画面那一半（公告、HUD）读的：屏幕上那一场（自己的比赛、观战、回放）的事和状态记录，按发生的 tick 排着。
//!
//! 玩法全在模拟里（`lib.rs` 的比赛钩子），每份模拟的状态按 `SIM_TAG` 各记各的；这里只有屏幕上那一场的「发生了什么」，
//! 进程里一份，**模拟从来不读它**（不影响玩法，预演和画面怎么跑都一样）。屏幕放的是跑在前面的模拟的回放（league_eggs
//! notice.rs、league_akshan banner.rs 的做法）：事情按模拟的 tick 记下，客户端扩展按屏幕上的比赛时钟
//! （`game_places::clock::screen_tick`）到了那一 tick 再画。屏幕那一场会跑两遍：同样的一条只记一次。换了一场就扔掉上一场的。
//!
//! 客户端扩展读不到对局里的实体，所以公告和 HUD 用这里的 [`events`] / [`record_at`]；画面里读得到实体的（league.dll 的显示
//! 钩子：小龙的皮肤）读模拟里的 buff：活着的小龙身上的 `league_dragons_el_<元素>`、水晶上的 `league_dragons_st:…` 和
//! `league_dragons_ev:…`（README「给画面的接口」）。

use std::sync::Mutex;

use super::rules::{Element, Record};

/// 一件事（屏幕上那一场的）。英雄都是英雄 id（`league_jinx`），画的时候换成游戏里的名字；队伍 0 蓝、1 红。
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum What {
    /// 一条元素亚龙出生。
    DrakeSpawn { element: Element },
    /// 远古巨龙出生。
    ElderSpawn,
    /// 一队拿下一条元素亚龙（`total`：这一队一共几条）。
    Drake { team: usize, element: Element, total: u8 },
    /// 一队拿到龙魂。
    Soul { team: usize, element: Element },
    /// 一队拿下远古巨龙，`holders` 拿到远古龙之力。
    ElderKilled { team: usize, holders: Vec<String> },
    /// 远古龙之力：`killer`（`team` 的）处决了 `victim`。
    Execute { team: usize, killer: String, victim: String },
    /// 一队拿下纳什男爵，`holders` 拿到纳什男爵之手。
    BaronKilled { team: usize, holders: Vec<String> },
    /// 撞上创意工坊的「Elemental Drakes & Baron」：本包什么都没做，请玩家关掉那个 mod。
    Conflict,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Event {
    /// 屏幕那一场的（比赛, 局）。
    pub m: u64,
    pub s: u64,
    /// 发生在模拟的哪个 tick。
    pub tick: usize,
    pub what: What,
}

static EVENTS: Mutex<Vec<Event>> = Mutex::new(Vec::new());
static RECORDS: Mutex<Vec<(u64, u64, Record)>> = Mutex::new(Vec::new());
static VIEW: Mutex<Option<(u64, u64)>> = Mutex::new(None);

/// 屏幕在放这一场（比赛钩子在每个屏幕模拟里每 tick 记）：换了一场就只留这一场的。-> 是不是换了一场。
pub fn view(m: u64, s: u64) -> bool {
    let Ok(mut v) = VIEW.lock() else { return false };
    if *v == Some((m, s)) {
        return false;
    }
    *v = Some((m, s));
    drop(v);
    if let Ok(mut e) = EVENTS.lock() {
        e.retain(|x| (x.m, x.s) == (m, s));
    }
    if let Ok(mut r) = RECORDS.lock() {
        r.retain(|x| (x.0, x.1) == (m, s));
    }
    true
}

/// 屏幕上在放的那一场（还没有：None）。
pub fn current() -> Option<(u64, u64)> {
    VIEW.lock().ok().and_then(|v| *v)
}

/// 屏幕模拟里发生了一件（同一场再放一遍时同样的一条不再记）。
pub fn push(e: Event) {
    if let Ok(mut l) = EVENTS.lock() {
        if !l.contains(&e) {
            l.push(e);
        }
    }
}

/// 屏幕模拟写了一份状态记录。
pub fn record(m: u64, s: u64, r: Record) {
    if let Ok(mut l) = RECORDS.lock() {
        if !l.iter().any(|x| (x.0, x.1) == (m, s) && x.2 == r) {
            l.push((m, s, r));
        }
    }
}

/// 这一场的事，按 tick 排（同一 tick 的按发生的先后）。
pub fn events(m: u64, s: u64) -> Vec<Event> {
    let mut v: Vec<Event> = EVENTS.lock().map(|l| l.iter().filter(|e| (e.m, e.s) == (m, s)).cloned().collect()).unwrap_or_default();
    v.sort_by_key(|e| e.tick);
    v
}

/// 这一场在屏幕时钟 `t` 时的状态：写在 `t` 或之前的最后一份记录（HUD：两队的层数、龙魂、远古龙之力和纳什男爵之手还剩多久 =
/// `until - t`）。
pub fn record_at(m: u64, s: u64, t: usize) -> Option<Record> {
    RECORDS.lock().ok().and_then(|l| {
        l.iter().filter(|x| (x.0, x.1) == (m, s) && x.2.tick <= t).max_by_key(|x| x.2.tick).map(|x| x.2)
    })
}

#[cfg(test)]
pub(crate) fn clear() {
    EVENTS.lock().unwrap().clear();
    RECORDS.lock().unwrap().clear();
    *VIEW.lock().unwrap() = None;
}

#[cfg(test)]
mod tests {
    use super::*;

    /// One test touches the globals (the screen's match), the hook's own test reads them through lib.rs's (one lock).
    #[test]
    fn the_screens_events_are_kept_once_and_by_match() {
        let _g = super::super::tests::GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
        clear();
        assert!(view(5, 1));
        assert!(!view(5, 1));
        let e = Event { m: 5, s: 1, tick: 900, what: What::ElderSpawn };
        push(e.clone());
        push(e.clone());
        push(Event { tick: 300, what: What::Conflict, ..e.clone() });
        assert_eq!(events(5, 1).iter().map(|x| x.tick).collect::<Vec<_>>(), vec![300, 900]);
        let r1 = Record { tick: 100, cur: 3, ..Record::default() };
        let r2 = Record { tick: 700, cur: 7, ..Record::default() };
        for r in [r1, r2, r1] {
            record(5, 1, r);
        }
        assert_eq!(record_at(5, 1, 99), None);
        assert_eq!(record_at(5, 1, 100), Some(r1));
        assert_eq!(record_at(5, 1, 699), Some(r1));
        assert_eq!(record_at(5, 1, 5000), Some(r2));
        // another match on screen: the last one's go
        assert!(view(6, 1));
        assert!(events(5, 1).is_empty() && record_at(5, 1, 5000).is_none());
        assert_eq!(current(), Some((6, 1)));
        clear();
    }
}
