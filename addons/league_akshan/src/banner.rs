//! 复活的大字（用户 2026-10-22：「阿克尚到底能复活人吗 能加个大点的字幕提示和音效吗」）。
//!
//! 复活由被动在模拟里做（`lib.rs` 的 REVIVE）；屏幕看的那一场（`ClientMatchView`、观战、回放）里队友站起来（BACK）时记下
//! (场次, 局, tick, 阿克尚, 被复活的英雄)。屏幕放的是跑在前面的模拟的回放，所以按屏幕上的比赛时钟
//! （`game_places::clock::screen_tick`，附加包合集里由佛耶戈的时钟读取器喂，单独装时由本包的 [`Overlay`] 喂）
//! 到了那一 tick 才在画面中上方画 `SHOW_T` tick 的大字：「阿克尚 复活了 XXX！」，名字按游戏的语言。
//!
//! 游戏每个 mod 只有一个客户端扩展槽：附加包合集的槽给 league_addons 的 `BundleClient`（佛耶戈的时钟 + 本包的 [`draw`]），
//! 单独的 league_akshan.dll 用 [`Overlay`]。
//!
//! 0.2.3（用户 2026-10-30：「没有阿克尚的对局也出现了阿克尚复活的提示」「就我现在这把 出现了」）：屏幕在放哪一场以前只由阿克尚
//! 的被动记，第 2 局（738 场，没有阿克尚）开始后还认为在放第 1 局，屏幕时钟走到 8:28 时又把第 1 局的复活画了一遍。现在由 AI 钩子
//! [`Screen`] 在每个屏幕模拟里记，有没有阿克尚都算。文字的键补上游戏自己用的 `#`（[`text`]）：0.2.0 不带它，什么都没查到，
//! 画出来的是「akshan revived jax!」。

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
/// 屏幕看的那一场（最近一个屏幕模拟，有没有阿克尚都算）。
static VIEW: Mutex<Option<(u64, u64)>> = Mutex::new(None);

/// 屏幕在放这一场（[`Screen`] 和阿克尚的被动记）：大字只认这一场的，换了一场就扔掉别场的，日志记一行 `VIEW`。
pub fn note_view(m: u64, s: u64) {
    if let Ok(mut v) = VIEW.lock() {
        if *v != Some((m, s)) {
            if let Some(k) = super::counted("view") {
                let was = v.map_or("none".to_string(), |(m, s)| format!("m={m} s={s}"));
                super::wlog(format!("VIEW m={m} s={s} on screen (was {was}) #{k}"));
            }
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

/// 记屏幕在放哪一场：每个模拟的 0 号玩家身上的 AI 钩子，隔 `SCREEN_EVERY` tick 看一次模拟的来源，只旁观、不改输入。
#[derive(Clone, Default)]
pub struct Screen {
    last: Option<usize>,
}

pub const SCREEN_EVERY: usize = 60;

/// 这一 tick 该看了：第一次、过了 `SCREEN_EVERY`，或者 tick 往回走了（换了一个模拟）。
pub fn due(last: Option<usize>, t: usize) -> bool {
    last.is_none_or(|l| t < l || t >= l + SCREEN_EVERY)
}

impl StablePlayerAi for Screen {
    fn clone_box(&self) -> Box<dyn StablePlayerAi> {
        Box::new(self.clone())
    }

    fn id(&self) -> String {
        format!("{}:screen", super::ID)
    }

    fn priority(&self) -> i32 {
        i32::MIN
    }

    fn matches(&self, init: &StableAiInit) -> bool {
        init.player_id == 0
    }

    fn think(&mut self, ctx: &mut StableAiContext<'_>, _base: Option<InputV1>) -> Option<InputV1> {
        let t = ctx.tick();
        if due(self.last, t) {
            self.last = Some(t);
            if let Some((m, s)) = ctx.sim().and_then(|sim| super::on_screen(&sim)) {
                note_view(m, s);
            }
        }
        None
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

/// 游戏的语言（按阿克尚第一个技能名的写法认：简体「去而复还」、繁体「復仇迴力鏢」，其他按文字）。
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

/// 游戏的一条文字。游戏自己的代码查的键带 `#`（TeamfightManager2.exe 里有 `#asset/base/text/champion?description.`）；
/// 先带 `#` 查，再按 0.2.0 的不带查，查到空的或原样的键都不算。
fn text(ctx: &StableClient<'_>, key: &str) -> Option<String> {
    [format!("#{key}"), key.to_string()].into_iter().find_map(|k| ctx.i18n(&k).filter(|s| !s.is_empty() && *s != k))
}

fn name(ctx: &StableClient<'_>, id: &str) -> String {
    text(ctx, &format!("asset/base/text/champion?description.{id}.name"))
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
    let lang = lang_of(&text(ctx, "asset/base/text/champion?skill_name.league_akshan.skill1").unwrap_or_default());
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
    fn the_screen_is_looked_at_every_60_ticks_and_on_a_new_sim() {
        assert!(due(None, 0));
        assert!(!due(Some(0), 1));
        assert!(!due(Some(0), SCREEN_EVERY - 1));
        assert!(due(Some(0), SCREEN_EVERY));
        // the tick went back: another sim on the same hook
        assert!(due(Some(30_000), 5));
    }

    #[test]
    fn another_match_on_screen_hides_the_last_ones_banner() {
        // 2026-10-30: set 1 (with Akshan) revived at 30513, set 2 (without) reached 8:28 on screen
        let all = vec![Banner { m: 738, s: 1, tick: 30_513, akshan: "league_akshan".into(), ally: "league_jax".into() }];
        assert!(showing(&all, Some((738, 1)), 30_513).is_some());
        assert!(showing(&all, Some((738, 2)), 30_513).is_none());
    }

    #[test]
    fn the_language_follows_the_skill_name() {
        // league/text/champion.i18n's skill_name.league_akshan.skill1 in each language
        assert_eq!(lang_of("去而复还"), Lang::Hans);
        assert_eq!(lang_of("復仇迴力鏢"), Lang::Hant);
        assert_eq!(lang_of("복수의 부메랑"), Lang::Ko);
        assert_eq!(lang_of("報復のブーメラン"), Lang::Ja);
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
