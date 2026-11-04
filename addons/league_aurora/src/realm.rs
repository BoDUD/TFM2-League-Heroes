//! 阿萝拉的大招判断（用户 2026-10-24：「阿罗拉大招逻辑怎么和LOL里面高手的不太一样」）：AI 钩子 `league_aurora:realm`。
//! 游戏的 AI 见到射程里有敌方英雄就按 R——满血的坦克、敌方塔下、对面五个人中间都放。英雄联盟里会玩的阿萝拉把「双界合一」
//! 留着做三件事：把一堆人关进领域里开团、关住想跑的残血收掉、被人贴脸时开在他身上（冲击波减速，领域的边界再减，她自己在
//! 领域里绕着边界穿来穿去）。本钩子替 AI 挑时机（判断在 `call`，纯计算、单元测试）。
//!
//! 0.3.0（2026-11-04，英雄联盟 V26.21 的规则：用户「阿罗拉的大招机制逻辑也是不太一样」）：R 不再跳到目标身上——她朝目标跃出
//! `R_LEAP`，冲击波和领域在她落地处前方 `R_AHEAD`（[`centre`]），所以下面「领域里」都按那个中心算：
//!
//! 1. **R PEEL**：`PEEL_R` 内有敌方英雄贴着她、她生命不到 `PEEL_HP`：朝贴得最近的那个按 R（领域罩住他，边界、冲到对面帮她拉开）。
//! 2. **R TRAP**：她生命不低于 `TRAP_HP`；R 射程里的每个敌方英雄，朝他放时领域（`TRAP_R` 内）罩住两个以上敌方英雄，
//!    中心不在敌方塔下，中心 `ALLY_R` 内至少有一个我方英雄，罩住的敌方英雄不比这些我方英雄（含她）多一个以上：按 R，挑罩住
//!    人最多的方向，一样多挑生命比例最低的目标。
//! 3. **R KILL**：她生命不低于 `KILL_SELF_HP`；R 射程里生命比例不到 `KILL_HP` 的敌方英雄，身边 `CROWD_R` 内的敌方英雄不超过
//!    两个，领域中心不在敌方塔下（生命不到 `DIVE_HP` 的除外）：按 R，挑生命比例最低的。
//! 4. **R HELD**：AI 自己想按 R，以上都不成立：不放（改成普攻它的目标，打不到就走过去）。
//!
//! 第 1–3 条在 AI 没想按 R 时也按（游戏的 AI 不一定在好时机按）。回城时、被控住或正在放技能时不管。
//!
//! 领域开着时（被动在她身上挂的 `league_aurora_rift:<x>,<y>`，`rift.rs`）照英雄联盟里的打法走（[`steer`]）：
//!
//! - **RIFT KITE**：`KITE_R` 内有敌方英雄（生命不到 `SPARE_HP` 的除外：留着收掉）、她的普攻没好或者 AI 不是要打射程里的英雄：
//!   往边界走（[`exit_point`]：沿半径最近的那一点，那人挡在路上就背着他走），碰到边界就冲到对面，把领域的直径隔在两人之间。
//! - **RIFT STAY**：没人贴身，AI 要走到领域外（走过去、或走去打射程外的人会走出去）：只走到边界里 `STAY_IN` 停下——碰到边界
//!   会被送到对面，追着外面的人会来回穿。
//!
//! 冲到对面的那 `r_wrap_t` tick 不管（她身上有 `league_aurora_r_wrap`）。

use mod_api_stable::*;

use super::rift::{self, EDGE};
use super::{counted, dist, head, on_screen, wlog, ID};

/// 排在 league_ult_press（100）之后。
pub const PRIORITY: i32 = 110;
/// 一串连着按的只记一行（league_heimerdinger 的 `ORDER_FRESH`）：引擎接下 R 之前钩子每 tick 再按一次，AI 每次思考也再想按一次 R，
/// 同一种决定离上一次不到这么多 tick 就算同一串（0.2.1：2026-11-03 夜里的日志一次 R KILL 记了 14 行，R HELD 100 tick 26 行）。
pub const ORDER_FRESH: usize = 30;

