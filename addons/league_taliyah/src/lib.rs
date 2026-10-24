//! 塔莉垭扩展包（用户 2026-10-24：「技能对了，继续接入（音效、文字、注册、扩展包）」）：墙幔立起的墙是真的地形。
//!
//! 主包是纯数据：数据造不出挡路的东西，墙幔的竖墙和横墙都只是一片区域，碰到的敌人减速 `r_slow`%（卡在墙边），竖墙
//! 立起时站在上面的被拖到她那一侧。`mod.override_info` 把主包的塔莉垭换成 `override/` 里的副本（tools/kit/build_taliyah.py
//! 的 native=1）：数据和主包一样，只是墙不再减速（区域还在，只当本包找墙的位置用），立墙时多挂两个标记，`passive` 挂本包的
//! `league_taliyah:wall`：
//!
//! - **竖墙**（目标近、或她已在打架）：她身上新出现 `league_taliyah_wall_up` 的那一 tick，带 `league_taliyah_aim` 的敌方英雄
//!   （墙幔的目标）站的地方就是墙心（数据的 `r_mark` 1 tick 落在它脚下，墙从那里立起）。竖着的长方形，宽 `r_w`、高 `r_h`，
//!   立 `r_t` tick；立起时站在墙上的单位推到她那一侧（主包的拖出一样）。
//! - **横墙**（骑墙）：她身上新出现 `league_taliyah_lay_up` 的那一 tick，数据从她脚下朝带 `aim` 的目标射出 `r_n` 根看不见的线，
//!   第 k 根飞 k×`r_seg` 停下，在那里铺一段 `r_seg`×`r_w` 的横墙。本包按她和目标的位置算出每一段的落点和到达的 tick，
//!   再对到她那几 tick 新放出、停着不动的区域上（线停在哪由引擎定，最多多飞一 tick 的 `r_lay_speed`）；对不上的到点就按算的
//!   位置立。每段立 `r_t` tick；铺下时压在上面的单位推到离得近的那一侧（上或下）。
//! - **挡路**：墙立着时，每个单位（英雄、小兵、野怪、召唤物，两边都算，她自己也算）的中心一进墙（长方形四边各加单位半径），
//!   就退回上一 tick 的位置，但保留顺着墙走的那一半（竖墙保留上下、横墙保留左右），绕着墙走不会被粘住。她骑墙
//!   （`league_taliyah_riding`）时不挡她：她站在墙顶上；跳下来那一 tick 她还在墙上，就推到近的一侧。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态都在被动自己身上（每局一份）。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_taliyah.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_taliyah";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";

/// 单位半径读不到时用的值。
pub const BODY: u64 = 6000;
/// 横墙一段到点后最多再等这么多 tick 对区域，过了就按算的位置立。
pub const LATE: usize = 3;
/// 两个投射物位置这么近算同一处。
pub const SAME: u64 = 200;

fn sn(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_TALIYAH_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_taliyah.log");
        }
    }
    PathBuf::from("league_taliyah.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (league_olaf_rage's lesson: opening it for every line stalled the simulation thread)
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

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 墙立多久（tick）。
    pub r_t: usize,
    /// 竖墙的宽、高；横墙一段的高是 `r_w`。
    pub r_w: u64,
    pub r_h: u64,
    /// 横墙一段的长（也是相邻两段的间距）、几段、铺墙的线飞多快。
    pub r_seg: u64,
    pub r_n: usize,
    pub r_lay_speed: u64,
}

impl Default for Params {
    fn default() -> Self {
        Params { r_t: 300, r_w: 12000, r_h: 120000, r_seg: 26000, r_n: 6, r_lay_speed: 8000 }
    }
}

/// `{"r_t":300,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        match k {
            "r_t" => p.r_t = v as usize,
            "r_w" => p.r_w = v,
            "r_h" => p.r_h = v,
            "r_seg" => p.r_seg = v,
            "r_n" => p.r_n = v as usize,
            "r_lay_speed" => p.r_lay_speed = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 墙的朝向：竖墙把压在上面的推到她那一侧（`left`：她在墙左边），横墙推到近的上下一侧。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Side {
    Upright { left: bool },
    Flat,
}

