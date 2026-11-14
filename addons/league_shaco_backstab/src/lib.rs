//! 萨科附加包：「背刺」照英雄联盟看是不是从背后打的（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补
//! 附加包」）；0.2.0 起大招「幻像」是一个真的单位（试点，见下）。
//!
//! 主包是纯数据，读不到朝向：普攻和毒刃打中**被控制**的敌方英雄（被恐惧的人背对着他逃跑）才多一下背刺。英雄联盟里从背后
//! 打到就是背刺，和控制无关。本包：副本里那两枚只打 `EnemyChampionInCC` 的分身弹改成打所有敌方英雄、只给他挂 `ASK`
//! （3 tick）；被动 `league_shaco_backstab:backstab` 每 tick 记下敌方英雄最近 `TRACK` tick 的位置，看到标记就判断：
//!
//! - **朝向**：这段时间走了 `MOVED` 以上，就是他走的方向；站着不动（在打东西）就朝着离他最近的萨科一方单位（英雄、小兵）。
//! - **背后**：萨科在他朝向的反方向那一半（朝向和「他→萨科」的夹角大于 90°）。
//! - 是背刺就补 `base` + `ad`% 攻击力的物理伤害（数字在英雄数据的 `passive.params`，同主包），播主包的背刺画面和声音。
//!
//! Q 落地那一刀（必定暴击）的背刺在主包数据里，不变。
//!
//! **幻像是真的单位（0.2.0，2026-11-14；用户看了和英雄联盟不一样的地方的清单：「全改吧」，其中一条是「召唤物不会走、不会打、
//! 打不掉」）。** 主包里幻像的画面和伤害是挂在目标身上的。英雄联盟里它是另一个萨科：自己走、自己打，伤害比本人低、受到的
//! 伤害比本人高，可以被打死，死了或者到时间就爆炸，放出三个小魔盒。稳定 mod API 有 `spawn_unit`（公用部分在 `summon.rs`）：
//!
//! - 副本的 R 出手时给萨科挂 `R_ASK`（3 tick）。被动看到就在他身旁选一个点（[`beside`]：离他 `SIDE`，横在他和最近的敌方
//!   英雄的连线旁边、和他并排，每次换一边——原版引擎自己的召唤物也是出现在召唤者身边 20000 处；不会选到场上所有单位
//!   围成的范围之外，那一边出了范围就用另一边，见 [`summon::inside`]），排一个原生效果
//!   `:clone`（`spawn_unit` 在原生效果里调，别的 mod 已经这样用过）。
//! - `:clone` 生成一个叫 `league_shaco` 的单位（应该就按他自己的图画，高清帧在内——要在游戏里看），属性照他此刻的
//!   （[`clone_spec`]：攻击、防御、移速一样，生命上限一样、当前生命也设成一样），普攻照他的普攻（距离、间隔、出手时刻），
//!   每下 `CLONE_HIT` + `CLONE_HIT_AD`% 攻击力（主包幻像每一下的数字），活 `CLONE_LIFE` tick（主包的 5 秒）；成功了就给萨科
//!   挂 `R_UNIT`——副本的数据在出手后第 12 tick 读它：有，就不再放挂在目标身上的那个幻像；没有（宿主没有这个接口、生成失败、
//!   或者开关关了），就和今天一模一样。再挂一个名字里带单位 id 的短 buff，被动读到就接手（[`summon::take_handoff`]）。
//! - 被动接手后给幻像挂「受到的伤害 +`CLONE_TAKES`%」，每 tick 看它一眼，每秒记一行；它没了（被打死或到时间）就在它最后
//!   站的地方爆炸（原生效果 `:burst`）：`BOOM` + `BOOM_AP`% 法强的魔法伤害、恐惧（英雄 `FEAR_CHAMP` tick、其余
//!   `FEAR_OTHER`）、三个小魔盒的画面，之后 `BOX_SHOTS` 次射击（`:box`）——数字都是主包的，`make_override.py` 对照检查。
//!   小魔盒还不是单位（打不掉），以后再做。
//! - 萨科先死了：被动不再跑，幻像接着打（引擎管着它），到时间前 2 tick 由排好的 `:end` 在它站的地方爆炸；这期间它被打死
//!   就不爆炸了（没人看着）。
//!
//! **惊吓魔盒有了身体（0.3.0，2026-11-14，`jack.rs`；用户：「召唤物的全做啊」）**：副本的 W 落地时原生效果 `:jack` 在落点生成
//! 身体 `league_shaco_jack`（打得到、打得掉，不会走），弹开时由本包按主包的节奏射击，身体被打掉就停；数据只留恐惧和声音。
//! 生成不了就和以前一样。幻像的代码和 `summon.rs` 没动。日志里 `JACK` 开头的行。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_shaco_backstab.log`。0.1.1：`BACKSTAB`、`SPAWN` 整个游戏一个
//! 计数（预模拟先记 40 行、之后每 200 行一行，你看的那场每行都记；以前每个被动自己数「前 80 行」），参数只在第一行 `SPAWN` 写。
//! 幻像的行都以 `CLONE` 开头。测试开关：日志旁边的 `league_shaco_backstab.cfg`（`summon.rs`）。

use std::collections::{HashMap, VecDeque};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod summon;

pub mod jack;

const ID: &str = "league_shaco_backstab";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_shaco_backstab") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const ASK: &str = "league_shaco_bs_ask";
pub const VIEW: &str = "league_shaco_bs_hit";
pub const TRACK: usize = 10;
pub const MOVED: f64 = 1_500.0;

// ---- 幻像（数字是主包的，make_override.py 对照主包检查；改主包就改这里）----

/// The copy's R lays it on him as it is cast (3 ticks): a clone, please.
pub const R_ASK: &str = "league_shaco_r_ask";
/// On him while his clone is a unit: the copy's data reads it and leaves the clone riding on the target out.
pub const R_UNIT: &str = "league_shaco_r_unit";
/// The handoff from `:clone` to the passive: `<R_UID>:<unit id>` on him for a few ticks.
pub const R_UID: &str = "league_shaco_r_uid";
/// The clone's unit name: his own id, so the game draws it from his own sheet.
pub const CLONE_NAME: &str = "league_shaco";
/// On the clone: it takes `CLONE_TAKES` % more damage (League: 50 %).
pub const CLONE_BUFF: &str = "league_shaco_clone";
pub const CLONE_TAKES: usize = 50;
/// The clone's time (the main pack's `league_shaco_r_on`).
pub const CLONE_LIFE: usize = 312;
/// Each hit of the clone: `CLONE_HIT` + `CLONE_HIT_AD` % of his attack (the main pack's riding clone).
pub const CLONE_HIT: usize = 10;
pub const CLONE_HIT_AD: usize = 40;
/// The clone's attack like his own: range, ticks between attacks, the action's length, the tick the hit lands.
pub const CLONE_RANGE: usize = 23_000;
pub const CLONE_COOL: usize = 52;
pub const CLONE_ACT: usize = 22;
pub const CLONE_LANDS: usize = 9;
/// The blast where the clone ends: `BOOM` + `BOOM_AP` % of his ability power, magic, within `BOOM_R`.
pub const BOOM: usize = 150;
pub const BOOM_AP: usize = 100;
pub const BOOM_R: f64 = 30_000.0;
/// The mini boxes' fear within `BOOM_R`: champions, the others.
pub const FEAR_CHAMP: u64 = 45;
pub const FEAR_OTHER: u64 = 75;
/// The mini boxes' shots: `BOX_SHOTS` of them, the first `BOX_FIRST` ticks after the blast and then every `BOX_EVERY`,
/// each `BOX_HIT` + `BOX_HIT_AP` % of his ability power, magic, within `BOX_R`.
pub const BOX_SHOTS: usize = 5;
pub const BOX_FIRST: usize = 1;
pub const BOX_EVERY: usize = 30;
pub const BOX_HIT: usize = 8;
pub const BOX_HIT_AP: usize = 10;
pub const BOX_R: f64 = 32_000.0;
/// The main pack's pictures and sounds the natives play.
pub const BOOM_VIEW: &str = "league_shaco_r_boom";
pub const BURN_VIEW: &str = "league_shaco_r_burn";
pub const MINI_VIEW: &str = "league_shaco_r_mini";
pub const POP_SFX: &str = "league_shaco_r_pop";
pub const FEAR_VIEW: &str = "league_shaco_fear";
pub const SHOT_VIEW: &str = "league_shaco_shot_hit";
pub const APPEAR_VIEW: &str = "league_shaco_q_appear";
pub const APPEAR_SFX: &str = "league_shaco_clone_in";

