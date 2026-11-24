//! Unified animation-tag display hook for all Abyss Pact (渊契) multi-form heroes:
//! - Bloodmoon (`abysspact_bloodmoon`): Human <-> Wolf (`wf_*`)
//! - Carapace  (`abysspact_carapace`):  Form 1 Armored -> Form 2 Bug (`bg_*`) -> Form 3 Winged (`wg_*`)
//! - Leech     (`abysspact_leech`):     Normal <-> Attached clinging on host's back (`attach`)
//! - Anchor    (`abysspact_anchor`):    Drag <-> Siege deployed cannon (`siege_idle` / `siege_attack`)
//! - Hourglass (`abysspact_hourglass`): Young black hair -> Grey (`gr_*`) -> White (`wh_*`)

#[cfg(windows)]
use std::sync::Once;

/// Maps an entity's current animation tag to its form-specific tag, or `None` if unchanged.
pub fn map_tag(hero: &str, cur: &str, has: impl Fn(&str) -> bool) -> Option<&'static str> {
    match hero {
        "abysspact_bloodmoon" => {
            let wolf = has(crate::bloodmoon::WOLF_BUFF) || has(crate::bloodmoon::GIANT_BUFF);
            crate::bloodmoon::anim_for(cur, wolf)
        }
        "abysspact_carapace" => {
            if has(crate::carapace::FORM3_BUFF) {
                prefix_map(cur, "wg_")
            } else if has(crate::carapace::FORM2_BUFF) {
                prefix_map(cur, "bg_")
            } else {
                strip_to_base(cur)
            }
        }
        "abysspact_leech" => {
            if has(crate::leech::ATTACHED_BUFF) {
                match cur {
                    "idle" | "run" | "attack" | "hit" => Some("attach"),
                    _ => None,
                }
            } else if cur == "attach" {
                Some("idle")
            } else {
                None
            }
        }
        "abysspact_anchor" => {
            if has(crate::anchor::SIEGE_BUFF) {
                match cur {
                    "idle" | "run" | "hit" => Some("siege_idle"),
                    "attack" => Some("siege_attack"),
                    _ => None,
                }
            } else {
                match cur {
                    "siege_idle" => Some("idle"),
                    "siege_attack" => Some("attack"),
                    _ => None,
                }
            }
        }
        "abysspact_hourglass" => {
            if has(crate::hourglass::HAIR_WHITE) {
                prefix_map(cur, "wh_")
            } else if has(crate::hourglass::HAIR_GREY) {
                prefix_map(cur, "gr_")
            } else {
                strip_to_base(cur)
            }
        }
        _ => None,
    }
}

fn base_of(cur: &str) -> Option<&'static str> {
    let bare = cur
        .strip_prefix("bg_")
        .or_else(|| cur.strip_prefix("wg_"))
        .or_else(|| cur.strip_prefix("gr_"))
        .or_else(|| cur.strip_prefix("wh_"))
        .unwrap_or(cur);
    match bare {
        "idle" => Some("idle"),
        "run" => Some("run"),
        "attack" => Some("attack"),
        "skill" => Some("skill"),
        "skill2" => Some("skill2"),
        "ult" => Some("ult"),
        "hit" => Some("hit"),
        "dead" => Some("dead"),
        _ => None,
    }
}

fn strip_to_base(cur: &str) -> Option<&'static str> {
    if cur.starts_with("bg_")
        || cur.starts_with("wg_")
        || cur.starts_with("gr_")
        || cur.starts_with("wh_")
    {
        base_of(cur)
    } else {
        None
    }
}

fn prefix_map(cur: &str, pref: &str) -> Option<&'static str> {
    let base = base_of(cur)?;
    let target = match (pref, base) {
        ("bg_", "idle") => "bg_idle",
        ("bg_", "run") => "bg_run",
        ("bg_", "attack") => "bg_attack",
        ("bg_", "skill") => "bg_skill",
        ("bg_", "skill2") => "bg_skill2",
        ("bg_", "ult") => "bg_ult",
        ("bg_", "hit") => "bg_hit",
        ("bg_", "dead") => "bg_dead",
        ("wg_", "idle") => "wg_idle",
        ("wg_", "run") => "wg_run",
        ("wg_", "attack") => "wg_attack",
        ("wg_", "skill") => "wg_skill",
        ("wg_", "skill2") => "wg_skill2",
        ("wg_", "ult") => "wg_ult",
        ("wg_", "hit") => "wg_hit",
        ("wg_", "dead") => "wg_dead",
        ("gr_", "idle") => "gr_idle",
        ("gr_", "run") => "gr_run",
        ("gr_", "attack") => "gr_attack",
        ("gr_", "skill") => "gr_skill",
        ("gr_", "skill2") => "gr_skill2",
        ("gr_", "ult") => "gr_ult",
        ("gr_", "hit") => "gr_hit",
        ("gr_", "dead") => "gr_dead",
        ("wh_", "idle") => "wh_idle",
        ("wh_", "run") => "wh_run",
        ("wh_", "attack") => "wh_attack",
        ("wh_", "skill") => "wh_skill",
        ("wh_", "skill2") => "wh_skill2",
        ("wh_", "ult") => "wh_ult",
        ("wh_", "hit") => "wh_hit",
        ("wh_", "dead") => "wh_dead",
        _ => return None,
    };
    (target != cur).then_some(target)
}

