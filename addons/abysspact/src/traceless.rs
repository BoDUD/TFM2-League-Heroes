//! 无痕 (`abysspact_traceless`) · 白衣剑客 · 中路物理刺客
//!
//! - 锋：她每打中一次敌方英雄（普攻和技能都算，`on_attack` 本来就连技能一起报），只要从上一下到这一下没掉过血，
//!   就叠一层，每层攻击力 +`edge_pct`%，最多 `edge_cap` 层。打小兵野怪不叠。只要实际掉了血（护盾挡下的不算），
//!   锋全部清零，白衣溅墨。
//! - `ooc` tick 没出手也没挨打就隐身；隐身后的第一剑必定叠锋，另加 `ambush`% 伤害（只算这一份，数据里不再另加一击）。
//! - W「残影」：数据里在原生模式下是 3 tick 的 idle 动作，只挂待命 `w_arm`。待命期间要挨敌方英雄的打（或者自己血
//!   低于 `w_low`% 时挨任何敌人的打），而且身上有 `w_edge` 层以上的锋，就躲开这一下（`on_damaged` 在扣血前调，把这
//!   一下的血原样加回去）、留残影、放逐自己 `w_banish` tick（选不中），接着隐身 `w_inv` tick、加速——隐身到点就停。
//!   待命没用上就把 W 的冷却退到只剩 `keep`。
//! - R「无影」：数据只挂 `r_go`，其余都在这里：放逐自己 `r_vanish` tick；`r_range` 内每个敌方英雄由近到远各挨一剑
//!   （`r_dmg + r_ad% 攻击力`，第一剑在 `r_first` tick，余下的匀开），每剑叠锋；结束时所有剑痕一起亮，停在血最少的
//!   那个人身后 `r_behind`。放逐中的人自己的范围搜索找不到任何单位，所以伤害不交给数据的 RangeEffect。
//! - Q「一线」击杀敌方英雄立刻刷新冷却。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, kit_param, map_box, onto_map, refund_cooldown, refund_hit};

pub const HERO: &str = "abysspact_traceless";
pub const NATIVE_MARK: &str = "abysspact_traceless_native";
pub const EDGE_STAT: &str = "abysspact_traceless_edge_stat";
pub const BLADE_GLOW: &str = "abysspact_traceless_blade_glow";
pub const STEALTH_BUFF: &str = "abysspact_traceless_stealth";
pub const HASTE_BUFF: &str = "abysspact_traceless_w_haste";
pub const HOLD: &str = "abysspact_traceless_hold";
pub const Q_CAST_ASK: &str = "abysspact_traceless_q_cast";
pub const W_ARM: &str = "abysspact_traceless_w_arm";
pub const R_GO: &str = "abysspact_traceless_r_go";
pub const R_CAST_VOICE: &str = "abysspact_traceless_r_voice";

pub const Q_RESET_WINDOW: usize = 45; // Q 出手后 0.75 秒内的击杀算 Q 的

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub edge_pct: usize,
    pub edge_cap: usize,
    pub ambush: usize,
    pub ooc: usize,
    pub w_arm: usize,
    pub w_edge: usize,
    pub w_low: usize,
    pub w_banish: usize,
    pub w_inv: usize,
    pub w_ms: usize,
    pub r_dmg: usize,
    pub r_ad: usize,
    pub r_vanish: usize,
    pub r_range: usize,
    pub r_first: usize,
    pub r_behind: usize,
    pub keep: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            edge_pct: 7, edge_cap: 8, ambush: 50, ooc: 90,
            w_arm: 300, w_edge: 2, w_low: 35, w_banish: 45, w_inv: 60, w_ms: 26,
            r_dmg: 138, r_ad: 104, r_vanish: 90, r_range: 55_000, r_first: 18, r_behind: 9_000, keep: 60,
        }
    }
}

