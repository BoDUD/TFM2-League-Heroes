//! 魔腾黑暗附加包 v3：R「鬼影重重」——全地图变暗，敌人只能看见、只打得到身边。
//!
//! 主包里魔腾的 R 让己方所有英雄隐身 3 秒、敌方英雄头上一团黑雾，再飞扑一名敌方英雄。
//! `mod.override_info` 把主包的魔腾换成 `override/` 里的副本：那条「全体隐身 180 tick」换成本包的
//! 原生效果 `start`，别的（黑雾、飞扑、伤害、画面、声音）照旧。
//!
//! - 模拟里（`start` + 每 tick 的 `tick`）：魔腾一方的每个英雄，`NEAR` 内没有敌方英雄
//!   时隐身 2 tick（每 tick 续上），有敌人贴近就现身——League 里被黑暗笼罩的人视野缩到身边，
//!   本作没有按队伍改视野的接口，用「贴近才看得见」来做。
//! - 黑暗只在大招的动作里（v4）：从出手到落地（最长 `FLY_T`），落地（`land`）后再 `LAND_T`（落地爆开的动作）。
//!   原来固定 180 tick（3 秒），魔腾 0.75 秒就落地爆开完了，之后两秒多看不出在放大、队友却还隐着身
//!   （用户：「魔腾不放大的时候也全队隐身」，选了「只在大招动作期间隐身」）。
//! - 鬼影重重（v3，`Paranoia`：每个玩家每 tick 的 AI 输入钩子）：本作的视野是全队共享的——一个敌人贴近，
//!   整队都看得见，魔腾飞扑落地后连远处的射手都锁他（用户：「梦魇开大时5个隐身别人还可以攻击的到」，模拟里
//!   R 期间 52 次出手 47 次打魔腾、一半从 6 万外）。League 的鬼影重重是每个敌人只看得见自己身边、没有共享
//!   视野，所以黑暗里每个敌方英雄要攻击、施放到的魔腾一方单位（英雄、小兵）离他超过 `SIGHT`，这一下就换成
//!   朝它走过去；走到 `SIGHT` 以内照常出手。指向点的技能看点附近 `AIM_POS` 内的单位，指方向的看方向两侧
//!   `AIM_DEG` 度、`AIM_REACH` 内离方向线最近的。
//! - 画面：R 出手时在地图中心播 `VEIL_LAYERS` 层铺满整张地图的半透明暗色（`VEIL`，副本里加的特效，
//!   贴图在 `effects/`），错开 `VEIL_STEP` tick 叠上去，各播 3 秒，所以渐入、渐出。特效画在单位下面
//!   （z −2）：地面变黑，英雄和技能特效照样看得清。它是普通的特效事件，跟着比赛画面同步播。
//!   （v1 用客户端每帧叠一层暗色、跟着模拟的「黑暗还在」走；可游戏先在后台快速算完比赛再按正常
//!   速度播给你看，暗色和画面对不上，不放大也一闪一闪地黑——已去掉。）
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_nocturne_dark.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_nocturne_dark";

/// 黑暗从 R 出手算起最长这么久（同主包出手时的隐身）：飞扑最长约 32 tick（每 tick 3500，施放距离 110000）；
/// 落地时改成再 `LAND_T`。
pub const FLY_T: usize = 32;
/// 落地后黑暗再留这么久（同主包落地时的隐身）：落地爆开的动作 ult_hit 20 tick。
pub const LAND_T: usize = 20;
/// 敌方英雄这么近才看得见魔腾一方的英雄。
pub const NEAR: f64 = 40_000.0;
/// 每 tick 续的隐身时长。
const VEIL_T: usize = 2;
/// 魔腾身上的标记：黑暗还在。
const ON: &str = "league_nocturne_dark_on";
/// 黑暗里敌方英雄看得见（打得到）的魔腾一方单位：身边这么近（同 `NEAR`）。
pub const SIGHT: f64 = NEAR;
/// 指向点的技能：点旁边这么近有魔腾一方的单位，就算瞄的它。
pub const AIM_POS: f64 = 15_000.0;
/// 指方向的技能：方向两侧这么多度、这么远以内的魔腾一方单位，算瞄的它。
pub const AIM_DEG: f64 = 15.0;
pub const AIM_REACH: f64 = 150_000.0;
/// 同一个敌人被拦下，这么多 tick 内只记一行日志。
const LOG_EVERY: usize = 30;

