//! 暗影狼（`tft_murkwolf`）数据做不到的部分（金铲铲第 18 赛季的峡谷野怪 / 狂战士，双头狼，技能按用户选的方案 A
//! 「撕裂之爪」，打野，2026-11-01）。它的数据（tools/kit/build_murkwolf.py）的 `passive` 是这里的
//! `tft_murkwolf:gray`，参数从数据的 `passive.params` 来（build_murkwolf.py 从参数表 P 写进去，`NATIVE_KEYS`），按单位
//! 编号记一份给效果用：
//!
//! - **灰霸符**：基础暴击率在它的属性里（普攻按引擎的规矩暴击）；每 `CHECK` 拍按已损失生命值给它一层 `p_gray`
//!   （暴击率 + `p_bonus` x 已损失生命%）。技能的每一下由这里按它的暴击率掷骰（用效果给的确定性种子，预演和观战
//!   一样），暴击造成 200 + `p_cdmg`%，亮 `p_hit`、放暴击音效。
//! - **撕裂之爪**（`tft_murkwolf:rend`：起跳后）：`q_range` 以内**血最少**的敌人（先英雄，再小兵野怪；都没有就用 AI
//!   选的目标），把它放到目标身前 `q_gap` 处，撕一下 `q_dmg` + 攻击 `q_ad`%（能暴击）。之后 `q_n` 次攻击（数据的
//!   `q_emp` 加攻速）每次多打 `q_emp_dmg` + 攻击 `q_emp_ad`%（`tft_murkwolf:bite`，能暴击），用 `q_n1` 记号计数，
//!   满了摘掉 `q_emp`。
//! - **狂战士之嚎**：`e_howl` 在身上时它的每一下（普攻、技能、小狼）多 `e_amp`%，对生命低于 `e_line`% 的单位翻倍
//!   （`on_attack`）；吸血是数据的。
//! - **狼群攻击**：施法时两只小狼扑向目标（`tft_murkwolf:pounce`，`r_leap_dmg` + 攻击 `r_leap_ad`%）；`r_pups` 在身上
//!   时它每次攻击，小狼咬同一个敌人 `r_n` 口，间隔 `r_gap` 拍（`tft_murkwolf:pup`，每口 `r_dmg` + 攻击 `r_ad`%）。
//!   两只小狼**面向敌人**（用户 2026-11-01：「召唤出来的小狼应该面向敌人 参考沙皇怎么做的」）：特效图不会跟着单位翻转，
//!   所以小狼是两张大表图 `r_pack_r`（都朝右）和 `r_pack_l`（都朝左），这里每 `PUP_CHECK` 拍看最近的敌人在哪边
//!   （左右差不到 `FACE_DX` 就不转，league_azir 的士兵的规矩），挂上那一边的、摘掉另一边的，时长是 `r_pups` 剩下的；
//!   它每次攻击和小狼扑上去时朝被咬的人重新挂一次，动画从缩身扑咬开始，和小狼的咬对上。
//!
//! 所有记号都挂在单位身上（不存静态表），预演和观战两个模拟同时跑也互不干扰。只有单元测试（经典 SDK 跑不了原生代码），
//! 要在游戏里看日志。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_murkwolf.log`，每次启动游戏重写，上一次的
//! 留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_murkwolf";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const PUP_FX: &str = "tft_murkwolf:pup";
/// How often Gray Buff's crit is matched to its missing health (ticks).
const CHECK: usize = 15;
/// How often the pups are turned toward the nearest enemy (ticks).
const PUP_CHECK: usize = 6;
/// An enemy less than this to the side is straight above or below: the pups keep facing the way they face.
const FACE_DX: u64 = 2_000;

fn mw(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_MURKWOLF_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_murkwolf.log");
        }
    }
    PathBuf::from("tft_murkwolf.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
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

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;
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
        _ => "unknown",
    };
    format!("[{kind} t={}] #{id}", sim.tick())
}