/// The clone appears this far beside him (the base game's own summons appear 20000 from their summoner; two bodies
/// on one spot would read as one Shaco).
pub const SIDE: f64 = 14_000.0;
/// Ticks the flag outlasts the clone's time.
const FLAG_MORE: usize = 30;
/// Ticks the handoff buff stays, and ticks the passive waits for it.
const UID_TICKS: usize = 6;
const ASK_WAIT: usize = 4;
/// Ticks a handed-over unit may take to read as one.
const LOOK_TRIES: usize = 5;
/// A unit gone within this many ticks was never really there: no blast, the flag goes and the data's clone plays (the
/// data reads the flag 12 ticks after the cast; the unit is spawned at most 3 ticks after it).
pub const LOST_AGE: usize = 6;
/// `:end` bursts the clone this many ticks before its time when he is dead.
const END_BEFORE: usize = 2;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SHACO_BACKSTAB_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_shaco_backstab.log");
        }
    }
    PathBuf::from("league_shaco_backstab.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

/// The test knobs (`league_shaco_backstab.cfg` beside the log), read once.
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

/// Lines of each kind a launch (0.1.1, league_irelia's): the server's presims (hundreds a launch, each with new passives -
/// a count in the passive counts one sim) the first `LOG_FIRST`, then every `LOG_EVERY`-th; the match on screen all.
/// 2026-11-03 night logs: the passive's own "first 80" let 1131 BACKSTAB lines through (84% of the log).
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

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    noted(kind, on_screen(sim))
}

/// The params the log showed last (the champion data's: the same in every sim of a launch).
static PARAMS_SHOWN: Mutex<Option<Vec<(String, usize)>>> = Mutex::new(None);

/// `p` not in the log yet: once a launch, again only if they ever differ (league_talon_vault's).
fn params_new(p: &[(String, usize)]) -> bool {
    let mut shown = PARAMS_SHOWN.lock().unwrap_or_else(|e| e.into_inner());
    if shown.as_deref() == Some(p) {
        return false;
    }
    *shown = Some(p.to_vec());
    true
}

fn params(json: &str) -> Vec<(String, usize)> {
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    body.split(',')
        .filter_map(|pair| {
            let (k, v) = pair.split_once(':')?;
            Some((k.trim().trim_matches('"').to_string(), v.trim().parse::<usize>().ok()?))
        })
        .collect()
}

fn get(p: &[(String, usize)], k: &str, d: usize) -> usize {
    p.iter().find(|(n, _)| n == k).map_or(d, |(_, v)| *v)
}

// ===================== 朝向 =====================

type Pt = (f64, f64);

fn sub(a: Pt, b: Pt) -> Pt {
    (a.0 - b.0, a.1 - b.1)
}

fn len(v: Pt) -> f64 {
    (v.0 * v.0 + v.1 * v.1).sqrt()
}

/// Which way he faces: where he walked (`trail`, oldest first), else toward `foe` (the nearest of Shaco's side).
pub fn facing(trail: &VecDeque<Pt>, foe: Option<Pt>) -> Option<Pt> {
    let (first, last) = (trail.front()?, trail.back()?);
    let walk = sub(*last, *first);
    if len(walk) >= MOVED {
        return Some(walk);
    }
    foe.map(|f| sub(f, *last)).filter(|v| len(*v) > 1.0)
}

/// Is Shaco at `shaco` behind someone at `at` facing `face`? (the back half: more than 90° off his facing)
pub fn behind(at: Pt, face: Pt, shaco: Pt) -> bool {
    let v = sub(shaco, at);
    face.0 * v.0 + face.1 * v.1 < 0.0
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

// ===================== 幻像：纯函数 =====================

/// Where the clone appears: `SIDE` beside him at `here`, across the line to the enemy he faces (`toward`: the nearest
/// enemy champion; none: as if one stood east of him) - shoulder to shoulder with him, on the other side for every
/// other clone (`n`: his clones so far). Never off the map's top or left edge.
pub fn beside(here: Pt, toward: Option<Pt>, n: usize) -> Pt {
    let v = toward.map(|t| sub(t, here)).filter(|v| len(*v) > 1.0).unwrap_or((1.0, 0.0));
    let d = len(v);
    let s = if n % 2 == 0 { SIDE } else { -SIDE };
    ((here.0 - v.1 / d * s).max(0.0), (here.1 + v.0 / d * s).max(0.0))
}

/// The clone from his own numbers now (`stat`, his health cap `max_hp`): his attack, defences and speed, his health
/// cap, his own attack's range and timing, each hit `CLONE_HIT` + `CLONE_HIT_AD` % of that attack. No crits, no regen.
pub fn clone_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    summon::Spec {
        name: CLONE_NAME.to_string(),
        life: CLONE_LIFE,
        stat: StatV1 {
            attack: stat.attack,
            magic_power: stat.magic_power,
            hp: max_hp.max(1),
            defence: stat.defence,
            magic_resistance: stat.magic_resistance,
            move_speed: stat.move_speed,
            hp_regen: 0,
            stack: 0,
            crit_chance: 0,
        },
        attack: UnitAttackV1 {
            attack_ratio: CLONE_HIT_AD,
            attack: CLONE_HIT,
            range: CLONE_RANGE,
            cooltime: CLONE_COOL,
            duration: CLONE_ACT,
            start_timing: CLONE_LANDS,
            cancelable: false,
            attack_type: AttackTypeV1::BaseAttack.code(),
        },
    }
}

/// The blast's and a box shot's magic damage before resistance, from his ability power.
pub fn boom_damage(ap: usize) -> usize {
    BOOM + ap * BOOM_AP / 100
}

pub fn box_damage(ap: usize) -> usize {
    BOX_HIT + ap * BOX_HIT_AP / 100
}

/// The length of the direction a native fear is given. The API says "direction" and no more: `FEAR_DIR` long it is a
/// unit vector should the engine count in thousandths, a walking pace should it step by it, and nothing at all to
/// one that normalises it (as it does a forced move's).
pub const FEAR_DIR: f64 = 1_000.0;

/// The way someone at `at` runs from a blast at `from`: `FEAR_DIR` long, never (0, 0).
pub fn away(from: Pt, at: Pt) -> (i64, i64) {
    let v = sub(at, from);
    let d = len(v);
    if d < 1.0 {
        return (FEAR_DIR as i64, 0);
    }
    let (dx, dy) = ((v.0 / d * FEAR_DIR).round() as i64, (v.1 / d * FEAR_DIR).round() as i64);
    if dx == 0 && dy == 0 { (FEAR_DIR as i64, 0) } else { (dx, dy) }
}

/// The ticks after a blast at which the mini boxes shoot.
pub fn box_ticks() -> Vec<usize> {
    (0..BOX_SHOTS).map(|k| BOX_FIRST + k * BOX_EVERY).collect()
}

