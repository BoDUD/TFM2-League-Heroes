//! 薇恩的 AI 钩子 `league_vayne_bolts:condemn`（用户 2026-11-02：「找墙放E要智能一点」「参考卡密尔多智能」）。恶魔审判撞墙
//! 才晕（`condemn`），游戏的 AI 却见人就放、不看墙。照卡蜜尔附加包钩墙的做法——记下敌方英雄的位置算出速度，预判出手那一刻
//! 他在哪；附近没有合适的就不出手——：
//!
//! - E 好了、她没被控、AI 不在放 Q / R 时，看射程里（AI 也认可的）每个敌方英雄：重箭打到他那一刻（第 `E_START` tick 出箭，
//!   再飞 距离 / `E_BOLT_SPEED` tick）他照这几 tick 的速度走到哪（最多 `LEAD_MAX`，碰到墙就停），从薇恩那里往他身后推，
//!   `E_KB_SPEED` x `E_KB_T` 的路上有墙——他现在站的地方和预判的地方都有——就替 AI 对他放 E（`E WALL`）：AI 正在打的人
//!   优先，再挑血量低的、身后的墙近的；
//! - 谁身后都没墙时：近身（身体之间不到 `PEEL_GAP`）的敌方英雄，AI 要放 E 或者她血量低于 `PEEL_HP`% 时推开自保（`E PEEL`）；
//!   AI 要放 E、这一箭打得死人的照放（`E KILL`）；别的时候 AI 想放 E 就不放，改打 AI 要 E 的那个人（打不到就走过去），等墙
//!   （`E HELD`）。
//!
//! 一次按键（引擎接下施放之前钩子每 tick 都再按）只记一行。

use std::collections::HashMap;

use mod_api_stable::*;

use super::{current, head, tally, unit, unit_points, wall_travel, wlog, Grid, Pt, E_BOLT_SPEED, E_KB_SPEED, E_KB_T, E_RANGE, E_START,
            ID};

/// 排在 league_ult_press（100）之后，同别的连招钩子。
pub const PRIORITY: i32 = 110;
/// 预判他走多远为止（卡蜜尔附加包的 24000）。
pub const LEAD_MAX: f64 = 24_000.0;
/// 速度按这么多 tick 之内的上一个位置算（再久的不算：他可能死过、闪现过）。
pub const VEL_SPAN: usize = 6;
/// 一 tick 走超过这么远的不算速度（闪现、传送）。
pub const VEL_MAX: f64 = 4_000.0;
/// 身体之间不到这么远算贴脸（近战英雄的普攻 23000～28000 是中心之间，减去两人的身体约 6000～12000）。
pub const PEEL_GAP: f64 = 8_000.0;
/// 血量低于这么多 % 时贴脸的人她自己就推开（AI 没想放 E 也放）。
pub const PEEL_HP: usize = 40;
/// 同一个人、同一类按键，离上一次不到这么多 tick 算同一次（league_ult_press 的 ORDER_FRESH）。
pub const PRESS_FRESH: usize = 30;

/// 主包重箭打中时的伤害：60 + 70% 攻击力（物理）。
pub const E_DMG: usize = 60;
pub const E_RATIO: usize = 70;

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 她自己这一 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub r: f64,
    pub ad: usize,
    pub hp_pct: usize,
}

/// 射程里一个敌方英雄（AI 认可对他放 E 的）：位置、身体、速度（每 tick）、生命、护盾、护甲。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub r: f64,
    pub vel: Pt,
    pub hp: usize,
    pub max: usize,
    pub shield: usize,
    pub armor: usize,
}

/// 这一 tick 怎么办。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Call {
    /// 对他放 E：他身后的墙多远（推多远就撞上）、预判他走了多远。
    Wall(usize, f64, f64),
    /// 对他放 E 自保：身体之间多远。
    Peel(usize, f64),
    /// 对他放 E 收人头：这一箭约打多少、他的生命 + 护盾。
    Kill(usize, usize, usize),
    /// AI 想放 E 却谁身后都没墙：不放，改打这个人。
    Hold(usize),
}

/// 重箭打到 `d` 远的人要几 tick（出手 + 飞）。
pub fn hit_ticks(d: f64) -> usize {
    E_START + (d / E_BOLT_SPEED as f64).ceil() as usize
}

/// 照速度 `vel` 走 `ticks` tick 后他在哪：最多 `LEAD_MAX`，路上碰到墙就停在墙前。
pub fn lead(grid: &Grid, at: Pt, vel: Pt, ticks: usize) -> Pt {
    let want = (vel.0 * ticks as f64, vel.1 * ticks as f64);
    let len = (want.0 * want.0 + want.1 * want.1).sqrt().min(LEAD_MAX);
    let Some(dir) = unit(want) else { return at };
    let go = wall_travel(grid, at, dir, len, 0.0).map_or(len, |w| w.min(len));
    (at.0 + dir.0 * go, at.1 + dir.1 * go)
}

