//! 锻造看得见（用户 2026-11-01：「锻造后装备上加点特效？不然看不出啊」，选了样式 2「金色光晕 + 角上小铁砧」）：活体锻炉加强过
//! 的装备，在比赛下方玩家栏里图标外一圈金色光晕、右下角一个小铁砧；奥恩自己的（+`P_ITEM`%，锻造杰作后 +`P_MASTER`%）亮，
//! 锻造杰作后队友的（+`P_ALLY`%）淡；刚锻造（新装备、升级、杰作）时图标闪一下金光（`FLASH_T` tick）。
//!
//! 锻造在模拟里做（`Forge::forge`），屏幕放的是跑在前面的模拟的回放：屏幕上那一场（`ClientMatchView`、观战、回放）里被动每
//! `FORGE_EVERY` tick 记下友方每个选手（队伍、分路）的装备件数和锻造的百分比（变了才记），加的属性变多就记一次锻造（[`record`]）；
//! 画的时候按屏幕上的比赛时钟（`game_places::clock::screen_tick`）取那一刻的。屏幕在放哪一个模拟由 0 号玩家身上的 AI 钩子
//! [`Screen`] 记：换了场次、局，或者 tick 往回走就是另一个模拟，编号 +1（阿克尚 banner.rs 的做法）；只画编号对得上的记录，
//! 没有奥恩的那一场不会画上一场的。
//!
//! 玩家栏（Riot 装备 mod 的布局 ui/layout/ingame.ui、ingame_component/player_info.ui）：`ingame.player_info`（宽屏
//! `ingame.wide_data.player_info`）下每行一条分路，行里 `blue_player` / `red_player` 各有 `items`，装备图标是运行时放进去的子节点。
//! 行号 = 分路（`LaneV1`：上 0、野 1、中 2、下 3、辅 4）、`blue_player` = 0 队是推的：日志 `FX ROWS` 记下屏幕上每行的 KDA / 补刀，
//! 和模拟每 `STATS_EVERY` tick 记的 `STATS`（每条分路的英雄、KDA、补刀）对得上就是对的。
//!
//! 游戏每个 mod 只有一个客户端扩展槽：附加包合集里由 league_addons 的 `BundleClient` 调 [`draw`]，单独的 league_ornn.dll 用
//! [`Overlay`]。

use std::collections::HashMap;
use std::sync::Mutex;

use mod_api_stable::*;

/// 刚锻造时图标闪多久（tick）。
pub const FLASH_T: usize = 45;
/// 屏幕模拟的 AI 钩子隔多久看一次。
pub const SCREEN_EVERY: usize = 60;
/// 屏幕上那一场里多久记一次每条分路的英雄、KDA、补刀（日志 `STATS`）。
pub const STATS_EVERY: usize = 1_800;
/// 屏幕时钟走到这些 tick 时记一次 `FX ROWS`（1、3、6 分钟）。
pub const ROWS_AT: [usize; 3] = [3_600, 10_800, 21_600];
/// 玩家栏的两种布局（普通、宽屏）。
pub const PANELS: [&str; 2] = ["ingame.player_info", "ingame.wide_data.player_info"];
/// 行里的两边、各是哪一队。
pub const SIDES: [(&str, usize); 2] = [("blue_player", 0), ("red_player", 1)];

const UI: &str = "UI";
const GOLD: u32 = 0xf2_c4_4a_00;
const GOLD_HI: u32 = 0xff_e8_96_00;

/// 一个选手某一刻的锻造：装备件数、锻造的百分比（0 = 没有）、是不是奥恩自己（亮）。
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Forged {
    pub tick: usize,
    pub items: usize,
    pub pct: usize,
    pub own: bool,
}

#[derive(Clone, Debug, Default, PartialEq)]
pub struct Track {
    /// 变了才记，tick 递增。
    pub states: Vec<Forged>,
    /// 加的属性变多的 tick。
    pub flashes: Vec<usize>,
    last: Option<[i32; 6]>,
}

