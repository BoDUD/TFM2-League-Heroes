//! AI 钩子 `league_orianna:farm`：走上去补刀（0.2.0，用户转来的玩家反馈 2026-10-23：「Orianna doesn't walk up to farm for
//! some reason, just stands next to tower」）。
//!
//! 0.1.2 的只读诊断（`league_orianna:diag`，没合进 main）看了 13 局预模拟、127 264 tick 游戏的 AI 给她的命令：没命令 99 483、
//! 走路 25 515、回城 1 396、普攻 407、Q 314、E 90、R 59；1065 行里 947 行的最后一条是走到离她 15–38k 的固定路点（兵线、塔边的
//! 点，8% 正好离她自己的塔 32000）；60k 内有敌方小兵的 158 段（每段 2 秒）平均还是走路 25.7 次、普攻 0.92 次，63 段一下都没打。
//! 也就是 AI 把她当成在路点之间来回走，不去打兵。
//!
//! 本钩子在 league_ult_press（100）之后（`PRIORITY`）：AI（或 league_ult_press）下的是普攻、技能、大招、回城就不管；只在它
//! 没下命令或只下走路命令时，`plan` 看这一 tick：
//! - 生命不到 `MIN_HP`、`CLEAR` 内有敌方英雄（打不打英雄是 AI 和 league_ult_press 的事：它的站桩普攻只打她普攻距离内的英雄）、
//!   正在回城、在放技能或被位移（`busy`）时不管；
//! - 普攻距离（`ATK_RANGE`）内有敌方小兵：普攻好了就打一个——这一下打得死的（`kills`：普攻的物理伤害按护甲、发条驱动的魔法伤害
//!   按魔抗）优先，其次血最少的；普攻没好、AI 要她走出能打到那个小兵的地方时让她站着（`Stay`）；
//! - 否则 `WALK` 内最近的敌方小兵：走到离它 `STAND` 的地方（走过去的那一点 `CLEAR` 内也不能有敌方英雄）。
//! 小兵和她站的地方都不能在敌方塔下（`TOWER_REACH`），除非那座塔下有至少 `TANKS` 个我方小兵替她扛塔。
//! 野怪、塔、敌方英雄不归这里。日志 `FARM`。

use mod_api_stable::*;

use super::{counted, dist, head, toward, who, wlog, ID};

/// league_ult_press（100）之后。
pub const PRIORITY: i32 = 105;
/// 她的普攻距离（主包 build_orianna.P 的 atk_range）、发条驱动每一下的魔法伤害（p_dmg + p_ap% 法强，不算叠层）。
pub const ATK_RANGE: f64 = 55_000.0;
pub const WINDUP_DMG: usize = 18;
pub const WINDUP_AP: usize = 15;
/// 这么近有敌方英雄就不管（她的普攻距离再加一点）。
pub const CLEAR: f64 = 60_000.0;
/// 这么近的敌方小兵才走上去；走到离它这么远（普攻距离以内）。
pub const WALK: f64 = 60_000.0;
pub const STAND: f64 = 50_000.0;
/// 敌方塔的攻击范围（大约），塔下要有这么多我方小兵才去。
pub const TOWER_REACH: f64 = 75_000.0;
pub const TANKS: usize = 2;
/// 生命比例低于这个不管（回不回城是 AI 的事）。
pub const MIN_HP: f64 = 0.4;

/// 一个敌方小兵：id、位置、现在的血、护甲、魔抗。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Minion {
    pub id: usize,
    pub at: (f64, f64),
    pub hp: usize,
    pub armour: usize,
    pub mr: usize,
}

/// 她这一 tick 看到的：位置、生命比例、攻击力、法强，敌方英雄、敌方小兵、我方小兵、敌方塔的位置。
pub struct Scene<'a> {
    pub me: (f64, f64),
    pub hp: f64,
    pub ad: usize,
    pub ap: usize,
    pub champs: &'a [(f64, f64)],
    pub minions: &'a [Minion],
    pub tanks: &'a [(f64, f64)],
    pub towers: &'a [(f64, f64)],
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Plan {
    /// 普攻这个小兵（这一下打得死它吗）。
    Attack(usize, bool),
    /// 普攻没好：站在原地（AI 要她走出能打到这个小兵的地方）。
    Stay(usize),
    /// 走到这里（朝这个小兵）。
    Walk((f64, f64), usize),
}

