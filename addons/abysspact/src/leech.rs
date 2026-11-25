//! 附骨 (`abysspact_leech`) · 深渊寄生者 · 打野法术刺客
//!
//! - Q「扑附」扑中敌方英雄后附在他背上 3 秒（180 tick）：
//!   * 附着时受到的伤害减为 0（`attached`），显示钩子把动作换成 `attach`。没做成真正的选不中：引擎里选不中只有放逐，
//!     放逐会把他整个藏起来、也放不了蚀髓，和设计的「画在宿主身后、附着时对宿主放 W」对不上；
//!   * 宿主一动，就用一 tick 的强制位移把他挪到宿主背后（宿主走的方向的反面，再往屏幕上方挪一点，画在宿主身后）。
//!     强制位移画面跟着走；以前每 3 tick 直接改坐标，画面不跟，下次出手才一下跳过去；
//!   * 每 0.5 秒吸宿主 2.5% 最大生命（魔法伤害），等量治疗自己；宿主 -30% 移速（`host_mark`，附多久慢多久）；
//!   * 附骨之疽：宿主每 tick 掉的血他跟着挨 25%，扣掉他自己吸的那一口（吸血下一 tick 才结算，吸完先从记下的血量里扣掉
//!     预计掉的血）。以前只看每 3 tick 里的那一 tick，只挨到三分之一，有时还把自己吸的那口算进去；
//!   * 宿主死了跳到 5 万内最近的敌方英雄身上再附 2 秒（一次附着最多跳一次）。
//!   * 疼死了：从背上掉下来，算宿主打死的。
//! - R「万蛭」：裂成 5 只小水蛭，9 万内每个敌方英雄一只，多出来的扑血最少的，一个人身上最多 2 只（以前 5 只能全扑一个人，
//!   3 秒吸掉 60% 最大生命）。他本人放逐 3 秒（不在场上、选不中），每只小水蛭一发弹道扑向它的宿主；每 0.5 秒每只吸 2%
//!   最大生命，每个宿主挨的打他分 10%；3 秒后小水蛭从每个宿主飞回来聚成他，吸到的血全部治疗他。
//! - 他倒下：宿主身上的减速、小水蛭标记当场摘掉。

use mod_api_stable::*;

use crate::voice::{Cue, Voice};
use crate::{consume_buff, dist_sq, has_buff};

pub const HERO: &str = "abysspact_leech";
pub const NATIVE_MARK: &str = "abysspact_leech_native";
pub const ATTACH_ASK: &str = "abysspact_leech_attach_ask";
pub const ATTACHED_BUFF: &str = "abysspact_leech_attached";
pub const HOST_MARK: &str = "abysspact_leech_host_mark";
pub const MINI_CLING: &str = "abysspact_leech_mini_cling";
pub const R_SPLIT_ASK: &str = "abysspact_leech_r_split";
pub const R_SWARM_BUFF: &str = "abysspact_leech_swarm";
pub const R_CAST_VOICE: &str = "abysspact_leech_r_voice";
/// 小水蛭的弹道图（数据 view_projectiles 的 r_mini），打中时什么都不做的原生效果。
pub const MINI_PROJ: &str = "abysspact_leech_r_mini";
pub const NOOP: &str = "abysspact_leech:noop";

pub const ATTACH_TICKS: usize = 180; // 3.0s
pub const JUMP_TICKS: usize = 120; // 2.0s on host death jump
pub const JUMP_RANGE: u64 = 50_000; // 5.0万
pub const DRAIN_PERIOD: usize = 30; // 0.5s
pub const DRAIN_PCT_X10: usize = 25; // 2.5% max HP per 0.5s
pub const SHARED_PAIN_PCT: usize = 25; // 25% of host's external damage
pub const SWARM_RANGE: u64 = 90_000; // 9.0万
pub const SWARM_TICKS: usize = 180; // 3.0s
pub const SWARM_DRAIN_PCT: usize = 2; // 2% max HP per 0.5s per leech
pub const SWARM_SHARED_PCT: usize = 10; // 10% shared pain per host
pub const SWARM_LEECHES: usize = 5;
/// 一个人身上最多几只小水蛭。
pub const MAX_PER_HOST: usize = 2;
pub const MINI_SPEED: u64 = 8_200;
/// 贴在宿主背后：横着离多远、往屏幕上方挪多少（画在宿主身后）；差得不多就不挪。
pub const FOLLOW_BACK: f64 = 3_500.0;
pub const FOLLOW_LIFT: f64 = 1_500.0;
pub const FOLLOW_SLACK: f64 = 600.0;
/// 放逐到点后最多再等几 tick 让他出来。
pub const OUT_GRACE: usize = 5;

