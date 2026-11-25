//! 陨夜 (`abysspact_starfall`) · 观星少女 · 下路法术射手
//!
//! - 普攻「黑星」：出手时数据调本包的 `abysspact_starfall:aim`，只记下打谁（在她身上挂一个交接 buff）。被动接过来，
//!   按目标最近几 tick 的走向往前算 `a_delay` tick（AI 预判），在那个点先亮落点圈、播黑星下落，`a_delay` tick 后
//!   落地：`a_r` 内主目标吃 `a_main_ad`% 攻击力 + `a_ap`% 法强的魔法伤害，旁边的人吃其中 `a_splash`%。
//!   代价「落不到脚边」：落地时离她 `a_min` 以内的单位一个都砸不到。没有出手当时就打上的那一截了，目标跑开就砸空。
//!   盲区只管普攻：Q、W、R 的伤害不受它影响。
//! - Q「星轨」：`abysspact_starfall:q_line` 从她到目标连一条线，以目标为中心每隔 `q_step` 一颗、共 `q_n` 颗，
//!   由近到远每 `q_gap` tick 落一颗（落点圈 + 下落 `q_fall` tick）；每颗 `q_r` 内 `q_dmg + q_ap% 法强`，
//!   同一个人挨到第二颗起才减速 `q_slow`% `q_slow_t` tick。
//! - R「陨夜」：数据只挂 `r_rain` 并在目标身上挂 `r_center`。被动在目标脚下半径 `r_r` 的一片地方，`r_t` tick 里
//!   每 `r_every` tick 随机落一颗（落点圈 + 下落 `r_fall`），每颗 `r_star_r` 内 `r_dmg + r_ap% 法强`，同一个人
//!   1 秒内最多挨 `r_cap` 颗。这 4 秒她照常走。
//! - 有敌方英雄贴到 `a_min` 内、W 又在冷却时，被动让她往后退一步（`step_dist`，`step_t` tick，强制位移），
//!   每 `step_cd` tick 最多一次；W 好着就留给 AI 放遁星。
//!
//! 数字从技能数据的 `passive.params` 来（参数表 PARAMS["starfall"]）。几个效果对象建在 configure 之前，
//! 所以参数另放一份全局（每个陨夜读的是同一份技能数据）。

use std::collections::{HashMap, VecDeque};
use std::sync::RwLock;

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{can_cast, consume_buff, dist_sq, kit_param, map_box, onto_map};

pub const HERO: &str = "abysspact_starfall";
pub const NATIVE_MARK: &str = "abysspact_starfall_native";
pub const STAR_RING: &str = "abysspact_starfall_star_ring";
pub const R_CAST_VOICE: &str = "abysspact_starfall_r_voice";
pub const AIM_PREFIX: &str = "abysspact_starfall_aim:";
pub const R_RAIN: &str = "abysspact_starfall_r_rain";
pub const R_CENTER: &str = "abysspact_starfall_r_center";
pub const Q_HIT: &str = "abysspact_starfall_q_hit";
pub const Q_SLOW: &str = "abysspact_starfall_q_slow";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub a_delay: usize,
    pub a_r: usize,
    pub a_main_ad: usize,
    pub a_ap: usize,
    pub a_splash: usize,
    pub a_min: usize,
    pub q_n: usize,
    pub q_step: usize,
    pub q_gap: usize,
    pub q_fall: usize,
    pub q_r: usize,
    pub q_dmg: usize,
    pub q_ap: usize,
    pub q_slow: usize,
    pub q_slow_t: usize,
    pub r_r: usize,
    pub r_t: usize,
    pub r_every: usize,
    pub r_fall: usize,
    pub r_star_r: usize,
    pub r_dmg: usize,
    pub r_ap: usize,
    pub r_cap: usize,
    pub step_dist: usize,
    pub step_t: usize,
    pub step_cd: usize,
}

pub const DEFAULT: Params = Params {
    a_delay: 30, a_r: 15_000, a_main_ad: 100, a_ap: 20, a_splash: 60, a_min: 30_000,
    q_n: 5, q_step: 13_000, q_gap: 8, q_fall: 30, q_r: 15_000, q_dmg: 38, q_ap: 28, q_slow: 30, q_slow_t: 90,
    r_r: 40_000, r_t: 240, r_every: 12, r_fall: 30, r_star_r: 15_000, r_dmg: 38, r_ap: 28, r_cap: 2,
    step_dist: 12_000, step_t: 12, step_cd: 45,
};

impl Default for Params {
    fn default() -> Self {
        DEFAULT
    }
}

