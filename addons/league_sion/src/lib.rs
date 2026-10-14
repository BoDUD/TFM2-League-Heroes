//! 赛恩附加包（用户选「主包数据 + 附加包复活」）：主包数据做不到的两件事。
//!
//! `mod.override_info` 把主包的赛恩换成 `override/` 里的副本（tools/kit/build_sion.py 的 native=1）：数据和主包一样，只是
//! - 被动挂本包的 `league_sion:glory`（参数在英雄数据的 `passive.params` 里）；
//! - 普攻不再自己查击杀加生命（本包按每一次击杀加，技能击杀也算）。
//!
//! - **死亡荣耀**：每条命第一次受到致命伤害时不倒下（本包一直给他挂着 `league_sion_p_guard`「不死」，生命停在 1 就触发），
//!   变成亡灵 `z_t` tick：生命回满，之后每 tick 均匀流失（`z_t` tick 后归零），攻速 +`z_as`%、吸血 `z_vamp`%，
//!   不能放技能（`BlockSkill`），身上挂 `league_sion_p_zombie`（画面）。时间到就倒下，击杀算最后打他的那个人。
//!   别人给的「不死」（索拉卡 W、基兰符文、凯尔等）在身上时不触发：那段时间他本来就死不了。
//! - **灵魂熔炉（被动）**：每击杀一个单位永久 +`k_u` 最大生命，英雄 +`k_c`（英雄联盟：小兵 4、英雄和大型野怪 15）；
//!   技能击杀也算，阵亡后不丢（主包数据的版本只算普攻击杀，阵亡就没了）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_sion.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_sion";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";

/// 「不死」挂多久、多久续一次（一直挂着，复活用掉前不断）。
pub const GUARD_T: usize = 30;
pub const GUARD_EVERY: usize = 10;

fn sn(x: &str) -> String {
    format!("league_sion_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SION_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_sion.log");
        }
    }
    PathBuf::from("league_sion.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (opening it for every line stalled the game, 2026-10-12)
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

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
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

/// 亡灵第 `k` tick（0 起）该剩多少生命：从 `max` 均匀降到 `z_t` tick 时的 0；至少 1（不死还在）。
pub fn zombie_hp(max: usize, k: usize, z_t: usize) -> usize {
    if k >= z_t {
        return 1;
    }
    (max * (z_t - k) / z_t).max(1)
}

/// 亡灵这一 tick 的流失：吸血回上来的不算进计划，所以按「每 tick 少 max / z_t」扣现在的生命。
pub fn decay_step(max: usize, z_t: usize) -> usize {
    (max / z_t.max(1)).max(1)
}

/// 灵魂熔炉一次击杀加多少最大生命。
pub fn kill_hp(victim_is_champion: bool, p: &Params) -> usize {
    if victim_is_champion { p.k_c } else { p.k_u }
}

/// 名字是不是本包的「不死」（别的「不死」在身上时不触发复活）。
pub fn ours(name: &str) -> bool {
    name == sn("p_guard") || name == sn("p_zombie")
}

pub fn other_undying(names_undying: &[(String, bool)]) -> bool {
    names_undying.iter().any(|(name, undying)| *undying && !ours(name))
}

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub k_u: usize,
    pub k_c: usize,
    pub z_t: usize,
    pub z_as: usize,
    pub z_vamp: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { k_u: 4, k_c: 15, z_t: 540, z_as: 60, z_vamp: 100 }
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
            "k_u" => p.k_u = v,
            "k_c" => p.k_c = v,
            "z_t" => p.z_t = v,
            "z_as" => p.z_as = v,
            "z_vamp" => p.z_vamp = v,
            _ => {}
        }
    }
    p
}

// ===================== 被动 =====================

fn buffs(sim: &StableSim<'_>, id: usize) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect())
}

