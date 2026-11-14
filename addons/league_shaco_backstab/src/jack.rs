//! 惊吓魔盒有了身体（0.3.0，2026-11-14；用户：「召唤物的全做啊 剩下的一批英雄也做了啊 都做完了装进去了再测」）。
//!
//! 英雄联盟（wiki 现行页面）：魔盒有生命（150–550）、护甲 50、魔抗 100，弹开时恐惧周围的敌人，之后 5 秒每 0.5 秒射一下，
//! 能被打掉（英雄的普攻一下打掉它三分之一），打掉给 10 金币。主包里魔盒是一张画面：落地的画面、弹开的画面、恐惧的区域和 5 秒
//! 的射击区域（`league_shaco_w_shots`：每 `W_EVERY` tick 打 `W_R` 内的敌人 `W_HIT` + `W_HIT_AP`% 法强），打不到。
//!
//! 本包（幻像那套之外，和它不相干——幻像的代码、`summon.rs` 都没动）：
//! - 副本的 W 落地时（抛物线的 end_effects）跑原生效果 [`JackFx`]（`:jack`）：在落点生成身体 `league_shaco_jack`（[`jack_spec`]：
//!   移速 1、攻击 0 伤害——只为了朝着敌人、播射一下的动作，生命是他上限的 `JACK_HP_PCT`%），马上放逐 `W_WAIT - 1` tick（主包
//!   落地的画面照放，弹开时身体出来），成功了给他挂 `W_UNIT`：副本的数据在弹开那一 tick 读它，不画弹开的画面、不放射击区域
//!   （恐惧和声音照旧是数据的）。
//! - 被动（[`Jacks::tick`]）：从弹开后第 `W_FIRST` tick 起每 `W_EVERY` tick 由他打一轮（[`volley`]：身体现在站的地方 `W_R` 内的
//!   每个敌人 `W_HIT` + `W_HIT_AP`% 法强的魔法伤害，主包的命中画面），共 `W_SHOTS` 轮；身体被打掉就停。萨科先死了：剩下的几轮
//!   排成原生效果 [`ShotFx`]（`:jack_shot`，排好的效果对死了的施法者也跑——幻像的 `:end` 也这样）。
//! - 退路：宿主没有 `spawn_unit`、失败、读不成单位、测试开关 `unit=off`——不挂 `W_UNIT`，数据照主包放画面和射击区域。
//! - 日志：`JACK` 开头的行。

use mod_api_stable::*;

use super::summon::{self, Event, Flock, Pt};
use super::{at_input, fx, head, point, tally, wlog, KNOBS, SHOT_VIEW};

/// The body's unit name: the game draws it from asset/base/aseprite_resources/champions/<name>, which mod.override_info
/// sends to the main pack's league/champions/league_shaco_jack (tools/art/unit_shaco_jack.py: the box's own 1x frames).
pub const JACK: &str = "league_shaco_jack";
/// On him from a body's spawn: the copy's data draws no spring picture and lays no shooting zone (`FLAG_TICKS`).
pub const W_UNIT: &str = "league_shaco_w_unit";
pub const W_UID: &str = "league_shaco_w_uid";
/// The main pack's box (checked by make_override.py against the data): it springs `W_WAIT` ticks after it lands, shoots
/// from `W_FIRST` ticks after that every `W_EVERY` ticks for `W_TIME` ticks (`W_SHOTS` volleys) at every enemy within
/// `W_R`: `W_HIT` + `W_HIT_AP` % of his ability power, magic.
pub const W_WAIT: usize = 10;
pub const W_FIRST: usize = 1;
pub const W_EVERY: usize = 30;
pub const W_TIME: usize = 300;
pub const W_SHOTS: usize = 10;
pub const W_R: usize = 35_000;
pub const W_HIT: usize = 10;
pub const W_HIT_AP: usize = 12;
/// The sheet's shot: ticks long and the tick the shot frame starts (checked by make_override.py).
pub const JACK_ACT: usize = 18;
pub const JACK_LANDS: usize = 4;
/// League (wiki, 2026-11-14): health 150-550 against his 587-2270 (25 %), armour 50 against his 30-101 (about all of it),
/// magic resistance 100 against his 32-54 (about 190 %).
pub const JACK_HP_PCT: usize = 25;
pub const JACK_DEF_PCT: usize = 100;
pub const JACK_MR_PCT: usize = 190;
const FLAG_TICKS: usize = 15;
const UID_TICKS: usize = 6;
const JACK_CAP: usize = 4;
/// A body gone within this many ticks was never really there.
const LOST_AGE: usize = 6;

