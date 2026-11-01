//! 悠米附加包：真正的附身（用户选的「放逐跟随 + 出招时现身」，2026-10-19）。
//!
//! 主包保持纯数据：W「悠米出动！」冲到队友身上放逐自己 `w_t` tick，每 `w_step` tick 传送一次跟着他，时间到跳下来；放逐期间她不能
//! 出招。`mod.override_info` 把主包的悠米换成 `override/` 里的副本（`tools/kit/build_yuumi.py --native`），被动 `league_yuumi:bond`：
//!
//! - **附身不限时**：副本的 W 跳到队友身上时给他挂 `league_yuumi_w_host`（3 tick），不再放逐自己；被动看见就附身：给她挂
//!   `league_yuumi_w_on`、给他挂 `league_yuumi_w_ride`（头上趴在书上的小猫），每 tick 把她摆到他的位置（`entity_set_pos`），一段一段
//!   地放逐她（每段 `w_chunk` tick，快结束时续上：谁都选不中、看不见她，防御塔也打不到）；每 `w_p` tick 给他回 `w_heal` + `w_hap`%
//!   法强生命（`league_yuumi_w_heal` 的画面）。他死了她就跳下来（`w_land` 的画面和声音）。
//! - **出招时现身**：她的 Q、R 好了且他身边（Q `q_range`、R `r_range`）有敌方英雄，或者 W 好了、他身边 `e_range` 内有敌方英雄
//!   （再给他一次旺盛精力），就不再续放逐：这一段放逐结束后她能出招，AI 钩子让她对最近的敌方英雄出这一招（不普攻、不走开）；
//!   出招期间挂 `league_yuumi_w_safe`（受到的伤害 -100%、免控）。冷却从 0 跳起来算出了招，这一招的动作（`q_dur` / `w_dur` / `r_dur`
//!   tick）放完就接着放逐；等了 `w_wait` tick 还没出招也接着放逐。出招时她的动作画成空白（`view.rs`，游戏 0.6.4 起的 Windows 版），头上的
//!   小猫一直在。
//! - **骑着再放 W，旺盛精力给他**（0.2.0，用户 2026-11-01：「悠米的W的护盾现在给上了吗」）：副本只在她身边 `W_ON_R` 内找队友给
//!   旺盛精力（0.1.0 她就坐在他身上），10-20 起她骑在他身后 `BESIDE`，够不着，11-01 的日志里她在他头上放了 19 次 W 都落空。现在
//!   看见她出了 W，`ZOOM_T` tick 后本包给他：护盾 `E_SH` + `E_AP`% 法强（`E_T` tick）、`league_yuumi_e_haste`（攻速、移速）、
//!   `league_yuumi_e_on` 和命中的画面；副本自己给上了（他身上已经有 e_on）就不再给。
//! - **看局势换人**（0.2.1，用户 2026-11-01：「还有个问题猫会智能附身吗 现在我感觉会长时间附身在一个人身上」——0.2.0 骑上
//!   一个人就骑到他死，日志里有一次 21355 tick）：骑着、没在出招时每 `SWITCH_EVERY` tick 看一次（同一个人至少骑 `MIN_RIDE`，
//!   两次换人隔 `SWITCH_CD`），在他 `SWITCH_R` 内的队友里照英雄联盟悠米的习惯挑（`switch_pick`）：他身边没有敌方英雄而别人在打，
//!   跳去打得最凶的；他血量好、旁边打架的队友快死了，跳去救；他不是中单 / 下路而中单 / 下路打得不比他少，跳去跟大哥。猫从他头上
//!   跳到新宿主头上（起跳的画面、附身的声音），她仍在放逐里，回血跟着换人。W 的冷却加不了，用 `SWITCH_CD` 代替。
//! - **AI**：附身时她不普攻、不回城、不自己走（都换成「站在他身上」），只在出招的那一小段放技能。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态记在每个悠米自己的被动实例里（服务端预模拟和
//! 你看的那场各算各的），AI 钩子读一张按（这份模拟的编号, 悠米）记的附身表。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yuumi.log`，每次启动游戏重写，上一次的留在 .prev.log：`ATTACH` /
//! `DETACH`（附在谁身上、为什么下来，ATTACH 带他那时的护盾）、`WINDOW`（为哪一招解除放逐、出没出招）、`AI casts`（每个窗口一行）、
//! `ZOOMIES`（骑着放的 W：他的护盾从多少到多少）、`SWITCH`（从谁换到谁、为什么、两人身边几个敌人和血量）、`WATCH`（每 30 秒
//! 一行的统计，没附身又什么都没变就不记）：你看的那场全记，服务端预模拟每种前 `LOG_FIRST` 行、之后每 `LOG_EVERY` 行记一行。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod lifts;
pub mod view;

