//! The screen's match clock, shared by the add-ons whose display hooks follow a sim that ran ahead of the screen
//! (league_viego_soul 0.1.7's way; league_neeko's disguise). The game has one client extension slot per mod and the
//! bundle's goes to Viego's reader, so the reader that owns the slot feeds this clock (`observe`) and every display
//! hook reads it (`screen_tick`). One copy per DLL: in league_addons all add-ons share it.
//! WARNING: `StableMod::set_extension` keeps only the last extension set. In league_addons that is BundleClient
//! (league_addons/src/lib.rs, set after every register): it calls Viego's ClockReader, which feeds this clock, and draws
//! Akshan's revive banner. Another add-on setting an extension in the bundle would replace it and stop the clock without
//! an error - Viego's possession, Neeko's disguise and Akshan's banner would never show. Add to BundleClient instead. A
//! single add-on DLL feeds its own copy (league_neeko's ClockFeed, league_akshan's Overlay).

use std::sync::Mutex;
use std::time::Instant;

/// The UI label holding the clock ("12:34").
pub const CLOCK_PATH: &str = "ingame.header.game_time.value";

struct Clock {
    secs: Option<(usize, Instant)>,
    rate: f64,
    ticking: bool,
}

static CLOCK: Mutex<Clock> = Mutex::new(Clock { secs: None, rate: 60.0, ticking: false });

/// "12:34" -> 754.
pub fn clock_secs(text: &str) -> Option<usize> {
    let (m, s) = text.trim().split_once(':')?;
    Some(m.trim().parse::<usize>().ok()? * 60 + s.trim().parse::<usize>().ok()?)
}

/// One look at the clock from a client extension's post_update: `in_game` false clears it; `shown` is the label's text
/// when it is on screen.
pub fn observe(in_game: bool, shown: Option<&str>) {
    let Ok(mut c) = CLOCK.lock() else { return };
    if !in_game {
        c.secs = None;
        c.ticking = false;
        return;
    }
    let Some(secs) = shown.and_then(clock_secs) else { return };
    let now = Instant::now();
    match c.secs {
        Some((s, _)) if s == secs => {}
        Some((s, at)) => {
            if secs == s + 1 {
                c.rate = (60.0 / now.duration_since(at).as_secs_f64()).clamp(10.0, 1200.0);
                c.ticking = true;
            } else if secs < s {
                c.ticking = false; // another match
            }
            c.secs = Some((secs, now));
        }
        None => c.secs = Some((secs, now)),
    }
}

/// The screen's sim tick now (None until the clock has stepped once this match).
pub fn screen_tick() -> Option<usize> {
    let c = CLOCK.lock().ok()?;
    let (secs, at) = c.secs?;
    c.ticking.then(|| secs * 60 + ((at.elapsed().as_secs_f64() * c.rate) as usize).min(59))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reads_the_label() {
        assert_eq!(clock_secs("15:48"), Some(948));
        assert_eq!(clock_secs(" 0:05 "), Some(5));
        assert_eq!(clock_secs("x"), None);
    }
}
