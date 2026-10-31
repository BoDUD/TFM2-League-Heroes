//! 悟空附加包（用户 2026-10-18：「技能方案按 A 做（带扩展包 league_wukong）」）。主包保持纯数据；`mod.override_info` 把主包的
//! 悟空换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_wukong.py 的 `native=1` 生成：技能一字不改，被动换成本包的
//! `league_wukong:stone`，金刚不坏的五层不再带数据里的固定回血），本包补数据做不到的三件事：
//!
//! - **按最大生命回血**（英雄联盟的金刚不坏）：数据读不到生命，主包每层每秒回固定值；本包每 `every` tick 按他身上金刚不坏的层数
//!   （主包的 `league_wukong_s_1` ~ `s_5`）回复最大生命：每 5 秒 `pct`/100 %（英雄联盟 0.35%）×（1 + 层数），叠满 5 层是 2.1%。
//!   零头攒着下次一起回，不会因为取整丢掉。
//! - **分身画出来**（0.1.2，用户 2026-10-29：「猴子开大还是没分身啊」「现在分身都看不见」）：主包的分身是锚点（射程 1 的
//!   弹道）`end_effects` 里一格一格放的画面，这种画面游戏里从来不显示（锤石 R 的箱子、永恩留下的身体同一个毛病），所以玩家
//!   从没见过分身。副本里 W 施放那一刻调 `league_wukong:clone`，把分身站的地方写成他身上的一个 buff（`league_wukong_clone:…`），
//!   被动下一拍读走（每份模拟各记各的，不用全局表，两份预模拟同时跑时不会串）；伤害照旧是数据锚点的，画面由本包每 `w_slot`
//!   tick 在那里放一次：他在转（`r_on`，英雄联盟里有分身时分身也开大）放 `w_clone_spin`，每 `w_period` 一次出手的那格放
//!   `w_clone_atk`，其余 `w_clone`。他死了、`w_live` 没了（数据的分身散了）、`w_t` 到了，就不再画。
//! - **替 AI 按 W**（0.1.2，「你确定会放分身吗现在 我怎么一次没见过」→「加上」，src/trickster.rs）：游戏的 AI 几乎总先按 E，
//!   W 一局只放几次；W 好了、射程内有敌方英雄时替他按（英雄联盟里 W 开团、接大招）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_wukong.log`，每次启动游戏重写，上一次的留在 .prev.log：`REGEN`
//! （回了多少、几层）、`W PRESS`（替他按的 W）、`CLONE`（分身站在哪）、`CLONE SPINS`（他开大时分身跟着转）、`CLONE GONE`；
//! 预模拟限了条数，你看的那场每条都记。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod trickster;

const ID: &str = "league_wukong";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.4";
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

fn bump(kind: &'static str) -> usize {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    *n
}

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let n = bump(kind);
    (n <= LOG_FIRST || n % LOG_EVERY == 0).then_some(n)
}

/// The match you watch (the view, a spectated match, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

/// Like `counted`, but every one when `shown` (the match you watch): the presims stay capped.
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let n = bump(kind);
    (shown || n <= LOG_FIRST || n % LOG_EVERY == 0).then_some(n)
}

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    noted(kind, on_screen(sim))
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
    /// 分身：活多久、一格画面多少 tick、多久出手一次（主包的 w_t、w_slot、w_period）。
    pub w_t: usize,
    pub w_slot: usize,
    pub w_period: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { pct: 35, every: 30, w_t: 240, w_slot: 20, w_period: 60 }
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
            "w_t" => p.w_t = v,
            "w_slot" => p.w_slot = v.max(1),
            "w_period" => p.w_period = v.max(1),
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

// ===================== 分身（W）：本包画 =====================

/// 交接 buff 的前缀：`league_wukong_clone:<x>:<y>:<tick>`（W 施放那一刻他站的地方、那一拍）。
const MARK: &str = "league_wukong_clone:";
/// 数据的分身还在（W 施放时挂上，`w_t` tick；他死了就没了）、他在转大招。
const W_LIVE: &str = "league_wukong_w_live";
const R_ON: &str = "league_wukong_r_on";
/// 数据锚点下一拍落下、第 k 格再过 k * w_slot + 1 tick：第一格在施放后 2 tick（SDK 模拟里量的）。
pub const FIRST_SLOT: usize = 2;

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 一个分身：站哪、哪拍散、下一格画面在哪拍、第几格、上一格在不在转（日志用）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Decoy {
    pub at: Pt,
    pub until: usize,
    pub next_slot: usize,
    pub slot: usize,
    pub spinning: bool,
}

