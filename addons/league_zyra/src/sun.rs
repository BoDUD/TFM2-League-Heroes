//! 光合作用（彩蛋，用户 2026-11-05「植物大战僵尸」：蕾欧娜的技能命中婕拉的植物会让植物模型变大一号）。
//!
//! 植物不是单位，技能「命中」植物 = 蕾欧娜的技能落在植物站的地方。只在比赛里有蕾欧娜（哪一边都算：她的阳光落在植物上就长）时
//! 才看，每 tick：
//! - **婕拉的植物**：本包种子长的（`grow` 时记下）和主包数据在 Q、E 落点长的（Q、E 的 2 tick 标记记下落点和时间，之后落点上出现
//!   一个不动的、她的弹道 = 植物的区域；按落地时间认是荆棘喷射者还是藤蔓鞭击者：Q `q_delay` / `q_fast`、E `e_grow` tick）。
//! - **蕾欧娜的技能**：她的弹道在动的（E 的光刃）经过植物 `LINE_HIT` 以内；她不动的弹道（R 的阳光区域）出现 `R_AT` tick 后阳光
//!   落下，植物在 `R_HIT` 以内；她身上多了一层 `league_leona_eclipse_hold`（W 日蚀爆开）时植物在她 `W_HIT` 以内；任何单位身上
//!   多了一层她的 `league_leona_sunlight`（Q、E、W、R 打中的都挂）而他站在植物 `UNIT_HIT` 以内。
//! - **变大一号**：植物自己的画面照放（数据的是 ViewEffect，种子的是本包放的一次），本包在上面按同一个节奏放大一号的
//!   （`tools/art/fx_zyra_sun.py`，本包的 `effects/league_zyra_sun`，x1.5）：当前这一轮从下一帧放起（`<k>_big<j>`），之后每轮开头
//!   放一整轮（`<k>_big0`），最后放抖动和枯萎（`<k>_big_end`）；后放的画在先放的上面，大的盖住小的。变大时放一道她的金光
//!   （`sun_pop`）。只变大一次（一号），玩法不变（植物出手、伤害都照旧）。
//!
//! 状态记在每个婕拉自己的被动实例里（服务端预模拟和你看的那场各算各的）。日志 `SUN`（哪一招、哪株、多大了）。

use mod_api_stable::*;

use super::{at, dist, fpos, head, tally, wlog, zy, Kind, Params};

/// 植物画面的节奏（主包 league_zyra_big 的 t_plant / v_plant，30 帧 5 秒）：长出来 `GROW_T` tick，之后 `CYCLES` 轮摇摆、每轮
/// `CYCLE` tick（一轮 5 帧，前 4 帧各 12.75 tick、最后一帧 9 tick），`END_AT` 起抖动、枯萎，`LIFE` 时没了。
pub const GROW_T: usize = 29;
pub const CYCLE: usize = 60;
pub const CYCLES: usize = 4;
pub const END_AT: usize = GROW_T + CYCLES * CYCLE;
pub const LIFE: usize = 300;
/// 一轮里每一帧从第几 tick 开始。
pub const FRAME_AT: [usize; 5] = [0, 13, 26, 38, 51];

/// 植物的身子有多宽（单位）；蕾欧娜的技能落在这么近算命中：E 的光刃（半径 7000）经过、她的阳光刚打中的单位站在这里、
/// R 的阳光（半径 36000）、W 的日蚀爆开（她身边 35000）。
pub const BODY: f64 = 9_000.0;
pub const LINE_HIT: f64 = 7_000.0 + BODY;
pub const UNIT_HIT: f64 = 7_000.0 + BODY;
pub const R_HIT: f64 = 36_000.0 + BODY;
pub const W_HIT: f64 = 35_000.0 + BODY;
/// R 的阳光区域出现后多少 tick 落下（主包：delay 60，apply 38）。
pub const R_AT: usize = 37;
/// 记她身上阳光层数的单位：离还没变大的植物这么近（走到植物上之前就记着，带着别处挂的阳光走过来不算新的）。
pub const WATCH_R: f64 = 150_000.0;
/// 数据的植物：Q、E 落点这么近、落地时间差这么多以内的不动弹道就是它；落点等这么久没长出来就不等了。
pub const MATCH_R: f64 = 6_000.0;
pub const MATCH_T: usize = 2;
pub const PENDING_T: usize = 45;
/// 比赛里有没有蕾欧娜：每这么多 tick 再看一次（被动实例可能接着下一场用）。
pub const LOOK_EVERY: usize = 300;

