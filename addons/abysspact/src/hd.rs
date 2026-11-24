//! HD PPU frame table for Abyss Pact (渊契) champions, summon units, and effects.

use hd_engine::Table;

pub const HEROES: &[(&str, f32, &str)] = &[
    // Batch 1
    ("abysspact_oathbreaker", 2.75, include_str!("../../../abysspact/champions/abysspact_oathbreaker#anim.fanim")),
    ("abysspact_faceless",    2.75, include_str!("../../../abysspact/champions/abysspact_faceless#anim.fanim")),
    ("abysspact_whisperer",   2.75, include_str!("../../../abysspact/champions/abysspact_whisperer#anim.fanim")),
    ("abysspact_bonebow",     2.75, include_str!("../../../abysspact/champions/abysspact_bonebow#anim.fanim")),
    ("abysspact_corvus",      2.75, include_str!("../../../abysspact/champions/abysspact_corvus#anim.fanim")),
    // Real summoned skeleton unit (spawn_unit) drawn at full Q-pixel HD density
    ("abysspact_skeleton",    2.75, include_str!("../../../abysspact/champions/abysspact_skeleton#anim.fanim")),
    // Batch 2
    ("abysspact_bloodmoon",   2.75, include_str!("../../../abysspact/champions/abysspact_bloodmoon#anim.fanim")),
    ("abysspact_undertaker",  2.75, include_str!("../../../abysspact/champions/abysspact_undertaker#anim.fanim")),
    ("abysspact_effigy",      2.75, include_str!("../../../abysspact/champions/abysspact_effigy#anim.fanim")),
    ("abysspact_sevenfold",   2.75, include_str!("../../../abysspact/champions/abysspact_sevenfold#anim.fanim")),
    ("abysspact_vesper",      2.75, include_str!("../../../abysspact/champions/abysspact_vesper#anim.fanim")),
    // Batch 3
    ("abysspact_carapace",    2.75, include_str!("../../../abysspact/champions/abysspact_carapace#anim.fanim")),
    ("abysspact_leech",       2.75, include_str!("../../../abysspact/champions/abysspact_leech#anim.fanim")),
    ("abysspact_noctua",      2.75, include_str!("../../../abysspact/champions/abysspact_noctua#anim.fanim")),
    ("abysspact_anchor",      2.75, include_str!("../../../abysspact/champions/abysspact_anchor#anim.fanim")),
    ("abysspact_hourglass",   2.75, include_str!("../../../abysspact/champions/abysspact_hourglass#anim.fanim")),
];

pub const SIZES: &[(&str, f32)] = &[];
pub const GROWTH: &[(&str, &str, f32)] = &[];
pub const FORMS: &[(&str, &[&str], f32, f32)] = &[
    // Bloodmoon R「血月降临」: smooth scale-up to 1.3x Giant Wolf for 8 seconds
    ("abysspact_bloodmoon", &["abysspact_bloodmoon_giant"], 1.3, 0.35),
];

pub const EFFECTS: &[(&str, f32, &str)] = &[
    // Batch 1
    ("abysspact_oathbreaker_fx", 3.3, include_str!("../../../abysspact/effects/abysspact_oathbreaker_fx#anim.fanim")),
    ("abysspact_faceless_fx",    3.3, include_str!("../../../abysspact/effects/abysspact_faceless_fx#anim.fanim")),
    ("abysspact_whisperer_fx",   3.3, include_str!("../../../abysspact/effects/abysspact_whisperer_fx#anim.fanim")),
    ("abysspact_bonebow_fx",     3.3, include_str!("../../../abysspact/effects/abysspact_bonebow_fx#anim.fanim")),
    ("abysspact_corvus_fx",      3.3, include_str!("../../../abysspact/effects/abysspact_corvus_fx#anim.fanim")),
    // Batch 2
    ("abysspact_bloodmoon_fx",   3.3, include_str!("../../../abysspact/effects/abysspact_bloodmoon_fx#anim.fanim")),
    ("abysspact_undertaker_fx",  3.3, include_str!("../../../abysspact/effects/abysspact_undertaker_fx#anim.fanim")),
    ("abysspact_effigy_fx",      3.3, include_str!("../../../abysspact/effects/abysspact_effigy_fx#anim.fanim")),
    ("abysspact_sevenfold_fx",   3.3, include_str!("../../../abysspact/effects/abysspact_sevenfold_fx#anim.fanim")),
    ("abysspact_vesper_fx",      3.3, include_str!("../../../abysspact/effects/abysspact_vesper_fx#anim.fanim")),
    // Batch 3
    ("abysspact_carapace_fx",    3.3, include_str!("../../../abysspact/effects/abysspact_carapace_fx#anim.fanim")),
    ("abysspact_leech_fx",       3.3, include_str!("../../../abysspact/effects/abysspact_leech_fx#anim.fanim")),
    ("abysspact_noctua_fx",      3.3, include_str!("../../../abysspact/effects/abysspact_noctua_fx#anim.fanim")),
    ("abysspact_anchor_fx",      3.3, include_str!("../../../abysspact/effects/abysspact_anchor_fx#anim.fanim")),
    ("abysspact_hourglass_fx",   3.3, include_str!("../../../abysspact/effects/abysspact_hourglass_fx#anim.fanim")),
];

pub const DRAWN_EFFECTS: &[&str] = &[
    "abysspact_oathbreaker_fx",
    "abysspact_faceless_fx",
    "abysspact_whisperer_fx",
    "abysspact_bonebow_fx",
    "abysspact_corvus_fx",
    "abysspact_bloodmoon_fx",
    "abysspact_undertaker_fx",
    "abysspact_effigy_fx",
    "abysspact_sevenfold_fx",
    "abysspact_vesper_fx",
    "abysspact_carapace_fx",
    "abysspact_leech_fx",
    "abysspact_noctua_fx",
    "abysspact_anchor_fx",
    "abysspact_hourglass_fx",
];

// Tall silhouettes (47-48px) scaled gently on compact BP cards.
pub const UI_SIZES: &[(&str, f32)] = &[
    ("abysspact_whisperer", 0.86),
    ("abysspact_undertaker", 0.88),
    ("abysspact_vesper", 0.86),
    ("abysspact_anchor", 0.88),
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
