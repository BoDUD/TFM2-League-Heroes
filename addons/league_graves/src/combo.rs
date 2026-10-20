//! 格雷福斯的连招（用户 2026-10-20：「有连招的话一起做了」）：AI 钩子 `league_graves:combo` 替游戏的 AI 决定 E、R 什么时候按，
//! 像英雄联盟里会玩的人那样（判断在 `e_call` / `r_call`，纯计算、单元测试；数字是主包的，被动的 `params` 带过来）。
//!
//! 1. **换弹连招**（普攻 → E → 普攻 → 普攻）：主包的霰弹枪两发一换弹，E 装回一发（去掉 `a_1`）；换弹开始以后（第二发打出、
//!    他身上挂了换弹的 BlockAttack）就装不回了。游戏的 AI 一有目标就按 E，常常弹匣还满着就用掉。本包把 E 留到第一发打出去
//!    之后、第二发之前：
//!    - 第一发刚打出（`a_1` 在、剩余不超过 `a_keep - a_hit - 2`，没在换弹）、E 好了、普攻够得着的地方有敌人：替 AI 按 E（打
//!      AI 正在打的那个，没有就最近的敌方英雄、再没有就最近的敌人）——这一轮换弹打三枪；
//!    - 弹匣满着或已经在换弹、普攻够得着的地方有敌人时，AI 按的 E 改成普攻；逃命（生命不到 `E_FLEE` 而 e_near 内有敌方英雄：
//!      E 往后滚开）、追残血（生命不到 `CHASE_LOW` 的敌方英雄在普攻够不着、E 够得着的地方）、够不着任何敌人时（E 当位移）照放。
//! 2. **大招收割**：R 停在路上的第一个敌方英雄身上（`first_on_line`）。AI 想放 R 时，只有打得死那个英雄（生命 + 护盾不超过 R
//!    按护甲打折后的伤害）、或他身后的锥形里还有敌方英雄（一炮两人，本包的锥形）、或自己残血（生命不到 `R_FLEE` 而 `R_THREAT`
//!    内有敌方英雄：后坐力把他弹开）才放；别的方向能打死人就换过去，都不行就改成普攻。R 好了、有打得死的英雄、AI 没在放
//!    技能时替它按 R。
//!
//! 被控住、正在放技能（施法动作 `Animation`）或被强制位移时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。

use mod_api_stable::*;

use super::{counted, head, params_of, sn, who, wlog, Params, ID};

/// 排在 league_ult_press（100）之后：引擎按优先级从小到大跑 AI 钩子，每个拿到前一个的决定。
pub const COMBO_PRIORITY: i32 = 110;
/// 生命低于这一比例、e_near 内有敌方英雄：AI 的 E 照放（往后滚开）。
pub const E_FLEE: f64 = 0.35;
/// 敌方英雄生命低于这一比例、在普攻够不着而 E 够得着的地方：AI 的 E 照放（追上去）。
pub const CHASE_LOW: f64 = 0.3;
/// AI 在走路时（可能在撤）只在生命不低于这一比例时替它按 E。
pub const MOVE_E: f64 = 0.5;
/// 生命低于这一比例、`R_THREAT` 内有敌方英雄：AI 的 R 照放（后坐力把他弹开）。
pub const R_FLEE: f64 = 0.25;
pub const R_THREAT: f64 = 25_000.0;

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 格雷福斯自己这一 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub r: f64,
    pub hp: f64,
    pub ad: usize,
    /// `a_1`（第一发打出后挂的）还剩几 tick；没有就是 None。
    pub a1_left: Option<usize>,
    /// 身上有 BlockAttack（第二发之后的换弹，或被缴械）。
    pub reloading: bool,
    pub e_ready: bool,
    pub r_ready: bool,
}

/// 一个敌方单位。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: Pt,
    pub r: f64,
    pub hp: usize,
    pub shield: usize,
    pub max: usize,
    pub def: usize,
    pub champion: bool,
}

impl Unit {
    pub fn share(&self) -> f64 {
        if self.max == 0 {
            1.0
        } else {
            self.hp as f64 / self.max as f64
        }
    }
}

/// AI 这一 tick 想做的（钩子拿到的决定）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Want {
    Attack(Option<usize>),
    Move,
    Q,
    E(Option<usize>),
    R(Option<usize>),
    Other,
}

