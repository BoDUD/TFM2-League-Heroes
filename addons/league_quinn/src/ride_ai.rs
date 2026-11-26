//! 深入敌后什么时候骑（0.4.0，用户 2026-11-03：「奎因参考LOL高手啊 这个要修的」）：11-02 夜里她唯一的一场 8 条命一次都没骑过——
//! 副本的大招只叫来华洛骑上，游戏的 AI 读不到这一招有什么用（数据里只有一个 buff），从来不按。照英雄联盟高手的用法，钩子
//! `league_quinn:ride_ai` 替 AI 按：
//!
//! - **赶路**：游戏的 AI 让她走去 `TRAVEL` 以外的地方（回城后回线上、去别的路游走、去支援打团），身边 `FIGHT_R` 内又没有敌方
//!   英雄（骑着挨一下打就会落地，交战中不骑）；
//! - **追残血**：`CHASE_R` 内有生命不到 `CHASE_LOW` 的敌方英雄，他在她的攻击距离外，她自己生命不低于 `MIN_HP`，身边没有别的
//!   敌方英雄：骑过去，骑着时游戏的 AI 想走开或打别人就改成打他，落地（这一下普攻）施放鹰翼天翔。
//!
//! 回城时、已经骑着、正在出招、大招没好（冷却或没解锁）时不按。副本的大招射程是全图（build_quinn 的 `r_ride_range`），
//! 哪里都按得出来；按的目标只是让游戏收下这个输入（骑乘不朝它冲）。日志 `RIDE AI`（赶路 / 追谁）、`CHASE`（骑着改打他）。
//!
//! 0.4.2（11-03 夜里的日志：一次启动 8 场、她骑了 14 次，`RIDE AI` / `CHASE` 0 次——全是游戏的 AI 自己按的 R，
//! `RIDE over after 1 ticks, 0 ridden`，别的 6 / 7 / 7 tick 就落地，打着打着就按）：
//! - 赶路的 R 对着**看得见的**敌方英雄按（游戏的 AI 自己按 R 时就用它的目标）：0.4.1 取实体表里第一个活着的敌方英雄，
//!   赶路时他多半在战争迷雾里，引擎不收这个输入，钩子一声不响地放弃了；引擎不收、或者一个看得见的都没有，记一行
//!   `RIDE REFUSED`（一串只记一行）。
//! - 游戏的 AI 自己按的 R 只在 `plan` 说该骑时放出去（照钩子的目标骑），不然不放（`R HELD`，tryndamere_rage 的
//!   `UltPlan::Hold`）：AI 的目标在 `FIGHT_R` 内就打他，不然接着走 AI 上一次让她走的路，再不然打 AI 的目标（走过去），
//!   都没有就站一下。
//!
//! 0.5.0（11-04 夜里的日志：一次启动 16 场预演，**一次 R 都没有**——钩子按的 40 次 `RIDE AI` 全被引擎拒收，目标都在
//! 100061–179834 外；AI 自己的 R 又全被 0.4.2 拦下）：副本的大招射程写着全图，引擎却不收 100000 外的 `Targeting` 输入
//! （11-03 那次 57475 的收了；死歌全图的 R 是 `EnemyChampionRecentlyAttacked`，收）。副本的大招改成**不指定目标的施法**
//! （`casting_type: None`，千珏、加里奥大招的写法，游戏的 AI 在全图任何距离都放得出），钩子按 R 不带目标——赶路时身边
//! 一个看得见的敌方英雄都没有也按得出来（以前要有人在视野里）。`RIDE REFUSED` 记目标（或最近的敌方英雄）离她多远；
//! 钩子的 R 一旦被引擎拒收，这条命里游戏 AI 自己的 R 不再拦（`R LET`）——它按的至少骑得上。
//!
//! 0.5.1：不指定目标的大招，游戏的 AI 按 R 的输入里也就没有人，`R HELD` 拿不到「AI 的目标」——交战中它每次想放 R（留着的
//! R 它每 4 tick 再按一次），她都改成走向 AI 上一次让她走的地方或站着，不打人。现在没有目标时用 `FIGHT_R` 内看得见的
//! 最近的敌方英雄顶上（[`hold_target`]，千珏附加包的做法）：交战中照样打人；交战外接着走路或站一下。
//!
//! 0.6.0（用户 2026-11-20：「还有修复奎因释放大招的逻辑 一般来说有大招后都开了大招去线上的 现在没有这种逻辑的 还有开大招
//! 赶路救队友之类的」）。11-19 晚上那次启动只有游戏自己的 AI（运营钩子没装），日志里钩子按的 42 行 `RIDE AI` 只有 2 行是
//! 赶路，40 行是追残血；你看的那场（m=6778）她回城 11 次、阵亡 3 次，整场只骑过一次，可大招冷却才 40 秒。游戏的 AI 带人
//! 走路是一段一段走路点（奥莉安娜附加包量过：线上一步走到 15–38k 外的固定路点），0.5.x 只看这一步，出门回线从来不到
//! `TRAVEL`，所以出泉水从来不骑：两份日志里赶路骑上的 14 次（她都是上单）没有一次是回上路，9 次是 AI 一步就让她走到小龙坑、
//! 大龙坑旁边，别的去中路、野区。队友在远处打架，没有一条规则管。
//! - **去线上**（[`lane_trip`]）：她那条路的前线是自家还站着的、这条路上离自家水晶最远的塔（[`lane_front`]，辅助算下路）。
//!   她在前线后面、游戏的 AI 这一步让她朝前线走、离前线还有 `TRAVEL` 以上，就骑——量的是到前线这一趟，不是 AI 的一步。
//!   复活、回城后一出泉水就骑；出门时大招还在冷却、路上好了，离前线还够远也骑。
//! - **去救队友**（[`help_target`]）：离她 `HELP_MIN`..`HELP_MAX` 的我方英雄在打架（`ALLY_FIGHT` 内有敌方英雄），或者残血被追
//!   （生命不到 `HELP_LOW`、`CHASED_R` 内有敌方英雄），不在敌方塔下，那边敌方的人不比我方（加上她）多；她自己生命不低于
//!   `MIN_HP`、身边没有敌方英雄：骑过去。骑着时游戏的 AI 想走开、打小兵野怪、放技能就改成朝他走（[`keeps_course`]）——骑着
//!   一出手就落地，路上打一下小兵大招就白交了；她身边有敌方英雄了、到了、他倒了或者架打完了（[`help_over`]）就交给游戏的
//!   AI 打（落地那一下施放鹰翼天翔，6 秒到了也落地）。
//! - 追残血、交战中不骑、回城 / 出招 / 已经骑着 / 大招没好不按，这些照旧；追残血排在最前，救人其次，去线上、赶路最后。
//! - 你看的那场（画面、观战、回放）的行每条都记：以前整次启动每种行只记前 40 行，后台预演先把它用完，你看的那场一行都没有。
//!   出泉水没骑也记一行 `OUT ON FOOT`（大招还要冷却多久，或者好着为什么没骑；大招还没解锁时不记）。

use mod_api_stable::*;

use super::{counted_on, dist, head, on_screen, wlog, Pt, ID, RIDE, R_RIDE_T};

