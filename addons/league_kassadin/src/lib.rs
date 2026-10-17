//! 卡萨丁附加包（用户：「被动看看rust能做吗」，附加包「你看着办吧」）：三件主包数据做不到的事。
//!
//! `mod.mod_info` 之外，`mod.override_info` 把主包的卡萨丁换成 `override/` 里的副本（tools/kit/build_kassadin.py 的
//! native=1）：数据和主包一样，只是
//! - 被动挂本包的 `league_kassadin:void_stone`（参数在英雄数据的 `passive.params` 里），主包的魔抗 buff 和「自己放 Q / R
//!   给 E 减冷却」的 buff 去掉；
//! - R 出手那一 tick 不再随机闪到射程里的一个敌方英雄，而是调本包的 `league_kassadin:rift` 选落点。
//!
//! - **虚空之石**：魔法伤害是 x 100 / (100 + 魔抗)，受到的魔法伤害正好少 `dr`% 要魔抗 M' = (100 + M) x 100 / (100 - dr) - 100。
//!   每 `MR_EVERY` tick 读他现在的魔抗（装备、别人的减魔抗都算上），减掉本包自己那份，算出该补多少，用一个永久 buff
//!   `league_kassadin_void` 补上（数字变了才换）。英雄联盟的「无视单位碰撞」游戏里没有开关（数据和原生接口都没有），不做。
//! - **能量脉冲充能**：每 tick 读所有英雄的冷却（`cooldowns()`），Q / E / R 的剩余冷却比上一 tick 跳高了 = 放了技能；
//!   放技能的英雄（敌我都算，也算他自己的 Q 和 R，不算他自己的 E）在他 `reach` 以内，E 的剩余冷却少 `cut` tick。
//!   减冷却靠 2 tick 的 `skill_cooldown_mult`（引擎每 tick 把剩余冷却压到 冷却 x 100 / (100 + mult)），mult 取不会顺带
//!   压低 Q 的最大值（Q 剩余冷却已经更短时才压满）。
//! - **虚空行走落点**：射程（`R_REACH`）里每个敌方英雄都试一遍：这一下（算上叠层和他的魔抗）能打死的优先，其次炸得到的
//!   英雄多、离他远（后排）的；敌方塔 `TOWER_REACH` 以内的不去。落在目标身前 `LAND_SHORT`（从卡萨丁看过去）。没有合适的
//!   就落在大招目标身上（和主包一样）。之后数据里的爆炸照常（一 tick 后，以他的新位置为中心）。
//!
//! 数字：被动的参数从英雄数据来；R 的数字写在这里（`R_*`），`tests::the_numbers_match_the_kit` 读主包的参数表核对。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_kassadin.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_kassadin";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";

/// 主包卡萨丁的名字（buff、画面都以它开头）。
fn ks(x: &str) -> String {
    format!("league_kassadin_{x}")
}

// ===================== 数值（主包 build_kassadin.P） =====================

/// 大招找落点的距离（r_reach）、爆炸半径（r_r）、伤害（r_dmg + r_ratio% 法强，每层 r_st + r_st_ratio%）。
pub const R_REACH: f64 = 56_000.0;
pub const R_R: f64 = 20_000.0;
pub const R_DMG: usize = 100;
pub const R_RATIO: usize = 50;
pub const R_ST: usize = 40;
pub const R_ST_RATIO: usize = 10;
/// 敌人的身体半径（爆炸半径算到身体边上）。
pub const BODY: f64 = 6_000.0;
/// 落在目标身前这么远（从卡萨丁看过去），不和它叠在一起。
pub const LAND_SHORT: f64 = 6_000.0;
/// 敌方塔的攻击范围（大约，塔下不去）。
pub const TOWER_REACH: f64 = 75_000.0;
/// 打分：能打死 KILL_SCORE，每个炸得到的英雄 CHAMP_SCORE，离他每远 10000 加 BACK_SCORE（后排），每个小兵或野怪 UNIT_SCORE。
pub const KILL_SCORE: f64 = 100.0;
pub const CHAMP_SCORE: f64 = 10.0;
pub const BACK_SCORE: f64 = 1.0;
pub const UNIT_SCORE: f64 = 0.5;
/// 魔抗多久重算一次。
pub const MR_EVERY: usize = 15;
/// 被动补魔抗的 buff。
const VOID: &str = "league_kassadin_void";
/// 给 E 减冷却的 2 tick buff。
const CHARGE: &str = "league_kassadin_e_charge";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_KASSADIN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_kassadin.log");
        }
    }
    PathBuf::from("league_kassadin.log")
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

