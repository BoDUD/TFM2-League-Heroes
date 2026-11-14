//! 小菊是真的单位（0.2.0，2026-11-14；用户看了和英雄联盟不一样的地方的清单：「全改吧」，其中一条是「召唤物不会走、不会打、
//! 打不掉」，之后「召唤物的全做啊」）。安妮的提伯斯（league_annie_q 0.3.0）的做法。
//!
//! 英雄联盟（wiki 现行页面）：小菊落在艾翁身前，最多留 45 秒，有自己的生命、护甲、魔抗，自己走、自己打最近的敌人，敌人打得到、
//! 打得死；连续三下打同一个英雄时第三下是一道冲击波，击飞（晕眩）1 秒。主包（和本包 0.1.x）：小菊落在敌方英雄身上（击飞、
//! 60 + 40% 法强），之后 8 秒是挂在他身上的画面和伤害（`AddCasted`：每 60 tick 一拳 25 + 20% 法强，每第三拳砸地再加
//! 40 + 30% 法强并击飞），打不到、不会走，他死了她就走。
//!
//! - 落下那一下还是数据（伤害、击飞、R → Q 的连招都不变）；副本在落下时给他挂 `D_MARK`，被动看到就等落下的画面放完（`D_FIRST`
//!   tick），在画面里她站的地方（他身后 `D_BEHIND`）排原生效果 `league_ivern:daisy`，它调 `spawn_unit`：单位叫
//!   `league_ivern_daisy`（图是主包的 league/champions/league_ivern_daisy，由 `mod.override_info` 接到这个名字上），活
//!   `D_LIFE` tick，属性按艾翁此刻的算（[`daisy_spec`]），每拳 `D_HIT` + `D_HIT_AP`% 法强（单位的普攻是物理伤害）。成功了给
//!   艾翁挂 `D_UNIT`：副本里挂在目标身上的那串拳（`AddCasted`）和最后挥手的画面每一次都先看它，有就不放。
//! - 第三拳：被动的 `on_attack` 要是听得到她的出拳（引擎是不是把召唤物的攻击告诉召唤者的被动，要在游戏里看），就数她连着打
//!   同一个英雄的次数；听不到就按她的出拳节奏数（她身边 `D_RANGE` + 两人身体内有敌方英雄的时候每 `D_COOL` tick 算一拳）。第三拳
//!   在那个英雄身上补 `D_SLAM` + `D_SLAM_AP`% 法强的魔法伤害、击飞 `D_UP` tick，放主包砸地的冲击波和声音。
//! - 生成不了（宿主没有这个接口、失败、读不成单位、6 tick 内就没了）：`D_UNIT` 不挂（或去掉），挂在目标身上的那串拳照旧打完。
//!   测试开关 `unit=off`（日志旁边的 `league_ivern.cfg`）：同样照旧。
//! - 艾翁先死了：被动不再跑，小菊由引擎管着接着打到时间（第三拳的击飞没了）。
//!
//! 日志（`league_ivern.log`）：`DAISY` 开头的一整套。

use mod_api_stable::*;

use super::{head, tally, wlog, ID, LOG_PATH};

// the shared part of the summons (萨科附加包的 summon.rs); not every item of it is used here
#[allow(dead_code)]
#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

pub type Pt = (f64, f64);

