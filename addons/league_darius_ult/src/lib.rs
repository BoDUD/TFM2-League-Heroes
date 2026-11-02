//! 诺手附加包：R「诺克萨斯断头台」只在一刀砍得死人时放（用户：「诺手总是在叠满血怒或敌人残血之前就放大招，这种情况
//! 可以用"插件"（或脚本）来调整吗？」「诺手需要调整」；0.1.2：「改成只在能斩杀时放大，血怒不再单独放行」）。
//!
//! 主包保持纯数据：数据读不到当前生命，诺手的 R 由 AI 对「队伍刚打过的敌方英雄」放出——R 一好、身边一开打就放，常常
//! 层数还没叠、对方血还厚，一刀砍不死，R 白白进 50 秒冷却。本包的 AI 钩子 `league_darius_ult:ult` 读生命、护盾和诺手
//! 身上的层数，照主包的数字算这一刀落下时的真实伤害（`plan.rs`）：
//!
//! - 射程内有人一刀砍得死（生命 + 护盾不高于伤害、身上没有免死）：放，几个时砍生命 + 护盾最少的；AI 没想放也放。
//! - 其余时候 AI 想放 R：改成普攻那个人（打不到就走过去），继续叠层。诺克萨斯之力（满 5 层）不单独放行，只让这一刀
//!   伤害翻倍、更容易砍死人（0.1.1 及以前它期间谁都砍：诺手常对着八九成血的人起手，日志里 67 刀只砍死 2 个）。
//!
//! 层数只算撑得到落刀（放出后 `R_LAND` tick）的；落刀前诺克萨斯之力就没了，伤害按 0 层、攻击力去掉它的加成算。
//! R 的伤害、击杀刷新、画面和声音全是主包的：`mod.override_info` 换上的副本只改了 R 的说明（开头【大招读血测试版】）。
//! AI 钩子自己看 R 的冷却和等级（引擎的「输入合法」不看冷却，league_pyke 的教训），放出后再看那一刀砍死了没有。
//!
//! 被动 `league_darius_ult:own_kill`（副本给诺手挂上；用户：「别人反馈人头是诺手的」「改」）：主包只在落刀那一下砍死人时
//! 刷新 R。诺手跃起后、落刀前大招目标就死了，这一刀不落、不刷新；人头若是队友的，照旧不刷新（用户：「这个不改 太违反常识」），
//! 人头是诺手自己的（多半是他的出血在半空里把残血流死），就把 R 还给他，和主包的刷新一样：2 tick 的 `ult_cooldown_mult`
//! 10000。副本在 R 出手时给目标挂 `league_darius_ult_mark` 认人；游戏只在人头算诺手的时候调 `on_kill`。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_darius_ult.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod plan;
use plan::{own_kill_refund, plan as decide, Foe, Me, Plan, Why, HEMO, HERO, MARK, MIGHT, R_KILL, R_LAND, R_RANGE};

const ID: &str = "league_darius_ult";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_darius_ult") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// R 从这一级起能放（同 league_pyke）。
const ULT_LEVEL: usize = 5;
/// 同一类日志至少隔这么多 tick 记一次（AI 每 tick 想一次）。
const LOG_EVERY: usize = 120;
/// 放出后隔多少 tick 看那一刀的结果（落刀后再等几 tick，击杀刷新也在这之内）。
const CHECK_AT: usize = R_LAND + 8;
/// R 的冷却一 tick 掉这么多以上就是刷新了（自然走一 tick 掉 1 左右）。
const REFRESH_DROP: usize = 100;
/// R 的冷却从 0 一下跳到这么多以上 = 刚放出 R（50 秒的冷却，数据 3000 tick）。
const CAST_JUMP: usize = 1000;
/// 主包刷新 R 用的 buff（同名：一次只有一个）。
const RESET: &str = "league_darius_r_reset";

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_DARIUS_ULT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_darius_ult.log");
        }
    }
    PathBuf::from("league_darius_ult.log")
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
    head_of(sim, &format!("#{id}"))
}

