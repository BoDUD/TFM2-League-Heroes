//! 玛尔扎哈附加包（用户选「做：E 跳转 + 被动精确」）：主包数据做不准的两件事。
//!
//! `mod.override_info` 把主包的玛尔扎哈换成 `override/` 里的副本（tools/kit/build_malzahar.py 的 native=1）：数据和主包一样，
//! 只是
//! - 被动挂本包的 `league_malzahar:void`（参数在英雄数据的 `passive.params` 里），主包的护盾被动（数据）不再加；
//! - 煞星幻象打中的每个单位都调用本包的 `league_malzahar:vision`，主包数据里的「死亡检查 + 跳一次」不再加。
//!
//! - **虚空穿越**（英雄联盟原版）：准备好时身上挂 `league_malzahar_p_shift`（画面）：受到的伤害减少 `p_dr`%、**免疫控制**；
//!   第一次被**非小兵**（英雄、野怪、防御塔）打中后再持续 `p_linger` tick 就消失；之后 `p_cd` tick 内**没受到英雄伤害**才重新
//!   准备好（每受一次英雄伤害重新计时）。小兵的伤害照样减少，但不会打破它。每条命开始时是准备好的。
//! - **煞星幻象的跳转**：幻象（主包数据的持续伤害）在 `e_t` tick 内目标死了，立刻跳到目标倒下处 `e_jump` 内最近的敌人身上
//!   （先找英雄，没有再找别的敌人，不找防御塔），新目标重新受到完整的幻象：`e_t` tick 内每 `e_p` tick 一段，共
//!   `e_dmg` + `e_ap`% 法强的魔法伤害（由本包结算），头上挂 `league_malzahar_e_markb`（画面）；它死了照样再跳，没有次数限制。
//!   英雄联盟里跳转还会刷新 E 的冷却：TFM2 的冷却加速（`skill_cooldown_mult`）会把 Q 一起刷新，所以不做。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_malzahar.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_malzahar";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_malzahar") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 虚空穿越的 buff 挂多久（一直挂到被打破，用一个很长的时间）。
pub const SHIFT_T: usize = 1_000_000;

fn sn(x: &str) -> String {
    format!("league_malzahar_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_MALZAHAR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_malzahar.log");
        }
    }
    PathBuf::from("league_malzahar.log")
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub p_cd: usize,
    pub p_linger: usize,
    pub p_dr: usize,
    pub e_t: usize,
    pub e_p: usize,
    pub e_dmg: usize,
    pub e_ap: usize,
    pub e_jump: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { p_cd: 720, p_linger: 15, p_dr: 90, e_t: 240, e_p: 15, e_dmg: 170, e_ap: 80, e_jump: 40000 }
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
            "p_cd" => p.p_cd = v,
            "p_linger" => p.p_linger = v,
            "p_dr" => p.p_dr = v,
            "e_t" => p.e_t = v,
            "e_p" => p.e_p = v,
            "e_dmg" => p.e_dmg = v,
            "e_ap" => p.e_ap = v,
            "e_jump" => p.e_jump = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 幻象一段的伤害：总伤害 `e_dmg` + `e_ap`% 法强，分成 `e_t / e_p` 段（至少 1）。
pub fn part_damage(p: &Params, ap: usize) -> usize {
    let runs = (p.e_t / p.e_p.max(1)).max(1);
    ((p.e_dmg + p.e_ap * ap / 100) / runs).max(1)
}

/// 虚空穿越什么时候重新准备好：被打破的时刻和最后一次英雄伤害里晚的那个，再过 `p_cd`。
pub fn shift_back_at(broken: usize, last_champion_hit: Option<usize>, p_cd: usize) -> usize {
    broken.max(last_champion_hit.unwrap_or(0)) + p_cd
}

/// 跳转目标：`cands` 是 (id, 是英雄, 距离²)。先选范围内最近的英雄，没有再选最近的其他单位；`r` 是半径。
pub fn pick_jump(cands: &[(usize, bool, u64)], r: u64) -> Option<usize> {
    let r2 = r.saturating_mul(r);
    let near = |champ: bool| {
        cands.iter().filter(|c| c.1 == champ && c.2 <= r2).min_by_key(|c| (c.2, c.0)).map(|c| c.0)
    };
    near(true).or_else(|| near(false))
}

