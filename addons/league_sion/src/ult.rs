//! 大招「蛮横冲撞」的日志（0.2.0，用户 2026-11-05：「塞恩是不是也不太放大？」——当天的日志里一行大招都没有）。
//!
//! 大招本身是主包的数据（tools/kit/build_sion.py：这一格只**上膛** `r_arm_t` tick，每 10 tick 查一次该不该冲）。本包的被动
//! 每 tick 看他身上的标记，把能看到的记下来：
//! - `league_sion_r_arm` 出现：上膛（`ARMED`）；窗口里每 10 tick 数一下 90000 内有没有敌方英雄、50000 内有没有队友；
//! - `r_arm` 没了：带 `league_sion_r_reset` 是窗口过期（`LAPSED`，附上窗口里看到的、以及大招剩余冷却——退还了应该只剩 72 tick），
//!   否则是冲出去了（`CHARGE`；冲撞的原因照前一 tick 的标记：`r_n3` 身边 2 名队友的团战，`r_n2` 1 名队友的开团 / 追击，
//!   都没有就是救人）；贴着脸冲的那一下 `r_go` 当 tick 就被撞击去掉，看不到，所以不用 `r_go` 认冲撞；
//! - `league_sion_r_go` 没了：不到 `R_TICK` tick 是撞上了（`HIT`，按跑了多久分三档），跑满就是没撞到（`MISS`）；
//! - 每条命结束（阵亡、变亡灵）记一行 `R this life: armed N, charged M`。
//! 变成亡灵时把 `r_arm` 摘掉：亡灵不能放技能，可数据的轮询还在跑，窗口开着就还会冲出去。
use std::collections::HashSet;

/// 主包参数表的数字（单元测试核对 build_sion.P）：冲最多 R_TICK tick，R_B1 / R_B2 分三档伤害，窗口 R_ARM_T tick，轮询 R_POLL。
pub const R_TICK: usize = 50;
pub const R_B1: usize = 16;
pub const R_B2: usize = 32;
pub const R_ARM_T: usize = 600;
pub const R_POLL: usize = 10;
/// 轮询看的范围（主包：r_range 90000 内的敌方英雄，r_near 50000 内的队友；都按圆心算，引擎还会加上两个身体）。
pub const R_RANGE: u64 = 90000;
pub const R_NEAR: u64 = 50000;

/// 冲撞的原因，照冲出去前一 tick 身上的标记。
pub fn reason(prev: &HashSet<String>) -> &'static str {
    if prev.contains("league_sion_r_n3") {
        "teamfight (2 allies near)"
    } else if prev.contains("league_sion_r_n2") {
        "engage / follow-up (1 ally near)"
    } else {
        "save (an ally in crowd control)"
    }
}

/// 冲了 `ran` tick 后 `r_go` 没了：撞上（第几档）还是跑满没撞到。
pub fn outcome(ran: usize) -> String {
    if ran >= R_TICK {
        return format!("MISS: ran the full {R_TICK} ticks and hit nobody");
    }
    let tier = if ran < R_B1 { 1 } else if ran < R_B2 { 2 } else { 3 };
    format!("HIT after {ran} ticks (tier {tier})")
}

/// 窗口里每次轮询看到的：有没有敌方英雄在冲程里、有没有队友在身边。
#[derive(Clone, Copy, Default, Debug, PartialEq, Eq)]
pub struct Seen {
    pub polls: usize,
    pub enemy: usize,
    pub enemy_alone: usize,
    pub enemy_with_ally: usize,
    pub none: usize,
}

impl Seen {
    pub fn add(&mut self, enemies: usize, allies: usize) {
        self.polls += 1;
        if enemies == 0 {
            self.none += 1;
        } else if allies == 0 {
            self.enemy += 1;
            self.enemy_alone += 1;
        } else {
            self.enemy += 1;
            self.enemy_with_ally += 1;
        }
    }

    pub fn summary(&self) -> String {
        format!("{} polls: enemy champion in reach {} (alone {}, with an ally {}), nobody in reach {}",
                self.polls, self.enemy, self.enemy_alone, self.enemy_with_ally, self.none)
    }
}

/// 一条命里大招的状态。
#[derive(Clone, Default, Debug)]
pub struct Onslaught {
    pub armed_at: Option<usize>,
    pub go_at: Option<usize>,
    pub armed: usize,
    pub charged: usize,
    pub seen: Seen,
    pub prev: HashSet<String>,
}

