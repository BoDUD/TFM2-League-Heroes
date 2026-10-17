//! 嘉文四世扩展包（用户选：「全按推荐做：打野、布局A、做扩展包」）：主包数据做不到的一件事——天崩地裂的**真岩墙**。
//!
//! `mod.override_info` 把主包的嘉文四世换成 `override/` 里的副本（tools/kit/build_jarvaniv.py 的 native=1）：数据和主包一样，
//! 只是被动挂本包的 `league_jarvaniv:cataclysm`，大招落地后没有主包那套「探测 + 拉回」的近似（本包让墙真的挡路）。
//!
//! - **岩墙环**：数据在他落地那一 tick 给他挂 `league_jarvaniv_r_on`；本包看到它新出现，就以他那一 tick 的位置为圆心、`r_r` 为半径
//!   立一圈墙 `r_t` tick。立墙时在圈里的单位（英雄、小兵、野怪、召唤物，两边都算，他自己也算）出不去，在圈外的进不来：
//!   每 tick 单位的中心一碰到墙（圈里的离圆心超过 `r_r` - 单位半径，圈外的不到 `r_r` + 单位半径），就放回上一 tick 的位置
//!   （上一 tick 也不在该在的一侧时，沿圆心方向推回墙内侧 / 外侧）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_jarvaniv.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_jarvaniv";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";

/// 单位半径读不到时用的值。
pub const BODY: u64 = 6000;

fn sn(x: &str) -> String {
    format!("league_jarvaniv_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_JARVANIV_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_jarvaniv.log");
        }
    }
    PathBuf::from("league_jarvaniv.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub fn wlog(msg: impl AsRef<str>) {
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
const LOG_EVERY: usize = 50;
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
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{kind} m={} s={}] t={} #{id}", m(o.match_id), m(o.set_index), sim.tick())
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub r_r: u64,
    pub r_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { r_r: 36000, r_t: 210 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        match k {
            "r_r" => p.r_r = v,
            "r_t" => p.r_t = v as usize,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 一圈墙：圆心、立起的 tick。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Ring {
    pub x: u64,
    pub y: u64,
    pub from: usize,
}

fn dist(r: &Ring, x: u64, y: u64) -> f64 {
    let dx = x as f64 - r.x as f64;
    let dy = y as f64 - r.y as f64;
    (dx * dx + dy * dy).sqrt()
}

/// 立墙那一 tick 单位在圈里吗。
pub fn starts_inside(r: &Ring, p: &Params, x: u64, y: u64) -> bool {
    dist(r, x, y) < p.r_r as f64
}

/// 这个位置对这个单位合法吗（圈里的不碰外墙，圈外的不碰内墙）。
pub fn allowed(r: &Ring, p: &Params, inside: bool, x: u64, y: u64, body: u64) -> bool {
    let d = dist(r, x, y);
    if inside { d <= (p.r_r.saturating_sub(body)) as f64 } else { d >= (p.r_r + body) as f64 }
}

/// 沿圆心方向放到墙内侧 / 外侧。
pub fn clamp(r: &Ring, p: &Params, inside: bool, x: u64, y: u64, body: u64) -> (u64, u64) {
    let d = dist(r, x, y).max(1.0);
    let target = if inside { p.r_r.saturating_sub(body + 1) as f64 } else { (p.r_r + body + 1) as f64 };
    let (dx, dy) = if dist(r, x, y) < 1.0 { (1.0, 0.0) } else { ((x as f64 - r.x as f64) / d, (y as f64 - r.y as f64) / d) };
    let nx = (r.x as f64 + dx * target).round().max(0.0) as u64;
    let ny = (r.y as f64 + dy * target).round().max(0.0) as u64;
    (nx, ny)
}

/// 这一 tick 单位该在哪（None：不用动）：碰墙就回到上一 tick 的位置，上一 tick 也不合法就推回去。
pub fn hold(r: &Ring, p: &Params, inside: bool, last: Option<(u64, u64)>, now: (u64, u64), body: u64) -> Option<(u64, u64)> {
    if allowed(r, p, inside, now.0, now.1, body) {
        return None;
    }
    match last {
        Some(l) if allowed(r, p, inside, l.0, l.1, body) => Some(l),
        _ => Some(clamp(r, p, inside, now.0, now.1, body)),
    }
}

// ===================== 被动 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

#[derive(Clone, Default)]
struct Cataclysm {
    p: Params,
    me: usize,
    had_r_on: bool,
    ring: Option<Ring>,
    /// 立墙时每个单位在圈里还是圈外。
    side: HashMap<usize, bool>,
    /// 每个单位上一 tick 的位置。
    last_pos: HashMap<usize, (u64, u64)>,
}

impl Cataclysm {
    fn watch(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let on = has(sim, me, &sn("r_on"));
        if on && !self.had_r_on {
            let (x, y) = sim.get_entity(me).map_or((0, 0), |e| e.pos());
            self.ring = Some(Ring { x, y, from: now });
            self.side.clear();
            self.last_pos.clear();
            if let Some(k) = counted("ring") {
                wlog(format!("{} RING #{k}: rock ring at ({x}, {y}), radius {}, {} ticks", head(sim, me), self.p.r_r,
                             self.p.r_t));
            }
        }
        self.had_r_on = on;
    }

    fn block(&mut self, sim: &mut StableSim<'_>, now: usize) {
        let Some(ring) = self.ring else { return };
        if now >= ring.from + self.p.r_t {
            self.ring = None;
            self.side.clear();
            self.last_pos.clear();
            return;
        }
        let mut moves = Vec::new();
        let mut seen = HashMap::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() {
                continue;
            }
            match e.kind() {
                Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Summon) => {}
                _ => continue,
            }
            let id = e.id();
            let pos = e.pos();
            let body = match e.radius() as u64 { 0 => BODY, r => r };
            let inside = *self.side.entry(id).or_insert_with(|| starts_inside(&ring, &self.p, pos.0, pos.1));
            let last = self.last_pos.get(&id).copied();
            let at = match hold(&ring, &self.p, inside, last, pos, body) {
                Some(q) => {
                    moves.push((id, q, inside));
                    q
                }
                None => pos,
            };
            seen.insert(id, at);
        }
        for (id, (x, y), inside) in moves {
            sim.entity_set_pos(id, x, y);
            if let Some(k) = counted(if inside { "kept_in" } else { "kept_out" }) {
                wlog(format!("{} {} #{k}: {} held at ({x}, {y})", head(sim, self.me),
                             if inside { "KEPT IN" } else { "KEPT OUT" }, who(sim, id)));
            }
        }
        self.last_pos = seen;
    }
}

