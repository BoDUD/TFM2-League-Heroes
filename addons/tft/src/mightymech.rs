//! 超级机甲（`tft_mightymech`）数据做不到的部分（金铲铲第 17 赛季的霸天机甲 / 旅人四费卡 The Mighty Mech，红银黑三色的超级
//! 机器人，技能按用户选的方案 A 辅助，2026-11-03）。它的数据（tools/kit/build_mightymech.py）的 `passive` 是这里的
//! `tft_mightymech:escort`，参数从数据的 `passive.params` 来（build_mightymech.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **旅人护航**（被动）：每条命第一次有敌方英雄进到 `p_see` 以内（开打），之后每过 `p_cd` 拍再有一次：`p_r` 以内生命比例
//!   最低的 `p_n` 个友方英雄（不算自己）各得 `p_sh` + 自己最大生命 `p_sh_hp`% 的护盾 `p_t` 拍，自己得那份的 `p_self`%
//!   （金铲铲旅人：开战时坦克得护盾，旅人双倍）。挂护盾时一直在的 `tft_mightymech_p_shield`。数据读不到生命，也没有"开打"的时机。
//! - **引力矩阵的冲击波** `tft_mightymech:shockwave`（数据在防御姿态结束那一拍调用）：`q_r` 以内每个敌人受 `q_dmg` + 自己
//!   （护甲 + 魔抗）的 `q_arm`% 物理伤害（金铲铲原样按双抗算）。数据读不到护甲。
//! - **机甲飞跃** `tft_mightymech:leap`（数据在技能2 出手那一拍调用）：`e_guard` 以内的友方英雄（不算自己）里，身边
//!   `e_near` 以内有敌方英雄、生命比例最低的那个；跳到离那人最近的那个敌方英雄身上（`e_air` 拍，`tft_mightymech:hop`
//!   一拍一拍挪），落地：`e_r` 以内每个敌人受 `e_dmg` + `e_ratio`% 攻击力的物理伤害，其中的敌方英雄击飞 `e_up` 拍。
//!   没人被冲：跳向数据给的目标。数据挑不出"在冲我方后排的那个人"。
//! - **死亡**：倒下时播 `tft_mightymech_d`（数据没有死亡的时机）。
//!
//! 活塞重斩、引力矩阵的减伤 / 嘲讽 / 回血、究极变形·超级战刃是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_mightymech.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_mightymech";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const HOP_FX: &str = "tft_mightymech:hop";

fn mm(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_MIGHTYMECH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_mightymech.log");
        }
    }
    PathBuf::from("tft_mightymech.log")
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
    /// 旅人护航：敌方英雄进到 p_see 以内开打；p_r 以内 p_n 个队友各 p_sh + 最大生命 p_sh_hp% 的护盾 p_t 拍，自己 p_self%；
    /// 之后 p_cd 拍再一次。
    pub p_see: usize,
    pub p_r: usize,
    pub p_n: usize,
    pub p_sh: usize,
    pub p_sh_hp: usize,
    pub p_self: usize,
    pub p_t: usize,
    pub p_cd: usize,
    /// 引力矩阵的冲击波：q_r 以内 q_dmg + （护甲 + 魔抗）q_arm% 的物理伤害。
    pub q_r: usize,
    pub q_dmg: usize,
    pub q_arm: usize,
    /// 机甲飞跃：e_guard 以内的队友、他身边 e_near 以内的敌人；e_air 拍跳到；e_r 以内 e_dmg + e_ratio% 攻击力，英雄击飞 e_up 拍。
    pub e_guard: usize,
    pub e_near: usize,
    pub e_air: usize,
    pub e_r: usize,
    pub e_dmg: usize,
    pub e_ratio: usize,
    pub e_up: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_see: 70000,
            p_r: 60000,
            p_n: 1,
            p_sh: 80,
            p_sh_hp: 6,
            p_self: 200,
            p_t: 600,
            p_cd: 1800,
            q_r: 45000,
            q_dmg: 60,
            q_arm: 60,
            e_guard: 70000,
            e_near: 35000,
            e_air: 24,
            e_r: 30000,
            e_dmg: 60,
            e_ratio: 80,
            e_up: 45,
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
            "p_see" => p.p_see = u,
            "p_r" => p.p_r = u,
            "p_n" => p.p_n = u,
            "p_sh" => p.p_sh = u,
            "p_sh_hp" => p.p_sh_hp = u,
            "p_self" => p.p_self = u,
            "p_t" => p.p_t = u,
            "p_cd" => p.p_cd = u.max(1),
            "q_r" => p.q_r = u,
            "q_dmg" => p.q_dmg = u,
            "q_arm" => p.q_arm = u,
            "e_guard" => p.e_guard = u,
            "e_near" => p.e_near = u,
            "e_air" => p.e_air = u.max(1),
            "e_r" => p.e_r = u,
            "e_dmg" => p.e_dmg = u,
            "e_ratio" => p.e_ratio = u,
            "e_up" => p.e_up = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// 每份模拟一个编号：被动在它第一次出生时抽，每次出生挂在它身上（buff `SIM_TAG<编号>`，没有数值、没有画面；tft_loris 的
