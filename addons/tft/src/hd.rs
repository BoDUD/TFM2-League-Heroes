//! Which of the tft pack's heroes have dense (PPU) frames: tft.dll's table. Its rows were league.dll's
//! (league_main/src/hd.rs) until 2026-10-31, drawn only with both packs enabled; now tft.dll hands them to
//! hd_engine at init (src/lib.rs) - hooking the game itself when it is the first pack DLL loaded (the tft pack on its
//! own, or before league in the Mods menu), else handing the table to the one that did (league.dll,
//! hd_engine src/share.rs). A row means what league_main/src/hd.rs's do (hd_engine src/hd.rs Table).

use hd_engine::Table;

/// Champion id, pixels per 1x square, the sheet's .fanim (as shipped in tft/).
pub const HEROES: &[(&str, f32, &str)] = &[
    // Powder (tft_powder, the tft pack in tft/: Teamfight Tactics' own units, its own mod; league.dll drew her dense
    // frames with both packs enabled, tft.dll since 2026-10-31): the idle design and Codex's skeleton poses with one
    // clean head, posed by tools/art/rig_powder.py at 1.75 squares a game pixel (61 rows: 「35」, then
    // 「PPU像素好低啊 能调一下吗」), shown at 90 % (SIZES)
    ("tft_powder", 1.75, include_str!("../../../tft/champions/tft_powder#anim.fanim")),
    // Norra (tft_norra, the tft pack's second hero): the design (Codex's step-0 A-1 at 72 rows, 36 game px hat top to
    // soles: 「A-1 36px PPU2.0」, the gold ring in her near hand) and Codex's key poses after the videos with the design's
    // head, posed by tools/art/rig_norra.py at 2.0 squares a game pixel, so no SIZES row
    ("tft_norra", 2.0, include_str!("../../../tft/champions/tft_norra#anim.fanim")),
    // Alune (tft_alune, the tft pack): riding her crescent glaive, step 0's A-1 at the user's 46 game px horns to the
    // crescent's foot, PPU 2.0 (「A-1 46 PPU 2.0」), and Codex's key poses after her own TFT clips with the design's head,
    // posed by tools/art/rig_alune.py, so no SIZES row
    ("tft_alune", 2.0, include_str!("../../../tft/champions/tft_alune#anim.fanim")),
    // Silco (tft_silco, the tft pack): leaning on his cane, step 0's A-1 at the user's 40 game px hair to soles, PPU 2.0
    // (「A-1 40 PPU 2.0」), and Codex's key poses after his own TFT clips with the design's head, posed by
    // tools/art/rig_silco.py, so no SIZES row
    ("tft_silco", 2.0, include_str!("../../../tft/champions/tft_silco#anim.fanim")),
    // Maddie (tft_maddie, the tft pack): the rifle on her shoulder, step 0's A-1 at the user's 38 game px beret to soles,
    // PPU 1.5 (「A-1 38 PPU 1.5」), and Codex's key poses after her own TFT clips with the design's head, posed by
    // tools/art/rig_maddie.py, so no SIZES row
    ("tft_maddie", 1.5, include_str!("../../../tft/champions/tft_maddie#anim.fanim")),
    // Loris (tft_loris, the tft pack): the tower shield upright at his side, step 0's B-1 at the user's 42 game px hair
    // to soles, PPU 2.0 (「B-1 42 PPU 2.0」), and Codex's key poses after his own TFT clips with the design's head, posed
    // by tools/art/rig_loris.py, so no SIZES row
    ("tft_loris", 2.0, include_str!("../../../tft/champions/tft_loris#anim.fanim")),
    // Kobuko (tft_kobuko, the tft pack): stroking his beard, step 0's A-1 at the user's 40 game px topknot to soles,
    // PPU 2.0 (「A-1 40 PPU 2.0」), and Codex's key poses after his own TFT clips with the design's head, posed by
    // tools/art/rig_kobuko.py, so no SIZES row
    ("tft_kobuko", 2.0, include_str!("../../../tft/champions/tft_kobuko#anim.fanim")),
    // Vander (tft_vander, the tft pack): the low fighting stance, step 0's B-2 at the user's 40 game px hair to soles,
    // PPU 2.0 (「B-2 40 PPU 2.0」), and Codex's key poses after his own TFT clips with the design's head, posed by
    // tools/art/rig_vander.py, so no SIZES row
    ("tft_vander", 2.0, include_str!("../../../tft/champions/tft_vander#anim.fanim")),
    // Violet (tft_violet, the tft pack): the fighting stance, both gauntlets up, step 0's B-1 at the user's 38 game px
    // hair to soles, PPU 2.0 (「B-1 38 PPU 2.0」), and Codex's key poses after her own TFT clips with the design's head,
    // posed by tools/art/rig_violet.py, so no SIZES row
    ("tft_violet", 2.0, include_str!("../../../tft/champions/tft_violet#anim.fanim")),
    // The Ancient Krug (tft_krug, the tft pack): hunched on all fours, step 0's A-1 at the user's 38 game px boulder to
    // soles, PPU 2.0 (「A-1 38 PPU 2.0」), and Codex's key poses after his own TFT clips, posed by tools/art/rig_krug.py,
    // so no SIZES row
    ("tft_krug", 2.0, include_str!("../../../tft/champions/tft_krug#anim.fanim")),
    // Ao Shin (tft_aoshin, the tft pack): the storm dragon hovering upright, step 0's A-1 at the user's 38 game px horns
    // to the tail's lowest curl, PPU 2.0 (「A-1 38 PPU 2.0」), and Codex's key poses after his own TFT clips, posed by
    // tools/art/rig_aoshin.py, so no SIZES row
    ("tft_aoshin", 2.0, include_str!("../../../tft/champions/tft_aoshin#anim.fanim")),
    // Scar (tft_scar, the tft pack): the spear guard, the point forward, step 0's B-1 at the user's 38 game px mohawk to
    // soles, PPU 2.0 (「B-1、38 游戏像素、PPU 2.0」), and Codex's key poses after his own TFT clips with the design's head,
    // posed by tools/art/rig_scar.py, so no SIZES row
    ("tft_scar", 2.0, include_str!("../../../tft/champions/tft_scar#anim.fanim")),
    // Renni (tft_renni, the tft pack): the stance, the chainsaw level forward, step 0's B-1 at the user's 38 game px hair
    // to soles, PPU 2.0 (「B-1、38 像素、PPU 2.0」), and Codex's key poses after her own TFT clips with the design's head,
    // posed by tools/art/rig_renni.py, so no SIZES row
    ("tft_renni", 2.0, include_str!("../../../tft/champions/tft_renni#anim.fanim")),
    // Smeech (tft_smeech, the tft pack): the ambush crouch, claws spread, step 0's B-1 at the user's 36 game px hat to
    // claw tips, PPU 2.4 (「B-1 36像素 PPU2.4」, the picture one square a pixel), and Codex's key poses after his own TFT
    // clips with the design's head, posed by tools/art/rig_smeech.py, so no SIZES row
    ("tft_smeech", 2.4, include_str!("../../../tft/champions/tft_smeech#anim.fanim")),
    // Sevika (tft_sevika, the tft pack): the standing guard, the mechanical arm hanging, step 0's A-1 at the user's 38
    // game px hair to soles, PPU 1.8 (「A-1、38、PPU 1.8」: 70 rows kept 1:1), and Codex's key poses after her own TFT
    // clips with the design's head, posed by tools/art/rig_sevika.py, so no SIZES row
    ("tft_sevika", 1.8, include_str!("../../../tft/champions/tft_sevika#anim.fanim")),
    // Steb (tft_steb, the tft pack): the idle, a baton on his shoulder, step 0's A-1 at the user's 40 game px quiff to
    // soles, PPU 2.6 (「A-1 40 PPU 2.6」: 106 rows kept 1:1), and Codex's key poses after his own TFT clips with the
    // design's head, posed by tools/art/rig_steb.py, so no SIZES row
    ("tft_steb", 2.6, include_str!("../../../tft/champions/tft_steb#anim.fanim")),
    // Nomsy (tft_nomsy, the tft pack): the chubby dragon sitting on all fours, step 0's A-1 at the user's 36 game px from
    // the far wing to her feet, PPU 2.6 (「A-1 36 PPU 2.6」: 94 rows kept 1:1), and Codex's key poses after her own TFT
    // clips on the design's palette, posed by tools/art/rig_nomsy.py, so no SIZES row
    ("tft_nomsy", 2.6, include_str!("../../../tft/champions/tft_nomsy#anim.fanim")),
    // Idas (tft_idas, the tft pack): the golden dragon side-on on her two digitigrade legs, step 0's B-1 at the user's
    // 40 game px from her crest to her feet, PPU 2.45 (「B-1 40 PPU 2.45」: 98 rows kept 1:1), and Codex's key poses after
    // her own TFT clips on the design's colours, posed by tools/art/rig_idas.py, so no SIZES row
    ("tft_idas", 2.45, include_str!("../../../tft/champions/tft_idas#anim.fanim")),
    // Daeja (tft_daeja, the tft pack): the crystal dragon-man standing upright, step 0's A-1 at the user's 40 game px from
    // the wing tips to his feet, PPU 1.72 (「A-1、40 游戏像素、PPU 1.72」: 69 rows kept 1:1), and Codex's key poses after his
    // own TFT clips with the design's face, posed by tools/art/rig_daeja.py, so no SIZES row
    ("tft_daeja", 1.72, include_str!("../../../tft/champions/tft_daeja#anim.fanim")),
    // Shi Oh Yu (tft_shiohyu, the tft pack): the jade dragon-man turned near side-on, step 0's B-1 at the user's 42 game px
    // from the wing tips to his feet, PPU 2.46 (「B1 42 PPU 2.46」: 103 rows), and Codex's key poses and run after his own
    // TFT clips with the design's face, posed by tools/art/rig_shiohyu.py, so no SIZES row
    ("tft_shiohyu", 2.46, include_str!("../../../tft/champions/tft_shiohyu#anim.fanim")),
    // Sy'fen (tft_syfen, the tft pack): the shadow wyvern side-on and hunched, step 0's B-1 at the user's 40 game px from
    // the horn tips to his feet, PPU 2.52 (「B-1、40 像素高、PPU 2.52」: 111 rows brought down to 101), and Codex's key poses
    // after his own TFT clips, posed by tools/art/rig_syfen.py, so no SIZES row
    ("tft_syfen", 2.52, include_str!("../../../tft/champions/tft_syfen#anim.fanim")),
    // Sohm (tft_sohm, the tft pack): the sea dragon side-on floating in her coil, step 0's B-1 at the user's 40 game px
    // from the antler tips to the bottom of her coil, PPU 1.8 (「B-1 40px PPU 1.8」: 72 rows 1:1), and Codex's key poses
    // after her own TFT clips, posed by tools/art/rig_sohm.py, so no SIZES row
    ("tft_sohm", 1.8, include_str!("../../../tft/champions/tft_sohm#anim.fanim")),
    // Terra (tft_terra, the tft pack): the earth dragon crouched at 3/4, step 0's A-1 at the user's 36 game px from the
    // wing-bone tips to her soles, PPU 1.45 (「A-1、36 px、PPU 1.45」: 52 rows 1:1), and Codex's key poses after her own
    // TFT clips, posed by tools/art/rig_terra.py, so no SIZES row
    ("tft_terra", 1.45, include_str!("../../../tft/champions/tft_terra#anim.fanim")),
    // Zippy (tft_zippy, the tft pack): the little raptor upright at 3/4, step 0's A-1 at the user's 38 game px from the
    // head spikes to its soles, PPU 2.2 (「A-1、38 px、PPU 2.2」: 83 rows 1:1), and Codex's key poses after its own TFT
    // clips, posed by tools/art/rig_zippy.py, so no SIZES row
    ("tft_zippy", 2.2, include_str!("../../../tft/champions/tft_zippy#anim.fanim")),
    // the Blue Sentinel (tft_sentinel, the tft pack): the stone golem hunched at 3/4, step 0's A-1 at the user's 40 game
    // px from the shoulder boulders to its soles, PPU 1.7 (「A-1 40像素 PPU1.7」: 68 rows 1:1), and Codex's key poses after
    // its own TFT clips, posed by tools/art/rig_sentinel.py, so no SIZES row
    ("tft_sentinel", 1.7, include_str!("../../../tft/champions/tft_sentinel#anim.fanim")),
];

