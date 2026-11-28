//! 入殓 (`abysspact_undertaker`) · 抬棺人 · 打野坦克
//!
//! 被动「棺盾」：普攻伤害常驻 -15%（`coffin_shield`）；每 8 秒备好一层技能护挡（`skill_guard`，技能伤害 -30%，挂着时
//! 引擎自己只减技能伤害）。护挡只在敌方英雄的技能打中他时用掉，用掉时棺材一闪。打中的那一刻认不出是不是技能：
//! 冷却在出招动作结束时才开始走，大多数技能打中他时对方的这一格冷却还是 0。所以挨了敌方英雄一下先记着（那一刻对方
//! 四格的冷却），之后 1 秒内对方哪一格的冷却从 0 跳起来：技能格就用掉护挡，普攻格就是普攻、丢掉这条。动作结束以后才落地的
//! 一下（弹道、延时）打中时对方技能格的冷却已经刚走起来（1 秒内），当场用掉。
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
// 写死的技能距离在大地图版跟着乘 1.3
use game_places::skill_scale::sk;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, has_buff};

pub const HERO: &str = "abysspact_undertaker";
pub const COFFIN_SHIELD: &str = "abysspact_undertaker_coffin_shield";
pub const SKILL_GUARD: &str = "abysspact_undertaker_skill_guard";
pub const COFFIN_ASK: &str = "abysspact_undertaker_coffin_ask";
pub const CARRYING: &str = "abysspact_undertaker_carrying";
pub const R_CAST_VOICE: &str = "abysspact_undertaker_r_voice";

pub const GUARD_CD: usize = 480; // 8.0s
/// 对方某一格技能的冷却开始走了这么多 tick 以内，打中他的这一下算那个技能的（动作结束后还在飞的弹道）。
pub const GUARD_RECENT: usize = 60;
/// 挨了一下以后等多久看对方哪一格的冷却跳起来（出招动作剩下的时间）。
pub const DECIDE_WINDOW: usize = 60;
/// 最多记几下。
const MAX_HITS: usize = 16;
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

/// 出手的人这一格技能的冷却刚走起来（动作刚结束）：动作结束以后才落地的弹道打中他时用。
pub fn just_cast(remaining: usize, cooltime: usize) -> bool {
    remaining > 0 && cooltime > 0 && remaining + GUARD_RECENT >= cooltime
}

/// 记下的那一下后来认出是什么。`before` / `now` 是对方（普攻、技能一、技能二、大招）四格剩下的冷却：
/// 某个技能格从 0 跳起来 → 是技能（Some(true)）；普攻格从 0 跳起来 → 是普攻（Some(false)）；都没跳 → 还不知道（None）。
pub fn hit_verdict(before: [usize; 4], now: [usize; 4]) -> Option<bool> {
    if (1..4).any(|k| before[k] == 0 && now[k] > 0) {
        return Some(true);
    }
    (before[0] == 0 && now[0] > 0).then_some(false)
}

