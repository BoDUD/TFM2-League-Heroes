//! 辛德拉附加包：W「驱使念力」能举起小兵和野怪（用户：「辛德拉W的球应该要做成能举小兵和野怪吧 除了大小龙」）。
//!
//! 主包是纯数据：数据挑不出「只要小兵和普通野怪」的目标（大小龙也是「除防御塔外的敌人」），也不能把一个单位挪到指定的点，
//! 所以主包的 W 总是掷出一颗手里凝聚的法球。`mod.override_info` 把主包的辛德拉换成 `override/` 里的副本
//! （tools/kit/build_syndra.py 的 native=True）：技能一样，只是 W 施放时在她身上挂 `league_syndra_w_grab`、在投掷目标身上挂
//! `league_syndra_w_at`，掷出时她身上有 `league_syndra_w_unit` 就换成一个不显示的抛物线（落点照样伤害、减速，不留法球）。
//!
//! 本包的被动 `league_syndra:grab` 每 tick 看一次：
//! - 看到 `w_grab`（一次施放只处理一次）：她身上还记着法球（`league_syndra_o1`–`o4`，主包的计数）就什么都不做——和英雄联盟一样
//!   法球优先，数据照常掷法球；
//! - 没有法球：在她身边 `w_grab_r` 内找最近的一个敌方小兵或野怪（不要英雄、防御塔、投掷目标本身，也不要大龙 `epic_monster`、
//!   小龙 `serpen`），挂上 `w_unit`，把它击飞（期间不能行动）并沿路径逐 tick 摆到位置上（`entity_set_pos`）：先以 `w_lift_speed`
//!   飞到她身前 `HOLD` 处举着，第 `w_rel` tick（数据出手的那一刻）起 `w_fly` tick 飞到目标脚下（目标走动就跟着他的位置）。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。不用全局变量，服务端预模拟和你看的那场各算各的。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_syndra.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_syndra";

/// 主包辛德拉的名字（buff 都以它开头）。
fn sy(x: &str) -> String {
    format!("league_syndra_{x}")
}

/// 主包记法球的四个计数位。
pub const SLOTS: [&str; 4] = ["o1", "o2", "o3", "o4"];
/// 不举的野怪：大龙、小龙（名字里含这些）。
pub const DRAGONS: [&str; 2] = ["epic_monster", "serpen"];
/// 举着时在她身前多远（朝投掷目标的方向）。
pub const HOLD: f64 = 12_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SYNDRA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_syndra.log");
        }
    }
    PathBuf::from("league_syndra.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
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

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub w_rel: usize,
    pub w_fly: usize,
    pub w_grab_r: usize,
    pub w_lift_speed: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { w_rel: 12, w_fly: 16, w_grab_r: 60_000, w_lift_speed: 6_000 }
    }
}

/// `{"w_rel":12,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "w_rel" => p.w_rel = v,
            "w_fly" => p.w_fly = v,
            "w_grab_r" => p.w_grab_r = v,
            "w_lift_speed" => p.w_lift_speed = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn lerp(a: (f64, f64), b: (f64, f64), t: f64) -> (f64, f64) {
    let t = t.clamp(0.0, 1.0);
    (a.0 + (b.0 - a.0) * t, a.1 + (b.1 - a.1) * t)
}

/// 身边的一个单位（挑举谁时用）。
#[derive(Clone, Debug)]
pub struct Unit {
    pub id: usize,
    pub at: (f64, f64),
    pub champion: bool,
    pub tower: bool,
    pub minion: bool,
    pub team: usize,
    pub name: String,
}

/// 能举的：小兵或野怪（中立，或名字里有 monster），不是大小龙。
pub fn liftable(u: &Unit) -> bool {
    if u.champion || u.tower {
        return false;
    }
    if DRAGONS.iter().any(|d| u.name.contains(d)) {
        return false;
    }
    u.minion || u.team > 1 || u.name.contains("monster")
}

/// 举谁：`me` 身边 `reach` 内、不是 `my_team`、不是 `target` 的、能举的单位里最近的一个。
pub fn pick(units: &[Unit], me: (f64, f64), my_team: usize, target: usize, reach: f64) -> Option<usize> {
    units
        .iter()
        .filter(|u| u.team != my_team && u.id != target && liftable(u))
        .map(|u| (dist(me, u.at), u.id))
        .filter(|(d, _)| *d <= reach)
        .min_by(|a, b| a.0.total_cmp(&b.0))
        .map(|(_, id)| id)
}

/// 举着的位置：她身前 `HOLD`，朝目标的方向（目标和她重合时就在她身上）。
pub fn hold_point(me: (f64, f64), target: (f64, f64)) -> (f64, f64) {
    let d = dist(me, target);
    if d < 1.0 {
        return me;
    }
    (me.0 + (target.0 - me.0) / d * HOLD, me.1 + (target.1 - me.1) / d * HOLD)
}

