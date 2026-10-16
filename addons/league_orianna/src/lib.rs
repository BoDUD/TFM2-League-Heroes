//! 奥莉安娜附加包（用户选「做附加包」，2026-10-16「方案可以」）：主包数据做不到的三件事。
//!
//! `mod.override_info` 把主包的奥莉安娜换成 `override/` 里的副本（tools/kit/build_orianna.py 的 native=1）：球的三种位置、
//! W/R 在球那里放、牵引、控制器都和主包一样，只是
//! - 被动挂本包的 `league_orianna:ball`（参数在英雄数据的 `passive.params` 里）：每 tick 记下球真正在哪；
//! - Q 扔球、E 送球、E 回到自己身上时先调本包（`:q` / `:e` / `:back`），数据自己的抛物线和追踪弹换成不显示的；
//! - E 选队友改成对她身边的每个友方英雄调 `:e_pick`，被选中的那个让她身上出现 1 tick 的 `league_orianna_e_this`；
//! - R 待命时对球附近的每个敌方英雄调 `:r_kill`，能击杀就算「两个英雄」（她身上 `league_orianna_c2`），不再有「落单目标」那条。
//!
//! - **球从它所在的位置飞出**：Q 的球从地上、队友身上或飞回来的半路飞向目标脚下（`league_orianna_q_ball` 的画面，飞 `q_travel` tick，
//!   和数据不显示的抛物线同时落地）；E 的球从那里飞向队友（`league_orianna_e_ball`，和数据的追踪弹同时到），球不在她身上时路上的
//!   敌人由本包从球的位置到队友这条线上打（`:e_hit`，`e_dmg` + `e_dap`% 法强魔法伤害，宽 `e_w`），数据那条从她出发的线只在球在她
//!   身上时才放；E 给自己时球从原处飞回来。
//! - **E 送给最危险的队友**：`e_range` 内、`e_near` 内有敌方英雄的友方英雄里，按「最近约一秒受到的伤害占最大生命的比例 × 2 +
//!   已损失生命比例」挑最高的；她自己身边也有敌人而且比他们都危险时留给自己（数据 2 tick 后给自己加盾）。
//! - **R 读血量**：球附近 2 个敌方英雄照旧放；只有 1 个时，`r_dmg` + `r_ap`% 法强按他的魔抗（伤害 × 100 / (100 + 魔抗)）算得死才放。
//!
//! 球在哪：她身上有 `league_orianna_home` 就在她身边；Q 扔出后按 `q_travel` 飞到落点，之后停在那里；E 送出后追着队友，那个队友身上
//! 出现 `league_orianna_e_def` 就跟着他；她身上有 `league_orianna_b_ret`（球在飞回来）就以 `b_back` 每 tick 朝她走。
//! 判断「被控」本包用不到。游戏 0.6.4 同一局两份预模拟和画面同时跑、实体编号一样：出生时给她挂模拟编号 buff
//! （`league_orianna_sim:<n>`），球的记录按（模拟，奥莉安娜）分开。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_orianna.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_orianna";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";

// ===================== 数值 =====================

/// 近一秒受到的伤害：每 tick 乘这个数（半衰期约 1 秒，60 tick）。
pub const FOCUS_DECAY: f64 = 0.9885;
/// 挑队友时「受到的伤害比例」的权重（再加已损失生命比例）。
pub const FOCUS_WEIGHT: f64 = 2.0;
/// E 给自己时球离她超过这么远才画飞回来的球；飞回来的速度。
pub const BACK_SHOWN: f64 = 6_000.0;
pub const BACK_SPEED: f64 = 6_000.0;
/// E 的球的速度限制（从球那里出发、和数据从她出发的追踪弹同时到）。
pub const E_SPEED_MIN: f64 = 1_000.0;
pub const E_SPEED_MAX: f64 = 12_000.0;

fn on(x: &str) -> String {
    format!("league_orianna_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ORIANNA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_orianna.log");
        }
    }
    PathBuf::from("league_orianna.log")
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

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 从 `from` 朝 `to` 走 `step`：(新位置, 到了吗)。
pub fn toward(from: (f64, f64), to: (f64, f64), step: f64) -> ((f64, f64), bool) {
    let d = dist(from, to);
    if d <= step || d <= 0.0 {
        return (to, true);
    }
    ((from.0 + (to.0 - from.0) * step / d, from.1 + (to.1 - from.1) * step / d), false)
}

