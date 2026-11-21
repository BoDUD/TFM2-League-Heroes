//! 暗灵缠身的真墙（0.3.0，2026-11-22；用户：「没有那个地形框出来的技能」）。
//!
//! 副本的 W（tools/kit/build_yorick.py 的 native 一支）：一个 1 tick 的隐藏抛射落在那名英雄脚下，打中的英雄挂 3 tick 的
//! `W_ASK`——被动看到就记下它站的地方当圆心；`w_delay` tick 后数据给约里克挂 `W_UP`，被动看到就在记下的圆心立墙 `w_t` tick
//! （副本的参数，2 秒：英雄联盟 4 秒，附加包副本在经典引擎里模拟立 4 秒击杀差高 0.8，见 build_yorick.py 的说明）。
//! 画面（地上裂开一圈、整圈鬼魂升起、站着、塌掉）和抓脚的鬼手、W -> E 的连招都还在数据里，这里只管挡路。
//!
//! 墙是一圈：墙线半径 `w_r`，圈里的单位中心离圆心不超过 `w_r - w_half`，圈外的不少于 `w_r + w_half`（中间是墙）。
//! 只挡约里克的敌人（两边的英雄、小兵、野怪、召唤物里不是他那一队的）：约里克、他的队友和召唤物照走（英雄联盟一样）。
//!
//! - 立墙那一 tick：站在墙上的敌人照英雄联盟拨开——离圆心不到墙线 210 / 225 的拉进圈里，其余推出去，用一段强制位移
//!   （`ForceMove`，画面上连着动；`entity_set_pos` 画面上不动，见 champion-data「An add-on's entity_set_pos is not drawn」）。
//!   免控的、无视地形的不拨。
//! - 之后每 tick：单位的中心碰到墙（圈里的走出 `w_r - w_half`，圈外的走进 `w_r + w_half`）：走路的贴着墙滑（这一步沿墙的
//!   那一份照走，进墙的那一份只走到墙面：沿圆心方向放回墙面，艾尼维亚附加包 0.1.5 的做法，游戏的寻路不知道墙，放回上一
//!   tick 会一直卡住），一 tick 走了 `DASH_STEP` 以上的（冲刺）放回上一 tick 的位置；一 tick 挪了 `BLINK` 以上的（闪现、
//!   飞越）放过去，以后按它落在的那一侧算（嘉文四世附加包 0.1.3）；身上有无视地形的 buff（`ignore_wall`）的穿过去
//!   （嘉文四世附加包 0.1.4）。
//! - 打塌：英雄联盟里敌方英雄普攻 2–4 下（按技能等级）墙就塌。墙不是单位，游戏的 AI 不会拿它当目标，API 也说不出一下普攻
//!   打的是谁（拿召唤单位拼墙又会让小兵、防御塔、技能都去打它、把 AI 引过去），所以照「想出去 / 想进来的英雄在打墙」算：
//!   敌方英雄每被墙挡住一 tick，就算它打了 1 / 攻击间隔 下（间隔最多按 `BLOW_EVERY` = 30 tick 算），所有敌方英雄加起来够
//!   [`hits_needed`] 下墙就塌（`BROKEN`）。
//!   塌在数据下一段画面的开头（每 30 tick 一段，[`next_piece`]），给约里克挂 `W_DOWN`：副本的数据那一段放塌掉的画面，
//!   以后几段不放。防御塔一下就塌没做（防御塔不打墙）。

use std::collections::{HashMap, HashSet};

use super::summon::{dist, pt, Pt};
use super::*;

