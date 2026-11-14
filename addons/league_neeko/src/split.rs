//! 两生花影的主动（W）：附加包自己放的技能，分身是真的单位（0.2.0，2026-11-14）。
//!
//! 用户 11-14 问妮蔻有没有 W 的分身（她的资料页写着「W 的分身在三个技能位里放不下，没有做」：TFM2 只有三个技能位，Q / E / R
//! 占满了，W 的被动并进了普攻），答「加」。主包不变（纯数据里没有 W 的主动）；技能由附加包的被动自己判断、自己放，普攻和
//! 三个技能位一个字节没改。英雄联盟（wiki 现行页面，V26.20）：W 主动让她和分身一起隐身 0.5 秒、两人移速 +20-40% 3 秒；分身
//! 照她当时的样子（假扮着就是那个样子，而且不会现形），活 3 秒，挨打 0.5 秒后消失，前 0.5 秒敌人选不中它；冷却 16-12 秒，
//! V26.05 起分身没了才开始算。
//!
//! - **什么时候放**：她挨了一大口——`W_WINDOW` tick 里受到的伤害到她最大生命的 `W_BURST`%——而 `W_NEAR` 内有敌方英雄；
//!   W 好了（冷却 `W_CD` tick，从上一个分身没了算起）、她没被控（击飞、晕眩、嘲讽、恐惧、魅惑、强制位移、沉默）、
//!   不在放 R（蓄力和跃起 `R_BUSY` tick）。每一口大伤害都记一行它的决定（`SPLIT CAST` / `SPLIT HOLD`）。
//! - **放了做什么**（原生效果 `league_neeko:split`：被动排它，下一拍放；排不进就被动当场放）：她隐身 `W_INVIS` tick、
//!   移速 +`W_MS`% `W_MS_T` tick，身上一团变身的烟（`league_neeko_p_poof`，变身的声音）；`spawn_unit` 在她脚下生成一个叫
//!   `league_neeko` 的单位（按她自己的图画，league.dll 的高清帧 PPU 2.5 也按这个名字认），活 `W_LIFE` tick，攻击 0（英雄
//!   联盟的分身不打人），普攻的距离、间隔照她的，移速、护甲、魔抗照她的。引擎管着它走、追人、被打。
//! - **它读成单位以后**：生成那一拍和下一拍它的最大生命、攻击、防御、移速都读成 1，那时设的生命会被盖掉（游戏 0.7.2 的
//!   预模拟日志：悟空的分身一拍后设成 1 血，再一拍读到 1851/1851），所以等它的最大生命读出来再动它：生命设成她当时的，
//!   隐身到施放后 `W_INVIS` tick，一样加速；她那时正假扮着，就在显示钩子里替它记下同一名队友（`view::note_on`，按它自己的
//!   实体号：分身画成那名队友，到它没了为止）。
//! - **挨了打**：它的生命第一次往下掉以后 `W_FADE` tick 放逐它到时间结束（`entity_banish`：看不见、打不到、不能动；API 没有
//!   让单位消失的接口，纳亚菲利的狗也这么做），原地一团烟和现形的声音；冷却从这一刻算。
//! - **退路**：宿主没有 `spawn_unit`、生成失败、给的 id 读不成单位——没有分身，她的隐身和加速照旧（施放那一刻就给了）；
//!   日志旁边的 `league_neeko.cfg` 写 `unit=off`——整个 W 都不放（和 0.1.x 一模一样）。
//! - 她先死了：挨过打、还没消失的分身当场放逐；没挨过打的由引擎管着到时间。
//!
//! 日志（`league_neeko.log`）：第二行 `SPLIT: ... - ON`；每口大伤害 `SPLIT #n CAST` / `SPLIT HOLD`；`SPLIT SPAWN` /
//! `SPAWN FAILED` / `NONE` / `LOST`；每个分身 `LOOK` / `DRESS` / 每秒一行 / `HURT` / `FADE` / `OVER` / `WAKE` / `ORPHAN`。

use std::sync::LazyLock;

use mod_api_stable::*;

use super::{head, on_screen, tally, view, wlog, ID, LOG_PATH};

// the shared part of the summons (萨科附加包的 summon.rs); not every item of it is used here
#[allow(dead_code)]
#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

pub type Pt = (f64, f64);

/// The clone's unit name: her own id, so the game draws it from her own sheet (and league.dll from her dense frames).
pub const UNIT_NAME: &str = "league_neeko";
/// W's cooldown: League's 16-12 s at rank 3 (14 s; her E keeps League's middle rank the same way, 12-10 s -> 11 s),
/// counted from the clone's end (League V26.05).
pub const W_CD: usize = 840;
/// A burst: this % of her max health lost within `W_WINDOW` ticks ...
pub const W_BURST: usize = 15;
pub const W_WINDOW: usize = 60;
/// ... with an enemy champion this close (her E's reach).
pub const W_NEAR: f64 = 90_000.0;
/// She and the clone unseen for 0.5 s (League's, every rank).
pub const W_INVIS: usize = 30;
/// Both faster: League's 20-40 % at rank 3, for 3 s.
pub const W_MS: i32 = 30;
pub const W_MS_T: usize = 180;
/// The clone's time (League's 3 s) and how long after it is first hurt it goes (League's 0.5 s).
pub const W_LIFE: usize = 180;
pub const W_FADE: usize = 30;
/// Its attack: no damage (League's clone does not attack), her bolt's reach, interval, length and release tick (the
/// main pack's atk_range, atk_cd, atk_dur, a_rel: make_override.py checks them).
pub const W_RANGE: usize = 55_000;
pub const W_COOL: usize = 92;
pub const W_ACT: usize = 27;
pub const W_LANDS: usize = 10;
/// Her R holds her this long from its cast (the charge, the leap, the landing): no W in it.
pub const R_BUSY: usize = 80;
/// The speed (on her and on the clone).
pub const W_GO: &str = "league_neeko_w_go";
/// The handoff from `:split` to the passive: `<W_UID>:<unit id>` on her for a few ticks.
pub const W_UID: &str = "league_neeko_w_uid";
/// `:split`'s word that it gave no unit.
pub const W_NONE: &str = "league_neeko_w_none";
/// The copy's poof (her disguise's) and her disguise's sounds: the split, the clone's going.
pub const W_POOF: &str = "league_neeko_p_poof";
pub const W_ON: &str = "league_neeko_p_on";
pub const W_OFF: &str = "league_neeko_p_off";
/// Crowd control that keeps her from casting.
pub const W_STOP: [CcKindV1; 7] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Taunt, CcKindV1::Fear, CcKindV1::Charm,
                                   CcKindV1::ForceMove, CcKindV1::BlockSkill];
