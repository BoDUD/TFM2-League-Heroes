//! 阿兹尔附加包：数据做不到的三件事（用户选的方案 C：「太阳圆盘」做附加包；大招禁军用侧面，朝左朝右按冲锋方向；沙兵
//! 「沙兵没攻击动作 你想办法补吧 不让codex了 还有不面向敌人」）。
//!
//! `mod.override_info` 把主包的阿兹尔换成 `override/` 里的副本（tools/kit/build_azir.py --native）：技能和主包一模一样，只是
//! - 被动挂本包的 `league_azir:disc`（参数在英雄数据的 `passive.params` 里）：**太阳圆盘**（英雄联盟的「恕瑞玛的传承」）。
//!   开局记下我方每座防御塔的位置；每局一次，某座塔倒了、阿兹尔走到它的废墟 `d_near` 内、废墟 `d_range` 内有敌方单位时，
//!   圆盘从沙里升起（`d_rise`、`disc_rise` 画面和声音），立 `d_life` tick：每 `d_per` tick 打 `d_range` 内最近的敌人一下
//!   （先打英雄，没有英雄再打小兵和野怪），`d_dmg` + `d_ap`% 法强的魔法伤害（太阳光束 `d_beam`），每 `s_step` tick 重新盖一次
//!   圆盘和脚下光环的画面。圆盘不跟着阿兹尔死，立满时间才消失。
//! - 大招的禁军墙出墙那一刻调本包的 `league_azir:r_wall`（拿到大招的目标）：数据看不到墙往哪边冲，主包的禁军永远朝右；
//!   本包按阿兹尔到目标的方向算出墙的路线，在数据那道墙每一跳停下的地方、停下的那个 tick（`r_len` 分 `r_stamps` 跳，速度
//!   `r_speed`）盖上朝冲锋方向的禁军（朝右 `r_guards_a/b`，朝左 `r_guards_la/lb`，两步轮流）和脚下的沙尘。伤害和击退还是数据那道墙的。
//! - v1.4（用户 2026-10-28：「沙皇推开别人后 别人马上就回到那位置」「反推也推不回去」「退完后沙兵秒消失和lol不一样 不卡住位置」）：
//!   **墙立住**：数据那道墙冲到头就没了，被推开的人 0.3 秒就走回来。本包让墙在最后一跳停下的地方再立 `r_hold` tick（英雄联盟
//!   3 秒），横向 `r_half` 宽，禁军一直站着；敌方英雄走不过去（走进墙里就放回他那一边的墙面外，`entity_set_pos`），正在被推、
//!   在冲刺的不挡。**反推绕对方向**：数据的 RushMoveToBack 是冲到目标「背对他自己」的那边，E 冲过了头或从侧面冲上去时墙就推歪、
//!   推反（日志：21 次反推 7 次推向敌方）；副本改调本包的 `league_azir:r_behind`：冲到目标背对他的队伍（`HOME_R` 内的我方英雄，
//!   没有就最近的我方塔）`r_behind` 远的地方，墙从那里把人推回他的队伍。
//! - **沙兵从侧面画，朝敌人，出手时刺**：数据分不出左右，主包的沙兵正面朝镜头、刺的时候不动。副本里每个槽位的沙兵升起、
//!   每个检查点、每次刺都调本包的 `rise_<槽>` / `sold_<槽>` / `stab_<槽>`（拿到沙兵站的地方、被刺的单位）；本包自己画：
//!   升起放侧面的 `ss_rise`，之后每 `ss_stand` tick 盖一次站着的 `ss_stand`，朝它 `FACE_R` 内最近的敌人（先英雄）；
//!   刺过以后下一次改放 `ss_stab`（`ss_stab` tick），朝被刺的那个。每个槽位按 `SLOT_AT` 错开一点（三个站一处时分得开）。
//!   狂沙猛攻把沙兵挪走时新的升起换一条盖章链，旧的那条自己停；检查点不来了（沙兵到时间、换代）就不再盖。
//!   谁放的都画（佛耶戈附身阿兹尔时也一样），不靠被动。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。服务端预模拟和你看的那场各算各的
//! （被动是每个阿兹尔一份；墙的路线只用施放那一刻的位置）。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_azir.log`，
//! 每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod combo;

const ID: &str = "league_azir";
/// The disc_rise tag's length (tools/art/rig_azir.py: four sinking frames of 90 ms and one of 200): its standing stamps
/// start after it.
const RISE_TICKS: usize = 34;
const LOG_FIRST: usize = 30;
const LOG_EVERY: usize = 50;

