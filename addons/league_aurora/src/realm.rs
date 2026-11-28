//! 阿萝拉的大招判断：AI 钩子 `league_aurora:realm`。
//!
//! 用户三次提到大招：10-24「阿罗拉大招逻辑怎么和LOL里面高手的不太一样」（加了本钩子），11-04「阿罗拉的大招机制逻辑也是不太
//! 一样」（0.3.0 照 V26.21 改成跃出一小段、前方冲击波、领域边界），11-26「阿罗拉这个大招释放的没有英雄联盟高手的感觉」。
//! 11-26 看了她的日志：领域关了 65 次，62 次是时间到，大多数她一次边界都没碰；满血的单个目标一律按住，只在「残血收人头」
//! 「两个人挤在一起」时才放，放完站在圈里等领域消失。0.4.0 照英雄联盟里会玩的阿萝拉重做（判断在 [`call`] / [`steer`]，
//! 纯计算、单元测试）。R 好了的时候，按下面的顺序看，第一条成立就放：
//!
//! 1. **R PEEL（反开）**：`PEEL_R` 内有敌方英雄贴着她，她生命不到 `PEEL_HP`，或者身边敌方英雄一套（[`threat`]）能打掉她
//!    `PEEL_BURST` 以上：朝贴得最近的那个放。领域把他罩住，她靠边界穿到对面拉开（下面的 RIFT KITE）。
//! 2. **R COMBO（一套带走）**：按她现在的法强、技能好没好，估算这一套（[`combo`]：冲击波、紧跟的怪奇喷涌、飞去来咒的去和回、
//!    凑满的驱灵奇术、领域里的 `RIFT_SHOTS` 下普攻，按魔抗、护甲打折）够不够他现在的生命加护盾的 `COMBO_MARGIN` 倍：够就放，
//!    不看他的血量比例。不进敌方塔下（冲击波加怪奇喷涌就能打死他的除外）；他身边 `CROWD_R` 内的敌方英雄不超过一个，或者那里
//!    我方人数不吃亏；她自己生命不低于 `COMBO_SELF_HP`。
//! 3. **R PICK（跟队友一起抓）**：我方英雄贴着他（`ENGAGE_R` 内，在打他），她这一套能打掉他一半以上（`PICK_SHARE`），他身边
//!    的敌方英雄不比那里的我们多，不在敌方塔下：把他关住，二打一。
//! 4. **R TRAP（开团）**：领域（`TRAP_R` 内）罩住两个以上敌方英雄，中心 `ALLY_R` 内有我方英雄，罩住的不比我们（含她）多一个
//!    以上，中心不在敌方塔下，她生命不低于 `TRAP_HP`：挑罩住人最多的方向。
//! 5. **R KILL（关住残血）**：生命不到 `KILL_HP` 的敌方英雄，身边的敌方英雄不超过两个，不在敌方塔下（不到 `DIVE_HP` 的除外）。
//! 6. **R HELD（按住）**：AI 自己想按 R，以上都不成立（满血坦克、一个人冲进五个人、敌方塔下）：不放，改成普攻它的目标。
//!
//! **瞄准**（[`aim`]）：冲击波的中心在她前方 `R_LEAP + R_AHEAD`（40500）。目标在 `AIM_FAR` 以外、没在往外跑，就先朝他走近
//! 再放（`R CLOSER`），让冲击波正好炸在他身上、他站在领域中间；他在跑、快出射程了就立刻放。COMBO / PICK 的目标在射程外
//! `APPROACH` 以内、没在跑，也先走过去。
//!
//! **领域开着时**（被动在她身上挂 `league_aurora_rift:<x>,<y>`，`rift.rs`），[`steer`]：
//!
//! - **RIFT HEX**：冲击波炸开后数据先放怪奇喷涌（R → E），打中英雄就追一颗必中的咒弹（E → Q）；这颗没追出去、飞去来咒还好着，
//!   `HEX_AFTER` tick 后就朝大招的目标放（R → E → Q）。
//! - **RIFT SHOOT**：`KITE_R` 内有敌方英雄、她的普攻好了、他在普攻距离里：先打一下（英雄联盟的走 A：打一下、再走）；
//!   AI 要去打圈外够不着的人、圈里有够得着的敌方英雄：打圈里的。
//! - **RIFT KITE**：普攻没好，`KITE_R` 内有敌方英雄（生命不到 `SPARE_HP` 的除外：留着收掉）：往边界走（[`exit_point`]），
//!   碰到边界穿到对面，把领域的直径隔在两人之间；追过来的人碰到边界被减速。扩散的 `R_GROW` tick 里边界还没成形，不走。
//! - **RIFT STAY**：圈里还有敌方英雄，AI 要走出去：只走到边界里 `STAY_IN`。圈里没有敌方英雄了，被动替她提前关掉领域
//!   （英雄联盟里再按 R，`rift.rs` 的 RIFT CLOSE EARLY），她带着加速去追。
//!
//! 第 1–5 条在 AI 没想按 R 时也按。回城时、被控住或正在放技能时不管；冲到对面的那 `r_wrap_t` tick 不管。

use std::collections::HashMap;

// 技能距离用的时候套 sk：大地图版跟着乘 1.3（game_places::skill_scale）
use game_places::skill_scale::sk;
use mod_api_stable::*;

use super::rift::{self, EDGE};
use super::spirit;
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

// ---------------- 时机的界线 ----------------
/// 贴脸：这么近的敌方英雄（近战够得着她）。0.3.x 是 22000，要贴到身上才算，放得太晚。
pub const PEEL_R: f64 = 30_000.0;
/// 反开：她的生命比例不到这个（0.3.x 是 0.5）。
pub const PEEL_HP: f64 = 0.7;
/// 反开：身边敌方英雄一套能打掉她现在生命的这么多。
pub const PEEL_BURST: f64 = 0.6;
/// 算进「一套」的敌方英雄：离她这么近。
pub const THREAT_R: f64 = 45_000.0;
/// 一套带走：估算的伤害要有他生命加护盾的这么多倍（留余量：他会走、会回血、我们会打偏）。
pub const COMBO_MARGIN: f64 = 1.1;
/// 一套带走：她的生命比例不低于这个。
pub const COMBO_SELF_HP: f64 = 0.25;
/// 跟队友一起抓：她这一套至少打掉他生命加护盾的这么多。
pub const PICK_SHARE: f64 = 0.5;
pub const PICK_SELF_HP: f64 = 0.35;
/// 跟队友一起抓：我方英雄离他这么近算在打他。
pub const ENGAGE_R: f64 = 35_000.0;
/// 开团：她的生命比例不低于这个。
pub const TRAP_HP: f64 = 0.4;
/// 我方英雄算在场：离领域中心（或目标）这么近。
pub const ALLY_R: f64 = 60_000.0;
/// 关住残血：目标的生命比例不到这个；她的不低于 `KILL_SELF_HP`。
pub const KILL_HP: f64 = 0.4;
pub const KILL_SELF_HP: f64 = 0.3;
/// 目标身边多少范围内的敌方英雄算一堆。
pub const CROWD_R: f64 = 30_000.0;
/// 敌方塔下也去关：目标的生命比例不到这个。
pub const DIVE_HP: f64 = 0.2;
/// 敌方塔的攻击范围（大约）。
pub const TOWER_REACH: f64 = 75_000.0;

