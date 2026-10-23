//! 梅尔附加包（用户选「做附加包」）：主包数据做不到的两件事，加上连招。
//!
//! `mod.override_info` 把主包的梅尔换成 `override/` 里的副本（tools/kit/build_mel.py 的 native）：数据和主包一样，只是
//! 每一层夺命残影（普攻、灼灼之光的光弹、Q 的每次爆炸、E 的法球中心打中英雄时）除了主包的残影（一个 `AddCasted`，R 读它）
//! 还在英雄身上挂一层 `m_mark`（本包数层数用），并调本包的 `league_mel:overwhelm`；普攻不再挂主包每 25 秒一次的屏障，被动
//! 挂本包的 `league_mel:reflect`（参数在英雄数据的 `passive.params` 里）。
//!
//! - **夺命残影的处决**：英雄联盟里残影的伤害够了，下一次打中就直接处决。`overwhelm` 在每层残影挂上时数那名英雄身上的
//!   `m_mark` 层数，层数 × (`x_st` + `x_ratio`% 法强) ≥ 他的生命 + 护盾，就处决他（真实伤害打掉剩下的生命，消耗本包的层数）。
//! - **灵魂折镜**：英雄联盟里 W 把敌人的弹体反弹回去、她自己不受伤害。数据里没有效果能挡住或拐弯一个弹体。被动每 tick 看
//!   一遍场上的弹体：W 好了（`w_cd`）、一个敌方英雄的弹体飞到她 `w_near` 以内，就张开屏障 `w_t` tick（`w_on`：受到的伤害
//!   减少 `w_red`%、反弹 `w_ref`%、移速 +`w_ms`%，和主包的同名屏障一样，画面也一样）；屏障开着时，飞到她 `w_back` 以内的每个
//!   敌方英雄的弹体（同一个人 `REFLECT_GAP` tick 内只算一次），复制一枚金色光弹飞回发射的人，打中造成 `w_back_dmg` +
//!   `w_back_r`% 法强魔法伤害（原来的弹体删不掉，靠屏障免伤）。
//! - **连招**（用户：「有连招要做连招」；`combo.rs`）：AI 钩子 `league_mel:combo` 替游戏的 AI 按 Q、E、R——E → Q（先禁锢，
//!   禁锢住了马上把 Q 砸在被禁锢的英雄身上，主包数据做的快速落点）、残影够杀人或两个英雄都叠满了才按 R。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_mel.log`，每次启动游戏重写：`SPAWN`、`EXECUTE`、`W UP`、
//! `REFLECT`、`E FIRST` / `Q ON ROOT` / `R KILL` / `R MANY` / `R HELD`（连招），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod combo;

const ID: &str = "league_mel";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.3";

/// 同一个人的弹体隔多久才再反弹一次（一个弹体从进圈到打中只有几 tick；读不到弹体的编号）。
pub const REFLECT_GAP: usize = 20;
/// 反弹回去的光弹的速度（每 tick）。
pub const BACK_SPEED: f64 = 5000.0;