/// 在 league_ult_press（100）之后。
pub const PRIORITY: i32 = 110;
/// 这么远的一趟就骑上华洛（6 秒、移速 +80%，比走过去快一倍）：游戏的 AI 一步让她走这么远，或者离她那条路的前线还有这么远。
pub const TRAVEL: f64 = 200_000.0;
/// 这么近以内有敌方英雄就是在交战：不骑（骑着挨一下就落地）。
pub const FIGHT_R: f64 = 70_000.0;
/// 追残血：这么远以内、生命不到 `CHASE_LOW` 的敌方英雄，她自己生命不低于 `MIN_HP`。
pub const CHASE_R: f64 = 180_000.0;
pub const CHASE_LOW: f64 = 0.35;
pub const MIN_HP: f64 = 0.5;
/// 她的攻击距离（build_quinn.P 的 atk_range，测试核对）：够得着的就不用骑。
pub const ATTACK_R: f64 = 52_500.0;
/// 追残血至少要这么远（0.4.1）：上鸟要引导半秒，近一点的走两步就打得到。11-03 13:05 那局她对 57475 外的残血上鸟，引导完人已
/// 进了射程，骑上 3 tick 就普攻落地放了鹰翼天翔，一步没骑，大招白交（用户：「奎因大招正常了吗」）。
pub const CHASE_MIN: f64 = 100_000.0;
/// 自家基地：离自家水晶这么近以内（原版图：基地的两座塔离水晶 81000 左右，泉水还在里面，最近的二塔在 200000 外）。
pub const BASE_R: f64 = 150_000.0;
/// 中路的塔离两座水晶的连线不到这么远（原版图：中路的塔就在线上，上下两路的二塔离它 270000）。
pub const MID_BAND: f64 = 120_000.0;
/// AI 这一步至少让她往那边近这么多才算朝那边走（走到自己脚下是站着）。
pub const STEP_MIN: f64 = 1_000.0;
/// 去救队友：他离她这么远以外（近的走过去：上鸟要引导半秒，骑过去也快不了几步）、这么远以内（骑过去 4 秒上下，架还没打完）。
pub const HELP_MIN: f64 = 150_000.0;
pub const HELP_MAX: f64 = 450_000.0;
/// 队友这么近有敌方英雄就是在打架（崔斯特大招的 TF_FIGHT）；生命不到 `HELP_LOW` 时这么近有敌方英雄就是被追。
pub const ALLY_FIGHT: f64 = 50_000.0;
pub const HELP_LOW: f64 = 0.4;
pub const CHASED_R: f64 = 90_000.0;
/// 那边的人数：队友身边这么近的敌方英雄，不比我方英雄（含他）再加上她多才去。
pub const ODDS_R: f64 = 70_000.0;
/// 敌方塔的攻击范围（大约，league_ult_press 的 TOWER_REACH）：在敌方塔下的架不去。
pub const TOWER_REACH: f64 = 75_000.0;
/// 骑着去救：离他这么近就算到了，交给游戏的 AI 打。
pub const ARRIVE_R: f64 = 60_000.0;
/// 骑着去救：他身边这么近一个敌方英雄都没有了，就是架打完了（或者他跑掉了）。
pub const FIGHT_OVER: f64 = 100_000.0;
/// 一 tick 挪了这么多以上是回城传送回家（她自己最快一 tick 挪 4000，E 的冲刺）。
pub const TELEPORT: f64 = 50_000.0;
/// 这一局的水晶、塔没找到时，隔这么多 tick 再找一次。
pub const FIELD_RETRY: usize = 600;

/// 看得见的一个敌方英雄：位置和生命比例。
#[derive(Clone, Copy, Debug)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub hp: f64,
}

/// 一个活着的我方英雄（不含她）：位置和生命比例。
#[derive(Clone, Copy, Debug)]
pub struct Mate {
    pub id: usize,
    pub at: Pt,
    pub hp: f64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Plan {
    /// 赶路：游戏的 AI 要她走 `far` 那么远。
    Travel { far: f64 },
    /// 追残血：骑去打他。
    Chase { target: usize, d: f64 },
    /// 去线上（0.6.0）：离她那条路的前线 `front` 还有 `trip` 远（AI 这一步只是朝那边走一小段）。
    Lane { trip: f64, front: Pt },
    /// 去救队友（0.6.0）：他离她 `d` 远，身边有 `foes` 个敌方英雄。
    Help { mate: usize, d: f64, foes: usize },
}

/// `plan` 看的场面。
#[derive(Clone, Copy, Debug)]
pub struct Scene<'a> {
    pub me: Pt,
    /// 她的生命比例。
    pub hp: f64,
    /// 游戏的 AI 最近一次让她走去的地方。
    pub walk_to: Option<Pt>,
    /// 看得见、选得中的敌方英雄。
    pub foes: &'a [Foe],
    /// 活着的我方英雄（不含她）。
    pub mates: &'a [Mate],
    /// 自家水晶和她那条路的前线（打野、这条路的塔都倒了、找不到水晶时没有）。
    pub lane: Option<(Pt, Pt)>,
    /// 敌方还站着的塔。
    pub towers: &'a [Pt],
}

/// 这一 tick 该不该骑、为什么。先看追残血；交战中不骑；再看救队友、去线上，最后是 AI 一步就走很远的赶路。
pub fn plan(s: &Scene<'_>) -> Option<Plan> {
    let me = s.me;
    if s.hp >= MIN_HP {
        let low = s
            .foes
            .iter()
            .filter(|f| f.hp <= CHASE_LOW)
            .map(|f| (f.id, dist(me, f.at)))
            .filter(|f| f.1 >= CHASE_MIN && f.1 <= CHASE_R)
            .min_by(|a, b| a.1.total_cmp(&b.1));
        if let Some((target, d)) = low {
            if s.foes.iter().all(|o| o.id == target || dist(me, o.at) > FIGHT_R) {
                return Some(Plan::Chase { target, d });
            }
        }
    }
    if s.foes.iter().any(|f| dist(me, f.at) <= FIGHT_R) {
        return None;
    }
    if s.hp >= MIN_HP {
        if let Some((mate, d, foes)) = help_target(me, s.mates, s.foes, s.towers) {
            return Some(Plan::Help { mate, d, foes });
        }
    }
    let walk = s.walk_to?;
    if let Some((nexus, front)) = s.lane {
        if let Some(trip) = lane_trip(me, walk, nexus, front) {
            return Some(Plan::Lane { trip, front });
        }
    }
    let far = dist(me, walk);
    (far >= TRAVEL).then_some(Plan::Travel { far })
}

/// 去线上的这一趟有多远（0.6.0）：她在前线后面（离自家水晶比前线近），游戏的 AI 这一步（`hop`）让她朝前线走（走到的地方
/// 离前线比她现在近 `STEP_MIN` 以上），离前线还有 `TRAVEL` 以上——这一趟就是到前线这么远。AI 一步只走一小段路点，只看这一步
/// 的话，出门回线从来不够骑。
pub fn lane_trip(me: Pt, hop: Pt, nexus: Pt, front: Pt) -> Option<f64> {
    let trip = dist(me, front);
    let behind = dist(me, nexus) < dist(front, nexus);
    let toward = dist(hop, front) + STEP_MIN <= trip;
    (behind && toward && trip >= TRAVEL).then_some(trip)
}

/// 一座塔在哪条路上：基地里的（离自家水晶 `BASE_R` 内）不算；离两座水晶的连线不到 `MID_BAND` 是中路；和地图原点 (0, 0) 那个
/// 角在连线同一边的是上路，另一边是下路（英雄联盟的图：蓝方在左下、红方在右上，上路过左上角；原版图的上路一塔在
/// (48000, 272000)，league_camille_wall 也是这么写的）。
pub fn tower_lane(nexus: Pt, enemy: Pt, t: Pt) -> Option<LaneV1> {
    if dist(t, nexus) <= BASE_R {
        return None;
    }
    let (ux, uy) = (enemy.0 - nexus.0, enemy.1 - nexus.1);
    let l = (ux * ux + uy * uy).sqrt();
    if l < 1.0 {
        return None;
    }
    let side = |p: Pt| (ux * (p.1 - nexus.1) - uy * (p.0 - nexus.0)) / l;
    let s = side(t);
    if s.abs() <= MID_BAND {
        return Some(LaneV1::Mid);
    }
    Some(if (s < 0.0) == (side((0.0, 0.0)) < 0.0) { LaneV1::Top } else { LaneV1::Bottom })
}

