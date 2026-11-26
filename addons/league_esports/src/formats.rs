//! 国际赛每年换赛制（0.2.0，用户 11-26：「各种大型赛事每年都是一样的有点无聊了」，选了「每年轮换」）。
//!
//! 游戏建一届杯赛时看的是这一年的整份日程（0.7.3 的 EXE 里查过，0.5.1 带符号的 game_core 里同一套）：
//! - 小组赛抽签（fn 0x192e2e0）：日程里只要有一个 `TournamentGroupMatch` 的 round > 1，就建 16 队瑞士轮（33 场），
//!   否则建 4 组小组赛（组内单循环 24 场，每组前 2 名晋级；事件是 round 0、1 各 index 0..11）；
//! - 淘汰赛抽签（fn 0x1925ec0）：只要有一个 `TournamentMatch` 的 round > 2 或 index >= 4，就建 8 队双败（14 场），
//!   否则建 8 队单败（7 场：round 0 四场、round 1 两场、round 2 决赛）。
//!
//! 所以本包在抽签之前把日程里这两种事件写成想要的样子，游戏就照它自己的规则建（积分榜、对阵图、名次都是游戏的）。
//! 因为看的是整年，上下半年赛制不一样时，下一次抽签之前另外半年的事件也要换成不冲突的样子（[`target`]）。
//!
//! 原版日程是什么样子看生涯设置（用户的存档 2026-2028 是瑞士轮 + 双败，2029 起淘汰赛是单败），所以每种样子的日子都从
//! 这一年原版日程里推（[`half_days`]）：
//! - 双败 14 天 → 单败用其中第 0-3、7、8、11 天（就是游戏自己单败的排法：八强 4 天，隔 6 天半决赛，再隔 7 天决赛）；
//! - 单败 7 天 → 双败：跨度够 17 天时一天一场排开（决赛还在原来那天），不够就用游戏压缩赛程的排法（一天几场）；
//! - 小组赛 8 天：瑞士轮每天 4/4/4/4/4/4/6/3 场，分组每天 3 场（0.5.1 生成日程的排法）。
//! 生成的事件都在这半年的范围里（主赛事小组赛抽签之后、下个赛季开始 / 赛季补丁之前），出了范围这半年就不改。

use super::{date_str, day_of, kind, window, Entry, Rng};

/// 一届国际赛的赛制：小组赛阶段 + 淘汰赛。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Format {
    /// 瑞士轮 + 8 队双败（游戏原版）
    SwissDouble,
    /// 瑞士轮 + 8 队单败（2023 年起的世界赛）
    SwissSingle,
    /// 4 组小组赛 + 8 队双败
    GroupsDouble,
    /// 4 组小组赛 + 8 队单败（2015-2022 年的世界赛）
    GroupsSingle,
}

pub use Format::*;

impl Format {
    pub fn swiss(self) -> bool {
        matches!(self, SwissDouble | SwissSingle)
    }

    pub fn double(self) -> bool {
        matches!(self, SwissDouble | GroupsDouble)
    }

    pub fn code(self) -> u8 {
        match self {
            SwissDouble => 0,
            SwissSingle => 1,
            GroupsDouble => 2,
            GroupsSingle => 3,
        }
    }

    pub fn from_code(c: u8) -> Option<Format> {
        Some(match c {
            0 => SwissDouble,
            1 => SwissSingle,
            2 => GroupsDouble,
            3 => GroupsSingle,
            _ => return None,
        })
    }

    pub fn of(swiss: bool, double: bool) -> Format {
        match (swiss, double) {
            (true, true) => SwissDouble,
            (true, false) => SwissSingle,
            (false, true) => GroupsDouble,
            (false, false) => GroupsSingle,
        }
    }
}

/// 存档里「没定过」的赛制码（游戏自己的，不改日程）。
pub const UNSET: u8 = 9;

/// 全球总决赛每年从这几种里抽（权重）。
pub const WORLDS: [(Format, u64); 3] = [(SwissSingle, 45), (GroupsSingle, 30), (SwissDouble, 25)];
/// MSI 每年从这几种里抽（权重）。
pub const MSI: [(Format, u64); 3] = [(SwissDouble, 40), (GroupsDouble, 35), (GroupsSingle, 25)];