/// 被举起的单位：从哪里来、举到哪里、何时出手、飞向哪里。
#[derive(Clone, Debug)]
pub struct Held {
    pub unit: usize,
    pub target: usize,
    pub from: (f64, f64),
    pub hold: (f64, f64),
    pub at: (f64, f64),
    pub start: usize,
    pub lift: usize,
}

impl Held {
    /// 第 `tick` 它该在哪里；`None` = 已经落地。
    pub fn place(&self, p: &Params, tick: usize) -> Option<(f64, f64)> {
        let k = tick.saturating_sub(self.start);
        if k < self.lift {
            return Some(lerp(self.from, self.hold, (k + 1) as f64 / self.lift.max(1) as f64));
        }
        if k < p.w_rel {
            return Some(self.hold);
        }
        let f = k - p.w_rel;
        if f < p.w_fly {
            return Some(lerp(self.hold, self.at, (f + 1) as f64 / p.w_fly.max(1) as f64));
        }
        None
    }

    pub fn ticks(&self, p: &Params) -> usize {
        p.w_rel + p.w_fly
    }
}

/// 举到身前要几 tick：按速度，最少 1，最多出手前 2 tick。
pub fn lift_ticks(p: &Params, d: f64) -> usize {
    let most = p.w_rel.saturating_sub(2).max(1);
    ((d / p.w_lift_speed.max(1) as f64).ceil() as usize).clamp(1, most)
}

// ===================== 小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    sim.get_entity(id).map(|e| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

fn alive(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive())
}

