//! Which heroes have dense (PPU) frames, and what the display hook does with them - the parts that need no game.
//!
//! A hero listed in `HEROES` carries `hd_<tag>` beside every `<tag>` in its own sheet (tools/art/ppu_hd.py, the same
//! PPU there), each frame PPU times the 1x frame's size. The hook plays `hd_<tag>` where the game plays `<tag>` and
//! draws the entity at its scale / PPU. The tags are read from the sheet's .fanim compiled in, so the DLL never asks
//! for an animation the sheet lacks (the game panics on a missing one: 「animation info not found」).

/// Champion id, pixels per 1x square, the sheet's .fanim (as shipped in league/).
pub const HEROES: &[(&str, f32, &str)] =
    &[("league_yasuo", 2.0, include_str!("../../../league/champions/league_yasuo#anim.fanim"))];

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
    pub tags: Vec<String>,
}

pub fn heroes() -> Vec<Hero> {
    HEROES
        .iter()
        .map(|&(id, ppu, fanim)| Hero {
            id,
            ppu,
            tags: hd_tags(fanim).into_iter().map(|t| t[PREFIX.len()..].to_string()).collect(),
        })
        .collect()
}

/// The animation the entity should play: `hd_<tag>` for a tag with a dense copy, the plain name for anything else
/// (a name the hook put on last frame comes back to its plain one first). None when it already plays that.
pub fn anim_for(cur: &str, tags: &[String]) -> Option<String> {
    let plain = cur.strip_prefix(PREFIX).unwrap_or(cur);
    let want = if tags.iter().any(|t| t == plain) { format!("{PREFIX}{plain}") } else { plain.to_string() };
    (want != cur).then_some(want)
}

/// One entity's draw scale: the game's own value (base) and what the hook last wrote over it.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Scale {
    pub base: f32,
    pub wrote: f32,
}

/// The scale to write this frame. `cur` is what the entity holds now: the hook's own last value (the game left it
/// alone - keep the base) or a fresh one from the game (a new base). Never divides twice.
pub fn next_scale(prev: Option<Scale>, cur: f32, ppu: f32) -> Scale {
    let base = match prev {
        Some(p) if (cur - p.wrote).abs() <= 1e-6 => p.base,
        _ => cur,
    };
    Scale { base, wrote: base / ppu }
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
    fn names_swap_both_ways() {
        let tags = vec!["idle".to_string(), "run".to_string()];
        assert_eq!(anim_for("idle", &tags).as_deref(), Some("hd_idle"));
        assert_eq!(anim_for("hd_idle", &tags), None);
        assert_eq!(anim_for("hd_ult", &tags).as_deref(), Some("ult"));
        assert_eq!(anim_for("ult", &tags), None);
    }

    #[test]
    fn the_scale_is_divided_once() {
        let s = next_scale(None, 1.0, 2.0);
        assert_eq!(s, Scale { base: 1.0, wrote: 0.5 });
        let s = next_scale(Some(s), 0.5, 2.0); // the game left our value
        assert_eq!(s, Scale { base: 1.0, wrote: 0.5 });
        let s = next_scale(Some(s), 1.0, 2.0); // the game wrote its own again
        assert_eq!(s, Scale { base: 1.0, wrote: 0.5 });
        let s = next_scale(Some(s), 1.3, 2.0); // a new base (a growth effect)
        assert_eq!(s, Scale { base: 1.3, wrote: 0.65 });
    }

    #[test]
    fn tags_are_read_from_a_fanim() {
        let f = r#"{"anims":{"idle":{"frames":[{"duration":0.1,"data":{"x":0.0}}]},"hd_idle":{"frames":[]},"hd_run" : {}}}"#;
        assert_eq!(hd_tags(f), vec!["hd_idle".to_string(), "hd_run".to_string()]);
    }
}
