//! 提莫附加包：R「种蘑菇」照英雄联盟一直埋在地上（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补
//! 附加包」）。
//!
//! 主包是纯数据：蘑菇是一个限时的范围投射物，最多潜伏 12 秒。英雄联盟里蘑菇埋好后几分钟都在，提莫死了也在，敌人踩上才炸。
//! 本包：副本里每个蘑菇落地之后的那一串（踩发判定、毒云、每 15 tick 的蘑菇画面）换成原生效果
//! `league_teemo_shrooms:plant`（`input` 就是落点）；被动 `league_teemo_shrooms:shrooms` 管所有埋着的蘑菇：
//!
//! - 落地 `ARM` tick 后布好，之后 `LIFE` tick 内一直在（最多 `MAX` 个，再多就收掉最早的）；每 `PIC_EVERY` tick 在原地播一次
//!   主包的蘑菇画面（同主包，画面自己会淡入草里）。
//! - 敌人（英雄、小兵、野怪）走到 `TRIGGER` 内就炸：播主包的爆炸画面和声音，`CLOUD` 内的敌人中毒 4 秒——每 60 tick
//!   `POISON` + `POISON_AP`% 法强的魔法伤害、共 4 跳（同主包 100 + 48%），减速 40% 2 秒，播中毒画面。
//! - 提莫阵亡后蘑菇照样在（被动每 tick 都在看，伤害仍算他的）。
//! - **0.2.0 主动往草丛里种**（用户 2026-10-30：「提莫好像不会种蘑菇了？」→「要，照LOL种」）：游戏的 AI 只把 R 往敌方英雄
//!   脚下扔。AI 钩子 `league_teemo_shrooms:sow`（`src/sow.rs`）在他没在打架、R 有多余充能时替 AI 把 R 按在身边最近的草丛里；
//!   草丛格子由读图钩子读地图文档的 `bushes`（奈德丽附加包的 `bush.rs`），他埋着的蘑菇由被动每 tick 记进 `FIELDS` 给钩子看。
//!
//! 落点经 `PLANTED` 交给被动、埋着的蘑菇经 `FIELDS` 给钩子：同一时间跑着几份模拟（服务器同一局两份预模拟并排跑，种子、局、
//! 实体编号都一样；还有观看），按每份模拟的编号（`SIM_TAG`，被动出生时挂在他身上）各记各的。0.2.1：以前按种子、来源、局记，
//! 并排的两份预模拟互相拿走对方的蘑菇，有提莫的局两份预模拟就分了岔（2026-10-30 的日志）。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_teemo_shrooms.log`。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[path = "../../league_nidalee/src/bush.rs"]
pub mod bush;
pub mod sow;

