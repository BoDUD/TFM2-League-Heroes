//! 乐芙兰的镜花水月：幻像是真的单位（0.3.0，2026-11-14；用户看了和英雄联盟不一样的地方的清单：「全改吧」，其中一条是「召唤物
//! 不会走、不会打、打不掉」，之后「召唤物的全做啊」）。
//!
//! 英雄联盟（wiki 现行页面）：生命降到 40% 时她和幻像一起隐身 1 秒；幻像和她一模一样，生命是她当时的生命，普攻没有效果，
//! 留 8 秒，敌人看不出哪个是真的。主包（和本包 0.2.x）的幻像是她站的地方放一下的画面（`league_leblanc_p_clone`：她的待机，
//! 然后化成光柱，1 秒），打不到、不会动。
//!
//! 这里用稳定 mod API 的 `spawn_unit`（公用部分是萨科附加包的 `summon.rs`）：
//!
//! - 被动在她活着时一直挂着 `P_UNIT`（每 tick 续，同 `league_leblanc_low` 的做法）：副本里那两处幻像画面外面套了
//!   `SwitchByBuff P_UNIT`，有就不放。画面不算伤害，AI 估伤害看到的和原来一样。
//! - 触发还是数据的（生命低于门槛、40 秒一次）：数据在那一刻挂上 40 秒的 `league_leblanc_p_cd`，被动看到它出现，就在她上一拍
//!   站的地方（她马上往后闪开）排原生效果 `league_lowhp:mirror`，它调 `spawn_unit`：单位叫 `league_leblanc`（按她自己的图画，
//!   和那张画面一样是她 PPU 2.0 的待机），活 `M_LIFE` tick（英雄联盟的 8 秒照她被动的冷却缩：60 秒 → 40 秒），攻击 0（普攻
//!   没有伤害），距离、间隔照她的普攻，移速、护甲、魔抗照她的，生命上限照她的、当前生命设成她当时的。引擎管着它：会追着敌人
//!   假装攻击，敌人打得到、打得死。
//! - 生成不了（宿主没有这个接口、失败、读不成单位、很快就没了）：在那个地方放原来那张画面（原生地放，同一个画面）；测试开关
//!   `unit=off`（日志旁边的 `league_lowhp.cfg`）：不挂 `P_UNIT`，数据照旧放画面。
//! - 她先死了：被动不再跑，幻像由引擎管着到时间。
//!
//! 日志（`league_lowhp.log`）：`MIRROR ASK` / `MIRROR SPAWN` / `MIRROR #n LOOK` / `DRESS` / 每秒一行 / `OVER` / `WAKE` /
//! `ORPHAN`，退路 `MIRROR SPAWN FAILED` / `NONE` / `LOST` / `OFF`。预模拟限了条数，你看的那场每条都记。

use std::collections::HashMap;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

use super::{head, wlog, HOLD, ID, LOG_PATH};

// the shared part of the summons (萨科附加包的 summon.rs); not every item of it is used here
#[allow(dead_code)]
#[path = "../../league_shaco_backstab/src/summon.rs"]
pub mod summon;

pub type Pt = (f64, f64);

/// The clone's unit name: her own id, so the game draws it from her own sheet (dense frames at PPU 2.0, like the picture).
pub const UNIT_NAME: &str = "league_leblanc";
/// The data's Mirror Image cooldown flag (40 s): laid as Mirror Image fires - its rise is the moment.
pub const P_CD: &str = "league_leblanc_p_cd";
/// Held on her while the add-on makes the clone a unit: the copy's data then leaves its picture out.
pub const P_UNIT: &str = "league_leblanc_p_unit";
/// The handoff from `:mirror` to the passive: `<P_UID>:<unit id>` on her for a few ticks.
pub const P_UID: &str = "league_lowhp_lb_uid";
/// `:mirror`'s word that it gave no unit (and played the picture itself).
pub const P_NONE: &str = "league_lowhp_lb_none";
/// The data's clone picture: where no unit comes, it is played natively where she stood.
pub const P_VIEW: &str = "league_leblanc_p_clone";
/// The clone's time: League's 8 s scaled like her passive's cooldown (League 60 s, here 40 s: 2400 ticks) - 320 ticks.
pub const M_LIFE: usize = 320;
/// Its attack: no damage (League's clone "can cast basic attacks with no effect"), her attack's reach, interval, length
/// and the tick her orb leaves the staff.
pub const M_RANGE: usize = 52_500;
pub const M_COOL: usize = 90;
pub const M_ACT: usize = 28;
pub const M_LANDS: usize = 13;
/// Ticks the handoff stays, ticks the passive waits for it, looks a handed-over id may take to read as a unit.
const UID_TICKS: usize = 6;
const ASK_WAIT: usize = 4;
const LOOK_TRIES: usize = 5;
/// A unit gone within this many ticks was never really there: the picture plays where it stood.
pub const LOST_AGE: usize = 6;

