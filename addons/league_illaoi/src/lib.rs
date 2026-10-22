//! 俄洛伊附加包（用户 2026-10-23：「俄洛伊不用做附加包吗」「附加包就按这四项做」）：主包的数据做不到的四件事。
//!
//! `mod.override_info` 把主包的俄洛伊换成 `override/` 里的副本（tools/kit/build_illaoi.py 的 native=1）：普攻、W、E、R
//! 和主包一样，只是触手全交给本包：长触手的地方给她挂 2 tick 的信号（`league_illaoi_p_new` 普攻时、`league_illaoi_r_new`
//! 大招落地时），E 的灵魂不再是「受到伤害增加」，W 打中后不再由数据抽打；被动挂本包的 `league_illaoi:prophet`。
//!
//! - **触手贴着墙长**：英雄联盟里触手长在她附近的墙上。本包读这局的墙格子（卡密尔附加包内置的三张地图，
//!   `league_camille_wall/src/maps.rs`），在她身边 `p_reach` 内找离她最近的「墙边」——挨着墙的空地格子的中心，往墙那边
//!   靠半格；附近没有墙（河道、空地）就长在她身前 `t_place`（朝最近的敌人）。大招：每个 `r_r` 内的敌方英雄身边各长一条
//!   （同样先找墙边）；躯壳：身边长一条。同时最多 `MOST` 条，新的挤掉最老的。
//! - **触手抽谁**：每条触手每 `t_per` tick（她大招期间 `r_per`）抽 `t_r` 内的一个敌人：先抽被严酷训诫打中的（`w_mark`）
//!   和躯壳（`e_vessel`），再抽英雄，再抽其他单位（不打塔）。物理伤害 `t_dmg` + `t_ratio`% 攻击力；抽中英雄她回
//!   `p_heal` + `p_heal_r`% 攻击力。严酷训诫打中谁（新挂上 `w_mark`），`t_r` 内的每条触手隔 `w_gap` tick 依次抽他一下。
//! - **灵魂分担伤害**：E 打中的英雄挂着 `e_spirit` 时，她打他的每一下（普攻和技能，`on_attack`）多算 `e_echo`%。
//! - **灵魂拉断变躯壳**：记下灵魂被扯出来时他站的地方；他走出 `e_leash` 外，或灵魂的 `e_t` tick 到了，就去掉
//!   `e_spirit`、挂 `e_vessel`（`e_vt` tick），播灵魂碎裂，身边长一条触手。
//!
//! 每个计时都在被动自己身上（被动跟着单位、每局一份，游戏并行跑的几局互不相干），不用全局变量。
//! 只有单元测试（经典 SDK 跑不了原生代码），要在游戏里看日志。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_illaoi.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_illaoi";
const HERO: &str = "league_illaoi";
/// 同时最多这么多条触手。
const MOST: usize = 6;
/// 墙格子每格的世界单位（地图的 `walls`，卡密尔附加包同）。
const CELL: f64 = 32000.0;

