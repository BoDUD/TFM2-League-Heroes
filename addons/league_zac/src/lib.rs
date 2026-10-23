//! 扎克扩展包（用户选：「粘液回血 + 扩展包复活」）：主包数据做不到的细胞分裂复活。
//!
//! `mod.override_info` 把主包的扎克换成 `override/` 里的副本（tools/kit/build_zac.py 的 native=1）：数据和主包一样，只是
//! 被动挂本包的 `league_zac:split`，普攻第一次挂上一个每 2 tick 看一次的监视（一命一次），按本包给的标记播化开、一滩、重新聚起。
//!
//! - **细胞分裂**：每 `split_cd` tick 一次（阵亡不重置），受到致命伤害时不倒下（本包一直挂着「不死」`league_zac_p_guard`，
//!   生命停在 1 就触发），化成一滩 `split_t` tick：生命设成最大生命的 `split_hp`%（英雄联盟：四块小黏液，存活的越多复活时
//!   生命越多），定身、禁普攻、禁技能；主包数据看到 `league_zac_split_go` 播化开、挂双抗降低的 `league_zac_split_on`、每 30 tick
//!   续一次一滩的动作。这一滩被打掉就是他阵亡（击杀算打掉它的人）；撑过 `split_t` tick 就挂 `league_zac_split_end`，数据播
//!   重新聚起，他带着这一滩剩下的生命继续打。别人给的「不死」在身上时不触发。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zac.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[cfg(windows)]
pub mod view;

/// 主包数据的一滩 buff（双抗降低，一滩在就有）：显示钩子按它把 idle / hit 换成一滩。
pub const FORM: &str = "league_zac_split_on";

const ID: &str = "league_zac";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";

/// 「不死」挂多久、多久续一次。
pub const GUARD_T: usize = 30;
pub const GUARD_EVERY: usize = 10;
/// 主包数据读标记的余量：数据的监视每 2 tick 看一次。
pub const FLAG_T: usize = 6;

fn sn(x: &str) -> String {
    format!("league_zac_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ZAC_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_zac.log");
        }
    }
    PathBuf::from("league_zac.log")
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub split_t: usize,
    pub split_cd: usize,
    pub split_hp: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { split_t: 360, split_cd: 18000, split_hp: 40 }
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
            "split_t" => p.split_t = v,
            "split_cd" => p.split_cd = v,
            "split_hp" => p.split_hp = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 一滩的生命：最大生命的 `split_hp`%，至少 1。
pub fn puddle_hp(max: usize, p: &Params) -> usize {
    (max * p.split_hp / 100).max(1)
}

/// 名字是不是本包的「不死」（别的「不死」在身上时不触发）。
pub fn ours(name: &str) -> bool {
    name == sn("p_guard")
}

pub fn other_undying(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(name, undying)| *undying && !ours(name))
}

// ===================== 被动 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

#[derive(Clone, Default)]
struct Split {
    p: Params,
    me: usize,
    /// 下一次能分裂的 tick（跨命保留）。
    ready_at: usize,
    /// 化成一滩的 tick（不在一滩里时 None）。
    split: Option<usize>,
    next_guard: usize,
    /// 这条命里见过他 1 血以上（0.6.4 开局第 0 tick 读到的血量是 0，那不是致命伤）。
    alive_seen: bool,
}

impl Split {
    fn guard(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        if now < self.next_guard {
            return;
        }
        let mut g = BuffV1::timed(&sn("p_guard"), GUARD_T);
        g.undying = true;
        sim.entity_remove_buff(me, &sn("p_guard"));
        sim.add_buff(me, &g);
        self.next_guard = now + GUARD_EVERY;
    }

    fn melt(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        let hp = puddle_hp(max, &self.p);
        self.split = Some(now);
        self.ready_at = now + self.p.split_cd;
        sim.entity_remove_buff(me, &sn("p_guard"));
        sim.entity_set_hp(me, hp);
        sim.add_buff(me, &BuffV1::timed(&sn("split_go"), FLAG_T));
        let t = self.p.split_t as u64;
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::Bind, t));
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::BlockSkill, t));
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::BlockAttack, t));
        if let Some(k) = counted("split") {
            wlog(format!("{} SPLIT #{k}: lethal damage caught at 1 hp, the puddle holds {hp} / {max} hp for {} ticks",
                         head(sim, me), self.p.split_t));
        }
    }

    fn reform(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.split = None;
        sim.add_buff(me, &BuffV1::timed(&sn("split_end"), FLAG_T));
        if let Some(k) = counted("reform") {
            let (hp, max) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
            wlog(format!("{} REFORM #{k}: whole again with the puddle's {hp} / {max} hp", head(sim, me)));
        }
    }
}

impl StablePassive for Split {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.split = None;
        self.next_guard = 0;
        self.alive_seen = false;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Zac (player {player}, team {team}), {:?}, split ready at t={}",
                         head(sim, me), self.p, self.ready_at));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        let (hp, _) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
        if let Some(t0) = self.split {
            if now >= t0 + self.p.split_t {
                self.reform(sim, me);
            }
            return;
        }
        if hp > 1 {
            self.alive_seen = true;
        }
        if now < self.ready_at {
            return;
        }
        self.guard(sim, me, now);
        if hp <= 1 && self.alive_seen {
            let list: Vec<(String, bool)> = buffs(sim, me).iter().map(|b| (b.name().to_string(), b.undying)).collect();
            if !other_undying(&list) {
                self.melt(sim, me, now);
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        if self.split.take().is_some() {
            if let Some(k) = counted("destroyed") {
                wlog(format!("{} DESTROYED #{k}: the puddle was destroyed - he is dead", head(sim, self.me)));
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
        "=== {ID} v{VERSION} (Zac: Cell Division's revive) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:split"), Split::default());
    #[cfg(windows)]
    view::install_once();
    host.log(LogLevel::Info, "league_zac loaded (Cell Division's revive).");
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
    fn params_from_the_kit() {
        let q = parse_params(r#"{"split_cd":18000,"split_hp":40,"split_t":360}"#);
        assert_eq!(q, Params::default());
        let q = parse_params(r#"{"split_t":300}"#);
        assert_eq!(q.split_t, 300);
        assert_eq!(q.split_cd, 18000);
    }

    #[test]
    fn the_puddle_holds_its_share_of_his_health() {
        let p = Params::default();
        assert_eq!(puddle_hp(2400, &p), 960);
        assert_eq!(puddle_hp(1, &p), 1);
        assert_eq!(puddle_hp(0, &p), 1);
    }

    #[test]
    fn only_someone_elses_undying_holds_the_split_back() {
        assert!(!other_undying(&[("league_zac_p_guard".to_string(), true)]));
        assert!(other_undying(&[("league_zilean_r_rune".to_string(), true)]));
        assert!(!other_undying(&[("league_zilean_r_rune".to_string(), false)]));
    }
}
