//! 技能栏里的层数（0.9.29，2026-11-11）。用户：「现在叠层数的技能英雄在游戏里看不到多少层 有没有办法在游戏里能看到？」；先做了
//! 头顶的数字，「放头顶有点丑啊」「不能放技能栏里面吗 和联盟一样」，选了「技能栏层数格」。
//!
//! **游戏自带的层数格。** 比赛里左下角的英雄信息面板（`ingame.champion_tooltip`：头像、血条、经验、三个技能图标）在技能图标
//! 右边有个 `stack_info`（一个图标、一个数字），平时藏着。游戏程序（0.7.1，填面板的函数 0x8729a0）的规则：英雄的
//! `ChampionInfo::stack_skill_index()` 有值它才露出来，图标是那个技能的图标，数字是这个英雄的属性 `stack`。数据英雄的
//! `stack_skill_index` 就是 .data_champion 里的同名字段（0 技能、1 技能 2、2 大招），tools/kit/stack_nums.py 写给表里的英雄。
//!
//! **数层数。** 数据只能问「身上有没有某个 buff」（`SwitchByBuff`），数不出有几层：一层就是同名 buff 多一个（维迦的
//! `league_veigar_p_stack`），或梯子爬上一级（奥瑞利安·索尔的 `league_aurelionsol_d1`..`d30`）。比赛钩子每 [`EVERY`] tick 看一次
//! [`STACKS`]（src/stack_table.rs，stack_nums.py 生成）里活着的英雄：[`Rule::Count`] 数那个 buff 有几个，[`Rule::Sum`] 把它们的
//! 一项数值加起来（维迦击杀英雄那一层 5 点法强，英雄联盟算 5 层），[`Rule::Ladder`] 看梯子爬到第几级（乘 `step`，满了的旗子
//! 另算），截到 [`Stack::cap`]。
//! 附加包自己的数也走梯子（0.9.36）：普朗克附加包把手里的银蛇币挂成 `league_gangplank_sv_<n>`（rungs 9999），只有附加包的
//! 副本有 `stack_skill_index`（stack_nums.py 的 `passive`：主包的普朗克没有银蛇币，不露出层数格）。
//!
//! 2026-11-22（用户：「还有很多叠层的技能在技能列表里看不到层数 想个办法解决一下」）又加了三种数法和「数敌人身上的」：
//! - [`Rule::Most`]：几个名字各对一个数，身上有的里取最大（名字不成梯子的：亚索的 `q_stack` 1、`q_ready` 2，阿狸第 6 级叫
//!   `et_ready`，梅尔的光弹 `p_3` / `p_6` / `p_9`）；
//! - [`Rule::Total`]：几个名字各对一个数，身上有的加起来（厄斐琉斯的子弹是 5 位二进制 `b0`..`b4`，辛德拉的法球是各自计时的
//!   四个槽 `o1`..`o4`）；
//! - [`Rule::Prefix`]：名字以它开头的 buff 有几个（附加包挂在敌人身上的层数名字后面带施法者的实体号：布兰德的
//!   `league_brand_bz_<id>`）；
//! - [`Stack::foes`]：这一行不数他自己，数每个活着的敌方英雄身上的，取最多的那个（附加包照英雄联盟把层数记在每个敌人身上：
//!   布隆的震荡猛击、韦鲁斯的枯萎、图奇的毒）。
//! 一个英雄可以有几行（主包的数据记在他自己身上、附加包记在敌人身上，各读各的名字），面板上是几行里最大的那个：每份英雄数据
//! 只挂得出自己那一行的 buff，另一行读出来是 0。
//! 后来又加了 [`Rule::Charges`]（技能的充能：提莫的蘑菇）和 [`Rule::Per`]（一项数值除以一层的量）。
//!
//! **tft.dll 也用这个文件**（addons/tft/src/lib.rs 用 `#[path]` 引进来）：表是它自己的 src/stack_table.rs（云顶的英雄，
//! `PREFIX` 是 `tft_`），比赛钩子只调 [`on_tick`]，客户端扩展调 [`tip`]。两个 DLL 各写各表里的英雄，谁先加载都一样。所以这里只用得到
//! `crate::wlog` 和 `crate::stack_table`，两边的根上都有。
//!
//! **写进 `stack`。** 稳定接口改属性只有 `entity_set_base_stat`：整块换掉基础属性（9 项）。可 `stat()` 读到的是算好的那块
//! （经典 SDK 0.5.1 的 `Entity::calculate_stat_cached`：每项 = (基础 + buff 的加值) x (100 + buff 的倍率) / 100，
//! `stack` = 基础的 `stack`），拿它当基础写回去，buff 就进了基础属性。所以 [`layout`] 从宿主自己这两个函数的机器码里读出：
//! 读属性时从世界取英雄用的是世界的第几个函数、算好的那块在英雄的哪里；写基础属性时写到英雄的哪里——两块必须正好挨着
//! （基础 9 项之后紧接算好的 9 项，0.7.1 是 +0x5c8 和 +0x610），对不上就整个关掉（日志一行 `STACK LAYOUT`），不再写。
//! 写的时候先照宿主的取法读出这个英雄现在的基础属性，只换 `stack`，用官方的 `entity_set_base_stat` 写回，再读一次核对；
//! 写之前算好的 `stack` 和基础的对不上（布局读错了）也不写。复活时游戏重算基础属性（`stack` 回到 0），下一次看就又写上。
//! 每份模拟（屏幕上的比赛、服务器的预演）在同样的 tick 做同样的事，src/diverge.rs 的快照（含 `stack`）里它们也一样。
//! `stack` 对数据英雄没有别的作用（只有原版英雄自己的原生代码读它）。
//!
//! **算好的跟不上不算错（2026-11-22）。** 写完基础的 `stack`，算好的那块要等游戏重算才跟上；没跟上的那一轮先不写新的数，
//! 下一轮再看。以前把这种「没跟上」全场累计，满 40 次就把所有英雄都关掉、一直关到重开游戏：过日时后台模拟的比赛也在数，
//! 当天第 790 秒亚恒的层数一秒里涨涨落落，之后开的每一局层数格都停在 0（用户：「龙王12级0层吗」）。现在只有写进去读回来
//! 不对（真写坏了）才整个关；一个英雄连着 [`LAG_LOG`] 轮都没跟上，日志记一行（每个英雄一次），照样接着等。这一轮写不写
//! 只看这一份模拟自己的数，屏幕上的比赛和服务器的预演照旧一样。
//!
//! **英雄介绍浮窗也显示（2026-11-22，用户：「大面板也加上」）。** 比赛里点开英雄出来的大面板（游戏拿
//! asset/base/ui/layout/champion_tooltip 生成，节点叫 `champion_info_tooltip`）只有名字、属性、三行技能说明，没有层数格。
//! 屏幕上这一局（`sim_origin` 是看比赛、观战、回放；过日后台模拟的不算）数出来的层数记一份「英雄 -> 层数」，[`tip`] 每帧
//! 看这个面板开着、名字标签是表上的英雄，就在层数格那个技能（表里的 [`Stack::skill`]）的图标右下角叠一个小数字牌，
//! 和英雄联盟技能图标上的层数一样。

