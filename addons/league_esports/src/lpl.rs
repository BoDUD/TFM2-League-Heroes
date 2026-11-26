//! LPL 赛制（0.2.0，用户 11-26：「LPL赛制没有和英雄联盟一样」，选了「按登峰/涅槃做」）。
//!
//! 游戏的联赛是 10 队双循环（90 场，开赛季时一次建好，每场带日期）+ 6 队双败季后赛（8 场，种子是「常规赛第 N 名」）。
//! 本包只动 LPL（一级联赛 TACC）这 90 场的对阵和日期，照真实 LPL 2024 夏季赛 / 2026 赛段的思路缩到 10 队：
//! - 第一阶段：前 45 场，10 队单循环 BO3；
//! - 第二阶段：按第一阶段排名分登峰组（前 6）、涅槃组（后 4），组内双循环 BO3（30 + 12 = 42 场）；
//! - 骑士之路（BO5，剩下的 3 场挪到常规赛和季后赛之间的空档）：登峰 5 vs 登峰 6（胜者进季后赛），涅槃 1 vs 涅槃 2
//!   （负者出局），再由前一场的负者打后一场的胜者（胜者进季后赛）；
//! - 季后赛：游戏自己的 6 队双败，登峰前四是 1-4 号种子，骑士之路的两个胜者是 5、6 号种子（从败者组打起）；
//! - 涅槃组第 3、4 名打升降级赛（游戏挑的人不一样就换过来）。
//! 组内排名按总战绩（第一阶段 + 第二阶段）：胜场、小分差、小分胜场、相互胜负。积分榜还是游戏的一张总表。
//!
//! 比赛按自己的日期打（0.5.1 的 game_core 里压缩赛程也只是改每场的日期），对阵槽位用游戏自己的写法：
//! `{"Normal":队}`、`{"CompetitionRank":[联赛届,名次]}`、`{"WinnerOf":场}`、`{"LoserOf":场}`。

use super::{compact, date_str, day_of, ids_at, ints, news, run_state, wlog, Run};
use mod_api_stable::*;
use std::collections::{BTreeMap, BTreeSet};

// ---------------- 纯函数 ----------------

/// 一场打完的比赛：两队、胜者、两队小分。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Game {
    pub a: usize,
    pub b: usize,
    pub winner: usize,
    pub sa: i64,
    pub sb: i64,
}

/// 单循环（圆圈法）：n 队（偶数）n-1 轮，每轮 n/2 场。主客：不动的那队隔轮换，其他按位置单双（每队主场差不超过 1）。
pub fn round_robin(teams: &[usize]) -> Vec<Vec<(usize, usize)>> {
    let n = teams.len();
    if n < 2 || n % 2 == 1 {
        return Vec::new();
    }
    let mut ring = teams.to_vec();
    let mut rounds = Vec::new();
    for r in 0..n - 1 {
        let mut round = Vec::new();
        for i in 0..n / 2 {
            let (x, y) = (ring[i], ring[n - 1 - i]);
            let home_first = if i == 0 { r % 2 == 0 } else { i % 2 == 1 };
            round.push(if home_first { (x, y) } else { (y, x) });
        }
        rounds.push(round);
        let last = ring.pop().unwrap_or(0);
        ring.insert(1, last);
    }
    rounds
}

/// 双循环：单循环再来一遍，主客对调。
pub fn double_round_robin(teams: &[usize]) -> Vec<Vec<(usize, usize)>> {
    let first = round_robin(teams);
    let second: Vec<Vec<(usize, usize)>> = first.iter().map(|r| r.iter().map(|&(x, y)| (y, x)).collect()).collect();
    first.into_iter().chain(second).collect()
}

/// 把一轮一轮的比赛按顺序排进时间槽（每个槽一个日子，日子不减）：同一天里一支队只打一场；一场最多提前一轮。
pub fn fit(rounds: &[Vec<(usize, usize)>], slot_days: &[i64]) -> Option<Vec<(usize, usize)>> {
    fit_tracks(&[rounds.to_vec()], slot_days)
}

/// 第二阶段：登峰组、涅槃组两个双循环各走各的轮次，一起排进 42 个时间槽。
pub fn fit_phase2(a: &[usize], n: &[usize], slot_days: &[i64]) -> Option<Vec<(usize, usize)>> {
    fit_tracks(&[double_round_robin(a), double_round_robin(n)], slot_days)
}

