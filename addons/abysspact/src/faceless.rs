//! 无面 (`abysspact_faceless`) · 无面者 · 打野刺客
//!
//! 招牌机制「夺面」+ R「撕面」25% 生命斩杀:
//! - R「撕面」命中敌方英雄后挂短标记 `abysspact_faceless_r_exec_ask`：若目标当前生命 <= 25% 最大生命，
//!   立即施加高额真实斩杀伤害撕死目标并当场触发夺面。
//! - 参与击杀敌方英雄（击杀，或击杀记录里助攻名单有他的分路）立即「夺面」10 秒（600 ticks）：
//!   * 通知显示层钩子 (`faceless_view::note_steal`) 把无面整身画成被杀英雄；
//!   * 模拟层挂上 `abysspact_faceless_shape`、黑影 `shroud`、白瓷裂纹 `cracks`、受害者的类别
//!     (`abysspact_faceless_cls_{melee,range,mage,util,assassin}`) 和一次借来的大招 `r_stolen`；
//!   * 普攻跟着变：射手、法师、辅助类的脸普攻变成飞出去的面具弹，射程由 [`Reach`]（`range_adjust`）按类别加长；
//!     攻速按受害者的普攻间隔调成和他一样快慢（`shroud` 的攻速）；
//!   * 大招跟着变：R 的冷却刷新，这 10 秒里放 R 是那一类的大招（数据里五套，照塞拉斯附加包按类别偷大招的做法），
//!     放过一次就回到撕面。冷却要等动作放完才开始走：夺面时 R / Q 还在放（冷却是 0）就先记下，冷却跳起来的那一拍再减
//!     （脸还戴着、借来的大招还没放才减）；
//!   * 10 秒到期时播放 `shards` 面具碎裂特效并恢复无面本体。

use mod_api_stable::*;

use crate::faceless_view;
use crate::voice::{Cue, Voice};
use crate::{buffs_present, foe_champions};

pub const HERO: &str = "abysspact_faceless";
pub const SHAPE: &str = "abysspact_faceless_shape";
pub const SHROUD: &str = "abysspact_faceless_shroud";
pub const CRACKS: &str = "abysspact_faceless_cracks";
pub const R_STOLEN: &str = "abysspact_faceless_r_stolen";
pub const R_EXEC_ASK: &str = "abysspact_faceless_r_exec_ask";
pub const R_CAST_VOICE: &str = "abysspact_faceless_r_voice";
pub const CLASSES: [&str; 5] = ["melee", "range", "mage", "util", "assassin"];

pub const MASK_TICKS: usize = 600; // 10 seconds
pub const EXEC_PCT: usize = 25;
/// 同一张脸这么多 tick 内只夺一次（斩杀自己夺一次，击杀的回调和击杀记录又会各报一次）。
pub const STEAL_DEDUP: usize = 30;
/// 敌方英雄的分路表多久看一次。
pub const LANES_EVERY: usize = 30;
/// 夺面时 Q 减多少冷却（连杀顺手）。
pub const Q_CUT: usize = 180;

pub fn should_execute(cur: usize, max: usize) -> bool {
    max > 0 && cur > 0 && cur.saturating_mul(100) <= max.saturating_mul(EXEC_PCT)
}

pub fn victim_category(champ_id: &str) -> &'static str {
    faceless_view::category_of(champ_id).unwrap_or("melee")
}

pub fn class_buff(cat: &str) -> String {
    format!("abysspact_faceless_cls_{cat}")
}

/// 借来的普攻多出的射程（无面自己 2.6 万）：射手到 6.2 万，法师 5.2 万，辅助 5 万，近战、刺客不变。
pub fn reach_bonus(cat: &str) -> u64 {
    match cat {
        "range" => 36_000,
        "mage" => 26_000,
        "util" => 24_000,
        _ => 0,
    }
}

/// 借来的手感：攻速改多少 %，让他的普攻间隔和受害者的一样（`mine` / `theirs` 是两人此刻的普攻间隔 tick）。
/// 读不到间隔（老宿主给 0）就照旧 +20%。
pub fn feel_attack_speed(mine: usize, theirs: usize) -> i32 {
    if mine == 0 || theirs == 0 {
        return 20;
    }
    let pct = (mine as i64 * 100 / theirs as i64) - 100;
    pct.clamp(-40, 100) as i32
}

