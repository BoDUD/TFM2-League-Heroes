//! Which heroes have dense (PPU) frames - the parts that need no game.
//!
//! A hero listed in `HEROES` carries `hd_<tag>` beside every `<tag>` in its own sheet (tools/art/ppu_hd.py, the same
//! PPU there), each frame PPU times the 1x frame's size - a drawn one may be grown alike at both ends (its centre, the
//! pivot, kept), hd_idle exactly PPU times as wide (src/lookup.rs tells a changed table by it). src/lookup.rs hands every
//! reader of the hero's animations a table whose every tag holds the dense frames with their rects divided by PPU, and
//! every reader of its sheet a texture that reports its size divided by PPU: the same UVs (the dense squares), the 1x
//! sizes. The tags are read from the sheet's .fanim compiled in.

/// Champion id, pixels per 1x square, the sheet's .fanim (as shipped in league/).
pub const HEROES: &[(&str, f32, &str)] = &[
    ("league_yasuo", 2.2, include_str!("../../../league/champions/league_yasuo#anim.fanim")),
    ("league_gragas", 1.45, include_str!("../../../league/champions/league_gragas#anim.fanim")),
    ("league_zeri", 3.0, include_str!("../../../league/champions/league_zeri#anim.fanim")),
    ("league_vladimir", 1.8, include_str!("../../../league/champions/league_vladimir#anim.fanim")),
    ("league_karma", 2.2, include_str!("../../../league/champions/league_karma#anim.fanim")),
    ("league_ashe", 2.2, include_str!("../../../league/champions/league_ashe#anim.fanim")),
    ("league_irelia", 2.0, include_str!("../../../league/champions/league_irelia#anim.fanim")),
    ("league_kassadin", 2.42, include_str!("../../../league/champions/league_kassadin#anim.fanim")),
    ("league_corki", 2.2, include_str!("../../../league/champions/league_corki#anim.fanim")),
    ("league_garen", 1.9, include_str!("../../../league/champions/league_garen#anim.fanim")),
    ("league_braum", 1.98, include_str!("../../../league/champions/league_braum#anim.fanim")),
    ("league_mordekaiser", 2.0, include_str!("../../../league/champions/league_mordekaiser#anim.fanim")),
    ("league_soraka", 2.2, include_str!("../../../league/champions/league_soraka#anim.fanim")),
    ("league_nidalee", 2.2, include_str!("../../../league/champions/league_nidalee#anim.fanim")),
    ("league_galio", 1.65, include_str!("../../../league/champions/league_galio#anim.fanim")),
    ("league_nilah", 1.98, include_str!("../../../league/champions/league_nilah#anim.fanim")),
    ("league_kindred", 2.2, include_str!("../../../league/champions/league_kindred#anim.fanim")),
    ("league_malzahar", 1.38, include_str!("../../../league/champions/league_malzahar#anim.fanim")),
];

