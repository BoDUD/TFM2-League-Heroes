//! 塞拉斯的连招（用户 2026-10-20：「有连招要做连招」）：AI 钩子 `league_sylas:combo` 替游戏的 AI 按 Q、E、R，像英雄联盟里
//! 会玩的人那样（判断在 `call`，纯计算、单元测试；数字是主包的，被动的 `params` 带过来）。
//!
//! 1. **E → Q**：强掳把他拉到英雄身上（E 放出后 `e_dur` 到 `e_dur` + `AFTER_E` tick 内），Q 好了：替 AI 朝离他最近的敌方英雄
//!    按 Q——锁链交叉在落点，爆炸接在击飞后面。（E → 弑君突刺在主包数据里：落地时突刺好了就马上刺。）
//! 2. **夺来的大招挑时机**：身上有夺来的大招（`r_have`）、R 好了：
//!    - `r_range` 内有一名敌方英雄身边 `r2_r` 内还有另一名敌方英雄（能炸到两个），或者有生命低于 `LOW`% 的敌方英雄：替 AI 朝他按 R；
//!    - AI 自己想放，但只炸得到一个满血的人、夺来的大招也还没快过期：改成普攻那个人，留着大招；
//!    - 快过期（他身上的 `r_have` 剩不到 `LAPSE` tick）就照 AI 的放。
//! 3. **残血优先**：弑君突刺好了（没有 `w_cd`）、AI 想普攻小兵 / 野怪，而 `w_r` 内有生命低于 `LOW`% 的敌方英雄：改成普攻那名英雄
//!    （普攻变成突刺，打完回血）。
//!
//! 被控住、正在放技能（施法动作 `Animation`）或被强制位移时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。

use mod_api_stable::*;

use super::{counted, head, params_of, sn, who, wlog, Params, ID};

/// 排在 league_ult_press（100）之后：引擎按优先级从小到大跑 AI 钩子，每个拿到前一个的决定。
pub const COMBO_PRIORITY: i32 = 110;
/// E 的动作结束后这么多 tick 内还算「刚拉过去」（E → Q）。
pub const AFTER_E: usize = 30;
/// 残血：生命比例低于这个百分比。
pub const LOW: usize = 40;
/// 夺来的大招剩不到这么多 tick 就不挑了。
pub const LAPSE: usize = 90;

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 塞拉斯自己这一 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub r: f64,
    pub hp: f64,
    pub q_ready: bool,
    pub r_ready: bool,
    /// 弑君突刺好了（身上没有 `w_cd`）。
    pub w_ready: bool,
    /// 夺来的大招还剩几 tick（没有是 None）。
    pub stolen: Option<usize>,
    /// E 放出后过了几 tick（E 在冷却时 = 冷却总长 - 剩余；E 好了是 None）。
    pub since_e: Option<usize>,
}

/// 一个敌方单位。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: Pt,
    pub r: f64,
    pub hp: usize,
    pub max: usize,
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
    Q(Option<usize>),
    E(Option<usize>),
    R(Option<usize>),
    Other,
}

/// 替 AI 按的：哪个格子、打谁、为什么（日志的种类和说明）。
#[derive(Clone, Debug, PartialEq)]
pub enum Call {
    PressQ(usize, &'static str, &'static str),
    PressR(usize, &'static str, &'static str),
    Attack(usize, &'static str, &'static str),
}

fn within(me: &Me, u: &Unit, reach: usize) -> bool {
    dist(me.at, u.at) <= reach as f64 + me.r + u.r
}

fn nearest<'a>(me: &Me, foes: &'a [Unit], reach: usize) -> Option<&'a Unit> {
    foes.iter()
        .filter(|u| u.champion && within(me, u, reach))
        .min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at)))
}

/// R 的落点打得到几名敌方英雄（落点 = 那名英雄，`r2_r` 内）。
fn caught(c: &Unit, foes: &[Unit], p: &Params) -> usize {
    foes.iter().filter(|u| u.champion && dist(u.at, c.at) <= p.r2_r as f64 + u.r).count()
}