pub fn drain_amount(host_max_hp: usize) -> usize {
    host_max_hp.saturating_mul(DRAIN_PCT_X10) / 1000
}

pub fn shared_pain(host_lost: usize, pct: usize) -> usize {
    host_lost.saturating_mul(pct) / 100
}

/// 魔法伤害打到身上大约掉多少血（按 100 / (100 + 魔抗)）。
pub fn mitigated(amount: usize, mr: usize) -> usize {
    amount.saturating_mul(100) / (100 + mr)
}

/// 附骨之疽按 tick 攒着算（单位：百分之一点生命），攒够 4 点才扣一次，返回这次扣几点。
pub fn pay_pain(owed: &mut usize, lost: usize, pct: usize) -> usize {
    *owed = owed.saturating_add(lost.saturating_mul(pct));
    if *owed >= 400 {
        let pain = *owed / 100;
        *owed %= 100;
        pain
    } else {
        0
    }
}

/// 5 只小水蛭分给宿主（已经按生命从少到多排好）：每人一只，多出来的先给血最少的，一个人最多 `cap` 只。
pub fn split_leeches(hosts: usize, total: usize, cap: usize) -> Vec<usize> {
    let n = hosts.min(total);
    let mut counts = vec![1; n];
    let mut extra = total.saturating_sub(n);
    for c in counts.iter_mut() {
        while extra > 0 && *c < cap {
            *c += 1;
            extra -= 1;
        }
    }
    counts
}

fn force_move(sim: &mut StableSim<'_>, id: usize, delta: (f64, f64), ticks: u64) {
    let d = (delta.0 * delta.0 + delta.1 * delta.1).sqrt();
    let ticks = ticks.max(1);
    let mut cc = CcV1::of_kind(CcKindV1::ForceMove, ticks);
    cc.dx = delta.0.round() as i64;
    cc.dy = delta.1.round() as i64;
    cc.speed = ((d / ticks as f64).ceil() as u64).max(1);
    sim.apply_cc(id, &cc);
}

fn mini_spec(entity: usize, team: usize, from: (u64, u64), to: (u64, u64), host: Option<usize>) -> ProjectileSpawnV1 {
    ProjectileSpawnV1 {
        caster_id: entity,
        team,
        x: from.0,
        y: from.1.saturating_sub(9_000),
        radius: 1_000,
        speed: MINI_SPEED,
        move_kind: if host.is_some() { ProjectileMoveKindV1::Target } else { ProjectileMoveKindV1::Linear }.code(),
        target_id: host.unwrap_or(0),
        target_x: to.0,
        target_y: to.1.saturating_sub(9_000),
        penetrate: true,
        attack_type: AttackTypeV1::Skill.code(),
        casting_type: if host.is_some() { CastingTypeV1::Targeting } else { CastingTypeV1::Position }.code(),
        casting_target: if host.is_some() { CastingTargetV1::EnemyChampion } else { CastingTargetV1::None }.code(),
    }
}

#[derive(Clone, Copy)]
struct HostAttach {
    host_id: usize,
    end_tick: usize,
    next_drain: usize,
    last_host_hp: usize,
    jumped: bool,
    /// 宿主背后在哪一边：-1 左边、+1 右边（宿主往右走，背后就在左边）。
    back: f64,
    last_host_pos: (u64, u64),
}

#[derive(Clone)]
struct SwarmState {
    /// (宿主, 身上几只小水蛭, 上一 tick 宿主的生命)
    hosts: Vec<(usize, usize, usize)>,
    end_tick: usize,
    next_drain: usize,
    banked_heal: usize,
    /// 他放逐时站的地方（小水蛭飞回来的地方）。
    home: (u64, u64),
}

#[derive(Clone, Default)]
struct LeechPassive {
    voice: Voice,
    attach: Option<HostAttach>,
    swarm: Option<SwarmState>,
    /// 攒着还没扣的附骨之疽（百分之一点生命）。
    owed: usize,
}

impl LeechPassive {
    fn clear_attach(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if let Some(a) = self.attach.take() {
            sim.entity_remove_buff(a.host_id, HOST_MARK);
        }
        sim.entity_remove_buff(entity, ATTACHED_BUFF);
    }

