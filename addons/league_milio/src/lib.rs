//! 米利欧附加包（用户 2026-10-15 选「被动主包数据近似 + 附加包精确」「R 像千珏那样挑时机」）：主包数据做不准的两件事。
//!
//! 主包是纯数据：数据里没有「另一个单位打中了谁」的时机，所以主包的热情洋溢！是 E / R 触及的友方 +30% 攻击力和法强 5 秒；
//! 数据也读不到生命，R 按控制和身边的敌人猜什么时候放。`mod.override_info` 把主包的米利欧换成 `override/` 里的副本
//! （`make_override.py` 用 `tools/kit/build_milio.py` 生成）：
//! - `league_milio_fired` 是热情洋溢！的记号（画面照旧；攻击力、法强加成从主包的 30% 降到 `make_override.MARK` 20%，只到下一次命中
//!   为止——只有灼烧时模拟里他掉到 -2.1），营火每一跳也给周围友方挂上（英雄联盟的营火每次治疗都附带热情洋溢！）；被动是本包的原生
//!   被动 `league_milio:fired`（数字在英雄数据的 `passive.params`）；
//! - R 用 `r_now=1`：一放出就生效（不再待命、不再在普攻和技能里查危险），R 的那圈里每个友方英雄先过本包的原生效果
//!   `league_milio:cleanse`（真的解控）。
//!
//! **热情洋溢！**：带着记号的友方英雄下一次打中敌人（不算防御塔），那个敌人在 `burn_t` tick 里分段受到魔法伤害（总量按米利欧的
//! 等级 `burn_lo` -> `burn_hi`，对野怪最多 `mon_cap`），记号随即消失（同一个友方身上叠了几层也一次用掉）。
//! SDK 里没有「别人打中了谁」的钩子（原生被动的 on_attack / on_damaged 只给被动的主人；布兰德、薇恩、剑姬的附加包是在
//! 自己的投射物里调原生效果，泽丽用她自己的 on_attack），所以友方的出手是这样看出来的（布隆附加包看友军普攻的办法，再细一些）：
//! - 被动每 tick 读每个友方玩家的冷却：某一栏跳高了 = 这一栏刚用掉，开始等这次出手的结果（普攻 `ATTACK_WAIT`、
//!   技能 `SKILL_WAIT` tick）；
//! - 观察钩子 `league_milio:watch`（所有非米利欧玩家都挂，优先级最低，永远不改 AI 的输入）记下每个玩家的 AI 最后一次下令
//!   普攻 / 放技能对准的是谁；出手开始时那道命令还算数（普攻：之后没下过走位 / 回城命令），就只等那个敌人掉血；
//! - 没有命令目标（边走边打、方向 / 地点技能）时，在出手后 `REACH` 以内掉了血（够多）的敌人里，先挑身边有那个友方投射物的，
//!   再挑离他最近的；技能对准友方（治疗、护盾）的不算出手。
//!   经典引擎里量过：AI 的普攻命令 98% 就是这一下打的目标；只按掉血猜，目标是英雄时对 80-84%，小兵 / 野怪 90%。
//! 米利欧自己带着记号时（E 给了自己），用他自己的 on_attack，准确。
//! 灼烧本身不算谁打中的（0.1.2）：引擎把它排进效果队列，下一 tick 才扣血、才触发他的 on_attack（游戏 0.6.4），被动记下上一次
//! 打给每个目标的灼烧，看掉血、看 on_attack 时先认出它（`rules::lost` / `rules::own_burn`）。
//!
//! **生生不息**（AI 钩子 `league_milio:ult`，千珏附加包的做法）：R 在他身边 `IN_CIRCLE` 以内有友方英雄（含他自己）危险时才放：
//! `DANGER_NEAR` 以内有敌方英雄，而且生命不到 `DANGER_HP`，或 `BURST_T` tick 内掉了 `BURST` 以上、只剩 `BURST_LEFT` 以下，
//! 或被硬控（眩晕、禁锢、击飞、嘲讽、恐惧、魅惑）着、还剩 `CC_MIN` tick 以上——AI 没想放也放；其余时候 AI 想放 R：改成普攻
//! 最近的敌方英雄（打不到就走过去），R 留着。R 生效时（放出后 `R_REL` tick），圈里身上有控制的友方英雄被
//! `league_milio:cleanse` 解掉控制（`entity_clear_cc`；主包的 `cc_immune` 只挡新的控制，挡不掉已经在身上的）。
//!
//! 每份模拟各算各的：被动、观察钩子、R 钩子的状态都在各自的对象里（引擎每份模拟各建一份）；唯一共用的是观察钩子交给被动的
//! 命令表，按「这份模拟的编号 + 友方实体」记——编号是被动在米利欧第一次出生时抽的，挂在他身上（buff `league_milio_sim:<编号>`，
//! 没有数值、没有画面），观察钩子从同队的米利欧身上读（游戏 0.6.4 同时跑同一局的两份预模拟，来历和实体编号都一样，
//! 按来历记会串：莫德凯撒附加包 2026-10-14 的教训）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_milio.log`，每次启动游戏重写，上一次的留在 .prev.log：
//! SPAWN / FIRED SET / BURN / FIRED UNUSED / R ORDER / R CAST / R RESULT / R HELD / R CLEANSE。

