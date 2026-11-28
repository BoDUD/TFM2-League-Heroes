//! 厄斐琉斯附加包（用户 2026-10-16：「方案可以，全按推荐做（下路 ADC，做附加包，PPU 1.5）」）。主包保持纯数据；
//! `mod.override_info` 把主包的厄斐琉斯换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_aphelios.py 的
//! `native=1` 生成：加上本包的被动 `league_aphelios:queue`，普攻、技能2 的说明开头加【附加包】），本包补数据做不到的三件事：
//!
//! - **整身换武器**（`view.rs`，游戏 0.6.4 起的 Windows 版）：主手是断魄 / 坠明 / 荧焰 / 折镜（主包的永久 buff
//!   `league_aphelios_mw_<武器>`）时，站着、跑着、挨打、出手的第一刻都画成那把武器在手里（图里的 `<武器>_idle` …），
//!   通碧主手时是原来的样子（通碧背在身后）。
//! - **真实的武器队列**（被动 `queue`）：主包的数据按固定循环（通碧 → 断魄 → 坠明 → 荧焰 → 折镜）换上副手以外的下一把；
//!   英雄联盟是先进先出的队列（打空的那把排到队尾），W 换过手以后两者会不一样。本包每 tick 看主手：数据换了武器、副手没变
//!   （打空换枪）时，按队列该换上的不是数据挑的那把，就把主手 buff 换成队列里那把（射程、吸血、攻速照主包的参数）；
//!   主手和副手互换（W）时队列不动。
//! - **残血换断魄**：生命低于 `low_hp`% 、副手是断魄、`near` 内有看得见的敌方英雄时，直接把断魄换到主手（吸血），每
//!   `low_cd` tick 最多一次（主包的 W 只在主手技能冷却、副手技能好了时才换）。
//!
//! - **高手的用法**（0.2.0，用户：「厄斐琉斯能做的像英雄联盟里面高手一样的逻辑吗」，「按 1-4 全做」；判断在 `brain.rs`）：
//!   1. Q 看武器和局面放：AI 钩子 `league_aphelios:hands`（优先级 `HANDS_PRIORITY`，排在 league_ult_press 之后，拿到它
//!      的决定再改）在 Q 好了、局面合适时替 AI 按 Q（给对的目标），AI 自己按的 Q 不合适就改成普攻（通碧不打兵、坠明等
//!      有标记的英雄、荧焰等扇形里两个英雄……）；
//!   2. W 换到合适的武器：被动直接换手（主副手互换，同数据的 W，每 `SWAP_CD` tick 最多一次）——主手 Q 在冷却、副手的 Q
//!      正合适时换手接 Q；被英雄贴脸时换上折镜 / 坠明；数据自己的 W（只看 Q 冷却）在副手的 Q 不合适时改成普攻；
//!   3. 开大前先换好主手：大招准备好（`r_arm`）、身边有敌方英雄时，副手的礼物更好（荧焰 > 坠明 > 断魄 > 通碧 > 折镜，
//!      残血时断魄最好）就先换上；
//!   4. 通碧标记换手引爆：通碧的 Q 一射出去就换上副手——副本里标记被引爆时带主手的命中效果（build_aphelios native），
//!      副手是坠明就打上标记，接着坠明 Q 定身；是荧焰、折镜就接它们的 Q。
//!
//! - **打架时不再否决 AI 的 Q / W**（0.2.4，用户 2026-11-15：「不知道为什么厄斐琉斯打架就站着不动 从满血被周围2 3个打死
//!   查一查这是我们的问题还是官方AI的问题」）：否决让 Q 的格子一直好着（格子冷却只有 60 tick，五把武器真正的冷却是 buff），
//!   AI 每 4 tick 再要一次，每次都被改成普攻——他就钉在原地一下一下打，AI 自己往后撤、走位的命令一直下不来（日志：一串否决
//!   4 tick 一次、中间隔一次普攻动作，能连好几秒；一次启动 Q 被否决 88,100 次、W 6,650 次）。现在：看得见的敌方英雄在
//!   `brain::FIGHT_R` 以内时 AI 的 Q / W 照放；不打架时照旧否决，但没有能改打的目标就放行（以前改成「站在原地」），AI 连着要
//!   同一个技能满 [`VETO_HOLD`] tick 也放行。另加记录器（`record.rs`）：每次阵亡写一行 `DEATH`（死前 5 秒走着、钉在原地、
//!   被控各多久，钉在原地时手上是谁的命令），每 100 次一行 `SUM`。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aphelios.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `QUEUE`（数据换枪，和队列一致 / 改成队列那把）、`LOW`（残血换断魄）、`FORM`（显示里的武器形态）、`SWAP`（被动换手和
//! 原因）、`Q PRESS` / `Q VETO` / `W VETO` / `Q PASS` / `W PASS` / `VETO RELEASED`（AI 钩子），都限了条数；`DEATH` / `SUM`
//! （记录器，看着的那场的阵亡全写）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;
use game_places::skill_scale::sk;