fn az(x: &str) -> String {
    format!("{ID}_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AZIR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_azir.log");
        }
    }
    PathBuf::from("league_azir.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
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

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// The first LOG_FIRST of a kind, then every LOG_EVERY-th: the count, or None (not logged).
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 太阳圆盘：立多少 tick、隔多少 tick 打一下、打多远、伤害（固定 + 法强百分比）、阿兹尔离废墟多近才立。
    pub d_life: usize,
    pub d_per: usize,
    pub d_range: usize,
    pub d_dmg: usize,
    pub d_ap: usize,
    pub d_near: usize,
    /// 禁军墙：速度、冲多远、分几跳（和数据那道墙一样）。
    pub r_speed: usize,
    pub r_len: usize,
    pub r_stamps: usize,
    /// 圆盘的画面隔多少 tick 重新盖一次（`disc` 那一段的长度）；沙兵的检查点也是这个间隔。
    pub s_step: usize,
    /// 侧面沙兵：站着的一次、升起、刺各多少 tick（`league_azir_soldier_side` 那几段的长度）。
    pub ss_stand: usize,
    pub ss_rise: usize,
    pub ss_stab: usize,
    /// 反推：冲刺速度、冲到目标身后多远。
    pub r_rush: usize,
    pub r_behind: usize,
    /// 墙立住多少 tick、横向半宽。
    pub r_hold: usize,
    pub r_half: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { d_life: 2700, d_per: 60, d_range: 45000, d_dmg: 50, d_ap: 35, d_near: 60000, r_speed: 3000, r_len: 60000,
               r_stamps: 5, s_step: 40, ss_stand: 4, ss_rise: 20, ss_stab: 16, r_rush: 8000, r_behind: 15000,
               r_hold: 180, r_half: 30000 }
    }
}

/// `{"d_life":2700,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        match k {
            "d_life" => p.d_life = v,
            "d_per" => p.d_per = v.max(1),
            "d_range" => p.d_range = v,
            "d_dmg" => p.d_dmg = v,
            "d_ap" => p.d_ap = v,
            "d_near" => p.d_near = v,
            "r_speed" => p.r_speed = v.max(1),
            "r_len" => p.r_len = v,
            "r_stamps" => p.r_stamps = v.max(1),
            "s_step" => p.s_step = v.max(1),
            "ss_stand" => p.ss_stand = v.max(1),
            "ss_rise" => p.ss_rise = v.max(1),
            "ss_stab" => p.ss_stab = v.max(1),
            "r_rush" => p.r_rush = v.max(1),
            "r_behind" => p.r_behind = v,
            "r_hold" => p.r_hold = v,
            "r_half" => p.r_half = v,
            _ => {}
        }
    }
    p
}

/// Each Azir's params (by entity id: the server's pre-simulation and the match on screen use the same numbers), for the
/// wall's native effect, which has no passive of its own.
static PARAMS: LazyLock<Mutex<HashMap<usize, Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&me).copied().unwrap_or_default()
}

// ===================== 计算 =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn at_of(e: &StableEntity<'_, '_>) -> (f64, f64) {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

fn ux(v: f64) -> u64 {
    v.round().max(0.0) as u64
}

fn pos_input(p: (f64, f64)) -> InputTargetV1 {
    InputTargetV1::pos(ux(p.0), ux(p.1))
}

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

/// The disc's damage: d_dmg + d_ap% of his ability power.
pub fn disc_damage(p: &Params, ap: usize) -> usize {
    p.d_dmg + p.d_ap * ap / 100
}

/// The wall's hops: for each of the r_stamps stops, (where it stops, the tick it stops on after the launch). The data's
/// hidden bolts fly r_len * i / r_stamps at r_speed a tick from where he stands toward the target.
pub fn wall_stops(p: &Params, from: (f64, f64), to: (f64, f64)) -> Vec<((f64, f64), usize)> {
    let (dx, dy) = (to.0 - from.0, to.1 - from.1);
    let d = (dx * dx + dy * dy).sqrt();
    let (ux_, uy_) = if d > 1.0 { (dx / d, dy / d) } else { (1.0, 0.0) };
    (1..=p.r_stamps)
        .map(|i| {
            let s = (p.r_len * i / p.r_stamps) as f64;
            ((from.0 + ux_ * s, from.1 + uy_ * s), ((s / p.r_speed as f64).round() as usize).max(1))
        })
        .collect()
}

/// Which way the guards face: to the right unless the wall runs to the left (a wall straight up or down keeps the side
/// his team charges toward: the blue side's right).
pub fn faces_right(from: (f64, f64), to: (f64, f64), team: usize) -> bool {
    let dx = to.0 - from.0;
    if dx.abs() > 500.0 {
        dx > 0.0
    } else {
        team == 0
    }
}

// ===================== 被动：太阳圆盘 =====================

#[derive(Clone, Copy, Debug)]
struct Up {
    at: (f64, f64),
    until: usize,
    next_shot: usize,
    next_stamp: usize,
}

/// 每个阿兹尔一份：参数、开局记下的我方塔（编号、位置）、这局用没用过、立着的圆盘。
#[derive(Clone, Default)]
struct Disc {
    p: Params,
    towers: Vec<(usize, (f64, f64))>,
    used: bool,
    up: Option<Up>,
}

/// The nearest enemy of `team` within r of `at`: champions first, then minions and monsters (never a tower or the nexus):
/// (its id, a champion, where it stands).
fn nearest(sim: &StableSim<'_>, team: usize, at: (f64, f64), r: f64) -> Option<(usize, bool, (f64, f64))> {
    let mut best_c: Option<(f64, usize, (f64, f64))> = None;
    let mut best_u: Option<(f64, usize, (f64, f64))> = None;
    for k in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(k) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower() {
            continue;
        }
        if matches!(u.kind(), Some(EntityKindV1::Nexus | EntityKindV1::Tower)) {
            continue;
        }
        let there = at_of(&u);
        let d = dist(there, at);
        if d > r {
            continue;
        }
        let slot = if u.is_champion() { &mut best_c } else { &mut best_u };
        if slot.map_or(true, |(bd, _, _)| d < bd) {
            *slot = Some((d, u.id(), there));
        }
    }
    best_c.map(|(_, id, p)| (id, true, p)).or(best_u.map(|(_, id, p)| (id, false, p)))
}

