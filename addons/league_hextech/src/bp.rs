//! BP 画面上的海克斯面板（第 2 步：玩家给自己的队伍选，用户 2026-11-26：「就在 BP 阶段选」）。
//!
//! BP 画面是游戏的 `asset/base/ui/layout/banpick/layout`（根节点 `main`，1920x1080 的布局）：英雄格子 `main.champions.contents`
//! 下每张卡按英雄 id 命名，卡上的 `blue` / `red` 标记显示着就是那边选了它、字是第几手（电竞大脑 draft_screen.rs 读的同一套）；
//! 底栏 `main.bottom.<边>_side.name` 是两队的队名（后面带着排名「#1」），和玩家自己的队名比就知道玩家是哪边；标题栏的
//! `main.header.desc.<边>_arrow` 显示着就是轮到那边。屏幕左下、右下两个角是电竞大脑的面板，本包不放东西。
//!
//! 本包的东西挂在 `main.hx_bp` 下（[`source`]）：标题栏右边一个入口按钮（也可以按 F7），点开是一块盖在英雄格子上的面板
//! （x 310、y 56、1300x620，比英雄格子大一圈，下面的英雄信息栏露着）：一排玩家这边的英雄（按选的先后），下面四行——开局、6 级、
//! 9 级、12 级——各三张卡，点卡选中，每张卡右下角的「刷新」换一张（每张一次），左下「这个英雄全部按 AI 推荐」。按钮和面板底板是
//! 游戏的界面节点（面板底板挡住下面英雄格子的点击）；卡上的字、选中的框每帧自己画（post_render），位置读按钮节点的实际位置，
//! 界面缩放了也对得上。
//!
//! 选的东西都在 [`super::pending`] 的记录里：BP 画面一出来、认出玩家是哪边就开一份（档位这时就定了，全场同一档），玩家这边
//! 每选一个英雄就给他发四次的牌（AI 推荐的先选上）。BP 结束、比赛的模拟一开始认这份记录，它就锁了。
//!
//! 第一次画的时候日志记一行几个节点的位置（`BP LAYOUT`），游戏里看着不对再挪。