pub mod brain;
pub mod record;
pub mod view;

const ID: &str = "league_aphelios";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_aphelios") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
const HERO: &str = "league_aphelios";
/// 五把武器，按主包数据的循环顺序（build_aphelios.WEAPONS）。
pub const WEAPONS: [&str; 5] = ["cal", "sev", "grav", "inf", "cre"];
pub const CAL: usize = brain::CAL;
pub const SEV: usize = brain::SEV;
/// AI 钩子排在 league_ult_press（100）之后：引擎按优先级从小到大跑钩子，每个拿到前一个的决定。
pub const HANDS_PRIORITY: i32 = 110;

pub fn main_buff(w: usize) -> String {
    format!("{HERO}_mw_{}", WEAPONS[w])
}

pub fn off_buff(w: usize) -> String {
    format!("{HERO}_ow_{}", WEAPONS[w])
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    // the tests' lines (the recorder's DEATH / SUM) never go into the game's log
    if cfg!(test) {
        return std::env::temp_dir().join("league_aphelios_test.log");
    }
    if let Some(path) = std::env::var_os("LEAGUE_APHELIOS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_aphelios.log");
        }
    }
    PathBuf::from("league_aphelios.log")
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

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 50;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// 模拟来源的名字（日志行头）。
fn origin_name(kind: u32) -> &'static str {
    match SimOriginKindV1::from_code(kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    }
}

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{} m={} s={}] t={} #{id}", origin_name(o.kind), m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 主手武器 buff 自带的属性（P 的 c_range、sev_vamp、sev_as）。
    pub c_range: usize,
    pub sev_vamp: i32,
    pub sev_as: i32,
    /// 残血换断魄：生命百分比、附近敌方英雄的距离、两次之间的 tick。
    pub low_hp: usize,
    pub near: u64,
    pub low_cd: u64,
}

impl Default for Params {
    fn default() -> Self {
        Self { c_range: 10000, sev_vamp: 10, sev_as: 20, low_hp: 35, near: 60000, low_cd: 360 }
    }
}

/// `{"c_range":10000,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        match k {
            "c_range" => p.c_range = v.max(0) as usize,
            "sev_vamp" => p.sev_vamp = v as i32,
            "sev_as" => p.sev_as = v as i32,
            "low_hp" => p.low_hp = v.max(0) as usize,
            "near" => p.near = v.max(0) as u64,
            "low_cd" => p.low_cd = v.max(0) as u64,
            _ => {}
        }
    }
    p
}

/// 主手武器 buff（和主包数据加的同名同属性：断魄吸血和攻速；通碧的 `c_range` 不在 buff 上——2026-11-07 起 buff 只是标记，
/// 射程由主包 league.dll 的 `league:range` 按 `league_aphelios_mw_cal` 加，AI 的出手判断也认）。
pub fn weapon_buff(w: usize, p: &Params) -> BuffV1 {
    let mut b = BuffV1::named(&main_buff(w));
    if w == SEV {
        b.vamp = p.sev_vamp;
        b.attack_speed_mult = p.sev_as;
    }
    b
}

// ===================== 武器队列（纯逻辑，单元测试） =====================

/// 一条命里的武器：主手、副手和排队的三把（先进先出）。
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Queue {
    pub main: usize,
    pub off: usize,
    pub line: Vec<usize>,
}

