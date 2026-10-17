//! 厄斐琉斯附加包（用户 2026-10-16：「方案可以，全按推荐做（下路 ADC，做附加包，PPU 1.5）」）。主包保持纯数据；
//! `mod.override_info` 把主包的厄斐琉斯换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_aphelios.py 的
//! `native=1` 生成：加上本包的被动 `league_aphelios:queue`，普攻、技能2 的说明开头加【附加包】），本包补数据做不到的三件事：
//!
//! - **整身换武器**（`view.rs`，只在游戏 0.6.4 上）：主手是断魄 / 坠明 / 荧焰 / 折镜（主包的永久 buff
//!   `league_aphelios_mw_<武器>`）时，站着、跑着、挨打、出手的第一刻都画成那把武器在手里（图里的 `<武器>_idle` …），
//!   通碧主手时是原来的样子（通碧背在身后）。
//! - **真实的武器队列**（被动 `queue`）：主包的数据按固定循环（通碧 → 断魄 → 坠明 → 荧焰 → 折镜）换上副手以外的下一把；
//!   英雄联盟是先进先出的队列（打空的那把排到队尾），W 换过手以后两者会不一样。本包每 tick 看主手：数据换了武器、副手没变
//!   （打空换枪）时，按队列该换上的不是数据挑的那把，就把主手 buff 换成队列里那把（射程、吸血、攻速照主包的参数）；
//!   主手和副手互换（W）时队列不动。
//! - **残血换断魄**：生命低于 `low_hp`% 、副手是断魄、`near` 内有看得见的敌方英雄时，直接把断魄换到主手（吸血），每
//!   `low_cd` tick 最多一次（主包的 W 只在主手技能冷却、副手技能好了时才换）。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aphelios.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `QUEUE`（数据换枪，和队列一致 / 改成队列那把）、`LOW`（残血换断魄）、`FORM`（显示里的武器形态），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_aphelios";
const HERO: &str = "league_aphelios";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 五把武器，按主包数据的循环顺序（build_aphelios.WEAPONS）。
pub const WEAPONS: [&str; 5] = ["cal", "sev", "grav", "inf", "cre"];
pub const CAL: usize = 0;
pub const SEV: usize = 1;

pub fn main_buff(w: usize) -> String {
    format!("{HERO}_mw_{}", WEAPONS[w])
}

pub fn off_buff(w: usize) -> String {
    format!("{HERO}_ow_{}", WEAPONS[w])
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_APHELIOS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_aphelios.log");
        }
    }
    PathBuf::from("league_aphelios.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 主手武器 buff 自带的属性（P 的 c_range、sev_vamp、sev_as）。
    pub c_range: usize,
    pub sev_vamp: i32,
    pub sev_as: i32,
    /// 残血换断魄：生命百分比、附近敌方英雄的距离、两次之间的 tick。
    pub low_hp: usize,
    pub near: u64,
    pub low_cd: u64,
}

impl Default for Params {
    fn default() -> Self {
        Self { c_range: 10000, sev_vamp: 10, sev_as: 20, low_hp: 35, near: 60000, low_cd: 360 }
    }
}

/// `{"c_range":10000,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        match k {
            "c_range" => p.c_range = v.max(0) as usize,
            "sev_vamp" => p.sev_vamp = v as i32,
            "sev_as" => p.sev_as = v as i32,
            "low_hp" => p.low_hp = v.max(0) as usize,
            "near" => p.near = v.max(0) as u64,
            "low_cd" => p.low_cd = v.max(0) as u64,
            _ => {}
        }
    }
    p
}

/// 主手武器 buff（和主包数据加的同名同属性：通碧射程、断魄吸血和攻速）。
pub fn weapon_buff(w: usize, p: &Params) -> BuffV1 {
    let mut b = BuffV1::named(&main_buff(w));
    if w == CAL {
        b.range = p.c_range;
    }
    if w == SEV {
        b.vamp = p.sev_vamp;
        b.attack_speed_mult = p.sev_as;
    }
    b
}

// ===================== 武器队列（纯逻辑，单元测试） =====================

/// 一条命里的武器：主手、副手和排队的三把（先进先出）。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Queue {
    pub main: usize,
    pub off: usize,
    pub line: Vec<usize>,
}

/// 这一 tick 看到的变化要怎么处理。
#[derive(Clone, Debug, PartialEq)]
pub enum Step {
    /// 没变 / 第一次看到 / W 互换 / 本包自己换的：只记下来。
    Keep,
    /// 数据打空换枪，换上的就是队列里那把。
    Agree(usize),
    /// 数据打空换枪，队列里该换上的是另一把：(数据挑的, 队列的)。
    Fix(usize, usize),
    /// 看不懂的变化（主手副手都换了，不是互换）：按循环重排队列。
    Resync,
}

