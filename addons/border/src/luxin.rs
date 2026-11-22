//! 鹭芯（`border_luxin`）数据做不到的部分。数据：tools/kit/build_luxin.py（参数表 P；`passive` 是这里的
//! `border_luxin:feather`）。
//!
//! - **追羽**（被动）：她打到的敌方英雄挂 `border_luxin_hit`（p_window 拍）；之后他离她越走越远（一拍远 p_away 以上），连着
//!   p_every 拍就在他脚下留一段羽迹：他逃的方向写在他身上（`border_luxin_trail_<dx>_<dy>`，p_t 拍，最多两段，新的顶掉旧的）。
//! - **贴风**（`cling` 第 1 拍、`cling_hit` 第 3 帧）：顺着目标最近一段羽迹的方向（没有就直冲）提前 q_lead 追过去，停在他面前，
//!   第 3 帧切他。
//! - **折鸢**（`kite`）：在目标脚下横着拉一道风线（和他逃的方向垂直），线写在她身上（`border_luxin_kite_<中点>_<方向>`，e_t 拍），
//!   画面是转到线方向的弹道（朝左时 `_l`）。被动每拍看敌人在线的哪一边，换了边就是穿过去了：伤害、减速（每人每条线一次）。
//! - **收线**（`reel1` 第 3 帧、`reel2`）：顺着目标的第一段、第二段羽迹（没有就从她这边、再反方向）各穿过他切一刀，每刀沿
//!   实际冲的方向亮一道切光（转到冲的方向的弹道画面）；第二刀按他掉的生命加成，每段羽迹再加；切完羽迹用掉。
//!
//! 日志写在本包的 border.log 里（行首 `luxin`）。

use std::collections::{HashMap, HashSet};

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_luxin";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const HIT_BY: &str = "border_luxin_hit";
const TRAIL: &str = "border_luxin_trail_";
const KITE: &str = "border_luxin_kite_";
const Q_MARK: &str = "border_luxin_q_";
const E_SLOW: &str = "border_luxin_e_slow";
const VIEW_HIT: &str = "border_luxin_a_hit";
const VIEW_FEATHER: &str = "border_luxin_p_feather";
const NOOP: &str = "border_luxin:noop";

