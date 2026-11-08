//! HUD：比赛画面左上角（游戏顶栏下面、时间控制按钮右边）一个小框——这一条（或下一条）龙是什么元素、纳什男爵在不在，两队各一行：
//! 每种元素亚龙的层数（元素颜色的圆点，里面是玩家的叫法「火 土 水 风 海 化」，后面是层数）、拿到的龙魂、远古龙之力 / 纳什男爵之手
//! 还剩多久；拿着远古龙之力 / 纳什男爵之手的人在比赛下方玩家栏的英雄头像左边各有一个小圆点。
//!
//! 内容来自 [`super::feed::record_at`]（屏幕时钟那一刻的状态记录）；没有大小龙的模式（死斗）这一局没有任何大小龙的事，不画。
//! 位置按游戏界面的节点算（`ingame.header` 的下沿、`ingame.time_control` 的右边，1920x1080 的界面坐标里是 (311, 56)），碰不到
//! 游戏的顶栏、比赛时间、左上角的时间控制、右边的击杀记录（`ingame.kills`，y 141 起），也碰不到彩蛋的公告（高度 16% 起）和
//! 玩家栏头像上彩蛋的计数、冠冕。

use mod_api_stable::*;

use super::feed::Event;
use super::notice::{em, Rect};
use super::rules::{Element, Record, DRAKES};
use super::screen::{colour, draw_text_in, BARON, BLUE, BOLD, FONT, RED, UI};
use super::words::{self, Lang};

/// HUD 里的一块。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Piece {
    /// 一行开头的队伍小标（0 蓝、1 红）。
    Tag(usize),
    /// 一种元素亚龙的层数。
    Stack(Element, u8),
    /// 这一队拿到的龙魂。
    Soul(Element),
    /// 远古龙之力（`baron` false）/ 纳什男爵之手还剩几秒、几个人拿着。
    Timer { baron: bool, left: usize, n: u32 },
    /// 这一队什么都还没有。
    Nothing,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Hud {
    /// 活着的那条龙的元素，没有活着的就是下一条的。
    pub element: Element,
    pub alive: bool,
    pub baron_alive: bool,
    /// 两队（0 蓝、1 红）各一行。
    pub rows: [Vec<Piece>; 2],
    /// 撞上创意工坊的大小龙 mod：本包什么都不做，HUD 只写一行请玩家关掉它。
    pub conflict: bool,
}

/// 屏幕时钟 `t` 时的 HUD（`rec`：写在 `t` 或之前的最后一份状态记录）。
pub fn hud(rec: &Record, t: usize) -> Hud {
    let mut rows = [Vec::new(), Vec::new()];
    for (team, row) in rows.iter_mut().enumerate() {
        row.push(Piece::Tag(team));
        for e in DRAKES {
            let n = rec.stacks[team][e.slot().unwrap_or(0)];
            if n > 0 {
                row.push(Piece::Stack(e, n));
            }
        }
        if let Some(e) = rec.soul.filter(|s| s.0 == team).and_then(|s| Element::from_code(s.1)) {
            row.push(Piece::Soul(e));
        }
        for (hold, baron) in [(rec.elder, false), (rec.baron, true)] {
            if let Some(h) = hold.filter(|h| h.team == team && h.until > t && h.lanes != 0) {
                row.push(Piece::Timer { baron, left: (h.until - t).div_ceil(60), n: h.lanes.count_ones() });
            }
        }
        if row.len() == 1 {
            row.push(Piece::Nothing);
        }
    }
    Hud {
        element: Element::from_code(rec.cur).unwrap_or(Element::Infernal),
        alive: rec.serpen_alive,
        baron_alive: rec.epic_alive,
        rows,
        conflict: rec.conflict,
    }
}