/// 记下的减冷却这一拍怎么办：`pending` 记着、`valid` 还作数（脸还戴着 / 借来的大招还没放）、`left` 是这一格剩下的冷却。
/// → (现在减, 继续记着)。冷却跳起来（> 0）的第一拍减；作废了就不记了。
pub fn settle_cut(pending: bool, valid: bool, left: usize) -> (bool, bool) {
    match (pending, valid, left > 0) {
        (false, ..) => (false, false),
        (true, false, _) => (false, false),
        (true, true, true) => (true, false),
        (true, true, false) => (false, true),
    }
}

/// 同一张脸刚夺过（`STEAL_DEDUP` tick 内）就不再夺。`at` 比现在还晚（新的一局，tick 从头算）不算刚夺过。
pub fn stolen_just_now(last: Option<&(String, usize)>, name: &str, tick: usize) -> bool {
    last.is_some_and(|(n, t)| n == name && tick >= *t && tick - *t <= STEAL_DEDUP)
}

/// 击杀记录的一条里，这一队、这个分路的人算不算参与了击杀（击杀者或助攻）。
pub fn took_part(k: &KillLogV1, team: usize, lane: u32) -> bool {
    k.killer_team == team
        && (k.killer_position == lane || k.assist_positions[..(k.assist_count as usize).min(4)].contains(&lane))
}

#[derive(Clone, Default)]
struct FacelessPassive {
    voice: Voice,
    /// 他这条命的单位（on_dead 只给玩家编号）。
    me: Option<usize>,
    /// 敌方英雄：(分路, 英雄 id, 普攻间隔)。阵亡的英雄单位第二拍就没了，助攻时按击杀记录的分路在这里认人。
    lanes: Vec<(u32, String, usize)>,
    lanes_at: usize,
    /// 击杀记录读到第几条。
    kills_seen: usize,
    /// Tick when current Face-Steal expires (0 = not masked).
    mask_until: usize,
    mask_cat: Option<&'static str>,
    noted_view: bool,
    last_steal: Option<(String, usize)>,
    /// 夺面时还没减成的冷却（R 刷新、Q 减一点）：冷却跳起来再减。
    pending_ult: bool,
    pending_q: bool,
    /// 上一次看到的 tick：变小了就是新的一局（被动实例可能被下一局接着用）。
    last_tick: usize,
}

impl FacelessPassive {
    /// 新的一局（或新的一条命）：上一局的分路表、刚夺过的脸、没减成的冷却都不要了。
    fn forget(&mut self) {
        self.lanes.clear();
        self.lanes_at = 0;
        self.last_steal = None;
        self.pending_ult = false;
        self.pending_q = false;
    }

    fn clear_mask(&mut self, sim: &mut StableSim<'_>, entity: usize, play_shards: bool, note_end: bool) {
        if self.mask_until == 0 {
            return;
        }
        self.mask_until = 0;
        sim.entity_remove_buff(entity, SHAPE);
        sim.entity_remove_buff(entity, SHROUD);
        sim.entity_remove_buff(entity, CRACKS);
        sim.entity_remove_buff(entity, R_STOLEN);
        for cat in CLASSES {
            sim.entity_remove_buff(entity, &class_buff(cat));
        }
        self.mask_cat = None;
        // 换下一张脸时不记结束：显示那边新的一段从同一 tick 开始，记了结束就把新脸也一起关掉了
        if note_end {
            if let Some((m, s)) = view_origin(sim) {
                faceless_view::note_end(m, s, entity, sim.tick());
            }
        }
        if play_shards {
            sim.play_view_effect("abysspact_faceless_shards", entity, &InputTargetV1::target(entity), 0, 0, 0);
            sim.play_sfx("abysspact_faceless_mask_crack", entity, &InputTargetV1::target(entity));
        }
    }