fn who(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n}#{id}"))
}

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

// ===================== 计算（单元测试用） =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 魔抗为 `m` 时，受到的魔法伤害少 `dr`% 需要补多少魔抗（四舍五入）。
pub fn void_bonus(m: usize, dr: usize) -> i32 {
    let dr = dr.min(90) as f64;
    let want = (100.0 + m as f64) * 100.0 / (100.0 - dr) - 100.0;
    (want - m as f64).round() as i32
}

/// 压 E 用的 mult：E 剩余 `e_rem`、冷却 `e_cool`，少 `cut` tick；不压低 Q（剩余 `q_rem`，冷却 `q_cool`）。None = 不压。
pub fn charge_mult(e_rem: usize, e_cool: usize, cut: usize, q_rem: usize, q_cool: usize) -> Option<i32> {
    if e_rem <= 3 || e_cool == 0 || cut == 0 {
        return None;
    }
    let want = e_rem.saturating_sub(cut).max(3) as f64;
    // 剩余冷却被压到 cool x 100 / (100 + mult)：要压到 want，mult = cool x 100 / want - 100（向上取整，压得到）
    let mut mult = (e_cool as f64 * 100.0 / want - 100.0).ceil();
    if q_rem > 0 && q_cool > 0 {
        // Q 被压到 q_cool x 100 / (100 + mult)，不能低于它现在的剩余：mult <= q_cool x 100 / q_rem - 100
        let q_max = (q_cool as f64 * 100.0 / q_rem as f64 - 100.0).floor();
        mult = mult.min(q_max);
    }
    // a cap above what E has left does nothing
    let cap = e_cool as f64 * 100.0 / (100.0 + mult);
    (mult >= 1.0 && cap < e_rem as f64).then_some(mult as i32)
}

/// 一个敌人：位置、是不是英雄、现在的血、魔抗。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub at: (f64, f64),
    pub champion: bool,
    pub hp: usize,
    pub mr: usize,
}

/// 落在 `c`（一个敌方英雄）身前：(落点, 分数, 能不能打死它)。`me` 是卡萨丁，`dmg` 是这一下的魔法伤害（魔抗前）。
pub fn score(me: (f64, f64), c: &Foe, foes: &[Foe], dmg: usize) -> ((f64, f64), f64, bool) {
    let d = dist(me, c.at);
    let spot = if d > LAND_SHORT {
        (c.at.0 + (me.0 - c.at.0) / d * LAND_SHORT, c.at.1 + (me.1 - c.at.1) / d * LAND_SHORT)
    } else {
        c.at
    };
    let kill = c.hp > 0 && dmg * 100 / (100 + c.mr) >= c.hp;
    let mut s = if kill { KILL_SCORE } else { 0.0 } + BACK_SCORE * d / 10_000.0;
    for f in foes {
        if dist(f.at, spot) <= R_R + BODY {
            s += if f.champion { CHAMP_SCORE } else { UNIT_SCORE };
        }
    }
    (spot, s, kill)
}

/// 最好的落点：塔外、`R_REACH` 以内的敌方英雄里分最高的。None = 没有（落在大招目标身上）。
pub fn best_spot(me: (f64, f64), foes: &[Foe], towers: &[(f64, f64)], dmg: usize) -> Option<((f64, f64), f64, bool)> {
    let mut best: Option<((f64, f64), f64, bool)> = None;
    for c in foes.iter().filter(|f| f.champion && dist(me, f.at) <= R_REACH) {
        let (spot, s, kill) = score(me, c, foes, dmg);
        if towers.iter().any(|t| dist(*t, spot) <= TOWER_REACH) {
            continue;
        }
        if best.is_none_or(|b| s > b.1 + 1e-6) {
            best = Some((spot, s, kill));
        }
    }
    best
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

/// 敌人（活着、能被选中、不是塔）。
fn foes_of(sim: &StableSim<'_>, team: usize) -> Vec<(usize, Foe)> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower() {
            continue;
        }
        let (x, y) = u.pos();
        out.push((u.id(), Foe { at: (x as f64, y as f64), champion: u.is_champion(), hp: u.hp().0,
                                mr: u.stat().magic_resistance }));
    }
    out
}

