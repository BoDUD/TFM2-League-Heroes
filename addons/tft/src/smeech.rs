//! 史密奇（`tft_smeech`）数据做不到的部分（金铲铲第 13 赛季的炼金男爵 / 伏击专家，技能按用户选的方案 A「废铁伏击手」，
//! 2026-10-29）。他的数据（tools/kit/build_smeech.py）的 `passive` 是这里的 `tft_smeech:ambush`，参数从数据的
//! `passive.params` 来（build_smeech.py 从参数表 P 写进去，`NATIVE_KEYS`），按他的单位编号记一份给效果用：
//!
//! - **伏击**：暴击率在他的属性里（普攻按引擎的规矩暴击，2 倍）；技能的每一下由这里按他的暴击率掷骰（用效果给的
//!   确定性种子，预演和观战一样），暴击造成 200 + `p_cdmg`%，亮 `p_hit`、放暴击音效。
//! - **废铁黑客**（`tft_smeech:hack`：技能起跳后）：`q_range` 以内**血最少**的敌人（先英雄，再小兵野怪；都没有就用
//!   AI 选的目标），把他放到目标身前 `q_gap` 处（朝他原来的方向），之后 `q_s1` / `q_s2` / `q_s3` 拍各斩一下
//!   （`tft_smeech:slash1`..`3`），每下 `q_dmg` + 攻击 `q_ad`%。目标被斩死就再跳一次（`q_again` 记号，每次施法一次），
//!   新目标的三下各打 `q_again`%（`q_weak` 记号）。
//! - **拆解**（`tft_smeech:rip`）：`e_dmg` + 攻击 `e_ad`%，能暴击；撕护甲是数据的。
//! - **废铁狂潮**（`tft_smeech:hop`：数据每跳一次调用一次）：他 `r_reach` 以内这次大招还没打过的敌人（`r_mark`
//!   记号，`r_dur` 拍），先英雄、再血最少，落到身前，`r_dmg` + 攻击 `r_ad`%，自己叠一层 `r_crit` 暴击率
//!   （`r_crit`，`r_t` 拍，每层单独计时）。没有能跳的就不动。
//!
//! 所有记号都挂在单位身上（不存静态表），预演和观战两个模拟同时跑也互不干扰。只有单元测试（经典 SDK 跑不了原生代码），
//! 要在游戏里看日志。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_smeech.log`，每次启动游戏重写，上一次的
//! 留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_smeech";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const SLASH_FX: [&str; 3] = ["tft_smeech:slash1", "tft_smeech:slash2", "tft_smeech:slash3"];
/// The sounds tft.dll plays itself (the tft pack's sound_info; the rest the data plays).
const SFX_LAND: &str = "tft_smeech_q_land";
const SFX_SLASH: &str = "tft_smeech_q_hit";
const SFX_HOP_HIT: &str = "tft_smeech_r_hit";
const SFX_CRIT: &str = "tft_smeech_p_hit";

