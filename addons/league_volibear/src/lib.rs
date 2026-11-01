//! 沃利贝尔附加包（用户 2026-10-19：「上单，方案 A，做附加包」）。主包保持纯数据；`mod.override_info` 把主包的沃利贝尔换成
//! `override/` 里的副本（`make_override.py` 用 tools/kit/build_volibear.py 的 `native=1` 生成：技能、时机一字不改，只有下面几处换成
//! 本包的原生效果），本包补数据做不到的三件事（英雄联盟的规则）：
//!
//! - **狂雷渐起的闪电跳到最近的 4 个敌人**（原生效果 `league_volibear:storm`，满 5 层的攻击打出时）：目标和离目标最近的
//!   `P_N` 个敌人（`P_R` 以内，防御塔不算）各受 `P_DMG` + `P_AP`% 法强魔法伤害，身上闪一下（`league_volibear_p_zap`）。主包：
//!   一道飞向目标的闪电，路上和目标身边 `P_R` 以内的敌人都被打到。
//! - **暴怒撕咬认准被标记的那个人**（原生效果 `league_volibear:maul`，撕咬咬中英雄时）：他身上没有本次的标记就标记他
//!   （`league_volibear_w_mark`，`W_MARK_T` tick）；有就是第二口：多造成撕咬的 `W2`% 物理伤害，回复 `W_HEAL` + `W_HEAL_AD`%
//!   攻击力 + 已损失生命的 `W_HEAL_MISS`%，标记去掉。主包：标记记在沃利贝尔自己身上（咬谁都算），回复固定值 + 攻击力加成。
//! - **天声震落让防御塔失效**（原生效果 `league_volibear:stormbringer`，落地砸地时）：落点 `R_TOWER_R` 以内的敌方防御塔
//!   `R_TOWER_T` tick 不能攻击（眩晕 + 禁止攻击，塔身上缠着电光 `league_volibear_r_tower`）。主包：没有这一条。
//! - **风暴形态变成雷电蓝**（0.2.0，用户 2026-10-30：「沃利贝尔开大是不是得搞个变色啊」→「2 雷电蓝+描边」，view.rs）：落地后的
//!   12 秒（主包的 buff `R_FORM`）他的每个动作都换成图里雷电蓝、电蓝外描边的 `r_*` 一套。主包：颜色不变，只有身后的雷云。
//!   （体型变大 35% 是主包 league.dll 画的，装不装本包都有：addons/league_main/src/hd.rs FORMS。）
//! - **天声震落跳进人堆**（0.3.0，用户 2026-11-01：「沃利贝尔现在的大招是跳进去开的吗 人群中」，AI 钩子 `league_volibear:leap`）：
//!   英雄联盟的 R 是指定地点，往人堆里跳；主包的 R 只能指定一个敌方英雄，游戏的 AI 挑谁就跳谁。AI 按下 R 时，`R_RANGE` 以内
//!   要是有落在他身上能砸到更多敌方英雄（他身边 `R_R` 以内，含他自己）的，改跳他；一样多照 AI 挑的。什么时候按还是 AI 定。
//!
//! 数字是主包参数表 P 的同名项（小写）；`make_override.py` 生成副本时核对，不一致就停。本包不自己按技能键：AI 按下的 R 只换个目标。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_volibear.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! `STORM`（闪电打到谁）、`MAUL`（标记 / 第二口回了多少）、`TOWER`（哪座塔失效）、`FORM`（画面上换成风暴形态的颜色）、
//! `LEAP`（AI 的 R 改跳了谁、照旧跳谁，各砸到几个敌方英雄），限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_volibear";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.3.0";
/// 天声震落落地后的风暴形态（主包数据的 buff，12 秒）：这期间画面上是雷电蓝的他（view.rs）。
pub const R_FORM: &str = "league_volibear_r_form";

