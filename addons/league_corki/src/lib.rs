//! 库奇附加包：火箭的智能瞄准、瓦尔基里俯冲的脱身方向（用户选的附加包：「要：智能火箭 + 脱身方向」）。
//!
//! 主包是纯数据：R 的火箭朝 AI 选的英雄直线飞、停在第一个敌人身上爆炸（Q 炸到人时改打「刚被打过的英雄」）；W 的后撤
//! 只能「正对着身边那个英雄往后跳」，不看墙、不看塔、不看队友。`mod.override_info` 把主包的库奇换成 `override/` 里的副本
//! （tools/kit/build_corki.py 的 native=1）：数据和主包一样，只是火箭出手、俯冲起飞那一 tick 改调本包的原生效果。
//!
//! - `aim`（普通火箭）/ `big`（每第 3 发的大火箭，主包的计数照旧）：读所有敌人的位置和血量，对射程内每个敌方英雄试一条
//!   线：火箭停在线上第一个敌人身上（线宽 `R_W` + 身体），按那里爆炸炸得到的敌人打分——英雄 `CHAMP_SCORE`、残血多加
//!   （`LOW_SCORE` x 少掉的血，大火箭 `BIG_LOW_SCORE`：大火箭优先砸残血），小兵和野怪 `UNIT_SCORE`；取分最高的线。
//!   火箭（主包的 `r_missile` / `r_big_missile` 画面）沿直线飞过去，到了那一 tick 排一个 `boom` / `big_boom`。
//! - `boom` / `big_boom`：落点播主包的爆炸画面和音效；`R_R`（大火箭 `R_BIG_R`）内每个敌人（塔除外）受到
//!   `R_DMG` + `R_AP`% 法强魔法、`R_AD`% 攻击力物理伤害（大火箭 x `R_BIG`%），走引擎的伤害流程。他死了就不炸。
//! - `escape`（瓦尔基里俯冲）/ `package`（弹药包）：24 个方向里找落点——路上没墙、在地图里、能飞满 `W_SPEED` x `W_TICK`
//!   （弹药包 `PK_SPEED` x `PK_TICK`）的点，按「离最近的敌方英雄多远」打分，朝队友的方向加分（`ALLY_SCORE`），落在敌方塔
//!   `TOWER_R` 内扣分；然后用强制位移（`ForceMove`）把他送过去。主包的火焰带照常每隔几 tick 落在他身后。
//!
//! 数字和主包 P 表的值写在这里（`R_*`、`W_*`、`PK_*`），主包改了这里一起改（`tests::the_numbers_match_the_kit` 读主包的
//! 参数表核对）。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_corki.log`，每次启动游戏重写。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod maps;

const ID: &str = "league_corki";

/// 主包库奇的名字（画面、音效都以它开头）。
fn ck(x: &str) -> String {
    format!("league_corki_{x}")
}

// ===================== 数值（主包 build_corki.P） =====================

/// 火箭射程（r_range）、速度（r_speed）、线宽（r_w）、爆炸半径（r_r / r_big_r）、伤害（r_dmg + r_ap% 法强、r_ad% 攻击力，
/// 大火箭 r_big%）。
pub const R_RANGE: f64 = 84_000.0;
pub const R_SPEED: f64 = 6_000.0;
pub const R_W: f64 = 3_000.0;
pub const R_R: f64 = 13_000.0;
pub const R_BIG_R: f64 = 20_000.0;
pub const R_DMG: usize = 55;
pub const R_AP: usize = 30;
pub const R_AD: usize = 40;
pub const R_BIG: usize = 200;
/// 瓦尔基里俯冲（w_speed x w_tick）和弹药包（pk_speed x pk_tick）。
pub const W_SPEED: f64 = 4_500.0;
pub const W_TICK: usize = 9;
pub const PK_SPEED: f64 = 5_000.0;
pub const PK_TICK: usize = 13;
/// 敌人的身体半径（线宽、爆炸半径都算到身体边上）。
pub const BODY: f64 = 6_000.0;
/// 打分：每个英雄、残血（少掉的血的比例 x 分）、大火箭的残血分、每个小兵或野怪。
pub const CHAMP_SCORE: f64 = 10.0;
pub const LOW_SCORE: f64 = 4.0;
pub const BIG_LOW_SCORE: f64 = 12.0;
pub const UNIT_SCORE: f64 = 0.5;
/// 脱身：朝队友方向的加分（每 10000 离敌人的距离算 1 分）、敌方塔的范围和扣分、地图大小。
pub const ALLY_SCORE: f64 = 1.5;
pub const TOWER_R: f64 = 60_000.0;
pub const TOWER_SCORE: f64 = 6.0;
pub const MAP: f64 = 960_000.0;
const CELL: f64 = 32_000.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_CORKI_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_corki.log");
        }
    }
    PathBuf::from("league_corki.log")
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