/// 日志行头：哪场模拟、第几 tick、谁（`who`）。
fn head_of(sim: &StableSim<'_>, who: &str) -> String {
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
    format!("[{kind} m={} s={}] t={} {who}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 读状态 =====================

/// 一个 buff 还剩几 tick（永久的算无限）。
fn left(b: &BuffV1) -> usize {
    if BuffDurationV1::from_code(b.duration_kind) == Some(BuffDurationV1::Time) {
        b.duration_tick
    } else {
        usize::MAX
    }
}

/// 诺手自己：当前攻击力，诺克萨斯之力和每层出血还剩几 tick。
fn read_me(e: &StableEntity<'_, '_>) -> Me {
    let mut me = Me { attack: e.stat().attack, ..Me::default() };
    for b in (0..e.buff_count()).filter_map(|i| e.buff_at(i)) {
        let slot = if b.name() == MIGHT {
            &mut me.might_left
        } else if let Some(k) = HEMO.iter().position(|h| b.name() == *h) {
            &mut me.hemo_left[k]
        } else {
            continue;
        };
        *slot = Some(slot.map_or(left(&b), |t| t.max(left(&b))));
    }
    me
}

/// 一个敌方英雄：生命、护盾，身上 buff 的免死和受到伤害增减（R 的真实伤害也吃这些，`Foe::damage_from`）。
fn read_foe(e: &StableEntity<'_, '_>) -> Foe {
    let mut foe = Foe { id: e.id(), hp: e.hp().0, shield: e.shield(), ..Foe::default() };
    for b in (0..e.buff_count()).filter_map(|i| e.buff_at(i)) {
        foe.undying |= b.undying;
        foe.reduce += b.damaged_reduce;
        foe.amplify += b.damaged_amplify;
        foe.skill_reduce += b.skill_damaged_reduce;
    }
    foe
}

fn ult(id: usize) -> InputV1 {
    InputV1::action(InputKindV1::Ult, InputTargetV1::target(id))
}

fn why_text(why: Why) -> &'static str {
    match why {
        Why::Kill => "a kill",
        Why::Wait | Why::Pass => "the AI",
    }
}

// ===================== AI 钩子 =====================

/// 放出去的一刀：放出时的 tick、目标、预计伤害、目标那时的生命 + 护盾、落刀时的层数、为什么放、R 刷新了没有。
#[derive(Clone, Copy, Debug)]
struct Cast {
    tick: usize,
    target: usize,
    damage: usize,
    ehp: usize,
    stacks: usize,
    why: Why,
    refreshed: bool,
}

#[derive(Clone, Default)]
struct UltAi {
    /// 最近一次放行或下令的 R（引擎接没接看冷却）。
    last_r: Option<Cast>,
    /// 冷却开始走了的刀，各等 `CHECK_AT` tick 后看结果。
    pending: Vec<Cast>,
    /// 上一 tick R 的冷却。
    last_cd: Option<usize>,
    last_hold: Option<usize>,
    last_cast_log: Option<(usize, usize)>,
    told_no_sim: bool,
}

impl UltAi {
    /// 冷却从 0 跳起来：最近下令的那一刀放出去了；冷却一下子掉了一大截：刚放的刀砍死人刷新了（主包的刷新把 3000 的
    /// 冷却一次削到 29 tick，SDK 模拟里看到的）。`CHECK_AT` tick 后看结果。
    fn watch(&mut self, sim: &StableSim<'_>, cd: Option<usize>, line: &str) {
        let tick = sim.tick();
        match (self.last_cd, cd) {
            (Some(0), Some(c)) if c > 0 => {
                if let Some(r) = self.last_r.filter(|r| tick <= r.tick + 6) {
                    self.pending.push(Cast { tick, refreshed: false, ..r });
                }
            }
            (Some(was), Some(c)) if was > c + REFRESH_DROP => self.pending.iter_mut().for_each(|p| p.refreshed = true),
            _ => {}
        }
        self.last_cd = cd;
        let (due, wait): (Vec<Cast>, Vec<Cast>) = self.pending.drain(..).partition(|p| tick >= p.tick + CHECK_AT);
        self.pending = wait;
        for p in due {
            // the main pack refreshes R only when its own blow kills: dead without a refresh = killed before the blow
            let after = match sim.get_entity(p.target) {
                Some(e) if e.is_alive() => {
                    let (hp, max) = e.hp();
                    format!("he lived, hp {hp}/{max} + shield {}", e.shield())
                }
                _ if p.refreshed => "he died, R refreshed".to_string(),
                _ => "he died before the blow (someone else's kill, no refresh)".to_string(),
            };
            let expect = if p.damage >= p.ehp { "a kill expected" } else { "no kill expected" };
            wlog(format!(
                "{line} R LANDED on #{}: {after} (cast for {}: {} damage at {} stacks vs {} hp + shield, {expect})",
                p.target,
                why_text(p.why),
                p.damage,
                p.stacks,
                p.ehp
            ));
        }
    }
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
        let wants_ult = base.is_some_and(|b| b.kind == InputKindV1::Ult.code());
        let ai_target = base.filter(|_| wants_ult).and_then(|b| {
            (InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)).then_some(b.target.target_id)
        });
        // AI 在放别的技能或回城：不抢着放 R（AI 自己想放的 R 照样检查）
        let busy = base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Return))
        });
        let read = {
            let Some(sim) = ctx.sim() else {
                if !self.told_no_sim {
                    self.told_no_sim = true;
                    wlog(format!("t={tick} player {player}: no simulation to read, R left to the AI"));
                }
                return None;
            };
            (|| {
                let pl = sim.get_player(player)?;
                let cd = pl.cooldowns().map(|c| c.3);
                let me = pl.champion();
                // the blow is watched even when he died right after casting it
                let line = match &me {
                    Some(e) => head(&sim, e.id()),
                    None => head_of(&sim, &format!("player {player}")),
                };
                self.watch(&sim, cd, &line);
                let me = me.filter(|e| e.is_alive())?;
                // `is_valid_input` does not look at cooldowns (league_pyke): an R order on cooldown holds him still
                let free = pl.level() >= ULT_LEVEL && cd == Some(0);
                let (id, team) = (me.id(), me.team());
                let r2 = (R_RANGE as u64).saturating_mul(R_RANGE as u64);
                let enemy = |e: &StableEntity<'_, '_>| e.is_champion() && e.is_alive() && e.team() != team;
                let foes: Vec<Foe> = (0..sim.entity_count())
                    .filter_map(|i| sim.entity_at(i))
                    .filter(|e| enemy(e) && e.is_targetable() && sim.distance_sq(id, e.id()) <= r2)
                    .map(|e| read_foe(&e))
                    .collect();
                let target = ai_target.and_then(|t| sim.get_entity(t));
                let ai_foe = target.as_ref().filter(|e| enemy(e)).map(|e| read_foe(e));
                let target_pos = target.as_ref().map(|e| e.pos());
                Some((read_me(&me), free, foes, ai_foe, target_pos, me.pos(), line))
            })()
        };
        let (me, free, foes, ai_foe, target_pos, my_pos, line) = read?;
        // 主动放只放给现在能被 R 选中的人（施放目标、距离）
        let foes: Vec<Foe> = foes.into_iter().filter(|f| ctx.is_valid_input(&ult(f.id))).collect();
        let (d, stacks) = (me.r_damage(), me.stacks_at_blow());
        let (todo, why) = decide(ai_target, ai_foe, &foes, &me, free && !busy);
        let foe_of = |id: usize| foes.iter().chain(ai_foe.iter()).find(|f| f.id == id).copied();
        let ehp_of = |id: usize| foe_of(id).map(|f| f.ehp());
        // the strike as it lands on him: "540", or "378 (540 less his damage reduction)"
        let blow_on = |id: usize| match foe_of(id).map(|f| f.damage_from(d)) {
            Some(x) if x != d => format!("{x} ({d} before his damage taken changes)"),
            _ => d.to_string(),
        };
        let landing = |id: usize| foe_of(id).map_or(d, |f| f.damage_from(d));
        let hold = |this: &mut Self, ctx: &mut StableAiContext<'_>, x: Option<usize>| -> Option<InputV1> {
            if this.last_hold.is_none_or(|t0| tick >= t0 + LOG_EVERY) {
                this.last_hold = Some(tick);
                let who = match (x, x.and_then(ehp_of)) {
                    (Some(x), Some(ehp)) => format!("#{x} hp + shield {ehp} > {}", blow_on(x)),
                    (Some(x), None) => format!("#{x} is no enemy champion alive"),
                    (None, _) => "no target".to_string(),
                };
                wlog(format!("{line} R HELD: {who} ({stacks} stacks, attack {}), attacking instead", me.attack));
            }
            if let Some(x) = x {
                let attack = InputV1::action(InputKindV1::Attack, InputTargetV1::target(x));
                if ctx.is_valid_input(&attack) {
                    return Some(attack);
                }
            }
            // 打不到：走过去（他不在了就站着），不让 AI 的 R 漏过去
            let (x, y) = target_pos.unwrap_or(my_pos);
            Some(InputV1::move_to(x, y))
        };
        match todo {
            // AI 的 R 没有目标（Darius 的 R 只点人，不该有）：不放行
            Plan::Keep if wants_ult && ai_target.is_none() => hold(self, ctx, None),
            Plan::Keep => {
                if let (Some(x), Why::Kill) = (ai_target, why) {
                    let ehp = ehp_of(x).unwrap_or(0);
                    self.last_r = Some(Cast { tick, target: x, damage: landing(x), ehp, stacks, why, refreshed: false });
                }
                None
            }
            Plan::Ult(id) => {
                let input = ult(id);
                if !ctx.is_valid_input(&input) {
                    return if wants_ult { hold(self, ctx, ai_target) } else { None };
                }
                let ehp = ehp_of(id).unwrap_or(0);
                if self.last_cast_log.is_none_or(|(t0, i)| i != id || tick >= t0 + LOG_EVERY) {
                    self.last_cast_log = Some((tick, id));
                    let instead = match (ai_target, ai_target.and_then(ehp_of)) {
                        (Some(x), Some(e)) => format!("retargeted from #{x} (hp + shield {e})"),
                        (Some(x), None) => format!("retargeted from #{x}"),
                        (None, _) => "the AI had not cast it".to_string(),
                    };
                    wlog(format!(
                        "{line} R KILL: #{id} hp + shield {ehp} vs {} ({stacks} stacks, attack {}), {instead}",
                        blow_on(id),
                        me.attack
                    ));
                }
                self.last_r = Some(Cast { tick, target: id, damage: landing(id), ehp, stacks, why, refreshed: false });
                Some(input)
            }
            Plan::Hold(x) => hold(self, ctx, Some(x)),
        }
    }
}