use std::sync::{LazyLock, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

use mod_api_stable::*;

use super::augments::{Traits, AUGS};
use super::pending::{self, Record};
use super::screen::{cursor_ui, draw_text_in, fit, game_lang, hero_name, shadowed, tier_colour, Rect, BOLD, FONT, UI};
use super::words;
use super::{counted, kit, rules, settings, wlog};

/// BP 画面的英雄格子（有它就是在 BP 画面上）。
pub const GRID: &str = "main.champions.contents";
const NAMES: [&str; 2] = ["main.bottom.blue_side.name", "main.bottom.red_side.name"];
const ARROWS: [&str; 2] = ["main.header.desc.blue_arrow", "main.header.desc.red_arrow"];
const ROOT: &str = "main";
const NODE: &str = "hx_bp";
pub const HOTKEY: &str = "F7";
/// 每几帧读一次格子（两百多张卡，每张两次）、看一次本包的节点还在不在（游戏重建了画面就再挂一次）。
const READ_EVERY: u64 = 10;
const HEAL_EVERY: u64 = 30;
/// 一排最多几个英雄。
const TABS: usize = 5;

// ===================== 布局（BP 画面的 1920x1080，相对 main） =====================

pub type Box4 = (i32, i32, i32, i32);

/// 标题栏里的入口：红方回合箭头（x 1315–1355）右边、靠右的那几句话（换位阶段的「请决定选手要使用的英雄。」从 x 1655 左右
/// 起，下一手的提示更靠右）左边。0.2.0 放在 x 1506，玩家的截图：盖住了「请决」两个字。
pub const OPEN_BTN: Box4 = (1362, 6, 136, 38);
/// 面板：盖住筛选栏和英雄格子（x 310–1610，y 60–680），下面的英雄信息栏露着。
pub const PANEL: Box4 = (310, 56, 1300, 620);
/// 面板里的（相对面板）
pub const CLOSE: Box4 = (1252, 8, 36, 30);
pub const AI_BTN: Box4 = (20, 574, 280, 36);
/// 「全部确定」「确定（这个英雄）」（玩家：「感觉少一个确定的按钮 不然已选一直是0/5」）。
pub const ALL_BTN: Box4 = (880, 574, 190, 36);
pub const OK_BTN: Box4 = (1090, 570, 190, 44);

pub fn tab(i: usize) -> Box4 {
    (20 + i as i32 * 252, 50, 240, 44)
}

pub fn card(k: usize, j: usize) -> Box4 {
    (184 + j as i32 * 356, 104 + k as i32 * 116, 340, 104)
}

pub fn reroll(k: usize, j: usize) -> Box4 {
    let (x, y, w, h) = card(k, j);
    (x + w - 92, y + h - 30, 84, 24)
}

/// 第 `k` 次拿的是技能海克斯时，左边那一栏（「6 级」下面）的三个按钮：技能 / 技能 2 / 大招（0.5.0）。
pub fn slot_btn(k: usize, i: usize) -> Box4 {
    let (_, y, _, _) = card(k, 0);
    (20 + i as i32 * 52, y + 60, 48, 30)
}

/// 本包挂在 `main` 下的节点（`.ui` 源码）：入口按钮、面板（一开始不显示）、面板里的每个按钮——都是透明的，字和框自己画。
pub fn source() -> String {
    let btn = |id: &str, (x, y, w, h): Box4| {
        format!("#{id}:color_icon_button {{ x: {x}px; y: {y}px; width: {w}px; height: {h}px; btn: {{ color: #00000000; }} \
                 hover: {{ btn: {{ color: #ffffff12; }} }} }} ")
    };
    let mut inner = btn("close", CLOSE);
    for i in 0..TABS {
        inner.push_str(&btn(&format!("t{i}"), tab(i)));
    }
    for k in 0..rules::SCREENS {
        for j in 0..3 {
            inner.push_str(&btn(&format!("c{k}{j}"), card(k, j)));
        }
    }
    // 刷新按钮在卡的后面：点它不会点到卡
    for k in 0..rules::SCREENS {
        for j in 0..3 {
            inner.push_str(&btn(&format!("r{k}{j}"), reroll(k, j)));
        }
    }
    for k in 0..rules::SCREENS {
        for i in 0..3 {
            inner.push_str(&btn(&format!("s{k}{i}"), slot_btn(k, i)));
        }
    }
    inner.push_str(&btn("ai", AI_BTN));
    inner.push_str(&btn("okall", ALL_BTN));
    inner.push_str(&btn("ok", OK_BTN));
    let (px, py, pw, ph) = PANEL;
    format!("{NODE}:empty {{ width: 100%; height: 100%; ignore_event: true; {open}\
             #panel:color {{ x: {px}px; y: {py}px; width: {pw}px; height: {ph}px; color: #0b0d14ff; \
             rounding: Uniform {{ rounding: 12; }} visible: false; {inner}}} }}",
            open = btn("open", OPEN_BTN))
}

/// 点得到的东西（节点名）：入口、关、第几个英雄、第几次的第几张卡、刷新、全部 AI。
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Click {
    Open,
    Close,
    Tab(usize),
    Card(usize, usize),
    Reroll(usize, usize),
    /// 第几次的技能海克斯放在第几个技能上（0 技能、1 技能 2、2 大招）
    Slot(usize, usize),
    Ai,
    /// 确定这个英雄（跳到下一个没确定的）、全部确定（关掉面板）
    Confirm,
    ConfirmAll,
}

pub fn clickables() -> Vec<String> {
    let mut v = vec!["open".to_string(), "close".to_string(), "ai".to_string(), "ok".to_string(), "okall".to_string()];
    v.extend((0..TABS).map(|i| format!("t{i}")));
    for k in 0..rules::SCREENS {
        for j in 0..3 {
            v.push(format!("c{k}{j}"));
            v.push(format!("r{k}{j}"));
            v.push(format!("s{k}{j}"));
        }
    }
    v
}

pub fn path_of(id: &str) -> String {
    if id == "open" {
        format!("{ROOT}.{NODE}.open")
    } else {
        format!("{ROOT}.{NODE}.panel.{id}")
    }
}

pub fn parse_click(id: &str) -> Option<Click> {
    let digits = |s: &str| -> Option<(usize, usize)> {
        let b = s.as_bytes();
        (b.len() == 2 && b[0].is_ascii_digit() && b[1].is_ascii_digit())
            .then(|| ((b[0] - b'0') as usize, (b[1] - b'0') as usize))
            .filter(|&(k, j)| k < rules::SCREENS && j < 3)
    };
    match id {
        "open" => Some(Click::Open),
        "close" => Some(Click::Close),
        "ai" => Some(Click::Ai),
        "ok" => Some(Click::Confirm),
        "okall" => Some(Click::ConfirmAll),
        _ => {
            let (head, rest) = id.split_at(1);
            match head {
                "t" => rest.parse::<usize>().ok().filter(|&i| i < TABS).map(Click::Tab),
                "c" => digits(rest).map(|(k, j)| Click::Card(k, j)),
                "r" => digits(rest).map(|(k, j)| Click::Reroll(k, j)),
                "s" => digits(rest).map(|(k, i)| Click::Slot(k, i)),
                _ => None,
            }
        }
    }
}

// ===================== 读 BP 画面 =====================

/// 队名比较用的样子：去掉后面的排名「 #1」、去空白、小写（电竞大脑的 team_key）。
pub fn team_key(name: &str) -> String {
    let clean: String = name.chars().filter(|c| *c != '\r' && *c != '\n').collect();
    let mut key = clean.trim();
    if let Some(at) = key.rfind(" #") {
        if at + 2 < key.len() && key[at + 2..].chars().all(|c| c.is_ascii_digit()) {
            key = key[..at].trim_end();
        }
    }
    key.to_lowercase()
}

/// 玩家是哪边：底栏两边的队名和玩家自己的队名比（-> 0 蓝、1 红；认不出：None）。
pub fn side_of(mine: &str, blue: &str, red: &str) -> Option<usize> {
    let k = team_key(mine);
    if k.is_empty() {
        return None;
    }
    [blue, red].iter().position(|n| team_key(n) == k)
}

fn player_side(ctx: &StableClient<'_>) -> Option<usize> {
    let mine = ctx.player_team_id().and_then(|id| ctx.team_name(id))?;
    let blue = ctx.ui_text(NAMES[0]).unwrap_or_default();
    let red = ctx.ui_text(NAMES[1]).unwrap_or_default();
    side_of(&mine, &blue, &red)
}

/// 两边选了谁（按第几手排）：格子里每张卡的 `blue` / `red` 标记显示着就是那边选的，字是第几手。
fn read_picks(ctx: &StableClient<'_>) -> (Vec<String>, Vec<String>) {
    let mut sides: [Vec<(u32, String)>; 2] = [Vec::new(), Vec::new()];
    for child in ctx.ui_child_names(GRID) {
        for (s, badge) in ["blue", "red"].iter().enumerate() {
            let p = format!("{GRID}.{child}.{badge}");
            if ctx.ui_visible(&p) == Some(true) {
                let n = ctx.ui_text(&format!("{p}.text")).and_then(|t| t.trim().parse().ok()).unwrap_or(99);
                sides[s].push((n, child.clone()));
            }
        }
    }
    let order = |mut v: Vec<(u32, String)>| -> Vec<String> {
        v.sort();
        v.into_iter().map(|x| x.1).collect()
    };
    let [b, r] = sides;
    (order(b), order(r))
}

fn traits_of(hero: &str) -> Traits {
    kit::traits(kit::get(hero).as_ref(), None).0
}

// ===================== 状态 =====================

#[derive(Default)]
struct Bp {
    /// 上一帧在不在 BP 画面上
    on: bool,
    /// 第几次 BP 画面
    session: u64,
    rec: Option<u64>,
    open: bool,
    tab: usize,
    frame: u64,
    built: bool,
    side: Option<usize>,
    read_at: u64,
    heal_at: u64,
    /// 轮到玩家这边选英雄
    turn: bool,
    /// 这一次 BP 记过布局、认不出边的日志没有
    logged: bool,
    side_logged: bool,
    /// 这一次 BP 把格子里的英雄补进特性表了没有
    kit_done: bool,
}

static BP: LazyLock<Mutex<Bp>> = LazyLock::new(|| Mutex::new(Bp::default()));
static CLICKS: Mutex<Vec<String>> = Mutex::new(Vec::new());

fn take_clicks() -> Vec<String> {
    let mut l = std::mem::take(&mut *CLICKS.lock().unwrap_or_else(|e| e.into_inner()));
    let mut seen = std::collections::HashSet::new();
    l.retain(|p| seen.insert(p.clone()));
    l
}

fn register(ctx: &mut StableClient<'_>) -> usize {
    let mut n = 0;
    for id in clickables() {
        let owned = id.clone();
        if ctx.ui_register_path_events(&path_of(&id), move |c| {
            // 点了（或者游戏没说是什么事）；鼠标移上去、节点被拿掉不算
            if matches!(c.ui_current_event().and_then(|e| e.kind), None | Some(UiEventKindV1::Click)) {
                CLICKS.lock().unwrap_or_else(|e| e.into_inner()).push(owned.clone());
            }
        }) {
            n += 1;
        }
    }
    n
}

fn now_seed() -> u64 {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_nanos() as u64).unwrap_or(0x5eed)
}

