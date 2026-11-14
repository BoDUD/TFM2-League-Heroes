//! 大嘴死后（`KOG`，0.3.1，2026-11-14）。
//!
//! 克格莫的被动「来自艾卡西亚的惊喜」只靠数据（tools/kit/build_kogmaw.py）：每条命第一次出手时挂上
//! `league_kogmaw_init`，同时在他身上挂一个整局的 `AddCasted`，每 6 tick 往自己身上抛一个隐藏的抛物物；抛物物落地时问
//! `RandomTarget {range: 1, AllyOnlySelf}` 他还活着吗，找不到就挂 `league_kogmaw_p_done`、放出虚空分身（追踪弹
//! `p_form` 加一颗隐藏的溅射弹 `p_burst`，两颗都离开尸体飞向敌方英雄）。经典引擎里他每次死都放；游戏里玩家两种普攻都
//! 没看到（「大嘴死了后的炸人怎么看不到了」「没看到大嘴炸人」）。游戏的日志也看不出来：league.dll 的画图日志开局就写满了，
//! 别的日志又不记这些名字。
//!
//! 他死了以后他自己的钩子不跑（和死掉的英雄的被动不跑是同一回事），所以每个活着的英雄的观察钩子每 tick 都看一眼每个
//! 克格莫，只由实体编号最小的那个活着的英雄的钩子写日志（[`first_alive`]）：
//! - `KOG LIFE`：这一局第一次看到他时，他身上 league_kogmaw_* 的 buff；
//! - `KOG FLAGS`：活着时 `init` / `p_done` 有了或没了（每条命的监视开了没有，放过分身以后清了没有）；
//! - `KOG DIED`：死的那一 tick 他身上的 buff，还有他放出去、还在飞的投射物（几颗、离尸体多远）；
//! - `KOG +n`：死后 [`AFTER`] tick 内，buff 或他的投射物的个数每变一次写一行（n 是死后第几 tick）；
//! - `KOG BACK`：复活时这一死的总结：`p_done` 出现过没有、多出来的 buff、死后他最多同时有几颗投射物、最远离尸体多远，
//!   和他复活时身上的 buff（`init` 还在的话，这条命不会再开监视）。
//!
//! 投射物只有位置和放的人，没有名字：活着时那颗抛物物落在他身上，分身是两颗离开尸体飞走的。

use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

use crate::{at, dist, head, on_screen, wlog};

pub const KOG: &str = "league_kogmaw";
const PREFIX: &str = "league_kogmaw_";
/// ticks after a death in which the changes are written
pub const AFTER: usize = 300;
/// his flags whose changes are written while he lives
const FLAGS: [&str; 2] = ["league_kogmaw_init", "league_kogmaw_p_done"];
const DONE: &str = "league_kogmaw_p_done";
/// KOG lines a launch from the matches not on screen (the one on screen: all of them), and at most this many a death
pub const CAP: usize = 6000;
pub const PER_DEATH: usize = 40;

static LINES: AtomicUsize = AtomicUsize::new(0);

fn room(sim: &StableSim<'_>) -> bool {
    on_screen(sim) || LINES.fetch_add(1, Ordering::Relaxed) < CAP
}

/// The entity of the lowest-numbered champion alive (the hook that writes is his player's).
pub fn first_alive(sim: &StableSim<'_>) -> Option<usize> {
    (0..sim.player_count())
        .filter_map(|i| sim.player_at(i))
        .filter(|p| p.is_alive())
        .filter_map(|p| p.champion())
        .filter(|c| c.is_alive())
        .map(|c| c.id())
        .min()
}

/// The players whose champion is Kog'Maw; None while no player has a champion yet.
fn kog_players(sim: &StableSim<'_>) -> Option<Vec<usize>> {
    let mut any = false;
    let mut found = Vec::new();
    for i in 0..sim.player_count() {
        let Some(p) = sim.player_at(i) else { continue };
        let Some(c) = p.champion() else { continue };
        any = true;
        if c.name().as_deref() == Some(KOG) {
            found.push(p.id());
        }
    }
    any.then_some(found)
}

