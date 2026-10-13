//! 莫德凯撒附加包（用户选了「要附加包 league_mordekaiser」）：主包数据做不到的两件事。
//!
//! `mod.override_info` 把主包的莫德凯撒换成 `override/` 里的副本（tools/kit/build_mordekaiser.py 的 native=1）：数据和
//! 主包一样，只是
//! - 被动挂本包的 `league_mordekaiser:revenant`（参数在英雄数据的 `passive.params` 里）；黑暗起兮仍在数据里；
//! - R 出手那一 tick 调本包的 `league_mordekaiser:realm`，不再用数据里的固定数值诅咒 / 嘲讽 / 拴绳 / 击杀判定；
//! - W 调本包的 `league_mordekaiser:indestructible`，不再给固定数值的护盾。
//!
//! - **轮回绝境**（用户：「R做不了独特空间吗？」，选了「放逐两人 + 附加包算单挑」，「嘲讽不做」）：射程 `R_RANGE` 里挑攻击
//!   + 法强最高的敌方英雄（英雄联盟里玩家都把大招给对面的核心）；按他此刻的面板真偷 `R_STEAL`%：攻击、法强、护甲、魔抗、
//!   最大生命（他身上 `league_mordekaiser_r_curse` 减，莫德身上 `league_mordekaiser_r_steal` 加，`R_T` tick）。两人都被放逐
//!   `R_T` tick（`entity_banish`：谁也选不中、看不见，原地留一个 `league_mordekaiser_r_realm` 漩涡），在「领域」里单挑：
//!   被动每 tick 看，谁的攻击间隔到了谁出手（`deal_damage` 走引擎自己的伤害流程：护甲魔抗、击杀、统计）。莫德：攻击 +
//!   `A_AP`% 法强，外加满层黑暗起兮的光环（每 `P_PER` tick `P_DMG` + `P_AP`% 法强 + `P_HP`% 最大生命）；对方：攻击 +
//!   `FOE_AP`% 法强（代替他的技能）。对方死在领域里：莫德回复 `kill` + `kill_ap`% 法强，偷来的属性再留 `keep` tick（英雄联盟：
//!   留到对方复活），莫德提前出来；莫德先死：对方提前出来。
//! - **不坏之身**：英雄联盟的护盾来自打出的伤害（`w_dealt`%，打小兵野怪只算 `MINION`%）和受到的伤害（`w_taken`%），最多
//!   最大生命的 `w_cap`%，脱战 `DECAY_AFTER` tick 后慢慢掉。被动在每次命中 / 受伤时攒，W 放出时整份变成护盾（至少最大生命
//!   的 `W_BASE`%，持续 `w_t`），`w_heal_at` tick 后按护盾还剩多少回复 `w_heal`%。
//!
//! 数字：参数从英雄数据来；R / W 的效果在被动之外运行，用到的数字写在这里（`R_*`、`W_*`），`tests::the_numbers_match_the_kit`
//! 读主包的参数表核对。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_mordekaiser.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_mordekaiser";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";

/// 主包莫德凯撒的名字（buff、画面都以它开头）。
fn mk(x: &str) -> String {
    format!("league_mordekaiser_{x}")
}

// ===================== 数值（主包 build_mordekaiser.P） =====================

