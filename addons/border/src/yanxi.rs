//! 盐汐（`border_yanxi`）数据做不到的部分。数据：tools/kit/build_yanxi.py（参数表 P；`passive` 是这里的
//! `border_yanxi:salt`）。
//!
//! - **盐带**：撒线（`border_yanxi:line`，第 3 帧）以目标为中点、沿她到目标的方向铺一条长 q_len、宽 q_w 的带子，位置写进她
//!   身上的 buff 名字（`border_yanxi_band_<中点 x>_<中点 y>_<方向 x>_<方向 y>`，方向乘 1000 再加 1000，q_t 拍）；一次只有一条。
//!   画面是一个几乎不动的原生投射物（`border_yanxi_q_band_r`，往左铺时换上下翻过的 `_l`：引擎把弹道画面转到它走的方向，
//!   朝左转半圈就倒过来了），带上的敌人当场吃魔法伤害、叠一层结晶。
//! - **析晶**（被动）：还站在她盐带里的敌人减速 p_slow%，每待 p_tick 拍叠一层结晶（`border_yanxi_crystal`，最多 p_max 层，
//!   离开后留 p_keep 拍），叠到三层身上亮一簇盐晶。
//! - **凝结**（`border_yanxi:congeal`）：e_reach 内带结晶的敌人全引爆、清掉结晶，结算完只给层数最高的敌方英雄定身。
//! - **退潮**（`border_yanxi:ebb`，大招第 3 帧）：施法的人身上的盐带（没有就先穿过目标铺一条）从远端朝他扫
//!   回来：一道晶浪（原生投射物，直线、穿透，`border_yanxi_r_wave_r` / 朝左走时 `_l`），扫到的敌人（`ebb_hit`）吃魔法伤害、
//!   叠结晶、被往他那边带；盐带收回（buff 摘掉）。塞拉斯偷去的是数据版（目标脚下掀起晶浪扫回他身边），不走这里。
//!
//! 日志写在本包的 border.log 里（行首 `yanxi`）。

use std::collections::HashMap;

use mod_api_stable::*;

use crate::common::*;

pub const ID: &str = "border_yanxi";
const VERSION: &str = env!("CARGO_PKG_VERSION");
const BAND: &str = "border_yanxi_band_";
pub const CRYSTAL: &str = "border_yanxi_crystal";
const SLOW: &str = "border_yanxi_p_slow";
const BAND_R: &str = "border_yanxi_q_band_r";
const BAND_L: &str = "border_yanxi_q_band_l";
const WAVE_R: &str = "border_yanxi_r_wave_r";
const WAVE_L: &str = "border_yanxi_r_wave_l";
const VIEW_HIT: &str = "border_yanxi_a_hit";
const VIEW_BURST: &str = "border_yanxi_e_burst";
const VIEW_CRYSTAL: &str = "border_yanxi_p_crystal";
/// 盐带的画面一拍挪多少（几乎不动；直线弹道要有个方向）
const BAND_DRIFT: f64 = 20.0;

pub static P: Params = Params::new(&[
    ("e_ap", 40), ("e_dmg", 70), ("e_kap", 15), ("e_kdmg", 25), ("e_reach", 90000), ("e_root", 60),
    ("p_keep", 240), ("p_max", 5), ("p_slow", 25), ("p_tick", 45), ("q_ap", 60), ("q_dmg", 80), ("q_len", 50000),
    ("q_t", 240), ("q_w", 14000), ("r_ap", 90), ("r_dmg", 220), ("r_pull", 15000), ("r_pull_t", 10),
    ("r_speed", 3000), ("r_stack", 2), ("r_w", 16000),
]);

static LOGS: Counter = Counter::new();

fn log(sim: &StableSim<'_>, msg: String) {
    if let Some(n) = LOGS.next() {
        crate::wlog(format!("yanxi [t={}] #{n} {msg}", sim.tick()));
    }
}

// ===================== 盐带（单元测试用） =====================

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Band {
    pub center: Pt,
    /// 单位向量：她铺的方向
    pub dir: Pt,
}

impl Band {
    pub fn name(&self) -> String {
        let enc = |v: f64| ((v.clamp(-1.0, 1.0) * 1000.0).round() as i64 + 1000) as u64;
        format!("{BAND}{}_{}_{}_{}", self.center.0.max(0.0).round() as u64, self.center.1.max(0.0).round() as u64,
                enc(self.dir.0), enc(self.dir.1))
    }