impl Params {
    pub fn parse(json: &str) -> Self {
        let d = Self::default();
        let g = |k: &str, v: usize| kit_param(json, k).unwrap_or(v);
        Self {
            edge_pct: g("edge_pct", d.edge_pct), edge_cap: g("edge_cap", d.edge_cap), ambush: g("ambush", d.ambush),
            ooc: g("ooc", d.ooc), w_arm: g("w_arm", d.w_arm), w_edge: g("w_edge", d.w_edge), w_low: g("w_low", d.w_low),
            w_banish: g("w_banish", d.w_banish), w_inv: g("w_inv", d.w_inv), w_ms: g("w_ms", d.w_ms),
            r_dmg: g("r_dmg", d.r_dmg), r_ad: g("r_ad", d.r_ad), r_vanish: g("r_vanish", d.r_vanish),
            r_range: g("r_range", d.r_range), r_first: g("r_first", d.r_first), r_behind: g("r_behind", d.r_behind),
            keep: g("keep", d.keep),
        }
    }
}

pub fn edge_attack_mult(p: &Params, stacks: u8) -> i32 {
    (stacks.min(p.edge_cap as u8) as i32) * p.edge_pct as i32
}

/// R 的每一剑什么时候落：第一剑 `r_first`，最后一剑离放逐结束留 10 tick，中间匀开。
pub fn cut_times(p: &Params, start: usize, n: usize) -> Vec<usize> {
    let last = p.r_vanish.saturating_sub(10).max(p.r_first);
    let gap = if n > 1 { (last - p.r_first) / (n - 1) } else { 0 };
    (0..n).map(|i| start + p.r_first + i * gap).collect()
}

/// 停在 `target` 身后：从她起手的地方看过去，过 `behind` 远。
pub fn behind(origin: (u64, u64), target: (u64, u64), behind: f64) -> (f64, f64) {
    let (dx, dy) = (target.0 as f64 - origin.0 as f64, target.1 as f64 - origin.1 as f64);
    let len = dx.hypot(dy);
    if len < 1.0 {
        return (target.0 as f64 + behind, target.1 as f64);
    }
    (target.0 as f64 + dx / len * behind, target.1 as f64 + dy / len * behind)
}

#[derive(Clone)]
struct RPlan {
    cuts: Vec<(usize, usize)>,
    hit: Vec<usize>,
    end: usize,
    origin: (u64, u64),
}

#[derive(Clone, Default)]
struct TracelessPassive {
    p: Params,
    voice: Voice,
    native_marked: bool,
    edge: u8,
    shown_edge: u8,
    last_hp: usize,
    last_combat_tick: usize,
    stealthed: bool,
    /// W 给的隐身到这一 tick 停。
    stealth_until: Option<usize>,
    ambush_ready: bool,
    q_cast_tick: usize,
    w_armed: Option<usize>,
    owed: usize,
    /// R 的剑正在结算：`on_attack` 别再叠一次锋、别吃伏击加成。
    cutting: bool,
    r: Option<RPlan>,
}

impl TracelessPassive {
    fn sync_edge(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if self.shown_edge == self.edge {
            return;
        }
        sim.entity_remove_buff(entity, EDGE_STAT);
        sim.entity_remove_buff(entity, BLADE_GLOW);
        for k in 1..=8u8 {
            sim.entity_remove_buff(entity, &format!("abysspact_traceless_edge_{k}"));
        }
        if self.edge > 0 {
            let mut st = BuffV1::named(EDGE_STAT);
            st.attack_mult = edge_attack_mult(&self.p, self.edge);
            sim.add_buff(entity, &st);
            sim.add_buff(entity, &BuffV1::named(BLADE_GLOW));
            sim.add_buff(entity, &BuffV1::named(&format!("abysspact_traceless_edge_{}", self.edge.min(8))));
        }
        self.shown_edge = self.edge;
    }

    fn gain_edge(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        let next = self.edge.saturating_add(1).min(self.p.edge_cap as u8);
        if next != self.edge {
            self.edge = next;
            self.sync_edge(sim, entity);
            sim.play_sfx("abysspact_traceless_stack", entity, &InputTargetV1::target(entity));
        }
    }

