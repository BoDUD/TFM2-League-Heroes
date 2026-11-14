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
//! - **狗群是真的单位（0.2.0，2026-11-14；用户：「召唤物的全做啊 剩下的一批英雄也做了啊」）**：主包里两只伙伴画在她自己的
//!   每一帧里，伤害是她每次命中时的一口撕咬。英雄联盟里伙伴是跟着她、自己打、能被打死的小狼，死了过一会儿再来，和她一起
//!   阵亡。稳定 mod API 的 `spawn_unit`（公用部分在萨科附加包的 `summon.rs`，一个召唤者好几个单位用它的 `Flock`）：她出生时被动
//!   排原生效果 `:hound` 在她身后生成 `PACK_N` 只 `league_naafiri_packmate`（[`packmate_spec`]），被打死的过 `HOUND_RESPAWN`
//!   tick 再来，到时间（`HOUND_LIFE`）的马上换一只；暴吼（`league_naafiri_pack4` 挂上）时再来 `CALL_N` 只，留到暴吼结束
//!   （`:call`）。有单位以后她身上一直挂着 `SOLO`：副本的数据读它，不再放狗群的撕咬和扑上去挂着的那一套，显示钩子把她的动作
//!   换成图里没有狗的 `solo_*` 版本。她阵亡时把她的狗放逐到它们的时间结束（`entity_banish`：看不见、打不到、不能动——没有让单位
//!   消失的接口）。生成不了（宿主没有这个接口、失败、测试开关关了、读不成单位）就不挂 `SOLO`，和今天一模一样。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_naafiri.log`，每次启动游戏重写；狗群的行以 `HOUND` 开头。
//! 测试开关：日志旁边的 `league_naafiri.cfg`（`summon.rs`：`unit=off` / `still=1` / `name=`）。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

use summon::{Event, Flock, Pt};

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

#[derive(Clone)]
pub struct Pack {
    p: Params,
    resets: usize,
    /// Her spawns in this simulation (the params go into the first one's line only, 0.1.2).
    spawns: usize,
    /// 0.2.0: her own unit, her packmates as units, the pack hounds asked for and not yet come, whether they are units
    /// (`SOLO` on her), the tick the missing ones are asked for, the roar seen last tick.
    me: usize,
    hounds: Flock<HoundBook>,
    pending: usize,
    units: bool,
    next_ask: usize,
    roared: bool,
}

