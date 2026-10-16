//! 芮尔附加包（用户 2026-10-16：「方案可以」，做附加包）。主包保持纯数据；`mod.override_info` 把主包的芮尔换成 `override/` 里的
//! 副本（`make_override.py` 用 tools/kit/build_rell.py 的 `native=1` 生成：被动换成本包的 `league_rell:iron`，数据里每个打中英雄
//! 的地方的「溃敌沉力」换成本包的原生效果 `league_rell:mold`，裂阵每个命中多调一次 `league_rell:shatter`，全速冲锋的第二段不再
//! 自己加到 30%，普攻、技能、技能2 的说明开头加【附加包】），本包补数据做不到的四件事：
//!
//! - **下马整身换形态**（`view.rs`，只在游戏 0.6.4 上）：下马作战（主包的 buff `league_rell_foot`）时站着、走着、挨打、普攻、裂阵、
//!   阵亡都是披甲步行的她（图里的 `f_*`），上马（驾临或下马时间到）换回骑马。
//! - **溃敌沉力按目标叠层**（原生效果 `mold`）：每个敌方英雄身上单独叠，最多 `STACKS` 层，每次命中刷新 `p_t` tick；每层削减它
//!   `p_shred`% 护甲和魔抗。第一层时记下它当时的护甲和魔抗（英雄联盟：之后的层都按这个快照算），芮尔每层得到快照的 `p_shred`%
//!   （至少 `STEAL_MIN`）作为额外护甲和魔抗，由被动每 tick 按各目标的层数汇总成一个 buff（`league_rell_p_steal`）。
//! - **裂阵打破护盾**（原生效果 `shatter`）：命中的单位身上所有护盾清掉（英雄联盟的裂阵先破盾再伤害）。
//! - **全速冲锋朝着跑时翻倍**（被动）：她和被加速的队友身上有全速冲锋的加速时，正朝最近的敌方英雄、或朝对方（她朝队友、队友
//!   朝她）跑，就再加 `e_toward`% 移速（英雄联盟：朝敌人或彼此时加速翻倍）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_rell.log`，每次启动游戏重写，上一次的留在 .prev.log：`FORM`（模拟里
//! 下马 / 上马、画面里换形态）、`MOLD`（叠层）、`STEAL`（她拿到的双抗）、`SHATTER`（破了谁的盾、多少）、`TILT`（E 的朝向加速）、
//! `RFIRE`（极涌放出时身边几个敌方英雄），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_rell";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 下马作战（主包数据的 buff）。
pub const FORM: &str = "league_rell_foot";
/// 目标身上的叠层（每层一个同名 buff）、记快照的 buff（名字带着数字）、她身上汇总的双抗。
pub const SHRED: &str = "league_rell_p_shred";
pub const SNAP: &str = "league_rell_p_snap:";
pub const STEAL: &str = "league_rell_p_steal";
/// 全速冲锋的两段加速（主包数据）和本包加的朝向加速。
pub const E_MS: [&str; 2] = ["league_rell_e_ms", "league_rell_e_ms2"];
pub const TOWARD: &str = "league_rell_e_toward";
pub const R_ON: &str = "league_rell_r_on";
pub const E_READY: &str = "league_rell_e_ready";
/// 每个目标最多几层（英雄联盟 5 层）；每层她至少拿到多少。
pub const STACKS: usize = 5;
pub const STEAL_MIN: i32 = 2;
/// 朝着跑：移动方向和到对方的方向夹角的余弦至少这么大；最近的敌方英雄在这么远内才算。
pub const TOWARD_COS: f64 = 0.7;
pub const TOWARD_R: f64 = 120_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_RELL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_rell.log");
        }
    }
    PathBuf::from("league_rell.log")
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 溃敌沉力：每层持续几 tick、每层削减 / 偷取的百分比（p_t、p_shred）。
    pub p_t: usize,
    pub p_shred: usize,
    /// 全速冲锋：朝着跑时多加的移速百分比（e_ms2 - e_ms1）。
    pub e_toward: usize,
    /// 极涌的半径（日志里数身边的敌方英雄）。
    pub r_r: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_t: 300, p_shred: 3, e_toward: 15, r_r: 34000 }
    }
}

/// `{"p_t":300,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "p_t" => p.p_t = v,
            "p_shred" => p.p_shred = v,
            "e_toward" => p.e_toward = v,
            "r_r" => p.r_r = v,
            _ => {}
        }
    }
    p
}

