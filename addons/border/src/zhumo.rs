//! 铸沫（`border_zhumo`）数据做不到的部分。数据：tools/kit/build_zhumo.py（参数表 P；`passive` 是这里的
//! `border_zhumo:heat`）。
//!
//! - **余温**（被动）：普攻出手（`on_base_attack`）后同一拍打到了东西（`on_attack`）才算一下实际命中，攒 p_gain 点热量；
//!   p_idle 拍没打中东西就每秒掉 p_decay。热量最多 100，十层挂在他身上（`border_zhumo_heat`，每层攻速 +p_as%）；热量到一半、
//!   到满时锤头亮一下余烬。压坯、回火、开炉读这几层（读施法的人自己的，塞拉斯偷去开炉也照样算）。
//! - **压坯**（`border_zhumo:press`）：重击目标，伤害随热量涨，热量够了再眩晕，身边的人吃一部分。
//! - **回火**（`border_zhumo:temper`）：热量全部用掉，按层数换减伤，金属环贴着他。
//! - **开炉**（`border_zhumo:furnace`，开炉后每秒一次）：热量 +r_gain 层，脚下炉圈亮一下；危险（生命低于 r_low%，或者身边
//!   两个以上敌方英雄、生命低于 70%）时把回火的冷却减 r_cdr 拍，不危险、热量够、身边 r_reach 内有敌方英雄时把压坯的冷却
//!   减 r_cdr 拍：游戏的 AI 技能一好、目标在射程内就放，回火防守还是攒热重击就这样由它挑出来。
//!
//! 日志写在本包的 border.log 里（行首 `zhumo`）。

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_zhumo";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const HEAT: &str = "border_zhumo_heat";
const TEMPER: &str = "border_zhumo_temper";
const Q_SLOW: &str = "border_zhumo_q_slow";
const VIEW_HIT: &str = "border_zhumo_a_hit";
const VIEW_TEMPER: &str = "border_zhumo_e_temper";
const VIEW_FURNACE: &str = "border_zhumo_r_furnace";
const VIEW_HEAT: &str = "border_zhumo_p_heat";
pub const LEVELS: usize = 10;

