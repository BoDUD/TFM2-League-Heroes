//! 赛芬（`tft_syfen`）数据做不到的部分（金铲铲第 7 赛季的幽影龙 / 格斗家 / 龙神，技能按用户选的方案 A「暴走猎杀」，
//! 2026-10-30）。他的数据（tools/kit/build_syfen.py）的 `passive` 是这里的 `tft_syfen:whisper`，参数从数据的
//! `passive.params` 来（build_syfen.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **幽影低语**：他打出的每一下伤害（`on_attack`，技能的伤害也算）都让那个敌人「缩小」`p_t` 拍：挂
//!   `tft_syfen_p_shrink`（护甲、魔抗各少 `p_shred`%，带画面）；新缩小的一下亮 `tft_syfen_p`、播 `tft_syfen_sfx_p`。
//!   打到**已经缩小**的敌人时他叠一层怒气：每层 `p_ad` 攻击力，最多 `p_max` 层，最后一次叠起 `p_stack_t` 拍后全部消失
//!   （`tft_syfen_p_rage`，带画面）。数据问不了目标身上有没有某个状态，所以由本被动来做。
//! - **暴走（冲锋）** `tft_syfen:rampage`：找 `r_range` 内**最远**的敌方英雄（没有就用 AI 选的目标），每拍往它冲
//!   `r_speed`，最多 `r_t` 拍，贴到身前就停；路上离他的路线 `r_w` 以内的每个敌人（不含塔）挨 `r_dmg` + `r_ad`% 攻击力的
//!   物理伤害并晕眩 `r_stun` 拍（每人一次），亮 `tft_syfen_r_hit`、播撞击声。数据找不到最远的人。
//! - **暴走（猛咬）** `tft_syfen:bite`：咬他冲向的那个人（还活着、在 `r_reach` 内；否则咬身边最近的敌人）：
//!   `r_bite_dmg` + `r_bite_ad`% 攻击力的物理伤害，无视 `r_pen`% 护甲，亮 `tft_syfen_r_bite`、播咬中的声音。
//! - **死亡**：倒下时播 `tft_syfen_sfx_d`，怒气清零。
//!
//! 翼爪连击、噬咬、翼刃横扫和暴走的龙吼、动作、免控是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_syfen.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_syfen";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const RUSH_FX: &str = "tft_syfen:rush";
/// 贴上去的距离（两人身体碰到）。
const TOUCH: u64 = 22000;
/// 缩小的声音最多每这么多拍一次（横扫一下打中一群人时只响一声）。
const SFX_GAP: usize = 20;