    pub fn parse(name: &str) -> Option<Band> {
        let rest = name.strip_prefix(BAND)?;
        let v: Vec<f64> = rest.split('_').map(|s| s.parse::<u64>().ok().map(|x| x as f64)).collect::<Option<_>>()?;
        if v.len() != 4 {
            return None;
        }
        let dir = unit(((v[2] - 1000.0) / 1000.0, (v[3] - 1000.0) / 1000.0))?;
        Some(Band { center: (v[0], v[1]), dir })
    }

    /// `p`（身子半径 `body`）在不在长 `len`、宽 `w` 的带子上。
    pub fn holds(&self, p: Pt, len: f64, w: f64, body: f64) -> bool {
        let v = (p.0 - self.center.0, p.1 - self.center.1);
        let along = v.0 * self.dir.0 + v.1 * self.dir.1;
        let across = -v.0 * self.dir.1 + v.1 * self.dir.0;
        along.abs() <= len / 2.0 + body * 0.5 && across.abs() <= w / 2.0 + body * 0.5
    }

    /// 离她远的那一头。
    pub fn far_end(&self, len: f64) -> Pt {
        (self.center.0 + self.dir.0 * len / 2.0, self.center.1 + self.dir.1 * len / 2.0)
    }
}

/// 朝左走的弹道画面要换上下翻过的那张。
pub fn leftward(dir: Pt) -> bool {
    dir.0 < -1e-6
}

/// 凝结：谁定身。`hits` 是 (id, 层数, 生命比例, 是不是英雄)，挑层数最多的英雄，一样多挑生命比例低的。
pub fn root_pick(hits: &[(usize, usize, f64, bool)]) -> Option<usize> {
    hits.iter()
        .filter(|h| h.3 && h.1 > 0)
        .max_by(|a, b| a.1.cmp(&b.1).then(b.2.total_cmp(&a.2)))
        .map(|h| h.0)
}

fn bands_of(sim: &StableSim<'_>, id: usize) -> Vec<(String, Band)> {
    buffs_of(sim, id).iter().filter_map(|b| Band::parse(b.name()).map(|x| (b.name().to_string(), x))).collect()
}

fn clear_bands(sim: &mut StableSim<'_>, id: usize) {
    for (n, _) in bands_of(sim, id) {
        sim.entity_remove_buff(id, &n);
    }
}

fn add_crystal(sim: &mut StableSim<'_>, caster: usize, id: usize, n: usize) -> usize {
    let mut k = 0;
    for _ in 0..n {
        k = sim.entity_stack_buff(id, &BuffV1::timed(CRYSTAL, P.get("p_keep")), P.get("p_max"), true);
    }
    if k >= 3 && n > 0 {
        sim.play_view_effect(VIEW_CRYSTAL, caster, &InputTargetV1::target(id), 0, 0, 0);
    }
    k
}

fn body(sim: &StableSim<'_>, id: usize) -> f64 {
    sim.get_entity(id).map_or(10_000.0, |e| e.radius().max(1) as f64)
}

/// 一个几乎不动、什么都不打的弹道当画面（往 `dir` 慢慢挪，活 `ticks` 拍）。
fn picture(sim: &mut StableSim<'_>, caster: usize, name: &str, at: Pt, dir: Pt, ticks: usize) -> bool {
    let Some(team) = team_of(sim, caster) else { return false };
    let to = (at.0 + dir.0 * BAND_DRIFT * ticks as f64, at.1 + dir.1 * BAND_DRIFT * ticks as f64);
    let spec = ProjectileSpawnV1 {
        caster_id: caster,
        team,
        x: at.0.max(0.0) as u64,
        y: at.1.max(0.0) as u64,
        radius: 1,
        speed: BAND_DRIFT as u64,
        move_kind: ProjectileMoveKindV1::Linear.code(),
        target_id: 0,
        target_x: to.0.max(0.0) as u64,
        target_y: to.1.max(0.0) as u64,
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: CastingTypeV1::Targeting.code(),
        casting_target: CastingTargetV1::None.code(),
    };
    sim.spawn_projectile(name, &format!("{ID}:noop"), &spec)
}