const ID: &str = "league_yuumi";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_yuumi") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
const HERO: &str = "league_yuumi";
/// 她身上的附身 buff（view.rs 照它把她的动作换成空白的 a_*）。
pub const RIDING: &str = "league_yuumi_w_on";
/// 冷却从 0 跳到多少以上算出了招。
const CAST_JUMP: usize = 30;
/// 附身后续上放逐时，提前几 tick 续（两段之间不留空档）。
const OVERLAP: usize = 1;
/// Out this many ticks in a row with no window: what is on her goes to the log (10-29 games: after a window she was
/// often out tens to hundreds of ticks while every re-banish "succeeded").
const OUT_LONG: usize = 30;
/// 每多少 tick 记一行 WATCH。
const REPORT: usize = 1800;
/// How far behind her ally she is kept while riding (world units: two champions' radii and a little more). She used
/// to be put on his very spot every tick and walk onto it: the engine pushed the two apart each tick, so he shook and
/// went 1.6-1.9 times his move speed (2026-10-20 in game: 「英雄模型各种抽搐」「无限飞快的移速」 - league_yuumi.log
/// WATCH host steps avg 1615-1993 at move speed 1040). Out of reach of each other they never collide; banished she is
/// unseen, and the cat on his head is his own buff's picture.
const BESIDE: f64 = 22000.0;
/// The two nexuses (blue, red): "behind" him is toward his own.
const NEXUS: [(f64, f64); 2] = [(96000.0, 864000.0), (864000.0, 96000.0)];
/// Zoomies (P's e_sh, e_ap, e_t, e_as, e_ms; a test checks them against the copy): the shield and its AP %, how long it
/// and the haste last, the haste's attack speed and move speed %.
pub const E_SH: usize = 130;
pub const E_AP: usize = 60;
pub const E_T: usize = 180;
pub const E_AS: i32 = 20;
pub const E_MS: i32 = 10;
/// Riding, W again gives him Zoomies alone: the copy looks for the ally within this of HER (P's w_on_r, from 0.1.0 when
/// she sat on his spot). BESIDE behind him (from 10-20) is out of it, so the add-on gives it to him.
pub const W_ON_R: f64 = 8000.0;
/// Ticks from seeing W cast (its cooldown jumped) to giving him Zoomies: the copy's W fires at w_st - 2 = 9, and two more
/// to see whether the copy's own reached him (his e_on).
pub const ZOOM_T: usize = 11;
/// Hopping to a better host (0.2.1, user 2026-11-01: 「还有个问题猫会智能附身吗 现在我感觉会长时间附身在一个人身上」 - she
/// rode one ally until he died, 21355 ticks once): looked at every SWITCH_EVERY ticks with no cast under way, after
/// MIN_RIDE ticks on him and SWITCH_CD after the last hop (League: W again after 10 s; an add-on cannot start W's
/// cooldown), among the allies within SWITCH_R of him (P's w_ally_r, the copy's W reach) - `switch_pick`.
pub const SWITCH_EVERY: usize = 30;
pub const MIN_RIDE: usize = 300;
pub const SWITCH_CD: usize = 600;
pub const SWITCH_R: f64 = 70000.0;
/// An ally with an enemy champion this near is fighting.
pub const FIGHT_R: f64 = 60000.0;
/// A fighting ally under this % of his health is about to die; her host is fine over HOST_OK %.
pub const LOW_HP: usize = 35;
pub const HOST_OK: usize = 60;

/// 主包悠米的名字（buff、声音、画面都以它开头）。
fn yu(x: &str) -> String {
    format!("league_yuumi_{x}")
}

/// How far over the host's pivot the ride picture reaches down as drawn (its tail tuft; tools/art/import_yuumi_fx.py puts
/// the book on a 36-px champion's crown, 25 px up).
pub const RIDE_BOTTOM: i32 = 23;
/// How deep the picture sits in the host's hair.
pub const RIDE_SINK: i32 = 2;

/// The lift (`lifts::LIFTS`, game px) that sits the ride picture on a crown `crown` px over the host's pivot: its bottom
/// `RIDE_SINK` into his hair, the nearest lift there is, the higher one on a tie (2026-10-28, the user: 「附身在烬身上
/// 烬的头部都被挡住了」 - Jhin's crown is 29 px up, the picture covered his head from 23).
pub fn lift_for(crown: i32) -> i32 {
    let want = crown - RIDE_SINK - RIDE_BOTTOM;
    lifts::LIFTS.iter().copied().min_by_key(|&k| ((k - want).abs(), -k)).unwrap_or(0)
}

/// The host's ride buff for a lift (tools/kit/build_yuumi.py ride_buff: each has its view with that lift's tag).
pub fn ride_buff(lift: i32) -> String {
    match lift {
        0 => yu("w_ride"),
        k if k > 0 => yu(&format!("w_ride_u{k}")),
        k => yu(&format!("w_ride_d{}", -k)),
    }
}

/// The lift for a host by his champion name (0: a champion this repo does not draw - the picture as it was).
pub fn lift_of(name: &str) -> i32 {
    lifts::CROWNS.iter().find(|(n, _)| *n == name).map_or(0, |&(_, c)| lift_for(c))
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_YUUMI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_yuumi.log");
        }
    }
    PathBuf::from("league_yuumi.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    // the file stays open (league_lillia's log_open_once fix: opening it for every line stalled the simulation thread)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// A simulation's lines of a kind in the server's presims (hundreds of runs a launch): the first LOG_FIRST, then every
/// LOG_EVERY-th (10-30: 3.65 MB a launch, AI casts and WATCH nine tenths of it).
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

/// One more line of a kind: its count.
fn bump(kind: &'static str) -> usize {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    *n
}

/// The n-th line of a kind: the first 12, then every 25th (None = leave it out of the log).
pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let n = bump(kind);
    (n <= 12 || n % 25 == 0).then_some(n)
}

/// The match you watch (the view, a spectated match, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

/// The n-th line of a kind from a simulation: every one when `shown` (the match on screen), the presims' the first
/// LOG_FIRST, then every LOG_EVERY-th (None = leave it out of the log).
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n} #{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Params {
    /// 附身期间给他的回血：固定值、法强 %，每几 tick 一次。
    pub w_heal: usize,
    pub w_hap: usize,
    pub w_p: usize,
    /// Q、W、R 的施放距离（他身边这么近有敌方英雄才为这一招解除放逐）。
    pub q_range: usize,
    pub e_range: usize,
    pub r_range: usize,
    /// Q、W、R 动作的 tick（出了招，这么久之后接着放逐）。
    pub q_dur: usize,
    pub w_dur: usize,
    pub r_dur: usize,
    /// 每段放逐的 tick；解除放逐后最多等几 tick 让她出招。
    pub w_chunk: usize,
    pub w_wait: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            w_heal: 45,
            w_hap: 15,
            w_p: 60,
            q_range: 80000,
            e_range: 75000,
            r_range: 80000,
            q_dur: 28,
            w_dur: 18,
            r_dur: 30,
            w_chunk: 20,
            w_wait: 24,
        }
    }
}

/// `{"w_heal":45,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "w_heal" => &mut p.w_heal,
            "w_hap" => &mut p.w_hap,
            "w_p" => &mut p.w_p,
            "q_range" => &mut p.q_range,
            "e_range" => &mut p.e_range,
            "r_range" => &mut p.r_range,
            "q_dur" => &mut p.q_dur,
            "w_dur" => &mut p.w_dur,
            "r_dur" => &mut p.r_dur,
            "w_chunk" => &mut p.w_chunk,
            "w_wait" => &mut p.w_wait,
            _ => continue,
        };
        *slot = v;
    }
    p.w_p = p.w_p.max(1);
    p.w_chunk = p.w_chunk.max(2);
    p
}

static PARAMS: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

fn params() -> Params {
    *PARAMS.lock().unwrap_or_else(|e| e.into_inner())
}

// ===================== 计算 =====================

/// 一次附身回血（治疗前）。
pub fn ride_heal(p: &Params, ap: usize) -> usize {
    p.w_heal + p.w_hap * ap / 100
}

