//! 艾瑞莉娅附加包：Q「利刃冲击」真正的刷新（用户选「做附加包：Q 真实刷新」）。
//!
//! 主包是纯数据：数据读不到目标身上的印记，也不知道 Q 打死了谁，所以主包里印记是她身上的旗子 `mk`（E/R 打中英雄时挂上，
//! 下一次 Q 时附近有敌方英雄就算），击杀靠 league_jinx 的击杀触发器近似。`mod.override_info` 把主包的艾瑞莉娅换成
//! `override/` 里的副本（tools/kit/build_irelia.py 的 native=True）：技能一样，只是
//! - 印记是挂在被打中的英雄身上的真 buff `league_irelia_mark`（5 秒，原本就有图），她身上不再挂 `mk`；
//! - Q 落地不再自己判断击杀，也不在施放时花 `mk`；
//! - 被动 `league_irelia:surge`。
//!
//! 被动：
//! - 她身上 `league_irelia_q_dash` 出现 = 一次 Q 冲刺开始；冲刺里她第一次造成伤害（`on_attack`）的那个单位就是 Q 的目标。
//!   目标身上有印记：拿掉印记（英雄联盟里印记被 Q 消耗），给她挂 `league_irelia_q_again`；这一下把目标打死了
//!   （冲刺开始后 `q_dur + 10` tick 内：英雄看 `on_kill`；小兵、野怪死了游戏不调 `on_kill`，看目标没了或没血）：也挂 `q_again`。数据里她身上的轮询看到 `q_again` 就再冲一次
//!   （被控的英雄 → 英雄 → 最近的单位，一次施放最多 3 段）。
//!
//! AI 钩子 `league_irelia:hop`（英雄联盟里刀妹的「跳兵线」）：Q 好了、Q 射程里没有敌方英雄、但 `hop_reach` 内有一个看得见、
//! 不在敌方塔下的英雄、她自己血量不低于 `hop_hp`% 时，挑一个 Q 射程内、这一下 Q 能打死（估算的伤害打过它现在的血量）、
//! 而且比她离那个英雄更近的小兵或野怪，对它放 Q：打死它就刷新，下一段冲向英雄。内置 AI 本来就要放 Q 时，射程里有带印记的
//! 英雄就改打他（印记 = 刷新）。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去；AI 钩子读被动配置时存下的同一份）。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_irelia.log`，每次启动游戏重写，上一次的留在 .prev.log。
//! 每种行（`SPAWN`、`RESET`、`Q HIT`、`HOP`、`Q AT THE MARK`）整个游戏一个计数：你看的那场每条都记，服务器的预模拟先记
//! `LOG_FIRST` 条、之后每 `LOG_EVERY` 条记一条（0.1.3：以前每个艾瑞莉娅自己数，每份预模拟又从 #1 记起，一次启动记了 11 403 行）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_irelia";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_irelia") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 主包艾瑞莉娅的名字（buff、音效都以它开头）。
fn ir(x: &str) -> String {
    format!("league_irelia_{x}")
}

/// 敌方塔的攻击范围（大约，塔下不跳）。
pub const TOWER_REACH: f64 = 75_000.0;
/// 跳板要比她离英雄近多少才算往英雄那边走。
pub const HOP_GAIN: f64 = 8_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_IRELIA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_irelia.log");
        }
    }
    PathBuf::from("league_irelia.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (15 000 lines a session,
    // about 9 s of stalls on the simulation thread, 2026-10-12, the user: 「LOL mod让游戏掉帧很严重 加载很卡」)
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

/// 日志条数：每种整个游戏先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条（你看的那场每条都写）。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

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

/// Like `noted`, but every line of the match on screen: only the presims capped.
fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    noted(kind, on_screen(sim))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// `q_again` 挂多久（= 数据里轮询的时长）。
    pub poll: usize,
    pub q_dmg: usize,
    pub q_ratio: usize,
    pub q_range: usize,
    pub q_dur: usize,
    /// 1 = AI 钩子跳兵线，0 = 不跳。
    pub hop: usize,
    pub hop_reach: usize,
    pub hop_hp: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { poll: 150, q_dmg: 25, q_ratio: 70, q_range: 45_000, q_dur: 16, hop: 1, hop_reach: 90_000, hop_hp: 40 }
    }
}