/// 客户端扩展每帧（post_update）：认 BP 画面、挂本包的节点、读两边选了谁、处理点击和 F7。
pub fn update(ctx: &mut StableClient<'_>) {
    let mut st = BP.lock().unwrap_or_else(|e| e.into_inner());
    st.frame += 1;
    let on = ctx.is_in_game() && ctx.ui_exists(GRID);
    if !on {
        if st.on {
            st.on = false;
            st.open = false;
            st.built = false;
            if let Some(r) = st.rec.and_then(pending::get) {
                wlog(format!("BP OFF: record #{} left for the match - the player {}, {} heroes, {} with picks of the player's \
                              own{}", r.id, if r.side == 0 { "blue" } else { "red" }, r.mine.len(), r.touched(),
                             if r.used { " (already used by a simulation)" } else { "" }));
            }
        }
        CLICKS.lock().unwrap_or_else(|e| e.into_inner()).clear();
        return;
    }
    if !st.on {
        let session = st.session + 1;
        *st = Bp { on: true, session, frame: st.frame, ..Bp::default() };
    }
    let node = format!("{ROOT}.{NODE}");
    if !st.built || (st.frame >= st.heal_at && !ctx.ui_exists(&node)) {
        st.heal_at = st.frame + HEAL_EVERY;
        if ctx.ui_exists(&node) || ctx.ui_spawn_source(ROOT, &source()) {
            let n = register(ctx);
            st.built = true;
            if let Some(k) = counted("bp built") {
                wlog(format!("BP PANEL put on the pick screen (session {}): {n} buttons #{k}", st.session));
            }
        } else if let Some(k) = counted("bp spawn failed") {
            wlog(format!("BP PANEL could not be put under {ROOT} #{k}"));
        }
    }
    if st.frame >= st.read_at {
        st.read_at = st.frame + READ_EVERY;
        if !st.kit_done {
            // 格子里每张卡就是一个能选的英雄（mod 的也在）：表上没有的补上
            st.kit_done = true;
            let n = kit::fill_from_client(ctx, ctx.ui_child_names(GRID));
            if n > 0 {
                wlog(format!("KIT {n} more champions' classes and tags from the pick screen's grid ({} in all)", kit::count()));
            }
        }
        if let Some(s) = player_side(ctx) {
            st.side = Some(s);
        } else if !st.side_logged && st.frame > 120 {
            st.side_logged = true;
            if let Some(k) = counted("bp side") {
                wlog(format!("BP SIDE not known: the player's team {:?}, blue {:?}, red {:?} - no panel this time #{k}",
                             ctx.player_team_id().and_then(|id| ctx.team_name(id)), ctx.ui_text(NAMES[0]),
                             ctx.ui_text(NAMES[1])));
            }
        }
        if let Some(side) = st.side {
            let (blue, red) = read_picks(ctx);
            if st.rec.is_none() {
                let seed = rules::splitmix(now_seed() ^ st.session);
                let rec = Record::new(seed, side, seed, settings::get().weights);
                let tiers: Vec<&str> = rec.tiers.iter().map(|t| t.key()).collect();
                wlog(format!("BP REC #{} opened: the player is {}, tiers {}", rec.id, if side == 0 { "blue" } else { "red" },
                             tiers.join(" / ")));
                st.rec = Some(pending::open(rec));
            }
            if let Some(id) = st.rec {
                pending::edit(id, |r| r.set_lineup(blue, red, traits_of));
            }
            st.turn = ctx.ui_visible(ARROWS[side]) == Some(true);
        }
        // 本包的节点排好版（有了位置）以后记一次（0.2.0 挂上去的那一帧就记，位置还都是 0）
        if !st.logged && st.built && ctx.ui_node_rect(&path_of("open")).is_some_and(|r| r.2 > 1.0) {
            st.logged = true;
            let r = |p: &str| ctx.ui_node_rect(p).map(|r| format!("{:.0},{:.0} {:.0}x{:.0}", r.0, r.1, r.2, r.3));
            if let Some(k) = counted("bp layout") {
                wlog(format!("BP LAYOUT main {:?}, header desc {:?}, next turn {:?}, swap phase label {:?}, timer {:?}, grid {:?}, \
                              our button {:?}, our panel {:?} #{k}",
                             r(ROOT), r("main.header.desc"), r("main.header.next_turn"), r("main.header.swap_phase"),
                             r("main.timer_area"), r("main.champions"), r(&path_of("open")), r(&format!("{node}.panel"))));
            }
        }
    }
    if ctx.key_pressed(HOTKEY) {
        st.open = !st.open;
    }
    if st.open && (ctx.key_pressed("Escape") || ctx.key_pressed("Esc")) {
        st.open = false;
    }
    for id in take_clicks() {
        if let Some(c) = parse_click(&id) {
            apply(&mut st, c);
        }
    }
    let want = st.open && st.rec.is_some();
    let panel = format!("{node}.panel");
    if ctx.ui_visible(&panel) != Some(want) {
        ctx.ui_set_visible(&panel, want);
    }
}

