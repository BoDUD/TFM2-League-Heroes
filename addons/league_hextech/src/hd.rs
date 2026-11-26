//! 身体变大（0.3.0，用户 2026-11-26：「身体变大那种特效如果有的话只能你自己做」）：歌利亚巨人、最终形态、坦克引擎的体型；
//! 0.4.0 起坦克引擎四档，加上泰坦的坚决（叠满）、狂舞怪兽（放大招后）。
//!
//! 游戏的 buff 不管画多大（`radius_mult` 只改碰撞，画面不变），所以借高清帧引擎（`hd_engine`，league.dll、tft.dll、大小龙共用
//! 那一个）的「通配变身行」：身上挂着这几个 buff 的单位，不管是谁，画大这么多（脚底不动，慢慢变大、慢慢变回去）——和英雄联盟主包
//! 璐璐大招的那一行（1.15 倍）一个做法。进程里第一个调 `hd_engine::start` 的 DLL 挂钩（主），后来的把表交给它（客）：和主包、
//! 云顶包、大小龙一起开着时谁先加载都行。表的 `pack` 是 `league`：引擎只认以 `<pack>_` 开头的 buff 名（`league_hextech_…`）。
//!
//! 一个单位身上同时有几个时用排在前面的那一行，所以按大小从大到小排；英雄自己会变大的（沃利贝尔的风暴形态……）取两者里大的那个，
//! 不乘在一起。只能变大：引擎的通配行不收小于 1 的倍数。

use hd_engine::hd::ANY;
use hd_engine::Table;

use super::augments::{buff_name, of_ev, Ev};
use super::procs::b2::{D_TITAN, E_MOSH};
use super::procs::{E_FINAL, G_TANK};

/// 最终形态。
pub const FINAL_SIZE: f32 = 1.25;
/// 歌利亚巨人（说明里写的 15%）。
pub const GOLIATH_SIZE: f32 = 1.15;
/// 坦克引擎 2、4、6、8 层（0.4.0 对齐英雄联盟：每层都变大，这里每 2 层一档）。
pub const TANK_SIZES: [f32; 4] = [1.05, 1.10, 1.14, 1.20];
/// 狂舞怪兽放大招后、泰坦的坚决叠满（0.4.0）。几行的倍数各不相同：同时有几个时用大的那个。
pub const MOSH_SIZE: f32 = 1.18;
pub const TITAN_SIZE: f32 = 1.12;

/// 变身行：(buff, 倍数, 几秒变过去)，从大到小。
pub fn rows() -> Vec<(String, f32, f32)> {
    let goliath = of_ev(Ev::Goliath).map(buff_name).unwrap_or_default();
    vec![
        (E_FINAL.to_string(), FINAL_SIZE, 0.3),
        (G_TANK[3].to_string(), TANK_SIZES[3], 0.5),
        (E_MOSH.to_string(), MOSH_SIZE, 0.3),
        (goliath, GOLIATH_SIZE, 0.6),
        (G_TANK[2].to_string(), TANK_SIZES[2], 0.5),
        (D_TITAN.to_string(), TITAN_SIZE, 0.4),
        (G_TANK[1].to_string(), TANK_SIZES[1], 0.5),
        (G_TANK[0].to_string(), TANK_SIZES[0], 0.5),
    ]
}

pub fn table() -> Table<'static> {
    let forms = rows()
        .into_iter()
        .map(|(buff, size, secs)| {
            let buff: &'static str = Box::leak(buff.into_boxed_str());
            (ANY, vec![buff], size, secs)
        })
        .collect();
    Table { pack: "league", forms, ..Table::default() }
}

#[cfg(test)]
mod tests {
    use super::*;
    use hd_engine::hd::{checks, Heroes};

    #[test]
    fn the_table_passes_the_engines_checks() {
        let t = table();
        checks::ids_are_the_packs_once(&t);
        let h = Heroes::of(&[&t]);
        let any: Vec<_> = h.any_forms().map(|f| (f.1[0], f.2)).collect();
        assert_eq!(any.len(), 8);
        // the biggest first: a unit with two of them is drawn at the first row's size
        assert!(any.windows(2).all(|w| w[0].1 > w[1].1), "{any:?}");
        assert_eq!(any[3], ("league_hextech_a:goliath", GOLIATH_SIZE));
        // no hero of its own: nothing else registered
        assert!(h.list.is_empty());
    }

    /// League's pack grows Lulu's ally by its own row; ours come in beside it, never in its place.
    #[test]
    fn the_rows_come_in_beside_the_main_packs() {
        let mut league = Table { pack: "league", ..Table::default() };
        league.forms.push((ANY, vec!["league_lulu_r_on"], 1.15, 0.5));
        let (h, _) = Heroes::of(&[&league]).and(&table());
        assert_eq!(h.any_forms().count(), 9);
        assert_eq!(h.any_forms().next().map(|f| f.1[0]), Some("league_lulu_r_on"));
    }
}