    fn shatter_edge(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if self.edge == 0 {
            return;
        }
        self.edge = 0;
        self.sync_edge(sim, entity);
        sim.play_view_effect("abysspact_traceless_ink", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_view_effect("abysspact_traceless_quench", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_traceless_ink", entity, &InputTargetV1::target(entity));
        sim.play_sfx("abysspact_traceless_quench", entity, &InputTargetV1::target(entity));
    }

    fn break_stealth(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if self.stealthed {
            self.stealthed = false;
            self.stealth_until = None;
            sim.entity_remove_buff(entity, STEALTH_BUFF);
        }
    }

    fn pay_owed(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if self.owed == 0 {
            return;
        }
        let owed = std::mem::take(&mut self.owed);
        let Some((now, max)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        let hp = now.saturating_add(owed).min(max);
        if hp > now {
            sim.entity_set_hp(me, hp);
        }
    }

    /// W：躲开这一下，留残影，放逐一下再隐身加速。
    fn dodge(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        let p = self.p;
        let pos = sim.get_entity(me).map(|e| e.pos()).unwrap_or((0, 0));
        sim.entity_banish(me, me, p.w_banish, "", "");
        let mut haste = BuffV1::timed(HASTE_BUFF, p.w_banish + p.w_inv);
        haste.move_speed_mult = p.w_ms as i32;
        sim.entity_remove_buff(me, HASTE_BUFF);
        sim.add_buff(me, &haste);
        sim.entity_set_invisible(me, p.w_banish + p.w_inv);
        sim.entity_remove_buff(me, STEALTH_BUFF);
        sim.add_buff(me, &BuffV1::timed(STEALTH_BUFF, p.w_banish + p.w_inv));
        self.stealthed = true;
        self.stealth_until = Some(tick + p.w_banish + p.w_inv);
        self.ambush_ready = true;
        let at = InputTargetV1::pos(pos.0, pos.1);
        sim.play_view_effect("abysspact_traceless_afterimage", me, &at, 0, 0, 0);
        sim.play_sfx("abysspact_traceless_foley_w", me, &at);
        sim.play_sfx("abysspact_traceless_w_dodge", me, &at);
    }

    fn start_r(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (u64, u64), tick: usize) {
        let r2 = (self.p.r_range as u64).saturating_mul(self.p.r_range as u64);
        let mut foes: Vec<(usize, u64)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| e.is_champion() && e.is_alive() && e.team() != team && e.is_targetable())
            .map(|e| (e.id(), dist_sq(pos, e.pos())))
            .filter(|&(_, d2)| d2 <= r2)
            .collect();
        foes.sort_by_key(|&(_, d2)| d2);
        sim.entity_banish(me, me, self.p.r_vanish, "", "");
        let times = cut_times(&self.p, tick, foes.len());
        self.r = Some(RPlan {
            cuts: times.into_iter().zip(foes.iter().map(|&(id, _)| id)).collect(),
            hit: Vec::new(),
            end: tick + self.p.r_vanish,
            origin: pos,
        });
    }

    fn run_r(&mut self, sim: &mut StableSim<'_>, me: usize, ad: usize, tick: usize) {
        let Some(mut plan) = self.r.take() else { return };
        let due: Vec<(usize, usize)> = plan.cuts.iter().copied().filter(|&(at, _)| at <= tick).collect();
        plan.cuts.retain(|&(at, _)| at > tick);
        for (_, t) in due {
            if !sim.get_entity(t).is_some_and(|e| e.is_alive() && e.is_targetable()) {
                continue;
            }
            let mut dmg = self.p.r_dmg + ad.saturating_mul(self.p.r_ad) / 100;
            if self.ambush_ready || self.stealthed {
                self.break_stealth(sim, me);
                self.ambush_ready = false;
                dmg += dmg * self.p.ambush / 100;
            }
            self.cutting = true;
            sim.deal_damage_typed(me, t, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
            self.cutting = false;
            self.last_combat_tick = tick;
            self.gain_edge(sim, me);
            sim.play_view_effect("abysspact_traceless_cut", me, &InputTargetV1::target(t), 0, 0, 0);
            sim.play_sfx("abysspact_traceless_r_cut", me, &InputTargetV1::target(t));
            plan.hit.push(t);
        }
        if tick < plan.end {
            self.r = Some(plan);
            return;
        }
        // 收剑：所有剑痕一起亮，停在血最少的那个人身后
        let alive: Vec<(usize, usize, (u64, u64))> = plan
            .hit
            .iter()
            .filter_map(|&t| sim.get_entity(t).filter(|e| e.is_alive()).map(|e| (t, e.hp().0, e.pos())))
            .collect();
        for &(t, _, _) in &alive {
            sim.play_view_effect("abysspact_traceless_cut_final", me, &InputTargetV1::target(t), 0, 0, 0);
        }
        if let Some(&(_, _, at)) = alive.iter().min_by_key(|&&(_, hp, _)| hp) {
            let goal = behind(plan.origin, at, self.p.r_behind as f64);
            let dest = onto_map(map_box(sim), goal.0, goal.1);
            sim.entity_set_pos(me, dest.0, dest.1);
        }
        sim.play_sfx("abysspact_traceless_r_final", me, &InputTargetV1::target(me));
        self.last_combat_tick = tick;
    }
}

impl StablePassive for TracelessPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = Params::parse(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.native_marked = false;
        self.edge = 0;
        self.shown_edge = 0;
        self.last_hp = sim.get_entity(entity).map(|e| e.hp().0).unwrap_or(0);
        self.last_combat_tick = sim.tick();
        self.stealthed = false;
        self.stealth_until = None;
        self.ambush_ready = false;
        self.q_cast_tick = 0;
        self.w_armed = None;
        self.owed = 0;
        self.cutting = false;
        self.r = None;
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, target: usize, damage: &mut usize) {
        if self.cutting {
            return;
        }
        self.last_combat_tick = sim.tick();
        if !sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            self.break_stealth(sim, entity);
            self.ambush_ready = false;
            return;
        }
        self.voice.play(sim, HERO, entity, Cue::Start);
        let cur_hp = sim.get_entity(entity).map(|e| e.hp().0).unwrap_or(0);
        if self.ambush_ready || self.stealthed {
            // 隐身后的第一剑：必定叠锋，另加伤害
            self.break_stealth(sim, entity);
            self.ambush_ready = false;
            *damage = damage.saturating_add(damage.saturating_mul(self.p.ambush) / 100);
            self.gain_edge(sim, entity);
            self.last_hp = cur_hp;
        } else if cur_hp >= self.last_hp {
            self.gain_edge(sim, entity);
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, attacker: usize, damage: usize) {
        self.pay_owed(sim, entity);
        if damage == 0 {
            return;
        }
        let tick = sim.tick();
        let Some((team, cur_hp, max_hp)) = sim.get_entity(entity).map(|e| (e.team(), e.hp().0, e.hp().1)) else { return };
        let (foe, champ) = sim
            .get_entity(attacker)
            .map(|a| (a.team() != team, a.is_champion()))
            .unwrap_or((false, false));
        let low = max_hp > 0 && cur_hp.saturating_mul(100) < max_hp.saturating_mul(self.p.w_low);
        let worth = self.edge as usize >= self.p.w_edge || low;
        if self.w_armed.is_some_and(|t| tick < t) && foe && (champ || low) && worth {
            // W：躲开这一下（这一下还没扣血，原样加回去）
            self.w_armed = None;
            let (set, owed, lethal) = refund_hit(cur_hp, max_hp, damage, damage);
            if set != cur_hp {
                sim.entity_set_hp(entity, set);
            }
            if lethal {
                let mut hold = BuffV1::timed(HOLD, 2);
                hold.undying = true;
                sim.add_buff(entity, &hold);
            }
            self.owed += owed;
            self.last_combat_tick = tick;
            self.dodge(sim, entity, tick);
            return;
        }
        self.last_combat_tick = tick;
        self.break_stealth(sim, entity);
        self.ambush_ready = false;
        // 这一下还没扣血，掉没掉血下一 tick 的 on_update 才看得到（护盾挡下的不算）
        if cur_hp < self.last_hp {
            self.shatter_edge(sim, entity);
        }
        self.last_hp = cur_hp;
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
            if sim.tick() <= self.q_cast_tick + Q_RESET_WINDOW {
                sim.entity_reduce_cooldown(entity, SkillSlotV1::Skill, 10_000);
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.edge = 0;
        self.shown_edge = 0;
        self.stealthed = false;
        self.stealth_until = None;
        self.ambush_ready = false;
        self.w_armed = None;
        self.owed = 0;
        self.r = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        self.pay_owed(sim, entity);
        let Some((alive, team, pos, cur_hp, ad)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.hp().0, e.stat().attack))
        else {
            return;
        };
        if !alive {
            return;
        }
        let tick = sim.tick();

        if !self.native_marked {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
            self.native_marked = true;
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }
        if consume_buff(sim, entity, Q_CAST_ASK) {
            self.q_cast_tick = tick;
            self.last_combat_tick = tick;
        }
        if consume_buff(sim, entity, W_ARM) {
            self.w_armed = Some(tick + self.p.w_arm);
        }
        if self.w_armed.is_some_and(|t| tick >= t) {
            self.w_armed = None;
            refund_cooldown(sim, entity, SkillSlotV1::Skill2, self.p.keep);
        }
        if consume_buff(sim, entity, R_GO) && self.r.is_none() {
            self.start_r(sim, entity, team, pos, tick);
        }
        if self.r.is_some() {
            self.run_r(sim, entity, ad, tick);
        }

        // 真的掉了血（护盾挡下的不算）：锋清零
        if cur_hp < self.last_hp {
            self.last_combat_tick = tick;
            self.break_stealth(sim, entity);
            self.ambush_ready = false;
            self.shatter_edge(sim, entity);
        }
        self.last_hp = cur_hp;

        // W 的隐身到点就停
        if self.stealth_until.is_some_and(|t| tick >= t) {
            self.break_stealth(sim, entity);
        }
        // 脱战隐身
        if !self.stealthed && self.r.is_none() && tick >= self.last_combat_tick + self.p.ooc {
            self.stealthed = true;
            self.ambush_ready = true;
            sim.add_buff(entity, &BuffV1::named(STEALTH_BUFF));
        }
        if self.stealthed && self.stealth_until.is_none() && tick % 12 == 0 {
            sim.entity_set_invisible(entity, 18);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_traceless:spotless", TracelessPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn edge_scales_seven_percent_up_to_eight_stacks() {
        let p = Params::default();
        assert_eq!(edge_attack_mult(&p, 0), 0);
        assert_eq!(edge_attack_mult(&p, 4), 28);
        assert_eq!(edge_attack_mult(&p, 8), 56);
        assert_eq!(edge_attack_mult(&p, 12), 56);
    }

    #[test]
    fn one_cut_each_inside_the_vanish_and_the_stop_is_behind() {
        let p = Params::default();
        let t = cut_times(&p, 100, 5);
        assert_eq!(t.len(), 5);
        assert_eq!(t[0], 100 + p.r_first);
        assert!(t[4] <= 100 + p.r_vanish - 10);
        assert!(t.windows(2).all(|w| w[0] < w[1]));
        assert_eq!(cut_times(&p, 0, 1), vec![p.r_first]);
        // 从左边过来，停在右边
        assert_eq!(behind((0, 0), (10_000, 0), 9_000.0), (19_000.0, 0.0));
    }

    #[test]
    fn params_come_from_the_kit_file() {
        assert_eq!(Params::parse(&crate::kit_params_of(include_str!(
            "../../../abysspact/champion/abysspact_traceless.data_champion"
        ))), Params::default());
    }
}
