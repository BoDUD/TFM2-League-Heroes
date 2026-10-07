//! 雷克顿附加包：被动「怒之领域」低于一半生命时怒气获取 +50%（英雄联盟的规则）。
//!
//! 主包保持纯数据：数据读不到当前生命，主包的怒气是雷克顿身上的一条阶梯（`league_renekton_f1`..`f5`，同一时刻只有
//! 一层，每次积攒往上走一阶并重新计时 `f_t` tick，到时间全部清掉），满 5 阶时下一个技能被强化并耗尽怒气。
//! `mod.override_info` 把主包的雷克顿换成 `override/` 里的副本：技能一字不改，只加了本包的被动
//! `league_renekton:anger`，它每 tick 看一次：
//!
//! - 阶梯往上走了几阶（这就是这一刻积攒的次数；满阶时的积攒只刷新时间，不算）；
//! - 生命低于 `low`%（默认 50）时，这些积攒记进计数，每满 `every`（默认 2）次就**再往上走一阶**（同主包：去掉当前那阶、
//!   加上高一阶，`f_t` tick）——两次积攒变三次，就是 +50%；
//! - 生命回到 `low`% 以上、怒气被耗尽或清空时，计数归零。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从 tools/kit/build_renekton.py 的参数表 P 写进去）。
//! 计数记在每个雷克顿自己的被动实例里；不用全局变量，服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_renekton.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_renekton";

/// 主包雷克顿的名字（buff 都以它开头）。
fn rk(x: &str) -> String {
    format!("league_renekton_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_RENEKTON_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_renekton.log");
        }
    }
    PathBuf::from("league_renekton.log")
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
    /// 怒气阶梯的阶数、每阶的计时（同主包）。
    pub f_n: usize,
    pub f_t: usize,
    /// 生命低于 `low`% 时，每积攒 `every` 次多走一阶。
    pub low: usize,
    pub every: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { f_n: 5, f_t: 480, low: 50, every: 2 }
    }
}

/// `{"f_n":5,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "f_n" => &mut p.f_n,
            "f_t" => &mut p.f_t,
            "low" => &mut p.low,
            "every" => &mut p.every,
            _ => continue,
        };
        *slot = v;
    }
    p.every = p.every.max(1);
    p
}

// ===================== 判断 =====================

/// 身上的怒气：阶梯上现在是第几阶（0 = 没有）。
pub fn rung_of(names: &[String], f_n: usize) -> usize {
    (1..=f_n).rev().find(|k| names.iter().any(|b| *b == rk(&format!("f{k}")))).unwrap_or(0)
}

/// 一个 tick 的结算：上一 tick 的阶数 `was`、现在的阶数 `now`、生命比例 `hp`（%）、已经攒下的低血积攒 `bank`。
/// 返回（新的 bank，要不要多走一阶）。
pub fn step(p: &Params, was: usize, now: usize, hp: f64, bank: usize) -> (usize, bool) {
    if now == 0 || now < was || hp >= p.low as f64 {
        return (0, false); // 耗尽、清空，或生命回到一半以上：重新数
    }
    let gained = now - was;
    if gained == 0 {
        return (bank, false);
    }
    let bank = bank + gained;
    if bank >= p.every && now < p.f_n {
        (bank - p.every, true)
    } else {
        (bank.min(p.every), false)
    }
}

// ===================== 小工具 =====================

fn buff_names(sim: &StableSim<'_>, id: usize) -> Vec<String> {
    sim.get_entity(id)
        .map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect())
}

/// 阶梯往上走一阶：同主包的 `climb`（去掉当前那阶，加上高一阶，`f_t` tick）。
fn climb(sim: &mut StableSim<'_>, me: usize, from: usize, p: &Params) {
    let to = (from + 1).min(p.f_n);
    if from > 0 {
        sim.entity_remove_buff(me, &rk(&format!("f{from}")));
    }
    let mut b = BuffV1::timed(&rk(&format!("f{to}")), p.f_t);
    b.duration_kind = BuffDurationV1::Time.code();
    sim.add_buff(me, &b);
}