/// The box's body from his numbers now (`stat`, his health cap `max_hp`): move speed 1, a harmless shot in the box's
/// reach and pace (it faces its target and plays the shot; the add-on's natives fire).
pub fn jack_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    summon::Spec {
        name: JACK.to_string(),
        life: W_WAIT + W_TIME + 2,
        stat: StatV1 { attack: 0, magic_power: stat.magic_power, hp: (max_hp * JACK_HP_PCT / 100).max(1),
                       defence: stat.defence * JACK_DEF_PCT / 100, magic_resistance: stat.magic_resistance * JACK_MR_PCT / 100,
                       move_speed: 1, hp_regen: 0, stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: 0, attack: 0, range: W_R, cooltime: W_EVERY, duration: JACK_ACT, start_timing: JACK_LANDS,
                               cancelable: false, attack_type: AttackTypeV1::BaseAttack.code() },
    }
}

/// A volley's magic damage (before resistances).
pub fn volley_damage(ap: usize) -> usize {
    W_HIT + ap * W_HIT_AP / 100
}

/// One volley from `at`: every enemy of his within `W_R` (no tower, no nexus) takes `volley_damage` as magic, with the main
/// pack's hit picture. -> how many it hit.
pub fn volley(sim: &mut StableSim<'_>, me: usize, at: Pt) -> usize {
    let Some((team, ap)) = sim.get_entity(me).map(|e| (e.team(), e.stat().magic_power)) else { return 0 };
    let dmg = volley_damage(ap);
    let hit: Vec<usize> = summon::foes_near(sim, team, at, W_R as f64).into_iter()
        .filter(|f| f.kind != "tower" && f.kind != "nexus")
        .map(|f| f.id)
        .collect();
    for id in &hit {
        sim.deal_damage_typed(me, *id, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
        sim.play_view_effect(SHOT_VIEW, me, &InputTargetV1::target(*id), 0, 0, 0);
    }
    hit.len()
}

/// `:jack` - the copy's W landing (its spot is the input): the box's body, banished until it springs.
pub struct JackFx;

impl StableEffectType for JackFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        sim.entity_remove_buff(caster, W_UNIT);
        let Some(at) = point(&input).or_else(|| {
            (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target))
                .then(|| sim.get_entity(input.target_id).map(|e| summon::at_of(&e))).flatten()
        }) else {
            if let Some(k) = tally(sim, "jack input") {
                wlog(format!("{} JACK NO SPOT #{k}: the box landed with input kind {} - no body, the main pack's box", head(sim, caster),
                             input.kind));
            }
            return;
        };
        if KNOBS.off {
            if let Some(k) = tally(sim, "jack knob") {
                wlog(format!("{} JACK OFF #{k}: unit=off in the test knobs - the main pack's box", head(sim, caster)));
            }
            return;
        }
        let Some((team, stat, max)) = sim.get_entity(caster).map(|e| (e.team(), e.stat(), e.hp().1)) else { return };
        let spec = jack_spec(&stat, max).with(&KNOBS);
        let spot = summon::inside(summon::field(sim), at);
        match summon::spawn(sim, caster, team, spot, &spec) {
            Some(id) => {
                sim.add_buff(caster, &BuffV1::timed(&summon::handoff(W_UID, id), UID_TICKS));
                sim.add_buff(caster, &BuffV1::timed(W_UNIT, FLAG_TICKS));
                let hidden = sim.entity_banish(caster, id, W_WAIT - 1, "", "");
                if let Some(k) = tally(sim, "jack spawn") {
                    wlog(format!("{} JACK SPAWN #{k}: the box's body, unit #{id} for team {team} at {}, banished until it springs: {}: \
                                  {}", head(sim, caster), summon::pt(spot), if hidden { "yes" } else { "REFUSED" }, spec.shown()));
                }
            }
            None => {
                if let Some(k) = tally(sim, "jack fail") {
                    wlog(format!("{} JACK SPAWN FAILED #{k}: spawn_unit gave no unit for '{}' at {} - the main pack's box",
                                 head(sim, caster), spec.name, summon::pt(spot)));
                }
            }
        }
    }
}

/// `:jack_shot` - one volley where the input says (Shaco died: his passive does not run, these were queued at his death).
pub struct ShotFx;

impl StableEffectType for ShotFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if let Some(at) = point(&input) {
            let n = volley(sim, caster, at);
            if let Some(k) = tally(sim, "jack orphan shot") {
                wlog(format!("{} JACK ORPHAN SHOT #{k}: a volley at {} for its dead summoner hit {n}", head(sim, caster), summon::pt(at)));
            }
        }
    }
}

/// A box as the passive keeps it: its next volley, volleys fired.
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct JackBook {
    pub next: usize,
    pub shots: usize,
}

/// His boxes' bodies.
#[derive(Clone)]
pub struct Jacks {
    pub flock: Flock<JackBook>,
}

impl Default for Jacks {
    fn default() -> Self {
        Jacks { flock: Flock::new(W_UID, JACK_CAP, W_WAIT + W_TIME + 2) }
    }
}

