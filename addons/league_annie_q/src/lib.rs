//! 安妮附加包：Q「碎裂之火」照英雄联盟击杀目标时返还一半冷却（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话
//! 全部补附加包」）；0.3.0 起提伯斯是一个真的单位（试点，见下）。
//!
//! 主包是纯数据：引擎没有「打死了就减冷却」的效果，Q 击杀不返还。本包：副本里 Q 的两枚火球（带不带眩晕的）打中时，在伤害之后
//! 多调用一次原生效果 `league_annie_q:refund`（`input` 就是被打中的单位）：他已经死了（小兵、野怪、英雄都算），就把 Q 的
//! 剩余冷却减 `REFUND` tick（Q 冷却 240 tick 的一半），英雄联盟还返还法力，这里没有法力。
//!
//! **提伯斯是真的单位（0.3.0，2026-11-14；用户看了和英雄联盟不一样的地方的清单：「全改吧」，其中一条是「召唤物不会走、不会打、
//! 打不掉」）。** 主包的提伯斯是挂在目标身上的一串特效和伤害。英雄联盟里他是一只自己走、自己打、能被打死的熊，身上有一圈
//! 灼烧的光环。稳定 mod API 有 `spawn_unit`（公用部分在萨科附加包的 `summon.rs`，这里用 `#[path]` 引进来）：
//!
//! - 副本的 R 不变：召唤那一下（落地的画面、130 + 70% 法强、嗜火的眩晕）是数据，R 给目标挂 `TIB_MARK`，被动看到就开始。
//! - 落地的画面放完的那一 tick（标记后 `TIB_FIRST` tick），被动在画面里那只熊站的地方（目标身后 `TIB_BEHIND`）排一个原生效果
//!   `:tibbers`，它调 `spawn_unit`：单位叫 `league_annie_tibbers`（图是主包的 league/champions/league_annie_tibbers，由
//!   `mod.override_info` 接到这个名字上），活 `TIB_UNIT_LIFE` tick，属性按安妮此刻的算（[`tibbers_spec`]），自己追、自己打，
//!   每下 `TIB_HIT` + `TIB_HIT_AP`% 法强（单位的普攻是物理伤害）。被动接手后每秒在他身边 `TIB_R` 内灼烧一次
//!   （`TIB_AURA` + `TIB_AURA_AP`% 法强的魔法伤害，火圈跟着他），每秒记一行；他没了就在他站的地方化烟。
//! - 生成不了（宿主没有这个接口、失败、测试开关关了）：照 0.2.x——提伯斯挂在目标身上，目标死了换下一个（下面那段）。
//! - 安妮先死了：被动不再跑，熊接着打（引擎管着他），灼烧由排好的 `:aura` 每秒接着烧，到他没了为止。
//!
//! 挂在目标身上的提伯斯（v0.2.0，现在是生成不了单位时的退路）：副本保留召唤那一下，之后的跟随换成给目标挂 `TIB_MARK`；本包
//! 照主包每秒在他身上播站立挥爪和火圈、`TIB_R` 内的敌人受到 14 + 8% 法强的魔法伤害，一共 `TIB_LIFE` tick；他死了（或不能
//! 选中）就换到 `TIB_REACH` 内最近的敌方英雄，没人了才化烟离场。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_annie_q.log`（提伯斯的行以 `TIBBERS` 开头）。测试开关：日志旁边的
//! `league_annie_q.cfg`（`summon.rs`）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

const ID: &str = "league_annie_q";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_annie_q") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const REFUND: usize = 120;
/// 提伯斯（主包的数字和画面）：R 给目标挂的标记、跟多久、第一爪和之后每爪的 tick、灼烧半径和伤害、换目标的距离。
pub const TIB_MARK: &str = "league_annie_q_tib_mark";
pub const TIB_LIFE: usize = 384;
pub const TIB_FIRST: usize = 24;
pub const TIB_PERIOD: usize = 60;
pub const TIB_R: f64 = 30_000.0;
pub const TIB_BURN: usize = 14;
pub const TIB_BURN_AP: usize = 8;
pub const TIB_REACH: f64 = 50_000.0;
pub const TIB_VIEW: &str = "league_annie_tibbers";
pub const TIB_RING: &str = "league_annie_r_ring";
pub const TIB_SWIPE: &str = "league_annie_r_swipe";
pub const TIB_BURN_VIEW: &str = "league_annie_burn";
pub const TIB_VANISH: &str = "league_annie_tibbers_vanish";
pub const TIB_VANISH_SFX: &str = "league_annie_r_vanish";

// ---- 提伯斯作为单位（0.3.0）----

/// The unit's name: the game draws it from asset/base/aseprite_resources/champions/<name>, which mod.override_info sends
/// to the main pack's league/champions/league_annie_tibbers.
pub const TIB_UNIT: &str = "league_annie_tibbers";
/// The handoff from `:tibbers` to the passive: `<TIB_UID>:<unit id>` on Annie for a few ticks.
pub const TIB_UID: &str = "league_annie_q_tib_uid";
/// Ticks the unit lives (8 s: League's 45 s cut for this game's pace; riding, he stayed 6 s after he landed).
pub const TIB_UNIT_LIFE: usize = 480;
/// His burning aura: every `TIB_AURA_EVERY` ticks, first `TIB_AURA_FIRST` after he lands, `TIB_AURA` + `TIB_AURA_AP` % of
/// her ability power as magic damage within `TIB_R` of him - half of what the riding Tibbers burned a second (League's
/// rank-1 aura is 8 + 4 % a second); the other half is his own attacks.
pub const TIB_AURA: usize = 7;
pub const TIB_AURA_AP: usize = 4;
pub const TIB_AURA_EVERY: usize = 60;
pub const TIB_AURA_FIRST: usize = 30;
/// His attack: `TIB_HIT` + `TIB_HIT_AP` % of her ability power a hit (his attack stat; physical, as a unit's attack is),
/// every `TIB_COOL` ticks (League's 0.625 a second), `TIB_ACT` ticks long with the claws down at `TIB_LANDS` (his sheet's
/// attack tag: 0.45 s, the swipe frame 0.17 s in), reach `TIB_RANGE`.
pub const TIB_HIT: usize = 12;
pub const TIB_HIT_AP: usize = 7;
pub const TIB_COOL: usize = 96;
pub const TIB_ACT: usize = 27;
pub const TIB_LANDS: usize = 10;
pub const TIB_RANGE: usize = 15_000;
/// His body: `TIB_HP_PCT` % of her health cap, her armour and magic resistance + `TIB_DEF_MORE`, a move speed of his own.
pub const TIB_HP_PCT: usize = 120;
pub const TIB_DEF_MORE: usize = 20;
pub const TIB_SPEED: usize = 1_050;
/// He appears this far behind (up the screen from) the champion he landed on: where the bear of the drop's picture
/// stands (its feet 10 px above the champion's), so the unit takes the picture's place without a jump.
pub const TIB_BEHIND: f64 = 10_000.0;
/// His puff of smoke as a unit: his own sheet's `dead` tag, on his own ground line (the copy's view effect).
pub const TIB_BYE: &str = "league_annie_q_tib_bye";

