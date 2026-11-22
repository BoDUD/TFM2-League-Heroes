//! 雾绫（`border_wuling`）数据做不到的部分。数据：tools/kit/build_wuling.py（参数表 P；`passive` 是这里的
//! `border_wuling:bell`）。
//!
//! - **闻铃**（被动）：敌人第一次碰到她的技能区域就挂铃（`border_wuling_bell`，p_t 拍，身上一只小铃）；挂着铃的人掉血时，离他
//!   p_ally_r 内的友方英雄移速 +p_ms%（`border_wuling_p_ms`，p_ms_t 拍）。
//! - **系铃**（`bell_drop`）：目标脚下放地铃，位置写在她身上（`border_wuling_belat_<x>_<y>`，q_t 拍）。被动每拍看：有敌人走到
//!   q_trig 内就响（伤害、减速、挂铃），铃收起。
//! - **挪幕**（`curtain`）：她到目标 e_frac% 处竖起一道短幕，写在她身上（`border_wuling_veil_<中点>_<方向>`，e_t 拍）。被动每拍看
//!   谁换到了幕的另一边：友方英雄加速（每人每道幕一次），敌人挂铃、减速。纱幕是竖着的地上画面（不转）。
//! - **合幕**（`close` 第 3 帧、`close_hit` r_land 拍后）：目标脚下合幕，位置写在她身上（`border_wuling_closeat_<x>_<y>`）；
//!   合上时圈里的敌人每人一次：伤害、减速、定身、挂铃。塞拉斯偷去的是数据版，不走这里。
//!
//! 日志写在本包的 border.log 里（行首 `wuling`）。

use std::collections::{HashMap, HashSet};

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_wuling";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const MARK: &str = "border_wuling_bell";
const BELL_AT: &str = "border_wuling_belat_";
const VEIL: &str = "border_wuling_veil_";
const CLOSE_AT: &str = "border_wuling_closeat_";
const P_MS: &str = "border_wuling_p_ms";
const E_MS: &str = "border_wuling_e_ms";
const Q_SLOW: &str = "border_wuling_q_slow";
const E_SLOW: &str = "border_wuling_e_slow";
const R_SLOW: &str = "border_wuling_r_slow";
const VIEW_HIT: &str = "border_wuling_a_hit";
const VIEW_MARK: &str = "border_wuling_p_bell";
const VIEW_BELL: &str = "border_wuling_q_bell";
const VIEW_RIPPLE: &str = "border_wuling_q_ripple";
const VIEW_CURTAIN: &str = "border_wuling_e_curtain";
const VIEW_CLOSE: &str = "border_wuling_r_close";

pub static P: Params = Params::new(&[
    ("e_frac", 40), ("e_len", 30000), ("e_ms", 30), ("e_ms_t", 120), ("e_slow", 30), ("e_slow_t", 60), ("e_t", 240),
    ("p_ally_r", 60000), ("p_ms", 15), ("p_ms_t", 60), ("p_t", 300), ("q_ap", 60), ("q_dmg", 75), ("q_r", 26000),
    ("q_slow", 50), ("q_slow_t", 90), ("q_t", 300), ("q_trig", 16000), ("r_ap", 80), ("r_dmg", 160), ("r_land", 12),
    ("r_r", 33000), ("r_root", 75), ("r_slow", 45), ("r_slow_t", 30),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("wuling [t={}] #{n} {msg}", sim.tick()));
    }
}

/// 挂铃（第一次挂上时亮一下小铃）。
fn ring(sim: &mut StableSim<'_>, caster: usize, id: usize) {
    if !has_buff(sim, id, MARK) {
        sim.play_view_effect(VIEW_MARK, caster, &InputTargetV1::target(id), 0, 0, 0);
    }
    sim.entity_stack_buff(id, &BuffV1::timed(MARK, P.get("p_t")), 1, true);
}

// ===================== 被动：闻铃、地铃、纱幕 =====================

#[derive(Clone, Default)]
struct Bell {
    me: usize,
    /// 挂铃的敌人上一拍的血
    hp: HashMap<usize, usize>,
    sides: HashMap<(String, usize), f64>,
    crossed: HashSet<(String, usize)>,
    chat: Chatter,
}

