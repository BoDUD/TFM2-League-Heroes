//! 潘森附加包（用户选「主包数据 + 附加包」，2026-10-16「方案可以，全按推荐做（上单，做附加包，PPU 1.5）」）：主包数据做不到的三件事。
//!
//! `mod.override_info` 把主包的潘森换成 `override/` 里的副本（tools/kit/build_pantheon.py 的 native=1）：数据和主包一样，只是
//! - 被动挂本包的 `league_pantheon:will`（参数在英雄数据的 `passive.params` 里）；
//! - E 举盾不再带四面的减伤（本包只挡正面）；
//! - Q 命中时调本包的 `league_pantheon:spear`；
//! - R 每次轮询时问每一个敌方英雄，调本包的 `league_pantheon:starfall`，被选中的那个才是落点。
//!
//! - **神佑枪阵只挡正面**：举盾（他身上有 `league_pantheon_e_hold`）期间盾朝最近的敌方英雄；从盾那一侧的半圆打来的伤害
//!   全部还回去（受伤后立刻把血加回来，布隆附加包的做法），背后来的、防御塔打的不挡（英雄联盟：「免疫来自该方向的非防御塔伤害」）。
//! - **贯星长枪的斩杀**：命中时目标血量低于最大生命的 `Q_LOW`%，再造成一份 `q_dmg` + `q_ratio`% 攻击力的物理伤害
//!   （英雄联盟里对 20% 以下的敌人伤害约翻一倍多；主包数据读不到当前血量）。
//! - **大荒星陨挑落点**：离潘森至少 `r_min` 的敌方英雄里，身边（`r_sur`）有友方英雄在打、或者 `r_r` 以内还有别的敌方英雄的
//!   才算；落点敌方英雄多的优先，再挑血量比例低的。选中的英雄让潘森身上出现 1 tick 的 `league_pantheon_r_this`，数据接着下蹲、
//!   起跳、落下。
//!
//! 被动的满层（开局、复活）主包数据已经做了，这里不重复。
//! 数字：`Q_LOW` 写在这里；其余从英雄数据来，`tests::the_numbers_match_the_kit` 读主包的参数表核对默认值。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_pantheon.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_pantheon";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_pantheon") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

// ===================== 数值 =====================

/// Q 的斩杀线：目标血量低于最大生命的这个百分比（英雄联盟 20%）。
pub const Q_LOW: usize = 20;
/// 举盾时盾朝多远以内最近的敌方英雄。
pub const FACE_REACH: f64 = 90_000.0;

fn pn(x: &str) -> String {
    format!("league_pantheon_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_PANTHEON_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_pantheon.log");
        }
    }
    PathBuf::from("league_pantheon.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening it for every line stalled the simulation thread (league_galio, 2026-10-12)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first).
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
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

// ===================== 计算（单元测试用） =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// `p` 在从 `me` 朝 `dir`（单位向量）的那一侧（前方半圆）吗。
pub fn in_front(me: (f64, f64), dir: (f64, f64), p: (f64, f64)) -> bool {
    (p.0 - me.0) * dir.0 + (p.1 - me.1) * dir.1 > 0.0
}

/// 血量 `hp` / `max` 在 Q 的斩杀线以下吗。
pub fn is_low(hp: usize, max: usize) -> bool {
    max > 0 && hp * 100 < max * Q_LOW
}

/// 一个可以落下去的敌方英雄。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Spot {
    pub id: usize,
    /// 离潘森多远。
    pub far: f64,
    /// 血量比例 0..1。
    pub hp: f64,
    /// 它 `r_r` 以内的敌方英雄（连它自己）、`r_sur` 以内的友方英雄。
    pub foes: usize,
    pub allies: usize,
}