/// 一块墙：中心、半宽、半高、拆掉的 tick、朝向。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Wall {
    pub x: u64,
    pub y: u64,
    pub hw: u64,
    pub hh: u64,
    pub until: usize,
    pub side: Side,
}

impl Wall {
    pub fn upright(p: &Params, (x, y): (u64, u64), left: bool, until: usize) -> Wall {
        Wall { x, y, hw: p.r_w / 2, hh: p.r_h / 2, until, side: Side::Upright { left } }
    }

    pub fn flat(p: &Params, (x, y): (u64, u64), until: usize) -> Wall {
        Wall { x, y, hw: p.r_seg / 2, hh: p.r_w / 2, until, side: Side::Flat }
    }
}

/// 单位中心在墙里（长方形四边各加单位半径）。
pub fn inside(w: &Wall, (x, y): (u64, u64), r: u64) -> bool {
    x.abs_diff(w.x) < w.hw + r && y.abs_diff(w.y) < w.hh + r
}

fn clear(walls: &[Wall], q: (u64, u64), r: u64) -> bool {
    !walls.iter().any(|w| inside(w, q, r))
}

/// 压在墙上的单位推出去：竖墙推到她那一侧（只改 x），横墙推到近的一侧（只改 y）。
pub fn push_out(w: &Wall, (x, y): (u64, u64), r: u64) -> (u64, u64) {
    match w.side {
        Side::Upright { left } => {
            let edge = w.hw + r + 1;
            (if left { w.x.saturating_sub(edge) } else { w.x + edge }, y)
        }
        Side::Flat => {
            let edge = w.hh + r + 1;
            (x, if y < w.y { w.y.saturating_sub(edge) } else { w.y + edge })
        }
    }
}

/// 这一 tick 单位该在哪（`None`：不用动）。进了墙：上一 tick 在墙外就退回去，只留顺着墙的那一半移动（竖墙留 y、横墙
/// 留 x），留不住就整个退回；上一 tick 也在墙里（墙刚立起压着它、她刚跳下墙），就推出去（推到的地方又在另一块墙里，
/// 就接着从那块推，最多推几次）。
pub fn hold(walls: &[Wall], last: Option<(u64, u64)>, now: (u64, u64), r: u64) -> Option<(u64, u64)> {
    let w = walls.iter().find(|w| inside(w, now, r))?;
    if let Some(l) = last.filter(|&l| clear(walls, l, r)) {
        let slide = match w.side {
            Side::Upright { .. } => (l.0, now.1),
            Side::Flat => (now.0, l.1),
        };
        return Some(if clear(walls, slide, r) { slide } else { l });
    }
    let mut q = push_out(w, now, r);
    for _ in 0..walls.len() {
        match walls.iter().find(|w| inside(w, q, r)) {
            Some(w) => q = push_out(w, q, r),
            None => break,
        }
    }
    Some(q)
}

/// 横墙第 k 段算出来的墙心：从她脚下朝目标 k×`r_seg`（目标就在她脚下时朝右）。
pub fn stretch_at(p: &Params, from: (u64, u64), to: (u64, u64), k: usize) -> (u64, u64) {
    let (dx, dy) = (to.0 as f64 - from.0 as f64, to.1 as f64 - from.1 as f64);
    let len = (dx * dx + dy * dy).sqrt();
    let (ux, uy) = if len < 1.0 { (1.0, 0.0) } else { (dx / len, dy / len) };
    let d = (k as u64 * p.r_seg) as f64;
    ((from.0 as f64 + ux * d).max(0.0).round() as u64, (from.1 as f64 + uy * d).max(0.0).round() as u64)
}

/// 横墙第 k 段铺下的 tick（线从 `from` tick 起飞，每 tick 飞 `r_lay_speed`，铺下那 tick 区域才列出来）。
pub fn stretch_due(p: &Params, from: usize, k: usize) -> usize {
    from + (k as u64 * p.r_seg).div_ceil(p.r_lay_speed.max(1)) as usize + 1
}

fn near(a: (u64, u64), b: (u64, u64), d: u64) -> bool {
    a.0.abs_diff(b.0) <= d && a.1.abs_diff(b.1) <= d
}