pub mod rules;

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;
use rules::*;

const ID: &str = "league_milio";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_milio") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// 主包的米利欧。
pub const HERO: &str = "league_milio";
/// 热情洋溢！的记号（主包的 buff，副本里没有数值，画面照旧）。
pub const FIRED: &str = "league_milio_fired";
/// 主包 R 给的免控：R RESULT 看它。
pub const FREE: &str = "league_milio_r_free";
/// 这份模拟的编号：buff `league_milio_sim:<编号>` 挂在米利欧身上。
pub const SIM_TAG: &str = "league_milio_sim:";
/// 灼烧的画面：主包 Q 落地的灼烧（他自己的 view_effects 里有）。
pub const BURN_VIEW: &str = "league_milio_q_burn";
/// 观察钩子的优先级：最低，排在所有英雄自己的钩子前面被问（经典引擎按优先级从低到高问），它只看不改。
const WATCH_PRIORITY: i32 = -1_000_000;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_MILIO_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_milio.log");
        }
    }
    PathBuf::from("league_milio.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (memory log-open-once)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first).
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// 日志条数：每种最多先写 `LOG_FIRST` 条，之后每 `LOG_EVERY` 条一条。
const LOG_FIRST: usize = 60;
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

// ===================== 小工具 =====================

fn at(e: &StableEntity<'_, '_>) -> (f64, f64) {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

fn hp_share((now, max): (usize, usize)) -> f64 {
    if max > 0 {
        now as f64 / max as f64
    } else {
        1.0
    }
}

fn marks(e: &StableEntity<'_, '_>, name: &str) -> usize {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).count()
}

fn undying(e: &StableEntity<'_, '_>) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.undying)
}

/// The number the passive hung on Milio when he spawned in this sim (0: none).
pub fn sim_tag(names: impl Iterator<Item = String>) -> u64 {
    names.into_iter().find_map(|n| n.strip_prefix(SIM_TAG).and_then(|v| v.parse().ok())).unwrap_or(0)
}

fn tag_of(e: &StableEntity<'_, '_>) -> u64 {
    sim_tag((0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()))
}

/// 野怪（R 的灼烧上限按它）：野区营地、大小龙。
fn monster(e: &StableEntity<'_, '_>) -> bool {
    matches!(e.kind(), Some(EntityKindV1::Jungle | EntityKindV1::Epic | EntityKindV1::Serpen))
}

/// 能挨打的敌方单位：防御塔、水晶不算。
fn foe_unit(e: &StableEntity<'_, '_>, team: usize) -> bool {
    e.team() != team && !e.is_tower() && !matches!(e.kind(), Some(EntityKindV1::Tower | EntityKindV1::Nexus))
}

/// 硬控：R 的「被控制着」看这些（剩得最久的那个还有几 tick）。
const HARD: [CcKindV1; 6] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm];
/// 放不出技能的控制（他自己被控住时不放 R）。
const NO_CAST: [CcKindV1; 7] =
    [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm, CcKindV1::BlockSkill];
/// R 解掉的控制（位移 ForceMove、动作锁 Animation 不算：只有身上有这些时才解）。
const CLEANSED: [CcKindV1; 9] = [
    CcKindV1::Airborne,
    CcKindV1::Stun,
    CcKindV1::Bind,
    CcKindV1::BlockAttack,
    CcKindV1::BlockSkill,
    CcKindV1::BlockMoveSkill,
    CcKindV1::Taunt,
    CcKindV1::Fear,
    CcKindV1::Charm,
];

fn cc_left(e: &StableEntity<'_, '_>, kinds: &[CcKindV1]) -> usize {
    (0..e.cc_count())
        .filter_map(|i| e.cc_at(i))
        .filter(|c| kinds.iter().any(|k| k.code() == c.kind))
        .map(|c| c.tick as usize)
        .max()
        .unwrap_or(0)
}

