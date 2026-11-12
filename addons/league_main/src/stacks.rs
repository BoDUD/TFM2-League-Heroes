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
//! **写进 `stack`。** 稳定接口改属性只有 `entity_set_base_stat`：整块换掉基础属性（9 项）。可 `stat()` 读到的是算好的那块
//! （经典 SDK 0.5.1 的 `Entity::calculate_stat_cached`：每项 = (基础 + buff 的加值) x (100 + buff 的倍率) / 100，
//! `stack` = 基础的 `stack`），拿它当基础写回去，buff 就进了基础属性。所以 [`layout`] 从宿主自己这两个函数的机器码里读出：
//! 读属性时从世界取英雄用的是世界的第几个函数、算好的那块在英雄的哪里；写基础属性时写到英雄的哪里——两块必须正好挨着
//! （基础 9 项之后紧接算好的 9 项，0.7.1 是 +0x5c8 和 +0x610），对不上就整个关掉（日志一行 `STACK LAYOUT`），不再写。
//! 写的时候先照宿主的取法读出这个英雄现在的基础属性，只换 `stack`，用官方的 `entity_set_base_stat` 写回，再读一次核对；
//! 写之前算好的 `stack` 和基础的对不上（布局读错了）也不写。复活时游戏重算基础属性（`stack` 回到 0），下一次看就又写上。
//! 每份模拟（屏幕上的比赛、服务器的预演）在同样的 tick 做同样的事，src/diverge.rs 的快照（含 `stack`）里它们也一样。
//! `stack` 对数据英雄没有别的作用（只有原版英雄自己的原生代码读它）。

use std::collections::HashMap;
use std::sync::{Mutex, OnceLock};

use mod_api_stable::*;

pub use crate::stack_table::STACKS;

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
}

/// [`Rule::Sum`] 加哪一项。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stat {
    MagicPower,
    Hp,
    Attack,
}

impl Stat {
    pub fn of(self, b: &BuffV1) -> i64 {
        match self {
            Stat::MagicPower => b.magic_power as i64,
            Stat::Hp => b.hp as i64,
            Stat::Attack => b.attack as i64,
        }
    }
}

/// 一个显示层数的英雄。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Stack {
    pub hero: &'static str,
    pub rule: Rule,
    /// 最多显示到这个数。
    pub cap: usize,
}

/// 隔几 tick 数一次（0.1 秒）：层数变了，面板上最多晚这么久。
pub const EVERY: usize = 6;

/// 他身上的 buff -> 层数。
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
    }
}

/// 表里的这个英雄。
pub fn find(hero: &str) -> Option<&'static Stack> {
    STACKS.iter().find(|s| s.hero == hero)
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

/// 写坏了（读回来不对，或者算好的 `stack` 和基础的对不上太多次）就不再写。
static OFF: Mutex<bool> = Mutex::new(false);
/// 算好的和基础的 `stack` 对不上的次数（刚写过的那几 tick 算好的还没跟上，偶尔一次不算错）。
static MISMATCH: Mutex<usize> = Mutex::new(0);
const MISMATCH_MAX: usize = 40;
/// 每个英雄最多记几行 `STACKS`。
static LOGGED: Mutex<Option<HashMap<&'static str, usize>>> = Mutex::new(None);
const LOG_LINES: usize = 40;

fn note(st: &Stack, id: usize, was: usize, now: usize, base: &StatV1, calc: &StatV1) {
    let mut guard = LOGGED.lock().unwrap_or_else(|e| e.into_inner());
    let n = guard.get_or_insert_with(HashMap::new).entry(st.hero).or_insert(0);
    if *n >= LOG_LINES {
        return;
    }
    *n += 1;
    crate::wlog(format!(
        "STACKS {}#{id}: {was} -> {now} (base attack {} ap {} hp {} def {} mr {} ms {}; calculated {} / {} / {} / {} / {} / {})",
        st.hero, base.attack, base.magic_power, base.hp, base.defence, base.magic_resistance, base.move_speed, calc.attack,
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

/// 比赛钩子（src/lib.rs 的 `Match`）每 tick 调一次。
pub fn on_tick(sim: &mut StableSim<'_>) {
    if sim.tick() % EVERY != 0 || *OFF.lock().unwrap_or_else(|e| e.into_inner()) {
        return;
    }
    let ids: Vec<usize> = (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).collect();
    for id in ids {
        let Some(e) = sim.get_entity(id) else { continue };
        let Some(st) = e.name().and_then(|n| find(&n)) else { continue };
        if !e.is_alive() {
            continue;
        }
        let buffs: Vec<BuffV1> = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).collect();
        let n = count(st.rule, &buffs).min(st.cap);
        let calc = e.stat();
        let Some(l) = host_layout(sim) else { return };
        let Some(base) = read_base(sim, l, id) else { continue };
        if base.stack == n {
            continue;
        }
        if calc.stack != base.stack {
            let mut m = MISMATCH.lock().unwrap_or_else(|e| e.into_inner());
            *m += 1;
            if *m > MISMATCH_MAX {
                drop(m);
                off(format!("{}#{id}: the calculated stack {} is not the base's {} ({MISMATCH_MAX} times)", st.hero,
                            calc.stack, base.stack));
                return;
            }
            continue;
        }
        let mut want = base;
        want.stack = n;
        sim.entity_set_base_stat(id, &want);
        match read_base(sim, l, id) {
            Some(back) if back == want => note(st, id, base.stack, n, &base, &calc),
            back => {
                off(format!("{}#{id}: wrote stack {n}, read back {back:?}", st.hero));
                return;
            }
        }
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
    fn the_table_is_sound() {
        for st in STACKS.iter() {
            assert!(st.hero.starts_with("league_") && st.cap > 0, "{}", st.hero);
            match st.rule {
                Rule::Count(b) | Rule::Sum(b, _) => assert!(b.starts_with(st.hero), "{} counts {b}", st.hero),
                Rule::Ladder { prefix, rungs, step, full } => {
                    assert!(prefix.starts_with(st.hero) && rungs > 0 && step > 0, "{} climbs {prefix}", st.hero);
                    assert!(full.is_none_or(|(f, top)| f.starts_with(st.hero) && top <= st.cap), "{}", st.hero);
                }
            }
        }
    }
}
