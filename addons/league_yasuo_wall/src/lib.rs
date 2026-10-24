//! 亚索附加包：W「风之障壁」（用户 2026-10-24：「还有个亚索风墙吧？但是亚索风墙要智能点放啊」）。
//!
//! 主包没有 W：游戏里没有能挡掉飞行物的效果，只画一面墙显得奇怪，用户当时决定删掉（主包 README）。亚索也没有空的技能格。本包
//! 用原生代码做（被动 `league_yasuo_wall:wall`，不占技能格、没有施法动作，英雄联盟的 W 也只是一挥手）：
//!
//! - **什么时候放（智能）**：墙好了（冷却 `CD`，`MIN_LEVEL` 级起），亚索没被硬控，而且敌方英雄的飞行物正朝亚索或 `GUARD_R`
//!   内的队友飞来、`NEAR`–`FAR` 之内就要打到：这样的飞行物 ≥ `MANY` 个，或者有一个是冲着生命不高于 `LOW`% 的人去的，才放。
//!   飞行物的方向由它这一 tick 和上一 tick 的位置算（按施放者配对）。
//! - **放在哪**：亚索身前 `AHEAD`，朝着来袭飞行物的平均方向，墙和这个方向垂直，长 2 × `HALF`，中间往敌人那边鼓 `BOW`
//!   （英雄联盟的弧形墙），`LIFE` tick。
//! - **画面像英雄联盟**（用户：「跟着方向转有点奇怪啊风墙 做成像英雄联盟那样啊」）：墙脚是地上的一条线，跟着墙的方向；风永远
//!   往上升，图不转。Codex 画的墙切成 `PIECES` 段竖着的风（`tools/art/import_yasuo_wall.py`），沿墙脚从屏幕左到右（竖着的墙
//!   从上到下）一段段摆开，墙脚每 `DOT` 放一个地上的小点；出手时他脚下卷起一阵风（`CAST_PIC`），挡住飞行物的地方一道青白的
//!   光（`BLOCK_PIC`），墙到时间在第 1、3、5 段散开（`FADE_PIC`）。
//! - **挡住**：敌方英雄的飞行物这一 tick 从墙的这一边穿到那一边，就算被挡：在穿过的地方播挡住的画面。引擎删不掉飞行物，
//!   所以之后它打到的友方英雄（它经过的路线 `HIT_R` 内、这一 tick 掉了血的）把这一下的伤害补回去（`heal`），这一 tick 新挂上的
//!   控制也清掉（`entity_clear_cc`）。塔的炮弹不挡（英雄联盟也不挡）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_yasuo_wall.log`。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_yasuo_wall";
pub const CD: usize = 1_200;
pub const MIN_LEVEL: usize = 2;
pub const LIFE: usize = 240;
pub const AHEAD: f64 = 24_000.0;
pub const BOW: f64 = 5_000.0;
pub const PIECES: usize = 7;
pub const DOT: f64 = 1_600.0;
pub const HALF: f64 = 22_000.0;
pub const GUARD_R: f64 = 50_000.0;
pub const NEAR: f64 = 4_000.0;
pub const FAR: f64 = 32_000.0;
pub const MANY: usize = 2;
pub const LOW: usize = 40;
pub const HIT_R: f64 = 12_000.0;
/// 上一 tick 和这一 tick 的同一个飞行物最多差这么远（最快的飞行物每 tick 约 20000）。
pub const MATCH_R: f64 = 30_000.0;
/// 墙的画面：`PIECE_PIC` + 段号（`plume_0`..`plume_6`），墙脚的小点。
pub const PIECE_PIC: &str = "league_yasuo_w_plume_";
pub const GROUND_PIC: &str = "league_yasuo_w_ground";
/// 出手时他脚下的风（跟着他）、挡住飞行物的一下（在穿过的地方）、墙散掉（墙到时间时，在第 1、3、5 段的地方）。
pub const CAST_PIC: &str = "league_yasuo_w_cast";
pub const BLOCK_PIC: &str = "league_yasuo_w_block";
pub const FADE_PIC: &str = "league_yasuo_w_fade";
const MAP: f64 = 960_000.0;
const HARD_CC: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                                CcKindV1::Charm, CcKindV1::ForceMove];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_YASUO_WALL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_yasuo_wall.log");
        }
    }
    PathBuf::from("league_yasuo_wall.log")
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