/// 她新放出、停着不动的区域：这一 tick 和上一 tick 都在同一处，而且那里比铺墙前多了。
pub fn settled(base: &[(u64, u64)], prev: &[(u64, u64)], now: &[(u64, u64)]) -> Vec<(u64, u64)> {
    let count = |list: &[(u64, u64)], q: (u64, u64)| list.iter().filter(|&&o| near(o, q, SAME)).count();
    let mut out: Vec<(u64, u64)> = Vec::new();
    for &q in now {
        if count(prev, q) > 0 && count(now, q) > count(base, q) && !out.iter().any(|&o| near(o, q, SAME)) {
            out.push(q);
        }
    }
    out
}

/// 对区域：离算出来的墙心 `tol` 以内、还没被别的段用掉的里面最近的一个。
pub fn snap(pred: (u64, u64), found: &[(u64, u64)], taken: &[(u64, u64)], tol: u64) -> Option<(u64, u64)> {
    found
        .iter()
        .copied()
        .filter(|&q| near(q, pred, tol) && !taken.iter().any(|&t| near(t, q, SAME)))
        .min_by_key(|&q| q.0.abs_diff(pred.0).max(q.1.abs_diff(pred.1)))
}

// ===================== 被动 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 横墙还没铺下的一段：第几段、算出来的墙心、该铺下的 tick。
#[derive(Clone, Copy, Debug)]
struct Pending {
    k: usize,
    at: (u64, u64),
    due: usize,
}

#[derive(Clone, Default)]
struct Weave {
    p: Params,
    me: usize,
    had_wall_up: bool,
    had_lay_up: bool,
    /// 上一 tick 她的投射物在哪、铺横墙那一 tick 之前她的投射物在哪。
    prev_proj: Vec<(u64, u64)>,
    base: Vec<(u64, u64)>,
    pending: Vec<Pending>,
    /// 这次横墙已经对上的区域（别的段不再用）。
    taken: Vec<(u64, u64)>,
    walls: Vec<Wall>,
    /// 墙立着时每个单位上一 tick 的位置。
    last_pos: HashMap<usize, (u64, u64)>,
}

