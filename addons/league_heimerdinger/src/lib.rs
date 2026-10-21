//! 黑默丁格附加包：照英雄联盟做主包数据做不到的炮台射击和塔边加速（用户 2026-10-21：中单、技能方案 A、「做附加包啊」）。
//!
//! 主包保持纯数据：数据没有召唤物，炮台是落点上的周期区域（每座三个区域：受控英雄、英雄、其他敌人），伤害在目标身上当场结算，
//! **看不到炮弹从炮台飞出去**；被动（海克斯科技亲和）是炮台的光环区域，**只认他自己的炮台、不认己方防御塔**。`mod.override_info`
//! 把主包的黑默丁格换成 `override/` 里的副本（`tools/kit/build_heimerdinger.py --native`）：
//!
//! - **炮台由本包来打**：副本的炮台保留画面、音效和三个槽位（最多 3 座），但没有区域；Q 放炮台和 R 的巨型炮台那一 tick 跑本包的
//!   `league_heimerdinger:q` / `:x`（拿施法的方向或目标），炮台站在隐形弹停下的地方（朝那个方向 `q_place` 远，`q_place / q_speed`
//!   tick 后），和数据的炮台图同一个点。
//! - **炮台侧面朝敌人**（用户：「炮台改成侧面朝敌人」「灵活利用PPU 炮也可以调的清晰」）：目标在他左边时 `:q` / `:x` 给他挂
//!   `league_heimerdinger_t_face_l` / `_x_face_l`（`FACE_T` tick），副本的隐形弹落地时据此画朝左的侧面炮台
//!   （`league_heimerdinger_turret_l` / `_apex_l`），否则朝右（`_r`）。主包不知道目标在哪边，还是正面朝镜头的炮台。
//! - **从炮口射出看得见的炮弹**：炮台照主包区域的节奏（站稳后 `t_first` / `x_first` tick 第一发、之后每 `t_per` / `x_per`，
//!   和炮台图的炮口闪光对齐）打一个敌人：先打范围内**受控制的英雄**（击飞、眩晕、禁锢、强制位移、恐惧、魅惑：游戏 `EnemyChampionInCC`
//!   的六种）发射充能光束（`t_beam_line`，`tb_dmg` + `tb_ratio`% 法强），没有就打最近的敌方英雄，再没有就打最近的小兵、野怪
//!   （防御塔不打），发射炮弹（`t_shot`，`t_dmg` + `t_ratio`%）；巨型炮台的等离子弹（`x_shot`）还减速 `x_slow`%。
//!   炮弹从侧面炮台的炮口（`T_MUZZLE` / `X_MUZZLE`，朝左时左右反过来）飞向目标（`spawn_projectile`），**飞到才扣血**
//!   （游戏 0.6.4 的 `deal_damage_typed` 只把伤害排进效果队列）。
//! - **海克斯科技亲和**：他活着时每 `p_per` tick 看一次，站在自己的炮台 `p_r` 内或己方防御塔 `p_tr` 内就加 `p_ms`% 移速
//!   `p_t` tick（主包的 `league_heimerdinger_haste`，画面照旧）。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态记在每个黑默丁格自己的被动实例里，
//! 原生效果把炮台交给被动时按（这局的种子、模拟的来源、他的编号）分开，服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_heimerdinger.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `SPAWN`（他出场和参数）、`PUT`（炮台站下，施法输入的种类）、`SHOT`（炮台出手）、`HASTE`（加速，塔边还是炮台边）、
//! `WATCH`（每 30 秒的计数），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_heimerdinger";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";
/// 侧面炮台朝右时炮口离炮台的点多远（游戏像素 x 1000：往前、往上；tools/art/import_heimerdinger_fx.py 写的
/// assets/source/heimerdinger/hd/side_muzzles.json，make_override.py 核对）。一颗飞行物画在它的点上方 5 px，所以发射点往南挪
/// 5 px 减去炮口的高度。
pub const T_MUZZLE: (i64, i64) = (10_330, -600);
pub const X_MUZZLE: (i64, i64) = (13_670, 4_070);
/// 朝左的标记挂多久：隐形弹飞 `q_place / q_speed`（5）tick 才落地画炮台。
const FACE_T: usize = 30;
/// 算「受控制」的控制种类：游戏 `CastingTarget::check` 的掩码 0x347（击飞、眩晕、禁锢、强制位移、恐惧、魅惑）。
const CC_MASK: u32 = 0x347;

