//! Which game build league.dll knows, by fingerprint: Steam 0.7.0 (2026-10-28). 0.6.5 is no longer listed, as 0.6.4 and
//! 0.6.3 were dropped before it (the user, 2026-10-14: 「0.6.3不用适配了 直接0.6.4就行了」) - another build is looked for at
//! run time ([`from_places`]); the earlier wish to know two builds at once (2026-10-12: 「就是你要兼容0.6.3和0.7」) is why
//! this is a list.
//!
//! 0.7.0's places were found from 0.6.5's (2026-10-28, tools/re/find_build.py; the user: 「游戏更新到SDK0.7.0了 我们要
//! 进行适配」). The EXE was built by a newer Rust compiler (its format strings are encoded another way): 0.6.5's patterns
//! found nothing, the game drew every hero at 1x. What changed: the lookups' head (sub rsp 0x98 -> 0xa8, the key
//! builder takes one more argument, the asset map moved inside its context: ctrl +0x368, items +0x380, hasher +0x388),
//! the hash's head is the same at 0x5e840; the body draw's four size asks keep their spacing but call other registers
//! (r13 -> r15); the entity render reads the scale as `movss xmm1, [r12+0x1b4]` (a SIB form); a draw command variant
//! was added before the scale and restore commands, so their tags are 0x…12 / 0x…13 (0.6.5: 0x…11 / 0x…12) -
//! [`Build::cmd_scale`]; the draw command made from a name pushes one register more (src/ui.rs runs whatever push /
//! sub rsp prologue it has). The rest was checked instruction by instruction and did not change: the display
//! handler's first 48 bytes are 0.6.5's; the display world (+0x138 / +0x140 / +0x150, 0x1d0-byte entries), the entity
//! value (+0x40 / +0x48 id, +0x50 / +0x58 / +0x60 body resource - the body draw formats its sheet's name from it,
//! +0x68 animation, +0xb8 / +0xc0 buffs of 0x28 bytes, +0x17c / +0x180 / +0x18c position, +0x1b4 scale), the anim
//! table (hashbrown head ctrl / mask / growth / items / hasher +0x20, 0x30-byte buckets: key String, frames Vec at
//! +0x18, 20-byte frames, duration at +0x10), the texture entry (data, vtable: width +0x28, height +0x30), the body
//! draw's arguments (it reads neither r9 nor its fifth argument), the 0xd0-byte draw commands (sprite 0x…03: sheet
//! name String +8, corner +0x78; scale: translation +8 / +0xc, factors +0x24 / +0x28, zeros between) and the view
//! node draw's Option<Vec> (None: cap usize::MAX). New in 0.7.0: the UI styles (Classic / New Light / New Dark) and a
//! console layout - the five drawers below are the game's shared ones (ui.rs, banpick_champion_slot.rs); a drawer of
//! another layout that is not among them gets the in-place dense frames at the plain UI size (src/lookup.rs).
//!
//! 2026-10-24: + the UI drawers' own sheet lookups and the two functions they hand a sheet's name to (src/ui.rs, the
//! UI sheets), found in 0.6.5 by hand (static disassembly; game_places::resolve finds them from the drawers).
//!
//! Everything src/lookup.rs, src/ui.rs and src/view.rs patch or call sits at a fixed place in one build of the game EXE. A build
//! is known when the bytes at each of its places are exactly the ones read from that build: the two lookup functions
//! (128 bytes each - 33 functions share their first 128 but for the calls), the hash, the display handler, and the call
//! sites whose return addresses the hooks compare. An unknown build (a new game version, a beta) is looked for by
//! game_places::resolve; when that fails too it gets no hook at all and the heroes draw their 1x frames, as on Mac /
//! Linux.
//!
//! 0.6.5's places were found from 0.6.4's (2026-10-21, tools/re/find_build.py; game_places::resolve finds the same ones
//! from 0.6.4's patterns since it reads the scale through a REX prefix and looks for the scoreboard portraits' drawer
//! inside the entity render): all the code moved again (the display handler's first 48 bytes are 0.6.4's, the hash
//! stayed at 0x58170), the structures it reads did not change (the display handler, the body draw and the entity render
//! still read the world table at +0x138 / +0x140 / +0x150 with 0x1d0-byte entries, the entity value's +0x40 id, +0x50 /
//! +0x60 body resource, +0x68 animation, +0xb8 / +0xc0 buffs, +0x17c / +0x180 / +0x18c position and +0x1b4 draw scale;
//! 0xd0-byte draw commands); the body draw shrank back to 0.6.3's frame (sub rsp 0x698 -> 0x678) with the same
//! arguments and its size asks at the old offsets; the entity render reads the scale through r13 (`movss xmm1,
//! [r13+0x1b4]`, 0.6.4: rdi); the scoreboard portraits' size asks moved by 3 bytes.
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
    /// return addresses of those UI drawers' own sheet lookups (the same order as `ui_anim_ret`): src/ui.rs hands them
    /// the hero's UI sheet
    pub ui_sheet_ret: &'static [usize],
    /// the two functions the UI drawers hand the sheet's name to - each copies it, and the texture is looked up by that
    /// name again when the frame is drawn: (out, name ptr, len, ...) -> a draw command (the BP grid, the scoreboard
    /// portraits, the pick moment's callers) and (image node, &String, &uv) (the encyclopedia / face icons, the pick
    /// slot). src/ui.rs swaps the name for the UI sheet's there. 0: not known (no UI sheets).
    pub cmd_by_name: usize,
    pub node_image: usize,
    /// the battlefield body draw (rcx = the command Vec it fills, rdx = the display entity value; src/view.rs)
    pub body_draw: usize,
    /// RawVec<draw command>::grow_one (0xd0-byte commands)
    pub cmd_grow: usize,
    /// the view node draw (rcx = the command Vec it returns, rdx = the node, r8 / r9 its own; the battlefield body draw
    /// and the world's effects call it): an effect picture's sprite command, UV x the texture's real pixels from a
    /// corner placed with its frame's size (src/view.rs effect_detour). 0: not known (dense effects drawn PPU times big).
    pub effect_draw: usize,
    /// the tags (the draw command enum's niche values at +0) of the scale and restore commands the entity render wraps
    /// the body draw's commands in: src/view.rs puts the same pairs round a dense hero's extras and round dense effects
    /// (0.6.5: 0x…11 / 0x…12; 0.7.0 added a variant before them)
    pub cmd_scale: u64,
    pub cmd_restore: u64,
    /// (rva, the bytes there)
    pub sigs: &'static [(usize, &'static [u8])],
}

