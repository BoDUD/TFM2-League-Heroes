//! 艾达丝（`tft_idas`）数据做不到的部分（金铲铲第 7 赛季的金鳞龙 / 龙神 / 护卫，技能按用户选的方案 A「黄金守护」，
//! 2026-10-30）。她的数据（tools/kit/build_idas.py）的 `passive` 是这里的 `tft_idas:guardian`，参数从数据的
//! `passive.params` 来（build_idas.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **护卫之誓**：金铲铲的护卫每场战斗一次，生命掉到一半时给自己和最近的一名友军护盾。数据读不到生命，也找不到最近的
//!   队友，所以由本被动每拍看她的生命：掉到最大生命的 `p_low`% 以下、且冷却 `p_cd` 拍已过（每条命一开始就是好的）时，
//!   她和 `p_r` 以内离她最近的友方英雄各得最大生命 `p_pct`% 的护盾，`p_t` 拍；两人身上挂护盾在时一直在的
//!   `tft_idas_p_shield`，各亮一下 `tft_idas_p_burst`，播 `tft_idas_p`。身边没有队友就只给自己。
//!
//! 黄金龙息（扇形吐息、降护甲）、龙威振翅（减速、小护盾）和黄金龙鳞（裹翼减伤、回血、队友护盾和攻速）是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_idas.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_idas";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// The vow's sound (the tft pack's sound_info; the rest of her sounds the data plays).
const SFX_VOW: &str = "tft_idas_p";

fn ia(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_IDAS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_idas.log");
        }
    }
    PathBuf::from("tft_idas.log")
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
    /// 护卫之誓：生命低于 p_low% 时，她和 p_r 以内最近的友军各得她最大生命 p_pct% 的护盾 p_t 拍；之后 p_cd 拍内不再有。
    pub p_low: usize,
    pub p_pct: usize,
    pub p_t: usize,
    pub p_r: u64,
    pub p_cd: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_low: 50,
            p_pct: 18,
            p_t: 300,
            p_r: 60000,
            p_cd: 1800,
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
            "p_t" => p.p_t = u,
            "p_r" => p.p_r = u as u64,
            "p_cd" => p.p_cd = u,
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

/// The vow is due: alive, under p_low% of her maximum health, and `ready` (the cooldown over).
pub fn due(hp: usize, max: usize, ready: bool, p: &Params) -> bool {
    ready && hp > 0 && max > 0 && hp * 100 < max * p.p_low
}

/// One shield of the vow: p_pct% of her maximum health, at least 1.
pub fn vow_amount(max: usize, p: &Params) -> usize {
    (max * p.p_pct / 100).max(1)
}

/// The allied champion nearest `at` within `reach` (a tie: the lower id), from (id, where).
pub fn nearest(friends: &[(usize, (u64, u64))], at: (u64, u64), reach: u64) -> Option<usize> {
    let r = (reach as u128) * (reach as u128);
    friends
        .iter()
        .map(|&(id, pos)| (dist_sq(pos, at), id))
        .filter(|&(d, _)| d <= r)
        .min()
        .map(|t| t.1)
}

// ===================== 模拟里的小工具 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// Her allied champions: alive, targetable, not herself.
fn friends(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64))> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.champion_count())
        .map(|i| sim.champion_id_at(i))
        .filter(|&id| id != me)
        .filter_map(|id| sim.get_entity(id))
        .filter(|c| c.team() == team && c.is_alive() && c.is_targetable())
        .map(|c| (c.id(), c.pos()))
        .collect()
}

/// A named buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Guardian {
    p: Params,
    /// The tick the vow is ready again (0: ready), and whether she was alive last tick (a respawn makes it ready).
    ready_at: usize,
    was_alive: bool,
    /// Who got the last vow's shield besides her (its picture is cleared when that shield is spent).
    ally: Option<usize>,
}

impl Guardian {
    fn vow(&mut self, sim: &mut StableSim<'_>, me: usize, max: usize) {
        let amount = vow_amount(max, &self.p);
        let at = sim.get_entity(me).map_or((0, 0), |e| e.pos());
        let ally = nearest(&friends(sim, me), at, self.p.p_r);
        let mut mark = BuffV1::named(&ia("p_shield"));
        mark.duration_kind = BuffDurationV1::WithShield.code();
        let mut ok = true;
        for id in std::iter::once(me).chain(ally) {
            ok &= sim.entity_add_shield(id, amount, self.p.p_t);
            put(sim, id, &mark);
            sim.play_view_effect(&ia("p_burst"), me, &InputTargetV1::target(id), 0, 0, 0);
        }
        sim.play_sfx(SFX_VOW, me, &InputTargetV1::target(me));
        self.ally = ally;
        self.ready_at = sim.tick() + self.p.p_cd;
        if let Some(k) = counted("vow") {
            wlog(format!("{} VOW #{k}: {amount} shield for {} ticks on her{}{}", head(sim, me), self.p.p_t,
                         ally.map_or_else(|| " alone".to_string(), |id| format!(" and {}", name_of(sim, id))),
                         if ok { "" } else { " (entity_add_shield refused)" }));
        }
    }

    /// A vow picture left on someone whose shields are all spent is taken off (WithShield stays while any shield holds).
    fn clear(&mut self, sim: &mut StableSim<'_>, id: usize) {
        if has(sim, id, &ia("p_shield")) && sim.get_entity(id).is_some_and(|e| e.shield() == 0) {
            sim.entity_remove_buff(id, &ia("p_shield"));
        }
    }
}

impl StablePassive for Guardian {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Idas (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((alive, (hp, max))) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp())) else { return };
        if alive && !self.was_alive {   // the first tick of a life: the vow is ready
            self.ready_at = 0;
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        if due(hp, max, sim.tick() >= self.ready_at, &self.p) {
            self.vow(sim, me, max);
        }
        self.clear(sim, me);
        if let Some(id) = self.ally {
            self.clear(sim, id);
            if !has(sim, id, &ia("p_shield")) {
                self.ally = None;
            }
        }
    }
}

// ===================== 注册 =====================

/// Idas's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Idas: the Guardian's vow, shields on her and the nearest ally at low health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:guardian"), Guardian::default());
    host.log(LogLevel::Info, "tft.dll: Idas (the Guardian's vow).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_cd":1800,"p_low":50,"p_pct":18,"p_r":60000,"p_t":300}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_vow_under_half_when_ready() {
        let p = Params::default();
        assert!(!due(500, 1000, true, &p));
        assert!(due(499, 1000, true, &p));
        assert!(!due(499, 1000, false, &p));
        assert!(!due(0, 1000, true, &p));
        assert!(!due(10, 0, true, &p));
    }

    #[test]
    fn a_share_of_her_health() {
        let p = Params::default();
        assert_eq!(vow_amount(2000, &p), 360);
        assert_eq!(vow_amount(1, &p), 1);
    }

    #[test]
    fn the_nearest_ally_in_reach() {
        let friends = [(1, (30_000, 0)), (2, (0, 20_000)), (3, (5_000, 0)), (4, (100_000, 0))];
        assert_eq!(nearest(&friends, (0, 0), 60_000), Some(3));
        assert_eq!(nearest(&friends, (90_000, 0), 15_000), Some(4));
        assert_eq!(nearest(&friends, (0, 0), 4_000), None);
        // a tie goes to the lower id
        assert_eq!(nearest(&[(7, (10, 0)), (5, (0, 10))], (0, 0), 100), Some(5));
    }
}
