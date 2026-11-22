//! 霁砚（`border_jiyan`）数据做不到的部分。数据：tools/kit/build_jiyan.py（参数表 P；`passive` 是这里的
//! `border_jiyan:chart`，只管配音：坐标由技能放、写在她身上）。
//!
//! - **坐标**（定标）：`border_jiyan_mark_<x>_<y>`（p_t 拍，最多 p_max 个，多了摘最旧的），地上亮着星图记号。长刻打中的地方
//!   （线上离她最近的那个敌方英雄，没有就最近的敌人）、照盘放的地方各留一个。
//! - **长刻**（`beam`）：朝目标一道长 q_len、宽 q_w 的星束（画面是转到方向的弹道，朝左 `_l`）；线上的敌人吃魔法伤害；
//!   线经过她自己的坐标，坐标炸开一小圈、用掉。
//! - **照盘**（`chart` / `chart_pulse`）：目标脚下放坐标、立六分仪，e_delay 拍后照一下（伤害、减速），照的位置写在她身上
//!   （`border_jiyan_lamp_<x>_<y>`）。
//! - **星历**（`almanac` 第 3 帧、`star` 三次）：沿她到目标的方向挑三处错开的落点（身边有坐标就落在坐标上、坐标用掉），
//!   每处先亮预警圈，落点写在她身上（`border_jiyan_star_<k>_<x>_<y>`）；`star` 每次结算编号最小的那一处。
//!
//! 日志写在本包的 border.log 里（行首 `jiyan`）。

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_jiyan";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const MARK: &str = "border_jiyan_mark_";
const LAMP: &str = "border_jiyan_lamp_";
const STAR: &str = "border_jiyan_star_";
const E_SLOW: &str = "border_jiyan_e_slow";
const R_SLOW: &str = "border_jiyan_r_slow";
const VIEW_HIT: &str = "border_jiyan_a_hit";
const VIEW_MARK: &str = "border_jiyan_p_mark";
const VIEW_CHART: &str = "border_jiyan_e_chart";
const VIEW_WARN: &str = "border_jiyan_r_warn";
const VIEW_STAR: &str = "border_jiyan_r_star";
const NOOP: &str = "border_jiyan:noop";
/// 星历的落点离她的坐标这么近就落到坐标上
const SNAP: f64 = 20_000.0;

