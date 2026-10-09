//! 奥拉夫附加包：被动「狂战之怒」按真实的已损失生命给攻速和吸血（英雄联盟的做法）。
//!
//! 主包保持纯数据：数据读不到生命，主包里奥拉夫的狂战之怒是「挨打计数」——普攻时发现 1 点护盾被打破就升一层
//! （`league_olaf_p_1`..`p_n`，每层攻速 `p_as`%，最高 `p_vn` 层另有吸血 `p_vamp`%），离开战斗每 `p_step` tick 掉一层。
//! `mod.override_info` 把主包的奥拉夫换成 `override/` 里的副本（tools/kit/build_olaf.py 的 native=1）：挨打计数去掉，
//! `passive` 换成本包的 `league_olaf_rage:rage`：
//!
//! - 每 tick 读他的生命：已损失 `n_lo`% 起一层，之后每多损失 `n_band`% 再多一层（最多 `p_n` 层）；层数一变就把
//!   `p_1`..`p_n` 换成新的层数（同样的名字、同样的数值，主包的满层画面照常显示）。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。不用全局变量，服务端预模拟和
//! 你看的那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_olaf_rage.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_olaf_rage";

/// 主包奥拉夫的名字（buff 都以它开头）。
fn ol(x: &str) -> String {
    format!("league_olaf_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_OLAF_RAGE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_olaf_rage.log");
        }
    }
    PathBuf::from("league_olaf_rage.log")
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 层数上限。
    pub p_n: usize,
    /// 每层攻速 %。
    pub p_as: usize,
    /// 最高 `p_vn` 层每层吸血 %。
    pub p_vamp: usize,
    pub p_vn: usize,
    /// 已损失生命 `n_lo`% 起一层，之后每 `n_band`% 一层。
    pub n_lo: usize,
    pub n_band: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_n: 4, p_as: 12, p_vamp: 6, p_vn: 2, n_lo: 15, n_band: 17 }
    }
}

/// `{"p_n":4,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "p_n" => &mut p.p_n,
            "p_as" => &mut p.p_as,
            "p_vamp" => &mut p.p_vamp,
            "p_vn" => &mut p.p_vn,
            "n_lo" => &mut p.n_lo,
            "n_band" => &mut p.n_band,
            _ => continue,
        };
        *slot = v;
    }
    p
}

// ===================== 计算 =====================

/// 生命 hp / max 时的层数：已损失 n_lo% 起一层，每多 n_band% 一层，最多 p_n。
pub fn level(p: &Params, hp: usize, max: usize) -> usize {
    if max == 0 {
        return 0;
    }
    let missing = 100usize.saturating_sub(hp * 100 / max);
    if missing < p.n_lo {
        return 0;
    }
    (1 + (missing - p.n_lo) / p.n_band.max(1)).min(p.p_n)
}

/// 第 k 层（1 起）的 buff：攻速，最高 p_vn 层另有吸血（和主包 rage_to 一样）。
pub fn level_buff(p: &Params, k: usize) -> BuffV1 {
    let mut b = BuffV1::named(&ol(&format!("p_{k}")));
    b.attack_speed_mult = p.p_as as i32;
    if k + p.p_vn > p.p_n {
        b.vamp = p.p_vamp as i32;
    }
    b
}

// ===================== 被动 =====================

/// 每个奥拉夫一份：参数、现在挂着几层。
#[derive(Clone, Default)]
struct Rage {
    p: Params,
    now: usize,
    changes: usize,
}

impl Rage {
    fn set(&mut self, sim: &mut StableSim<'_>, me: usize, want: usize) {
        for k in 1..=self.p.p_n {
            sim.entity_remove_buff(me, &ol(&format!("p_{k}")));
        }
        for k in 1..=want {
            sim.add_buff(me, &level_buff(&self.p, k));
        }
        self.changes += 1;
        if self.changes <= 40 || self.changes % 100 == 0 {
            let (hp, max) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
            wlog(format!("{} RAGE {} -> {want}: hp {hp}/{max} ({}%)", head(sim, me), self.now, hp * 100 / max.max(1)));
        }
        self.now = want;
    }
}

impl StablePassive for Rage {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.now = 0;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Olaf (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let (hp, max) = e.hp();
        let want = level(&self.p, hp, max);
        if want != self.now {
            self.set(sim, me, want);
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        // death clears the buffs; the next life starts at full health
        self.now = 0;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Berserker Rage from missing health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:rage"), Rage::default());
    host.log(LogLevel::Info, "league_olaf_rage v1 loaded (Olaf's Berserker Rage reads his health).");
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
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"p_as":16,"n_lo":10,"x":1}"#), Params { p_as: 16, n_lo: 10, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn levels_follow_the_missing_health() {
        let p = Params::default();
        assert_eq!(level(&p, 1000, 1000), 0);
        assert_eq!(level(&p, 860, 1000), 0);
        assert_eq!(level(&p, 850, 1000), 1);
        assert_eq!(level(&p, 680, 1000), 2);
        assert_eq!(level(&p, 510, 1000), 3);
        assert_eq!(level(&p, 340, 1000), 4);
        assert_eq!(level(&p, 10, 1000), 4);
        assert_eq!(level(&p, 0, 0), 0);
    }

    #[test]
    fn the_top_levels_steal_life() {
        let p = Params::default();
        assert_eq!(level_buff(&p, 1).vamp, 0);
        assert_eq!(level_buff(&p, 2).vamp, 0);
        assert_eq!(level_buff(&p, 3).vamp, 6);
        assert_eq!(level_buff(&p, 4).vamp, 6);
        assert_eq!(level_buff(&p, 4).attack_speed_mult, 12);
        assert_eq!(level_buff(&p, 4).name(), "league_olaf_p_4");
    }
}
