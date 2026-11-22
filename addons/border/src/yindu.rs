//! 殷渡（`border_yindu`）数据做不到的部分。数据：tools/kit/build_yindu.py（参数表 P；`passive` 是这里的
//! `border_yindu:tide`）。
//!
//! - **迎汐**（被动）：每拍量他离 p_reach 内最近的敌方英雄多远，比上一拍近了 200 以上算在推进，推进满 p_step 拍攒一层潮势
//!   （`border_yindu_tide`，最多 p_max 层，满了身上卷起一道潮头）；p_keep 拍没推进就每 p_step 拍退一层。
//! - **扣舷**（`border_yindu:ram` 第 1 拍、`ram_hit` 第 3 帧）：朝目标短冲，路上第一个敌人（宽 q_w 的道上）挡住就停在他面前，
//!   撞谁记在他身上（`border_yindu_q_<id>`）；撞到时眩晕、减速（每层潮势更慢），潮势用掉。
//! - **立标**（`border_yindu:beacon`）：在目标那一群敌方英雄的中点插航标（`border_yindu_beacon_<x>_<y>`，地上立着），落地时
//!   砸一下身边的敌人。
//! - **合汛**（`border_yindu:tide` 第 3 帧、`tide_hit` r_land 拍后）：施法的人身边有自己的航标就在航标合拢，不然在目标脚下；
//!   汇合点写在身上（`border_yindu_r_<x>_<y>`），先放预警的潮墙，结算时圈里的敌人每人只卷一次（强制位移到汇合点）、伤害、
//!   眩晕。塞拉斯偷去的是数据版（目标脚下），不走这里。
//!
//! 日志写在本包的 border.log 里（行首 `yindu`）。

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_yindu";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const TIDE: &str = "border_yindu_tide";
const Q_MARK: &str = "border_yindu_q_";
const BEACON: &str = "border_yindu_beacon_";
const CENTER: &str = "border_yindu_r_";
const Q_SLOW: &str = "border_yindu_q_slow";
const E_SLOW: &str = "border_yindu_e_slow";
const VIEW_HIT: &str = "border_yindu_a_hit";
const VIEW_TIDE: &str = "border_yindu_p_tide";
const VIEW_BUOY: &str = "border_yindu_e_buoy";
const VIEW_BUOY_END: &str = "border_yindu_e_buoy_end";
const VIEW_WALLS: &str = "border_yindu_r_tide";

