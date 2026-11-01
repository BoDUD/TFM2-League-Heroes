//! 厄加特附加包（用户选「主包数据 + 附加包」，2026-10-16「方案可以，全按推荐做（上单，W 并进 Q/E，做附加包，PPU 1.5）」）：
//! 主包数据做不到的两件事。
//!
//! `mod.override_info` 把主包的厄加特换成 `override/` 里的副本（tools/kit/build_urgot.py 的 native=1）：数据和主包一样，只是
//! - 被动挂本包的 `league_urgot:legs`（参数在英雄数据的 `passive.params` 里）；
//! - 普攻和净除的每一发调本包的 `league_urgot:leg`，本包让厄加特身上出现 1 tick 的 `league_urgot_leg_go` 时才喷；
//! - R 拴满时调本包的 `league_urgot:mercy`，本包让厄加特身上出现 1 tick 的 `league_urgot_r_low` 时才拽回来处决。
//!
//! - **回响烈焰按方向**：六条腿各朝一个方向（每条 60°），各有自己的冷却（主包每条腿冷却 x `LEGS_FACING`：朝着目标的两条
//!   轮流，平均下来和主包一样快）；目标在哪个方向，就用朝那边的两条腿里冷却好的那条（英雄联盟：普攻落在哪条腿的扇形里就是哪条）。
//!   主包数据只有一个公共冷却、六条腿轮流。3 级前的冷却用 `leg_t0`（数据只认得 3 级，这里用技能 2 是否解锁来判断，和数据一致）。
//! - **超越死亡的恐惧的真处决**：拴满 4 秒时，目标当前生命低于最大生命的 `EXECUTE`%（英雄联盟 25%）才拽回来处决；
//!   血多的只吃钻头的伤害和减速。主包数据读不到当前生命，拴满就拽、造成最大生命 25% 的真实伤害。
//!
//! - **鄙弃把人甩到身后**（用户 2026-10-24：「厄加特的E是不是有bug啊 不能把人背回来」）：E 出手时 `league_urgot:dash` 记下
//!   他起跳的位置；抓住后 `e_fling` tick，`league_urgot:fling` 把目标在 `e_pull_t` tick 内一步步挪到他身后 `e_behind`
//!   处、朝起跳那一边（英雄联盟：越过他的头甩到背后，等于拖回自己这边）。主包数据只能用 `Pull` 往他身上拉：冲刺落在目标
//!   身上时两人重叠，引擎把两人往随机方向推开，大约一半甩错了边（经典模拟 trace）。
//!
//! - **鄙弃把人甩到身后**（用户 2026-10-24：「厄加特的E是不是有bug啊 不能把人背回来」）：E 出手时 `league_urgot:dash` 记下
//!   他起跳的位置；抓住时 `league_urgot:fling` 记下抓住的人（0.2.1：原来放在冲刺结束后的 Delayed 里，游戏里一次都没调到，
//!   146 个厄加特 0 行 FLING），`e_fling` tick 后本包把目标在 `e_pull_t` tick 内一步步挪到他身后 `e_behind` 处、
//!   朝起跳那一边（英雄联盟：越过他的头甩到背后，等于拖回自己这边）。主包数据只能用 `Pull` 往他身上拉：冲刺落在目标身上时
//!   两人重叠，引擎把两人往随机方向推开，大约一半甩错了边（经典模拟 trace）。
//!
//! 数字：`EXECUTE`、`LEGS_FACING` 写在这里；其余从英雄数据来，`tests::the_numbers_match_the_kit` 读主包的参数表核对默认值。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_urgot.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_urgot";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_urgot") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

// ===================== 数值 =====================

/// R 的处决线：目标当前生命低于最大生命的这个百分比（英雄联盟 25%）。
pub const EXECUTE: usize = 25;
/// 朝着目标的腿有几条（它们轮流喷）：每条腿的冷却 = 主包的公共冷却 x 这个数。
pub const LEGS_FACING: u64 = 2;

fn ur(x: &str) -> String {
    format!("league_urgot_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_URGOT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_urgot.log");
        }
    }
    PathBuf::from("league_urgot.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening it for every line stalled the simulation thread (league_galio, 2026-10-12)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first).
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
    noted(kind, false)
}

