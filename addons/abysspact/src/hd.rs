//! HD PPU frame table for Abyss Pact (渊契) champions, summon units, and effects.

use hd_engine::Table;

pub const HEROES: &[(&str, f32, &str)] = &[
    ("abysspact_oathbreaker", 2.75, include_str!("../../../abysspact/champions/abysspact_oathbreaker#anim.fanim")),
    ("abysspact_faceless",    2.75, include_str!("../../../abysspact/champions/abysspact_faceless#anim.fanim")),
    ("abysspact_whisperer",   2.75, include_str!("../../../abysspact/champions/abysspact_whisperer#anim.fanim")),
    ("abysspact_bonebow",     2.75, include_str!("../../../abysspact/champions/abysspact_bonebow#anim.fanim")),
    ("abysspact_corvus",      2.75, include_str!("../../../abysspact/champions/abysspact_corvus#anim.fanim")),
    // Real summoned skeleton unit (spawn_unit) drawn at full Q-pixel HD density
    ("abysspact_skeleton",    2.75, include_str!("../../../abysspact/champions/abysspact_skeleton#anim.fanim")),
];

pub const SIZES: &[(&str, f32)] = &[];
pub const GROWTH: &[(&str, &str, f32)] = &[];
pub const FORMS: &[(&str, &[&str], f32, f32)] = &[];

pub const EFFECTS: &[(&str, f32, &str)] = &[
    ("abysspact_oathbreaker_fx", 3.3, include_str!("../../../abysspact/effects/abysspact_oathbreaker_fx#anim.fanim")),
    ("abysspact_faceless_fx",    3.3, include_str!("../../../abysspact/effects/abysspact_faceless_fx#anim.fanim")),
    ("abysspact_whisperer_fx",   3.3, include_str!("../../../abysspact/effects/abysspact_whisperer_fx#anim.fanim")),
    ("abysspact_bonebow_fx",     3.3, include_str!("../../../abysspact/effects/abysspact_bonebow_fx#anim.fanim")),
    ("abysspact_corvus_fx",      3.3, include_str!("../../../abysspact/effects/abysspact_corvus_fx#anim.fanim")),
];

pub const DRAWN_EFFECTS: &[&str] = &[
    "abysspact_oathbreaker_fx",
    "abysspact_faceless_fx",
    "abysspact_whisperer_fx",
    "abysspact_bonebow_fx",
    "abysspact_corvus_fx",
];

// Whisperer has floating prayer beads reaching 48 game px tall: scale slightly on compact BP cards.
pub const UI_SIZES: &[(&str, f32)] = &[
    ("abysspact_whisperer", 0.86),
];

pub fn table() -> Table<'static> {
    Table {
        pack: "abysspact",
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
    fn heroes_and_skeleton_registered() {
        let h = Heroes::of(&[&table()]);
        assert_eq!(h.list.len(), HEROES.len() + EFFECTS.len());
        for &(id, ..) in HEROES {
            assert_eq!(h.get(id).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/abysspact/champions/{id}#anim")).map(|x| x.id), Some(id));
        }
        assert_eq!(h.packs, vec!["abysspact"]);
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