/// 狂雷渐起：闪电伤害（固定、法强 %）、离目标多远以内、除目标外最多几个。
pub const P_DMG: usize = 30;
pub const P_AP: usize = 40;
pub const P_R: usize = 22_000;
pub const P_N: usize = 4;
/// 暴怒撕咬：撕咬的伤害（固定、攻击力 % 另加、最大生命 %）、第二口多出的 %、标记 tick、回复（固定、攻击力 %、已损失生命 %）。
pub const W_DMG: usize = 30;
pub const W_RATIO: usize = 40;
pub const W_HP: usize = 2;
pub const W2: usize = 50;
pub const W_MARK_T: usize = 480;
pub const W_HEAL: usize = 40;
pub const W_HEAL_AD: usize = 50;
pub const W_HEAL_MISS: usize = 12;
/// 天声震落：多远以内的敌方塔、失效多少 tick。
pub const R_TOWER_R: usize = 55_000;
pub const R_TOWER_T: usize = 240;
/// 天声震落：射程、落地砸到多远以内（跳进人堆时数人用）。
pub const R_RANGE: usize = 70_000;
pub const R_R: usize = 32_000;
/// 闪电打中时身上的电光（p_hit 一遍的长度）。
pub const ZAP_T: usize = 20;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VOLIBEAR_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_volibear.log");
        }
    }
    PathBuf::from("league_volibear.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
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

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
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

// ===================== 规则（单元测试用） =====================

pub type Pt = (f64, f64);

fn n(name: &str) -> String {
    format!("{ID}_{name}")
}

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 闪电跳给谁：候选（id、位置）里离目标 `at` 在 `reach` 以内的，按远近取前 `count` 个（不含目标自己）。
pub fn nearest(at: Pt, target: usize, candidates: &[(usize, Pt)], reach: f64, count: usize) -> Vec<usize> {
    let mut near: Vec<(f64, usize)> = candidates
        .iter()
        .filter(|(id, _)| *id != target)
        .map(|&(id, p)| (dist(at, p), id))
        .filter(|(d, _)| *d <= reach)
        .collect();
    near.sort_by(|a, b| a.0.total_cmp(&b.0).then(a.1.cmp(&b.1)));
    near.into_iter().take(count).map(|(_, id)| id).collect()
}

/// 天声震落跳谁：`me` 射程 `range` 内的敌方英雄（id、位置）里，落在他身上砸到的敌方英雄（他身边 `radius` 以内，含他）最多的；
/// 一样多时 AI 自己挑的 `ai` 优先，再挑离得近的。返回（目标，砸到几个）。
pub fn crowd_pick(me: Pt, ai: Option<usize>, champs: &[(usize, Pt)], range: f64, radius: f64) -> Option<(usize, usize)> {
    champs
        .iter()
        .filter(|&&(_, p)| dist(me, p) <= range)
        .map(|&(id, p)| (id, in_slam(p, champs, radius), dist(me, p)))
        .max_by(|a, b| a.1.cmp(&b.1).then((Some(a.0) == ai).cmp(&(Some(b.0) == ai))).then(b.2.total_cmp(&a.2)))
        .map(|(id, n, _)| (id, n))
}

/// 落在 `at` 砸到的敌方英雄：`champs` 里 `radius` 以内的个数。
pub fn in_slam(at: Pt, champs: &[(usize, Pt)], radius: f64) -> usize {
    champs.iter().filter(|&&(_, p)| dist(at, p) <= radius).count()
}

/// 第二口的回复：攻击力 `ad`、生命 (`hp`, `max_hp`)。
pub fn maul_heal(ad: usize, hp: usize, max_hp: usize) -> usize {
    W_HEAL + W_HEAL_AD * ad / 100 + W_HEAL_MISS * max_hp.saturating_sub(hp) / 100
}

/// 第二口多出的物理伤害：攻击力 `ad`、他自己的最大生命 `max_hp`（撕咬本身的 W2%）。
pub fn maul_extra(ad: usize, max_hp: usize) -> usize {
    (W_DMG + (100 + W_RATIO) * ad / 100 + W_HP * max_hp / 100) * W2 / 100
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

// ===================== 原生效果 =====================

/// 满层的攻击：闪电打目标和离它最近的 P_N 个敌人。
fn storm(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    let Some(team) = sim.get_entity(me).map(|e| e.team()) else { return };
    let Some(at) = sim.get_entity(target).filter(|e| e.is_alive() && e.is_targetable()).map(|e| (e.pos().0 as f64, e.pos().1 as f64)) else {
        return;
    };
    let foes: Vec<(usize, Pt)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.team() != team && e.is_alive() && e.is_targetable())
        .filter(|e| !matches!(e.kind(), Some(EntityKindV1::Tower) | Some(EntityKindV1::Nexus) | None))
        .map(|e| (e.id(), (e.pos().0 as f64, e.pos().1 as f64)))
        .collect();
    let mut hit = vec![target];
    hit.extend(nearest(at, target, &foes, P_R as f64, P_N));
    let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
    let dmg = P_DMG + P_AP * ap / 100;
    for &id in &hit {
        sim.deal_damage_typed(me, id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        sim.entity_remove_buff(id, &n("p_zap"));
        sim.add_buff(id, &BuffV1::timed(&n("p_zap"), ZAP_T));
    }
    if let Some(k) = counted("storm") {
        wlog(format!("{} STORM on #{target}: {} struck ({hit:?}) for {dmg} magic #{k}", head(sim, me), hit.len()));
    }
}

/// 撕咬咬中英雄：没标记就标记，有标记就是第二口（多伤害 + 回复）。
fn maul(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(target) = target_of(&input) else { return };
    if !sim.get_entity(target).is_some_and(|e| e.is_alive()) {
        return;
    }
    let mark = n("w_mark");
    if !has_buff(sim, target, &mark) {
        sim.add_buff(target, &BuffV1::timed(&mark, W_MARK_T));
        if let Some(k) = counted("mark") {
            wlog(format!("{} MAUL #{target}: marked for {W_MARK_T} ticks #{k}", head(sim, me)));
        }
        return;
    }
    sim.entity_remove_buff(target, &mark);
    let Some((ad, (hp, max_hp))) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| (e.stat().attack, e.hp())) else {
        return;
    };
    let extra = maul_extra(ad, max_hp);
    sim.deal_damage_typed(me, target, extra, DamageTypeV1::Ad, AttackTypeV1::Skill);
    let heal = maul_heal(ad, hp, max_hp);
    sim.heal(me, me, heal);
    sim.add_buff(me, &BuffV1::timed(&n("w_healed"), 30));
    if let Some(k) = counted("maul") {
        wlog(format!("{} MAUL #{target}: the second bite, +{extra} physical, healed {heal} at {hp}/{max_hp} #{k}", head(sim, me)));
    }
}

/// 天声震落落地：附近的敌方塔失效。
fn stormbringer(sim: &mut StableSim<'_>, me: usize, _input: InputTargetV1) {
    let Some((team, at)) = sim.get_entity(me).map(|e| (e.team(), (e.pos().0 as f64, e.pos().1 as f64))) else { return };
    let towers: Vec<usize> = (0..sim.tower_count())
        .map(|i| sim.tower_id_at(i))
        .filter(|&t| sim.get_entity(t).is_some_and(|e| e.is_alive() && e.team() != team))
        .filter(|&t| pos(sim, t).is_some_and(|p| dist(p, at) <= R_TOWER_R as f64))
        .collect();
    for &t in &towers {
        sim.apply_cc(t, &CcV1::stun(R_TOWER_T as u64));
        sim.apply_cc(t, &CcV1::of_kind(CcKindV1::BlockAttack, R_TOWER_T as u64));
        sim.entity_remove_buff(t, &n("r_tower"));
        sim.add_buff(t, &BuffV1::timed(&n("r_tower"), R_TOWER_T));
    }
    if let Some(k) = counted("tower") {
        wlog(format!("{} TOWER landing at ({:.0}, {:.0}): {} enemy towers off for {R_TOWER_T} ticks {towers:?} #{k}",
                     head(sim, me), at.0, at.1, towers.len()));
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== AI 钩子：天声震落跳进人堆 =====================

/// AI 按下天声震落时，改跳射程内落下去砸到敌方英雄最多的那个（`crowd_pick`）；不比 AI 挑的多就不动。
#[derive(Clone, Default)]
struct Leap;

impl StablePlayerAi for Leap {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:leap")
    }

    /// league_ult_press（100）之后。
    fn priority(&self) -> i32 {
        105
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let b = base?;
        if InputKindV1::from_code(b.kind) != Some(InputKindV1::Ult) {
            return None;
        }
        let ai = target_of(&b.target);
        let player = ctx.player_id();
        let (input, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() {
                return None;
            }
            let (my_id, team) = (me.id(), me.team());
            let at = (me.pos().0 as f64, me.pos().1 as f64);
            let champs: Vec<(usize, Pt)> = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .filter(|e| e.team() != team && e.is_alive() && e.is_targetable() && e.is_champion())
                .map(|e| (e.id(), (e.pos().0 as f64, e.pos().1 as f64)))
                .collect();
            let was = ai.and_then(|a| champs.iter().find(|c| c.0 == a)).map_or(0, |&(_, p)| in_slam(p, &champs, R_R as f64));
            let (t, n) = crowd_pick(at, ai, &champs, R_RANGE as f64, R_R as f64)?;
            if Some(t) == ai || n <= was {
                if let Some(k) = counted("leap_kept") {
                    let who = ai.map_or("-".to_string(), |a| format!("#{a}"));
                    wlog(format!("{} LEAP the AI's {who} kept: {was} enemy champions in the slam #{k}", head(&sim, my_id)));
                }
                return None;
            }
            let who = ai.map_or("-".to_string(), |a| format!("#{a}"));
            (InputV1::action(InputKindV1::Ult, InputTargetV1::target(t)),
             format!("{} LEAP at #{t}: {n} enemy champions in the slam (the AI's {who}: {was})", head(&sim, my_id)))
        };
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(k) = counted("leap") {
            wlog(format!("{line} #{k}"));
        }
        Some(input)
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Volibear: chain lightning to the 4 nearest, the second maul by the mark on its target, Stormbringer leaps into the crowd and silences towers, the storm form in electric blue) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:storm"), Step(storm));
    module.add_native_effect(format!("{ID}:maul"), Step(maul));
    module.add_native_effect(format!("{ID}:stormbringer"), Step(stormbringer));
    module.add_player_input_ai(Leap);
    view::install_once();
    host.log(LogLevel::Info, "league_volibear loaded (chain lightning, marked maul, leap into the crowd, tower silence, storm colours).");
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
    fn lightning_jumps_to_the_nearest_four() {
        let at = (0.0, 0.0);
        let c = [(1, at), (2, (5_000.0, 0.0)), (3, (1_000.0, 0.0)), (4, (30_000.0, 0.0)), (5, (8_000.0, 8_000.0)),
                 (6, (0.0, 12_000.0)), (7, (2_000.0, 2_000.0))];
        assert_eq!(nearest(at, 1, &c, 22_000.0, 4), vec![3, 7, 2, 5]);
        assert_eq!(nearest(at, 1, &c, 4_000.0, 4), vec![3, 7]);
        assert!(nearest(at, 1, &[(1, at)], 22_000.0, 4).is_empty());
    }

    #[test]
    fn stormbringer_leaps_into_the_crowd() {
        let (range, r) = (R_RANGE as f64, R_R as f64);
        let me = (0.0, 0.0);
        // the AI's #1 alone in front; #2 with #3 and #4 round him, in range; #5 in a bigger pile out of range
        let c = [(1, (20_000.0, 0.0)), (2, (60_000.0, 0.0)), (3, (75_000.0, 10_000.0)), (4, (60_000.0, -25_000.0)),
                 (5, (120_000.0, 0.0)), (6, (125_000.0, 5_000.0)), (7, (118_000.0, -6_000.0)), (8, (122_000.0, 9_000.0))];
        assert_eq!(in_slam((60_000.0, 0.0), &c, r), 3);
        assert_eq!(crowd_pick(me, Some(1), &c, range, r), Some((2, 3)));
        // two pairs, two in the slam wherever he lands: the AI's pick stays, else the nearest
        let two = [(1, (20_000.0, 0.0)), (2, (20_000.0, 20_000.0)), (3, (60_000.0, -30_000.0)), (4, (60_000.0, -50_000.0))];
        assert_eq!(crowd_pick(me, Some(3), &two, range, r), Some((3, 2)));
        assert_eq!(crowd_pick(me, None, &two, range, r), Some((1, 2)), "a tie and no AI pick: the nearest");
        assert_eq!(crowd_pick(me, Some(1), &[(1, (90_000.0, 0.0))], range, r), None, "nobody in range");
        assert_eq!(crowd_pick(me, Some(9), &[(1, (40_000.0, 0.0))], range, r), Some((1, 1)));
    }

    #[test]
    fn the_second_bite() {
        assert_eq!(maul_heal(100, 1_000, 1_000), W_HEAL + W_HEAL_AD);
        assert_eq!(maul_heal(100, 500, 1_500), W_HEAL + W_HEAL_AD + W_HEAL_MISS * 10);
        assert_eq!(maul_extra(100, 2_000), (W_DMG + 100 + W_RATIO + W_HP * 20) * W2 / 100);
    }

    #[test]
    fn names_fit_a_buff() {
        for s in ["w_mark", "p_zap", "r_tower", "w_healed"] {
            assert!(n(s).len() <= BUFF_NAME_CAP);
        }
        assert_eq!(R_FORM, n("r_form"));
    }

    #[test]
    fn the_copy_uses_the_natives() {
        let copy = include_str!("../override/league_volibear.data_champion");
        for r in ["league_volibear:storm", "league_volibear:maul", "league_volibear:stormbringer"] {
            assert!(copy.contains(r), "the copy never uses {r}");
        }
        assert!(!copy.contains("\"type\": \"TargetSplashProjectile\""), "the copy still splashes in data");
        assert!(copy.contains(&format!("\"{R_FORM}\"")), "the copy no longer gives him {R_FORM}");
    }
}