/// One more line of `kind` (the count of the whole launch, every sim): its number when it is to be written - the first
/// `LOG_FIRST`, then every `LOG_EVERY`-th, and every one when `shown`.
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

/// Like `counted`, but every line of the match on screen: only the presims capped.
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 计算（单元测试用） =====================

/// 从 `me` 看 `p` 在哪条腿的扇形里：0..6，0 = 正右（屏幕 x 正方向），逆着 y 增大的方向数（60° 一条）。
pub fn leg_of(me: (f64, f64), p: (f64, f64)) -> usize {
    let a = (p.1 - me.1).atan2(p.0 - me.0).to_degrees().rem_euclid(360.0);
    ((a + 30.0) / 60.0).floor() as usize % 6
}

/// 朝着 `p` 的两条腿：它所在扇形的那条，和它更靠近的那个邻居。
pub fn facing_legs(me: (f64, f64), p: (f64, f64)) -> [usize; 2] {
    let a = (p.1 - me.1).atan2(p.0 - me.0).to_degrees().rem_euclid(360.0);
    let k = leg_of(me, p);
    let centre = k as f64 * 60.0;
    let off = ((a - centre + 540.0) % 360.0) - 180.0;
    let other = if off >= 0.0 { (k + 1) % 6 } else { (k + 5) % 6 };
    [k, other]
}

/// 两条朝着目标的腿里，冷却好（`now - last >= cd`）的那条，先看扇形里那条。
pub fn ready_leg(last: &[u64; 6], legs: [usize; 2], now: u64, cd: u64) -> Option<usize> {
    legs.into_iter().find(|&k| last[k] == 0 || now.saturating_sub(last[k]) >= cd)
}

/// 生命 `hp` / `max` 在处决线以下吗。
pub fn under_line(hp: usize, max: usize) -> bool {
    max > 0 && hp * 100 < max * EXECUTE
}

// ===================== 参数（英雄数据的 passive.params） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 主包的公共腿冷却：3 级前、3 级起（tick）。
    pub leg_t0: u64,
    pub leg_t: u64,
    /// 主包处决的真实伤害（最大生命 %），只用来核对处决线。
    pub r_ex: usize,
    /// 鄙弃：甩到他身后多远、几 tick 甩完。
    pub e_behind: u64,
    pub e_pull_t: u64,
    /// 抓住后几 tick 才甩（数据的 `e_fling`；本包自己等，数据里的 Delayed 在游戏里调不到本包）。
    pub e_fling: u64,
}

impl Default for Params {
    fn default() -> Self {
        Params { leg_t0: 480, leg_t: 180, r_ex: 25, e_behind: 15000, e_pull_t: 3, e_fling: 15 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        match k {
            "leg_t0" => p.leg_t0 = v,
            "leg_t" => p.leg_t = v,
            "r_ex" => p.r_ex = v as usize,
            "e_behind" => p.e_behind = v,
            "e_pull_t" => p.e_pull_t = v,
            "e_fling" => p.e_fling = v,
            _ => {}
        }
    }
    p
}

/// 每份模拟的厄加特一个编号，出生时由被动挂在他身上（buff `league_urgot_sim:<编号>`，没有数值、没有画面）：游戏 0.6.4
/// 同一局两份预模拟和画面同时跑，实体编号和 tick 都一样，只按实体记会串到别的模拟（加里奥附加包的做法）。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
const SIM_TAG: &str = "league_urgot_sim:";

/// The number the passive hung on him when he spawned in this sim (0: none).
pub fn sim_tag(names: impl Iterator<Item = String>) -> u64 {
    names.into_iter().find_map(|n| n.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())).unwrap_or(0)
}

fn sim_of(sim: &StableSim<'_>, me: usize) -> u64 {
    sim.get_entity(me).map_or(0, |e| sim_tag((0..e.buff_count()).filter_map(|i| e.buff_at(i))
        .map(|b| b.name().to_string())))
}

/// 每份模拟的每个厄加特：参数、六条腿上次喷的 tick（0 = 还没喷过）、鄙弃起跳的位置、正在甩的人。
#[derive(Clone, Copy, Default)]
struct Legs {
    p: Params,
    last: [u64; 6],
    from: Option<(f64, f64)>,
    /// 抓住的人和甩出去的 tick（到了才算落点：那时他和目标的位置）。
    due: Option<(usize, u64)>,
    throw: Option<Throw>,
}