/// 做法）。跳跃按 (编号, 它) 记：同时跑的模拟（服务器同一局两份预模拟、观看）实体编号一样，不能共用一份。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
pub const SIM_TAG: &str = "tft_mightymech_sim:";

/// The simulation number hung on this unit (0: none).
fn sim_no(sim: &StableSim<'_>, id: usize) -> u64 {
    sim.get_entity(id).map_or(0, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .find_map(|b| b.name().strip_prefix(SIM_TAG).and_then(|v| v.parse().ok()))
            .unwrap_or(0)
    })
}

/// 一次跳跃：从哪、到哪、哪一拍起跳、哪一拍落地。
#[derive(Clone, Copy, Debug, Default)]
struct Leap {
    from: (u64, u64),
    to: (u64, u64),
    start: usize,
    land: usize,
}

static LEAPS: LazyLock<Mutex<HashMap<(u64, usize), Leap>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

// ===================== 规则（单元测试用） =====================

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

fn dist(a: (u64, u64), b: (u64, u64)) -> u64 {
    (dist_sq(a, b) as f64).sqrt() as u64
}

/// base + ratio% of a stat.
pub fn scaled(base: usize, ratio: usize, stat: usize) -> usize {
    base + stat * ratio / 100
}

/// The escort's shield for an ally (p_sh + p_sh_hp% of its own maximum health) and for itself (p_self% of that).
pub fn escort_shields(max_hp: usize, p: &Params) -> (usize, usize) {
    let ally = scaled(p.p_sh, p.p_sh_hp, max_hp);
    (ally, ally * p.p_self / 100)
}

/// The escorted among (id, health per mille): the `n` with the lowest health share (ties: the lower id).
pub fn escorted(allies: &[(usize, usize)], n: usize) -> Vec<usize> {
    let mut v = allies.to_vec();
    v.sort_by(|a, b| a.1.cmp(&b.1).then(a.0.cmp(&b.0)));
    v.into_iter().take(n).map(|a| a.0).collect()
}

/// The enemy champion diving its back line: among the allies (id, where, health per mille), the lowest health share
/// with an enemy champion (id, where) within `near`; the enemy nearest that ally (ties: the lower id). None: nobody is
/// being dived.
pub fn diver(allies: &[(usize, (u64, u64), usize)], foes: &[(usize, (u64, u64))], near: u64) -> Option<(usize, usize)> {
    let near2 = (near as u128) * (near as u128);
    let mut dived: Vec<_> = allies
        .iter()
        .filter_map(|a| {
            foes.iter()
                .filter(|f| dist_sq(a.1, f.1) <= near2)
                .min_by(|x, y| dist_sq(a.1, x.1).cmp(&dist_sq(a.1, y.1)).then(x.0.cmp(&y.0)))
                .map(|f| (a.0, a.2, f.0))
        })
        .collect();
    dived.sort_by(|a, b| a.1.cmp(&b.1).then(a.0.cmp(&b.0)));
    dived.first().map(|d| (d.0, d.2))
}

