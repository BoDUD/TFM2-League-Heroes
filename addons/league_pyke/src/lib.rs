//! 派克附加包：R「涌泉之恨」只砍斩得死的人，斩杀线精确（用户：「大招逻辑也有点问题 总是满血砍人」，
//! 早先：「这个读不到的话就改rust原码」）。
//!
//! 主包保持纯数据：数据读不到当前生命，派克的 R 由 AI 对「队伍刚打过的敌方英雄」放出（满血的也会被砍），
//! X 里的英雄先吃斩杀线 T = `R_DMG` + `R_RATIO`% 攻击力的真实伤害、下一 tick 活下来的回一半——近似「低于 T 处决、
//! 其余掉一半」。`mod.override_info` 把主包的派克换成 `override/` 里的副本，两处不同：
//!
//! - AI 钩子 `league_pyke:ult`：R 只放向射程 `R_RANGE` 内生命不高于 T 的敌方英雄（几个时砍血最少的）。
//!   AI 想对斩不死的人放 R，就改成打他（打不到就走过去）；R 好了、有斩得死的人，AI 没想放也放。副本的 R 改成对
//!   任何敌方英雄可放（`EnemyChampion`），放不放全由钩子定。
//! - 原生效果 `league_pyke:execute`：X 落下时对其中每个敌方英雄读生命——不高于 T 的处决（真实伤害，击杀算派克的），
//!   其余吃 T 的 `SURVIVE`%（同主包落下后的净伤害）。处决的那个 `K_READ` tick 后（`league_pyke:after`）真死了，派克
//!   闪到他倒下的地方、R 刷新（`ult_cooldown_mult` 10000 的 2 tick buff，同主包），播主包的 r_reset 画面、声音和台词。
//!   主包 X 里「真实伤害 + 一 tick 后回一半」和那套击杀检查（`k_r`、闪现、刷新）都由这两步代替：原生的伤害要到这一
//!   tick 结算完才扣，数据的检查当场看人还活着，就把闪现和刷新取消了（用户：「放大招的时候人没过去？」）。
//!
//! 数字是主包 tools/kit/build_pyke.py 参数表 P 的 `r_dmg`、`r_ratio`、`r_range`；`make_override.py` 生成副本时核对
//! 这里的常数和 P 一致，不一致就停。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_pyke.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_pyke";
const HERO: &str = "league_pyke";

/// 斩杀线：`R_DMG` + `R_RATIO`% 攻击力（主包 P 的 r_dmg、r_ratio）。
pub const R_DMG: usize = 180;
pub const R_RATIO: usize = 60;
/// R 的施放距离（主包 P 的 r_range）。
pub const R_RANGE: usize = 75_000;
/// 斩不死的英雄吃斩杀线的这么多 %（主包：T 的真实伤害，再回 T/2）。
pub const SURVIVE: usize = 50;
/// 处决后隔几 tick 看人死没死、闪过去（主包 P 的 k_read）。
pub const K_READ: usize = 4;
/// 同一类日志至少隔这么多 tick 记一次（AI 每 tick 想一次）。
const LOG_EVERY: usize = 120;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_PYKE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_pyke.log");
        }
    }
    PathBuf::from("league_pyke.log")
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

// ===================== 判断 =====================

/// 斩杀线：攻击力 `attack` 时的 T。
pub fn threshold(attack: usize) -> usize {
    R_DMG + attack * R_RATIO / 100
}

/// 斩不死时掉的血。
pub fn survivor_damage(attack: usize) -> usize {
    threshold(attack) * SURVIVE / 100
}

/// 射程内的一个敌方英雄：id、当前生命。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Foe {
    pub id: usize,
    pub hp: usize,
}

/// 斩得死的人里血最少的那个。
pub fn best_kill(foes: &[Foe], t: usize) -> Option<Foe> {
    foes.iter().copied().filter(|f| f.hp <= t).min_by_key(|f| (f.hp, f.id))
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Plan {
    /// 照 AI 原来的输入。
    Keep,
    /// 放 R，砍这个人。
    Ult(usize),
    /// AI 想放 R 砍斩不死的人：改成打他。
    Hold(usize),
}

/// `ult_target`：AI 原来的输入是 R 时它的目标；`ult_ready`：现在放 R 是合法输入。
pub fn plan(ult_target: Option<usize>, foes: &[Foe], t: usize, ult_ready: bool) -> Plan {
    let kill = best_kill(foes, t);
    match (ult_target, kill) {
        (Some(id), _) if foes.iter().any(|f| f.id == id && f.hp <= t) => Plan::Keep,
        (Some(_), Some(k)) => Plan::Ult(k.id),
        // not in reach (walking up to cast, or gone): decided again when he gets there
        (Some(id), None) if !foes.iter().any(|f| f.id == id) => Plan::Keep,
        (Some(id), None) => Plan::Hold(id),
        (None, Some(k)) if ult_ready => Plan::Ult(k.id),
        (None, _) => Plan::Keep,
    }
}

// ===================== AI 钩子 =====================

fn foes_in_reach(sim: &StableSim<'_>, me: usize, team: usize) -> Vec<Foe> {
    let r2 = (R_RANGE as u64).saturating_mul(R_RANGE as u64);
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.is_champion() && e.is_alive() && e.team() != team && sim.distance_sq(me, e.id()) <= r2)
        .map(|e| Foe { id: e.id(), hp: e.hp().0 })
        .collect()
}

