//! 千珏之印的狩猎（0.2.0，2026-11-11）。用户：「千珏印记是不是不能印记英雄啊 你看看 如果不能的话就要改了」。
//!
//! 主包是纯数据：读不到别人身上的东西，也没法「指名」一个英雄，所以那里的千珏之印是个近似——她普攻打过的敌方英雄 3 秒内
//! 阵亡就加一层印记，谁都算，没有哪个英雄头上有印记，她一死印记就清空。英雄联盟的规则（客户端 zh_CN 的说明和 wiki，
//! 2026-11-11 读）：羊灵指名一名敌方英雄作为狩猎目标（最近 6 秒没和她交过手的），8 秒后狩猎生效；参与击杀（击杀或助攻）
//! 被狩猎的目标得一层印记，印记永久保留；成功狩猎过的英雄 240 秒内不会再被指名；每 75 秒指名一次（狼灵狩猎野怪，本包不做）。
//!
//! 本包的千珏副本（make_override.py：build_kindred 的 `p_native=1`）去掉普攻里数据的那套近似，印记全由这个被动
//! `league_kindred:hunt` 给：
//!
//! - **指名**：开局 [`FIRST_PICK`] tick 起每 [`PICK_EVERY`] tick 一次。活着的敌方英雄里，[`IMMUNE_T`] 内没被她成功狩猎过、
//!   [`COMBAT_T`] tick 内没和她交过手（她打中过他、他打中过她）的，挑最脆的（最大生命最少；一样就当前生命比例低的）
//!   ——AI 点不了头像，挑最可能被拿下的。他头顶出现半透明、一闪一闪的印记（[`WAIT`]，本包图 `league_kindred_hunt` 的
//!   `wait`），[`ARM_T`] tick 后换成完整的印记（[`HUNTED`]，`on`）：狩猎生效。
//! - **完成**：他阵亡时看击杀记录——她是击杀者或助攻者，而且狩猎已经生效：一层印记。主包的 `league_kindred_p_mark`
//!   （攻速、法强照主包，由副本的 params 传来；射程是 league.dll 的 league:range 按这个名字给的）、`league_kindred_p_has`
//!   （横生惧意读它）、她头顶主包的得印记画面 `league_kindred_p_stack` 和音效 `league_kindred_p`；他 [`IMMUNE_T`] 内不会再被
//!   指名。不是她参与的、或还没生效就死了：这次落空。不管哪种，印记都从尸体上去掉。
//! - **作罢**：到下一次指名时他还活着，这次狩猎作罢（印记去掉），重新指名（还可以是他）。
//! - **印记死了不掉**：活着时记下身上的每一层（和 league_veigar_power 一样，按完整的数值配对），少了（阵亡、复活时引擎
//!   清掉）就补回；她死着时完成的狩猎记成欠的，复活后补上。
//!
//! 日志（league_kindred.log）：每次指名、生效、完成、落空、作罢一行（`HUNT PICK / ARMED / DONE / LOST / LAPSED`），
//! 每次补回一行（`MARKS KEPT`）。

use mod_api_stable::*;

use super::{counted, head, team_lane, who, wlog};

/// 第一次指名（开局 1 秒）。
pub const FIRST_PICK: usize = 60;
/// 每 75 秒指名一次（英雄联盟的羊灵：75 秒一轮）。
pub const PICK_EVERY: usize = 75 * 60;
/// 指名 8 秒后狩猎生效。
pub const ARM_T: usize = 8 * 60;
/// 成功狩猎过的英雄 240 秒内不会再被指名。
pub const IMMUNE_T: usize = 240 * 60;
/// 最近 6 秒和她交过手的不指名。
pub const COMBAT_T: usize = 6 * 60;
/// 他阵亡后最多等几 tick 击杀记录（记录和阵亡同一 tick 写，多等几 tick 保险）。
pub const KILL_WAIT: usize = 6;

/// 头顶的印记：指名后、生效前（她的队伍 0 蓝 / 1 红各一个名字：两边都有千珏时互不干扰）。
pub const WAIT: [&str; 2] = ["league_kindred_hunt_wait_b", "league_kindred_hunt_wait_r"];
/// 头顶的印记：狩猎生效后。
pub const HUNTED: [&str; 2] = ["league_kindred_hunted_b", "league_kindred_hunted_r"];
/// 主包的一层印记、「有印记」的旗子、得印记的画面、音效。
pub const MARK: &str = "league_kindred_p_mark";
pub const HAS: &str = "league_kindred_p_has";
pub const SHOW: &str = "league_kindred_p_stack";
pub const SOUND: &str = "league_kindred_p";

/// 副本的 params：一层印记的攻速、法强，得印记画面停几 tick（主包 build_kindred 的 p_as / p_ap / p_show）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    pub attack_speed: i32,
    pub magic_power: i32,
    pub show: usize,
}

