//! 格雷福斯附加包（用户选「做附加包」）：主包数据做不到的三件事。
//!
//! `mod.override_info` 把主包的格雷福斯换成 `override/` 里的副本（tools/kit/build_graves.py 的 native）：数据和主包一样，
//! 只是霰弹枪的弹丸和扇形每打中一个单位调一次本包的 `league_graves:hit`，大招的爆弹打中英雄时调 `league_graves:cone`
//! （去掉主包那一圈爆炸），被动挂本包的 `league_graves:grit`（参数在英雄数据的 `passive.params` 里）。
//!
//! - **快速拔枪的冷却**：英雄联盟里格雷福斯的普攻每有一颗弹丸打中，E 的冷却少 0.5 秒。数据不能减冷却。本包每次 `hit`
//!   把 E（技能 2）的冷却减 `e_cut` tick，一次普攻最多 `e_cuts` 下（四颗弹丸）。
//! - **击退小兵和野怪**：英雄联盟里被几颗弹丸同时打中的非英雄单位会被击退。一次普攻里同一个单位挨了两下（正面那颗弹丸
//!   和扇形）且不是英雄、不是塔，就把它往外推 `kb_speed` × `kb_t`。
//! - **终极爆弹的锥形爆炸**：英雄联盟里爆弹打中第一个英雄后在他身后炸开一个锥形。主包只能在那名英雄身边炸一圈；本包按
//!   格雷福斯到那名英雄的方向，在那名英雄身后 `r_len` 内、偏离不到 acos(`r_dot`/1000) 的敌方单位（塔除外，不含那名英雄）
//!   受到 `r2_dmg` + `r2_ratio`% 攻击力的物理伤害。
//!
//! - **穷途末路撞墙**（0.2.0，用户：「还有Q技能碰到墙会马上弹回来吗 和英雄联盟一样」；`shell.rs`）：副本的 Q 由本包发射——
//!   炮弹撞到墙就停在墙边，`q_wall` tick 后就炸（没撞墙照旧 `q_fuse`），炸完炮弹沿原路飞回出手的地方、沿途再打一次。
//! - **连招**（0.2.0，用户：「有连招的话一起做了」；`combo.rs`）：AI 钩子 `league_graves:combo` 替游戏的 AI 决定 E、R
//!   什么时候按——E 留到第一发打出去之后再按（装回一发，一轮换弹打三枪：普攻 → E → 普攻 → 普攻），弹匣满着或已经在换弹时
//!   AI 按的 E 改成普攻（逃命、追残血、够不着敌人时照放）；R 只在打得死路上第一个英雄、或他身后锥形里还有英雄、或自己残血
//!   时放，有打得死的英雄就替 AI 按。
//!
//! 一次普攻：同一个格雷福斯（按这局的种子和他的编号分开）第一次 `hit` 起 `VOLLEY_T` tick 内的都算这一枪（扇形在开枪那
//! tick 打中，正面那颗弹丸飞到目标最多几 tick）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_graves.log`，每次启动游戏重写：`CUT` / `KNOCK` / `CONE`
//! （上面三件事），`Q` / `Q BOOM` / `Q BACK`（撞墙的炮弹），`E PRESS` / `E VETO` / `R PRESS` / `R VETO`（连招），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod combo;
pub mod shell;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;

const ID: &str = "league_graves";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_graves") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

/// 一枪的时间窗：第一次打中起这么多 tick 内的打中都算同一枪（他的普攻间隔 54 tick）。
pub const VOLLEY_T: usize = 14;