/// 球在哪。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Where {
    /// 在她身边。
    Home,
    /// Q 扔出去，正飞向落点。
    Flying { to: (f64, f64), speed: f64 },
    /// 停在地上。
    Lying,
    /// E 送出去，正追着队友。
    Sent { ally: usize, speed: f64 },
    /// 挂在队友身上。
    Riding { ally: usize },
    /// 正飞回她身边。
    Back,
}

impl Where {
    pub fn label(&self) -> &'static str {
        match self {
            Where::Home => "beside her",
            Where::Flying { .. } => "in the air",
            Where::Lying => "on the ground",
            Where::Sent { .. } => "on its way to an ally",
            Where::Riding { .. } => "on an ally",
            Where::Back => "flying back",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Ball {
    pub at: (f64, f64),
    pub w: Where,
}

/// 这一 tick 从数据看到的：她身上的 `home` / `b_ret`，她的位置，带着 `e_def` 的队友，球追着的那个队友在哪。
#[derive(Clone, Copy, Debug, Default)]
pub struct Seen {
    pub home: bool,
    pub ret: bool,
    pub me: (f64, f64),
    pub carrier: Option<usize>,
    pub ally_at: Option<(f64, f64)>,
}

impl Ball {
    pub fn new(at: (f64, f64)) -> Self {
        Ball { at, w: Where::Home }
    }

    /// 球走一 tick。
    pub fn step(&mut self, s: &Seen, b_back: f64) {
        if s.home {
            self.w = Where::Home;
            self.at = s.me;
            return;
        }
        match self.w {
            // home gone without a call of ours: it stays where it was (or flies back)
            Where::Home => self.w = if s.ret { Where::Back } else { Where::Lying },
            Where::Flying { to, speed } => {
                let (p, done) = toward(self.at, to, speed);
                self.at = p;
                if done {
                    self.w = if s.ret { Where::Back } else { Where::Lying };
                }
            }
            Where::Lying => {
                if s.ret {
                    self.w = Where::Back;
                }
            }
            Where::Sent { ally, speed } => match s.ally_at {
                Some(a) => {
                    let (p, done) = toward(self.at, a, speed);
                    self.at = p;
                    if done || s.carrier == Some(ally) {
                        self.at = a;
                        self.w = Where::Riding { ally };
                    }
                }
                None => self.w = Where::Lying,
            },
            Where::Riding { .. } => {
                if let Some(a) = s.ally_at {
                    self.at = a;
                }
                if s.ret {
                    self.w = Where::Back;
                }
            }
            Where::Back => self.at = toward(self.at, s.me, b_back).0,
        }
    }

    /// 球追着、挂着的队友。
    pub fn ally(&self) -> Option<usize> {
        match self.w {
            Where::Sent { ally, .. } | Where::Riding { ally } => Some(ally),
            _ => None,
        }
    }
}

/// 一个可以送球的友方英雄（或者她自己）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Mate {
    pub id: usize,
    /// 血量比例 0..1。
    pub hp: f64,
    /// 近一秒受到的伤害占最大生命的比例。
    pub focus: f64,
    /// `e_near` 以内的敌方英雄。
    pub foes: usize,
}

impl Mate {
    pub fn danger(&self) -> f64 {
        FOCUS_WEIGHT * self.focus + (1.0 - self.hp)
    }
}

/// 球送给谁：身边有敌方英雄的友方英雄里最危险的；她自己身边也有敌人、而且比他们都危险时留给自己（None）。
pub fn choose_ally(mates: &[Mate], me: &Mate) -> Option<usize> {
    let best = mates
        .iter()
        .filter(|m| m.foes >= 1)
        .max_by(|a, b| a.danger().partial_cmp(&b.danger()).unwrap_or(std::cmp::Ordering::Equal))?;
    if me.foes >= 1 && me.danger() >= best.danger() {
        return None;
    }
    Some(best.id)
}

/// R 打在魔抗 `mr` 的敌人身上还剩多少（`raw` × 100 / (100 + 魔抗)）。
pub fn after_mr(raw: usize, mr: usize) -> usize {
    raw * 100 / (100 + mr)
}

/// R 能打死他吗。
pub fn kills(hp: usize, raw: usize, mr: usize) -> bool {
    hp > 0 && hp <= after_mr(raw, mr)
}

// ===================== 小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn alive_at(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() {
        return None;
    }
    let (x, y) = e.pos();
    Some((x as f64, y as f64))
}

