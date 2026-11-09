//! 屏幕上的大小龙公告（league_eggs notice.rs 的做法）：龙魂、远古巨龙出现 / 被击杀、纳什男爵被击杀是大字，每条元素亚龙
//! 出现 / 被击杀（说是什么元素、全队多了什么）、远古龙之力的斩杀、创意工坊大小龙 mod 的冲突是小一号的提示。
//!
//! 事情来自 [`super::feed`]（屏幕上那一场，按模拟的 tick 记）；屏幕放的是跑在前面的模拟的回放，所以按屏幕上的比赛时钟
//! （`game_places::clock::screen_tick`）到了那一 tick 才放，几条挤在一起时排队一条接一条（[`schedule`]）。大字、小提示各一条道。
//!
//! 位置：和彩蛋的公告一样在画面中上方（大字在高度 16% 处，小提示在它下面）；附加包合集里彩蛋那条道上正放着东西时，本包那条道
//! 挪到彩蛋的下面（[`lanes`]，合集的 `BundleClient` 把彩蛋正在放什么告诉 [`super::screen::draw`]），两边不叠。

use mod_api_stable::*;

use super::feed::{Event, What};
use super::rules::Element;
use super::screen::{colour, draw_line_text, BOLD, FONT, UI};

/// 大字停多久、小提示停多久、冲突的提示停多久（tick，60 一秒），最后多久淡出。
pub const BIG_T: usize = 300;
pub const SMALL_T: usize = 240;
pub const CONFLICT_T: usize = 900;
pub const FADE_T: usize = 40;

/// 大字的几件事：龙魂、远古巨龙出现、远古巨龙和纳什男爵被击杀。
pub fn big(w: &What) -> bool {
    matches!(w, What::ElderSpawn | What::Soul { .. } | What::ElderKilled { .. } | What::BaronKilled { .. })
}

/// 这一条放多久。
pub fn show_t(w: &What) -> usize {
    match w {
        What::Conflict => CONFLICT_T,
        w if big(w) => BIG_T,
        _ => SMALL_T,
    }
}

/// 一条公告的颜色：元素的、纳什男爵的紫、斩杀的红、冲突的黄。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Tone {
    Element(Element),
    Baron,
    Execute,
    Warn,
}

pub fn tone(w: &What) -> Tone {
    match w {
        What::DrakeSpawn { element } | What::Drake { element, .. } | What::Soul { element, .. } => Tone::Element(*element),
        What::ElderSpawn | What::ElderKilled { .. } => Tone::Element(Element::Elder),
        What::Execute { .. } => Tone::Execute,
        What::BaronKilled { .. } => Tone::Baron,
        What::Conflict => Tone::Warn,
    }
}

/// 公告框的边和标题的颜色（0xRRGGBB00，透明度另加）。
pub fn tone_colour(t: Tone) -> u32 {
    match t {
        Tone::Element(e) => colour(e),
        Tone::Baron => 0xc0_7a_ff_00,
        Tone::Execute => 0xff_5a_3c_00,
        Tone::Warn => 0xff_d2_3c_00,
    }
}

/// 一条道（大字或小提示）上的公告排队：按发生的 tick（同一 tick 的按发生的先后），前一条没放完的往后排。
/// -> (开始的 tick, 在 `events` 里第几条)
pub fn schedule(events: &[Event], big_lane: bool) -> Vec<(usize, usize)> {
    let mut v: Vec<usize> = (0..events.len()).filter(|&i| big(&events[i].what) == big_lane).collect();
    v.sort_by_key(|&i| events[i].tick); // stable: the same tick keeps the order they came in
    let mut end = 0;
    v.into_iter()
        .map(|i| {
            let start = events[i].tick.max(end);
            end = start + show_t(&events[i].what);
            (start, i)
        })
        .collect()
}

/// 屏幕时钟 `t` 时这条道上在放的那条：(在 `events` 里第几条, 放了几 tick, 一共放多久)。
pub fn showing(events: &[Event], big_lane: bool, t: usize) -> Option<(usize, usize, usize)> {
    schedule(events, big_lane).into_iter().find_map(|(start, i)| {
        let show = show_t(&events[i].what);
        (start <= t && t < start + show).then(|| (i, t - start, show))
    })
}

