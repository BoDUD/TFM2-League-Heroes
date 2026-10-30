//! 提莫主动种蘑菇（0.2.0，用户 2026-10-30：「提莫好像不会种蘑菇了？」→「要，照LOL种」）：AI 钩子 `league_teemo_shrooms:sow`。
//!
//! 游戏的 AI 只把 R 往射程里的敌方英雄脚下扔（R 是大招：5 级解锁，3 次充能，3600 tick 回满、一次 1200 tick），打得不顺、
//! 没碰上人时一颗都不种（那天看的一场 5 分半才第一颗）。英雄联盟的提莫一有蘑菇就往草丛、路口埋。本钩子在他没在打架时替
//! AI 把 R 按在身边的草丛里（判断在 [`can_sow`]、[`base_free`]、[`sow_spot`]，纯计算、单元测试）：
//!
//! - **什么时候**：R 已解锁、充能多于 `KEEP`（留一个给打架时 AI 自己扔；只有一次充能的格子、充满了也种），`FIGHT_R` 内没有
//!   敌方英雄（看不看得见都算），AI 这一 tick 在走路、站着或打英雄以外的东西（打英雄、放技能、回城时不管），离上一次按下超过
//!   `GAP` tick；他活着、没被控。
//! - **种在哪**：这局地图（按站进墙里的单位最少挑，[`pick_grid`]）的草丛格子（地图文档的 `bushes`，奈德丽附加包的读法）里
//!   离他最近的一格的中心：在 `REACH` 内（R 的射程
//!   75000 留点余量，单元测试对照副本）、`SPREAD` 内没有他埋着的蘑菇（一片草丛不扎堆）、`CLEAR_R` 内没有敌方单位（一落地
//!   就会被踩）、离自己水晶 `HOME_R` 以外（家里不种）。
//! - 日志：按下记 `SOW`（从哪、种到哪、R 剩几次、地上几个、AI 原来在干什么），引擎不收这个输入记 `SOW ... REFUSED`；按下后
//!   `WATCH` tick 内那里长出了他的蘑菇记 `SOWN`，没长出来记 `SOW MISSED`。你看的那场每条都记，预模拟先记 30 条、之后每 50 条记一条。
//!
//! 他埋着的蘑菇由被动记（`FIELDS`，按模拟和玩家），本钩子只读。

use mod_api_stable::*;

use super::{bush, dist, field_of, head, tally, wlog, Pt, HERO, ID};

/// 排在 league_ult_press（100）之后、league_unlock_guard（i32::MAX）之前。
pub const PRIORITY: i32 = 105;
/// 草丛离他这么近才种（主包 R 的射程 75000，留余量：按下到出手之间他还在走）。
pub const REACH: f64 = 70_000.0;
/// 这么近有敌方英雄（看不看得见都算）就不种：留给 AI 打架时自己扔。
pub const FIGHT_R: f64 = 70_000.0;
/// 新蘑菇离他埋着的每个蘑菇至少这么远（两格草丛）。
pub const SPREAD: f64 = 64_000.0;
/// 落点这么近有敌方单位（英雄、小兵、野怪）就不种：布好前就会被踩（踩发 8000）。
pub const CLEAR_R: f64 = 20_000.0;
/// 离自己水晶这么近的草丛不种（家里）。
pub const HOME_R: f64 = 160_000.0;
/// 留几次充能给打架。
pub const KEEP: usize = 1;
/// 两次按下至少隔这么多 tick（R 出手 26 tick，蘑菇飞过去、落地）。
pub const GAP: usize = 120;
/// 按下后这么多 tick 内落点 `SOWN_R` 内长出他的蘑菇算种上了。
pub const WATCH: usize = 180;
pub const SOWN_R: f64 = 12_000.0;

/// R can go into a bush now: unlocked, a use left over the `KEEP` for fights - or every use there is (a slot of one use,
/// or all of them back).
pub fn can_sow(unlocked: bool, uses: usize, max_uses: usize) -> bool {
    unlocked && uses > 0 && (uses > KEEP || uses >= max_uses.max(1))
}

/// Uses ready in the slot: its charges, or one when it has no charges and its cooldown is over.
pub fn uses(c: &CooldownV1) -> usize {
    if c.max_charges <= 1 {
        usize::from(c.remaining == 0 || c.charges > 0)
    } else {
        c.charges
    }
}