/// 旺盛精力的护盾（护盾强化前）。
pub fn zoomies_shield(ap: usize) -> usize {
    E_SH + E_AP * ap / 100
}

/// An ally as `switch_pick` weighs him: enemy champions within FIGHT_R of him, his health %, a carry (mid or bottom).
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Mate {
    pub id: usize,
    pub foes: usize,
    pub hp: usize,
    pub carry: bool,
}

/// Why she hops.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Why {
    /// He is out of the fight and someone near fights.
    Idle,
    /// He is fine and someone near, in a fight, is about to die.
    Rescue,
    /// He is no carry, he is fine and a carry fights as many as he does.
    Carry,
}

/// Who to hop to from `host` among `near` (the allies within SWITCH_R of him), League's Yuumi's way: she goes where the
/// fight is (the most enemy champions round him, then the lowest health, then a carry), saves the one about to die,
/// rides the carry (a hurt rider in a fight keeps her: 2026-11-02 logs, she left a Rumble at 30% for a Sivir at 96%
/// and came back to rescue him 2550 ticks later). None: she stays.
pub fn switch_pick(host: Mate, near: &[Mate]) -> Option<(Mate, Why)> {
    let need = |m: &&Mate| (m.foes, std::cmp::Reverse(m.hp), m.carry);
    if host.foes == 0 {
        return near.iter().filter(|m| m.foes > 0).max_by_key(need).map(|m| (*m, Why::Idle));
    }
    if host.hp > HOST_OK {
        if let Some(m) = near.iter().filter(|m| m.foes > 0 && m.hp < LOW_HP).min_by_key(|m| m.hp) {
            return Some((*m, Why::Rescue));
        }
    }
    if !host.carry && host.hp > HOST_OK {
        return near.iter().filter(|m| m.carry && m.foes >= host.foes).max_by_key(need).map(|m| (*m, Why::Carry));
    }
    None
}

/// 冷却从 `was` 变成 `now`：出了这一招（从好着跳到 CAST_JUMP 以上）。
pub fn cast_seen(was: usize, now: usize) -> bool {
    was == 0 && now > CAST_JUMP
}

/// 想出的招：三个技能各自好没好（冷却 0）、他身边各自的距离里有没有敌方英雄 -> 先 R、再 Q、再 W（旺盛精力）。
pub fn wanted(ready: [bool; 3], foe_in: [bool; 3]) -> Option<InputKindV1> {
    // [skill (Q), skill2 (W/E), ult (R)]
    if ready[2] && foe_in[2] {
        return Some(InputKindV1::Ult);
    }
    if ready[0] && foe_in[0] {
        return Some(InputKindV1::Skill);
    }
    if ready[1] && foe_in[1] {
        return Some(InputKindV1::Skill2);
    }
    None
}

fn kind_name(k: InputKindV1) -> &'static str {
    match k {
        InputKindV1::Skill => "Q",
        InputKindV1::Skill2 => "W/E",
        InputKindV1::Ult => "R",
        _ => "?",
    }
}

fn dist(a: (u64, u64), b: (u64, u64)) -> f64 {
    let dx = a.0 as f64 - b.0 as f64;
    let dy = a.1 as f64 - b.1 as f64;
    (dx * dx + dy * dy).sqrt()
}

/// Her spot while riding `at` (her ally's): BESIDE toward her team's nexus, inside the map.
pub fn beside(at: (u64, u64), team: usize) -> (u64, u64) {
    let (nx, ny) = NEXUS[team.min(1)];
    let (x, y) = (at.0 as f64, at.1 as f64);
    let (dx, dy) = (nx - x, ny - y);
    let d = (dx * dx + dy * dy).sqrt();
    let (ux, uy) = if d < 1.0 {
        let k = if team == 0 { -1.0 } else { 1.0 };
        (k * std::f64::consts::FRAC_1_SQRT_2, -k * std::f64::consts::FRAC_1_SQRT_2)
    } else {
        (dx / d, dy / d)
    };
    let clamp = |v: f64| v.clamp(0.0, 960000.0).round() as u64;
    (clamp(x + ux * BESIDE), clamp(y + uy * BESIDE))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// Her team's living champions but her, as `switch_pick` weighs them, and where they are.
fn mates(sim: &StableSim<'_>, team: usize, me: usize) -> Vec<(Mate, (u64, u64))> {
    let foes = champions(sim, team, false);
    let mut lanes = HashMap::new();
    for i in 0..sim.player_count() {
        if let Some(pl) = sim.player_at(i) {
            if let Some(c) = pl.champion() {
                lanes.insert(c.id(), pl.lane());
            }
        }
    }
    champions(sim, team, true).into_iter().filter(|c| c.0 != me).filter_map(|(id, at)| {
        let (hp, max) = sim.get_entity(id)?.hp();
        let carry = matches!(lanes.get(&id).copied().flatten(), Some(LaneV1::Mid | LaneV1::Bottom));
        let near = foes.iter().filter(|f| dist(at, f.1) <= FIGHT_R).count();
        Some((Mate { id, foes: near, hp: if max == 0 { 100 } else { hp * 100 / max }, carry }, at))
    }).collect()
}

/// Living champions of `team` (`mates`) or of the other team: (id, position).
fn champions(sim: &StableSim<'_>, team: usize, mates: bool) -> Vec<(usize, (u64, u64))> {
    let mut out = Vec::new();
    for i in 0..sim.champion_count() {
        let id = sim.champion_id_at(i);
        let Some(e) = sim.get_entity(id) else { continue };
        if (e.team() == team) == mates && e.is_alive() {
            out.push((id, e.pos()));
        }
    }
    out
}

fn ready_of(sim: &StableSim<'_>, me: usize) -> [usize; 3] {
    let Some(e) = sim.get_entity(me) else { return [usize::MAX; 3] };
    let cd = |s| left(e.cooldown(s));
    [cd(SkillSlotV1::Skill), cd(SkillSlotV1::Skill2), cd(SkillSlotV1::Ult)]
}

/// 一格还要冷却几 tick；等级没到、还锁着的格子（W 3 级前、R 5 级前）永远不算好了：不然她 5 级前每次都为 R 解除放逐，
/// R 按不出来（league_unlock_guard 把它换成普攻或站着），Q 和旺盛精力也轮不上（2026-10-27 的日志：附身 80 秒开了 34 次窗、
/// 一招没出）。
pub fn left(c: Option<CooldownV1>) -> usize {
    c.filter(|c| c.unlocked).map_or(usize::MAX, |c| c.remaining)
}

// ===================== 附身表（AI 钩子读） =====================

static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
const SIM_TAG: &str = "league_yuumi_sim:";

#[derive(Clone, Copy, Debug)]
struct Ride {
    host: usize,
    /// 解除放逐、等她出的那一招。
    cast: Option<InputKindV1>,
    /// The AI hook has logged its press of this window's cast (log only: it presses every tick of the window, about 26
    /// a window - one line a window).
    told: bool,
}

/// (这份模拟的编号, 悠米的 entity id) -> 她骑在谁身上。
static RIDES: LazyLock<Mutex<HashMap<(u64, usize), Ride>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn sim_tag(names: impl Iterator<Item = String>) -> u64 {
    let mut names = names;
    names.find_map(|n| n.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())).unwrap_or(0)
}

