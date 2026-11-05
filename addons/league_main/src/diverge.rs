//! 对局校验和（0.9.12）：屏幕上的比赛和服务器为它预演的两份模拟该一模一样，可 2026-11-05 的日志里（league_aatrox_chain.log
//! m=2636 s=4、league_yasuo_wall.log m=2636 s=5）三份走到一半就分道扬镳——链子拴的人、风墙的位置、单位 id 都不同，游戏自己
//! 的 log.log 也写 `server/live simulation diverged`（19 局 19 局都是，5 局胜负翻了）。哪个 tick 开始、谁先不一样，以前的日志
//! 看不出来：各附加包只在自己的事件上写一行，预演那边还限了量。
//!
//! 这里用比赛钩子（`StableMatchHook`，一个模块只能设一个；league.dll 以前没有）每 `EVERY` 个 tick 给每份模拟拍一张快照：
//! 所有活着的单位（id、种类、阵营、位置、血量、buff 名——附加包按模拟编号挂的 `xxx_sim:N` buff 除外，它们本来就每份不同）
//! 按 id 排好算一个 FNV-1a 64 位哈希，再记每个英雄的 `名字#id 血/满血 (x,y) b<buff 数>`。快照按（比赛、种类、小局、线程）归到
//! 一次「run」里（tick 倒回去就是新的一次：预演的两份 s=- 一样，靶同一条线程跑就靠这个分开），同一场比赛里别的 run 到了同一个
//! tick 就对一对：哈希相同记「一致到这个 tick」，不同就写一行 DIVERGE——第一个不一样的英雄、两边的单位数、两边的英雄汇总——每对
//! run 只写第一次；钩子给的每 tick 随机种子 `rng` 只记录、只在状态一致而它不同时说一次（RNG 行），不算分道扬镳。局终
//! （`is_end`）再写一行 END 汇总每对的结果。
//!
//! 日志（league.log）：
//! - `SYNC [view m=2636 s=4 run 3 thr 17] t=600 rng=… n=137 h=… | aatrox#18 1000/1000 (189901,96150) b2; …`
//!   每 `EVERY` tick 一行（英雄汇总只在 t=0 和每 `SUMMARY_EVERY` tick 带）；`n` 活着的单位数，`h` 哈希。
//! - `DIVERGE [view … run 3] vs [presim … run 1] first seen at tick 6000 (agreed at 5400): fiora#23 hp 812 vs 790, pos … | n … | view: … | presim: …`
//! - `END [view … run 3] t=48000 n=… blue score diff=+5: vs presim run 1 agreed through 5400, diverged at 6000; vs …`
//! 开销：每 600 tick 把一两百个单位读一遍、拼几百字节——可以忽略。

use std::collections::{HashMap, VecDeque};
use std::sync::Mutex;

use mod_api_stable::*;

use crate::wlog;

/// Ticks between snapshots.
pub const EVERY: usize = 600;
/// Ticks between snapshots that also log the per-champion summary.
pub const SUMMARY_EVERY: usize = 3000;
/// Snapshots kept per run (128 x 600 ticks = 76 800 ticks: a whole set, so the view's second run of a set - the game
/// runs the view once fast and once at watching speed, lol_audio's "first run" - still finds the presims' early ticks).
pub const KEEP: usize = 128;
/// Matches remembered; the oldest goes when a new one starts.
const MAX_MATCHES: usize = 3;
/// Runs remembered per match (2 presims + a view or two per set, across a series).
const MAX_RUNS: usize = 48;

/// One entity's row in the hash.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Row {
    pub id: usize,
    pub kind: u32,
    pub team: usize,
    pub pos: (u64, u64),
    pub hp: usize,
    pub buffs: Vec<String>,
}

/// One champion's line in the summary.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Champ {
    pub id: usize,
    pub name: String,
    pub team: usize,
    pub hp: usize,
    pub max: usize,
    pub pos: (u64, u64),
    pub buffs: usize,
}

#[derive(Clone, Debug)]
pub struct Snapshot {
    pub tick: usize,
    pub hash: u64,
    pub rng: u64,
    pub count: usize,
    pub champs: Vec<Champ>,
}

/// Which simulation a snapshot comes from.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Origin {
    pub kind: u32,
    pub match_id: u64,
    pub set: u64,
    pub seed: u64,
    pub thread: u64,
}