impl Params {
    pub fn parse(json: &str) -> Self {
        let d = DEFAULT;
        let g = |k: &str, v: usize| kit_param(json, k).unwrap_or(v);
        Self {
            a_delay: g("a_delay", d.a_delay), a_r: g("a_r", d.a_r), a_main_ad: g("a_main_ad", d.a_main_ad),
            a_ap: g("a_ap", d.a_ap), a_splash: g("a_splash", d.a_splash), a_min: g("a_min", d.a_min),
            q_n: g("q_n", d.q_n), q_step: g("q_step", d.q_step), q_gap: g("q_gap", d.q_gap), q_fall: g("q_fall", d.q_fall),
            q_r: g("q_r", d.q_r), q_dmg: g("q_dmg", d.q_dmg), q_ap: g("q_ap", d.q_ap), q_slow: g("q_slow", d.q_slow),
            q_slow_t: g("q_slow_t", d.q_slow_t), r_r: g("r_r", d.r_r), r_t: g("r_t", d.r_t), r_every: g("r_every", d.r_every),
            r_fall: g("r_fall", d.r_fall), r_star_r: g("r_star_r", d.r_star_r), r_dmg: g("r_dmg", d.r_dmg),
            r_ap: g("r_ap", d.r_ap), r_cap: g("r_cap", d.r_cap), step_dist: g("step_dist", d.step_dist),
            step_t: g("step_t", d.step_t), step_cd: g("step_cd", d.step_cd),
        }
    }
}

/// 效果对象读的参数（被动的 configure 写进来）。
static KIT: RwLock<Params> = RwLock::new(DEFAULT);

fn kit() -> Params {
    *KIT.read().unwrap_or_else(|e| e.into_inner())
}

/// 普攻主目标吃的伤害（魔法）。
pub fn star_damage(p: &Params, ad: usize, ap: usize) -> usize {
    ad.saturating_mul(p.a_main_ad) / 100 + ap.saturating_mul(p.a_ap) / 100
}

/// 预判落点：目标现在的位置 + 最近的走向 × 下落时间，最多往前算 `cap`。
pub fn lead(now: (u64, u64), before: (u64, u64), span: usize, ahead: usize, cap: f64) -> (f64, f64) {
    let (x, y) = (now.0 as f64, now.1 as f64);
    if span == 0 {
        return (x, y);
    }
    let (vx, vy) = ((x - before.0 as f64) / span as f64, (y - before.1 as f64) / span as f64);
    let (mut dx, mut dy) = (vx * ahead as f64, vy * ahead as f64);
    let len = dx.hypot(dy);
    if len > cap && len > 0.0 {
        dx *= cap / len;
        dy *= cap / len;
    }
    (x + dx, y + dy)
}

/// Q 的落点：以目标为中心沿她到目标的方向，每隔 `step` 一颗，由近到远。
pub fn line_points(from: (u64, u64), to: (u64, u64), n: usize, step: f64) -> Vec<(f64, f64)> {
    let (dx, dy) = (to.0 as f64 - from.0 as f64, to.1 as f64 - from.1 as f64);
    let len = dx.hypot(dy);
    let (ux, uy) = if len < 1.0 { (1.0, 0.0) } else { (dx / len, dy / len) };
    let mid = (n.saturating_sub(1)) as f64 / 2.0;
    (0..n)
        .map(|k| {
            let off = (k as f64 - mid) * step;
            (to.0 as f64 + ux * off, to.1 as f64 + uy * off)
        })
        .collect()
}

/// 圆盘里均匀取一点（`a`、`b` 是 0..1 的两个随机数）。
pub fn disc_point(center: (u64, u64), r: f64, a: f64, b: f64) -> (f64, f64) {
    let rr = r * a.sqrt();
    let th = b * std::f64::consts::TAU;
    (center.0 as f64 + rr * th.cos(), center.1 as f64 + rr * th.sin())
}

fn play_fall(sim: &mut StableSim<'_>, caster: usize, at: (u64, u64)) {
    let here = InputTargetV1::pos(at.0, at.1);
    sim.play_view_effect("abysspact_starfall_warning", caster, &here, 0, 0, 0);
    sim.play_view_effect("abysspact_starfall_star_fall", caster, &here, 0, 0, 0);
}

fn play_impact(sim: &mut StableSim<'_>, caster: usize, at: (u64, u64), sfx: &str) {
    let here = InputTargetV1::pos(at.0, at.1);
    sim.play_view_effect("abysspact_starfall_star_impact", caster, &here, 0, 0, 0);
    sim.play_sfx(sfx, caster, &here);
}

