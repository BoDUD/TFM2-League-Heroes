//! 乙骨忧太（Yuta）+ 里香（Rika）。
//!
//! 数据层负责：普攻五层强化形态、技能一突进减速、技能二范围伤害、
//! 大招五段光速；native 侧负责：
//! - A~E 咒力标记：独立计时（死亡暂停），全局单一 LIFO 栈（最近获得先打出），
//!   标记栈保存在 Rust 侧，死亡不清、复活时按栈重建 buff
//! - F 标记与永久召唤物里香：自动召唤、阵亡 5 秒后返还 F
//! - 里香面板固定为乙骨当前等级基础面板 ×2（出生定死，存活期不再动态更新）
//! - 噬魂成长：乙骨每次击杀/助攻，乙骨与里香基础属性各 +10%（永久叠加）
//! - 里香战斗 AI：普攻周期回血（过量转永久护盾）、8 秒一次击飞强化普攻
//! - 乙骨暴击光环 +50%（里香在场）
//! - 技能/强化普攻附带里香最大生命 10% 真伤（在 native 命中点同步结算）
//! - 技能二禁锢、强化普攻三突进五连（位移走数据层 Rush 节点）、
//!   大招碎盾/削双抗/封技、里香原生 banish 退场
//!
//! 稳定性铁律（对照 kirito / necoarc / sungjinwoo 三个稳定 mod）：
//! 位移一律走数据层 Rush，绝不在 native 里 entity_set_pos；不使用
//! queue_effect；击杀成长用 on_kill/on_assist 回调而非轮询击杀日志。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "yuta";

// ---------------- 调试日志（定位崩溃用，每次写盘 flush） ----------------

const DEBUG_LOG: &str = r"E:\新建文件夹\yuta_debug.log";

fn dlog(msg: impl AsRef<str>) {
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(DEBUG_LOG) {
        let _ = writeln!(f, "[yuta] {}", msg.as_ref());
        let _ = f.flush();
    }
}

// ---------------- 标记 ----------------

const MARK_NAMES: [&str; 5] = [
    "yuta_mark_a",
    "yuta_mark_b",
    "yuta_mark_c",
    "yuta_mark_d",
    "yuta_mark_e",
];
const NEXT_NAMES: [&str; 5] = [
    "yuta_next_a",
    "yuta_next_b",
    "yuta_next_c",
    "yuta_next_d",
    "yuta_next_e",
];
/// 各标记获取周期（tick）：A 6s / B 12s / C 8s / D 9s / E 9s。
const MARK_PERIODS: [usize; 5] = [360, 720, 480, 540, 540];
const MARK_CAP: usize = 99;
const F_MARK: &str = "yuta_f_mark";

/// 标记 LIFO 栈，按英雄实体 id 存于 Rust 侧（引擎死亡会清空实体 buff）。
static STACKS: LazyLock<Mutex<HashMap<usize, Vec<u8>>>> =
    LazyLock::new(|| Mutex::new(HashMap::new()));

fn with_stack<R>(eid: usize, f: impl FnOnce(&mut Vec<u8>) -> R) -> R {
    // PoisonError::into_inner：即使此前回调 panic 过也继续可用，避免连锁崩溃。
    let mut map = STACKS.lock().unwrap_or_else(|e| e.into_inner());
    f(map.entry(eid).or_default())
}

// ---------------- 噬魂成长（击杀/助攻 +10% 基础属性） ----------------

const GROWTH_BUFF: &str = "yuta_growth";
/// 每层 +10%：攻击/法强/护甲/生命/魔抗（同名 buff 按层叠加）。
const GROWTH_MULT: i32 = 10;

/// 每个乙骨的成长层数（引擎死亡会清 buff，故真值存 Rust 侧）。
static GROWTH: LazyLock<Mutex<HashMap<usize, u32>>> =
    LazyLock::new(|| Mutex::new(HashMap::new()));

fn with_growth<R>(eid: usize, f: impl FnOnce(&mut u32) -> R) -> R {
    let mut map = GROWTH.lock().unwrap_or_else(|e| e.into_inner());
    f(map.entry(eid).or_insert(0))
}

/// 一层成长 buff（永久，同名按层叠加，引擎负责属性换算）。
fn growth_buff_layer() -> BuffV1 {
    let mut b = BuffV1::named(GROWTH_BUFF);
    b.attack_mult = GROWTH_MULT;
    b.magic_power_mult = GROWTH_MULT;
    b.defence_mult = GROWTH_MULT;
    b.hp_mult = GROWTH_MULT;
    b.magic_resistance_mult = GROWTH_MULT;
    b
}

/// 给实体补挂一层成长（max_stacks=0 不限层；refresh 只续时间，层数照加）。
fn growth_push(sim: &mut StableSim<'_>, eid: usize) {
    sim.entity_stack_buff(eid, &growth_buff_layer(), 0, true);
}

/// 出生/复活：按记录层数重建成长 buff。
fn growth_rebuild(sim: &mut StableSim<'_>, eid: usize) {
    let n = with_growth(eid, |n| *n);
    for _ in 0..n {
        growth_push(sim, eid);
    }
}

// ---------------- 里香 ----------------

