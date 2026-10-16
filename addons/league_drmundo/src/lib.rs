//! 蒙多附加包（用户选「主包数据 + 附加包」，2026-10-16）：主包数据读不到生命，蒙多的技能又几乎全按生命算，这里补上。
//!
//! `mod.override_info` 把主包的蒙多换成 `override/` 里的副本（tools/kit/build_drmundo.py 的 native=1）：数据和主包一样，只是
//! - 被动挂本包的 `league_drmundo:pleases`（参数在英雄数据的 `passive.params` 里）；
//! - Q 打中英雄调 `league_drmundo:saw`（不再是主包的「最大生命 %」），E 的强化普攻调 `league_drmundo:bonk`，W 开启 / 结束调
//!   `league_drmundo:zap` / `league_drmundo:zap_end`（不再是主包「数挨打次数」的灰色生命），R 调 `league_drmundo:dose`；
//! - R 是普通的点目标施放，放不放由本包的 AI 钩子看他的真实生命决定（主包是「最近挨打次数」）。
//!
//! - **走自己想去的地方**：被动好了（身上没有 `p_cd`）时，硬控落到他身上的那个 tick 就清掉（`entity_clear_cc`），扣当前生命的
//!   7%，挂 `p_drop_n`：数据那边 3 tick 的自检看到它，就给 `p_cd`、短暂免控、丢药罐（药罐的区域、捡起回血和减冷却都还是
//!   数据）。数据的药罐跟着他飞 `p_fly` tick、落在他脚下（他身上挂上 `can`）：落地那个 tick 记下位置，`can` 没了（捡起、
//!   被踩碎、过期）才忘掉。药罐在场、他生命不满 `CAN_PCT`% 时 AI 走过去捡：身边 `SAFE` 以内没有敌方英雄，或者药罐就在
//!   `NEAR_TANK` 以内（两步路）；该放 R 的时候先放 R。
//! - **感染之锯**：打中英雄时按对方**当前生命**的 `q_pct`%（至少 `q_dmg`）算魔法伤害，补上主包那一下 `q_dmg` 的差额。
//! - **钝器创伤**：强化普攻按他**已损生命**最多再加 `e_miss`%（`e_dmg` + `e_ad`% 攻击力那部分）；他的攻击力随**额外生命**
//!   （最大生命高出这一级本来的部分，装备给的）涨 `e_bonus`‰。
//! - **心脏电击器**：开启后受到的伤害存 `w_store`% 成灰色生命；结束时数据的电击打中英雄（`w_full`）全回，只打中小兵野怪
//!   （`w_half`）回一半，没打中不回。
//! - **极限剂量**（「看好时机」）：AI 要放 R 时，他生命低于 `r_low`%，或 1 秒内掉了 `r_burst`% 以上，并且身边有敌方英雄才放；
//!   否则改成普攻。放出时回复已损生命的 `r_miss`%。
//!
//! 状态按模拟分开记（同一局同时跑几份模拟，实体编号一样）：被动出生时给他挂 `league_drmundo_sim:<编号>`（塔姆、莫德凯撒、
//! 蛮王附加包的做法）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_drmundo.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_drmundo";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.1";
const HERO: &str = "league_drmundo";

// ===================== 数值 =====================

/// R：AI 放 R 的距离（r_range）、看身边敌方英雄的距离（r_n）。
pub const R_RANGE: f64 = 50_000.0;
pub const R_NEAR: f64 = 40_000.0;
/// 生命记录多久（看 1 秒内掉了多少）。
pub const BURST_TICKS: usize = 60;
/// 被动扣当前生命的 %。
pub const SHAKE_PCT: usize = 7;
/// 去捡药罐：生命低于这个 %、身边这么远没有敌方英雄（或者药罐就在 NEAR_TANK 以内）、药罐不超过这么远。
pub const CAN_PCT: usize = 85;
pub const SAFE: f64 = 35_000.0;
pub const NEAR_TANK: f64 = 15_000.0;
pub const CAN_REACH: f64 = 45_000.0;
/// 丢出后这么久还没落地就算没丢成（数据 3 tick 一次的自检 + p_fly 20 tick 的飞行）。
pub const LAND_WAIT: usize = 60;
/// 药罐在地上多久（p_can_t）。
pub const CAN_TICKS: usize = 600;
/// 灰色生命最多存最大生命的几成。
pub const GREY_CAP_PCT: usize = 50;