fn cc_names(e: &StableEntity<'_, '_>, kinds: &[CcKindV1]) -> Vec<String> {
    (0..e.cc_count())
        .filter_map(|i| e.cc_at(i))
        .filter(|c| kinds.iter().any(|k| k.code() == c.kind))
        .map(|c| format!("{:?} {}", CcKindV1::from_code(c.kind).unwrap_or(CcKindV1::Stun), c.tick))
        .collect()
}

fn controlled(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).filter_map(|i| e.cc_at(i)).any(|c| NO_CAST.iter().any(|k| k.code() == c.kind))
}

// ===================== 观察钩子交给被动的命令表 =====================

/// 一道命令对准的。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Aim {
    /// 一个敌方单位。
    Foe(usize),
    /// 友方单位（治疗、护盾）：这次出手不打人。
    Friend,
    /// 地点、方向，或没有目标。
    Place,
}

/// 一个玩家的 AI 最近下的命令。
#[derive(Clone, Copy, Debug, Default)]
struct Orders {
    /// 最后一次普攻命令：(tick, 目标)。
    attack: Option<(usize, usize)>,
    /// 最后一次走位 / 回城命令的 tick：比它早的普攻命令不再说明他在打谁。
    moved: usize,
    /// 技能、技能2、大招的最后一次命令：(tick, 对准的)。
    skill: [Option<(usize, Aim)>; 3],
}

/// (这份模拟的编号, 友方英雄的实体) -> 他的 AI 最近的命令。
static ORDERS: LazyLock<Mutex<HashMap<(u64, usize), Orders>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
static NEXT_SIM: AtomicU64 = AtomicU64::new(1);
/// 技能命令下了以后这么多 tick 内冷却跳了，才算这道命令放出来的。
const SKILL_ORDER_FRESH: usize = 30;

fn orders_of(sim_no: u64, ally: usize) -> Orders {
    ORDERS.lock().unwrap_or_else(|e| e.into_inner()).get(&(sim_no, ally)).copied().unwrap_or_default()
}

/// 观察钩子：只记命令，永远不改 AI 的输入。
#[derive(Clone, Default)]
struct Watch {
    /// 同队的米利欧：(实体, 这份模拟的编号)；他死了再出生是新的实体，找不到就重找。
    milio: Option<(usize, u64)>,
    /// 同队没有米利欧：到这一 tick 前不再找。
    none_until: usize,
}

/// 隔多久再找一次同队的米利欧（没找到时）。
const RESCAN: usize = 300;

impl Watch {
    fn sim_no(&mut self, sim: &StableSim<'_>, team: usize, tick: usize) -> Option<u64> {
        if let Some((id, n)) = self.milio {
            if sim.get_entity(id).is_some_and(|e| e.is_alive()) {
                return Some(n);
            }
            self.milio = None;
        }
        if tick < self.none_until {
            return None;
        }
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !e.is_champion() || e.team() != team || !e.is_alive() || e.name().as_deref() != Some(HERO) {
                continue;
            }
            let n = tag_of(&e);
            if n > 0 {
                self.milio = Some((e.id(), n));
                return Some(n);
            }
        }
        self.none_until = tick + RESCAN;
        None
    }
}

impl StablePlayerAi for Watch {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:watch")
    }

    fn priority(&self) -> i32 {
        WATCH_PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name != HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        // only a new order says anything (the AI gives one on its judgement ticks, None in between)
        let b = base?;
        let tick = ctx.tick();
        let player = ctx.player_id();
        let kind = InputKindV1::from_code(b.kind)?;
        let sim = ctx.sim()?;
        let me = sim.get_player(player)?.champion()?;
        let (mid, team) = (me.id(), me.team());
        let n = self.sim_no(&sim, team, tick)?;
        let aim = match InputTargetKindV1::from_code(b.target.kind) {
            Some(InputTargetKindV1::Target) => match sim.get_entity(b.target.target_id) {
                Some(t) if t.team() != team => Aim::Foe(t.id()),
                Some(_) => Aim::Friend,
                None => Aim::Place,
            },
            _ => Aim::Place,
        };
        let mut map = ORDERS.lock().unwrap_or_else(|e| e.into_inner());
        if map.len() > 4096 {
            map.clear();
        }
        let o = map.entry((n, mid)).or_default();
        match kind {
            InputKindV1::Attack => match aim {
                Aim::Foe(t) => o.attack = Some((tick, t)),
                _ => o.moved = tick,
            },
            InputKindV1::Skill => o.skill[0] = Some((tick, aim)),
            InputKindV1::Skill2 => o.skill[1] = Some((tick, aim)),
            InputKindV1::Ult => o.skill[2] = Some((tick, aim)),
            InputKindV1::Move | InputKindV1::Return => o.moved = tick,
        }
        None
    }
}

