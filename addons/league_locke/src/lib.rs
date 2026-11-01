//! 洛克附加包：数据做不到、和英雄联盟不一样的地方，这里照英雄联盟做。
//!
//! `mod.override_info` 把主包的洛克换成 `override/` 里的副本（tools/kit/build_locke.py --native），`passive` 换成本包的
//! `league_locke:exorcist`：
//!
//! - **圣银穿心按已损失生命加伤害**：主包只能附带固定的魔法伤害（数据读不到当前生命）。副本给普攻打中的单位挂 3 拍
//!   `league_locke_p_hit`；本包看到它，再打它**已损失生命 `p_miss`%** 的魔法伤害。
//! - **灵焰仪式按当前生命自伤、结束时补回**：主包每秒烧最大生命的 `w_cost`%、结束时回固定的数。副本的 `league_locke_w_on`
//!   只带攻速；本包在它挂着时每 60 拍烧他**当前生命 `w_cost`%**（真实伤害），记下烧掉多少，`w_on` 没了时回其中的 `w_back`%。
//! - **万魔狱真正处决、封印留一整局**：主包用「打阈值那么多真实伤害、下一拍补回去」近似处决，封印层数死了就没。副本只给大招命中的
//!   英雄挂 `league_locke_r_mark`；本包每拍看挂着它的敌方英雄，**当前生命低于最大生命 `r_exec`%（每层封印 +`r_exec_step`%）**
//!   就处决（真实伤害打掉剩下的血），在它倒下的地方放下法器（`league_locke_r_land` 的画面）；洛克走到法器 `pick_r` 以内就捡起来：
//!   封印 +1（最多 3 层，整局都在，死了也不掉），大招**剩下的冷却少 `r_cap`%**（`league_locke_r_seal` 的画面）。法器放 `r_drop`
//!   拍没人捡就消失。
//! - **参与击杀刷新灰猎无影**：主包用一个击杀窗口（数据只能看到「被他打过的英雄的记号断了」）。副本不带窗口；本包记下每个敌方英雄
//!   最近一次被他打（普攻的 `p_hit`、Q 的 `league_locke_q_mark`、R 的 `r_mark`）的拍数，`p_win` 拍内它倒下了（谁打死的都算）
//!   就拿掉他身上的 `league_locke_e_cd`：E 立刻好。
//! - **W 期间换成 W 的样子**（`view.rs`）：他身上有 `league_locke_w_on` 时，游戏按名字播的 idle / run / hit 和数据播的
//!   attack / skill / skill2 / ult 换成洛克图里的 `w_*`（第 0 步 B 的配色：深蓝皮肤、白西装、发白光的眼镜）。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。不用全局变量，服务端预模拟和
//! 你看的那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_locke.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_locke";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_locke") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// On him while Soul Ignition lasts (the data's W: its attack speed and move speed; the add-on burns and heals).
pub const W_ON: &str = "league_locke_w_on";
/// On a unit his attack hit (3 ticks): Silver Stake's missing-health part.
const P_HIT: &str = "league_locke_p_hit";
/// On a champion his nails marked (the data's Q mark, q_mark_t ticks).
const Q_MARK: &str = "league_locke_q_mark";
/// On a champion Purgatory marked (r_t ticks).
const R_MARK: &str = "league_locke_r_mark";
/// Ashen Pursuit's cooldown flag on him (the data keeps E's cooldown in it).
const E_CD: &str = "league_locke_e_cd";
/// The pictures: the artifact left where a champion was sealed, the pick-up, the E reset.
const R_LAND: &str = "league_locke_r_land";
const R_SEAL: &str = "league_locke_r_seal";
const P_RESET: &str = "league_locke_p_reset";
/// The artifact's picture plays again every LAND_EVERY ticks while it lies there.
const LAND_EVERY: usize = 60;
/// At most this many seals.
const SEALS: usize = 3;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LOCKE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_locke.log");
        }
    }
    PathBuf::from("league_locke.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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

/// Logs the first 40 of a kind, then every 100th.
fn often(n: usize) -> bool {
    n <= 40 || n % 100 == 0
}

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，build_locke.NATIVE_KEYS）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 圣银穿心：再打已损失生命的这么多百分比（魔法伤害）。
    pub p_miss: usize,
    /// 灵焰仪式持续多少拍（只用来写日志；什么时候结束看 `w_on`）。
    pub w_t: usize,
    /// 灵焰仪式每秒烧当前生命的百分比，结束时补回烧掉的百分比。
    pub w_cost: usize,
    pub w_back: usize,
    /// 万魔狱的标记留多少拍（只用来写日志；看 `r_mark`）。
    pub r_t: usize,
    /// 处决线：最大生命的百分比，每层封印再加的百分比。
    pub r_exec: usize,
    pub r_exec_step: usize,
    /// 法器在地上留多少拍，走到多近能捡（距离单位）。
    pub r_drop: usize,
    pub pick_r: u64,
    /// 捡起法器时大招剩下的冷却少这么多百分比。
    pub r_cap: usize,
    /// 参与击杀的窗口：英雄被他打过以后多少拍内倒下算他的（击杀窗口，同主包）。
    pub p_win: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { p_miss: 8, w_t: 240, w_cost: 2, w_back: 70, r_t: 240, r_exec: 15, r_exec_step: 3, r_drop: 300, pick_r: 9000, r_cap: 50, p_win: 180 }
    }
}

