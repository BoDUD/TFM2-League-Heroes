//! 入殓 (`abysspact_undertaker`) · 抬棺人 · 打野坦克
//!
//! 被动「棺盾」：普攻伤害常驻 -15%（`coffin_shield`）；每 8 秒备好一层技能护挡（`skill_guard`，技能伤害 -30%）。
//! 只有敌方英雄刚放出去的技能打中他才用掉：`on_damaged` 里看出手的人哪一栏技能的冷却刚开始走（2 秒内）。用掉时棺材一闪。
//! 以前是「一 tick 掉血超过 25」就用掉，野怪、小兵、普攻都会把它打掉，打野时每 8 秒白闪一次。
//!
//! 大招「入殓」：数据关棺、定住目标、给他挂 `coffin_ask`；本包看到后
//! - 把人放逐进棺材 2 秒（`entity_banish`：看不见、谁都选不中、不能动作），就是设计里的「不能动、也打不到」；
//! - 给自己挂 `carrying`（+20% 移速，棺缝里挣扎的影子画在他身上），强制位移加跑步动作往自己人那边走：队友扎堆的地方，
//!   没有队友就去最近的己方塔，走到离那里 1.5 万为止；
//! - 2 秒到、放逐结束，把人放到他脚下，再强制位移甩到他身前 8000（画面跟着走，撞墙引擎自己停），然后摔棺：
//!   `150 + 8% 目标最大生命` 物理伤害、眩晕 1 秒。放逐被韧性提前结束时当场摔出来；放逐不上（免控）就直接摔。
//! 放逐中的人在模拟里挪不动（塔姆附加包的结论），所以不逐 tick 跟着他走，摔的时候一次放到位。
//! 他自己死了：人留在棺材里到放逐结束，在原地出来，不摔。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, has_buff};

pub const HERO: &str = "abysspact_undertaker";
pub const COFFIN_SHIELD: &str = "abysspact_undertaker_coffin_shield";
pub const SKILL_GUARD: &str = "abysspact_undertaker_skill_guard";
pub const COFFIN_ASK: &str = "abysspact_undertaker_coffin_ask";
pub const CARRYING: &str = "abysspact_undertaker_carrying";
pub const R_CAST_VOICE: &str = "abysspact_undertaker_r_voice";

pub const GUARD_CD: usize = 480; // 8.0s
/// 对方某一栏技能的冷却开始走了这么多 tick 以内，打中他的这一下算那个技能的（出手加弹道飞行）。
pub const GUARD_RECENT: usize = 120;
pub const CARRY_TICKS: usize = 120; // 2.0s
pub const CARRY_MS_PCT: i32 = 20;
pub const SLAM_STUN: u64 = 60; // 1.0s
pub const SLAM_BASE: usize = 150;
pub const SLAM_HP_PCT: usize = 8;
/// 摔出来甩多远、几 tick 甩完。
pub const THROW_DIST: f64 = 8_000.0;
pub const THROW_TICKS: u64 = 6;
/// 扛着走：走到离队友扎堆处这么近就停；找队友、找己方塔的范围。
pub const HOME_STOP: f64 = 15_000.0;
pub const ALLY_LOOK: f64 = 100_000.0;
pub const TOWER_LOOK: f64 = 250_000.0;
/// 放逐到点后最多再等几 tick 让人出来。
pub const OUT_GRACE: usize = 5;

pub fn slam_damage(target_max_hp: usize) -> usize {
    SLAM_BASE + target_max_hp.saturating_mul(SLAM_HP_PCT) / 100
}

/// 出手的人这一栏技能刚放出去（冷却刚开始走）。
pub fn just_cast(remaining: usize, cooltime: usize) -> bool {
    remaining > 0 && cooltime > 0 && remaining + GUARD_RECENT >= cooltime
}

/// 扛着走的位移：从 `from` 朝 `home`，停在离 `home` HOME_STOP 处，最多走 `max_len`；太短就不走。
pub fn carry_step(from: (f64, f64), home: (f64, f64), max_len: f64) -> Option<(f64, f64)> {
    let (dx, dy) = (home.0 - from.0, home.1 - from.1);
    let d = (dx * dx + dy * dy).sqrt();
    let len = (d - HOME_STOP).min(max_len);
    if len < 2_000.0 || d < 1.0 {
        return None;
    }
    Some((dx / d * len, dy / d * len))
}

fn unit(v: (f64, f64)) -> Option<(f64, f64)> {
    let d = (v.0 * v.0 + v.1 * v.1).sqrt();
    (d >= 1.0).then(|| (v.0 / d, v.1 / d))
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

/// 强制位移 `delta`，`ticks` 内走完（画面跟着走；`entity_set_pos` 画面不跟）。
fn force_move(sim: &mut StableSim<'_>, id: usize, delta: (f64, f64), ticks: u64) {
    let d = (delta.0 * delta.0 + delta.1 * delta.1).sqrt();
    let ticks = ticks.max(1);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks);
    cc.dx = delta.0.round() as i64;
    cc.dy = delta.1.round() as i64;
    cc.speed = ((d / ticks as f64).ceil() as u64).max(1);
    sim.apply_cc(id, &cc);
}