impl Disc {
    /// The nearest enemy within d_range of the disc: champions first, then minions and monsters (never a tower).
    fn target(&self, sim: &StableSim<'_>, team: usize, at: (f64, f64)) -> Option<(usize, bool)> {
        nearest(sim, team, at, self.p.d_range as f64).map(|(id, champ, _)| (id, champ))
    }

    fn snapshot(&mut self, sim: &StableSim<'_>, team: usize) {
        self.towers = (0..sim.tower_count())
            .filter_map(|k| sim.get_entity(sim.tower_id_at(k)))
            .filter(|t| t.team() == team && t.is_alive())
            .map(|t| (t.id(), at_of(&t)))
            .collect();
    }

    /// A fallen tower of his whose ruin he stands by with an enemy in the disc's reach: where the disc rises.
    fn ruin(&self, sim: &StableSim<'_>, team: usize, here: (f64, f64)) -> Option<(f64, f64)> {
        self.towers
            .iter()
            .filter(|(id, _)| sim.get_entity(*id).map_or(true, |t| !t.is_alive()))
            .map(|(_, at)| *at)
            .filter(|at| dist(*at, here) <= self.p.d_near as f64)
            .find(|at| self.target(sim, team, *at).is_some())
    }
}

impl StablePassive for Disc {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert(me, self.p);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if self.towers.is_empty() {
            self.snapshot(sim, team);
        }
        wlog(format!("{} SPAWN: the add-on's Azir (player {player}, team {team}), {} towers of his, disc {}, {:?}",
                     head(sim, me), self.towers.len(), if self.used { "used" } else { "ready" }, self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let here = at_of(&e);
        let alive = e.is_alive();
        let ap = e.stat().magic_power;
        walls_tick(sim, me, team, tick, &self.p);
        if self.towers.is_empty() && tick < 600 {
            self.snapshot(sim, team);
        }
        if let Some(mut up) = self.up {
            if tick >= up.until {
                wlog(format!("{} DISC GONE at {}", head(sim, me), pt(up.at)));
                self.up = None;
                return;
            }
            if tick >= up.next_stamp {
                sim.play_view_effect(&az("disc"), me, &pos_input(up.at), 0, 0, 0);
                sim.play_view_effect(&az("d_glow"), me, &pos_input(up.at), 0, 0, 0);
                up.next_stamp = tick + self.p.s_step;
            }
            if tick >= up.next_shot {
                if let Some((t, champ)) = self.target(sim, team, up.at) {
                    let dmg = disc_damage(&self.p, ap);
                    sim.deal_damage_typed(me, t, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                    sim.play_view_effect(&az("d_beam"), me, &InputTargetV1::target(t), 0, 0, 0);
                    sim.play_sfx(&az("d_beam"), me, &InputTargetV1::target(t));
                    if let Some(k) = counted("shot") {
                        wlog(format!("{} SHOT #{k} the disc at {} -> #{t} ({}) {dmg} magic", head(sim, me), pt(up.at),
                                     if champ { "champion" } else { "unit" }));
                    }
                }
                up.next_shot = tick + self.p.d_per;
            }
            self.up = Some(up);
            return;
        }
        if self.used || !alive {
            return;
        }
        if let Some(at) = self.ruin(sim, team, here) {
            self.used = true;
            self.up = Some(Up { at, until: tick + self.p.d_life, next_shot: tick + RISE_TICKS, next_stamp: tick + RISE_TICKS });
            sim.play_view_effect(&az("d_rise"), me, &pos_input(at), 0, 0, 0);
            sim.play_view_effect(&az("disc_rise"), me, &pos_input(at), 0, 0, 0);
            sim.play_sfx(&az("d_rise"), me, &pos_input(at));
            wlog(format!("{} DISC RISES on the ruin at {} ({:.0} from him), {} ticks", head(sim, me), pt(at),
                         dist(at, here), self.p.d_life));
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        // the disc stands on (League's does); `used` is the game's
    }
}

// ===================== 大招：禁军墙朝冲锋方向 =====================

/// R's wall launching (the native copy's `league_azir:r_wall`, the ult's target as input): the guards stamped where and
/// when each of the data's hidden bolts stops, facing the way the wall runs.
struct Wall;

impl StableEffectType for Wall {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(e) = sim.get_entity(me) else { return };
        let (from, team) = (at_of(&e), e.team());
        let to = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Target) => match sim.get_entity(input.target_id) {
                Some(t) => at_of(&t),
                None => return,
            },
            Some(InputTargetKindV1::Pos) => (input.x as f64, input.y as f64),
            _ => return,
        };
        let p = params_of(me);
        let right = faces_right(from, to, team);
        let stops = wall_stops(&p, from, to);
        let up = standing(&p, from, to, sim.tick(), right);
        let key = wall_key(sim, me);
        WALLS.lock().unwrap_or_else(|e| e.into_inner()).entry(key).or_default().push(up);
        for (i, (at, delay)) in stops.iter().enumerate() {
            let name = format!("{ID}:stamp_{}{}", if right { "r" } else { "l" }, if (i + 1) % 2 == 1 { "b" } else { "a" });
            if !sim.queue_effect(&name, AttackTypeV1::Skill, me, &pos_input(*at), *delay) {
                wlog(format!("{} queue_effect({name}) refused", head(sim, me)));
            }
        }
        if let Some(k) = counted("wall") {
            wlog(format!("{} WALL #{k} from {} toward {}: facing {}, {} stops", head(sim, me), pt(from), pt(to),
                         if right { "right" } else { "left" }, stops.len()));
        }
    }
}