/// 大招：射程（r_range）、持续（r_t）、偷多少 %（r_steal）、嘲讽（r_taunt）。
pub const R_RANGE: f64 = 48_000.0;
pub const R_T: usize = 420;
pub const R_STEAL: usize = 10;
/// 领域里：莫德的普攻带 A_AP% 法强（a_ap），满层光环每 P_PER tick P_DMG + P_AP% 法强 + P_HP% 最大生命（p_per, p_dmg, p_ap,
/// p_hp）；对方每次出手带 FOE_AP% 法强（代替技能）；读不到攻击间隔时用 SWING。
pub const A_AP: usize = 40;
pub const P_PER: usize = 30;
pub const P_DMG: usize = 4;
pub const P_AP: usize = 15;
pub const P_HP: usize = 1;
pub const FOE_AP: usize = 40;
pub const SWING: usize = 60;
/// 两个身体的半径（射程算到身体边上）。
pub const BODY: f64 = 12_000.0;
/// W：护盾持续（w_t）、多久后按剩余护盾回血（w_heal_at）。
pub const W_T: usize = 180;
pub const W_HEAL_AT: usize = 150;
/// W 的护盾至少是最大生命的这么多 %（英雄联盟 5%）。
pub const W_BASE: usize = 5;
/// 打小兵、野怪只算这么多 %（英雄联盟 25%）。
pub const MINION: usize = 25;
/// 脱战多久后攒的护盾开始掉，每 tick 掉最大生命的 1/DECAY_DIV（约每秒 1%）。
pub const DECAY_AFTER: usize = 60;
pub const DECAY_DIV: f64 = 6_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_MORDEKAISER_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_mordekaiser.log");
        }
    }
    PathBuf::from("league_mordekaiser.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (the user: 「LOL mod让游戏掉帧
    // 很严重 加载很卡」, PR #242)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}
", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first).
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

// ===================== 计算（单元测试用） =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 偷走的数值：攻击、法强、护甲、魔抗、最大生命。
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Steal {
    pub attack: i32,
    pub magic_power: i32,
    pub defence: i32,
    pub magic_resistance: i32,
    pub hp: i32,
}

/// `pct`% 的面板（向下取整，至少 0）。
pub fn steal_of(s: &StatV1, max_hp: usize, pct: usize) -> Steal {
    let f = |v: usize| (v * pct / 100) as i32;
    Steal { attack: f(s.attack), magic_power: f(s.magic_power), defence: f(s.defence),
            magic_resistance: f(s.magic_resistance), hp: f(max_hp) }
}

fn steal_buff(name: &str, ticks: usize, s: Steal, sign: i32) -> BuffV1 {
    let mut b = BuffV1::timed(name, ticks);
    b.attack = sign * s.attack;
    b.magic_power = sign * s.magic_power;
    b.defence = sign * s.defence;
    b.magic_resistance = sign * s.magic_resistance;
    b.hp = sign * s.hp;
    b
}

/// 大招挑谁：(id, 位置, 攻击 + 法强)；射程以内分最高的，同分取近的。None = 射程里没有。
pub fn pick_carry(me: (f64, f64), champs: &[(usize, (f64, f64), usize)], reach: f64) -> Option<usize> {
    let mut best: Option<(usize, usize, f64)> = None;
    for &(id, at, power) in champs {
        let d = dist(me, at);
        if d > reach {
            continue;
        }
        if best.is_none_or(|b| power > b.1 || (power == b.1 && d < b.2)) {
            best = Some((id, power, d));
        }
    }
    best.map(|b| b.0)
}

/// 攒护盾：打出 `dealt`（小兵野怪按 MINION%）、受到 `taken`，上限最大生命的 cap%。
pub fn gain(pot: f64, dealt: usize, minion: bool, taken: usize, p: &Params, max_hp: usize) -> f64 {
    let d = dealt as f64 * if minion { MINION as f64 / 100.0 } else { 1.0 } * p.w_dealt as f64 / 100.0;
    let t = taken as f64 * p.w_taken as f64 / 100.0;
    (pot + d + t).min(max_hp as f64 * p.w_cap as f64 / 100.0)
}

/// W 放出时的护盾：攒的，至少 W_BASE%，至多 cap%。
pub fn shield_of(pot: f64, max_hp: usize, cap: usize) -> usize {
    let lo = max_hp * W_BASE / 100;
    let hi = max_hp * cap / 100;
    (pot.round() as usize).clamp(lo, hi.max(lo))
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub kill: usize,
    pub kill_ap: usize,
    pub keep: usize,
    pub w_dealt: usize,
    pub w_taken: usize,
    pub w_cap: usize,
    pub w_heal: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { kill: 150, kill_ap: 50, keep: 900, w_dealt: 45, w_taken: 15, w_cap: 30, w_heal: 40 }
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
            "kill" => p.kill = v,
            "kill_ap" => p.kill_ap = v,
            "keep" => p.keep = v,
            "w_dealt" => p.w_dealt = v,
            "w_taken" => p.w_taken = v,
            "w_cap" => p.w_cap = v,
            "w_heal" => p.w_heal = v,
            _ => {}
        }
    }
    p
}

// ===================== 每个莫德凯撒的状态 =====================