/// 落在谁那里：够远、身边有友军在打的里面，落点敌人多的优先，再挑血量比例低的。没有友军也跳（落点两个敌人就算）的
/// 第一版：日志里 41 次有 35 次身边没有友军，几乎每次落地后半分钟内就死了（用户：「看一下附加包的日志对不对」）。
pub fn choose(spots: &[Spot], r_min: f64) -> Option<usize> {
    spots
        .iter()
        .filter(|s| s.far >= r_min && s.allies >= 1)
        .max_by(|a, b| {
            a.foes.cmp(&b.foes).then(b.hp.partial_cmp(&a.hp).unwrap_or(std::cmp::Ordering::Equal))
        })
        .map(|s| s.id)
}

// ===================== 小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn alive_at(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() {
        return None;
    }
    let (x, y) = e.pos();
    Some((x as f64, y as f64))
}

/// 某一队活着、能被选中的英雄：(id, 位置)。
fn champions(sim: &StableSim<'_>, team: usize, same: bool) -> Vec<(usize, (f64, f64))> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if (u.team() == team) != same || !u.is_alive() || !u.is_targetable() || !u.is_champion() {
            continue;
        }
        let (x, y) = u.pos();
        out.push((u.id(), (x as f64, y as f64)));
    }
    out
}

// ===================== 参数（英雄数据的 passive.params） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// Q 的伤害（斩杀时再来一份）。
    pub q_dmg: usize,
    pub q_ratio: usize,
    /// R：落点至少多远、落点身边多远算有友军在打、落地半径。
    pub r_min: usize,
    pub r_sur: usize,
    pub r_r: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { q_dmg: 90, q_ratio: 100, r_min: 35_000, r_sur: 30_000, r_r: 32_000 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "q_dmg" => p.q_dmg = v,
            "q_ratio" => p.q_ratio = v,
            "r_min" => p.r_min = v,
            "r_sur" => p.r_sur = v,
            "r_r" => p.r_r = v,
            _ => {}
        }
    }
    p
}

/// 每个潘森的参数（native effect 按施法者找）。
static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

// ===================== Q 的斩杀 =====================

struct Spear;

impl StableEffectType for Spear {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let target = input.target_id;
        let Some((hp, max)) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        if !is_low(hp, max) {
            return;
        }
        let p = params_of(caster);
        let ad = sim.get_entity(caster).map_or(0, |e| e.stat().attack);
        let amount = p.q_dmg + p.q_ratio * ad / 100;
        sim.deal_damage_typed(caster, target, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
        sim.play_view_effect(&pn("q_low"), caster, &InputTargetV1::target(target), 0, 0, 0);
        if let Some(k) = counted("low") {
            wlog(format!("{} LOW #{k} {} at {hp}/{max}: +{amount} physical", head(sim, caster), who(sim, target)));
        }
    }
}

// ===================== R 挑落点 =====================

/// 这一 tick 选好的落点（每份模拟的每个潘森一份：同一 tick 每个敌方英雄都会来问一次，只算一遍）。
static PICKS: LazyLock<Mutex<HashMap<(u64, usize), (usize, Option<usize>)>>> =
    LazyLock::new(|| Mutex::new(HashMap::new()));

/// 每份模拟的潘森一个编号，出生时由被动挂在他身上（buff `league_pantheon_sim:<编号>`，没有数值、没有画面）：游戏 0.6.4
/// 同一局两份预模拟和画面同时跑，实体编号和 tick 都一样，只按实体记会串到别的模拟（加里奥附加包的做法）。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
const SIM_TAG: &str = "league_pantheon_sim:";

/// The number the passive hung on him when he spawned in this sim (0: none).
pub fn sim_tag(names: impl Iterator<Item = String>) -> u64 {
    names.into_iter().find_map(|n| n.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())).unwrap_or(0)
}

fn sim_of(sim: &StableSim<'_>, me: usize) -> u64 {
    sim.get_entity(me).map_or(0, |e| sim_tag((0..e.buff_count()).filter_map(|i| e.buff_at(i))
        .map(|b| b.name().to_string())))
}

