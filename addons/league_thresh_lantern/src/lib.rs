//! 锤石附加包：W「魂引之灯」照英雄联盟把有危险的队友拉回来（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话
//! 全部补附加包」）。
//!
//! 主包是纯数据：引擎做不了「队友点灯笼」，灯笼飞向 50000 内一名随机友方英雄，只给护盾。英雄联盟里锤石把灯笼扔给挨打的
//! 队友，队友点一下就被拉到锤石身边。本包：副本里那段随机挑人换成原生效果 `league_thresh_lantern:throw`——
//!
//! - **挑谁**：`REACH` 内的友方英雄（不含锤石），先挑有危险的（生命不高于 `LOW`%、或身边 `CROWD_R` 内有 `CROWD` 个以上
//!   敌方英雄），几个时挑生命比例最低的；都没危险就挑最近的。
//! - **灯笼**：主包的灯笼（`league_thresh_w_lantern`）飞过去，到了由 `league_thresh_lantern:land` 给他主包那份护盾
//!   （60 + 40% 锤石法强，2.5 秒，护盾画面 `league_thresh_w_shield`、声音）。
//! - **拉回来**：他有危险、离锤石超过 `NEAR`、没被硬控时，把他拉到锤石身边（`entity_pull`，每 tick `PULL_SPEED`）。
//! - **两张 5v5 地图**（2026-11-10）：灯笼从锤石站的地方飞出，夹在这一场的地图里（`game_places::terrain::map_of_sim`：游戏
//!   自己的 960000 见方，Rin 的召唤师峡谷 1614545 见方；以前一律按 960000，峡谷上过了 960000 就从半张图的边上飞出来）。
//!
//! 0.2.0（用户 2026-11-22：「锤石的灯笼是不是完全没有 我是没见过」，选了「照英雄联盟做」）：灯笼以前每 tick 飞 5000（主包的
//! 速度），两三万远一眨眼就到，落地只剩护盾，画面上从来没有灯。现在照英雄联盟：
//!
//! - 灯笼每 tick 飞 `FLY`，两三万远要飞小半秒，看得见；落地照旧给护盾。
//! - 落地后在他身边（往锤石那边挪 `OFFSET`，不压在他脚下）立一盏灯，留 `LIFE` tick（6 秒）。这期间灯边上 `GRAB_R` 以内有
//!   队友有危险（同上面的条件），就当他点了灯：拉到锤石身边，灯随即没了。灯在不在记在锤石身上的 buff `UP` 上：用掉就去掉，
//!   到时间自己没。
//! - 地上的灯是主包锤石特效图里的 `w_ground`（`league_thresh_w_ground`，一段 0.6 秒）：落地播一段，之后每 `WATCH` tick
//!   （0.5 秒）看一次灯，还在就再播一段。数据里的画面只能整段播完、中途收不回来，所以这样切成小段：灯被用掉或到时间就不再
//!   播，最多 0.1 秒就没了；一段比间隔长 0.1 秒、最后一帧和第一帧一样，两段接上的地方看不出来。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_thresh_lantern.log`。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use game_places::terrain::{map_of_sim, rift_status, Map};
use mod_api_stable::*;
// 灯笼扔多远、飞多快、拉人多快在大地图版跟着乘 1.3（扔的距离、飞的时间和主包数据一致）
use game_places::skill_scale::sk;

