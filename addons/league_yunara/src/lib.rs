//! 芸阿娜附加包（用户 2026-10-17：「方案可以，全按推荐做（下路 ADC，基础暴击 10%，做附加包，R 形态换待机/跑步，PPU 1.5）」）。主包保持纯
//! 数据；`mod.override_info` 把主包的芸阿娜换成 `override/` 里的副本（`make_override.py` 用 tools/kit/build_yunara.py 的 `native=1`
//! 生成：被动 `league_yunara:faith`），本包补数据做不到的事：
//!
//! - **夜影翻往哪冲**（超凡形态里的 E）：每 tick 判断，挂 `re_f` / `re_b` 标记给数据；数据播翻身动作时挂 `re_go`，本包看到就逐 tick
//!   把她挪过去（`re_v` x `re_t`）。最近的敌方英雄残血（35% 以下）又在攻击距离 80% 以外，就往前冲把它拉进射程；它贴身（`e_close` 内）
//!   或她自己残血（40% 以下）就往后冲、背离它。身边没有敌方英雄时两个标记都不挂，数据照主包：贴身往后冲，不然加速。
//! - **明踪步朝英雄跑时更快**：主包副本里明踪步只给 `e_ms`%；她身上有明踪步的加速、而且实际在朝最近的敌方英雄移动（3 tick 里走了 300 以上，
//!   方向和指向它的方向夹角小于 45°）时，本包挂 `e_toward`（移速再加 `e_ms2 - e_ms`%），不朝它跑了就摘掉（英雄联盟的 1.5 倍）。
//! - **定圣诀按真实血量开**：主包只看人数（附近 2 个以上敌方英雄）和控制；本包另外在大招射程内有敌方英雄残血（40% 以下），或她自己残血
//!   （50% 以下）而且有敌方英雄在攻击距离内时挂 `r_ok`，数据看到就开。
//! - **超凡形态整身换待机 / 跑步**（view.rs）：大招期间（身上有 `league_yunara_r_on`）站着、跑着都画成带金边和光环的 `r_idle` / `r_run`。
//!
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志：
//! `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yunara.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `DASH`（往哪冲、为什么）、`DASH DONE`（实际挪了多远）、`TOWARD`（明踪步加成开关）、`RISE`（大招开了，是本包的 r_ok 还是主包的条件）、
//! `FORM`（显示里换形态），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_yunara";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 数据和本包之间的标记（主包数据的施法者 buff 名）。
pub const RE_F: &str = "league_yunara_re_f";
pub const RE_B: &str = "league_yunara_re_b";
pub const RE_GO: &str = "league_yunara_re_go";
pub const E_MS: &str = "league_yunara_e_ms";
pub const E_TOWARD: &str = "league_yunara_e_toward";
pub const R_OK: &str = "league_yunara_r_ok";
pub const R_ON: &str = "league_yunara_r_on";
/// 地图边长（坐标 0..MAP）。
const MAP: f64 = 960_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_YUNARA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_yunara.log");
        }
    }
    PathBuf::from("league_yunara.log")
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
const LOG_EVERY: usize = 50;

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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，make_override.py 从 P 写进副本）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub atk_range: usize,
    pub e_close: usize,
    pub re_v: usize,
    pub re_t: usize,
    pub r_range: usize,
    pub e_ms: usize,
    pub e_ms2: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { atk_range: 57500, e_close: 35000, re_v: 2600, re_t: 14, r_range: 70000, e_ms: 40, e_ms2: 60 }
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
            "atk_range" => p.atk_range = v,
            "e_close" => p.e_close = v,
            "re_v" => p.re_v = v,
            "re_t" => p.re_t = v,
            "r_range" => p.r_range = v,
            "e_ms" => p.e_ms = v,
            "e_ms2" => p.e_ms2 = v,
            _ => {}
        }
    }
    p
}

static SHARED: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

fn shared() -> Params {
    SHARED.lock().unwrap_or_else(|e| e.into_inner()).clone()
}

// ===================== 计算（单元测试用） =====================

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