// ===================== 几何 =====================

pub type Pt = (f64, f64);

fn sub(a: Pt, b: Pt) -> Pt {
    (a.0 - b.0, a.1 - b.1)
}

fn add(a: Pt, b: Pt) -> Pt {
    (a.0 + b.0, a.1 + b.1)
}

fn mul(a: Pt, k: f64) -> Pt {
    (a.0 * k, a.1 * k)
}

fn dot(a: Pt, b: Pt) -> f64 {
    a.0 * b.0 + a.1 * b.1
}

fn cross(a: Pt, b: Pt) -> f64 {
    a.0 * b.1 - a.1 * b.0
}

fn len(a: Pt) -> f64 {
    dot(a, a).sqrt()
}

fn unit(a: Pt) -> Option<Pt> {
    let l = len(a);
    (l > 1e-6).then(|| (a.0 / l, a.1 / l))
}

/// Where segment p0-p1 crosses segment q0-q1, if it does.
pub fn crossing(p0: Pt, p1: Pt, q0: Pt, q1: Pt) -> Option<Pt> {
    let r = sub(p1, p0);
    let s = sub(q1, q0);
    let d = cross(r, s);
    if d.abs() < 1e-9 {
        return None;
    }
    let t = cross(sub(q0, p0), s) / d;
    let u = cross(sub(q0, p0), r) / d;
    ((0.0..=1.0).contains(&t) && (0.0..=1.0).contains(&u)).then(|| add(p0, mul(r, t)))
}

/// Distance from `p` to segment a-b.
pub fn seg_dist(p: Pt, a: Pt, b: Pt) -> f64 {
    let ab = sub(b, a);
    let l2 = dot(ab, ab);
    if l2 < 1e-9 {
        return len(sub(p, a));
    }
    let t = (dot(sub(p, a), ab) / l2).clamp(0.0, 1.0);
    len(sub(p, add(a, mul(ab, t))))
}

/// A flying missile this tick: who threw it, where it was, where it is.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Missile {
    pub caster: usize,
    pub from: Pt,
    pub at: Pt,
}

/// Pair this tick's missiles with last tick's (same caster, nearest within `MATCH_R`); a new one starts where it is.
pub fn pair(prev: &[(usize, Pt)], now: &[(usize, Pt)]) -> Vec<Missile> {
    let mut used = vec![false; prev.len()];
    now.iter()
        .map(|&(c, at)| {
            let best = prev.iter().enumerate()
                .filter(|(i, p)| !used[*i] && p.0 == c && len(sub(p.1, at)) <= MATCH_R)
                .min_by(|a, b| len(sub(a.1 .1, at)).total_cmp(&len(sub(b.1 .1, at))))
                .map(|(i, _)| i);
            let from = best.map_or(at, |i| {
                used[i] = true;
                prev[i].1
            });
            Missile { caster: c, from, at }
        })
        .collect()
}

/// An ally (or Yasuo): id, where, health share in per mille.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Guarded {
    pub id: usize,
    pub at: Pt,
    pub share: usize,
}

/// The missile's mark: the guarded one it flies at, `NEAR`..`FAR` away (None: not a threat).
pub fn aimed_at(m: &Missile, guarded: &[Guarded]) -> Option<Guarded> {
    let v = unit(sub(m.at, m.from))?;
    guarded.iter().copied().filter(|g| {
        let to = sub(g.at, m.at);
        let d = len(to);
        (NEAR..=FAR).contains(&d) && dot(v, to) >= 0.9 * d
    }).min_by(|a, b| len(sub(a.at, m.at)).total_cmp(&len(sub(b.at, m.at))))
}