fn sim_of(sim: &StableSim<'_>, me: usize) -> u64 {
    sim.get_entity(me).map_or(0, |e| sim_tag((0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string())))
}

/// The AI hook's first press of a window's cast: marks the ride told (true only that first time).
fn first_press(key: (u64, usize)) -> bool {
    RIDES.lock().unwrap_or_else(|e| e.into_inner()).get_mut(&key).is_some_and(|r| !std::mem::replace(&mut r.told, true))
}

// ===================== 被动 =====================

#[derive(Clone, Copy, Debug)]
struct Window {
    kind: InputKindV1,
    /// 看见出了招的 tick。
    cast_at: Option<usize>,
    /// 到这一 tick 关窗（接着放逐）。
    until: usize,
}

/// 每个悠米一份。
#[derive(Clone, Default)]
struct Bond {
    p: Params,
    sim_no: u64,
    host: Option<usize>,
    /// the ride picture's buff on him (`ride_buff` of his lift)
    ride: String,
    since: usize,
    /// 她这一段放逐到哪一 tick。
    banished_until: usize,
    window: Option<Window>,
    /// 上一 tick 三个技能的冷却。
    last_cd: [usize; 3],
    next_heal: usize,
    /// 跳下来以后，放逐结束的那一 tick 放落地的画面。
    land_at: Option<usize>,
    attaches: usize,
    windows: usize,
    casts: usize,
    heals: usize,
    healed: usize,
    next_report: usize,
    /// Riding ticks, and those of them she was out (targetable) with no window open - a banish that did not hold.
    ridden: usize,
    out: usize,
    /// Ticks out in a row with no window open (logged at OUT_LONG).
    out_run: usize,
    /// `entity_banish` refusals (it respects cc_immune: the data's `w_act` / the window's `w_safe`).
    refused: usize,
    /// The host's position last tick and his steps since the last report (a push shows as steps over his move speed).
    host_at: Option<(u64, u64)>,
    steps: usize,
    step_sum: f64,
    step_max: f64,
    /// The counters at the last WATCH (log only: a report while she is free with none of them moved is left out).
    watched: [usize; 10],
    /// W cast from his head: (him, the tick to give him Zoomies); Zoomies given so far.
    zoom: Option<(usize, usize)>,
    zooms: usize,
    /// The first tick she may hop to another ally; hops so far.
    next_switch: usize,
    switches: usize,
}

impl Bond {
    fn record(&self, me: usize, cast: Option<InputKindV1>) {
        let mut r = RIDES.lock().unwrap_or_else(|e| e.into_inner());
        match self.host {
            Some(host) => {
                r.insert((self.sim_no, me), Ride { host, cast, told: false });
            }
            None => {
                r.remove(&(self.sim_no, me));
            }
        }
    }

    fn banish(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        let n = self.p.w_chunk;
        // a banish is refused while she is crowd-control immune (the data's casting flag `w_act` outlasts the window
        // by a tick, the window's `w_safe`): both go first. A refused one is tried again the next tick - it used to
        // count as taken, and she stood on the ally, out and hittable, until the next chunk (2026-10-19 in game:
        // 「附身后ADC非常的强 移速又快」)
        sim.entity_remove_buff(me, &yu("w_safe"));
        sim.entity_remove_buff(me, &yu("w_act"));
        if sim.entity_banish(me, me, n, "", "") {
            self.banished_until = tick + n;
        } else {
            self.refused += 1;
            if let Some(k) = tally(sim, "refused") {
                wlog(format!("{} BANISH #{k} refused", head(sim, me)));
            }
        }
    }

    fn attach(&mut self, sim: &mut StableSim<'_>, me: usize, host: usize, tick: usize) {
        self.host = Some(host);
        self.since = tick;
        self.window = None;
        self.land_at = None;
        self.next_heal = tick + self.p.w_p;
        self.attaches += 1;
        sim.entity_remove_buff(me, RIDING);
        sim.add_buff(me, &BuffV1::named(RIDING));
        let lift = sim.get_entity(host).and_then(|e| e.name()).map_or(0, |n| lift_of(&n));
        self.ride = ride_buff(lift);
        sim.entity_remove_buff(host, &self.ride);
        sim.add_buff(host, &BuffV1::named(&self.ride));
        if let Some(at) = sim.get_entity(host).map(|e| e.pos()) {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            let spot = beside(at, team);
            sim.entity_set_pos(me, spot.0, spot.1);
        }
        self.banish(sim, me, tick);
        self.record(me, None);
        self.zoom = None;
        self.next_switch = tick + MIN_RIDE;
        if let Some(k) = tally(sim, "attach") {
            // the jump's Zoomies lands with it (the copy shields the ally it lands on): his shield shows it
            let (hp, max, shield) = sim.get_entity(host).map_or((0, 0, 0), |e| (e.hp().0, e.hp().1, e.shield()));
            wlog(format!("{} ATTACH #{k} on {} ({hp}/{max} hp, shield {shield}), the ride picture {}", head(sim, me),
                         who(sim, host), self.ride));
        }
    }

