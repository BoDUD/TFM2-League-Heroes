//! 澜缇（`border_lanti`）数据做不到的部分。数据：tools/kit/build_lanti.py（参数表 P；`passive` 是这里的
//! `border_lanti:fracture`）。
//!
//! - **折纹**（被动）：她挨了一下（`on_damaged`），打她的是敌方英雄、他那一刻正在放技能（施法动作还在播，或技能刚进冷却
//!   p_window 拍内）就算技能伤害：只给他一个人挂镜纹（`border_lanti_mark`，p_t 拍，换人就摘掉旧的）。
//! - **候击**（`border_lanti:guard`）：起架（`border_lanti_guard`，受到的技能伤害降低 e_dr%）。架着时挨了一下技能就算成功：
//!   架子收起，双棱的冷却刷新，挡下的那部分（这一下 x e_dr / (100 - e_dr)）记下来。
//! - **还响**：最近 r_window 拍挡下的伤害，每 10 点一层挂在她身上（`border_lanti_echo`，最多 r_cap / 10 层，被动管）；
//!   `echo` 推出一道玻璃波（原生直线弹道 `border_lanti_r_wave`，朝左时 `_l`），加成写在她身上（`border_lanti_r_bonus_<n>`），
//!   打中的人（`echo_hit`）每人一下。层数用掉。塞拉斯偷去的是数据版（没有加成），不走这里。
//! - **双棱**（`prism1` / `prism2`）：两拳，每拳打中在他身上亮一下拳光；第二拳打到带镜纹的人，镜纹用掉、加伤、减速。
//!
//! 日志写在本包的 border.log 里（行首 `lanti`）。

use std::collections::VecDeque;

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_lanti";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const MARK: &str = "border_lanti_mark";
pub const GUARD: &str = "border_lanti_guard";
pub const ECHO: &str = "border_lanti_echo";
const BONUS: &str = "border_lanti_r_bonus_";
const Q_SLOW: &str = "border_lanti_q_slow";
const R_SLOW: &str = "border_lanti_r_slow";
const WAVE: &str = "border_lanti_r_wave";
const VIEW_MARK: &str = "border_lanti_p_mark";
const VIEW_PUNCH: &str = "border_lanti_q_punch";
const VIEW_GUARD: &str = "border_lanti_e_guard";
const VIEW_HIT: &str = "border_lanti_a_hit";

