//! Which heroes have dense (PPU) frames - the parts that need no game.
//!
//! A hero listed in a pack's table (`HEROES` in league_main/src/hd.rs and tft/src/hd.rs, handed over as a [`Table`])
//! carries `hd_<tag>` beside every `<tag>` in its own sheet (tools/art/ppu_hd.py, the same PPU there), each frame PPU
//! times the 1x frame's size - a drawn one may be grown alike at both ends (its centre, the pivot, kept), hd_idle exactly
//! PPU times as wide (src/lookup.rs tells a changed table by it). src/lookup.rs hands every reader of the hero's
//! animations a table whose every tag holds the dense frames with their rects divided by PPU, and every reader of its
//! sheet a texture that reports its size divided by PPU: the same UVs (the dense squares), the 1x sizes. The tags are
//! read from the sheet's .fanim each pack's DLL compiles in.
//!
//! The registered heroes are one [`Heroes`] snapshot a process ([`heroes`]): the host's own table first, then each
//! guest's as it comes in (src/share.rs). The hooks read it without a lock; a registration builds a new snapshot and
//! leaves the old one allocated (a handful of registrations at startup), so a hero registered after a lookup is found
//! by the next one.

use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, AtomicPtr, Ordering};
use std::sync::{LazyLock, Mutex};

/// Game pixels from a frame's centre (the unit's position) down to its soles (tools/art/ppu_rig.py FEET).
pub const FEET: f32 = 11.5;

/// The body's growth for `stacks` stacks of a growth row (1.0 for none): `per` a stack for the first `GROW_KNEE`, then
/// `GROW_TAIL` of it a stack, with no cap (the user 2026-10-31, 「大虫子体型应该可以无限变大吧」; 2026-11-03, 「大虫子在局内后期
/// 变的有点太大了 稍微可以缩小一点」 - the watched game's 9 bites drew Cho'Gath 3.7x, now 2.95x; one to four bites unchanged).
/// Both packs' DLLs carry this engine and the host's draws: league.dll's in the user's game (it loads first).
pub const GROW_KNEE: usize = 4;
pub const GROW_TAIL: f32 = 0.5;

pub fn grown(per: f32, stacks: usize) -> f32 {
    let early = stacks.min(GROW_KNEE) as f32;
    let late = stacks.saturating_sub(GROW_KNEE) as f32;
    1.0 + per * (early + GROW_TAIL * late)
}

/// A growth row's stacks from the names of the buffs on a hero's display entity. The game's display world keeps one
/// entry a name (it adds a name only when it has none of it), so any number of `buff` stacks shows as one; the add-on
/// (league_chogath) marks the 2nd, 3rd ... stack with `buff_2`, `buff_3` ...: the stacks are the highest mark seen with
/// a `buff` on him, or the `buff` entries if a display ever keeps them all (2026-11-02: league.log never drew a 2nd
/// bite, two minutes on screen with 2 stacks).
pub fn grow_count<'a>(names: impl IntoIterator<Item = &'a str>, buff: &str) -> usize {
    let (mut plain, mut mark) = (0, 0);
    for n in names {
        if n == buff {
            plain += 1;
        } else if let Some(k) = n.strip_prefix(buff).and_then(|r| r.strip_prefix('_')).and_then(|k| k.parse::<usize>().ok()) {
            mark = mark.max(k);
        }
    }
    if plain == 0 { 0 } else { plain.max(mark) }
}

/// Seconds a form's body ([`Table::forms`]) may go undrawn and still ease on: past it the next draw is another unit at
/// that address or a new match, drawn straight at its size.
pub const FORM_STALE: f32 = 0.5;

/// A form row's id that stands for any unit ([`Table::forms`]): whoever carries one of the row's buffs is drawn bigger,
/// dense frames or 1x - Lulu's Wild Growth grows the ally it lands on, any hero of any pack or the base game (league.dll
/// 2026-11-14). In the table's text it is the row's id like any other (`form * 1.15 0.5 league_lulu_r_on`): the
/// grammar and [`crate::PROTOCOL`] are unchanged, a table without such a row is the same text as before, and an
/// engine from before reads the row and leaves it out the way it leaves out a row of an id it does not register
/// ([`Heroes::and`] kept a form row only for an id the table brought) - its guest is not refused, Lulu's ally is only
/// not grown there.
pub const ANY: &str = "*";

/// The seconds of one frame: a wildcard form's first step ([`eased_any`]).
pub const FRAME: f32 = 1.0 / 60.0;

/// [`eased`] for a wildcard form row ([`ANY`]). The engine keeps no record of a unit no such row has grown yet, so a
/// unit first seen with the buff (`prev` None, `on`) grows from its plain size, one frame (`first` seconds) in, instead
/// of jumping to the row's size; a stale record (a unit back on screen, or another at that address) jumps like a hero's
/// own form; with no record and no buff it is 1.0.
pub fn eased_any(prev: Option<(f32, f32)>, on: bool, size: f32, secs: f32, first: f32) -> f32 {
    let target = if on { size } else { 1.0 };
    match prev {
        None if on => eased(Some((1.0, first)), target, size, secs),
        _ => eased(prev, target, size, secs),
    }
}

