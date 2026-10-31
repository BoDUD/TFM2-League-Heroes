//! 佛耶戈附加包：被动「君命已决」照英雄联盟做——附身他参与击杀的英雄，**整个身体变成那个英雄**，用那类英雄的招式打。
//!
//! 主包是纯数据：数据看不到「谁死了」，只能靠一个「被打过的英雄身上的计时器断了」的近似（一个窗口里打过两个英雄，只看得到最后
//! 死的那个），附身后外形还是佛耶戈，只加一圈亡魂黑雾。`mod.override_info` 把主包的佛耶戈换成 `override/` 里的副本
//! （`make_override.py` 从 tools/kit/build_viego.py 的 native=1 生成）：他打中英雄时在对方身上挂 `league_viego_mark`
//! （p_win tick），被动 `league_viego_soul:possess` 每 tick：
//!
//! - **记功**：哪些敌方英雄身上有他的标记、最后一次看到是哪一 tick；
//! - **灵魂**：有标记的敌方英雄由活变死 = 他参与了击杀，尸体那里留下一个灵魂 soul_t tick；他活着、在 soul_r 以内就**附身**，soul_dash 以内就冲过去（0.1.5）
//!   （英雄联盟要去点那个灵魂；离得近就马上附身）；
//! - **附身** p_t tick：身上挂 `league_viego_soul:<英雄 id>`（给显示钩子看：整个身体画成那个英雄，src/view.rs）、
//!   `league_viego_soul_<类别>`（数据副本的普攻 / Q / W 按它换成五套招式之一：近战、射手、法师、辅助、刺客，类别按英雄 id 查
//!   src/souls.rs，查不到按攻击距离猜）、`league_viego_p_on`（借来的攻击 / 攻速 / 移速；远程三类再加 s_range 25000 攻击距离——2026-10-21 起曾是 0：游戏 0.6.x 的 AI 被原生加的攻击距离
//!   拉到远处站着不打人，「佛耶戈有bug 会无限期停在原地不动」；0.7.0 官方修了「mod 改了射程后来回走、不按改过的射程攻击」，恢复）、
//!   `league_viego_p_safe`（p_inv tick 无敌、免控）、一下技能冷却（p_skill：Q、W 刷新；大招按 p_ult）、回血，
//!   再挂 `league_viego_p_go` 让数据在他下一个动作里播吸魂的画面、动作和声音；
//! - **结束**：时间到、他阵亡、或数据的大招拿掉了 `league_viego_p_on`（英雄联盟：放 R 回到本体）——拿掉外形和类别 buff，
//!   挂 `league_viego_p_off` 让数据播回到本体的雾。
//!
//! - **破败之雾**（0.2.0，用户 2026-10-20：「佛耶哥的二技能被ai当成点控用了，没法利用破败之雾抓人。把开雾写成一个有内置cd的
//!   靠近敌方英雄一定范围自动触发的隐身技能」）：副本的 W 只剩千载幽咽（冲刺吐魂眩晕），黑雾由被动自己升起——看得见的敌方
//!   英雄进到 `e_trig` 以内、离上次 `e_cd` tick 以上、没在附身：`league_viego_e_on`（e_t tick，移速 +e_ms%、攻速 +e_as%，
//!   同数据原来的雾）、隐身 e_hide tick（`entity_set_invisible`）、黑雾的画面和声音（`league_viego_e_zone`、`_e`、`_e_mist`）。
//!
//! 原生代码只做判断和 buff；画面、伤害在数据里。整身外形在游戏 0.6.4 起的 Windows 版上（显示钩子的地址由 game_places 运行时找），别的版本只有数据的黑雾。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_viego_soul.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

mod souls;
pub mod stuck;
pub mod view;

const ID: &str = "league_viego_soul";
/// 主包里佛耶戈的 id。
pub const HERO: &str = "league_viego";
/// 数据副本挂在被打中的英雄身上的标记。
pub const MARK: &str = "league_viego_mark";
/// 给显示钩子的外形标记：`league_viego_soul:<英雄 id>`。
pub const LOOK: &str = "league_viego_soul:";
pub const ON: &str = "league_viego_p_on";
pub const SAFE: &str = "league_viego_p_safe";
pub const CDR: &str = "league_viego_p_cdr";
pub const GO: &str = "league_viego_p_go";
pub const OFF: &str = "league_viego_p_off";
/// 每份模拟的佛耶戈一个编号（`league_viego_sim:<编号>`，没有数值、没有画面）：2v2 这类对局来历都是「未知」，游戏同时跑整轮
/// 好几场、每场好几遍，日志里分不清屏幕放的是哪一遍（用户：「画面根本没附身啊」，别的模拟里附身 PPU 英雄很多次）；屏幕上
/// 的佛耶戈身上带着编号，显示钩子记下它，这份模拟的每一行（出生时的对阵名单、灵魂、附身）就对得上了。
pub const SIM_TAG: &str = "league_viego_sim:";
static NEXT_SIM: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(1);