/// Raise the wall now? Where (its middle, the direction the missiles come from, unit): from the missiles aimed at the
/// guarded ones round Yasuo at `me`.
pub fn plan(me: Pt, missiles: &[Missile], guarded: &[Guarded]) -> Option<(Pt, Pt, usize)> {
    let threats: Vec<(Missile, Guarded)> = missiles.iter().filter_map(|m| aimed_at(m, guarded).map(|g| (*m, g))).collect();
    let low = threats.iter().any(|(_, g)| g.share * 100 <= LOW * 1000);
    if threats.len() < MANY && !low {
        return None;
    }
    let toward = threats.iter().fold((0.0, 0.0), |s, (m, _)| add(s, unit(sub(m.at, me)).unwrap_or((0.0, 0.0))));
    let dir = unit(toward)?;
    Some((add(me, mul(dir, AHEAD)), dir, threats.len()))
}

/// Along the wall: the side vector, pointing left to right on screen (top to bottom when the wall stands up and down).
pub fn side_of(dir: Pt) -> Pt {
    let s = (-dir.1, dir.0);
    if s.0 < 0.0 || (s.0.abs() < 1e-9 && s.1 < 0.0) { mul(s, -1.0) } else { s }
}

/// The point at `t` (-1 .. 1) along the bowed wall.
pub fn along(mid: Pt, dir: Pt, t: f64) -> Pt {
    add(add(mid, mul(side_of(dir), HALF * t)), mul(dir, BOW * (1.0 - t * t)))
}

/// The wall's line as a polyline (for the blocking test).
pub fn line(mid: Pt, dir: Pt) -> Vec<Pt> {
    (0..=8).map(|i| along(mid, dir, -1.0 + i as f64 / 4.0)).collect()
}

/// Where the pieces of wind stand (piece k from the left), and the ground dots.
pub fn pieces(mid: Pt, dir: Pt) -> (Vec<Pt>, Vec<Pt>) {
    let n = PIECES as f64;
    let plumes = (0..PIECES).map(|k| along(mid, dir, -1.0 + (2.0 * k as f64 + 1.0) / n)).collect();
    let dots = (2.0 * HALF / DOT) as usize + 1;
    let ground = (0..dots).map(|i| along(mid, dir, -1.0 + 2.0 * i as f64 / (dots - 1) as f64)).collect();
    (plumes, ground)
}

// ===================== 被动 =====================

#[derive(Clone, Copy, Debug)]
struct Wall {
    mid: Pt,
    dir: Pt,
    until: usize,
}

#[derive(Clone, Default)]
struct WallPassive {
    /// 上一 tick 敌方英雄的飞行物（施放者、位置）。
    prev: Vec<(usize, Pt)>,
    /// 被墙挡住、还在飞的飞行物（施放者、位置）。
    blocked: Vec<(usize, Pt)>,
    wall: Option<Wall>,
    ready_at: usize,
    /// 上一 tick 友方英雄的生命和控制数。
    seen: HashMap<usize, (usize, usize)>,
    walls: usize,
    stops: usize,
    saved: usize,
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn hard_cc(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| HARD_CC.iter().any(|k| k.code() == c.kind)))
}

fn upos(p: Pt) -> (u64, u64) {
    (p.0.round().clamp(0.0, MAP - 1.0) as u64, p.1.round().clamp(0.0, MAP - 1.0) as u64)
}