/// 一 tick 里挪了这么远就是闪现 / 飞越，放过去（嘉文四世附加包的 BLINK）。
pub const BLINK: f64 = 15_000.0;
/// 一 tick 走了这么远以上算冲刺：碰墙放回上一 tick 的位置（艾尼维亚附加包的 DASH_STEP）。
pub const DASH_STEP: f64 = 2_200.0;
/// 立墙时离圆心不到墙线这么多倍的拉进圈里，其余推出去（英雄联盟：210 / 225）。
pub const PULL_IN: f64 = 210.0 / 225.0;
/// 拨开用的强制位移走几 tick。
pub const PUSH_TICKS: u64 = 4;
/// 圆心记下以后最多等 `W_UP` 这么多 tick（数据在 `w_delay` tick 后挂；多出来的是余量）。
pub const PEND_SLACK: usize = 15;
/// 数据的画面：立墙后 `RISE` tick 起每 `PIECE` tick 一段（build_yorick.py 的 w_stand / w_fall）。
pub const RISE: usize = 15;
pub const PIECE: usize = 30;
/// 一下打墙最多算这么多 tick（攻击间隔比它长也按它算；读不到攻击间隔时也按它）：团战经理的团战比英雄联盟快，墙困住人
/// 的分量也大得多（经典引擎模拟主包：不能打塌的墙困 1 秒还行，1.5 秒、2 秒、4 秒击杀差多 +1、+2、+5），一个英雄打塌墙要
/// 2 / 3 / 4 x 30 tick（1–2 秒），和主包墙立的 1 秒差不多。
pub const BLOW_EVERY: usize = 30;

/// 墙塌要敌方英雄打几下（英雄联盟：2 / 2 / 3 / 3 / 4，按技能等级；这里按英雄等级 1–4 级 2 下、5–8 级 3 下、9 级起 4 下）。
pub fn hits_needed(level: usize) -> f64 {
    match level {
        0..=4 => 2.0,
        5..=8 => 3.0,
        _ => 4.0,
    }
}

/// `now` 以后数据的下一段画面从哪一 tick 开始（墙 `from` 立起）。
pub fn next_piece(from: usize, now: usize) -> usize {
    let first = from + RISE;
    if now < first {
        return first;
    }
    first + PIECE * ((now - first) / PIECE + 1)
}

/// 一圈墙：圆心、墙线、圈里 / 圈外的中心界限、立起和倒下的 tick。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Ring {
    pub c: Pt,
    pub line: f64,
    pub inner: f64,
    pub outer: f64,
    pub from: usize,
    pub until: usize,
}

impl Ring {
    pub fn new(c: Pt, p: &Params, from: usize) -> Ring {
        let (line, half) = (p.w_r as f64, p.w_half as f64);
        // 倒在数据最后一段画面（塌掉，build_yorick.py 的 n_up）放到一半的时候：小鬼闪白、缩回土里
        let n = ((p.w_t as f64 - 35.0) / PIECE as f64).round().max(0.0) as usize;
        Ring { c, line, inner: (line - half).max(0.0), outer: line + half, from, until: from + RISE + PIECE * n + 10 }
    }

    /// 这个位置在这一侧合不合法（圈里的不碰内墙面，圈外的不碰外墙面）。
    pub fn allowed(&self, inside: bool, at: Pt) -> bool {
        let d = dist(self.c, at);
        if inside { d <= self.inner } else { d >= self.outer }
    }

    /// 沿圆心方向放回这一侧的墙面（正好在圆心上的往右放）。
    pub fn face(&self, inside: bool, at: Pt) -> Pt {
        let d = dist(self.c, at);
        let (ux, uy) = if d < 1.0 { (1.0, 0.0) } else { ((at.0 - self.c.0) / d, (at.1 - self.c.1) / d) };
        let r = if inside { (self.inner - 1.0).max(0.0) } else { self.outer + 1.0 };
        (self.c.0 + ux * r, self.c.1 + uy * r)
    }

    /// 墙线的哪一侧（闪现、穿墙以后按这个算）。
    pub fn side_of(&self, at: Pt) -> bool {
        dist(self.c, at) < self.line
    }
}

/// 立墙那一 tick 一个单位怎么办：在哪一侧，要不要拨（拨到哪）。
pub fn at_rise(r: &Ring, at: Pt) -> (bool, Option<Pt>) {
    let d = dist(r.c, at);
    if d <= r.inner {
        (true, None)
    } else if d >= r.outer {
        (false, None)
    } else if d < r.line * PULL_IN {
        (true, Some(r.face(true, at)))
    } else {
        (false, Some(r.face(false, at)))
    }
}