/// 几组各自一轮一轮的比赛（组和组之间队伍不重）排进时间槽（日子不减）：同一天里一支队只打一场；每组的一场最多比这组
/// 还没排完的最早那一轮提前一轮。一天一天地挑：先挑让几组进度最齐的那几场，装不下了就退回去换。排不出来是 None。
pub fn fit_tracks(tracks: &[Vec<Vec<(usize, usize)>>], slot_days: &[i64]) -> Option<Vec<(usize, usize)>> {
    // （组、轮、对阵）
    let all: Vec<(usize, usize, (usize, usize))> = tracks
        .iter()
        .enumerate()
        .flat_map(|(t, rounds)| rounds.iter().enumerate().flat_map(move |(r, ms)| ms.iter().map(move |&m| (t, r, m))))
        .collect();
    if all.len() != slot_days.len() || slot_days.windows(2).any(|w| w[0] > w[1]) {
        return None;
    }
    // 每天几个槽
    let mut days: Vec<usize> = Vec::new();
    for (i, &d) in slot_days.iter().enumerate() {
        if i == 0 || slot_days[i - 1] != d {
            days.push(1);
        } else if let Some(c) = days.last_mut() {
            *c += 1;
        }
    }
    let size: Vec<usize> = tracks.iter().map(|r| r.iter().map(|x| x.len()).sum()).collect();
    // 每组一天最多几场（队数的一半）
    let per_day: Vec<usize> = tracks
        .iter()
        .map(|r| r.iter().flatten().flat_map(|&(x, y)| [x, y]).collect::<std::collections::BTreeSet<usize>>().len() / 2)
        .collect();
    struct S<'a> {
        all: &'a [(usize, usize, (usize, usize))],
        days: &'a [usize],
        size: &'a [usize],
        per_day: &'a [usize],
        used: Vec<bool>,
        done: Vec<usize>,
        out: Vec<usize>,
        budget: u32,
    }
    /// 从第 `k` 天起剩下的还装得下吗：每组剩下的场次 <= 以后每天它最多能打的之和；以后每天的槽 <= 那天各组最多能打的之和。
    fn room(s: &S<'_>, k: usize) -> bool {
        let left: Vec<usize> = (0..s.size.len()).map(|t| s.size[t] - s.done[t]).collect();
        for t in 0..s.size.len() {
            let c: usize = s.days[k..].iter().map(|&c| s.per_day[t].min(c)).sum();
            if left[t] > c {
                return false;
            }
        }
        s.days[k..].iter().all(|&c| c <= (0..s.size.len()).map(|t| s.per_day[t].min(left[t])).sum::<usize>())
    }
    /// 这一天能挑的：没排过、不超过这组最早没排完那一轮的下一轮
    fn pool(s: &S<'_>) -> Vec<usize> {
        let low: Vec<usize> = (0..s.size.len())
            .map(|t| s.all.iter().zip(&s.used).filter(|(m, &u)| !u && m.0 == t).map(|(m, _)| m.1).min().unwrap_or(usize::MAX))
            .collect();
        (0..s.all.len()).filter(|&i| !s.used[i] && s.all[i].1 <= low[s.all[i].0].saturating_add(1)).collect()
    }
    /// 从 `pool` 里挑 `k` 场队伍不重的（按编号从小到大，不重复）
    fn combos(s: &S<'_>, pool: &[usize], k: usize, from: usize, cur: &mut Vec<usize>, out: &mut Vec<Vec<usize>>) {
        if cur.len() == k {
            out.push(cur.clone());
            return;
        }
        if out.len() > 4000 {
            return;
        }
        for p in from..pool.len() {
            let i = pool[p];
            let (_, _, (x, y)) = s.all[i];
            if cur.iter().any(|&j| {
                let (_, _, (a, b)) = s.all[j];
                a == x || a == y || b == x || b == y
            }) {
                continue;
            }
            cur.push(i);
            combos(s, pool, k, p + 1, cur, out);
            cur.pop();
        }
    }
    fn go(s: &mut S<'_>, k: usize) -> bool {
        if k == s.days.len() {
            return s.out.len() == s.all.len();
        }
        if s.budget == 0 || !room(s, k) {
            return false;
        }
        s.budget -= 1;
        let slots = s.days[k];
        let pool = pool(s);
        let mut cs = Vec::new();
        combos(s, &pool, slots, 0, &mut Vec::new(), &mut cs);
        // 挑完以后各组进度（打了的比例）差得最少的先试，再按轮次早的先
        let placed: usize = s.done.iter().sum();
        let total: usize = s.size.iter().sum();
        let score = |c: &Vec<usize>| -> (u64, usize) {
            let mut done = s.done.clone();
            for &i in c {
                done[s.all[i].0] += 1;
            }
            let goal = (placed + c.len()) as f64 / total.max(1) as f64;
            let gap: f64 = (0..done.len()).map(|t| (done[t] as f64 / s.size[t].max(1) as f64 - goal).abs()).sum();
            ((gap * 1e6) as u64, c.iter().map(|&i| s.all[i].1).sum())
        };
        cs.sort_by_key(|c| score(c));
        for c in cs {
            for &i in &c {
                s.used[i] = true;
                s.done[s.all[i].0] += 1;
                s.out.push(i);
            }
            if go(s, k + 1) {
                return true;
            }
            for &i in &c {
                s.used[i] = false;
                s.done[s.all[i].0] -= 1;
                s.out.pop();
            }
        }
        false
    }
    let mut s = S {
        all: &all,
        days: &days,
        size: &size,
        per_day: &per_day,
        used: vec![false; all.len()],
        done: vec![0; size.len()],
        out: Vec::with_capacity(all.len()),
        budget: 200_000,
    };
    go(&mut s, 0).then(|| s.out.iter().map(|&i| all[i].2).collect())
}

/// 每队的（胜场、小分差、小分胜场）。
fn table(teams: &[usize], games: &[Game]) -> BTreeMap<usize, (i64, i64, i64)> {
    let mut t: BTreeMap<usize, (i64, i64, i64)> = teams.iter().map(|&x| (x, (0, 0, 0))).collect();
    for g in games {
        for (me, mine, theirs) in [(g.a, g.sa, g.sb), (g.b, g.sb, g.sa)] {
            if let Some(e) = t.get_mut(&me) {
                e.0 += i64::from(g.winner == me);
                e.1 += mine - theirs;
                e.2 += mine;
            }
        }
    }
    t
}

/// 排名：胜场、小分差、小分胜场，一样的看相互之间的胜场，再一样按队伍编号。
pub fn rank(teams: &[usize], games: &[Game]) -> Vec<usize> {
    let t = table(teams, games);
    let mut order = teams.to_vec();
    order.sort_by(|x, y| {
        let (a, b) = (t[x], t[y]);
        b.cmp(&a).then(x.cmp(y))
    });
    // 积分一样的一段：相互之间的胜场
    let mut out = Vec::new();
    let mut i = 0;
    while i < order.len() {
        let mut j = i + 1;
        while j < order.len() && t[&order[j]] == t[&order[i]] {
            j += 1;
        }
        let tied: BTreeSet<usize> = order[i..j].iter().copied().collect();
        let mut seg = order[i..j].to_vec();
        if seg.len() > 1 {
            let h2h = |x: usize| games.iter().filter(|g| g.winner == x && tied.contains(&g.a) && tied.contains(&g.b)).count();
            seg.sort_by(|x, y| h2h(*y).cmp(&h2h(*x)).then(x.cmp(y)));
        }
        out.extend(seg);
        i = j;
    }
    out
}

/// 这 45 场是不是 10 队单循环（每对各一场）。
pub fn is_single_rr(teams: &[usize], pairs: &[(usize, usize)]) -> bool {
    let n = teams.len();
    if pairs.len() != n * (n - 1) / 2 {
        return false;
    }
    let set: BTreeSet<usize> = teams.iter().copied().collect();
    let mut seen = BTreeSet::new();
    pairs.iter().all(|&(x, y)| x != y && set.contains(&x) && set.contains(&y) && seen.insert((x.min(y), x.max(y))))
}

/// 一个对阵槽位。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Slot {
    Normal(usize),
    Rank(usize, usize),
    Winner(usize),
    Loser(usize),
    Other,
}

pub fn slot_of(json: &str) -> Slot {
    let s = compact(json);
    let n = ints(&s);
    let head = |k: &str| s.starts_with(&format!("{{\"{k}\":"));
    match () {
        _ if head("Normal") && n.len() == 1 => Slot::Normal(n[0]),
        _ if head("CompetitionRank") && n.len() == 2 => Slot::Rank(n[0], n[1]),
        _ if head("WinnerOf") && n.len() == 1 => Slot::Winner(n[0]),
        _ if head("LoserOf") && n.len() == 1 => Slot::Loser(n[0]),
        _ => Slot::Other,
    }
}

pub fn slot_json(s: Slot) -> Option<String> {
    Some(match s {
        Slot::Normal(t) => format!("{{\"Normal\":{t}}}"),
        Slot::Rank(c, r) => format!("{{\"CompetitionRank\":[{c},{r}]}}"),
        Slot::Winner(m) => format!("{{\"WinnerOf\":{m}}}"),
        Slot::Loser(m) => format!("{{\"LoserOf\":{m}}}"),
        Slot::Other => return None,
    })
}