/// The size a body is drawn at from its own growth or form row (`own`: [`grown`] / [`eased`], None for a hero with no
/// such row) and a wildcard form row (`any`: [`eased_any`], None when none is on him or easing back): the larger, never
/// the two multiplied - a hero that grows by himself (Volibear's storm form, Bel'Veth's true form, Cho'Gath's Feast)
/// is not grown twice over by Lulu's Wild Growth (the user's limits: Volibear's x1.35 was 「实在太大了」, x1.15 kept).
/// None: nothing grows this body.
pub fn form_size(own: Option<f32>, any: Option<f32>) -> Option<f32> {
    match (own, any) {
        (None, None) => None,
        (a, b) => Some(a.unwrap_or(1.0).max(b.unwrap_or(1.0))),
    }
}

/// The size a form's body is drawn at now: `prev` the size it was drawn at last and the seconds since (None: never
/// drawn), `target` the row's size while a buff is on him, else 1.0. It moves toward the target by (size - 1) / secs a
/// second (the whole way in `secs`), straight to it when never drawn or stale.
pub fn eased(prev: Option<(f32, f32)>, target: f32, size: f32, secs: f32) -> f32 {
    match prev {
        Some((was, dt)) if dt <= FORM_STALE && secs > 0.0 => {
            let step = (size - 1.0).abs() / secs * dt;
            if (target - was).abs() <= step {
                target
            } else {
                was + step * (target - was).signum()
            }
        }
        _ => target,
    }
}

pub const PREFIX: &str = "hd_";

/// `lo_<tag>`: the same frames at [`UI_PPU`] squares a displayed game pixel (tools/art/ppu_hd.py add_lo) - what the BP
/// grid, the encyclopedia, the pick slots and the pick moment draw (src/lookup.rs ui_table; the user, 2026-10-13:
/// 「BP界面里看英雄还是太清晰」, picked the 1.5 row of the preview). The battlefield keeps the hd_ frames.
pub const LO_PREFIX: &str = "lo_";
pub const UI_PPU: f32 = 1.5;

/// `bp`: the hero's ban/pick reel (tools/art/hero_reels.py) - its idle loop with its actions and idle snippets in
/// between, cut from the frames its sheet holds. The BP grid plays it where it asks for the idle (src/lookup.rs
/// ui_table / reel_table; the user, 2026-10-22: 「BP页面的动图可以随便切动画帧里面的动作来做吧 包括待机的时候」).
pub const REEL: &str = "bp";

