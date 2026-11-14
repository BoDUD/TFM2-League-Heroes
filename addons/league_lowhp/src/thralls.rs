//! 丽桑卓的冰仆是真的单位（0.3.1，2026-11-14；用户：「召唤物的全做啊 剩下的一批英雄也做了啊 都做完了装进去了再测」）。
//!
//! 英雄联盟（wiki 现行页面，V26.10）：附近的敌方英雄阵亡时从他的尸体里站起一个冰仆，追着附近看得见的敌人走 4 秒（先追英雄，
//! 速度从 33 涨到 325），让附近的敌人减速 25%，4 秒后碎裂，对附近的敌人造成 120–520 + 50% 法强的魔法伤害；冰仆选不中、
//! 打不死。本包原来（`lib.rs` 的 `Thralls`）在尸体处放冰仆的画面，`THRALL_TICKS` 后扑向 `THRALL_LUNGE` 内最近的敌人碎裂。
//!
//! 现在（这个文件；`lib.rs` 只多几处接线）：冰仆站起时排原生效果 [`ThrallFx`]（`league_lowhp:thrall`），在尸体处生成单位
//! `league_lissandra_thrall`（[`thrall_spec`]：移速和她一样，攻击 0 且够不着任何人——冰仆不打人，只走），留到碎裂；它读成单位
//! 那一 tick 起挂上 `ICE`（受到的伤害 -100%、不死、免控：英雄联盟里打不死；选不中没有接口，敌人会白打它）；成功了尸体处不放
//! 冰仆的画面（失败时 `ThrallFx` 照旧放）。到时间时碎裂从冰仆**走到的地方**再扑（[`Bodies::shatter_from`]），伤害、减速照旧。
//! 退路：宿主没有 `spawn_unit`、失败、读不成单位、测试开关 `unit=off`（日志旁边的 `league_lowhp.cfg`）——和以前一样画面 +
//! 从尸体处扑。日志里 `THRALL UNIT` 开头的行。

use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

use super::{head, wlog, LOG_PATH};

#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

use summon::{Event, Flock, Pt};

/// The unit name: the game draws it from asset/base/aseprite_resources/champions/<name>, which mod.override_info sends to
/// the main pack's league/champions/league_lissandra_thrall (tools/art/unit_lissandra_thrall.py: the thrall's own 1x frames).
pub const THRALL_UNIT: &str = "league_lissandra_thrall";
pub const T_UID: &str = "league_lissandra_t_uid";
/// On the thrall from its first look: League's thrall cannot be hurt (`damaged_reduce` 100, undying, no crowd control).
pub const ICE: &str = "league_lissandra_thrall_ice";
/// A thrall's health (it is not to be hurt: a share of hers, should the ice not hold), her armour and magic resistance,
/// her move speed (League's thrall speeds up to her 325 while it walks; ours walks only 1.5 s).
pub const THRALL_HP_PCT: usize = 30;
pub const THRALL_SPEED_PCT: usize = 100;
const UID_TICKS: usize = 6;
const THRALL_CAP: usize = 8;

/// The picture the add-on plays where a thrall rises (`lib.rs`'s THRALL_VIEW): `ThrallFx` plays it when no unit comes.
const RISE_VIEW: &str = "league_lissandra_p_thrall";

/// The test knobs (`league_lowhp.cfg` beside the log), read once.
pub static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

/// A thrall from her numbers now (`stat`, her health cap `max_hp`) for `life` ticks: her pace, an attack that reaches
/// nowhere.
pub fn thrall_spec(stat: &StatV1, max_hp: usize, life: usize) -> summon::Spec {
    summon::Spec {
        name: THRALL_UNIT.to_string(),
        life,
        stat: StatV1 { attack: 0, magic_power: stat.magic_power, hp: (max_hp * THRALL_HP_PCT / 100).max(1), defence: stat.defence,
                       magic_resistance: stat.magic_resistance, move_speed: (stat.move_speed * THRALL_SPEED_PCT / 100).max(1),
                       hp_regen: 0, stack: 0, crit_chance: 0 },
        attack: UnitAttackV1 { attack_ratio: 0, attack: 0, range: 1, cooltime: 600, duration: 12, start_timing: 6, cancelable: false,
                               attack_type: AttackTypeV1::BaseAttack.code() },
    }
}

