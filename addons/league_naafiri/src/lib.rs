//! 纳亚菲利附加包（用户 2026-10-21「做附加包啊 4也做」）：第二把匕首的斩杀、大招按真正的击杀 / 助攻再扑一次、
//! 聪明的开大、暴吼时四只狗跟着她。
//!
//! 主包是纯数据：第二把匕首读不到目标的生命（英雄联盟按目标已损失的生命加伤），大招的再扑用佛耶戈的击杀窗口（同一个窗口
//! 只认最后一个阵亡的），AI 只要射程里有英雄就开大，暴吼时画面上还是两只狗。`mod.override_info` 把主包的纳亚菲利换成
//! `override/` 里的副本（tools/kit/build_naafiri.py 的 native=1）：数据和主包一样，只是
//! - 第二把匕首的伤害换成本包的原生效果 `league_naafiri:q2`：`q2_dmg` + `q2_ratio`% 攻击力，再按目标已损失生命的比例
//!   最多多 `q_exec`%（英雄联盟的 ExecuteMultiplier 2：空血时翻倍）；
//! - 大招落地不开击杀窗口，只挂 `league_naafiri_r_armed`（`r_win` tick）；被动 `league_naafiri:pack` 在这段时间里她参与的每次
//!   英雄击杀（`on_kill` 的英雄、`on_assist`）都让大招就绪、挂上主包的 `league_naafiri_r_again`（`r_recast` tick，数据读它
//!   决定下一次大招是不带暴吼、带护盾的再扑），一次大招只给一次。
//! - AI 钩子 [`UltAi`]：只在扑得死（飞扑 + 匕首 + 剔骨 + 狗群算出的爆发打得穿他的生命和护盾）、有队友一起打（目标残血、
//!   旁边有我方英雄）或者团战（身边两名以上我方英雄、射程里两名以上敌方英雄）时开大，扑最该扑的那个；不满足时 AI 想开大
//!   就改成普攻原目标。再扑（`r_again`）时扑射程里生命最少的英雄。自己按大招前先看解锁和冷却（league_addons 的规矩）。
//! - 显示钩子（[`view`]）：暴吼的 `league_naafiri_pack4` 期间她的动作换成图里四只狗的 `p4_*` 版本。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_naafiri.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_naafiri";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_naafiri") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
const HERO: &str = "league_naafiri";

/// 主包纳亚菲利的名字（buff、画面、音效都以它开头）。
fn nf(x: &str) -> String {
    format!("{HERO}_{x}")
}

/// 暴吼：狗群四只（主包的 caster buff）。
pub const PACK4: &str = "league_naafiri_pack4";

// 主包参数表 P 里 AI 钩子要算爆发用的数字（make_override.py 核对它们和 P 一样）。
pub const R_RANGE: usize = 60_000;
pub const R_DMG: usize = 70;
pub const R_RATIO: usize = 65;
pub const Q_DMG: usize = 30;
pub const Q_RATIO: usize = 25;
pub const Q_B_DMG: usize = 30;
pub const Q_B_RATIO: usize = 45;
pub const Q2_DMG: usize = 35;
pub const Q2_RATIO: usize = 55;
pub const E_DMG: usize = 35;
pub const E_RATIO: usize = 50;
pub const E2_DMG: usize = 25;
pub const E2_RATIO: usize = 40;
pub const PK_DMG: usize = 8;
pub const PK_RATIO: usize = 12;
pub const ROAR_AD: usize = 20;