fn il(x: &str) -> String {
    format!("{HERO}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ILLAOI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_illaoi.log");
        }
    }
    PathBuf::from("league_illaoi.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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
    /// 触手够得着的半径（主包 t_r）。
    pub t_r: u64,
    /// 触手活多少 tick（主包 t_life）。
    pub t_life: usize,
    /// 触手多久抽一下（主包 t_per；她大招期间 r_per）。
    pub t_per: usize,
    pub r_per: usize,
    /// 长出来后多久抽第一下（主包 t_first）。
    pub t_first: usize,
    /// 一下的伤害：t_dmg + t_ratio% 攻击力。
    pub t_dmg: usize,
    pub t_ratio: usize,
    /// 抽中英雄她回的血：p_heal + p_heal_r% 攻击力。
    pub p_heal: usize,
    pub p_heal_r: usize,
    /// 找墙的半径、没墙时长在身前多远（主包 p_reach / t_place）。
    pub p_reach: u64,
    pub t_place: u64,
    /// 大招长触手的半径（主包 r_r）。
    pub r_r: u64,
    /// 灵魂：持续、分担的百分比、拉断的距离、躯壳持续（主包 e_t / e_echo / e_leash / e_vt）。
    pub e_t: usize,
    pub e_echo: usize,
    pub e_leash: u64,
    pub e_vt: usize,
    /// 严酷训诫的标记持续、触手依次抽他的间隔（主包 w_mark_t / w_gap）。
    pub w_mark_t: usize,
    pub w_gap: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            t_r: 30000,
            t_life: 360,
            t_per: 90,
            r_per: 60,
            t_first: 40,
            t_dmg: 10,
            t_ratio: 35,
            p_heal: 6,
            p_heal_r: 6,
            p_reach: 60000,
            t_place: 15000,
            r_r: 45000,
            e_t: 300,
            e_echo: 15,
            e_leash: 150000,
            e_vt: 240,
            w_mark_t: 240,
            w_gap: 6,
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
            "t_r" => p.t_r = u as u64,
            "t_life" => p.t_life = u,
            "t_per" => p.t_per = u.max(1),
            "r_per" => p.r_per = u.max(1),
            "t_first" => p.t_first = u,
            "t_dmg" => p.t_dmg = u,
            "t_ratio" => p.t_ratio = u,
            "p_heal" => p.p_heal = u,
            "p_heal_r" => p.p_heal_r = u,
            "p_reach" => p.p_reach = u as u64,
            "t_place" => p.t_place = u as u64,
            "r_r" => p.r_r = u as u64,
            "e_t" => p.e_t = u,
            "e_echo" => p.e_echo = u,
            "e_leash" => p.e_leash = u as u64,
            "e_vt" => p.e_vt = u,
            "w_mark_t" => p.w_mark_t = u,
            "w_gap" => p.w_gap = u,
            _ => {}
        }
    }
    p
}

// ===================== 墙（单元测试用） =====================

/// 一张墙格子：`cells[y][x]` 为真是墙（`maps.rs` 的 `#`）。
#[derive(Clone, Debug, PartialEq)]
pub struct Walls {
    pub cells: Vec<Vec<bool>>,
}

impl Walls {
    pub fn from_rows(rows: &[&str]) -> Walls {
        Walls { cells: rows.iter().map(|r| r.chars().map(|c| c == '#').collect()).collect() }
    }

    fn wall_at(&self, cx: i64, cy: i64) -> bool {
        if cx < 0 || cy < 0 {
            return false; // 地图外不算（只找地图里的墙）
        }
        self.cells.get(cy as usize).and_then(|r| r.get(cx as usize)).copied().unwrap_or(false)
    }

    /// 世界坐标在墙里吗（地图外算墙）。
    pub fn is_wall(&self, x: f64, y: f64) -> bool {
        if x < 0.0 || y < 0.0 {
            return true;
        }
        let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
        self.cells.get(cy).and_then(|r| r.get(cx)).copied().unwrap_or(true)
    }

    pub fn count(&self) -> usize {
        self.cells.iter().flatten().filter(|c| **c).count()
    }

    /// `at` 附近 `reach` 内离 `at` 最近的墙边：挨着墙（上下左右）的空地格子的中心，往墙那边靠半格（触手贴着墙）。
    pub fn edge_near(&self, at: (f64, f64), reach: f64) -> Option<(f64, f64)> {
        let (cx, cy) = ((at.0 / CELL).floor() as i64, (at.1 / CELL).floor() as i64);
        let k = (reach / CELL).ceil() as i64 + 1;
        let mut best: Option<((f64, f64), f64)> = None;
        for y in cy - k..=cy + k {
            for x in cx - k..=cx + k {
                if x < 0 || y < 0 || self.wall_at(x, y) || y as usize >= self.cells.len() {
                    continue;
                }
                if x as usize >= self.cells[y as usize].len() {
                    continue;
                }
                let toward: Vec<(f64, f64)> = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    .iter()
                    .filter(|(dx, dy)| self.wall_at(x + dx, y + dy))
                    .map(|(dx, dy)| (*dx as f64, *dy as f64))
                    .collect();
                if toward.is_empty() {
                    continue;
                }
                let n = toward.len() as f64;
                let (sx, sy) = toward.iter().fold((0.0, 0.0), |a, b| (a.0 + b.0, a.1 + b.1));
                let spot = ((x as f64 + 0.5 + 0.35 * sx / n) * CELL, (y as f64 + 0.5 + 0.35 * sy / n) * CELL);
                let d = dist(spot, at);
                if d <= reach && best.is_none_or(|(_, bd)| d < bd) {
                    best = Some((spot, d));
                }
            }
        }
        best.map(|(s, _)| s)
    }
}