/// 淡入淡出：前 10 tick 升上来，最后 FADE_T tick 线性降到 0。
pub fn alpha(age: usize, show: usize) -> u32 {
    let left = show.saturating_sub(age);
    let a = if left >= FADE_T { 255 } else { 255 * left / FADE_T };
    (a.min(255 * (age + 1) / 10)).min(255) as u32
}

/// 一行字大约多宽（以字号为单位）：中日韩的字一个字号宽，别的半个多。
pub fn em(text: &str) -> f32 {
    text.chars().map(|c| if (c as u32) >= 0x2e80 { 1.0 } else if c == ' ' { 0.3 } else { 0.56 }).sum()
}

/// 放得进 `width` 的字号：`base` 放得下就用它，放不下按比例缩小，最小 `min`。
pub fn fit(text: &str, width: f32, base: f32, min: f32) -> f32 {
    let e = em(text);
    if e <= 0.0 {
        return base;
    }
    (width * 0.94 / e).min(base).max(min)
}

/// 屏幕上的一块 (x, y, 宽, 高)。
pub type Rect = (f32, f32, f32, f32);

pub fn overlap(a: Rect, b: Rect) -> bool {
    a.0 < b.0 + b.2 && b.0 < a.0 + a.2 && a.1 < b.1 + b.3 && b.1 < a.1 + a.3
}

/// league_eggs notice.rs 的两条道在画面上的位置（照它的算法）：(大字那一块, 小提示那一块)。
pub fn eggs_lanes((w, h): (f32, f32)) -> (Rect, Rect) {
    let size = (h * 0.055).max(26.0);
    let small = (h * 0.026).max(15.0);
    let big_h = size * 1.5 + small * 1.7;
    let banner = ((w - w * 0.66) / 2.0, h * 0.16, w * 0.66, big_h);
    let tsize = (h * 0.028).max(17.0);
    let toast = ((w - w * 0.56) / 2.0, h * 0.16 + big_h + 10.0, w * 0.56, tsize * 1.7);
    (banner, toast)
}

/// 本包公告的字号和两块的位置。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Lanes {
    pub banner: Rect,
    pub title: f32,
    pub sub: f32,
    pub toast: Rect,
    pub line: f32,
    pub detail: f32,
}

/// 本包两条道的位置：彩蛋那条道上没东西时和彩蛋一样（大字在高度 16% 处，小提示在大字下面）；彩蛋正放着大字时本包的大字
/// 挪到彩蛋小提示那一块的下面、小提示再往下；彩蛋只放着小提示时本包的小提示挪到它下面。`eggs` = (彩蛋放着大字, 放着小提示)。
pub fn lanes((w, h): (f32, f32), eggs: (bool, bool)) -> Lanes {
    let title = (h * 0.052).max(24.0);
    let sub = (h * 0.024).max(14.0);
    let line = (h * 0.026).max(16.0);
    let detail = (h * 0.019).max(12.0);
    let (_, et) = eggs_lanes((w, h));
    let eggs_bottom = et.1 + et.3;
    let banner_h = title * 1.5 + sub * 1.8;
    let toast_h = line * 1.5 + detail * 1.5 + 6.0;
    let (bw, tw) = (w * 0.66, w * 0.58);
    let banner_y = if eggs.0 { eggs_bottom + 10.0 } else { h * 0.16 };
    let mut toast_y = banner_y + banner_h + 10.0;
    if eggs.1 && !eggs.0 {
        toast_y = toast_y.max(eggs_bottom + 8.0);
    }
    Lanes {
        banner: ((w - bw) / 2.0, banner_y, bw, banner_h),
        title,
        sub,
        toast: ((w - tw) / 2.0, toast_y, tw, toast_h),
        line,
        detail,
    }
}

/// 画一条在放着的公告（每帧；字由 [`super::words::notice`] 先写好）：大字或小提示，透明度 `a`。
pub fn draw_one(ctx: &mut StableClient<'_>, l: &Lanes, big_lane: bool, title: &str, sub: &str, a: u32, tone: Tone) {
    if big_lane {
        banner(ctx, l, title, sub, a, tone);
    } else {
        toast(ctx, l, title, sub, a, tone);
    }
}

