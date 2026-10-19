//! 古拉加斯附加包：R「爆破酒桶」的智能落点（用户选的附加包：「做：大招智能落点」）。
//!
//! 主包是纯数据，找不到「目标身后的一点」：酒桶落在目标脚下，爆炸把周围的敌人拽向古拉加斯（和英雄联盟里落在身后、把人炸向
//! 他一样的结果）。`mod.override_info` 把主包的古拉加斯换成 `override/` 里的副本（tools/kit/build_gragas.py 的 native=1）：
//! 数据和主包一样，只是出手那一 tick 不再扔主包的酒桶，而是调本包的原生效果 `league_gragas:cask`（输入是大招的目标）。
//!
//! - `cask`：读所有敌人的位置，在射程内每个敌方英雄身后（从古拉加斯看过去）0 / `BEHIND_1` / `BEHIND_2` 处各试一个落点，
//!   按炸得到的敌人打分：英雄 `CHAMP_SCORE`，离古拉加斯越远（后排）多加，小兵和野怪 `UNIT_SCORE`；同分时取更靠后的点。
//!   酒桶（主包的 `r_cask` 画面）沿直线飞过去，`R_FLY` tick 后在那里排一个 `boom`。
//! - `boom`：落点播主包的爆炸画面和音效；`R_R` 内每个敌人（塔除外）受到 `R_DMG` + `R_RATIO`% 法强的魔法伤害（走引擎的
//!   伤害流程：魔抗、统计、击杀），并被拽向古拉加斯（`entity_grab`，`R_GRAB` 每 tick、`R_GRAB_T` tick）。
//! - 他死了就不炸（落点只是画面）。
//!
//! 数字和主包 P 表的值写在这里（`R_*`），主包改了这里一起改（`tests::the_numbers_match_the_kit` 读主包的参数表核对）。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_gragas.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_gragas";

/// 主包古拉加斯的名字（画面、音效都以它开头）。
fn gr(x: &str) -> String {
    format!("league_gragas_{x}")
}

// ===================== 数值（主包 build_gragas.P） =====================

/// 大招射程（r_range）、爆炸半径（r_r）、伤害（r_dmg + r_ratio% 法强）、飞行 tick（r_fly）、拽的速度和时长（r_grab、r_grab_t）。
pub const R_RANGE: f64 = 70_000.0;
pub const R_R: f64 = 26_000.0;
pub const R_DMG: usize = 240;
pub const R_RATIO: usize = 80;
pub const R_FLY: usize = 16;
pub const R_GRAB: usize = 3_000;
pub const R_GRAB_T: usize = 12;
/// 落点试在敌方英雄身后这么远（从古拉加斯看过去）。
pub const BEHIND_1: f64 = 9_000.0;
pub const BEHIND_2: f64 = 16_000.0;
/// 落点离古拉加斯最远这么远（射程 + 一点：目标在射程边上时还能落在它身后）。
pub const REACH: f64 = R_RANGE + 18_000.0;
/// 敌人的身体半径（爆炸半径算到身体边上）。
pub const BODY: f64 = 6_000.0;
/// 打分：每个英雄、离他每远 10000 加的分（后排）、每个小兵或野怪。
pub const CHAMP_SCORE: f64 = 10.0;
pub const BACK_SCORE: f64 = 1.0;
pub const UNIT_SCORE: f64 = 0.5;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_GRAGAS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_gragas.log");
        }
    }
    PathBuf::from("league_gragas.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (15 000 lines a session,
    // about 9 s of stalls on the simulation thread, 2026-10-12, the user: 「LOL mod让游戏掉帧很严重 加载很卡」)
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

fn pt(p: (f64, f64)) -> String {
    format!("({:.0},{:.0})", p.0, p.1)
}

// ===================== 落点 =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn unit(v: (f64, f64)) -> Option<(f64, f64)> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

/// 一个敌人：位置、是不是英雄。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub at: (f64, f64),
    pub champion: bool,
}

/// 落在 `spot` 炸得到的敌人的分数（`me` 是古拉加斯）。
pub fn score(me: (f64, f64), spot: (f64, f64), foes: &[Foe]) -> f64 {
    foes.iter()
        .filter(|f| dist(f.at, spot) <= R_R + BODY)
        .map(|f| if f.champion { CHAMP_SCORE + BACK_SCORE * dist(me, f.at) / 10_000.0 } else { UNIT_SCORE })
        .sum()
}