/// 按权重抽一个，`last`（去年实际打的）不抽；只剩它时照常抽。
pub fn pick(r: &mut Rng, opts: &[(Format, u64)], last: Option<Format>) -> Format {
    let pool: Vec<(Format, u64)> = opts.iter().copied().filter(|(f, _)| Some(*f) != last).collect();
    let pool = if pool.is_empty() { opts.to_vec() } else { pool };
    let total: u64 = pool.iter().map(|(_, w)| w).sum();
    let mut x = r.below(total.max(1));
    for (f, w) in &pool {
        if x < *w {
            return *f;
        }
        x -= w;
    }
    pool[0].0
}

/// 公告里的赛制说明。
pub fn words(f: Format, group_bo1: bool) -> String {
    let group = if f.swiss() {
        "16 队瑞士轮（5 轮，3 胜晋级、3 负出局）"
    } else {
        "4 组小组赛（每组 4 队单循环，前 2 名晋级）"
    };
    let bo = if group_bo1 { "全程 BO1" } else { "局数照原版" };
    let ko = if f.double() { "8 队双败淘汰" } else { "8 队单败淘汰" };
    let note = match f {
        SwissSingle => "，同 2023 年起的全球总决赛",
        GroupsSingle => "，同 2015—2022 年的全球总决赛",
        SwissDouble => "，游戏原版赛制",
        GroupsDouble => "",
    };
    format!("{group}{bo} + {ko}{note}")
}

// ---------------- 日程里的样子 ----------------

/// 这一种事件下一次抽签那一届的要求（None：这一年这种抽签都抽完了）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Shape {
    /// 照这一届自己的赛制
    Own,
    /// 换成和下一次抽签不冲突的样子（分组 / 单败），日子按那个样子排
    Compat,
    /// 现在是什么样就是什么样
    Keep,
}

/// 一个半年从原版日程推出来的日子：小组赛 8 天（瑞士轮、分组共用），双败 14 场、单败 7 场各自的日子（可以一天几场）；
/// 原版是瑞士轮 / 双败吗。
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct HalfDays {
    pub group: Option<Vec<i64>>,
    pub double: Option<Vec<i64>>,
    pub single: Option<Vec<i64>>,
    pub orig_swiss: Option<bool>,
    pub orig_double: Option<bool>,
}

/// 游戏一天一场排单败时，八强 / 半决赛 / 决赛在双败 14 天里的位置。
pub const SINGLE_IN_DOUBLE: [usize; 7] = [0, 1, 2, 3, 7, 8, 11];
/// 从单败推双败：一天一场（第 0 天起），最后一场在第 17 天（单败的决赛那天）。
pub const DOUBLE_SPREAD: [i64; 14] = [0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 12, 13, 15, 17];
/// 游戏压缩赛程的双败排法（0.5.1 `generate_tournament_matches`）：6 天打完。
pub const DOUBLE_CONDENSED: [i64; 14] = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 3, 4, 5];

fn round_index(event: &str) -> Option<(u64, u64)> {
    let num = |key: &str| -> Option<u64> {
        let rest = event.split(&format!("\"{key}\":")).nth(1)?;
        rest.chars().take_while(|c| c.is_ascii_digit()).collect::<String>().parse().ok()
    };
    Some((num("round")?, num("index")?))
}

/// 这半年窗口里某一种比赛事件（按 list 里的先后）。
pub fn events_of(list: &[Entry], half: usize, group: bool) -> Option<Vec<Entry>> {
    let (_, inside) = window(list, half)?;
    let want = if group { "TournamentGroupMatch" } else { "TournamentMatch" };
    Some(list.iter().zip(&inside).filter(|(e, &i)| i && kind(&e.event).0 == want).map(|(e, _)| e.clone()).collect())
}

fn days_sorted(events: &[Entry]) -> Option<Vec<i64>> {
    let mut v: Vec<i64> = events.iter().map(|e| day_of(&e.date)).collect::<Option<_>>()?;
    v.sort();
    Some(v)
}

fn distinct(v: &[i64]) -> Vec<i64> {
    let mut d = v.to_vec();
    d.dedup();
    d
}

