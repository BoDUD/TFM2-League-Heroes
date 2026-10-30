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
//!   `r_speed`）盖上朝冲锋方向的禁军（朝右 `r_guards_a/b`，朝左 `r_guards_la/lb`，两步轮流）和脚下的沙尘。伤害还是数据那道墙的
//!   （推人见 v1.5）。
//! - v1.4（用户 2026-10-28：「沙皇推开别人后 别人马上就回到那位置」「反推也推不回去」「退完后沙兵秒消失和lol不一样 不卡住位置」）：
//!   **墙立住**：数据那道墙冲到头就没了，被推开的人 0.3 秒就走回来。本包让墙在最后一跳停下的地方再立 `r_hold` tick（英雄联盟
//!   3 秒），横向 `r_half` 宽，禁军一直站着；敌方英雄走不过去（走进墙里就放回他那一边的墙面外，`entity_set_pos`），正在被推、
//!   在冲刺的不挡。**反推绕对方向**：数据的 RushMoveToBack 是冲到目标「背对他自己」的那边，E 冲过了头或从侧面冲上去时墙就推歪、
//!   推反（日志：21 次反推 7 次推向敌方）；副本改调本包的 `league_azir:r_behind`：冲到目标背对他的队伍（`HOME_R` 内的我方英雄，
//!   没有就最近的我方塔）`r_behind` 远的地方，墙从那里把人推回他的队伍。
//! - v1.5（用户 2026-10-29：「压根推不走人也推不回来人」）：**墙把打中的人带到墙外**。数据的击退从被打中的地方推
//!   `r_kb_speed` x `r_kb`（0 到 54000），墙却冲 `r_len`（60000）才立住：经典模拟器里 24 次打中英雄有 12 次停在立住的墙前面
//!   （阿兹尔这边），正推的人就站在墙这边直接走回来，反推的人落在墙线上、被墙放回哪边全看运气。副本把击退换成本包的
//!   `league_azir:r_carry`：墙打中谁，就用强制位移把他带到墙停下的地方再往外 `WALL_THICK` + `CARRY_PAST`（横向不动），
//!   墙立住时刚好到，之后墙挡着他回不来（正推：推离阿兹尔；反推：推进阿兹尔的队伍里）；免疫控制的不带。**反推的冲刺不再冲过头**：
//!   强制位移走的是「速度 x tick」，原来要冲 10770 实际冲了 16000，现在按距离算速度。日志：屏幕上那场的 `WALL` / `CARRY` /
//!   `WALL DOWN` / `BEHIND` 每条都记（预模拟照旧限条数），`WALL DOWN` 写出被带走的英雄最后在墙的哪边。
//! - v1.6（用户 2026-10-29：「沙皇的大还是有问题啊 看日志」）：v1.5 装进游戏后两场 104 道墙，日志里 `CARRY` 一条都没有、
//!   `WALL DOWN` 全是 `carried []`：`r_carry` 一次都没被调到，而击退已经换掉了，墙就一个人都没推动。v1.5 还把 `r_wall`
//!   挪到了墙的最前面（之前一直在最后，那时墙打人、推人都是好的），这两处哪一处让它没调到，日志分不出来。现在不靠它：
//!   **本包自己扫墙的路线**（他的被动每 tick 算一遍：圆心和数据那道墙一样从他站的地方每 tick `r_speed` 走，半径 `r_w`），
//!   扫到的敌方单位 `SWEEP_LAG`（2）tick 后带到墙外（`sweep`；先让数据那道墙打中他，伤害在它身上）；`r_wall` 放回最后；`r_carry` 还留着当第二条路，一道墙只带一次（`take`）。
//!   日志的 `CARRY` 写出是哪条路带的（`by the sweep` / `by the wall's hit`），`WALL DOWN` 写出带走了几个单位。
//! - **沙兵从侧面画，朝敌人，出手时刺**：数据分不出左右，主包的沙兵正面朝镜头、刺的时候不动。副本里每个槽位的沙兵升起、
//!   每个检查点、每次刺都调本包的 `rise_<槽>` / `sold_<槽>` / `stab_<槽>`（拿到沙兵站的地方、被刺的单位）；本包自己画：
//!   升起放侧面的 `ss_rise`，之后每 `ss_stand` tick 盖一次站着的 `ss_stand`，朝它 `FACE_R` 内最近的敌人（先英雄）；
//!   刺过以后下一次改放 `ss_stab`（`ss_stab` tick），朝被刺的那个。每个槽位按 `SLOT_AT` 错开一点（三个站一处时分得开）。
//!   狂沙猛攻把沙兵挪走时新的升起换一条盖章链，旧的那条自己停；检查点不来了（沙兵到时间、换代）就不再盖。
//!   谁放的都画（佛耶戈附身阿兹尔时也一样），不靠被动。
//! - v1.7（用户 2026-10-30：「沙皇和召唤的士兵之间没连接线 LOL是有的」）：**他和沙兵之间连一条流沙线**。英雄联盟从阿兹尔到
//!   牵引半径内（Arise! 的 TETHER RADIUS 660，V7.19 起的指挥距离）的每个沙兵拉一道流沙光束（Azir_Base_W_SoldierIndicator）。
//!   被动每 tick 给每个站着的沙兵（升起完、盖章链还接着）放一段投射物画面 `tether_<像素>`，从他到沙兵画的地方：两头都抬高
//!   `TETHER_LIFT`、各往里收 `TETHER_INSET`（身体盖住两头），游戏把图转向它飞的方向；离得超过 `TETHER_R`（660 x 100）不连。
//!   沙粒每 `FLOW_T` tick 朝沙兵挪一像素。图是本包自己的 `effects/league_azir_tether`（tools/art/fx_azir_tether.py），主包不动。
//!   线靠被动画：沙兵只有阿兹尔自己放（佛耶戈附身用的是五套通用招式，召不出沙兵）。
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

