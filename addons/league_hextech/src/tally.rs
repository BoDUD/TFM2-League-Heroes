//! 海克斯起没起作用的账（0.5.2，用户 2026-11-27：「海克斯乱斗确定全生效了吗」→「做 0.5.2」）。
//!
//! 每份模拟结束时记一笔（[`add`]）：这一局有人拿着的每个海克斯起没起作用。会触发的看这一局触发过没有（[`crate::procs::Procs`]
//! 的 `count`）；属性类和歌利亚巨人看它的 buff 在不在拿着它的人身上（人死着的这一局不算）。整次启动累计，[`line`] 写成日志里的
//! `TALLY` 一行：拿着却一次没起作用的排最前面，然后是还没人拿过的，最后是每个的「起作用的局数 / 拿着的局数」和一共触发了几次。
//! 只记数，不碰比赛。

use std::sync::Mutex;

use crate::augments::{Ev, AUGS};

/// 每结束这么多份模拟写一行 `TALLY`（屏幕上那一场结束时也写）。
pub const EVERY: u64 = 20;

/// 一个海克斯在这一局里怎么样。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Seen {
    /// 会触发的：这一局触发了几次（0 = 拿着没触发）
    Fired(u32),
    /// 属性类：buff 在不在拿着它的人身上
    On(bool),
}

/// 属性类（拿到就挂上的 buff 就是全部效果）：看 buff 在不在。
pub fn by_buff(ev: Ev) -> bool {
    matches!(ev, Ev::Stat | Ev::Goliath)
}

struct Book {
    sims: u64,
    /// 有人拿着的局数
    held: Vec<u32>,
    /// 其中起了作用的局数
    worked: Vec<u32>,
    /// 会触发的一共触发了几次
    times: Vec<u64>,
}

static BOOK: Mutex<Book> = Mutex::new(Book { sims: 0, held: Vec::new(), worked: Vec::new(), times: Vec::new() });

/// 记一份结束的模拟（`seen`：这一局有人拿着的，每个一条）。-> 一共结束了几份
pub fn add(seen: &[(usize, Seen)]) -> u64 {
    let mut b = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    if b.held.len() != AUGS.len() {
        b.held = vec![0; AUGS.len()];
        b.worked = vec![0; AUGS.len()];
        b.times = vec![0; AUGS.len()];
    }
    b.sims += 1;
    for &(a, s) in seen {
        if a >= AUGS.len() {
            continue;
        }
        b.held[a] += 1;
        let worked = match s {
            Seen::Fired(n) => {
                b.times[a] += n as u64;
                n > 0
            }
            Seen::On(on) => on,
        };
        if worked {
            b.worked[a] += 1;
        }
    }
    b.sims
}

/// 现在的账，一行（不带前面的 `[..] t=..`）。
pub fn line() -> String {
    let b = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    let n = AUGS.len();
    let held = |a: usize| b.held.get(a).copied().unwrap_or(0);
    let worked = |a: usize| b.worked.get(a).copied().unwrap_or(0);
    let quiet: Vec<String> =
        (0..n).filter(|&a| held(a) > 0 && worked(a) == 0).map(|a| format!("{} 0/{}", AUGS[a].key, held(a))).collect();
    let never: Vec<&str> = (0..n).filter(|&a| held(a) == 0).map(|a| AUGS[a].key).collect();
    let all: Vec<String> = (0..n)
        .filter(|&a| held(a) > 0)
        .map(|a| {
            if by_buff(AUGS[a].ev) {
                format!("{} {}/{}", AUGS[a].key, worked(a), held(a))
            } else {
                format!("{} {}/{} x{}", AUGS[a].key, worked(a), held(a), b.times[a])
            }
        })
        .collect();
    let list = |v: &[String]| if v.is_empty() { "-".to_string() } else { v.join(", ") };
    format!("TALLY {} simulations ended since the game started, {} of {n} augments held at least once | held but never \
             worked: {} | never held yet ({}): {} | worked / held (times fired): {}",
            b.sims, n - never.len(), list(&quiet), never.len(), if never.is_empty() { "-".into() } else { never.join(" ") },
            list(&all))
}

#[cfg(test)]
pub(crate) fn reset_for_test() {
    let mut b = BOOK.lock().unwrap_or_else(|e| e.into_inner());
    b.sims = 0;
    b.held.clear();
    b.worked.clear();
    b.times.clear();
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::augments::by_key;

    #[test]
    fn the_book_puts_the_quiet_ones_first() {
        let _g = crate::tests::GLOBALS.lock().unwrap_or_else(|e| e.into_inner());
        reset_for_test();
        let n = AUGS.len();
        let chain = by_key("chain_lightning").unwrap();
        let shark = by_key("shark_bait").unwrap();
        // 第一个属性类（「属性！」那几个是属性铁砧，会触发，不算）
        let stats = AUGS.iter().position(|a| a.ev == Ev::Stat).unwrap();
        let sk = AUGS[stats].key;
        assert_eq!(add(&[(chain, Seen::Fired(5)), (shark, Seen::Fired(0)), (stats, Seen::On(true))]), 1);
        assert_eq!(add(&[(chain, Seen::Fired(2)), (shark, Seen::Fired(0))]), 2);
        let l = line();
        let parts: Vec<&str> = l.split(" | ").collect();
        assert_eq!(parts.len(), 4, "{l}");
        assert_eq!(parts[0], format!("TALLY 2 simulations ended since the game started, 3 of {n} augments held at least once"));
        assert_eq!(parts[1], "held but never worked: shark_bait 0/2");
        assert!(parts[2].starts_with(&format!("never held yet ({}): ", n - 3)), "{l}");
        let all: Vec<&str> = parts[3].trim_start_matches("worked / held (times fired): ").split(", ").collect();
        let mut want = [(chain, "chain_lightning 2/2 x7".to_string()), (shark, "shark_bait 0/2 x0".to_string()),
                            (stats, format!("{sk} 1/1"))];
        want.sort();
        assert_eq!(all, want.iter().map(|x| x.1.as_str()).collect::<Vec<_>>(), "in the augments' order");
        // 属性类的 buff 不在身上：拿着却没起作用
        add(&[(stats, Seen::On(false))]);
        let l = line();
        assert!(l.contains(&format!(", {sk} 1/2")) || l.contains(&format!(": {sk} 1/2")), "{l}");
        reset_for_test();
        assert!(line().contains(&format!("held but never worked: - | never held yet ({n})")));
    }
}
