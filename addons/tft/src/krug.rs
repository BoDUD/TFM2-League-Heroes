//! 远古石甲虫（`tft_krug`）数据做不到的部分（金铲铲第 18 赛季的峡谷野怪 / 斗士；技能按用户选的方案 A「岩之摇滚」，
//! 2026-10-28）。他的数据（tools/kit/build_krug.py）的 `passive` 是这里的 `tft_krug:split`，参数从数据的 `passive.params`
//! 来（build_krug.py 从参数表 P 写进去，`NATIVE_KEYS`）：
//!
//! - **碎岩重生**：金铲铲里他阵亡时分裂成两只会嘲讽的小石甲虫；召唤物在数据里不能走路，所以做成重生。数据读不到生命：
//!   本被动在他能重生时一直挂着「不死」`tft_krug_p_guard`（艾尼维亚冰蛋的做法，生命停在 1 就触发），每条命第一次
//!   受到致命伤害、且离上次重生过了 `p_cd` tick 时，他碎成一堆石头 `p_t` tick（晕住自己、`tft_krug_p_shatter` 免伤），
//!   亮 `p_burst`、碎裂声；然后以小石甲虫站起来：生命 `p_hp`%，这条命剩下的时间攻速 +`p_as`%（`tft_krug_p_mini`），
//!   中心 `p_r` 内的敌人（英雄、小兵、野怪）被嘲讽 `p_taunt` tick，亮 `p_up`、吼一声。别人给的「不死」在身上时不触发。
//!
//! 岩之摇滚（护盾、滚向目标、击退）、坚岩外壳（双抗、嘲讽）和远古崩落（跃起、砸落、击飞、落石）是数据自己的。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft_krug.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "tft_krug";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// The shatter and the reforming roar (the tft pack's sound_info; the rest of his sounds the data plays).
const SFX_SHATTER: &str = "tft_krug_p";
const SFX_UP: &str = "tft_krug_p_up";
/// How long the guard lasts and how often it is renewed.
pub const GUARD_T: usize = 30;
pub const GUARD_EVERY: usize = 10;

fn kr(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_KRUG_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft_krug.log");
        }
    }
    PathBuf::from("tft_krug.log")
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 碎岩重生：站起来时的生命 p_hp%、两次重生至少隔 p_cd tick、碎着 p_t tick。
    pub p_hp: usize,
    pub p_cd: usize,
    pub p_t: usize,
    /// 小石甲虫：这条命剩下的时间攻速 +p_as%；中心 p_r 内的敌人嘲讽 p_taunt tick。
    pub p_as: usize,
    pub p_r: usize,
    pub p_taunt: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            p_hp: 35,
            p_cd: 3600,
            p_t: 45,
            p_as: 30,
            p_r: 40000,
            p_taunt: 60,
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
            "p_hp" => p.p_hp = u.clamp(1, 100),
            "p_cd" => p.p_cd = u,
            "p_t" => p.p_t = u,
            "p_as" => p.p_as = u,
            "p_r" => p.p_r = u,
            "p_taunt" => p.p_taunt = u,
            _ => {}
        }
    }
    p
}

// ===================== 规则（单元测试用） =====================

/// The guard is up (he can be reborn): not reborn yet this life, the cooldown over, and nobody else's undying on him.
pub fn can_rebirth(reborn: bool, now: usize, ready_at: usize) -> bool {
    !reborn && now >= ready_at
}

/// A blow that would have killed him: the guard holds him at 1 hp (0.6.4 reads 0 hp on a match's first tick: only
/// after he was seen above 1 this life).
pub fn lethal(hp: usize, alive_seen: bool) -> bool {
    alive_seen && hp <= 1
}

/// His health when he stands up again: p_hp% of his maximum, at least 1.
pub fn reborn_hp(max: usize, p: &Params) -> usize {
    (max * p.p_hp / 100).max(1)
}

