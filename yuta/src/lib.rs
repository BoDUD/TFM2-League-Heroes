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
//!
//! 状态隔离铁律（「有的对局有里香、有的对局没有」的根因）：
//! 游戏在同一个进程里会跑多份模拟——服务器预模拟（ServerPresim，赛程结果先在
//! 后台算一遍）、屏幕上正在看的对局（ClientMatchView）、观战、回放。每份模拟的
//! 实体 id 都从同样的小整数开始，而 match hook / native effect 是所有模拟共用的
//! 同一个对象。旧版把大脑、标记栈、成长放在只按实体 id 区分的全局表里：后台预模拟
//! 开局会重置、收场会清空、逐 tick 会拿它自己世界里的实体去推进屏幕对局的大脑，
//! 屏幕上的里香于是时有时无（官方 SDK 文档对 sim 回调的要求：no global state）。
//! 现在所有运行时状态都按「哪一份模拟」分开存放，见 [`SimKey`] / [`with_state`]。

use std::collections::btree_map::Entry;
use std::collections::{BTreeMap, HashMap};
use std::fs::OpenOptions;
use std::io::Write;
use std::sync::atomic::{AtomicU64, Ordering};
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

/// 带模拟来源的日志：预模拟与屏幕对局交错写同一个文件时，也能分清每行属于哪一份。
fn slog(sim: &StableSim<'_>, msg: impl AsRef<str>) {
    dlog(format!("[{}] {}", SimKey::of(sim).label(), msg.as_ref()));
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

// ===================== 按模拟隔离的运行时状态 =====================

/// 一份模拟的身份：来源（预模拟 / 屏幕对局 / 观战 / 回放 / 工具）+ 赛程、回放、
/// 小局编号 + 对局种子。同一赛程的预模拟和屏幕对局种子相同但来源不同；不同赛程
/// 编号和种子都不同，所以并行或交错跑的几份模拟各用各的状态。
#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug)]
struct SimKey {
    kind: u32,
    match_id: u64,
    replay_id: u64,
    set_index: u64,
    seed: u64,
}

impl SimKey {
    fn of(sim: &StableSim<'_>) -> Self {
        let origin = sim.sim_origin().unwrap_or_default();
        Self {
            kind: origin.kind,
            match_id: origin.match_id,
            replay_id: origin.replay_id,
            set_index: origin.set_index,
            seed: sim.seed(),
        }
    }

    fn label(&self) -> String {
        let kind = match SimOriginKindV1::from_code(self.kind) {
            Some(SimOriginKindV1::ServerPresim) => "presim",
            Some(SimOriginKindV1::ClientMatchView) => "view",
            Some(SimOriginKindV1::ClientSpectate) => "spectate",
            Some(SimOriginKindV1::ClientReplay) => "replay",
            Some(SimOriginKindV1::Tool) => "tool",
            _ => "unknown",
        };
        let id = |v: u64| {
            if v == SimOriginV1::NONE {
                "-".to_string()
            } else {
                v.to_string()
            }
        };
        format!(
            "{kind} m={} r={} s={} seed={:x}",
            id(self.match_id),
            id(self.replay_id),
            id(self.set_index),
            self.seed
        )
    }
}

/// 一份模拟里本 mod 的全部运行时状态。键都是【该模拟世界】里的实体 id；用 BTreeMap
/// 保证遍历顺序固定（同一赛程的预模拟和屏幕对局必须算出一样的结果）。
#[derive(Default)]
struct SimState {
    /// 这份模拟见过的最大 tick。tick 变小 = 同一身份的模拟重新开跑（重看回放、
    /// 中途退出后重开），上一轮留下的状态整份作废。
    last_tick: usize,
    /// 最近一次访问的序号，只用来回收没跑到收场就被放弃的模拟留下的状态。
    stamp: u64,
    /// 乙骨实体 id -> 大脑。
    brains: BTreeMap<usize, YutaBrain>,
    /// 乙骨实体 id -> 标记 LIFO 栈（引擎死亡会清空实体 buff，真值存这里）。
    stacks: BTreeMap<usize, Vec<u8>>,
    /// 乙骨实体 id -> 噬魂成长层数（同理，死亡不丢）。
    growth: BTreeMap<usize, u32>,
}

static SIMS: LazyLock<Mutex<HashMap<SimKey, SimState>>> =
    LazyLock::new(|| Mutex::new(HashMap::new()));
static STAMP: AtomicU64 = AtomicU64::new(0);
/// 同时保留的模拟状态上限。进行中的模拟每 tick 都会访问自己的状态，不会被回收。
const MAX_SIMS: usize = 64;

/// 取当前这份模拟的状态。闭包里【只许改 Rust 数据】：持锁期间调用会改世界的
/// sim API，可能经引擎回调重入本 mod（伤害 -> on_kill 等）而死锁。
fn with_state<R>(sim: &StableSim<'_>, f: impl FnOnce(&mut SimState) -> R) -> R {
    // 先把要问引擎的都问完，再上锁。
    let key = SimKey::of(sim);
    let tick = sim.tick();
    let stamp = STAMP.fetch_add(1, Ordering::Relaxed);
    // PoisonError::into_inner：即使此前回调 panic 过也继续可用，避免连锁崩溃。
    let mut map = SIMS.lock().unwrap_or_else(|e| e.into_inner());
    if map.len() >= MAX_SIMS && !map.contains_key(&key) {
        if let Some(oldest) = map.iter().min_by_key(|(_, s)| s.stamp).map(|(k, _)| *k) {
            map.remove(&oldest);
        }
    }
    let st = map.entry(key).or_default();
    if tick < st.last_tick {
        *st = SimState::default();
    }
    st.last_tick = tick;
    st.stamp = stamp;
    f(st)
}

/// 这份模拟是否已有状态（不新建）。没有乙骨的模拟（大多数后台预模拟）不建状态。
fn has_state(sim: &StableSim<'_>) -> bool {
    let key = SimKey::of(sim);
    SIMS.lock().unwrap_or_else(|e| e.into_inner()).contains_key(&key)
}

/// 收场：拿走这份模拟的状态（只动 Rust 内存，不改世界）。
fn take_state(sim: &StableSim<'_>) -> Option<SimState> {
    let key = SimKey::of(sim);
    SIMS.lock().unwrap_or_else(|e| e.into_inner()).remove(&key)
}

// ---------------- 噬魂成长（击杀/助攻 +10% 基础属性） ----------------

const GROWTH_BUFF: &str = "yuta_growth";
/// 每层 +10%：攻击/法强/护甲/生命/魔抗（同名 buff 按层叠加）。
const GROWTH_MULT: i32 = 10;

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

/// 出生/复活：补挂 `layers` 层成长 buff。
fn growth_rebuild(sim: &mut StableSim<'_>, eid: usize, layers: u32) {
    for _ in 0..layers {
        growth_push(sim, eid);
    }
}

/// 乙骨在这份模拟里累计的成长层数。
fn growth_of(sim: &StableSim<'_>, yuta_id: usize) -> u32 {
    with_state(sim, |st| st.growth.get(&yuta_id).copied().unwrap_or(0))
}

// ---------------- 里香 ----------------

const RIKA_UNIT: &str = "yuta_summon";
/// 里香归属标记：必须用固定静态名，绝不能按实体 id 现场 format! 出动态名——
/// 动态 buff 名会在引擎侧反复注册/在跨局复用的实体 id 上残留，收场时崩溃。
/// 归属（哪只乙骨的里香）记在本份模拟的大脑里，不靠 buff 名区分。
const RIKA_TAG: &str = "yuta_rika_tag";
/// 乙骨自身标记（同样是固定静态名）：on_spawn 挂上，match hook 靠它在任何一份
/// 模拟里认出乙骨，保证每只乙骨都有大脑。
const YUTA_TAG: &str = "yuta_self_tag";
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
/// 里香在场时乙骨的额外暴击率（百分点，与面板 crit_chance 同单位）。
/// 旧版光环 buff 只有名字没有数值，挂上去不加任何暴击。
const CRIT_AURA_PCT: i32 = 50;

fn crit_aura_buff() -> BuffV1 {
    let mut b = BuffV1::named(CRIT_AURA);
    b.crit_chance = CRIT_AURA_PCT;
    b
}

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
    let Some(rid) = rika_of(sim, caster) else {
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

/// `id` 是否仍是 `team` 一方存活的里香。实体 id 会被引擎复用：里香死后这个 id
/// 可能分给新刷的小兵，只看 is_alive 会把小兵当成里香，所以还要核对队伍和身份
/// （归属标记；标记万一被清掉时退回按单位名核对）。
fn is_rika(sim: &StableSim<'_>, id: usize, team: usize) -> bool {
    let Some(e) = sim.get_entity(id) else {
        return false;
    };
    e.is_alive()
        && e.team() == team
        && (has_buff_named(&e, RIKA_TAG) || e.name().as_deref() == Some(RIKA_UNIT))
}

/// 这只乙骨在【这份模拟】里的里香：按他大脑记录的 id 查，不再全图找任意一只
/// （镜像对局里旧版会拿到对面的里香）。大脑不在这份状态里时退回找同队的里香。
fn rika_of(sim: &StableSim<'_>, owner: usize) -> Option<usize> {
    match with_state(sim, |st| st.brains.get(&owner).map(|b| (b.rika, b.team))) {
        Some((Some(rid), team)) => is_rika(sim, rid, team).then_some(rid),
        Some((None, _)) => None,
        None => {
            let team = sim.get_entity(owner)?.team();
            find_unclaimed_rika(sim, team, &[])
        }
    }
}

/// 场上本方存活、且没有被这份模拟里其他乙骨认领的里香（大脑状态重建后认领用）。
fn find_unclaimed_rika(sim: &StableSim<'_>, team: usize, claimed: &[usize]) -> Option<usize> {
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        let id = e.id();
        if !claimed.contains(&id) && is_rika(sim, id, team) {
            return Some(id);
        }
    }
    None
}

/// 这份模拟里所有存活、挂着自身标记（on_spawn 挂的）的乙骨，返回 (实体 id, 队伍)。
fn find_yutas(sim: &StableSim<'_>) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        if e.is_champion() && e.is_alive() && has_buff_named(&e, YUTA_TAG) {
            out.push((e.id(), e.team()));
        }
    }
    out
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
    let pushed = with_state(sim, |st| {
        let stack = st.stacks.entry(eid).or_default();
        if stack.len() >= MARK_CAP {
            false
        } else {
            stack.push(ty as u8);
            true
        }
    });
    if !pushed {
        return;
    }
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
    with_state(sim, |st| {
        if let Some(stack) = st.stacks.get_mut(&eid) {
            if let Some(pos) = stack.iter().rposition(|m| *m as usize == ty) {
                stack.remove(pos);
            }
        }
    });
    sync_next(sim, eid);
}