impl Weave {
    /// 墙幔的目标：带 `aim` 的敌方英雄（不止一个就取离她近的）。
    fn target(&self, sim: &StableSim<'_>, me: (u64, u64), team: usize) -> Option<(usize, (u64, u64))> {
        let aim = sn("aim");
        (0..sim.entity_count())
            .filter_map(|i| sim.entity_at(i))
            .filter(|e| e.is_alive() && e.team() != team && matches!(e.kind(), Some(EntityKindV1::Champion)))
            .filter(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == aim))
            .map(|e| (e.id(), e.pos()))
            .min_by_key(|&(_, q)| q.0.abs_diff(me.0).max(q.1.abs_diff(me.1)))
    }

    fn watch(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize) {
        let mine: Vec<(u64, u64)> = (0..sim.projectile_count())
            .filter_map(|i| sim.projectile_at(i))
            .filter(|q| q.caster_id == me && !q.is_end)
            .map(|q| (q.x, q.y))
            .collect();
        let (me_pos, team) = sim.get_entity(me).map_or(((0, 0), 0), |e| (e.pos(), e.team()));
        let p = self.p;

        let wall_up = has(sim, me, &sn("wall_up"));
        if wall_up && !self.had_wall_up {
            match self.target(sim, me_pos, team) {
                Some((t, at)) => {
                    let left = me_pos.0 < at.0;
                    self.walls.push(Wall::upright(&p, at, left, now + p.r_t + 1));
                    if let Some(k) = counted("upright") {
                        wlog(format!("{} UPRIGHT #{k}: the wall at ({}, {}) behind {}, she on its {} side, {} ticks",
                                     head(sim, me), at.0, at.1, who(sim, t), if left { "left" } else { "right" }, p.r_t));
                    }
                }
                None => {
                    if let Some(k) = counted("upright_lost") {
                        wlog(format!("{} UPRIGHT? #{k}: wall_up rose but no enemy champion carries aim", head(sim, me)));
                    }
                }
            }
        }
        self.had_wall_up = wall_up;

        let lay_up = has(sim, me, &sn("lay_up"));
        if lay_up && !self.had_lay_up {
            match self.target(sim, me_pos, team) {
                Some((t, at)) => {
                    self.base = self.prev_proj.clone();
                    self.taken.clear();
                    self.pending = (0..p.r_n)
                        .map(|k| Pending { k, at: stretch_at(&p, me_pos, at, k), due: stretch_due(&p, now, k) })
                        .collect();
                    if let Some(k) = counted("lay") {
                        wlog(format!("{} LAY #{k}: {} stretches from ({}, {}) toward {} at ({}, {})", head(sim, me),
                                     p.r_n, me_pos.0, me_pos.1, who(sim, t), at.0, at.1));
                    }
                }
                None => {
                    if let Some(k) = counted("lay_lost") {
                        wlog(format!("{} LAY? #{k}: lay_up rose but no enemy champion carries aim", head(sim, me)));
                    }
                }
            }
        }
        self.had_lay_up = lay_up;

        if !self.pending.is_empty() {
            let found = settled(&self.base, &self.prev_proj, &mine);
            let tol = p.r_lay_speed + 2000;
            let mut left = Vec::new();
            for s in std::mem::take(&mut self.pending) {
                let got = if now + 1 >= s.due { snap(s.at, &found, &self.taken, tol) } else { None };
                let at = match got {
                    Some(q) => {
                        self.taken.push(q);
                        Some((q, "zone"))
                    }
                    None if now >= s.due + LATE => Some((s.at, "worked out")),
                    None => None,
                };
                match at {
                    Some((q, how)) => {
                        self.walls.push(Wall::flat(&p, q, now + p.r_t));
                        if let Some(k) = counted("stretch") {
                            wlog(format!("{} STRETCH #{k}: {} at ({}, {}) ({how}; worked out ({}, {}), due t={})",
                                         head(sim, me), s.k, q.0, q.1, s.at.0, s.at.1, s.due));
                        }
                    }
                    None => left.push(s),
                }
            }
            self.pending = left;
        }
        self.prev_proj = mine;
    }

    /// 墙立着时：每个单位进墙就放回去（她骑墙时不管她）。
    fn block(&mut self, sim: &mut StableSim<'_>, now: usize) {
        self.walls.retain(|w| now < w.until);
        if self.walls.is_empty() {
            self.last_pos.clear();
            return;
        }
        let riding = has(sim, self.me, &sn("riding"));
        let mut moves = Vec::new();
        let mut seen = HashMap::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_alive() {
                continue;
            }
            match e.kind() {
                Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Summon) => {}
                _ => continue,
            }
            let id = e.id();
            let now_pos = e.pos();
            if riding && id == self.me {
                seen.insert(id, now_pos);
                continue;
            }
            let r = match e.radius() as u64 { 0 => BODY, r => r };
            let last = self.last_pos.get(&id).copied();
            let at = match hold(&self.walls, last, now_pos, r) {
                Some(q) => {
                    moves.push((id, q, last.is_some_and(|l| clear(&self.walls, l, r))));
                    q
                }
                None => now_pos,
            };
            seen.insert(id, at);
        }
        for (id, (x, y), held) in moves {
            sim.entity_set_pos(id, x, y);
            if let Some(k) = counted(if held { "hold" } else { "push" }) {
                wlog(format!("{} {} #{k}: {} kept out of the wall at ({x}, {y})", head(sim, self.me),
                             if held { "HOLD" } else { "PUSH" }, who(sim, id)));
            }
        }
        self.last_pos = seen;
    }
}

impl StablePassive for Weave {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.had_wall_up = false;
        self.had_lay_up = false;
        self.prev_proj.clear();
        self.pending.clear();
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Taliyah (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let now = sim.tick();
        if sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            self.watch(sim, me, now);
        } else {
            self.pending.clear();
        }
        self.block(sim, now);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Taliyah: Weaver's Wall as real terrain) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:wall"), Weave::default());
    host.log(LogLevel::Info, "league_taliyah loaded (Weaver's Wall as real terrain).");
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

    fn p() -> Params {
        Params::default()
    }