/// A press at `tick` starts a burst: none of its kind in the `ORDER_FRESH` ticks before (`last`: that kind's last press;
/// a tick before it is another match).
pub fn new_burst(last: Option<usize>, tick: usize) -> bool {
    last.is_none_or(|t0| tick < t0 || tick > t0 + ORDER_FRESH)
}
/// 贴脸：这么近的敌方英雄。
pub const PEEL_R: f64 = 22_000.0;
/// 自保：她的生命比例不到这个。
pub const PEEL_HP: f64 = 0.5;
/// 开团：她的生命比例不低于这个。
pub const TRAP_HP: f64 = 0.4;
/// 我方英雄算在场：离领域中心这么近。
pub const ALLY_R: f64 = 60_000.0;
/// 收人头：目标的生命比例不到这个。
pub const KILL_HP: f64 = 0.4;
/// 收人头：她的生命比例不低于这个。
pub const KILL_SELF_HP: f64 = 0.3;
/// 收人头时目标身边多少范围内的敌方英雄算一堆（超过两个不去）。
pub const CROWD_R: f64 = 30_000.0;
/// 敌方塔下也去收：目标的生命比例不到这个。
pub const DIVE_HP: f64 = 0.2;
/// 敌方塔的攻击范围（大约）。
pub const TOWER_REACH: f64 = 75_000.0;
/// 主包数据：R 的射程、领域的半径、跃出多远、冲击波（领域）的中心在落地处前方多远（build_aurora.P，单元测试核对）。
pub const R_RANGE: f64 = 60_000.0;
pub const R_ZONE: f64 = 38_000.0;
pub const R_LEAP: f64 = 15_000.0;
pub const R_AHEAD: f64 = 25_500.0;
/// 关在领域里：离中心这么近（那一圈加半个身体）。
pub const TRAP_R: f64 = 43_000.0;
/// 两个单位的身体（射程算到身体边上，大约）。
pub const BODIES: f64 = 12_000.0;
/// 她的普攻够得着（主包 atk_range + 两个身体）。
pub const ATK_REACH: f64 = 55_000.0 + BODIES;
/// 领域里贴身的敌方英雄：这么近（近战够得着她）。
pub const KITE_R: f64 = 45_000.0;
/// 贴身的人生命比例不到这个：不跑，收掉他。
pub const SPARE_HP: f64 = 0.25;
/// 不出领域：走到边界里这么远停下。
pub const STAY_IN: f64 = 6_000.0;
/// 放风筝：走到边界外这么远的点（一定碰得到边界）。
pub const PAST: f64 = 4_000.0;

pub type Pt = (f64, f64);

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub hp: f64,
    pub r_ready: bool,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: Pt,
    pub hp: f64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Call {
    /// (target, kind for the log)
    R(usize, &'static str),
    /// the AI's R held: attack / walk to its target
    Hold(Option<usize>),
}

fn near(at: Pt, units: &[Unit], within: f64) -> usize {
    units.iter().filter(|u| dist(at, u.at) <= within).count()
}

fn towered(at: Pt, towers: &[Pt]) -> bool {
    towers.iter().any(|&w| dist(w, at) <= TOWER_REACH)
}

fn unit(from: Pt, to: Pt) -> Option<Pt> {
    let d = dist(from, to);
    (d >= 1.0).then(|| ((to.0 - from.0) / d, (to.1 - from.1) / d))
}

/// Where the rift opens when she casts R at a champion at `t` from `me`: she leaps `R_LEAP` toward it (through it when it
/// is nearer), and the shockwave goes off `R_AHEAD` toward it from where she lands (the data's `Forward` offset).
pub fn centre(me: Pt, t: Pt) -> Pt {
    let Some(u) = unit(me, t) else { return me };
    let land = (me.0 + u.0 * R_LEAP, me.1 + u.1 * R_LEAP);
    let ahead = if dist(me, t) > R_LEAP { R_AHEAD } else { -R_AHEAD };
    (land.0 + u.0 * ahead, land.1 + u.1 * ahead)
}

/// What to press (None: leave the AI's input).
pub fn call(me: &Me, foes: &[Unit], allies: &[Unit], towers: &[Pt], ai_wants_r: Option<Option<usize>>) -> Option<Call> {
    if me.r_ready {
        // 1. someone on her and she is hurt: the rift over him (its border and her crossings keep him off her)
        let close = foes.iter().filter(|u| dist(me.at, u.at) <= PEEL_R).min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at)));
        if let (Some(t), true) = (close, me.hp < PEEL_HP) {
            return Some(Call::R(t.id, "peel"));
        }
        let reach: Vec<&Unit> = foes.iter().filter(|u| dist(me.at, u.at) <= R_RANGE + BODIES).collect();
        // 2. two or more in the rift where it opens, a friend there, not more of them than of us (+1), not under their tower
        if me.hp >= TRAP_HP {
            let t = reach
                .iter()
                .map(|u| {
                    let c = centre(me.at, u.at);
                    (*u, c, near(c, foes, TRAP_R))
                })
                .filter(|&(_, c, n)| {
                    let ours = 1 + near(c, allies, ALLY_R);
                    n >= 2 && ours >= 2 && n <= ours + 1 && !towered(c, towers)
                })
                .max_by(|a, b| a.2.cmp(&b.2).then(b.0.hp.total_cmp(&a.0.hp)));
            if let Some((t, _, _)) = t {
                return Some(Call::R(t.id, "trap"));
            }
        }
        // 3. a low one in reach, not deep in his team
        if me.hp >= KILL_SELF_HP {
            let t = reach
                .iter()
                .filter(|u| {
                    u.hp < KILL_HP && near(u.at, foes, CROWD_R) <= 2 && (u.hp < DIVE_HP || !towered(centre(me.at, u.at), towers))
                })
                .min_by(|a, b| a.hp.total_cmp(&b.hp));
            if let Some(t) = t {
                return Some(Call::R(t.id, "kill"));
            }
        }
    }
    // 4. the AI's own R, none of the above: hold it
    ai_wants_r.map(Call::Hold)
}