    /// 夺面。`interval` 是受害者的普攻间隔（读不到给 0）。
    fn steal_face(&mut self, sim: &mut StableSim<'_>, entity: usize, victim_name: &str, interval: usize) {
        if victim_name.is_empty() || victim_name == HERO {
            return;
        }
        let tick = sim.tick();
        if stolen_just_now(self.last_steal.as_ref(), victim_name, tick) {
            return;
        }
        self.last_steal = Some((victim_name.to_string(), tick));
        self.clear_mask(sim, entity, false, false);
        self.mask_until = tick + MASK_TICKS;
        let cat = victim_category(victim_name);
        self.mask_cat = Some(cat);

        // 手感：攻速调成受害者的快慢（先拿掉旧黑影再读自己的间隔）
        let mine = sim.get_entity(entity).map_or(0, |e| e.attack_interval());
        sim.add_buff(entity, &BuffV1::timed(SHAPE, MASK_TICKS));
        let mut shroud = BuffV1::timed(SHROUD, MASK_TICKS);
        shroud.attack_mult = 15;
        shroud.attack_speed_mult = feel_attack_speed(mine, interval);
        shroud.move_speed_mult = 10;
        sim.add_buff(entity, &shroud);
        sim.add_buff(entity, &BuffV1::timed(CRACKS, MASK_TICKS));
        sim.add_buff(entity, &BuffV1::timed(&class_buff(cat), MASK_TICKS));
        sim.add_buff(entity, &BuffV1::timed(R_STOLEN, MASK_TICKS));

        // 大招刷新：借来的那一招这 10 秒里能放一次；Q 也减一点冷却，连杀顺手。冷却在走的当场减；
        // 还是 0 的（多半正在放 R / Q，冷却要等动作放完才开始走）先记下，跳起来那一拍再减
        let (ult_left, q_left) = sim.get_entity(entity).map_or((0, 0), |e| {
            (
                e.cooldown(SkillSlotV1::Ult).map_or(0, |c| c.remaining),
                e.cooldown(SkillSlotV1::Skill).map_or(0, |c| c.remaining),
            )
        });
        self.pending_ult = ult_left == 0;
        if ult_left > 0 {
            sim.entity_reduce_cooldown(entity, SkillSlotV1::Ult, ult_left);
        }
        self.pending_q = q_left == 0;
        if q_left > 0 {
            sim.entity_reduce_cooldown(entity, SkillSlotV1::Skill, Q_CUT);
        }
        sim.play_sfx("abysspact_faceless_shroud_rise", entity, &InputTargetV1::target(entity));

        if let Some((m, s)) = view_origin(sim) {
            faceless_view::note_steal(m, s, entity, tick, victim_name);
        }
    }

    /// 敌方英雄的分路表：活着的时候记下名字和普攻间隔。
    fn note_lanes(&mut self, sim: &StableSim<'_>, team: usize) {
        for i in 0..sim.player_count() {
            let Some(p) = sim.player_at(i) else { continue };
            if p.team() == team {
                continue;
            }
            let (Some(lane), Some(c)) = (p.lane(), p.champion()) else { continue };
            if !c.is_alive() {
                continue;
            }
            let Some(name) = c.name() else { continue };
            let interval = c.attack_interval();
            match self.lanes.iter_mut().find(|l| l.0 == lane.code()) {
                Some(l) => {
                    l.1 = name;
                    l.2 = interval;
                }
                None => self.lanes.push((lane.code(), name, interval)),
            }
        }
    }

    /// 新的击杀记录：他参与了的（击杀者或助攻名单里有他的分路），按被杀的分路认人夺面。
    fn read_kills(&mut self, sim: &mut StableSim<'_>, player: usize, team: usize, entity: usize) {
        let n = sim.kill_log_count();
        if self.kills_seen > n {
            self.kills_seen = 0; // 一局新的比赛
        }
        let Some(lane) = sim.get_player(player).and_then(|p| p.lane()).map(|l| l.code()) else {
            self.kills_seen = n;
            return;
        };
        let mut victim: Option<(String, usize)> = None;
        while self.kills_seen < n {
            let Some(k) = sim.kill_log_at(self.kills_seen) else { break };
            self.kills_seen += 1;
            if took_part(&k, team, lane) {
                if let Some(l) = self.lanes.iter().find(|l| l.0 == k.killed_position) {
                    victim = Some((l.1.clone(), l.2));
                }
            }
        }
        if let Some((name, interval)) = victim {
            self.steal_face(sim, entity, &name, interval);
        }
    }
}

fn view_origin(sim: &StableSim<'_>) -> Option<(u64, u64)> {
    let o = sim.sim_origin()?;
    let k = SimOriginKindV1::from_code(o.kind)?;
    matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
        .then_some((o.match_id, o.set_index))
}