/// Ticks the handoff stays, ticks the passive waits for it, looks a handed-over id gets to read as a settled unit.
const UID_TICKS: usize = 6;
const ASK_WAIT: usize = 4;
pub const LOOK_TRIES: usize = 6;
/// Hits kept for the burst (a second of them).
const HITS_KEPT: usize = 256;

/// The test knobs (`league_neeko.cfg` beside the log, summon.rs), read once.
pub static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

fn fx(name: &str) -> String {
    format!("{ID}:{name}")
}

fn at_input(at: Pt) -> InputTargetV1 {
    InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64)
}

fn haste(ticks: usize) -> BuffV1 {
    let mut b = BuffV1::timed(W_GO, ticks);
    b.move_speed_mult = W_MS;
    b
}

// ===================== 算式 =====================

/// The clone from her numbers now (`stat`, her health cap `max_hp`): no attack, her defences and speed, her health
/// cap, her bolt's reach and timing. No regeneration.
pub fn clone_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    summon::Spec {
        name: UNIT_NAME.to_string(),
        life: W_LIFE,
        stat: StatV1 {
            attack: 0,
            magic_power: 0,
            hp: max_hp.max(1),
            defence: stat.defence,
            magic_resistance: stat.magic_resistance,
            move_speed: stat.move_speed.max(1),
            hp_regen: 0,
            stack: 0,
            crit_chance: 0,
        },
        attack: UnitAttackV1 {
            attack_ratio: 0,
            attack: 0,
            range: W_RANGE,
            cooltime: W_COOL,
            duration: W_ACT,
            start_timing: W_LANDS,
            cancelable: false,
            attack_type: AttackTypeV1::BaseAttack.code(),
        },
    }
}

/// The damage she took in the window ending at `tick`: (all of it, the part enemy champions dealt). `hits`: (tick,
/// damage, from a champion).
pub fn burst(hits: &[(usize, usize, bool)], tick: usize) -> (usize, usize) {
    hits.iter().filter(|h| h.0 + W_WINDOW > tick && h.0 <= tick)
        .fold((0, 0), |(all, champs), h| (all + h.1, champs + if h.2 { h.1 } else { 0 }))
}

/// A burst big enough for W.
pub fn is_burst(taken: usize, max_hp: usize) -> bool {
    max_hp > 0 && taken * 100 >= max_hp * W_BURST
}

/// Why a burst did not cast W.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Hold {
    /// `unit=off` in the test knobs: no W at all.
    Off,
    /// The last cast's clone is still out (the cooldown starts when it is gone).
    Out,
    /// On cooldown, this many ticks left.
    Cooldown(usize),
    /// Held by crowd control of this kind.
    Held(CcKindV1),
    /// In Pop Blossom's charge or leap.
    Ult,
    /// No enemy champion within `W_NEAR`.
    Alone,
}

impl Hold {
    pub fn text(&self) -> String {
        match self {
            Hold::Off => "W is off (unit=off in the test knobs)".to_string(),
            Hold::Out => "the last clone is still out (the cooldown starts when it is gone)".to_string(),
            Hold::Cooldown(n) => format!("on cooldown, {n} ticks left"),
            Hold::Held(k) => format!("she is crowd-controlled ({k:?})"),
            Hold::Ult => "she is in Pop Blossom's charge or leap".to_string(),
            Hold::Alone => format!("no enemy champion within {W_NEAR:.0}"),
        }
    }
}

/// W on a burst at `tick`, or why not (in this order: the knobs, a clone still out, the cooldown, her crowd control,
/// her R, no champion near).
pub fn decide(off: bool, out: bool, ready: usize, tick: usize, held: Option<CcKindV1>, ult: bool, foe: bool) -> Result<(), Hold> {
    if off {
        return Err(Hold::Off);
    }
    if out {
        return Err(Hold::Out);
    }
    if tick < ready {
        return Err(Hold::Cooldown(ready - tick));
    }
    if let Some(k) = held {
        return Err(Hold::Held(k));
    }
    if ult {
        return Err(Hold::Ult);
    }
    if !foe {
        return Err(Hold::Alone);
    }
    Ok(())
}

/// The crowd control on `e` that keeps her from casting.
fn stopped(e: &StableEntity<'_, '_>) -> Option<CcKindV1> {
    (0..e.cc_count()).filter_map(|i| e.cc_at(i))
        .find_map(|c| W_STOP.iter().copied().find(|k| k.code() == c.kind))
}

/// The nearest living enemy champion within `reach` of her: (id, name, how far).
fn nearest_foe(sim: &StableSim<'_>, at: Pt, team: usize, reach: f64) -> Option<(usize, String, f64)> {
    (0..sim.champion_count()).filter_map(|i| sim.get_entity(sim.champion_id_at(i)))
        .filter(|u| u.team() != team && u.is_alive())
        .map(|u| (u.id(), u.name().unwrap_or_default(), summon::dist(summon::at_of(&u), at)))
        .filter(|f| f.2 <= reach)
        .min_by(|a, b| a.2.total_cmp(&b.2))
}

// ===================== 施放（原生效果） =====================