/// 一名英雄四格的（剩下的冷却, 一轮多长）。
fn slots(sim: &StableSim<'_>, id: usize) -> Option<[(usize, usize); 4]> {
    let e = sim.get_entity(id)?;
    let mut out = [(0, 0); 4];
    for (k, s) in [SkillSlotV1::Attack, SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult].into_iter().enumerate() {
        let c = e.cooldown(s)?;
        out[k] = (c.remaining, c.cooltime);
    }
    Some(out)
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

/// 挨的敌方英雄的一下：谁打的、哪一 tick、那时对方四格剩下的冷却。
#[derive(Clone, Copy)]
struct Hit {
    attacker: usize,
    tick: usize,
    before: [usize; 4],
}

#[derive(Clone, Default)]
struct UndertakerPassive {
    voice: Voice,
    shield_applied: bool,
    guard_ready_at: usize,
    guard_armed: bool,
    hits: Vec<Hit>,
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
        force_move(sim, c.victim, (c.dir.0 * sk(THROW_DIST), c.dir.1 * sk(THROW_DIST)), THROW_TICKS);
        self.slam(sim, entity, c.victim, max_hp);
    }

    fn give_up(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        self.carry = None;
        sim.entity_remove_buff(entity, CARRYING);
    }

    /// 技能护挡用掉：8 秒后再备，棺材一闪。
    fn spend_guard(&mut self, sim: &mut StableSim<'_>, entity: usize, tick: usize) {
        sim.entity_remove_buff(entity, SKILL_GUARD);
        self.guard_armed = false;
        self.guard_ready_at = tick + GUARD_CD;
        self.hits.clear();
        sim.play_view_effect("abysspact_undertaker_guard", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_undertaker_guard", entity, &InputTargetV1::target(entity));
    }

    /// 记着的那几下：对方的冷却跳起来了就认出是技能还是普攻。
    fn judge_hits(&mut self, sim: &mut StableSim<'_>, entity: usize, tick: usize) {
        let mut waiting = Vec::new();
        let mut skill = false;
        for h in std::mem::take(&mut self.hits) {
            if tick > h.tick + DECIDE_WINDOW {
                continue;
            }
            let Some(cd) = slots(sim, h.attacker) else { continue };
            match hit_verdict(h.before, [cd[0].0, cd[1].0, cd[2].0, cd[3].0]) {
                Some(true) => skill = true,
                Some(false) => {}
                None => waiting.push(h),
            }
        }
        if skill {
            self.spend_guard(sim, entity, tick);
        } else {
            self.hits = waiting;
        }
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
        self.hits.clear();
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
        if !sim.get_entity(attacker).is_some_and(|a| a.is_champion() && a.team() != team) {
            return;
        }
        let Some(cd) = slots(sim, attacker) else { return };
        let tick = sim.tick();
        // 动作结束以后才落地的技能（技能格的冷却刚走起来）：当场用掉
        if (1..4).any(|k| just_cast(cd[k].0, cd[k].1)) {
            self.spend_guard(sim, entity, tick);
            return;
        }
        // 还在对方的出招动作里：先记着，等对方哪一格的冷却跳起来再认
        if self.hits.len() >= MAX_HITS {
            self.hits.remove(0);
        }
        self.hits.push(Hit { attacker, tick, before: [cd[0].0, cd[1].0, cd[2].0, cd[3].0] });
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
        self.hits.clear();
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
        if self.guard_armed && !self.hits.is_empty() {
            self.judge_hits(sim, entity, tick);
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
    fn a_hit_inside_the_casters_action_is_judged_when_his_cooldown_starts() {
        // 技能在对方的出招动作里打中：那一刻这一格还是 0（冷却动作结束才走），当场认不出；大招还在冷却一半
        let before = [0, 0, 0, 1_800];
        let cooltime = [60, 400, 600, 3_600];
        assert!(!(1..4).any(|k| just_cast(before[k], cooltime[k])));
        // 还在动作里：谁都没跳，接着等
        assert_eq!(hit_verdict(before, [0, 0, 0, 1_790]), None);
        // 动作结束，技能二从 0 跳到 600：是技能，用掉护挡
        assert_eq!(hit_verdict(before, [0, 0, 600, 1_780]), Some(true));
        // 普攻：动作结束时普攻格从 0 跳起来，技能格没动：不用
        assert_eq!(hit_verdict(before, [60, 0, 0, 1_780]), Some(false));
        // 本来就在冷却里的格子往下走不算跳
        assert_eq!(hit_verdict([0, 300, 0, 0], [0, 290, 0, 0]), None);
    }

    #[test]
    fn a_projectile_landing_after_the_action_spends_the_guard_at_once() {
        // 冷却 600 的技能动作刚结束、弹道还在飞：打中时这一格的冷却刚走起来
        assert!(just_cast(570, 600));
        assert!(just_cast(600 - GUARD_RECENT, 600));
        // 放出去好几秒了、冷却好了、没有这一格：不算
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
