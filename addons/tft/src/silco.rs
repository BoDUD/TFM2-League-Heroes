//! 希尔科（`tft_silco`）数据做不到的部分（金铲铲第 13 赛季的炼金男爵 / 统领，技能和被动按用户选的方案 A「统领·畸变体」，
//! 2026-10-27）。他的数据（tools/kit/build_silco.py）的 `passive` 是这里的 `tft_silco:baron`，参数从数据的
//! `passive.params` 来（build_silco.py 从参数表 P 写进去，`NATIVE_KEYS`），按他的单位编号记一份给效果用：
//!
//! - **统领的护盾每次出生都有**：数据没有「出生」的时机，被动在他出生 / 复活时给 `s_amt` + 法强 `s_ap`% 的护盾，`s_t` 拍，
//!   身上挂护盾在时一直在的 `tft_silco_p_shield`（数据里同名的画面）。
//! - **畸变体**（`tft_silco:canister`：罐装畸变体的储罐落地；`tft_silco:flood`：炼金狂潮的巨型储罐落地）：放出 `q_n` /
//!   `r_n` 只畸变体，扑向储罐附近的敌人（先英雄，几只分给不同的人），每只咬 `m_n` 口、每 `m_gap` 拍一口，每口 `m_dmg` +
//!   法强 `m_ratio`% 魔法伤害；被咬的人死了 / 选不中了，就跳到 `m_reach` 以内最近的敌人身上接着咬，咬完或 `m_life` 拍后化掉。
//!   畸变体是骑在被咬的人身上的画面（扑上去 `m_leap`、啃咬 `m_bite_l` / `m_bite_r` 分在他左右两边、化掉 `m_die`），像安妮的
//!   提伯斯；被咬的人、剩几口、哪一边、到期的拍记在全局表里（按这份模拟的编号 `SIM_TAG` 和希尔科），每口排一次效果
//!   （`tft_silco:monster`，普通的位置输入），到点时把表里这一行到点的畸变体都处理掉。
//! - **巨型储罐留下微光毒雾**（`tft_silco:flood` 接着 `tft_silco:fog`）：`r_fog_t` 拍里，`r_fog_r` 以内（加那人的半径）的敌人
//!   减速 `r_slow`%（`tft_silco_r_slow`），每秒受到 `r_fog_dmg` + 法强 `r_fog_ratio`% 魔法伤害；毒雾的画面 `r_fog` 隔一会儿
//!   重播。毒雾也记在表里（同上）。
//! - **微光注射给身边的队友**（`tft_silco:inject`：技能2 出手）：`e_r` 以内攻击力最高的友方英雄（没有就他自己）攻速
//!   +`e_as`%、移速 +`e_ms`%，`e_t` 拍（`tft_silco_e_shimmer`）；药效过去（`tft_silco:comedown`）扣掉当前生命的
//!   `e_cost`%（不会扣死）。
//!
//! 统领叠的法强是数据自己的（技能 / 技能2 / 大招每放一次登上一级 d1..d_max，死了就没了）。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_silco.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

use crate::sim_tag::{due, forget, wait, Key, Rows, SimTag};

const ID: &str = "tft_silco";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const MONSTER_FX: &str = "tft_silco:monster";
const FOG_FX: &str = "tft_silco:fog";
const COMEDOWN_FX: &str = "tft_silco:comedown";
/// The bite's sound (the tft pack's sound_info; the rest of his sounds the data plays).
const SFX_BITE: &str = "tft_silco_m_bite";
/// 毒雾隔几拍看一次（减速挂到下一次再多一点），毒雾的画面多久重播一次（它的长度）。
const FOG_GAP: usize = 15;
const FOG_SHOW: usize = 60;