/// `{"poll":150,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "poll" => p.poll = v,
            "q_dmg" => p.q_dmg = v,
            "q_ratio" => p.q_ratio = v,
            "q_range" => p.q_range = v,
            "q_dur" => p.q_dur = v,
            "hop" => p.hop = v,
            "hop_reach" => p.hop_reach = v,
            "hop_hp" => p.hop_hp = v,
            _ => {}
        }
    }
    p
}

/// 被动 `configure` 时存下（所有艾瑞莉娅共用同一张参数表），AI 钩子读它。
static SHARED: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

// ===================== 计算 =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// Q 打一个单位大概多少（物理伤害，按护甲 `def` 打折：100 / (100 + def)）。
pub fn q_damage(ad: usize, def: usize, p: &Params) -> usize {
    let raw = p.q_dmg + ad * p.q_ratio / 100;
    raw * 100 / (100 + def)
}

/// 一个看得见的单位。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Unit {
    pub id: usize,
    pub at: (f64, f64),
    pub r: f64,
    pub champion: bool,
    pub hp: usize,
    pub def: usize,
    pub marked: bool,
}

/// 跳板：Q 射程内、这一下能打死、比她离英雄 `c` 近 `HOP_GAIN` 以上的小兵或野怪里，离 `c` 最近的。
pub fn pick_hop(me: (f64, f64), ad: usize, c: &Unit, units: &[Unit], p: &Params) -> Option<Unit> {
    let mine = dist(me, c.at);
    units
        .iter()
        .filter(|u| !u.champion && u.hp > 0)
        .filter(|u| dist(me, u.at) <= p.q_range as f64 + u.r)
        .filter(|u| q_damage(ad, u.def, p) >= u.hp)
        .filter(|u| dist(u.at, c.at) + HOP_GAIN < mine)
        .min_by(|a, b| dist(a.at, c.at).total_cmp(&dist(b.at, c.at)))
        .copied()
}

// ===================== 小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn timed(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 被动 =====================

/// 正在进行的一段 Q 冲刺。
#[derive(Clone, Copy, Debug, Default)]
struct Dash {
    start: usize,
    target: Option<usize>,
    reset: bool,
}

/// 每个艾瑞莉娅一份。日志的计数不在这里（每份预模拟从 #1 数起就限不住条数），在 `noted`。
#[derive(Clone, Default)]
struct Surge {
    p: Params,
    dash: Option<Dash>,
    was_dashing: bool,
}

impl Surge {
    fn reset(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str, target: usize) {
        let Some(d) = self.dash.as_mut() else { return };
        if d.reset {
            return;
        }
        d.reset = true;
        timed(sim, me, &ir("q_again"), self.p.poll);
        if let Some(n) = tally(sim, if why == "mark" { "reset mark" } else { "reset kill" }) {
            wlog(format!("{} RESET #{n} ({why}): Q on {} -> one more dash", head(sim, me), who(sim, target)));
        }
    }
}