// ===================== 被动：析晶 =====================

#[derive(Clone, Default)]
struct Salt {
    me: usize,
    /// 每个敌人在盐带里待了几拍
    inside: HashMap<usize, usize>,
    chat: Chatter,
}

impl Salt {
    fn step(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let bands = bands_of(sim, me);
        if bands.is_empty() {
            self.inside.clear();
            return;
        }
        let Some(team) = team_of(sim, me) else { return };
        let (len, w) = (P.f("q_len"), P.f("q_w"));
        let mut still = Vec::new();
        for id in all_units(sim) {
            if !hittable_enemy(sim, team, id) {
                continue;
            }
            let Some(p) = pos_of(sim, id) else { continue };
            let b = body(sim, id);
            if !bands.iter().any(|(_, band)| band.holds(p, len, w, b)) {
                continue;
            }
            still.push(id);
            let mut slow = slow_buff(SLOW, P.get("p_slow"), 10);
            slow.duration_tick = 10;
            sim.entity_stack_buff(id, &slow, 1, true);
            let n = self.inside.entry(id).or_insert(0);
            *n += 1;
            if n.is_multiple_of(P.get("p_tick").max(1)) {
                let k = add_crystal(sim, me, id, 1);
                if k <= 2 {
                    log(sim, format!("CRYSTAL #{id} {k}"));
                }
            }
        }
        self.inside.retain(|id, _| still.contains(id));
    }
}

impl StablePassive for Salt {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        P.configure(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        self.chat.spawned();
        self.inside.clear();
        log(sim, format!("SPAWN #{me}: border.dll's Yan Xi (player {player})"));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, me: usize) {
        self.me = me;
        if !self.chat.alive_now(sim, me) {
            self.inside.clear();
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
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, victim: usize) {
        self.chat.killed(sim, ID, me, victim);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        let me = self.me;
        self.inside.clear();
        self.chat.died(sim, ID, me);
    }
}

// ===================== 原生效果 =====================

fn aim_point(sim: &StableSim<'_>, input: &InputTargetV1) -> Option<Pt> {
    if input.kind == InputTargetKindV1::Target.code() {
        pos_of(sim, input.target_id)
    } else if input.kind == InputTargetKindV1::Pos.code() {
        Some((input.x as f64, input.y as f64))
    } else {
        None
    }
}

/// 以目标为中点、沿施法的人到目标的方向的一条带子。
fn band_through(sim: &StableSim<'_>, caster: usize, input: &InputTargetV1) -> Option<Band> {
    let at = pos_of(sim, caster)?;
    let to = aim_point(sim, input)?;
    let dir = unit((to.0 - at.0, to.1 - at.1)).unwrap_or((1.0, 0.0));
    Some(Band { center: to, dir })
}

struct Line;

impl StableEffectType for Line {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let Some(team) = team_of(sim, caster) else { return };
        let Some(band) = band_through(sim, caster, &input) else { return };
        clear_bands(sim, caster);
        sim.add_buff(caster, &BuffV1::timed(&band.name(), P.get("q_t")));
        let pic = if leftward(band.dir) { BAND_L } else { BAND_R };
        let shown = picture(sim, caster, pic, band.center, band.dir, P.get("q_t"));
        let dmg = amount(sim, caster, P.get("q_dmg"), 0, P.get("q_ap"), 0);
        let (len, w) = (P.f("q_len"), P.f("q_w"));
        let mut hit = 0;
        for id in all_units(sim) {
            if !hittable_enemy(sim, team, id) {
                continue;
            }
            if pos_of(sim, id).is_some_and(|p| band.holds(p, len, w, body(sim, id))) {
                sim.deal_damage(caster, id, 0, dmg, AttackTypeV1::Skill);
                add_crystal(sim, caster, id, 1);
                hit += 1;
            }
        }
        log(sim, format!("LINE #{caster} at ({:.0}, {:.0}) dir ({:.2}, {:.2}): {hit} hit for {dmg}{}",
                         band.center.0, band.center.1, band.dir.0, band.dir.1,
                         if shown { "" } else { " (picture refused)" }));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (0, P.get("q_dmg") + s.magic_power * P.get("q_ap") / 100)
    }
}

