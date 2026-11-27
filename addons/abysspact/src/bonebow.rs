//! 骸弦 (`abysspact_bonebow`) · 骨弓手 · 下路射手
//!
//! 招牌机制「亡兵」真实骷髅兵召唤 + W「葬礼」全军冲锋自爆 + R「亡军」5 骷髅列阵:
//! - 每第 4 支箭在目标身边拉起一名真实骷髅兵（`sim.spawn_unit("abysspact_skeleton", ...)`）：继承骸弦 30% 攻击力，
//!   持续 6 秒（360 ticks），常规上限 3 个。数的是箭：普攻的箭打中时数据给她挂 `a_shot`，Q 放出去时挂 `q_arrow`
//!   （以前数的是 on_attack——技能的每一下伤害都算，Q 穿过一线兵、W 和 R 的范围、骷髅兵自爆都在加数）。
//! - Q 穿骨每命中一个敌方英雄，在他身边再拉起一名（数据给他挂 `q_hit_ask`）。
//! - R「亡军」：箭射出去时数据给她挂 `r_ask`、给大招的目标挂 `r_aim`；本被动记下目标的位置，箭雨落地那一 tick
//!   在那里爬出 5 名骷髅兵（8 秒，不计入常规上限）。以前每个被箭雨打中的敌人身上也挂 `r_ask`，每 tick 认一个、
//!   每次拉 5 个，一场团战能爬出三十几个。
//! - 骷髅兵爬出来时播它图里的 `spawn`（从地里拼起来），用动画控制播，播完才走动。
//! - W「葬礼」：活着的骷髅兵（生成满 2 tick 的）强制位移冲向她的目标，到了才自爆：每个在落点 1.5 万内造成
//!   `40 + 50% AD` 物理伤害；减速 30% 1 秒，一次葬礼每人只减一次（以前每炸一下叠一层，几个一起炸就钉死在原地）。
//! - 生成、冲锋的落点都收在地图里（看全部单位所在的范围），不会落到地图外面。

use std::collections::HashSet;

use mod_api_stable::*;
// 写死的技能距离在大地图版跟着乘 1.3
use game_places::skill_scale::sk;

use crate::voice::{Cue, Voice};
use crate::{buffs_present, consume_buff, dist_sq, foe_champions};

pub const HERO: &str = "abysspact_bonebow";
pub const UNIT_NAME: &str = "abysspact_skeleton";
pub const A_SHOT: &str = "abysspact_bonebow_a_shot";
pub const Q_ARROW: &str = "abysspact_bonebow_q_arrow";
pub const Q_HIT_ASK: &str = "abysspact_bonebow_q_hit_ask";
pub const W_CMD: &str = "abysspact_bonebow_w_cmd";
pub const W_MARK: &str = "abysspact_bonebow_w_mark";
pub const W_SLOW: &str = "abysspact_bonebow_w_slow";
pub const R_ASK: &str = "abysspact_bonebow_r_ask";
pub const R_AIM: &str = "abysspact_bonebow_r_aim";
pub const R_CAST_VOICE: &str = "abysspact_bonebow_r_voice";

pub const NORMAL_CAP: usize = 3;
pub const NORMAL_LIFE: u64 = 360; // 6.0s
pub const ULT_LIFE: u64 = 480;    // 8.0s
pub const ULT_COUNT: usize = 5;
pub const ARROWS_PER_SKELETON: usize = 4;
pub const FUNERAL_RADIUS: u64 = 15_000; // 1.5万
pub const FUNERAL_BASE: usize = 40;
pub const FUNERAL_AD_PCT: usize = 50;
pub const FUNERAL_SLOW: i32 = -30;
pub const FUNERAL_SLOW_TICKS: usize = 60;
/// 葬礼冲锋：每 tick 冲多远、最少几 tick。
pub const CHARGE_SPEED: u64 = 3_000;
/// 新生成的骷髅兵满这么多 tick 才听葬礼的号令（生成那一拍和下一拍它的属性还没站稳）。
pub const MIN_AGE: usize = 2;
/// 生成后这么多 tick 内读不到它也先留着（宿主可能 tick 结束才把它加进来）。
pub const LOOK_GRACE: usize = 3;
/// 爬出来的动画（`spawn`，8 帧 × 0.08 秒）。
pub const RISE_TICKS: u64 = 38;
/// 箭射出去到箭雨落地（数据里大招的 lob 飞 12 tick，落地后 1 tick 的圈）。
pub const R_LAND_DELAY: usize = 13;

