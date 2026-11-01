//! 斯特卜（`tft_steb`）数据做不到的部分（金铲铲第 13 赛季的执法官 / 格斗家，技能和被动按用户选的方案 A「战地军医」，
//! 2026-10-29）。他的数据（tools/kit/build_steb.py）的 `passive` 是这里的 `tft_steb:medic`，参数从数据的
//! `passive.params` 来（build_steb.py 从参数表 P 写进去，`NATIVE_KEYS`），按他的单位编号记一份给效果用：
//!
//! - **战地医疗**：数据读不到生命。被动每拍看他的生命，比上一拍多出来的就是他受到的治疗（他自己的、队友给的、吸血都算）；
//!   离他最近的 `p_n` 名友方英雄（`p_r` 以内，不算他自己，满血的不算）各回复这次治疗量的 `p_share`%（引擎的 heal，
//!   算治疗统计）。队友身上亮一下 `p_heal`（同一个人 `FX_GAP` 拍内只亮一次）。
//! - **通缉令**（`tft_steb:wanted`：技能2 出手）：`e_r` 以内当前生命最多的敌方英雄挂上 `tft_steb_e_wanted`（受到的伤害多
//!   `e_amp`%，`e_t` 拍）；被动每拍看它，挂着通缉时倒下，他和 `e_kr` 以内的友方英雄都得 `tft_steb_e_rush`（攻速 +`e_as`%，
//!   `e_as_t` 拍），他身上亮 `e_kill`。
//!
//! 战地医疗的回血和重击、医疗背包（护盾、减伤、持续治疗）是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_steb.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_steb";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// The shared heal's sound and the Wanted kill's (the tft pack's sound_info; the rest of his sounds the data plays).
const SFX_SHARE: &str = "tft_steb_p";
const SFX_KILL: &str = "tft_steb_e_kill";
const SFX_MARK: &str = "tft_steb_e_hit";
/// One ally's shared-heal flash and sound at most once in this many ticks; a share under FX_MIN shows nothing.
const FX_GAP: usize = 30;
const FX_MIN: usize = 8;

fn sb(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_STEB_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_steb.log");
        }
    }
    PathBuf::from("tft_steb.log")
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
    /// 战地医疗：最近的 p_n 名友方英雄（p_r 以内）各回复 p_share%。
    pub p_n: usize,
    pub p_share: usize,
    pub p_r: u64,
    /// 通缉令：找人的距离、增伤 %、几拍；倒下时 e_kr 以内的友方攻速 +e_as%，e_as_t 拍。
    pub e_r: u64,
    pub e_amp: usize,
    pub e_t: usize,
    pub e_kr: u64,
    pub e_as: usize,
    pub e_as_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_n: 2,
            p_share: 25,
            p_r: 60000,
            e_r: 80000,
            e_amp: 25,
            e_t: 300,
            e_kr: 70000,
            e_as: 30,
            e_as_t: 300,
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
            "p_n" => p.p_n = u.min(4),
            "p_share" => p.p_share = u.min(100),
            "p_r" => p.p_r = u as u64,
            "e_r" => p.e_r = u as u64,
            "e_amp" => p.e_amp = u,
            "e_t" => p.e_t = u,
            "e_kr" => p.e_kr = u as u64,
            "e_as" => p.e_as = u,
            "e_as_t" => p.e_as_t = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// 通缉中的人：(这场模拟的种子、来历、比赛、第几局, 他) -> (那人、通缉到哪一拍)。按模拟分开记（洛里斯的 LEAPS 一样：
/// 预演和观看同时在跑，只按他的编号记会串）。
type Key = (u64, u32, u64, u64, usize);
static WANTED: LazyLock<Mutex<HashMap<Key, (usize, usize)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn key(sim: &StableSim<'_>, me: usize) -> Key {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index, me)
}

// ===================== 规则（单元测试用） =====================

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// A champion on the field: (id, where, hp, max hp).
pub type Unit = (usize, (u64, u64), usize, usize);

/// The `n` allies nearest `at` within `reach` that are not at full health (a tie: the lower id).
pub fn nearest(friends: &[Unit], at: (u64, u64), reach: u64, n: usize) -> Vec<usize> {
    let mut near: Vec<&Unit> = friends
        .iter()
        .filter(|&&(_, p, hp, max)| hp < max && dist_sq(p, at) <= (reach as u128) * (reach as u128))
        .collect();
    near.sort_by(|a, b| dist_sq(a.1, at).cmp(&dist_sq(b.1, at)).then(a.0.cmp(&b.0)));
    near.into_iter().take(n).map(|u| u.0).collect()
}