pub static P: Params = Params::new(&[
    ("e_dmg", 70), ("e_group", 30000), ("e_hp", 4), ("e_r", 25000), ("e_slow", 20), ("e_slow_t", 60), ("e_t", 360),
    ("p_keep", 120), ("p_max", 8), ("p_reach", 90000), ("p_step", 15), ("q_ad", 80), ("q_dmg", 95), ("q_dur", 34),
    ("q_hp", 4), ("q_len", 40000), ("q_slow", 25), ("q_slow_k", 5), ("q_slow_t", 90), ("q_speed", 3500),
    ("q_stun", 26), ("q_w", 12000), ("r_ad", 60), ("r_beacon_r", 90000), ("r_dmg", 190), ("r_hp", 7),
    ("r_land", 12), ("r_pull_t", 8), ("r_r", 38000), ("r_stun", 57),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("yindu [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 规则（单元测试用） =====================

/// 冲的路上第一个挡道的：(id, 位置, 身子) 里，顺着 `u`（单位向量）在 0..len 之间、离道中线不到 w / 2 加半个身子的，最近的那个，
/// 返回 (id, 顺着走多远)。
pub fn first_on_path(from: Pt, u: Pt, len: f64, w: f64, units: &[(usize, Pt, f64)]) -> Option<(usize, f64)> {
    units
        .iter()
        .filter_map(|&(id, p, body)| {
            let v = (p.0 - from.0, p.1 - from.1);
            let along = v.0 * u.0 + v.1 * u.1;
            let across = (-v.0 * u.1 + v.1 * u.0).abs();
            (along > 0.0 && along <= len + body && across <= w / 2.0 + body * 0.5).then_some((id, along))
        })
        .min_by(|a, b| a.1.total_cmp(&b.1))
}

/// 几个点的中点。
pub fn centroid(pts: &[Pt]) -> Option<Pt> {
    if pts.is_empty() {
        return None;
    }
    let n = pts.len() as f64;
    Some((pts.iter().map(|p| p.0).sum::<f64>() / n, pts.iter().map(|p| p.1).sum::<f64>() / n))
}

// ===================== 被动：迎汐 =====================

#[derive(Clone, Default)]
struct Tide {
    me: usize,
    stacks: usize,
    last_gap: Option<f64>,
    pushing: usize,
    idle: usize,
    chat: Chatter,
}

impl Tide {
    fn step(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let (Some(at), Some(team)) = (pos_of(sim, me), team_of(sim, me)) else { return };
        let gap = live_champions(sim, team, false)
            .into_iter()
            .filter_map(|e| pos_of(sim, e))
            .map(|p| dist(at, p))
            .filter(|&d| d <= P.f("p_reach"))
            .fold(f64::INFINITY, f64::min);
        // 扣舷用掉了（层数比记的少）
        let have = count_buff(sim, me, TIDE);
        if have < self.stacks {
            self.stacks = have;
        }
        let advancing = gap.is_finite() && self.last_gap.is_some_and(|g| gap < g - 200.0);
        self.last_gap = gap.is_finite().then_some(gap);
        let step = P.get("p_step").max(1);
        if advancing {
            self.idle = 0;
            self.pushing += 1;
            if self.pushing.is_multiple_of(step) && self.stacks < P.get("p_max") {
                self.stacks += 1;
                if self.stacks == P.get("p_max") {
                    sim.play_view_effect(VIEW_TIDE, me, &InputTargetV1::target(me), 0, 0, 0);
                }
            }
        } else {
            self.idle += 1;
            if self.idle >= P.get("p_keep") && (self.idle - P.get("p_keep")).is_multiple_of(step) && self.stacks > 0 {
                self.stacks -= 1;
            }
        }
        if have != self.stacks {
            set_stacks(sim, me, TIDE, self.stacks, || BuffV1::named(TIDE));
        }
    }
}

impl StablePassive for Tide {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        P.configure(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.chat.spawned();
        self.stacks = 0;
        self.last_gap = None;
        log(sim, format!("SPAWN #{me}: border.dll's Yin Du (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.stacks = 0;
            self.last_gap = None;
            return;
        }
        self.chat.tick(sim, ID, player, me);
        self.step(sim, me);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.chat.attacked(sim, ID, me, target);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _attacker: usize, damage: usize) {
        self.chat.damaged(sim, ID, me, damage);
        self.chat.flinch(sim, ID, me, damage);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.chat.killed(sim, ID, me, victim);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        let me = self.me;
        self.stacks = 0;
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

struct Ram;

impl StableEffectType for Ram {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) || held(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let Some(to) = target_of(&input).and_then(|t| pos_of(sim, t)) else { return };
        let Some(u) = unit((to.0 - at.0, to.1 - at.1)) else { return };
        let units: Vec<(usize, Pt, f64)> = all_units(sim)
            .into_iter()
            .filter(|&id| hittable_enemy(sim, team, id))
            .filter_map(|id| pos_of(sim, id).map(|p| (id, p, body_of(sim, id))))
            .collect();
        let len = P.f("q_len");
        let hit = first_on_path(at, u, len, P.f("q_w"), &units);
        let go = hit.map_or(len, |(_, along)| (along - 14_000.0).max(0.0));
        clear_named(sim, caster, Q_MARK, 1);
        if let Some((h, _)) = hit {
            sim.add_buff(caster, &BuffV1::timed(&format!("{Q_MARK}{h}"), 24));
        }
        let ticks = force_move(sim, caster, at, (at.0 + u.0 * go, at.1 + u.1 * go), P.f("q_speed"), 12);
        if ticks > 0 {
            hold_pose(sim, caster, "skill", P.get("q_dur").saturating_sub(2));
        }
        log(sim, format!("RAM #{caster} {go:.0}{}", hit.map_or(String::new(), |(h, _)| format!(", blocked by #{h}"))));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("q_dmg") + s.attack * P.get("q_ad") / 100 + s.hp * P.get("q_hp") / 100, 0)
    }

    fn expected_cc_time(&self) -> Option<usize> {
        Some(P.get("q_stun"))
    }
}

struct RamHit;

impl StableEffectType for RamHit {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let near = |id: usize| hittable_enemy(sim, team, id) && pos_of(sim, id).is_some_and(|p| dist(at, p) <= 30_000.0);
        let marked = named(sim, caster, Q_MARK, 1).last().map(|(_, v)| v[0] as usize);
        let t = marked.filter(|&m| near(m)).or_else(|| {
            all_units(sim).into_iter().filter(|&u| near(u)).min_by(|a, b| {
                let (pa, pb) = (pos_of(sim, *a).unwrap_or(at), pos_of(sim, *b).unwrap_or(at));
                dist(at, pa).total_cmp(&dist(at, pb))
            })
        });
        clear_named(sim, caster, Q_MARK, 1);
        let Some(t) = t else { return };
        let k = count_buff(sim, caster, TIDE);
        let dmg = amount(sim, caster, P.get("q_dmg"), P.get("q_ad"), 0, P.get("q_hp"));
        sim.deal_damage(caster, t, dmg, 0, AttackTypeV1::Skill);
        stun(sim, t, P.get("q_stun"));
        sim.add_buff(t, &slow_buff(Q_SLOW, P.get("q_slow") + k * P.get("q_slow_k"), P.get("q_slow_t")));
        sim.entity_remove_buff(caster, TIDE);
        sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(t), 0, 0, 0);
        log(sim, format!("RAM HIT #{caster} -> #{t}: {dmg}, tide {k}"));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("q_dmg") + s.attack * P.get("q_ad") / 100 + s.hp * P.get("q_hp") / 100, 0)
    }
}

struct Beacon;

impl StableEffectType for Beacon {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(team) = team_of(sim, caster) else { return };
        let Some(t_at) = target_of(&input).and_then(|t| pos_of(sim, t)) else { return };
        let group: Vec<Pt> = live_champions(sim, team, false)
            .into_iter()
            .filter_map(|e| pos_of(sim, e))
            .filter(|&p| dist(t_at, p) <= P.f("e_group"))
            .collect();
        let at = centroid(&group).unwrap_or(t_at);
        clear_named(sim, caster, BEACON, 2);
        sim.add_buff(caster, &BuffV1::timed(&pt_name(BEACON, at), P.get("e_t")));
        sim.play_view_effect(VIEW_BUOY, caster, &InputTargetV1::pos(at.0 as u64, at.1 as u64), 0, 0, 0);
        let dmg = amount(sim, caster, P.get("e_dmg"), 0, 0, P.get("e_hp"));
        let hit = enemies_near(sim, team, at, P.f("e_r"));
        for &id in &hit {
            sim.deal_damage(caster, id, dmg, 0, AttackTypeV1::Skill);
            sim.add_buff(id, &slow_buff(E_SLOW, P.get("e_slow"), P.get("e_slow_t")));
        }
        log(sim, format!("BEACON #{caster} at ({:.0}, {:.0}) amid {} champions, {} hit", at.0, at.1, group.len(), hit.len()));
    }
}