/// 屏幕上那一场的锻造记录：模拟编号、记到的最后一 tick、(队伍, 分路) -> 记录。
#[derive(Debug, Default)]
pub struct Board {
    pub gen: u64,
    pub tick: usize,
    pub tracks: HashMap<(usize, usize), Track>,
}

static BOARD: Mutex<Option<Board>> = Mutex::new(None);
/// (屏幕模拟的编号, 上一次看到的 (场次, 局, tick))。
static GEN: Mutex<(u64, Option<(u64, u64, usize)>)> = Mutex::new((0, None));
/// 客户端：(编号, 记过几次 `FX ROWS`, 记过 `FX DRAW` 没有)。
static SHOWN: Mutex<(u64, usize, bool)> = Mutex::new((0, 0, false));

/// 屏幕模拟走到 (`m`, `s`, `t`)：换了场次、局，或者 tick 往回走，是另一个模拟。-> 现在的编号
pub fn next_gen(gen: u64, last: Option<(u64, u64, usize)>, now: (u64, u64, usize)) -> u64 {
    match last {
        Some((m, s, t)) if (m, s) == (now.0, now.1) && now.2 >= t => gen,
        _ => gen + 1,
    }
}

pub fn note_screen(m: u64, s: u64, t: usize) {
    if let Ok(mut g) = GEN.lock() {
        g.0 = next_gen(g.0, g.1, (m, s, t));
        g.1 = Some((m, s, t));
    }
}

pub fn screen_gen() -> u64 {
    GEN.lock().map_or(0, |g| g.0)
}

/// 记一个选手（`key` = (队伍, 分路)）这一刻的锻造，`want` 是加在他身上的属性：编号换了、tick 往回走（同一个编号里换了模拟）
/// 就从头记；属性比上次多（新装备、升级、杰作）记一次锻造。
pub fn record(board: &mut Board, gen: u64, tick: usize, key: (usize, usize), items: usize, pct: usize, own: bool,
              want: [i32; 6]) {
    if board.gen != gen || tick < board.tick {
        *board = Board { gen, tick, tracks: HashMap::new() };
    }
    board.tick = tick;
    let tr = board.tracks.entry(key).or_default();
    if tr.states.last().is_none_or(|s| (s.items, s.pct, s.own) != (items, pct, own)) {
        tr.states.push(Forged { tick, items, pct, own });
    }
    if pct > 0 && (0..6).any(|i| want[i] > tr.last.map_or(0, |w| w[i])) {
        tr.flashes.push(tick);
    }
    tr.last = Some(want);
}

pub fn publish(gen: u64, tick: usize, key: (usize, usize), items: usize, pct: usize, own: bool, want: [i32; 6]) {
    if let Ok(mut b) = BOARD.lock() {
        record(b.get_or_insert_with(Board::default), gen, tick, key, items, pct, own, want);
    }
}

/// 屏幕时钟 `t` 时这个选手的锻造（tick ≤ t 的最后一条）。
pub fn state_at(tr: &Track, t: usize) -> Option<Forged> {
    tr.states.iter().rev().find(|s| s.tick <= t).copied()
}

/// 屏幕时钟 `t` 时离上一次锻造多久（`FLASH_T` 以内才算）。
pub fn flash_age(tr: &Track, t: usize) -> Option<usize> {
    tr.flashes.iter().rev().find(|&&f| f <= t).map(|&f| t - f).filter(|&a| a < FLASH_T)
}

/// 光晕：图标外三圈，(外扩多少，按 24 像素的图标算, 透明度)；奥恩自己的亮、队友的淡。
pub fn rings(own: bool) -> [(f32, u32); 3] {
    if own {
        [(1.0, 190), (2.4, 110), (3.8, 50)]
    } else {
        [(1.0, 120), (2.4, 65), (3.8, 28)]
    }
}