/// 要不要画：这一局到 `t` 有过大小龙的事，或者状态记录里有东西（活着的小龙 / 纳什男爵、层数、龙魂、远古 / 男爵、冲突）。
/// 没有小龙的模式里状态记录也写着（开局一份），但什么都没有：不画。
pub fn visible(rec: &Record, events: &[Event], t: usize) -> bool {
    events.iter().any(|e| e.tick <= t)
        || rec.serpen_alive
        || rec.epic_alive
        || rec.conflict
        || rec.soul.is_some()
        || rec.elder.is_some()
        || rec.baron.is_some()
        || rec.stacks.iter().flatten().any(|&n| n > 0)
}

/// 字号和间距（按界面高度，1080 时层数 17、标签 15、一行 23：三行的框正好在击杀记录（y 141 起）上面）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Metrics {
    pub s: f32,
    pub font: f32,
    pub small: f32,
    pub row: f32,
    pub pad: f32,
    pub gap: f32,
    pub disc: f32,
}

pub fn metrics(h: f32) -> Metrics {
    let s = h / 1080.0;
    let font = (17.0 * s).max(12.0);
    Metrics {
        s,
        font,
        small: (15.0 * s).max(11.0),
        row: font * 1.375,
        pad: (6.0 * s).max(4.0),
        gap: (6.0 * s).max(4.0),
        disc: font * 1.2,
    }
}

fn tag_w(lang: Lang, team: usize, m: &Metrics) -> f32 {
    em(words::team_tag(lang, team)) * m.font * 0.9 + 10.0 * m.s
}

fn stack_text(n: u8) -> String {
    format!("×{n}")
}

fn timer_text(lang: Lang, baron: bool, left: usize) -> String {
    format!("{} {}", words::timer_label(lang, baron), words::clock(left))
}

/// 一块多宽。
pub fn piece_w(p: &Piece, lang: Lang, m: &Metrics) -> f32 {
    match *p {
        Piece::Tag(team) => tag_w(lang, team, m),
        Piece::Stack(_, n) => m.disc + 3.0 * m.s + em(&stack_text(n)) * m.font,
        Piece::Soul(e) => em(&words::soul(lang, e)) * m.small + 12.0 * m.s,
        Piece::Timer { baron, left, .. } => em(&timer_text(lang, baron, left)) * m.small + 12.0 * m.s,
        Piece::Nothing => em(words::NOTHING) * m.font,
    }
}

pub fn row_w(row: &[Piece], lang: Lang, m: &Metrics) -> f32 {
    row.iter().map(|p| piece_w(p, lang, m)).sum::<f32>() + m.gap * row.len().saturating_sub(1) as f32
}

/// 顶上一行（圆点、这一条 / 下一条龙，纳什男爵活着时再写一句）多宽。
pub fn top_w(h: &Hud, lang: Lang, m: &Metrics) -> f32 {
    let mut w = m.disc + m.gap + em(&words::dragon_status(lang, h.element, h.alive)) * m.small;
    if h.baron_alive {
        w += 3.0 * m.gap + em(words::baron_status(lang)) * m.small;
    }
    w
}

/// 框的大小：(宽, 高)。冲突时只有一行字。
pub fn size(h: &Hud, lang: Lang, m: &Metrics) -> (f32, f32) {
    if h.conflict {
        return (em(words::conflict_line(lang)) * m.small + 2.0 * m.pad, m.row + 2.0 * m.pad);
    }
    let content = h.rows.iter().map(|r| row_w(r, lang, m)).fold(top_w(h, lang, m), f32::max);
    (content + 2.0 * m.pad, 3.0 * m.row + 2.0 * m.pad)
}

/// 框放在哪：游戏顶栏（`header`）下沿往下 6、时间控制按钮（`time_ctrl`，看得见时）右边 10；找不到节点时用 1920x1080 布局里
/// 的位置（顶栏 50 高、时间控制到 x 301）。不出画面。
pub fn place(ui: (f32, f32), header: Option<Rect>, time_ctrl: Option<Rect>, (w, h): (f32, f32)) -> Rect {
    let s = ui.1 / 1080.0;
    let y = header.filter(|r| r.3 > 0.0).map_or(56.0 * s, |r| r.1 + r.3 + 6.0 * s);
    let x = time_ctrl.filter(|r| r.2 > 0.0).map_or(311.0 * s, |r| r.0 + r.2 + 10.0 * s);
    (x.min(ui.0 - w - 8.0 * s).max(8.0 * s), y, w, h)
}