// ===================== 被动：热情洋溢！ =====================

/// 一次灼烧：目标、还没烧的各段 (tick, 伤害)。
#[derive(Clone, Debug)]
struct Burn {
    target: usize,
    parts: Vec<(usize, usize)>,
}

/// 每个米利欧一份。
#[derive(Clone, Default)]
struct Fired {
    p: Params,
    /// 这份模拟的编号（`SIM_TAG`），他第一次出生时抽。
    sim_no: u64,
    /// 每个友方玩家上一 tick 的冷却。
    cds: HashMap<usize, (usize, usize, usize, usize)>,
    /// 每个友方英雄（实体）正在等结果的那次出手。
    swings: HashMap<usize, Swing>,
    /// 每个友方英雄上一 tick 身上的记号数。
    marks: HashMap<usize, usize>,
    /// 每个敌方单位（防御塔除外）上一 tick 的生命 + 护盾。
    foes: HashMap<usize, usize>,
    /// 每个友方英雄上一 tick 的投射物在哪。
    shots: HashMap<usize, Vec<(f64, f64)>>,
    burns: Vec<Burn>,
    /// 上一次 on_update 打出去的灼烧：目标 -> 减免前的伤害。打出去时只是排进效果队列，下一 tick 才扣血、才触发他的 on_attack。
    burned: HashMap<usize, usize>,
}

impl Fired {
    /// 这一下打中了 `target`：开始灼烧，`ally` 身上的记号用掉。
    fn ignite(&mut self, sim: &mut StableSim<'_>, me: usize, ally: usize, target: usize, how: &str) {
        let now = sim.tick();
        let Some(t) = sim.get_entity(target) else { return };
        let mob = monster(&t);
        let alive = t.is_alive();
        let lv = sim.get_entity(me).map_or(1, |e| e.level());
        sim.entity_remove_buff(ally, FIRED);
        self.marks.insert(ally, 0);
        self.swings.remove(&ally);
        if !alive {
            if let Some(k) = counted("burn_dead") {
                wlog(format!("{} BURN #{k}: {} {how} hit {} - it died of the blow, mark spent", head(sim, me), who(sim, ally),
                             who(sim, target)));
            }
            return;
        }
        let parts = burn_parts(&self.p, lv, mob);
        let total: usize = parts.iter().map(|x| x.1).sum();
        self.burns.retain(|b| b.target != target || b.parts.is_empty());
        self.burns.push(Burn { target, parts: parts.iter().map(|(dt, d)| (now + dt, *d)).collect() });
        sim.play_view_effect(BURN_VIEW, me, &InputTargetV1::target(target), 0, 0, 0);
        if let Some(k) = counted("burn") {
            wlog(format!(
                "{} BURN #{k}: {} {how} hit {} -> {total} magic over {} ticks (Milio Lv{lv}{})",
                head(sim, me),
                who(sim, ally),
                who(sim, target),
                self.p.burn_t,
                if mob { ", monster cap" } else { "" }
            ));
        }
    }

    /// 到点的灼烧段，记进 `burned`：下一 tick 看掉血时先扣掉，他的 on_attack 也认得出它（打出去之前就记：立刻结算的宿主会在
    /// 这次调用里就触发 on_attack）。
    fn burn_parts_due(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let now = sim.tick();
        let mut hit = Vec::new();
        for b in self.burns.iter_mut() {
            while b.parts.first().is_some_and(|p| p.0 <= now) {
                let (_, dmg) = b.parts.remove(0);
                if sim.get_entity(b.target).is_some_and(|e| e.is_alive()) {
                    hit.push((b.target, dmg));
                } else {
                    b.parts.clear();
                }
            }
        }
        self.burns.retain(|b| !b.parts.is_empty());
        for (target, dmg) in hit {
            *self.burned.entry(target).or_insert(0) += dmg;
            if !sim.deal_damage_typed(me, target, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill) {
                if let Some(v) = self.burned.get_mut(&target) {
                    *v -= dmg;
                }
                if let Some(k) = counted("burn_refused") {
                    wlog(format!("{} BURN refused #{k} by the host on {} ({dmg})", head(sim, me), who(sim, target)));
                }
            }
        }
    }