#[derive(Clone, Debug, PartialEq)]
pub enum Call {
    /// 替 AI 按 E / R：目标、为什么。
    PressE(usize, &'static str),
    PressR(usize, String),
    /// AI 按的 E / R 不合适：改成普攻这个目标（None：站住）。
    Veto(&'static str, Option<usize>, String),
}

/// 第一发已经打出去、还没开始换弹：这时按 E，弹匣又是两发。
pub fn one_shell_out(me: &Me, p: &Params) -> bool {
    !me.reloading && me.a1_left.is_some_and(|t| t + p.a_hit + 2 <= p.a_keep)
}

/// 普攻够得着（中心距离 = 射程 + 两人的半径）。
pub fn in_reach(me: &Me, u: &Unit, p: &Params) -> bool {
    dist(me.at, u.at) <= p.atk_range as f64 + me.r + u.r
}

fn nearest<'a>(me: &Me, foes: &'a [Unit], f: impl Fn(&Unit) -> bool) -> Option<&'a Unit> {
    foes.iter().filter(|u| f(u)).min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at)))
}

/// 普攻打谁：AI 自己挑的（够得着的敌人）、否则最近的够得着的敌方英雄、再否则最近的够得着的敌人。
pub fn shoot_at(me: &Me, foes: &[Unit], p: &Params, ai: Option<usize>) -> Option<usize> {
    ai.and_then(|t| foes.iter().find(|u| u.id == t && in_reach(me, u, p)).map(|u| u.id))
        .or_else(|| nearest(me, foes, |u| u.champion && in_reach(me, u, p)).map(|u| u.id))
        .or_else(|| nearest(me, foes, |u| in_reach(me, u, p)).map(|u| u.id))
}

/// E：替 AI 按、改成普攻、或不管（None）。
pub fn e_call(me: &Me, foes: &[Unit], p: &Params, want: Want) -> Option<Call> {
    let shell = one_shell_out(me, p);
    match want {
        Want::E(t) => {
            if shell {
                return None; // the combo's moment: let it go
            }
            let target = shoot_at(me, foes, p, t)?; // nothing in reach: E as a dash, let it go
            let flee = me.hp < E_FLEE
                && foes.iter().any(|u| u.champion && dist(me.at, u.at) <= p.e_near as f64 + me.r + u.r);
            let chase = foes.iter().any(|u| {
                u.champion && u.share() < CHASE_LOW && !in_reach(me, u, p)
                    && dist(me.at, u.at) <= p.e_range as f64 + me.r + u.r
            });
            if flee || chase {
                return None;
            }
            let why = if me.reloading { "the reload has begun: E would load nothing" } else { "both shells loaded" };
            Some(Call::Veto("veto e", Some(target), format!("E VETO: {why} - shoot first, E after the first shell")))
        }
        Want::Attack(t) if shell && me.e_ready => {
            let target = shoot_at(me, foes, p, t)?;
            Some(Call::PressE(target, "the first shell is out: E loads it back, three shots before the reload"))
        }
        // walking (maybe away): only while he is not hurt - E dashes at the target unless a champion is close
        Want::Move if shell && me.e_ready && me.hp >= MOVE_E => {
            let target = shoot_at(me, foes, p, None)?;
            Some(Call::PressE(target, "the first shell is out: E loads it back, three shots before the reload"))
        }
        _ => None,
    }
}

/// R 往 `toward` 放，停在谁身上：从他到 `toward` 这条线上、离线不超过半宽加半径、沿线最近的敌方英雄。
pub fn first_on_line(me: &Me, toward: Pt, champs: &[Unit], p: &Params) -> Option<Unit> {
    let d = dist(me.at, toward);
    if d < 1.0 {
        return None;
    }
    let (ux, uy) = ((toward.0 - me.at.0) / d, (toward.1 - me.at.1) / d);
    champs
        .iter()
        .filter_map(|c| {
            let (vx, vy) = (c.at.0 - me.at.0, c.at.1 - me.at.1);
            let along = vx * ux + vy * uy;
            let off = (vx * uy - vy * ux).abs();
            (along >= 0.0 && along <= p.r_range as f64 + c.r && off <= p.r_w as f64 / 2.0 + c.r).then_some((along, *c))
        })
        .min_by(|a, b| a.0.total_cmp(&b.0))
        .map(|(_, c)| c)
}