// ===================== 几何 =====================

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn unit(v: (f64, f64)) -> Option<(f64, f64)> {
    let l = (v.0 * v.0 + v.1 * v.1).sqrt();
    (l > 1.0).then_some((v.0 / l, v.1 / l))
}

/// 5v5 的碰撞墙：`MOBA[y]` 第 x 个字符是 `#` 为墙，每格 32000；地图外也算墙。
pub fn is_wall(x: f64, y: f64) -> bool {
    if x < 0.0 || y < 0.0 || x >= MAP || y >= MAP {
        return true;
    }
    let (cx, cy) = ((x / CELL) as usize, (y / CELL) as usize);
    maps::MOBA.get(cy).and_then(|row| row.as_bytes().get(cx)).is_none_or(|c| *c == b'#')
}

/// 一个敌人：位置、是不是英雄、血量比例（0..1）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Foe {
    pub at: (f64, f64),
    pub champion: bool,
    pub hp: f64,
}

/// 从 `me` 朝 `aim` 的火箭停在哪：线上（宽 R_W + 身体）离他最近的敌人；没人就在射程尽头。
pub fn stop_at(me: (f64, f64), aim: (f64, f64), foes: &[Foe]) -> (f64, f64) {
    let Some(u) = unit((aim.0 - me.0, aim.1 - me.1)) else { return aim };
    let reach = R_RANGE + 10_000.0;
    foes.iter()
        .filter_map(|f| {
            let v = (f.at.0 - me.0, f.at.1 - me.1);
            let along = v.0 * u.0 + v.1 * u.1;
            let off = (v.0 * u.1 - v.1 * u.0).abs();
            (along > 0.0 && along <= reach && off <= R_W + BODY).then_some((along, f.at))
        })
        .min_by(|a, b| a.0.total_cmp(&b.0))
        .map_or((me.0 + u.0 * reach, me.1 + u.1 * reach), |x| x.1)
}

/// 在 `spot` 爆炸（半径 `r`）的分数；`low` 是残血的分。
pub fn blast_score(spot: (f64, f64), r: f64, low: f64, foes: &[Foe]) -> f64 {
    foes.iter()
        .filter(|f| dist(f.at, spot) <= r + BODY)
        .map(|f| if f.champion { CHAMP_SCORE + low * (1.0 - f.hp).clamp(0.0, 1.0) } else { UNIT_SCORE })
        .sum()
}

/// 最好的一发：对射程内每个敌方英雄（和大招的目标）试一条线，火箭停下的地方爆炸分最高的。返回（瞄准点，停下的点，分）。
pub fn best_shot(me: (f64, f64), target: Option<(f64, f64)>, foes: &[Foe], big: bool) -> Option<((f64, f64), (f64, f64), f64)> {
    let (r, low) = if big { (R_BIG_R, BIG_LOW_SCORE) } else { (R_R, LOW_SCORE) };
    let aims = target.into_iter().chain(foes.iter().filter(|f| f.champion && dist(me, f.at) <= R_RANGE).map(|f| f.at));
    let mut best: Option<((f64, f64), (f64, f64), f64)> = None;
    for aim in aims {
        let stop = stop_at(me, aim, foes);
        let s = blast_score(stop, r, low, foes);
        if best.is_none_or(|b| s > b.2 + 1e-6) {
            best = Some((aim, stop, s));
        }
    }
    best
}