/// 算「被控」的硬控（游戏 0.6.4 把施法动作也记成一种控制 Animation，不能用 cc_count() > 0）。
pub const HARD_CC: [CcKindV1; 7] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
    CcKindV1::ForceMove,
];

fn md(x: &str) -> String {
    format!("league_drmundo_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_DRMUNDO_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_drmundo.log");
        }
    }
    PathBuf::from("league_drmundo.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
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

pub fn pct(hp: usize, max: usize) -> usize {
    if max == 0 { 0 } else { hp * 100 / max }
}

/// Q 打中英雄：按打中前的当前生命（`hp_before`）的 `q_pct`%，至少 `q_dmg`；减去数据已经打出的 `q_dmg` 后补多少。
pub fn saw_extra(hp_before: usize, q_pct: usize, q_dmg: usize) -> usize {
    (hp_before * q_pct / 100).max(q_dmg) - q_dmg
}

/// 强化普攻按已损生命再加多少：(e_dmg + e_ad% 攻击力) × e_miss% × 已损比例。
pub fn bonk_extra(e_dmg: usize, e_ad: usize, attack: usize, e_miss: usize, hp: usize, max: usize) -> usize {
    if max == 0 {
        return 0;
    }
    let base = e_dmg + e_ad * attack / 100;
    base * e_miss / 100 * (max - hp.min(max)) / max
}

/// 额外生命（装备给的）：最大生命高出这一级本来的部分。
pub fn bonus_hp(max: usize, base: usize, growth: usize, level: usize) -> usize {
    max.saturating_sub(base + growth * level.saturating_sub(1))
}

/// 被动扣多少（当前生命的 SHAKE_PCT%，留至少 1 点）。
pub fn shake_cost(hp: usize) -> usize {
    (hp * SHAKE_PCT / 100).min(hp.saturating_sub(1))
}

/// 去不去捡药罐：生命 %、离药罐多远、身边的敌方英雄数。
pub fn tank_ok(hp_pct: usize, d: f64, foes_near: usize) -> Option<&'static str> {
    if hp_pct >= CAN_PCT || d > CAN_REACH {
        return None;
    }
    if foes_near == 0 {
        Some("safe")
    } else if d <= NEAR_TANK {
        Some("close")
    } else {
        None
    }
}

/// 药罐没了没有：`can` 在身上就还在；不在的话，落过地（`seen`）就是没了，没落过地的等 LAND_WAIT。
pub fn tank_gone(has_can: bool, seen: bool, now: usize, dropped: usize) -> bool {
    !has_can && (seen || now > dropped + LAND_WAIT)
}

/// R 的时机：生命 %、1 秒内掉的 %、身边的敌方英雄数。
pub fn dose_ok(hp_pct: usize, lost_pct: usize, foes_near: usize, r_low: usize, r_burst: usize) -> Option<&'static str> {
    if foes_near == 0 {
        return None;
    }
    if hp_pct < r_low {
        return Some("LOW");
    }
    if lost_pct >= r_burst {
        return Some("BURST");
    }
    None
}

/// 灰色生命存多少（`store`%），不超过上限。
pub fn stored(grey: usize, damage: usize, store: usize, cap: usize) -> usize {
    (grey + damage * store / 100).min(cap)
}

// ===================== 小工具 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn hard_cc(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| {
        (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
    })
}

/// 敌队活着、能选中的英雄的位置。
fn foes(sim: &StableSim<'_>, team: usize) -> Vec<(usize, (f64, f64))> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_targetable() || !u.is_champion() {
            continue;
        }
        let (x, y) = u.pos();
        out.push((u.id(), (x as f64, y as f64)));
    }
    out
}