pub static P: Params = Params::new(&[
    ("e_dr", 50), ("e_t", 150), ("p_t", 300), ("p_window", 30), ("q1_ad", 80), ("q1_dmg", 50), ("q2_ad", 130),
    ("q2_dmg", 80), ("q_mark", 60), ("q_slow", 20), ("q_slow_t", 45), ("r_ad", 160), ("r_cap", 300),
    ("r_dmg", 260), ("r_k", 60), ("r_len", 45000), ("r_slow", 30), ("r_slow_t", 60), ("r_speed", 6000),
    ("r_w", 16000), ("r_window", 480),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("lanti [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 规则（单元测试用） =====================

/// 减伤 dr% 时挨了 `taken`：挡下了多少。
pub fn blocked(taken: usize, dr: usize) -> usize {
    let dr = dr.min(90);
    taken * dr / (100 - dr)
}

/// 还响的加成：挡下 `stored`，r_k%，最多 cap。
pub fn echo_bonus(stored: usize, k: usize, cap: usize) -> usize {
    (stored * k / 100).min(cap)
}

// ===================== 被动：折纹 =====================

#[derive(Clone, Default)]
struct Fracture {
    me: usize,
    marked: Option<usize>,
    /// 最近挡下的伤害（哪一拍、多少）
    blocks: VecDeque<(usize, usize)>,
    shown: usize,
    chat: Chatter,
}

impl Fracture {
    fn sync(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        while self.blocks.front().is_some_and(|&(t, _)| t + P.get("r_window") < tick) {
            self.blocks.pop_front();
        }
        let have = count_buff(sim, me, ECHO);
        // 还响用掉了
        if have < self.shown {
            self.blocks.clear();
            self.shown = have;
        }
        let stored: usize = self.blocks.iter().map(|b| b.1).sum();
        let want = (stored / 10).min(P.get("r_cap") / 10);
        if want != have {
            set_stacks(sim, me, ECHO, want, || BuffV1::named(ECHO));
        }
        self.shown = want;
    }
}

impl StablePassive for Fracture {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        P.configure(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.chat.spawned();
        self.blocks.clear();
        self.shown = 0;
        log(sim, format!("SPAWN #{me}: border.dll's Lan Ti (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.blocks.clear();
            self.shown = 0;
            return;
        }
        self.chat.tick(sim, ID, player, me);
        self.sync(sim, me);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        self.chat.damaged(sim, ID, me, damage);
        self.chat.flinch(sim, ID, me, damage);
        let mine = team_of(sim, me);
        let foe = sim.get_entity(attacker).is_some_and(|a| a.is_champion() && Some(a.team()) != mine);
        if !foe || !(casting(sim, attacker) || just_cast(sim, attacker, P.get("p_window"))) {
            return;
        }
        // 折纹：只标最近一个
        if let Some(old) = self.marked.filter(|&o| o != attacker) {
            sim.entity_remove_buff(old, MARK);
        }
        self.marked = Some(attacker);
        sim.entity_stack_buff(attacker, &BuffV1::timed(MARK, P.get("p_t")), 1, true);
        sim.play_view_effect(VIEW_MARK, me, &InputTargetV1::target(attacker), 0, 0, 0);
        // 候击：架着挨了一下技能就是成功
        if has_buff(sim, me, GUARD) {
            let b = blocked(damage, P.get("e_dr"));
            self.blocks.push_back((sim.tick(), b));
            sim.entity_remove_buff(me, GUARD);
            sim.entity_reduce_cooldown(me, SkillSlotV1::Skill, 100_000);
            log(sim, format!("GUARD #{me} caught #{attacker}'s spell: took {damage}, blocked {b}, Double Prism ready"));
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.chat.attacked(sim, ID, me, target);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.chat.killed(sim, ID, me, victim);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        let me = self.me;
        self.blocks.clear();
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

fn punch(sim: &mut StableSim<'_>, caster: usize, input: &InputTargetV1, second: bool) {
    if !alive(sim, caster) {
        return;
    }
    let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
    let Some(t) = target_of(input).filter(|&t| {
        hittable_enemy(sim, team, t) && pos_of(sim, t).is_some_and(|p| dist(at, p) <= 34_000.0)
    }) else {
        return;
    };
    let (flat, ratio) = if second { (P.get("q2_dmg"), P.get("q2_ad")) } else { (P.get("q1_dmg"), P.get("q1_ad")) };
    let mut dmg = amount(sim, caster, flat, ratio, 0, 0);
    let mut cracked = false;
    if second && has_buff(sim, t, MARK) {
        dmg += dmg * P.get("q_mark") / 100;
        sim.entity_remove_buff(t, MARK);
        sim.add_buff(t, &slow_buff(Q_SLOW, P.get("q_slow"), P.get("q_slow_t")));
        cracked = true;
    }
    sim.deal_damage(caster, t, dmg, 0, AttackTypeV1::Skill);
    // 拳光朝右画的：她在目标右边（往左打）就放左右翻过的那张
    let leftward = pos_of(sim, t).is_some_and(|p| p.0 < at.0);
    let view = if leftward { format!("{VIEW_PUNCH}_l") } else { VIEW_PUNCH.to_string() };
    sim.play_view_effect(&view, caster, &InputTargetV1::target(t), 0, 0, 0);
    if second {
        log(sim, format!("PRISM #{caster} -> #{t} {dmg}{}", if cracked { " (the mirror mark broke)" } else { "" }));
    }
}

struct Prism1;

impl StableEffectType for Prism1 {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        punch(sim, caster, &input, false);
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("q1_dmg") + s.attack * P.get("q1_ad") / 100, 0)
    }
}

struct Prism2;

impl StableEffectType for Prism2 {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        punch(sim, caster, &input, true);
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("q2_dmg") + s.attack * P.get("q2_ad") / 100, 0)
    }
}

struct Guard;

impl StableEffectType for Guard {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let mut g = BuffV1::timed(GUARD, P.get("e_t"));
        g.skill_damaged_reduce = P.get("e_dr");
        sim.entity_remove_buff(caster, GUARD);
        sim.add_buff(caster, &g);
        sim.play_view_effect(VIEW_GUARD, caster, &InputTargetV1::target(caster), 0, 0, 0);
    }

    fn expected_buff(&self, _s: &StatV1) -> Option<BuffV1> {
        let mut g = BuffV1::timed(GUARD, P.get("e_t"));
        g.skill_damaged_reduce = P.get("e_dr");
        Some(g)
    }
}

struct Echo;

impl StableEffectType for Echo {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let Some(to) = target_of(&input).and_then(|t| pos_of(sim, t)) else { return };
        let u = unit((to.0 - at.0, to.1 - at.1)).unwrap_or((1.0, 0.0));
        let stored = count_buff(sim, caster, ECHO) * 10;
        let bonus = echo_bonus(stored, P.get("r_k"), P.get("r_cap"));
        clear_named(sim, caster, BONUS, 1);
        sim.add_buff(caster, &BuffV1::timed(&format!("{BONUS}{bonus}"), 90));
        sim.entity_remove_buff(caster, ECHO);
        let len = P.f("r_len");
        let end = (at.0 + u.0 * len, at.1 + u.1 * len);
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
            penetrate: true,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        let name = if u.0 < -1e-6 { format!("{WAVE}_l") } else { WAVE.to_string() };
        let ok = sim.spawn_projectile(&name, &format!("{ID}:echo_hit"), &spec);
        log(sim, format!("ECHO #{caster}: blocked {stored} -> +{bonus}{}", if ok { "" } else { " (spawn refused)" }));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("r_dmg") + s.attack * P.get("r_ad") / 100, 0)
    }
}

