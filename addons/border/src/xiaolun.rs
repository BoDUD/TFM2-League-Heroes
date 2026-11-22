//! 绡轮（`border_xiaolun`）数据做不到的部分。数据：tools/kit/build_xiaolun.py（参数表 P；`passive` 是这里的
//! `border_xiaolun:string`）。
//!
//! - **走弦**（被动）：按她实际挪过的距离上弦（每拍量一次位置；一拍跳出 JUMP 以上算传送、复活，不算；被推、自己侧移都算），
//!   走 p_full 上满。十层挂在她身上（`border_xiaolun_tension`，放扣读它），满了挂 `border_xiaolun_taut`、绕起玻璃环，下一发
//!   普攻带加成（数据在弹道打中时摘掉 taut，这里看到就把弦清零）。
//! - **切角**（`border_xiaolun:sidestep`，出手第 1 拍）：朝目标的侧面强制位移 q_step（宿主每拍挪她，撞墙就停，画面上是
//!   连着滑过去的），两边挑离别的敌方英雄远、还在地图里的那边；滑的时候摆着技能的姿势。第 3 帧那一箭在数据里。
//! - **放扣**（`border_xiaolun:latch`）：读施法的人身上的张力层数，换 e_t 拍攻速，放掉弦。
//! - **满弧**（`border_xiaolun:arc`，三次）：每一次放的时候重新挑目标（原目标还能打就打他，不然 r_reach 内生命比例最低的
//!   敌方英雄，再不然最近的敌方单位），放一支原生投射物 `border_xiaolun_r_arrow`（追着目标飞），打中走 `arc_hit`。被控住的
//!   那一下不放。
//!
//! 日志写在本包的 border.log 里（行首 `xiaolun`）。

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_xiaolun";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const TENSION: &str = "border_xiaolun_tension";
pub const TAUT: &str = "border_xiaolun_taut";
const LATCH_AS: &str = "border_xiaolun_latch_as";
pub const R_ARROW: &str = "border_xiaolun_r_arrow";
const VIEW_RING: &str = "border_xiaolun_p_ring";
const VIEW_HIT: &str = "border_xiaolun_a_hit";
pub const LEVELS: usize = 10;
/// 一拍挪得比这远就是传送、复活（不上弦），挪得多也最多算 STEP_MAX
const JUMP: f64 = 20_000.0;
const STEP_MAX: f64 = 6_000.0;
/// 地图（960000 见方）里留的边
const MAP_LO: f64 = 12_000.0;
const MAP_HI: f64 = 948_000.0;