    /// Zoomies for him, W cast from his head: the copy's own looks within `W_ON_R` of her, out of reach `BESIDE` behind
    /// him; given only when it did not reach him (no e_on on him).
    fn zoomies(&mut self, sim: &mut StableSim<'_>, me: usize, host: usize, ap: usize) {
        let on = yu("e_on");
        if has_buff(sim, host, &on) {
            if let Some(k) = tally(sim, "zoomies") {
                wlog(format!("{} ZOOMIES #{k}: the copy's own reached {} (e_on on him)", head(sim, me), who(sim, host)));
            }
            return;
        }
        let amount = zoomies_shield(ap);
        let before = sim.get_entity(host).map_or(0, |e| e.shield());
        let given = sim.entity_add_shield(host, amount, E_T);
        sim.add_buff(host, &BuffV1::timed(&on, E_T));
        let haste = yu("e_haste");
        let mut buff = BuffV1::timed(&haste, E_T);
        buff.attack_speed_mult = E_AS;
        buff.move_speed_mult = E_MS;
        sim.entity_remove_buff(host, &haste);
        sim.add_buff(host, &buff);
        let at = InputTargetV1::target(host);
        sim.play_view_effect(&yu("e_hit"), me, &at, 0, 0, 0);
        sim.play_sfx(&yu("e_hit"), me, &at);
        self.zooms += 1;
        if let Some(k) = tally(sim, "zoomies") {
            let after = sim.get_entity(host).map_or(0, |e| e.shield());
            wlog(format!("{} ZOOMIES #{k} on {}: shield {before} -> {after} (+{amount}{}), +{E_AS}% attack speed, \
                          +{E_MS}% move speed for {E_T} ticks", head(sim, me), who(sim, host),
                         if given { "" } else { ", refused" }));
        }
    }

    /// Hop from `from` to `to` (switch_pick's pick; `was` is how it weighed `from`): the ride picture leaves his head for
    /// the new one's, her jump's picture where she was and the attach sound on him, her spot beside him; still
    /// banished, and the heals go on to him.
    #[allow(clippy::too_many_arguments)]
    fn switch(&mut self, sim: &mut StableSim<'_>, me: usize, from: usize, to: Mate, was: Mate, why: Why, team: usize,
              tick: usize) {
        if let Some(here) = sim.get_entity(me).map(|e| e.pos()) {
            sim.play_view_effect(&yu("w_jump"), me, &InputTargetV1::pos(here.0, here.1), 0, 0, 0);
        }
        sim.entity_remove_buff(from, &self.ride);
        let lift = sim.get_entity(to.id).and_then(|e| e.name()).map_or(0, |n| lift_of(&n));
        self.ride = ride_buff(lift);
        sim.entity_remove_buff(to.id, &self.ride);
        sim.add_buff(to.id, &BuffV1::named(&self.ride));
        if let Some(at) = sim.get_entity(to.id).map(|e| e.pos()) {
            let spot = beside(at, team);
            sim.entity_set_pos(me, spot.0, spot.1);
        }
        sim.play_sfx(&yu("w_on"), me, &InputTargetV1::target(to.id));
        let rode = tick.saturating_sub(self.since);
        self.host = Some(to.id);
        self.since = tick;
        self.host_at = None;
        self.zoom = None;
        self.next_switch = tick + SWITCH_CD;
        self.switches += 1;
        self.record(me, None);
        if let Some(k) = tally(sim, "switch") {
            wlog(format!("{} SWITCH #{k} from {} after {rode} ticks to {}: {why:?} (he: {} enemy champions near, {}% hp; \
                          the new one: {}, {}%{})", head(sim, me), who(sim, from), who(sim, to.id), was.foes, was.hp,
                         to.foes, to.hp, if to.carry { ", a carry" } else { "" }));
        }
    }

    fn detach(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str, tick: usize) {
        let Some(host) = self.host.take() else { return };
        self.zoom = None;
        sim.entity_remove_buff(me, RIDING);
        sim.entity_remove_buff(me, &yu("w_safe"));
        self.host_at = None;
        if sim.get_entity(host).is_some() {
            sim.entity_remove_buff(host, &self.ride);
        }
        self.window = None;
        // she shows again when the banish she is in runs out: the landing then
        self.land_at = Some(self.banished_until.max(tick));
        self.record(me, None);
        if let Some(k) = tally(sim, "detach") {
            wlog(format!("{} DETACH #{k} from {} after {} ticks: {why}", head(sim, me), who(sim, host),
                         tick.saturating_sub(self.since)));
        }
    }

    /// The ally the data's jump just landed on (it marks him `w_host` for 3 ticks).
    fn new_host(&self, sim: &StableSim<'_>, me: usize, team: usize) -> Option<usize> {
        let mark = yu("w_host");
        champions(sim, team, true).into_iter().map(|c| c.0).find(|&id| id != me && has_buff(sim, id, &mark))
    }