/// 主包黑默丁格的名字（buff、声音、画面都以它开头）。
fn hd(x: &str) -> String {
    format!("league_heimerdinger_{x}")
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_HEIMERDINGER_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_heimerdinger.log");
        }
    }
    PathBuf::from("league_heimerdinger.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    // the file stays open (league_lillia's log_open_once fix: opening it for every line stalled the simulation thread)
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

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 隐形弹飞多远、多快（炮台站在它停下的地方）。
    pub q_place: usize,
    pub q_speed: usize,
    /// Q 的炮台：活多久、出手间隔、第一发、射程、炮弹伤害和法强 %、光束伤害和法强 %。
    pub t_life: usize,
    pub t_per: usize,
    pub t_first: usize,
    pub t_r: usize,
    pub t_dmg: usize,
    pub t_ratio: usize,
    pub tb_dmg: usize,
    pub tb_ratio: usize,
    /// R 的巨型炮台：同上，加减速 % 和 tick。
    pub x_life: usize,
    pub x_per: usize,
    pub x_first: usize,
    pub x_r: usize,
    pub x_dmg: usize,
    pub x_ratio: usize,
    pub x_slow: usize,
    pub x_slow_t: usize,
    pub xb_dmg: usize,
    pub xb_ratio: usize,
    /// 被动：炮台 / 防御塔多近算「旁边」、多久看一次、移速 %、加多久。
    pub p_r: usize,
    pub p_tr: usize,
    pub p_per: usize,
    pub p_ms: usize,
    pub p_t: usize,
    /// 炮弹、光束、等离子弹飞多快（每 tick）。
    pub t_speed: usize,
    pub b_speed: usize,
    pub x_speed: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            q_place: 20000,
            q_speed: 4000,
            t_life: 600,
            t_per: 50,
            t_first: 40,
            t_r: 50000,
            t_dmg: 6,
            t_ratio: 4,
            tb_dmg: 18,
            tb_ratio: 14,
            x_life: 480,
            x_per: 30,
            x_first: 30,
            x_r: 60000,
            x_dmg: 18,
            x_ratio: 10,
            x_slow: 25,
            x_slow_t: 45,
            xb_dmg: 45,
            xb_ratio: 30,
            p_r: 40000,
            p_tr: 60000,
            p_per: 20,
            p_ms: 20,
            p_t: 30,
            t_speed: 2800,
            b_speed: 9000,
            x_speed: 3500,
        }
    }
}

/// `{"t_per":50,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "q_place" => &mut p.q_place,
            "q_speed" => &mut p.q_speed,
            "t_life" => &mut p.t_life,
            "t_per" => &mut p.t_per,
            "t_first" => &mut p.t_first,
            "t_r" => &mut p.t_r,
            "t_dmg" => &mut p.t_dmg,
            "t_ratio" => &mut p.t_ratio,
            "tb_dmg" => &mut p.tb_dmg,
            "tb_ratio" => &mut p.tb_ratio,
            "x_life" => &mut p.x_life,
            "x_per" => &mut p.x_per,
            "x_first" => &mut p.x_first,
            "x_r" => &mut p.x_r,
            "x_dmg" => &mut p.x_dmg,
            "x_ratio" => &mut p.x_ratio,
            "x_slow" => &mut p.x_slow,
            "x_slow_t" => &mut p.x_slow_t,
            "xb_dmg" => &mut p.xb_dmg,
            "xb_ratio" => &mut p.xb_ratio,
            "p_r" => &mut p.p_r,
            "p_tr" => &mut p.p_tr,
            "p_per" => &mut p.p_per,
            "p_ms" => &mut p.p_ms,
            "p_t" => &mut p.p_t,
            "t_speed" => &mut p.t_speed,
            "b_speed" => &mut p.b_speed,
            "x_speed" => &mut p.x_speed,
            _ => continue,
        };
        *slot = v;
    }
    p.q_speed = p.q_speed.max(1);
    p.t_per = p.t_per.max(1);
    p.x_per = p.x_per.max(1);
    p.p_per = p.p_per.max(1);
    p.t_speed = p.t_speed.max(1);
    p.b_speed = p.b_speed.max(1);
    p.x_speed = p.x_speed.max(1);
    p.x_slow = p.x_slow.min(95);
    p
}