struct Congeal;

impl StableEffectType for Congeal {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let mut hits = Vec::new();
        for id in all_units(sim) {
            if !hittable_enemy(sim, team, id) {
                continue;
            }
            let k = count_buff(sim, id, CRYSTAL);
            if k == 0 || !pos_of(sim, id).is_some_and(|p| dist(at, p) <= P.f("e_reach")) {
                continue;
            }
            let dmg = amount(sim, caster, P.get("e_dmg") + k * P.get("e_kdmg"), 0, P.get("e_ap") + k * P.get("e_kap"), 0);
            let champ = sim.get_entity(id).is_some_and(|e| e.is_champion());
            sim.entity_remove_buff(id, CRYSTAL);
            sim.deal_damage(caster, id, 0, dmg, AttackTypeV1::Skill);
            sim.play_view_effect(VIEW_BURST, caster, &InputTargetV1::target(id), 0, 0, 0);
            hits.push((id, k, hp_ratio(sim, id), champ));
        }
        if hits.is_empty() {
            // 谁都没有结晶：只打目标，不定身
            if let Some(t) = (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id)
                .filter(|&t| hittable_enemy(sim, team, t))
            {
                let dmg = amount(sim, caster, P.get("e_dmg"), 0, P.get("e_ap"), 0);
                sim.deal_damage(caster, t, 0, dmg, AttackTypeV1::Skill);
                sim.play_view_effect(VIEW_BURST, caster, &InputTargetV1::target(t), 0, 0, 0);
            }
            log(sim, format!("CONGEAL #{caster}: no crystals"));
            return;
        }
        let rooted = root_pick(&hits).filter(|&r| !cc_immune(sim, r));
        if let Some(r) = rooted {
            sim.apply_cc(r, &CcV1::of_kind(CcKindV1::Bind, P.get("e_root") as u64));
        }
        log(sim, format!("CONGEAL #{caster}: {} burst, root {:?}", hits.len(), rooted));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (0, P.get("e_dmg") + 2 * P.get("e_kdmg") + s.magic_power * (P.get("e_ap") + 2 * P.get("e_kap")) / 100)
    }

    fn expected_cc_time(&self) -> Option<usize> {
        Some(P.get("e_root"))
    }
}

struct Ebb;

impl StableEffectType for Ebb {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        if !alive(sim, caster) {
            return;
        }
        let (Some(at), Some(team)) = (pos_of(sim, caster), team_of(sim, caster)) else { return };
        let own = bands_of(sim, caster).pop().map(|x| x.1);
        let Some(band) = own.or_else(|| band_through(sim, caster, &input)) else { return };
        clear_bands(sim, caster);
        let far = band.far_end(P.f("q_len"));
        let Some(dir) = unit((at.0 - far.0, at.1 - far.1)) else { return };
        let pic = if leftward(dir) { WAVE_L } else { WAVE_R };
        let spec = ProjectileSpawnV1 {
            caster_id: caster,
            team,
            x: far.0.max(0.0) as u64,
            y: far.1.max(0.0) as u64,
            radius: (P.get("r_w") / 2) as u64,
            speed: P.get("r_speed") as u64,
            move_kind: ProjectileMoveKindV1::Linear.code(),
            target_id: 0,
            target_x: at.0.max(0.0) as u64,
            target_y: at.1.max(0.0) as u64,
            penetrate: true,
            attack_type: AttackTypeV1::Skill.code(),
            casting_type: CastingTypeV1::Targeting.code(),
            casting_target: CastingTargetV1::EnemyWithoutTower.code(),
        };
        let ok = sim.spawn_projectile(pic, &format!("{ID}:ebb_hit"), &spec);
        log(sim, format!("EBB #{caster}: {} band, wave from ({:.0}, {:.0}) {}{}",
                         if own.is_some() { "her" } else { "a new" }, far.0, far.1, pic,
                         if ok { "" } else { " (spawn_projectile refused)" }));
    }

    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        (0, P.get("r_dmg") + s.magic_power * P.get("r_ap") / 100)
    }
}

struct EbbHit;