    fn ride(&mut self, sim: &mut StableSim<'_>, me: usize, host: usize, team: usize, tick: usize) {
        let Some((alive, at)) = sim.get_entity(host).map(|e| (e.is_alive(), e.pos())) else {
            self.detach(sim, me, "the ally is gone", tick);
            return;
        };
        if !alive {
            self.detach(sim, me, "the ally died", tick);
            return;
        }
        let spot = beside(at, team);
        sim.entity_set_pos(me, spot.0, spot.1);
        self.ridden += 1;
        if let Some(last) = self.host_at {
            let d = dist(last, at);
            self.steps += 1;
            self.step_sum += d;
            self.step_max = self.step_max.max(d);
        }
        self.host_at = Some(at);
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        if tick >= self.next_heal {
            self.next_heal = tick + self.p.w_p;
            let amount = ride_heal(&self.p, ap);
            sim.heal(me, host, amount);
            sim.play_view_effect(&yu("w_heal"), me, &InputTargetV1::target(host), 0, 0, 0);
            self.heals += 1;
            self.healed += amount;
        }
        if let Some((h, due)) = self.zoom {
            if tick >= due {
                self.zoom = None;
                if h == host {
                    self.zoomies(sim, me, host, ap);
                }
            }
        }
        // a better host (League's Yuumi hops where she is needed): with no cast under way
        if self.window.is_none() && tick >= self.next_switch && tick % SWITCH_EVERY == 0 {
            let all = mates(sim, team, me);
            if let Some(&(him, _)) = all.iter().find(|(m, _)| m.id == host) {
                let near: Vec<Mate> =
                    all.iter().filter(|(m, p)| m.id != host && dist(at, *p) <= SWITCH_R).map(|(m, _)| *m).collect();
                if let Some((to, why)) = switch_pick(him, &near) {
                    self.switch(sim, me, host, to, him, why, team, tick);
                    self.last_cd = ready_of(sim, me);
                    return;
                }
            }
        }
        let cd = ready_of(sim, me);
        match self.window {
            None => {
                let foes = champions(sim, team, false);
                let near = |r: usize| foes.iter().any(|f| dist(at, f.1) <= r as f64);
                let ready = [cd[0] == 0, cd[1] == 0, cd[2] == 0];
                let foe_in = [near(self.p.q_range), near(self.p.e_range), near(self.p.r_range)];
                if let Some(kind) = wanted(ready, foe_in) {
                    let free_at = self.banished_until.max(tick);
                    let until = free_at + self.p.w_wait;
                    self.window = Some(Window { kind, cast_at: None, until });
                    self.out_run = 0;
                    self.windows += 1;
                    let mut safe = BuffV1::timed(&yu("w_safe"), until - tick + self.p.r_dur + 4);
                    safe.damaged_reduce = 100;
                    safe.cc_immune = true;
                    sim.entity_remove_buff(me, &yu("w_safe"));
                    sim.add_buff(me, &safe);
                    self.record(me, Some(kind));
                    if let Some(k) = tally(sim, "window") {
                        wlog(format!("{} WINDOW #{k} opens for {} in {} ticks ({} enemy champions near {})",
                                     head(sim, me), kind_name(kind), free_at - tick, foes.iter().filter(|f| dist(at, f.1)
                                         <= self.p.r_range.max(self.p.q_range) as f64).count(), who(sim, host)));
                    }
                } else {
                    // out with no window open: the last chunk ran out early or a re-banish given while it lasted did not
                    // lengthen it (the data's Banish ignores one in the SDK) - banish her again at once
                    let out = sim.get_entity(me).is_some_and(|e| e.is_targetable());
                    if out {
                        self.out += 1;
                        self.out_run += 1;
                        if self.out_run == OUT_LONG {
                            if let Some(k) = tally(sim, "long_out") {
                                let what = sim.get_entity(me).map_or_else(String::new, |e| {
                                    let b: Vec<String> = (0..e.buff_count()).filter_map(|i| e.buff_at(i))
                                        .map(|b| b.name().to_string()).collect();
                                    let c: Vec<String> = (0..e.cc_count()).filter_map(|i| e.cc_at(i))
                                        .map(|c| c.kind.to_string()).collect();
                                    format!("buffs [{}], cc [{}]", b.join(", "), c.join(" "))
                                });
                                wlog(format!("{} OUT LONG #{k}: {OUT_LONG} ticks out with no window ({what})", head(sim, me)));
                            }
                        }
                    } else {
                        self.out_run = 0;
                    }
                    if out || tick + OVERLAP >= self.banished_until {
                        self.banish(sim, me, tick);
                    }
                    if out {
                        // out between windows: no damage until the banish holds again (no cc immunity - that refuses
                        // the banish)
                        let mut cover = BuffV1::timed(&yu("w_cover"), 3);
                        cover.damaged_reduce = 100;
                        sim.entity_remove_buff(me, &yu("w_cover"));
                        sim.add_buff(me, &cover);
                    }
                }
            }
            Some(mut w) => {
                if w.cast_at.is_none() {
                    let slots = [InputKindV1::Skill, InputKindV1::Skill2, InputKindV1::Ult];
                    let durs = [self.p.q_dur, self.p.w_dur, self.p.r_dur];
                    if let Some(i) = (0..3).find(|&i| cast_seen(self.last_cd[i], cd[i])) {
                        w.cast_at = Some(tick);
                        w.until = tick + durs[i] + 2;
                        self.casts += 1;
                        if let Some(k) = tally(sim, "cast") {
                            wlog(format!("{} WINDOW cast #{k}: {} from {}'s head (asked {})", head(sim, me),
                                         kind_name(slots[i]), who(sim, host), kind_name(w.kind)));
                        }
                        if matches!(slots[i], InputKindV1::Skill2) {
                            self.zoom = Some((host, tick + ZOOM_T));
                        }
                    }
                }
                if tick >= w.until {
                    self.window = None;
                    sim.entity_remove_buff(me, &yu("w_safe"));
                    if w.cast_at.is_none() {
                        if let Some(k) = tally(sim, "nocast") {
                            wlog(format!("{} WINDOW #{k} closed without a cast ({})", head(sim, me), kind_name(w.kind)));
                        }
                    }
                    self.banish(sim, me, tick);
                    self.record(me, None);
                } else {
                    self.window = Some(w);
                }
            }
        }
        self.last_cd = cd;
    }
}