fn fx(name: &str) -> String {
    format!("{ID}:{name}")
}

fn point(input: &InputTargetV1) -> Option<Pt> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Pos)).then_some((input.x as f64, input.y as f64))
}

fn at_input(at: Pt) -> InputTargetV1 {
    InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64)
}

// ===================== 幻像：原生效果 =====================

/// The clone spawned for `me` at `at`: the unit's id, the flag for the data and the handoff for the passive on him.
/// `None` (and a line): the host gave no unit, so the data's clone plays.
fn make_clone(sim: &mut StableSim<'_>, me: usize, at: Pt, by: &str) -> Option<usize> {
    let (team, stat, max) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1))?;
    let spec = clone_spec(&stat, max).with(&KNOBS);
    match summon::spawn(sim, me, team, at, &spec) {
        Some(id) => {
            sim.add_buff(me, &BuffV1::timed(R_UNIT, CLONE_LIFE + FLAG_MORE));
            sim.add_buff(me, &BuffV1::timed(&summon::handoff(R_UID, id), UID_TICKS));
            if let Some(k) = tally(sim, "clone spawn") {
                wlog(format!("{} CLONE SPAWN #{k} ({by}): unit #{id} for team {team} at {}: {}", head(sim, me), summon::pt(at),
                             spec.shown()));
            }
            Some(id)
        }
        None => {
            if let Some(k) = tally(sim, "clone fail") {
                wlog(format!("{} CLONE SPAWN FAILED #{k} ({by}): spawn_unit gave no unit for '{}' at {} - the clone rides on \
                              the target as before", head(sim, me), spec.name, summon::pt(at)));
            }
            None
        }
    }
}

/// `:clone` - the passive queues it when R is cast; the input is where the clone is to stand.
struct CloneFx;

impl StableEffectType for CloneFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = point(&input).or_else(|| sim.get_entity(caster).map(|e| pos(&e))) else { return };
        make_clone(sim, caster, at, "the queued effect");
    }
}

/// The blast at `at`: magic damage and a flame on every enemy but towers within `BOOM_R`, the mini boxes' fear, their
/// picture, and their shots queued. `me` deals it (alive or his body).
fn burst(sim: &mut StableSim<'_>, me: usize, at: Pt, why: &str) {
    let Some((team, ap)) = sim.get_entity(me).map(|e| (e.team(), e.stat().magic_power)) else {
        wlog(format!("{} CLONE BURST at {} ({why}): its Shaco #{me} is no entity any more - nothing dealt", head(sim, me),
                     summon::pt(at)));
        return;
    };
    // (id, where, a champion, not to be feared: crowd-control immune or an epic monster, name)
    let hit: Vec<(usize, Pt, bool, bool, String)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && summon::hittable(u))
        .filter(|u| len(sub(pos(u), at)) <= BOOM_R)
        .map(|u| (u.id(), pos(&u), u.is_champion(),
                  (0..u.buff_count()).filter_map(|i| u.buff_at(i)).any(|b| b.cc_immune)
                      || matches!(u.kind(), Some(EntityKindV1::Epic | EntityKindV1::Serpen)),
                  u.name().unwrap_or_default()))
        .collect();
    let damage = boom_damage(ap);
    let spot = at_input(at);
    sim.play_view_effect(BOOM_VIEW, me, &spot, 0, 0, 0);
    sim.play_sfx(BOOM_VIEW, me, &spot);
    sim.play_view_effect(MINI_VIEW, me, &spot, 0, 0, 0);
    sim.play_sfx(POP_SFX, me, &spot);
    let (mut champs, mut others, mut read_back) = (Vec::new(), 0usize, String::new());
    for (id, p, champion, unmoved, name) in &hit {
        sim.deal_damage_typed(me, *id, damage, DamageTypeV1::Ap, AttackTypeV1::Skill);
        sim.play_view_effect(BURN_VIEW, me, &InputTargetV1::target(*id), 0, 0, 0);
        if *unmoved || !sim.get_entity(*id).is_some_and(|e| e.is_alive()) {
            continue;
        }
        let mut fear = CcV1::of_kind(CcKindV1::Fear, if *champion { FEAR_CHAMP } else { FEAR_OTHER });
        (fear.dx, fear.dy) = away(at, *p);
        sim.apply_cc(*id, &fear);
        sim.play_view_effect(FEAR_VIEW, me, &InputTargetV1::target(*id), 0, 0, 0);
        if *champion {
            if champs.len() < 5 {
                champs.push(format!("#{id} {name} {:.0} away", len(sub(*p, at))));
            }
            if read_back.is_empty() {
                // what the engine made of the first fear (its direction's form is not written down anywhere)
                read_back = sim.get_entity(*id).map(|e| {
                    (0..e.cc_count()).filter_map(|i| e.cc_at(i)).filter(|c| c.kind == CcKindV1::Fear.code())
                        .map(|c| format!("; #{id}'s fear reads back as {} ticks toward ({},{}) (asked ({},{}))", c.tick, c.dx, c.dy,
                                         fear.dx, fear.dy))
                        .next().unwrap_or_else(|| format!("; #{id} shows no fear right after it was applied"))
                }).unwrap_or_default();
            }
        } else {
            others += 1;
        }
    }
    let queued = box_ticks().into_iter().filter(|t| sim.queue_effect(&fx("box"), AttackTypeV1::Skill, me, &spot, *t)).count();
    if let Some(k) = tally(sim, "clone burst") {
        wlog(format!("{} CLONE BURST #{k} at {} ({why}): {damage} magic to {} enemies within {BOOM_R:.0}; feared {FEAR_CHAMP} \
                      ticks: [{}], {FEAR_OTHER} ticks: {others} others{read_back}; {queued} of {BOX_SHOTS} box shots queued",
                     head(sim, me), summon::pt(at), hit.len(), champs.join(", ")));
    }
}

/// `:burst` - the clone's blast at the input point.
struct BurstFx;

impl StableEffectType for BurstFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = point(&input) else { return };
        burst(sim, caster, at, "queued");
    }
}

/// `:box` - one shot of the three mini boxes at the input point.
struct BoxFx;

impl StableEffectType for BoxFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let Some(at) = point(&input) else { return };
        let Some((team, ap)) = sim.get_entity(caster).map(|e| (e.team(), e.stat().magic_power)) else { return };
        let hit: Vec<(usize, bool, f64, String, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && summon::hittable(u))
            .filter(|u| len(sub(pos(u), at)) <= BOX_R)
            .map(|u| (u.id(), u.is_champion(), len(sub(pos(&u), at)), u.name().unwrap_or_default(),
                      (0..u.cc_count()).filter_map(|i| u.cc_at(i)).any(|c| c.kind == CcKindV1::Fear.code())))
            .collect();
        let damage = box_damage(ap);
        for (id, ..) in &hit {
            sim.deal_damage_typed(caster, *id, damage, DamageTypeV1::Ap, AttackTypeV1::Skill);
            sim.play_view_effect(SHOT_VIEW, caster, &InputTargetV1::target(*id), 0, 0, 0);
        }
        if let Some(k) = tally(sim, "clone box") {
            // the champions' distances from the blast shot by shot: a fear that works walks them away from it
            let champs: Vec<String> = hit.iter().filter(|h| h.1).take(5)
                .map(|h| format!("#{} {} {:.0} away{}", h.0, h.3, h.2, if h.4 { " (feared)" } else { "" })).collect();
            wlog(format!("{} CLONE BOX #{k} at {}: {damage} magic to {} enemies within {BOX_R:.0}; champions: [{}]",
                         head(sim, caster), summon::pt(at), hit.len(), champs.join(", ")));
        }
    }
}