use std::collections::{HashMap, HashSet};
use std::sync::{Mutex, OnceLock};

use mod_api_stable::*;

pub use crate::stack_table::{PREFIX, STACKS};

/// 怎么从英雄自己的 buff 读出层数。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Rule {
    /// 这个 buff 有几个（一层多一个）。
    Count(&'static str),
    /// 这个 buff 的一项数值加起来（一层的大小不一样时：维迦击杀英雄那一层 5 点法强，英雄联盟算 5 层）。
    Sum(&'static str, Stat),
    /// 梯子 `<前缀>1`..`<前缀>rungs` 里身上最高的那一级乘 `step`（兰博的热量一级 10、泰达米尔的怒气一级 20：照英雄联盟的
    /// 0..100）；身上有 `full`（满了的旗子：德莱厄斯的诺克萨斯之力、纳尔的满怒）就是它后面的那个数。
    Ladder { prefix: &'static str, rungs: usize, step: usize, full: Option<(&'static str, usize)> },
    /// 几个名字各对一个数，身上有的里面取最大（不成梯子的几级：亚索的 `q_stack` 是 1、`q_ready` 是 2）。
    Most(&'static [(&'static str, usize)]),
    /// 几个名字各对一个数，身上有的加起来，同名的只算一次（厄斐琉斯的子弹 `b0`..`b4` 是二进制的 1 / 2 / 4 / 8 / 16，
    /// 辛德拉各自到时的四个法球槽各算 1）。
    Total(&'static [(&'static str, usize)]),
    /// 名字以它开头的 buff 有几个（附加包挂在敌人身上的层数名字里带着施法者的实体号）。
    Prefix(&'static str),
    /// 这个技能的充能还剩几次（0 技能、1 技能 2、2 大招，和 `stack_skill_index` 一样数）：读游戏自己的冷却
    /// （`entity_cooldown` 的 `charges`），不是 buff。没学会、不是充能技能的时候是 0。
    Charges(usize),
    /// 这个 buff 的一项数值加起来、再除以一层的量（四舍五入）：原生代码把层数折成一个 buff 的数值的（云顶赛芬的怒气
    /// 一层 5 攻击力、麦迪的赏金一份 15% 攻速、呲呲身边一个队友 10 护甲）。
    Per(&'static str, Stat, usize),
}

/// [`Rule::Sum`] / [`Rule::Per`] 加哪一项。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stat {
    MagicPower,
    Hp,
    Attack,
    Defence,
    AttackSpeedMult,
    DamagedReduce,
}

impl Stat {
    pub fn of(self, b: &BuffV1) -> i64 {
        match self {
            Stat::MagicPower => b.magic_power as i64,
            Stat::Hp => b.hp as i64,
            Stat::Attack => b.attack as i64,
            Stat::Defence => b.defence as i64,
            Stat::AttackSpeedMult => b.attack_speed_mult as i64,
            Stat::DamagedReduce => b.damaged_reduce as i64,
        }
    }
}

/// 表里的一行：一个英雄的一种数法（一个英雄可以有几行，面板上取最大的）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Stack {
    pub hero: &'static str,
    pub rule: Rule,
    /// 最多显示到这个数。
    pub cap: usize,
    /// 数每个活着的敌方英雄身上的（取最多的那个），不数他自己的。
    pub foes: bool,
    /// 层数格配的技能（0 技能、1 技能 2、2 大招，就是数据里的 `stack_skill_index`；一个英雄的几行一样）：英雄介绍浮窗把数字
    /// 叠在这个技能的图标上。
    pub skill: usize,
}

/// 隔几 tick 数一次（0.1 秒）：层数变了，面板上最多晚这么久。
pub const EVERY: usize = 6;

/// 一串 buff -> 层数。
pub fn count(rule: Rule, buffs: &[BuffV1]) -> usize {
    match rule {
        Rule::Count(name) => buffs.iter().filter(|b| b.name() == name).count(),
        Rule::Sum(name, stat) => {
            buffs.iter().filter(|b| b.name() == name).map(|b| stat.of(b)).sum::<i64>().max(0) as usize
        }
        Rule::Ladder { prefix, rungs, step, full } => {
            if let Some((flag, top)) = full {
                if buffs.iter().any(|b| b.name() == flag) {
                    return top;
                }
            }
            buffs
                .iter()
                .filter_map(|b| b.name().strip_prefix(prefix)?.parse::<usize>().ok())
                .filter(|k| (1..=rungs).contains(k))
                .max()
                .unwrap_or(0)
                * step
        }
        Rule::Most(names) => names
            .iter()
            .filter(|(n, _)| buffs.iter().any(|b| b.name() == *n))
            .map(|&(_, v)| v)
            .max()
            .unwrap_or(0),
        Rule::Total(names) => names.iter().filter(|(n, _)| buffs.iter().any(|b| b.name() == *n)).map(|&(_, v)| v).sum(),
        Rule::Prefix(prefix) => buffs.iter().filter(|b| b.name().starts_with(prefix)).count(),
        // 充能不在 buff 里，见 [`value`]
        Rule::Charges(_) => 0,
        Rule::Per(name, stat, per) => {
            let total = buffs.iter().filter(|b| b.name() == name).map(|b| stat.of(b)).sum::<i64>().max(0) as usize;
            (total + per / 2) / per.max(1)
        }
    }
}

