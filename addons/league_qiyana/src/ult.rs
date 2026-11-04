//! 惊才绝景（R）照英雄联盟 V26.21（用户 2026-11-04：「奇亚娜很多机制和英雄联盟不一样」）：
//!
//! - **风**（[`launch`]，主包 R 第 `r_at` - 1 tick）：朝目标英雄吹，碰到第一面墙（墙格子、5v5 地图四边、地图外，[`terrain::windblast`]）
//!   就停，最远 `r_len`。画面是主包的 `league_qiyana_r_wave`（本包放的飞行物，飞到停点）；它路上碰到的敌人（[`push`]）只被
//!   沿风的方向击退 `r_kb_speed` x `r_kb_t`（撞墙就停在墙前，免控的不动），**不受伤害**。
//! - **冲击波**（[`boom`]，风放出后 `r_det` tick，被吹的人都到了）：沿风路过的草丛（连着的那一片）、河道（进河的地方前后 `r_span`）
//!   和撞上的那面墙（连着的墙格子里离停点 `r_span` 内的，墙边 `r_border` 内；地图的边是停点前后 `r_span` 的一段）走
//!   （[`terrain::Shock::caught`]）。被打到的：`r_dmg` + `r_ratio`% 攻击力 + 最大生命的 `r_hp`%（野怪这部分最多 `r_mon_cap`）物理
//!   伤害，按离这股冲击波起点的远近晕 `r_stun_max`（贴着）到 `r_stun_min`（`r_span` 外）tick（[`stun_ticks`]）。打到敌方英雄时给她挂
//!   `league_qiyana_r_go`，主包数据下一 tick 接 R -> E -> Q。风没碰到任何地形：只击退。凌人贵气不算 R。
//! - **读不到地图**（地图钩子没跑）：照主包，风路上的人都伤害、击退、`r_stun` tick 后晕（[`stun`]）。
//! - **AI 钩子**（[`super::ai`]）用 [`best`] 挑目标：朝每个够得着的敌方英雄吹一次，风路上的人先按击退挪过去，看冲击波打到几个
//!   敌方英雄。

use std::collections::HashMap;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

use super::terrain::{self, Blast, Kind, MapGrids, Pt, Shock};
use super::{alive_at, break_field, current_map, dist, foe_of, foes, note, params_of, pt, qy, queue, seg, sim_no, unit, upos, Foe,
            Params, ID};

/// 冲击波的画面最多放几处。
pub const SPOTS: usize = 8;
/// 她挂 `r_go` 多久（主包数据在冲击波后第 2 tick 读）。
pub const GO_T: usize = 4;

/// 一阵风：(这份模拟, 她) -> 它。`blast` 为 None：读不到地图，照主包。
#[derive(Clone, Debug)]
struct Shot {
    blast: Option<Blast>,
    dir: Pt,
    pushed: usize,
    champs: usize,
}

static SHOTS: LazyLock<Mutex<HashMap<(u64, usize), Shot>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// 击退多远：`full`，路上撞墙就停在墙前（身体 `r` + 1000）。
pub fn push_len(m: Option<&MapGrids>, at: Pt, dir: Pt, r: f64, full: f64) -> f64 {
    m.and_then(|m| terrain::wall_travel(m, at, dir, full, r)).map_or(full, |w| w.min(full))
}

/// 离冲击波起点 `d` 的人晕多久：贴着 `r_stun_max`，`r_span` 外 `r_stun_min`，中间按距离。
pub fn stun_ticks(p: &Params, d: f64) -> usize {
    let k = (d / p.r_span.max(1) as f64).clamp(0.0, 1.0);
    (p.r_stun_max as f64 - (p.r_stun_max.saturating_sub(p.r_stun_min)) as f64 * k).round() as usize
}

