//! 头顶的层数（0.9.29，2026-11-11）。用户：「现在叠层数的技能英雄在游戏里看不到多少层 有没有办法在游戏里能看到？」，选了
//! 「办法1」：英雄头顶一个数字。
//!
//! 数据只能问「身上有没有某个 buff」（`SwitchByBuff`），数不出有几层：一层就是同名 buff 多一个（维迦的
//! `league_veigar_p_stack`），或者梯子爬上一级（奥瑞利安·索尔的 `league_aurelionsol_d1`..`d30`）；游戏的显示世界一个名字
//! 也只记一个（hd_engine 的 `grow_count`），客户端也数不出来。所以在模拟里数：比赛钩子每 [`EVERY`] tick 看一次
//! [`STACKS`]（src/stack_table.rs，tools/kit/stack_nums.py 生成）里的英雄——[`Rule::Count`] 数他身上那个 buff 有几个，
//! [`Rule::Sum`] 把那些 buff 的一项数值加起来（维迦击杀英雄那一层是 5 点法强：英雄联盟的层数就是法强），[`Rule::Ladder`]
//! 看梯子爬到第几级——给他挂不带任何数值的显示 buff，一位数字一个：`<英雄>_sn_y<高>槽<数字>`
//! （[`names`]）。主包里这个英雄的 view_buffs（和附加包的副本里的）把每个名字画成公用图 league_stack_num 里的那一格：
//! 数字的中心在他头顶 Y 个游戏像素（stack_nums.py 按他的帧量的；科加斯按盛宴的层数长高，[`Stack::ys`] 一层一个高度）。
//!
//! 数字变了才换：去掉不该有的、挂上缺的，别的不动（一位数字一个名字，显示世界正好一个名字一个画面）。死了全去掉
//! ——数字不跟着尸体；复活后下一次看就又挂上（附加包补回层数的英雄，补回的那一刻也就对了）。每一份模拟（屏幕上的比赛、
//! 服务器的预演）在同样的 tick 做同样的事，src/diverge.rs 的快照里它们也一样。超过 [`Stack::cap`] 的显示上限。

use std::collections::HashMap;
use std::sync::Mutex;

use mod_api_stable::*;

pub use crate::stack_table::STACKS;