    /// 一个友方英雄开始出手（`slot` 0 普攻、1-3 技能）：等它打中谁。技能对准友方的不算。
    fn open(&self, sim: &StableSim<'_>, ally: &StableEntity<'_, '_>, slot: usize, now: usize) -> Option<Swing> {
        let o = orders_of(self.sim_no, ally.id());
        let target = if slot == 0 {
            o.attack.filter(|(t, _)| *t >= o.moved).map(|x| x.1)
        } else {
            match o.skill[slot - 1] {
                Some((t, Aim::Friend)) if t + SKILL_ORDER_FRESH >= now => return None,
                Some((t, Aim::Foe(x))) if t + SKILL_ORDER_FRESH >= now => Some(x),
                _ => None,
            }
        };
        let from = at(ally);
        let team = ally.team();
        let target = target.filter(|t| {
            sim.get_entity(*t).is_some_and(|e| e.is_alive() && foe_unit(&e, team) && dist(from, at(&e)) <= REACH)
        });
        let wait = if slot == 0 { ATTACK_WAIT } else { SKILL_WAIT };
        Some(Swing { start: now, until: now + wait, target, attack: slot == 0 })
    }

    /// `burned`: what his burn dealt on the last update (landed since, not a hit of anybody's).
    fn watch(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, burned: &HashMap<usize, usize>) {
        let now = sim.tick();
        // 1. allied champions: cooldowns (every tick, for the jumps), marks, the actions that started
        struct Watched {
            cid: usize,
            sw: Swing,
            from: (f64, f64),
            min: usize,
            shots: Vec<(f64, f64)>,
        }
        let mut seen = Vec::new();
        let mut watched: Vec<Watched> = Vec::new();
        let mut any_mark = false;
        for i in 0..sim.player_count() {
            let Some(pl) = sim.player_at(i) else { continue };
            let pid = pl.id();
            let cd = pl.cooldowns();
            let Some(c) = pl.champion() else { continue };
            if c.team() != team || c.id() == me {
                continue;
            }
            let was_cd = match cd {
                Some(cd) => self.cds.insert(pid, (cd.0, cd.1, cd.2, cd.3)),
                None => self.cds.remove(&pid),
            };
            let cid = c.id();
            seen.push(cid);
            if !c.is_alive() {
                self.swings.remove(&cid);
                self.marks.remove(&cid);
                self.shots.remove(&cid);
                continue;
            }
            let n = marks(&c, FIRED);
            let had = self.marks.insert(cid, n).unwrap_or(0);
            if n > had {
                if let Some(k) = counted("fired") {
                    wlog(format!("{} FIRED SET #{k}: {} fired up ({n} mark{})", head(sim, me), who(sim, cid),
                                 if n > 1 { "s" } else { "" }));
                }
            }
            if n == 0 {
                if had > 0 {
                    if let Some(k) = counted("unused") {
                        wlog(format!("{} FIRED UNUSED #{k}: {}'s mark ran out", head(sim, me), who(sim, cid)));
                    }
                }
                self.swings.remove(&cid);
                self.shots.remove(&cid);
                continue;
            }
            any_mark = true;
            // where its projectiles are (this tick and the last: a shot that landed is gone now)
            let shots_now: Vec<(f64, f64)> = (0..sim.projectile_count())
                .filter_map(|k| sim.projectile_at(k))
                .filter(|p| p.caster_id == cid && !p.is_end)
                .map(|p| (p.x as f64, p.y as f64))
                .collect();
            let mut shots = self.shots.insert(cid, shots_now.clone()).unwrap_or_default();
            shots.extend(shots_now);
            // an action started: the slot's cooldown jumped up (one watched at a time: the earlier lands first)
            if !self.swings.contains_key(&cid) {
                if let (Some(was), Some(cd)) = (was_cd, cd) {
                    let jumped = [used(was.0, cd.0), used(was.1, cd.1), used(was.2, cd.2), used(was.3, cd.3)];
                    if let Some(slot) = jumped.iter().position(|j| *j) {
                        if let Some(sw) = self.open(sim, &c, slot, now) {
                            self.swings.insert(cid, sw);
                        }
                    }
                }
            }
            let Some(sw) = self.swings.get(&cid).copied() else { continue };
            if now > sw.until {
                self.swings.remove(&cid);
                continue;
            }
            if now <= sw.start {
                continue;
            }
            let s = c.stat();
            watched.push(Watched { cid, sw, from: at(&c), min: min_amount(sw.attack, s.attack, s.magic_power), shots });
        }
        // allies that left the game (or changed entity at a respawn): forget them
        self.marks.retain(|k, _| seen.contains(k));
        self.swings.retain(|k, _| seen.contains(k));
        self.shots.retain(|k, _| seen.contains(k));
        // 2. nobody carries a mark: nothing to watch (the enemy scan starts again on the tick one does)
        if !any_mark {
            self.foes.clear();
            return;
        }
        // 3. every enemy unit's health + shield, the ones that dropped since the last tick (the ones that died too),
        //    less what his own burn took
        let mut foes = HashMap::new();
        let mut dropped: Vec<(usize, (f64, f64), usize)> = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if !foe_unit(&e, team) {
                continue;
            }
            let id = e.id();
            let left = e.is_alive().then(|| e.hp().0 + e.shield());
            if let Some(&was) = self.foes.get(&id) {
                let amount = lost(was, left, burned.get(&id).copied().unwrap_or(0));
                if amount > 0 {
                    dropped.push((id, at(&e), amount));
                }
            }
            if let Some(v) = left {
                foes.insert(id, v);
            }
        }
        self.foes = foes;
        // 4. which of the watched actions hit someone this tick
        let mut fire: Vec<(usize, usize, String)> = Vec::new();
        for w in watched {
            let drops: Vec<Drop> = dropped
                .iter()
                .map(|(id, p, amount)| Drop {
                    id: *id,
                    dist: dist(w.from, *p),
                    amount: *amount,
                    by_shot: w.shots.iter().any(|s| dist(*s, *p) <= SHOT_NEAR),
                })
                .collect();
            if let Some(t) = hit_of(w.sw.target, &drops, w.min) {
                let slot = if w.sw.attack { "attack" } else { "spell" };
                let how = if w.sw.target.is_some() { format!("{slot} (ordered at it)") } else { format!("{slot} (guessed)") };
                fire.push((w.cid, t, how));
            } else if let Some(t) = w.sw.target {
                // the ordered target is gone: stop waiting for it
                if !sim.get_entity(t).is_some_and(|e| e.is_alive()) {
                    self.swings.remove(&w.cid);
                }
            }
        }
        for (ally, target, how) in fire {
            self.ignite(sim, me, ally, target, &how);
        }
    }
}