fn within(list: &[(usize, (f64, f64))], at: (f64, f64), r: f64) -> usize {
    list.iter().filter(|c| dist(c.1, at) <= r).count()
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub p_cd: usize,
    pub q_dmg: usize,
    pub q_pct: usize,
    pub e_dmg: usize,
    pub e_ad: usize,
    pub e_miss: usize,
    pub e_bonus: usize,
    pub hp: usize,
    pub hp_g: usize,
    pub w_store: usize,
    pub r_low: usize,
    pub r_burst: usize,
    pub r_miss: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { p_cd: 2400, q_dmg: 140, q_pct: 20, e_dmg: 80, e_ad: 60, e_miss: 100, e_bonus: 25, hp: 1350, hp_g: 125,
                 w_store: 75, r_low: 40, r_burst: 25, r_miss: 25 }
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
            "p_cd" => p.p_cd = v,
            "q_dmg" => p.q_dmg = v,
            "q_pct" => p.q_pct = v,
            "e_dmg" => p.e_dmg = v,
            "e_ad" => p.e_ad = v,
            "e_miss" => p.e_miss = v,
            "e_bonus" => p.e_bonus = v,
            "hp" => p.hp = v,
            "hp_g" => p.hp_g = v,
            "w_store" => p.w_store = v,
            "r_low" => p.r_low = v,
            "r_burst" => p.r_burst = v,
            "r_miss" => p.r_miss = v,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<Params>> = LazyLock::new(|| Mutex::new(Params::default()));

fn params() -> Params {
    *PARAMS.lock().unwrap_or_else(|e| e.into_inner())
}

// ===================== 按模拟分开的状态 =====================

static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
const SIM_TAG: &str = "league_drmundo_sim:";

#[derive(Clone, Copy, Debug, Default)]
struct State {
    /// 心脏电击器开着时存的灰色生命。
    grey: usize,
    zapping: bool,
    /// 药罐：落点和消失的 tick（0 = 没有）、丢出的 tick、落地了没有、AI 正在走过去。
    can_at: (f64, f64),
    can_until: usize,
    can_drop: usize,
    can_seen: bool,
    walking: bool,
    /// 上个 tick p_cd 还剩多少（捡起时数据把冷却重设成缩短后的，就不是正好少 1）。
    cd_left: usize,
}

/// (这份模拟的编号, 蒙多的 entity id) -> 状态。
static STATE: LazyLock<Mutex<HashMap<(u64, usize), State>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// (这份模拟的编号, 蒙多的 entity id) -> 最近的 (tick, 生命)（每 10 tick 一次）。
static HP_LOG: LazyLock<Mutex<HashMap<(u64, usize), Vec<(usize, usize)>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// The number the passive hung on him when he spawned in this sim (0: none).
pub fn sim_tag(names: impl Iterator<Item = String>) -> u64 {
    names.into_iter().find_map(|n| n.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())).unwrap_or(0)
}

fn sim_of(sim: &StableSim<'_>, me: usize) -> u64 {
    sim.get_entity(me).map_or(0, |e| sim_tag((0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string())))
}

fn with_state<R>(key: (u64, usize), f: impl FnOnce(&mut State) -> R) -> R {
    let mut map = STATE.lock().unwrap_or_else(|e| e.into_inner());
    f(map.entry(key).or_default())
}

fn peak_hp(key: (u64, usize), now: usize, hp: usize) -> usize {
    let log = HP_LOG.lock().unwrap_or_else(|e| e.into_inner());
    log.get(&key).map_or(hp, |v| v.iter().filter(|s| s.0 + BURST_TICKS >= now).map(|s| s.1).max().unwrap_or(hp).max(hp))
}

// ===================== 技能效果 =====================

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

/// Q 打中英雄：按对方当前生命补伤害。
struct Saw;

impl StableEffectType for Saw {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(t) = target_of(&input) else { return };
        let Some(e) = sim.get_entity(t).filter(|e| e.is_alive() && e.is_champion()) else { return };
        let p = params();
        // the data's own q_dmg landed a moment before (the line's hit; its champion twin comes right after)
        let before = e.hp().0 + p.q_dmg;
        let extra = saw_extra(before, p.q_pct, p.q_dmg);
        if extra > 0 {
            sim.deal_damage(caster, t, 0, extra, AttackTypeV1::Skill);
        }
        if let Some(n) = counted("saw") {
            wlog(format!("{} SAW #{n} {}: {}% of {before} -> {} more", head(sim, caster), who(sim, t), p.q_pct, extra));
        }
    }
}