fn sf(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_SYFEN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_syfen.log");
        }
    }
    PathBuf::from("tft_syfen.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the simulation thread in game, league_talon_vault)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        _ => "unknown",
    };
    format!("[{kind} t={}] #{id}", sim.tick())
}

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n} #{id}"))
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 幽影低语：缩小 p_t 拍，护甲、魔抗各少 p_shred%；怒气每层 p_ad 攻击力，最多 p_max 层，p_stack_t 拍后消失。
    pub p_t: usize,
    pub p_shred: usize,
    pub p_ad: usize,
    pub p_max: usize,
    pub p_stack_t: usize,
    /// 暴走冲锋：找 r_range 内最远的敌方英雄，每拍 r_speed、最多 r_t 拍；路线 r_w 以内的敌人挨 r_dmg + r_ad% 攻击力、
    /// 晕眩 r_stun 拍。
    pub r_range: usize,
    pub r_speed: usize,
    pub r_t: usize,
    pub r_w: usize,
    pub r_dmg: usize,
    pub r_ad: usize,
    pub r_stun: usize,
    /// 暴走猛咬：r_bite_dmg + r_bite_ad% 攻击力，无视 r_pen% 护甲；咬 r_reach 以内的人。
    pub r_bite_dmg: usize,
    pub r_bite_ad: usize,
    pub r_pen: usize,
    pub r_reach: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_t: 240,
            p_shred: 20,
            p_ad: 5,
            p_max: 5,
            p_stack_t: 300,
            r_range: 72000,
            r_speed: 4500,
            r_t: 16,
            r_w: 20000,
            r_dmg: 30,
            r_ad: 140,
            r_stun: 75,
            r_bite_dmg: 60,
            r_bite_ad: 235,
            r_pen: 33,
            r_reach: 40000,
        }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        let u = v.max(0) as usize;
        match k {
            "p_t" => p.p_t = u,
            "p_shred" => p.p_shred = u.min(99),
            "p_ad" => p.p_ad = u,
            "p_max" => p.p_max = u,
            "p_stack_t" => p.p_stack_t = u,
            "r_range" => p.r_range = u,
            "r_speed" => p.r_speed = u.max(1),
            "r_t" => p.r_t = u,
            "r_w" => p.r_w = u,
            "r_dmg" => p.r_dmg = u,
            "r_ad" => p.r_ad = u,
            "r_stun" => p.r_stun = u,
            "r_bite_dmg" => p.r_bite_dmg = u,
            "r_bite_ad" => p.r_bite_ad = u,
            "r_pen" => p.r_pen = u.min(100),
            "r_reach" => p.r_reach = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// 一次冲锋：冲向谁、到哪一拍为止、它最后在哪、已经撞过谁。
#[derive(Clone, Debug, Default)]
struct Rush {
    target: usize,
    until: usize,
    last: (u64, u64),
    rammed: Vec<usize>,
}

/// 冲锋和猛咬按（种子、模拟来源、比赛、局、他）分开：同一个进程里预演和观看的模拟各算各的（league_loris 的做法）。
type Key = (u64, u32, u64, u64, usize);
static RUSHES: LazyLock<Mutex<HashMap<Key, Rush>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static BITES: LazyLock<Mutex<HashMap<Key, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn key(sim: &StableSim<'_>, me: usize) -> Key {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index, me)
}

// ===================== 规则（单元测试用） =====================

/// base + ratio% of the attack.
pub fn physical(base: usize, ratio: usize, atk: usize) -> usize {
    base + atk * ratio / 100
}

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// `speed` from `from` toward `to` (or onto it when nearer).
pub fn step(from: (u64, u64), to: (u64, u64), speed: u64) -> (u64, u64) {
    let d = (dist_sq(from, to) as f64).sqrt();
    if d <= speed as f64 {
        return to;
    }
    let k = speed as f64 / d;
    let x = from.0 as f64 + (to.0 as f64 - from.0 as f64) * k;
    let y = from.1 as f64 + (to.1 as f64 - from.1 as f64) * k;
    (x.round().max(0.0) as u64, y.round().max(0.0) as u64)
}

/// The point TOUCH short of `to` on the way from `from` (where he stops in front of it).
pub fn front_of(from: (u64, u64), to: (u64, u64)) -> (u64, u64) {
    let d = (dist_sq(from, to) as f64).sqrt();
    step(from, to, (d - TOUCH as f64).max(0.0) as u64)
}

/// Squared distance from `p` to the segment a-b.
pub fn seg_dist_sq(a: (u64, u64), b: (u64, u64), p: (u64, u64)) -> f64 {
    let (ax, ay, bx, by, px, py) = (a.0 as f64, a.1 as f64, b.0 as f64, b.1 as f64, p.0 as f64, p.1 as f64);
    let (dx, dy) = (bx - ax, by - ay);
    let len = dx * dx + dy * dy;
    let t = if len > 0.0 { (((px - ax) * dx + (py - ay) * dy) / len).clamp(0.0, 1.0) } else { 0.0 };
    let (cx, cy) = (ax + dx * t, ay + dy * t);
    (px - cx) * (px - cx) + (py - cy) * (py - cy)
}

/// The farthest of the (id, where) within `reach` of `at`.
pub fn farthest(at: (u64, u64), champs: &[(usize, (u64, u64))], reach: usize) -> Option<usize> {
    let r = (reach as u128) * (reach as u128);
    champs.iter().filter(|(_, p)| dist_sq(at, *p) <= r).max_by_key(|(id, p)| (dist_sq(at, *p), *id)).map(|(id, _)| *id)
}

/// The nearest of the (id, where) within `reach` of `at`.
pub fn nearest(at: (u64, u64), units: &[(usize, (u64, u64))], reach: usize) -> Option<usize> {
    let r = (reach as u128) * (reach as u128);
    units.iter().filter(|(_, p)| dist_sq(at, *p) <= r).min_by_key(|(id, p)| (dist_sq(at, *p), *id)).map(|(id, _)| *id)
}

/// The fury after one more stack.
pub fn fury_after(stacks: usize, p: &Params) -> usize {
    (stacks + 1).min(p.p_max)
}

/// The shrink: p_shred% less armour and magic resistance for p_t ticks.
pub fn shrink_buff(p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(&sf("p_shrink"), p.p_t);
    b.defence_mult = -(p.p_shred as i32);
    b.magic_resistance_mult = -(p.p_shred as i32);
    b
}

/// The fury: p_ad attack a stack for p_stack_t ticks.
pub fn fury_buff(stacks: usize, p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(&sf("p_rage"), p.p_stack_t);
    b.attack = (p.p_ad * stacks) as i32;
    b
}

// ===================== 场上 =====================

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn reachable(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive() && e.is_targetable())
}