impl Decoy {
    pub fn new(at: Pt, cast: usize, p: &Params) -> Decoy {
        Decoy { at, until: cast + p.w_t, next_slot: cast + FIRST_SLOT, slot: 0, spinning: false }
    }
}

/// 交接 buff 的名字。
pub fn mark(at: Pt, tick: usize) -> String {
    format!("{MARK}{:.0}:{:.0}:{tick}", at.0, at.1)
}

/// 交接 buff -> (位置, 施放的那拍)。
pub fn read_mark(name: &str) -> Option<(Pt, usize)> {
    let mut it = name.strip_prefix(MARK)?.split(':');
    let x = it.next()?.parse::<f64>().ok()?;
    let y = it.next()?.parse::<f64>().ok()?;
    let t = it.next()?.parse::<usize>().ok()?;
    Some(((x, y), t))
}

/// 第 k 格放哪张（主包的排法）：他在转就是转的；每 `w_period` 一次出手的那格是出手的；其余站着的。
pub fn slot_pic(p: &Params, k: usize, spinning: bool) -> &'static str {
    if spinning {
        "w_clone_spin"
    } else if k % (p.w_period / p.w_slot).max(1) == 0 {
        "w_clone_atk"
    } else {
        "w_clone"
    }
}

fn pos_input(p: Pt) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

/// W 施放（`league_wukong:clone`，在他冲出去之前）：把他站的地方写在他身上，被动下一拍读走。0.1.4：一个短时 buff（交接位置的
/// 附加包都这么做：奥恩的柱子、阿克尚的绳子），日志 `MARK`——2026-10-30 的两次启动 W 放了，却一次 `CLONE` 都没有。
struct CloneMark;

/// 交接 buff 留多久（被动下一拍就读走）。
const MARK_T: usize = 30;

impl StableEffectType for CloneMark {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _input: InputTargetV1) {
        let Some(at) = sim.get_entity(me).map(|e| (e.pos().0 as f64, e.pos().1 as f64)) else { return };
        let name = mark(at, sim.tick());
        sim.add_buff(me, &BuffV1::timed(&name, MARK_T));
        if let Some(k) = tally(sim, "mark") {
            wlog(format!("{} MARK #{k}: W cast at ({:.0}, {:.0})", head(sim, me), at.0, at.1));
        }
    }
}

// ===================== 被动：金刚不坏 =====================

#[derive(Clone, Default)]
struct StoneSkin {
    p: Params,
    /// 回血的零头（百万分之一点生命）。
    carry: u64,
    /// 本包在画的分身。
    decoy: Option<Decoy>,
}