pub static P: Params = Params::new(&[
    ("e_dr", 25), ("e_k", 4), ("e_t", 150), ("p_as", 3), ("p_decay", 10), ("p_gain", 12), ("p_idle", 180),
    ("q_ad", 140), ("q_dmg", 70), ("q_heat", 10), ("q_slow", 30), ("q_slow_t", 60), ("q_splash", 18000),
    ("q_splash_pct", 50), ("q_stun", 24), ("q_stun_heat", 5), ("r_cdr", 240), ("r_gain", 2), ("r_low", 40),
    ("r_reach", 30000), ("r_smash", 6),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("zhumo [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 规则（单元测试用） =====================

/// 回火：热量 k 层时受到的伤害降低多少。
pub fn temper_dr(k: usize, e_dr: usize, e_k: usize) -> usize {
    (e_dr + k.min(LEVELS) * e_k).min(80)
}

/// 压坯：热量 k 层时的攻击力加成（百分比）。
pub fn press_ratio(k: usize, q_ad: usize, q_heat: usize) -> usize {
    q_ad + k.min(LEVELS) * q_heat
}

/// 开炉这一秒怎么帮 AI：危险就回火，不然热量够、有人在身边就重击，都不是就不管。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Beat {
    Temper,
    Smash,
    Nothing,
}

pub fn beat(hp_pct: usize, enemies_close: usize, heat: usize, low: usize, smash: usize) -> Beat {
    let danger = hp_pct < low || (enemies_close >= 2 && hp_pct < 70);
    if danger {
        Beat::Temper
    } else if heat >= smash && enemies_close >= 1 {
        Beat::Smash
    } else {
        Beat::Nothing
    }
}

// ===================== 被动：余温 =====================

#[derive(Clone, Default)]
struct Heat {
    me: usize,
    heat: f64,
    shown: usize,
    /// 普攻出手的那一拍（等这一拍的 on_attack 认命中）
    swing: Option<usize>,
    last_hit: usize,
    chat: Chatter,
}

impl Heat {
    fn reset(&mut self) {
        self.heat = 0.0;
        self.shown = 0;
        self.swing = None;
    }
}

impl StablePassive for Heat {
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
        log(sim, format!("SPAWN #{me}: border.dll's Zhu Mo (player {player})"));
    }

    fn on_base_attack(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, _me: usize) {
        self.swing = Some(sim.tick());
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        let tick = sim.tick();
        if self.swing.is_some_and(|t| tick <= t + 1) {
            self.swing = None;
            self.heat = (self.heat + P.f("p_gain")).min(100.0);
            self.last_hit = tick;
        }
        self.chat.attacked(sim, ID, me, target);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.reset();
            return;
        }
        self.chat.tick(sim, ID, player, me);
        let tick = sim.tick();
        let have = count_buff(sim, me, HEAT);
        // 回火用掉了（少了）或者开炉加了（多了）：记的跟着层数走
        if have < self.shown {
            self.heat = (have * 10) as f64;
        } else if have > self.shown {
            self.heat = self.heat.max((have * 10) as f64);
        }
        self.shown = have;
        if tick > self.last_hit + P.get("p_idle") && !has_buff(sim, me, "border_zhumo_furnace") {
            self.heat = (self.heat - P.f("p_decay") / SECOND as f64).max(0.0);
        }
        let want = ((self.heat / 10.0 + 1e-9).floor() as usize).min(LEVELS);
        if want != self.shown {
            let as_ = P.get("p_as") as i32;
            set_stacks(sim, me, HEAT, want, || {
                let mut b = BuffV1::named(HEAT);
                b.attack_speed_mult = as_;
                b
            });
            if (self.shown < 5 && want >= 5) || (self.shown < LEVELS && want >= LEVELS) {
                sim.play_view_effect(VIEW_HEAT, me, &InputTargetV1::target(me), 0, 0, 0);
            }
            self.shown = want;
        }
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
        self.reset();
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
}

struct Press;

impl StableEffectType for Press {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(team) = team_of(sim, caster) else { return };
        let Some(t) = target_of(&input).filter(|&t| hittable_enemy(sim, team, t)) else { return };
        let k = count_buff(sim, caster, HEAT);
        let dmg = amount(sim, caster, P.get("q_dmg"), press_ratio(k, P.get("q_ad"), P.get("q_heat")), 0, 0);
        sim.deal_damage(caster, t, dmg, 0, AttackTypeV1::Skill);
        sim.add_buff(t, &slow_buff(Q_SLOW, P.get("q_slow"), P.get("q_slow_t")));
        let stunned = k >= P.get("q_stun_heat") && stun(sim, t, P.get("q_stun"));
        sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(t), 0, 0, 0);
        // 锤下去的熔流溅到旁边的人
        let mut splashed = 0;
        if let Some(at) = pos_of(sim, t) {
            let part = dmg * P.get("q_splash_pct") / 100;
            for id in all_units(sim) {
                if id == t || !hittable_enemy(sim, team, id) {
                    continue;
                }
                if pos_of(sim, id).is_some_and(|p| dist(at, p) <= P.f("q_splash")) {
                    sim.deal_damage(caster, id, part, 0, AttackTypeV1::Skill);
                    splashed += 1;
                }
            }
        }
        log(sim, format!("PRESS #{caster} -> #{t}: heat {k}, {dmg}{}, {splashed} splashed",
                         if stunned { ", stunned" } else { "" }));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("q_dmg") + s.attack * press_ratio(5, P.get("q_ad"), P.get("q_heat")) / 100, 0)
    }
}

struct Temper;