/// 某一队活着、能被选中的英雄：(id, 位置)。
fn champions(sim: &StableSim<'_>, team: usize, same: bool) -> Vec<(usize, (f64, f64))> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if (u.team() == team) != same || !u.is_alive() || !u.is_targetable() || !u.is_champion() {
            continue;
        }
        let (x, y) = u.pos();
        out.push((u.id(), (x as f64, y as f64)));
    }
    out
}

fn ux(v: f64) -> u64 {
    v.round().max(0.0) as u64
}

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

fn input_target(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

// ===================== 参数（英雄数据的 passive.params） =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// Q 的球飞多少 tick。
    pub q_travel: usize,
    /// E：球的速度、施放范围、队友身边多远算有敌人、路上的伤害（线长、宽、伤害、法强比例）。
    pub e_speed: usize,
    pub e_range: usize,
    pub e_near: usize,
    pub e_len: usize,
    pub e_w: usize,
    pub e_dmg: usize,
    pub e_dap: usize,
    /// 球飞回来的速度。
    pub b_back: usize,
    /// R 的伤害。
    pub r_dmg: usize,
    pub r_ap: usize,
    /// 带球者的护甲、魔抗（E 的被动；出生时挂上的「球在身边」也带着）。
    pub e_def: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params {
            q_travel: 18,
            e_speed: 3500,
            e_range: 75_000,
            e_near: 40_000,
            e_len: 60_000,
            e_w: 8000,
            e_dmg: 60,
            e_dap: 30,
            b_back: 4500,
            r_dmg: 250,
            r_ap: 100,
            e_def: 12,
        }
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
            "q_travel" => p.q_travel = v,
            "e_speed" => p.e_speed = v,
            "e_range" => p.e_range = v,
            "e_near" => p.e_near = v,
            "e_len" => p.e_len = v,
            "e_w" => p.e_w = v,
            "e_dmg" => p.e_dmg = v,
            "e_dap" => p.e_dap = v,
            "b_back" => p.b_back = v,
            "r_dmg" => p.r_dmg = v,
            "r_ap" => p.r_ap = v,
            "e_def" => p.e_def = v,
            _ => {}
        }
    }
    p
}

/// 每个奥莉安娜的参数（native effect 按施法者找）。
static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

// ===================== 每份模拟、每个奥莉安娜的记录 =====================

/// 每份模拟的奥莉安娜一个编号，出生时由被动挂在她身上（buff `league_orianna_sim:<编号>`，没有数值、没有画面）。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
const SIM_TAG: &str = "league_orianna_sim:";

/// The number the passive hung on her when she spawned in this sim (0: none).
pub fn sim_tag(names: impl Iterator<Item = String>) -> u64 {
    names.into_iter().find_map(|n| n.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())).unwrap_or(0)
}

fn sim_of(sim: &StableSim<'_>, me: usize) -> u64 {
    sim.get_entity(me).map_or(0, |e| sim_tag((0..e.buff_count()).filter_map(|i| e.buff_at(i))
        .map(|b| b.name().to_string())))
}

#[derive(Clone, Debug)]
struct Track {
    ball: Ball,
    /// 每个友方英雄（连她）：上一 tick 的血量、近一秒受到的伤害占最大生命的比例。
    hurt: HashMap<usize, (usize, f64)>,
    /// 这一 tick 选好的送球对象（同一 tick 每个队友都会来问一次，只算一遍）。
    pick: Option<(usize, Option<usize>)>,
}

static TRACKS: LazyLock<Mutex<HashMap<(u64, usize), Track>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// 球现在在哪（没有记录：在她身边）。
fn ball_at(sim: &StableSim<'_>, me: usize) -> Option<Ball> {
    TRACKS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim_of(sim, me), me)).map(|t| t.ball)
}

fn set_ball(sim: &StableSim<'_>, me: usize, ball: Ball) {
    if let Some(t) = TRACKS.lock().unwrap_or_else(|e| e.into_inner()).get_mut(&(sim_of(sim, me), me)) {
        t.ball = ball;
    }
}