pub fn skeleton_stat(ad: usize, owner_max_hp: usize) -> StatV1 {
    StatV1 {
        attack: (ad.saturating_mul(30) / 100).max(20),
        magic_power: 0,
        hp: (owner_max_hp.saturating_mul(24) / 100).max(180),
        defence: 16,
        magic_resistance: 16,
        move_speed: 1120,
        hp_regen: 0,
        stack: 0,
        crit_chance: 0,
    }
}

/// 骷髅兵的普攻：28 tick 一个动作，第 21 tick（图里第 7 帧，剑刺出去那一帧）打中。
pub fn skeleton_attack() -> UnitAttackV1 {
    UnitAttackV1 {
        attack_ratio: 100,
        attack: 0,
        range: 14_000,
        cooltime: 54,
        duration: 28,
        start_timing: 21,
        cancelable: false,
        attack_type: AttackTypeV1::BaseAttack.code(),
    }
}

pub fn funeral_damage(ad: usize) -> usize {
    FUNERAL_BASE + ad.saturating_mul(FUNERAL_AD_PCT) / 100
}

/// 5 offsets around a point (radius 13_000) for R「亡军」skeleton formation.
pub fn ring_offsets(idx: usize) -> (i64, i64) {
    const OFF: [(i64, i64); 5] = [
        (13_000, 0),
        (4_000, 12_400),
        (-10_500, 7_600),
        (-10_500, -7_600),
        (4_000, -12_400),
    ];
    OFF[idx % OFF.len()]
}

/// 全部单位所在的范围（左上、右下）：引擎自己放单位的地方。
fn field(sim: &StableSim<'_>) -> Option<((u64, u64), (u64, u64))> {
    (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).map(|e| e.pos()).fold(None, |b, p| {
        Some(match b {
            None => (p, p),
            Some((lo, hi)) => ((lo.0.min(p.0), lo.1.min(p.1)), (hi.0.max(p.0), hi.1.max(p.1))),
        })
    })
}

/// `p` 挪 `off`，再收进 `field` 里（没有范围时只保证不出左上边）。
pub fn place(p: (u64, u64), off: (i64, i64), field: Option<((u64, u64), (u64, u64))>) -> (u64, u64) {
    let x = (p.0 as i64).saturating_add(off.0).max(0) as u64;
    let y = (p.1 as i64).saturating_add(off.1).max(0) as u64;
    match field {
        Some((lo, hi)) => (x.clamp(lo.0, hi.0.max(lo.0)), y.clamp(lo.1, hi.1.max(lo.1))),
        None => (x, y),
    }
}

/// 冲锋：从 `from` 到 `to` 要几 tick、每 tick 多快（强制位移的参数）。
pub fn charge(from: (u64, u64), to: (u64, u64)) -> (u64, u64) {
    let d = (dist_sq(from, to) as f64).sqrt();
    let ticks = (d / sk(CHARGE_SPEED) as f64).ceil().max(1.0) as u64;
    let speed = (d / ticks as f64).ceil() as u64;
    (ticks, speed)
}

#[derive(Clone, Copy, Debug, PartialEq)]
struct Skel {
    id: usize,
    born: usize,
}

#[derive(Clone, Copy, Debug)]
struct Charge {
    id: usize,
    at: usize,
    to: (u64, u64),
}