pub fn builtin(mode: GameModeKindV1) -> Walls {
    Walls::from_rows(match mode {
        GameModeKindV1::Moba => &maps::MOBA,
        GameModeKindV1::SingleLane => &maps::SINGLE_LANE,
        GameModeKindV1::DeathMatch => &maps::DEATH_MATCH,
    })
}

/// 这局的地图：站进墙里的单位最少的那张，一样少时墙最多的（卡密尔附加包的 pick_grid）。
pub fn pick(points: &[(f64, f64)]) -> Walls {
    [GameModeKindV1::Moba, GameModeKindV1::SingleLane, GameModeKindV1::DeathMatch]
        .into_iter()
        .map(builtin)
        .map(|w| (points.iter().filter(|p| w.is_wall(p.0, p.1)).count(), w.count(), w))
        .min_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)))
        .map(|(_, _, w)| w)
        .unwrap_or_else(|| builtin(GameModeKindV1::Moba))
}

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 没有墙时：从 `from` 朝 `to` 走 `reach`（`to` 就在脚下时原地）。
pub fn ahead(from: (f64, f64), to: Option<(f64, f64)>, reach: f64) -> (f64, f64) {
    match to {
        Some(t) if dist(from, t) > 1.0 => {
            let d = dist(from, t);
            let k = reach.min(d) / d;
            (from.0 + (t.0 - from.0) * k, from.1 + (t.1 - from.1) * k)
        }
        _ => from,
    }
}

// ===================== 选目标（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub id: usize,
    pub pos: (f64, f64),
    pub champion: bool,
    /// 被严酷训诫打中的、躯壳：触手先抽。
    pub marked: bool,
}

/// 触手抽谁：够得着的里面先抽带标记的，再抽英雄，再抽别的；同一档里最近的。
pub fn choose(foes: &[Foe], from: (f64, f64), reach: f64) -> Option<Foe> {
    let near: Vec<&Foe> = foes.iter().filter(|f| dist(f.pos, from) <= reach).collect();
    let by = |a: &&&Foe, b: &&&Foe| dist(a.pos, from).total_cmp(&dist(b.pos, from));
    near.iter()
        .filter(|f| f.marked)
        .min_by(by)
        .or_else(|| near.iter().filter(|f| f.champion).min_by(by))
        .or_else(|| near.iter().min_by(by))
        .map(|f| **f)
}

pub fn strike_damage(dmg: usize, ratio: usize, attack: usize) -> usize {
    dmg + ratio * attack / 100
}

// ===================== 被动 =====================

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

fn at(p: (f64, f64)) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 一个计时 buff（先去掉再加：同名 buff 会叠）。
fn refresh(sim: &mut StableSim<'_>, id: usize, buff: &BuffV1) {
    sim.entity_remove_buff(id, &buff.name());
    sim.add_buff(id, buff);
}

#[derive(Clone, Debug)]
struct Tentacle {
    pos: (f64, f64),
    until: usize,
    next: usize,
    on_wall: bool,
}

#[derive(Clone, Debug)]
struct Spirit {
    target: usize,
    spot: (f64, f64),
    until: usize,
}

/// 等着抽某个被严酷训诫打中的人的一下。
#[derive(Clone, Debug)]
struct Lash {
    due: usize,
    from: (f64, f64),
    target: usize,
}

/// 每个俄洛伊一份。
#[derive(Clone, Default)]
struct Prophet {
    p: Params,
    walls: Option<Walls>,
    tentacles: Vec<Tentacle>,
    spirits: Vec<Spirit>,
    marked: Vec<(usize, usize)>,
    lashes: Vec<Lash>,
    n_grown: usize,
    n_wall: usize,
    n_strike: usize,
    n_marked: usize,
    n_echo: usize,
    n_vessel: usize,
    next_report: usize,
}

struct Unit {
    id: usize,
    pos: (f64, f64),
    champion: bool,
    enemy: bool,
}

fn units(sim: &StableSim<'_>, team: usize) -> Vec<Unit> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if !e.is_alive() {
            continue;
        }
        let ok = matches!(
            e.kind(),
            Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Epic | EntityKindV1::Serpen)
        );
        if ok {
            out.push(Unit { id: e.id(), pos: fpos(e.pos()), champion: e.kind() == Some(EntityKindV1::Champion), enemy: e.team() != team });
        }
    }
    out
}

