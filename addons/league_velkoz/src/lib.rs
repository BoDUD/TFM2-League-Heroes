//! 维克兹附加包：照英雄联盟做主包数据做不到的被动层数、Q 的分裂和连招（用户 2026-10-20：技能方案 A、中单、做附加包、
//! 「有连招要做连招」）。
//!
//! 主包保持纯数据：数据只读得到施法者自己身上的 buff，所以主包把「有机体解构」的层数记在维克兹身上（施法者标记 p_1 -> p_2，
//! 布兰德的做法）——技能连中不同的英雄也会叠到第 3 层；数据也不能让投射物拐弯，所以 Q 的分裂是命中点周围的一圈爆炸。
//! `mod.override_info` 把主包的维克兹换成 `override/` 里的副本（`tools/kit/build_velkoz.py --native`），只有这几处不同：
//!
//! - **有机体解构（`league_velkoz:deconstruct`）**：层数是那个英雄身上的 buff `league_velkoz_pd_<维克兹的编号>`（每层
//!   `p_keep` tick，再中一下全部刷新），每个敌方英雄分开计；第 3 层清掉层数，造成 `p_dmg` + `p_ratio`% 法强的**真实伤害**；
//!   头上照旧亮 1、2 层和爆发的画面。每叠一层都给那个英雄挂 `p_keep` tick 的「被研究」`league_velkoz_rs_<编号>`，
//!   并刷新维克兹身上的 `league_velkoz_p_res`（主包数据的 R 读它决定能不能放）。
//! - **等离子裂变的分裂（`league_velkoz:fission`）**：Q 打中东西停下的那一点，朝飞行方向的左右两边各射出一颗分裂弹
//!   （`q_split_bolt`，从命中点旁 `q_soff` 起飞 `q_slen` 远，速度 `q_speed`）；分裂弹打中的第一个敌人
//!   （`league_velkoz:split_hit`）受到 `q_sdmg` + `q_sratio`% 法强的魔法伤害和减速，英雄还会叠层、打开 Q -> W 的窗口
//!   `q_combo`。英雄联盟：分裂弹和主弹打不中同一个人——分裂弹从命中点旁边起飞。
//! - **生命形态瓦解射线（`league_velkoz:ray`）**：每一波伤害线由本包算：被**这个**维克兹研究过的英雄受到真实伤害
//!   （主包：只要他身上有 p_res，射线对谁都是真实伤害），其他敌人魔法伤害；每 `r_mark` 波叠一层。
//! - **连招（`combo.rs`，AI 钩子 `league_velkoz:combo`）**：E -> Q、Q / E 之后普攻打英雄（裂隙打在他身上）、R 先射被研究的英雄。
//!
//! 游戏 0.6.4 的 `deal_damage_typed` 只把伤害排进效果队列，下一次 on_update 之前才扣血（莉莉娅 0.1.2 的教训）。
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_velkoz.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `SPAWN`、`STACK` / `BURST`（被动）、`SPLIT` / `SPLIT HIT`（Q 分裂）、`RAY`（射线一波）、`WATCH`（每 30 秒的计数）和连招，
//! 都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::Ordering;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod combo;

const ID: &str = "league_velkoz";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";
/// 诊断：每这么多 tick 报一次（30 秒）。
const WATCH_EVERY: usize = 1800;

/// 主包维克兹的名字（buff、声音、画面都以它开头）。
fn vk(x: &str) -> String {
    format!("{ID}_{x}")
}

/// 维克兹 `me` 记在敌方英雄身上的层数。
fn stacks_name(me: usize) -> String {
    vk(&format!("pd_{me}"))
}

/// 维克兹 `me` 研究过的英雄身上的标记。
fn research_name(me: usize) -> String {
    vk(&format!("rs_{me}"))
}

// ===================== 日志 =====================

