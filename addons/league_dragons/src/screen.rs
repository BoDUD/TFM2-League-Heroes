//! 画面上的大小龙（客户端扩展的 post_render 里画）：公告（[`super::notice`]）、HUD 和玩家栏头像上拿着远古龙之力 / 纳什男爵之手
//! 的小圆点（[`super::hud`]）。
//!
//! 客户端扩展读不到对局里的实体，读的是 [`super::feed`]：比赛钩子在屏幕放的那场模拟里记下的事和状态记录，按屏幕上的比赛时钟
//! （`game_places::clock::screen_tick`）取到那一刻（league_eggs notice.rs 的做法）。文字按游戏的语言（简体、繁体，其他语言用英文，
//! [`super::words`]），英雄名按游戏自己的文字。
//!
//! 本包是单独的 mod（0.3.0 起，用户 2026-11-10：「把我们的龙魂也单独做成mod开关啊」）：league_dragons.dll 自己的客户端扩展
//! [`Overlay`] 喂屏幕时钟、画公告和 HUD。彩蛋（在附加包合集里）的公告道上正放着什么，从 league_addons.dll 导出的
//! `league_addons_eggs_showing` 读（[`eggs_showing`]；合集没装就当没有），本包的公告挪到它们下面，和以前编在合集里一样。
//!
//! 小龙按元素换模型、远古巨龙和纳什男爵的模型在 [`super::skin`]（显示钩子，同样按屏幕时钟读 `feed`）；这里只画公告和 HUD。

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;

use mod_api_stable::*;

use super::rules::Element;
use super::{counted, feed, fx, hud, notice, wlog, words};

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

/// The language: this mod's own name for Baron (text/object.i18n), else - another mod renamed him - the game's own
/// champions' names and skills (0.3.5: no League Heroes needed, the user: 「就是用原版英雄也能用这个大小龙」).
fn lang(ctx: &StableClient<'_>) -> words::Lang {
    let baron = text(ctx, "asset/base/text/object?epic.name").unwrap_or_default();
    let mut sample = String::new();
    if !words::named_by_us(&baron) {
        for id in NATIVE_SAMPLE {
            for k in ["description.{id}.name", "skill_name.{id}.skill1", "skill_name.{id}.skill2"] {
                if let Some(t) = text(ctx, &format!("asset/base/text/champion?{}", k.replace("{id}", id))) {
                    sample.push_str(&t);
                }
            }
        }
    }
    words::lang_of(&baron, &sample)
}

/// The game's own champions whose names and skills tell Simplified from Traditional Chinese (the display world's
/// names, league_dragons.log `SKIN seen`).
const NATIVE_SAMPLE: [&str; 4] = ["ghost", "necromancer", "shield_bearer", "hypnotist"];

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

/// 认得出**不是**比赛画面的界面：经营主界面、阵容、入场、结算、休息室、夺冠庆典、颁奖、局间反馈。游戏没说（读不到、这份
/// 接口还不认识的新界面）不算，由比赛时钟的标签在不在屏幕上说了算（[`match_screen`]）。
pub fn off_match(scene: Option<ClientSceneKindV1>) -> bool {
    use ClientSceneKindV1::*;
    match scene {
        Some(Main | Lineup | StadiumEntrance | MatchResult | LockerRoom | ChampionshipCelebration | AwardsCeremony | SetFeedback) => true,
        Some(Match | InGame | Prologue | PrologueFirst | TutorialMorgad | TutorialSerpen | Tutorial5v5) | None => false,
    }
}