impl Prophet {
    fn walls(&mut self, us: &[Unit]) -> &Walls {
        if self.walls.is_none() {
            let points: Vec<(f64, f64)> = us.iter().map(|u| u.pos).collect();
            self.walls = Some(pick(&points));
        }
        self.walls.as_ref().unwrap()
    }

    /// 在 `near` 附近长一条触手：先找墙边，没有就在 `fallback`。
    fn grow(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit], near: (f64, f64), fallback: (f64, f64), why: &str) {
        let reach = self.p.p_reach as f64;
        let edge = self.walls(us).edge_near(near, reach);
        let pos = edge.unwrap_or(fallback);
        let tick = sim.tick();
        if self.tentacles.len() >= MOST {
            self.tentacles.remove(0);
        }
        self.tentacles.push(Tentacle { pos, until: tick + self.p.t_life, next: tick + self.p.t_first, on_wall: edge.is_some() });
        sim.play_view_effect(&il("tentacle"), me, &at(pos), 0, 0, 0);
        sim.play_view_effect(&il("p_spawn"), me, &at(pos), 0, 0, 0);
        sim.play_sfx(&il("p_spawn"), me, &at(pos));
        self.n_grown += 1;
        if edge.is_some() {
            self.n_wall += 1;
        }
        if self.n_grown <= 20 || self.n_grown % 50 == 0 {
            wlog(format!("{} GROW #{} ({why}): at ({:.0}, {:.0}){}, {} standing", head(sim, me), self.n_grown, pos.0, pos.1,
                         if edge.is_some() { " on a wall's edge" } else { " in the open" }, self.tentacles.len()));
        }
    }

    /// 一下：伤害、画面、抽中英雄回血。
    fn strike(&mut self, sim: &mut StableSim<'_>, me: usize, attack: usize, target: usize, champion: bool, why: &str) {
        let Some(t) = sim.get_entity(target) else { return };
        if !t.is_alive() {
            return;
        }
        let tp = fpos(t.pos());
        let dmg = strike_damage(self.p.t_dmg, self.p.t_ratio, attack);
        sim.deal_damage_typed(me, target, dmg, DamageTypeV1::Ad, AttackTypeV1::Skill);
        sim.play_view_effect(&il("lash"), me, &at(tp), 0, 0, 0);
        sim.play_view_effect(&il("p_slam"), me, &at(tp), 0, 0, 0);
        let hit = InputTargetV1::target(target);
        sim.play_view_effect(&il("p_hit"), me, &hit, 0, 0, 0);
        sim.play_sfx(&il("p_hit"), me, &hit);
        if champion && sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            sim.heal(me, me, strike_damage(self.p.p_heal, self.p.p_heal_r, attack));
            refresh(sim, me, &BuffV1::timed(&il("p_heal"), 36));
        }
        self.n_strike += 1;
        if self.n_strike <= 20 || self.n_strike % 100 == 0 {
            wlog(format!("{} STRIKE #{} ({why}): #{target}{} for {dmg}", head(sim, me), self.n_strike,
                         if champion { " (champion)" } else { "" }));
        }
    }

    fn signals(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit], pos: (f64, f64)) {
        let foe_champs: Vec<(usize, (f64, f64))> = us.iter().filter(|u| u.enemy && u.champion).map(|u| (u.id, u.pos)).collect();
        let nearest = us.iter().filter(|u| u.enemy).min_by(|a, b| dist(a.pos, pos).total_cmp(&dist(b.pos, pos))).map(|u| u.pos);
        if has_buff(sim, me, &il("p_new")) {
            sim.entity_remove_buff(me, &il("p_new"));
            let fallback = ahead(pos, nearest, self.p.t_place as f64);
            self.grow(sim, me, us, pos, fallback, "attack");
        }
        if has_buff(sim, me, &il("r_new")) {
            sim.entity_remove_buff(me, &il("r_new"));
            let r = self.p.r_r as f64;
            for (_, cp) in foe_champs.iter().filter(|(_, cp)| dist(*cp, pos) <= r) {
                self.grow(sim, me, us, *cp, *cp, "leap of faith");
            }
        }
    }

    /// 新挂上灵魂的英雄记下来；灵魂到时或拉断：躯壳。
    fn spirits(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit]) {
        let tick = sim.tick();
        let spirit = il("e_spirit");
        for u in us.iter().filter(|u| u.enemy && u.champion) {
            if !self.spirits.iter().any(|s| s.target == u.id) && has_buff(sim, u.id, &spirit) {
                self.spirits.push(Spirit { target: u.id, spot: u.pos, until: tick + self.p.e_t });
                wlog(format!("{} SPIRIT: #{} torn out at ({:.0}, {:.0})", head(sim, me), u.id, u.pos.0, u.pos.1));
            }
        }
        let mut broken = Vec::new();
        self.spirits.retain(|s| {
            let Some(u) = us.iter().find(|u| u.id == s.target) else { return false };
            let far = dist(u.pos, s.spot) > self.p.e_leash as f64;
            if far || tick >= s.until {
                broken.push((s.target, u.pos, far));
                return false;
            }
            true
        });
        for (target, tp, far) in broken {
            sim.entity_remove_buff(target, &spirit);
            refresh(sim, target, &BuffV1::timed(&il("e_vessel"), self.p.e_vt));
            sim.play_view_effect(&il("e_break"), me, &InputTargetV1::target(target), 0, 0, 0);
            sim.play_sfx(&il("e_break"), me, &InputTargetV1::target(target));
            self.n_vessel += 1;
            wlog(format!("{} VESSEL: #{target} ({})", head(sim, me), if far { "walked off its spirit" } else { "spirit ran out" }));
            self.grow(sim, me, us, tp, tp, "vessel");
        }
    }

    /// 严酷训诫新打中的人：够得着的触手依次抽他。
    fn lessons(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit]) {
        let tick = sim.tick();
        let mark = il("w_mark");
        self.marked.retain(|(_, until)| *until > tick);
        for u in us.iter().filter(|u| u.enemy) {
            if self.marked.iter().any(|(id, _)| *id == u.id) || !has_buff(sim, u.id, &mark) {
                continue;
            }
            self.marked.push((u.id, tick + self.p.w_mark_t));
            self.n_marked += 1;
            let reach = self.p.t_r as f64;
            let mut k = 0;
            for t in self.tentacles.iter().filter(|t| dist(t.pos, u.pos) <= reach * 1.5) {
                self.lashes.push(Lash { due: tick + 1 + k * self.p.w_gap, from: t.pos, target: u.id });
                k += 1;
            }
            if self.n_marked <= 20 {
                wlog(format!("{} LESSON: #{} - {k} tentacles lash it", head(sim, me), u.id));
            }
        }
    }

    fn fire(&mut self, sim: &mut StableSim<'_>, me: usize, us: &[Unit], attack: usize, fast: bool) {
        let tick = sim.tick();
        self.tentacles.retain(|t| t.until > tick);
        let (mark, vessel) = (il("w_mark"), il("e_vessel"));
        let foes: Vec<Foe> = us
            .iter()
            .filter(|u| u.enemy)
            .map(|u| Foe { id: u.id, pos: u.pos, champion: u.champion,
                           marked: has_buff(sim, u.id, &mark) || has_buff(sim, u.id, &vessel) })
            .collect();
        let per = if fast { self.p.r_per } else { self.p.t_per };
        let reach = self.p.t_r as f64;
        let mut hits = Vec::new();
        for t in self.tentacles.iter_mut() {
            if t.next > tick {
                continue;
            }
            t.next = tick + per;
            if let Some(f) = choose(&foes, t.pos, reach) {
                hits.push((f.id, f.champion, if f.marked { "marked" } else { "tentacle" }));
            }
        }
        let (due, wait): (Vec<Lash>, Vec<Lash>) = std::mem::take(&mut self.lashes).into_iter().partition(|l| l.due <= tick);
        self.lashes = wait;
        for l in due {
            let champ = us.iter().any(|u| u.id == l.target && u.champion);
            let _ = l.from;
            hits.push((l.target, champ, "lesson"));
        }
        for (id, champ, why) in hits {
            self.strike(sim, me, attack, id, champ, why);
        }
    }
}