/// 这一 tick 看到的变化要怎么处理。
#[derive(Clone, Debug, PartialEq)]
pub enum Step {
    /// 没变 / 第一次看到 / W 互换 / 本包自己换的：只记下来。
    Keep,
    /// 数据打空换枪，换上的就是队列里那把。
    Agree(usize),
    /// 数据打空换枪，队列里该换上的是另一把：(数据挑的, 队列的)。
    Fix(usize, usize),
    /// 看不懂的变化（主手副手都换了，不是互换）：按循环重排队列。
    Resync,
}

impl Queue {
    /// 主手 main、副手 off 时，按数据的循环顺序排出其余三把（这条命开局、或者看不懂的时候）。
    pub fn fresh(main: usize, off: usize) -> Queue {
        let line = (1..5).map(|k| (main + k) % 5).filter(|w| *w != off).collect();
        Queue { main, off, line }
    }

    /// 这一 tick 主手 main、副手 off：更新队列，返回怎么处理。
    pub fn step(&mut self, main: usize, off: usize) -> Step {
        if main == self.main && off == self.off {
            return Step::Keep;
        }
        if main == self.off && off == self.main {
            std::mem::swap(&mut self.main, &mut self.off);
            return Step::Keep;
        }
        if off == self.off && main != self.main && !self.line.is_empty() {
            let want = self.line.remove(0);
            self.line.push(self.main);
            self.main = want;
            return if want == main { Step::Agree(want) } else { Step::Fix(main, want) };
        }
        *self = Queue::fresh(main, off);
        Step::Resync
    }
}

// ===================== 被动：队列 + 残血换断魄 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn buffs_have(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn hp_share(e: &StableEntity<'_, '_>) -> f64 {
    let (hp, max) = e.hp();
    if max == 0 { 0.0 } else { hp as f64 / max as f64 }
}

fn at_of(e: &StableEntity<'_, '_>) -> (f64, f64) {
    (e.pos().0 as f64, e.pos().1 as f64)
}

/// `team` 看得见、能选中的敌方单位（防御塔不算），带坠明标记的英雄记下。
pub(crate) fn foes_of(sim: &StableSim<'_>, team: usize) -> Vec<brain::Foe> {
    let (g, r) = (format!("{HERO}_g_slow"), format!("{HERO}_r_slow"));
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower() && sim.is_visible(team, u.id()))
        .map(|u| brain::Foe {
            id: u.id(),
            at: at_of(&u),
            champion: u.is_champion(),
            hp: hp_share(&u),
            marked: u.is_champion() && (buffs_have(&u, &g) || buffs_have(&u, &r)),
        })
        .collect()
}

/// 这把武器的 Q 在冷却（数据的 `qcd_<武器>`）。
fn q_cooling(e: &StableEntity<'_, '_>, w: usize) -> bool {
    buffs_have(e, &format!("{HERO}_qcd_{}", WEAPONS[w]))
}

/// 身上的主手 / 副手武器（主包数据第一次普攻才加；之前没有）。
fn weapons_of(sim: &StableSim<'_>, id: usize) -> Option<(usize, usize)> {
    let main = (0..5).find(|w| has_buff(sim, id, &main_buff(*w)))?;
    let off = (0..5).find(|w| has_buff(sim, id, &off_buff(*w)))?;
    Some((main, off))
}

static SHARED: Mutex<Option<Params>> = Mutex::new(None);

fn shared() -> Params {
    SHARED.lock().unwrap_or_else(|e| e.into_inner()).clone().unwrap_or_default()
}

#[derive(Clone, Default)]
struct Moon {
    /// 这条命的队列（None = 还没看到武器）。每个模拟、每个英雄各一份（被动实例不共用）。
    queue: Option<Queue>,
    /// 上次残血换断魄的 tick。
    low_at: Option<u64>,
    /// 上次被动换手的 tick、上一 tick 通碧的 Q 在不在冷却（刚射出去 = 这一 tick 开始冷却）。
    swap_at: Option<usize>,
    cal_cd: bool,
}

impl Moon {
    fn set_main(sim: &mut StableSim<'_>, me: usize, from: usize, to: usize, p: &Params) {
        sim.entity_remove_buff(me, &main_buff(from));
        sim.add_buff(me, &weapon_buff(to, p));
    }