impl Default for Params {
    fn default() -> Self {
        Params { attack_speed: 4, magic_power: 1, show: 90 }
    }
}

/// `{"ap":1,"as":4,"show":90}` -> Params（没写的用默认）。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let Ok(v) = v.trim().parse::<i64>() else { continue };
        match k.trim().trim_matches('"') {
            "as" => p.attack_speed = v as i32,
            "ap" => p.magic_power = v as i32,
            "show" => p.show = v.max(1) as usize,
            _ => {}
        }
    }
    p
}

/// 一个能被指名的敌方英雄：实体、(当前, 最大) 生命。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Candidate {
    pub entity: usize,
    pub hp: (usize, usize),
}

/// 这一 tick 指名谁：`immune` 是 (实体, 到哪一 tick)，`fought` 是 (实体, 最后一次交手的 tick)。
pub fn pick(cands: &[Candidate], immune: &[(usize, usize)], fought: &[(usize, usize)], tick: usize) -> Option<usize> {
    cands
        .iter()
        .filter(|c| !immune.iter().any(|&(e, until)| e == c.entity && until > tick))
        .filter(|c| !fought.iter().any(|&(e, last)| e == c.entity && last + COMBAT_T > tick))
        .min_by_key(|c| (c.hp.1, c.hp.0 * 1000 / c.hp.1.max(1), c.entity))
        .map(|c| c.entity)
}

/// 被狩猎的 `victim`（队伍, 分路）从 `from` 起阵亡的那一条击杀记录里有没有她 `me`（队伍, 分路）：击杀者或助攻者
/// -> Some(true)；有记录、没有她 -> Some(false)；还没有记录 -> None。
pub fn takedown(log: &[KillLogV1], victim: (usize, u32), me: (usize, u32), from: usize) -> Option<bool> {
    let k = log
        .iter()
        .rev()
        .take_while(|k| k.tick >= from)
        .find(|k| k.killed_position == victim.1 && k.killer_team != victim.0)?;
    if k.killer_team != me.0 {
        return Some(false);
    }
    let assists = &k.assist_positions[..(k.assist_count as usize).min(4)];
    Some(k.killer_position == me.1 || assists.contains(&me.1))
}

/// `kept` 里有、`have` 里没有的那些（按完整的数值配对，league_veigar_power 的 missing）。
pub fn missing(kept: &[BuffV1], have: &[BuffV1]) -> Vec<BuffV1> {
    let mut left: Vec<Option<&BuffV1>> = have.iter().map(Some).collect();
    let mut out = Vec::new();
    for k in kept {
        match left.iter_mut().find(|h| h.is_some_and(|h| h == k)) {
            Some(slot) => *slot = None,
            None => out.push(*k),
        }
    }
    out
}

/// 正在狩猎的那个人：实体、(队伍, 分路)、指名的 tick、生效了没有、阵亡后等了几 tick 击杀记录。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
struct Quarry {
    entity: usize,
    who: Option<(usize, u32)>,
    picked: usize,
    armed: bool,
    waited: usize,
}

#[derive(Clone, Default)]
pub struct Hunt {
    p: Params,
    /// 她活着时身上看到的每一层印记和「有印记」的旗子。
    kept: Vec<BuffV1>,
    /// 她死着时完成的狩猎（复活后补上）。
    owed: usize,
    quarry: Option<Quarry>,
    next_pick: Option<usize>,
    immune: Vec<(usize, usize)>,
    fought: Vec<(usize, usize)>,
    was_alive: bool,
    /// 这一局完成的狩猎（日志）。
    done: usize,
}

fn buffs_named(sim: &StableSim<'_>, id: usize, names: &[&str]) -> Vec<BuffV1> {
    sim.get_entity(id).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| names.contains(&b.name())).collect()
    })
}

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn say(kind: &'static str, line: String) {
    if let Some(k) = counted(kind) {
        wlog(format!("{line} #{k}"));
    }
}

impl Hunt {
    fn note_fight(&mut self, sim: &StableSim<'_>, me: usize, other: usize) {
        let (Some(a), Some(b)) = (sim.get_entity(me), sim.get_entity(other)) else { return };
        if !b.is_champion() || a.team() == b.team() {
            return;
        }
        let tick = sim.tick();
        match self.fought.iter_mut().find(|f| f.0 == other) {
            Some(f) => f.1 = tick,
            None => self.fought.push((other, tick)),
        }
    }