/// 一次甩人：谁、从哪到哪、第几 tick 开始、几 tick 甩完。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Throw {
    pub target: usize,
    pub start: (f64, f64),
    pub end: (f64, f64),
    pub at: u64,
    pub ticks: u64,
}

/// 地图的边（单位坐标，留一个身位）。
const MAP_MIN: f64 = 12_000.0;
const MAP_MAX: f64 = 948_000.0;

/// Where the caught one lands: `behind` past him, on the side he dashed from (from the target's side when he did not
/// move: then straight over him).
pub fn landing(me: (f64, f64), from: Option<(f64, f64)>, target: (f64, f64), behind: f64) -> (f64, f64) {
    let unit = |d: (f64, f64)| {
        let n = (d.0 * d.0 + d.1 * d.1).sqrt();
        (n > 1.0).then(|| (d.0 / n, d.1 / n))
    };
    let back = from
        .and_then(|f| unit((f.0 - me.0, f.1 - me.1)))
        .or_else(|| unit((me.0 - target.0, me.1 - target.1)))
        .unwrap_or((1.0, 0.0));
    let c = |v: f64| v.clamp(MAP_MIN, MAP_MAX);
    (c(me.0 + back.0 * behind), c(me.1 + back.1 * behind))
}

/// The thrown one's spot `k` ticks into the throw (the last tick on the landing).
pub fn step(t: &Throw, k: u64) -> (f64, f64) {
    let f = (k as f64 / t.ticks.max(1) as f64).min(1.0);
    (t.start.0 + (t.end.0 - t.start.0) * f, t.start.1 + (t.end.1 - t.start.1) * f)
}

static STATE: LazyLock<Mutex<HashMap<(u64, usize), Legs>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn pos_of(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() {
        return None;
    }
    let (x, y) = e.pos();
    Some((x as f64, y as f64))
}

// ===================== 回响烈焰：哪条腿 =====================

struct Leg;

impl StableEffectType for Leg {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let (Some(me), Some(at)) = (pos_of(sim, caster), pos_of(sim, input.target_id)) else { return };
        let level3 = sim.get_entity(caster).and_then(|e| e.cooldown(SkillSlotV1::Skill2)).is_some_and(|c| c.unlocked);
        let key = (sim_of(sim, caster), caster);
        let now = sim.tick() as u64;
        let legs = facing_legs(me, at);
        let mut st = STATE.lock().unwrap_or_else(|e| e.into_inner());
        let s = st.entry(key).or_default();
        let cd = LEGS_FACING * if level3 { s.p.leg_t } else { s.p.leg_t0 };
        let Some(k) = ready_leg(&s.last, legs, now, cd) else { return };
        s.last[k] = now;
        drop(st);
        sim.add_buff(caster, &BuffV1::timed(&ur("leg_go"), 1));
        if let Some(n) = counted("leg") {
            wlog(format!("{} LEG #{n} leg {k} (facing {legs:?}) at {}, cooldown {cd} ticks", head(sim, caster),
                         who(sim, input.target_id)));
        }
    }
}

// ===================== 鄙弃：起跳的位置、甩到身后 =====================

struct Dash;

impl StableEffectType for Dash {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        let Some(me) = pos_of(sim, caster) else { return };
        let key = (sim_of(sim, caster), caster);
        STATE.lock().unwrap_or_else(|e| e.into_inner()).entry(key).or_default().from = Some(me);
    }
}

struct Fling;

impl StableEffectType for Fling {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            if let Some(n) = counted("fling?") {
                wlog(format!("{} FLING? #{n}: called without a target (input kind {})", head(sim, caster), input.kind));
            }
            return;
        }
        let target = input.target_id;
        if pos_of(sim, caster).is_none() || pos_of(sim, target).is_none() {
            return;
        }
        let key = (sim_of(sim, caster), caster);
        let now = sim.tick() as u64;
        let mut st = STATE.lock().unwrap_or_else(|e| e.into_inner());
        let s = st.entry(key).or_default();
        let at = now + s.p.e_fling;
        s.due = Some((target, at));
        drop(st);
        if let Some(n) = counted("catch") {
            wlog(format!("{} CATCH #{n} {}: flung at t={at}", head(sim, caster), who(sim, target)));
        }
    }
}

