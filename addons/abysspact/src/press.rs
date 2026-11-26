//! 替 AI 按渊契几位英雄的「待命」格子（league_ult_press 的做法，AI 钩子 `abysspact:press`）。
//!
//! 这些格子在技能数据里是 3 tick 的 idle 动作：按下去只挂一个待命标记，真正放不放、什么时候放、对谁放都由各英雄的
//! 原生代码决定，待命到点没用上就退冷却。可游戏的 AI 几乎不按这种格子（league_ult_press 实测：凯尔 R 每 10 分钟
//! 0.9 次、伊芙琳 1.5、迦娜 0，多数大招 3.5–6 次；格子里加护盾、搜敌都没用），所以这里在合适的时候替它按：
//!
//! - 格子好了：解锁了、冷却是 0（没解锁的技能二、大招被钩子按下去，游戏的 AI 会崩、过日卡死，champion-data.md）；
//! - 英雄活着、能出招（`can_cast`：没被控、没在放别的动作、没被放逐），不在回城（`still_recalling` 那道闩）；
//! - AI 这一 tick 没有自己要放的技能（只在它走路、普攻或什么都不下时按，不盖掉游戏的 AI 或别的钩子要放的技能；
//!   排在后面的钩子要盖掉这一按也行，下一 tick 再按——不靠加载顺序）；
//! - 附近（[`ARMS`] 里各格子的距离，不超过那一格的施法距离）有看得见、选得中的敌方英雄，再加上：
//!   * 烛灵 R：10 秒内有队友倒在她 6 万内，或者她 5 万内有生命低于 35% 的队友（含她自己）而 5 万内有敌方英雄；
//!   * 返照 Q：7 万内有队友（含她）3 秒内掉了最大生命的 10% 以上，按在掉得最多的那个人身上；
//!   * 返照 R：10 万内的队友 3 秒内掉的血（按各自最大生命的百分比）加起来到 35%；
//!   * 沉锚 W：按她现在的姿态该切了才按（`anchor::want`），其余时候她的被动每 10 tick 自己判断。
//!
//! 按下去以后各英雄的原生代码再看一次自己的条件（返照的 15% / 60%、赊命的 35% / 60%、丧钟的两个人和半血……），
//! 用不上照样退冷却。

use std::collections::{HashMap, VecDeque};

use mod_api_stable::*;

use crate::{can_cast, dist_sq};

pub const HOURGLASS: &str = "abysspact_hourglass";
pub const VESPER: &str = "abysspact_vesper";
pub const ANCHOR: &str = "abysspact_anchor";

/// 一个待命格子按的条件。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Rule {
    /// 附近有敌方英雄就按，按在最近的那个身上。
    Near,
    /// 烛灵 R：附近有敌方英雄，而且有刚倒下的队友或残血被贴的队友。
    Revive,
    /// 返照 Q：有队友 3 秒内掉血够多。
    RewindOne,
    /// 返照 R：队友 3 秒内一共掉血够多。
    RewindAll,
    /// 沉锚 W：该切姿态了。
    Anchor,
}

#[derive(Clone, Copy, Debug)]
pub struct Arm {
    pub hero: &'static str,
    pub slot: SkillSlotV1,
    /// 这么近有敌方英雄才按（不超过这一格的施法距离：按的目标要在射程里）。
    pub near: u64,
    pub rule: Rule,
}

/// 所有待命格子（生成好的技能数据里 action_name 是 idle 的那几格，测试会对一遍）。
pub const ARMS: &[Arm] = &[
    Arm { hero: "abysspact_oathbreaker", slot: SkillSlotV1::Ult, near: 35_000, rule: Rule::Near },
    Arm { hero: VESPER, slot: SkillSlotV1::Ult, near: 60_000, rule: Rule::Revive },
    Arm { hero: HOURGLASS, slot: SkillSlotV1::Ult, near: 90_000, rule: Rule::RewindAll },
    Arm { hero: HOURGLASS, slot: SkillSlotV1::Skill, near: 90_000, rule: Rule::RewindOne },
    Arm { hero: "abysspact_debtor", slot: SkillSlotV1::Ult, near: 60_000, rule: Rule::Near },
    Arm { hero: "abysspact_knell", slot: SkillSlotV1::Ult, near: 50_000, rule: Rule::Near },
    Arm { hero: "abysspact_traceless", slot: SkillSlotV1::Skill2, near: 44_000, rule: Rule::Near },
    Arm { hero: ANCHOR, slot: SkillSlotV1::Skill2, near: 60_000, rule: Rule::Anchor },
];