/// Ticks the handoff buff stays, and ticks the passive waits for it.
const UID_TICKS: usize = 6;
const ASK_WAIT: usize = 4;
/// Ticks a handed-over unit may take to read as one.
const LOOK_TRIES: usize = 5;
/// A unit gone within this many ticks was never really there: he rides on the target as before.
pub const LOST_AGE: usize = 6;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNT: Mutex<usize> = Mutex::new(0);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ANNIE_Q_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_annie_q.log");
        }
    }
    PathBuf::from("league_annie_q.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

/// The test knobs (`league_annie_q.cfg` beside the log), read once.
static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

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

/// Log the first 150 and every 25th after.
fn counted() -> Option<usize> {
    let mut n = COUNT.lock().unwrap_or_else(|e| e.into_inner());
    *n += 1;
    (*n <= 150 || *n % 25 == 0).then_some(*n)
}

/// Lines of each kind of the unit's a launch (league_shaco_backstab's): the server's presims the first `LOG_FIRST`, then
/// every `LOG_EVERY`-th; the match on screen all.
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

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    let shown = sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    });
    noted(kind, shown)
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

// ===================== 返还 =====================

/// Did this hit kill him? (hp 0 or not alive any more)
pub fn killed(alive: bool, hp: usize) -> bool {
    !alive || hp == 0
}

struct Refund;

impl StableEffectType for Refund {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let id = input.target_id;
        let Some((alive, hp, champ)) = sim.get_entity(id).map(|e| (e.is_alive(), e.hp().0, e.is_champion())) else { return };
        if !killed(alive, hp) {
            return;
        }
        let left = sim.get_entity(caster).and_then(|e| e.cooldown(SkillSlotV1::Skill)).map_or(0, |c| c.remaining);
        sim.entity_reduce_cooldown(caster, SkillSlotV1::Skill, REFUND);
        if let Some(k) = counted() {
            wlog(format!("{} Q KILL #{k} on #{id}{}: cooldown {left} -> {}", head(sim, caster),
                         if champ { " (champion)" } else { "" }, left.saturating_sub(REFUND)));
        }
    }
}

// ===================== 提伯斯：纯函数 =====================

type Pt = (f64, f64);

fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// Whom Tibbers goes on to when his target is gone: the nearest living enemy champion within `TIB_REACH` of `at`.
pub fn next_target(at: Pt, foes: &[(usize, Pt)]) -> Option<usize> {
    foes.iter().filter(|f| dist(at, f.1) <= TIB_REACH).min_by(|a, b| dist(at, a.1).total_cmp(&dist(at, b.1))).map(|f| f.0)
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// Tibbers the unit from Annie's numbers now (`stat`, her health cap `max_hp`).
pub fn tibbers_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    summon::Spec {
        name: TIB_UNIT.to_string(),
        life: TIB_UNIT_LIFE,
        stat: StatV1 {
            attack: TIB_HIT + stat.magic_power * TIB_HIT_AP / 100,
            magic_power: stat.magic_power,
            hp: (max_hp * TIB_HP_PCT / 100).max(1),
            defence: stat.defence + TIB_DEF_MORE,
            magic_resistance: stat.magic_resistance + TIB_DEF_MORE,
            move_speed: TIB_SPEED,
            hp_regen: 0,
            stack: 0,
            crit_chance: 0,
        },
        attack: UnitAttackV1 {
            attack_ratio: 100,
            attack: 0,
            range: TIB_RANGE,
            cooltime: TIB_COOL,
            duration: TIB_ACT,
            start_timing: TIB_LANDS,
            cancelable: false,
            attack_type: AttackTypeV1::BaseAttack.code(),
        },
    }
}

/// One pulse of the unit's aura, before resistance.
pub fn aura_damage(ap: usize) -> usize {
    TIB_AURA + ap * TIB_AURA_AP / 100
}

/// The ticks after his landing at which the aura burns in his `TIB_UNIT_LIFE`.
pub fn aura_ticks() -> Vec<usize> {
    (0..).map(|k| TIB_AURA_FIRST + k * TIB_AURA_EVERY).take_while(|t| *t < TIB_UNIT_LIFE).collect()
}

fn fx(name: &str) -> String {
    format!("{ID}:{name}")
}

fn at_input(at: Pt) -> InputTargetV1 {
    InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64)
}

// ===================== 提伯斯：原生效果 =====================

/// Tibbers spawned for Annie `me` at `at`: the unit's id, and the handoff for her passive on her. `None` (and a line): the
/// host gave no unit, so he rides on the target as before.
fn make_tibbers(sim: &mut StableSim<'_>, me: usize, at: Pt, by: &str) -> Option<usize> {
    let (team, stat, max) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1))?;
    let spec = tibbers_spec(&stat, max).with(&KNOBS);
    match summon::spawn(sim, me, team, at, &spec) {
        Some(id) => {
            sim.add_buff(me, &BuffV1::timed(&summon::handoff(TIB_UID, id), UID_TICKS));
            if let Some(k) = tally(sim, "tib spawn") {
                wlog(format!("{} TIBBERS SPAWN #{k} ({by}): unit #{id} for team {team} at {}: {}", head(sim, me), summon::pt(at),
                             spec.shown()));
            }
            Some(id)
        }
        None => {
            if let Some(k) = tally(sim, "tib fail") {
                wlog(format!("{} TIBBERS SPAWN FAILED #{k} ({by}): spawn_unit gave no unit for '{}' at {} - he rides on the \
                              target as before", head(sim, me), spec.name, summon::pt(at)));
            }
            None
        }
    }
}

