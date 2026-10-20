//! Which game build league.dll knows, by fingerprint: Steam 0.6.4 (2026-10-14). 0.6.3 is no longer listed (the user,
//! 2026-10-14: 「0.6.3不用适配了 直接0.6.4就行了」); the earlier wish to know two builds at once (2026-10-12: 「就是你要兼容
//! 0.6.3和0.7」) is why this is a list.
//!
//! Everything src/lookup.rs and src/view.rs patch or call sits at a fixed place in one build of the game EXE. A build
//! is known when the bytes at each of its places are exactly the ones read from that build: the two lookup functions
//! (128 bytes each - 33 functions share their first 128 but for the calls), the hash, the display handler, and the call
//! sites whose return addresses the hooks compare. An unknown build (a new game version, a beta) gets no hook at all and
//! the heroes draw their 1x frames, as on Mac / Linux; a build is added here once its places are found and checked.
//!
//! 0.6.4's places were found from 0.6.3's (2026-10-14, tools/re/find_build.py): the same code moved (the display
//! handler's first 48 bytes are 0.6.3's, the hash stayed at 0x58170), the structures it reads did not change (display
//! world table +0x138 / 0x1d0-byte entries, entity value +0x40 id, +0x50 body resource, +0x68 animation, +0xb8 buffs,
//! +0x17c position, +0x1b4 draw scale; 0xd0-byte draw commands, scale 0x…11 / restore 0x…12); the battlefield frame
//! lookup and the body draw's size asks sit at 0.6.3's offsets inside their functions; the body draw itself grew
//! (sub rsp 0x678 -> 0x698) with the same arguments; the UI drawers were matched by their 'idle' compare, their callers'
//! strings and the spacing of their four size asks.

/// One game build's places (rvas in TeamfightManager2.exe).
pub struct Build {
    pub name: &'static str,
    /// (ctx, name ptr, len) -> the `<path>#anim` table
    pub anim: usize,
    /// (ctx, name ptr, len) -> the `<path>#sheet` texture entry
    pub sheet: usize,
    /// the anim tables' hash (&hasher, key ptr, len) -> u64
    pub hash: usize,
    /// the display-update handler and the slot that holds it
    pub display_fn: usize,
    pub display_slot: usize,
    /// return addresses of the battlefield's anim lookup and of its size asks (src/lookup.rs)
    pub battle_anim_ret: &'static [usize],
    pub battle_size_ret: &'static [usize],
    /// return addresses of the UI's anim lookups and size asks that draw a hero's lo_ frames (src/lookup.rs ui_table):
    /// the encyclopedia / face icons, the pick slot, the BP grid, the pick moment, the scoreboard portraits
    pub ui_anim_ret: &'static [usize],
    pub ui_size_ret: &'static [usize],
    /// the ones of those that show the whole body - the pick slot, the BP grid, the pick moment: only they draw a hero at
    /// its [`crate::hd::UI_SIZES`] size; the encyclopedia / face icons and the scoreboard portraits crop around the
    /// face point and keep the plain UI size, so the face points stay on the faces
    pub ui_sized_anim_ret: &'static [usize],
    pub ui_sized_size_ret: &'static [usize],
    /// the battlefield body draw (rcx = the command Vec it fills, rdx = the display entity value; src/view.rs)
    pub body_draw: usize,
    /// RawVec<draw command>::grow_one (0xd0-byte commands)
    pub cmd_grow: usize,
    /// (rva, the bytes there)
    pub sigs: &'static [(usize, &'static [u8])],
}