/// 原版日程里这半年每种样子的日子。
pub fn half_days(orig: &[Entry], half: usize) -> Option<HalfDays> {
    let g = events_of(orig, half, true)?;
    let k = events_of(orig, half, false)?;
    let gd = days_sorted(&g)?;
    let kd = days_sorted(&k)?;
    let g8 = distinct(&gd);
    let (group, orig_swiss) = match (g.len(), reads_as(&g, true)) {
        (33, Some(true)) | (24, Some(false)) if g8.len() == 8 => (Some(g8), reads_as(&g, true)),
        _ => (None, None),
    };
    let (double, single, orig_double) = match (k.len(), reads_as(&k, false)) {
        (14, Some(true)) if distinct(&kd).len() == 14 => {
            let single: Vec<i64> = SINGLE_IN_DOUBLE.iter().map(|&i| kd[i]).collect();
            (Some(kd), Some(single), Some(true))
        }
        (7, Some(false)) if distinct(&kd).len() == 7 => {
            let (first, last) = (kd[0], kd[6]);
            let double = if last - first >= 17 {
                Some(DOUBLE_SPREAD.iter().map(|o| first + o).collect())
            } else if last - first >= 5 {
                Some(DOUBLE_CONDENSED.iter().map(|o| first + o).collect())
            } else {
                None
            };
            (double, Some(kd), Some(false))
        }
        _ => (None, None, None),
    };
    Some(HalfDays { group, double, single, orig_swiss, orig_double })
}

fn ev(kind: &str, round: u64, index: u64) -> String {
    format!("{{\"{kind}\":{{\"index\":{index},\"round\":{round}}}}}")
}

/// 小组赛事件：瑞士轮 33 个（8 天每天 4/4/4/4/4/4/6/3），分组 24 个（8 天每天 3 个，前 4 天 round 0，后 4 天 round 1）。
pub fn group_events(swiss: bool, days: &[i64]) -> Vec<Entry> {
    let mut out = Vec::new();
    if days.len() != 8 {
        return out;
    }
    if swiss {
        let plan: [(u64, std::ops::Range<u64>); 8] =
            [(0, 0..4), (0, 4..8), (1, 0..4), (1, 4..8), (2, 0..4), (2, 4..8), (3, 0..6), (4, 0..3)];
        for (d, (round, idx)) in days.iter().zip(plan) {
            for i in idx {
                out.push(Entry { date: date_str(*d), event: ev("TournamentGroupMatch", round, i) });
            }
        }
    } else {
        for (n, d) in days.iter().enumerate() {
            let round = (n / 4) as u64;
            for k in 0..3 {
                out.push(Entry { date: date_str(*d), event: ev("TournamentGroupMatch", round, (n % 4) as u64 * 3 + k) });
            }
        }
    }
    out
}

/// 淘汰赛事件，一场一个日子（`days` 双败 14 个、单败 7 个，可以重复）：双败 round 0 六场、1 四场、2 两场、3、4 各一场；
/// 单败 round 0 四场、1 两场、2 一场。
pub fn ko_events(double: bool, days: &[i64]) -> Vec<Entry> {
    let sizes: &[u64] = if double { &[6, 4, 2, 1, 1] } else { &[4, 2, 1] };
    let total: u64 = sizes.iter().sum();
    if days.len() as u64 != total {
        return Vec::new();
    }
    let mut out = Vec::new();
    let mut n = 0;
    for (round, size) in sizes.iter().enumerate() {
        for i in 0..*size {
            out.push(Entry { date: date_str(days[n]), event: ev("TournamentMatch", round as u64, i) });
            n += 1;
        }
    }
    out
}

/// 日程里这一种事件现在是什么赛制：瑞士轮 / 双败为 true（游戏判断的那条：round > 1 / round > 2 或 index >= 4）。
pub fn reads_as(list: &[Entry], group: bool) -> Option<bool> {
    let want = if group { "TournamentGroupMatch" } else { "TournamentMatch" };
    let mut any = false;
    for e in list {
        if kind(&e.event).0 != want {
            continue;
        }
        any = true;
        let (round, index) = round_index(&e.event)?;
        if (group && round > 1) || (!group && (round > 2 || index >= 4)) {
            return Some(true);
        }
    }
    any.then_some(false)
}

/// 这半年的范围：主赛事小组赛抽签那天（不含，之后的才算）到下个赛季开始 / 赛季补丁那天（不含）。
fn span(list: &[Entry], half: usize) -> Option<(i64, i64)> {
    let (draw, _) = window(list, half)?;
    let start = day_of(&list[draw].date)?;
    let end = list[draw + 1..]
        .iter()
        .find(|e| matches!(kind(&e.event).0.as_str(), "LeagueScheduleCreate" | "SeasonPatch"))
        .and_then(|e| day_of(&e.date))
        .unwrap_or(i64::MAX);
    Some((start, end))
}