    /// 主手和副手互换（数据的 W 做的事：主手 buff 带那把的属性），换枪的声音和画面。
    fn swap_hands(sim: &mut StableSim<'_>, me: usize, main: usize, off: usize, p: &Params) {
        Moon::set_main(sim, me, main, off, p);
        sim.entity_remove_buff(me, &off_buff(off));
        sim.add_buff(me, &BuffV1::named(&off_buff(main)));
        let on = InputTargetV1::target(me);
        sim.play_sfx(&format!("{HERO}_swap_{}", WEAPONS[off]), me, &on);
        sim.play_view_effect(&format!("{HERO}_swap"), me, &on, 0, 0, 0);
    }

    /// 高手的换手（brain::swap_plan）：大招前换礼物、通碧 Q 后换手引爆、换手接 Q、被贴脸换近身武器。
    fn smart_swap(&mut self, sim: &mut StableSim<'_>, me: usize, p: &Params) {
        let Some(q) = self.queue.clone() else { return };
        let Some(e) = sim.get_entity(me) else { return };
        let tick = sim.tick();
        let cal_cd = q_cooling(&e, CAL);
        let cal_cast = cal_cd && !self.cal_cd;
        self.cal_cd = cal_cd;
        let firing = buffs_have(&e, &format!("{HERO}_r_go"));
        let s = brain::Swap {
            main: q.main,
            off: q.off,
            main_q: !q_cooling(&e, q.main),
            off_q: !q_cooling(&e, q.off),
            r_armed: buffs_have(&e, &format!("{HERO}_r_arm")) && !firing,
            cal_cast,
        };
        // Moonshot's swap is timed (before the mark is shot off); the others wait for the swap's pause
        if firing || (!cal_cast && self.swap_at.is_some_and(|t| tick < t + brain::SWAP_CD)) {
            return;
        }
        let (team, at, hp) = (e.team(), at_of(&e), hp_share(&e));
        let foes = foes_of(sim, team);
        let Some(why) = brain::swap_plan(&s, at, hp, &foes) else { return };
        Moon::swap_hands(sim, me, q.main, q.off, p);
        self.swap_at = Some(tick);
        if let Some(k) = counted("swap") {
            wlog(format!("{} SWAP {} -> {} ({why}; {:.0}% hp, {} enemy champions within {:.0}) #{k}", head(sim, me),
                WEAPONS[q.main], WEAPONS[q.off], hp * 100.0,
                foes.iter().filter(|f| f.champion && brain::dist(at, f.at) <= sk(brain::R_LOOK)).count(), sk(brain::R_LOOK)));
        }
    }

    fn low_swap(&mut self, sim: &mut StableSim<'_>, me: usize, p: &Params) {
        let Some(q) = self.queue.clone() else { return };
        if q.off != SEV || q.main == SEV {
            return;
        }
        let tick = sim.tick() as u64;
        if self.low_at.is_some_and(|t| tick < t + p.low_cd) {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let (hp, max) = e.hp();
        if max == 0 || hp * 100 >= max * p.low_hp {
            return;
        }
        let (team, at) = (e.team(), e.pos());
        let near = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).any(|u| {
            u.team() != team && u.is_alive() && u.is_champion() && sim.is_visible(team, u.id()) && {
                let (dx, dy) = (u.pos().0 as f64 - at.0 as f64, u.pos().1 as f64 - at.1 as f64);
                (dx * dx + dy * dy).sqrt() <= p.near as f64
            }
        });
        if !near {
            return;
        }
        // the swap the data's W does: Severum to the main hand, the main weapon to the off hand
        Moon::swap_hands(sim, me, q.main, SEV, p);
        self.low_at = Some(tick);
        self.swap_at = Some(tick as usize);
        if let Some(k) = counted("low") {
            wlog(format!("{} LOW {}% hp, an enemy champion within {}: Severum to the main hand, {} to the off hand #{k}",
                head(sim, me), hp * 100 / max, p.near, WEAPONS[q.main]));
        }
    }
}

