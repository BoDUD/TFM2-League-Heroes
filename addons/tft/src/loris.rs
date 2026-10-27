//! 洛里斯（`tft_loris`）数据做不到的部分（金铲铲第 16 赛季的皮尔特沃夫 / 神盾使，技能和被动按用户选的方案 A「神盾使·皮城争斗」，
//! 2026-10-27）。他的数据（tools/kit/build_loris.py）的 `passive` 是这里的 `tft_loris:warden`，参数从数据的
//! `passive.params` 来（build_loris.py 从参数表 P 写进去，`NATIVE_KEYS`），按他的单位编号记一份给效果用：
//!
//! - **神盾使**：数据读不到生命。被动每拍看他的生命，每条命第一次掉到 `p_hi`% 以下、第一次掉到 `p_lo`% 以下各给一层
//!   最大生命 `p_pct`% 的护盾，`p_t` 拍；身上挂护盾在时一直在的 `tft_loris_p_shield`，亮一下 `p_burst`。
//! - **盾卫**（`tft_loris:bulwark`：技能2 出手）：`e_r` 以内生命比例最低的友方英雄（不算他自己）；他每拍朝那人走 `e_speed`
//!   （`tft_loris:leap`，自己排下一拍），贴上去后两人各得 `e_sh` + 法强 `e_sh_ap`% 的护盾 `e_t` 拍，那人挂上
//!   `tft_loris_e_guard`（受到的伤害少 `e_share`%），被动在这 `e_t` 拍里每拍把那人掉的血折回原来的伤害、把少掉的那
//!   `e_share`% 从他身上扣（不会扣死）。身边没有队友就只给自己护盾；那人半路死了 / 选不中了，就落在原地只给自己护盾。
//!
//! 皮城争斗（冲锋、击退、晕眩）和钢铁防线（砸地、击飞、嘲讽、减伤）是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_loris.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_loris";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const LEAP_FX: &str = "tft_loris:leap";
/// The landing's sound and the Warden shield's (the tft pack's sound_info; the rest of his sounds the data plays).
const SFX_SHIELD: &str = "tft_loris_e_shield";
const SFX_WARDEN: &str = "tft_loris_p";
/// 贴上去的距离（两人身体碰到）、冲过去最多几拍（追不上就落在原地）。
const TOUCH: u64 = 22000;
const LEAP_MAX: usize = 45;

fn lo(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_LORIS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_loris.log");
        }
    }
    PathBuf::from("tft_loris.log")
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
    /// 神盾使：第一次掉到 p_hi% / p_lo% 以下各一层最大生命 p_pct% 的护盾，p_t 拍。
    pub p_hi: usize,
    pub p_lo: usize,
    pub p_pct: usize,
    pub p_t: usize,
    /// 盾卫：找队友的距离、每拍走多远、护盾 e_sh + e_sh_ap% 法强、几拍、替那人承受的 %。
    pub e_r: u64,
    pub e_speed: u64,
    pub e_sh: usize,
    pub e_sh_ap: usize,
    pub e_t: usize,
    pub e_share: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_hi: 75,
            p_lo: 25,
            p_pct: 12,
            p_t: 240,
            e_r: 70000,
            e_speed: 4500,
            e_sh: 70,
            e_sh_ap: 45,
            e_t: 240,
            e_share: 30,
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
            "p_hi" => p.p_hi = u.min(100),
            "p_lo" => p.p_lo = u.min(100),
            "p_pct" => p.p_pct = u,
            "p_t" => p.p_t = u,
            "e_r" => p.e_r = u as u64,
            "e_speed" => p.e_speed = (u as u64).max(1),
            "e_sh" => p.e_sh = u,
            "e_sh_ap" => p.e_sh_ap = u,
            "e_t" => p.e_t = u,
            "e_share" => p.e_share = u.min(90),
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

/// 盾卫守着的人：他的编号 -> (那人、到哪一拍、那人上一拍的生命)。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Guard {
    pub ally: usize,
    pub until: usize,
    pub last_hp: usize,
}