/// W's moment for `me`: her invisibility and speed and the poof (they come whether a clone does or not), then the clone
/// spawned on her and its id handed to the passive - or the word that none came.
fn split_now(sim: &mut StableSim<'_>, me: usize, by: &str) -> Option<usize> {
    let (team, stat, max, alive, at) =
        sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1, e.is_alive(), summon::at_of(&e)))?;
    if !alive {
        sim.add_buff(me, &BuffV1::timed(W_NONE, UID_TICKS));
        return None;
    }
    let hid = sim.entity_set_invisible(me, W_INVIS);
    sim.entity_remove_buff(me, W_GO);
    sim.add_buff(me, &haste(W_MS_T));
    let on_her = InputTargetV1::target(me);
    sim.play_view_effect(W_POOF, me, &on_her, 0, 0, 0);
    sim.play_sfx(W_ON, me, &on_her);
    let her = format!("she is unseen for {W_INVIS} ticks ({}) and +{W_MS}% faster for {W_MS_T} ticks",
                      if hid { "set" } else { "entity_set_invisible REFUSED" });
    if KNOBS.off {
        // never: the passive does not cast with unit=off
        sim.add_buff(me, &BuffV1::timed(W_NONE, UID_TICKS));
        return None;
    }
    // League: the clone "spawns directly on top of her" (V13.9)
    let spec = clone_spec(&stat, max).with(&KNOBS);
    let at = summon::inside(summon::field(sim), at);
    match summon::spawn(sim, me, team, at, &spec) {
        Some(id) => {
            sim.add_buff(me, &BuffV1::timed(&summon::handoff(W_UID, id), UID_TICKS));
            if let Some(k) = tally(sim, "split spawn") {
                wlog(format!("{} SPLIT SPAWN #{k} ({by}): {her}; unit #{id} for team {team} on her at {}: {}", head(sim, me),
                             summon::pt(at), spec.shown()));
            }
            Some(id)
        }
        None => {
            sim.add_buff(me, &BuffV1::timed(W_NONE, UID_TICKS));
            if let Some(k) = tally(sim, "split fail") {
                wlog(format!("{} SPLIT SPAWN FAILED #{k} ({by}): spawn_unit gave no unit for '{}' at {} - {her}, no clone",
                             head(sim, me), spec.name, summon::pt(at)));
            }
            None
        }
    }
}

/// `:split` - the passive queues it the tick it decides on W.
pub struct SplitFx;

impl StableEffectType for SplitFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _input: InputTargetV1) {
        split_now(sim, caster, "the queued effect");
    }
}

// ===================== 被动里 W 的那一份 =====================

/// A cast waiting for its unit: the tick of the cast, the tick the unit comes.
#[derive(Clone, Copy, Debug)]
struct Ask {
    tick: usize,
    born: usize,
}

/// A handed-over unit not yet read as a settled one: its id, the tick it came, the tick its handoff was taken, looks.
#[derive(Clone, Copy, Debug)]
struct Fresh {
    id: usize,
    born: usize,
    seen: usize,
    tries: usize,
}

/// Her clone as a unit, as the passive keeps it.
#[derive(Clone, Debug)]
struct Live {
    unit: summon::Unit,
    /// The health it was to start with (hers), and whether the look a tick after was logged.
    hp_goal: usize,
    dressed: bool,
    /// Its health at the last look (from the dress line on), the tick it was first hurt, the tick it fades, the tick
    /// it faded.
    last_hp: Option<usize>,
    hurt: Option<usize>,
    fade_at: Option<usize>,
    faded: Option<usize>,
    /// The ally whose body the display hook was told it wears (she was disguised as it came), and the screen's sim.
    worn: Option<(String, u64, u64)>,
}

/// W's part of her passive (state of the passive instance: the presims and the match on screen each have their own).
#[derive(Clone, Default)]
pub struct Split {
    /// Damage she took: (tick, damage, from an enemy champion), the last `W_WINDOW` ticks.
    hits: Vec<(usize, usize, bool)>,
    /// The tick W is ready again; a cast in progress (its clone not gone yet: the cooldown waits for it).
    ready: usize,
    open: bool,
    /// The last tick was a burst (one decision line a burst, and one more if it casts later in it).
    bursting: bool,
    /// The tick her R was last seen cast.
    ult_at: Option<usize>,
    wait: Option<Ask>,
    fresh: Option<Fresh>,
    live: Option<Live>,
    wake: Option<summon::Wake>,
    /// Casts so far (`SPLIT #n`: the cast and its clone).
    n: usize,
    me: usize,
}

impl Split {
    /// A hit on her (`on_damaged`).
    pub fn hurt(&mut self, tick: usize, damage: usize, champion: bool) {
        if damage == 0 {
            return;
        }
        if self.hits.len() >= HITS_KEPT {
            self.hits.remove(0);
        }
        self.hits.push((tick, damage, champion));
    }

    /// Her R's cooldown has just risen.
    pub fn saw_ult(&mut self, tick: usize) {
        self.ult_at = Some(tick);
    }

    /// The cast's end: no clone came or it is gone; the cooldown runs from now.
    fn close(&mut self, tick: usize) {
        self.open = false;
        self.ready = tick + W_CD;
    }

    /// A new life (a new entity): nothing of the old one's clone is hers to watch any more; the cooldown runs on.
    pub fn spawned(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if let Some(live) = self.live.take() {
            wlog(format!("{} SPLIT #{}: its clone #{} still on the books at her respawn (her death did not reach on_dead) - let go",
                         head(sim, me), live.unit.n, live.unit.id));
        }
        let tick = sim.tick();
        let ready = if self.open { tick + W_CD } else { self.ready };
        *self = Split { me, ready, n: self.n, ..Split::default() };
    }