    fn clear_swarm(&mut self, sim: &mut StableSim<'_>, entity: usize) {
        if let Some(sw) = self.swarm.take() {
            for &(hid, _, _) in &sw.hosts {
                sim.entity_remove_buff(hid, MINI_CLING);
            }
        }
        sim.entity_remove_buff(entity, R_SWARM_BUFF);
    }

    fn start_attach(&mut self, sim: &mut StableSim<'_>, entity: usize, host_id: usize, dur: usize, jumped: bool) {
        let Some((host_hp, host_pos)) = sim.get_entity(host_id).filter(|e| e.is_alive()).map(|e| (e.hp().0, e.pos()))
        else {
            return;
        };
        let my_x = sim.get_entity(entity).map_or(host_pos.0, |e| e.pos().0);
        let tick = sim.tick();
        self.owed = 0;
        self.attach = Some(HostAttach {
            host_id,
            end_tick: tick + dur,
            next_drain: tick + DRAIN_PERIOD,
            last_host_hp: host_hp,
            jumped,
            // 从哪边扑上来就先挂在哪边
            back: if my_x > host_pos.0 { 1.0 } else { -1.0 },
            last_host_pos: host_pos,
        });
        // 伤害减为 0；不免控：强制位移要能挪得动他
        let mut att = BuffV1::timed(ATTACHED_BUFF, dur);
        att.damaged_reduce = 100;
        sim.entity_remove_buff(entity, ATTACHED_BUFF);
        sim.add_buff(entity, &att);

        let mut hm = BuffV1::timed(HOST_MARK, dur);
        hm.move_speed_mult = -30;
        sim.entity_remove_buff(host_id, HOST_MARK);
        sim.add_buff(host_id, &hm);
    }