const RIKA_UNIT: &str = "yuta_summon";
/// 里香归属标记：必须用固定静态名，绝不能按实体 id 现场 format! 出动态名——
/// 动态 buff 名会在引擎侧反复注册/在跨局复用的实体 id 上残留，收场时崩溃。
const RIKA_TAG: &str = "yuta_rika_tag";
/// 里香存活时长。反汇编稳定 mod（sungjinwoo）实测：它的常驻自由移动召唤物
/// spawn_unit 的 duration 传的就是 0x5f5e100=100_000_000 tick（近永久），且连开
/// 多局从不崩——证明引擎收场会安全回收召唤单位及其永久标记 buff。直接沿用同一值，
/// 不自己发明（此前的 432000/30000 都是想当然）。自然死亡时大脑仍按 5 秒复活重召。
const RIKA_DURATION: u64 = 100_000_000;
const RIKA_RESPAWN_TICKS: usize = 300; // 阵亡 5 秒后返还 F
const RIKA_RANGE: u64 = 16_000;
const RIKA_SATK_TICKS: usize = 480; // 8 秒攒一个自身强化普攻
const RIKA_LIFESTEAL_PCT: usize = 5; // 普攻周期回最大生命 5%
const RIKA_SATK_HEAL_PCT: usize = 3;
const RIKA_SATK_DAMAGE_BASE: usize = 40;
const RIKA_SATK_AD_RATIO: usize = 35;
/// 强化普攻动画总时长约 62 tick（fanim 6 帧 0.333+0.033+0.033+0.067+0.5+0.067）。
/// 播放期间把里香本体隐身，避免场上同时出现「本体 + 一个做攻击动作的里香特效」
/// 两个里香；动画播完隐身到期本体恢复（期间敌人也无法选中她，等同一次突进斩）。
const RIKA_SATK_HIDE_TICKS: usize = 62;
const RIKA_LINK_TRUE_PCT: usize = 10; // 技能附带里香最大生命 10% 真伤
/// 过量治疗转成的护盾【持续时长】。这是关键安全值：护盾是独立于 buff 的组件，带
/// 自己的到期定时器；若时长长到对局结束仍未到期（旧值 600000/30000 都远大于单局
/// ~5271 tick），收场时召唤物身上就挂着未触发的护盾定时器，连开第二场引擎复用实体
/// 槽位时双重释放→无 panic 闪退。取 420 tick（7 秒）：实测战斗最后一次护盾在 3031、
/// 收场 is_end 在 5271，间隔 2240 tick（37 秒），护盾早在收场前自然到期；过量回血在
/// 无盾时会重新补一个，「过量转盾」玩法不变（同时也修掉了旧版护盾近乎永久的问题）。
const RIKA_SHIELD_TICKS: usize = 420;

const RIKA_SATK_FX: [&str; 5] = [
    "yuta_fx_rika_30001",
    "yuta_fx_rika_30100",
    "yuta_fx_rika_30118",
    "yuta_fx_rika_30117",
    "yuta_fx_rika_30101",
];

// ---------------- 乙骨基础面板（必须与 data_champion 一致） ----------------

const BASE_ATTACK: usize = 75;
const BASE_HP: usize = 1100;
const BASE_DEF: usize = 34;
const BASE_MR: usize = 32;
const BASE_MS: usize = 1050;
const BASE_REGEN: usize = 4;
const BASE_CRIT: usize = 10;
const GROW_ATTACK: usize = 9;
const GROW_HP: usize = 105;
const GROW_DEF: usize = 4;
const GROW_MR: usize = 3;
const GROW_MS: usize = 6;
const GROW_REGEN: usize = 1;

const CRIT_AURA: &str = "yuta_crit_aura";

// ---------------- 技能数值 ----------------

const S2_BIND_TICKS: u64 = 90;
const ULT_DEBUFF_TICKS: usize = 300;
const ULT_RESIST_DOWN: i32 = -65; // 削减 65%（剩 35%）
const ULT_BLOCK_TICKS: u64 = 300;
const ULT_BANISH_TICKS: usize = 90;

const ATK3_SEGMENTS: usize = 5;
const ATK3_SEG_BASE: usize = 18;
const ATK3_SEG_AD: usize = 18;
const ATK3_HEAL: usize = 120;

// ===================== 通用查询 =====================

/// 里香联动真伤：里香在场时，对存活的非建筑目标造成里香最大生命 10% 固定伤害。
///
/// 直接在 native 命中回调里同步结算。Fixed 真伤走完整伤害管线是安全用法
/// （稳定 mod 桐人即在 native 命中点同步打 Fixed，甚至按当前血量斩杀）。
/// 真正会破坏引擎状态的是 entity_set_pos / queue_effect，二者已全部移除。
fn rika_true_strike(sim: &mut StableSim<'_>, caster: usize, target: usize) {
    let Some(t) = sim.get_entity(target) else {
        return;
    };
    if !t.is_alive() || t.is_tower() {
        return;
    }
    let Some(rid) = find_rika(sim, caster) else {
        return;
    };
    let max_hp = sim.get_entity(rid).map(|e| e.hp().1).unwrap_or(0);
    if max_hp > 0 {
        sim.deal_damage_typed(
            caster,
            target,
            max_hp * RIKA_LINK_TRUE_PCT / 100,
            DamageTypeV1::Fixed,
            AttackTypeV1::Skill,
        );
    }
}