/// A buff the add-ons hang on a champion to number its simulation (`league_azir_sim:17`, `league_drmundo_sim:3` ...):
/// different in every simulation by design, so never part of the hash.
pub fn is_sim_tag(buff: &str) -> bool {
    buff.contains("_sim:")
}

/// FNV-1a 64 over every row in id order: stable across builds and platforms, unlike `DefaultHasher`.
pub fn hash_rows(rows: &mut Vec<Row>) -> u64 {
    rows.sort_by_key(|r| r.id);
    let mut h: u64 = 0xcbf2_9ce4_8422_2325;
    let mut feed = |bytes: &[u8]| {
        for b in bytes {
            h ^= *b as u64;
            h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
        h ^= 0xff;
        h = h.wrapping_mul(0x0000_0100_0000_01b3);
    };
    for r in rows.iter() {
        feed(&r.id.to_le_bytes());
        feed(&r.kind.to_le_bytes());
        feed(&r.team.to_le_bytes());
        feed(&r.pos.0.to_le_bytes());
        feed(&r.pos.1.to_le_bytes());
        feed(&r.hp.to_le_bytes());
        for b in &r.buffs {
            if !is_sim_tag(b) {
                feed(b.as_bytes());
            }
        }
    }
    h
}

fn short(name: &str) -> &str {
    name.strip_prefix("league_").unwrap_or(name)
}

/// `aatrox#18 1000/1000 (189901,96150) b2; fiora#23 ...` in id order.
pub fn summary(champs: &[Champ]) -> String {
    let mut parts: Vec<String> = champs.iter().map(|c| format!("{}#{} {}/{} ({},{}) b{}",
        short(&c.name), c.id, c.hp, c.max, c.pos.0, c.pos.1, c.buffs)).collect();
    if parts.is_empty() {
        parts.push("no champions".into());
    }
    parts.join("; ")
}

/// The first champion (lowest id) whose row differs between two summaries, as a short phrase; `None` when equal.
pub fn first_difference(a: &[Champ], b: &[Champ]) -> Option<String> {
    let mut ids: Vec<usize> = a.iter().chain(b.iter()).map(|c| c.id).collect();
    ids.sort_unstable();
    ids.dedup();
    for id in ids {
        let x = a.iter().find(|c| c.id == id);
        let y = b.iter().find(|c| c.id == id);
        match (x, y) {
            (Some(x), None) => return Some(format!("{}#{} only on the first side", short(&x.name), id)),
            (None, Some(y)) => return Some(format!("{}#{} only on the second side", short(&y.name), id)),
            (Some(x), Some(y)) if x != y => {
                let mut what = Vec::new();
                if x.name != y.name {
                    what.push(format!("name {} vs {}", short(&x.name), short(&y.name)));
                }
                if x.team != y.team {
                    what.push(format!("team {} vs {}", x.team, y.team));
                }
                if (x.hp, x.max) != (y.hp, y.max) {
                    what.push(format!("hp {}/{} vs {}/{}", x.hp, x.max, y.hp, y.max));
                }
                if x.pos != y.pos {
                    what.push(format!("pos ({},{}) vs ({},{})", x.pos.0, x.pos.1, y.pos.0, y.pos.1));
                }
                if x.buffs != y.buffs {
                    what.push(format!("buffs {} vs {}", x.buffs, y.buffs));
                }
                return Some(format!("{}#{} {}", short(&x.name), id, what.join(", ")));
            }
            _ => {}
        }
    }
    None
}

pub fn kind_name(kind: u32) -> &'static str {
    match SimOriginKindV1::from_code(kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    }
}

fn none_dash(v: u64) -> String {
    if v == SimOriginV1::NONE { "-".into() } else { v.to_string() }
}

/// How one pair of runs of the same match compares so far.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Pair {
    pub agreed: Option<usize>,
    pub diverged: Option<usize>,
    /// The hook's per-tick rng seed differed while the state agreed: said once per pair, never a divergence by itself
    /// (if the host draws that seed per run, every pair would differ on it).
    pub rng_noted: bool,
}

struct Run {
    origin: Origin,
    no: u32,
    snaps: VecDeque<Snapshot>,
    last_tick: usize,
    ended: bool,
    /// By the other run's number.
    pairs: HashMap<u32, Pair>,
}