fn sc(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

/// The tests log into the temp folder (lib.rs's way: the monstrosity test's lines must not land in the game's log).
#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("tft_silco_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_SILCO_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_silco.log");
        }
    }
    PathBuf::from("tft_silco.log")
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
    /// 统领的护盾：s_amt + s_ap% 法强，s_t 拍。
    pub s_amt: usize,
    pub s_ap: usize,
    pub s_t: usize,
    /// 罐装畸变体放出几只。
    pub q_n: usize,
    /// 畸变体：咬几口、隔几拍一口、扑上去要几拍、每口 m_dmg + m_ratio% 法强、换人的距离、最多活几拍。
    pub m_n: usize,
    pub m_gap: usize,
    pub m_leap: usize,
    pub m_dmg: usize,
    pub m_ratio: usize,
    pub m_reach: u64,
    pub m_life: usize,
    /// 微光注射：找队友的距离、攻速 / 移速 +%、几拍、药效过去扣当前生命的 %。
    pub e_r: u64,
    pub e_as: i32,
    pub e_ms: i32,
    pub e_t: usize,
    pub e_cost: usize,
    /// 炼金狂潮放出几只；毒雾的半径、几拍、减速 %、每秒 r_fog_dmg + r_fog_ratio% 法强。
    pub r_n: usize,
    pub r_fog_r: u64,
    pub r_fog_t: usize,
    pub r_slow: i32,
    pub r_fog_dmg: usize,
    pub r_fog_ratio: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            s_amt: 120,
            s_ap: 40,
            s_t: 900,
            q_n: 2,
            m_n: 5,
            m_gap: 45,
            m_leap: 18,
            m_dmg: 15,
            m_ratio: 11,
            m_reach: 45000,
            m_life: 600,
            e_r: 50000,
            e_as: 50,
            e_ms: 20,
            e_t: 240,
            e_cost: 8,
            r_n: 4,
            r_fog_r: 40000,
            r_fog_t: 240,
            r_slow: 30,
            r_fog_dmg: 6,
            r_fog_ratio: 4,
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
            "s_amt" => p.s_amt = u,
            "s_ap" => p.s_ap = u,
            "s_t" => p.s_t = u,
            "q_n" => p.q_n = u,
            "m_n" => p.m_n = u,
            "m_gap" => p.m_gap = u.max(1),
            "m_leap" => p.m_leap = u.max(1),
            "m_dmg" => p.m_dmg = u,
            "m_ratio" => p.m_ratio = u,
            "m_reach" => p.m_reach = u as u64,
            "m_life" => p.m_life = u,
            "e_r" => p.e_r = u as u64,
            "e_as" => p.e_as = v as i32,
            "e_ms" => p.e_ms = v as i32,
            "e_t" => p.e_t = u,
            "e_cost" => p.e_cost = u.min(99),
            "r_n" => p.r_n = u,
            "r_fog_r" => p.r_fog_r = u as u64,
            "r_fog_t" => p.r_fog_t = u,
            "r_slow" => p.r_slow = v as i32,
            "r_fog_dmg" => p.r_fog_dmg = u,
            "r_fog_ratio" => p.r_fog_ratio = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

// ===================== 每份模拟的畸变体和毒雾 =====================

/// 畸变体和毒雾按（这份模拟的编号 `SIM_TAG`、希尔科）记在这里（2026-11-04 修，11-03 夜里的日志：40 个储罐 39 次挑到了人，
/// 一口 BITE、一次 LEAP 都没有）。以前每只畸变体塞在排队效果的输入里（被咬的人 + 1 在 target_id，剩几口和哪一边在 dir_x，
/// 化掉的拍在 dir_y），毒雾的起止拍在 dir_x / dir_y；排队只留下位置输入的 x、y（格雷福斯附加包的撞墙标记一样丢了），
/// 取出来剩 0 口，第一口就悄悄化掉，毒雾第一拍就散了。现在排的是普通的位置输入，效果到点时把这一行里到点的都处理掉
/// （sim_tag.rs 的 `Rows`）。
const TAG: SimTag = SimTag("tft_silco_sim:");
static MONSTERS: LazyLock<Rows<Monster>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static FOGS: LazyLock<Rows<Cloud>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// His new life: the monstrosities and fogs of the last one stopped with him.
fn new_life(no: u64) {
    forget(&MONSTERS, no);
    forget(&FOGS, no);
}

// ===================== 规则（单元测试用） =====================

/// base + ratio% of the ability power.
pub fn magic(base: usize, ratio: usize, ap: usize) -> usize {
    base + ap * ratio / 100
}

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// A unit a monstrosity may go for: (id, where, a champion).
pub type Foe = (usize, (u64, u64), bool);

/// The enemies within `reach` of `at`, champions first, each group nearest first (a tie: the lower id).
pub fn by_preference(foes: &[Foe], at: (u64, u64), reach: u64) -> Vec<usize> {
    let mut v: Vec<(bool, u128, usize)> = foes
        .iter()
        .map(|&(id, p, champ)| (!champ, dist_sq(p, at), id))
        .filter(|&(_, d, _)| d <= (reach as u128) * (reach as u128))
        .collect();
    v.sort();
    v.into_iter().map(|(_, _, id)| id).collect()
}

