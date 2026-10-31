//! 小木灵（`tft_meepsie`）数据做不到的部分（金铲铲第 17 赛季的木灵族 / 牧羊人 / 旅人二费卡 Meepsie，月岩巨像和驾驶它的
//! 小木灵，技能按用户选的方案 A「木灵守护」，2026-11-01）。它的数据（tools/kit/build_meepsie.py）的 `passive` 是这里的
//! `tft_meepsie:pilot`，参数从数据的 `passive.params` 来（build_meepsie.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **治疗木灵** `tft_meepsie:meeps`（数据在 E 出手那一拍调用）：`e_r` 以内生命比例最低的 `e_n` 个友方英雄（先别人，名额
//!   有剩才算自己）各飞去一只小木灵（`tft_meepsie_e_meep`，每拍 `e_speed`）；落到谁身上（`tft_meepsie:mend`），谁就
//!   `e_t` 拍里每 `e_every` 拍回 `e_hot` + `e_hot_ap`% 法强（挂 `tft_meepsie_e_hot`，带画面）。再中一只只续时间。数据读不到
//!   生命，挑不出最需要的人。
//! - **宇宙大爆炸** `tft_meepsie:bigbang`（数据在大招出手那一拍调用，金铲铲原技能）：在自己 `r_leap` 以内找一个落点，
//!   让 `r_r` 以内的敌方英雄最多（候选：每个敌方英雄脚下、每两个之间的中点；一样多取离目标近的），`r_air` 拍跳过去
//!   （`tft_meepsie:hop` 一拍一拍挪），落地砸地：`r_r` 以内每个敌人受 `r_dmg` + `r_ap`% 法强的魔法伤害，离落点每远
//!   `r_hex` 少 `r_fall`%；离落点最近的 `r_n` 个敌方英雄被击飞 `r_up` 拍。数据挑不出落点，也算不了按距离衰减和"最近的三个"。
//! - **死亡**：倒下时播 `tft_meepsie_d`（数据没有死亡的时机）。
//!
//! 月岩重拳 + 木灵驾驶员的额外魔法伤害、月尘震地是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_meepsie.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_meepsie";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const MEND_FX: &str = "tft_meepsie:mend";
const MEND_TICK_FX: &str = "tft_meepsie:mend_tick";
const HOP_FX: &str = "tft_meepsie:hop";

fn mp(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_MEEPSIE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_meepsie.log");
        }
    }
    PathBuf::from("tft_meepsie.log")
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
    /// 治疗木灵：e_r 以内最多 e_n 个友方英雄，每只每拍飞 e_speed；中了的人 e_t 拍里每 e_every 拍回 e_hot + e_hot_ap% 法强。
    pub e_r: usize,
    pub e_n: usize,
    pub e_speed: usize,
    pub e_t: usize,
    pub e_every: usize,
    pub e_hot: usize,
    pub e_hot_ap: usize,
    /// 宇宙大爆炸：r_leap 以内找落点，r_air 拍跳到；r_r 以内 r_dmg + r_ap% 法强，每远 r_hex 少 r_fall%；最近 r_n 个
    /// 敌方英雄击飞 r_up 拍。
    pub r_leap: usize,
    pub r_air: usize,
    pub r_r: usize,
    pub r_hex: usize,
    pub r_fall: usize,
    pub r_dmg: usize,
    pub r_ap: usize,
    pub r_n: usize,
    pub r_up: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            e_r: 60000,
            e_n: 4,
            e_speed: 2500,
            e_t: 180,
            e_every: 30,
            e_hot: 20,
            e_hot_ap: 10,
            r_leap: 45000,
            r_air: 30,
            r_r: 45000,
            r_hex: 15000,
            r_fall: 35,
            r_dmg: 160,
            r_ap: 90,
            r_n: 3,
            r_up: 75,
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
            "e_r" => p.e_r = u,
            "e_n" => p.e_n = u,
            "e_speed" => p.e_speed = u.max(1),
            "e_t" => p.e_t = u,
            "e_every" => p.e_every = u.max(1),
            "e_hot" => p.e_hot = u,
            "e_hot_ap" => p.e_hot_ap = u,
            "r_leap" => p.r_leap = u,
            "r_air" => p.r_air = u.max(1),
            "r_r" => p.r_r = u,
            "r_hex" => p.r_hex = u.max(1),
            "r_fall" => p.r_fall = u.min(100),
            "r_dmg" => p.r_dmg = u,
            "r_ap" => p.r_ap = u,
            "r_n" => p.r_n = u,
            "r_up" => p.r_up = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// 一次跳跃：从哪、到哪、哪一拍落地。