/// 复活：按 Rust 栈重建全部 mark buff（引擎死亡已清空实体 buff）。
fn stack_rebuild(sim: &mut StableSim<'_>, eid: usize, marks: &[u8]) {
    for &ty in marks {
        sim.add_buff(eid, &BuffV1::named(MARK_NAMES[ty as usize]));
    }
    sync_next(sim, eid);
}

// ===================== 里香大脑（按模拟存放，由 MatchHook 驱动） =====================
//
// 关键架构（对照稳定 mod sungjinwoo / necoarc）：一切「每帧遍历世界、召唤、
// 治疗、造成伤害」的逻辑都必须在 StableMatchHook::on_match_tick（核心世界 tick
// 与输入阶段结束后的安全点）里做，绝不能放进 StablePassive::on_update——后者
// 运行在引擎逐实体更新/战斗迭代中途，此时 spawn_unit / deal_damage / heal 等
// 会改变世界实体集合，破坏引擎内部迭代，表现为无 panic、爆点漂移的随机闪退。
// 召唤物流的 sjw 正是用 on_match_tick 管理召唤物。

/// 每个乙骨的运行时状态，存在所属模拟的 [`SimState`] 里；只在 on_match_tick 内复制出来推进。
#[derive(Clone)]
struct YutaBrain {
    /// 乙骨所在队伍（登记时记下；乙骨阵亡期间也靠它核对里香归属）。
    team: usize,
    /// 各标记剩余获取计时（死亡期间不递减）。
    timers: [usize; 5],
    /// 这只乙骨的里香（本份模拟里的实体 id）。
    rika: Option<usize>,
    respawn: usize,
    /// 开局世界未稳定前延迟召唤（tick）。
    spawn_delay: usize,
    next_heal: usize,
    satk: usize,
}

