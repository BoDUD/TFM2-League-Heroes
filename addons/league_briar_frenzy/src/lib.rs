//! 贝蕾亚附加包：E 撞墙才眩晕、血狂锁定目标、大招的血狂持续到猎物倒下（用户 2026-10-24：「查看现在没有做附加包的英雄有明显
//! 不一样的话全部补附加包」）。
//!
//! 主包是纯数据：读不到墙，E 击退的英雄一律在击退结束时眩晕；血莽、彻底血狂期间 AI 照常挑目标（还会回城）；大招的血狂固定
//! 6 秒。英雄联盟里 E 要把人推到墙上才眩晕，血狂中的她只扑最近的敌人，大招的血狂直到她或猎物倒下。本包：
//!
//! - **E（被动 `league_briar_frenzy:frenzy`）**：副本里击退结束时的眩晕换成给英雄挂 `E_MARK`；本包从挂上那一刻记下他的
//!   位置，`KNOCK` tick 后（击退结束）他被推出去不到 `BLOCKED`%（主包推 `KNOCK_DIST`），就是撞上了墙、地图边或别的单位：
//!   眩晕 `E_STUN` tick（`apply_cc`），播主包的眩晕画面和声音。
//! - **大招**：她身上有彻底血狂 `HEMA`、猎物（身上有 `PREY`）还活着，就在血狂快结束时照主包的数值续上，猎物的标记也续上，
//!   最多 `HEMA_MAX` tick。
//! - **血狂锁定（AI 钩子 `league_briar_frenzy:lock`）**：她身上有血莽 `FRENZY` 或 `HEMA` 时，AI 要普攻、走路、回城都改成普攻
//!   ——彻底血狂时打猎物，否则打 `LOCK_R` 内最近的敌方英雄，没有就打最近的敌人；放技能不拦。
//!
//! - **猩红诅咒的另一半（0.1.4，2026-11-14，用户看了「和英雄联盟不一样的地方」清单后说「全改吧」）**：英雄联盟里她每个技能
//!   "5% current Health"，没有生命回复，而 "increases healing from all sources by 0% – 40% (based on missing health)"。
//!   主包把这两条都去掉了（数据读不到当前生命）。副本里：三个技能（冲头、惊吼、毙除）出手时调 `league_briar_frenzy:cost`
//!   ——直接扣当前生命的 `COST_PCT`%，至少留 1 点（耗血不会把自己耗死，也不是伤害）；她自己的三种回血（流血每一跳、
//!   噬击、惊吼蓄力）换成 `league_briar_frenzy:mend_bleed` / `mend_snack` / `mend_scream`：主包的数值按已损生命放大，
//!   满血 +0%，空血 +`MEND_MAX`%（[`mended`]）。彻底血狂的生命偷取是 buff 上的数，没有放大。日志 `COST`、`MEND` 行。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_briar_frenzy.log`。0.1.1：`FRENZY LOCK` 带上
//! `[kind m= s=]`，一次血狂换了目标才记一行，和 `SPAWN` 一样整个游戏一个计数（预模拟先记 40 行、之后每 200 行一行，你看的
//! 那场每行都记）。
//!
//! 0.1.3（2026-11-06，画面和预模拟分岔的排查）：击退结束的英雄按实体编号从小到大判撞墙、眩晕（`knocks_due`）；以前从
//! HashMap 里按它的顺序取，每份模拟都不一样（各有各的随机键），同一 tick 两个人一起结束时眩晕的先后不定。