fn apply(st: &mut Bp, c: Click) {
    let Some(id) = st.rec else {
        if matches!(c, Click::Open) {
            st.open = !st.open;
        }
        return;
    };
    let hero = pending::get(id).and_then(|r| r.mine.get(st.tab).map(|m| m.hero.clone()));
    match c {
        Click::Open => st.open = !st.open,
        Click::Close => st.open = false,
        Click::Tab(i) => {
            if pending::get(id).is_some_and(|r| i < r.mine.len()) {
                st.tab = i;
            }
        }
        Click::Card(k, j) => {
            if let Some(h) = hero {
                pending::edit(id, |r| r.choose(&h, k, j));
            }
        }
        Click::Reroll(k, j) => {
            if let Some(h) = hero {
                let t = traits_of(&h);
                pending::edit(id, |r| r.reroll(&h, k, j, &t));
            }
        }
        Click::Slot(k, i) => {
            if let Some(h) = hero {
                pending::edit(id, |r| r.set_slot(&h, k, i as u8 + 1));
            }
        }
        Click::Ai => {
            if let Some(h) = hero {
                let t = traits_of(&h);
                pending::edit(id, |r| r.all_ai(&h, &t));
            }
        }
        Click::Confirm => {
            if let Some(h) = hero {
                let tab = st.tab;
                match pending::edit(id, |r| {
                    r.confirm(&h);
                    r.next_open(tab)
                }) {
                    Some(Some(next)) => st.tab = next,
                    // 都确定了：关掉面板
                    Some(None) => st.open = false,
                    None => {}
                }
            }
        }
        Click::ConfirmAll => {
            pending::edit(id, |r| r.confirm_all());
            st.open = false;
        }
    }
}