fn dist2(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0.abs_diff(b.0);
    let dy = a.1.abs_diff(b.1);
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

// ===================== 煞星幻象：记录和跳转 =====================

#[derive(Clone, Copy, Debug)]
struct Vision {
    target: usize,
    until: usize,
    /// 本包结算伤害（跳过来的）；主包数据打中的那个由数据结算。
    ours: bool,
    next: usize,
    last_pos: (u64, u64),
}

/// 每份模拟的编号（0.1.x，2026-11-01 复查；league_teemo_shrooms / league_galio 的做法）：被动第一次出生时抽一个，每次出生挂在
/// 他身上（buff `SIM_TAG<n>`）。以前两张表只按实体 id 记：服务器并排跑的两份预演实体 id 一样，别的比赛里同 id 的玛尔扎哈也会撞上，
/// 一份模拟的被动 `remove` 走另一份的幻象，幻象的伤害和跳转只在其中一份里发生。
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
pub const SIM_TAG: &str = "league_malzahar_sim:";

/// 挂在这个单位身上的模拟编号（还没挂：0）。
fn sim_no(sim: &StableSim<'_>, id: usize) -> u64 {
    sim.get_entity(id).map_or(0, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i))
            .find_map(|b| b.name().strip_prefix(SIM_TAG).and_then(|v| v.parse().ok()))
            .unwrap_or(0)
    })
}

/// 每个玛尔扎哈（模拟编号, 实体 id）身上正在跑的幻象。效果和被动是两个对象，用这张表连起来。
static VISIONS: LazyLock<Mutex<HashMap<(u64, usize), Vec<Vision>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// 每个玛尔扎哈的参数（被动 on_spawn 时写入，效果用它算时间）。
static PARAMS: LazyLock<Mutex<HashMap<(u64, usize), Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(key: (u64, usize)) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&key).copied().unwrap_or_default()
}

/// 主包数据的幻象打中一个单位（`league_malzahar:vision`）：记下它，被动每 tick 看它死没死。
fn vision_hit(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let target = input.target_id;
    let Some(e) = sim.get_entity(target) else { return };
    let pos = e.pos();
    let key = (sim_no(sim, caster), caster);
    let p = params_of(key);
    let now = sim.tick();
    let mut map = VISIONS.lock().unwrap_or_else(|e| e.into_inner());
    let list = map.entry(key).or_default();
    list.retain(|v| v.target != target);
    list.push(Vision { target, until: now + p.e_t, ours: false, next: now + p.e_p, last_pos: pos });
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Void {
    p: Params,
    me: usize,
    /// 虚空穿越准备好了（buff 在身上）。
    ready: bool,
    /// 被第一次打中后，到这个 tick 消失。
    linger_until: Option<usize>,
    broken_at: usize,
    last_champion_hit: Option<usize>,
    /// 这份模拟的编号（`SIM_TAG`），他第一次出生时抽。
    sim: u64,
}

impl Void {
    fn arm(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let mut b = BuffV1::timed(&sn("p_shift"), SHIFT_T);
        b.damaged_reduce = self.p.p_dr;
        b.cc_immune = true;
        sim.entity_remove_buff(me, &sn("p_shift"));
        sim.add_buff(me, &b);
        sim.play_sfx(&sn("p_shift"), me, &InputTargetV1::target(me));
        self.ready = true;
        self.linger_until = None;
    }

    fn break_shift(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        sim.entity_remove_buff(me, &sn("p_shift"));
        self.ready = false;
        self.linger_until = None;
        self.broken_at = now;
        if let Some(k) = counted("break") {
            wlog(format!("{} SHIFT #{k}: Void Shift spent, back after {} ticks without champion damage", head(sim, me),
                         self.p.p_cd));
        }
    }

    fn visions(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let mut list = {
            let mut map = VISIONS.lock().unwrap_or_else(|e| e.into_inner());
            map.remove(&(self.sim, me)).unwrap_or_default()
        };
        if list.is_empty() {
            return;
        }
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let mut keep = Vec::new();
        for mut v in list.drain(..) {
            let alive = sim.get_entity(v.target).is_some_and(|e| e.is_alive());
            if alive {
                if now >= v.until {
                    continue;
                }
                if let Some(e) = sim.get_entity(v.target) {
                    v.last_pos = e.pos();
                }
                if v.ours && now >= v.next {
                    v.next += self.p.e_p;
                    sim.deal_damage_typed(me, v.target, part_damage(&self.p, ap), DamageTypeV1::Ap, AttackTypeV1::Skill);
                }
                keep.push(v);
                continue;
            }
            if now >= v.until {
                continue;
            }
            // the target fell while the vision ran: to the nearest enemy where it fell, champions first
            let mut cands = Vec::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.team() == team || !e.is_alive() || e.is_tower() || !e.is_targetable() || e.id() == v.target {
                    continue;
                }
                cands.push((e.id(), e.is_champion(), dist2(e.pos(), v.last_pos)));
            }
            let Some(next) = pick_jump(&cands, self.p.e_jump as u64) else {
                if let Some(k) = counted("lost") {
                    wlog(format!("{} JUMP #{k}: {} fell under the vision, no enemy within {}", head(sim, me),
                                 who(sim, v.target), self.p.e_jump));
                }
                continue;
            };
            let mark = BuffV1::timed(&sn("e_markb"), self.p.e_t);
            sim.entity_remove_buff(next, &sn("e_markb"));
            sim.add_buff(next, &mark);
            sim.play_sfx(&sn("e_jump"), me, &InputTargetV1::target(next));
            if let Some(k) = counted("jump") {
                wlog(format!("{} JUMP #{k}: {} fell, the vision moves to {} ({} ticks, {} a part)", head(sim, me),
                             who(sim, v.target), who(sim, next), self.p.e_t, part_damage(&self.p, ap)));
            }
            let pos = sim.get_entity(next).map_or(v.last_pos, |e| e.pos());
            keep.retain(|k: &Vision| k.target != next);
            keep.push(Vision { target: next, until: now + self.p.e_t, ours: true, next: now + self.p.e_p, last_pos: pos });
        }
        let mut map = VISIONS.lock().unwrap_or_else(|e| e.into_inner());
        let slot = map.entry((self.sim, me)).or_default();
        // visions the data started during this tick are already in the table: keep both
        for v in keep {
            if !slot.iter().any(|s| s.target == v.target) {
                slot.push(v);
            }
        }
    }
}