/// 薇恩在 `me` 把站在 `at`、身体 `r` 的人往后推：身后的墙多远（`condemn` 的同一个判断），没墙就 None。
pub fn wall_behind(grid: &Grid, me: Pt, at: Pt, r: f64) -> Option<f64> {
    let dir = unit((at.0 - me.0, at.1 - me.1))?;
    wall_travel(grid, at, dir, (E_KB_SPEED * E_KB_T) as f64, r)
}

/// 这一箭约打多少（物理伤害按护甲减）。
pub fn bolt_damage(ad: usize, armor: usize) -> usize {
    (E_DMG + E_RATIO * ad / 100) * 100 / (100 + armor)
}

/// AI 这一 tick想要的：放 E（对谁）、普攻（对谁），别的。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Want {
    E(Option<usize>),
    Attack(Option<usize>),
    /// Q、R：不打扰。
    Skill,
    Other,
}

pub fn want_of(base: Option<InputV1>) -> Want {
    let Some(b) = base else { return Want::Other };
    let target = (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id);
    match InputKindV1::from_code(b.kind) {
        Some(InputKindV1::Skill2) => Want::E(target),
        Some(InputKindV1::Attack) => Want::Attack(target),
        Some(InputKindV1::Skill | InputKindV1::Ult) => Want::Skill,
        _ => Want::Other,
    }
}

/// 这一 tick的决定（`foes`：射程里 AI 认可的敌方英雄）。
pub fn call(grid: &Grid, me: &Me, foes: &[Foe], want: Want) -> Option<Call> {
    if want == Want::Skill {
        return None;
    }
    let aimed = match want {
        Want::E(t) | Want::Attack(t) => t,
        _ => None,
    };
    // 1. someone with a wall behind him, now and where the bolt will find him
    let walls = foes.iter().filter_map(|f| {
        let now = wall_behind(grid, me.at, f.at, f.r)?;
        let there = lead(grid, f.at, f.vel, hit_ticks(dist(me.at, f.at)));
        let then = wall_behind(grid, me.at, there, f.r)?;
        Some((f, now.max(then), dist(f.at, there)))
    });
    let best = walls.min_by_key(|(f, len, _)| (Some(f.id) != aimed, f.hp * 10 / f.max.max(1), *len as u64));
    if let Some((f, len, moved)) = best {
        return Some(Call::Wall(f.id, len, moved));
    }
    // 2. someone on her: pushed off when the AI wants E or she is low
    let gap = |f: &Foe| dist(me.at, f.at) - me.r - f.r;
    if let Some(f) = foes.iter().filter(|f| gap(f) <= PEEL_GAP).min_by(|a, b| gap(a).total_cmp(&gap(b))) {
        if matches!(want, Want::E(_)) || me.hp_pct < PEEL_HP {
            return Some(Call::Peel(f.id, gap(f)));
        }
    }
    let Want::E(t) = want else { return None };
    // 3. a bolt that finishes someone
    if let Some(f) = foes.iter().find(|f| bolt_damage(me.ad, f.armor) >= f.hp + f.shield) {
        return Some(Call::Kill(f.id, bolt_damage(me.ad, f.armor), f.hp + f.shield));
    }
    // 4. no wall behind anyone: keep E, attack the one the AI wanted it on
    t.or_else(|| foes.iter().min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at))).map(|f| f.id)).map(Call::Hold)
}

const STOP: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
    CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

/// The AI is still recalling (league_ornn's combo): its last order was a Return, and any other order ends it.
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

