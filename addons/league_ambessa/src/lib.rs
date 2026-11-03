//! 安蓓萨附加包：数据做不到、和英雄联盟不一样的地方，这里照英雄联盟做（用户：「和原版不一样的地方要做附加包」）。
//!
//! `mod.override_info` 把主包的安蓓萨换成 `override/` 里的副本（tools/kit/build_ambessa.py --native），`passive` 换成本包的
//! `league_ambessa:matriarch`：
//!
//! - **狡诈横扫只有刀尖加伤**：主包读不到「离她多远」，扫中的都吃最大生命 `q_pct`%。副本的横扫给扫中的挂 `league_ambessa_q_edge`、
//!   给她挂 `league_ambessa_q_on`；本包只对离她 `q_tip`% 半径以外（刀尖）的造成最大生命 `q_pct`% 的物理伤害。
//! - **裂地重击打第一个**：主包把加伤给技能的目标。副本的直线给打中的挂 `league_ambessa_q2_first`；本包把最大生命 `q2_pct`%
//!   给离她最近的那个（直线上的第一个）。0.1.1（2026-11-03 晚的日志：重击放了几百次，一行 `FIRST` 也没有）：副本在同一拍给她挂
//!   `q2_on`、放出直线，直线 2 拍后才打中、挂上标记；0.1.0 看到 `q2_on` 当拍就摘掉、去找标记，一个也没有，加伤从来没打出去。
//!   现在看到 `q2_on` 起等 `Q2_WAIT` 拍（`q2_watch`），标记来了才打、才摘 `q2_on`，没等到就记一行 `FIRST none`。
//! - **拒斥挨打才强化**：主包读不到「她挨没挨打」，砸地总对英雄加伤。副本格挡时给她挂 `league_ambessa_w_on`；本包在这期间
//!   她被敌方英雄或野怪打到时挂 `league_ambessa_w_hit`，砸地才对打中的所有敌人加伤（数据读它）。
//! - **公开处决闪到一条线上最远的英雄**：主包只能闪到技能的目标。副本的大招只给目标挂 `league_ambessa_r_aim`、给她挂
//!   `league_ambessa_r_go`；本包在她到目标这条线上（`r_range` 长、`r_w` 半宽）找最远的敌方英雄，把她放到它身边、按住
//!   （`r_sup` 拍眩晕），`r_slam` 拍后砸下（`r_dmg` + `r_ratio`% 攻击 + 最大生命 `r_pct`%，眩晕 `r_stun` 拍），再接连招：
//!   狡诈横扫冷却清零并马上扫（`league_ambessa_q_go`，控制器读它）、拒斥就绪、强化普攻（龙犬之步）。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。玩法的状态不用全局变量，服务端
//! 预模拟和你看的那场各算各的；只有日志的条数是整次启动一个计数（0.1.1：以前每局重新数，每局都写前 40 条，一次启动 2411 行里
//! `TIP` 1418 行）。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ambessa.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_ambessa";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_ambessa") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// League's names for the flags and marks the data and this add-on share (`league_ambessa_<x>`).
fn n(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AMBESSA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ambessa.log");
        }
    }
    PathBuf::from("league_ambessa.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (league_olaf_rage's lesson: opening it for every line stalled the simulation thread)
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

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).unwrap_or_else(|| format!("#{id}"))
}

/// 日志条数（0.1.1，2026-11-03 晚的日志：计数在每个安蓓萨的被动上，每局重新从 1 数，一次启动 2411 行里 `TIP` 1418 行）：
/// 每种整次启动一个计数，服务器的预模拟先写 `LOG_FIRST` 条、之后每 `LOG_EVERY` 条一条；你看的那场每条都写。
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

/// The `Params` the log showed last (they come from the champion data: the same in every sim of a launch).
static PARAMS_SHOWN: Mutex<Option<Params>> = Mutex::new(None);

