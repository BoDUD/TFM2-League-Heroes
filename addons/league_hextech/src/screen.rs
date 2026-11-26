//! 屏幕上的海克斯（客户端扩展的 post_render 里画，只读 [`super::feed`]，按屏幕上的比赛时钟取到那一刻）：
//!
//! - 开局对阵面板：画面中间，10 个人开局拿到的海克斯（蓝色方左、红色方右，按分路排），8 秒后淡出；
//! - 之后每次选择右边一条提示（谁、几级、拿了哪张、效果、三张候选和刷新掉的），最多同时 4 条，多了排队；
//! - 玩家栏每个头像右边一列小色块（每个海克斯一块，银 / 金 / 棱彩的颜色），鼠标放在头像上看这个英雄的全部海克斯。
//!
//! 位置：大小龙的公告在画面中上方（高度 16% 起）、它的框在左上角，所以面板从 27% 往下，提示在右边 30% 往下。第一次画在哪
//! 记一行日志（`DRAW`），游戏里看着不对再挪。只在比赛画面上画（大小龙 screen.rs 的判断：游戏说的界面不是经营界面，
//! 比赛时钟的标签这一帧就在屏幕上）。

use std::sync::Mutex;
use std::time::Instant;

use mod_api_stable::*;

use super::augments::{Tier, AUGS};
use super::feed::{self, Event};
use super::words::{self, Lang};
use super::{counted, kit, settings, wlog};

pub const UI: &str = "UI";
pub const FONT: &str = "asset/base/font/set/regular";
pub const BOLD: &str = "asset/base/font/set/bold";

/// 档位的颜色（0xRRGGBB00，透明度另加）。
pub fn tier_colour(t: Tier) -> u32 {
    match t {
        Tier::Silver => 0xc8_d2_dc_00,
        Tier::Gold => 0xf2_c1_4e_00,
        Tier::Prismatic => 0xd3_8c_ff_00,
    }
}

/// 一个海克斯自己那一档的颜色（一般就是这一次的档；整档发空了借来的卡按它自己的档）。
pub fn aug_colour(aug: u16) -> u32 {
    tier_colour(AUGS[aug as usize].tier)
}

/// 两队的颜色（游戏顶栏两边的色条）。
pub const BLUE: u32 = 0x5b_73_ff_00;
pub const RED: u32 = 0xf0_52_62_00;

/// 开局面板放多久、每条提示放多久（tick，60 一秒），最后多久淡出；同时最多几条提示。
pub const OPEN_T: usize = 480;
pub const TOAST_T: usize = 240;
pub const FADE_T: usize = 40;
pub const TOAST_SLOTS: usize = 2;

/// 屏幕上的一块 (x, y, 宽, 高)。
pub type Rect = (f32, f32, f32, f32);

// ===================== 字 =====================

#[allow(clippy::too_many_arguments)]
pub fn draw_text_in(ctx: &mut StableClient<'_>, text: &str, font: &str, r: Rect, z: i32, size: f32, colour: u32,
                    align: TextAlignXV1) {
    if !ctx.draw_text(UI, text, font, r, z, size, colour, align, TextAlignYV1::Center) && font != FONT {
        ctx.draw_text(UI, text, FONT, r, z, size, colour, align, TextAlignYV1::Center);
    }
}