/// `:end` - queued when he dies with his clone out, for 2 ticks before its time; the input is the clone. It bursts
/// where it stands if it still stands (killed meanwhile: nobody watched, no blast).
struct EndFx;

impl StableEffectType for EndFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Target) {
            return;
        }
        let id = input.target_id;
        let team = sim.get_entity(caster).map(|e| e.team());
        let name = KNOBS.name.as_deref().unwrap_or(CLONE_NAME);
        // his clone still: alive, of his team, under the clone's name, no champion (his own next life could get the id)
        let at = sim.get_entity(id).filter(|e| {
            id != caster && e.is_alive() && Some(e.team()) == team && e.kind() != Some(EntityKindV1::Champion)
                && e.name().unwrap_or_default() == name
        }).map(|e| pos(&e));
        match at {
            Some(at) => burst(sim, caster, at, "its time is up, Shaco is dead"),
            None => {
                if let Some(k) = tally(sim, "clone end") {
                    wlog(format!("{} CLONE END #{k}: the clone #{id} of the dead Shaco is gone before its time - no blast",
                                 head(sim, caster)));
                }
            }
        }
    }
}

// ===================== 被动 =====================

/// His clone as a unit, as the passive keeps it.
#[derive(Clone, Debug)]
struct Live {
    unit: summon::Unit,
    /// The health it was to start with (his own then), and whether the look after the dressing was logged.
    hp_goal: usize,
    dressed: bool,
}

#[derive(Clone, Default)]
struct Backstab {
    p: Vec<(String, usize)>,
    trails: HashMap<usize, VecDeque<Pt>>,
    asked: usize,
    stabs: usize,
    /// His own unit (on_dead is given the player).
    me: usize,
    /// The tick a clone was asked for, while its handoff is awaited.
    wait: Option<usize>,
    /// A handed-over unit not yet read as one: (id, the tick it was asked for, looks so far).
    fresh: Option<(usize, usize, usize)>,
    clone: Option<Live>,
    wake: Option<summon::Wake>,
    clones: usize,
    /// 0.3.0: his boxes' bodies (jack.rs).
    jacks: jack::Jacks,
}

impl Backstab {
    /// A line for a hook that fired while the clone is out.
    fn hooked(&self, sim: &StableSim<'_>, hook: &str, entity: usize, other: usize, damage: Option<usize>) {
        let Some(live) = &self.clone else { return };
        if let Some(k) = tally(sim, "clone hook") {
            wlog(format!("{} CLONE #{} HOOK #{k} {hook}: {}{}", head(sim, self.me), live.unit.n,
                         live.unit.hook_text(sim, entity, other, self.me), damage.map(|d| format!(", damage {d}")).unwrap_or_default()));
        }
    }

    /// The clone's part of a tick: R's ask, the handoff, the look at the unit, its end.
    #[allow(clippy::too_many_arguments)]
    fn clone_tick(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize, here: Pt, team: usize, hp: usize, r_cast: bool) {
        let tick = sim.tick();
        if r_cast {
            sim.entity_remove_buff(me, R_ASK);
            if KNOBS.off {
                if let Some(k) = tally(sim, "clone off") {
                    wlog(format!("{} CLONE OFF #{k}: R cast, unit=off in the test knobs - the clone rides on the target as before",
                                 head(sim, me)));
                }
            } else {
                // beside him, across the line to the nearest living enemy champion
                let toward = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                    .filter(|u| u.team() != team && u.is_champion() && u.is_alive())
                    .map(|u| pos(&u))
                    .min_by(|a, b| len(sub(*a, here)).total_cmp(&len(sub(*b, here))));
                // never outside the box round the units the engine holds (a point off the map's grid is not for a pilot
                // to try): of his two sides the one that keeps its distance there, the usual one first
                let field = summon::field(sim);
                let (a, b) = (summon::inside(field, beside(here, toward, self.clones)),
                              summon::inside(field, beside(here, toward, self.clones + 1)));
                let at = if len(sub(b, here)) > len(sub(a, here)) + 1.0 { b } else { a };
                let queued = sim.queue_effect(&fx("clone"), AttackTypeV1::Skill, me, &at_input(at), 1);
                if !queued {
                    make_clone(sim, me, at, "queue_effect refused: spawned by the passive");
                }
                self.wait = Some(tick);
                if let Some(k) = tally(sim, "clone ask") {
                    wlog(format!("{} CLONE ASK #{k}: R cast at {}, the clone asked for at {} ({:.0} beside him, across the \
                                  line to {}){}", head(sim, me), summon::pt(here), summon::pt(at), len(sub(at, here)),
                                 toward.map_or("the east (no enemy champion alive)".to_string(),
                                               |t| format!("the nearest enemy champion at {}", summon::pt(t))),
                                 if queued { "" } else { " - queue_effect REFUSED" }));
                }
            }
        }
        if let Some(since) = self.wait {
            if let Some(id) = summon::take_handoff(sim, me, R_UID) {
                // its time counted from the ask - the spawn is a tick or two later, so a blast queued by that count
                // (`:end`, when he is dead) comes a tick or two early, never after the unit is gone
                (self.wait, self.fresh) = (None, Some((id, since, 0)));
            } else if tick > since + ASK_WAIT {
                self.wait = None;
                if let Some(k) = tally(sim, "clone none") {
                    wlog(format!("{} CLONE NONE #{k}: no unit came within {ASK_WAIT} ticks of the ask - the clone rides on the \
                                  target as before", head(sim, me)));
                }
            }
        }
        if let Some((id, born, tries)) = self.fresh {
            match summon::Unit::look(sim, id, self.clones + 1, born, CLONE_LIFE, team, player) {
                Ok((mut unit, line)) => {
                    self.fresh = None;
                    self.clones += 1;
                    // dressed here, where it reads as a unit: +50 % damage taken, his own health now
                    let mut worse = BuffV1::named(CLONE_BUFF);
                    worse.damaged_amplify = CLONE_TAKES;
                    sim.add_buff(id, &worse);
                    let (had, hp_goal) = (unit.hp, hp.clamp(1, unit.max.max(1)));
                    let set = hp_goal < had && sim.entity_set_hp(id, hp_goal);
                    if set {
                        unit.health_set(hp_goal);
                    }
                    let on = InputTargetV1::target(id);
                    sim.play_view_effect(APPEAR_VIEW, me, &on, 0, 0, 0);
                    sim.play_sfx(APPEAR_SFX, me, &on);
                    if let Some(k) = tally(sim, "clone look") {
                        wlog(format!("{} CLONE #{} LOOK #{k}: {line}; given +{CLONE_TAKES}% damage taken; health to his own \
                                      {hp_goal}: {}", head(sim, me), self.clones,
                                     if set { "set" } else if hp_goal >= had { "it has no more" } else { "entity_set_hp REFUSED" }));
                    }
                    self.clone = Some(Live { unit, hp_goal, dressed: false });
                }
                Err(why) if tries + 1 >= LOOK_TRIES => {
                    self.fresh = None;
                    sim.entity_remove_buff(me, R_UNIT);
                    if let Some(k) = tally(sim, "clone lost") {
                        wlog(format!("{} CLONE LOST #{k}: the unit spawn_unit named never read as one in {LOOK_TRIES} ticks \
                                      ({why}) - the flag is off, the clone rides on the target as before", head(sim, me)));
                    }
                }
                Err(_) => self.fresh = Some((id, born, tries + 1)),
            }
            return;
        }
        if let Some(mut live) = self.clone.take() {
            let n = live.unit.n;
            if !live.dressed {
                live.dressed = true;
                let seen = sim.get_entity(live.unit.id).map(|e| (has_buff(&e, CLONE_BUFF), e.hp()));
                if let (Some(k), Some((worse, (now, max)))) = (tally(sim, "clone dress"), seen) {
                    wlog(format!("{} CLONE #{n} DRESS #{k}: a tick on, the +{CLONE_TAKES}% damage taken buff {} on it, its \
                                  health {now}/{max} (asked {})", head(sim, me), if worse { "is" } else { "is NOT" },
                                 live.hp_goal));
                }
            }
            match live.unit.step(sim, Some(here)) {
                summon::Step::Alive(line) => {
                    if let (Some(line), Some(k)) = (line, tally(sim, "clone unit")) {
                        wlog(format!("{} CLONE #{n} #{k}: {line}", head(sim, me)));
                    }
                    self.clone = Some(live);
                }
                summon::Step::Over(end) => {
                    if let Some(k) = tally(sim, "clone over") {
                        wlog(format!("{} CLONE #{n} OVER #{k}: {}", head(sim, me), end.text));
                    }
                    if end.age <= LOST_AGE {
                        // never really there: the data has not read the flag yet, so its clone can still play
                        sim.entity_remove_buff(me, R_UNIT);
                        wlog(format!("{} CLONE #{n}: gone {} ticks after it was asked for - no blast, the flag is off, the \
                                      clone rides on the target as before", head(sim, me), end.age));
                    } else if !sim.queue_effect(&fx("burst"), AttackTypeV1::Skill, me, &at_input(end.at), 1) {
                        burst(sim, me, end.at, "queue_effect refused: by the passive");
                    }
                    self.wake = Some(live.unit.wake(sim, &end));
                }
            }
        }
        if let Some(mut w) = self.wake.take() {
            let (lines, over) = w.step(sim);
            for line in lines {
                if let Some(k) = tally(sim, "clone wake") {
                    wlog(format!("{} CLONE #{} WAKE #{k}: {line}", head(sim, me), w.n));
                }
            }
            if !over {
                self.wake = Some(w);
            }
        }
    }
}