fn atk_of(sim: &StableSim<'_>, me: usize) -> usize {
    sim.get_entity(me).map_or(0, |e| e.stat().attack)
}

/// Live, targetable enemies that are not towers (or the nexus): (id, where, champion).
fn foes(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64), bool)> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| (u.id(), u.pos(), u.is_champion()))
        .collect()
}

/// Physical damage that ignores `pen`% of the target's armour (a self buff for the hit only).
fn pierce(sim: &mut StableSim<'_>, me: usize, id: usize, dmg: usize, pen: usize) {
    let mut b = BuffV1::timed(&sf("r_pen"), 1);
    b.defence_penetration = pen;
    if pen > 0 {
        put(sim, me, &b);
    }
    sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
    if pen > 0 {
        sim.entity_remove_buff(me, b.name());
    }
}

// ===================== 暴走 =====================

/// Rampage's charge starts: the farthest enemy champion in reach, else the AI's target.
struct Rampage;
impl StableEffectType for Rampage {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let champs: Vec<_> = foes(sim, me).into_iter().filter(|f| f.2).map(|f| (f.0, f.1)).collect();
        let aimed = (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id);
        let target = farthest(at, &champs, p.r_range).or(aimed.filter(|&id| reachable(sim, id)));
        let Some(target) = target else {
            if let Some(k) = counted("rampage_none") {
                wlog(format!("{} RAMPAGE NONE #{k}: nobody to charge at", head(sim, me)));
            }
            return;
        };
        let to = sim.get_entity(target).map_or(at, |e| e.pos());
        let k_ = key(sim, me);
        RUSHES.lock().unwrap_or_else(|e| e.into_inner()).insert(k_, Rush {
            target,
            until: sim.tick() + p.r_t,
            last: to,
            rammed: Vec::new(),
        });
        BITES.lock().unwrap_or_else(|e| e.into_inner()).insert(k_, target);
        if let Some(k) = counted("rampage") {
            let d = (dist_sq(at, to) as f64).sqrt() as u64;
            wlog(format!("{} RAMPAGE #{k}: at {} ({d} away; the AI aimed at {})", head(sim, me), name_of(sim, target),
                         aimed.map_or_else(|| "nobody".to_string(), |id| name_of(sim, id))));
        }
        rush(sim, me, k_);
    }
}

/// One tick of the charge (queued again until he arrives or runs out of ticks).
struct RushStep;
impl StableEffectType for RushStep {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let k_ = key(sim, me);
        rush(sim, me, k_);
    }
}