fn timed(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

// ===================== 被动 =====================

/// 每个辛德拉一份：参数、正举着的单位、已处理到哪个 tick 的施放。
#[derive(Clone, Default)]
struct Grab {
    p: Params,
    held: Option<Held>,
    done_until: usize,
    grabs: usize,
}

impl Grab {
    /// 举着 / 飞着的那个单位：摆到这一 tick 的位置；落地或它死了就放手。
    fn carry(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(h) = self.held.as_mut() else { return };
        let tick = sim.tick();
        if !alive(sim, h.unit) {
            wlog(format!("{} the lifted {} died in her hands", head(sim, me), who(sim, h.unit)));
            self.held = None;
            return;
        }
        // the throw follows the target while it flies, as the data's lob lands where he stood at the release
        let k = tick.saturating_sub(h.start);
        if k <= self.p.w_rel && alive(sim, h.target) {
            if let Some(t) = pos(sim, h.target) {
                h.at = t;
            }
        }
        match h.place(&self.p, tick) {
            Some(to) => {
                sim.entity_set_pos(h.unit, to.0.round().max(0.0) as u64, to.1.round().max(0.0) as u64);
            }
            None => {
                wlog(format!("{} {} landed at {}", head(sim, me), who(sim, h.unit), pt(h.at)));
                self.held = None;
            }
        }
    }

    /// 一次 W：法球优先；没有法球就举起身边最近的小兵或野怪。
    fn start(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        self.done_until = tick + self.p.w_rel + 2;
        if SLOTS.iter().any(|s| has_buff(sim, me, &sy(s))) {
            wlog(format!("{} W: a sphere is counted - the data throws it", head(sim, me)));
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let Some(here) = pos(sim, me) else { return };
        let mark = sy("w_at");
        let mut target = None;
        let mut units = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if !u.is_alive() || !u.is_targetable() {
                continue;
            }
            let (x, y) = u.pos();
            let id = u.id();
            if target.is_none() && (0..u.buff_count()).filter_map(|k| u.buff_at(k)).any(|b| b.name() == mark) {
                target = Some(id);
            }
            units.push(Unit {
                id,
                at: (x as f64, y as f64),
                champion: u.is_champion(),
                tower: u.is_tower(),
                minion: u.is_minion(),
                team: u.team(),
                name: u.name().unwrap_or_default(),
            });
        }
        let Some(target) = target else {
            wlog(format!("{} W: no unit carries {mark} - nothing to throw at", head(sim, me)));
            return;
        };
        let Some(unit) = pick(&units, here, team, target, self.p.w_grab_r as f64) else {
            wlog(format!("{} W: no minion or monster within {} - the data throws a sphere", head(sim, me), self.p.w_grab_r));
            return;
        };
        let (Some(from), Some(at)) = (pos(sim, unit), pos(sim, target)) else { return };
        let hold = hold_point(here, at);
        let lift = lift_ticks(&self.p, dist(from, hold));
        let held = Held { unit, target, from, hold, at, start: tick, lift };
        timed(sim, me, &sy("w_unit"), self.p.w_rel + self.p.w_fly + 4);
        let mut up = CcV1::of_kind(CcKindV1::Airborne, (held.ticks(&self.p) + 2) as u64);
        up.set_name(&sy("w_lift"));
        sim.apply_cc(unit, &up);
        self.grabs += 1;
        if self.grabs <= 60 || self.grabs % 25 == 0 {
            wlog(format!(
                "{} W #{}: lifts {} from {} to {} in {lift} ticks, throws it at {} {} on tick {}",
                head(sim, me),
                self.grabs,
                who(sim, unit),
                pt(from),
                pt(hold),
                who(sim, target),
                pt(at),
                tick + self.p.w_rel
            ));
        }
        self.held = Some(held);
        self.carry(sim, me);
    }
}

impl StablePassive for Grab {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.held = None;
        self.done_until = 0;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Syndra (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if !alive(sim, me) {
            self.held = None;
            return;
        }
        if self.held.is_some() {
            self.carry(sim, me);
            return;
        }
        if sim.tick() >= self.done_until && has_buff(sim, me, &sy("w_grab")) {
            self.start(sim, me);
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.held = None;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Syndra: Force of Will lifts a minion or monster when no sphere is counted, not the dragons) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:grab"), Grab::default());
    host.log(LogLevel::Info, "league_syndra v1 loaded (Syndra's W lifts minions and monsters).");
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

    fn unit(id: usize, x: f64, team: usize, name: &str) -> Unit {
        Unit {
            id,
            at: (x, 0.0),
            champion: name.starts_with("league_"),
            tower: name.contains("tower"),
            minion: name.contains("minion"),
            team,
            name: name.to_string(),
        }
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"w_rel":10,"w_grab_r":50000,"x":1}"#),
                   Params { w_rel: 10, w_grab_r: 50_000, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn minions_and_camps_but_never_the_dragons_champions_or_towers() {
        assert!(liftable(&unit(1, 0.0, 1, "melee_minion")));
        assert!(liftable(&unit(2, 0.0, 2, "rhino_monster")));
        assert!(liftable(&unit(3, 0.0, 2, "stump")));
        assert!(!liftable(&unit(4, 0.0, 2, "epic_monster")));
        assert!(!liftable(&unit(5, 0.0, 2, "serpen_monster")));
        assert!(!liftable(&unit(6, 0.0, 1, "league_garen")));
        assert!(!liftable(&unit(7, 0.0, 1, "tower")));
    }

    #[test]
    fn the_nearest_enemy_unit_in_reach_not_the_target_nor_her_own() {
        let units = vec![
            unit(1, 5_000.0, 0, "melee_minion"),      // hers
            unit(2, 20_000.0, 1, "range_minion"),     // the target of the throw
            unit(3, 30_000.0, 1, "melee_minion"),
            unit(4, 25_000.0, 2, "epic_monster"),
            unit(5, 70_000.0, 2, "rhino_monster"),    // out of reach
        ];
        assert_eq!(pick(&units, (0.0, 0.0), 0, 2, 60_000.0), Some(3));
        assert_eq!(pick(&units, (0.0, 0.0), 0, 3, 60_000.0), Some(2));
        assert_eq!(pick(&units[3..], (0.0, 0.0), 0, 2, 60_000.0), None);
    }

    #[test]
    fn lifted_to_her_held_then_thrown_at_the_target() {
        let p = Params::default();
        let me = (0.0, 0.0);
        let at = (80_000.0, 0.0);
        let hold = hold_point(me, at);
        assert_eq!(hold, (HOLD, 0.0));
        let from = (30_000.0, 30_000.0);
        let lift = lift_ticks(&p, dist(from, hold));
        assert!(lift >= 1 && lift <= p.w_rel - 2);
        let h = Held { unit: 9, target: 2, from, hold, at, start: 100, lift };
        assert_eq!(h.place(&p, 100 + lift - 1), Some(hold));
        assert_eq!(h.place(&p, 100 + p.w_rel - 1), Some(hold));
        let first = h.place(&p, 100 + p.w_rel).unwrap();
        assert!(first.0 > hold.0 && first.0 < at.0);
        assert_eq!(h.place(&p, 100 + p.w_rel + p.w_fly - 1), Some(at));
        assert_eq!(h.place(&p, 100 + p.w_rel + p.w_fly), None);
    }

    #[test]
    fn a_far_unit_still_reaches_her_before_the_throw() {
        let p = Params::default();
        assert_eq!(lift_ticks(&p, 1_000_000.0), p.w_rel - 2);
        assert_eq!(lift_ticks(&p, 1.0), 1);
    }
}