/// 她这一下打在这个小兵身上打得死吗：普攻 = 攻击力的物理伤害（× 100 / (100 + 护甲)），加发条驱动的魔法伤害（× 100 / (100 + 魔抗)）。
pub fn kills(ad: usize, ap: usize, m: &Minion) -> bool {
    let hit = ad * 100 / (100 + m.armour) + (WINDUP_DMG + WINDUP_AP * ap / 100) * 100 / (100 + m.mr);
    m.hp > 0 && m.hp <= hit
}

impl Scene<'_> {
    /// 这一点不在敌方塔下，或那座塔下有 `TANKS` 个我方小兵扛塔。
    pub fn safe(&self, p: (f64, f64)) -> bool {
        self.towers.iter().all(|&t| {
            dist(t, p) > TOWER_REACH || self.tanks.iter().filter(|&&m| dist(t, m) <= TOWER_REACH).count() >= TANKS
        })
    }

    fn clear(&self, p: (f64, f64)) -> bool {
        !self.champs.iter().any(|&c| dist(c, p) <= CLEAR)
    }
}

/// 这一 tick 让她做什么（None = 交给 AI）。`ready`：普攻好了；`ai_move`：AI 这一 tick 让她走到哪（没下命令就是 None）。
pub fn plan(s: &Scene<'_>, ready: bool, ai_move: Option<(f64, f64)>) -> Option<Plan> {
    if s.hp < MIN_HP || !s.clear(s.me) {
        return None;
    }
    let ok: Vec<&Minion> = s.minions.iter().filter(|m| s.safe(m.at)).collect();
    let in_range = ok.iter().filter(|m| dist(s.me, m.at) <= ATK_RANGE);
    // the one this hit kills first, then the lowest
    let best = in_range.min_by_key(|m| (!kills(s.ad, s.ap, m), m.hp)).copied();
    if let Some(m) = best.filter(|_| s.safe(s.me)) {
        if ready {
            return Some(Plan::Attack(m.id, kills(s.ad, s.ap, m)));
        }
        return match ai_move {
            Some(to) if dist(to, m.at) > ATK_RANGE => Some(Plan::Stay(m.id)),
            _ => None,
        };
    }
    let m = ok
        .iter()
        .filter(|m| dist(s.me, m.at) <= WALK)
        .min_by(|a, b| dist(s.me, a.at).total_cmp(&dist(s.me, b.at)))?;
    let d = dist(s.me, m.at);
    let spot = toward(s.me, m.at, (d - STAND).max(0.0)).0;
    (s.safe(spot) && s.clear(spot)).then_some(Plan::Walk(spot, m.id))
}

// ===================== 钩子 =====================

/// 正在放技能（施法动作还在播）或被强制位移：不替 AI 下命令，按普攻会打断它（league_ult_press 的 `busy`）。
const BUSY: [CcKindV1; 2] = [CcKindV1::Animation, CcKindV1::ForceMove];

fn busy(e: &StableEntity<'_, '_>) -> bool {
    (0..e.cc_count()).any(|i| e.cc_at(i).is_some_and(|c| BUSY.iter().any(|k| k.code() == c.kind)))
}

fn at(e: &StableEntity<'_, '_>) -> (f64, f64) {
    let (x, y) = e.pos();
    (x as f64, y as f64)
}

fn is_minion(e: &StableEntity<'_, '_>) -> bool {
    match e.kind() {
        Some(k) => k == EntityKindV1::Minion,
        None => e.is_minion(),
    }
}

#[derive(Clone, Default)]
pub struct Farm {
    /// 正在回城（回城命令开始、别的命令结束；游戏 0.6.5 的 AI 只在判断的那几 tick 下命令）。
    recalling: bool,
}