/// 远古龙之力 / 纳什男爵之手的小圆点在一个英雄头像上的位置：(圆心 x, 圆心 y, 半径)。头像左边，远古在中间、纳什男爵在下面
/// （彩蛋的计数在头像右下、冠冕在上缘，都碰不到）。
pub fn holder_dot(icon: Rect, baron: bool) -> (f32, f32, f32) {
    let (x, y, w, h) = icon;
    (x + 0.20 * w, y + if baron { 0.82 } else { 0.47 } * h, 0.13 * w)
}

/// 远古龙之力的颜色（淡金）和纳什男爵之手的（紫）。
pub fn hold_colour(baron: bool) -> u32 {
    if baron {
        BARON
    } else {
        colour(Element::Elder)
    }
}

/// 画 HUD（`at` 是 [`place`] 算好的框）。
pub fn draw(ctx: &mut StableClient<'_>, at: Rect, h: &Hud, lang: Lang, m: &Metrics) {
    let (x, y, w, bh) = at;
    ctx.draw_rect(UI, x, y, w, bh, 900, 6.0 * m.s, 0x10_14_22_c8);
    let left = x + m.pad;
    if h.conflict {
        draw_text_in(ctx, words::conflict_line(lang), FONT, (left, y + m.pad, w + 4.0 * m.small, m.row), 902, m.small,
                     0xff_d2_3c_ff, TextAlignXV1::Left);
        return;
    }
    // the dragon up (or next) and Baron
    let y0 = y + m.pad;
    let a = if h.alive { 0xff } else { 0x90 };
    disc(ctx, (left + m.disc / 2.0, y0 + m.row / 2.0), h.element, lang, a, m);
    let status = words::dragon_status(lang, h.element, h.alive);
    let sx = left + m.disc + m.gap;
    let sw = em(&status) * m.small + 2.0;
    let tc = if h.alive { 0xf4_ee_dc_ff } else { 0xb4_b0_a8_ff };
    draw_text_in(ctx, &status, FONT, (sx, y0, sw + 2.0 * m.small, m.row), 902, m.small, tc, TextAlignXV1::Left);
    if h.baron_alive {
        let bx = sx + sw + 3.0 * m.gap;
        let bs = words::baron_status(lang);
        draw_text_in(ctx, bs, FONT, (bx, y0, (em(bs) + 2.0) * m.small, m.row), 902, m.small, BARON | 0xff, TextAlignXV1::Left);
    }
    // the two teams
    for (team, row) in h.rows.iter().enumerate() {
        let ry = y0 + m.row * (1 + team) as f32;
        let mut px = left;
        for p in row {
            let pw = piece_w(p, lang, m);
            piece(ctx, (px, ry, pw, m.row), p, lang, m);
            px += pw + m.gap;
        }
    }
}

/// 元素的圆点：元素颜色，里面一个字。
fn disc(ctx: &mut StableClient<'_>, (cx, cy): (f32, f32), e: Element, lang: Lang, a: u32, m: &Metrics) {
    let r = m.disc / 2.0;
    ctx.draw_circle(UI, cx, cy, r + 1.0, 903, 0x08_0a_10_00 | a);
    ctx.draw_circle(UI, cx, cy, r, 904, colour(e) | a);
    let g = words::glyph(lang, e);
    let size = if em(g) > 1.05 { m.disc * 0.46 } else { m.disc * 0.62 };
    draw_text_in(ctx, g, BOLD, (cx - 2.0 * r, cy - r, 4.0 * r, 2.0 * r), 905, size, 0x14_16_20_00 | a, TextAlignXV1::Center);
}