impl Bell {
    fn bells(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        for (name, v) in named(sim, me, BELL_AT, 2) {
            let at = (v[0] as f64, v[1] as f64);
            if enemies_near(sim, team, at, P.f("q_trig")).is_empty() {
                continue;
            }
            sim.entity_remove_buff(me, &name);
            sim.play_view_effect(VIEW_RIPPLE, me, &InputTargetV1::pos(at.0 as u64, at.1 as u64), 0, 0, 0);
            let dmg = amount(sim, me, P.get("q_dmg"), 0, P.get("q_ap"), 0);
            let hit = enemies_near(sim, team, at, P.f("q_r"));
            for &id in &hit {
                sim.deal_damage(me, id, 0, dmg, AttackTypeV1::Skill);
                sim.add_buff(id, &slow_buff(Q_SLOW, P.get("q_slow"), P.get("q_slow_t")));
                ring(sim, me, id);
            }
            log(sim, format!("BELL #{me} rang at ({:.0}, {:.0}): {} hit for {dmg}", at.0, at.1, hit.len()));
        }
    }

    fn veils(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let veils: Vec<(String, Seg)> =
            named(sim, me, VEIL, 4).into_iter().filter_map(|(n, _)| Seg::parse(VEIL, &n).map(|s| (n, s))).collect();
        if veils.is_empty() {
            self.sides.clear();
            self.crossed.clear();
            return;
        }
        let half = P.f("e_len") / 2.0;
        let mut units: Vec<(usize, bool)> = live_champions(sim, team, true).into_iter().map(|a| (a, true)).collect();
        units.extend(all_units(sim).into_iter().filter(|&id| hittable_enemy(sim, team, id)).map(|e| (e, false)));
        for (name, seg) in &veils {
            for &(id, friend) in &units {
                let Some(p) = pos_of(sim, id) else { continue };
                if seg.along(p).abs() > half + body_of(sim, id) {
                    self.sides.remove(&(name.clone(), id));
                    continue;
                }
                let side = seg.across(p);
                let key = (name.clone(), id);
                let before = self.sides.insert(key.clone(), side);
                if !(before.is_some_and(|b| b * side < 0.0) && self.crossed.insert(key)) {
                    continue;
                }
                if friend {
                    let mut ms = BuffV1::timed(E_MS, P.get("e_ms_t"));
                    ms.move_speed_mult = P.get("e_ms") as i32;
                    sim.entity_remove_buff(id, E_MS);
                    sim.add_buff(id, &ms);
                } else {
                    ring(sim, me, id);
                    sim.add_buff(id, &slow_buff(E_SLOW, P.get("e_slow"), P.get("e_slow_t")));
                }
            }
        }
        let names: HashSet<String> = veils.iter().map(|v| v.0.clone()).collect();
        self.sides.retain(|k, _| names.contains(&k.0));
        self.crossed.retain(|k| names.contains(&k.0));
    }

    /// 挂铃的人掉血：他身边的友方英雄加速。
    fn chase(&mut self, sim: &mut StableSim<'_>, team: usize) {
        let marked: Vec<usize> = live_champions(sim, team, false).into_iter().filter(|&e| has_buff(sim, e, MARK)).collect();
        let allies = live_champions(sim, team, true);
        for &e in &marked {
            let now = sim.get_entity(e).map_or(0, |x| x.hp().0);
            let before = self.hp.insert(e, now);
            if before.is_none_or(|b| b <= now) {
                continue;
            }
            let Some(p) = pos_of(sim, e) else { continue };
            for &a in &allies {
                if pos_of(sim, a).is_some_and(|q| dist(p, q) <= P.f("p_ally_r")) {
                    let mut ms = BuffV1::timed(P_MS, P.get("p_ms_t"));
                    ms.move_speed_mult = P.get("p_ms") as i32;
                    sim.entity_stack_buff(a, &ms, 1, true);
                }
            }
        }
        self.hp.retain(|id, _| marked.contains(id));
    }
}