/// 出发点：她身上有 `home` 就是她的位置，否则是记下的球。
fn start(sim: &StableSim<'_>, me: usize, her: (f64, f64)) -> (f64, f64, &'static str) {
    if has_buff(sim, me, &on("home")) {
        return (her.0, her.1, "beside her");
    }
    match ball_at(sim, me) {
        Some(b) => (b.at.0, b.at.1, b.w.label()),
        None => (her.0, her.1, "unknown (beside her)"),
    }
}

fn spawn(sim: &mut StableSim<'_>, me: usize, name: &str, effect: &str, spec: ProjectileSpawnV1) -> bool {
    let ok = sim.spawn_projectile(&on(name), &format!("{ID}:{effect}"), &spec);
    if !ok {
        if let Some(k) = counted("refused") {
            wlog(format!("{} spawn_projectile({name}) refused #{k}", head(sim, me)));
        }
    }
    ok
}

fn team_of(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| e.team())
}

// ===================== Q：球从它所在的位置飞出 =====================

struct Throw;

impl StableEffectType for Throw {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(target) = input_target(&input) else { return };
        let (Some(her), Some(to)) = (alive_at(sim, me), alive_at(sim, target)) else { return };
        let p = params_of(me);
        let (x, y, from_what) = start(sim, me, her);
        let from = (x, y);
        // the data's hidden lob lands q_travel ticks from now where the target stands: the picture arrives with it
        let speed = (dist(from, to) / p.q_travel.max(1) as f64).max(100.0);
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team: team_of(sim, me),
            x: ux(from.0),
            y: ux(from.1),
            radius: 1_000,
            speed: speed.round() as u64,
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: ux(to.0),
            target_y: ux(to.1),
            penetrate: true,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Position.code(),
            casting_target: CastingTargetV1::None.code(),
        };
        let shown = spawn(sim, me, "q_ball", "noop", spec);
        set_ball(sim, me, Ball { at: from, w: Where::Flying { to, speed } });
        if let Some(k) = counted("throw") {
            wlog(format!("{} THROW #{k} from {from_what} {} ({:.0} from her) -> {} at {}: {:.0} in {} ticks{}",
                         head(sim, me), pt(from), dist(from, her), who(sim, target), pt(to), dist(from, to), p.q_travel,
                         if shown { "" } else { " (no picture)" }));
        }
    }
}

// ===================== E：球从它所在的位置飞向队友 =====================

struct Send;

impl StableEffectType for Send {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(ally) = input_target(&input) else { return };
        let (Some(her), Some(to)) = (alive_at(sim, me), alive_at(sim, ally)) else { return };
        let p = params_of(me);
        let home = has_buff(sim, me, &on("home"));
        let (x, y, from_what) = start(sim, me, her);
        let from = (x, y);
        // the data's hidden homing leaves her at e_speed: this one leaves the ball and arrives with it
        let eta = (dist(her, to) / p.e_speed.max(1) as f64).max(1.0);
        let speed = (dist(from, to) / eta).clamp(E_SPEED_MIN, E_SPEED_MAX);
        let team = team_of(sim, me);
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team,
            x: ux(from.0),
            y: ux(from.1),
            radius: 1_000,
            speed: speed.round() as u64,
            move_kind: ProjectileMoveKindV1::Target.code(),
            target_id: ally,
            target_x: 0,
            target_y: 0,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::AllyChampion.code(),
        };
        let shown = spawn(sim, me, "e_ball", "noop", spec);
        // the enemies between the ball and him (the data's line from her runs only while the ball is beside her)
        let mut line = "";
        if !home && dist(from, to) > 1.0 {
            let d = dist(from, to);
            let reach = d.min(p.e_len as f64).max(1.0);
            let end = (from.0 + (to.0 - from.0) * reach / d, from.1 + (to.1 - from.1) * reach / d);
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team,
                x: ux(from.0),
                y: ux(from.1),
                radius: p.e_w as u64,
                speed: speed.round() as u64,
                move_kind: ProjectileMoveKindV1::Linear.code(),
                target_id: 0,
                target_x: ux(end.0),
                target_y: ux(end.1),
                penetrate: true,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::EnemyWithoutTower.code(),
            };
            line = if spawn(sim, me, "e_line", "e_hit", spec) { ", line from the ball" } else { ", line refused" };
        }
        set_ball(sim, me, Ball { at: from, w: Where::Sent { ally, speed } });
        if let Some(k) = counted("send") {
            wlog(format!("{} SEND #{k} from {from_what} {} ({:.0} from her) -> {} {:.0} away at {speed:.0}/tick{line}{}",
                         head(sim, me), pt(from), dist(from, her), who(sim, ally), dist(from, to),
                         if shown { "" } else { " (no picture)" }));
        }
    }
}

