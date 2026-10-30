//! 艾翁附加包（用户 2026-10-22：「需要就做」「还有艾翁的W能触发雷恩加尔的跳 别忘了」「还有奇安娜也可以触发元素 艾翁的这个草
//! 你们两可以联动一下」）：揠苗助攻长出来的草丛是一块真正的草丛。主包的数据读不到位置，只能在长草那一刻给身边的队友加成。
//!
//! `mod.override_info` 把主包的艾翁换成 `override/` 里的副本（tools/kit/build_ivern.py 的 native=1）：数据和主包一样，只是
//! 长草时给他挂 2 tick 的 `league_ivern_w_new`、不再给身边的队友加成（交给本包），被动挂本包的 `league_ivern:brush`。
//!
//! - **记住草丛**：被动每 tick 看他身上有没有 `league_ivern_w_new`：有就去掉它，在他脚下记一丛草（半径 `w_r`，`w_t` tick 后
//!   枯掉）。他死了、草丛还在（英雄联盟的草丛不跟着人走）。
//! - **站在草丛里**：每丛活着的草，范围里的每个英雄（两边都算）挂 2 tick 的 `league_ivern_in_brush`（每 tick 续上）；他的
//!   队友另挂 2 tick 的 `league_ivern_w_buff`（攻击 +`w_atk`%，主包同名的叶子画面）。
//! - **联动**：`league_ivern_in_brush` 是给别的附加包看的：雷恩加尔（league_rengar_bush）站在里面就像站在地图的草丛里一样能扑，
//!   奇亚娜（league_qiyana）突进落地时身上有它就算身边有草（拿草元素）。这三个附加包谁装了都行，标记只是一个 buff，
//!   没装艾翁的附加包时它们照旧只看地图。
//!
//! 每个计时都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量（只有日志的行数是全局的）。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ivern.log`，每次启动游戏重写，上一次的留在 .prev.log。
//! 你看的那场每行都写，服务器的预模拟 SPAWN、BRUSH 各先写 `LOG_FIRST` 行、之后每 `LOG_EVERY` 次一行（见 `tally`）；
//! 行头带 `m=`（哪一场）、`s=`（第几局）：同时跑着的不同场的预模拟分得开。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_ivern";
const HERO: &str = "league_ivern";
/// 别的附加包看的标记（雷恩加尔、奇亚娜）：站在艾翁的草丛里。
pub const IN_BRUSH: &str = "league_ivern_in_brush";
/// 同时最多记这么多丛草（揠苗助攻 4 秒、种豆得瓜 9 秒一次，一般只有一丛）。
const MOST: usize = 8;

fn iv(x: &str) -> String {
    format!("{HERO}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_IVERN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ivern.log");
        }
    }
    PathBuf::from("league_ivern.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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

/// 日志行数的上限（2026-10-30 一次启动 719 KB：78% 是预模拟的 BRUSH，两成多是预模拟的 SPAWN）。计数是全局的：每场预模拟的
/// 被动都是新实例，以前记在实例里的 `grown <= 40 || grown % 50 == 0` 管不住几百场预模拟（一次启动约一万八千丛草）。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind`: its count when it is to be written - every one in the match on screen (watched,
/// spectated or replayed), the server's presims (and background matches) the first `LOG_FIRST`, then every
/// `LOG_EVERY`-th.
fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let on_screen = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (on_screen || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// `[presim m=.. s=..] t=.. #id`: which run, which match and set (presims of different matches running at once told
/// apart), the tick, the unit.
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 草丛的半径（世界单位，主包 w_r）。
    pub w_r: u64,
    /// 草丛活多少 tick（主包 w_t）。
    pub w_t: usize,
    /// 草丛里队友的攻击加成（%，主包 w_atk）。
    pub w_atk: i32,
}

impl Default for Params {
    fn default() -> Self {
        Self { w_r: 26000, w_t: 240, w_atk: 15 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        match k {
            "w_r" => p.w_r = v.max(0) as u64,
            "w_t" => p.w_t = v.max(0) as usize,
            "w_atk" => p.w_atk = v as i32,
            _ => {}
        }
    }
    p
}

// ===================== 草丛（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Brush {
    pub x: u64,
    pub y: u64,
    /// 枯掉的 tick。
    pub until: usize,
}

/// 这个点在这丛草里吗。
pub fn inside(b: &Brush, r: u64, x: u64, y: u64) -> bool {
    let dx = b.x as f64 - x as f64;
    let dy = b.y as f64 - y as f64;
    dx * dx + dy * dy <= (r as f64) * (r as f64)
}

/// 去掉枯了的草，加上新长的（最多 MOST 丛：新的挤掉最早的）。
pub fn grow(list: &mut Vec<Brush>, tick: usize, new: Option<Brush>) {
    list.retain(|b| b.until > tick);
    if let Some(b) = new {
        list.push(b);
        if list.len() > MOST {
            list.remove(0);
        }
    }
}

// ===================== 被动 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 一个 2 tick 的 buff，每 tick 续上（先去掉再加：同名 buff 会叠）。
fn refresh(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, &buff.name());
    sim.add_buff(id, buff);
}

