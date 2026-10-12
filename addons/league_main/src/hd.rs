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
    ("league_yasuo", 3.0, include_str!("../../../league/champions/league_yasuo#anim.fanim")),
    ("league_gragas", 2.0, include_str!("../../../league/champions/league_gragas#anim.fanim")),
    ("league_zeri", 3.0, include_str!("../../../league/champions/league_zeri#anim.fanim")),
    ("league_vladimir", 2.0, include_str!("../../../league/champions/league_vladimir#anim.fanim")),
    ("league_karma", 3.0, include_str!("../../../league/champions/league_karma#anim.fanim")),
    ("league_ashe", 5.4571, include_str!("../../../league/champions/league_ashe#anim.fanim")),
    ("league_irelia", 2.0, include_str!("../../../league/champions/league_irelia#anim.fanim")),
];

/// Effect sheets with dense frames (their own `hd_<tag>` beside every tag, tools/art/ppu_<hero>_fx.py): the sheet's name
/// (`.../effects/<name>#anim`), its PPU, its .fanim. src/lookup.rs changes their anim tables and textures as a hero's
/// (every reader that draws by the frame's size draws the dense frames at the 1x size); src/view.rs does NOT scale them
/// (0.6.0: it logs the display entities that carry an effect's name, to see how the battlefield draws them).
/// Garen's: the user, 2026-10-12, branch ppu-rebuild: 「导入特效吧」 (the effects redone from the original pictures).
pub const EFFECTS: &[(&str, f32, &str)] = &[
    ("league_garen_hits", 2.5, include_str!("../../../league/effects/league_garen_hits#anim.fanim")),
    ("league_garen_buffs", 2.5, include_str!("../../../league/effects/league_garen_buffs#anim.fanim")),
    ("league_garen_spin", 2.5, include_str!("../../../league/effects/league_garen_spin#anim.fanim")),
    ("league_garen_r", 2.5, include_str!("../../../league/effects/league_garen_r#anim.fanim")),
    ("league_garen_sym", 2.5, include_str!("../../../league/effects/league_garen_sym#anim.fanim")),
];

/// Champion id, its size everywhere the dense frames are drawn (1.0 = the 1x frames' size): the anim tables' rects and
/// the texture's reported size are divided by PPU / size (src/lookup.rs: the cards, the encyclopedia, the face icons,
/// the BP slots draw him that much smaller, the UVs unchanged) and the battlefield scale is the game's / PPU x size
/// (src/view.rs), each about the frame's centre / the unit's position - so the hero's dense frames are drawn lower by
/// (1 / size - 1) x the pivot-to-soles distance and the soles stay where they were (tools/art/ppu_gragas.py SHIFT).
/// Gragas: the user, 2026-10-12: 「酒桶模型缩小一点 太大了」 (85%), then 「要改全改啊」, then 80% (「怎么看起来还是比诺手高这么多」) (the cards and the encyclopedia too).
/// Zeri: 「等等泽丽感觉游戏里有点小」, picked 105% from the size sheet (drawn RAISE rows higher: tools/art/ppu_zeri.py).
pub const SIZES: &[(&str, f32)] = &[("league_gragas", 0.80), ("league_zeri", 1.05)];

pub const PREFIX: &str = "hd_";

/// The `"hd_..."` animation names of a .fanim (its keys under "anims"; no frame key starts with hd_).
pub fn hd_tags(fanim: &str) -> Vec<String> {
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
        if j < b.len() && b[j] == b':' && name.starts_with(PREFIX) && !out.iter().any(|t| t == name) {
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
    /// the tag whose first frame tells a changed table from an untouched one (src/lookup.rs): idle for a hero, the
    /// first tag for an effect sheet
    pub check: String,
    pub effect: bool,
}

impl Hero {
    /// What a dense frame's pixels are divided by to give its shown size: PPU / size.
    pub fn shown(&self) -> f32 {
        self.ppu / self.size
    }
}

fn sheet(id: &'static str, ppu: f32, fanim: &str, effect: bool) -> Hero {
    let tags: Vec<String> = hd_tags(fanim).into_iter().map(|t| t[PREFIX.len()..].to_string()).collect();
    let check = if effect { tags.first().cloned().unwrap_or_default() } else { "idle".to_string() };
    Hero { id, ppu, size: SIZES.iter().find(|s| s.0 == id).map_or(1.0, |s| s.1), tags, check, effect }
}

/// The heroes (src/view.rs scales their battlefield entities).
pub fn heroes() -> Vec<Hero> {
    HEROES.iter().map(|&(id, ppu, fanim)| sheet(id, ppu, fanim, false)).collect()
}

/// The heroes and the effect sheets (src/lookup.rs changes the tables and textures of both).
pub fn sheets() -> Vec<Hero> {
    let mut v = heroes();
    v.extend(EFFECTS.iter().map(|&(id, ppu, fanim)| sheet(id, ppu, fanim, true)));
    v
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
        }
    }

    #[test]
    fn every_effect_sheet_has_an_hd_copy_of_each_tag() {
        for &(id, _, fanim) in EFFECTS {
            let hd = hd_tags(fanim);
            assert!(!hd.is_empty(), "{id}: no hd_ tags (python tools/art/ppu_garen_fx.py)");
            for t in &hd {
                assert!(fanim.contains(&format!("\"{}\"", &t[PREFIX.len()..])), "{id}: {t} without its 1x tag");
            }
        }
        let s = sheets();
        assert!(s.iter().any(|h| h.effect && h.check == "spark"));
        assert!(s.iter().filter(|h| !h.effect).all(|h| h.check == "idle"));
    }

    #[test]
    fn tags_are_read_from_a_fanim() {
        let f = r#"{"anims":{"idle":{"frames":[{"duration":0.1,"data":{"x":0.0}}]},"hd_idle":{"frames":[]},"hd_run" : {}}}"#;
        assert_eq!(hd_tags(f), vec!["hd_idle".to_string(), "hd_run".to_string()]);
    }
}