pub static BUILDS: &[Build] = &[Build {
    name: "0.6.4 (Steam, EXE sha256 a1d05045...)",
    anim: 0x20fb50,
    sheet: 0x16cf80,
    hash: 0x58170,
    display_fn: 0x23312a0,
    display_slot: 0x3c82db8,
    battle_anim_ret: &[0x2ae8e40],
    battle_size_ret: &[0x2ae908f, 0x2ae9098, 0x2ab03ae, 0x2ab03ce, 0x2ab03e1, 0x2ab03f0],
    ui_anim_ret: &[0x24bf611, 0x24bba3a, 0x2a92c99, 0x20e323d, 0x2ac3388],
    ui_size_ret: &[0x24bf7d2, 0x24bf829, 0x24bf83f, 0x24bf854, 0x24bbc82, 0x24bbc98, 0x24bbca9, 0x24bbcbb,
                   0x2a92fd2, 0x2a92fe6, 0x2a92ff5, 0x2a93006, 0x20e35d8, 0x20e35e6, 0x20e35f0, 0x20e35fb,
                   0x2ac35de, 0x2ac35fd, 0x2ac3617, 0x2ac362c],
    ui_sized_anim_ret: &[0x24bba3a, 0x2a92c99, 0x20e323d],
    ui_sized_size_ret: &[0x24bbc82, 0x24bbc98, 0x24bbca9, 0x24bbcbb, 0x2a92fd2, 0x2a92fe6, 0x2a92ff5, 0x2a93006,
                         0x20e35d8, 0x20e35e6, 0x20e35f0, 0x20e35fb],
    body_draw: 0x2aaf630,
    cmd_grow: 0x38db8d0,
    sigs: &[
    // the anim-table lookup
    (0x20fb50, &[
        0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53, 0x48, 0x81, 0xec, 0x98,
        0x00, 0x00, 0x00, 0x48, 0x8d, 0xac, 0x24, 0x80, 0x00, 0x00, 0x00, 0x66, 0x44, 0x0f, 0x7f, 0x45,
        0x00, 0x66, 0x0f, 0x7f, 0x7d, 0xf0, 0x66, 0x0f, 0x7f, 0x75, 0xe0, 0x48, 0xc7, 0x45, 0xd8, 0xfe,
        0xff, 0xff, 0xff, 0x4d, 0x89, 0xc1, 0x49, 0x89, 0xd0, 0x48, 0x89, 0xcf, 0x48, 0x8d, 0x4d, 0xb0,
        0x48, 0x89, 0xfa, 0xe8, 0xb8, 0xba, 0xf7, 0xff, 0x48, 0x8b, 0x75, 0xb8, 0x48, 0x83, 0x7f, 0x48,
        0x00, 0x0f, 0x84, 0x06, 0x01, 0x00, 0x00, 0x48, 0x8b, 0x5d, 0xc0, 0x48, 0x8d, 0x4f, 0x50, 0x48,
        0x89, 0xf2, 0x49, 0x89, 0xd8, 0xe8, 0xb6, 0x85, 0xe4, 0xff, 0x48, 0x89, 0xc1, 0x48, 0xc1, 0xe9,
        0x39, 0x4c, 0x8b, 0x77, 0x30, 0x4c, 0x8b, 0x7f, 0x38, 0x66, 0x0f, 0x6e, 0xc1, 0x66, 0x0f, 0x60,
    ]),
    // the sheet (texture) lookup
    (0x16cf80, &[
        0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53, 0x48, 0x81, 0xec, 0x98,
        0x00, 0x00, 0x00, 0x48, 0x8d, 0xac, 0x24, 0x80, 0x00, 0x00, 0x00, 0x66, 0x44, 0x0f, 0x7f, 0x45,
        0x00, 0x66, 0x0f, 0x7f, 0x7d, 0xf0, 0x66, 0x0f, 0x7f, 0x75, 0xe0, 0x48, 0xc7, 0x45, 0xd8, 0xfe,
        0xff, 0xff, 0xff, 0x4d, 0x89, 0xc1, 0x49, 0x89, 0xd0, 0x48, 0x89, 0xcf, 0x48, 0x8d, 0x4d, 0xb0,
        0x48, 0x89, 0xfa, 0xe8, 0x88, 0xe6, 0x01, 0x00, 0x48, 0x8b, 0x75, 0xb8, 0x48, 0x83, 0x7f, 0x48,
        0x00, 0x0f, 0x84, 0x06, 0x01, 0x00, 0x00, 0x48, 0x8b, 0x5d, 0xc0, 0x48, 0x8d, 0x4f, 0x50, 0x48,
        0x89, 0xf2, 0x49, 0x89, 0xd8, 0xe8, 0x86, 0xb1, 0xee, 0xff, 0x48, 0x89, 0xc1, 0x48, 0xc1, 0xe9,
        0x39, 0x4c, 0x8b, 0x77, 0x30, 0x4c, 0x8b, 0x7f, 0x38, 0x66, 0x0f, 0x6e, 0xc1, 0x66, 0x0f, 0x60,
    ]),
    // the battlefield body draw
    (0x2aaf630, &[
        0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53, 0x48, 0x81, 0xec, 0x98,
        0x06, 0x00, 0x00, 0x48, 0x8d, 0xac, 0x24, 0x80,
    ]),
    // the draw commands' grow_one (new capacity max(4, 2 x cap), 0xd0 bytes, align 8)
    (0x38db8d0, &[
        0x56, 0x57, 0x48, 0x83, 0xec, 0x48, 0x48, 0x89, 0xce, 0x48, 0x8b, 0x11, 0x48, 0x8d, 0x04, 0x12,
        0x48, 0x83, 0xf8, 0x05, 0xbf, 0x04, 0x00, 0x00, 0x00, 0x48, 0x0f, 0x43, 0xf8, 0x4c, 0x8b, 0x41,
        0x08, 0x48, 0xc7, 0x44, 0x24, 0x28, 0xd0, 0x00, 0x00, 0x00, 0x48, 0xc7, 0x44, 0x24, 0x20, 0x08,
    ]),
    // the entity render's call of the body draw, and its scale command (+0x1b4 round the body draw's commands)
    (0x2abfcd5, &[0xe8, 0x56, 0xf9, 0xfe, 0xff]),
    (0x2abfdc0, &[0xf3, 0x0f, 0x10, 0x8f, 0xb4, 0x01, 0x00, 0x00]),
    // the UI's calls of the anim lookup (encyclopedia, pick slot, BP grid, pick moment, scoreboard portraits) and
    // their size asks
    (0x24bf60c, &[0xe8, 0x3f, 0x05, 0xd5, 0xfd]), // encyclopedia / face icons
    (0x24bf7d0, &[0xff, 0xd3]), (0x24bf826, &[0x41, 0xff, 0xd7]), (0x24bf83d, &[0xff, 0xd3]), (0x24bf851, &[0x41, 0xff, 0xd7]),
    (0x24bba35, &[0xe8, 0x16, 0x41, 0xd5, 0xfd]), // pick slot
    (0x24bbc80, &[0xff, 0xd7]), (0x24bbc95, &[0x41, 0xff, 0xd6]), (0x24bbca7, &[0xff, 0xd7]), (0x24bbcb8, &[0x41, 0xff, 0xd6]),
    (0x2a92c94, &[0xe8, 0xb7, 0xce, 0x77, 0xfd]), // BP grid
    (0x2a92fd0, &[0xff, 0xd7]), (0x2a92fe3, &[0x41, 0xff, 0xd6]), (0x2a92ff3, &[0xff, 0xd7]), (0x2a93003, &[0x41, 0xff, 0xd6]),
    (0x20e3238, &[0xe8, 0x13, 0xc9, 0x12, 0xfe]), // pick moment
    (0x20e35d5, &[0x41, 0xff, 0xd6]), (0x20e35e3, &[0x41, 0xff, 0xd7]), (0x20e35ed, &[0x41, 0xff, 0xd6]), (0x20e35f8, &[0x41, 0xff, 0xd7]),
    (0x2ac3383, &[0xe8, 0xc8, 0xc7, 0x74, 0xfd]), // scoreboard portraits
    (0x2ac35dc, &[0xff, 0xd3]), (0x2ac35fa, &[0x41, 0xff, 0xd6]), (0x2ac3615, &[0xff, 0xd3]), (0x2ac3629, &[0x41, 0xff, 0xd6]),
    // the anim tables' hash
    (0x58170, &[
        0x56, 0x48, 0x81, 0xec, 0x80, 0x00, 0x00, 0x00, 0xf3, 0x0f, 0x6f, 0x01, 0x66, 0x0f, 0x70, 0xc8,
        0x44, 0x66, 0x0f, 0xef, 0x0d, 0x27, 0x05, 0x9d, 0x03, 0x66, 0x0f, 0x7f, 0x4c, 0x24, 0x30, 0x66,
        0x0f, 0x70, 0xc8, 0xee, 0x66, 0x0f, 0xef, 0x0d, 0x24, 0x05, 0x9d, 0x03, 0x66, 0x0f, 0x7f, 0x4c,
    ]),
    // the display-update handler
    (0x23312a0, &[
        0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x55, 0x53, 0x48, 0x81, 0xec, 0x88,
        0x00, 0x00, 0x00, 0x66, 0x0f, 0x7f, 0x7c, 0x24, 0x70, 0x0f, 0x29, 0x74, 0x24, 0x60, 0x48, 0x8b,
        0x59, 0x18, 0x48, 0x85, 0xdb, 0x0f, 0x84, 0x20, 0x05, 0x00, 0x00, 0x4c, 0x8b, 0x29, 0x66, 0x41,
    ]),
    // the battlefield frame lookup's call of the anim lookup, and its size asks (width, height)
    (0x2ae8e3b, &[0xe8, 0x10, 0x6d, 0x72, 0xfd]),
    (0x2ae908c, &[0xff, 0x53, 0x28]),
    (0x2ae9095, &[0xff, 0x53, 0x30]),
    // the body draw's size asks
    (0x2ab03ac, &[0xff, 0xd7]), (0x2ab03cb, &[0x41, 0xff, 0xd5]), (0x2ab03df, &[0xff, 0xd7]), (0x2ab03ed, &[0x41, 0xff, 0xd5]),
    ],
}];