/// 爆发里算几口狗咬（飞扑、两把匕首、剔骨落地；暴吼时每口翻倍）。
pub const BITES: usize = 4;
/// 只算一半流血（扑完几秒内就打完了）。
pub const BLEED_SHARE: usize = 50;
/// 有队友一起打：目标生命不到这个百分比……
pub const GANK_HP: usize = 60;
/// ……而且这么远内有我方英雄。
pub const ALLY_R: u64 = 40_000;
/// 团战：她身边这么远内的我方英雄、射程里的敌方英雄各至少两名。
pub const FIGHT_R: u64 = 55_000;
/// 同一类日志隔这么多 tick 才再写。
const LOG_EVERY: usize = 120;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_NAAFIRI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_naafiri.log");
        }
    }
    PathBuf::from("league_naafiri.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the simulation thread in game, league_talon_vault)
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

// ===================== 参数 =====================

/// 被动的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub r_recast: usize,
    pub r_win: usize,
    pub q2_dmg: usize,
    pub q2_ratio: usize,
    pub q_exec: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { r_recast: 720, r_win: 420, q2_dmg: Q2_DMG, q2_ratio: Q2_RATIO, q_exec: 100 }
    }
}

/// `{"r_recast":720,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "r_recast" => &mut p.r_recast,
            "r_win" => &mut p.r_win,
            "q2_dmg" => &mut p.q2_dmg,
            "q2_ratio" => &mut p.q2_ratio,
            "q_exec" => &mut p.q_exec,
            _ => continue,
        };
        *slot = v;
    }
    p
}

/// 每局的被动参数，给原生效果用：(sim 种子, 她) -> 参数（league_graves 的做法；服务端预模拟和画面各算各的）。
static PARAMS: Mutex<Vec<((u64, usize), Params)>> = Mutex::new(Vec::new());

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    let key = (sim.seed(), me);
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).iter().find(|(k, _)| *k == key).map_or_else(Params::default, |(_, p)| p.clone())
}

fn keep_params(sim: &StableSim<'_>, me: usize, p: &Params) {
    let key = (sim.seed(), me);
    let mut all = PARAMS.lock().unwrap_or_else(|e| e.into_inner());
    all.retain(|(k, _)| *k != key);
    all.push((key, p.clone()));
    if all.len() > 64 {
        all.remove(0);
    }
}

// ===================== 算式 =====================

/// 第二把匕首：`q2_dmg` + `q2_ratio`% 攻击力，目标每损失 1% 生命多 `q_exec`/100 %（空血时多 `q_exec`%）。
pub fn q2_damage(p: &Params, attack: usize, hp: usize, max: usize) -> usize {
    let base = p.q2_dmg + attack * p.q2_ratio / 100;
    let missing = max.saturating_sub(hp) * 100 / max.max(1);
    base * (100 * 100 + p.q_exec * missing) / (100 * 100)
}

/// 扑上去的一套爆发（护甲前）：飞扑、第一把匕首和一半流血、第二把匕首（按目标现在的生命算斩杀）、剔骨两下、狗咬；
/// 暴吼的攻击力加成算进去（第一次开大带暴吼）。
pub fn burst(attack: usize, hp: usize, max: usize, roar: bool) -> usize {
    let ad = if roar { attack * (100 + ROAR_AD) / 100 } else { attack };
    let bite = (PK_DMG + ad * PK_RATIO / 100) * if roar { 2 } else { 1 };
    let q2 = q2_damage(&Params::default(), ad, hp, max);
    R_DMG + ad * R_RATIO / 100
        + Q_DMG + ad * Q_RATIO / 100
        + (Q_B_DMG + ad * Q_B_RATIO / 100) * BLEED_SHARE / 100
        + q2
        + E_DMG + ad * E_RATIO / 100
        + E2_DMG + ad * E2_RATIO / 100
        + bite * BITES
}

/// 护甲后的伤害（主包的物理伤害，league_graves 的算法）。
pub fn after_armour(dmg: usize, def: usize) -> usize {
    dmg * 100 / (100 + def)
}

// ===================== 判断 =====================

/// 射程里的一个敌方英雄。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Foe {
    pub id: usize,
    pub hp: usize,
    pub max: usize,
    pub shield: usize,
    pub def: usize,
    /// 这么远内有几名我方英雄（不算她）。
    pub allies_near: usize,
}