fn enemy_towers(sim: &StableSim<'_>, team: usize) -> Vec<(f64, f64)> {
    (0..sim.tower_count())
        .filter_map(|i| sim.get_entity(sim.tower_id_at(i)))
        .filter(|t| t.team() != team && t.is_alive())
        .map(|t| {
            let (x, y) = t.pos();
            (x as f64, y as f64)
        })
        .collect()
}

// ===================== 被动 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// E 的冷却（e_cd）和 Q 的冷却（q_cd）。
    pub cool: usize,
    pub q_cool: usize,
    /// 每次施法 E 少多少 tick（英雄联盟 1.5 秒）。
    pub cut: usize,
    /// 多远以内的施法算数。
    pub reach: usize,
    /// 魔法伤害少多少 %。
    pub dr: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { cool: 900, q_cool: 360, cut: 90, reach: 32_000, dr: 10 }
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
            "cool" => p.cool = v,
            "q_cool" => p.q_cool = v,
            "cut" => p.cut = v,
            "reach" => p.reach = v,
            "dr" => p.dr = v,
            _ => {}
        }
    }
    p
}

/// 每个卡萨丁一份。
#[derive(Clone, Default)]
struct VoidStone {
    p: Params,
    /// 本包补的魔抗（已经在 buff 里的）。
    bonus: i32,
    /// stat() 的魔抗含不含 buff（第一次补上之后看出来）；probe = 没有 buff 时的魔抗。
    counts_buffs: Option<bool>,
    probe: Option<i32>,
    /// 各玩家上一 tick 的 (Q, E, R) 剩余冷却。
    last: HashMap<usize, (usize, usize, usize)>,
    /// 日志计数。
    mr_logs: usize,
    charges: usize,
}

impl VoidStone {
    fn void_stone(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let shown = e.stat().magic_resistance as i32;
        // 死了 buff 就没了：没有 buff 时本包那份是 0
        let mine = if has_buff(sim, me, VOID) { self.bonus } else { 0 };
        // stat() 含不含 buff 只看一次：第一次加上 buff 前记下魔抗，下一次看它涨没涨
        if mine > 0 && self.counts_buffs.is_none() {
            if let Some(before) = self.probe {
                let counts = shown >= before + mine / 2;
                self.counts_buffs = Some(counts);
                wlog(format!("{} VOID stat() {} buffs ({before} -> {shown} with +{mine})", head(sim, me),
                             if counts { "counts" } else { "leaves out" }));
            }
        }
        if mine == 0 {
            self.probe = Some(shown);
        }
        let base = if self.counts_buffs == Some(false) { shown.max(0) } else { (shown - mine).max(0) } as usize;
        let want = void_bonus(base, self.p.dr);
        if want == mine {
            return;
        }
        sim.entity_remove_buff(me, VOID);
        let mut b = BuffV1::named(VOID);
        b.magic_resistance = want;
        sim.add_buff(me, &b);
        self.bonus = want;
        self.mr_logs += 1;
        if self.mr_logs <= 30 || self.mr_logs % 50 == 0 {
            wlog(format!("{} VOID #{} resistance {} (shown {shown}, mine {mine}) -> +{want} = {}: magic damage x {:.3}",
                         head(sim, me), self.mr_logs, base, base as i32 + want,
                         100.0 / (100.0 + (base as i32 + want) as f64)));
        }
    }

