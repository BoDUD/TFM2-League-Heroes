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
use std::sync::atomic::{AtomicPtr, Ordering};
use std::sync::{LazyLock, Mutex};

/// The most a growing body ([`Table::growth`]) is drawn: twice its size.
pub const GROW_CAP: f32 = 2.0;

/// Game pixels from a frame's centre (the unit's position) down to its soles (tools/art/ppu_rig.py FEET).
pub const FEET: f32 = 11.5;

/// The body's growth for `stacks` stacks of a growth row (1.0 for none, GROW_CAP at most).
pub fn grown(per: f32, stacks: usize) -> f32 {
    (1.0 + per * stacks as f32).min(GROW_CAP)
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
    /// body drawn that much bigger about his soles, up to [`GROW_CAP`] (src/view.rs)
    pub growth: Vec<(&'a str, &'a str, f32)>,
    /// effect sheets drawn dense like a hero's sheet (id, PPU, .fanim: `idle` / `hd_idle` and any more tags, each with
    /// its hd_ twin): looked up like the heroes, no entity's body
    pub effects: Vec<(&'a str, f32, &'a str)>,
    /// effects whose pictures the view node draw (src/view.rs effect_detour) shrinks to 1 / PPU about their top-left
    /// corner; every other effect is drawn a square a game pixel
    pub drawn_effects: Vec<&'a str>,
    /// tall heroes drawn smaller wherever the UI draws lo_ frames (the ban/pick card above all): id, size
    pub ui_sizes: Vec<(&'a str, f32)>,
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
    /// every table's drawn effects ([`Table::drawn_effects`])
    pub drawn_effects: Vec<&'static str>,
}

impl Heroes {
    /// The heroes of `tables`, in order (tests and checks; the game's go through [`Registry`]).
    pub fn of(tables: &[&Table<'_>]) -> Self {
        tables.iter().fold(Heroes::default(), |h, t| h.and(t).0)
    }

    /// These heroes and table `t`'s -> them and the ids `t` brought. An id registered already keeps its first row (the
    /// host's own, the first guest's): `t`'s row of it is left out, with its growth and drawn-effect rows.
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
        let mut drawn_effects = self.drawn_effects.clone();
        drawn_effects.extend(t.drawn_effects.iter().filter(|id| came.contains(id)).map(|id| keep(id)));
        (Heroes { list, by_id, packs, prefixes, growth, drawn_effects }, came)
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
    /// [`Heroes::and`]); every other row is about one of them.
    pub fn ids_are_the_packs_once(t: &Table<'_>) {
        let mut seen = Vec::new();
        for &(id, ..) in t.heroes.iter().chain(t.effects.iter()) {
            assert!(id.starts_with(&format!("{}_", t.pack)), "{id}: not a {} id", t.pack);
            assert!(!id.contains(char::is_whitespace), "{id:?}");
            assert!(!seen.contains(&id), "{id}: listed twice");
            seen.push(id);
        }
        let others = t.sizes.iter().map(|s| s.0).chain(t.ui_sizes.iter().map(|s| s.0)).chain(t.growth.iter().map(|g| g.0));
        for id in others.chain(t.drawn_effects.iter().copied()) {
            assert!(seen.contains(&id), "{id}: a row for an id the table does not register");
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

    /// The table as a guest hands it to the host (src/share.rs) is read back the same.
    pub fn the_table_goes_through_the_text_unchanged(t: &Table<'_>) {
        let text = t.to_text();
        assert_eq!(Table::parse(&text).as_ref(), Ok(t));
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

    #[test]
    fn tags_are_read_from_a_fanim() {
        let f = r#"{"anims":{"idle":{"frames":[{"duration":0.1,"data":{"x":0.0}}]},"hd_idle":{"frames":[]},"hd_run" : {}}}"#;
        assert_eq!(hd_tags(f), vec!["hd_idle".to_string(), "hd_run".to_string()]);
    }
}
