//! 内瑟斯附加包（用户 2026-10-17：「全按推荐做」，做附加包）。主包保持纯数据；`mod.override_info` 把主包的内瑟斯换成 `override/`
//! 里的副本（`make_override.py` 用 tools/kit/build_nasus.py 的 `native=1` 生成：技能一字不改，被动换成本包的
//! `league_nasus:soul_eater`，大招的 buff 去掉「技能冷却减半」，Q 和大招的说明开头加【附加包】），本包补数据做不到的三件事：
//!
//! - **汲魂痛击的层数死了也不掉**（被动 `soul_eater`，league_veigar_power / league_swain 的做法）：每一次 Q 击杀是他身上一个永久的
//!   `league_nasus_q_stack`（法术强度 +4，击杀英雄 +10；Q 的叠层伤害按法术强度算，他没有别的法术强度）。引擎在他死亡时清掉身上全部
//!   buff，所以主包里层数每条命从零叠起（说明里写着「死后清空」）；被动活着时把每一层原样记下，少了（死亡、复活时引擎清掉）就原样补回，
//!   和英雄联盟一样永久。
//! - **死神降临只让 Q 冷却减半**：数据里的「技能冷却」buff 会同时作用于 Q 和 E；副本的大招 buff 不带它，本包在大招期间每 tick
//!   给 Q 的冷却多减 1 tick（`entity_reduce_cooldown`，Q 冷却快一倍 = 减半），E 照常。旧游戏（ABI 10 以前没有这个接口）退回主包的
//!   做法：大招期间挂一个 2 tick 的「技能冷却 +100」。
//! - **大号形态整身替换**（`view.rs`，游戏 0.6.4 起的 Windows 版）：死神降临期间（主包的 buff `league_nasus_r_on`）站着、走着、挨打都是变大的
//!   他（图里的 `b_*`），形态结束换回原来的大小。
//!
//! 开大的时机不归本包管：主包按场面判断（身边两个敌方英雄，或正在和敌方英雄交战），本包只在日志里记下每次变身时身边几个敌方英雄。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nasus.log`，每次启动游戏重写，上一次的留在 .prev.log：`KEEP`（补回的
//! 层数）、`STACK`（叠到多少层）、`RISE`（变身时身边的敌方英雄）、`QCD`（大招期间 Q 冷却加速）、`FORM`（画面里换形态），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_nasus";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 大号形态（主包数据的 buff）。
pub const FORM: &str = "league_nasus_r_on";
/// 一次 Q 击杀的层数（主包数据：永久，法术强度 +q_s / +q_sc）。
pub const STACK: &str = "league_nasus_q_stack";
/// 旧游戏上的退路：大招期间挂着的「技能冷却 +100」（2 tick，一次只挂一个）。
pub const QCD: &str = "league_nasus_r_qcd";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_NASUS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_nasus.log");
        }
    }
    PathBuf::from("league_nasus.log")
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 击杀一个单位的层数（日志里认层）。
    pub q_s: usize,
    /// 击杀一个英雄的层数。
    pub q_sc: usize,
    /// 沙暴的半径（日志里数变身时身边的敌方英雄）。
    pub r_r: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { q_s: 4, q_sc: 10, r_r: 30000 }
    }
}

/// `{"q_s":4,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "q_s" => p.q_s = v,
            "q_sc" => p.q_sc = v,
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

/// `kept` 里有、`have` 里没有的那些层（按完整的数值配对，league_veigar_power 的 missing）。
pub fn missing(kept: &[BuffV1], have: &[BuffV1]) -> Vec<BuffV1> {
    let mut left: Vec<Option<&BuffV1>> = have.iter().map(Some).collect();
    let mut out = Vec::new();
    for k in kept {
        match left.iter_mut().find(|h| h.is_some_and(|h| h == k)) {
            Some(slot) => *slot = None,
            None => out.push(*k),
        }
    }
    out
}

/// 层数合计（每个 buff 的法术强度之和）。
pub fn total(stacks: &[BuffV1]) -> i64 {
    stacks.iter().map(|b| b.magic_power as i64).sum()
}

/// 大招期间 Q 冷却该多减的 tick：剩余冷却 > 0 时 1（冷却快一倍），否则 0。
pub fn q_extra(remaining: usize) -> usize {
    usize::from(remaining > 0)
}

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

// ===================== 被动：吞噬灵魂（层数留到死后、大招只减 Q、日志） =====================

#[derive(Clone, Default)]
struct SoulEater {
    /// 这一局他叠到的每一层（活着时在身上看到的）。被动在玩家身上、按模拟各有一份，死了不丢。
    kept: Vec<BuffV1>,
    /// 上一 tick 他活着（死了 / 复活的那一刻记一行日志）、身上有大号形态。
    was_alive: bool,
    r_on: bool,
}