/// `p` not in the log yet: once a launch, again only if they ever differ (league_talon_vault's way; every Ambessa of
/// every presim wrote them at every spawn).
fn params_new(p: &Params) -> bool {
    let mut shown = PARAMS_SHOWN.lock().unwrap_or_else(|e| e.into_inner());
    if shown.as_ref() == Some(p) {
        return false;
    }
    *shown = Some(p.clone());
    true
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 控制器的周期（拍）：大招给的 `q_go` 留到下一次控制器之后。
    pub ctl_p: usize,
    /// 强化普攻留多少拍、攻速加多少百分比（龙犬之步）。
    pub pw_t: usize,
    pub pw_as: usize,
    /// 横扫的半径；离她这么多百分比的半径以外算刀尖；刀尖加伤（最大生命百分比）。
    pub q_r: usize,
    pub q_tip: usize,
    pub q_pct: usize,
    /// 裂地重击对第一个敌人的加伤（最大生命百分比）。
    pub q2_pct: usize,
    /// 大招找人的直线：长、半宽。
    pub r_range: usize,
    pub r_w: usize,
    /// 按住多少拍、多少拍后砸下。
    pub r_sup: usize,
    pub r_slam: usize,
    /// 砸下：固定伤害、攻击力百分比、最大生命百分比、眩晕拍数。
    pub r_dmg: usize,
    pub r_ratio: usize,
    pub r_pct: usize,
    pub r_stun: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { ctl_p: 3, pw_t: 180, pw_as: 50, q_r: 30000, q_tip: 60, q_pct: 3, q2_pct: 4, r_range: 60000, r_w: 8000,
               r_sup: 36, r_slam: 30, r_dmg: 115, r_ratio: 85, r_pct: 5, r_stun: 36 }
    }
}

/// `{"q_r":30000,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "ctl_p" => p.ctl_p = v,
            "pw_t" => p.pw_t = v,
            "pw_as" => p.pw_as = v,
            "q_r" => p.q_r = v,
            "q_tip" => p.q_tip = v,
            "q_pct" => p.q_pct = v,
            "q2_pct" => p.q2_pct = v,
            "r_range" => p.r_range = v,
            "r_w" => p.r_w = v,
            "r_sup" => p.r_sup = v,
            "r_slam" => p.r_slam = v,
            "r_dmg" => p.r_dmg = v,
            "r_ratio" => p.r_ratio = v,
            "r_pct" => p.r_pct = v,
            "r_stun" => p.r_stun = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

/// pct% of a maximum health (at least 1).
pub fn share(max_hp: usize, pct: usize) -> usize {
    (max_hp * pct / 100).max(1)
}

/// Is a unit this far from her (squared distance between the centres) at the sweep's edge?
pub fn at_edge(p: &Params, dist_sq: u64) -> bool {
    let tip = (p.q_r * p.q_tip / 100) as u64;
    dist_sq >= tip * tip
}

/// R's slam: r_dmg + r_ratio% of her attack + r_pct% of the champion's maximum health (before armour).
pub fn slam_damage(p: &Params, attack: usize, max_hp: usize) -> usize {
    p.r_dmg + attack * p.r_ratio / 100 + max_hp * p.r_pct / 100
}

/// How long after her `q2_on` shows up Q2's marks are looked for. The copy adds the 4-tick `q2_on` and starts the line
/// in the same tick; the line (delay 2, apply 1) marks what it hits 2-3 ticks later, the marks last 4 ticks.
pub const Q2_WAIT: usize = 8;

/// Q2's wait for the line's marks, one update: `wait` = the last tick it still looks (None: no Q2 pending), `on` = her
/// `q2_on` is there, `marks` = an enemy carries `q2_first`. Returns the new wait and what came of it: Some(true) = the
/// marks are in (deal the bonus, take `q2_on` off), Some(false) = none came in time (the line hit nobody).
/// 0.1.0 took `q2_on` off and looked for the marks on the first update it saw it, before the line had hit anything.
pub fn q2_watch(wait: Option<usize>, on: bool, marks: bool, tick: usize) -> (Option<usize>, Option<bool>) {
    let Some(until) = wait.or(on.then_some(tick + Q2_WAIT)) else { return (None, None) };
    if marks {
        (None, Some(true))
    } else if tick >= until {
        (None, Some(false))
    } else {
        (Some(until), None)
    }
}