/// The enemy with the most health within `reach` of `at` (a tie: the nearer, then the lower id).
pub fn most_health(enemies: &[Unit], at: (u64, u64), reach: u64) -> Option<usize> {
    enemies
        .iter()
        .filter(|&&(_, p, _, _)| dist_sq(p, at) <= (reach as u128) * (reach as u128))
        .min_by(|a, b| b.2.cmp(&a.2).then(dist_sq(a.1, at).cmp(&dist_sq(b.1, at))).then(a.0.cmp(&b.0)))
        .map(|u| u.0)
}

/// His share of a heal of `gained`.
pub fn share_of(gained: usize, pct: usize) -> usize {
    gained * pct / 100
}

// ===================== 模拟里的小工具 =====================

/// The alive, targetable champions on his side (`ours`) or the other (not himself either way).
fn units(sim: &StableSim<'_>, me: usize, ours: bool) -> Vec<Unit> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.champion_count())
        .map(|i| sim.champion_id_at(i))
        .filter(|&id| id != me)
        .filter_map(|id| sim.get_entity(id))
        .filter(|c| (c.team() == team) == ours && c.is_alive() && c.is_targetable())
        .map(|c| {
            let (hp, max) = c.hp();
            (c.id(), c.pos(), hp, max)
        })
        .collect()
}

/// A named timed buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

// ===================== 通缉令 =====================

/// Wanted's cast: the enemy champion with the most health in reach takes more damage; the passive watches it.
struct Wanted;
impl StableEffectType for Wanted {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let Some(target) = most_health(&units(sim, me, false), at, p.e_r) else {
            if let Some(k) = counted("wanted_none") {
                wlog(format!("{} WANTED NONE #{k}: no enemy champion within {}", head(sim, me), p.e_r));
            }
            return;
        };
        let mut mark = BuffV1::timed(&sb("e_wanted"), p.e_t);
        mark.damaged_amplify = p.e_amp;
        put(sim, target, &mark);
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&sb("e_mark"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_MARK, me, &on);
        WANTED.lock().unwrap_or_else(|e| e.into_inner()).insert(key(sim, me), (target, sim.tick() + p.e_t));
        if let Some(k) = counted("wanted") {
            let (hp, max) = sim.get_entity(target).map_or((0, 0), |e| e.hp());
            wlog(format!("{} WANTED #{k}: {} ({hp}/{max}) takes {}% more for {} ticks", head(sim, me),
                         name_of(sim, target), p.e_amp, p.e_t));
        }
    }

    fn expected_buff(&self, _: &StatV1) -> Option<BuffV1> {
        let p = Params::default();
        let mut mark = BuffV1::timed(&sb("e_wanted"), p.e_t);
        mark.damaged_amplify = p.e_amp;
        Some(mark)
    }
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Medic {
    p: Params,
    /// His health last tick, and whether he was alive (a respawn's full health is no heal).
    last_hp: usize,
    was_alive: bool,
    /// The last tick each ally showed a shared heal.
    shown: HashMap<usize, usize>,
}

impl Medic {
    /// The heal he just got, its share to the nearest allies.
    fn share(&mut self, sim: &mut StableSim<'_>, me: usize, gained: usize) {
        let amount = share_of(gained, self.p.p_share);
        if amount == 0 {
            return;
        }
        let Some(at) = sim.get_entity(me).map(|e| e.pos()) else { return };
        let to = nearest(&units(sim, me, true), at, self.p.p_r, self.p.p_n);
        let tick = sim.tick();
        for &ally in &to {
            sim.heal(me, ally, amount);
            let due = self.shown.get(&ally).is_none_or(|&t| tick >= t + FX_GAP);
            if amount >= FX_MIN && due {
                self.shown.insert(ally, tick);
                let on = InputTargetV1::target(ally);
                sim.play_view_effect(&sb("p_heal"), me, &on, 0, 0, 0);
                sim.play_sfx(SFX_SHARE, me, &on);
            }
        }
        if !to.is_empty() {
            if let Some(k) = counted("share") {
                let who: Vec<String> = to.iter().map(|&id| name_of(sim, id)).collect();
                wlog(format!("{} SHARE #{k}: healed {gained}, {amount} each to {}", head(sim, me), who.join(", ")));
            }
        }
    }