fn sm(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_SMEECH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_smeech.log");
        }
    }
    PathBuf::from("tft_smeech.log")
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
    /// 伏击：技能暴击造成 200 + p_cdmg %。
    pub p_cdmg: usize,
    /// 废铁黑客：q_range 以内血最少的敌人，落在它身前 q_gap，q_s1/q_s2/q_s3 拍后各斩 q_dmg + 攻击 q_ad%，重跳打 q_again%。
    pub q_range: usize,
    pub q_gap: usize,
    pub q_s1: usize,
    pub q_s2: usize,
    pub q_s3: usize,
    pub q_dmg: usize,
    pub q_ad: usize,
    pub q_again: usize,
    /// 拆解：e_dmg + 攻击 e_ad%。
    pub e_dmg: usize,
    pub e_ad: usize,
    /// 废铁狂潮：r_dur 拍内 r_reach 以内没打过的敌人，r_dmg + 攻击 r_ad%，每跳 +r_crit 暴击率 r_t 拍。
    pub r_dur: usize,
    pub r_reach: usize,
    pub r_dmg: usize,
    pub r_ad: usize,
    pub r_crit: usize,
    pub r_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_cdmg: 20,
            q_range: 45000,
            q_gap: 14000,
            q_s1: 8,
            q_s2: 16,
            q_s3: 24,
            q_dmg: 20,
            q_ad: 55,
            q_again: 70,
            e_dmg: 40,
            e_ad: 90,
            r_dur: 72,
            r_reach: 45000,
            r_dmg: 50,
            r_ad: 80,
            r_crit: 10,
            r_t: 300,
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
            "p_cdmg" => p.p_cdmg = u,
            "q_range" => p.q_range = u,
            "q_gap" => p.q_gap = u,
            "q_s1" => p.q_s1 = u.max(1),
            "q_s2" => p.q_s2 = u.max(1),
            "q_s3" => p.q_s3 = u.max(1),
            "q_dmg" => p.q_dmg = u,
            "q_ad" => p.q_ad = u,
            "q_again" => p.q_again = u,
            "e_dmg" => p.e_dmg = u,
            "e_ad" => p.e_ad = u,
            "r_dur" => p.r_dur = u.max(1),
            "r_reach" => p.r_reach = u,
            "r_dmg" => p.r_dmg = u,
            "r_ad" => p.r_ad = u,
            "r_crit" => p.r_crit = u,
            "r_t" => p.r_t = u,
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

/// Where he lands: `gap` short of the target on the line from where he stands (on it when he stands on it).
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