/// The farthest of `foes` (id, position) on the line from `from` through `aim`: along it 0..=r_range, at most r_w off
/// it. The aimed champion itself always counts (the AI cast on it within the ult's range).
pub fn farthest_on_line(p: &Params, from: (u64, u64), aim: (usize, (u64, u64)), foes: &[(usize, (u64, u64))])
                        -> usize {
    let (fx, fy) = (from.0 as f64, from.1 as f64);
    let (dx, dy) = (aim.1 .0 as f64 - fx, aim.1 .1 as f64 - fy);
    let len = (dx * dx + dy * dy).sqrt();
    if len < 1.0 {
        return aim.0;
    }
    let (ux, uy) = (dx / len, dy / len);
    let mut best = (aim.0, len);
    for &(id, (x, y)) in foes {
        let (vx, vy) = (x as f64 - fx, y as f64 - fy);
        let along = vx * ux + vy * uy;
        let off = (vx * uy - vy * ux).abs();
        if along >= 0.0 && along <= p.r_range as f64 && off <= p.r_w as f64 && along > best.1 {
            best = (id, along);
        }
    }
    best.0
}

/// Where she lands: `gap` short of the champion, on her side of it (the map's coordinates are unsigned).
pub fn blink_spot(from: (u64, u64), to: (u64, u64), gap: u64) -> (u64, u64) {
    let (dx, dy) = (from.0 as f64 - to.0 as f64, from.1 as f64 - to.1 as f64);
    let len = (dx * dx + dy * dy).sqrt();
    if len <= gap as f64 || len < 1.0 {
        return from;
    }
    let k = gap as f64 / len;
    ((to.0 as f64 + dx * k).round().max(0.0) as u64, (to.1 as f64 + dy * k).round().max(0.0) as u64)
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn cc_immune(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.cc_immune))
}

/// The living enemies of `team` carrying `mark` (any unit: the sweep and the line hit minions and monsters too).
fn marked(sim: &StableSim<'_>, team: usize, mark: &str) -> Vec<usize> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.team() != team && e.is_alive())
        .map(|e| e.id())
        .collect::<Vec<_>>()
        .into_iter()
        .filter(|&id| has(sim, id, mark))
        .collect()
}

// ===================== 被动 =====================

/// 每个安蓓萨一份：参数、等着砸下的大招、等着标记的重击。
#[derive(Clone, Default)]
struct Matriarch {
    p: Params,
    /// R: (the pinned champion, the tick of the slam).
    slam: Option<(usize, usize)>,
    /// Q2: the last tick its marks are looked for (`q2_watch`; None: no Q2 pending).
    q2_wait: Option<usize>,
}

impl Matriarch {
    /// Q: the % max-health part on the units at the blade's edge only.
    fn sweep(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let mark = n("q_edge");
        for id in marked(sim, team, &mark) {
            sim.entity_remove_buff(id, &mark);
            if !at_edge(&self.p, sim.distance_sq(me, id)) {
                continue;
            }
            let Some(max_hp) = sim.get_entity(id).map(|e| e.hp().1) else { continue };
            let dmg = share(max_hp, self.p.q_pct);
            sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
            sim.play_view_effect(&n("q_tip"), me, &InputTargetV1::target(id), 0, 0, 0);
            if let Some(k) = tally(sim, "tip") {
                wlog(format!("{} TIP #{k} {} at the blade's edge: {dmg}", head(sim, me), name_of(sim, id)));
            }
        }
    }

    /// Q2 (Sundering Slam), once a `q2_on` showed up: waits for the line's marks (`q2_watch`); when they are in, the bonus
    /// on the first enemy on the line (the one nearest her) and `q2_on` comes off.
    fn sundering(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let on = has(sim, me, &n("q2_on"));
        if !on && self.q2_wait.is_none() {
            return;
        }
        let mark = n("q2_first");
        let hit = marked(sim, team, &mark);
        let (wait, done) = q2_watch(self.q2_wait, on, !hit.is_empty(), sim.tick());
        self.q2_wait = wait;
        match done {
            Some(true) => {
                sim.entity_remove_buff(me, &n("q2_on"));
                self.first(sim, me, &hit);
            }
            Some(false) => {
                sim.entity_remove_buff(me, &n("q2_on"));
                if let Some(k) = tally(sim, "first_none") {
                    wlog(format!("{} FIRST none #{k}: no mark from the slam's line within {Q2_WAIT} ticks", head(sim, me)));
                }
            }
            None => {}
        }
    }