struct EchoHit;

impl StableEffectType for EchoHit {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        let Some(t) = target_of(&input) else { return };
        let bonus = named(sim, caster, BONUS, 1).last().map_or(0, |(_, v)| v[0] as usize);
        let dmg = amount(sim, caster, P.get("r_dmg"), P.get("r_ad"), 0, 0) + bonus;
        sim.deal_damage(caster, t, dmg, 0, AttackTypeV1::Skill);
        sim.add_buff(t, &slow_buff(R_SLOW, P.get("r_slow"), P.get("r_slow_t")));
        sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(t), 0, 0, 0);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("lanti: {ID} v{VERSION} (Lan Ti: fracture mark, double prism, await the strike, echo) registered"));
    module.add_native_passive(format!("{ID}:fracture"), Fracture::default());
    module.add_native_effect(format!("{ID}:prism1"), Prism1);
    module.add_native_effect(format!("{ID}:prism2"), Prism2);
    module.add_native_effect(format!("{ID}:guard"), Guard);
    module.add_native_effect(format!("{ID}:echo"), Echo);
    module.add_native_effect(format!("{ID}:echo_hit"), EchoHit);
    host.log(LogLevel::Info, "border.dll: Lan Ti (fracture mark, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn the_guard_counts_what_it_kept_off() {
        // 50% 减伤：挨了 100，原来是 200，挡下 100
        assert_eq!(blocked(100, 50), 100);
        assert_eq!(blocked(100, 0), 0);
        assert_eq!(echo_bonus(200, 60, 300), 120);
        assert_eq!(echo_bonus(900, 60, 300), 300);
    }
}