impl StablePassive for Backstab {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        // the params in the first SPAWN line of a launch only; the line itself capped in the presims
        let params = params_new(&self.p).then(|| format!(", {:?}", self.p));
        if tally(sim, "spawn").is_some() || params.is_some() {
            wlog(format!("{} SPAWN: the add-on's Shaco (player {player}){}", head(sim, me), params.unwrap_or_default()));
        }
        // a new life is a new entity: nothing of the old one's clone is his any more (on_dead queued its end)
        if let Some(live) = self.clone.take() {
            wlog(format!("{} CLONE #{}: still on the books at his respawn (his death did not reach on_dead) - let go",
                         head(sim, me), live.unit.n));
        }
        (self.me, self.wait, self.fresh, self.wake) = (me, None, None, None);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        let me_now = sim.get_player(player).and_then(|p| p.champion()).map_or(self.me, |e| e.id());
        self.jacks.on_dead(sim, me_now);
        (self.wait, self.fresh, self.wake) = (None, None, None);
        let Some(live) = self.clone.take() else { return };
        let me = sim.get_player(player).and_then(|p| p.champion()).map_or(self.me, |e| e.id());
        let (tick, u) = (sim.tick(), &live.unit);
        // a dead champion's passive does not run: the clone fights on by itself, and a queued effect (they do run for a
        // dead caster) bursts it just before its time
        let left = u.left(tick);
        let queued = if left > END_BEFORE {
            sim.queue_effect(&fx("end"), AttackTypeV1::Skill, me, &InputTargetV1::target(u.id), left - END_BEFORE)
        } else {
            sim.queue_effect(&fx("burst"), AttackTypeV1::Skill, me, &at_input(u.at), 1)
        };
        if let Some(k) = tally(sim, "clone dead") {
            wlog(format!("{} CLONE #{} ORPHAN #{k}: Shaco died, his clone #{} at {} has {left} ticks left and hp {}/{} - it \
                          fights on unwatched; its blast {}", head(sim, me), u.n, u.id, summon::pt(u.at), u.hp, u.max,
                         if queued { "is queued for its time" } else { "was REFUSED (queue_effect): none" }));
        }
    }

    // While his clone is out, what the engine tells his passive: do the clone's hits and kills come here, and under
    // whose id? (the answer for every summon that is to carry its summoner's marks or stacks)
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, target: usize, damage: &mut usize) {
        self.hooked(sim, "on_attack", entity, target, Some(*damage));
        self.jacks.hooked(sim, "on_attack", self.me, entity, target, Some(*damage));
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_kill", entity, victim, None);
    }

    fn on_unit_kill(&mut self, sim: &mut StableSim<'_>, _: usize, entity: usize, victim: usize) {
        self.hooked(sim, "on_unit_kill", entity, victim, None);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, at, attack, hp, r_ask) = (e.team(), pos(&e), e.stat().attack, e.hp().0, has_buff(&e, R_ASK));
        self.me = me;
        let mine: Vec<Pt> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() == team && u.is_alive() && (u.is_champion() || u.is_minion()))
            .map(|u| pos(&u)).collect();
        let foes: Vec<(usize, Pt, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_champion())
            .map(|u| (u.id(), pos(&u), u.is_alive() && has_buff(&u, ASK)))
            .collect();
        let mut asks = Vec::new();
        for (id, p, ask) in &foes {
            let t = self.trails.entry(*id).or_default();
            if t.back().is_some_and(|b| len(sub(*b, *p)) > 20_000.0) {
                t.clear(); // a recall, a respawn or a blink: no walking direction across it
            }
            t.push_back(*p);
            while t.len() > TRACK {
                t.pop_front();
            }
            if *ask {
                let near = mine.iter().copied().min_by(|a, b| len(sub(*a, *p)).total_cmp(&len(sub(*b, *p))));
                asks.push((*id, *p, facing(t, near)));
            }
        }
        // a respawn is a new entity with a new id: the trails of ids no enemy champion has any more go
        if self.trails.len() > foes.len() {
            self.trails.retain(|id, _| foes.iter().any(|f| f.0 == *id));
        }
        let damage = get(&self.p, "base", 15) + attack * get(&self.p, "ad", 25) / 100;
        for (id, p, face) in asks {
            sim.entity_remove_buff(id, ASK);
            self.asked += 1;
            let Some(face) = face else { continue };
            if !behind(p, face, at) {
                continue;
            }
            sim.deal_damage_typed(me, id, damage, DamageTypeV1::Ad, AttackTypeV1::Skill);
            sim.play_view_effect(VIEW, me, &InputTargetV1::target(id), 0, 0, 0);
            sim.play_sfx(VIEW, me, &InputTargetV1::target(id));
            self.stabs += 1;
            if let Some(k) = tally(sim, "backstab") {
                wlog(format!("{} BACKSTAB #{k} on #{id}: +{damage} physical ({} of {} hits from behind)", head(sim, me),
                             self.stabs, self.asked));
            }
        }
        self.clone_tick(sim, player, me, at, team, hp, r_ask);
        self.jacks.tick(sim, me, player, team, at);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Shaco's Backstab from behind, by where the target faces; his clone a unit of its own) loaded: \
         game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    wlog(format!(
        "CLONE: Hallucinate's clone is a unit ('{}', spawn_unit) - {}; {CLONE_LIFE} ticks, {CLONE_HIT} + {CLONE_HIT_AD}% of his \
         attack a hit, +{CLONE_TAKES}% damage taken, the blast {BOOM} + {BOOM_AP}% of his ability power. Test knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(CLONE_NAME),
        if KNOBS.off { "OFF by the test knobs: the clone rides on the target as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(),
        KNOBS.shown()
    ));
    wlog(format!(
        "JACK: Jack in the Box has a body of its own ('{}', spawn_unit: move speed 1, a harmless shot, {}% of his health, banished \
         until it springs) - {}; the add-on fires its {} volleys ({} + {}% of his ability power), a broken box stops.",
        jack::JACK, jack::JACK_HP_PCT, if KNOBS.off { "OFF by the test knobs: the main pack's box" } else { "ON" }, jack::W_SHOTS,
        jack::W_HIT, jack::W_HIT_AP
    ));
    module.add_native_passive(format!("{ID}:backstab"), Backstab::default());
    module.add_native_effect(fx("clone"), CloneFx);
    module.add_native_effect(fx("burst"), BurstFx);
    module.add_native_effect(fx("box"), BoxFx);
    module.add_native_effect(fx("end"), EndFx);
    module.add_native_effect(fx("jack"), jack::JackFx);
    module.add_native_effect(fx("jack_shot"), jack::ShotFx);
    host.log(LogLevel::Info, "league_shaco_backstab v2 loaded (Backstab from behind; the clone as a unit).");
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
#[path = "summon_mock.rs"]
mod mock;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn walking_away_shows_his_back() {
        let t: VecDeque<Pt> = (0..10).map(|k| (k as f64 * 300.0, 0.0)).collect();
        let f = facing(&t, None).unwrap();
        assert!(f.0 > 0.0);
        // Shaco chasing him from the left: behind; in front on the right: not
        assert!(behind((2_700.0, 0.0), f, (-5_000.0, 0.0)));
        assert!(!behind((2_700.0, 0.0), f, (9_000.0, 0.0)));
    }

    #[test]
    fn standing_he_faces_the_nearest_foe() {
        let t: VecDeque<Pt> = (0..10).map(|_| (0.0, 0.0)).collect();
        let f = facing(&t, Some((10_000.0, 0.0))).unwrap();
        assert!(behind((0.0, 0.0), f, (-8_000.0, 1_000.0)));
        assert!(!behind((0.0, 0.0), f, (8_000.0, 0.0)));
        assert_eq!(facing(&t, None), None);
    }

    #[test]
    fn presim_lines_are_capped_for_the_launch_and_the_match_on_screen_is_not() {
        let logged: Vec<usize> = (0..LOG_EVERY * 3).filter_map(|_| noted("test presim", false)).collect();
        assert_eq!(logged.len(), LOG_FIRST + 3);
        assert_eq!(logged[LOG_FIRST..], [LOG_EVERY, LOG_EVERY * 2, LOG_EVERY * 3]);
        assert!((0..LOG_EVERY * 2).all(|_| noted("test shown", true).is_some()));
    }

    #[test]
    fn the_params_are_logged_once() {
        let p = params(r#"{"ad":25,"base":15}"#);
        assert!(params_new(&p));
        assert!(!params_new(&p));
        assert!(params_new(&params(r#"{"ad":30,"base":15}"#)), "other params: again");
    }

    #[test]
    fn the_clone_appears_beside_him() {
        let here = (300_000.0, 300_000.0);
        // the enemy east of him: the clone 14000 south of him, the next one 14000 north - shoulder to shoulder
        assert_eq!(beside(here, Some((350_000.0, 300_000.0)), 0), (300_000.0, 314_000.0));
        assert_eq!(beside(here, Some((350_000.0, 300_000.0)), 1), (300_000.0, 286_000.0));
        // wherever the enemy stands: SIDE from him, at a right angle to the line between them
        for foe in [(350_000.0, 340_000.0), (100_000.0, 290_000.0), (300_000.0, 900_000.0)] {
            let at = beside(here, Some(foe), 0);
            assert!((len(sub(at, here)) - SIDE).abs() < 1.0);
            let (a, b) = (sub(at, here), sub(foe, here));
            assert!((a.0 * b.0 + a.1 * b.1).abs() < 1.0, "not across the line to {foe:?}");
        }
        // no enemy champion, or one on his very spot: as if he faced east
        assert_eq!(beside(here, None, 0), (300_000.0, 314_000.0));
        assert_eq!(beside(here, Some(here), 1), (300_000.0, 286_000.0));
        // never off the map's top or left edge
        assert_eq!(beside((5_000.0, 5_000.0), Some((90_000.0, 5_000.0)), 1), (5_000.0, 0.0));
    }

    #[test]
    fn the_clone_is_him_with_weaker_hits() {
        let his = StatV1 { attack: 200, magic_power: 60, hp: 900, defence: 44, magic_resistance: 24, move_speed: 1150, hp_regen: 7,
                           stack: 3, crit_chance: 25 };
        let spec = clone_spec(&his, 1500);
        assert_eq!(spec.name, "league_shaco");
        assert_eq!(spec.life, 312);
        assert_eq!(spec.stat, StatV1 { attack: 200, magic_power: 60, hp: 1500, defence: 44, magic_resistance: 24, move_speed: 1150,
                                       hp_regen: 0, stack: 0, crit_chance: 0 });
        // a hit: 10 + 40 % of 200 = 90 (his own: 200)
        let a = spec.attack;
        assert_eq!(a.attack + spec.stat.attack * a.attack_ratio / 100, 90);
        assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (23_000, 52, 22, 9));
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        assert_eq!(a.attack_type, AttackTypeV1::BaseAttack.code());
        // never a unit of no health
        assert_eq!(clone_spec(&his, 0).stat.hp, 1);
    }

    #[test]
    fn the_blast_and_the_boxes_are_the_main_packs_numbers() {
        assert_eq!(boom_damage(0), 150);
        assert_eq!(boom_damage(120), 270);
        assert_eq!(box_damage(120), 20);
        assert_eq!(box_ticks(), [1, 31, 61, 91, 121]);
        assert!(*box_ticks().last().unwrap() <= 150, "the main pack's boxes shoot for 150 ticks");
    }

    #[test]
    fn a_fear_always_has_a_way_to_run() {
        assert_eq!(away((100.0, 100.0), (400.0, 100.0)), (1000, 0));
        assert_eq!(away((100.0, 100.0), (100.0, 40.0)), (0, -1000));
        assert_eq!(away((0.0, 0.0), (30_000.0, 40_000.0)), (600, 800));
        assert_eq!(away((100.0, 100.0), (100.0, 100.0)), (1000, 0));
        assert_eq!(away((100.2, 100.2), (100.0, 100.0)), (1000, 0));
    }

    #[test]
    fn the_flag_outlasts_the_datas_check_and_a_lost_unit_is_told_before_it() {
        // the data reads the flag 12 ticks after the cast; the unit comes at most 3 ticks after it and is handed over a
        // tick or two later: a unit gone by LOST_AGE takes the flag off before the data looks
        assert!(3 + LOST_AGE < 12);
        assert!(ASK_WAIT + LOOK_TRIES < 12);
        assert!(UID_TICKS > 2);
        assert!(CLONE_LIFE + FLAG_MORE > CLONE_LIFE);
        assert!(END_BEFORE >= 1 && END_BEFORE < summon::TIME_SLACK + 2);
        for name in [R_ASK, R_UNIT, CLONE_BUFF, &summon::handoff(R_UID, usize::MAX)] {
            assert!(name.len() <= BUFF_NAME_CAP, "{name}");
        }
    }

    // ---- the clone on the mock world (summon_mock.rs: our guess of the host, to check this side's logic) ----

    use super::mock::{champion, unit, MPlayer, World};

    const GAREN: usize = 1;
    const MINION: usize = 2;

    /// The test log, set before anything logs (the log's path is read once a process).
    fn log_file() -> PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_shaco_backstab_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_SHACO_BACKSTAB_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// Shaco #0 (team 0) has walked right to (300000, 300000); Garen #1 (team 1) stands 50000 east of him, an enemy
    /// minion #2 far to the south; a player each.
    fn world() -> (World, Backstab) {
        log_file();
        let mut w = World::default();
        let mut shaco = champion("league_shaco", 0, 300_000.0 - 30.0 * 1_100.0, 300_000.0);
        (shaco.hp, shaco.max) = (600, 1000);
        w.units = vec![shaco, champion("league_garen", 1, 350_000.0, 300_000.0),
                       unit("melee_minion", EntityKindV1::Minion, 1, 300_000.0, 500_000.0, 300)];
        w.players = vec![MPlayer { team: 0, champion: 0, gold: 500, cs: 10, kills: 0, deal: 0 },
                         MPlayer { team: 1, champion: GAREN, gold: 700, cs: 20, kills: 1, deal: 0 }];
        let mut me = Backstab::default();
        w.sim(|sim| me.on_spawn(sim, 0, 0));
        for _ in 0..30 {
            w.units[0].x += 1_100.0;
            tick(&mut w, &mut me);
        }
        (w, me)
    }

    /// One tick: the queued effects due, his passive while he lives, the world's own step.
    fn tick(w: &mut World, me: &mut Backstab) {
        for (name, caster, input) in w.due() {
            w.sim(|sim| match name.as_str() {
                "league_shaco_backstab:clone" => CloneFx.apply(sim, 0, caster, input),
                "league_shaco_backstab:burst" => BurstFx.apply(sim, 0, caster, input),
                "league_shaco_backstab:box" => BoxFx.apply(sim, 0, caster, input),
                "league_shaco_backstab:end" => EndFx.apply(sim, 0, caster, input),
                other => panic!("an effect nobody registered: {other}"),
            });
        }
        if w.units[0].hp > 0 {
            w.sim(|sim| me.on_update(sim, 0, 0, 0));
        }
        w.step();
    }

    fn run(w: &mut World, me: &mut Backstab, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    /// The copy's R as the data lays it: the ask on him.
    fn cast_r(w: &mut World) -> usize {
        w.units[0].buffs.push((BuffV1::timed(R_ASK, 3), 3));
        w.tick
    }

    /// The blasts so far: (tick, target, amount) of his magic damage of the blast's size.
    fn blasts(w: &World, ap: usize) -> Vec<(usize, usize)> {
        w.damage.iter().filter(|d| d.1 == 0 && d.4 == DamageTypeV1::Ap.code() && d.3 == boom_damage(ap)).map(|d| (d.0, d.2)).collect()
    }

    #[test]
    fn the_clone_never_appears_outside_the_field() {
        // Garen west of him: the first clone's side is north of him - but he is the northernmost of all, so that
        // point lies outside the box round everybody: the other side it is
        let (mut w, mut me) = world();
        w.units[GAREN].x = 250_000.0;
        cast_r(&mut w);
        run(&mut w, &mut me, 3);
        assert_eq!(w.spawns.len(), 1);
        assert_eq!(w.spawns[0].at, (300_000, 314_000));
        // everybody on one row: no room on either side, the clone appears where he stands (ground for sure)
        let (mut w, mut me) = world();
        (w.units[2].x, w.units[2].y) = (100_000.0, 300_000.0);
        cast_r(&mut w);
        run(&mut w, &mut me, 3);
        assert_eq!(w.spawns.len(), 1);
        assert_eq!(w.spawns[0].at, (300_000, 300_000));
    }

    #[test]
    fn the_clone_is_a_unit_that_walks_fights_and_bursts() {
        let (mut w, mut me) = world();
        let t0 = cast_r(&mut w);
        run(&mut w, &mut me, 12);
        // one spawn_unit: his own name, his team, 14000 beside him (Garen is east: south of him), his numbers with the
        // clone's hits
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life), ("league_shaco", 0, 0, 312));
        assert_eq!(s.at, (300_000, 314_000));
        assert!(s.tick <= t0 + 3, "spawned {} ticks after the cast", s.tick - t0);
        assert_eq!((s.stat.attack, s.stat.hp, s.stat.move_speed), (100, 1000, 1100));
        assert_eq!((s.attack.attack, s.attack.attack_ratio, s.attack.range, s.attack.cooltime), (10, 40, 23_000, 52));
        let clone = s.gave.unwrap();
        // the data reads the flag 12 ticks after the cast: it is there, and stays for the clone's time
        assert!(w.has(0, R_UNIT), "no flag on him when the data looks");
        assert!(!w.has(0, R_ASK) && !w.units[0].buffs.iter().any(|b| b.0.name().starts_with(R_UID)));
        // dressed: +50 % damage taken, his own health (600 of 1000)
        assert!(w.has(clone, CLONE_BUFF));
        assert_eq!((w.units[clone].hp, w.units[clone].max), (600, 1000));
        w.hurt(clone, 100);
        assert_eq!(w.units[clone].hp, 450);
        assert_eq!((w.viewed(APPEAR_VIEW), w.heard(APPEAR_SFX)), (1, 1));
        // it walks to Garen and hits him: 10 + 40 % of 100 each, no faster than his own attack
        run(&mut w, &mut me, 290);
        let hits = w.dealt(clone, DamageTypeV1::Ad);
        assert!(hits.len() >= 4 && hits.len() <= 6, "{} hits", hits.len());
        assert!(hits.iter().all(|h| *h == (GAREN, 50)));
        assert!(blasts(&w, 30).is_empty(), "burst before its end");
        assert!(w.has(0, R_UNIT));
        // its time is up: one blast where it stood - Garen within 30000 takes 150 + 100 % of 30, is feared away from it;
        // the minion far away is not touched
        run(&mut w, &mut me, 30);
        assert!(!w.units[clone].valid);
        let b = blasts(&w, 30);
        assert_eq!(b.len(), 1, "{b:?}");
        assert_eq!(b[0].1, GAREN);
        assert!(b[0].0 >= t0 + 312 && b[0].0 <= t0 + 318, "the blast {} ticks after the cast", b[0].0 - t0);
        assert_eq!((w.viewed(BOOM_VIEW), w.viewed(MINI_VIEW), w.viewed(BURN_VIEW), w.viewed(FEAR_VIEW)), (1, 1, 1, 1));
        assert_eq!((w.heard(BOOM_VIEW), w.heard(POP_SFX)), (1, 1));
        assert_eq!(w.fears.len(), 1);
        let (_, who, fear) = w.fears[0];
        assert_eq!((who, fear.tick), (GAREN, FEAR_CHAMP));
        assert!(fear.dx > 0 && fear.dy < 0, "Garen stands north-east of the clone: he runs that way ({}, {})", fear.dx, fear.dy);
        // the mini boxes: five shots of 8 + 10 % of 30 over the next 121 ticks
        run(&mut w, &mut me, 130);
        let shots: Vec<_> = w.dealt(0, DamageTypeV1::Ap).into_iter().filter(|d| d.1 == box_damage(30)).collect();
        assert_eq!(shots, vec![(GAREN, 11); 5]);
        assert_eq!(w.viewed(SHOT_VIEW), 5);
        assert_eq!(blasts(&w, 30).len(), 1, "a second blast");
        assert!(!w.dealt(0, DamageTypeV1::Ap).iter().any(|d| d.0 == MINION));
        // nothing left over: no clone on the books, the queue empty, the flag gone with its time
        run(&mut w, &mut me, 200);
        assert!(me.clone.is_none() && me.wake.is_none() && me.wait.is_none() && me.fresh.is_none());
        assert!(w.queue.is_empty() && !w.has(0, R_UNIT));
        assert_eq!(me.clones, 1);
    }

    #[test]
    fn a_killed_clone_bursts_where_it_fell_once() {
        for body_ticks in [0, 60] {
            let (mut w, mut me) = world();
            w.body_ticks = body_ticks;
            let t0 = cast_r(&mut w);
            run(&mut w, &mut me, 100);
            let clone = w.spawns[0].gave.unwrap();
            let at = (w.units[clone].x, w.units[clone].y);
            w.players[1].gold += 37;
            w.players[1].cs += 1;
            w.hurt(clone, 10_000);
            run(&mut w, &mut me, 5);
            let b = blasts(&w, 30);
            assert_eq!(b.len(), 1, "body {body_ticks}: {b:?}");
            assert!(b[0].0 > t0 + 100 && b[0].0 <= t0 + 104);
            assert_eq!(w.views.iter().find(|v| v.1 == BOOM_VIEW).map(|v| (v.2.x, v.2.y)), Some((at.0.round() as u64, at.1.round() as u64)));
            run(&mut w, &mut me, 400);
            assert_eq!(blasts(&w, 30).len(), 1, "body {body_ticks}: burst again at its time");
            assert!(me.clone.is_none() && me.wake.is_none() && w.queue.is_empty());
        }
    }

    #[test]
    fn no_unit_from_the_host_leaves_the_data_its_clone() {
        // no such slot (an older host), a refusal, an id that never reads as a unit, a unit gone at once
        for case in 0..4 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                2 => w.spawn_never = true,
                _ => {}
            }
            let t0 = cast_r(&mut w);
            if case == 3 {
                run(&mut w, &mut me, 3);
                assert!(w.has(0, R_UNIT) && me.clone.is_some());
                let id = w.spawns[0].gave.unwrap();
                w.units[id].valid = false;
            }
            while w.tick < t0 + 12 {
                tick(&mut w, &mut me);
            }
            // the data looks now: no flag, so the clone riding on the target plays as it always did
            assert!(!w.has(0, R_UNIT), "case {case}: the flag is on him when the data looks - no clone at all");
            run(&mut w, &mut me, 400);
            assert!(blasts(&w, 30).is_empty(), "case {case}: a blast without a clone");
            assert!(me.clone.is_none() && me.wait.is_none() && me.fresh.is_none() && w.queue.is_empty(), "case {case}");
            assert_eq!(w.spawns.len(), if case == 0 { 0 } else { 1 }, "case {case}");
        }
    }

    #[test]
    fn a_host_that_queues_nothing_or_adds_the_unit_late_still_gets_its_clone() {
        // queue_effect refused: the passive spawns and bursts itself (no box shots: they are queued ones)
        let (mut w, mut me) = world();
        w.queue_ok = false;
        cast_r(&mut w);
        run(&mut w, &mut me, 12);
        assert_eq!(w.spawns.len(), 1);
        assert!(w.has(0, R_UNIT) && me.clone.is_some());
        run(&mut w, &mut me, 320);
        assert_eq!(blasts(&w, 30).len(), 1);
        assert_eq!(w.viewed(SHOT_VIEW), 0);
        // the unit readable only a tick after spawn_unit returned its id: looked at again, then kept
        let (mut w, mut me) = world();
        w.spawn_late = true;
        cast_r(&mut w);
        run(&mut w, &mut me, 12);
        assert!(w.has(0, R_UNIT) && me.clone.is_some());
        assert!(w.has(w.spawns[0].gave.unwrap(), CLONE_BUFF));
        run(&mut w, &mut me, 320);
        assert_eq!(blasts(&w, 30).len(), 1);
    }

    #[test]
    fn the_clone_outlives_him_and_still_bursts_at_its_time() {
        let (mut w, mut me) = world();
        let t0 = cast_r(&mut w);
        run(&mut w, &mut me, 100);
        let clone = w.spawns[0].gave.unwrap();
        // Shaco dies: his passive stops, the clone fights on
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.on_dead(sim, 0));
        assert!(me.clone.is_none());
        let before = w.dealt(clone, DamageTypeV1::Ad).len();
        run(&mut w, &mut me, 150);
        assert!(w.dealt(clone, DamageTypeV1::Ad).len() > before, "the clone stopped fighting when he died");
        assert!(blasts(&w, 30).is_empty());
        run(&mut w, &mut me, 70);
        let b = blasts(&w, 30);
        assert_eq!(b.len(), 1, "{b:?}");
        assert!(b[0].0 >= t0 + 306 && b[0].0 <= t0 + 312, "the blast {} ticks after the cast", b[0].0 - t0);
        run(&mut w, &mut me, 200);
        assert_eq!(blasts(&w, 30).len(), 1);
        assert!(w.queue.is_empty());
        // killed while he is dead: nobody watched it, no blast
        let (mut w, mut me) = world();
        cast_r(&mut w);
        run(&mut w, &mut me, 100);
        let clone = w.spawns[0].gave.unwrap();
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.on_dead(sim, 0));
        run(&mut w, &mut me, 50);
        w.hurt(clone, 10_000);
        run(&mut w, &mut me, 300);
        assert!(blasts(&w, 30).is_empty());
        assert!(w.queue.is_empty());
    }

    #[test]
    fn the_log_tells_a_clones_whole_life() {
        let (mut w, mut me) = world();
        let t0 = cast_r(&mut w);
        run(&mut w, &mut me, 200);
        let clone = w.spawns[0].gave.unwrap();
        // the engine telling his passive of a hit under the clone's id, and of a minion kill under his own
        let mut dealt = 50;
        w.sim(|sim| me.on_attack(sim, 0, clone, GAREN, &mut dealt));
        w.sim(|sim| me.on_unit_kill(sim, 0, 0, MINION));
        w.body_ticks = 40;
        w.players[1].gold += 25;
        w.hurt(clone, 10_000);
        run(&mut w, &mut me, 300);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" CLONE ")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "CLONE ASK #", "the clone asked for at (300000,314000) (14000 beside him, across the line to the nearest enemy champion at \
             (350000,300000))",
            "CLONE SPAWN #", "'league_shaco' for 312 ticks, attack 100 ap 30 hp 1000 def 20 mr 20 speed 1100; hits 10 + 40% of its attack, \
             range 23000, every 52 ticks (22 long, lands at 9)",
            "LOOK #", "reads back as name 'league_shaco' kind summon team 0 champion=false", "health to his own 600: set",
            "DRESS #", "the +50% damage taken buff is on it, its health 600/1000",
            " of 312 ticks, at (", "near it: champion #1 league_garen",
            "OVER #", "KILLED after 200 of 312 ticks", "its dead body is still there", "p1 gold +25",
            "its summoner's damage statistic +50 in the second (now 50)", "its summoner's damage statistic +200 over its life (now 200)",
            "CLONE BURST #", "180 magic to 1 enemies within 30000", "feared 45 ticks: [#1 league_garen",
            "#1's fear reads back as 45 ticks toward (", "5 of 5 box shots queued",
            "CLONE BOX #", "11 magic to 1 enemies within 32000", "(feared)",
            "HOOK #", "on_attack: entity #3 (the unit itself) -> champion #1 league_garen, ", " from the unit, 50000 from its summoner, damage 50",
            "on_unit_kill: entity #0 (its summoner) -> minion #2 melee_minion, ", " from the unit, 200000 from its summoner",
            "WAKE #", "its body was there for 41 ticks after its end", "the enemy players from the tick before its end to 3 ticks after",
            " from where it stood a second ago), hp 600/1000 (+0 in the second), ",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        // every line carries where it ran, and none is long
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
        let longest = mine.iter().map(|l| l.len()).max().unwrap();
        assert!(longest < 700, "a line of {longest} bytes");
        // one line a second while it lived: 200 ticks -> 3
        let unit_lines = mine.iter().filter(|l| l.contains(&format!("t={}", t0 + 61)) || l.contains(" of 312 ticks, at (")).count();
        assert!(unit_lines >= 3, "{unit_lines} lines of the living clone");
    }
}