/// 右下角的小铁砧（图标 (x, y, w, h) 里）：底板、砧面、砧角、砧腰、砧脚，各 (x, y, w, h)。
pub fn anvil(icon: (f32, f32, f32, f32)) -> [(f32, f32, f32, f32); 5] {
    let (x, y, w, h) = icon;
    let a = w.min(h) * 0.42;
    let (ax, ay) = (x + w - a - w * 0.06, y + h - a * 0.84 - h * 0.06);
    [
        (ax - a * 0.08, ay - a * 0.08, a * 1.16, a * 1.0),
        (ax + a * 0.28, ay, a * 0.72, a * 0.3),
        (ax, ay + a * 0.06, a * 0.3, a * 0.16),
        (ax + a * 0.36, ay + a * 0.3, a * 0.28, a * 0.28),
        (ax + a * 0.16, ay + a * 0.58, a * 0.74, a * 0.24),
    ]
}

/// 这一次该记 `FX ROWS` 了（这个编号下记过 `done` 次）。
pub fn rows_due(done: usize, t: usize) -> bool {
    done < ROWS_AT.len() && t >= ROWS_AT[done]
}

/// 节点和它的每一层父节点都显示着。
fn shown(ctx: &StableClient<'_>, path: &str) -> bool {
    let parts: Vec<&str> = path.split('.').collect();
    (1..=parts.len()).all(|n| ctx.ui_visible(&parts[..n].join(".")) == Some(true))
}

fn frame(ctx: &mut StableClient<'_>, r: (f32, f32, f32, f32), lw: f32, z: i32, color: u32) {
    let (x0, y0, x1, y1) = (r.0, r.1, r.0 + r.2, r.1 + r.3);
    let e = lw / 2.0;
    ctx.draw_line(UI, x0 - e, y0, x1 + e, y0, lw, z, color);
    ctx.draw_line(UI, x0 - e, y1, x1 + e, y1, lw, z, color);
    ctx.draw_line(UI, x0, y0, x0, y1, lw, z, color);
    ctx.draw_line(UI, x1, y0, x1, y1, lw, z, color);
}

/// 一个装备图标上的光晕、小铁砧，刚锻造时再闪一下。
fn paint(ctx: &mut StableClient<'_>, r: (f32, f32, f32, f32), own: bool, flash: Option<usize>) {
    let (x, y, w, h) = r;
    let s = (w.min(h) / 24.0).max(0.5);
    for (k, (off, a)) in rings(own).into_iter().enumerate() {
        let o = off * s;
        frame(ctx, (x - o, y - o, w + 2.0 * o, h + 2.0 * o), 1.3 * s, 905 - k as i32, GOLD | a);
    }
    let parts = anvil(r);
    let b = parts[0];
    ctx.draw_rect(UI, b.0, b.1, b.2, b.3, 906, b.3 * 0.2, 0x1e_14_0a_c8);
    let col = if own { GOLD_HI } else { GOLD } | 0xff;
    for p in &parts[1..] {
        ctx.draw_rect(UI, p.0, p.1, p.2, p.3, 907, 0.0, col);
    }
    if let Some(age) = flash {
        let f = 1.0 - age as f32 / FLASH_T as f32;
        ctx.draw_rect(UI, x, y, w, h, 908, 2.0 * s, 0xff_f0_b4_00 | (150.0 * f) as u32);
        // a four-point glint at the top right
        let (cx, cy, l) = (x + w * 0.78, y + h * 0.22, w * 0.3 * (0.6 + 0.4 * f));
        let c = 0xff_ff_ff_00 | (255.0 * f) as u32;
        ctx.draw_line(UI, cx - l, cy, cx + l, cy, 1.4 * s, 909, c);
        ctx.draw_line(UI, cx, cy - l, cx, cy + l, 1.4 * s, 909, c);
    }
}