impl Run {
    fn head(&self) -> String {
        format!("[{} m={} s={} run {} thr {}]", kind_name(self.origin.kind), none_dash(self.origin.match_id),
            none_dash(self.origin.set), self.no, self.origin.thread)
    }

    fn label(&self) -> String {
        format!("{} run {}", kind_name(self.origin.kind), self.no)
    }

    fn at(&self, tick: usize) -> Option<&Snapshot> {
        self.snaps.iter().find(|s| s.tick == tick)
    }
}

struct Match {
    match_id: u64,
    runs: Vec<Run>,
    next_no: u32,
}

/// Every match's runs; the lines to log come back from `record`, so the store itself never touches the log (tests).
#[derive(Default)]
pub struct Store {
    matches: Vec<Match>,
}

impl Store {
    /// Files one snapshot and returns the lines to log (the SYNC line, any DIVERGE lines).
    pub fn record(&mut self, origin: Origin, snap: Snapshot, with_summary: bool) -> Vec<String> {
        let mut out = Vec::new();
        let mi = match self.matches.iter().position(|m| m.match_id == origin.match_id) {
            Some(i) => i,
            None => {
                while self.matches.len() >= MAX_MATCHES {
                    self.matches.remove(0);
                }
                self.matches.push(Match { match_id: origin.match_id, runs: Vec::new(), next_no: 1 });
                self.matches.len() - 1
            }
        };
        let m = &mut self.matches[mi];
        // the run: the latest one of this kind / set / seed / thread, if its ticks are still going up; otherwise a new one
        // (a set the view runs again starts at tick 0; two presims on one thread would land here too - then the presim
        // run numbers climb past 2 in one set and the snapshots of the two get mixed: tell by the `thr` numbers)
        let latest = m.runs.iter().rposition(|r| r.origin == origin);
        let ri = match latest.filter(|&i| m.runs[i].last_tick < snap.tick && !m.runs[i].ended) {
            Some(i) => i,
            None => {
                while m.runs.len() >= MAX_RUNS {
                    m.runs.remove(0);
                }
                let no = m.next_no;
                m.next_no += 1;
                m.runs.push(Run { origin, no, snaps: VecDeque::new(), last_tick: 0, ended: false, pairs: HashMap::new() });
                m.runs.len() - 1
            }
        };
        let tick = snap.tick;
        {
            let run = &mut m.runs[ri];
            run.last_tick = tick;
            let mut line = format!("SYNC {} t={} rng={:016x} n={} h={:016x}", run.head(), tick, snap.rng, snap.count, snap.hash);
            if with_summary {
                line.push_str(" | ");
                line.push_str(&summary(&snap.champs));
            }
            out.push(line);
            run.snaps.push_back(snap);
            while run.snaps.len() > KEEP {
                run.snaps.pop_front();
            }
        }
        // compare with every other run of the match that has this tick
        let mine_no = m.runs[ri].no;
        let others: Vec<usize> = (0..m.runs.len()).filter(|&i| i != ri && m.runs[i].at(tick).is_some()).collect();
        for oi in others {
            let other_no = m.runs[oi].no;
            let already = m.runs[ri].pairs.get(&other_no).copied().unwrap_or_default();
            if already.diverged.is_some() {
                continue;
            }
            let (a, b) = (m.runs[ri].at(tick).cloned(), m.runs[oi].at(tick).cloned());
            let (Some(a), Some(b)) = (a, b) else { continue };
            let same = a.hash == b.hash && a.count == b.count;
            let mut rng_noted = already.rng_noted;
            if same && a.rng != b.rng && !rng_noted {
                rng_noted = true;
                out.push(format!("RNG {} vs {} the hook's rng seed differs at tick {tick} ({:016x} vs {:016x}) while the state agrees",
                    m.runs[ri].head(), m.runs[oi].head(), a.rng, b.rng));
            }
            let pair = if same {
                Pair { agreed: Some(tick), diverged: None, rng_noted }
            } else {
                let what = first_difference(&a.champs, &b.champs)
                    .unwrap_or_else(|| "no champion differs (a minion / monster / buff does)".into());
                let agreed = already.agreed.map_or("never agreed".to_string(), |t| format!("agreed at {t}"));
                out.push(format!(
                    "DIVERGE {} vs {} first seen at tick {tick} ({agreed}): {what} | n {} vs {}, rng {} | {}: {} | {}: {}",
                    m.runs[ri].head(), m.runs[oi].head(), a.count, b.count,
                    if a.rng == b.rng { "same" } else { "differs" },
                    m.runs[ri].label(), summary(&a.champs), m.runs[oi].label(), summary(&b.champs)));
                Pair { agreed: already.agreed, diverged: Some(tick), rng_noted }
            };
            m.runs[ri].pairs.insert(other_no, pair);
            m.runs[oi].pairs.insert(mine_no, pair);
        }
        out
    }