pub static BUILDS: &[Build] = &[Build {
    name: "0.7.0 (Steam, EXE sha256 d678e012...)",
    anim: 0x261f50,
    sheet: 0x159060,
    hash: 0x5e840,
    display_fn: 0x309ad00,
    display_slot: 0x416f528,
    battle_anim_ret: &[0x250f790],
    battle_size_ret: &[0x250f9df, 0x250f9e8, 0x246711b, 0x246713b, 0x246714e, 0x246715d],
    ui_anim_ret: &[0x2f5a521, 0x2f5570a, 0x2431609, 0x2f6c29d, 0x2f2ab53],
    ui_size_ret: &[0x2f5a6e2, 0x2f5a739, 0x2f5a74f, 0x2f5a764, 0x2f55952, 0x2f55968, 0x2f55979, 0x2f5598b,
                   0x2431942, 0x2431956, 0x2431965, 0x2431976, 0x2f6c638, 0x2f6c646, 0x2f6c650, 0x2f6c65b,
                   0x2f2ad8f, 0x2f2adae, 0x2f2adc9, 0x2f2adde],
    ui_sized_anim_ret: &[0x2f5570a, 0x2431609, 0x2f6c29d],
    ui_sized_size_ret: &[0x2f55952, 0x2f55968, 0x2f55979, 0x2f5598b, 0x2431942, 0x2431956, 0x2431965, 0x2431976,
                         0x2f6c638, 0x2f6c646, 0x2f6c650, 0x2f6c65b],
    ui_sheet_ret: &[0x2f5a53e, 0x2f55727, 0x2431923, 0x2f6c3fa, 0x2f2abd9],
    cmd_by_name: 0x1c97d0,
    node_image: 0x2beb0c0,
    body_draw: 0x2466400,
    cmd_grow: 0x3e65ef0,
    effect_draw: 0x245f150,
    cmd_scale: 0x8000000000000012,
    cmd_restore: 0x8000000000000013,
    sigs: &[
    // the anim-table lookup
    (0x261f50, &[
        0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53, 0x48, 0x81, 0xec, 0xa8,
        0x00, 0x00, 0x00, 0x48, 0x8d, 0xac, 0x24, 0x80, 0x00, 0x00, 0x00, 0x66, 0x44, 0x0f, 0x7f, 0x45,
        0x10, 0x66, 0x0f, 0x7f, 0x7d, 0x00, 0x66, 0x0f, 0x7f, 0x75, 0xf0, 0x48, 0xc7, 0x45, 0xe8, 0xfe,
        0xff, 0xff, 0xff, 0x4d, 0x89, 0xc1, 0x49, 0x89, 0xd0, 0x48, 0x89, 0xcf, 0xc6, 0x44, 0x24, 0x20,
        0x01, 0x48, 0x8d, 0x4d, 0xc0, 0x48, 0x89, 0xfa, 0xe8, 0xc3, 0x08, 0xf4, 0xff, 0x48, 0x8b, 0x75,
        0xc8, 0x48, 0x83, 0xbf, 0x80, 0x03, 0x00, 0x00, 0x00, 0x0f, 0x84, 0x0e, 0x01, 0x00, 0x00, 0x48,
        0x8b, 0x5d, 0xd0, 0x48, 0x8d, 0x8f, 0x88, 0x03, 0x00, 0x00, 0x48, 0x89, 0xf2, 0x49, 0x89, 0xd8,
        0xe8, 0x7b, 0xc8, 0xdf, 0xff, 0x48, 0x89, 0xc1, 0x48, 0xc1, 0xe9, 0x39, 0x4c, 0x8b, 0xb7, 0x68,
    ]),
    // the sheet (texture) lookup
    (0x159060, &[
        0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53, 0x48, 0x81, 0xec, 0xa8,
        0x00, 0x00, 0x00, 0x48, 0x8d, 0xac, 0x24, 0x80, 0x00, 0x00, 0x00, 0x66, 0x44, 0x0f, 0x7f, 0x45,
        0x10, 0x66, 0x0f, 0x7f, 0x7d, 0x00, 0x66, 0x0f, 0x7f, 0x75, 0xf0, 0x48, 0xc7, 0x45, 0xe8, 0xfe,
        0xff, 0xff, 0xff, 0x4d, 0x89, 0xc1, 0x49, 0x89, 0xd0, 0x48, 0x89, 0xcf, 0xc6, 0x44, 0x24, 0x20,
        0x01, 0x48, 0x8d, 0x4d, 0xc0, 0x48, 0x89, 0xfa, 0xe8, 0xb3, 0x97, 0x04, 0x00, 0x48, 0x8b, 0x75,
        0xc8, 0x48, 0x83, 0xbf, 0x80, 0x03, 0x00, 0x00, 0x00, 0x0f, 0x84, 0x0e, 0x01, 0x00, 0x00, 0x48,
        0x8b, 0x5d, 0xd0, 0x48, 0x8d, 0x8f, 0x88, 0x03, 0x00, 0x00, 0x48, 0x89, 0xf2, 0x49, 0x89, 0xd8,
        0xe8, 0x6b, 0x57, 0xf0, 0xff, 0x48, 0x89, 0xc1, 0x48, 0xc1, 0xe9, 0x39, 0x4c, 0x8b, 0xb7, 0x68,
    ]),
    // the battlefield body draw
    (0x2466400, &[
        0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53, 0x48, 0x81, 0xec, 0x88,
        0x06, 0x00, 0x00, 0x48, 0x8d, 0xac, 0x24, 0x80,
    ]),
    // the draw commands' grow_one (new capacity max(4, 2 x cap), 0xd0 bytes, align 8)
    (0x3e65ef0, &[
        0x56, 0x57, 0x48, 0x83, 0xec, 0x48, 0x48, 0x89, 0xce, 0x48, 0x8b, 0x11, 0x48, 0x8d, 0x04, 0x12,
        0x48, 0x83, 0xf8, 0x05, 0xbf, 0x04, 0x00, 0x00, 0x00, 0x48, 0x0f, 0x43, 0xf8, 0x4c, 0x8b, 0x41,
        0x08, 0x48, 0xc7, 0x44, 0x24, 0x28, 0xd0, 0x00, 0x00, 0x00, 0x48, 0xc7, 0x44, 0x24, 0x20, 0x08,
    ]),
    // the view node draw
    (0x245f150, &[
        0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x53, 0x48, 0x81, 0xec, 0x58,
        0x03, 0x00, 0x00, 0x48, 0x8d, 0xac, 0x24, 0x80,
    ]),
    // the entity render's call of the body draw, its read of the scale (+0x1b4 round the body draw's commands)
    // and the tags of the scale / restore commands it wraps them in
    (0x2f272c1, &[0xe8, 0x3a, 0xf1, 0x53, 0xff]),
    (0x2f273a0, &[0xf3, 0x41, 0x0f, 0x10, 0x8c, 0x24, 0xb4, 0x01, 0x00, 0x00]),
    (0x2f2742a, &[0x48, 0xb8, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80]),
    (0x2f2748b, &[0x48, 0xb8, 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80]),
    // the UI's calls of the anim lookup (encyclopedia, pick slot, BP grid, pick moment, scoreboard portraits) and
    // their size asks
    (0x2f5a51c, &[0xe8, 0x2f, 0x7a, 0x30, 0xfd]), // encyclopedia / face icons
    (0x2f5a6e0, &[0xff, 0xd3]), (0x2f5a736, &[0x41, 0xff, 0xd7]), (0x2f5a74d, &[0xff, 0xd3]),
    (0x2f5a761, &[0x41, 0xff, 0xd7]),
    (0x2f55705, &[0xe8, 0x46, 0xc8, 0x30, 0xfd]), // pick slot
    (0x2f55950, &[0xff, 0xd7]), (0x2f55965, &[0x41, 0xff, 0xd6]), (0x2f55977, &[0xff, 0xd7]),
    (0x2f55988, &[0x41, 0xff, 0xd6]),
    (0x2431604, &[0xe8, 0x47, 0x09, 0xe3, 0xfd]), // BP grid
    (0x2431940, &[0xff, 0xd7]), (0x2431953, &[0x41, 0xff, 0xd6]), (0x2431963, &[0xff, 0xd7]),
    (0x2431973, &[0x41, 0xff, 0xd6]),
    (0x2f6c298, &[0xe8, 0xb3, 0x5c, 0x2f, 0xfd]), // pick moment
    (0x2f6c635, &[0x41, 0xff, 0xd6]), (0x2f6c643, &[0x41, 0xff, 0xd7]), (0x2f6c64d, &[0x41, 0xff, 0xd6]),
    (0x2f6c658, &[0x41, 0xff, 0xd7]),
    (0x2f2ab4e, &[0xe8, 0xfd, 0x73, 0x33, 0xfd]), // scoreboard portraits
    (0x2f2ad8c, &[0x41, 0xff, 0xd6]), (0x2f2adab, &[0x41, 0xff, 0xd7]), (0x2f2adc6, &[0x41, 0xff, 0xd6]),
    (0x2f2addb, &[0x41, 0xff, 0xd7]),
    // the same drawers' own calls of the sheet lookup (src/ui.rs)
    (0x2f5a539, &[0xe8, 0x22, 0xeb, 0x1f, 0xfd]), (0x2f55722, &[0xe8, 0x39, 0x39, 0x20, 0xfd]),
    (0x243191e, &[0xe8, 0x3d, 0x77, 0xd2, 0xfd]), (0x2f6c3f5, &[0xe8, 0x66, 0xcc, 0x1e, 0xfd]),
    (0x2f2abd4, &[0xe8, 0x87, 0xe4, 0x22, 0xfd]),
    // the draw command made from a sheet's name (src/ui.rs hooks its prologue)
    (0x1c97d0, &[
        0x55, 0x41, 0x57, 0x41, 0x56, 0x56, 0x57, 0x53, 0x48, 0x81, 0xec, 0xc8, 0x00, 0x00, 0x00, 0x48,
        0x8d, 0xac, 0x24, 0x80, 0x00, 0x00, 0x00, 0x44, 0x0f, 0x29, 0x6d, 0x30, 0x44, 0x0f, 0x29, 0x65,
        0x20, 0x44, 0x0f, 0x29, 0x5d, 0x10, 0x44, 0x0f, 0x29, 0x55, 0x00, 0x44, 0x0f, 0x29, 0x4d, 0xf0,
    ]),
    // the image node's setter (src/ui.rs hooks its prologue)
    (0x2beb0c0, &[
        0x41, 0x57, 0x41, 0x56, 0x41, 0x54, 0x56, 0x57, 0x53, 0x48, 0x83, 0xec, 0x28, 0x4c, 0x89, 0xc7,
        0x48, 0x89, 0xcb, 0x4c, 0x8b, 0x72, 0x08, 0x48, 0x8b, 0x72, 0x10, 0x48, 0x85, 0xf6, 0x0f, 0x84,
        0xe0, 0x01, 0x00, 0x00, 0x31, 0xd2, 0x49, 0x89, 0xf0, 0xe8, 0xa2, 0x40, 0x98, 0x00, 0x48, 0x85,
    ]),
    // the anim tables' hash
    (0x5e840, &[
        0x56, 0x48, 0x81, 0xec, 0x80, 0x00, 0x00, 0x00, 0xf3, 0x0f, 0x6f, 0x01, 0x66, 0x0f, 0x70, 0xc8,
        0x44, 0x66, 0x0f, 0xef, 0x0d, 0x07, 0x28, 0xea, 0x03, 0x66, 0x0f, 0x7f, 0x4c, 0x24, 0x30, 0x66,
        0x0f, 0x70, 0xc8, 0xee, 0x66, 0x0f, 0xef, 0x0d, 0x04, 0x28, 0xea, 0x03, 0x66, 0x0f, 0x7f, 0x4c,
    ]),
    // the display-update handler
    (0x309ad00, &[
        0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x55, 0x53, 0x48, 0x81, 0xec, 0x88,
        0x00, 0x00, 0x00, 0x66, 0x0f, 0x7f, 0x7c, 0x24, 0x70, 0x0f, 0x29, 0x74, 0x24, 0x60, 0x48, 0x8b,
        0x59, 0x18, 0x48, 0x85, 0xdb, 0x0f, 0x84, 0x20, 0x05, 0x00, 0x00, 0x4c, 0x8b, 0x29, 0x66, 0x41,
    ]),
    // the battlefield frame lookup's call of the anim lookup, and its size asks (width, height)
    (0x250f78b, &[0xe8, 0xc0, 0x27, 0xd5, 0xfd]),
    (0x250f9dc, &[0xff, 0x53, 0x28]),
    (0x250f9e5, &[0xff, 0x53, 0x30]),
    // the body draw's size asks
    (0x2467119, &[0xff, 0xd7]), (0x2467138, &[0x41, 0xff, 0xd7]), (0x246714c, &[0xff, 0xd7]),
    (0x246715a, &[0x41, 0xff, 0xd7]),
    ],
}];