impl StablePassive for Void {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.last_champion_hit = None;
        if self.sim == 0 {
            self.sim = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert((self.sim, me), self.p);
        VISIONS.lock().unwrap_or_else(|e| e.into_inner()).remove(&(self.sim, me));
        self.arm(sim, me);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Malzahar (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let now = sim.tick();
        if let Some(t) = self.linger_until {
            if now >= t {
                self.break_shift(sim, me, now);
            }
        } else if !self.ready && now >= shift_back_at(self.broken_at, self.last_champion_hit, self.p.p_cd) {
            self.arm(sim, me);
            if let Some(k) = counted("back") {
                wlog(format!("{} SHIFT #{k}: Void Shift ready again", head(sim, me)));
            }
        }
        self.visions(sim, me, now);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        if damage == 0 || attacker == me {
            return;
        }
        let Some(a) = sim.get_entity(attacker) else { return };
        let (champ, minion) = (a.is_champion(), a.is_minion());
        let now = sim.tick();
        if champ {
            self.last_champion_hit = Some(now);
        }
        if self.ready && !minion && self.linger_until.is_none() {
            self.linger_until = Some(now + self.p.p_linger);
            if let Some(k) = counted("hit") {
                wlog(format!("{} SHIFT #{k}: struck by {} ({damage}), Void Shift fades in {} ticks", head(sim, me),
                             who(sim, attacker), self.p.p_linger));
            }
        }
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        self.ready = false;
        self.linger_until = None;
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Malzahar: Void Shift as in League, Malefic Visions jumping on every death) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:vision"), Step(vision_hit));
    module.add_native_passive(format!("{ID}:void"), Void::default());
    host.log(LogLevel::Info, "league_malzahar loaded (Void Shift as in League, Malefic Visions jumping on every death).");
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
    fn a_part_of_the_vision() {
        let p = Params::default();
        assert_eq!(part_damage(&p, 0), 170 / 16);
        assert_eq!(part_damage(&p, 200), (170 + 160) / 16);
        assert_eq!(part_damage(&Params { e_dmg: 0, e_ap: 0, ..p }, 0), 1);
    }

    #[test]
    fn void_shift_waits_for_the_last_champion_hit() {
        assert_eq!(shift_back_at(100, None, 720), 820);
        assert_eq!(shift_back_at(100, Some(50), 720), 820);
        assert_eq!(shift_back_at(100, Some(400), 720), 1120);
    }

    #[test]
    fn the_jump_prefers_champions_in_reach() {
        let r = 40_000u64;
        let near_minion = (7, false, 100u64);
        let far_champ = (3, true, (r + 1) * (r + 1));
        let champ = (5, true, 30_000u64 * 30_000);
        assert_eq!(pick_jump(&[near_minion, champ], r), Some(5));
        assert_eq!(pick_jump(&[near_minion, far_champ], r), Some(7));
        assert_eq!(pick_jump(&[far_champ], r), None);
        assert_eq!(pick_jump(&[], r), None);
        let a = (9, true, 400u64);
        let b = (2, true, 400u64);
        assert_eq!(pick_jump(&[a, b], r), Some(2));
    }

    #[test]
    fn params_parse() {
        let p = parse_params(r#"{"e_ap":80,"e_dmg":170,"e_jump":40000,"e_p":15,"e_t":240,"p_cd":720,"p_dr":90,"p_linger":15}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_malzahar.py");
        let src = std::fs::read_to_string(path).expect("build_malzahar.py");
        let d = Params::default();
        for (key, v) in [("p_cd", d.p_cd), ("p_linger", d.p_linger), ("p_dr", d.p_dr), ("e_t", d.e_t), ("e_p", d.e_p),
                         ("e_dmg", d.e_dmg), ("e_ap", d.e_ap), ("e_jump", d.e_jump)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_malzahar.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["p_shift", "e_markb", "e_jump"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }
}