// ===================== 计算 =====================

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Kind {
    /// Q 的 H-28G 进化炮台。
    Turret,
    /// R 的 H-28Q 巨型炮台。
    Apex,
}

/// 一发的样子：光束（打受控英雄）还是炮弹。
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Fire {
    Cannon,
    Beam,
}

/// 一发的魔法伤害（减免前）：`dmg` + `ratio`% 法强。
pub fn shot_damage(dmg: usize, ratio: usize, ap: usize) -> usize {
    dmg + ratio * ap / 100
}

/// 炮台站在哪：`from` 朝 `dir`（不必是单位长度）`reach` 远；没有方向就在 `from`。
pub fn stand_spot(from: (f64, f64), dir: Option<(f64, f64)>, reach: f64) -> (f64, f64) {
    match dir.and_then(unit) {
        Some((ux, uy)) => (from.0 + ux * reach, from.1 + uy * reach),
        None => from,
    }
}

fn unit(v: (f64, f64)) -> Option<(f64, f64)> {
    let d = (v.0 * v.0 + v.1 * v.1).sqrt();
    (d >= 1e-6).then(|| (v.0 / d, v.1 / d))
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 控制种类的列表里有没有算「受控制」的。
pub fn hard_cc(kinds: impl IntoIterator<Item = u32>) -> bool {
    kinds.into_iter().any(|k| k < 32 && CC_MASK & (1 << k) != 0)
}

fn at(p: (f64, f64)) -> InputTargetV1 {
    InputTargetV1::pos(p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

pub struct Unit {
    pub id: usize,
    pub pos: (f64, f64),
    pub champion: bool,
    pub in_cc: bool,
}

/// 能打的敌方单位（英雄、小兵、野怪；塔、水晶不算：主包区域的 `EnemyWithoutTower`）。
fn enemies(sim: &StableSim<'_>, team: usize) -> Vec<Unit> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.team() == team || !e.is_alive() || !e.is_targetable() {
            continue;
        }
        let ok = matches!(
            e.kind(),
            Some(EntityKindV1::Champion | EntityKindV1::Minion | EntityKindV1::Jungle | EntityKindV1::Epic | EntityKindV1::Serpen)
        );
        if ok {
            let champion = e.kind() == Some(EntityKindV1::Champion);
            let in_cc = champion && hard_cc((0..e.cc_count()).filter_map(|j| e.cc_at(j)).map(|c| c.kind));
            out.push(Unit { id: e.id(), pos: fpos(e.pos()), champion, in_cc });
        }
    }
    out
}

/// 炮台打谁：范围内最近的受控英雄（光束），没有就最近的英雄，再没有就最近的其他单位（炮弹）。
pub fn choose(units: &[Unit], from: (f64, f64), reach: f64) -> Option<(&Unit, Fire)> {
    let near = |u: &&Unit| dist(u.pos, from) <= reach;
    let by = |a: &&Unit, b: &&Unit| dist(a.pos, from).total_cmp(&dist(b.pos, from));
    if let Some(u) = units.iter().filter(|u| u.in_cc).filter(near).min_by(by) {
        return Some((u, Fire::Beam));
    }
    units
        .iter()
        .filter(|u| u.champion)
        .filter(near)
        .min_by(by)
        .or_else(|| units.iter().filter(near).min_by(by))
        .map(|u| (u, Fire::Cannon))
}

// ===================== 原生效果 -> 被动 =====================

/// 一次放炮台：施法那一 tick 他站的地方、方向（`None`：施法输入里没有）。
#[derive(Clone, Debug)]
struct Put {
    kind: Kind,
    from: (f64, f64),
    dir: Option<(f64, f64)>,
    tick: usize,
    input_kind: u32,
}

/// 炮台朝左吗：方向往左（x 为负）才朝左，没有方向朝右（数据默认画朝右的）。
pub fn faces_left(dir: Option<(f64, f64)>) -> bool {
    dir.is_some_and(|d| d.0 < 0.0)
}

/// 一发从哪出来：朝右的炮口 `muzzle`（往前、往上，游戏像素 x 1000）按朝向翻过来，往南挪 5 px 减炮口高度（飞行物画在点上方 5 px）。
pub fn shot_from(pos: (f64, f64), muzzle: (i64, i64), left: bool) -> (f64, f64) {
    let dx = if left { -muzzle.0 } else { muzzle.0 } as f64;
    (pos.0 + dx, pos.1 + (5_000 - muzzle.1) as f64)
}

/// 原生效果放下、被动还没接走的炮台：按（这局的种子、模拟的来源、比赛、局、他的编号）分开。
type Key = (u64, u32, u64, u64, usize);
static PUTS: LazyLock<Mutex<HashMap<Key, Vec<Put>>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn key(sim: &StableSim<'_>, me: usize) -> Key {
    let o = sim.sim_origin().unwrap_or_default();
    (sim.seed(), o.kind, o.match_id, o.set_index, me)
}

/// `league_heimerdinger:q` / `:x`：副本里炮台的槽位空着、隐形弹出手的那一 tick。
struct Stand(Kind);

impl StableEffectType for Stand {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(e) = sim.get_entity(caster) else { return };
        let from = fpos(e.pos());
        let dir = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Dir) => Some((input.dir_x as f64, input.dir_y as f64)),
            Some(InputTargetKindV1::Pos) => Some((input.x as f64 - from.0, input.y as f64 - from.1)),
            Some(InputTargetKindV1::Target) => {
                sim.get_entity(input.target_id).map(|t| fpos(t.pos())).map(|t| (t.0 - from.0, t.1 - from.1))
            }
            _ => None,
        };
        // the data's bolt draws the turret when it lands: from the side facing the target (t_face_l: to his left)
        let face = hd(match self.0 {
            Kind::Turret => "t_face_l",
            Kind::Apex => "x_face_l",
        });
        sim.entity_remove_buff(caster, &face);
        if faces_left(dir) {
            sim.add_buff(caster, &BuffV1::timed(&face, FACE_T));
        }
        let put = Put { kind: self.0, from, dir, tick: sim.tick(), input_kind: input.kind };
        PUTS.lock().unwrap_or_else(|e| e.into_inner()).entry(key(sim, caster)).or_default().push(put);
    }
}