pub static P: Params = Params::new(&[
    ("e_ad", 60), ("e_dmg", 40), ("e_len", 40000), ("e_slow", 40), ("e_slow_t", 90), ("e_t", 240), ("p_away", 300),
    ("p_every", 30), ("p_t", 240), ("p_window", 240), ("q_ad", 130), ("q_dmg", 80), ("q_dur", 34),
    ("q_hit_r", 30000), ("q_lead", 8000), ("q_speed", 4500), ("q_stop", 12000), ("r_ad", 100), ("r_dmg", 120),
    ("r_low", 60), ("r_speed", 6000), ("r_through", 18000), ("r_trail", 20),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("luxin [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 规则（单元测试用） =====================

/// 第二刀：他掉了 (1 - hp_ratio) 的生命，加成最多 r_low%。
pub fn second_cut(dmg: usize, hp_ratio: f64, r_low: usize) -> usize {
    let missing = (1.0 - hp_ratio).clamp(0.0, 1.0);
    dmg + (dmg as f64 * missing * r_low as f64 / 100.0).round() as usize
}

fn trail_name(d: Pt) -> String {
    format!("{TRAIL}{}_{}", enc_dir(d.0), enc_dir(d.1))
}

/// 他身上的羽迹（先留的在前）。
fn trails_of(sim: &StableSim<'_>, id: usize) -> Vec<Pt> {
    named(sim, id, TRAIL, 2).iter().filter_map(|(_, v)| unit((dec_dir(v[0]), dec_dir(v[1])))).collect()
}

// ===================== 被动：追羽、风线 =====================

#[derive(Clone, Copy, Default)]
struct Flee {
    last_d: f64,
    last_at: Option<Pt>,
    run: usize,
}

#[derive(Clone, Default)]
struct Feather {
    me: usize,
    flee: HashMap<usize, Flee>,
    /// 每条风线上每个单位上一拍在哪一边
    sides: HashMap<(String, usize), f64>,
    crossed: HashSet<(String, usize)>,
    chat: Chatter,
}

impl Feather {
    fn trails(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let (Some(at), Some(team)) = (pos_of(sim, me), team_of(sim, me)) else { return };
        let foes = live_champions(sim, team, false);
        for &e in &foes {
            let Some(p) = pos_of(sim, e) else { continue };
            let d = dist(at, p);
            let f = self.flee.entry(e).or_default();
            let hunted = has_buff(sim, e, HIT_BY);
            let away = f.last_at.is_some() && d - f.last_d >= P.f("p_away");
            let dir = f.last_at.and_then(|q| unit((p.0 - q.0, p.1 - q.1)));
            f.last_d = d;
            f.last_at = Some(p);
            if !(hunted && away) {
                f.run = 0;
                continue;
            }
            f.run += 1;
            if !f.run.is_multiple_of(P.get("p_every").max(1)) {
                continue;
            }
            let Some(dir) = dir else { continue };
            // 最多两段：新的顶掉最旧的
            let old = named(sim, e, TRAIL, 2);
            if old.len() >= 2 {
                sim.entity_remove_buff(e, &old[0].0);
            }
            sim.add_buff(e, &BuffV1::timed(&trail_name(dir), P.get("p_t")));
            sim.play_view_effect(VIEW_FEATHER, me, &InputTargetV1::pos(p.0 as u64, p.1 as u64), 0, 0, 0);
            log(sim, format!("TRAIL #{e} flees ({:.2}, {:.2})", dir.0, dir.1));
        }
        self.flee.retain(|id, _| foes.contains(id));
    }

    fn kites(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let lines: Vec<(String, Seg)> =
            named(sim, me, KITE, 4).into_iter().filter_map(|(n, _)| Seg::parse(KITE, &n).map(|s| (n, s))).collect();
        if lines.is_empty() {
            self.sides.clear();
            self.crossed.clear();
            return;
        }
        let Some(team) = team_of(sim, me) else { return };
        let half = P.f("e_len") / 2.0;
        let units: Vec<usize> = all_units(sim).into_iter().filter(|&id| hittable_enemy(sim, team, id)).collect();
        for (name, seg) in &lines {
            for &id in &units {
                let Some(p) = pos_of(sim, id) else { continue };
                if seg.along(p).abs() > half + body_of(sim, id) {
                    self.sides.remove(&(name.clone(), id));
                    continue;
                }
                let side = seg.across(p);
                let key = (name.clone(), id);
                let before = self.sides.insert(key.clone(), side);
                if before.is_some_and(|b| b * side < 0.0) && self.crossed.insert(key) {
                    let dmg = amount(sim, me, P.get("e_dmg"), P.get("e_ad"), 0, 0);
                    sim.deal_damage(me, id, dmg, 0, AttackTypeV1::Skill);
                    sim.add_buff(id, &slow_buff(E_SLOW, P.get("e_slow"), P.get("e_slow_t")));
                    sim.play_view_effect(VIEW_HIT, me, &InputTargetV1::target(id), 0, 0, 0);
                    log(sim, format!("KITE #{id} crossed the wind line: {dmg}"));
                }
            }
        }
        let names: HashSet<String> = lines.iter().map(|l| l.0.clone()).collect();
        self.sides.retain(|k, _| names.contains(&k.0));
        self.crossed.retain(|k| names.contains(&k.0));
    }
}

impl StablePassive for Feather {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        P.configure(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.chat.spawned();
        self.flee.clear();
        log(sim, format!("SPAWN #{me}: border.dll's Lu Xin (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.flee.clear();
            return;
        }
        self.chat.tick(sim, ID, player, me);
        self.trails(sim, me);
        self.kites(sim, me);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        let mine = team_of(sim, me);
        if sim.get_entity(target).is_some_and(|t| t.is_champion() && Some(t.team()) != mine) {
            sim.entity_stack_buff(target, &BuffV1::timed(HIT_BY, P.get("p_window")), 1, true);
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
        self.flee.clear();
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

struct Cling;

impl StableEffectType for Cling {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) || held(sim, caster) {
            return;
        }
        let Some(at) = pos_of(sim, caster) else { return };
        let Some(t) = target_of(&input) else { return };
        let Some(tp) = pos_of(sim, t) else { return };
        let ahead = trails_of(sim, t).last().copied().map_or(tp, |v| (tp.0 + v.0 * P.f("q_lead"), tp.1 + v.1 * P.f("q_lead")));
        let d = dist(at, ahead) - P.f("q_stop");
        clear_named(sim, caster, Q_MARK, 1);
        sim.add_buff(caster, &BuffV1::timed(&format!("{Q_MARK}{t}"), 24));
        if d > 2_000.0 {
            let u = unit((ahead.0 - at.0, ahead.1 - at.1)).unwrap_or((1.0, 0.0));
            force_move(sim, caster, at, (at.0 + u.0 * d, at.1 + u.1 * d), P.f("q_speed"), 12);
            hold_pose(sim, caster, "skill", P.get("q_dur").saturating_sub(2));
        }
        log(sim, format!("CLING #{caster} -> #{t} {d:.0}"));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("q_dmg") + s.attack * P.get("q_ad") / 100, 0)
    }
}

struct ClingHit;

impl StableEffectType for ClingHit {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let reach = P.f("q_hit_r");
        let near = |id: usize| hittable_enemy(sim, team, id) && pos_of(sim, id).is_some_and(|p| dist(at, p) <= reach);
        let marked = named(sim, caster, Q_MARK, 1).last().map(|(_, v)| v[0] as usize);
        let t = marked.filter(|&m| near(m)).or_else(|| {
            all_units(sim).into_iter().filter(|&u| near(u)).min_by(|a, b| {
                let (pa, pb) = (pos_of(sim, *a).unwrap_or(at), pos_of(sim, *b).unwrap_or(at));
                dist(at, pa).total_cmp(&dist(at, pb))
            })
        });
        clear_named(sim, caster, Q_MARK, 1);
        let Some(t) = t else { return };
        let dmg = amount(sim, caster, P.get("q_dmg"), P.get("q_ad"), 0, 0);
        sim.deal_damage(caster, t, dmg, 0, AttackTypeV1::Skill);
        sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(t), 0, 0, 0);
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("q_dmg") + s.attack * P.get("q_ad") / 100, 0)
    }
}

struct Kite;

impl StableEffectType for Kite {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(at) = pos_of(sim, caster) else { return };
        let Some(t) = target_of(&input) else { return };
        let Some(tp) = pos_of(sim, t) else { return };
        let flee = trails_of(sim, t).last().copied().or_else(|| unit((tp.0 - at.0, tp.1 - at.1))).unwrap_or((1.0, 0.0));
        // 风线和他逃的方向垂直
        let seg = Seg { c: tp, d: (-flee.1, flee.0) };
        clear_named(sim, caster, KITE, 4);
        sim.add_buff(caster, &BuffV1::timed(&seg.name(KITE), P.get("e_t")));
        let shown = picture(sim, caster, &lr("border_luxin_e_kite", seg.d), NOOP, seg.c, seg.d, P.get("e_t"));
        log(sim, format!("KITE #{caster} at ({:.0}, {:.0}){}", seg.c.0, seg.c.1, if shown { "" } else { " (picture refused)" }));
    }
}

