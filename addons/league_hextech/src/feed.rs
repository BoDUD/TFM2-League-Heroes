//! 给画面读的：屏幕上那一场（自己的比赛、观战、回放）里每次选择，按发生的 tick 排着（大小龙 feed.rs 的做法）。
//!
//! 玩法全在模拟里，每份模拟的状态各记各的；这里只有屏幕上那一场的「发生了什么」，进程里一份，**模拟从来不读它**。屏幕放的是
//! 跑在前面的模拟的回放：事情按模拟的 tick 记下，客户端扩展按屏幕上的比赛时钟到了那一 tick 再画。屏幕那一场会跑两遍：同样的
//! 一条只记一次。换了一场就扔掉上一场的。
//!
//! 0.3.0 起也记触发类海克斯的战场特效（[`Fx`]：哪个 tick、哪一种、在哪），[`super::fx`] 按屏幕时钟画。

use std::collections::HashSet;
use std::sync::{LazyLock, Mutex};

use super::augments::Tier;
use super::procs::Show;

/// 一次选择（英雄是英雄 id，`league_jinx`；队伍 0 蓝、1 红；`lane` 是分路的编号：0 上 1 野 2 中 3 下 4 辅）。
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Pick {
    pub team: usize,
    pub lane: u8,
    pub hero: String,
    /// 第几次（0 = 开局）
    pub screen: u8,
    /// 选的时候几级
    pub level: u8,
    pub tier: Tier,
    /// 最后的三张、最先发的三张（刷新过的那几张不一样）、拿了哪张（都是海克斯的编号）
    pub cards: [u16; 3],
    pub first: [u16; 3],
    pub chosen: u16,
    /// 谁选的：0 AI（比赛里那一刻）、1 BP 面板上 AI 推荐的（玩家没动）、2 玩家自己点的；0.5.0：3 质变 / 潘朵拉随机给的，4 被潘朵拉
    /// 换掉了（`chosen` 是没了的那个）
    pub by: u8,
    /// 技能海克斯作用在哪个技能上（1 技能、2 技能 2、3 大招；别的 0）
    pub slot: u8,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Event {
    pub m: u64,
    pub s: u64,
    pub tick: usize,
    pub pick: Pick,
}

/// 屏幕那一场的一次战场特效（[`super::procs::Out`] 加上是哪一场）。
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct Fx {
    pub m: u64,
    pub s: u64,
    pub tick: usize,
    pub show: Show,
    pub at: (u64, u64),
    pub to: Vec<(u64, u64)>,
    pub dur: u16,
}

static EVENTS: Mutex<Vec<Event>> = Mutex::new(Vec::new());
static FXS: Mutex<Vec<Fx>> = Mutex::new(Vec::new());
/// 记过的特效（第二遍放的同一条不再记；按内容认，比在整张表里找快）。
static FX_SEEN: LazyLock<Mutex<HashSet<Fx>>> = LazyLock::new(|| Mutex::new(HashSet::new()));
/// 一场最多记这么多次特效（再多先丢最早的四分之一：早就放完了）。
const FX_MOST: usize = 16_384;
static VIEW: Mutex<Option<(u64, u64)>> = Mutex::new(None);
static ENDED: Mutex<Vec<(u64, u64, usize)>> = Mutex::new(Vec::new());
/// 屏幕那一场 4 次的档位。
static TIERS: Mutex<Vec<(u64, u64, [Tier; 4])>> = Mutex::new(Vec::new());

/// 屏幕在放这一场（比赛钩子在每个屏幕模拟里记）：换了一场就只留这一场的。-> 是不是换了一场
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
    if let Ok(mut d) = ENDED.lock() {
        d.retain(|x| (x.0, x.1) == (m, s));
    }
    if let Ok(mut t) = TIERS.lock() {
        t.retain(|x| (x.0, x.1) == (m, s));
    }
    if let Ok(mut f) = FXS.lock() {
        f.retain(|x| (x.m, x.s) == (m, s));
    }
    if let Ok(mut seen) = FX_SEEN.lock() {
        seen.retain(|x| (x.m, x.s) == (m, s));
    }
    true
}

/// 屏幕模拟里放了一次特效（同一场再放一遍时同样的一条不再记）。
pub fn fx(f: Fx) {
    let Ok(mut seen) = FX_SEEN.lock() else { return };
    if seen.contains(&f) {
        return;
    }
    let Ok(mut l) = FXS.lock() else { return };
    if l.len() >= FX_MOST {
        for old in l.drain(..FX_MOST / 4) {
            seen.remove(&old);
        }
    }
    seen.insert(f.clone());
    l.push(f);
}

/// 这一场在屏幕时钟 `t` 时还在放的特效：开始在 `t` 或之前、不超过 `longest` tick 之前的（每种放多久由画的那边定）。
pub fn fx_live(m: u64, s: u64, t: usize, longest: usize) -> Vec<Fx> {
    FXS.lock()
        .map(|l| l.iter().filter(|f| (f.m, f.s) == (m, s) && f.tick <= t && t - f.tick < longest).cloned().collect())
        .unwrap_or_default()
}

