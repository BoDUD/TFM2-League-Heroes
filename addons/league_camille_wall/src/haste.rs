//! 钩索攻速期间她打没打英雄（只记日志，不改行为）：用户 2026-10-28「卡蜜尔钩索的攻速加成会让她的平A出bug，感觉在buff
//! 持续期间她没法平A敌方英雄」。经典模拟（只有主包数据）里攻速期间照样打英雄，游戏里的日志又没有普攻，所以在这里数：
//! 每段 `league_camille_e_as`（E 落地的攻速，300 tick）和它结束后同样长的一段（对照），各记一行 `HASTE` / `AFTER`：
//!
//! - 普攻好了、攻击距离里有敌方英雄的 tick 数，其中她身上有出招动作（`Animation`）、强制位移（`ForceMove`）、硬控的各几 tick；
//! - 出手几次（普攻冷却往上跳）、打中英雄 / 别的几下（`on_attack`）；
//! - 大招场地钩子（[`super::arena`]）这段里把她按回中心、改成普攻各几次。
//!
//! 判断在 [`swung`]、[`in_reach`]（纯计算、单元测试）。

use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

use super::{camille, head, wlog};

/// 主包普攻的距离（`attack.range`），再加两人的身体半径算够得着。
pub const ATTACK_RANGE: f64 = 25_000.0;
/// E 落地的攻速持续多久（主包 `e_as`、本包 `E_AS_T`）：对照段也这么长。
pub const AFTER_TICKS: usize = 300;

/// 普攻冷却从这一 tick 到下一 tick 往上跳了：出手了一次。
pub fn swung(was: usize, now: usize) -> bool {
    now > was
}

/// 她（半径 `mine`）够不够得着离她 `d`、半径 `theirs` 的人。
pub fn in_reach(d: f64, mine: f64, theirs: f64) -> bool {
    d <= ATTACK_RANGE + mine + theirs
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Stats {
    pub ticks: usize,
    /// 普攻好了、够得着敌方英雄
    pub open: usize,
    pub open_anim: usize,
    pub open_moved: usize,
    pub open_cc: usize,
    pub swings: usize,
    pub hit_champs: usize,
    pub hit_others: usize,
    pub centre: usize,
    pub attack: usize,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Phase {
    Haste,
    After { until: usize },
}

#[derive(Clone, Default)]
pub struct Watch {
    phase: Option<Phase>,
    stats: Stats,
    last_cd: usize,
}

/// 场地钩子这一段里做了什么：(这场模拟, 她) -> (按回中心, 改成普攻)。
type Key = (u64, u32, u64, u64, usize);
static ARENA: LazyLock<Mutex<HashMap<Key, (usize, usize)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn key(sim: &StableSim<'_>, me: usize) -> Key {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index, me)
}

/// 场地钩子改了她的命令（`centre`：按回中心，否则改成普攻）。
pub fn note_arena(sim: &StableSim<'_>, me: usize, centre: bool) {
    let mut m = ARENA.lock().unwrap_or_else(|e| e.into_inner());
    let c = m.entry(key(sim, me)).or_default();
    if centre {
        c.0 += 1;
    } else {
        c.1 += 1;
    }
}

fn take_arena(sim: &StableSim<'_>, me: usize) -> (usize, usize) {
    ARENA.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me)).unwrap_or_default()
}

static LINES: AtomicUsize = AtomicUsize::new(0);

/// The first 60 lines, then every 20th.
fn counted() -> Option<usize> {
    let n = LINES.fetch_add(1, Ordering::Relaxed) + 1;
    (n <= 60 || n % 20 == 0).then_some(n)
}

impl Watch {
    /// Every tick (her passive).
    pub fn tick(&mut self, sim: &StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let tick = sim.tick();
        let hasted = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == camille("e_as"));
        let cd = e.cooldown(SkillSlotV1::Attack).map_or(0, |c| c.remaining);
        let alive = e.is_alive();
        match self.phase {
            None if hasted => self.start(sim, me, Phase::Haste),
            Some(Phase::Haste) if !hasted || !alive => {
                self.close(sim, me, "HASTE");
                if alive {
                    self.start(sim, me, Phase::After { until: tick + AFTER_TICKS });
                }
            }
            Some(Phase::After { until }) if hasted || !alive || tick >= until => {
                self.close(sim, me, "AFTER");
                if hasted && alive {
                    self.start(sim, me, Phase::Haste);
                }
            }
            _ => {}
        }
        if self.phase.is_none() || !alive {
            self.last_cd = cd;
            return;
        }
        let s = &mut self.stats;
        s.ticks += 1;
        if swung(self.last_cd, cd) {
            s.swings += 1;
        }
        self.last_cd = cd;
        let ready = e.cooldown(SkillSlotV1::Attack).is_some_and(|c| c.unlocked && c.remaining == 0);
        let (x, y) = e.pos();
        let (team, mine) = (e.team(), e.radius() as f64);
        let near = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).any(|u| {
            let (ux, uy) = u.pos();
            u.team() != team && u.is_alive() && u.is_champion() && u.is_targetable()
                && in_reach((ux as f64 - x as f64).hypot(uy as f64 - y as f64), mine, u.radius() as f64)
        });
        if ready && near {
            s.open += 1;
            let has = |kinds: &[CcKindV1]| {
                (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| kinds.iter().any(|k| k.code() == c.kind)))
            };
            if has(&[CcKindV1::Animation]) {
                s.open_anim += 1;
            }
            if has(&[CcKindV1::ForceMove]) {
                s.open_moved += 1;
            }
            if has(&super::HARD_CC) {
                s.open_cc += 1;
            }
        }
    }

    /// Her attack landed on `target` (her passive's `on_attack`).
    pub fn hit(&mut self, sim: &StableSim<'_>, target: usize) {
        if self.phase.is_none() {
            return;
        }
        if sim.get_entity(target).is_some_and(|t| t.is_champion()) {
            self.stats.hit_champs += 1;
        } else {
            self.stats.hit_others += 1;
        }
    }

    fn start(&mut self, sim: &StableSim<'_>, me: usize, phase: Phase) {
        take_arena(sim, me);
        self.phase = Some(phase);
        self.stats = Stats::default();
    }

    fn close(&mut self, sim: &StableSim<'_>, me: usize, what: &str) {
        let (centre, attack) = take_arena(sim, me);
        let s = Stats { centre, attack, ..self.stats };
        self.phase = None;
        if let Some(n) = counted() {
            wlog(format!(
                "{} {what} #{n}: {} ticks; attack ready with an enemy champion in reach {} ticks (casting {}, moved {}, \
                 controlled {}); {} swings, hit {} champions and {} others; the arena held her at the centre {} times, \
                 sent her to attack {}",
                head(sim, me), s.ticks, s.open, s.open_anim, s.open_moved, s.open_cc, s.swings, s.hit_champs,
                s.hit_others, s.centre, s.attack
            ));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_swing_is_the_attack_cooldown_going_up() {
        assert!(swung(0, 39));
        assert!(swung(3, 39)); // swung a tick before the last one ran out
        assert!(!swung(39, 38));
        assert!(!swung(0, 0));
    }

    #[test]
    fn reach_counts_both_bodies() {
        assert!(in_reach(25_000.0, 0.0, 0.0));
        assert!(in_reach(33_000.0, 4_000.0, 4_000.0));
        assert!(!in_reach(33_001.0, 4_000.0, 4_000.0));
    }
}