/// `MIST` lines: every one on screen, the server's presims the first `MIST_FIRST`, then every `MIST_EVERY`-th - a count
/// per Viego (40, then every 25th) logged about every mist of every presim (2026-10-30: about 1 MB a launch).
static MISTS: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
const MIST_FIRST: usize = 40;
const MIST_EVERY: usize = 200;

fn mist_logged(shown: bool) -> bool {
    let n = MISTS.fetch_add(1, std::sync::atomic::Ordering::Relaxed) + 1;
    shown || n <= MIST_FIRST || n % MIST_EVERY == 0
}
/// 五套招式（数据副本里 `league_viego_soul_<类别>`）。
pub const CATS: [&str; 5] = ["melee", "range", "mage", "util", "assassin"];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VIEGO_SOUL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_viego_soul.log");
        }
    }
    PathBuf::from("league_viego_soul.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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
    let t = sim.tick();
    format!("[{kind} m={} s={}] t={t} ({}:{:02}) #{id}", m(o.match_id), m(o.set_index), t / 3600, t / 60 % 60)
}

/// The sims the screen replays (the client's own match view, spectating, a replay) - not the server's presims: the
/// screen draws their possessions (view::note_possess).
fn on_screen(sim: &StableSim<'_>) -> Option<(u64, u64)> {
    let o = sim.sim_origin().unwrap_or_default();
    matches!(SimOriginKindV1::from_code(o.kind),
        Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay))
        .then_some((o.match_id, o.set_index))
}

// ===================== 计算 =====================

/// 从被动参数（整数 JSON，如 `{"p_t":600,"soul_r":35000}`）读一个值。
pub fn param(json: &str, key: &str) -> Option<u32> {
    let at = json.find(&format!("\"{key}\""))?;
    let rest = json[at + key.len() + 2..].trim_start().strip_prefix(':')?.trim_start();
    let end = rest.find(|c: char| !c.is_ascii_digit()).unwrap_or(rest.len());
    rest[..end].parse().ok()
}

/// 英雄 id → 五套招式之一：查表（本包英雄和原版英雄），查不到的（别的 mod）按攻击距离：35000 以上算射手。
pub fn category(name: &str, range: Option<u32>) -> &'static str {
    match souls::SOULS.binary_search_by(|s| s.0.cmp(name)) {
        Ok(i) => souls::SOULS[i].1,
        Err(_) if range.unwrap_or(0) >= 35000 => "range",
        Err(_) => "melee",
    }
}

/// 远程的三类（射手、法师、辅助）附身时加攻击距离。
pub fn ranged(cat: &str) -> bool {
    matches!(cat, "range" | "mage" | "util")
}

fn dist(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0.abs_diff(b.0) as f64;
    let dy = a.1.abs_diff(b.1) as f64;
    (dx * dx + dy * dy).sqrt() as u64
}

fn buff_names(sim: &StableSim<'_>, id: usize) -> Vec<String> {
    sim.get_entity(id).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect()
    })
}

/// His dash onto a soul, a tick (League's possession leap).
const DASH_SPEED: f64 = 4000.0;

/// A forced move onto `to` (league_aatrox_chain's), ending exactly there; the ticks it takes.
fn force_move(sim: &mut StableSim<'_>, id: usize, from: (f64, f64), to: (f64, f64), speed: f64) -> usize {
    let d = ((to.0 - from.0).powi(2) + (to.1 - from.1).powi(2)).sqrt();
    if d < 1.0 {
        return 0;
    }
    let ticks = (d / speed).ceil().max(1.0);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (to.0 - from.0).round() as i64;
    cc.dy = (to.1 - from.1).round() as i64;
    cc.speed = (d / ticks).ceil() as u64;
    sim.apply_cc(id, &cc);
    ticks as usize
}

fn timed(name: &str, ticks: u32) -> BuffV1 {
    let mut b = BuffV1::named(name);
    b.duration_kind = BuffDurationV1::Time.code();
    b.duration_tick = ticks as usize;
    b
}

// ===================== 被动 =====================