/// 她那条路的前线（0.6.0）：自家还站着的塔（`mine`）里，这条路上离自家水晶最远的那座。辅助算下路；打野没有前线。
pub fn lane_front(lane: LaneV1, nexus: Pt, enemy: Pt, mine: &[Pt]) -> Option<Pt> {
    let lane = match lane {
        LaneV1::Support => LaneV1::Bottom,
        LaneV1::Jungle => return None,
        l => l,
    };
    mine.iter()
        .copied()
        .filter(|t| tower_lane(nexus, enemy, *t) == Some(lane))
        .max_by(|a, b| dist(*a, nexus).total_cmp(&dist(*b, nexus)))
}

/// 去救谁（0.6.0）：离她 `HELP_MIN`..`HELP_MAX` 的我方英雄，`ALLY_FIGHT` 内有敌方英雄（在打架），或者生命不到 `HELP_LOW`、
/// `CHASED_R` 内有敌方英雄（被追）；他不在敌方塔下（`TOWER_REACH`）；他身边 `ODDS_R` 内的敌方英雄不比那里的我方英雄（含他）
/// 加上她多。挑离她最近的：(队友, 离她多远, 他身边几个敌方英雄)。她自己在不在交战、血够不够由 `plan` 看。
pub fn help_target(me: Pt, mates: &[Mate], foes: &[Foe], towers: &[Pt]) -> Option<(usize, f64, usize)> {
    mates
        .iter()
        .filter_map(|m| {
            let d = dist(me, m.at);
            if !(HELP_MIN..=HELP_MAX).contains(&d) {
                return None;
            }
            let fight = foes.iter().any(|f| dist(m.at, f.at) <= ALLY_FIGHT);
            let chased = m.hp < HELP_LOW && foes.iter().any(|f| dist(m.at, f.at) <= CHASED_R);
            if !(fight || chased) || towers.iter().any(|t| dist(m.at, *t) <= TOWER_REACH) {
                return None;
            }
            let theirs = foes.iter().filter(|f| dist(m.at, f.at) <= ODDS_R).count();
            let ours = mates.iter().filter(|o| dist(m.at, o.at) <= ODDS_R).count() + 1;
            (theirs <= ours).then_some((m.id, d, theirs))
        })
        .min_by(|a, b| a.1.total_cmp(&b.1))
}

/// 游戏的 AI 这一 tick 的命令（骑着去救队友时看它照不照放）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Order {
    /// 没下命令：上一个命令接着走。
    Nothing,
    /// 走去这里。
    Walk(Pt),
    /// 普攻或技能，对着一个敌方英雄。
    AtChampion,
    /// 回城、大招。
    Keep,
    /// 别的：对小兵、野怪、塔出手，或者朝一个方向、一个地方放技能。
    Other,
}

impl Order {
    fn name(self) -> &'static str {
        match self {
            Order::Nothing => "silence",
            Order::Walk(_) => "walk elsewhere",
            Order::AtChampion => "attack on a champion",
            Order::Keep => "recall or ult",
            Order::Other => "attack or cast on something else",
        }
    }
}

/// 骑着去救队友（在 `mate`）时，游戏 AI 的这个命令照放吗（0.6.0）：朝他走的（走到的地方离他比她近）、对敌方英雄出手的
/// （它自己开打，落地那一下施放鹰翼天翔）、回城、没下命令都照放；别的——走开、站着、打小兵野怪塔、对一个方向放技能——改成
/// 朝他走。
pub fn keeps_course(me: Pt, mate: Pt, order: Order) -> bool {
    match order {
        Order::Walk(w) => dist(w, mate) + STEP_MIN <= dist(me, mate),
        Order::Other => false,
        Order::Nothing | Order::AtChampion | Order::Keep => true,
    }
}

/// 骑着去救的这一趟完了没有、为什么（0.6.0）：他倒了；她身边 `FIGHT_R` 内有敌方英雄了（开打）；到了（离他 `ARRIVE_R` 内）；
/// 他身边 `FIGHT_OVER` 内一个敌方英雄都没有了（打完了）。完了就交给游戏的 AI。
pub fn help_over(me: Pt, mate: Option<Pt>, foes: &[Foe]) -> Option<&'static str> {
    let Some(m) = mate else { return Some("he is down") };
    if foes.iter().any(|f| dist(me, f.at) <= FIGHT_R) {
        Some("in the fight")
    } else if dist(me, m) <= ARRIVE_R {
        Some("there")
    } else if !foes.iter().any(|f| dist(m, f.at) <= FIGHT_OVER) {
        Some("the fight is over")
    } else {
        None
    }
}

/// 游戏的 AI 是不是正在让她回城（league_graves 的写法）：下了回城命令，之后没有新命令时回城还在走。
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// 一串连着的只记一行（league_ult_press 的 `ORDER_FRESH`）：游戏的 AI 每 4 tick 下一次命令，留着的 R 它每次都再按。
pub const ORDER_FRESH: usize = 30;

/// A line at `tick` starts a burst: none of its kind in the `ORDER_FRESH` ticks before (`last`: that kind's last tick;
/// a tick before it is another match).
pub fn new_burst(last: Option<usize>, tick: usize) -> bool {
    last.is_none_or(|t0| tick < t0 || tick > t0 + ORDER_FRESH)
}

/// 赶路的 R 是朝着谁的（0.4.2；0.5.0 起只为日志——R 不带目标）：游戏的 AI 自己按 R 时它的目标（它只点看得见的），不然
/// 离她最近的看得见的敌方英雄（`foes` 只收看得见、选得中的）；一个都没有就没有。
pub fn travel_target(me: Pt, ai_target: Option<usize>, foes: &[Foe]) -> Option<usize> {
    ai_target
        .filter(|t| foes.iter().any(|f| f.id == *t))
        .or_else(|| foes.iter().min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at))).map(|f| f.id))
}

/// 游戏的 AI 自己按 R、`plan` 又不骑时她改做什么（0.4.2）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Instead {
    Attack(usize),
    Walk(Pt),
    Stand,
}

/// AI 的目标（`target`：实体和位置，看不见就没有）在 `FIGHT_R` 内就打他；不然接着走 AI 上一次让她走的路（`walk_to`，
/// 已经走到了不算）；再不然打 AI 的目标（走过去）；都没有就站一下。
pub fn instead(me: Pt, target: Option<(usize, Pt)>, walk_to: Option<Pt>) -> Instead {
    match (target, walk_to) {
        (Some((t, at)), _) if dist(me, at) <= FIGHT_R => Instead::Attack(t),
        (_, Some(w)) if dist(me, w) > 1_000.0 => Instead::Walk(w),
        (Some((t, _)), _) => Instead::Attack(t),
        _ => Instead::Stand,
    }
}

/// `R HELD` 时的「AI 的目标」（0.5.1）：AI 自己按的 R 的目标（看得见的）；没有就是 `FIGHT_R` 内看得见的最近的敌方英雄
/// （千珏附加包的做法）。0.5.0 起副本的大招不指定目标，AI 按 R 的输入里没有人，`instead` 拿到的目标总是空的——交战中
/// AI 每次想放 R，她都改成走向 AI 上一次让她走的地方或站着，不打人。交战外不找人顶上：接着走路或站一下，不朝 AI 没挑的
/// 远处英雄走。
pub fn hold_target(me: Pt, ai_seen: Option<(usize, Pt)>, foes: &[Foe]) -> Option<(usize, Pt)> {
    ai_seen.or_else(|| {
        foes.iter()
            .filter(|f| dist(me, f.at) <= FIGHT_R)
            .min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at)))
            .map(|f| (f.id, f.at))
    })
}

/// 正在出招（游戏记成 `Animation`）或被强制位移：不替 AI 按，按了会打断。
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];

fn busy(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| BUSY.iter().any(|k| k.code() == c.kind)))
}