const ID: &str = "league_thresh_lantern";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_thresh_lantern") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const LANTERN: &str = "league_thresh_w_lantern";
pub const SHIELD_VIEW: &str = "league_thresh_w_shield";
pub const SHIELD_SFX: &str = "league_thresh_w_shield";
/// 地上那盏灯（副本数据里的画面，主包锤石特效图的 `w_ground`）。
pub const GROUND: &str = "league_thresh_w_ground";
/// 锤石身上「地上有灯」的 buff。
pub const UP: &str = "league_thresh_lantern_up";
/// 灯笼扔多远（主包的 `RandomTarget` 是 50000）；主包的灯笼飞多快（make_override.py 拿它和主包对照，本包不用它飞）。
pub const REACH: f64 = 50_000.0;
pub const SPEED: u64 = 5_000;
/// 本包的灯笼飞多快：两三万远飞 15–25 tick，英雄联盟里灯笼飞过去也是小半秒。
pub const FLY: u64 = 1_400;
/// 灯落在队友身边、往锤石那边挪多远（不压在他脚下）；灯在地上留多久（英雄联盟 6 秒）；多久看一次灯（同时重播一段画面）；
/// 离灯多近的队友碰得到它。
pub const OFFSET: f64 = 14_000.0;
pub const LIFE: usize = 360;
pub const WATCH: usize = 30;
pub const GRAB_R: f64 = 20_000.0;
/// 主包的护盾：60 + 40% 法强，150 tick。
pub const SHIELD: usize = 60;
pub const SHIELD_AP: usize = 40;
pub const SHIELD_TICKS: usize = 150;
pub const LOW: usize = 45;
pub const CROWD: usize = 2;
pub const CROWD_R: f64 = 25_000.0;
/// 离锤石这么近就不拉；拉到离他这么近停下。
pub const NEAR: f64 = 15_000.0;
pub const STOP: f64 = 8_000.0;
pub const PULL_SPEED: usize = 3_000;
/// 游戏自己的 5v5 地图边长；峡谷的看 `Map::extent`。
const MAP: f64 = 960_000.0;
const HARD_CC: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                                CcKindV1::Charm, CcKindV1::ForceMove];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNT: Mutex<usize> = Mutex::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_THRESH_LANTERN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_thresh_lantern.log");
        }
    }
    PathBuf::from("league_thresh_lantern.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
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

/// Log the first 120 and every 25th after.
fn counted() -> Option<usize> {
    let mut n = COUNT.lock().unwrap_or_else(|e| e.into_inner());
    *n += 1;
    (*n <= 120 || *n % 25 == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>, me: usize) -> String {
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
    format!("[{kind} m={} s={}] t={} #{me}", m(o.match_id), m(o.set_index), sim.tick())
}

/// 这次启动已经在日志里说过峡谷了。
static RIFT_TOLD: AtomicBool = AtomicBool::new(false);

/// 这一场的地图；第一次碰到峡谷（一次启动）时日志写一行。
fn map_here(sim: &StableSim<'_>) -> Map {
    let map = map_of_sim(sim);
    if map == Map::Rift && !RIFT_TOLD.swap(true, Ordering::Relaxed) {
        wlog(format!("== Rift: the lantern flies from where Thresh stands on the Rift's {:.0} square (not the game's own \
                      {MAP:.0}); {} ==", map.extent(), rift_status()));
    }
    map
}

// ===================== 挑人 =====================

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// An ally in reach: id, where, hp, max, enemy champions within `CROWD_R`.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Ally {
    pub id: usize,
    pub at: Pt,
    pub hp: usize,
    pub max: usize,
    pub crowd: usize,
}

impl Ally {
    pub fn danger(&self) -> bool {
        self.hp * 100 <= LOW * self.max.max(1) || self.crowd >= CROWD
    }
}

/// Whom the lantern goes to: the one in danger with the lowest health share, else the nearest to Thresh at `me`.
pub fn pick(me: Pt, allies: &[Ally]) -> Option<Ally> {
    let share = |a: &Ally| a.hp * 1000 / a.max.max(1);
    allies.iter().filter(|a| a.danger()).min_by_key(|a| share(a)).copied()
        .or_else(|| allies.iter().min_by(|a, b| dist(me, a.at).total_cmp(&dist(me, b.at))).copied())
}

/// Ticks to pull an ally from `d` away to `STOP` from Thresh (0: no pull).
pub fn pull_ticks(d: f64) -> usize {
    if d <= NEAR {
        return 0;
    }
    ((d - STOP) / sk(PULL_SPEED) as f64).ceil().max(1.0) as usize
}

/// 灯放在哪：队友 `ally` 身边，往锤石 `me` 那边挪 `OFFSET`（两人挨得近就挪一半的距离）。
pub fn spot_by(ally: Pt, me: Pt) -> Pt {
    let d = dist(ally, me);
    if d < 1.0 {
        return ally;
    }
    let k = OFFSET.min(d / 2.0) / d;
    (ally.0 + (me.0 - ally.0) * k, ally.1 + (me.1 - ally.1) * k)
}

/// 谁来点灯：灯 `spot` 边上 `GRAB_R` 以内、有危险、离锤石 `me` 够远（`pull_ticks` 不为 0）、没被硬控（`held`）的队友里
/// 生命比例最低的。-> (他, 拉几 tick)。
pub fn grabber(me: Pt, spot: Pt, allies: &[Ally], held: impl Fn(usize) -> bool) -> Option<(Ally, usize)> {
    allies.iter()
        .filter(|a| dist(a.at, spot) <= sk(GRAB_R) && a.danger() && !held(a.id))
        .map(|a| (*a, pull_ticks(dist(me, a.at))))
        .filter(|&(_, t)| t > 0)
        .min_by_key(|(a, _)| a.hp * 1000 / a.max.max(1))
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

/// A spot on `map` in whole units (the lantern's start).
fn upos(map: Map, p: Pt) -> (u64, u64) {
    let e = map.extent();
    (p.0.round().clamp(0.0, e - 1.0) as u64, p.1.round().clamp(0.0, e - 1.0) as u64)
}

fn hard_cc(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

fn read_allies(sim: &StableSim<'_>, me: usize) -> Option<(Pt, Vec<Ally>)> {
    let e = sim.get_entity(me)?;
    let (team, at) = (e.team(), pos(&e));
    let units: Vec<_> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|u| u.is_champion() && u.is_alive()).collect();
    let allies = units.iter()
        .filter(|u| u.team() == team && u.id() != me && u.is_targetable() && dist(at, pos(u)) <= sk(REACH))
        .map(|u| Ally {
            id: u.id(),
            at: pos(u),
            hp: u.hp().0,
            max: u.hp().1,
            crowd: units.iter().filter(|f| f.team() != team && dist(pos(u), pos(f)) <= CROWD_R).count(),
        })
        .collect();
    Some((at, allies))
}

// ===================== 原生效果 =====================

struct Throw;

impl StableEffectType for Throw {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _input: InputTargetV1) {
        let Some((at, allies)) = read_allies(sim, caster) else { return };
        let Some(a) = pick(at, &allies) else { return };
        let Some(team) = sim.get_entity(caster).map(|e| e.team()) else { return };
        let (x, y) = upos(map_here(sim), at);
        let spec = ProjectileSpawnV1 {
            caster_id: caster,
            team,
            x,
            y,
            radius: 1_000,
            speed: sk(FLY),
            move_kind: ProjectileMoveKindV1::Target.code(),
            target_id: a.id,
            target_x: 0,
            target_y: 0,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::AllyChampion.code(),
        };
        let flew = sim.spawn_projectile(LANTERN, &format!("{ID}:land"), &spec);
        if let Some(k) = counted() {
            wlog(format!("{} LANTERN #{k} -> #{} (hp {}/{}, {} enemies around, {:.0} away){}{}", head(sim, caster), a.id, a.hp,
                         a.max, a.crowd, dist(at, a.at), if a.danger() { " IN DANGER" } else { "" },
                         if flew { "" } else { " (spawn_projectile refused)" }));
        }
    }
}

struct Land;

impl StableEffectType for Land {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Target.code() {
            return;
        }
        let id = input.target_id;
        let Some(me) = sim.get_entity(caster) else { return };
        let (power, at, alive) = (me.stat().magic_power, pos(&me), me.is_alive());
        let Some(a) = sim.get_entity(id).filter(|e| e.is_alive()) else { return };
        let there = pos(&a);
        sim.entity_add_shield(id, SHIELD + power * SHIELD_AP / 100, SHIELD_TICKS);
        let mut view = BuffV1::named(SHIELD_VIEW);
        view.duration_kind = BuffDurationV1::WithShield.code();
        sim.add_buff(id, &view);
        sim.play_sfx(SHIELD_SFX, caster, &InputTargetV1::target(id));
        // 灯立在他身边，留 LIFE tick
        let (x, y) = upos(map_here(sim), spot_by(there, at));
        let spot = InputTargetV1::pos(x, y);
        let shown = sim.play_view_effect(GROUND, caster, &spot, 0, 0, 0);
        sim.add_buff(caster, &BuffV1::timed(UP, LIFE));
        if let Some(k) = counted() {
            wlog(format!("{} LANDED #{k} on #{id}: shield {}, lantern down at ({x}, {y}) for {LIFE} ticks{}",
                         head(sim, caster), SHIELD + power * SHIELD_AP / 100,
                         if shown { "" } else { " (the view effect was refused)" }));
        }
        // 他这会儿就有危险：当场点灯，不用再看
        if alive && grab(sim, caster, (x as f64, y as f64)) {
            return;
        }
        if !sim.queue_effect(&format!("{ID}:watch"), AttackTypeV1::Skill, caster, &spot, WATCH) {
            wlog(format!("{} queue_effect({ID}:watch) refused: the lantern stays one piece long", head(sim, caster)));
        }
    }
}