    /// Q2: the bonus on the first enemy on the line (the one nearest her) of the units it marked (`hit`).
    fn first(&mut self, sim: &mut StableSim<'_>, me: usize, hit: &[usize]) {
        let mark = n("q2_first");
        for &id in hit {
            sim.entity_remove_buff(id, &mark);
        }
        let Some(&id) = hit.iter().min_by_key(|&&id| sim.distance_sq(me, id)) else { return };
        let Some(max_hp) = sim.get_entity(id).map(|e| e.hp().1) else { return };
        let dmg = share(max_hp, self.p.q2_pct);
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
        if let Some(k) = tally(sim, "first") {
            wlog(format!("{} FIRST #{k} {} first of {} on the slam: {dmg}", head(sim, me), name_of(sim, id), hit.len()));
        }
    }

    /// R, on r_go: the farthest champion on the line, the blink and the pin.
    fn execute(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let aim_mark = n("r_aim");
        let champs: Vec<(usize, (u64, u64))> = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter_map(|id| sim.get_entity(id).map(|e| (id, e.team(), e.is_alive(), e.pos())))
            .filter(|&(_, t, alive, _)| t != team && alive)
            .map(|(id, _, _, pos)| (id, pos))
            .collect();
        let aim = champs.iter().copied().find(|&(id, _)| has(sim, id, &aim_mark));
        for &(id, _) in &champs {
            sim.entity_remove_buff(id, &aim_mark);
        }
        let Some(aim) = aim else {
            if let Some(k) = tally(sim, "r_none") {
                wlog(format!("{} R none #{k}: no aimed champion left (dead or gone): nothing", head(sim, me)));
            }
            return;
        };
        let Some(from) = sim.get_entity(me).map(|e| e.pos()) else { return };
        let foe = farthest_on_line(&self.p, from, aim, &champs);
        let Some(to) = sim.get_entity(foe).map(|e| e.pos()) else { return };
        let gap = sim.get_entity(me).map_or(0, |e| e.radius()) + sim.get_entity(foe).map_or(0, |e| e.radius());
        let spot = blink_spot(from, to, gap as u64);
        sim.entity_set_pos(me, spot.0, spot.1);
        if !cc_immune(sim, foe) {
            sim.apply_cc(foe, &CcV1::stun(self.p.r_sup as u64));
        }
        sim.play_view_effect(&n("r_pin"), me, &InputTargetV1::target(foe), 0, 0, 0);
        sim.play_sfx(&n("r_pin"), me, &InputTargetV1::target(foe));
        self.slam = Some((foe, sim.tick() + self.p.r_slam));
        if let Some(k) = tally(sim, "r") {
            wlog(format!("{} R #{k} aimed at {}, the farthest on the line {}{}: blinked {} -> {:?}", head(sim, me),
                         name_of(sim, aim.0), name_of(sim, foe), if foe == aim.0 { "" } else { " (another)" },
                         ((from.0 as f64 - to.0 as f64).hypot(from.1 as f64 - to.1 as f64)).round(), spot));
        }
    }