/// 最好的落点：每个够得着的敌方英雄身后 0 / BEHIND_1 / BEHIND_2 处，分最高的；同分取更靠后的（离他更远）。
/// `target` 是大招的目标：没有更好的点时就落在它身后。
pub fn best_spot(me: (f64, f64), target: (f64, f64), foes: &[Foe]) -> (f64, f64) {
    let mut best: Option<((f64, f64), f64, f64)> = None;
    let anchors = std::iter::once(target).chain(foes.iter().filter(|f| f.champion).map(|f| f.at));
    for c in anchors {
        let Some(u) = unit((c.0 - me.0, c.1 - me.1)) else { continue };
        for off in [0.0, BEHIND_1, BEHIND_2] {
            let spot = (c.0 + u.0 * off, c.1 + u.1 * off);
            if dist(me, spot) > REACH {
                continue;
            }
            let s = score(me, spot, foes);
            let far = dist(me, spot);
            let better = match best {
                None => true,
                Some((_, bs, bf)) => s > bs + 1e-6 || ((s - bs).abs() <= 1e-6 && far > bf),
            };
            if better {
                best = Some((spot, s, far));
            }
        }
    }
    best.map_or(target, |b| b.0)
}

// ===================== 小工具 =====================

fn alive_at(sim: &StableSim<'_>, id: usize) -> Option<(f64, f64)> {
    let e = sim.get_entity(id)?;
    if !e.is_alive() {
        return None;
    }
    let (x, y) = e.pos();
    Some((x as f64, y as f64))
}

fn input_pos(input: &InputTargetV1) -> Option<(f64, f64)> {
    (input.kind == InputTargetKindV1::Pos.code()).then_some((input.x as f64, input.y as f64))
}

fn upos(p: (f64, f64)) -> (u64, u64) {
    (p.0.round().max(0.0) as u64, p.1.round().max(0.0) as u64)
}

/// 敌人（活着、能被选中、不是塔）：(id, 位置, 是不是英雄)。
fn foes_of(sim: &StableSim<'_>, team: usize) -> Vec<(usize, Foe)> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if u.team() == team || !u.is_alive() || !u.is_targetable() || u.is_tower() {
            continue;
        }
        let (x, y) = u.pos();
        out.push((u.id(), Foe { at: (x as f64, y as f64), champion: u.is_champion() }));
    }
    out
}

fn queue(sim: &mut StableSim<'_>, stage: &str, caster: usize, input: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{stage}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
}

// ===================== 三步 =====================

/// 出手那一 tick（主包 R 的 `r_at`）：挑落点，酒桶飞过去。
fn cask(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let Some(me) = alive_at(sim, caster) else { return };
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let foes = foes_of(sim, team);
    let list: Vec<Foe> = foes.iter().map(|f| f.1).collect();
    let target = (input.kind == InputTargetKindV1::Target.code())
        .then(|| alive_at(sim, input.target_id))
        .flatten()
        .or_else(|| input_pos(&input))
        .or_else(|| list.iter().filter(|f| f.champion).map(|f| f.at).min_by(|a, b| dist(me, *a).total_cmp(&dist(me, *b))));
    let Some(target) = target else {
        wlog(format!("{} cask: no target in the input (kind {})", head(sim, caster), input.kind));
        return;
    };
    let spot = best_spot(me, target, &list);
    let (x, y) = upos(me);
    let (tx, ty) = upos(spot);
    let d = dist(me, spot);
    let spec = ProjectileSpawnV1 {
        caster_id: caster,
        team,
        x,
        y,
        radius: 1_000,
        speed: (d / R_FLY as f64).ceil().max(1.0) as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: tx,
        target_y: ty,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::EnemyWithoutTower.code(),
    };
    let flew = sim.spawn_projectile(&gr("r_cask"), &format!("{ID}:pass"), &spec);
    let hit = list.iter().filter(|f| dist(f.at, spot) <= R_R + BODY).count();
    let champs = list.iter().filter(|f| f.champion && dist(f.at, spot) <= R_R + BODY).count();
    wlog(format!(
        "{} CASK at {} (target {}, {:.0} behind it, {:.0} from him): {} enemies in reach, {} champions{}",
        head(sim, caster),
        pt(spot),
        pt(target),
        dist(target, spot),
        d,
        hit,
        champs,
        if flew { "" } else { " (spawn_projectile refused: no flying cask)" }
    ));
    queue(sim, "boom", caster, InputTargetV1::pos(tx, ty), R_FLY);
}