// ===================== 被动 =====================

#[derive(Clone, Debug)]
struct Turret {
    kind: Kind,
    pos: (f64, f64),
    left: bool,
    stand: usize,
    until: usize,
    next: usize,
}

/// 炮弹在飞：到了 `due` 再扣血。
#[derive(Clone, Debug)]
struct Flight {
    kind: Kind,
    fire: Fire,
    target: usize,
    due: usize,
    dmg: usize,
}

/// 每个黑默丁格一份。
#[derive(Clone, Default)]
struct Workshop {
    p: Params,
    turrets: Vec<Turret>,
    flights: Vec<Flight>,
    next_haste: usize,
    n_put: usize,
    n_shot: usize,
    n_beam: usize,
    n_haste_turret: usize,
    n_haste_tower: usize,
    next_report: usize,
}

impl Workshop {
    /// 原生效果交过来的炮台：站在隐形弹停下的地方。
    fn take_puts(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let puts = PUTS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me)).unwrap_or_default();
        for put in puts {
            let pos = stand_spot(put.from, put.dir, self.p.q_place as f64);
            let stand = put.tick + self.p.q_place.div_ceil(self.p.q_speed);
            let (life, first) = match put.kind {
                Kind::Turret => (self.p.t_life, self.p.t_first),
                Kind::Apex => (self.p.x_life, self.p.x_first),
            };
            let left = faces_left(put.dir);
            self.turrets.push(Turret { kind: put.kind, pos, left, stand, until: stand + life, next: stand + first });
            self.n_put += 1;
            if self.n_put <= 12 || self.n_put % 25 == 0 {
                wlog(format!("{} PUT #{}: {:?} at ({:.0}, {:.0}) from ({:.0}, {:.0}) facing {}, input kind {}{}, {} standing",
                             head(sim, me), self.n_put, put.kind, pos.0, pos.1, put.from.0, put.from.1,
                             if left { "left" } else { "right" }, put.input_kind,
                             if put.dir.is_some() { "" } else { " (no direction: at his feet)" }, self.turrets.len()));
            }
        }
    }

    fn fire(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, ap: usize) {
        let tick = sim.tick();
        self.turrets.retain(|t| t.until > tick);
        if self.turrets.iter().all(|t| t.next > tick) {
            return;
        }
        let units = enemies(sim, team);
        let mut flights = Vec::new();
        for t in &mut self.turrets {
            if t.next > tick {
                continue;
            }
            let p = &self.p;
            let (per, reach, muzzle) = match t.kind {
                Kind::Turret => (p.t_per, p.t_r, T_MUZZLE),
                Kind::Apex => (p.x_per, p.x_r, X_MUZZLE),
            };
            let from = shot_from(t.pos, muzzle, t.left);
            t.next = tick + per;
            let Some((u, fire)) = choose(&units, t.pos, reach as f64) else { continue };
            let (pic, speed, dmg) = match (t.kind, fire) {
                (Kind::Turret, Fire::Cannon) => ("t_shot", p.t_speed, shot_damage(p.t_dmg, p.t_ratio, ap)),
                (Kind::Turret, Fire::Beam) => ("t_beam_line", p.b_speed, shot_damage(p.tb_dmg, p.tb_ratio, ap)),
                (Kind::Apex, Fire::Cannon) => ("x_shot", p.x_speed, shot_damage(p.x_dmg, p.x_ratio, ap)),
                (Kind::Apex, Fire::Beam) => ("t_beam_line", p.b_speed, shot_damage(p.xb_dmg, p.xb_ratio, ap)),
            };
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team,
                x: from.0.round().max(0.0) as u64,
                y: from.1.round().max(0.0) as u64,
                radius: 1_000,
                speed: speed as u64,
                move_kind: ProjectileMoveKindV1::Target.code(),
                target_id: u.id,
                target_x: 0,
                target_y: 0,
                penetrate: false,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::None.code(),
            };
            sim.spawn_projectile(&hd(pic), &format!("{ID}:noop"), &spec);
            let fly = (dist(from, u.pos) / speed as f64).ceil() as usize;
            flights.push(Flight { kind: t.kind, fire, target: u.id, due: tick + fly.max(1), dmg });
            if fire == Fire::Beam {
                self.n_beam += 1;
            }
            self.n_shot += 1;
            if self.n_shot <= 12 || self.n_shot % 100 == 0 {
                wlog(format!("{} SHOT #{}: {:?} -> #{} ({}) {:?} for {dmg}", head(sim, me), self.n_shot, t.kind, u.id,
                             if u.in_cc { "champion in cc" } else if u.champion { "champion" } else { "unit" }, fire));
            }
        }
        self.flights.extend(flights);
    }

    /// 飞到的炮弹扣血（巨型炮台的等离子弹还减速）。
    fn land(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        let (due, wait): (Vec<Flight>, Vec<Flight>) = std::mem::take(&mut self.flights).into_iter().partition(|f| f.due <= tick);
        self.flights = wait;
        for f in due {
            if !sim.get_entity(f.target).is_some_and(|e| e.is_alive()) {
                continue;
            }
            sim.deal_damage_typed(me, f.target, f.dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            let (pic, snd) = match (f.kind, f.fire) {
                (Kind::Turret, Fire::Cannon) => ("t_hit", "t_hit"),
                (Kind::Turret, Fire::Beam) => ("t_beam", "t_beam"),
                (Kind::Apex, Fire::Cannon) => ("x_hit", "x_hit"),
                (Kind::Apex, Fire::Beam) => ("x_beam", "t_beam"),
            };
            if f.kind == Kind::Apex && f.fire == Fire::Cannon {
                let mut slow = BuffV1::timed(&hd("x_slow"), self.p.x_slow_t);
                slow.move_speed_mult = -(self.p.x_slow as i32);
                sim.entity_remove_buff(f.target, &hd("x_slow"));
                sim.add_buff(f.target, &slow);
            }
            let hit = InputTargetV1::target(f.target);
            sim.play_view_effect(&hd(pic), me, &hit, 0, 0, 0);
            sim.play_sfx(&hd(snd), me, &hit);
        }
    }

    /// 海克斯科技亲和：炮台旁或己方防御塔旁加速。
    fn haste(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, pos: (f64, f64)) {
        let tick = sim.tick();
        if tick < self.next_haste {
            return;
        }
        self.next_haste = tick + self.p.p_per;
        let by_turret = self.turrets.iter().any(|t| t.stand <= tick && dist(t.pos, pos) <= self.p.p_r as f64);
        let by_tower = !by_turret
            && (0..sim.tower_count()).filter_map(|i| sim.get_entity(sim.tower_id_at(i))).any(|t| {
                t.team() == team && t.is_alive() && dist(fpos(t.pos()), pos) <= self.p.p_tr as f64
            });
        if !(by_turret || by_tower) {
            return;
        }
        let name = hd("haste");
        let mut b = BuffV1::timed(&name, self.p.p_t);
        b.move_speed_mult = self.p.p_ms as i32;
        sim.entity_remove_buff(me, &name);
        sim.add_buff(me, &b);
        let n = if by_turret {
            self.n_haste_turret += 1;
            self.n_haste_turret
        } else {
            self.n_haste_tower += 1;
            self.n_haste_tower
        };
        if n <= 4 {
            wlog(format!("{} HASTE: +{}% by {} (#{n})", head(sim, me), self.p.p_ms, if by_turret { "a turret" } else { "a tower" }));
        }
    }
}