fn sn(x: &str) -> String {
    format!("league_mel_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_MEL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_mel.log");
        }
    }
    PathBuf::from("league_mel.log")
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
    /// 处决：每层残影值多少（`x_st` + `x_ratio`% 法强）
    pub x_st: usize,
    pub x_ratio: usize,
    /// 灵魂折镜：冷却、持续、减伤、反弹、移速、张开的距离、反弹的距离、反弹光弹的伤害
    pub w_cd: usize,
    pub w_t: usize,
    pub w_red: usize,
    pub w_ref: usize,
    pub w_ms: usize,
    pub w_near: usize,
    pub w_back: usize,
    pub w_back_dmg: usize,
    pub w_back_r: usize,
    // the combos (combo.rs): the reaches, R's cooldown, R's worth a stack, the stacks' life
    pub atk_range: usize,
    pub q_range: usize,
    pub e_range: usize,
    pub r_range: usize,
    pub r_cd: usize,
    pub r_st: usize,
    pub r_ratio: usize,
    pub m_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { x_st: 15, x_ratio: 8, w_cd: 1500, w_t: 75, w_red: 50, w_ref: 40, w_ms: 25, w_near: 30000,
                 w_back: 6000, w_back_dmg: 40, w_back_r: 25, atk_range: 55000, q_range: 85000, e_range: 80000,
                 r_range: 70000, r_cd: 2100, r_st: 15, r_ratio: 8, m_t: 360 }
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
            "x_st" => p.x_st = v,
            "x_ratio" => p.x_ratio = v,
            "w_cd" => p.w_cd = v,
            "w_t" => p.w_t = v,
            "w_red" => p.w_red = v,
            "w_ref" => p.w_ref = v,
            "w_ms" => p.w_ms = v,
            "w_near" => p.w_near = v,
            "w_back" => p.w_back = v,
            "w_back_dmg" => p.w_back_dmg = v,
            "w_back_r" => p.w_back_r = v,
            "atk_range" => p.atk_range = v,
            "q_range" => p.q_range = v,
            "e_range" => p.e_range = v,
            "r_range" => p.r_range = v,
            "r_cd" => p.r_cd = v,
            "r_st" => p.r_st = v,
            "r_ratio" => p.r_ratio = v,
            "m_t" => p.m_t = v,
            _ => {}
        }
    }
    p
}

/// 每个梅尔的参数（被动 configure 时存下，原生效果和 AI 钩子里读）：键是 (这局的种子, 她的编号)。
static PARAMS: LazyLock<Mutex<HashMap<(u64, usize), Params>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn params_of(sim: &StableSim<'_>, me: usize) -> Params {
    PARAMS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim.seed(), me)).copied().unwrap_or_default()
}

// ===================== 计算（单元测试用） =====================

/// `stacks` 层残影值多少伤害：每层 `per` + `ratio`% 法强。
pub fn stacks_worth(stacks: usize, per: usize, ratio: usize, ap: usize) -> usize {
    stacks * (per + ratio * ap / 100)
}

/// 残影够不够处决：值的伤害 ≥ 生命 + 护盾。
pub fn executes(stacks: usize, ap: usize, hp: usize, shield: usize, p: &Params) -> bool {
    stacks > 0 && stacks_worth(stacks, p.x_st, p.x_ratio, ap) >= hp + shield
}

/// 反弹回去的光弹的伤害。
pub fn back_damage(ap: usize, p: &Params) -> usize {
    p.w_back_dmg + p.w_back_r * ap / 100
}

fn ap_of(sim: &StableSim<'_>, me: usize) -> usize {
    sim.get_entity(me).map_or(0, |e| e.stat().magic_power)
}

/// 一个单位身上某个名字的增益有几层。
pub fn count_buff(e: &StableEntity<'_, '_>, name: &str) -> usize {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).count()
}

// ===================== 原生效果 =====================

/// 一层残影刚挂上：够了就处决。
fn overwhelm(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let t = input.target_id;
    let p = params_of(sim, me);
    let ap = ap_of(sim, me);
    let mark = sn("m_mark");
    let Some(u) = sim.get_entity(t) else { return };
    if !u.is_alive() || !u.is_champion() {
        return;
    }
    let (hp, _) = u.hp();
    let shield = u.shield();
    let stacks = count_buff(&u, &mark);
    if !executes(stacks, ap, hp, shield, &p) {
        return;
    }
    let worth = stacks_worth(stacks, p.x_st, p.x_ratio, ap);
    sim.deal_damage_typed(me, t, hp + shield + 1, DamageTypeV1::Fixed, AttackTypeV1::Skill);
    sim.entity_remove_buff(t, &mark);
    let hit = InputTargetV1::target(t);
    sim.play_view_effect(&sn("x_hit"), me, &hit, 0, 0, 0);
    sim.play_sfx(&sn("x"), me, &hit);
    if let Some(k) = counted("execute") {
        wlog(format!("{} EXECUTE #{k}: {} - {stacks} stacks worth {worth} >= health {hp} + shield {shield}", head(sim, me),
                     who(sim, t)));
    }
}

