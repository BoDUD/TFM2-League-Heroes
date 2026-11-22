//! 灯弥（`border_dengmi`）数据做不到的部分。数据：tools/kit/build_dengmi.py（参数表 P；`passive` 是这里的
//! `border_dengmi:light`）。
//!
//! - **存光**（被动）：每拍看身边 p_reach 内的友军（连她自己）掉了多少血；掉血的那一刻他附近 p_near 内有敌方英雄正在施法
//!   （施法动作还在播，或者技能刚进冷却），或者一下掉了最大生命的 p_burst% 以上，就算技能伤害：每掉 1% 攒 p_gain / 100 点
//!   灯火，最多 100，十层挂在她身上（`border_dengmi_light`，收灯读它）。灯火每攒满一半亮一下水母灯。
//!   她还每拍挑身边最承压的友军（最近 1.5 秒掉的血、身边的敌方英雄、生命比例），给他挂 `border_dengmi_focus`（递灯认它）。
//! - **递灯**（`border_dengmi:lamp`）：给 focus 的友军（没有就 q_reach 内生命比例最低的，连她自己）护盾。
//! - **引路**（`border_dengmi:path`）：给 e_reach 内生命比例最低的友军（有别人先挑别人）加移速，低血再加；她自己也快一点。
//! - **收灯**：第一脉冲的基础治疗在数据里（AI 看得见治疗量，等有人掉了血才放）；`pulse1` 按施法的人身上的灯火补上加成、
//!   在主目标脚下放套环、给主目标做记号；`pulse2` 在主目标身边 r_near 内挑生命比例最低的有效友军（有别人先挑别人）治疗，
//!   放套环，灯火清零。别人放的（佛耶戈附身）没有灯火，按 0 算；塞拉斯偷去的是数据版，不走这里。
//!
//! 日志写在本包的 border.log 里（行首 `dengmi`）。

use std::collections::{HashMap, VecDeque};

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_dengmi";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const LIGHT: &str = "border_dengmi_light";
pub const FOCUS: &str = "border_dengmi_focus";
const MAIN: &str = "border_dengmi_main";
const PATH: &str = "border_dengmi_e_path";
const LEAD: &str = "border_dengmi_e_lead";
const VIEW_SHIELD: &str = "border_dengmi_q_shield";
const VIEW_PATH: &str = "border_dengmi_e_path";
const VIEW_RING: &str = "border_dengmi_r_ring";
const VIEW_GLOW: &str = "border_dengmi_p_glow";
pub const LEVELS: usize = 10;
/// 算「最近掉的血」往回看多久
const RECENT: usize = 90;
/// 敌方英雄刚施法的窗口
const CAST_WINDOW: usize = 20;

pub static P: Params = Params::new(&[
    ("e_low", 50), ("e_ms", 35), ("e_ms_low", 20), ("e_reach", 60000), ("e_self", 15), ("e_t", 150),
    ("p_burst", 8), ("p_gain", 100), ("p_near", 90000), ("p_reach", 60000), ("q_ap", 70), ("q_flare_r", 30000),
    ("q_flare_slow", 50), ("q_flare_t", 90), ("q_hp", 6), ("q_reach", 60000), ("q_sh", 110), ("q_t", 150),
    ("r_ap", 80), ("r_burst", 90), ("r_burst_ap", 45), ("r_burst_r", 35000), ("r_burst_slow", 30), ("r_heal", 180),
    ("r_light", 100), ("r_near", 40000), ("r_reach", 75000),
]);

const FLARE: &str = "border_dengmi_q_flare";
const FLASH: &str = "border_dengmi_r_flash";