/// The victims of `n` monstrosities out of one canister: spread over the preferred enemies, then round again.
pub fn victims(foes: &[Foe], at: (u64, u64), reach: u64, n: usize) -> Vec<usize> {
    let list = by_preference(foes, at, reach);
    if list.is_empty() {
        return Vec::new();
    }
    (0..n).map(|k| list[k % list.len()]).collect()
}

/// The comedown: e_cost% of the current health, never the last point.
pub fn comedown(hp: usize, cost: usize) -> usize {
    hp.saturating_sub(hp * cost / 100).max(1).min(hp)
}

/// One monstrosity (its row in [`MONSTERS`]): where it is, whom it bites, how many bites are left, which side of its
/// victim it is drawn on, the tick it melts.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Monster {
    pub at: (u64, u64),
    pub victim: Option<usize>,
    pub bites: usize,
    pub side: usize,
    pub until: usize,
}

impl Monster {
    pub fn bite_picture(&self) -> String {
        sc(if self.side == 0 { "m_bite_l" } else { "m_bite_r" })
    }
}

/// The Shimmer fog of one giant canister (its row in [`FOGS`]): where, the tick it rose (its picture replays from it),
/// the tick it goes.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Cloud {
    pub at: (u64, u64),
    pub born: usize,
    pub until: usize,
}

/// `unit_at` (a body of radius `unit_r`) is in the circle of radius `r` around `at`: a shape counts the body it tests.
pub fn in_circle(at: (u64, u64), r: u64, unit_at: (u64, u64), unit_r: u64) -> bool {
    let reach = (r + unit_r) as u128;
    dist_sq(at, unit_at) <= reach * reach
}

// ===================== 模拟里的小工具 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn ap_of(sim: &StableSim<'_>, me: usize) -> usize {
    sim.get_entity(me).map_or(0, |e| e.stat().magic_power)
}

fn team_of(sim: &StableSim<'_>, me: usize) -> Option<usize> {
    sim.get_entity(me).map(|e| e.team())
}

/// The point an effect runs on: a position, or where its unit stands.
fn point(sim: &StableSim<'_>, input: &InputTargetV1) -> Option<(u64, u64)> {
    match InputTargetKindV1::from_code(input.kind) {
        Some(InputTargetKindV1::Pos) => Some((input.x, input.y)),
        Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|e| e.pos()),
        _ => None,
    }
}

/// His enemies a monstrosity or the fog can touch: alive, targetable, not a tower or a nexus.
fn foes(sim: &StableSim<'_>, team: usize) -> Vec<Foe> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| (u.id(), u.pos(), u.is_champion()))
        .collect()
}

fn biteable(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive() && e.is_targetable())
}

/// A named timed buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

/// One of his effects queued `delay` ticks on, with a plain input (the queue keeps a position's x and y, nothing more);
/// a refusal is logged (2026-11-04: it was dropped without a word).
fn queue(sim: &mut StableSim<'_>, fx: &str, me: usize, input: InputTargetV1, delay: usize) {
    if !sim.queue_effect(fx, AttackTypeV1::Skill, me, &input, delay.max(1)) {
        if let Some(k) = counted("refused") {
            wlog(format!("{} REFUSED #{k}: queue_effect({fx})", head(sim, me)));
        }
    }
}

// ===================== 畸变体 =====================

/// Monstrosity `m` waits in his row for `delay` ticks; its effect is queued for then.
fn send(sim: &mut StableSim<'_>, me: usize, row: Key, m: Monster, delay: usize) {
    wait(&MONSTERS, row, sim.tick() + delay.max(1), m);
    queue(sim, MONSTER_FX, me, InputTargetV1::pos(m.at.0, m.at.1), delay);
}