/// One pack's dense-frame rows as its DLL lists them (league_main/src/hd.rs, tft/src/hd.rs): what [`crate::start`]
/// takes and what a guest hands the host as text (src/share.rs). Every id is the pack's (`<pack>_...`).
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Table<'a> {
    /// the pack's mod id (league, tft): its ids start with `<pack>_`, its UI sheets are `asset/<pack>/ui_sheets/...`
    /// (src/ui.rs)
    pub pack: &'a str,
    /// champion id, pixels per 1x square, the sheet's .fanim (as shipped in the pack)
    pub heroes: Vec<(&'a str, f32, &'a str)>,
    /// champion id, its size everywhere the dense frames are drawn (1.0 = the 1x frames' size, the size when not
    /// listed): the anim tables' rects and the texture's reported size are divided by PPU / size, the battlefield
    /// scale is the game's / PPU x size
    pub sizes: Vec<(&'a str, f32)>,
    /// heroes whose body grows with a stack: (id, the buff whose instances on him are the stacks, growth a stack), the
    /// body drawn that much bigger about his soles, with no cap (src/view.rs)
    pub growth: Vec<(&'a str, &'a str, f32)>,
    /// heroes drawn bigger while a buff of theirs is on them: (id, the buffs - any one of them, the size, seconds to
    /// grow to it and to shrink back), about the soles like growth, eased in and out ([`eased`], src/view.rs). A row of
    /// id [`ANY`] grows any unit carrying one of its buffs, whoever's it is (the buffs are the pack's own)
    pub forms: Vec<(&'a str, Vec<&'a str>, f32, f32)>,
    /// effect sheets drawn dense like a hero's sheet (id, PPU, .fanim: `idle` / `hd_idle` and any more tags, each with
    /// its hd_ twin): looked up like the heroes, no entity's body
    pub effects: Vec<(&'a str, f32, &'a str)>,
    /// effects whose pictures the view node draw (src/view.rs effect_detour) shrinks to 1 / PPU about their top-left
    /// corner - a kit's view effects, at a point or following a unit (the body draw calls the node draw; cmd_kind keeps
    /// the shrink inside a dense hero's extras); a buff's view never passes there. Every other effect is drawn a square a
    /// game pixel
    pub drawn_effects: Vec<&'a str>,
    /// tall heroes drawn smaller wherever the UI draws lo_ frames (the ban/pick card above all): id, size
    pub ui_sizes: Vec<(&'a str, f32)>,
    /// drawn effects (in [`Table::drawn_effects`]) some of whose pictures are a kit's projectiles or buffs (2026-11-09,
    /// the effects PPU: a hero's whole effect sheets dense). Only this engine shrinks those - a buff's in the body draw,
    /// a projectile's in its own render (src/view.rs) - so they are dense only in the DLL that hooks the game with both
    /// in ([`full_on`]): never handed to another DLL's engine (src/share.rs leaves them out of the text, so the protocol
    /// is unchanged and an older host draws them at 1x), and at 1x where the projectile renders were not found.
    pub full_effects: Vec<&'a str>,
}

static FULL_ON: AtomicBool = AtomicBool::new(false);

/// Whether this process's engine shrinks projectile and buff pictures too (src/view.rs sets it once its hooks went in):
/// until then the [`Table::full_effects`] are not looked up as dense.
pub fn full_on() -> bool {
    FULL_ON.load(Ordering::Acquire)
}

pub(crate) fn set_full_on(on: bool) {
    FULL_ON.store(on, Ordering::Release);
}

/// The `"lo_..."` animation names of a .fanim.
pub fn lo_tags(fanim: &str) -> Vec<String> {
    keys_with(fanim, LO_PREFIX)
}

/// The `"hd_..."` animation names of a .fanim (its keys under "anims"; no frame key starts with hd_).
pub fn hd_tags(fanim: &str) -> Vec<String> {
    keys_with(fanim, PREFIX)
}

/// The quoted keys of a .fanim (`"name":`) that start with `prefix`, each once, in order.
pub fn keys_with(fanim: &str, prefix: &str) -> Vec<String> {
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
#[derive(Clone, Debug)]
pub struct Hero {
    pub id: &'static str,
    pub ppu: f32,
    /// the size it is shown at ([`Table::sizes`]; 1.0 when not listed)
    pub size: f32,
    pub tags: Vec<String>,
    /// the sheet has lo_ frames for every tag (the UI draws those)
    pub lo: bool,
    /// what the whole-body UI (the pick slot, the BP grid, the pick moment) divides a lo_ frame's pixels by:
    /// [`UI_PPU`] / its [`Table::ui_sizes`] size; the encyclopedia / face icons and the scoreboard divide by [`UI_PPU`]
    /// ([`Hero::ui_for`])
    pub ui: f32,
}

impl Hero {
    /// What a dense frame's pixels are divided by to give its shown size: PPU / size.
    pub fn shown(&self) -> f32 {
        self.ppu / self.size
    }

    /// What the BP grid divides an hd_ frame's pixels by: PPU / its [`Table::ui_sizes`] size - the battlefield's frames
    /// at the size the whole-body UI draws the hero (2026-10-21: 「BP 格子也改成显示战场那套 hd_ 高清帧」).
    pub fn bp_hd(&self) -> f32 {
        self.ppu * self.ui / UI_PPU
    }

    /// The UI's divisor for a caller: `sized` (a whole-body drawer, src/build.rs ui_sized_*) takes the UI_SIZES size,
    /// the face crops (encyclopedia / face icons, scoreboard portraits) the plain [`UI_PPU`] - their face point is
    /// measured on the hero at that size (2026-10-20: Galio's and Mordekaiser's icons showed a crown / a belly).
    pub fn ui_for(&self, sized: bool) -> f32 {
        if sized { self.ui } else { UI_PPU }
    }
}

/// A name kept for the process: a snapshot's heroes outlive the table (a guest's text) they came from.
fn keep(s: &str) -> &'static str {
    Box::leak(s.to_owned().into_boxed_str())
}

impl Table<'_> {
    /// Its heroes then its effects, as registered heroes (the sizes and UI sizes are the table's own).
    pub fn to_heroes(&self) -> Vec<Hero> {
        self.heroes
            .iter()
            .chain(self.effects.iter())
            .map(|&(id, ppu, fanim)| Hero {
                id: keep(id),
                ppu,
                size: self.sizes.iter().find(|s| s.0 == id).map_or(1.0, |s| s.1),
                tags: hd_tags(fanim).into_iter().map(|t| t[PREFIX.len()..].to_string()).collect(),
                lo: !lo_tags(fanim).is_empty(),
                ui: UI_PPU / self.ui_sizes.iter().find(|s| s.0 == id).map_or(1.0, |s| s.1),
            })
            .collect()
    }
}