#[derive(Clone, Copy, Debug, Default)]
struct Leap {
    from: (u64, u64),
    to: (u64, u64),
    start: usize,
    land: usize,
}

/// 一个人身上的木灵治疗：谁给的、到哪一拍为止、上次回在哪一拍。
#[derive(Clone, Copy, Debug, Default)]
pub struct Mend {
    pub by: usize,
    pub until: usize,
    pub last: usize,
}

/// 按（种子、模拟来源、比赛、局、单位）分开：同一个进程里预演和观看的模拟各算各的（league_loris 的做法）。
type Key = (u64, u32, u64, u64, usize);
static LEAPS: LazyLock<Mutex<HashMap<Key, Leap>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static MENDS: LazyLock<Mutex<HashMap<Key, Mend>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn key(sim: &StableSim<'_>, id: usize) -> Key {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index, id)
}

// ===================== 规则（单元测试用） =====================

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

fn dist(a: (u64, u64), b: (u64, u64)) -> u64 {
    (dist_sq(a, b) as f64).sqrt() as u64
}

/// base + ratio% of the ability power.
pub fn magic(base: usize, ratio: usize, ap: usize) -> usize {
    base + ap * ratio / 100
}

/// The meeps' patients among (id, health per mille, is me): the `n` others with the lowest health share (ties: the
/// lower id), then itself if a slot is left.
pub fn patients(allies: &[(usize, usize, bool)], n: usize) -> Vec<usize> {
    let mut others: Vec<_> = allies.iter().filter(|a| !a.2).collect();
    others.sort_by(|a, b| a.1.cmp(&b.1).then(a.0.cmp(&b.0)));
    let mut out: Vec<usize> = others.iter().take(n).map(|a| a.0).collect();
    if out.len() < n {
        out.extend(allies.iter().filter(|a| a.2).map(|a| a.0));
    }
    out
}

/// Whether a queued heal tick at `now` heals: the mend still on and a full period since the last one (the ticks each
/// meep queues overlap; one heals per period).
pub fn mends_now(m: &Mend, now: usize, every: usize) -> bool {
    now <= m.until && now >= m.last + every
}

/// Where to land among the enemy champions (id, where): the candidate (each one's spot, each pair's midpoint) within
/// `leap` of `at` with the most enemy champions within `r`; ties go to the one nearest `aim` (its target's spot), then
/// the first. None with nobody in reach.
pub fn landing(at: (u64, u64), foes: &[(usize, (u64, u64))], leap: u64, r: u64, aim: (u64, u64)) -> Option<(u64, u64)> {
    let mut cands: Vec<(u64, u64)> = foes.iter().map(|f| f.1).collect();
    for (i, a) in foes.iter().enumerate() {
        for b in &foes[i + 1..] {
            cands.push(((a.1 .0 + b.1 .0) / 2, (a.1 .1 + b.1 .1) / 2));
        }
    }
    let leap2 = (leap as u128) * (leap as u128);
    let r2 = (r as u128) * (r as u128);
    cands
        .into_iter()
        .filter(|c| dist_sq(at, *c) <= leap2)
        .map(|c| (foes.iter().filter(|f| dist_sq(c, f.1) <= r2).count(), c))
        .filter(|(n, _)| *n > 0)
        .max_by(|a, b| a.0.cmp(&b.0).then(dist_sq(b.1, aim).cmp(&dist_sq(a.1, aim))))
        .map(|(_, c)| c)
}

/// The slam's damage at `d` from the centre: full, `fall`% less for every whole `hex` out, never under zero.
pub fn falloff(full: usize, d: u64, hex: u64, fall: usize) -> usize {
    let rings = (d / hex.max(1)) as usize;
    full * 100usize.saturating_sub(rings * fall) / 100
}

/// The `n` enemy champions nearest the landing point (ties: the lower id).
pub fn nearest(at: (u64, u64), champs: &[(usize, (u64, u64))], n: usize) -> Vec<usize> {
    let mut v: Vec<_> = champs.to_vec();
    v.sort_by(|a, b| dist_sq(at, a.1).cmp(&dist_sq(at, b.1)).then(a.0.cmp(&b.0)));
    v.into_iter().take(n).map(|c| c.0).collect()
}