/// E 的球路过的敌人。
struct EHit;

impl StableEffectType for EHit {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(target) = input_target(&input) else { return };
        let Some((hp, max)) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        let p = params_of(me);
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let amount = p.e_dmg + p.e_dap * ap / 100;
        let dealt = sim.deal_damage_typed(me, target, amount, DamageTypeV1::Ap, AttackTypeV1::Skill);
        sim.play_view_effect(&on("e_hit"), me, &InputTargetV1::target(target), 0, 0, 0);
        if let Some(k) = counted("e_hit") {
            wlog(format!("{} E-HIT #{k} {} at {hp}/{max}: {amount} magic before resistance{}", head(sim, me),
                         who(sim, target), if dealt { "" } else { " (refused)" }));
        }
    }
}

/// E 给自己：球从原处飞回来（数据马上把它算回她身边）。
struct Back;

impl StableEffectType for Back {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some(her) = alive_at(sim, me) else { return };
        let (x, y, from_what) = start(sim, me, her);
        let from = (x, y);
        let far = dist(from, her);
        if far > BACK_SHOWN {
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team: team_of(sim, me),
                x: ux(from.0),
                y: ux(from.1),
                radius: 1_000,
                speed: BACK_SPEED as u64,
                move_kind: ProjectileMoveKindV1::Target.code(),
                target_id: me,
                target_x: 0,
                target_y: 0,
                penetrate: false,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::AllyOnlySelf.code(),
            };
            spawn(sim, me, "b_back", "noop", spec);
        }
        set_ball(sim, me, Ball::new(her));
        if let Some(k) = counted("back") {
            wlog(format!("{} BACK #{k} E on herself: the ball {from_what}, {far:.0} away", head(sim, me)));
        }
    }
}

// ===================== E 选队友 =====================

fn pick_for(sim: &StableSim<'_>, me: usize) -> Option<usize> {
    let tick = sim.tick();
    let key = (sim_of(sim, me), me);
    let mut tracks = TRACKS.lock().unwrap_or_else(|e| e.into_inner());
    let track = tracks.get_mut(&key)?;
    if let Some((t, id)) = track.pick {
        if t == tick {
            return id;
        }
    }
    let p = params_of(me);
    let her = alive_at(sim, me)?;
    let team = sim.get_entity(me)?.team();
    let foes = champions(sim, team, false);
    let mate = |id: usize, at: (f64, f64)| {
        let (hp, max) = sim.get_entity(id).map_or((0, 1), |e| e.hp());
        Mate {
            id,
            hp: hp as f64 / max.max(1) as f64,
            focus: track.hurt.get(&id).map_or(0.0, |h| h.1),
            foes: foes.iter().filter(|f| dist(at, f.1) <= p.e_near as f64).count(),
        }
    };
    let mates: Vec<Mate> = champions(sim, team, true)
        .into_iter()
        .filter(|a| a.0 != me && dist(her, a.1) <= p.e_range as f64)
        .map(|a| mate(a.0, a.1))
        .collect();
    let mine = mate(me, her);
    let id = choose_ally(&mates, &mine);
    track.pick = Some((tick, id));
    drop(tracks);
    match id.and_then(|id| mates.iter().find(|m| m.id == id)) {
        Some(m) => {
            if let Some(k) = counted("pick") {
                wlog(format!("{} PICK #{k} -> {}: hp {:.0}%, took {:.0}% of his health in the last second, {} enemy \
                              champions near (her: hp {:.0}%, {:.0}%, {}; {} allies in range)", head(sim, me),
                             who(sim, m.id), m.hp * 100.0, m.focus * 100.0, m.foes, mine.hp * 100.0,
                             mine.focus * 100.0, mine.foes, mates.len()));
            }
        }
        None => {
            if let Some(k) = counted("keep") {
                wlog(format!("{} PICK #{k} herself: hp {:.0}%, took {:.0}%, {} enemy champions near; {} allies in \
                              range, {} with an enemy near", head(sim, me), mine.hp * 100.0, mine.focus * 100.0,
                             mine.foes, mates.len(), mates.iter().filter(|m| m.foes >= 1).count()));
            }
        }
    }
    id
}