fn riding(e: &StableEntity<'_, '_>) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| &b.name_buf[..b.name_len.min(BUFF_NAME_CAP)] == RIDE.as_bytes())
}

fn at(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn hp_share(e: &StableEntity<'_, '_>) -> f64 {
    e.hp().0 as f64 / e.hp().1.max(1) as f64
}

/// 看得见、选得中的敌方英雄和活着的我方英雄（不含她）。只看英雄表（0.6.0：以前每 tick 把这局所有实体——小兵、野怪、投射物——
/// 看一遍，league_ult_press 量过这样很费时间）。
fn champions(sim: &StableSim<'_>, me: &StableEntity<'_, '_>) -> (Vec<Foe>, Vec<Mate>) {
    let (team, mid) = (me.team(), me.id());
    let (mut foes, mut mates) = (Vec::new(), Vec::new());
    for i in 0..sim.champion_count() {
        let id = sim.champion_id_at(i);
        if id == mid {
            continue;
        }
        let Some(u) = sim.get_entity(id) else { continue };
        if !u.is_alive() {
            continue;
        }
        if u.team() == team {
            mates.push(Mate { id, at: at(&u), hp: hp_share(&u) });
        } else if u.is_targetable() && sim.is_visible(team, id) {
            foes.push(Foe { id, at: at(&u), hp: hp_share(&u) });
        }
    }
    (foes, mates)
}

/// 这一局的地图：自家和敌方的水晶，两边的塔（实体、位置；之后每 tick 只看还在不在：塔不会动、不会复活）。
#[derive(Clone, Debug, Default)]
struct Field {
    nexus: Pt,
    enemy: Pt,
    mine: Vec<(usize, Pt)>,
    theirs: Vec<(usize, Pt)>,
}

/// 一局找一次：把这局的实体看一遍，找两边的水晶和还站着的塔。找不到水晶（实体种类要游戏 ABI 10 以上）就没有。
fn find_field(sim: &StableSim<'_>, team: usize) -> Option<Field> {
    let (mut nexus, mut enemy) = (None, None);
    let mut f = Field::default();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        let mine = e.team() == team;
        match e.kind() {
            Some(EntityKindV1::Nexus) if mine => nexus = Some(at(&e)),
            Some(EntityKindV1::Nexus) => enemy = Some(at(&e)),
            Some(EntityKindV1::Tower) if e.is_alive() => {
                if mine { f.mine.push((e.id(), at(&e))) } else { f.theirs.push((e.id(), at(&e))) }
            }
            _ => {}
        }
    }
    f.nexus = nexus?;
    f.enemy = enemy?;
    Some(f)
}

/// 日志里的路名。
fn lane_name(lane: Option<LaneV1>) -> &'static str {
    match lane {
        Some(LaneV1::Top) => "Top",
        Some(LaneV1::Jungle) => "Jungle",
        Some(LaneV1::Mid) => "Mid",
        Some(LaneV1::Bottom) => "Bottom",
        Some(LaneV1::Support) => "Support (bottom)",
        None => "unknown",
    }
}

/// 还站着的塔的位置。
fn standing(sim: &StableSim<'_>, towers: &[(usize, Pt)]) -> Vec<Pt> {
    towers.iter().filter(|(id, _)| sim.get_entity(*id).is_some_and(|e| e.is_alive())).map(|t| t.1).collect()
}

/// 游戏 AI 的这个命令是什么（骑着去救时看）。
fn order_of(sim: &StableSim<'_>, team: usize, base: Option<InputV1>) -> Order {
    let Some(b) = base else { return Order::Nothing };
    match InputKindV1::from_code(b.kind) {
        Some(InputKindV1::Move) => Order::Walk((b.x as f64, b.y as f64)),
        Some(InputKindV1::Return | InputKindV1::Ult) => Order::Keep,
        Some(InputKindV1::Attack | InputKindV1::Skill | InputKindV1::Skill2) => {
            let on_champion = (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target))
                .then_some(b.target.target_id)
                .and_then(|t| sim.get_entity(t))
                .is_some_and(|e| e.is_champion() && e.team() != team);
            if on_champion { Order::AtChampion } else { Order::Other }
        }
        None => Order::Nothing,
    }
}

/// 骑着追的人、骑着去救的人：(实体, 到这个 tick 为止)。
type Chase = Option<(usize, usize)>;

/// 钩子的 R 被引擎拒收过（这条命里）：游戏 AI 自己的 R 该不该拦（0.5.0——拦了就一次都骑不上，11-04 夜里 16 场 0 次 R）。
pub fn let_ais_r_through(refused_since: Option<usize>) -> bool {
    refused_since.is_some()
}

#[derive(Clone, Default)]
pub struct RideAi {
    /// 游戏的 AI 最近一次让她走去的地方（这条命里，回城传送回家就作废）。
    walk_to: Option<Pt>,
    /// 游戏的 AI 最近的一个命令是走路（之后下了普攻、技能就不是了）：去线上、赶路只看正在走的路。
    walking: bool,
    recalling: bool,
    chase: Chase,
    /// 骑着去救的队友（0.6.0）。
    help: Chase,
    alive: bool,
    /// 这条命的实体（复活是一个新实体）。
    me_id: Option<usize>,
    /// 上一 tick 她在哪（一 tick 挪了 `TELEPORT` 以上是回城传送回家）。
    last_at: Option<Pt>,
    /// 上一次 think 的 tick（变小了是新的一局）。
    last_tick: usize,
    /// 每种行最近一次的 tick（`new_burst`：一串只记一行）。
    lines: Vec<(&'static str, usize)>,
    /// 钩子的 R 从这一 tick 起被引擎拒收过（这条命里；骑成一次就清掉）。
    refused_since: Option<usize>,
    /// 这一局的水晶和塔（一局找一次），没找到时下一次找的 tick。
    field: Option<Field>,
    field_next: usize,
    /// 上一 tick 她在不在自家基地里；这次进基地以后按过 R 没有（出泉水没骑记一行）。
    in_base: bool,
    rode_out: bool,
}

/// 这一 tick 钩子要做的。
enum Todo {
    Nothing,
    /// 骑上华洛（按 R，不带目标）；`target`：朝着谁（只为日志和追击），`d`：他（或最近的敌方英雄）离她多远；`chase` /
    /// `help`：追谁、救谁，到哪一 tick。
    Ride { target: Option<usize>, d: f64, line: String, chase: Chase, help: Chase },
    /// 骑着追残血：改成打他。
    Chase(InputV1, String),
    /// 骑着去救队友：改成朝他走。
    Help(Pt, String),
    /// 只记一行。
    Note(&'static str, String),
    /// 游戏的 AI 自己按的 R 不放：改做 `Instead`（`line` 说为什么）。
    Hold(Instead, String),
    /// 游戏的 AI 自己按的 R 照放（钩子的 R 被拒收过：它的至少骑得上），记一行。
    Let(String),
}

impl RideAi {
    /// One more line of `kind` at `tick`: true when it starts a burst (`new_burst`), the line to be written.
    fn burst(&mut self, kind: &'static str, tick: usize) -> bool {
        let last = self.lines.iter().find(|(k, _)| *k == kind).map(|&(_, t)| t);
        self.lines.retain(|(k, _)| *k != kind);
        self.lines.push((kind, tick));
        new_burst(last, tick)
    }

