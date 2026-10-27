//! 范德尔（`tft_vander`）数据做不到的部分（金铲铲第 13 赛季的家人 / 监察，技能和被动按用户选的方案 A「监察·地下猎犬」，
//! 2026-10-27）。他的数据（tools/kit/build_vander.py）的 `passive` 是这里的 `tft_vander:watcher`，参数从数据的
//! `passive.params` 来（build_vander.py 从参数表 P 写进去，`NATIVE_KEYS`），按他的单位编号记一份给效果用：
//!
//! - **监察**：数据读不到生命。被动每拍看他的生命：高于 `p_line`% 时挂 `tft_vander_p_watch`（受到的伤害少 `p_hi`%），
//!   不高于时换成少 `p_lo`% 的那一档；死了就摘掉。
//! - **地下猎犬的重击**（`tft_vander:family`：重击打中时）：他队里每有一个家人（爆爆 `tft_powder`、蔚 `league_vi`、
//!   金克丝 `league_jinx`），对那个目标多打攻击力 `q_fam`% 的物理伤害（金铲铲里是每个一二费队友加 100% 攻击力）。
//! - **桥头死守**（`tft_vander:stand`：砸地时）：`r_r` 以内每有一个敌方英雄（最多 `r_cap` 个），减伤在 `r_red`% 上再加
//!   `r_per`%，挂 `tft_vander_r_hold` `r_t` 拍。
//!
//! 防御姿态、嘲讽、重击本身、铁拳突进和砸地击飞是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_vander.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_vander";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 家人：金铲铲第 13 赛季的【家人】是爆爆、蔚、范德尔（金克丝是长大的爆爆）。
const FAMILY: [&str; 3] = ["tft_powder", "league_vi", "league_jinx"];

fn va(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_VANDER_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_vander.log");
        }
    }
    PathBuf::from("tft_vander.log")
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
    /// 监察：生命高于 p_line% 时少受 p_hi%，否则 p_lo%。
    pub p_lo: usize,
    pub p_hi: usize,
    pub p_line: usize,
    /// 重击：每个家人多打攻击力 q_fam%。
    pub q_fam: usize,
    /// 桥头死守：数敌人的半径、基础减伤、每个敌人加多少、最多数几个、几拍。
    pub r_r: u64,
    pub r_red: usize,
    pub r_per: usize,
    pub r_cap: usize,
    pub r_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_lo: 10,
            p_hi: 20,
            p_line: 50,
            q_fam: 40,
            r_r: 34000,
            r_red: 15,
            r_per: 8,
            r_cap: 4,
            r_t: 240,
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
            "p_lo" => p.p_lo = u.min(90),
            "p_hi" => p.p_hi = u.min(90),
            "p_line" => p.p_line = u.min(100),
            "q_fam" => p.q_fam = u,
            "r_r" => p.r_r = u as u64,
            "r_red" => p.r_red = u.min(90),
            "r_per" => p.r_per = u,
            "r_cap" => p.r_cap = u,
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

// ===================== 算式 =====================

/// 监察这一拍该少受多少：生命高于 line% 时 hi，否则 lo（没有最大生命就算 lo）。
pub fn watch_tier(hp: usize, max: usize, p: &Params) -> usize {
    if max > 0 && hp * 100 > max * p.p_line {
        p.p_hi
    } else {
        p.p_lo
    }
}

/// 队里的家人有几个（不算他自己）。
pub fn family_count<'a>(names: impl IntoIterator<Item = &'a str>) -> usize {
    names.into_iter().filter(|n| FAMILY.contains(n)).count()
}

/// 桥头死守的减伤：基础 + 每个敌人 r_per（最多数 r_cap 个），不超过 90%。
pub fn stand_reduce(enemies: usize, p: &Params) -> usize {
    (p.r_red + enemies.min(p.r_cap) * p.r_per).min(90)
}

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

// ===================== 游戏里 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn put(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, buff.name());
    sim.add_buff(id, buff);
}

/// 他这一队还活着的英雄（不算他自己）的名字。
fn team_names(sim: &StableSim<'_>, me: usize) -> Vec<String> {
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return Vec::new() };
    (0..sim.champion_count())
        .map(|i| sim.champion_id_at(i))
        .filter(|&id| id != me)
        .filter_map(|id| sim.get_entity(id))
        .filter(|c| c.team() == team)
        .filter_map(|c| c.name())
        .collect()
}

