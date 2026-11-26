//! 驱灵奇术按敌人分别叠层、飞去来咒的回程（英雄联盟 V26.22；用户 2026-11-26「检查一下阿罗拉和薇古丝完美还原英雄联盟了没有」）。
//!
//! 主包是纯数据：`SwitchByBuff` 只看施法者身上的 buff，所以主包的驱灵奇术记在她身上（打谁都往上加），第三层的伤害也只能写
//! 「40 + 30% 法强 + 2% 最大生命」。附加包的副本把每处叠层换成本模块的原生效果 `league_aurora:mark_<来源>`（[`Mark`]）：
//!
//! - **每个敌方英雄分别叠**：层数是他身上的 buff `league_aurora_p1` / `league_aurora_p2`（`p_t` tick，再叠刷新）。同一个来源
//!   （普攻、Q 去、Q 回、E、R）一次施放对同一个人只算一层（他身上 2 tick 的 `league_aurora_lk_<来源>`）。
//! - **第三层**：清掉层数，魔法伤害 = 最大生命 × (`p_hp_pm` + `p_hp_ap_pm` × 法强 / 100) / 1000（英雄联盟 1% + 每 100 法强
//!   2.7%），抽出一个灵物：给她挂 1 tick 的 `league_aurora_spirit_new`，被动（`lib.rs`）读到就让灵物跟着她 `sp_t` tick，每个
//!   灵物每秒回 `sp0`–`sp1`（按等级）+ `sp_ap`% 法强，最多 `sp_max` 个，再抽出一个就刷新全部。
//!
//! 飞去来咒的回程（数据的 `ApAttack` 换成 [`HexBack`]，`league_aurora:hex_back`）：
//!
//! - 对英雄按他已损失的生命加伤，满血 +0%、快死 +`q2_miss`%（50%）；对小兵打 `q2_minion`%、野怪 `q2_monster`%；
//! - 同一个敌人 `q2_again_t` tick 内第二颗以后只打 `q2_again`%（怪奇喷涌的 E → Q 那颗和自己按的 Q 回程叠在一起时）。
//!
//! 数字是英雄数据 `passive.params` 里的（参数表 P，`make_override.py` 写进去）；原生效果不带参数，读不到被动的 `Params`，
//! 所以本模块自己按 [`Params`] 的默认值算，`make_override.py` 和单元测试核对两边一样。

use mod_api_stable::*;

use super::{counted, head, on_screen, wlog, Params};

/// 他身上一层、两层。
pub const P1: &str = "league_aurora_p1";
pub const P2: &str = "league_aurora_p2";
/// 他头顶驱灵的光圈（主包的画面，层数在就挂着）。
pub const MARK_VIEW: &str = "league_aurora_p_mark";
/// 第三层抽出灵物（主包的画面和声音）。
pub const SPIRIT_VIEW: &str = "league_aurora_p_spirit";
/// 灵物回到她身上回血的画面。
pub const HEAL_VIEW: &str = "league_aurora_p_heal";
/// 给被动的：这一 tick 抽出了一个灵物。
pub const NEW_SPIRIT: &str = "league_aurora_spirit_new";
/// 回程打过他（`q2_again_t` tick）。
pub const HEXED: &str = "league_aurora_hexed";
/// 叠层的来源（副本数据里的原生效果名 `league_aurora:mark_<来源>`）。
pub const SOURCES: [&str; 5] = ["a", "q", "q2", "e", "r"];

/// 这个 buff 名是几层（不是层数的 0）。
pub fn stacks_in(name: &str) -> usize {
    match name {
        P1 => 1,
        P2 => 2,
        _ => 0,
    }
}

/// 第三层的魔法伤害（打折之前）。
pub fn proc_damage(p: &Params, max_hp: usize, ap: usize) -> usize {
    max_hp * (p.p_hp_pm + p.p_hp_ap_pm * ap / 100) / 1000
}

/// 一个灵物每秒回多少（1–12 级从 sp0 到 sp1，加 sp_ap% 法强）。
pub fn spirit_heal(p: &Params, level: usize, ap: usize) -> usize {
    let l = level.clamp(1, 12) - 1;
    p.sp0 + (p.sp1.saturating_sub(p.sp0)) * l / 11 + p.sp_ap * ap / 100
}

/// 回程打这个单位多少（打折之前）：`kind` 他是什么，`hp` / `max` 他的生命，`again` 刚被回程打过。
pub fn hex_back_damage(p: &Params, ap: usize, kind: Option<EntityKindV1>, hp: usize, max: usize, again: bool) -> usize {
    let base = p.q2_dmg + p.q2_ratio * ap / 100;
    let mut d = match kind {
        Some(EntityKindV1::Minion) => base * p.q2_minion / 100,
        Some(EntityKindV1::Jungle) | Some(EntityKindV1::Epic) | Some(EntityKindV1::Serpen) => base * p.q2_monster / 100,
        Some(EntityKindV1::Champion) | None => {
            let lost = max.saturating_sub(hp) * 100 / max.max(1);
            base * (100 + p.q2_miss * lost / 100) / 100
        }
        _ => base,
    };
    if again {
        d = d * p.q2_again / 100;
    }
    d
}

