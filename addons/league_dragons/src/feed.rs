//! 给画面那一半（公告、HUD）读的：屏幕上那一场（自己的比赛、观战、回放）的事和状态记录，按发生的 tick 排着。
//!
//! 玩法全在模拟里（`lib.rs` 的比赛钩子），每份模拟的状态按 `SIM_TAG` 各记各的；这里只有屏幕上那一场的「发生了什么」，
//! 进程里一份，**模拟从来不读它**（不影响玩法，预演和画面怎么跑都一样）。屏幕放的是跑在前面的模拟的回放（league_eggs
//! notice.rs、league_akshan banner.rs 的做法）：事情按模拟的 tick 记下，客户端扩展按屏幕上的比赛时钟
//! （`game_places::clock::screen_tick`）到了那一 tick 再画。屏幕那一场会跑两遍：同样的一条只记一次。换了一场就扔掉上一场的。
//!
//! 客户端扩展读不到对局里的实体，所以公告和 HUD 用这里的 [`events`] / [`record_at`]；显示钩子（[`super::skin`]：小龙按元素
//! 换模型）也收不到原生 buff，同样按屏幕时钟读这里的出生事件。模拟里的 buff（`league_dragons_el_<元素>`、`league_dragons_st:…`、
//! `league_dragons_ev:…`）留给别的模组读（README「给画面的接口」）。

use std::sync::Mutex;

use super::fx::Fx;
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
    /// 峡谷变成这种元素，地形跟着变（第二条元素亚龙被拿下时；只有游戏自带的 5v5 地图）。
    Rift { element: Element },
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
/// (比赛, 局, 实体编号, 元素)：屏幕那一场每条小龙 / 远古巨龙出生时记下它的实体编号（显示世界的实体用同一个编号，日志
/// `SPAWN sim … serpent #266` 和 `SKIN world … #266`）。换外观按编号找元素，不靠屏幕时钟——倒退、快进回放时时钟读不到
/// （用户 2026-11-10：「倒退看回放的时候小龙的模型又恢复成原样了」）。
static DRAKES: Mutex<Vec<(u64, u64, usize, Element)>> = Mutex::new(Vec::new());
/// (比赛, 局, tick)：屏幕那一场的模拟在哪个 tick 结束（比赛钩子的 `end`）。屏幕时钟走到这里以后本包什么都不画——结算画面上
/// 游戏还当是在比赛里、时钟也还读得到（用户 2026-11-10：「这东西一局对战结束了 还显示啊」）。
static ENDED: Mutex<Vec<(u64, u64, usize)>> = Mutex::new(Vec::new());
/// 屏幕那一场画在战场上的特效（[`super::fx`]）：哪个 tick、在哪、哪一种。
static FXS: Mutex<Vec<Fx>> = Mutex::new(Vec::new());
/// 特效最多留这么多条（很长的一局）：满了丢掉最早的四分之一。
const FX_MOST: usize = 16_384;

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
    if let Ok(mut d) = DRAKES.lock() {
        d.retain(|x| (x.0, x.1) == (m, s));
    }
    if let Ok(mut d) = ENDED.lock() {
        d.retain(|x| (x.0, x.1) == (m, s));
    }
    if let Ok(mut f) = FXS.lock() {
        f.retain(|x| (x.m, x.s) == (m, s));
    }
    true
}

/// 屏幕模拟里放了一次特效（同一场再放一遍时同样的一条不再记）。
pub fn fx(f: Fx) {
    if let Ok(mut l) = FXS.lock() {
        if !l.contains(&f) {
            if l.len() >= FX_MOST {
                l.drain(..FX_MOST / 4);
            }
            l.push(f);
        }
    }
}

/// 这一场在屏幕时钟 `t` 时还在放的特效：开始在 `t` 或之前、不超过 `longest` tick 之前的（每种放多久由画的那边定）。
pub fn fx_live(m: u64, s: u64, t: usize, longest: usize) -> Vec<Fx> {
    FXS.lock()
        .map(|l| l.iter().filter(|f| (f.m, f.s) == (m, s) && f.tick <= t && t - f.tick < longest).cloned().collect())
        .unwrap_or_default()
}

