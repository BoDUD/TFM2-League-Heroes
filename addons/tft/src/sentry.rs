//! 苍蓝哨戒（`tft_sentry`，英文 Pebbles）数据做不到的部分（金铲铲第 18 赛季的峡谷野怪 / 神谕；技能按用户选的方案 A
//! 「蔚蓝激光」，2026-11-02）。它的数据（tools/kit/build_sentry.py）的 `passive` 是这里的 `tft_sentry:blue`，参数从数据的
//! `passive.params` 来（build_sentry.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **青霸符**：蔚蓝激光引导时（它身上有数据的旗子 `tft_sentry_q_ch`），每满 `p_every` tick，大招的剩余冷却少 `p_cut`
//!   tick（2 tick 的 `ult_cooldown_mult`：引擎每 tick 把大招的剩余冷却压到 冷却 x 100 / (100 + 技能 + 大招的 mult)，
//!   技能那份是 0，Q 和 E 不跟着缩），播 `tft_sentry_p`。数据的被动不会计时，也读不到剩余冷却。
//! - **断线**：引导时被照的敌人身上有数据的 `tft_sentry_q_lock`；它离开 `q_break` 以外（或死了、没了），拿掉旗子
//!   `tft_sentry_q_ch`，数据的下一波看见没有旗子就收起激光（停动作、播 `tft_sentry_q_end`）。被控断线是数据自己的。
//! - **死亡**：倒下时播 `tft_sentry_d`（数据没有死亡的时机）。
//!
//! 普攻的碎光弹、激光每一波的伤害和减魔抗、裂石跃迁、棱镜扫射都是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_sentry.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_sentry";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn gp(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_SENTRY_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_sentry.log");
        }
    }
    PathBuf::from("tft_sentry.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub p_every: usize,
    pub p_cut: usize,
    pub r_cd: usize,
    pub q_break: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_every: 60,
            p_cut: 60,
            r_cd: 2100,
            q_break: 85000,
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
            "p_every" => p.p_every = u.max(1),
            "p_cut" => p.p_cut = u,
            "r_cd" => p.r_cd = u.max(1),
            "q_break" => p.q_break = u,
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// The `ult_cooldown_mult` that caps the ult's remaining cooldown at `r_rem - cut`: the engine caps it at
/// cool x 100 / (100 + mult) (rounded up so the cap is reached); None when nothing is left to cut.
pub fn cut_mult(r_rem: usize, r_cool: usize, cut: usize) -> Option<i32> {
    if r_rem <= 3 || r_cool == 0 || cut == 0 {
        return None;
    }
    let want = r_rem.saturating_sub(cut).max(1) as f64;
    let mult = (r_cool as f64 * 100.0 / want - 100.0).ceil();
    let cap = r_cool as f64 * 100.0 / (100.0 + mult);
    (mult >= 1.0 && cap < r_rem as f64).then_some(mult as i32)
}

/// How many full p_every the channel has run at `now` since `start`.
pub fn charges(start: usize, now: usize, every: usize) -> usize {
    now.saturating_sub(start) / every.max(1)
}

pub fn within(a: (u64, u64), b: (u64, u64), r: usize) -> bool {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    dx * dx + dy * dy <= (r as i128) * (r as i128)
}

// ===================== 模拟里的小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// The enemies alive with the laser's lock on them (champions, minions, camps), and whether one is within `r` of
/// `me`.
fn locked_near(sim: &StableSim<'_>, me: usize, r: usize) -> (usize, bool) {
    let Some((team, at)) = sim.get_entity(me).map(|e| (e.team(), e.pos())) else { return (0, false) };
    let lock = gp("q_lock");
    let mut n = 0;
    let mut near = false;
    for e in (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)) {
        if !e.is_alive() || e.team() == team || !has_buff(sim, e.id(), &lock) {
            continue;
        }
        n += 1;
        near |= within(e.pos(), at, r);
    }
    (n, near)
}