/// R 打一个英雄（物理伤害，按护甲打折：100 / (100 + 护甲)）。
pub fn r_damage(ad: usize, def: usize, p: &Params) -> usize {
    (p.r_dmg + ad * p.r_ratio / 100) * 100 / (100 + def)
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RWhy {
    Kill,
    Two,
}

/// R 打中 `first` 值不值：打得死他，或他身后的锥形里还有敌方英雄。
pub fn r_worth(me: &Me, first: &Unit, champs: &[Unit], p: &Params) -> Option<RWhy> {
    if first.hp + first.shield <= r_damage(me.ad, first.def, p) {
        return Some(RWhy::Kill);
    }
    let more = champs.iter().any(|c| {
        c.id != first.id && super::in_cone(me.at, first.at, c.at, p.r_len as f64, p.r_dot as f64)
    });
    more.then_some(RWhy::Two)
}

/// 施放距离内、R 打得死的方向（停下的那个英雄打得死）：挑生命 + 护盾最少的。
pub fn r_kill(me: &Me, champs: &[Unit], p: &Params) -> Option<(usize, Unit)> {
    champs
        .iter()
        .filter(|c| dist(me.at, c.at) <= p.r_cast as f64 + me.r + c.r)
        .filter_map(|c| first_on_line(me, c.at, champs, p).map(|f| (c.id, f)))
        .filter(|(_, f)| r_worth(me, f, champs, p) == Some(RWhy::Kill))
        .min_by_key(|(_, f)| f.hp + f.shield)
}

/// R：替 AI 按、换个方向、改成普攻、或不管（None）。
pub fn r_call(me: &Me, foes: &[Unit], p: &Params, want: Want) -> Option<Call> {
    let champs: Vec<Unit> = foes.iter().copied().filter(|u| u.champion).collect();
    match want {
        Want::R(t) => {
            let flee = me.hp < R_FLEE && champs.iter().any(|c| dist(me.at, c.at) <= R_THREAT + me.r + c.r);
            if flee {
                return None;
            }
            let aimed = t.and_then(|t| champs.iter().find(|c| c.id == t)).and_then(|c| first_on_line(me, c.at, &champs, p));
            if aimed.is_some_and(|f| r_worth(me, &f, &champs, p).is_some()) {
                return None; // a kill or two champions: let it go
            }
            if let Some((t, f)) = r_kill(me, &champs, p) {
                return Some(Call::PressR(t, format!("turned to the kill: {} hp {}+{} <= ~{}", f.id, f.hp, f.shield,
                                                    r_damage(me.ad, f.def, p))));
            }
            let target = shoot_at(me, foes, p, None);
            Some(Call::Veto("veto r", target, "R VETO: no kill and nobody behind the champion it would hit".to_string()))
        }
        Want::Attack(_) | Want::Move if me.r_ready => {
            let (t, f) = r_kill(me, &champs, p)?;
            Some(Call::PressR(t, format!("a kill: {} hp {}+{} <= ~{}", f.id, f.hp, f.shield, r_damage(me.ad, f.def, p))))
        }
        _ => None,
    }
}

/// 两件事一起看：大招收割在前，换弹连招在后。
pub fn call(me: &Me, foes: &[Unit], p: &Params, want: Want) -> Option<Call> {
    r_call(me, foes, p, want).or_else(|| e_call(me, foes, p, want))
}

// ===================== 游戏里 =====================

/// 放不出技能的控制，和正在放技能 / 被强制位移。
const STOP: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
    CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

fn ready(e: &StableEntity<'_, '_>, slot: SkillSlotV1) -> bool {
    e.cooldown(slot).is_some_and(|c| c.unlocked && c.remaining == 0)
}

fn want_of(base: Option<InputV1>) -> Want {
    let Some(b) = base else { return Want::Move };
    let target = (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id);
    match InputKindV1::from_code(b.kind) {
        Some(InputKindV1::Attack) => Want::Attack(target),
        Some(InputKindV1::Move) => Want::Move,
        Some(InputKindV1::Skill) => Want::Q,
        Some(InputKindV1::Skill2) => Want::E(target),
        Some(InputKindV1::Ult) => Want::R(target),
        _ => Want::Other,
    }
}

/// 这一 tick 的格雷福斯和看得见的敌人；被控住、正在放技能时 None。
fn read(sim: &StableSim<'_>, me: usize) -> Option<(Me, Vec<Unit>)> {
    let e = sim.get_entity(me)?;
    if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
        return None;
    }
    let a1 = sn("a_1");
    let a1_left = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == a1).map(|b| b.duration_tick);
    let reloading = (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| c.kind == CcKindV1::BlockAttack.code()));
    let (hp, max) = e.hp();
    let (x, y) = e.pos();
    let team = e.team();
    let m = Me { at: (x as f64, y as f64), r: e.radius() as f64, hp: if max > 0 { hp as f64 / max as f64 } else { 1.0 },
                 ad: e.stat().attack, a1_left, reloading, e_ready: ready(&e, SkillSlotV1::Skill2),
                 r_ready: ready(&e, SkillSlotV1::Ult) };
    let mut foes = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || u.is_tower() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
            continue;
        }
        let (hp, max) = u.hp();
        let (x, y) = u.pos();
        foes.push(Unit { id: u.id(), at: (x as f64, y as f64), r: u.radius() as f64, hp, shield: u.shield(), max,
                         def: u.stat().defence, champion: u.is_champion() });
    }
    Some((m, foes))
}