static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VELKOZ_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_velkoz.log");
        }
    }
    PathBuf::from("league_velkoz.log")
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

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 30;
const LOG_EVERY: usize = 50;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn total(kind: &'static str) -> usize {
    COUNTS.lock().unwrap_or_else(|e| e.into_inner()).get(kind).copied().unwrap_or(0)
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

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 被动：层数和研究留多久、第 3 层的真实伤害和法强 %。
    pub p_keep: usize,
    pub p_dmg: usize,
    pub p_ratio: usize,
    /// Q：分裂弹的伤害和法强 %、减速 % 和 tick、Q -> W 的窗口、弹速、半径、Q 的施放距离、分裂弹飞多远和从命中点旁多远起飞。
    pub q_sdmg: usize,
    pub q_sratio: usize,
    pub q_slow: usize,
    pub q_slow_t: usize,
    pub q_cw: usize,
    pub q_speed: usize,
    pub q_rad: usize,
    pub q_range: usize,
    pub q_slen: usize,
    pub q_soff: usize,
    /// E：施放距离、半径；普攻距离（连招）。
    pub e_range: usize,
    pub e_r: usize,
    pub atk_range: usize,
    /// R：施放距离、射线长和宽、总伤害和法强 %、引导多久、一波隔多久、每几波叠一层。
    pub r_range: usize,
    pub r_len: usize,
    pub r_w: usize,
    pub r_dmg: usize,
    pub r_ratio: usize,
    pub r_t: usize,
    pub r_p: usize,
    pub r_mark: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { p_keep: 420, p_dmg: 40, p_ratio: 40, q_sdmg: 40, q_sratio: 30, q_slow: 50, q_slow_t: 75, q_cw: 90,
                 q_speed: 2200, q_rad: 5000, q_range: 85000, q_slen: 55000, q_soff: 12000, e_range: 75000, e_r: 22000,
                 atk_range: 55000, r_range: 95000, r_len: 120000, r_w: 10000, r_dmg: 300, r_ratio: 100, r_t: 150, r_p: 15,
                 r_mark: 3 }
    }
}

/// `{"p_keep":420,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "p_keep" => &mut p.p_keep,
            "p_dmg" => &mut p.p_dmg,
            "p_ratio" => &mut p.p_ratio,
            "q_sdmg" => &mut p.q_sdmg,
            "q_sratio" => &mut p.q_sratio,
            "q_slow" => &mut p.q_slow,
            "q_slow_t" => &mut p.q_slow_t,
            "q_cw" => &mut p.q_cw,
            "q_speed" => &mut p.q_speed,
            "q_rad" => &mut p.q_rad,
            "q_range" => &mut p.q_range,
            "q_slen" => &mut p.q_slen,
            "q_soff" => &mut p.q_soff,
            "e_range" => &mut p.e_range,
            "e_r" => &mut p.e_r,
            "atk_range" => &mut p.atk_range,
            "r_range" => &mut p.r_range,
            "r_len" => &mut p.r_len,
            "r_w" => &mut p.r_w,
            "r_dmg" => &mut p.r_dmg,
            "r_ratio" => &mut p.r_ratio,
            "r_t" => &mut p.r_t,
            "r_p" => &mut p.r_p,
            "r_mark" => &mut p.r_mark,
            _ => continue,
        };
        *slot = v;
    }
    p.q_speed = p.q_speed.max(1);
    p.q_slow = p.q_slow.min(95);
    p.r_p = p.r_p.max(1);
    p.r_mark = p.r_mark.max(1);
    p
}

/// 每个维克兹的参数（被动 configure 时存下，原生效果和连招里读）：键是 (这局的种子, 他的编号)。
static PARAMS: LazyLock<Mutex<HashMap<(u64, usize), Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim.seed(), me)).copied().unwrap_or_default()
}

// ===================== 计算 =====================

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 第几层之后怎么办：叠到 1、2 层（亮对应的画面），或第 3 层爆发。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stack {
    Pips(usize),
    Burst,
}

pub fn outcome(count: usize) -> Stack {
    if count >= 3 {
        Stack::Burst
    } else {
        Stack::Pips(count.max(1))
    }
}

/// 第 3 层的真实伤害。
pub fn burst_damage(p: &Params, ap: usize) -> usize {
    p.p_dmg + p.p_ratio * ap / 100
}

/// 分裂弹：从命中点 `hit` 起飞的两颗（起点、终点），垂直于从 `me` 到 `hit` 的飞行方向。
pub fn split_paths(me: Pt, hit: Pt, p: &Params) -> [(Pt, Pt); 2] {
    let d = dist(me, hit);
    let (ux, uy) = if d < 1.0 { (1.0, 0.0) } else { ((hit.0 - me.0) / d, (hit.1 - me.1) / d) };
    let (px, py) = (-uy, ux);
    let (off, far) = (p.q_soff as f64, (p.q_soff + p.q_slen) as f64);
    let path = |s: f64| ((hit.0 + px * s * off, hit.1 + py * s * off), (hit.0 + px * s * far, hit.1 + py * s * far));
    [path(1.0), path(-1.0)]
}