// ===================== 领域开着时怎么走 =====================

/// What the game's AI wants while the rift is open.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Want {
    /// walk there
    Move(Pt),
    /// attack the unit there (walking up to it when it is out of reach); is it a champion
    Attack(Pt, bool),
    /// a skill, the ult, recall: left alone
    Cast,
    /// no new input this think
    Idle,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Steer {
    /// to the border away from this champion (it carries her across)
    Kite(Pt, usize),
    /// the AI's walk held inside the rift
    Stay(Pt),
}

/// `p` pulled in to `r` from `c`.
fn clamp(c: Pt, p: Pt, r: f64) -> Pt {
    let d = dist(c, p);
    if d <= r {
        p
    } else {
        (c.0 + (p.0 - c.0) / d * r, c.1 + (p.1 - c.1) / d * r)
    }
}

/// The point past the border she walks to when `t` is on her: straight out along the radius (the nearest border, and the
/// crossing puts the whole rift between them), or straight away from him when he stands in that way or she is at the
/// centre.
pub fn exit_point(me: Pt, c: Pt, t: Pt) -> Pt {
    let r = EDGE + PAST;
    if dist(me, c) >= 6_000.0 {
        if let Some(u) = unit(c, me) {
            let b = (c.0 + u.0 * r, c.1 + u.1 * r);
            if dist(t, b) >= dist(me, b) {
                return b;
            }
        }
    }
    let v = unit(t, me).unwrap_or((1.0, 0.0));
    let w = (me.0 - c.0, me.1 - c.1);
    let wv = w.0 * v.0 + w.1 * v.1;
    let s = -wv + (wv * wv - (w.0 * w.0 + w.1 * w.1 - r * r)).max(0.0).sqrt();
    (me.0 + v.0 * s, me.1 + v.1 * s)
}

/// Inside the rift (centre `c`): kite to the border when a champion is on her, keep the AI's walks inside (None: leave it).
pub fn steer(me: Pt, c: Pt, foes: &[Unit], want: Want, attack_ready: bool) -> Option<Steer> {
    if want == Want::Cast {
        return None;
    }
    let threat = foes.iter().filter(|u| u.hp >= SPARE_HP && dist(me, u.at) <= KITE_R)
        .min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at)));
    if let Some(t) = threat {
        // her attack ready for a champion in reach: shoot first (League's kiting: attack, then step)
        let shooting = attack_ready && matches!(want, Want::Attack(at, true) if dist(me, at) <= ATK_REACH);
        return (!shooting).then(|| Steer::Kite(exit_point(me, c, t.at), t.id));
    }
    let inner = EDGE - STAY_IN;
    match want {
        Want::Move(p) if dist(c, p) > inner => Some(Steer::Stay(clamp(c, p, inner))),
        Want::Attack(at, _) => {
            let d = dist(me, at);
            if d <= ATK_REACH {
                return None;
            }
            let stop = (at.0 - (at.0 - me.0) / d * ATK_REACH, at.1 - (at.1 - me.1) / d * ATK_REACH);
            (dist(c, stop) > inner).then(|| Steer::Stay(clamp(c, stop, inner)))
        }
        _ => None,
    }
}