/// Its spot on tick `now` of a leap: the straight line from `from` to `to` in `land - start` equal steps.
pub fn leap_at(l: &(u64, u64, u64, u64, usize, usize), now: usize) -> (u64, u64) {
    let (fx, fy, tx, ty, start, land) = *l;
    let total = land.saturating_sub(start).max(1) as f64;
    let k = (now.saturating_sub(start) as f64 / total).min(1.0);
    let x = fx as f64 + (tx as f64 - fx as f64) * k;
    let y = fy as f64 + (ty as f64 - fy as f64) * k;
    (x.round().max(0.0) as u64, y.round().max(0.0) as u64)
}

// ===================== 场上 =====================

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

fn team_of(sim: &StableSim<'_>, id: usize) -> Option<usize> {
    sim.get_entity(id).map(|e| e.team())
}

/// Live, targetable champions: (id, where, health per mille, ally).
fn champs(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64), usize, bool)> {
    let Some(team) = team_of(sim, me) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_alive() && u.is_targetable() && u.is_champion())
        .map(|u| {
            let (hp, max) = u.hp();
            (u.id(), u.pos(), hp * 1000 / max.max(1), u.team() == team)
        })
        .collect()
}

/// Live, targetable enemies of every kind (the slam strikes minions and monsters too): (id, where, champion).
fn enemies(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64), bool)> {
    let Some(team) = team_of(sim, me) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower()
            && !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| (u.id(), u.pos(), u.is_champion()))
        .collect()
}

fn ap_of(sim: &StableSim<'_>, me: usize) -> usize {
    sim.get_entity(me).map_or(0, |e| e.stat().magic_power)
}

// ===================== 治疗木灵 =====================

/// E's cast: a meep flies to each of the e_n allied champions in most need within e_r.
struct Meeps;
impl StableEffectType for Meeps {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some((at, team)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.pos(), e.team())) else { return };
        let p = params_of(me);
        let r2 = (p.e_r as u128) * (p.e_r as u128);
        let allies: Vec<(usize, usize, bool)> = champs(sim, me)
            .into_iter()
            .filter(|c| c.3 && dist_sq(at, c.1) <= r2)
            .map(|c| (c.0, c.2, c.0 == me))
            .collect();
        let to = patients(&allies, p.e_n);
        let mut direct = 0;
        for &t in &to {
            if t == me {   // its own meep never leaves the cockpit: the mend at once
                mend(sim, me, t);
                continue;
            }
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team,
                x: at.0,
                y: at.1,
                radius: 4000,
                speed: p.e_speed as u64,
                move_kind: ProjectileMoveKindV1::Target.code(),
                target_id: t,
                target_x: 0,
                target_y: 0,
                penetrate: false,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::AllyChampion.code(),
            };
            if !sim.spawn_projectile(&mp("e_meep"), MEND_FX, &spec) {
                direct += 1;   // refused: the mend lands at once rather than not at all
                mend(sim, me, t);
            }
        }
        if !to.is_empty() {
            sim.play_sfx(&mp("e_fly"), me, &InputTargetV1::target(me));
        }
        if let Some(k) = counted("meeps") {
            wlog(format!(
                "{} MEEPS #{k}: to {:?}{}",
                head(sim, me),
                to.iter().map(|&t| name_of(sim, t)).collect::<Vec<_>>(),
                if direct > 0 { format!(" - spawn_projectile refused {direct}, mended at once") } else { String::new() }
            ));
        }
    }
}

/// A meep lands on an ally.
struct MendFx;
impl StableEffectType for MendFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind == InputTargetKindV1::Target.code() {
            mend(sim, me, input.target_id);
        }
    }
}

fn mend(sim: &mut StableSim<'_>, me: usize, id: usize) {
    if !sim.get_entity(id).is_some_and(|e| e.is_alive()) {
        return;
    }
    let p = params_of(me);
    let now = sim.tick();
    let fresh = {
        let mut mends = MENDS.lock().unwrap_or_else(|e| e.into_inner());
        let m = mends.entry(key(sim, id)).or_default();
        let fresh = now > m.until;
        if fresh {
            m.last = now;   // the first heal a full period after the landing
        }
        m.by = me;
        m.until = now + p.e_t;
        fresh
    };
    put(sim, id, &BuffV1::timed(&mp("e_hot"), p.e_t));
    let on = InputTargetV1::target(id);
    sim.play_sfx(&mp("e_heal"), me, &on);
    for k in 1..=p.e_t / p.e_every {
        sim.queue_effect(MEND_TICK_FX, AttackTypeV1::Skill, me, &on, k * p.e_every);
    }
    if let Some(k) = counted("mend") {
        wlog(format!("{} MEND #{k}: {} ({})", head(sim, me), name_of(sim, id), if fresh { "new" } else { "renewed" }));
    }
}