    /// 一层印记（她死着就记成欠的）。
    fn gain(&mut self, sim: &mut StableSim<'_>, me: usize, alive: bool) {
        if !alive {
            self.owed += 1;
            return;
        }
        let mut b = BuffV1::named(MARK);
        b.attack_speed_mult = self.p.attack_speed;
        b.magic_power = self.p.magic_power;
        sim.add_buff(me, &b);
        if !has(sim, me, HAS) {
            sim.add_buff(me, &BuffV1::named(HAS));
        }
        sim.entity_remove_buff(me, SHOW);
        sim.add_buff(me, &BuffV1::timed(SHOW, self.p.show));
        sim.play_sfx(SOUND, me, &InputTargetV1::target(me));
    }

    /// 印记死了不掉。
    fn keep(&mut self, sim: &mut StableSim<'_>, me: usize, alive: bool) {
        if alive {
            for _ in 0..std::mem::take(&mut self.owed) {
                self.gain(sim, me, true);
            }
        }
        let have = buffs_named(sim, me, &[MARK, HAS]);
        let gone = missing(&self.kept, &have);
        if gone.is_empty() {
            if alive && have.len() > self.kept.len() {
                self.kept = have;
            }
            return;
        }
        for b in &gone {
            sim.add_buff(me, b);
        }
        let marks = self.kept.iter().filter(|b| b.name() == MARK).count();
        say("kept", format!("{} MARKS KEPT: {} put back ({}), {marks} marks", head(sim, me), gone.len(),
                            if alive { "alive" } else { "dead" }));
    }

    fn clear_marks(sim: &mut StableSim<'_>, q: &Quarry, team: usize) {
        sim.entity_remove_buff(q.entity, WAIT[team]);
        sim.entity_remove_buff(q.entity, HUNTED[team]);
    }

    fn step(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, alive: bool) {
        let tick = sim.tick();
        let side = team.min(1);
        let next = *self.next_pick.get_or_insert(FIRST_PICK);
        if let Some(mut q) = self.quarry {
            let target_alive = sim.get_entity(q.entity).is_some_and(|t| t.is_alive());
            if target_alive && !q.armed && tick >= q.picked + ARM_T {
                sim.entity_remove_buff(q.entity, WAIT[side]);
                sim.add_buff(q.entity, &BuffV1::named(HUNTED[side]));
                q.armed = true;
                say("armed", format!("{} HUNT ARMED on {}", head(sim, me), who(sim, q.entity)));
            }
            if !target_alive {
                let log: Vec<KillLogV1> = (0..sim.kill_log_count()).filter_map(|i| sim.kill_log_at(i)).collect();
                let mine = team_lane(sim, me);
                let res = match (q.who, mine) {
                    (Some(v), Some(m)) => takedown(&log, v, m, q.picked),
                    _ => Some(false),
                };
                if res.is_none() && q.waited < KILL_WAIT {
                    q.waited += 1;
                    self.quarry = Some(q);
                    return;
                }
                let name = who(sim, q.entity);
                match res {
                    Some(true) if q.armed => {
                        self.gain(sim, me, alive);
                        self.done += 1;
                        self.immune.retain(|i| i.0 != q.entity);
                        self.immune.push((q.entity, tick + IMMUNE_T));
                        say("done", format!("{} HUNT DONE on {name}: a mark ({} hunts this match{})", head(sim, me),
                                            self.done, if alive { "" } else { ", owed until she is back" }));
                    }
                    Some(true) => say("lost", format!("{} HUNT LOST on {name}: taken down {} ticks after the pick, before it \
                                                       armed", head(sim, me), tick - q.picked)),
                    Some(false) => say("lost", format!("{} HUNT LOST on {name}: died without her", head(sim, me))),
                    None => say("lost", format!("{} HUNT LOST on {name}: no kill record", head(sim, me))),
                }
                Self::clear_marks(sim, &q, side);
                self.quarry = None;
            } else if tick >= q.picked + PICK_EVERY {
                Self::clear_marks(sim, &q, side);
                say("lapsed", format!("{} HUNT LAPSED on {} (alive after {} s)", head(sim, me), who(sim, q.entity),
                                      PICK_EVERY / 60));
                self.quarry = None;
            } else {
                self.quarry = Some(q);
            }
        }
        if self.quarry.is_some() || tick < next {
            return;
        }
        let cands: Vec<Candidate> = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter_map(|id| sim.get_entity(id).map(|e| (id, e.is_alive(), e.team(), e.hp())))
            .filter(|&(_, alive, t, _)| alive && t != team)
            .map(|(id, _, _, hp)| Candidate { entity: id, hp })
            .collect();
        match pick(&cands, &self.immune, &self.fought, tick) {
            Some(target) => {
                sim.add_buff(target, &BuffV1::timed(WAIT[side], ARM_T + 2));
                self.quarry = Some(Quarry { entity: target, who: team_lane(sim, target), picked: tick, armed: false,
                                            waited: 0 });
                self.next_pick = Some(tick + PICK_EVERY);
                let hp = cands.iter().find(|c| c.entity == target).map_or((0, 0), |c| c.hp);
                say("pick", format!("{} HUNT PICK {} (hp {}/{}, {} candidates)", head(sim, me), who(sim, target), hp.0,
                                    hp.1, cands.len()));
            }
            // nobody to name (all fought just now, hunted or dead): try again in a second
            None => self.next_pick = Some(tick + 60),
        }
    }
}