fn name_of(sim: &StableSim<'_>, id: usize) -> String {
    sim.get_entity(id).and_then(|e| e.name()).map_or_else(|| format!("#{id}"), |n| format!("{n} #{id}"))
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 灰霸符：暴击率最多再加 p_bonus（按已损失生命%）；技能暴击造成 200 + p_cdmg %。
    pub p_bonus: usize,
    pub p_cdmg: usize,
    /// 撕裂之爪：q_range 以内血最少的敌人，落在它身前 q_gap，撕 q_dmg + 攻击 q_ad%；之后 q_n 次攻击各多 q_emp_dmg + 攻击 q_emp_ad%。
    pub q_range: usize,
    pub q_gap: usize,
    pub q_dmg: usize,
    pub q_ad: usize,
    pub q_n: usize,
    pub q_emp_dmg: usize,
    pub q_emp_ad: usize,
    /// 狂战士之嚎：多 e_amp% 伤害，对生命低于 e_line% 的翻倍。
    pub e_amp: usize,
    pub e_line: usize,
    /// 狼群攻击：扑击 r_leap_dmg + 攻击 r_leap_ad%；每次攻击小狼咬 r_n 口、间隔 r_gap 拍，每口 r_dmg + 攻击 r_ad%。
    pub r_leap_dmg: usize,
    pub r_leap_ad: usize,
    pub r_n: usize,
    pub r_gap: usize,
    pub r_dmg: usize,
    pub r_ad: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_bonus: 30,
            p_cdmg: 0,
            q_range: 45000,
            q_gap: 20000,
            q_dmg: 40,
            q_ad: 110,
            q_n: 3,
            q_emp_dmg: 10,
            q_emp_ad: 30,
            e_amp: 15,
            e_line: 50,
            r_leap_dmg: 40,
            r_leap_ad: 60,
            r_n: 2,
            r_gap: 4,
            r_dmg: 12,
            r_ad: 25,
        }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    for part in json.trim().trim_start_matches('{').trim_end_matches('}').split(',') {
        let mut kv = part.splitn(2, ':');
        let (Some(k), Some(v)) = (kv.next(), kv.next()) else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        let u = v.max(0) as usize;
        match k {
            "p_bonus" => p.p_bonus = u,
            "p_cdmg" => p.p_cdmg = u,
            "q_range" => p.q_range = u,
            "q_gap" => p.q_gap = u,
            "q_dmg" => p.q_dmg = u,
            "q_ad" => p.q_ad = u,
            "q_n" => p.q_n = u.max(1),
            "q_emp_dmg" => p.q_emp_dmg = u,
            "q_emp_ad" => p.q_emp_ad = u,
            "e_amp" => p.e_amp = u,
            "e_line" => p.e_line = u,
            "r_leap_dmg" => p.r_leap_dmg = u,
            "r_leap_ad" => p.r_leap_ad = u,
            "r_n" => p.r_n = u,
            "r_gap" => p.r_gap = u.max(1),
            "r_dmg" => p.r_dmg = u,
            "r_ad" => p.r_ad = u,
            _ => {}
        }
    }
    p
}

static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

// ===================== 规则（单元测试用） =====================

/// (id, position, current health, is a champion)
pub type Foe = (usize, (u64, u64), usize, bool);

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// The prey: within `reach` of `at`, champions first, then the lowest health, then the nearer, then the lower id.
pub fn weakest(foes: &[Foe], at: (u64, u64), reach: u64) -> Option<usize> {
    let r2 = (reach as u128) * (reach as u128);
    foes.iter()
        .filter(|f| dist_sq(f.1, at) <= r2)
        .min_by_key(|f| (!f.3, f.2, dist_sq(f.1, at), f.0))
        .map(|f| f.0)
}

/// Where it lands: `gap` short of the target on the line from where it stands (on it when it stands on it).
pub fn beside(target: (u64, u64), from: (u64, u64), gap: u64) -> (u64, u64) {
    let d = (dist_sq(target, from) as f64).sqrt();
    if d < 1.0 {
        return target;
    }
    let k = (gap as f64).min(d) / d;
    let x = target.0 as f64 + (from.0 as f64 - target.0 as f64) * k;
    let y = target.1 as f64 + (from.1 as f64 - target.1 as f64) * k;
    (x.round().max(0.0) as u64, y.round().max(0.0) as u64)
}

/// A hit before armour: dmg + ratio% AD, x (200 + cdmg)% on a crit.
pub fn hit(dmg: usize, ratio: usize, attack: usize, crit: bool, cdmg: usize) -> usize {
    let base = dmg + attack * ratio / 100;
    if crit { base * (200 + cdmg) / 100 } else { base }
}