/// Champion id, its size everywhere the dense frames are drawn (1.0 = the 1x frames' size): the anim tables' rects and
/// the texture's reported size are divided by PPU / size (src/lookup.rs: the cards, the encyclopedia, the face icons,
/// the BP slots draw him that much smaller, the UVs unchanged) and the battlefield scale is the game's / PPU x size
/// (src/view.rs), each about the frame's centre / the unit's position - so the hero's dense frames are drawn lower by
/// (1 / size - 1) x the pivot-to-soles distance and the soles stay where they were (tools/art/ppu_gragas.py SHIFT).
/// Gragas: the user, 2026-10-12: 「酒桶模型缩小一点 太大了」 (85%), then 「要改全改啊」, then 80% (「怎么看起来还是比诺手高这么多」) (the cards and the encyclopedia too);
/// 2026-10-13 after the restyle 「酒桶可以稍微放大点吧 现在也太小了」 -> 90% from a size sheet, then 「还是太小啊」 -> 100% - judged on a preview GIF that
/// drew him at 80% - then 「感觉又太大了？」 from a true-scale sheet -> 90% (40 game px, Darius 42); his frames
/// lifted by the restyle (RESTYLE gragas lift_sq).
/// Zeri: 「等等泽丽感觉游戏里有点小」, picked 105% from the size sheet (drawn RAISE rows higher: tools/art/ppu_zeri.py).
/// Kassadin: 「在游戏太小了吧」, picked 115%, then 「感觉太大了点？调到110%差不多吧」 (41 game px); after the restyle
/// 「刀妹和卡萨丁感觉在游戏里偏大啊」 -> 100% (39 game px; RESTYLE kassadin lift_sq -3 undoes the rig's 110% raise) and Irelia
/// 115% -> 105% (44 game px with her blades); his hd frames drawn RAISE
/// rows higher (tools/art/rig_kassadin.py).
/// Braum: 「布隆做的也有点大 得缩小一点」 (85%), then 「稍微调大点」 (90%, 39 game px); after the restyle (a tenth
/// shorter) 「布隆也有这个看起来小的问题」 next to Alistar -> 105% (the user took the suggestion: 「按照你的建议选吧」).
/// His hd frames come SHIFT rows lower from tools/art/rig_braum.py (its 90%) and the restyle lifts them back
/// (tools/art/ppu_restyle.py RESTYLE braum lift).
/// Mordekaiser: the user picked 110% with a thicker outline (C, Kassadin's way), then 「铁男感觉做的太大了吧？」 -> 95%,
/// then 「铁男再稍微调大点」 -> 100%; then 「为什么模型看起来小啊 牛头那种就看起来很大」「铁男再游戏里还是过于高清」 ->
/// 115% at PPU 2.0 (1.74 squares a game pixel), his frames lifted by the restyle (RESTYLE mordekaiser lift).
/// Then 「铁男和布隆游戏里偏大了」: Mordekaiser 100 % (47 game px, Nautilus 51), Braum 95 % (39 px, 55 wide with his
/// shield), picked from a true-scale sheet; their frames moved down by the restyle (RESTYLE lift_sq).
/// Then on game 0.6.4 (2026-10-14) 「铁男模型太小」「铁男到110%吧」: Mordekaiser 110 % (52 game px).
/// Soraka: 「稍微变大点」 -> 110% (her frames lifted 3 squares: tools/art/ppu_restyle.py RESTYLE soraka).
/// Nilah: 「模型别太大 参考泽丽之前改过一版」 -> 90% from a size sheet (about 38 game rows with the blade's tip); her frames
/// lowered 3 squares by the restyle (RESTYLE nilah lift_sq).
/// Galio: PPU 2.0 at 85 % first (「这做的也太大了吧 缩小点模型」), then 「加里奥在局内看起来太小了」「而且在局内还是太高清了」 ->
/// 100 % at PPU 1.5 (tools/art/rig_galio.py dense), picked from true-scale sheets; then 「在局内还是偏小啊」 (38 game px
/// crown to soles, Darius 42) -> 110 % at PPU 1.65 (still 1.5 squares a game pixel), his dense frames drawn RAISE rows higher (rig_galio.py
/// SIZE / RAISE).
/// Corki: grown 1.2x by the restyle (「飞机像泽丽那样变大点」), then 「飞机在游戏里是不是偏大了？」 - 48 x 37 game px, as wide as
/// Garen and a solid lump - shown at 80 % (「到80%吧」, from a true-scale sheet), then 「太小了库奇 调到90%吧」 -> 90 %;
/// he flies, so his frames are not lowered.
/// Malzahar: 115 % from the size sheet (all actions from the 3/4 front), drawn at PPU 2.2 first, then 「像素有点高 降低点需要」 ->
/// PPU 1.38 (1.2 squares a game pixel at 115 %); he floats, his frames lifted by the restyle (RESTYLE malzahar lift).
pub const SIZES: &[(&str, f32)] = &[("league_gragas", 0.90), ("league_zeri", 1.05), ("league_kassadin", 1.00),
                                    ("league_braum", 0.95), ("league_mordekaiser", 1.10),
                                    ("league_irelia", 1.05), ("league_soraka", 1.10), ("league_galio", 1.10), ("league_nilah", 0.90),
                                    ("league_corki", 0.90), ("league_malzahar", 1.15)];

pub const PREFIX: &str = "hd_";