impl StablePassive for Moon {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let p = parse_params(params_json);
        let mut s = SHARED.lock().unwrap_or_else(|e| e.into_inner());
        if s.as_ref() != Some(&p) {
            wlog(format!("params {params_json} -> {p:?}"));
            *s = Some(p);
        }
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.queue = None;
        self.low_at = None;
        self.swap_at = None;
        self.cal_cd = false;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        let Some((main, off)) = weapons_of(sim, me) else { return };
        let p = shared();
        match self.queue.as_mut() {
            None => self.queue = Some(Queue::fresh(main, off)),
            Some(q) => match q.step(main, off) {
                Step::Keep => {}
                Step::Agree(w) => {
                    if let Some(k) = counted("queue") {
                        wlog(format!("{} QUEUE {} empty -> {} (the data's pick is the queue's) #{k}", head(sim, me),
                            WEAPONS[q.line[q.line.len() - 1]], WEAPONS[w]));
                    }
                }
                Step::Fix(data, want) => {
                    Moon::set_main(sim, me, data, want, &p);
                    if let Some(k) = counted("queue") {
                        wlog(format!("{} QUEUE {} empty -> {} (the data took {}; queue now {:?}) #{k}", head(sim, me),
                            WEAPONS[q.line[q.line.len() - 1]], WEAPONS[want], WEAPONS[data],
                            q.line.iter().map(|w| WEAPONS[*w]).collect::<Vec<_>>()));
                    }
                }
                Step::Resync => {
                    if let Some(k) = counted("queue") {
                        wlog(format!("{} QUEUE resync: main {} off {} #{k}", head(sim, me), WEAPONS[main], WEAPONS[off]));
                    }
                }
            },
        }
        let before = self.swap_at;
        self.low_swap(sim, me, &p);
        if self.swap_at == before {
            self.smart_swap(sim, me, &p);
        }
        // a swap changed the buffs: the queue sees it as a swap next tick (main and off exchanged)
    }
}

// ===================== AI 钩子：Q 看武器和局面，W 只在副手的 Q 合适时 =====================

/// 被控（不能放技能）、正在出手或被强制位移：不替 AI 按（同 league_ult_press 的 controlled / busy）。
const NO_ACT: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
    CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

/// 普攻够得着的距离（普攻 55000 + 通碧 10000，中心距离再宽一点）：否决 Q / W 时改打的目标要在这以内。
const ATTACK_REACH: f64 = 70_000.0;
/// 生命低于这一比例、AI 在走（多半在跑）：只替它按断魄的 Q。
const LOW_RUN: f64 = 0.3;
/// 不打架时一回否决最多拦这么久（0.2.4）：AI 一直要同一个技能（被否决的格子一直好着，它每 4 tick 再要一次），拦满就放行。
pub const VETO_HOLD: usize = 120;
/// AI 两次要同一个技能隔这么多 tick 以内算同一回。
pub const VETO_GAP: usize = 12;

/// AI 一回一回地要同一个技能（[`Insist::ask`]）。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Insist {
    slot: Option<u32>,
    since: usize,
    last: usize,
}

impl Insist {
    /// AI 在 `tick` 又要了格子 `slot`：还在拦的时限里（Ok），或已经连着要了这么多 tick、该放行了（Err）。
    pub fn ask(&mut self, slot: u32, tick: usize) -> Result<(), usize> {
        if self.slot != Some(slot) || tick > self.last + VETO_GAP || tick < self.since {
            *self = Insist { slot: Some(slot), since: tick, last: tick };
        }
        self.last = tick;
        let held = tick - self.since;
        if held >= VETO_HOLD { Err(held) } else { Ok(()) }
    }
}

/// AI 按的 Q / W 不合适时怎么办（0.2.4）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Veto {
    /// 改成普攻这个目标
    Attack(usize),
    /// 打架时：AI 自己的照放
    PassFight,
    /// 没有能改打的目标：也放行（0.2.3 这时下「走到脚下」，他就站在原地不动）
    PassNothing,
}

pub fn veto_or_pass(fight: bool, attack: Option<usize>) -> Veto {
    match (fight, attack) {
        (true, _) => Veto::PassFight,
        (false, Some(t)) => Veto::Attack(t),
        (false, None) => Veto::PassNothing,
    }
}

/// The AI is still recalling (game 0.6.5 decides when to go home and buy): its last order was a Return - it orders only
/// on its judgement ticks, a Return again while the recall lasts, nothing in between - and any other order ends it
/// (league_ult_press 0.5.0's rule).
pub fn still_recalling(was: bool, base: Option<InputV1>) -> bool {
    match base {
        Some(b) => b.kind == InputKindV1::Return.code(),
        None => was,
    }
}