/// 把 `list` 里这半年的小组赛（`group` 为 true）或淘汰赛事件换成 `events`；其他事件不动，按日子排好。
/// 已经是这样就原样返回；`events` 有一个不在这半年范围里就不换（None）。
pub fn replace(list: &[Entry], half: usize, group: bool, events: Vec<Entry>) -> Option<Vec<Entry>> {
    if events.is_empty() {
        return None;
    }
    let (start, end) = span(list, half)?;
    if events.iter().any(|e| day_of(&e.date).map_or(true, |d| d <= start || d >= end)) {
        return None;
    }
    let (_, inside) = window(list, half)?;
    let want = if group { "TournamentGroupMatch" } else { "TournamentMatch" };
    let now: Vec<&Entry> = list.iter().zip(&inside).filter(|(e, &i)| i && kind(&e.event).0 == want).map(|(e, _)| e).collect();
    if now.len() == events.len() && now.iter().zip(&events).all(|(a, b)| **a == *b) {
        return Some(list.to_vec());
    }
    let mut out: Vec<Entry> =
        list.iter().zip(&inside).filter(|(e, &i)| !(i && kind(&e.event).0 == want)).map(|(e, _)| e.clone()).collect();
    out.extend(events);
    out.sort_by_key(|e| day_of(&e.date).unwrap_or(i64::MAX));
    Some(out)
}

/// 这一种事件写成 `swiss_or_double` 的样子、日子挪 `k` 天要生成的事件（日子推不出来就是 None）。
pub fn generate(d: &HalfDays, group: bool, swiss_or_double: bool, k: i64) -> Option<Vec<Entry>> {
    let shift = |v: &Vec<i64>| -> Vec<i64> { v.iter().map(|x| x + k).collect() };
    if group {
        Some(group_events(swiss_or_double, &shift(d.group.as_ref()?)))
    } else {
        let days = if swiss_or_double { d.double.as_ref()? } else { d.single.as_ref()? };
        Some(ko_events(swiss_or_double, &shift(days)))
    }
}

/// 现在这半年这一种事件是哪个样子（按挪 `k` 天的日子比对）：Some(瑞士轮 / 双败为 true)，都对不上（游戏自己重排过）是 None。
pub fn current(list: &[Entry], d: &HalfDays, half: usize, group: bool, k: i64) -> Option<bool> {
    let now = events_of(list, half, group)?;
    [true, false].into_iter().find(|&s| generate(d, group, s, k).is_some_and(|g| g == now))
}

/// 半年里一种事件的要求：`own` 这一届自己是不是瑞士轮 / 双败，`next` 下一次这种抽签是哪半年、要不要瑞士轮 / 双败，
/// `in_use` 这一届这种比赛还在打。冲突 = 下一次抽签要分组 / 单败而这半年是瑞士轮 / 双败。
pub fn target(own: bool, next: Option<(usize, bool)>, half: usize, in_use: bool) -> Shape {
    if in_use {
        return Shape::Keep;
    }
    match next {
        None => Shape::Keep,
        Some((h, _)) if h == half => Shape::Own,
        Some((_, want)) if !want && own => Shape::Compat,
        Some(_) => Shape::Own,
    }
}

/// 一个半年的情况：从原版推出来的日子、现在两种事件的样子（None：不是本包排的，不碰）、两种事件挪的天数。
#[derive(Clone, Debug)]
pub struct Half {
    pub days: HalfDays,
    pub now_group: Option<bool>,
    pub now_ko: Option<bool>,
    pub k_group: i64,
    pub k_ko: i64,
}

/// 现在的日程里这半年是不是还是本包认得的样子（主赛事抽签那天和原版一样，两种事件都是某种样子挪 k 天）。
pub fn half_of(now: &[Entry], orig: &[Entry], half: usize, k_group: i64, k_ko: i64) -> Option<Half> {
    let a = window(now, half).and_then(|(d, _)| day_of(&now[d].date));
    let b = window(orig, half).and_then(|(d, _)| day_of(&orig[d].date));
    if a.is_none() || a != b {
        return None;
    }
    let days = half_days(orig, half)?;
    let now_group = current(now, &days, half, true, k_group);
    let now_ko = current(now, &days, half, false, k_ko);
    Some(Half { days, now_group, now_ko, k_group, k_ko })
}