// ===================== 大招：禁军墙立住、挡人；反推绕到身后 =====================

/// 墙的厚度的一半：敌方英雄离墙这么近（沿冲锋方向）就算走进墙里，放回他原来那一边的墙面外。
pub const WALL_THICK: f64 = 6_000.0;
/// 立着的墙隔多少 tick 重新盖一次禁军（一跳的画面长度：r_len / r_stamps / r_speed）。
pub const STAND_STEP: usize = 4;
/// 立着的墙除了中间那一组禁军，两边各再盖一组，离中间这么远（横向）。
pub const STAND_SPREAD: f64 = 18_000.0;
/// 反推找「他的队伍」：这么近的我方英雄（不算他自己），没有就最近的我方防御塔。
pub const HOME_R: f64 = 90_000.0;

pub type Pt = (f64, f64);

fn unit(v: Pt) -> Option<Pt> {
    let d = (v.0 * v.0 + v.1 * v.1).sqrt();
    (d > 1.0).then(|| (v.0 / d, v.1 / d))
}

/// 一道立住的墙：中点、冲锋方向（单位向量）、从哪个 tick 立到哪个 tick、禁军朝哪边、每个敌方英雄在墙的哪一边（+1 冲锋
/// 方向那边、-1 阿兹尔这边）、下一次盖禁军的 tick、挡回来几次。
#[derive(Clone, Debug)]
pub struct Standing {
    pub mid: Pt,
    pub dir: Pt,
    pub from: usize,
    pub until: usize,
    pub right: bool,
    pub sides: HashMap<usize, f64>,
    pub next_stamp: usize,
    pub held: usize,
}

/// 墙立在哪：数据那道墙最后一跳停下的地方（从他站的地方朝目标 r_len），r_len / r_speed tick 后立住，再立 r_hold tick。
pub fn standing(p: &Params, from: Pt, to: Pt, tick: usize, right: bool) -> Standing {
    let dir = unit((to.0 - from.0, to.1 - from.1)).unwrap_or((1.0, 0.0));
    let len = p.r_len as f64;
    let up = tick + (p.r_len / p.r_speed.max(1)).max(1);
    Standing { mid: (from.0 + dir.0 * len, from.1 + dir.1 * len), dir, from: up, until: up + p.r_hold, right,
               sides: HashMap::new(), next_stamp: up, held: 0 }
}

/// 一个敌方英雄在 `pos`，原来在墙的 `side` 边（没记过就按现在的位置算）：返回他这一边，和他走进墙里、穿过墙时要放回的
/// 位置（他那一边的墙面外，横向不动）。墙两头 `half` 以外绕过去不管，那时按他现在在哪边重新记。
pub fn hold(mid: Pt, dir: Pt, half: f64, pos: Pt, side: Option<f64>) -> (f64, Option<Pt>) {
    let (rx, ry) = (pos.0 - mid.0, pos.1 - mid.1);
    let along = rx * dir.0 + ry * dir.1;
    let n = (-dir.1, dir.0);
    let across = rx * n.0 + ry * n.1;
    let now = if along >= 0.0 { 1.0 } else { -1.0 };
    if across.abs() > half {
        return (now, None);
    }
    let s = side.unwrap_or(now);
    if along * s >= WALL_THICK {
        return (s, None);
    }
    let back = (mid.0 + dir.0 * s * WALL_THICK + n.0 * across, mid.1 + dir.1 * s * WALL_THICK + n.1 * across);
    (s, Some(back))
}

/// 反推时他绕到哪：目标身后、背对他的队伍 r_behind 远（`home` 是他的队伍那边的一点；没有就背对他自己，同数据的
/// RushMoveToBack）。
pub fn behind(p: &Params, me: Pt, target: Pt, home: Option<Pt>) -> Pt {
    let away = home.and_then(|h| unit((target.0 - h.0, target.1 - h.1)))
        .or_else(|| unit((target.0 - me.0, target.1 - me.1)))
        .unwrap_or((1.0, 0.0));
    let b = p.r_behind as f64;
    (target.0 + away.0 * b, target.1 + away.1 * b)
}

type WallKey = (u64, u32, u64, u64, usize);

/// 立着的墙，按（种子、哪一种模拟、比赛、局、阿兹尔）分开：服务器的预演和屏幕上的比赛同时在跑。
static WALLS: LazyLock<Mutex<HashMap<WallKey, Vec<Standing>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn wall_key(sim: &StableSim<'_>, me: usize) -> WallKey {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index, me)
}

/// 正在被推、在冲刺的人不挡（被墙推过去的那一下、闪现和突进都能过墙，同英雄联盟）。
fn flying(u: &StableEntity<'_, '_>) -> bool {
    (0..u.cc_count()).any(|i| u.cc_at(i).is_some_and(|c| c.kind == CcKindV1::ForceMove.code() || c.kind == CcKindV1::Airborne.code()))
}