impl Queue {
    /// 主手 main、副手 off 时，按数据的循环顺序排出其余三把（这条命开局、或者看不懂的时候）。
    pub fn fresh(main: usize, off: usize) -> Queue {
        let line = (1..5).map(|k| (main + k) % 5).filter(|w| *w != off).collect();
        Queue { main, off, line }
    }

    /// 这一 tick 主手 main、副手 off：更新队列，返回怎么处理。
    pub fn step(&mut self, main: usize, off: usize) -> Step {
        if main == self.main && off == self.off {
            return Step::Keep;
        }
        if main == self.off && off == self.main {
            std::mem::swap(&mut self.main, &mut self.off);
            return Step::Keep;
        }
        if off == self.off && main != self.main && !self.line.is_empty() {
            let want = self.line.remove(0);
            self.line.push(self.main);
            self.main = want;
            return if want == main { Step::Agree(want) } else { Step::Fix(main, want) };
        }
        *self = Queue::fresh(main, off);
        Step::Resync
    }
}

// ===================== 被动：队列 + 残血换断魄 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 身上的主手 / 副手武器（主包数据第一次普攻才加；之前没有）。
fn weapons_of(sim: &StableSim<'_>, id: usize) -> Option<(usize, usize)> {
    let main = (0..5).find(|w| has_buff(sim, id, &main_buff(*w)))?;
    let off = (0..5).find(|w| has_buff(sim, id, &off_buff(*w)))?;
    Some((main, off))
}

static SHARED: Mutex<Option<Params>> = Mutex::new(None);

fn shared() -> Params {
    SHARED.lock().unwrap_or_else(|e| e.into_inner()).clone().unwrap_or_default()
}

#[derive(Clone, Default)]
struct Moon {
    /// 这条命的队列（None = 还没看到武器）。每个模拟、每个英雄各一份（被动实例不共用）。
    queue: Option<Queue>,
    /// 上次残血换断魄的 tick。
    low_at: Option<u64>,
}

impl Moon {
    fn set_main(sim: &mut StableSim<'_>, me: usize, from: usize, to: usize, p: &Params) {
        sim.entity_remove_buff(me, &main_buff(from));
        sim.add_buff(me, &weapon_buff(to, p));
    }

    fn low_swap(&mut self, sim: &mut StableSim<'_>, me: usize, p: &Params) {
        let Some(q) = self.queue.clone() else { return };
        if q.off != SEV || q.main == SEV {
            return;
        }
        let tick = sim.tick() as u64;
        if self.low_at.is_some_and(|t| tick < t + p.low_cd) {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let (hp, max) = e.hp();
        if max == 0 || hp * 100 >= max * p.low_hp {
            return;
        }
        let (team, at) = (e.team(), e.pos());
        let near = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).any(|u| {
            u.team() != team && u.is_alive() && u.is_champion() && sim.is_visible(team, u.id()) && {
                let (dx, dy) = (u.pos().0 as f64 - at.0 as f64, u.pos().1 as f64 - at.1 as f64);
                (dx * dx + dy * dy).sqrt() <= p.near as f64
            }
        });
        if !near {
            return;
        }
        // the swap the data's W does: Severum to the main hand, the main weapon to the off hand
        Moon::set_main(sim, me, q.main, SEV, p);
        sim.entity_remove_buff(me, &off_buff(SEV));
        sim.add_buff(me, &BuffV1::named(&off_buff(q.main)));
        self.low_at = Some(tick);
        if let Some(k) = counted("low") {
            wlog(format!("{} LOW {}% hp, an enemy champion within {}: Severum to the main hand, {} to the off hand #{k}",
                head(sim, me), hp * 100 / max, p.near, WEAPONS[q.main]));
        }
    }
}