/// (单位, 位置) ：活着的、不是 `team` 的、离 `at` 不超过 `r`（加上身体半径）的单位。
fn foes_near(sim: &StableSim<'_>, team: usize, at: (u64, u64), r: usize, towers: bool) -> Vec<(usize, (u64, u64))> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.is_alive() && e.team() != team && (towers || !e.is_tower()) && e.is_targetable())
        .filter(|e| {
            let reach = (r + e.radius()) as u64;
            dist_sq(at, e.pos()) <= reach.saturating_mul(reach)
        })
        .map(|e| (e.id(), e.pos()))
        .collect()
}

#[derive(Clone, Copy)]
enum StarKind {
    Attack { main: usize },
    Rain,
}

#[derive(Clone, Copy)]
struct Star {
    land: usize,
    at: (u64, u64),
    kind: StarKind,
}

#[derive(Clone, Copy)]
struct Rain {
    center: (u64, u64),
    end: usize,
    next: usize,
}

#[derive(Clone, Default)]
struct StarfallPassive {
    p: Params,
    voice: Voice,
    native_marked: bool,
    stars: Vec<Star>,
    /// 敌方英雄最近几 tick 的位置（算走向用）。
    trail: HashMap<usize, VecDeque<(u64, u64)>>,
    rain: Option<Rain>,
    rain_hits: HashMap<usize, VecDeque<usize>>,
    next_step: usize,
    seq: u64,
}

impl StarfallPassive {
    fn rand01(&mut self, seed: u64) -> f64 {
        // splitmix64：同一局每次都一样
        self.seq = self.seq.wrapping_add(1);
        let mut z = seed ^ self.seq.wrapping_mul(0x9E37_79B9_7F4A_7C15);
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^= z >> 31;
        (z >> 11) as f64 / (1u64 << 53) as f64
    }

    /// 接过普攻交接：在预判点落一颗星。
    fn take_aims(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        let names: Vec<String> = sim
            .get_entity(me)
            .map(|e| {
                (0..e.buff_count())
                    .filter_map(|i| e.buff_at(i))
                    .filter(|b| b.name().starts_with(AIM_PREFIX))
                    .map(|b| b.name().to_string())
                    .collect()
            })
            .unwrap_or_default();
        for name in names {
            sim.entity_remove_buff(me, &name);
            let Some(target) = name[AIM_PREFIX.len()..].parse::<usize>().ok() else { continue };
            let Some(now) = sim.get_entity(target).map(|e| e.pos()) else { continue };
            let (before, span) = match self.trail.get(&target) {
                Some(q) if q.len() > 1 => (*q.front().unwrap_or(&now), q.len() - 1),
                _ => (now, 0),
            };
            let guess = lead(now, before, span, self.p.a_delay, self.p.a_r as f64 * 1.5);
            let at = onto_map(map_box(sim), guess.0, guess.1);
            play_fall(sim, me, at);
            self.stars.push(Star { land: tick + self.p.a_delay, at, kind: StarKind::Attack { main: target } });
        }
    }