impl Jacks {
    /// The boxes' part of a tick: the flock looked at, the volleys due.
    pub fn tick(&mut self, sim: &mut StableSim<'_>, me: usize, player: usize, team: usize, here: Pt) {
        let tick = sim.tick();
        for ev in self.flock.tick(sim, me, team, player, Some(here)) {
            match ev {
                Event::NoUnit { .. } => {}
                Event::Look { id, n, line } => {
                    let mut hide = 0;
                    if let Some(m) = self.flock.get_mut(id) {
                        m.extra.next = m.unit.born + W_WAIT + W_FIRST;
                        hide = (m.unit.born + W_WAIT).saturating_sub(tick);
                    }
                    // the live game (2026-11-14): what is done to a unit on its spawn tick may be overwritten - still seen
                    // before it springs: banished again for the rest of the wait
                    let again = hide > 1 && sim.get_entity(id).is_some_and(|e| e.is_targetable())
                        && sim.entity_banish(me, id, hide - 1, "", "");
                    if let Some(k) = tally(sim, "jack look") {
                        wlog(format!("{} JACK #{n} LOOK #{k}: {line}{}", head(sim, me),
                                     if again { format!(" - targetable before it springs: banished again for {} ticks", hide - 1) } else { String::new() }));
                    }
                }
                Event::Lost { id, why, .. } => {
                    sim.entity_remove_buff(me, W_UNIT);
                    if let Some(k) = tally(sim, "jack lost") {
                        wlog(format!("{} JACK LOST #{k}: the unit #{id} spawn_unit named never read as one in {} ticks ({why}){}",
                                     head(sim, me), summon::FLOCK_LOOKS,
                                     " - the flag is off: the main pack's box springs if it has not yet"));
                    }
                }
                Event::Line { n, line, .. } => {
                    if let Some(k) = tally(sim, "jack unit") {
                        wlog(format!("{} JACK #{n} #{k}: {line}", head(sim, me)));
                    }
                }
                Event::Over { member, end } => {
                    if end.age <= LOST_AGE {
                        sim.entity_remove_buff(me, W_UNIT);
                    }
                    let then = if end.fate == summon::Fate::Killed {
                        format!(" - the box is broken: {} of {W_SHOTS} volleys fired", member.extra.shots)
                    } else {
                        format!(" - {} of {W_SHOTS} volleys fired", member.extra.shots)
                    };
                    if let Some(k) = tally(sim, "jack over") {
                        wlog(format!("{} JACK #{} OVER #{k}: {}{then}", head(sim, me), member.unit.n, end.text));
                    }
                }
                Event::LetGo { member } => {
                    if let Some(k) = tally(sim, "jack let go") {
                        wlog(format!("{} JACK #{} LET GO #{k}: {JACK_CAP} boxes on the books - the unit #{} is out there, no longer \
                                      watched", head(sim, me), member.unit.n, member.unit.id));
                    }
                }
                Event::Wake { n, line } => {
                    if let Some(k) = tally(sim, "jack wake") {
                        wlog(format!("{} JACK #{n} WAKE #{k}: {line}", head(sim, me)));
                    }
                }
            }
        }
        let due: Vec<(usize, Pt)> = self.flock.live.iter()
            .filter(|m| m.extra.shots < W_SHOTS && m.extra.next > 0 && tick >= m.extra.next)
            .map(|m| (m.unit.id, m.unit.at))
            .collect();
        for (id, at) in due {
            let n = volley(sim, me, at);
            if let Some(m) = self.flock.get_mut(id) {
                m.extra.shots += 1;
                m.extra.next += W_EVERY;
                if let Some(k) = tally(sim, "jack shot") {
                    wlog(format!("{} JACK #{} SHOT #{k}: volley {} of {W_SHOTS} from {} hit {n}", head(sim, me), m.unit.n, m.extra.shots,
                                 summon::pt(at)));
                }
            }
        }
    }

    /// Shaco died: the volleys his boxes still owe are queued where each stands (his passive does not run while he is dead).
    pub fn on_dead(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let tick = sim.tick();
        for m in self.flock.orphans() {
            let left = W_SHOTS.saturating_sub(m.extra.shots);
            let mut queued = 0;
            for k in 0..left {
                let due = m.extra.next.max(tick + 1) + k * W_EVERY;
                if sim.queue_effect(&fx("jack_shot"), AttackTypeV1::Skill, me, &at_input(m.unit.at), due - tick) {
                    queued += 1;
                }
            }
            if let Some(k) = tally(sim, "jack orphan") {
                wlog(format!("{} JACK #{} ORPHAN #{k}: Shaco died - its {left} volleys left queued where it stands: {queued} taken",
                             head(sim, me), m.unit.n));
            }
        }
    }

    /// A line for a hook that fired while boxes of his are out.
    pub fn hooked(&self, sim: &StableSim<'_>, hook: &str, me: usize, entity: usize, other: usize, damage: Option<usize>) {
        let Some(m) = self.flock.get(entity) else { return };
        if let Some(k) = tally(sim, "jack hook") {
            wlog(format!("{} JACK HOOK #{k} {hook}: entity #{entity} (the box #{}) -> #{other}{}", head(sim, me), m.unit.n,
                         damage.map(|d| format!(", damage {d}")).unwrap_or_default()));
        }
    }
}

