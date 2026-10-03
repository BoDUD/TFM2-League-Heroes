//! 拿游戏日志里真实的出 E 情形重新选一遍钩点：她在哪、目标在哪、照日志里的预判他往哪跑，
//! 用现在的 `plan_engage`（5v5 墙格 + 地图四边，不含塔——日志里没有塔的位置）重选，统计钩点的方向和
//! 「拉过去 → 扑」的拐角，和日志里当时的选择比。
//!
//!     cargo run --release --example replay -- <league_camille_wall.log> [只看以这个开头的行，如 "[view m=589 s=1]"]

use std::collections::BTreeMap;

use league_camille_wall::{hook_points, plan_engage, ticks_to_e2, Foe, Grid};
use mod_api_stable::GameModeKindV1;

fn num(s: &str) -> f64 {
    s.trim().parse().unwrap_or(f64::NAN)
}

/// 「(x,y)」→ 坐标。
fn point(s: &str) -> (f64, f64) {
    let inner = s.trim().trim_start_matches('(').trim_end_matches(')');
    let (x, y) = inner.split_once(',').unwrap_or(("nan", "nan"));
    (num(x), num(y))
}

/// `text` 里 `key` 后面的第一个「(x,y)」。
fn after(text: &str, key: &str) -> Option<(f64, f64)> {
    let rest = &text[text.find(key)? + key.len()..];
    let open = rest.find('(')?;
    let close = rest[open..].find(')')? + open;
    Some(point(&rest[open..=close]))
}

fn cos(a: (f64, f64), b: (f64, f64)) -> f64 {
    let n = a.0.hypot(a.1) * b.0.hypot(b.1);
    if n > 0.0 {
        (a.0 * b.0 + a.1 * b.1) / n
    } else {
        1.0
    }
}

fn deg(c: f64) -> f64 {
    c.clamp(-1.0, 1.0).acos().to_degrees()
}

fn bucket(d: f64) -> &'static str {
    match d as i64 {
        0..=60 => "0-60",
        61..=90 => "61-90",
        91..=110 => "91-110",
        111..=135 => "111-135",
        _ => "136-180",
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let text = std::fs::read_to_string(&args[1]).expect("log");
    let only = args.get(2);
    let grid = Grid::builtin(GameModeKindV1::Moba);
    let (mut n, mut planned, mut same) = (0, 0, 0);
    let mut old_turns: BTreeMap<&str, usize> = BTreeMap::new();
    let mut new_turns: BTreeMap<&str, usize> = BTreeMap::new();
    let mut lines = Vec::new();
    for line in text.lines().filter(|l| l.contains(" ENGAGE map=Moba ") && only.is_none_or(|o| l.starts_with(o.as_str()))) {
        let (Some(me), Some(old_hook), Some(at), Some(exp)) =
            (after(line, " from "), after(line, "-> "), after(line, " at "), after(line, "expected at "))
        else {
            continue;
        };
        n += 1;
        let old_dist = num(line.split("-> ").nth(1).and_then(|r| r.split(") (").nth(1)).and_then(|r| r.split(' ').next()).unwrap_or("0"));
        let t = ticks_to_e2(old_dist).max(1.0);
        let foe = Foe { id: 1, x: at.0, y: at.1, vx: (exp.0 - at.0) / t, vy: (exp.1 - at.1) / t, ..Default::default() };
        let old_turn = deg(cos((old_hook.0 - me.0, old_hook.1 - me.1), (exp.0 - old_hook.0, exp.1 - old_hook.1)));
        *old_turns.entry(bucket(old_turn)).or_default() += 1;
        let hits = hook_points(&grid, me, 10_000.0, &[]);
        match plan_engage(&grid, &hits, me, &[foe], &[]) {
            Some((h, _)) => {
                planned += 1;
                let p = league_camille_wall::lead_on(&grid, &foe, ticks_to_e2(h.dist));
                let turn = deg(cos((h.x - me.0, h.y - me.1), (p.0 - h.x, p.1 - h.y)));
                *new_turns.entry(bucket(turn)).or_default() += 1;
                if (h.x - old_hook.0).abs() < 1.0 && (h.y - old_hook.1).abs() < 1.0 {
                    same += 1;
                }
                if only.is_some() {
                    lines.push(format!(
                        "{} target {:.0} away: old hook {:.0} away turn {old_turn:.0} deg -> new hook ({:.0},{:.0}) {:.0} away {:?} turn {turn:.0} deg",
                        line.split(" camille#").next().unwrap_or(""),
                        ((at.0 - me.0).hypot(at.1 - me.1)),
                        ((old_hook.0 - me.0).hypot(old_hook.1 - me.1)),
                        h.x,
                        h.y,
                        h.dist,
                        h.surface
                    ));
                }
            }
            None => {
                if only.is_some() {
                    lines.push(format!(
                        "{} target {:.0} away: old turn {old_turn:.0} deg -> NO E now",
                        line.split(" camille#").next().unwrap_or(""),
                        ((at.0 - me.0).hypot(at.1 - me.1))
                    ));
                }
            }
        }
    }
    println!("{n} logged engages (walls + map edges only; tower hooks re-planned without towers)");
    println!("still engage: {planned} ({:.0}%), same hook as before: {same}", planned as f64 * 100.0 / n.max(1) as f64);
    println!("pull -> dive turn, before: {old_turns:?}");
    println!("pull -> dive turn, now:    {new_turns:?}");
    for l in lines {
        println!("{l}");
    }
}