static GUARDS: LazyLock<Mutex<HashMap<usize, Guard>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

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

/// An allied champion Bulwark may go to: (id, where, hp, max hp).
pub type Friend = (usize, (u64, u64), usize, usize);

/// The ally with the lowest share of health within `reach` of `at` (a tie: the nearer, then the lower id).
pub fn weakest(friends: &[Friend], at: (u64, u64), reach: u64) -> Option<usize> {
    friends
        .iter()
        .filter(|&&(_, p, _, max)| max > 0 && dist_sq(p, at) <= (reach as u128) * (reach as u128))
        .min_by(|a, b| {
            // a.hp / a.max against b.hp / b.max, without division
            let l = a.2 as u128 * b.3 as u128;
            let r = b.2 as u128 * a.3 as u128;
            l.cmp(&r).then(dist_sq(a.1, at).cmp(&dist_sq(b.1, at))).then(a.0.cmp(&b.0))
        })
        .map(|f| f.0)
}

/// One step of `speed` from `from` toward `to` (onto it when closer).
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

/// The Warden thresholds crossed now: (the high one, the low one) for `hp` of `max`, those not given yet this life.
pub fn crossed(hp: usize, max: usize, hi: usize, lo: usize, given: (bool, bool)) -> (bool, bool) {
    let under = |pct: usize| max > 0 && hp * 100 < max * pct;
    (!given.0 && under(hi), !given.1 && under(lo))
}

/// What the ally lost this tick was (100 - share)% of the blow: his part, share% of it. Never his last point.
pub fn his_share(ally_lost: usize, share: usize, his_hp: usize) -> usize {
    if share == 0 || share >= 100 {
        return 0;
    }
    (ally_lost * share / (100 - share)).min(his_hp.saturating_sub(1))
}

// ===================== 模拟里的小工具 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn ap_of(sim: &StableSim<'_>, me: usize) -> usize {
    sim.get_entity(me).map_or(0, |e| e.stat().magic_power)
}

fn reachable(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive() && e.is_targetable())
}

/// His allied champions Bulwark can go to: alive, targetable, not himself.
fn friends(sim: &StableSim<'_>, me: usize) -> Vec<Friend> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.champion_count())
        .map(|i| sim.champion_id_at(i))
        .filter(|&id| id != me)
        .filter_map(|id| sim.get_entity(id))
        .filter(|c| c.team() == team && c.is_alive() && c.is_targetable())
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

// ===================== 盾卫 =====================

/// Bulwark's shields on landing: on him, and on the ally he guards from now on (none: him alone).
fn land(sim: &mut StableSim<'_>, me: usize, ally: Option<usize>) {
    let p = params_of(me);
    let amount = magic(p.e_sh, p.e_sh_ap, ap_of(sim, me));
    sim.entity_add_shield(me, amount, p.e_t);
    let at = ally.unwrap_or(me);
    if let Some(id) = ally {
        sim.entity_add_shield(id, amount, p.e_t);
        let mut guard = BuffV1::timed(&lo("e_guard"), p.e_t);
        guard.damaged_reduce = p.e_share;
        put(sim, id, &guard);
        let last_hp = sim.get_entity(id).map_or(0, |e| e.hp().0);
        GUARDS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, Guard { ally: id, until: sim.tick() + p.e_t, last_hp });
    }
    let on = InputTargetV1::target(at);
    sim.play_view_effect(&lo("e_land"), me, &on, 0, 0, 0);
    sim.play_sfx(SFX_SHIELD, me, &on);
    if let Some(k) = counted("land") {
        wlog(format!("{} LAND #{k}: {amount} shields on {}{}", head(sim, me), name_of(sim, me),
                     ally.map_or_else(|| " alone".to_string(), |id| format!(" and {} (guarded {} ticks)", name_of(sim, id), p.e_t))));
    }
}