impl StableEffectType for EbbHit {
    fn apply(&self, sim: &mut StableSim<'_>, _rng: u64, caster: usize, input: InputTargetV1) {
        let Some(t) = (input.kind == InputTargetKindV1::Target.code()).then_some(input.target_id) else { return };
        let dmg = amount(sim, caster, P.get("r_dmg"), 0, P.get("r_ap"), 0);
        sim.deal_damage(caster, t, 0, dmg, AttackTypeV1::Skill);
        sim.play_view_effect(VIEW_HIT, caster, &InputTargetV1::target(t), 0, 0, 0);
        add_crystal(sim, caster, t, P.get("r_stack"));
        // 被潮水往施法的人那边带
        if let (Some(from), Some(to)) = (pos_of(sim, t), pos_of(sim, caster)) {
            let d = dist(from, to);
            let pull = P.f("r_pull").min((d - 15_000.0).max(0.0));
            if pull > 1_000.0 && !cc_immune(sim, t) {
                let u = unit((to.0 - from.0, to.1 - from.1)).unwrap_or((0.0, 0.0));
                let ticks = P.get("r_pull_t").max(1) as u64;
                let mut mv = CcV1::of_kind(CcKindV1::ForceMove, ticks);
                mv.dx = (u.0 * pull).round() as i64;
                mv.dy = (u.1 * pull).round() as i64;
                mv.speed = (pull / ticks as f64).ceil() as u64;
                sim.apply_cc(t, &mv);
            }
        }
    }
}

struct Noop;

impl StableEffectType for Noop {
    fn apply(&self, _: &mut StableSim<'_>, _: u64, _: usize, _: InputTargetV1) {}
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    crate::wlog(format!("yanxi: {ID} v{VERSION} (Yan Xi: salt band, crystals, congeal, ebb tide) registered"));
    module.add_native_passive(format!("{ID}:salt"), Salt::default());
    module.add_native_effect(format!("{ID}:line"), Line);
    module.add_native_effect(format!("{ID}:congeal"), Congeal);
    module.add_native_effect(format!("{ID}:ebb"), Ebb);
    module.add_native_effect(format!("{ID}:ebb_hit"), EbbHit);
    module.add_native_effect(format!("{ID}:noop"), Noop);
    host.log(LogLevel::Info, "border.dll: Yan Xi (salt band, crystals, voice lines).");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_kit_and_the_dll_agree() {
        check_kit_params(ID, &P);
    }

    #[test]
    fn the_band_rides_in_the_buff_name() {
        let b = Band { center: (480_000.0, 300_000.0), dir: unit((-3.0, 4.0)).unwrap() };
        let n = b.name();
        assert!(n.len() <= BUFF_NAME_CAP, "{n}");
        let back = Band::parse(&n).unwrap();
        assert_eq!(back.center, b.center);
        assert!((back.dir.0 - b.dir.0).abs() < 2e-3 && (back.dir.1 - b.dir.1).abs() < 2e-3);
        assert!(Band::parse("border_yanxi_crystal").is_none());
    }

    #[test]
    fn the_band_holds_what_lies_on_it() {
        let b = Band { center: (0.0, 0.0), dir: (1.0, 0.0) };
        assert!(b.holds((20_000.0, 0.0), 50_000.0, 14_000.0, 0.0));
        assert!(!b.holds((30_000.0, 0.0), 50_000.0, 14_000.0, 0.0));
        assert!(!b.holds((0.0, 9_000.0), 50_000.0, 14_000.0, 0.0));
        // 身子压到边上也算
        assert!(b.holds((0.0, 9_000.0), 50_000.0, 14_000.0, 10_000.0));
        assert_eq!(b.far_end(50_000.0), (25_000.0, 0.0));
    }

    #[test]
    fn only_the_most_crystallised_champion_is_rooted() {
        let hits = [(1, 3, 0.9, true), (2, 5, 0.9, true), (3, 5, 0.4, true), (4, 9, 0.1, false)];
        assert_eq!(root_pick(&hits), Some(3));
        assert_eq!(root_pick(&[(4, 9, 0.1, false)]), None);
        assert_eq!(root_pick(&[]), None);
    }

    #[test]
    fn leftward_pictures_are_flipped() {
        assert!(leftward((-1.0, 0.0)));
        assert!(leftward((-0.2, 0.98)));
        assert!(!leftward((0.2, -0.98)));
        assert!(!leftward((0.0, 1.0)));
    }
}