/// 铺满地图的暗色特效（副本的 view_effects 里加的，贴图 `effects/league_nocturne_dark`）、播在哪（地图中心）、
/// 叠几层、每层隔几 tick。
pub const VEIL: &str = "league_nocturne_dark_veil";
pub const MAP_CENTER: (u64, u64) = (480_000, 480_000);
pub const VEIL_LAYERS: usize = 3;
pub const VEIL_STEP: usize = 4;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_NOCTURNE_DARK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_nocturne_dark.log");
        }
    }
    PathBuf::from("league_nocturne_dark.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
}

fn head(sim: &StableSim<'_>, id: usize) -> String {
    head_of(sim, "nocturne", id)
}

fn head_of(sim: &StableSim<'_>, who: &str, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let label = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{label} m={} s={}] t={} {who}#{id}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 模拟：贴近才看得见 =====================

fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 这一 tick 要隐身的己方英雄：`NEAR` 内没有敌方英雄的。
pub fn to_hide(allies: &[(usize, (f64, f64))], enemies: &[(f64, f64)]) -> Vec<usize> {
    allies.iter().filter(|(_, at)| enemies.iter().all(|e| dist(*at, *e) > NEAR)).map(|(id, _)| *id).collect()
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).any(|i| e.buff_at(i).is_some_and(|b| b.name() == name)))
}

/// 隐身 `NEAR` 外的己方英雄；返回 (隐身的, 己方总数)。
fn veil(sim: &mut StableSim<'_>, nocturne: usize) -> (usize, usize) {
    let team = sim.get_entity(nocturne).map_or(0, |e| e.team());
    let mut allies = Vec::new();
    let mut enemies = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if !e.is_champion() || !e.is_alive() {
            continue;
        }
        let (x, y) = e.pos();
        if e.team() == team {
            allies.push((e.id(), (x as f64, y as f64)));
        } else {
            enemies.push((x as f64, y as f64));
        }
    }
    let hide = to_hide(&allies, &enemies);
    for id in &hide {
        sim.entity_set_invisible(*id, VEIL_T);
    }
    (hide.len(), allies.len())
}

fn queue(sim: &mut StableSim<'_>, step: &str, nocturne: usize, delay: usize) {
    let name = format!("{ID}:{step}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, nocturne, &InputTargetV1::target(nocturne), delay) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, nocturne)));
    }
}

/// 在地图中心播一层暗色。
fn dark_layer(sim: &mut StableSim<'_>, nocturne: usize) {
    let at = InputTargetV1::pos(MAP_CENTER.0, MAP_CENTER.1);
    sim.play_view_effect(VEIL, nocturne, &at, 0, 0, 0);
}

/// R 出手：黑暗到落地（最长 `FLY_T` tick），画面暗色叠 `VEIL_LAYERS` 层。
fn start(sim: &mut StableSim<'_>, nocturne: usize) {
    sim.entity_remove_buff(nocturne, ON);
    sim.add_buff(nocturne, &BuffV1::timed(ON, FLY_T));
    let (hidden, allies) = veil(sim, nocturne);
    dark_layer(sim, nocturne);
    for k in 1..VEIL_LAYERS {
        queue(sim, "layer", nocturne, k * VEIL_STEP);
    }
    queue(sim, "tick", nocturne, 1);
    wlog(format!(
        "{} DARKNESS until the landing (at most {FLY_T} ticks), then {LAND_T}: {hidden} of {allies} allies unseen",
        head(sim, nocturne)
    ));
}