#[derive(Clone, Default)]
struct BonebowPassive {
    voice: Voice,
    arrows: usize,
    /// 她最近打的目标（不含塔）：葬礼、亡军找落点用。
    last_target: Option<usize>,
    /// 她最近一箭射的目标（塔也算）：第 4 支箭在它身边拉起骷髅兵。
    arrow_target: Option<usize>,
    /// Live normal skeletons (capped at 3, oldest despawned when overflowing).
    normal_skels: Vec<Skel>,
    /// Live ult skeletons (uncapped, live 8s).
    ult_skels: Vec<Skel>,
    /// 箭雨落地时爬出亡军：(哪一 tick, 在哪)。
    army_at: Option<(usize, (u64, u64))>,
    /// 爬出来的动画在哪一 tick 给它播（生成后一拍）。
    rises: Vec<(usize, usize)>,
    /// 冲锋中的骷髅兵：到了就炸。
    charges: Vec<Charge>,
    /// 这一次葬礼已经减过速的人。
    slowed: HashSet<usize>,
    /// 上一次看到的 tick：变小了就是新的一局（被动实例可能被下一局接着用）。
    last_tick: usize,
}

/// 这个骷髅兵还记着吗：生成不久（读不到也先留着）或者还活着。生在「以后」的（上一局记下的，这一局 tick 从头算）不要：
/// 那个单位号这一局可能是别的单位，留着会被当成骷髅兵杀掉。
pub fn keep_skel(born: usize, tick: usize, alive: bool) -> bool {
    born <= tick && (tick < born + LOOK_GRACE || alive)
}

impl BonebowPassive {
    /// 新的一局：上一局的骷髅兵、要播的动画、冲锋、箭数都不要了。
    fn forget(&mut self) {
        self.normal_skels.clear();
        self.ult_skels.clear();
        self.rises.clear();
        self.charges.clear();
        self.army_at = None;
        self.slowed.clear();
        self.arrows = 0;
        self.last_target = None;
        self.arrow_target = None;
    }

    fn prune_dead(&mut self, sim: &StableSim<'_>, tick: usize) {
        let keep = |s: &Skel| keep_skel(s.born, tick, sim.get_entity(s.id).is_some_and(|e| e.is_alive()));
        self.normal_skels.retain(keep);
        self.ult_skels.retain(keep);
    }

    #[allow(clippy::too_many_arguments)]
    fn spawn_one(
        &mut self,
        sim: &mut StableSim<'_>,
        owner: usize,
        team: usize,
        at: (u64, u64),
        ad: usize,
        owner_max_hp: usize,
        is_ult: bool,
    ) {
        let tick = sim.tick();
        self.prune_dead(sim, tick);
        if !is_ult {
            while self.normal_skels.len() >= NORMAL_CAP {
                let oldest = self.normal_skels.remove(0);
                if sim.get_entity(oldest.id).is_some_and(|e| e.is_alive()) {
                    sim.entity_set_hp(oldest.id, 0);
                }
            }
        }
        let stat = skeleton_stat(ad, owner_max_hp);
        let atk = skeleton_attack();
        let life = if is_ult { ULT_LIFE } else { NORMAL_LIFE };
        if let Some(uid) = sim.spawn_unit(UNIT_NAME, owner, team, at.0, at.1, life, &stat, &atk) {
            if uid == owner {
                return;
            }
            let s = Skel { id: uid, born: tick };
            if is_ult {
                self.ult_skels.push(s);
            } else {
                self.normal_skels.push(s);
            }
            self.rises.push((uid, tick + 1));
            sim.play_view_effect("abysspact_bonebow_crypt", owner, &InputTargetV1::pos(at.0, at.1), 0, 0, 0);
            sim.play_sfx("abysspact_bonebow_skeleton_rise", owner, &InputTargetV1::pos(at.0, at.1));
        }
    }

    /// 普攻的箭、Q 的箭各算一支，第 4 支在目标身边拉起一个。
    fn count_arrow(&mut self, sim: &mut StableSim<'_>, owner: usize, team: usize, ad: usize, max_hp: usize) {
        self.arrows += 1;
        if self.arrows % ARROWS_PER_SKELETON != 0 {
            return;
        }
        let Some(tpos) = self.arrow_target.and_then(|t| sim.get_entity(t)).filter(|e| e.is_alive()).map(|e| e.pos())
        else {
            return;
        };
        let at = place(tpos, (8_000, 0), field(sim));
        self.spawn_one(sim, owner, team, at, ad, max_hp, false);
    }