#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub p_t: u32,
    pub p_inv: u32,
    pub p_heal: u32,
    pub p_heal_ratio: u32,
    pub p_ad: u32,
    pub p_as: u32,
    pub p_ms: u32,
    pub p_skill: u32,
    pub p_ult: u32,
    pub p_win: u32,
    pub soul_r: u32,
    pub soul_t: u32,
    pub s_range: u32,
    pub soul_dash: u32,
    /// the mist (0.2.0): its buff's ticks, move / attack speed %, the pause between two, the reach that raises it,
    /// the ticks hidden
    pub e_t: u32,
    pub e_ms: u32,
    pub e_as: u32,
    pub e_cd: u32,
    pub e_trig: u32,
    pub e_hide: u32,
}

impl Default for Params {
    fn default() -> Self {
        Params { p_t: 600, p_inv: 60, p_heal: 60, p_heal_ratio: 50, p_ad: 25, p_as: 30, p_ms: 15, p_skill: 10000,
                 p_ult: 0, p_win: 180, soul_r: 35000, soul_t: 480, s_range: 25000,
                 soul_dash: 90000, e_t: 300, e_ms: 30, e_as: 40, e_cd: 600, e_trig: 90000, e_hide: 120 }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct Soul {
    pub name: String,
    pub cat: &'static str,
    pub pos: (u64, u64),
    pub until: usize,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Possession {
    pub name: String,
    pub cat: &'static str,
    pub until: usize,
}

#[derive(Clone, Default)]
pub struct Possess {
    pub p: Params,
    /// 敌方英雄 → (最后一次看到他的标记的 tick, 上一 tick 活着)。
    pub marked: Vec<(usize, usize, bool)>,
    pub souls: Vec<Soul>,
    pub on: Option<Possession>,
    pub was_alive: bool,
    /// His unit, set by every update (`on_dead` is given only the player).
    pub me: Option<usize>,
    /// The first update has run (a sim the screen replays is noted for the display hook then).
    pub started: bool,
    /// No new dash onto a soul before this tick (the last one's length).
    pub dash_until: usize,
    /// What the sim showed of the possession's data side (p_go taken, shape on), for the log: 0.1.6.
    pub seen: (bool, bool),
    /// This sim's number (`SIM_TAG`), drawn at the first update.
    pub sim_no: u64,
    /// The mist may rise again from this tick (0.2.0), and how many times it rose.
    pub mist_at: usize,
    pub mists: usize,
    /// The stuck-dash guard (0.2.13, [`stuck`]) and his attack / Q / W / R cooldowns last tick (a rise = he acted).
    pub stuck: stuck::Watch,
    pub cds: [usize; 4],
}

/// 破败之雾升不升：没在附身、冷却过了、最近的看得见的敌方英雄在 `trig` 以内（`nearest` = 距离）。
pub fn mist_due(possessed: bool, now: usize, mist_at: usize, nearest: Option<u64>, trig: u64) -> bool {
    !possessed && now >= mist_at && nearest.is_some_and(|d| d <= trig)
}

impl Possess {
    /// 破败之雾（0.2.0）：敌方英雄靠近就自己升起，每 e_cd tick 最多一次。
    fn mist(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, mpos: (u64, u64)) {
        let now = sim.tick();
        let nearest = (0..sim.champion_count())
            .filter_map(|i| sim.get_entity(sim.champion_id_at(i)))
            .filter(|c| c.team() != team && c.is_alive() && c.is_targetable() && sim.is_visible(team, c.id()))
            .map(|c| dist(c.pos(), mpos))
            .min();
        if !mist_due(self.on.is_some(), now, self.mist_at, nearest, self.p.e_trig as u64) {
            return;
        }
        let p = self.p.clone();
        let mut on = timed("league_viego_e_on", p.e_t);
        on.move_speed_mult = p.e_ms as i32;
        on.attack_speed_mult = p.e_as as i32;
        sim.entity_remove_buff(me, "league_viego_e_on");
        sim.add_buff(me, &on);
        let hidden = sim.entity_set_invisible(me, p.e_hide as usize);
        let here = InputTargetV1::pos(mpos.0, mpos.1);
        sim.play_view_effect("league_viego_e_zone", me, &here, 0, 0, 0);
        let on_me = InputTargetV1::target(me);
        for s in ["league_viego_e", "league_viego_e_mist", "league_viego_vo_e"] {
            sim.play_sfx(s, me, &on_me);
        }
        self.mist_at = now + p.e_cd as usize;
        self.mists += 1;
        if mist_logged(on_screen(sim).is_some()) {
            wlog(format!("{} MIST #{}: an enemy champion {} away (reach {}), +{}% move / +{}% attack speed {} ticks, hidden {} ticks{}",
                head(sim, me), self.mists, nearest.unwrap_or(0), p.e_trig, p.e_ms, p.e_as, p.e_t, p.e_hide,
                if hidden { "" } else { " (entity_set_invisible refused)" }));
        }
    }

    /// 一个有标记的敌方英雄阵亡（`died` tick，最后一次看到标记在 `seen`）：算不算他的功劳。
    pub fn credited(&self, seen: usize, died: usize) -> bool {
        died <= seen + 3 || died - seen <= self.p.p_win as usize
    }

    /// 灵魂里离他最近、在 soul_r 以内的那个。
    pub fn reachable(&self, me: (u64, u64)) -> Option<usize> {
        self.souls
            .iter()
            .enumerate()
            .filter(|(_, s)| dist(s.pos, me) <= self.p.soul_r as u64)
            .min_by_key(|(_, s)| dist(s.pos, me))
            .map(|(i, _)| i)
    }

    /// The nearest soul out of soul_r but within soul_dash: the one he dashes onto.
    pub fn dashable(&self, me: (u64, u64)) -> Option<&Soul> {
        self.souls
            .iter()
            .filter(|s| (self.p.soul_r as u64..=self.p.soul_dash as u64).contains(&dist(s.pos, me)))
            .min_by_key(|s| dist(s.pos, me))
    }

    fn end(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        let Some(on) = self.on.take() else { return };
        sim.entity_remove_buff(me, &format!("{LOOK}{}", on.name));
        sim.entity_remove_buff(me, &format!("league_viego_soul_{}", on.cat));
        sim.entity_remove_buff(me, ON);
        sim.entity_remove_buff(me, SAFE);
        if why != "dead" {
            sim.entity_remove_buff(me, OFF);
            sim.add_buff(me, &timed(OFF, 600));
        }
        wlog(format!("{} END possession of {} ({why})", head(sim, me), on.name));
        if let Some((m, s)) = on_screen(sim) {
            view::note_end(m, s, me, sim.tick());
        }
    }

    fn possess(&mut self, sim: &mut StableSim<'_>, me: usize, soul: Soul) {
        if self.on.is_some() {
            self.end(sim, me, "a new soul");
            sim.entity_remove_buff(me, OFF);
        }
        let p = self.p.clone();
        sim.add_buff(me, &timed(&format!("{LOOK}{}", soul.name), p.p_t));
        sim.add_buff(me, &timed(&format!("league_viego_soul_{}", soul.cat), p.p_t));
        let mut on = timed(ON, p.p_t);
        on.attack_mult = p.p_ad as i32;
        on.attack_speed_mult = p.p_as as i32;
        on.move_speed_mult = p.p_ms as i32;
        if ranged(soul.cat) && p.s_range > 0 {
            on.range = p.s_range as usize;
        }
        sim.entity_remove_buff(me, ON);
        sim.add_buff(me, &on);
        let mut safe = timed(SAFE, p.p_inv);
        safe.damaged_reduce = 100;
        safe.cc_immune = true;
        sim.entity_remove_buff(me, SAFE);
        sim.add_buff(me, &safe);
        let mut cdr = timed(CDR, 2);
        cdr.skill_cooldown_mult = p.p_skill as i32;
        cdr.ult_cooldown_mult = p.p_ult as i32 - p.p_skill as i32;
        sim.add_buff(me, &cdr);
        sim.entity_remove_buff(me, GO);
        sim.add_buff(me, &timed(GO, 600));
        let atk = sim.get_entity(me).map_or(0, |e| e.stat().attack.max(0) as usize);
        let heal = p.p_heal as usize + atk * p.p_heal_ratio as usize / 100;
        sim.heal(me, me, heal);
        wlog(format!("{} POSSESS {} ({}) for {} ticks, heal {heal}", head(sim, me), soul.name, soul.cat, p.p_t));
        if let Some((m, s)) = on_screen(sim) {
            view::note_possess(m, s, me, sim.tick(), &soul.name);
        }
        self.on = Some(Possession { name: soul.name, cat: soul.cat, until: sim.tick() + p.p_t as usize });
        self.seen = (false, false);
    }
}

impl Possess {
    /// Frees him when a dash or a cast never ends, or he stands by an enemy doing nothing ([`stuck`]): his crowd control
    /// cleared, a [`stuck::KICK`]-tick knock-up (what the players saw free him), and a `STUCK` line.
    fn unstick(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let has = |k: CcKindV1| (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| c.kind == k.code()));
        let cds = [SkillSlotV1::Attack, SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult]
            .map(|s| e.cooldown(s).map_or(0, |c| c.remaining));
        let acted = cds.iter().zip(self.cds.iter()).any(|(now, was)| now > was);
        self.cds = cds;
        let (team, pos, alive) = (e.team(), e.pos(), e.is_alive());
        // a held body that is no stuck cast: Guardian Angel's stasis (a 241-tick Animation) or a banish (Mordekaiser's
        // realm) - the guard fired on every revive and cut it short, and lifted the realm's lock (the 2026-10-30 log)
        let held = !e.is_targetable()
            || (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == stuck::STASIS);
        let (force, anim) = (has(CcKindV1::ForceMove), has(CcKindV1::Animation) && !held);
        let ccs: Vec<String> = (0..e.cc_count())
            .filter_map(|i| e.cc_at(i))
            .map(|c| format!("{:?} {}", CcKindV1::from_code(c.kind), c.tick))
            .collect();
        let foe_near = (0..sim.champion_count()).filter_map(|i| sim.get_entity(sim.champion_id_at(i))).any(|c| {
            c.team() != team && c.is_alive() && c.is_targetable() && dist(c.pos(), pos) as f64 <= stuck::NEAR
        });
        // held, he stands still by design: no Still either (2026-11-01 log: Still(300) during the stasis next to an enemy
        // cut a revive 178 ticks short, as the Anim path did before 0.2.34)
        let obs = stuck::Obs { alive, pos, force, anim, acted, foe_near: foe_near && !held };
        let Some(why) = self.stuck.step(obs) else { return };
        let cleared = sim.entity_clear_cc(me);
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::Airborne, stuck::KICK));
        wlog(format!(
            "{} STUCK {why:?} at {pos:?}: crowd control [{}] - {cleared} cleared, knocked up {} ticks; cooldowns {cds:?};              buffs [{}]",
            head(sim, me), ccs.join(", "), stuck::KICK, buff_names(sim, me).join(", ")
        ));
    }
}