impl StablePassive for Fired {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        if self.sim_no == 0 {
            self.sim_no = NEXT_SIM.fetch_add(1, Ordering::Relaxed);
        }
        let tag = format!("{SIM_TAG}{}", self.sim_no);
        sim.entity_remove_buff(me, &tag);
        sim.add_buff(me, &BuffV1::named(&tag));
        let team = sim.get_entity(me).map_or(usize::MAX, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Milio (player {player}, team {team}, sim {}), {:?}", head(sim, me),
                         self.sim_no, self.p));
        }
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        // his own hits (the burn's own damage, landing a tick after it was dealt, does not count)
        if *damage == 0 || own_burn(*damage, self.burned.get(&target).copied().unwrap_or(0)) {
            return;
        }
        let Some(m) = sim.get_entity(me) else { return };
        if marks(&m, FIRED) == 0 {
            return;
        }
        let team = m.team();
        if !sim.get_entity(target).is_some_and(|t| foe_unit(&t, team)) {
            return;
        }
        self.ignite(sim, me, me, target, "own hit");
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        // the burn dealt on the last update has landed by now (its on_attack came before this update)
        let burned = std::mem::take(&mut self.burned);
        let team = match sim.get_entity(me) {
            Some(e) => e.team(),
            None => match sim.get_player(player) {
                Some(p) => p.team(),
                None => return,
            },
        };
        self.watch(sim, me, team, &burned);
        self.burn_parts_due(sim, me);
    }
}

// ===================== R：解控 =====================

/// 主包 R 的那圈里每个友方英雄（副本在 R 的效果最前面调它）：身上有控制就全部解掉。
struct Cleanse;

impl StableEffectType for Cleanse {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            if let Some(k) = counted("cleanse_kind") {
                wlog(format!("{} R CLEANSE #{k} skipped: input kind {} is not a unit", head(sim, caster), input.kind));
            }
            return;
        }
        let target = input.target_id;
        let Some(e) = sim.get_entity(target) else { return };
        if !e.is_alive() {
            return;
        }
        let held = cc_names(&e, &CLEANSED);
        if held.is_empty() {
            return;
        }
        let n = sim.entity_clear_cc(target);
        if let Some(k) = counted("cleanse") {
            wlog(format!("{} R CLEANSE #{k}: {} freed from [{}] ({n} removed)", head(sim, caster), who(sim, target),
                         held.join(", ")));
        }
    }
}

// ===================== AI 钩子：R 只在有人危险时放 =====================

/// 放出去的一次 R：哪一 tick、为谁、他当时的生命比例、为什么。
#[derive(Clone, Copy, Debug)]
struct Cast {
    tick: usize,
    me: usize,
    ally: usize,
    hp: f64,
    why: Why,
}