    /// 葬礼：每个生成满 2 tick 的骷髅兵冲向集合点，到了再炸。
    fn start_funeral(&mut self, sim: &mut StableSim<'_>, owner: usize, team: usize, my_pos: (u64, u64)) {
        let tick = sim.tick();
        self.prune_dead(sim, tick);
        // 集合点：W 打中的英雄 → 她最近打的目标 → 8 万内最近的敌人（英雄优先）
        let mut rally: Option<(u64, u64)> = None;
        for (id, pos) in foe_champions(sim, team) {
            let [marked] = buffs_present(sim, id, [W_MARK]);
            if marked {
                rally = Some(pos);
                sim.entity_remove_buff(id, W_MARK);
                break;
            }
        }
        if rally.is_none() {
            rally = self
                .last_target
                .and_then(|lt| sim.get_entity(lt))
                .filter(|e| e.is_alive() && e.team() != team)
                .map(|e| e.pos());
        }
        if rally.is_none() {
            let mut best: Option<(u64, (u64, u64))> = None;
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_alive() || e.team() == team || e.is_tower() {
                    continue;
                }
                let d2 = dist_sq(my_pos, e.pos());
                if d2 <= 80_000 * 80_000 {
                    let score = if e.is_champion() { d2 / 4 } else { d2 };
                    if best.is_none_or(|(bd, _)| score < bd) {
                        best = Some((score, e.pos()));
                    }
                }
            }
            rally = best.map(|(_, p)| p);
        }
        let target = rally.unwrap_or(my_pos);
        let area = field(sim);
        let ready: Vec<Skel> = self
            .normal_skels
            .iter()
            .chain(self.ult_skels.iter())
            .copied()
            .filter(|s| tick >= s.born + MIN_AGE)
            .collect();
        self.normal_skels.retain(|s| tick < s.born + MIN_AGE);
        self.ult_skels.retain(|s| tick < s.born + MIN_AGE);
        if ready.is_empty() {
            return;
        }
        self.slowed.clear();
        sim.play_sfx("abysspact_bonebow_funeral_burst", owner, &InputTargetV1::pos(target.0, target.1));
        for (idx, s) in ready.into_iter().enumerate() {
            let Some(from) = sim.get_entity(s.id).filter(|e| e.is_alive()).map(|e| e.pos()) else { continue };
            let off = ring_offsets(idx);
            let to = place(target, (off.0 / 3, off.1 / 3), area);
            let (ticks, speed) = charge(from, to);
            let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks);
            cc.dx = to.0 as i64 - from.0 as i64;
            cc.dy = to.1 as i64 - from.1 as i64;
            cc.speed = speed;
            sim.apply_cc(s.id, &cc);
            self.charges.push(Charge { id: s.id, at: tick + ticks as usize, to });
        }
    }

    /// 冲到了的骷髅兵自爆。
    fn blow_arrived(&mut self, sim: &mut StableSim<'_>, owner: usize, team: usize, ad: usize) {
        let tick = sim.tick();
        let due: Vec<Charge> = self.charges.iter().copied().filter(|c| tick >= c.at).collect();
        self.charges.retain(|c| tick < c.at);
        let dmg = funeral_damage(ad);
        let rad_sq = sk(FUNERAL_RADIUS) * sk(FUNERAL_RADIUS);
        for c in due {
            let Some(at) = sim.get_entity(c.id).filter(|e| e.is_alive()).map(|e| e.pos()) else { continue };
            // 强制位移没把它挪过去（被定住之类）就在落点炸
            let at = if dist_sq(at, c.to) > rad_sq { c.to } else { at };
            sim.play_view_effect("abysspact_bonebow_bone_burst", owner, &InputTargetV1::pos(at.0, at.1), 0, 0, 0);
            let victims: Vec<usize> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|e| e.is_alive() && e.team() != team && !e.is_tower() && dist_sq(at, e.pos()) <= rad_sq)
                .map(|e| e.id())
                .collect();
            for vid in victims {
                sim.deal_damage_typed(owner, vid, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
                if self.slowed.insert(vid) {
                    sim.entity_remove_buff(vid, W_SLOW);
                    let mut slow = BuffV1::timed(W_SLOW, FUNERAL_SLOW_TICKS);
                    slow.move_speed_mult = FUNERAL_SLOW;
                    sim.add_buff(vid, &slow);
                }
            }
            sim.entity_set_hp(c.id, 0);
        }
    }
}