// ---------------- 瞄准 ----------------
/// 目标比这远、没在跑：先走近再放（冲击波中心在 40500，领域半径 38000：他站在中间才跑不掉）。
pub const AIM_FAR: f64 = 48_000.0;
/// 一 tick 离她远了这么多算在跑（英雄走路一 tick 900–1300）。
pub const AWAY_FAST: f64 = 300.0;
/// 在跑、离射程尽头不到这么远：立刻放。
pub const EDGE_OF_REACH: f64 = 12_000.0;
/// 一套带走 / 一起抓的目标在射程外这么远以内、没在跑：先走过去。
pub const APPROACH: f64 = 15_000.0;
/// 算「在跑」看多少 tick 前的位置。
pub const AWAY_SPAN: usize = 8;

// ---------------- 主包数据（build_aurora.P，单元测试核对） ----------------
/// R 的射程、领域的半径、跃出多远、冲击波（领域）的中心在落地处前方多远、扩散多久（附加包的 r_grow）。
pub const R_RANGE: f64 = 60_000.0;
pub const R_ZONE: f64 = 38_000.0;
pub const R_LEAP: f64 = 15_000.0;
pub const R_AHEAD: f64 = 25_500.0;
pub const R_GROW: usize = 45;
/// 冲击波的半径（加上两个身体就是领域那一圈）。
pub const R_R1: f64 = 28_000.0;
/// 两个单位的身体（射程算到身体边上，大约）。
pub const BODIES: f64 = 12_000.0;
/// 她的普攻够得着（主包 atk_range + 两个身体）、飞去来咒的射程。
pub const ATK_REACH: f64 = 55_000.0 + BODIES;
pub const Q_REACH: f64 = 85_000.0 + BODIES;
/// 飞去来咒的射程这一版是多少：大地图版只乘射程那段，身体不乘。
pub fn q_reach() -> f64 {
    sk(Q_REACH - BODIES) + BODIES
}
/// 一套的伤害（主包参数表 P；英雄联盟的按团战经理的数值换算过）。
pub const R_DMG: usize = 260;
pub const R_RATIO: usize = 80;
pub const E_DMG: usize = 150;
pub const E_RATIO: usize = 80;
pub const Q_DMG: usize = 100;
pub const Q_RATIO: usize = 55;
pub const Q2_DMG: usize = 100;
pub const Q2_RATIO: usize = 55;
/// 飞去来咒回程按他已损失的生命最多加这么多 %（附加包，`spirit.rs`）。
pub const Q2_MISSING: usize = 50;
/// 驱灵奇术第三层：最大生命的千分之 `P_HP_PM`，每 100 法强再加千分之 `P_HP_AP_PM`（英雄联盟 1% + 2.7%）。
pub const P_HP_PM: usize = 10;
pub const P_HP_AP_PM: usize = 27;
/// 领域里还能打的普攻（3 秒左右，攻击间隔 1.5 秒）。
pub const RIFT_SHOTS: usize = 2;

// ---------------- 领域里 ----------------
/// 领域里这么近的敌方英雄算贴着她（够得着她，或者马上就够得着）。
pub const KITE_R: f64 = 40_000.0;
/// 贴身的人生命比例不到这个：不跑，收掉他。
pub const SPARE_HP: f64 = 0.25;
/// 不出领域：走到边界里这么远停下。
pub const STAY_IN: f64 = 6_000.0;
/// 放风筝：走到边界外这么远的点（一定碰得到边界）。
pub const PAST: f64 = 4_000.0;
/// R → E → Q：冲击波炸开（领域出现）这么多 tick 后飞去来咒还好着就朝大招的目标放——数据的 R → E 在 re_gap 8 tick 打出
/// 怪奇喷涌，它打中英雄、飞去来咒好着就在 eq_gap 6 tick 后追一颗必中的咒弹（E → Q，用掉飞去来咒）；没追（怪奇喷涌没好、
/// 没打中英雄）才轮到这里。过了 `HEX_UNTIL` 不再特意放。
pub const HEX_AFTER: usize = 16;
pub const HEX_UNTIL: usize = 150;
/// 她生命不到这个、贴身的人在 `PEEL_R` 内：先跑再打。
pub const RUN_FIRST: f64 = 0.35;

pub type Pt = (f64, f64);

/// 她自己这一 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Me {
    pub at: Pt,
    pub hp: usize,
    pub max: usize,
    pub ap: usize,
    pub ad: usize,
    pub def: usize,
    pub mr: usize,
    pub r_ready: bool,
    pub q_ready: bool,
    pub e_ready: bool,
    pub attack_ready: bool,
}

impl Me {
    pub fn share(&self) -> f64 {
        if self.max == 0 { 0.0 } else { self.hp as f64 / self.max as f64 }
    }
}

/// 一个英雄（敌方或我方）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: Pt,
    pub hp: usize,
    pub max: usize,
    pub shield: usize,
    pub mr: usize,
    pub def: usize,
    pub ad: usize,
    pub ap: usize,
    /// 驱灵奇术在他身上几层（附加包按敌人分别叠，`spirit.rs`）。
    pub stacks: usize,
    /// 这几 tick 他平均每 tick 离她远了多少（负数：在靠近）。
    pub away: f64,
}

impl Unit {
    pub fn share(&self) -> f64 {
        if self.max == 0 { 0.0 } else { self.hp as f64 / self.max as f64 }
    }

    /// 打死他要打掉的：生命加护盾。
    pub fn life(&self) -> f64 {
        (self.hp + self.shield) as f64
    }
}

/// 魔抗、护甲打折（游戏的公式 100 / (100 + 抗性)）。
pub fn mitigated(amount: f64, resist: usize) -> f64 {
    amount * 100.0 / (100.0 + resist as f64)
}

fn scaled(base: usize, ratio: usize, ap: usize) -> f64 {
    base as f64 + (ratio * ap) as f64 / 100.0
}

/// 冲击波加紧跟的怪奇喷涌（落地就到，塔来不及打她）。
pub fn instant(me: &Me, u: &Unit) -> f64 {
    let e = if me.e_ready { scaled(E_DMG, E_RATIO, me.ap) } else { 0.0 };
    mitigated(scaled(R_DMG, R_RATIO, me.ap) + e, u.mr)
}