impl Default for Pack {
    fn default() -> Self {
        Pack { p: Params::default(), resets: 0, spawns: 0, me: 0, hounds: Flock::new(H_UID, HOUND_CAP, HOUND_LIFE), pending: 0,
               units: false, next_ask: 0, roared: false }
    }
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
        // a new life: the old one's packmates are out of play (banished at her death) - a new pack comes at once
        self.let_go(sim, me, "Naafiri respawned");
        (self.me, self.next_ask, self.roared) = (me, sim.tick(), false);
        keep_params(sim, me, &self.p);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        self.spawns += 1;
        // the params on her first spawn of a set only (0.1.2; 11-04's logs: 146 SPAWN lines, each with the whole table)
        if self.spawns == 1 {
            wlog(format!("{} SPAWN: the add-on's Naafiri (player {player}, team {team}), {:?}", head(sim, me), self.p));
        } else if self.spawns <= 40 {
            wlog(format!("{} SPAWN #{}: the add-on's Naafiri again (player {player}, team {team})", head(sim, me), self.spawns));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        // League's packmates die with her: banished until their time (a dead champion's passive does not run)
        let me = self.me;
        self.banish_all(sim, me);
        self.let_go(sim, me, "Naafiri died");
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let Some((alive, team, here)) = sim.get_entity(me).map(|e| (e.is_alive(), e.team(), summon::at_of(&e))) else { return };
        if alive {
            self.me = me;
            self.pack_tick(sim, player, me, team, here);
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, target: usize, damage: &mut usize) {
        self.hooked(sim, "on_attack", entity, target, Some(*damage));
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_unit_kill", entity, victim, None);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.hooked(sim, "on_kill", me, victim, None);
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

// ===================== 狗群作为单位（0.2.0） =====================

/// Her attack's interval and reach, The Call of the Pack's time (the main pack's atk_cd, atk_range, roar_t; make_override.py
/// checks them against P).
pub const ATK_CD: usize = 58;
pub const ATK_RANGE: usize = 23_000;
pub const ROAR_T: usize = 300;
/// Each packmate's bite: half the riding pack's (two of them), PK_DMG / 2 + PK_RATIO / 2 % of her attack, at her own pace.
pub const HOUND_HIT: usize = 4;
pub const HOUND_HIT_AD: usize = 6;
/// The unit sheet's attack: ticks long and the tick the bite lands (tools/art/unit_naafiri_packmate.py: 420 ms, the bite
/// 170 ms in).
pub const HOUND_ACT: usize = 25;
pub const HOUND_LANDS: usize = 10;
/// The unit name: the game draws it from asset/base/aseprite_resources/champions/<name>, which mod.override_info sends to
/// the main pack's league/champions/league_naafiri_packmate.
pub const PACKMATE: &str = "league_naafiri_packmate";
/// `PACK_N` packmates (League: 2-5 by level; the main pack draws two), each `HOUND_LIFE` ticks at a time (League: no end
/// but her death - a new one takes the place of one timed out), back `HOUND_RESPAWN` ticks after one is killed (League's
/// passive cooldown, 30-10 s by level); `CALL_N` more in The Call of the Pack, for its time (League: +2 for the hunt).
/// `HOUND_HP_PCT` % of her health cap (League: 80-336 against her 610-2395), `HOUND_DEF_PCT` % of her armour and magic
/// resistance (League: 0-35 against 28-108), her move speed and reach (League: hers).
pub const PACK_N: usize = 2;
pub const CALL_N: usize = 2;
pub const HOUND_LIFE: usize = 3_600;
pub const HOUND_RESPAWN: usize = 900;
pub const HOUND_HP_PCT: usize = 13;
pub const HOUND_DEF_PCT: usize = 30;
/// They come out this far behind her (away from the nearest enemy champion), a quarter turn apart.
pub const HOUND_SPREAD: f64 = 14_000.0;
/// On her while her packmates are units: the copy's data plays no pack bite and no riding pack, the view hook her solo_*.
pub const SOLO: &str = "league_naafiri_solo";
pub const H_UID: &str = "league_naafiri_h_uid";
/// Packmates on the books at once; ticks SOLO is laid for (renewed every tick); the handoff buffs.
pub const HOUND_CAP: usize = 8;
const SOLO_TICKS: usize = 30;
const UID_TICKS: usize = 6;
/// A unit gone within this many ticks was never really there.
pub const LOST_AGE: usize = 6;
/// Ticks between looks for missing packmates when nothing else holds them back.
const ASK_EVERY: usize = 30;

/// The test knobs (`league_naafiri.cfg` beside the log), read once.
static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

/// Lines of each kind of the units' a launch (league_shaco_backstab's): the server's presims the first 40, then every 200th;
/// the match on screen all.
static COUNTS: LazyLock<Mutex<std::collections::HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(Default::default()));

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let shown = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= 40 || *n % 200 == 0).then_some(*n)
}

/// A packmate from her numbers now (`stat`, her health cap `max_hp`), living `life` ticks.
pub fn packmate_spec(stat: &StatV1, max_hp: usize, life: usize) -> summon::Spec {
    summon::Spec {
        name: PACKMATE.to_string(),
        life,
        stat: StatV1 { attack: stat.attack, magic_power: 0, hp: (max_hp * HOUND_HP_PCT / 100).max(1),
                       defence: stat.defence * HOUND_DEF_PCT / 100, magic_resistance: stat.magic_resistance * HOUND_DEF_PCT / 100,
                       move_speed: stat.move_speed, hp_regen: 0, stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: HOUND_HIT_AD, attack: HOUND_HIT, range: ATK_RANGE, cooltime: ATK_CD, duration: HOUND_ACT,
                               start_timing: HOUND_LANDS, cancelable: false, attack_type: AttackTypeV1::BaseAttack.code() },
    }
}