/// The AI's input this tick leaves room for a throw: walking, standing, or hitting something that is no champion.
pub fn base_free(kind: Option<InputKindV1>, on_champion: bool) -> bool {
    match kind {
        None | Some(InputKindV1::Move) => true,
        Some(InputKindV1::Attack) => !on_champion,
        _ => false,
    }
}

/// This match's bushes: the map read with the fewest of the units standing in its walls (league_camille_wall's pick),
/// then its bush grid - None when that map has none (bush::pick_bushes picks among maps with bushes only: on another
/// map he would sow at the 5v5 map's bushes).
pub fn pick_grid(points: &[Pt], maps: &[bush::MapGrids]) -> Option<bush::Grid> {
    maps.iter()
        .min_by_key(|m| m.walls.as_ref().map_or(usize::MAX / 2, |w| points.iter().filter(|p| w.at(p.0, p.1)).count()))
        .and_then(|m| m.bushes.clone())
}

/// The centre of every bush cell, world units.
pub fn bush_spots(g: &bush::Grid) -> Vec<Pt> {
    g.cells
        .iter()
        .enumerate()
        .flat_map(|(y, row)| {
            row.iter()
                .enumerate()
                .filter(|(_, v)| **v != 0)
                .map(move |(x, _)| ((x as f64 + 0.5) * bush::CELL, (y as f64 + 0.5) * bush::CELL))
        })
        .collect()
}

/// Where the next shroom goes: of the bush `spots`, the nearest to him within `REACH` that has none of his `shrooms`
/// within `SPREAD`, no enemy `units` within `CLEAR_R` and lies `HOME_R` or more from his nexus - None when none does.
pub fn sow_spot(me: Pt, spots: &[Pt], shrooms: &[Pt], units: &[Pt], home: Option<Pt>) -> Option<Pt> {
    spots
        .iter()
        .copied()
        .filter(|&s| dist(me, s) <= REACH)
        .filter(|&s| !shrooms.iter().any(|&f| dist(f, s) < SPREAD))
        .filter(|&s| !units.iter().any(|&u| dist(u, s) < CLEAR_R))
        .filter(|&s| home.is_none_or(|h| dist(h, s) >= HOME_R))
        .min_by(|&a, &b| dist(me, a).total_cmp(&dist(me, b)))
}

// ===================== 游戏里 =====================

const STOP: [CcKindV1; 9] = [CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Bind, CcKindV1::Taunt, CcKindV1::Fear,
                             CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::Animation, CcKindV1::ForceMove];