    /// `line` (a `kind` line) once a burst, through the launch-wide count (every one from the match on screen).
    fn note(&mut self, kind: &'static str, tick: usize, line: &str, shown: bool) {
        if self.burst(kind, tick) {
            if let Some(k) = counted_on(kind, shown) {
                wlog(format!("{line} #{k}"));
            }
        }
    }
}

impl StablePlayerAi for RideAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ride_ai")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let lane = ctx.lane();
        if tick < self.last_tick {
            // 新的一局（tick 倒回去了）：上一局的地图、这条命、记过的行都不算
            *self = RideAi::default();
        }
        self.last_tick = tick;
        let was = base.and_then(|b| InputKindV1::from_code(b.kind));
        // the game's AI pressing this R itself (0.4.2): it goes out only when plan() says ride
        let ai_ult = was == Some(InputKindV1::Ult);
        let ai_target = base.filter(|_| ai_ult).and_then(|b| {
            (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
        });
        self.recalling = still_recalling(self.recalling, base);
        let (todo, here, shown, out_line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                self.alive = false;
                return None;
            }
            let here = at(&me);
            if !self.alive || self.me_id != Some(me.id()) {
                // 新的一条命（复活是一个新实体）：上一条命走的路、追的人、救的人都不算了
                self.alive = true;
                self.me_id = Some(me.id());
                self.walk_to = None;
                self.walking = false;
                self.chase = None;
                self.help = None;
                self.refused_since = None;
                self.last_at = None;
                self.rode_out = false;
            }
            if self.last_at.is_some_and(|p| dist(p, here) >= TELEPORT) {
                // 回城传送回家了：AI 上一次让她走去的地方是回城前的
                self.walk_to = None;
                self.walking = false;
            }
            self.last_at = Some(here);
            if let Some(b) = base {
                self.walking = was == Some(InputKindV1::Move);
                if self.walking {
                    self.walk_to = Some((b.x as f64, b.y as f64));
                }
            }
            let shown = on_screen(&sim);
            let line = head(&sim, me.id());
            let team = me.team();
            if self.field.is_none() && tick >= self.field_next {
                self.field_next = tick + FIELD_RETRY;
                self.field = find_field(&sim, team);
            }
            let (foes, mates) = champions(&sim, &me);
            let cd = me.cooldown(SkillSlotV1::Ult);
            let ready = cd.is_some_and(|c| c.unlocked && c.remaining == 0);
            let on_valor = riding(&me);
            // 进出自家基地：出泉水时没骑上记一行（0.6.0）
            let in_base = self.field.as_ref().is_some_and(|f| dist(here, f.nexus) <= BASE_R);
            if in_base && !self.in_base {
                self.rode_out = false;
            }
            let walked_out = self.in_base && !in_base && !on_valor && !self.rode_out;
            self.in_base = in_base;
            let mut out_line = None;
            // the AI's target where she can see it (an attack on it, if the AI's R is held)
            let ai_seen = ai_target
                .and_then(|t| sim.get_entity(t))
                .filter(|e| e.is_alive() && e.is_targetable() && sim.is_visible(team, e.id()))
                .map(|e| (e.id(), at(&e)));
            let todo = if on_valor {
                if self.recalling || busy(&me) {
                    Todo::Nothing
                } else if let Some((t, until)) = self.chase {
                    // on Valor after a low one: what the game's AI wants elsewhere becomes an attack on him (the landing's
                    // Skystrike comes with it)
                    let prey = sim.get_entity(t).filter(|e| e.is_alive() && e.is_targetable() && sim.is_visible(team, t));
                    if tick > until || prey.is_none() {
                        self.chase = None;
                        Todo::Nothing
                    } else if base.is_none()
                        || base.is_some_and(|b| was == Some(InputKindV1::Attack) && b.target.target_id == t)
                    {
                        Todo::Nothing
                    } else {
                        let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                        Todo::Chase(attack, format!("{line} CHASE: on Valor after #{t}"))
                    }
                } else if let Some((m, until)) = self.help {
                    // 骑着去救队友：朝他走，路上不打小兵、不乱放技能；开打了、到了、他倒了、架打完了就交给游戏的 AI
                    let mate = sim.get_entity(m).filter(|e| e.is_alive()).map(|e| at(&e));
                    let over = if tick > until { Some("the ride's time is up") } else { help_over(here, mate, &foes) };
                    match (over, mate) {
                        (None, Some(to)) => {
                            let order = order_of(&sim, team, base);
                            if keeps_course(here, to, order) {
                                Todo::Nothing
                            } else {
                                Todo::Help(to, format!("{line} HELP: on Valor to #{m} {:.0} away - the AI's {} turned into a \
                                                        walk to him", dist(here, to), order.name()))
                            }
                        }
                        (why, _) => {
                            self.help = None;
                            let left = mate.map_or("he is down".to_string(), |p| format!("#{m} {:.0} away", dist(here, p)));
                            Todo::Note("help_end", format!("{line} HELP OVER: {} ({left}) - the game's AI takes it from here",
                                                           why.unwrap_or("he is down")))
                        }
                    }
                } else {
                    Todo::Nothing
                }
            } else {
                if self.help.is_some_and(|(_, until)| tick > until) {
                    self.help = None;
                }
                let hp = hp_share(&me);
                let free = ready && !self.recalling && !busy(&me);
                // 她那条路的前线、敌方还站着的塔：大招好着、能按时才看（0.6.0）
                let (front, towers) = match (&self.field, free) {
                    (Some(f), true) => {
                        let mine = standing(&sim, &f.mine);
                        let front = lane.and_then(|l| lane_front(l, f.nexus, f.enemy, &mine)).map(|p| (f.nexus, p));
                        (front, standing(&sim, &f.theirs))
                    }
                    _ => (None, Vec::new()),
                };
                // 去线上、赶路只看 AI 正在走的路（它最近的命令是走路）
                let walk_now = self.walk_to.filter(|_| self.walking);
                let scene = Scene { me: here, hp, walk_to: walk_now, foes: &foes, mates: &mates, lane: front, towers: &towers };
                let planned = if free { plan(&scene) } else { None };
                let near = foes.iter().map(|f| dist(here, f.at)).fold(f64::INFINITY, f64::min);
                let walk_to = self.walk_to;
                let walk = |w: Option<Pt>| w.map_or("none".to_string(), |w| format!("{:.0}", dist(here, w)));
                // 比赛开头大招还没解锁时出门不记（每局都一样）
                let unlocked = cd.is_none_or(|c| c.unlocked);
                if walked_out && unlocked && planned.is_none() {
                    let why = match cd {
                        None => "R not readable".to_string(),
                        Some(c) if c.remaining > 0 => format!("R cooling {} more ticks", c.remaining),
                        Some(_) if !free => "R ready, recalling or casting".to_string(),
                        Some(_) => format!("R ready, no ride planned (the AI's walk {}, {}, nearest enemy champion {near:.0})",
                                           walk(walk_now),
                                           match front {
                                               Some((_, p)) => format!("the {} front {:.0} away", lane_name(lane), dist(here, p)),
                                               None => format!("no front for the {} lane", lane_name(lane)),
                                           }),
                    };
                    out_line = Some(format!("{line} OUT ON FOOT: out of the base without Valor - {why}"));
                }
                match planned {
                    Some(plan) => {
                        // the ride is a no-target cast (0.5.0): the prey, or the one the roam heads for, is for the log and
                        // the chase only - 0.4.2 pressed a Targeting R on a champion in sight and the engine took none
                        // beyond ~100000 (11-04 night: 40 RIDE AI, 40 REFUSED, 0 rides in 16 presims)
                        let target = match plan {
                            Plan::Chase { target, .. } => Some(target),
                            _ => travel_target(here, ai_target, &foes),
                        };
                        let d = target
                            .and_then(|t| foes.iter().find(|f| f.id == t))
                            .map_or(f64::NAN, |f| dist(here, f.at));
                        let seen = match target {
                            Some(t) => format!(", #{t} in sight {d:.0} away"),
                            None => ", no enemy champion in sight".to_string(),
                        };
                        let (why, chase, help) = match plan {
                            Plan::Travel { far } => (format!("a walk of {far:.0} (to {:?}){seen}", self.walk_to), None, None),
                            Plan::Chase { target, d } => {
                                (format!("after #{target}, {d:.0} away and low"), Some((target, tick + R_RIDE_T + 40)), None)
                            }
                            Plan::Lane { trip, front } => (
                                format!("to lane{}: {trip:.0} to the {} front ({:.0}, {:.0}), the AI's walk {}{seen}",
                                        if in_base { " out of the base" } else { "" }, lane_name(lane), front.0, front.1,
                                        walk(walk_now)),
                                None,
                                None,
                            ),
                            Plan::Help { mate, d, foes: n } => (
                                format!("to help #{mate} {d:.0} away ({:.0}% hp, {n} enemy champions on him)",
                                        mates.iter().find(|m| m.id == mate).map_or(f64::NAN, |m| m.hp * 100.0)),
                                None,
                                Some((mate, tick + R_RIDE_T + 40)),
                            ),
                        };
                        Todo::Ride { target, d, line: format!("{line} RIDE AI: {why}"), chase, help }
                    }
                    None if ai_ult && let_ais_r_through(self.refused_since) => {
                        Todo::Let(format!("{line} R LET: the AI's own R goes out, the hook's rides refused since t={}",
                                          self.refused_since.unwrap_or(0)))
                    }
                    None if ai_ult => {
                        let why = if !ready {
                            "R not ready".to_string()
                        } else if self.recalling || busy(&me) {
                            "recalling or casting".to_string()
                        } else {
                            format!("no ride planned (nearest enemy champion {near:.0}, the walk {})", walk(walk_to))
                        };
                        // the AI's R carries no target since 0.5.0 (a None cast): the nearest one in sight stands in
                        let target = hold_target(here, ai_seen, &foes);
                        Todo::Hold(instead(here, target, self.walk_to), format!("{line} R HELD: the AI's own R, {why}"))
                    }
                    None => Todo::Nothing,
                }
            };
            (todo, here, shown, out_line)
        };
        let out = match todo {
            Todo::Nothing => None,
            Todo::Note(kind, line) => {
                self.note(kind, tick, &line, shown);
                None
            }
            Todo::Chase(input, line) => {
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                self.note("chase", tick, &line, shown);
                Some(input)
            }
            Todo::Help(to, line) => {
                self.note("help", tick, &line, shown);
                Some(InputV1::move_to(to.0.max(0.0) as u64, to.1.max(0.0) as u64))
            }
            Todo::Ride { target, d, line, chase, help } => {
                let input = InputV1::action(InputKindV1::Ult, InputTargetV1::NONE);
                if ctx.is_valid_input(&input) {
                    self.refused_since = None;
                    self.chase = chase;
                    self.help = help;
                    self.rode_out |= self.in_base;
                    self.note("ride_ai", tick, &line, shown);
                    Some(input)
                } else {
                    // the game took no R: the AI's own R (a ride all the same) goes out, else nothing; from here on the
                    // AI's own R is never held in this life (0.5.0)
                    self.refused_since.get_or_insert(tick);
                    self.note("refused", tick, &format!("{line} -> RIDE REFUSED: the game took no R ({}; the AI's own R {})",
                                                        match target {
                                                            Some(t) => format!("#{t} {d:.0} away"),
                                                            None => "nobody in sight".to_string(),
                                                        },
                                                        if ai_ult { "kept" } else { "let through from now on" }), shown);
                    None
                }
            }
            Todo::Let(line) => {
                self.note("r_let", tick, &line, shown);
                None
            }
            Todo::Hold(what, line) => {
                let stand = InputV1::move_to(here.0.max(0.0) as u64, here.1.max(0.0) as u64);
                let walk = |w: Pt| InputV1::move_to(w.0.max(0.0) as u64, w.1.max(0.0) as u64);
                let (input, did) = match what {
                    Instead::Attack(t) => {
                        let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                        match (ctx.is_valid_input(&attack), self.walk_to) {
                            (true, _) => (attack, format!("attacking #{t} instead")),
                            (false, Some(w)) => (walk(w), "walking on instead".to_string()),
                            (false, None) => (stand, "standing instead".to_string()),
                        }
                    }
                    Instead::Walk(w) => (walk(w), "walking on instead".to_string()),
                    Instead::Stand => (stand, "standing instead".to_string()),
                };
                self.note("r_held", tick, &format!("{line} - {did}"), shown);
                Some(input)
            }
        };
        if let Some(line) = out_line {
            self.note("out_on_foot", tick, &line, shown);
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn foe(id: usize, at: Pt, hp: f64) -> Foe {
        Foe { id, at, hp }
    }

    fn mate(id: usize, at: Pt, hp: f64) -> Mate {
        Mate { id, at, hp }
    }

    /// 0.5.x 的场面：只有她、AI 的路和敌方英雄（没有队友、不知道前线）。
    fn plain(me: Pt, hp: f64, walk_to: Option<Pt>, foes: &[Foe]) -> Option<Plan> {
        plan(&Scene { me, hp, walk_to, foes, mates: &[], lane: None, towers: &[] })
    }

    // 原版图（league_macro_log 11-19 的 MAP 行）：两座水晶，蓝方（T0）在左下、红方（T1）在右上
    const BLUE: Pt = (96_000.0, 864_000.0);
    const RED: Pt = (864_000.0, 96_000.0);
    /// 蓝方的塔：上路二塔、一塔，中路二塔、一塔，下路二塔、一塔，基地的两座。
    const BLUE_TOWERS: [Pt; 8] = [
        (48_000.0, 528_000.0), (48_000.0, 272_000.0),
        (240_000.0, 720_000.0), (368_000.0, 592_000.0),
        (432_000.0, 912_000.0), (688_000.0, 912_000.0),
        (111_000.0, 784_000.0), (176_000.0, 848_000.0),
    ];
    /// 红方的塔，顺序同上。
    const RED_TOWERS: [Pt; 8] = [
        (528_000.0, 48_000.0), (272_000.0, 48_000.0),
        (720_000.0, 240_000.0), (592_000.0, 368_000.0),
        (912_000.0, 432_000.0), (912_000.0, 688_000.0),
        (784_000.0, 111_000.0), (848_000.0, 176_000.0),
    ];

    #[test]
    fn a_long_walk_out_of_a_fight_is_ridden() {
        let me = (100_000.0, 100_000.0);
        // back to lane from the fountain: 400000 to walk, nobody near
        assert_eq!(plain(me, 1.0, Some((500_000.0, 100_000.0)), &[foe(1, (600_000.0, 600_000.0), 1.0)]),
                   Some(Plan::Travel { far: 400_000.0 }));
        // a short walk: on foot
        assert_eq!(plain(me, 1.0, Some((150_000.0, 100_000.0)), &[]), None);
        // an enemy champion close: in a fight, no ride
        assert_eq!(plain(me, 1.0, Some((500_000.0, 100_000.0)), &[foe(1, (150_000.0, 100_000.0), 1.0)]), None);
        // no walk known yet: nothing
        assert_eq!(plain(me, 1.0, None, &[]), None);
    }

    #[test]
    fn a_low_one_beyond_her_reach_is_chased() {
        let me = (100_000.0, 100_000.0);
        let low = foe(7, (220_000.0, 100_000.0), 0.2);
        assert_eq!(plain(me, 0.8, None, &[low]), Some(Plan::Chase { target: 7, d: 120_000.0 }));
        // within her attack: no need
        assert_eq!(plain(me, 0.8, None, &[foe(7, (140_000.0, 100_000.0), 0.2)]), None);
        // just past it (11-03: 57475 away, in range by the time she sat on Valor, Skystrike after 3 ticks): on foot
        assert_eq!(plain(me, 0.8, None, &[foe(7, (157_475.0, 100_000.0), 0.2)]), None);
        assert!(CHASE_MIN > ATTACK_R * 1.5);
        // she is low herself: no chase
        assert_eq!(plain(me, 0.3, None, &[low]), None);
        // someone else beside her: no chase (and no ride)
        assert_eq!(plain(me, 0.8, Some((600_000.0, 100_000.0)), &[low, foe(8, (130_000.0, 100_000.0), 1.0)]), None);
        // too far to catch
        assert_eq!(plain(me, 0.8, None, &[foe(7, (400_000.0, 100_000.0), 0.2)]), None);
    }

    #[test]
    fn the_native_maps_towers_sort_into_lanes() {
        let lanes = [LaneV1::Top, LaneV1::Top, LaneV1::Mid, LaneV1::Mid, LaneV1::Bottom, LaneV1::Bottom];
        for (i, l) in lanes.iter().enumerate() {
            assert_eq!(tower_lane(BLUE, RED, BLUE_TOWERS[i]), Some(*l), "blue tower {i}");
            assert_eq!(tower_lane(RED, BLUE, RED_TOWERS[i]), Some(*l), "red tower {i}");
        }
        // the base towers are the base, no lane
        for i in 6..8 {
            assert_eq!(tower_lane(BLUE, RED, BLUE_TOWERS[i]), None);
            assert_eq!(tower_lane(RED, BLUE, RED_TOWERS[i]), None);
        }
        // the front is the lane's outer tower while it stands, then the inner one
        assert_eq!(lane_front(LaneV1::Top, BLUE, RED, &BLUE_TOWERS), Some((48_000.0, 272_000.0)));
        assert_eq!(lane_front(LaneV1::Mid, BLUE, RED, &BLUE_TOWERS), Some((368_000.0, 592_000.0)));
        assert_eq!(lane_front(LaneV1::Bottom, BLUE, RED, &BLUE_TOWERS), Some((688_000.0, 912_000.0)));
        assert_eq!(lane_front(LaneV1::Support, BLUE, RED, &BLUE_TOWERS), Some((688_000.0, 912_000.0)), "the support's is bottom");
        assert_eq!(lane_front(LaneV1::Jungle, BLUE, RED, &BLUE_TOWERS), None);
        assert_eq!(lane_front(LaneV1::Top, RED, BLUE, &RED_TOWERS), Some((272_000.0, 48_000.0)));
        assert_eq!(lane_front(LaneV1::Bottom, RED, BLUE, &RED_TOWERS), Some((912_000.0, 688_000.0)));
        let outer_down: Vec<Pt> = BLUE_TOWERS.iter().copied().filter(|t| *t != (48_000.0, 272_000.0)).collect();
        assert_eq!(lane_front(LaneV1::Top, BLUE, RED, &outer_down), Some((48_000.0, 528_000.0)));
        let top_down: Vec<Pt> = outer_down.into_iter().filter(|t| *t != (48_000.0, 528_000.0)).collect();
        assert_eq!(lane_front(LaneV1::Top, BLUE, RED, &top_down), None, "both down: no front, the base towers are no lane");
        assert!(dist(BLUE, BLUE_TOWERS[6]) < BASE_R && dist(BLUE, BLUE_TOWERS[2]) > BASE_R);
    }

    #[test]
    fn out_of_the_base_she_rides_to_her_lane() {
        // 11-19（你看的那场 m=6778）：回城 11 次、阵亡 3 次，整场只骑过一次——AI 带她回线一步只走一小段，0.5.x 只看这一步
        let front = (48_000.0, 272_000.0);
        let lane = Some((BLUE, front));
        let fountain = (60_000.0, 900_000.0);
        let hop = (60_000.0, 870_000.0);
        assert_eq!(plain(fountain, 1.0, Some(hop), &[]), None, "0.5.x: a hop of 30000 is no trip");
        let s = Scene { me: fountain, hp: 1.0, walk_to: Some(hop), foes: &[], mates: &[], lane, towers: &RED_TOWERS };
        match plan(&s) {
            Some(Plan::Lane { trip, front: f }) => {
                assert_eq!(f, front);
                assert!((trip - dist(fountain, front)).abs() < 1e-6 && trip > 600_000.0, "{trip}");
            }
            p => panic!("{p:?}"),
        }
        // walking home (away from the front): no ride to lane
        assert_eq!(plan(&Scene { walk_to: Some((70_000.0, 930_000.0)), ..s }), None);
        // standing (the AI's walk on her own spot): nothing
        assert_eq!(plan(&Scene { walk_to: Some(fountain), ..s }), None);
        // an enemy champion beside her (her base under siege): no ride
        assert_eq!(plan(&Scene { foes: &[foe(5, (100_000.0, 850_000.0), 1.0)], ..s }), None);
        // on the way, R back from its cooldown: still far enough - ride
        let mid_way = (48_000.0, 560_000.0);
        assert!(matches!(plan(&Scene { me: mid_way, walk_to: Some((48_000.0, 540_000.0)), ..s }), Some(Plan::Lane { .. })));
        // a short way left to the front: on foot
        let close = (48_000.0, 400_000.0);
        assert_eq!(plan(&Scene { me: close, walk_to: Some((48_000.0, 380_000.0)), ..s }), None);
        // in lane past her outer tower: the front is behind her, no lane ride
        let in_lane = (48_000.0, 150_000.0);
        assert_eq!(lane_trip(in_lane, (48_000.0, 120_000.0), BLUE, front), None);
        assert_eq!(lane_trip(in_lane, (48_000.0, 250_000.0), BLUE, front), None);
        // a jungler, or no lane known: the 0.5.x rule only (one long walk)
        assert_eq!(plan(&Scene { lane: None, ..s }), None);
    }

    #[test]
    fn she_rides_to_an_ally_in_a_fight() {
        let me = (100_000.0, 600_000.0);
        let ally = mate(3, (400_000.0, 600_000.0), 0.7);
        let on_him = foe(9, (430_000.0, 600_000.0), 1.0);
        let s = Scene { me, hp: 0.9, walk_to: None, foes: &[on_him], mates: &[ally], lane: None, towers: &[] };
        assert_eq!(plan(&s), Some(Plan::Help { mate: 3, d: 300_000.0, foes: 1 }));
        // a short walk: on foot (the game's AI walks her there or not)
        let near = mate(3, (220_000.0, 600_000.0), 0.7);
        assert_eq!(plan(&Scene { mates: &[near], foes: &[foe(9, (250_000.0, 600_000.0), 1.0)], ..s }), None);
        // too far to be in time
        let far = mate(3, (600_000.0, 600_000.0), 0.7);
        assert_eq!(plan(&Scene { mates: &[far], foes: &[foe(9, (630_000.0, 600_000.0), 1.0)], ..s }), None);
        // nobody on him: no fight
        assert_eq!(plan(&Scene { foes: &[foe(9, (480_000.0, 600_000.0), 1.0)], ..s }), None);
        // low and chased (the chaser 80000 behind him): go
        let low = mate(3, (400_000.0, 600_000.0), 0.3);
        assert!(matches!(plan(&Scene { mates: &[low], foes: &[foe(9, (480_000.0, 600_000.0), 1.0)], ..s }),
                         Some(Plan::Help { mate: 3, .. })));
        // under an enemy tower: no
        assert_eq!(plan(&Scene { towers: &[(450_000.0, 620_000.0)], ..s }), None);
        // one of ours against three: no; two of ours against three: go
        let three = [on_him, foe(10, (420_000.0, 630_000.0), 1.0), foe(11, (420_000.0, 570_000.0), 1.0)];
        assert_eq!(plan(&Scene { foes: &three, ..s }), None);
        let two = [ally, mate(4, (380_000.0, 620_000.0), 0.8)];
        assert_eq!(plan(&Scene { foes: &three, mates: &two, ..s }), Some(Plan::Help { mate: 4, d: dist(me, two[1].at), foes: 3 }));
        // she is low herself: no
        assert_eq!(plan(&Scene { hp: 0.4, ..s }), None);
        // an enemy champion beside her: she is in a fight herself
        assert_eq!(plan(&Scene { foes: &[on_him, foe(12, (130_000.0, 600_000.0), 1.0)], ..s }), None);
        // a low one in her chase range comes first
        let prey = foe(12, (220_000.0, 600_000.0), 0.2);
        assert_eq!(plan(&Scene { foes: &[on_him, prey], ..s }), Some(Plan::Chase { target: 12, d: 120_000.0 }));
        // helping comes before the ride to lane
        let lane = Some((BLUE, (48_000.0, 272_000.0)));
        assert!(matches!(plan(&Scene { lane, walk_to: Some((100_000.0, 580_000.0)), ..s }), Some(Plan::Help { .. })));
    }

    #[test]
    fn on_valor_to_an_ally_she_keeps_to_him() {
        let me = (100_000.0, 600_000.0);
        let him = (400_000.0, 600_000.0);
        assert!(keeps_course(me, him, Order::Walk((150_000.0, 600_000.0))), "the AI walks her his way");
        assert!(!keeps_course(me, him, Order::Walk((50_000.0, 600_000.0))), "walking off");
        assert!(!keeps_course(me, him, Order::Walk(me)), "standing");
        assert!(!keeps_course(me, him, Order::Other), "a minion on the way would land her: Skystrike for nothing");
        assert!(keeps_course(me, him, Order::AtChampion), "the AI picks a fight with a champion: Skystrike on him");
        assert!(keeps_course(me, him, Order::Keep) && keeps_course(me, him, Order::Nothing));
        // and when it is over
        let on_him = foe(9, (430_000.0, 600_000.0), 1.0);
        assert_eq!(help_over(me, Some(him), &[on_him]), None);
        assert_eq!(help_over(me, None, &[on_him]), Some("he is down"));
        assert_eq!(help_over((380_000.0, 560_000.0), Some(him), &[on_him]), Some("in the fight"));
        assert_eq!(help_over((350_000.0, 600_000.0), Some(him), &[]), Some("there"));
        assert_eq!(help_over(me, Some(him), &[foe(9, (520_000.0, 600_000.0), 1.0)]), Some("the fight is over"));
    }

    #[test]
    fn a_recall_runs_until_another_order() {
        assert!(still_recalling(false, Some(InputV1::return_home())));
        assert!(still_recalling(true, None));
        assert!(!still_recalling(true, Some(InputV1::move_to(1, 1))));
    }

    #[test]
    fn the_travel_ride_names_a_champion_she_can_see_for_the_log() {
        // 11-03 night logs: 0.4.1 pressed it on the first enemy champion in the entity list, in the fog - never taken;
        // 0.5.0: the press carries no target at all (a None cast), the name is for the log only
        let me = (100_000.0, 100_000.0);
        let seen = [foe(4, (700_000.0, 700_000.0), 1.0), foe(9, (300_000.0, 100_000.0), 1.0)];
        assert_eq!(travel_target(me, None, &seen), Some(9), "the nearest one in sight");
        assert_eq!(travel_target(me, Some(4), &seen), Some(4), "the game's AI pressed R on one in sight: that one");
        assert_eq!(travel_target(me, Some(5), &seen), Some(9), "the AI's target out of sight: the nearest seen");
        assert_eq!(travel_target(me, None, &[]), None, "nobody in sight: the ride is pressed all the same");
    }

    #[test]
    fn the_ride_is_a_no_target_cast() {
        // 11-04 night: the engine took no Targeting R beyond ~100000 whatever the range (40 RIDE AI, 40 REFUSED, 0 rides)
        let s = include_str!("../override/league_quinn.data_champion");
        let at = s.find("\"action_name\": \"ult\"").expect("the copy has no ult");
        let head: String = s[at..at + 600].chars().filter(|c| !c.is_whitespace()).collect();
        assert!(head.contains("\"range\":960000"), "{head}");
        assert!(head.contains("\"casting_type\":\"None\"") && head.contains("\"casting_target\":\"EnemyChampion\""), "{head}");
        // the main pack's Quinn still dives at a champion
        let main = include_str!("../../../league/champion/league_quinn.data_champion");
        let at = main.find("\"action_name\": \"ult\"").expect("the main pack has no ult");
        let head: String = main[at..at + 600].chars().filter(|c| !c.is_whitespace()).collect();
        assert!(head.contains("\"casting_type\":\"Targeting\""), "{head}");
    }

    #[test]
    fn once_refused_the_ais_own_r_goes_out() {
        assert!(!let_ais_r_through(None), "nothing refused yet: the AI's R is held unless plan() rides");
        assert!(let_ais_r_through(Some(5000)), "the hook's ride was refused: the AI's own R is the only ride left");
    }

    #[test]
    fn the_ais_own_r_turns_into_a_fight_or_the_walk() {
        // 11-03 night logs: the game's AI rode in fights (`RIDE over after 1 ticks, 0 ridden`): held unless plan() rides
        let me = (100_000.0, 100_000.0);
        let lane = Some((400_000.0, 100_000.0));
        assert_eq!(instead(me, Some((7, (150_000.0, 100_000.0))), lane), Instead::Attack(7), "its target in the fight");
        assert_eq!(instead(me, Some((7, (300_000.0, 100_000.0))), lane), Instead::Walk((400_000.0, 100_000.0)),
                   "its target far: on with the walk");
        assert_eq!(instead(me, Some((7, (300_000.0, 100_000.0))), Some(me)), Instead::Attack(7), "walked already");
        assert_eq!(instead(me, None, None), Instead::Stand);
    }

    #[test]
    fn a_held_r_with_no_target_fights_the_nearest_in_sight() {
        // 0.5.0's ride is a None cast: the AI's own R carries no target, and the hold walked off or stood in fights
        let me = (100_000.0, 100_000.0);
        let lane = Some((400_000.0, 100_000.0));
        let foes = [foe(4, (700_000.0, 700_000.0), 1.0), foe(9, (140_000.0, 100_000.0), 1.0)];
        assert_eq!(hold_target(me, None, &foes), Some((9, (140_000.0, 100_000.0))), "the nearest one in the fight");
        assert_eq!(instead(me, hold_target(me, None, &foes), lane), Instead::Attack(9), "in a fight: attack, not walk off");
        assert_eq!(hold_target(me, Some((4, (700_000.0, 700_000.0))), &foes).map(|t| t.0), Some(4),
                   "the AI's own target (a Targeting input) first");
        // out of a fight nobody stands in for the AI's target: on with the walk, else a tick in place - never a walk
        // toward a champion far off that the AI did not pick
        let far = [foe(4, (300_000.0, 100_000.0), 1.0)];
        assert_eq!(hold_target(me, None, &far), None);
        assert_eq!(instead(me, hold_target(me, None, &far), lane), Instead::Walk((400_000.0, 100_000.0)));
        assert_eq!(instead(me, hold_target(me, None, &far), Some(me)), Instead::Stand);
        assert_eq!(instead(me, hold_target(me, None, &[]), None), Instead::Stand);
    }

    #[test]
    fn a_burst_of_presses_is_one_line() {
        assert!(new_burst(None, 5000));
        assert!(!new_burst(Some(5000), 5000 + ORDER_FRESH));
        assert!(new_burst(Some(5000), 5001 + ORDER_FRESH), "the next press");
        assert!(new_burst(Some(5000), 100), "another match");
        let mut ai = RideAi::default();
        assert!(ai.burst("r_held", 5000));
        assert!((5004..5030).step_by(4).all(|t| !ai.burst("r_held", t)), "the AI's R held every 4 ticks: one line");
        assert!(ai.burst("refused", 5010), "kinds apart");
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let src = std::fs::read_to_string(concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_quinn.py")).unwrap();
        assert!(src.contains(&format!("\"atk_range\": {}", ATTACK_R as usize)), "atk_range is not {ATTACK_R}");
        assert!(src.contains("\"r_ride_range\": 960000"), "the copy's R must reach the whole map");
    }

    #[test]
    fn the_hook_comes_after_ult_press() {
        assert!(PRIORITY > 100);
    }
}