/// Where packmate `k` comes out: `HOUND_SPREAD` behind her at `here` (away from `foe`, the nearest enemy champion; none:
/// as if one stood east of her), the k-th an eighth of a turn to one side or the other.
pub fn hound_spot(here: Pt, foe: Option<Pt>, k: usize) -> Pt {
    let toward = foe.map(|f| (f.1 - here.1).atan2(f.0 - here.0)).unwrap_or(0.0);
    let side = if k % 2 == 0 { 1.0 } else { -1.0 } * std::f64::consts::FRAC_PI_4 * (1 + k / 2) as f64;
    let a = toward + std::f64::consts::PI + side;
    ((here.0 + HOUND_SPREAD * a.cos()).max(0.0), (here.1 + HOUND_SPREAD * a.sin()).max(0.0))
}

/// One packmate for Naafiri `me` at `at` for `life` ticks, handed to her passive by a `<H_UID>:<id>` buff. -> its id.
fn make_hound(sim: &mut StableSim<'_>, me: usize, at: Pt, life: usize, what: &str, by: &str) -> Option<usize> {
    let (team, stat, max) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1))?;
    let spec = packmate_spec(&stat, max, life).with(&KNOBS);
    let at = summon::inside(summon::field(sim), at);
    match summon::spawn(sim, me, team, at, &spec) {
        Some(id) => {
            sim.add_buff(me, &BuffV1::timed(&summon::handoff(H_UID, id), UID_TICKS));
            if let Some(k) = tally(sim, "hound spawn") {
                wlog(format!("{} HOUND SPAWN #{k} ({what}, {by}): unit #{id} for team {team} at {}: {}", head(sim, me), summon::pt(at),
                             spec.shown()));
            }
            Some(id)
        }
        None => {
            if let Some(k) = tally(sim, "hound fail") {
                wlog(format!("{} HOUND SPAWN FAILED #{k} ({what}, {by}): spawn_unit gave no unit for '{}' at {}", head(sim, me),
                             spec.name, summon::pt(at)));
            }
            None
        }
    }
}

fn spot_of(input: &InputTargetV1, sim: &StableSim<'_>, caster: usize) -> Option<Pt> {
    if InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Pos) {
        return Some((input.x as f64, input.y as f64));
    }
    sim.get_entity(caster).map(|e| summon::at_of(&e))
}

fn at_input(at: Pt) -> InputTargetV1 {
    InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64)
}

/// `:hound` - one of her pack (the passive queues one for each missing); the input is where it comes out.
struct HoundFx;

impl StableEffectType for HoundFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if let Some(at) = spot_of(&input, sim, caster) {
            make_hound(sim, caster, at, HOUND_LIFE, "her pack", "the queued effect");
        }
    }
}

/// `:call` - one of the two The Call of the Pack brings, for the roar's time.
struct CallFx;

impl StableEffectType for CallFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if let Some(at) = spot_of(&input, sim, caster) {
            make_hound(sim, caster, at, ROAR_T, "the call", "the queued effect");
        }
    }
}

/// Which packmates these are.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum Hound {
    /// Her pack: back after a while when killed.
    #[default]
    Pack,
    /// The two The Call of the Pack brings for its time.
    Call,
}

/// A packmate as the passive keeps it.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct HoundBook {
    pub kind: Hound,
}

impl Pack {
    /// The pack hounds alive on the books.
    fn pack_alive(&self) -> usize {
        self.hounds.live.iter().filter(|m| m.extra.kind == Hound::Pack).count()
    }