pub const LEONA: &str = "league_leona";
pub const SUNLIGHT: &str = "league_leona_sunlight";
pub const ECLIPSE_HOLD: &str = "league_leona_eclipse_hold";

/// 放哪一段大的：一轮从第 `j` 帧放起，或者最后的抖动和枯萎。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Seg {
    From(usize),
    End,
}

/// 植物 `age` tick 时被命中：大的从它第几 tick（年龄）开始、放哪一段。太晚（已经在枯萎）就 None。
pub fn plan(age: usize) -> Option<(usize, Seg)> {
    if age >= END_AT {
        return None;
    }
    if age < GROW_T {
        return Some((GROW_T, Seg::From(0)));
    }
    let o = (age - GROW_T) % CYCLE;
    let base = age - o;
    if let Some(j) = FRAME_AT.iter().position(|&f| f >= o) {
        return Some((base + FRAME_AT[j], Seg::From(j)));
    }
    let next = base + CYCLE;
    Some(if next >= END_AT { (END_AT, Seg::End) } else { (next, Seg::From(0)) })
}

/// 在年龄 `start` 放了 `seg` 之后，下一段：下一轮的开头放一整轮，轮完了放枯萎。
pub fn follow(start: usize, seg: Seg) -> Option<(usize, Seg)> {
    match seg {
        Seg::End => None,
        Seg::From(_) => {
            let next = start - (start.max(GROW_T) - GROW_T) % CYCLE + CYCLE;
            Some(if next >= END_AT { (END_AT, Seg::End) } else { (next, Seg::From(0)) })
        }
    }
}

/// 这一段的画面名（主包名字之后的部分）。
pub fn seg_view(kind: Kind, seg: Seg) -> String {
    let k = match kind {
        Kind::Spitter => "t",
        Kind::Lasher => "v",
    };
    match seg {
        Seg::From(j) => format!("{k}_big{j}"),
        Seg::End => format!("{k}_big_end"),
    }
}

/// 蕾欧娜上一 tick 新出现的弹道 `fresh`，这一 tick 的弹道 `now`：还在原地的是区域（R），不在了的是飞走的（E 的光刃）。
pub fn split_fresh(fresh: &[(u64, u64)], now: &[(u64, u64)]) -> (Vec<(u64, u64)>, Vec<(u64, u64)>) {
    fresh.iter().copied().partition(|s| now.contains(s))
}

/// 数据的植物：Q、E 的标记在 `mark` tick、落点 `land`；`born` tick 在 `spot` 出现一个不动的弹道，是不是它。
pub fn is_landing(p: &Params, kind: Kind, land: (f64, f64), mark: usize, spot: (f64, f64), born: usize) -> bool {
    let after = born.saturating_sub(mark);
    let near = |t: usize| after.abs_diff(t) <= MATCH_T;
    let timed = match kind {
        Kind::Spitter => near(p.q_delay) || near(p.q_fast),
        Kind::Lasher => near(p.e_grow),
    };
    timed && born >= mark && dist(land, spot) <= MATCH_R
}

#[derive(Clone, Debug)]
struct Shown {
    kind: Kind,
    pos: (f64, f64),
    born: usize,
    data: bool,
    big: bool,
    /// 下一段大的在哪个 tick 放、放哪段。
    next: Option<(usize, Seg)>,
}

#[derive(Clone, Debug)]
struct Landing {
    kind: Kind,
    land: (f64, f64),
    mark: usize,
}