fn pick_for(sim: &StableSim<'_>, me: usize) -> Option<usize> {
    let tick = sim.tick();
    let key = (sim_of(sim, me), me);
    if let Some(&(t, id)) = PICKS.lock().unwrap_or_else(|e| e.into_inner()).get(&key) {
        if t == tick {
            return id;
        }
    }
    let p = params_of(me);
    let at = alive_at(sim, me)?;
    let team = sim.get_entity(me)?.team();
    let foes = champions(sim, team, false);
    let friends: Vec<_> = champions(sim, team, true).into_iter().filter(|a| a.0 != me).collect();
    let mut spots = Vec::new();
    for &(id, pos) in &foes {
        let Some(e) = sim.get_entity(id) else { continue };
        let (hp, max) = e.hp();
        spots.push(Spot {
            id,
            far: dist(at, pos),
            hp: if max > 0 { hp as f64 / max as f64 } else { 1.0 },
            foes: foes.iter().filter(|f| dist(pos, f.1) <= p.r_r as f64).count(),
            allies: friends.iter().filter(|a| dist(pos, a.1) <= p.r_sur as f64).count(),
        });
    }
    let id = choose(&spots, p.r_min as f64);
    let mut picks = PICKS.lock().unwrap_or_else(|e| e.into_inner());
    if picks.len() > 4096 {
        picks.clear(); // finished sims
    }
    picks.insert(key, (tick, id));
    drop(picks);
    if let Some(s) = id.and_then(|id| spots.iter().find(|s| s.id == id)) {
        if let Some(k) = counted("starfall") {
            wlog(format!("{} STARFALL #{k} -> {}: {} enemy champions where he lands, {} allies fighting there, hp {:.0}%, \
                          {:.0} away", head(sim, me), who(sim, s.id), s.foes, s.allies, s.hp * 100.0, s.far));
        }
    }
    id
}

struct Starfall;

impl StableEffectType for Starfall {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        if pick_for(sim, caster) == Some(input.target_id) {
            sim.add_buff(caster, &BuffV1::timed(&pn("r_this"), 1));
        }
    }
}

// ===================== 被动：神佑枪阵的方向 =====================

/// 每个潘森一份。
#[derive(Clone, Default)]
struct Will {
    p: Params,
    /// 举着盾吗、盾朝哪（单位向量）、这次举盾挡了多少、挡了几下。
    raised: bool,
    dir: Option<(f64, f64)>,
    blocked: usize,
    hits: usize,
    /// This sim's number (`SIM_TAG`), drawn at his first spawn.
    sim_no: u64,
}

impl Will {
    fn shield(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let on = has_buff(sim, me, &pn("e_hold"));
        let Some(at) = alive_at(sim, me) else {
            self.raised = false;
            return;
        };
        if on && !self.raised {
            self.blocked = 0;
            self.hits = 0;
            self.dir = None;
        }
        if !on && self.raised {
            if let Some(n) = counted("raise") {
                wlog(format!("{} SHIELD #{n} down: {} hits from the front, {} damage given back", head(sim, me),
                             self.hits, self.blocked));
            }
        }
        self.raised = on;
        if !on {
            self.dir = None;
            return;
        }
        // the shield faces the nearest enemy champion (he turns it toward the fight)
        let foes = champions(sim, team, false);
        if let Some(&(_, f)) = foes.iter().filter(|f| dist(at, f.1) <= FACE_REACH).min_by(|a, b| {
            dist(at, a.1).partial_cmp(&dist(at, b.1)).unwrap_or(std::cmp::Ordering::Equal)
        }) {
            let d = dist(at, f);
            if d > 0.0 {
                self.dir = Some(((f.0 - at.0) / d, (f.1 - at.1) / d));
            }
        }
    }
}