impl StablePassive for Bell {
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
        log(sim, format!("SPAWN #{me}: border.dll's Wu Ling (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.hp.clear();
            return;
        }
        self.chat.tick(sim, ID, player, me);
        let Some(team) = team_of(sim, me) else { return };
        self.bells(sim, me, team);
        self.veils(sim, me, team);
        self.chase(sim, team);
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
        self.hp.clear();
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

struct BellDrop;

impl StableEffectType for BellDrop {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(at) = target_of(&input).and_then(|t| pos_of(sim, t)) else { return };
        clear_named(sim, caster, BELL_AT, 2);
        sim.add_buff(caster, &BuffV1::timed(&pt_name(BELL_AT, at), P.get("q_t")));
        sim.play_view_effect(VIEW_BELL, caster, &InputTargetV1::pos(at.0 as u64, at.1 as u64), 0, 0, 0);
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (0, P.get("q_dmg") + s.magic_power * P.get("q_ap") / 100)
    }
}

struct Curtain;

impl StableEffectType for Curtain {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(at) = pos_of(sim, caster) else { return };
        let Some(to) = target_of(&input).and_then(|t| pos_of(sim, t)) else { return };
        let f = P.f("e_frac") / 100.0;
        let c = (at.0 + (to.0 - at.0) * f, at.1 + (to.1 - at.1) * f);
        let u = unit((to.0 - at.0, to.1 - at.1)).unwrap_or((1.0, 0.0));
        let seg = Seg { c, d: (-u.1, u.0) };
        clear_named(sim, caster, VEIL, 4);
        sim.add_buff(caster, &BuffV1::timed(&seg.name(VEIL), P.get("e_t")));
        sim.play_view_effect(VIEW_CURTAIN, caster, &InputTargetV1::pos(c.0 as u64, c.1 as u64), 0, 0, 0);
        log(sim, format!("CURTAIN #{caster} at ({:.0}, {:.0})", c.0, c.1));
    }
}

struct Close;

impl StableEffectType for Close {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(at) = target_of(&input).and_then(|t| pos_of(sim, t)) else { return };
        clear_named(sim, caster, CLOSE_AT, 2);
        sim.add_buff(caster, &BuffV1::timed(&pt_name(CLOSE_AT, at), P.get("r_land") + 10));
        sim.play_view_effect(VIEW_CLOSE, caster, &InputTargetV1::pos(at.0 as u64, at.1 as u64), 0, 0, 0);
    }
}

struct CloseHit;

impl StableEffectType for CloseHit {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(team) = team_of(sim, caster) else { return };
        let Some(at) = named(sim, caster, CLOSE_AT, 2).last().map(|(_, v)| (v[0] as f64, v[1] as f64)) else { return };
        clear_named(sim, caster, CLOSE_AT, 2);
        let dmg = amount(sim, caster, P.get("r_dmg"), 0, P.get("r_ap"), 0);
        let hit = enemies_near(sim, team, at, P.f("r_r"));
        // 每人只结算一次：这一遍就是全部
        for &id in &hit {
            sim.deal_damage(caster, id, 0, dmg, AttackTypeV1::Skill);
            sim.add_buff(id, &slow_buff(R_SLOW, P.get("r_slow"), P.get("r_slow_t")));
            if !cc_immune(sim, id) {
                sim.apply_cc(id, &CcV1::of_kind(CcKindV1::Bind, P.get("r_root") as u64));
            }
            ring(sim, caster, id);
            sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(id), 0, 0, 0);
        }
        log(sim, format!("CLOSE #{caster}: {} caught for {dmg}", hit.len()));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (0, P.get("r_dmg") + s.magic_power * P.get("r_ap") / 100)
    }

    fn expected_cc_time(&self) -> Option<usize> {
        Some(P.get("r_root"))
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("wuling: {ID} v{VERSION} (Wu Ling: hear the bell, ground bell, curtains) registered"));
    module.add_native_passive(format!("{ID}:bell"), Bell::default());
    module.add_native_effect(format!("{ID}:bell_drop"), BellDrop);
    module.add_native_effect(format!("{ID}:curtain"), Curtain);
    module.add_native_effect(format!("{ID}:close"), Close);
    module.add_native_effect(format!("{ID}:close_hit"), CloseHit);
    host.log(LogLevel::Info, "border.dll: Wu Ling (bells and curtains, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn prefixes_do_not_swallow_other_buffs() {
        // 带数的才算：border_wuling_veil_ 的名字和别的 buff 不撞
        assert!(parse_pt(BELL_AT, "border_wuling_belat_120_340").is_some());
        assert!(parse_pt(BELL_AT, MARK).is_none());
        assert!(Seg::parse(VEIL, E_MS).is_none());
    }
}