#[derive(Clone, Default)]
struct Glory {
    p: Params,
    me: usize,
    /// 灵魂熔炉攒下的最大生命（跨命保留）。
    stacks: usize,
    /// 这条命的复活还在。
    ready: bool,
    /// 亡灵开始的 tick（不在亡灵状态时 None）。
    zombie: Option<usize>,
    /// 最后一个打他的（倒下时算击杀）。
    last_hit: Option<usize>,
    next_guard: usize,
    /// 这条命里见过他 1 血以上：游戏 0.6.4 开局第 0 tick 读到的血量还是 0，那不是致命伤（每局第一条命都在 0 tick 变成亡灵、
    /// 9 秒后倒下，用户：「塞恩有bug吧 开局血掉光？」）。
    alive_seen: bool,
}

impl Glory {
    fn stack_buff(&self, sim: &mut StableSim<'_>, me: usize) {
        sim.entity_remove_buff(me, &sn("k_hp"));
        if self.stacks > 0 {
            let mut b = BuffV1::named(&sn("k_hp"));
            b.hp = self.stacks as i32;
            sim.add_buff(me, &b);
        }
    }

    fn guard(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        if now < self.next_guard {
            return;
        }
        let mut g = BuffV1::timed(&sn("p_guard"), GUARD_T);
        g.undying = true;
        sim.entity_remove_buff(me, &sn("p_guard"));
        sim.add_buff(me, &g);
        self.next_guard = now + GUARD_EVERY;
    }

    fn rise(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        self.ready = false;
        self.zombie = Some(now);
        sim.entity_remove_buff(me, &sn("p_guard"));
        let mut z = BuffV1::timed(&sn("p_zombie"), self.p.z_t + 2);
        z.undying = true;
        z.attack_speed_mult = self.p.z_as as i32;
        z.vamp = self.p.z_vamp as i32;
        sim.add_buff(me, &z);
        sim.apply_cc(me, &CcV1::of_kind(CcKindV1::BlockSkill, self.p.z_t as u64));
        sim.entity_set_hp(me, max);
        sim.play_sfx(&sn("p_rise"), me, &InputTargetV1::target(me));
        sim.play_sfx(&sn("vo_p"), me, &InputTargetV1::target(me));
        if let Some(k) = counted("rise") {
            wlog(format!("{} RISE #{k}: lethal damage caught at 1 hp (last hit by {}), zombie {} ticks from {max} hp",
                         head(sim, me), self.last_hit.map_or_else(|| "-".to_string(), |a| who(sim, a)), self.p.z_t));
        }
    }