#[derive(Clone, Copy)]
struct Carry {
    victim: usize,
    since: usize,
    until: usize,
    /// 摔出去的方向（单位向量）：扛着走的方向；没走就是从抓人的地方朝他。
    dir: (f64, f64),
}

#[derive(Clone, Default)]
struct UndertakerPassive {
    voice: Voice,
    shield_applied: bool,
    guard_ready_at: usize,
    guard_armed: bool,
    carry: Option<Carry>,
}

impl UndertakerPassive {
    /// 往哪扛：身边队友扎堆的地方；没有队友就去最近的己方塔。
    fn home_point(sim: &StableSim<'_>, entity: usize, team: usize, at: (f64, f64)) -> Option<(f64, f64)> {
        let mut sum = (0.0, 0.0);
        let mut n = 0.0;
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.id() == entity || !e.is_champion() || !e.is_alive() || e.team() != team {
                continue;
            }
            let p = fpos(e.pos());
            if (p.0 - at.0).hypot(p.1 - at.1) <= ALLY_LOOK {
                sum = (sum.0 + p.0, sum.1 + p.1);
                n += 1.0;
            }
        }
        if n > 0.0 {
            return Some((sum.0 / n, sum.1 / n));
        }
        let mut best: Option<(f64, (f64, f64))> = None;
        for i in 0..sim.tower_count() {
            let Some(t) = sim.get_entity(sim.tower_id_at(i)) else { continue };
            if !t.is_alive() || t.team() != team {
                continue;
            }
            let p = fpos(t.pos());
            let d = (p.0 - at.0).hypot(p.1 - at.1);
            if d <= TOWER_LOOK && best.is_none_or(|(bd, _)| d < bd) {
                best = Some((d, p));
            }
        }
        best.map(|(_, p)| p)
    }

    fn start_carry(&mut self, sim: &mut StableSim<'_>, entity: usize, victim: usize, team: usize, at: (u64, u64)) {
        sim.entity_remove_buff(victim, COFFIN_ASK);
        let Some((v_at, v_max)) = sim.get_entity(victim).map(|e| (e.pos(), e.hp().1)) else { return };
        let tick = sim.tick();
        let me = fpos(at);
        let mut dir = unit((me.0 - v_at.0 as f64, me.1 - v_at.1 as f64)).unwrap_or((1.0, 0.0));
        if !sim.entity_banish(entity, victim, CARRY_TICKS, "", "") {
            // 塞不进棺材（免控之类）：直接摔
            self.slam(sim, entity, victim, v_max);
            return;
        }
        let mut speed = BuffV1::timed(CARRYING, CARRY_TICKS);
        speed.move_speed_mult = CARRY_MS_PCT;
        sim.entity_remove_buff(entity, CARRYING);
        sim.add_buff(entity, &speed);
        sim.play_sfx("abysspact_undertaker_coffin_close", entity, &InputTargetV1::target(entity));
        // 扛着往自己人那边走：强制位移（画面跟着走），配跑步动作
        let ms = sim.get_entity(entity).map_or(0, |e| e.stat().move_speed) as f64 * (100 + CARRY_MS_PCT) as f64 / 100.0;
        if let Some(home) = Self::home_point(sim, entity, team, me) {
            if let Some(step) = carry_step(me, home, ms * CARRY_TICKS as f64) {
                let len = (step.0 * step.0 + step.1 * step.1).sqrt();
                let ticks = ((len / ms.max(1.0)).ceil() as u64).clamp(1, CARRY_TICKS as u64);
                force_move(sim, entity, step, ticks);
                let mut pose = CcV1::of_kind(CcKindV1::Animation, ticks);
                pose.set_name("run");
                sim.apply_cc(entity, &pose);
                dir = unit(step).unwrap_or(dir);
            }
        }
        self.carry = Some(Carry { victim, since: tick, until: tick + CARRY_TICKS, dir });
    }

    /// 摔棺：伤害、眩晕、画面和声音。
    fn slam(&mut self, sim: &mut StableSim<'_>, entity: usize, victim: usize, max_hp: usize) {
        sim.play_view_effect("abysspact_undertaker_drop", entity, &InputTargetV1::target(victim), 0, 0, 0);
        sim.play_sfx("abysspact_undertaker_coffin_drop", entity, &InputTargetV1::target(victim));
        sim.deal_damage_typed(entity, victim, slam_damage(max_hp), DamageTypeV1::Ad, AttackTypeV1::Skill);
        sim.apply_cc(victim, &CcV1::stun(SLAM_STUN));
    }

    /// 放逐结束：把人放到他脚下，甩到他身前，再摔。
    fn drop_out(&mut self, sim: &mut StableSim<'_>, entity: usize, c: Carry, at: (u64, u64), max_hp: usize) {
        self.carry = None;
        sim.entity_remove_buff(entity, CARRYING);
        sim.entity_set_pos(c.victim, at.0, at.1);
        force_move(sim, c.victim, (c.dir.0 * THROW_DIST, c.dir.1 * THROW_DIST), THROW_TICKS);
        self.slam(sim, entity, c.victim, max_hp);
    }

    fn give_up(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        self.carry = None;
        sim.entity_remove_buff(entity, CARRYING);
    }
}