fn rush(sim: &mut StableSim<'_>, me: usize, k_: Key) {
    let Some(mut r) = RUSHES.lock().unwrap_or_else(|e| e.into_inner()).get(&k_).cloned() else { return };
    let Some(from) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else {
        RUSHES.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
        return;
    };
    let p = params_of(me);
    if reachable(sim, r.target) {
        r.last = sim.get_entity(r.target).map_or(r.last, |e| e.pos());
    }
    let goal = front_of(from, r.last);
    let next = step(from, goal, p.r_speed as u64);
    sim.entity_set_pos(me, next.0, next.1);
    // everyone within r_w of the path walked this tick (and the one he charged at, once he is in front of it)
    let w = (p.r_w as f64) * (p.r_w as f64);
    let arrived = next == goal;
    let hit: Vec<usize> = foes(sim, me)
        .into_iter()
        .filter(|f| !r.rammed.contains(&f.0))
        .filter(|f| seg_dist_sq(from, next, f.1) <= w || (arrived && f.0 == r.target))
        .map(|f| f.0)
        .collect();
    let atk = atk_of(sim, me);
    let dmg = physical(p.r_dmg, p.r_ad, atk);
    let stun = CcV1::stun(p.r_stun as u64);
    for &id in &hit {
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
        sim.apply_cc(id, &stun);
        let on = InputTargetV1::target(id);
        sim.play_view_effect(&sf("r_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(&sf("r_hit"), me, &on);
        r.rammed.push(id);
        if let Some(k) = counted("ram") {
            wlog(format!("{} RAM #{k}: {} takes {dmg}, stunned {} ticks", head(sim, me), name_of(sim, id), p.r_stun));
        }
    }
    if arrived || sim.tick() >= r.until {
        RUSHES.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
        if let Some(k) = counted("arrive") {
            let d = (dist_sq(next, r.last) as f64).sqrt() as u64;
            wlog(format!("{} ARRIVE #{k}: {} ({d} from {}), {} rammed", head(sim, me),
                         if arrived { "in front" } else { "out of ticks" }, name_of(sim, r.target), r.rammed.len()));
        }
        return;
    }
    RUSHES.lock().unwrap_or_else(|e| e.into_inner()).insert(k_, r);
    sim.queue_effect(RUSH_FX, AttackTypeV1::Skill, me, &InputTargetV1::target(me), 1);
}

/// Rampage's bite: the one he charged at when still in reach, else the nearest enemy.
struct Bite;
impl StableEffectType for Bite {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let k_ = key(sim, me);
        RUSHES.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
        let charged = BITES.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let r = (p.r_reach as u128) * (p.r_reach as u128);
        let near = |sim: &StableSim<'_>, id: usize| {
            reachable(sim, id) && sim.get_entity(id).is_some_and(|e| dist_sq(at, e.pos()) <= r)
        };
        let all: Vec<_> = foes(sim, me).into_iter().map(|f| (f.0, f.1)).collect();
        let Some(id) = charged.filter(|&id| near(sim, id)).or_else(|| nearest(at, &all, p.r_reach)) else {
            if let Some(k) = counted("bite_none") {
                wlog(format!("{} BITE NONE #{k}: nobody within {}", head(sim, me), p.r_reach));
            }
            return;
        };
        let dmg = physical(p.r_bite_dmg, p.r_bite_ad, atk_of(sim, me));
        pierce(sim, me, id, dmg, p.r_pen);
        let on = InputTargetV1::target(id);
        sim.play_view_effect(&sf("r_bite"), me, &on, 0, 0, 0);
        sim.play_sfx(&sf("r_bite_hit"), me, &on);
        if let Some(k) = counted("bite") {
            wlog(format!("{} BITE #{k}: {} takes {dmg} ({}% armour ignored){}", head(sim, me), name_of(sim, id), p.r_pen,
                         if Some(id) == charged { "" } else { " - not the one he charged at" }));
        }
    }
}

// ===================== 被动：幽影低语 =====================

#[derive(Clone, Default)]
struct Whisper {
    p: Params,
    /// Fury stacks and the tick they all fall off; the last tick the shrink sound played.
    stacks: usize,
    fury_until: usize,
    sfx_at: usize,
}