fn piece(ctx: &mut StableClient<'_>, (x, y, w, h): Rect, p: &Piece, lang: Lang, m: &Metrics) {
    let inner = (y + h * 0.12, h * 0.76);
    // centred texts get room on both sides: a line a little wider than estimated never wraps
    let wide = (x - m.small, y, w + 2.0 * m.small, h);
    match *p {
        Piece::Tag(team) => {
            ctx.draw_rect(UI, x, inner.0, w, inner.1, 903, 4.0 * m.s, if team == 0 { BLUE } else { RED } | 0xe8);
            draw_text_in(ctx, words::team_tag(lang, team), BOLD, wide, 904, m.font * 0.9, 0xff_ff_ff_ff,
                         TextAlignXV1::Center);
        }
        Piece::Stack(e, n) => {
            disc(ctx, (x + m.disc / 2.0, y + h / 2.0), e, lang, 0xff, m);
            let tx = x + m.disc + 3.0 * m.s;
            draw_text_in(ctx, &stack_text(n), BOLD, (tx, y, w - (tx - x) + m.font, h), 904, m.font, 0xff_ff_ff_ff,
                         TextAlignXV1::Left);
        }
        Piece::Soul(e) => {
            ctx.draw_rect(UI, x, inner.0, w, inner.1, 903, 4.0 * m.s, colour(e) | 0xe8);
            draw_text_in(ctx, &words::soul(lang, e), BOLD, wide, 904, m.small, 0x14_16_20_ff, TextAlignXV1::Center);
        }
        Piece::Timer { baron, left, .. } => {
            ctx.draw_rect(UI, x, inner.0, w, inner.1, 903, 4.0 * m.s, hold_colour(baron) | 0xe8);
            draw_text_in(ctx, &timer_text(lang, baron, left), BOLD, wide, 904, m.small, 0x14_16_20_ff,
                         TextAlignXV1::Center);
        }
        Piece::Nothing => {
            draw_text_in(ctx, words::NOTHING, FONT, (x, y, w + m.font, h), 904, m.font, 0x8c_88_80_ff, TextAlignXV1::Left);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::feed::What;
    use super::super::notice::{eggs_lanes, overlap};
    use super::super::rules::HoldRec;

    fn rec() -> Record {
        Record { tick: 100, cur: 1, order: [1, 3, 4], ..Record::default() }
    }

    #[test]
    fn the_record_becomes_two_rows() {
        let mut r = rec();
        r.stacks[0] = [2, 0, 1, 0, 0, 0];
        r.stacks[1] = [0, 0, 0, 1, 0, 0];
        r.soul = Some((0, 1));
        r.serpen_alive = true;
        r.elder = Some(HoldRec { team: 1, lanes: 0b10110, until: 10_000 });
        r.baron = Some(HoldRec { team: 0, lanes: 0b1, until: 9_000 });
        let h = hud(&r, 8_941);
        assert_eq!((h.element, h.alive, h.baron_alive, h.conflict), (Element::Infernal, true, false, false));
        assert_eq!(h.rows[0], vec![Piece::Tag(0), Piece::Stack(Element::Infernal, 2), Piece::Stack(Element::Ocean, 1),
                                   Piece::Soul(Element::Infernal), Piece::Timer { baron: true, left: 1, n: 1 }]);
        assert_eq!(h.rows[1], vec![Piece::Tag(1), Piece::Stack(Element::Cloud, 1),
                                   Piece::Timer { baron: false, left: 18, n: 3 }]);
        // time up, or all its holders dead: no timer; nothing at all: a dash
        let h = hud(&r, 10_000);
        assert!(!h.rows[1].iter().any(|p| matches!(p, Piece::Timer { .. })));
        r.elder = Some(HoldRec { team: 1, lanes: 0, until: 10_000 });
        r.stacks[1] = [0; 6];
        assert_eq!(hud(&r, 9_500).rows[1], vec![Piece::Tag(1), Piece::Nothing]);
    }

    #[test]
    fn nothing_shows_in_a_mode_without_dragons() {
        let r = rec();
        assert!(!visible(&r, &[], 5_000));
        let spawn = Event { m: 1, s: 1, tick: 7_200, what: What::DrakeSpawn { element: Element::Ocean } };
        assert!(!visible(&r, std::slice::from_ref(&spawn), 7_199));
        assert!(visible(&r, std::slice::from_ref(&spawn), 7_200));
        assert!(visible(&Record { epic_alive: true, ..rec() }, &[], 5_000));
        assert!(visible(&Record { conflict: true, ..rec() }, &[], 5_000));
    }

    /// The biggest box (three elements, a soul, both timers, in each language) keeps clear of the game's header, its match
    /// clock, the time controls, the kill log and the easter eggs' notices, in the 1920x1080 layout's own places.
    #[test]
    fn the_box_keeps_clear_of_the_game_and_the_eggs() {
        let ui = (1920.0, 1080.0);
        let header = (0.0, 0.0, 1920.0, 50.0);
        let time_ctrl = (19.0, 64.0, 282.0, 36.0);
        let game_time = (930.0, 44.0, 60.0, 28.0);
        let kills = (848.0, 141.0, 130.0, 900.0);
        let (eggs_banner, eggs_toast) = eggs_lanes(ui);
        let full = |team: usize| {
            vec![Piece::Tag(team), Piece::Stack(Element::Chemtech, 2), Piece::Stack(Element::Mountain, 1),
                 Piece::Stack(Element::Hextech, 1), Piece::Soul(Element::Chemtech),
                 Piece::Timer { baron: false, left: 90, n: 5 }, Piece::Timer { baron: true, left: 120, n: 5 }]
        };
        let worst = Hud { element: Element::Chemtech, alive: false, baron_alive: true, rows: [full(0), full(1)], conflict: false };
        let m = metrics(ui.1);
        for lang in [Lang::Hans, Lang::Hant, Lang::En] {
            for h in [worst.clone(), Hud { conflict: true, ..worst.clone() }] {
                let at = place(ui, Some(header), Some(time_ctrl), size(&h, lang, &m));
                for (what, r) in [("header", header), ("time controls", time_ctrl), ("match clock", game_time),
                                  ("kill log", kills), ("eggs' banner", eggs_banner), ("eggs' toast", eggs_toast)] {
                    assert!(!overlap(at, r), "{lang:?} conflict {}: {at:?} covers the {what} {r:?}", h.conflict);
                }
                assert!(at.0 >= 0.0 && at.0 + at.2 <= ui.0 && at.1 + at.3 <= ui.1);
                // readable: the text is at least 12 px at 1080
                assert!(m.small >= 12.0 && m.font >= 12.0);
            }
        }
        // the layout's own place when the nodes aren't there
        let at = place(ui, None, None, (300.0, 80.0));
        assert_eq!((at.0, at.1), (311.0, 56.0));
        // smaller screens scale down and stay inside
        let small = (1280.0, 720.0);
        let m = metrics(small.1);
        let at = place(small, None, None, size(&worst, Lang::En, &m));
        assert!(at.0 + at.2 <= small.0 && m.font >= 12.0);
    }

    /// The holders' dots sit on the left of the champion icon, clear of the easter eggs' count badge and ice crown.
    #[test]
    fn the_holder_dots_keep_clear_of_the_eggs_badges() {
        let icon = (372.0, 200.0, 40.0, 40.0);
        let (x, y, w, h) = icon;
        // league_eggs notice.rs: the count badge and the crown's parts
        let (bw, bh) = (w * 0.62, h * 0.52);
        let badge = (x + w - bw * 0.85, y + h - bh * 0.8, bw, bh);
        let u = w / 10.0;
        let crown = (x + w / 2.0 - 3.5 * u, y - 2.0 * u, 7.0 * u, 4.6 * u);
        let mut boxes = Vec::new();
        for baron in [false, true] {
            let (cx, cy, r) = holder_dot(icon, baron);
            let b = (cx - r - 1.0, cy - r - 1.0, 2.0 * r + 2.0, 2.0 * r + 2.0);
            assert!(b.0 >= x && b.0 + b.2 <= x + w && b.1 >= y && b.1 + b.3 <= y + h, "{baron}: inside the icon");
            assert!(!overlap(b, badge) && !overlap(b, crown), "{baron}");
            boxes.push(b);
        }
        assert!(!overlap(boxes[0], boxes[1]));
    }
}