/// The throw's start the tick it is due: from where the caught one stands, over him to the side he dashed from.
fn start_throw(sim: &StableSim<'_>, me: usize, s: &mut Legs, target: usize, now: u64) {
    s.due = None;
    let (Some(u), Some(at)) = (pos_of(sim, me), pos_of(sim, target)) else { return };
    let end = landing(u, s.from.take(), at, s.p.e_behind as f64);
    s.throw = Some(Throw { target, start: at, end, at: now, ticks: s.p.e_pull_t.max(1) });
    if let Some(n) = counted("fling") {
        wlog(format!("{} FLING #{n} {} from ({:.0}, {:.0}) over him at ({:.0}, {:.0}) to ({:.0}, {:.0})", head(sim, me),
                     who(sim, target), at.0, at.1, u.0, u.1, end.0, end.1));
    }
}

// ===================== 超越死亡的恐惧：处决谁 =====================

struct Mercy;

impl StableEffectType for Mercy {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let target = input.target_id;
        if pos_of(sim, caster).is_none() {
            return; // a dead Urgot reels nobody in
        }
        let Some((hp, max)) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        let low = under_line(hp, max);
        if low {
            sim.add_buff(caster, &BuffV1::timed(&ur("r_low"), 1));
        }
        if let Some(n) = counted(if low { "mercy" } else { "spared" }) {
            wlog(format!("{} {} #{n} {} at {hp}/{max} ({:.0}%)", head(sim, caster), if low { "EXECUTE" } else { "SPARED" },
                         who(sim, target), hp as f64 * 100.0 / max.max(1) as f64));
        }
    }
}

// ===================== 被动：参数和模拟编号 =====================

#[derive(Clone, Default)]
struct Passive {
    p: Params,
    /// This sim's number (`SIM_TAG`), drawn at his first spawn.
    sim_no: u64,
}