/// Whether `name` is our own guard (another undying on him stops the rebirth).
pub fn ours(name: &str) -> bool {
    name == kr("p_guard")
}

pub fn other_undying(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(name, undying)| *undying && !ours(name))
}

pub fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u128 {
    let dx = a.0 as i128 - b.0 as i128;
    let dy = a.1 as i128 - b.1 as i128;
    (dx * dx + dy * dy) as u128
}

/// The Mini Krug's buff: attack speed for the rest of the life (Permanent; taken off at the start of the next life).
pub fn mini_buff(p: &Params) -> BuffV1 {
    let mut b = BuffV1::named(&kr("p_mini"));
    b.attack_speed_mult = p.p_as as i32;
    b
}

/// While he lies shattered: no damage, and still undying (the guard is gone by then).
pub fn shatter_buff(p: &Params) -> BuffV1 {
    let mut b = BuffV1::timed(&kr("p_shatter"), p.p_t + 2);
    b.damaged_reduce = 100;
    b.undying = true;
    b
}

// ===================== 被动 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

#[derive(Clone, Default)]
struct Split {
    p: Params,
    /// The next tick a rebirth may come (kept across lives), and whether this life had its rebirth.
    ready_at: usize,
    reborn: bool,
    /// The tick he shattered (None when he is not lying in pieces).
    shattered: Option<usize>,
    next_guard: usize,
    alive_seen: bool,
    was_alive: bool,
}

impl Split {
    fn guard(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        if now < self.next_guard {
            return;
        }
        let mut g = BuffV1::timed(&kr("p_guard"), GUARD_T);
        g.undying = true;
        sim.entity_remove_buff(me, &kr("p_guard"));
        sim.add_buff(me, &g);
        self.next_guard = now + GUARD_EVERY;
    }