/// 拨开的强制位移：(dx, dy, 每 tick 多快, 几 tick)。
pub fn push(from: Pt, to: Pt) -> Option<(i64, i64, u64, u64)> {
    let d = dist(from, to);
    if d < 1.0 {
        return None;
    }
    Some(((to.0 - from.0).round() as i64, (to.1 - from.1).round() as i64, (d / PUSH_TICKS as f64).ceil() as u64, PUSH_TICKS))
}

/// 墙对一个单位这一 tick 的处理。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Hold {
    /// 没碰墙。
    Free,
    /// 走路碰墙：贴着墙放到这里。
    Slide(Pt),
    /// 冲刺碰墙：放回上一 tick 的这里。
    Back(Pt),
    /// 闪现 / 飞越：放过去，以后在这一侧（true：圈里）。
    Leapt(bool),
    /// 无视地形：穿过去，以后在这一侧。
    Ghost(bool),
}

/// 这一 tick 墙怎么处理一个在 `inside` 一侧的单位（上一 tick 在 `last`，这一 tick 在 `now`）。
pub fn hold(r: &Ring, inside: bool, last: Option<Pt>, now: Pt, ghost: bool) -> Hold {
    if ghost {
        return Hold::Ghost(r.side_of(now));
    }
    let step = last.map_or(0.0, |l| dist(l, now));
    if step > BLINK {
        return Hold::Leapt(r.side_of(now));
    }
    if r.allowed(inside, now) {
        return Hold::Free;
    }
    match last {
        Some(l) if step >= DASH_STEP && r.allowed(inside, l) => Hold::Back(l),
        _ => Hold::Slide(r.face(inside, now)),
    }
}

/// 墙挡得住的：活着的英雄、小兵、野怪、召唤物（防御塔、水晶不算），不是约里克那一队的。
pub fn blocks(kind: Option<EntityKindV1>, team: usize, mine: usize) -> bool {
    team != mine && matches!(kind, Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Summon))
}

/// 一圈立着的墙和它这一路的账。
#[derive(Clone, Debug)]
pub struct Live {
    pub ring: Ring,
    pub n: usize,
    /// 每个单位在哪一侧（立墙时定，后来出现的按墙线定；闪现、穿墙后改）。
    pub side: HashMap<usize, bool>,
    /// 每个单位上一 tick 的位置。
    pub last: HashMap<usize, Pt>,
    /// 正在被拨开的单位：强制位移走完以前不管它。
    pub pushing: HashMap<usize, usize>,
    /// 挡过的单位：挡了几 tick、是不是英雄（倒下时一行总账）。
    pub held: HashMap<usize, (usize, bool)>,
    /// 已经记过 LEAPT / THROUGH 的单位（一道墙一个单位一行）。
    pub crossed: HashSet<usize>,
    /// 敌方英雄打了几下墙（被挡住的 tick / 它的攻击间隔）、打塌以后倒下的 tick。
    pub blows: f64,
    pub broken: Option<usize>,
    /// 原定倒下的 tick（`w_t` 到）。
    pub planned: usize,
}

/// W_ASK 记下的圆心，等 W_UP。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Pending {
    pub c: Pt,
    pub tick: usize,
    pub on: usize,
}

/// 约里克的墙（被动里一份）。
#[derive(Clone, Debug, Default)]
pub struct Walls {
    pub live: Vec<Live>,
    pub pending: Vec<Pending>,
    pub count: usize,
}

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

fn ignore_wall(e: &StableEntity<'_, '_>) -> Option<String> {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.ignore_wall).map(|b| b.name().to_string())
}

fn immune(e: &StableEntity<'_, '_>) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.cc_immune)
}

impl Walls {
    /// 副本挂的 `W_ASK`：英雄 `on` 站在 `at`（几个英雄同时挂上就取它们的中点）。
    pub fn asked(&mut self, now: usize, on: usize, at: Pt) {
        if let Some(p) = self.pending.iter_mut().find(|p| p.tick == now) {
            p.c = ((p.c.0 + at.0) / 2.0, (p.c.1 + at.1) / 2.0);
            return;
        }
        self.pending.push(Pending { c: at, tick: now, on });
    }