    fn land(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, my_pos: (u64, u64), star: Star, tick: usize) {
        let Some(stat) = sim.get_entity(me).map(|e| e.stat()) else { return };
        let p = self.p;
        match star.kind {
            StarKind::Attack { main } => {
                play_impact(sim, me, star.at, "abysspact_starfall_a_hit");
                let full = star_damage(&p, stat.attack, stat.magic_power);
                let min2 = (p.a_min as u64).saturating_mul(p.a_min as u64);
                for (u, pos) in foes_near(sim, team, star.at, p.a_r, true) {
                    // 落不到她脚边
                    if dist_sq(my_pos, pos) < min2 {
                        continue;
                    }
                    let dmg = if u == main { full } else { full * p.a_splash / 100 };
                    sim.deal_damage_typed(me, u, dmg, DamageTypeV1::Ap, AttackTypeV1::BaseAttack);
                }
            }
            StarKind::Rain => {
                play_impact(sim, me, star.at, "abysspact_starfall_r_rain");
                let dmg = p.r_dmg + stat.magic_power.saturating_mul(p.r_ap) / 100;
                for (u, _) in foes_near(sim, team, star.at, p.r_star_r, false) {
                    let q = self.rain_hits.entry(u).or_default();
                    while q.front().is_some_and(|&t| tick.saturating_sub(t) >= 60) {
                        q.pop_front();
                    }
                    if q.len() >= p.r_cap {
                        continue;
                    }
                    q.push_back(tick);
                    sim.deal_damage_typed(me, u, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                }
            }
        }
    }

    fn start_rain(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, tick: usize) {
        let center = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| e.team() != team)
            .find(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == R_CENTER))
            .map(|e| (e.id(), e.pos()));
        let Some((cid, center)) = center else { return };
        sim.entity_remove_buff(cid, R_CENTER);
        let here = InputTargetV1::pos(center.0, center.1);
        sim.play_view_effect("abysspact_starfall_sky_rift", me, &here, 0, 0, 0);
        sim.play_sfx("abysspact_starfall_r_rift", me, &here);
        self.rain = Some(Rain { center, end: tick + self.p.r_t, next: tick });
        self.rain_hits.clear();
    }

    /// 贴脸又没有遁星：往后退一步。
    fn step_back(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (u64, u64), tick: usize) {
        if tick < self.next_step {
            return;
        }
        let w_ready = sim
            .get_entity(me)
            .and_then(|e| e.cooldown(SkillSlotV1::Skill2))
            .is_some_and(|c| c.unlocked && c.remaining == 0);
        if w_ready || !can_cast(sim, me) {
            return;
        }
        let min2 = (self.p.a_min as u64).saturating_mul(self.p.a_min as u64);
        let near = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| e.is_champion() && e.is_alive() && e.team() != team)
            .map(|e| (e.pos(), dist_sq(pos, e.pos())))
            .filter(|&(_, d2)| d2 < min2)
            .min_by_key(|&(_, d2)| d2);
        let Some((foe, _)) = near else { return };
        let (dx, dy) = (pos.0 as f64 - foe.0 as f64, pos.1 as f64 - foe.1 as f64);
        let len = dx.hypot(dy).max(1.0);
        let ticks = self.p.step_t.max(1);
        let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
        cc.dx = (dx / len * 1000.0).round() as i64;
        cc.dy = (dy / len * 1000.0).round() as i64;
        cc.speed = (self.p.step_dist / ticks).max(1) as u64;
        sim.apply_cc(me, &cc);
        self.next_step = tick + self.p.step_cd;
    }
}

impl StablePassive for StarfallPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = Params::parse(params_json);
        *KIT.write().unwrap_or_else(|e| e.into_inner()) = self.p;
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.native_marked = false;
        self.stars.clear();
        self.trail.clear();
        self.rain = None;
        self.rain_hits.clear();
        self.next_step = 0;
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, target: usize, _damage: &mut usize) {
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        self.stars.clear();
        self.rain = None;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, rng: u64, _player: usize, entity: usize) {
        let Some((alive, team, pos)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.team(), e.pos())) else {
            return;
        };
        if !alive {
            return;
        }
        let tick = sim.tick();
        if !self.native_marked {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
            sim.add_buff(entity, &BuffV1::named(STAR_RING));
            self.native_marked = true;
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 敌方英雄的走向：留最近 7 个位置
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(e) = sim.get_entity(id) else { continue };
            if e.team() == team {
                continue;
            }
            let q = self.trail.entry(id).or_default();
            if !e.is_alive() {
                q.clear();
                continue;
            }
            q.push_back(e.pos());
            while q.len() > 7 {
                q.pop_front();
            }
        }

        self.take_aims(sim, entity, tick);

        if consume_buff(sim, entity, R_RAIN) && self.rain.is_none() {
            self.start_rain(sim, entity, team, tick);
        }
        if let Some(mut rain) = self.rain {
            if tick >= rain.end {
                self.rain = None;
            } else {
                if tick >= rain.next {
                    rain.next = tick + self.p.r_every.max(1);
                    let (a, b) = (self.rand01(rng), self.rand01(rng));
                    let spot = disc_point(rain.center, self.p.r_r as f64, a, b);
                    let at = onto_map(map_box(sim), spot.0, spot.1);
                    play_fall(sim, entity, at);
                    self.stars.push(Star { land: tick + self.p.r_fall, at, kind: StarKind::Rain });
                }
                self.rain = Some(rain);
            }
        }

        let due: Vec<Star> = self.stars.iter().copied().filter(|s| s.land <= tick).collect();
        self.stars.retain(|s| s.land > tick);
        for star in due {
            self.land(sim, entity, team, pos, star, tick);
        }

        self.step_back(sim, entity, team, pos, tick);
    }
}

/// 普攻出手：记下打谁，交给被动。
#[derive(Debug)]
struct Aim;

impl StableEffectType for Aim {
    fn apply(&self, sim: &mut StableSim<'_>, _seed: u64, caster: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() || sim.get_entity(input.target_id).is_none() {
            return;
        }
        sim.add_buff(caster, &BuffV1::timed(&format!("{AIM_PREFIX}{}", input.target_id), 8));
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        (0, star_damage(&kit(), caster_stat.attack, caster_stat.magic_power))
    }
}

