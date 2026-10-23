//! 升级给谁（用户 2026-10-24：「大发明家的手雷不能升级？炮台不能升级么？」，选了「改成升级下一个技能」）：主包的 R 不再直接
//! 放东西，刷新 Q、E 的冷却并给他挂 `upg`（`r_keep` tick），先来的、够得着敌方英雄的 Q（巨型炮台）、E（CH-3X 三颗手雷）或
//! 普攻（导弹群）升级。
//! AI 钩子 `league_heimerdinger:combo` 替游戏的 AI 挑（判断在 `call`，纯计算、单元测试；数字是主包的，被动的 `params` 带过来）：
//!
//! 1. **E CLUMP**：升级挂着、E 好了、`e_range` 内有一名敌方英雄身边 `re_r` 内还有别的敌方英雄：朝身边人最多的那名按 E。
//! 2. **Q APEX**：升级挂着、Q 好了、`q_range` 内有敌方英雄：朝最近的那名按 Q。
//! 3. **E ONE**：升级挂着、Q 没好、E 好了、`e_range` 内有敌方英雄：朝最近的那名按 E。
//!    都不行就让 AI 接着打（普攻打到身边有英雄时射出导弹群）。
//!
//! 被控住、正在放技能（施法动作 `Animation`）或被强制位移、AI 在回城时什么都不做；格子的冷却自己看（引擎的「输入合法」不看冷却）。

use std::sync::atomic::{AtomicUsize, Ordering};

use mod_api_stable::*;

use super::{hd, head, params_of, wlog, Params, ID};

/// 排在 league_ult_press（100）之后：引擎按优先级从小到大跑 AI 钩子，每个拿到前一个的决定。
pub const COMBO_PRIORITY: i32 = 110;
/// 每种决定最多记多少行（presim 和画面里那场一起算）。
const LOG_LINES: usize = 40;
static LOGGED: [AtomicUsize; 3] = [const { AtomicUsize::new(0) }; 3];

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 黑默丁格自己这一 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub r: f64,
    pub q_ready: bool,
    pub e_ready: bool,
    /// R 的升级挂着（`upg`）。
    pub upgraded: bool,
}

/// 一名看得见的敌方英雄。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub r: f64,
}

/// 为什么替 AI 按（日志的种类，`LOGGED` 的下标）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Why {
    Clump,
    Apex,
    One,
}

impl Why {
    fn line(self) -> &'static str {
        match self {
            Why::Clump => "E CLUMP: CH-3X at the champions standing together",
            Why::Apex => "Q APEX: the apex turret toward the nearest champion",
            Why::One => "E ONE: Q cooling, CH-3X at the nearest champion",
        }
    }
}

/// 替 AI 按的：Q 朝谁、E 打谁。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Call {
    Q(usize, Why),
    E(usize, Why),
}

fn within(me: &Me, f: &Foe, reach: usize) -> bool {
    dist(me.at, f.at) <= reach as f64 + me.r + f.r
}

/// `f` 和他身边 `re_r` 内的敌方英雄一共几名（CH-3X 一颗砸中几个）。
pub fn crowd(foes: &[Foe], f: &Foe, re_r: usize) -> usize {
    foes.iter().filter(|g| dist(g.at, f.at) <= re_r as f64 + g.r).count()
}

fn nearest<'a>(me: &Me, foes: &'a [Foe], reach: usize) -> Option<&'a Foe> {
    foes.iter().filter(|f| within(me, f, reach)).min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at)))
}