/// 每个婕拉一份。
#[derive(Clone, Default)]
pub struct Sun {
    /// 比赛里有蕾欧娜（上次看的 tick）。
    leona: bool,
    looked: Option<usize>,
    plants: Vec<Shown>,
    landings: Vec<Landing>,
    /// 上一 tick 她的、蕾欧娜的弹道在哪（不动的 = 区域）；蕾欧娜的弹道里上一 tick 新出现的（这一 tick 还在原地 = R 的区域，
    /// 不在了 = 飞过去的 E 光刃）。
    mine: Vec<(u64, u64)>,
    hers: Vec<(u64, u64)>,
    fresh: Vec<(u64, u64)>,
    /// 蕾欧娜的 R：区域中心、阳光落下的 tick。
    r_zones: Vec<((f64, f64), usize)>,
    /// 单位身上蕾欧娜的阳光层数、蕾欧娜身上日蚀的层数（上一 tick）。
    sunlit: Vec<(usize, usize)>,
    holds: Vec<(usize, usize)>,
    pub n_sun: usize,
}

fn count(sim: &StableSim<'_>, id: usize, name: &str) -> usize {
    sim.get_entity(id).map_or(0, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).filter(|b| b.name() == name).count())
}

impl Sun {
    /// 比赛里有没有蕾欧娜（哪一边都算），隔一阵再看一次。
    fn look(&mut self, sim: &StableSim<'_>, me: usize) -> bool {
        let tick = sim.tick();
        if self.looked.is_none_or(|t| tick < t || tick >= t + LOOK_EVERY) {
            self.looked = Some(tick);
            let was = self.leona;
            self.leona = (0..sim.champion_count())
                .filter_map(|i| sim.get_entity(sim.champion_id_at(i)))
                .any(|e| e.name().as_deref() == Some(LEONA));
            if !self.leona {
                *self = Sun { looked: self.looked, n_sun: self.n_sun, ..Sun::default() };
            } else if !was {
                if let Some(k) = tally(sim, "sun leona") {
                    wlog(format!("{} SUN: Leona is in this match - her sunlight grows Zyra's plants one size #{k}", head(sim, me)));
                }
            }
        }
        self.leona
    }

    /// 本包的种子长成植物（画面这一 tick 开始放）。
    pub fn seed_plant(&mut self, kind: Kind, pos: (f64, f64), tick: usize) {
        if self.leona {
            self.plants.push(Shown { kind, pos, born: tick, data: false, big: false, next: None });
        }
    }

    /// Q、E 出手的标记：数据在落点长植物，等它的区域出现。
    pub fn landing(&mut self, kind: Kind, land: (f64, f64), tick: usize) {
        if self.leona {
            self.landings.push(Landing { kind, land, mark: tick });
        }
    }