/// 一行字，先画一道黑影（透明度 `a`）。
#[allow(clippy::too_many_arguments)]
pub fn shadowed(ctx: &mut StableClient<'_>, text: &str, font: &str, r: Rect, z: i32, size: f32, a: u32, colour: u32,
                align: TextAlignXV1) {
    let d = (size * 0.06).max(1.2);
    draw_text_in(ctx, text, font, (r.0 + d, r.1 + d, r.2, r.3), z, size, a * 200 / 255, align);
    draw_text_in(ctx, text, font, r, z + 1, size, colour | a, align);
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

/// 淡入淡出：前 10 tick 升上来，最后 FADE_T tick 线性降到 0。
pub fn alpha(age: usize, show: usize) -> u32 {
    let left = show.saturating_sub(age);
    let a = if left >= FADE_T { 255 } else { 255 * left / FADE_T };
    (a.min(255 * (age + 1) / 10)).min(255) as u32
}

/// 游戏的一条文字（先带 `#` 查，再不带查，查到空的或原样的键都不算）。
fn text(ctx: &StableClient<'_>, key: &str) -> Option<String> {
    [format!("#{key}"), key.to_string()].into_iter().find_map(|k| ctx.i18n(&k).filter(|s| !s.is_empty() && *s != k))
}

pub fn hero_name(ctx: &StableClient<'_>, id: &str) -> String {
    text(ctx, &format!("asset/base/text/champion?description.{id}.name"))
        .unwrap_or_else(|| id.trim_start_matches("league_").to_string())
}

/// 游戏的语言（BP 面板用；认一次记着，换语言要重开游戏）。
pub fn game_lang(ctx: &StableClient<'_>) -> Lang {
    static ONCE: Mutex<Option<Lang>> = Mutex::new(None);
    if let Some(l) = ONCE.lock().ok().and_then(|l| *l) {
        return l;
    }
    let l = lang(ctx, u64::MAX, u64::MAX);
    if let Ok(mut o) = ONCE.lock() {
        *o = Some(l);
    }
    l
}

/// 游戏自己的几个英雄：它们的名字和技能名分得出简体、繁体。
const NATIVE_SAMPLE: [&str; 4] = ["ghost", "necromancer", "shield_bearer", "hypnotist"];

/// 这一场用的语言（换了一场再认一次）。
static LANG: Mutex<Option<((u64, u64), Lang)>> = Mutex::new(None);

fn lang(ctx: &StableClient<'_>, m: u64, s: u64) -> Lang {
    if let Ok(l) = LANG.lock() {
        if let Some((key, lang)) = *l {
            if key == (m, s) {
                return lang;
            }
        }
    }
    let mut sample = String::new();
    for id in NATIVE_SAMPLE {
        for k in ["description.{id}.name", "skill_name.{id}.skill1", "skill_name.{id}.skill2"] {
            if let Some(t) = text(ctx, &format!("asset/base/text/champion?{}", k.replace("{id}", id))) {
                sample.push_str(&t);
            }
        }
    }
    let lang = words::lang_of(&sample);
    if let Ok(mut l) = LANG.lock() {
        *l = Some(((m, s), lang));
    }
    lang
}

// ===================== 什么时候画 =====================

/// 节点和它的每一层父节点都显示着。
fn shown(ctx: &StableClient<'_>, path: &str) -> bool {
    let parts: Vec<&str> = path.split('.').collect();
    (1..=parts.len()).all(|n| ctx.ui_visible(&parts[..n].join(".")) == Some(true))
}

fn rect_of(ctx: &StableClient<'_>, path: &str) -> Option<Rect> {
    shown(ctx, path).then(|| ctx.ui_node_rect(path)).flatten().filter(|r| r.2 > 1.0 && r.3 > 1.0)
}

/// 认得出不是比赛画面的界面（经营主界面、阵容、入场、结算、休息室、庆典、颁奖、局间反馈）。
pub fn off_match(scene: Option<ClientSceneKindV1>) -> bool {
    use ClientSceneKindV1::*;
    match scene {
        Some(Main | Lineup | StadiumEntrance | MatchResult | LockerRoom | ChampionshipCelebration | AwardsCeremony | SetFeedback) => true,
        Some(Match | InGame | Prologue | PrologueFirst | TutorialMorgad | TutorialSerpen | Tutorial5v5) | None => false,
    }
}

pub fn match_screen(in_game: bool, scene: Option<ClientSceneKindV1>, clock_shown: bool) -> bool {
    in_game && clock_shown && !off_match(scene)
}

fn match_screen_now(ctx: &StableClient<'_>) -> bool {
    let in_game = ctx.is_in_game();
    let scene = in_game.then(|| ctx.client_scene_kind()).flatten();
    match_screen(in_game, scene, in_game && shown(ctx, game_places::clock::CLOCK_PATH))
}

// ===================== 排队和位置（不碰画面，测得了） =====================

/// 提示排队：按发生的 tick，`TOAST_SLOTS` 条道，一条道上前一条放完下一条才上。-> (开始的 tick, 在 `ev` 里第几条)
pub fn schedule(ev: &[Event]) -> Vec<(usize, usize)> {
    let mut idx: Vec<usize> = (0..ev.len()).filter(|&i| ev[i].pick.screen > 0).collect();
    idx.sort_by_key(|&i| ev[i].tick);
    let mut free = [0usize; TOAST_SLOTS];
    idx.into_iter()
        .map(|i| {
            let slot = (0..TOAST_SLOTS).min_by_key(|&k| free[k]).unwrap_or(0);
            let start = ev[i].tick.max(free[slot]);
            free[slot] = start + TOAST_T;
            (start, i)
        })
        .collect()
}

/// 屏幕时钟 `t` 时在放的提示：(在 `ev` 里第几条, 放了几 tick)，先开始的在上面。
pub fn toasts_at(ev: &[Event], t: usize) -> Vec<(usize, usize)> {
    let mut v: Vec<(usize, usize, usize)> = schedule(ev)
        .into_iter()
        .filter(|&(start, _)| start <= t && t < start + TOAST_T)
        .map(|(start, i)| (start, i, t - start))
        .collect();
    v.sort();
    v.into_iter().map(|(_, i, age)| (i, age)).take(TOAST_SLOTS).collect()
}

/// 开局面板：(开局的那几条, 放了几 tick)，没有或放完了：None。
pub fn opening_at(ev: &[Event], t: usize) -> Option<(Vec<usize>, usize)> {
    let picks: Vec<usize> = (0..ev.len()).filter(|&i| ev[i].pick.screen == 0).collect();
    let start = picks.iter().map(|&i| ev[i].tick).min()?;
    (start <= t && t < start + OPEN_T).then(|| (picks, t - start))
}

/// 字号（按画面高度）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Sizes {
    pub title: f32,
    pub line: f32,
    pub small: f32,
}

pub fn sizes(h: f32) -> Sizes {
    Sizes { title: (h * 0.034).max(18.0), line: (h * 0.022).max(13.0), small: (h * 0.017).max(11.0) }
}

/// 开局面板那一块。
pub fn opening_rect((w, h): (f32, f32)) -> Rect {
    let s = sizes(h);
    let pw = (w * 0.64).min(1240.0);
    let ph = s.title * 1.6 + s.small * 1.6 + 5.0 * (s.line * 1.4 + s.small * 1.4 + 6.0) + 16.0;
    ((w - pw) / 2.0, h * 0.27, pw, ph)
}

/// 第 `k` 条在放的提示那一块。宽屏布局（玩家 2026-11-26 的截图；0.1.0 的日志：击杀记录在右边 x 1320 起、y 127 往下，不是布局
/// 文件里的左边）：左边——时间按钮（y 64–100）和大小龙的框（到 y 140）下面、蓝色方选手栏（y 383 起）上面只有地图——从 y 145 往下
/// 两条。普通布局右半边是数据面板，放在战场左上角、时间按钮下面，击杀记录（x 378 起）左边。
pub fn toast_rect((w, h): (f32, f32), k: usize, wide: bool) -> Rect {
    let s = sizes(h);
    let u = h / 1080.0;
    let th = s.line * 1.5 + s.small * 1.45 * 2.0 + 8.0;
    if wide {
        let tw = (w * 0.24).max(300.0).min(w * 0.45);
        (10.0 * u, 145.0 * u + k as f32 * (th + 6.0), tw, th)
    } else {
        (19.0 * u, 108.0 * u + k as f32 * (th + 6.0), 350.0 * u, th)
    }
}