/// Q 出手：沿线排好五颗星。
#[derive(Debug)]
struct QLine;

impl StableEffectType for QLine {
    fn apply(&self, sim: &mut StableSim<'_>, _seed: u64, caster: usize, input: InputTargetV1) {
        let p = kit();
        let Some(from) = sim.get_entity(caster).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let to = if input.kind == InputTargetKindV1::Target.code() {
            match sim.get_entity(input.target_id) {
                Some(e) => e.pos(),
                None => return,
            }
        } else {
            (input.x, input.y)
        };
        let bx = map_box(sim);
        for (k, (x, y)) in line_points(from, to, p.q_n, p.q_step as f64).into_iter().enumerate() {
            let at = onto_map(bx, x, y);
            let here = InputTargetV1::pos(at.0, at.1);
            if k == 0 {
                play_fall(sim, caster, at);
            } else {
                sim.queue_effect("abysspact_starfall:q_fall", AttackTypeV1::Skill, caster, &here, k * p.q_gap);
            }
            sim.queue_effect("abysspact_starfall:q_star", AttackTypeV1::Skill, caster, &here, k * p.q_gap + p.q_fall);
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = kit();
        (0, 2 * (p.q_dmg + caster_stat.magic_power.saturating_mul(p.q_ap) / 100))
    }
}

#[derive(Debug)]
struct QFall;

impl StableEffectType for QFall {
    fn apply(&self, sim: &mut StableSim<'_>, _seed: u64, caster: usize, input: InputTargetV1) {
        play_fall(sim, caster, (input.x, input.y));
    }
}

/// Q 的一颗星落地：挨第二颗起减速。
#[derive(Debug)]
struct QStar;

impl StableEffectType for QStar {
    fn apply(&self, sim: &mut StableSim<'_>, _seed: u64, caster: usize, input: InputTargetV1) {
        let p = kit();
        let Some((team, ap)) = sim.get_entity(caster).map(|e| (e.team(), e.stat().magic_power)) else { return };
        let at = (input.x, input.y);
        play_impact(sim, caster, at, "abysspact_starfall_a_hit");
        let dmg = p.q_dmg + ap.saturating_mul(p.q_ap) / 100;
        for (u, _) in foes_near(sim, team, at, p.q_r, false) {
            sim.deal_damage_typed(caster, u, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            if consume_buff(sim, u, Q_HIT) {
                sim.entity_remove_buff(u, Q_SLOW);
                let mut slow = BuffV1::timed(Q_SLOW, p.q_slow_t.max(1));
                slow.move_speed_mult = -(p.q_slow as i32);
                sim.add_buff(u, &slow);
            }
            sim.add_buff(u, &BuffV1::timed(Q_HIT, 60));
        }
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_starfall:starfall", StarfallPassive::default());
    module.add_native_effect("abysspact_starfall:aim", Aim);
    module.add_native_effect("abysspact_starfall:q_line", QLine);
    module.add_native_effect("abysspact_starfall:q_fall", QFall);
    module.add_native_effect("abysspact_starfall:q_star", QStar);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_star_leads_a_walking_target() {
        // 6 tick 走了 6000：0.5 秒后再往前 30000，但最多往前 22500
        assert_eq!(lead((106_000, 0), (100_000, 0), 6, 30, 22_500.0), (128_500.0, 0.0));
        // 站着不动：就砸脚下
        assert_eq!(lead((100_000, 50_000), (100_000, 50_000), 6, 30, 22_500.0), (100_000.0, 50_000.0));
    }

    #[test]
    fn five_stars_on_a_line_through_the_target() {
        let pts = line_points((0, 0), (50_000, 0), 5, 13_000.0);
        let xs: Vec<f64> = pts.iter().map(|p| p.0).collect();
        assert_eq!(xs, vec![24_000.0, 37_000.0, 50_000.0, 63_000.0, 76_000.0]);
        assert!(pts.iter().all(|p| p.1 == 0.0));
    }

    #[test]
    fn rain_points_stay_in_the_disc() {
        for (a, b) in [(0.0, 0.0), (1.0, 0.25), (0.5, 0.75), (0.999, 0.999)] {
            let (x, y) = disc_point((100_000, 100_000), 40_000.0, a, b);
            assert!((x - 100_000.0).hypot(y - 100_000.0) <= 40_000.0 + 1e-6);
        }
    }

    #[test]
    fn params_come_from_the_kit_file() {
        let p = Params::parse(&crate::kit_params_of(include_str!(
            "../../../abysspact/champion/abysspact_starfall.data_champion"
        )));
        assert_eq!(p, Params::default());
        assert_eq!(star_damage(&p, 100, 100), 120);
    }
}
