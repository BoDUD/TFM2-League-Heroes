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

/// 客户端扩展每帧喂一次时钟（league.dll、tft.dll 这样喂；league_addons 由佛耶戈的 ClockReader 喂，league_dragons 由它的
/// Overlay 喂）：`in_game` 是不是在游戏里，`visible(路径)` 界面节点显示没有，`text(路径)` 节点上的字。
pub fn feed(in_game: bool, visible: impl Fn(&str) -> Option<bool>, text: impl Fn(&str) -> Option<String>) {
    if !in_game {
        observe(false, None);
        return;
    }
    let t = if label_shown(visible) { text(CLOCK_PATH) } else { None };
    observe(true, t.as_deref());
}

/// The screen's sim tick now (None until the clock has stepped once this match).
pub fn screen_tick() -> Option<usize> {
    let c = CLOCK.lock().ok()?;
    let (secs, at) = c.secs?;
    c.ticking.then(|| secs * 60 + ((at.elapsed().as_secs_f64() * c.rate) as usize).min(59))
}

/// 比赛时钟的标签这一帧在不在屏幕上：路径上每一层都显示着（`visible` 是客户端的 `ui_visible`）。离开比赛画面以后标签就没了，
/// 可 [`screen_tick`] 还停在最后读到的那一秒，所以「比赛画面上才画」的东西要先问这个。
pub fn label_shown(visible: impl Fn(&str) -> Option<bool>) -> bool {
    let parts: Vec<&str> = CLOCK_PATH.split('.').collect();
    (1..=parts.len()).all(|n| visible(&parts[..n].join(".")) == Some(true))
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

    #[test]
    fn the_label_counts_only_with_every_level_shown() {
        assert!(label_shown(|_| Some(true)));
        // 禁选画面：比赛界面的根节点藏着
        assert!(!label_shown(|p| Some(p != "ingame")));
        assert!(!label_shown(|p| Some(p != "ingame.header.game_time.value")));
        // 节点读不到也不算
        assert!(!label_shown(|p| (p != "ingame.header").then_some(true)));
    }
}
