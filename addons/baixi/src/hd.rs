//! 百戏包的高清帧表（PPU）：init 时交给与 league.dll / ragnarok.dll 共用的 hd_engine。

use hd_engine::Table;

pub const HEROES: &[(&str, f32, &str)] = &[
    ("baixi_dianjing", 2.75, include_str!("../../../baixi/champions/baixi_dianjing#anim.fanim")),
    ("baixi_sangeng", 2.75, include_str!("../../../baixi/champions/baixi_sangeng#anim.fanim")),
    ("baixi_maiya", 2.75, include_str!("../../../baixi/champions/baixi_maiya#anim.fanim")),
    ("baixi_huoshu", 2.75, include_str!("../../../baixi/champions/baixi_huoshu#anim.fanim")),
    ("baixi_fumian", 2.75, include_str!("../../../baixi/champions/baixi_fumian#anim.fanim")),
];

pub const SIZES: &[(&str, f32)] = &[];
pub const GROWTH: &[(&str, &str, f32)] = &[];
pub const FORMS: &[(&str, &[&str], f32, f32)] = &[];

pub const EFFECTS: &[(&str, f32, &str)] = &[
    ("baixi_dianjing_fx", 3.3, include_str!("../../../baixi/effects/baixi_dianjing_fx#anim.fanim")),
    ("baixi_sangeng_fx", 3.3, include_str!("../../../baixi/effects/baixi_sangeng_fx#anim.fanim")),
    ("baixi_maiya_fx", 3.3, include_str!("../../../baixi/effects/baixi_maiya_fx#anim.fanim")),
    ("baixi_huoshu_fx", 3.3, include_str!("../../../baixi/effects/baixi_huoshu_fx#anim.fanim")),
    ("baixi_fumian_fx", 3.3, include_str!("../../../baixi/effects/baixi_fumian_fx#anim.fanim")),
];

pub const DRAWN_EFFECTS: &[&str] = &[
    "baixi_dianjing_fx",
    "baixi_sangeng_fx",
    "baixi_maiya_fx",
    "baixi_huoshu_fx",
    "baixi_fumian_fx",
];

/// 高头盔/凤冠/狮头在 BP 选人卡上适当缩小，避免挡腿或出框。
pub const UI_SIZES: &[(&str, f32)] = &[
    ("baixi_fumian", 0.86),
    ("baixi_sangeng", 0.88),
    ("baixi_dianjing", 0.90),
];

pub fn table() -> Table<'static> {
    Table {
        pack: "baixi",
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
    fn all_five_baixi_heroes_registered() {
        let h = Heroes::of(&[&table()]);
        assert_eq!(h.list.len(), HEROES.len() + EFFECTS.len());
        for &(id, ..) in HEROES {
            assert_eq!(h.get(id).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/baixi/champions/{id}#anim")).map(|x| x.id), Some(id));
        }
        assert_eq!(h.packs, vec!["baixi"]);
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