/// 这一套对他能打掉多少：冲击波、怪奇喷涌（好了的话）、飞去来咒去和回（好了的话，回程按那时他已损失的生命加伤）、
/// 这些凑满的驱灵奇术第三层、领域里 `RIFT_SHOTS` 下普攻。
pub fn combo(me: &Me, u: &Unit) -> f64 {
    let mut magic = scaled(R_DMG, R_RATIO, me.ap);
    let mut counts = 1 + RIFT_SHOTS;
    if me.e_ready {
        magic += scaled(E_DMG, E_RATIO, me.ap);
        counts += 1;
    }
    if me.q_ready {
        magic += scaled(Q_DMG, Q_RATIO, me.ap);
        let lost = ((u.max as f64 - u.hp as f64 + mitigated(magic, u.mr)) / u.max.max(1) as f64).clamp(0.0, 1.0);
        magic += scaled(Q2_DMG, Q2_RATIO, me.ap) * (1.0 + lost * Q2_MISSING as f64 / 100.0);
        counts += 2;
    }
    let procs = (u.stacks.min(2) + counts) / 3;
    magic += procs as f64 * u.max as f64 * (P_HP_PM + P_HP_AP_PM * me.ap / 100) as f64 / 1000.0;
    mitigated(magic, u.mr) + mitigated((RIFT_SHOTS * me.ad) as f64, u.def)
}

/// 身边 `THREAT_R` 内的敌方英雄一套打她多少（粗估：各自两下普攻加一个技能的法强，按她的护甲、魔抗打折）。
pub fn threat(me: &Me, foes: &[Unit]) -> f64 {
    // 没人时 f64 的和是 -0.0，加 0.0 让日志写 0
    foes.iter().filter(|u| dist(me.at, u.at) <= sk(THREAT_R))
        .map(|u| mitigated(2.0 * u.ad as f64, me.def) + mitigated(150.0 + u.ap as f64, me.mr))
        .sum::<f64>() + 0.0
}

/// 大招的时机（日志里的名字）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Peel,
    Combo,
    Pick,
    Trap,
    Kill,
}

impl Kind {
    pub fn name(self) -> &'static str {
        match self {
            Kind::Peel => "peel",
            Kind::Combo => "combo",
            Kind::Pick => "pick",
            Kind::Trap => "trap",
            Kind::Kill => "kill",
        }
    }

    pub fn line(self) -> &'static str {
        match self {
            Kind::Peel => "R PEEL: the rift over the diver, across the border from him",
            Kind::Combo => "R COMBO: the combo kills him",
            Kind::Pick => "R PICK: a friend is on him, the rift keeps him there",
            Kind::Trap => "R TRAP: the rift over a crowd",
            Kind::Kill => "R KILL: the low one trapped",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Call {
    /// 朝这个英雄放 R
    R(usize, Kind),
    /// 先朝他走近：现在放冲击波炸不到他
    Closer(usize, Kind),
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
    let (leap, ahead) = (sk(R_LEAP), sk(R_AHEAD));
    let land = (me.0 + u.0 * leap, me.1 + u.1 * leap);
    let ahead = if dist(me, t) > leap { ahead } else { -ahead };
    (land.0 + u.0 * ahead, land.1 + u.1 * ahead)
}

/// R 的射程（算到身体边上）。
pub fn in_reach(me: Pt, u: &Unit) -> bool {
    dist(me, u.at) <= sk(R_RANGE) + BODIES
}

/// 他身边敌方英雄的人数（不算他）、我方的人数（含她）：不吃亏吗。`allow_one`：他身边只多一个敌人也去。
fn fair(u: &Unit, foes: &[Unit], allies: &[Unit], allow_one: bool) -> bool {
    let theirs = foes.iter().filter(|f| f.id != u.id && dist(f.at, u.at) <= sk(CROWD_R)).count();
    let ours = 1 + near(u.at, allies, sk(ALLY_R));
    (allow_one && theirs <= 1) || theirs + 1 <= ours
}

/// 瞄准：朝 `t` 放（他站在领域中间附近），还是先走近。`peeled`：有人贴着她，不再走。
pub fn aim(me: &Me, t: &Unit, kind: Kind, peeled: bool) -> Call {
    let d = dist(me.at, t.at);
    let running = t.away >= AWAY_FAST;
    let reach = sk(R_RANGE) + BODIES;
    if d > reach || (d > sk(AIM_FAR) && !peeled && !(running && d > reach - EDGE_OF_REACH)) {
        return Call::Closer(t.id, kind);
    }
    Call::R(t.id, kind)
}

/// What to press (None: leave the AI's input).
pub fn call(me: &Me, foes: &[Unit], allies: &[Unit], towers: &[Pt], ai_wants_r: Option<Option<usize>>) -> Option<Call> {
    if me.r_ready {
        let close = foes.iter().filter(|u| dist(me.at, u.at) <= PEEL_R)
            .min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at)));
        // 1. 有人贴着她，她掉了血或者对面一套能打掉她大半：领域罩住他
        if let Some(t) = close {
            if me.share() < PEEL_HP || threat(me, foes) >= PEEL_BURST * me.hp as f64 {
                return Some(Call::R(t.id, Kind::Peel));
            }
        }
        let peeled = close.is_some();
        let reach: Vec<&Unit> = foes.iter().filter(|u| in_reach(me.at, u)).collect();
        // 2. 这一套打得死他（不进塔，落地就能打死的除外；不冲进他们一堆人里）
        if me.share() >= COMBO_SELF_HP {
            let t = foes.iter()
                .filter(|u| dist(me.at, u.at) <= sk(R_RANGE) + BODIES + if u.away < AWAY_FAST { APPROACH } else { 0.0 })
                .filter(|u| combo(me, u) >= COMBO_MARGIN * u.life())
                .filter(|u| fair(u, foes, allies, true))
                .filter(|u| instant(me, u) >= u.life() || !(towered(u.at, towers) || towered(centre(me.at, u.at), towers)))
                .min_by(|a, b| a.life().total_cmp(&b.life()));
            if let Some(t) = t {
                return Some(aim(me, t, Kind::Combo, peeled));
            }
        }
        // 3. 队友贴着他：关住他，二打一
        if me.share() >= PICK_SELF_HP {
            let t = foes.iter()
                .filter(|u| dist(me.at, u.at) <= sk(R_RANGE) + BODIES + if u.away < AWAY_FAST { APPROACH } else { 0.0 })
                .filter(|u| allies.iter().any(|a| dist(a.at, u.at) <= ENGAGE_R))
                .filter(|u| combo(me, u) >= PICK_SHARE * u.life())
                .filter(|u| fair(u, foes, allies, false))
                .filter(|u| u.share() < DIVE_HP || !towered(u.at, towers))
                .max_by(|a, b| (combo(me, a) / a.life().max(1.0)).total_cmp(&(combo(me, b) / b.life().max(1.0))));
            if let Some(t) = t {
                return Some(aim(me, t, Kind::Pick, peeled));
            }
        }
        // 4. 领域能罩住两个以上，那里有队友，人数不吃亏（最多多一个），不在敌方塔下
        if me.share() >= TRAP_HP {
            let t = reach.iter()
                .map(|u| {
                    let c = centre(me.at, u.at);
                    (*u, c, near(c, foes, sk(TRAP_R)))
                })
                .filter(|&(_, c, n)| {
                    let ours = 1 + near(c, allies, sk(ALLY_R));
                    n >= 2 && ours >= 2 && n <= ours + 1 && !towered(c, towers)
                })
                .max_by(|a, b| a.2.cmp(&b.2).then(b.0.share().total_cmp(&a.0.share()))
                    .then(dist(me.at, b.0.at).total_cmp(&dist(me.at, a.0.at))));
            if let Some((t, _, _)) = t {
                return Some(aim(me, t, Kind::Trap, peeled));
            }
        }
        // 5. 射程里的残血，不在他们一堆人里
        if me.share() >= KILL_SELF_HP {
            let t = reach.iter()
                .filter(|u| {
                    u.share() < KILL_HP && near(u.at, foes, sk(CROWD_R)) <= 2
                        && (u.share() < DIVE_HP || !towered(centre(me.at, u.at), towers))
                })
                .min_by(|a, b| a.share().total_cmp(&b.share()));
            if let Some(t) = t {
                return Some(aim(me, t, Kind::Kill, peeled));
            }
        }
    }
    // 6. AI 自己想按 R，上面都不成立：按住
    ai_wants_r.map(Call::Hold)
}