#[derive(Clone, Default)]
struct Hands {
    /// the AI is recalling (`still_recalling`): nothing pressed
    recalling: bool,
    /// the AI asking for a vetoed slot again and again (0.2.4)
    insist: Insist,
    /// the recorder: this life's last 5 seconds (0.2.4)
    life: record::Life,
}

enum Call {
    /// 替 AI 按 Q：目标、武器、为什么。
    Press(usize, usize, &'static str),
    /// AI 按的 Q / W 不合适：改成普攻这个目标，记哪一类、为什么、哪个格子。
    Veto(usize, &'static str, String, SkillSlotV1),
    /// AI 按的 Q / W 0.2.3 会否决，现在放行（0.2.4）：哪个格子、哪把武器、是不是因为在打架（否则是没有能改打的目标）。
    Pass(SkillSlotV1, usize, bool),
}

impl Hands {
    fn call(sim: &StableSim<'_>, me: usize, base: Option<InputV1>) -> Option<Call> {
        let e = sim.get_entity(me)?;
        if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| NO_ACT.iter().any(|k| k.code() == c.kind))) {
            return None;
        }
        let (main, off) = weapons_of(sim, me)?;
        let (team, at, hp) = (e.team(), at_of(&e), hp_share(&e));
        let foes = foes_of(sim, team);
        let kind = base.and_then(|b| InputKindV1::from_code(b.kind));
        let target = base.filter(|b| InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target))
            .map(|b| b.target.target_id);
        // the attack a vetoed Q / W turns into: its own target if an enemy, else the nearest enemy in reach (0.2.4: never
        // "walk to where he stands" - with nothing to attack the AI's own Q / W goes out)
        let instead = target.filter(|t| foes.iter().any(|f| f.id == *t)).or_else(|| {
            foes.iter().filter(|f| brain::dist(at, f.at) <= ATTACK_REACH)
                .min_by(|a, b| brain::dist(at, a.at).total_cmp(&brain::dist(at, b.at))).map(|f| f.id)
        });
        // 0.2.4: in a fight the AI's own Q / W goes out - a veto keeps the slot ready, the AI asks again every 4 ticks and
        // each veto turned into an attack where he stood, so its walks away never came (brain::fight_near)
        let fight = brain::fight_near(at, &foes, sk(brain::FIGHT_R));
        let veto = |slot: SkillSlotV1, kind: &'static str, why: String| {
            Some(match veto_or_pass(fight, instead) {
                Veto::Attack(t) => Call::Veto(t, kind, why, slot),
                Veto::PassFight => Call::Pass(slot, main, true),
                Veto::PassNothing => Call::Pass(slot, main, false),
            })
        };
        let plan = brain::q_plan(main, off, at, hp, &foes);
        match kind {
            Some(InputKindV1::Skill) => match plan {
                Some((t, why)) if Some(t) != target => Some(Call::Press(t, main, why)),
                Some(_) => None,
                None => veto(SkillSlotV1::Skill, "veto q", format!("Q VETO {}: not the moment for its Q", WEAPONS[main])),
            },
            Some(InputKindV1::Skill2) => {
                let fits = brain::q_plan(off, main, at, hp, &foes).is_some() && !q_cooling(&e, off);
                if fits {
                    return None;
                }
                veto(SkillSlotV1::Skill2, "veto w",
                    format!("W VETO {} -> {}: the off hand's Q does not fit now", WEAPONS[main], WEAPONS[off]))
            }
            // the ult (league_ult_press's arm press) and a recall stay as they are
            Some(InputKindV1::Ult) | Some(InputKindV1::Return) => None,
            // running away low: only Severum's Q (its heal and speed) is worth stopping for
            Some(InputKindV1::Move) if hp < LOW_RUN && main != SEV => None,
            _ => {
                let ready = e.cooldown(SkillSlotV1::Skill).is_some_and(|c| c.unlocked && c.remaining == 0);
                let (t, why) = plan.filter(|_| ready && !q_cooling(&e, main))?;
                Some(Call::Press(t, main, why))
            }
        }
    }
}