/// A canister landed at `at`: `n` monstrosities pounce on the enemies near it.
fn release(sim: &mut StableSim<'_>, me: usize, at: (u64, u64), n: usize, what: &'static str) {
    let Some(team) = team_of(sim, me) else { return };
    let p = params_of(me);
    let (tick, row) = (sim.tick(), TAG.key(sim, me, me));
    let picked = victims(&foes(sim, team), at, p.m_reach, n);
    for (k, &id) in picked.iter().enumerate() {
        sim.play_view_effect(&sc("m_leap"), me, &InputTargetV1::target(id), 0, 0, 0);
        let m = Monster { at, victim: Some(id), bites: p.m_n, side: k & 1, until: tick + p.m_life };
        send(sim, me, row, m, p.m_leap);
    }
    if picked.is_empty() {
        sim.play_view_effect(&sc("m_die"), me, &InputTargetV1::pos(at.0, at.1), 0, 0, 0);
    }
    if let Some(k) = counted(what) {
        let names: Vec<String> = picked.iter().map(|&id| name_of(sim, id)).collect();
        wlog(format!("{} {} #{k}: {} monstrosities at ({}, {}) -> {:?}", head(sim, me), what.to_uppercase(), n, at.0,
                     at.1, names));
    }
}

/// The canister of Canister of Monstrosities landed.
struct Canister;
impl StableEffectType for Canister {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(at) = point(sim, &input) else { return };
        release(sim, me, at, params_of(me).q_n, "canister");
    }
}

/// One monstrosity's turn: bite its victim, or leap to the nearest enemy when the victim is gone.
fn monster(sim: &mut StableSim<'_>, me: usize, row: Key, mut m: Monster) {
    let (Some(team), tick) = (team_of(sim, me), sim.tick()) else { return };
    let p = params_of(me);
    let alive_victim = m.victim.filter(|&id| biteable(sim, id));
    if let Some(id) = alive_victim {
        m.at = sim.get_entity(id).map_or(m.at, |e| e.pos());
    }
    if m.bites == 0 || tick >= m.until {
        sim.play_view_effect(&sc("m_die"), me, &InputTargetV1::pos(m.at.0, m.at.1), 0, 0, 0);
        return;
    }
    let Some(id) = alive_victim else {
        // the victim died or slipped away: the nearest enemy within reach, or it melts
        match by_preference(&foes(sim, team), m.at, p.m_reach).first() {
            Some(&next) => {
                sim.play_view_effect(&sc("m_leap"), me, &InputTargetV1::target(next), 0, 0, 0);
                if let Some(k) = counted("leap") {
                    wlog(format!("{} LEAP #{k}: a monstrosity ({} bites left) to {}", head(sim, me), m.bites,
                                 name_of(sim, next)));
                }
                send(sim, me, row, Monster { victim: Some(next), ..m }, p.m_leap);
            }
            None => {
                sim.play_view_effect(&sc("m_die"), me, &InputTargetV1::pos(m.at.0, m.at.1), 0, 0, 0);
            }
        }
        return;
    };
    let dmg = magic(p.m_dmg, p.m_ratio, ap_of(sim, me));
    sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
    let on = InputTargetV1::target(id);
    sim.play_view_effect(&m.bite_picture(), me, &on, 0, 0, 0);
    sim.play_sfx(SFX_BITE, me, &on);
    if let Some(k) = counted("bite") {
        wlog(format!("{} BITE #{k}: {} takes {dmg} magic ({} bites left)", head(sim, me), name_of(sim, id),
                     m.bites - 1));
    }
    m.bites -= 1;
    send(sim, me, row, m, p.m_gap);
}

/// A monstrosity's tick came (a bite, a leap's landing): every monstrosity of his due by now takes its turn.
struct Monstrosity;
impl StableEffectType for Monstrosity {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let row = TAG.key(sim, me, me);
        for m in due(&MONSTERS, row, sim.tick()) {
            monster(sim, me, row, m);
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (0, magic(p.m_dmg, p.m_ratio, caster_stat.magic_power))
    }
}

// ===================== 炼金狂潮 =====================

/// The giant canister landed: r_n monstrosities and the fog.
struct Flood;
impl StableEffectType for Flood {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(at) = point(sim, &input) else { return };
        let p = params_of(me);
        release(sim, me, at, p.r_n, "flood");
        let (tick, row) = (sim.tick(), TAG.key(sim, me, me));
        sim.play_view_effect(&sc("r_fog"), me, &InputTargetV1::pos(at.0, at.1), 0, 0, 0);
        wait(&FOGS, row, tick + FOG_GAP, Cloud { at, born: tick, until: tick + p.r_fog_t });
        queue(sim, FOG_FX, me, InputTargetV1::pos(at.0, at.1), FOG_GAP);
    }
}