const ID: &str = "league_teemo_shrooms";
/// The main pack's Teemo (the sowing hook's champion).
pub const HERO: &str = "league_teemo";
const LOG_FIRST: usize = 30;
const LOG_EVERY: usize = 50;
pub const ARM: usize = 60;
pub const LIFE: usize = 10_800;
pub const MAX: usize = 9;
pub const PIC_EVERY: usize = 15;
pub const TRIGGER: f64 = 8_000.0;
pub const CLOUD: f64 = 30_000.0;
pub const POISON: usize = 25;
pub const POISON_AP: usize = 12;
pub const POISON_TICKS: usize = 4;
pub const POISON_PERIOD: usize = 60;
pub const SLOW: (&str, usize, i32) = ("league_teemo_r_slow", 120, -40);
pub const PIC: &str = "league_teemo_r_trap";
pub const BURST: &str = "league_teemo_r_burst";
pub const POISONED: &str = "league_teemo_poisoned";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_TEEMO_SHROOMS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_teemo_shrooms.log");
        }
    }
    PathBuf::from("league_teemo_shrooms.log")
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

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more of a kind: its count when it is to be logged - every one in the match on screen (watched, spectated or
/// replayed), the server's presims (the same match run many times over) the first LOG_FIRST, then every LOG_EVERY-th.
fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let on_screen = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (on_screen || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>, me: usize) -> String {
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
    format!("[{kind} m={} s={}] t={} #{me}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 落点 =====================

/// Each simulation's number: his passive draws one at his first spawn and hangs it on him at every spawn (buff
/// `SIM_TAG<n>`, no stats, no picture; league_galio's way).
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
pub const SIM_TAG: &str = "league_teemo_shrooms_sim:";

/// The simulation number hung on this unit (0: none).
fn sim_no(sim: &StableSim<'_>, id: usize) -> u64 {
    sim.get_entity(id).map_or(0, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .find_map(|b| b.name().strip_prefix(SIM_TAG).and_then(|v| v.parse().ok()))
            .unwrap_or(0)
    })
}

/// Which simulation (and Teemo in it) a planted shroom belongs to.
type Key = (u64, usize);

/// Shrooms planted by the data and not yet taken by the passive (the next tick): (simulation, x, y). More than
/// `MAX_PLANTED` (simulations that ended between a plant and its take): the older half goes.
static PLANTED: Mutex<Vec<(Key, f64, f64)>> = Mutex::new(Vec::new());
const MAX_PLANTED: usize = 4096;

/// Each Teemo's shrooms in the ground, by (simulation, player) - his entity changes with every life, the player does
/// not: the passive writes them every tick, the sowing hook (sow.rs) reads them (new ones keep apart from them, and its
/// own show up there).
type FieldKey = (u64, usize);
static FIELDS: LazyLock<Mutex<HashMap<FieldKey, Vec<Shroom>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// More fields remembered than this (matches that ended): start over.
const MAX_FIELDS: usize = 4096;

fn publish(sim_no: u64, player: usize, field: &[Shroom]) {
    let mut f = FIELDS.lock().unwrap_or_else(|e| e.into_inner());
    if f.len() > MAX_FIELDS {
        f.clear();
    }
    f.insert((sim_no, player), field.to_vec());
}

/// The player's Teemo's shrooms in the ground (`me`: his champion now; none before his passive has run).
fn field_of(sim: &StableSim<'_>, player: usize, me: usize) -> Vec<Shroom> {
    FIELDS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim_no(sim, me), player)).cloned().unwrap_or_default()
}

struct Plant;

impl StableEffectType for Plant {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let at = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|e| (e.pos().0 as f64, e.pos().1 as f64)),
            _ => Some((input.x as f64, input.y as f64)),
        };
        let Some((x, y)) = at else { return };
        let k = (sim_no(sim, caster), caster);
        let mut p = PLANTED.lock().unwrap_or_else(|e| e.into_inner());
        if p.len() > MAX_PLANTED {
            p.drain(..MAX_PLANTED / 2); // nobody took them: simulations that have ended
        }
        p.push((k, x, y));
    }
}

// ===================== 蘑菇 =====================

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Shroom {
    pub at: Pt,
    pub planted: usize,
}

impl Shroom {
    pub fn armed(&self, tick: usize) -> bool {
        tick >= self.planted + ARM
    }
    pub fn gone(&self, tick: usize) -> bool {
        tick >= self.planted + LIFE
    }
}

/// Add one, dropping the oldest past `MAX`.
pub fn add(field: &mut Vec<Shroom>, s: Shroom) {
    field.push(s);
    while field.len() > MAX {
        field.remove(0);
    }
}

/// The first armed shroom an enemy at one of `foes` stands on.
pub fn stepped(field: &[Shroom], foes: &[Pt], tick: usize) -> Option<usize> {
    field.iter().position(|s| s.armed(tick) && foes.iter().any(|f| dist(*f, s.at) <= TRIGGER))
}

fn pos_input(p: Pt) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

#[derive(Clone, Default)]
struct Shrooms {
    field: Vec<Shroom>,
    /// 中毒的人：下一跳的 tick、还剩几跳。
    poisoned: HashMap<usize, (usize, usize)>,
    planted: usize,
    booms: usize,
    /// 这份模拟的编号（`SIM_TAG`），他第一次出生时抽。
    sim: u64,
}