#[derive(Clone, Default)]
struct Brushmaker {
    p: Params,
    brushes: Vec<Brush>,
    grown: usize,
}

impl StablePassive for Brushmaker {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if tally(sim, "spawn").is_some() {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN: the add-on's Ivern (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let new = if has_buff(sim, me, &iv("w_new")) {
            sim.entity_remove_buff(me, &iv("w_new"));
            sim.get_entity(me).map(|e| {
                let (x, y) = e.pos();
                Brush { x, y, until: tick + self.p.w_t }
            })
        } else {
            None
        };
        if let Some(b) = new {
            self.grown += 1;
            if tally(sim, "brush").is_some() {
                wlog(format!("{} BRUSH #{}: at ({}, {}) until t={}", head(sim, me), self.grown, b.x, b.y, b.until));
            }
        }
        grow(&mut self.brushes, tick, new);
        if self.brushes.is_empty() {
            return;
        }
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let mark = BuffV1::timed(IN_BRUSH, 2);
        let mut lift = BuffV1::timed(&iv("w_buff"), 2);
        lift.attack_mult = self.p.w_atk;
        let inside_ids: Vec<(usize, bool)> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.is_alive())
            .filter(|u| {
                let (x, y) = u.pos();
                self.brushes.iter().any(|b| inside(b, self.p.w_r, x, y))
            })
            .map(|u| (u.id(), u.team() == team))
            .collect();
        for (id, ally) in inside_ids {
            refresh(sim, id, &mark);
            if ally && id != me {
                refresh(sim, id, &lift);
            }
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Ivern: Brushmaker's brush a real brush - Rengar pounces from it, Qiyana takes grass from it) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:brush"), Brushmaker::default());
    host.log(LogLevel::Info, "league_ivern loaded (Brushmaker's brush: Rengar and Qiyana read it).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        assert_eq!(parse_params(r#"{"w_atk":15,"w_r":26000,"w_t":240}"#), Params::default());
    }

    #[test]
    fn inside_the_radius() {
        let b = Brush { x: 100_000, y: 100_000, until: 240 };
        assert!(inside(&b, 26_000, 126_000, 100_000));
        assert!(!inside(&b, 26_000, 126_001, 100_000));
        assert!(inside(&b, 26_000, 110_000, 110_000));
    }

    #[test]
    fn brushes_wither_and_the_oldest_goes() {
        let mut v = Vec::new();
        grow(&mut v, 0, Some(Brush { x: 1, y: 1, until: 240 }));
        grow(&mut v, 100, Some(Brush { x: 2, y: 2, until: 340 }));
        assert_eq!(v.len(), 2);
        grow(&mut v, 240, None);
        assert_eq!(v, vec![Brush { x: 2, y: 2, until: 340 }]);
        for k in 0..20 {
            grow(&mut v, 241, Some(Brush { x: k, y: k, until: 1000 }));
        }
        assert_eq!(v.len(), MOST);
        assert_eq!(v.last().unwrap().x, 19);
    }
}