/// 收线的一刀：从她现在的位置朝 `dir` 方向穿过目标冲到他身后 r_through 处，切他。
fn cut(sim: &mut StableSim<'_>, caster: usize, t: usize, dir: Option<Pt>, second: bool) {
    let Some(at) = pos_of(sim, caster) else { return };
    let Some(tp) = pos_of(sim, t) else { return };
    let u = dir.or_else(|| unit((tp.0 - at.0, tp.1 - at.1))).unwrap_or((1.0, 0.0));
    let through = P.f("r_through");
    let dest = (tp.0 + u.0 * through, tp.1 + u.1 * through);
    let moved = unit((dest.0 - at.0, dest.1 - at.1)).unwrap_or(u);
    force_move(sim, caster, at, dest, P.f("r_speed"), 14);
    // 切光沿实际冲的方向
    let mid = ((at.0 + dest.0) / 2.0, (at.1 + dest.1) / 2.0);
    picture(sim, caster, &lr("border_luxin_r_cut", moved), NOOP, mid, moved, 24);
    let trails = trails_of(sim, t).len();
    let mut dmg = amount(sim, caster, P.get("r_dmg"), P.get("r_ad"), 0, 0);
    dmg += dmg * trails * P.get("r_trail") / 100;
    if second {
        dmg = second_cut(dmg, hp_ratio(sim, t), P.get("r_low"));
    }
    sim.deal_damage(caster, t, dmg, 0, AttackTypeV1::Skill);
    sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(t), 0, 0, 0);
    log(sim, format!("REEL #{caster} -> #{t} cut {}: {dmg} ({trails} trails)", if second { 2 } else { 1 }));
}