/// 每 tick（他的被动里）：立着的墙盖禁军、挡敌方英雄，到时候撤掉。
fn walls_tick(sim: &mut StableSim<'_>, me: usize, team: usize, tick: usize, p: &Params) {
    let key = wall_key(sim, me);
    let Some(mut walls) = WALLS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key) else { return };
    let half = p.r_half as f64;
    for w in walls.iter_mut().filter(|w| tick >= w.from) {
        if tick >= w.next_stamp {
            let n = (-w.dir.1, w.dir.0);
            let view = az(if w.right { "r_guards_a" } else { "r_guards_la" });
            for k in [-1.0, 0.0, 1.0] {
                let at = (w.mid.0 + n.0 * STAND_SPREAD * k, w.mid.1 + n.1 * STAND_SPREAD * k);
                sim.play_view_effect(&view, me, &pos_input(at), 0, 0, 0);
            }
            w.next_stamp = tick + STAND_STEP;
        }
        let foes: Vec<(usize, Pt, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.is_alive() && u.team() != team)
            .map(|u| (u.id(), at_of(&u), flying(&u)))
            .collect();
        for (id, at, fly) in foes {
            if fly {
                w.sides.remove(&id); // landed: its side is wherever it lands
                continue;
            }
            let (side, back) = hold(w.mid, w.dir, half, at, w.sides.get(&id).copied());
            w.sides.insert(id, side);
            if let Some(b) = back {
                sim.entity_set_pos(id, ux(b.0), ux(b.1));
                w.held += 1;
            }
        }
    }
    let (gone, left): (Vec<Standing>, Vec<Standing>) = walls.into_iter().partition(|w| tick >= w.until);
    for w in gone {
        if let Some(k) = counted("wall_down") {
            wlog(format!("{} WALL DOWN #{k} at {}: held enemy champions back {} time(s)", head(sim, me), pt(w.mid), w.held));
        }
    }
    if !left.is_empty() {
        WALLS.lock().unwrap_or_else(|e| e.into_inner()).insert(key, left);
    }
}

/// 反推（数据：E 冲到英雄身上后 R，`r_win` 开着）出墙前调本包的 `league_azir:r_behind`（大招的目标）：他冲到目标身后、
/// 背对他的队伍那一边（我方英雄，没有就最近的我方塔），墙就从那边把人推回他的队伍。数据原来的 RushMoveToBack 只是
/// 「冲到目标背后」——背对的是他自己冲来的方向，E 冲过了头或者从侧面冲上去时就推歪、推反（日志：21 次反推 7 次推向
/// 敌方那边）。
struct Behind;

impl StableEffectType for Behind {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let Some(e) = sim.get_entity(me) else { return };
        let (here, team) = (at_of(&e), e.team());
        let Some(target) = (match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|t| at_of(&t)),
            Some(InputTargetKindV1::Pos) => Some((input.x as f64, input.y as f64)),
            _ => None,
        }) else { return };
        let p = params_of(me);
        let friends: Vec<Pt> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.is_alive() && u.team() == team && u.id() != me)
            .map(|u| at_of(&u))
            .filter(|at| dist(*at, here) <= HOME_R)
            .collect();
        let home = if friends.is_empty() {
            (0..sim.tower_count()).filter_map(|k| sim.get_entity(sim.tower_id_at(k)))
                .filter(|t| t.team() == team && t.is_alive())
                .map(|t| at_of(&t))
                .min_by(|a, b| dist(*a, here).total_cmp(&dist(*b, here)))
        } else {
            let n = friends.len() as f64;
            Some((friends.iter().map(|f| f.0).sum::<f64>() / n, friends.iter().map(|f| f.1).sum::<f64>() / n))
        };
        let spot = behind(&p, here, target, home);
        let (dx, dy) = (spot.0 - here.0, spot.1 - here.1);
        let len = (dx * dx + dy * dy).sqrt();
        let ticks = ((len / p.r_rush.max(1) as f64).ceil() as u64).max(1);
        let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks);
        cc.dx = dx.round() as i64;
        cc.dy = dy.round() as i64;
        cc.speed = p.r_rush as u64;
        sim.apply_cc(me, &cc);
        if let Some(k) = counted("behind") {
            wlog(format!("{} BEHIND #{k}: from {} round the target at {} to {} ({:.0} in {ticks} ticks), his team {}",
                         head(sim, me), pt(here), pt(target), pt(spot), len,
                         home.map_or("unknown (away from him)".to_string(), |h| format!("at {}", pt(h)))));
        }
    }
}

/// One hop's guards (and the dust at their feet) where the input says.
struct Stamp {
    view: &'static str,
}

impl StableEffectType for Stamp {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        sim.play_view_effect(&az(self.view), me, &input, 0, 0, 0);
        sim.play_view_effect(&az("r_dust"), me, &input, 0, 0, 0);
    }
}

// ===================== 沙兵：侧面，朝最近的敌人，出手时刺 =====================