/// The registered heroes, found by id with one hash lookup. The hooks ask for every resource the game looks up by name
/// and every entity on the battlefield each frame; a walk down the list compared up to 55 names, twice for each lookup
/// (2026-10-19 profile: league.dll's own time on the render thread was mostly that walk).
#[derive(Default)]
pub struct Heroes {
    pub list: Vec<Hero>,
    by_id: HashMap<&'static str, usize>,
    /// the registered packs (league, tft), in order: their heroes have UI sheets (src/ui.rs)
    pub packs: Vec<&'static str>,
    /// `<pack>_` of each: every registered id starts with one of them
    prefixes: Vec<String>,
    /// every table's growth rows ([`Table::growth`])
    pub growth: Vec<(&'static str, &'static str, f32)>,
    /// every table's form rows ([`Table::forms`]), the wildcard ones ([`ANY`]) too
    pub forms: Vec<(&'static str, &'static [&'static str], f32, f32)>,
    /// every table's drawn effects ([`Table::drawn_effects`])
    pub drawn_effects: Vec<&'static str>,
    /// the host's own table's full effects ([`Table::full_effects`]; a guest's text never carries any)
    pub full_effects: Vec<&'static str>,
}

impl Heroes {
    /// The heroes of `tables`, in order (tests and checks; the game's go through [`Registry`]).
    pub fn of(tables: &[&Table<'_>]) -> Self {
        tables.iter().fold(Heroes::default(), |h, t| h.and(t).0)
    }

    /// These heroes and table `t`'s -> them and the ids `t` brought. An id registered already keeps its first row (the
    /// host's own, the first guest's): `t`'s row of it is left out, with its growth, form and drawn-effect rows. A
    /// wildcard form row ([`ANY`]) is no id's: it comes in unless a table before brought one of the same buffs.
    pub fn and(&self, t: &Table<'_>) -> (Self, Vec<&'static str>) {
        let mut list = self.list.clone();
        let mut by_id = self.by_id.clone();
        let mut came = Vec::new();
        for h in t.to_heroes() {
            if by_id.contains_key(h.id) {
                continue;
            }
            by_id.insert(h.id, list.len());
            came.push(h.id);
            list.push(h);
        }
        let mut packs = self.packs.clone();
        if !t.pack.is_empty() && !packs.contains(&t.pack) {
            packs.push(keep(t.pack));
        }
        let prefixes = packs.iter().map(|p| format!("{p}_")).collect();
        let mut growth = self.growth.clone();
        growth.extend(t.growth.iter().filter(|g| came.contains(&g.0)).map(|&(id, buff, per)| (keep(id), keep(buff), per)));
        let mut forms = self.forms.clone();
        for (id, buffs, size, secs) in &t.forms {
            let any = *id == ANY;
            if !(any || came.contains(id)) {
                continue;
            }
            if any && forms.iter().any(|f| f.0 == ANY && f.1.iter().eq(buffs.iter())) {
                continue; // a wildcard row another table brought already
            }
            let buffs: &'static [&'static str] =
                Box::leak(buffs.iter().map(|b| keep(b)).collect::<Vec<_>>().into_boxed_slice());
            forms.push((if any { ANY } else { keep(id) }, buffs, *size, *secs));
        }
        let mut drawn_effects = self.drawn_effects.clone();
        drawn_effects.extend(t.drawn_effects.iter().filter(|id| came.contains(id)).map(|id| keep(id)));
        let mut full_effects = self.full_effects.clone();
        full_effects.extend(t.full_effects.iter().filter(|id| came.contains(id)).map(|id| keep(id)));
        (Heroes { list, by_id, packs, prefixes, growth, forms, drawn_effects, full_effects }, came)
    }

    /// The hero a resource name is of, as the lookups take it: a full effect ([`Table::full_effects`]) only once this
    /// engine shrinks projectile and buff pictures too ([`full_on`]) - else it is drawn at 1x, as if not registered.
    pub fn dense_of_name(&self, name: &str) -> Option<&Hero> {
        self.dense_of_name_if(name, full_on())
    }

    /// [`Heroes::dense_of_name`] with the full effects dense or not (`on`).
    pub fn dense_of_name_if(&self, name: &str, on: bool) -> Option<&Hero> {
        self.of_name(name).filter(|h| on || !self.full_effects.contains(&h.id))
    }

    /// The wildcard form rows ([`ANY`]): any unit carrying one of a row's buffs is drawn bigger (src/view.rs).
    pub fn any_forms(&self) -> impl Iterator<Item = &(&'static str, &'static [&'static str], f32, f32)> {
        self.forms.iter().filter(|f| f.0 == ANY)
    }

    pub fn get(&self, id: &str) -> Option<&Hero> {
        // every registered id starts with its pack's `<pack>_` (league_, tft_): the base heroes, effects and UI names
        // go without hashing
        if !self.prefixes.iter().any(|p| id.starts_with(p.as_str())) {
            return None;
        }
        self.by_id.get(id).map(|&k| &self.list[k])
    }

    /// The hero a resource name is of: `.../league_yasuo#anim` (or the bare id) -> league_yasuo.
    pub fn of_name(&self, name: &str) -> Option<&Hero> {
        self.get(name.rsplit('/').next()?.split('#').next()?)
    }
}

/// The process's registered heroes: one immutable [`Heroes`] snapshot, replaced whole on each registration.
pub struct Registry {
    snap: AtomicPtr<Heroes>,
    adding: Mutex<()>,
}

static NONE: LazyLock<Heroes> = LazyLock::new(Heroes::default);

impl Registry {
    pub const fn new() -> Self {
        Registry { snap: AtomicPtr::new(std::ptr::null_mut()), adding: Mutex::new(()) }
    }

    /// The snapshot now (no lock: the hooks' hot path).
    pub fn heroes(&self) -> &'static Heroes {
        let p = self.snap.load(Ordering::Acquire);
        if p.is_null() {
            &NONE
        } else {
            // SAFETY: a published snapshot is never freed, so a reader's reference outlives every later swap
            unsafe { &*p }
        }
    }

    /// Table `t` registered -> the ids it brought ([`Heroes::and`]). The new snapshot is published whole; the old one
    /// stays allocated for whoever still reads it (leaked: a handful of registrations a process).
    pub fn add(&self, t: &Table<'_>) -> Vec<&'static str> {
        let _one_at_a_time = self.adding.lock().unwrap_or_else(|e| e.into_inner());
        let (next, came) = self.heroes().and(t);
        self.snap.store(Box::into_raw(Box::new(next)), Ordering::Release);
        came
    }
}

impl Default for Registry {
    fn default() -> Self {
        Self::new()
    }
}

/// This process's registry: the host's hooks read it, its door (src/share.rs) adds the guests' tables to it.
pub static REGISTRY: Registry = Registry::new();

/// The heroes registered in this process so far.
pub fn heroes() -> &'static Heroes {
    REGISTRY.heroes()
}

/// The data checks every pack's table must pass (each DLL's tests: league_main/src/hd.rs, tft/src/hd.rs). Each panics
/// at the first row that fails.
pub mod checks {
    use super::*;

    /// The first frame's width of tag `t` in a .fanim (`"t": {"frames": [{... "w": <here>`).
    fn first_w(fanim: &str, t: &str) -> Option<f32> {
        let at = fanim.find(&format!("\"{t}\""))?;
        let w = at + fanim[at..].find("\"w\"")?;
        let num = fanim[w + 3..].trim_start().strip_prefix(':')?.trim_start();
        num[..num.find(|c: char| !(c.is_ascii_digit() || c == '.'))?].parse().ok()
    }

    /// Every hero and effect is the pack's and listed once (a second row of an id would never be registered:
    /// [`Heroes::and`]); every other row is about one of them (a growth or form row of another id is dropped there
    /// without a word) but a wildcard form row ([`ANY`]), whose buffs are the pack's own (`<pack>_...`: no other pack's
    /// table grows units by them), each in one such row; a form row names at least one buff, each one word (the table's
    /// text: src/share.rs).
    pub fn ids_are_the_packs_once(t: &Table<'_>) {
        let mut seen = Vec::new();
        for &(id, ..) in t.heroes.iter().chain(t.effects.iter()) {
            assert!(id.starts_with(&format!("{}_", t.pack)), "{id}: not a {} id", t.pack);
            assert!(!id.contains(char::is_whitespace), "{id:?}");
            assert!(!seen.contains(&id), "{id}: listed twice");
            seen.push(id);
        }
        let others = t.sizes.iter().map(|s| s.0).chain(t.ui_sizes.iter().map(|s| s.0)).chain(t.growth.iter().map(|g| g.0));
        let others = others.chain(t.forms.iter().map(|f| f.0).filter(|id| *id != ANY));
        for id in others.chain(t.drawn_effects.iter().copied()) {
            assert!(seen.contains(&id), "{id}: a row for an id the table does not register");
        }
        // a full effect is an effect sheet the node draw shrinks too (its view effects)
        for id in &t.full_effects {
            assert!(t.effects.iter().any(|e| e.0 == *id), "{id}: a full effect that is no effect sheet");
            assert!(t.drawn_effects.contains(id), "{id}: a full effect not in the drawn effects");
        }
        let mut wild: Vec<&str> = Vec::new();
        for (id, buffs, size, secs) in &t.forms {
            assert!(!buffs.is_empty(), "{id}: a form row with no buff");
            assert!(buffs.iter().all(|b| !b.is_empty() && !b.contains(char::is_whitespace)), "{id}: {buffs:?}");
            if *id == ANY {
                assert!(buffs.iter().all(|b| b.starts_with(&format!("{}_", t.pack))), "a wildcard form row of buffs not \
                         the {} pack's: {buffs:?}", t.pack);
                assert!(buffs.iter().all(|b| !wild.contains(b)), "{buffs:?}: a buff in two wildcard form rows");
                assert!(*size > 1.0 && *secs > 0.0, "a wildcard form row x{size} over {secs} s");
                wild.extend(buffs.iter().copied());
            }
        }
    }

    /// src/lookup.rs takes a table only when hd_idle is PPU times as wide as idle (within half a square), else it
    /// leaves it alone and the texture's size, divided all the same, cuts the wrong part of the sheet: Daisy at PPU
    /// 1.333 on her 2.533 sheets drew nothing (the user, 2026-10-27: 「你改了小菊后 我怎么在游戏里看不到了」).
    pub fn every_registered_sheet_is_ppu_times_as_wide(t: &Table<'_>) {
        for &(id, ppu, fanim) in t.heroes.iter().chain(t.effects.iter()) {
            let (Some(wi), Some(wh)) = (first_w(fanim, "idle"), first_w(fanim, "hd_idle")) else {
                panic!("{id}: no idle / hd_idle frame");
            };
            assert!((wh - wi * ppu).abs() <= 0.5, "{id}: hd_idle {wh} wide, idle {wi}: not PPU {ppu} times");
        }
    }

    pub fn every_registered_sheet_has_hd_tags_for_all_its_tags(t: &Table<'_>) {
        for &(id, ppu, fanim) in &t.heroes {
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

    pub fn ui_sizes_shrink_heroes_with_lo_frames(t: &Table<'_>) {
        let h = Heroes::of(&[t]);
        for &(id, size) in &t.ui_sizes {
            let hero = h.get(id).unwrap_or_else(|| panic!("{id}: not a registered hero"));
            assert!(hero.lo, "{id}: no lo_ frames - the UI draws its 1x frames, a UI size would not reach them");
            assert!(size > 0.5 && size < 1.0, "{id}: {size}");
            assert!((hero.ui - UI_PPU / size).abs() < 1e-6);
        }
    }

    pub fn effect_sheets_have_a_dense_idle(t: &Table<'_>) {
        let h = Heroes::of(&[t]);
        for &(id, ppu, fanim) in &t.effects {
            assert!(ppu > 1.0);
            // src/lookup.rs densify_table: idle / hd_idle tell a dense table, every other tag needs its hd_ twin
            let hd = hd_tags(fanim);
            assert!(hd.contains(&format!("{PREFIX}idle")), "{id}: no hd_idle");
            assert!(fanim.contains("\"idle\""), "{id}: no idle");
            // the anims' names: every quoted key but the frame fields
            let fields = ["anims", "frames", "duration", "data", "x", "y", "w", "h"];
            for t in keys_with(fanim, "").into_iter().filter(|t| !fields.contains(&t.as_str())) {
                assert!(t.starts_with(PREFIX) || hd.contains(&format!("{PREFIX}{t}")), "{id}: {t} has no {PREFIX}{t}");
            }
            assert!(lo_tags(fanim).is_empty(), "{id}: no UI frames for an effect");
            assert_eq!(h.of_name(&format!("asset/{}/effects/{id}#anim", t.pack)).map(|x| x.id), Some(id));
            assert_eq!(h.get(id).map(|x| x.size), Some(1.0), "{id}: an effect is never resized");
        }
    }

    /// The table as a guest hands it to the host (src/share.rs) is read back the same - but for its full effects, which
    /// stay out of the text ([`Table::full_effects`]).
    pub fn the_table_goes_through_the_text_unchanged(t: &Table<'_>) {
        let text = t.to_text();
        let mut sent = t.clone();
        sent.effects.retain(|e| !t.full_effects.contains(&e.0));
        sent.drawn_effects.retain(|id| !t.full_effects.contains(id));
        sent.full_effects.clear();
        assert_eq!(Table::parse(&text).as_ref(), Ok(&sent));
        for id in &t.full_effects {
            assert!(!text.contains(&format!(" {id} ")) && !text.contains(&format!("drawn {id}\n")), "{id} in the text");
        }
    }
}

#[cfg(test)]
pub(crate) mod tests {
    use super::*;

    /// A .fanim with idle / hd_idle (PPU `ppu`) and, with `lo`, lo_idle - the least a dense sheet holds.
    pub(crate) fn fanim(ppu: f32, lo: bool) -> String {
        let f = |w: f32| format!(r#"{{"frames":[{{"duration":0.1,"data":{{"x":0.0,"y":0.0,"w":{w},"h":{w}}}}}]}}"#);
        let mut s = format!(r#"{{"anims":{{"idle":{},"hd_idle":{}"#, f(10.0), f(10.0 * ppu));
        if lo {
            s += &format!(r#","lo_idle":{}"#, f(15.0));
        }
        s + "}}"
    }

    /// Pack `pack`'s table of `heroes` (id, PPU), each sheet a [`fanim`] with lo_ frames.
    pub(crate) fn table(pack: &'static str, heroes: &[(&'static str, f32)]) -> Table<'static> {
        Table { pack, heroes: heroes.iter().map(|&(id, ppu)| (id, ppu, keep(&fanim(ppu, true)))).collect(), ..Table::default() }
    }

    /// A full effect is dense only once this engine shrinks buff and projectile pictures too; it never goes into the
    /// text a guest hands another DLL's engine, which then draws it at 1x (2026-11-09, the effects PPU pilot).
    #[test]
    fn full_effects_are_dense_only_where_their_pictures_are_all_shrunk() {
        let mut league = table("league", &[("league_yasuo", 2.2)]);
        league.effects.push(("league_akshan_fx", 2.0, keep(&fanim(2.0, false))));
        league.effects.push(("league_zoe_spells", 2.0, keep(&fanim(2.0, false))));
        league.drawn_effects.extend(["league_akshan_fx", "league_zoe_spells"]);
        league.full_effects.push("league_akshan_fx");
        checks::ids_are_the_packs_once(&league);
        let h = Heroes::of(&[&league]);
        assert_eq!(h.full_effects, vec!["league_akshan_fx"]);
        let name = "asset/league/effects/league_akshan_fx#anim";
        assert!(h.dense_of_name_if(name, false).is_none());
        assert_eq!(h.dense_of_name_if(name, true).map(|x| x.id), Some("league_akshan_fx"));
        // the other effects and the heroes as before
        assert!(h.dense_of_name_if("asset/league/effects/league_zoe_spells#sheet", false).is_some());
        assert!(h.dense_of_name_if("asset/league/champions/league_yasuo#anim", false).is_some());
        // a guest's text leaves it out (its effect row and its drawn row), the rest goes through
        checks::the_table_goes_through_the_text_unchanged(&league);
        let text = league.to_text();
        let sent = Table::parse(&text).unwrap();
        assert_eq!(sent.effects.iter().map(|e| e.0).collect::<Vec<_>>(), vec!["league_zoe_spells"]);
        assert_eq!(sent.drawn_effects, vec!["league_zoe_spells"]);
        assert!(Heroes::of(&[&sent]).get("league_akshan_fx").is_none());
    }

    #[test]
    fn heroes_are_found_by_id_and_resource_name() {
        let mut league = table("league", &[("league_yasuo", 2.2), ("league_gragas", 1.45)]);
        league.sizes.push(("league_gragas", 0.90));
        league.effects.push(("league_yuumi_ride", 1.5, keep(&fanim(1.5, false))));
        let mut tft = table("tft", &[("tft_powder", 1.75)]);
        tft.sizes.push(("tft_powder", 0.90));
        let h = Heroes::of(&[&league, &tft]);
        assert_eq!(h.list.len(), 4);
        for id in ["league_yasuo", "league_gragas", "league_yuumi_ride", "tft_powder"] {
            assert_eq!(h.get(id).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/league/champions/{id}#anim")).map(|x| x.id), Some(id));
            assert_eq!(h.of_name(&format!("asset/base/aseprite_resources/champions/{id}#sheet")).map(|x| x.id), Some(id));
        }
        assert_eq!(h.get("league_gragas").map(|x| (x.size, x.shown())), Some((0.90, 1.45 / 0.90)));
        assert_eq!(h.get("tft_powder").map(|x| (x.id, x.size)), Some(("tft_powder", 0.90)));
        assert!(h.get("league_amumu").is_none());
        assert!(h.get("tft_nobody").is_none());
        assert!(h.of_name("asset/base/aseprite_resources/champions/alchemist#anim").is_none());
        assert!(h.of_name("asset/league/champions/league_ashe_fx#sheet").is_none());
        assert!(h.of_name("").is_none());
        assert_eq!(h.packs, vec!["league", "tft"]);
        // one pack only: the other's ids are not even hashed
        let only = Heroes::of(&[&league]);
        assert!(only.get("tft_powder").is_none());
        assert_eq!(only.packs, vec!["league"]);
    }

    #[test]
    fn an_id_registered_already_keeps_its_first_row() {
        let first = table("league", &[("league_yasuo", 2.2)]);
        let again = table("league", &[("league_yasuo", 3.0), ("league_zeri", 3.0)]);
        let (h, came) = Heroes::of(&[&first]).and(&again);
        assert_eq!(came, vec!["league_zeri"]);
        assert_eq!(h.get("league_yasuo").map(|x| x.ppu), Some(2.2));
        assert_eq!(h.packs, vec!["league"]);
    }

    #[test]
    fn a_registration_is_seen_by_the_next_reader() {
        let reg = Registry::new();
        assert!(reg.heroes().list.is_empty() && reg.heroes().get("league_chogath").is_none());
        let before = reg.heroes();
        let mut league = table("league", &[("league_chogath", 2.0)]);
        league.growth.push(("league_chogath", "league_chogath_r_stack", 0.30));
        assert_eq!(reg.add(&league), vec!["league_chogath"]);
        // a reader holding the old snapshot keeps it; the next one sees the hero
        assert!(before.get("league_chogath").is_none());
        let now = reg.heroes();
        assert_eq!(now.get("league_chogath").map(|x| x.ppu), Some(2.0));
        assert_eq!(now.growth, vec![("league_chogath", "league_chogath_r_stack", 0.30)]);
        assert_eq!(reg.add(&table("tft", &[("tft_norra", 2.0)])), vec!["tft_norra"]);
        assert!(now.get("tft_norra").is_none());
        assert_eq!(reg.heroes().list.iter().map(|h| h.id).collect::<Vec<_>>(), vec!["league_chogath", "tft_norra"]);
    }

    #[test]
    fn the_checks_take_a_good_table_and_catch_a_bad_one() {
        let mut t = table("tft", &[("tft_alune", 2.0)]);
        t.ui_sizes.push(("tft_alune", 0.85));
        checks::ids_are_the_packs_once(&t);
        checks::every_registered_sheet_is_ppu_times_as_wide(&t);
        checks::ui_sizes_shrink_heroes_with_lo_frames(&t);
        checks::effect_sheets_have_a_dense_idle(&t);
        checks::the_table_goes_through_the_text_unchanged(&t);
        let mut thin = t.clone();
        thin.heroes[0].1 = 3.0; // hd_idle 20 wide: not 3 times idle's 10
        assert!(std::panic::catch_unwind(|| checks::every_registered_sheet_is_ppu_times_as_wide(&thin)).is_err());
        let other = table("tft", &[("league_ashe", 2.0)]);
        assert!(std::panic::catch_unwind(|| checks::ids_are_the_packs_once(&other)).is_err());
    }

    /// A wildcard form row ([`ANY`], Lulu's Wild Growth) is no hero's: it is registered whichever ids its table brought,
    /// once for the same buffs, and the checks take it only with the pack's own buffs.
    #[test]
    fn a_wildcard_form_row_grows_any_unit() {
        let mut league = table("league", &[("league_volibear", 1.2)]);
        league.forms.push(("league_volibear", vec!["league_volibear_r_form"], 1.15, 1.25));
        league.forms.push((ANY, vec!["league_lulu_r_on"], 1.15, 0.5));
        checks::ids_are_the_packs_once(&league);
        let h = Heroes::of(&[&league]);
        assert_eq!(h.forms.len(), 2);
        let any: Vec<_> = h.any_forms().collect();
        assert_eq!(any.len(), 1);
        assert_eq!((any[0].0, any[0].1, any[0].2, any[0].3), (ANY, &["league_lulu_r_on"][..], 1.15, 0.5));
        // no id is the wildcard: no hero is found by it, and a hero's own row is still found by his id
        assert!(h.get(ANY).is_none() && h.of_name("asset/league/champions/*#anim").is_none());
        assert_eq!(h.forms.iter().filter(|f| f.0 == "league_volibear").count(), 1);
        // a second table with the same wildcard row (or the same table again) adds nothing; another buff's row comes in
        let mut again = table("league", &[("league_yasuo", 2.2)]);
        again.forms.push((ANY, vec!["league_lulu_r_on"], 1.30, 2.0));
        let (h2, came) = h.and(&again);
        assert_eq!(came, vec!["league_yasuo"]);
        assert_eq!(h2.any_forms().map(|f| f.2).collect::<Vec<_>>(), vec![1.15], "the first row of those buffs stays");
        let mut tft = table("tft", &[("tft_norra", 2.0)]);
        tft.forms.push((ANY, vec!["tft_norra_big"], 1.1, 1.0));
        checks::ids_are_the_packs_once(&tft);
        assert_eq!(h2.and(&tft).0.any_forms().count(), 2);
        // the checks: another pack's buff, a buff in two wildcard rows, a row that does not grow
        let mut foreign = table("tft", &[("tft_norra", 2.0)]);
        foreign.forms.push((ANY, vec!["league_lulu_r_on"], 1.15, 0.5));
        assert!(std::panic::catch_unwind(|| checks::ids_are_the_packs_once(&foreign)).is_err());
        let mut twice = league.clone();
        twice.forms.push((ANY, vec!["league_x", "league_lulu_r_on"], 1.1, 0.5));
        assert!(std::panic::catch_unwind(|| checks::ids_are_the_packs_once(&twice)).is_err());
        let mut flat = table("league", &[("league_yasuo", 2.2)]);
        flat.forms.push((ANY, vec!["league_lulu_r_on"], 1.0, 0.5));
        assert!(std::panic::catch_unwind(|| checks::ids_are_the_packs_once(&flat)).is_err());
    }

    /// A unit first seen under a wildcard row's buff grows from its plain size (no record of it yet: not a jump to the
    /// size), eases back after it, and is drawn at the larger of its own growth and the wildcard's, never their product.
    #[test]
    fn a_wildcard_form_eases_from_the_units_own_size() {
        let (size, secs) = (1.15, 0.5);
        // first seen with the buff: one frame of the way, not the whole size
        let g = eased_any(None, true, size, secs, FRAME);
        assert!((g - (1.0 + 0.15 / 0.5 / 60.0)).abs() < 1e-6, "{g}");
        // every frame on, the whole way in half a second (30 frames), then held
        let mut g = 1.0;
        let mut prev = None;
        for _ in 0..31 {
            g = eased_any(prev, true, size, secs, FRAME);
            prev = Some((g, FRAME));
        }
        assert_eq!(g, size);
        // the buff over: back at the same pace; no buff and no record: plain
        let down = eased_any(Some((size, 0.1)), false, size, secs, FRAME);
        assert!((down - (size - 0.03)).abs() < 1e-6, "{down}");
        assert_eq!(eased_any(None, false, size, secs, FRAME), 1.0);
        // a stale record (back on screen mid-way): straight at the size, as a hero's own form
        assert_eq!(eased_any(Some((1.02, FORM_STALE + 0.1)), true, size, secs, FRAME), size);
        // with a growth of his own: the larger of the two
        assert_eq!(form_size(None, None), None);
        assert_eq!(form_size(Some(1.0), None), Some(1.0));
        assert_eq!(form_size(None, Some(1.15)), Some(1.15));
        assert_eq!(form_size(Some(1.15), Some(1.15)), Some(1.15), "Volibear's storm form under Wild Growth: x1.15, not x1.32");
        assert_eq!(form_size(Some(grown(0.30, 1)), Some(1.15)), Some(1.3), "Cho'Gath after a bite stays at his own x1.3");
        assert_eq!(form_size(Some(1.0), Some(1.08)), Some(1.08));
    }

    #[test]
    fn tags_are_read_from_a_fanim() {
        let f = r#"{"anims":{"idle":{"frames":[{"duration":0.1,"data":{"x":0.0}}]},"hd_idle":{"frames":[]},"hd_run" : {}}}"#;
        assert_eq!(hd_tags(f), vec!["hd_idle".to_string(), "hd_run".to_string()]);
    }
}