pub fn clamp(p: Pt) -> Pt {
    (p.0.clamp(0.0, MAP - 1.0), p.1.clamp(0.0, MAP - 1.0))
}

/// 一个看得见的敌方英雄：id、位置、生命百分比。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub at: Pt,
    pub hp_pct: usize,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Dash {
    /// 朝 `Foe` 冲。
    Forward(Foe),
    /// 背离 `Foe` 冲。
    Back(Foe),
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum DashWhy {
    /// 它残血又快出射程：追。
    Chase,
    /// 它贴身：拉开。
    Close,
    /// 她自己残血：退。
    SelfLow,
}

pub fn nearest(me: Pt, foes: &[Foe], within: f64) -> Option<Foe> {
    foes.iter().filter(|f| dist(me, f.at) <= within).min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at))).copied()
}

/// 夜影翻往哪冲（只看攻击距离 1.4 倍内最近的敌方英雄；没有就 None，数据照主包）。
pub fn dash_choice(me: Pt, my_hp_pct: usize, foes: &[Foe], p: &Params) -> Option<(Dash, DashWhy)> {
    let near = nearest(me, foes, p.atk_range as f64 * 1.4)?;
    let d = dist(me, near.at);
    if near.hp_pct < 35 && d > p.atk_range as f64 * 0.8 && my_hp_pct >= 40 {
        return Some((Dash::Forward(near), DashWhy::Chase));
    }
    if d <= p.e_close as f64 {
        return Some((Dash::Back(near), DashWhy::Close));
    }
    if my_hp_pct < 40 {
        return Some((Dash::Back(near), DashWhy::SelfLow));
    }
    None
}

/// 单位方向：往前 = 朝目标，往后 = 背离目标；重合时往后朝画面左边（-x）、往前朝右。
pub fn dash_dir(me: Pt, dash: Dash) -> Pt {
    let (to, sign) = match dash {
        Dash::Forward(f) => (f.at, 1.0),
        Dash::Back(f) => (f.at, -1.0),
    };
    let (dx, dy) = (to.0 - me.0, to.1 - me.1);
    let l = (dx * dx + dy * dy).sqrt();
    if l < 1.0 {
        return (sign, 0.0);
    }
    (sign * dx / l, sign * dy / l)
}

/// 「朝它跑」：从 `before` 到 `now` 走了 `min_step` 以上，方向和指向 `foe` 的方向夹角小于 45°。
pub fn moving_toward(before: Pt, now: Pt, foe: Pt, min_step: f64) -> bool {
    let (mx, my) = (now.0 - before.0, now.1 - before.1);
    let ml = (mx * mx + my * my).sqrt();
    let (fx, fy) = (foe.0 - now.0, foe.1 - now.1);
    let fl = (fx * fx + fy * fy).sqrt();
    if ml < min_step || fl < 1.0 {
        return false;
    }
    (mx * fx + my * fy) / (ml * fl) > std::f64::consts::FRAC_1_SQRT_2
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum RiseWhy {
    /// 大招射程内有残血（40% 以下）的敌方英雄。
    Kill,
    /// 她自己残血（50% 以下）而且有敌方英雄在攻击距离内。
    Desperate,
}

/// 定圣诀的本包条件（主包的人数 / 控制条件之外）。
pub fn rise_arm(me: Pt, my_hp_pct: usize, foes: &[Foe], p: &Params) -> Option<RiseWhy> {
    if foes.iter().any(|f| f.hp_pct < 40 && dist(me, f.at) <= p.r_range as f64) {
        return Some(RiseWhy::Kill);
    }
    if my_hp_pct < 50 && nearest(me, foes, p.atk_range as f64).is_some() {
        return Some(RiseWhy::Desperate);
    }
    None
}

// ===================== 被动：不破之誓 =====================

#[derive(Clone, Copy)]
struct Dashing {
    dir: Pt,
    left: usize,
    /// 起点、游戏拒绝挪人的次数（日志 DASH DONE 用：Kalista 的教训，挪人一定要记实际挪了多远）。
    from: Pt,
    refused: usize,
}

#[derive(Clone, Default)]
struct Faith {
    /// 现在挂着的冲刺方向标记、上次挂的 tick。
    dash_flag: Option<(&'static str, usize)>,
    dashing: Option<Dashing>,
    /// 最近几 tick 的位置（明踪步判断朝哪跑）。
    trail: Vec<(usize, Pt)>,
    toward: bool,
    /// r_ok 上次挂的 tick、为什么。
    rise: Option<(usize, RiseWhy)>,
    /// 上一 tick 她身上有没有 r_on（大招刚开时记一行 RISE）。
    risen: bool,
}

fn ent_has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| ent_has(&e, name))
}