/// R 落地：黑暗只再留 `LAND_T` tick（落地爆开的动作），之后结束；飞得比 `FLY_T` 久、黑暗已经停了，就从落地再开 `LAND_T`。
fn land(sim: &mut StableSim<'_>, nocturne: usize) {
    let running = has_buff(sim, nocturne, ON);
    sim.entity_remove_buff(nocturne, ON);
    sim.add_buff(nocturne, &BuffV1::timed(ON, LAND_T));
    veil(sim, nocturne);
    if !running {
        queue(sim, "tick", nocturne, 1);
    }
    wlog(format!("{} landed: darkness for {LAND_T} more ticks", head(sim, nocturne)));
}

/// 每 tick：黑暗还在就重新隐身（贴近的敌人看得见），没了就结束。
fn tick(sim: &mut StableSim<'_>, nocturne: usize) {
    if !has_buff(sim, nocturne, ON) {
        wlog(format!("{} darkness over", head(sim, nocturne)));
        return;
    }
    veil(sim, nocturne);
    queue(sim, "tick", nocturne, 1);
}

// ===================== 鬼影重重：只打得到身边的 =====================

fn fpos(p: (u64, u64)) -> (f64, f64) {
    (p.0 as f64, p.1 as f64)
}

/// 看不见就不出手：瞄的位置 `aim` 离出手的人 `me` 超过 `SIGHT`，就改成朝那里走（返回要走去的点）。
pub fn blinded(me: (f64, f64), aim: (f64, f64)) -> Option<(f64, f64)> {
    (dist(me, aim) > SIGHT).then_some(aim)
}

/// 指向点的技能瞄的是谁：点旁边 `AIM_POS` 以内最近的魔腾一方单位。
pub fn aimed_at_point(p: (f64, f64), dark: &[(f64, f64)]) -> Option<(f64, f64)> {
    dark.iter().copied().filter(|u| dist(p, *u) <= AIM_POS).min_by(|a, b| dist(p, *a).total_cmp(&dist(p, *b)))
}

/// 指方向的技能瞄的是谁：从 `me` 沿 `dir` 两侧 `AIM_DEG` 度、`AIM_REACH` 以内，离方向线最近的魔腾一方单位。
pub fn aimed_along(me: (f64, f64), dir: (f64, f64), dark: &[(f64, f64)]) -> Option<(f64, f64)> {
    let len = (dir.0 * dir.0 + dir.1 * dir.1).sqrt();
    if len == 0.0 {
        return None;
    }
    let (ux, uy) = (dir.0 / len, dir.1 / len);
    let cos_max = AIM_DEG.to_radians().cos();
    dark.iter()
        .copied()
        .filter_map(|u| {
            let (vx, vy) = (u.0 - me.0, u.1 - me.1);
            let d = (vx * vx + vy * vy).sqrt();
            let along = vx * ux + vy * uy;
            (d > 0.0 && d <= AIM_REACH && along / d >= cos_max).then_some((u, (d * d - along * along).max(0.0)))
        })
        .min_by(|a, b| a.1.total_cmp(&b.1))
        .map(|(u, _)| u)
}

/// 正对着 `team` 的黑暗：对面一方有魔腾带着 `ON`，返回对面那一方。
fn darkness_against(sim: &StableSim<'_>, team: usize) -> Option<usize> {
    (0..sim.entity_count()).find_map(|i| {
        let e = sim.entity_at(i)?;
        (e.is_champion() && e.team() != team && has_buff(sim, e.id(), ON)).then(|| e.team())
    })
}

#[derive(Clone, Default)]
struct Paranoia {
    /// 上次记日志的 tick（每个玩家一份）。
    last_log: Option<usize>,
}