#[derive(Clone, Copy, Debug)]
struct Realm {
    target: usize,
    until: usize,
    steal: Steal,
    /// the next tick each side swings (him, the cursed one) and his aura's next pulse
    mine: usize,
    theirs: usize,
    aura: usize,
    swings: (usize, usize),
}

#[derive(Clone, Copy, Debug)]
struct Guard {
    given: usize,
    before: usize,
    at: usize,
}

#[derive(Clone, Copy, Debug, Default)]
struct State {
    pot: f64,
    fight: usize,
    realm: Option<Realm>,
    guard: Option<Guard>,
}

/// (哪一局的哪种模拟, 实体)：R 和 W 是效果，被动是另一个对象，状态放在这里共用。
type Key = (u32, u64, u64, usize);

static STATES: LazyLock<Mutex<HashMap<Key, State>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn key(sim: &StableSim<'_>, id: usize) -> Key {
    let o = sim.sim_origin().unwrap_or_default();
    (o.kind, o.match_id, o.set_index, id)
}

fn with_state<T>(sim: &StableSim<'_>, id: usize, f: impl FnOnce(&mut State) -> T) -> T {
    let mut map = STATES.lock().unwrap_or_else(|e| e.into_inner());
    if map.len() > 4096 {
        map.clear();
    }
    f(map.entry(key(sim, id)).or_default())
}

fn alive_at(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() {
        return None;
    }
    let (x, y) = e.pos();
    Some((x as f64, y as f64))
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Revenant {
    p: Params,
    guards: usize,
}

impl Revenant {
    fn decay(&self, sim: &StableSim<'_>, me: usize) {
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        let t = sim.tick();
        with_state(sim, me, |s| {
            if t > s.fight + DECAY_AFTER && s.pot > 0.0 {
                s.pot = (s.pot - max as f64 / DECAY_DIV).max(0.0);
            }
        });
    }

    fn guard(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let t = sim.tick();
        let Some(g) = with_state(sim, me, |s| s.guard) else { return };
        if t < g.at + W_HEAL_AT {
            return;
        }
        with_state(sim, me, |s| s.guard = None);
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let left = e.shield().saturating_sub(g.before).min(g.given);
        let amount = left * self.p.w_heal / 100;
        if amount > 0 {
            sim.heal(me, me, amount);
        }
        self.guards += 1;
        if self.guards <= 40 || self.guards % 25 == 0 {
            wlog(format!("{} W HEAL #{}: {left} of {} shield left -> +{amount}", head(sim, me), self.guards, g.given));
        }
    }

    fn realm(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let t = sim.tick();
        let Some(r) = with_state(sim, me, |s| s.realm) else { return };
        let mine = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.stat(), e.hp().1, e.attack_interval()));
        let theirs = sim.get_entity(r.target).filter(|e| e.is_alive()).map(|e| (e.stat(), e.attack_interval()));
        match (mine, theirs) {
            (None, _) => {
                // he died first: the cursed one comes back now
                with_state(sim, me, |s| s.realm = None);
                sim.entity_clear_cc(r.target);
                wlog(format!("{} R LOST: he died in the realm ({} swings vs {}); {} back", head(sim, me), r.swings.0,
                             r.swings.1, who(sim, r.target)));
            }
            (Some((ms, _, _)), None) => {
                // the cursed one died in the realm: the heal, the stats kept longer, out now
                with_state(sim, me, |s| s.realm = None);
                let amount = self.p.kill + self.p.kill_ap * ms.magic_power / 100;
                sim.heal(me, me, amount);
                sim.entity_remove_buff(me, &mk("r_keep"));
                sim.add_buff(me, &steal_buff(&mk("r_keep"), self.p.keep, r.steal, 1));
                sim.entity_clear_cc(me);
                wlog(format!("{} R WON: {} died in the realm ({} swings vs {}) -> +{amount} hp, {:?} kept {} more ticks",
                             head(sim, me), who(sim, r.target), r.swings.0, r.swings.1, r.steal, self.p.keep));
            }
            (Some(_), Some(_)) if t >= r.until => {
                with_state(sim, me, |s| s.realm = None);
                wlog(format!("{} R END: both out ({} swings vs {})", head(sim, me), r.swings.0, r.swings.1));
            }
            (Some((ms, max, mi)), Some((ts, ti))) => {
                let mut r = r;
                if t >= r.mine {
                    sim.deal_damage(me, r.target, ms.attack, ms.magic_power * A_AP / 100, AttackTypeV1::BaseAttack);
                    r.mine = t + if mi > 0 { mi } else { SWING };
                    r.swings.0 += 1;
                }
                if t >= r.aura {
                    sim.deal_damage(me, r.target, 0, P_DMG + ms.magic_power * P_AP / 100 + max * P_HP / 100,
                                    AttackTypeV1::Skill);
                    r.aura = t + P_PER;
                }
                if t >= r.theirs {
                    sim.deal_damage(r.target, me, ts.attack, ts.magic_power * FOE_AP / 100, AttackTypeV1::BaseAttack);
                    r.theirs = t + if ti > 0 { ti } else { SWING };
                    r.swings.1 += 1;
                }
                with_state(sim, me, |s| s.realm = Some(r));
            }
        }
    }
}