/// The test knobs (`league_lowhp.cfg` beside the log, summon.rs), read once.
pub static KNOBS: LazyLock<summon::Knobs> = LazyLock::new(|| summon::Knobs::read(&LOG_PATH.with_extension("cfg")));

// ===================== 日志的条数 =====================

/// Lines of each kind a launch (league_shaco_backstab's): the server's presims the first `LOG_FIRST`, then every
/// `LOG_EVERY`-th; the match on screen all.
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

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

fn fx(name: &str) -> String {
    format!("{ID}:{name}")
}

fn at_input(at: Pt) -> InputTargetV1 {
    InputTargetV1::pos(at.0.round().max(0.0) as u64, at.1.round().max(0.0) as u64)
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

// ===================== 生成 =====================

/// The clone from her numbers now (`stat`, her health cap `max_hp`): no attack, her defences and speed, her health cap,
/// her attack's reach and timing. No regeneration.
pub fn mirror_spec(stat: &StatV1, max_hp: usize) -> summon::Spec {
    summon::Spec {
        name: UNIT_NAME.to_string(),
        life: M_LIFE,
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
            range: M_RANGE,
            cooltime: M_COOL,
            duration: M_ACT,
            start_timing: M_LANDS,
            cancelable: false,
            attack_type: AttackTypeV1::BaseAttack.code(),
        },
    }
}

/// The picture of the main pack's clone where she stood (no unit came).
fn picture(sim: &mut StableSim<'_>, me: usize, at: Pt) {
    sim.play_view_effect(P_VIEW, me, &at_input(at), 0, 0, 0);
}

/// The clone spawned for `me` at `at`: the handoff on her. `None` (a line, the picture where she stood, the word on her):
/// the host gave no unit.
fn make_mirror(sim: &mut StableSim<'_>, me: usize, at: Pt, by: &str) -> Option<usize> {
    let (team, stat, max) = sim.get_entity(me).map(|e| (e.team(), e.stat(), e.hp().1))?;
    let spec = mirror_spec(&stat, max).with(&KNOBS);
    match summon::spawn(sim, me, team, at, &spec) {
        Some(id) => {
            sim.add_buff(me, &BuffV1::timed(&summon::handoff(P_UID, id), UID_TICKS));
            if let Some(k) = tally(sim, "mirror spawn") {
                wlog(format!("{} MIRROR SPAWN #{k} ({by}): unit #{id} for team {team} at {}: {}", head(sim, me), summon::pt(at),
                             spec.shown()));
            }
            Some(id)
        }
        None => {
            picture(sim, me, at);
            sim.add_buff(me, &BuffV1::timed(P_NONE, UID_TICKS));
            if let Some(k) = tally(sim, "mirror fail") {
                wlog(format!("{} MIRROR SPAWN FAILED #{k} ({by}): spawn_unit gave no unit for '{}' at {} - the picture plays \
                              there as before", head(sim, me), spec.name, summon::pt(at)));
            }
            None
        }
    }
}

/// `:mirror` - the passive queues it as Mirror Image fires; the input is where she stood.
pub struct MirrorFx;

impl StableEffectType for MirrorFx {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let at = match InputTargetKindV1::from_code(input.kind) {
            Some(InputTargetKindV1::Pos) => (input.x as f64, input.y as f64),
            _ => match sim.get_entity(caster) {
                Some(e) => summon::at_of(&e),
                None => return,
            },
        };
        make_mirror(sim, caster, at, "the queued effect");
    }
}