fn kog_buffs(e: &StableEntity<'_, '_>) -> Vec<String> {
    let mut v: Vec<String> = (0..e.buff_count())
        .filter_map(|i| e.buff_at(i))
        .filter(|b| b.name().starts_with(PREFIX))
        .map(|b| b.name().to_string())
        .collect();
    v.sort();
    v.dedup();
    v
}

/// What a hook saw of one Kog'Maw in a tick (`buffs` / `shots`: None when not read in that tick).
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Obs {
    pub id: usize,
    pub alive: bool,
    pub at: Option<(f64, f64)>,
    pub buffs: Option<Vec<String>>,
    pub shots: Option<Vec<(f64, f64)>>,
}

#[derive(Clone, Debug, Default, PartialEq)]
struct Death {
    tick: usize,
    at: Option<(f64, f64)>,
    /// the hook did not see the death itself (it was not watching then): no lines, the summary says so
    partial: bool,
    lines: usize,
    done: bool,
    gained: Vec<String>,
    most: usize,
    far: f64,
}

#[derive(Clone, Debug, Default, PartialEq)]
struct Seen {
    player: usize,
    alive: bool,
    buffs: Vec<String>,
    shots: usize,
    death: Option<Death>,
}

/// One hook's view of the match's Kog'Maws.
#[derive(Clone, Debug, Default)]
pub struct KogEye {
    players: Option<Vec<usize>>,
    last: Option<usize>,
    writer: bool,
    seen: Vec<Seen>,
}

fn short(b: &str) -> &str {
    b.strip_prefix(PREFIX).unwrap_or(b)
}

fn names(buffs: &[String]) -> String {
    buffs.iter().map(|b| short(b)).collect::<Vec<_>>().join(", ")
}

fn change(old: &[String], new: &[String]) -> String {
    let mut s = String::new();
    for b in new.iter().filter(|b| !old.contains(b)) {
        s += &format!(" +{}", short(b));
    }
    for b in old.iter().filter(|b| !new.contains(b)) {
        s += &format!(" -{}", short(b));
    }
    s
}

fn flags(buffs: &[String]) -> Vec<String> {
    buffs.iter().filter(|b| FLAGS.contains(&b.as_str())).cloned().collect()
}

fn farthest(shots: &[(f64, f64)], from: Option<(f64, f64)>) -> f64 {
    from.map_or(0.0, |f| shots.iter().map(|&p| dist(p, f)).fold(0.0, f64::max))
}

fn spots(shots: &[(f64, f64)], from: Option<(f64, f64)>) -> String {
    let Some(f) = from else { return String::new() };
    if shots.is_empty() {
        return String::new();
    }
    let mut d: Vec<String> = shots.iter().take(6).map(|&p| format!("{:.0}k", dist(p, f) / 1000.0)).collect();
    if shots.len() > 6 {
        d.push("...".into());
    }
    format!(" ({} from the body)", d.join(" "))
}