/// 画（客户端扩展的 post_render 里调）：屏幕上那一场里被锻造的选手，玩家栏里他的前几个装备图标（他有几件就几个）。
pub fn draw(ctx: &mut StableClient<'_>) {
    if !ctx.is_in_game() {
        return;
    }
    let Some(t) = game_places::clock::screen_tick() else { return };
    let gen = screen_gen();
    let now: Vec<((usize, usize), Forged, Option<usize>)> = {
        let Ok(b) = BOARD.lock() else { return };
        let Some(b) = b.as_ref().filter(|b| b.gen == gen) else { return };
        b.tracks.iter().filter_map(|(&k, tr)| state_at(tr, t).map(|s| (k, s, flash_age(tr, t)))).collect()
    };
    let (log_rows, log_draw) = {
        let Ok(mut s) = SHOWN.lock() else { return };
        if s.0 != gen {
            *s = (gen, 0, false);
        }
        let rows = rows_due(s.1, t);
        if rows {
            s.1 += 1;
        }
        (rows, !s.2)
    };
    let mut drawn = Vec::new();
    for panel in PANELS {
        if !shown(ctx, panel) {
            continue;
        }
        let mut seen = Vec::new();
        for (lane, row) in ctx.ui_child_names(panel).iter().enumerate() {
            for (side, team) in SIDES {
                let base = format!("{panel}.{row}.{side}");
                let items = format!("{base}.items");
                let icons = ctx.ui_child_names(&items);
                let state = now.iter().find(|(k, _, _)| *k == (team, lane));
                if log_rows {
                    let kda = ctx.ui_text(&format!("{base}.kda")).unwrap_or_default();
                    let cs = ctx.ui_text(&format!("{base}.cs.value")).unwrap_or_default();
                    let forged = state.map_or("-".to_string(), |(_, s, _)| format!("{} items +{}%", s.items, s.pct));
                    seen.push(format!("{row}.{side} {kda} cs {cs} icons {} [team {team} lane {lane}: {forged}]", icons.len()));
                }
                let Some(&(_, s, flash)) = state.filter(|(_, s, _)| s.pct > 0) else { continue };
                for icon in icons.iter().take(s.items) {
                    let Some(r) = ctx.ui_node_rect(&format!("{items}.{icon}")).filter(|r| r.2 > 1.0 && r.3 > 1.0) else {
                        continue;
                    };
                    paint(ctx, r, s.own, flash);
                    drawn.push((team, lane, r));
                }
            }
        }
        if log_rows {
            if let Some(k) = super::counted("fx rows") {
                let size = ctx.draw_map_size(UI).map_or("?".to_string(), |(w, h)| format!("{w:.0}x{h:.0}"));
                super::wlog(format!("FX ROWS gen {gen} screen t={t} {panel} (UI {size}): {} #{k}", seen.join(" | ")));
            }
        }
    }
    if log_draw && !drawn.is_empty() {
        if let Ok(mut s) = SHOWN.lock() {
            s.2 = true;
        }
        if let Some(k) = super::counted("fx draw") {
            let (team, lane, r) = drawn[0];
            super::wlog(format!("FX DRAW gen {gen} screen t={t}: {} forged item icons, the first team {team} lane {lane} at \
                                 ({:.0}, {:.0}, {:.0}x{:.0}) #{k}", drawn.len(), r.0, r.1, r.2, r.3));
        }
    }
}

/// 记屏幕在放哪一个模拟：每个模拟 0 号玩家身上的 AI 钩子，隔 `SCREEN_EVERY` tick 看一次，只旁观、不改输入。
#[derive(Clone, Default)]
pub struct Screen {
    last: Option<usize>,
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
        if self.last.is_none_or(|l| t < l || t >= l + SCREEN_EVERY) {
            self.last = Some(t);
            if let Some(o) = ctx.sim().filter(|sim| super::on_screen(sim)).and_then(|sim| sim.sim_origin()) {
                note_screen(o.match_id, o.set_index, t);
            }
        }
        None
    }
}