fn has_buff_named(e: &StableEntity<'_, '_>, name: &str) -> bool {
    for i in 0..e.buff_count() {
        if let Some(b) = e.buff_at(i) {
            if b.name() == name {
                return true;
            }
        }
    }
    false
}

/// 按召唤时打上的归属标记找里香（固定静态 buff 名）。
fn find_rika(sim: &StableSim<'_>, _owner: usize) -> Option<usize> {
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.is_alive() && has_buff_named(&e, RIKA_TAG) {
            return Some(e.id());
        }
    }
    None
}

fn mark_count(sim: &StableSim<'_>, eid: usize, name: &str) -> usize {
    let mut n = 0;
    if let Some(e) = sim.get_entity(eid) {
        for i in 0..e.buff_count() {
            if let Some(b) = e.buff_at(i) {
                if b.name() == name {
                    n += 1;
                }
            }
        }
    }
    n
}

/// 最近敌人；`max_radius` 为 None 时全图索敌（不含防御塔）。
fn nearest_enemy(sim: &StableSim<'_>, eid: usize, max_radius: Option<u64>) -> Option<usize> {
    let c = sim.get_entity(eid)?;
    let (cx, cy) = c.pos();
    let team = c.team();
    let cap2 = max_radius.map(|r| r.saturating_mul(r));
    let mut best = None;
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.team() == team || !e.is_alive() || e.is_tower() {
            continue;
        }
        let (ex, ey) = e.pos();
        let dx = ex as i64 - cx as i64;
        let dy = ey as i64 - cy as i64;
        let d2 = (dx * dx + dy * dy) as u64;
        if let Some(m2) = cap2 {
            if d2 > m2 {
                continue;
            }
        }
        if best.map_or(true, |(_, bd)| d2 < bd) {
            best = Some((e.id(), d2));
        }
    }
    best.map(|(id, _)| id)
}

// ===================== 标记栈（LIFO） =====================

/// 按实体当前挂着的 mark buff，重算唯一的 next 指针（最近添加者）。
fn sync_next(sim: &mut StableSim<'_>, eid: usize) {
    let mut last: Option<usize> = None;
    let mut last_idx: usize = 0;
    if let Some(e) = sim.get_entity(eid) {
        for i in 0..e.buff_count() {
            if let Some(b) = e.buff_at(i) {
                if let Some(k) = MARK_NAMES.iter().position(|n| *n == b.name()) {
                    if last.is_none() || i >= last_idx {
                        last = Some(k);
                        last_idx = i;
                    }
                }
            }
        }
    }
    for n in NEXT_NAMES {
        sim.entity_remove_buff(eid, n);
    }
    if let Some(k) = last {
        sim.add_buff(eid, &BuffV1::named(NEXT_NAMES[k]));
    }
}

fn stack_grant(sim: &mut StableSim<'_>, eid: usize, ty: usize) {
    let full = with_stack(eid, |st| st.len() >= MARK_CAP);
    if full {
        return;
    }
    with_stack(eid, |st| st.push(ty as u8));
    sim.add_buff(eid, &BuffV1::named(MARK_NAMES[ty]));
    sync_next(sim, eid);
}

/// 打出一个指定类型标记：buff 层删一份（引擎 remove 清同名全部，补挂剩余），
/// Rust 栈层弹出最近的一个同类型。
fn stack_consume(sim: &mut StableSim<'_>, eid: usize, ty: usize) {
    let cur = mark_count(sim, eid, MARK_NAMES[ty]);
    if cur > 0 {
        sim.entity_remove_buff(eid, MARK_NAMES[ty]);
        for _ in 0..cur - 1 {
            sim.add_buff(eid, &BuffV1::named(MARK_NAMES[ty]));
        }
    }
    with_stack(eid, |st| {
        if let Some(pos) = st.iter().rposition(|m| *m as usize == ty) {
            st.remove(pos);
        }
    });
    sync_next(sim, eid);
}

/// 出生/复活：按 Rust 栈重建全部 mark buff（引擎死亡已清空实体 buff）。
fn stack_rebuild(sim: &mut StableSim<'_>, eid: usize) {
    let marks = with_stack(eid, |st| st.clone());
    for &ty in &marks {
        sim.add_buff(eid, &BuffV1::named(MARK_NAMES[ty as usize]));
    }
    sync_next(sim, eid);
}

// ===================== 里香大脑（全局状态，由 MatchHook 驱动） =====================
//
// 关键架构（对照稳定 mod sungjinwoo / necoarc）：一切「每帧遍历世界、召唤、
// 治疗、造成伤害」的逻辑都必须在 StableMatchHook::on_match_tick（核心世界 tick
// 与输入阶段结束后的安全点）里做，绝不能放进 StablePassive::on_update——后者
// 运行在引擎逐实体更新/战斗迭代中途，此时 spawn_unit / deal_damage / heal 等
// 会改变世界实体集合，破坏引擎内部迭代，表现为无 panic、爆点漂移的随机闪退。
// 召唤物流的 sjw 正是用 on_match_tick 管理召唤物。

/// 每个乙骨的运行时状态，按英雄实体 id 存全局；只在 on_match_tick 内短暂取出使用。
#[derive(Clone)]
struct YutaBrain {
    /// 各标记剩余获取计时（死亡期间不递减）。
    timers: [usize; 5],
    rika: Option<usize>,
    respawn: usize,
    /// 开局世界未稳定前延迟召唤（tick）。
    spawn_delay: usize,
    next_heal: usize,
    satk: usize,
}

