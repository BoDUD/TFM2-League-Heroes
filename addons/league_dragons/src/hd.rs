//! 高清帧（0.3.5，用户 2026-11-10：「不行 你要改成不依赖主包的」「就是用原版英雄也能用这个大小龙」「高清帧可以拆出来啊
//! 云顶不就是么」「云顶英雄也不用依赖啊」）：本包自己带高清帧引擎（`hd_engine`，league.dll 和 tft.dll 共用的那个），把 8 张图的
//! `hd_` 帧登记成高清——和 league_main/src/hd.rs `EFFECTS` 里大小龙那 8 行一样的数（亚龙、远古 1.8，男爵 1.5）。
//!
//! 进程里第一个调 `hd_engine::start` 的 DLL 挂钩（主），后来的把表交给它（客）：只装本包（原版英雄）时本包挂钩画这 8 张；
//! 和英雄联盟主包、云顶包一起开着时谁先加载都行。主包 0.9.25 起自己也登记这 8 张，同一个名字登记两次时先登记的那一行留着
//! （两边的数一样）。表的 `pack` 是 `league`：引擎只认以 `<pack>_` 开头的名字（这 8 张是 `league_drake_*`、`league_baron`），
//! 没有英雄，也就不碰 `asset/league/ui_sheets`。
use hd_engine::Table;

/// (name, PPU, .fanim): the sheets in this mod's `effects/` (tools/art/dragons_hd.py), each tag with its hd_ twin.
pub const EFFECTS: &[(&str, f32, &str)] = &[
    ("league_drake_infernal", 1.8, include_str!("../effects/league_drake_infernal#anim.fanim")),
    ("league_drake_mountain", 1.8, include_str!("../effects/league_drake_mountain#anim.fanim")),
    ("league_drake_ocean", 1.8, include_str!("../effects/league_drake_ocean#anim.fanim")),
    ("league_drake_cloud", 1.8, include_str!("../effects/league_drake_cloud#anim.fanim")),
    ("league_drake_hextech", 1.8, include_str!("../effects/league_drake_hextech#anim.fanim")),
    ("league_drake_chemtech", 1.8, include_str!("../effects/league_drake_chemtech#anim.fanim")),
    ("league_drake_elder", 1.8, include_str!("../effects/league_drake_elder#anim.fanim")),
    ("league_baron", 1.5, include_str!("../effects/league_baron#anim.fanim")),
];

/// Baron's attack_target_effect, a picture at a point from his sheet (league_main/src/hd.rs DRAWN_EFFECTS' first row).
pub const DRAWN_EFFECTS: &[&str] = &["league_baron"];

pub fn table() -> Table<'static> {
    Table { pack: "league", effects: EFFECTS.to_vec(), drawn_effects: DRAWN_EFFECTS.to_vec(), ..Table::default() }
}

#[cfg(test)]
mod tests {
    use super::*;
    use hd_engine::hd::{checks, Heroes};

    #[test]
    fn the_eight_sheets_are_registered_dense_by_their_names() {
        let h = Heroes::of(&[&table()]);
        assert_eq!(h.list.len(), EFFECTS.len());
        for &(id, ppu, _) in EFFECTS {
            assert_eq!(h.get(id).map(|x| (x.id, x.ppu)), Some((id, ppu)));
            // the body draw finds them by the renamed display entity's resource (src/skin.rs): both paths
            for dir in ["champions", "ingame"] {
                assert_eq!(h.of_name(&format!("asset/base/aseprite_resources/{dir}/{id}#sheet")).map(|x| x.id), Some(id));
            }
        }
        // the native monsters' own names are not ours
        assert!(h.of_name("asset/base/aseprite_resources/ingame/serpen#sheet").is_none());
        assert!(h.get("league_yasuo").is_none());
    }

    #[test]
    fn the_table_passes_the_engines_checks() {
        let t = table();
        checks::ids_are_the_packs_once(&t);
        checks::every_registered_sheet_is_ppu_times_as_wide(&t);
        checks::every_registered_sheet_has_hd_tags_for_all_its_tags(&t);
        checks::effect_sheets_have_a_dense_idle(&t);
    }

    /// The same rows as league.dll's (league_main/src/hd.rs EFFECTS): either DLL may register them first.
    #[test]
    fn the_rows_match_league_dlls() {
        let main = include_str!("../../league_main/src/hd.rs");
        for &(id, ppu, _) in EFFECTS {
            let row = format!("(\"{id}\", {ppu:?}, include_str!(\"../../league_dragons/effects/{id}#anim.fanim\"))");
            assert!(main.contains(&row), "league_main/src/hd.rs has no row {row}");
        }
    }
}