/// One heal of a mend (queued by every meep; one heals per period while the mend lasts).
struct MendTick;
impl StableEffectType for MendTick {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let id = input.target_id;
        let k_ = key(sim, id);
        if !sim.get_entity(id).is_some_and(|e| e.is_alive()) {
            MENDS.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
            return;
        }
        let p = params_of(me);
        let now = sim.tick();
        let by = {
            let mut mends = MENDS.lock().unwrap_or_else(|e| e.into_inner());
            let Some(m) = mends.get_mut(&k_) else { return };
            if !mends_now(m, now, p.e_every) {
                return;
            }
            m.last = now;
            m.by
        };
        if by != me {
            return;   // another Meepsie's meep: its own ticks heal it
        }
        let amount = magic(p.e_hot, p.e_hot_ap, ap_of(sim, me));
        sim.heal(me, id, amount);
        if let Some(k) = counted("mend_tick") {
            wlog(format!("{} HEAL #{k}: {} +{amount}", head(sim, me), name_of(sim, id)));
        }
    }
}

// ===================== 宇宙大爆炸 =====================

/// The ult's cast: pick the landing point, start the leap.
struct BigBang;
impl StableEffectType for BigBang {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let foes: Vec<(usize, (u64, u64))> = champs(sim, me).into_iter().filter(|c| !c.3).map(|c| (c.0, c.1)).collect();
        let aim = if input.kind == InputTargetKindV1::Target.code() {
            sim.get_entity(input.target_id).map_or(at, |e| e.pos())
        } else {
            at
        };
        // nobody within the leap: it slams on its target (the cast's range let it start), else where it stands
        let to = landing(at, &foes, p.r_leap as u64, p.r_r as u64, aim).unwrap_or(aim);
        let now = sim.tick();
        let k_ = key(sim, me);
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).insert(k_, Leap { from: at, to, start: now, land: now + p.r_air });
        if let Some(k) = counted("leap") {
            wlog(format!("{} LEAP #{k}: from ({}, {}) to ({}, {}), {} away, {} ticks", head(sim, me), at.0, at.1, to.0,
                         to.1, dist(at, to), p.r_air));
        }
        sim.queue_effect(HOP_FX, AttackTypeV1::Skill, me, &InputTargetV1::target(me), 1);
    }
}

/// One tick of the leap (queued again until it lands).
struct Hop;
impl StableEffectType for Hop {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let k_ = key(sim, me);
        let Some(l) = LEAPS.lock().unwrap_or_else(|e| e.into_inner()).get(&k_).copied() else { return };
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
            return;
        }
        let now = sim.tick();
        let spot = leap_at(&(l.from.0, l.from.1, l.to.0, l.to.1, l.start, l.land), now);
        sim.entity_set_pos(me, spot.0, spot.1);
        if now + 3 == l.land {
            sim.play_sfx(&mp("r_into"), me, &InputTargetV1::target(me));
        }
        if now < l.land {
            sim.queue_effect(HOP_FX, AttackTypeV1::Skill, me, &InputTargetV1::target(me), 1);
            return;
        }
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
        slam(sim, me, l.to);
    }
}

fn slam(sim: &mut StableSim<'_>, me: usize, at: (u64, u64)) {
    let p = params_of(me);
    let full = magic(p.r_dmg, p.r_ap, ap_of(sim, me));
    let r2 = (p.r_r as u128) * (p.r_r as u128);
    let struck: Vec<_> = enemies(sim, me).into_iter().filter(|e| dist_sq(at, e.1) <= r2).collect();
    let here = InputTargetV1::pos(at.0, at.1);
    sim.play_view_effect(&mp("r_slam"), me, &here, 0, 0, 0);
    sim.play_sfx(&mp("r_hit"), me, &here);
    let mut dealt = Vec::new();
    for &(id, pos, _) in &struck {
        let d = falloff(full, dist(at, pos), p.r_hex as u64, p.r_fall);
        if d > 0 {
            sim.deal_damage_typed(me, id, d, DamageTypeV1::Ap, AttackTypeV1::Skill);
        }
        dealt.push(d);
    }
    let champs_in: Vec<(usize, (u64, u64))> = struck.iter().filter(|e| e.2).map(|e| (e.0, e.1)).collect();
    let up = nearest(at, &champs_in, p.r_n);
    for &id in &up {
        if sim.get_entity(id).is_some_and(|e| e.is_alive()) {
            sim.apply_cc(id, &CcV1::of_kind(CcKindV1::Airborne, p.r_up as u64));
            sim.play_view_effect(&mp("r_up"), me, &InputTargetV1::target(id), 0, 0, 0);
        }
    }
    if let Some(k) = counted("slam") {
        wlog(format!(
            "{} SLAM #{k}: at ({}, {}), {} struck {:?}, knocked up {:?}",
            head(sim, me),
            at.0,
            at.1,
            struck.len(),
            dealt,
            up.iter().map(|&t| name_of(sim, t)).collect::<Vec<_>>()
        ));
    }
}

