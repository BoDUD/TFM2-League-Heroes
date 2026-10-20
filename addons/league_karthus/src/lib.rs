//! 卡尔萨斯附加包（用户选「被动做附加包」）：主包数据做不到的死亡契约。
//!
//! `mod.override_info` 把主包的卡尔萨斯换成 `override/` 里的副本（tools/kit/build_karthus.py 的 native=1）：数据和主包
//! 一样，只是被动挂本包的 `league_karthus:death_defied`（参数在英雄数据的 `passive.params` 里），多一个灵体的画面。
//!
//! - **死亡契约**：英雄联盟里卡尔萨斯死后化成灵体，7 秒内照样放技能，然后才倒下。数据读不到血量，主包做不了。
//!   本包一直给他挂着「不死」`league_karthus_p_guard`，致命伤害只会把他打到 1 血；到 1 血（身上没有别人给的不死）时
//!   **化成灵体** `p_t` tick：隐身（敌人选不中他，`entity_set_invisible`）、不再受伤（`damaged_reduce` 100%）、免控，
//!   照常走动、放技能、攻击；身上挂 `league_karthus_p_spirit`（画面）。时间到就倒下，击杀算最后打他的那个人。
//!   每条命都有（英雄联盟每次死亡都会触发）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_karthus.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_karthus";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";

/// 「不死」挂多久、多久续一次（一直挂着，化成灵体前不断）。
pub const GUARD_T: usize = 30;
pub const GUARD_EVERY: usize = 10;
/// 灵体的隐身每隔多久续一次（放技能、攻击可能让隐身断掉）。
pub const HIDE_EVERY: usize = 30;

fn sn(x: &str) -> String {
    format!("league_karthus_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KARTHUS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_karthus.log");
        }
    }
    PathBuf::from("league_karthus.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the game, 2026-10-12)
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

/// 名字是不是本包的「不死」（别的「不死」在身上时不化成灵体）。
pub fn ours(name: &str) -> bool {
    name == sn("p_guard") || name == sn("p_spirit")
}

pub fn other_undying(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(name, undying)| *undying && !ours(name))
}

/// 灵体第 `k` tick（0 起）该不该续隐身。
pub fn hide_due(k: usize) -> bool {
    k % HIDE_EVERY == 0
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub p_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { p_t: 420 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        if k == "p_t" {
            p.p_t = v;
        }
    }
    p
}

// ===================== 被动 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

#[derive(Clone, Default)]
struct DeathDefied {
    p: Params,
    me: usize,
    /// 灵体开始的 tick（不是灵体时 None）。
    spirit: Option<usize>,
    /// 这条命还没化过灵体。
    ready: bool,
    /// 最后一个打他的（倒下时算击杀）。
    last_hit: Option<usize>,
    next_guard: usize,
    /// 这条命里见过他 1 血以上：游戏 0.6.4 开局第 0 tick 读到的血量是 0，那不是致命伤（赛恩附加包的教训）。
    alive_seen: bool,
}

impl DeathDefied {
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

    fn rise(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        self.ready = false;
        self.spirit = Some(now);
        sim.entity_remove_buff(me, &sn("p_guard"));
        let mut s = BuffV1::timed(&sn("p_spirit"), self.p.p_t + 2);
        s.undying = true;
        s.damaged_reduce = 100;
        s.cc_immune = true;
        sim.add_buff(me, &s);
        let hidden = sim.entity_set_invisible(me, self.p.p_t);
        sim.play_sfx(&sn("p"), me, &InputTargetV1::target(me));
        sim.play_sfx(&sn("vo_p"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("spirit") {
            wlog(format!("{} SPIRIT #{k}: lethal damage caught at 1 hp (last hit by {}), a spirit for {} ticks{}",
                         head(sim, me), self.last_hit.map_or_else(|| "-".to_string(), |a| who(sim, a)), self.p.p_t,
                         if hidden { "" } else { " (entity_set_invisible refused)" }));
        }
    }

    fn fall(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.spirit = None;
        sim.entity_remove_buff(me, &sn("p_spirit"));
        let (hp, _) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
        let killer = self.last_hit.filter(|&a| sim.get_entity(a).is_some()).unwrap_or(me);
        sim.deal_damage_typed(killer, me, hp + 1000, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        if let Some(k) = counted("fall") {
            wlog(format!("{} FALL #{k}: the spirit's time is up, killed by {}", head(sim, me), who(sim, killer)));
        }
    }
}

impl StablePassive for DeathDefied {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.ready = true;
        self.spirit = None;
        self.last_hit = None;
        self.next_guard = 0;
        self.alive_seen = false;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Karthus (player {player}, team {team}), {:?}", head(sim, me),
                         self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let (hp, _) = e.hp();
        let now = sim.tick();
        if let Some(t0) = self.spirit {
            let k = now.saturating_sub(t0);
            if k >= self.p.p_t {
                self.fall(sim, me);
            } else if k > 0 && hide_due(k) {
                sim.entity_set_invisible(me, self.p.p_t - k);
            }
            return;
        }
        if !self.ready {
            return;
        }
        if hp > 1 {
            self.alive_seen = true;
        }
        self.guard(sim, me, now);
        if hp <= 1 && self.alive_seen {
            let list: Vec<(String, bool)> = buffs(sim, me).iter().map(|b| (b.name().to_string(), b.undying)).collect();
            if !other_undying(&list) {
                self.rise(sim, me, now);
            }
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, _: usize, attacker: usize, damage: usize) {
        if damage > 0 && attacker != self.me && sim.get_entity(attacker).is_some() && self.spirit.is_none() {
            self.last_hit = Some(attacker);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if self.spirit.is_some() {
            if let Some(k) = counted("spirit_kill") {
                wlog(format!("{} SPIRIT KILL #{k}: {} killed by the spirit", head(sim, me), who(sim, victim)));
            }
        }
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        self.spirit = None;
        self.ready = false;
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Karthus: Death Defied's spirit) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:death_defied"), DeathDefied::default());
    host.log(LogLevel::Info, "league_karthus loaded (Death Defied's spirit).");
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
    fn only_someone_elses_undying_holds_the_spirit_back() {
        let l = |v: &[(&str, bool)]| v.iter().map(|(n, u)| (n.to_string(), *u)).collect::<Vec<_>>();
        assert!(!other_undying(&l(&[("league_karthus_p_guard", true)])));
        assert!(!other_undying(&l(&[("league_karthus_p_spirit", true), ("league_karthus_e_on", false)])));
        assert!(other_undying(&l(&[("league_karthus_p_guard", true), ("league_soraka_w_guard", true)])));
    }

    #[test]
    fn the_veil_is_renewed() {
        assert!(hide_due(30));
        assert!(!hide_due(31));
    }

    #[test]
    fn params_parse() {
        assert_eq!(parse_params(r#"{"p_t":420}"#), Params::default());
        assert_eq!(parse_params(r#"{"p_t":300}"#).p_t, 300);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_karthus.py");
        let src = std::fs::read_to_string(path).expect("build_karthus.py");
        let d = Params::default();
        assert!(src.contains(&format!("\"p_t\": {}", d.p_t)), "p_t is not {} in build_karthus.P", d.p_t);
    }

    #[test]
    fn the_names_fit() {
        for x in ["p_guard", "p_spirit", "p", "vo_p"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }
}