struct Family;
impl StableEffectType for Family {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let target = input.target_id;
        if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
            return;
        }
        let names = team_names(sim, me);
        let n = family_count(names.iter().map(String::as_str));
        if n == 0 {
            return;
        }
        let atk = sim.get_entity(me).map_or(0, |e| e.stat().attack);
        let extra = atk * params_of(me).q_fam * n / 100;
        sim.deal_damage(me, target, extra, 0, AttackTypeV1::BaseAttack);
        if let Some(k) = counted("family") {
            wlog(format!("{} FAMILY #{k}: {n} family on the team, +{extra} on {}", head(sim, me), name_of(sim, target)));
        }
    }
}

struct Stand;
impl StableEffectType for Stand {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, _: InputTargetV1) {
        let Some((team, at)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.team(), e.pos())) else { return };
        let p = params_of(me);
        let reach = (p.r_r as u128) * (p.r_r as u128);
        let enemies = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter_map(|id| sim.get_entity(id))
            .filter(|c| c.team() != team && c.is_alive() && dist_sq(c.pos(), at) <= reach)
            .count();
        let reduce = stand_reduce(enemies, &p);
        let mut hold = BuffV1::timed(&va("r_hold"), p.r_t);
        hold.damaged_reduce = reduce;
        put(sim, me, &hold);
        if let Some(k) = counted("stand") {
            wlog(format!("{} STAND #{k}: {enemies} enemy champions round him, {reduce}% less damage for {} ticks",
                         head(sim, me), p.r_t));
        }
    }
}

#[derive(Clone, Default)]
struct Watcher {
    p: Params,
    tier: Option<usize>,
}

impl StablePassive for Watcher {
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
            let family = family_count(team_names(sim, me).iter().map(String::as_str));
            wlog(format!("{} SPAWN #{k}: tft.dll's Vander (player {player}, team {team}, {family} family), {:?}",
                         head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some((alive, (hp, max))) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp())) else { return };
        if !alive {
            if self.tier.take().is_some() {
                sim.entity_remove_buff(me, &va("p_watch"));
            }
            return;
        }
        let tier = watch_tier(hp, max, &self.p);
        // put again when the tier changes, or when something took the buff off (a cleanse)
        let missing = !has(sim, me, &va("p_watch"));
        if self.tier != Some(tier) || missing {
            let mut watch = BuffV1::named(&va("p_watch"));
            watch.damaged_reduce = tier;
            put(sim, me, &watch);
            if self.tier != Some(tier) {
                if let Some(k) = counted("watch") {
                    wlog(format!("{} WATCH #{k}: {hp}/{max}, {tier}% less damage", head(sim, me)));
                }
            }
            self.tier = Some(tier);
        }
    }
}

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Vander: the Watcher by health, the Family strike, the stand by the enemies round him) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:watcher"), Watcher::default());
    module.add_native_effect(format!("{ID}:family"), Family);
    module.add_native_effect(format!("{ID}:stand"), Stand);
    host.log(LogLevel::Info, "tft.dll: Vander (Watcher, Family strike, Last Stand).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_hi":20,"p_line":50,"p_lo":10,"q_fam":40,"r_cap":4,"r_per":8,"r_r":34000,"r_red":15,"r_t":240}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn the_watch_by_health() {
        let p = Params::default();
        assert_eq!(watch_tier(1000, 1000, &p), 20);
        assert_eq!(watch_tier(501, 1000, &p), 20);
        // exactly half is not above it
        assert_eq!(watch_tier(500, 1000, &p), 10);
        assert_eq!(watch_tier(1, 1000, &p), 10);
        assert_eq!(watch_tier(0, 0, &p), 10);
    }

    #[test]
    fn his_family_only() {
        assert_eq!(family_count(["tft_powder", "league_vi", "league_garen"]), 2);
        assert_eq!(family_count(["league_jinx"]), 1);
        assert_eq!(family_count(["tft_silco", "league_warwick"]), 0);
    }

    #[test]
    fn the_stand_grows_with_the_enemies_then_stops() {
        let p = Params::default();
        assert_eq!(stand_reduce(0, &p), 15);
        assert_eq!(stand_reduce(2, &p), 31);
        assert_eq!(stand_reduce(4, &p), 47);
        assert_eq!(stand_reduce(9, &p), 47);
        let big = Params { r_per: 40, ..p };
        assert_eq!(stand_reduce(4, &big), 90);
    }
}