impl StablePassive for Bond {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
        *PARAMS.lock().unwrap_or_else(|e| e.into_inner()) = self.p;
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if self.sim_no == 0 {
            self.sim_no = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim_no);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        sim.entity_remove_buff(me, RIDING);
        self.host = None;
        self.window = None;
        self.land_at = None;
        self.zoom = None;
        self.record(me, None);
        if tally(sim, "spawn").is_some() {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN: the add-on's Yuumi (player {player}, team {team}, sim {}), {:?}", head(sim, me),
                         self.sim_no, self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let Some((alive, team, at)) = sim.get_entity(me).map(|e| (e.is_alive(), e.team(), e.pos())) else { return };
        if !alive {
            self.detach(sim, me, "she died", tick);
            return;
        }
        if let Some(t) = self.land_at {
            if tick >= t {
                self.land_at = None;
                let here = InputTargetV1::pos(at.0, at.1);
                sim.play_view_effect(&yu("w_land"), me, &here, 0, 0, 0);
                sim.play_sfx(&yu("w_off"), me, &here);
            }
        }
        match self.host {
            None => {
                if let Some(h) = self.new_host(sim, me, team) {
                    self.attach(sim, me, h, tick);
                }
            }
            Some(h) => self.ride(sim, me, h, team, tick),
        }
        if tick >= self.next_report {
            self.next_report = tick + REPORT;
            if tick > 0 {
                // free with nothing moved since the last report: no line (10-30: a quarter of the WATCH lines were all
                // zeros), and the presims' capped
                let now = [self.attaches, self.windows, self.casts, self.heals, self.healed, self.out, self.ridden,
                           self.refused, self.zooms, self.switches];
                let quiet = self.host.is_none() && now == self.watched;
                self.watched = now;
                if !quiet && tally(sim, "watch").is_some() {
                    // the host now: his move speed and attack speed (percent, 100 unbuffed), and his steps while ridden
                    let host_now = self.host.and_then(|h| sim.get_entity(h)).map_or(String::new(), |e| {
                        format!(", host move speed {} attack speed {}%", e.stat().move_speed, e.attack_speed_mult())
                    });
                    let steps = if self.steps > 0 {
                        format!(", host steps avg {:.0} max {:.0}", self.step_sum / self.steps as f64, self.step_max)
                    } else {
                        String::new()
                    };
                    wlog(format!("{} WATCH: attached {} times ({}), switches {}, windows {}, casts from the head {}, heals {} \
                                  ({} hp), zoomies {}, out {}/{} riding ticks, banish refused {}{steps}{host_now}",
                                 head(sim, me), self.attaches,
                                 self.host.map_or("free".to_string(), |h| format!("on {}", who(sim, h))), self.switches,
                                 self.windows, self.casts, self.heals, self.healed, self.zooms, self.out, self.ridden,
                                 self.refused));
                }
                self.steps = 0;
                self.step_sum = 0.0;
                self.step_max = 0.0;
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        self.detach(sim, me, "she died", tick);
    }
}

// ===================== AI 钩子：附身时不普攻、不走开，窗里出那一招 =====================

#[derive(Clone, Default)]
struct Ai;

impl StablePlayerAi for Ai {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ai")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let (input, line, key, told, shown) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let id = me.id();
            let key = (sim_of(&sim, id), id);
            let ride = RIDES.lock().unwrap_or_else(|e| e.into_inner()).get(&key).copied()?;
            let at = sim.get_entity(ride.host)?.pos();
            // stay on her spot behind him (walking onto his own spot pushed him: BESIDE)
            let spot = beside(at, me.team());
            let stay = InputV1::move_to(spot.0, spot.1);
            let input = match ride.cast {
                Some(kind) => {
                    let p = params();
                    let range = match kind {
                        InputKindV1::Ult => p.r_range,
                        InputKindV1::Skill => p.q_range,
                        _ => p.e_range,
                    };
                    let team = me.team();
                    let near = champions(&sim, team, false).into_iter().filter(|f| dist(at, f.1) <= range as f64)
                        .min_by(|a, b| dist(at, a.1).partial_cmp(&dist(at, b.1)).unwrap_or(std::cmp::Ordering::Equal));
                    match near {
                        Some((t, _)) => InputV1::action(kind, InputTargetV1::target(t)),
                        None => stay,
                    }
                }
                None => stay,
            };
            // the game's own choice stands when it is the cast she is out for
            if let (Some(b), Some(kind)) = (base, ride.cast) {
                if b.kind == kind.code() {
                    return None;
                }
            }
            (input, head(&sim, id), key, ride.told, on_screen(&sim))
        };
        if input.kind != InputKindV1::Move.code() {
            if !ctx.is_valid_input(&input) {
                return None;
            }
            // it presses every tick of the window, about 26 times: the first press is logged (10-30: every 25th press
            // was, 22.5k lines a launch), the presims' capped
            if !told && first_press(key) {
                if let Some(k) = noted("ai_cast", shown) {
                    wlog(format!("{line} AI casts {} from the ally's head #{k}",
                                 InputKindV1::from_code(input.kind).map_or("?", kind_name)));
                }
            }
        }
        Some(input)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Yuumi rides her ally with no end, untargetable, casting from his head) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:bond"), Bond::default());
    module.add_player_input_ai(Ai);
    view::install_once();
    host.log(LogLevel::Info, "league_yuumi loaded (Yuumi rides her ally with no end, casting from his head).");
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
    fn beside_keeps_her_off_his_spot() {
        for (at, team) in [((480000, 480000), 0), ((480000, 480000), 1), ((96000, 864000), 0), ((5000, 955000), 1)] {
            let b = beside(at, team);
            assert!(dist(at, b) > 20000.0, "{at:?} team {team}: {b:?}");
            assert!(b.0 <= 960000 && b.1 <= 960000);
        }
        // toward her own nexus
        assert!(beside((480000, 480000), 0).0 < 480000 && beside((480000, 480000), 1).0 > 480000);
    }