/// 表里的技能格（0 技能、1 技能 2、2 大招）是游戏的哪个技能栏。
pub fn slot_of(k: usize) -> Option<SkillSlotV1> {
    [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult].get(k).copied()
}

/// 一个技能栏现在还剩几次充能：学会了、而且是充能技能（最多不止 1 次）才算，别的是 0。
pub fn charges_now(cd: Option<CooldownV1>) -> usize {
    cd.filter(|c| c.unlocked && c.max_charges > 1).map_or(0, |c| c.charges.min(c.max_charges))
}

/// 这一行读出的数：他自己身上的、他技能的充能（`charges` 按技能格），或者（`foes`）敌方英雄里身上最多的那个；
/// 截到 `cap`。
pub fn value(st: &Stack, mine: &[BuffV1], charges: &[usize; 3], foes: &[&[BuffV1]]) -> usize {
    let n = match st.rule {
        Rule::Charges(k) => charges.get(k).copied().unwrap_or(0),
        _ if st.foes => foes.iter().map(|b| count(st.rule, b)).max().unwrap_or(0),
        _ => count(st.rule, mine),
    };
    n.min(st.cap)
}

/// 表里这个英雄的几行。
pub fn rows(hero: &str) -> impl Iterator<Item = &'static Stack> + '_ {
    STACKS.iter().filter(move |s| s.hero == hero)
}

/// 面板上的数：这个英雄几行里最大的（每份英雄数据只挂得出自己那一行的名字，别的行读出来是 0）。
pub fn number(hero: &str, mine: &[BuffV1], charges: &[usize; 3], foes: &[&[BuffV1]]) -> usize {
    rows(hero).map(|st| value(st, mine, charges, foes)).max().unwrap_or(0)
}

// ===================== 宿主的属性布局 =====================

/// 宿主的两个属性函数说的布局：读属性时取英雄用世界的第几个函数（字节偏移），基础属性块、算好的属性块在英雄的哪里。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Layout {
    pub get_slot: usize,
    pub base: usize,
    pub calc: usize,
}

/// 一块属性（9 项 usize）多长。
pub const BLOCK: usize = 9 * 8;

fn d32(b: &[u8], at: usize) -> Option<usize> {
    let s = b.get(at..at + 4)?;
    Some(u32::from_le_bytes([s[0], s[1], s[2], s[3]]) as usize)
}

fn find_seq(b: &[u8], seq: &[u8]) -> Option<usize> {
    b.windows(seq.len()).position(|w| w == seq)
}

/// 宿主取英雄的那几条指令：`mov rax,[rcx]; mov r8,[rcx+8]; mov rcx,rax; call qword ptr [r8+槽]`（世界是一个 trait 对象，
/// 状态的头两个字是它的数据和函数表）。-> 槽的字节偏移和这条 call 之后的位置。
fn world_call(code: &[u8]) -> Option<(usize, usize)> {
    const CALL: [u8; 13] = [0x48, 0x8b, 0x01, 0x4c, 0x8b, 0x41, 0x08, 0x48, 0x89, 0xc1, 0x41, 0xff, 0x90];
    let at = find_seq(code, &CALL)? + CALL.len();
    Some((d32(code, at)?, at + 4))
}

/// 四条 16 字节的搬运（`movups`，`op` 0x10 读、0x11 写）和一条 8 字节的（`mov`，读 0x8b、写 0x89），对着 `[rax+块]`
/// 连续的 0x48 字节：-> 块的偏移。
fn block_at(code: &[u8], from: usize, op: u8, mov: u8, rcx_first: bool) -> Option<usize> {
    let pos = from + find_seq(code.get(from..)?, &[0x0f, op, 0x80])?;
    let base = d32(code, pos + 3)?;
    for (k, modrm) in [(1usize, 0x88u8), (2, 0x90), (3, 0x98)] {
        let p = pos + 7 * k;
        if code.get(p..p + 3)? != [0x0f, op, modrm] || d32(code, p + 3)? != base + 0x10 * k {
            return None;
        }
    }
    // the eighth-word move (rcx <-> [rax+base+0x40]): before the four in the getter, after them in the setter
    let tail = if rcx_first { pos.checked_sub(7)? } else { pos + 28 };
    if code.get(tail..tail + 3)? != [0x48, mov, 0x88] || d32(code, tail + 3)? != base + 0x40 {
        return None;
    }
    Some(base)
}

/// 宿主的 `entity_stat`（`getter`）和 `entity_set_base_stat`（`setter`）开头的机器码 -> 布局；看不懂或者两块不挨着 -> None。
pub fn layout(getter: &[u8], setter: &[u8]) -> Option<Layout> {
    let (get_slot, g) = world_call(getter)?;
    let (_, s) = world_call(setter)?;
    let calc = block_at(getter, g, 0x10, 0x8b, true)?;
    let base = block_at(setter, s, 0x11, 0x89, false)?;
    (base + BLOCK == calc && get_slot % 8 == 0 && get_slot < 0x1000).then_some(Layout { get_slot, base, calc })
}

// ===================== 读、写基础属性 =====================

/// 这一份模拟的原始上下文（`StableSim` 只有这一个指针字段；大小不对就不碰）。
unsafe fn raw_ctx(sim: &StableSim<'_>) -> Option<*mut SimCtxV1> {
    if std::mem::size_of::<StableSim<'_>>() != std::mem::size_of::<usize>() {
        return None;
    }
    let p = *(sim as *const StableSim<'_> as *const *mut SimCtxV1);
    (!p.is_null() && (*p).size >= std::mem::size_of::<SimCtxV1>() && !(*p).sim.is_null()).then_some(p)
}