/// 选手栏头像旁边那一列小色块的第 `k` 块：竖着贴在头像朝按钮中间的那一边（头像和名字之间本来空着 10 像素；蓝色方头像在左、
/// 色块在它右边，红色方反过来）。
pub fn badge_rect(icon: Rect, bar: Rect, k: usize) -> Rect {
    let (x, y, w, h) = icon;
    let sq = (h * 0.2).max(4.0);
    let gap = (h * 0.05).max(1.0);
    let right = icon.0 + icon.2 / 2.0 <= bar.0 + bar.2 / 2.0;
    let bx = if right { x + w + gap } else { x - gap - sq };
    (bx, y + k as f32 * (sq + gap), sq, sq)
}

/// 说明框贴在游戏的英雄大面板旁边：左边放得下放左边，不然放右边；上沿和它对齐，不出画面，也不压到它。
pub fn beside(panel: Rect, (w, h): (f32, f32), ui: (f32, f32)) -> (f32, f32) {
    let x = if panel.0 - w - 8.0 >= 4.0 { panel.0 - w - 8.0 } else { (panel.0 + panel.2 + 8.0).min(ui.0 - w - 4.0) };
    (x, panel.1.min(ui.1 - h - 4.0).max(4.0))
}

/// 说明框放在选手栏朝屏幕中间的那一侧（左边的栏放它右边，右边的栏放它左边），上沿对齐。
pub fn by_bar(bar: Rect, (w, h): (f32, f32), ui: (f32, f32)) -> (f32, f32) {
    let left_half = bar.0 + bar.2 / 2.0 < ui.0 / 2.0;
    let x = if left_half { bar.0 + bar.2 + 8.0 } else { bar.0 - w - 8.0 };
    (x.clamp(4.0, (ui.0 - w - 4.0).max(4.0)), bar.1.min(ui.1 - h - 4.0).max(4.0))
}

/// 游戏大面板名字标签里的文字引用 `#asset/base/text/champion?description.<英雄>.name` -> 英雄 id（league.dll stacks.rs 一样读）。
pub fn champion_of(text: &str) -> Option<&str> {
    text.trim().strip_prefix("#asset/base/text/champion?description.")?.strip_suffix(".name")
}

// ===================== 画 =====================