impl StablePassive for Passive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if self.sim_no == 0 {
            self.sim_no = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim_no);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        let mut st = STATE.lock().unwrap_or_else(|e| e.into_inner());
        if st.len() > 4096 {
            st.clear(); // finished sims
        }
        st.insert((self.sim_no, me), Legs { p: self.p, ..Legs::default() });
        drop(st);
        // every spawn of every presim's Urgot: the launch's count (0.2.2; 212 lines on 11-01)
        if tally(sim, "spawn").is_some() {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN: the add-on's Urgot (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let key = (self.sim_no, me);
        let now = sim.tick() as u64;
        {
            let mut st = STATE.lock().unwrap_or_else(|e| e.into_inner());
            if let Some(s) = st.get_mut(&key) {
                if let Some((target, _)) = s.due.filter(|&(_, at)| now >= at) {
                    start_throw(sim, me, s, target, now);
                }
            }
        }
        let throw = STATE.lock().unwrap_or_else(|e| e.into_inner()).get(&key).and_then(|s| s.throw);
        let Some(t) = throw else { return };
        let k = (sim.tick() as u64).saturating_sub(t.at) + 1;
        if pos_of(sim, t.target).is_some() {
            let (x, y) = step(&t, k);
            sim.entity_set_pos(t.target, x.round() as u64, y.round() as u64);
        }
        if k >= t.ticks || pos_of(sim, t.target).is_none() {
            if let Some(s) = STATE.lock().unwrap_or_else(|e| e.into_inner()).get_mut(&key) {
                s.throw = None;
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
        "=== {ID} v{VERSION} (Urgot: Echoing Flames by direction, Disdain flings over him, Fear Beyond Death executes below {EXECUTE}% health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:legs"), Passive::default());
    module.add_native_effect(format!("{ID}:leg"), Leg);
    module.add_native_effect(format!("{ID}:mercy"), Mercy);
    module.add_native_effect(format!("{ID}:dash"), Dash);
    module.add_native_effect(format!("{ID}:fling"), Fling);
    host.log(LogLevel::Info, "league_urgot loaded (Echoing Flames by direction, Disdain flings over him, Fear Beyond Death's real execute).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_leg_facing_the_target() {
        let me = (0.0, 0.0);
        assert_eq!(leg_of(me, (10.0, 0.0)), 0);
        assert_eq!(leg_of(me, (10.0, 10.0)), 1); // 45 degrees
        assert_eq!(leg_of(me, (-10.0, 0.0)), 3);
        assert_eq!(leg_of(me, (10.0, -1.0)), 0); // just under the x axis
        assert_eq!(facing_legs(me, (10.0, 1.0)), [0, 1]);
        assert_eq!(facing_legs(me, (10.0, -1.0)), [0, 5]);
    }

    #[test]
    fn two_legs_take_turns() {
        let mut last = [0u64; 6];
        let legs = [0, 1];
        assert_eq!(ready_leg(&last, legs, 100, 360), Some(0));
        last[0] = 100;
        assert_eq!(ready_leg(&last, legs, 150, 360), Some(1));
        last[1] = 150;
        assert_eq!(ready_leg(&last, legs, 300, 360), None);
        assert_eq!(ready_leg(&last, legs, 460, 360), Some(0));
    }

    #[test]
    fn the_execution_line() {
        assert!(under_line(249, 1000));
        assert!(!under_line(250, 1000));
        assert!(!under_line(0, 0));
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"leg_t":180,"leg_t0":480,"r_ex":25,"e_behind":15000,"e_pull_t":3,"e_fling":15}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_fling_lands_behind_him_on_the_side_he_came_from() {
        // he dashed from (400000, 500000) to (500000, 500000) onto a target standing on him
        let end = landing((500_000.0, 500_000.0), Some((400_000.0, 500_000.0)), (500_000.0, 500_000.0), 15_000.0);
        assert_eq!(end, (485_000.0, 500_000.0));
        // the target bumped past him: still thrown to the side he came from
        let end = landing((500_000.0, 500_000.0), Some((400_000.0, 500_000.0)), (490_000.0, 500_000.0), 15_000.0);
        assert_eq!(end, (485_000.0, 500_000.0));
        // no dash recorded: straight over him, away from the target
        let end = landing((500_000.0, 500_000.0), None, (510_000.0, 500_000.0), 15_000.0);
        assert_eq!(end, (485_000.0, 500_000.0));
        // never off the map
        let end = landing((14_000.0, 500_000.0), Some((0.0, 500_000.0)), (20_000.0, 500_000.0), 15_000.0);
        assert_eq!(end, (MAP_MIN, 500_000.0));
    }

    #[test]
    fn the_throw_steps_to_the_landing() {
        let t = Throw { target: 9, start: (0.0, 0.0), end: (30_000.0, 0.0), at: 100, ticks: 3 };
        assert_eq!(step(&t, 1), (10_000.0, 0.0));
        assert_eq!(step(&t, 3), (30_000.0, 0.0));
        assert_eq!(step(&t, 5), (30_000.0, 0.0));
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_urgot.py");
        let src = std::fs::read_to_string(path).expect("build_urgot.py");
        let d = Params::default();
        for (key, v) in [("leg_t0", d.leg_t0 as usize), ("leg_t", d.leg_t as usize), ("r_ex", d.r_ex),
                         ("e_behind", d.e_behind as usize), ("e_pull_t", d.e_pull_t as usize),
                         ("e_fling", d.e_fling as usize)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_urgot.P");
        }
        assert_eq!(d.r_ex, EXECUTE, "the main pack's execute line is the add-on's");
    }

    #[test]
    fn the_names_fit() {
        for x in ["leg_go", "r_low"] {
            assert!(ur(x).len() <= BUFF_NAME_CAP);
        }
        assert!(format!("{SIM_TAG}{}", u64::MAX).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn each_sim_finds_its_own_number() {
        let names = |v: &[&str]| v.iter().map(|s| s.to_string()).collect::<Vec<_>>().into_iter();
        assert_eq!(sim_tag(names(&["league_urgot_leg_go", "league_urgot_sim:7"])), 7);
        assert_eq!(sim_tag(names(&["league_urgot_r_low"])), 0);
    }
}