impl StablePassive for BonebowPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        let tick = sim.tick();
        if tick < self.last_tick {
            self.forget();
        }
        self.last_tick = tick;
        self.army_at = None;
        self.charges.clear();
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
        let Some((is_champ, is_tower)) = sim.get_entity(target).map(|e| (e.is_champion(), e.is_tower())) else {
            return;
        };
        if is_champ {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
        self.arrow_target = Some(target);
        if !is_tower {
            self.last_target = Some(target);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        // 冲到一半她死了：骷髅兵照旧活到时间，不再炸
        self.army_at = None;
        self.charges.clear();
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        self.voice.observe(entity);
        let Some((alive, my_team, my_pos, ad, max_hp)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.stat().attack, e.hp().1))
        else {
            return;
        };
        if !alive {
            return;
        }
        let tick = sim.tick();
        if tick < self.last_tick {
            // tick 变小：新的一局用着上一局的被动实例
            self.forget();
        }
        self.last_tick = tick;

        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 0. 新骷髅兵爬出来（生成后一拍再播，生成那一拍它还没站稳）
        if !self.rises.is_empty() {
            let due: Vec<usize> = self.rises.iter().filter(|r| tick >= r.1).map(|r| r.0).collect();
            self.rises.retain(|r| tick < r.1);
            for id in due {
                if sim.get_entity(id).is_some_and(|e| e.is_alive()) {
                    let mut rise = CcV1::of_kind(CcKindV1::Animation, RISE_TICKS);
                    rise.set_name("spawn");
                    sim.apply_cc(id, &rise);
                }
            }
        }

        // 1. 数箭：普攻的箭打中、Q 的箭射出
        let [a_shot, q_arrow, r_ask, w_cmd] = buffs_present(sim, entity, [A_SHOT, Q_ARROW, R_ASK, W_CMD]);
        if a_shot {
            sim.entity_remove_buff(entity, A_SHOT);
            self.count_arrow(sim, entity, my_team, ad, max_hp);
        }
        if q_arrow {
            sim.entity_remove_buff(entity, Q_ARROW);
            self.count_arrow(sim, entity, my_team, ad, max_hp);
        }

        // 2. Q「穿骨」打中的敌方英雄身边各拉起一个
        let mut q_hits = Vec::new();
        for (id, pos) in foe_champions(sim, my_team) {
            let [hit, aim] = buffs_present(sim, id, [Q_HIT_ASK, R_AIM]);
            if hit {
                q_hits.push((id, pos));
            }
            if aim && r_ask && self.army_at.is_none() {
                self.army_at = Some((tick + R_LAND_DELAY, pos));
                sim.entity_remove_buff(id, R_AIM);
            }
        }
        if !q_hits.is_empty() {
            let area = field(sim);
            for (id, pos) in q_hits {
                sim.entity_remove_buff(id, Q_HIT_ASK);
                self.last_target = Some(id);
                self.spawn_one(sim, entity, my_team, place(pos, (7_500, 0), area), ad, max_hp, false);
            }
        }

        // 3. R「亡军」：箭射出去记下落点，落地那一 tick 爬出 5 个
        if r_ask {
            sim.entity_remove_buff(entity, R_ASK);
            if self.army_at.is_none() {
                // 大招的目标没认出来（刚死了之类）：落在她最近打的目标、再不行她自己脚下
                let at = self
                    .last_target
                    .and_then(|t| sim.get_entity(t))
                    .filter(|e| e.is_alive())
                    .map_or(my_pos, |e| e.pos());
                self.army_at = Some((tick + R_LAND_DELAY, at));
            }
        }
        if let Some((at_tick, center)) = self.army_at {
            if tick >= at_tick {
                self.army_at = None;
                let area = field(sim);
                for k in 0..ULT_COUNT {
                    let pt = place(center, ring_offsets(k), area);
                    self.spawn_one(sim, entity, my_team, pt, ad, max_hp, true);
                }
            }
        }

        // 4. W「葬礼」：冲锋，到了再炸
        if w_cmd {
            sim.entity_remove_buff(entity, W_CMD);
            self.start_funeral(sim, entity, my_team, my_pos);
        }
        if !self.charges.is_empty() {
            self.blow_arrived(sim, entity, my_team, ad);
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_bonebow:skeletons", BonebowPassive::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn skeleton_inherits_30pct_ad_and_scaled_hp() {
        let s = skeleton_stat(200, 1500);
        assert_eq!(s.attack, 60);
        assert_eq!(s.hp, 360);
        let low = skeleton_stat(40, 500);
        assert_eq!(low.attack, 20);
        assert_eq!(low.hp, 180);
    }

    #[test]
    fn funeral_damage_scales_with_50pct_ad() {
        assert_eq!(funeral_damage(100), 90);
        assert_eq!(funeral_damage(260), 170);
    }

    #[test]
    fn spawn_points_stay_on_the_map() {
        let f = Some(((10_000, 10_000), (900_000, 600_000)));
        assert_eq!(place((895_000, 300_000), (8_000, 0), f), (900_000, 300_000));
        assert_eq!(place((12_000, 15_000), (-13_000, -12_400), f), (10_000, 10_000));
        assert_eq!(place((500_000, 300_000), (8_000, 0), f), (508_000, 300_000));
        assert_eq!(place((5_000, 5_000), (-13_000, 0), None), (0, 5_000));
    }

    #[test]
    fn a_charge_arrives_at_its_point() {
        let (ticks, speed) = charge((0, 0), (30_000, 40_000));
        assert_eq!(ticks, 17);
        assert!(ticks * speed >= 50_000);
        assert_eq!(charge((5, 5), (5, 5)).0, 1);
    }

    #[test]
    fn the_skeleton_strikes_within_its_attack() {
        let a = skeleton_attack();
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        let anim = include_str!("../../../abysspact/champions/abysspact_skeleton#anim.fanim");
        assert_eq!(crate::fanim_ticks(anim, "attack"), Some(a.duration));
        assert_eq!(crate::fanim_ticks(anim, "spawn"), Some(RISE_TICKS as usize));
    }

    #[test]
    fn the_kit_raises_one_army_a_cast() {
        let kit = include_str!("../../../abysspact/champion/abysspact_bonebow.data_champion");
        // 箭雨打中的人身上不再挂 r_ask（以前每人一批 5 个）
        assert_eq!(kit.matches("\"abysspact_bonebow_r_ask\"").count(), 2, "only the caster flag, in both live branches");
        assert!(kit.contains(R_AIM));
        // 两个旗子都得是挂在她身上的（AddCasterBuff），名字和弹道不重
        for flag in [A_SHOT, Q_ARROW] {
            assert_eq!(effect_naming(kit, flag), Some("AddCasterBuff"), "{flag} is a caster flag in the kit");
        }
    }

    /// 生成好的技能文件里，第一个写着 `name` 的效果是什么类型（往前找最近的 `"type"`）。
    fn effect_naming<'a>(kit: &'a str, name: &str) -> Option<&'a str> {
        let at = kit.find(&format!("\"name\": \"{name}\""))?;
        let ty = kit[..at].rfind("\"type\": \"")? + "\"type\": \"".len();
        let end = ty + kit[ty..].find('"')?;
        Some(&kit[ty..end])
    }

    #[test]
    fn a_skeleton_from_the_last_match_is_never_kept() {
        assert!(keep_skel(100, 101, false), "just spawned: may not read as a unit yet");
        assert!(!keep_skel(100, 110, false), "gone");
        assert!(keep_skel(100, 400, true));
        // 上一局 5000 tick 生的，这一局才 30 tick：那个单位号是别的单位了
        assert!(!keep_skel(5000, 30, true));
    }
}
