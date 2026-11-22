//! 伏梭（`border_fusuo`）数据做不到的部分。数据：tools/kit/build_fusuo.py（参数表 P；`passive` 是这里的
//! `border_fusuo:steps`）。错拍（大招）全在数据里。
//!
//! - **数步**（被动）：每拍看看得见的敌方英雄离他自己最近的队友多远：在 p_alone 外、还没往回靠，就数一步，连着 p_steps 步
//!   就被盯上（`border_fusuo_track`，p_keep 拍，一直落单就一直续），刚盯上时他脚下亮一串脚印；回到队友身边就慢慢不数了。
//!   伏梭打被盯上的人（普攻、技能，`on_attack`）伤害 +p_dmg%。
//! - **掠阶**（`border_fusuo:skim` 第 1 拍、`skim_hit` 第 3 帧）：q_reach 内有被盯上的敌方英雄就改冲他（最近的那个），不然冲
//!   目标；强制位移冲到离他 q_stop 处（撞墙就停），冲的时候摆着技能的姿势。冲的是谁记在他身上（`border_fusuo_q_<id>`），
//!   第 3 帧砍他（不在 q_hit_r 内就砍身边最近的敌人），被盯上的再加 q_track%。
//! - **留扣**（`border_fusuo:clasp` 第 2 帧）：脚下的位置记成回撤点（`border_fusuo_anchor_<x>_<y>`，e_win 拍），地上亮着；
//!   e_win 拍内被动看他危险了（生命低于 e_low%、一秒内掉了 e_burst% 以上，或者身边 35000 内 e_crowd 个以上敌方英雄）
//!   就闪回去（强制位移，速度 e_back；被控着的那几拍不闪，等控制完），回来时减伤。
//!
//! 日志写在本包的 border.log 里（行首 `fusuo`）。

use std::collections::{HashMap, VecDeque};

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_fusuo";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const TRACK: &str = "border_fusuo_track";
const Q_MARK: &str = "border_fusuo_q_";
const ANCHOR: &str = "border_fusuo_anchor_";
const CLASP_MS: &str = "border_fusuo_e_ms";
const BACK_DR: &str = "border_fusuo_e_dr";
const VIEW_HIT: &str = "border_fusuo_a_hit";
const VIEW_TRACK: &str = "border_fusuo_p_track";
const VIEW_ANCHOR: &str = "border_fusuo_e_anchor";
const VIEW_RECALL: &str = "border_fusuo_e_recall";
/// 留扣：身边这么近的敌方英雄算在围他
const CROWD_R: f64 = 35_000.0;