#[cfg(windows)]
mod hook_impl {
    use super::*;
    use game_places::hook::{
        Ent, ANIM_CAP, ANIM_LEN, ANIM_PTR, BUFFS_LEN, BUFFS_PTR, BUFF_SIZE, NAME_LEN_AT, NAME_PTR, VALUE,
    };

    static HOOK: Once = Once::new();

    #[link(name = "kernel32")]
    extern "system" {
        fn GetProcessHeap() -> isize;
        fn HeapAlloc(heap: isize, flags: u32, bytes: usize) -> *mut u8;
        fn HeapFree(heap: isize, flags: u32, mem: *mut u8) -> i32;
    }

    #[inline]
    unsafe fn q(p: usize) -> usize {
        std::ptr::read_unaligned(p as *const usize)
    }

    #[inline]
    fn plausible(p: usize) -> bool {
        (0x10000..=0x7fff_ffff_ffff).contains(&p)
    }

    unsafe fn has_buff_raw(v: usize, want: &str) -> bool {
        let (bp, bn) = (q(v + BUFFS_PTR), q(v + BUFFS_LEN));
        plausible(bp) && bn <= 256 && (0..bn).any(|k| {
            let bf = bp + k * BUFF_SIZE;
            let (p, n) = (q(bf + 8), q(bf + 0x10));
            if !plausible(p) || n != want.len() {
                return false;
            }
            std::slice::from_raw_parts(p as *const u8, n) == want.as_bytes()
        })
    }

    unsafe fn dress(_world: usize, ents: &[Ent]) {
        for e in ents {
            let v = e.elem + VALUE;
            let nlen = q(v + NAME_LEN_AT);
            if !(14..=24).contains(&nlen) {
                continue;
            }
            let nptr = q(v + NAME_PTR);
            if !plausible(nptr) {
                continue;
            }
            let Ok(hero) = std::str::from_utf8(std::slice::from_raw_parts(nptr as *const u8, nlen)) else {
                continue;
            };
            if !matches!(
                hero,
                "abysspact_bloodmoon"
                    | "abysspact_carapace"
                    | "abysspact_leech"
                    | "abysspact_anchor"
                    | "abysspact_hourglass"
            ) {
                continue;
            }
            let (acap, aptr, alen) = (q(v + ANIM_CAP), q(v + ANIM_PTR), q(v + ANIM_LEN));
            if !(1..=32).contains(&alen) || acap < alen || !plausible(aptr) {
                continue;
            }
            let Ok(cur) = std::str::from_utf8(std::slice::from_raw_parts(aptr as *const u8, alen)) else {
                continue;
            };
            let Some(want) = map_tag(hero, cur, |b| has_buff_raw(v, b)) else {
                continue;
            };
            let heap = GetProcessHeap();
            let fresh = HeapAlloc(heap, 0, want.len());
            if fresh.is_null() {
                continue;
            }
            std::ptr::copy_nonoverlapping(want.as_ptr(), fresh, want.len());
            std::ptr::write_unaligned((v + ANIM_CAP) as *mut usize, want.len());
            std::ptr::write_unaligned((v + ANIM_PTR) as *mut usize, fresh as usize);
            std::ptr::write_unaligned((v + ANIM_LEN) as *mut usize, want.len());
            if acap > 0 {
                HeapFree(heap, 0, aptr as *mut u8);
            }
        }
    }

    pub fn install() {
        HOOK.call_once(|| {
            let _ = game_places::hook::add("abysspact_forms", dress, |m| crate::wlog(m));
        });
    }
}

pub fn install() {
    #[cfg(windows)]
    hook_impl::install();
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn all_five_form_mappings_work_and_roundtrip() {
        assert_eq!(map_tag("abysspact_carapace", "idle", |b| b == crate::carapace::FORM2_BUFF), Some("bg_idle"));
        assert_eq!(map_tag("abysspact_carapace", "bg_attack", |b| b == crate::carapace::FORM3_BUFF), Some("wg_attack"));
        assert_eq!(map_tag("abysspact_carapace", "wg_idle", |_| false), Some("idle"));

        assert_eq!(map_tag("abysspact_leech", "run", |b| b == crate::leech::ATTACHED_BUFF), Some("attach"));
        assert_eq!(map_tag("abysspact_leech", "attach", |_| false), Some("idle"));

        assert_eq!(map_tag("abysspact_anchor", "idle", |b| b == crate::anchor::SIEGE_BUFF), Some("siege_idle"));
        assert_eq!(map_tag("abysspact_anchor", "attack", |b| b == crate::anchor::SIEGE_BUFF), Some("siege_attack"));
        assert_eq!(map_tag("abysspact_anchor", "siege_idle", |_| false), Some("idle"));

        assert_eq!(map_tag("abysspact_hourglass", "ult", |b| b == crate::hourglass::HAIR_GREY), Some("gr_ult"));
        assert_eq!(map_tag("abysspact_hourglass", "gr_run", |b| b == crate::hourglass::HAIR_WHITE), Some("wh_run"));
        assert_eq!(map_tag("abysspact_hourglass", "wh_idle", |_| false), Some("idle"));
    }
}