/// One more of a kind: its count.
fn bump(kind: &'static str) -> usize {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    *n
}

/// The first LOG_FIRST of a kind, then every LOG_EVERY-th: the count, or None (not logged).
fn counted(kind: &'static str) -> Option<usize> {
    let n = bump(kind);
    (n <= LOG_FIRST || n % LOG_EVERY == 0).then_some(n)
}

/// Like `counted`, but every one in the match on screen (watched, spectated or replayed): the server's pre-simulations
/// run the same match many times over, the one the user watches is the one to read.
fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let on_screen = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    let n = bump(kind);
    (on_screen || n <= LOG_FIRST || n % LOG_EVERY == 0).then_some(n)
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
    /// 冲锋的墙（数据那道线）的半径：本包扫墙的路线时用（v1.6）。
    pub r_w: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { d_life: 2700, d_per: 60, d_range: 45000, d_dmg: 50, d_ap: 35, d_near: 60000, r_speed: 3000, r_len: 60000,
               r_stamps: 5, s_step: 40, ss_stand: 4, ss_rise: 20, ss_stab: 16, r_rush: 8000, r_behind: 15000,
               r_hold: 180, r_half: 30000, r_w: 20000 }
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
            "r_w" => p.r_w = v,
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
        if alive {
            tethers(sim, me, team, tick, here);
        }
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
        let (up_mid, up_from) = (up.mid, up.from);
        let key = wall_key(sim, me);
        WALLS.lock().unwrap_or_else(|e| e.into_inner()).entry(key).or_default().push(up);
        for (i, (at, delay)) in stops.iter().enumerate() {
            let name = format!("{ID}:stamp_{}{}", if right { "r" } else { "l" }, if (i + 1) % 2 == 1 { "b" } else { "a" });
            if !sim.queue_effect(&name, AttackTypeV1::Skill, me, &pos_input(*at), *delay) {
                wlog(format!("{} queue_effect({name}) refused", head(sim, me)));
            }
        }
        if let Some(k) = tally(sim, "wall") {
            wlog(format!("{} WALL #{k} from {} toward {}: facing {}, {} stops, stands at {} from tick {}", head(sim, me),
                         pt(from), pt(to), if right { "right" } else { "left" }, stops.len(), pt(up_mid), up_from));
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
/// 墙打中的人带到墙停下的地方再往外：墙的厚度一半（`WALL_THICK`）再多这么远（身体落在墙外，不贴着墙）。
pub const CARRY_PAST: f64 = 4_000.0;
/// 带人最快每 tick 这么远（墙快到头时才打中的，赶不上墙立住也不瞬移过去）。
pub const CARRY_MAX_SPEED: usize = 12_000;
/// 本包扫到一个单位后等这么多 tick 再带走：数据那道墙（伤害在它身上）先打中他，带走以后它追不上（它的圆心还比本包算的
/// 偏一点：经典模拟器里飞行物从他身上 5000 外出发）。
pub const SWEEP_LAG: usize = 2;

pub type Pt = (f64, f64);

fn unit(v: Pt) -> Option<Pt> {
    let d = (v.0 * v.0 + v.1 * v.1).sqrt();
    (d > 1.0).then(|| (v.0 / d, v.1 / d))
}

/// 一道墙：冲锋时（从 `start`、`launch` 那个 tick 起，每 tick `speed`，半径 `reach`）和立住时（中点、冲锋方向的单位向量、
/// 从哪个 tick 立到哪个 tick、禁军朝哪边、每个敌方英雄在墙的哪一边：+1 冲锋方向那边、-1 阿兹尔这边、下一次盖禁军的 tick、
/// 挡回来几次）；被墙带着走的单位（到哪个 tick 落地）、被带走的英雄和没带走的英雄（日志用）。
#[derive(Clone, Debug)]
pub struct Standing {
    pub start: Pt,
    pub launch: usize,
    pub speed: usize,
    pub reach: f64,
    pub mid: Pt,
    pub dir: Pt,
    pub from: usize,
    pub until: usize,
    pub right: bool,
    pub sides: HashMap<usize, f64>,
    pub next_stamp: usize,
    pub held: usize,
    pub carried: HashMap<usize, usize>,
    pub pending: HashMap<usize, usize>,
    pub moved: usize,
    pub took: Vec<usize>,
    pub skipped: Vec<usize>,
}

/// 墙立在哪：数据那道墙最后一跳停下的地方（从他站的地方朝目标 r_len），r_len / r_speed tick 后立住，再立 r_hold tick。
pub fn standing(p: &Params, from: Pt, to: Pt, tick: usize, right: bool) -> Standing {
    let dir = unit((to.0 - from.0, to.1 - from.1)).unwrap_or((1.0, 0.0));
    let len = p.r_len as f64;
    let up = tick + (p.r_len / p.r_speed.max(1)).max(1);
    Standing { start: from, launch: tick, speed: p.r_speed.max(1), reach: p.r_w as f64,
               mid: (from.0 + dir.0 * len, from.1 + dir.1 * len), dir, from: up, until: up + p.r_hold, right,
               sides: HashMap::new(), next_stamp: up, held: 0, carried: HashMap::new(), pending: HashMap::new(), moved: 0,
               took: Vec::new(), skipped: Vec::new() }
}

/// 冲锋的墙在 `tick` 的圆心：和数据那道墙一样从 `start` 每 tick `speed` 朝冲锋方向走，冲到立住的地方停下。
pub fn wall_center(w: &Standing, tick: usize) -> Pt {
    let len = dist(w.start, w.mid);
    let gone = (tick.saturating_sub(w.launch) as f64 * w.speed as f64).min(len);
    (w.start.0 + w.dir.0 * gone, w.start.1 + w.dir.1 * gone)
}

/// 冲锋的墙在 `tick` 扫到了站在 `at`、身体半径 `body` 的单位（墙冲锋的那几 tick：`launch` 到立住的 `from`）。
pub fn swept(w: &Standing, tick: usize, at: Pt, body: f64) -> bool {
    tick >= w.launch && tick <= w.from && dist(wall_center(w, tick), at) <= w.reach + body
}

/// 墙带走一个在 `at` 的单位：一道墙只带一次（本包扫到的、数据那道墙打中的，谁先算谁）；记下他到哪个 tick 落地，英雄再记
/// 「在墙那一边」和被带走（日志用）。返回强制位移的计划（`carry_plan`）；带过了、已经在墙外面就是 None。
pub fn take(w: &mut Standing, id: usize, at: Pt, champ: bool, now: usize) -> Option<(Pt, f64, usize, usize)> {
    if w.carried.contains_key(&id) {
        return None;
    }
    let plan = carry_plan(w, at, now, w.speed)?;
    w.carried.insert(id, now + plan.2 + 2);
    w.moved += 1;
    if champ {
        w.sides.insert(id, 1.0);
        w.took.push(id);
    }
    Some(plan)
}

/// 离墙多远（沿冲锋方向；正数在墙的那一边，负数在阿兹尔这边）。
pub fn along(w: &Standing, at: Pt) -> f64 {
    (at.0 - w.mid.0) * w.dir.0 + (at.1 - w.mid.1) * w.dir.1
}

/// 墙在 `now` 打中一个在 `at` 的敌人：把他带到墙停下的地方再往外 `WALL_THICK` + `CARRY_PAST`（横向不动），墙立住时到
/// （至少墙的速度 `wall_speed`，最快 `CARRY_MAX_SPEED`）。返回（落点、距离、tick 数、速度）：强制位移走的是速度 x tick，
/// 所以速度按 tick 数重新算，走的就是这段距离。已经在那外面了就不带。
pub fn carry_plan(w: &Standing, at: Pt, now: usize, wall_speed: usize) -> Option<(Pt, f64, usize, usize)> {
    let len = WALL_THICK + CARRY_PAST - along(w, at);
    if len < 1.0 {
        return None;
    }
    let lo = wall_speed.max(1);
    let left = w.from.saturating_sub(now).max(1) as f64;
    let fast = ((len / left).ceil() as usize).clamp(lo, CARRY_MAX_SPEED.max(lo));
    let ticks = ((len / fast as f64).ceil() as usize).max(1);
    let speed = (len / ticks as f64).ceil() as usize;
    Some(((at.0 + w.dir.0 * len, at.1 + w.dir.1 * len), len, ticks, speed))
}

/// 被带走的人落地后在墙的哪一边：到了墙里或墙外就是墙那一边（+1，之后墙挡着他回不来）；离墙还远（被地形挡住）就是
/// 阿兹尔这边（-1，墙不把他瞬移过去）。
pub fn side_after_carry(w: &Standing, at: Pt) -> f64 {
    if along(w, at) >= -WALL_THICK { 1.0 } else { -1.0 }
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

fn immune(u: &StableEntity<'_, '_>) -> bool {
    (0..u.buff_count()).filter_map(|i| u.buff_at(i)).any(|b| b.cc_immune)
}

/// 用强制位移把 `id` 带到计划的落点（`carry_plan`：速度 x tick 就是那段距离）。
fn shove(sim: &mut StableSim<'_>, id: usize, at: Pt, (dest, _, ticks, speed): (Pt, f64, usize, usize)) {
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (dest.0 - at.0).round() as i64;
    cc.dy = (dest.1 - at.1).round() as i64;
    cc.speed = speed as u64;
    sim.apply_cc(id, &cc);
}

/// 墙冲锋的那几 tick（每 tick，他的被动里）：本包自己扫墙的路线（`swept`，和数据那道墙一样的圆心、半径、速度），扫到的
/// 敌方单位（英雄、小兵、野怪，不算塔）`SWEEP_LAG` tick 后带到墙外（`take`；先让数据那道墙打中他，伤害在它身上）；免疫控制的
/// 不带。不靠数据那道墙打中时调 `r_carry`：0.1.5 只有那一条路，用户 2026-10-29 的两场里一次都没调到（日志 0 条 CARRY），墙就
/// 一个人都没推动。
fn sweep(sim: &mut StableSim<'_>, me: usize, team: usize, tick: usize, w: &mut Standing) {
    let units: Vec<(usize, Pt, bool, bool, f64)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
        .filter(|u| !matches!(u.kind(), Some(EntityKindV1::Nexus | EntityKindV1::Tower)))
        .map(|u| (u.id(), at_of(&u), u.is_champion(), immune(&u), u.radius() as f64))
        .collect();
    for (id, at, champ, immune, body) in units {
        if w.carried.contains_key(&id) || w.skipped.contains(&id) {
            continue;
        }
        match w.pending.get(&id) {
            None => {
                if swept(w, tick, at, body) {
                    w.pending.insert(id, tick + SWEEP_LAG);
                }
                continue;
            }
            Some(&due) if tick < due => continue,
            Some(_) => {
                w.pending.remove(&id);
            }
        }
        if immune {
            w.skipped.push(id);
            if champ {
                if let Some(k) = tally(sim, "carry") {
                    wlog(format!("{} CARRY #{k} #{id} at {}: immune to crowd control, not carried (by the sweep)",
                                 head(sim, me), pt(at)));
                }
            }
            continue;
        }
        let from_wall = along(w, at);
        let Some(plan) = take(w, id, at, champ, tick) else { continue };
        shove(sim, id, at, plan);
        if champ {
            if let Some(k) = tally(sim, "carry") {
                wlog(format!("{} CARRY #{k} #{id} at {} ({from_wall:+.0} from the wall) -> {}: {:.0} in {} ticks (by the sweep)",
                             head(sim, me), pt(at), pt(plan.0), plan.1, plan.2));
            }
        }
    }
}

/// 每 tick（他的被动里）：冲锋的墙扫人、带到墙外（`sweep`）；立着的墙盖禁军、挡敌方英雄，到时候撤掉。
fn walls_tick(sim: &mut StableSim<'_>, me: usize, team: usize, tick: usize, p: &Params) {
    let key = wall_key(sim, me);
    let Some(mut walls) = WALLS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key) else { return };
    let half = p.r_half as f64;
    for w in walls.iter_mut() {
        if tick <= w.from + SWEEP_LAG {
            sweep(sim, me, team, tick, w);
        }
        if tick < w.from {
            continue;
        }
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
            if let Some(&end) = w.carried.get(&id) {
                if tick < end {
                    continue; // the wall is carrying him past it
                }
                w.carried.remove(&id);
                let side = side_after_carry(w, at);
                w.sides.insert(id, side);
            } else if fly {
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
        if let Some(k) = tally(sim, "wall_down") {
            // where the champions it carried are now: + past it (on the far side), - on his side
            let took: Vec<String> = w.took.iter()
                .map(|&id| match sim.get_entity(id).filter(|u| u.is_alive()) {
                    Some(u) => format!("#{id} {:+.0}", along(&w, at_of(&u))),
                    None => format!("#{id} dead"),
                })
                .collect();
            wlog(format!("{} WALL DOWN #{k} at {}: held enemy champions back {} time(s); carried {} unit(s), champions [{}]",
                         head(sim, me), pt(w.mid), w.held, w.moved, took.join(", ")));
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
        // a forced move goes speed x ticks (dx / dy only aim it): the speed from the ticks, or he overshoots (10770 asked,
        // 16000 gone in the log of 2026-10-29)
        let ticks = ((len / p.r_rush.max(1) as f64).ceil() as u64).max(1);
        let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks);
        cc.dx = dx.round() as i64;
        cc.dy = dy.round() as i64;
        cc.speed = ((len / ticks as f64).ceil() as u64).max(1);
        sim.apply_cc(me, &cc);
        if let Some(k) = tally(sim, "behind") {
            wlog(format!("{} BEHIND #{k}: from {} round the target at {} to {} ({:.0} in {ticks} ticks), his team {}",
                         head(sim, me), pt(here), pt(target), pt(spot), len,
                         home.map_or("unknown (away from him)".to_string(), |h| format!("at {}", pt(h)))));
        }
    }
}

/// 墙打中一个敌方单位（副本把数据的击退换成了 `league_azir:r_carry`，墙打中的每个敌方单位一次）：和本包自己扫墙的路线
/// （`sweep`）是两条路，谁先算谁（`take`：一道墙只带一次）。0.1.5 只有这一条，游戏里一次都没调到；它调到了、拿到的输入
/// 不是被打中的单位，日志都记一行（`CARRY ... by the wall's hit` / `r_carry got input kind`），看是哪一环断的。
struct Carry;

impl StableEffectType for Carry {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, me: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            if let Some(k) = tally(sim, "carry input") {
                wlog(format!("{} r_carry got input kind {} (not a unit hit): left to the sweep #{k}", head(sim, me), input.kind));
            }
            return;
        }
        let id = input.target_id;
        let (at, champ, immune) = {
            let Some(u) = sim.get_entity(id) else { return };
            if !u.is_alive() || u.is_tower() || matches!(u.kind(), Some(EntityKindV1::Nexus | EntityKindV1::Tower)) {
                return;
            }
            (at_of(&u), u.is_champion(), immune(&u))
        };
        let now = sim.tick();
        let key = wall_key(sim, me);
        let plan = {
            let mut walls = WALLS.lock().unwrap_or_else(|e| e.into_inner());
            match walls.get_mut(&key).and_then(|v| v.last_mut()) {
                None => Err("no wall of his recorded yet: left to the sweep"),
                Some(w) if w.carried.contains_key(&id) => Err("already carried by the sweep"),
                Some(w) if immune => {
                    if !w.skipped.contains(&id) {
                        w.skipped.push(id);
                    }
                    Err("immune to crowd control: not carried (the wall stands all the same)")
                }
                Some(w) => {
                    let from_wall = along(w, at);
                    take(w, id, at, champ, now).map(|plan| (plan, from_wall)).ok_or("already past where the wall stops")
                }
            }
        };
        match plan {
            Ok((plan, from_wall)) => {
                shove(sim, id, at, plan);
                if champ {
                    if let Some(k) = tally(sim, "carry") {
                        wlog(format!("{} CARRY #{k} #{id} at {} ({from_wall:+.0} from the wall) -> {}: {:.0} in {} ticks (by the wall's hit)",
                                     head(sim, me), pt(at), pt(plan.0), plan.1, plan.2));
                    }
                }
            }
            Err(why) => {
                if champ {
                    if let Some(k) = tally(sim, "carry") {
                        wlog(format!("{} CARRY #{k} #{id} at {}: {why} (the wall's hit)", head(sim, me), pt(at)));
                    }
                }
            }
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
    /// 0.1.7: the tick it stands, out of the sand (its line to him starts then).
    up: usize,
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
                let up = if rising { tick + p.ss_rise } else { tick };
                map.insert(key, Soldier { at, right, chain, stab: None, until, next: tick + first, last: tick, up });
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

// ===================== 沙兵和他之间的流沙线（0.1.7） =====================

/// League's tether radius (Arise!'s TETHER RADIUS 660, the soldiers' command range since V7.19; League's 525 range is
/// atk_range 52500 here): a soldier within this of him is joined to him by a line of sand.
pub const TETHER_R: f64 = 66_000.0;
/// The line runs this far over both pivots (a unit's pivot is 11 px over its soles, a soldier's spot too), game units:
/// his waist, the soldier's chest.
pub const TETHER_LIFT: f64 = 5_000.0;
/// It starts and ends this far inside him and the soldier, game units: the flow and the even lengths move each end up
/// to 3 px, still behind the bodies (the line is drawn under the units, z -1).
pub const TETHER_INSET: f64 = 3_000.0;
/// The pieces drawn (tools/art/fx_azir_tether.py: `tether_<px>` for px in TETHER_MIN..=TETHER_MAX step 2).
pub const TETHER_MIN: usize = 8;
pub const TETHER_MAX: usize = 64;
/// The sand flows toward the soldier a px every FLOW_T ticks; its grains repeat every FLOW_P px.
pub const FLOW_T: usize = 2;
pub const FLOW_P: usize = 3;

/// The piece of the line drawn on `tick` between him at `a` and the soldier at `b` (both already raised): its length
/// (px: the tag `tether_<px>`), its centre and the way it points (toward the soldier); None when they stand too far
/// apart or on top of each other. Whatever the phase it covers a + INSET to b - INSET: it starts FLOW_P - 1 - phase px
/// before a + INSET (the grains move a px toward the soldier a phase) and is the gap and FLOW_P - 1 px more, rounded up
/// to an even length.
pub fn tether_piece(a: Pt, b: Pt, tick: usize) -> Option<(usize, Pt, Pt)> {
    let d = dist(a, b);
    let gap = d - 2.0 * TETHER_INSET;
    if d > TETHER_R || gap < 2_000.0 {
        return None;
    }
    let u = unit((b.0 - a.0, b.1 - a.1))?;
    let need = gap / 1_000.0 + (FLOW_P - 1) as f64;
    let len = ((need / 2.0).ceil() as usize * 2).max(TETHER_MIN);
    if len > TETHER_MAX {
        return None;
    }
    let phase = (tick / FLOW_T) % FLOW_P;
    let mid = TETHER_INSET - (FLOW_P - 1 - phase) as f64 * 1_000.0 + len as f64 * 500.0;
    Some((len, (a.0 + u.0 * mid, a.1 + u.1 * mid), u))
}

/// Is the soldier drawn on `tick`: out of the sand (`up`), its checkpoints still coming (`until`), its chain of stamps
/// going (the next one due at `next`, taken up to two ticks late: `stamp_due`)?
pub fn standing_up(up: usize, until: usize, next: usize, tick: usize) -> bool {
    tick >= up && tick < until && tick <= next + 2
}

/// One piece of the line: the projectile picture `tether_<len>` at `c` pointing along `dir` (the game turns a
/// projectile's picture to its direction), gone after a tick (league_akshan's rope, league_illaoi's tether).
fn tether_spawn(sim: &mut StableSim<'_>, me: usize, team: usize, len: usize, c: Pt, dir: Pt) -> bool {
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team,
        x: ux(c.0),
        y: ux(c.1),
        radius: 1_000,
        speed: 1_000,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: ux(c.0 + dir.0 * 1_000.0),
        target_y: ux(c.1 + dir.1 * 1_000.0),
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Position.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    sim.spawn_projectile(&az(&format!("tether_{len}")), &format!("{ID}:noop"), &spec)
}

/// Every tick (his passive, while he lives): a piece of the line to each soldier of his standing within TETHER_R.
fn tethers(sim: &mut StableSim<'_>, me: usize, team: usize, tick: usize, here: Pt) {
    let a = (here.0, here.1 - TETHER_LIFT);
    let pieces: Vec<(usize, usize, Pt, Pt)> = {
        let map = SOLDIERS.lock().unwrap_or_else(|e| e.into_inner());
        (0..SLOTS.len())
            .filter_map(|slot| {
                let s = map.get(&soldier_key(sim, me, slot)).filter(|s| standing_up(s.up, s.until, s.next, tick))?;
                let (ox, oy) = SLOT_AT[slot];
                let (len, c, u) = tether_piece(a, (s.at.0 + ox, s.at.1 + oy - TETHER_LIFT), tick)?;
                Some((slot, len, c, u))
            })
            .collect()
    };
    for (slot, len, c, u) in pieces {
        if !tether_spawn(sim, me, team, len, c, u) {
            if let Some(k) = counted("tether refused") {
                wlog(format!("{} TETHER {} #{k}: spawn_projectile refused tether_{len}", head(sim, me), SLOTS[slot]));
            }
        } else if let Some(k) = counted("tether") {
            if k <= 6 || k % 5_000 == 0 {
                wlog(format!("{} TETHER {} #{k}: tether_{len} at {} pointing ({:.2},{:.2})", head(sim, me), SLOTS[slot],
                             pt(c), u.0, u.1));
            }
        }
    }
}

/// The line's pieces hit nothing (a projectile needs an effect to apply on a hit).
struct Noop;

impl StableEffectType for Noop {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1.7 (the Sun Disc on a fallen tower, the guards facing the charge, soldiers redrawn, the R's timing, E only when it dashes, the wall stands and the insec kicks home, the wall sweeps its path and carries them past it, a line of sand to each soldier) loaded: game {}.{}.{} abi {} log={} ===",
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
    // v1.5: the wall carries everyone it hits past where it stops (the data's Knockback left half of them short); from v1.6
    // the passive's sweep does it too (walls_tick), this is the second way in
    module.add_native_effect(format!("{ID}:r_carry"), Carry);
    // the data's stamps alternate the guards' two steps: an odd hop b, an even one a (build_azir.py: "ab"[i % 2])
    for (suffix, view) in [("ra", "r_guards_a"), ("rb", "r_guards_b"), ("la", "r_guards_la"), ("lb", "r_guards_lb")] {
        module.add_native_effect(format!("{ID}:stamp_{suffix}"), Stamp { view });
    }
    for (slot, s) in SLOTS.iter().enumerate() {
        for (what, step) in [("rise", Step::Rise), ("sold", Step::Seen), ("stab", Step::Stab), ("ss", Step::Stamp)] {
            module.add_native_effect(format!("{ID}:{what}_{s}"), SoldierFx { slot, step });
        }
    }
    // 0.1.7: the line of sand to each soldier (the passive spawns its pieces; they hit nothing)
    module.add_native_effect(format!("{ID}:noop"), Noop);
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
    fn the_wall_carries_them_past_where_it_stands() {
        let p = Params::default();
        // the wall from (100000, 100000) eastward stops at (160000, 100000) and stands from tick 1020
        let w = standing(&p, (100_000.0, 100_000.0), (130_000.0, 100_000.0), 1000, true);
        let past = WALL_THICK + CARRY_PAST;
        for (at, now) in [((130_000.0, 105_000.0), 1005), ((100_000.0, 90_000.0), 1001), ((155_000.0, 100_000.0), 1016)] {
            let (dest, len, ticks, speed) = carry_plan(&w, at, now, p.r_speed).expect("short of the wall: carried");
            // past the far face, at the same height across the wall
            assert_eq!(dest, (160_000.0 + past, at.1));
            assert!((len - (160_000.0 + past - at.0)).abs() < 1e-6);
            // a forced move goes speed x ticks: that is the distance (rounded up by less than a tick's worth)
            assert!(speed * ticks >= len as usize && ((speed * ticks) as f64) < len + ticks as f64, "{speed} x {ticks}");
            // there by the time the wall stands
            assert!(speed <= CARRY_MAX_SPEED);
            assert!(now + ticks <= w.from, "{now} + {ticks} after {}", w.from);
        }
        // hit just before it stops: as fast as a carry goes, a tick or two late (the wall lets him through meanwhile)
        let (_, _, ticks, speed) = carry_plan(&w, (150_000.0, 100_000.0), 1019, p.r_speed).unwrap();
        assert_eq!((ticks, speed), (2, 10_000));
        // already past it: left alone
        assert_eq!(carry_plan(&w, (175_000.0, 100_000.0), 1005, p.r_speed), None);
    }

    #[test]
    fn once_carried_the_wall_keeps_them_past_it() {
        let p = Params::default();
        let w = standing(&p, (0.0, 0.0), (30_000.0, 0.0), 0, true);
        let half = p.r_half as f64;
        // landed past it: the far side, and walking back into it puts him back on the far face
        let side = side_after_carry(&w, (70_000.0, 2_000.0));
        assert_eq!(side, 1.0);
        assert_eq!(hold(w.mid, w.dir, half, (62_000.0, 2_000.0), Some(side)), (1.0, Some((60_000.0 + WALL_THICK, 2_000.0))));
        // a tenacious one stopped inside it: still the far side, out of it on that face
        let side = side_after_carry(&w, (57_000.0, 0.0));
        assert_eq!(hold(w.mid, w.dir, half, (57_000.0, 0.0), Some(side)), (1.0, Some((60_000.0 + WALL_THICK, 0.0))));
        // stopped well short (a wall of the map in the way): his side, not pulled through
        assert_eq!(side_after_carry(&w, (30_000.0, 0.0)), -1.0);
    }

    #[test]
    fn the_sweep_follows_the_data_wall() {
        let p = Params::default();
        // launched at tick 1000 from (100000, 100000) eastward: the centre 3000 a tick, radius 20000, stands at
        // (160000, 100000) from tick 1020
        let w = standing(&p, (100_000.0, 100_000.0), (130_000.0, 100_000.0), 1000, true);
        assert_eq!(wall_center(&w, 1000), (100_000.0, 100_000.0));
        assert_eq!(wall_center(&w, 1004), (112_000.0, 100_000.0));
        assert_eq!(wall_center(&w, 1030), (160_000.0, 100_000.0), "it stops where it stands");
        let body = 2_000.0;
        // 40000 ahead: reached once the centre is within 22000 of it - tick 1006 (118000), not 1005 (115000)
        assert!(!swept(&w, 1005, (140_000.0, 100_000.0), body));
        assert!(swept(&w, 1006, (140_000.0, 100_000.0), body));
        // beside its path, out of its reach
        assert!(!swept(&w, 1010, (130_000.0, 125_000.0), body));
        // at his feet, behind him: swept on the launch
        assert!(swept(&w, 1000, (90_000.0, 100_000.0), body));
        // past where it stops and out of reach: never; and nothing once it stands
        assert!(!swept(&w, 1020, (185_000.0, 100_000.0), body));
        assert!(!swept(&w, 1021, (160_000.0, 100_000.0), body));
    }

    #[test]
    fn a_wall_carries_each_unit_once() {
        let p = Params::default();
        let mut w = standing(&p, (100_000.0, 100_000.0), (130_000.0, 100_000.0), 1000, true);
        let first = take(&mut w, 7, (130_000.0, 100_000.0), true, 1005).expect("short of the wall: carried");
        assert_eq!(first.0, (160_000.0 + WALL_THICK + CARRY_PAST, 100_000.0));
        assert_eq!(w.sides.get(&7), Some(&1.0));
        assert_eq!((w.took.clone(), w.moved), (vec![7], 1));
        // the wall's hit after the sweep (or the other way round): not twice
        assert_eq!(take(&mut w, 7, (140_000.0, 100_000.0), true, 1007), None);
        // a minion: carried, no side kept (the wall holds champions only)
        assert!(take(&mut w, 900, (120_000.0, 95_000.0), false, 1004).is_some());
        assert_eq!((w.sides.get(&900), w.moved), (None, 2));
        // past it already: left alone
        assert_eq!(take(&mut w, 8, (175_000.0, 100_000.0), true, 1005), None);
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

    /// Where a piece starts and ends along the line from `a`, game units.
    fn ends(a: Pt, (len, c, u): (usize, Pt, Pt)) -> (f64, f64) {
        let mid = (c.0 - a.0) * u.0 + (c.1 - a.1) * u.1;
        (mid - len as f64 * 500.0, mid + len as f64 * 500.0)
    }

    /// The line covers him to the soldier at every phase, its ends inside the two bodies (within the insets), in an
    /// even length the sheet has, pointing at the soldier.
    #[test]
    fn the_tether_runs_from_him_to_the_soldier() {
        let lines = [((100_000.0, 100_000.0), (140_000.0, 100_000.0)), ((100_000.0, 100_000.0), (70_000.0, 130_000.0)),
                     ((200_000.0, 50_000.0), (200_000.0, 100_000.0)), ((0.0, 0.0), (9_000.0, 4_000.0)),
                     ((0.0, 0.0), (TETHER_R, 0.0))];
        for (a, b) in lines {
            let d = dist(a, b);
            for tick in 0..FLOW_T * FLOW_P {
                let piece = tether_piece(a, b, tick).expect("in reach");
                let (len, _, u) = piece;
                assert!(len % 2 == 0 && (TETHER_MIN..=TETHER_MAX).contains(&len), "{d}: length {len}");
                assert!((u.0 - (b.0 - a.0) / d).abs() < 1e-9 && (u.1 - (b.1 - a.1) / d).abs() < 1e-9, "{d}: {u:?}");
                let (s, e) = ends(a, piece);
                assert!((0.0..=TETHER_INSET + 1e-6).contains(&s), "{d}: starts {s}");
                assert!(e >= d - TETHER_INSET - 1e-6 && e <= d + TETHER_INSET + 1e-6, "{d}: ends {e}");
            }
        }
    }

    /// The grains move a px toward the soldier every FLOW_T ticks: the piece's start does, and goes back FLOW_P - 1 px
    /// at the wrap (the grains, FLOW_P px apart, then look one px further on).
    #[test]
    fn the_sand_flows_toward_the_soldier() {
        let (a, b) = ((100_000.0, 100_000.0), (130_000.0, 120_000.0));
        let start = |tick: usize| ends(a, tether_piece(a, b, tick).unwrap()).0;
        for k in 0..FLOW_P - 1 {
            assert!((start((k + 1) * FLOW_T) - start(k * FLOW_T) - 1_000.0).abs() < 1e-6, "phase {k}");
            assert!((start(k * FLOW_T + FLOW_T - 1) - start(k * FLOW_T)).abs() < 1e-6, "still for FLOW_T ticks");
        }
        let back = start(FLOW_P * FLOW_T) - start((FLOW_P - 1) * FLOW_T);
        assert!((back + (FLOW_P - 1) as f64 * 1_000.0).abs() < 1e-6, "wrap {back}");
    }

    #[test]
    fn no_tether_out_of_reach_or_on_top_of_him() {
        let a = (100_000.0, 100_000.0);
        assert!(tether_piece(a, (a.0 + TETHER_R + 1.0, a.1), 0).is_none());
        assert!(tether_piece(a, (a.0, a.1 - TETHER_R), 0).is_some());
        assert!(tether_piece(a, (a.0 + 7_000.0, a.1), 0).is_none());
        assert!(tether_piece(a, a, 0).is_none());
    }

    /// Risen on tick 100 (ss_rise 20): up from 120, its next stamp due on 124, its checkpoints keeping it to 150.
    #[test]
    fn the_tether_waits_for_the_soldier_to_stand() {
        assert!(!standing_up(120, 150, 124, 119), "still rising");
        assert!(standing_up(120, 150, 124, 120));
        assert!(standing_up(120, 150, 124, 126), "a stamp up to two ticks late");
        assert!(!standing_up(120, 150, 124, 127), "its stamps stopped");
        assert!(!standing_up(120, 150, 160, 150), "its checkpoints stopped");
    }

    /// Every length the passive can draw is a tag of the sheet (tools/art/fx_azir_tether.py) and a view of the copy
    /// (make_override.py).
    #[test]
    fn every_tether_length_is_drawn_and_a_view() {
        let fanim = include_str!("../effects/league_azir_tether#anim.fanim");
        let copy = include_str!("../override/league_azir.data_champion");
        for len in (TETHER_MIN..=TETHER_MAX).step_by(2) {
            assert!(fanim.contains(&format!("\"tether_{len}\":")), "tether_{len} not in the sheet");
            assert!(copy.contains(&format!("\"name\": \"{}\"", az(&format!("tether_{len}")))), "tether_{len} not a view");
        }
        assert!(!fanim.contains(&format!("\"tether_{}\":", TETHER_MAX + 2)));
        assert!(copy.contains("\"anim\": \"asset/league_azir/effects/league_azir_tether\""));
    }
}
