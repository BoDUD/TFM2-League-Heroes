//! 钟砾（`border_zhongli`）数据做不到的部分。数据：tools/kit/build_zhongli.py（参数表 P；`passive` 是这里的
//! `border_zhongli:plant`）。压簧在数据里（`border_zhongli_spring`，打中那一拍站稳着就穿甲）。
//!
//! - **定脚**（被动）：一拍挪不到 300 算站着；连着站 p_still 拍就站稳（脚下支架落地），之后每 p_step 拍多一档，最多 p_levels
//!   档（`border_zhongli_plant` 的层数，每层攻速 +p_as%）；站稳后累计挪开 p_move 就全部解除。落架的支架在（`border_zhongli_stand`）
//!   时直接满档，挪开 p_move 时支架一起收起。
//! - **落架**（`stand`）：护盾，支架立起（e_stand 拍），定脚满档。
//! - **齐鸣**（`aim` 第 1 拍、`volley` / `volley_last` 四次）：出手那一刻把方向和他站的位置写在身上
//!   （`border_zhongli_aim_<x>_<y>_<dx>_<dy>`）；每一发都朝这个方向放一个单独的直线弹丸（`border_zhongli_r_bolt`，打到第一个
//!   敌人停，`volley_hit` / 最后一发 `volley_hit_last`）。他被控住、或者离开那个位置 r_move 以上，方向摘掉，后面的不放了。
//!
//! 日志写在本包的 border.log 里（行首 `zhongli`）。

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_zhongli";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const PLANT: &str = "border_zhongli_plant";
pub const STAND: &str = "border_zhongli_stand";
const AIM: &str = "border_zhongli_aim_";
const BOLT: &str = "border_zhongli_r_bolt";
const VIEW_HIT: &str = "border_zhongli_a_hit";
const VIEW_FEET: &str = "border_zhongli_p_feet";
const VIEW_SHIELD: &str = "border_zhongli_e_shield";
/// 一拍挪得比这少算站着
const STILL_STEP: f64 = 300.0;

