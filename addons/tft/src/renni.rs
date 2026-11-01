//! 伦妮（荏妮，`tft_renni`）数据做不到的部分（金铲铲第 13 赛季的炼金男爵 / 格斗家，技能按用户选的方案 A「泥奔者」，2026-10-29）。
//! 她的数据（tools/kit/build_renni.py）的 `passive` 是这里的 `tft_renni:shimmer`，参数从数据的 `passive.params` 来
//! （build_renni.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **微光狂热**：数据读不到生命。被动每拍看她的生命：低于 `p_line`% 且冷却（`p_cd` 拍）好了，就给自己打一针微光：
//!   `p_t` 拍内攻速 +`p_as`%（`tft_renni_p_rush`），并在这段时间里分几次回复最大生命的 `p_heal`%；亮 `p`、放 `p` 的声音。
//! - **泥奔者重击的回血**：数据在她把目标举起来时给她挂 `r_up` 拍的 `tft_renni_r_hold`；被动看到它就在这 `r_up` 拍里
//!   分几次回复最大生命的 `r_heal`%。
//!
//! 链锯研磨、链锯冲撞、锯刃格挡和举起砸地本身都是数据的。只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_renni.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_renni";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// The sound tft.dll plays itself (the tft pack's sound_info; the rest the data plays).
const SFX_SHOT: &str = "tft_renni_p";
const SFX_HEAL: &str = "tft_renni_p_heal";
/// A heal over time lands in steps this many ticks apart (one number every tick would bury her health bar).
const STEP: u64 = 10;

fn sc(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_RENNI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_renni.log");
        }
    }
    PathBuf::from("tft_renni.log")
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 微光狂热：生命低于 p_line% 时，每 p_cd 拍一次：p_t 拍内攻速 +p_as%，其间回复最大生命的 p_heal%。
    pub p_line: usize,
    pub p_cd: usize,
    pub p_t: usize,
    pub p_as: usize,
    pub p_heal: usize,
    /// 泥奔者重击：举着目标的 r_up 拍里回复最大生命的 r_heal%。
    pub r_heal: usize,
    pub r_up: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_line: 40,
            p_cd: 1800,
            p_t: 240,
            p_as: 40,
            p_heal: 20,
            r_heal: 15,
            r_up: 66,
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
            "p_line" => p.p_line = u.min(100),
            "p_cd" => p.p_cd = u,
            "p_t" => p.p_t = u.max(1),
            "p_as" => p.p_as = u,
            "p_heal" => p.p_heal = u,
            "r_heal" => p.r_heal = u,
            "r_up" => p.r_up = u.max(1),
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// Whether the shimmer shot fires: under p_line% health and its cooldown over (`ready` = the first tick it may).
pub fn shot_ready(p: &Params, hp: usize, max: usize, now: u64, ready: u64) -> bool {
    max > 0 && hp * 100 < max * p.p_line && now >= ready
}

/// A heal over time: `left` still to heal, `ticks` still to go.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Regen {
    pub left: usize,
    pub ticks: u64,
}

impl Regen {
    pub fn new(max: usize, pct: usize, ticks: usize) -> Self {
        Self { left: max * pct / 100, ticks: ticks.max(1) as u64 }
    }

    /// One tick on: what heals now (every STEP ticks a share of what is left, the rest on the last tick).
    pub fn tick(&mut self) -> usize {
        if self.ticks == 0 {
            return 0;
        }
        self.ticks -= 1;
        if self.ticks % STEP != 0 {
            return 0;
        }
        let steps = self.ticks / STEP + 1;
        let now = self.left / steps as usize;
        self.left -= now;
        now
    }

    pub fn done(&self) -> bool {
        self.ticks == 0
    }
}

// ===================== 模拟里的小工具 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    let Some(e) = sim.get_entity(id) else { return false };
    (0..).map_while(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// A named buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

// ===================== 被动：微光狂热 + 举起时的回血 =====================

#[derive(Clone, Default)]
struct Shimmer {
    p: Params,
    /// The first tick the shot may fire again, and whether she was alive last tick.
    ready: u64,
    was_alive: bool,
    /// The heals running now (the shot's, the lift's).
    regens: Vec<Regen>,
}

impl StablePassive for Shimmer {
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
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Renni (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((alive, (hp, max))) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp())) else { return };
        if alive && !self.was_alive {   // a new life: no heal carried over (the shot's cooldown is kept)
            self.regens.clear();
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        let now = sim.tick() as u64;
        // the shimmer shot under p_line% health
        if shot_ready(&self.p, hp, max, now, self.ready) {
            self.ready = now + self.p.p_cd as u64;
            let mut b = BuffV1::timed(&sc("p_rush"), self.p.p_t);
            b.attack_speed_mult = self.p.p_as as i32;
            put(sim, me, &b);
            self.regens.push(Regen::new(max, self.p.p_heal, self.p.p_t));
            let on = InputTargetV1::target(me);
            sim.play_view_effect(&sc("p"), me, &on, 0, 0, 0);
            sim.play_sfx(SFX_SHOT, me, &on);
            if let Some(k) = counted("shot") {
                wlog(format!("{} SHOT #{k}: {hp}/{max}: +{}% attack speed, heals {} over {} ticks", head(sim, me),
                             self.p.p_as, max * self.p.p_heal / 100, self.p.p_t));
            }
        }
        // the lift: heal while she holds the target up
        if has(sim, me, &sc("r_hold")) {
            sim.entity_remove_buff(me, &sc("r_hold"));
            self.regens.push(Regen::new(max, self.p.r_heal, self.p.r_up));
            sim.play_sfx(SFX_HEAL, me, &InputTargetV1::target(me));
            if let Some(k) = counted("lift") {
                wlog(format!("{} LIFT #{k}: {hp}/{max}: heals {} over {} ticks", head(sim, me),
                             max * self.p.r_heal / 100, self.p.r_up));
            }
        }
        let mut amount = 0;
        for r in &mut self.regens {
            amount += r.tick();
        }
        self.regens.retain(|r| !r.done());
        if amount > 0 {
            sim.heal(me, me, amount);
        }
    }
}

// ===================== 注册 =====================

/// Renni's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Renni: the shimmer shot, the lift's heal) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:shimmer"), Shimmer::default());
    host.log(LogLevel::Info, "tft.dll: Renni (Shimmer Frenzy, Mudrunner Slam's heal).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_as":40,"p_cd":1800,"p_heal":20,"p_line":40,"p_t":240,"r_heal":15,"r_up":66}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_shot_under_the_line_off_cooldown() {
        let p = Params::default();
        assert!(shot_ready(&p, 399, 1000, 10, 0));
        assert!(!shot_ready(&p, 400, 1000, 10, 0));
        assert!(!shot_ready(&p, 100, 1000, 10, 11));
        assert!(!shot_ready(&p, 0, 0, 10, 0));
    }

    #[test]
    fn a_regen_heals_it_all_in_steps() {
        let mut r = Regen::new(1150, 20, 240);
        let mut total = 0;
        let mut steps = 0;
        while !r.done() {
            let h = r.tick();
            if h > 0 {
                steps += 1;
            }
            total += h;
        }
        assert_eq!(total, 230);
        assert_eq!(steps, 24);
        let mut short = Regen::new(1000, 15, 66);
        let total: usize = (0..66).map(|_| short.tick()).sum();
        assert_eq!(total, 150);
        assert!(short.done());
    }
}