    fn shatter(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        self.shattered = Some(now);
        self.reborn = true;
        self.ready_at = now + self.p.p_cd;
        sim.entity_remove_buff(me, &kr("p_guard"));
        sim.apply_cc(me, &CcV1::stun(self.p.p_t as u64));
        sim.entity_remove_buff(me, &kr("p_shatter"));
        sim.add_buff(me, &shatter_buff(&self.p));
        let on = InputTargetV1::target(me);
        sim.play_view_effect(&kr("p_burst"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_SHATTER, me, &on);
        if let Some(k) = counted("shatter") {
            wlog(format!("{} SHATTER #{k}: a lethal blow caught at 1 hp, in pieces for {} ticks", head(sim, me),
                         self.p.p_t));
        }
    }

    fn stand(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.shattered = None;
        let Some((team, at, max)) = sim.get_entity(me).map(|e| (e.team(), e.pos(), e.hp().1)) else { return };
        let hp = reborn_hp(max, &self.p);
        sim.entity_set_hp(me, hp);
        sim.entity_remove_buff(me, &kr("p_shatter"));
        sim.entity_remove_buff(me, &kr("p_mini"));
        sim.add_buff(me, &mini_buff(&self.p));
        let on = InputTargetV1::target(me);
        sim.play_view_effect(&kr("p_up"), me, &on, 0, 0, 0);
        sim.play_sfx(SFX_UP, me, &on);
        let reach = (self.p.p_r as u128) * (self.p.p_r as u128);
        let near: Vec<usize> = (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| e.team() != team && e.is_alive() && dist_sq(e.pos(), at) <= reach)
            .filter(|e| !matches!(e.kind(), Some(EntityKindV1::Tower) | Some(EntityKindV1::Nexus) | None))
            .map(|e| e.id())
            .collect();
        let mut taunt = CcV1::of_kind(CcKindV1::Taunt, self.p.p_taunt as u64);
        taunt.target = me;
        for &id in &near {
            sim.apply_cc(id, &taunt);
            sim.entity_remove_buff(id, &kr("e_taunt"));
            sim.add_buff(id, &BuffV1::timed(&kr("e_taunt"), self.p.p_taunt));
        }
        if let Some(k) = counted("stand") {
            wlog(format!("{} REBORN #{k}: a Mini Krug with {hp}/{max} hp, +{}% attack speed, {} enemies taunted {} ticks",
                         head(sim, me), self.p.p_as, near.len(), self.p.p_taunt));
        }
    }
}

impl StablePassive for Split {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if let Some(k) = counted("spawn") {
            let team = sim.get_entity(me).map_or(0, |e| e.team());
            wlog(format!("{} SPAWN #{k}: tft.dll's Ancient Krug (player {player}, team {team}), {:?}", head(sim, me),
                         self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        let Some((alive, (hp, _))) = sim.get_entity(me).map(|e| (e.is_alive(), e.hp())) else { return };
        if alive && !self.was_alive {   // the first tick of a life: a whole Ancient Krug again
            self.reborn = false;
            self.shattered = None;
            self.alive_seen = false;
            sim.entity_remove_buff(me, &kr("p_mini"));
        }
        self.was_alive = alive;
        if !alive {
            return;
        }
        if let Some(t0) = self.shattered {
            if now >= t0 + self.p.p_t {
                self.stand(sim, me);
            }
            return;
        }
        if hp > 1 {
            self.alive_seen = true;
        }
        if !can_rebirth(self.reborn, now, self.ready_at) {
            return;
        }
        self.guard(sim, me, now);
        if lethal(hp, self.alive_seen) {
            let list: Vec<(String, bool)> = buffs(sim, me).iter().map(|b| (b.name().to_string(), b.undying)).collect();
            if !other_undying(&list) {
                self.shatter(sim, me, now);
            }
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if self.shattered.take().is_some() {
            if let Some(k) = counted("broken") {
                wlog(format!("{} BROKEN #{k}: killed while in pieces", head(sim, me)));
            }
        }
    }
}

// ===================== 注册 =====================

/// The Ancient Krug's passive, into the tft pack's module (lib.rs's `init`).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (the Ancient Krug: the Shattered Rebirth) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:split"), Split::default());
    host.log(LogLevel::Info, "tft.dll: the Ancient Krug (the Shattered Rebirth).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let json = r#"{"p_as":30,"p_cd":3600,"p_hp":35,"p_r":40000,"p_t":45,"p_taunt":60}"#;
        assert_eq!(parse_params(json), Params::default());
    }

    #[test]
    fn one_rebirth_a_life_and_a_cooldown() {
        assert!(can_rebirth(false, 100, 0));
        assert!(!can_rebirth(true, 100, 0));
        assert!(!can_rebirth(false, 100, 3700));
        assert!(can_rebirth(false, 3700, 3700));
    }

    #[test]
    fn lethal_only_after_he_was_seen_alive() {
        assert!(lethal(1, true));
        assert!(lethal(0, true));
        assert!(!lethal(0, false));
        assert!(!lethal(2, true));
    }

    #[test]
    fn reborn_with_part_of_his_health() {
        let p = Params::default();
        assert_eq!(reborn_hp(2000, &p), 700);
        assert_eq!(reborn_hp(1, &p), 1);
    }

    #[test]
    fn another_undying_stops_it() {
        assert!(!other_undying(&[("tft_krug_p_guard".into(), true), ("x".into(), false)]));
        assert!(other_undying(&[("league_sion_r".into(), true)]));
    }

    #[test]
    fn the_buffs() {
        let p = Params::default();
        let m = mini_buff(&p);
        assert_eq!(m.name(), "tft_krug_p_mini");
        assert_eq!(m.attack_speed_mult, 30);
        assert_eq!(m.duration_kind, BuffDurationV1::Permanent.code());
        let s = shatter_buff(&p);
        assert_eq!((s.damaged_reduce, s.undying, s.duration_tick), (100, true, 47));
    }
}