impl Default for YutaBrain {
    fn default() -> Self {
        Self::fresh()
    }
}

/// 大脑表：英雄实体 id -> 大脑。passive on_spawn 负责登记，MatchHook 负责推进。
static BRAINS: LazyLock<Mutex<HashMap<usize, YutaBrain>>> =
    LazyLock::new(|| Mutex::new(HashMap::new()));

fn brains_lock<R>(f: impl FnOnce(&mut HashMap<usize, YutaBrain>) -> R) -> R {
    let mut map = BRAINS.lock().unwrap_or_else(|e| e.into_inner());
    f(&mut map)
}

impl YutaBrain {
    fn fresh() -> Self {
        Self {
            timers: MARK_PERIODS,
            rika: None,
            respawn: 0,
            spawn_delay: 30,
            next_heal: 0,
            satk: RIKA_SATK_TICKS,
        }
    }

    /// 乙骨当前等级基础面板（必须与 data_champion 的 stat/growth 一致）。
    fn base_stat(level: usize) -> StatV1 {
        let g = level.saturating_sub(1);
        StatV1 {
            attack: BASE_ATTACK + GROW_ATTACK * g,
            magic_power: 0,
            hp: BASE_HP + GROW_HP * g,
            defence: BASE_DEF + GROW_DEF * g,
            magic_resistance: BASE_MR + GROW_MR * g,
            move_speed: BASE_MS + GROW_MS * g,
            hp_regen: BASE_REGEN + GROW_REGEN * g,
            stack: 0,
            crit_chance: BASE_CRIT,
        }
    }

    /// 里香出生面板 = 乙骨当前等级基础面板 ×2（出生定死，存活期不动态更新）。
    fn rika_spawn_stat(level: usize) -> StatV1 {
        let b = Self::base_stat(level);
        StatV1 {
            attack: b.attack * 2,
            magic_power: b.magic_power * 2,
            hp: b.hp * 2,
            defence: b.defence * 2,
            magic_resistance: b.magic_resistance * 2,
            move_speed: b.move_speed * 2,
            hp_regen: b.hp_regen * 2,
            stack: 0,
            crit_chance: b.crit_chance * 2,
        }
    }

    fn spawn_rika(&mut self, sim: &mut StableSim<'_>, yuta_id: usize) {
        let Some(y) = sim.get_entity(yuta_id) else { return };
        let team = y.team();
        let level = y.level();
        let (x, yp) = y.pos();
        let stat = Self::rika_spawn_stat(level);
        let attack = UnitAttackV1 {
            range: 14_000,
            ..UnitAttackV1::default()
        };
        dlog(format!(
            "spawn_unit begin tick={} lv={level} pos=({},{}) hp={} atk={} ms={} crit={}",
            sim.tick(), x, yp, stat.hp, stat.attack, stat.move_speed, stat.crit_chance
        ));
        // 在乙骨脚下出生（固定偏移会让一侧队伍刷出场外）。
        let spawned = sim.spawn_unit(
            RIKA_UNIT,
            yuta_id,
            team,
            x,
            yp,
            RIKA_DURATION,
            &stat,
            &attack,
        );
        dlog(format!("spawn_unit end => {:?}", spawned));
        if let Some(id) = spawned {
            sim.add_buff(id, &BuffV1::named(RIKA_TAG));
            self.rika = Some(id);
            self.satk = RIKA_SATK_TICKS;
            self.next_heal = sim.tick() + 60;
            // 把乙骨已积累的噬魂成长同步给新出生的里香。
            growth_rebuild(sim, id);
            dlog(format!("spawn_rika ok id={id}"));
        }
    }

    /// 治疗里香，过量部分转为一层长期护盾。
    ///
    /// 只在里香【当前没有护盾】时才新建一层：否则满 HP 下每个攻击周期都会把
    /// 全部治疗转成一层新的永久护盾，无限叠加（稳定 mod 的护盾都是短时会过期
    /// 的）。这里把过量护盾限制为单层，被打掉后才允许重新生成。
    fn heal_overflow(&self, sim: &mut StableSim<'_>, rika: usize, amount: usize) {
        let cur = sim.get_entity(rika).map(|e| e.hp().0).unwrap_or(0);
        sim.heal(rika, rika, amount);
        let after = sim.get_entity(rika).map(|e| e.hp().0).unwrap_or(cur);
        if after > cur {
            if let Some(over) = amount.checked_sub(after - cur) {
                let no_shield = sim.get_entity(rika).map(|e| e.shield() == 0).unwrap_or(true);
                if over > 0 && no_shield {
                    sim.entity_add_shield(rika, over, RIKA_SHIELD_TICKS);
                    dlog(format!("rika shield +{over} tick={}", sim.tick()));
                }
            }
        }
    }

