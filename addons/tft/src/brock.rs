//! 岩宝（`tft_brock`）数据做不到的部分（金铲铲第 16 赛季的以绪塔尔五费，技能按用户选的方案 A「震地猛击」，上单，
//! 2026-11-02）。他的数据（tools/kit/build_brock.py）的 `passive` 是这里的 `tft_brock:stone`，参数从数据的
//! `passive.params` 来（build_brock.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **岩心不动**：每条命一开始（和每 `CHECK` 拍看一次，没了就补上）挂上永久的 `tft_brock_p_stone`：免疫控制（金铲铲
//!   原版的被动）。数据没有一条命开始的时机（--plain 的数据从他的第一个动作挂上）。
//! - **震地猛击**（`tft_brock:slam`，大招落地那一下）：`r_r` 以内的每个敌人（不算塔）挨 `r_dmg` + `r_ratio`% 攻击力 +
//!   `r_hp`% 他最大生命的物理伤害，离落点每 `r_hex`（一格）少 `r_fall`%，最少 `r_min`%（金铲铲的每格 -15%、最低 40%）；
//!   **这一场里第一次**被震地猛击砸中的（`r_mark` 拍内没被砸过的：身上没有 `tft_brock_r_mark`）还被击飞 `r_up` 拍、亮
//!   `tft_brock_r_hit`。数据既不会按距离算伤害，也读不到目标身上的标记。
//! - **死亡**：倒下时播 `tft_brock_d`。
//!
//! 震地拳（溅射、每第三下击飞）、巨岩投掷、苔藤缠握、大招的起跳落地和落石是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_brock.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_brock";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// How often (ticks) the passive looks whether the stone heart is still on him.
const CHECK: usize = 30;
/// A unit's body (its collision radius, about): the slam's reach counts it, as the data's circles do.
const BODY: u64 = 15000;

fn bk(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_BROCK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_brock.log");
        }
    }
    PathBuf::from("tft_brock.log")
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
    /// 震地猛击：落地 r_r 以内（加上身子）的敌人。
    pub r_r: usize,
    /// 伤害：r_dmg + r_ratio% 攻击力 + r_hp% 他的最大生命。
    pub r_dmg: usize,
    pub r_ratio: usize,
    pub r_hp: usize,
    /// 离落点每 r_hex 少 r_fall%，最少 r_min%。
    pub r_hex: usize,
    pub r_fall: usize,
    pub r_min: usize,
    /// 第一次被砸中的击飞 r_up 拍；r_mark 拍内再被砸中不再击飞。
    pub r_up: usize,
    pub r_mark: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            r_r: 50000,
            r_dmg: 90,
            r_ratio: 80,
            r_hp: 3,
            r_hex: 18000,
            r_fall: 15,
            r_min: 40,
            r_up: 75,
            r_mark: 3600,
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
            "r_r" => p.r_r = u,
            "r_dmg" => p.r_dmg = u,
            "r_ratio" => p.r_ratio = u,
            "r_hp" => p.r_hp = u,
            "r_hex" => p.r_hex = u.max(1),
            "r_fall" => p.r_fall = u.min(100),
            "r_min" => p.r_min = u.min(100),
            "r_up" => p.r_up = u,
            "r_mark" => p.r_mark = u,
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

/// The stone heart: no crowd control, for good.
pub fn stone_buff() -> BuffV1 {
    let mut b = BuffV1::named(&bk("p_stone"));
    b.cc_immune = true;
    b
}

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// The percentage of the slam a unit `dist` from where he landed takes: r_fall% less a whole hex out, never under
/// r_min%.
pub fn falloff(dist: u64, p: &Params) -> usize {
    let hexes = (dist / p.r_hex.max(1) as u64) as usize;
    100usize.saturating_sub(hexes * p.r_fall).max(p.r_min)
}

/// The slam's full damage: base + ratio% of his attack + hp% of his maximum health.
pub fn slam_damage(p: &Params, attack: usize, max_hp: usize) -> usize {
    p.r_dmg + attack * p.r_ratio / 100 + max_hp * p.r_hp / 100
}

// ===================== 场上 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

// ===================== 震地猛击 =====================