    fn charge(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(at) = alive_at(sim, me) else {
            self.last.clear();
            return;
        };
        let mut casts = Vec::new();
        let mut mine = None;
        for i in 0..sim.player_count() {
            let Some(pl) = sim.player_at(i) else { continue };
            let pid = pl.id();
            let Some(c) = pl.champion() else { continue };
            let cid = c.id();
            let Some(cd) = pl.cooldowns() else { continue };
            let now = (cd.1, cd.2, cd.3);
            if cid == me {
                mine = Some(now);
            }
            if let Some(was) = self.last.insert(pid, now) {
                let jumped = |a: usize, b: usize| a > b + 5;
                let q = jumped(now.0, was.0);
                let e = jumped(now.1, was.1) && cid != me;
                let r = jumped(now.2, was.2);
                if (q || e || r) && c.is_alive() {
                    let (x, y) = c.pos();
                    if dist(at, (x as f64, y as f64)) <= self.p.reach as f64 {
                        casts.push((cid, if q { "Q" } else if e { "E" } else { "R" }));
                    }
                }
            }
        }
        if casts.is_empty() {
            return;
        }
        let Some((q_rem, e_rem, _)) = mine else { return };
        let cut = self.p.cut * casts.len();
        let Some(mult) = charge_mult(e_rem, self.p.cool, cut, q_rem, self.p.q_cool) else { return };
        sim.entity_remove_buff(me, CHARGE);
        let mut b = BuffV1::timed(CHARGE, 2);
        b.skill_cooldown_mult = mult;
        sim.add_buff(me, &b);
        self.charges += casts.len();
        if self.charges <= 40 || self.charges % 25 == 0 {
            let list: Vec<String> = casts.iter().map(|(c, s)| format!("{} {s}", who(sim, *c))).collect();
            wlog(format!("{} CHARGE #{} {}: E {e_rem} -> about {} (mult {mult}, Q {q_rem})", head(sim, me), self.charges,
                         list.join(", "), e_rem.saturating_sub(cut)));
        }
    }
}

impl StablePassive for VoidStone {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.bonus = 0;
        self.last.clear();
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Kassadin (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if sim.tick() % MR_EVERY == 0 {
            self.void_stone(sim, me);
        }
        self.charge(sim, me);
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.bonus = 0;
        self.last.clear();
    }
}

// ===================== 虚空行走落点 =====================

/// 大招 `r_at` 那一 tick：挑落点，把他放过去（爆炸在数据里，一 tick 后）。
fn rift(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let Some(me) = alive_at(sim, caster) else { return };
    let (team, ap) = sim.get_entity(caster).map_or((0, 0), |e| (e.team(), e.stat().magic_power));
    let stacks = ["r_s3", "r_s2", "r_s1"].iter().position(|s| has_buff(sim, caster, &ks(s))).map_or(0, |i| 3 - i);
    let dmg = R_DMG + stacks * R_ST + (R_RATIO + stacks * R_ST_RATIO) * ap / 100;
    let foes = foes_of(sim, team);
    let list: Vec<Foe> = foes.iter().map(|f| f.1).collect();
    let towers = enemy_towers(sim, team);
    let target = (input.kind == InputTargetKindV1::Target.code()).then(|| alive_at(sim, input.target_id)).flatten();
    let (spot, why) = match best_spot(me, &list, &towers, dmg) {
        Some((spot, s, kill)) => (spot, format!("score {s:.1}{}", if kill { ", a kill" } else { "" })),
        None => match target {
            Some(t) => (t, "nothing outside the towers: on the target".to_string()),
            None => {
                wlog(format!("{} RIFT: no champion in reach and no target (kind {})", head(sim, caster), input.kind));
                return;
            }
        },
    };
    let x = spot.0.round().max(0.0) as u64;
    let y = spot.1.round().max(0.0) as u64;
    let moved = sim.entity_set_pos(caster, x, y);
    let champs = list.iter().filter(|f| f.champion && dist(f.at, spot) <= R_R + BODY).count();
    wlog(format!("{} RIFT {} -> {} ({:.0} away, {} stacks, {dmg} magic before resistance): {} champions in the blast, {why}{}",
                 head(sim, caster), pt(me), pt(spot), dist(me, spot), stacks, champs,
                 if moved { "" } else { " (entity_set_pos refused)" }));
}

// ===================== 注册 =====================

struct Rift;