    fn rika_special(&mut self, sim: &mut StableSim<'_>, rika: usize) {
        let Some(tid) = nearest_enemy(sim, rika, Some(20_000)) else {
            return;
        };
        let Some(ri) = sim.get_entity(rika) else {
            return;
        };
        // 出手前再次确认目标存活，避免把伤害/击飞挂到当帧死亡的实体上。
        if !sim.get_entity(tid).map(|e| e.is_alive()).unwrap_or(false) {
            return;
        }
        let ad = ri.stat().attack;
        let (_, max_hp) = ri.hp();
        let dmg = RIKA_SATK_DAMAGE_BASE + ad * RIKA_SATK_AD_RATIO / 100;
        sim.deal_damage(rika, tid, dmg, 0, AttackTypeV1::Skill);
        self.heal_overflow(sim, rika, max_hp * RIKA_SATK_HEAL_PCT / 100);
        sim.play_sfx("yuta_rika_spatk", rika, &InputTargetV1::target(rika));
        sim.play_view_effect(
            "yuta_fx_rika_spatk",
            rika,
            &InputTargetV1::target(rika),
            0,
            0,
            0,
        );
        // 特效本身就是一个「做攻击动作的里香」，先让特效出生，再把本体隐掉整个
        // 动画时长，画面上只会剩下一个里香（特效结束隐身到期，本体回归）。
        sim.entity_set_invisible(rika, RIKA_SATK_HIDE_TICKS);
        // 仅当目标吃下这发后仍存活，才上击飞与命中特效，不触碰当帧死亡的实体。
        if sim.get_entity(tid).map(|e| e.is_alive()).unwrap_or(false) {
            sim.apply_cc(tid, &CcV1::of_kind(CcKindV1::Airborne, 60));
            for fx in RIKA_SATK_FX {
                sim.play_view_effect(fx, rika, &InputTargetV1::target(tid), 0, 0, 0);
            }
        }
        dlog(format!("rika_special tick={} tid={tid} dmg={dmg}", sim.tick()));
    }

    fn tick_rika(&mut self, sim: &mut StableSim<'_>, yuta_id: usize, yuta_alive: bool) {
        // 状态自愈：若大脑里没记录里香，但场上确有带归属标记的存活里香（例如
        // 状态重建/复活后），直接认领它，绝不再生一只造成重复召唤。
        if self.rika.is_none() {
            if let Some(existing) = find_rika(sim, yuta_id) {
                self.rika = Some(existing);
                self.respawn = 0;
            }
        }

        // 阵亡检测。
        if let Some(id) = self.rika {
            let alive = sim.get_entity(id).map(|e| e.is_alive()).unwrap_or(false);
            if !alive {
                self.rika = None;
                self.respawn = RIKA_RESPAWN_TICKS;
            }
        }

        if self.rika.is_none() {
            if self.respawn > 0 {
                self.respawn -= 1;
            } else if self.spawn_delay > 0 {
                // 开局等世界稳定（约 0.5 秒）再召唤。
                self.spawn_delay -= 1;
            } else if yuta_alive && mark_count(sim, yuta_id, F_MARK) == 0 {
                // 计时结束，返还 F。
                sim.add_buff(yuta_id, &BuffV1::named(F_MARK));
            }
            if yuta_alive && mark_count(sim, yuta_id, F_MARK) > 0 {
                self.spawn_rika(sim, yuta_id);
                if self.rika.is_some() {
                    sim.entity_remove_buff(yuta_id, F_MARK);
                }
            }
            return;
        }

        let rid = self.rika.unwrap();
        let Some(ri) = sim.get_entity(rid) else {
            self.rika = None;
            return;
        };
        if !ri.is_alive() {
            return;
        }
        // 大招原生 banish 退场期间：不可选中/隐身/锁输入，不进行任何战斗动作。
        if !ri.is_targetable() {
            return;
        }

        // 暴击光环：里香在场时乙骨常驻 +50% 暴击。
        if yuta_alive && mark_count(sim, yuta_id, CRIT_AURA) == 0 {
            sim.add_buff(yuta_id, &BuffV1::named(CRIT_AURA));
        }

        // 普攻周期：面前有敌时按攻击间隔回血（过量转单层护盾）。
        if sim.tick() >= self.next_heal {
            let interval = sim
                .get_entity(rid)
                .map(|e| e.attack_interval())
                .filter(|t| *t > 0)
                .unwrap_or(60);
            if nearest_enemy(sim, rid, Some(RIKA_RANGE)).is_some() {
                let max_hp = sim.get_entity(rid).map(|e| e.hp().1).unwrap_or(0);
                if max_hp > 0 {
                    self.heal_overflow(sim, rid, max_hp * RIKA_LIFESTEAL_PCT / 100);
                }
            }
            self.next_heal = sim.tick() + interval;
        }

        // 8 秒一次自身强化普攻。
        if self.satk > 0 {
            self.satk -= 1;
        }
        if self.satk == 0 {
            self.rika_special(sim, rid);
            self.satk = RIKA_SATK_TICKS;
        }
    }

    /// 每个世界 tick（安全点）推进一次：标记计时 + 里香。
    fn tick(&mut self, sim: &mut StableSim<'_>, yuta_id: usize) {
        let yuta_alive = sim.get_entity(yuta_id).map(|e| e.is_alive()).unwrap_or(false);

        // 标记计时：死亡期间暂停。
        if yuta_alive {
            let tick = sim.tick();
            for k in 0..5 {
                if self.timers[k] > 0 {
                    self.timers[k] -= 1;
                    if self.timers[k] == 0 {
                        dlog(format!("grant mark {k} tick={tick}"));
                        stack_grant(sim, yuta_id, k);
                        self.timers[k] = MARK_PERIODS[k];
                    }
                }
            }
        }

        self.tick_rika(sim, yuta_id, yuta_alive);
    }
}