/// The copy's drop lays it on the champion Daisy lands on (3 ticks).
pub const D_MARK: &str = "league_ivern_r_mark";
/// On Ivern while Daisy is a unit: the copy's riding punches and her wave at the end read it and play nothing.
pub const D_UNIT: &str = "league_ivern_d_unit";
/// The handoff from `:daisy` to the passive: `<D_UID>:<unit id>` on Ivern for a few ticks.
pub const D_UID: &str = "league_ivern_d_uid";
/// The unit's name: the game draws it from asset/base/aseprite_resources/champions/<name>, which mod.override_info sends to
/// the main pack's league/champions/league_ivern_daisy (tools/art/unit_ivern_daisy.py).
pub const D_NAME: &str = "league_ivern_daisy";
/// The drop's picture (her climbing out of the ground: league_ivern_daisy_drop, 0.9 s) - the unit is asked for as it ends.
pub const D_FIRST: usize = 54;
/// Ticks she lives as a unit: the riding Daisy's 8 s (the kit's r_t; League's 45 s cut for this game's pace, Tibbers' too).
pub const D_LIFE: usize = 480;
/// She appears this far behind (up the screen from) the champion she dropped on: where the drop's picture stands her
/// (rig_ivern.py DAISY_BACK: her feet 9 game px behind his).
pub const D_BEHIND: f64 = 9_000.0;
/// Her punch: `D_HIT` + `D_HIT_AP` % of his ability power (the kit's r_dmg / r_ratio; her attack stat - a unit's attack is
/// physical), every `D_COOL` ticks (r_per), the swing `D_ACT` ticks long (her sheet's attack tag: 0.7 s) with the fist
/// down at `D_LANDS` (r_hit_at), reach `D_RANGE` (Tibbers').
pub const D_HIT: usize = 25;
pub const D_HIT_AP: usize = 20;
pub const D_COOL: usize = 60;
pub const D_ACT: usize = 42;
pub const D_LANDS: usize = 21;
pub const D_RANGE: usize = 15_000;
/// Every third punch on the same champion the slam: `D_SLAM` + `D_SLAM_AP` % of his ability power more, magic, and a
/// knock-up of `D_UP` ticks (the kit's r_slam / r_slam_r / r_up).
pub const D_SLAM: usize = 40;
pub const D_SLAM_AP: usize = 30;
pub const D_UP: u64 = 50;
/// Her body: `D_HP_PCT` % of his health cap, his armour and magic resistance + `D_DEF_MORE`, his move speed x
/// `D_SPEED_PCT` % (League's Daisy 430 against his 330).
pub const D_HP_PCT: usize = 120;
pub const D_DEF_MORE: usize = 20;
pub const D_SPEED_PCT: usize = 130;
/// Reach of her fist for the punch count by the clock: her reach and two bodies.
pub const D_BODIES: f64 = 12_000.0;
/// The main pack's pictures and sounds the natives play: the slam's shockwave, the hit, the slam's sound; her wave at the
/// end (only when the engine leaves no body to play her own `dead`).
pub const SHOCK_VIEW: &str = "league_ivern_r_shock";
pub const HIT_VIEW: &str = "league_ivern_r_hit";
pub const SLAM_SFX: &str = "league_ivern_r_slam";
pub const BYE_VIEW: &str = "league_ivern_r_bye";
/// Ticks the flag outlasts her time; ticks the handoff stays; ticks the passive waits for it; looks a handed-over id may
/// take to read as a unit.
const FLAG_MORE: usize = 30;
const UID_TICKS: usize = 6;
const ASK_WAIT: usize = 4;
const LOOK_TRIES: usize = 5;
/// A unit gone within this many ticks was never really there: the flag goes, the riding punches play on.
pub const LOST_AGE: usize = 6;

/// The test knobs (`league_ivern.cfg` beside the log, summon.rs), read once.
pub static KNOBS: std::sync::LazyLock<summon::Knobs> =
    std::sync::LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

fn fx(name: &str) -> String {
    format!("{ID}:{name}")
}

fn at_input(at: Pt) -> InputTargetV1 {
    InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64)
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

/// Daisy the unit from Ivern's numbers now (`stat`, his health cap `max_hp`).
pub fn daisy_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    summon::Spec {
        name: D_NAME.to_string(),
        life: D_LIFE,
        stat: StatV1 {
            attack: D_HIT + stat.magic_power * D_HIT_AP / 100,
            magic_power: stat.magic_power,
            hp: (max_hp * D_HP_PCT / 100).max(1),
            defence: stat.defence + D_DEF_MORE,
            magic_resistance: stat.magic_resistance + D_DEF_MORE,
            move_speed: (stat.move_speed * D_SPEED_PCT / 100).max(1),
            hp_regen: 0,
            stack: 0,
            crit_chance: 0,
        },
        attack: UnitAttackV1 {
            attack_ratio: 100,
            attack: 0,
            range: D_RANGE,
            cooltime: D_COOL,
            duration: D_ACT,
            start_timing: D_LANDS,
            cancelable: false,
            attack_type: AttackTypeV1::BaseAttack.code(),
        },
    }
}

/// The slam's magic damage before resistance, from his ability power.
pub fn slam_damage(ap: usize) -> usize {
    D_SLAM + ap * D_SLAM_AP / 100
}

/// One more punch of hers on `target`: (the champion she hit last, how many in a row on him) -> the new count, and
/// whether this one is the third in a row (the count starts again).
pub fn punch(last: Option<usize>, hits: usize, target: usize) -> (Option<usize>, usize, bool) {
    let n = if last == Some(target) { hits + 1 } else { 1 };
    if n >= 3 { (Some(target), 0, true) } else { (Some(target), n, false) }
}