impl StableEffectType for Temper {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let k = count_buff(sim, caster, HEAT);
        let mut b = BuffV1::timed(TEMPER, P.get("e_t"));
        b.damaged_reduce = temper_dr(k, P.get("e_dr"), P.get("e_k"));
        sim.entity_remove_buff(caster, TEMPER);
        sim.add_buff(caster, &b);
        sim.entity_remove_buff(caster, HEAT);
        sim.play_view_effect(VIEW_TEMPER, caster, &InputTargetV1::target(caster), 0, 0, 0);
        log(sim, format!("TEMPER #{caster}: heat {k} -> -{}% damage", b.damaged_reduce));
    }

    fn expected_buff(&self, _s: &StatV1) -> Option<BuffV1> {
        let mut b = BuffV1::timed(TEMPER, P.get("e_t"));
        b.damaged_reduce = temper_dr(5, P.get("e_dr"), P.get("e_k"));
        Some(b)
    }
}

struct Furnace;

impl StableEffectType for Furnace {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        // 升温：加层（他的被动看到多了就跟上）
        let have = count_buff(sim, caster, HEAT);
        let want = (have + P.get("r_gain")).min(LEVELS);
        let as_ = P.get("p_as") as i32;
        set_stacks(sim, caster, HEAT, want, || {
            let mut b = BuffV1::named(HEAT);
            b.attack_speed_mult = as_;
            b
        });
        sim.play_view_effect(VIEW_FURNACE, caster, &InputTargetV1::target(caster), 0, 0, 0);
        let close = live_champions(sim, team, false)
            .into_iter()
            .filter(|&e| pos_of(sim, e).is_some_and(|p| dist(at, p) <= P.f("r_reach")))
            .count();
        let hp = (hp_ratio(sim, caster) * 100.0) as usize;
        let what = beat(hp, close, want, P.get("r_low"), P.get("r_smash"));
        let slot = match what {
            Beat::Temper => Some(SkillSlotV1::Skill2),
            Beat::Smash => Some(SkillSlotV1::Skill),
            Beat::Nothing => None,
        };
        let mut cut = false;
        if let Some(s) = slot {
            let cooling = sim.get_entity(caster).and_then(|e| e.cooldown(s)).is_some_and(|c| c.remaining > 0);
            if cooling {
                cut = sim.entity_reduce_cooldown(caster, s, P.get("r_cdr"));
            }
        }
        log(sim, format!("FURNACE #{caster}: heat {have} -> {want}, hp {hp}%, {close} close: {what:?}{}",
                         if cut { " (cooldown cut)" } else { "" }));
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("zhumo: {ID} v{VERSION} (Zhu Mo: afterheat, press, temper, furnace) registered"));
    module.add_native_passive(format!("{ID}:heat"), Heat::default());
    module.add_native_effect(format!("{ID}:press"), Press);
    module.add_native_effect(format!("{ID}:temper"), Temper);
    module.add_native_effect(format!("{ID}:furnace"), Furnace);
    host.log(LogLevel::Info, "border.dll: Zhu Mo (afterheat, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn heat_buys_damage_and_guard() {
        assert_eq!(press_ratio(0, 100, 8), 100);
        assert_eq!(press_ratio(10, 100, 8), 180);
        assert_eq!(press_ratio(15, 100, 8), 180);
        assert_eq!(temper_dr(0, 10, 3), 10);
        assert_eq!(temper_dr(10, 10, 3), 40);
    }

    #[test]
    fn the_furnace_guards_when_in_danger_and_smashes_when_hot() {
        assert_eq!(beat(30, 1, 10, 40, 6), Beat::Temper);
        assert_eq!(beat(60, 2, 10, 40, 6), Beat::Temper);
        assert_eq!(beat(90, 2, 10, 40, 6), Beat::Smash);
        assert_eq!(beat(90, 1, 6, 40, 6), Beat::Smash);
        assert_eq!(beat(90, 1, 5, 40, 6), Beat::Nothing);
        assert_eq!(beat(90, 0, 10, 40, 6), Beat::Nothing);
    }
}