/// 宿主的布局（整个进程读一次）。
fn host_layout(sim: &StableSim<'_>) -> Option<Layout> {
    static L: OnceLock<Option<Layout>> = OnceLock::new();
    *L.get_or_init(|| {
        let found = unsafe {
            raw_ctx(sim).and_then(|ctx| {
                let vt = (*ctx).sim;
                // the host's table must reach the setter's slot (the getter's comes before it)
                if (*vt).size < std::mem::offset_of!(SimVtableV1, entity_set_base_stat) + std::mem::size_of::<usize>() {
                    return None;
                }
                let g = (*vt).entity_stat? as usize;
                let s = (*vt).entity_set_base_stat? as usize;
                layout(std::slice::from_raw_parts(g as *const u8, 0x80), std::slice::from_raw_parts(s as *const u8, 0xb0))
            })
        };
        crate::wlog(match found {
            Some(l) => format!("STACK LAYOUT entity getter slot +{:#x}, base stats +{:#x}, calculated +{:#x}: the panel's \
                                stack is written", l.get_slot, l.base, l.calc),
            None => "STACK LAYOUT not recognised (the host's stat functions changed): no stack is written".to_string(),
        });
        found
    })
}

/// 照宿主的取法读这个实体现在的基础属性。
fn read_base(sim: &StableSim<'_>, l: Layout, id: usize) -> Option<StatV1> {
    unsafe {
        let ctx = raw_ctx(sim)?;
        let state = (*ctx).state as *const usize;
        if state.is_null() {
            return None;
        }
        let (world, table) = (*state, *state.add(1) as *const usize);
        if world == 0 || table.is_null() {
            return None;
        }
        let f = *table.add(l.get_slot / 8);
        if f == 0 {
            return None;
        }
        let get: unsafe extern "C" fn(usize, usize) -> *const u8 = std::mem::transmute(f);
        let entity = get(world, id);
        (!entity.is_null()).then(|| std::ptr::read_unaligned(entity.add(l.base) as *const StatV1))
    }
}

// ===================== 比赛钩子 =====================

/// 写坏了（写进去读回来不对）就不再写。
static OFF: Mutex<bool> = Mutex::new(false);
/// 一个英雄连着这么多轮算好的 `stack` 都没跟上基础的，日志记一行（每个英雄一次）；不关掉谁，接着等。
pub const LAG_LOG: usize = 40;
/// 实体号 -> 连着几轮没跟上（只为记日志：几份模拟的实体号会重，数错了也只是日志早一点晚一点）。
static LAG: Mutex<Option<HashMap<usize, usize>>> = Mutex::new(None);
static LAG_LOGGED: Mutex<Option<HashSet<&'static str>>> = Mutex::new(None);
/// 每个英雄最多记几行 `STACKS`。
static LOGGED: Mutex<Option<HashMap<&'static str, usize>>> = Mutex::new(None);
const LOG_LINES: usize = 40;

fn note(hero: &'static str, id: usize, was: usize, now: usize, base: &StatV1, calc: &StatV1) {
    let mut guard = LOGGED.lock().unwrap_or_else(|e| e.into_inner());
    let n = guard.get_or_insert_with(HashMap::new).entry(hero).or_insert(0);
    if *n >= LOG_LINES {
        return;
    }
    *n += 1;
    crate::wlog(format!(
        "STACKS {}#{id}: {was} -> {now} (base attack {} ap {} hp {} def {} mr {} ms {}; calculated {} / {} / {} / {} / {} / {})",
        hero, base.attack, base.magic_power, base.hp, base.defence, base.magic_resistance, base.move_speed, calc.attack,
        calc.magic_power, calc.hp, calc.defence, calc.magic_resistance, calc.move_speed
    ));
}

fn off(why: String) {
    let mut o = OFF.lock().unwrap_or_else(|e| e.into_inner());
    if !*o {
        *o = true;
        crate::wlog(format!("STACKS OFF: {why}"));
    }
}

/// 这一轮这个实体跟上了没有 -> 连着没跟上的轮数到 [`LAG_LOG`] 的那一轮返回 true（该记日志了）。跟上了就从头数。
pub fn lag_step(lag: &mut HashMap<usize, usize>, id: usize, behind: bool) -> bool {
    if !behind {
        lag.remove(&id);
        return false;
    }
    if lag.len() > 4096 {
        lag.clear();
    }
    let n = lag.entry(id).or_insert(0);
    *n += 1;
    *n == LAG_LOG
}

fn lagging(hero: &'static str, id: usize, calc: usize, base: usize) {
    let due = lag_step(LAG.lock().unwrap_or_else(|e| e.into_inner()).get_or_insert_with(HashMap::new), id, true);
    if due && LAG_LOGGED.lock().unwrap_or_else(|e| e.into_inner()).get_or_insert_with(HashSet::new).insert(hero) {
        crate::wlog(format!("STACKS LAG {hero}#{id}: the calculated stack {calc} is still not the base's {base} after \
                             {LAG_LOG} checks - waiting for the game to recalculate (nothing is turned off)"));
    }
}

fn caught_up(id: usize) {
    if let Some(m) = LAG.lock().unwrap_or_else(|e| e.into_inner()).as_mut() {
        lag_step(m, id, false);
    }
}

/// 屏幕上的这一局（看比赛、观战、回放）：-> (比赛号, 第几局)。服务器的预演、过日后台模拟的比赛是 None。
fn on_screen(sim: &StableSim<'_>) -> Option<(u64, u64)> {
    let o = sim.sim_origin()?;
    matches!(SimOriginKindV1::from_code(o.kind),
        Some(SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay))
        .then_some((o.match_id, o.set_index))
}

/// 这一 tick 看到的一个活着的英雄。
struct Seen {
    id: usize,
    team: usize,
    /// 表里有他就是表里的名字。
    hero: Option<&'static str>,
    /// 要数的时候才读（表里的英雄，或者有人要数敌人身上的）。
    buffs: Vec<BuffV1>,
    /// 他表里有充能那一行的技能格的充能（别的格不读，是 0）。
    charges: [usize; 3],
    calc: StatV1,
}

