//! 海克斯霸龙（`tft_thex`）数据做不到的部分（金铲铲第 16 赛季的海克斯机甲五费，技能按用户选的方案 A「海克斯军械库」，
//! 上单，2026-11-02）。它的数据（tools/kit/build_thex.py）的 `passive` 是这里的 `tft_thex:pilot`，参数从数据的
//! `passive.params` 来（build_thex.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **驾驶员弹射**：每条命一开始播 `tft_thex_p_in`（驾驶员跳进机甲）。它倒下时机甲爆开（金铲铲「海克斯机甲」的阵亡）：
//!   倒下的地方 `p_r` 以内的每个敌人（不算塔）挨 `p_dmg` + `p_ratio`% 攻击力的物理伤害、被击退（`p_kb` 速度 `p_kb_t`
//!   拍）并晕眩 `p_stun` 拍；播 `tft_thex_p_eject`、`tft_thex_d` 和爆炸的画面 `tft_thex_p_blast`。数据没有阵亡的时机。
//! - **海克斯军械库的激光**（`tft_thex:laser`，大招每一拍）：从它穿过目标、`r_len` 长、`r_w` 宽的一条线上的敌人（不算
//!   塔），离它最近的挨满 `r_dmg` + `r_ratio`% 攻击力的物理伤害，往后每一个少 `r_fall`%，最少 `r_min`%（金铲铲的每穿
//!   一人 -70%、最多 -90%）。数据的线对每个人一样。
//!
//! 加特林弹幕、追踪导弹、霸龙冲撞、大招的护盾和导弹、激光的画面是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_thex.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_thex";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// A unit's body (its collision radius, about): the burst's and the laser's reach count it, as the data's shapes do.
const BODY: u64 = 15000;

fn tx(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_THEX_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_thex.log");
        }
    }
    PathBuf::from("tft_thex.log")
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
    /// 驾驶员弹射：倒下的地方 p_r 以内（加上身子）的敌人。
    pub p_r: usize,
    /// 伤害：p_dmg + p_ratio% 攻击力。
    pub p_dmg: usize,
    pub p_ratio: usize,
    /// 击退：速度 p_kb、p_kb_t 拍；晕眩 p_stun 拍。
    pub p_kb: usize,
    pub p_kb_t: usize,
    pub p_stun: usize,
    /// 激光：从它穿过目标 r_len 长、r_w 宽。
    pub r_len: usize,
    pub r_w: usize,
    /// 伤害：r_dmg + r_ratio% 攻击力，往后每一个少 r_fall%，最少 r_min%。
    pub r_dmg: usize,
    pub r_ratio: usize,
    pub r_fall: usize,
    pub r_min: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_r: 40000,
            p_dmg: 100,
            p_ratio: 100,
            p_kb: 1800,
            p_kb_t: 12,
            p_stun: 90,
            r_len: 90000,
            r_w: 14000,
            r_dmg: 80,
            r_ratio: 130,
            r_fall: 70,
            r_min: 10,
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
            "p_r" => p.p_r = u,
            "p_dmg" => p.p_dmg = u,
            "p_ratio" => p.p_ratio = u,
            "p_kb" => p.p_kb = u,
            "p_kb_t" => p.p_kb_t = u,
            "p_stun" => p.p_stun = u,
            "r_len" => p.r_len = u,
            "r_w" => p.r_w = u,
            "r_dmg" => p.r_dmg = u,
            "r_ratio" => p.r_ratio = u,
            "r_fall" => p.r_fall = u.min(100),
            "r_min" => p.r_min = u.min(100),
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

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// The percentage of the beam the `k`-th enemy along it takes (0 = the nearest): r_fall% less for each one before it,
/// never under r_min%.
pub fn falloff(k: usize, p: &Params) -> usize {
    100usize.saturating_sub(k * p.r_fall).max(p.r_min)
}

/// The full beam: base + ratio% of its attack.
pub fn beam_damage(p: &Params, attack: usize) -> usize {
    p.r_dmg + attack * p.r_ratio / 100
}

/// The burst: base + ratio% of its attack.
pub fn burst_damage(p: &Params, attack: usize) -> usize {
    p.p_dmg + attack * p.p_ratio / 100
}

/// Where along the beam (from `from` toward `to`, `len` long) `at` lies and how far from its middle line: (distance
/// along, squared distance off the line); None behind it or past its end.
pub fn on_beam(from: (u64, u64), to: (u64, u64), len: u64, at: (u64, u64)) -> Option<(f64, f64)> {
    let (dx, dy) = (to.0 as f64 - from.0 as f64, to.1 as f64 - from.1 as f64);
    let d = (dx * dx + dy * dy).sqrt();
    if d < 1.0 {
        return None;
    }
    let (ux, uy) = (dx / d, dy / d);
    let (px, py) = (at.0 as f64 - from.0 as f64, at.1 as f64 - from.1 as f64);
    let along = px * ux + py * uy;
    if along < 0.0 || along > len as f64 + BODY as f64 {
        return None;
    }
    let off = px * uy - py * ux;
    Some((along, off * off))
}

// ===================== 场上 =====================

/// Live, targetable enemies of `team` that are not towers (or the nexus): (id, where).
fn foes(sim: &StableSim<'_>, team: usize) -> Vec<(usize, (u64, u64))> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
        .map(|u| (u.id(), u.pos()))
        .collect()
}

// ===================== 海克斯军械库：激光 =====================