impl StablePassive for Moon {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let p = parse_params(params_json);
        let mut s = SHARED.lock().unwrap_or_else(|e| e.into_inner());
        if s.as_ref() != Some(&p) {
            wlog(format!("params {params_json} -> {p:?}"));
            *s = Some(p);
        }
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.queue = None;
        self.low_at = None;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        let Some((main, off)) = weapons_of(sim, me) else { return };
        let p = shared();
        match self.queue.as_mut() {
            None => self.queue = Some(Queue::fresh(main, off)),
            Some(q) => match q.step(main, off) {
                Step::Keep => {}
                Step::Agree(w) => {
                    if let Some(k) = counted("queue") {
                        wlog(format!("{} QUEUE {} empty -> {} (the data's pick is the queue's) #{k}", head(sim, me),
                            WEAPONS[q.line[q.line.len() - 1]], WEAPONS[w]));
                    }
                }
                Step::Fix(data, want) => {
                    Moon::set_main(sim, me, data, want, &p);
                    if let Some(k) = counted("queue") {
                        wlog(format!("{} QUEUE {} empty -> {} (the data took {}; queue now {:?}) #{k}", head(sim, me),
                            WEAPONS[q.line[q.line.len() - 1]], WEAPONS[want], WEAPONS[data],
                            q.line.iter().map(|w| WEAPONS[*w]).collect::<Vec<_>>()));
                    }
                }
                Step::Resync => {
                    if let Some(k) = counted("queue") {
                        wlog(format!("{} QUEUE resync: main {} off {} #{k}", head(sim, me), WEAPONS[main], WEAPONS[off]));
                    }
                }
            },
        }
        self.low_swap(sim, me, &p);
        // the low swap changed the buffs: let the queue see it as a swap next tick (main and off exchanged)
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Aphelios: the whole-body weapon forms, the real weapon queue, Severum when low) loaded: game {}.{}.{} abi {} log={} ===",
        v.major, v.minor, v.patch, host.abi_level(), LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:queue"), Moon::default());
    host.log(LogLevel::Info, "league_aphelios loaded (weapon forms, the weapon queue, Severum when low).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_queue_starts_in_the_cycle() {
        let q = Queue::fresh(CAL, SEV);
        assert_eq!(q.line, vec![2, 3, 4]);
    }

    #[test]
    fn without_swaps_the_queue_and_the_cycle_agree() {
        let mut q = Queue::fresh(CAL, SEV);
        assert_eq!(q.step(2, SEV), Step::Agree(2)); // Calibrum empty -> Gravitum
        assert_eq!(q.line, vec![3, 4, 0]);
        assert_eq!(q.step(3, SEV), Step::Agree(3));
        assert_eq!(q.step(4, SEV), Step::Agree(4));
        assert_eq!(q.step(0, SEV), Step::Agree(0));
    }

    #[test]
    fn after_a_swap_the_queue_wins() {
        // the counterexample of the plan: main Calibrum off Severum; W; Severum empty -> Gravitum (both agree);
        // W (main Calibrum, off Gravitum); Calibrum empty: the queue gives Infernum, the cycle Severum
        let mut q = Queue::fresh(CAL, SEV);
        assert_eq!(q.step(SEV, CAL), Step::Keep); // W
        assert_eq!(q.step(2, CAL), Step::Agree(2)); // Severum empty -> Gravitum; line [3, 4, 1]
        assert_eq!(q.step(CAL, 2), Step::Keep); // W
        assert_eq!(q.step(SEV, 2), Step::Fix(SEV, 3)); // the data took Severum, the queue Infernum
        assert_eq!(q.main, 3);
        assert_eq!(q.line, vec![4, 1, 0]);
    }

    #[test]
    fn a_strange_change_resyncs() {
        let mut q = Queue::fresh(CAL, SEV);
        assert_eq!(q.step(3, 4), Step::Resync);
        assert_eq!(q, Queue::fresh(3, 4));
    }

    #[test]
    fn params_from_the_main_pack() {
        let p = parse_params(r#"{"c_range": 10000, "sev_vamp": 12, "sev_as": 25, "low_hp": 30}"#);
        assert_eq!((p.c_range, p.sev_vamp, p.sev_as, p.low_hp, p.near), (10000, 12, 25, 30, 60000));
    }

    #[test]
    fn the_weapon_buffs_carry_the_main_packs_stats() {
        let p = Params::default();
        let c = weapon_buff(CAL, &p);
        assert_eq!((c.name(), c.range), ("league_aphelios_mw_cal", 10000));
        let s = weapon_buff(SEV, &p);
        assert_eq!((s.vamp, s.attack_speed_mult), (10, 20));
        assert_eq!(weapon_buff(2, &p).range, 0);
    }

    #[test]
    fn the_copy_carries_the_passive_and_the_main_packs_numbers() {
        let copy = include_str!("../override/league_aphelios.data_champion");
        assert!(copy.contains("\"passive_ref\": \"league_aphelios:queue\""));
        for k in ["c_range", "sev_vamp", "sev_as", "low_hp", "near", "low_cd"] {
            assert!(copy.contains(&format!("\"{k}\"")), "{k} missing from the copy's params");
        }
        for w in WEAPONS {
            assert!(copy.contains(&format!("\"league_aphelios_mw_{w}\"")), "the copy has no mw_{w}");
            assert!(copy.contains(&format!("\"league_aphelios_ow_{w}\"")), "the copy has no ow_{w}");
        }
    }
}
