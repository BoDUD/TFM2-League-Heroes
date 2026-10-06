//! 卡兹克附加包：被动「无形威胁」真的看敌方视野，进化直接读等级（用户：「数据读不到就用rust 改写源码」）。
//!
//! 主包保持纯数据：数据读不到视野，主包的无形威胁在 R 隐身、复活和约 4 秒没出手后就绪；数据也读不到等级，进化靠一套
//! 「法强探测」（每级 +1 法强，自伤打护盾）在 5/8/11 级后一两秒内认出等级。`mod.override_info` 把主包的卡兹克换成
//! `override/` 里的副本（`make_override.py` 用 tools/kit/build_khazix.py 的 `native=1` 生成：去掉探测和「没出手就绪」，
//! `passive` 换成本包的 `league_khazix:void`），被动每 tick 看：
//!
//! - **无形威胁**：他活着、敌方队伍看不见他（`is_visible`，草丛、战争迷雾、R 的隐身都算）、身上还没有 `league_khazix_ut`
//!   时加上它（永久，下一次攻击英雄时由数据打出伤害和减速并去掉）。
//! - **进化**：等级到 `lv_q` / `lv_e` / `lv_r` 而身上没有对应的 `league_khazix_s1` / `s2` / `s3` 时加上（s1 带
//!   `q_evo_range` 攻击距离），播放进化的画面和声音；复活后第一次补回已有的进化时不播（主包也是静默重读）。
//!
//! 孤立无援仍用主包的数据判定（目标身边数人头，已经是英雄联盟的意思）。数字从英雄数据的 `passive.params` 来。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_khazix.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_khazix";
const HERO: &str = "league_khazix";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KHAZIX_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_khazix.log");
        }
    }
    PathBuf::from("league_khazix.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
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

fn n(x: &str) -> String {
    format!("{HERO}_{x}")
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub lv_q: usize,
    pub lv_e: usize,
    pub lv_r: usize,
    /// 进化收割利爪给的攻击距离。
    pub q_evo_range: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { lv_q: 5, lv_e: 8, lv_r: 11, q_evo_range: 6000 }
    }
}

/// `{"lv_e":8,"lv_q":5,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "lv_q" => p.lv_q = v,
            "lv_e" => p.lv_e = v,
            "lv_r" => p.lv_r = v,
            "q_evo_range" => p.q_evo_range = v,
            _ => {}
        }
    }
    p
}

// ===================== 判断 =====================

/// 这个等级该有的进化：(`s1`, `s2`, `s3`)。
pub fn stages(p: &Params, level: usize) -> [bool; 3] {
    [level >= p.lv_q, level >= p.lv_e, level >= p.lv_r]
}

/// 无形威胁该不该就绪：活着、敌方看不见、还没就绪。
pub fn unseen_ready(alive: bool, seen: bool, has_ut: bool) -> bool {
    alive && !seen && !has_ut
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Void {
    p: Params,
    /// 这条命还没跑过 on_update：补回进化时不播画面和声音。
    fresh: bool,
}

impl StablePassive for Void {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.fresh = true;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, team, level) = (e.is_alive(), e.team(), e.level());
        if !alive {
            self.fresh = true;
            return;
        }
        let quiet = std::mem::take(&mut self.fresh);
        let on_me = InputTargetV1::target(me);
        let names = [n("s1"), n("s2"), n("s3")];
        let voices = ["vo_evo_q", "vo_evo_e", "vo_evo_r"];
        for (k, want) in stages(&self.p, level).into_iter().enumerate() {
            if !want || has_buff(sim, me, &names[k]) {
                continue;
            }
            let mut b = BuffV1::named(&names[k]);
            if k == 0 {
                b.range = self.p.q_evo_range;
            }
            sim.add_buff(me, &b);
            if !quiet {
                sim.play_view_effect(&n("evo"), me, &on_me, 0, 0, 0);
                sim.play_sfx(&n("evo"), me, &on_me);
                sim.play_sfx(&n(voices[k]), me, &on_me);
            }
            wlog(format!("{} EVOLVE {} at level {level}{}", head(sim, me), names[k], if quiet { " (silent, after respawn)" } else { "" }));
        }
        let seen = sim.is_visible(1 - team.min(1), me);
        let ut = n("ut");
        if unseen_ready(alive, seen, has_buff(sim, me, &ut)) {
            sim.add_buff(me, &BuffV1::named(&ut));
            sim.play_view_effect(&n("p_ready"), me, &on_me, 0, 0, 0);
            sim.play_sfx(&n("p_ready"), me, &on_me);
            wlog(format!("{} UNSEEN: Unseen Threat ready", head(sim, me)));
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Kha'Zix: Unseen Threat from real vision, evolutions from his level) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:void"), Void::default());
    host.log(LogLevel::Info, "league_khazix v1 loaded (Kha'Zix: Unseen Threat from vision, evolutions from level).");
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
    fn params_from_the_main_pack() {
        let p = parse_params(r#"{"lv_e":8,"lv_q":5,"lv_r":11,"q_evo_range":6000}"#);
        assert_eq!(p, Params::default());
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"lv_q":4,"junk":7}"#).lv_q, 4);
    }

    #[test]
    fn evolutions_by_level() {
        let p = Params::default();
        assert_eq!(stages(&p, 1), [false, false, false]);
        assert_eq!(stages(&p, 5), [true, false, false]);
        assert_eq!(stages(&p, 8), [true, true, false]);
        assert_eq!(stages(&p, 12), [true, true, true]);
    }

    #[test]
    fn unseen_threat_only_when_hidden() {
        assert!(unseen_ready(true, false, false));
        assert!(!unseen_ready(true, true, false));
        assert!(!unseen_ready(true, false, true));
        assert!(!unseen_ready(false, false, false));
    }
}