struct Reel1;

impl StableEffectType for Reel1 {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) || held(sim, caster) {
            return;
        }
        let Some(team) = team_of(sim, caster) else { return };
        let Some(t) = target_of(&input).filter(|&t| hittable_enemy(sim, team, t)) else { return };
        let first = trails_of(sim, t).first().copied();
        cut(sim, caster, t, first, false);
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("r_dmg") + s.attack * P.get("r_ad") / 100, 0)
    }
}

struct Reel2;

impl StableEffectType for Reel2 {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) || held(sim, caster) {
            return;
        }
        let Some(team) = team_of(sim, caster) else { return };
        let Some(t) = target_of(&input).filter(|&t| hittable_enemy(sim, team, t)) else { return };
        let tr = trails_of(sim, t);
        let second = if tr.len() >= 2 { tr.last().copied() } else { None };
        cut(sim, caster, t, second, true);
        clear_named(sim, t, TRAIL, 2);
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("r_dmg") + s.attack * P.get("r_ad") / 100, 0)
    }
}

struct Noop;

impl StableEffectType for Noop {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("luxin: {ID} v{VERSION} (Lu Xin: chasing feather, cling, kite line, reel in) registered"));
    module.add_native_passive(format!("{ID}:feather"), Feather::default());
    module.add_native_effect(format!("{ID}:cling"), Cling);
    module.add_native_effect(format!("{ID}:cling_hit"), ClingHit);
    module.add_native_effect(format!("{ID}:kite"), Kite);
    module.add_native_effect(format!("{ID}:reel1"), Reel1);
    module.add_native_effect(format!("{ID}:reel2"), Reel2);
    module.add_native_effect(NOOP, Noop);
    host.log(LogLevel::Info, "border.dll: Lu Xin (chasing feather, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn the_second_cut_bites_the_wounded() {
        assert_eq!(second_cut(100, 1.0, 60), 100);
        assert_eq!(second_cut(100, 0.5, 60), 130);
        assert_eq!(second_cut(100, 0.0, 60), 160);
    }

    #[test]
    fn trails_ride_in_buff_names() {
        let n = trail_name((0.6, -0.8));
        assert!(n.len() <= BUFF_NAME_CAP);
        let v = parse_nums(TRAIL, &n).unwrap();
        assert!((dec_dir(v[0]) - 0.6).abs() < 1e-3 && (dec_dir(v[1]) + 0.8).abs() < 1e-3);
    }
}