pub static P: Params = Params::new(&[
    ("e_back", 8000), ("e_burst", 25), ("e_crowd", 3), ("e_dr", 30), ("e_dr_t", 30), ("e_low", 35),
    ("e_ms", 35), ("e_ms_t", 90), ("e_win", 240), ("p_alone", 50000), ("p_dmg", 15), ("p_keep", 180),
    ("p_steps", 60), ("q_ad", 160), ("q_dmg", 110), ("q_dur", 34), ("q_hit_r", 32000), ("q_reach", 60000),
    ("q_speed", 4000), ("q_stop", 14000), ("q_track", 30),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("fusuo [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 规则（单元测试用） =====================

/// 这一拍数不数步：离最近的队友 `gap`（没有活着的队友是无穷大），上一拍 `last`。
pub fn step_on(gap: f64, last: f64, alone: f64) -> bool {
    gap > alone && gap + 500.0 >= last
}

/// 回撤点写进 buff 名字，再读回来。
pub fn anchor_name(at: Pt) -> String {
    format!("{ANCHOR}{}_{}", at.0.max(0.0).round() as u64, at.1.max(0.0).round() as u64)
}

pub fn parse_anchor(name: &str) -> Option<Pt> {
    let rest = name.strip_prefix(ANCHOR)?;
    let (x, y) = rest.split_once('_')?;
    Some((x.parse::<u64>().ok()? as f64, y.parse::<u64>().ok()? as f64))
}

/// 留扣：危险了没有。
pub fn danger(hp_pct: usize, lost_pct: usize, crowd: usize, low: usize, burst: usize, crowd_min: usize) -> bool {
    hp_pct < low || lost_pct >= burst || crowd >= crowd_min
}

// ===================== 被动：数步 =====================

#[derive(Clone, Copy, Debug, Default)]
struct Watch {
    steps: usize,
    last_gap: f64,
    tracked: bool,
}

#[derive(Clone, Default)]
struct Steps {
    me: usize,
    watch: HashMap<usize, Watch>,
    /// 最近一秒每拍的血
    hp: VecDeque<(usize, usize)>,
    chat: Chatter,
}

fn anchor_of(sim: &StableSim<'_>, id: usize) -> Option<(String, Pt)> {
    buffs_of(sim, id).iter().rev().find_map(|b| parse_anchor(b.name()).map(|p| (b.name().to_string(), p)))
}

fn clear_anchors(sim: &mut StableSim<'_>, id: usize) {
    let names: Vec<String> =
        buffs_of(sim, id).iter().filter(|b| b.name().starts_with(ANCHOR)).map(|b| b.name().to_string()).collect();
    for n in names {
        sim.entity_remove_buff(id, &n);
    }
}

impl Steps {
    fn track(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(team) = team_of(sim, me) else { return };
        let foes = live_champions(sim, team, false);
        let alone = P.f("p_alone");
        for &e in &foes {
            let Some(p) = pos_of(sim, e) else { continue };
            let gap = foes
                .iter()
                .filter(|&&o| o != e)
                .filter_map(|&o| pos_of(sim, o))
                .map(|q| dist(p, q))
                .fold(f64::INFINITY, f64::min);
            let seen = sim.is_visible(team, e);
            let w = self.watch.entry(e).or_default();
            if seen && step_on(gap, w.last_gap, alone) {
                w.steps += 1;
            } else {
                w.steps = w.steps.saturating_sub(2);
            }
            w.last_gap = if gap.is_finite() { gap } else { 1e9 };
            let on = w.steps >= P.get("p_steps");
            let fresh = on && !w.tracked;
            w.tracked = on || (w.tracked && has_buff(sim, e, TRACK));
            if on {
                sim.entity_stack_buff(e, &BuffV1::timed(TRACK, P.get("p_keep")), 1, true);
            }
            if fresh {
                sim.play_view_effect(VIEW_TRACK, me, &InputTargetV1::target(e), 0, 0, 0);
                log(sim, format!("TRACK #{me} -> #{e} (alone, {gap:.0} from the nearest ally)"));
            }
        }
        self.watch.retain(|id, _| foes.contains(id));
    }

    fn clasp(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (now, max) = e.hp();
        self.hp.push_back((tick, now));
        while self.hp.front().is_some_and(|&(t, _)| t + SECOND < tick) {
            self.hp.pop_front();
        }
        let Some((_, anchor)) = anchor_of(sim, me) else { return };
        if held(sim, me) {
            return;
        }
        let Some(at) = pos_of(sim, me) else { return };
        let Some(team) = team_of(sim, me) else { return };
        let peak = self.hp.iter().map(|h| h.1).max().unwrap_or(now);
        let lost_pct = (peak.saturating_sub(now) * 100).checked_div(max).unwrap_or(0);
        let hp_pct = (now * 100).checked_div(max).unwrap_or(100);
        let crowd = live_champions(sim, team, false)
            .into_iter()
            .filter(|&f| pos_of(sim, f).is_some_and(|p| dist(at, p) <= CROWD_R))
            .count();
        if !danger(hp_pct, lost_pct, crowd, P.get("e_low"), P.get("e_burst"), P.get("e_crowd")) {
            return;
        }
        clear_anchors(sim, me);
        let d = dist(at, anchor);
        let mut ticks = 0;
        if d >= 2_000.0 {
            let speed = P.f("e_back").max(1.0);
            ticks = (d / speed).ceil().min(30.0) as u64;
            let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks);
            mv.dx = (anchor.0 - at.0).round() as i64;
            mv.dy = (anchor.1 - at.1).round() as i64;
            mv.speed = (d / ticks as f64).ceil() as u64;
            sim.apply_cc(me, &mv);
        }
        let mut dr = BuffV1::timed(BACK_DR, P.get("e_dr_t") + ticks as usize);
        dr.damaged_reduce = P.get("e_dr");
        sim.add_buff(me, &dr);
        sim.play_view_effect(VIEW_RECALL, me, &InputTargetV1::target(me), 0, 0, 0);
        log(sim, format!("RECALL #{me}: hp {hp_pct}%, lost {lost_pct}% in 1 s, {crowd} round him -> back {d:.0} \
                          over {ticks} ticks"));
    }
}

impl StablePassive for Steps {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        P.configure(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.chat.spawned();
        self.hp.clear();
        log(sim, format!("SPAWN #{me}: border.dll's Fu Suo (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.hp.clear();
            return;
        }
        self.chat.tick(sim, ID, player, me);
        self.track(sim, me);
        self.clasp(sim, me);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        if has_buff(sim, target, TRACK) && team_of(sim, target) != team_of(sim, me) {
            *damage += *damage * P.get("p_dmg") / 100;
        }
        self.chat.attacked(sim, ID, me, target);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _attacker: usize, damage: usize) {
        self.chat.damaged(sim, ID, me, damage);
        self.chat.flinch(sim, ID, me, damage);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.chat.killed(sim, ID, me, victim);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        let me = self.me;
        self.hp.clear();
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
}

fn tracked_near(sim: &StableSim<'_>, caster: usize, reach: f64) -> Option<usize> {
    let at = pos_of(sim, caster)?;
    let team = team_of(sim, caster)?;
    live_champions(sim, team, false)
        .into_iter()
        .filter(|&e| has_buff(sim, e, TRACK))
        .filter_map(|e| pos_of(sim, e).map(|p| (e, dist(at, p))))
        .filter(|&(_, d)| d <= reach)
        .min_by(|a, b| a.1.total_cmp(&b.1))
        .map(|x| x.0)
}

struct Skim;

impl StableEffectType for Skim {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) || held(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let prey = tracked_near(sim, caster, P.f("q_reach"));
        let Some(t) = prey.or_else(|| target_of(&input).filter(|&t| hittable_enemy(sim, team, t))) else { return };
        let Some(to) = pos_of(sim, t) else { return };
        let d = dist(at, to);
        let go = d - P.f("q_stop");
        let names: Vec<String> =
            buffs_of(sim, caster).iter().filter(|b| b.name().starts_with(Q_MARK)).map(|b| b.name().to_string()).collect();
        for n in names {
            sim.entity_remove_buff(caster, &n);
        }
        sim.add_buff(caster, &BuffV1::timed(&format!("{Q_MARK}{t}"), 24));
        if go > 2_000.0 {
            let speed = P.f("q_speed").max(1.0);
            let ticks = (go / speed).ceil().min(14.0) as u64;
            let u = unit((to.0 - at.0, to.1 - at.1)).unwrap_or((1.0, 0.0));
            let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks);
            mv.dx = (u.0 * go).round() as i64;
            mv.dy = (u.1 * go).round() as i64;
            mv.speed = (go / ticks as f64).ceil() as u64;
            sim.apply_cc(caster, &mv);
            let mut pose = CcV1::of_kind(CcKindV1::Animation, P.get("q_dur").saturating_sub(2) as u64);
            pose.set_name("skill");
            sim.apply_cc(caster, &pose);
        }
        log(sim, format!("SKIM #{caster} -> #{t}{} {go:.0} away", if prey.is_some() { " (tracked)" } else { "" }));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("q_dmg") + s.attack * P.get("q_ad") / 100, 0)
    }

    fn expected_move_distance(&self) -> Option<(usize, u64)> {
        Some((10, P.get("q_reach") as u64))
    }
}

struct SkimHit;

impl StableEffectType for SkimHit {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let reach = P.f("q_hit_r");
        let marked = buffs_of(sim, caster)
            .iter()
            .rev()
            .find_map(|b| b.name().strip_prefix(Q_MARK).and_then(|s| s.parse::<usize>().ok()));
        let near = |id: usize| hittable_enemy(sim, team, id) && pos_of(sim, id).is_some_and(|p| dist(at, p) <= reach);
        let t = marked.filter(|&m| near(m)).or_else(|| {
            all_units(sim)
                .into_iter()
                .filter(|&u| near(u))
                .min_by(|a, b| {
                    let (pa, pb) = (pos_of(sim, *a).unwrap_or(at), pos_of(sim, *b).unwrap_or(at));
                    dist(at, pa).total_cmp(&dist(at, pb))
                })
        });
        let Some(t) = t else {
            log(sim, format!("SKIM HIT #{caster}: nobody in reach"));
            return;
        };
        let mut dmg = amount(sim, caster, P.get("q_dmg"), P.get("q_ad"), 0, 0);
        if has_buff(sim, t, TRACK) {
            dmg += dmg * P.get("q_track") / 100;
        }
        sim.deal_damage(caster, t, dmg, 0, AttackTypeV1::Skill);
        sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(t), 0, 0, 0);
        log(sim, format!("SKIM HIT #{caster} -> #{t} {dmg}"));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("q_dmg") + s.attack * P.get("q_ad") / 100, 0)
    }
}