/// 乙骨取得一次击杀或助攻：乙骨与在场里香各加一层噬魂成长（+10%，永久叠加）。
/// 由 passive on_kill / on_assist 触发；里香按归属标记实时查找，不依赖大脑表，
/// 因此即便在伤害结算中重入也安全。
fn gain_growth(sim: &mut StableSim<'_>, yuta_id: usize) {
    dlog(format!("growth +1 tick={}", sim.tick()));
    with_growth(yuta_id, |n| *n += 1);
    if sim.get_entity(yuta_id).map(|e| e.is_alive()).unwrap_or(false) {
        growth_push(sim, yuta_id);
    }
    if let Some(rid) = find_rika(sim, yuta_id) {
        if sim.get_entity(rid).map(|e| e.is_alive()).unwrap_or(false) {
            growth_push(sim, rid);
        }
    }
}

/// 本场是否已经做过收场清理（on_match_start 重置；is_end 首次为真时执行一次）。
static END_SEEN: AtomicBool = AtomicBool::new(false);

/// 收场处理：【只读自检 + 只清我方 Rust 内存】，绝不在 is_end 阶段调用任何会改世界
/// 的 API（entity_set_hp/clear_shield 等会触发引擎死亡/结算流程，在收场中途改世界
/// 本身就可能崩溃，和当年 on_update 的教训一致）。召唤物本身由引擎在拆除世界时
/// 安全回收——这是稳定 mod 已验证的路径，不需要我们去杀它。
fn reap_rika_at_end(sim: &mut StableSim<'_>) {
    // 只读：记录收场瞬间里香是否还挂着护盾（应恒为 0，因为 RIKA_SHIELD_TICKS=420
    // 远小于战斗结束到 is_end 的间隔）。若哪天看到非 0，说明护盾定时器仍是隐患。
    let mut shields: Vec<(usize, usize)> = Vec::new();
    for i in 0..sim.entity_count() {
        if let Some(e) = sim.entity_at(i) {
            if e.is_alive() && has_buff_named(&e, RIKA_TAG) {
                shields.push((e.id(), e.shield()));
            }
        }
    }
    STACKS.lock().unwrap_or_else(|e| e.into_inner()).clear();
    GROWTH.lock().unwrap_or_else(|e| e.into_inner()).clear();
    BRAINS.lock().unwrap_or_else(|e| e.into_inner()).clear();
    dlog(format!(
        "end cleanup tick={} rika_shields={:?} ec={} (memory-only)",
        sim.tick(),
        shields,
        sim.entity_count()
    ));
}

/// 世界 tick 结束后的安全点：推进每个乙骨的大脑。
/// 大脑先从全局表取出（避免在调用会改世界的 API 时持锁/重入死锁），再放回。
struct YutaHook;
impl StableMatchHook for YutaHook {
    /// 每局开局一次（玩家已出生、首个 tick 完成前）。关键：引擎在「再来一局」时
    /// 会复用实体 id（上一局里香是 id8/id93，新一局仍是 id8/id93），而 Rust 侧
    /// 三张全局表会跨局残留。若不清干净，上一局 GROWTH[93] 等会在新局被错误重建
    /// 到复用 id 上，并在收场阶段触发崩溃。这里与 on_spawn 的先后无关地做彻底重置。
    fn on_match_start(&self, sim: &mut StableSim<'_>) {
        // 新一局：复位收场标记。
        END_SEEN.store(false, Ordering::Relaxed);
        // 标记/成长：新局一律从零开始，直接整表清空（on_spawn 随后会重建英雄本体）。
        STACKS.lock().unwrap_or_else(|e| e.into_inner()).clear();
        GROWTH.lock().unwrap_or_else(|e| e.into_inner()).clear();

        // 大脑：仍在场且是英雄的 id 重置为 fresh（新局的乙骨），其余（上一局里香等
        // 已不存在/被复用的 id）一律剔除，杜绝指向上一局已销毁世界的悬挂引用。
        let mut brains = BRAINS.lock().unwrap_or_else(|e| e.into_inner());
        brains.retain(|eid, brain| {
            let keep = sim.get_entity(*eid).map(|e| e.is_champion()).unwrap_or(false);
            if keep {
                *brain = YutaBrain::fresh();
            }
            keep
        });
        dlog(format!(
            "on_match_start swept; ec={} brains_left={}",
            sim.entity_count(),
            brains.len()
        ));
    }

