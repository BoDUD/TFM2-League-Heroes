//! 斯维因附加包（用户 2026-10-17：「全按推荐」，做附加包）。主包保持纯数据；`mod.override_info` 把主包的斯维因换成 `override/`
//! 里的副本（`make_override.py` 用 tools/kit/build_swain.py 的 `native=1` 生成：技能一字不改，被动换成本包的
//! `league_swain:flock`，普攻和大招的说明开头加【附加包】），本包补数据做不到的两件事：
//!
//! - **魂屑死了也不掉**（被动 `flock`，league_veigar_power 的做法）：每块魂屑是他身上一个永久的 `league_swain_frag`（最大生命
//!   +p_hp）。引擎在他死亡时清掉身上全部 buff，所以主包里魂屑每条命从零攒起（说明里写着「死后清空」）；被动活着时把每块原样记下，
//!   少了（死亡、复活时引擎清掉）就原样补回，和英雄联盟一样永久。
//! - **恶魔形态整身替换**（`view.rs`，游戏 0.6.4 起的 Windows 版）：恶魔升华期间（主包的 buff `league_swain_r_on`）站着、走着、挨打都是化身
//!   恶魔的他（图里的 `b_*`），形态结束换回斯维因。
//!
//! 开大的时机不归本包管（用户：「是乌鸦看情况开大吧」）：主包按场面判断（身边两个敌方英雄，或队友在围攻被控住的敌方英雄），本包只在
//! 日志里记下每次变身时身边几个敌方英雄。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_swain.log`，每次启动游戏重写，上一次的留在 .prev.log：`KEEP`（补回的
//! 魂屑）、`FRAG`（攒到第几块）、`RISE`（变身时身边的敌方英雄）、`FORM`（画面里换形态），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_swain";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 恶魔形态（主包数据的 buff）。
pub const FORM: &str = "league_swain_r_on";
/// 一块魂屑（主包数据：永久，最大生命 +p_hp）。
pub const FRAG: &str = "league_swain_frag";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SWAIN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_swain.log");
        }
    }
    PathBuf::from("league_swain.log")
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
    /// 一块魂屑的最大生命（日志里算总数）。
    pub p_hp: usize,
    /// 恶魔吸取的半径（日志里数变身时身边的敌方英雄）。
    pub r_r: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_hp: 15, r_r: 60000 }
    }
}

/// `{"p_hp":15,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "p_hp" => p.p_hp = v,
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

/// `kept` 里有、`have` 里没有的那些魂屑（按完整的数值配对，league_veigar_power 的 missing）。
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

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

// ===================== 被动：狂食鸦群（魂屑留到死后、日志） =====================

#[derive(Clone, Default)]
struct Flock {
    /// 这一局他攒到的每一块魂屑（活着时在身上看到的）。被动在玩家身上、按模拟各有一份，死了不丢。
    kept: Vec<BuffV1>,
    /// 上一 tick 他活着（死了 / 复活的那一刻记一行日志）、身上有恶魔形态。
    was_alive: bool,
    r_on: bool,
}

impl StablePassive for Flock {
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
        if alive != self.was_alive {
            wlog(format!("{} {} with {} fragments kept (+{} max health)", head(sim, me), if alive { "ALIVE" } else { "DEAD" },
                self.kept.len(), self.kept.len() * p.p_hp));
            self.was_alive = alive;
        }
        let all = buffs(sim, me);
        let have: Vec<BuffV1> = all.iter().filter(|b| b.name() == FRAG).copied().collect();
        let gone = missing(&self.kept, &have);
        if gone.is_empty() {
            if alive && have.len() > self.kept.len() {
                if let Some(k) = counted("frag") {
                    wlog(format!("{} FRAG {} fragment{} (+{} max health) #{k}", head(sim, me), have.len(),
                        if have.len() == 1 { "" } else { "s" }, have.len() * p.p_hp));
                }
                self.kept = have;
            }
        } else {
            for b in &gone {
                sim.add_buff(me, b);
            }
            if let Some(k) = counted("keep") {
                wlog(format!("{} KEEP {} fragments put back ({}), {} in all #{k}", head(sim, me), gone.len(),
                    if alive { "alive" } else { "dead" }, self.kept.len()));
            }
        }
        // the demon rising (the data's own moment): who is round him
        let r_on = alive && all.iter().any(|b| b.name() == FORM);
        if r_on && !self.r_on {
            let d = |u: (i64, i64)| (((u.0 - at.0) as f64).powi(2) + ((u.1 - at.1) as f64).powi(2)).sqrt();
            let n = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).filter(|u| {
                u.team() != team && u.is_alive() && u.is_champion() && d((u.pos().0 as i64, u.pos().1 as i64)) <= p.r_r as f64
            }).count();
            if let Some(k) = counted("rise") {
                wlog(format!("{} RISE Demonic Ascension with {n} enemy champion{} within {} #{k}", head(sim, me),
                    if n == 1 { "" } else { "s" }, p.r_r));
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
        "=== {ID} v{VERSION} (Swain: Soul Fragments kept through death, the whole body as the demon) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:flock"), Flock::default());
    host.log(LogLevel::Info, "league_swain loaded (Soul Fragments kept through death, the whole body as the demon).");
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

    fn frag() -> BuffV1 {
        let mut b = BuffV1::named(FRAG);
        b.hp = 15;
        b
    }

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"p_hp":20,"junk":7,"r_r":50000,"r_range":55000}"#);
        assert_eq!((p.p_hp, p.r_r), (20, 50000));
    }

    #[test]
    fn the_copy_carries_the_default_params() {
        let copy = include_str!("../override/league_swain.data_champion");
        let at = copy.find("\"passive_ref\": \"league_swain:flock\"").expect("no league_swain:flock passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("p_hp", d.p_hp), ("r_r", d.r_r)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        assert!(copy.contains(&format!("\"name\": \"{FRAG}\"")), "the copy has no fragment buff");
        assert!(copy.contains(&format!("\"name\": \"{FORM}\"")), "the copy has no demon form buff");
    }

    #[test]
    fn a_death_puts_every_fragment_back() {
        let kept = vec![frag(); 12];
        assert!(missing(&kept, &vec![frag(); 12]).is_empty());
        assert!(missing(&kept, &vec![frag(); 14]).is_empty());
        let back = missing(&kept, &[]);
        assert_eq!(back.len(), 12);
        assert!(back.iter().all(|b| b.name() == FRAG && b.hp == 15));
        assert_eq!(missing(&kept, &vec![frag(); 9]).len(), 3);
    }
}