/// `:tibbers` - the passive queues it as the drop's picture ends; the input is where he landed.
struct TibbersFx;

impl StableEffectType for TibbersFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let at = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Pos) => (input.x as f64, input.y as f64),
            _ => match sim.get_entity(caster) {
                Some(e) => pos(&e),
                None => return,
            },
        };
        make_tibbers(sim, caster, at, "the queued effect");
    }
}

/// One pulse of the aura round the unit at `at`: the ring and his growl on him, magic damage and a flame on every enemy
/// but towers within `TIB_R`. -> (enemies burned, the damage each before resistance).
fn pulse(sim: &mut StableSim<'_>, annie: usize, unit: usize, at: Pt, team: usize, ap: usize) -> (usize, usize) {
    let on = InputTargetV1::target(unit);
    sim.play_view_effect(TIB_RING, annie, &on, 0, 0, 0);
    sim.play_sfx(TIB_SWIPE, annie, &on);
    let damage = aura_damage(ap);
    let hit: Vec<usize> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && summon::hittable(u) && dist(pos(u), at) <= TIB_R)
        .map(|u| u.id()).collect();
    for id in &hit {
        sim.deal_damage_typed(annie, *id, damage, DamageTypeV1::Ap, AttackTypeV1::Skill);
        sim.play_view_effect(TIB_BURN_VIEW, annie, &InputTargetV1::target(*id), 0, 0, 0);
    }
    (hit.len(), damage)
}

/// `:aura` - queued when Annie dies with the unit out (a dead champion's passive does not run; queued effects do): one
/// pulse round the unit (the input) and the next queued, until he is gone or her body is.
struct AuraFx;

impl StableEffectType for AuraFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let id = input.target_id;
        let Some((team, ap)) = sim.get_entity(caster).map(|e| (e.team(), e.stat().magic_power)) else { return };
        let name = KNOBS.name.as_deref().unwrap_or(TIB_UNIT);
        // her Tibbers still: alive, of her team, under his name, no champion
        let at = sim.get_entity(id).filter(|e| {
            id != caster && e.is_alive() && e.team() == team && e.kind() != Some(EntityKindV1::Champion)
                && e.name().unwrap_or_default() == name
        }).map(|e| pos(&e));
        let Some(at) = at else {
            if let Some(k) = tally(sim, "tib orphan end") {
                wlog(format!("{} TIBBERS ORPHAN END #{k}: the unit #{id} of the dead Annie is gone - the aura stops", head(sim, caster)));
            }
            return;
        };
        let (n, damage) = pulse(sim, caster, id, at, team, ap);
        let again = sim.queue_effect(&fx("aura"), AttackTypeV1::Skill, caster, &InputTargetV1::target(id), TIB_AURA_EVERY);
        if let Some(k) = tally(sim, "tib orphan aura") {
            wlog(format!("{} TIBBERS ORPHAN AURA #{k}: {damage} magic to {n} enemies within {TIB_R:.0} of the unit #{id} at {} \
                          (Annie is dead){}", head(sim, caster), summon::pt(at), if again { "" } else { "; the next one was REFUSED" }));
        }
    }
}

// ===================== 提伯斯：被动 =====================

/// How far a Tibbers has come.
#[derive(Clone, Copy, Debug, PartialEq)]
enum Stage {
    /// The drop's picture plays; the unit is asked for as it ends.
    Drop,
    /// The unit asked for at this tick: its handoff is awaited.
    Asked(usize),
    /// The handed-over unit (id), asked for at the tick, looked at so many times without reading as one.
    Fresh(usize, usize, usize),
    /// No unit: he rides on his target (0.2.x).
    Riding,
}

/// 提伯斯：跟着谁、他在哪、从哪个 tick 起、下一次挥爪的 tick；走到哪一步。
#[derive(Clone, Copy, Debug)]
struct Bear {
    target: usize,
    at: Pt,
    from: usize,
    next: usize,
    stage: Stage,
}

/// Tibbers as a unit, as the passive keeps him.
#[derive(Clone, Debug)]
struct Live {
    unit: summon::Unit,
    /// The tick of the next aura pulse; what the pulses did so far: (pulses, pulses that burned someone, burns, damage).
    next_aura: usize,
    aura: (usize, usize, usize, usize),
    /// The riding Tibbers to fall back to while the unit may still turn out to be none.
    back: Option<Bear>,
}

#[derive(Clone, Default)]
struct Tibbers {
    bear: Option<Bear>,
    n: usize,
    /// Annie herself (on_dead is given the player, not the unit).
    me: usize,
    live: Option<Live>,
    wake: Option<summon::Wake>,
}

impl Tibbers {
    fn vanish(&mut self, sim: &mut StableSim<'_>, me: usize, b: Bear, why: &str) {
        let input = sim.get_entity(b.target).filter(|e| e.is_alive()).map(|_| InputTargetV1::target(b.target))
            .unwrap_or(InputTargetV1::pos(b.at.0.round() as u64, b.at.1.round() as u64));
        sim.play_view_effect(TIB_VANISH, me, &input, 0, 0, 0);
        sim.play_sfx(TIB_VANISH_SFX, me, &input);
        if self.n <= 80 {
            wlog(format!("{} TIBBERS #{} gone ({why})", head(sim, me), self.n));
        }
        self.bear = None;
    }

    /// A line for a hook that fired while the unit is out.
    fn hooked(&self, sim: &StableSim<'_>, hook: &str, entity: usize, other: usize, damage: Option<usize>) {
        let Some(live) = &self.live else { return };
        if let Some(k) = tally(sim, "tib hook") {
            wlog(format!("{} TIBBERS #{} HOOK #{k} {hook}: {}{}", head(sim, self.me), live.unit.n,
                         live.unit.hook_text(sim, entity, other, self.me), damage.map(|d| format!(", damage {d}")).unwrap_or_default()));
        }
    }