/// Daisy spawned for Ivern `me` at `at`: the flag for the data and the handoff for the passive on him. `None` (and a
/// line): the host gave no unit, so she rides on the champion as before.
fn make_daisy(sim: &mut StableSim<'_>, me: usize, at: Pt, by: &str) -> Option<usize> {
    let (team, stat, max) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1))?;
    let spec = daisy_spec(&stat, max).with(&KNOBS);
    match summon::spawn(sim, me, team, at, &spec) {
        Some(id) => {
            sim.add_buff(me, &BuffV1::timed(D_UNIT, D_LIFE + FLAG_MORE));
            sim.add_buff(me, &BuffV1::timed(&summon::handoff(D_UID, id), UID_TICKS));
            if let Some(k) = tally(sim, "daisy spawn") {
                wlog(format!("{} DAISY SPAWN #{k} ({by}): unit #{id} for team {team} at {}: {}", head(sim, me), summon::pt(at),
                             spec.shown()));
            }
            Some(id)
        }
        None => {
            if let Some(k) = tally(sim, "daisy fail") {
                wlog(format!("{} DAISY SPAWN FAILED #{k} ({by}): spawn_unit gave no unit for '{}' at {} - she rides on the \
                              champion as before", head(sim, me), spec.name, summon::pt(at)));
            }
            None
        }
    }
}

/// `:daisy` - the passive queues it as the drop's picture ends; the input is where she stands.
pub struct DaisyFx;

impl StableEffectType for DaisyFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let at = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Pos) => (input.x as f64, input.y as f64),
            _ => match sim.get_entity(caster) {
                Some(e) => summon::at_of(&e),
                None => return,
            },
        };
        make_daisy(sim, caster, at, "the queued effect");
    }
}

/// The slam on `target`: magic damage, the knock-up unless he is immune to crowd control or an epic monster, the
/// shockwave and the hit on him, the slam's sound. -> whether he was knocked up.
fn slam(sim: &mut StableSim<'_>, me: usize, target: usize, ap: usize) -> bool {
    let Some((alive, unmoved)) = sim.get_entity(target).map(|u| {
        (u.is_alive(), (0..u.buff_count()).filter_map(|i| u.buff_at(i)).any(|b| b.cc_immune)
            || matches!(u.kind(), Some(EntityKindV1::Epic | EntityKindV1::Serpen)))
    }) else {
        return false;
    };
    if !alive {
        return false;
    }
    let on = InputTargetV1::target(target);
    sim.deal_damage_typed(me, target, slam_damage(ap), DamageTypeV1::Ap, AttackTypeV1::Skill);
    sim.play_view_effect(SHOCK_VIEW, me, &on, 0, 0, 0);
    sim.play_view_effect(HIT_VIEW, me, &on, 0, 0, 0);
    sim.play_sfx(SLAM_SFX, me, &on);
    let up = !unmoved && sim.get_entity(target).is_some_and(|e| e.is_alive());
    if up {
        sim.apply_cc(target, &CcV1::of_kind(CcKindV1::Airborne, D_UP));
    }
    up
}

// ===================== 被动里小菊的那一份 =====================

/// How far a Daisy has come.
#[derive(Clone, Copy, Debug, PartialEq)]
enum Stage {
    /// The drop's picture plays: the champion she dropped on, where he stands, the tick of the drop.
    Drop(usize, Pt, usize),
    /// The unit asked for at this tick, at this spot: its handoff is awaited.
    Asked(usize, Pt),
    /// The handed-over unit: id, the tick it was asked for, looks so far.
    Fresh(usize, usize, usize),
}

/// Daisy as a unit, as the passive keeps her.
#[derive(Clone, Debug)]
struct Live {
    unit: summon::Unit,
    /// His passive heard her punches (on_attack under her id): then those are counted, not the clock.
    heard: bool,
    /// The clock's next presumed punch while a champion is in her reach.
    next: Option<usize>,
    /// The champion punched last and how many in a row; slams by the hook, by the clock; knock-ups.
    last: Option<usize>,
    hits: usize,
    slams: (usize, usize, usize),
}

/// Ivern's Daisy part of league_ivern's passive.
#[derive(Clone, Default)]
pub struct Daisy {
    me: usize,
    stage: Option<Stage>,
    live: Option<Live>,
    wake: Option<summon::Wake>,
    n: usize,
}

impl Daisy {
    pub fn spawned(&mut self, sim: &mut StableSim<'_>, me: usize) {
        // a new life is a new entity: Daisy of the old one is no longer his to watch
        if let Some(live) = self.live.take() {
            wlog(format!("{} DAISY #{}: the unit #{} still on the books at his respawn (his death did not reach on_dead) - let \
                          go", head(sim, me), live.unit.n, live.unit.id));
        }
        *self = Daisy { me, n: self.n, ..Daisy::default() };
    }

