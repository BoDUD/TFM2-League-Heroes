//! 队友这一下真的打中了谁（0.1.0 复审，league_milio 的做法）。
//!
//! 复审指出：只看「队友的冷却跳起来 + 他身边最近的（带日光的）敌人」，治疗、护盾、只是待命的大招、放在队友身上的技能也算打中
//! 了，引爆的是谁都没打的人；普攻打塔时算到他身边最近的别的单位上。现在要过两道关：
//! 1. **命令**：观察钩子 `league_leona:watch`（她以外的每个玩家都挂，优先级最低，只记不改）记下每个玩家的 AI 最后一次下令普攻 /
//!    放技能对准的是谁（league_milio 的命令表：按这份模拟的编号 + 英雄实体记，编号挂在她身上 `SIM_TAG`，同一局并排跑的两份
//!    预演不会串）。技能对准友方（治疗、护盾、给队友的技能）的不算出手；普攻对准塔、水晶的不算；
//! 2. **掉血**：被动每 tick 记下带日光的敌方单位的生命 + 护盾掉了多少（[`Drop`]，最近 `KEEP` tick）。冷却跳起时，往前 `LOOKBACK`
//!    tick 到往后 `ATTACK_WAIT` / `SKILL_WAIT` tick 里，命令对准的那个人掉了血才算；没有命令目标（地点、方向技能，没记下命令）时，
//!    取离他 `REACH` 以内、掉得够多（`MIN_SHARE`% 他的攻击力 / 法强）的最近的一个。
//!
//! 为什么往前也看：引擎在动作结束时才开始走冷却（champion-data.md 布兰德 R 那一段），动作中途结算的伤害比冷却跳起早；经典引擎
//! 里冷却在出手后一 tick 就跳（SIM_DUMP 量的），伤害在后面——两边都接得住。

use std::collections::{BTreeMap, VecDeque};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Mutex;

use mod_api_stable::*;

/// 主包的英雄（钩子不挂在她身上：她自己的出手不引爆）；编号的 buff 名的开头；钩子的名字。
pub const HERO: &str = "league_leona";
pub const SIM_TAG: &str = "league_leona_sim:";
pub const WATCH_ID: &str = "league_leona:watch";
/// 观察钩子的优先级：最低（引擎按优先级从低到高问，它只看不改）。
const WATCH_PRIORITY: i32 = -1_000_000;
/// 冷却跳起之前多久的掉血也算（一个动作的长度）；之后最多等多久（普攻的飞行、技能的落地）。
pub const LOOKBACK: usize = 40;
pub const ATTACK_WAIT: usize = 45;
pub const SKILL_WAIT: usize = 60;
/// 掉血记多久。
pub const KEEP: usize = LOOKBACK + SKILL_WAIT + 5;
/// 技能命令下了以后这么多 tick 内冷却跳了，才算这道命令放出来的（命令在动作开始前，冷却到动作结束才跳）。
pub const ORDER_FRESH: usize = 90;
/// 队友这么远以内掉血的敌人才可能是他打的（没有命令目标时）。
pub const REACH: f64 = 95_000.0;
/// 没有命令目标时，掉的血（加护盾）至少是他攻击力（技能：攻击力、法强里大的那个）的这么多 %（小兵、塔的零碎伤害不算）。
pub const MIN_SHARE: usize = 25;

/// 一道命令对准的。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Aim {
    /// 一个敌方单位。
    Foe(usize),
    /// 友方单位（治疗、护盾）：这次出手不打人。
    Friend,
    /// 地点、方向，或没有目标。
    Place,
}

/// 一个玩家的 AI 最近下的命令。
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct Orders {
    /// 最后一次普攻命令：(tick, 目标)。
    pub attack: Option<(usize, usize)>,
    /// 最后一次走位 / 回城命令的 tick：比它早的普攻命令不再说明他在打谁。
    pub moved: usize,
    /// 技能、技能2、大招的最后一次命令：(tick, 对准的)。
    pub skill: [Option<(usize, Aim)>; 3],
}