impl StablePassive for Prophet {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Illaoi (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    /// 灵魂分担伤害：她打带着灵魂的英雄，每一下多算 e_echo%。
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        if *damage == 0 || !has_buff(sim, target, &il("e_spirit")) {
            return;
        }
        let extra = *damage * self.p.e_echo / 100;
        *damage += extra;
        self.n_echo += 1;
        if self.n_echo <= 10 || self.n_echo % 100 == 0 {
            wlog(format!("{} ECHO #{}: #{target} +{extra}", head(sim, me), self.n_echo));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, attack, pos) = (e.team(), e.stat().attack, fpos(e.pos()));
        let tick = sim.tick();
        let us = units(sim, team);
        self.signals(sim, me, &us, pos);
        self.spirits(sim, me, &us);
        self.lessons(sim, me, &us);
        let fast = has_buff(sim, me, &il("r_on"));
        // her tentacles stand and strike after her death (League's)
        self.fire(sim, me, &us, attack, fast);
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 {
                wlog(format!("{} WATCH: tentacles grown {} ({} on walls, {} standing), strikes {}, lessons {}, echoes {}, vessels {}",
                             head(sim, me), self.n_grown, self.n_wall, self.tentacles.len(), self.n_strike, self.n_marked,
                             self.n_echo, self.n_vessel));
            }
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Illaoi: tentacles on the walls, the spirit's echo and leash, tentacles after the marked) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:prophet"), Prophet::default());
    host.log(LogLevel::Info, "league_illaoi loaded (tentacles on the walls, Test of Spirit's echo and leash).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 10);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn params_from_the_kit() {
        let p = parse_params(r#"{"e_echo":15,"e_leash":150000,"e_t":300,"e_vt":240,"p_heal":6,"p_heal_r":6,"p_reach":60000,"r_per":60,"r_r":45000,"t_dmg":10,"t_first":40,"t_life":360,"t_per":90,"t_place":15000,"t_r":30000,"t_ratio":35,"w_gap":6,"w_mark_t":240}"#);
        assert_eq!(p, Params::default());
    }

    #[test]
    fn the_wall_edge_nearest_her() {
        let w = Walls::from_rows(&["....", "..#.", "....", "...."]);
        // she stands in cell (0, 1): the nearest edge is cell (1, 1) left of the wall, pushed toward it
        let her = (0.5 * CELL, 1.5 * CELL);
        let e = w.edge_near(her, 2.0 * CELL).unwrap();
        assert!((e.0 - 1.85 * CELL).abs() < 1.0 && (e.1 - 1.5 * CELL).abs() < 1.0, "{e:?}");
        // no wall within reach: none
        let open = Walls::from_rows(&["......", "......", "......"]);
        assert_eq!(open.edge_near(her, 3.0 * CELL), None);
        // a wall too far
        assert_eq!(w.edge_near((0.5 * CELL, 3.5 * CELL), 0.5 * CELL), None);
    }

    #[test]
    fn the_map_is_the_one_nobody_stands_in_walls() {
        // units in the 5v5 map's corners stand in the single lane map's rock (its rows 0-5 start with walls)
        let w = pick(&[(16000.0, 16000.0), (944000.0, 944000.0), (480000.0, 160000.0)]);
        assert_eq!(w, builtin(GameModeKindV1::Moba));
        assert_eq!(builtin(GameModeKindV1::Moba).count(), 90);
    }

    #[test]
    fn marked_first_then_champions_then_the_rest() {
        let me = (0.0, 0.0);
        let foes = [
            Foe { id: 1, pos: (5000.0, 0.0), champion: false, marked: false },
            Foe { id: 2, pos: (20000.0, 0.0), champion: true, marked: false },
            Foe { id: 3, pos: (29000.0, 0.0), champion: false, marked: true },
            Foe { id: 4, pos: (90000.0, 0.0), champion: true, marked: true },
        ];
        assert_eq!(choose(&foes, me, 30000.0).map(|f| f.id), Some(3));
        assert_eq!(choose(&foes[..2], me, 30000.0).map(|f| f.id), Some(2));
        assert_eq!(choose(&foes[..1], me, 30000.0).map(|f| f.id), Some(1));
        assert_eq!(choose(&foes[3..], me, 30000.0), None);
    }

    #[test]
    fn ahead_toward_the_nearest_enemy() {
        assert_eq!(ahead((0.0, 0.0), Some((30000.0, 0.0)), 15000.0), (15000.0, 0.0));
        assert_eq!(ahead((0.0, 0.0), Some((10000.0, 0.0)), 15000.0), (10000.0, 0.0));
        assert_eq!(ahead((5.0, 5.0), None, 15000.0), (5.0, 5.0));
        assert_eq!(strike_damage(10, 35, 100), 45);
    }
}