/// The landing: every enemy (no towers, no nexus) in reach takes the slam by its distance; the first time in a fight,
/// knocked up.
struct Slam;
impl StableEffectType for Slam {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _input: InputTargetV1) {
        let Some((at, team, attack, max_hp)) = sim
            .get_entity(me)
            .filter(|e| e.is_alive())
            .map(|e| (e.pos(), e.team(), e.stat().attack, e.hp().1))
        else {
            return;
        };
        let p = params_of(me);
        let full = slam_damage(&p, attack, max_hp);
        let reach = (p.r_r as u64 + BODY) as u128;
        let foes: Vec<(usize, (u64, u64))> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
            .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus)))
            .filter(|u| dist_sq(u.pos(), at) <= reach * reach)
            .map(|u| (u.id(), u.pos()))
            .collect();
        let (mut thrown, mut champs) = (0, 0);
        for (id, pos) in &foes {
            let d = (dist_sq(*pos, at) as f64).sqrt() as u64;
            let pct = falloff(d.saturating_sub(BODY), &p);
            sim.deal_damage_typed(me, *id, full * pct / 100, DamageTypeV1::Ad, AttackTypeV1::Skill);
            if sim.get_entity(*id).is_some_and(|e| e.is_champion()) {
                champs += 1;
            }
            if !has_buff(sim, *id, &bk("r_mark")) {
                sim.apply_cc(*id, &CcV1::of_kind(CcKindV1::Airborne, p.r_up as u64));
                put(sim, *id, &BuffV1::timed(&bk("r_hit"), p.r_up.max(30)));
                put(sim, *id, &BuffV1::timed(&bk("r_mark"), p.r_mark));
                sim.play_sfx(&bk("r_hit"), me, &InputTargetV1::target(*id));
                thrown += 1;
            }
        }
        if let Some(k) = counted("slam") {
            wlog(format!("{} SLAM #{k}: {} enemies ({champs} champions) take up to {full}, {thrown} thrown up {} ticks",
                         head(sim, me), foes.len(), p.r_up));
        }
    }
}

// ===================== 被动：岩心不动 =====================

#[derive(Clone, Default)]
struct Stone {
    /// The champion it belongs to (on_dead is given the player, not the unit).
    me: usize,
    p: Params,
    /// Whether he was alive last tick (a new life puts the stone heart on at once).
    was_alive: bool,
}

impl StablePassive for Stone {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        // a new life is a new unit, and on_update does not run while it is dead: the first tick of this life
        // must see a dead one (Terra's way)
        self.was_alive = false;
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Brock (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).entry(me).or_insert(self.p);
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        let new_life = alive && !self.was_alive;
        self.was_alive = alive;
        if !alive || !(new_life || sim.tick() % CHECK == 0) {
            return;
        }
        let b = stone_buff();
        if has_buff(sim, me, b.name()) {
            return;
        }
        sim.add_buff(me, &b);
        if let Some(k) = counted("stone") {
            wlog(format!("{} STONE #{k}: immune to crowd control{}", head(sim, me),
                         if new_life { " (a new life)" } else { " (was gone)" }));
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _player: usize) {
        let me = self.me;
        // his crumbling (the data has no moment for it)
        sim.play_sfx(&bk("d"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("dead") {
            wlog(format!("{} DEAD #{k}: {}", head(sim, me), name_of(sim, me)));
        }
    }
}

// ===================== 注册 =====================

/// Brock's passive and his ult's landing, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Brock: the stone heart, Seismic Slam) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:stone"), Stone::default());
    module.add_native_effect(format!("{ID}:slam"), Slam);
    host.log(LogLevel::Info, "tft.dll: Brock (stone heart, Seismic Slam).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"r_r":50000,"r_dmg":90,"r_ratio":80,"r_hp":3,"r_hex":18000,"r_fall":15,"r_min":40,"r_up":75,"r_mark":3600}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_stone_heart_is_permanent() {
        let b = stone_buff();
        assert_eq!((b.name(), b.cc_immune, b.duration_kind), ("tft_brock_p_stone", true, BuffDurationV1::Permanent.code()));
    }

    #[test]
    fn the_slam_falls_off_by_hex() {
        let p = Params::default();
        assert_eq!(falloff(0, &p), 100);
        assert_eq!(falloff(17999, &p), 100);
        assert_eq!(falloff(18000, &p), 85);
        assert_eq!(falloff(36000, &p), 70);
        assert_eq!(falloff(90000, &p), 40);
        assert_eq!(falloff(400000, &p), 40);
    }

    #[test]
    fn slam_damage_by_the_numbers() {
        assert_eq!(slam_damage(&Params::default(), 100, 2000), 90 + 80 + 60);
    }
}
