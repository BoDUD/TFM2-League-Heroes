//! 本包哪些英雄有高清帧（PPU）：ragnarok.dll 的表，init 时交给 hd_engine。一行的意思和 league_main/src/hd.rs、
//! tft/src/hd.rs 的一样（hd_engine src/hd.rs 的 Table）。

use hd_engine::Table;

/// 英雄 id、一个游戏像素几格、图的 .fanim（ragnarok/ 里的原样）。
pub const HEROES: &[(&str, f32, &str)] = &[
    // 吕布（ragnarok_lubu）：Codex 画的 128 格原画就是高清帧，头发到脚底 66 格、翎子尖 73 格。原来 PPU 1.65（头顶 40），
    // 用户说比索尔高出不少，改成 1.94：同样的像素画成 85% 大，头顶 34、翎子 37.6 个游戏像素。1 倍帧由
    // tools/art/import_lubu.py 从高清帧缩出来，高清帧原样；他的特效图还是 1.65（下面 EFFECTS）
    ("ragnarok_lubu", 1.94, include_str!("../../../ragnarok/champions/ragnarok_lubu#anim.fanim")),
    // 索尔（ragnarok_thor）：同样是 Codex 的 128 格原画，头发到脚底 55 格、肩上雷槌顶 76 格；PPU 1.65，游戏里头顶 33、
    // 锤顶 46 个游戏像素（和缩过的吕布头顶齐平）。投锤的接锤单独一个标签 skill2_catch（锤子真飞回来才播）
    ("ragnarok_thor", 1.65, include_str!("../../../ragnarok/champions/ragnarok_thor#anim.fanim")),
];

/// 英雄在高清帧画出来的地方的大小（1.0 = 1 倍帧的大小，不列就是 1.0）。
pub const SIZES: &[(&str, f32)] = &[];

/// 身体随层数变大的英雄：本包没有。
pub const GROWTH: &[(&str, &str, f32)] = &[];

/// 身上有某个 buff 时画大一点的英雄：本包没有。
pub const FORMS: &[(&str, &[&str], f32, f32)] = &[];

/// 像英雄的图一样画高清的特效图：吕布打在人身上的火花、天喰的冲击、碎盾，原画就是高清帧（tools/art/import_lubu.py）。
pub const EFFECTS: &[(&str, f32, &str)] = &[
    ("ragnarok_lubu_fx", 1.65, include_str!("../../../ragnarok/effects/ragnarok_lubu_fx#anim.fanim")),
    // 索尔打在人身上的雷击、觉醒重砸的冲击、雷槌觉醒的红纹（飞出去的锤子是弹道画面，1 倍，不在这里）
    ("ragnarok_thor_fx", 1.65, include_str!("../../../ragnarok/effects/ragnarok_thor_fx#anim.fanim")),
];

/// 画面节点画特效时缩成 1 / PPU 的特效：上面这张只当 view_effects 播，没有 buff 和弹道的画面，走普通的门就行。
pub const DRAWN_EFFECTS: &[&str] = &["ragnarok_lubu_fx", "ragnarok_thor_fx"];

/// 界面上画 lo_ 帧的地方（选人卡片）缩小画的高个子英雄。
pub const UI_SIZES: &[(&str, f32)] = &[];

/// 本包的表，ragnarok.dll 在 init 时交给 hd_engine（src/lib.rs）。
pub fn table() -> Table<'static> {
    Table {
        pack: "ragnarok",
        heroes: HEROES.to_vec(),
        sizes: SIZES.to_vec(),
        growth: GROWTH.to_vec(),
        forms: FORMS.iter().map(|&(id, buffs, size, secs)| (id, buffs.to_vec(), size, secs)).collect(),
        effects: EFFECTS.to_vec(),
        drawn_effects: DRAWN_EFFECTS.to_vec(),
        ui_sizes: UI_SIZES.to_vec(),
        full_effects: Vec::new(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use hd_engine::hd::{checks, Heroes};

    #[test]
    fn heroes_are_found_by_id_and_resource_name() {
        let h = Heroes::of(&[&table()]);
        assert_eq!(h.list.len(), HEROES.len() + EFFECTS.len());
        for &(id, ..) in HEROES {
            assert_eq!(h.get(id).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/ragnarok/champions/{id}#anim")).map(|x| x.id), Some(id));
        }
        assert!(h.get("ragnarok_nobody").is_none());
        // 别的包的英雄在它们自己的表里
        assert!(h.get("league_yasuo").is_none());
        assert!(h.get("tft_powder").is_none());
        assert_eq!(h.packs, vec!["ragnarok"]);
    }

    #[test]
    fn every_registered_sheet_is_ppu_times_as_wide() {
        checks::every_registered_sheet_is_ppu_times_as_wide(&table());
    }

    #[test]
    fn every_registered_sheet_has_hd_tags_for_all_its_tags() {
        checks::every_registered_sheet_has_hd_tags_for_all_its_tags(&table());
    }

    #[test]
    fn ui_sizes_shrink_heroes_with_lo_frames() {
        checks::ui_sizes_shrink_heroes_with_lo_frames(&table());
    }

    #[test]
    fn effect_sheets_have_a_dense_idle() {
        checks::effect_sheets_have_a_dense_idle(&table());
    }

    #[test]
    fn every_row_is_one_of_the_packs_heroes_once() {
        checks::ids_are_the_packs_once(&table());
    }

    #[test]
    fn the_table_reaches_a_host_unchanged() {
        checks::the_table_goes_through_the_text_unchanged(&table());
    }
}