/// 冲击波打一个人多少（物理，护甲前）：`r_dmg` + `r_ratio`% 攻击力 + 最大生命 `r_hp`%（野怪这部分最多 `r_mon_cap`）。
pub fn r_damage(p: &Params, ad: usize, max_hp: usize, monster: bool) -> usize {
    let hp = max_hp * p.r_hp / 100;
    p.r_dmg + ad * p.r_ratio / 100 + if monster { hp.min(p.r_mon_cap) } else { hp }
}

/// 风从 `from` 朝 `toward` 吹：它走的路和冲击波。
pub fn wind(m: &MapGrids, from: Pt, toward: Pt, p: &Params) -> Option<(Blast, Shock)> {
    let dir = unit((toward.0 - from.0, toward.1 - from.1))?;
    let b = terrain::windblast(m, from, dir, p.r_len as f64);
    let s = terrain::shockwave(m, &b, p.r_span as f64);
    Some((b, s))
}

/// 朝 `toward` 放 R 的话，冲击波打得到 `champs` 里的谁（风路上的人先按击退挪过去，免控的不动）。
pub fn caught_by(m: &MapGrids, from: Pt, toward: Pt, champs: &[Foe], p: &Params) -> Vec<usize> {
    let Some((b, s)) = wind(m, from, toward, p) else { return Vec::new() };
    if s.none() {
        return Vec::new();
    }
    let full = (p.r_kb_speed * p.r_kb_t) as f64;
    champs
        .iter()
        .filter(|f| {
            let (off, along) = seg(f.at, from, b.stop);
            let on_path = off <= p.r_w as f64 + f.r && along > -f.r;
            let at = if on_path && !f.immune {
                let len = push_len(Some(m), f.at, b.dir, f.r, full);
                (f.at.0 + b.dir.0 * len, f.at.1 + b.dir.1 * len)
            } else {
                f.at
            };
            s.caught(m, at.0, at.1, f.r, p.r_border as f64, p.r_span as f64).is_some()
        })
        .map(|f| f.id)
        .collect()
}

/// R 的目标：朝哪个（`cands`：够得着的敌方英雄）吹，冲击波打到的敌方英雄（`champs` 里）最多；一样多时 AI 想打的那个、再挑生命
/// 比例低的。一个都打不到为 None。
#[derive(Clone, Debug, PartialEq)]
pub struct Plan {
    pub target: usize,
    pub caught: Vec<usize>,
}

pub fn best(m: &MapGrids, from: Pt, cands: &[Foe], champs: &[Foe], aimed: Option<usize>, p: &Params) -> Option<Plan> {
    cands
        .iter()
        .map(|t| (t, caught_by(m, from, t.at, champs, p)))
        .filter(|(_, c)| !c.is_empty())
        .max_by_key(|(t, c)| (c.len(), Some(t.id) == aimed, std::cmp::Reverse(t.hp * 1000 / t.max.max(1))))
        .map(|(t, c)| Plan { target: t.id, caught: c })
}

fn stage(sim: &mut StableSim<'_>, me: usize, name: &str, input: InputTargetV1, delay: usize) {
    queue(sim, name, me, input, delay);
}