/// 灯边上有人点灯：拉他过来，灯没了（去掉 `UP`）。-> 拉了没有。
fn grab(sim: &mut StableSim<'_>, caster: usize, spot: Pt) -> bool {
    let Some(at) = sim.get_entity(caster).map(|e| pos(&e)) else { return false };
    let Some((_, allies)) = read_allies(sim, caster) else { return false };
    let held: Vec<usize> = allies.iter().filter(|a| sim.get_entity(a.id).is_some_and(|e| hard_cc(&e))).map(|a| a.id).collect();
    let Some((a, ticks)) = grabber(at, spot, &allies, |id| held.contains(&id)) else { return false };
    let pulled = sim.entity_pull(caster, a.id, sk(PULL_SPEED), ticks);
    if pulled {
        sim.entity_remove_buff(caster, UP);
    }
    if let Some(k) = counted() {
        wlog(format!("{} GRAB #{k}: #{} (hp {}/{}, {} enemies around) took the lantern: {}", head(sim, caster), a.id,
                     a.hp, a.max, a.crowd,
                     if pulled { format!("pulled {:.0} in {ticks} ticks", dist(at, a.at)) } else { "the pull was refused".into() }));
    }
    pulled
}

/// 每 `WATCH` tick 看一次地上的灯：还在就看有没有人点灯，没人点就再播一段灯、接着看。
struct Watch;