/// 返照：3 秒（180 tick）内的血量；Q 按在掉了 10% 以上的队友身上（7 万内），R 等 10 万内一共掉 35%。
pub const REWIND_T: usize = 180;
pub const REWIND_ONE_PCT: usize = 10;
pub const REWIND_ONE_RANGE: u64 = 70_000;
pub const REWIND_ALL_PCT: usize = 35;
pub const REWIND_ALL_RANGE: u64 = 100_000;
/// 烛灵：10 秒内倒在 6 万内的队友；5 万内生命低于 35% 的队友、5 万内的敌方英雄。
pub const FALLEN_T: usize = 600;
pub const FALLEN_RANGE: u64 = 60_000;
pub const DANGER_RANGE: u64 = 50_000;
pub const DANGER_PCT: usize = 35;

/// 回城那道闩（league_ult_press 的 `still_recalling`）：回城命令开始，别的命令结束，没命令照旧。
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// AI 这一 tick 自己要放技能（或回城）：不盖掉它。
pub fn base_is_cast(base: Option<InputV1>) -> bool {
    base.is_some_and(|b| {
        [InputKindV1::Skill, InputKindV1::Skill2, InputKindV1::Ult, InputKindV1::Return].iter().any(|k| b.kind == k.code())
    })
}

fn input_kind(slot: SkillSlotV1) -> InputKindV1 {
    match slot {
        SkillSlotV1::Attack => InputKindV1::Attack,
        SkillSlotV1::Skill => InputKindV1::Skill,
        SkillSlotV1::Skill2 => InputKindV1::Skill2,
        SkillSlotV1::Ult => InputKindV1::Ult,
    }
}

/// 3 秒内掉了最大生命的百分之几：窗口里最早那一笔减现在（回了血就是 0）。
pub fn window_loss(hist: &VecDeque<(usize, usize, usize)>) -> usize {
    match (hist.front(), hist.back()) {
        (Some(&(_, old, _)), Some(&(_, now, max))) if max > 0 => old.saturating_sub(now).saturating_mul(100) / max,
        _ => 0,
    }
}

#[derive(Clone, Default)]
struct Press {
    recalling: bool,
    /// 返照：每个友方英雄最近 3 秒的 (tick, 生命, 最大生命)。
    hp: HashMap<usize, VecDeque<(usize, usize, usize)>>,
    /// 烛灵：每个队友（玩家）上一次看到时活没活、在哪；最近倒下的队友 (位置, tick)。
    seen: HashMap<usize, (bool, (u64, u64))>,
    fallen: HashMap<usize, ((u64, u64), usize)>,
}