use std::collections::{BTreeMap, HashMap};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_briar_frenzy";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_briar_frenzy") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const HERO: &str = "league_briar";
pub const E_MARK: &str = "league_briar_frenzy_e";
pub const KNOCK: usize = 16;
pub const KNOCK_DIST: f64 = 40_000.0;
pub const BLOCKED: f64 = 65.0;
pub const E_STUN: u64 = 60;
pub const E_STUN_FX: &str = "league_briar_e_stun";
pub const FRENZY: &str = "league_briar_frenzy";
pub const HEMA: &str = "league_briar_hema";
pub const PREY: &str = "league_briar_r_mark";
pub const HEMA_MAX: usize = 900;
/// 主包彻底血狂的数值（攻速、移速、护甲、魔抗、生命偷取）。
pub const HEMA_STATS: (i32, i32, i32, i32, i32) = (70, 45, 20, 20, 10);
pub const LOCK_R: u64 = 50_000;
pub const UNIT_R: u64 = 30_000;
/// 0.1.4：每个技能耗当前生命的 %（英雄联盟 V26.03 起 5%，之前 6%）。
pub const COST_PCT: usize = 5;
/// 0.1.4：空血时回血多出的 %（英雄联盟："0% – 40% (based on missing health)"）。
pub const MEND_MAX: usize = 40;
/// 主包里她自己的三种回血（固定值、攻击力 %）：流血每一跳、噬击、惊吼蓄力的每一次。`make_override.py` 按这三组数把副本里的
/// `Heal` 换成对应的原生效果，对不上就停。
pub const MEND_BLEED: (usize, usize) = (1, 1);
pub const MEND_SNACK: (usize, usize) = (20, 20);
pub const MEND_SCREAM: (usize, usize) = (6, 4);

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_BRIAR_FRENZY_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_briar_frenzy.log");
        }
    }
    PathBuf::from("league_briar_frenzy.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
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

/// `SPAWN` / `FRENZY LOCK` lines a launch (0.1.1): the server's presims (hundreds a launch, each with new passives and AI
/// hooks - a count in them counts one sim) the first `LOG_FIRST`, then every `LOG_EVERY`-th; the match on screen all.
/// 2026-11-03 night logs: 6188 FRENZY LOCK lines of 7054 (14873 of 16959, 1.0 MB, the launch before), 397 SPAWN.
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind`: its count this launch when it is to be written (`shown`: the match on screen).
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

fn head(sim: &StableSim<'_>, me: usize) -> String {
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
    format!("[{kind} m={} s={}] t={} #{me}", m(o.match_id), m(o.set_index), sim.tick())
}

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn buff_left(e: &StableEntity<'_, '_>, name: &str) -> Option<usize> {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).map(|b| {
        if BuffDurationV1::from_code(b.duration_kind) == Some(BuffDurationV1::Time) { b.duration_tick } else { usize::MAX }
    }).max()
}

/// Did the knock-back hit something? (pushed `moved` of `KNOCK_DIST`)
pub fn blocked(moved: f64) -> bool {
    moved * 100.0 < BLOCKED * KNOCK_DIST
}

/// 根本没被推动（0.1.2）：推了不到 `UNPUSHED`，是击退没生效（免控、不可位移），不是撞上了墙。11-04 的日志里 660 次 E 有 43 次
/// 「pushed 0 of 40000 -> STUNNED」（布隆 E、免控的大招等）：主包的击退推不动他，本包却把他当撞墙晕了。
pub const UNPUSHED: f64 = 1_000.0;

pub fn unpushed(moved: f64) -> bool {
    moved < UNPUSHED
}

/// 身上有免控的 buff（主包的击退、眩晕本来就推不动、晕不了他）。
fn cc_immune(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.cc_immune))
}

fn hema_buff(ticks: usize) -> BuffV1 {
    let mut b = BuffV1::timed(HEMA, ticks);
    (b.attack_speed_mult, b.move_speed_mult, b.defence, b.magic_resistance, b.vamp) = HEMA_STATS;
    b
}

// ===================== 猩红诅咒：技能耗血、血越少回得越多 =====================

/// 一个技能耗多少：当前生命的 `COST_PCT`%，至少给她留 1 点。
pub fn cast_cost(hp: usize) -> usize {
    (hp * COST_PCT / 100).min(hp.saturating_sub(1))
}

/// 这一次回多少：主包的 `flat` + `ratio`% 攻击力，按已损生命放大（满血 +0%，空血 +`MEND_MAX`%）。按百分之一点算再取整：
/// 满血时和数据的 `Heal` 一样（1 + 1% × 150 攻击 = 2.5 -> 2），流血一跳这样的小数也吃得到放大（半血 2.5 × 1.2 = 3）。
pub fn mended(flat: usize, ratio: usize, attack: usize, hp: usize, max: usize) -> usize {
    let missing = if max == 0 { 0 } else { (max - hp.min(max)) * 100 / max };
    (flat * 100 + ratio * attack) * (100 + MEND_MAX * missing / 100) / 10_000
}

/// 副本里每个技能出手时：扣当前生命的 `COST_PCT`%（直接改生命：不是伤害，不被护盾挡）。
fn cost(sim: &mut StableSim<'_>, me: usize, _: InputTargetV1) {
    let Some(hp) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.hp().0) else { return };
    let cost = cast_cost(hp);
    if cost > 0 {
        sim.entity_set_hp(me, hp - cost);
    }
    if let Some(k) = noted("cost", on_screen(sim)) {
        wlog(format!("{} COST: {cost} of {hp} hp #{k}", head(sim, me)));
    }
}

/// 副本里她自己的回血（主包的 `Heal` 换成这个）：按已损生命放大后回给她。
fn mend(sim: &mut StableSim<'_>, me: usize, what: &'static str, (flat, ratio): (usize, usize)) {
    let Some(e) = sim.get_entity(me).filter(|e| e.is_alive()) else { return };
    let ((hp, max), attack) = (e.hp(), e.stat().attack);
    let heal = mended(flat, ratio, attack, hp, max);
    if heal > 0 {
        sim.heal(me, me, heal);
    }
    // the bleed ticks several times a second: only the bigger heals are logged
    if what != "bleed" {
        if let Some(k) = noted("mend", on_screen(sim)) {
            wlog(format!("{} MEND {what}: {heal} at {hp}/{max} hp ({} + {}% of {attack} AD at full health) #{k}",
                         head(sim, me), flat, ratio));
        }
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

/// One of her three heals (its name for the log, the main pack's flat amount and AD ratio). The AI is told what the
/// data's `Heal` told it - the amount at full health - so the copy's actions score as the main pack's do.
struct Mend(&'static str, (usize, usize));
impl StableEffectType for Mend {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        mend(sim, caster, self.0, self.1);
    }

    fn expected_heal(&self, caster_stat: &StatV1) -> usize {
        mended(self.1 .0, self.1 .1, caster_stat.attack, 1, 1)
    }
}

// ===================== 被动 =====================

/// The champions whose knock-back is over at `tick` (`KNOCK` ticks since the mark), by entity id from the smallest: the
/// order their walls are judged and their stuns go out, the same in every run (0.1.3: a HashMap's order, each
/// simulation's own).
pub fn knocks_due(knocked: &BTreeMap<usize, (Pt, usize)>, tick: usize) -> Vec<usize> {
    knocked.iter().filter(|(_, v)| tick >= v.1 + KNOCK).map(|(k, _)| *k).collect()
}

#[derive(Clone, Default)]
struct Frenzy {
    /// E 击退中的英雄：起点、挂上的 tick（按实体编号排，0.1.3）。
    knocked: BTreeMap<usize, (Pt, usize)>,
    /// 彻底血狂开始的 tick。
    hema_from: Option<usize>,
    n: usize,
}

impl StablePassive for Frenzy {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.knocked.clear();
        self.hema_from = None;
        if let Some(k) = noted("spawn", on_screen(sim)) {
            wlog(format!("{} SPAWN: the add-on's Briar (player {player}) #{k}", head(sim, me)));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (team, alive, hema) = (e.team(), e.is_alive(), buff_left(&e, HEMA));
        let foes: Vec<(usize, Pt, bool, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.team() != team)
            .map(|u| (u.id(), pos(&u), u.is_alive() && buff_left(&u, E_MARK).is_some(), u.is_alive() && buff_left(&u, PREY).is_some()))
            .collect();
        // E: where the knocked-back champions started, and whether they got far
        for f in foes.iter().filter(|f| f.2) {
            sim.entity_remove_buff(f.0, E_MARK);
            self.knocked.insert(f.0, (f.1, tick));
        }
        for id in knocks_due(&self.knocked, tick) {
            let (from, _) = self.knocked.remove(&id).unwrap_or(((0.0, 0.0), 0));
            let Some(now) = foes.iter().find(|f| f.0 == id).map(|f| f.1) else { continue };
            let moved = dist(from, now);
            let alive = sim.get_entity(id).is_some_and(|u| u.is_alive());
            // 0.1.2: never pushed at all (the knock-back took no hold: cc immune, unstoppable) is no wall
            let immune = alive && (cc_immune(sim, id) || unpushed(moved));
            let hit = blocked(moved) && alive && !immune;
            if hit {
                sim.apply_cc(id, &CcV1::of_kind(CcKindV1::Stun, E_STUN));
                sim.play_view_effect(E_STUN_FX, me, &InputTargetV1::target(id), 0, 0, 0);
                sim.play_sfx(E_STUN_FX, me, &InputTargetV1::target(id));
            }
            self.n += 1;
            if immune {
                if let Some(k) = noted("immune", on_screen(sim)) {
                    wlog(format!("{} E #{} on #{id}: pushed {moved:.0} of {KNOCK_DIST:.0}: cc immune / not moved, no stun #{k}",
                                 head(sim, me), self.n));
                }
            } else if self.n <= 80 || self.n % 25 == 0 {
                wlog(format!("{} E #{} on #{id}: pushed {moved:.0} of {KNOCK_DIST:.0}{}", head(sim, me), self.n,
                             if hit { " -> hit a wall, STUNNED" } else { " (no wall)" }));
            }
        }
        // R: the full frenzy lasts while the prey lives
        let Some(left) = hema.filter(|_| alive) else {
            self.hema_from = None;
            return;
        };
        let from = *self.hema_from.get_or_insert(tick);
        let prey = foes.iter().find(|f| f.3).map(|f| f.0);
        if let Some(p) = prey {
            if left < 30 && tick < from + HEMA_MAX {
                sim.entity_remove_buff(me, HEMA);
                sim.add_buff(me, &hema_buff(60));
                sim.entity_remove_buff(p, PREY);
                sim.add_buff(p, &BuffV1::timed(PREY, 90));
            }
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.hema_from = None;
    }
}

// ===================== AI 钩子 =====================

#[derive(Clone, Default)]
struct Lock {
    /// the target this frenzy's last FRENZY LOCK line named (a line only when it changes; None: no frenzy)
    locked: Option<usize>,
}

/// A FRENZY LOCK line for `pick`: a new target in this frenzy (0.1.1: a line every 120 ticks of every Briar before).
pub fn new_lock(locked: Option<usize>, pick: usize) -> bool {
    locked != Some(pick)
}

impl StablePlayerAi for Lock {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:lock")
    }

    fn priority(&self) -> i32 {
        100
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        let casting = base.is_some_and(|b| {
            matches!(InputKindV1::from_code(b.kind), Some(InputKindV1::Skill | InputKindV1::Skill2 | InputKindV1::Ult))
        });
        if casting {
            return None;
        }
        let player = ctx.player_id();
        let (pick, line, shown) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion().filter(|e| e.is_alive())?;
            let (id, team) = (me.id(), me.team());
            let hema = buff_left(&me, HEMA).is_some();
            if !hema && buff_left(&me, FRENZY).is_none() {
                self.locked = None;
                return None;
            }
            let units: Vec<(usize, bool, bool, u64)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower())
                .map(|u| (u.id(), u.is_champion(), buff_left(&u, PREY).is_some(), sim.distance_sq(id, u.id())))
                .collect();
            let prey = units.iter().find(|u| u.2 && hema).map(|u| u.0);
            let champ = units.iter().filter(|u| u.1 && u.3 <= LOCK_R * LOCK_R).min_by_key(|u| u.3).map(|u| u.0);
            let unit = units.iter().filter(|u| u.3 <= UNIT_R * UNIT_R).min_by_key(|u| u.3).map(|u| u.0);
            (prey.or(champ).or(unit)?, head(&sim, id), on_screen(&sim))
        };
        let input = InputV1::action(InputKindV1::Attack, InputTargetV1::target(pick));
        let same = base.is_some_and(|b| b.kind == InputKindV1::Attack.code() && b.target.target_id == pick);
        if same || !ctx.is_valid_input(&input) {
            return None;
        }
        // one line a new target, with the [kind m= s=] head, capped for the launch (2026-11-03 night logs: 85% of the log)
        if new_lock(self.locked, pick) {
            self.locked = Some(pick);
            if let Some(k) = noted("lock", shown) {
                wlog(format!("{line} FRENZY LOCK on #{pick} (the AI had {:?}) #{k}", base.map(|b| (b.kind, b.target.target_id))));
            }
        }
        Some(input)
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Briar's E stuns on walls, her frenzy locks on, her ult lasts while the prey lives, her abilities cost health and she heals more the lower she is) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:frenzy"), Frenzy::default());
    module.add_native_effect(format!("{ID}:cost"), Step(cost));
    module.add_native_effect(format!("{ID}:mend_bleed"), Mend("bleed", MEND_BLEED));
    module.add_native_effect(format!("{ID}:mend_snack"), Mend("snack", MEND_SNACK));
    module.add_native_effect(format!("{ID}:mend_scream"), Mend("scream", MEND_SCREAM));
    module.add_player_input_ai(Lock::default());
    host.log(LogLevel::Info, "league_briar_frenzy v1 loaded (Briar: wall stun, frenzy lock, ult on the prey).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_short_push_hit_a_wall() {
        assert!(blocked(10_000.0));
        assert!(blocked(25_000.0));
        assert!(!blocked(39_000.0));
    }

    #[test]
    fn a_push_that_never_moved_him_is_no_wall() {
        // 11-04 logs: 43 of 660 "pushed 0 of 40000 -> STUNNED" (cc-immune targets, Braum's E)
        assert!(unpushed(0.0));
        assert!(unpushed(999.0));
        assert!(!unpushed(1_000.0));
        assert!(!unpushed(10_000.0) && blocked(10_000.0), "a short push is still a wall");
    }

    #[test]
    fn lock_lines_once_a_target_and_capped_for_the_launch() {
        assert!(new_lock(None, 50));
        assert!(!new_lock(Some(50), 50), "the same target: no line");
        assert!(new_lock(Some(50), 51));
        let logged: Vec<usize> = (0..LOG_EVERY * 3).filter_map(|_| noted("test presim", false)).collect();
        assert_eq!(logged.len(), LOG_FIRST + 3);
        assert_eq!(logged[LOG_FIRST..], [LOG_EVERY, LOG_EVERY * 2, LOG_EVERY * 3]);
        assert!((0..LOG_EVERY * 2).all(|_| noted("test shown", true).is_some()));
    }

    /// 0.1.4: Crimson Curse's other half - 5% of current health a cast, healing up to 40% more by missing health.
    #[test]
    fn a_cast_costs_health_but_never_her_last_point() {
        assert_eq!(cast_cost(1000), 50);
        assert_eq!(cast_cost(100), 5);
        assert_eq!(cast_cost(19), 0, "5% of 19 rounds to nothing");
        assert_eq!(cast_cost(1), 0);
        assert_eq!(cast_cost(0), 0);
    }

    #[test]
    fn the_lower_she_is_the_more_she_heals() {
        // full health: the data's own heal (1 + 1% of 150 AD = 2.5 -> 2; Snack Attack 20 + 20% of 150 = 50)
        assert_eq!(mended(1, 1, 150, 1000, 1000), 2);
        assert_eq!(mended(20, 20, 150, 1000, 1000), 50);
        // half health: +20%
        assert_eq!(mended(1, 1, 150, 500, 1000), 3);
        assert_eq!(mended(20, 20, 150, 500, 1000), 60);
        // nearly dead: +40% at most
        assert_eq!(mended(20, 20, 150, 0, 1000), 70);
        assert_eq!(mended(6, 4, 150, 100, 1000), 16);   // 12 x 1.36
        // more health than her maximum (a buff ran out), or no maximum at all: no bonus, no panic
        assert_eq!(mended(20, 20, 150, 1200, 1000), 50);
        assert_eq!(mended(20, 20, 150, 0, 0), 50);
        // what the AI is told: the heal at full health, the data's own number
        let stat = StatV1 { attack: 150, ..StatV1::default() };
        assert_eq!(Mend("snack", MEND_SNACK).expected_heal(&stat), 50);
        assert_eq!(Mend("scream", MEND_SCREAM).expected_heal(&stat), 12);
    }

    #[test]
    fn the_copy_pays_and_mends_natively() {
        let copy = include_str!("../override/league_briar.data_champion");
        for r in ["cost", "mend_bleed", "mend_snack", "mend_scream"] {
            assert!(copy.contains(&format!("\"effect_ref\": \"{ID}:{r}\"")), "the copy never calls {ID}:{r}");
        }
        assert!(!copy.contains("\"type\": \"Heal\""), "a data Heal is left in the copy");
        assert_eq!(copy.matches(&format!("\"effect_ref\": \"{ID}:cost\"")).count(), 3, "one cost a skill");
    }

    #[test]
    fn knock_backs_end_by_id_in_every_run() {
        // 11-06's audit: the knocked went through a HashMap (each simulation's own random order): two knock-backs ending
        // in one tick were judged and stunned in another order in each run of the match
        let knocked = BTreeMap::from([(44, ((0.0, 0.0), 100)), (9, ((0.0, 0.0), 100)), (21, ((0.0, 0.0), 110))]);
        assert_eq!(knocks_due(&knocked, 100 + KNOCK - 1), Vec::<usize>::new());
        assert_eq!(knocks_due(&knocked, 100 + KNOCK), vec![9, 44]);
        assert_eq!(knocks_due(&knocked, 110 + KNOCK), vec![9, 21, 44]);
    }
}