/// 比赛钩子（src/lib.rs 的 `Match`）每 tick 调一次。
pub fn on_tick(sim: &mut StableSim<'_>) {
    if sim.tick() % EVERY != 0 {
        return;
    }
    // 写坏了就不写了，可屏幕上这一局还是照数，给英雄介绍浮窗
    let stopped = *OFF.lock().unwrap_or_else(|e| e.into_inner());
    let screen = on_screen(sim);
    if stopped && screen.is_none() {
        return;
    }
    let ids: Vec<usize> = (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).collect();
    let mut seen: Vec<Seen> = Vec::new();
    for id in ids {
        let Some(e) = sim.get_entity(id) else { continue };
        if !e.is_alive() {
            continue;
        }
        // 别的包的英雄（云顶的、诸神的）名字前缀就对不上，不用翻表
        let hero = e.name().filter(|n| n.starts_with(PREFIX)).and_then(|n| STACKS.iter().find(|s| s.hero == n).map(|s| s.hero));
        seen.push(Seen { id, team: e.team(), hero, buffs: Vec::new(), charges: [0; 3], calc: StatV1::default() });
    }
    if seen.iter().all(|s| s.hero.is_none()) {
        return;
    }
    // 表里有人要数敌人身上的，才把场上每个人的 buff 都读一遍
    let foes_wanted = seen.iter().any(|s| s.hero.is_some_and(|h| rows(h).any(|st| st.foes)));
    for s in seen.iter_mut() {
        if s.hero.is_none() && !foes_wanted {
            continue;
        }
        let Some(e) = sim.get_entity(s.id) else { continue };
        s.buffs = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect();
        if let Some(hero) = s.hero {
            s.calc = e.stat();
            // 只读表里有充能那一行的技能格（提莫的蘑菇、库奇的导弹），一个英雄一两次
            for st in rows(hero) {
                if let Rule::Charges(k) = st.rule {
                    if let (Some(slot), Some(c)) = (slot_of(k), s.charges.get_mut(k)) {
                        *c = charges_now(e.cooldown(slot));
                    }
                }
            }
        }
    }
    for s in seen.iter() {
        let Some(hero) = s.hero else { continue };
        let foes: Vec<&[BuffV1]> = seen.iter().filter(|o| o.team != s.team).map(|o| o.buffs.as_slice()).collect();
        let n = number(hero, &s.buffs, &s.charges, &foes);
        if let Some(key) = screen {
            shown_put(key, hero, n);
        }
        if stopped {
            continue;
        }
        let (id, calc) = (s.id, s.calc);
        let Some(l) = host_layout(sim) else { return };
        let Some(base) = read_base(sim, l, id) else { continue };
        // 算好的还没跟上上次写的：这一轮先不写新的（不算错，也不关掉谁）
        if calc.stack != base.stack {
            lagging(hero, id, calc.stack, base.stack);
            continue;
        }
        caught_up(id);
        if base.stack == n {
            continue;
        }
        let mut want = base;
        want.stack = n;
        sim.entity_set_base_stat(id, &want);
        match read_base(sim, l, id) {
            Some(back) if back == want => note(hero, id, base.stack, n, &base, &calc),
            back => {
                off(format!("{hero}#{id}: wrote stack {n}, read back {back:?}"));
                return;
            }
        }
    }
}

// ===================== 英雄介绍浮窗 =====================

/// 屏幕上这一局（比赛号, 第几局）数出来的层数：英雄 -> (层数, 叠在哪个技能)。换了一局就清掉重记。
struct Shown {
    key: (u64, u64),
    heroes: HashMap<&'static str, (usize, usize)>,
}

static SHOWN: Mutex<Option<Shown>> = Mutex::new(None);

/// 这个英雄的层数格配哪个技能（表里几行一样，取第一行）。
pub fn skill_of(hero: &str) -> usize {
    rows(hero).next().map_or(0, |s| s.skill)
}

fn shown_put(key: (u64, u64), hero: &'static str, n: usize) {
    let mut g = SHOWN.lock().unwrap_or_else(|e| e.into_inner());
    if g.as_ref().is_none_or(|s| s.key != key) {
        *g = Some(Shown { key, heroes: HashMap::new() });
    }
    if let Some(s) = g.as_mut() {
        s.heroes.insert(hero, (n, skill_of(hero)));
    }
}

/// 屏幕上这一局里这个英雄现在的 (层数, 技能)；不在这一局 -> None。
pub fn shown(hero: &str) -> Option<(usize, usize)> {
    SHOWN.lock().unwrap_or_else(|e| e.into_inner()).as_ref()?.heroes.get(hero).copied()
}

/// 比赛画面的根（asset/base/ui/layout/ingame）：没有它就不在比赛画面上，上一局记的数也不拿出来。
const MATCH_ROOT: &str = "ingame";
/// 比赛里点开英雄出来的大面板：游戏拿 asset/base/ui/layout/champion_tooltip 生成的节点名。
const TIP: &str = "champion_info_tooltip";
/// 大面板里三行技能图标（40 x 40）的左上角：技能、技能 2、大招（布局里的 skill1_icon / skill2_icon / ult_icon）。
pub const ICON: [(i32, i32); 3] = [(33, 222), (33, 330), (33, 438)];
/// 数字牌的宽、高：叠在图标右下角，往外伸出 2 格（英雄联盟技能图标上的层数也在右下角）。
pub const BADGE: (i32, i32) = (30, 18);

/// 数字牌在大面板里的左上角。
pub fn badge_at(skill: usize) -> (i32, i32) {
    let (x, y) = ICON[skill.min(2)];
    (x + 40 + 2 - BADGE.0, y + 40 + 2 - BADGE.1)
}

/// 名字标签里是游戏的文字引用 `#asset/base/text/champion?description.<英雄>.name`（电竞大脑的 balance_view 也这么读）。
pub fn champion_of(text: &str) -> Option<&str> {
    text.trim().strip_prefix("#asset/base/text/champion?description.")?.strip_suffix(".name")
}