/// The lives `rise` asked for, by (sim seed, her, spot): the effect takes its own.
static LIVES: Mutex<Vec<((u64, usize, u64, u64), usize)>> = Mutex::new(Vec::new());

/// `ICE` for `ticks`: no damage, undying, no crowd control.
fn ice(ticks: usize) -> BuffV1 {
    let mut ice = BuffV1::timed(ICE, ticks.max(1));
    (ice.damaged_reduce, ice.undying, ice.cc_immune) = (100, true, true);
    ice
}

/// `league_lowhp:thrall` - a thrall unit where its champion fell (the input); no unit: the thrall's picture as before.
pub struct ThrallFx;

impl StableEffectType for ThrallFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        if InputTargetKindV1::from_code(input.kind) != Some(InputTargetKindV1::Pos) {
            return;
        }
        let key = (sim.seed(), caster, input.x, input.y);
        let life = {
            let mut all = LIVES.lock().unwrap_or_else(|e| e.into_inner());
            let k = all.iter().position(|(k, _)| *k == key);
            k.map(|k| all.remove(k).1)
        };
        let Some(life) = life else { return };
        let Some((team, stat, max)) = sim.get_entity(caster).map(|e| (e.team(), e.stat(), e.hp().1)) else { return };
        let spec = thrall_spec(&stat, max, life).with(&KNOBS);
        let spot = (input.x as f64, input.y as f64);
        match summon::spawn(sim, caster, team, spot, &spec) {
            Some(id) => {
                sim.add_buff(caster, &BuffV1::timed(&summon::handoff(T_UID, id), UID_TICKS));
                // the ice from its first tick too: the flock takes it on only once it has settled (summon.rs), and what
                // is laid on it before may or may not hold (the look lays it again, the passive every tick it lacks it)
                sim.add_buff(id, &ice(life + 10));
                wlog(format!("{} THRALL UNIT SPAWN: unit #{id} for team {team} at {}: {}", head(sim, caster), summon::pt(spot),
                             spec.shown()));
            }
            None => {
                sim.play_view_effect(RISE_VIEW, caster, &input, 0, 0, 0);
                wlog(format!("{} THRALL UNIT SPAWN FAILED: spawn_unit gave no unit for '{}' at {} - the thrall's picture as before",
                             head(sim, caster), spec.name, summon::pt(spot)));
            }
        }
    }
}

/// Her thralls as units, as her passive keeps them.
#[derive(Clone)]
pub struct Bodies {
    flock: Flock<()>,
    /// (where its champion fell, its unit once it read as one, where it stood last).
    links: Vec<(Pt, Option<usize>, Pt)>,
    /// Lines written (the presims' share capped like lib.rs's THRALL lines).
    n: usize,
}

impl Default for Bodies {
    fn default() -> Self {
        Bodies { flock: Flock::new(T_UID, THRALL_CAP, 90), links: Vec::new(), n: 0 }
    }
}

impl Bodies {
    fn say(&mut self, line: String) {
        self.n += 1;
        if self.n <= 200 || self.n % 100 == 0 {
            wlog(line);
        }
    }