// ===================== 被动里她的那一份 =====================

/// Her clone as a unit, as the passive keeps it.
#[derive(Clone, Debug)]
struct Live {
    unit: summon::Unit,
    /// Where it was asked for (the picture goes there should it turn out to be none), the health it was to start with,
    /// whether the look a tick after was logged.
    at: Pt,
    hp_goal: usize,
    dressed: bool,
}

/// What a handed-over unit is waited for with: the id, the tick it was asked for, looks so far, where.
#[derive(Clone, Copy, Debug)]
struct Fresh {
    id: usize,
    asked: usize,
    tries: usize,
    at: Pt,
}

/// LeBlanc's part of league_lowhp's passive.
#[derive(Clone, Default)]
pub struct Mirror {
    /// Her own unit (on_dead is given the player).
    me: usize,
    /// The data's cooldown flag at the last look; `P_UNIT` laid at the last look; where she stood then.
    had_cd: bool,
    held: bool,
    prev_at: Option<Pt>,
    /// Asked at this tick for this spot, its handoff awaited.
    wait: Option<(usize, Pt)>,
    fresh: Option<Fresh>,
    live: Option<Live>,
    wake: Option<summon::Wake>,
    n: usize,
}

impl Mirror {
    pub fn spawned(&mut self, sim: &mut StableSim<'_>, me: usize) {
        // a new life is a new entity: nothing of the old one's clone is hers to watch any more
        if let Some(live) = self.live.take() {
            wlog(format!("{} MIRROR #{}: still on the books at her respawn (her death did not reach on_dead) - let go",
                         head(sim, me), live.unit.n));
        }
        *self = Mirror { me, n: self.n, ..Mirror::default() };
    }