/// One fog's turn, every FOG_GAP ticks while it lasts.
fn fog(sim: &mut StableSim<'_>, me: usize, row: Key, c: Cloud) {
    let tick = sim.tick();
    let Some(team) = team_of(sim, me) else { return };
    if tick >= c.until {
        return;
    }
    let p = params_of(me);
    let dmg = magic(p.r_fog_dmg, p.r_fog_ratio, ap_of(sim, me)) * FOG_GAP / 60;
    let mut slow = BuffV1::timed(&sc("r_slow"), FOG_GAP + 5);
    slow.move_speed_mult = -p.r_slow;
    let inside: Vec<usize> = foes(sim, team)
        .into_iter()
        .filter(|&(id, q, _)| in_circle(c.at, p.r_fog_r, q, sim.get_entity(id).map_or(0, |e| e.radius() as u64)))
        .map(|(id, _, _)| id)
        .collect();
    for &id in &inside {
        put(sim, id, &slow);
        if dmg > 0 {
            sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        }
    }
    if (tick - c.born) % FOG_SHOW < FOG_GAP && tick - c.born >= FOG_SHOW {
        sim.play_view_effect(&sc("r_fog"), me, &InputTargetV1::pos(c.at.0, c.at.1), 0, 0, 0);
    }
    if !inside.is_empty() {
        if let Some(k) = counted("fog") {
            wlog(format!("{} FOG #{k}: {} inside, {dmg} magic each", head(sim, me), inside.len()));
        }
    }
    wait(&FOGS, row, tick + FOG_GAP, c);
    queue(sim, FOG_FX, me, InputTargetV1::pos(c.at.0, c.at.1), FOG_GAP);
}

/// A fog's tick came: every fog of his due by now takes its turn.
struct Fog;
impl StableEffectType for Fog {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let row = TAG.key(sim, me, me);
        for c in due(&FOGS, row, sim.tick()) {
            fog(sim, me, row, c);
        }
    }
}

// ===================== 微光注射 =====================

/// Shimmer Shot: the allied champion with the most attack within e_r (himself when none).
struct Inject;
impl StableEffectType for Inject {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some((team, at)) = sim.get_entity(me).map(|e| (e.team(), e.pos())) else { return };
        let p = params_of(me);
        let mut best: Option<(usize, usize)> = None;   // (attack, id)
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            if id == me {
                continue;
            }
            let Some(c) = sim.get_entity(id) else { continue };
            if c.team() != team || !c.is_alive() || !c.is_targetable() {
                continue;
            }
            if dist_sq(c.pos(), at) > (p.e_r as u128) * (p.e_r as u128) {
                continue;
            }
            let atk = c.stat().attack;
            if best.is_none_or(|(b, bid)| atk > b || (atk == b && id < bid)) {
                best = Some((atk, id));
            }
        }
        let ally = best.map_or(me, |(_, id)| id);
        let mut dose = BuffV1::timed(&sc("e_shimmer"), p.e_t);
        dose.attack_speed_mult = p.e_as;
        dose.move_speed_mult = p.e_ms;
        put(sim, ally, &dose);
        let on = InputTargetV1::target(ally);
        sim.play_view_effect(&sc("e_dose"), me, &on, 0, 0, 0);
        sim.queue_effect(COMEDOWN_FX, AttackTypeV1::Skill, me, &on, p.e_t);
        if let Some(k) = counted("inject") {
            wlog(format!("{} INJECT #{k}: {}{}", head(sim, me), name_of(sim, ally),
                         if ally == me { " (himself)" } else { "" }));
        }
    }
}

/// The comedown after e_t ticks: e_cost% of the current health (never the last point).
struct Comedown;
impl StableEffectType for Comedown {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let id = input.target_id;
        let Some((hp, _)) = sim.get_entity(id).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        let left = comedown(hp, params_of(me).e_cost);
        sim.entity_set_hp(id, left);
        sim.play_view_effect(&sc("e_crash"), me, &input, 0, 0, 0);
        if let Some(k) = counted("comedown") {
            wlog(format!("{} COMEDOWN #{k}: {} {hp} -> {left}", head(sim, me), name_of(sim, id)));
        }
    }
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Baron {
    p: Params,
    /// The unit last shielded, and whether it was alive last tick (a respawn shields again).
    shielded: Option<usize>,
    was_alive: bool,
    /// This simulation's number (`SIM_TAG`), drawn at his first spawn.
    sim: u64,
}