impl Press {
    fn track_hp(&mut self, sim: &StableSim<'_>, team: usize, tick: usize) {
        let mut alive = Vec::new();
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(e) = sim.get_entity(id) else { continue };
            if e.team() != team || !e.is_alive() {
                continue;
            }
            let (hp, max) = e.hp();
            let q = self.hp.entry(id).or_default();
            q.push_back((tick, hp, max));
            while q.front().is_some_and(|&(t, _, _)| tick.saturating_sub(t) > REWIND_T) {
                q.pop_front();
            }
            alive.push(id);
        }
        self.hp.retain(|id, _| alive.contains(id));
    }

    fn track_deaths(&mut self, sim: &StableSim<'_>, team: usize, me: usize, tick: usize) {
        for i in 0..sim.player_count() {
            let Some(p) = sim.player_at(i) else { continue };
            let pid = p.id();
            if p.team() != team || pid == me {
                continue;
            }
            let alive = p.is_alive();
            let at = p.champion().map(|c| c.pos());
            let prev = self.seen.get(&pid).copied();
            if let Some((was, last)) = prev {
                if was && !alive {
                    self.fallen.insert(pid, (last, tick));
                }
            }
            if alive {
                self.fallen.remove(&pid);
            }
            let keep = if alive { at.or(prev.map(|x| x.1)) } else { prev.map(|x| x.1) };
            if let Some(pos) = keep {
                self.seen.insert(pid, (alive, pos));
            }
        }
        self.fallen.retain(|_, &mut (_, t)| tick.saturating_sub(t) <= FALLEN_T);
    }

    /// 这一格按不按、按在谁身上。`foes`：看得见、选得中的敌方英雄 (编号, 位置, 离她的距离平方)。
    fn target(&self, sim: &StableSim<'_>, arm: &Arm, me: &StableEntity<'_, '_>, foes: &[(usize, (u64, u64), u64)]) -> Option<usize> {
        let sq = |v: u64| v.saturating_mul(v);
        let (mid, team, at) = (me.id(), me.team(), me.pos());
        let nearest = foes.iter().filter(|f| f.2 <= sq(arm.near)).min_by_key(|f| f.2).map(|f| f.0);
        match arm.rule {
            Rule::Near => nearest,
            Rule::Revive => {
                let foe = nearest?;
                let fallen = self.fallen.values().any(|&(pos, _)| dist_sq(at, pos) <= sq(FALLEN_RANGE));
                let danger_foe = foes.iter().any(|f| f.2 <= sq(DANGER_RANGE));
                let hurt = (0..sim.champion_count())
                    .filter_map(|i| sim.get_entity(sim.champion_id_at(i)))
                    .filter(|e| e.team() == team && e.is_alive() && dist_sq(at, e.pos()) <= sq(DANGER_RANGE))
                    .any(|e| e.hp().0.saturating_mul(100) < e.hp().1.saturating_mul(DANGER_PCT));
                (fallen || (hurt && danger_foe)).then_some(foe)
            }
            Rule::RewindOne => {
                nearest?;
                self.hp
                    .iter()
                    .filter(|(id, _)| sim.get_entity(**id).is_some_and(|e| dist_sq(at, e.pos()) <= sq(REWIND_ONE_RANGE)))
                    .map(|(id, q)| (*id, window_loss(q)))
                    .filter(|&(_, l)| l >= REWIND_ONE_PCT)
                    .max_by_key(|&(_, l)| l)
                    .map(|(id, _)| id)
            }
            Rule::RewindAll => {
                nearest?;
                let total: usize = self
                    .hp
                    .iter()
                    .filter(|(id, _)| sim.get_entity(**id).is_some_and(|e| dist_sq(at, e.pos()) <= sq(REWIND_ALL_RANGE)))
                    .map(|(_, q)| window_loss(q))
                    .sum();
                (total >= REWIND_ALL_PCT).then_some(mid)
            }
            Rule::Anchor => {
                let foe = nearest?;
                let siege = crate::has_buff(sim, mid, crate::anchor::SIEGE_BUFF);
                let p = crate::anchor::Params::default();
                let closest = foes.iter().map(|f| f.2).min().unwrap_or(u64::MAX);
                let in_engage = foes.iter().any(|f| f.2 <= sq(p.engage as u64));
                crate::anchor::want(&p, siege, closest, in_engage, 0).map(|_| foe)
            }
        }
    }
}