/// `{"p_miss":8,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        let u = v as usize;
        match k {
            "p_miss" => p.p_miss = u,
            "w_t" => p.w_t = u,
            "w_cost" => p.w_cost = u,
            "w_back" => p.w_back = u,
            "r_t" => p.r_t = u,
            "r_exec" => p.r_exec = u,
            "r_exec_step" => p.r_exec_step = u,
            "r_drop" => p.r_drop = u,
            "pick_r" => p.pick_r = v,
            "r_cap" => p.r_cap = u,
            "p_win" => p.p_win = u,
            _ => {}
        }
    }
    p
}

// ===================== 计算 =====================

/// `pct`% of `of`, at least 1 when `of` is not 0.
pub fn share(of: usize, pct: usize) -> usize {
    if of == 0 { 0 } else { (of * pct / 100).max(1) }
}

/// Silver Stake's extra: p_miss% of the missing health.
pub fn stake(p: &Params, hp: usize, max: usize) -> usize {
    let missing = max.saturating_sub(hp);
    if missing == 0 { 0 } else { share(missing, p.p_miss) }
}

/// The execute line with `seals` held: (r_exec + seals x r_exec_step)% of the maximum health.
pub fn exec_line(p: &Params, max: usize, seals: usize) -> usize {
    max * (p.r_exec + seals.min(SEALS) * p.r_exec_step) / 100
}

/// What picking the artifact up takes off the ult's remaining cooldown.
pub fn refund(p: &Params, remaining: usize) -> usize {
    remaining * p.r_cap / 100
}