/// `running_state` 打完时的（胜者、一队小分、二队小分）。
pub fn end_of(json: &str) -> Option<(usize, i64, i64)> {
    let s = compact(json);
    if !s.starts_with("{\"End\":") {
        return None;
    }
    let num = |key: &str| -> Option<i64> {
        let rest = s.split(&format!("\"{key}\":")).nth(1)?;
        rest.chars().take_while(|c| c.is_ascii_digit()).collect::<String>().parse().ok()
    };
    Some((num("winner")? as usize, num("team1_score")?, num("team2_score")?))
}

/// 季后赛里「常规赛第 r 名」换成什么：1-4 名是登峰前四（`a`，None 是还没打完先不换），5、6 名是骑士之路两个胜者。
pub fn seed_for(r: usize, a: Option<&[usize]>, kr: [usize; 3]) -> Option<Slot> {
    match r {
        1..=4 => a.and_then(|a| a.get(r - 1)).map(|&t| Slot::Normal(t)),
        5 => Some(Slot::Winner(kr[0])),
        6 => Some(Slot::Winner(kr[2])),
        _ => None,
    }
}

/// 升降级赛里 LPL 这边的队换成涅槃组第 3、4 名：每场（这边现在的队）→ 换成谁。已经是这两队的不动。
pub fn promo_swaps(now: &[usize], want: [usize; 2]) -> Vec<Option<usize>> {
    let mut missing: Vec<usize> = want.iter().copied().filter(|w| !now.contains(w)).collect();
    now.iter().map(|t| if want.contains(t) { None } else if missing.is_empty() { None } else { Some(missing.remove(0)) }).collect()
}

// ---------------- 存档里的进度 ----------------

/// 一届 LPL 走到哪了（存档键 `lpl:<联赛届 id>`）。
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Progress {
    /// skip / p1 / p2 / kr / done
    pub phase: String,
    pub teams: Vec<usize>,
    /// 第一阶段 45 场、第二阶段 42 场、骑士之路 3 场
    pub first: Vec<usize>,
    pub group: Vec<usize>,
    pub kr: Vec<usize>,
    /// 登峰组 6、涅槃组 4（排名顺序）
    pub a: Vec<usize>,
    pub n: Vec<usize>,
    /// 打升降级的两队（涅槃 3、4）
    pub rel: Vec<usize>,
    pub promo_done: bool,
    pub why: String,
    /// 开赛季时从第一阶段最后一天挪走的场次：（场、原来的日期、原来的两队），放弃时还原
    pub early: Vec<(usize, String, usize, usize)>,
}

impl Progress {
    pub fn to_text(&self) -> String {
        let j = |v: &[usize]| v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",");
        let early: Vec<String> = self.early.iter().map(|(m, d, a, b)| format!("{m}@{d}@{a}@{b}")).collect();
        format!(
            "phase={};teams={};first={};group={};kr={};a={};n={};rel={};promo={};early={};why={}",
            self.phase,
            j(&self.teams),
            j(&self.first),
            j(&self.group),
            j(&self.kr),
            j(&self.a),
            j(&self.n),
            j(&self.rel),
            u8::from(self.promo_done),
            early.join(","),
            self.why.replace([';', '='], " ")
        )
    }

    pub fn from_text(s: &str) -> Option<Progress> {
        let mut m = BTreeMap::new();
        for part in s.split(';') {
            let (k, v) = part.split_once('=')?;
            m.insert(k, v);
        }
        let ids = |k: &str| -> Vec<usize> { m.get(k).map(|v| v.split(',').filter_map(|x| x.parse().ok()).collect()).unwrap_or_default() };
        Some(Progress {
            phase: m.get("phase")?.to_string(),
            teams: ids("teams"),
            first: ids("first"),
            group: ids("group"),
            kr: ids("kr"),
            a: ids("a"),
            n: ids("n"),
            rel: ids("rel"),
            promo_done: m.get("promo").is_some_and(|v| *v == "1"),
            why: m.get("why").map(|v| v.to_string()).unwrap_or_default(),
            early: m
                .get("early")
                .map(|v| {
                    v.split(',')
                        .filter_map(|x| {
                            let p: Vec<&str> = x.split('@').collect();
                            (p.len() == 4).then(|| Some((p[0].parse().ok()?, p[1].to_string(), p[2].parse().ok()?, p[3].parse().ok()?))).flatten()
                        })
                        .collect()
                })
                .unwrap_or_default(),
        })
    }
}

fn key(lc: usize) -> String {
    format!("lpl:{lc}")
}

pub fn load(ctx: &StableServerCtx<'_>, lc: usize) -> Option<Progress> {
    ctx.save_get_string(&key(lc)).and_then(|s| Progress::from_text(&s))
}

fn store(ctx: &mut StableServerCtx<'_>, lc: usize, p: &Progress) {
    let ok = ctx.save_set_string(&key(lc), &p.to_text());
    wlog(format!("LPL {lc} -> {} (kept {ok}): {}", p.phase, p.to_text()));
}

// ---------------- 读写比赛 ----------------

const MATCH: RecordKindV1 = RecordKindV1::Match;
const LC: RecordKindV1 = RecordKindV1::LeagueCompetition;

fn date_of(ctx: &StableServerCtx<'_>, m: usize) -> Option<String> {
    ctx.record_get_string(MATCH, m, "date")
}

fn slot(ctx: &StableServerCtx<'_>, m: usize, side: &str) -> Slot {
    ctx.record_get_json(MATCH, m, side).map(|s| slot_of(&s)).unwrap_or(Slot::Other)
}

fn pair(ctx: &StableServerCtx<'_>, m: usize) -> Option<(usize, usize)> {
    match (slot(ctx, m, "team1"), slot(ctx, m, "team2")) {
        (Slot::Normal(a), Slot::Normal(b)) => Some((a, b)),
        _ => None,
    }
}

fn game(ctx: &StableServerCtx<'_>, m: usize) -> Option<Game> {
    let (a, b) = pair(ctx, m)?;
    let (winner, sa, sb) = end_of(&ctx.record_get_json(MATCH, m, "running_state")?)?;
    Some(Game { a, b, winner, sa, sb })
}

fn set(ctx: &mut StableServerCtx<'_>, m: usize, path: &str, json: &str) -> bool {
    let ok = ctx.record_set_json(MATCH, m, path, json);
    let back = ctx.record_get_json(MATCH, m, path).map(|s| compact(&s));
    let same = back.as_deref() == Some(compact(json).as_str());
    if !(ok && same) {
        wlog(format!("LPL match {m}: {path} <- {json} {} (reads {back:?})", if ok { "accepted but reads back otherwise" } else { "REFUSED" }));
    }
    ok && same
}

/// 两边一起写：第二边写不进去，第一边改回原样（不会留下一边新一边旧）。
fn set_pair(ctx: &mut StableServerCtx<'_>, m: usize, s1: Slot, s2: Slot) -> bool {
    let (Some(a), Some(b)) = (slot_json(s1), slot_json(s2)) else { return false };
    let old1 = ctx.record_get_json(MATCH, m, "team1");
    if !set(ctx, m, "team1", &a) {
        return false;
    }
    if set(ctx, m, "team2", &b) {
        return true;
    }
    if let Some(o) = old1 {
        set(ctx, m, "team1", &compact(&o));
    }
    false
}