/// 夺来的大招最值得放给谁：能炸到两名以上的、或残血的；炸到的人多的先，再看生命比例低的。
pub fn best_r(me: &Me, foes: &[Unit], p: &Params) -> Option<Unit> {
    let low = LOW as f64 / 100.0;
    foes.iter()
        .filter(|u| u.champion && within(me, u, p.r_range))
        .map(|u| (caught(u, foes, p), *u))
        .filter(|(n, u)| *n >= 2 || u.share() < low)
        .max_by(|a, b| a.0.cmp(&b.0).then(b.1.share().total_cmp(&a.1.share())))
        .map(|(_, u)| u)
}

pub fn call(me: &Me, foes: &[Unit], p: &Params, want: Want) -> Option<Call> {
    // 1. E -> Q: pulled onto a champion, the chains cross where he landed
    if me.q_ready && me.since_e.is_some_and(|t| t >= p.e_dur && t <= p.e_dur + AFTER_E) {
        if let Some(u) = nearest(me, foes, p.q_range) {
            return Some(Call::PressQ(u.id, "e then q", "E THEN Q: pulled in - the chains cross on him"));
        }
    }
    // 2. the stolen ult: thrown where it catches two champions or a wounded one
    if let Some(left) = me.stolen {
        if me.r_ready {
            if let Some(u) = best_r(me, foes, p) {
                if want != Want::R(Some(u.id)) {
                    return Some(Call::PressR(u.id, "stolen r", "STOLEN R: two champions in the blast or a wounded one"));
                }
                return None;
            }
            if let Want::R(Some(t)) = want {
                if left > LAPSE {
                    return Some(Call::Attack(t, "hold r", "HOLD R: one healthy champion - the stolen ult waits"));
                }
            }
        }
    }
    // 3. Kingslayer on a wounded champion instead of a minion or a monster
    if me.w_ready {
        if let Want::Attack(Some(t)) = want {
            let target = foes.iter().find(|u| u.id == t)?;
            if !target.champion {
                let low = LOW as f64 / 100.0;
                if let Some(u) = foes.iter().filter(|u| u.champion && within(me, u, p.w_r) && u.share() < low)
                    .min_by(|a, b| a.share().total_cmp(&b.share())) {
                    return Some(Call::Attack(u.id, "w on prey", "W ON PREY: Kingslayer on a wounded champion"));
                }
            }
        }
    }
    None
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
        Some(InputKindV1::Skill) => Want::Q(target),
        Some(InputKindV1::Skill2) => Want::E(target),
        Some(InputKindV1::Ult) => Want::R(target),
        _ => Want::Other,
    }
}