/// A hit before armour: dmg + ratio% AD, at `pct`% (the re-leap), x (200 + cdmg)% on a crit.
pub fn hit(dmg: usize, ratio: usize, attack: usize, pct: usize, crit: bool, cdmg: usize) -> usize {
    let base = (dmg + attack * ratio / 100) * pct / 100;
    if crit { base * (200 + cdmg) / 100 } else { base }
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

/// His enemies he can leap at: alive, targetable, not a tower or a nexus, not carrying `skip`.
fn foes(sim: &StableSim<'_>, me: usize, skip: Option<&str>) -> Vec<Foe> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .filter(|u| skip.map_or(true, |s| !(0..).map_while(|i| u.buff_at(i)).any(|b| b.name() == s)))
        .map(|u| (u.id(), u.pos(), u.hp().0, u.is_champion()))
        .collect()
}

fn unit(input: &InputTargetV1) -> Option<usize> {
    (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
}

fn alive(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| e.is_alive())
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    let Some(e) = sim.get_entity(id) else { return false };
    (0..).map_while(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// A named buff put on fresh (the old one taken off first, so it never stacks).
fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

/// Him onto `target`: `gap` short of it on his side. Returns false when either is gone.
fn land(sim: &mut StableSim<'_>, me: usize, target: usize, gap: usize) -> bool {
    let (Some(from), Some(at)) = (sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()),
                                  sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.pos())) else {
        return false;
    };
    let to = beside(at, from, gap as u64);
    sim.entity_set_pos(me, to.0, to.1);
    true
}

/// One of his skill hits on `target`: rolled against his crit chance (Ambusher), dealt as a skill's physical damage.
/// Returns (damage, crit, killed).
fn strike(sim: &mut StableSim<'_>, seed: u64, me: usize, target: usize, dmg: usize, ratio: usize, pct: usize)
          -> (usize, bool, bool) {
    let p = params_of(me);
    let stat = sim.get_entity(me).map(|e| e.stat()).unwrap_or_default();
    let crit = rolls_crit(seed, (me as u64) << 32 | target as u64, stat.crit_chance);
    let amount = hit(dmg, ratio, stat.attack, pct, crit, p.p_cdmg);
    sim.deal_damage_typed(me, target, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
    if crit {
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&sm("p_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_CRIT, me, &on);
    }
    (amount, crit, !alive(sim, target))
}

// ===================== 被动：伏击 =====================

/// Records his params for the effects (the crits themselves are rolled where his skills hit).
#[derive(Clone, Default)]
struct Ambush {
    p: Params,
}

impl StablePassive for Ambush {
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
            wlog(format!("{} SPAWN #{k}: tft.dll's Smeech (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, _: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
    }
}

// ===================== 废铁黑客 =====================

/// The leap lands: the weakest enemy in reach (else the AI's target), him beside it, three slashes queued.
fn leap(sim: &mut StableSim<'_>, me: usize, fallback: Option<usize>, again: bool) -> Option<usize> {
    let p = params_of(me);
    let at = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos())?;
    let target = weakest(&foes(sim, me, None), at, p.q_range as u64).or(fallback.filter(|&id| alive(sim, id)))?;
    if !land(sim, me, target, p.q_gap) {
        return None;
    }
    let on_me = InputTargetV1::target(me);
    sim.play_view_effect(&sm("q_land"), me, &on_me, 0, 0, 0);
    sim.play_sfx(SFX_LAND, me, &on_me);
    let on = InputTargetV1::target(target);
    for (fx, at) in SLASH_FX.iter().zip([p.q_s1, p.q_s2, p.q_s3]) {
        sim.queue_effect(fx, AttackTypeV1::Skill, me, &on, at);
    }
    if let Some(k) = counted(if again { "releap" } else { "leap" }) {
        wlog(format!("{} {} #{k}: onto {}", head(sim, me), if again { "RE-LEAP" } else { "LEAP" }, name_of(sim, target)));
    }
    Some(target)
}

struct Hack;
impl StableEffectType for Hack {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        // a fresh cast: the re-leap ready again (the marks of the last one long gone; taken off to be sure)
        sim.entity_remove_buff(me, &sm("q_again"));
        sim.entity_remove_buff(me, &sm("q_weak"));
        leap(sim, me, unit(&input), false);
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (3 * hit(p.q_dmg, p.q_ad, caster_stat.attack, 100, false, 0), 0)
    }
}

/// One of the three slashes: on its target while it lives; a kill leaps once more per cast.
struct Slash(usize);
impl StableEffectType for Slash {
    fn apply(&self, sim: &mut StableSim<'_>, seed: u64, me: usize, input: InputTargetV1) {
        let Some(target) = unit(&input) else { return };
        if !alive(sim, me) || !alive(sim, target) {
            return;
        }
        let p = params_of(me);
        let pct = if has(sim, me, &sm("q_weak")) { p.q_again } else { 100 };
        let (amount, crit, killed) = strike(sim, seed.wrapping_add(self.0 as u64), me, target, p.q_dmg, p.q_ad, pct);
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&sm("q_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_SLASH, me, &on);
        if let Some(k) = counted("slash") {
            wlog(format!("{} SLASH{} #{k}: {} takes {amount}{}{}", head(sim, me), self.0 + 1, name_of(sim, target),
                         if crit { " (crit)" } else { "" }, if killed { ", killed" } else { "" }));
        }
        if killed && !has(sim, me, &sm("q_again")) {
            let t = p.q_s3 + 6;
            put(sim, me, &BuffV1::timed(&sm("q_again"), t));
            put(sim, me, &BuffV1::timed(&sm("q_weak"), t));
            leap(sim, me, None, true);
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (hit(p.q_dmg, p.q_ad, caster_stat.attack, 100, false, 0), 0)
    }
}

// ===================== 拆解 =====================

struct Rip;
impl StableEffectType for Rip {
    fn apply(&self, sim: &mut StableSim<'_>, seed: u64, me: usize, input: InputTargetV1) {
        let Some(target) = unit(&input) else { return };
        if !alive(sim, me) || !alive(sim, target) {
            return;
        }
        let p = params_of(me);
        let (amount, crit, _) = strike(sim, seed, me, target, p.e_dmg, p.e_ad, 100);
        if let Some(k) = counted("rip") {
            wlog(format!("{} RIP #{k}: {} takes {amount}{}", head(sim, me), name_of(sim, target),
                         if crit { " (crit)" } else { "" }));
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (hit(p.e_dmg, p.e_ad, caster_stat.attack, 100, false, 0), 0)
    }
}

// ===================== 废铁狂潮 =====================

/// One hop: the next enemy in reach not hit by this ult (champions first, then the weakest), a strike, a crit stack.
struct Hop;
impl StableEffectType for Hop {
    fn apply(&self, sim: &mut StableSim<'_>, seed: u64, me: usize, _: InputTargetV1) {
        let p = params_of(me);
        let Some(at) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.pos()) else { return };
        let mark = sm("r_mark");
        let Some(target) = weakest(&foes(sim, me, Some(&mark)), at, p.r_reach as u64) else {
            if let Some(k) = counted("hop_none") {
                wlog(format!("{} HOP NONE #{k}: nobody left in reach", head(sim, me)));
            }
            return;
        };
        if !land(sim, me, target, p.q_gap) {
            return;
        }
        put(sim, target, &BuffV1::timed(&mark, p.r_dur));
        let (amount, crit, killed) = strike(sim, seed, me, target, p.r_dmg, p.r_ad, 100);
        let mut stack = BuffV1::timed(&sm("r_crit"), p.r_t);
        stack.crit_chance = p.r_crit as i32;
        sim.add_buff(me, &stack);   // each hop its own stack
        let on = InputTargetV1::target(target);
        sim.play_view_effect(&sm("r_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_HOP_HIT, me, &on);
        if let Some(k) = counted("hop") {
            wlog(format!("{} HOP #{k}: {} takes {amount}{}{}", head(sim, me), name_of(sim, target),
                         if crit { " (crit)" } else { "" }, if killed { ", killed" } else { "" }));
        }
    }

    fn expected_damage(&self, caster_stat: &StatV1) -> (usize, usize) {
        let p = Params::default();
        (hit(p.r_dmg, p.r_ad, caster_stat.attack, 100, false, 0), 0)
    }
}

// ===================== 注册 =====================

/// Smeech's passive and effects, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Smeech: Ambusher's skill crits, Scrap Hacker, Scrap Rip, Scrap Frenzy) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:ambush"), Ambush::default());
    module.add_native_effect(format!("{ID}:hack"), Hack);
    module.add_native_effect(format!("{ID}:slash1"), Slash(0));
    module.add_native_effect(format!("{ID}:slash2"), Slash(1));
    module.add_native_effect(format!("{ID}:slash3"), Slash(2));
    module.add_native_effect(format!("{ID}:rip"), Rip);
    module.add_native_effect(format!("{ID}:hop"), Hop);
    host.log(LogLevel::Info, "tft.dll: Smeech (Ambusher, Scrap Hacker, Scrap Rip, Scrap Frenzy).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"e_ad":90,"e_dmg":40,"p_cdmg":20,"q_ad":55,"q_again":70,"q_dmg":20,"q_gap":14000,"q_range":45000,"q_s1":8,"q_s2":16,"q_s3":24,"r_ad":80,"r_crit":10,"r_dmg":50,"r_dur":72,"r_reach":45000,"r_t":300}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn slash_names_match_the_registry() {
        assert_eq!(SLASH_FX.map(|s| s.to_string()), ["slash1", "slash2", "slash3"].map(|s| format!("{ID}:{s}")));
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
    fn lands_short_of_the_target_on_his_side() {
        assert_eq!(beside((100_000, 100_000), (150_000, 100_000), 14_000), (114_000, 100_000));
        assert_eq!(beside((100_000, 100_000), (105_000, 100_000), 14_000), (105_000, 100_000));
        assert_eq!(beside((100_000, 100_000), (100_000, 100_000), 14_000), (100_000, 100_000));
    }

    #[test]
    fn hits_and_crits() {
        assert_eq!(hit(20, 55, 100, 100, false, 20), 75);
        assert_eq!(hit(20, 55, 100, 70, false, 20), 52);
        assert_eq!(hit(20, 55, 100, 100, true, 20), 165);
        assert!(rolls_crit(7, 1, 100));
        assert!(!rolls_crit(7, 1, 0));
        let crits = (0..10_000u64).filter(|&s| rolls_crit(s, 3, 25)).count();
        assert!((2_300..2_700).contains(&crits), "{crits}");
    }
}