/// 第一次画在哪（日志用）：(比赛, 局, 哪一种)
static DRAWN: Mutex<Vec<(u64, u64, &'static str)>> = Mutex::new(Vec::new());

fn first_time(key: (u64, u64, &'static str)) -> bool {
    let Ok(mut l) = DRAWN.lock() else { return false };
    if l.contains(&key) {
        return false;
    }
    l.push(key);
    if l.len() > 256 {
        l.drain(..128);
    }
    true
}

pub fn draw(ctx: &mut StableClient<'_>) {
    if !match_screen_now(ctx) {
        return;
    }
    let Some(t) = game_places::clock::screen_tick() else { return };
    let Some((m, s)) = feed::current() else { return };
    // 比赛在屏幕上打完了（结算画面还算在比赛里、时钟也还读得到）：不画
    if feed::ended_at(m, s).is_some_and(|end| t > end + 60) {
        return;
    }
    // 战场上的触发特效（画在比赛世界里，在界面下面）
    super::fx::draw(ctx, m, s, t);
    let ev = feed::events(m, s);
    if ev.is_empty() {
        return;
    }
    let Some(ui) = ctx.draw_map_size(UI).filter(|u| u.0 > 0.0 && u.1 > 0.0) else { return };
    let lang = lang(ctx, m, s);
    let set = settings::get();
    badges(ctx, &ev, t, lang, ui, m, s, &set);
    if set.show {
        // 开局对阵面板 0.3.3 起默认不画（用户：「游戏内开局海克斯那个显示提示不需要 太占屏幕了」），settings.ini 的 show_opening
        if let Some((picks, age)) = opening_at(&ev, t).filter(|_| set.opening) {
            opening(ctx, &ev, &picks, age, lang, ui, m, s);
        }
        for (k, (i, age)) in toasts_at(&ev, t).into_iter().enumerate() {
            toast(ctx, &ev[i], k, age, lang, ui, m, s);
        }
    }
}

fn panel_bg(ctx: &mut StableClient<'_>, r: Rect, z: i32, a: u32, edge: u32) {
    ctx.draw_rect(UI, r.0, r.1, r.2, r.3, z, 8.0, 0x10_14_22_00 | (a * 225 / 255));
    ctx.draw_rect(UI, r.0, r.1, r.2, 3.0, z + 1, 0.0, edge | (a * 200 / 255));
}

/// 开局对阵面板。
#[allow(clippy::too_many_arguments)]
fn opening(ctx: &mut StableClient<'_>, ev: &[Event], picks: &[usize], age: usize, lang: Lang, ui: (f32, f32), m: u64,
           s: u64) {
    let a = alpha(age, OPEN_T);
    if a == 0 {
        return;
    }
    let r = opening_rect(ui);
    let sz = sizes(ui.1);
    let tier = ev[picks[0]].pick.tier;
    let edge = tier_colour(tier);
    if first_time((m, s, "opening")) {
        if let Some(k) = counted("draw") {
            wlog(format!("DRAW m={m} s={s} opening panel at {:.0},{:.0} {:.0}x{:.0} (UI {:.0}x{:.0}, {lang:?}, {} picks) #{k}",
                         r.0, r.1, r.2, r.3, ui.0, ui.1, picks.len()));
        }
    }
    panel_bg(ctx, r, 920, a, edge);
    let title = words::opening_title(lang, tier);
    let ts = fit(&title, r.2, sz.title, sz.title * 0.6);
    shadowed(ctx, &title, BOLD, (r.0, r.1 + 6.0, r.2, sz.title * 1.4), 922, ts, a, edge, TextAlignXV1::Center);
    let next = words::opening_next(lang, settings::get().levels);
    shadowed(ctx, &next, FONT, (r.0, r.1 + 6.0 + sz.title * 1.4, r.2, sz.small * 1.5), 922, sz.small, a,
             0xd8_d4_c8_00, TextAlignXV1::Center);
    let top = r.1 + 10.0 + sz.title * 1.4 + sz.small * 1.6;
    let col_w = (r.2 - 36.0) / 2.0;
    let row_h = sz.line * 1.4 + sz.small * 1.4 + 6.0;
    for team in 0..2 {
        let mut rows: Vec<&Event> = picks.iter().map(|&i| &ev[i]).filter(|e| e.pick.team == team).collect();
        rows.sort_by_key(|e| e.pick.lane);
        let x = r.0 + 12.0 + team as f32 * (col_w + 12.0);
        let side_c = if team == 0 { BLUE } else { RED };
        for (n, e) in rows.iter().take(5).enumerate() {
            let y = top + n as f32 * row_h;
            ctx.draw_rect(UI, x, y + 2.0, 4.0, row_h - 6.0, 923, 1.0, side_c | a);
            let hero = hero_name(ctx, &e.pick.hero);
            let line = format!("{hero} · {}", words::tagged(lang, e.pick.chosen as usize));
            let ls = fit(&line, col_w - 14.0, sz.line, sz.line * 0.6);
            shadowed(ctx, &line, BOLD, (x + 10.0, y, col_w - 14.0, sz.line * 1.4), 924, ls,
                     a, aug_colour(e.pick.chosen), TextAlignXV1::Left);
            let d = words::brief(lang, e.pick.chosen as usize);
            let ds = fit(&d, col_w - 14.0, sz.small, sz.small * 0.6);
            shadowed(ctx, &d, FONT, (x + 10.0, y + sz.line * 1.35, col_w - 14.0, sz.small * 1.4), 924, ds, a,
                     0xe6_e0_d2_00, TextAlignXV1::Left);
        }
    }
}

/// 一条选择的提示。
#[allow(clippy::too_many_arguments)]
fn toast(ctx: &mut StableClient<'_>, e: &Event, k: usize, age: usize, lang: Lang, ui: (f32, f32), m: u64, s: u64) {
    let a = alpha(age, TOAST_T);
    if a == 0 {
        return;
    }
    let r = toast_rect(ui, k, ctx.ui_visible("ingame.wide_data") == Some(true));
    let sz = sizes(ui.1);
    let p = &e.pick;
    let edge = aug_colour(p.chosen);
    if first_time((m, s, "toast")) {
        if let Some(n) = counted("draw") {
            wlog(format!("DRAW m={m} s={s} first toast at {:.0},{:.0} {:.0}x{:.0} (UI {:.0}x{:.0}, {lang:?}; kill log {:?}, \
                          header {:?}) #{n}",
                         r.0, r.1, r.2, r.3, ui.0, ui.1, rect_of(ctx, "ingame.kills"), rect_of(ctx, "ingame.header")));
        }
    }
    ctx.draw_rect(UI, r.0, r.1, r.2, r.3, 920, r.3 * 0.18, 0x14_12_10_00 | (a * 205 / 255));
    let side_c = if p.team == 0 { BLUE } else { RED };
    ctx.draw_rect(UI, r.0, r.1 + 3.0, 5.0, r.3 - 6.0, 921, 2.0, side_c | a);
    ctx.draw_rect(UI, r.0 + r.2 - 5.0, r.1 + 3.0, 5.0, r.3 - 6.0, 921, 2.0, edge | a);
    let inner = (r.0 + 12.0, r.2 - 24.0);
    let hero = hero_name(ctx, &p.hero);
    let title = format!("{}{}", words::toast_title(lang, p.team, &hero, p.level, p.chosen as usize), words::by_note(lang, p.by));
    let ts = fit(&title, inner.1, sz.line, sz.line * 0.55);
    shadowed(ctx, &title, BOLD, (inner.0, r.1 + 3.0, inner.1, sz.line * 1.45), 922, ts, a, edge, TextAlignXV1::Left);
    let d = words::brief(lang, p.chosen as usize);
    let ds = fit(&d, inner.1, sz.small, sz.small * 0.6);
    shadowed(ctx, &d, FONT, (inner.0, r.1 + 3.0 + sz.line * 1.4, inner.1, sz.small * 1.4), 922, ds, a, 0xf0_ea_dc_00,
             TextAlignXV1::Left);
    let c = words::candidates(lang, p.cards, p.first);
    let cs = fit(&c, inner.1, sz.small * 0.92, sz.small * 0.55);
    shadowed(ctx, &c, FONT, (inner.0, r.1 + 3.0 + sz.line * 1.4 + sz.small * 1.4, inner.1, sz.small * 1.4), 922, cs, a,
             0xa8_a4_9c_00, TextAlignXV1::Left);
}

/// 两侧的选手栏（宽屏布局、普通布局；游戏的 ingame_component/wide_camera_info、camera_info）：一行一条分路，每行蓝、红两个
/// 按钮，按钮里 `icon` 是 40x40 的英雄头像、`text` 是「Lv.7 名字 (F1)」、下面一条血条。
const BARS: [&str; 2] = ["ingame.wide_data.camera_buttons", "ingame.center_data.camera_buttons"];
const SIDES: [(&str, usize); 2] = [("blue_player", 0), ("red_player", 1)];
/// 游戏的英雄大面板（点头像、点战场上的英雄打开；asset/base/ui/layout/champion_tooltip 生成的节点）。
const TIP: &str = "champion_info_tooltip";

/// 游戏大面板的路径（找到一次记着，没了再找：先看比赛画面的根下面，再翻一遍每个根；league.dll stacks.rs 的找法）。
fn big_panel(ctx: &StableClient<'_>) -> Option<String> {
    static AT: Mutex<Option<String>> = Mutex::new(None);
    let mut at = AT.lock().ok()?;
    if !at.as_ref().is_some_and(|p| ctx.ui_exists(p)) {
        *at = std::iter::once("ingame".to_string())
            .chain(ctx.ui_child_names(""))
            .map(|r| format!("{r}.{TIP}"))
            .find(|p| ctx.ui_exists(p));
    }
    at.clone()
}

/// 选手栏头像旁边的小色块（一个海克斯一块）；游戏的英雄大面板开着时把那个英雄的海克斯贴在它旁边，没开、鼠标停在选手栏上时
/// 贴在那条栏旁边。
#[allow(clippy::too_many_arguments)]
fn badges(ctx: &mut StableClient<'_>, ev: &[Event], t: usize, lang: Lang, ui: (f32, f32), m: u64, s: u64,
          set: &settings::Settings) {
    let cursor = cursor_ui(ui);
    let mut hovered: Option<(Rect, String)> = None;
    for bars in BARS {
        if !shown(ctx, bars) {
            continue;
        }
        for (lane, row) in ctx.ui_child_names(bars).iter().enumerate().take(8) {
            for (sidename, team) in SIDES {
                let got: Vec<&Event> =
                    ev.iter().filter(|e| e.tick <= t && e.pick.team == team && e.pick.lane as usize == lane).collect();
                let Some(first) = got.first() else { continue };
                let button = format!("{bars}.{row}.{sidename}");
                let (Some(bar), Some(icon)) = (rect_of(ctx, &button), rect_of(ctx, &format!("{button}.icon"))) else { continue };
                if first_time((m, s, "badges")) {
                    if let Some(k) = counted("draw") {
                        wlog(format!("DRAW m={m} s={s} badges beside {button}.icon at {:.0},{:.0} {:.0}x{:.0} (bar {:.0},{:.0} \
                                      {:.0}x{:.0}, UI {:.0}x{:.0}) #{k}",
                                     icon.0, icon.1, icon.2, icon.3, bar.0, bar.1, bar.2, bar.3, ui.0, ui.1));
                    }
                }
                for (k, e) in got.iter().take(4).enumerate() {
                    let b = badge_rect(icon, bar, k);
                    ctx.draw_rect(UI, b.0 - 1.0, b.1 - 1.0, b.2 + 2.0, b.3 + 2.0, 930, 1.5, 0x08_0a_10_e6);
                    ctx.draw_rect(UI, b.0, b.1, b.2, b.3, 931, 1.0, aug_colour(e.pick.chosen) | 0xf0);
                }
                if cursor.is_some_and(|(cx, cy)| cx >= bar.0 && cx < bar.0 + bar.2 && cy >= bar.1 && cy < bar.1 + bar.3) {
                    hovered = Some((bar, first.pick.hero.clone()));
                }
            }
        }
    }
    // 游戏的大面板开着、上面是这一场有海克斯的英雄：贴在它旁边（不压到它）
    if let Some(tip) = big_panel(ctx).filter(|p| ctx.ui_visible(p) == Some(true)) {
        let hero = ctx.ui_text(&format!("{tip}.header.name")).and_then(|t| champion_of(&t).map(str::to_string));
        if let (Some(panel), Some(hero)) = (rect_of(ctx, &tip), hero) {
            let got: Vec<&Event> = ev.iter().filter(|e| e.tick <= t && e.pick.hero == hero).collect();
            if !got.is_empty() {
                if first_time((m, s, "dock")) {
                    if let Some(k) = counted("draw") {
                        wlog(format!("DRAW m={m} s={s} augments docked beside the game's {tip} at {:.0},{:.0} {:.0}x{:.0} #{k}",
                                     panel.0, panel.1, panel.2, panel.3));
                    }
                }
                tooltip(ctx, &got, |size| beside(panel, size, ui), lang, ui, set);
                return;
            }
        }
    }
    if let Some((bar, hero)) = hovered {
        let got: Vec<&Event> = ev.iter().filter(|e| e.tick <= t && e.pick.hero == hero).collect();
        tooltip(ctx, &got, |size| by_bar(bar, size, ui), lang, ui, set);
    }
}

/// 一个英雄拿到的全部海克斯（还没到的几次写几级再选）：宽高按字算，位置由 `place` 按宽高定。
fn tooltip(ctx: &mut StableClient<'_>, got: &[&Event], place: impl Fn((f32, f32)) -> (f32, f32), lang: Lang,
           ui: (f32, f32), set: &settings::Settings) {
    let Some(first) = got.first() else { return };
    let sz = sizes(ui.1);
    let hero = hero_name(ctx, &first.pick.hero);
    let pending: Vec<usize> = (got.len()..4).filter_map(|k| set.levels.get(k - 1).copied()).collect();
    let title = words::tip_title(lang, &hero);
    let pad = (sz.small * 0.8).max(8.0);
    // 宽：最长的那一行（标题、每个海克斯的名字和效果、还没到的几次）
    let mut widest = em(&title) * sz.line;
    for e in got {
        let p = &e.pick;
        widest = widest.max(em(&format!("{}{}", words::tagged(lang, p.chosen as usize), words::by_note(lang, p.by))) * sz.line);
        widest = widest.max(em(words::desc(lang, p.chosen as usize)) * sz.small);
    }
    let w = (widest + 2.0 * pad).clamp(200.0, (ui.0 * 0.32).max(200.0));
    // 放不下一行的说明（触发类）折成几行
    let descs: Vec<Vec<String>> = got.iter()
        .map(|e| words::wrap(words::desc(lang, e.pick.chosen as usize), (w - 2.0 * pad) * 0.97 / sz.small))
        .collect();
    let extra: usize = descs.iter().map(|d| d.len().saturating_sub(1)).sum();
    let rows = got.len() + pending.len();
    let h = sz.line * 1.5 + rows as f32 * (sz.line * 1.3 + sz.small * 1.3) - pending.len() as f32 * sz.line * 0.9 + pad * 1.5
        + extra as f32 * sz.small * 1.2;
    let (x, y) = place((w, h));
    ctx.draw_rect(UI, x, y, w, h, 940, 6.0, 0x0c_0e_16_f6);
    ctx.draw_rect(UI, x, y, w, 3.0, 941, 0.0, 0xf2_c1_4e_ff);
    shadowed(ctx, &title, BOLD, (x + pad, y + pad * 0.5, w - 2.0 * pad, sz.line * 1.4), 942, fit(&title, w - 2.0 * pad, sz.line, 9.0),
             0xff, 0xf4_ee_dc_00, TextAlignXV1::Left);
    let mut yy = y + pad * 0.5 + sz.line * 1.5;
    for (e, lines) in got.iter().zip(&descs) {
        let p = &e.pick;
        let line = format!("{}{}", words::tagged(lang, p.chosen as usize), words::by_note(lang, p.by));
        shadowed(ctx, &line, BOLD, (x + pad, yy, w - 2.0 * pad, sz.line * 1.3), 942, fit(&line, w - 2.0 * pad, sz.line, 9.0), 0xff,
                 aug_colour(p.chosen), TextAlignXV1::Left);
        for (i, d) in lines.iter().enumerate() {
            shadowed(ctx, d, FONT, (x + pad, yy + sz.line * 1.25 + i as f32 * sz.small * 1.2, w - 2.0 * pad, sz.small * 1.3),
                     942, fit(d, w - 2.0 * pad, sz.small, 8.0), 0xff, 0xe0_da_cc_00, TextAlignXV1::Left);
        }
        yy += sz.line * 1.3 + sz.small * 1.3 + lines.len().saturating_sub(1) as f32 * sz.small * 1.2;
    }
    for level in pending {
        let line = words::tip_pending(lang, level);
        shadowed(ctx, &line, FONT, (x + pad, yy, w - 2.0 * pad, sz.small * 1.3), 942, sz.small, 0xff, 0x90_8c_84_00,
                 TextAlignXV1::Left);
        yy += sz.small * 1.3 + sz.line * 0.4;
    }
}

/// 鼠标在界面坐标里的位置（游戏窗口在最前面时）：稳定接口没有鼠标位置，用 Win32 取光标在窗口里的位置再按界面大小换算
/// （大小龙 screen.rs 的做法）。
#[cfg(windows)]
pub fn cursor_ui(ui: (f32, f32)) -> Option<(f32, f32)> {
    #[repr(C)]
    struct Point {
        x: i32,
        y: i32,
    }
    #[repr(C)]
    struct WinRect {
        l: i32,
        t: i32,
        r: i32,
        b: i32,
    }
    #[link(name = "user32")]
    extern "system" {
        fn GetCursorPos(p: *mut Point) -> i32;
        fn GetForegroundWindow() -> isize;
        fn GetWindowThreadProcessId(h: isize, pid: *mut u32) -> u32;
        fn ScreenToClient(h: isize, p: *mut Point) -> i32;
        fn GetClientRect(h: isize, r: *mut WinRect) -> i32;
    }
    #[link(name = "kernel32")]
    extern "system" {
        fn GetCurrentProcessId() -> u32;
    }
    unsafe {
        let hwnd = GetForegroundWindow();
        let mut pid = 0u32;
        if hwnd == 0 || GetWindowThreadProcessId(hwnd, &mut pid) == 0 || pid != GetCurrentProcessId() {
            return None;
        }
        let mut p = Point { x: 0, y: 0 };
        let mut r = WinRect { l: 0, t: 0, r: 0, b: 0 };
        if GetCursorPos(&mut p) == 0 || ScreenToClient(hwnd, &mut p) == 0 || GetClientRect(hwnd, &mut r) == 0 {
            return None;
        }
        let (cw, ch) = ((r.r - r.l) as f32, (r.b - r.t) as f32);
        (cw > 0.0 && ch > 0.0).then(|| (p.x as f32 * ui.0 / cw, p.y as f32 * ui.1 / ch))
    }
}

#[cfg(not(windows))]
pub fn cursor_ui(_ui: (f32, f32)) -> Option<(f32, f32)> {
    None
}

// ===================== 客户端扩展 =====================

/// 上次试着从客户端填英雄特性表的时候（没填上的话每 2 秒再试一次）。
static KIT_TRY: Mutex<Option<Instant>> = Mutex::new(None);

/// league_hextech.dll 的客户端扩展：喂屏幕时钟、进了生涯填一次英雄特性表、画。
pub struct Overlay;

impl StableExtension for Overlay {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        if !ctx.is_in_game() || off_match(ctx.client_scene_kind()) {
            game_places::clock::observe(false, None);
        } else {
            let path = game_places::clock::CLOCK_PATH;
            let text = shown(ctx, path).then(|| ctx.ui_text(path)).flatten();
            game_places::clock::observe(true, text.as_deref());
        }
        if !kit::filled() && ctx.is_in_game() {
            let due = KIT_TRY.lock().map(|mut l| {
                let go = l.is_none_or(|at| at.elapsed().as_secs() >= 2);
                if go {
                    *l = Some(Instant::now());
                }
                go
            });
            if due.unwrap_or(false) {
                let n = kit::fill_from_client(ctx, ctx.champion_names());
                if n > 0 {
                    wlog(format!("KIT {n} champions' classes and tags read in the career (client; the game's own ones)"));
                }
            }
        }
        // BP 画面上的海克斯面板（玩家给自己的队伍选）
        super::bp::update(ctx);
        save_sync(ctx);
        // 身体变大的显示钩子（本包是高清帧引擎的主时）：第一帧挂上，之后被跳过就接回来（要上面喂过的屏幕时钟）
        game_places::hook::tick();
    }

    fn post_render(&self, ctx: &mut StableClient<'_>) {
        draw(ctx);
        super::bp::draw(ctx);
    }
}

/// 存档里最多留几局玩家选的（最早的先删）。
const SAVE_MOST: usize = 300;

/// 存档：屏幕上那一场认过的玩家记录写进存档（重开游戏看回放用；存档写不了的时候等下一帧）；进了生涯读一次存档里的。
fn save_sync(ctx: &mut StableClient<'_>) {
    static IN: Mutex<bool> = Mutex::new(false);
    let in_game = ctx.is_in_game();
    let entered = IN.lock().map(|mut was| std::mem::replace(&mut *was, in_game) != in_game && in_game).unwrap_or(false);
    if entered {
        let mut keys: Vec<(u64, u64, String)> = ctx
            .save_keys()
            .into_iter()
            .filter_map(|k| {
                let rest = k.strip_prefix(super::pending::SAVE_PREFIX)?;
                let (m, s) = rest.split_once(':')?;
                Some((m.parse().ok()?, s.parse().ok()?, k.clone()))
            })
            .collect();
        keys.sort();
        let mut read = 0;
        for (i, (m, s, k)) in keys.iter().enumerate() {
            if keys.len() > SAVE_MOST && i < keys.len() - SAVE_MOST {
                if ctx.save_can_write() {
                    ctx.save_remove_key(k);
                }
                continue;
            }
            let id = super::rules::splitmix(m.wrapping_mul(31).wrapping_add(*s));
            if let Some(r) = ctx.save_get_string(k).and_then(|t| super::pending::decode(&t, *m, *s, id)) {
                super::pending::restore(r);
                read += 1;
            }
        }
        if !keys.is_empty() {
            wlog(format!("SAVE {read} of {} pick-screen records read back from the save (for replays)", keys.len()));
        }
    }
    let recs = super::pending::take_unsaved();
    if recs.is_empty() {
        return;
    }
    if !ctx.save_can_write() {
        super::pending::unsave_again(&recs.iter().map(|r| r.id).collect::<Vec<_>>());
        return;
    }
    for r in recs {
        if let Some((m, s)) = r.bound {
            let ok = ctx.save_set_string(&super::pending::save_key(m, s), &super::pending::encode(&r));
            wlog(format!("SAVE record #{} of match {m} set {s} {}", r.id, if ok { "written to the save" } else { "NOT written" }));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::feed::Pick;

    fn ev(tick: usize, screen: u8, team: usize, lane: u8) -> Event {
        Event { m: 1, s: 1, tick, pick: Pick { team, lane, hero: "league_jinx".into(), screen, level: 6, tier: Tier::Gold,
                                                cards: [0, 1, 2], first: [0, 1, 2], chosen: 1, by: 0 } }
    }

    #[test]
    fn the_opening_panel_shows_the_starts_picks_for_eight_seconds() {
        let v: Vec<Event> = (0..10).map(|i| ev(30, 0, i / 5, (i % 5) as u8)).chain([ev(5000, 1, 0, 3)]).collect();
        assert!(opening_at(&v, 29).is_none());
        let (picks, age) = opening_at(&v, 100).expect("panel");
        assert_eq!((picks.len(), age), (10, 70));
        assert!(opening_at(&v, 30 + OPEN_T).is_none());
        assert!(opening_at(&[ev(5000, 1, 0, 3)], 5000).is_none());
    }

    #[test]
    fn toasts_queue_two_at_a_time() {
        // six picks at the same moment (the catch-up minute): two show, the others wait their turn
        let v: Vec<Event> = (0..6).map(|i| ev(36_000, 3, i % 2, (i % 5) as u8)).chain([ev(30, 0, 0, 0)]).collect();
        let now = toasts_at(&v, 36_010);
        assert_eq!(now.len(), TOAST_SLOTS);
        assert!(now.iter().all(|&(i, age)| v[i].pick.screen == 3 && age == 10));
        let later = toasts_at(&v, 36_000 + TOAST_T + 5);
        assert_eq!(later.len(), 2);
        assert_eq!(toasts_at(&v, 36_000 + 2 * TOAST_T + 5).len(), 2);
        assert!(toasts_at(&v, 36_000 + 3 * TOAST_T + 1).is_empty());
        // the opening picks never make toasts
        assert!(toasts_at(&v, 40).is_empty());
    }

    #[test]
    fn the_boxes_stay_on_screen_and_apart() {
        for ui in [(1920.0, 1080.0), (1280.0, 720.0), (2560.0, 1440.0)] {
            let o = opening_rect(ui);
            assert!(o.0 >= 0.0 && o.0 + o.2 <= ui.0 && o.1 >= ui.1 * 0.25 && o.1 + o.3 < ui.1 * 0.8, "{ui:?} {o:?}");
            let u = ui.1 / 1080.0;
            for wide in [true, false] {
                let mut last = 0.0;
                for k in 0..TOAST_SLOTS {
                    let r = toast_rect(ui, k, wide);
                    assert!(r.0 >= 0.0 && r.0 + r.2 <= ui.0 && r.1 >= last && r.1 >= 50.0 * u, "{ui:?} {k} {r:?}");
                    if wide {
                        // the left side: under the time controls and the dragons' box (y 140), above blue's bars (y 383),
                        // left of the kill log (x 1320 in the wide layout)
                        assert!(r.1 >= 140.0 * u && r.1 + r.3 <= 383.0 * u && r.0 + r.2 <= 1320.0 * u, "{ui:?} {k} {r:?}");
                    } else {
                        // under the time controls, left of the kill log
                        assert!(r.1 >= 100.0 * u && r.0 + r.2 <= 378.0 * u, "{ui:?} {k} {r:?}");
                    }
                    last = r.1 + r.3;
                }
            }
        }
    }

    /// The game's wide layout (the player's screenshot, 1920x1080): blue's bars at x 10-310, red's at 1610-1910, 60 high,
    /// the portrait 40x40 at 10,10 of a blue bar (at the right end of a red one), the name from x 60. The squares go in the
    /// gap between portrait and name, a column of four inside the portrait's height.
    #[test]
    fn the_squares_sit_between_portrait_and_name() {
        let blue_bar = (10.0, 383.0, 300.0, 60.0);
        let blue_icon = (20.0, 393.0, 40.0, 40.0);
        let red_bar = (1610.0, 383.0, 300.0, 60.0);
        let red_icon = (1860.0, 393.0, 40.0, 40.0);
        for k in 0..4 {
            let b = badge_rect(blue_icon, blue_bar, k);
            assert!(b.0 >= 60.0 && b.0 + b.2 <= 70.0, "blue {k} {b:?}: right of the portrait, left of the name");
            let r = badge_rect(red_icon, red_bar, k);
            assert!(r.0 + r.2 <= 1860.0 && r.0 >= 1850.0, "red {k} {r:?}: left of the portrait");
            for x in [b, r] {
                assert!(x.1 >= 393.0 && x.1 + x.3 <= 433.0 + 0.01, "{k} {x:?} within the portrait's height");
            }
        }
    }

    /// The player's screenshot: the game's champion panel at 915,530 600x540; ours goes left of it, never over it, and
    /// right of it when the left has no room. By a bar: toward the middle of the screen.
    #[test]
    fn the_augment_box_keeps_off_the_games_panel() {
        let ui = (1920.0, 1080.0);
        let panel = (915.0, 530.0, 600.0, 540.0);
        let size = (330.0, 230.0);
        let (x, y) = beside(panel, size, ui);
        assert!(x + size.0 <= panel.0 && x >= 0.0 && y == panel.1, "{x},{y}");
        let near_left = (100.0, 300.0, 600.0, 540.0);
        let (x, _) = beside(near_left, size, ui);
        assert!(x >= near_left.0 + near_left.2, "right of it: {x}");
        let tall = beside(panel, (330.0, 700.0), ui);
        assert!(tall.1 + 700.0 <= ui.1, "kept on screen: {tall:?}");
        let (x, _) = by_bar((10.0, 383.0, 300.0, 60.0), size, ui);
        assert!(x >= 310.0);
        let (x, _) = by_bar((1610.0, 383.0, 300.0, 60.0), size, ui);
        assert!(x + size.0 <= 1610.0);
        assert_eq!(champion_of("#asset/base/text/champion?description.league_gangplank.name"), Some("league_gangplank"));
        assert_eq!(champion_of("普朗克"), None);
    }

    #[test]
    fn nothing_is_drawn_off_the_match_screen() {
        use ClientSceneKindV1::*;
        for scene in [InGame, Match] {
            assert!(match_screen(true, Some(scene), true));
            assert!(!match_screen(true, Some(scene), false));
        }
        for scene in [Main, Lineup, StadiumEntrance, MatchResult, LockerRoom, ChampionshipCelebration, AwardsCeremony, SetFeedback] {
            assert!(!match_screen(true, Some(scene), true), "{scene:?}");
        }
        assert_eq!(ClientSceneKindV1::VARIANTS.len(), 15, "a new screen: is it a match? (off_match)");
        assert!(!match_screen(false, Some(InGame), true));
    }

    #[test]
    fn fades() {
        assert!(alpha(0, TOAST_T) < 60);
        assert_eq!(alpha(20, TOAST_T), 255);
        assert_eq!(alpha(TOAST_T, TOAST_T), 0);
        assert_eq!(em("海克斯"), 3.0);
        assert!(fit("一二三四五六七八九十", 100.0, 30.0, 5.0) < 30.0);
        // the tier colours differ and carry no alpha
        let c: Vec<u32> = Tier::ALL.iter().map(|&t| tier_colour(t)).collect();
        assert!(c[0] != c[1] && c[1] != c[2] && c.iter().all(|x| x & 0xff == 0));
        assert_eq!(AUGS.len(), 47);
    }
}