impl StablePassive for Workshop {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        // a stale put of an earlier match with the same seed and id
        PUTS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key(sim, me));
        wlog(format!("{} SPAWN: the add-on's Heimerdinger (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, ap, pos, alive) = (e.team(), e.stat().magic_power, fpos(e.pos()), e.is_alive());
        let tick = sim.tick();
        // his turrets stand and fire after his death (League's; the main pack's zones too)
        self.take_puts(sim, me);
        self.land(sim, me);
        self.fire(sim, me, team, ap);
        if alive {
            self.haste(sim, me, team, pos);
        }
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 {
                wlog(format!("{} WATCH: turrets put {} ({} standing), shots {} ({} beams), haste by turrets {} / towers {}",
                             head(sim, me), self.n_put, self.turrets.len(), self.n_shot, self.n_beam, self.n_haste_turret,
                             self.n_haste_tower));
            }
        }
    }
}

struct NoopFx;
impl StableEffectType for NoopFx {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Heimerdinger's turrets firing visible shots, Hextech Affinity by towers too) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:noop"), NoopFx);
    module.add_native_effect(format!("{ID}:q"), Stand(Kind::Turret));
    module.add_native_effect(format!("{ID}:x"), Stand(Kind::Apex));
    module.add_native_passive(format!("{ID}:affinity"), Workshop::default());
    host.log(LogLevel::Info, "league_heimerdinger v1 loaded (turrets firing visible shots, Hextech Affinity by towers too).");
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
        let p = parse_params(r#"{"t_per":40,"p_tr":70000,"x":1}"#);
        assert_eq!((p.t_per, p.p_tr), (40, 70000));
        assert_eq!(p.x_per, Params::default().x_per);
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"t_per":0,"q_speed":0}"#).t_per, 1);
        assert_eq!(parse_params(r#"{"x_slow":200}"#).x_slow, 95);
    }

    #[test]
    fn shots_scale_with_ability_power() {
        assert_eq!(shot_damage(6, 4, 0), 6);
        assert_eq!(shot_damage(6, 4, 100), 10);
        assert_eq!(shot_damage(45, 30, 150), 90);
    }

    #[test]
    fn turrets_stand_where_the_bolt_stops() {
        let s = stand_spot((100_000.0, 50_000.0), Some((3.0, 4.0)), 20_000.0);
        assert!((s.0 - 112_000.0).abs() < 1e-6 && (s.1 - 66_000.0).abs() < 1e-6);
        assert_eq!(stand_spot((1.0, 2.0), None, 20_000.0), (1.0, 2.0));
        assert_eq!(stand_spot((1.0, 2.0), Some((0.0, 0.0)), 20_000.0), (1.0, 2.0));
    }

    #[test]
    fn side_turrets_face_their_target_and_fire_from_the_muzzle() {
        assert!(faces_left(Some((-3.0, 1.0))));
        assert!(!faces_left(Some((3.0, -1.0))));
        assert!(!faces_left(None));
        assert_eq!(shot_from((100_000.0, 50_000.0), (10_000, 2_000), false), (110_000.0, 53_000.0));
        assert_eq!(shot_from((100_000.0, 50_000.0), (10_000, 2_000), true), (90_000.0, 53_000.0));
        assert!(hd("t_face_l").len() <= BUFF_NAME_CAP && hd("x_face_l").len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn crowd_control_as_the_game_counts_it() {
        for k in [0, 1, 2, 6, 8, 9] {
            assert!(hard_cc([k]), "{k}");
        }
        for k in [3, 4, 5, 7, 10] {
            assert!(!hard_cc([k]), "{k}");
        }
        assert!(!hard_cc([]));
        assert!(hard_cc([4, 1]));
    }

    #[test]
    fn beams_first_then_champions_then_the_rest() {
        let u = |id, x: f64, champion, in_cc| Unit { id, pos: (x, 0.0), champion, in_cc };
        let units = [u(1, 1_000.0, false, false), u(2, 20_000.0, true, false), u(3, 45_000.0, true, true)];
        assert_eq!(choose(&units, (0.0, 0.0), 50_000.0).map(|(u, f)| (u.id, f)), Some((3, Fire::Beam)));
        assert_eq!(choose(&units, (0.0, 0.0), 30_000.0).map(|(u, f)| (u.id, f)), Some((2, Fire::Cannon)));
        assert_eq!(choose(&units, (0.0, 0.0), 10_000.0).map(|(u, f)| (u.id, f)), Some((1, Fire::Cannon)));
        assert!(choose(&units, (200_000.0, 0.0), 10_000.0).is_none());
    }

    #[test]
    fn buff_names_fit() {
        for x in ["haste", "x_slow", "t_shot", "t_beam_line", "x_shot", "t_hit", "x_beam"] {
            assert!(hd(x).len() <= BUFF_NAME_CAP);
        }
    }
}