fn pt(e: &StableEntity<'_, '_>) -> Pt {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

#[derive(Clone, Default)]
pub struct Sow {
    recalling: bool,
    /// this match's bush grid: None until looked up, Some(None) when the map has none
    grid: Option<Option<bush::Grid>>,
    /// the tick of the last press (`GAP`)
    last: Option<usize>,
    /// the last press: (tick, spot), until a shroom of his shows up there or `WATCH` ticks pass
    pressed: Option<(usize, Pt)>,
    /// the R slot's charges written to the log once
    told: bool,
}

impl StablePlayerAi for Sow {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:sow")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == HERO
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        self.recalling = match base {
            Some(b) => b.kind == InputKindV1::Return.code(),
            None => self.recalling,
        };
        if self.recalling {
            return None;
        }
        let player = ctx.player_id();
        let (spot, line) = {
            let sim = ctx.sim()?;
            let e = sim.get_player(player)?.champion()?;
            if !e.is_alive() || (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| STOP.iter().any(|k| k.code() == c.kind))) {
                return None;
            }
            let (id, team, at) = (e.id(), e.team(), pt(&e));
            let tick = sim.tick();
            let field = field_of(&sim, player, id);
            if let Some((t0, s)) = self.pressed {
                if field.iter().any(|f| f.planted >= t0 && dist(f.at, s) <= SOWN_R) {
                    if let Some(n) = tally(&sim, "sown") {
                        wlog(format!("{} SOWN #{n}: the shroom is in the bush at ({:.0}, {:.0}), {} ticks after the press",
                                     head(&sim, id), s.0, s.1, tick.saturating_sub(t0)));
                    }
                    self.pressed = None;
                } else if tick >= t0 + WATCH || tick < t0 {
                    if let Some(n) = tally(&sim, "sow missed") {
                        wlog(format!("{} SOW MISSED #{n}: no shroom at ({:.0}, {:.0}) {WATCH} ticks after the press",
                                     head(&sim, id), s.0, s.1));
                    }
                    self.pressed = None;
                }
            }
            let c = e.cooldown(SkillSlotV1::Ult)?;
            if c.unlocked && !self.told {
                self.told = true;
                if let Some(n) = tally(&sim, "r unlocked") {
                    wlog(format!("{} R UNLOCKED #{n}: {} of {} charges, {} ticks to the next", head(&sim, id), c.charges,
                                 c.max_charges, c.next_charge_ticks));
                }
            }
            if !can_sow(c.unlocked, uses(&c), c.max_charges) || self.last.is_some_and(|t| tick >= t && tick < t + GAP) {
                return None;
            }
            let on_champion = base.is_some_and(|b| {
                InputTargetKindV1::from_code(b.target.kind) == Some(InputTargetKindV1::Target)
                    && sim.get_entity(b.target.target_id).is_some_and(|t| t.kind() == Some(EntityKindV1::Champion))
            });
            if !base_free(base.and_then(|b| InputKindV1::from_code(b.kind)), on_champion) {
                return None;
            }
            let (mut champs, mut units, mut home) = (Vec::new(), Vec::new(), None);
            for i in 0..sim.entity_count() {
                let Some(u) = sim.entity_at(i) else { continue };
                if !u.is_alive() || u.id() == id {
                    continue;
                }
                let kind = u.kind();
                if u.team() == team {
                    if kind == Some(EntityKindV1::Nexus) {
                        home = Some(pt(&u));
                    }
                    continue;
                }
                if u.is_tower() || kind == Some(EntityKindV1::Nexus) {
                    continue;
                }
                // seen or not (one waiting in a bush counts too): the throw stays for the fight
                if kind == Some(EntityKindV1::Champion) {
                    champs.push(pt(&u));
                }
                units.push(pt(&u));
            }
            if champs.iter().any(|&p| dist(at, p) <= FIGHT_R) {
                return None;
            }
            if self.grid.is_none() {
                let points: Vec<Pt> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i)).filter(|u| u.is_alive())
                    .map(|u| pt(&u)).collect();
                let g = pick_grid(&points, &bush::maps());
                wlog(match &g {
                    Some(g) => format!("{} BUSHES: {} bush cells to sow in", head(&sim, id), g.count()),
                    None => format!("{} BUSHES: no bush grid - no shrooms sown, only the AI's throws", head(&sim, id)),
                });
                self.grid = Some(g);
            }
            let grid = self.grid.as_ref()?.as_ref()?;
            let shrooms: Vec<Pt> = field.iter().map(|f| f.at).collect();
            let spot = sow_spot(at, &bush_spots(grid), &shrooms, &units, home)?;
            let was = base.and_then(|b| InputKindV1::from_code(b.kind)).map_or("standing".to_string(), |k| format!("{k:?}"));
            let line = tally(&sim, "sow").map(|n| {
                format!("{} SOW #{n}: from ({:.0}, {:.0}) into the bush at ({:.0}, {:.0}), {:.0} away; R {}/{}, {} in the ground, the AI was {was}",
                        head(&sim, id), at.0, at.1, spot.0, spot.1, dist(at, spot), uses(&c), c.max_charges, shrooms.len())
            });
            (spot, line)
        };
        let tick = ctx.tick();
        self.last = Some(tick);
        let input = InputV1::action(InputKindV1::Ult, InputTargetV1::pos(spot.0.max(0.0) as u64, spot.1.max(0.0) as u64));
        if !ctx.is_valid_input(&input) {
            if let Some(l) = line {
                wlog(format!("{l} - REFUSED: the engine took no R at the spot"));
            }
            return None;
        }
        self.pressed = Some((tick, spot));
        if let Some(l) = line {
            wlog(l);
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_charge_kept_for_fights() {
        assert!(!can_sow(false, 3, 3), "locked");
        assert!(!can_sow(true, 0, 3));
        assert!(!can_sow(true, 1, 3), "the last one waits for a fight");
        assert!(can_sow(true, 2, 3));
        assert!(can_sow(true, 3, 3));
        assert!(can_sow(true, 1, 1), "a slot of one use: every use is all of them");
        let c = |remaining, charges, max_charges| CooldownV1 {
            size: std::mem::size_of::<CooldownV1>(),
            remaining,
            cooltime: 3600,
            max_charges,
            charges,
            next_charge_ticks: remaining,
            unlocked: true,
        };
        assert_eq!(uses(&c(0, 2, 3)), 2);
        assert_eq!(uses(&c(600, 1, 3)), 1);
        assert_eq!(uses(&c(0, 0, 1)), 1, "no charges: ready when the cooldown is over");
        assert_eq!(uses(&c(600, 0, 0)), 0);
    }

    #[test]
    fn walking_standing_or_farming_leave_room() {
        assert!(base_free(None, false));
        assert!(base_free(Some(InputKindV1::Move), false));
        assert!(base_free(Some(InputKindV1::Attack), false), "a minion, a monster, a tower");
        assert!(!base_free(Some(InputKindV1::Attack), true), "fighting a champion");
        for k in [InputKindV1::Skill, InputKindV1::Skill2, InputKindV1::Ult, InputKindV1::Return] {
            assert!(!base_free(Some(k), false), "{k:?}");
        }
    }

    /// The match's map by its walls, bushes or none: never another map's bushes.
    #[test]
    fn the_bushes_of_the_map_played() {
        let grid = |rows: &[&str]| bush::Grid { cells: rows.iter().map(|r| r.chars().map(|c| (c == '#') as i64).collect()).collect() };
        let moba = bush::MapGrids { walls: Some(grid(&["#.", ".."])), bushes: Some(grid(&["..", ".#"])) };
        let lane = bush::MapGrids { walls: Some(grid(&[".#", "##"])), bushes: None };
        let in_cell = |x: f64, y: f64| ((x + 0.5) * bush::CELL, (y + 0.5) * bush::CELL);
        // units in the lane map's open cell (0, 0): a wall of the 5v5 map - the lane map, which has no bushes
        assert_eq!(pick_grid(&[in_cell(0.0, 0.0)], &[moba.clone(), lane.clone()]), None);
        // units in the 5v5 map's open cells, the lane map's walls: the 5v5 map's bushes
        assert_eq!(pick_grid(&[in_cell(1.0, 1.0), in_cell(1.0, 0.0)], &[lane, moba.clone()]), moba.bushes);
        assert_eq!(pick_grid(&[], &[]), None);
    }

    #[test]
    fn bush_cells_give_their_centres() {
        let g = bush::Grid { cells: vec![vec![0, 1], vec![1, 0]] };
        assert_eq!(bush_spots(&g), vec![(1.5 * bush::CELL, 0.5 * bush::CELL), (0.5 * bush::CELL, 1.5 * bush::CELL)]);
    }

    #[test]
    fn the_nearest_free_bush_in_reach() {
        let me = (400_000.0, 400_000.0);
        let near = (430_000.0, 400_000.0);
        let next = (400_000.0, 450_000.0);
        let far = (400_000.0 + REACH + 1_000.0, 400_000.0);
        let spots = [far, next, near];
        assert_eq!(sow_spot(me, &spots, &[], &[], None), Some(near));
        // one of his shrooms by the nearest (31623 off it, 84853 off the next): the next one
        assert_eq!(sow_spot(me, &spots, &[(460_000.0, 390_000.0)], &[], None), Some(next));
        assert_eq!(sow_spot(me, &spots, &[(460_000.0, 390_000.0), (400_000.0, 500_000.0)], &[], None), None);
        // a minion on it: it would go off before it is armed
        assert_eq!(sow_spot(me, &spots, &[], &[(431_000.0, 405_000.0)], None), Some(next));
        // his base (123693 off the nearest, 180278 off the next): not there
        assert_eq!(sow_spot(me, &spots, &[], &[], Some((460_000.0, 280_000.0))), Some(next));
        // nothing left in reach
        assert_eq!(sow_spot(me, &[far], &[], &[], None), None);
        assert_eq!(sow_spot(me, &[], &[], &[], None), None);
    }

    /// The reach stays inside the R's range in the copy (the main pack's).
    #[test]
    fn the_reach_is_inside_the_r_range() {
        let copy = include_str!("../override/league_teemo.data_champion");
        let at = copy.find("\"action_name\": \"ult\"").expect("the ult");
        let tail = &copy[at..];
        let r = &tail[tail.find("\"range\": ").expect("its range") + 9..];
        let range: f64 = r[..r.find(|c: char| !c.is_ascii_digit()).unwrap()].parse().unwrap();
        assert!(REACH < range && range - REACH <= 10_000.0, "R range {range}, REACH {REACH}");
        assert!(FIGHT_R >= REACH, "an enemy champion the throw could reach is a fight");
        assert!(CLEAR_R > super::super::TRIGGER, "a unit on the spot sets it off");
    }
}