    /// Her death: a clone hurt and not yet gone goes now; one never hurt goes on to its time unwatched.
    pub fn dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        let tick = sim.tick();
        (self.hits, self.bursting, self.wait, self.fresh, self.wake) = (Vec::new(), false, None, None, None);
        if let Some(mut live) = self.live.take() {
            let me = sim.get_player(player).and_then(|p| p.champion()).map_or(self.me, |e| e.id());
            let now = live.hurt.is_some() && live.faded.is_none() && sim.get_entity(live.unit.id).is_some_and(|e| e.is_alive());
            if now {
                self.fade(sim, me, &mut live, "Neeko died with it hurt");
            }
            if let Some((_, m, s)) = &live.worn {
                view::note_off(*m, *s, live.unit.id, live.unit.born + live.unit.life);
            }
            let u = &live.unit;
            if let Some(k) = tally(sim, "split orphan") {
                wlog(format!("{} SPLIT #{} ORPHAN #{k}: Neeko died, her clone #{} at {} has {} ticks left and hp {}/{} - {}",
                             head(sim, me), u.n, u.id, summon::pt(u.at), u.left(tick), u.hp, u.max,
                             if now { "faded now (it was hurt)" } else { "it goes on unwatched to its time" }));
            }
        }
        if self.open {
            self.close(tick);
        }
    }

    /// Her tick while she lives (after the disguise's): the burst and W's decision, the unit asked for, looked at,
    /// watched. `worn`: the ally she is disguised as now.
    pub fn update(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize, worn: Option<&str>) {
        self.me = me;
        let tick = sim.tick();
        let Some((team, here, hp, max, held)) =
            sim.get_entity(me).map(|e| (e.team(), summon::at_of(&e), e.hp().0, e.hp().1, stopped(&e)))
        else {
            return;
        };
        self.hits.retain(|h| h.0 + W_WINDOW > tick);
        let (taken, champs) = burst(&self.hits, tick);
        if is_burst(taken, max) {
            let first = !std::mem::replace(&mut self.bursting, true);
            let foe = nearest_foe(sim, here, team, W_NEAR);
            let ult = self.ult_at.is_some_and(|u| tick < u + R_BUSY);
            let decision = decide(KNOBS.off, self.open, self.ready, tick, held, ult, foe.is_some());
            if decision.is_ok() || first {
                let what = format!(
                    "{}% of her max health ({taken} of {max}) in the last {W_WINDOW} ticks, {}% of it from champions; {}",
                    taken * 100 / max.max(1), champs * 100 / taken.max(1),
                    foe.as_ref().map_or_else(|| format!("no enemy champion within {W_NEAR:.0}"),
                                             |f| format!("enemy champion #{} {} {:.0} away", f.0, f.1, f.2)));
                match decision {
                    Ok(()) => self.cast(sim, me, here, &what),
                    Err(hold) => {
                        if let Some(k) = tally(sim, "split hold") {
                            wlog(format!("{} SPLIT HOLD #{k}: {what} - held: {}", head(sim, me), hold.text()));
                        }
                    }
                }
            }
        } else {
            self.bursting = false;
        }
        self.watch(sim, player, me, team, here, hp, worn);
    }

    /// W cast: `:split` queued for the next tick (refused: run at once).
    fn cast(&mut self, sim: &mut StableSim<'_>, me: usize, here: Pt, what: &str) {
        let tick = sim.tick();
        self.n += 1;
        self.open = true;
        let queued = sim.queue_effect(&fx("split"), AttackTypeV1::Skill, me, &at_input(here), 1);
        if let Some(k) = tally(sim, "split cast") {
            wlog(format!("{} SPLIT #{} CAST #{k}: {what} - Shapesplitter at {}{}", head(sim, me), self.n, summon::pt(here),
                         if queued { "" } else { " - queue_effect REFUSED: cast by the passive" }));
        }
        let born = if queued {
            tick + 1
        } else {
            split_now(sim, me, "queue_effect refused: cast by the passive");
            tick
        };
        self.wait = Some(Ask { tick, born });
    }

    #[allow(clippy::too_many_arguments)]
    fn watch(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize, team: usize, here: Pt, hp: usize, worn: Option<&str>) {
        let tick = sim.tick();
        if let Some(a) = self.wait {
            if let Some(id) = summon::take_handoff(sim, me, W_UID) {
                self.wait = None;
                self.fresh = Some(Fresh { id, born: a.born, seen: tick, tries: 0 });
            } else if sim.get_entity(me).is_some_and(|e| summon::has_buff(&e, W_NONE)) {
                // the effect gave no unit and said so (its own line)
                sim.entity_remove_buff(me, W_NONE);
                self.wait = None;
                self.close(tick);
            } else if tick > a.tick + ASK_WAIT {
                self.wait = None;
                self.close(tick);
                if let Some(k) = tally(sim, "split none") {
                    wlog(format!("{} SPLIT #{} NONE #{k}: no unit came within {ASK_WAIT} ticks of the cast (the queued effect never \
                                  ran?) - no clone", head(sim, me), self.n));
                }
            }
        }
        if let Some(f) = self.fresh {
            // a new unit reads max health 1 and attack / defences / speed 1 on its spawn tick and the next, and a health
            // set then is lost (game 0.7.2's presims): it is looked at a tick after its handoff at the soonest, taken on
            // once its health cap reads
            if tick <= f.seen {
                return;
            }
            match summon::Unit::look(sim, f.id, self.n, f.born, W_LIFE, team, player) {
                Ok((unit, line)) if unit.max > 1 || f.tries + 1 >= LOOK_TRIES => {
                    self.fresh = None;
                    self.dress(sim, me, hp, unit, line, f.tries, worn);
                }
                Err(why) if f.tries + 1 >= LOOK_TRIES => {
                    self.fresh = None;
                    self.close(tick);
                    if let Some(k) = tally(sim, "split lost") {
                        wlog(format!("{} SPLIT #{} LOST #{k}: the unit spawn_unit named never read as one in {LOOK_TRIES} ticks \
                                      ({why}) - no clone", head(sim, me), self.n));
                    }
                }
                _ => self.fresh = Some(Fresh { tries: f.tries + 1, ..f }),
            }
            return;
        }
        if let Some(live) = self.live.take() {
            self.live_tick(sim, me, here, live);
        }
        if let Some(mut w) = self.wake.take() {
            let (lines, over) = w.step(sim);
            for line in lines {
                if let Some(k) = tally(sim, "split wake") {
                    wlog(format!("{} SPLIT #{} WAKE #{k}: {line}", head(sim, me), w.n));
                }
            }
            if !over {
                self.wake = Some(w);
            }
        }
    }

    /// The clone read as a settled unit: her health, unseen to W_INVIS ticks after the cast, the speed, her disguise.
    #[allow(clippy::too_many_arguments)]
    fn dress(&mut self, sim: &mut StableSim<'_>, me: usize, hp: usize, mut unit: summon::Unit, line: String, tries: usize,
             worn: Option<&str>) {
        let tick = sim.tick();
        let (id, n, age) = (unit.id, unit.n, unit.age(tick));
        // League's clone is her to the eye: the cap is hers, the health now set to her own
        let (had, hp_goal) = (unit.hp, hp.clamp(1, unit.max.max(1)));
        let set = hp_goal < had && sim.entity_set_hp(id, hp_goal);
        if set {
            unit.health_set(hp_goal);
        }
        // unseen until W_INVIS ticks after the cast, like her (League: enemies cannot target it its first 0.5 s)
        let unseen = W_INVIS.saturating_sub(age);
        let hid = unseen > 0 && sim.entity_set_invisible(id, unseen);
        let fast = W_MS_T.saturating_sub(age);
        if fast > 0 {
            sim.add_buff(id, &haste(fast));
        }
        // her disguise: League's clone takes her form then and never loses it
        let screen = on_screen(sim);
        if let Some((m, s)) = screen {
            view::note_clone(m, s, id);
        }
        let worn = worn.zip(screen).map(|(name, (m, s))| {
            view::note_on(m, s, id, unit.born, name);
            (name.to_string(), m, s)
        });
        if let Some(k) = tally(sim, "split look") {
            wlog(format!(
                "{} SPLIT #{n} LOOK #{k}: {line}{}; health to her own {hp_goal}: {}; unseen for {unseen} more ticks: {}; +{W_MS}% \
                 speed for {fast} ticks; drawn as {}",
                head(sim, me), if unit.max > 1 { String::new() } else { format!(" (its health cap still reads 1 after {} looks)", tries + 1) },
                if set { "set" } else if hp_goal >= had { "it has no more" } else { "entity_set_hp REFUSED" },
                if unseen == 0 { "-" } else if hid { "set" } else { "entity_set_invisible REFUSED" },
                match (&worn, worn_or_none(screen.is_some(), unit.name.as_str())) {
                    (Some((name, _, _)), _) => format!("her disguise, {name} (the display hook told)"),
                    (None, note) => note.to_string(),
                }));
        }
        self.live = Some(Live { unit, hp_goal, dressed: false, last_hp: None, hurt: None, fade_at: None, faded: None, worn });
    }

    /// The clone's tick: the dress line a tick after its look, its first hurt, its fade, its line, its end.
    fn live_tick(&mut self, sim: &mut StableSim<'_>, me: usize, here: Pt, mut live: Live) {
        let tick = sim.tick();
        let (id, n) = (live.unit.id, live.unit.n);
        let seen = sim.get_entity(id).filter(|e| e.is_alive()).map(|e| (e.hp(), summon::has_buff(&e, W_GO), e.is_targetable()));
        if !live.dressed {
            live.dressed = true;
            live.last_hp = seen.map(|s| s.0 .0);
            if let (Some(k), Some(((now, max), fast, targetable))) = (tally(sim, "split dress"), seen) {
                wlog(format!("{} SPLIT #{n} DRESS #{k}: a tick on, its health {now}/{max} (asked {}), its speed buff {}, \
                              targetable={targetable}", head(sim, me), live.hp_goal, if fast { "on it" } else { "NOT on it" }));
            }
        } else if let (Some(((now, _), _, _)), Some(last)) = (seen, live.last_hp) {
            if now < last && live.hurt.is_none() && live.faded.is_none() {
                live.hurt = Some(tick);
                live.fade_at = Some(tick + W_FADE);
                if let Some(k) = tally(sim, "split hurt") {
                    wlog(format!("{} SPLIT #{n} HURT #{k}: its health {last} -> {now} at {} ticks old - it fades in {W_FADE} ticks",
                                 head(sim, me), live.unit.age(tick)));
                }
            }
            live.last_hp = Some(now);
        }
        match live.unit.step(sim, Some(here)) {
            summon::Step::Alive(line) => {
                // counted only when there is a line (a count every tick would cap the presims' lines by ticks)
                if let Some(line) = line {
                    if let Some(k) = tally(sim, "split line") {
                        wlog(format!("{} SPLIT #{n} #{k}: {line}", head(sim, me)));
                    }
                }
                if live.faded.is_none() && live.fade_at.is_some_and(|t| tick >= t) {
                    self.fade(sim, me, &mut live, "League's clone goes 0.5 s after it is hurt");
                }
                self.live = Some(live);
            }
            summon::Step::Over(end) => {
                let story = match (live.hurt, live.faded) {
                    (Some(h), Some(f)) => format!("first hurt at {} ticks old, faded at {}", h.saturating_sub(live.unit.born),
                                                  f.saturating_sub(live.unit.born)),
                    (Some(h), None) => format!("first hurt at {} ticks old, gone before it faded", h.saturating_sub(live.unit.born)),
                    _ => "never hurt".to_string(),
                };
                if let Some(k) = tally(sim, "split over") {
                    wlog(format!("{} SPLIT #{n} OVER #{k}: {}; {story}", head(sim, me), end.text));
                }
                if live.faded.is_none() {
                    self.close(tick);
                }
                if let Some((_, m, s)) = &live.worn {
                    view::note_off(*m, *s, id, tick);
                }
                self.wake = Some(live.unit.wake(sim, &end));
            }
        }
    }

    /// The clone out of play to its time (no API ends a unit early): banished, a poof where it stands; W's cooldown
    /// runs from now.
    fn fade(&mut self, sim: &mut StableSim<'_>, me: usize, live: &mut Live, why: &str) {
        let tick = sim.tick();
        let left = live.unit.left(tick).max(1);
        let ok = sim.entity_banish(me, live.unit.id, left + 1, "", "");
        let at = at_input(live.unit.at);
        sim.play_view_effect(W_POOF, me, &at, 0, 0, 0);
        sim.play_sfx(W_OFF, me, &at);
        live.faded = Some(tick);
        self.close(tick);
        if let Some(k) = tally(sim, "split fade") {
            wlog(format!("{} SPLIT #{} FADE #{k}: {why} - banished for the rest of its time ({} ticks): {}; a poof at {}",
                         head(sim, me), live.unit.n, left + 1, if ok { "yes" } else { "entity_banish REFUSED" },
                         summon::pt(live.unit.at)));
        }
    }
}