impl Baron {
    fn shield(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let amount = magic(self.p.s_amt, self.p.s_ap, ap_of(sim, me));
        let ok = sim.entity_add_shield(me, amount, self.p.s_t);
        let mut mark = BuffV1::named(&sc("p_shield"));
        mark.duration_kind = BuffDurationV1::WithShield.code();
        put(sim, me, &mark);
        self.shielded = Some(me);
        if let Some(k) = counted("shield") {
            wlog(format!("{} SHIELD #{k}: Dominator {amount} for {} ticks{}", head(sim, me), self.p.s_t,
                         if ok { "" } else { " (entity_add_shield refused)" }));
        }
    }
}

impl StablePassive for Baron {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // his monstrosities and fogs go by this number (2026-11-04); a new life starts without the last one's
        TAG.spawn(sim, me, &mut self.sim);
        new_life(self.sim);
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = team_of(sim, me).unwrap_or(0);
            wlog(format!("{} SPAWN #{k}: tft.dll's Silco (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        if alive && (self.shielded != Some(me) || !self.was_alive) {
            PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
            self.shield(sim, me);
        }
        self.was_alive = alive;
        // the shield's picture goes with the last shield (WithShield), but a buff left from a broken shield is cleared
        if alive && has(sim, me, &sc("p_shield")) && sim.get_entity(me).is_some_and(|e| e.shield() == 0) {
            sim.entity_remove_buff(me, &sc("p_shield"));
        }
    }
}

// ===================== 注册 =====================