/// E 的强化普攻：按已损生命加伤害。
struct Bonk;

impl StableEffectType for Bonk {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(t) = target_of(&input) else { return };
        if !sim.get_entity(t).is_some_and(|e| e.is_alive()) {
            return;
        }
        let Some(me) = sim.get_entity(caster) else { return };
        let (hp, max) = me.hp();
        let p = params();
        let extra = bonk_extra(p.e_dmg, p.e_ad, me.stat().attack, p.e_miss, hp, max);
        if extra > 0 {
            sim.deal_damage(caster, t, extra, 0, AttackTypeV1::Skill);
        }
        if let Some(n) = counted("bonk") {
            wlog(format!("{} BONK #{n} {} at {}% hp: {extra} more", head(sim, caster), who(sim, t), pct(hp, max)));
        }
    }
}

/// W 开启：开始存灰色生命。
struct Zap;

impl StableEffectType for Zap {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        let key = (sim_of(sim, caster), caster);
        with_state(key, |s| {
            s.grey = 0;
            s.zapping = true;
        });
        if let Some(n) = counted("zap") {
            wlog(format!("{} ZAP #{n} on", head(sim, caster)));
        }
    }
}

/// W 结束（数据的电击之后 1 tick）：打中英雄全回，只打中小兵野怪回一半。
struct ZapEnd;

impl StableEffectType for ZapEnd {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        let key = (sim_of(sim, caster), caster);
        let grey = with_state(key, |s| {
            s.zapping = false;
            std::mem::take(&mut s.grey)
        });
        let full = has(sim, caster, &md("w_full"));
        let half = has(sim, caster, &md("w_half"));
        let back = if full { grey } else if half { grey / 2 } else { 0 };
        if back > 0 {
            sim.heal(caster, caster, back);
        }
        if let Some(n) = counted("zap_end") {
            let hit = if full { "a champion" } else if half { "minions / monsters only" } else { "nothing" };
            wlog(format!("{} ZAP END #{n}: {grey} grey stored, hit {hit} -> healed {back}", head(sim, caster)));
        }
    }
}

/// R：回复已损生命的 r_miss%。
struct Dose;

impl StableEffectType for Dose {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        let Some(me) = sim.get_entity(caster) else { return };
        let (hp, max) = me.hp();
        let back = (max - hp.min(max)) * params().r_miss / 100;
        if back > 0 {
            sim.heal(caster, caster, back);
        }
        if let Some(n) = counted("dose") {
            wlog(format!("{} DOSE #{n} at {}% hp: healed {back}", head(sim, caster), pct(hp, max)));
        }
    }
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Pleases {
    p: Params,
    sim_no: u64,
    /// 上次给的额外生命攻击力（变了才换 buff）。
    bonus_ad: i32,
}

impl Pleases {
    fn key(&self, me: usize) -> (u64, usize) {
        (self.sim_no, me)
    }

    fn record_hp(&self, sim: &StableSim<'_>, me: usize) {
        let now = sim.tick() as usize;
        if now % 10 != 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let mut log = HP_LOG.lock().unwrap_or_else(|e| e.into_inner());
        let v = log.entry(self.key(me)).or_default();
        v.push((now, e.hp().0));
        v.retain(|s| s.0 + BURST_TICKS + 10 >= now);
    }