/// The slots (the data's a, b, c) and where each one's soldier stands off the data's spot, game units (tools/art/
/// rig_azir.py SLOT_AT: three on one spot - after Conquering Sands - stand apart).
const SLOTS: [&str; 3] = ["a", "b", "c"];
const SLOT_AT: [(f64, f64); 3] = [(0.0, 0.0), (-8_000.0, -3_000.0), (8_000.0, 3_000.0)];
/// A soldier turns to the nearest enemy within this of it (its reach, s_r 42000, and a step more).
const FACE_R: f64 = 60_000.0;
/// An enemy less than this to the side is straight above or below it: it keeps facing the way it faced.
const FACE_DX: f64 = 2_000.0;
/// More soldiers remembered than this (games that ended mid-life never removed theirs): start over.
const MAX_SOLDIERS: usize = 4096;

/// Which way a soldier at `at` faces: toward `enemy` unless that is straight above or below it, then `keep`.
pub fn turn_to(at: (f64, f64), enemy: Option<(f64, f64)>, keep: bool) -> bool {
    match enemy {
        Some(e) if (e.0 - at.0).abs() >= FACE_DX => e.0 > at.0,
        _ => keep,
    }
}

/// One soldier's picture: the data's spot, the way it faces, its chain of stamps (a new rise starts a new one; the old
/// one stops itself), a stab to draw on the next stamp (toward the unit stabbed), the tick its checkpoints keep it to.
#[derive(Clone, Copy, Debug)]
struct Soldier {
    at: (f64, f64),
    right: bool,
    chain: usize,
    stab: Option<(f64, f64)>,
    until: usize,
    /// 0.1.1 (the user, 2026-10-23: 「沙皇召唤出来的小兵会瞬间消失」): the tick its next stamp is due and the tick it was
    /// last drawn. A stamp is taken when it is due, whatever chain number its input carries (a position's target id may
    /// not survive the queue); a checkpoint of the data finding it undrawn for `REDRAW` ticks draws it and starts again.
    next: usize,
    last: usize,
}

/// A checkpoint redraws a soldier nothing drew for this many ticks (its chain of stamps broken).
pub const REDRAW: usize = 6;

/// Is a stamp arriving at `tick` the one due (`next`)? Earlier ones are another chain's, a later one a late copy.
pub fn stamp_due(tick: usize, next: usize) -> bool {
    tick >= next && tick <= next + 2
}

/// Every soldier drawn: by (this game's seed, the simulation's origin, match, set, the caster, the slot) - the server's
/// pre-simulation and the match on screen draw their own.
type SoldierKey = (u64, u32, u64, u64, usize, usize);
static SOLDIERS: LazyLock<Mutex<HashMap<SoldierKey, Soldier>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static CHAINS: AtomicUsize = AtomicUsize::new(1);

fn soldier_key(sim: &StableSim<'_>, caster: usize, slot: usize) -> SoldierKey {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index, caster, slot)
}

/// The spot a native in the soldier's landing gets: its position (a unit given instead: where it stands).
fn spot_of(sim: &StableSim<'_>, input: &InputTargetV1) -> Option<(f64, f64)> {
    match InputTargetKindV1::from_code(input.kind) {
        Some(InputTargetKindV1::Pos) => Some((input.x as f64, input.y as f64)),
        Some(InputTargetKindV1::Target) => sim.get_entity(input.target_id).map(|t| at_of(&t)),
        _ => None,
    }
}

/// The soldier's picture `what` (stand, rise, stab) facing its way, where its slot stands off the spot.
fn draw_soldier(sim: &mut StableSim<'_>, me: usize, slot: usize, at: (f64, f64), what: &str, right: bool) {
    let (ox, oy) = SLOT_AT[slot];
    let name = az(&format!("ss_{what}_{}", if right { "r" } else { "l" }));
    sim.play_view_effect(&name, me, &pos_input((at.0 + ox, at.1 + oy)), 0, 0, 0);
}

/// The chain's next stamp, `delay` ticks on (the chain rides in the input's target id).
fn queue_stamp(sim: &mut StableSim<'_>, me: usize, slot: usize, at: (f64, f64), chain: usize, delay: usize) {
    let mut input = pos_input(at);
    input.target_id = chain;
    let name = format!("{ID}:ss_{}", SLOTS[slot]);
    if !sim.queue_effect(&name, AttackTypeV1::Skill, me, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, me)));
    }
}

#[derive(Clone, Copy, Debug)]
enum Step {
    /// `rise_<slot>`: the data's soldier rises on the spot (a new one, or one Conquering Sands moved there).
    Rise,
    /// `sold_<slot>`: one of its checkpoints (every s_step while it stands).
    Seen,
    /// `stab_<slot>`: it stabbed the unit given.
    Stab,
    /// `ss_<slot>`: the next stamp of its chain (queued by this add-on).
    Stamp,
}

struct SoldierFx {
    slot: usize,
    step: Step,
}