impl StableEffectType for Watch {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if input.kind != InputTargetKindV1::Pos.code() {
            return;
        }
        // 用掉了、到时间了、锤石倒了：不再播，最多 0.1 秒灯就没了
        if !sim.get_entity(caster).is_some_and(|e| e.is_alive() && has_buff(&e, UP)) {
            return;
        }
        if grab(sim, caster, (input.x as f64, input.y as f64)) {
            return;
        }
        sim.play_view_effect(GROUND, caster, &input, 0, 0, 0);
        sim.queue_effect(&format!("{ID}:watch"), AttackTypeV1::Skill, caster, &input, WATCH);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Thresh's lantern lands by the ally in danger and stays 6 s; whoever takes it in danger is pulled to him) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:throw"), Throw);
    module.add_native_effect(format!("{ID}:land"), Land);
    module.add_native_effect(format!("{ID}:watch"), Watch);
    host.log(LogLevel::Info, "league_thresh_lantern v1 loaded (Dark Passage pulls the ally in danger).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    fn a(id: usize, x: f64, hp: usize, crowd: usize) -> Ally {
        Ally { id, at: (x, 0.0), hp, max: 1000, crowd }
    }

    #[test]
    fn the_lantern_goes_to_the_ally_in_danger_else_the_nearest() {
        assert_eq!(pick((0.0, 0.0), &[a(1, 10_000.0, 900, 0), a(2, 40_000.0, 400, 0), a(3, 30_000.0, 300, 0)]).map(|x| x.id),
                   Some(3));
        assert_eq!(pick((0.0, 0.0), &[a(1, 10_000.0, 900, 0), a(2, 40_000.0, 800, 2)]).map(|x| x.id), Some(2));
        assert_eq!(pick((0.0, 0.0), &[a(1, 30_000.0, 900, 0), a(2, 20_000.0, 800, 1)]).map(|x| x.id), Some(2));
        assert_eq!(pick((0.0, 0.0), &[]), None);
    }