/// A build found at run time (game_places::resolve, 2026-10-20: 「想个方法做个动态寻地址的 后面游戏更新了我们维护压力小一点」):
/// when no listed build's fingerprints hold, league.dll looks for the same places by the patterns made from the listed
/// one; found, they are kept for the process (leaked: one Build per load).
pub fn from_places(p: game_places::Places, name: String) -> &'static Build {
    let keep = |v: Vec<usize>| -> &'static [usize] { Box::leak(v.into_boxed_slice()) };
    Box::leak(Box::new(Build {
        name: Box::leak(name.into_boxed_str()),
        anim: p.anim,
        sheet: p.sheet,
        hash: p.hash,
        display_fn: p.display_fn,
        display_slot: p.display_slot,
        battle_anim_ret: keep(p.battle_anim_ret),
        battle_size_ret: keep(p.battle_size_ret),
        ui_anim_ret: keep(p.ui_anim_ret),
        ui_size_ret: keep(p.ui_size_ret),
        ui_sized_anim_ret: keep(p.ui_sized_anim_ret),
        ui_sized_size_ret: keep(p.ui_sized_size_ret),
        body_draw: p.body_draw,
        cmd_grow: p.cmd_grow,
        sigs: &[],
    }))
}

/// The known build whose every fingerprint `read(rva, len)` matches, else None (and why the first one failed).
pub fn detect(read: impl Fn(usize, usize) -> Option<Vec<u8>>) -> Result<&'static Build, String> {
    let mut why = String::from("no builds listed");
    for b in BUILDS {
        match b.sigs.iter().find(|(rva, want)| read(*rva, want.len()).as_deref() != Some(*want)) {
            None => return Ok(b),
            Some((rva, _)) => why = format!("not {}: the bytes at {rva:#x} differ", b.name),
        }
    }
    Err(why)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn only_the_whole_body_drawers_take_the_ui_sizes() {
        for b in BUILDS {
            // the pick slot, the BP grid, the pick moment: among the UI callers, each with its four size asks
            assert_eq!(b.ui_sized_anim_ret.len(), 3, "{}", b.name);
            assert_eq!(b.ui_sized_size_ret.len(), 4 * b.ui_sized_anim_ret.len(), "{}", b.name);
            assert!(b.ui_sized_anim_ret.iter().all(|r| b.ui_anim_ret.contains(r)));
            assert!(b.ui_sized_size_ret.iter().all(|r| b.ui_size_ret.contains(r)));
            // the face crops - the encyclopedia / face icons (first) and the scoreboard portraits (last) - are not
            let (first, last) = (b.ui_anim_ret[0], b.ui_anim_ret[b.ui_anim_ret.len() - 1]);
            assert!(!b.ui_sized_anim_ret.contains(&first) && !b.ui_sized_anim_ret.contains(&last));
            assert!(b.ui_size_ret[..4].iter().chain(&b.ui_size_ret[b.ui_size_ret.len() - 4..])
                .all(|r| !b.ui_sized_size_ret.contains(r)));
            // each sized drawer's size asks follow its lookup (the spacing build.rs matched them by)
            for (k, a) in b.ui_sized_anim_ret.iter().enumerate() {
                assert!(b.ui_sized_size_ret[4 * k..4 * k + 4].iter().all(|r| *r > *a && *r - *a < 0x1000), "{a:#x}");
            }
        }
    }

    /// The run-time finder (game_places::resolve) on the game's EXE on disk must find exactly the listed places (skipped
    /// when the game is not installed at the usual path or is another build).
    #[test]
    fn the_run_time_finder_finds_the_listed_build() {
        let path = std::env::var("TFM2_EXE")
            .unwrap_or_else(|_| r"D:/steam/steamapps/common/Teamfight Manager2/TeamfightManager2.exe".into());
        let Ok(data) = std::fs::read(&path) else { return };
        let img = game_places::Image::from_file(&data).unwrap();
        let b = &BUILDS[0];
        if detect(|rva, n| img.read(rva, n).map(|x| x.to_vec())).is_err() {
            return; // another build: nothing to compare with
        }
        let t0 = std::time::Instant::now();
        let p = game_places::resolve(&img).unwrap();
        eprintln!("resolved in {:?}: {:?}", t0.elapsed(), p.notes);
        assert_eq!((p.anim, p.sheet, p.hash, p.display_fn, p.display_slot, p.body_draw, p.cmd_grow),
                   (b.anim, b.sheet, b.hash, b.display_fn, b.display_slot, b.body_draw, b.cmd_grow));
        assert_eq!(p.battle_anim_ret, b.battle_anim_ret);
        assert_eq!(p.battle_size_ret, b.battle_size_ret);
        assert_eq!(p.ui_anim_ret, b.ui_anim_ret);
        assert_eq!(p.ui_size_ret, b.ui_size_ret);
        assert_eq!(p.ui_sized_anim_ret, b.ui_sized_anim_ret);
        assert_eq!(p.ui_sized_size_ret, b.ui_sized_size_ret);
    }

    #[test]
    fn a_build_is_known_only_by_all_its_bytes() {
        let b = &BUILDS[0];
        let all = |rva: usize, n: usize| b.sigs.iter().find(|s| s.0 == rva).map(|s| s.1[..n].to_vec());
        assert_eq!(detect(all).unwrap().name, b.name);
        // one byte off anywhere: unknown
        let (bad_rva, bad) = (b.sigs[4].0, b.sigs[4].1);
        let off = |rva: usize, n: usize| {
            let mut v = all(rva, n)?;
            if rva == bad_rva {
                v[bad.len() - 1] ^= 1;
            }
            Some(v)
        };
        assert!(detect(off).is_err());
        assert!(detect(|_, _| None).is_err());
        // the hooks' places are among the checked ones
        for rva in [b.anim, b.sheet, b.hash, b.display_fn, b.body_draw, b.cmd_grow] {
            assert!(b.sigs.iter().any(|s| s.0 == rva), "{rva:#x} unchecked");
        }
    }
}