impl YutaBrain {
    fn fresh(team: usize) -> Self {
        Self {
            team,
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
        slog(
            sim,
            format!(
                "spawn_unit begin tick={} owner={yuta_id} lv={level} pos=({},{}) hp={} atk={} ms={} crit={}",
                sim.tick(),
                x,
                yp,
                stat.hp,
                stat.attack,
                stat.move_speed,
                stat.crit_chance
            ),
        );
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
        slog(sim, format!("spawn_unit end => {:?}", spawned));
        if let Some(id) = spawned {
            sim.add_buff(id, &BuffV1::named(RIKA_TAG));
            self.rika = Some(id);
            self.satk = RIKA_SATK_TICKS;
            self.next_heal = sim.tick() + 60;
            // 把乙骨已积累的噬魂成长同步给新出生的里香（旧版误按里香自己的 id 查表）。
            let layers = growth_of(sim, yuta_id);
            growth_rebuild(sim, id, layers);
            slog(sim, format!("spawn_rika ok id={id} owner={yuta_id} growth={layers}"));
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
                    slog(sim, format!("rika shield +{over} tick={}", sim.tick()));
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
        slog(sim, format!("rika_special tick={} tid={tid} dmg={dmg}", sim.tick()));
    }

    /// `claimed`：这份模拟里其他乙骨的里香，绝不认领。
    fn tick_rika(&mut self, sim: &mut StableSim<'_>, yuta_id: usize, yuta_alive: bool, claimed: &[usize]) {
        // 阵亡/失效检测：记录的 id 必须仍是本方存活的里香（id 被复用给别的单位也算没了）。
        if let Some(id) = self.rika {
            if !is_rika(sim, id, self.team) {
                self.rika = None;
                self.respawn = RIKA_RESPAWN_TICKS;
                // 里香不在场，暴击光环随之撤掉。
                sim.entity_remove_buff(yuta_id, CRIT_AURA);
                slog(sim, format!("rika gone id={id} owner={yuta_id} tick={}", sim.tick()));
            }
        }

        // 状态自愈：没记录里香，但场上有本方、未被别的乙骨认领的存活里香（例如大脑
        // 状态重建后），直接认领它，绝不再生一只造成重复召唤。
        if self.rika.is_none() {
            if let Some(existing) = find_unclaimed_rika(sim, self.team, claimed) {
                self.rika = Some(existing);
                self.respawn = 0;
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
            sim.add_buff(yuta_id, &crit_aura_buff());
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
    fn tick(&mut self, sim: &mut StableSim<'_>, yuta_id: usize, claimed: &[usize]) {
        let yuta_alive = sim.get_entity(yuta_id).map(|e| e.is_alive()).unwrap_or(false);

        // 标记计时：死亡期间暂停。
        if yuta_alive {
            let tick = sim.tick();
            for k in 0..5 {
                if self.timers[k] > 0 {
                    self.timers[k] -= 1;
                    if self.timers[k] == 0 {
                        slog(sim, format!("grant mark {k} tick={tick} owner={yuta_id}"));
                        stack_grant(sim, yuta_id, k);
                        self.timers[k] = MARK_PERIODS[k];
                    }
                }
            }
        }

        self.tick_rika(sim, yuta_id, yuta_alive, claimed);
    }
}

/// 乙骨取得一次击杀或助攻：乙骨与他自己的里香各加一层噬魂成长（+10%，永久叠加）。
/// 由 passive on_kill / on_assist 触发；只短暂读写本份模拟的状态，即便在伤害结算中
/// 重入也安全。
fn gain_growth(sim: &mut StableSim<'_>, yuta_id: usize) {
    let layers = with_state(sim, |st| {
        let n = st.growth.entry(yuta_id).or_insert(0);
        *n += 1;
        *n
    });
    slog(sim, format!("growth -> {layers} tick={} owner={yuta_id}", sim.tick()));
    if sim.get_entity(yuta_id).map(|e| e.is_alive()).unwrap_or(false) {
        growth_push(sim, yuta_id);
    }
    if let Some(rid) = rika_of(sim, yuta_id) {
        growth_push(sim, rid);
    }
}

/// 收场处理：【只读自检】，状态已由调用方从表里拿走（只清我方 Rust 内存）。绝不在
/// is_end 阶段调用任何会改世界的 API（entity_set_hp/clear_shield 等会触发引擎死亡/
/// 结算流程，在收场中途改世界本身就可能崩溃，和当年 on_update 的教训一致）。召唤物
/// 本身由引擎在拆除世界时安全回收——这是稳定 mod 已验证的路径，不需要我们去杀它。
fn log_end(sim: &StableSim<'_>, st: &SimState) {
    // 只读：记录收场瞬间里香是否还挂着护盾（应恒为 0，因为 RIKA_SHIELD_TICKS=420
    // 远小于战斗结束到 is_end 的间隔）。若哪天看到非 0，说明护盾定时器仍是隐患。
    let mut shields: Vec<(usize, usize)> = Vec::new();
    for brain in st.brains.values() {
        if let Some(rid) = brain.rika {
            if let Some(e) = sim.get_entity(rid) {
                if e.is_alive() {
                    shields.push((rid, e.shield()));
                }
            }
        }
    }
    slog(
        sim,
        format!(
            "end cleanup tick={} brains={} rika_shields={:?} ec={} (memory-only)",
            sim.tick(),
            st.brains.len(),
            shields,
            sim.entity_count()
        ),
    );
}

/// 世界 tick 结束后的安全点：推进这份模拟里每个乙骨的大脑。
/// 大脑先从状态表复制出来（推进时会调用改世界的 API，期间不能持锁/重入死锁），再写回。
struct YutaHook;
impl StableMatchHook for YutaHook {
    /// 每份模拟开局一次（玩家已出生、首个 tick 完成前）。只整理【这份模拟】自己的
    /// 状态：on_spawn 刚登记的乙骨保留并复位，标记栈/成长从零开始。旧版在这里清空
    /// 全进程共用的全局表——后台预模拟一开局，屏幕对局的状态就跟着被清掉了。
    fn on_match_start(&self, sim: &mut StableSim<'_>) {
        let brains = with_state(sim, |st| {
            st.stacks.clear();
            st.growth.clear();
            for brain in st.brains.values_mut() {
                *brain = YutaBrain::fresh(brain.team);
            }
            st.brains.len()
        });
        slog(
            sim,
            format!(
                "on_match_start tick={} ec={} brains={brains}",
                sim.tick(),
                sim.entity_count()
            ),
        );
    }

    fn on_match_tick(&self, sim: &mut StableSim<'_>, _rng_seed: u64) {
        let tick = sim.tick();

        // ===== 收场阶段：只读自检 + 丢掉这份模拟的状态，不改世界 =====
        // 反汇编 sungjinwoo 证实：近永久(1亿tick)召唤物 + 永久标记 buff 在连开多局时
        // 由引擎安全回收，不是崩溃源；真正不能留下的是「收场时仍未到期的护盾定时器」
        // （已用 RIKA_SHIELD_TICKS=420 保证其在战斗结束后、is_end 前自然到期）。
        // 这里绝不能 set_hp/clear_shield——在 is_end 改世界会触发引擎死亡/结算，危险。
        if sim.is_end() {
            if let Some(st) = take_state(sim) {
                log_end(sim, &st);
            }
            // 收场阶段不再推进任何战斗逻辑。
            return;
        }

        // 确保这份模拟里每个存活的乙骨都有大脑（on_spawn 已登记的不受影响；这是
        // passive 与 hook 拿到的模拟身份万一不一致时的兜底）。没有乙骨的模拟每 30 tick
        // 才看一眼，也不为它建状态。
        let known = has_state(sim);
        if !known && tick % 30 != 0 {
            return;
        }
        let found = find_yutas(sim);
        if !known && found.is_empty() {
            return;
        }
        let owners: Vec<usize> = with_state(sim, |st| {
            for &(eid, team) in &found {
                st.brains.entry(eid).or_insert_with(|| YutaBrain::fresh(team));
            }
            st.brains.keys().copied().collect()
        });

        for eid in owners {
            let taken = with_state(sim, |st| {
                let brain = st.brains.get(&eid).cloned()?;
                let claimed: Vec<usize> = st
                    .brains
                    .iter()
                    .filter(|(owner, _)| **owner != eid)
                    .filter_map(|(_, b)| b.rika)
                    .collect();
                Some((brain, claimed))
            });
            let Some((mut brain, claimed)) = taken else { continue };
            if tick % 600 == 0 {
                slog(sim, format!("brain tick={tick} entity={eid} rika={:?}", brain.rika));
            }
            brain.tick(sim, eid, &claimed);
            with_state(sim, |st| {
                st.brains.insert(eid, brain);
            });
        }

        // 尾段打点：进入可能结束的区间后每 30 tick 一次；一旦还崩，最后一行就是
        // 钩子完整跑完的确切 tick。
        if tick >= 6_900 && tick % 30 == 0 {
            slog(sim, format!("tickpost tick={tick} ec={}", sim.entity_count()));
        }
    }

    /// 收场判定钩子（引擎判定胜负时调用）。双保险：若 on_match_tick 尚未观测到
    /// is_end 翻转，这里在 is_end 为真时同样丢掉这份模拟的状态；始终返回 None 不干预胜负。
    fn check_match_end(&self, sim: &mut StableSim<'_>) -> Option<bool> {
        let tick = sim.tick();
        if sim.is_end() {
            if let Some(st) = take_state(sim) {
                log_end(sim, &st);
            }
        }
        if tick >= 6_900 && tick % 60 == 0 {
            slog(
                sim,
                format!("check_match_end tick={tick} ec={} end={}", sim.entity_count(), sim.is_end()),
            );
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
        let Some(team) = sim.get_entity(entity).map(|e| e.team()) else {
            return;
        };
        slog(sim, format!("on_spawn tick={} entity={entity} team={team}", sim.tick()));
        // 自身标记（固定静态名，死亡被清、复活重挂）：match hook 靠它认出乙骨。
        if mark_count(sim, entity, YUTA_TAG) == 0 {
            sim.add_buff(entity, &BuffV1::named(YUTA_TAG));
        }
        // 这份模拟里第一次出生：登记新大脑、清掉残留；复活：保留大脑（里香跨乙骨
        // 死亡继续存在），按记录重建标记与成长。
        let (marks, layers) = with_state(sim, |st| {
            if let Entry::Vacant(slot) = st.brains.entry(entity) {
                slot.insert(YutaBrain::fresh(team));
                st.stacks.remove(&entity);
                st.growth.remove(&entity);
            }
            (
                st.stacks.get(&entity).cloned().unwrap_or_default(),
                st.growth.get(&entity).copied().unwrap_or(0),
            )
        });
        stack_rebuild(sim, entity, &marks);
        growth_rebuild(sim, entity, layers);
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
        slog(sim, format!("atk3 tick={} tid={tid}", sim.tick()));
    }
}

/// 大招（方向性光束）的 native 部分拆成两个：UltOpen 自身瞬间 / UltHit 光束命中。
/// 大招开启瞬间（方向性技能，无目标依赖）：【自己的】里香原生退场
/// （引擎自己处理隐身/不可选中/输入锁定）。
struct UltOpen;
impl StableEffectType for UltOpen {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, _: InputTargetV1) {
        if let Some(rid) = rika_of(sim, caster) {
            sim.entity_banish(caster, rid, ULT_BANISH_TICKS, "", "");
        }
        slog(sim, format!("ult open tick={} owner={caster}", sim.tick()));
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
        slog(sim, format!("ult beam hit tick={} tid={tid}", sim.tick()));
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