impl StableEffectType for Rift {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        rift(sim, caster, input);
    }
}

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Kassadin: Void Stone exact, Force Pulse charged by casts nearby, Riftwalk's landing) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:void_stone"), VoidStone::default());
    module.add_native_effect(format!("{ID}:rift"), Rift);
    host.log(LogLevel::Info, "league_kassadin loaded (Void Stone, Force Pulse charge, Riftwalk landing).");
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

    fn champ(x: f64, y: f64, hp: usize) -> Foe {
        Foe { at: (x, y), champion: true, hp, mr: 30 }
    }

    #[test]
    fn void_stone_takes_ten_percent() {
        for m in [0usize, 22, 40, 80, 150] {
            let b = void_bonus(m, 10);
            let taken = 100.0 / (100.0 + (m as i32 + b) as f64);
            let plain = 100.0 / (100.0 + m as f64);
            assert!((taken / plain - 0.9).abs() < 0.006, "mr {m}: +{b} -> x {:.4}", taken / plain);
        }
    }

    #[test]
    fn the_charge_cuts_e_and_never_q() {
        // E 600 of 900 left, cut 90 -> about 510; Q has 100 of 360 left (a smaller share: untouched)
        let mult = charge_mult(600, 900, 90, 100, 360).expect("a cut");
        let e_cap = 900.0 * 100.0 / (100.0 + mult as f64);
        let q_cap = 360.0 * 100.0 / (100.0 + mult as f64);
        assert!((505.0..=510.0).contains(&e_cap), "E cap {e_cap}");
        assert!(q_cap >= 100.0 - 1e-6, "Q cut: cap {q_cap}");
        // Q just cast (300 of 360, a bigger share than E's): E is cut only as far as Q stays where it is
        assert_eq!(charge_mult(600, 900, 90, 300, 360), None);
        let mult = charge_mult(600, 900, 90, 200, 360).unwrap();
        let q_cap = 360.0 * 100.0 / (100.0 + mult as f64);
        assert!(q_cap >= 200.0 - 1e-6 && 900.0 * 100.0 / (100.0 + mult as f64) < 600.0);
        // Q ready: the full cut
        let mult = charge_mult(600, 900, 90, 0, 360).unwrap();
        let e_cap = 900.0 * 100.0 / (100.0 + mult as f64);
        assert!((505.0..=510.0).contains(&e_cap), "cap {e_cap}");
        assert_eq!(charge_mult(2, 900, 90, 0, 360), None);
    }

    #[test]
    fn a_kill_beats_a_crowd() {
        let me = (0.0, 0.0);
        let low = champ(40_000.0, 0.0, 50);
        let pack = [champ(30_000.0, 30_000.0, 2000), champ(32_000.0, 33_000.0, 2000), champ(29_000.0, 35_000.0, 2000)];
        let mut foes = pack.to_vec();
        foes.push(low);
        let (spot, _, kill) = best_spot(me, &foes, &[], 300).unwrap();
        assert!(kill && dist(spot, low.at) <= LAND_SHORT + 1.0, "{spot:?}");
    }

    #[test]
    fn the_back_line_without_a_kill_and_never_under_a_tower() {
        let me = (0.0, 0.0);
        let front = champ(20_000.0, 0.0, 2000);
        let back = champ(50_000.0, 0.0, 2000);
        let (spot, _, _) = best_spot(me, &[front, back], &[], 300).unwrap();
        assert!(dist(spot, back.at) <= LAND_SHORT + 1.0, "{spot:?}");
        // a tower 66000 past the back liner's spot keeps him off it; the front liner's spot is 96000 from it
        let (spot, _, _) = best_spot(me, &[front, back], &[(110_000.0, 0.0)], 300).unwrap();
        assert!(dist(spot, front.at) <= LAND_SHORT + 1.0, "{spot:?}");
        assert!(best_spot(me, &[front], &[(20_000.0, 0.0)], 300).is_none());
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"cool":900,"cut":90,"dr":10,"q_cool":360,"reach":32000}"#);
        assert_eq!(p, Params { cool: 900, q_cool: 360, cut: 90, reach: 32_000, dr: 10 });
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_kassadin.py");
        let src = std::fs::read_to_string(path).expect("build_kassadin.py");
        for (key, v) in [("r_reach", R_REACH as usize), ("r_r", R_R as usize), ("r_dmg", R_DMG), ("r_ratio", R_RATIO),
                         ("r_st", R_ST), ("r_st_ratio", R_ST_RATIO)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_kassadin.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in [VOID, CHARGE] {
            assert!(x.len() <= BUFF_NAME_CAP);
        }
        for x in ["r_s1", "r_s2", "r_s3"] {
            assert!(ks(x).len() <= BUFF_NAME_CAP);
        }
    }
}