// ===================== 被动：木灵驾驶员 =====================

#[derive(Clone, Default)]
struct Pilot {
    p: Params,
}

impl StablePassive for Pilot {
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
            wlog(format!("{} SPAWN #{k}: tft.dll's Meepsie (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, _: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        // it falls on its face (the data has no moment for it); a leap in the air ends there
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me));
        sim.play_sfx(&mp("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// Meepsie's healing meeps and its Big Bang, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Meepsie: the healing meeps, the Big Bang) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:pilot"), Pilot::default());
    module.add_native_effect(format!("{ID}:meeps"), Meeps);
    module.add_native_effect(format!("{ID}:bigbang"), BigBang);
    module.add_native_effect(MEND_FX, MendFx);
    module.add_native_effect(MEND_TICK_FX, MendTick);
    module.add_native_effect(HOP_FX, Hop);
    host.log(LogLevel::Info, "tft.dll: Meepsie (the healing meeps, the Big Bang).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"e_every":30,"e_hot":20,"e_hot_ap":10,"e_n":4,"e_r":60000,"e_speed":2500,"e_t":180,"r_air":30,"r_ap":90,"r_dmg":160,"r_fall":35,"r_hex":15000,"r_leap":45000,"r_n":3,"r_r":45000,"r_up":75}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_patients() {
        // (id, health per mille, me)
        let a = [(1, 900, true), (2, 300, false), (3, 800, false), (4, 100, false), (5, 600, false), (6, 300, false)];
        assert_eq!(patients(&a, 4), vec![4, 2, 6, 5]);      // the four lowest others, ties by id; not itself
        assert_eq!(patients(&a[..3], 4), vec![2, 3, 1]);    // a slot left: itself too
        assert_eq!(patients(&a[..1], 4), vec![1]);
        let m = Mend { by: 1, until: 200, last: 20 };
        assert!(!mends_now(&m, 40, 30));
        assert!(mends_now(&m, 50, 30));
        assert!(!mends_now(&m, 201, 30));
    }

    #[test]
    fn the_landing() {
        // three close together to the right, one alone to the left
        let foes = [(1, (100000, 0)), (2, (110000, 0)), (3, (105000, 10000)), (4, (40000, 0))];
        let at = (70000, 0);
        let to = landing(at, &foes, 45000, 20000, (40000, 0)).unwrap();
        assert!(dist(to, (105000, 3000)) < 10000, "{to:?}");      // the group, not its target alone
        assert_eq!(landing(at, &foes, 45000, 45000, (40000, 0)), Some((70000, 0)));   // wide: all four from between
        assert_eq!(landing(at, &foes[3..], 45000, 45000, (40000, 0)), Some((40000, 0)));
        assert_eq!(landing((0, 0), &foes, 20000, 45000, (0, 0)), None);   // nobody within the leap
    }

    #[test]
    fn the_slam() {
        assert_eq!(falloff(300, 0, 15000, 35), 300);
        assert_eq!(falloff(300, 16000, 15000, 35), 195);
        assert_eq!(falloff(300, 31000, 15000, 35), 90);
        assert_eq!(falloff(300, 46000, 15000, 35), 0);   // never under zero
        let c = [(1, (10000, 0)), (2, (3000, 0)), (3, (30000, 0)), (4, (3000, 0))];
        assert_eq!(nearest((0, 0), &c, 3), vec![2, 4, 1]);
        assert_eq!(magic(160, 90, 100), 250);
        let l = (0, 0, 30000, 0, 10, 40);
        assert_eq!(leap_at(&l, 10), (0, 0));
        assert_eq!(leap_at(&l, 25), (15000, 0));
        assert_eq!(leap_at(&l, 40), (30000, 0));
        assert_eq!(leap_at(&l, 99), (30000, 0));
    }
}