struct Pick;

impl StableEffectType for Pick {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(ally) = input_target(&input) else { return };
        if pick_for(sim, me) == Some(ally) {
            sim.add_buff(me, &BuffV1::timed(&on("e_this"), 2));
        }
    }
}

// ===================== R 读血量 =====================

struct Kill;

impl StableEffectType for Kill {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(target) = input_target(&input) else { return };
        let Some((hp, max, mr)) = sim.get_entity(target).filter(|e| e.is_alive())
            .map(|e| (e.hp().0, e.hp().1, e.stat().magic_resistance)) else { return };
        let p = params_of(me);
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let raw = p.r_dmg + p.r_ap * ap / 100;
        if !kills(hp, raw, mr) {
            // R is armed and looking (the data asks only then): the first calls show it in the log
            if let Some(k) = counted("armed") {
                if k <= 20 {
                    wlog(format!("{} R-ARMED #{k} {} near the Ball at {hp}/{max}: the shockwave would deal {}, no kill",
                                 head(sim, me), who(sim, target), after_mr(raw, mr)));
                }
            }
            return;
        }
        sim.add_buff(me, &BuffV1::timed(&on("c2"), 3));
        if let Some(k) = counted("kill") {
            wlog(format!("{} KILL #{k} {} at {hp}/{max}, magic resistance {mr}: the shockwave deals {} ({raw} before \
                          resistance) -> R goes", head(sim, me), who(sim, target), after_mr(raw, mr)));
        }
    }
}

/// 每次 E 真正放出（日志用）：控制器在不在跑、球在哪、离她最近的敌方英雄多远。
struct ECast;

impl StableEffectType for ECast {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some(her) = alive_at(sim, me) else { return };
        let team = team_of(sim, me);
        let near = champions(sim, team, false).iter().map(|f| dist(her, f.1)).fold(f64::INFINITY, f64::min);
        let polling = has_buff(sim, me, &on("polling"));
        let (_, _, ball) = start(sim, me, her);
        if let Some(k) = counted("e_cast") {
            wlog(format!("{} E-CAST #{k}: controller {}, the ball {ball}, nearest enemy champion {near:.0} away",
                         head(sim, me), if polling { "running" } else { "not running (shield on herself)" }));
        }
    }
}

/// E 走到「送给队友」这一步（日志用）：范围内的队友、其中身边有敌方英雄的。
struct ETry;

impl StableEffectType for ETry {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some(her) = alive_at(sim, me) else { return };
        let p = params_of(me);
        let team = team_of(sim, me);
        let foes = champions(sim, team, false);
        let mates: Vec<_> = champions(sim, team, true).into_iter()
            .filter(|a| a.0 != me && dist(her, a.1) <= p.e_range as f64).collect();
        let fighting = mates.iter().filter(|a| foes.iter().any(|f| dist(a.1, f.1) <= p.e_near as f64)).count();
        if let Some(k) = counted("e_try") {
            wlog(format!("{} E-TRY #{k}: {} allies within {}, {fighting} with an enemy champion within {}",
                         head(sim, me), mates.len(), p.e_range, p.e_near));
        }
    }
}

/// 只画画面的投射物（Q / E 的球、飞回来的球）碰到东西时什么都不做。
struct Noop;