/// 这一场一共记了几次特效（日志、测试）。
pub fn fx_count(m: u64, s: u64) -> usize {
    FXS.lock().map(|l| l.iter().filter(|f| (f.m, f.s) == (m, s)).count()).unwrap_or(0)
}

pub fn current() -> Option<(u64, u64)> {
    VIEW.lock().ok().and_then(|v| *v)
}

/// 屏幕模拟里选了一次（同一场再放一遍时同样的一条不再记）。
pub fn push(e: Event) {
    if let Ok(mut l) = EVENTS.lock() {
        if !l.contains(&e) {
            l.push(e);
        }
    }
}

/// 这一场的选择，按 tick 排（同一 tick 的按发生的先后）。
pub fn events(m: u64, s: u64) -> Vec<Event> {
    let mut v: Vec<Event> = EVENTS.lock().map(|l| l.iter().filter(|e| (e.m, e.s) == (m, s)).cloned().collect()).unwrap_or_default();
    v.sort_by_key(|e| e.tick);
    v
}

pub fn tiers(m: u64, s: u64, t: [Tier; 4]) {
    if let Ok(mut l) = TIERS.lock() {
        if !l.iter().any(|x| (x.0, x.1) == (m, s)) {
            l.push((m, s, t));
        }
    }
}

pub fn tiers_of(m: u64, s: u64) -> Option<[Tier; 4]> {
    TIERS.lock().ok().and_then(|l| l.iter().find(|x| (x.0, x.1) == (m, s)).map(|x| x.2))
}

/// 屏幕那一场的模拟在 `tick` 结束了（再放一遍时记第一次的）。
pub fn ended(m: u64, s: u64, tick: usize) {
    if let Ok(mut d) = ENDED.lock() {
        if !d.iter().any(|x| (x.0, x.1) == (m, s)) {
            d.push((m, s, tick));
        }
    }
}

pub fn ended_at(m: u64, s: u64) -> Option<usize> {
    ENDED.lock().ok().and_then(|d| d.iter().find(|x| (x.0, x.1) == (m, s)).map(|x| x.2))
}

#[cfg(test)]
pub(crate) fn clear() {
    EVENTS.lock().unwrap().clear();
    FXS.lock().unwrap().clear();
    FX_SEEN.lock().unwrap().clear();
    ENDED.lock().unwrap().clear();
    TIERS.lock().unwrap().clear();
    *VIEW.lock().unwrap() = None;
}

#[cfg(test)]
mod tests {
    use super::*;

    fn pick(screen: u8) -> Pick {
        Pick { team: 0, lane: 3, hero: "league_jinx".into(), screen, level: 1, tier: Tier::Gold, cards: [1, 2, 3],
               first: [1, 2, 3], chosen: 2, by: 0, slot: 0 }
    }

    #[test]
    fn the_screens_picks_are_kept_once_and_by_match() {
        let _g = super::super::tests::GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
        clear();
        assert!(view(5, 1));
        assert!(!view(5, 1));
        let e = Event { m: 5, s: 1, tick: 900, pick: pick(1) };
        push(e.clone());
        push(e.clone());
        push(Event { tick: 30, pick: pick(0), ..e.clone() });
        assert_eq!(events(5, 1).iter().map(|x| x.tick).collect::<Vec<_>>(), vec![30, 900]);
        tiers(5, 1, [Tier::Gold; 4]);
        tiers(5, 1, [Tier::Silver; 4]);
        assert_eq!(tiers_of(5, 1), Some([Tier::Gold; 4]));
        ended(5, 1, 40000);
        ended(5, 1, 40100);
        assert_eq!(ended_at(5, 1), Some(40000));
        // another match on screen: the last one's go
        assert!(view(6, 2));
        assert!(events(5, 1).is_empty() && ended_at(5, 1).is_none() && tiers_of(5, 1).is_none());
        assert_eq!(current(), Some((6, 2)));
        clear();
    }

    #[test]
    fn the_screens_effects_are_kept_once_and_by_match() {
        let _g = super::super::tests::GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
        clear();
        assert!(view(5, 1));
        let f = Fx { m: 5, s: 1, tick: 600, show: Show::Burn, at: (100_000, 200_000), to: Vec::new(), dur: 0 };
        fx(f.clone());
        fx(f.clone());
        fx(Fx { tick: 650, ..f.clone() });
        assert_eq!(fx_count(5, 1), 2);
        // live from its tick for `longest` ticks
        assert!(fx_live(5, 1, 599, 30).is_empty());
        assert_eq!(fx_live(5, 1, 640, 50).len(), 1);
        assert_eq!(fx_live(5, 1, 660, 61).len(), 2);
        assert!(view(6, 1));
        assert_eq!(fx_count(5, 1), 0);
        clear();
    }
}