impl KogEye {
    /// Every tick from an alive champion's hook; `write`: this hook is the one that writes.
    pub fn look(&mut self, sim: &StableSim<'_>, write: bool) {
        let tick = sim.tick();
        if self.last == Some(tick) {
            return;
        }
        let steady = self.last.is_some_and(|t| t + 1 == tick);
        let current = steady && self.writer;
        self.last = Some(tick);
        self.writer = write;
        if self.players.is_none() {
            self.players = kog_players(sim);
        }
        let players = match &self.players {
            Some(v) if !v.is_empty() => v.clone(),
            _ => return,
        };
        let mut all_shots: Option<Vec<ProjectileInfoV1>> = None;
        for p in players {
            let Some(pl) = sim.get_player(p) else { continue };
            let ent = pl.champion();
            let alive = pl.is_alive() && ent.as_ref().is_some_and(|e| e.is_alive());
            let id = ent.as_ref().map_or(usize::MAX, |e| e.id());
            let (known, window) = match self.seen.iter().find(|s| s.player == p) {
                None => (false, false),
                Some(s) => (
                    true,
                    !alive && (s.alive || s.death.as_ref().is_some_and(|d| tick.saturating_sub(d.tick) <= AFTER)),
                ),
            };
            let shots = window.then(|| {
                let all = all_shots.get_or_insert_with(|| {
                    (0..sim.projectile_count()).filter_map(|i| sim.projectile_at(i)).filter(|q| !q.is_end).collect()
                });
                all.iter().filter(|q| q.caster_id == id).map(|q| (q.x as f64, q.y as f64)).collect()
            });
            let o = Obs {
                id,
                alive,
                at: ent.as_ref().map(|e| at(e)),
                buffs: (write || window || !known).then(|| ent.as_ref().map(|e| kog_buffs(e)).unwrap_or_default()),
                shots,
            };
            for (kind, body) in self.step(p, &o, tick, steady, write, current) {
                if room(sim) {
                    wlog(format!("KOG {kind} {} {body}", head(sim)));
                }
            }
        }
    }