pub fn call(me: &Me, foes: &[Foe], p: &Params) -> Option<Call> {
    if !me.upgraded {
        return None;
    }
    {
        // 1. the most champions round one within E's reach (the nearer of equals)
        if me.e_ready {
            let best = foes.iter().filter(|f| within(me, f, p.e_range)).map(|f| (crowd(foes, f, p.re_r), f)).min_by(
                |(na, a), (nb, b)| nb.cmp(na).then(dist(me.at, a.at).total_cmp(&dist(me.at, b.at))));
            if let Some((n, f)) = best {
                if n >= 2 {
                    return Some(Call::E(f.id, Why::Clump));
                }
            }
        }
        if me.q_ready {
            if let Some(f) = nearest(me, foes, p.q_range) {
                return Some(Call::Q(f.id, Why::Apex));
            }
        }
        if me.e_ready {
            if let Some(f) = nearest(me, foes, p.e_range) {
                return Some(Call::E(f.id, Why::One));
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

/// 这一 tick 的他和看得见的敌方英雄；被控住、正在放技能时 None。
fn read(sim: &StableSim<'_>, me: usize) -> Option<(Me, Vec<Foe>)> {
    let e = sim.get_entity(me)?;
    if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
        return None;
    }
    let upg = hd("upg");
    let (x, y) = e.pos();
    let team = e.team();
    let m = Me { at: (x as f64, y as f64), r: e.radius() as f64, q_ready: ready(&e, SkillSlotV1::Skill),
                 e_ready: ready(&e, SkillSlotV1::Skill2),
                 upgraded: (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == upg) };
    let mut foes = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_champion() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
            continue;
        }
        let (x, y) = u.pos();
        foes.push(Foe { id: u.id(), at: (x as f64, y as f64), r: u.radius() as f64 });
    }
    Some((m, foes))
}

/// The AI is still recalling (game 0.6.5 decides when to go home and buy; the combos leave it be): its last order was a
/// Return - it orders only on its judgement ticks, again a Return while the recall lasts, nothing in between - and any
/// other order ends it (league_ult_press 0.5.0's rule).
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

#[derive(Clone, Default)]
pub struct Combo {
    /// the AI is recalling (`still_recalling`)
    recalling: bool,
}

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
        self.recalling = still_recalling(self.recalling, base);
        if self.recalling {
            return None;
        }
        let player = ctx.player_id();
        let (c, line, at, foe_at) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?.id();
            let (m, foes) = read(&sim, me)?;
            let c = call(&m, &foes, &params_of(&sim, me))?;
            let (Call::Q(t, _) | Call::E(t, _)) = c;
            let foe_at = foes.iter().find(|f| f.id == t)?.at;
            (c, format!("{} on #{t}", head(&sim, me)), m.at, foe_at)
        };
        let (input, why) = match c {
            // Q is a Direction cast: the game's AI gives it a direction (the add-on's `:q` / `:x` read it too)
            Call::Q(_, why) => (InputV1::action(InputKindV1::Skill,
                                                InputTargetV1::dir((foe_at.0 - at.0) as i64, (foe_at.1 - at.1) as i64)), why),
            Call::E(t, why) => (InputV1::action(InputKindV1::Skill2, InputTargetV1::target(t)), why),
        };
        if !ctx.is_valid_input(&input) {
            return None;
        }
        let n = LOGGED[why as usize].fetch_add(1, Ordering::Relaxed) + 1;
        if n <= LOG_LINES || n % 100 == 0 {
            wlog(format!("{line} {} #{n}", why.line()));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn me(upgraded: bool) -> Me {
        Me { at: (0.0, 0.0), r: 3000.0, q_ready: true, e_ready: true, upgraded }
    }

    fn foe(id: usize, x: f64, y: f64) -> Foe {
        Foe { id, at: (x, y), r: 3000.0 }
    }

    #[test]
    fn a_recall_is_the_ais() {
        assert!(still_recalling(false, Some(InputV1::return_home())) && still_recalling(true, None));
        assert!(!still_recalling(true, Some(InputV1::move_to(0, 0))) && !still_recalling(false, None));
    }

    #[test]
    fn the_grenade_goes_at_a_clump_else_the_turret() {
        let p = Params::default();
        // two champions 10000 apart and a third alone: E at the pair (the nearer one of it)
        let clump = [foe(1, 40_000.0, 0.0), foe(2, 50_000.0, 0.0), foe(3, 0.0, 30_000.0)];
        assert_eq!(call(&me(true), &clump, &p), Some(Call::E(1, Why::Clump)));
        // apart: the apex turret toward the nearest
        let apart = [foe(1, 40_000.0, 0.0), foe(3, 0.0, 30_000.0)];
        assert_eq!(call(&me(true), &apart, &p), Some(Call::Q(3, Why::Apex)));
        // Q cooling: CH-3X at the nearest
        let mut no_q = me(true);
        no_q.q_ready = false;
        assert_eq!(call(&no_q, &apart, &p), Some(Call::E(3, Why::One)));
        // E cooling at a clump: the turret
        let mut no_e = me(true);
        no_e.e_ready = false;
        assert_eq!(call(&no_e, &clump, &p), Some(Call::Q(3, Why::Apex)));
        // nobody in reach, or no upgrade: the AI goes on
        assert_eq!(call(&me(true), &[foe(1, 300_000.0, 0.0)], &p), None);
        assert_eq!(call(&me(false), &clump, &p), None);
    }

    #[test]
    fn the_flag_fits() {
        assert!(hd("upg").len() <= BUFF_NAME_CAP);
    }
}
