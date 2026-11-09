//! 画面上的大小龙（客户端扩展的 post_render 里画）：公告（[`super::notice`]）、HUD 和玩家栏头像上拿着远古龙之力 / 纳什男爵之手
//! 的小圆点（[`super::hud`]）。
//!
//! 客户端扩展读不到对局里的实体，读的是 [`super::feed`]：比赛钩子在屏幕放的那场模拟里记下的事和状态记录，按屏幕上的比赛时钟
//! （`game_places::clock::screen_tick`）取到那一刻（league_eggs notice.rs 的做法）。文字按游戏的语言（简体、繁体，其他语言用英文，
//! [`super::words`]），英雄名按游戏自己的文字。
//!
//! 游戏每个 mod 只有一个客户端扩展槽：附加包合集里由 league_addons 的 `BundleClient` 调 [`draw`]（同时告诉它彩蛋的公告道上正放着
//! 什么，本包的挪开），单独的 league_dragons.dll 用 [`Overlay`]（也喂屏幕时钟）。
//!
//! 小龙按元素换模型、远古巨龙和纳什男爵的模型在 [`super::skin`]（显示钩子，同样按屏幕时钟读 `feed`）；这里只画公告和 HUD。

use std::sync::Mutex;

use mod_api_stable::*;

use super::rules::Element;
use super::{counted, feed, hud, notice, wlog, words};

pub const UI: &str = "UI";
pub const FONT: &str = "asset/base/font/set/regular";
pub const BOLD: &str = "asset/base/font/set/bold";

/// 两队的颜色（游戏顶栏两边的色条）和纳什男爵的紫（0xRRGGBB00，透明度另加）。
pub const BLUE: u32 = 0x5b_73_ff_00;
pub const RED: u32 = 0xf0_52_62_00;
pub const BARON: u32 = 0xb8_6c_ff_00;

/// 元素的颜色（0xRRGGBB00）：炼狱橙红、山脉土黄、海洋青、云端淡蓝白、海克斯电紫蓝、化学科技毒绿，远古巨龙淡金。
pub fn colour(e: Element) -> u32 {
    match e {
        Element::Infernal => 0xff_60_2a_00,
        Element::Mountain => 0xc8_96_50_00,
        Element::Ocean => 0x2c_c4_d8_00,
        Element::Cloud => 0xd8_ee_ff_00,
        Element::Hextech => 0x8c_7c_ff_00,
        Element::Chemtech => 0x8c_e0_32_00,
        Element::Elder => 0xff_d8_8a_00,
    }
}

/// 一段字；粗体字体组画不出来（返回 false）时改用常规体。
pub fn draw_text_in(ctx: &mut StableClient<'_>, text: &str, font: &str, r: (f32, f32, f32, f32), z: i32, size: f32,
                    colour: u32, align: TextAlignXV1) {
    if !ctx.draw_text(UI, text, font, r, z, size, colour, align, TextAlignYV1::Center) && font != FONT {
        ctx.draw_text(UI, text, FONT, r, z, size, colour, align, TextAlignYV1::Center);
    }
}

/// 居中的一行字，先画一道黑影（透明度 `shadow`）。
pub fn draw_line_text(ctx: &mut StableClient<'_>, text: &str, font: &str, r: (f32, f32, f32, f32), z: i32, size: f32,
                      shadow: u32, colour: u32) {
    let d = (size * 0.06).max(1.5);
    draw_text_in(ctx, text, font, (r.0 + d, r.1 + d, r.2, r.3), z, size, shadow * 200 / 255, TextAlignXV1::Center);
    draw_text_in(ctx, text, font, r, z + 1, size, colour, TextAlignXV1::Center);
}

/// 游戏的一条文字（league_akshan banner.rs：先带 `#` 查，再不带查，查到空的或原样的键都不算）。
fn text(ctx: &StableClient<'_>, key: &str) -> Option<String> {
    [format!("#{key}"), key.to_string()].into_iter().find_map(|k| ctx.i18n(&k).filter(|s| !s.is_empty() && *s != k))
}

fn hero_name(ctx: &StableClient<'_>, id: &str) -> String {
    text(ctx, &format!("asset/base/text/champion?description.{id}.name"))
        .unwrap_or_else(|| id.trim_start_matches("league_").to_string())
}