impl StablePassive for Revenant {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let p = self.p;
        with_state(sim, me, |s| *s = State { pot: 0.0, fight: 0, realm: None, guard: None });
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(key(sim, me), p);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Mordekaiser (player {player}, team {team}), {p:?}", head(sim, me)));
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        let minion = sim.get_entity(target).is_some_and(|e| !e.is_champion());
        let (t, p, d) = (sim.tick(), self.p, *damage);
        with_state(sim, me, |s| {
            s.pot = gain(s.pot, d, minion, 0, &p, max);
            s.fight = t;
        });
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _: usize, damage: usize) {
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        let (t, p) = (sim.tick(), self.p);
        with_state(sim, me, |s| {
            s.pot = gain(s.pot, 0, false, damage, &p, max);
            s.fight = t;
        });
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.decay(sim, me);
        self.guard(sim, me);
        self.realm(sim, me);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        let _ = sim;
    }
}

/// 被动的参数，效果（R / W）也要用：按 (局, 实体) 记下。
static PARAMS: LazyLock<Mutex<HashMap<Key, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(sim: &StableSim<'_>, id: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&key(sim, id)).copied().unwrap_or_default()
}

// ===================== R 轮回绝境 =====================

fn realm(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let Some(me) = alive_at(sim, caster) else { return };
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let mut champs = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_champion() || !u.is_targetable() {
            continue;
        }
        let (x, y) = u.pos();
        let s = u.stat();
        champs.push((u.id(), (x as f64, y as f64), s.attack + s.magic_power));
    }
    let asked = (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id);
    let Some(target) = pick_carry(me, &champs, R_RANGE + BODY).or(asked) else {
        wlog(format!("{} R: no enemy champion in reach", head(sim, caster)));
        return;
    };
    let Some(e) = sim.get_entity(target) else { return };
    let steal = steal_of(&e.stat(), e.hp().1, R_STEAL);
    sim.entity_remove_buff(target, &mk("r_curse"));
    sim.add_buff(target, &steal_buff(&mk("r_curse"), R_T, steal, -1));
    sim.entity_remove_buff(caster, &mk("r_steal"));
    sim.add_buff(caster, &steal_buff(&mk("r_steal"), R_T, steal, 1));
    let into_me = sim.entity_banish(caster, caster, R_T, &mk("r_realm"), "");
    let into_it = sim.entity_banish(caster, target, R_T, "", "");
    let t = sim.tick();
    with_state(sim, caster, |s| {
        s.realm = Some(Realm { target, until: t + R_T, steal, mine: t + 1, theirs: t + 1, aura: t + 1, swings: (0, 0) });
    });
    let swapped = asked.is_some_and(|a| a != target);
    wlog(format!("{} R REALM with {}{}: steals {:?}, both banished {R_T} ticks{}", head(sim, caster),
                 who(sim, target), if swapped { format!(" (the AI asked for {})", who(sim, asked.unwrap())) } else {
                     String::new() }, steal, if into_me && into_it { "" } else { " (entity_banish refused)" }));
}

struct RealmEffect;

impl StableEffectType for RealmEffect {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        realm(sim, caster, input);
    }
}

// ===================== W 不坏之身 =====================