pub static P: Params = Params::new(&[
    ("e_as", 35), ("e_as_k", 5), ("e_t", 180), ("p_full", 100000), ("q_dur", 34), ("q_step", 18000),
    ("q_step_t", 12), ("r_ad", 90), ("r_dmg", 120), ("r_reach", 78000), ("r_speed", 9000),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("xiaolun [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 规则（单元测试用） =====================

/// 这一拍挪了 `step`：上多少弦（满弦 100）。
pub fn wind(step: f64, full: f64) -> f64 {
    if !(0.0..JUMP).contains(&step) || full <= 0.0 {
        return 0.0;
    }
    step.min(STEP_MAX) * 100.0 / full
}

/// 侧移往哪边：从 `at` 朝目标 `to` 的两个侧面里，挑终点离 `foes`（别的敌方英雄）最近的那个最远、还在地图里的。
pub fn side(at: Pt, to: Pt, step: f64, foes: &[Pt]) -> Option<Pt> {
    let v = unit((to.0 - at.0, to.1 - at.1))?;
    let mut best: Option<(f64, Pt)> = None;
    for s in [(-v.1, v.0), (v.1, -v.0)] {
        let end = (at.0 + s.0 * step, at.1 + s.1 * step);
        let inside = (MAP_LO..=MAP_HI).contains(&end.0) && (MAP_LO..=MAP_HI).contains(&end.1);
        let room = foes.iter().map(|f| dist(*f, end)).fold(1e12, f64::min);
        let score = room + if inside { 0.0 } else { -1e13 };
        if best.is_none_or(|b| score > b.0) {
            best = Some((score, s));
        }
    }
    best.map(|b| b.1)
}

// ===================== 被动：走弦 =====================

#[derive(Clone, Default)]
struct String_ {
    me: usize,
    tension: f64,
    last: Option<Pt>,
    shown: usize,
    taut: bool,
    chat: Chatter,
}

impl String_ {
    fn reset(&mut self) {
        self.tension = 0.0;
        self.shown = 0;
        self.taut = false;
        self.last = None;
    }
}

impl StablePassive for String_ {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        P.configure(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.chat.spawned();
        self.reset();
        log(sim, format!("SPAWN #{me}: border.dll's Xiao Lun (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.reset();
            return;
        }
        self.chat.tick(sim, ID, player, me);
        let at = pos_of(sim, me);
        if let (Some(a), Some(b)) = (self.last, at) {
            self.tension += wind(dist(a, b), P.f("p_full"));
        }
        self.last = at;
        // 放扣把弦放掉了（层数比记的少）
        let have = count_buff(sim, me, TENSION);
        if have < self.shown {
            self.tension = (have * 10) as f64;
            self.shown = have;
        }
        // 满弦那一箭打中了（数据在弹道里摘掉 taut）
        if self.taut && !has_buff(sim, me, TAUT) {
            self.taut = false;
            self.tension = 0.0;
            log(sim, format!("TAUT SHOT #{me}"));
        }
        self.tension = self.tension.min(100.0);
        let want = ((self.tension / 10.0 + 1e-9).floor() as usize).min(LEVELS);
        if want != self.shown {
            set_stacks(sim, me, TENSION, want, || BuffV1::named(TENSION));
            self.shown = want;
        }
        if self.tension >= 100.0 && !self.taut {
            if !has_buff(sim, me, TAUT) {
                sim.add_buff(me, &BuffV1::named(TAUT));
            }
            self.taut = true;
            sim.play_view_effect(VIEW_RING, me, &InputTargetV1::target(me), 0, 0, 0);
            log(sim, format!("TAUT #{me}"));
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
        self.reset();
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
}

struct Sidestep;

impl StableEffectType for Sidestep {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) || held(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let target = target_of(&input);
        let Some(to) = target.and_then(|t| pos_of(sim, t)) else { return };
        let foes: Vec<Pt> = live_champions(sim, team, false)
            .into_iter()
            .filter(|&e| Some(e) != target)
            .filter_map(|e| pos_of(sim, e))
            .collect();
        let step = P.f("q_step");
        let Some(s) = side(at, to, step, &foes) else { return };
        let ticks = P.get("q_step_t").max(1);
        let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
        mv.dx = (s.0 * step).round() as i64;
        mv.dy = (s.1 * step).round() as i64;
        mv.speed = (step / ticks as f64).ceil() as u64;
        sim.apply_cc(caster, &mv);
        // 滑的时候摆着技能的姿势（强制位移会把动作换掉）
        let mut pose = CcV1::of_kind(CcKindV1::Animation, P.get("q_dur").saturating_sub(2) as u64);
        pose.set_name("skill");
        sim.apply_cc(caster, &pose);
        log(sim, format!("SIDESTEP #{caster} ({:.2}, {:.2}) x {step:.0} over {ticks} ticks", s.0, s.1));
    }

    fn expected_move_distance(&self) -> Option<(usize, u64)> {
        Some((P.get("q_step_t"), P.get("q_step") as u64))
    }
}

struct Latch;

impl StableEffectType for Latch {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let k = count_buff(sim, caster, TENSION);
        let mut b = BuffV1::timed(LATCH_AS, P.get("e_t"));
        b.attack_speed_mult = (P.get("e_as") + k * P.get("e_as_k")) as i32;
        sim.entity_remove_buff(caster, LATCH_AS);
        sim.add_buff(caster, &b);
        sim.entity_remove_buff(caster, TENSION);
        sim.entity_remove_buff(caster, TAUT);
        log(sim, format!("LATCH #{caster}: {k} levels -> attack speed +{}%", b.attack_speed_mult));
    }

    fn expected_buff(&self, _s: &StatV1) -> Option<BuffV1> {
        let mut b = BuffV1::timed(LATCH_AS, P.get("e_t"));
        b.attack_speed_mult = (P.get("e_as") + 5 * P.get("e_as_k")) as i32;
        Some(b)
    }
}

/// 满弧这一箭射谁。
fn arc_target(sim: &StableSim<'_>, caster: usize, first: Option<usize>) -> Option<usize> {
    let at = pos_of(sim, caster)?;
    let team = team_of(sim, caster)?;
    let reach = P.f("r_reach");
    let ok = |id: usize| hittable_enemy(sim, team, id) && pos_of(sim, id).is_some_and(|p| dist(at, p) <= reach);
    if let Some(t) = first.filter(|&t| ok(t)) {
        return Some(t);
    }
    let weakest = live_champions(sim, team, false)
        .into_iter()
        .filter(|&e| ok(e))
        .min_by(|a, b| hp_ratio(sim, *a).total_cmp(&hp_ratio(sim, *b)));
    if weakest.is_some() {
        return weakest;
    }
    all_units(sim)
        .into_iter()
        .filter(|&u| ok(u))
        .min_by(|a, b| {
            let (pa, pb) = (pos_of(sim, *a).unwrap_or(at), pos_of(sim, *b).unwrap_or(at));
            dist(at, pa).total_cmp(&dist(at, pb))
        })
}

struct Arc;

impl StableEffectType for Arc {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) || held(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (sim.get_entity(caster).map(|e| e.pos()), team_of(sim, caster)) else { return };
        let Some(t) = arc_target(sim, caster, target_of(&input)) else {
            log(sim, format!("ARC #{caster}: nobody in reach"));
            return;
        };
        let spec = ProjectileSpawnV1 {
            caster_id: caster,
            team,
            x: at.0,
            y: at.1,
            radius: 8_000,
            speed: P.get("r_speed") as u64,
            move_kind: ProjectileMoveKindV1::Target.code(),
            target_id: t,
            target_x: 0,
            target_y: 0,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::Enemy.code(),
        };
        let ok = sim.spawn_projectile(R_ARROW, &format!("{ID}:arc_hit"), &spec);
        log(sim, format!("ARC #{caster} -> #{t}{}", if ok { "" } else { " (spawn_projectile refused)" }));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("r_dmg") + s.attack * P.get("r_ad") / 100, 0)
    }
}

struct ArcHit;

impl StableEffectType for ArcHit {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        let Some(t) = target_of(&input) else { return };
        let dmg = amount(sim, caster, P.get("r_dmg"), P.get("r_ad"), 0, 0);
        sim.deal_damage(caster, t, dmg, 0, AttackTypeV1::Skill);
        sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(t), 0, 0, 0);
        sim.play_sfx("crossbowman_ult_hit", caster, &InputTargetV1::target(t));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("r_dmg") + s.attack * P.get("r_ad") / 100, 0)
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("xiaolun: {ID} v{VERSION} (Xiao Lun: walking string, sidestep, latch, full arc) registered"));
    module.add_native_passive(format!("{ID}:string"), String_::default());
    module.add_native_effect(format!("{ID}:sidestep"), Sidestep);
    module.add_native_effect(format!("{ID}:latch"), Latch);
    module.add_native_effect(format!("{ID}:arc"), Arc);
    module.add_native_effect(format!("{ID}:arc_hit"), ArcHit);
    host.log(LogLevel::Info, "border.dll: Xiao Lun (walking string, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn the_string_winds_by_the_way_walked() {
        // 走 100000 上满：一拍 1000 是 1
        assert!((wind(1000.0, 100_000.0) - 1.0).abs() < 1e-9);
        // 一拍挪得再多也最多算 6000
        assert!((wind(15_000.0, 100_000.0) - 6.0).abs() < 1e-9);
        // 传送、复活不算
        assert_eq!(wind(25_000.0, 100_000.0), 0.0);
        assert_eq!(wind(0.0, 100_000.0), 0.0);
    }

    #[test]
    fn the_sidestep_keeps_away_from_the_others() {
        let at = (400_000.0, 400_000.0);
        let to = (460_000.0, 400_000.0);
        // 目标在右边，另一个敌人在上面（y 小）：往下（y 大）走
        let s = side(at, to, 18_000.0, &[(430_000.0, 360_000.0)]).unwrap();
        assert!(s.1 > 0.9, "{s:?}");
        // 敌人在下面：往上
        let s = side(at, to, 18_000.0, &[(430_000.0, 440_000.0)]).unwrap();
        assert!(s.1 < -0.9, "{s:?}");
        // 贴着地图上边：往下，哪怕敌人在下面
        let edge = (400_000.0, 20_000.0);
        let s = side(edge, (460_000.0, 20_000.0), 18_000.0, &[(430_000.0, 60_000.0)]).unwrap();
        assert!(s.1 > 0.9, "{s:?}");
        // 目标就在脚下：没有方向
        assert!(side(at, at, 18_000.0, &[]).is_none());
    }
}