fn lang(ctx: &StableClient<'_>) -> words::Lang {
    let baron = text(ctx, "asset/base/text/object?epic.name").unwrap_or_default();
    let skill = text(ctx, "asset/base/text/champion?skill_name.league_akshan.skill1").unwrap_or_default();
    words::lang_of(&baron, &skill)
}

/// 节点和它的每一层父节点都显示着（league_ornn fx.rs）。
fn shown(ctx: &StableClient<'_>, path: &str) -> bool {
    let parts: Vec<&str> = path.split('.').collect();
    (1..=parts.len()).all(|n| ctx.ui_visible(&parts[..n].join(".")) == Some(true))
}

fn rect_of(ctx: &StableClient<'_>, path: &str) -> Option<notice::Rect> {
    shown(ctx, path).then(|| ctx.ui_node_rect(path)).flatten().filter(|r| r.2 > 1.0 && r.3 > 1.0)
}

/// 玩家栏的两种布局（普通、宽屏），行里的两边、各是哪一队（league_eggs notice.rs、league_ornn fx.rs）。
const PANELS: [&str; 2] = ["ingame.player_info", "ingame.wide_data.player_info"];
const SIDES: [(&str, usize); 2] = [("blue_player", 0), ("red_player", 1)];

/// 画过的公告（场次, 局, tick, 大字?）、HUD 的位置（场次, 局, x, y, 宽, 高）、头像上的圆点（场次, 局, 队伍, 分路位, 男爵?）：
/// 各在第一次画（变了）时记一行日志。
static DRAWN: Mutex<Vec<(u64, u64, usize, bool)>> = Mutex::new(Vec::new());
static PLACED: Mutex<Option<(u64, u64, i32, i32, i32, i32)>> = Mutex::new(None);
static DOTTED: Mutex<Vec<(u64, u64, usize, u8, bool)>> = Mutex::new(Vec::new());

fn first_time<T: PartialEq>(list: &Mutex<Vec<T>>, key: T) -> bool {
    let Ok(mut l) = list.lock() else { return false };
    if l.contains(&key) {
        return false;
    }
    l.push(key);
    if l.len() > 512 {
        l.drain(..256);
    }
    true
}

/// 画（客户端扩展的 post_render 里调）。`eggs` = 彩蛋的公告道上正放着 (大字, 小提示)：本包的挪到它们下面（只有附加包合集
/// 知道，单独装时是 (false, false)）。
pub fn draw(ctx: &mut StableClient<'_>, eggs: (bool, bool)) {
    if !ctx.is_in_game() {
        return;
    }
    let Some(t) = game_places::clock::screen_tick() else { return };
    let Some((m, s)) = feed::current() else { return };
    let events = feed::events(m, s);
    let rec = feed::record_at(m, s, t);
    if events.is_empty() && rec.is_none() {
        return;
    }
    let Some(ui) = ctx.draw_map_size(UI).filter(|s| s.0 > 0.0 && s.1 > 0.0) else { return };
    let lang = lang(ctx);
    // the notices: their words first (the names read the game's text), then drawn
    let showing: Vec<(bool, usize, usize, usize, String, String)> = [true, false]
        .into_iter()
        .filter_map(|big| {
            let (i, age, show) = notice::showing(&events, big, t)?;
            let name = |id: &str| hero_name(ctx, id);
            let (title, sub) = words::notice(lang, &events[i].what, &name);
            Some((big, i, age, show, title, sub))
        })
        .collect();
    let lanes = notice::lanes(ui, eggs);
    for (big, i, age, show, title, sub) in &showing {
        let e = &events[*i];
        if first_time(&DRAWN, (m, s, e.tick, *big)) {
            if let Some(k) = counted("note") {
                wlog(format!("NOTE m={m} s={s} t={} on screen at {t}: {} \"{title}\" \"{sub}\" ({lang:?}, UI {:.0}x{:.0}, \
                              eggs showing {eggs:?}) #{k}", e.tick, if *big { "banner" } else { "toast" }, ui.0, ui.1));
            }
        }
        notice::draw_one(ctx, &lanes, *big, title, sub, notice::alpha(*age, *show), notice::tone(&e.what));
    }
    // the HUD and the holders' dots
    let Some(rec) = rec else { return };
    if !hud::visible(&rec, &events, t) {
        return;
    }
    let h = hud::hud(&rec, t);
    let mx = hud::metrics(ui.1);
    let header = rect_of(ctx, "ingame.header");
    let time_ctrl = rect_of(ctx, "ingame.time_control");
    let at = hud::place(ui, header, time_ctrl, hud::size(&h, lang, &mx));
    let key = (m, s, at.0 as i32, at.1 as i32, at.2 as i32, at.3 as i32);
    if let Ok(mut p) = PLACED.lock() {
        if *p != Some(key) {
            *p = Some(key);
            if let Some(k) = counted("hud") {
                let kills = rect_of(ctx, "ingame.kills");
                wlog(format!("HUD m={m} s={s} screen t={t}: box at {:.0},{:.0} {:.0}x{:.0} (UI {:.0}x{:.0}; header {header:?}, \
                              time controls {time_ctrl:?}, kill log {kills:?}; {lang:?}) {h:?} #{k}",
                             at.0, at.1, at.2, at.3, ui.0, ui.1));
            }
        }
    }
    hud::draw(ctx, at, &h, lang, &mx);
    dots(ctx, &rec, t, m, s);
}