/// 这一场到 `t` 为止的某一类特效（蜂蜜果实什么时候被吃掉：画面按它算果实长好了没有）。
pub fn fx_where(m: u64, s: u64, t: usize, want: impl Fn(&Fx) -> bool) -> Vec<Fx> {
    FXS.lock().map(|l| l.iter().filter(|f| (f.m, f.s) == (m, s) && f.tick <= t && want(f)).cloned().collect()).unwrap_or_default()
}

/// 这一场一共记了几次特效（日志、测试）。
pub fn fx_count(m: u64, s: u64) -> usize {
    FXS.lock().map(|l| l.iter().filter(|f| (f.m, f.s) == (m, s)).count()).unwrap_or(0)
}

/// 屏幕那一场的模拟在 `tick` 结束了（同一场再放一遍时记第一次的）。
pub fn ended(m: u64, s: u64, tick: usize) {
    if let Ok(mut d) = ENDED.lock() {
        if !d.iter().any(|x| (x.0, x.1) == (m, s)) {
            d.push((m, s, tick));
        }
    }
}

/// 这一场的模拟结束在哪个 tick（还没结束：None）。
pub fn ended_at(m: u64, s: u64) -> Option<usize> {
    ENDED.lock().ok().and_then(|d| d.iter().find(|x| (x.0, x.1) == (m, s)).map(|x| x.2))
}

/// 屏幕那一场出生了一条小龙 / 远古巨龙（`element` 是 Elder 时是远古），实体编号 `ent`。
pub fn drake_born(m: u64, s: u64, ent: usize, element: Element) {
    if let Ok(mut d) = DRAKES.lock() {
        if !d.iter().any(|x| (x.0, x.1, x.2) == (m, s, ent)) {
            d.push((m, s, ent, element));
        }
    }
}

/// 这一场实体编号 `ent` 的那条龙是什么元素（不是小龙或还没记下：None）。
pub fn drake_of(m: u64, s: u64, ent: usize) -> Option<Element> {
    DRAKES.lock().ok().and_then(|d| d.iter().find(|x| (x.0, x.1, x.2) == (m, s, ent)).map(|x| x.3))
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
    DRAKES.lock().unwrap().clear();
    ENDED.lock().unwrap().clear();
    FXS.lock().unwrap().clear();
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
        // the drakes by entity id (a replay played again records nothing twice)
        drake_born(5, 1, 266, Element::Infernal);
        drake_born(5, 1, 266, Element::Infernal);
        drake_born(5, 1, 627, Element::Elder);
        assert_eq!(drake_of(5, 1, 266), Some(Element::Infernal));
        assert_eq!(drake_of(5, 1, 627), Some(Element::Elder));
        assert_eq!(drake_of(5, 1, 7), None);
        // the end of the match (played again: the first one kept)
        assert_eq!(ended_at(5, 1), None);
        ended(5, 1, 40878);
        ended(5, 1, 40900);
        assert_eq!(ended_at(5, 1), Some(40878));
        // the effects: once each, alive from their tick for as long as asked
        let blast = Fx { m: 5, s: 1, tick: 1000, kind: super::super::fx::Kind::InfernalBlast, at: (10, 20), to: vec![] };
        fx(blast.clone());
        fx(blast.clone());
        fx(Fx { tick: 1040, ..blast.clone() });
        assert_eq!(fx_count(5, 1), 2);
        assert!(fx_live(5, 1, 999, 50).is_empty());
        assert_eq!(fx_live(5, 1, 1000, 50), vec![blast.clone()]);
        assert_eq!(fx_live(5, 1, 1045, 50).len(), 2);
        assert_eq!(fx_live(5, 1, 1050, 50).iter().map(|f| f.tick).collect::<Vec<_>>(), vec![1040]);
        assert!(fx_live(4, 1, 1000, 50).is_empty());
        // another match on screen: the last one's go
        assert!(view(6, 1));
        assert_eq!(fx_count(5, 1), 0);
        assert!(events(5, 1).is_empty() && record_at(5, 1, 5000).is_none());
        assert_eq!(drake_of(5, 1, 266), None);
        assert_eq!(ended_at(5, 1), None);
        assert_eq!(current(), Some((6, 1)));
        clear();
    }
}