impl StablePassive for Possess {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let d = Params::default();
        let g = |k: &str, v: u32| param(params_json, k).unwrap_or(v);
        self.p = Params {
            p_t: g("p_t", d.p_t).max(1),
            p_inv: g("p_inv", d.p_inv),
            p_heal: g("p_heal", d.p_heal),
            p_heal_ratio: g("p_heal_ratio", d.p_heal_ratio),
            p_ad: g("p_ad", d.p_ad),
            p_as: g("p_as", d.p_as),
            p_ms: g("p_ms", d.p_ms),
            p_skill: g("p_skill", d.p_skill),
            p_ult: g("p_ult", d.p_ult),
            p_win: g("p_win", d.p_win),
            soul_r: g("soul_r", d.soul_r),
            soul_t: g("soul_t", d.soul_t),
            s_range: g("s_range", d.s_range),
            soul_dash: g("soul_dash", d.soul_dash),
            e_t: g("e_t", d.e_t),
            e_ms: g("e_ms", d.e_ms),
            e_as: g("e_as", d.e_as),
            e_cd: g("e_cd", d.e_cd),
            e_trig: g("e_trig", d.e_trig),
            e_hide: g("e_hide", d.e_hide),
        };
    }

    /// His death ends a possession at once (0.2.41, the 2026-11-01 logs: 25 possessions outlived his death and ended
    /// "(time)" on the respawned Viego thousands of ticks later, with the return-to-body mist - a dead champion's update
    /// does not run, so the `alive` change below never saw it).
    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        if let Some(me) = self.me {
            self.end(sim, me, "dead");
        }
        self.souls.clear();
        self.was_alive = false;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        self.me = Some(me);
        self.unstick(sim, me);
        let now = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, team, mpos) = (e.is_alive(), e.team(), e.pos());
        if !self.started {
            self.started = true;
            if self.sim_no == 0 {
                self.sim_no = NEXT_SIM.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
            }
            if let Some((m, s)) = on_screen(sim) {
                view::note_view(m, s);
                wlog(format!("{} the passive is on (team {team}); this sim is the one the screen replays", head(sim, me)));
            }
            let lineup: Vec<String> = (0..sim.champion_count())
                .filter_map(|i| sim.get_entity(sim.champion_id_at(i)))
                .map(|c| format!("{}#{}{}", c.name().unwrap_or_default(), c.id(), if c.team() == team { "" } else { "*" }))
                .collect();
            wlog(format!("{} SIM {}: champions [{}] (* = enemies)", head(sim, me), self.sim_no, lineup.join(", ")));
        }
        let tag = format!("{SIM_TAG}{}", self.sim_no);
        if alive && !buff_names(sim, me).iter().any(|b| *b == tag) {
            sim.add_buff(me, &BuffV1::named(&tag));
        }
        if alive != self.was_alive {
            self.was_alive = alive;
            if !alive {
                self.end(sim, me, "dead");
                self.souls.clear();
            }
        }
        // 记功：敌方英雄身上的标记；有标记的由活变死 = 一个灵魂
        let mut born = Vec::new();
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(c) = sim.get_entity(id) else { continue };
            if c.team() == team {
                continue;
            }
            let c_alive = c.is_alive();
            let has = (0..c.buff_count()).filter_map(|k| c.buff_at(k)).any(|b| b.name() == MARK);
            let slot = match self.marked.iter().position(|m| m.0 == id) {
                Some(s) => s,
                None => {
                    self.marked.push((id, usize::MAX, c_alive));
                    self.marked.len() - 1
                }
            };
            if has && c_alive {
                self.marked[slot].1 = now;
            }
            let (seen, was) = (self.marked[slot].1, self.marked[slot].2);
            if was && !c_alive && seen != usize::MAX && self.credited(seen, now) {
                let name = c.name().unwrap_or_default();
                let range = None::<u32>;
                born.push(Soul { cat: category(&name, range), name, pos: c.pos(), until: now + self.p.soul_t as usize });
            }
            self.marked[slot].2 = c_alive;
        }
        for s in born {
            wlog(format!("{} SOUL {} ({}) at {:?}, {} away", head(sim, me), s.name, s.cat, s.pos, dist(s.pos, mpos)));
            self.souls.retain(|o| o.name != s.name);
            self.souls.push(s);
        }
        self.souls.retain(|s| s.until > now);
        // the data side of a possession, logged once each: the next action takes p_go and adds the shape buff (the
        // screen draws the body swap from that buff) - 「还是不能变身」: is it the sim or the screen that misses?
        if self.on.is_some() {
            let names = buff_names(sim, me);
            let (go, shape) = (names.iter().any(|b| b == GO), names.iter().any(|b| b == "league_viego_shape"));
            if !go && !self.seen.0 {
                self.seen.0 = true;
                wlog(format!("{} p_go taken by his action (shape buff {})", head(sim, me), if shape { "on" } else { "not yet" }));
            }
            if shape && !self.seen.1 {
                self.seen.1 = true;
                wlog(format!("{} shape buff on in the sim", head(sim, me)));
            }
        }
        // 附身中：时间到 / 数据的大招拿掉了 p_on
        if let Some(on) = &self.on {
            if now >= on.until {
                self.end(sim, me, "time");
            } else if !buff_names(sim, me).iter().any(|b| b == ON) {
                self.end(sim, me, "Heartbreaker");
            }
        }
        // a soul he cannot reach but within soul_dash: he dashes onto it (League: he goes and takes the soul; the AI
        // never walked to one - the user's game had one soul, 56000 away, never taken: 「可能是地上没有魂」)
        // not while he is banished (game 0.6.4: a banished unit neither moves nor acts)
        let alive = alive && sim.get_entity(me).is_some_and(|e| e.is_targetable());
        if alive && now >= self.dash_until && self.reachable(mpos).is_none() {
            if let Some((pos, name)) = self.dashable(mpos).map(|s| (s.pos, s.name.clone())) {
                let ticks = force_move(sim, me, (mpos.0 as f64, mpos.1 as f64), (pos.0 as f64, pos.1 as f64), DASH_SPEED);
                self.dash_until = now + ticks + 2;
                wlog(format!("{} DASH to the soul of {name}, {} away, {ticks} ticks", head(sim, me), dist(pos, mpos)));
            }
        }
        if alive {
            if let Some(i) = self.reachable(mpos) {
                let s = self.souls.remove(i);
                self.possess(sim, me, s);
            }
            self.mist(sim, me, team, mpos);
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
        "=== {ID} v{} (Viego: possess the champions he helps kill, their whole body on game 0.6.4 and later (Windows); the mist rises by itself near enemy champions) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:possess"), Possess::default());
    view::install_once();
    // the screen's match clock for the body swap (0.1.7); the bundle's only client extension
    module.set_extension(view::ClockReader);
    host.log(LogLevel::Info, "league_viego_soul loaded (Viego: Sovereign's Domination as in League).");
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

    /// The repo's heroes: the main pack's (league/champion/*.data_champion) and the tft pack's (tft/champion, 2026-10-26:
    /// 「让佛耶戈和妮蔻也能变成 tft 英雄」).
    fn pack_heroes() -> Vec<String> {
        let mut v = Vec::new();
        for pack in ["league", "tft"] {
            let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join(format!("../../{pack}/champion"));
            v.extend(std::fs::read_dir(&dir).expect("the pack's champion folder").filter_map(|e| {
                e.ok()?.file_name().into_string().ok()?.strip_suffix(".data_champion").map(str::to_string)
            }));
        }
        v.sort();
        assert!(v.len() > 100, "read only {} heroes", v.len());
        assert!(v.iter().any(|h| h.starts_with("tft_")), "no tft hero read");
        v
    }

    #[test]
    fn every_pack_hero_has_a_soul() {
        // src/souls.rs is generated: a hero added without make_override.py run again is never drawn as his body (Ornn
        // and Shyvana, both dense, were missing until 2026-10-21)
        let missing: Vec<String> =
            pack_heroes().into_iter().filter(|h| !souls::SOULS.iter().any(|s| s.0 == h)).collect();
        assert!(missing.is_empty(), "not in src/souls.rs - run make_override.py: {missing:?}");
    }

    /// The animation tags of an `#anim.fanim` (`{"anims":{"<tag>":{...},...}}`), sorted.
    fn fanim_tags(json: &str) -> Vec<String> {
        let Some(k) = json.find("\"anims\"") else { return Vec::new() };
        let Some(open) = json[k..].find('{').map(|o| k + o) else { return Vec::new() };
        let b = json.as_bytes();
        let (mut i, mut depth, mut out) = (open + 1, 1usize, Vec::new());
        while i < b.len() && depth > 0 {
            match b[i] {
                b'{' | b'[' => depth += 1,
                b'}' | b']' => depth -= 1,
                b'"' => {
                    let end = i + 1 + json[i + 1..].find('"').expect("an unclosed string");
                    let after = json[end + 1..].trim_start();
                    if depth == 1 && after.starts_with(':') {
                        out.push(json[i + 1..end].to_string());
                    }
                    i = end;
                }
                _ => {}
            }
            i += 1;
        }
        out.sort();
        out
    }

    #[test]
    fn every_soul_has_its_sheets_tags() {
        // the view hook writes the playing animation's name into Viego's body only when the victim's tags (here) have
        // it: a tag left here that the hero's sheet lost makes the game panic ("animation info not found") the moment he
        // possesses that hero, a tag the sheet gained is never used - so a re-exported sheet needs make_override.py again
        // (the user, 2026-10-21: 「测试佛耶戈 souls.rs 的标签和每个英雄 #anim 的标签一致」)
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
        let mut wrong = Vec::new();
        for id in pack_heroes() {
            let pack = if id.starts_with("tft_") { "tft" } else { "league" };
            let data = std::fs::read_to_string(root.join(format!("{pack}/champion/{id}.data_champion"))).unwrap();
            let sprite = data
                .lines()
                .find_map(|l| l.trim().strip_prefix("\"sprite\": \""))
                .map(|r| r.trim_end_matches(',').trim_end_matches('"'))
                .unwrap_or_else(|| panic!("no sprite in {id}"));
            let name = sprite.rsplit('/').next().unwrap();
            let Ok(anim) = std::fs::read_to_string(root.join(format!("{pack}/champions/{name}#anim.fanim"))) else {
                continue; // make_override.py leaves a hero without its own sheet out (every_pack_hero_has_a_soul says so)
            };
            let sheet = fanim_tags(&anim);
            assert!(!sheet.is_empty(), "no tags read from {name}#anim.fanim");
            let Some(soul) = souls::SOULS.iter().find(|s| s.0 == id) else { continue };
            let mut listed: Vec<String> = soul.2.iter().map(|t| t.to_string()).collect();
            listed.sort();
            if listed != sheet {
                let gone: Vec<&String> = listed.iter().filter(|t| !sheet.contains(t)).collect();
                let new: Vec<&String> = sheet.iter().filter(|t| !listed.contains(t)).collect();
                wrong.push(format!("{id}: not in the sheet any more {gone:?}, not in souls.rs {new:?}"));
            }
        }
        assert!(wrong.is_empty(), "src/souls.rs differs from the heroes' #anim.fanim - run make_override.py: {wrong:#?}");
    }

    #[test]
    fn the_tag_reader_reads_only_the_anims_keys() {
        let json = r#"{"anims":{"idle":{"frames":[{"duration":0.1,"data":{"x":0.0}}]},"hd_run":{"frames":[]}},"other":1}"#;
        assert_eq!(fanim_tags(json), vec!["hd_run".to_string(), "idle".to_string()]);
        let pretty = "{\n  \"anims\": {\n    \"run\": {\n      \"frames\": []\n    },\n    \"attack\": {}\n  }\n}";
        assert_eq!(fanim_tags(pretty), vec!["attack".to_string(), "run".to_string()]);
    }

    #[test]
    fn the_mist_rises_near_an_enemy_champion_once_a_pause() {
        assert!(mist_due(false, 1000, 0, Some(60000), 90000));
        assert!(!mist_due(false, 1000, 0, Some(95000), 90000)); // too far
        assert!(!mist_due(false, 1000, 0, None, 90000)); // nobody in sight
        assert!(!mist_due(false, 1000, 1200, Some(60000), 90000)); // its pause
        assert!(!mist_due(true, 1000, 0, Some(60000), 90000)); // possessed: the soul's own mist
        let mut p = Possess::default();
        p.configure(r#"{"e_cd":480,"e_trig":80000,"e_hide":90}"#);
        assert_eq!((p.p.e_cd, p.p.e_trig, p.p.e_hide, p.p.e_ms), (480, 80000, 90, 30));
    }

    #[test]
    fn the_copy_hands_the_mist_to_the_add_on() {
        let copy = include_str!("../override/league_viego.data_champion");
        for k in ["\"e_cd\"", "\"e_trig\"", "\"e_hide\""] {
            assert!(copy.contains(k), "{k} missing from the copy's passive params");
        }
        assert!(copy.contains("description.league_viego_soul.skill2"));
    }

    #[test]
    fn params_are_read_from_the_passive_json() {
        let mut p = Possess::default();
        p.configure(r#"{"p_t":540,"soul_r":30000,"s_range":20000}"#);
        assert_eq!((p.p.p_t, p.p.soul_r, p.p.s_range, p.p.p_win), (540, 30000, 20000, 180));
    }

    #[test]
    fn categories_come_from_the_table_or_the_range() {
        assert_eq!(category("league_jinx", None), "range");
        assert_eq!(category("league_garen", None), "melee");
        assert_eq!(category("league_lux", None), "mage");
        assert_eq!(category("league_soraka", None), "util");
        assert_eq!(category("league_zed", None), "assassin");
        assert_eq!(category("archer", None), "range");
        assert_eq!(category("someone_elses_hero", Some(60000)), "range");
        assert_eq!(category("someone_elses_hero", None), "melee");
        assert!(ranged("mage") && !ranged("assassin"));
    }

    #[test]
    fn a_death_counts_inside_the_window() {
        let p = Possess::default();
        assert!(p.credited(1000, 1001));
        assert!(p.credited(1000, 1180));
        assert!(!p.credited(1000, 1181));
    }

    #[test]
    fn the_nearest_soul_in_reach_is_taken() {
        let mut p = Possess::default();
        let s = |n: &str, x| Soul { name: n.into(), cat: "melee", pos: (x, 0), until: 99 };
        p.souls = vec![s("a", 50_000), s("b", 20_000), s("c", 30_000)];
        assert_eq!(p.reachable((0, 0)), Some(1));
        p.souls = vec![s("a", 50_000)];
        assert_eq!(p.reachable((0, 0)), None);
    }

    #[test]
    fn a_soul_out_of_reach_is_dashed_to() {
        let mut p = Possess::default();
        let s = |n: &str, x| Soul { name: n.into(), cat: "melee", pos: (x, 0), until: 99 };
        p.souls = vec![s("far", 120_000), s("dash", 56_000), s("near", 70_000)];
        assert_eq!(p.dashable((0, 0)).map(|s| s.name.as_str()), Some("dash"));
        p.souls = vec![s("far", 120_000)];
        assert!(p.dashable((0, 0)).is_none());
    }

    #[test]
    fn the_table_is_sorted_for_the_search() {
        assert!(souls::SOULS.windows(2).all(|w| w[0].0 < w[1].0));
        assert!(souls::SOULS.iter().all(|s| CATS.contains(&s.1)));
    }
}