impl StablePassive for Will {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.raised = false;
        self.dir = None;
        if self.sim_no == 0 {
            self.sim_no = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim_no);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Pantheon (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(team) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.team()) else {
            self.raised = false;
            return;
        };
        self.shield(sim, me, team);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        if !self.raised || damage == 0 {
            return;
        }
        if sim.get_entity(attacker).is_some_and(|e| e.is_tower()) {
            return;
        }
        let (Some(dir), Some(at), Some(from)) = (self.dir, alive_at(sim, me), alive_at(sim, attacker)) else { return };
        if !in_front(at, dir, from) {
            return;
        }
        // 挡下的伤害直接把血加回去（entity_set_hp，布隆、赵信的做法）：heal 会飘绿色数字、记进治疗量、吃重伤
        let Some((hp, max)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        sim.entity_set_hp(me, (hp + damage).min(max));
        self.blocked += damage;
        self.hits += 1;
        if let Some(n) = counted("block") {
            wlog(format!("{} BLOCK #{n} {} hit {damage} from the front -> all back", head(sim, me), who(sim, attacker)));
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.raised = false;
        self.dir = None;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Pantheon: Aegis Assault blocks the front only, Comet Spear's bonus below {Q_LOW}% health, Grand Starfall picks its spot) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:will"), Will::default());
    module.add_native_effect(format!("{ID}:spear"), Spear);
    module.add_native_effect(format!("{ID}:starfall"), Starfall);
    host.log(LogLevel::Info, "league_pantheon loaded (Aegis Assault front only, Comet Spear execute, Grand Starfall spot).");
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

    #[test]
    fn the_front_half() {
        let me = (0.0, 0.0);
        assert!(in_front(me, (1.0, 0.0), (10.0, 5.0)));
        assert!(!in_front(me, (1.0, 0.0), (-10.0, 5.0)));
    }

    #[test]
    fn low_health() {
        assert!(is_low(199, 1000));
        assert!(!is_low(200, 1000));
        assert!(!is_low(0, 0));
    }

    fn spot(id: usize, far: f64, hp: f64, foes: usize, allies: usize) -> Spot {
        Spot { id, far, hp, foes, allies }
    }

    #[test]
    fn the_spot_to_land_on() {
        // too near, or nobody fighting there and alone: nobody
        assert_eq!(choose(&[spot(1, 20_000.0, 0.2, 3, 2)], 35_000.0), None);
        assert_eq!(choose(&[spot(1, 90_000.0, 0.2, 1, 0)], 35_000.0), None);
        // allies fighting it; two enemies together and no ally is a fall into them alone: nobody
        assert_eq!(choose(&[spot(1, 90_000.0, 0.9, 1, 1)], 35_000.0), Some(1));
        assert_eq!(choose(&[spot(1, 90_000.0, 0.9, 2, 0)], 35_000.0), None);
        // the most enemies first (among those with allies), then the lowest health share
        let s = [spot(1, 90_000.0, 0.3, 1, 2), spot(2, 90_000.0, 0.8, 3, 0), spot(3, 90_000.0, 0.5, 3, 1)];
        assert_eq!(choose(&s, 35_000.0), Some(3));
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"e_r":42000,"e_t":90,"q_dmg":90,"q_ratio":100,"r_min":35000,"r_r":32000,"r_sur":30000}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_pantheon.py");
        let src = std::fs::read_to_string(path).expect("build_pantheon.py");
        let d = Params::default();
        for (key, v) in [("q_dmg", d.q_dmg), ("q_ratio", d.q_ratio), ("r_min", d.r_min), ("r_sur", d.r_sur), ("r_r", d.r_r)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_pantheon.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["e_hold", "r_this", "q_low"] {
            assert!(pn(x).len() <= BUFF_NAME_CAP);
        }
        assert!(format!("{SIM_TAG}{}", u64::MAX).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn each_sim_finds_its_own_number() {
        let names = |v: &[&str]| v.iter().map(|s| s.to_string()).collect::<Vec<_>>().into_iter();
        assert_eq!(sim_tag(names(&["league_pantheon_e_hold", "league_pantheon_sim:7"])), 7);
        assert_eq!(sim_tag(names(&["league_pantheon_r_this"])), 0);
    }
}