#[derive(Clone, Default)]
struct UltAi {
    last_hold: Option<usize>,
    last_cast: Option<(usize, usize)>,
}

impl StablePlayerAi for UltAi {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:ult")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let player = ctx.player_id();
        let tick = ctx.tick();
        let ult_target = base.and_then(|b| {
            (b.kind == InputKindV1::Ult.code() && InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target))
                .then_some(b.target.target_id)
        });
        // AI 在做别的事（走路、回家、放别的技能）时才看要不要主动放 R；攻击和空闲时也看
        let busy = base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Return))
        });
        let (foes, t, line, pos, free) = {
            let sim = ctx.sim()?;
            let pl = sim.get_player(player)?;
            // `is_valid_input` does not look at cooldowns: on cooldown an R order every tick held him still for
            // seconds (the log of 2026-10-06: 230 ticks of "R EXECUTE" with no X)
            let free = pl.level() >= 5 && pl.cooldowns().is_some_and(|c| c.3 == 0);
            let me = pl.champion()?;
            if !me.is_alive() {
                return None;
            }
            let t = threshold(me.stat().attack);
            let foes = foes_in_reach(&sim, me.id(), me.team());
            let pos = |id: usize| sim.get_entity(id).map(|e| e.pos());
            let target_pos = ult_target.and_then(pos);
            (foes, t, head(&sim, me.id()), target_pos, free)
        };
        let ready = free && !busy && best_kill(&foes, t).is_some_and(|k| {
            ctx.is_valid_input(&InputV1::action(InputKindV1::Ult, InputTargetV1::target(k.id)))
        });
        let hp_of = |id: usize| foes.iter().find(|f| f.id == id).map_or(0, |f| f.hp);
        match plan(ult_target, &foes, t, ready) {
            Plan::Keep => None,
            Plan::Ult(id) => {
                let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(id));
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                let why = match ult_target {
                    Some(o) => format!("retargeted from #{o} (hp {})", hp_of(o)),
                    None => "the AI had not cast it".to_string(),
                };
                if self.last_cast.is_none_or(|(t0, i)| i != id || tick >= t0 + LOG_EVERY) {
                    self.last_cast = Some((tick, id));
                    wlog(format!("{line} R EXECUTE #{id}: hp {} <= {t}, {why}", hp_of(id)));
                }
                Some(input)
            }
            Plan::Hold(id) => {
                if self.last_hold.is_none_or(|t0| tick >= t0 + LOG_EVERY) {
                    self.last_hold = Some(tick);
                    wlog(format!("{line} R HELD: #{id} hp {} > {t}, nobody in reach to execute", hp_of(id)));
                }
                let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(id));
                if ctx.is_valid_input(&attack) {
                    return Some(attack);
                }
                let (x, y) = pos.unwrap_or_default();
                Some(InputV1::move_to(x, y))
            }
        }
    }
}

// ===================== 原生效果 =====================