    pub fn dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        (self.stage, self.wake) = (None, None);
        let Some(live) = self.live.take() else { return };
        let me = sim.get_player(player).and_then(|p| p.champion()).map_or(self.me, |e| e.id());
        let (tick, u) = (sim.tick(), &live.unit);
        if let Some(k) = tally(sim, "daisy orphan") {
            wlog(format!("{} DAISY #{} ORPHAN #{k}: Ivern died, Daisy #{} at {} has {} ticks left and hp {}/{} - she fights on \
                          unwatched (no more slams)", head(sim, me), u.n, u.id, summon::pt(u.at), u.left(tick), u.hp, u.max));
        }
    }

    /// One punch of hers on `target` (heard or presumed): the third in a row on him is the slam.
    fn punched(&mut self, sim: &mut StableSim<'_>, target: usize, by: &str) {
        let me = self.me;
        let Some(live) = self.live.as_mut() else { return };
        let (last, hits, third) = punch(live.last, live.hits, target);
        (live.last, live.hits) = (last, hits);
        if !third {
            return;
        }
        let ap = sim.get_entity(me).map_or(0, |e| e.stat().magic_power);
        let up = slam(sim, me, target, ap);
        let s = &mut live.slams;
        if by == "the hook" { s.0 += 1 } else { s.1 += 1 }
        s.2 += usize::from(up);
        let n = live.unit.n;
        if let Some(k) = tally(sim, "daisy slam") {
            let name = sim.get_entity(target).and_then(|e| e.name()).unwrap_or_default();
            wlog(format!("{} DAISY #{n} SLAM #{k} (by {by}): the third punch in a row on #{target} {name} - {} magic{}",
                         head(sim, me), slam_damage(ap), if up { format!(", knocked up {D_UP} ticks") } else { ", no knock-up".into() }));
        }
    }

    /// His passive's on_attack: a punch of hers when it names her (summon.rs's question: does a summon's attack reach
    /// its summoner's passive, under whose id?), and the line for it.
    pub fn hooked(&mut self, sim: &mut StableSim<'_>, hook: &str, entity: usize, other: usize, damage: Option<usize>) {
        let Some(live) = self.live.as_mut() else { return };
        if let Some(k) = tally(sim, "daisy hook") {
            wlog(format!("{} DAISY #{} HOOK #{k} {hook}: {}{}", head(sim, self.me), live.unit.n,
                         live.unit.hook_text(sim, entity, other, self.me), damage.map(|d| format!(", damage {d}")).unwrap_or_default()));
        }
        if hook != "on_attack" || entity != live.unit.id {
            return;
        }
        if !live.heard {
            // from now on her punches are counted as heard: the clock's count starts again
            (live.heard, live.next, live.last, live.hits) = (true, None, None, 0);
        }
        let is_champion = sim.get_entity(other).is_some_and(|e| e.is_champion());
        if is_champion {
            self.punched(sim, other, "the hook");
        }
    }

    /// His tick while he lives: R's mark seen, the unit asked for as the drop's picture ends, looked at, watched.
    pub fn update(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        let tick = sim.tick();
        let Some((team, here)) = sim.get_entity(me).map(|e| (e.team(), summon::at_of(&e))) else { return };
        // a new Daisy: the copy's drop has just marked her champion
        let marked: Option<(usize, Pt)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_champion() && has_buff(u, D_MARK))
            .map(|u| (u.id(), summon::at_of(&u)))
            .next();
        if let Some((target, at)) = marked {
            sim.entity_remove_buff(target, D_MARK);
            if KNOBS.off {
                if let Some(k) = tally(sim, "daisy off") {
                    wlog(format!("{} DAISY OFF #{k}: R dropped her on #{target}, unit=off in the test knobs - she rides on him as \
                                  before", head(sim, me)));
                }
            } else {
                self.stage = Some(Stage::Drop(target, at, tick));
            }
        }
        match self.stage {
            Some(Stage::Drop(target, at, from)) => {
                // where the drop's picture stands her: behind her champion while he is there, else where he fell
                let at = sim.get_entity(target).filter(|e| e.is_alive()).map_or(at, |e| summon::at_of(&e));
                if tick + 1 >= from + D_FIRST {
                    let spot = (at.0, (at.1 - D_BEHIND).max(0.0));
                    let queued = sim.queue_effect(&fx("daisy"), AttackTypeV1::Skill, me, &at_input(spot), 1);
                    if !queued {
                        make_daisy(sim, me, spot, "queue_effect refused: spawned by the passive");
                    }
                    self.n += 1;
                    if let Some(k) = tally(sim, "daisy ask") {
                        wlog(format!("{} DAISY #{} ASK #{k}: the unit asked for at {} ({D_BEHIND:.0} behind #{target}, where the \
                                      drop's picture stands her){}", head(sim, me), self.n, summon::pt(spot),
                                     if queued { "" } else { " - queue_effect REFUSED" }));
                    }
                    self.stage = Some(Stage::Asked(tick, spot));
                } else {
                    self.stage = Some(Stage::Drop(target, at, from));
                }
            }
            Some(Stage::Asked(since, _)) => {
                if let Some(id) = summon::take_handoff(sim, me, D_UID) {
                    self.stage = Some(Stage::Fresh(id, since, 0));
                } else if tick > since + ASK_WAIT {
                    self.stage = None;
                    if let Some(k) = tally(sim, "daisy none") {
                        wlog(format!("{} DAISY #{} NONE #{k}: no unit came within {ASK_WAIT} ticks of the ask - she rides on the \
                                      champion as before", head(sim, me), self.n));
                    }
                }
            }
            _ => {}
        }
        if let Some(Stage::Fresh(id, born, tries)) = self.stage {
            match summon::Unit::look(sim, id, self.n, born, D_LIFE, team, player) {
                // taken on once she has settled (summon.rs's Unit::settled: a new unit reads max health 1 and every stat
                // 1 on its spawn tick and the next - game 0.7.2's presims), so her LOOK line shows the numbers she really
                // has; when her looks run out, all the same
                Ok((unit, line)) if unit.settled() || tries + 1 >= LOOK_TRIES => {
                    self.stage = None;
                    if let Some(k) = tally(sim, "daisy look") {
                        wlog(format!("{} DAISY #{} LOOK #{k}: {line}{}", head(sim, me), self.n, unit.unsettled_note(tries + 1)));
                    }
                    if let Some(old) = self.live.take() {
                        wlog(format!("{} DAISY #{}: the unit #{} of an earlier one is still out - no longer watched", head(sim, me),
                                     self.n, old.unit.id));
                    }
                    self.live = Some(Live { unit, heard: false, next: None, last: None, hits: 0, slams: (0, 0, 0) });
                }
                Err(why) if tries + 1 >= LOOK_TRIES => {
                    self.stage = None;
                    sim.entity_remove_buff(me, D_UNIT);
                    if let Some(k) = tally(sim, "daisy lost") {
                        wlog(format!("{} DAISY #{} LOST #{k}: the unit spawn_unit named never read as one in {LOOK_TRIES} ticks \
                                      ({why}) - the flag is off, she rides on the champion as before", head(sim, me), self.n));
                    }
                }
                _ => self.stage = Some(Stage::Fresh(id, born, tries + 1)),
            }
            return;
        }
        let Some(mut live) = self.live.take() else {
            self.wake_step(sim, me);
            return;
        };
        let n = live.unit.n;
        match live.unit.step(sim, Some(here)) {
            summon::Step::Alive(line) => {
                // counted only when there is a line (a count every tick let the presims' first 40 and every 200th go by
                // ticks, not lines: hardly a line a second got through)
                if let Some(line) = line {
                    if let Some(k) = tally(sim, "daisy unit") {
                        wlog(format!("{} DAISY #{n} #{k}: {line}", head(sim, me)));
                    }
                }
                // her punches by the clock while his passive hears none: a champion in her reach is punched every D_COOL
                let mut presumed = None;
                if !live.heard {
                    let near = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
                        .filter(|u| u.team() != team && u.is_champion() && u.is_alive() && u.is_targetable())
                        .map(|u| (u.id(), summon::dist(summon::at_of(&u), live.unit.at)))
                        .filter(|u| u.1 <= D_RANGE as f64 + D_BODIES)
                        .min_by(|a, b| a.1.total_cmp(&b.1))
                        .map(|u| u.0);
                    match (near, live.next) {
                        (Some(_), None) => live.next = Some(tick + D_LANDS),
                        (Some(c), Some(t)) if tick >= t => {
                            live.next = Some(t + D_COOL);
                            presumed = Some(c);
                        }
                        (None, _) => live.next = None,
                        _ => {}
                    }
                }
                self.live = Some(live);
                if let Some(c) = presumed {
                    self.punched(sim, c, "the clock");
                }
            }
            summon::Step::Over(end) => {
                let s = live.slams;
                if let Some(k) = tally(sim, "daisy over") {
                    wlog(format!("{} DAISY #{n} OVER #{k}: {}; her slams: {} by the hook, {} by the clock, {} knocked up{}",
                                 head(sim, me), end.text, s.0, s.1, s.2,
                                 if live.heard { "; her punches reached his passive" } else { "; none of her punches reached his passive" }));
                }
                if end.age <= LOST_AGE {
                    // never really there: the riding punches go on
                    sim.entity_remove_buff(me, D_UNIT);
                    wlog(format!("{} DAISY #{n}: gone {} ticks after it was asked for - the flag is off, she rides on the champion \
                                  as before", head(sim, me), end.age));
                } else if !end.body {
                    // no body left for the engine to play her `dead` on: her wave where she stood, her feet on her ground
                    sim.play_view_effect(BYE_VIEW, me, &at_input((end.at.0, end.at.1 + D_BEHIND)), 0, 0, 0);
                }
                self.wake = Some(live.unit.wake(sim, &end));
            }
        }
        self.wake_step(sim, me);
    }

    fn wake_step(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if let Some(mut w) = self.wake.take() {
            let (lines, over) = w.step(sim);
            for line in lines {
                if let Some(k) = tally(sim, "daisy wake") {
                    wlog(format!("{} DAISY #{} WAKE #{k}: {line}", head(sim, me), w.n));
                }
            }
            if !over {
                self.wake = Some(w);
            }
        }
    }
}