impl StablePassive for Shrooms {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if self.sim == 0 {
            self.sim = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        wlog(format!("{} SPAWN: the add-on's Teemo (player {player}), {} shrooms in the ground", head(sim, me), self.field.len()));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let tick = sim.tick();
        let k = (self.sim, me);
        let new: Vec<Pt> = {
            let mut p = PLANTED.lock().unwrap_or_else(|e| e.into_inner());
            let mine: Vec<Pt> = p.iter().filter(|q| q.0 == k).map(|q| (q.1, q.2)).collect();
            p.retain(|q| q.0 != k);
            mine
        };
        for at in new {
            add(&mut self.field, Shroom { at, planted: tick });
            self.planted += 1;
            // one count for all Teemos (0.2.1): 80 a Teemo logged every plant of every presim (830 KB a launch)
            if let Some(k) = tally(sim, "plant") {
                wlog(format!("{} PLANT #{} at ({:.0}, {:.0}), {} in the ground #{k}", head(sim, me), self.planted, at.0,
                             at.1, self.field.len()));
            }
        }
        self.field.retain(|s| !s.gone(tick));
        publish(self.sim, player, &self.field);
        for s in self.field.iter().filter(|s| s.armed(tick) && (tick - s.planted - ARM) % PIC_EVERY == 0) {
            sim.play_view_effect(PIC, me, &pos_input(s.at), 0, 0, 0);
        }
        let Some((team, power)) = sim.get_entity(me).map(|e| (e.team(), e.stat().magic_power)) else { return };
        let foes: Vec<(usize, Pt)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
            .map(|u| (u.id(), (u.pos().0 as f64, u.pos().1 as f64)))
            .collect();
        let points: Vec<Pt> = foes.iter().map(|f| f.1).collect();
        while let Some(i) = stepped(&self.field, &points, tick) {
            let s = self.field.remove(i);
            sim.play_view_effect(BURST, me, &pos_input(s.at), 0, 0, 0);
            sim.play_sfx(BURST, me, &pos_input(s.at));
            let hit: Vec<usize> = foes.iter().filter(|f| dist(f.1, s.at) <= CLOUD).map(|f| f.0).collect();
            for id in &hit {
                self.poisoned.insert(*id, (tick + POISON_PERIOD, POISON_TICKS));
                let mut slow = BuffV1::timed(SLOW.0, SLOW.1);
                slow.move_speed_mult = SLOW.2;
                sim.add_buff(*id, &slow);
                sim.play_view_effect(POISONED, me, &InputTargetV1::target(*id), 0, 0, 0);
            }
            self.booms += 1;
            if let Some(k) = tally(sim, "boom") {
                wlog(format!("{} BOOM #{} at ({:.0}, {:.0}) {} ticks after planting: {} enemies poisoned #{k}", head(sim, me),
                             self.booms, s.at.0, s.at.1, tick - s.planted, hit.len()));
            }
            publish(self.sim, player, &self.field);
        }
        let damage = POISON + power * POISON_AP / 100;
        let due: Vec<usize> = self.poisoned.iter().filter(|(_, v)| tick >= v.0).map(|(k, _)| *k).collect();
        for id in due {
            let (_, left) = self.poisoned[&id];
            if sim.get_entity(id).is_some_and(|e| e.is_alive()) {
                sim.deal_damage_typed(me, id, damage, DamageTypeV1::Ap, AttackTypeV1::Skill);
            }
            if left <= 1 {
                self.poisoned.remove(&id);
            } else {
                self.poisoned.insert(id, (tick + POISON_PERIOD, left - 1));
            }
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Teemo's shrooms stay in the ground for minutes, and he sows them in the bushes) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:plant"), Plant);
    module.add_native_passive(format!("{ID}:shrooms"), Shrooms::default());
    // 0.2.0: out of fights he sows his spare shrooms in the bushes near him (src/sow.rs)
    module.add_player_input_ai(sow::Sow::default());
    host.log(LogLevel::Info, "league_teemo_shrooms v1 loaded (Noxious Traps stay for minutes, sown in the bushes).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    // the bush grid (in league_addons the bundle's MapReaders calls bush::BushReader::read)
    module.set_map_customizer(bush::BushReader);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_sim_tag_fits_a_buff_name() {
        assert!(format!("{SIM_TAG}{}", u64::MAX).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn shrooms_arm_wait_and_go_off_under_feet() {
        let mut f = Vec::new();
        for k in 0..12 {
            add(&mut f, Shroom { at: (k as f64 * 100_000.0, 0.0), planted: k });
        }
        assert_eq!(f.len(), MAX);
        assert_eq!(f[0].planted, 3);
        let s = [Shroom { at: (0.0, 0.0), planted: 100 }];
        assert_eq!(stepped(&s, &[(5_000.0, 0.0)], 120), None); // not armed yet
        assert_eq!(stepped(&s, &[(5_000.0, 0.0)], 160), Some(0));
        assert_eq!(stepped(&s, &[(9_000.0, 0.0)], 5_000), None);
        assert!(s[0].gone(100 + LIFE));
    }
}