    /// The Wanted one down while marked: attack speed for him and the allies near him.
    fn watch(&self, sim: &mut StableSim<'_>, me: usize) {
        let k = key(sim, me);
        let Some((target, until)) = WANTED.lock().unwrap_or_else(|e| e.into_inner()).get(&k).copied() else { return };
        let tick = sim.tick();
        if tick >= until {
            WANTED.lock().unwrap_or_else(|e| e.into_inner()).remove(&k);
            return;
        }
        if sim.get_entity(target).is_some_and(|e| e.is_alive()) {
            return;
        }
        WANTED.lock().unwrap_or_else(|e| e.into_inner()).remove(&k);
        let Some(at) = sim.get_entity(me).map(|e| e.pos()) else { return };
        let r = (self.p.e_kr as u128) * (self.p.e_kr as u128);
        let mut team: Vec<usize> = units(sim, me, true).into_iter().filter(|u| dist_sq(u.1, at) <= r).map(|u| u.0).collect();
        team.push(me);
        let mut rush = BuffV1::timed(&sb("e_rush"), self.p.e_as_t);
        rush.attack_speed_mult = self.p.e_as as i32;
        for &id in &team {
            put(sim, id, &rush);
        }
        let on = InputTargetV1::target(me);
        sim.play_view_effect(&sb("e_kill"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_KILL, me, &on);
        if let Some(n) = counted("bounty") {
            wlog(format!("{} BOUNTY #{n}: {} down while Wanted, +{}% attack speed to {} champions", head(sim, me),
                         name_of(sim, target), self.p.e_as, team.len()));
        }
    }
}

impl StablePassive for Medic {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // a new life is a new unit, and on_update does not run while it is dead: the first tick of this life
        // must see a dead one, or what each life has once stays used up (2026-11-02 logs)
        self.was_alive = false;
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Steb (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((alive, hp)) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp().0)) else { return };
        let gained = if alive && self.was_alive { hp.saturating_sub(self.last_hp) } else { 0 };
        if alive && !self.was_alive {
            PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        }
        self.was_alive = alive;
        self.last_hp = hp;
        if !alive {
            return;
        }
        if gained > 0 {
            self.share(sim, me, gained);
        }
        self.watch(sim, me);
    }
}

// ===================== 注册 =====================

/// Steb's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Steb: Field Medicine's shared heals, Wanted on the healthiest enemy and its bounty) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:medic"), Medic::default());
    module.add_native_effect(format!("{ID}:wanted"), Wanted);
    host.log(LogLevel::Info, "tft.dll: Steb (Field Medicine's shared heals, Wanted).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"e_amp":25,"e_as":30,"e_as_t":300,"e_kr":70000,"e_r":80000,"e_t":300,"p_n":2,"p_r":60000,"p_share":25}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_nearest_hurt_allies() {
        let f = [(1, (100, 0), 900, 1000), (2, (50, 0), 1000, 1000), (3, (300, 0), 10, 500), (4, (90_000, 0), 1, 1000),
                 (5, (200, 0), 5, 100)];
        // 2 is at full health, 4 out of reach
        assert_eq!(nearest(&f, (0, 0), 1000, 2), vec![1, 5]);
        assert_eq!(nearest(&f, (0, 0), 1000, 4), vec![1, 5, 3]);
        assert_eq!(nearest(&f, (0, 0), 10, 2), Vec::<usize>::new());
    }

    #[test]
    fn the_healthiest_enemy_in_reach() {
        let e = [(7, (100, 0), 900, 1000), (8, (500, 0), 1400, 1500), (9, (200, 0), 1400, 2000), (10, (90_000, 0), 5000, 5000)];
        // 8 and 9 tie on health: 9 is nearer; 10 out of reach
        assert_eq!(most_health(&e, (0, 0), 1000), Some(9));
        assert_eq!(most_health(&e, (0, 0), 150), Some(7));
        assert_eq!(most_health(&e, (0, 0), 50), None);
    }

    #[test]
    fn a_quarter_of_the_heal() {
        assert_eq!(share_of(200, 25), 50);
        assert_eq!(share_of(3, 25), 0);
    }
}