/// 单独装的 league_ornn.dll 的客户端扩展：喂屏幕时钟（league_neeko 的 ClockFeed 的做法）、画锻造。
#[cfg_attr(league_bundle, allow(dead_code))]
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
        draw(ctx);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_new_sim_on_screen_gets_a_new_number() {
        assert_eq!(next_gen(0, None, (5, 1, 0)), 1);
        assert_eq!(next_gen(1, Some((5, 1, 0)), (5, 1, 60)), 1, "the same sim going on");
        assert_eq!(next_gen(1, Some((5, 1, 9000)), (5, 1, 60)), 2, "the tick went back: another sim");
        assert_eq!(next_gen(2, Some((5, 1, 60)), (5, 2, 60)), 3, "the next game of the series");
        assert_eq!(next_gen(3, Some((5, 2, 60)), (6, 1, 120)), 4, "another match");
    }

    #[test]
    fn the_board_keeps_changes_and_flashes_on_more_stats() {
        let mut b = Board::default();
        let key = (0, 2);
        record(&mut b, 1, 30, key, 1, 20, true, [0, 0, 0, 20, 0, 0]);
        record(&mut b, 1, 60, key, 1, 20, true, [0, 0, 0, 20, 0, 0]);
        record(&mut b, 1, 90, key, 2, 20, true, [0, 0, 5, 40, 0, 0]);
        record(&mut b, 1, 120, (0, 3), 2, 0, false, [0; 6]);
        let tr = &b.tracks[&key];
        assert_eq!(tr.states.iter().map(|s| (s.tick, s.items)).collect::<Vec<_>>(), [(30, 1), (90, 2)]);
        assert_eq!(tr.flashes, [30, 90], "his first item, then the second");
        assert!(b.tracks[&(0, 3)].flashes.is_empty(), "an ally before the masterwork: nothing forged");
        // the screen lags behind the sim
        assert_eq!(state_at(tr, 10), None);
        assert_eq!(state_at(tr, 75).map(|s| s.items), Some(1));
        assert_eq!(state_at(tr, 9_000).map(|s| s.items), Some(2));
        assert_eq!(flash_age(tr, 100), Some(10));
        assert_eq!(flash_age(tr, 90 + FLASH_T), None);
        // the masterwork forges the ally's items: a flash
        record(&mut b, 1, 150, (0, 3), 2, 10, false, [10, 0, 0, 0, 0, 0]);
        assert_eq!(b.tracks[&(0, 3)].flashes, [150]);
        // another sim (number or tick back): from scratch
        record(&mut b, 1, 30, key, 1, 20, true, [0, 0, 0, 20, 0, 0]);
        assert_eq!(b.tracks.len(), 1);
        record(&mut b, 2, 60, key, 1, 20, true, [0, 0, 0, 20, 0, 0]);
        assert_eq!((b.gen, b.tracks[&key].states.len()), (2, 1));
    }

    #[test]
    fn the_glow_and_the_anvil_sit_on_the_icon() {
        let icon = (100.0, 50.0, 24.0, 24.0);
        for p in anvil(icon) {
            assert!(p.0 >= icon.0 && p.1 >= icon.1 && p.0 + p.2 <= icon.0 + icon.2 + 0.01 && p.1 + p.3 <= icon.1 + icon.3 + 0.01,
                    "{p:?} leaves the icon");
        }
        let a = anvil(icon);
        assert!(a[1].0 > icon.0 + icon.2 / 2.0 && a[4].1 > icon.1 + icon.3 / 2.0, "in the bottom right corner");
        let (own, ally) = (rings(true), rings(false));
        assert!(own.iter().zip(ally.iter()).all(|(o, a)| o.1 > a.1), "his own items glow brighter");
        assert!(own.windows(2).all(|w| w[0].0 < w[1].0 && w[0].1 > w[1].1), "fainter further out");
    }

    #[test]
    fn rows_are_logged_three_times_a_match() {
        assert!(!rows_due(0, 3_000));
        assert!(rows_due(0, 3_600));
        assert!(!rows_due(1, 9_000));
        assert!(rows_due(2, 30_000));
        assert!(!rows_due(3, 90_000));
    }
}