/// 硬控（击飞、晕眩、定身、嘲讽、恐惧、魅惑、被强制位移）。不是 `cc_count() > 0`：游戏把正在播的施法动作也记成一种控制
/// （`CcKindV1::Animation`），翻身的动作一开始就会把挪人叫停（卡莉丝塔附加包的教训）。
const HARD_CC: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                                CcKindV1::Charm, CcKindV1::ForceMove];

fn hard_cc(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
    })
}

fn pos_of(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

fn hp_pct(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(100, |e| {
        let (hp, max) = e.hp();
        if max == 0 { 100 } else { hp * 100 / max }
    })
}

fn foes(sim: &StableSim<'_>, team: usize) -> Vec<Foe> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_champion() || !u.is_targetable() || !sim.is_visible(team, u.id()) {
            continue;
        }
        let (hp, max) = u.hp();
        out.push(Foe { id: u.id(), at: (u.pos().0 as f64, u.pos().1 as f64), hp_pct: if max == 0 { 100 } else { hp * 100 / max } });
    }
    out
}

fn set_flag(sim: &mut StableSim<'_>, me: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(me, name);
    sim.add_buff(me, &BuffV1::timed(name, ticks));
}

impl Faith {
    fn update_dash(&mut self, sim: &mut StableSim<'_>, me: usize, at: Pt, fs: &[Foe], p: &Params) {
        let tick = sim.tick();
        let my_hp = hp_pct(sim, me);
        // the way only matters in the Transcendent State (E is the dash there); off it the flags come down
        let choice = if has_buff(sim, me, R_ON) { dash_choice(at, my_hp, fs, p) } else { None };
        let want = match choice {
            Some((Dash::Forward(_), _)) => Some(RE_F),
            Some((Dash::Back(_), _)) => Some(RE_B),
            None => None,
        };
        let had = self.dash_flag.map(|(n, _)| n);
        if want != had || self.dash_flag.is_some_and(|(_, t)| tick >= t + 3) {
            if let Some(old) = had.filter(|o| Some(*o) != want) {
                sim.entity_remove_buff(me, old);
            }
            self.dash_flag = None;
            if let Some(n) = want {
                set_flag(sim, me, n, 5);
                self.dash_flag = Some((n, tick));
            }
        }
        // the data played the flip: move her
        if has_buff(sim, me, RE_GO) && self.dashing.is_none() {
            sim.entity_remove_buff(me, RE_GO);
            if let Some((dash, why)) = choice {
                self.dashing = Some(Dashing { dir: dash_dir(at, dash), left: p.re_t.max(1), from: at, refused: 0 });
                if let Some(k) = counted("dash") {
                    let (way, f) = match dash {
                        Dash::Forward(f) => ("FORWARD to", f),
                        Dash::Back(f) => ("BACK from", f),
                    };
                    wlog(format!("{} DASH {way} {} ({why:?}, {:.0} away, {}% hp, hers {my_hp}%) #{k}", head(sim, me),
                                 who(sim, f.id), dist(at, f.at), f.hp_pct));
                }
            }
        }
        if let Some(d) = self.dashing.as_mut() {
            let held = hard_cc(sim, me);
            if d.left == 0 || held {
                if let Some(k) = counted("dash_done") {
                    wlog(format!("{} DASH DONE moved {:.0} of {} ({} steps refused{}) #{k}", head(sim, me), dist(d.from, at),
                                 p.re_v * p.re_t, d.refused, if held { ", cut by CC" } else { "" }));
                }
                self.dashing = None;
            } else {
                let step = p.re_v as f64;
                let next = clamp((at.0 + d.dir.0 * step, at.1 + d.dir.1 * step));
                if !sim.entity_set_pos(me, next.0.round() as u64, next.1.round() as u64) {
                    d.refused += 1;
                }
                d.left -= 1;
            }
        }
    }