static SHARED: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

fn shared() -> Params {
    SHARED.lock().unwrap_or_else(|e| e.into_inner()).clone()
}

// ===================== 计算（单元测试用） =====================

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 快照 buff 的名字：`league_rell_p_snap:<护甲>:<魔抗>`。
pub fn snap_name(def: i32, mr: i32) -> String {
    format!("{SNAP}{def}:{mr}")
}

/// 从快照 buff 的名字读回（护甲, 魔抗）。
pub fn parse_snap(name: &str) -> Option<(i32, i32)> {
    let rest = name.strip_prefix(SNAP)?;
    let (d, m) = rest.split_once(':')?;
    Some((d.parse().ok()?, m.parse().ok()?))
}

/// 一层从快照里偷到的（护甲, 魔抗）：`shred`% ，至少 `STEAL_MIN`。
pub fn steal_per_stack(snap: (i32, i32), shred: usize) -> (i32, i32) {
    let f = |v: i32| (v.max(0) * shred as i32 / 100).max(STEAL_MIN);
    (f(snap.0), f(snap.1))
}

/// 各目标（层数, 快照）汇总成她的（护甲, 魔抗）加成。
pub fn steal_total(targets: &[(usize, (i32, i32))], shred: usize) -> (i32, i32) {
    targets.iter().fold((0, 0), |acc, &(n, snap)| {
        let (d, m) = steal_per_stack(snap, shred);
        (acc.0 + d * n.min(STACKS) as i32, acc.1 + m * n.min(STACKS) as i32)
    })
}

/// 从 `from` 移到 `to`（这一 tick 的位移）是不是朝着 `goal`。
pub fn heading_to(from: Pt, to: Pt, goal: Pt) -> bool {
    let (mx, my) = (to.0 - from.0, to.1 - from.1);
    let (gx, gy) = (goal.0 - from.0, goal.1 - from.1);
    let (lm, lg) = ((mx * mx + my * my).sqrt(), (gx * gx + gy * gy).sqrt());
    if lm < 1.0 || lg < 1.0 {
        return false;
    }
    (mx * gx + my * gy) / (lm * lg) >= TOWARD_COS
}

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    buffs(sim, id).iter().any(|b| b.name() == name)
}

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

// ===================== 被动：铁骑（叠层汇总、E 的朝向加速、日志） =====================

#[derive(Clone, Default)]
struct Iron {
    /// 上一 tick 身上有没有下马 buff（None = 这条命还没看过）。
    foot: Option<bool>,
    /// 上一 tick 的极涌、E 强化。
    r_on: bool,
    e_ready: bool,
    /// 她身上汇总的双抗（上次写进 buff 的）。
    steal: (i32, i32),
    /// 有全速冲锋加速的单位上一 tick 的位置。
    last: HashMap<usize, Pt>,
}