    pub fn dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        (self.wait, self.fresh, self.wake, self.held, self.had_cd, self.prev_at) = (None, None, None, false, false, None);
        let Some(live) = self.live.take() else { return };
        let me = sim.get_player(player).and_then(|p| p.champion()).map_or(self.me, |e| e.id());
        let (tick, u) = (sim.tick(), &live.unit);
        if let Some(k) = tally(sim, "mirror orphan") {
            wlog(format!("{} MIRROR #{} ORPHAN #{k}: LeBlanc died, her clone #{} at {} has {} ticks left and hp {}/{} - it goes on \
                          unwatched", head(sim, me), u.n, u.id, summon::pt(u.at), u.left(tick), u.hp, u.max));
        }
    }

    /// A line for a hook that fired while the clone is out.
    pub fn hooked(&self, sim: &StableSim<'_>, hook: &str, entity: usize, other: usize, damage: Option<usize>) {
        let Some(live) = &self.live else { return };
        if let Some(k) = tally(sim, "mirror hook") {
            wlog(format!("{} MIRROR #{} HOOK #{k} {hook}: {}{}", head(sim, self.me), live.unit.n,
                         live.unit.hook_text(sim, entity, other, self.me), damage.map(|d| format!(", damage {d}")).unwrap_or_default()));
        }
    }

    /// Her tick while she lives: the flag held, Mirror Image's moment seen, the unit asked for, looked at, watched.
    pub fn update(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        let tick = sim.tick();
        let Some((team, here, hp, cd)) = sim.get_entity(me).map(|e| (e.team(), summon::at_of(&e), e.hp().0, has_buff(&e, P_CD)))
        else {
            return;
        };
        // the data's moment: its 40 s cooldown flag has just come on
        if cd && !self.had_cd {
            let at = self.prev_at.unwrap_or(here);
            if !self.held {
                if let Some(k) = tally(sim, "mirror off") {
                    wlog(format!("{} MIRROR OFF #{k}: Mirror Image at {} with no unit asked for ({}) - the data's picture played",
                                 head(sim, me), summon::pt(at),
                                 if KNOBS.off { "unit=off in the test knobs" } else { "the flag was not on her yet this life" }));
                }
            } else {
                let queued = sim.queue_effect(&fx("mirror"), AttackTypeV1::Skill, me, &at_input(at), 1);
                if !queued {
                    make_mirror(sim, me, at, "queue_effect refused: spawned by the passive");
                }
                self.wait = Some((tick, at));
                if let Some(k) = tally(sim, "mirror ask") {
                    wlog(format!("{} MIRROR ASK #{k}: Mirror Image at {} (where she stood a tick ago; she is at {} now){}",
                                 head(sim, me), summon::pt(at), summon::pt(here), if queued { "" } else { " - queue_effect REFUSED" }));
                }
            }
        }
        self.had_cd = cd;
        // the flag the copy's data reads as it fires: on her from this tick on, unless the knobs say no unit
        if !KNOBS.off {
            sim.entity_remove_buff(me, P_UNIT);
            sim.add_buff(me, &BuffV1::timed(P_UNIT, HOLD));
        }
        self.held = !KNOBS.off;
        self.prev_at = Some(here);
        if let Some((since, at)) = self.wait {
            if let Some(id) = summon::take_handoff(sim, me, P_UID) {
                (self.wait, self.fresh) = (None, Some(Fresh { id, asked: since, tries: 0, at }));
            } else if sim.get_entity(me).is_some_and(|e| has_buff(&e, P_NONE)) {
                sim.entity_remove_buff(me, P_NONE);
                self.wait = None;
            } else if tick > since + ASK_WAIT {
                self.wait = None;
                picture(sim, me, at);
                if let Some(k) = tally(sim, "mirror none") {
                    wlog(format!("{} MIRROR NONE #{k}: no unit came within {ASK_WAIT} ticks of the ask - the picture played at {} \
                                  instead", head(sim, me), summon::pt(at)));
                }
            }
        }
        if let Some(f) = self.fresh {
            match summon::Unit::look(sim, f.id, self.n + 1, f.asked, M_LIFE, team, player) {
                Ok((mut unit, line)) => {
                    self.fresh = None;
                    self.n += 1;
                    // League's clone has her current health: the cap is hers, the health now set to her own
                    let (had, hp_goal) = (unit.hp, hp.clamp(1, unit.max.max(1)));
                    let set = hp_goal < had && sim.entity_set_hp(f.id, hp_goal);
                    if set {
                        unit.health_set(hp_goal);
                    }
                    if let Some(k) = tally(sim, "mirror look") {
                        wlog(format!("{} MIRROR #{} LOOK #{k}: {line}; health to her own {hp_goal}: {}", head(sim, me), self.n,
                                     if set { "set" } else if hp_goal >= had { "it has no more" } else { "entity_set_hp REFUSED" }));
                    }
                    if let Some(old) = self.live.take() {
                        wlog(format!("{} MIRROR #{}: the clone #{} of an earlier one is still out - no longer watched", head(sim, me),
                                     self.n, old.unit.id));
                    }
                    self.live = Some(Live { unit, at: f.at, hp_goal, dressed: false });
                }
                Err(why) if f.tries + 1 >= LOOK_TRIES => {
                    self.fresh = None;
                    picture(sim, me, f.at);
                    if let Some(k) = tally(sim, "mirror lost") {
                        wlog(format!("{} MIRROR LOST #{k}: the unit spawn_unit named never read as one in {LOOK_TRIES} ticks ({why}) - \
                                      the picture played at {} instead", head(sim, me), summon::pt(f.at)));
                    }
                }
                Err(_) => self.fresh = Some(Fresh { tries: f.tries + 1, ..f }),
            }
            return;
        }
        if let Some(mut live) = self.live.take() {
            let n = live.unit.n;
            if !live.dressed {
                live.dressed = true;
                let seen = sim.get_entity(live.unit.id).map(|e| e.hp());
                if let (Some(k), Some((now, max))) = (tally(sim, "mirror dress"), seen) {
                    wlog(format!("{} MIRROR #{n} DRESS #{k}: a tick on, its health {now}/{max} (asked {})", head(sim, me), live.hp_goal));
                }
            }
            match live.unit.step(sim, Some(here)) {
                summon::Step::Alive(line) => {
                    if let (Some(line), Some(k)) = (line, tally(sim, "mirror line")) {
                        wlog(format!("{} MIRROR #{n} #{k}: {line}", head(sim, me)));
                    }
                    self.live = Some(live);
                }
                summon::Step::Over(end) => {
                    if let Some(k) = tally(sim, "mirror over") {
                        wlog(format!("{} MIRROR #{n} OVER #{k}: {}", head(sim, me), end.text));
                    }
                    if end.age <= LOST_AGE {
                        // never really there: the picture where it was asked for
                        picture(sim, me, live.at);
                        wlog(format!("{} MIRROR #{n}: gone {} ticks after it was asked for - the picture played at {} instead",
                                     head(sim, me), end.age, summon::pt(live.at)));
                    }
                    self.wake = Some(live.unit.wake(sim, &end));
                }
            }
        }
        if let Some(mut w) = self.wake.take() {
            let (lines, over) = w.step(sim);
            for line in lines {
                if let Some(k) = tally(sim, "mirror wake") {
                    wlog(format!("{} MIRROR #{} WAKE #{k}: {line}", head(sim, me), w.n));
                }
            }
            if !over {
                self.wake = Some(w);
            }
        }
    }
}