/// 怎么从英雄自己的 buff 读出层数。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Rule {
    /// 这个 buff 有几个（一层多一个）。
    Count(&'static str),
    /// 这个 buff 的一项数值加起来（一层的大小不一样时：维迦击杀英雄那一层 5 点法强，英雄联盟算 5 层）。
    Sum(&'static str, Stat),
    /// 梯子 `<前缀>1`..`<前缀>n` 里身上最高的那一级。
    Ladder(&'static str, usize),
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
    /// 最多显示到这个数（也决定最多几位）。
    pub cap: usize,
    /// 数字的中心在他头顶多高：1 层、2 层……各一个（只有一个就是哪层都一样；层数比表长就用最后一个）。
    pub ys: &'static [u16],
}

/// 隔几 tick 数一次（0.1 秒）：层数变了，数字最多晚这么久。
pub const EVERY: usize = 6;

/// 显示 buff 的名字里这一段之后是图里的格子名。
pub const MARK: &str = "_sn_";

/// `n` 显示成哪几位：(槽, 数字)，一位数 a，两位数 b c，三位数 d e f；0 什么都不显示。
pub fn slots(n: usize) -> Vec<(char, u8)> {
    let s = n.to_string();
    let slot_names: &[char] = match s.len() {
        1 => &['a'],
        2 => &['b', 'c'],
        _ => &['d', 'e', 'f'],
    };
    if n == 0 {
        return Vec::new();
    }
    slot_names.iter().zip(s.bytes()).map(|(&c, b)| (c, b - b'0')).collect()
}

/// 层数 `n` 的高度。
pub fn y_for(ys: &[u16], n: usize) -> u16 {
    ys[n.clamp(1, ys.len()) - 1]
}

/// 这个英雄身上该有的显示 buff（`n` 先截到上限）。
pub fn names(st: &Stack, n: usize) -> Vec<String> {
    let n = n.min(st.cap);
    let y = y_for(st.ys, n);
    slots(n).into_iter().map(|(c, d)| format!("{}{MARK}y{y}{c}{d}", st.hero)).collect()
}

/// 他身上的 buff -> 层数。
pub fn count(rule: Rule, buffs: &[BuffV1]) -> usize {
    match rule {
        Rule::Count(name) => buffs.iter().filter(|b| b.name() == name).count(),
        Rule::Sum(name, stat) => {
            buffs.iter().filter(|b| b.name() == name).map(|b| stat.of(b)).sum::<i64>().max(0) as usize
        }
        Rule::Ladder(prefix, rungs) => buffs
            .iter()
            .filter_map(|b| b.name().strip_prefix(prefix)?.parse::<usize>().ok())
            .filter(|k| (1..=rungs).contains(k))
            .max()
            .unwrap_or(0),
    }
}

/// 表里的这个英雄。
pub fn find(hero: &str) -> Option<&'static Stack> {
    STACKS.iter().find(|s| s.hero == hero)
}

/// (要去掉的, 要挂上的)：身上的显示 buff `shown` 和该有的 `want` 比。
pub fn diff(shown: &[String], want: &[String]) -> (Vec<String>, Vec<String>) {
    let mut drop: Vec<String> = shown.iter().filter(|s| !want.contains(s)).cloned().collect();
    drop.sort();
    drop.dedup();
    let add = want.iter().filter(|w| !shown.contains(w)).cloned().collect();
    (drop, add)
}

/// 每个英雄最近一次记日志的层数（每种变化记一行，`LOG_LINES` 行为止）。
static LOGGED: Mutex<Option<HashMap<&'static str, usize>>> = Mutex::new(None);
const LOG_LINES: usize = 40;

fn note(st: &Stack, id: usize, was: usize, now: usize, alive: bool, add: &[String]) {
    let mut guard = LOGGED.lock().unwrap_or_else(|e| e.into_inner());
    let lines = guard.get_or_insert_with(HashMap::new);
    let n = lines.entry(st.hero).or_insert(0);
    if *n >= LOG_LINES {
        return;
    }
    *n += 1;
    crate::wlog(format!("STACKS {}#{id}: {was} -> {now}{} {}", st.hero, if alive { "" } else { " (dead: none shown)" },
                        if add.is_empty() { String::new() } else { format!("[{}]", add.join(" ")) }));
}

/// 比赛钩子（src/lib.rs 的 `Match`）每 tick 调一次。
pub fn on_tick(sim: &mut StableSim<'_>) {
    if sim.tick() % EVERY != 0 {
        return;
    }
    let ids: Vec<usize> = (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).collect();
    for id in ids {
        let Some(e) = sim.get_entity(id) else { continue };
        let Some(st) = e.name().and_then(|n| find(&n)) else { continue };
        let alive = e.is_alive();
        let prefix = format!("{}{MARK}", st.hero);
        let mut buffs = Vec::new();
        let mut shown = Vec::new();
        for b in (0..e.buff_count()).filter_map(|i| e.buff_at(i)) {
            if b.name().starts_with(&prefix) {
                shown.push(b.name().to_string());
            } else {
                buffs.push(b);
            }
        }
        let n = if alive { count(st.rule, &buffs) } else { 0 };
        let want = names(st, n);
        let (drop, add) = diff(&shown, &want);
        if drop.is_empty() && add.is_empty() {
            continue;
        }
        let was = shown_number(st, &shown);
        for name in &drop {
            sim.entity_remove_buff(id, name);
        }
        for name in &add {
            sim.add_buff(id, &BuffV1::named(name));
        }
        note(st, id, was, n.min(st.cap), alive, &add);
    }
}

/// 身上的显示 buff 读回的数字（日志用；读不出就 0）。
pub fn shown_number(st: &Stack, shown: &[String]) -> usize {
    let prefix = format!("{}{MARK}", st.hero);
    let mut digits: Vec<(char, u8)> = shown
        .iter()
        .filter_map(|s| {
            let tag = s.strip_prefix(&prefix)?;
            let mut it = tag.chars().rev();
            let d = it.next()?.to_digit(10)? as u8;
            let slot = it.next()?;
            Some((slot, d))
        })
        .collect();
    digits.sort();
    digits.iter().fold(0, |acc, (_, d)| acc * 10 + *d as usize)
}

#[cfg(test)]
mod tests {
    use super::*;

    const VEIGAR: Stack =
        Stack { hero: "league_veigar", rule: Rule::Sum("league_veigar_p_stack", Stat::MagicPower), cap: 999, ys: &[34] };
    const GROWING: Stack = Stack { hero: "league_chogath", rule: Rule::Count("league_chogath_r_stack"), cap: 99,
                                   ys: &[57, 71, 86] };
    const LADDER: Stack = Stack { hero: "league_aurelionsol", rule: Rule::Ladder("league_aurelionsol_d", 30), cap: 30,
                                  ys: &[39] };

    #[test]
    fn a_number_is_one_buff_a_digit_in_its_slots() {
        assert!(slots(0).is_empty());
        assert_eq!(slots(7), vec![('a', 7)]);
        assert_eq!(slots(40), vec![('b', 4), ('c', 0)]);
        assert_eq!(slots(137), vec![('d', 1), ('e', 3), ('f', 7)]);
        assert_eq!(names(&VEIGAR, 37), vec!["league_veigar_sn_y34b3", "league_veigar_sn_y34c7"]);
        assert_eq!(names(&VEIGAR, 1200), names(&VEIGAR, 999), "the cap");
        assert!(names(&VEIGAR, 0).is_empty());
    }

    #[test]
    fn a_growing_hero_s_number_rides_higher_with_his_stacks() {
        assert_eq!(names(&GROWING, 1), vec!["league_chogath_sn_y57a1"]);
        assert_eq!(names(&GROWING, 3), vec!["league_chogath_sn_y86a3"]);
        assert_eq!(names(&GROWING, 12), vec!["league_chogath_sn_y86b1", "league_chogath_sn_y86c2"], "past the table: its last");
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
        assert_eq!(count(VEIGAR.rule, &s), 7, "a champion's stack is 5 ability power: League's 5 stacks");
        assert_eq!(count(Rule::Sum("league_veigar_p_stack", Stat::Hp), &s), 0);
        let l = buffs(&["league_aurelionsol_d1", "league_aurelionsol_d2", "league_aurelionsol_d12", "league_aurelionsol_dash",
                        "league_aurelionsol_d31"]);
        assert_eq!(count(LADDER.rule, &l), 12, "the top rung, nothing past the ladder, no other name with the prefix");
        assert_eq!(count(LADDER.rule, &buffs(&["league_aurelionsol_c1"])), 0);
    }

    #[test]
    fn only_the_changed_digits_move() {
        let shown = names(&VEIGAR, 37);
        let (drop, add) = diff(&shown, &names(&VEIGAR, 38));
        assert_eq!(drop, vec!["league_veigar_sn_y34c7"]);
        assert_eq!(add, vec!["league_veigar_sn_y34c8"]);
        let (drop, add) = diff(&shown, &names(&VEIGAR, 37));
        assert!(drop.is_empty() && add.is_empty());
        let (drop, add) = diff(&shown, &[]);
        assert_eq!((drop.len(), add.len()), (2, 0), "dead: all of them go");
        assert_eq!(shown_number(&VEIGAR, &names(&VEIGAR, 137)), 137);
        assert_eq!(shown_number(&VEIGAR, &[]), 0);
    }

    #[test]
    fn the_table_is_sound() {
        for st in STACKS.iter() {
            assert!(st.hero.starts_with("league_"), "{}", st.hero);
            assert!(!st.ys.is_empty() && st.cap > 0, "{}", st.hero);
            // every name fits a buff name (the API cuts at 64 bytes)
            for n in [1, 9, 10, 99, 100, st.cap] {
                for name in names(st, n) {
                    assert!(name.len() <= BUFF_NAME_CAP, "{name}");
                }
            }
            match st.rule {
                Rule::Count(b) | Rule::Sum(b, _) => assert!(b.starts_with(st.hero), "{} counts {b}", st.hero),
                Rule::Ladder(p, n) => assert!(p.starts_with(st.hero) && n > 0, "{} climbs {p}", st.hero),
            }
        }
    }
}