/// 玩家栏头像上的小圆点：拿着远古龙之力（淡金，头像左边中间）/ 纳什男爵之手（紫，左下）的人。
fn dots(ctx: &mut StableClient<'_>, rec: &super::rules::Record, t: usize, m: u64, s: u64) {
    let holds: Vec<(bool, super::rules::HoldRec)> = [(false, rec.elder), (true, rec.baron)]
        .into_iter()
        .filter_map(|(baron, h)| h.filter(|h| h.until > t && h.lanes != 0).map(|h| (baron, h)))
        .collect();
    if holds.is_empty() {
        return;
    }
    for panel in PANELS {
        if !shown(ctx, panel) {
            continue;
        }
        for (lane, row) in ctx.ui_child_names(panel).iter().enumerate().take(8) {
            for (side, team) in SIDES {
                let here: Vec<bool> =
                    holds.iter().filter(|(_, h)| h.team == team && h.lanes & (1 << lane) != 0).map(|(b, _)| *b).collect();
                if here.is_empty() {
                    continue;
                }
                let Some(r) = ctx.ui_node_rect(&format!("{panel}.{row}.{side}.champion")).filter(|r| r.2 > 1.0 && r.3 > 1.0)
                else {
                    continue;
                };
                for baron in here {
                    if first_time(&DOTTED, (m, s, team, lane as u8, baron)) {
                        if let Some(k) = counted("holder") {
                            wlog(format!("HOLDER m={m} s={s} screen t={t}: {} on team {team} lane {lane} ({panel}.{row}.{side} \
                                          at {:.0},{:.0} {:.0}x{:.0}) #{k}",
                                         if baron { "Hand of Baron" } else { "Aspect of the Dragon" }, r.0, r.1, r.2, r.3));
                        }
                    }
                    let (cx, cy, rad) = hud::holder_dot(r, baron);
                    ctx.draw_circle(UI, cx, cy, rad + 1.5, 906, 0x08_0a_10_e0);
                    ctx.draw_circle(UI, cx, cy, rad, 907, hud::hold_colour(baron) | 0xff);
                }
            }
        }
    }
}

/// 单独装的 league_dragons.dll 的客户端扩展：喂屏幕时钟（league_eggs、league_akshan 的 Overlay）、画公告、HUD。
pub struct Overlay;

impl StableExtension for Overlay {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        if !ctx.is_in_game() {
            game_places::clock::observe(false, None);
            return;
        }
        let path = game_places::clock::CLOCK_PATH;
        let text = shown(ctx, path).then(|| ctx.ui_text(path)).flatten();
        game_places::clock::observe(true, text.as_deref());
    }

    fn post_render(&self, ctx: &mut StableClient<'_>) {
        draw(ctx, (false, false));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_element_has_its_own_colour() {
        let mut c: Vec<u32> = super::super::rules::DRAKES.iter().map(|&e| colour(e)).collect();
        c.push(colour(Element::Elder));
        c.push(BARON);
        let n = c.len();
        c.sort();
        c.dedup();
        assert_eq!(c.len(), n);
        // colours carry no alpha: it is or-ed in when drawn
        assert!(c.iter().all(|x| x & 0xff == 0) && BLUE & 0xff == 0 && RED & 0xff == 0);
    }

    #[test]
    fn first_time_logs_once() {
        let l: Mutex<Vec<u32>> = Mutex::new(Vec::new());
        assert!(first_time(&l, 3));
        assert!(!first_time(&l, 3));
        assert!(first_time(&l, 4));
    }
}