struct Clasp;

impl StableEffectType for Clasp {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(at) = pos_of(sim, caster) else { return };
        clear_anchors(sim, caster);
        sim.add_buff(caster, &BuffV1::timed(&anchor_name(at), P.get("e_win")));
        let mut ms = BuffV1::timed(CLASP_MS, P.get("e_ms_t"));
        ms.move_speed_mult = P.get("e_ms") as i32;
        sim.entity_remove_buff(caster, CLASP_MS);
        sim.add_buff(caster, &ms);
        let spot = InputTargetV1::pos(at.0 as u64, at.1 as u64);
        sim.play_view_effect(VIEW_ANCHOR, caster, &spot, 0, 0, 0);
        log(sim, format!("CLASP #{caster} at ({:.0}, {:.0})", at.0, at.1));
    }

    fn expected_buff(&self, _s: &StatV1) -> Option<BuffV1> {
        let mut ms = BuffV1::timed(CLASP_MS, P.get("e_ms_t"));
        ms.move_speed_mult = P.get("e_ms") as i32;
        Some(ms)
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("fusuo: {ID} v{VERSION} (Fu Suo: counting steps, skim, clasp) registered"));
    module.add_native_passive(format!("{ID}:steps"), Steps::default());
    module.add_native_effect(format!("{ID}:skim"), Skim);
    module.add_native_effect(format!("{ID}:skim_hit"), SkimHit);
    module.add_native_effect(format!("{ID}:clasp"), Clasp);
    host.log(LogLevel::Info, "border.dll: Fu Suo (counting steps, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn steps_count_only_while_alone_and_not_coming_back() {
        assert!(step_on(60_000.0, 58_000.0, 50_000.0));
        assert!(step_on(60_000.0, 60_300.0, 50_000.0));
        assert!(!step_on(60_000.0, 62_000.0, 50_000.0));
        assert!(!step_on(40_000.0, 30_000.0, 50_000.0));
        assert!(step_on(f64::INFINITY, 1e9, 50_000.0));
    }

    #[test]
    fn the_anchor_rides_in_the_buff_name() {
        let n = anchor_name((480_123.4, 12_000.0));
        assert_eq!(n, "border_fusuo_anchor_480123_12000");
        assert!(n.len() <= BUFF_NAME_CAP);
        assert_eq!(parse_anchor(&n), Some((480_123.0, 12_000.0)));
        assert_eq!(parse_anchor("border_fusuo_track"), None);
    }

    #[test]
    fn danger_is_low_health_a_burst_or_a_crowd() {
        assert!(danger(30, 0, 0, 35, 25, 3));
        assert!(danger(80, 25, 0, 35, 25, 3));
        assert!(danger(80, 0, 3, 35, 25, 3));
        assert!(!danger(80, 10, 2, 35, 25, 3));
    }
}