    fn update_toward(&mut self, sim: &mut StableSim<'_>, me: usize, at: Pt, fs: &[Foe], p: &Params) {
        let tick = sim.tick();
        self.trail.retain(|(t, _)| tick < t + 4 && *t <= tick);
        self.trail.push((tick, at));
        let before = self.trail.first().map(|(_, b)| *b).unwrap_or(at);
        let quick = has_buff(sim, me, E_MS);
        let near = nearest(at, fs, p.atk_range as f64 * 2.0);
        let on = quick && near.is_some_and(|f| moving_toward(before, at, f.at, 300.0));
        if on {
            // a few ticks at a time, refreshed while she keeps running at it
            let mut b = BuffV1::timed(E_TOWARD, 4);
            b.move_speed_mult = p.e_ms2.saturating_sub(p.e_ms) as i32;
            sim.entity_remove_buff(me, E_TOWARD);
            sim.add_buff(me, &b);
        } else if self.toward {
            sim.entity_remove_buff(me, E_TOWARD);
        }
        if on != self.toward {
            if let Some(k) = counted("toward") {
                let f = near.map_or("-".into(), |f| who(sim, f.id));
                wlog(format!("{} TOWARD {} ({f}) #{k}", head(sim, me), if on { "on: +speed" } else { "off" }));
            }
            self.toward = on;
        }
    }

    fn update_rise(&mut self, sim: &mut StableSim<'_>, me: usize, at: Pt, fs: &[Foe], p: &Params) {
        let tick = sim.tick();
        let why = rise_arm(at, hp_pct(sim, me), fs, p);
        match why {
            Some(w) if self.rise.is_none_or(|(t, _)| tick >= t + 3) => {
                set_flag(sim, me, R_OK, 6);
                self.rise = Some((tick, w));
            }
            None if self.rise.is_some() => {
                sim.entity_remove_buff(me, R_OK);
                self.rise = None;
            }
            _ => {}
        }
        let risen = has_buff(sim, me, R_ON);
        if risen && !self.risen {
            if let Some(k) = counted("rise") {
                let by = match self.rise {
                    Some((t, w)) if tick <= t + 6 => format!("the add-on's r_ok ({w:?})"),
                    _ => "the main pack's gate (2+ champions or one in CC)".into(),
                };
                wlog(format!("{} RISE Transcend One's Self by {by}, {} enemy champions seen #{k}", head(sim, me), fs.len()));
            }
        }
        self.risen = risen;
    }
}

