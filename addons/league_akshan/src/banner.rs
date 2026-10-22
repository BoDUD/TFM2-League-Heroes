//! 复活的大字（用户 2026-10-22：「阿克尚到底能复活人吗 能加个大点的字幕提示和音效吗」）。
//!
//! 复活由被动在模拟里做（`lib.rs` 的 REVIVE）；屏幕看的那一场（`ClientMatchView`、观战、回放）里队友站起来（BACK）时记下
//! (场次, 局, tick, 阿克尚, 被复活的英雄)。屏幕放的是跑在前面的模拟的回放，所以按屏幕上的比赛时钟
//! （`game_places::clock::screen_tick`，附加包合集里由佛耶戈的时钟读取器喂，单独装时由本包的 [`Overlay`] 喂）
//! 到了那一 tick 才在画面中上方画 `SHOW_T` tick 的大字：「阿克尚 复活了 XXX！」，名字按游戏的语言。
//!
//! 游戏每个 mod 只有一个客户端扩展槽：附加包合集的槽给 league_addons 的 `BundleClient`（佛耶戈的时钟 + 本包的 [`draw`]），
//! 单独的 league_akshan.dll 用 [`Overlay`]。

use std::sync::Mutex;

use mod_api_stable::*;

/// 大字停多久（tick，60 一秒）、最后多久淡出。
pub const SHOW_T: usize = 180;
pub const FADE_T: usize = 40;

#[derive(Clone, Debug, PartialEq)]
pub struct Banner {
    pub m: u64,
    pub s: u64,
    pub tick: usize,
    pub akshan: String,
    pub ally: String,
}

static BANNERS: Mutex<Vec<Banner>> = Mutex::new(Vec::new());
/// The last banner logged (its tick): one `BANNER` line each, with the text drawn.
static LOGGED: Mutex<Option<(u64, u64, usize)>> = Mutex::new(None);
/// 屏幕看的那一场（最近一个有阿克尚的屏幕模拟）。
static VIEW: Mutex<Option<(u64, u64)>> = Mutex::new(None);

/// 屏幕模拟里有阿克尚：大字只认这一场的。
pub fn note_view(m: u64, s: u64) {
    if let Ok(mut v) = VIEW.lock() {
        if *v != Some((m, s)) {
            *v = Some((m, s));
            if let Ok(mut b) = BANNERS.lock() {
                b.retain(|x| (x.m, x.s) == (m, s));
            }
        }
    }
}

/// 屏幕模拟里复活成功一次。
pub fn note_revive(b: Banner) {
    if let Ok(mut l) = BANNERS.lock() {
        if !l.contains(&b) {
            l.push(b);
        }
    }
}

/// 屏幕时钟 `t` 时该画的那条（最近开始的一条）和它已经画了几 tick。
pub fn showing(all: &[Banner], view: Option<(u64, u64)>, t: usize) -> Option<(&Banner, usize)> {
    let (m, s) = view?;
    all.iter()
        .filter(|b| (b.m, b.s) == (m, s) && b.tick <= t && t < b.tick + SHOW_T)
        .max_by_key(|b| b.tick)
        .map(|b| (b, t - b.tick))
}

/// 游戏的语言（按阿克尚第一个技能名的写法认：简体「去而复还」、繁体「去而復還」，其他按文字）。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Lang {
    Hans,
    Hant,
    Ko,
    Ja,
    En,
}

pub fn lang_of(skill1: &str) -> Lang {
    let has = |lo: u32, hi: u32| skill1.chars().any(|c| (lo..=hi).contains(&(c as u32)));
    if has(0xac00, 0xd7a3) {
        Lang::Ko
    } else if has(0x3040, 0x30ff) {
        Lang::Ja
    } else if skill1.contains('復') || skill1.contains('還') {
        Lang::Hant
    } else if has(0x4e00, 0x9fff) {
        Lang::Hans
    } else {
        Lang::En
    }
}

pub fn line(lang: Lang, akshan: &str, ally: &str) -> String {
    match lang {
        Lang::Hans => format!("{akshan} 复活了 {ally}！"),
        Lang::Hant => format!("{akshan} 復活了 {ally}！"),
        Lang::Ko => format!("{akshan}이(가) {ally}을(를) 부활시켰습니다!"),
        Lang::Ja => format!("{akshan}が{ally}を復活させた！"),
        Lang::En => format!("{akshan} revived {ally}!"),
    }
}

/// 淡出：最后 FADE_T tick 线性降到 0。
pub fn alpha(age: usize) -> u32 {
    let left = SHOW_T.saturating_sub(age);
    if left >= FADE_T {
        255
    } else {
        (255 * left / FADE_T) as u32
    }
}

fn name(ctx: &StableClient<'_>, id: &str) -> String {
    ctx.i18n(&format!("asset/base/text/champion?description.{id}.name")).filter(|s| !s.is_empty())
        .unwrap_or_else(|| id.trim_start_matches("league_").to_string())
}

const FONT: &str = "asset/base/font/set/regular";