impl StablePassive for Hunt {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _player: usize, me: usize, target: usize, _damage: &mut usize) {
        self.note_fight(sim, me, target);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _player: usize, me: usize, attacker: usize, _damage: usize) {
        self.note_fight(sim, me, attacker);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, team) = (e.is_alive(), e.team());
        if alive != self.was_alive {
            say("life", format!("{} {} with {} marks kept", head(sim, me), if alive { "ALIVE" } else { "DEAD" },
                                self.kept.iter().filter(|b| b.name() == MARK).count()));
            self.was_alive = alive;
        }
        self.keep(sim, me, alive);
        self.step(sim, me, team, alive);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn c(entity: usize, hp: usize, max: usize) -> Candidate {
        Candidate { entity, hp: (hp, max) }
    }

    fn kill(tick: usize, killer: (usize, u32), victim_lane: u32, assists: &[u32]) -> KillLogV1 {
        let mut a = [0u32; 4];
        a[..assists.len()].copy_from_slice(assists);
        KillLogV1 { tick, killer_team: killer.0, killer_position: killer.1, killed_position: victim_lane,
                    assist_count: assists.len() as u32, assist_positions: a }
    }

    #[test]
    fn she_names_the_squishiest_one_she_has_not_just_fought_or_hunted() {
        let cands = [c(10, 900, 1000), c(11, 300, 700), c(12, 700, 700), c(13, 500, 1500)];
        assert_eq!(pick(&cands, &[], &[], 1000), Some(11), "the lowest max health, then the lowest health share");
        assert_eq!(pick(&cands, &[(11, 5000)], &[], 1000), Some(12), "hunted: immune until 5000");
        assert_eq!(pick(&cands, &[(11, 900)], &[], 1000), Some(11), "the immunity ran out");
        assert_eq!(pick(&cands, &[], &[(11, 800)], 1000), Some(12), "fought 200 ticks ago");
        assert_eq!(pick(&cands, &[], &[(11, 1000 - COMBAT_T)], 1000), Some(11), "fought 6 s ago: fine again");
        assert_eq!(pick(&[], &[], &[], 1000), None);
    }

    #[test]
    fn a_takedown_is_her_kill_or_her_assist_on_the_hunted_one() {
        let me = (0, 2);
        let victim = (1, 4);
        assert_eq!(takedown(&[kill(500, (0, 2), 4, &[])], victim, me, 100), Some(true), "her kill");
        assert_eq!(takedown(&[kill(500, (0, 3), 4, &[1, 2])], victim, me, 100), Some(true), "her assist");
        assert_eq!(takedown(&[kill(500, (0, 3), 4, &[1])], victim, me, 100), Some(false), "her team without her");
        assert_eq!(takedown(&[kill(500, (0, 3), 4, &[1, 0, 0, 0])], victim, me, 100), Some(false));
        assert_eq!(takedown(&[kill(500, (0, 2), 3, &[])], victim, me, 100), None, "somebody else died");
        assert_eq!(takedown(&[kill(50, (0, 2), 4, &[])], victim, me, 100), None, "before the pick");
        assert_eq!(takedown(&[kill(500, (1, 1), 4, &[])], victim, me, 100), None, "not killed by the other team: no record");
        // an older death of the same champion, then the one after the pick
        let log = [kill(50, (0, 3), 4, &[]), kill(400, (0, 1), 2, &[]), kill(500, (0, 3), 4, &[2])];
        assert_eq!(takedown(&log, victim, me, 100), Some(true));
    }

    #[test]
    fn params_come_from_the_copy() {
        assert_eq!(parse_params(r#"{"ap":2,"as":5,"show":60}"#), Params { attack_speed: 5, magic_power: 2, show: 60 });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn kept_marks_pair_by_their_numbers() {
        let mut m = BuffV1::named(MARK);
        m.attack_speed_mult = 4;
        let h = BuffV1::named(HAS);
        assert_eq!(missing(&[m, m, h], &[m]), vec![m, h]);
        assert!(missing(&[m], &[m, m]).is_empty());
    }

    #[test]
    fn the_timings_are_league_s() {
        assert_eq!((PICK_EVERY, ARM_T, IMMUNE_T, COMBAT_T), (4500, 480, 14400, 360));
        assert!(ARM_T < PICK_EVERY && FIRST_PICK < PICK_EVERY);
        assert_ne!(WAIT[0], WAIT[1]);
        assert_ne!(HUNTED[0], HUNTED[1]);
    }
}