    /// Marks the run ended and returns its END line (once).
    pub fn end(&mut self, origin: Origin, tick: usize, count: usize, blue_diff: i32) -> Option<String> {
        let m = self.matches.iter_mut().find(|m| m.match_id == origin.match_id)?;
        let labels: Vec<(u32, String)> = m.runs.iter().map(|r| (r.no, r.label())).collect();
        let run = m.runs.iter_mut().filter(|r| r.origin == origin && !r.ended).max_by_key(|r| r.last_tick)?;
        run.ended = true;
        let mut pairs: Vec<(&u32, &Pair)> = run.pairs.iter().collect();
        pairs.sort_by_key(|(no, _)| **no);
        let verdicts: Vec<String> = pairs.iter().map(|(no, p)| {
            let name = labels.iter().find(|(n, _)| n == *no).map_or_else(|| format!("run {no}"), |(_, l)| l.clone());
            match (p.agreed, p.diverged) {
                (Some(a), Some(d)) => format!("vs {name} agreed through {a}, diverged at {d}"),
                (None, Some(d)) => format!("vs {name} diverged from the first snapshot ({d})"),
                (Some(a), None) => format!("vs {name} agreed through {a}"),
                (None, None) => format!("vs {name} never at the same tick"),
            }
        }).collect();
        let verdict = if verdicts.is_empty() { "no other run of this match reached the same ticks".to_string() }
            else { verdicts.join("; ") };
        Some(format!("END {} t={tick} n={count} blue score diff={blue_diff:+}: {verdict}", run.head()))
    }

    /// The pair record between two runs of a match (tests).
    pub fn pair(&self, match_id: u64, a: u32, b: u32) -> Option<Pair> {
        let m = self.matches.iter().find(|m| m.match_id == match_id)?;
        m.runs.iter().find(|r| r.no == a)?.pairs.get(&b).copied()
    }
}

static STORE: Mutex<Store> = Mutex::new(Store { matches: Vec::new() });
static NO_ORIGIN: Mutex<bool> = Mutex::new(false);

fn thread_no() -> u64 {
    // ThreadId's Debug is `ThreadId(17)`; the number is all we show
    let s = format!("{:?}", std::thread::current().id());
    s.trim_start_matches(|c: char| !c.is_ascii_digit()).trim_end_matches(|c: char| !c.is_ascii_digit()).parse().unwrap_or(0)
}

/// Reads every living entity of the simulation into rows and the champions into the summary.
fn snapshot(sim: &StableSim<'_>, rng: u64) -> Snapshot {
    let tick = sim.tick();
    let mut rows = Vec::new();
    let mut champs = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if !e.is_alive() {
            continue;
        }
        let id = e.id();
        if id == usize::MAX {
            continue;
        }
        let (hp, max) = e.hp();
        let pos = e.pos();
        let team = e.team();
        let kind = e.kind().map_or(u32::MAX, |k| k.code());
        let n = e.buff_count();
        let mut buffs = Vec::with_capacity(n);
        for b in 0..n {
            if let Some(buff) = e.buff_at(b) {
                buffs.push(buff.name().to_string());
            }
        }
        if e.is_champion() {
            champs.push(Champ { id, name: e.name().unwrap_or_default(), team, hp, max, pos, buffs: buffs.len() });
        }
        rows.push(Row { id, kind, team, pos, hp, buffs });
    }
    champs.sort_by_key(|c| c.id);
    let count = rows.len();
    let hash = hash_rows(&mut rows);
    Snapshot { tick, hash, rng, count, champs }
}

/// The match hook: a snapshot every `EVERY` ticks (and on the first tick), compared with the other runs of the match.
pub struct Diverge;