    /// 硬控落到身上、被动又好了：清掉、扣血、让数据丢药罐。
    fn shake(&self, sim: &mut StableSim<'_>, me: usize) {
        if has(sim, me, &md("p_cd")) || has(sim, me, &md("p_drop_n")) || !hard_cc(sim, me) {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let (hp, _) = e.hp();
        let at = e.pos();
        let cleared = sim.entity_clear_cc(me);
        let cost = shake_cost(hp);
        sim.entity_set_hp(me, hp - cost);
        sim.add_buff(me, &BuffV1::timed(&md("p_drop_n"), 6));
        let now = sim.tick() as usize;
        with_state(self.key(me), |s| {
            s.can_at = (at.0 as f64, at.1 as f64);
            s.can_until = now + LAND_WAIT + CAN_TICKS;
            s.can_drop = now;
            s.can_seen = false;
            s.walking = false;
        });
        if let Some(n) = counted("shake") {
            wlog(format!("{} SHAKE #{n}: {cleared} controls cleared, {cost} hp paid, tank dropped", head(sim, me)));
        }
    }

    /// 药罐落地那个 tick 记下位置（数据的药罐跟着他飞、落在他脚下，挂上 `can`）；`can` 没了就忘掉。
    fn tank(&self, sim: &StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let now = sim.tick() as usize;
        let has_can = has(sim, me, &md("can"));
        let cd = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).find(|b| b.name() == md("p_cd")).map_or(0, |b| b.duration_tick);
        let at = (e.pos().0 as f64, e.pos().1 as f64);
        let mut line = None;
        with_state(self.key(me), |s| {
            if s.can_until > now {
                if has_can && !s.can_seen {
                    s.can_seen = true;
                    let off = dist(at, s.can_at);
                    s.can_at = at;
                    line = Some(("tank_land", format!("TANK LANDED {} ticks after the shake, {off:.0} from the shake spot",
                                                      now - s.can_drop)));
                } else if tank_gone(has_can, s.can_seen, now, s.can_drop) {
                    let how = if !s.can_seen {
                        "never landed"
                    } else if cd + 1 != s.cd_left {
                        "picked up"
                    } else {
                        "broken / expired"
                    };
                    line = Some(("tank_gone", format!("TANK GONE: {how}{}", if s.walking { " (he walked to it)" } else { "" })));
                    s.can_until = 0;
                    s.walking = false;
                }
            }
            s.cd_left = cd;
        });
        if let Some((kind, msg)) = line {
            if let Some(n) = counted(kind) {
                wlog(format!("{} {msg} #{n}", head(sim, me)));
            }
        }
    }

    /// 攻击力随额外生命涨（e_bonus‰）。
    fn bonus(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if sim.tick() % 30 != 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let extra = bonus_hp(e.hp().1, self.p.hp, self.p.hp_g, e.level());
        let ad = (extra * self.p.e_bonus / 1000) as i32;
        if ad == self.bonus_ad {
            return;
        }
        self.bonus_ad = ad;
        let name = md("e_bonus_ad");
        sim.entity_remove_buff(me, &name);
        if ad > 0 {
            let mut b = BuffV1::named(&name);
            b.attack = ad;
            sim.add_buff(me, &b);
        }
    }
}

impl StablePassive for Pleases {
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
        self.bonus_ad = 0;
        with_state(self.key(me), |s| *s = State::default());
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Dr. Mundo (player {player}, team {team}, sim {}), {:?}", head(sim, me),
                     self.sim_no, self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        self.record_hp(sim, me);
        self.shake(sim, me);
        self.tank(sim, me);
        self.bonus(sim, me);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _: usize, damage: usize) {
        if damage == 0 {
            return;
        }
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        let store = self.p.w_store;
        with_state(self.key(me), |s| {
            if s.zapping {
                s.grey = stored(s.grey, damage, store, max * GREY_CAP_PCT / 100);
            }
        });
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        let mut map = STATE.lock().unwrap_or_else(|e| e.into_inner());
        for (k, s) in map.iter_mut() {
            if k.0 == self.sim_no {
                *s = State::default();
            }
        }
    }
}

// ===================== AI 钩子：R 的时机、去捡药罐 =====================

#[derive(Clone, Default)]
struct Ai;