impl StablePlayerAi for Hands {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:hands")
    }

    fn priority(&self) -> i32 {
        HANDS_PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        // the recorder's look at him this tick (read only)
        let look = ctx.sim().map(|sim| record::look(&sim, player));
        // game 0.6.5's AI decides when to recall (and buy): nothing pressed while it does
        self.recalling = still_recalling(self.recalling, base);
        let (out, ours, pass) = if self.recalling { (None, None, false) } else { self.decide(ctx, base) };
        if let Some(look) = look {
            // the order he holds from now on: ours if we replaced the AI's, else the AI's own new one (if it gave one)
            let went = match (out, ours) {
                (Some(_), Some(o)) => Some(o),
                _ => base.and_then(|b| record::Order::of_input(b.kind)),
            };
            self.life.step(&look, went, ours == Some(record::Order::OurVeto), pass);
        }
        out
    }
}

impl Hands {
    /// This tick's decision: the input (None keeps the AI's), whose replacement it is, and whether the AI's Q / W went out
    /// in a fight where 0.2.3 would have vetoed it.
    fn decide(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> (Option<InputV1>, Option<record::Order>, bool) {
        const KEEP: (Option<InputV1>, Option<record::Order>, bool) = (None, None, false);
        let player = ctx.player_id();
        let (call, line, tick) = {
            let Some(sim) = ctx.sim() else { return KEEP };
            let Some(me) = sim.get_player(player).and_then(|p| p.champion()).map(|e| e.id()) else { return KEEP };
            let Some(call) = Hands::call(&sim, me, base) else { return KEEP };
            (call, head(&sim, me), sim.tick())
        };
        let key = |slot: SkillSlotV1| if slot == SkillSlotV1::Skill { "Q" } else { "W" };
        match call {
            Call::Press(t, w, why) => {
                let input = InputV1::action(InputKindV1::Skill, InputTargetV1::target(t));
                if !ctx.is_valid_input(&input) {
                    return KEEP;
                }
                if let Some(k) = counted("press") {
                    wlog(format!("{line} Q PRESS {} on #{t}: {why} #{k}", WEAPONS[w]));
                }
                (Some(input), Some(record::Order::OurPress), false)
            }
            Call::Pass(slot, w, fight) => {
                record::note_pass(fight);
                let (kind, why) = if fight {
                    ("pass fight", "in a fight (an enemy champion within FIGHT_R)")
                } else {
                    ("pass nothing", "nothing to attack instead")
                };
                if let Some(k) = counted(kind) {
                    wlog(format!("{line} {} PASS {}: {why} - the AI's own goes out #{k}", key(slot), WEAPONS[w]));
                }
                (None, None, fight)
            }
            Call::Veto(t, kind, why, slot) => {
                let input = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                if !ctx.is_valid_input(&input) {
                    return KEEP;
                }
                match self.insist.ask(slot.code(), tick) {
                    Ok(()) => {
                        record::note_veto();
                        if let Some(k) = counted(kind) {
                            wlog(format!("{line} {why} #{k}"));
                        }
                        (Some(input), Some(record::Order::OurVeto), false)
                    }
                    Err(held) => {
                        record::note_release();
                        if let Some(k) = counted("veto released") {
                            wlog(format!("{line} {} VETO RELEASED: the AI asked for it {held} ticks on end - its own goes out #{k}",
                                key(slot)));
                        }
                        KEEP
                    }
                }
            }
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Aphelios: the whole-body weapon forms, the real weapon queue, Severum when low, Q / W / R by the situation like a good player; the AI's own Q / W in a fight; a DEATH line per death: the last 5 s) loaded: game {}.{}.{} abi {} log={} ===",
        v.major, v.minor, v.patch, host.abi_level(), LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_passive(format!("{ID}:queue"), Moon::default());
    module.add_player_input_ai(Hands::default());
    host.log(LogLevel::Info, "league_aphelios loaded (weapon forms, the weapon queue, Severum when low).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_queue_starts_in_the_cycle() {
        let q = Queue::fresh(CAL, SEV);
        assert_eq!(q.line, vec![2, 3, 4]);
    }

    #[test]
    fn without_swaps_the_queue_and_the_cycle_agree() {
        let mut q = Queue::fresh(CAL, SEV);
        assert_eq!(q.step(2, SEV), Step::Agree(2)); // Calibrum empty -> Gravitum
        assert_eq!(q.line, vec![3, 4, 0]);
        assert_eq!(q.step(3, SEV), Step::Agree(3));
        assert_eq!(q.step(4, SEV), Step::Agree(4));
        assert_eq!(q.step(0, SEV), Step::Agree(0));
    }

    #[test]
    fn after_a_swap_the_queue_wins() {
        // the counterexample of the plan: main Calibrum off Severum; W; Severum empty -> Gravitum (both agree);
        // W (main Calibrum, off Gravitum); Calibrum empty: the queue gives Infernum, the cycle Severum
        let mut q = Queue::fresh(CAL, SEV);
        assert_eq!(q.step(SEV, CAL), Step::Keep); // W
        assert_eq!(q.step(2, CAL), Step::Agree(2)); // Severum empty -> Gravitum; line [3, 4, 1]
        assert_eq!(q.step(CAL, 2), Step::Keep); // W
        assert_eq!(q.step(SEV, 2), Step::Fix(SEV, 3)); // the data took Severum, the queue Infernum
        assert_eq!(q.main, 3);
        assert_eq!(q.line, vec![4, 1, 0]);
    }

    #[test]
    fn a_strange_change_resyncs() {
        let mut q = Queue::fresh(CAL, SEV);
        assert_eq!(q.step(3, 4), Step::Resync);
        assert_eq!(q, Queue::fresh(3, 4));
    }

    #[test]
    fn params_from_the_main_pack() {
        let p = parse_params(r#"{"c_range": 10000, "sev_vamp": 12, "sev_as": 25, "low_hp": 30}"#);
        assert_eq!((p.c_range, p.sev_vamp, p.sev_as, p.low_hp, p.near), (10000, 12, 25, 30, 60000));
    }

    #[test]
    fn the_weapon_buffs_carry_the_main_packs_stats() {
        let p = Params::default();
        // Calibrum's reach is league.dll's league:range reading the marker (2026-11-07): no `range` on the buff
        let c = weapon_buff(CAL, &p);
        assert_eq!((c.name(), c.range), ("league_aphelios_mw_cal", 0));
        let s = weapon_buff(SEV, &p);
        assert_eq!((s.vamp, s.attack_speed_mult), (10, 20));
        assert_eq!(weapon_buff(2, &p).range, 0);
    }

    #[test]
    fn a_veto_never_happens_in_a_fight_nor_stands_him_still() {
        // 0.2.3 turned the AI's Q / W into an attack (or a walk to where he stood) in every case
        assert_eq!(veto_or_pass(true, Some(27)), Veto::PassFight);
        assert_eq!(veto_or_pass(true, None), Veto::PassFight);
        assert_eq!(veto_or_pass(false, Some(27)), Veto::Attack(27));
        assert_eq!(veto_or_pass(false, None), Veto::PassNothing);
    }

    #[test]
    fn the_ais_insistence_is_released_after_the_hold() {
        // the AI asks every 4 ticks (the log of 2026-11-15: t=3506..3738, 28 vetoes)
        let mut i = Insist::default();
        let q = SkillSlotV1::Skill.code();
        let mut t = 1000;
        while t < 1000 + VETO_HOLD {
            assert_eq!(i.ask(q, t), Ok(()), "tick {t}");
            t += 4;
        }
        assert_eq!(i.ask(q, t), Err(t - 1000));
        // a pause longer than VETO_GAP, or another slot, starts a new round
        assert_eq!(i.ask(q, t + VETO_GAP + 1), Ok(()));
        assert_eq!(i.ask(SkillSlotV1::Skill2.code(), t + VETO_GAP + 2), Ok(()));
        // a new simulation's ticks start low again
        assert_eq!(i.ask(SkillSlotV1::Skill2.code(), 5), Ok(()));
    }

    #[test]
    fn the_copy_carries_the_passive_and_the_main_packs_numbers() {
        let copy = include_str!("../override/league_aphelios.data_champion");
        assert!(copy.contains("\"passive_ref\": \"league_aphelios:queue\""));
        for k in ["c_range", "sev_vamp", "sev_as", "low_hp", "near", "low_cd"] {
            assert!(copy.contains(&format!("\"{k}\"")), "{k} missing from the copy's params");
        }
        for w in WEAPONS {
            assert!(copy.contains(&format!("\"league_aphelios_mw_{w}\"")), "the copy has no mw_{w}");
            assert!(copy.contains(&format!("\"league_aphelios_ow_{w}\"")), "the copy has no ow_{w}");
        }
    }
}