fn sn(x: &str) -> String {
    format!("league_graves_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_GRAVES_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_graves.log");
        }
    }
    PathBuf::from("league_graves.log")
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
    pub e_cut: usize,
    pub e_cuts: usize,
    pub kb_speed: usize,
    pub kb_t: usize,
    pub r2_dmg: usize,
    pub r2_ratio: usize,
    pub r_len: usize,
    pub r_dot: usize,
    // the combos (combo.rs): the shotgun's shell flag and shot tick, the reaches, R's line and damage
    pub a_hit: usize,
    pub a_keep: usize,
    pub atk_range: usize,
    pub e_range: usize,
    pub e_near: usize,
    pub r_cast: usize,
    pub r_range: usize,
    pub r_w: usize,
    pub r_dmg: usize,
    pub r_ratio: usize,
    // Q's shell stopped by walls (shell.rs): the shell, the bomb, the fuse (a wall's)
    pub q_dmg: usize,
    pub q_ratio: usize,
    pub q2_dmg: usize,
    pub q2_ratio: usize,
    pub q_range: usize,
    pub q_speed: usize,
    pub q_w: usize,
    pub q_r: usize,
    pub q_fuse: usize,
    pub q_wall: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { e_cut: 30, e_cuts: 4, kb_speed: 1500, kb_t: 4, r2_dmg: 80, r2_ratio: 60, r_len: 55000, r_dot: 866,
                 a_hit: 8, a_keep: 300, atk_range: 46000, e_range: 60000, e_near: 22000, r_cast: 100000,
                 r_range: 110000, r_w: 12000, r_dmg: 120, r_ratio: 90, q_dmg: 45, q_ratio: 60, q2_dmg: 60,
                 q2_ratio: 80, q_range: 70000, q_speed: 5000, q_w: 8000, q_r: 24000, q_fuse: 60, q_wall: 15 }
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
            "e_cut" => p.e_cut = v,
            "e_cuts" => p.e_cuts = v,
            "kb_speed" => p.kb_speed = v,
            "kb_t" => p.kb_t = v,
            "r2_dmg" => p.r2_dmg = v,
            "r2_ratio" => p.r2_ratio = v,
            "r_len" => p.r_len = v,
            "r_dot" => p.r_dot = v,
            "a_hit" => p.a_hit = v,
            "a_keep" => p.a_keep = v,
            "atk_range" => p.atk_range = v,
            "e_range" => p.e_range = v,
            "e_near" => p.e_near = v,
            "r_cast" => p.r_cast = v,
            "r_range" => p.r_range = v,
            "r_w" => p.r_w = v,
            "r_dmg" => p.r_dmg = v,
            "r_ratio" => p.r_ratio = v,
            "q_dmg" => p.q_dmg = v,
            "q_ratio" => p.q_ratio = v,
            "q2_dmg" => p.q2_dmg = v,
            "q2_ratio" => p.q2_ratio = v,
            "q_range" => p.q_range = v,
            "q_speed" => p.q_speed = v,
            "q_w" => p.q_w = v,
            "q_r" => p.q_r = v,
            "q_fuse" => p.q_fuse = v,
            "q_wall" => p.q_wall = v,
            _ => {}
        }
    }
    p
}

/// 每个格雷福斯的参数（被动 configure 时存下，原生效果里读）：键是 (这局的种子, 他的编号)。
static PARAMS: LazyLock<Mutex<HashMap<(u64, usize), Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim.seed(), me)).copied().unwrap_or_default()
}

// ===================== 计算（单元测试用） =====================

/// 一枪：从第一次打中的 tick 起，减过几次冷却，打中过哪些单位（各几下）。
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Volley {
    pub start: usize,
    pub cuts: usize,
    pub hits: Vec<(usize, usize)>,
}

impl Volley {
    /// 这一下打中 `unit`：返回 (这下减不减冷却, 这个单位在这枪里挨的是第几下)。`now` 离这枪开始超过 `VOLLEY_T` 就是新的一枪。
    pub fn hit(&mut self, now: usize, unit: usize, cap: usize) -> (bool, usize) {
        if self.hits.is_empty() || now >= self.start + VOLLEY_T || now < self.start {
            *self = Volley { start: now, cuts: 0, hits: Vec::new() };
        }
        let cut = self.cuts < cap;
        if cut {
            self.cuts += 1;
        }
        let n = match self.hits.iter_mut().find(|(u, _)| *u == unit) {
            Some(h) => {
                h.1 += 1;
                h.1
            }
            None => {
                self.hits.push((unit, 1));
                1
            }
        };
        (cut, n)
    }
}

