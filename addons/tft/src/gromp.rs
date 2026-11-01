//! 魔沼蛙（`tft_gromp`）数据做不到的部分（金铲铲第 18 赛季的峡谷野怪 / 魔战士；技能按用户选的方案 A「打嗝泡泡」，2026-11-01）。
//! 它的数据（tools/kit/build_gromp.py）的 `passive` 是这里的 `tft_gromp:purple`，参数从数据的 `passive.params` 来
//! （build_gromp.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **紫霸符**：附近 `p_near` 内有敌方英雄（在打架）时，每 `p_every` tick 叠一层 `p_ap` 法术加成（`tft_gromp_p_ap`），
//!   最多 `p_max` 层，每层持续 `p_t` tick、叠下一层时刷新（引擎的叠层 buff；数据的被动不会计时，同名 buff 也不封顶）。
//!   叠满那一下播 `tft_gromp_p`。
//! - **死亡**：倒下时播 `tft_gromp_d`（数据没有死亡的时机）。
//!
//! 普攻的毒口水、打嗝泡泡（碰到第一个敌人停下炸开、周围中毒）、黏液沼泽和毒沼大嗝都是数据自己的；大招时身体变大由
//! league.dll 的 hd::FORMS 按旗子 `tft_gromp_r_big` 画。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_gromp.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_gromp";
const VERSION: &str = env!("CARGO_PKG_VERSION");

fn gp(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_GROMP_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_gromp.log");
        }
    }
    PathBuf::from("tft_gromp.log")
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
    pub p_ap: usize,
    pub p_max: usize,
    pub p_t: usize,
    pub p_near: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_every: 240,
            p_ap: 8,
            p_max: 8,
            p_t: 600,
            p_near: 90000,
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
            "p_ap" => p.p_ap = u,
            "p_max" => p.p_max = u.max(1),
            "p_t" => p.p_t = u.max(1),
            "p_near" => p.p_near = u,
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// One stack of Purple Buff: p_ap magic power for p_t ticks (same-name stat buffs count as stacks).
pub fn purple_buff(p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(&gp("p_ap"), p.p_t);
    b.magic_power = p.p_ap as i32;
    b
}

/// Whether a stack is due at `now`: a full p_every since the last one (or since it began fighting).
pub fn stack_due(last: usize, now: usize, every: usize) -> bool {
    now >= last + every
}

pub fn within(a: (u64, u64), b: (u64, u64), r: usize) -> bool {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    dx * dx + dy * dy <= (r as i128) * (r as i128)
}

// ===================== 模拟里的小工具 =====================

fn stacks(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).count())
}

/// An enemy champion alive within `r` of `me`: it is fighting.
fn fighting(sim: &StableSim<'_>, me: usize, r: usize) -> bool {
    let Some((team, at)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.team(), e.pos())) else { return false };
    (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).any(|id| {
        sim.get_entity(id).is_some_and(|e| e.is_alive() && e.team() != team && within(e.pos(), at, r))
    })
}

// ===================== 被动：紫霸符（计时叠法强、死亡音效） =====================

#[derive(Clone, Default)]
struct Purple {
    p: Params,
    me: usize,
    /// the tick of the last stack, or of the moment it started fighting (None: not fighting)
    last: Option<usize>,
}

impl StablePassive for Purple {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.last = None;
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Gromp (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.me = me;
        let p = self.p;
        let now = sim.tick();
        if !fighting(sim, me, p.p_near) {
            self.last = None;   // out of the fight the clock stops; the stacks run out on their own
            return;
        }
        let last = *self.last.get_or_insert(now);
        if !stack_due(last, now, p.p_every) {
            return;
        }
        self.last = Some(now);
        let name = gp("p_ap");
        let before = stacks(sim, me, &name);
        let after = sim.entity_stack_buff(me, &purple_buff(&p), p.p_max, true);
        if before < p.p_max && after >= p.p_max {
            sim.play_sfx(&gp("p"), me, &InputTargetV1::target(me));
        }
        if let Some(k) = counted("purple") {
            wlog(format!("{} PURPLE #{k}: +{} ability power x {after} (max {})", head(sim, me), p.p_ap, p.p_max));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        // its death croak (the data has no moment for it)
        let me = self.me;
        self.last = None;
        sim.play_sfx(&gp("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 注册 =====================

/// Gromp's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Gromp: Purple Buff's timed, capped ability power) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:purple"), Purple::default());
    host.log(LogLevel::Info, "tft.dll: Gromp (Purple Buff).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_ap":8,"p_every":240,"p_max":8,"p_near":90000,"p_t":600}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn a_stack_is_magic_power() {
        let b = purple_buff(&Params::default());
        assert_eq!(b.name(), "tft_gromp_p_ap");
        assert_eq!(b.magic_power, 8);
        assert_eq!(b.duration_tick, 600);
    }

    #[test]
    fn a_stack_every_four_seconds() {
        assert!(!stack_due(100, 339, 240));
        assert!(stack_due(100, 340, 240));
    }

    #[test]
    fn near_is_a_circle() {
        assert!(within((0, 0), (90000, 0), 90000));
        assert!(!within((0, 0), (64000, 64000), 90000));
    }
}
