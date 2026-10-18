//! 悟空附加包（用户 2026-10-18：「技能方案按 A 做（带扩展包 league_wukong）」）。主包保持纯数据；`mod.override_info` 把主包的
//! 悟空换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_wukong.py 的 `native=1` 生成：技能一字不改，被动换成本包的
//! `league_wukong:stone`，金刚不坏的五层不再带数据里的固定回血），本包补数据做不到的一件事：
//!
//! - **按最大生命回血**（英雄联盟的金刚不坏）：数据读不到生命，主包每层每秒回固定值；本包每 `every` tick 按他身上金刚不坏的层数
//!   （主包的 `league_wukong_s_1` ~ `s_5`）回复最大生命：每 5 秒 `pct`/100 %（英雄联盟 0.35%）×（1 + 层数），叠满 5 层是 2.1%。
//!   零头攒着下次一起回，不会因为取整丢掉。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_wukong.log`，每次启动游戏重写，上一次的留在 .prev.log：`REGEN`
//! （回了多少、几层），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_wukong";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 金刚不坏的层（主包数据：打中英雄时叠，最多 5 层，每层一个名字）。
pub const STACKS: [&str; 5] =
    ["league_wukong_s_1", "league_wukong_s_2", "league_wukong_s_3", "league_wukong_s_4", "league_wukong_s_5"];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_WUKONG_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_wukong.log");
        }
    }
    PathBuf::from("league_wukong.log")
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
const LOG_EVERY: usize = 200;

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
    /// 每 5 秒回复最大生命的万分比，每有一层再加一份（英雄联盟 0.35% = 35）。
    pub pct: usize,
    /// 每多少 tick 回一次（30 = 半秒，英雄联盟的回血节奏）。
    pub every: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { pct: 35, every: 30 }
    }
}

/// `{"pct":35,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "pct" => p.pct = v,
            "every" => p.every = v.max(1),
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 一次（`every` tick）该回的生命，按百万分之一记：最大生命 x pct/10000 x (1 + 层数) x every / 300。
/// 返回 (整数部分, 新的零头)，零头留到下一次。
pub fn regen_step(p: &Params, max_hp: usize, stacks: usize, carry: u64) -> (usize, u64) {
    let micro = max_hp as u64 * p.pct as u64 * (1 + stacks as u64) * p.every as u64 * 1_000_000 / (10_000 * 300) + carry;
    ((micro / 1_000_000) as usize, micro % 1_000_000)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 他身上金刚不坏有几层（最高一层还在就是几层：低层总比高层留得久）。
fn stacks(sim: &StableSim<'_>, id: usize) -> usize {
    (0..STACKS.len()).rev().find(|&k| has_buff(sim, id, STACKS[k])).map_or(0, |k| k + 1)
}

// ===================== 被动：金刚不坏 =====================

#[derive(Clone, Default)]
struct StoneSkin {
    p: Params,
    /// 回血的零头（百万分之一点生命）。
    carry: u64,
}

impl StablePassive for StoneSkin {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.carry = 0;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        if sim.tick() % self.p.every != 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, (hp, max_hp)) = (e.is_alive(), e.hp());
        if !alive || hp >= max_hp {
            self.carry = 0;
            return;
        }
        let n = stacks(sim, me);
        let (amount, carry) = regen_step(&self.p, max_hp, n, self.carry);
        self.carry = carry;
        if amount > 0 {
            sim.heal(me, me, amount);
            if let Some(k) = counted("regen") {
                wlog(format!("{} REGEN {amount} ({hp}/{max_hp}, {n} stacks) #{k}", head(sim, me)));
            }
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
        "=== {ID} v{VERSION} (Wukong: Stone Skin regenerates % max health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:stone"), StoneSkin::default());
    host.log(LogLevel::Info, "league_wukong loaded (Stone Skin % max-health regeneration).");
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
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"pct":40,"junk":7,"every":60}"#);
        assert_eq!((p.pct, p.every), (40, 60));
        assert_eq!(parse_params(r#"{"every":0}"#).every, 1);
    }

    #[test]
    fn the_copy_carries_the_default_params_and_no_data_regen() {
        let copy = include_str!("../override/league_wukong.data_champion");
        let at = copy.find("\"passive_ref\": \"league_wukong:stone\"").expect("no league_wukong:stone passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("pct", d.pct), ("every", d.every)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for name in STACKS {
            assert!(copy.contains(&format!("\"name\": \"{name}\"")), "the copy never lays {name}");
        }
        assert!(copy.contains("\"hp_regen\": 0"), "the copy's stacks still regenerate in data");
    }

    #[test]
    fn league_rates() {
        let p = Params::default();
        // 0.35% of 3000 every 5 s = 10.5; ten half-second steps
        let (mut sum, mut carry) = (0, 0);
        for _ in 0..10 {
            let (a, c) = regen_step(&p, 3000, 0, carry);
            sum += a;
            carry = c;
        }
        assert_eq!(sum, 10);
        // five stacks: 2.1% of 3000 every 5 s = 63
        let (mut sum, mut carry) = (0, 0);
        for _ in 0..10 {
            let (a, c) = regen_step(&p, 3000, 5, carry);
            sum += a;
            carry = c;
        }
        assert_eq!(sum, 63);
    }
}