/// 灯光晃眼：`center` 身边 `radius` 内的敌人（不算塔）减速；`dmg`（魔法伤害）不是 0 就先打一下。返回几个人。
fn light_burst(sim: &mut StableSim<'_>, caster: usize, center: Pt, radius: f64, dmg: usize, name: &str, slow: usize,
               ticks: usize) -> usize {
    let Some(team) = team_of(sim, caster) else { return 0 };
    let mut n = 0;
    for id in all_units(sim) {
        if !hittable_enemy(sim, team, id) || !pos_of(sim, id).is_some_and(|p| dist(center, p) <= radius) {
            continue;
        }
        if dmg > 0 {
            sim.deal_damage(caster, id, 0, dmg, AttackTypeV1::Skill);
        }
        sim.add_buff(id, &slow_buff(name, slow, ticks));
        n += 1;
    }
    n
}

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("dengmi [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 规则（单元测试用） =====================

/// 掉了 `drop`（最大生命 `max`）：攒多少灯火。
pub fn gain(drop: usize, max: usize, p_gain: usize) -> f64 {
    if max == 0 {
        return 0.0;
    }
    drop as f64 * 100.0 / max as f64 * p_gain as f64 / 100.0
}

/// 承压的分：最近掉的血（占最大生命的百分比）、身边的敌方英雄一个 15 分、生命比例越低越高。
pub fn stress(recent_pct: f64, enemies_near: usize, hp_ratio: f64) -> f64 {
    recent_pct + 15.0 * enemies_near as f64 + 30.0 * (1.0 - hp_ratio.clamp(0.0, 1.0))
}

/// 灯火 `k` 层时治疗乘多少（r_light 是满层的加成百分比）。
pub fn light_mult(k: usize, r_light: usize) -> f64 {
    1.0 + (k.min(LEVELS) * r_light) as f64 / (LEVELS * 100) as f64
}

/// 挑生命比例最低的；`prefer_not` 在别人里挑得出来就不挑他。
pub fn lowest(cands: &[(usize, f64)], prefer_not: Option<usize>) -> Option<usize> {
    let others: Vec<&(usize, f64)> = cands.iter().filter(|c| Some(c.0) != prefer_not).collect();
    let pool: Vec<&(usize, f64)> = if others.is_empty() { cands.iter().collect() } else { others };
    pool.into_iter().min_by(|a, b| a.1.total_cmp(&b.1)).map(|c| c.0)
}

// ===================== 被动：存光 =====================

#[derive(Clone, Default)]
struct Light {
    me: usize,
    light: f64,
    shown: usize,
    /// 每个友军上一拍的血
    hp: HashMap<usize, usize>,
    /// 每个友军最近掉的血（哪一拍、掉多少）
    drops: HashMap<usize, VecDeque<(usize, usize)>>,
    /// 每个敌方英雄上一次施法是哪一拍
    cast_at: HashMap<usize, usize>,
    focus: Option<usize>,
    chat: Chatter,
}

impl Light {
    fn reset(&mut self, sim: &mut StableSim<'_>) {
        self.light = 0.0;
        self.shown = 0;
        self.hp.clear();
        self.drops.clear();
        if let Some(f) = self.focus.take() {
            sim.entity_remove_buff(f, FOCUS);
        }
    }

    fn step(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        let (Some(at), Some(team)) = (pos_of(sim, me), team_of(sim, me)) else { return };
        let foes = live_champions(sim, team, false);
        for &e in &foes {
            if casting(sim, e) || just_cast(sim, e, CAST_WINDOW) {
                self.cast_at.insert(e, tick);
            }
        }
        let foe_pos: Vec<(usize, Pt)> = foes.iter().filter_map(|&e| pos_of(sim, e).map(|p| (e, p))).collect();
        let reach = P.f("p_reach");
        let near_r = P.f("p_near");
        let mut gained = 0.0;
        for a in live_champions(sim, team, true) {
            let Some(e) = sim.get_entity(a) else { continue };
            let (now, max) = e.hp();
            let before = self.hp.insert(a, now);
            let Some(p) = pos_of(sim, a) else { continue };
            let Some(before) = before.filter(|&b| b > now) else { continue };
            let drop = before - now;
            self.drops.entry(a).or_default().push_back((tick, drop));
            if dist(at, p) > reach {
                continue;
            }
            let burst = max > 0 && drop * 100 >= max * P.get("p_burst");
            let spell = foe_pos.iter().any(|&(f, fp)| {
                dist(fp, p) <= near_r && self.cast_at.get(&f).is_some_and(|&t| tick <= t + CAST_WINDOW)
            });
            if burst || spell {
                gained += gain(drop, max, P.get("p_gain"));
            }
        }
        for q in self.drops.values_mut() {
            while q.front().is_some_and(|&(t, _)| t + RECENT < tick) {
                q.pop_front();
            }
        }
        // 收灯放掉了（层数比记的少）
        let have = count_buff(sim, me, LIGHT);
        if have < self.shown {
            self.light = (have * 10) as f64;
            self.shown = have;
        }
        let before = self.light;
        self.light = (self.light + gained).min(100.0);
        if gained > 0.0 && ((before < 50.0 && self.light >= 50.0) || (before < 100.0 && self.light >= 100.0)) {
            sim.play_view_effect(VIEW_GLOW, me, &InputTargetV1::target(me), 0, 0, 0);
            log(sim, format!("LIGHT #{me} {:.0}", self.light));
        }
        let want = ((self.light / 10.0 + 1e-9).floor() as usize).min(LEVELS);
        if want != self.shown {
            set_stacks(sim, me, LIGHT, want, || BuffV1::named(LIGHT));
            self.shown = want;
        }
        self.pick_focus(sim, me, at, team, &foe_pos);
    }

    /// 最承压的友军挂 focus（换人时摘掉旧的）。
    fn pick_focus(&mut self, sim: &mut StableSim<'_>, me: usize, at: Pt, team: usize, foes: &[(usize, Pt)]) {
        let reach = P.f("q_reach");
        let best = live_champions(sim, team, true)
            .into_iter()
            .filter_map(|a| pos_of(sim, a).map(|p| (a, p)))
            .filter(|&(_, p)| dist(at, p) <= reach)
            .map(|(a, p)| {
                let max = sim.get_entity(a).map_or(1, |e| e.hp().1.max(1));
                let recent: usize = self.drops.get(&a).map_or(0, |q| q.iter().map(|d| d.1).sum());
                let near = foes.iter().filter(|f| dist(f.1, p) <= 32_000.0).count();
                (a, stress(recent as f64 * 100.0 / max as f64, near, hp_ratio(sim, a)))
            })
            .filter(|&(_, s)| s >= 10.0)
            .max_by(|a, b| a.1.total_cmp(&b.1))
            .map(|b| b.0);
        if best != self.focus {
            if let Some(old) = self.focus {
                sim.entity_remove_buff(old, FOCUS);
            }
            self.focus = best;
        }
        if let Some(f) = best {
            sim.entity_stack_buff(f, &BuffV1::timed(FOCUS, 30), 1, true);
        }
        let _ = me;
    }
}

impl StablePassive for Light {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        P.configure(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.chat.spawned();
        self.light = 0.0;
        self.shown = 0;
        self.hp.clear();
        self.drops.clear();
        self.focus = None;
        log(sim, format!("SPAWN #{me}: border.dll's Deng Mi (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.reset(sim);
            return;
        }
        self.chat.tick(sim, ID, player, me);
        self.step(sim, me);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.chat.attacked(sim, ID, me, target);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _attacker: usize, damage: usize) {
        self.chat.damaged(sim, ID, me, damage);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.chat.killed(sim, ID, me, victim);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        let me = self.me;
        self.reset(sim);
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

/// 施法的人这一队、离他 `reach` 内活着的英雄（连他自己）和生命比例。
fn allies_in(sim: &StableSim<'_>, caster: usize, center: Pt, reach: f64) -> Vec<(usize, f64)> {
    let Some(team) = team_of(sim, caster) else { return Vec::new() };
    live_champions(sim, team, true)
        .into_iter()
        .filter(|&a| pos_of(sim, a).is_some_and(|p| dist(center, p) <= reach))
        .map(|a| (a, hp_ratio(sim, a)))
        .collect()
}

struct Lamp;

impl StableEffectType for Lamp {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(at) = pos_of(sim, caster) else { return };
        let cands = allies_in(sim, caster, at, P.f("q_reach"));
        let focus = cands.iter().map(|c| c.0).find(|&a| has_buff(sim, a, FOCUS));
        let Some(t) = focus.or_else(|| lowest(&cands, None)) else { return };
        let max = sim.get_entity(t).map_or(0, |e| e.hp().1);
        let amt = amount(sim, caster, P.get("q_sh"), 0, P.get("q_ap"), 0) + max * P.get("q_hp") / 100;
        sim.entity_add_shield(t, amt, P.get("q_t"));
        sim.play_view_effect(VIEW_SHIELD, caster, &InputTargetV1::target(t), 0, 0, 0);
        // 灯一亮，他身边的敌人晃眼减速
        let dazzled = pos_of(sim, t).map_or(0, |c| {
            light_burst(sim, caster, c, P.f("q_flare_r"), 0, FLARE, P.get("q_flare_slow"), P.get("q_flare_t"))
        });
        log(sim, format!("LAMP #{caster} -> #{t} shield {amt}{}, {dazzled} dazzled",
                         if focus.is_some() { " (focus)" } else { "" }));
    }

    fn expected_shield(&self, s: &StatV1) -> usize {
        P.get("q_sh") + s.magic_power * P.get("q_ap") / 100
    }
}

struct Path;

impl StableEffectType for Path {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(at) = pos_of(sim, caster) else { return };
        let cands = allies_in(sim, caster, at, P.f("e_reach"));
        // 都差不多满血时挑别人；生命比例低得明显的就是她自己也挑她
        let mine = cands.iter().find(|c| c.0 == caster).map_or(1.0, |c| c.1);
        let other_min = cands.iter().filter(|c| c.0 != caster).map(|c| c.1).fold(2.0, f64::min);
        let prefer_not = (mine + 0.05 >= other_min).then_some(caster);
        let Some(t) = lowest(&cands, prefer_not) else { return };
        let low = hp_ratio(sim, t) * 100.0 < P.f("e_low");
        let mut b = BuffV1::timed(PATH, P.get("e_t"));
        b.move_speed_mult = (P.get("e_ms") + if low { P.get("e_ms_low") } else { 0 }) as i32;
        sim.entity_remove_buff(t, PATH);
        sim.add_buff(t, &b);
        if t != caster {
            let mut l = BuffV1::timed(LEAD, P.get("e_t"));
            l.move_speed_mult = P.get("e_self") as i32;
            sim.entity_remove_buff(caster, LEAD);
            sim.add_buff(caster, &l);
        }
        sim.play_view_effect(VIEW_PATH, caster, &InputTargetV1::target(t), 0, 0, 0);
        log(sim, format!("PATH #{caster} -> #{t} +{}%{}", b.move_speed_mult, if low { " (low)" } else { "" }));
    }

    fn expected_buff(&self, _s: &StatV1) -> Option<BuffV1> {
        let mut b = BuffV1::timed(PATH, P.get("e_t"));
        b.move_speed_mult = P.get("e_ms") as i32;
        Some(b)
    }
}

/// 脉冲的光在受治疗的人身边炸开：伤害、减速 1 秒。
fn burst_round(sim: &mut StableSim<'_>, caster: usize, healed: usize) {
    if let Some(c) = pos_of(sim, healed) {
        let dmg = amount(sim, caster, P.get("r_burst"), 0, P.get("r_burst_ap"), 0);
        light_burst(sim, caster, c, P.f("r_burst_r"), dmg, FLASH, P.get("r_burst_slow"), SECOND);
    }
}

fn base_heal(sim: &StableSim<'_>, caster: usize) -> usize {
    amount(sim, caster, P.get("r_heal"), 0, P.get("r_ap"), 0)
}

struct Pulse1;

impl StableEffectType for Pulse1 {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(main) = (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id) else { return };
        if !alive(sim, main) {
            return;
        }
        let k = count_buff(sim, caster, LIGHT);
        // 数据已经治疗了基础量，这里补灯火的加成
        let extra = (base_heal(sim, caster) as f64 * (light_mult(k, P.get("r_light")) - 1.0)).round() as usize;
        if extra > 0 {
            sim.heal(caster, main, extra);
        }
        sim.play_view_effect(VIEW_RING, caster, &InputTargetV1::target(main), 0, 0, 0);
        burst_round(sim, caster, main);
        sim.entity_remove_buff(main, MAIN);
        sim.add_buff(main, &BuffV1::timed(MAIN, 40));
        log(sim, format!("PULSE1 #{caster} -> #{main}: light {k}, +{extra}"));
    }

    fn expected_heal(&self, s: &StatV1) -> usize {
        // 基础量在数据的 Heal 里，这里只报平均的加成（一半灯火）
        (P.get("r_heal") + s.magic_power * P.get("r_ap") / 100) * P.get("r_light") / 200
    }
}

struct Pulse2;

impl StableEffectType for Pulse2 {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(team) = team_of(sim, caster) else { return };
        let main = live_champions(sim, team, true).into_iter().find(|&a| has_buff(sim, a, MAIN));
        let Some(center) = main.and_then(|m| pos_of(sim, m)).or_else(|| pos_of(sim, caster)) else { return };
        let cands = allies_in(sim, caster, center, P.f("r_near"));
        let k = count_buff(sim, caster, LIGHT);
        if let Some(t) = lowest(&cands, main) {
            let amt = (base_heal(sim, caster) as f64 * light_mult(k, P.get("r_light"))).round() as usize;
            sim.heal(caster, t, amt);
            sim.play_view_effect(VIEW_RING, caster, &InputTargetV1::target(t), 0, 0, 0);
            burst_round(sim, caster, t);
            log(sim, format!("PULSE2 #{caster} -> #{t} heal {amt} (light {k}){}",
                             if Some(t) == main { " (main again)" } else { "" }));
        }
        if let Some(m) = main {
            sim.entity_remove_buff(m, MAIN);
        }
        sim.entity_remove_buff(caster, LIGHT);
    }

    fn expected_heal(&self, s: &StatV1) -> usize {
        P.get("r_heal") + s.magic_power * P.get("r_ap") / 100
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("dengmi: {ID} v{VERSION} (Deng Mi: stored light, lamp, path, gathering) registered"));
    module.add_native_passive(format!("{ID}:light"), Light::default());
    module.add_native_effect(format!("{ID}:lamp"), Lamp);
    module.add_native_effect(format!("{ID}:path"), Path);
    module.add_native_effect(format!("{ID}:pulse1"), Pulse1);
    module.add_native_effect(format!("{ID}:pulse2"), Pulse2);
    host.log(LogLevel::Info, "border.dll: Deng Mi (stored light, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn light_comes_from_the_share_of_health_lost() {
        assert!((gain(100, 1000, 100) - 10.0).abs() < 1e-9);
        assert!((gain(100, 1000, 50) - 5.0).abs() < 1e-9);
        assert_eq!(gain(100, 0, 100), 0.0);
    }

    #[test]
    fn full_light_doubles_the_heal() {
        assert!((light_mult(0, 100) - 1.0).abs() < 1e-9);
        assert!((light_mult(5, 100) - 1.5).abs() < 1e-9);
        assert!((light_mult(10, 100) - 2.0).abs() < 1e-9);
        assert!((light_mult(30, 100) - 2.0).abs() < 1e-9);
    }

    #[test]
    fn the_second_pulse_prefers_someone_else() {
        let c = [(1, 0.3), (2, 0.5), (3, 0.9)];
        assert_eq!(lowest(&c, Some(1)), Some(2));
        assert_eq!(lowest(&c, None), Some(1));
        // 只有主目标一个人：还是他
        assert_eq!(lowest(&[(1, 0.3)], Some(1)), Some(1));
        assert_eq!(lowest(&[], None), None);
    }

    #[test]
    fn stress_counts_hits_enemies_and_health() {
        assert!(stress(0.0, 0, 1.0) < 10.0);
        assert!(stress(15.0, 0, 1.0) >= 10.0);
        assert!(stress(0.0, 1, 1.0) >= 10.0);
        assert!(stress(20.0, 1, 0.5) > stress(20.0, 0, 0.5));
    }
}