#[derive(Clone, Default)]
pub struct Condemn {
    recalling: bool,
    /// enemy champions' last seen (tick, place): their speed
    seen: HashMap<usize, (usize, Pt)>,
    /// the last press: its kind, target, tick (one log line a burst)
    last: Option<(&'static str, usize, usize)>,
}

impl StablePlayerAi for Condemn {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:condemn")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == "league_vayne"
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        self.recalling = still_recalling(self.recalling, base);
        if self.recalling {
            return None;
        }
        let player = ctx.player_id();
        let (me, foes, grid, line, tick, names) = {
            let sim = ctx.sim()?;
            let e = sim.get_player(player)?.champion()?;
            let (my_id, team, tick) = (e.id(), e.team(), sim.tick());
            // every tick: where the enemy champions are (their speed for the lead)
            let mut seen = Vec::new();
            let mut names = HashMap::new();
            for i in 0..sim.champion_count() {
                let Some(u) = sim.get_entity(sim.champion_id_at(i)) else { continue };
                if u.team() == team || !u.is_alive() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
                    continue;
                }
                let at = (u.pos().0 as f64, u.pos().1 as f64);
                let vel = match self.seen.get(&u.id()) {
                    Some(&(t0, p0)) if t0 < tick && tick - t0 <= VEL_SPAN && dist(p0, at) <= VEL_MAX * (tick - t0) as f64 => {
                        let k = (tick - t0) as f64;
                        ((at.0 - p0.0) / k, (at.1 - p0.1) / k)
                    }
                    _ => (0.0, 0.0),
                };
                let immune = (0..u.buff_count()).filter_map(|i| u.buff_at(i)).any(|b| b.cc_immune);
                names.insert(u.id(), u.name().unwrap_or_default());
                let (hp, max) = u.hp();
                seen.push((Foe { id: u.id(), at, r: u.radius() as f64, vel, hp, max, shield: u.shield(), armor: u.stat().defence },
                           immune));
            }
            self.seen = seen.iter().map(|(f, _)| (f.id, (tick, f.at))).collect();
            let ready = e.cooldown(SkillSlotV1::Skill2).is_some_and(|c| c.unlocked && c.remaining == 0);
            let held = (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind)));
            if !e.is_alive() || !ready || held {
                return None;
            }
            let reach = |f: &Foe| dist((e.pos().0 as f64, e.pos().1 as f64), f.at) <= E_RANGE as f64 + e.radius() as f64 + f.r;
            // immune to crowd control: the push does nothing to them
            let foes: Vec<Foe> = seen.into_iter().filter(|(f, immune)| !immune && reach(f)).map(|(f, _)| f).collect();
            if foes.is_empty() {
                return None;
            }
            let grids = Grid::builtin();
            let grid = current(&grids, &unit_points(&sim)).and_then(|i| grids.into_iter().nth(i))?;
            let (hp, max) = e.hp();
            let me = Me { at: (e.pos().0 as f64, e.pos().1 as f64), r: e.radius() as f64, ad: e.stat().attack,
                          hp_pct: hp * 100 / max.max(1) };
            (me, foes, grid, head(&sim, my_id), tick, names)
        };
        // the engine has the last word on the range: E only at those it takes
        let can_e = |ctx: &StableAiContext<'_>, id: usize| ctx.is_valid_input(&InputV1::action(InputKindV1::Skill2, InputTargetV1::target(id)));
        let foes: Vec<Foe> = foes.into_iter().filter(|f| can_e(ctx, f.id)).collect();
        if foes.is_empty() {
            return None;
        }
        let c = call(&grid, &me, &foes, want_of(base))?;
        let name = |id: usize| names.get(&id).cloned().unwrap_or_default();
        let (input, kind, text) = match c {
            Call::Wall(t, len, moved) => (InputV1::action(InputKindV1::Skill2, InputTargetV1::target(t)), "e wall",
                format!("E WALL on {}#{t}: a wall {len:.0} behind him where the bolt lands (he moves {moved:.0} till then)", name(t))),
            Call::Peel(t, gap) => (InputV1::action(InputKindV1::Skill2, InputTargetV1::target(t)), "e peel",
                format!("E PEEL on {}#{t}: {gap:.0} from her, hp {}%", name(t), me.hp_pct)),
            Call::Kill(t, d, ehp) => (InputV1::action(InputKindV1::Skill2, InputTargetV1::target(t)), "e kill",
                format!("E KILL on {}#{t}: the bolt does about {d} >= health + shield {ehp}", name(t))),
            Call::Hold(t) => {
                let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                let input = if ctx.is_valid_input(&attack) {
                    attack
                } else {
                    let at = foes.iter().find(|f| f.id == t).map_or(me.at, |f| f.at);
                    InputV1::move_to(at.0.max(0.0) as u64, at.1.max(0.0) as u64)
                };
                (input, "e held", format!("E HELD: no wall behind anyone in reach - attacking {}#{t} instead", name(t)))
            }
        };
        let t = match c {
            Call::Wall(t, ..) | Call::Peel(t, _) | Call::Kill(t, ..) | Call::Hold(t) => t,
        };
        let burst = self.last.is_some_and(|(k, at, t0)| k == kind && at == t && tick >= t0 && tick <= t0 + PRESS_FRESH);
        self.last = Some((kind, t, tick));
        if !burst {
            if let Some(k) = ctx.sim().and_then(|sim| tally(&sim, kind)) {
                wlog(format!("{line} {text} #{k}"));
            }
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn moba() -> Grid {
        Grid::builtin().into_iter().next().unwrap()
    }

    fn foe(id: usize, x: f64, y: f64) -> Foe {
        Foe { id, at: (x, y), r: 6_000.0, vel: (0.0, 0.0), hp: 900, max: 1_800, shield: 0, armor: 30 }
    }

    fn me(x: f64, y: f64) -> Me {
        Me { at: (x, y), r: 6_000.0, ad: 150, hp_pct: 90 }
    }

    #[test]
    fn the_bolt_lands_after_its_windup_and_flight() {
        assert_eq!(hit_ticks(0.0), E_START);
        assert_eq!(hit_ticks(49_000.0), E_START + 7);
    }

    #[test]
    fn the_lead_follows_his_speed_up_to_a_wall() {
        let g = moba();
        // open ground: 1000 a tick for 10 ticks
        assert_eq!(lead(&g, (480_000.0, 480_000.0), (1_000.0, 0.0), 10), (490_000.0, 480_000.0));
        // never more than LEAD_MAX
        let far = lead(&g, (480_000.0, 480_000.0), (3_000.0, 0.0), 30);
        assert!((far.0 - 480_000.0 - LEAD_MAX).abs() < 1.0);
        // walking at the 5v5 map's left edge: stops before it
        let edge = lead(&g, (40_000.0, 480_000.0), (-2_000.0, 0.0), 20);
        assert!(edge.0 > 22_500.0 && edge.0 < 40_000.0, "{edge:?}");
        // standing: where he is
        assert_eq!(lead(&g, (40_000.0, 480_000.0), (0.0, 0.0), 20), (40_000.0, 480_000.0));
    }

    #[test]
    fn e_goes_at_the_one_with_a_wall_behind_him() {
        let g = moba();
        let v = me(90_000.0, 480_000.0);
        // pinned against the left edge (x 22500) from her right, and one on open ground the AI is hitting
        let wall = foe(1, 40_000.0, 480_000.0);
        let open = foe(2, 90_000.0, 430_000.0);
        assert!(matches!(call(&g, &v, &[open, wall], Want::Attack(Some(2))), Some(Call::Wall(1, ..))));
        // he walks off the wall faster than the bolt flies: not where the bolt finds him, no E
        let leaving = Foe { vel: (2_500.0, 0.0), ..wall };
        assert_eq!(call(&g, &v, &[leaving], Want::Attack(Some(1))), None);
        // two against walls: the AI's target first, then the lower health
        let wall2 = Foe { id: 3, at: (40_000.0, 520_000.0), hp: 200, ..wall };
        assert!(matches!(call(&g, &v, &[wall2, wall], Want::Attack(Some(1))), Some(Call::Wall(1, ..))));
        assert!(matches!(call(&g, &v, &[wall, wall2], Want::Attack(None)), Some(Call::Wall(3, ..))));
        // a Q or R the AI is on: left alone
        assert_eq!(call(&g, &v, &[wall], Want::Skill), None);
    }

    #[test]
    fn no_wall_e_is_kept_but_for_a_peel_or_a_kill() {
        let g = moba();
        let v = me(480_000.0, 480_000.0);
        let open = foe(2, 480_000.0, 440_000.0);
        // the AI wants E with no wall anywhere: kept, the AI's target attacked
        assert_eq!(call(&g, &v, &[open], Want::E(Some(2))), Some(Call::Hold(2)));
        // and when it does not want E: nothing
        assert_eq!(call(&g, &v, &[open], Want::Attack(Some(2))), None);
        // on her: pushed off when the AI wants E, or on its own when she is low
        let close = foe(4, 480_000.0, 465_000.0);
        assert!(matches!(call(&g, &v, &[open, close], Want::E(Some(2))), Some(Call::Peel(4, _))));
        assert_eq!(call(&g, &v, &[close], Want::Attack(Some(4))), None);
        let low = Me { hp_pct: 25, ..v };
        assert!(matches!(call(&g, &low, &[close], Want::Attack(Some(4))), Some(Call::Peel(4, _))));
        // a bolt that finishes him (60 + 70% of 150 = 165, 30 armour: 126)
        assert_eq!(bolt_damage(150, 30), 126);
        let dying = Foe { hp: 100, ..open };
        assert_eq!(call(&g, &v, &[dying], Want::E(Some(2))), Some(Call::Kill(2, 126, 100)));
    }

    #[test]
    fn the_ai_s_wishes_are_read() {
        assert_eq!(want_of(None), Want::Other);
        assert_eq!(want_of(Some(InputV1::action(InputKindV1::Skill2, InputTargetV1::target(7)))), Want::E(Some(7)));
        assert_eq!(want_of(Some(InputV1::action(InputKindV1::Attack, InputTargetV1::target(7)))), Want::Attack(Some(7)));
        assert_eq!(want_of(Some(InputV1::action(InputKindV1::Ult, InputTargetV1::target(7)))), Want::Skill);
        assert_eq!(want_of(Some(InputV1::move_to(1, 2))), Want::Other);
    }
}