static VOLLEYS: LazyLock<Mutex<HashMap<(u64, usize), Volley>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// 锥形：`me` 是格雷福斯，`hit` 是被爆弹打中的英雄，`p` 是另一个单位。它在 `hit` 身后（沿 me→hit 的方向）`len` 以内、
/// 偏离那个方向的余弦不小于 `dot`/1000 时算在锥形里。
pub fn in_cone(me: (f64, f64), hit: (f64, f64), p: (f64, f64), len: f64, dot: f64) -> bool {
    let (dx, dy) = (hit.0 - me.0, hit.1 - me.1);
    let d = (dx * dx + dy * dy).sqrt();
    if d < 1.0 {
        return false;
    }
    let (ux, uy) = (dx / d, dy / d);
    let (vx, vy) = (p.0 - hit.0, p.1 - hit.1);
    let along = vx * ux + vy * uy;
    let r = (vx * vx + vy * vy).sqrt();
    if r < 1.0 {
        return true;
    }
    along > 0.0 && r <= len && along / r >= dot / 1000.0
}

fn fpos(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    sim.get_entity(id).map(|e| {
        let (x, y) = e.pos();
        (x as f64, y as f64)
    })
}

// ===================== 原生效果 =====================

/// 霰弹枪的一下打中了 `input` 的单位。
fn pellet(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let unit = input.target_id;
    let p = params_of(sim, me);
    let now = sim.tick();
    let (cut, n) = VOLLEYS
        .lock()
        .unwrap_or_else(|e| e.into_inner())
        .entry((sim.seed(), me))
        .or_default()
        .hit(now, unit, p.e_cuts);
    if cut {
        let ok = sim.entity_reduce_cooldown(me, SkillSlotV1::Skill2, p.e_cut);
        if let Some(k) = counted("cut") {
            let left = sim.get_entity(me).and_then(|e| e.cooldown(SkillSlotV1::Skill2)).map_or(0, |c| c.remaining);
            wlog(format!("{} CUT #{k}: shotgun hit on {} - Quickdraw -{} ticks (now {left} left){}", head(sim, me),
                         who(sim, unit), p.e_cut, if ok { "" } else { " (entity_reduce_cooldown refused)" }));
        }
    }
    if n == 2 {
        let Some(e) = sim.get_entity(unit) else { return };
        if e.is_alive() && !e.is_champion() && !e.is_tower() {
            let ok = sim.entity_knockback(me, unit, p.kb_speed, p.kb_t);
            if let Some(k) = counted("knock") {
                wlog(format!("{} KNOCK #{k}: {} took two pellets - knocked back {}x{}{}", head(sim, me), who(sim, unit),
                             p.kb_speed, p.kb_t, if ok { "" } else { " (refused)" }));
            }
        }
    }
}

struct HitFx;
impl StableEffectType for HitFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        pellet(sim, caster, input);
    }
}

/// 终极爆弹打中了 `input` 的英雄：在他身后炸开锥形。
fn cone(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let hit = input.target_id;
    let (Some(a), Some(b)) = (fpos(sim, me), fpos(sim, hit)) else { return };
    let p = params_of(sim, me);
    let (team, attack) = sim.get_entity(me).map_or((usize::MAX, 0), |e| (e.team(), e.stat().attack));
    let amount = p.r2_dmg + attack * p.r2_ratio / 100;
    let mut struck = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        let id = e.id();
        if id == hit || id == me || e.team() == team || !e.is_alive() || e.is_tower() || !e.is_targetable() {
            continue;
        }
        let (x, y) = e.pos();
        if in_cone(a, b, (x as f64, y as f64), p.r_len as f64, p.r_dot as f64) {
            struck.push(id);
        }
    }
    for &id in &struck {
        sim.deal_damage_typed(me, id, amount, DamageTypeV1::Ad, AttackTypeV1::Skill);
        sim.play_view_effect(&sn("r_hit2"), me, &InputTargetV1::target(id), 0, 0, 0);
    }
    if let Some(k) = counted("cone") {
        let names: Vec<String> = struck.iter().map(|&id| who(sim, id)).collect();
        wlog(format!("{} CONE #{k}: Collateral Damage hit {} - the cone behind ({} long) struck [{}] for {amount} before armour",
                     head(sim, me), who(sim, hit), p.r_len, names.join(", ")));
    }
}