    fn on_match_tick(&self, sim: &mut StableSim<'_>, _rng_seed: u64) {
        let tick = sim.tick();

        // ===== 收场阶段：只读自检 + 清我方内存，不改世界 =====
        // 反汇编 sungjinwoo 证实：近永久(1亿tick)召唤物 + 永久标记 buff 在连开多局时
        // 由引擎安全回收，不是崩溃源；真正不能留下的是「收场时仍未到期的护盾定时器」
        // （已用 RIKA_SHIELD_TICKS=420 保证其在战斗结束后、is_end 前自然到期）。
        // 这里绝不能 set_hp/clear_shield——在 is_end 改世界会触发引擎死亡/结算，危险。
        if sim.is_end() {
            if !END_SEEN.swap(true, Ordering::Relaxed) {
                reap_rika_at_end(sim);
            }
            // 收场阶段不再推进任何战斗逻辑。
            return;
        }

        // 登记的乙骨实体 id 快照。
        let ids: Vec<usize> = brains_lock(|m| m.keys().copied().collect());
        let mut stale: Vec<usize> = Vec::new();
        for eid in ids {
            let is_champ = sim.get_entity(eid).map(|e| e.is_champion()).unwrap_or(false);
            if !is_champ {
                // 开局早期实体可能尚未就绪，仅在比赛进行一段时间后才清理失效 id。
                if tick > 300 {
                    stale.push(eid);
                }
                continue;
            }
            if tick % 600 == 0 {
                dlog(format!("brain tick={tick} entity={eid} end={}", sim.is_end()));
            }
            let mut brain = brains_lock(|m| m.remove(&eid)).unwrap_or_else(YutaBrain::fresh);
            brain.tick(sim, eid);
            brains_lock(|m| {
                m.insert(eid, brain);
            });
        }
        if !stale.is_empty() {
            brains_lock(|m| {
                for s in stale {
                    m.remove(&s);
                }
            });
        }
        // 尾段打点：进入可能结束的区间后每 30 tick 一次；一旦还崩，最后一行就是
        // 钩子完整跑完的确切 tick，并能看出 is_end 是否曾翻转（end=true 会先走上面
        // 的 end cleanup 分支）。
        if tick >= 6_900 && tick % 30 == 0 {
            dlog(format!(
                "tickpost tick={tick} ec={} end={}",
                sim.entity_count(),
                sim.is_end()
            ));
        }
    }

    /// 收场判定钩子（引擎判定胜负时调用）。双保险：若 on_match_tick 尚未观测到
    /// is_end 翻转，这里在 is_end 为真时同样执行一次里香清理；始终返回 None 不干预胜负。
    fn check_match_end(&self, sim: &mut StableSim<'_>) -> Option<bool> {
        let tick = sim.tick();
        if sim.is_end() && !END_SEEN.swap(true, Ordering::Relaxed) {
            reap_rika_at_end(sim);
        }
        if tick >= 6_900 && tick % 60 == 0 {
            dlog(format!(
                "check_match_end tick={tick} ec={} end={}",
                sim.entity_count(),
                sim.is_end()
            ));
        }
        None
    }
}

// ===================== 被动（仅事件回调，不做每帧世界逻辑） =====================

struct YutaPassive;

impl StablePassive for YutaPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(Self)
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        dlog(format!("on_spawn tick={} entity={}", sim.tick(), entity));
        // 新比赛开局（tick < 10）清空全部残留并登记一个新大脑；复活则保留大脑
        // （里香跨乙骨死亡继续存在），只确保已登记。
        if sim.tick() < 10 {
            with_stack(entity, |st| st.clear());
            with_growth(entity, |n| *n = 0);
            brains_lock(|m| {
                m.insert(entity, YutaBrain::fresh());
            });
        } else {
            brains_lock(|m| {
                m.entry(entity).or_insert_with(YutaBrain::fresh);
            });
        }
        stack_rebuild(sim, entity);
        growth_rebuild(sim, entity);
    }

    fn on_kill(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize, _victim: usize) {
        gain_growth(sim, entity);
    }

    fn on_assist(&mut self, sim: &mut StableSim<'_>, _player: usize, entity: usize) {
        gain_growth(sim, entity);
    }
}

// ===================== Native effects =====================

struct MarkSync;
impl StableEffectType for MarkSync {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        sync_next(sim, caster);
    }
}

struct ConsumeMark(usize);
impl StableEffectType for ConsumeMark {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        stack_consume(sim, caster, self.0);
    }
}

/// 里香最大生命 10% 真实伤害命中点（挂在技能/强化普攻效果链中，含范围节点
/// 对每个敌人生效一次）。同步结算，安全用法见 [`rika_true_strike`]。
struct RikaTrue;
impl StableEffectType for RikaTrue {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        rika_true_strike(sim, caster, input.target_id);
    }
}

/// 技能二：禁锢 1.5 秒（只锁移动）。
struct BindHit;
impl StableEffectType for BindHit {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, _caster: usize, input: InputTargetV1) {
        if sim.get_entity(input.target_id).map(|e| e.is_alive()).unwrap_or(false) {
            sim.apply_cc(input.target_id, &CcV1::of_kind(CcKindV1::Bind, S2_BIND_TICKS));
        }
    }
}