impl StablePassive for FacelessPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.me = Some(entity);
        self.mask_until = 0;
        self.mask_cat = None;
        self.forget();
        self.last_tick = sim.tick();
        // 死着的时候记下的击杀不算（复活那一刻突然换脸很怪）
        self.kills_seen = sim.kill_log_count();
        self.voice.on_spawn(sim, HERO, entity);
        if !self.noted_view {
            if let Some((m, s)) = view_origin(sim) {
                faceless_view::note_view(m, s);
                self.noted_view = true;
            }
        }
    }

    fn on_attack(
        &mut self,
        sim: &mut StableSim<'_>,
        _player: usize,
        entity: usize,
        target: usize,
        _damage: &mut usize,
    ) {
        if sim.get_entity(target).is_some_and(|te| te.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        let info = sim
            .get_entity(victim)
            .filter(|e| e.is_champion())
            .and_then(|e| e.name().map(|n| (n, e.attack_interval())));
        if let Some((vname, interval)) = info {
            self.voice.play(sim, HERO, entity, Cue::Kill);
            self.steal_face(sim, entity, &vname, interval);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        // 他死了，脸也碎了：显示那边记下结束，尸体不再画成别人
        if self.mask_until > 0 {
            if let (Some(me), Some((m, s))) = (self.me, view_origin(sim)) {
                faceless_view::note_end(m, s, me, sim.tick());
            }
        }
        self.mask_until = 0;
        self.mask_cat = None;
        self.pending_ult = false;
        self.pending_q = false;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, player: usize, entity: usize) {
        self.me = Some(entity);
        self.voice.observe(entity);
        if !self.noted_view {
            if let Some((m, s)) = view_origin(sim) {
                faceless_view::note_view(m, s);
                self.noted_view = true;
            }
        }
        let tick = sim.tick();
        if tick < self.last_tick {
            // tick 变小：新的一局用着上一局的被动实例
            self.forget();
            self.kills_seen = 0;
            self.mask_until = 0;
            self.mask_cat = None;
        }
        self.last_tick = tick;
        let Some((alive, my_team)) = sim.get_entity(entity).map(|e| (e.is_alive(), e.team())) else {
            return;
        };
        if !alive {
            if self.mask_until > 0 {
                self.clear_mask(sim, entity, false, true);
            }
            return;
        }

        if crate::consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        if tick >= self.lanes_at {
            self.lanes_at = tick + LANES_EVERY;
            self.note_lanes(sim, my_team);
        }

        // 1. R 的斩杀标记：只看敌方英雄（十个人里的五个）
        for (cid, _) in foe_champions(sim, my_team) {
            let [ask] = buffs_present(sim, cid, [R_EXEC_ASK]);
            if !ask {
                continue;
            }
            sim.entity_remove_buff(cid, R_EXEC_ASK);
            let Some((cur, max, name, interval)) =
                sim.get_entity(cid).map(|e| (e.hp().0, e.hp().1, e.name().unwrap_or_default(), e.attack_interval()))
            else {
                continue;
            };
            if should_execute(cur, max) {
                // 真实伤害撕死；击杀的回调也会来夺面，steal_face 按名字去重，只夺一次
                sim.deal_damage_typed(entity, cid, max.max(9999), DamageTypeV1::Fixed, AttackTypeV1::Skill);
                self.voice.play(sim, HERO, entity, Cue::Kill);
                self.steal_face(sim, entity, &name, interval);
            }
        }

        // 2. 助攻：击杀记录里有他的分路
        self.read_kills(sim, player, my_team, entity);

        // 3. 夺面时记下的减冷却：冷却跳起来的第一拍减（R：借来的大招还没放；Q：脸还戴着）
        if self.pending_ult || self.pending_q {
            let [stolen] = buffs_present(sim, entity, [R_STOLEN]);
            let (ult_left, q_left) = sim.get_entity(entity).map_or((0, 0), |e| {
                (
                    e.cooldown(SkillSlotV1::Ult).map_or(0, |c| c.remaining),
                    e.cooldown(SkillSlotV1::Skill).map_or(0, |c| c.remaining),
                )
            });
            let (cut, keep) = settle_cut(self.pending_ult, stolen, ult_left);
            self.pending_ult = keep;
            if cut {
                sim.entity_reduce_cooldown(entity, SkillSlotV1::Ult, ult_left);
            }
            let (cut, keep) = settle_cut(self.pending_q, self.mask_until > 0, q_left);
            self.pending_q = keep;
            if cut {
                sim.entity_reduce_cooldown(entity, SkillSlotV1::Skill, Q_CUT);
            }
        }

        // 4. Expire 10s Face-Steal with shattering mask shards
        if self.mask_until > 0 && tick >= self.mask_until {
            self.clear_mask(sim, entity, true, true);
        }
    }
}

/// 借来的普攻射程（`StableEffectType::range_adjust`，数据的普攻最后挂这个原生效果）：身上是哪一类的脸就加多少，
/// AI 的射程判断也读它。
struct Reach;

impl StableEffectType for Reach {
    fn apply(&self, _sim: &mut StableSim<'_>, _seed: u64, _caster: usize, _input: InputTargetV1) {}

    fn may_adjust_range(&self) -> bool {
        true
    }

    fn range_adjust(&self, caster: &StableEntityView<'_>, _target: &StableEntityView<'_>) -> u64 {
        let mut best = 0;
        for i in 0..caster.buff_count() {
            let Some(b) = caster.buff_at(i) else { continue };
            if let Some(cat) = b.name().strip_prefix("abysspact_faceless_cls_") {
                best = best.max(reach_bonus(cat));
            }
        }
        best
    }
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_faceless:mask", FacelessPassive::default());
    module.add_native_effect("abysspact_faceless:reach", Reach);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn execute_threshold_is_25_percent() {
        assert!(should_execute(250, 1000));
        assert!(should_execute(1, 1000));
        assert!(!should_execute(251, 1000));
        assert!(!should_execute(0, 1000));
    }

    #[test]
    fn a_borrowed_ranged_face_reaches_like_its_owner() {
        assert_eq!(26_000 + reach_bonus("range"), 62_000);
        assert_eq!(26_000 + reach_bonus("mage"), 52_000);
        assert_eq!(26_000 + reach_bonus("util"), 50_000);
        assert_eq!(reach_bonus("melee"), 0);
        assert_eq!(reach_bonus("assassin"), 0);
    }

    #[test]
    fn the_borrowed_feel_matches_the_owners_attack_interval() {
        // 他 56 tick 一下，金克丝 28 tick 一下：攻速翻倍
        assert_eq!(feel_attack_speed(56, 28), 100);
        // 慢的坦克 75 tick 一下：慢下来，最多 -40%
        assert_eq!(feel_attack_speed(56, 75), -26);
        assert_eq!(feel_attack_speed(56, 200), -40);
        // 读不到间隔照旧 +20%
        assert_eq!(feel_attack_speed(0, 30), 20);
    }

    #[test]
    fn a_cut_waits_for_the_cooldown_to_start() {
        // 夺面时 R 正在放：冷却还是 0，记着
        assert_eq!(settle_cut(true, true, 0), (false, true));
        // 动作放完冷却跳起来：这一拍减掉
        assert_eq!(settle_cut(true, true, 3300), (true, false));
        // 借来的大招已经放了 / 脸碎了：作废，那一下的冷却照走
        assert_eq!(settle_cut(true, false, 3300), (false, false));
        assert_eq!(settle_cut(false, true, 3300), (false, false));
    }

    #[test]
    fn the_same_face_is_taken_once_and_a_new_match_forgets_it() {
        let last = ("league_jinx".to_string(), 5000);
        assert!(stolen_just_now(Some(&last), "league_jinx", 5020));
        assert!(!stolen_just_now(Some(&last), "league_jinx", 5031));
        assert!(!stolen_just_now(Some(&last), "league_lux", 5001));
        // 新的一局 tick 从头算：上一局 5000 tick 夺的不挡这一局
        assert!(!stolen_just_now(Some(&last), "league_jinx", 100));
    }

    #[test]
    fn an_assist_is_his_lane_in_the_kill_log() {
        let mut k = KillLogV1 { killer_team: 0, killer_position: 3, killed_position: 2, assist_count: 2, ..Default::default() };
        k.assist_positions = [4, 1, 0, 0];
        // 打野（1）在助攻名单里
        assert!(took_part(&k, 0, 1));
        // 上路（0）不在（后面两格是空的）
        assert!(!took_part(&k, 0, 0));
        // 击杀者自己
        assert!(took_part(&k, 0, 3));
        // 对面那一队的击杀
        assert!(!took_part(&k, 1, 1));
    }

    #[test]
    fn every_class_has_its_borrowed_ult_in_the_kit() {
        let kit = include_str!("../../../abysspact/champion/abysspact_faceless.data_champion");
        // 前四类各一个分支，刺客是最后剩下的那一支（闪到目标身上）
        for cat in &CLASSES[..4] {
            assert!(kit.contains(&format!("\"{}\"", class_buff(cat))), "no {cat} branch in the kit");
        }
        assert!(kit.contains("\"Teleport\""), "no assassin branch in the kit");
        assert!(kit.contains("abysspact_faceless:reach"), "the attack carries the borrowed reach");
        assert!(kit.contains("EnemyChampionRecentlyAttacked"), "R goes on a champion his team has been hitting");
        assert!(kit.contains("RushMoveToBack"), "Q dashes through to behind the target");
    }
}