// ===================== 被动：自己的人头也刷新 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

#[derive(Clone, Default)]
struct OwnKill {
    /// 这一刀放出的 tick 和认出来的大招目标。
    cast: Option<usize>,
    target: Option<usize>,
    last_cd: Option<usize>,
    refunds: usize,
}

impl StablePassive for OwnKill {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        *self = OwnKill { refunds: self.refunds, ..OwnKill::default() };
        wlog(format!("{} SPAWN: own-kill passive on Darius (player {player})", head(sim, me)));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let tick = sim.tick();
        let cd = sim.get_player(player).and_then(|p| p.cooldowns()).map(|c| c.3);
        if let (Some(was), Some(c)) = (self.last_cd, cd) {
            if was == 0 && c > CAST_JUMP {
                self.cast = Some(tick);
                self.target = None;
            }
            // a refresh (the main pack's kill refresh, or this passive's own-kill refund): the 2-tick ult_cooldown_mult
            // leaves about 1% of R's 3000 ticks (29); from game 0.6.4 the rest goes too, a full reset as in League
            // (entity_reduce_cooldown - false on older games, which keep the 29)
            if was > c + REFRESH_DROP && c > 0 && sim.entity_reduce_cooldown(me, SkillSlotV1::Ult, c) {
                wlog(format!("{} R REFRESH: its last {c} ticks cut as well, R ready now", head(sim, me)));
            }
        }
        self.last_cd = cd;
        let Some(t0) = self.cast else { return };
        if tick > t0 + R_LAND + 2 {
            self.cast = None;
            self.target = None;
            return;
        }
        if self.target.is_none() {
            let team = sim.get_entity(me).map_or(usize::MAX, |e| e.team());
            self.target = (0..sim.entity_count())
                .filter_map(|i| sim.entity_at(i))
                .find(|e| e.is_champion() && e.team() != team && (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == MARK))
                .map(|e| e.id());
            if let Some(x) = self.target {
                wlog(format!("{} R CAST seen {} ticks ago, R's target #{x} marked", head(sim, me), tick - t0));
            }
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, me: usize, victim: usize) {
        let is_target = self.target == Some(victim) || has_buff(sim, victim, MARK);
        let landed = has_buff(sim, me, R_KILL);
        if !own_kill_refund(sim.tick(), self.cast, is_target, landed) {
            // every champion kill of his during an R, refunded or not (the in-game check)
            if let Some(t0) = self.cast.filter(|_| sim.get_entity(victim).is_none_or(|e| e.is_champion())) {
                let why = if !is_target { "not R's target" } else if landed { "the blow's own kill: the main pack refreshes" } else { "past the blow" };
                wlog(format!("{} R KILL SEEN: #{victim} {} ticks after the cast, no refund ({why})", head(sim, me), sim.tick() - t0));
            }
            return;
        }
        sim.entity_remove_buff(me, RESET);
        let mut b = BuffV1::timed(RESET, 2);
        b.ult_cooldown_mult = 10000;
        sim.add_buff(me, &b);
        self.refunds += 1;
        let after = self.cast.map_or(0, |t| sim.tick() - t);
        wlog(format!("{} R OWN KILL #{}: #{victim} died to his own damage {after} ticks after the cast, before the blow: R refreshed",
                     head(sim, me), self.refunds));
        self.cast = None;
        self.target = None;
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.cast = None;
        self.target = None;
        self.last_cd = None;
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Darius's R only for a kill; his own kill before the blow refreshes it) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_player_input_ai(UltAi::default());
    module.add_native_passive(format!("{ID}:own_kill"), OwnKill::default());
    host.log(LogLevel::Info, "league_darius_ult v1 loaded (Darius's R: only for a kill; his own kill before the blow refreshes it).");
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