impl Iron {
    fn sum_steal(&mut self, sim: &mut StableSim<'_>, me: usize, p: &Params) {
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let mut targets = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() || !u.is_champion() {
                continue;
            }
            let bs: Vec<BuffV1> = (0..u.buff_count()).filter_map(|k| u.buff_at(k)).collect();
            let n = bs.iter().filter(|b| b.name() == SHRED).count();
            if n == 0 {
                continue;
            }
            let snap = bs.iter().find_map(|b| parse_snap(b.name())).unwrap_or((0, 0));
            targets.push((n, snap));
        }
        let total = steal_total(&targets, p.p_shred);
        if total != self.steal {
            sim.entity_remove_buff(me, STEAL);
            if total != (0, 0) {
                let mut b = BuffV1::named(STEAL);
                b.defence = total.0;
                b.magic_resistance = total.1;
                sim.add_buff(me, &b);
            }
            if let Some(k) = counted("steal") {
                wlog(format!("{} STEAL armour/mr {:+}/{:+} from {} champion{} ({} stacks) #{k}", head(sim, me), total.0, total.1,
                    targets.len(), if targets.len() == 1 { "" } else { "s" }, targets.iter().map(|t| t.0).sum::<usize>()));
            }
            self.steal = total;
        }
    }

    fn tilt(&mut self, sim: &mut StableSim<'_>, me: usize, p: &Params) {
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let (mut hasted, mut foes) = (Vec::new(), Vec::new());
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_alive() || !u.is_champion() {
                continue;
            }
            let at = (u.pos().0 as f64, u.pos().1 as f64);
            if u.team() != team {
                if sim.is_visible(team, u.id()) {
                    foes.push(at);
                }
            } else if (0..u.buff_count()).filter_map(|k| u.buff_at(k)).any(|b| E_MS.contains(&b.name())) {
                hasted.push((u.id(), at));
            }
        }
        let mut seen = HashMap::new();
        for &(id, at) in &hasted {
            seen.insert(id, at);
            let Some(&was) = self.last.get(&id) else { continue };
            let near = foes.iter().copied().filter(|f| dist(at, *f) <= TOWARD_R)
                .min_by(|a, b| dist(at, *a).total_cmp(&dist(at, *b)));
            let partner = hasted.iter().find(|&&(o, _)| o != id).map(|&(_, a)| a);
            let why = if near.is_some_and(|f| heading_to(was, at, f)) {
                Some("an enemy champion")
            } else if partner.is_some_and(|q| heading_to(was, at, q)) {
                Some(if id == me { "her ally" } else { "Rell" })
            } else {
                None
            };
            if let Some(why) = why {
                let mut b = BuffV1::timed(TOWARD, 3);
                b.move_speed_mult = p.e_toward as i32;
                sim.entity_stack_buff(id, &b, 1, true);
                if let Some(k) = counted("tilt") {
                    wlog(format!("{} TILT {} runs toward {why}: +{}% move speed #{k}", head(sim, me), who(sim, id), p.e_toward));
                }
            }
        }
        self.last = seen;
    }
}

impl StablePassive for Iron {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let p = parse_params(params_json);
        let mut s = SHARED.lock().unwrap_or_else(|e| e.into_inner());
        if *s != p {
            wlog(format!("params {params_json} -> {p:?}"));
            *s = p;
        }
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.foot = None;
        self.steal = (0, 0);
        self.last.clear();
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN {} (mounted) #{k}", head(sim, entity), who(sim, entity)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let p = shared();
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        let foot = has_buff(sim, me, FORM);
        if self.foot.is_some_and(|was| was != foot) {
            if let Some(k) = counted("form_sim") {
                wlog(format!("{} FORM sim: {}{} #{k}", head(sim, me),
                    if foot { "DISMOUNTED (Crash Down)" } else { "mounted again" }, if alive { "" } else { ", dead" }));
            }
        }
        self.foot = Some(foot);
        if !alive {
            return;
        }
        let r_on = has_buff(sim, me, R_ON);
        if r_on && !self.r_on {
            let (team, at) = match sim.get_entity(me) {
                Some(e) => (e.team(), (e.pos().0 as f64, e.pos().1 as f64)),
                None => return,
            };
            let n = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).filter(|u| {
                u.team() != team && u.is_alive() && u.is_champion() && dist(at, (u.pos().0 as f64, u.pos().1 as f64)) <= p.r_r as f64
            }).count();
            if let Some(k) = counted("rfire") {
                wlog(format!("{} RFIRE Magnet Storm with {n} enemy champion{} within {} #{k}", head(sim, me),
                    if n == 1 { "" } else { "s" }, p.r_r));
            }
        }
        self.r_on = r_on;
        let e_ready = has_buff(sim, me, E_READY);
        if e_ready && !self.e_ready {
            if let Some(k) = counted("ecast") {
                wlog(format!("{} ECAST Full Tilt: her next attack or Shattering Strike explodes #{k}", head(sim, me)));
            }
        }
        self.e_ready = e_ready;
        self.sum_steal(sim, me, &p);
        self.tilt(sim, me, &p);
    }
}

// ===================== 原生效果：溃敌沉力按目标叠层 =====================

struct Mold;