impl StablePassive for SoulEater {
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

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let p = shared();
        let Some(e) = sim.get_entity(me) else { return };
        let alive = e.is_alive();
        let (team, at) = (e.team(), (e.pos().0 as i64, e.pos().1 as i64));
        let q_cd = e.cooldown(SkillSlotV1::Skill);
        if alive != self.was_alive {
            wlog(format!("{} {} with {} stacks kept ({} kills)", head(sim, me), if alive { "ALIVE" } else { "DEAD" },
                total(&self.kept), self.kept.len()));
            self.was_alive = alive;
        }
        let all = buffs(sim, me);
        let have: Vec<BuffV1> = all.iter().filter(|b| b.name() == STACK).copied().collect();
        let gone = missing(&self.kept, &have);
        if gone.is_empty() {
            if alive && have.len() > self.kept.len() {
                if let Some(k) = counted("stack") {
                    let champ = have.last().is_some_and(|b| b.magic_power as usize == p.q_sc);
                    wlog(format!("{} STACK {} stacks ({} kills, the last a {}) #{k}", head(sim, me), total(&have), have.len(),
                        if champ { "champion" } else { "unit" }));
                }
                self.kept = have;
            }
        } else {
            for b in &gone {
                sim.add_buff(me, b);
            }
            if let Some(k) = counted("keep") {
                wlog(format!("{} KEEP {} kills put back ({}), {} stacks in all #{k}", head(sim, me), gone.len(),
                    if alive { "alive" } else { "dead" }, total(&self.kept)));
            }
        }
        // Fury of the Sands (the data's own moment): who is round him; while it lasts Q cools twice as fast
        let r_on = alive && all.iter().any(|b| b.name() == FORM);
        if r_on && !self.r_on {
            let d = |u: (i64, i64)| (((u.0 - at.0) as f64).powi(2) + ((u.1 - at.1) as f64).powi(2)).sqrt();
            let n = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).filter(|u| {
                u.team() != team && u.is_alive() && u.is_champion() && d((u.pos().0 as i64, u.pos().1 as i64)) <= p.r_r as f64
            }).count();
            if let Some(k) = counted("rise") {
                wlog(format!("{} RISE Fury of the Sands with {n} enemy champion{} within {} #{k}", head(sim, me),
                    if n == 1 { "" } else { "s" }, p.r_r));
            }
        }
        if r_on {
            let remaining = q_cd.map_or(0, |c| c.remaining);
            let extra = q_extra(remaining);
            let done = extra > 0 && sim.entity_reduce_cooldown(me, SkillSlotV1::Skill, extra);
            if extra > 0 && !done && q_cd.is_none() && !all.iter().any(|b| b.name() == QCD) {
                // an older host: no per-slot cooldown - the main pack's way (Q and E alike), one instance at a time
                let mut b = BuffV1::timed(QCD, 2);
                b.skill_cooldown_mult = 100;
                sim.add_buff(me, &b);
            }
            if done {
                if let Some(k) = counted("qcd") {
                    wlog(format!("{} QCD Q cools 2 ticks a tick ({remaining} left) #{k}", head(sim, me)));
                }
            }
        }
        self.r_on = r_on;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Nasus: Siphoning Strike stacks kept through death, Fury of the Sands halving Q only, the whole big body) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:soul_eater"), SoulEater::default());
    host.log(LogLevel::Info, "league_nasus loaded (Siphoning Strike stacks kept through death, Fury of the Sands halving Q only, the whole big body).");
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

    fn stack(k: i32) -> BuffV1 {
        let mut b = BuffV1::named(STACK);
        b.magic_power = k;
        b
    }

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"q_s":3,"junk":7,"q_sc":12,"r_r":25000}"#);
        assert_eq!((p.q_s, p.q_sc, p.r_r), (3, 12, 25000));
    }

    #[test]
    fn the_copy_carries_the_default_params_and_no_shared_cooldown_cut() {
        let copy = include_str!("../override/league_nasus.data_champion");
        let at = copy.find("\"passive_ref\": \"league_nasus:soul_eater\"").expect("no league_nasus:soul_eater passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("q_s", d.q_s), ("q_sc", d.q_sc), ("r_r", d.r_r)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        assert!(copy.contains(&format!("\"name\": \"{STACK}\"")), "the copy has no stack buff");
        assert!(copy.contains(&format!("\"name\": \"{FORM}\"")), "the copy has no form buff");
        assert!(!copy.contains("skill_cooldown_mult"), "the copy's R still halves E too");
    }

    #[test]
    fn a_death_puts_every_stack_back() {
        let kept = vec![stack(4), stack(4), stack(10), stack(4)];
        assert!(missing(&kept, &kept).is_empty());
        let back = missing(&kept, &[]);
        assert_eq!(back.len(), 4);
        assert_eq!(total(&back), 22);
        assert_eq!(missing(&kept, &[stack(4), stack(10)]).len(), 2);
        assert_eq!(total(&missing(&kept, &[stack(4), stack(4), stack(4)])), 10);
    }

    #[test]
    fn q_cools_twice_as_fast_only_while_cooling() {
        assert_eq!(q_extra(0), 0);
        assert_eq!(q_extra(1), 1);
        assert_eq!(q_extra(240), 1);
    }
}
