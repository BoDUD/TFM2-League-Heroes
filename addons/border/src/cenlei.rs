//! 岑垒（`border_cenlei`）数据做不到的部分。数据：tools/kit/build_cenlei.py（参数表 P；`passive` 是这里的
//! `border_cenlei:pressure`，参数从数据的 params 读）。
//!
//! - **背压**（被动）：接肩贴在队友身上的盾板（`border_cenlei_ward`，受到的伤害降低 e_share%）每让队友少挨一下，少挨的
//!   那部分岑垒替他挨：队友这一拍掉了 d，原来该掉 d / (1 - s)，岑垒挨 d x s / (1 - s)（真实伤害，扣到剩 1 点为止，不会
//!   因此倒下），挨多少攒多少背压，最多他最大生命的 p_cap%。盾板转够 e_hits 次就摘掉。转移只在这里按队友的掉血算一次：
//!   岑垒挨的这一下不算到任何人头上，也不会再转给谁（没有递归、没有重复计数）。背压分十层（`border_cenlei_pressure`，
//!   每层护甲、魔抗 +p_res / 10），每多一层他身上聚一下珍珠。
//! - **横楔**（`border_cenlei:wedge`，技能第 3 帧）：身前半边 q_seek 内有正在施法的敌方英雄就朝最近的那个扫，不然朝目标；
//!   扇形里的敌人吃伤害、减速，正在施法的敌方英雄被打断（眩晕）。
//! - **接肩**（`border_cenlei:shoulder`）：挑身边最受威胁的队友贴盾板；没人就自己顶住。
//! - **卸城**（`border_cenlei:release`）：读施法的人身上的背压层数（塞拉斯偷来的没有，按 0），扇形里每个敌人只吃一下：
//!   伤害 + 背压加成、推开、减速；放掉背压，给自己加护盾。
//! - 配音（Codex 的九句普通话试音，common::Chatter）。
//!
//! 日志写在本包的 border.log 里（行首 `cenlei`）。

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_cenlei";
const VERSION: &str = env!("CARGO_PKG_VERSION");
pub const WARD: &str = "border_cenlei_ward";
pub const BRACE: &str = "border_cenlei_brace";
pub const PRESSURE: &str = "border_cenlei_pressure";
const Q_SLOW: &str = "border_cenlei_q_slow";
const R_SLOW: &str = "border_cenlei_r_slow";
const VIEW_WARD: &str = "border_cenlei_e_ward";
const VIEW_PEARL: &str = "border_cenlei_p_pearl";
const VIEW_HIT: &str = "border_cenlei_hit";
const VIEW_A_HIT: &str = "border_cenlei_a_hit";
/// 背压分几层
pub const LEVELS: usize = 10;
/// 挑队友时离他多近的敌方英雄算在威胁他
const THREAT_R: f64 = 32_000.0;