/// 钩子下令的一次 R（他正忙时引擎几 tick 后才接，期间每 tick 再下一次）。冷却真的开始走时才算放出去（`R CAST`）。
#[derive(Clone, Debug)]
struct Order {
    tick: usize,
    ally: usize,
    hp: f64,
    drop: f64,
    cc: usize,
    why: Why,
    target: usize,
    saved: String,
}

#[derive(Clone, Default)]
struct UltAi {
    /// 每个友方英雄最近 `BURST_T` tick 的生命比例。
    seen: HashMap<usize, Vec<(usize, f64)>>,
    pending: Vec<Cast>,
    order: Option<Order>,
    last_cd: Option<usize>,
    told_no_sim: bool,
}

/// 下令后这么多 tick 内 R 的冷却开始走，就算这道命令放出去的。
const ORDER_FRESH: usize = 30;

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
        let wants_ult = base.is_some_and(|b| b.kind == InputKindV1::Ult.code());
        enum Do {
            Keep,
            Cast(Order),
            /// the enemy champion to attack (in his reach), else the place to walk toward
            Hold(Option<usize>, Option<(u64, u64)>, String),
        }
        let todo = {
            let Some(sim) = ctx.sim() else {
                if !self.told_no_sim {
                    self.told_no_sim = true;
                    wlog(format!("t={tick} player {player}: no simulation to read, R left to the AI"));
                }
                return None;
            };
            let pl = sim.get_player(player)?;
            let me = pl.champion()?;
            let (mid, team) = (me.id(), me.team());
            let line = head(&sim, mid);
            // R went out when its cooldown starts: the order behind it (or the AI's own, which the hold should stop)
            let cd = pl.cooldowns().map(|c| c.3);
            if let (Some(0), Some(c)) = (self.last_cd, cd) {
                if c > 0 {
                    match self.order.take().filter(|o| tick <= o.tick + ORDER_FRESH) {
                        Some(o) => {
                            if let Some(k) = counted("r_cast") {
                                let why = match o.why {
                                    Why::Low => format!("hp {:.0}%", o.hp * 100.0),
                                    Why::Burst => format!("hp {:.0}%, lost {:.0}% in {BURST_T} ticks", o.hp * 100.0, o.drop * 100.0),
                                    Why::Cc => format!("crowd-controlled {} more ticks, hp {:.0}%", o.cc, o.hp * 100.0),
                                };
                                wlog(format!(
                                    "{line} R CAST #{k} [{}] for {} ({why}; R target #{}, ordered {} ticks before)",
                                    o.why.word(),
                                    o.saved,
                                    o.target,
                                    tick - o.tick
                                ));
                            }
                            self.pending.push(Cast { tick, me: mid, ally: o.ally, hp: o.hp, why: o.why });
                        }
                        None => {
                            if let Some(k) = counted("r_cast_ai") {
                                wlog(format!("{line} R CAST by the AI itself (the hold did not stop it) #{k}"));
                            }
                        }
                    }
                }
            }
            self.last_cd = cd;
            let (due, wait): (Vec<Cast>, Vec<Cast>) = self.pending.drain(..).partition(|c| tick >= c.tick + CHECK_AT);
            self.pending = wait;
            for c in due {
                let after = match sim.get_entity(c.ally) {
                    Some(a) if a.is_alive() => {
                        let cc = cc_names(&a, &HARD);
                        format!(
                            "alive, hp {:.0}%{}{}",
                            hp_share(a.hp()) * 100.0,
                            if marks(&a, FREE) > 0 { ", cc-immune (in R)" } else { ", NOT in R" },
                            if cc.is_empty() { String::new() } else { format!(", still held: {}", cc.join(", ")) }
                        )
                    }
                    _ => "dead".to_string(),
                };
                wlog(format!("{} R RESULT [{}] for {} (hp {:.0}% at the cast): {after}", head(&sim, c.me), c.why.word(),
                             who(&sim, c.ally), c.hp * 100.0));
            }
            // health history of his side's champions (every think, so the burst rule sees the last BURST_T ticks)
            let mut allies = Vec::new();
            let mut enemies = Vec::new();
            let mut nearest: Option<(usize, f64, (u64, u64))> = None;
            let my_at = at(&me);
            let mut seen = HashMap::new();
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_champion() || !e.is_alive() {
                    continue;
                }
                let p = at(&e);
                if e.team() != team {
                    enemies.push(p);
                    let d = dist(my_at, p);
                    if e.is_targetable() && d <= R_CAST_RANGE && nearest.is_none_or(|(_, n, _)| d < n) {
                        nearest = Some((e.id(), d, e.pos()));
                    }
                    continue;
                }
                let hp = hp_share(e.hp());
                let mut past = self.seen.remove(&e.id()).unwrap_or_default();
                past.retain(|(t, _)| t + BURST_T >= tick);
                let drop = drop_of(&past, tick, hp);
                past.push((tick, hp));
                seen.insert(e.id(), past);
                if e.is_targetable() {
                    allies.push(Ally { id: e.id(), at: p, hp, drop, undying: undying(&e), cc: cc_left(&e, &HARD) });
                }
            }
            self.seen = seen;
            if !me.is_alive() {
                return None;
            }
            let ready = pl.level() >= ULT_LEVEL && cd == Some(0);
            let save = if ready && !controlled(&me) { pick_save(my_at, &allies, &enemies) } else { None };
            match (save, nearest) {
                (Some((a, why)), Some((t, _, _))) => Do::Cast(Order {
                    tick,
                    ally: a.id,
                    hp: a.hp,
                    drop: a.drop,
                    cc: a.cc,
                    why,
                    target: t,
                    saved: who(&sim, a.id),
                }),
                _ if wants_ult => match nearest {
                    // in reach: attack him (if the attack is not taken, step toward him - never let the R through)
                    Some((t, d, p)) if d <= ATTACK_RANGE => Do::Hold(Some(t), Some(p), line),
                    Some((_, _, p)) => Do::Hold(None, Some(p), line),
                    None => Do::Hold(None, Some(me.pos()), line),
                },
                _ => Do::Keep,
            }
        };
        match todo {
            Do::Keep => None,
            Do::Cast(o) => {
                let input = InputV1::action(InputKindV1::Ult, InputTargetV1::target(o.target));
                if !ctx.is_valid_input(&input) {
                    return None;
                }
                if let Some(k) = counted("r_order") {
                    wlog(format!("t={tick} player {player} R ORDER [{}] for {} (hp {:.0}%) #{k}", o.why.word(), o.saved, o.hp * 100.0));
                }
                self.order = Some(o);
                Some(input)
            }
            Do::Hold(t, walk, line) => {
                if let Some(k) = counted("r_held") {
                    wlog(format!("{line} R HELD #{k}: nobody around him in danger, attacking instead"));
                }
                if let Some(t) = t {
                    let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(t));
                    if ctx.is_valid_input(&attack) {
                        return Some(attack);
                    }
                }
                walk.map(|(x, y)| InputV1::move_to(x, y))
            }
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Milio: Fired Up! burns on an ally's next hit, Breath of Life only to save, a real cleanse) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:fired"), Fired::default());
    module.add_native_effect(format!("{ID}:cleanse"), Cleanse);
    module.add_player_input_ai(UltAi::default());
    module.add_player_input_ai(Watch::default());
    host.log(LogLevel::Info, "league_milio loaded (Fired Up! burns on an ally's next hit, Breath of Life only to save, a real cleanse).");
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
    fn each_sim_finds_its_own_number() {
        let names = |v: &[&str]| v.iter().map(|s| s.to_string()).collect::<Vec<_>>().into_iter();
        assert_eq!(sim_tag(names(&["league_milio_fired", "league_milio_sim:42"])), 42);
        assert_eq!(sim_tag(names(&["league_milio_fired"])), 0);
        assert_eq!(sim_tag(names(&["league_milio_sim:x"])), 0);
    }

    #[test]
    fn the_names_fit_a_buff() {
        assert!(format!("{SIM_TAG}{}", u64::MAX).len() <= BUFF_NAME_CAP);
        assert!(FIRED.len() <= BUFF_NAME_CAP && FREE.len() <= BUFF_NAME_CAP);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_milio.py");
        let src = std::fs::read_to_string(path).expect("build_milio.py");
        for (key, v) in [("r_arm_range", R_CAST_RANGE as usize), ("r_r", R_RADIUS as usize), ("atk_range", ATTACK_RANGE as usize),
                         ("atk", HIS_ATTACK)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_milio.P");
        }
        assert!(src.contains("R_ANIM, R_REL = 36, 20") && R_REL == 20, "R_REL is not build_milio's");
    }

    #[test]
    fn the_passive_params_match_make_override() {
        // from the add-on's own folder, so the add-on bundle (CARGO_MANIFEST_DIR = addons/league_addons) finds it too
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../league_milio/make_override.py");
        let src = std::fs::read_to_string(path).expect("make_override.py");
        let d = Params::default();
        for (key, v) in [("burn_lo", d.burn_lo), ("burn_hi", d.burn_hi), ("burn_t", d.burn_t), ("burn_p", d.burn_p),
                         ("mon_cap", d.mon_cap)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in make_override.PASSIVE");
        }
    }
}