/// Bulwark's cast: the weakest ally in reach, then the leap (or his own shield when nobody is there).
struct Bulwark;
impl StableEffectType for Bulwark {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let p = params_of(me);
        match weakest(&friends(sim, me), at, p.e_r) {
            Some(ally) => {
                if let Some(k) = counted("bulwark") {
                    let (hp, max) = sim.get_entity(ally).map_or((0, 0), |e| e.hp());
                    wlog(format!("{} BULWARK #{k}: to {} ({hp}/{max})", head(sim, me), name_of(sim, ally)));
                }
                let input = InputTargetV1 { dir_y: (sim.tick() + LEAP_MAX) as i64, ..InputTargetV1::target(ally) };
                sim.queue_effect(LEAP_FX, AttackTypeV1::Skill, me, &input, 1);
            }
            None => land(sim, me, None),
        }
    }

    fn expected_shield(&self, caster_stat: &StatV1) -> usize {
        let p = Params::default();
        magic(p.e_sh, p.e_sh_ap, caster_stat.magic_power)
    }
}

/// One tick of the leap: a step toward the ally, landing when touching (or in place when the ally is gone / too slow).
struct Leap;
impl StableEffectType for Leap {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() || input.dir_y < 0 {
            return;
        }
        let Some(from) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let ally = input.target_id;
        let until = input.dir_y as usize;
        if !reachable(sim, ally) {
            land(sim, me, None);
            return;
        }
        let to = sim.get_entity(ally).map_or(from, |e| e.pos());
        let p = params_of(me);
        if dist_sq(from, to) <= (TOUCH as u128) * (TOUCH as u128) {
            land(sim, me, Some(ally));
            return;
        }
        // stop TOUCH short of the ally's centre, not on it
        let d = (dist_sq(from, to) as f64).sqrt();
        let goal = step(from, to, (d - TOUCH as f64 * 0.8).max(0.0) as u64);
        let next = step(from, goal, p.e_speed);
        sim.entity_set_pos(me, next.0, next.1);
        if sim.tick() >= until {
            if let Some(k) = counted("leap_short") {
                wlog(format!("{} LEAP SHORT #{k}: {} not reached", head(sim, me), name_of(sim, ally)));
            }
            land(sim, me, None);
            return;
        }
        sim.queue_effect(LEAP_FX, AttackTypeV1::Skill, me, &input, 1);
    }
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Warden {
    p: Params,
    /// The thresholds given this life (high, low), and whether he was alive last tick (a respawn starts them over).
    given: (bool, bool),
    was_alive: bool,
}