impl StableEffectType for Noop {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 被动：记下球在哪、队友受到的伤害 =====================

#[derive(Clone, Default)]
struct Keeper {
    p: Params,
    /// This sim's number (`SIM_TAG`), drawn at her first spawn.
    sim_no: u64,
}

impl StablePassive for Keeper {
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
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        // the Ball beside her from the spawn: the data hangs `home` at her first action of a life (it has no spawn
        // hook), so she walked to her lane and back from the fountain without it (the user: 「一开始走路的时候怎么不带着
        // 球？」); the same buff the data's is (its view_buffs picture, E's passive armour and magic resistance)
        let mut home = BuffV1::named(&on("home"));
        home.defence = self.p.e_def as i32;
        home.magic_resistance = self.p.e_def as i32;
        sim.entity_remove_buff(me, &on("home"));
        sim.add_buff(me, &home);
        let at = alive_at(sim, me).unwrap_or_default();
        let mut tracks = TRACKS.lock().unwrap_or_else(|e| e.into_inner());
        if tracks.len() > 4096 {
            tracks.clear(); // finished sims
        }
        tracks.insert((self.sim_no, me), Track { ball: Ball::new(at), hurt: HashMap::new(), pick: None });
        drop(tracks);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Orianna (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(her) = alive_at(sim, me) else { return };
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let mut seen = Seen {
            home: has_buff(sim, me, &on("home")),
            ret: has_buff(sim, me, &on("b_ret")),
            me: her,
            ..Seen::default()
        };
        let def = on("e_def");
        let mut hp_now = Vec::new();
        for (id, _) in champions(sim, team, true) {
            let Some(e) = sim.get_entity(id) else { continue };
            hp_now.push((id, e.hp()));
            if id != me && (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == def) {
                seen.carrier = Some(id);
            }
        }
        let mut tracks = TRACKS.lock().unwrap_or_else(|e| e.into_inner());
        let Some(track) = tracks.get_mut(&(self.sim_no, me)) else { return };
        if let Some(ally) = track.ball.ally() {
            seen.ally_at = alive_at(sim, ally);
        }
        track.ball.step(&seen, self.p.b_back as f64);
        // damage taken by each ally (and her) over about the last second, as a share of his maximum health
        let mut hurt = HashMap::with_capacity(hp_now.len());
        for (id, (hp, max)) in hp_now {
            let (last, f) = track.hurt.get(&id).copied().unwrap_or((hp, 0.0));
            let lost = last.saturating_sub(hp) as f64 / max.max(1) as f64;
            hurt.insert(id, (hp, f * FOCUS_DECAY + lost));
        }
        track.hurt = hurt;
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        // she is back with the ball beside her (death clears the data's flags; init raises home again)
        for (key, t) in TRACKS.lock().unwrap_or_else(|e| e.into_inner()).iter_mut() {
            if key.0 == self.sim_no {
                t.ball.w = Where::Home;
                t.pick = None;
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
        "=== {ID} v{VERSION} (Orianna: the Ball flies from where it is, Command: Protect to the ally in danger, Command: Shockwave for two champions or a kill) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:ball"), Keeper::default());
    module.add_native_effect(format!("{ID}:q"), Throw);
    module.add_native_effect(format!("{ID}:e"), Send);
    module.add_native_effect(format!("{ID}:e_hit"), EHit);
    module.add_native_effect(format!("{ID}:back"), Back);
    module.add_native_effect(format!("{ID}:e_pick"), Pick);
    module.add_native_effect(format!("{ID}:r_kill"), Kill);
    module.add_native_effect(format!("{ID}:noop"), Noop);
    module.add_native_effect(format!("{ID}:e_cast"), ECast);
    module.add_native_effect(format!("{ID}:e_try"), ETry);
    host.log(LogLevel::Info, "league_orianna loaded (the Ball from where it is, Protect to the ally in danger, Shockwave for a kill).");
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

    fn seen(home: bool, ret: bool, me: (f64, f64)) -> Seen {
        Seen { home, ret, me, ..Seen::default() }
    }

    #[test]
    fn a_thrown_ball_lands_and_stays() {
        let mut b = Ball { at: (0.0, 0.0), w: Where::Flying { to: (30_000.0, 0.0), speed: 10_000.0 } };
        b.step(&seen(false, false, (0.0, 0.0)), 4500.0);
        assert_eq!(b.at, (10_000.0, 0.0));
        b.step(&seen(false, false, (0.0, 0.0)), 4500.0);
        b.step(&seen(false, false, (0.0, 0.0)), 4500.0);
        assert_eq!((b.at, b.w), ((30_000.0, 0.0), Where::Lying));
        // she walks away: it stays
        b.step(&seen(false, false, (-50_000.0, 0.0)), 4500.0);
        assert_eq!(b.at, (30_000.0, 0.0));
        // leash: it flies back, then home
        b.step(&seen(false, true, (0.0, 0.0)), 4500.0);
        assert_eq!(b.w, Where::Back);
        b.step(&seen(false, true, (0.0, 0.0)), 4500.0);
        assert_eq!(b.at, (25_500.0, 0.0));
        b.step(&seen(true, false, (1.0, 2.0)), 4500.0);
        assert_eq!((b.at, b.w), ((1.0, 2.0), Where::Home));
    }

    #[test]
    fn a_sent_ball_rides_its_ally() {
        let mut b = Ball { at: (0.0, 0.0), w: Where::Sent { ally: 7, speed: 4000.0 } };
        let s = Seen { ally_at: Some((10_000.0, 0.0)), ..seen(false, false, (0.0, 0.0)) };
        b.step(&s, 4500.0);
        assert_eq!(b.at, (4000.0, 0.0));
        // his e_def shows: on him at once
        b.step(&Seen { carrier: Some(7), ..s }, 4500.0);
        assert_eq!((b.at, b.w), ((10_000.0, 0.0), Where::Riding { ally: 7 }));
        // it follows him
        b.step(&Seen { ally_at: Some((20_000.0, 5.0)), ..s }, 4500.0);
        assert_eq!(b.at, (20_000.0, 5.0));
        // he dies on the way: it lies there
        let mut b = Ball { at: (0.0, 0.0), w: Where::Sent { ally: 7, speed: 4000.0 } };
        b.step(&seen(false, false, (0.0, 0.0)), 4500.0);
        assert_eq!(b.w, Where::Lying);
    }

    fn mate(id: usize, hp: f64, focus: f64, foes: usize) -> Mate {
        Mate { id, hp, focus, foes }
    }

    #[test]
    fn the_ally_in_danger() {
        let me = mate(1, 1.0, 0.0, 0);
        // nobody near an enemy: none (the data shields her)
        assert_eq!(choose_ally(&[mate(2, 0.2, 0.0, 0)], &me), None);
        // the one taking the most damage beats the lower one standing back
        let m = [mate(2, 0.5, 0.0, 1), mate(3, 0.7, 0.3, 2)];
        assert_eq!(choose_ally(&m, &me), Some(3));
        // she is in more danger herself: she keeps it
        assert_eq!(choose_ally(&m, &mate(1, 0.2, 0.3, 1)), None);
        // she is hurt but nobody is on her: the ally
        assert_eq!(choose_ally(&m, &mate(1, 0.2, 0.3, 0)), Some(3));
    }

    #[test]
    fn the_shockwave_kills() {
        assert_eq!(after_mr(500, 25), 400);
        assert!(kills(400, 500, 25));
        assert!(!kills(401, 500, 25));
        assert!(!kills(0, 500, 25));
    }

    #[test]
    fn towards() {
        assert_eq!(toward((0.0, 0.0), (3.0, 4.0), 10.0), ((3.0, 4.0), true));
        assert_eq!(toward((0.0, 0.0), (30.0, 40.0), 5.0), ((3.0, 4.0), false));
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"b_back":4500,"e_dap":30,"e_dmg":60,"e_len":60000,"e_near":40000,"e_range":75000,
                                 "e_speed":3500,"e_w":8000,"q_travel":18,"r_ap":100,"r_dmg":250,"e_def":12}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_orianna.py");
        let src = std::fs::read_to_string(path).expect("build_orianna.py");
        let d = Params::default();
        for (key, v) in [("q_travel", d.q_travel), ("e_speed", d.e_speed), ("e_range", d.e_range), ("e_near", d.e_near),
                         ("e_len", d.e_len), ("e_w", d.e_w), ("e_dmg", d.e_dmg), ("e_dap", d.e_dap),
                         ("b_back", d.b_back), ("r_dmg", d.r_dmg), ("r_ap", d.r_ap), ("e_def", d.e_def)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_orianna.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["home", "b_ret", "e_def", "e_this", "c2", "q_ball", "e_ball", "e_line", "b_back"] {
            assert!(on(x).len() <= BUFF_NAME_CAP);
        }
        assert!(format!("{SIM_TAG}{}", u64::MAX).len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn each_sim_finds_its_own_number() {
        let names = |v: &[&str]| v.iter().map(|s| s.to_string()).collect::<Vec<_>>().into_iter();
        assert_eq!(sim_tag(names(&["league_orianna_home", "league_orianna_sim:7"])), 7);
        assert_eq!(sim_tag(names(&["league_orianna_home"])), 0);
    }
}