/// X 落在一个敌方英雄身上：不高于斩杀线的处决，其余吃斩杀线的 `SURVIVE`%。
fn execute(sim: &mut StableSim<'_>, caster: usize, input: InputTargetV1) {
    if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
        return;
    }
    let target = input.target_id;
    let Some(atk) = sim.get_entity(caster).map(|e| e.stat().attack) else { return };
    let Some((hp, max)) = sim.get_entity(target).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
    let t = threshold(atk);
    let line = head(sim, caster);
    if hp <= t {
        let (x, y) = sim.get_entity(target).map_or((0, 0), |e| e.pos());
        // 护盾也一起打穿：给足量（这一 tick 结算完才扣）
        sim.deal_damage_typed(caster, target, hp + max, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        let mut mark = BuffV1::timed(&mark_name(target, x, y), K_READ + 2);
        mark.duration_kind = BuffDurationV1::Time.code();
        sim.add_buff(caster, &mark);
        if !sim.queue_effect(&format!("{ID}:after"), AttackTypeV1::Skill, caster, &InputTargetV1::target(caster), K_READ) {
            wlog(format!("{line} queue_effect({ID}:after) refused"));
        }
        wlog(format!("{line} X EXECUTED #{target}: hp {hp}/{max} <= {t}"));
    } else {
        let d = survivor_damage(atk);
        sim.deal_damage_typed(caster, target, d, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        wlog(format!("{line} X hit #{target}: hp {hp}/{max} > {t}, {d} true damage"));
    }
}

/// 处决标记：`league_pyke_rk:<目标>:<x>:<y>`（他倒下的地方；buff 名最多 64 字节）。
pub fn mark_name(target: usize, x: u64, y: u64) -> String {
    format!("{HERO}_rk:{target}:{x}:{y}")
}

pub fn parse_mark(name: &str) -> Option<(usize, u64, u64)> {
    let rest = name.strip_prefix(&format!("{HERO}_rk:"))?;
    let mut it = rest.split(':');
    let (t, x, y) = (it.next()?.parse().ok()?, it.next()?.parse().ok()?, it.next()?.parse().ok()?);
    it.next().is_none().then_some((t, x, y))
}

/// 处决后 `K_READ` tick：真死了的，闪到他倒下的地方、刷新 R。
fn after(sim: &mut StableSim<'_>, caster: usize) {
    let marks: Vec<String> = sim
        .get_entity(caster)
        .map_or_else(Vec::new, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect())
        .into_iter()
        .filter(|n| n.starts_with(&format!("{HERO}_rk:")))
        .collect();
    let line = head(sim, caster);
    let alive = sim.get_entity(caster).is_some_and(|e| e.is_alive());
    let mut done = false;
    for m in marks {
        sim.entity_remove_buff(caster, &m);
        let Some((target, x, y)) = parse_mark(&m) else { continue };
        let dead = sim.get_entity(target).is_none_or(|e| !e.is_alive());
        if !dead {
            wlog(format!("{line} X: #{target} survived the execute"));
            continue;
        }
        if done || !alive {
            continue;
        }
        done = true;
        sim.entity_set_pos(caster, x, y);
        sim.entity_remove_buff(caster, &format!("{HERO}_r_reset"));
        let mut reset = BuffV1::timed(&format!("{HERO}_r_reset"), 2);
        reset.duration_kind = BuffDurationV1::Time.code();
        reset.ult_cooldown_mult = 10_000;
        sim.add_buff(caster, &reset);
        let at_me = InputTargetV1::target(caster);
        sim.play_view_effect(&format!("{HERO}_r_reset"), caster, &at_me, 0, 0, 0);
        sim.play_sfx(&format!("{HERO}_r_reset"), caster, &at_me);
        sim.play_sfx(&format!("{HERO}_vo_r"), caster, &at_me);
        wlog(format!("{line} RESET: #{target} died, blinked to ({x}, {y}), R ready again"));
    }
}

struct After;
impl StableEffectType for After {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        after(sim, caster);
    }
}

struct Execute;
impl StableEffectType for Execute {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        execute(sim, caster, input);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Pyke's R executes for real, cast only on who it kills) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_effect(format!("{ID}:execute"), Execute);
    module.add_native_effect(format!("{ID}:after"), After);
    module.add_player_input_ai(UltAi::default());
    host.log(LogLevel::Info, "league_pyke v1 loaded (Pyke's R: the exact execute, cast only on a champion it kills).");
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

    fn f(id: usize, hp: usize) -> Foe {
        Foe { id, hp }
    }

    #[test]
    fn the_threshold_is_the_main_packs() {
        // 攻击 72：180 + 43 = 223；斩不死的掉 111（主包：223 真实伤害，回 90 + 30% 攻击力 = 111）
        assert_eq!(threshold(72), 223);
        assert_eq!(survivor_damage(72), 111);
    }

    #[test]
    fn r_only_on_who_it_kills() {
        let foes = [f(1, 900), f(2, 200), f(3, 150)];
        // AI 想砍满血的 1：改砍血最少的 3
        assert_eq!(plan(Some(1), &foes, 223, true), Plan::Ult(3));
        // AI 想砍斩得死的 2：照旧
        assert_eq!(plan(Some(2), &foes, 223, true), Plan::Keep);
        // 没人斩得死：不放，改打他
        assert_eq!(plan(Some(1), &[f(1, 900), f(2, 400)], 223, true), Plan::Hold(1));
        // 目标不在射程表里（走过去放、或已经死了）：先不管，到了再看
        assert_eq!(plan(Some(9), &[f(1, 900)], 223, true), Plan::Keep);
        // AI 没想放、R 好了、有人斩得死：放
        assert_eq!(plan(None, &foes, 223, true), Plan::Ult(3));
        assert_eq!(plan(None, &foes, 223, false), Plan::Keep);
        assert_eq!(plan(None, &[f(1, 900)], 223, true), Plan::Keep);
        // 正好等于斩杀线也处决
        assert_eq!(best_kill(&[f(4, 223)], 223), Some(f(4, 223)));
    }

    #[test]
    fn the_mark_carries_where_he_fell() {
        let m = mark_name(1234, 1_234_567, 7_654_321);
        assert!(m.len() <= BUFF_NAME_CAP);
        assert_eq!(parse_mark(&m), Some((1234, 1_234_567, 7_654_321)));
        assert_eq!(parse_mark("league_pyke_r_reset"), None);
        assert_eq!(parse_mark("league_pyke_rk:1:2"), None);
    }
}