impl Warden {
    fn shield(&mut self, sim: &mut StableSim<'_>, me: usize, max: usize, which: &str) {
        let amount = max * self.p.p_pct / 100;
        let ok = sim.entity_add_shield(me, amount, self.p.p_t);
        let mut mark = BuffV1::named(&lo("p_shield"));
        mark.duration_kind = BuffDurationV1::WithShield.code();
        put(sim, me, &mark);
        let on = InputTargetV1::target(me);
        sim.play_view_effect(&lo("p_burst"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_WARDEN, me, &on);
        if let Some(k) = counted("warden") {
            wlog(format!("{} WARDEN #{k}: under {which}, {amount} shield for {} ticks{}", head(sim, me), self.p.p_t,
                         if ok { "" } else { " (entity_add_shield refused)" }));
        }
    }

    /// The guarded ally's loss since last tick, his share of it taken from him.
    fn guard(&self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        let mut guards = GUARDS.lock().unwrap_or_else(|e| e.into_inner());
        let Some(g) = guards.get(&me).copied() else { return };
        let ally_hp = sim.get_entity(g.ally).filter(|e| e.is_alive()).map(|e| e.hp().0);
        let (Some(hp), true) = (ally_hp, tick < g.until) else {
            guards.remove(&me);
            return;
        };
        guards.insert(me, Guard { last_hp: hp, ..g });
        drop(guards);
        let lost = g.last_hp.saturating_sub(hp);
        if lost == 0 {
            return;
        }
        let Some(mine) = sim.get_entity(me).map(|e| e.hp().0) else { return };
        let part = his_share(lost, self.p.e_share, mine);
        if part > 0 {
            sim.entity_set_hp(me, mine - part);
            if let Some(k) = counted("share") {
                wlog(format!("{} SHARE #{k}: {} lost {lost}, he takes {part} ({mine} -> {})", head(sim, me),
                             name_of(sim, g.ally), mine - part));
            }
        }
    }
}

impl StablePassive for Warden {
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
            wlog(format!("{} SPAWN #{k}: tft.dll's Loris (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((alive, (hp, max))) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp())) else { return };
        if alive && !self.was_alive {   // the first tick of a life: the thresholds start over
            PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
            self.given = (false, false);
        }
        self.was_alive = alive;
        if !alive {
            GUARDS.lock().unwrap_or_else(|e| e.into_inner()).remove(&me);
            return;
        }
        let (hi, low) = crossed(hp, max, self.p.p_hi, self.p.p_lo, self.given);
        if hi {
            self.given.0 = true;
            self.shield(sim, me, max, "high");
        }
        if low {
            self.given.1 = true;
            self.shield(sim, me, max, "low");
        }
        self.guard(sim, me);
        // the shield's picture goes with the last shield (WithShield), but a buff left from a broken shield is cleared
        if has(sim, me, &lo("p_shield")) && sim.get_entity(me).is_some_and(|e| e.shield() == 0) {
            sim.entity_remove_buff(me, &lo("p_shield"));
        }
    }
}

// ===================== 注册 =====================

/// Loris's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Loris: the Warden's shields at 75% / 25%, Bulwark's leap to the weakest ally and the guard) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:warden"), Warden::default());
    module.add_native_effect(format!("{ID}:bulwark"), Bulwark);
    module.add_native_effect(format!("{ID}:leap"), Leap);
    host.log(LogLevel::Info, "tft.dll: Loris (Warden's shields, Bulwark's leap and guard).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"e_r":70000,"e_sh":70,"e_sh_ap":45,"e_share":30,"e_speed":4500,"e_t":240,"p_hi":75,"p_lo":25,"p_pct":12,"p_t":240}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_weakest_share_of_health_in_reach() {
        let friends = [(1, (100, 0), 900, 1000), (2, (500, 0), 300, 1500), (3, (200, 0), 100, 500), (4, (90_000, 0), 1, 1000)];
        // 3 is at 20%, 2 at 20% too but farther; 4 out of reach
        assert_eq!(weakest(&friends, (0, 0), 1000), Some(3));
        assert_eq!(weakest(&friends, (0, 0), 150), Some(1));
        assert_eq!(weakest(&friends, (0, 0), 50), None);
    }

    #[test]
    fn a_step_toward_never_past() {
        assert_eq!(step((0, 0), (10_000, 0), 4500), (4500, 0));
        assert_eq!(step((0, 0), (3000, 4000), 4500), (2700, 3600));
        assert_eq!(step((0, 0), (1000, 0), 4500), (1000, 0));
    }

    #[test]
    fn each_threshold_once_a_life() {
        assert_eq!(crossed(800, 1000, 75, 25, (false, false)), (false, false));
        assert_eq!(crossed(740, 1000, 75, 25, (false, false)), (true, false));
        assert_eq!(crossed(740, 1000, 75, 25, (true, false)), (false, false));
        // a big blow past both at once gives both
        assert_eq!(crossed(200, 1000, 75, 25, (false, false)), (true, true));
        assert_eq!(crossed(200, 1000, 75, 25, (true, false)), (false, true));
    }

    #[test]
    fn his_part_of_the_blow() {
        // the ally took 70 of a 100 blow (30% less): he takes the other 30
        assert_eq!(his_share(70, 30, 1000), 30);
        assert_eq!(his_share(70, 30, 10), 9);
        assert_eq!(his_share(70, 0, 1000), 0);
    }
}