pub static P: Params = Params::new(&[
    ("e_hp", 8), ("e_sh", 90), ("e_stand", 240), ("e_t", 150), ("p_as", 12), ("p_levels", 4), ("p_move", 3000),
    ("p_step", 30), ("p_still", 45), ("r_ad", 85), ("r_dmg", 110), ("r_dur", 52), ("r_last", 200), ("r_len", 90000),
    ("r_move", 4000), ("r_speed", 9000), ("r_w", 9000),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("zhongli [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 规则（单元测试用） =====================

/// 定脚的一拍：(站了几拍, 站稳后挪了多远, 档位) 加上这一拍挪的 `step`、支架在不在，得出新的。
pub fn plant_step(state: (usize, f64, usize), step: f64, stand: bool, still: usize, every: usize, levels: usize,
                  move_out: f64) -> (usize, f64, usize) {
    let (mut quiet, mut moved, mut level) = state;
    if step < STILL_STEP {
        quiet += 1;
    } else {
        quiet = 0;
    }
    if level > 0 {
        moved += step;
        if moved >= move_out {
            return (0, 0.0, 0);
        }
    }
    if stand {
        return (quiet.max(still), moved, levels);
    }
    if level == 0 && quiet >= still {
        level = 1;
        moved = 0.0;
    } else if level > 0 && quiet >= still && (quiet - still).is_multiple_of(every.max(1)) && quiet > still {
        level = (level + 1).min(levels);
    }
    (quiet, moved, level)
}

// ===================== 被动：定脚 =====================

#[derive(Clone, Default)]
struct Plant {
    me: usize,
    last: Option<Pt>,
    quiet: usize,
    moved: f64,
    level: usize,
    chat: Chatter,
}

impl Plant {
    fn step(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let at = pos_of(sim, me);
        let step = match (self.last, at) {
            (Some(a), Some(b)) => dist(a, b),
            _ => 0.0,
        };
        self.last = at;
        let stand = has_buff(sim, me, STAND);
        let before = self.level;
        let (q, m, l) = plant_step((self.quiet, self.moved, self.level), step, stand, P.get("p_still"), P.get("p_step"),
                                   P.get("p_levels"), P.f("p_move"));
        self.quiet = q;
        self.moved = m;
        self.level = l;
        if l == 0 && before > 0 && stand {
            // 走开了：支架收起
            sim.entity_remove_buff(me, STAND);
        }
        if l != count_buff(sim, me, PLANT) {
            let as_ = P.get("p_as") as i32;
            set_stacks(sim, me, PLANT, l, || {
                let mut b = BuffV1::named(PLANT);
                b.attack_speed_mult = as_;
                b
            });
        }
        if before == 0 && l > 0 {
            sim.play_view_effect(VIEW_FEET, me, &InputTargetV1::target(me), 0, 0, 0);
        }
    }
}

impl StablePassive for Plant {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        P.configure(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.chat.spawned();
        self.last = None;
        self.quiet = 0;
        self.level = 0;
        log(sim, format!("SPAWN #{me}: border.dll's Zhong Li (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.last = None;
            self.level = 0;
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
        self.level = 0;
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

struct Stand;

impl StableEffectType for Stand {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let max = sim.get_entity(caster).map_or(0, |e| e.hp().1);
        let amt = P.get("e_sh") + max * P.get("e_hp") / 100;
        sim.entity_add_shield(caster, amt, P.get("e_t"));
        sim.entity_remove_buff(caster, STAND);
        sim.add_buff(caster, &BuffV1::timed(STAND, P.get("e_stand")));
        let as_ = P.get("p_as") as i32;
        set_stacks(sim, caster, PLANT, P.get("p_levels"), || {
            let mut b = BuffV1::named(PLANT);
            b.attack_speed_mult = as_;
            b
        });
        sim.play_view_effect(VIEW_SHIELD, caster, &InputTargetV1::target(caster), 0, 0, 0);
        log(sim, format!("STAND #{caster}: shield {amt}"));
    }

    fn expected_shield(&self, s: &StatV1) -> usize {
        P.get("e_sh") + s.hp * P.get("e_hp") / 100
    }
}

struct Aim;

impl StableEffectType for Aim {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = pos_of(sim, caster) else { return };
        let Some(to) = target_of(&input).and_then(|t| pos_of(sim, t)) else { return };
        let u = unit((to.0 - at.0, to.1 - at.1)).unwrap_or((1.0, 0.0));
        clear_named(sim, caster, AIM, 4);
        sim.add_buff(caster, &BuffV1::timed(&Seg { c: at, d: u }.name(AIM), P.get("r_dur") + 10));
    }
}

fn volley(sim: &mut StableSim<'_>, caster: usize, last: bool) {
    let Some(aim) = named(sim, caster, AIM, 4).last().and_then(|(n, _)| Seg::parse(AIM, n)) else { return };
    let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
    if !alive(sim, caster) || held(sim, caster) || dist(at, aim.c) > P.f("r_move") {
        clear_named(sim, caster, AIM, 4);
        log(sim, format!("VOLLEY #{caster} broken off (moved or held)"));
        return;
    }
    let len = P.f("r_len");
    let end = (at.0 + aim.d.0 * len, at.1 + aim.d.1 * len);
    let spec = ProjectileSpawnV1 {
        caster_id: caster,
        team,
        x: at.0 as u64,
        y: at.1 as u64,
        radius: (P.get("r_w") / 2) as u64,
        speed: P.get("r_speed") as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: end.0.max(0.0) as u64,
        target_y: end.1.max(0.0) as u64,
        penetrate: false,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::EnemyWithoutTower.code(),
    };
    let hit = if last { "volley_hit_last" } else { "volley_hit" };
    sim.spawn_projectile(BOLT, &format!("{ID}:{hit}"), &spec);
    sim.play_sfx("gunner_ult", caster, &InputTargetV1::target(caster));
    if last {
        clear_named(sim, caster, AIM, 4);
    }
}

struct Volley;

impl StableEffectType for Volley {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        volley(sim, caster, false);
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("r_dmg") + s.attack * P.get("r_ad") / 100, 0)
    }
}

struct VolleyLast;

impl StableEffectType for VolleyLast {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        volley(sim, caster, true);
    }
}

fn volley_hit(sim: &mut StableSim<'_>, caster: usize, input: &InputTargetV1, last: bool) {
    let Some(t) = target_of(input) else { return };
    let mut dmg = amount(sim, caster, P.get("r_dmg"), P.get("r_ad"), 0, 0);
    if last {
        dmg = dmg * P.get("r_last") / 100;
    }
    sim.deal_damage(caster, t, dmg, 0, AttackTypeV1::Skill);
    sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(t), 0, 0, 0);
}

struct VolleyHit;

impl StableEffectType for VolleyHit {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        volley_hit(sim, caster, &input, false);
    }
}

struct VolleyHitLast;

impl StableEffectType for VolleyHitLast {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        volley_hit(sim, caster, &input, true);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("zhongli: {ID} v{VERSION} (Zhong Li: planted feet, stand, chorus) registered"));
    module.add_native_passive(format!("{ID}:plant"), Plant::default());
    module.add_native_effect(format!("{ID}:stand"), Stand);
    module.add_native_effect(format!("{ID}:aim"), Aim);
    module.add_native_effect(format!("{ID}:volley"), Volley);
    module.add_native_effect(format!("{ID}:volley_last"), VolleyLast);
    module.add_native_effect(format!("{ID}:volley_hit"), VolleyHit);
    module.add_native_effect(format!("{ID}:volley_hit_last"), VolleyHitLast);
    host.log(LogLevel::Info, "border.dll: Zhong Li (planted feet, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn standing_still_plants_him_and_walking_off_ends_it() {
        let mut s = (0, 0.0, 0);
        // 站 45 拍站稳
        for _ in 0..44 {
            s = plant_step(s, 0.0, false, 45, 30, 4, 3000.0);
        }
        assert_eq!(s.2, 0);
        s = plant_step(s, 0.0, false, 45, 30, 4, 3000.0);
        assert_eq!(s.2, 1);
        // 再站 30 拍一档
        for _ in 0..30 {
            s = plant_step(s, 0.0, false, 45, 30, 4, 3000.0);
        }
        assert_eq!(s.2, 2);
        // 小步挪（每拍 200）累计 3000 解除
        for _ in 0..14 {
            s = plant_step(s, 200.0, false, 45, 30, 4, 3000.0);
        }
        assert_eq!(s.2, 2);
        s = plant_step(s, 200.0, false, 45, 30, 4, 3000.0);
        assert_eq!(s.2, 0);
        // 支架：直接满档
        let t = plant_step((0, 0.0, 0), 0.0, true, 45, 30, 4, 3000.0);
        assert_eq!(t.2, 4);
    }
}