    /// The unit's part of a tick: its look, its aura, its end and what comes after.
    fn unit_tick(&mut self, sim: &mut StableSim<'_>, me: usize, here: Pt, team: usize, ap: usize) {
        let tick = sim.tick();
        if let Some(mut live) = self.live.take() {
            let n = live.unit.n;
            if live.back.is_some() && live.unit.age(tick) > LOST_AGE {
                live.back = None;
            }
            match live.unit.step(sim, Some(here)) {
                summon::Step::Alive(line) => {
                    // counted only when there is a line (a count every tick let the presims' first 40 and every 200th
                    // go by ticks, not lines: the game's logs had `TIBBERS #1 #18418:` - hardly a line a second got through)
                    if let Some(line) = line {
                        if let Some(k) = tally(sim, "tib unit") {
                            wlog(format!("{} TIBBERS #{n} #{k}: {line}", head(sim, me)));
                        }
                    }
                    if tick >= live.next_aura {
                        live.next_aura += TIB_AURA_EVERY;
                        let (burned, damage) = pulse(sim, me, live.unit.id, live.unit.at, team, ap);
                        let a = &mut live.aura;
                        (a.0, a.1, a.2, a.3) = (a.0 + 1, a.1 + usize::from(burned > 0), a.2 + burned, a.3 + burned * damage);
                        if let Some(k) = tally(sim, "tib aura") {
                            wlog(format!("{} TIBBERS #{n} AURA #{k}: pulse {} - {damage} magic to {burned} enemies within \
                                          {TIB_R:.0} of him at {}", head(sim, me), a.0, summon::pt(live.unit.at)));
                        }
                    }
                    self.live = Some(live);
                }
                summon::Step::Over(end) => {
                    let a = live.aura;
                    if let Some(k) = tally(sim, "tib over") {
                        wlog(format!("{} TIBBERS #{n} OVER #{k}: {}; his aura: {} pulses, {} burned someone, {} burns, {} magic \
                                      in all before resistance", head(sim, me), end.text, a.0, a.1, a.2, a.3));
                    }
                    match live.back.filter(|_| end.age <= LOST_AGE) {
                        Some(back) => {
                            // never really there: he rides on the target as before
                            wlog(format!("{} TIBBERS #{n}: the unit was gone {} ticks after it was asked for - he rides on \
                                          #{} as before", head(sim, me), end.age, back.target));
                            self.bear = Some(Bear { stage: Stage::Riding, ..back });
                        }
                        None => {
                            // his puff of smoke where he stood, on his own ground line
                            let spot = at_input(end.at);
                            sim.play_view_effect(TIB_BYE, me, &spot, 0, 0, 0);
                            sim.play_sfx(TIB_VANISH_SFX, me, &spot);
                        }
                    }
                    self.wake = Some(live.unit.wake(sim, &end));
                }
            }
        }
        if let Some(mut w) = self.wake.take() {
            let (lines, over) = w.step(sim);
            for line in lines {
                if let Some(k) = tally(sim, "tib wake") {
                    wlog(format!("{} TIBBERS #{} WAKE #{k}: {line}", head(sim, me), w.n));
                }
            }
            if !over {
                self.wake = Some(w);
            }
        }
    }

    /// The steps from R's mark to the unit. -> the bear to go on with as the riding one this tick (`None`: nothing more
    /// to do with him now - the unit is on its way, or he is one).
    fn to_unit(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize, team: usize, mut b: Bear) -> Option<Bear> {
        let tick = sim.tick();
        if b.stage == Stage::Drop && tick + 1 >= b.from + TIB_FIRST {
            // the drop's picture ends next tick: the unit where its bear stands (just behind the champion it landed on)
            let at = (b.at.0, (b.at.1 - TIB_BEHIND).max(0.0));
            let queued = sim.queue_effect(&fx("tibbers"), AttackTypeV1::Skill, me, &at_input(at), 1);
            if !queued {
                make_tibbers(sim, me, at, "queue_effect refused: spawned by the passive");
            }
            b.stage = Stage::Asked(tick);
            if let Some(k) = tally(sim, "tib ask") {
                wlog(format!("{} TIBBERS #{} ASK #{k}: the unit asked for at {} ({TIB_BEHIND:.0} behind #{}, where the drop's \
                              picture stands){}", head(sim, me), self.n, summon::pt(at), b.target,
                             if queued { "" } else { " - queue_effect REFUSED" }));
            }
        }
        if let Stage::Asked(since) = b.stage {
            if let Some(id) = summon::take_handoff(sim, me, TIB_UID) {
                b.stage = Stage::Fresh(id, since, 0);
            } else if tick > since + ASK_WAIT {
                b.stage = Stage::Riding;
                if let Some(k) = tally(sim, "tib none") {
                    wlog(format!("{} TIBBERS #{} NONE #{k}: no unit came within {ASK_WAIT} ticks of the ask - he rides on #{} \
                                  as before", head(sim, me), self.n, b.target));
                }
            }
        }
        if let Stage::Fresh(id, born, tries) = b.stage {
            match summon::Unit::look(sim, id, self.n, born, TIB_UNIT_LIFE, team, player) {
                // taken on once he has settled (summon.rs's Unit::settled: a new unit reads max health 1 and every stat 1
                // on its spawn tick and the next - game 0.7.2's presims read him `hp 2124/1 attack 1 def 1 ...` there),
                // so his LOOK line shows the numbers he really has; when his looks run out, all the same
                Ok((unit, line)) if unit.settled() || tries + 1 >= LOOK_TRIES => {
                    if let Some(k) = tally(sim, "tib look") {
                        wlog(format!("{} TIBBERS #{} LOOK #{k}: {line}{}", head(sim, me), self.n, unit.unsettled_note(tries + 1)));
                    }
                    if let Some(old) = self.live.take() {
                        wlog(format!("{} TIBBERS #{}: the unit #{} of an earlier one is still out - no longer watched",
                                     head(sim, me), self.n, old.unit.id));
                    }
                    self.live = Some(Live { unit, next_aura: tick + TIB_AURA_FIRST, aura: (0, 0, 0, 0), back: Some(b) });
                    self.bear = None;
                    return None;
                }
                Err(why) if tries + 1 >= LOOK_TRIES => {
                    b.stage = Stage::Riding;
                    if let Some(k) = tally(sim, "tib lost") {
                        wlog(format!("{} TIBBERS #{} LOST #{k}: the unit spawn_unit named never read as one in {LOOK_TRIES} \
                                      ticks ({why}) - he rides on #{} as before", head(sim, me), self.n, b.target));
                    }
                }
                _ => b.stage = Stage::Fresh(id, born, tries + 1),
            }
        }
        if b.stage == Stage::Riding {
            return Some(b);
        }
        self.bear = Some(b);
        None
    }
}