impl WallPassive {
    fn raise(&mut self, sim: &mut StableSim<'_>, me: usize, mid: Pt, dir: Pt, n: usize) {
        let tick = sim.tick();
        self.wall = Some(Wall { mid, dir, until: tick + LIFE });
        self.ready_at = tick + CD;
        let (plumes, ground) = pieces(mid, dir);
        for p in ground {
            let (x, y) = upos(p);
            sim.play_view_effect(GROUND_PIC, me, &InputTargetV1::pos(x, y), 0, 0, 0);
        }
        sim.play_view_effect(CAST_PIC, me, &InputTargetV1::target(me), 0, 0, 0);
        let mut shown = 0;
        for (k, p) in plumes.iter().enumerate() {
            let (x, y) = upos(*p);
            shown += sim.play_view_effect(&format!("{PIECE_PIC}{k}"), me, &InputTargetV1::pos(x, y), 0, 0, 0) as usize;
        }
        self.walls += 1;
        if self.walls <= 80 {
            wlog(format!("{} WALL #{} at ({:.0}, {:.0}) facing ({:.2}, {:.2}): {n} missiles coming, {shown} of {PIECES} pieces shown",
                         head(sim, me), self.walls, mid.0, mid.1, dir.0, dir.1));
        }
    }
}

impl StablePassive for WallPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.wall = None;
        self.blocked.clear();
        wlog(format!("{} SPAWN: the add-on's Yasuo (player {player}), Wind Wall ready at t={}", head(sim, me), self.ready_at));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (team, at, alive, held, (hp, max)) = (e.team(), pos(&e), e.is_alive(), hard_cc(&e), e.hp());
        let level = sim.get_player(player).map_or(1, |p| p.level());
        let champs: Vec<(usize, usize, Pt, (usize, usize), usize)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.is_alive())
            .map(|u| (u.id(), u.team(), pos(&u), u.hp(), u.cc_count()))
            .collect();
        let enemy_champ = |id: usize| champs.iter().any(|c| c.0 == id && c.1 != team);
        let now: Vec<(usize, Pt)> = (0..sim.projectile_count()).filter_map(|i| sim.projectile_at(i))
            .filter(|p| p.team != team && !p.is_end && enemy_champ(p.caster_id))
            .map(|p| (p.caster_id, (p.x as f64, p.y as f64)))
            .collect();
        let missiles = pair(&self.prev, &now);
        // the wall stops what crosses it, then goes (its pictures last as long)
        let mut newly = Vec::new();
        if let Some(w) = self.wall {
            let pl = line(w.mid, w.dir);
            for m in &missiles {
                if self.blocked.iter().any(|q| q.0 == m.caster && len(sub(q.1, m.from)) < 1.0) {
                    continue;
                }
                if let Some(p) = pl.windows(2).find_map(|s| crossing(m.from, m.at, s[0], s[1])) {
                    newly.push((m.caster, m.at, p));
                }
            }
            if tick >= w.until {
                let (plumes, _) = pieces(w.mid, w.dir);
                for p in plumes.iter().skip(1).step_by(2) {
                    let (x, y) = upos(*p);
                    sim.play_view_effect(FADE_PIC, me, &InputTargetV1::pos(x, y), 0, 0, 0);
                }
                self.wall = None;
            }
        }
        for (c, now_at, p) in newly {
            let (x, y) = upos(p);
            sim.play_view_effect(BLOCK_PIC, me, &InputTargetV1::pos(x, y), 0, 0, 0);
            self.stops += 1;
            if self.stops <= 120 {
                wlog(format!("{} BLOCKED #{}: a missile of #{c} at ({:.0}, {:.0})", head(sim, me), self.stops, p.0, p.1));
            }
            self.blocked.push((c, now_at));
        }
        // the blocked ones' paths this tick (still flying: from -> at; gone: where they were last)
        let mut paths: Vec<(Pt, Pt)> = Vec::new();
        let mut still = Vec::new();
        for &(c, last) in &self.blocked {
            match missiles.iter().find(|m| m.caster == c && len(sub(m.from, last)) < 1.0) {
                Some(m) => {
                    paths.push((m.from, m.at));
                    still.push((c, m.at));
                }
                None => paths.push((last, last)),
            }
        }
        self.blocked = still;
        // the damage and the new crowd control they did to allies: undone
        let mut seen = HashMap::new();
        for &(id, t, p, (h, _), cc) in champs.iter().filter(|c| c.1 == team) {
            if let Some(&(h0, cc0)) = self.seen.get(&id) {
                let lost = h0.saturating_sub(h);
                let near = paths.iter().any(|(a, b)| seg_dist(p, *a, *b) <= HIT_R);
                if lost > 0 && near {
                    sim.heal(me, id, lost);
                    if cc > cc0 {
                        sim.entity_clear_cc(id);
                    }
                    self.saved += lost;
                    if self.stops <= 120 {
                        wlog(format!("{} SAVED #{id}: {lost} damage given back{}", head(sim, me),
                                     if cc > cc0 { ", crowd control cleared" } else { "" }));
                    }
                }
            }
            let _ = t;
            seen.insert(id, (h, cc));
        }
        self.seen = seen;
        self.prev = now;
        // when to raise it
        if !alive || held || self.wall.is_some() || tick < self.ready_at || level < MIN_LEVEL {
            return;
        }
        let guarded: Vec<Guarded> = champs.iter()
            .filter(|c| c.1 == team && len(sub(c.2, at)) <= GUARD_R)
            .map(|c| Guarded { id: c.0, at: c.2, share: c.3 .0 * 1000 / c.3 .1.max(1) })
            .collect();
        let _ = (hp, max);
        if let Some((mid, dir, n)) = plan(at, &missiles, &guarded) {
            self.raise(sim, me, mid, dir, n);
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        // a wall already up stays until it fades (League's does too); nothing to forget
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Yasuo's Wind Wall, raised when missiles come) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:wall"), WallPassive::default());
    host.log(LogLevel::Info, "league_yasuo_wall v1 loaded (Wind Wall).");
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

    #[test]
    fn missiles_pair_by_caster_and_distance() {
        let m = pair(&[(7, (0.0, 0.0)), (8, (100_000.0, 0.0))], &[(7, (5_000.0, 0.0)), (9, (1.0, 1.0))]);
        assert_eq!(m[0].from, (0.0, 0.0));
        assert_eq!(m[1].from, (1.0, 1.0));
    }

    #[test]
    fn the_wall_goes_up_for_two_missiles_or_one_at_a_low_ally() {
        let me = (0.0, 0.0);
        let g = [Guarded { id: 1, at: (0.0, 0.0), share: 900 }, Guarded { id: 2, at: (0.0, 10_000.0), share: 300 }];
        let at_me = Missile { caster: 5, from: (-30_000.0, 0.0), at: (-20_000.0, 0.0) };
        let away = Missile { caster: 6, from: (-20_000.0, 0.0), at: (-30_000.0, 0.0) };
        assert_eq!(plan(me, &[at_me, away], &g), None);
        let (mid, dir, n) = plan(me, &[at_me, at_me], &g).unwrap();
        assert_eq!(n, 2);
        assert!(dir.0 < -0.99 && (mid.0 + AHEAD).abs() < 1e-6);
        let at_low = Missile { caster: 5, from: (-20_000.0, 10_000.0), at: (-15_000.0, 10_000.0) };
        assert!(plan(me, &[at_low], &g).is_some());
    }

    #[test]
    fn crossing_the_wall_is_seen() {
        let pl = line((-24_000.0, 0.0), (-1.0, 0.0));
        let hit = |p0: Pt, p1: Pt| pl.windows(2).any(|s| crossing(p0, p1, s[0], s[1]).is_some());
        assert!(hit((-40_000.0, 0.0), (-10_000.0, 0.0)));
        assert!(hit((-40_000.0, 20_000.0), (-10_000.0, 20_000.0)));
        assert!(!hit((-40_000.0, 30_000.0), (-10_000.0, 30_000.0)));
        let (plumes, ground) = pieces((0.0, 0.0), (1.0, 0.0));
        assert_eq!(plumes.len(), PIECES);
        assert!(plumes[0].1 < plumes[6].1 && plumes[3].0 > plumes[0].0); // top to bottom, bowed toward the enemy
        assert!(ground.len() > 20);
        assert!(seg_dist((0.0, 5_000.0), (-1.0, 0.0), (1.0, 0.0)) < 5_001.0);
    }
}