/// `lo_<tag>`: the same frames at [`UI_PPU`] squares a displayed game pixel (tools/art/ppu_hd.py add_lo) - what the BP
/// grid, the encyclopedia, the pick slots and the pick moment draw (src/lookup.rs ui_table; the user, 2026-10-13:
/// 「BP界面里看英雄还是太清晰」, picked the 1.5 row of the preview). The battlefield keeps the hd_ frames.
pub const LO_PREFIX: &str = "lo_";
pub const UI_PPU: f32 = 1.5;

/// The `"lo_..."` animation names of a .fanim.
pub fn lo_tags(fanim: &str) -> Vec<String> {
    keys_with(fanim, LO_PREFIX)
}

/// The `"hd_..."` animation names of a .fanim (its keys under "anims"; no frame key starts with hd_).
pub fn hd_tags(fanim: &str) -> Vec<String> {
    keys_with(fanim, PREFIX)
}

fn keys_with(fanim: &str, prefix: &str) -> Vec<String> {
    let mut out = Vec::new();
    let b = fanim.as_bytes();
    let mut i = 0;
    while let Some(off) = fanim[i..].find('"') {
        let start = i + off + 1;
        let Some(len) = fanim[start..].find('"') else { break };
        let end = start + len;
        let name = &fanim[start..end];
        let mut j = end + 1;
        while j < b.len() && b[j].is_ascii_whitespace() {
            j += 1;
        }
        if j < b.len() && b[j] == b':' && name.starts_with(prefix) && !out.iter().any(|t| t == name) {
            out.push(name.to_string());
        }
        i = end + 1;
    }
    out
}

/// A registered hero: its PPU and the plain tags that have an hd copy.
pub struct Hero {
    pub id: &'static str,
    pub ppu: f32,
    /// the size it is shown at (SIZES; 1.0 when not listed)
    pub size: f32,
    pub tags: Vec<String>,
    /// the sheet has lo_ frames for every tag (the UI draws those)
    pub lo: bool,
}

impl Hero {
    /// What a dense frame's pixels are divided by to give its shown size: PPU / size.
    pub fn shown(&self) -> f32 {
        self.ppu / self.size
    }
}

pub fn heroes() -> Vec<Hero> {
    HEROES
        .iter()
        .map(|&(id, ppu, fanim)| Hero {
            id,
            ppu,
            size: SIZES.iter().find(|s| s.0 == id).map_or(1.0, |s| s.1),
            tags: hd_tags(fanim).into_iter().map(|t| t[PREFIX.len()..].to_string()).collect(),
            lo: !lo_tags(fanim).is_empty(),
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_registered_sheet_has_hd_tags_for_all_its_tags() {
        for &(id, ppu, fanim) in HEROES {
            let hd = hd_tags(fanim);
            assert!(!hd.is_empty(), "{id}: no hd_ tags in its sheet (python tools/art/ppu_hd.py)");
            assert!(ppu > 1.0);
            // the plain tags: every top-level anim name that is not hd_
            let anims = &fanim[fanim.find("\"anims\"").unwrap()..];
            for t in ["idle", "run", "attack", "hit", "dead"] {
                assert!(anims.contains(&format!("\"{t}\"")), "{id}: no {t}");
                assert!(hd.contains(&format!("{PREFIX}{t}")), "{id}: no {PREFIX}{t}");
            }
            // lo_ frames: none, or one for every hd_ tag (the UI table maps every tag to its lo_ frames)
            let lo = lo_tags(fanim);
            if !lo.is_empty() {
                for h in &hd {
                    let want = format!("{LO_PREFIX}{}", &h[PREFIX.len()..]);
                    assert!(lo.contains(&want), "{id}: no {want} (python tools/art/ppu_hd.py --hero ...)");
                }
            }
        }
    }

    #[test]
    fn tags_are_read_from_a_fanim() {
        let f = r#"{"anims":{"idle":{"frames":[{"duration":0.1,"data":{"x":0.0}}]},"hd_idle":{"frames":[]},"hd_run" : {}}}"#;
        assert_eq!(hd_tags(f), vec!["hd_idle".to_string(), "hd_run".to_string()]);
    }
}