/// 画大字（客户端扩展的 post_render 里调）。
pub fn draw(ctx: &mut StableClient<'_>) {
    if !ctx.is_in_game() {
        return;
    }
    let Some(t) = game_places::clock::screen_tick() else { return };
    let view = VIEW.lock().ok().and_then(|v| *v);
    let shown = {
        let Ok(all) = BANNERS.lock() else { return };
        showing(&all, view, t).map(|(b, age)| (b.clone(), age))
    };
    let Some((b, age)) = shown else { return };
    let Some((w, h)) = ctx.draw_map_size("UI").filter(|s| s.0 > 0.0 && s.1 > 0.0) else { return };
    let lang = lang_of(&ctx.i18n("asset/base/text/champion?skill_name.league_akshan.skill1").unwrap_or_default());
    let text = line(lang, &name(ctx, &b.akshan), &name(ctx, &b.ally));
    if let Ok(mut l) = LOGGED.lock() {
        if *l != Some((b.m, b.s, b.tick)) {
            *l = Some((b.m, b.s, b.tick));
            if let Some(k) = super::counted("banner") {
                super::wlog(format!("BANNER m={} s={} t={} on screen at {t}: \"{text}\" ({lang:?}, UI {w:.0}x{h:.0}) #{k}",
                                    b.m, b.s, b.tick));
            }
        }
    }
    let a = alpha(age);
    let size = (h * 0.065).max(28.0);
    let (bw, bh) = (w * 0.62, size * 1.9);
    let (x, y) = ((w - bw) / 2.0, h * 0.2);
    ctx.draw_rect("UI", x, y, bw, bh, 900, bh * 0.25, 0x1a_10_08_00 | (a * 200 / 255));
    ctx.draw_rect("UI", x, y + bh - 4.0, bw, 4.0, 901, 0.0, 0xf2_c4_4a_00 | a);
    // a dark copy one step down-right, then the gold line over it
    let r = (x, y, bw, bh);
    ctx.draw_text("UI", &text, FONT, (r.0 + 3.0, r.1 + 3.0, r.2, r.3), 902, size, a, TextAlignXV1::Center,
                  TextAlignYV1::Center);
    ctx.draw_text("UI", &text, FONT, r, 903, size, 0xff_d8_5a_00 | a, TextAlignXV1::Center, TextAlignYV1::Center);
}

/// 单独装的 league_akshan.dll 的客户端扩展：喂屏幕时钟（league_neeko 的 ClockFeed 的做法）、画大字。
pub struct Overlay;

impl StableExtension for Overlay {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        if !ctx.is_in_game() {
            game_places::clock::observe(false, None);
            return;
        }
        let path = game_places::clock::CLOCK_PATH;
        let parts: Vec<&str> = path.split('.').collect();
        let shown = (1..=parts.len()).all(|n| ctx.ui_visible(&parts[..n].join(".")) == Some(true));
        let text = shown.then(|| ctx.ui_text(path)).flatten();
        game_places::clock::observe(true, text.as_deref());
    }

    fn post_render(&self, ctx: &mut StableClient<'_>) {
        draw(ctx);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn b(m: u64, tick: usize) -> Banner {
        Banner { m, s: 0, tick, akshan: "league_akshan".into(), ally: "league_garen".into() }
    }

    #[test]
    fn a_banner_shows_on_its_own_match_from_its_tick_for_show_t() {
        let all = vec![b(7, 1000), b(8, 1000)];
        assert!(showing(&all, Some((7, 0)), 999).is_none());
        assert_eq!(showing(&all, Some((7, 0)), 1000).map(|x| (x.0.m, x.1)), Some((7, 0)));
        assert_eq!(showing(&all, Some((7, 0)), 1000 + SHOW_T - 1).map(|x| x.1), Some(SHOW_T - 1));
        assert!(showing(&all, Some((7, 0)), 1000 + SHOW_T).is_none());
        assert!(showing(&all, None, 1000).is_none());
        // two close together: the later one
        let two = vec![b(7, 1000), b(7, 1050)];
        assert_eq!(showing(&two, Some((7, 0)), 1100).map(|x| x.0.tick), Some(1050));
    }

    #[test]
    fn the_language_follows_the_skill_name() {
        assert_eq!(lang_of("去而复还"), Lang::Hans);
        assert_eq!(lang_of("去而復還"), Lang::Hant);
        assert_eq!(lang_of("돌아오는 응징"), Lang::Ko);
        assert_eq!(lang_of("アヴェンジェラン"), Lang::Ja);
        assert_eq!(lang_of("Avengerang"), Lang::En);
        assert_eq!(line(Lang::Hans, "阿克尚", "盖伦"), "阿克尚 复活了 盖伦！");
    }

    #[test]
    fn it_fades_at_the_end() {
        assert_eq!(alpha(0), 255);
        assert_eq!(alpha(SHOW_T - FADE_T), 255);
        assert!(alpha(SHOW_T - 1) < 10);
        assert_eq!(alpha(SHOW_T), 0);
    }
}