/// 俯冲的落点：24 个方向里路上没墙、能飞满 `reach` 的点，离最近的敌方英雄越远越好，朝队友（`allies` 的重心）加分，
/// 落在敌方塔范围里扣分。都不行就返回 None（主包的数据方向不变：调用方背对 `from` 跳）。
pub fn escape_spot(me: (f64, f64), reach: f64, foes: &[(f64, f64)], allies: &[(f64, f64)], towers: &[(f64, f64)],
                   walls: bool) -> Option<(f64, f64)> {
    let nearest = |p: (f64, f64)| foes.iter().map(|f| dist(p, *f)).fold(f64::INFINITY, f64::min);
    let toward = if allies.is_empty() {
        None
    } else {
        let n = allies.len() as f64;
        unit((allies.iter().map(|a| a.0).sum::<f64>() / n - me.0, allies.iter().map(|a| a.1).sum::<f64>() / n - me.1))
    };
    let steps = (reach / 1_000.0).ceil().max(1.0) as usize;
    (0..24)
        .filter_map(|k| {
            let a = k as f64 * std::f64::consts::TAU / 24.0;
            let d = (a.cos(), a.sin());
            let free = (1..=steps).all(|i| {
                let f = reach * i as f64 / steps as f64;
                let p = (me.0 + d.0 * f, me.1 + d.1 * f);
                p.0 >= 0.0 && p.1 >= 0.0 && p.0 < MAP && p.1 < MAP && !(walls && is_wall(p.0, p.1))
            });
            if !free {
                return None;
            }
            let w = (me.0 + d.0 * reach, me.1 + d.1 * reach);
            let mut s = nearest(w).min(200_000.0) / 10_000.0;
            if let Some(t) = toward {
                s += ALLY_SCORE * (d.0 * t.0 + d.1 * t.1);
            }
            if towers.iter().any(|t| dist(*t, w) <= TOWER_R) {
                s -= TOWER_SCORE;
            }
            Some((s, w))
        })
        .max_by(|a, b| a.0.total_cmp(&b.0))
        .map(|x| x.1)
}

// ===================== 模拟里的小工具 =====================

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

fn input_unit(sim: &StableSim<'_>, input: &InputTargetV1) -> Option<(f64, f64)> {
    (input.kind == InputTargetKindV1::Target.code()).then(|| alive_at(sim, input.target_id)).flatten()
}

fn upos(p: (f64, f64)) -> (u64, u64) {
    (p.0.round().clamp(0.0, MAP - 1.0) as u64, p.1.round().clamp(0.0, MAP - 1.0) as u64)
}

/// 场上的单位：敌人（活着、能选中、不是塔）、己方英雄（不含他）、敌方的塔，和这张图能不能用 5v5 的墙。
struct Field {
    foes: Vec<(usize, Foe)>,
    allies: Vec<(f64, f64)>,
    towers: Vec<(f64, f64)>,
    walls: bool,
}

fn field(sim: &StableSim<'_>, me: usize, team: usize) -> Field {
    let mut out = Field { foes: Vec::new(), allies: Vec::new(), towers: Vec::new(), walls: true };
    for i in 0..sim.entity_count() {
        let Some(u) = sim.entity_at(i) else { continue };
        if !u.is_alive() {
            continue;
        }
        let (x, y) = u.pos();
        let at = (x as f64, y as f64);
        if is_wall(at.0, at.1) {
            out.walls = false;
        }
        if u.team() == team {
            if u.is_champion() && u.id() != me {
                out.allies.push(at);
            }
            continue;
        }
        if u.is_tower() {
            out.towers.push(at);
            continue;
        }
        if !u.is_targetable() {
            continue;
        }
        let (now, max) = u.hp();
        let hp = if max > 0 { now as f64 / max as f64 } else { 1.0 };
        out.foes.push((u.id(), Foe { at, champion: u.is_champion(), hp }));
    }
    out
}