impl StablePlayerAi for Paranoia {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:paranoia")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let input = base?;
        let kind = InputKindV1::from_code(input.kind)?;
        if matches!(kind, InputKindV1::Move | InputKindV1::Return) {
            return None;
        }
        let player = ctx.player_id();
        let team = ctx.team();
        let sim = ctx.sim()?;
        let dark_team = darkness_against(&sim, team)?;
        let me = sim.get_player(player)?.champion()?;
        let my = fpos(me.pos());
        let mut dark = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.team() == dark_team && e.is_alive() && (e.is_champion() || e.is_minion()) {
                dark.push((e.id(), fpos(e.pos())));
            }
        }
        let spots: Vec<(f64, f64)> = dark.iter().map(|(_, p)| *p).collect();
        let t = input.target;
        let aim = match InputTargetKindV1::from_code(t.kind)? {
            InputTargetKindV1::Target => dark.iter().find(|(id, _)| *id == t.target_id).map(|(_, p)| *p)?,
            InputTargetKindV1::Pos => aimed_at_point((t.x as f64, t.y as f64), &spots)?,
            InputTargetKindV1::Dir => aimed_along(my, (t.dir_x as f64, t.dir_y as f64), &spots)?,
            InputTargetKindV1::None => return None,
        };
        let to = blinded(my, aim)?;
        let now = sim.tick();
        if self.last_log.is_none_or(|t0| now >= t0 + LOG_EVERY) {
            self.last_log = Some(now);
            wlog(format!(
                "{} PARANOIA: player {player} {kind:?} out of sight ({:.0} away) - walks there instead",
                head_of(&sim, "enemy", me.id()),
                dist(my, aim)
            ));
        }
        Some(InputV1::move_to(to.0 as u64, to.1 as u64))
    }
}

// ===================== 注册 =====================

struct Start;
impl StableEffectType for Start {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        start(sim, caster);
    }
}

struct Land;
impl StableEffectType for Land {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        land(sim, caster);
    }
}

struct Tick;
impl StableEffectType for Tick {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        tick(sim, caster);
    }
}

struct Layer;
impl StableEffectType for Layer {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        dark_layer(sim, caster);
    }
}

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    // 上一次启动的日志留一份（.prev.log），重启游戏不丢
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Paranoia: darkness, map veil, enemies hit only what is near) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:start"), Start);
    module.add_native_effect(format!("{ID}:land"), Land);
    module.add_native_effect(format!("{ID}:tick"), Tick);
    module.add_native_effect(format!("{ID}:layer"), Layer);
    module.add_player_input_ai(Paranoia::default());
    host.log(LogLevel::Info, "league_nocturne_dark v4 loaded (Nocturne's R darkens the map while he flies and lands; enemies hit only what is near).");
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
    fn only_allies_with_an_enemy_close_are_seen() {
        let allies = [(1, (100_000.0, 100_000.0)), (2, (300_000.0, 300_000.0)), (3, (500_000.0, 500_000.0))];
        let enemies = [(130_000.0, 100_000.0), (500_000.0, 545_000.0)];
        // #1 有敌人在 30000 内：看得见；#3 的敌人在 45000：看不见
        assert_eq!(to_hide(&allies, &enemies), [2, 3]);
        assert_eq!(to_hide(&allies, &[]), [1, 2, 3]);
    }

    #[test]
    fn far_targets_turn_into_a_walk() {
        let me = (100_000.0, 100_000.0);
        // 3 万外看得见：照常出手；6 万外看不见：改成走过去
        assert_eq!(blinded(me, (130_000.0, 100_000.0)), None);
        assert_eq!(blinded(me, (160_000.0, 100_000.0)), Some((160_000.0, 100_000.0)));
    }

    #[test]
    fn point_and_direction_skills_find_what_they_aim_at() {
        let dark = [(200_000.0, 100_000.0), (100_000.0, 220_000.0)];
        assert_eq!(aimed_at_point((205_000.0, 104_000.0), &dark), Some((200_000.0, 100_000.0)));
        assert_eq!(aimed_at_point((150_000.0, 150_000.0), &dark), None);
        let me = (100_000.0, 100_000.0);
        assert_eq!(aimed_along(me, (1.0, 0.05), &dark), Some((200_000.0, 100_000.0)));
        assert_eq!(aimed_along(me, (0.0, 1.0), &dark), Some((100_000.0, 220_000.0)));
        assert_eq!(aimed_along(me, (-1.0, 0.0), &dark), None);
        assert_eq!(aimed_along(me, (0.0, 0.0), &dark), None);
    }
}