impl StableEffectType for SoldierFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        let key = soldier_key(sim, me, self.slot);
        let p = params_of(me);
        let tick = sim.tick();
        let (team, from) = sim.get_entity(me).map_or((0, None), |e| (e.team(), Some(at_of(&e))));
        let s_ = SLOTS[self.slot];
        match self.step {
            Step::Rise | Step::Seen => {
                let Some(at) = spot_of(sim, &input) else {
                    if let Some(k) = counted("no spot") {
                        wlog(format!("{} SOLDIER {s_} #{k}: no spot (input kind {})", head(sim, me), input.kind));
                    }
                    return;
                };
                let rising = matches!(self.step, Step::Rise);
                let until = tick + p.s_step + p.ss_stand;
                let mut map = SOLDIERS.lock().unwrap_or_else(|e| e.into_inner());
                if !rising {
                    if let Some(s) = map.get_mut(&key).filter(|s| dist(s.at, at) <= 1_000.0) {
                        s.until = until;
                        if tick.saturating_sub(s.last) <= REDRAW {
                            return;
                        }
                        // its stamps stopped: draw it now and start the chain again
                        let (at_, right) = (s.at, s.right);
                        s.last = tick;
                        s.next = tick + p.ss_stand;
                        let chain = s.chain;
                        drop(map);
                        draw_soldier(sim, me, self.slot, at_, "stand", right);
                        queue_stamp(sim, me, self.slot, at_, chain, p.ss_stand);
                        if let Some(k) = counted("redraw") {
                            wlog(format!("{} SOLDIER {s_} REDRAWN #{k}: its stamps had stopped", head(sim, me)));
                        }
                        return;
                    }
                }
                if map.len() > MAX_SOLDIERS {
                    map.clear();
                }
                // a new soldier (or one this add-on lost): toward the nearest enemy, else away from him
                let enemy = nearest(sim, team, at, FACE_R).map(|(_, _, e)| e);
                let right = turn_to(at, enemy, from.map_or(true, |f| at.0 >= f.0));
                let chain = CHAINS.fetch_add(1, Ordering::Relaxed);
                let first = if rising { p.ss_rise } else { 1 };
                map.insert(key, Soldier { at, right, chain, stab: None, until, next: tick + first, last: tick });
                drop(map);
                if rising {
                    draw_soldier(sim, me, self.slot, at, "rise", right);
                }
                queue_stamp(sim, me, self.slot, at, chain, first);
                if let Some(k) = counted(if rising { "rise" } else { "found" }) {
                    wlog(format!("{} SOLDIER {s_} {} #{k} at {} (input kind {}), facing {}", head(sim, me),
                                 if rising { "RISES" } else { "FOUND" }, pt(at), input.kind,
                                 if right { "right" } else { "left" }));
                }
            }
            Step::Stab => {
                let target = spot_of(sim, &input);
                if let Some(s) = SOLDIERS.lock().unwrap_or_else(|e| e.into_inner()).get_mut(&key) {
                    s.stab = Some(target.unwrap_or(s.at));
                }
                if let Some(k) = counted("stab") {
                    wlog(format!("{} SOLDIER {s_} STABS #{k} toward {} (input kind {})", head(sim, me),
                                 target.map_or("?".to_string(), pt), input.kind));
                }
            }
            Step::Stamp => {
                let mut map = SOLDIERS.lock().unwrap_or_else(|e| e.into_inner());
                let Some(s) = map.get(&key).copied().filter(|s| stamp_due(tick, s.next)) else { return };
                if tick >= s.until {
                    map.remove(&key);
                    return;
                }
                let (what, right, next) = match s.stab {
                    Some(t) => ("stab", turn_to(s.at, Some(t), s.right), p.ss_stab),
                    None => ("stand", turn_to(s.at, nearest(sim, team, s.at, FACE_R).map(|(_, _, e)| e), s.right),
                             p.ss_stand),
                };
                map.insert(key, Soldier { right, stab: None, next: tick + next, last: tick, ..s });
                drop(map);
                draw_soldier(sim, me, self.slot, s.at, what, right);
                queue_stamp(sim, me, self.slot, s.at, s.chain, next);
                if let Some(k) = counted("stamp") {
                    if k <= 6 || k % 500 == 0 {
                        wlog(format!("{} SOLDIER {s_} STAMP #{k} ({what})", head(sim, me)));
                    }
                }
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
        "=== {ID} v1.4 (the Sun Disc on a fallen tower, the guards facing the charge, soldiers redrawn, the R's timing, E only when it dashes, the wall stands and the insec kicks home) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:disc"), Disc::default());
    // 0.1.1: the R's timing for the AI (insec / peel / held), src/combo.rs
    module.add_player_input_ai(combo::Shurima::default());
    module.add_native_effect(format!("{ID}:r_wall"), Wall);
    // v1.4: the insec's rush round the target to the side away from his team
    module.add_native_effect(format!("{ID}:r_behind"), Behind);
    // the data's stamps alternate the guards' two steps: an odd hop b, an even one a (build_azir.py: "ab"[i % 2])
    for (suffix, view) in [("ra", "r_guards_a"), ("rb", "r_guards_b"), ("la", "r_guards_la"), ("lb", "r_guards_lb")] {
        module.add_native_effect(format!("{ID}:stamp_{suffix}"), Stamp { view });
    }
    for (slot, s) in SLOTS.iter().enumerate() {
        for (what, step) in [("rise", Step::Rise), ("sold", Step::Seen), ("stab", Step::Stab), ("ss", Step::Stamp)] {
            module.add_native_effect(format!("{ID}:{what}_{s}"), SoldierFx { slot, step });
        }
    }
    host.log(LogLevel::Info, "league_azir v1 loaded (Azir's Sun Disc, his guards facing the charge).");
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
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"d_dmg":70,"d_life":1800,"r_stamps":4,"x":1}"#);
        assert_eq!((p.d_dmg, p.d_life, p.r_stamps), (70, 1800, 4));
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_disc_hits_by_his_ability_power() {
        let p = Params::default();
        assert_eq!(disc_damage(&p, 0), 50);
        assert_eq!(disc_damage(&p, 200), 120);
    }

    #[test]
    fn the_wall_stops_where_the_data_stamps_it() {
        let p = Params::default();
        let stops = wall_stops(&p, (100_000.0, 50_000.0), (130_000.0, 50_000.0));
        assert_eq!(stops.len(), 5);
        assert_eq!(stops[0], ((112_000.0, 50_000.0), 4));
        assert_eq!(stops[4], ((160_000.0, 50_000.0), 20));
        let back = wall_stops(&p, (100_000.0, 50_000.0), (70_000.0, 50_000.0));
        assert_eq!(back[4].0, (40_000.0, 50_000.0));
    }

    #[test]
    fn the_guards_face_the_charge() {
        assert!(faces_right((0.0, 0.0), (10_000.0, 0.0), 1));
        assert!(!faces_right((10_000.0, 0.0), (0.0, 0.0), 0));
        assert!(faces_right((0.0, 0.0), (100.0, 9_000.0), 0));
        assert!(!faces_right((0.0, 0.0), (100.0, 9_000.0), 1));
    }

    #[test]
    fn the_wall_stands_where_it_stops_for_r_hold() {
        let p = Params::default();
        let w = standing(&p, (100_000.0, 100_000.0), (130_000.0, 100_000.0), 1000, true);
        assert_eq!(w.mid, (160_000.0, 100_000.0));
        assert_eq!((w.from, w.until), (1020, 1020 + p.r_hold));
    }

    #[test]
    fn the_wall_holds_them_on_their_side() {
        let (mid, dir, half) = ((0.0, 0.0), (1.0, 0.0), 30_000.0);
        // pushed past it: on the far side, left alone
        assert_eq!(hold(mid, dir, half, (20_000.0, 5_000.0), None), (1.0, None));
        // walking back into it: put back on the far face, the same height
        assert_eq!(hold(mid, dir, half, (2_000.0, 5_000.0), Some(1.0)), (1.0, Some((WALL_THICK, 5_000.0))));
        // through it in one step: back too
        assert_eq!(hold(mid, dir, half, (-9_000.0, -4_000.0), Some(1.0)), (1.0, Some((WALL_THICK, -4_000.0))));
        // round the end: free, and on the other side from now on
        assert_eq!(hold(mid, dir, half, (-9_000.0, 40_000.0), Some(1.0)), (-1.0, None));
        // Azir's side stays Azir's side
        assert_eq!(hold(mid, dir, half, (3_000.0, 0.0), Some(-1.0)), (-1.0, Some((-WALL_THICK, 0.0))));
    }

    #[test]
    fn the_insec_rushes_round_to_the_side_away_from_his_team() {
        let p = Params::default();
        // his team to the west: he ends east of the target, whichever side he dashed in from
        assert_eq!(behind(&p, (110_000.0, 0.0), (100_000.0, 0.0), Some((0.0, 0.0))), (115_000.0, 0.0));
        assert_eq!(behind(&p, (90_000.0, 0.0), (100_000.0, 0.0), Some((0.0, 0.0))), (115_000.0, 0.0));
        // no team to find: away from him (the data's RushMoveToBack)
        assert_eq!(behind(&p, (100_000.0, 10_000.0), (100_000.0, 0.0), None), (100_000.0, -15_000.0));
    }

    #[test]
    fn the_views_are_the_data_ones() {
        assert_eq!(az("r_guards_la"), "league_azir_r_guards_la");
        assert_eq!(az("disc_rise"), "league_azir_disc_rise");
        assert_eq!(az("ss_stab_l"), "league_azir_ss_stab_l");
    }

    #[test]
    fn a_soldier_faces_the_nearest_enemy() {
        assert!(turn_to((100_000.0, 0.0), Some((130_000.0, 5_000.0)), false));
        assert!(!turn_to((100_000.0, 0.0), Some((70_000.0, 0.0)), true));
        assert!(turn_to((100_000.0, 0.0), Some((101_000.0, 20_000.0)), true), "straight below: it keeps its way");
        assert!(!turn_to((100_000.0, 0.0), None, false));
    }

    /// The side soldier's tags (tools/art/rig_azir.py) last the ticks the stamps are queued by.
    #[test]
    fn the_side_soldier_tags_last_their_ticks() {
        let fanim = include_str!("../../../league/effects/league_azir_soldier_side#anim.fanim");
        let ms = |tag: &str| -> f64 {
            let at = fanim.find(&format!("\"{tag}\":{{")).unwrap_or_else(|| panic!("no {tag}"));
            let body = &fanim[at..at + fanim[at..].find("]}").unwrap()];
            body.split("\"duration\":").skip(1).map(|d| d.split(',').next().unwrap().parse::<f64>().unwrap()).sum::<f64>()
                * 1000.0
        };
        let p = Params::default();
        for (tag, ticks) in [("stand", p.ss_stand), ("rise", p.ss_rise), ("stab", p.ss_stab)] {
            for side in ["r", "l"] {
                for pre in ["", "hd_"] {
                    let got = ms(&format!("{pre}{tag}_{side}"));
                    let want = ticks as f64 * 1000.0 / 60.0;
                    assert!((got - want).abs() <= 1.0, "{pre}{tag}_{side}: {got} ms against {ticks} ticks");
                }
            }
        }
    }
}