fn queue(sim: &mut StableSim<'_>, stage: &str, caster: usize, input: InputTargetV1, delay: usize) {
    let name = format!("{ID}:{stage}");
    if !sim.queue_effect(&name, AttackTypeV1::Skill, caster, &input, delay.max(1)) {
        wlog(format!("{} queue_effect({name}) refused", head(sim, caster)));
    }
}

// ===================== 火箭 =====================

/// 出手那一 tick（主包 R 的 `r_at`）：挑一条线，火箭飞过去，到了那一 tick 爆炸。
fn shoot(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1, big: bool) {
    let Some(me) = alive_at(sim, caster) else { return };
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let f = field(sim, caster, team);
    let list: Vec<Foe> = f.foes.iter().map(|x| x.1).collect();
    let target = input_unit(sim, &input).or_else(|| input_pos(&input));
    let Some((aim, stop, score)) = best_shot(me, target, &list, big) else {
        wlog(format!("{} {}: nobody to aim at (input kind {})", head(sim, caster), if big { "BIG" } else { "AIM" }, input.kind));
        return;
    };
    let (x, y) = upos(me);
    let (tx, ty) = upos(stop);
    let d = dist(me, stop);
    let spec = ProjectileSpawnV1 {
        caster_id: caster,
        team,
        x,
        y,
        radius: 1_000,
        speed: R_SPEED as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: tx,
        target_y: ty,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::EnemyWithoutTower.code(),
    };
    let (pic, sound, stage) = if big { ("r_big_missile", "r_big", "big_boom") } else { ("r_missile", "r", "boom") };
    sim.play_sfx(&ck(sound), caster, &InputTargetV1::target(caster));
    let flew = sim.spawn_projectile(&ck(pic), &format!("{ID}:pass"), &spec);
    let ticks = (d / R_SPEED).ceil().max(1.0) as usize;
    wlog(format!(
        "{} {} aim {} -> stops at {} ({:.0} away, {} ticks), score {:.1}{}",
        head(sim, caster),
        if big { "BIG" } else { "AIM" },
        pt(aim),
        pt(stop),
        d,
        ticks,
        score,
        if flew { "" } else { " (spawn_projectile refused: no flying missile)" }
    ));
    queue(sim, stage, caster, InputTargetV1::pos(tx, ty), ticks);
}