    #[test]
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"w_heal":30,"w_p":45,"q_range":70000,"w_chunk":10,"x":1}"#);
        assert_eq!((p.w_heal, p.w_p, p.q_range, p.w_chunk), (30, 45, 70000, 10));
        assert_eq!(p.w_hap, Params::default().w_hap);
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"w_p":0,"w_chunk":0}"#).w_p, 1);
        assert_eq!(parse_params(r#"{"w_chunk":0}"#).w_chunk, 2);
    }

    #[test]
    fn the_ride_heal_scales_with_ability_power() {
        let p = Params::default();
        assert_eq!(ride_heal(&p, 0), 45);
        assert_eq!(ride_heal(&p, 200), 75);
    }

    #[test]
    fn a_cast_is_a_cooldown_jumping_up_from_ready() {
        assert!(cast_seen(0, 420));
        assert!(!cast_seen(0, 0));
        assert!(!cast_seen(0, 10)); // a refund, not a cast
        assert!(!cast_seen(300, 420)); // still on cooldown
    }

    #[test]
    fn a_locked_slot_is_never_ready() {
        let cd = |remaining, unlocked| Some(CooldownV1 { remaining, unlocked, ..Default::default() });
        assert_eq!(left(cd(0, true)), 0);
        assert_eq!(left(cd(120, true)), 120);
        assert_eq!(left(cd(0, false)), usize::MAX); // R before level 5: cooldown 0 but it cannot be cast
        assert_eq!(left(None), usize::MAX);
        // the slot unlocking is not taken for a cast
        assert!(!cast_seen(left(cd(0, false)), left(cd(0, true))));
    }

    #[test]
    fn she_hops_where_she_is_needed() {
        let m = |id, foes, hp, carry| Mate { id, foes, hp, carry };
        // out of the fight: to the ally with the most enemy champions round him (then the lowest health)
        let idle = m(1, 0, 90, true);
        assert_eq!(switch_pick(idle, &[m(2, 1, 40, false), m(3, 2, 80, false)]), Some((m(3, 2, 80, false), Why::Idle)));
        assert_eq!(switch_pick(idle, &[m(2, 1, 40, false), m(3, 1, 80, false)]), Some((m(2, 1, 40, false), Why::Idle)));
        assert_eq!(switch_pick(idle, &[m(2, 0, 20, true)]), None, "nobody fights: she stays");
        // fine in a fight: to the ally about to die (the lowest)
        let fine = m(1, 1, 90, true);
        assert_eq!(switch_pick(fine, &[m(2, 2, 30, false), m(3, 1, 20, false)]), Some((m(3, 1, 20, false), Why::Rescue)));
        assert_eq!(switch_pick(m(1, 1, 50, true), &[m(3, 1, 20, false)]), None, "he needs her too");
        assert_eq!(switch_pick(fine, &[m(3, 0, 20, false)]), None, "low but out of the fight");
        // no carry: to a carry fighting as many
        let tank = m(1, 1, 80, false);
        assert_eq!(switch_pick(tank, &[m(4, 1, 70, true)]), Some((m(4, 1, 70, true), Why::Carry)));
        assert_eq!(switch_pick(tank, &[m(4, 0, 70, true)]), None);
        assert_eq!(switch_pick(m(1, 1, 30, false), &[m(4, 1, 96, true)]), None, "a hurt rider in a fight keeps her");
        assert_eq!(switch_pick(fine, &[m(4, 3, 70, true)]), None, "a carry's rider stays");
        // the pace: a hop waits for MIN_RIDE on him and SWITCH_CD after the last one, W's reach is the copy's
        assert!(MIN_RIDE < SWITCH_CD && SWITCH_EVERY < MIN_RIDE);
        assert!(SWITCH_R > BESIDE + FIGHT_R / 2.0);
    }

    #[test]
    fn zoomies_reach_him_from_behind() {
        // the copy gives the riding recast's Zoomies only within W_ON_R of her: she rides BESIDE behind him, out of it
        let at = (480_000, 480_000);
        for team in [0, 1] {
            assert!(dist(at, beside(at, team)) > W_ON_R, "team {team}: the copy's own would reach him");
        }
        assert_eq!(zoomies_shield(0), E_SH);
        assert_eq!(zoomies_shield(150), E_SH + E_AP * 150 / 100);
        // the numbers are the copy's (its riding W: skill2's w_on branch up to effect_none)
        let copy = include_str!("../override/league_yuumi.data_champion");
        let w = copy.find("\"skill2\"").expect("no skill2 in the copy");
        let at = w + copy[w..].find("\"buff_name\": \"league_yuumi_w_on\"").expect("no riding branch in the copy's W");
        let end = copy[at..].find("\"effect_none\"").expect("no end to the riding branch");
        let branch = &copy[at..at + end];
        for want in [format!("\"range\": {}", W_ON_R as usize), format!("\"amount\": {E_SH}"), format!("\"ap_ratio\": {E_AP}"),
                     format!("\"tick\": {E_T}"), format!("\"move_speed_mult\": {E_MS}"),
                     format!("\"attack_speed_mult\": {E_AS}")] {
            assert!(branch.contains(&want), "{want} is not in the copy's riding W");
        }
    }

    #[test]
    fn the_ult_first_then_q_then_zoomies() {
        assert_eq!(wanted([true, true, true], [true, true, true]), Some(InputKindV1::Ult));
        assert_eq!(wanted([true, true, true], [true, true, false]), Some(InputKindV1::Skill));
        assert_eq!(wanted([false, true, true], [true, true, false]), Some(InputKindV1::Skill2));
        assert_eq!(wanted([true, false, false], [false, true, true]), None); // Q ready but nobody in its range
        assert_eq!(wanted([false, false, false], [true, true, true]), None);
    }

    #[test]
    fn the_ride_picture_sits_on_the_hosts_crown() {
        // a 36-px champion (crown 25 up): as drawn
        assert_eq!(lift_for(25), 0);
        // Jhin (29 up) 4 higher, Hwei (39) as high as it goes, a small one (20) lower
        assert_eq!(lift_for(29), 4);
        assert_eq!(lift_for(60), 16);
        assert_eq!(lift_for(20), -4);
        assert_eq!(lift_for(0), -6);
        // a tie goes up
        assert_eq!(lift_for(26), 2);
        assert_eq!(lift_for(28), 4);
        assert_eq!(lift_of("league_jhin"), 4);
        assert_eq!(lift_of("some_other_mod_champion"), 0);
        assert_eq!(ride_buff(0), "league_yuumi_w_ride");
        assert_eq!(ride_buff(4), "league_yuumi_w_ride_u4");
        assert_eq!(ride_buff(-2), "league_yuumi_w_ride_d2");
    }

    #[test]
    fn every_lift_has_its_view_and_tag() {
        let main = include_str!("../../../league/champion/league_yuumi.data_champion");
        let copy = include_str!("../override/league_yuumi.data_champion");
        let fanim = include_str!("../../../league/effects/league_yuumi_ride#anim.fanim");
        for &k in lifts::LIFTS {
            let name = ride_buff(k);
            assert!(name.len() <= BUFF_NAME_CAP);
            let tag = if k == 0 { "idle".to_string() } else { name.trim_start_matches("league_yuumi_w_ride_").to_string() };
            for text in [main, copy] {
                assert!(text.contains(&format!("\"name\": \"{name}\"")), "no view for {name}");
                assert!(text.contains(&format!("\"tag\": \"{tag}\"")), "no tag {tag}");
            }
            assert!(fanim.contains(&format!("\"{tag}\"")) && fanim.contains(&format!("\"hd_{tag}\"")), "no tag {tag} in the sheet");
        }
    }

    #[test]
    fn the_sim_number_rides_on_a_buff() {
        let names = vec!["league_yuumi_w_on".to_string(), format!("{SIM_TAG}4")];
        assert_eq!(sim_tag(names.into_iter()), 4);
        assert_eq!(sim_tag(vec!["league_tahmkench_sim:3".to_string()].into_iter()), 0);
    }

    #[test]
    fn buff_names_fit() {
        for x in ["w_on", "w_ride", "w_host", "w_safe", "w_heal", "w_land", "w_off"] {
            assert!(yu(x).len() <= BUFF_NAME_CAP);
        }
        assert_eq!(RIDING, yu("w_on"));
    }

    #[test]
    fn the_copy_names_what_the_add_on_reads() {
        // the add-on's copy of the kit carries the passive and the host mark the add-on looks for
        let copy = include_str!("../override/league_yuumi.data_champion");
        assert!(copy.contains("\"league_yuumi:bond\""));
        assert!(copy.contains("\"league_yuumi_w_host\""));
        assert!(copy.contains("\"league_yuumi_w_on\""));
        let main = include_str!("../../../league/champion/league_yuumi.data_champion");
        assert!(main.contains("\"league_yuumi_w_ride\""), "the ride picture's view is in the main pack");
        assert!(main.contains("\"league_yuumi_w_heal\"") && main.contains("\"league_yuumi_w_land\""));
    }
}