    /// One Kog'Maw's observation in a tick: the lines to write (only when `write`), the state brought up to date.
    /// `steady`: this hook saw the tick before (otherwise the state is caught up without lines); `current`: it read his
    /// buffs the tick before as well (it was the writer).
    fn step(&mut self, player: usize, o: &Obs, tick: usize, steady: bool, write: bool, current: bool) -> Vec<(String, String)> {
        let mut out = Vec::new();
        let Some(k) = self.seen.iter().position(|s| s.player == player) else {
            let buffs = o.buffs.clone().unwrap_or_default();
            if write && o.alive {
                out.push(("LIFE".into(), format!("#{} P{player}: buffs [{}]", o.id, names(&buffs))));
            }
            let death = (!o.alive).then(|| Death { tick, at: o.at, partial: true, ..Death::default() });
            self.seen.push(Seen { player, alive: o.alive, buffs, shots: 0, death });
            return out;
        };
        let s = &mut self.seen[k];
        let buffs = o.buffs.clone().unwrap_or_else(|| s.buffs.clone());
        let n = o.shots.as_ref().map_or(0, |v| v.len());
        if !steady {
            if o.alive {
                s.death = None;
            } else if s.death.is_none() {
                s.death = Some(Death { tick, at: o.at, partial: true, ..Death::default() });
            }
            s.alive = o.alive;
            s.buffs = buffs;
            s.shots = n;
            return out;
        }
        if s.alive && !o.alive {
            let shots = o.shots.clone().unwrap_or_default();
            let mut d = Death { tick, at: o.at, most: n, far: farthest(&shots, o.at), ..Death::default() };
            if write {
                out.push((
                    "DIED".into(),
                    format!("#{} P{player}: buffs [{}] | his projectiles {n}{}", o.id, names(&buffs), spots(&shots, o.at)),
                ));
                d.lines = 1;
            }
            s.death = Some(d);
        } else if !s.alive && o.alive {
            if let (Some(d), true) = (s.death.take(), write) {
                out.push((
                    "BACK".into(),
                    format!(
                        "#{} P{player} after {:.1}s{}: p_done seen {} | gained [{}] | his projectiles after the death at \
                         most {}, farthest {:.0}k from the body | buffs now [{}]",
                        o.id,
                        tick.saturating_sub(d.tick) as f64 / 60.0,
                        if d.partial { " (partial)" } else { "" },
                        if d.done { "yes" } else { "NO" },
                        names(&d.gained),
                        d.most,
                        d.far / 1000.0,
                        names(&buffs)
                    ),
                ));
            }
        } else if !o.alive {
            if let Some(d) = s.death.as_mut() {
                let dt = tick.saturating_sub(d.tick);
                if let Some(shots) = &o.shots {
                    d.most = d.most.max(shots.len());
                    d.far = d.far.max(farthest(shots, d.at));
                }
                d.done |= buffs.iter().any(|b| b == DONE);
                for b in &buffs {
                    if !s.buffs.contains(b) && !d.gained.contains(b) {
                        d.gained.push(b.clone());
                    }
                }
                let changed = buffs != s.buffs || (o.shots.is_some() && n != s.shots);
                if write && changed && !d.partial && dt <= AFTER && d.lines < PER_DEATH {
                    let shots = o.shots.clone().unwrap_or_default();
                    out.push((
                        format!("+{dt}"),
                        format!(
                            "#{} P{player}: buffs [{}]{} | his projectiles {n}{}",
                            o.id,
                            names(&buffs),
                            change(&s.buffs, &buffs),
                            spots(&shots, d.at)
                        ),
                    ));
                    d.lines += 1;
                }
            }
        } else if write && current {
            let (was, now) = (flags(&s.buffs), flags(&buffs));
            if was != now {
                out.push(("FLAGS".into(), format!("#{} P{player}:{}", o.id, change(&was, &now))));
            }
        }
        s.alive = o.alive;
        s.buffs = buffs;
        if o.shots.is_some() {
            s.shots = n;
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn b(names: &[&str]) -> Option<Vec<String>> {
        Some(names.iter().map(|n| format!("{PREFIX}{n}")).collect())
    }

    fn obs(alive: bool, buffs: Option<Vec<String>>, shots: Option<Vec<(f64, f64)>>) -> Obs {
        Obs { id: 26, alive, at: Some((500_000.0, 500_000.0)), buffs, shots }
    }

    fn kinds(lines: &[(String, String)]) -> Vec<&str> {
        lines.iter().map(|(k, _)| k.as_str()).collect()
    }

    #[test]
    fn a_death_that_wakes_the_form_reads_in_the_lines() {
        let mut eye = KogEye::default();
        let l = eye.step(3, &obs(true, b(&["init", "q_pas"]), None), 100, true, true, false);
        assert_eq!(l, vec![("LIFE".to_string(), "#26 P3: buffs [init, q_pas]".to_string())]);
        assert!(eye.step(3, &obs(true, b(&["init", "q_pas"]), None), 101, true, true, true).is_empty());
        // he dies with the watch's lob in the air on him
        let l = eye.step(3, &obs(false, b(&["init", "q_pas"]), Some(vec![(500_000.0, 501_000.0)])), 102, true, true, true);
        assert_eq!(kinds(&l), ["DIED"]);
        assert!(l[0].1.ends_with("buffs [init, q_pas] | his projectiles 1 (1k from the body)"), "{}", l[0].1);
        // the lob lands: p_done, the form and the burst leave the body
        let two = vec![(501_000.0, 500_000.0), (501_000.0, 500_000.0)];
        let l = eye.step(3, &obs(false, b(&["init", "p_done", "q_pas"]), Some(two)), 105, true, true, true);
        assert_eq!(kinds(&l), ["+3"]);
        assert!(l[0].1.contains("buffs [init, p_done, q_pas] +p_done | his projectiles 2 (1k 1k from the body)"), "{}", l[0].1);
        // they fly on: same count, no line; they hit: a line
        let far = vec![(510_000.0, 500_000.0), (510_000.0, 500_000.0)];
        assert!(eye.step(3, &obs(false, b(&["init", "p_done", "q_pas"]), Some(far)), 110, true, true, true).is_empty());
        let l = eye.step(3, &obs(false, b(&["init", "p_done", "q_pas"]), Some(vec![])), 130, true, true, true);
        assert_eq!(kinds(&l), ["+28"]);
        // back: the summary, and the new life's watch when init comes back
        let l = eye.step(3, &obs(true, b(&["p_done"]), None), 984, true, true, true);
        assert_eq!(kinds(&l), ["BACK"]);
        let s = &l[0].1;
        assert!(s.contains("after 14.7s: p_done seen yes | gained [p_done] | his projectiles after the death at most 2, farthest 10k from the body | buffs now [p_done]"), "{s}");
        let l = eye.step(3, &obs(true, b(&["init"]), None), 985, true, true, true);
        assert_eq!(l, vec![("FLAGS".to_string(), "#26 P3: +init -p_done".to_string())]);
    }

    #[test]
    fn a_death_without_the_form_says_no() {
        let mut eye = KogEye::default();
        eye.step(0, &obs(true, b(&["init"]), None), 10, true, true, false);
        eye.step(0, &obs(false, b(&["init"]), Some(vec![(500_000.0, 500_000.0)])), 11, true, true, true);
        let l = eye.step(0, &obs(false, b(&["init"]), Some(vec![])), 18, true, true, true);
        assert_eq!(kinds(&l), ["+7"]);
        let l = eye.step(0, &obs(true, b(&["init"]), None), 600, true, true, true);
        assert!(l[0].1.contains("p_done seen NO | gained [] | his projectiles after the death at most 1, farthest 0k"), "{}", l[0].1);
        assert!(l[0].1.ends_with("buffs now [init]"), "{}", l[0].1);
    }

    #[test]
    fn only_the_writer_writes_and_a_gap_writes_nothing() {
        let mut eye = KogEye::default();
        assert!(eye.step(1, &obs(true, b(&["init"]), None), 10, true, false, false).is_empty());
        // not the writer: the death is followed all the same
        assert!(eye.step(1, &obs(false, b(&["init"]), Some(vec![])), 11, true, false, false).is_empty());
        assert!(eye.step(1, &obs(false, b(&["init", "p_done"]), Some(vec![(500_000.0, 520_000.0)])), 12, true, false, false).is_empty());
        // it becomes the writer mid-death: the changes from now on are written, the summary has what it followed
        let l = eye.step(1, &obs(false, b(&["init", "p_done"]), Some(vec![])), 13, true, true, false);
        assert_eq!(kinds(&l), ["+2"]);
        let l = eye.step(1, &obs(true, b(&["init", "p_done"]), None), 400, true, true, true);
        assert!(l[0].1.contains("p_done seen yes") && l[0].1.contains("farthest 20k"), "{}", l[0].1);
        // a hook that missed ticks catches up silently, and a death it did not see is marked partial
        let mut late = KogEye::default();
        late.step(1, &obs(true, b(&["init"]), None), 10, true, true, false);
        assert!(late.step(1, &obs(false, b(&["init"]), Some(vec![])), 50, false, true, false).is_empty());
        assert!(late.step(1, &obs(false, b(&["init", "p_done"]), Some(vec![])), 51, true, true, true).is_empty());
        let l = late.step(1, &obs(true, b(&["init"]), None), 300, true, true, true);
        assert!(l[0].1.contains("after 4.2s (partial): p_done seen yes"), "{}", l[0].1);
    }

    #[test]
    fn the_flags_alone_are_written_while_he_lives() {
        let mut eye = KogEye::default();
        eye.step(2, &obs(true, b(&[]), None), 10, true, true, false);
        // Bio-Arcane Barrage and the like come and go without a line
        assert!(eye.step(2, &obs(true, b(&["w_on"]), None), 11, true, true, true).is_empty());
        let l = eye.step(2, &obs(true, b(&["init", "q_pas", "w_on"]), None), 12, true, true, true);
        assert_eq!(l, vec![("FLAGS".to_string(), "#26 P2: +init".to_string())]);
        // a hook that becomes the writer reads his buffs afresh before it compares
        let mut other = KogEye::default();
        other.step(2, &obs(true, b(&[]), None), 10, true, false, false);
        assert!(other.step(2, &obs(true, b(&["init"]), None), 11, true, true, false).is_empty());
    }
}