/// 火箭飞过的单位：什么都不做（伤害在停下的地方）。
fn pass(_: &mut StableSim<'_>, _: usize, _: InputTargetV1) {}

/// 爆炸：魔法 + 物理伤害。
fn boom(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1, big: bool) {
    let Some(spot) = input_pos(&input) else { return };
    if alive_at(sim, caster).is_none() {
        wlog(format!("{} boom: he is dead, no blast", head(sim, caster)));
        return;
    }
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let stat = sim.get_entity(caster).map(|e| e.stat()).unwrap_or_default();
    let mult = if big { R_BIG } else { 100 };
    let magic = (R_DMG + R_AP * stat.magic_power / 100) * mult / 100;
    let phys = R_AD * stat.attack / 100 * mult / 100;
    let (r, k) = if big { (R_BIG_R, "r_big") } else { (R_R, "r") };
    sim.play_view_effect(&ck(&format!("{k}_boom")), caster, &input, 0, 0, 0);
    sim.play_sfx(&ck(&format!("{k}_boom")), caster, &input);
    let mut n = (0, 0);
    for (id, f) in field(sim, caster, team).foes {
        if dist(f.at, spot) > r + BODY {
            continue;
        }
        sim.deal_damage(caster, id, phys, magic, AttackTypeV1::Skill);
        sim.play_view_effect(&ck("r_hit"), caster, &InputTargetV1::target(id), 0, 0, 0);
        n.0 += 1;
        if f.champion {
            n.1 += 1;
        }
    }
    wlog(format!("{} {} at {}: {} enemies hit ({} champions), {} magic + {} physical each", head(sim, caster),
                 if big { "BIG BOOM" } else { "BOOM" }, pt(spot), n.0, n.1, magic, phys));
}

// ===================== 俯冲 =====================

/// 起飞那一 tick（主包 W 的 `w_at`）：挑落点，强制位移送他过去；挑不到就背对身边那个英雄（主包的方向）。
fn fly(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1, package: bool) {
    let Some(me) = alive_at(sim, caster) else { return };
    let team = sim.get_entity(caster).map_or(0, |e| e.team());
    let f = field(sim, caster, team);
    let (speed, ticks) = if package { (PK_SPEED, PK_TICK) } else { (W_SPEED, W_TICK) };
    let reach = speed * ticks as f64;
    let champs: Vec<(f64, f64)> = f.foes.iter().filter(|x| x.1.champion).map(|x| x.1.at).collect();
    let from = input_unit(sim, &input).or_else(|| input_pos(&input));
    let spot = escape_spot(me, reach, &champs, &f.allies, &f.towers, f.walls).or_else(|| {
        let u = unit((me.0 - from?.0, me.1 - from?.1))?;
        Some((me.0 + u.0 * reach, me.1 + u.1 * reach))
    });
    let Some(spot) = spot else {
        wlog(format!("{} {}: no way out", head(sim, caster), if package { "PACKAGE" } else { "ESCAPE" }));
        return;
    };
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
    cc.dx = (spot.0 - me.0).round() as i64;
    cc.dy = (spot.1 - me.1).round() as i64;
    cc.speed = speed.ceil() as u64;
    sim.apply_cc(caster, &cc);
    let near = champs.iter().map(|c| dist(spot, *c)).fold(f64::INFINITY, f64::min);
    wlog(format!(
        "{} {} from {} to {} ({:.0}), nearest enemy champion then {:.0} (now {:.0}), {} allies, walls {}",
        head(sim, caster),
        if package { "PACKAGE" } else { "ESCAPE" },
        pt(me),
        pt(spot),
        reach,
        near,
        champs.iter().map(|c| dist(me, *c)).fold(f64::INFINITY, f64::min),
        f.allies.len(),
        f.walls
    ));
}

// ===================== 注册 =====================

#[derive(Clone, Copy)]
enum Step {
    Aim,
    Big,
    Pass,
    Boom,
    BigBoom,
    Escape,
    Package,
}

struct Stage(Step);

impl StableEffectType for Stage {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        match self.0 {
            Step::Aim => shoot(sim, caster, input, false),
            Step::Big => shoot(sim, caster, input, true),
            Step::Pass => pass(sim, caster, input),
            Step::Boom => boom(sim, caster, input, false),
            Step::BigBoom => boom(sim, caster, input, true),
            Step::Escape => fly(sim, caster, input, false),
            Step::Package => fly(sim, caster, input, true),
        }
    }
}

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Corki's missiles aimed at the best blast, Valkyrie flies away from danger) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    for (name, step) in [("aim", Step::Aim), ("big", Step::Big), ("pass", Step::Pass), ("boom", Step::Boom),
                         ("big_boom", Step::BigBoom), ("escape", Step::Escape), ("package", Step::Package)] {
        module.add_native_effect(format!("{ID}:{name}"), Stage(step));
    }
    host.log(LogLevel::Info, "league_corki v1 loaded (Corki's missiles aim, Valkyrie escapes).");
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

    fn champ(x: f64, y: f64, hp: f64) -> Foe {
        Foe { at: (x, y), champion: true, hp }
    }

    fn minion(x: f64, y: f64) -> Foe {
        Foe { at: (x, y), champion: false, hp: 1.0 }
    }

    #[test]
    fn the_missile_stops_on_the_first_enemy() {
        let me = (0.0, 0.0);
        let foes = [minion(30_000.0, 2_000.0), champ(60_000.0, 0.0, 1.0)];
        assert_eq!(stop_at(me, (60_000.0, 0.0), &foes), (30_000.0, 2_000.0));
    }

    #[test]
    fn a_clear_line_is_picked_over_a_blocked_one() {
        let me = (0.0, 0.0);
        // a champion behind a minion, another in the open
        let foes = [minion(25_000.0, 0.0), champ(60_000.0, 0.0, 1.0), champ(0.0, 60_000.0, 1.0)];
        let (aim, stop, _) = best_shot(me, Some((60_000.0, 0.0)), &foes, false).unwrap();
        assert_eq!(aim, (0.0, 60_000.0));
        assert_eq!(stop, (0.0, 60_000.0));
    }

    #[test]
    fn the_big_one_goes_for_the_low_champion() {
        let me = (0.0, 0.0);
        let foes = [champ(60_000.0, 0.0, 1.0), champ(0.0, 60_000.0, 0.2)];
        let (aim, _, _) = best_shot(me, Some((60_000.0, 0.0)), &foes, true).unwrap();
        assert_eq!(aim, (0.0, 60_000.0));
    }

    #[test]
    fn two_champions_together_beat_one_alone() {
        let me = (0.0, 0.0);
        let foes = [champ(60_000.0, 0.0, 1.0), champ(0.0, 60_000.0, 1.0), champ(4_000.0, 66_000.0, 1.0)];
        let (_, stop, _) = best_shot(me, Some((60_000.0, 0.0)), &foes, false).unwrap();
        assert!(dist(stop, (0.0, 60_000.0)) < 1.0, "{stop:?}");
    }

    #[test]
    fn he_flies_away_from_the_enemy() {
        let me = (480_000.0, 480_000.0);
        let enemy = (500_000.0, 480_000.0);
        let w = escape_spot(me, W_SPEED * W_TICK as f64, &[enemy], &[], &[], false).unwrap();
        assert!(w.0 < me.0 - 30_000.0, "{w:?}");
    }

    #[test]
    fn he_leans_toward_his_team() {
        let me = (480_000.0, 480_000.0);
        let enemy = (500_000.0, 480_000.0);
        let ally = (400_000.0, 400_000.0);
        let w = escape_spot(me, W_SPEED * W_TICK as f64, &[enemy], &[ally], &[], false).unwrap();
        assert!(w.1 < me.1, "{w:?} not toward the ally");
    }

    #[test]
    fn he_keeps_off_enemy_towers() {
        let me = (480_000.0, 480_000.0);
        let enemy = (500_000.0, 480_000.0);
        let tower = (440_000.0, 480_000.0);
        let w = escape_spot(me, W_SPEED * W_TICK as f64, &[enemy], &[], &[tower], false).unwrap();
        assert!(dist(w, tower) > TOWER_R, "{w:?} lands under the tower");
    }

    #[test]
    fn never_off_the_map() {
        let me = (5_000.0, 5_000.0);
        let enemy = (30_000.0, 30_000.0);
        let w = escape_spot(me, PK_SPEED * PK_TICK as f64, &[enemy], &[], &[], false).unwrap();
        assert!(w.0 >= 0.0 && w.1 >= 0.0 && w.0 < MAP && w.1 < MAP, "{w:?}");
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_corki.py");
        let src = std::fs::read_to_string(path).expect("build_corki.py");
        for (key, v) in [("r_range", R_RANGE as usize), ("r_speed", R_SPEED as usize), ("r_w", R_W as usize),
                         ("r_r", R_R as usize), ("r_big_r", R_BIG_R as usize), ("r_dmg", R_DMG), ("r_ap", R_AP),
                         ("r_ad", R_AD), ("r_big", R_BIG), ("w_speed", W_SPEED as usize), ("w_tick", W_TICK),
                         ("pk_speed", PK_SPEED as usize), ("pk_tick", PK_TICK)] {
            assert!(src.contains(&format!("\"{key}\": {v},")), "{key} is not {v} in build_corki.P");
        }
    }

    #[test]
    fn the_names_fit() {
        for x in ["r_missile", "r_big_missile", "r_big_boom", "r_boom", "r_hit"] {
            assert!(ck(x).len() <= BUFF_NAME_CAP);
        }
    }
}