/// 大字：画面中上方一个框，标题用这件事的颜色（元素的、纳什男爵的紫），第二行白色。
fn banner(ctx: &mut StableClient<'_>, l: &Lanes, title: &str, sub: &str, a: u32, tone: Tone) {
    let (x, y, bw, bh) = l.banner;
    let edge = tone_colour(tone);
    ctx.draw_rect(UI, x, y, bw, bh, 910, bh * 0.2, 0x10_14_22_00 | (a * 220 / 255));
    ctx.draw_rect(UI, x, y + bh - 4.0, bw, 4.0, 911, 0.0, edge | a);
    ctx.draw_rect(UI, x + bw * 0.1, y, bw * 0.8, 2.0, 911, 0.0, edge | (a * 160 / 255));
    let size = fit(title, bw, l.title, l.title * 0.5);
    let r = (x, y + l.title * 0.12, bw, l.title * 1.3);
    draw_line_text(ctx, title, BOLD, r, 912, size, a, edge | a);
    if !sub.is_empty() {
        let s = fit(sub, bw, l.sub, l.sub * 0.6);
        let r2 = (x, y + l.title * 1.42, bw, l.sub * 1.6);
        draw_line_text(ctx, sub, FONT, r2, 912, s, a, 0xf4_ee_dc_00 | a);
    }
}

/// 小提示：大字下面一条框，左边一道这件事的颜色；第一行亮色，第二行（全队多了什么、谁拿到了）小一号。
fn toast(ctx: &mut StableClient<'_>, l: &Lanes, title: &str, detail: &str, a: u32, tone: Tone) {
    let (x, y, tw, _) = l.toast;
    let edge = tone_colour(tone);
    let th = if detail.is_empty() { l.line * 1.6 } else { l.toast.3 };
    let fill = if tone == Tone::Execute { 0x2a_0c_08_00 } else { 0x14_12_10_00 };
    ctx.draw_rect(UI, x, y, tw, th, 910, th * 0.25, fill | (a * 200 / 255));
    ctx.draw_rect(UI, x, y + 3.0, 6.0, th - 6.0, 911, 2.0, edge | a);
    let inner = (x + 10.0, tw - 20.0);
    let size = fit(title, inner.1, l.line, l.line * 0.55);
    let r = (inner.0, y + 2.0, inner.1, l.line * 1.5);
    draw_line_text(ctx, title, BOLD, r, 912, size, a, lighten(edge) | a);
    if !detail.is_empty() {
        let s = fit(detail, inner.1, l.detail, l.detail * 0.6);
        let r2 = (inner.0, y + l.line * 1.45, inner.1, l.detail * 1.5);
        draw_line_text(ctx, detail, FONT, r2, 912, s, a, 0xe6_e0_d2_00 | a);
    }
}