/// 这一帧屏幕上是不是比赛画面。`is_in_game()` 说的是整份经营游戏（经营主界面、阵容、结算都算），不是「在比赛里」；离开比赛
/// 画面后时钟的标签没了，`game_places::clock` 还留着最后读到的那一秒，比赛没放到结束就离开（跳过、中途退出观战 / 回放）时
/// [`hud::over`] 也拦不住——0.3.11 以前框就一直画在经营界面上（玩家 2026-11-11：「战斗结束了 这个框还显示」，截图是经营主界面）。
/// 所以两样都要：游戏说的界面不是认得出的非比赛界面（[`off_match`]），比赛时钟的标签这一帧就在屏幕上。
pub fn match_screen(in_game: bool, scene: Option<ClientSceneKindV1>, clock_shown: bool) -> bool {
    in_game && clock_shown && !off_match(scene)
}

/// 上一帧是不是比赛画面、游戏说的界面、时钟标签在不在：变了记一行日志（`SCREEN`）。
static SCREEN: Mutex<Option<(bool, Option<u32>, bool)>> = Mutex::new(None);

/// 这一帧画不画（[`match_screen`]），变了时记一行。
fn on_match_screen(ctx: &StableClient<'_>) -> bool {
    let in_game = ctx.is_in_game();
    let scene = in_game.then(|| ctx.client_scene_kind()).flatten();
    let clock = in_game && shown(ctx, game_places::clock::CLOCK_PATH);
    let on = match_screen(in_game, scene, clock);
    if let Ok(mut last) = SCREEN.lock() {
        let key = (on, scene.map(|k| k.code()), clock);
        if *last != Some(key) {
            *last = Some(key);
            if let Some(k) = counted("screen") {
                wlog(format!("SCREEN {}: in a career {in_game}, the game's screen {scene:?}, the match clock's label {} #{k}",
                             if on { "the match screen - notices, HUD and dots drawn" } else { "not the match screen - nothing drawn" },
                             if clock { "shown" } else { "not shown" }));
            }
        }
    }
    on
}

/// 画（客户端扩展的 post_render 里调）。`eggs` = 彩蛋的公告道上正放着 (大字, 小提示)：本包的挪到它们下面（[`eggs_showing`]）。
pub fn draw(ctx: &mut StableClient<'_>, eggs: (bool, bool)) {
    if !on_match_screen(ctx) {
        return;
    }
    let Some(t) = game_places::clock::screen_tick() else { return };
    let Some((m, s)) = feed::current() else { return };
    // the match over on screen (the result screen still counts as in game, its clock still reads): no notice, HUD or dot
    if hud::over(feed::ended_at(m, s), t) {
        return;
    }
    let events = feed::events(m, s);
    // the rift's terrain once it has turned (the last such event up to now), then the effects on the battlefield (the
    // souls' triggers, the Elder's burn and execute, a gate's flash), all under the notices and the HUD
    let terrain = events.iter().rev().find_map(|e| match e.what {
        feed::What::Rift { element } if e.tick <= t => Some((element, e.tick)),
        _ => None,
    });
    fx::draw(ctx, m, s, t, terrain);
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
    if !h.conflict && cursor_ui(ui).is_some_and(|(cx, cy)| cx >= at.0 && cx < at.0 + at.2 && cy >= at.1 && cy < at.1 + at.3) {
        hud::draw_tip(ctx, at, &rec, terrain.map(|r| r.0), lang, &mx, ui);
    }
    dots(ctx, &rec, t, m, s);
}

/// Where the mouse is in the UI's own coordinates, when the game's window is the one in front: the stable API has no
/// mouse position, so the cursor's place in the window (Win32) times the UI's size over the window's client size.
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
        // off the match (the management screens are "in game" too): the clock goes - it would keep the last second it read
        if !ctx.is_in_game() || off_match(ctx.client_scene_kind()) {
            game_places::clock::observe(false, None);
            return;
        }
        let path = game_places::clock::CLOCK_PATH;
        let text = shown(ctx, path).then(|| ctx.ui_text(path)).flatten();
        game_places::clock::observe(true, text.as_deref());
    }

    fn post_render(&self, ctx: &mut StableClient<'_>) {
        draw(ctx, eggs_showing());
    }
}