/// 酒桶飞过的单位：什么都不做（伤害在落点）。
fn pass(_: &mut StableSim<'_>, _: usize, _: InputTargetV1) {}

/// 落地爆炸：魔法伤害，拽向古拉加斯。
fn boom(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    let Some(spot) = input_pos(&input) else { return };
    if alive_at(sim, caster).is_none() {
        wlog(format!("{} boom: he is dead, no blast", head(sim, caster)));
        return;
    }
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let ap = sim.get_entity(caster).map_or(0, |e| e.stat().magic_power);
    let amount = R_DMG + R_RATIO * ap / 100;
    sim.play_view_effect(&gr("r_boom"), caster, &input, 0, 0, 0);
    sim.play_sfx(&gr("r_boom"), caster, &input);
    let mut n = (0, 0);
    for (id, f) in foes_of(sim, team) {
        if dist(f.at, spot) > R_R + BODY {
            continue;
        }
        sim.deal_damage(caster, id, 0, amount, AttackTypeV1::Skill);
        sim.entity_grab(caster, id, R_GRAB, R_GRAB_T);
        sim.play_view_effect(&gr("r_hit"), caster, &InputTargetV1::target(id), 0, 0, 0);
        n.0 += 1;
        if f.champion {
            n.1 += 1;
        }
    }
    wlog(format!("{} BOOM at {}: {} enemies hit ({} champions), {} magic each, flung toward him", head(sim, caster), pt(spot), n.0, n.1, amount));
}

// ===================== 注册 =====================

#[derive(Clone, Copy)]
enum Step {
    Cask,
    Pass,
    Boom,
}

struct Stage(Step);

impl StableEffectType for Stage {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        match self.0 {
            Step::Cask => cask(sim, caster, input),
            Step::Pass => pass(sim, caster, input),
            Step::Boom => boom(sim, caster, input),
        }
    }
}

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Gragas's Explosive Cask lands behind the enemies it flings the most of) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:cask"), Stage(Step::Cask));
    module.add_native_effect(format!("{ID}:pass"), Stage(Step::Pass));
    module.add_native_effect(format!("{ID}:boom"), Stage(Step::Boom));
    host.log(LogLevel::Info, "league_gragas v1 loaded (Gragas's Explosive Cask aims behind the enemies).");
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

    fn champ(x: f64, y: f64) -> Foe {
        Foe { at: (x, y), champion: true }
    }

    fn minion(x: f64, y: f64) -> Foe {
        Foe { at: (x, y), champion: false }
    }

    #[test]
    fn a_lone_target_gets_the_cask_behind_it() {
        let me = (0.0, 0.0);
        let t = (40_000.0, 0.0);
        let s = best_spot(me, t, &[champ(t.0, t.1)]);
        assert!((s.1).abs() < 1.0, "{s:?}");
        assert!(s.0 > t.0 + 1.0 && dist(s, t) <= R_R + BODY, "the spot {s:?} is not behind the target in reach");
    }

    #[test]
    fn the_spot_catches_the_back_line_too() {
        let me = (0.0, 0.0);
        // the front liner the AI aimed at, and a carry 30000 behind it
        let front = champ(40_000.0, 0.0);
        let carry = champ(70_000.0, 2_000.0);
        let s = best_spot(me, front.at, &[front, carry]);
        assert!(dist(s, front.at) <= R_R + BODY && dist(s, carry.at) <= R_R + BODY, "{s:?} misses one of them");
    }

    #[test]
    fn champions_count_more_than_a_wave() {
        let me = (0.0, 0.0);
        let lone = champ(30_000.0, 30_000.0);
        let wave: Vec<Foe> = (0..6).map(|k| minion(50_000.0 + k as f64 * 2_000.0, -30_000.0)).collect();
        let mut foes = wave.clone();
        foes.push(lone);
        let s = best_spot(me, lone.at, &foes);
        assert!(dist(s, lone.at) <= R_R + BODY, "{s:?} left the champion for the wave");
    }

    #[test]
    fn never_past_the_reach() {
        let me = (0.0, 0.0);
        let t = (R_RANGE, 0.0);
        let s = best_spot(me, t, &[champ(t.0, t.1)]);
        assert!(dist(me, s) <= REACH + 1.0);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_gragas.py");
        let src = std::fs::read_to_string(path).expect("build_gragas.py");
        for (key, v) in [("r_range", R_RANGE as usize), ("r_r", R_R as usize), ("r_dmg", R_DMG), ("r_ratio", R_RATIO),
                         ("r_fly", R_FLY), ("r_grab", R_GRAB), ("r_grab_t", R_GRAB_T)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_gragas.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["r_cask", "r_boom", "r_hit"] {
            assert!(gr(x).len() <= BUFF_NAME_CAP);
        }
    }
}