/// 这一 tick 的塞拉斯和看得见的敌人；被控住、正在放技能时 None。
fn read(sim: &StableSim<'_>, me: usize) -> Option<(Me, Vec<Unit>)> {
    let e = sim.get_entity(me)?;
    if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
        return None;
    }
    let (have, w_cd) = (sn("r_have"), sn("w_cd"));
    let buffs: Vec<BuffV1> = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect();
    let stolen = buffs.iter().find(|b| b.name() == have).map(|b| {
        if b.duration_kind == BuffDurationV1::Time.code() { b.duration_tick } else { usize::MAX }
    });
    let since_e = e.cooldown(SkillSlotV1::Skill2)
        .filter(|c| c.unlocked && c.remaining > 0)
        .map(|c| c.cooltime.saturating_sub(c.remaining));
    let (hp, max) = e.hp();
    let (x, y) = e.pos();
    let team = e.team();
    let m = Me { at: (x as f64, y as f64), r: e.radius() as f64, hp: if max > 0 { hp as f64 / max as f64 } else { 1.0 },
                 q_ready: ready(&e, SkillSlotV1::Skill), r_ready: ready(&e, SkillSlotV1::Ult),
                 w_ready: !buffs.iter().any(|b| b.name() == w_cd), stolen, since_e };
    let mut foes = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || u.is_tower() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
            continue;
        }
        let (hp, max) = u.hp();
        let (x, y) = u.pos();
        foes.push(Unit { id: u.id(), at: (x as f64, y as f64), r: u.radius() as f64, hp, max, champion: u.is_champion() });
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
        let (call, line, on) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?.id();
            let (m, foes) = read(&sim, me)?;
            let p = params_of(&sim, me);
            let c = call(&m, &foes, &p, want_of(base))?;
            let t = match &c {
                Call::PressQ(t, ..) | Call::PressR(t, ..) | Call::Attack(t, ..) => *t,
            };
            (c, format!("{} [hp {:.0}%]", head(&sim, me), m.hp * 100.0), who(&sim, t))
        };
        let (kind, slot, t, kind_log, why) = match call {
            Call::PressQ(t, k, w) => ("q", InputKindV1::Skill, t, k, w),
            Call::PressR(t, k, w) => ("r", InputKindV1::Ult, t, k, w),
            Call::Attack(t, k, w) => ("attack", InputKindV1::Attack, t, k, w),
        };
        let input = InputV1::action(slot, InputTargetV1::target(t));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(n) = counted(kind_log) {
            wlog(format!("{line} {why} - {kind} on {on} #{n}"));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn me() -> Me {
        Me { at: (0.0, 0.0), r: 3000.0, hp: 1.0, q_ready: true, r_ready: true, w_ready: true, stolen: None, since_e: None }
    }

    fn champ(id: usize, x: f64, y: f64, hp: usize) -> Unit {
        Unit { id, at: (x, y), r: 3000.0, hp, max: 1000, champion: true }
    }

    fn minion(id: usize, x: f64) -> Unit {
        Unit { id, at: (x, 0.0), r: 3000.0, hp: 400, max: 400, champion: false }
    }

    #[test]
    fn q_follows_the_pull() {
        let p = Params::default();
        let foes = [champ(1, 10_000.0, 0.0, 900), minion(5, 5_000.0)];
        let mut pulled = me();
        pulled.since_e = Some(p.e_dur + 2);
        assert!(matches!(call(&pulled, &foes, &p, Want::Attack(Some(5))), Some(Call::PressQ(1, ..))));
        // long after: nothing
        pulled.since_e = Some(p.e_dur + AFTER_E + 1);
        assert_eq!(call(&pulled, &foes, &p, Want::Attack(Some(5))), None);
        // Q cooling: nothing
        let mut cool = me();
        cool.since_e = Some(p.e_dur + 2);
        cool.q_ready = false;
        assert_eq!(call(&cool, &foes, &p, Want::Attack(Some(5))), None);
    }

    #[test]
    fn the_stolen_ult_waits_for_two_or_a_wounded_one() {
        let p = Params::default();
        let mut holding = me();
        holding.stolen = Some(400);
        holding.q_ready = false;
        // two champions together: thrown at them
        let pair = [champ(1, 50_000.0, 0.0, 900), champ(2, 60_000.0, 0.0, 900)];
        assert!(matches!(call(&holding, &pair, &p, Want::Move), Some(Call::PressR(..))));
        // one healthy champion: the AI's own cast becomes an attack
        let one = [champ(1, 20_000.0, 0.0, 900)];
        assert!(matches!(call(&holding, &one, &p, Want::R(Some(1))), Some(Call::Attack(1, ..))));
        assert_eq!(call(&holding, &one, &p, Want::Move), None);
        // about to lapse: the AI's cast goes through
        holding.stolen = Some(LAPSE - 1);
        assert_eq!(call(&holding, &one, &p, Want::R(Some(1))), None);
        // a wounded one: thrown at him
        holding.stolen = Some(400);
        let low = [champ(1, 50_000.0, 0.0, 300)];
        assert!(matches!(call(&holding, &low, &p, Want::Move), Some(Call::PressR(1, ..))));
    }

    #[test]
    fn kingslayer_goes_to_the_wounded() {
        let p = Params::default();
        let mut m = me();
        m.r_ready = false;
        let foes = [minion(5, 10_000.0), champ(1, 20_000.0, 0.0, 300)];
        assert!(matches!(call(&m, &foes, &p, Want::Attack(Some(5))), Some(Call::Attack(1, ..))));
        let healthy = [minion(5, 10_000.0), champ(1, 20_000.0, 0.0, 900)];
        assert_eq!(call(&m, &healthy, &p, Want::Attack(Some(5))), None);
        m.w_ready = false;
        assert_eq!(call(&m, &foes, &p, Want::Attack(Some(5))), None);
    }
}