/// league_addons.dll's `league_addons_eggs_showing(m, s, t)`: the easter eggs' notice lanes in use (bit 0 a banner, bit 1
/// a toast) at sim tick t of the screen's match.
type EggsShowing = extern "C" fn(u64, u64, usize) -> u32;
static EGGS: AtomicUsize = AtomicUsize::new(0);

/// The easter eggs' notice lanes in use on screen now (a banner, a toast), from the add-on bundle when it is loaded (its
/// export looked up each frame until found: the mods load in any order); (false, false) without it.
pub fn eggs_showing() -> (bool, bool) {
    let (Some(t), Some((m, s))) = (game_places::clock::screen_tick(), feed::current()) else { return (false, false) };
    let Some(f) = eggs_query() else { return (false, false) };
    let bits = f(m, s, t);
    (bits & 1 != 0, bits & 2 != 0)
}

#[cfg(windows)]
fn eggs_query() -> Option<EggsShowing> {
    #[link(name = "kernel32")]
    extern "system" {
        fn GetModuleHandleW(name: *const u16) -> isize;
        fn GetProcAddress(module: isize, name: *const u8) -> usize;
    }
    let got = EGGS.load(Ordering::Relaxed);
    if got != 0 {
        return Some(unsafe { std::mem::transmute::<usize, EggsShowing>(got) });
    }
    let name: Vec<u16> = "league_addons.dll".encode_utf16().chain([0]).collect();
    let module = unsafe { GetModuleHandleW(name.as_ptr()) };
    if module == 0 {
        return None;
    }
    let p = unsafe { GetProcAddress(module, b"league_addons_eggs_showing\0".as_ptr()) };
    if p == 0 {
        return None;
    }
    EGGS.store(p, Ordering::Relaxed);
    wlog("EGGS: league_addons.dll's notice lanes found - this mod's notices go below the easter eggs' ones");
    Some(unsafe { std::mem::transmute::<usize, EggsShowing>(p) })
}

#[cfg(not(windows))]
fn eggs_query() -> Option<EggsShowing> {
    None
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

    /// The player's report (2026-11-11, the box left over the management screen after a match): "in game" is the whole
    /// career, so the game's own screen and the match clock's label decide.
    #[test]
    fn nothing_is_drawn_off_the_match_screen() {
        use ClientSceneKindV1::*;
        // the match: the play screen, whatever the game calls it, with its clock on screen
        for scene in [InGame, Match, Tutorial5v5, TutorialSerpen, TutorialMorgad, Prologue, PrologueFirst] {
            assert!(match_screen(true, Some(scene), true), "{scene:?}");
            assert!(!match_screen(true, Some(scene), false), "{scene:?} without its clock (the pick screen, a full-screen panel)");
        }
        // back in the management screens the clock's label may still read (a match skipped or left half-way): nothing
        for scene in [Main, Lineup, StadiumEntrance, MatchResult, LockerRoom, ChampionshipCelebration, AwardsCeremony, SetFeedback] {
            assert!(off_match(Some(scene)), "{scene:?}");
            assert!(!match_screen(true, Some(scene), true), "{scene:?} with a stale clock label");
            assert!(!match_screen(true, Some(scene), false), "{scene:?}");
        }
        // every screen the game can name is decided one way or the other
        assert_eq!(ClientSceneKindV1::VARIANTS.len(), 15, "a new screen: is it a match? (off_match)");
        // a screen this API cannot name yet: the clock's label decides
        assert!(match_screen(true, None, true));
        assert!(!match_screen(true, None, false));
        // not in a career at all (the title, the database editor)
        assert!(!match_screen(false, None, true) && !match_screen(false, Some(InGame), true));
    }

    #[test]
    fn first_time_logs_once() {
        let l: Mutex<Vec<u32>> = Mutex::new(Vec::new());
        assert!(first_time(&l, 3));
        assert!(!first_time(&l, 3));
        assert!(first_time(&l, 4));
    }
}