enum Plan {
    Keep,
    /// 换成这个输入；有话就按这一类记一行日志（R 每 tick 都在等、TANK 只记开始走的那一下：两类分开数）。
    Instead(InputV1, Option<(&'static str, String)>),
}

impl Ai {
    fn plan(&self, sim: &StableSim<'_>, me: usize, kind: InputKindV1, current: Option<usize>) -> Option<Plan> {
        let e = sim.get_entity(me)?;
        let team = e.team();
        let (hp, max) = e.hp();
        let at = (e.pos().0 as f64, e.pos().1 as f64);
        let now = sim.tick() as usize;
        let enemies = foes(sim, team);
        let key = (sim_of(sim, me), me);
        let ult = kind == InputKindV1::Ult;
        let peak = peak_hp(key, now, hp);
        let lost = if peak > hp { (peak - hp) * 100 / max.max(1) } else { 0 };
        let near = within(&enemies, at, R_NEAR);
        let p = params();
        // R first: when it is time, cast it
        if ult {
            if let Some(why) = dose_ok(pct(hp, max), lost, near, p.r_low, p.r_burst) {
                if let Some(n) = counted("dose_ok") {
                    wlog(format!("{} R GO #{n} ({why}: {}% hp, {lost}% lost in 1 s, {near} enemy champions near)",
                                 head(sim, me), pct(hp, max)));
                }
                with_state(key, |s| s.walking = false);
                return Some(Plan::Keep);
            }
        }
        // the tank on the ground (landed, `can` on him), not full, safe or close: walk over it (the data picks it up)
        let can = with_state(key, |s| (s.can_seen && s.can_until > now).then_some(s.can_at));
        if let Some(c) = can.filter(|_| has(sim, me, &md("can"))) {
            let d = dist(at, c);
            let foes_near = within(&enemies, at, SAFE);
            if let Some(why) = tank_ok(pct(hp, max), d, foes_near) {
                let started = with_state(key, |s| !std::mem::replace(&mut s.walking, true));
                let line = started.then(|| {
                    ("tank", format!("TANK: walking to it at {}% hp, {d:.0} away ({why}: {foes_near} enemy champions within {SAFE:.0})",
                                     pct(hp, max)))
                });
                return Some(Plan::Instead(InputV1::move_to(c.0.max(0.0) as u64, c.1.max(0.0) as u64), line));
            }
        }
        with_state(key, |s| s.walking = false);
        if !ult {
            return None;
        }
        let why = format!("R HELD: {}% hp, {lost}% lost in 1 s, {near} enemy champions near", pct(hp, max));
        let target = current.filter(|c| enemies.iter().any(|f| f.0 == *c));
        Some(match target {
            Some(t) => Plan::Instead(InputV1::action(InputKindV1::Attack, InputTargetV1::target(t)), Some(("held", why))),
            None => Plan::Instead(InputV1::move_to(at.0.max(0.0) as u64, at.1.max(0.0) as u64), Some(("held", why))),
        })
    }
}

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
        let b = base?;
        let kind = InputKindV1::from_code(b.kind)?;
        let current = (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id);
        let player = ctx.player_id();
        let (plan, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let plan = self.plan(&sim, me.id(), kind, current)?;
            (plan, head(&sim, me.id()))
        };
        match plan {
            Plan::Keep => None,
            Plan::Instead(input, why) => {
                if !ctx.is_valid_input(&input) && input.kind == InputKindV1::Attack.code() {
                    return None;
                }
                if let Some((kind, why)) = why {
                    if let Some(k) = counted(kind) {
                        wlog(format!("{line} {why} #{k}"));
                    }
                }
                Some(input)
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
        "=== {ID} v{VERSION} (Dr. Mundo: the passive blocks hard CC, Q by current health, E by missing health, W real grey health, R by real health) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:pleases"), Pleases::default());
    module.add_native_effect(format!("{ID}:saw"), Saw);
    module.add_native_effect(format!("{ID}:bonk"), Bonk);
    module.add_native_effect(format!("{ID}:zap"), Zap);
    module.add_native_effect(format!("{ID}:zap_end"), ZapEnd);
    module.add_native_effect(format!("{ID}:dose"), Dose);
    module.add_player_input_ai(Ai);
    host.log(LogLevel::Info, "league_drmundo loaded (passive CC block, health-scaled Q/E/W/R).");
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
    fn the_sim_tag_reads_back() {
        let names = vec!["league_drmundo_w_on".to_string(), format!("{SIM_TAG}4")];
        assert_eq!(sim_tag(names.into_iter()), 4);
        assert_eq!(sim_tag(vec!["league_tahmkench_sim:3".to_string()].into_iter()), 0);
    }

    #[test]
    fn the_saw_takes_a_share_of_current_health() {
        assert_eq!(saw_extra(2000, 20, 90), 310, "20% of 2000 = 400, the data dealt 90");
        assert_eq!(saw_extra(300, 20, 90), 0, "the minimum is the data's own hit");
    }

    #[test]
    fn the_bat_grows_with_missing_health() {
        assert_eq!(bonk_extra(40, 30, 200, 100, 1000, 1000), 0, "full health: nothing more");
        assert_eq!(bonk_extra(40, 30, 200, 100, 500, 1000), 50, "half health: half of 100");
        assert_eq!(bonk_extra(40, 30, 200, 100, 0, 1000), 100);
    }

    #[test]
    fn bonus_health_is_above_the_level() {
        assert_eq!(bonus_hp(1500, 1250, 125, 1), 250);
        assert_eq!(bonus_hp(2500, 1250, 125, 11), 0);
        assert_eq!(bonus_hp(1000, 1250, 125, 1), 0);
    }

    #[test]
    fn the_passive_never_kills() {
        assert_eq!(shake_cost(1000), 70);
        assert_eq!(shake_cost(5), 0);
        assert_eq!(shake_cost(1), 0);
    }

    #[test]
    fn when_to_dose() {
        assert_eq!(dose_ok(30, 0, 1, 40, 25), Some("LOW"));
        assert_eq!(dose_ok(30, 0, 0, 40, 25), None, "no enemy near: keep it");
        assert_eq!(dose_ok(70, 30, 2, 40, 25), Some("BURST"));
        assert_eq!(dose_ok(70, 10, 2, 40, 25), None);
    }

    #[test]
    fn when_to_walk_to_the_tank() {
        assert_eq!(tank_ok(70, 20_000.0, 0), Some("safe"));
        assert_eq!(tank_ok(70, 10_000.0, 2), Some("close"), "two steps away: grab it in the fight");
        assert_eq!(tank_ok(70, 20_000.0, 1), None, "an enemy near and the tank far");
        assert_eq!(tank_ok(90, 0.0, 0), None, "nearly full");
        assert_eq!(tank_ok(50, 50_000.0, 0), None, "too far");
    }

    #[test]
    fn the_tank_is_kept_until_it_lands() {
        // 0.1.0 forgot it on the first tick without `can`: the data's tank lands p_fly + up to 3 ticks after the shake
        assert!(!tank_gone(false, false, 105, 100), "in the air");
        assert!(!tank_gone(true, true, 400, 100), "on the ground");
        assert!(tank_gone(false, true, 400, 100), "picked up or broken");
        assert!(tank_gone(false, false, 100 + LAND_WAIT + 1, 100), "never landed");
    }

    #[test]
    fn grey_health_is_capped() {
        assert_eq!(stored(0, 200, 75, 500), 150);
        assert_eq!(stored(450, 200, 75, 500), 500);
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"e_ad":60,"e_bonus":25,"e_dmg":80,"e_miss":100,"hp":1350,"hp_g":125,"p_cd":2400,"q_dmg":140,"q_pct":20,"r_burst":25,"r_low":40,"r_miss":25,"w_store":75}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_drmundo.py");
        let src = std::fs::read_to_string(path).expect("build_drmundo.py");
        for (key, v) in [("r_range", R_RANGE as usize), ("r_n", R_NEAR as usize), ("p_can_t", CAN_TICKS)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_drmundo.P");
        }
        // the tank flies p_fly ticks after the data's 3-tick check: LAND_WAIT must outlast both
        let fly: usize = src.split("\"p_fly\": ").nth(1).and_then(|v| v.split(',').next()).and_then(|v| v.trim().parse().ok())
            .expect("p_fly in build_drmundo.P");
        assert!(fly + 3 < LAND_WAIT, "p_fly {fly} + 3 >= LAND_WAIT {LAND_WAIT}");
        let d = Params::default();
        for (key, v) in [("p_cd", d.p_cd), ("q_dmg", d.q_dmg), ("q_pct", d.q_pct), ("e_dmg", d.e_dmg), ("e_ad", d.e_ad),
                         ("e_miss", d.e_miss), ("e_bonus", d.e_bonus), ("hp", d.hp), ("hp_g", d.hp_g),
                         ("w_store", d.w_store), ("r_low", d.r_low), ("r_burst", d.r_burst), ("r_miss", d.r_miss)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_drmundo.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["p_cd", "p_drop_n", "can", "w_full", "w_half", "e_bonus_ad"] {
            assert!(md(x).len() <= BUFF_NAME_CAP);
        }
    }
}
