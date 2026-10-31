//! 呲呲（`tft_zippy`）数据做不到的部分（金铲铲第 7 赛季的冒险家 / 龙神小迅猛龙，技能按用户选的方案 A「冒险家突击」，
//! 2026-10-31）。它的数据（tools/kit/build_zippy.py）的 `passive` 是这里的 `tft_zippy:guild`，参数从数据的
//! `passive.params` 来（build_zippy.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **冒险家之魂**：每 `CHECK` 拍数一次它身边 `p_r` 以内活着的友方英雄（不算它自己，最多 `p_max` 个），每个给它
//!   `p_def` 护甲和魔抗（`tft_zippy_p_guild`，带画面，比下一次数多活几拍）；一个也没有就摘掉。数据数不了身边的人。
//! - **翻滚突袭（跃起）** `tft_zippy:leap`：找 `r_range` 内**生命百分比最高**的敌方英雄（没有就用 AI 选的目标），每拍
//!   往它跳 `r_speed`，最多 `r_t` 拍，落到身前（`tft_zippy:hop` 一拍一拍接着跳）；落地时那个人（还活着、碰得到）挨
//!   `r_dmg` + `r_ad`% 攻击力的物理伤害，晕眩 `r_stun` 拍，被往后撞开 `r_kb` × `r_kb_t`，亮 `tft_zippy_r_hit`、播撞击和
//!   落地的声音。数据读不了谁的血量。
//! - **死亡**：倒下时播 `tft_zippy_d`。
//!
//! 利爪踢、后空翻踢（击飞）、翻滚冲锋（滚过的敌人受伤、友军加速）和翻滚突袭的护盾、免控是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_zippy.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_zippy";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const HOP_FX: &str = "tft_zippy:hop";
/// How often (ticks) the passive counts the allies round it; the armour lasts a few ticks past the next count.
const CHECK: usize = 15;
const LINGER: usize = 5;
/// 落到身前的距离（两个身子碰到）。
const TOUCH: u64 = 22000;

fn zp(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_ZIPPY_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_zippy.log");
        }
    }
    PathBuf::from("tft_zippy.log")
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
    /// 冒险家之魂：p_r 以内每个友方英雄 p_def 护甲和魔抗，最多 p_max 个。
    pub p_r: usize,
    pub p_def: usize,
    pub p_max: usize,
    /// 翻滚突袭：找 r_range 内生命百分比最高的敌方英雄，每拍 r_speed、最多 r_t 拍；落地 r_dmg + r_ad% 攻击力、
    /// 晕眩 r_stun 拍、撞开 r_kb × r_kb_t。
    pub r_range: usize,
    pub r_speed: usize,
    pub r_t: usize,
    pub r_dmg: usize,
    pub r_ad: usize,
    pub r_stun: usize,
    pub r_kb: usize,
    pub r_kb_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_r: 50000,
            p_def: 10,
            p_max: 4,
            r_range: 70000,
            r_speed: 4000,
            r_t: 20,
            r_dmg: 80,
            r_ad: 220,
            r_stun: 90,
            r_kb: 1500,
            r_kb_t: 8,
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
            "p_r" => p.p_r = u,
            "p_def" => p.p_def = u,
            "p_max" => p.p_max = u,
            "r_range" => p.r_range = u,
            "r_speed" => p.r_speed = u.max(1),
            "r_t" => p.r_t = u,
            "r_dmg" => p.r_dmg = u,
            "r_ad" => p.r_ad = u,
            "r_stun" => p.r_stun = u,
            "r_kb" => p.r_kb = u,
            "r_kb_t" => p.r_kb_t = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// 一次跃起：跳向谁、到哪一拍为止、它最后在哪。
#[derive(Clone, Debug, Default)]
struct Leap {
    target: usize,
    until: usize,
    last: (u64, u64),
}

/// 跃起按（种子、模拟来源、比赛、局、它）分开：同一个进程里预演和观看的模拟各算各的（league_loris 的做法）。
type Key = (u64, u32, u64, u64, usize);
static LEAPS: LazyLock<Mutex<HashMap<Key, Leap>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

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

/// The point TOUCH short of `to` on the way from `from` (where it lands in front of it).
pub fn front_of(from: (u64, u64), to: (u64, u64)) -> (u64, u64) {
    let d = (dist_sq(from, to) as f64).sqrt();
    step(from, to, (d - TOUCH as f64).max(0.0) as u64)
}