/// 放 R（主包第 `r_at` - 1 tick，目标 = 那个英雄）：风朝他吹到第一面墙，`r_det` tick 后冲击波。
pub fn launch(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    break_field(sim, me, "R");
    let Some(here) = alive_at(sim, me) else { return };
    let p = params_of(sim, me);
    let target = (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id);
    let toward = target.and_then(|t| alive_at(sim, t)).or_else(|| {
        foes(sim, me)
            .into_iter()
            .filter(|f| f.champion)
            .min_by(|a, b| dist(a.at, here).total_cmp(&dist(b.at, here)))
            .map(|f| f.at)
    });
    let Some(dir) = toward.and_then(|t| unit((t.0 - here.0, t.1 - here.1))) else {
        note(sim, "r", me, |n| format!("R #{n}: no champion to blow at"));
        return;
    };
    let map = current_map(sim);
    let blast = map.as_ref().map(|m| terrain::windblast(m, here, dir, p.r_len as f64));
    let stop = blast.as_ref().map_or((here.0 + dir.0 * p.r_len as f64, here.1 + dir.1 * p.r_len as f64), |b| b.stop);
    // the wind leaves from her front (nobody behind her is caught)
    let my_r = sim.get_entity(me).map_or(0.0, |e| e.radius() as f64);
    let lead = my_r.min(dist(here, stop));
    let start = (here.0 + dir.0 * lead, here.1 + dir.1 * lead);
    let (x, y) = upos(start);
    let (tx, ty) = upos(stop);
    let spec = ProjectileSpawnV1 {
        caster_id: me,
        team: sim.get_entity(me).map_or(0, |e| e.team()),
        x,
        y,
        radius: p.r_w as u64,
        speed: p.r_speed.max(1) as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: tx,
        target_y: ty,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::EnemyWithoutTower.code(),
    };
    let flew = sim.spawn_projectile(&qy("r_wave"), &format!("{ID}:r_push"), &spec);
    let key = (sim_no(sim, me), me);
    SHOTS.lock().unwrap_or_else(|e| e.into_inner()).insert(key, Shot { blast: blast.clone(), dir, pushed: 0, champs: 0 });
    if blast.is_some() {
        stage(sim, me, "r_boom", InputTargetV1::pos(tx, ty), p.r_det);
    }
    let said = match &blast {
        None => "no map read: every one on its way struck as in the main pack".to_string(),
        Some(b) => {
            let stop_said = match (b.wall, map.as_ref()) {
                (Some(w), Some(m)) if m.walls.as_ref().is_some_and(|g| g.at(w.0, w.1)) => {
                    let c = terrain::cell_of(w.0, w.1);
                    format!("stops at the wall cell ({}, {})", c.0, c.1)
                }
                (Some(w), Some(m)) => format!("stops at the map's {:?} edge", m.edge(w.0, w.1).map(|e| e.0)),
                _ => "blows its whole length".to_string(),
            };
            format!("{stop_said} after {:.0}; brush {} cells; river {}", dist(here, b.stop), b.brush.len(),
                    b.river.map_or("no".to_string(), |c| format!("at {}", pt(c))))
        }
    };
    note(sim, "r", me, |n| format!("R #{n} at #{}: the wind {said}{}", target.unwrap_or(0),
                                   if flew { "" } else { " (spawn_projectile refused: nobody pushed)" }));
}

/// 风碰到一个敌人：沿风的方向击退（撞墙停在墙前，免控的不动）；读不到地图时照主包：伤害、击退、晕。
pub fn push(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if input.kind != InputTargetKindV1::Target.code() {
        return;
    }
    let Some(f) = foe_of(sim, input.target_id) else { return };
    let key = (sim_no(sim, me), me);
    let shot = SHOTS.lock().unwrap_or_else(|e| e.into_inner()).get(&key).cloned();
    let p = params_of(sim, me);
    let dir = shot.as_ref().map(|s| s.dir).or_else(|| alive_at(sim, me).and_then(|h| unit((f.at.0 - h.0, f.at.1 - h.1))));
    let Some(dir) = dir else { return };
    let fallback = shot.as_ref().is_none_or(|s| s.blast.is_none());
    if !f.immune {
        let map = if fallback { None } else { current_map(sim) };
        let full = (p.r_kb_speed * p.r_kb_t) as f64;
        let len = push_len(map.as_deref(), f.at, dir, f.r, full);
        if len >= 1.0 {
            let ticks = (len / p.r_kb_speed.max(1) as f64).ceil().max(1.0);
            let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks as u64);
            cc.dx = (dir.0 * len).round() as i64;
            cc.dy = (dir.1 * len).round() as i64;
            cc.speed = (len / ticks).ceil() as u64;
            sim.apply_cc(f.id, &cc);
        }
    }
    if let Some(s) = SHOTS.lock().unwrap_or_else(|e| e.into_inner()).get_mut(&key) {
        s.pushed += 1;
        s.champs += f.champion as usize;
    }
    if fallback {
        let ad = sim.get_entity(me).map_or(0, |e| e.stat().attack);
        sim.deal_damage(me, f.id, r_damage(&p, ad, f.max, f.monster), 0, AttackTypeV1::Skill);
        let on = InputTargetV1::target(f.id);
        sim.play_view_effect(&qy("r_hit"), me, &on, 0, 0, 0);
        sim.play_sfx(&qy("r_hit"), me, &on);
        stage(sim, me, "r_stun", on, p.r_kb_t);
        if f.champion {
            sim.entity_remove_buff(me, &qy("r_go"));
            // read by the data r_at - 1 + r_det + 2 ticks after the cast: past the hit of anyone on the way
            sim.add_buff(me, &BuffV1::timed(&qy("r_go"), p.r_det + GO_T + 2));
        }
    }
}