fn team_name(ctx: &StableServerCtx<'_>, t: usize) -> String {
    ctx.team_get_string(t, "name").filter(|s| !s.is_empty()).unwrap_or_else(|| format!("#{t}"))
}

fn names(ctx: &StableServerCtx<'_>, ts: &[usize]) -> String {
    ts.iter().map(|&t| team_name(ctx, t)).collect::<Vec<_>>().join("、")
}

/// LPL（一级联赛 TACC）的 League 记录 id。
pub fn lpl_league(ctx: &StableServerCtx<'_>) -> Option<usize> {
    let kind = RecordKindV1::League;
    ctx.record_ids(kind).into_iter().find(|&id| {
        ctx.record_get_string(kind, id, "name").as_deref() == Some("TACC")
            && ctx.record_get_json(kind, id, "division").is_some_and(|d| d.trim() == "0")
    })
}

/// 现在这一届 LPL（还没结束的那届）。
pub fn current(ctx: &StableServerCtx<'_>) -> Option<usize> {
    let lg = lpl_league(ctx)?;
    let lc = *ids_at(ctx, RecordKindV1::League, lg, "competitions").last()?;
    let done = ctx.record_get_json(LC, lc, "finalized").is_some_and(|v| v.trim() == "true");
    let promo_done = ctx.record_get_json(LC, lc, "promotion_series_finalized").is_some_and(|v| v.trim() == "true");
    (!(done && promo_done)).then_some(lc)
}

fn sorted_by_date(ctx: &StableServerCtx<'_>, ids: &[usize]) -> Vec<(usize, String)> {
    let mut v: Vec<(usize, String)> = ids.iter().filter_map(|&m| Some((m, date_of(ctx, m)?))).collect();
    v.sort_by(|x, y| x.1.cmp(&y.1).then(x.0.cmp(&y.0)));
    v
}

fn all_over(ctx: &StableServerCtx<'_>, ids: &[usize]) -> bool {
    !ids.is_empty() && ids.iter().all(|&m| run_state(ctx, m) == Run::Over)
}

fn all_wait(ctx: &StableServerCtx<'_>, ids: &[usize]) -> bool {
    ids.iter().all(|&m| run_state(ctx, m) == Run::Wait)
}