#[derive(Clone, Default)]
pub struct Combo;

impl StablePlayerAi for Combo {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:combo")
    }

    fn priority(&self) -> i32 {
        COMBO_PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let (call, line, names) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?.id();
            let (m, foes) = read(&sim, me)?;
            let p = params_of(&sim, me);
            let c = call(&m, &foes, &p, want_of(base))?;
            let target = match &c {
                Call::PressE(t, _) | Call::PressR(t, _) => Some(*t),
                Call::Veto(_, t, _) => *t,
            };
            let shells = if m.reloading { "reloading".to_string() } else if one_shell_out(&m, &p) { "1 shell".to_string() }
                         else { "2 shells".to_string() };
            (c, format!("{} [{shells}, hp {:.0}%]", head(&sim, me), m.hp * 100.0), target.map(|t| who(&sim, t)))
        };
        let on = names.unwrap_or_else(|| "-".to_string());
        match call {
            Call::PressE(t, why) => {
                let input = InputV1::action(InputKindV1::Skill2, InputTargetV1::target(t));
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                if let Some(k) = counted("e press") {
                    wlog(format!("{line} E PRESS on {on}: {why} #{k}"));
                }
                Some(input)
            }
            Call::PressR(t, why) => {
                let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(t));
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                if let Some(k) = counted("r press") {
                    wlog(format!("{line} R PRESS toward {on}: {why} #{k}"));
                }
                Some(input)
            }
            Call::Veto(kind, t, why) => {
                let input = match t {
                    Some(t) => InputV1::action(InputKindV1::Attack, InputTargetV1::target(t)),
                    None => return None,
                };
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                if let Some(k) = counted(kind) {
                    wlog(format!("{line} {why}; shoots {on} instead #{k}"));
                }
                Some(input)
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn me(a1: Option<usize>, reloading: bool) -> Me {
        Me { at: (0.0, 0.0), r: 3000.0, hp: 1.0, ad: 150, a1_left: a1, reloading, e_ready: true, r_ready: true }
    }

    fn champ(id: usize, x: f64, y: f64, hp: usize) -> Unit {
        Unit { id, at: (x, y), r: 3000.0, hp, shield: 0, max: 1500, def: 50, champion: true }
    }

    fn camp(id: usize, x: f64) -> Unit {
        Unit { id, at: (x, 0.0), r: 4000.0, hp: 1200, shield: 0, max: 1200, def: 20, champion: false }
    }

    #[test]
    fn e_waits_for_the_first_shell() {
        let p = Params::default();
        let foes = [champ(1, 40_000.0, 0.0, 1400)];
        // both shells loaded: the AI's E becomes a shot at the champion in reach
        assert!(matches!(e_call(&me(None, false), &foes, &p, Want::E(Some(1))), Some(Call::Veto(_, Some(1), _))));
        // the first shell just fired (a_1 set two ticks before the shot): E still waits for the pellet
        assert_eq!(e_call(&me(Some(p.a_keep - p.a_hit + 1), false), &foes, &p, Want::Attack(Some(1))), None);
        // the pellet is out: E is pressed on the AI's target
        let out = Some(p.a_keep - p.a_hit - 2);
        assert!(matches!(e_call(&me(out, false), &foes, &p, Want::Attack(Some(1))), Some(Call::PressE(1, _))));
        // and the AI's own E goes through
        assert_eq!(e_call(&me(out, false), &foes, &p, Want::E(Some(1))), None);
        // reloading: E loads nothing - the AI's E becomes a shot (it cannot shoot, but the attack waits in the queue)
        assert!(matches!(e_call(&me(out, true), &foes, &p, Want::E(Some(1))), Some(Call::Veto(_, Some(1), _))));
        // and nothing is pressed for it
        assert_eq!(e_call(&me(out, true), &foes, &p, Want::Attack(Some(1))), None);
    }

    #[test]
    fn e_still_rolls_away_chases_and_dashes() {
        let p = Params::default();
        let mut low = me(None, false);
        low.hp = 0.2;
        let close = [champ(1, 20_000.0, 0.0, 1400)];
        assert_eq!(e_call(&low, &close, &p, Want::E(Some(1))), None); // the roll away
        let fleeing = [champ(2, 60_000.0, 0.0, 300), camp(3, 30_000.0)];
        assert_eq!(e_call(&me(None, false), &fleeing, &p, Want::E(Some(2))), None); // after a champion at 20%
        let far = [camp(4, 80_000.0)];
        assert_eq!(e_call(&me(None, false), &far, &p, Want::E(Some(4))), None); // nothing in reach: a dash
    }

    #[test]
    fn e_clears_camps_too() {
        let p = Params::default();
        let foes = [camp(5, 30_000.0)];
        let out = Some(p.a_keep - p.a_hit - 2);
        assert!(matches!(e_call(&me(out, false), &foes, &p, Want::Attack(Some(5))), Some(Call::PressE(5, _))));
    }

    #[test]
    fn the_shell_stops_on_the_first_champion() {
        let p = Params::default();
        let front = champ(1, 40_000.0, 1_000.0, 1400);
        let back = champ(2, 80_000.0, 0.0, 200);
        let aside = champ(3, 40_000.0, 30_000.0, 200);
        let all = [front, back, aside];
        assert_eq!(first_on_line(&me(None, false), back.at, &all, &p).map(|c| c.id), Some(1));
        assert_eq!(first_on_line(&me(None, false), aside.at, &all, &p).map(|c| c.id), Some(3));
    }

    #[test]
    fn r_damage_follows_armour() {
        let p = Params::default();
        // (120 + 150 x 90%) x 100 / (100 + 50) = 255 x 2/3 = 170
        assert_eq!(r_damage(150, 50, &p), 170);
    }

    #[test]
    fn r_only_for_a_kill_or_two() {
        let p = Params::default();
        let m = me(None, false);
        let full = [champ(1, 50_000.0, 0.0, 1400)];
        assert!(matches!(r_call(&m, &full, &p, Want::R(Some(1))), Some(Call::Veto(..))));
        let low = [champ(1, 50_000.0, 0.0, 160)];
        assert_eq!(r_call(&m, &low, &p, Want::R(Some(1))), None);
        let two = [champ(1, 50_000.0, 0.0, 1400), champ(2, 80_000.0, 3_000.0, 1400)];
        assert_eq!(r_call(&m, &two, &p, Want::R(Some(1))), None);
        // a full-health champion aimed at, a low one elsewhere in range: turned to the kill
        let other = [champ(1, 50_000.0, 0.0, 1400), champ(2, 0.0, 60_000.0, 150)];
        assert!(matches!(r_call(&m, &other, &p, Want::R(Some(1))), Some(Call::PressR(2, _))));
        // the low one hides behind a full one on the line: the shell would stop on the full one - no kill
        let hidden = [champ(1, 40_000.0, 0.0, 1400), champ(2, 80_000.0, 0.0, 150)];
        assert!(r_kill(&m, &hidden, &p).is_none());
        // R ready, the AI attacking, a kill in range: pressed
        assert!(matches!(r_call(&m, &low, &p, Want::Attack(Some(1))), Some(Call::PressR(1, _))));
        // low on health with a champion on top of him: the recoil is his way out
        let mut hurt = me(None, false);
        hurt.hp = 0.2;
        let near = [champ(1, 20_000.0, 0.0, 1400)];
        assert_eq!(r_call(&hurt, &near, &p, Want::R(Some(1))), None);
    }
}