// ===================== 游戏里 =====================

const STOP: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                             CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

fn ready(e: &StableEntity<'_, '_>, slot: SkillSlotV1) -> bool {
    e.cooldown(slot).is_some_and(|c| c.unlocked && (c.remaining == 0 || c.charges > 0))
}

fn share(hp: (usize, usize)) -> f64 {
    if hp.1 == 0 { 0.0 } else { hp.0 as f64 / hp.1 as f64 }
}

fn pt(e: &StableEntity<'_, '_>) -> Pt {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

fn on_map(p: Pt) -> (u64, u64) {
    (p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

#[derive(Clone, Default)]
pub struct Realm {
    recalling: bool,
    /// the last press of each kind (peel, trap, kill, held, kite, stay): one line a burst
    pressed: [Option<usize>; 6],
}

/// The `pressed` slot of a kind of call.
fn slot(kind: &str) -> usize {
    match kind {
        "peel" => 0,
        "trap" => 1,
        "kill" => 2,
        "kite" => 4,
        "stay" => 5,
        _ => 3,
    }
}

impl Realm {
    /// A press of `kind` at `tick`: the first of its burst (it gets a line); noted for the next.
    fn fresh(&mut self, kind: &str, tick: usize) -> bool {
        let last = &mut self.pressed[slot(kind)];
        let first = new_burst(*last, tick);
        *last = Some(tick);
        first
    }
}

/// What think() decided while the sim was borrowed.
enum Plan {
    Steer(Steer, String, bool),
    Press(Call, String, (Option<(u64, u64)>, (u64, u64)), bool),
}

impl StablePlayerAi for Realm {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:realm")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        self.recalling = match base {
            Some(b) => b.kind == InputKindV1::Return.code(),
            None => self.recalling,
        };
        if self.recalling {
            return None;
        }
        let player = ctx.player_id();
        let plan = {
            let sim = ctx.sim()?;
            let e = sim.get_player(player)?.champion()?;
            if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
                return None;
            }
            let buffs: Vec<BuffV1> = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect();
            // crossing the rift: nothing to steer
            if buffs.iter().any(|b| b.name() == rift::WRAP) {
                return None;
            }
            let rift_at = buffs.iter().find_map(|b| rift::parse_at(b.name(), rift::AT));
            let (id, team) = (e.id(), e.team());
            let me = Me { at: pt(&e), hp: share(e.hp()), r_ready: ready(&e, SkillSlotV1::Ult) };
            let (mut foes, mut allies, mut towers) = (Vec::new(), Vec::new(), Vec::new());
            for i in 0..sim.entity_count() {
                let Some(u) = sim.entity_at(i) else { continue };
                if !u.is_alive() || u.id() == id {
                    continue;
                }
                if u.is_tower() {
                    if u.team() != team {
                        towers.push(pt(&u));
                    }
                    continue;
                }
                if !u.is_champion() {
                    continue;
                }
                let unit = Unit { id: u.id(), at: pt(&u), hp: share(u.hp()) };
                if u.team() == team {
                    allies.push(unit);
                } else if u.is_targetable() {
                    foes.push(unit);
                }
            }
            let shown = on_screen(&sim);
            let kind = base.and_then(|b| InputKindV1::from_code(b.kind));
            let steered = rift_at.and_then(|c| {
                let want = match (kind, base) {
                    (Some(InputKindV1::Move), Some(b)) => Want::Move((b.x as f64, b.y as f64)),
                    (Some(InputKindV1::Attack), Some(b)) => sim.get_entity(b.target.target_id)
                        .map_or(Want::Cast, |t| Want::Attack(pt(&t), t.is_champion())),
                    (None, _) => Want::Idle,
                    _ => Want::Cast,
                };
                steer(me.at, c, &foes, want, ready(&e, SkillSlotV1::Attack)).map(|s| {
                    let why = match (s, want) {
                        (Steer::Kite(to, t), _) => {
                            let d = foes.iter().find(|u| u.id == t).map_or(0.0, |u| dist(me.at, u.at));
                            format!("RIFT KITE: #{t} on her ({d:.0} away), to the border at ({:.0}, {:.0}) - across from there", to.0, to.1)
                        }
                        (Steer::Stay(to), Want::Move(p)) => format!(
                            "RIFT STAY: the AI's walk to ({:.0}, {:.0}) leaves the rift, held at ({:.0}, {:.0})", p.0, p.1, to.0, to.1),
                        (Steer::Stay(to), _) => format!(
                            "RIFT STAY: the AI's walk to its target out of reach leaves the rift, held at ({:.0}, {:.0})", to.0, to.1),
                    };
                    (s, format!("{} [hp {:.0}%] rift at ({:.0}, {:.0}), {:.0} from it: {why}", head(&sim, id), me.hp * 100.0,
                                c.0, c.1, dist(me.at, c)))
                })
            });
            match steered {
                Some((s, line)) => Plan::Steer(s, line, shown),
                None => {
                    let wants = base.filter(|b| b.kind == InputKindV1::Ult.code()).map(|b| {
                        (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
                    });
                    let c = call(&me, &foes, &allies, &towers, wants)?;
                    let on = match c {
                        Call::R(t, _) | Call::Hold(Some(t)) => Some(t),
                        Call::Hold(None) => None,
                    };
                    let target = on.and_then(|t| foes.iter().find(|u| u.id == t));
                    let spot = target.map(|u| on_map(u.at));
                    let opens = target.map(|u| centre(me.at, u.at));
                    let crowd = opens.map_or(0, |c| near(c, &foes, TRAP_R));
                    let at = opens.map_or("-".to_string(), |c| format!("({:.0}, {:.0})", c.0, c.1));
                    Plan::Press(c, format!("{} [hp {:.0}%] on #{} ({crowd} in the rift at {at}, hp {:.0}%)", head(&sim, id),
                                           me.hp * 100.0, on.map_or("-".to_string(), |t| t.to_string()),
                                           target.map_or(0.0, |u| u.hp * 100.0)),
                                (spot, on_map(me.at)), shown)
                }
            }
        };
        let (c, line, spot, shown) = match plan {
            Plan::Steer(s, line, shown) => {
                let (kind, to) = match s {
                    Steer::Kite(to, _) => ("kite", to),
                    Steer::Stay(to) => ("stay", to),
                };
                let (x, y) = on_map(to);
                let input = InputV1::move_to(x, y);
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                if self.fresh(kind, ctx.tick()) {
                    if let Some(n) = counted(if kind == "kite" { "rift kite" } else { "rift stay" }, shown) {
                        wlog(format!("{line} #{n}"));
                    }
                }
                return Some(input);
            }
            Plan::Press(c, line, spot, shown) => (c, line, spot, shown),
        };
        let (input, kind, why) = match c {
            Call::R(t, k) => (InputV1::action(InputKindV1::Ult, InputTargetV1::target(t)), k, match k {
                "peel" => "R PEEL: the rift over the diver",
                "trap" => "R TRAP: the rift over a crowd",
                _ => "R KILL: the low one trapped",
            }),
            Call::Hold(t) => {
                let attack = t.map(|t| InputV1::action(InputKindV1::Attack, InputTargetV1::target(t)));
                let input = match attack.filter(|a| ctx.is_valid_input(a)) {
                    Some(a) => a,
                    None => {
                        let (x, y) = spot.0.unwrap_or(spot.1);
                        InputV1::move_to(x, y)
                    }
                };
                if self.fresh("held", ctx.tick()) {
                    if let Some(n) = counted("r held", shown) {
                        wlog(format!("{line} R HELD: no crowd, no kill, no peel - the AI's R kept #{n}"));
                    }
                }
                return Some(input);
            }
        };
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if self.fresh(kind, ctx.tick()) {
            if let Some(n) = counted(kind, shown) {
                wlog(format!("{line} {why} #{n}"));
            }
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn me(hp: f64) -> Me {
        Me { at: (0.0, 0.0), hp, r_ready: true }
    }

    fn u(id: usize, x: f64, hp: f64) -> Unit {
        Unit { id, at: (x, 0.0), hp }
    }

    fn close(a: Pt, b: Pt) -> bool {
        dist(a, b) < 1.0
    }

    #[test]
    fn the_rift_opens_ahead_of_where_she_lands() {
        // a champion 60000 away: the leap 15000, the centre 25500 further
        assert!(close(centre((0.0, 0.0), (60_000.0, 0.0)), (40_500.0, 0.0)));
        assert!(close(centre((0.0, 0.0), (0.0, -30_000.0)), (0.0, -40_500.0)));
        // nearer than the leap: she leaps through him and the shockwave faces him, behind her
        assert!(close(centre((0.0, 0.0), (10_000.0, 0.0)), (15_000.0 - 25_500.0, 0.0)));
        // every champion in reach is in the rift opened toward him
        for d in [16_000.0, 30_000.0, 50_000.0, R_RANGE + BODIES] {
            assert!(dist(centre((0.0, 0.0), (d, 0.0)), (d, 0.0)) <= TRAP_R, "{d}");
        }
        // she is in it: the passive does not close it at once
        assert!(dist(centre((0.0, 0.0), (60_000.0, 0.0)), (R_LEAP, 0.0)) < EDGE);
    }

    #[test]
    fn a_diver_on_a_hurt_aurora_is_slammed() {
        assert_eq!(call(&me(0.4), &[u(1, 15_000.0, 1.0)], &[], &[], None), Some(Call::R(1, "peel")));
        // healthy, one full champion in front of her: the AI's R is held
        assert_eq!(call(&me(0.9), &[u(1, 15_000.0, 1.0)], &[], &[], Some(Some(1))), Some(Call::Hold(Some(1))));
        assert_eq!(call(&me(0.9), &[u(1, 40_000.0, 1.0)], &[], &[], None), None);
    }

    #[test]
    fn the_rift_goes_over_the_biggest_crowd() {
        let allies = [Unit { id: 10, at: (20_000.0, 0.0), hp: 1.0 }];
        // #1 alone to the east; #2 to the south with #3 behind him: toward #2 the rift holds both
        let foes = [u(1, 50_000.0, 1.0), Unit { id: 2, at: (0.0, 60_000.0), hp: 0.9 }, Unit { id: 3, at: (0.0, 75_000.0), hp: 1.0 },
                    u(4, 300_000.0, 1.0)];
        assert_eq!(call(&me(0.9), &foes, &allies, &[], None), Some(Call::R(2, "trap")));
        // two in a row to the east: the one with less health is the target (the same rift)
        let row = [u(1, 50_000.0, 1.0), u(2, 60_000.0, 0.7), u(3, 90_000.0, 1.0)];
        assert_eq!(call(&me(0.9), &row, &allies, &[], None), Some(Call::R(2, "trap")));
        // no friend of hers there: no engage
        assert_eq!(call(&me(0.9), &row, &[], &[], None), None);
        // the rift under their tower: no
        assert_eq!(call(&me(0.9), &row, &allies, &[(60_000.0, 0.0)], None), None);
        // she is low: no engage
        assert_eq!(call(&me(0.35), &row, &allies, &[], None), None);
    }

    #[test]
    fn a_low_one_is_trapped_unless_he_is_deep_in_his_team() {
        assert_eq!(call(&me(0.9), &[u(1, 50_000.0, 0.3)], &[], &[], None), Some(Call::R(1, "kill")));
        let deep = [u(1, 50_000.0, 0.3), u(2, 60_000.0, 1.0), u(3, 65_000.0, 1.0)];
        assert_eq!(call(&me(0.9), &deep, &[], &[], Some(Some(1))), Some(Call::Hold(Some(1))));
        // under the tower only when nearly dead
        let tower = [(60_000.0, 0.0)];
        assert_eq!(call(&me(0.9), &[u(1, 50_000.0, 0.3)], &[], &tower, None), None);
        assert_eq!(call(&me(0.9), &[u(1, 50_000.0, 0.15)], &[], &tower, None), Some(Call::R(1, "kill")));
        // out of reach
        assert_eq!(call(&me(0.9), &[u(1, 90_000.0, 0.1)], &[], &[], None), None);
    }

    #[test]
    fn nothing_without_the_ult() {
        let m = Me { r_ready: false, ..me(0.3) };
        assert_eq!(call(&m, &[u(1, 10_000.0, 0.1)], &[], &[], None), None);
    }

    #[test]
    fn a_champion_on_her_in_the_rift_sends_her_to_the_border() {
        let c = (0.0, 0.0);
        // she stands 25500 west of the centre, a fighter on her from the east: straight out west, past the edge
        let at = (-25_500.0, 0.0);
        let on_her = [u(7, -5_000.0, 1.0)];
        let Some(Steer::Kite(to, 7)) = steer(at, c, &on_her, Want::Attack((-5_000.0, 0.0), true), false) else { panic!() };
        assert!(close(to, (-(EDGE + PAST), 0.0)), "{to:?}");
        // her attack ready for him: she shoots first; for a minion: she steps off instead
        assert_eq!(steer(at, c, &on_her, Want::Attack((-5_000.0, 0.0), true), true), None);
        assert!(matches!(steer(at, c, &on_her, Want::Attack((-30_000.0, 9_000.0), false), true), Some(Steer::Kite(..))));
        // with no new input the step to the border still comes
        assert!(matches!(steer(at, c, &on_her, Want::Idle, true), Some(Steer::Kite(..))));
        // a skill is never cut
        assert_eq!(steer(at, c, &on_her, Want::Cast, false), None);
        // nearly dead: no running, finish him
        assert_eq!(steer(at, c, &[u(7, -5_000.0, 0.2)], Want::Attack((-5_000.0, 0.0), true), false), None);
        // he stands between her and that border: away from him instead
        let blocking = [u(8, -45_000.0, 1.0)];
        let Some(Steer::Kite(to, 8)) = steer((-20_000.0, 0.0), c, &blocking, Want::Idle, false) else { panic!() };
        assert!(to.0 > -20_000.0 && (dist(c, to) - (EDGE + PAST)).abs() < 1.0, "{to:?}");
        // at the centre: away from him
        let to = exit_point(c, c, (-10_000.0, 0.0));
        assert!(close(to, (EDGE + PAST, 0.0)), "{to:?}");
    }

    #[test]
    fn the_ai_does_not_walk_out_of_the_rift() {
        let c = (0.0, 0.0);
        let at = (-10_000.0, 0.0);
        // a walk far east is held inside, on its way
        let Some(Steer::Stay(to)) = steer(at, c, &[], Want::Move((200_000.0, 0.0)), true) else { panic!() };
        assert!(close(to, (EDGE - STAY_IN, 0.0)), "{to:?}");
        // a walk inside is left alone
        assert_eq!(steer(at, c, &[], Want::Move((20_000.0, 5_000.0)), true), None);
        // attacking one in reach: left alone; one far outside: walk only to the edge's inside toward him
        assert_eq!(steer(at, c, &[], Want::Attack((50_000.0, 0.0), true), true), None);
        let Some(Steer::Stay(to)) = steer(at, c, &[], Want::Attack((150_000.0, 0.0), false), true) else { panic!() };
        assert!(close(to, (EDGE - STAY_IN, 0.0)), "{to:?}");
        // one out of reach whose stop point is still inside the rift: the engine's own walk
        assert_eq!(steer((-30_000.0, 0.0), c, &[], Want::Attack((60_000.0, 0.0), true), true), None);
        assert_eq!(steer(at, c, &[], Want::Idle, true), None);
    }

    #[test]
    fn one_line_a_burst_of_presses() {
        let mut r = Realm::default();
        // R KILL pressed every tick until the engine takes it (11-03 night logs: 57921..57929, one line now)
        let kills: Vec<bool> = (57_921..=57_929).map(|t| r.fresh("kill", t)).collect();
        assert_eq!(kills.iter().filter(|&&f| f).count(), 1);
        // R HELD at every AI think (4 ticks) for 100 ticks: one line; a later hold is a new burst
        assert_eq!((9_309..9_409).step_by(4).filter(|&t| r.fresh("held", t)).count(), 1);
        assert!(r.fresh("held", 11_741));
        // kinds apart: a peel right after a kill burst still gets its line, kite and stay their own
        assert!(r.fresh("peel", 57_930));
        assert!(r.fresh("kite", 57_931) && r.fresh("stay", 57_931) && !r.fresh("kite", 57_935));
        assert!(new_burst(Some(57_929), 100), "another match");
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let src = include_str!("../../../tools/kit/build_aurora.py");
        for (key, v) in [("r_range", R_RANGE), ("r_zone", R_ZONE), ("r_leap", R_LEAP), ("r_ahead", R_AHEAD), ("atk_range", ATK_REACH - BODIES)] {
            assert!(src.contains(&format!("\"{key}\": {}", v as usize)), "{key} {v}");
        }
        assert_eq!(R_ZONE, rift::RING);
    }
}