/// The ult's remaining cooldown ticks (the player whose champion it is).
fn ult_remaining(sim: &StableSim<'_>, me: usize) -> Option<usize> {
    (0..sim.player_count()).filter_map(|i| sim.player_at(i)).find_map(|pl| {
        let c = pl.champion()?;
        (c.id() == me).then(|| pl.cooldowns().map(|cd| cd.3)).flatten()
    })
}

// ===================== 被动：青霸符（引导减大招冷却、断线、死亡音效） =====================

#[derive(Clone, Default)]
struct Blue {
    p: Params,
    me: usize,
    /// the tick the current channel began and the charges already paid (None: not channelling)
    channel: Option<(usize, usize)>,
}

impl Blue {
    fn charge(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let p = self.p;
        let Some(r_rem) = ult_remaining(sim, me) else { return };
        let Some(mult) = cut_mult(r_rem, p.r_cd, p.p_cut) else { return };
        let name = gp("p_cd");
        sim.entity_remove_buff(me, &name);
        let mut b = BuffV1::timed(&name, 2);
        b.ult_cooldown_mult = mult;
        sim.add_buff(me, &b);
        sim.play_sfx(&gp("p"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("blue") {
            wlog(format!("{} BLUE #{k}: ult {r_rem} -> about {} (mult {mult})", head(sim, me), r_rem.saturating_sub(p.p_cut)));
        }
    }
}

impl StablePassive for Blue {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.channel = None;
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Sentry (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.me = me;
        let now = sim.tick();
        if !has_buff(sim, me, &gp("q_ch")) {
            self.channel = None;
            return;
        }
        let (start, paid) = *self.channel.get_or_insert((now, 0));
        // the lit enemy gone or out of q_break: the data's next wave sees no flag and folds the laser
        let (locked, near) = locked_near(sim, me, self.p.q_break);
        if locked > 0 && !near || locked == 0 && now > start + 2 {
            sim.entity_remove_buff(me, &gp("q_ch"));
            self.channel = None;
            if let Some(k) = counted("break") {
                let why = if locked == 0 { "target gone" } else { "out of range" };
                wlog(format!("{} BREAK #{k}: laser folded after {} ticks ({why})", head(sim, me), now - start));
            }
            return;
        }
        let due = charges(start, now, self.p.p_every);
        if due > paid {
            self.channel = Some((start, due));
            self.charge(sim, me);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        // the shards falling apart (the data has no moment for it)
        let me = self.me;
        self.channel = None;
        sim.play_sfx(&gp("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// The Sentry's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Sentry: Blue Buff's ult refund while lasing, the laser's range break) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:blue"), Blue::default());
    host.log(LogLevel::Info, "tft.dll: Sentry (Blue Buff, laser break).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_cut":60,"p_every":60,"q_break":85000,"r_cd":2100}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn a_charge_cuts_a_second() {
        // 1000 left of 2100: capped at 940 or a hair under
        let m = cut_mult(1000, 2100, 60).unwrap();
        let cap = 2100.0 * 100.0 / (100.0 + m as f64);
        assert!(cap <= 940.0 && cap > 935.0, "cap {cap}");
    }

    #[test]
    fn nothing_to_cut_when_ready() {
        assert_eq!(cut_mult(0, 2100, 60), None);
        assert_eq!(cut_mult(3, 2100, 60), None);
    }

    #[test]
    fn a_short_rest_goes_to_zero_not_below() {
        let m = cut_mult(40, 2100, 60).unwrap();
        assert!(2100.0 * 100.0 / (100.0 + m as f64) <= 1.0);
    }

    #[test]
    fn one_charge_a_second() {
        assert_eq!(charges(100, 159, 60), 0);
        assert_eq!(charges(100, 160, 60), 1);
        assert_eq!(charges(100, 250, 60), 2);
    }

    #[test]
    fn near_is_a_circle() {
        assert!(within((0, 0), (85000, 0), 85000));
        assert!(!within((0, 0), (61000, 61000), 85000));
    }
}