impl StablePassive for UndertakerPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.shield_applied = false;
        self.guard_ready_at = 0;
        self.guard_armed = false;
        self.carry = None;
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(
        &mut self,
        sim: &mut StableSim<'_>,
        _player: usize,
        entity: usize,
        target: usize,
        _damage: &mut usize,
    ) {
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, attacker: usize, _damage: usize) {
        if !self.guard_armed {
            return;
        }
        let Some(team) = sim.get_entity(entity).map(|e| e.team()) else { return };
        let skill_hit = sim.get_entity(attacker).is_some_and(|a| {
            a.is_champion()
                && a.team() != team
                && [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult]
                    .into_iter()
                    .any(|s| a.cooldown(s).is_some_and(|c| just_cast(c.remaining, c.cooltime)))
        });
        if !skill_hit {
            return;
        }
        // 这一下技能伤害已经按 -30% 算过了：护挡用掉，8 秒后再备
        sim.entity_remove_buff(entity, SKILL_GUARD);
        self.guard_armed = false;
        self.guard_ready_at = sim.tick() + GUARD_CD;
        sim.play_view_effect("abysspact_undertaker_guard", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_undertaker_guard", entity, &InputTargetV1::target(entity));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.carry = None;
        self.shield_applied = false;
        self.guard_armed = false;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, team, at)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.team(), e.pos())) else {
            return;
        };
        if !alive {
            return;
        }
        let tick = sim.tick();

        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 1. 被动「棺盾」：普攻 -15% 常驻；技能护挡 8 秒备一层
        if !self.shield_applied {
            let mut base = BuffV1::named(COFFIN_SHIELD);
            base.base_attack_damaged_reduce = 15;
            sim.add_buff(entity, &base);
            self.shield_applied = true;
        }
        if !self.guard_armed && tick >= self.guard_ready_at {
            let mut g = BuffV1::named(SKILL_GUARD);
            g.skill_damaged_reduce = 30;
            sim.entity_remove_buff(entity, SKILL_GUARD);
            sim.add_buff(entity, &g);
            self.guard_armed = true;
        }

        // 2. 大招：数据在敌方英雄身上挂了 coffin_ask
        if self.carry.is_none() {
            let mut found = None;
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_champion() && e.is_alive() && e.team() != team && has_buff(sim, e.id(), COFFIN_ASK) {
                    found = Some(e.id());
                    break;
                }
            }
            if let Some(victim) = found {
                self.start_carry(sim, entity, victim, team, at);
            }
        }

        // 3. 扛着：到点（或被韧性提前放出来）就摔
        if let Some(c) = self.carry {
            match sim.get_entity(c.victim).map(|e| (e.is_alive(), e.is_targetable(), e.hp().1)) {
                Some((true, targetable, max_hp)) => {
                    let out_early = targetable && tick > c.since + 2;
                    if tick < c.until && !out_early {
                        return;
                    }
                    if !targetable && tick < c.until + OUT_GRACE {
                        return;
                    }
                    self.drop_out(sim, entity, c, at, max_hp);
                }
                _ => self.give_up(sim, entity),
            }
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_undertaker:coffin", UndertakerPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn coffin_slam_scales_with_8pct_target_max_hp() {
        assert_eq!(slam_damage(1000), 230);
        assert_eq!(slam_damage(2500), 350);
    }

    #[test]
    fn the_guard_is_spent_only_on_a_fresh_skill() {
        // 冷却 600 的技能刚放出去 1 秒：算
        assert!(just_cast(540, 600));
        assert!(just_cast(600 - GUARD_RECENT, 600));
        // 放出去 3 秒了、冷却好了、没有这一栏：不算
        assert!(!just_cast(420, 600));
        assert!(!just_cast(0, 600));
        assert!(!just_cast(0, 0));
    }

    #[test]
    fn the_carry_stops_short_of_the_allies() {
        let s = carry_step((0.0, 0.0), (100_000.0, 0.0), 150_000.0).expect("walks");
        assert!((s.0 - (100_000.0 - HOME_STOP)).abs() < 1e-6 && s.1.abs() < 1e-6, "{s:?}");
        // 走不了那么远：走满 max_len
        let s = carry_step((0.0, 0.0), (0.0, 300_000.0), 120_000.0).expect("walks");
        assert!((s.1 - 120_000.0).abs() < 1e-6, "{s:?}");
        // 已经在队友身边：不走
        assert_eq!(carry_step((0.0, 0.0), (10_000.0, 0.0), 150_000.0), None);
    }
}