/// 这一 tick 的变化（纯逻辑，单元测试用）：`names` 是他现在身上的标记。
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Event {
    Armed,
    /// 窗口过期（退还冷却），跑了多少 tick
    Lapsed(usize),
    /// 冲出去了：原因
    Charge(&'static str),
    /// `r_go` 没了：跑了多少 tick
    Done(usize),
    Poll,
}

impl Onslaught {
    pub fn step(&mut self, now: usize, names: &HashSet<String>) -> Vec<Event> {
        let mut out = vec![];
        let arm = names.contains("league_sion_r_arm");
        let go = names.contains("league_sion_r_go");
        match (self.armed_at, arm) {
            (None, true) => {
                self.armed_at = Some(now);
                self.armed += 1;
                self.seen = Seen::default();
                out.push(Event::Armed);
            }
            (Some(t0), false) => {
                self.armed_at = None;
                if names.contains("league_sion_r_reset") {
                    out.push(Event::Lapsed(now - t0));
                } else {
                    self.charged += 1;
                    out.push(Event::Charge(reason(&self.prev)));
                    if !go {
                        // hit on the spot: r_go was put on and taken off within the tick
                        out.push(Event::Done(0));
                    }
                }
            }
            (Some(t0), true) if (now - t0) % R_POLL == 0 => out.push(Event::Poll),
            _ => {}
        }
        match (self.go_at, go) {
            (None, true) => self.go_at = Some(now),
            (Some(t0), false) => {
                self.go_at = None;
                out.push(Event::Done(now - t0));
            }
            _ => {}
        }
        self.prev = names.clone();
        out
    }

    /// 新的一条命。
    pub fn reset(&mut self) {
        *self = Onslaught::default();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn names(v: &[&str]) -> HashSet<String> {
        v.iter().map(|s| format!("league_sion_{s}")).collect()
    }

    #[test]
    fn the_reason_follows_the_count_flags() {
        assert_eq!(reason(&names(&["r_arm", "r_n1", "r_n2", "r_n3"])), "teamfight (2 allies near)");
        assert_eq!(reason(&names(&["r_arm", "r_n1", "r_n2"])), "engage / follow-up (1 ally near)");
        assert_eq!(reason(&names(&["r_arm", "r_n1"])), "save (an ally in crowd control)");
        assert_eq!(reason(&names(&[])), "save (an ally in crowd control)");
    }

    #[test]
    fn the_outcome_by_how_far_he_ran() {
        assert_eq!(outcome(0), "HIT after 0 ticks (tier 1)");
        assert_eq!(outcome(15), "HIT after 15 ticks (tier 1)");
        assert_eq!(outcome(16), "HIT after 16 ticks (tier 2)");
        assert_eq!(outcome(32), "HIT after 32 ticks (tier 3)");
        assert_eq!(outcome(49), "HIT after 49 ticks (tier 3)");
        assert!(outcome(50).starts_with("MISS"));
        assert!(outcome(51).starts_with("MISS"));
    }

    #[test]
    fn a_window_that_lapses_and_one_that_charges() {
        let mut o = Onslaught::default();
        assert_eq!(o.step(100, &names(&["k_hp"])), vec![]);
        assert_eq!(o.step(101, &names(&["k_hp", "r_arm"])), vec![Event::Armed]);
        assert_eq!(o.step(105, &names(&["k_hp", "r_arm"])), vec![]);
        assert_eq!(o.step(111, &names(&["k_hp", "r_arm", "r_n1"])), vec![Event::Poll]);
        // the reset flag with the arm flag gone: lapsed, refunded
        assert_eq!(o.step(698, &names(&["k_hp", "r_reset"])), vec![Event::Lapsed(597)]);
        assert_eq!((o.armed, o.charged), (1, 0));
        // a second window: the count flags on the poll tick, the charge the tick after
        assert_eq!(o.step(800, &names(&["r_arm"])), vec![Event::Armed]);
        assert_eq!(o.step(810, &names(&["r_arm", "r_n1", "r_n2"])), vec![Event::Poll]);
        assert_eq!(o.step(811, &names(&["r_go", "r_d1", "r_d2"])), vec![Event::Charge("engage / follow-up (1 ally near)")]);
        assert_eq!(o.step(820, &names(&["r_go", "r_d2"])), vec![]);
        assert_eq!(o.step(831, &names(&[])), vec![Event::Done(20)]);
        assert_eq!((o.armed, o.charged), (2, 1));
    }

    #[test]
    fn a_hit_on_the_spot_shows_no_r_go() {
        let mut o = Onslaught::default();
        o.step(10, &names(&["r_arm"]));
        o.step(20, &names(&["r_arm", "r_n1", "r_n2", "r_n3"]));
        assert_eq!(o.step(21, &names(&[])), vec![Event::Charge("teamfight (2 allies near)"), Event::Done(0)]);
        assert_eq!(o.charged, 1);
    }

    #[test]
    fn the_poll_tally() {
        let mut s = Seen::default();
        s.add(0, 0);
        s.add(2, 0);
        s.add(1, 1);
        s.add(1, 3);
        assert_eq!(s, Seen { polls: 4, enemy: 3, enemy_alone: 1, enemy_with_ally: 2, none: 1 });
        assert_eq!(s.summary(), "4 polls: enemy champion in reach 3 (alone 1, with an ally 2), nobody in reach 1");
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_sion.py");
        let src = std::fs::read_to_string(path).expect("build_sion.py");
        for (key, v) in [("r_tick", R_TICK), ("r_b1", R_B1), ("r_b2", R_B2), ("r_arm_t", R_ARM_T), ("r_poll", R_POLL),
                         ("r_range", R_RANGE as usize), ("r_near", R_NEAR as usize)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_sion.P");
        }
    }
}