impl Build {
    /// The BP grid's call of the anim lookup and its four size asks (the third of the UI drawers: encyclopedia, pick
    /// slot, BP grid, pick moment, scoreboard): it draws the battlefield's hd_ frames, not the UI's lo_ ones (the user,
    /// 2026-10-21: 「BP 格子也改成显示战场那套 hd_ 高清帧」).
    pub fn bp_grid(&self) -> (usize, &[usize]) {
        (self.ui_anim_ret[2], &self.ui_size_ret[8..12])
    }
}

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
        ui_sheet_ret: keep(p.ui_sheet_ret),
        cmd_by_name: p.cmd_by_name,
        node_image: p.node_image,
        body_draw: p.body_draw,
        cmd_grow: p.cmd_grow,
        effect_draw: p.effect_draw,
        cmd_scale: p.cmd_scale,
        cmd_restore: p.cmd_restore,
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
        assert_eq!(p.ui_sheet_ret, b.ui_sheet_ret);
        assert_eq!((p.cmd_by_name, p.node_image), (b.cmd_by_name, b.node_image));
        assert_eq!((p.effect_draw, p.cmd_scale, p.cmd_restore), (b.effect_draw, b.cmd_scale, b.cmd_restore));
    }

    #[test]
    fn each_ui_drawer_asks_for_its_sheet_between_its_anim_lookup_and_its_size_asks() {
        for b in BUILDS {
            assert_eq!(b.ui_sheet_ret.len(), b.ui_anim_ret.len(), "{}", b.name);
            for (k, r) in b.ui_sheet_ret.iter().enumerate() {
                assert!(b.ui_anim_ret[k] < *r && *r < b.ui_size_ret[4 * k], "{}: drawer {k}", b.name);
                let call = b.sigs.iter().find(|s| s.0 == r - 5).expect("its call is checked").1;
                let target = (r - 5) as i64 + 5 + i32::from_le_bytes(call[1..5].try_into().unwrap()) as i64;
                assert_eq!(target as usize, b.sheet, "{}: drawer {k}", b.name);
            }
        }
    }

    #[test]
    fn the_bp_grid_is_the_third_ui_drawer() {
        for b in BUILDS {
            let (call, asks) = b.bp_grid();
            // a whole-body drawer, its four asks right after its call
            assert!(b.ui_sized_anim_ret.contains(&call) && asks.len() == 4, "{}", b.name);
            assert!(asks.iter().all(|r| b.ui_sized_size_ret.contains(r) && *r > call && *r - call < 0x1000));
        }
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
        for rva in [b.anim, b.sheet, b.hash, b.display_fn, b.body_draw, b.cmd_grow, b.cmd_by_name, b.node_image,
                    b.effect_draw] {
            assert!(rva == 0 || b.sigs.iter().any(|s| s.0 == rva), "{rva:#x} unchecked");
        }
    }

    /// The scale / restore tags are the entity render's own: a `movabs rax, tag` of each is among the fingerprints.
    #[test]
    fn the_command_tags_are_the_entity_renders() {
        for b in BUILDS {
            assert_eq!(b.cmd_restore, b.cmd_scale + 1, "{}", b.name);
            for tag in [b.cmd_scale, b.cmd_restore] {
                let mut movabs = vec![0x48, 0xb8];
                movabs.extend_from_slice(&tag.to_le_bytes());
                assert!(b.sigs.iter().any(|s| s.1 == &movabs[..]), "{}: {tag:#x} not checked", b.name);
            }
        }
    }
}