    pub fn tick(&mut self, sim: &mut StableSim<'_>, me: usize, p: &Params) {
        if !self.look(sim, me) {
            return;
        }
        let tick = sim.tick();
        self.plants.retain(|pl| tick < pl.born + LIFE);
        self.landings.retain(|l| tick <= l.mark + PENDING_T);
        self.r_zones.retain(|z| z.1 >= tick);
        // ---- projectiles: her plants' zones (only while a landing waits), Leona's blade and sunlight zones
        let leonas: Vec<(usize, (f64, f64))> = (0..sim.champion_count())
            .map(|i| sim.champion_id_at(i))
            .filter_map(|id| sim.get_entity(id).filter(|e| e.name().as_deref() == Some(LEONA)).map(|e| (id, fpos(e.pos()))))
            .collect();
        let (mut mine, mut hers) = (Vec::new(), Vec::new());
        for i in 0..sim.projectile_count() {
            let Some(pr) = sim.projectile_at(i) else { continue };
            if pr.is_end {
                continue;
            }
            if pr.caster_id == me && !self.landings.is_empty() {
                mine.push((pr.x, pr.y));
            } else if leonas.iter().any(|l| l.0 == pr.caster_id) {
                hers.push((pr.x, pr.y));
            }
        }
        for &s in mine.iter().filter(|s| self.mine.contains(s)) {
            let spot = fpos(s);
            if self.plants.iter().any(|pl| pl.data && dist(pl.pos, spot) < 100.0) {
                continue;
            }
            let born = tick - 1;
            if let Some(i) = self.landings.iter().position(|l| is_landing(p, l.kind, l.land, l.mark, spot, born)) {
                let l = self.landings.remove(i);
                self.plants.push(Shown { kind: l.kind, pos: spot, born, data: true, big: false, next: None });
            }
        }
        self.mine = mine;
        let mut hits: Vec<(usize, String)> = Vec::new();
        let open: Vec<usize> = (0..self.plants.len())
            .filter(|&i| !self.plants[i].big && tick < self.plants[i].born + END_AT)
            .collect();
        let near = |plants: &[Shown], c: (f64, f64), r: f64| -> Vec<usize> {
            open.iter().copied().filter(|&i| dist(plants[i].pos, c) <= r).collect()
        };
        // what appeared last tick: still on its spot = her R's sunlight zone (its stun core stands on the same spot), gone on
        // = her E's blade flying past that spot
        let (zones, blades) = split_fresh(&self.fresh, &hers);
        for c in zones.into_iter().map(fpos) {
            if !self.r_zones.iter().any(|z| dist(z.0, c) < 2_000.0) {
                self.r_zones.push((c, tick - 1 + R_AT));
            }
        }
        for c in blades.into_iter().map(fpos) {
            hits.extend(near(&self.plants, c, LINE_HIT).into_iter().map(|i| (i, "her E's blade".to_string())));
        }
        self.fresh = hers.iter().copied().filter(|s| !self.hers.contains(s)).collect();
        self.hers = hers;
        for z in self.r_zones.iter().filter(|z| z.1 == tick) {
            hits.extend(near(&self.plants, z.0, R_HIT).into_iter().map(|i| (i, "her R's sunlight".to_string())));
        }
        // ---- W: a new eclipse_hold on her is the burst round her
        let mut holds = Vec::new();
        for &(id, pos) in &leonas {
            let n = count(sim, id, ECLIPSE_HOLD);
            if n > self.holds.iter().find(|h| h.0 == id).map_or(n, |h| h.1) {
                hits.extend(near(&self.plants, pos, W_HIT).into_iter().map(|i| (i, "her W's burst".to_string())));
            }
            holds.push((id, n));
        }
        self.holds = holds;
        // ---- a unit her sunlight just hit, standing on a plant
        let mut sunlit = Vec::new();
        if !open.is_empty() {
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if !e.is_alive() {
                    continue;
                }
                let pos = fpos(e.pos());
                if !open.iter().any(|&k| dist(self.plants[k].pos, pos) <= WATCH_R) {
                    continue;
                }
                let id = e.id();
                let n = (0..e.buff_count()).filter_map(|j| e.buff_at(j)).filter(|b| b.name() == SUNLIGHT).count();
                let before = self.sunlit.iter().find(|s| s.0 == id).map(|s| s.1);
                if before.is_some_and(|b| n > b) {
                    hits.extend(near(&self.plants, pos, UNIT_HIT).into_iter().map(|k| (k, format!("her sunlight on #{id}"))));
                }
                sunlit.push((id, n));
            }
        }
        self.sunlit = sunlit;
        // ---- one size bigger
        for (i, how) in hits {
            let pl = &mut self.plants[i];
            if pl.big {
                continue;
            }
            let age = tick - pl.born;
            let Some((start, seg)) = plan(age) else { continue };
            let from = pl.born + start;
            pl.big = true;
            pl.next = Some((from, seg));
            let (kind, pos, data) = (pl.kind, pl.pos, pl.data);
            sim.play_view_effect(&zy("sun_pop"), me, &at(pos), 0, 0, 0);
            self.n_sun += 1;
            if let Some(k) = tally(sim, "sun") {
                wlog(format!("{} SUN #{}: {how} landed on a {kind:?} ({}) at ({:.0}, {:.0}), {age} ticks old: one size bigger from \
                              tick {from} #{k}", head(sim, me), self.n_sun, if data { "Q/E's" } else { "a seed's" }, pos.0, pos.1));
            }
        }
        // ---- the big plants' segments, in step with the small ones
        for pl in self.plants.iter_mut() {
            while let Some((t, seg)) = pl.next {
                if t > tick {
                    break;
                }
                sim.play_view_effect(&zy(&seg_view(pl.kind, seg)), me, &at(pl.pos), 0, 0, 0);
                pl.next = follow(t - pl.born, seg).map(|(a, s)| (pl.born + a, s));
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_timeline_is_the_plant_picture_s() {
        // league_zyra_big's t_plant and v_plant: 4 growing frames, 4 x 5 sway frames, 6 shake / wither frames, 5 s
        let fanim = include_str!("../../../league/effects/league_zyra_big#anim.fanim");
        for tag in ["t_plant", "v_plant"] {
            let at = fanim.find(&format!("\"{tag}\"")).unwrap();
            let body = &fanim[at..];
            let body = &body[..body.find("]}").unwrap()];
            let ms: Vec<f64> = body
                .split("\"duration\":")
                .skip(1)
                .map(|s| s[..s.find(',').unwrap()].trim().parse::<f64>().unwrap() * 60.0)
                .collect();
            assert_eq!(ms.len(), 30, "{tag}");
            let sum = |a: usize, b: usize| ms[a..b].iter().sum::<f64>();
            assert_eq!(sum(0, 4).round() as usize, GROW_T, "{tag} grows");
            for c in 0..CYCLES {
                let s = 4 + 5 * c;
                assert_eq!(sum(s, s + 5).round() as usize, CYCLE, "{tag} cycle {c}");
                for (j, &f) in FRAME_AT.iter().enumerate() {
                    assert!((sum(s, s + j) - f as f64).abs() < 1.0, "{tag} frame {j} of cycle {c} at {}", sum(s, s + j));
                }
            }
            assert_eq!(sum(0, 24).round() as usize, END_AT, "{tag} withers");
            assert_eq!(sum(0, 30).round() as usize, LIFE, "{tag} lives");
        }
    }

    #[test]
    fn the_big_plant_starts_at_the_next_frame_and_keeps_step() {
        // growing: from the first cycle
        assert_eq!(plan(0), Some((GROW_T, Seg::From(0))));
        assert_eq!(plan(GROW_T - 1), Some((GROW_T, Seg::From(0))));
        // on a cycle's start: at once
        assert_eq!(plan(GROW_T), Some((GROW_T, Seg::From(0))));
        assert_eq!(plan(GROW_T + CYCLE), Some((GROW_T + CYCLE, Seg::From(0))));
        // inside a cycle: its next frame
        assert_eq!(plan(GROW_T + 1), Some((GROW_T + 13, Seg::From(1))));
        assert_eq!(plan(GROW_T + 13), Some((GROW_T + 13, Seg::From(1))));
        assert_eq!(plan(GROW_T + 40), Some((GROW_T + 51, Seg::From(4))));
        // after the last frame's start: the next cycle, or the wither after the fourth
        assert_eq!(plan(GROW_T + 55), Some((GROW_T + CYCLE, Seg::From(0))));
        assert_eq!(plan(END_AT - 2), Some((END_AT, Seg::End)));
        // withering already: too late
        assert_eq!(plan(END_AT), None);
        assert_eq!(plan(LIFE), None);
        // after any segment, whole cycles at the cycles' starts, then the wither, then nothing
        let mut at = plan(GROW_T + 20);
        let mut seen = Vec::new();
        while let Some((a, s)) = at {
            seen.push((a, s));
            at = follow(a, s);
        }
        assert_eq!(seen, vec![(GROW_T + 26, Seg::From(2)), (GROW_T + CYCLE, Seg::From(0)), (GROW_T + 2 * CYCLE, Seg::From(0)),
                              (GROW_T + 3 * CYCLE, Seg::From(0)), (END_AT, Seg::End)]);
        assert_eq!(follow(GROW_T, Seg::From(0)), Some((GROW_T + CYCLE, Seg::From(0))));
    }

    #[test]
    fn every_segment_has_its_picture() {
        let fanim = include_str!("../effects/league_zyra_sun#anim.fanim");
        let copy = include_str!("../override/league_zyra.data_champion");
        for kind in [Kind::Spitter, Kind::Lasher] {
            for seg in [Seg::From(0), Seg::From(1), Seg::From(2), Seg::From(3), Seg::From(4), Seg::End] {
                let v = seg_view(kind, seg);
                assert!(fanim.contains(&format!("\"{v}\"")), "no tag {v}");
                assert!(copy.contains(&format!("\"name\": \"{}\"", zy(&v))), "the copy binds no {v}");
                assert!(zy(&v).len() <= BUFF_NAME_CAP);
            }
        }
        assert!(fanim.contains("\"sun_pop\"") && copy.contains("\"name\": \"league_zyra_sun_pop\""));
        // the big cycle lasts the small one's (plus the 2-tick overlap)
        let at = fanim.find("\"t_big0\"").unwrap();
        let body = &fanim[at..];
        let body = &body[..body.find("]}").unwrap()];
        let ticks: f64 = body.split("\"duration\":").skip(1).map(|s| s[..s.find(',').unwrap()].parse::<f64>().unwrap() * 60.0).sum();
        assert_eq!(ticks.round() as usize, CYCLE + 2);
    }

    #[test]
    fn a_data_plant_is_told_by_its_landing_time() {
        let p = Params::default();
        let land = (100_000.0, 50_000.0);
        let spot = (101_000.0, 50_500.0);
        // Q's spines lobbed q_delay ticks, or q_fast after E's root; E's vines' lasher e_grow ticks
        assert!(is_landing(&p, Kind::Spitter, land, 1000, spot, 1000 + p.q_delay));
        assert!(is_landing(&p, Kind::Spitter, land, 1000, spot, 1000 + p.q_fast + 1));
        assert!(is_landing(&p, Kind::Lasher, land, 1000, spot, 1000 + p.e_grow - 2));
        // E's lasher is not taken for Q's spitter and the other way round
        assert!(!is_landing(&p, Kind::Spitter, land, 1000, spot, 1000 + p.e_grow));
        assert!(!is_landing(&p, Kind::Lasher, land, 1000, spot, 1000 + p.q_delay));
        // too far, or before the mark
        assert!(!is_landing(&p, Kind::Spitter, land, 1000, (120_000.0, 50_000.0), 1000 + p.q_delay));
        assert!(!is_landing(&p, Kind::Lasher, land, 1000, spot, 990));
    }

    #[test]
    fn her_zones_stand_still_and_her_blade_flies_on() {
        // last tick: her R's zone and core on one spot, her E's blade and its champion twin side by side
        let fresh = [(500_000, 400_000), (300_000, 300_000), (300_000, 301_000)];
        // this tick: the zone and core where they were, the blades 6000 on
        let now = [(500_000, 400_000), (500_000, 400_000), (306_000, 300_000), (306_000, 301_000)];
        let (zones, blades) = split_fresh(&fresh, &now);
        assert_eq!(zones, vec![(500_000, 400_000)]);
        assert_eq!(blades, vec![(300_000, 300_000), (300_000, 301_000)]);
        assert_eq!(split_fresh(&[], &now), (vec![], vec![]));
    }

    #[test]
    fn the_reaches_cover_leona_s_skills() {
        // her E's blade (radius 7000) on the plant's body, her R's sunlight (36000) and W's burst (35000) round it
        assert!(LINE_HIT >= 7_000.0 + BODY && R_HIT >= 36_000.0 && W_HIT >= 35_000.0);
        assert!(WATCH_R > UNIT_HIT * 5.0, "a unit's sunlight is counted well before it reaches a plant");
        // R: delay 60, apply 38 -> the sunlight lands 37 ticks after the zone appears
        assert_eq!(R_AT, 38 - 1);
    }
}