// ===================== 被动 =====================

/// 每个雷克顿一份：参数、上一 tick 的阶数、低血时攒下的积攒次数、诊断计数。
#[derive(Clone, Default)]
struct Anger {
    p: Params,
    was: usize,
    bank: usize,
    gains: usize,
    extra: usize,
    next_report: usize,
}

impl StablePassive for Anger {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.was = 0;
        self.bank = 0;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Renekton (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.was = 0;
            self.bank = 0;
            return;
        }
        let (now_hp, max_hp) = e.hp();
        let hp = if max_hp > 0 { now_hp as f64 * 100.0 / max_hp as f64 } else { 100.0 };
        let now = rung_of(&buff_names(sim, me), self.p.f_n);
        if now > self.was {
            self.gains += now - self.was;
        }
        let (bank, more) = step(&self.p, self.was, now, hp, self.bank);
        self.bank = bank;
        self.was = now;
        if more {
            climb(sim, me, now, &self.p);
            self.was = now + 1;
            self.extra += 1;
            if self.extra <= 8 || self.extra % 50 == 0 {
                wlog(format!("{} ANGER #{}: hp {hp:.0}%, Fury {now} -> {}", head(sim, me), self.extra, now + 1));
            }
        }
        let tick = sim.tick();
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 {
                wlog(format!("{} WATCH: Fury {now}, hp {hp:.0}%, gains {} extra {}", head(sim, me), self.gains, self.extra));
            }
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Reign of Anger: +50% Fury below half health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:anger"), Anger::default());
    host.log(LogLevel::Info, "league_renekton v1 loaded (Renekton's Fury +50% below half health).");
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
        let p = parse_params(r#"{"every":3,"f_n":5,"f_t":400,"low":40,"unknown":4}"#);
        assert_eq!(p, Params { f_n: 5, f_t: 400, low: 40, every: 3 });
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"every":0}"#).every, 1);
    }

    #[test]
    fn every_second_gain_below_half_brings_one_more() {
        let p = Params::default();
        // above half health: nothing
        assert_eq!(step(&p, 1, 2, 80.0, 0), (0, false));
        // below: the first gain is banked, the second brings one more rung
        assert_eq!(step(&p, 1, 2, 40.0, 0), (1, false));
        assert_eq!(step(&p, 2, 3, 40.0, 1), (0, true));
        // two rungs at once (R's cast) below half: one more at once
        assert_eq!(step(&p, 0, 2, 30.0, 0), (0, true));
        // no gain this tick: the bank waits
        assert_eq!(step(&p, 3, 3, 30.0, 1), (1, false));
    }

    #[test]
    fn spent_lost_or_healed_starts_over() {
        let p = Params::default();
        assert_eq!(step(&p, 5, 0, 30.0, 1), (0, false)); // a skill spent it
        assert_eq!(step(&p, 3, 0, 30.0, 1), (0, false)); // the hold lapsed
        assert_eq!(step(&p, 2, 3, 55.0, 1), (0, false)); // healed above half
    }

    #[test]
    fn never_past_the_top_rung() {
        let p = Params::default();
        assert_eq!(step(&p, 4, 5, 20.0, 1), (2, false));
        assert_eq!(step(&p, 5, 5, 20.0, 2), (2, false));
    }

    #[test]
    fn the_rung_is_the_highest_flag() {
        let names: Vec<String> = ["league_renekton_f3", "league_renekton_q_cd", "dagger"].iter().map(|s| s.to_string()).collect();
        assert_eq!(rung_of(&names, 5), 3);
        assert_eq!(rung_of(&[], 5), 0);
        assert!(rk("f5").len() <= BUFF_NAME_CAP);
    }
}