    #[test]
    fn params_from_the_kit() {
        let q = parse_params(r#"{"r_h":120000,"r_lay_speed":8000,"r_n":6,"r_seg":26000,"r_t":300,"r_w":12000}"#);
        assert_eq!(q, Params::default());
    }

    #[test]
    fn walking_into_the_upright_wall_keeps_only_the_step_along_it() {
        let w = [Wall::upright(&p(), (500000, 400000), true, 300)];
        // from the left, walking right and down: the step right taken back, the step down kept
        assert_eq!(hold(&w, Some((488000, 400000)), (491000, 401000), 6000), Some((488000, 401000)));
        // from the right the same
        assert_eq!(hold(&w, Some((512000, 410000)), (509000, 410000), 6000), Some((512000, 410000)));
        // past its end: free
        assert_eq!(hold(&w, Some((495000, 470000)), (500000, 470000), 6000), None);
    }

    #[test]
    fn walking_onto_the_flat_wall_keeps_only_the_step_along_it() {
        let w = [Wall::flat(&p(), (500000, 400000), 300)];
        // from below (smaller y), walking up and right: up taken back, right kept
        assert_eq!(hold(&w, Some((500000, 388000)), (502000, 391000), 6000), Some((502000, 388000)));
        // the two stretches side by side are one wall: walking along it from one to the next is free outside them
        let w2 = [Wall::flat(&p(), (500000, 400000), 300), Wall::flat(&p(), (526000, 400000), 300)];
        assert_eq!(hold(&w2, Some((512000, 388000)), (514000, 390000), 6000), Some((514000, 388000)));
    }

    #[test]
    fn standing_on_a_wall_when_it_rises_pushed_off() {
        // the upright wall: to her side, wherever they stood on it
        let w = [Wall::upright(&p(), (500000, 400000), true, 300)];
        assert_eq!(hold(&w, None, (503000, 400000), 6000), Some((500000 - 12001, 400000)));
        let w = [Wall::upright(&p(), (500000, 400000), false, 300)];
        assert_eq!(hold(&w, None, (498000, 400000), 6000), Some((500000 + 12001, 400000)));
        // a flat stretch: to the nearer side
        let w = [Wall::flat(&p(), (500000, 400000), 300)];
        assert_eq!(hold(&w, None, (510000, 398000), 6000), Some((510000, 400000 - 12001)));
        assert_eq!(hold(&w, None, (510000, 402000), 6000), Some((510000, 400000 + 12001)));
        // she jumped off the wall (her last spot on it too): pushed off the same way
        assert_eq!(hold(&w, Some((508000, 401000)), (510000, 401000), 6000), Some((510000, 412001)));
    }

    #[test]
    fn the_stretches_laid_toward_the_target() {
        let me = (300000, 400000);
        assert_eq!(stretch_at(&p(), me, (450000, 400000), 0), me);
        assert_eq!(stretch_at(&p(), me, (450000, 400000), 2), (352000, 400000));
        // toward the left and up a little: along that line
        let q = stretch_at(&p(), me, (200000, 400000 - 100000 * 3 / 4), 1);
        assert_eq!(q, (300000 - 20800, 400000 - 15600));
        // the target right on her: to the right
        assert_eq!(stretch_at(&p(), me, me, 1), (326000, 400000));
        // the k-th line flies k x r_seg at r_lay_speed a tick, its zone listed the tick after it stops
        assert_eq!(stretch_due(&p(), 100, 0), 101);
        assert_eq!(stretch_due(&p(), 100, 1), 105);
        assert_eq!(stretch_due(&p(), 100, 5), 118);
    }

    #[test]
    fn only_zones_that_stay_put_count_and_each_once() {
        let base = [(330000, 410000)];
        // a line flying (moved since last tick), an old mine field, a new zone that stayed, listed twice (two zones there)
        let prev = [(330000, 410000), (340000, 400000), (352400, 400000), (352400, 400000)];
        let now = [(330000, 410000), (348000, 400000), (352400, 400000), (352400, 400000)];
        assert_eq!(settled(&base, &prev, &now), vec![(352400, 400000)]);
        // the stretch worked out at 352000 takes it; a second stretch never takes the same one
        let found = settled(&base, &prev, &now);
        assert_eq!(snap((352000, 400000), &found, &[], 10000), Some((352400, 400000)));
        assert_eq!(snap((352000, 400000), &found, &[(352400, 400000)], 10000), None);
        // too far from where it should be
        assert_eq!(snap((378000, 400000), &found, &[], 10000), None);
    }
}