/// Silco's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Silco: the Dominator's shield at every spawn, monstrosities, the Shimmer fog, Shimmer Shot) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:baron"), Baron::default());
    module.add_native_effect(format!("{ID}:canister"), Canister);
    module.add_native_effect(format!("{ID}:monster"), Monstrosity);
    module.add_native_effect(format!("{ID}:flood"), Flood);
    module.add_native_effect(format!("{ID}:fog"), Fog);
    module.add_native_effect(format!("{ID}:inject"), Inject);
    module.add_native_effect(format!("{ID}:comedown"), Comedown);
    host.log(LogLevel::Info, "tft.dll: Silco (Dominator's shield, monstrosities, Shimmer fog, Shimmer Shot).");
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sim_tag::mock::{step, with_sim, Unit, World};

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"e_as":50,"e_cost":8,"e_ms":20,"e_r":50000,"e_t":240,"m_dmg":15,"m_gap":45,"m_leap":18,"m_life":600,"m_n":5,"m_ratio":11,"m_reach":45000,"q_n":2,"r_fog_dmg":6,"r_fog_r":40000,"r_fog_ratio":4,"r_fog_t":240,"r_n":4,"r_slow":30,"s_amt":120,"s_ap":40,"s_t":900}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn champions_first_then_the_nearest() {
        let foes = [(1, (100, 0), false), (2, (900, 0), true), (3, (500, 0), true), (4, (5000, 0), true)];
        assert_eq!(by_preference(&foes, (0, 0), 1000), vec![3, 2, 1]);
        assert_eq!(by_preference(&foes, (0, 0), 200), vec![1]);
        assert!(by_preference(&foes, (0, 0), 50).is_empty());
    }

    #[test]
    fn monstrosities_spread_over_different_enemies() {
        let foes = [(7, (0, 300), true), (9, (0, 100), true)];
        assert_eq!(victims(&foes, (0, 0), 1000, 4), vec![9, 7, 9, 7]);
        assert_eq!(victims(&foes, (0, 0), 1000, 1), vec![9]);
        assert!(victims(&foes, (0, 0), 10, 2).is_empty());
    }

    #[test]
    fn a_shape_counts_the_body_it_tests() {
        assert!(in_circle((0, 0), 40_000, (43_000, 0), 4_000));
        assert!(!in_circle((0, 0), 40_000, (45_000, 0), 4_000));
        assert!(in_circle((0, 0), 40_000, (40_000, 0), 0));
        let m = Monster { at: (0, 0), victim: None, bites: 1, side: 1, until: 1 };
        assert_eq!(m.bite_picture(), "tft_silco_m_bite_r");
    }

    /// His queued effects, as the game fires them.
    fn fire(sim: &mut StableSim<'_>, name: &str, caster: usize, input: InputTargetV1) {
        match name {
            MONSTER_FX => Monstrosity.apply(sim, 0, caster, input),
            FOG_FX => Fog.apply(sim, 0, caster, input),
            other => panic!("{other} queued"),
        }
    }

    /// Silco #0 (team 0), enemy champions #1 and #2 next to (105000, 0), #3 farther off.
    fn world() -> World {
        let units = vec![Unit::new(0, (0, 0)), Unit::new(1, (100_000, 0)), Unit::new(1, (110_000, 0)),
                         Unit::new(1, (148_000, 0))];
        World { units, ..Default::default() }
    }

    #[test]
    fn monstrosities_bite_through_a_queue_that_keeps_only_the_position() {
        // 11-03 night: 39 of 40 canisters picked victims, not one BITE - the queue handed back 0 bites
        let p = Params::default();
        let bite = magic(p.m_dmg, p.m_ratio, 0);
        // the server's twin presims of one set: Silco is #0 in both, his canisters land on the same tick
        let (mut a, mut b) = (world(), world());
        let (mut pa, mut pb) = (Baron::default(), Baron::default());
        with_sim(&mut a, |sim| pa.on_spawn(sim, 0, 0));
        with_sim(&mut b, |sim| pb.on_spawn(sim, 0, 0));
        assert!(pa.sim > 0 && pb.sim > 0 && pa.sim != pb.sim);
        for x in [&mut a, &mut b] {
            with_sim(x, |sim| Canister.apply(sim, 0, 0, InputTargetV1::pos(105_000, 0)));
        }
        // a: #1 dies after its first bite - its monstrosity leaps to the nearest enemy, #2
        for t in 0..400 {
            if t == 30 {
                a.units[1].alive = false;
            }
            step(&mut a, fire);
            step(&mut b, fire);
        }
        let on = |x: &World, id| x.hits.iter().filter(|h| h.0 == id && h.1 == bite).count();
        assert_eq!((on(&b, 1), on(&b, 2), on(&b, 3)), (p.m_n, p.m_n, 0), "b: q_n monstrosities, m_n bites each");
        assert_eq!((on(&a, 1), on(&a, 2)), (1, 2 * p.m_n - 1), "a: one bite on #1, the rest on #2");
        assert!(a.queue.is_empty() && b.queue.is_empty(), "all melted: nothing queued any more");
        assert!(due(&MONSTERS, (pa.sim, 0), usize::MAX).is_empty());
    }

    #[test]
    fn the_fog_lasts_its_time_and_counts_the_body() {
        let p = Params::default();
        let mut x = world();
        let mut silco = Baron::default();
        with_sim(&mut x, |sim| silco.on_spawn(sim, 0, 0));
        // the giant canister lands 43000 short of #3: only its body (4000) reaches into the fog (r_fog_r 40000)
        with_sim(&mut x, |sim| Flood.apply(sim, 0, 0, InputTargetV1::pos(105_000, 0)));
        for _ in 0..p.r_fog_t + 2 * FOG_GAP {
            step(&mut x, fire);
        }
        let puff = magic(p.r_fog_dmg, p.r_fog_ratio, 0) * FOG_GAP / 60;
        let turns = (p.r_fog_t - 1) / FOG_GAP;
        let fogged = |id| x.hits.iter().filter(|h| h.0 == id && h.1 == puff).count();
        assert_eq!((fogged(1), fogged(2), fogged(3)), (turns, turns, turns));
        assert!(x.units[3].buffs.iter().any(|b| b.name() == sc("r_slow")));
        assert!(due(&FOGS, (silco.sim, 0), usize::MAX).is_empty(), "the fog is gone");
    }

    #[test]
    fn the_comedown_never_kills() {
        assert_eq!(comedown(1000, 8), 920);
        assert_eq!(comedown(1, 8), 1);
        assert_eq!(comedown(10, 99), 1);
    }

    #[test]
    fn names_are_his() {
        assert!(SFX_BITE.starts_with("tft_silco_"));
        for n in [MONSTER_FX, FOG_FX, COMEDOWN_FX] {
            assert!(n.starts_with("tft_silco:"), "{n}");
        }
        assert_eq!(sc("m_leap"), "tft_silco_m_leap");
    }
}