/// Champion id, its size everywhere the dense frames are drawn (1.0 = the 1x frames' size): the rects and the
/// texture's reported size divided by PPU / size, the battlefield scale the game's / PPU x size, the frames drawn
/// lower so the soles stay (league_main/src/hd.rs SIZES).
/// Powder (tft_powder): 90 % (the user, 2026-10-19: 「人物模型太大 缩小一点」), her frames 2 squares lower (RESTYLE powder lift).
pub const SIZES: &[(&str, f32)] = &[("tft_powder", 0.90)];

/// Heroes whose body grows with a stack (league_main/src/hd.rs GROWTH: Cho'Gath's Feast): none in this pack yet.
pub const GROWTH: &[(&str, &str, f32)] = &[];

/// Effect sheets drawn dense like a hero's sheet (league_main/src/hd.rs EFFECTS): none in this pack yet.
pub const EFFECTS: &[(&str, f32, &str)] = &[];

/// Effects whose pictures the view node draw shrinks to 1 / PPU (league_main/src/hd.rs DRAWN_EFFECTS): none yet.
pub const DRAWN_EFFECTS: &[&str] = &[];

/// Tall heroes drawn smaller wherever the UI draws lo_ frames (the ban/pick card above all): size = 39 / the idle's
/// height, set with tools/art/bp_card_audit.py (league_main/src/hd.rs UI_SIZES has the rule).
pub const UI_SIZES: &[(&str, f32)] = &[
    // Alune (tft_alune): 46 game px from her horns to the crescent's foot at PPU 2.0 (the card's canvas is 40 tall); UI size
    // and card value set with bp_card_audit.py's math (85 %: the horns a pixel under the canvas top, the foot on its bottom)
    ("tft_alune", 0.85),
];

/// This pack's table, as tft.dll hands it to hd_engine at init (src/lib.rs).
pub fn table() -> Table<'static> {
    Table {
        pack: "tft",
        heroes: HEROES.to_vec(),
        sizes: SIZES.to_vec(),
        growth: GROWTH.to_vec(),
        effects: EFFECTS.to_vec(),
        drawn_effects: DRAWN_EFFECTS.to_vec(),
        ui_sizes: UI_SIZES.to_vec(),
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
            assert_eq!(h.of_name(&format!("asset/tft/champions/{id}#anim")).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/base/aseprite_resources/champions/{id}#sheet")).map(|x| x.id), Some(id));
        }
        assert_eq!(h.get("tft_powder").map(|x| (x.id, x.size)), Some(("tft_powder", 0.90)));
        assert!(h.get("tft_nobody").is_none());
        // league.dll's heroes are its own table's (league_main/src/hd.rs)
        assert!(h.get("league_yasuo").is_none());
        assert_eq!(h.packs, vec!["tft"]);
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