fn dist2(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0.abs_diff(b.0);
    let dy = a.1.abs_diff(b.1);
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

fn has(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

// ===================== 被动 =====================

/// An artifact on the ground: where, until when, the tick its picture plays again.
#[derive(Clone, Debug)]
struct Artifact {
    at: (u64, u64),
    until: usize,
    shown: usize,
}

/// 每个洛克一份：参数、封印、地上的法器、W 的账、每个敌方英雄最近被他打的拍数，和日志计数。
#[derive(Clone, Default)]
struct Exorcist {
    p: Params,
    /// Seals held: kept for the whole game (League: the artifact's stacks), dying does not take them.
    seals: usize,
    artifacts: Vec<Artifact>,
    /// Soul Ignition: on last tick, the next burn's tick, what it has burnt.
    w_was: bool,
    w_next: usize,
    burnt: usize,
    /// Enemy champions: (id, the last tick he touched it).
    touched: Vec<(usize, usize)>,
    /// Purgatory's executes waiting for their damage: (id, where, the tick, hp, max). The game lands damage on the next
    /// tick, so whether one died is read then (0.1.1: read at once, every execute "survived" - no artifact, no seal).
    pending: Vec<(usize, (u64, u64), usize, usize, usize)>,
    n_stake: usize,
    n_burn: usize,
    n_exec: usize,
    n_pick: usize,
    n_reset: usize,
}

impl Exorcist {
    /// Silver Stake: every unit marked `p_hit` takes p_miss% of its missing health as magic damage.
    fn stakes(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let mut hit = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.is_alive() && has(&u, P_HIT) {
                let (hp, max) = u.hp();
                hit.push((u.id(), stake(&self.p, hp, max)));
            }
        }
        for (id, dmg) in hit {
            sim.entity_remove_buff(id, P_HIT);
            if dmg > 0 {
                sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::BaseAttack);
            }
            self.n_stake += 1;
            if often(self.n_stake) {
                wlog(format!("{} STAKE {}: +{dmg} magic ({} in all)", head(sim, me), name_of(sim, id), self.n_stake));
            }
        }
    }

    /// Soul Ignition: w_cost% of his current health every second while `w_on` lasts, w_back% of it back at the end.
    fn ignition(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let on = has(&e, W_ON);
        let (hp, _) = e.hp();
        if on && !self.w_was {
            self.burnt = 0;
            self.w_next = tick + 60;
        }
        if on && tick >= self.w_next {
            let cost = share(hp, self.p.w_cost).min(hp.saturating_sub(1));   // the soul fire never kills him
            if cost > 0 {
                sim.deal_damage_typed(me, me, cost, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                // the damage lands next tick: count what was dealt (0.1.1 read his health at once - burnt 0, healed 0)
                self.burnt += cost;
            }
            self.w_next = tick + 60;
        }
        if !on && self.w_was {
            let back = self.burnt * self.p.w_back / 100;
            if back > 0 {
                sim.heal(me, me, back);
            }
            self.n_burn += 1;
            if often(self.n_burn) {
                wlog(format!("{} IGNITION over: burnt {}, healed {back} ({} in all)", head(sim, me), self.burnt, self.n_burn));
            }
            self.burnt = 0;
        }
        self.w_was = on;
    }

    /// The enemy champions: who he touched, takedowns (E ready), Purgatory's execute and the artifacts it leaves.
    fn champions(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, mine) = (e.team(), e.pos());
        let mut fallen = Vec::new();
        let mut execute = Vec::new();
        // last tick's executes: dead now (or gone) - sealed, the artifact left where he fell
        for (id, at, t0, hp, max) in std::mem::take(&mut self.pending) {
            if t0 >= tick {
                self.pending.push((id, at, t0, hp, max));
                continue;
            }
            let dead = !sim.get_entity(id).is_some_and(|c| c.is_alive());
            if dead {
                self.artifacts.push(Artifact { at, until: tick + self.p.r_drop, shown: tick });
                fallen.push(id);
                self.touched.retain(|&(t, _)| t != id);
            }
            if often(self.n_exec) {
                wlog(format!("{} EXECUTE {} at {hp}/{max} (line {}%, {} seals): {} ({} in all)", head(sim, me),
                             name_of(sim, id), self.p.r_exec + self.seals * self.p.r_exec_step, self.seals,
                             if dead { "SEALED, the artifact left there" } else { "survived" }, self.n_exec));
            }
        }
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(c) = sim.get_entity(id) else { continue };
            if c.team() == team {
                continue;
            }
            if !c.is_alive() {
                if let Some(k) = self.touched.iter().position(|&(t, _)| t == id) {
                    let (_, at) = self.touched.remove(k);
                    if tick <= at + self.p.p_win {
                        fallen.push(id);
                    }
                }
                continue;
            }
            if has(&c, P_HIT) || has(&c, Q_MARK) || has(&c, R_MARK) {
                match self.touched.iter_mut().find(|(t, _)| *t == id) {
                    Some(x) => x.1 = tick,
                    None => self.touched.push((id, tick)),
                }
            }
            if has(&c, R_MARK) {
                let (hp, max) = c.hp();
                if hp > 0 && hp < exec_line(&self.p, max, self.seals) {
                    execute.push((id, hp, max, c.pos()));
                }
            }
        }
        for (id, hp, max, at) in execute {
            sim.entity_remove_buff(id, R_MARK);
            // through any shield, heal or regeneration before it lands next tick (league_pyke's way): exactly his health
            // let 5 of 19 executes survive (the 2026-10-30 log)
            sim.deal_damage_typed(me, id, hp + max, DamageTypeV1::Fixed, AttackTypeV1::Skill);
            self.n_exec += 1;
            self.pending.push((id, at, tick, hp, max));
        }
        if !fallen.is_empty() && sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            sim.entity_remove_buff(me, E_CD);
            sim.play_view_effect(P_RESET, me, &InputTargetV1::pos(mine.0, mine.1), 0, 0, 0);
            self.n_reset += 1;
            if often(self.n_reset) {
                let names: Vec<String> = fallen.iter().map(|&id| name_of(sim, id)).collect();
                wlog(format!("{} TAKEDOWN {}: Ashen Pursuit ready ({} in all)", head(sim, me), names.join(", "), self.n_reset));
            }
        }
    }

    /// The artifacts on the ground: their picture, the pick-up (a seal, the ult's cooldown cut), the ones left too long.
    fn artifacts(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        self.artifacts.retain(|a| tick < a.until);
        if self.artifacts.is_empty() {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, at) = (e.is_alive(), e.pos());
        let r2 = self.p.pick_r.saturating_mul(self.p.pick_r);
        let mut k = 0;
        while k < self.artifacts.len() {
            let a = self.artifacts[k].clone();
            if alive && dist2(a.at, at) <= r2 {
                self.artifacts.remove(k);
                self.seals = (self.seals + 1).min(SEALS);
                let left = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Ult)).map_or(0, |c| c.remaining);
                let cut = refund(&self.p, left);
                if cut > 0 {
                    sim.entity_reduce_cooldown(me, SkillSlotV1::Ult, cut);
                }
                sim.play_view_effect(R_SEAL, me, &InputTargetV1::pos(at.0, at.1), 0, 0, 0);
                self.n_pick += 1;
                if often(self.n_pick) {
                    wlog(format!("{} PICKUP: {} seals, the ult's cooldown {left} -> {} ({} in all)", head(sim, me),
                                 self.seals, left - cut, self.n_pick));
                }
                continue;
            }
            if tick >= a.shown {
                sim.play_view_effect(R_LAND, me, &InputTargetV1::pos(a.at.0, a.at.1), 0, 0, 0);
                self.artifacts[k].shown = tick + LAND_EVERY;
            }
            k += 1;
        }
    }
}