impl StablePlayerAi for Farm {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{ID}:farm")
    }

    fn priority(&self) -> i32 {
        PRIORITY
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.champion_name == ID
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, base: Option<InputV1>) -> Option<InputV1> {
        self.recalling = match base {
            Some(b) => b.kind == InputKindV1::Return.code(),
            None => self.recalling,
        };
        if self.recalling {
            return None;
        }
        // an attack, a skill or an R (the AI's, or league_ult_press's press): its call
        let ai_move = match base {
            None => None,
            Some(b) if b.kind == InputKindV1::Move.code() => Some((b.x as f64, b.y as f64)),
            Some(_) => return None,
        };
        let player = ctx.player_id();
        let (input, kind, line) = {
            let sim = ctx.sim()?;
            let me = sim.get_player(player)?.champion()?;
            if !me.is_alive() || busy(&me) {
                return None;
            }
            let (my_id, team, here) = (me.id(), me.team(), at(&me));
            let (hp, max) = me.hp();
            let stat = me.stat();
            let ready = me.cooldown(SkillSlotV1::Attack).is_some_and(|c| c.unlocked && c.remaining == 0);
            let (mut champs, mut minions, mut tanks) = (Vec::new(), Vec::new(), Vec::new());
            for i in 0..sim.entity_count() {
                let Some(u) = sim.entity_at(i) else { continue };
                if !u.is_alive() || u.id() == my_id {
                    continue;
                }
                let mine = u.team() == team;
                if u.is_champion() {
                    if !mine {
                        champs.push(at(&u));
                    }
                } else if is_minion(&u) {
                    if mine {
                        tanks.push(at(&u));
                    } else if u.is_targetable() {
                        let s = u.stat();
                        minions.push(Minion { id: u.id(), at: at(&u), hp: u.hp().0, armour: s.defence, mr: s.magic_resistance });
                    }
                }
            }
            let towers: Vec<(f64, f64)> = (0..sim.tower_count())
                .filter_map(|i| sim.get_entity(sim.tower_id_at(i)))
                .filter(|t| t.team() != team && t.is_alive())
                .map(|t| at(&t))
                .collect();
            let scene = Scene {
                me: here,
                hp: hp as f64 / max.max(1) as f64,
                ad: stat.attack,
                ap: stat.magic_power,
                champs: &champs,
                minions: &minions,
                tanks: &tanks,
                towers: &towers,
            };
            let p = plan(&scene, ready, ai_move)?;
            let far = |id: usize| minions.iter().find(|m| m.id == id).map_or(f64::NAN, |m| dist(here, m.at));
            let hp_of = |id: usize| minions.iter().find(|m| m.id == id).map_or(0, |m| m.hp);
            let (input, kind, what) = match p {
                Plan::Attack(t, kill) => (
                    InputV1::action(InputKindV1::Attack, InputTargetV1::target(t)),
                    if kill { "farm last hit" } else { "farm attack" },
                    format!("attack {} at {} hp, {:.0} away{}", who(&sim, t), hp_of(t), far(t),
                            if kill { ": a last hit" } else { "" }),
                ),
                Plan::Stay(t) => (
                    InputV1::move_to(here.0.max(0.0) as u64, here.1.max(0.0) as u64),
                    "farm stay",
                    format!("stay (attack not ready) by {} {:.0} away instead of the AI's walk", who(&sim, t), far(t)),
                ),
                Plan::Walk(to, t) => (
                    InputV1::move_to(to.0.max(0.0) as u64, to.1.max(0.0) as u64),
                    "farm walk",
                    format!("walk up to {} {:.0} away (the AI: {})", who(&sim, t), far(t),
                            if ai_move.is_some() { "a walk elsewhere" } else { "no order" }),
                ),
            };
            (input, kind, format!("{} FARM {what}", head(&sim, my_id)))
        };
        if !ctx.is_valid_input(&input) {
            return None;
        }
        if let Some(k) = counted(kind) {
            wlog(format!("{line} #{k}"));
        }
        Some(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn minion(id: usize, x: f64, hp: usize) -> Minion {
        Minion { id, at: (x, 0.0), hp, armour: 0, mr: 0 }
    }

    fn scene<'a>(minions: &'a [Minion], champs: &'a [(f64, f64)], tanks: &'a [(f64, f64)],
                 towers: &'a [(f64, f64)]) -> Scene<'a> {
        Scene { me: (0.0, 0.0), hp: 1.0, ad: 50, ap: 0, champs, minions, tanks, towers }
    }

    #[test]
    fn the_last_hit_first_then_the_lowest() {
        // 50 attack + 18 windup = 68: the 60-hp one dies to it, the 30-hp one (armour 200) takes 16 + 18 = 34 and dies too
        let mut tough = minion(3, 30_000.0, 30);
        tough.armour = 200;
        let wave = [minion(1, 40_000.0, 300), minion(2, 50_000.0, 60), tough];
        assert_eq!(plan(&scene(&wave, &[], &[], &[]), true, None), Some(Plan::Attack(3, true)));
        let wave = [minion(1, 40_000.0, 300), minion(2, 50_000.0, 69)];
        assert!(!kills(50, 0, &wave[1]) && kills(50, 7, &wave[1]));
        // nobody dies to this hit: the lowest
        assert_eq!(plan(&scene(&wave, &[], &[], &[]), true, None), Some(Plan::Attack(2, false)));
        // out of her attack range: not attacked
        let far = [minion(1, 56_000.0, 10)];
        assert!(matches!(plan(&scene(&far, &[], &[], &[]), true, None), Some(Plan::Walk(..))));
    }

    #[test]
    fn the_attack_not_ready_she_stays_in_range() {
        let wave = [minion(1, 40_000.0, 300)];
        let s = scene(&wave, &[], &[], &[]);
        // the AI walks her back to its point by her tower: she stays
        assert_eq!(plan(&s, false, Some((-30_000.0, 0.0))), Some(Plan::Stay(1)));
        // a walk that keeps the minion in reach, or no order: the AI's
        assert_eq!(plan(&s, false, Some((10_000.0, 0.0))), None);
        assert_eq!(plan(&s, false, None), None);
    }

    #[test]
    fn she_walks_up_to_the_wave() {
        let wave = [minion(1, 58_000.0, 300), minion(2, 70_000.0, 300)];
        match plan(&scene(&wave, &[], &[], &[]), false, Some((-30_000.0, 0.0))) {
            Some(Plan::Walk(to, 1)) => assert!((dist(to, (58_000.0, 0.0)) - STAND).abs() < 1.0, "{to:?}"),
            p => panic!("{p:?}"),
        }
        // beyond WALK: the AI's
        let wave = [minion(1, 61_000.0, 300)];
        assert_eq!(plan(&scene(&wave, &[], &[], &[]), true, None), None);
        assert_eq!(plan(&scene(&[], &[], &[], &[]), true, None), None);
    }

    #[test]
    fn champions_low_health_and_towers_stop_her() {
        let wave = [minion(1, 40_000.0, 300)];
        // an enemy champion within CLEAR: the AI's and league_ult_press's call
        assert_eq!(plan(&scene(&wave, &[(-55_000.0, 0.0)], &[], &[]), true, None), None);
        assert!(plan(&scene(&wave, &[(-65_000.0, 0.0)], &[], &[]), true, None).is_some());
        // walking up (to 8000) would bring her within CLEAR of one 66000 away
        let far = [minion(1, 58_000.0, 300)];
        assert_eq!(plan(&scene(&far, &[(66_000.0, 0.0)], &[], &[]), true, None), None);
        assert!(plan(&scene(&far, &[(70_000.0, 0.0)], &[], &[]), true, None).is_some());
        // low
        let mut s = scene(&wave, &[], &[], &[]);
        s.hp = 0.3;
        assert_eq!(plan(&s, true, None), None);
        // the minion under an enemy tower, nothing of hers there: no; two of her minions under it: yes
        let tower = [(100_000.0, 0.0)];
        assert_eq!(plan(&scene(&wave, &[], &[], &tower), true, None), None);
        let one = [(90_000.0, 0.0)];
        assert_eq!(plan(&scene(&wave, &[], &one, &tower), true, None), None);
        let two = [(90_000.0, 0.0), (95_000.0, 5_000.0)];
        assert_eq!(plan(&scene(&wave, &[], &two, &tower), true, None), Some(Plan::Attack(1, false)));
        // the minion clear of it but she stands under it: no
        let near_her = [(-70_000.0, 0.0)];
        assert_eq!(plan(&scene(&wave, &[], &[], &near_her), true, None), None);
    }

    #[test]
    fn the_numbers_match_the_kit() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../../tools/kit/build_orianna.py");
        let src = std::fs::read_to_string(path).expect("build_orianna.py");
        for (key, v) in [("atk_range", ATK_RANGE as usize), ("p_dmg", WINDUP_DMG), ("p_ap", WINDUP_AP)] {
            assert!(src.contains(&format!("\"{key}\": {v}")), "{key} is not {v} in build_orianna.P");
        }
        assert!(STAND < ATK_RANGE && WALK <= CLEAR);
    }

    #[test]
    fn after_league_ult_press() {
        assert!(PRIORITY > 100);
    }
}