impl StablePassive for Whisper {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Sy'fen (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        if *damage == 0 || target == me {
            return;
        }
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        // not the Nexus either (`foes` leaves it out too): it was shrunk and fed her fury (the 2026-10-30 log)
        let ok = sim.get_entity(target).is_some_and(|e| {
            e.team() != team && e.is_alive() && !e.is_tower() && !matches!(e.kind(), Some(EntityKindV1::Nexus))
        });
        if !ok {
            return;
        }
        let tick = sim.tick();
        let shrink = shrink_buff(&self.p);
        if has_buff(sim, target, shrink.name()) {
            // a hit on one already shrunk: one more fury stack
            if tick > self.fury_until {
                self.stacks = 0;
            }
            self.stacks = fury_after(self.stacks, &self.p);
            self.fury_until = tick + self.p.p_stack_t;
            put(sim, me, &fury_buff(self.stacks, &self.p));
            if let Some(k) = counted("fury") {
                wlog(format!("{} FURY #{k}: {} was shrunk -> {} stacks (+{} attack)", head(sim, me),
                             name_of(sim, target), self.stacks, self.p.p_ad * self.stacks));
            }
        } else {
            let on = InputTargetV1::target(target);
            sim.play_view_effect(&sf("p"), me, &on, 0, 0, 0);
            if tick >= self.sfx_at + SFX_GAP || self.sfx_at == 0 {
                sim.play_sfx(&sf("p"), me, &on);
                self.sfx_at = tick;
            }
            if let Some(k) = counted("shrink") {
                wlog(format!("{} SHRINK #{k}: {} (-{}% armour and magic resistance for {} ticks)", head(sim, me),
                             name_of(sim, target), self.p.p_shred, self.p.p_t));
            }
        }
        put(sim, target, &shrink);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        if self.stacks > 0 && sim.tick() > self.fury_until {
            self.stacks = 0;
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        // his death cry (the data has no moment for it); the fury is gone
        self.stacks = 0;
        sim.play_sfx(&sf("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// Sy'fen's passive and Rampage's charge and bite, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Sy'fen: Whispers' shrink and fury, Rampage at the farthest enemy) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:whisper"), Whisper::default());
    module.add_native_effect(format!("{ID}:rampage"), Rampage);
    module.add_native_effect(format!("{ID}:rush"), RushStep);
    module.add_native_effect(format!("{ID}:bite"), Bite);
    host.log(LogLevel::Info, "tft.dll: Sy'fen (Whispers, Rampage).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_ad":5,"p_max":5,"p_shred":20,"p_stack_t":300,"p_t":240,"r_ad":140,"r_bite_ad":235,"r_bite_dmg":60,"r_dmg":30,"r_pen":33,"r_range":72000,"r_reach":40000,"r_speed":4500,"r_stun":75,"r_t":16,"r_w":20000}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_shrink_and_the_fury() {
        let p = Params::default();
        let s = shrink_buff(&p);
        assert_eq!((s.name(), s.defence_mult, s.magic_resistance_mult, s.duration_tick), ("tft_syfen_p_shrink", -20, -20, 240));
        assert_eq!((fury_after(0, &p), fury_after(4, &p), fury_after(5, &p)), (1, 5, 5));
        let f = fury_buff(3, &p);
        assert_eq!((f.name(), f.attack, f.duration_tick), ("tft_syfen_p_rage", 15, 300));
    }

    #[test]
    fn the_charge_goes_to_the_farthest_in_reach() {
        let champs = [(1, (10000, 0)), (2, (60000, 0)), (3, (90000, 0)), (4, (0, 50000))];
        assert_eq!(farthest((0, 0), &champs, 72000), Some(2));
        assert_eq!(farthest((0, 0), &champs, 5000), None);
        assert_eq!(nearest((0, 0), &champs, 72000), Some(1));
    }

    #[test]
    fn he_stops_in_front_and_rams_what_is_near_the_path() {
        let goal = front_of((0, 0), (100000, 0));
        assert_eq!(goal, (100000 - TOUCH, 0));
        assert_eq!(step((0, 0), goal, 4500), (4500, 0));
        assert_eq!(step((76000, 0), goal, 4500), goal);
        assert!(seg_dist_sq((0, 0), (4500, 0), (2000, 19000)) <= 20000f64 * 20000f64);
        assert!(seg_dist_sq((0, 0), (4500, 0), (2000, 21000)) > 20000f64 * 20000f64);
        assert!(seg_dist_sq((0, 0), (4500, 0), (30000, 0)) > 20000f64 * 20000f64);
    }

    #[test]
    fn damage_by_the_numbers() {
        let p = Params::default();
        assert_eq!(physical(p.r_dmg, p.r_ad, 100), 170);
        assert_eq!(physical(p.r_bite_dmg, p.r_bite_ad, 100), 295);
    }
}