/// 一波射线的伤害（总伤害平分到每一波）。
pub fn wave_damage(p: &Params, ap: usize) -> usize {
    let waves = (p.r_t / p.r_p).max(1);
    ((p.r_dmg * 100 + p.r_ratio * ap) as f64 / 100.0 / waves as f64).round() as usize
}

/// 点 `u` 在从 `a` 朝 `b` 方向、长 `len` 的射线上吗（离线不超过 `half` + 他的半径 `r`）。
pub fn on_ray(a: Pt, b: Pt, len: f64, half: f64, u: Pt, r: f64) -> bool {
    let d = dist(a, b);
    if d < 1.0 {
        return false;
    }
    let (ux, uy) = ((b.0 - a.0) / d, (b.1 - a.1) / d);
    let (vx, vy) = (u.0 - a.0, u.1 - a.1);
    let along = vx * ux + vy * uy;
    let off = (vx * uy - vy * ux).abs();
    along >= -r && along <= len + r && off <= half + r
}

fn fpos(p: (u64, u64)) -> Pt {
    (p.0 as f64, p.1 as f64)
}

fn upos(p: Pt) -> (u64, u64) {
    (p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn flag(sim: &mut StableSim<'_>, id: usize, name: &str, ticks: usize) {
    sim.entity_remove_buff(id, name);
    sim.add_buff(id, &BuffV1::timed(name, ticks));
}

fn magic_power(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| e.stat().magic_power)
}

// ===================== 原生效果 =====================

/// 技能打中一个敌方英雄：在他身上叠一层（第 3 层真实伤害），研究他。
fn deconstruct(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    if !sim.get_entity(target).is_some_and(|e| e.is_alive() && e.is_champion()) {
        return;
    }
    let p = params_of(sim, me);
    flag(sim, target, &research_name(me), p.p_keep);
    flag(sim, me, &vk("p_res"), p.p_keep);
    let c = sim.entity_stack_buff(target, &BuffV1::timed(&stacks_name(me), p.p_keep), 3, true);
    if c == 0 {
        if let Some(k) = counted("refused") {
            wlog(format!("{} STACK refused by entity_stack_buff on #{target} #{k}", head(sim, me)));
        }
        return;
    }
    let on = InputTargetV1::target(target);
    match outcome(c) {
        Stack::Pips(k) => {
            sim.play_view_effect(&vk(&format!("p_s{k}")), me, &on, 0, 0, 0);
            sim.play_sfx(&vk(&format!("p_{k}")), me, &on);
            if let Some(n) = counted("stack") {
                wlog(format!("{} STACK #{n}: {} now at {k}", head(sim, me), who(sim, target)));
            }
        }
        Stack::Burst => {
            sim.entity_remove_buff(target, &stacks_name(me));
            let d = burst_damage(&p, magic_power(sim, me));
            sim.deal_damage_typed(me, target, d, DamageTypeV1::Fixed, AttackTypeV1::Skill);
            sim.play_view_effect(&vk("p_full"), me, &on, 0, 0, 0);
            sim.play_sfx(&vk("p_full"), me, &on);
            if let Some(n) = counted("burst") {
                wlog(format!("{} BURST #{n}: {} takes {d} true damage", head(sim, me), who(sim, target)));
            }
        }
    }
}

/// Q 停在打中的地方：左右两颗分裂弹。
fn fission(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let hit = match InputTargetKindV1::from_code(input.kind) {
        Some(InputTargetKindV1::Pos) => (input.x as f64, input.y as f64),
        Some(InputTargetKindV1::Target) => match sim.get_entity(input.target_id) {
            Some(e) => fpos(e.pos()),
            None => return,
        },
        _ => return,
    };
    let Some(e) = sim.get_entity(me) else { return };
    let (at, team) = (fpos(e.pos()), e.team());
    let p = params_of(sim, me);
    let spot = upos(hit);
    sim.play_sfx(&vk("q_split"), me, &InputTargetV1::pos(spot.0, spot.1));
    let mut sent = 0;
    for (from, to) in split_paths(at, hit, &p) {
        let (fx, fy) = upos(from);
        let (tx, ty) = upos(to);
        let spec = ProjectileSpawnV1 {
            caster_id: me,
            team,
            x: fx,
            y: fy,
            radius: p.q_rad as u64,
            speed: p.q_speed as u64,
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: tx,
            target_y: ty,
            penetrate: false,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        if sim.spawn_projectile(&vk("q_split_bolt"), &format!("{ID}:split_hit"), &spec) {
            sent += 1;
        }
    }
    if let Some(n) = counted("split") {
        wlog(format!("{} SPLIT #{n}: {sent} bolts from ({:.0}, {:.0})", head(sim, me), hit.0, hit.1));
    }
}

/// 分裂弹打中的第一个敌人。
fn split_hit(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    let Some(champion) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.is_champion()) else { return };
    let p = params_of(sim, me);
    let d = p.q_sdmg + p.q_sratio * magic_power(sim, me) / 100;
    sim.deal_damage_typed(me, target, d, DamageTypeV1::Ap, AttackTypeV1::Skill);
    let mut slow = BuffV1::timed(&vk("q_slow"), p.q_slow_t);
    slow.move_speed_mult = -(p.q_slow as i32);
    sim.entity_remove_buff(target, &vk("q_slow"));
    sim.add_buff(target, &slow);
    let on = InputTargetV1::target(target);
    sim.play_view_effect(&vk("q_split_hit"), me, &on, 0, 0, 0);
    sim.play_sfx(&vk("q_split_hit"), me, &on);
    if champion {
        flag(sim, me, &vk("q_combo"), p.q_cw);
        deconstruct(sim, me, on);
    }
    if let Some(n) = counted("split hit") {
        wlog(format!("{} SPLIT HIT #{n}: {} for {d}{}", head(sim, me), who(sim, target),
                     if champion { " (champion: a stack, the Q -> W window)" } else { "" }));
    }
}

/// 每个维克兹这次射线到第几波了：(上一波的 tick, 第几波)。
static WAVES: LazyLock<Mutex<HashMap<(u64, usize), (usize, usize)>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// 射线的一波：从他到目标那条线上的敌人；被他研究过的英雄受到真实伤害。
fn ray(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let Some(t) = sim.get_entity(input.target_id).filter(|e| e.is_alive()).map(|e| fpos(e.pos())) else { return };
    let Some(e) = sim.get_entity(me) else { return };
    let (at, team) = (fpos(e.pos()), e.team());
    let p = params_of(sim, me);
    let tick = sim.tick();
    let k = {
        let mut w = WAVES.lock().unwrap_or_else(|e| e.into_inner());
        let slot = w.entry((sim.seed(), me)).or_insert((0, 0));
        let k = if tick > slot.0 + p.r_p * 2 || slot.1 == 0 && slot.0 == 0 { 0 } else { slot.1 + 1 };
        *slot = (tick, k);
        k
    };
    let d = wave_damage(&p, magic_power(sim, me));
    let half = p.r_w as f64 / 2.0;
    let hit: Vec<(usize, bool)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && !u.is_tower() && u.is_targetable())
        .filter(|u| on_ray(at, t, p.r_len as f64, half, fpos(u.pos()), u.radius() as f64))
        .map(|u| (u.id(), u.is_champion()))
        .collect();
    let research = research_name(me);
    let mut trues = 0;
    for &(id, champ) in &hit {
        let on = InputTargetV1::target(id);
        let studied = champ && has_buff(sim, id, &research);
        let kind = if studied { DamageTypeV1::Fixed } else { DamageTypeV1::Ap };
        sim.deal_damage_typed(me, id, d, kind, AttackTypeV1::Skill);
        sim.play_view_effect(&vk("r_hit"), me, &on, 0, 0, 0);
        if champ {
            sim.play_sfx(&vk(if studied { "r_true" } else { "r_hit" }), me, &on);
            if k % p.r_mark == 0 {
                deconstruct(sim, me, on);
            }
        }
        trues += studied as usize;
    }
    if let Some(n) = counted("ray") {
        wlog(format!("{} RAY #{n}: wave {k}, {} hit ({} champions, {trues} researched: true damage) for {d} each",
                     head(sim, me), hit.len(), hit.iter().filter(|h| h.1).count()));
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));

impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 被动 =====================

/// 记下参数，证明这局的维克兹是附加包的副本，并定时报告。
#[derive(Clone, Default)]
struct Research {
    p: Params,
}

impl StablePassive for Research {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert((sim.seed(), me), self.p);
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Vel'Koz (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let t = sim.tick();
        if t == 0 || t % WATCH_EVERY != 0 {
            return;
        }
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, level, ap) = (e.is_alive(), e.level(), e.stat().magic_power);
        wlog(format!(
            "{} WATCH: alive {alive}, level {level}, ap {ap}; stacks {}, bursts {}, splits {} (hits {}), ray waves {}, combos {}",
            head(sim, me),
            total("stack"),
            total("burst"),
            total("split"),
            total("split hit"),
            total("ray"),
            combo::TOTAL.load(Ordering::Relaxed)
        ));
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Vel'Koz: Organic Deconstruction per champion, Plasma Fission's split, the ray's research, the combos) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:deconstruct"), Step(deconstruct));
    module.add_native_effect(format!("{ID}:fission"), Step(fission));
    module.add_native_effect(format!("{ID}:split_hit"), Step(split_hit));
    module.add_native_effect(format!("{ID}:ray"), Step(ray));
    module.add_native_passive(format!("{ID}:research"), Research::default());
    module.add_player_input_ai(combo::Combo);
    host.log(LogLevel::Info, "league_velkoz loaded (Organic Deconstruction per champion, Plasma Fission's split, the combos).");
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
        let p = parse_params(r#"{"p_keep":300,"r_mark":0,"q_slow":200,"x":1}"#);
        assert_eq!(p.p_keep, 300);
        assert_eq!(p.r_mark, 1);
        assert_eq!(p.q_slow, 95);
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn the_third_stack_bursts() {
        assert_eq!(outcome(1), Stack::Pips(1));
        assert_eq!(outcome(2), Stack::Pips(2));
        assert_eq!(outcome(3), Stack::Burst);
        let p = Params::default();
        assert_eq!(burst_damage(&p, 100), 80); // 40 + 40 % of 100 AP
    }

    #[test]
    fn the_split_flies_at_right_angles() {
        let p = Params::default();
        let [(a0, a1), (b0, b1)] = split_paths((0.0, 0.0), (50_000.0, 0.0), &p);
        // flying right: the bolts leave up and down from beside the hit, never through it
        assert!((a0.0 - 50_000.0).abs() < 1.0 && (a0.1.abs() - 12_000.0).abs() < 1.0);
        assert!((a1.1.abs() - 67_000.0).abs() < 1.0);
        assert!(a0.1 * b0.1 < 0.0 && (b1.0 - 50_000.0).abs() < 1.0);
        // a hit on his own spot: still two bolts
        let [(c0, _), (d0, _)] = split_paths((10.0, 10.0), (10.0, 10.0), &p);
        assert!(dist(c0, d0) > 20_000.0);
    }

    #[test]
    fn the_ray_reaches_along_its_line() {
        let a = (0.0, 0.0);
        let b = (30_000.0, 0.0);
        assert!(on_ray(a, b, 120_000.0, 5_000.0, (100_000.0, 3_000.0), 3_000.0));
        assert!(!on_ray(a, b, 120_000.0, 5_000.0, (100_000.0, 20_000.0), 3_000.0));
        assert!(!on_ray(a, b, 120_000.0, 5_000.0, (130_000.0, 0.0), 3_000.0));
        assert!(!on_ray(a, b, 120_000.0, 5_000.0, (-20_000.0, 0.0), 3_000.0));
    }

    #[test]
    fn the_ray_splits_its_damage_into_waves() {
        let p = Params::default();
        assert_eq!(wave_damage(&p, 0), 30); // 300 over 10 waves
        assert_eq!(wave_damage(&p, 100), 40); // + 100 % of 100 AP
    }

    #[test]
    fn buff_names_fit() {
        for x in [stacks_name(usize::MAX), research_name(usize::MAX), vk("q_split_bolt"), vk("p_res")] {
            assert!(x.len() <= BUFF_NAME_CAP);
        }
    }
}