/// Gray Buff's extra crit chance: `bonus` x the missing share of its health, rounded down.
pub fn gray_bonus(bonus: usize, hp: usize, max: usize) -> usize {
    if max == 0 {
        return 0;
    }
    bonus * max.saturating_sub(hp) / max
}

/// Slayer's Howl: the extra damage % on a unit at `hp` of `max`: `amp`, twice under `line`% health.
pub fn howl_amp(amp: usize, line: usize, hp: usize, max: usize) -> usize {
    if max > 0 && hp * 100 < max * line { 2 * amp } else { amp }
}

/// A crit roll from the effect's deterministic seed: `chance`% (100 or more always crits).
pub fn rolls_crit(seed: u64, salt: u64, chance: usize) -> bool {
    let mut x = seed ^ salt.wrapping_mul(0x9E37_79B9_7F4A_7C15);
    x ^= x >> 33;
    x = x.wrapping_mul(0xFF51_AFD7_ED55_8CCD);
    x ^= x >> 33;
    x = x.wrapping_mul(0xC4CE_B9FE_1A85_EC53);
    x ^= x >> 33;
    ((x % 100) as usize) < chance
}

// ===================== 模拟里的小工具 =====================

/// Its enemies it can leap at: alive, targetable, not a tower or a nexus.
fn foes(sim: &StableSim<'_>, me: usize) -> Vec<Foe> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| (u.id(), u.pos(), u.hp().0, u.is_champion()))
        .collect()
}

fn unit(input: &InputTargetV1) -> Option<usize> {
    (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
}

fn alive(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive())
}

fn count(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    let Some(e) = sim.get_entity(id) else { return 0 };
    (0..).map_while(|i| e.buff_at(i)).filter(|b| b.name() == name).count()
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    count(sim, id, name) > 0
}

/// A named buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

/// It onto `target`: `gap` short of it on its side. Returns false when either is gone.
fn land(sim: &mut StableSim<'_>, me: usize, target: usize, gap: usize) -> bool {
    let (Some(from), Some(at)) = (sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()),
                                  sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.pos())) else {
        return false;
    };
    let to = beside(at, from, gap as u64);
    sim.entity_set_pos(me, to.0, to.1);
    true
}