    /// R, r_slam ticks after the pin: the slam and the combos.
    fn slam(&mut self, sim: &mut StableSim<'_>, me: usize, foe: usize) {
        let Some((alive, max_hp)) = sim.get_entity(foe).map(|e| (e.is_alive(), e.hp().1)) else { return };
        if !alive {
            return;
        }
        let attack = sim.get_entity(me).map_or(0, |e| e.stat().attack);
        let dmg = slam_damage(&self.p, attack, max_hp);
        sim.deal_damage_typed(me, foe, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
        if !cc_immune(sim, foe) {
            sim.apply_cc(foe, &CcV1::stun(self.p.r_stun as u64));
        }
        sim.play_view_effect(&n("r_crash"), me, &InputTargetV1::target(foe), 0, 0, 0);
        sim.play_sfx(&n("r_crash"), me, &InputTargetV1::target(foe));
        // R -> Q -> Q2 (the controller sweeps the champion on q_go) and Repudiation ready; the Step's empowered attack
        sim.entity_remove_buff(me, &n("q_cd"));
        sim.entity_remove_buff(me, &n("w_cd"));
        sim.entity_remove_buff(me, &n("q_go"));
        sim.add_buff(me, &BuffV1::timed(&n("q_go"), self.p.ctl_p + 30));
        sim.entity_remove_buff(me, &n("pw"));
        let mut pw = BuffV1::timed(&n("pw"), self.p.pw_t);
        pw.attack_speed_mult = self.p.pw_as as i32;
        sim.add_buff(me, &pw);
        if let Some(k) = tally(sim, "slam") {
            wlog(format!("{} SLAM #{k} {}: {dmg}, stunned {} ticks; Q and W ready", head(sim, me), name_of(sim, foe),
                         self.p.r_stun));
        }
    }
}

impl StablePassive for Matriarch {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.slam = None;
        self.q2_wait = None;
        // the Params in the first SPAWN line of a launch only; the line itself capped in the presims (0.1.1)
        let params = params_new(&self.p).then(|| format!(", {:?}", self.p));
        if tally(sim, "spawn").is_some() || params.is_some() {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN: the add-on's Ambessa (player {player}, team {team}){}", head(sim, me),
                         params.unwrap_or_default()));
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, _: usize) {
        // W: struck while braced by an enemy champion or monster (League: a champion or a large monster)
        if !has(sim, me, &n("w_on")) || has(sim, me, &n("w_hit")) {
            return;
        }
        let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
        let Some((kind, side)) = sim.get_entity(attacker).map(|e| (e.kind(), e.team())) else { return };
        if side == team || !matches!(kind, Some(EntityKindV1::Champion | EntityKindV1::Jungle | EntityKindV1::Epic)) {
            return;
        }
        sim.add_buff(me, &BuffV1::timed(&n("w_hit"), 60));
        if let Some(k) = tally(sim, "brace") {
            wlog(format!("{} BRACE #{k} struck by {}: the slam is empowered", head(sim, me), name_of(sim, attacker)));
        }
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        self.slam = None;
        self.q2_wait = None;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((alive, team)) = sim.get_entity(me).map(|e| (e.is_alive(), e.team())) else { return };
        if !alive {
            self.slam = None;
            self.q2_wait = None;
            return;
        }
        if has(sim, me, &n("q_on")) {
            self.sweep(sim, me, team);
        }
        // Q2's marks come 2-3 ticks after its q2_on (0.1.1: q2_on was taken off before they came, 0 FIRST lines)
        self.sundering(sim, me, team);
        if has(sim, me, &n("r_go")) {
            sim.entity_remove_buff(me, &n("r_go"));
            self.execute(sim, me, team);
        }
        if let Some((foe, at)) = self.slam {
            if sim.tick() >= at {
                self.slam = None;
                self.slam(sim, me, foe);
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
        "=== {ID} v{VERSION} (the sweep's edge, the slam's first, the brace when struck, the farthest execution) loaded: \
         game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:matriarch"), Matriarch::default());
    host.log(LogLevel::Info, "league_ambessa loaded (the sweep's edge, the slam's first, the brace when struck, the farthest execution).");
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
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"q_r":20000,"r_w":5000,"x":1}"#);
        assert_eq!(p, Params { q_r: 20000, r_w: 5000, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn only_the_blade_s_edge_takes_the_sweep_s_bonus() {
        let p = Params::default(); // edge from 18000
        assert!(!at_edge(&p, 17999 * 17999));
        assert!(at_edge(&p, 18000 * 18000));
        assert!(at_edge(&p, 29000 * 29000));
        assert_eq!(share(2000, 3), 60);
        assert_eq!(share(10, 3), 1);
    }

    #[test]
    fn the_execution_takes_the_farthest_champion_on_the_line() {
        let p = Params::default();
        let me = (100000, 100000);
        let aim = (1, (120000, 100000));
        let foes = [aim, (2, (150000, 105000)), (3, (159000, 100000)), (4, (140000, 120000)), (5, (80000, 100000)),
                    (6, (170000, 100000))];
        // 2 on the line, 3 farther on it, 4 off it, 5 behind her, 6 past the range
        assert_eq!(farthest_on_line(&p, me, aim, &foes), 3);
        assert_eq!(farthest_on_line(&p, me, aim, &[aim]), 1);
        assert_eq!(farthest_on_line(&p, me, (1, me), &foes), 1);
    }

    #[test]
    fn she_lands_beside_the_champion_on_her_side() {
        assert_eq!(blink_spot((0, 0), (10000, 0), 3000), (7000, 0));
        assert_eq!(blink_spot((10000, 10000), (10000, 2000), 3000), (10000, 5000));
        assert_eq!(blink_spot((0, 0), (1000, 0), 3000), (0, 0)); // already beside it
    }

    #[test]
    fn the_slam_scales_with_attack_and_max_health() {
        let p = Params::default();
        assert_eq!(slam_damage(&p, 200, 2000), 115 + 170 + 100);
    }

    /// One Ambessa's Q2s over ticks 0..60: `casts` put the 4-tick `q2_on` on her, the line marks what it hit at each of
    /// `marked_at` (4 ticks); an outcome takes `q2_on` off, a hit the marks too (as the passive does). The tick and the
    /// outcome of each.
    fn q2_run(casts: &[usize], marked_at: &[usize]) -> Vec<(usize, bool)> {
        let (mut wait, mut on_until, mut marks_until) = (None, 0, 0);
        let mut out = Vec::new();
        for tick in 0..60 {
            if casts.contains(&tick) {
                on_until = tick + 4;
            }
            if marked_at.contains(&tick) {
                marks_until = tick + 4;
            }
            let (w, done) = q2_watch(wait, tick < on_until, tick < marks_until, tick);
            wait = w;
            if let Some(d) = done {
                on_until = 0;
                if d {
                    marks_until = 0;
                }
                out.push((tick, d));
            }
        }
        out
    }

    #[test]
    fn q2_waits_for_the_line_s_marks() {
        // the 11-03 night logs: hundreds of Q2 casts, 0 FIRST lines - q2_on (4 ticks) shows up the tick the line starts,
        // the line marks what it hits 2-3 ticks later; 0.1.0 took q2_on off and looked on the first tick
        assert_eq!(q2_run(&[10], &[12]), [(12, true)]);
        assert_eq!(q2_run(&[10], &[13]), [(13, true)]);
        // marks that come after q2_on ran out still count, within Q2_WAIT of it
        assert_eq!(q2_run(&[10], &[15]), [(15, true)]);
        // the line hit nobody: one "none", when the wait runs out
        assert_eq!(q2_run(&[10], &[]), [(10 + Q2_WAIT, false)]);
        // marks with no Q2 pending are not this add-on's to take
        assert_eq!(q2_run(&[], &[5]), []);
        // two casts: each its own outcome
        assert_eq!(q2_run(&[10, 40], &[13]), [(13, true), (40 + Q2_WAIT, false)]);
        assert_eq!(q2_run(&[10, 40], &[12, 42]), [(12, true), (42, true)]);
    }

    #[test]
    fn presim_lines_are_capped_for_the_launch_and_the_match_on_screen_is_not() {
        let logged: Vec<usize> = (0..LOG_EVERY * 3).filter_map(|_| noted("test presim", false)).collect();
        assert_eq!(logged.len(), LOG_FIRST + 3);
        assert_eq!(logged[LOG_FIRST..], [LOG_EVERY, LOG_EVERY * 2, LOG_EVERY * 3]);
        assert!((0..LOG_EVERY * 2).all(|_| noted("test shown", true).is_some()));
    }

    #[test]
    fn the_params_are_logged_once() {
        let p = Params::default();
        assert!(params_new(&p));
        assert!(!params_new(&p));
        assert!(params_new(&Params { q2_pct: 9, ..Params::default() }), "other Params: again");
    }

    #[test]
    fn names_are_the_data_s() {
        for x in ["q_edge", "q_on", "q2_first", "q2_on", "w_on", "w_hit", "r_aim", "r_go", "q_go", "q_cd", "w_cd", "pw"] {
            assert_eq!(n(x), format!("league_ambessa_{x}"));
        }
    }
}