struct TideCall;

impl StableEffectType for TideCall {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(at) = pos_of(sim, caster) else { return };
        let beacon = named(sim, caster, BEACON, 2)
            .last()
            .map(|(n, v)| (n.clone(), (v[0] as f64, v[1] as f64)))
            .filter(|(_, p)| dist(at, *p) <= P.f("r_beacon_r"));
        let Some(center) = beacon.as_ref().map(|b| b.1).or_else(|| target_of(&input).and_then(|t| pos_of(sim, t)))
        else {
            return;
        };
        if let Some((name, p)) = &beacon {
            sim.entity_remove_buff(caster, name);
            sim.play_view_effect(VIEW_BUOY_END, caster, &InputTargetV1::pos(p.0 as u64, p.1 as u64), 0, 0, 0);
        }
        clear_named(sim, caster, CENTER, 2);
        sim.add_buff(caster, &BuffV1::timed(&pt_name(CENTER, center), P.get("r_land") + 10));
        sim.play_view_effect(VIEW_WALLS, caster, &InputTargetV1::pos(center.0 as u64, center.1 as u64), 0, 0, 0);
        log(sim, format!("TIDE #{caster} closes on ({:.0}, {:.0}){}", center.0, center.1,
                         if beacon.is_some() { " (the beacon)" } else { "" }));
    }
}