/// 叠一层之后：(新的层数, 这一下到了第三层)。`now`：他身上的层数。
pub fn next_stack(now: usize) -> (usize, bool) {
    if now >= 2 {
        (0, true)
    } else {
        (now + 1, false)
    }
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn target_of(input: InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

/// `league_aurora:mark_<来源>`：打中一个敌方英雄，在他身上叠一层。
pub struct Mark {
    pub src: &'static str,
}

impl Mark {
    fn lock(&self) -> String {
        format!("league_aurora_lk_{}", self.src)
    }
}

impl StableEffectType for Mark {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let p = Params::default();
        let Some(t) = target_of(input) else { return };
        let Some(u) = sim.get_entity(t) else { return };
        if !u.is_alive() || !u.is_champion() {
            return;
        }
        let (stacks, max) = ((0..u.buff_count()).filter_map(|i| u.buff_at(i)).map(|b| stacks_in(b.name())).max().unwrap_or(0), u.hp().1);
        let lock = self.lock();
        if has(sim, t, &lock) {
            return;
        }
        sim.add_buff(t, &BuffV1::timed(&lock, 2));
        sim.entity_remove_buff(t, P1);
        sim.entity_remove_buff(t, P2);
        sim.entity_remove_buff(t, MARK_VIEW);
        let (n, third) = next_stack(stacks);
        if !third {
            sim.add_buff(t, &BuffV1::timed(if n == 1 { P1 } else { P2 }, p.p_t));
            sim.add_buff(t, &BuffV1::timed(MARK_VIEW, p.p_t));
            return;
        }
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let dmg = proc_damage(&p, max, ap);
        sim.deal_damage(me, t, 0, dmg, AttackTypeV1::Skill);
        sim.play_view_effect(SPIRIT_VIEW, me, &InputTargetV1::target(t), 0, 0, 0);
        sim.play_sfx(SPIRIT_VIEW, me, &InputTargetV1::target(t));
        sim.entity_remove_buff(me, NEW_SPIRIT);
        sim.add_buff(me, &BuffV1::timed(NEW_SPIRIT, 2));
        if let Some(n) = counted("spirit", on_screen(sim)) {
            wlog(format!("{} SPIRIT third stack on #{t} ({}): {dmg} magic (max hp {max}, ap {ap}), a spirit drawn #{n}",
                         head(sim, me), self.src));
        }
    }
}

/// `league_aurora:hex_back`：飞去来咒回程（和 E → Q 那颗收回时）的伤害。
pub struct HexBack;

impl StableEffectType for HexBack {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let p = Params::default();
        let Some(t) = target_of(input) else { return };
        let Some(u) = sim.get_entity(t) else { return };
        if !u.is_alive() {
            return;
        }
        let (kind, (hp, max)) = (u.kind(), u.hp());
        let again = has(sim, t, HEXED);
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let dmg = hex_back_damage(&p, ap, kind, hp, max, again);
        sim.deal_damage(me, t, 0, dmg, AttackTypeV1::Skill);
        sim.entity_remove_buff(t, HEXED);
        sim.add_buff(t, &BuffV1::timed(HEXED, p.q2_again_t));
    }

    fn expected_damage(&self, caster: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (0, p.q2_dmg + p.q2_ratio * caster.magic_power / 100)
    }
}

#[cfg(test)]
mod tests {
    use super::super::ID;
    use super::*;

    #[test]
    fn three_stacks_on_one_enemy() {
        assert_eq!(next_stack(0), (1, false));
        assert_eq!(next_stack(1), (2, false));
        assert_eq!(next_stack(2), (0, true));
        assert_eq!(stacks_in(P1) + stacks_in(P2) + stacks_in("league_aurora_s_1"), 3);
        for name in [P1, P2, MARK_VIEW, SPIRIT_VIEW, HEAL_VIEW, NEW_SPIRIT, HEXED] {
            assert!(name.starts_with(ID) && name.len() <= BUFF_NAME_CAP, "{name}");
        }
    }

    #[test]
    fn the_third_stack_is_leagues() {
        let p = Params::default();
        // 0 法强：2000 的 1%；每 100 法强再加 2.7%
        assert_eq!(proc_damage(&p, 2000, 0), 20);
        assert_eq!(proc_damage(&p, 2000, 200), 2000 * (10 + 54) / 1000);
        // 一个灵物每秒回：1 级 3、12 级 20，再加 2% 法强
        assert_eq!(spirit_heal(&p, 1, 0), p.sp0);
        assert_eq!(spirit_heal(&p, 12, 0), p.sp1);
        assert_eq!(spirit_heal(&p, 12, 300), p.sp1 + 6);
    }

    #[test]
    fn the_return_grows_with_missing_health() {
        let p = Params::default();
        let full = hex_back_damage(&p, 200, Some(EntityKindV1::Champion), 1000, 1000, false);
        let half = hex_back_damage(&p, 200, Some(EntityKindV1::Champion), 500, 1000, false);
        let dying = hex_back_damage(&p, 200, Some(EntityKindV1::Champion), 0, 1000, false);
        assert_eq!(full, p.q2_dmg + p.q2_ratio * 2);
        assert_eq!(half, full * 125 / 100);
        assert_eq!(dying, full * 150 / 100);
        assert_eq!(hex_back_damage(&p, 200, Some(EntityKindV1::Minion), 1, 1000, false), full * 40 / 100);
        assert_eq!(hex_back_damage(&p, 200, Some(EntityKindV1::Jungle), 1, 1000, false), full * 50 / 100);
        assert_eq!(hex_back_damage(&p, 200, Some(EntityKindV1::Champion), 1000, 1000, true), full * 20 / 100);
    }
}