fn split_name(ctx: &StableServerCtx<'_>, lc: usize) -> &'static str {
    match ctx.record_get_string(LC, lc, "league_type").as_deref() {
        Some("Summer") => "夏季赛",
        _ => "春季赛",
    }
}

/// 某天、某个时刻的比赛日期字符串（`time` 是 `T17:00:00` 这样的后半截）。
fn at(day: i64, time: &str) -> String {
    format!("{}{}", date_str(day), time)
}

fn time_part(s: &str) -> String {
    s.get(10..).unwrap_or("T17:00:00").to_string()
}

// ---------------- 每个 tick ----------------

/// 骑士之路和第二阶段的比赛（本包定局数）：这届 LPL 的（第一、二阶段的场次，骑士之路的场次）。
pub fn series(ctx: &StableServerCtx<'_>) -> Option<(usize, Vec<usize>, Vec<usize>)> {
    let lc = current(ctx)?;
    let p = load(ctx, lc)?;
    // 分组以前就放弃的一届照每年的常规赛局数；骑士之路排好以后放弃的，骑士之路还是 BO5
    if p.first.is_empty() || (p.phase == "skip" && p.kr.len() != 3) {
        return None;
    }
    let mut regular = p.first.clone();
    regular.extend(&p.group);
    Some((lc, regular, p.kr))
}

/// 这一届不再往下做：记下原因；开赛季时挪走的场次（还没打的）改回原来的对阵（双循环还是完整的）；第一阶段还没打完时
/// 日子也改回去，打完了（原来那天已经过了）就留在常规赛之后那天打。
fn skip(ctx: &mut StableServerCtx<'_>, lc: usize, p: Option<&Progress>, why: &str) {
    let mut q = p.cloned().unwrap_or_default();
    if q.kr.len() != 3 {
        let phase1_on = q.first.iter().any(|&m| run_state(ctx, m) == Run::Wait);
        for (m, date, a, b) in std::mem::take(&mut q.early) {
            if run_state(ctx, m) == Run::Wait {
                let back = phase1_on && set(ctx, m, "date", &format!("\"{date}\""));
                let ok = set_pair(ctx, m, Slot::Normal(a), Slot::Normal(b));
                wlog(format!("LPL {lc}: match {m} back to {a} vs {b} (written {ok}), date {}",
                             if back { date.as_str() } else { "kept after the season" }));
            }
        }
    }
    q.phase = "skip".into();
    q.why = why.into();
    store(ctx, lc, &q);
}

/// 这届 LPL 往前推一步（每个 tick 都可以调，没事做就只读几条记录）。
pub fn step(ctx: &mut StableServerCtx<'_>) {
    let Some(lc) = current(ctx) else { return };
    let mut p = match load(ctx, lc) {
        Some(p) => p,
        None => match start(ctx, lc) {
            Some(p) => p,
            None => return,
        },
    };
    // 存档里的进度要对得上（坏了就不做，不去碰比赛）：场数、队数，场次不重复
    let ids: BTreeSet<usize> = p.first.iter().chain(&p.group).chain(&p.kr).copied().collect();
    let sane = p.phase == "skip"
        || (p.teams.len() == 10
            && p.first.len() == 45
            && ids.len() == p.first.len() + p.group.len() + p.kr.len()
            && match p.phase.as_str() {
                "p1" => p.group.len() == 45 && p.kr.is_empty(),
                _ => p.group.len() == 42 && p.kr.len() == 3 && p.a.len() == 6 && p.n.len() == 4,
            });
    if !sane {
        skip(ctx, lc, Some(&p), "the progress kept in the save does not add up");
        return;
    }
    match p.phase.as_str() {
        "p1" if all_over(ctx, &p.first) => to_groups(ctx, lc, &mut p),
        "p2" if all_over(ctx, &p.group) => to_knights(ctx, lc, &mut p),
        "kr" if all_over(ctx, &p.kr) => {
            let adv: Vec<usize> = [p.kr[0], p.kr[2]].iter().filter_map(|&m| game(ctx, m).map(|g| g.winner)).collect();
            let y = year_of(ctx, &p);
            news(
                ctx,
                &format!("{y} LPL {}骑士之路结果", split_name(ctx, lc)),
                &format!("{} 晋级季后赛，从败者组首轮打起。", names(ctx, &adv)),
            );
            p.phase = "done".into();
            store(ctx, lc, &p);
        }
        _ => {}
    }
    if matches!(p.phase.as_str(), "kr" | "done") && !p.promo_done && p.rel.len() == 2 {
        promotion(ctx, lc, &mut p);
    }
}

fn year_of(ctx: &StableServerCtx<'_>, p: &Progress) -> i64 {
    p.first.first().and_then(|&m| date_of(ctx, m)).and_then(|d| day_of(&d)).map(|d| super::civil_from_days(d).0).unwrap_or(0)
}

/// 第一次看到这一届：常规赛 90 场、10 队；前 45 场（按日期）要是单循环（新的一届可以重排），后 45 场都还没打。
/// 先把以后每一步都查一遍（第二阶段 42 场排得进、骑士之路有空档、挪走的场次放得下），都行才动比赛。
fn start(ctx: &mut StableServerCtx<'_>, lc: usize) -> Option<Progress> {
    let matches = ids_at(ctx, LC, lc, "matches");
    if matches.is_empty() {
        return None;
    }
    let by_date = sorted_by_date(ctx, &matches);
    let mut teams: Vec<usize> = Vec::new();
    for &(m, _) in &by_date {
        if let Some((a, b)) = pair(ctx, m) {
            for t in [a, b] {
                if !teams.contains(&t) {
                    teams.push(t);
                }
            }
        }
    }
    teams.sort();
    if by_date.len() != 90 || teams.len() != 10 {
        skip(ctx, lc, None, &format!("{} matches, {} teams (want 90 / 10)", by_date.len(), teams.len()));
        return None;
    }
    let first: Vec<usize> = by_date[..45].iter().map(|x| x.0).collect();
    let second: Vec<usize> = by_date[45..].iter().map(|x| x.0).collect();
    if !all_wait(ctx, &second) {
        skip(ctx, lc, None, "phase 2 already started");
        return None;
    }
    let pairs: Vec<(usize, usize)> = first.iter().filter_map(|&m| pair(ctx, m)).collect();
    let rr = is_single_rr(&teams, &pairs);
    if !rr && !all_wait(ctx, &first) {
        skip(ctx, lc, None, "the first 45 matches are not a single round robin and some are played");
        return None;
    }
    let day = |s: &str| day_of(s).unwrap_or(0);
    let last1 = by_date[..45].iter().map(|x| day(&x.1)).max().unwrap_or(0);
    let end = by_date.iter().map(|x| day(&x.1)).max().unwrap_or(0);
    let Some(first_po) = ids_at(ctx, LC, lc, "playoffs").iter().filter_map(|&m| date_of(ctx, m)).map(|d| day(&d)).min() else {
        skip(ctx, lc, None, "no playoff dates");
        return None;
    };
    // 第一阶段要重排时：排得进
    let order1 = if rr {
        None
    } else {
        let days: Vec<i64> = by_date[..45].iter().map(|x| day(&x.1)).collect();
        match fit(&round_robin(&teams), &days) {
            Some(o) => Some(o),
            None => {
                skip(ctx, lc, None, "no single round robin fits the first 45 dates");
                return None;
            }
        }
    };
    // 第二阶段：第一阶段最后一天之后的 42 个日子排得进两组双循环（排法只看日子，先拿任意 6 + 4 试）
    let later: Vec<i64> = by_date[45..].iter().map(|x| day(&x.1)).filter(|&d| d > last1).collect();
    if later.len() < 42 || fit_phase2(&teams[..6], &teams[6..], &later[..42]).is_none() {
        skip(ctx, lc, None, &format!("phase 2 does not fit the {} dates after phase 1", later.len()));
        return None;
    }
    // 骑士之路：第二阶段最后一天之后、季后赛之前至少还有两天
    if later[41] + 2 >= first_po {
        skip(ctx, lc, None, "no room for 骑士之路 before the playoffs");
        return None;
    }
    // 和第一阶段最后一场同一天（或更早）的第二阶段场次：最多 3 场，放到常规赛最后一天的后一天
    let early: Vec<(usize, String)> = by_date[45..].iter().filter(|x| day(&x.1) <= last1).cloned().collect();
    if early.len() > 3 || (!early.is_empty() && end + 1 >= first_po) {
        skip(ctx, lc, None, &format!("{} phase 2 matches share phase 1's last day and there is no room after the season", early.len()));
        return None;
    }
    // 都行：动比赛
    if let Some(order) = order1 {
        if !set_pair(ctx, first[0], Slot::Normal(order[0].0), Slot::Normal(order[0].1)) {
            skip(ctx, lc, None, "the game refused the first single round robin pairing");
            return None;
        }
        let mut ok = true;
        for (&m, &(a, b)) in first.iter().zip(&order).skip(1) {
            ok &= set_pair(ctx, m, Slot::Normal(a), Slot::Normal(b));
        }
        wlog(format!("LPL {lc}: the first 45 matches set to a single round robin (all written: {ok})"));
    }
    // 分组要等第一阶段打完：同一天的那几场先挪走（之后是骑士之路），对阵先按总排名占位；原来的记下，放弃时改回去
    let mut kept = Vec::new();
    let mut ok = true;
    for (i, (m, date)) in early.iter().enumerate() {
        let Some((a, b)) = pair(ctx, *m) else {
            ok = false;
            continue;
        };
        let moved = set(ctx, *m, "date", &format!("\"{}\"", at(end + 1, &time_part(date))));
        if moved {
            kept.push((*m, date.clone(), a, b));
        }
        ok &= moved && set_pair(ctx, *m, Slot::Rank(lc, 5 + 2 * i), Slot::Rank(lc, 6 + 2 * i));
    }
    if !early.is_empty() {
        wlog(format!("LPL {lc}: phase 2 matches {:?} on phase 1's last day moved to {} (all written: {ok})",
                     early.iter().map(|x| x.0).collect::<Vec<_>>(), date_str(end + 1)));
    }
    let p = Progress { phase: "p1".into(), teams, first, group: second, early: kept, ..Progress::default() };
    if !ok {
        skip(ctx, lc, Some(&p), "moving the phase 2 matches off phase 1's last day failed");
        return None;
    }
    store(ctx, lc, &p);
    Some(p)
}

/// 第一阶段打完：分组，第二阶段 42 场、骑士之路 3 场排好，季后赛 5、6 号种子接到骑士之路上。
fn to_groups(ctx: &mut StableServerCtx<'_>, lc: usize, p: &mut Progress) {
    let second = p.group.clone();
    if !all_wait(ctx, &second) {
        skip(ctx, lc, Some(&*p), "phase 2 started before the groups were drawn");
        return;
    }
    let games: Vec<Game> = p.first.iter().filter_map(|&m| game(ctx, m)).collect();
    if games.len() != p.first.len() {
        skip(ctx, lc, Some(&*p), "a phase 1 result could not be read");
        return;
    }
    let order = rank(&p.teams, &games);
    let (a, n) = (order[..6].to_vec(), order[6..].to_vec());
    let last1 = p.first.iter().filter_map(|&m| date_of(ctx, m)).max().and_then(|d| day_of(&d)).unwrap_or(0);
    let by_date = sorted_by_date(ctx, &second);
    let later: Vec<(usize, String)> = by_date.iter().filter(|x| day_of(&x.1).is_some_and(|d| d > last1)).cloned().collect();
    if later.len() < 42 {
        skip(ctx, lc, Some(&*p), &format!("only {} phase 2 dates after phase 1", later.len()));
        return;
    }
    let slots: Vec<(usize, String)> = later[..42].to_vec();
    let group_ids: Vec<usize> = slots.iter().map(|x| x.0).collect();
    let mut kr: Vec<usize> = second.iter().copied().filter(|m| !group_ids.contains(m)).collect();
    kr.sort();
    if kr.len() != 3 {
        skip(ctx, lc, Some(&*p), &format!("{} matches left for 骑士之路 (want 3)", kr.len()));
        return;
    }
    let days: Vec<i64> = slots.iter().filter_map(|x| day_of(&x.1)).collect();
    let Some(order2) = fit_phase2(&a, &n, &days) else {
        skip(ctx, lc, Some(&*p), "no phase 2 order fits the dates");
        return;
    };
    // 骑士之路的日子：小组赛最后一天之后 2 天（两场）、4 天（一场），要在季后赛第一场之前
    let last2 = *days.last().unwrap_or(&last1);
    let playoffs = ids_at(ctx, LC, lc, "playoffs");
    let first_po = playoffs.iter().filter_map(|&m| date_of(ctx, m)).min().and_then(|d| day_of(&d));
    let Some(first_po) = first_po else {
        skip(ctx, lc, Some(&*p), "no playoff dates");
        return;
    };
    let (d1, d2) = if last2 + 4 < first_po {
        (last2 + 2, last2 + 4)
    } else if last2 + 2 < first_po {
        (last2 + 1, last2 + 2)
    } else {
        skip(ctx, lc, Some(&*p), "no room for 骑士之路 before the playoffs");
        return;
    };
    let (t_early, t_late) = {
        let mut ts: Vec<String> = slots.iter().rev().take(2).map(|x| time_part(&x.1)).collect();
        ts.sort();
        (ts.first().cloned().unwrap_or_else(|| "T17:00:00".into()), ts.last().cloned().unwrap_or_else(|| "T18:00:00".into()))
    };
    // 第一场就写不进去：游戏不认这种改法，这一届照原版打
    if !set_pair(ctx, group_ids[0], Slot::Normal(order2[0].0), Slot::Normal(order2[0].1)) {
        skip(ctx, lc, Some(&*p), "the game refused the first phase 2 pairing");
        return;
    }
    let mut ok = true;
    for (&m, &(x, y)) in group_ids.iter().zip(&order2).skip(1) {
        ok &= set_pair(ctx, m, Slot::Normal(x), Slot::Normal(y));
    }
    // 骑士之路：先按总排名占位（本包万一没赶上第二阶段结束，游戏也能照名次打），第二阶段结束时换成登峰 5/6、涅槃 1/2
    let kr3 = [kr[0], kr[1], kr[2]];
    ok &= set(ctx, kr3[0], "date", &format!("\"{}\"", at(d1, &t_early)));
    ok &= set(ctx, kr3[1], "date", &format!("\"{}\"", at(d1, &t_late)));
    ok &= set(ctx, kr3[2], "date", &format!("\"{}\"", at(d2, &t_early)));
    ok &= set_pair(ctx, kr3[0], Slot::Rank(lc, 5), Slot::Rank(lc, 6));
    ok &= set_pair(ctx, kr3[1], Slot::Rank(lc, 7), Slot::Rank(lc, 8));
    ok &= set_pair(ctx, kr3[2], Slot::Loser(kr3[0]), Slot::Winner(kr3[1]));
    for &m in &kr3 {
        ok &= set(ctx, m, "need_win", "3");
    }
    let seeds = rewire_playoffs(ctx, lc, None, kr3);
    wlog(format!(
        "LPL {lc} GROUPS: 登峰 {a:?} 涅槃 {n:?}; 42 phase 2 matches {:?}..; 骑士之路 {kr3:?} on {} / {}; playoff seeds 5/6 rewired {seeds}; all written {ok}",
        group_ids.first(),
        date_str(d1),
        date_str(d2)
    ));
    p.group = group_ids;
    p.kr = kr3.to_vec();
    p.a = a.clone();
    p.n = n.clone();
    p.phase = "p2".into();
    store(ctx, lc, p);
    let y = year_of(ctx, p);
    news(
        ctx,
        &format!("{y} LPL {}第二阶段分组", split_name(ctx, lc)),
        &format!(
            "第一阶段单循环结束，按排名分组：\n登峰组：{}。组内双循环 BO3，前四名直接进入季后赛胜者组，第五、六名进入骑士之路。\n\
             涅槃组：{}。组内双循环 BO3，前两名进入骑士之路，第三、四名参加升降级赛。\n组内排名按总战绩（第一阶段 + 第二阶段）。\n\
             骑士之路（BO5）：{}，登峰组第五对第六（胜者晋级季后赛）、涅槃组第一对第二（负者出局）；{}，前一场的负者对后一场的胜者，胜者晋级季后赛。",
            names(ctx, &a),
            names(ctx, &n),
            super::md(d1),
            super::md(d2)
        ),
    );
}

/// 季后赛里「常规赛第 r 名」的槽位换掉（1-4 名在 `a` 有了才换）；返回换了几个。
fn rewire_playoffs(ctx: &mut StableServerCtx<'_>, lc: usize, a: Option<&[usize]>, kr: [usize; 3]) -> usize {
    let mut n = 0;
    for m in ids_at(ctx, LC, lc, "playoffs") {
        if run_state(ctx, m) != Run::Wait {
            continue;
        }
        for side in ["team1", "team2"] {
            if let Slot::Rank(c, r) = slot(ctx, m, side) {
                if c != lc {
                    continue;
                }
                if let Some(json) = seed_for(r, a, kr).and_then(slot_json) {
                    if set(ctx, m, side, &json) {
                        n += 1;
                    }
                }
            }
        }
    }
    n
}

/// 第二阶段打完：骑士之路的对阵、季后赛 1-4 号种子、打升降级的两队。
fn to_knights(ctx: &mut StableServerCtx<'_>, lc: usize, p: &mut Progress) {
    let mut regular = p.first.clone();
    regular.extend(&p.group);
    let games: Vec<Game> = regular.iter().filter_map(|&m| game(ctx, m)).collect();
    let a = rank(&p.a, &games);
    let n = rank(&p.n, &games);
    if a.len() != 6 || n.len() != 4 || p.kr.len() != 3 {
        skip(ctx, lc, Some(&*p), "groups lost");
        return;
    }
    let kr = [p.kr[0], p.kr[1], p.kr[2]];
    // 骑士之路已经按占位的名次开打了（本包没赶上）：不改它，也不发对阵新闻
    let ready = all_wait(ctx, &kr);
    let ok = ready
        && set_pair(ctx, kr[0], Slot::Normal(a[4]), Slot::Normal(a[5]))
        && set_pair(ctx, kr[1], Slot::Normal(n[0]), Slot::Normal(n[1]));
    let seeds = rewire_playoffs(ctx, lc, Some(&a), kr);
    wlog(format!("LPL {lc} KNIGHTS: 登峰 {a:?} 涅槃 {n:?}; 骑士之路 not started {ready}, written {ok}; playoff slots rewired {seeds}"));
    p.a = a.clone();
    p.n = n.clone();
    p.rel = vec![n[2], n[3]];
    p.phase = "kr".into();
    store(ctx, lc, p);
    if !ok {
        return;
    }
    let y = year_of(ctx, p);
    let day = |m: usize| date_of(ctx, m).and_then(|d| day_of(&d)).map(super::md).unwrap_or_default();
    news(
        ctx,
        &format!("{y} LPL {}骑士之路对阵", split_name(ctx, lc)),
        &format!(
            "第二阶段结束。\n直接进入季后赛胜者组：{}。\n骑士之路（BO5）：{} {} 对 {}（胜者晋级季后赛），{} 对 {}（负者出局）；{} 由前一场的负者对后一场的胜者，胜者晋级季后赛。\n\
             涅槃组第三、四名 {} 参加升降级赛。",
            names(ctx, &a[..4]),
            day(kr[0]),
            team_name(ctx, a[4]),
            team_name(ctx, a[5]),
            team_name(ctx, n[0]),
            team_name(ctx, n[1]),
            day(kr[2]),
            names(ctx, &n[2..])
        ),
    );
}

/// 升降级赛建好以后：LPL 这边的两队要是不是涅槃组第 3、4 名，换过来。
fn promotion(ctx: &mut StableServerCtx<'_>, lc: usize, p: &mut Progress) {
    let promo = ids_at(ctx, LC, lc, "promotion_series");
    if promo.is_empty() {
        return;
    }
    if !all_wait(ctx, &promo) {
        p.promo_done = true;
        store(ctx, lc, p);
        return;
    }
    // 每场 LPL 这边是哪一侧、现在是谁
    let mut sides: Vec<(usize, &'static str, usize)> = Vec::new();
    for &m in &promo {
        for side in ["team1", "team2"] {
            match slot(ctx, m, side) {
                Slot::Normal(t) if p.teams.contains(&t) => sides.push((m, side, t)),
                Slot::Rank(c, r) if c == lc => sides.push((m, side, usize::MAX - r)),
                _ => {}
            }
        }
    }
    let now: Vec<usize> = sides.iter().map(|x| x.2).collect();
    let want = [p.rel[0], p.rel[1]];
    let swaps = promo_swaps(&now, want);
    let mut changed = Vec::new();
    for ((m, side, old), new) in sides.iter().zip(&swaps) {
        if let Some(t) = new {
            if set(ctx, *m, side, &format!("{{\"Normal\":{t}}}")) {
                changed.push((*old, *t));
            }
        }
    }
    wlog(format!("LPL {lc} PROMOTION: matches {promo:?}, LPL side now {now:?}, want {want:?}, changed {changed:?}"));
    p.promo_done = true;
    store(ctx, lc, p);
    if !changed.is_empty() {
        let y = year_of(ctx, p);
        let old: Vec<usize> = changed.iter().map(|x| x.0).filter(|&t| t < usize::MAX / 2).collect();
        news(
            ctx,
            &format!("{y} LPL 升降级赛对阵调整"),
            &format!(
                "按 LPL 赛制，涅槃组第三、四名 {} 参加升降级赛{}。",
                names(ctx, &want),
                if old.is_empty() { String::new() } else { format!("（原定 {}）", names(ctx, &old)) }
            ),
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn days_2_per_day(n: usize, from: i64) -> Vec<i64> {
        (0..n).map(|i| from + (i / 2) as i64).collect()
    }

    #[test]
    fn single_round_robin_meets_everyone_once() {
        let teams: Vec<usize> = (10..20).collect();
        let rr = round_robin(&teams);
        assert_eq!(rr.len(), 9);
        assert!(rr.iter().all(|r| r.len() == 5));
        let pairs: Vec<(usize, usize)> = rr.iter().flatten().copied().collect();
        assert!(is_single_rr(&teams, &pairs));
        // 每轮每队一场
        for r in &rr {
            let mut seen = BTreeSet::new();
            assert!(r.iter().all(|&(a, b)| seen.insert(a) && seen.insert(b)));
        }
        // 主场 4 或 5 场
        let home = |t: usize| pairs.iter().filter(|p| p.0 == t).count();
        assert!(teams.iter().all(|&t| (4..=5).contains(&home(t))), "{:?}", teams.iter().map(|&t| home(t)).collect::<Vec<_>>());
        // 双循环：每队主客各一半
        let dbl: Vec<(usize, usize)> = double_round_robin(&teams).into_iter().flatten().collect();
        assert!(teams.iter().all(|&t| dbl.iter().filter(|p| p.0 == t).count() == 9));
        assert!(!is_single_rr(&teams, &pairs[1..]));
    }

    #[test]
    fn the_rounds_fit_two_a_day_without_a_team_twice() {
        let teams: Vec<usize> = (10..20).collect();
        let days = days_2_per_day(45, 100);
        let order = fit(&round_robin(&teams), &days).unwrap();
        assert_eq!(order.len(), 45);
        for d in 100..123 {
            let today: Vec<&(usize, usize)> = order.iter().zip(&days).filter(|(_, &x)| x == d).map(|(m, _)| m).collect();
            let mut seen = BTreeSet::new();
            assert!(today.iter().all(|&&(a, b)| seen.insert(a) && seen.insert(b)), "day {d}");
        }
        assert!(is_single_rr(&teams, &order));
    }

    #[test]
    fn phase_two_is_two_double_round_robins() {
        let a = [1, 2, 3, 4, 5, 6];
        let n = [7, 8, 9, 10];
        // 排进 42 个时间槽（一天两场）
        let days = days_2_per_day(42, 200);
        let all = fit_phase2(&a, &n, &days).unwrap();
        assert_eq!(all.len(), 42);
        let count = |x: usize, y: usize| all.iter().filter(|p| (p.0, p.1) == (x, y) || (p.0, p.1) == (y, x)).count();
        for i in 0..6 {
            for j in i + 1..6 {
                assert_eq!(count(a[i], a[j]), 2);
            }
        }
        for i in 0..4 {
            for j in i + 1..4 {
                assert_eq!(count(n[i], n[j]), 2);
            }
            for &x in &a {
                assert_eq!(count(n[i], x), 0, "groups do not meet");
            }
        }
        // 同一天没有队打两场
        for d in 200..221 {
            let today: Vec<&(usize, usize)> = all.iter().zip(&days).filter(|(_, &x)| x == d).map(|(m, _)| m).collect();
            let mut seen = BTreeSet::new();
            assert!(today.iter().all(|&&(x, y)| seen.insert(x) && seen.insert(y)), "day {d}");
        }
        // 涅槃组铺满整个第二阶段，不是一口气打完：前一半、后一半都有，最后一场在最后几天
        let nir: Vec<usize> = all.iter().enumerate().filter(|(_, m)| n.contains(&m.0)).map(|(i, _)| i).collect();
        assert_eq!(nir.len(), 12);
        assert!(nir.iter().filter(|&&i| i < 21).count() >= 4 && nir.iter().filter(|&&i| i >= 21).count() >= 4, "{nir:?}");
        assert!(*nir.last().unwrap() >= 34, "{nir:?}");
        // 每组自己的主客各一半
        for &t in a.iter().chain(&n) {
            let home = all.iter().filter(|p| p.0 == t).count();
            let away = all.iter().filter(|p| p.1 == t).count();
            assert_eq!(home, away, "team {t}");
        }
    }

    #[test]
    fn ranking_uses_wins_then_maps_then_head_to_head() {
        let g = |a, b, w, sa, sb| Game { a, b, winner: w, sa, sb };
        // 1、2 都 2 胜，1 小分差 +3、2 是 0；3、4 都 1 胜，4 小分差 -1、3 是 -2
        let games = vec![g(1, 2, 2, 1, 2), g(1, 3, 1, 2, 0), g(1, 4, 1, 2, 0), g(2, 3, 2, 2, 1), g(2, 4, 4, 0, 2), g(3, 4, 3, 2, 1)];
        assert_eq!(rank(&[1, 2, 3, 4], &games), vec![1, 2, 4, 3]);
        // 胜场、小分全一样、相互之间也一样：按编号
        let games = vec![g(5, 6, 6, 1, 2), g(5, 7, 5, 2, 1), g(6, 7, 7, 1, 2)];
        assert_eq!(rank(&[7, 6, 5], &games), vec![5, 6, 7]);
        // 胜场、小分一样的两队，相互之间赢的在前
        let games = vec![g(8, 9, 9, 1, 2), g(8, 10, 8, 2, 1), g(9, 10, 10, 1, 2), g(8, 11, 8, 2, 0), g(9, 11, 9, 2, 0)];
        let t = table(&[8, 9], &games);
        assert_eq!(t[&8], t[&9]);
        assert_eq!(rank(&[8, 9], &games), vec![9, 8]);
    }

    #[test]
    fn slots_read_and_write_like_the_game() {
        assert_eq!(slot_of("{\"Normal\": 31}"), Slot::Normal(31));
        assert_eq!(slot_of(r#"{"CompetitionRank":[73,4]}"#), Slot::Rank(73, 4));
        assert_eq!(slot_of(r#"{"WinnerOf":8181}"#), Slot::Winner(8181));
        assert_eq!(slot_of(r#"{"LoserOf":8177}"#), Slot::Loser(8177));
        assert_eq!(slot_of(r#"{"GroupRank":[1,2,3]}"#), Slot::Other);
        for s in [Slot::Normal(5), Slot::Rank(73, 6), Slot::Winner(9), Slot::Loser(10)] {
            assert_eq!(slot_of(&slot_json(s).unwrap()), s);
        }
        assert_eq!(end_of(r#"{"End": {"loser": 13, "team1_score": 2, "team2_score": 1, "winner": 73}}"#), Some((73, 2, 1)));
        assert_eq!(end_of("\"Wait\""), None);
    }

    #[test]
    fn playoff_seeds_come_from_the_groups_and_the_knights() {
        let a = [11, 12, 13, 14, 15, 16];
        let kr = [901, 902, 903];
        assert_eq!(seed_for(1, Some(&a), kr), Some(Slot::Normal(11)));
        assert_eq!(seed_for(4, Some(&a), kr), Some(Slot::Normal(14)));
        assert_eq!(seed_for(2, None, kr), None);
        assert_eq!(seed_for(5, None, kr), Some(Slot::Winner(901)));
        assert_eq!(seed_for(6, None, kr), Some(Slot::Winner(903)));
        assert_eq!(seed_for(7, Some(&a), kr), None);
    }

    #[test]
    fn promotion_takes_nirvana_three_and_four() {
        assert_eq!(promo_swaps(&[7, 8], [7, 8]), vec![None, None]);
        assert_eq!(promo_swaps(&[7, 5], [7, 8]), vec![None, Some(8)]);
        assert_eq!(promo_swaps(&[1, 2], [7, 8]), vec![Some(7), Some(8)]);
        assert_eq!(promo_swaps(&[8, 3], [7, 8]), vec![None, Some(7)]);
    }

    #[test]
    fn progress_round_trips() {
        let p = Progress {
            phase: "p2".into(),
            teams: (10..20).collect(),
            first: vec![1, 2, 3],
            group: vec![4, 5],
            kr: vec![6, 7, 8],
            a: vec![10, 11, 12, 13, 14, 15],
            n: vec![16, 17, 18, 19],
            rel: vec![],
            promo_done: false,
            why: "a;b=c".into(),
            early: vec![(77, "2029-03-03T18:00:00".into(), 12, 15)],
        };
        let back = Progress::from_text(&p.to_text()).unwrap();
        assert_eq!(back.why, "a b c");
        assert_eq!(back.early, vec![(77, "2029-03-03T18:00:00".to_string(), 12, 15)]);
        assert_eq!(Progress { why: "a b c".into(), ..p }, back);
        // 0.2.0 早先的写法（没有 early）也读得进来
        assert!(Progress::from_text("phase=p1;teams=1,2;first=;group=;kr=;a=;n=;rel=;promo=0;why=").unwrap().early.is_empty());
    }

    #[test]
    fn several_matches_a_day_still_fit() {
        let teams: Vec<usize> = (10..20).collect();
        let a: Vec<usize> = (1..7).collect();
        let n: Vec<usize> = (7..11).collect();
        for per_day in 1..=5usize {
            let days = |k: usize| (0..k).map(|i| 300 + (i / per_day) as i64).collect::<Vec<i64>>();
            let check = |order: &[(usize, usize)], d: &[i64]| {
                for day in d.iter().copied().collect::<BTreeSet<i64>>() {
                    let mut seen = BTreeSet::new();
                    for (m, _) in order.iter().zip(d).filter(|(_, &x)| x == day) {
                        assert!(seen.insert(m.0) && seen.insert(m.1), "{per_day} a day: a team twice on day {day}");
                    }
                }
            };
            let d45 = days(45);
            let o1 = fit(&round_robin(&teams), &d45).unwrap_or_else(|| panic!("phase 1 at {per_day} a day"));
            assert!(is_single_rr(&teams, &o1));
            check(&o1, &d45);
            let d42 = days(42);
            // 一天 5 场排不下第二阶段（登峰组每队 10 场，42 场只有 9 天）：返回 None，这一届开赛季时就不做
            if per_day == 5 {
                assert!(fit_phase2(&a, &n, &d42).is_none());
                continue;
            }
            let o2 = fit_phase2(&a, &n, &d42).unwrap_or_else(|| panic!("phase 2 at {per_day} a day"));
            assert_eq!(o2.len(), 42);
            check(&o2, &d42);
        }
    }
}