struct OverwhelmFx;
impl StableEffectType for OverwhelmFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        overwhelm(sim, caster, input);
    }
}

/// 反弹光弹只是画面：伤害在 `Reflect` 里按飞行时间结算。
struct NoopFx;
impl StableEffectType for NoopFx {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 被动：灵魂折镜 =====================

#[derive(Clone, Copy, Debug, PartialEq)]
struct Back {
    target: usize,
    due: usize,
    dmg: usize,
}

#[derive(Clone, Default)]
struct Reflect {
    p: Params,
    ready_at: usize,
    until: usize,
    /// 发射的人 -> 上次反弹他的 tick
    last: HashMap<usize, usize>,
    backs: Vec<Back>,
}

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

impl Reflect {
    fn tick(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        // the reflected bolts landing
        let due: Vec<Back> = self.backs.iter().copied().filter(|b| b.due <= now).collect();
        self.backs.retain(|b| b.due > now);
        for b in due {
            if sim.get_entity(b.target).is_some_and(|u| u.is_alive()) {
                sim.deal_damage_typed(me, b.target, b.dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                let hit = InputTargetV1::target(b.target);
                sim.play_view_effect(&sn("a_hit"), me, &hit, 0, 0, 0);
            }
        }
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.until = 0;
            return;
        }
        let team = e.team();
        let (x, y) = e.pos();
        let at = (x as f64, y as f64);
        let r = e.radius() as f64;
        // enemy champions' projectiles near her: (distance, caster)
        let mut near = Vec::new();
        for i in 0..sim.projectile_count() {
            let Some(pr) = sim.projectile_at(i) else { continue };
            if pr.is_end || pr.team == team {
                continue;
            }
            if !sim.get_entity(pr.caster_id).is_some_and(|c| c.is_champion() && c.is_alive()) {
                continue;
            }
            near.push((dist(at, (pr.x as f64, pr.y as f64)) - r, pr.caster_id));
        }
        if now >= self.ready_at && near.iter().any(|&(d, _)| d <= self.p.w_near as f64) {
            let mut b = BuffV1::timed(&sn("w_on"), self.p.w_t);
            b.damaged_reduce = self.p.w_red;
            b.damage_reflect = self.p.w_ref;
            b.move_speed_mult = self.p.w_ms as i32;
            sim.add_buff(me, &b);
            self.until = now + self.p.w_t;
            self.ready_at = now + self.p.w_cd;
            let at_me = InputTargetV1::target(me);
            sim.play_sfx(&sn("w"), me, &at_me);
            sim.play_sfx(&sn("vo_w"), me, &at_me);
            if let Some(k) = counted("w up") {
                let (d, c) = near.iter().copied().min_by(|a, b| a.0.total_cmp(&b.0)).unwrap_or((0.0, me));
                wlog(format!("{} W UP #{k}: a projectile of {} {d:.0} away - the barrier for {} ticks", head(sim, me),
                             who(sim, c), self.p.w_t));
            }
        }
        if now >= self.until {
            return;
        }
        let ap = ap_of(sim, me);
        for &(d, c) in &near {
            if d > self.p.w_back as f64 || self.last.get(&c).is_some_and(|&t0| now < t0 + REFLECT_GAP) {
                continue;
            }
            self.last.insert(c, now);
            let Some(cu) = sim.get_entity(c) else { continue };
            let (cx, cy) = cu.pos();
            let fly = (dist(at, (cx as f64, cy as f64)) / BACK_SPEED).ceil().max(1.0) as usize;
            let spec = ProjectileSpawnV1 {
                caster_id: me,
                team,
                x,
                y: y.saturating_sub(5000),
                radius: 1_000,
                speed: BACK_SPEED as u64,
                move_kind: ProjectileMoveKindV1::Target.code(),
                target_id: c,
                target_x: 0,
                target_y: 0,
                penetrate: false,
                attack_type: AttackTypeV1::Skill.code(),
                casting_type: CastingTypeV1::Targeting.code(),
                casting_target: CastingTargetV1::None.code(),
            };
            sim.spawn_projectile(&sn("w_back"), &format!("{ID}:noop"), &spec);
            let dmg = back_damage(ap, &self.p);
            self.backs.push(Back { target: c, due: now + fly, dmg });
            sim.play_sfx(&sn("w_reflect"), me, &InputTargetV1::target(me));
            if let Some(k) = counted("reflect") {
                wlog(format!("{} REFLECT #{k}: a projectile of {} sent back ({dmg} magic in {fly} ticks)", head(sim, me),
                             who(sim, c)));
            }
        }
    }
}

impl StablePassive for Reflect {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        PARAMS.lock().unwrap_or_else(|e| e.into_inner()).insert((sim.seed(), me), self.p);
        self.until = 0;
        self.backs.clear();
        self.last.clear();
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Mel (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.tick(sim, me);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Mel: Overwhelm's execute, Rebuttal reflecting projectiles, the combos) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:overwhelm"), OverwhelmFx);
    module.add_native_effect(format!("{ID}:noop"), NoopFx);
    module.add_native_passive(format!("{ID}:reflect"), Reflect::default());
    module.add_player_input_ai(combo::Combo::default());
    host.log(LogLevel::Info, "league_mel loaded (Overwhelm's execute, Rebuttal reflecting projectiles, the combos).");
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
    fn the_stacks_execute_when_they_are_worth_the_health() {
        let p = Params::default();
        // 15 + 8% of 200 = 31 a stack
        assert_eq!(stacks_worth(10, p.x_st, p.x_ratio, 200), 310);
        assert!(executes(10, 200, 300, 0, &p));
        assert!(!executes(10, 200, 300, 20, &p));
        assert!(!executes(0, 200, 0, 0, &p));
        assert!(!executes(3, 200, 500, 0, &p));
    }

    #[test]
    fn the_reflected_bolt_scales_with_ap() {
        let p = Params::default();
        assert_eq!(back_damage(0, &p), 40);
        assert_eq!(back_damage(200, &p), 90);
    }

    #[test]
    fn params_parse() {
        assert_eq!(parse_params(r#"{"x_st":15,"x_ratio":8,"w_cd":1500,"w_t":75,"w_red":50,"w_ref":40,"w_ms":25,"w_near":30000,"w_back":6000,"w_back_dmg":40,"w_back_r":25,"atk_range":55000,"q_range":85000,"e_range":80000,"r_range":70000,"r_cd":2100,"r_st":15,"r_ratio":8,"m_t":360}"#), Params::default());
        assert_eq!(parse_params(r#"{"x_st":30}"#).x_st, 30);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_mel.py");
        let src = std::fs::read_to_string(path).expect("build_mel.py");
        let d = Params::default();
        for (k, v) in [("x_st", d.x_st), ("x_ratio", d.x_ratio), ("w_cd", d.w_cd), ("w_t", d.w_t), ("w_red", d.w_red),
                       ("w_ref", d.w_ref), ("w_ms", d.w_ms), ("w_near", d.w_near), ("w_back", d.w_back),
                       ("w_back_dmg", d.w_back_dmg), ("w_back_r", d.w_back_r), ("atk_range", d.atk_range),
                       ("q_range", d.q_range), ("e_range", d.e_range), ("r_range", d.r_range), ("r_cd", d.r_cd),
                       ("r_st", d.r_st), ("r_ratio", d.r_ratio), ("m_t", d.m_t)] {
            assert!(src.contains(&format!("\"{k}\": {v}")), "{k} is not {v} in build_mel.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["w_on", "m_mark", "e_combo", "e_bound", "w_back", "w_reflect"] {
            assert!(sn(x).len() <= BUFF_NAME_CAP);
        }
    }
}