/// Its spot on tick `now` of a leap: the straight line from `from` to `to` in `land - start` equal steps.
pub fn leap_at(from: (u64, u64), to: (u64, u64), start: usize, land: usize, now: usize) -> (u64, u64) {
    let total = land.saturating_sub(start).max(1) as f64;
    let k = (now.saturating_sub(start) as f64 / total).min(1.0);
    let x = from.0 as f64 + (to.0 as f64 - from.0 as f64) * k;
    let y = from.1 as f64 + (to.1 as f64 - from.1 as f64) * k;
    (x.round().max(0.0) as u64, y.round().max(0.0) as u64)
}

// ===================== 场上 =====================

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// Live, targetable champions: (id, where, health per mille, ally).
fn champs(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64), usize, bool)> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.champion_count())
        .map(|i| sim.champion_id_at(i))
        .filter_map(|id| sim.get_entity(id))
        .filter(|c| c.is_alive() && c.is_targetable())
        .map(|c| {
            let (hp, max) = c.hp();
            (c.id(), c.pos(), hp * 1000 / max.max(1), c.team() == team)
        })
        .collect()
}

/// Live, targetable enemies of every kind but towers and the nexus: (id, where, champion).
fn enemies(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64), bool)> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower()
            && !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| (u.id(), u.pos(), u.is_champion()))
        .collect()
}

// ===================== 引力矩阵的冲击波 =====================

/// Gravity Matrix's end: the shockwave on its armour + magic resistance.
struct Shockwave;
impl StableEffectType for Shockwave {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some((at, stat)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.pos(), e.stat())) else { return };
        let p = params_of(me);
        let dmg = scaled(p.q_dmg, p.q_arm, stat.defence + stat.magic_resistance);
        let r2 = (p.q_r as u128) * (p.q_r as u128);
        let struck: Vec<usize> = enemies(sim, me).into_iter().filter(|e| dist_sq(at, e.1) <= r2).map(|e| e.0).collect();
        sim.play_sfx(&mm("q_hit"), me, &InputTargetV1::target(me));
        for &id in &struck {
            sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
            sim.play_view_effect(&mm("q_hit"), me, &InputTargetV1::target(id), 0, 0, 0);
        }
        if let Some(k) = counted("shockwave") {
            wlog(format!("{} SHOCKWAVE #{k}: {dmg} (armour {} + mr {}) on {} enemies", head(sim, me), stat.defence,
                         stat.magic_resistance, struck.len()));
        }
    }
}

// ===================== 机甲飞跃 =====================

/// Mecha Leap's cast: the enemy diving its weakest ally (else the data's target), then the leap.
struct LeapFx;
impl StableEffectType for LeapFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let all = champs(sim, me);
        let guard2 = (p.e_guard as u128) * (p.e_guard as u128);
        let allies: Vec<_> =
            all.iter().filter(|c| c.3 && c.0 != me && dist_sq(at, c.1) <= guard2).map(|c| (c.0, c.1, c.2)).collect();
        let foes: Vec<_> = all.iter().filter(|c| !c.3).map(|c| (c.0, c.1)).collect();
        let (target, why) = match diver(&allies, &foes, p.e_near as u64) {
            Some((ally, foe)) => (Some(foe), format!("diving {}", name_of(sim, ally))),
            None if input.kind == InputTargetKindV1::Target.code() => (Some(input.target_id), "its target".to_string()),
            None => (None, "nobody".to_string()),
        };
        let to = target.and_then(|t| sim.get_entity(t)).map_or(at, |e| e.pos());
        let now = sim.tick();
        LEAPS.lock().unwrap_or_else(|e| e.into_inner())
            .insert((sim_no(sim, me), me), Leap { from: at, to, start: now, land: now + p.e_air });
        if let Some(k) = counted("leap") {
            wlog(format!("{} LEAP #{k}: onto {} ({why}), {} away, {} ticks", head(sim, me),
                         target.map_or_else(|| "its own spot".to_string(), |t| name_of(sim, t)), dist(at, to), p.e_air));
        }
        sim.queue_effect(HOP_FX, AttackTypeV1::Skill, me, &InputTargetV1::target(me), 1);
    }
}