/// The load line, and `:daisy` registered.
pub fn register(module: &mut StableMod) {
    wlog(format!(
        "DAISY: Daisy is a unit of her own ('{}', spawn_unit) - {}; {D_LIFE} ticks, {D_HIT} + {D_HIT_AP}% of his ability power a \
         punch every {D_COOL} ticks, every third on the same champion {D_SLAM} + {D_SLAM_AP}% more and a knock-up of {D_UP} \
         ticks. Test knobs ({}): {}",
        KNOBS.name.as_deref().unwrap_or(D_NAME),
        if KNOBS.off { "OFF by the test knobs: she rides on the champion as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(),
        KNOBS.shown()
    ));
    module.add_native_effect(fx("daisy"), DaisyFx);
}

#[cfg(test)]
#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn daisy_is_built_from_his_numbers() {
        let his = StatV1 { attack: 50, magic_power: 100, hp: 900, defence: 30, magic_resistance: 25, move_speed: 1000, hp_regen: 2,
                           stack: 1, crit_chance: 5 };
        let spec = daisy_spec(&his, 1500);
        assert_eq!((spec.name.as_str(), spec.life), ("league_ivern_daisy", 480));
        // a punch 25 + 20 % of 100 = 45; health 120 % of 1500; his defences + 20; 130 % of his speed
        assert_eq!(spec.stat, StatV1 { attack: 45, magic_power: 100, hp: 1800, defence: 50, magic_resistance: 45, move_speed: 1300,
                                       hp_regen: 0, stack: 0, crit_chance: 0 });
        let a = spec.attack;
        assert_eq!(a.attack + spec.stat.attack * a.attack_ratio / 100, 45);
        assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (15_000, 60, 42, 21));
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        assert_eq!(daisy_spec(&StatV1::default(), 0).stat.hp, 1);
        assert_eq!(slam_damage(100), 70);
        for name in [D_MARK, D_UNIT, &summon::handoff(D_UID, usize::MAX)] {
            assert!(name.len() <= BUFF_NAME_CAP, "{name}");
        }
        // asked for as the drop's picture ends, the flag on before the riding punches' second run
        assert!(D_FIRST + ASK_WAIT < D_COOL && LOST_AGE < D_COOL);
    }

    #[test]
    fn the_third_punch_in_a_row_on_one_champion_is_the_slam() {
        let (mut last, mut hits) = (None, 0);
        let mut slams = Vec::new();
        for (k, t) in [1, 1, 1, 1, 2, 1, 1, 1, 1].into_iter().enumerate() {
            let (l, h, third) = punch(last, hits, t);
            (last, hits) = (l, h);
            if third {
                slams.push(k);
            }
        }
        // 1 1 1 -> slam; 1 then 2 breaks the row; 1 1 1 again -> slam
        assert_eq!(slams, vec![2, 7]);
    }

    #[test]
    fn the_copy_lets_the_unit_take_her_place() {
        let copy = include_str!("../override/league_ivern.data_champion").replace('\r', "");
        let main = include_str!("../../../league/champion/league_ivern.data_champion").replace('\r', "");
        assert!(!main.contains(D_UNIT) && !main.contains(D_MARK));
        // the riding punches and her wave each behind the flag; the drop marks the champion
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{D_UNIT}\"")).count(), 2);
        assert_eq!(copy.matches(&format!("\"name\": \"{D_MARK}\"")).count(), 1);
        // the sheet the unit is drawn from is mapped to its name
        let info = include_str!("../mod.override_info");
        for k in ["sheet", "anim"] {
            assert!(info.contains(&format!("\"asset/base/aseprite_resources/champions/{D_NAME}#{k}\"")), "{k}");
            assert!(info.contains(&format!("\"asset/league/champions/{D_NAME}#{k}\"")), "{k}");
        }
    }

    // ---- Daisy on the mock world (summon_mock.rs: our guess of the host, to check this side's logic) ----

    use super::mock::{champion, MPlayer, World};

    const GAREN: usize = 1;
    const DARIUS: usize = 2;

    fn log_file() -> PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_ivern_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_IVERN_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// Ivern #0 (team 0, 100 ability power, 1500 health) at (300000, 300000); Garen #1 60000 east of him, Darius #2 20000
    /// beyond; a player each.
    fn world() -> (World, Daisy) {
        log_file();
        let mut w = World::default();
        let mut iv = champion("league_ivern", 0, 300_000.0, 300_000.0);
        (iv.hp, iv.max, iv.stat.magic_power, iv.stat.defence, iv.stat.magic_resistance, iv.stat.move_speed) = (1500, 1500, 100, 30, 25, 1000);
        let mut garen = champion("league_garen", 1, 360_000.0, 300_000.0);
        (garen.hp, garen.max) = (5000, 5000);
        let mut darius = champion("league_darius", 1, 380_000.0, 300_000.0);
        (darius.hp, darius.max) = (5000, 5000);
        w.units = vec![iv, garen, darius];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() },
                         MPlayer { team: 1, champion: DARIUS, ..Default::default() }];
        let mut me = Daisy::default();
        w.sim(|sim| me.spawned(sim, 0));
        (w, me)
    }

    fn tick(w: &mut World, me: &mut Daisy) {
        for (name, caster, input) in w.due() {
            w.sim(|sim| match name.as_str() {
                "league_ivern:daisy" => DaisyFx.apply(sim, 0, caster, input),
                other => panic!("an effect nobody registered: {other}"),
            });
        }
        if w.units[0].hp > 0 {
            w.sim(|sim| me.update(sim, 0, 0));
        }
        w.step();
    }

    fn run(w: &mut World, me: &mut Daisy, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    /// The copy's drop as the data lays it: the mark on its champion.
    fn drop_on(w: &mut World, target: usize) -> usize {
        w.units[target].buffs.push((BuffV1::timed(D_MARK, 3), 3));
        w.tick
    }

    fn slams(w: &World, target: usize) -> usize {
        w.dealt(0, DamageTypeV1::Ap).iter().filter(|d| **d == (target, slam_damage(100))).count()
    }

    #[test]
    fn daisy_is_taken_on_once_her_numbers_read() {
        // game 0.7.2's presims: a new unit reads max health 1 and every stat 1 on its spawn tick and the next (World::settle)
        let (mut w, mut me) = world();
        w.settle = 2;
        drop_on(&mut w, GAREN);
        run(&mut w, &mut me, D_FIRST + 2);
        assert_eq!(w.spawns.len(), 1);
        let spawned = w.spawns[0].tick;
        run(&mut w, &mut me, 5);
        let live = me.live.as_ref().expect("never taken on");
        assert!(live.unit.settled() && live.unit.max == 1800);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let look = text.lines().find(|l| l.contains(" DAISY #") && l.contains(" LOOK #") && l.contains(&format!("t={} ", spawned + 2)));
        assert!(look.is_some_and(|l| l.contains("hp 1800/1800 attack 45 def 50") && !l.contains("still reads")), "{look:?}");
        assert!(w.has(0, D_UNIT));
    }

    #[test]
    fn daisy_is_a_unit_that_walks_punches_and_slams() {
        let (mut w, mut me) = world();
        let t0 = drop_on(&mut w, GAREN);
        run(&mut w, &mut me, D_FIRST - 3);
        assert!(w.spawns.is_empty(), "the unit came before the drop's picture ended");
        run(&mut w, &mut me, 6);
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life), ("league_ivern_daisy", 0, 0, 480));
        assert_eq!(s.at, (360_000, 291_000));
        assert!(s.tick + 1 >= t0 + D_FIRST && s.tick <= t0 + D_FIRST + 1, "spawned {} ticks after the drop", s.tick - t0);
        assert_eq!((s.stat.attack, s.stat.hp, s.stat.defence, s.stat.magic_resistance, s.stat.move_speed), (45, 1800, 50, 45, 1300));
        let daisy = s.gave.unwrap();
        assert!(w.has(0, D_UNIT) && !w.has(GAREN, D_MARK));
        assert!(me.live.is_some());
        // her time: she punches Garen (45 a punch, physical), every third punch in a row is the slam - his passive hears
        // none of her punches in this world, so they are counted by the clock: punches 21, 81, 141 (slam), .. 321 (slam)
        run(&mut w, &mut me, D_LIFE + 10);
        let punches = w.dealt(daisy, DamageTypeV1::Ad);
        assert!(punches.len() >= 7 && punches.iter().all(|p| *p == (GAREN, 45)), "{punches:?}");
        assert_eq!(slams(&w, GAREN), 2);
        assert_eq!(w.viewed(SHOCK_VIEW), 2);
        assert!(!w.units[daisy].valid);
        assert!(me.live.is_none() && me.stage.is_none() && w.queue.is_empty());
        // no body left to play her own death on: her wave where she stood
        assert_eq!(w.viewed(BYE_VIEW), 1);
    }

    #[test]
    fn heard_punches_are_counted_instead_of_the_clock() {
        let (mut w, mut me) = world();
        drop_on(&mut w, GAREN);
        run(&mut w, &mut me, D_FIRST + 3);
        let daisy = w.spawns[0].gave.unwrap();
        // the engine tells his passive of three punches of hers on Garen: the third is the slam, at once
        for _ in 0..3 {
            w.sim(|sim| me.hooked(sim, "on_attack", daisy, GAREN, Some(45)));
        }
        assert_eq!(slams(&w, GAREN), 1);
        // a punch on Darius breaks the row; the clock counts no more
        w.sim(|sim| me.hooked(sim, "on_attack", daisy, DARIUS, Some(45)));
        w.sim(|sim| me.hooked(sim, "on_attack", daisy, GAREN, Some(45)));
        w.sim(|sim| me.hooked(sim, "on_attack", daisy, GAREN, Some(45)));
        assert_eq!(slams(&w, GAREN), 1);
        run(&mut w, &mut me, 300);
        assert_eq!(slams(&w, GAREN), 1, "the clock slammed beside the heard punches");
        // his own attacks are no punches of hers
        for _ in 0..3 {
            w.sim(|sim| me.hooked(sim, "on_attack", 0, GAREN, Some(60)));
        }
        assert_eq!(slams(&w, GAREN), 1);
    }

    #[test]
    fn no_unit_from_the_host_leaves_her_riding_on_the_champion() {
        // no such slot, a refusal, an id that never reads as a unit, a unit gone at once
        for case in 0..4 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                2 => w.spawn_never = true,
                _ => {}
            }
            let t0 = drop_on(&mut w, GAREN);
            if case == 3 {
                run(&mut w, &mut me, D_FIRST + 2);
                assert!(me.live.is_some(), "case 3");
                let id = w.spawns[0].gave.unwrap();
                w.units[id].valid = false;
            }
            while w.tick < t0 + D_COOL {
                tick(&mut w, &mut me);
            }
            // the riding punches' second run reads the flag now: off, so they play on
            assert!(!w.has(0, D_UNIT), "case {case}: the flag is on with no unit");
            run(&mut w, &mut me, 400);
            assert_eq!(slams(&w, GAREN), 0, "case {case}: slams without a unit");
            assert!(me.live.is_none() && me.stage.is_none() && w.queue.is_empty(), "case {case}");
        }
    }

    #[test]
    fn she_fights_on_when_ivern_dies() {
        let (mut w, mut me) = world();
        drop_on(&mut w, GAREN);
        run(&mut w, &mut me, D_FIRST + 100);
        let daisy = w.spawns[0].gave.unwrap();
        let before = w.dealt(daisy, DamageTypeV1::Ad).len();
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.dead(sim, 0));
        assert!(me.live.is_none());
        run(&mut w, &mut me, 200);
        assert!(w.dealt(daisy, DamageTypeV1::Ad).len() > before, "she stopped when he died");
        assert!(w.queue.is_empty());
    }

    #[test]
    fn the_log_tells_her_whole_life() {
        let (mut w, mut me) = world();
        drop_on(&mut w, GAREN);
        run(&mut w, &mut me, D_FIRST + 200);
        let daisy = w.spawns[0].gave.unwrap();
        w.sim(|sim| me.hooked(sim, "on_attack", daisy, GAREN, Some(45)));
        w.body_ticks = 30;
        w.players[1].gold += 40;
        w.hurt(daisy, 100_000);
        run(&mut w, &mut me, 60);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" DAISY ")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "ASK #", "the unit asked for at (360000,291000) (9000 behind #1, where the drop's picture stands her)",
            "DAISY SPAWN #", "'league_ivern_daisy' for 480 ticks, attack 45 ap 100 hp 1800 def 50 mr 45 speed 1300; hits 0 + 100% of \
             its attack, range 15000, every 60 ticks (42 long, lands at 21)",
            "LOOK #", "reads back as name 'league_ivern_daisy' kind summon team 0 champion=false",
            " of 480 ticks, at (", "near it: champion #1 league_garen",
            "SLAM #", "(by the clock): the third punch in a row on #1 league_garen - 70 magic, knocked up 50 ticks",
            "HOOK #", "on_attack: entity #3 (the unit itself) -> champion #1 league_garen", "damage 45",
            "OVER #", "KILLED after ", "p1 gold +40", "her slams: ", "her punches reached his passive",
            "WAKE #", "its body was there for ",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
        let longest = mine.iter().map(|l| l.len()).max().unwrap();
        assert!(longest < 700, "a line of {longest} bytes");
    }
}