/// 读不到地图时（照主包）：击退完了晕 `r_stun` tick。
pub fn stun(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    if input.kind != InputTargetKindV1::Target.code() {
        return;
    }
    let Some(f) = foe_of(sim, input.target_id) else { return };
    if !f.immune {
        let p = params_of(sim, me);
        sim.apply_cc(f.id, &CcV1::stun(p.r_stun as u64));
    }
}

/// 冲击波：沿风路过的草丛、河道和撞上的墙边走，伤害并按远近晕；打到敌方英雄就给她挂 `r_go`（R -> E -> Q）。
pub fn boom(sim: &mut StableSim<'_>, me: usize, _input: InputTargetV1) {
    let key = (sim_no(sim, me), me);
    let Some(shot) = SHOTS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key) else { return };
    let Some(blast) = shot.blast else { return };
    let Some(m) = current_map(sim) else { return };
    let p = params_of(sim, me);
    let shock = terrain::shockwave(&m, &blast, p.r_span as f64);
    let ad = sim.get_entity(me).map_or(0, |e| e.stat().attack);
    let (mut champs, mut others) = (Vec::new(), 0);
    if !shock.none() {
        for f in foes(sim, me) {
            let Some(d) = shock.caught(&m, f.at.0, f.at.1, f.r, p.r_border as f64, p.r_span as f64) else { continue };
            sim.deal_damage(me, f.id, r_damage(&p, ad, f.max, f.monster), 0, AttackTypeV1::Skill);
            let t = stun_ticks(&p, d);
            if !f.immune {
                sim.apply_cc(f.id, &CcV1::stun(t as u64));
            }
            let on = InputTargetV1::target(f.id);
            sim.play_view_effect(&qy("r_hit"), me, &on, 0, 0, 0);
            sim.play_sfx(&qy("r_hit"), me, &on);
            if f.champion {
                champs.push(format!("#{} {}{}", f.id, if f.immune { "immune".to_string() } else { format!("{t}t") },
                                    format_args!(" {:.0} off", d)));
            } else {
                others += 1;
            }
        }
        for (kind, at) in shock.spots(p.r_span as f64, SPOTS) {
            let view = match kind {
                Kind::Wall => "q_r_hit",
                Kind::River => "q_w_hit",
                Kind::Brush => "q_g_hit",
            };
            let (x, y) = upos(at);
            sim.play_view_effect(&qy(view), me, &InputTargetV1::pos(x, y), 0, 0, 0);
        }
    }
    if !champs.is_empty() {
        sim.entity_remove_buff(me, &qy("r_go"));
        sim.add_buff(me, &BuffV1::timed(&qy("r_go"), GO_T));
    }
    let terrain_said = if shock.none() {
        "no terrain reached: knock-back only".to_string()
    } else {
        format!("wall {} cells{}, brush {} cells, river {}", shock.wall.len(),
                shock.edge.map_or(String::new(), |e| format!(" / the {e:?} edge")), shock.brush.len(),
                if shock.river.is_some() { "yes" } else { "no" })
    };
    note(sim, "boom", me, |n| format!("R BOOM #{n}: {} champions [{}] and {others} others caught; {} pushed ({} champions); {terrain_said}",
                                      champs.len(), champs.join(", "), shot.pushed, shot.champs));
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::terrain::{Grid, CELL};

    fn map(walls: &[(usize, usize)]) -> MapGrids {
        let rows: Vec<String> = (0..30).map(|y| (0..30).map(|x| if walls.contains(&(x, y)) { '#' } else { '.' }).collect()).collect();
        let empty: Vec<String> = (0..30).map(|_| ".".repeat(30)).collect();
        MapGrids {
            mode: GameModeKindV1::Moba.code(),
            walls: Some(Grid::from_rows(&rows.iter().map(|s| s.as_str()).collect::<Vec<_>>())),
            bushes: Some(Grid::from_rows(&empty.iter().map(|s| s.as_str()).collect::<Vec<_>>())),
            river: None,
        }
    }

    fn champ(id: usize, at: Pt) -> Foe {
        Foe { id, at, r: 10_000.0, champion: true, monster: false, hp: 800, max: 1000, immune: false }
    }

    #[test]
    fn stun_by_proximity_and_damage() {
        let p = Params::default();
        assert_eq!(stun_ticks(&p, 0.0), 60);
        assert_eq!(stun_ticks(&p, 48_000.0), 45);
        assert_eq!(stun_ticks(&p, 500_000.0), 30);
        assert_eq!(r_damage(&p, 200, 2000, false), 50 + 180 + 200);
        // the max-health part capped on monsters
        assert_eq!(r_damage(&p, 200, 9000, true), 50 + 180 + 300);
    }

    #[test]
    fn the_shockwave_finds_the_one_pushed_into_the_wall() {
        // a wall column at x = 15 (cells 15, 1..5), far from the river; Qiyana 57600 from its face, the champion between
        let m = map(&[(15, 1), (15, 2), (15, 3), (15, 4), (15, 5)]);
        let p = Params::default();
        let me = (13.2 * CELL, 3.5 * CELL);
        let him = champ(1, (14.0 * CELL, 3.5 * CELL));
        // he stands 32000 from the wall: pushed against it (21000), caught
        assert_eq!(caught_by(&m, me, him.at, &[him], &p), vec![1]);
        // immune to crowd control: not pushed, and too far from the wall to be caught
        let still = Foe { immune: true, ..him };
        assert_eq!(caught_by(&m, me, still.at, &[still], &p), Vec::<usize>::new());
        // the other way, open ground: nobody
        let away = champ(2, (10.0 * CELL, 3.5 * CELL));
        assert_eq!(caught_by(&m, me, away.at, &[away], &p), Vec::<usize>::new());
        // the plan picks the one whose wind reaches a wall
        let plan = best(&m, me, &[away, him], &[away, him], Some(2), &p).unwrap();
        assert_eq!(plan.target, 1);
        assert_eq!(best(&m, me, &[away], &[away], Some(2), &p), None);
        // a wall beyond the wind's reach: nothing
        let short = (12.0 * CELL, 3.5 * CELL);
        assert_eq!(caught_by(&m, short, him.at, &[him], &p), Vec::<usize>::new());
    }

    #[test]
    fn pushes_stop_at_walls() {
        let m = map(&[(15, 12)]);
        let at = (14.0 * CELL, 12.5 * CELL);
        // 32000 to the wall's face minus the body and the gap
        assert_eq!(push_len(Some(&m), at, (1.0, 0.0), 10_000.0, 25_000.0), 21_000.0);
        assert_eq!(push_len(Some(&m), at, (-1.0, 0.0), 10_000.0, 25_000.0), 25_000.0);
        assert_eq!(push_len(None, at, (1.0, 0.0), 10_000.0, 25_000.0), 25_000.0);
    }
}