impl StablePassive for Exorcist {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        // the seals and the artifacts on the ground stay (League: the seals are for the game)
        self.w_was = false;
        self.burnt = 0;
        wlog(format!("{} SPAWN: the add-on's Locke (player {player}, team {team}), {} seals, {:?}", head(sim, me),
                     self.seals, self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        // takedowns and the artifacts count while he is dead too (an assist from the fountain, an artifact waiting)
        self.champions(sim, me, tick);
        self.artifacts(sim, me, tick);
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            self.w_was = false;
            self.burnt = 0;
            return;
        }
        self.stakes(sim, me);
        self.ignition(sim, me, tick);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Silver Stake on missing health, Soul Ignition on current health, Purgatory's execute and seals, takedown resets, the W look) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:exorcist"), Exorcist::default());
    view::install_once();
    host.log(LogLevel::Info, "league_locke loaded (Silver Stake, Soul Ignition, Purgatory's execute and seals, the W look).");
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
        let p = parse_params(r#"{"p_miss":10,"r_exec":20,"pick_r":12000,"x":1}"#);
        assert_eq!((p.p_miss, p.r_exec, p.pick_r), (10, 20, 12000));
        assert_eq!(p.w_back, Params::default().w_back);
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn silver_stake_grows_with_missing_health() {
        let p = Params::default();
        assert_eq!(stake(&p, 1000, 1000), 0);
        assert_eq!(stake(&p, 500, 1000), 40);   // 8% of 500 missing
        assert_eq!(stake(&p, 100, 1000), 72);
        assert_eq!(stake(&p, 999, 1000), 1);
    }

    #[test]
    fn the_execute_line_grows_with_the_seals_up_to_three() {
        let p = Params::default();
        assert_eq!(exec_line(&p, 2000, 0), 300);   // 15%
        assert_eq!(exec_line(&p, 2000, 2), 420);   // 21%
        assert_eq!(exec_line(&p, 2000, 3), 480);   // 24%
        assert_eq!(exec_line(&p, 2000, 9), 480);   // capped at three
    }

    #[test]
    fn the_pickup_cuts_the_remaining_cooldown() {
        let p = Params::default();
        assert_eq!(refund(&p, 3000), 1500);
        assert_eq!(refund(&p, 0), 0);
    }

    #[test]
    fn names_are_the_data_s() {
        for n in [W_ON, P_HIT, Q_MARK, R_MARK, E_CD, R_LAND, R_SEAL, P_RESET] {
            assert!(n.starts_with("league_locke_"), "{n}");
        }
    }
}