/// The LOOK line's word on a clone not told to wear a disguise.
fn worn_or_none(screen: bool, name: &str) -> &'static str {
    match (screen, name == UNIT_NAME) {
        (_, false) => "its own unit name's sheet (a test name)",
        (true, true) => "herself (she was not disguised)",
        (false, true) => "herself (this sim is not drawn)",
    }
}

/// The load line, and `:split` registered.
pub fn register(module: &mut StableMod) {
    wlog(format!(
        "SPLIT: Shapesplitter's active (W) is the add-on's own: {W_BURST}% of her max health lost within {W_WINDOW} ticks with an \
         enemy champion within {W_NEAR:.0} casts it ({W_CD} ticks cooldown from the clone's end) - she is unseen {W_INVIS} ticks and \
         +{W_MS}% faster {W_MS_T} ticks, and a clone '{}' (spawn_unit) comes on her for {W_LIFE} ticks, no damage, fading {W_FADE} \
         ticks after it is hurt - {}. Test knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(UNIT_NAME),
        if KNOBS.off { "OFF by the test knobs: no W at all" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(),
        KNOBS.shown()
    ));
    module.add_native_effect(fx("split"), SplitFx);
}

#[cfg(test)]
#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
pub(crate) mod mock;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_clone_is_her_with_no_damage() {
        let hers = StatV1 { attack: 70, magic_power: 300, hp: 960, defence: 21, magic_resistance: 22, move_speed: 900, hp_regen: 3,
                            stack: 1, crit_chance: 10 };
        let spec = clone_spec(&hers, 1500);
        assert_eq!((spec.name.as_str(), spec.life), ("league_neeko", 180));
        assert_eq!(spec.stat, StatV1 { attack: 0, magic_power: 0, hp: 1500, defence: 21, magic_resistance: 22, move_speed: 900,
                                       hp_regen: 0, stack: 0, crit_chance: 0 });
        let a = spec.attack;
        assert_eq!(a.attack + spec.stat.attack * a.attack_ratio / 100, 0, "League's clone does not attack");
        assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (55_000, 92, 27, 10));
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        assert_eq!(clone_spec(&hers, 0).stat.hp, 1);
        // League's numbers: 0.5 s unseen, 3 s of speed, a 3 s clone gone 0.5 s after a hit, 14 s at rank 3 (16-12)
        assert_eq!((W_INVIS, W_MS_T, W_LIFE, W_FADE, W_CD), (30, 180, 180, 30, 14 * 60));
        assert!((20..=40).contains(&W_MS));
        for name in [W_GO, W_NONE, &summon::handoff(W_UID, usize::MAX), &fx("split")] {
            assert!(name.len() <= BUFF_NAME_CAP, "{name}");
        }
        assert!(ASK_WAIT + LOOK_TRIES < W_INVIS && W_FADE < W_LIFE);
    }

    #[test]
    fn a_burst_is_a_second_of_damage() {
        // (tick, damage, from a champion)
        let hits = [(940, 500, true), (941, 60, false), (990, 40, true), (1000, 50, true)];
        assert_eq!(burst(&hits, 1000), (150, 90), "the hit 60 ticks back is out of the window");
        assert_eq!(burst(&hits, 999), (600, 540), "a tick earlier it is in, the hit to come is not");
        assert_eq!(burst(&[], 1000), (0, 0));
        assert!(is_burst(150, 1000) && !is_burst(149, 1000) && !is_burst(500, 0));
    }

    #[test]
    fn w_waits_for_its_cooldown_her_hands_and_a_champion() {
        let ok = |held, ult, foe| decide(false, false, 0, 5000, held, ult, foe);
        assert_eq!(ok(None, false, true), Ok(()));
        assert_eq!(decide(true, false, 0, 5000, None, false, true), Err(Hold::Off));
        assert_eq!(decide(false, true, 0, 5000, None, false, true), Err(Hold::Out));
        assert_eq!(decide(false, false, 5300, 5000, None, false, true), Err(Hold::Cooldown(300)));
        assert_eq!(decide(false, false, 5000, 5000, None, false, true), Ok(()), "ready at its tick");
        assert_eq!(ok(Some(CcKindV1::Stun), false, true), Err(Hold::Held(CcKindV1::Stun)));
        assert_eq!(ok(None, true, true), Err(Hold::Ult));
        assert_eq!(ok(None, false, false), Err(Hold::Alone));
        // a root does not stop a cast that is not a dash (League's W)
        assert!(!W_STOP.contains(&CcKindV1::Bind) && W_STOP.contains(&CcKindV1::BlockSkill));
        assert!(Hold::Cooldown(12).text().contains("12 ticks left") && Hold::Alone.text().contains("90000"));
    }

    // ---- W on the mock world (summon_mock.rs: our guess of the host, to check this side's logic) ----

    use super::mock::{champion, MPlayer, World};
    use std::path::PathBuf;

    const FOE: usize = 1;

    fn log_file() -> PathBuf {
        super::super::tests::test_log()
    }

    /// Neeko #0 (team 0, 960 health) at (300000, 300000); an enemy champion #1 40000 east of her; a player each. The
    /// host's new units read unsettled for 2 ticks (game 0.7.2).
    fn world() -> (World, Split) {
        log_file();
        let mut w = World { settle: 2, ..World::default() };
        let mut nk = champion("league_neeko", 0, 300_000.0, 300_000.0);
        (nk.hp, nk.max, nk.stat.hp) = (960, 960, 960);
        w.units = vec![nk, champion("league_garen", 1, 340_000.0, 300_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: FOE, ..Default::default() }];
        let mut me = Split::default();
        w.sim(|sim| me.spawned(sim, 0));
        run(&mut w, &mut me, 3, None);
        (w, me)
    }

    fn tick(w: &mut World, me: &mut Split, worn: Option<&str>) {
        for (name, caster, input) in w.due() {
            w.sim(|sim| match name.as_str() {
                "league_neeko:split" => SplitFx.apply(sim, 0, caster, input),
                other => panic!("an effect nobody registered: {other}"),
            });
        }
        if w.units[0].hp > 0 {
            w.sim(|sim| me.update(sim, 0, 0, worn));
        }
        w.step();
    }

    fn run(w: &mut World, me: &mut Split, n: usize, worn: Option<&str>) {
        for _ in 0..n {
            tick(w, me, worn);
        }
    }

    /// A hit of `amount` on her from `attacker` as the engine reports it: the hook first, then the health.
    fn hit(w: &mut World, me: &mut Split, attacker: usize, amount: usize) {
        let champ = w.units[attacker].kind == EntityKindV1::Champion;
        me.hurt(w.tick, amount, champ);
        w.hurt(0, amount);
    }

    #[test]
    fn a_big_hit_casts_w_and_leaves_a_clone_that_goes_when_hit() {
        let (mut w, mut me) = world();
        hit(&mut w, &mut me, FOE, 100);
        run(&mut w, &mut me, 2, None);
        assert!(w.spawns.is_empty(), "10% is no burst");
        hit(&mut w, &mut me, FOE, 60);
        let cast = w.tick;
        run(&mut w, &mut me, 1, None);
        assert_eq!(me.n, 1, "16% in a second is a burst");
        run(&mut w, &mut me, 1, None);
        // the effect a tick on: her unseen 30 ticks and 30% faster 180, the poof; one unit on her
        assert!(w.invisibles.iter().any(|v| v.1 == 0 && v.2 == W_INVIS));
        assert!(w.units[0].buffs.iter().any(|b| b.0.name() == W_GO && b.0.move_speed_mult == W_MS && b.1 <= W_MS_T));
        assert_eq!((w.viewed(W_POOF), w.heard(W_ON)), (1, 1));
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life as usize, s.at), ("league_neeko", 0, 0, W_LIFE, (300_000, 300_000)));
        assert_eq!(s.tick, cast + 1);
        assert_eq!((s.stat.attack, s.stat.hp, s.attack.attack, s.attack.attack_ratio), (0, 960, 0, 0));
        let clone = s.gave.unwrap();
        // unsettled for its first 2 ticks: nothing done to it then (a health set would be lost)
        assert!(me.live.is_none() && me.fresh.is_some());
        run(&mut w, &mut me, 3, None);
        let live = me.live.as_ref().expect("the clone was never taken on");
        assert!(live.unit.max > 1, "taken on before its numbers read");
        assert_eq!(w.units[clone].hp, 960 - 160, "the clone does not have her health");
        assert!(w.invisibles.iter().any(|v| v.1 == clone && v.2 > 0 && v.2 < W_INVIS), "the clone is not unseen like her");
        assert!(w.has(clone, W_GO));
        // no second cast on the same burst; the clone hit: it goes 30 ticks later, not before
        hit(&mut w, &mut me, FOE, 200);
        run(&mut w, &mut me, 5, None);
        assert_eq!(me.n, 1, "a second W while the clone is out");
        w.hurt(clone, 5);
        let hurt = w.tick;
        run(&mut w, &mut me, W_FADE - 1, None);
        assert!(w.banishes.is_empty(), "it went before 0.5 s");
        run(&mut w, &mut me, 2, None);
        assert_eq!(w.banishes.len(), 1);
        let b = w.banishes[0];
        assert_eq!((b.1, b.2), (0, clone));
        assert!(b.0 >= hurt + W_FADE && b.0 <= hurt + W_FADE + 1);
        assert!(b.0 + b.3 > s.tick + W_LIFE, "banished short of its time");
        assert_eq!(w.viewed(W_POOF), 2, "no poof where it went");
        // W's cooldown runs from the fade
        assert!(!me.open && me.ready == b.0 + W_CD, "cooldown {} from the fade at {}", me.ready, b.0);
        // it times out; the books are clean
        run(&mut w, &mut me, W_LIFE, None);
        assert!(!w.units[clone].valid);
        assert!(me.live.is_none() && me.fresh.is_none() && me.wait.is_none() && w.queue.is_empty());
        assert_eq!(w.spawns.len(), 1);
    }

    #[test]
    fn the_cooldown_holds_w_and_a_lone_or_held_neeko_does_not_cast() {
        // no champion near: a tower's shot is no reason
        let (mut w, mut me) = world();
        w.units[FOE].x = 500_000.0;
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, 5, None);
        assert!(me.n == 0 && w.spawns.is_empty());
        // stunned
        let (mut w, mut me) = world();
        w.units[0].ccs.push((CcV1::stun(30), 30));
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, 5, None);
        assert_eq!(me.n, 0);
        // in her R
        let (mut w, mut me) = world();
        me.saw_ult(w.tick);
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, 5, None);
        assert_eq!(me.n, 0);
        // the burst outlasts the R's lock: W comes then, in the same burst
        run(&mut w, &mut me, R_BUSY, None);
        assert_eq!(me.n, 0, "the burst is over by then");
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, 2, None);
        assert_eq!(me.n, 1);
        // the cooldown: a burst right after the clone's end does nothing; one after W_CD casts
        let (mut w, mut me) = world();
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, W_LIFE + 20, None);
        assert_eq!(me.n, 1);
        assert!(!me.open && me.ready > w.tick);
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, 3, None);
        assert_eq!(me.n, 1, "W on cooldown");
        let wait = me.ready - w.tick;
        run(&mut w, &mut me, wait, None);
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, 3, None);
        assert_eq!(me.n, 2, "W ready again");
    }

    #[test]
    fn no_unit_from_the_host_leaves_her_the_invisibility_and_the_speed() {
        // no such slot, a refusal, an id that never reads as a unit, no queued effects at all
        for case in 0..4 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                2 => w.spawn_never = true,
                _ => w.queue_ok = false,
            }
            hit(&mut w, &mut me, FOE, 300);
            run(&mut w, &mut me, 20, None);
            assert_eq!(me.n, 1, "case {case}");
            assert!(w.invisibles.iter().any(|v| v.1 == 0), "case {case}: she was not unseen");
            assert!(w.has(0, W_GO), "case {case}: she is not faster");
            if case == 3 {
                // the passive cast it itself: a unit all the same
                assert!(me.live.is_some() && w.spawns.len() == 1, "case 3");
                continue;
            }
            assert!(me.live.is_none() && me.fresh.is_none() && me.wait.is_none(), "case {case}");
            assert!(!me.open && me.ready > w.tick, "case {case}: the cooldown did not start");
            assert!(!w.has(0, W_NONE) && w.queue.is_empty(), "case {case}");
        }
    }

    #[test]
    fn her_disguise_goes_to_the_clone_on_screen_only() {
        let (mut w, mut me) = world();
        // pad the world so the clone's id is this test's own in the shared notes of the screen
        for k in 0..37 {
            w.units.push(champion("league_garen", 1, 1_000_000.0 + k as f64, 1_000_000.0));
            w.units.last_mut().unwrap().valid = false;
        }
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, 6, Some("league_jinx"));
        let clone = w.spawns[0].gave.unwrap();
        assert_eq!(clone, 39);
        let live = me.live.as_ref().unwrap();
        assert_eq!(live.worn.as_ref().map(|w| w.0.as_str()), Some("league_jinx"));
        let born = live.unit.born;
        let shown = |t: usize| view::worn_at(7, 1, clone, t);
        assert_eq!(shown(born).as_deref(), Some("league_jinx"), "drawn as herself at its first frame");
        assert_eq!(shown(born - 1), None);
        // her reveal does not reach the clone (League: it never loses the disguise); its end does
        run(&mut w, &mut me, 30, None);
        assert_eq!(shown(w.tick).as_deref(), Some("league_jinx"));
        run(&mut w, &mut me, W_LIFE, None);
        assert!(me.live.is_none());
        assert_eq!(shown(w.tick), None);
        // in a presim nothing is noted
        let (mut w, mut me) = world();
        w.origin = SimOriginKindV1::ServerPresim;
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, 6, Some("league_jinx"));
        assert!(me.live.as_ref().is_some_and(|l| l.worn.is_none()));
    }

    #[test]
    fn the_clone_goes_on_when_she_dies_unless_it_was_hurt() {
        for hurt in [false, true] {
            let (mut w, mut me) = world();
            hit(&mut w, &mut me, FOE, 300);
            run(&mut w, &mut me, 10, None);
            let clone = w.spawns[0].gave.unwrap();
            if hurt {
                w.hurt(clone, 5);
                run(&mut w, &mut me, 3, None);
            }
            (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
            w.sim(|sim| me.dead(sim, 0));
            assert!(me.live.is_none() && !me.open, "hurt {hurt}");
            assert_eq!(w.banishes.len(), usize::from(hurt), "hurt {hurt}");
            run(&mut w, &mut me, W_LIFE, None);
            assert!(!w.units[clone].valid, "hurt {hurt}: it outlived its time");
            assert!(w.queue.is_empty());
        }
    }

    #[test]
    fn the_knob_turns_w_off() {
        // the knobs are read once a launch: this only checks the decision the passive takes with unit=off
        assert_eq!(decide(true, false, 0, 1, None, false, true), Err(Hold::Off));
        assert!(Hold::Off.text().contains("unit=off"));
    }

    #[test]
    fn the_log_tells_ws_story() {
        let (mut w, mut me) = world();
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, 70, None);
        let clone = w.spawns[0].gave.unwrap();
        w.players[1].gold += 20;
        w.hurt(clone, 10);
        run(&mut w, &mut me, W_FADE + 5, None);
        hit(&mut w, &mut me, FOE, 300);
        run(&mut w, &mut me, 2, None);
        run(&mut w, &mut me, W_LIFE, None);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" SPLIT ")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "SPLIT #1 CAST #", "31% of her max health (300 of 960) in the last 60 ticks, 100% of it from champions; enemy champion #1 \
             league_garen 40000 away - Shapesplitter at (300000,300000)",
            "SPLIT SPAWN #", "she is unseen for 30 ticks (set) and +30% faster for 180 ticks; unit #2 for team 0 on her at (300000,300000): \
             'league_neeko' for 180 ticks, attack 0 ap 0 hp 960 def 20 mr 20 speed 1100; hits 0 + 0% of its attack, range 55000, every \
             92 ticks (27 long, lands at 10)",
            "SPLIT #1 LOOK #", "reads back as name 'league_neeko' kind summon team 0 champion=false", "health to her own 660: set",
            "unseen for", "drawn as herself (she was not disguised)",
            "SPLIT #1 DRESS #", "its health 660/960 (asked 660), its speed buff on it",
            "SPLIT #1 HURT #", "it fades in 30 ticks",
            "SPLIT #1 FADE #", "banished for the rest of its time", ": yes; a poof at",
            "SPLIT HOLD #", "- held: on cooldown",
            "SPLIT #1 OVER #", "TIMED OUT after", "faded at",
            "SPLIT #1 WAKE #",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        // (the other tests write to the same log: one of them a presim)
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=") || l.starts_with("[presim m=7 s=1] t=")));
        let longest = mine.iter().map(|l| l.len()).max().unwrap();
        assert!(longest < 800, "a line of {longest} bytes");
    }
}