/// The healthiest (highest hp / max hp) of the (id, where, hp, max hp) within `reach` of `at`; ties go to the nearer.
pub fn healthiest(at: (u64, u64), champs: &[(usize, (u64, u64), usize, usize)], reach: usize) -> Option<usize> {
    let r = (reach as u128) * (reach as u128);
    champs
        .iter()
        .filter(|c| c.3 > 0 && dist_sq(at, c.1) <= r)
        .max_by(|a, b| {
            // a.2 / a.3 against b.2 / b.3 without rounding, then the nearer, then the lower id
            (a.2 as u128 * b.3 as u128)
                .cmp(&(b.2 as u128 * a.3 as u128))
                .then(dist_sq(at, b.1).cmp(&dist_sq(at, a.1)))
                .then(b.0.cmp(&a.0))
        })
        .map(|c| c.0)
}

/// How many allies count: at most p_max.
pub fn allies_counted(n: usize, p: &Params) -> usize {
    n.min(p.p_max)
}

/// The guild's armour and magic resistance for `n` allies, lasting past the next count.
pub fn guild_buff(n: usize, p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(&zp("p_guild"), CHECK + LINGER);
    b.defence = (p.p_def * n) as i32;
    b.magic_resistance = (p.p_def * n) as i32;
    b
}

// ===================== 场上 =====================

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

fn reachable(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive() && e.is_targetable())
}

/// Live allied champions within `reach` of it (not itself).
fn allies_near(sim: &StableSim<'_>, me: usize, reach: usize) -> usize {
    let Some((team, at)) = sim.get_entity(me).map(|e| (e.team(), e.pos())) else { return 0 };
    let r = (reach as u128) * (reach as u128);
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.id() != me && u.team() == team && u.is_alive() && u.is_champion())
        .filter(|u| dist_sq(at, u.pos()) <= r)
        .count()
}

/// Live, targetable enemy champions: (id, where, hp, max hp).
fn enemy_champs(sim: &StableSim<'_>, me: usize) -> Vec<(usize, (u64, u64), usize, usize)> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && u.is_champion())
        .map(|u| {
            let (hp, max) = u.hp();
            (u.id(), u.pos(), hp, max)
        })
        .collect()
}

// ===================== 翻滚突袭 =====================

/// Somersault Assault's leap starts: the enemy champion with the highest percent health in reach, else the AI's target.
struct LeapStart;
impl StableEffectType for LeapStart {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let champs = enemy_champs(sim, me);
        let aimed = (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id);
        let target = healthiest(at, &champs, p.r_range).or(aimed.filter(|&id| reachable(sim, id)));
        let Some(target) = target else {
            if let Some(k) = counted("leap_none") {
                wlog(format!("{} LEAP NONE #{k}: nobody to leap at", head(sim, me)));
            }
            return;
        };
        let to = sim.get_entity(target).map_or(at, |e| e.pos());
        let k_ = key(sim, me);
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).insert(k_, Leap { target, until: sim.tick() + p.r_t, last: to });
        if let Some(k) = counted("leap") {
            let (hp, max) = sim.get_entity(target).map_or((0, 0), |e| e.hp());
            let d = (dist_sq(at, to) as f64).sqrt() as u64;
            wlog(format!("{} LEAP #{k}: at {} ({hp}/{max} hp, {d} away; the AI aimed at {})", head(sim, me),
                         name_of(sim, target), aimed.map_or_else(|| "nobody".to_string(), |id| name_of(sim, id))));
        }
        hop(sim, me, k_);
    }
}

/// One tick of the leap (queued again until it lands or runs out of ticks).
struct Hop;
impl StableEffectType for Hop {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let k_ = key(sim, me);
        hop(sim, me, k_);
    }
}