struct ConeFx;
impl StableEffectType for ConeFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        cone(sim, caster, input);
    }
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Grit {
    p: Params,
}

impl StablePassive for Grit {
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
            wlog(format!("{} SPAWN #{k}: the add-on's Graves (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Graves: Quickdraw's cooldown per pellet, knockback, Collateral Damage's cone, the combos) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:hit"), HitFx);
    module.add_native_effect(format!("{ID}:cone"), ConeFx);
    module.add_native_passive(format!("{ID}:grit"), Grit::default());
    module.add_player_input_ai(combo::Combo::default());
    shell::register(module);
    host.log(LogLevel::Info, "league_graves loaded (Quickdraw's cooldown, knockback, Collateral Damage's cone, the combos).");
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
    fn a_volley_cuts_at_most_four_times_and_counts_each_unit() {
        let mut v = Volley::default();
        assert_eq!(v.hit(100, 7, 4), (true, 1)); // the spread on the target
        assert_eq!(v.hit(100, 8, 4), (true, 1)); // the spread on another
        assert_eq!(v.hit(104, 7, 4), (true, 2)); // the pellet on the target: its second
        assert_eq!(v.hit(104, 9, 4), (true, 1));
        assert_eq!(v.hit(105, 10, 4), (false, 1)); // a fifth: no cut
        // the next attack, 54 ticks on
        assert_eq!(v.hit(154, 7, 4), (true, 1));
    }

    #[test]
    fn the_cone_lies_behind_the_champion_hit() {
        let me = (0.0, 0.0);
        let hit = (100_000.0, 0.0);
        assert!(in_cone(me, hit, (130_000.0, 5_000.0), 55_000.0, 866.0));
        assert!(!in_cone(me, hit, (90_000.0, 0.0), 55_000.0, 866.0)); // in front of him
        assert!(!in_cone(me, hit, (120_000.0, 30_000.0), 55_000.0, 866.0)); // 56 degrees off
        assert!(!in_cone(me, hit, (170_000.0, 0.0), 55_000.0, 866.0)); // too far
    }

    #[test]
    fn params_parse() {
        assert_eq!(parse_params(r#"{"a_hit":8,"e_cut":30,"e_cuts":4,"kb_speed":1500,"kb_t":4,"r2_dmg":80,"r2_ratio":60,"r_dot":866,"r_len":55000,"a_keep":300,"atk_range":46000,"e_range":60000,"e_near":22000,"r_cast":100000,"r_range":110000,"r_w":12000,"r_dmg":120,"r_ratio":90,"q_dmg":45,"q_ratio":60,"q2_dmg":60,"q2_ratio":80,"q_range":70000,"q_speed":5000,"q_w":8000,"q_r":24000,"q_fuse":60,"q_wall":15}"#), Params::default());
        assert_eq!(parse_params(r#"{"e_cut":20}"#).e_cut, 20);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_graves.py");
        let src = std::fs::read_to_string(path).expect("build_graves.py");
        let d = Params::default();
        for (k, v) in [("e_cut", d.e_cut), ("e_cuts", d.e_cuts), ("kb_speed", d.kb_speed), ("kb_t", d.kb_t),
                       ("r2_dmg", d.r2_dmg), ("r2_ratio", d.r2_ratio), ("r_len", d.r_len), ("r_dot", d.r_dot),
                       ("a_hit", d.a_hit), ("a_keep", d.a_keep), ("atk_range", d.atk_range), ("e_range", d.e_range),
                       ("e_near", d.e_near), ("r_cast", d.r_cast), ("r_range", d.r_range), ("r_w", d.r_w),
                       ("r_dmg", d.r_dmg), ("r_ratio", d.r_ratio), ("q_dmg", d.q_dmg), ("q_ratio", d.q_ratio),
                       ("q2_dmg", d.q2_dmg), ("q2_ratio", d.q2_ratio), ("q_range", d.q_range), ("q_speed", d.q_speed),
                       ("q_w", d.q_w), ("q_r", d.q_r), ("q_fuse", d.q_fuse), ("q_wall", d.q_wall)] {
            assert!(src.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in build_graves.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["r_hit2", "a_1", "q_blast_w", "q_shell"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }
}