/// 数字牌的 .ui 源（`ui_spawn_source` 用的和 .ui 文件一样的写法）：半透明黑底、圆角，白字。
pub fn badge_source(name: &str, (x, y): (i32, i32)) -> String {
    let (w, h) = BADGE;
    format!(
        r##"{name}:color {{
  x: {x}px;
  y: {y}px;
  width: {w}px;
  height: {h}px;
  color: #000000d0;
  ignore_event: true;

  rounding: Uniform {{
    rounding: 4;
  }}

  #value:label {{
    @"asset/base/style/main#bold_label";
    width: 100%;
    height: 100%;
    size: 13;
    align_x: Center;
    align_y: Center;
    ignore_event: true;
    text: "";
  }}
}}
"##
    )
}

/// 每帧（league.dll / tft.dll 的客户端扩展）：大面板开着、名字是屏幕上这一局里表上的英雄，就把层数叠在他那个技能的图标
/// 右下角；别的时候把数字牌藏起来。数字牌的名字带包的前缀（`league_stack_tip` / `tft_stack_tip`），两个 DLL 各管各的英雄。
pub fn tip(ctx: &mut StableClient<'_>) {
    static AT: Mutex<Option<String>> = Mutex::new(None);
    static LAST: Mutex<Option<(usize, usize)>> = Mutex::new(None);
    static SEEN: Mutex<bool> = Mutex::new(false);
    if !ctx.ui_exists(MATCH_ROOT) {
        return;
    }
    let tip = {
        let mut at = AT.lock().unwrap_or_else(|e| e.into_inner());
        if !at.as_ref().is_some_and(|p| ctx.ui_exists(p)) {
            // 先找比赛画面的根下面，再翻一遍界面的每个根
            *at = std::iter::once(MATCH_ROOT.to_string())
                .chain(ctx.ui_child_names(""))
                .map(|r| format!("{r}.{TIP}"))
                .find(|p| ctx.ui_exists(p));
        }
        match at.clone() {
            Some(p) => p,
            None => return,
        }
    };
    let name = format!("{PREFIX}stack_tip");
    let badge = format!("{tip}.{name}");
    let label = (ctx.ui_visible(&tip) == Some(true)).then(|| ctx.ui_text(&format!("{tip}.header.name"))).flatten();
    if label.is_some() && !std::mem::replace(&mut *SEEN.lock().unwrap_or_else(|e| e.into_inner()), true) {
        crate::wlog(format!("STACKS TIP {tip}: the name label reads {label:?}"));
    }
    let want = label.as_deref().and_then(champion_of).filter(|id| id.starts_with(PREFIX)).and_then(shown);
    let mut last = LAST.lock().unwrap_or_else(|e| e.into_inner());
    let Some((n, k)) = want else {
        if last.take().is_some() && ctx.ui_exists(&badge) {
            ctx.ui_set_visible(&badge, false);
        }
        return;
    };
    let pos = badge_at(k);
    if !ctx.ui_exists(&badge) {
        *last = None;
        if !ctx.ui_spawn_source(&tip, &badge_source(&name, pos)) {
            return;
        }
    }
    if *last != Some((n, k)) {
        ctx.ui_set_properties(&badge, &format!("x: {}px; y: {}px;", pos.0, pos.1));
        ctx.ui_set_text(&format!("{badge}.value"), &n.to_string());
        ctx.ui_set_visible(&badge, true);
        *last = Some((n, k));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The 0.7.1 host's `entity_stat` and `entity_set_base_stat` (TeamfightManager2.exe RVA 0x34953c0 / 0x3499220).
    const GETTER: &str = "55 56 48 83 ec 28 48 8d 6c 24 20 48 c7 45 00 fe ff ff ff 48 85 d2 74 5c 4c 89 c6 48 ff ca 48 8b 01 \
        4c 8b 41 08 48 89 c1 41 ff 90 08 02 00 00 90 48 85 c0 74 3f 48 8b 88 50 06 00 00 0f 10 80 10 06 00 00 0f 10 88 20 06 00 00 \
        0f 10 90 30 06 00 00 0f 10 98 40 06 00 00 0f 11 06 0f 11 4e 10 0f 11 56 20 0f 11 5e 30 48 89 4e 40 b0 01 48 83 c4";
    const SETTER: &str = "55 56 48 83 ec 28 48 8d 6c 24 20 48 c7 45 00 fe ff ff ff 4d 85 c0 74 7a 48 85 c9 74 14 31 c0 48 85 \
        d2 74 06 80 79 18 00 74 0c 48 83 c4 28 5e 5d c3 48 85 d2 74 5c 4c 89 c6 48 ff ca 48 8b 01 4c 8b 41 08 48 89 c1 41 ff 90 10 \
        02 00 00 90 48 85 c0 74 3f 48 8b 4e 40 0f 10 06 0f 10 4e 10 0f 10 56 20 0f 10 5e 30 0f 11 80 c8 05 00 00 0f 11 88 d8 05 \
        00 00 0f 11 90 e8 05 00 00 0f 11 98 f8 05 00 00 48 89 88 08 06 00 00 b0 01 48 83 c4 28 5e";

    fn bytes(s: &str) -> Vec<u8> {
        s.split_whitespace().map(|h| u8::from_str_radix(h, 16).unwrap()).collect()
    }

    #[test]
    fn the_host_s_own_code_gives_the_layout() {
        let l = layout(&bytes(GETTER), &bytes(SETTER)).expect("0.7.1's layout");
        assert_eq!(l, Layout { get_slot: 0x208, base: 0x5c8, calc: 0x610 });
    }

    #[test]
    fn a_layout_not_understood_writes_nothing() {
        let (g, s) = (bytes(GETTER), bytes(SETTER));
        // the calculated block moved away from the base: not the layout we know
        let moved = GETTER.replace("10 06 00 00", "10 07 00 00").replace("20 06 00 00", "20 07 00 00")
            .replace("30 06 00 00", "30 07 00 00").replace("40 06 00 00", "40 07 00 00").replace("50 06 00 00", "50 07 00 00");
        assert_eq!(layout(&bytes(&moved), &s), None);
        // a store missing from the setter
        let mut cut = s.clone();
        let at = cut.windows(3).position(|w| w == [0x0f, 0x11, 0x90]).unwrap();
        cut[at + 2] = 0x91;
        assert_eq!(layout(&g, &cut), None);
        // no world call
        assert_eq!(layout(&g[40..], &s), None);
        assert_eq!(layout(&[], &[]), None);
    }

    fn buffs(names: &[&str]) -> Vec<BuffV1> {
        names.iter().map(|n| BuffV1::named(n)).collect()
    }

    fn power(name: &str, ap: i32) -> BuffV1 {
        let mut b = BuffV1::named(name);
        b.magic_power = ap;
        b
    }

    #[test]
    fn counts_sums_and_ladders() {
        let b = buffs(&["league_veigar_p_stack", "x", "league_veigar_p_stack", "league_veigar_p_stack_old"]);
        assert_eq!(count(Rule::Count("league_veigar_p_stack"), &b), 2);
        let s = [power("league_veigar_p_stack", 1), power("league_veigar_p_stack", 5), power("x", 9),
                 power("league_veigar_p_stack", 1)];
        assert_eq!(count(Rule::Sum("league_veigar_p_stack", Stat::MagicPower), &s), 7,
                   "a champion's stack is 5 ability power: League's 5 stacks");
        assert_eq!(count(Rule::Sum("league_veigar_p_stack", Stat::Hp), &s), 0);
        let ladder = Rule::Ladder { prefix: "league_aurelionsol_d", rungs: 30, step: 1, full: None };
        let l = buffs(&["league_aurelionsol_d1", "league_aurelionsol_d2", "league_aurelionsol_d12", "league_aurelionsol_dash",
                        "league_aurelionsol_d31"]);
        assert_eq!(count(ladder, &l), 12, "the top rung, nothing past the ladder, no other name with the prefix");
        assert_eq!(count(ladder, &buffs(&["league_aurelionsol_c1"])), 0);
        let heat = Rule::Ladder { prefix: "league_rumble_h", rungs: 9, step: 10, full: Some(("league_rumble_oh", 100)) };
        assert_eq!(count(heat, &buffs(&["league_rumble_h3", "league_rumble_hot"])), 30, "a step of heat is 10");
        assert_eq!(count(heat, &buffs(&["league_rumble_h9", "league_rumble_oh"])), 100, "overheated: the flag's number");
        assert_eq!(count(heat, &[]), 0);
    }

    #[test]
    fn most_total_and_prefix() {
        let yasuo = Rule::Most(&[("league_yasuo_q_stack", 1), ("league_yasuo_q_ready", 2)]);
        assert_eq!(count(yasuo, &buffs(&["league_yasuo_q_stack"])), 1);
        assert_eq!(count(yasuo, &buffs(&["x", "league_yasuo_q_ready"])), 2);
        assert_eq!(count(yasuo, &[]), 0);
        let ammo = Rule::Total(&[("league_aphelios_b0", 1), ("league_aphelios_b1", 2), ("league_aphelios_b2", 4),
                                 ("league_aphelios_b3", 8), ("league_aphelios_b4", 16)]);
        assert_eq!(count(ammo, &buffs(&["league_aphelios_b2", "league_aphelios_b4"])), 20, "20 = 0b10100");
        assert_eq!(count(ammo, &buffs(&["league_aphelios_b0", "league_aphelios_b0"])), 1, "a name counts once");
        let blaze = Rule::Prefix("league_brand_bz_");
        assert_eq!(count(blaze, &buffs(&["league_brand_bz_17", "league_brand_bz_17", "league_brand_b_1"])), 2);
    }

    #[test]
    fn foes_read_the_enemy_with_the_most() {
        let st = Stack {
            hero: "league_varus",
            rule: Rule::Ladder { prefix: "league_varus_blight_", rungs: 3, step: 1, full: None },
            cap: 3,
            foes: true,
            skill: 0,
        };
        let (a, b) = (buffs(&["league_varus_blight_1"]), buffs(&["league_varus_blight_2", "league_varus_blight_1"]));
        let mine = buffs(&["league_varus_blight_3"]);
        let none = [0; 3];
        assert_eq!(value(&st, &mine, &none, &[&a, &b]), 2, "the most on one enemy, not his own");
        assert_eq!(value(&st, &mine, &none, &[]), 0);
        let own = Stack { foes: false, ..st };
        assert_eq!(value(&own, &mine, &none, &[&a, &b]), 3);
        assert_eq!(value(&Stack { cap: 2, ..own }, &mine, &none, &[]), 2, "capped");
    }

    #[test]
    fn per_divides_the_stat_by_a_stack() {
        // 赛芬的怒气：一个 buff，攻击力是层数 x 5
        let mut rage = BuffV1::named("tft_syfen_p_rage");
        rage.attack = 15;
        assert_eq!(count(Rule::Per("tft_syfen_p_rage", Stat::Attack, 5), &[rage]), 3);
        // 麦迪的赏金（攻速倍率）、呲呲的冒险家之魂（护甲）、峡谷先锋的甲壳（受到的伤害减少）
        let mut bounty = BuffV1::named("tft_maddie_p_bounty");
        bounty.attack_speed_mult = 45;
        assert_eq!(count(Rule::Per("tft_maddie_p_bounty", Stat::AttackSpeedMult, 15), &[bounty]), 3);
        let mut guild = BuffV1::named("tft_zippy_p_guild");
        guild.defence = 20;
        assert_eq!(count(Rule::Per("tft_zippy_p_guild", Stat::Defence, 10), &[guild]), 2);
        let mut shell = BuffV1::named("tft_riftherald_p_shell");
        shell.damaged_reduce = 12;
        assert_eq!(count(Rule::Sum("tft_riftherald_p_shell", Stat::DamagedReduce), &[shell]), 12);
        assert_eq!(count(Rule::Per("tft_zippy_p_guild", Stat::Defence, 10), &[]), 0);
        guild.defence = 14;
        assert_eq!(count(Rule::Per("tft_zippy_p_guild", Stat::Defence, 10), &[guild]), 1, "rounded");
    }

    fn cooldown(unlocked: bool, max_charges: usize, charges: usize) -> Option<CooldownV1> {
        Some(CooldownV1 { unlocked, max_charges, charges, ..CooldownV1::default() })
    }

    #[test]
    fn charges_come_from_the_skill_slot() {
        assert_eq!(slot_of(0), Some(SkillSlotV1::Skill));
        assert_eq!(slot_of(2), Some(SkillSlotV1::Ult));
        assert_eq!(slot_of(3), None);
        assert_eq!(charges_now(cooldown(true, 3, 2)), 2, "two mushrooms left");
        assert_eq!(charges_now(cooldown(false, 3, 3)), 0, "the ult not learnt yet");
        assert_eq!(charges_now(cooldown(true, 1, 1)), 0, "not a skill with charges");
        assert_eq!(charges_now(cooldown(true, 3, 7)), 3);
        assert_eq!(charges_now(None), 0, "an old host");
        let st = Stack { hero: "league_teemo", rule: Rule::Charges(2), cap: 3, foes: false, skill: 2 };
        let mine = buffs(&["league_teemo_r_alive_a"]);
        assert_eq!(value(&st, &mine, &[0, 0, 2], &[]), 2);
        assert_eq!(value(&st, &mine, &[3, 3, 0], &[]), 0, "the ult's slot only");
        assert_eq!(count(Rule::Charges(2), &mine), 0, "no buff counts");
    }

    #[test]
    fn the_table_is_sound() {
        // 表里的英雄都以表的前缀开头（league.dll 的 league_，tft.dll 的 tft_：两个 DLL 共用这个文件）
        let prefix = PREFIX;
        for st in STACKS.iter() {
            assert!(st.hero.starts_with(prefix) && st.cap > 0, "{}", st.hero);
            // 他自己身上的名字以他开头；敌人身上的可以是附加包起的名字（图奇的毒 league_takedowns_tw_v<n>）
            let own = |n: &str| if st.foes { n.starts_with(prefix) } else { n.starts_with(st.hero) };
            match st.rule {
                Rule::Count(b) | Rule::Sum(b, _) | Rule::Prefix(b) => assert!(own(b), "{} counts {b}", st.hero),
                Rule::Ladder { prefix, rungs, step, full } => {
                    assert!(own(prefix) && rungs > 0 && step > 0, "{} climbs {prefix}", st.hero);
                    assert!(full.is_none_or(|(f, top)| own(f) && top <= st.cap), "{}", st.hero);
                }
                Rule::Most(names) | Rule::Total(names) => {
                    assert!(!names.is_empty() && names.iter().all(|&(n, v)| own(n) && v > 0), "{}", st.hero);
                }
                Rule::Charges(k) => assert!(slot_of(k).is_some() && !st.foes, "{} charges {k}", st.hero),
                Rule::Per(b, _, per) => assert!(own(b) && per > 0, "{} counts {b} by {per}", st.hero),
            }
        }
        // 同一个英雄的几行挨在一起（表按英雄排序）
        for w in STACKS.windows(3) {
            assert!(!(w[0].hero == w[2].hero && w[1].hero != w[0].hero), "{} split", w[0].hero);
        }
        // 层数格配的技能是三个技能格之一，一个英雄的几行一样（大面板只叠一个数字牌）
        for st in STACKS.iter() {
            assert!(st.skill <= 2 && st.skill == skill_of(st.hero), "{} skill {}", st.hero, st.skill);
        }
    }

    #[test]
    fn falling_behind_is_counted_per_unit_and_never_turns_anything_off() {
        let mut lag = HashMap::new();
        for k in 1..LAG_LOG {
            assert!(!lag_step(&mut lag, 7, true), "round {k}: not yet");
        }
        assert!(lag_step(&mut lag, 7, true), "the 40th round in a row: one log line");
        assert!(!lag_step(&mut lag, 7, true), "only once");
        assert!(!lag_step(&mut lag, 9, true), "another unit counts on its own");
        assert!(!lag_step(&mut lag, 7, false), "caught up");
        assert_eq!(lag.get(&7), None, "counting starts again");
        assert_eq!(lag.get(&9), Some(&1));
    }

    #[test]
    fn the_tooltip_names_its_champion_by_reference() {
        assert_eq!(champion_of("#asset/base/text/champion?description.league_smolder.name"), Some("league_smolder"));
        assert_eq!(champion_of(" #asset/base/text/champion?description.tft_maddie.name "), Some("tft_maddie"));
        assert_eq!(champion_of("斯莫德"), None, "a plain name: no badge");
        assert_eq!(champion_of("#asset/base/text/champion?description.league_smolder.title"), None);
    }

    #[test]
    fn the_badge_sits_on_the_skill_icons_corner() {
        assert_eq!(badge_at(0), (45, 246), "Q's icon is 40 x 40 at (33, 222): 2 past its bottom right");
        assert_eq!(badge_at(1), (45, 354));
        assert_eq!(badge_at(2), (45, 462));
        assert_eq!(badge_at(9), badge_at(2));
        let src = badge_source("league_stack_tip", badge_at(2));
        assert!(src.starts_with("league_stack_tip:color {"), "{src}");
        assert!(src.contains("x: 45px;") && src.contains("y: 462px;") && src.contains("#value:label {"), "{src}");
        assert_eq!(src.matches('{').count(), src.matches('}').count(), "{src}");
    }

    #[test]
    fn the_shown_numbers_belong_to_one_match() {
        shown_put((1, 0), "test_hero_a", 12);
        shown_put((1, 0), "test_hero_b", 3);
        assert_eq!(shown("test_hero_a").map(|s| s.0), Some(12));
        shown_put((1, 0), "test_hero_a", 13);
        assert_eq!(shown("test_hero_a").map(|s| s.0), Some(13));
        shown_put((1, 1), "test_hero_b", 1);
        assert_eq!(shown("test_hero_a"), None, "the next game of the series starts empty");
        assert_eq!(shown("test_hero_b").map(|s| s.0), Some(1));
    }
}