impl Foe {
    fn hp_pct(&self) -> usize {
        self.hp * 100 / self.max.max(1)
    }
}

/// 她这时的情况。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Me {
    pub attack: usize,
    /// 这一次大招是再扑（`r_again`：不带暴吼）。
    pub again: bool,
    /// 她身边的我方英雄数（不算她）。
    pub allies_near: usize,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Why {
    Kill,
    Gank,
    Fight,
    Again,
}

/// 扑谁、为什么；`None` = 现在不值得开大。
pub fn pick(me: &Me, foes: &[Foe]) -> Option<(usize, Why)> {
    if foes.is_empty() {
        return None;
    }
    if me.again {
        // 再扑：生命最少的那个
        return foes.iter().min_by_key(|f| (f.hp + f.shield, f.id)).map(|f| (f.id, Why::Again));
    }
    let killable = |f: &Foe| after_armour(burst(me.attack, f.hp, f.max, true), f.def) >= f.hp + f.shield;
    if let Some(f) = foes.iter().filter(|f| killable(f)).min_by_key(|f| (f.hp + f.shield, f.id)) {
        return Some((f.id, Why::Kill));
    }
    if let Some(f) = foes.iter().filter(|f| f.hp_pct() <= GANK_HP && f.allies_near >= 1).min_by_key(|f| (f.hp_pct(), f.id)) {
        return Some((f.id, Why::Gank));
    }
    if me.allies_near >= 2 && foes.len() >= 2 {
        return foes.iter().min_by_key(|f| (f.hp_pct(), f.id)).map(|f| (f.id, Why::Fight));
    }
    None
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Plan {
    /// 照 AI 原来的输入。
    Keep,
    /// 开大扑这个人。
    Ult(usize, Why),
    /// AI 想开大但不值得：改成普攻它原来的目标。
    Hold(usize),
}

/// `ult_target`：AI 原来的输入是大招时的目标；`ready`：大招解锁、冷却好了、她能自己按。
pub fn plan(ult_target: Option<usize>, me: &Me, foes: &[Foe], ready: bool) -> Plan {
    let best = pick(me, foes);
    match (ult_target, best) {
        // the AI's own pounce is already on the right one
        (Some(t), Some((id, _))) if id == t => Plan::Keep,
        (Some(_), Some((id, why))) => Plan::Ult(id, why),
        // 目标不在射程里（正走过去）：到了再判断
        (Some(t), None) if !foes.iter().any(|f| f.id == t) => Plan::Keep,
        (Some(t), None) => Plan::Hold(t),
        (None, Some((id, why))) if ready => Plan::Ult(id, why),
        (None, _) => Plan::Keep,
    }
}

// ===================== AI 钩子 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 被控时什么都不按。
const STOP: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
    CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

fn read(sim: &StableSim<'_>, me: usize) -> Option<(Me, Vec<Foe>, bool)> {
    let e = sim.get_entity(me)?;
    if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
        return None;
    }
    let ready = e.cooldown(SkillSlotV1::Ult).is_some_and(|c| c.unlocked && c.remaining == 0);
    let team = e.team();
    let (allies, enemies): (Vec<_>, Vec<_>) = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_champion() && u.is_alive() && u.id() != me)
        .partition(|u| u.team() == team);
    let near = |a: usize, b: usize, r: u64| sim.distance_sq(a, b) <= r.saturating_mul(r);
    let r = R_RANGE as u64;
    let foes = enemies
        .iter()
        .filter(|u| u.is_targetable() && sim.is_visible(team, u.id()) && near(me, u.id(), r))
        .map(|u| {
            let (hp, max) = u.hp();
            Foe { id: u.id(), hp, max, shield: u.shield(), def: u.stat().defence,
                  allies_near: allies.iter().filter(|a| near(a.id(), u.id(), ALLY_R)).count() }
        })
        .collect();
    let m = Me { attack: e.stat().attack, again: has_buff(sim, me, &nf("r_again")),
                 allies_near: allies.iter().filter(|a| near(a.id(), me, FIGHT_R)).count() };
    Some((m, foes, ready))
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