    #[test]
    fn far_allies_are_pulled_near_ones_not() {
        assert_eq!(pull_ticks(10_000.0), 0);
        assert_eq!(pull_ticks(44_000.0), 12);
    }

    #[test]
    fn the_lantern_starts_where_thresh_stands_on_either_map() {
        // the game's own map: held at its edge, as before
        assert_eq!(upos(Map::Native, (970_000.4, -3.0)), (MAP as u64 - 1, 0));
        // the Rift: past 960000 is where he stands, its own edge at 1614545
        assert_eq!(upos(Map::Rift, (1_300_000.4, 1_500_000.0)), (1_300_000, 1_500_000));
        assert_eq!(upos(Map::Rift, (2_000_000.0, 5.0)), (Map::Rift.extent() as u64 - 1, 5));
    }

    /// 0.2.0：灯落在队友身边、往锤石那边挪一点，不压在他脚下；两人挨得近就挪一半。
    #[test]
    fn the_lantern_lands_beside_the_ally_toward_thresh() {
        let s = spot_by((40_000.0, 0.0), (0.0, 0.0));
        assert!((s.0 - (40_000.0 - OFFSET)).abs() < 1e-6 && s.1.abs() < 1e-6, "{s:?}");
        assert_eq!(spot_by((10_000.0, 0.0), (0.0, 0.0)), (5_000.0, 0.0));
        assert_eq!(spot_by((3.0, 4.0), (3.0, 4.0)), (3.0, 4.0));
    }

    /// 0.2.0：灯在地上的 6 秒里，灯边上有危险、离锤石够远、没被硬控的队友点灯，几个时生命比例最低的先。
    #[test]
    fn whoever_is_in_danger_by_the_lantern_takes_it() {
        let me = (0.0, 0.0);
        let spot = (40_000.0, 0.0);
        let free = |_: usize| false;
        // 灯边上、有危险、离锤石 4.5 万：拉，拉 13 tick
        assert_eq!(grabber(me, spot, &[a(1, 45_000.0, 300, 0)], free).map(|(x, t)| (x.id, t)), Some((1, 13)));
        // 没危险、离灯太远、离锤石太近、被硬控：都不拉
        assert_eq!(grabber(me, spot, &[a(1, 45_000.0, 900, 0)], free), None);
        assert_eq!(grabber(me, spot, &[a(1, 40_000.0 + GRAB_R + 1.0, 300, 0)], free), None);
        assert_eq!(grabber(me, (12_000.0, 0.0), &[a(1, 12_000.0, 300, 0)], free), None);
        assert_eq!(grabber(me, spot, &[a(1, 45_000.0, 300, 0)], |id| id == 1), None);
        // 两个都能点：生命比例低的先
        let two = [a(1, 42_000.0, 400, 0), a(2, 38_000.0, 200, 2)];
        assert_eq!(grabber(me, spot, &two, free).map(|(x, _)| x.id), Some(2));
    }
}