/// 关住了吗：离中心这么近（那一圈加半个身体）。
pub const TRAP_R: f64 = 43_000.0;

// ===================== 领域开着时怎么走 =====================

/// What the game's AI wants while the rift is open.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Want {
    /// walk there
    Move(Pt),
    /// 普攻这个单位（够不着就走过去）：它的 id、位置、是不是英雄
    Attack(usize, Pt, bool),
    /// a skill, the ult, recall: left alone
    Cast,
    /// no new input this think
    Idle,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Steer {
    /// R → E → Q：朝他放飞去来咒
    Hex(usize),
    /// 普攻他（她的普攻好了，他在普攻距离里）
    Shoot(usize),
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
    let r = sk(EDGE) + PAST;
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

/// 领域开着时（中心 `c`，开了 `age` tick，`aimed` 是她大招的目标）：R → E 之后放 Q、走 A、有人贴身就往边界走、
/// AI 往外走时留在圈里（None：不管 AI 的命令）。
pub fn steer(me: &Me, c: Pt, age: usize, foes: &[Unit], want: Want, aimed: Option<usize>) -> Option<Steer> {
    if want == Want::Cast {
        return None;
    }
    let in_rift = |u: &&Unit| dist(c, u.at) < sk(rift::RING) + rift::BAND / 2.0;
    let threat = foes.iter().filter(|u| u.share() >= SPARE_HP && dist(me.at, u.at) <= KITE_R)
        .min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at)));
    let running = threat.is_some_and(|t| me.share() < RUN_FIRST && dist(me.at, t.at) <= PEEL_R);
    // R → E → Q：怪奇喷涌打出去以后，朝大招的目标（没有就圈里最近的）放飞去来咒
    if me.q_ready && !running && (HEX_AFTER..=HEX_UNTIL).contains(&age) {
        let t = aimed.and_then(|id| foes.iter().find(|u| u.id == id))
            .or_else(|| foes.iter().filter(in_rift).min_by(|a, b| dist(me.at, a.at).total_cmp(&dist(me.at, b.at))))
            .filter(|u| dist(me.at, u.at) <= q_reach());
        if let Some(t) = t {
            return Some(Steer::Hex(t.id));
        }
    }
    if let Some(t) = threat {
        // 普攻好了、他够得着：先打一下（英雄联盟的走 A：打一下再走）；她残血、他贴着她时先跑
        if me.attack_ready && !running && dist(me.at, t.at) <= ATK_REACH {
            return Some(Steer::Shoot(t.id));
        }
        if age >= R_GROW {
            return Some(Steer::Kite(exit_point(me.at, c, t.at), t.id));
        }
    }
    let inner = sk(EDGE) - STAY_IN;
    let anyone_in = foes.iter().any(|u| in_rift(&u));
    match want {
        Want::Move(p) if dist(c, p) > inner && anyone_in => Some(Steer::Stay(clamp(c, p, inner))),
        Want::Attack(_, at, _) => {
            let d = dist(me.at, at);
            if d <= ATK_REACH {
                return None;
            }
            // 圈里有她够得着的：打他，不去追圈外的
            if let Some(u) = foes.iter().filter(in_rift).filter(|u| dist(me.at, u.at) <= ATK_REACH)
                .min_by(|a, b| a.share().total_cmp(&b.share())) {
                return me.attack_ready.then_some(Steer::Shoot(u.id));
            }
            if !anyone_in {
                return None;
            }
            let stop = (at.0 - (at.0 - me.at.0) / d * ATK_REACH, at.1 - (at.1 - me.at.1) / d * ATK_REACH);
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

fn pt(e: &StableEntity<'_, '_>) -> Pt {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

fn on_map(p: Pt) -> (u64, u64) {
    (p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

/// 他身上驱灵奇术几层（`spirit.rs` 的 p1 / p2）。
fn stacks_of(e: &StableEntity<'_, '_>) -> usize {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| spirit::stacks_in(b.name())).max().unwrap_or(0)
}

fn unit_of(e: &StableEntity<'_, '_>, away: f64) -> Unit {
    let (hp, max) = e.hp();
    let s = e.stat();
    Unit { id: e.id(), at: pt(e), hp, max, shield: e.shield(), mr: s.magic_resistance, def: s.defence, ad: s.attack,
           ap: s.magic_power, stacks: stacks_of(e), away }
}

/// 每种决定一串只记一行。
const KINDS: [&str; 11] = ["peel", "combo", "pick", "trap", "kill", "held", "closer", "hex", "shoot", "kite", "stay"];

/// 敌方英雄是不是在跑：`AWAY_SPAN` tick 前的位置，和那以后每 tick 离她远了多少。
#[derive(Clone, Default)]
pub struct Track {
    seen: Option<(usize, HashMap<usize, Pt>)>,
    pub away: HashMap<usize, f64>,
}

impl Track {
    /// 每个敌方英雄离她远去得多快（每 tick，按 AWAY_SPAN tick 前的位置算）。
    pub fn update(&mut self, now: usize, me: Pt, foes: &[(usize, Pt)]) {
        match &self.seen {
            Some((t0, _)) if now >= *t0 && now < t0 + AWAY_SPAN => {}
            Some((t0, then)) if now >= *t0 => {
                let dt = (now - t0) as f64;
                self.away = foes.iter().filter_map(|(id, at)| then.get(id).map(|p| (*id, (dist(me, *at) - dist(me, *p)) / dt)))
                    .collect();
                self.seen = Some((now, foes.iter().copied().collect()));
            }
            _ => {
                self.away.clear();
                self.seen = Some((now, foes.iter().copied().collect()));
            }
        }
    }

    pub fn away_of(&self, id: usize) -> f64 {
        self.away.get(&id).copied().unwrap_or(0.0)
    }
}

/// 领域的中心和第一次看到它的 tick（领域开着多久）。
pub fn rift_since(now: usize, mark: Option<Pt>, was: Option<(Pt, usize)>) -> Option<(Pt, usize)> {
    match (mark, was) {
        (Some(c), Some((c0, t0))) if dist(c, c0) < 1.0 && now >= t0 => Some((c0, t0)),
        (Some(c), _) => Some((c, now)),
        (None, _) => None,
    }
}

/// 数据的连招锁（E → Q 用掉飞去来咒时挂的 `league_aurora_q_cd`，R → E 用掉怪奇喷涌时的 `league_aurora_e_cd`）：
/// 挂着的时候按那个格子什么也不放。
pub const Q_LOCK: &str = "league_aurora_q_cd";
pub const E_LOCK: &str = "league_aurora_e_cd";

#[derive(Clone, Default)]
pub struct Realm {
    recalling: bool,
    /// 每种决定上一次按的 tick（KINDS）：一串只记一行
    pressed: [Option<usize>; 11],
    track: Track,
    /// 她在的领域：中心、第一次看到标记的 tick；她大招的目标
    rift: Option<(Pt, usize)>,
    aimed: Option<(usize, usize)>,
}

impl Realm {
    /// A press of `kind` at `tick`: the first of its burst (it gets a line); noted for the next.
    fn fresh(&mut self, kind: &str, tick: usize) -> bool {
        let k = KINDS.iter().position(|x| *x == kind).unwrap_or(5);
        let last = &mut self.pressed[k];
        let first = new_burst(*last, tick);
        *last = Some(tick);
        first
    }
}

/// What think() decided while the sim was borrowed.
enum Plan {
    /// 怎么走、日志那一行、是不是你看的那场、飞去来咒的方向
    Steer(Steer, String, bool, (i64, i64)),
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
        let now = ctx.tick();
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
            let (hp, max) = e.hp();
            let s = e.stat();
            let locked = |name: &str| buffs.iter().any(|b| b.name() == name);
            let me = Me { at: pt(&e), hp, max, ap: s.magic_power, ad: s.attack, def: s.defence, mr: s.magic_resistance,
                          r_ready: ready(&e, SkillSlotV1::Ult), q_ready: ready(&e, SkillSlotV1::Skill) && !locked(Q_LOCK),
                          e_ready: ready(&e, SkillSlotV1::Skill2) && !locked(E_LOCK),
                          attack_ready: ready(&e, SkillSlotV1::Attack) };
            let (mut champs, mut allies, mut towers) = (Vec::new(), Vec::new(), Vec::new());
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
                if u.team() == team {
                    allies.push(unit_of(&u, 0.0));
                } else if u.is_targetable() {
                    champs.push(u.id());
                }
            }
            let spots: Vec<(usize, Pt)> = champs.iter().filter_map(|&c| sim.get_entity(c)).map(|u| (u.id(), pt(&u))).collect();
            self.track.update(now, me.at, &spots);
            let foes: Vec<Unit> = champs.iter().filter_map(|&c| sim.get_entity(c))
                .map(|u| unit_of(&u, self.track.away_of(u.id()))).collect();
            // 领域在哪、开了多久（标记在开的那一 tick 出现）
            self.rift = rift_since(now, rift_at, self.rift);
            let aimed = self.aimed.filter(|(_, t)| now >= *t && now <= t + 600).map(|(a, _)| a);
            let shown = on_screen(&sim);
            let kind = base.and_then(|b| InputKindV1::from_code(b.kind));
            let steered = self.rift.and_then(|(c, t0)| {
                let want = match (kind, base) {
                    (Some(InputKindV1::Move), Some(b)) => Want::Move((b.x as f64, b.y as f64)),
                    (Some(InputKindV1::Attack), Some(b)) => sim.get_entity(b.target.target_id)
                        .map_or(Want::Cast, |t| Want::Attack(t.id(), pt(&t), t.is_champion())),
                    (None, _) => Want::Idle,
                    _ => Want::Cast,
                };
                steer(&me, c, now - t0, &foes, want, aimed).map(|s| {
                    let about = |t: usize| foes.iter().find(|u| u.id == t).map_or((0.0, 0.0), |u| (dist(me.at, u.at), u.share() * 100.0));
                    let why = match (s, want) {
                        (Steer::Hex(t), _) => {
                            let (d, h) = about(t);
                            format!("RIFT HEX: R -> E -> Q, the hex at #{t} ({d:.0} away, hp {h:.0}%)")
                        }
                        (Steer::Shoot(t), _) => {
                            let (d, h) = about(t);
                            format!("RIFT SHOOT: her attack is ready, #{t} in reach ({d:.0} away, hp {h:.0}%)")
                        }
                        (Steer::Kite(to, t), _) => {
                            let (d, _) = about(t);
                            format!("RIFT KITE: #{t} on her ({d:.0} away), to the border at ({:.0}, {:.0}) - across from there", to.0, to.1)
                        }
                        (Steer::Stay(to), Want::Move(p)) => format!(
                            "RIFT STAY: the AI's walk to ({:.0}, {:.0}) leaves the rift, held at ({:.0}, {:.0})", p.0, p.1, to.0, to.1),
                        (Steer::Stay(to), _) => format!(
                            "RIFT STAY: the AI's walk to its target out of reach leaves the rift, held at ({:.0}, {:.0})", to.0, to.1),
                    };
                    (s, format!("{} [hp {:.0}%] rift at ({:.0}, {:.0}), {:.0} from it, open {} ticks: {why}", head(&sim, id),
                                me.share() * 100.0, c.0, c.1, dist(me.at, c), now - t0))
                })
            });
            match steered {
                Some((s, line)) => {
                    let to = match s {
                        Steer::Hex(t) => foes.iter().find(|u| u.id == t).map_or((1, 0), |u| {
                            ((u.at.0 - me.at.0).round() as i64, (u.at.1 - me.at.1).round() as i64)
                        }),
                        _ => (0, 0),
                    };
                    Plan::Steer(s, line, shown, to)
                }
                None => {
                    let wants = base.filter(|b| b.kind == InputKindV1::Ult.code()).map(|b| {
                        (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
                    });
                    let c = call(&me, &foes, &allies, &towers, wants)?;
                    let on = match c {
                        Call::R(t, _) | Call::Closer(t, _) | Call::Hold(Some(t)) => Some(t),
                        Call::Hold(None) => None,
                    };
                    let target = on.and_then(|t| foes.iter().find(|u| u.id == t));
                    let spot = target.map(|u| on_map(u.at));
                    let opens = target.map(|u| centre(me.at, u.at));
                    let crowd = opens.map_or(0, |c| near(c, &foes, sk(TRAP_R)));
                    let at = opens.map_or("-".to_string(), |c| format!("({:.0}, {:.0})", c.0, c.1));
                    let est = target.map_or(String::new(), |u| format!(", combo {:.0} of his {:.0}", combo(&me, u), u.life()));
                    let d = target.map_or(0.0, |u| dist(me.at, u.at));
                    Plan::Press(c, format!("{} [hp {:.0}%] on #{} {d:.0} away ({crowd} in the rift at {at}, hp {:.0}%{est})",
                                           head(&sim, id), me.share() * 100.0, on.map_or("-".to_string(), |t| t.to_string()),
                                           target.map_or(0.0, |u| u.share() * 100.0)),
                                (spot, on_map(me.at)), shown)
                }
            }
        };
        let (c, line, spot, shown) = match plan {
            Plan::Steer(s, line, shown, hex) => {
                let (kind, input) = match s {
                    // 飞去来咒按方向放：朝他（大头附加包的做法）
                    Steer::Hex(_) => ("hex", InputV1::action(InputKindV1::Skill, InputTargetV1::dir(hex.0, hex.1))),
                    Steer::Shoot(t) => ("shoot", InputV1::action(InputKindV1::Attack, InputTargetV1::target(t))),
                    Steer::Kite(to, _) => {
                        let (x, y) = on_map(to);
                        ("kite", InputV1::move_to(x, y))
                    }
                    Steer::Stay(to) => {
                        let (x, y) = on_map(to);
                        ("stay", InputV1::move_to(x, y))
                    }
                };
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                if self.fresh(kind, now) {
                    let tag = match kind {
                        "hex" => "rift hex",
                        "shoot" => "rift shoot",
                        "kite" => "rift kite",
                        _ => "rift stay",
                    };
                    if let Some(n) = counted(tag, shown) {
                        wlog(format!("{line} #{n}"));
                    }
                }
                return Some(input);
            }
            Plan::Press(c, line, spot, shown) => (c, line, spot, shown),
        };
        let (input, kind, why) = match c {
            Call::R(t, k) => (InputV1::action(InputKindV1::Ult, InputTargetV1::target(t)), k.name(), k.line()),
            Call::Closer(t, k) => {
                let (x, y) = spot.0.unwrap_or(spot.1);
                let _ = t;
                (InputV1::move_to(x, y), "closer", match k {
                    Kind::Combo => "R CLOSER: walking up for the combo - the shockwave goes off 40500 ahead",
                    Kind::Pick => "R CLOSER: walking up for the pick - the shockwave goes off 40500 ahead",
                    Kind::Trap => "R CLOSER: walking up to the crowd - the shockwave goes off 40500 ahead",
                    _ => "R CLOSER: walking up - the shockwave goes off 40500 ahead",
                })
            }
            Call::Hold(t) => {
                let attack = t.map(|t| InputV1::action(InputKindV1::Attack, InputTargetV1::target(t)));
                let input = match attack.filter(|a| ctx.is_valid_input(a)) {
                    Some(a) => a,
                    None => {
                        let (x, y) = spot.0.unwrap_or(spot.1);
                        InputV1::move_to(x, y)
                    }
                };
                if self.fresh("held", now) {
                    if let Some(n) = counted("r held", shown) {
                        wlog(format!("{line} R HELD: no kill, no pick, no crowd, no peel - the AI's R kept #{n}"));
                    }
                }
                return Some(input);
            }
        };
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Call::R(t, _) = c {
            self.aimed = Some((t, now));
        }
        if self.fresh(kind, now) {
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

    fn me(share: f64) -> Me {
        Me { at: (0.0, 0.0), hp: (1500.0 * share) as usize, max: 1500, ap: 200, ad: 110, def: 40, mr: 40,
             r_ready: true, q_ready: true, e_ready: true, attack_ready: false }
    }

    /// 一个敌方英雄：x 处，生命比例 share（最大 2000），魔抗 40。
    fn u(id: usize, x: f64, share: f64) -> Unit {
        Unit { id, at: (x, 0.0), hp: (2000.0 * share) as usize, max: 2000, shield: 0, mr: 40, def: 40, ad: 120, ap: 0,
               stacks: 0, away: 0.0 }
    }

    fn at(id: usize, x: f64, y: f64, share: f64) -> Unit {
        Unit { at: (x, y), ..u(id, 0.0, share) }
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
        // 走近到 AIM_FAR 再放：冲击波炸在他身上，他站在领域中间
        assert!(dist(centre((0.0, 0.0), (AIM_FAR, 0.0)), (AIM_FAR, 0.0)) < 10_000.0);
    }

    #[test]
    fn the_combo_counts_what_is_ready() {
        let m = me(1.0);
        let t = u(1, 40_000.0, 1.0);
        let all = combo(&m, &t);
        let no_q = combo(&Me { q_ready: false, ..m }, &t);
        let no_qe = combo(&Me { q_ready: false, e_ready: false, ..m }, &t);
        assert!(all > no_q && no_q > no_qe, "{all} {no_q} {no_qe}");
        // 只有 R（260 + 200 的 80% = 420 魔法，40 魔抗打折后 300）加两下普攻（220，40 护甲打折后 157）：
        // R 加两下普攻正好三层：2000 的 1% + 2.7% × 2 = 128 魔法，打折后 91
        assert!((no_qe - (300.0 + 157.1 + 91.4)).abs() < 2.0, "{no_qe}");
        // 他身上已经有层数，第三层来得更早：只会更多
        assert!(combo(&m, &Unit { stacks: 2, ..t }) >= all);
        // 魔抗高就少
        assert!(combo(&m, &Unit { mr: 100, ..t }) < all);
        // 他掉了血，回程打得更疼
        let hurt = Unit { hp: 600, ..t };
        assert!(combo(&m, &hurt) > all - 1.0);
    }

    #[test]
    fn a_killable_champion_at_full_health_is_comboed() {
        // 0.3.x：满血的单个目标一律按住（R KILL 要 40% 以下）。现在一套打得死的脆皮照放
        let m = me(0.9);
        let squishy = Unit { hp: 900, max: 900, ..u(1, 45_000.0, 1.0) };
        assert!(combo(&m, &squishy) >= COMBO_MARGIN * squishy.life());
        assert_eq!(call(&m, &[squishy], &[], &[], None), Some(Call::R(1, Kind::Combo)));
        // 满血坦克打不死：按住
        let tank = Unit { hp: 3000, max: 3000, mr: 80, ..u(2, 45_000.0, 1.0) };
        assert_eq!(call(&m, &[tank], &[], &[], Some(Some(2))), Some(Call::Hold(Some(2))));
        // 同一个脆皮在塔下：不放（落地那一下打不死他）
        assert!(instant(&m, &squishy) < squishy.life());
        assert_eq!(call(&m, &[squishy], &[], &[(60_000.0, 0.0)], None), None);
        // 冲击波加怪奇喷涌就打得死：放
        let dying = Unit { hp: 300, ..squishy };
        assert_eq!(call(&m, &[dying], &[], &[(60_000.0, 0.0)], None), Some(Call::R(1, Kind::Combo)));
        // 他身边还有两个队友、她一个人：不放
        let deep = [squishy, at(5, 50_000.0, 5_000.0, 1.0), at(6, 50_000.0, -5_000.0, 1.0)];
        assert!(!matches!(call(&m, &deep, &[], &[], None), Some(Call::R(1, Kind::Combo))));
    }

    #[test]
    fn the_shockwave_is_aimed_on_him() {
        let m = me(0.9);
        let far = Unit { hp: 800, max: 900, ..u(1, 65_000.0, 1.0) };
        // 远、站着：先走近
        assert_eq!(call(&m, &[far], &[], &[], None), Some(Call::Closer(1, Kind::Combo)));
        // 远、在往外跑：马上放
        let running = Unit { away: 800.0, ..far };
        assert_eq!(call(&m, &[running], &[], &[], None), Some(Call::R(1, Kind::Combo)));
        // 够近：放
        let near_ = Unit { at: (42_000.0, 0.0), ..far };
        assert_eq!(call(&m, &[near_], &[], &[], None), Some(Call::R(1, Kind::Combo)));
        // 刚出射程、站着：走过去；在跑：不追
        let out = Unit { at: (80_000.0, 0.0), ..far };
        assert_eq!(call(&m, &[out], &[], &[], None), Some(Call::Closer(1, Kind::Combo)));
        assert_eq!(call(&m, &[Unit { away: 800.0, ..out }], &[], &[], None), None);
    }

    #[test]
    fn a_diver_is_answered_early() {
        // 0.3.x 要到 50% 以下，现在 65% 就反开
        let diver = u(1, 20_000.0, 1.0);
        assert_eq!(call(&me(0.65), &[diver], &[], &[], None), Some(Call::R(1, Kind::Peel)));
        // 健康、贴着她的人打不疼：不反开（一套也打不死他：按住）
        let weak = Unit { ad: 60, ap: 0, hp: 3000, max: 3000, ..diver };
        assert_eq!(call(&me(0.95), &[weak], &[], &[], Some(Some(1))), Some(Call::Hold(Some(1))));
        // 健康但三个人贴着她，一套能打掉她大半：反开
        let three = [Unit { ad: 300, ..weak }, Unit { id: 2, ad: 300, ..weak }, Unit { id: 3, ad: 300, ap: 300, ..weak }];
        assert!(threat(&me(0.95), &three) >= PEEL_BURST * me(0.95).hp as f64);
        assert_eq!(call(&me(0.95), &three, &[], &[], None), Some(Call::R(1, Kind::Peel)));
        // 40000 外不算贴身
        assert_eq!(call(&me(0.4), &[u(1, 40_000.0, 1.0)], &[], &[], None).map(|c| matches!(c, Call::R(_, Kind::Peel))), None);
    }

    #[test]
    fn a_friend_on_him_makes_a_pick() {
        let m = me(0.9);
        let t = Unit { hp: 1800, max: 2000, ..u(1, 45_000.0, 1.0) };
        assert!(combo(&m, &t) < COMBO_MARGIN * t.life() && combo(&m, &t) >= PICK_SHARE * t.life());
        let friend = at(10, 60_000.0, 10_000.0, 1.0);
        assert_eq!(call(&m, &[t], &[friend], &[], None), Some(Call::R(1, Kind::Pick)));
        // 没有队友在打他：按住
        let away = at(10, -60_000.0, 0.0, 1.0);
        assert_eq!(call(&m, &[t], &[away], &[], Some(Some(1))), Some(Call::Hold(Some(1))));
        // 他那边三个、我们这边一个：不抓
        let crowd = [t, at(2, 50_000.0, 8_000.0, 1.0), at(3, 50_000.0, -8_000.0, 1.0)];
        assert!(!matches!(call(&m, &crowd, &[friend], &[], None), Some(Call::R(_, Kind::Pick))));
    }

    #[test]
    fn the_rift_goes_over_the_biggest_crowd() {
        let allies = [at(10, 20_000.0, 0.0, 1.0)];
        let tank = |id, x: f64, y: f64| Unit { hp: 3500, max: 3500, mr: 90, ..at(id, x, y, 1.0) };
        // #1 alone to the east; #2 to the south with #3 behind him: toward #2 the rift holds both
        let foes = [tank(1, 45_000.0, 0.0), Unit { hp: 3000, ..tank(2, 0.0, 45_000.0) }, tank(3, 0.0, 60_000.0),
                    tank(4, 300_000.0, 0.0)];
        assert_eq!(call(&me(0.9), &foes, &allies, &[], None), Some(Call::R(2, Kind::Trap)));
        // no friend of hers there: no engage
        assert_eq!(call(&me(0.9), &foes, &[], &[], None), None);
        // the rift under their tower: no
        assert_eq!(call(&me(0.9), &foes, &allies, &[(0.0, 50_000.0)], None).map(|c| matches!(c, Call::R(_, Kind::Trap))), None);
    }

    #[test]
    fn a_low_one_is_trapped_unless_he_is_deep_in_his_team() {
        let tank = |id, x: f64, share: f64| Unit { hp: (5000.0 * share) as usize, max: 5000, mr: 120, ..u(id, x, share) };
        assert_eq!(call(&me(0.9), &[tank(1, 45_000.0, 0.3)], &[], &[], None), Some(Call::R(1, Kind::Kill)));
        let deep = [tank(1, 45_000.0, 0.3), tank(2, 55_000.0, 1.0), tank(3, 60_000.0, 1.0)];
        assert_eq!(call(&me(0.9), &deep, &[], &[], Some(Some(1))), Some(Call::Hold(Some(1))));
        assert_eq!(call(&me(0.9), &[tank(1, 45_000.0, 0.3)], &[], &[(45_000.0, 0.0)], None), None);
    }

    #[test]
    fn nothing_without_the_ult() {
        let m = Me { r_ready: false, ..me(0.3) };
        assert_eq!(call(&m, &[u(1, 10_000.0, 0.1)], &[], &[], None), None);
    }

    #[test]
    fn after_the_blast_the_hex() {
        let c = (0.0, 0.0);
        let m = Me { at: (-25_500.0, 0.0), ..me(0.9) };
        let t = [u(7, 10_000.0, 0.8)];
        // 冲击波和 R → E 都打出去了：朝大招的目标放 Q
        assert_eq!(steer(&m, c, HEX_AFTER, &t, Want::Idle, Some(7)), Some(Steer::Hex(7)));
        // 还早（先等怪奇喷涌），Q 没好也不放
        assert_ne!(steer(&m, c, 2, &t, Want::Idle, Some(7)), Some(Steer::Hex(7)));
        assert_ne!(steer(&Me { q_ready: false, ..m }, c, HEX_AFTER, &t, Want::Idle, Some(7)), Some(Steer::Hex(7)));
        // AI 在放技能：不打断
        assert_eq!(steer(&m, c, HEX_AFTER, &t, Want::Cast, Some(7)), None);
    }

    #[test]
    fn a_champion_on_her_in_the_rift_sends_her_to_the_border() {
        let c = (0.0, 0.0);
        // she stands 25500 west of the centre, a fighter on her from the east: straight out west, past the edge
        let m = Me { at: (-25_500.0, 0.0), q_ready: false, ..me(0.9) };
        let on_her = [u(7, -5_000.0, 1.0)];
        let Some(Steer::Kite(to, 7)) = steer(&m, c, R_GROW, &on_her, Want::Attack(7, (-5_000.0, 0.0), true), None) else { panic!() };
        assert!(close(to, (-(EDGE + PAST), 0.0)), "{to:?}");
        // 普攻好了：先打一下，不管 AI 说什么
        let ready = Me { attack_ready: true, ..m };
        assert_eq!(steer(&ready, c, R_GROW, &on_her, Want::Idle, None), Some(Steer::Shoot(7)));
        // 残血、他贴着：先跑
        let low = Me { hp: 300, attack_ready: true, ..m };
        let on_top = [u(7, -15_000.0, 1.0)];
        assert!(matches!(steer(&low, c, R_GROW, &on_top, Want::Idle, None), Some(Steer::Kite(..))));
        // 领域还在扩散：还没有边界可穿
        assert_eq!(steer(&m, c, R_GROW - 1, &on_her, Want::Idle, None), None);
        // nearly dead: no running, finish him
        assert_eq!(steer(&m, c, R_GROW, &[u(7, -5_000.0, 0.2)], Want::Idle, None), None);
        // he stands between her and that border: away from him instead
        let blocking = [u(8, -45_000.0, 1.0)];
        let mid = Me { at: (-20_000.0, 0.0), ..m };
        let Some(Steer::Kite(to, 8)) = steer(&mid, c, R_GROW, &blocking, Want::Idle, None) else { panic!() };
        assert!(to.0 > -20_000.0 && (dist(c, to) - (EDGE + PAST)).abs() < 1.0, "{to:?}");
        // at the centre: away from him
        let to = exit_point(c, c, (-10_000.0, 0.0));
        assert!(close(to, (EDGE + PAST, 0.0)), "{to:?}");
    }

    #[test]
    fn the_ai_does_not_walk_out_of_the_rift_while_someone_is_in_it() {
        let c = (0.0, 0.0);
        let m = Me { at: (-25_000.0, 0.0), q_ready: false, ..me(0.9) };
        // 圈里有一个敌人，在她对面（没贴着她）
        let inside = [u(3, 25_000.0, 1.0)];
        let Some(Steer::Stay(to)) = steer(&m, c, 60, &inside, Want::Move((-200_000.0, 0.0)), None) else { panic!() };
        assert!(close(to, (-(EDGE - STAY_IN), 0.0)), "{to:?}");
        // a walk inside is left alone
        assert_eq!(steer(&m, c, 60, &inside, Want::Move((-20_000.0, 5_000.0)), None), None);
        // 圈里没人了：让她走（被动会提前关掉领域）
        assert_eq!(steer(&m, c, 60, &[u(3, 120_000.0, 1.0)], Want::Move((-200_000.0, 0.0)), None), None);
        // AI 要去打圈外的，圈里有够得着的：打圈里的
        let both = [u(3, 25_000.0, 1.0), u(4, -150_000.0, 1.0)];
        let ready = Me { attack_ready: true, ..m };
        assert_eq!(steer(&ready, c, 60, &both, Want::Attack(4, (-150_000.0, 0.0), true), None), Some(Steer::Shoot(3)));
        // 圈里没有够得着的：只走到边界里侧
        let far_in = [u(3, 36_000.0, 1.0), u(4, -150_000.0, 1.0)];
        let wide = Me { at: (-34_000.0, 0.0), ..m };
        let Some(Steer::Stay(to)) = steer(&wide, c, 60, &far_in, Want::Attack(4, (-150_000.0, 0.0), true), None) else { panic!() };
        assert!(close(to, (-(EDGE - STAY_IN), 0.0)), "{to:?}");
        assert_eq!(steer(&m, c, 60, &inside, Want::Idle, None), None);
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
        assert!(r.fresh("combo", 57_932) && r.fresh("pick", 57_932) && r.fresh("hex", 57_932) && r.fresh("shoot", 57_932));
        assert!(new_burst(Some(57_929), 100), "another match");
    }

    #[test]
    fn running_is_read_from_the_last_ticks() {
        let mut r = Track::default();
        r.update(100, (0.0, 0.0), &[(1, (40_000.0, 0.0))]);
        r.update(104, (0.0, 0.0), &[(1, (44_000.0, 0.0))]);
        assert!(r.away.is_empty(), "too soon to tell");
        r.update(100 + AWAY_SPAN, (0.0, 0.0), &[(1, (48_000.0, 0.0))]);
        assert!((r.away_of(1) - 1_000.0).abs() < 1.0, "{:?}", r.away);
        // 换了一局（tick 变小）：重来
        r.update(5, (0.0, 0.0), &[(1, (48_000.0, 0.0))]);
        assert!(r.away.is_empty());
    }

    #[test]
    fn the_rift_is_timed_from_its_first_mark() {
        let c = (100.0, 200.0);
        let r = rift_since(50, Some(c), None);
        assert_eq!(r, Some((c, 50)));
        assert_eq!(rift_since(80, Some(c), r), Some((c, 50)));
        // 别处开了新领域，或者没了
        assert_eq!(rift_since(90, Some((900.0, 0.0)), r), Some(((900.0, 0.0), 90)));
        assert_eq!(rift_since(95, None, r), None);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let src = include_str!("../../../tools/kit/build_aurora.py");
        for (key, v) in [("r_range", R_RANGE as usize), ("r_zone", R_ZONE as usize), ("r_leap", R_LEAP as usize),
                         ("r_ahead", R_AHEAD as usize), ("r_r1", R_R1 as usize), ("atk_range", (ATK_REACH - BODIES) as usize),
                         ("q_range", (Q_REACH - BODIES) as usize), ("r_dmg", R_DMG), ("r_ratio", R_RATIO), ("e_dmg", E_DMG),
                         ("e_ratio", E_RATIO), ("q_dmg", Q_DMG), ("q_ratio", Q_RATIO), ("q2_dmg", Q2_DMG),
                         ("q2_ratio", Q2_RATIO), ("q2_miss", Q2_MISSING), ("p_hp_pm", P_HP_PM), ("p_hp_ap_pm", P_HP_AP_PM),
                         ("r_grow", R_GROW)] {
            assert!(src.contains(&format!("\"{key}\": {v},")), "{key} {v}");
        }
        assert_eq!(R_ZONE, rift::RING);
        // 数据的 R → E → Q（re_gap 再 eq_gap）在钩子自己的 Q 前面
        assert!(src.contains("\"re_gap\": 8") && src.contains("\"eq_gap\": 6") && HEX_AFTER > 8 + 6);
    }
}