impl StablePlayerAi for Press {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        "abysspact:press".to_string()
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        ARMS.iter().any(|a| a.hero == init.champion_name)
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        self.recalling = still_recalling(self.recalling, base);
        let cands: Vec<InputV1> = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            let name = me.name().unwrap_or_default();
            let team = me.team();
            // 返照、烛灵要看的历史每次都记
            if name == HOURGLASS {
                self.track_hp(&sim, team, tick);
            }
            if name == VESPER {
                self.track_deaths(&sim, team, player, tick);
            }
            if self.recalling || base_is_cast(base) || !can_cast(&sim, me.id()) {
                return None;
            }
            let ready = |s: SkillSlotV1| me.cooldown(s).is_some_and(|c| c.unlocked && c.remaining == 0);
            let arms: Vec<&Arm> = ARMS.iter().filter(|a| a.hero == name && ready(a.slot)).collect();
            if arms.is_empty() {
                return None;
            }
            let at = me.pos();
            let foes: Vec<(usize, (u64, u64), u64)> = (0..sim.champion_count())
                .filter_map(|i| sim.get_entity(sim.champion_id_at(i)))
                .filter(|e| e.team() != team && e.is_alive() && e.is_targetable() && sim.is_visible(team, e.id()))
                .map(|e| (e.id(), e.pos(), dist_sq(at, e.pos())))
                .collect();
            arms.iter()
                .filter_map(|a| self.target(&sim, a, &me, &foes).map(|t| InputV1::action(input_kind(a.slot), InputTargetV1::target(t))))
                .collect()
        };
        cands.into_iter().find(|i| ctx.is_valid_input(i))
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_player_input_ai(Press::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    const KITS: [(&str, &str); 20] = [
        ("abysspact_oathbreaker", include_str!("../../../abysspact/champion/abysspact_oathbreaker.data_champion")),
        ("abysspact_faceless", include_str!("../../../abysspact/champion/abysspact_faceless.data_champion")),
        ("abysspact_whisperer", include_str!("../../../abysspact/champion/abysspact_whisperer.data_champion")),
        ("abysspact_bonebow", include_str!("../../../abysspact/champion/abysspact_bonebow.data_champion")),
        ("abysspact_corvus", include_str!("../../../abysspact/champion/abysspact_corvus.data_champion")),
        ("abysspact_bloodmoon", include_str!("../../../abysspact/champion/abysspact_bloodmoon.data_champion")),
        ("abysspact_undertaker", include_str!("../../../abysspact/champion/abysspact_undertaker.data_champion")),
        ("abysspact_effigy", include_str!("../../../abysspact/champion/abysspact_effigy.data_champion")),
        ("abysspact_sevenfold", include_str!("../../../abysspact/champion/abysspact_sevenfold.data_champion")),
        ("abysspact_vesper", include_str!("../../../abysspact/champion/abysspact_vesper.data_champion")),
        ("abysspact_carapace", include_str!("../../../abysspact/champion/abysspact_carapace.data_champion")),
        ("abysspact_leech", include_str!("../../../abysspact/champion/abysspact_leech.data_champion")),
        ("abysspact_noctua", include_str!("../../../abysspact/champion/abysspact_noctua.data_champion")),
        ("abysspact_anchor", include_str!("../../../abysspact/champion/abysspact_anchor.data_champion")),
        ("abysspact_hourglass", include_str!("../../../abysspact/champion/abysspact_hourglass.data_champion")),
        ("abysspact_reprieve", include_str!("../../../abysspact/champion/abysspact_reprieve.data_champion")),
        ("abysspact_debtor", include_str!("../../../abysspact/champion/abysspact_debtor.data_champion")),
        ("abysspact_traceless", include_str!("../../../abysspact/champion/abysspact_traceless.data_champion")),
        ("abysspact_starfall", include_str!("../../../abysspact/champion/abysspact_starfall.data_champion")),
        ("abysspact_knell", include_str!("../../../abysspact/champion/abysspact_knell.data_champion")),
    ];

    /// 技能数据里一格的 (action_name, range)：找 `"<slot>": {` 之后的头两个字段（生成脚本的写法）。
    fn slot_of(kit: &str, slot: &str) -> (String, u64) {
        let at = kit.find(&format!("\"{slot}\": {{")).expect("slot");
        let rest = &kit[at..];
        let field = |key: &str| {
            let k = rest.find(&format!("\"{key}\": ")).expect(key) + key.len() + 4;
            let v = &rest[k..];
            v[..v.find([',', '\r', '\n']).unwrap()].trim().trim_matches('"').to_string()
        };
        (field("action_name"), field("range").parse().unwrap())
    }

    fn slot_name(s: SkillSlotV1) -> &'static str {
        match s {
            SkillSlotV1::Attack => "attack",
            SkillSlotV1::Skill => "skill",
            SkillSlotV1::Skill2 => "skill2",
            SkillSlotV1::Ult => "ult",
        }
    }

    #[test]
    fn every_armed_slot_of_the_kits_is_pressed_and_only_those() {
        let mut idle = Vec::new();
        for (id, kit) in KITS {
            for s in [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult] {
                let (name, range) = slot_of(kit, slot_name(s));
                if name == "idle" {
                    idle.push((id, s));
                    let arm = ARMS.iter().find(|a| a.hero == id && a.slot == s);
                    let arm = arm.unwrap_or_else(|| panic!("{id} {}: an armed slot nobody presses", slot_name(s)));
                    // 按在敌方英雄身上的格子：按的目标要在射程里
                    if matches!(arm.rule, Rule::Near | Rule::Revive | Rule::Anchor) {
                        assert!(arm.near <= range, "{id} {}: near {} past the range {range}", slot_name(s), arm.near);
                    }
                }
            }
        }
        assert_eq!(idle.len(), ARMS.len(), "a pressed slot that is no armed slot: {idle:?}");
    }

    #[test]
    fn the_hook_leaves_recalls_and_the_ais_own_casts() {
        let ret = Some(InputV1::action(InputKindV1::Return, InputTargetV1::NONE));
        let mv = Some(InputV1::move_to(1, 2));
        assert!(still_recalling(false, ret));
        assert!(still_recalling(true, None));
        assert!(!still_recalling(true, mv));
        assert!(base_is_cast(Some(InputV1::action(InputKindV1::Ult, InputTargetV1::target(3)))));
        assert!(base_is_cast(ret));
        assert!(!base_is_cast(mv));
        assert!(!base_is_cast(Some(InputV1::action(InputKindV1::Attack, InputTargetV1::target(3)))));
        assert!(!base_is_cast(None));
    }

    #[test]
    fn three_seconds_of_health() {
        let q: VecDeque<(usize, usize, usize)> = [(0, 1000, 1000), (60, 900, 1000), (120, 850, 1000)].into();
        assert_eq!(window_loss(&q), 15);
        let healed: VecDeque<(usize, usize, usize)> = [(0, 500, 1000), (60, 900, 1000)].into();
        assert_eq!(window_loss(&healed), 0);
        assert_eq!(window_loss(&VecDeque::new()), 0);
    }
}