/// One beat's laser: through the action's target, the nearest enemy on it taking the full beam, each next one less.
struct Laser;
impl StableEffectType for Laser {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some((at, team, attack)) =
            sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.pos(), e.team(), e.stat().attack))
        else {
            return;
        };
        let Some(to) = sim.get_entity(input.target_id).map(|e| e.pos()) else { return };
        let p = params_of(me);
        let half = (p.r_w as u64 / 2 + BODY) as f64;
        let mut hit: Vec<(f64, usize)> = foes(sim, team)
            .into_iter()
            .filter_map(|(id, pos)| on_beam(at, to, p.r_len as u64, pos).filter(|(_, off)| *off <= half * half).map(|(a, _)| (a, id)))
            .collect();
        hit.sort_by(|a, b| a.0.total_cmp(&b.0).then(a.1.cmp(&b.1)));
        let full = beam_damage(&p, attack);
        let mut dealt = Vec::new();
        for (k, (_, id)) in hit.iter().enumerate() {
            let dmg = full * falloff(k, &p) / 100;
            sim.deal_damage_typed(me, *id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
            sim.play_view_effect(&tx("r_hit"), me, &InputTargetV1::target(*id), 0, 0, 0);
            dealt.push(dmg);
        }
        if let Some(k) = counted("laser") {
            wlog(format!("{} LASER #{k}: through {}, {} enemies take {:?} (full {full})", head(sim, me),
                         name_of(sim, input.target_id), hit.len(), dealt));
        }
    }
}

// ===================== 被动：驾驶员弹射 =====================

#[derive(Clone, Default)]
struct Pilot {
    /// The champion it belongs to (on_dead is given the player, not the unit).
    me: usize,
    p: Params,
    /// Whether it was alive last tick (a new life: the pilot jumps in).
    was_alive: bool,
    /// Where it was, its team and its attack the last tick it was alive (the burst goes off there).
    last: Option<((u64, u64), usize, usize)>,
}

impl StablePassive for Pilot {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        // a new life is a new unit, and on_update does not run while it is dead: the first tick of this life must
        // see a dead one (Terra's way)
        self.was_alive = false;
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's T-Hex (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        let now = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.pos(), e.team(), e.stat().attack));
        let alive = now.is_some();
        if alive && !self.was_alive {
            // the pilot jumps in
            sim.play_sfx(&tx("p_in"), me, &InputTargetV1::target(me));
            if let Some(k) = counted("pilot") {
                wlog(format!("{} PILOT #{k}: the pilot jumps in", head(sim, me)));
            }
        }
        self.was_alive = alive;
        if now.is_some() {
            self.last = now;
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        let me = self.me;
        let Some((at, team, attack)) = self.last.take() else { return };
        let p = self.p;
        let reach = (p.p_r as u64 + BODY) as u128;
        let hit: Vec<usize> =
            foes(sim, team).into_iter().filter(|(_, pos)| dist_sq(*pos, at) <= reach * reach).map(|(id, _)| id).collect();
        let dmg = burst_damage(&p, attack);
        for id in &hit {
            sim.deal_damage_typed(me, *id, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
            sim.entity_knockback(me, *id, p.p_kb, p.p_kb_t);
            sim.apply_cc(*id, &CcV1::stun(p.p_stun as u64));
        }
        let here = InputTargetV1::pos(at.0, at.1);
        sim.play_view_effect(&tx("p_blast"), me, &here, 0, 0, 0);
        sim.play_sfx(&tx("p_eject"), me, &here);
        sim.play_sfx(&tx("d"), me, &here);
        if let Some(k) = counted("eject") {
            wlog(format!("{} EJECT #{k}: {} bursts at ({}, {}): {} enemies take {dmg}, knocked back, stunned {} ticks",
                         head(sim, me), name_of(sim, me), at.0, at.1, hit.len(), p.p_stun));
        }
    }
}

// ===================== 注册 =====================

/// T-Hex's passive and its ult's laser, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (T-Hex: Pilot Eject, the Hex Armory laser) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:pilot"), Pilot::default());
    module.add_native_effect(format!("{ID}:laser"), Laser);
    host.log(LogLevel::Info, "tft.dll: T-Hex (Pilot Eject, the Hex Armory laser).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_r":40000,"p_dmg":100,"p_ratio":100,"p_kb":1800,"p_kb_t":12,"p_stun":90,"r_len":90000,"r_w":14000,"r_dmg":80,"r_ratio":130,"r_fall":70,"r_min":10}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_beam_falls_off_by_enemy() {
        let p = Params::default();
        assert_eq!(falloff(0, &p), 100);
        assert_eq!(falloff(1, &p), 30);
        assert_eq!(falloff(2, &p), 10);
        assert_eq!(falloff(9, &p), 10);
    }

    #[test]
    fn damage_by_the_numbers() {
        let p = Params::default();
        assert_eq!(beam_damage(&p, 100), 80 + 130);
        assert_eq!(burst_damage(&p, 100), 100 + 100);
    }

    #[test]
    fn the_beam_runs_through_the_target() {
        let (from, to) = ((100000, 100000), (130000, 100000));
        assert!(on_beam(from, to, 90000, (160000, 103000)).is_some_and(|(a, off)| (a - 60000.0).abs() < 1.0 && off == 9e6));
        assert!(on_beam(from, to, 90000, (90000, 100000)).is_none(), "behind it");
        assert!(on_beam(from, to, 90000, (210000, 100000)).is_none(), "past its end");
        assert!(on_beam(from, from, 90000, (120000, 100000)).is_none(), "no direction");
    }
}