impl StablePassive for Cataclysm {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.had_r_on = false;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Jarvan IV (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        if sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            self.watch(sim, me, now);
        } else {
            self.had_r_on = false;
        }
        self.block(sim, now);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Jarvan IV: Cataclysm's real rock ring) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:cataclysm"), Cataclysm::default());
    host.log(LogLevel::Info, "league_jarvaniv loaded (Cataclysm's real rock ring).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    fn p() -> Params {
        Params::default()
    }

    const RING: Ring = Ring { x: 500000, y: 400000, from: 0 };

    #[test]
    fn params_from_the_kit() {
        assert_eq!(parse_params(r#"{"r_r":36000,"r_t":210}"#), Params::default());
    }

    #[test]
    fn inside_stays_inside() {
        // walking out: back to the last tick's spot
        assert_eq!(hold(&RING, &p(), true, Some((525000, 400000)), (532000, 400000), 6000), Some((525000, 400000)));
        // well inside: free
        assert_eq!(hold(&RING, &p(), true, Some((510000, 400000)), (512000, 400000), 6000), None);
        // no good last spot: pushed back onto the inner side along the ray
        assert_eq!(hold(&RING, &p(), true, None, (540000, 400000), 6000), Some((500000 + 29999, 400000)));
    }

    #[test]
    fn outside_stays_outside() {
        assert_eq!(hold(&RING, &p(), false, Some((550000, 400000)), (538000, 400000), 6000), Some((550000, 400000)));
        assert_eq!(hold(&RING, &p(), false, Some((560000, 400000)), (555000, 400000), 6000), None);
        assert_eq!(hold(&RING, &p(), false, None, (500000, 430000), 6000), Some((500000, 400000 + 42001)));
    }

    #[test]
    fn the_side_is_where_it_stood() {
        assert!(starts_inside(&RING, &p(), 520000, 410000));
        assert!(!starts_inside(&RING, &p(), 540000, 400000));
    }
}