    /// 宿主挨的打跟着疼。疼死了就从背上掉下来，算 `source`（宿主）打死的。返回他还挂不挂得住。
    fn suffer(&mut self, sim: &mut StableSim<'_>, entity: usize, source: usize, pain: usize) -> bool {
        let Some(cur) = sim.get_entity(entity).filter(|e| e.is_alive()).map(|e| e.hp().0) else {
            return false;
        };
        sim.play_view_effect("abysspact_leech_shared_hit", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_leech_shared_pain", entity, &InputTargetV1::target(entity));
        if pain < cur {
            sim.entity_set_hp(entity, cur - pain);
            return true;
        }
        self.clear_attach(sim, entity);
        sim.entity_remove_buff(entity, R_SWARM_BUFF);
        sim.entity_set_hp(entity, 1);
        sim.deal_damage_typed(source, entity, pain, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        false
    }

    /// 宿主一动就把他挪到宿主背后（一 tick 的强制位移，画面跟着走）。
    fn follow(sim: &mut StableSim<'_>, entity: usize, att: &mut HostAttach, host_pos: (u64, u64)) {
        let dx = host_pos.0 as f64 - att.last_host_pos.0 as f64;
        if dx.abs() > 200.0 {
            att.back = if dx > 0.0 { -1.0 } else { 1.0 };
        }
        att.last_host_pos = host_pos;
        let Some(me) = sim.get_entity(entity).map(|e| e.pos()) else { return };
        let want = (host_pos.0 as f64 + att.back * FOLLOW_BACK, (host_pos.1 as f64 - FOLLOW_LIFT).max(0.0));
        let d = (want.0 - me.0 as f64, want.1 - me.1 as f64);
        if (d.0 * d.0 + d.1 * d.1).sqrt() > FOLLOW_SLACK {
            force_move(sim, entity, d, 1);
        }
    }

    fn start_swarm(&mut self, sim: &mut StableSim<'_>, entity: usize, my_team: usize, my_pos: (u64, u64)) {
        self.clear_attach(sim, entity);
        let r2 = SWARM_RANGE * SWARM_RANGE;
        let mut foes: Vec<(usize, usize)> = Vec::new();
        for i in 0..sim.entity_count() {
            let Some(e) = sim.entity_at(i) else { continue };
            if e.is_champion() && e.is_alive() && e.is_targetable() && e.team() != my_team && dist_sq(my_pos, e.pos()) <= r2 {
                foes.push((e.id(), e.hp().0));
            }
        }
        if foes.is_empty() {
            return;
        }
        // 血最少的排前面：多出来的小水蛭先扑他们，一个人最多两只
        foes.sort_by_key(|&(id, hp)| (hp, id));
        let counts = split_leeches(foes.len(), SWARM_LEECHES, MAX_PER_HOST);
        let hosts: Vec<(usize, usize, usize)> = foes.iter().zip(&counts).map(|(&(id, hp), &n)| (id, n, hp)).collect();
        let tick = sim.tick();
        // 先放小水蛭（放逐以后他放不出弹道），每只一发
        for &(hid, n, _) in &hosts {
            let to = sim.get_entity(hid).map_or(my_pos, |e| e.pos());
            for _ in 0..n {
                sim.spawn_projectile(MINI_PROJ, NOOP, &mini_spec(entity, my_team, my_pos, to, Some(hid)));
            }
            sim.add_buff(hid, &BuffV1::timed(MINI_CLING, SWARM_TICKS));
        }
        sim.play_view_effect("abysspact_leech_split", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_leech_split", entity, &InputTargetV1::target(entity));
        // 他本人不在场上：放逐 3 秒（看不见、选不中、不能动作）
        let mut sw = BuffV1::timed(R_SWARM_BUFF, SWARM_TICKS);
        sw.damaged_reduce = 100;
        sim.add_buff(entity, &sw);
        sim.entity_banish(entity, entity, SWARM_TICKS, "", "");

        self.swarm = Some(SwarmState {
            hosts,
            end_tick: tick + SWARM_TICKS,
            next_drain: tick + DRAIN_PERIOD,
            banked_heal: 0,
            home: my_pos,
        });
    }

    /// 万蛭结束：小水蛭从每个宿主飞回来聚成他，吸到的血全部治疗他。
    fn end_swarm(&mut self, sim: &mut StableSim<'_>, entity: usize, my_team: usize, sw: SwarmState) {
        for &(hid, _, _) in &sw.hosts {
            sim.entity_remove_buff(hid, MINI_CLING);
            if let Some(from) = sim.get_entity(hid).filter(|e| e.is_alive()).map(|e| e.pos()) {
                sim.spawn_projectile(MINI_PROJ, NOOP, &mini_spec(entity, my_team, from, sw.home, None));
            }
        }
        sim.entity_remove_buff(entity, R_SWARM_BUFF);
        if sw.banked_heal > 0 {
            sim.heal(entity, entity, sw.banked_heal);
        }
        sim.play_view_effect("abysspact_leech_rejoin", entity, &InputTargetV1::target(entity), 0, 0, 0);
        sim.play_sfx("abysspact_leech_rejoin", entity, &InputTargetV1::target(entity));
    }
}

impl StablePassive for LeechPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        self.attach = None;
        self.swarm = None;
        self.owed = 0;
        self.voice.on_spawn(sim, HERO, entity);
    }

    fn on_attack(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, target: usize, _damage: &mut usize) {
        if sim.get_entity(target).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Start);
        }
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, victim: usize) {
        if sim.get_entity(victim).is_some_and(|e| e.is_champion()) {
            self.voice.play(sim, HERO, entity, Cue::Kill);
        }
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, player: usize) {
        // 他倒下：宿主身上的减速、小水蛭标记当场摘掉
        if let Some(a) = self.attach.take() {
            sim.entity_remove_buff(a.host_id, HOST_MARK);
        }
        if let Some(sw) = self.swarm.take() {
            for &(hid, _, _) in &sw.hosts {
                sim.entity_remove_buff(hid, MINI_CLING);
            }
        }
        self.owed = 0;
        self.voice.on_dead(sim, HERO, player);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _rng: u64, _player: usize, entity: usize) {
        let Some((alive, my_team, my_pos, targetable)) = sim
            .get_entity(entity)
            .map(|e| (e.is_alive(), e.team(), e.pos(), e.is_targetable()))
        else {
            return;
        };
        if !alive {
            self.clear_attach(sim, entity);
            self.clear_swarm(sim, entity);
            return;
        }
        let tick = sim.tick();
        if !has_buff(sim, entity, NATIVE_MARK) {
            sim.add_buff(entity, &BuffV1::named(NATIVE_MARK));
        }
        if consume_buff(sim, entity, R_CAST_VOICE) {
            self.voice.play(sim, HERO, entity, Cue::Ult);
        }

        // 1. R「万蛭」
        if consume_buff(sim, entity, R_SPLIT_ASK) {
            self.start_swarm(sim, entity, my_team, my_pos);
        }

        // 2. 万蛭进行中
        if let Some(mut sw) = self.swarm.take() {
            if tick >= sw.end_tick && (targetable || tick >= sw.end_tick + OUT_GRACE) {
                self.end_swarm(sim, entity, my_team, sw);
                return;
            }
            let do_drain = tick < sw.end_tick && tick >= sw.next_drain;
            if do_drain {
                sw.next_drain = tick + DRAIN_PERIOD;
            }
            let mut total_pain = 0usize;
            let mut source = None;
            for (hid, cnt, last_hp) in &mut sw.hosts {
                let Some((h_alive, cur_hp, max_hp, mr)) = sim
                    .get_entity(*hid)
                    .map(|e| (e.is_alive(), e.hp().0, e.hp().1, e.stat().magic_resistance))
                else {
                    continue;
                };
                if !h_alive {
                    continue;
                }
                let lost = (*last_hp).saturating_sub(cur_hp);
                if lost > 0 {
                    total_pain = total_pain.saturating_add(lost);
                    source = Some(*hid);
                }
                let mut expect = 0;
                if do_drain {
                    let amt = max_hp.saturating_mul(SWARM_DRAIN_PCT * (*cnt)) / 100;
                    if amt > 0 {
                        sim.deal_damage_typed(entity, *hid, amt, DamageTypeV1::Ap, AttackTypeV1::Skill);
                        sw.banked_heal = sw.banked_heal.saturating_add(amt);
                        expect = mitigated(amt, mr);
                        sim.play_view_effect("abysspact_leech_drain", entity, &InputTargetV1::target(*hid), 0, 0, 0);
                    }
                }
                // 自己吸的那一口下一 tick 才扣：先从记下的血量里扣掉，不算进附骨之疽
                *last_hp = cur_hp.saturating_sub(expect);
            }
            let pain = pay_pain(&mut self.owed, total_pain, SWARM_SHARED_PCT);
            let still = pain == 0 || self.suffer(sim, entity, source.unwrap_or(entity), pain);
            if still && sim.get_entity(entity).is_some_and(|e| e.is_alive()) {
                self.swarm = Some(sw);
            } else {
                // 疼死了：小水蛭散了，吸到的血也不回
                for &(hid, _, _) in &sw.hosts {
                    sim.entity_remove_buff(hid, MINI_CLING);
                }
            }
            return;
        }

        // 3. Q「扑附」：数据在敌方英雄身上挂了 attach_ask
        if self.attach.is_none() {
            let mut target = None;
            for i in 0..sim.entity_count() {
                let Some(e) = sim.entity_at(i) else { continue };
                if e.is_champion() && e.is_alive() && e.team() != my_team && has_buff(sim, e.id(), ATTACH_ASK) {
                    target = Some(e.id());
                    break;
                }
            }
            if let Some(hid) = target {
                sim.entity_remove_buff(hid, ATTACH_ASK);
                self.start_attach(sim, entity, hid, ATTACH_TICKS, false);
            }
        }

        // 4. 附着中：贴在背后、吸血、附骨之疽、宿主死了跳下一个
        if let Some(mut att) = self.attach {
            let host = sim
                .get_entity(att.host_id)
                .map(|e| (e.is_alive(), e.pos(), e.hp().0, e.hp().1, e.stat().magic_resistance));
            match host {
                Some((true, hpos, cur_hp, max_hp, mr)) if tick < att.end_tick => {
                    Self::follow(sim, entity, &mut att, hpos);
                    let lost = att.last_host_hp.saturating_sub(cur_hp);
                    let pain = pay_pain(&mut self.owed, lost, SHARED_PAIN_PCT);
                    if pain > 0 && !self.suffer(sim, entity, att.host_id, pain) {
                        return;
                    }
                    let mut expect = 0;
                    if tick >= att.next_drain {
                        att.next_drain = tick + DRAIN_PERIOD;
                        let amt = drain_amount(max_hp);
                        if amt > 0 {
                            sim.deal_damage_typed(entity, att.host_id, amt, DamageTypeV1::Ap, AttackTypeV1::Skill);
                            sim.heal(entity, entity, amt);
                            expect = mitigated(amt, mr);
                            sim.play_view_effect("abysspact_leech_drain", entity, &InputTargetV1::target(att.host_id), 0, 0, 0);
                            sim.play_sfx("abysspact_leech_drain", entity, &InputTargetV1::target(att.host_id));
                        }
                    }
                    // 自己吸的那一口下一 tick 才扣：先从记下的血量里扣掉，不算进附骨之疽
                    att.last_host_hp = cur_hp.saturating_sub(expect);
                    self.attach = Some(att);
                }
                Some((false, dead_pos, _, _, _)) if !att.jumped => {
                    // 宿主死了：跳到 5 万内最近的另一个敌方英雄身上再附 2 秒
                    self.clear_attach(sim, entity);
                    let r2 = JUMP_RANGE * JUMP_RANGE;
                    let mut next_host: Option<(usize, u64)> = None;
                    for i in 0..sim.entity_count() {
                        let Some(e) = sim.entity_at(i) else { continue };
                        if e.is_champion() && e.is_alive() && e.is_targetable() && e.team() != my_team {
                            let d2 = dist_sq(dead_pos, e.pos());
                            if d2 <= r2 && next_host.is_none_or(|(_, best)| d2 < best) {
                                next_host = Some((e.id(), d2));
                            }
                        }
                    }
                    if let Some((nh, _)) = next_host {
                        sim.play_view_effect("abysspact_leech_jump", entity, &InputTargetV1::target(nh), 0, 0, 0);
                        sim.play_sfx("abysspact_leech_jump", entity, &InputTargetV1::target(nh));
                        self.start_attach(sim, entity, nh, JUMP_TICKS, true);
                    }
                }
                _ => {
                    self.clear_attach(sim, entity);
                }
            }
        }
    }
}