impl StableEffectType for Mold {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(target) = target_of(&input) else { return };
        let p = shared();
        let Some(e) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_champion()) else { return };
        let (def, mr) = (e.stat().defence, e.stat().magic_resistance);
        let before: Vec<BuffV1> = (0..e.buff_count()).filter_map(|k| e.buff_at(k)).collect();
        let fresh = !before.iter().any(|b| b.name() == SHRED);
        let mut b = BuffV1::timed(SHRED, p.p_t);
        b.defence_mult = -(p.p_shred as i32);
        b.magic_resistance_mult = -(p.p_shred as i32);
        let n = sim.entity_stack_buff(target, &b, STACKS, true);
        // the snapshot: taken on the first stack, kept (refreshed) while the stacks last
        let snap = if fresh {
            for old in before.iter().filter(|b| b.name().starts_with(SNAP)) {
                sim.entity_remove_buff(target, old.name());
            }
            (def as i32, mr as i32)
        } else {
            before.iter().find_map(|b| parse_snap(b.name())).unwrap_or((def as i32, mr as i32))
        };
        sim.entity_stack_buff(target, &BuffV1::timed(&snap_name(snap.0, snap.1), p.p_t), 1, true);
        if let Some(k) = counted("mold") {
            wlog(format!("{} MOLD {}: {n} stack{} (snapshot armour {} / mr {}){} #{k}", head(sim, caster), who(sim, target),
                if n == 1 { "" } else { "s" }, snap.0, snap.1, if fresh { ", first" } else { "" }));
        }
    }
}

// ===================== 原生效果：裂阵破盾 =====================

struct Shatter;

impl StableEffectType for Shatter {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(target) = target_of(&input) else { return };
        let Some(e) = sim.get_entity(target).filter(|e| e.is_alive()) else { return };
        let amount = e.shield();
        if amount == 0 {
            return;
        }
        let layers = sim.entity_clear_shield(target);
        if let Some(k) = counted("shatter") {
            wlog(format!("{} SHATTER {}: {layers} shield layer{} ({amount}) broken #{k}", head(sim, caster), who(sim, target),
                if layers == 1 { "" } else { "s" }));
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
        "=== {ID} v{VERSION} (Rell: the whole body on foot, Break the Mold per champion, Shattering Strike breaks shields, Full Tilt toward) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:iron"), Iron::default());
    module.add_native_effect(format!("{ID}:mold"), Mold);
    module.add_native_effect(format!("{ID}:shatter"), Shatter);
    host.log(LogLevel::Info, "league_rell loaded (whole body on foot, Break the Mold per champion, shield-breaking Shattering Strike, Full Tilt toward).");
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
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"p_shred":4,"junk":7,"e_toward":20}"#);
        assert_eq!((p.p_shred, p.e_toward, p.p_t, p.r_r), (4, 20, 300, 34000));
    }

    #[test]
    fn the_copy_carries_the_default_params_and_the_native_effects() {
        let copy = include_str!("../override/league_rell.data_champion");
        let at = copy.find("\"passive_ref\": \"league_rell:iron\"").expect("no league_rell:iron passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("p_t", d.p_t), ("p_shred", d.p_shred), ("e_toward", d.e_toward), ("r_r", d.r_r)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        assert!(copy.contains("\"effect_ref\": \"league_rell:mold\""), "the copy does not call league_rell:mold");
        assert!(copy.contains("\"effect_ref\": \"league_rell:shatter\""), "the copy does not call league_rell:shatter");
        assert!(!copy.contains("\"name\": \"league_rell_p_steal\""), "the data's own steal buff is still in the copy");
    }

    #[test]
    fn the_snapshot_rides_in_a_buff_name() {
        let n = snap_name(87, -3);
        assert!(n.len() <= BUFF_NAME_CAP);
        assert_eq!(parse_snap(&n), Some((87, -3)));
        assert_eq!(parse_snap("league_rell_p_shred"), None);
    }

    #[test]
    fn she_steals_a_share_of_each_snapshot_per_stack() {
        assert_eq!(steal_per_stack((100, 40), 3), (3, 2)); // 3% of 100, 3% of 40 = 1 -> the floor 2
        assert_eq!(steal_total(&[(5, (100, 40)), (2, (200, 200))], 3), (15 + 12, 10 + 12));
        assert_eq!(steal_total(&[(9, (100, 100))], 3), (15, 15)); // never past five stacks
        assert_eq!(steal_total(&[], 3), (0, 0));
    }

    #[test]
    fn toward_means_within_45_degrees() {
        assert!(heading_to((0.0, 0.0), (100.0, 0.0), (10_000.0, 500.0)));
        assert!(!heading_to((0.0, 0.0), (100.0, 0.0), (0.0, 10_000.0)));
        assert!(!heading_to((0.0, 0.0), (0.0, 0.0), (10_000.0, 0.0))); // standing still
    }
}