impl StablePassive for Faith {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let p = parse_params(params_json);
        let mut s = SHARED.lock().unwrap_or_else(|e| e.into_inner());
        if *s != p {
            wlog(format!("params {params_json} -> {p:?}"));
            *s = p;
        }
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        *self = Faith::default();
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN {} (the add-on's Yunara) #{k}", head(sim, entity), who(sim, entity)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        let Some(at) = pos_of(sim, me) else { return };
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let fs = foes(sim, team);
        let p = shared();
        self.update_dash(sim, me, at, &fs, &p);
        self.update_toward(sim, me, at, &fs, &p);
        self.update_rise(sim, me, at, &fs, &p);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Yunara: Untouchable Shadow's way, Kanmei's Steps toward a champion, Transcend One's Self by real health, the Transcendent body) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:faith"), Faith::default());
    view::install_once();
    host.log(LogLevel::Info, "league_yunara loaded (dash way, E toward a champion, R by real health, Transcendent body).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    fn foe(id: usize, at: Pt, hp_pct: usize) -> Foe {
        Foe { id, at, hp_pct }
    }

    #[test]
    fn params_from_the_main_pack() {
        assert_eq!(parse_params("{}"), Params::default());
        let p = parse_params(r#"{"re_v":3000,"junk":3,"e_ms2":70}"#);
        assert_eq!((p.re_v, p.e_ms2, p.re_t), (3000, 70, 14));
    }

    #[test]
    fn the_copy_carries_the_params_and_the_flags() {
        let copy = include_str!("../override/league_yunara.data_champion");
        let at = copy.find("\"passive_ref\": \"league_yunara:faith\"").expect("no league_yunara:faith passive in the copy");
        let params = &copy[at..];
        let d = Params::default();
        for (k, v) in [("atk_range", d.atk_range), ("e_close", d.e_close), ("re_v", d.re_v), ("re_t", d.re_t),
                       ("r_range", d.r_range), ("e_ms", d.e_ms), ("e_ms2", d.e_ms2)] {
            assert!(params.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in the copy's passive params");
        }
        for name in [RE_F, RE_B, RE_GO, E_MS, R_OK, R_ON] {
            assert!(copy.contains(&format!("\"{name}\"")), "{name} is not in the copy");
        }
        // the add-on's dash flags first; the main pack's MoveBack stays only for no enemy champion near (neither flag)
        let f = copy.find(RE_F).expect("the copy has no re_f switch");
        let back = copy.find("\"MoveBack\"").expect("the copy has no fallback dash");
        assert!(f < back, "the copy's MoveBack comes before the add-on's dash flags");
    }

    #[test]
    fn dash_back_when_close_or_low_forward_after_a_low_one() {
        let p = Params::default();
        let me = (0.0, 0.0);
        let close = foe(1, (20_000.0, 0.0), 100);
        assert_eq!(dash_choice(me, 100, &[close], &p), Some((Dash::Back(close), DashWhy::Close)));
        assert_eq!(dash_dir(me, Dash::Back(close)), (-1.0, 0.0));
        // a low one slipping out of range: chase it (not when she is low herself)
        let low = foe(2, (0.0, 60_000.0), 20);
        assert_eq!(dash_choice(me, 100, &[low], &p), Some((Dash::Forward(low), DashWhy::Chase)));
        assert_eq!(dash_dir(me, Dash::Forward(low)), (0.0, 1.0));
        assert_eq!(dash_choice(me, 30, &[low], &p), Some((Dash::Back(low), DashWhy::SelfLow)));
        // a healthy one at a comfortable range: no flag (the main pack's rule)
        assert_eq!(dash_choice(me, 100, &[foe(3, (50_000.0, 0.0), 90)], &p), None);
        // nobody near
        assert_eq!(dash_choice(me, 10, &[foe(4, (300_000.0, 0.0), 10)], &p), None);
    }

    #[test]
    fn toward_means_running_at_it() {
        let foe_at = (100_000.0, 0.0);
        assert!(moving_toward((0.0, 0.0), (1_000.0, 0.0), foe_at, 300.0));
        assert!(moving_toward((0.0, 0.0), (1_000.0, 800.0), foe_at, 300.0)); // 39 degrees off
        assert!(!moving_toward((0.0, 0.0), (1_000.0, 1_200.0), foe_at, 300.0)); // 50 degrees off
        assert!(!moving_toward((0.0, 0.0), (-1_000.0, 0.0), foe_at, 300.0)); // away
        assert!(!moving_toward((0.0, 0.0), (100.0, 0.0), foe_at, 300.0)); // standing
    }

    #[test]
    fn rise_by_a_low_foe_or_when_she_is_low_in_a_fight() {
        let p = Params::default();
        let me = (0.0, 0.0);
        assert_eq!(rise_arm(me, 100, &[foe(1, (60_000.0, 0.0), 30)], &p), Some(RiseWhy::Kill));
        assert_eq!(rise_arm(me, 100, &[foe(1, (90_000.0, 0.0), 30)], &p), None); // out of R's range
        assert_eq!(rise_arm(me, 40, &[foe(2, (50_000.0, 0.0), 90)], &p), Some(RiseWhy::Desperate));
        assert_eq!(rise_arm(me, 40, &[foe(2, (80_000.0, 0.0), 90)], &p), None); // nobody in attack range
        assert_eq!(rise_arm(me, 90, &[foe(2, (50_000.0, 0.0), 90)], &p), None);
    }
}