/// 颜色往白里调一半（深一点的元素色在暗底上也看得清）。
pub fn lighten(c: u32) -> u32 {
    let ch = |shift: u32| (((c >> shift) & 0xff) + 0xff) / 2;
    (ch(24) << 24) | (ch(16) << 16) | (ch(8) << 8)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ev(tick: usize, what: What) -> Event {
        Event { m: 7, s: 1, tick, what }
    }

    fn drake(tick: usize, total: u8) -> Event {
        ev(tick, What::Drake { team: 0, element: Element::Infernal, total })
    }

    /// Every kind of the feed's events goes to its lane with its look.
    #[test]
    fn feed_events_map_to_their_lane_and_look() {
        let cases = [
            (What::DrakeSpawn { element: Element::Ocean }, false, Tone::Element(Element::Ocean)),
            (What::Drake { team: 1, element: Element::Cloud, total: 2 }, false, Tone::Element(Element::Cloud)),
            (What::Soul { team: 0, element: Element::Hextech }, true, Tone::Element(Element::Hextech)),
            (What::ElderSpawn, true, Tone::Element(Element::Elder)),
            (What::ElderKilled { team: 0, holders: vec![] }, true, Tone::Element(Element::Elder)),
            (What::Execute { team: 1, killer: "a".into(), victim: "b".into() }, false, Tone::Execute),
            (What::BaronKilled { team: 1, holders: vec![] }, true, Tone::Baron),
            (What::Conflict, false, Tone::Warn),
        ];
        for (w, b, t) in cases {
            assert_eq!((big(&w), tone(&w)), (b, t), "{w:?}");
        }
        assert_eq!(show_t(&What::Conflict), CONFLICT_T);
        assert_eq!(show_t(&What::ElderSpawn), BIG_T);
        assert_eq!(show_t(&What::Drake { team: 0, element: Element::Infernal, total: 1 }), SMALL_T);
    }

    #[test]
    fn notes_queue_one_after_another_in_their_own_lane() {
        // two drakes taken a moment apart, a soul at the second: the toasts queue, the soul's banner shows at once
        let events = vec![drake(1000, 3), drake(1010, 4), ev(1010, What::Soul { team: 0, element: Element::Infernal }),
                          ev(5000, What::ElderSpawn)];
        let small = schedule(&events, false);
        assert_eq!(small, vec![(1000, 0), (1000 + SMALL_T, 1)]);
        let big_ = schedule(&events, true);
        assert_eq!(big_, vec![(1010, 2), (5000, 3)]);
        assert_eq!(showing(&events, false, 1100), Some((0, 100, SMALL_T)));
        assert_eq!(showing(&events, false, 1000 + SMALL_T + 5), Some((1, 5, SMALL_T)));
        assert_eq!(showing(&events, true, 1100), Some((2, 90, BIG_T)));
        assert_eq!(showing(&events, true, 1010 + BIG_T), None);
        assert_eq!(showing(&events, false, 999), None);
        // the conflict warning stays longer
        let c = vec![ev(300, What::Conflict)];
        assert!(showing(&c, false, 300 + SMALL_T + 10).is_some());
        assert!(showing(&c, false, 300 + CONFLICT_T).is_none());
    }

    #[test]
    fn it_fades_in_and_out() {
        assert!(alpha(0, BIG_T) < 60);
        assert_eq!(alpha(20, BIG_T), 255);
        assert_eq!(alpha(BIG_T - FADE_T, BIG_T), 255);
        assert!(alpha(BIG_T - 1, BIG_T) < 10);
        assert_eq!(alpha(BIG_T, BIG_T), 0);
    }

    #[test]
    fn long_lines_shrink_to_fit() {
        assert_eq!(em("炼狱"), 2.0);
        assert!((em("ab") - 1.12).abs() < 1e-4);
        assert_eq!(fit("短", 600.0, 30.0, 10.0), 30.0);
        let long = "检测到创意工坊模组 Elemental Drakes & Baron，请在模组列表里关掉它，本模组的龙才会生效";
        let s = fit(long, 600.0, 30.0, 10.0);
        assert!(s < 30.0 && s * em(long) <= 600.0 * 0.95, "{s}");
        assert_eq!(fit(long, 50.0, 30.0, 10.0), 10.0);
    }

    /// Ours never cover the easter eggs' notices on screen, whatever the eggs show; and they stay on screen.
    #[test]
    fn the_lanes_keep_clear_of_the_eggs() {
        for ui in [(1920.0, 1080.0), (1280.0, 720.0)] {
            let (eb, et) = eggs_lanes(ui);
            for eggs in [(false, false), (true, false), (false, true), (true, true)] {
                let l = lanes(ui, eggs);
                assert!(!overlap(l.banner, l.toast), "{ui:?} {eggs:?}");
                for mine in [l.banner, l.toast] {
                    if eggs.0 {
                        assert!(!overlap(mine, eb), "{ui:?} {eggs:?} {mine:?} vs the eggs' banner");
                    }
                    if eggs.1 {
                        assert!(!overlap(mine, et), "{ui:?} {eggs:?} {mine:?} vs the eggs' toast");
                    }
                    assert!(mine.0 >= 0.0 && mine.0 + mine.2 <= ui.0 && mine.1 + mine.3 < ui.1 * 0.6, "{ui:?} {eggs:?}");
                }
            }
            // nothing of the eggs on screen: the same place as the eggs' lanes (the top of the screen's middle)
            let free = lanes(ui, (false, false));
            assert_eq!(free.banner.1, eb.1);
            // below the game's header (50 of 1080)
            assert!(free.banner.1 > ui.1 * 50.0 / 1080.0);
        }
    }
}