/// 一次在等结果的出手。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Swing {
    /// 冷却跳起的 tick；从这一 tick 起的掉血算（冷却跳起前 `LOOKBACK` tick，不早于他上一下认过的那次掉血）；等到 `until` 为止。
    pub jump: usize,
    pub since: usize,
    pub until: usize,
    /// AI 下令打的那个敌人；`None` = 不知道，按掉血猜。
    pub target: Option<usize>,
    /// 没有命令目标时，掉血至少这么多才算。
    pub min: usize,
}

/// 一个敌方单位掉了血：哪一 tick、谁、在哪、掉了多少（生命 + 护盾）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Drop {
    pub tick: usize,
    pub id: usize,
    pub at: (f64, f64),
    pub amount: usize,
}

/// 冷却跳起（`slot` 0 普攻、1-3 技能、技能2、大招）时这次出手等什么：`None` = 不算出手（技能对准友方、普攻对准塔 / 水晶）；
/// 否则一个 [`Swing`]（有命令目标就等它掉血）。`tower(id)`：这个单位是不是塔、水晶；`atk` / `ap`：他的攻击力、法强；`floor`：
/// 他上一下认过的那次掉血之后的 tick（同一次掉血不给他的两下各算一次）。
pub fn open(o: &Orders, slot: usize, now: usize, tower: impl Fn(usize) -> bool, atk: usize, ap: usize, floor: usize)
            -> Option<Swing> {
    let (target, wait, min) = if slot == 0 {
        let t = o.attack.filter(|(t, _)| *t >= o.moved).map(|x| x.1);
        if t.is_some_and(&tower) {
            return None;
        }
        (t, ATTACK_WAIT, MIN_SHARE * atk / 100)
    } else {
        let t = match o.skill[slot - 1].filter(|(t, _)| *t + ORDER_FRESH >= now) {
            Some((_, Aim::Friend)) => return None,
            Some((_, Aim::Foe(x))) if tower(x) => return None,
            Some((_, Aim::Foe(x))) => Some(x),
            _ => None,
        };
        (t, SKILL_WAIT, MIN_SHARE * atk.max(ap) / 100)
    };
    Some(Swing { jump: now, since: now.saturating_sub(LOOKBACK).max(floor), until: now + wait, target, min })
}

/// 这次出手打中了谁、认的是哪一 tick 的掉血：`drops` 里 `sw.since` 起的掉血，命令目标掉了血就是它；没有命令目标时，`ok` 的、
/// 离 `from` `REACH` 以内、掉得够多的最近的一个。
pub fn hit_of(sw: &Swing, drops: &VecDeque<Drop>, from: (f64, f64), ok: impl Fn(usize) -> bool) -> Option<(usize, usize)> {
    let mut window = drops.iter().filter(|d| d.tick >= sw.since);
    if let Some(t) = sw.target {
        return window.find(|d| d.id == t && ok(t)).map(|d| (t, d.tick));
    }
    let dist = |p: (f64, f64)| ((p.0 - from.0).powi(2) + (p.1 - from.1).powi(2)).sqrt();
    window
        .filter(|d| d.amount >= sw.min && dist(d.at) <= REACH && ok(d.id))
        .min_by(|a, b| dist(a.at).total_cmp(&dist(b.at)).then(a.id.cmp(&b.id)))
        .map(|d| (d.id, d.tick))
}

// ===================== 观察钩子交给被动的命令表 =====================

/// (这份模拟的编号, 英雄实体) -> 他的 AI 最近的命令。每份模拟只删自己的（league_milio 0.1.4 的做法）。
type OrderBook = BTreeMap<(u64, usize), Orders>;
static ORDERS: Mutex<OrderBook> = Mutex::new(BTreeMap::new());
const ORDERS_MOST: usize = 4096;
/// 每份模拟一个编号（被动在她第一次出生时取，挂在她身上）。
pub static NEXT_SIM: AtomicU64 = AtomicU64::new(1);

