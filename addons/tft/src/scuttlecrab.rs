//! 迅捷蟹（`tft_scuttlecrab`）数据做不到的部分（金铲铲第 18 赛季的峡谷野怪 / 主宰二费卡 Scuttle Crab，河道里背着青绿
//! 甲壳的螃蟹，技能按用户选的方案 A「河道守护」，2026-11-01）。它的数据（tools/kit/build_scuttlecrab.py）的 `passive` 是
//! 这里的 `tft_scuttlecrab:greenbuff`，参数从数据的 `passive.params` 来（build_scuttlecrab.py 从参数表 P 写进去，
//! `NATIVE_KEYS`）：
//!
//! - **绿霸符**（金铲铲的羁绊）：本被动每拍看 `p_r` 以内的友方英雄（连它自己）：谁的生命掉到最大生命的 `p_low`% 以下、
//!   且他自己的冷却已过，谁就回最大生命的 `p_pct`%，亮一下 `tft_scuttlecrab_p_heal`，播 `tft_scuttlecrab_p`；之后这个人
//!   `p_cd` 拍内不再有。数据读不到生命。
//! - **蟹壳护盾碎裂**：数据在 E 出手时给它护盾和 `e_t` 拍的标记 `tft_scuttlecrab_e_shell`；本被动每拍看：护盾打光了、
//!   或者标记到时间了，蟹壳就碎：`e_r` 以内每个敌人（不算塔）受 `e_dmg` + `e_dmg_ap`% 法强的魔法伤害、眩晕 `e_stun` 拍、
//!   `e_slow_t` 拍里慢 `e_slow`%（挂 `tft_scuttlecrab_e_slow`），它身上亮 `tft_scuttlecrab_e_burst`，
//!   播 `tft_scuttlecrab_e_break`（打到人时再在第一个人身上播 `tft_scuttlecrab_e_slow`）。
//!   数据读不到护盾。
//! - **死亡**：倒下时播 `tft_scuttlecrab_d`（数据没有死亡的时机）。
//!
//! 螃蟹舞、疾行神龛、蟹壳护盾本身和「你挖得动吗？」是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_scuttlecrab.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_scuttlecrab";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn sc(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_SCUTTLECRAB_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_scuttlecrab.log");
        }
    }
    PathBuf::from("tft_scuttlecrab.log")
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
    /// 绿霸符：p_r 以内的友方英雄（连自己）生命低于 p_low% 时回最大生命的 p_pct%；之后这个人 p_cd 拍内不再有。
    pub p_low: usize,
    pub p_pct: usize,
    pub p_r: u64,
    pub p_cd: usize,
    /// 蟹壳护盾：标记 e_t 拍；碎时 e_r 以内的敌人受 e_dmg + e_dmg_ap% 法强、眩晕 e_stun 拍、e_slow_t 拍里慢 e_slow%。
    pub e_t: usize,
    pub e_r: u64,
    pub e_dmg: usize,
    pub e_dmg_ap: usize,
    pub e_slow: usize,
    pub e_slow_t: usize,
    pub e_stun: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_low: 40,
            p_pct: 12,
            p_r: 70000,
            p_cd: 600,
            e_t: 120,
            e_r: 40000,
            e_dmg: 80,
            e_dmg_ap: 60,
            e_slow: 40,
            e_slow_t: 90,
            e_stun: 30,
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
            "p_low" => p.p_low = u.min(100),
            "p_pct" => p.p_pct = u,
            "p_r" => p.p_r = u as u64,
            "p_cd" => p.p_cd = u,
            "e_t" => p.e_t = u,
            "e_r" => p.e_r = u as u64,
            "e_dmg" => p.e_dmg = u,
            "e_dmg_ap" => p.e_dmg_ap = u,
            "e_slow" => p.e_slow = u.min(100),
            "e_slow_t" => p.e_slow_t = u,
            "e_stun" => p.e_stun = u,
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// The Green Buff is due for someone: alive, under p_low% of the maximum health, and `ready` (the cooldown over).
pub fn due(hp: usize, max: usize, ready: bool, p: &Params) -> bool {
    ready && hp > 0 && max > 0 && hp * 100 < max * p.p_low
}

/// The Green Buff's heal: p_pct% of the maximum health, at least 1.
pub fn green_amount(max: usize, p: &Params) -> usize {
    (max * p.p_pct / 100).max(1)
}

/// base + ratio% of the ability power.
pub fn magic(base: usize, ratio: usize, ap: usize) -> usize {
    base + ap * ratio / 100
}

/// The shell bursts this tick: its mark is gone (e_t ran out) or the shield is spent.
pub fn bursts(marked: bool, shield: usize) -> bool {
    !marked || shield == 0
}

// ===================== 模拟里的小工具 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// Its allied champions within `reach` (itself too): alive, targetable; (id, hp, max).
fn allies_near(sim: &StableSim<'_>, me: usize, reach: u64) -> Vec<(usize, usize, usize)> {
    let Some((team, at)) = sim.get_entity(me).map(|e| (e.team(), e.pos())) else { return Vec::new() };
    let r2 = (reach as u128) * (reach as u128);
    (0..sim.champion_count())
        .map(|i| sim.champion_id_at(i))
        .filter_map(|id| sim.get_entity(id))
        .filter(|c| c.team() == team && c.is_alive() && c.is_targetable() && dist_sq(c.pos(), at) <= r2)
        .map(|c| {
            let (hp, max) = c.hp();
            (c.id(), hp, max)
        })
        .collect()
}