impl StoneSkin {
    /// 每 tick：读走 W 刚写的位置，在分身站的地方按格放画面；他死了、数据的分身散了、时间到了就停。
    fn draw_clone(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        let (names, alive) = {
            let Some(e) = sim.get_entity(me) else { return };
            ((0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect::<Vec<_>>(),
             e.is_alive())
        };
        for name in names.iter().filter(|n| n.starts_with(MARK)) {
            sim.entity_remove_buff(me, name);
            if let Some((at, cast)) = read_mark(name) {
                self.decoy = Some(Decoy::new(at, cast, &self.p));
                if let Some(k) = tally(sim, "clone") {
                    wlog(format!("{} CLONE #{k} at ({:.0}, {:.0}) for {} ticks", head(sim, me), at.0, at.1, self.p.w_t));
                }
            }
        }
        let Some(mut d) = self.decoy else { return };
        let live = names.iter().any(|n| n == W_LIVE);
        if !alive || !live || now >= d.until {
            self.decoy = None;
            if let Some(k) = tally(sim, "clone gone") {
                let why = if !alive { "he died" } else if !live { "the data's clone is gone" } else { "its time is up" };
                wlog(format!("{} CLONE GONE #{k} after {} slots: {why}", head(sim, me), d.slot));
            }
            return;
        }
        if now >= d.next_slot {
            let spinning = names.iter().any(|n| n == R_ON);
            let pic = slot_pic(&self.p, d.slot, spinning);
            sim.play_view_effect(&format!("{ID}_{pic}"), me, &pos_input(d.at), 0, 0, 0);
            if spinning && !d.spinning {
                if let Some(k) = tally(sim, "clone spins") {
                    wlog(format!("{} CLONE SPINS #{k}: his R with the clone out, slot {}", head(sim, me), d.slot));
                }
            }
            d.spinning = spinning;
            d.slot += 1;
            d.next_slot += self.p.w_slot;
        }
        self.decoy = Some(d);
    }
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
        self.decoy = None;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        self.draw_clone(sim, me);
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
        "=== {ID} v{VERSION} (Wukong: Stone Skin regenerates % max health, the clone drawn where it stands) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:stone"), StoneSkin::default());
    // 0.1.2: W's clone drawn by the add-on (the data's pictures in its anchor never show in game), and W pressed for the
    // AI with an enemy champion in reach (src/trickster.rs: the game's AI cast it 4 times a game)
    module.add_native_effect(format!("{ID}:clone"), CloneMark);
    module.add_player_input_ai(trickster::Trickster::default());
    host.log(LogLevel::Info, "league_wukong loaded (Stone Skin % max-health regeneration, the clone drawn).");
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
        for (k, v) in [("pct", d.pct), ("every", d.every), ("w_t", d.w_t), ("w_slot", d.w_slot), ("w_period", d.w_period)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for name in STACKS {
            assert!(copy.contains(&format!("\"name\": \"{name}\"")), "the copy never lays {name}");
        }
        assert!(copy.contains("\"hp_regen\": 0"), "the copy's stacks still regenerate in data");
    }

    #[test]
    fn the_copy_leaves_the_clone_s_pictures_to_the_add_on() {
        let copy = include_str!("../override/league_wukong.data_champion").replace('\r', "");
        let main = include_str!("../../../league/champion/league_wukong.data_champion").replace('\r', "");
        assert!(copy.contains("\"effect_ref\": \"league_wukong:clone\""), "W does not mark the clone's spot");
        for pic in ["w_clone", "w_clone_atk", "w_clone_spin"] {
            // a ViewEffect's name is its last key (no comma after it); the view_effects entry goes on with "anim"
            let call = format!("\"name\": \"league_wukong_{pic}\"\n");
            assert!(main.matches(&call).count() > 1, "the main pack never plays {pic}");
            assert_eq!(copy.matches(&call).count(), 0, "the copy still plays {pic} in data");
            assert!(copy.contains(&format!("\"name\": \"league_wukong_{pic}\",\n")), "the copy lost the {pic} view");
        }
        // no clone of the spin's own (League's: the clone spins only when W left one)
        assert!(!main.contains("league_wukong_w_rc"), "the spin still brings a clone of its own");
    }

    #[test]
    fn the_mark_carries_the_spot_and_the_tick() {
        assert_eq!(read_mark(&mark((314_040.0, 367_255.0), 15_653)), Some(((314_040.0, 367_255.0), 15_653)));
        assert_eq!(read_mark("league_wukong_w_live"), None);
        assert_eq!(read_mark("league_wukong_clone:1:2"), None);
    }

    #[test]
    fn the_slots_follow_the_data() {
        let p = Params::default();
        // the SDK simulation: W at 15652 (its effect 15653), pictures at 15655 then every 20 ticks, 12 of them
        let d = Decoy::new((0.0, 0.0), 15_653, &p);
        assert_eq!((d.next_slot, d.until), (15_655, 15_893));
        let pics: Vec<_> = (0..6).map(|k| slot_pic(&p, k, false)).collect();
        assert_eq!(pics, ["w_clone_atk", "w_clone", "w_clone", "w_clone_atk", "w_clone", "w_clone"]);
        assert_eq!(slot_pic(&p, 4, true), "w_clone_spin");
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