/// How much farther from a champion the AI's walk must end to be a retreat (league_ult_press's `HOLD_AWAY`).
pub const AWAY: f64 = 10_000.0;
/// An enemy tower this close: under it (league_ult_press's `TOWER_REACH`).
pub const TOWER_REACH: f64 = 75_000.0;
/// A gank or a fight pounces under an enemy tower only on a champion at this health or lower (league_ult_press's
/// `DIVE_HP`).
pub const DIVE_HP: usize = 25;

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// The AI walks away from `to` this tick (a retreat, a disperse from a lost objective): its Move ends more than `AWAY`
/// farther from it than she stands now.
pub fn walking_away(base: Option<InputV1>, me: (f64, f64), to: (f64, f64)) -> bool {
    base.is_some_and(|b| b.kind == InputKindV1::Move.code() && dist((b.x as f64, b.y as f64), to) > dist(me, to) + AWAY)
}

/// A pounce she starts herself that 0.6.5's AI would not take: a gank or a fight at a champion it walks away from, or
/// one under an enemy tower above `DIVE_HP` (a kill and the pounce again after a takedown still go).
pub fn overrules_the_ai(why: Why, walking_away: bool, under_tower: bool, hp_pct: usize) -> bool {
    matches!(why, Why::Gank | Why::Fight) && (walking_away || (under_tower && hp_pct > DIVE_HP))
}

#[derive(Clone, Default)]
pub struct UltAi {
    last: Option<(usize, String)>,
    /// the AI is recalling (`still_recalling`)
    recalling: bool,
}

impl UltAi {
    fn say(&mut self, tick: usize, kind: &str, line: String) {
        if self.last.as_ref().is_none_or(|(t0, k)| k != kind || tick >= t0 + LOG_EVERY) {
            self.last = Some((tick, kind.to_string()));
            wlog(line);
        }
    }
}

impl StablePlayerAi for UltAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ult")
    }

    fn priority(&self) -> i32 {
        110
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let ult_target = base.and_then(|b| {
            (b.kind == InputKindV1::Ult.code() && InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target))
                .then_some(b.target.target_id)
        });
        // AI 在放别的技能、回家时不主动开大（回城引导中没命令的 tick 也算回家：0.6.5 的 AI 自己决定什么时候回城买装备）
        self.recalling = still_recalling(self.recalling, base);
        let busy = self.recalling || base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Return))
        });
        // her spot, each foe in reach's spot, whether an enemy tower covers it (for a pounce she starts herself)
        let (m, foes, ready, line, my_at, spots) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?.id();
            let (m, foes, ready) = read(&sim, me)?;
            let pt = |id: usize| sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64));
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            let towers: Vec<(f64, f64)> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|u| u.is_tower() && u.is_alive() && u.team() != team)
                .map(|u| (u.pos().0 as f64, u.pos().1 as f64))
                .collect();
            let spots: Vec<(usize, (f64, f64), bool)> = foes
                .iter()
                .filter_map(|f| pt(f.id).map(|p| (f.id, p, towers.iter().any(|&w| dist(w, p) <= TOWER_REACH))))
                .collect();
            (m, foes, ready, head(&sim, me), pt(me)?, spots)
        };
        let hp_of = |id: usize| foes.iter().find(|f| f.id == id).map_or(0, |f| f.hp);
        match plan(ult_target, &m, &foes, ready && !busy) {
            Plan::Keep => None,
            Plan::Ult(id, why) => {
                // 自己按之前再看一次解锁和冷却（AI 原来就要开的不用）
                if ult_target.is_none() && !ready {
                    return None;
                }
                if ult_target.is_none() {
                    if let Some(&(_, at, towered)) = spots.iter().find(|s| s.0 == id) {
                        let pct = foes.iter().find(|f| f.id == id).map_or(100, |f| f.hp * 100 / f.max.max(1));
                        if overrules_the_ai(why, walking_away(base, my_at, at), towered, pct) {
                            return None;
                        }
                    }
                }
                let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(id));
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                let from = match ult_target {
                    Some(o) => format!("retargeted from #{o}"),
                    None => "the AI had not cast it".to_string(),
                };
                self.say(tick, "ult", format!("{line} R POUNCE #{id} ({why:?}, hp {}): {from}", hp_of(id)));
                Some(input)
            }
            Plan::Hold(t) => {
                let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                if !ctx.is_valid_input(&attack) {
                    return None;
                }
                self.say(tick, "hold", format!("{line} R HELD: #{t} hp {} not worth it, attacks instead", hp_of(t)));
                Some(attack)
            }
        }
    }
}