    fn fall(&mut self, sim: &mut StableSim<'_>, me: usize) {
        self.zombie = None;
        sim.entity_remove_buff(me, &sn("p_zombie"));
        let (hp, _) = sim.get_entity(me).map_or((0, 0), |e| e.hp());
        let killer = self.last_hit.filter(|&a| sim.get_entity(a).is_some()).unwrap_or(me);
        sim.deal_damage_typed(killer, me, hp + 1000, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        if let Some(k) = counted("fall") {
            wlog(format!("{} FALL #{k}: the zombie's time is up, killed by {}", head(sim, me), who(sim, killer)));
        }
    }
}

impl StablePassive for Glory {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.ready = true;
        self.zombie = None;
        self.last_hit = None;
        self.next_guard = 0;
        self.alive_seen = false;
        self.stack_buff(sim, me);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Sion (player {player}, team {team}), {:?}, soul furnace +{} hp",
                         head(sim, me), self.p, self.stacks));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let (hp, max) = e.hp();
        let now = sim.tick();
        if let Some(t0) = self.zombie {
            let k = now.saturating_sub(t0);
            if k >= self.p.z_t {
                self.fall(sim, me);
            } else if hp > 1 {
                // max / z_t a tick off what he has: untouched he reaches 1 at the end (zombie_hp), what the life steal
                // brings back stays
                sim.entity_set_hp(me, hp.saturating_sub(decay_step(max, self.p.z_t)).max(1));
            }
            return;
        }
        if !self.ready {
            return;
        }
        if hp > 1 {
            self.alive_seen = true;
        }
        self.guard(sim, me, now);
        if hp <= 1 && self.alive_seen {
            let list: Vec<(String, bool)> = buffs(sim, me).iter().map(|b| (b.name().to_string(), b.undying)).collect();
            if !other_undying(&list) {
                self.rise(sim, me, now);
            }
        }
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, _: usize, attacker: usize, damage: usize) {
        if damage > 0 && attacker != self.me && sim.get_entity(attacker).is_some() {
            self.last_hit = Some(attacker);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        let champ = sim.get_entity(victim).is_some_and(|v| v.is_champion());
        self.stacks += kill_hp(champ, &self.p);
        self.stack_buff(sim, me);
        if champ {
            if let Some(k) = counted("furnace") {
                wlog(format!("{} FURNACE #{k}: {} killed, max health +{} in all", head(sim, me), who(sim, victim),
                             self.stacks));
            }
        }
    }

    /// 小兵、野怪的击杀（游戏 0.6.4 起才有这个回调；`on_kill` 只管英雄，所以之前附加包里打死小兵野怪一直没加生命）：
    /// 照说明「每击杀一个单位 +`k_u`」。大小龙等史诗野怪奖励全队，两个回调都不触发。
    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        let camp = sim.get_entity(victim).and_then(|v| v.kind()) == Some(EntityKindV1::Jungle);
        self.stacks += kill_hp(false, &self.p);
        self.stack_buff(sim, me);
        if let Some(k) = counted("unit") {
            wlog(format!("{} FURNACE unit kill #{k} ({}): max health +{} in all", head(sim, me),
                         if camp { "camp" } else { "minion" }, self.stacks));
        }
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        self.zombie = None;
        self.ready = false;
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Sion: Glory in Death's zombie, Soul Furnace's health from every kill) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:glory"), Glory::default());
    host.log(LogLevel::Info, "league_sion loaded (Glory in Death's zombie, Soul Furnace from every kill).");
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

    #[test]
    fn the_zombie_drains_to_nothing() {
        assert_eq!(zombie_hp(2000, 0, 540), 2000);
        assert_eq!(zombie_hp(2000, 270, 540), 1000);
        assert_eq!(zombie_hp(2000, 539, 540), 3);
        assert_eq!(zombie_hp(2000, 540, 540), 1);
        assert_eq!(decay_step(2000, 540), 3);
        assert_eq!(decay_step(100, 540), 1);
    }

    #[test]
    fn soul_furnace_by_victim() {
        let p = Params::default();
        assert_eq!(kill_hp(false, &p), 4);
        assert_eq!(kill_hp(true, &p), 15);
    }

    #[test]
    fn only_someone_elses_undying_holds_the_rise_back() {
        let l = |v: &[(&str, bool)]| v.iter().map(|(n, u)| (n.to_string(), *u)).collect::<Vec<_>>();
        assert!(!other_undying(&l(&[("league_sion_p_guard", true)])));
        assert!(!other_undying(&l(&[("league_sion_p_guard", true), ("league_sion_k_hp", false)])));
        assert!(other_undying(&l(&[("league_sion_p_guard", true), ("league_soraka_w_guard", true)])));
        assert!(other_undying(&l(&[("league_zilean_r_rune", true)])));
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"k_c":15,"k_u":4,"z_as":60,"z_t":540,"z_vamp":100}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_sion.py");
        let src = std::fs::read_to_string(path).expect("build_sion.py");
        let d = Params::default();
        for (key, v) in [("k_u", d.k_u), ("k_c", d.k_c), ("z_t", d.z_t), ("z_as", d.z_as), ("z_vamp", d.z_vamp)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_sion.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["p_guard", "p_zombie", "k_hp", "p_rise", "vo_p"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }
}