/// The load line, and `:mirror` registered.
pub fn register(module: &mut StableMod) {
    wlog(format!(
        "MIRROR: Mirror Image's clone is a unit ('{}', spawn_unit) - {}; {M_LIFE} ticks, no damage, her health then. Test knobs \
         ({}): {}",
        KNOBS.name.as_deref().unwrap_or(UNIT_NAME),
        if KNOBS.off { "OFF by the test knobs: the data's picture plays as before" } else { "ON" },
        LOG_PATH.with_extension("cfg").display(),
        KNOBS.shown()
    ));
    module.add_native_effect(fx("mirror"), MirrorFx);
}

#[cfg(test)]
#[path = "../../league_shaco_backstab/src/summon_mock.rs"]
mod mock;

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn the_clone_is_her_with_no_damage() {
        let hers = StatV1 { attack: 80, magic_power: 300, hp: 880, defence: 44, magic_resistance: 36, move_speed: 990, hp_regen: 3,
                            stack: 1, crit_chance: 10 };
        let spec = mirror_spec(&hers, 1900);
        assert_eq!((spec.name.as_str(), spec.life), ("league_leblanc", 320));
        assert_eq!(spec.stat, StatV1 { attack: 0, magic_power: 0, hp: 1900, defence: 44, magic_resistance: 36, move_speed: 990,
                                       hp_regen: 0, stack: 0, crit_chance: 0 });
        let a = spec.attack;
        assert_eq!(a.attack + spec.stat.attack * a.attack_ratio / 100, 0, "League's clone hits for nothing");
        assert_eq!((a.range, a.cooltime, a.duration, a.start_timing), (52_500, 90, 28, 13));
        assert!(a.start_timing < a.duration && a.duration < a.cooltime);
        assert_eq!(mirror_spec(&hers, 0).stat.hp, 1);
        // League's 8 s scaled like her passive's cooldown: 60 s there, 2400 ticks here
        assert_eq!(M_LIFE, 8 * 60 * 2400 / (60 * 60));
        for name in [P_UNIT, P_NONE, P_CD, &summon::handoff(P_UID, usize::MAX)] {
            assert!(name.len() <= BUFF_NAME_CAP, "{name}");
        }
        assert!(ASK_WAIT + LOOK_TRIES < 30 && LOST_AGE < 60);
    }

    #[test]
    fn the_copy_leaves_its_picture_to_the_flag() {
        let copy = include_str!("../override/league_leblanc.data_champion").replace('\r', "");
        let main = include_str!("../../../league/champion/league_leblanc.data_champion").replace('\r', "");
        assert!(!main.contains(P_UNIT));
        // both of the main pack's pictures (her attack's and her skill's), each inside a switch on the flag
        assert_eq!(main.matches(&format!("\"name\": \"{P_VIEW}\"\n")).count(), 2);
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{P_UNIT}\"")).count(), 2);
        assert_eq!(copy.matches(&format!("\"name\": \"{P_VIEW}\"\n")).count(), 2);
    }

    // ---- the clone on the mock world (summon_mock.rs: our guess of the host, to check this side's logic) ----

    use super::mock::{champion, MPlayer, World};

    const GAREN: usize = 1;

    fn log_file() -> PathBuf {
        static SET: std::sync::Once = std::sync::Once::new();
        let path = std::env::temp_dir().join(format!("league_lowhp_test_{}.log", std::process::id()));
        SET.call_once(|| {
            std::env::set_var("LEAGUE_LOWHP_LOG", &path);
            let _ = std::fs::remove_file(&path);
            let _ = std::fs::remove_file(path.with_extension("cfg"));
        });
        path
    }

    /// LeBlanc #0 (team 0, 350 of 1000 health) at (300000, 300000); Garen #1 30000 east of her; a player each.
    fn world() -> (World, Mirror) {
        log_file();
        let mut w = World::default();
        let mut lb = champion("league_leblanc", 0, 300_000.0, 300_000.0);
        (lb.hp, lb.max) = (350, 1000);
        w.units = vec![lb, champion("league_garen", 1, 330_000.0, 300_000.0)];
        w.players = vec![MPlayer { team: 0, champion: 0, ..Default::default() }, MPlayer { team: 1, champion: GAREN, ..Default::default() }];
        let mut me = Mirror::default();
        w.sim(|sim| me.spawned(sim, 0));
        run(&mut w, &mut me, 3);
        (w, me)
    }

    fn tick(w: &mut World, me: &mut Mirror) {
        for (name, caster, input) in w.due() {
            w.sim(|sim| match name.as_str() {
                "league_lowhp:mirror" => MirrorFx.apply(sim, 0, caster, input),
                other => panic!("an effect nobody registered: {other}"),
            });
        }
        if w.units[0].hp > 0 {
            w.sim(|sim| me.update(sim, 0, 0));
        }
        w.step();
    }

    fn run(w: &mut World, me: &mut Mirror, n: usize) {
        for _ in 0..n {
            tick(w, me);
        }
    }

    /// The copy's Mirror Image as the data plays it: the cooldown on, a picture unless the flag is on, the dash back.
    fn fire(w: &mut World) -> usize {
        if !w.has(0, P_UNIT) {
            w.views.push((w.tick, P_VIEW.to_string(), InputTargetV1::target(0)));
        }
        w.units[0].buffs.push((BuffV1::timed(P_CD, 2400), 2400));
        w.units[0].x -= 6_000.0;
        w.tick
    }

    #[test]
    fn mirror_image_leaves_a_clone_that_stands_in_for_her() {
        let (mut w, mut me) = world();
        assert!(w.has(0, P_UNIT), "the flag is not held while she lives");
        let t0 = fire(&mut w);
        run(&mut w, &mut me, 4);
        // one unit where she stood a tick before her dash: her name, her team, no damage, her health now
        assert_eq!(w.spawns.len(), 1);
        let s = w.spawns[0].clone();
        assert_eq!((s.name.as_str(), s.summoner, s.team, s.life), ("league_leblanc", 0, 0, 320));
        assert_eq!(s.at, (300_000, 300_000));
        assert!(s.tick <= t0 + 2);
        assert_eq!((s.stat.attack, s.stat.hp, s.attack.attack, s.attack.attack_ratio), (0, 1000, 0, 0));
        let clone = s.gave.unwrap();
        assert_eq!(w.units[clone].hp, 350);
        assert_eq!(w.viewed(P_VIEW), 0, "the picture played beside the unit");
        // it goes for Garen and hits him for nothing; it can be hit; it ends at its time
        run(&mut w, &mut me, 200);
        assert!(w.damage.iter().filter(|d| d.1 == clone).all(|d| d.3 == 0));
        assert!(w.damage.iter().any(|d| d.1 == clone && d.2 == GAREN), "the clone never went for Garen");
        run(&mut w, &mut me, 200);
        assert!(!w.units[clone].valid);
        assert!(me.live.is_none() && me.wake.is_none() && me.fresh.is_none() && me.wait.is_none() && w.queue.is_empty());
        assert_eq!(w.viewed(P_VIEW), 0);
        assert_eq!(me.n, 1);
        // the cooldown still on: no second clone
        assert_eq!(w.spawns.len(), 1);
    }

    #[test]
    fn no_unit_from_the_host_plays_the_picture_where_she_stood() {
        // no such slot, a refusal, an id that never reads as a unit, a unit gone at once, no queued effects at all
        for case in 0..5 {
            let (mut w, mut me) = world();
            match case {
                0 => w.has_spawn = false,
                1 => w.spawn_ok = false,
                2 => w.spawn_never = true,
                4 => w.queue_ok = false,
                _ => {}
            }
            fire(&mut w);
            if case == 3 {
                run(&mut w, &mut me, 4);
                assert!(me.live.is_some(), "case 3");
                let id = w.spawns[0].gave.unwrap();
                w.units[id].valid = false;
            }
            run(&mut w, &mut me, 20);
            let pics: Vec<(u64, u64)> = w.views.iter().filter(|v| v.1 == P_VIEW).map(|v| (v.2.x, v.2.y)).collect();
            if case == 4 {
                // the passive spawned it itself: a unit, no picture
                assert!(pics.is_empty() && w.spawns.len() == 1, "case 4: {pics:?}");
                continue;
            }
            assert_eq!(pics, vec![(300_000, 300_000)], "case {case}: one picture where she stood");
            assert!(me.live.is_none() && me.fresh.is_none() && me.wait.is_none(), "case {case}");
            assert!(w.queue.is_empty(), "case {case}");
        }
    }

    #[test]
    fn the_clone_goes_on_when_she_dies() {
        let (mut w, mut me) = world();
        fire(&mut w);
        run(&mut w, &mut me, 60);
        let clone = w.spawns[0].gave.unwrap();
        (w.units[0].hp, w.units[0].died) = (0, Some(w.tick));
        w.sim(|sim| me.dead(sim, 0));
        assert!(me.live.is_none());
        let before = w.damage.iter().filter(|d| d.1 == clone).count();
        run(&mut w, &mut me, 120);
        assert!(w.damage.iter().filter(|d| d.1 == clone).count() > before, "the clone stopped when she died");
        assert!(w.queue.is_empty());
    }

    #[test]
    fn the_log_tells_the_clones_life() {
        let (mut w, mut me) = world();
        fire(&mut w);
        run(&mut w, &mut me, 70);
        let clone = w.spawns[0].gave.unwrap();
        w.sim(|sim| me.hooked(sim, "on_attack", clone, GAREN, Some(0)));
        w.players[1].gold += 20;
        w.hurt(clone, 10_000);
        run(&mut w, &mut me, 10);
        let text = std::fs::read_to_string(log_file()).expect("the log");
        let mine: Vec<&str> = text.lines().filter(|l| l.contains(" MIRROR ")).collect();
        let has = |what: &str| mine.iter().any(|l| l.contains(what));
        for what in [
            "MIRROR ASK #", "Mirror Image at (300000,300000) (where she stood a tick ago; she is at (294000,300000) now)",
            "MIRROR SPAWN #", "'league_leblanc' for 320 ticks, attack 0 ap 0 hp 1000 def 20 mr 20 speed 1100; hits 0 + 0% of its attack, \
             range 52500, every 90 ticks (28 long, lands at 13)",
            "LOOK #", "reads back as name 'league_leblanc' kind summon team 0 champion=false", "health to her own 350: set",
            "DRESS #", "a tick on, its health 350/1000 (asked 350)",
            " of 320 ticks, at (", "near it: champion #1 league_garen",
            "OVER #", "KILLED after ", "p1 gold +20", "HOOK #", "on_attack: entity #2 (the unit itself) -> champion #1 league_garen",
            "WAKE #",
        ] {
            assert!(has(what), "missing {what:?} in the log:\n{}", mine.join("\n"));
        }
        assert!(mine.iter().all(|l| l.starts_with("[view m=7 s=1] t=")));
        let longest = mine.iter().map(|l| l.len()).max().unwrap();
        assert!(longest < 700, "a line of {longest} bytes");
    }
}