impl StableMatchHook for Diverge {
    fn on_match_tick(&self, sim: &mut StableSim<'_>, rng_seed: u64) {
        let Some(o) = sim.sim_origin() else {
            let mut said = NO_ORIGIN.lock().unwrap_or_else(|e| e.into_inner());
            if !*said {
                *said = true;
                wlog("SYNC off: the host gives no sim_origin (ABI level < 6)");
            }
            return;
        };
        let tick = sim.tick();
        let origin = Origin { kind: o.kind, match_id: o.match_id, set: o.set_index, seed: sim.seed(), thread: thread_no() };
        if o.match_id == SimOriginV1::NONE {
            // a tool / warm-up simulation with no match: one line when it starts, nothing to compare it with
            if tick <= 1 {
                let s = snapshot(sim, rng_seed);
                wlog(format!("SYNC [{} m=- s={} thr {}] t={tick} rng={:016x} n={} h={:016x} (no match: not compared) | {}",
                    kind_name(o.kind), none_dash(o.set_index), origin.thread, s.rng, s.count, s.hash, summary(&s.champs)));
            }
            return;
        }
        let ended = sim.is_end();
        if tick % EVERY == 0 || tick <= 1 || ended {
            // the first tick and every EVERY ticks; the end tick too, so the END line has a snapshot behind it
            let s = snapshot(sim, rng_seed);
            let count = s.count;
            let with_summary = tick <= 1 || tick % SUMMARY_EVERY == 0;
            let lines = {
                let mut store = STORE.lock().unwrap_or_else(|e| e.into_inner());
                let mut lines = if tick % EVERY == 0 || tick <= 1 { store.record(origin, s, with_summary) } else { Vec::new() };
                if ended {
                    if let Some(end) = store.end(origin, tick, count, sim.score_diff(0)) {
                        lines.push(end);
                    }
                }
                lines
            };
            for line in lines {
                wlog(line);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn row(id: usize, hp: usize, buffs: &[&str]) -> Row {
        Row { id, kind: 0, team: id % 2, pos: (1000 * id as u64, 7), hp, buffs: buffs.iter().map(|s| s.to_string()).collect() }
    }

    fn champ(id: usize, hp: usize) -> Champ {
        Champ { id, name: format!("league_c{id}"), team: id % 2, hp, max: 1000, pos: (1000 * id as u64, 7), buffs: 1 }
    }

    fn snap(tick: usize, hp18: usize, rng: u64) -> Snapshot {
        let mut rows = vec![row(18, hp18, &["a"]), row(23, 500, &[])];
        Snapshot { tick, hash: hash_rows(&mut rows), rng, count: 2, champs: vec![champ(18, hp18), champ(23, 500)] }
    }

    const PRESIM: u32 = 1;
    const VIEW: u32 = 2;

    fn origin(kind: u32, set: u64, thread: u64) -> Origin {
        Origin { kind, match_id: 2636, set, seed: 99, thread }
    }

    #[test]
    fn hash_ignores_order_and_sim_tags_but_not_state() {
        let mut a = vec![row(18, 900, &["x", "league_azir_sim:17"]), row(23, 500, &[])];
        let mut b = vec![row(23, 500, &[]), row(18, 900, &["x", "league_azir_sim:18"])];
        assert_eq!(hash_rows(&mut a), hash_rows(&mut b));
        let mut c = vec![row(18, 901, &["x"]), row(23, 500, &[])];
        assert_ne!(hash_rows(&mut a), hash_rows(&mut c));
        let mut d = vec![row(18, 900, &["y"]), row(23, 500, &[])];
        assert_ne!(hash_rows(&mut a), hash_rows(&mut d));
        let mut e = vec![row(18, 900, &["x"])];
        assert_ne!(hash_rows(&mut a), hash_rows(&mut e));
    }

    #[test]
    fn first_difference_names_the_lowest_id_that_differs() {
        let a = vec![champ(18, 900), champ(23, 500), champ(25, 700)];
        let mut b = a.clone();
        assert_eq!(first_difference(&a, &b), None);
        b[2].hp = 650;
        b[1].pos = (0, 0);
        let what = first_difference(&a, &b).unwrap();
        assert!(what.starts_with("c23#23 pos (23000,7) vs (0,0)"), "{what}");
        let c = vec![champ(18, 900), champ(25, 700)];
        assert_eq!(first_difference(&a, &c).unwrap(), "c23#23 only on the first side");
        assert_eq!(first_difference(&c, &a).unwrap(), "c23#23 only on the second side");
    }

    #[test]
    fn twins_and_view_compare_and_diverge_once() {
        let mut store = Store::default();
        let p1 = origin(PRESIM, SimOriginV1::NONE, 7);
        let p2 = origin(PRESIM, SimOriginV1::NONE, 8);
        let v = origin(VIEW, 4, 1);
        // tick 0: all three agree
        for o in [p1, p2, v] {
            let lines = store.record(o, snap(0, 1000, 5), true);
            assert_eq!(lines.iter().filter(|l| l.starts_with("DIVERGE")).count(), 0, "{lines:?}");
            assert!(lines[0].starts_with("SYNC "), "{lines:?}");
            assert!(lines[0].contains("c18#18 1000/1000"), "{lines:?}");
        }
        assert_eq!(store.pair(2636, 3, 1), Some(Pair { agreed: Some(0), diverged: None, rng_noted: false }));
        // tick 600: twins agree, the view differs (hp of #18)
        store.record(p1, snap(600, 900, 6), false);
        let lines = store.record(p2, snap(600, 900, 6), false);
        assert_eq!(lines.len(), 1, "{lines:?}");
        let lines = store.record(v, snap(600, 880, 6), false);
        let div: Vec<&String> = lines.iter().filter(|l| l.starts_with("DIVERGE")).collect();
        assert_eq!(div.len(), 2, "{lines:?}");
        assert!(div[0].contains("first seen at tick 600 (agreed at 0): c18#18 hp 880/1000 vs 900/1000"), "{}", div[0]);
        assert!(div[0].contains("rng same"), "{}", div[0]);
        assert_eq!(store.pair(2636, 3, 1), Some(Pair { agreed: Some(0), diverged: Some(600), rng_noted: false }));
        assert_eq!(store.pair(2636, 1, 2), Some(Pair { agreed: Some(600), diverged: None, rng_noted: false }));
        // tick 1200: no second DIVERGE line for the same pair
        store.record(p1, snap(1200, 800, 7), false);
        let lines = store.record(v, snap(1200, 700, 7), false);
        assert_eq!(lines.len(), 1, "{lines:?}");
        // the end line sums it up
        let end = store.end(v, 1300, 2, 3).unwrap();
        assert!(end.contains("vs presim run 1 agreed through 0, diverged at 600"), "{end}");
        assert!(end.contains("blue score diff=+3"), "{end}");
        assert!(store.end(v, 1301, 2, 3).is_none(), "END once");
    }

    #[test]
    fn a_tick_going_back_starts_a_new_run_and_a_different_rng_is_noted_once() {
        let mut store = Store::default();
        let v = origin(VIEW, 5, 1);
        store.record(v, snap(0, 1000, 5), true);
        store.record(v, snap(600, 900, 6), false);
        // the view runs the set again (the same thread): a new run, compared with the first
        let lines = store.record(v, snap(0, 1000, 5), true);
        assert!(lines[0].contains("run 2"), "{lines:?}");
        assert_eq!(store.pair(2636, 2, 1), Some(Pair { agreed: Some(0), diverged: None, rng_noted: false }));
        let lines = store.record(v, snap(600, 900, 66), false);
        assert_eq!(lines.len(), 2, "{lines:?}");
        assert!(lines[1].starts_with("RNG ") && lines[1].contains("while the state agrees"), "{lines:?}");
        assert_eq!(store.pair(2636, 2, 1), Some(Pair { agreed: Some(600), diverged: None, rng_noted: true }));
        let lines = store.record(v, snap(1200, 800, 67), false);
        assert_eq!(lines.len(), 1, "said once: {lines:?}");
        // run 1 stopped at 600: a later tick still goes to the latest run (2), never back into the stale one
        let lines = store.record(v, snap(1800, 700, 68), false);
        assert_eq!(lines.len(), 1, "{lines:?}");
        assert!(lines[0].contains("run 2"), "{lines:?}");
        let lines = store.record(v, snap(1800, 700, 68), false); // tick not going up: a third run
        assert!(lines[0].contains("run 3"), "{lines:?}");
    }

    #[test]
    fn summary_strips_the_pack_prefix() {
        assert_eq!(summary(&[champ(18, 900)]), "c18#18 900/1000 (18000,7) b1");
        assert_eq!(summary(&[]), "no champions");
        assert!(is_sim_tag("league_drmundo_sim:3") && !is_sim_tag("league_drmundo_w_on"));
    }
}