impl StablePassive for Tibbers {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        // Tibbers still out at her respawn (her death did not reach on_dead): gone with his picture (0.2.1; before,
        // dropped without a line)
        if let Some(b) = self.bear {
            self.vanish(sim, me, b, "she respawned");
        }
        // a new life is a new entity: the unit of the old one is no longer hers to watch (on_dead queued its aura)
        if let Some(live) = self.live.take() {
            wlog(format!("{} TIBBERS #{}: the unit #{} still on the books at her respawn (her death did not reach on_dead) - \
                          let go", head(sim, me), live.unit.n, live.unit.id));
        }
        self.wake = None;
        wlog(format!("{} SPAWN: the add-on's Annie (player {player})", head(sim, me)));
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        // 0.2.1: the riding Tibbers vanishes with her (11-04's logs: he went silently, no `gone` line, no picture). League
        // keeps him up after her death; a dead champion's passive does not run, so the riding one cannot go on.
        if let Some(b) = self.bear {
            self.vanish(sim, self.me, b, "Annie died");
        }
        self.wake = None;
        // 0.3.0: the unit fights on by itself, as League's does; its aura goes on by a queued effect (those do run for a
        // dead caster) pulse by pulse. Unwatched: no line a second, no puff at his end.
        let Some(live) = self.live.take() else { return };
        let me = sim.get_player(player).and_then(|p| p.champion()).map_or(self.me, |e| e.id());
        let (tick, u) = (sim.tick(), &live.unit);
        let queued = sim.queue_effect(&fx("aura"), AttackTypeV1::Skill, me, &InputTargetV1::target(u.id),
                                      live.next_aura.saturating_sub(tick).max(1));
        if let Some(k) = tally(sim, "tib orphan") {
            wlog(format!("{} TIBBERS #{} ORPHAN #{k}: Annie died, the unit #{} at {} has {} ticks left and hp {}/{} - he fights \
                          on unwatched; his aura {}", head(sim, me), u.n, u.id, summon::pt(u.at), u.left(tick), u.hp, u.max,
                         if queued { "goes on by the queued effect" } else { "was REFUSED (queue_effect): it stops" }));
        }
    }

    // While the unit is out, what the engine tells her passive: do his hits and kills come here, and under whose id?
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, target: usize, damage: &mut usize) {
        self.hooked(sim, "on_attack", entity, target, Some(*damage));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_kill", entity, victim, None);
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_unit_kill", entity, victim, None);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (team, power, here) = (e.team(), e.stat().magic_power, pos(&e));
        self.me = me;
        let foes: Vec<(usize, Pt, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.is_champion() && u.is_alive() && u.team() != team && u.is_targetable())
            .map(|u| (u.id(), pos(&u), has_buff(&u, TIB_MARK)))
            .collect();
        // a new Tibbers: R has just marked his target
        if let Some(f) = foes.iter().find(|f| f.2) {
            sim.entity_remove_buff(f.0, TIB_MARK);
            if let Some(old) = self.bear.take() {
                self.bear = Some(old);
                self.vanish(sim, me, old, "a new one");
            }
            self.n += 1;
            let stage = if KNOBS.off { Stage::Riding } else { Stage::Drop };
            self.bear = Some(Bear { target: f.0, at: f.1, from: tick, next: tick + TIB_FIRST, stage });
            if self.n <= 80 {
                wlog(format!("{} TIBBERS #{} on #{}{}", head(sim, me), self.n, f.0,
                             if KNOBS.off { " (unit=off in the test knobs: he rides on the target as before)" } else { "" }));
            }
        }
        self.unit_tick(sim, me, here, team, power);
        let Some(mut b) = self.bear else { return };
        if b.stage != Stage::Riding {
            // on his way to being a unit: he is where the drop's picture is - on his target while it lives
            if let Some(f) = foes.iter().find(|f| f.0 == b.target) {
                b.at = f.1;
            }
            match self.to_unit(sim, player, me, team, b) {
                Some(riding) => b = riding,
                None => return,
            }
        }
        if tick >= b.from + TIB_LIFE {
            return self.vanish(sim, me, b, "time");
        }
        match foes.iter().find(|f| f.0 == b.target) {
            Some(f) => b.at = f.1,
            None => {
                let near: Vec<(usize, Pt)> = foes.iter().map(|f| (f.0, f.1)).collect();
                match next_target(b.at, &near) {
                    Some(t) => {
                        if self.n <= 80 {
                            wlog(format!("{} TIBBERS #{}: #{} is gone, on to #{t}", head(sim, me), self.n, b.target));
                        }
                        b.target = t;
                        b.at = foes.iter().find(|f| f.0 == t).map_or(b.at, |f| f.1);
                    }
                    None => return self.vanish(sim, me, b, "nobody left near him"),
                }
            }
        }
        if tick >= b.next {
            b.next = tick + TIB_PERIOD;
            let on = InputTargetV1::target(b.target);
            sim.play_view_effect(TIB_RING, me, &on, 0, 0, 0);
            sim.play_view_effect(TIB_VIEW, me, &on, 0, 0, 0);
            sim.play_sfx(TIB_SWIPE, me, &on);
            let damage = TIB_BURN + power * TIB_BURN_AP / 100;
            let hit: Vec<usize> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                .filter(|u| u.team() != team && u.is_alive() && !u.is_tower() && u.is_targetable() && dist(pos(u), b.at) <= TIB_R)
                .map(|u| u.id()).collect();
            for id in hit {
                sim.deal_damage_typed(me, id, damage, DamageTypeV1::Ap, AttackTypeV1::Skill);
                sim.play_view_effect(TIB_BURN_VIEW, me, &InputTargetV1::target(id), 0, 0, 0);
            }
        }
        self.bear = Some(b);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Annie's Disintegrate refunds on a kill, Tibbers a unit of his own) loaded: game {}.{}.{} abi {} \
         log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "TIBBERS: a unit of his own ('{}', spawn_unit) - {}; {TIB_UNIT_LIFE} ticks, {TIB_HIT} + {TIB_HIT_AP}% of her ability power \
         a hit every {TIB_COOL} ticks, the aura {TIB_AURA} + {TIB_AURA_AP}% every {TIB_AURA_EVERY} ticks within {TIB_R:.0}. Test \
         knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(TIB_UNIT),
        if KNOBS.off { "OFF by the test knobs: he rides on the target as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(),
        KNOBS.shown()
    ));
    module.add_native_effect(format!("{ID}:refund"), Refund);
    module.add_native_effect(fx("tibbers"), TibbersFx);
    module.add_native_effect(fx("aura"), AuraFx);
    module.add_native_passive(format!("{ID}:tibbers"), Tibbers::default());
    host.log(LogLevel::Info, "league_annie_q v3 loaded (Disintegrate refunds half its cooldown on a kill; Tibbers as a unit).");
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
#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_kill_is_no_life_left() {
        assert!(killed(false, 100));
        assert!(killed(true, 0));
        assert!(!killed(true, 1));
    }

    #[test]
    fn tibbers_goes_on_to_the_nearest() {
        let f = [(1, (40_000.0, 0.0)), (2, (20_000.0, 0.0)), (3, (5_000.0, 90_000.0))];
        assert_eq!(next_target((0.0, 0.0), &f), Some(2));
        assert_eq!(next_target((0.0, 0.0), &[(3, (5_000.0, 90_000.0))]), None);
    }

    #[test]
    fn the_unit_is_built_from_her_numbers() {
        let hers = StatV1 { attack: 80, magic_power: 240, hp: 900, defence: 90, magic_resistance: 50, move_speed: 990, hp_regen: 5,
                            stack: 2, crit_chance: 10 };
        let spec = tibbers_spec(&hers, 1900);
        assert_eq!(spec.name, "league_annie_tibbers");
        assert_eq!(spec.life, 480);
        // a hit 12 + 7 % of 240 = 28; health 120 % of 1900; her defences + 20; his own speed
        assert_eq!(spec.stat, StatV1 { attack: 28, magic_power: 240, hp: 2280, defence: 110, magic_resistance: 70, move_speed: 1050,
                                       hp_regen: 0, stack: 0, crit_chance: 0 });
        let a = spec.attack;
        assert_eq!(a.attack + spec.stat.attack * a.attack_ratio / 100, 28);
        assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (15_000, 96, 27, 10));
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        assert_eq!(tibbers_spec(&StatV1::default(), 0).stat.hp, 1);
    }

    /// The arithmetic of the README: what the unit can deal against what the riding Tibbers dealt.
    #[test]
    fn the_units_damage_is_about_the_riding_ones() {
        // riding: 6 burns (ticks 24, 84 .. 324 of 384) of 14 + 8 % on everyone in his ring
        let riding_burns = (TIB_FIRST..TIB_LIFE).step_by(TIB_PERIOD).count();
        assert_eq!(riding_burns, 6);
        let riding = |ap: usize| riding_burns * (TIB_BURN + ap * TIB_BURN_AP / 100);
        // the unit: 8 aura pulses of 7 + 4 %, and up to 5 hits of 12 + 7 % on the one he fights (a hit every 96 ticks, the
        // first landing 10 ticks in: 10, 106 .. 394 of 480)
        assert_eq!(aura_ticks(), [30, 90, 150, 210, 270, 330, 390, 450]);
        let hits = (TIB_LANDS..TIB_UNIT_LIFE).step_by(TIB_COOL).count();
        assert_eq!(hits, 5);
        let hit = |ap: usize| TIB_HIT + ap * TIB_HIT_AP / 100;
        for ap in [40, 140, 240, 400] {
            let (aura, blows, old) = (aura_ticks().len() * aura_damage(ap), hits * hit(ap), riding(ap));
            // never out of reach for 8 s: at most 1.45 times the riding one's (on the one he fights; on the others in
            // the ring only the aura - two thirds of it)
            assert!((aura + blows) * 100 <= old * 145, "ap {ap}: {aura} + {blows} against {old}");
            assert!(aura * 100 >= old * 60 && aura * 100 <= old * 70, "ap {ap}: aura {aura} against {old}");
            // in reach of the aura 85 % of the time and of his claws 60 %: about the same as before
            let expected = aura * 85 / 100 + blows * 60 / 100;
            assert!(expected * 100 >= old * 93 && expected * 100 <= old * 107, "ap {ap}: {expected} expected against {old}");
        }
    }

    // ---- Tibbers on the mock world (summon_mock.rs: our guess of the host, to check this side's logic) ----

    use super::mock::{champion, unit, MPlayer, World};

    const GAREN: usize = 1;
    const DARIUS: usize = 2;

    fn log_file() -> PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_annie_q_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_ANNIE_Q_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// Annie #0 (team 0, 240 ability power, 1900 health) at (300000, 300000); Garen #1 60000 east of her, Darius #2
    /// 20000 beyond him, an enemy minion #3 far north; a player each for the champions.
    fn world() -> (World, Tibbers) {
        log_file();
        let mut w = World::default();
        let mut annie = champion("league_annie", 0, 300_000.0, 300_000.0);
        (annie.hp, annie.max, annie.stat.magic_power, annie.stat.defence, annie.stat.magic_resistance) = (1900, 1900, 240, 90, 50);
        let mut garen = champion("league_garen", 1, 360_000.0, 300_000.0);
        (garen.hp, garen.max) = (3000, 3000);
        let mut darius = champion("league_darius", 1, 380_000.0, 300_000.0);
        (darius.hp, darius.max) = (3000, 3000);
        w.units = vec![annie, garen, darius, unit("melee_minion", EntityKindV1::Minion, 1, 300_000.0, 100_000.0, 300)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() },
                         MPlayer { team: 1, champion: DARIUS, ..Default::default() }];
        let mut me = Tibbers::default();
        w.sim(|sim| me.on_spawn(sim, 0, 0));
        (w, me)
    }

    fn tick(w: &mut World, me: &mut Tibbers) {
        for (name, caster, input) in w.due() {
            w.sim(|sim| match name.as_str() {
                "league_annie_q:tibbers" => TibbersFx.apply(sim, 0, caster, input),
                "league_annie_q:aura" => AuraFx.apply(sim, 0, caster, input),
                other => panic!("an effect nobody registered: {other}"),
            });
        }
        if w.units[0].hp > 0 {
            w.sim(|sim| me.on_update(sim, 0, 0, 0));
        }
        w.step();
    }

    fn run(w: &mut World, me: &mut Tibbers, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    /// The copy's R as the data lays it: the mark on its target.
    fn cast_r(w: &mut World, target: usize) -> usize {
        w.units[target].buffs.push((BuffV1::timed(TIB_MARK, 3 + TIB_FIRST), 3 + TIB_FIRST));
        w.tick
    }

    /// Annie's magic damage of the size `amount` so far: the targets in order.
    fn burned(w: &World, amount: usize) -> Vec<usize> {
        w.damage.iter().filter(|d| d.1 == 0 && d.4 == DamageTypeV1::Ap.code() && d.3 == amount).map(|d| d.2).collect()
    }

    #[test]
    fn tibbers_is_a_unit_that_fights_and_burns() {
        let (mut w, mut me) = world();
        let t0 = cast_r(&mut w, GAREN);
        // while the drop's picture plays there is no unit yet, and no riding bear either
        run(&mut w, &mut me, TIB_FIRST - 2);
        assert!(w.spawns.is_empty() && w.views.is_empty());
        run(&mut w, &mut me, 4);
        // one spawn_unit as the picture ends: his name, her team, on the champion he landed on, her numbers
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life), ("league_annie_tibbers", 0, 0, 480));
        assert_eq!(s.at, (360_000, 290_000));
        assert!(s.tick >= t0 + TIB_FIRST - 1 && s.tick <= t0 + TIB_FIRST + 1, "spawned {} ticks after the mark", s.tick - t0);
        assert_eq!((s.stat.attack, s.stat.hp, s.stat.defence, s.stat.magic_resistance, s.stat.move_speed), (28, 2280, 110, 70, 1050));
        let bear = s.gave.unwrap();
        assert!(me.live.is_some() && me.bear.is_none());
        assert!(!w.units[0].buffs.iter().any(|b| b.0.name().starts_with(TIB_UID)) && !w.has(GAREN, TIB_MARK));
        // his whole time: he hits Garen with his claws (28 each, at most 5), the aura burns Garen and Darius (16 each
        // pulse, 8 pulses), the riding bear's pictures and burns never play
        run(&mut w, &mut me, TIB_UNIT_LIFE + 10);
        let claws = w.dealt(bear, DamageTypeV1::Ad);
        assert!(claws.len() >= 4 && claws.len() <= 5 && claws.iter().all(|c| *c == (GAREN, 28)), "{claws:?}");
        let aura = burned(&w, aura_damage(240));
        assert_eq!(aura_damage(240), 16);
        assert_eq!(aura.iter().filter(|t| **t == GAREN).count(), 8, "{aura:?}");
        assert_eq!(aura.iter().filter(|t| **t == DARIUS).count(), 8, "{aura:?}");
        assert_eq!(aura.len(), 16, "something else was burned: {aura:?}");
        assert_eq!(w.viewed(TIB_RING), 8);
        assert_eq!(w.viewed(TIB_BURN_VIEW), 16);
        assert_eq!((w.viewed(TIB_VIEW), w.viewed(TIB_VANISH)), (0, 0), "the riding bear's pictures played beside the unit");
        assert!(burned(&w, TIB_BURN + 240 * TIB_BURN_AP / 100).is_empty(), "the riding bear's burn was dealt beside the unit's");
        // gone at his time: his own puff where he stood, once
        assert!(!w.units[bear].valid);
        assert_eq!((w.viewed(TIB_BYE), w.heard(TIB_VANISH_SFX)), (1, 1));
        let puff = w.views.iter().find(|v| v.1 == TIB_BYE).unwrap();
        assert!(puff.0 >= t0 + TIB_FIRST + TIB_UNIT_LIFE - 3 && puff.0 <= t0 + TIB_FIRST + TIB_UNIT_LIFE + 4);
        run(&mut w, &mut me, 300);
        assert!(me.live.is_none() && me.wake.is_none() && me.bear.is_none() && w.queue.is_empty());
        assert_eq!(w.viewed(TIB_BYE), 1);
        assert_eq!(me.n, 1);
    }

    #[test]
    fn tibbers_is_taken_on_once_his_numbers_read() {
        // game 0.7.2's presims: a new unit reads max health 1 and every stat 1 on its spawn tick and the next
        // (World::settle) - his LOOK line read `hp 2124/1 attack 1 def 1 mr 1 speed 1`
        let (mut w, mut me) = world();
        w.settle = 2;
        cast_r(&mut w, GAREN);
        run(&mut w, &mut me, TIB_FIRST + 2);
        assert_eq!(w.spawns.len(), 1);
        let spawned = w.spawns[0].tick;
        run(&mut w, &mut me, 5);
        let live = me.live.as_ref().expect("never taken on");
        assert!(live.unit.settled() && live.unit.max == 2280);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let look = text.lines().find(|l| l.contains(" TIBBERS #") && l.contains(" LOOK #") && l.contains(&format!("t={} ", spawned + 2)));
        assert!(look.is_some_and(|l| l.contains("hp 2280/2280 attack 28 def 110") && !l.contains("still reads")), "{look:?}");
        // his whole time all the same: the aura's eight pulses
        run(&mut w, &mut me, TIB_UNIT_LIFE + 10);
        assert_eq!(burned(&w, aura_damage(240)).iter().filter(|t| **t == GAREN).count(), 8);
    }

    #[test]
    fn a_killed_tibbers_leaves_in_smoke_and_burns_no_more() {
        let (mut w, mut me) = world();
        cast_r(&mut w, GAREN);
        run(&mut w, &mut me, TIB_FIRST + 100);
        let bear = w.spawns[0].gave.unwrap();
        let before = burned(&w, 16).len();
        assert!(before >= 2);
        w.body_ticks = 30;
        w.hurt(bear, 100_000);
        run(&mut w, &mut me, 5);
        assert_eq!((w.viewed(TIB_BYE), w.heard(TIB_VANISH_SFX)), (1, 1));
        run(&mut w, &mut me, 600);
        assert_eq!(burned(&w, 16).len(), before, "the aura burned on after his death");
        assert_eq!(w.viewed(TIB_BYE), 1);
        assert!(me.live.is_none() && me.wake.is_none() && w.queue.is_empty());
    }

    #[test]
    fn no_unit_from_the_host_and_he_rides_as_before() {
        // no such slot, a refusal, an id that never reads as a unit, a unit gone at once
        for case in 0..4 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                2 => w.spawn_never = true,
                _ => {}
            }
            let t0 = cast_r(&mut w, GAREN);
            if case == 3 {
                run(&mut w, &mut me, TIB_FIRST + 2);
                assert!(me.live.is_some());
                let id = w.spawns[0].gave.unwrap();
                w.units[id].valid = false;
            }
            while w.tick < t0 + TIB_LIFE + 20 {
                tick(&mut w, &mut me);
            }
            // the riding Tibbers of 0.2.x: his pictures on Garen once a second, 14 + 8 % of 240 = 33 to both in the ring,
            // six times (a few ticks late: the wait for the unit), then his puff on Garen
            let riding = burned(&w, 33);
            assert_eq!(riding.iter().filter(|t| **t == GAREN).count(), 6, "case {case}: {riding:?}");
            assert_eq!(riding.iter().filter(|t| **t == DARIUS).count(), 6, "case {case}");
            assert_eq!((w.viewed(TIB_VIEW), w.viewed(TIB_RING)), (6, 6), "case {case}");
            assert_eq!((w.viewed(TIB_VANISH), w.viewed(TIB_BYE)), (1, 0), "case {case}");
            assert!(burned(&w, 16).is_empty(), "case {case}: the unit's aura burned without a unit");
            let first = w.damage.iter().find(|d| d.3 == 33).unwrap().0;
            assert!(first >= t0 + TIB_FIRST && first <= t0 + TIB_FIRST + 12, "case {case}: the first burn {} ticks after the mark", first - t0);
            assert!(me.live.is_none() && me.bear.is_none() && w.queue.is_empty(), "case {case}");
        }
    }

    #[test]
    fn a_host_that_queues_nothing_still_gets_the_unit() {
        let (mut w, mut me) = world();
        w.queue_ok = false;
        cast_r(&mut w, GAREN);
        run(&mut w, &mut me, TIB_FIRST + 3);
        assert_eq!(w.spawns.len(), 1);
        assert!(me.live.is_some());
        run(&mut w, &mut me, TIB_UNIT_LIFE + 10);
        assert_eq!(burned(&w, 16).len(), 16);
        assert_eq!(w.viewed(TIB_BYE), 1);
    }

    #[test]
    fn the_target_killed_by_the_drop_still_gets_a_bear_on_its_spot() {
        let (mut w, mut me) = world();
        cast_r(&mut w, GAREN);
        run(&mut w, &mut me, 8);
        // the drop killed Garen: the unit still comes, where he fell
        (w.units[GAREN].hp, w.units[GAREN].died) = (0, Some(w.tick));
        run(&mut w, &mut me, TIB_FIRST);
        assert_eq!(w.spawns.len(), 1);
        assert_eq!(w.spawns[0].at, (360_000, 290_000));
        assert!(me.live.is_some());
        // and he goes for Darius by himself
        run(&mut w, &mut me, 200);
        assert!(w.dealt(w.spawns[0].gave.unwrap(), DamageTypeV1::Ad).iter().all(|c| c.0 == DARIUS));
        assert!(!w.dealt(w.spawns[0].gave.unwrap(), DamageTypeV1::Ad).is_empty());
    }

    #[test]
    fn he_fights_and_burns_on_when_annie_dies() {
        let (mut w, mut me) = world();
        cast_r(&mut w, GAREN);
        run(&mut w, &mut me, TIB_FIRST + 100);
        let bear = w.spawns[0].gave.unwrap();
        let (burns, claws) = (burned(&w, 16).len(), w.dealt(bear, DamageTypeV1::Ad).len());
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.on_dead(sim, 0));
        assert!(me.live.is_none());
        run(&mut w, &mut me, 200);
        assert!(w.dealt(bear, DamageTypeV1::Ad).len() > claws, "he stopped fighting when she died");
        let later = burned(&w, 16).len();
        assert!(later >= burns + 4, "the aura stopped when she died ({burns} -> {later})");
        // to his end, and no further: 8 pulses on two in all, the chain ends with him
        run(&mut w, &mut me, 400);
        assert_eq!(burned(&w, 16).len(), 16);
        assert!(w.queue.is_empty());
        // the riding one (no unit) still vanishes with her, as 0.2.1
        let (mut w, mut me) = world();
        w.has_spawn = false;
        cast_r(&mut w, GAREN);
        run(&mut w, &mut me, TIB_FIRST + 100);
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.on_dead(sim, 0));
        assert_eq!(w.viewed(TIB_VANISH), 1);
        assert!(me.bear.is_none() && w.queue.is_empty());
    }

    #[test]
    fn the_log_tells_tibbers_whole_life() {
        let (mut w, mut me) = world();
        cast_r(&mut w, GAREN);
        run(&mut w, &mut me, TIB_FIRST + 200);
        let bear = w.spawns[0].gave.unwrap();
        // the engine telling her passive of a hit under the unit's id
        let mut dealt = 28;
        w.sim(|sim| me.on_attack(sim, 0, bear, GAREN, &mut dealt));
        w.players[1].gold += 40;
        w.hurt(bear, 100_000);
        run(&mut w, &mut me, 300);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" TIBBERS ")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "TIBBERS #1 on #1",
            "ASK #", "the unit asked for at (360000,290000) (10000 behind #1, where the drop's picture stands)",
            "TIBBERS SPAWN #", "'league_annie_tibbers' for 480 ticks, attack 28 ap 240 hp 2280 def 110 mr 70 speed 1050; hits 0 + 100% of \
             its attack, range 15000, every 96 ticks (27 long, lands at 10)",
            "LOOK #", "reads back as name 'league_annie_tibbers' kind summon team 0 champion=false",
            " of 480 ticks, at (", "near it: champion #1 league_garen", "its summoner's damage statistic +",
            "AURA #", "pulse 1 - 16 magic to 2 enemies within 30000 of him at (360000,290000)",
            "OVER #", "KILLED after 201 of 480 ticks", "p1 gold +40", "his aura: 3 pulses, 3 burned someone, 6 burns, 96 magic in all before resistance",
            "HOOK #", "on_attack: entity #4 (the unit itself) -> champion #1 league_garen, 10000 from the unit, 60000 from its summoner, damage 28",
            "WAKE #",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
        let longest = mine.iter().map(|l| l.len()).max().unwrap();
        assert!(longest < 700, "a line of {longest} bytes");
    }
}