fn hop(sim: &mut StableSim<'_>, me: usize, k_: Key) {
    let Some(mut l) = LEAPS.lock().unwrap_or_else(|e| e.into_inner()).get(&k_).cloned() else { return };
    let Some(from) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else {
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
        return;
    };
    let p = params_of(me);
    if reachable(sim, l.target) {
        l.last = sim.get_entity(l.target).map_or(l.last, |e| e.pos());
    }
    let goal = front_of(from, l.last);
    let next = step(from, goal, p.r_speed as u64);
    sim.entity_set_pos(me, next.0, next.1);
    let landed = next == goal;
    if !landed && sim.tick() < l.until {
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).insert(k_, l);
        sim.queue_effect(HOP_FX, AttackTypeV1::Skill, me, &InputTargetV1::target(me), 1);
        return;
    }
    LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&k_);
    sim.play_sfx(&zp("r_land"), me, &InputTargetV1::target(me));
    if !landed || !reachable(sim, l.target) {
        if let Some(k) = counted("land_miss") {
            let d = (dist_sq(next, l.last) as f64).sqrt() as u64;
            wlog(format!("{} LAND MISS #{k}: {} ({d} from {})", head(sim, me),
                         if landed { "the target is gone" } else { "out of ticks" }, name_of(sim, l.target)));
        }
        return;
    }
    let atk = sim.get_entity(me).map_or(0, |e| e.stat().attack);
    let dmg = physical(p.r_dmg, p.r_ad, atk);
    let id = l.target;
    sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
    sim.apply_cc(id, &CcV1::stun(p.r_stun as u64));
    sim.entity_knockback(me, id, p.r_kb, p.r_kb_t);
    let on = InputTargetV1::target(id);
    sim.play_view_effect(&zp("r_hit"), me, &on, 0, 0, 0);
    sim.play_sfx(&zp("r_hit"), me, &on);
    if let Some(k) = counted("land") {
        wlog(format!("{} LAND #{k}: {} takes {dmg}, stunned {} ticks, knocked back", head(sim, me), name_of(sim, id),
                     p.r_stun));
    }
}

// ===================== 被动：冒险家之魂 =====================

#[derive(Clone, Default)]
struct Guild {
    p: Params,
    /// How many allies the last count gave armour for (a change is logged).
    last: usize,
}

impl StablePassive for Guild {
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
            wlog(format!("{} SPAWN #{k}: tft.dll's Zippy (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        if sim.tick() % CHECK != 0 || !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        let n = allies_counted(allies_near(sim, me, self.p.p_r), &self.p);
        let b = guild_buff(n, &self.p);
        if n == 0 {
            sim.entity_remove_buff(me, b.name());
        } else {
            put(sim, me, &b);
        }
        if n != self.last {
            if let Some(k) = counted("guild") {
                wlog(format!("{} GUILD #{k}: {n} allies near -> +{} armour and magic resistance", head(sim, me),
                             self.p.p_def * n));
            }
            if n > self.last {
                sim.play_sfx(&zp("p"), me, &InputTargetV1::target(me));
            }
            self.last = n;
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        // its death cry (the data has no moment for it); the count starts again on the next life
        self.last = 0;
        LEAPS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me));
        sim.play_sfx(&zp("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// Zippy's passive and Somersault Assault's leap, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Zippy: Adventurer's Spirit, Somersault Assault at the healthiest enemy) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:guild"), Guild::default());
    module.add_native_effect(format!("{ID}:leap"), LeapStart);
    module.add_native_effect(format!("{ID}:hop"), Hop);
    host.log(LogLevel::Info, "tft.dll: Zippy (Adventurer's Spirit, Somersault Assault).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_def":10,"p_max":4,"p_r":50000,"r_ad":220,"r_dmg":80,"r_kb":1500,"r_kb_t":8,"r_range":70000,"r_speed":4000,"r_stun":90,"r_t":20}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_guild_armour() {
        let p = Params::default();
        assert_eq!((allies_counted(0, &p), allies_counted(3, &p), allies_counted(6, &p)), (0, 3, 4));
        let b = guild_buff(3, &p);
        assert_eq!((b.name(), b.defence, b.magic_resistance, b.duration_tick), ("tft_zippy_p_guild", 30, 30, CHECK + LINGER));
    }

    #[test]
    fn the_leap_goes_to_the_healthiest_in_reach() {
        // (id, where, hp, max hp): 2 is at 100%, 3 at 100% but farther, 4 out of reach at 100%, 1 at 50%
        let champs = [(1, (10000, 0), 500, 1000), (2, (30000, 0), 900, 900), (3, (60000, 0), 1200, 1200),
                      (4, (90000, 0), 800, 800)];
        assert_eq!(healthiest((0, 0), &champs, 70000), Some(2));
        assert_eq!(healthiest((0, 0), &champs[..1], 70000), Some(1));
        assert_eq!(healthiest((0, 0), &champs, 5000), None);
        let hurt = [(1, (10000, 0), 300, 1000), (2, (30000, 0), 700, 1400)];
        assert_eq!(healthiest((0, 0), &hurt, 70000), Some(2));
    }

    #[test]
    fn it_lands_in_front() {
        let goal = front_of((0, 0), (100000, 0));
        assert_eq!(goal, (100000 - TOUCH, 0));
        assert_eq!(step((0, 0), goal, 4000), (4000, 0));
        assert_eq!(step((76000, 0), goal, 4000), goal);
    }

    #[test]
    fn damage_by_the_numbers() {
        let p = Params::default();
        assert_eq!(physical(p.r_dmg, p.r_ad, 100), 300);
    }
}