/// Live, targetable enemies within `reach` of every kind but towers and the nexus.
fn enemies_near(sim: &StableSim<'_>, me: usize, reach: u64) -> Vec<usize> {
    let Some((team, at)) = sim.get_entity(me).map(|e| (e.team(), e.pos())) else { return Vec::new() };
    let r2 = (reach as u128) * (reach as u128);
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower()
            && !matches!(u.kind(), Some(EntityKindV1::Nexus)) && dist_sq(u.pos(), at) <= r2)
        .map(|u| u.id())
        .collect()
}

/// A named buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct GreenBuff {
    p: Params,
    /// The tick each ally's Green Buff is ready again (none: ready).
    ready_at: HashMap<usize, usize>,
    /// Whether the shell's mark was on it last tick (a mark coming on arms the burst).
    shell: bool,
}

impl GreenBuff {
    fn green(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        for (id, hp, max) in allies_near(sim, me, self.p.p_r) {
            let ready = self.ready_at.get(&id).is_none_or(|&t| now >= t);
            if !due(hp, max, ready, &self.p) {
                continue;
            }
            let amount = green_amount(max, &self.p);
            sim.heal(me, id, amount);
            sim.play_view_effect(&sc("p_heal"), me, &InputTargetV1::target(id), 0, 0, 0);
            sim.play_sfx(&sc("p"), me, &InputTargetV1::target(id));
            self.ready_at.insert(id, now + self.p.p_cd);
            if let Some(k) = counted("green") {
                wlog(format!("{} GREEN #{k}: {} at {hp}/{max} +{amount}", head(sim, me), name_of(sim, id)));
            }
        }
    }

    fn burst(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        let p = self.p;
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let dmg = magic(p.e_dmg, p.e_dmg_ap, ap);
        let mut slow = BuffV1::timed(&sc("e_slow"), p.e_slow_t);
        slow.move_speed_mult = -(p.e_slow as i32);
        let hit = enemies_near(sim, me, p.e_r);
        for &id in &hit {
            sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            if sim.get_entity(id).is_some_and(|e| e.is_alive()) {
                put(sim, id, &slow);
                if p.e_stun > 0 {
                    sim.apply_cc(id, &CcV1::of_kind(CcKindV1::Stun, p.e_stun as u64));
                }
            }
        }
        sim.entity_remove_buff(me, &sc("e_shell"));
        sim.play_view_effect(&sc("e_burst"), me, &InputTargetV1::target(me), 0, 0, 0);
        sim.play_sfx(&sc("e_break"), me, &InputTargetV1::target(me));
        if let Some(&first) = hit.first() {
            sim.play_sfx(&sc("e_slow"), me, &InputTargetV1::target(first));
        }
        if let Some(k) = counted("burst") {
            wlog(format!("{} BURST #{k} ({why}): {dmg} to {:?}", head(sim, me),
                         hit.iter().map(|&t| name_of(sim, t)).collect::<Vec<_>>()));
        }
    }
}

impl StablePassive for GreenBuff {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Scuttle Crab (player {player}, team {team}), {:?}", head(sim, me),
                         self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            self.shell = false;
            return;
        }
        self.green(sim, me);
        let marked = has(sim, me, &sc("e_shell"));
        if marked && !self.shell {   // the shell just closed: its shield came with the mark
            self.shell = true;
            return;
        }
        if self.shell {
            let shield = sim.get_entity(me).map_or(0, |e| e.shield());
            if bursts(marked, shield) {
                self.shell = false;
                self.burst(sim, me, if marked { "shield spent" } else { "ran out" });
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        // it curls up in its shell (the data has no moment for it); a closed shell dies with it
        self.shell = false;
        sim.play_sfx(&sc("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// The Scuttle Crab's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Scuttle Crab: the Green Buff, the shell bursting) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:greenbuff"), GreenBuff::default());
    host.log(LogLevel::Info, "tft.dll: Scuttle Crab (the Green Buff, the shell bursting).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_low":40,"p_pct":12,"p_r":70000,"p_cd":600,"e_t":120,"e_r":40000,"e_dmg":80,"e_dmg_ap":60,"e_slow":40,"e_slow_t":90,"e_stun":30}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_green_buff() {
        let p = Params::default();
        assert!(due(399, 1000, true, &p));
        assert!(!due(400, 1000, true, &p));     // at the line: not yet
        assert!(!due(100, 1000, false, &p));    // its cooldown
        assert!(!due(0, 1000, true, &p));       // dead
        assert_eq!(green_amount(1500, &p), 180);
        assert_eq!(green_amount(1, &p), 1);
    }

    #[test]
    fn the_shell() {
        assert!(!bursts(true, 120));
        assert!(bursts(true, 0));               // the shield spent
        assert!(bursts(false, 80));             // e_t ran out
        assert_eq!(magic(50, 40, 100), 90);
    }
}