// ===================== 被动：击杀 / 助攻 -> 再扑 =====================

#[derive(Clone, Default)]
pub struct Pack {
    p: Params,
    resets: usize,
}

impl Pack {
    fn takedown(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        let armed = nf("r_armed");
        if !has_buff(sim, me, &armed) || !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            return;
        }
        sim.entity_remove_buff(me, &armed);           // 一次大招只给一次
        sim.entity_remove_buff(me, &nf("r_again"));
        sim.add_buff(me, &BuffV1::timed(&nf("r_again"), self.p.r_recast));
        let mut reset = BuffV1::timed(&nf("r_reset"), 2);
        reset.ult_cooldown_mult = 10_000;
        sim.entity_remove_buff(me, &nf("r_reset"));
        sim.add_buff(me, &reset);
        // the multiplier leaves about 1% of the cooldown; from game 0.6.4 the rest goes too (league_pyke)
        let left = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Ult)).map_or(0, |c| c.remaining);
        if left > 0 {
            sim.entity_reduce_cooldown(me, SkillSlotV1::Ult, left);
        }
        let at_me = InputTargetV1::target(me);
        sim.play_view_effect(&nf("r_reset"), me, &at_me, 0, 0, 0);
        sim.play_sfx(&nf("r_reset"), me, &at_me);
        self.resets += 1;
        if self.resets <= 80 {
            wlog(format!("{} RECAST #{} ({why}): the pounce is ready again for {} ticks", head(sim, me), self.resets,
                         self.p.r_recast));
        }
    }
}

impl StablePassive for Pack {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        keep_params(sim, me, &self.p);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Naafiri (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|v| v.is_champion()) {
            self.takedown(sim, me, &format!("killed #{victim}"));
        }
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize) {
        self.takedown(sim, me, "assist");
    }
}

// ===================== 原生效果：第二把匕首 =====================