fn indestructible(sim: &mut StableSim<'_>, caster: usize) {
    let Some(e) = sim.get_entity(caster) else { return };
    if !e.is_alive() {
        return;
    }
    let (max, before) = (e.hp().1, e.shield());
    let p = params_of(sim, caster);
    let pot = with_state(sim, caster, |s| std::mem::take(&mut s.pot));
    let given = shield_of(pot, max, p.w_cap);
    let ok = sim.entity_add_shield(caster, given, W_T);
    let t = sim.tick();
    with_state(sim, caster, |s| s.guard = Some(Guard { given, before, at: t }));
    wlog(format!("{} W SHIELD {given} (stored {pot:.0}, max hp {max}){}", head(sim, caster),
                 if ok { "" } else { " (entity_add_shield refused)" }));
}

struct Indestructible;

impl StableEffectType for Indestructible {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        indestructible(sim, caster);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Mordekaiser: Realm of Death banishes the carry and him into a duel, Indestructible from the damage) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:revenant"), Revenant::default());
    module.add_native_effect(format!("{ID}:realm"), RealmEffect);
    module.add_native_effect(format!("{ID}:indestructible"), Indestructible);
    host.log(LogLevel::Info, "league_mordekaiser loaded (Realm of Death, Indestructible).");
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

    fn stat(attack: usize, ap: usize, def: usize, mr: usize) -> StatV1 {
        StatV1 { attack, magic_power: ap, hp: 0, defence: def, magic_resistance: mr, move_speed: 0, hp_regen: 0,
                 stack: 0, crit_chance: 0 }
    }

    #[test]
    fn ten_percent_of_the_carry() {
        let s = steal_of(&stat(250, 40, 60, 45), 2400, 10);
        assert_eq!(s, Steal { attack: 25, magic_power: 4, defence: 6, magic_resistance: 4, hp: 240 });
    }

    #[test]
    fn the_carry_is_picked_in_reach() {
        let me = (0.0, 0.0);
        let champs = [(1, (20_000.0, 0.0), 150), (2, (50_000.0, 0.0), 320), (3, (90_000.0, 0.0), 900)];
        assert_eq!(pick_carry(me, &champs, R_RANGE + BODY), Some(2));
        assert_eq!(pick_carry(me, &champs[..1], R_RANGE + BODY), Some(1));
        assert_eq!(pick_carry(me, &champs[2..], R_RANGE + BODY), None);
        // a tie: the nearer
        let tie = [(4, (30_000.0, 0.0), 300), (5, (10_000.0, 0.0), 300)];
        assert_eq!(pick_carry(me, &tie, R_RANGE + BODY), Some(5));
    }

    #[test]
    fn the_shield_grows_from_the_fight_and_stops_at_the_cap() {
        let p = Params::default();
        let mut pot = gain(0.0, 200, false, 0, &p, 3000);
        assert!((pot - 90.0).abs() < 1e-6);
        pot = gain(pot, 200, true, 0, &p, 3000);
        assert!((pot - 112.5).abs() < 1e-6);
        pot = gain(pot, 0, false, 300, &p, 3000);
        assert!((pot - 157.5).abs() < 1e-6);
        assert!((gain(0.0, 100_000, false, 0, &p, 3000) - 900.0).abs() < 1e-6);
        assert_eq!(shield_of(0.0, 3000, 30), 150);
        assert_eq!(shield_of(400.0, 3000, 30), 400);
        assert_eq!(shield_of(5000.0, 3000, 30), 900);
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"keep":900,"kill":150,"kill_ap":50,"w_cap":30,"w_dealt":45,"w_heal":40,"w_taken":15}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_mordekaiser.py");
        let src = std::fs::read_to_string(path).expect("build_mordekaiser.py");
        for (key, v) in [("r_range", R_RANGE as usize), ("r_t", R_T), ("r_steal", R_STEAL), ("w_t", W_T),
                         ("w_heal_at", W_HEAL_AT), ("a_ap", A_AP), ("p_per", P_PER), ("p_dmg", P_DMG), ("p_ap", P_AP),
                         ("p_hp", P_HP)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_mordekaiser.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["r_curse", "r_steal", "r_keep"] {
            assert!(mk(x).len() <= BUFF_NAME_CAP);
        }
    }
}