/// 两届的小组赛、淘汰赛按要求写好。`halves`：两届的情况（None 不碰），`fmt`：两届定的赛制（None：这届不定，照原样，
/// 只在冲突时换），`k`：两届这次写的时候挪的天数（核对过赛程浮动以后的），`next_group` / `next_ko` 下一次抽签是哪半年，
/// `in_use` 两届各自的小组赛 / 淘汰赛还在打。换不了（日子推不出、出了范围、现在不是本包排的样子）就照旧。
pub fn shapes(
    list: &[Entry],
    halves: &[Option<Half>; 2],
    fmt: [Option<Format>; 2],
    k: [(i64, i64); 2],
    next_group: Option<usize>,
    next_ko: Option<usize>,
    in_use: [(bool, bool); 2],
) -> Vec<Entry> {
    let mut out = list.to_vec();
    let known_kind = |h: usize, group: bool| halves[h].as_ref().and_then(|x| if group { x.now_group } else { x.now_ko });
    // 本包碰不了的半年（认不得）里已经有瑞士轮 / 双败事件：整年一定读成瑞士轮 / 双败，下一次抽签那届也只能是它
    let locked = |group: bool| -> bool {
        (0..2).any(|h| known_kind(h, group).is_none() && events_of(list, h, group).and_then(|e| reads_as(&e, group)) == Some(true))
    };
    // 下一次抽签那一届要的：本包认得它、又定了赛制，用定的；认得、没定，是它现在的样子；认不得（本包不碰它），
    // 看日程里它现在实际是什么样（没有这种事件就不限制）
    let want = |h: usize, group: bool| -> bool {
        if locked(group) {
            return true;
        }
        match (known_kind(h, group), fmt[h]) {
            (Some(_), Some(f)) => if group { f.swiss() } else { f.double() },
            (Some(now), None) => now,
            (None, _) => events_of(list, h, group).and_then(|e| reads_as(&e, group)).unwrap_or(true),
        }
    };
    let ng = next_group.map(|h| (h, want(h, true)));
    let nk = next_ko.map(|h| (h, want(h, false)));
    for half in [0, 1] {
        let Some(x) = &halves[half] else { continue };
        for group in [true, false] {
            let Some(now_shape) = (if group { x.now_group } else { x.now_ko }) else { continue };
            let next_here = (if group { ng } else { nk }).is_some_and(|(h, _)| h == half);
            let own = match fmt[half] {
                // 下一次抽签就是这届、整年又被碰不了的半年定成了瑞士轮 / 双败：只能跟着
                _ if next_here && locked(group) => true,
                Some(f) => if group { f.swiss() } else { f.double() },
                None => now_shape,
            };
            let next = if group { ng } else { nk };
            let used = if group { in_use[half].0 } else { in_use[half].1 };
            let shape = match target(own, next, half, used) {
                Shape::Own => own,
                Shape::Compat => false,
                Shape::Keep => now_shape,
            };
            let kk = if group { k[half].0 } else { k[half].1 };
            if let Some(events) = generate(&x.days, group, shape, kk) {
                if let Some(next_list) = replace(&out, half, group, events) {
                    out = next_list;
                }
            }
        }
    }
    out
}

/// 两届（本包认得的那几届）的小组赛、淘汰赛事件换回原版的样子，日子是原版的挪 k 天（0.1.x 的赛程浮动核对在这上面做）。
pub fn canonical(list: &[Entry], halves: &[Option<Half>; 2]) -> Vec<Entry> {
    let mut out = list.to_vec();
    for half in [0, 1] {
        let Some(x) = &halves[half] else { continue };
        for (group, orig, kk) in [(true, x.days.orig_swiss, x.k_group), (false, x.days.orig_double, x.k_ko)] {
            let Some(s) = orig else { continue };
            if (if group { x.now_group } else { x.now_ko }).is_none() {
                continue;
            }
            if let Some(events) = generate(&x.days, group, s, kk) {
                if let Some(next_list) = replace(&out, half, group, events) {
                    out = next_list;
                }
            }
        }
    }
    out
}

/// 这半年按 `fmt`（None：原版）打的话，决赛是原版日程里的哪一天（还没挪）。
pub fn final_day(orig: &[Entry], half: usize, fmt: Option<Format>) -> Option<i64> {
    let d = half_days(orig, half)?;
    let days = match fmt {
        Some(f) if f.double() => d.double?,
        Some(_) => d.single?,
        None => if d.orig_double? { d.double? } else { d.single? },
    };
    days.last().copied()
}

/// 这半年两种事件都认得出是某种样子吗（游戏重排过就认不得）。
pub fn known(x: &Option<Half>) -> bool {
    x.as_ref().is_some_and(|x| x.now_group.is_some() && x.now_ko.is_some())
}

/// 这一年原版日程这半年是什么赛制（瑞士轮 / 分组 × 双败 / 单败）。
pub fn played(orig: &[Entry], half: usize) -> Option<Format> {
    let d = half_days(orig, half)?;
    Some(Format::of(d.orig_swiss?, d.orig_double?))
}