/// One tick of the leap (queued again until it lands).
struct Hop;
impl StableEffectType for Hop {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let key = (sim_no(sim, me), me);
        let Some(l) = LEAPS.lock().unwrap_or_else(|e| e.into_inner()).get(&key).copied() else { return };
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key);
            return;
        }
        let now = sim.tick();
        let spot = leap_at(l.from, l.to, l.start, l.land, now);
        sim.entity_set_pos(me, spot.0, spot.1);
        if now < l.land {
            sim.queue_effect(HOP_FX, AttackTypeV1::Skill, me, &InputTargetV1::target(me), 1);
            return;
        }
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key);
        land(sim, me, l.to);
    }
}

fn land(sim: &mut StableSim<'_>, me: usize, at: (u64, u64)) {
    let p = params_of(me);
    let atk = sim.get_entity(me).map_or(0, |e| e.stat().attack);
    let dmg = scaled(p.e_dmg, p.e_ratio, atk);
    let r2 = (p.e_r as u128) * (p.e_r as u128);
    let struck: Vec<_> = enemies(sim, me).into_iter().filter(|e| dist_sq(at, e.1) <= r2).collect();
    let here = InputTargetV1::pos(at.0, at.1);
    sim.play_view_effect(&mm("e_slam"), me, &here, 0, 0, 0);
    sim.play_sfx(&mm("e_hit"), me, &here);
    let mut up = Vec::new();
    for &(id, _, champ) in &struck {
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
        if champ && sim.get_entity(id).is_some_and(|e| e.is_alive()) {
            sim.apply_cc(id, &CcV1::of_kind(CcKindV1::Airborne, p.e_up as u64));
            sim.play_view_effect(&mm("e_up"), me, &InputTargetV1::target(id), 0, 0, 0);
            up.push(id);
        }
    }
    if let Some(k) = counted("land") {
        wlog(format!("{} LAND #{k}: at ({}, {}), {dmg} on {} enemies, knocked up {:?}", head(sim, me), at.0, at.1,
                     struck.len(), up.iter().map(|&t| name_of(sim, t)).collect::<Vec<_>>()));
    }
}

// ===================== 被动：旅人护航 =====================

#[derive(Clone, Default)]
struct Escort {
    /// The champion it belongs to (on_dead is given the player, not the unit).
    me: usize,
    p: Params,
    /// The tick from which the escort can come again (0 at each life's start), whether it was alive last tick.
    ready: usize,
    was_alive: bool,
    /// This simulation's number (`SIM_TAG`), drawn at its first spawn.
    sim: u64,
}

impl Escort {
    fn escort(&mut self, sim: &mut StableSim<'_>, me: usize, at: (u64, u64), max: usize) {
        let p = self.p;
        let r2 = (p.p_r as u128) * (p.p_r as u128);
        let allies: Vec<(usize, usize)> = champs(sim, me)
            .into_iter()
            .filter(|c| c.3 && c.0 != me && dist_sq(at, c.1) <= r2)
            .map(|c| (c.0, c.2))
            .collect();
        let to = escorted(&allies, p.p_n);
        let (ally_sh, self_sh) = escort_shields(max, &p);
        let mut ok = sim.entity_add_shield(me, self_sh, p.p_t);
        for &id in &to {
            ok &= sim.entity_add_shield(id, ally_sh, p.p_t);
        }
        for &id in to.iter().chain(std::iter::once(&me)) {
            let mut mark = BuffV1::named(&mm("p_shield"));
            mark.duration_kind = BuffDurationV1::WithShield.code();
            put(sim, id, &mark);
        }
        sim.play_sfx(&mm("p"), me, &InputTargetV1::target(me));
        self.ready = sim.tick() + p.p_cd;
        if let Some(k) = counted("escort") {
            wlog(format!("{} ESCORT #{k}: itself {self_sh}, {} {ally_sh} each, {} ticks{}", head(sim, me),
                         if to.is_empty() { "nobody else".to_string() } else {
                             to.iter().map(|&t| name_of(sim, t)).collect::<Vec<_>>().join(", ") },
                         p.p_t, if ok { "" } else { " (entity_add_shield refused)" }));
        }
    }
}