/// 强化普攻三：数据层 Rush 已把乙骨突进到锁定敌人身边，这里打五连物伤 +
/// 固定回血 + 里香真伤。位移完全交给引擎 Rush，native 不再 set_pos。
struct Atk3;
impl StableEffectType for Atk3 {
    /// 【必须非零】atk3 是 attack.effect 里【唯一没有数据层 Attack 节点】的分支
    /// （伤害全部在本 native 结算）。战斗 AI 按分支期望伤害做评估，若这里返回默认
    /// (0,0)，引擎 battle.rs 会 attempt to divide by zero 直接闪退（无 mod panic，
    /// 崩点随 AI 何时规划该分支漂移）——创作指南 2026-09-10 铁律。返回与 apply 完全
    /// 一致的五段物理伤害总和（基础 90，保证任何等级都非零）。
    fn expected_damage(&self, s: &StatV1) -> (usize, usize) {
        let seg = ATK3_SEG_BASE + s.attack * ATK3_SEG_AD / 100;
        (ATK3_SEGMENTS * seg, 0)
    }

    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let tid = input.target_id;
        if !sim.get_entity(tid).map(|e| e.is_alive()).unwrap_or(false) {
            return;
        }
        let ad = sim.get_entity(caster).map(|e| e.stat().attack).unwrap_or(0);
        let seg = ATK3_SEG_BASE + ad * ATK3_SEG_AD / 100;
        for _ in 0..ATK3_SEGMENTS {
            if !sim.get_entity(tid).map(|e| e.is_alive()).unwrap_or(false) {
                break;
            }
            sim.deal_damage(caster, tid, seg, 0, AttackTypeV1::Skill);
        }
        sim.heal(caster, caster, ATK3_HEAL);
        sim.play_sfx("yuta_atk3", caster, &InputTargetV1::target(tid));
        for fx in [
            "yuta_fx_atk3_6602",
            "yuta_fx_atk3_6605",
            "yuta_fx_atk3_6606",
            "yuta_fx_atk3_6607",
        ] {
            sim.play_view_effect(fx, caster, &InputTargetV1::target(tid), 0, 0, 0);
        }
        rika_true_strike(sim, caster, tid);
        dlog(format!("atk3 tick={} tid={tid}", sim.tick()));
    }
}

/// 大招（方向性光束）的 native 部分拆成两个：UltOpen 自身瞬间 / UltHit 光束命中。
/// 大招开启瞬间（方向性技能，无目标依赖）：里香原生退场
/// （引擎自己处理隐身/不可选中/输入锁定）。
struct UltOpen;
impl StableEffectType for UltOpen {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        if let Some(rid) = find_rika(sim, caster) {
            sim.entity_banish(caster, rid, ULT_BANISH_TICKS, "", "");
        }
        dlog(format!("ult open tick={}", sim.tick()));
    }
}

/// 大招光束每一跳对命中敌人结算：碎盾、削双抗、封技能、里香同步真伤。
/// 挂在 LineRangeProjectile.applied_effects 里，同分支还有数据层 Attack（80+50%AD），
/// AI 期望伤害非零，无需覆盖 expected_damage。
struct UltHit;
impl StableEffectType for UltHit {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        let tid = input.target_id;
        let Some(t) = sim.get_entity(tid) else { return };
        if !t.is_alive() || t.is_tower() {
            return;
        }
        sim.entity_clear_shield(tid);
        let mut debuff = BuffV1::timed("yuta_ult_shred", ULT_DEBUFF_TICKS);
        debuff.defence_mult = ULT_RESIST_DOWN;
        debuff.magic_resistance_mult = ULT_RESIST_DOWN;
        sim.add_buff(tid, &debuff);
        sim.apply_cc(tid, &CcV1::of_kind(CcKindV1::BlockSkill, ULT_BLOCK_TICKS));
        // 里香此刻已被 UltOpen 退场（不可选中），但联动真伤由乙骨直接结算，仍生效。
        rika_true_strike(sim, caster, tid);
        dlog(format!("ult beam hit tick={} tid={tid}", sim.tick()));
    }
}

// ===================== 入口 =====================

fn init(host: &StableHost) -> StableMod {
    // 每次加载清空旧调试日志，并挂 panic 钩子把崩溃信息写盘。
    use std::panic;
    let _ = std::fs::remove_file(DEBUG_LOG);
    panic::set_hook(Box::new(|info| {
        let msg = if let Some(s) = info.payload().downcast_ref::<&str>() {
            s.to_string()
        } else if let Some(s) = info.payload().downcast_ref::<String>() {
            s.clone()
        } else {
            "unknown panic".to_string()
        };
        let loc = info
            .location()
            .map(|l| format!("{}:{}", l.file(), l.line()))
            .unwrap_or_default();
        dlog(format!("!!! RUST PANIC: {msg} @ {loc}"));
    }));
    dlog("=== yuta mod init ===");
    let mut module = StableMod::new(ID);
    module.add_native_effect(format!("{ID}:yuta_mark_sync"), MarkSync);
    module.add_native_effect(format!("{ID}:yuta_consume_a"), ConsumeMark(0));
    module.add_native_effect(format!("{ID}:yuta_consume_b"), ConsumeMark(1));
    module.add_native_effect(format!("{ID}:yuta_consume_c"), ConsumeMark(2));
    module.add_native_effect(format!("{ID}:yuta_consume_d"), ConsumeMark(3));
    module.add_native_effect(format!("{ID}:yuta_consume_e"), ConsumeMark(4));
    module.add_native_effect(format!("{ID}:yuta_rika_true"), RikaTrue);
    module.add_native_effect(format!("{ID}:yuta_bind"), BindHit);
    module.add_native_effect(format!("{ID}:yuta_atk3"), Atk3);
    module.add_native_effect(format!("{ID}:yuta_ult_open"), UltOpen);
    module.add_native_effect(format!("{ID}:yuta_ult_hit"), UltHit);
    module.add_native_passive(format!("{ID}:yuta_passive"), YutaPassive);
    module.set_match_hook(YutaHook);
    host.log(LogLevel::Info, "Yuta mod loaded.");
    module
}

declare_stable_mod!(init, requires = 9);