    /// A thrall rises at `at` for `life` ticks: its unit asked for (`league_lowhp:thrall` queued). -> whether one was asked
    /// for (then the caller plays no rise picture: the effect plays it when the host gives no unit).
    pub fn rise(&mut self, sim: &mut StableSim<'_>, me: usize, at: Pt, life: usize) -> bool {
        if KNOBS.off {
            return false;
        }
        let input = InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64);
        {
            let mut all = LIVES.lock().unwrap_or_else(|e| e.into_inner());
            all.push(((sim.seed(), me, input.x, input.y), life));
            if all.len() > 64 {
                all.remove(0);
            }
        }
        self.flock.life = life;
        if !sim.queue_effect("league_lowhp:thrall", AttackTypeV1::Skill, me, &input, 1) {
            LIVES.lock().unwrap_or_else(|e| e.into_inner()).retain(|(k, _)| *k != (sim.seed(), me, input.x, input.y));
            return false;
        }
        self.links.push((at, None, at));
        if self.links.len() > THRALL_CAP * 2 {
            self.links.remove(0);
        }
        true
    }

    /// Where the thrall that rose at `at` shatters from: where its unit walked to (it ends by its time now too), or `at`.
    pub fn shatter_from(&mut self, at: Pt) -> Pt {
        match self.links.iter().position(|l| summon::dist(l.0, at) < 1.0) {
            Some(k) => self.links.remove(k).2,
            None => at,
        }
    }

    /// This tick's look at her thralls: linked to where they rose, the ice on them, their walk, their end.
    pub fn tick(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize) {
        let player = (0..sim.player_count()).filter_map(|i| sim.player_at(i))
            .find(|p| p.champion().is_some_and(|c| c.id() == me)).map_or(0, |p| p.id());
        let here = sim.get_entity(me).map(|e| summon::at_of(&e));
        for ev in self.flock.tick(sim, me, team, player, here) {
            match ev {
                Event::NoUnit { .. } => {}
                Event::Look { id, n, line } => {
                    let spot = self.flock.get(id).map_or((0.0, 0.0), |m| m.unit.at);
                    let k = self.links.iter().enumerate().filter(|(_, l)| l.1.is_none())
                        .min_by(|a, b| summon::dist(a.1 .0, spot).total_cmp(&summon::dist(b.1 .0, spot)))
                        .filter(|(_, l)| summon::dist(l.0, spot) <= 3_000.0).map(|(k, _)| k);
                    if let Some(k) = k {
                        self.links[k].1 = Some(id);
                    }
                    // League's thrall cannot be hurt: laid again at its first look, once it has settled (what is done on
                    // the spawn tick may be overwritten in the live game)
                    sim.entity_remove_buff(id, ICE);
                    sim.add_buff(id, &ice(self.flock.life + 10));
                    let on = sim.get_entity(id).is_some_and(|e| summon::has_buff(&e, ICE));
                    self.say(format!("{} THRALL UNIT #{n} LOOK: {line}; the ice (no damage, undying, no crowd control) {}{}",
                                          head(sim, me), if on { "is on it" } else { "is NOT on it" },
                                          if k.is_some() { "" } else { " - NO thrall rose there: it only walks" }));
                }
                Event::Lost { id, why, .. } => {
                    self.say(format!("{} THRALL UNIT LOST: the unit #{id} spawn_unit named never read as one in {} ticks ({why})",
                                          head(sim, me), summon::FLOCK_LOOKS));
                }
                Event::Line { id, n, line } => {
                    if let Some(l) = self.links.iter_mut().find(|l| l.1 == Some(id)) {
                        l.2 = self.flock.get(id).map_or(l.2, |m| m.unit.at);
                    }
                    self.say(format!("{} THRALL UNIT #{n}: {line}", head(sim, me)));
                }
                Event::Over { member, end } => {
                    if let Some(l) = self.links.iter_mut().find(|l| l.1 == Some(member.unit.id)) {
                        l.2 = end.at;
                    }
                    self.say(format!("{} THRALL UNIT #{} OVER: {}", head(sim, me), member.unit.n, end.text));
                }
                Event::LetGo { member } => {
                    self.say(format!("{} THRALL UNIT #{} LET GO: {THRALL_CAP} thralls on the books - the unit #{} walks on unwatched",
                                          head(sim, me), member.unit.n, member.unit.id));
                }
                Event::Wake { n, line } => {
                    self.say(format!("{} THRALL UNIT #{n} WAKE: {line}", head(sim, me)));
                }
            }
        }
        // where each walking thrall stands now (for its shatter); the ice laid again on one that lacks it (the live game,
        // 2026-11-14: what is done to a unit on its spawn tick may be overwritten, and its first look can be that tick)
        let life = self.flock.life;
        let mut iced = Vec::new();
        for l in self.links.iter_mut() {
            if let Some(m) = l.1.and_then(|id| self.flock.get(id)) {
                if let Some(e) = sim.get_entity(m.unit.id).filter(|e| e.is_alive()) {
                    l.2 = summon::at_of(&e);
                    if !summon::has_buff(&e, ICE) {
                        iced.push((m.unit.id, m.unit.left(sim.tick())));
                    }
                }
            }
        }
        for (id, left) in iced {
            sim.add_buff(id, &ice(left.max(1).min(life + 10)));
        }
    }
}