// ===================== 画（post_render） =====================

fn rect(ctx: &StableClient<'_>, path: &str) -> Option<Rect> {
    ctx.ui_node_rect(path).filter(|r| r.2 > 1.0 && r.3 > 1.0)
}

fn inside(p: Option<(f32, f32)>, r: Rect) -> bool {
    p.is_some_and(|(x, y)| x >= r.0 && x < r.0 + r.2 && y >= r.1 && y < r.1 + r.3)
}

/// 每帧画入口按钮的字；面板开着时画面板里的东西（底板是界面节点自己画的）。
pub fn draw(ctx: &mut StableClient<'_>) {
    let (on, rec, open, tab, turn) = {
        let st = BP.lock().unwrap_or_else(|e| e.into_inner());
        (st.on, st.rec, st.open, st.tab, st.turn)
    };
    if !on {
        return;
    }
    let Some(rec) = rec.and_then(pending::get) else { return };
    let lang = game_lang(ctx);
    let ui = ctx.draw_map_size(UI).unwrap_or((1920.0, 1080.0));
    let cursor = cursor_ui(ui);
    if let Some(b) = rect(ctx, &path_of("open")) {
        let hot = inside(cursor, b) || open;
        ctx.draw_rect(UI, b.0, b.1, b.2, b.3, 960, b.3 * 0.25, if hot { 0x2a_24_10_f0 } else { 0x1a_18_10_e6 });
        ctx.draw_rect(UI, b.0, b.1 + b.3 - 3.0, b.2, 3.0, 961, 1.0, tier_colour(super::augments::Tier::Gold) | 0xff);
        let t = words::bp_button(lang, rec.confirmed(), rec.mine.len());
        let s = fit(&t, b.2 - 12.0, b.3 * 0.42, 9.0);
        shadowed(ctx, &t, BOLD, (b.0 + 6.0, b.1, b.2 - 12.0, b.3), 962, s, 0xff, 0xf2_e6_c4_00, TextAlignXV1::Center);
    }
    if !open {
        return;
    }
    let Some(p) = rect(ctx, &format!("{ROOT}.{NODE}.panel")) else { return };
    let unit = p.3 / PANEL.3 as f32; // 面板 620 高对应多少屏幕单位
    let z = 970;
    // 标题、档位、关
    let title = words::bp_title(lang, rec.used);
    shadowed(ctx, &title, BOLD, (p.0 + 20.0 * unit, p.1 + 6.0 * unit, 640.0 * unit, 36.0 * unit), z, 22.0 * unit, 0xff,
             if rec.used { 0xc8_c4_ba_00 } else { 0xf4_ee_dc_00 }, TextAlignXV1::Left);
    let levels = settings::get().levels;
    for k in 0..rules::SCREENS {
        let x = p.0 + (700.0 + k as f32 * 135.0) * unit;
        let t = format!("{} {}", words::screen_name(lang, k, levels), words::tier(lang, rec.tiers[k]));
        shadowed(ctx, &t, BOLD, (x, p.1 + 8.0 * unit, 130.0 * unit, 32.0 * unit), z, fit(&t, 126.0 * unit, 16.0 * unit, 8.0),
                 0xff, tier_colour(rec.tiers[k]), TextAlignXV1::Center);
    }
    if let Some(c) = rect(ctx, &format!("{ROOT}.{NODE}.panel.close")) {
        shadowed(ctx, "×", BOLD, c, z, c.3 * 0.9, 0xff, if inside(cursor, c) { 0xff_ff_ff_00 } else { 0xb4_b8_c4_00 },
                 TextAlignXV1::Center);
    }
    if rec.mine.is_empty() {
        let t = words::bp_none(lang);
        shadowed(ctx, t, FONT, (p.0, p.1 + p.3 * 0.4, p.2, 40.0 * unit), z, 20.0 * unit, 0xff, 0xc8_c4_ba_00, TextAlignXV1::Center);
        return;
    }
    // 一排英雄
    let tab = tab.min(rec.mine.len() - 1);
    for (i, m) in rec.mine.iter().enumerate().take(TABS) {
        let Some(r) = rect(ctx, &format!("{ROOT}.{NODE}.panel.t{i}")) else { continue };
        let sel = i == tab;
        ctx.draw_rect(UI, r.0, r.1, r.2, r.3, z, 6.0 * unit, if sel { 0x26_2c_44_ff } else if inside(cursor, r) { 0x1c_20_30_ff } else { 0x14_17_22_ff });
        if sel {
            ctx.draw_rect(UI, r.0, r.1 + r.3 - 3.0 * unit, r.2, 3.0 * unit, z + 1, 1.0, 0x5b_73_ff_ff);
        }
        let mark = if m.confirmed { " ✓" } else { "" };
        let t = format!("{}{mark}", hero_name(ctx, &m.hero));
        shadowed(ctx, &t, BOLD, r, z + 2, fit(&t, r.2 - 8.0, r.3 * 0.42, 8.0), 0xff, if sel { 0xff_ff_ff_00 } else { 0xb8_bc_c8_00 },
                 TextAlignXV1::Center);
    }
    // 四次、各三张
    let m = &rec.mine[tab];
    for (k, c) in m.picks.iter().enumerate() {
        if let Some(r0) = rect(ctx, &format!("{ROOT}.{NODE}.panel.c{k}0")) {
            let label = (p.0 + 20.0 * unit, r0.1, r0.0 - p.0 - 30.0 * unit, r0.3);
            let name = words::screen_name(lang, k, levels);
            shadowed(ctx, &name, BOLD, (label.0, label.1 + label.3 * 0.18, label.2, label.3 * 0.32), z, label.3 * 0.24, 0xff,
                     0xf4_ee_dc_00, TextAlignXV1::Left);
            // 拿的是技能海克斯：档位那一行换成三个选技能的按钮（档位标题栏上也有）
            let ev = AUGS[c.chosen as usize].ev;
            if super::augments::skill_aug(ev) {
                let now = if c.slot > 0 { c.slot } else { super::augments::ai_slot(ev) };
                for i in 0..3 {
                    let Some(b) = rect(ctx, &format!("{ROOT}.{NODE}.panel.s{k}{i}")) else { continue };
                    let on = now == i as u8 + 1;
                    let gold = tier_colour(AUGS[c.chosen as usize].tier);
                    ctx.draw_rect(UI, b.0, b.1, b.2, b.3, z + 1, 4.0 * unit,
                                  if on { 0x34_2c_14_ff } else if inside(cursor, b) && !rec.used { 0x26_2a_3a_ff } else { 0x18_1b_26_ff });
                    if on {
                        ctx.draw_rect(UI, b.0, b.1 + b.3 - 2.0 * unit, b.2, 2.0 * unit, z + 2, 1.0, gold | 0xff);
                    }
                    let t = words::slot_name(lang, i as u8 + 1);
                    draw_text_in(ctx, t, BOLD, b, z + 2, fit(t, b.2 - 4.0, b.3 * 0.5, 7.0),
                                 if on { 0xff_f0_c8_ff } else { 0xa8_ac_b8_ff }, TextAlignXV1::Center);
                }
            } else {
                let t = words::tier(lang, rec.tiers[k]);
                shadowed(ctx, t, BOLD, (label.0, label.1 + label.3 * 0.52, label.2, label.3 * 0.3), z, label.3 * 0.2, 0xff,
                         tier_colour(rec.tiers[k]), TextAlignXV1::Left);
            }
        }
        for j in 0..3 {
            let Some(r) = rect(ctx, &format!("{ROOT}.{NODE}.panel.c{k}{j}")) else { continue };
            let aug = c.cards[j] as usize;
            let chosen = c.chosen == c.cards[j];
            let edge = tier_colour(AUGS[aug].tier);
            let bg = if chosen { 0x22_26_36_ff } else if inside(cursor, r) && !rec.used { 0x1a_1d_2a_ff } else { 0x12_14_1e_ff };
            ctx.draw_rect(UI, r.0, r.1, r.2, r.3, z, 8.0 * unit, bg);
            if chosen {
                let w = 3.0 * unit;
                for (x, y, ww, hh) in [(r.0, r.1, r.2, w), (r.0, r.1 + r.3 - w, r.2, w), (r.0, r.1, w, r.3), (r.0 + r.2 - w, r.1, w, r.3)] {
                    ctx.draw_rect(UI, x, y, ww, hh, z + 1, 0.0, edge | 0xff);
                }
            }
            let pad = 12.0 * unit;
            let inner = r.2 - 2.0 * pad;
            let nm = words::name(lang, aug);
            shadowed(ctx, nm, BOLD, (r.0 + pad, r.1 + 4.0 * unit, inner, r.3 * 0.3), z + 2, fit(nm, inner, r.3 * 0.2, 8.0), 0xff,
                     edge, TextAlignXV1::Left);
            // 说明：一行放不下就折成两三行（触发类的说明长），挑字最大的那种折法；下面 30 像素是「已选」和刷新按钮
            let d = words::desc(lang, aug);
            let (top, area) = (r.1 + r.3 * 0.34, r.3 - r.3 * 0.34 - 31.0 * unit);
            let (lines, size) = (1..=3)
                .map(|n| {
                    let lines = words::wrap_in(d, n);
                    let longest = lines.iter().map(|l| words::line_em(l)).fold(0.0, f32::max).max(1.0);
                    let size = (r.3 * 0.145).min(inner * 0.94 / longest).min(area / (lines.len() as f32 * 1.12));
                    (lines, size)
                })
                .fold((Vec::new(), 0.0f32), |best, x| if x.1 > best.1 + 0.25 { x } else { best });
            for (i, l) in lines.iter().enumerate() {
                draw_text_in(ctx, l, FONT, (r.0 + pad, top + i as f32 * size * 1.12, inner, size * 1.1), z + 2, size.max(7.0),
                             0xe6_e0_d2_ff, TextAlignXV1::Left);
            }
            if chosen {
                let t = words::bp_chosen(lang, c.by_user, m.confirmed);
                draw_text_in(ctx, t, BOLD, (r.0 + pad, r.1 + r.3 - 28.0 * unit, inner * 0.6, 24.0 * unit), z + 2,
                             fit(t, inner * 0.6, r.3 * 0.13, 7.0), edge | 0xff, TextAlignXV1::Left);
            }
            if let Some(rr) = rect(ctx, &format!("{ROOT}.{NODE}.panel.r{k}{j}")) {
                let used = c.cards[j] != c.first[j];
                let left = rec.reroll_left(&m.hero, k, j);
                let live = left && !rec.used;
                ctx.draw_rect(UI, rr.0, rr.1, rr.2, rr.3, z + 2, 4.0 * unit,
                              if live && inside(cursor, rr) { 0x34_3a_52_ff } else if live { 0x24_28_38_ff } else { 0x16_18_22_ff });
                let t = words::bp_reroll(lang, used, left);
                draw_text_in(ctx, t, FONT, rr, z + 3, fit(t, rr.2 - 4.0, rr.3 * 0.6, 7.0),
                             if live { 0xd8_dc_e8_ff } else { 0x70_74_80_ff }, TextAlignXV1::Center);
            }
        }
    }
    // 下面一行：全部 AI、说明、轮到你了
    if let Some(a) = rect(ctx, &format!("{ROOT}.{NODE}.panel.ai")) {
        ctx.draw_rect(UI, a.0, a.1, a.2, a.3, z, 6.0 * unit, if inside(cursor, a) && !rec.used { 0x2a_30_46_ff } else { 0x1c_20_2e_ff });
        let t = words::bp_ai(lang);
        draw_text_in(ctx, t, BOLD, a, z + 1, fit(t, a.2 - 10.0, a.3 * 0.42, 7.0), 0xe8_e8_e8_ff, TextAlignXV1::Center);
        // 说明在「全部 AI」和「全部确定」之间
        let right = rect(ctx, &format!("{ROOT}.{NODE}.panel.okall")).map_or(p.0 + p.2 - 20.0 * unit, |r| r.0);
        let hint_r = (a.0 + a.2 + 16.0 * unit, a.1, right - (a.0 + a.2) - 32.0 * unit, a.3);
        if turn && !rec.used {
            let t = words::bp_turn(lang);
            draw_text_in(ctx, t, BOLD, hint_r, z, fit(t, hint_r.2, a.3 * 0.42, 7.0), 0xff_6a_5a_ff, TextAlignXV1::Right);
        } else {
            let t = words::bp_hint(lang);
            draw_text_in(ctx, t, FONT, hint_r, z, fit(t, hint_r.2, a.3 * 0.36, 7.0), 0x9a_9e_a8_ff, TextAlignXV1::Center);
        }
    }
    // 全部确定、确定这个英雄（确定过了写「已确定」）
    let all_done = rec.confirmed() == rec.mine.len();
    if let Some(b) = rect(ctx, &format!("{ROOT}.{NODE}.panel.okall")) {
        let live = !rec.used && !all_done;
        ctx.draw_rect(UI, b.0, b.1, b.2, b.3, z, 6.0 * unit,
                      if live && inside(cursor, b) { 0x2a_30_46_ff } else if live { 0x1c_20_2e_ff } else { 0x14_16_20_ff });
        let t = words::bp_confirm_all(lang);
        draw_text_in(ctx, t, BOLD, b, z + 1, fit(t, b.2 - 10.0, b.3 * 0.42, 7.0), if live { 0xe8_e8_e8_ff } else { 0x70_74_80_ff },
                     TextAlignXV1::Center);
    }
    if let Some(b) = rect(ctx, &format!("{ROOT}.{NODE}.panel.ok")) {
        let gold = tier_colour(super::augments::Tier::Gold);
        let live = !rec.used && !m.confirmed;
        ctx.draw_rect(UI, b.0, b.1, b.2, b.3, z, 7.0 * unit,
                      if live && inside(cursor, b) { 0x4a_3a_14_ff } else if live { 0x36_2b_10_ff } else { 0x16_18_22_ff });
        if live {
            ctx.draw_rect(UI, b.0, b.1 + b.3 - 3.0 * unit, b.2, 3.0 * unit, z + 1, 1.0, gold | 0xff);
        }
        let t = if m.confirmed { words::bp_confirmed(lang).to_string() } else { words::bp_confirm(lang, &hero_name(ctx, &m.hero)) };
        draw_text_in(ctx, &t, BOLD, b, z + 2, fit(&t, b.2 - 12.0, b.3 * 0.4, 7.0), if live { 0xff_f0_c8_ff } else { 0x9a_9e_a8_ff },
                     TextAlignXV1::Center);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn within(r: Box4, outer: Box4) -> bool {
        r.0 >= 0 && r.1 >= 0 && r.0 + r.2 <= outer.2 && r.1 + r.3 <= outer.3
    }

    fn apart(a: Box4, b: Box4) -> bool {
        a.0 + a.2 <= b.0 || b.0 + b.2 <= a.0 || a.1 + a.3 <= b.1 || b.1 + b.3 <= a.1
    }

    /// Everything inside the panel sits inside it, nothing on top of something else (but each reroll button on its own
    /// card's corner), and the panel stays off the pick columns (x 0-300, 1620-1920), the bottom bar (y 980+) and
    /// the other mod's corner panels.
    #[test]
    fn the_layout_fits() {
        let mut boxes = vec![CLOSE, AI_BTN, ALL_BTN, OK_BTN];
        boxes.extend((0..TABS).map(tab));
        for k in 0..rules::SCREENS {
            for i in 0..3 {
                boxes.push(slot_btn(k, i));
            }
            for j in 0..3 {
                boxes.push(card(k, j));
                let r = reroll(k, j);
                let c = card(k, j);
                assert!(r.0 >= c.0 && r.1 >= c.1 && r.0 + r.2 <= c.0 + c.2 && r.1 + r.3 <= c.1 + c.3, "reroll on its card");
            }
        }
        for (i, a) in boxes.iter().enumerate() {
            assert!(within(*a, PANEL), "{a:?}");
            for b in &boxes[i + 1..] {
                assert!(apart(*a, *b), "{a:?} {b:?}");
            }
        }
        let (px, py, pw, ph) = PANEL;
        assert!(px >= 300 && px + pw <= 1620 && py + ph < 690 && py >= 50, "between the pick columns, over the grid only");
        // in the header: right of red's turn arrow (x 1315-1355), left of the right-aligned lines (the swap phase's from
        // about x 1655 - the player's screenshot of 0.2.0 at x 1506 covered its first two characters)
        assert!(OPEN_BTN.1 + OPEN_BTN.3 <= 50 && OPEN_BTN.0 >= 1356 && OPEN_BTN.0 + OPEN_BTN.2 <= 1502);
    }

    #[test]
    fn every_button_is_in_the_source_and_parses_back() {
        let src = source();
        for id in clickables() {
            assert!(src.contains(&format!("#{id}:color_icon_button")), "{id}");
            assert!(parse_click(&id).is_some(), "{id}");
            assert!(path_of(&id).starts_with("main.hx_bp."));
        }
        assert_eq!(parse_click("c21"), Some(Click::Card(2, 1)));
        assert_eq!(parse_click("r30"), Some(Click::Reroll(3, 0)));
        assert_eq!(parse_click("s12"), Some(Click::Slot(1, 2)));
        assert_eq!(parse_click("s13"), None);
        assert_eq!(parse_click("t4"), Some(Click::Tab(4)));
        assert_eq!(parse_click("t5"), None);
        assert_eq!(parse_click("c43"), None);
        assert_eq!(parse_click("x"), None);
        assert_eq!(path_of("open"), "main.hx_bp.open");
        assert_eq!(path_of("c00"), "main.hx_bp.panel.c00");
        // the braces balance
        assert_eq!(src.matches('{').count(), src.matches('}').count());
    }

    #[test]
    fn the_players_side_is_read_from_the_team_names() {
        assert_eq!(side_of("T1", "T1 #1", "Gen.G #2"), Some(0));
        assert_eq!(side_of("gen.g", "T1 #1", "Gen.G #2"), Some(1));
        assert_eq!(side_of("DRX", "T1 #1", "Gen.G #2"), None);
        assert_eq!(side_of("", "", ""), None);
        assert_eq!(team_key("  Team 99 #12 "), "team 99");
        assert_eq!(team_key("Team #A"), "team #a");
    }
}