/// One of its skill hits on `target`: rolled against its crit chance (Gray Buff), dealt as a skill's physical damage
/// (Slayer's Howl adds its share in on_attack). Returns (damage, crit, killed).
fn strike(sim: &mut StableSim<'_>, seed: u64, me: usize, target: usize, dmg: usize, ratio: usize) -> (usize, bool, bool) {
    let p = params_of(me);
    let stat = sim.get_entity(me).map(|e| e.stat()).unwrap_or_default();
    let crit = rolls_crit(seed, (me as u64) << 32 | target as u64, stat.crit_chance);
    let amount = hit(dmg, ratio, stat.attack, crit, p.p_cdmg);
    sim.deal_damage_typed(me, target, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
    if crit {
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&mw("p_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(&mw("p"), me, &on);
    }
    (amount, crit, !alive(sim, target))
}

/// Which way the pups face: toward the enemy at `enemy` unless it is less than FACE_DX to the side of the wolf at `me`
/// (straight above or below), then `keep`.
pub fn pups_right(me: u64, enemy: Option<u64>, keep: bool) -> bool {
    match enemy {
        Some(e) if e.abs_diff(me) >= FACE_DX => e > me,
        _ => keep,
    }
}

fn ticks_left(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    let Some(e) = sim.get_entity(id) else { return 0 };
    (0..).map_while(|i| e.buff_at(i)).filter(|b| b.name() == name).map(|b| b.duration_tick).max().unwrap_or(0)
}

/// The pups' picture toward `toward` (else the nearest enemy) for what is left of `r_pups`: that side's put on (again
/// when `restart`: its loop starts over from the wind-up), the other taken off; both off once `r_pups` is gone.
fn show_pups(sim: &mut StableSim<'_>, me: usize, toward: Option<usize>, restart: bool) {
    let (right_n, left_n) = (mw("r_pack_r"), mw("r_pack_l"));
    let left = ticks_left(sim, me, &mw("r_pups"));
    let (on_r, on_l) = (has(sim, me, &right_n), has(sim, me, &left_n));
    if left == 0 || !alive(sim, me) {
        if on_r || on_l {
            sim.entity_remove_buff(me, &right_n);
            sim.entity_remove_buff(me, &left_n);
        }
        return;
    }
    let Some(at) = sim.get_entity(me).map(|e| e.pos()) else { return };
    let enemy = toward.and_then(|t| sim.get_entity(t)).filter(|e| e.is_alive()).map(|e| e.pos())
        .or_else(|| foes(sim, me).into_iter().min_by_key(|f| dist_sq(f.1, at)).map(|f| f.1));
    let right = pups_right(at.0, enemy.map(|e| e.0), on_r || !on_l);
    let (name, other) = if right { (right_n, left_n) } else { (left_n, right_n) };
    let turned = if right { on_l } else { on_r };
    if turned {
        sim.entity_remove_buff(me, &other);
    }
    if restart || turned || !has(sim, me, &name) {
        put(sim, me, &BuffV1::timed(&name, left));
        if turned {
            if let Some(k) = counted("pups_turn") {
                wlog(format!("{} PUPS TURN #{k}: facing {}", head(sim, me), if right { "right" } else { "left" }));
            }
        }
    }
}

// ===================== 被动：灰霸符（和狂战士之嚎的伤害） =====================

#[derive(Clone, Default)]
struct Gray {
    p: Params,
    /// the crit bonus last put on (to log changes only)
    last: usize,
}

impl StablePassive for Gray {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Murk Wolf (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        if sim.tick() % PUP_CHECK == 0 {
            show_pups(sim, me, None, false);
        }
        if sim.tick() % CHECK != 0 {
            return;
        }
        let Some((hp, max)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        let bonus = gray_bonus(self.p.p_bonus, hp, max);
        if bonus == 0 {
            sim.entity_remove_buff(me, &mw("p_gray"));
        } else {
            let mut b = BuffV1::timed(&mw("p_gray"), CHECK + 5);
            b.crit_chance = bonus as i32;
            put(sim, me, &b);
        }
        if bonus / 10 != self.last / 10 {
            if let Some(k) = counted("gray") {
                wlog(format!("{} GRAY #{k}: hp {hp}/{max}, crit +{bonus}%", head(sim, me)));
            }
        }
        self.last = bonus;
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        // Slayer's Howl: every hit of its own while it howls, twice the share under e_line% health
        if *damage == 0 || !has(sim, me, &mw("e_howl")) {
            return;
        }
        let Some((hp, max)) = sim.get_entity(target).map(|e| e.hp()) else { return };
        let amp = howl_amp(self.p.e_amp, self.p.e_line, hp, max);
        let extra = *damage * amp / 100;
        *damage += extra;
        if amp > self.p.e_amp {
            sim.play_sfx(&mw("e_hit"), me, &InputTargetV1::target(target));
        }
        if let Some(k) = counted(if amp > self.p.e_amp { "howl_low" } else { "howl" }) {
            wlog(format!("{} HOWL #{k}: {} +{amp}% (+{extra})", head(sim, me), name_of(sim, target)));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        // its death howl (the data has no moment for it)
        sim.play_sfx(&mw("d"), me, &InputTargetV1::target(me));
    }
}

// ===================== 撕裂之爪 =====================

/// The leap lands: the weakest enemy in reach (else the AI's target), it beside it, the rend; the empowered attacks'
/// count starts again.
struct Rend;
impl StableEffectType for Rend {
    fn apply(&self, sim: &mut StableSim<'_>, seed: u64, me: usize, input: InputTargetV1) {
        sim.entity_remove_buff(me, &mw("q_n1"));
        let p = params_of(me);
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let fallback = unit(&input).filter(|&id| alive(sim, id));
        let Some(target) = weakest(&foes(sim, me), at, p.q_range as u64).or(fallback) else { return };
        if !land(sim, me, target, p.q_gap) {
            return;
        }
        let on_me = InputTargetV1::target(me);
        sim.play_view_effect(&mw("q_land"), me, &on_me, 0, 0, 0);
        let (amount, crit, killed) = strike(sim, seed, me, target, p.q_dmg, p.q_ad);
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&mw("q_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(&mw("q_hit"), me, &on);
        if let Some(k) = counted("rend") {
            wlog(format!("{} REND #{k}: onto {}, {amount}{}{}", head(sim, me), name_of(sim, target),
                         if crit { " (crit)" } else { "" }, if killed { ", killed" } else { "" }));
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (hit(p.q_dmg, p.q_ad, caster_stat.attack, false, 0), 0)
    }
}

// ===================== 双头撕咬（每次攻击） =====================

/// Every attack: Rending Claws' bonus while `q_emp` lasts (counted, `q_emp` off after q_n), the pups' bites while
/// `r_pups` lasts (the pups turned to the bitten).
struct Bite;
impl StableEffectType for Bite {
    fn apply(&self, sim: &mut StableSim<'_>, seed: u64, me: usize, input: InputTargetV1) {
        let Some(target) = unit(&input) else { return };
        if !alive(sim, me) || !alive(sim, target) {
            return;
        }
        let p = params_of(me);
        let on = InputTargetV1::target(target);
        if has(sim, me, &mw("q_emp")) {
            let (amount, crit, _) = strike(sim, seed, me, target, p.q_emp_dmg, p.q_emp_ad);
            sim.play_sfx(&mw("q_emp"), me, &on);
            let n = count(sim, me, &mw("q_n1")) + 1;
            if n >= p.q_n {
                sim.entity_remove_buff(me, &mw("q_n1"));
                sim.entity_remove_buff(me, &mw("q_emp"));
            } else {
                sim.add_buff(me, &BuffV1::timed(&mw("q_n1"), 600));   // one a bite; q_emp's end clears them with it
            }
            if let Some(k) = counted("claw") {
                wlog(format!("{} CLAW{n} #{k}: {} +{amount}{}", head(sim, me), name_of(sim, target),
                             if crit { " (crit)" } else { "" }));
            }
        } else if has(sim, me, &mw("q_n1")) {
            sim.entity_remove_buff(me, &mw("q_n1"));   // q_emp ran out before q_n attacks
        }
        if has(sim, me, &mw("r_pups")) {
            show_pups(sim, me, Some(target), true);   // the pups turn to the bitten and lunge with their bites
            for i in 0..p.r_n {
                sim.queue_effect(PUP_FX, AttackTypeV1::Skill, me, &on, p.r_gap * (i + 1));
            }
        }
    }

    fn expected_damage(&self, _: &StatV1) -> (usize, usize) {
        (0, 0)
    }
}

// ===================== 狼群攻击 =====================

/// The pups pounce at the ult's target on arrival.
struct Pounce;
impl StableEffectType for Pounce {
    fn apply(&self, sim: &mut StableSim<'_>, seed: u64, me: usize, input: InputTargetV1) {
        let Some(target) = unit(&input) else { return };
        if !alive(sim, me) || !alive(sim, target) {
            return;
        }
        let p = params_of(me);
        show_pups(sim, me, Some(target), true);
        let (amount, crit, killed) = strike(sim, seed, me, target, p.r_leap_dmg, p.r_leap_ad);
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&mw("r_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(&mw("r_bite"), me, &on);
        if let Some(k) = counted("pounce") {
            wlog(format!("{} POUNCE #{k}: {} takes {amount}{}{}", head(sim, me), name_of(sim, target),
                         if crit { " (crit)" } else { "" }, if killed { ", killed" } else { "" }));
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (hit(p.r_leap_dmg, p.r_leap_ad, caster_stat.attack, false, 0), 0)
    }
}

/// One pup's bite on the attacked enemy (no crit: the pups are not Gray Buff's).
struct Pup;
impl StableEffectType for Pup {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(target) = unit(&input) else { return };
        if !alive(sim, me) || !alive(sim, target) {
            return;
        }
        let p = params_of(me);
        let ad = sim.get_entity(me).map_or(0, |e| e.stat().attack);
        let amount = hit(p.r_dmg, p.r_ad, ad, false, 0);
        sim.deal_damage_typed(me, target, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&mw("r_bite"), me, &on, 0, 0, 0);
        sim.play_sfx(&mw("r_bite"), me, &on);
        if let Some(k) = counted("pup") {
            wlog(format!("{} PUP #{k}: {} takes {amount}", head(sim, me), name_of(sim, target)));
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (hit(p.r_dmg, p.r_ad, caster_stat.attack, false, 0), 0)
    }
}

// ===================== 注册 =====================

/// The Murk Wolf's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Murk Wolf: Gray Buff, Rending Claws, Slayer's Howl, Pack Attack) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:gray"), Gray::default());
    module.add_native_effect(format!("{ID}:rend"), Rend);
    module.add_native_effect(format!("{ID}:bite"), Bite);
    module.add_native_effect(format!("{ID}:pounce"), Pounce);
    module.add_native_effect(format!("{ID}:pup"), Pup);
    host.log(LogLevel::Info, "tft.dll: Murk Wolf (Gray Buff, Rending Claws, Slayer's Howl, Pack Attack).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"e_amp":15,"e_line":50,"p_bonus":30,"p_cdmg":0,"q_ad":110,"q_dmg":40,"q_emp_ad":30,"q_emp_dmg":10,"q_gap":20000,"q_n":3,"q_range":45000,"r_ad":25,"r_dmg":12,"r_gap":4,"r_leap_ad":60,"r_leap_dmg":40,"r_n":2}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn pup_name_matches_the_registry() {
        assert_eq!(PUP_FX, format!("{ID}:pup"));
    }

    #[test]
    fn the_pups_face_the_enemy() {
        assert!(pups_right(100_000, Some(130_000), false));     // the enemy to the right: turn right
        assert!(!pups_right(100_000, Some(70_000), true));      // to the left: turn left
        assert!(!pups_right(100_000, Some(101_000), false));    // straight above or below: keep the way they face
        assert!(pups_right(100_000, Some(99_000), true));
        assert!(pups_right(100_000, None, true));               // nobody: keep
    }

    #[test]
    fn the_weakest_champion_first() {
        let at = (100_000, 100_000);
        let foes = [
            (1, (110_000, 100_000), 50, false),    // a camp, nearly dead
            (2, (130_000, 100_000), 900, true),
            (3, (120_000, 100_000), 400, true),    // the weakest champion
            (4, (100_000, 125_000), 400, true),    // as weak, farther
            (5, (200_000, 100_000), 10, true),     // out of reach
        ];
        assert_eq!(weakest(&foes, at, 45_000), Some(3));
        assert_eq!(weakest(&foes[..1], at, 45_000), Some(1));
        assert_eq!(weakest(&foes, at, 5_000), None);
    }

    #[test]
    fn lands_short_of_the_target_on_its_side() {
        assert_eq!(beside((100_000, 100_000), (150_000, 100_000), 20_000), (120_000, 100_000));
        assert_eq!(beside((100_000, 100_000), (105_000, 100_000), 14_000), (105_000, 100_000));
        assert_eq!(beside((100_000, 100_000), (100_000, 100_000), 14_000), (100_000, 100_000));
    }

    #[test]
    fn gray_buff_grows_with_missing_health() {
        assert_eq!(gray_bonus(30, 1000, 1000), 0);
        assert_eq!(gray_bonus(30, 500, 1000), 15);
        assert_eq!(gray_bonus(30, 0, 1000), 30);
        assert_eq!(gray_bonus(30, 10, 0), 0);
    }

    #[test]
    fn the_howl_doubles_under_the_line() {
        assert_eq!(howl_amp(15, 50, 600, 1000), 15);
        assert_eq!(howl_amp(15, 50, 500, 1000), 15);   // at the line: not under it
        assert_eq!(howl_amp(15, 50, 499, 1000), 30);
        assert_eq!(howl_amp(15, 50, 0, 0), 15);
    }

    #[test]
    fn hits_and_crits() {
        assert_eq!(hit(40, 110, 100, false, 0), 150);   // 40 + 110% of 100
        assert_eq!(hit(40, 110, 100, true, 0), 300);
        assert_eq!(hit(12, 25, 100, false, 0), 37);
        assert!(rolls_crit(7, 1, 100));
        assert!(!rolls_crit(7, 1, 0));
        let crits = (0..10_000u64).filter(|&s| rolls_crit(s, 3, 25)).count();
        assert!((2_300..2_700).contains(&crits), "{crits}");
    }
}