    /// 数据挂了 `W_UP`：最早那个还等着的圆心立墙。-> 立起来的墙（没有等着的圆心就是 None）。
    pub fn rise(&mut self, sim: &mut StableSim<'_>, me: usize, p: &Params) -> Option<Ring> {
        let now = sim.tick();
        self.pending.retain(|q| now <= q.tick + p.w_delay + PEND_SLACK);
        if self.pending.is_empty() {
            if let Some(k) = tally(sim, "wall lost") {
                wlog(format!("{} WALL? #{k}: w_up rose but no w_ask was seen within {} ticks before it - no wall",
                             head(sim, me), p.w_delay + PEND_SLACK));
            }
            return None;
        }
        let at = self.pending.remove(0);
        let ring = Ring::new(at.c, p, now);
        let mine = sim.get_entity(me).map_or(0, |e| e.team());
        self.count += 1;
        let mut live = Live { ring, n: self.count, side: HashMap::new(), last: HashMap::new(), pushing: HashMap::new(),
                              held: HashMap::new(), crossed: HashSet::new(), blows: 0.0, broken: None,
                              planned: ring.until };
        let units: Vec<(usize, Pt, bool, bool, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|e| e.is_alive() && blocks(e.kind(), e.team(), mine))
            .map(|e| (e.id(), summon::at_of(&e), e.is_champion(), immune(&e), ignore_wall(&e).is_some()))
            .collect();
        let (mut inside, mut pulled, mut pushed) = (0usize, 0usize, 0usize);
        for (id, pos, champion, cc_immune, ghost) in units {
            let (side, to) = at_rise(&ring, pos);
            live.side.insert(id, side);
            live.last.insert(id, pos);
            inside += usize::from(side);
            let Some(to) = to.filter(|_| !cc_immune && !ghost) else { continue };
            let Some((dx, dy, speed, ticks)) = push(pos, to) else { continue };
            let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks);
            (mv.dx, mv.dy, mv.speed) = (dx, dy, speed);
            sim.apply_cc(id, &mv);
            live.pushing.insert(id, now + ticks as usize + 1);
            if side { pulled += 1 } else { pushed += 1 }
            if let Some(k) = tally(sim, "pushed") {
                wlog(format!("{} PUSHED #{k} (wall {}): {} {} on the wall line {:.0} from the centre -> {} ({} ticks forced move{})",
                             head(sim, me), live.n, name_of(sim, id), if side { "IN" } else { "OUT" }, dist(ring.c, pos), pt(to),
                             ticks, if champion { ", a champion" } else { "" }));
            }
        }
        if let Some(k) = tally(sim, "wall") {
            wlog(format!("{} WALL #{k} (wall {}): ring at {} line {:.0} (inside within {:.0}, outside beyond {:.0}), {} ticks; \
                          {inside} enemies inside, {pulled} pulled in, {pushed} pushed out (the ask at t={} on #{})",
                         head(sim, me), live.n, pt(ring.c), ring.line, ring.inner, ring.outer, p.w_t, at.tick, at.on));
        }
        self.live.push(live);
        Some(ring)
    }

    /// 墙立着时每 tick：挡住碰墙的敌人；到时间的倒下（一行总账）。
    pub fn block(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if self.live.is_empty() {
            return;
        }
        let now = sim.tick();
        let mine = sim.get_entity(me).map_or(0, |e| e.team());
        for w in std::mem::take(&mut self.live) {
            if now >= w.ring.until {
                fallen(sim, me, &w);
            } else {
                self.live.push(w);
            }
        }
        if self.live.is_empty() {
            return;
        }
        let units: Vec<(usize, Pt, bool, Option<String>, usize)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|e| e.is_alive() && blocks(e.kind(), e.team(), mine))
            .map(|e| (e.id(), summon::at_of(&e), e.is_champion(), ignore_wall(&e), e.attack_interval()))
            .collect();
        let level = sim.get_entity(me).map_or(1, |e| e.level());
        for w in self.live.iter_mut() {
            let mut moves = Vec::new();
            for (id, now_at, champion, ghost, every) in &units {
                let (id, now_at) = (*id, *now_at);
                let inside = *w.side.entry(id).or_insert_with(|| w.ring.side_of(now_at));
                let last = w.last.insert(id, now_at);
                if w.pushing.get(&id).is_some_and(|t| now < *t) {
                    continue;
                }
                match hold(&w.ring, inside, last, now_at, ghost.is_some()) {
                    Hold::Free => {}
                    Hold::Slide(to) | Hold::Back(to) => {
                        moves.push((id, to, inside, *champion));
                        w.last.insert(id, to);
                        if *champion {
                            w.blows += 1.0 / (if *every == 0 { BLOW_EVERY } else { (*every).min(BLOW_EVERY) }).max(20) as f64;
                        }
                    }
                    Hold::Leapt(side) | Hold::Ghost(side) => {
                        w.side.insert(id, side);
                        if side != inside && w.crossed.insert(id) {
                            let what = if ghost.is_some() { "THROUGH" } else { "LEAPT" };
                            if let Some(k) = tally(sim, "crossed") {
                                wlog(format!("{} {what} {} #{k} (wall {}): {} {} at {} - let through", head(sim, me),
                                             if side { "IN" } else { "OUT" }, w.n, name_of(sim, id),
                                             ghost.as_deref().map_or("crossed in one tick".to_string(),
                                                                     |b| format!("ignores terrain ({b})")), pt(now_at)));
                            }
                        }
                    }
                }
            }
            let need = hits_needed(level);
            if w.broken.is_none() && w.blows >= need {
                let fall = next_piece(w.ring.from, now).min(w.ring.until);
                w.broken = Some(fall);
                w.ring.until = fall;
                // 副本的画面：下一段换成塌掉，之后几段都不放（挂到原定倒下以后）
                let left = (w.planned + PIECE).saturating_sub(now);
                sim.entity_remove_buff(me, W_DOWN);
                sim.add_buff(me, &BuffV1::timed(W_DOWN, left.max(PIECE)));
                if let Some(k) = tally(sim, "broken") {
                    wlog(format!("{} BROKEN #{k} (wall {}): the enemy champions it held struck it {:.1} times ({need} needed at \
                                  level {level}) - it falls at t={fall} with the picture's next piece", head(sim, me), w.n,
                                 w.blows));
                }
            }
            for (id, to, inside, champion) in moves {
                sim.entity_set_pos(id, to.0.round().max(0.0) as u64, to.1.round().max(0.0) as u64);
                let first = !w.held.contains_key(&id);
                w.held.entry(id).or_insert((0, champion)).0 += 1;
                if !first {
                    continue;
                }
                if let Some(k) = tally(sim, if inside { "kept in" } else { "kept out" }) {
                    wlog(format!("{} {} #{k} (wall {}): {} held at {} ({:.0} from the centre)", head(sim, me),
                                 if inside { "KEPT IN" } else { "KEPT OUT" }, w.n, name_of(sim, id), pt(to), dist(w.ring.c, to)));
                }
            }
        }
    }
}

/// 一道墙倒了：挡过谁（`WALL DOWN`：几个单位、几个英雄、一共几 tick、最久几 tick）。
fn fallen(sim: &StableSim<'_>, me: usize, w: &Live) {
    let ticks: usize = w.held.values().map(|v| v.0).sum();
    let longest = w.held.values().map(|v| v.0).max().unwrap_or(0);
    let champions = w.held.values().filter(|v| v.1).count();
    if let Some(k) = tally(sim, "wall down") {
        wlog(format!("{} WALL DOWN #{k} (wall {}) at {} after {} ticks{}: held {} units ({champions} champions), {ticks} ticks in \
                      all, the longest {longest}; {} crossed it", head(sim, me), w.n, pt(w.ring.c), w.ring.until - w.ring.from,
                     if w.broken.is_some() { format!(" (broken, struck {:.1} times)", w.blows) } else { String::new() },
                     w.held.len(), w.crossed.len()));
    }
}