    /// One packmate asked for (`kind`), the `k`-th to come now.
    fn ask_hound(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, here: Pt, kind: Hound, k: usize) {
        let foe = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_champion() && u.is_alive())
            .map(|u| summon::at_of(&u))
            .min_by(|a, b| summon::dist(*a, here).total_cmp(&summon::dist(*b, here)));
        let at = hound_spot(here, foe, k);
        let (effect, life) = if kind == Hound::Pack { ("hound", HOUND_LIFE) } else { ("call", ROAR_T) };
        self.hounds.ask(sim.tick(), life, HoundBook { kind });
        if kind == Hound::Pack {
            self.pending += 1;
        }
        let queued = sim.queue_effect(&format!("{ID}:{effect}"), AttackTypeV1::Skill, me, &at_input(at), 1);
        if !queued {
            make_hound(sim, me, at, life, if kind == Hound::Pack { "her pack" } else { "the call" },
                       "queue_effect refused: spawned by the passive");
        }
        if let Some(k) = tally(sim, "hound ask") {
            wlog(format!("{} HOUND ASK #{k}: {} at {} ({HOUND_SPREAD:.0} behind her){}", head(sim, me),
                         if kind == Hound::Pack { "one of her pack" } else { "one of the call's two" }, summon::pt(at),
                         if queued { "" } else { " - queue_effect REFUSED" }));
        }
    }

    /// No pack hound comes (or none is left): back to the pack drawn on her.
    fn units_off(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        if self.units {
            self.units = false;
            sim.entity_remove_buff(me, SOLO);
            wlog(format!("{} HOUND SOLO OFF: {why} - the pack is drawn on her and bites with her hits as before", head(sim, me)));
        }
    }

    /// The pack's part of a tick: the roar's two, the missing ones, the flock, SOLO.
    fn pack_tick(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize, team: usize, here: Pt) {
        let tick = sim.tick();
        let roar = has_buff(sim, me, PACK4);
        if !KNOBS.off {
            if roar && !self.roared && self.units {
                for k in 0..CALL_N {
                    self.ask_hound(sim, me, team, here, Hound::Call, PACK_N + k);
                }
            }
            if tick >= self.next_ask {
                let have = self.pack_alive() + self.pending;
                for k in have..PACK_N {
                    self.ask_hound(sim, me, team, here, Hound::Pack, k);
                }
                self.next_ask = tick + ASK_EVERY;
            }
        } else if tick >= self.next_ask && self.spawns <= 1 {
            self.next_ask = usize::MAX;
            if let Some(k) = tally(sim, "hound off") {
                wlog(format!("{} HOUND OFF #{k}: unit=off in the test knobs - the pack is drawn on her as before", head(sim, me)));
            }
        }
        self.roared = roar;
        for ev in self.hounds.tick(sim, me, team, player, Some(here)) {
            match ev {
                Event::NoUnit { asked, what } => {
                    if what.kind == Hound::Pack {
                        self.pending = self.pending.saturating_sub(1);
                        self.next_ask = self.next_ask.max(tick + HOUND_RESPAWN);
                    }
                    if let Some(k) = tally(sim, "hound none") {
                        wlog(format!("{} HOUND NONE #{k}: no packmate came within {} ticks of the ask at t={asked}", head(sim, me),
                                     summon::FLOCK_WAIT));
                    }
                    if self.pack_alive() == 0 && self.pending == 0 {
                        self.units_off(sim, me, "no packmate came");
                    }
                }
                Event::Look { id, n, line } => {
                    let kind = self.hounds.get(id).map_or(Hound::Pack, |m| m.extra.kind);
                    if kind == Hound::Pack {
                        self.pending = self.pending.saturating_sub(1);
                        if !self.units {
                            self.units = true;
                            wlog(format!("{} HOUND SOLO ON: her packmates are units - her solo frames, no pack bites in the data",
                                         head(sim, me)));
                        }
                    }
                    if let Some(k) = tally(sim, "hound look") {
                        wlog(format!("{} HOUND #{n} LOOK #{k} ({}): {line}", head(sim, me),
                                     if kind == Hound::Pack { "her pack" } else { "the call" }));
                    }
                }
                Event::Lost { id, why, what } => {
                    if what.kind == Hound::Pack {
                        self.pending = self.pending.saturating_sub(1);
                        self.next_ask = self.next_ask.max(tick + HOUND_RESPAWN);
                    }
                    if let Some(k) = tally(sim, "hound lost") {
                        wlog(format!("{} HOUND LOST #{k}: the unit #{id} spawn_unit named never read as one in {} ticks ({why})",
                                     head(sim, me), summon::FLOCK_LOOKS));
                    }
                    if self.pack_alive() == 0 && self.pending == 0 {
                        self.units_off(sim, me, "the packmate never read as a unit");
                    }
                }
                Event::Line { n, line, .. } => {
                    if let Some(k) = tally(sim, "hound unit") {
                        wlog(format!("{} HOUND #{n} #{k}: {line}", head(sim, me)));
                    }
                }
                Event::Over { member, end } => {
                    let n = member.unit.n;
                    let pack = member.extra.kind == Hound::Pack;
                    let back = if !pack {
                        String::new()
                    } else if end.fate == summon::Fate::Killed {
                        self.next_ask = self.next_ask.max(tick + HOUND_RESPAWN);
                        format!(" - another comes in {HOUND_RESPAWN} ticks")
                    } else {
                        self.next_ask = tick;
                        " - another takes its place now".to_string()
                    };
                    if let Some(k) = tally(sim, "hound over") {
                        wlog(format!("{} HOUND #{n} OVER #{k} ({}): {}{back}", head(sim, me),
                                     if pack { "her pack" } else { "the call" }, end.text));
                    }
                    if pack && end.age <= LOST_AGE && self.pack_alive() == 0 && self.pending == 0 {
                        self.units_off(sim, me, &format!("the packmate was gone {} ticks after it was asked for", end.age));
                    }
                }
                Event::LetGo { member } => {
                    if let Some(k) = tally(sim, "hound let go") {
                        wlog(format!("{} HOUND #{} LET GO #{k}: {HOUND_CAP} packmates on the books - the unit #{} is out there, no \
                                      longer watched", head(sim, me), member.unit.n, member.unit.id));
                    }
                }
                Event::Wake { n, line } => {
                    if let Some(k) = tally(sim, "hound wake") {
                        wlog(format!("{} HOUND #{n} WAKE #{k}: {line}", head(sim, me)));
                    }
                }
            }
        }
        if self.units {
            sim.entity_remove_buff(me, SOLO);
            sim.add_buff(me, &BuffV1::timed(SOLO, SOLO_TICKS));
        }
    }

    /// Her packmates die with her: each banished until its time (no API ends a unit early).
    fn banish_all(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        let ids: Vec<(usize, usize, usize)> = self.hounds.live.iter().map(|m| (m.unit.id, m.unit.n, m.unit.left(tick))).collect();
        if ids.is_empty() {
            return;
        }
        let mut done = Vec::new();
        for (id, n, left) in &ids {
            let alive = sim.get_entity(*id).is_some_and(|e| e.is_alive());
            let ok = alive && sim.entity_banish(me, *id, (*left).max(1), "", "");
            done.push(format!("#{n} (unit #{id}, {left} ticks) {}", if ok { "banished" } else if alive { "REFUSED" } else { "gone" }));
        }
        if let Some(k) = tally(sim, "hound banish") {
            wlog(format!("{} HOUND BANISH #{k}: Naafiri died - her packmates go with her: {}", head(sim, me), done.join(", ")));
        }
    }

    /// Everything of her packmates off the books (she died or a new life began).
    fn let_go(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        let gone = self.hounds.orphans();
        self.pending = 0;
        if self.units {
            self.units = false;
            sim.entity_remove_buff(me, SOLO);
        }
        if !gone.is_empty() {
            if let Some(k) = tally(sim, "hound orphan") {
                wlog(format!("{} HOUND ORPHAN #{k}: {why} - {} packmates off the books", head(sim, me), gone.len()));
            }
        }
    }

    /// A line for a hook that fired while packmates of hers are out.
    fn hooked(&self, sim: &StableSim<'_>, hook: &str, entity: usize, other: usize, damage: Option<usize>) {
        if self.hounds.live.is_empty() {
            return;
        }
        let who = match self.hounds.get(entity) {
            Some(m) => format!("the packmate #{}", m.unit.n),
            None if entity == self.me => "Naafiri".to_string(),
            None => "neither Naafiri nor a packmate of hers".to_string(),
        };
        if let Some(k) = tally(sim, "hound hook") {
            wlog(format!("{} HOUND HOOK #{k} {hook}: entity #{entity} ({who}) -> #{other}{}", head(sim, self.me),
                         damage.map(|d| format!(", damage {d}")).unwrap_or_default()));
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
        "=== {ID} v{VERSION} (Naafiri: the second dagger's execute, the pounce again on every takedown, a smart ult, four hounds in the roar, \
         the packmates units of their own) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "HOUNDS: her packmates are units ('{}', spawn_unit) - {}; {PACK_N} for {HOUND_LIFE} ticks at a time ({} + {}% of her attack a \
         bite, {HOUND_HP_PCT}% of her health), back {HOUND_RESPAWN} ticks after one is killed, {CALL_N} more in the roar; her solo_* \
         frames while they are units. Test knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(PACKMATE), if KNOBS.off { "OFF by the test knobs: the pack is drawn on her as before" } else { "ON" },
        HOUND_HIT, HOUND_HIT_AD, LOG_PATH.with_extension("cfg").display(), KNOBS.shown()
    ));
    module.add_native_passive(format!("{ID}:pack"), Pack::default());
    module.add_native_effect(format!("{ID}:q2"), Q2);
    module.add_native_effect(format!("{ID}:hound"), HoundFx);
    module.add_native_effect(format!("{ID}:call"), CallFx);
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
#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

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

    // ---- 0.2.0: the packmates as units ----

    #[test]
    fn the_packmates_are_built_from_her_numbers() {
        let hers = StatV1 { attack: 200, magic_power: 0, hp: 900, defence: 60, magic_resistance: 40, move_speed: 1150, hp_regen: 3,
                            stack: 0, crit_chance: 0 };
        let s = packmate_spec(&hers, 2000, HOUND_LIFE);
        assert_eq!((s.name.as_str(), s.life), ("league_naafiri_packmate", 3600));
        assert_eq!(s.stat, StatV1 { attack: 200, magic_power: 0, hp: 260, defence: 18, magic_resistance: 12, move_speed: 1150,
                                    hp_regen: 0, stack: 0, crit_chance: 0 });
        // a bite: 4 + 6 % of 200 = 16, at her pace; two of them: the riding pack's 8 + 12 % on each of her attacks
        let a = s.attack;
        assert_eq!(a.attack + s.stat.attack * a.attack_ratio / 100, 16);
        assert_eq!(2 * HOUND_HIT, PK_DMG);
        assert_eq!(2 * HOUND_HIT_AD, PK_RATIO);
        assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (23_000, 58, 25, 10));
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        assert_eq!(packmate_spec(&StatV1::default(), 0, 1).stat.hp, 1);
        for name in [SOLO, &summon::handoff(H_UID, usize::MAX)] {
            assert!(name.starts_with("league_naafiri_") && name.len() <= BUFF_NAME_CAP, "{name}");
        }
    }

    #[test]
    fn the_pack_comes_out_behind_her() {
        let here = (300_000.0, 300_000.0);
        // the enemy east of her: both west of her, one each side of the line
        let (a, b) = (hound_spot(here, Some((400_000.0, 300_000.0)), 0), hound_spot(here, Some((400_000.0, 300_000.0)), 1));
        for p in [a, b] {
            assert!((summon::dist(p, here) - HOUND_SPREAD).abs() < 1.0);
            assert!(p.0 < here.0, "{p:?} not behind her");
        }
        assert!((a.1 - here.1) * (b.1 - here.1) < 0.0, "both on one side");
        assert!(hound_spot((5_000.0, 5_000.0), Some((90_000.0, 5_000.0)), 0).0 >= 0.0);
    }

    #[test]
    fn the_copy_leaves_the_pack_drawn_on_her_behind_solo() {
        let copy = include_str!("../override/league_naafiri.data_champion");
        // every pack bite pair (the attack's three, Q's, E's, the ult's four) and the riding pack of Q (and the ult's two)
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{SOLO}\"")).count(), 9 * 2 + 3);
    }

    // ---- the packmates on the mock world (summon_mock.rs: our guess of the host, to check this side's logic) ----

    use super::mock::{champion, MPlayer, World};

    const GAREN: usize = 1;

    fn log_file() -> std::path::PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_naafiri_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_NAAFIRI_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// Naafiri #0 (team 0, attack 200, 2000 health) at (300000, 300000); Garen #1 60000 east of her; two more far off (the
    /// field round them all); a player each for the champions.
    fn world() -> (World, Pack) {
        log_file();
        let mut w = World::default();
        let mut naafiri = champion("league_naafiri", 0, 300_000.0, 300_000.0);
        (naafiri.hp, naafiri.max, naafiri.stat.attack) = (2000, 2000, 200);
        let mut garen = champion("league_garen", 1, 360_000.0, 300_000.0);
        (garen.hp, garen.max) = (50_000, 50_000);
        w.units = vec![naafiri, garen, champion("league_darius", 1, 600_000.0, 600_000.0), champion("league_ahri", 0, 100_000.0, 100_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() }];
        let mut me = Pack::default();
        w.sim(|sim| me.on_spawn(sim, 0, 0));
        (w, me)
    }

    fn tick(w: &mut World, me: &mut Pack) {
        for (name, caster, input) in w.due() {
            w.sim(|sim| match name.as_str() {
                "league_naafiri:hound" => HoundFx.apply(sim, 0, caster, input),
                "league_naafiri:call" => CallFx.apply(sim, 0, caster, input),
                other => panic!("an effect nobody registered: {other}"),
            });
        }
        if w.units[0].hp > 0 {
            w.sim(|sim| me.on_update(sim, 0, 0, 0));
        }
        w.step();
    }

    fn run(w: &mut World, me: &mut Pack, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    fn hounds(w: &World) -> Vec<usize> {
        w.spawns.iter().filter(|s| s.name == PACKMATE).filter_map(|s| s.gave).collect()
    }

    #[test]
    fn her_pack_comes_with_her_bites_and_comes_back() {
        let (mut w, mut me) = world();
        run(&mut w, &mut me, 4);
        let ids = hounds(&w);
        assert_eq!(ids.len(), PACK_N);
        assert!(w.spawns.iter().all(|s| s.life as usize == HOUND_LIFE && s.summoner == 0 && s.team == 0));
        assert!(w.spawns.iter().all(|s| (s.at.0 as f64) < 300_000.0), "the pack comes out behind her");
        assert!(w.has(0, SOLO) && me.units);
        // they bite Garen: 4 + 6 % of 200 = 16
        run(&mut w, &mut me, 200);
        for id in &ids {
            let bites = w.dealt(*id, DamageTypeV1::Ad);
            assert!(!bites.is_empty() && bites.iter().all(|b| *b == (GAREN, 16)), "{bites:?}");
        }
        // one killed: SOLO stays, another comes HOUND_RESPAWN ticks later
        w.hurt(ids[0], 1_000_000);
        run(&mut w, &mut me, HOUND_RESPAWN - 10);
        assert_eq!(hounds(&w).len(), PACK_N);
        assert!(w.has(0, SOLO));
        run(&mut w, &mut me, 20 + ASK_EVERY);
        assert_eq!(hounds(&w).len(), PACK_N + 1);
        assert_eq!(me.pack_alive(), PACK_N);
    }

    #[test]
    fn the_roar_brings_two_more_for_its_time() {
        let (mut w, mut me) = world();
        run(&mut w, &mut me, 10);
        w.units[0].buffs.push((BuffV1::timed(PACK4, ROAR_T), ROAR_T));
        run(&mut w, &mut me, 5);
        let call: Vec<_> = w.spawns.iter().filter(|s| s.life as usize == ROAR_T).collect();
        assert_eq!(call.len(), CALL_N);
        assert_eq!(me.hounds.live.len(), PACK_N + CALL_N);
        run(&mut w, &mut me, ROAR_T + 10);
        assert_eq!(me.pack_alive(), PACK_N);
        assert_eq!(me.hounds.live.len(), PACK_N, "the call's two outlived the roar");
    }

    #[test]
    fn her_pack_dies_with_her_and_a_new_one_comes_with_her_next_life() {
        let (mut w, mut me) = world();
        run(&mut w, &mut me, 10);
        let ids = hounds(&w);
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.on_dead(sim, 0));
        assert_eq!(w.banishes.len(), PACK_N);
        assert!(w.banishes.iter().all(|b| ids.contains(&b.2) && b.1 == 0 && b.3 > HOUND_LIFE - 20));
        assert!(me.hounds.is_empty() && !me.units);
        // banished: they do nothing and nobody hits them
        let before = w.damage.len();
        run(&mut w, &mut me, 100);
        assert_eq!(w.damage.len(), before);
        // her next life: a new champion entity, a new pack
        let mut again = champion("league_naafiri", 0, 100_000.0, 300_000.0);
        (again.hp, again.max) = (2000, 2000);
        w.units.push(again);
        let me2 = w.units.len() - 1;
        w.players[0].champion = me2;
        w.sim(|sim| me.on_spawn(sim, 0, me2));
        for _ in 0..4 {
            for (name, caster, input) in w.due() {
                w.sim(|sim| match name.as_str() {
                    "league_naafiri:hound" => HoundFx.apply(sim, 0, caster, input),
                    _ => CallFx.apply(sim, 0, caster, input),
                });
            }
            w.sim(|sim| me.on_update(sim, 0, 0, me2));
            w.step();
        }
        assert_eq!(hounds(&w).len(), 2 * PACK_N);
        assert!(w.has(me2, SOLO));
    }

    #[test]
    fn no_unit_from_the_host_keeps_the_pack_drawn_on_her() {
        for case in 0..3 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                _ => w.spawn_never = true,
            }
            run(&mut w, &mut me, 20);
            assert!(!w.has(0, SOLO) && !me.units, "case {case}: SOLO without packmates");
            // and it does not ask again every tick
            let asked = w.spawns.len();
            run(&mut w, &mut me, 200);
            assert_eq!(w.spawns.len(), asked, "case {case}");
        }
    }

    #[test]
    fn the_log_tells_the_packs_whole_lives() {
        let (mut w, mut me) = world();
        run(&mut w, &mut me, 100);
        let ids = hounds(&w);
        let mut dealt = 16;
        w.sim(|sim| me.on_attack(sim, 0, ids[0], GAREN, &mut dealt));
        w.players[1].gold += 3;
        w.hurt(ids[1], 1_000_000);
        run(&mut w, &mut me, 100);
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.on_dead(sim, 0));
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" HOUND")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "HOUND ASK #", "one of her pack at (", "(14000 behind her)",
            "HOUND SPAWN #", "(her pack, the queued effect): unit #4 for team 0 at (", "'league_naafiri_packmate' for 3600 ticks, attack \
             200 ap 0 hp 260 def 6 mr 6 speed 1100; hits 4 + 6% of its attack, range 23000, every 58 ticks (25 long, lands at 10)",
            "HOUND SOLO ON: her packmates are units", "HOUND #1 LOOK #", "(her pack): #4 reads back as name 'league_naafiri_packmate'",
            " of 3600 ticks, at (", "near it: champion #1 league_garen",
            "HOUND HOOK #", "on_attack: entity #4 (the packmate #1) -> #1, damage 16",
            "OVER #", "KILLED after ", "p1 gold +3", "another comes in 900 ticks",
            "HOUND BANISH #", "Naafiri died - her packmates go with her: #1 (unit #4, ", " banished",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
        assert!(mine.iter().map(|l| l.len()).max().unwrap() < 700);
    }
}