struct Q2;
impl StableEffectType for Q2 {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let target = input.target_id;
        let Some(atk) = sim.get_entity(caster).map(|e| e.stat().attack) else { return };
        let Some((hp, max, champion)) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| {
            let (hp, max) = e.hp();
            (hp, max, e.is_champion())
        }) else { return };
        let p = params_of(sim, caster);
        let d = q2_damage(&p, atk, hp, max);
        sim.deal_damage(caster, target, d, 0, AttackTypeV1::Skill);
        if champion {
            wlog(format!("{} Q2 #{target}: hp {hp}/{max}, {d} before armour (base {})", head(sim, caster),
                         p.q2_dmg + atk * p.q2_ratio / 100));
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
        "=== {ID} v{VERSION} (Naafiri: the second dagger's execute, the pounce again on every takedown, a smart ult, four hounds in the roar) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:pack"), Pack::default());
    module.add_native_effect(format!("{ID}:q2"), Q2);
    module.add_player_input_ai(UltAi::default());
    view::install_once();
    host.log(LogLevel::Info, "league_naafiri loaded (Naafiri's execute, takedown recast, smart ult and four hounds).");
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
    fn her_own_pounces_leave_0_6_5s_recalls_retreats_and_towers_alone() {
        assert!(still_recalling(false, Some(InputV1::return_home())) && still_recalling(true, None));
        assert!(!still_recalling(true, Some(InputV1::move_to(0, 0))));
        assert!(walking_away(Some(InputV1::move_to(0, 0)), (20_000.0, 0.0), (60_000.0, 0.0)));
        assert!(!walking_away(Some(InputV1::move_to(50_000, 0)), (20_000.0, 0.0), (60_000.0, 0.0)));
        // a gank or a fight: not while the AI walks away, not under a tower above 25 %
        assert!(overrules_the_ai(Why::Gank, true, false, 40) && overrules_the_ai(Why::Fight, false, true, 50));
        assert!(!overrules_the_ai(Why::Gank, false, true, 20) && !overrules_the_ai(Why::Fight, false, false, 90));
        // a kill and the pounce again always
        assert!(!overrules_the_ai(Why::Kill, true, true, 80) && !overrules_the_ai(Why::Again, true, true, 80));
    }

    fn foe(id: usize, hp: usize, max: usize, allies_near: usize) -> Foe {
        Foe { id, hp, max, shield: 0, def: 30, allies_near }
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"r_recast":600,"q_exec":80,"x":1}"#),
                   Params { r_recast: 600, q_exec: 80, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_second_dagger_doubles_on_an_empty_target() {
        let p = Params::default();
        let base = q2_damage(&p, 100, 1000, 1000);
        assert_eq!(base, 35 + 55);
        assert_eq!(q2_damage(&p, 100, 500, 1000), base * 3 / 2);
        assert_eq!(q2_damage(&p, 100, 0, 1000), base * 2);
    }

    #[test]
    fn she_pounces_on_what_she_can_kill() {
        let me = Me { attack: 150, again: false, allies_near: 0 };
        let tank = foe(1, 2000, 2000, 0);
        let weak = foe(2, 300, 1500, 0);
        assert_eq!(pick(&me, &[tank, weak]), Some((2, Why::Kill)));
        // nobody killable, nobody hurt, alone: not worth it
        assert_eq!(pick(&me, &[tank]), None);
        // a hurt one with an ally beside him: the gank
        assert_eq!(pick(&me, &[tank, foe(3, 800, 2000, 1)]), Some((3, Why::Gank)));
        // a teamfight: the lowest share of health
        let team = Me { allies_near: 2, ..me };
        assert_eq!(pick(&team, &[tank, foe(4, 1500, 2000, 0)]), Some((4, Why::Fight)));
        // the recast: the lowest health in reach
        let again = Me { again: true, ..me };
        assert_eq!(pick(&again, &[tank, foe(5, 1400, 3000, 0)]), Some((5, Why::Again)));
    }

    #[test]
    fn the_ai_is_held_or_retargeted() {
        let me = Me { attack: 150, again: false, allies_near: 0 };
        let tank = foe(1, 2000, 2000, 0);
        let weak = foe(2, 300, 1500, 0);
        assert_eq!(plan(Some(1), &me, &[tank], true), Plan::Hold(1));
        assert_eq!(plan(Some(1), &me, &[tank, weak], true), Plan::Ult(2, Why::Kill));
        assert_eq!(plan(Some(2), &me, &[tank, weak], true), Plan::Keep);
        assert_eq!(plan(None, &me, &[tank, weak], true), Plan::Ult(2, Why::Kill));
        assert_eq!(plan(None, &me, &[tank, weak], false), Plan::Keep); // not ready: never pressed
        assert_eq!(plan(Some(9), &me, &[tank], true), Plan::Keep); // walking up to it
    }

    #[test]
    fn the_names_fit() {
        for x in ["r_armed", "r_again", "r_reset", "pack4"] {
            assert!(nf(x).len() <= BUFF_NAME_CAP);
        }
        assert_eq!(nf("pack4"), PACK4);
    }
}