pub static P: Params = Params::new(&[
    ("e_ap", 45), ("e_dmg", 60), ("e_r", 20000), ("e_slow", 25), ("e_slow_t", 60), ("p_max", 3), ("p_t", 240),
    ("q_ap", 70), ("q_bap", 40), ("q_br", 16000), ("q_burst", 60), ("q_dmg", 95), ("q_len", 85000), ("q_w", 9000),
    ("r_ap", 85), ("r_dmg", 200), ("r_r", 22000), ("r_slow", 30), ("r_slow_t", 60), ("r_spread", 22000),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("jiyan [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 规则（单元测试用） =====================

/// 星历的三处：目标脚下，往前、往后各错开 spread（再往两侧错开一半）。`u` 是她到目标的单位向量。
pub fn landings(target: Pt, u: Pt, spread: f64) -> [Pt; 3] {
    let side = (-u.1, u.0);
    [
        target,
        (target.0 + u.0 * spread + side.0 * spread / 2.0, target.1 + u.1 * spread + side.1 * spread / 2.0),
        (target.0 - u.0 * spread - side.0 * spread / 2.0, target.1 - u.1 * spread - side.1 * spread / 2.0),
    ]
}

/// 点 `p` 离从 `a` 朝 `u` 长 `len` 的线段多远（线段外的按端点算）。
pub fn off_line(a: Pt, u: Pt, len: f64, p: Pt) -> f64 {
    let v = (p.0 - a.0, p.1 - a.1);
    let t = (v.0 * u.0 + v.1 * u.1).clamp(0.0, len);
    dist(p, (a.0 + u.0 * t, a.1 + u.1 * t))
}

/// 加一个坐标（多了摘最旧的），亮记号。
fn add_mark(sim: &mut StableSim<'_>, caster: usize, at: Pt) {
    let marks = named(sim, caster, MARK, 2);
    let max = P.get("p_max").max(1);
    if marks.len() >= max {
        for (name, _) in &marks[..marks.len() + 1 - max] {
            sim.entity_remove_buff(caster, name);
        }
    }
    sim.add_buff(caster, &BuffV1::timed(&pt_name(MARK, at), P.get("p_t")));
    sim.play_view_effect(VIEW_MARK, caster, &InputTargetV1::pos(at.0 as u64, at.1 as u64), 0, 0, 0);
}

fn magic_round(sim: &mut StableSim<'_>, caster: usize, team: usize, at: Pt, r: f64, dmg: usize, slow: Option<(&str, usize, usize)>)
               -> usize {
    let hit = enemies_near(sim, team, at, r);
    for &id in &hit {
        sim.deal_damage(caster, id, 0, dmg, AttackTypeV1::Skill);
        if let Some((name, pct, t)) = slow {
            sim.add_buff(id, &slow_buff(name, pct, t));
        }
        sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(id), 0, 0, 0);
    }
    hit.len()
}

// ===================== 被动：只有配音 =====================

#[derive(Clone, Default)]
struct Chart {
    me: usize,
    chat: Chatter,
}

impl StablePassive for Chart {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        P.configure(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.chat.spawned();
        log(sim, format!("SPAWN #{me}: border.dll's Ji Yan (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if self.chat.alive_now(sim, me) {
            self.chat.tick(sim, ID, player, me);
        }
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
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

struct Beam;

impl StableEffectType for Beam {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let Some(to) = target_of(&input).and_then(|t| pos_of(sim, t)) else { return };
        let u = unit((to.0 - at.0, to.1 - at.1)).unwrap_or((1.0, 0.0));
        let (len, w) = (P.f("q_len"), P.f("q_w"));
        let dmg = amount(sim, caster, P.get("q_dmg"), 0, P.get("q_ap"), 0);
        let mut first: Option<(f64, Pt, bool)> = None;
        let mut hit = 0;
        for id in all_units(sim) {
            if !hittable_enemy(sim, team, id) {
                continue;
            }
            let Some(p) = pos_of(sim, id) else { continue };
            let v = (p.0 - at.0, p.1 - at.1);
            let along = v.0 * u.0 + v.1 * u.1;
            if along < 0.0 || along > len || off_line(at, u, len, p) > w / 2.0 + body_of(sim, id) * 0.5 {
                continue;
            }
            sim.deal_damage(caster, id, 0, dmg, AttackTypeV1::Skill);
            hit += 1;
            let champ = sim.get_entity(id).is_some_and(|e| e.is_champion());
            // 坐标留在最近的那个英雄脚下（没有英雄就最近的敌人）
            let better = match first {
                None => true,
                Some((d, _, c)) => (champ && !c) || (champ == c && along < d),
            };
            if better {
                first = Some((along, p, champ));
            }
        }
        // 经过她的坐标：炸一小圈，坐标用掉
        let burst = amount(sim, caster, P.get("q_burst"), 0, P.get("q_bap"), 0);
        let mut bursts = 0;
        for (name, v) in named(sim, caster, MARK, 2) {
            let m = (v[0] as f64, v[1] as f64);
            if off_line(at, u, len, m) <= w / 2.0 + 5_000.0 {
                sim.entity_remove_buff(caster, &name);
                sim.play_view_effect(VIEW_STAR, caster, &InputTargetV1::pos(m.0 as u64, m.1 as u64), 0, 0, 0);
                magic_round(sim, caster, team, m, P.f("q_br"), burst, None);
                bursts += 1;
            }
        }
        if let Some((_, p, _)) = first {
            add_mark(sim, caster, p);
        }
        let mid = (at.0 + u.0 * len / 2.0, at.1 + u.1 * len / 2.0);
        picture(sim, caster, &lr("border_jiyan_q_beam", u), NOOP, mid, u, 19);
        log(sim, format!("BEAM #{caster}: {hit} hit for {dmg}, {bursts} marks burst"));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (0, P.get("q_dmg") + s.magic_power * P.get("q_ap") / 100)
    }
}

struct ChartPlace;

impl StableEffectType for ChartPlace {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(at) = target_of(&input).and_then(|t| pos_of(sim, t)) else { return };
        add_mark(sim, caster, at);
        clear_named(sim, caster, LAMP, 2);
        sim.add_buff(caster, &BuffV1::timed(&pt_name(LAMP, at), 90));
        sim.play_view_effect(VIEW_CHART, caster, &InputTargetV1::pos(at.0 as u64, at.1 as u64), 0, 0, 0);
    }
}

struct ChartPulse;

impl StableEffectType for ChartPulse {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(team) = team_of(sim, caster) else { return };
        let Some(at) = named(sim, caster, LAMP, 2).last().map(|(_, v)| (v[0] as f64, v[1] as f64)) else { return };
        clear_named(sim, caster, LAMP, 2);
        let dmg = amount(sim, caster, P.get("e_dmg"), 0, P.get("e_ap"), 0);
        let n = magic_round(sim, caster, team, at, P.f("e_r"), dmg, Some((E_SLOW, P.get("e_slow"), P.get("e_slow_t"))));
        log(sim, format!("CHART #{caster} pulse: {n} hit"));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (0, P.get("e_dmg") + s.magic_power * P.get("e_ap") / 100)
    }
}

struct Almanac;

impl StableEffectType for Almanac {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(at) = pos_of(sim, caster) else { return };
        let Some(to) = target_of(&input).and_then(|t| pos_of(sim, t)) else { return };
        let u = unit((to.0 - at.0, to.1 - at.1)).unwrap_or((1.0, 0.0));
        let mut marks: Vec<(String, Pt)> =
            named(sim, caster, MARK, 2).into_iter().map(|(n, v)| (n, (v[0] as f64, v[1] as f64))).collect();
        clear_named(sim, caster, STAR, 3);
        let mut snapped = 0;
        for (k, p) in landings(to, u, P.f("r_spread")).into_iter().enumerate() {
            // 身边有她的坐标就落在坐标上
            let near = marks.iter().position(|(_, m)| dist(*m, p) <= SNAP);
            let land = match near {
                Some(i) => {
                    let (name, m) = marks.remove(i);
                    sim.entity_remove_buff(caster, &name);
                    snapped += 1;
                    m
                }
                None => p,
            };
            sim.add_buff(caster, &BuffV1::timed(&format!("{STAR}{k}_{}_{}", land.0.max(0.0) as u64, land.1.max(0.0) as u64), 90));
            sim.play_view_effect(VIEW_WARN, caster, &InputTargetV1::pos(land.0 as u64, land.1 as u64), 0, 0, 0);
        }
        log(sim, format!("ALMANAC #{caster}: three landings, {snapped} on her marks"));
    }
}

struct Star;

impl StableEffectType for Star {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        let Some(team) = team_of(sim, caster) else { return };
        let Some((name, v)) = named(sim, caster, STAR, 3).into_iter().min_by_key(|(_, v)| v[0]) else { return };
        sim.entity_remove_buff(caster, &name);
        let at = (v[1] as f64, v[2] as f64);
        sim.play_view_effect(VIEW_STAR, caster, &InputTargetV1::pos(at.0 as u64, at.1 as u64), 0, 0, 0);
        let dmg = amount(sim, caster, P.get("r_dmg"), 0, P.get("r_ap"), 0);
        let n = magic_round(sim, caster, team, at, P.f("r_r"), dmg, Some((R_SLOW, P.get("r_slow"), P.get("r_slow_t"))));
        log(sim, format!("STAR #{caster} {}: {n} hit for {dmg}", v[0]));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (0, P.get("r_dmg") + s.magic_power * P.get("r_ap") / 100)
    }
}

struct Noop;

impl StableEffectType for Noop {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("jiyan: {ID} v{VERSION} (Ji Yan: chart marks, long engraving, star almanac) registered"));
    module.add_native_passive(format!("{ID}:chart"), Chart::default());
    module.add_native_effect(format!("{ID}:beam"), Beam);
    module.add_native_effect(format!("{ID}:chart"), ChartPlace);
    module.add_native_effect(format!("{ID}:chart_pulse"), ChartPulse);
    module.add_native_effect(format!("{ID}:almanac"), Almanac);
    module.add_native_effect(format!("{ID}:star"), Star);
    module.add_native_effect(NOOP, Noop);
    host.log(LogLevel::Info, "border.dll: Ji Yan (chart marks, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn three_staggered_landings_along_the_aim() {
        let l = landings((100_000.0, 100_000.0), (1.0, 0.0), 22_000.0);
        assert_eq!(l[0], (100_000.0, 100_000.0));
        assert_eq!(l[1], (122_000.0, 111_000.0));
        assert_eq!(l[2], (78_000.0, 89_000.0));
    }

    #[test]
    fn distance_to_a_segment() {
        assert!((off_line((0.0, 0.0), (1.0, 0.0), 50_000.0, (20_000.0, 3_000.0)) - 3_000.0).abs() < 1e-6);
        // 线段外按端点算
        assert!((off_line((0.0, 0.0), (1.0, 0.0), 50_000.0, (-4_000.0, 3_000.0)) - 5_000.0).abs() < 1e-6);
    }
}