fn make_room(map: &mut OrderBook, n: u64, alive: impl Fn(usize) -> bool) {
    let gone: Vec<_> = map.range((n, 0)..=(n, usize::MAX)).map(|(k, _)| *k).filter(|k| !alive(k.1)).collect();
    for k in gone {
        map.remove(&k);
    }
    while map.len() >= ORDERS_MOST {
        let Some(old) = map.keys().next().map(|k| k.0).filter(|&s| s != n) else { break };
        let gone: Vec<_> = map.range((old, 0)..=(old, usize::MAX)).map(|(k, _)| *k).collect();
        for k in gone {
            map.remove(&k);
        }
    }
}

pub fn orders_of(sim_no: u64, champion: usize) -> Orders {
    ORDERS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim_no, champion)).copied().unwrap_or_default()
}

/// 她身上挂的编号（0：没有）。
pub fn sim_tag(e: &StableEntity<'_, '_>) -> u64 {
    (0..e.buff_count())
        .filter_map(|i| e.buff_at(i))
        .find_map(|b| b.name().strip_prefix(SIM_TAG).and_then(|v| v.parse().ok()))
        .unwrap_or(0)
}

/// 观察钩子：只记命令，永远不改 AI 的输入。
#[derive(Clone, Default)]
pub struct Watch {
    /// 同队的她：(实体, 这份模拟的编号)；她死了再出生是新的实体，找不到就重找。
    hero: Option<(usize, u64)>,
    /// 同队没有她：到这一 tick 前不再找。
    none_until: usize,
}

const RESCAN: usize = 300;

impl Watch {
    fn sim_no(&mut self, sim: &StableSim<'_>, team: usize, tick: usize) -> Option<u64> {
        if let Some((id, n)) = self.hero {
            if sim.get_entity(id).is_some_and(|e| e.is_alive()) {
                return Some(n);
            }
            self.hero = None;
        }
        if tick < self.none_until {
            return None;
        }
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || e.team() != team || !e.is_alive() || e.name().as_deref() != Some(HERO) {
                continue;
            }
            let n = sim_tag(&e);
            if n > 0 {
                self.hero = Some((e.id(), n));
                return Some(n);
            }
        }
        self.none_until = tick + RESCAN;
        None
    }
}

impl StablePlayerAi for Watch {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        WATCH_ID.to_string()
    }

    fn priority(&self) -> i32 {
        WATCH_PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name != HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        // only a new order says anything (the AI gives one on its judgement ticks, None in between)
        let b = base?;
        let tick = ctx.tick();
        let player = ctx.player_id();
        let kind = InputKindV1::from_code(b.kind)?;
        let sim = ctx.sim()?;
        let me = sim.get_player(player)?.champion()?;
        let (mid, team) = (me.id(), me.team());
        let n = self.sim_no(&sim, team, tick)?;
        let aim = match InputTargetKindV1::from_code(b.target.kind) {
            Some(InputTargetKindV1::Target) => match sim.get_entity(b.target.target_id) {
                Some(t) if t.team() != team => Aim::Foe(t.id()),
                Some(_) => Aim::Friend,
                None => Aim::Place,
            },
            _ => Aim::Place,
        };
        let mut map = ORDERS.lock().unwrap_or_else(|e| e.into_inner());
        if !map.contains_key(&(n, mid)) {
            make_room(&mut map, n, |id| sim.get_entity(id).is_some_and(|e| e.is_alive()));
        }
        let o = map.entry((n, mid)).or_default();
        match kind {
            InputKindV1::Attack => match aim {
                Aim::Foe(t) => o.attack = Some((tick, t)),
                _ => o.moved = tick,
            },
            InputKindV1::Skill => o.skill[0] = Some((tick, aim)),
            InputKindV1::Skill2 => o.skill[1] = Some((tick, aim)),
            InputKindV1::Ult => o.skill[2] = Some((tick, aim)),
            InputKindV1::Move | InputKindV1::Return => o.moved = tick,
        }
        None
    }
}