impl StablePassive for Escort {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // a new life is a new unit, and on_update does not run while it is dead: the first tick of this life must see
        // a dead one, or the escort stays used up (tft_loris, the 2026-11-02 logs)
        self.me = me;
        self.was_alive = false;
        if self.sim == 0 {
            self.sim = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Mighty Mech (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((alive, at, max, team)) = sim.get_entity(me).map(|e| (e.is_alive(), e.pos(), e.hp().1, e.team())) else {
            return;
        };
        if alive && !self.was_alive {   // the first tick of a life: the escort is ready again
            PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
            self.ready = 0;
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        if sim.tick() >= self.ready {
            let see2 = (self.p.p_see as u128) * (self.p.p_see as u128);
            let fight = (0..sim.champion_count())
                .map(|i| sim.champion_id_at(i))
                .filter_map(|id| sim.get_entity(id))
                .any(|c| c.team() != team && c.is_alive() && c.is_targetable() && dist_sq(at, c.pos()) <= see2);
            if fight {
                self.escort(sim, me, at, max);
            }
        }
        // the shield's picture goes with the last shield (WithShield), but a buff left from a broken shield is cleared
        if has(sim, me, &mm("p_shield")) && sim.get_entity(me).is_some_and(|e| e.shield() == 0) {
            sim.entity_remove_buff(me, &mm("p_shield"));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        let me = self.me;
        // it crashes down (the data has no moment for it); a leap in the air ends there
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&(self.sim, me));
        sim.play_sfx(&mm("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// The Mighty Mech's escort, shockwave and leap, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (The Mighty Mech: the Voyager escort, Gravity Matrix's shockwave, the Mecha Leap) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:escort"), Escort::default());
    module.add_native_effect(format!("{ID}:shockwave"), Shockwave);
    module.add_native_effect(format!("{ID}:leap"), LeapFx);
    module.add_native_effect(HOP_FX, Hop);
    host.log(LogLevel::Info, "tft.dll: The Mighty Mech (the escort, the shockwave, the leap).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"e_air":24,"e_dmg":60,"e_guard":70000,"e_near":35000,"e_r":30000,"e_ratio":80,"e_up":45,"p_cd":1800,"p_n":1,"p_r":60000,"p_see":70000,"p_self":200,"p_sh":80,"p_sh_hp":6,"p_t":600,"q_arm":60,"q_dmg":60,"q_r":45000}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_escort() {
        let p = Params::default();
        assert_eq!(escort_shields(2000, &p), (200, 400));   // 80 + 6% of 2000, itself twice
        let a = [(2, 700), (3, 300), (4, 300), (5, 900)];
        assert_eq!(escorted(&a, 1), vec![3]);           // the lowest share, ties by id
        assert_eq!(escorted(&a, 2), vec![3, 4]);
        assert_eq!(escorted(&[], 1), Vec::<usize>::new());
    }

    #[test]
    fn the_diver() {
        // ally 2 healthy with an enemy on it, ally 3 hurt with two enemies near, ally 4 hurt alone
        let allies = [(2, (0, 0), 900), (3, (100000, 0), 400), (4, (200000, 0), 100)];
        let foes = [(10, (10000, 0)), (11, (120000, 0)), (12, (110000, 5000))];
        assert_eq!(diver(&allies, &foes, 35000), Some((3, 12)));   // the hurt one being dived, the nearest enemy on him
        assert_eq!(diver(&allies[..1], &foes, 35000), Some((2, 10)));
        assert_eq!(diver(&allies[2..], &foes, 35000), None);         // nobody near the one alone
        assert_eq!(scaled(60, 60, 200), 180);
    }

    #[test]
    fn the_leap() {
        assert_eq!(leap_at((0, 0), (30000, 0), 10, 40, 10), (0, 0));
        assert_eq!(leap_at((0, 0), (30000, 0), 10, 40, 25), (15000, 0));
        assert_eq!(leap_at((0, 0), (30000, 0), 10, 40, 99), (30000, 0));
    }
}