struct TideHit;

impl StableEffectType for TideHit {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(team) = team_of(sim, caster) else { return };
        let Some(center) = named(sim, caster, CENTER, 2).last().map(|(_, v)| (v[0] as f64, v[1] as f64)) else { return };
        clear_named(sim, caster, CENTER, 2);
        let dmg = amount(sim, caster, P.get("r_dmg"), P.get("r_ad"), 0, P.get("r_hp"));
        let pull_t = P.get("r_pull_t").max(1);
        let hit = enemies_near(sim, team, center, P.f("r_r"));
        // 每人只卷一次：这一遍就是全部
        for &id in &hit {
            if let Some(p) = pos_of(sim, id) {
                if !cc_immune(sim, id) {
                    let d = dist(p, center);
                    if d > 5_000.0 {
                        let u = unit((center.0 - p.0, center.1 - p.1)).unwrap_or((0.0, 0.0));
                        let go = d - 4_000.0;
                        force_move(sim, id, p, (p.0 + u.0 * go, p.1 + u.1 * go), go / pull_t as f64, pull_t);
                    }
                }
            }
            sim.deal_damage(caster, id, dmg, 0, AttackTypeV1::Skill);
            stun(sim, id, pull_t + P.get("r_stun"));
        }
        log(sim, format!("TIDE HIT #{caster}: {} swept in for {dmg}", hit.len()));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("r_dmg") + s.attack * P.get("r_ad") / 100 + s.hp * P.get("r_hp") / 100, 0)
    }

    fn expected_cc_time(&self) -> Option<usize> {
        Some(P.get("r_stun"))
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("yindu: {ID} v{VERSION} (Yin Du: tide momentum, ram, beacon, converging tide) registered"));
    module.add_native_passive(format!("{ID}:tide"), Tide::default());
    module.add_native_effect(format!("{ID}:ram"), Ram);
    module.add_native_effect(format!("{ID}:ram_hit"), RamHit);
    module.add_native_effect(format!("{ID}:beacon"), Beacon);
    module.add_native_effect(format!("{ID}:tide"), TideCall);
    module.add_native_effect(format!("{ID}:tide_hit"), TideHit);
    host.log(LogLevel::Info, "border.dll: Yin Du (tide momentum, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn the_ram_stops_at_the_first_one_on_the_way() {
        let units = [(1, (30_000.0, 0.0), 10_000.0), (2, (15_000.0, 4_000.0), 10_000.0), (3, (10_000.0, 30_000.0), 10_000.0),
                     (4, (-5_000.0, 0.0), 10_000.0)];
        // 2 在道上、比 1 近；3 离道太远；4 在身后
        assert_eq!(first_on_path((0.0, 0.0), (1.0, 0.0), 40_000.0, 12_000.0, &units).map(|x| x.0), Some(2));
        assert_eq!(first_on_path((0.0, 0.0), (1.0, 0.0), 40_000.0, 12_000.0, &units[2..]), None);
    }

    #[test]
    fn the_beacon_sits_amid_the_group() {
        assert_eq!(centroid(&[(0.0, 0.0), (10.0, 20.0)]), Some((5.0, 10.0)));
        assert_eq!(centroid(&[]), None);
    }
}