/// 新的一 tick 里新挂上编号的 buff（被动出生时调）。
pub fn tag(sim: &mut StableSim<'_>, me: usize, n: u64) {
    let name = format!("{SIM_TAG}{n}");
    sim.entity_remove_buff(me, &name);
    sim.add_buff(me, &BuffV1::named(&name));
}

/// 这份模拟的一个新编号。
pub fn next_sim() -> u64 {
    NEXT_SIM.fetch_add(1, Ordering::Relaxed)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn drop(tick: usize, id: usize, x: f64, amount: usize) -> Drop {
        Drop { tick, id, at: (x, 0.0), amount }
    }

    #[test]
    fn a_heal_or_a_shield_on_an_ally_opens_nothing() {
        let o = Orders { skill: [Some((100, Aim::Friend)), Some((100, Aim::Place)), None], ..Orders::default() };
        assert_eq!(open(&o, 1, 120, |_| false, 80, 100, 0), None, "skill ordered at a friend");
        let sw = open(&o, 2, 120, |_| false, 80, 100, 0).expect("a place / direction skill is watched");
        assert_eq!(sw.target, None);
        // an old order (before the action) still counts up to ORDER_FRESH
        assert_eq!(open(&o, 1, 100 + ORDER_FRESH, |_| false, 80, 100, 0), None);
        assert!(open(&o, 1, 101 + ORDER_FRESH, |_| false, 80, 100, 0).is_some(), "too old: guessed by the drops");
    }

    #[test]
    fn an_attack_on_a_tower_opens_nothing_and_one_on_a_foe_waits_for_it() {
        let o = Orders { attack: Some((50, 7)), moved: 10, ..Orders::default() };
        assert_eq!(open(&o, 0, 60, |id| id == 7, 80, 0, 0), None, "attacking a tower");
        assert_eq!(open(&o, 0, 60, |_| false, 80, 0, 0).map(|s| s.target), Some(Some(7)));
        let moved = Orders { attack: Some((50, 7)), moved: 55, ..Orders::default() };
        assert_eq!(open(&moved, 0, 60, |_| false, 80, 0, 0).map(|s| s.target), Some(None), "walked since: guessed");
    }

    #[test]
    fn only_a_drop_in_the_window_counts() {
        let sw = Swing { jump: 1_000, since: 1_000 - LOOKBACK, until: 1_045, target: Some(5), min: 20 };
        let mut d = VecDeque::new();
        d.push_back(drop(900, 5, 0.0, 100)); // long before the action: not this one
        assert_eq!(hit_of(&sw, &d, (0.0, 0.0), |_| true), None);
        d.push_back(drop(1_000 - LOOKBACK, 5, 0.0, 30)); // during the action (the cooldown jumps at its end)
        assert_eq!(hit_of(&sw, &d, (0.0, 0.0), |_| true), Some((5, 1_000 - LOOKBACK)));
        assert_eq!(hit_of(&sw, &d, (0.0, 0.0), |_| false), None, "not marked");
        // the same drop already taken by his last hit: not again
        let o = Orders { attack: Some((990, 5)), ..Orders::default() };
        let next = open(&o, 0, 1_010, |_| false, 80, 0, 1_000 - LOOKBACK + 1).expect("watched");
        assert_eq!(hit_of(&next, &d, (0.0, 0.0), |_| true), None);
        // guessed: the nearest that dropped enough, within reach
        let g = Swing { target: None, ..sw };
        let mut d = VecDeque::new();
        d.push_back(drop(1_010, 8, 50_000.0, 10)); // too small
        d.push_back(drop(1_010, 9, 120_000.0, 300)); // too far
        assert_eq!(hit_of(&g, &d, (0.0, 0.0), |_| true), None, "a heal: nothing near dropped");
        d.push_back(drop(1_012, 4, 60_000.0, 90));
        d.push_back(drop(1_013, 3, 30_000.0, 90));
        assert_eq!(hit_of(&g, &d, (0.0, 0.0), |_| true), Some((3, 1_013)));
    }
}