/// tools/kit/build_cenlei.py 的 P 里 border.dll 用的那些（NATIVE），单元测试和生成的 .data_champion 对过。
pub static P: Params = Params::new(&[
    ("e_hits", 2), ("e_reach", 55000), ("e_self", 20), ("e_self_t", 120), ("e_share", 40), ("e_time", 240),
    ("p_cap", 25), ("p_res", 20), ("q_ad", 90), ("q_cos", 570), ("q_dmg", 60), ("q_hp", 4), ("q_r", 45000),
    ("q_seek", 45000), ("q_slow", 35), ("q_slow_t", 90), ("q_stun", 60), ("q_stun_all", 40), ("r_ad", 100),
    ("r_cos", 420), ("r_dmg", 150), ("r_p", 60), ("r_push", 1000), ("r_push_t", 6), ("r_r", 50000), ("r_sh", 50),
    ("r_sh_t", 180), ("r_slow", 30), ("r_slow_t", 90), ("r_stun", 60),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("cenlei [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 规则（单元测试用） =====================

/// 队友这一拍掉了 `drop`（盾板已经减掉 share%）：岑垒替他挨的那部分。
pub fn transfer(drop: usize, share: usize) -> usize {
    let share = share.min(90);
    if share == 0 {
        return 0;
    }
    (drop * share + (100 - share) / 2) / (100 - share)
}

/// 攒了 `stored` 的背压、上限 `cap`：几层。
pub fn levels(stored: f64, cap: f64) -> usize {
    if cap <= 0.0 {
        return 0;
    }
    ((stored / cap * LEVELS as f64 + 1e-9).floor() as usize).min(LEVELS)
}

/// 挑队友的分：身边的敌方英雄一个 2 分，掉的血（比例）最多 3 分，被控着 1 分。至少 1 分才算受威胁。
pub fn threat(enemies_near: usize, hp_ratio: f64, held: bool) -> f64 {
    2.0 * enemies_near as f64 + 3.0 * (1.0 - hp_ratio.clamp(0.0, 1.0)) + if held { 1.0 } else { 0.0 }
}

// ===================== 被动：背压 =====================

#[derive(Clone, Copy, Debug)]
struct Link {
    ally: usize,
    last_hp: usize,
    hits: usize,
}

#[derive(Clone, Default)]
struct Pressure {
    me: usize,
    /// 攒下的背压（生命值）
    stored: f64,
    /// 他身上挂着几层
    shown: usize,
    link: Option<Link>,
    chat: Chatter,
}

impl Pressure {
    fn cap(sim: &StableSim<'_>, me: usize) -> f64 {
        let max = sim.get_entity(me).map_or(0, |e| e.hp().1);
        max as f64 * P.f("p_cap") / 100.0
    }

    fn reset(&mut self, sim: &mut StableSim<'_>) {
        if let Some(l) = self.link.take() {
            sim.entity_remove_buff(l.ally, WARD);
        }
        self.stored = 0.0;
        self.shown = 0;
    }

    /// 盾板：找本队带着盾板的队友，看他这一拍掉了多少，替他挨。
    fn watch(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(team) = team_of(sim, me) else { return };
        if self.link.is_none() {
            let found = live_champions(sim, team, true).into_iter().find(|&a| a != me && has_buff(sim, a, WARD));
            if let Some(ally) = found {
                let last_hp = sim.get_entity(ally).map_or(0, |e| e.hp().0);
                self.link = Some(Link { ally, last_hp, hits: 0 });
                log(sim, format!("WARD #{me} -> ally #{ally} ({last_hp} hp)"));
            }
        }
        let Some(mut l) = self.link else { return };
        if !alive(sim, l.ally) || !has_buff(sim, l.ally, WARD) {
            log(sim, format!("WARD #{me} on #{} ended after {} hits", l.ally, l.hits));
            self.link = None;
            return;
        }
        let now = sim.get_entity(l.ally).map_or(0, |e| e.hp().0);
        if now < l.last_hp {
            let drop = l.last_hp - now;
            let mine = sim.get_entity(me).map_or(0, |e| e.hp().0);
            let take = transfer(drop, P.get("e_share")).min(mine.saturating_sub(1));
            if take > 0 {
                // 真实伤害扣他自己的血：不算到谁头上，不触发谁的转移
                sim.deal_damage_raw(me, me, take, 0, AttackTypeV1::Skill);
                let cap = Self::cap(sim, me);
                self.stored = (self.stored + take as f64).min(cap);
                sim.play_view_effect(VIEW_HIT, me, &InputTargetV1::target(me), 0, 0, 0);
            }
            l.hits += 1;
            log(sim, format!("TRANSFER #{} lost {drop} -> #{me} takes {take} (stored {:.0}), hit {}/{}",
                             l.ally, self.stored, l.hits, P.get("e_hits")));
            if l.hits >= P.get("e_hits") {
                sim.entity_remove_buff(l.ally, WARD);
                self.link = None;
                return;
            }
        }
        l.last_hp = now;
        self.link = Some(l);
    }

    fn sync(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let have = count_buff(sim, me, PRESSURE);
        let cap = Self::cap(sim, me);
        // 卸城放掉了（层数比记的少）：记的跟着少
        if have < self.shown {
            self.stored = cap * have as f64 / LEVELS as f64;
            self.shown = have;
        }
        let want = levels(self.stored, cap);
        if want != self.shown {
            let res = (P.get("p_res") / LEVELS) as i32;
            set_stacks(sim, me, PRESSURE, want, || {
                let mut b = BuffV1::named(PRESSURE);
                b.defence = res;
                b.magic_resistance = res;
                b
            });
            if want > self.shown {
                sim.play_view_effect(VIEW_PEARL, me, &InputTargetV1::target(me), 0, 0, 0);
            }
            self.shown = want;
        }
    }
}

impl StablePassive for Pressure {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        P.configure(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.chat.spawned();
        self.link = None;
        self.stored = 0.0;
        self.shown = 0;
        log(sim, format!("SPAWN #{me}: border.dll's Cen Lei (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.reset(sim);
            return;
        }
        self.chat.tick(sim, ID, player, me);
        self.watch(sim, me);
        self.sync(sim, me);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, _damage: &mut usize) {
        self.chat.attacked(sim, ID, me, target);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, _attacker: usize, damage: usize) {
        self.chat.damaged(sim, ID, me, damage);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.chat.killed(sim, ID, me, victim);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        let me = self.me;
        self.reset(sim);
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

/// 朝哪扫：施法目标的方向；没有目标就朝最近的敌方英雄。
fn aim(sim: &StableSim<'_>, caster: usize, input: &InputTargetV1) -> Option<Pt> {
    let at = pos_of(sim, caster)?;
    let team = team_of(sim, caster)?;
    let to = if input.kind == InputTargetKindV1::Target.code() {
        pos_of(sim, input.target_id)
    } else if input.kind == InputTargetKindV1::Pos.code() {
        Some((input.x as f64, input.y as f64))
    } else {
        None
    };
    let to = to.or_else(|| {
        live_champions(sim, team, false)
            .into_iter()
            .filter_map(|e| pos_of(sim, e))
            .min_by(|a, b| dist(at, *a).total_cmp(&dist(at, *b)))
    })?;
    unit((to.0 - at.0, to.1 - at.1)).or(Some((1.0, 0.0)))
}

fn body(sim: &StableSim<'_>, id: usize) -> f64 {
    sim.get_entity(id).map_or(10_000.0, |e| e.radius().max(1) as f64)
}

struct Wedge;

impl StableEffectType for Wedge {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team), Some(mut dir)) = (pos_of(sim, caster), team_of(sim, caster), aim(sim, caster, &input))
        else {
            return;
        };
        // 优先打断：身前半边 q_seek 内正在施法的敌方英雄，扇形朝最近的那个
        let seek = P.f("q_seek");
        let caster_near = live_champions(sim, team, false)
            .into_iter()
            .filter(|&e| casting(sim, e))
            .filter_map(|e| pos_of(sim, e).map(|p| (e, p)))
            .filter(|&(_, p)| dist(at, p) <= seek && (p.0 - at.0) * dir.0 + (p.1 - at.1) * dir.1 >= 0.0)
            .min_by(|a, b| dist(at, a.1).total_cmp(&dist(at, b.1)));
        if let Some((_, p)) = caster_near {
            dir = unit((p.0 - at.0, p.1 - at.1)).unwrap_or(dir);
        }
        let dmg = amount(sim, caster, P.get("q_dmg"), P.get("q_ad"), 0, P.get("q_hp"));
        let (mut hit, mut broke) = (0, 0);
        for id in all_units(sim) {
            if !hittable_enemy(sim, team, id) {
                continue;
            }
            let Some(p) = pos_of(sim, id) else { continue };
            if !in_cone(at, dir, p, P.f("q_r"), P.f("q_cos"), body(sim, id)) {
                continue;
            }
            // 先看他在不在施法，再打（打了以后动作可能就断了）
            let champ = sim.get_entity(id).is_some_and(|e| e.is_champion());
            let spell = champ && casting(sim, id);
            sim.deal_damage(caster, id, dmg, 0, AttackTypeV1::Skill);
            sim.add_buff(id, &slow_buff(Q_SLOW, P.get("q_slow"), P.get("q_slow_t")));
            if spell && stun(sim, id, P.get("q_stun")) {
                sim.play_view_effect(VIEW_A_HIT, caster, &InputTargetV1::target(id), 0, 0, 0);
                broke += 1;
            } else if champ {
                // 没在施法的英雄也被楔子顶一下（q_stun_all 拍，0 就不顶）
                stun(sim, id, P.get("q_stun_all"));
            }
            hit += 1;
        }
        log(sim, format!("WEDGE #{caster}: {hit} hit for {dmg}, {broke} casts broken{}",
                         if caster_near.is_some() { " (turned to a caster)" } else { "" }));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("q_dmg") + s.attack * P.get("q_ad") / 100 + s.hp * P.get("q_hp") / 100, 0)
    }

    fn expected_cc_time(&self) -> Option<usize> {
        Some(P.get("q_stun"))
    }
}

struct Shoulder;

impl StableEffectType for Shoulder {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, _input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let foes: Vec<Pt> = live_champions(sim, team, false).into_iter().filter_map(|e| pos_of(sim, e)).collect();
        let reach = P.f("e_reach");
        let best = live_champions(sim, team, true)
            .into_iter()
            .filter(|&a| a != caster)
            .filter_map(|a| pos_of(sim, a).map(|p| (a, p)))
            .filter(|&(_, p)| dist(at, p) <= reach)
            .map(|(a, p)| {
                let near = foes.iter().filter(|f| dist(**f, p) <= THREAT_R).count();
                (a, threat(near, hp_ratio(sim, a), controlled(sim, a)))
            })
            .filter(|&(_, s)| s >= 1.0)
            .max_by(|a, b| a.1.total_cmp(&b.1));
        match best {
            Some((ally, score)) => {
                // 换人：先摘掉本队别人身上的旧盾板（一次只护一个）
                for a in live_champions(sim, team, true) {
                    if a != ally {
                        sim.entity_remove_buff(a, WARD);
                    }
                }
                sim.entity_remove_buff(ally, WARD);
                let mut ward = BuffV1::timed(WARD, P.get("e_time"));
                ward.damaged_reduce = P.get("e_share");
                sim.add_buff(ally, &ward);
                sim.play_view_effect(VIEW_WARD, caster, &InputTargetV1::target(ally), 0, 0, 0);
                log(sim, format!("SHOULDER #{caster} -> #{ally} (threat {score:.1})"));
            }
            None => {
                let mut brace = BuffV1::timed(BRACE, P.get("e_self_t"));
                brace.damaged_reduce = P.get("e_self");
                sim.add_buff(caster, &brace);
                sim.play_view_effect(VIEW_WARD, caster, &InputTargetV1::target(caster), 0, 0, 0);
                log(sim, format!("SHOULDER #{caster}: nobody threatened, braces himself"));
            }
        }
    }

    fn expected_shield(&self, s: &StatV1) -> usize {
        s.hp * P.get("e_share") / 100 / 4
    }
}

struct Release;

impl StableEffectType for Release {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team), Some(dir)) = (pos_of(sim, caster), team_of(sim, caster), aim(sim, caster, &input))
        else {
            return;
        };
        let k = count_buff(sim, caster, PRESSURE);
        let max = sim.get_entity(caster).map_or(0, |e| e.hp().1);
        let consumed = max * P.get("p_cap") / 100 * k / LEVELS;
        let dmg = amount(sim, caster, P.get("r_dmg"), P.get("r_ad"), 0, 0) + consumed * P.get("r_p") / 100;
        let mut hit = 0;
        // 三道楔浪是同一下：每个敌人只结算一次
        for id in all_units(sim) {
            if !hittable_enemy(sim, team, id) {
                continue;
            }
            let Some(p) = pos_of(sim, id) else { continue };
            if !in_cone(at, dir, p, P.f("r_r"), P.f("r_cos"), body(sim, id)) {
                continue;
            }
            sim.deal_damage(caster, id, dmg, 0, AttackTypeV1::Skill);
            sim.entity_knockback(caster, id, P.get("r_push"), P.get("r_push_t"));
            sim.add_buff(id, &slow_buff(R_SLOW, P.get("r_slow"), P.get("r_slow_t")));
            // 推出去以后站不稳（r_stun 拍，0 就没有）：眩晕从推开那一拍算起，推开的时间加上 r_stun，落地时还晕着
            // （眩晕不挡强制位移，champion-data 第 4 节 Pull vs Grab）
            if P.get("r_stun") > 0 {
                stun(sim, id, P.get("r_push_t") + P.get("r_stun"));
            }
            hit += 1;
        }
        if k > 0 {
            sim.entity_remove_buff(caster, PRESSURE);
            sim.entity_add_shield(caster, consumed * P.get("r_sh") / 100, P.get("r_sh_t"));
        }
        log(sim, format!("RELEASE #{caster}: {k} levels of pressure ({consumed}), {hit} hit for {dmg}"));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (P.get("r_dmg") + s.attack * P.get("r_ad") / 100, 0)
    }

    fn expected_cc_time(&self) -> Option<usize> {
        Some(P.get("r_push_t"))
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("cenlei: {ID} v{VERSION} (Cen Lei: back pressure, wedge, shoulder, release) registered"));
    module.add_native_passive(format!("{ID}:pressure"), Pressure::default());
    module.add_native_effect(format!("{ID}:wedge"), Wedge);
    module.add_native_effect(format!("{ID}:shoulder"), Shoulder);
    module.add_native_effect(format!("{ID}:release"), Release);
    host.log(LogLevel::Info, "border.dll: Cen Lei (back pressure, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn the_ward_moves_the_part_it_took_off() {
        // 35%：队友掉 65，原来该掉 100，岑垒挨 35
        assert_eq!(transfer(65, 35), 35);
        assert_eq!(transfer(130, 35), 70);
        assert_eq!(transfer(0, 35), 0);
        assert_eq!(transfer(100, 0), 0);
    }

    #[test]
    fn pressure_comes_in_ten_levels() {
        assert_eq!(levels(0.0, 300.0), 0);
        assert_eq!(levels(29.9, 300.0), 0);
        assert_eq!(levels(30.0, 300.0), 1);
        assert_eq!(levels(299.0, 300.0), 9);
        assert_eq!(levels(300.0, 300.0), 10);
        assert_eq!(levels(900.0, 300.0), 10);
        assert_eq!(levels(10.0, 0.0), 0);
    }

    #[test]
    fn threat_needs_an_enemy_or_lost_health() {
        assert!(threat(0, 1.0, false) < 1.0);
        assert!(threat(1, 1.0, false) >= 1.0);
        assert!(threat(0, 0.6, false) >= 1.0);
        assert!(threat(0, 1.0, true) >= 1.0);
        assert!(threat(2, 0.5, false) > threat(1, 0.5, false));
    }
}