impl StablePassive for Surge {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
        *SHARED.lock().unwrap_or_else(|e| e.into_inner()) = self.p.clone();
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.dash = None;
        self.was_dashing = false;
        // every respawn comes here: the launch's count like the other lines
        if tally(sim, "spawn").is_some() {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN: the add-on's Irelia (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let now = has_buff(sim, me, &ir("q_dash"));
        if now && !self.was_dashing {
            self.dash = Some(Dash { start: tick, target: None, reset: false });
        }
        self.was_dashing = now;
        // 小兵、野怪死了游戏不调 on_kill（只有英雄）：冲刺里打中的目标在窗口内没了或没血 = 这一下打死了
        if let Some(d) = self.dash {
            if let Some(t) = d.target {
                if !d.reset && tick <= d.start + self.p.q_dur + 10 && sim.get_entity(t).map_or(true, |e| e.hp().0 == 0) {
                    self.reset(sim, me, "kill", t);
                }
            }
        }
        if self.dash.is_some_and(|d| tick > d.start + self.p.q_dur + 12) {
            self.dash = None;
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        let Some(d) = self.dash else { return };
        if d.target.is_some() || !has_buff(sim, me, &ir("q_dash")) {
            return;
        }
        self.dash.as_mut().unwrap().target = Some(target);
        if !sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            if let Some(n) = tally(sim, "q hit") {
                wlog(format!("{} Q HIT #{n} {} ({} hp left)", head(sim, me), who(sim, target),
                             sim.get_entity(target).map_or(0, |e| e.hp().0)));
            }
        }
        let mark = ir("mark");
        if has_buff(sim, target, &mark) {
            sim.entity_remove_buff(target, &mark);
            self.reset(sim, me, "mark", target);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        let Some(d) = self.dash else { return };
        if d.target == Some(victim) && sim.tick() <= d.start + self.p.q_dur + 10 {
            self.reset(sim, me, "kill", victim);
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.dash = None;
        self.was_dashing = false;
    }
}

// ===================== AI 钩子：跳兵线 =====================

/// The AI is still recalling (game 0.6.5 decides when to go home and buy): its last order was a Return - it orders only
/// on its judgement ticks, a Return again while the recall lasts, nothing in between - and any other order ends it
/// (league_ult_press 0.5.0's rule).
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

/// How much farther from a champion the AI's walk must end to be a retreat (league_ult_press's `HOLD_AWAY`).
pub const AWAY: f64 = 10_000.0;

/// The AI walks away from `to` this tick (a retreat, a disperse from a lost objective): its Move ends more than `AWAY`
/// farther from it than the champion stands now.
pub fn walking_away(base: Option<InputV1>, me: (f64, f64), to: (f64, f64)) -> bool {
    let d = |a: (f64, f64), b: (f64, f64)| ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt();
    base.is_some_and(|b| b.kind == InputKindV1::Move.code() && d((b.x as f64, b.y as f64), to) > d(me, to) + AWAY)
}

#[derive(Clone, Default)]
struct Hop {
    /// 上一次改写的 (她, 目标)：施放开始前每 tick 都会再问一次，同一个目标只算一次
    last: Option<(usize, usize)>,
    /// AI 在回城（`still_recalling`）：不跳兵线
    recalling: bool,
}

/// 她看得见的敌方单位（不含塔），和敌方塔的位置。
fn scan(sim: &StableSim<'_>, team: usize) -> (Vec<Unit>, Vec<(f64, f64)>) {
    let mark = ir("mark");
    let mut units = Vec::new();
    let mut towers = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if !e.is_alive() || e.team() == team {
            continue;
        }
        let (x, y) = e.pos();
        let at = (x as f64, y as f64);
        if e.is_tower() {
            towers.push(at);
            continue;
        }
        if !e.is_targetable() || !sim.is_visible(team, e.id()) {
            continue;
        }
        let marked = (0..e.buff_count()).filter_map(|k| e.buff_at(k)).any(|b| b.name() == mark);
        units.push(Unit {
            id: e.id(),
            at,
            r: e.radius() as f64,
            champion: e.is_champion(),
            hp: e.hp().0,
            def: e.stat().defence,
            marked,
        });
    }
    (units, towers)
}

impl StablePlayerAi for Hop {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:hop")
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == "league_irelia"
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let p = SHARED.lock().unwrap_or_else(|e| e.into_inner()).clone();
        let me_id = ctx.player_id();
        self.recalling = still_recalling(self.recalling, base);
        let (choice, line, shown) = {
            let sim = ctx.sim()?;
            let shown = on_screen(&sim);
            let player = sim.get_player(me_id)?;
            if player.cooldowns()?.1 > 0 {
                self.last = None;               // Q 放出去了：下一次同一个目标再记一行
                return None;
            }
            let her = player.champion()?;
            if !her.is_alive() {
                return None;
            }
            let (hx, hy) = her.pos();
            let me = (hx as f64, hy as f64);
            let team = her.team();
            let her_id = her.id();
            let ad = her.stat().attack;
            let (hp, max) = her.hp();
            let (units, towers) = scan(&sim, team);
            let in_q = |u: &Unit| dist(me, u.at) <= p.q_range as f64 + u.r;
            let champs: Vec<&Unit> = units.iter().filter(|u| u.champion).collect();
            let wants_q = base.is_some_and(|b| b.kind == InputKindV1::Skill.code());
            // 内置 AI 要放 Q：射程里有带印记的英雄就改打他
            if wants_q {
                if let Some(m) = champs.iter().filter(|u| u.marked && in_q(u)).min_by(|a, b| {
                    dist(me, a.at).total_cmp(&dist(me, b.at))
                }) {
                    if base.is_some_and(|b| b.target.target_id != m.id) {
                        (Some((m.id, false)), format!("{} Q AT THE MARK: {} instead", head(&sim, her_id), who(&sim, m.id)),
                         shown)
                    } else {
                        return None;
                    }
                } else {
                    return None;
                }
            } else {
                // not while the AI recalls (0.6.5 decides when to go home and buy)
                if self.recalling || p.hop == 0 || max == 0 || hp * 100 < p.hop_hp * max || champs.iter().any(|u| in_q(u)) {
                    return None;
                }
                let safe = |c: &Unit| towers.iter().all(|t| dist(*t, c.at) > TOWER_REACH);
                let Some(c) = champs
                    .iter()
                    .filter(|c| dist(me, c.at) <= p.hop_reach as f64 && safe(c))
                    .min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at)))
                else {
                    return None;
                };
                // nor toward a champion the AI walks away from (a retreat, 0.6.5's disperse)
                if walking_away(base, me, c.at) {
                    return None;
                }
                let s = pick_hop(me, ad, c, &units, &p)?;
                (
                    Some((s.id, true)),
                    format!(
                        "{} HOP: Q at {} ({} hp, {:.0} away) toward {} ({:.0} away)",
                        head(&sim, her_id),
                        who(&sim, s.id),
                        s.hp,
                        dist(me, s.at),
                        who(&sim, c.id),
                        dist(me, c.at)
                    ),
                    shown,
                )
            }
        };
        let (target, hop) = choice?;
        let input = InputV1::action(InputKindV1::Skill, InputTargetV1::target(target));
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if self.last == Some((me_id, target)) {
            return Some(input);
        }
        self.last = Some((me_id, target));
        if let Some(n) = noted(if hop { "hop" } else { "mark" }, shown) {
            wlog(format!("{line} (#{n})"));
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
        "=== {ID} v{} (Irelia: Bladesurge resets on the real mark or kill, hops the wave) loaded: game {}.{}.{} abi {} log={} ===",
        VERSION,
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:surge"), Surge::default());
    module.add_player_input_ai(Hop::default());
    host.log(LogLevel::Info, "league_irelia v1 loaded (Irelia's Bladesurge resets and wave hops).");
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

    fn unit(id: usize, x: f64, champion: bool, hp: usize) -> Unit {
        Unit { id, at: (x, 0.0), r: 8_000.0, champion, hp, def: 0, marked: false }
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"poll":120,"q_range":40000,"x":1}"#),
                   Params { poll: 120, q_range: 40_000, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn q_damage_follows_armour() {
        let p = Params::default();
        assert_eq!(q_damage(100, 0, &p), 95);
        assert_eq!(q_damage(100, 100, &p), 47);
    }

    #[test]
    fn the_hop_is_a_killable_unit_toward_the_champion() {
        let p = Params::default();
        let c = unit(9, 80_000.0, true, 900);
        let units = [
            unit(1, 30_000.0, false, 50),   // killable, toward him
            unit(2, 40_000.0, false, 500),  // too healthy
            unit(3, -30_000.0, false, 50),  // killable, the wrong way
            unit(4, 60_000.0, false, 50),   // out of Q range (45000 + 8000)
            c,
        ];
        assert_eq!(pick_hop((0.0, 0.0), 100, &c, &units, &p).map(|u| u.id), Some(1));
        assert_eq!(pick_hop((0.0, 0.0), 10, &c, &units, &p), None, "too weak to kill anything");
    }

    #[test]
    fn presim_lines_are_capped_for_the_launch_and_the_match_on_screen_is_not() {
        let logged: Vec<usize> = (0..LOG_EVERY * 3).filter_map(|_| noted("test presim", false)).collect();
        assert_eq!(logged.len(), LOG_FIRST + 3);
        assert_eq!(logged[LOG_FIRST..], [LOG_EVERY, LOG_EVERY * 2, LOG_EVERY * 3]);
        assert!((0..LOG_EVERY * 2).all(|_| noted("test shown", true).is_some()));
    }
}