/// 附着时 W「蚀髓」的射程 +2.5 万，背上的宿主总够得着。
#[derive(Debug)]
struct AttachedWRange;

impl StableEffectType for AttachedWRange {
    fn apply(&self, _sim: &mut StableSim<'_>, _seed: u64, _caster: usize, _input: InputTargetV1) {}
    fn may_adjust_range(&self) -> bool {
        true
    }
    fn range_adjust(&self, caster: &StableEntityView<'_>, _target: &StableEntityView<'_>) -> u64 {
        if caster.has_buff(ATTACHED_BUFF) { 25_000 } else { 0 }
    }
}

/// 小水蛭弹道打中时什么都不做（吸血在被动里算）。
#[derive(Debug)]
struct Noop;

impl StableEffectType for Noop {
    fn apply(&self, _sim: &mut StableSim<'_>, _seed: u64, _caster: usize, _input: InputTargetV1) {}
}

pub fn register(_host: &StableHost, module: &mut StableMod) {
    module.add_native_passive("abysspact_leech:parasite", LeechPassive::default());
    module.add_native_effect("abysspact_leech:w_range", AttachedWRange);
    module.add_native_effect(NOOP, Noop);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn drain_and_shared_pain_math() {
        assert_eq!(drain_amount(2000), 50);
        assert_eq!(shared_pain(400, SHARED_PAIN_PCT), 100);
        assert_eq!(shared_pain(400, SWARM_SHARED_PCT), 40);
    }

    #[test]
    fn pain_is_paid_from_every_tick() {
        // 宿主连着 6 tick 各掉 10 点：25% 一共 15 点，一点不少（以前只算三分之一）
        let mut owed = 0;
        let paid: usize = (0..6).map(|_| pay_pain(&mut owed, 10, SHARED_PAIN_PCT)).sum();
        assert_eq!(paid + owed / 100, 15);
        assert!(owed < 100);
    }

    #[test]
    fn five_leeches_two_at_most_on_one_host() {
        assert_eq!(split_leeches(1, SWARM_LEECHES, MAX_PER_HOST), vec![2]);
        assert_eq!(split_leeches(2, SWARM_LEECHES, MAX_PER_HOST), vec![2, 2]);
        assert_eq!(split_leeches(3, SWARM_LEECHES, MAX_PER_HOST), vec![2, 2, 1]);
        assert_eq!(split_leeches(5, SWARM_LEECHES, MAX_PER_HOST), vec![1, 1, 1, 1, 1]);
        assert_eq!(split_leeches(7, SWARM_LEECHES, MAX_PER_HOST), vec![1, 1, 1, 1, 1]);
        assert!(split_leeches(0, SWARM_LEECHES, MAX_PER_HOST).is_empty());
    }

    #[test]
    fn own_drain_is_not_counted_as_pain() {
        // 吸了 50（魔抗 25 -> 掉 40）：记下的血先扣 40，下一 tick 宿主真掉了 40，算出来 0
        let expect = mitigated(50, 25);
        assert_eq!(expect, 40);
        let last = 1_000 - expect;
        assert_eq!(shared_pain(last - (1_000 - 40), SHARED_PAIN_PCT), 0);
    }
}
