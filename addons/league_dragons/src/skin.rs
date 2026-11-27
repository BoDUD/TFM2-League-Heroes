//! 小龙按元素换外观、纳什男爵换成 Codex 的模型（0.2.0，用户 2026-11-09：「大小龙模型呢？codex做吗 还有攻击动画」「你要参考
//! 英雄联盟里面的攻击姿势啊」「龙魂的也都交付了 你处理完」）。
//!
//! 图在本包的 `effects/`（tools/art/dragons_hd.py 从 Codex 的两次交付读出来的）：`league_drake_<元素>`（六种元素亚龙）、
//! `league_drake_elder`、`league_baron`，动作名和原生的一样（双角巨蛇 idle / base / attack / dead，莫尔加德 idle / base /
//! attack_left / attack_right / attack_target_effect / dead），所以只换图、不换动作名。`mod.override_info` 把
//! `asset/base/aseprite_resources/ingame/<名字>` 指到这些图；league.dll 0.9.25 起它们登记成高清（league_main hd.rs
//! EFFECTS），身体绘制按资源名找到、按 1 / PPU 画。
//!
//! 显示钩子（`game_places::hook`，妮蔻、佛耶戈的那一个）每帧走显示世界的实体：资源名（值 +0x50 的 String）最后一段是
//! `serpen_monster`（游戏里小龙的资源名，日志 `SKIN seen`）的换成这一刻该是的元素亚龙，`epic_monster` 的换成 `league_baron`。
//! 游戏 0.6.3 起画身体按这个资源名取图（妮蔻同一个字段；凯隐当初改的是名字字段，没用），不认识的名字按英雄的
//! `aseprite_resources/champions/<名字>` 去找，所以 `mod.override_info` 把 champions 和 ingame 两种路径都指到本包的图。哪一种元素：显示世界收不到原生加的 buff（佛耶戈 0.1.3 / 0.1.6、妮蔻的教训），所以按屏幕上的比赛时钟
//! （`game_places::clock::screen_tick`）在 [`super::feed`] 里找这一场到这一刻为止最近的一次「元素亚龙出生 / 远古巨龙
//! 出生」；还没有（模组冲突时本包什么都不做，也就没有）或读不到时钟就不换，画原生的。0.3.3 起先按实体编号找（屏幕那一场
//! 小龙出生时 [`super::feed::drake_born`] 记下编号和元素，显示世界的实体是同一个编号）：倒退 / 快进回放时屏幕时钟读不到，
//! 只按时钟找会画回原生的（用户：「倒退看回放的时候小龙的模型又恢复成原样了」）；两样都没有时用这个实体上次换成的。每个实体换了什么记一行日志
//! （`SKIN`），第一次见到小龙 / 莫尔加德时把它原来的资源名也记下来。
//!
//! 0.5.12（用户 2026-11-26：「我们的小龙在大地图的龙坑站位方向应该朝着外面吧 要和原版地图不一样吧 这个得改一下吧」）：Rin 的召唤师
//! 峡谷上小龙坑被墙围了大半圈、只朝右上方开口，正面朝着镜头的龙等于脸对着墙。那张地图上（读阵容时认出来，[`super::feed::is_rift`]）
//! 元素亚龙和远古巨龙换成 Codex 第 3 步转身朝右上方的那一套 `league_drake_<元素>_rift`（[`on_map`]，tools/art/dragons_rift_hd.py），
//! 游戏自带的地图照旧是正面的。纳什男爵两张地图一样。
//!
//! 0.5.15（用户 2026-11-27：「小龙头的朝向有的还是不对啊 比如风龙 有的朝向还是看左边的」「风龙朝向还是和原地图一样的 好像其他有的
//! 元素龙会看左边」）两处：
//! - 看左边：游戏出招、普攻时把身体转向目标——显示实体值 +0x1bc 的一个字节，1 = 把图水平翻过来画（[`FLIP`]，卢锡安 view.rs 记过）。
//!   目标在左边时，只画了朝右上方坑口的那一套就被翻成了朝左上。所以画的是那一套时每一步把它写回 0（[`faces_the_pit`]）。
//! - 和原地图一样：系列赛第二、三局开头游戏还在后台重跑上一局，两场来回切，读阵容时记下的「这一场在峡谷上」被清掉了（feed.rs 的
//!   `RIFT`），小龙画回了正面那套。

use std::sync::{Mutex, Once};

use super::feed::{self, What};
use super::wlog;
use game_places::hook::{Ent, NAME_LEN_AT, NAME_PTR, VALUE};

/// The display entity value's body resource name: String {cap, ptr, len} at +0x50 (league_neeko view.rs).
const RES_CAP: usize = 0x50;
/// 显示实体值里的朝向（bool：1 = 画成水平翻转，朝左；league_lucian view.rs 的 `FLIP`）。游戏每走一步按横向走的方向、每次出招按
/// 目标在哪边写它；0.7.3 的身体绘制（rva 0x2751f90）在 0x2752b48 读这个字节。
const FLIP: usize = 0x1bc;
/// The native monsters' names: the display entity's resource (and name) is `serpen_monster` / `epic_monster` (league_dragons.log
/// `SKIN seen`, 2026-11-10; the sprites are ingame/serpen and ingame/epic).
const SERPEN: &str = "serpen";
const EPIC: &str = "epic";
const SERPEN_MONSTER: &str = "serpen_monster";
const EPIC_MONSTER: &str = "epic_monster";
pub(crate) const DRAKE_PREFIX: &str = "league_drake_";
pub const BARON: &str = "league_baron";

/// What a resource name is the body of.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    Drake,
    Baron,
}

/// (prefix, last part) of a resource name: `asset/base/aseprite_resources/ingame/serpen` -> (`asset/…/ingame/`,
/// `serpen`); a `#…` suffix is left to the caller (resource names have none).
fn split(res: &str) -> (&str, &str) {
    match res.rfind(['/', '\\']) {
        Some(i) => (&res[..=i], &res[i + 1..]),
        None => ("", res),
    }
}

/// The monster a resource name draws: the native one or ours.
pub fn kind_of(res: &str) -> Option<Kind> {
    let (_, last) = split(res);
    if last == SERPEN || last == SERPEN_MONSTER || last.starts_with(DRAKE_PREFIX) {
        Some(Kind::Drake)
    } else if last == EPIC || last == EPIC_MONSTER || last == BARON {
        Some(Kind::Baron)
    } else {
        None
    }
}

/// The monster an entity's name says it is: the simulation calls the drake `serpen_monster` (league_dragons.log SPAWN),
/// and the display entity may carry such a name rather than a resource ending in `serpen`.
pub fn kind_of_name(name: &str) -> Option<Kind> {
    let n = name.to_ascii_lowercase();
    if n.contains(SERPEN) || n.contains("league_drake_") {
        Some(Kind::Drake)
    } else if n.starts_with(EPIC) || n.contains("_epic") || n.contains("morgard") || n.contains(BARON) {
        Some(Kind::Baron)
    } else {
        None
    }
}

/// The resource name with its last part `want` (the prefix kept), or None when it already is.
pub fn renamed(res: &str, want: &str) -> Option<String> {
    let (prefix, last) = split(res);
    (last != want).then(|| format!("{prefix}{want}"))
}

/// Our sheet for the drake alive at sim tick `t`: the last drake / Elder spawn at or before it.
pub fn drake_at(events: &[feed::Event], t: usize) -> Option<String> {
    events
        .iter()
        .filter(|e| e.tick <= t)
        .filter_map(|e| match &e.what {
            What::DrakeSpawn { element } => Some((e.tick, format!("{DRAKE_PREFIX}{}", element.key()))),
            What::ElderSpawn => Some((e.tick, format!("{DRAKE_PREFIX}elder"))),
            _ => None,
        })
        .max_by_key(|(tick, _)| *tick)
        .map(|(_, name)| name)
}

/// Sim ticks the drake's display entity can show up before this add-on records its spawn (2026-11-10's log: the entity
/// drawn at screen tick 16953, its spawn event at 16981, so it was the previous drake's element for half a second). The
/// next drake spawns two minutes after a kill, so looking a second ahead never picks it early.
pub(crate) const SPAWN_LEAD: usize = 60;

/// Our sheet for an element (the Elder's too).
pub fn sheet_of(element: super::rules::Element) -> String {
    format!("{DRAKE_PREFIX}{}", element.key())
}

/// 峡谷版那一套的名字后缀：`league_drake_<元素>_rift`（tools/art/dragons_rift_hd.py）。
pub const RIFT_SUFFIX: &str = "_rift";

/// 这条龙在这张地图上画哪一套：Rin 的召唤师峡谷上小龙坑只朝右上方开口，换成转身朝坑口的那一套（0.5.12，用户 2026-11-26：
/// 「我们的小龙在大地图的龙坑站位方向应该朝着外面吧 要和原版地图不一样吧」）；别的地图照旧是正面的。
pub fn on_map(sheet: String, rift: bool) -> String {
    if rift && !sheet.ends_with(RIFT_SUFFIX) {
        format!("{sheet}{RIFT_SUFFIX}")
    } else {
        sheet
    }
}

/// 这个资源名画的是不是峡谷那一套小龙：只画了朝右上方坑口的一面，不能让游戏左右翻过来画（0.5.15）。
pub fn faces_the_pit(res: &str) -> bool {
    let (_, last) = split(res);
    last.starts_with(DRAKE_PREFIX) && last.ends_with(RIFT_SUFFIX)
}

/// What the drake with entity id `key` should be drawn as: the element its spawn recorded (the display world's entities
/// carry the simulation's ids), else the last drake / Elder spawn before the screen clock; None when neither is known.
/// The id comes first: while a replay is wound back or forward the clock reads nothing (2026-11-10's log: the drake back
/// on screen with `screen tick None`, drawn native - the user: 「倒退看回放的时候小龙的模型又恢复成原样了」).
/// On Rin's Summoner's Rift the sheet is the one turned to the pit's opening ([`on_map`]).
fn drake_for(key: u64) -> Option<String> {
    let (m, s) = feed::current()?;
    let sheet = match feed::drake_of(m, s, key as usize) {
        Some(e) => sheet_of(e),
        None => {
            let t = game_places::clock::screen_tick()?;
            drake_at(&feed::events(m, s), t + SPAWN_LEAD)?
        }
    };
    Some(on_map(sheet, feed::is_rift(m, s)))
}

static HOOK: Once = Once::new();
/// (display world, key) -> what it was last drawn as (a line when it changes).
static LOOKS: Mutex<Vec<(usize, u64, String)>> = Mutex::new(Vec::new());

#[link(name = "kernel32")]
extern "system" {
    fn GetProcessHeap() -> isize;
    fn HeapAlloc(heap: isize, flags: u32, bytes: usize) -> *mut u8;
    fn HeapFree(heap: isize, flags: u32, mem: *mut u8) -> i32;
}

unsafe fn q(addr: usize) -> usize {
    std::ptr::read_unaligned(addr as *const usize)
}

fn plausible(p: usize) -> bool {
    (0x10000..0x7fff_ffff_ffff).contains(&p)
}

unsafe fn string_at(at: usize, max: usize) -> Option<String> {
    let (cap, ptr, len) = (q(at), q(at + 8), q(at + 16));
    if !(len >= 1 && len <= max && cap >= len && plausible(ptr)) {
        return None;
    }
    std::str::from_utf8(std::slice::from_raw_parts(ptr as *const u8, len)).ok().map(str::to_string)
}

/// A String {cap, ptr, len} the game owns on its heap: a capacity no bigger than 1 GiB and at least the length. Only such
/// a String is replaced (a borrowed or static one starts with no such capacity, and freeing it would crash the game).
unsafe fn owned_string_at(at: usize, max: usize) -> Option<String> {
    let cap = q(at);
    (cap <= 1 << 30).then(|| string_at(at, max)).flatten().filter(|s| s.len() <= cap)
}

/// The display entity's name: +0x40 pointer, +0x48 length (game_places::hook).
unsafe fn name_of(v: usize) -> Option<String> {
    let (n, p) = (q(v + NAME_LEN_AT), q(v + NAME_PTR));
    ((1..=64).contains(&n) && plausible(p))
        .then(|| String::from_utf8_lossy(std::slice::from_raw_parts(p as *const u8, n)).into_owned())
}

/// A new String in the game's heap at `at` (the old one freed the game's way, league_neeko view.rs) - only over an owned
/// String ([`owned_string_at`]).
unsafe fn put_string(at: usize, want: &[u8]) -> bool {
    let (cap, ptr) = (q(at), q(at + 8));
    if cap > 1 << 30 {
        return false;
    }
    let heap = GetProcessHeap();
    let fresh = HeapAlloc(heap, 0, want.len().max(1));
    if fresh.is_null() {
        return false;
    }
    std::ptr::copy_nonoverlapping(want.as_ptr(), fresh, want.len());
    std::ptr::write_unaligned(at as *mut usize, want.len());
    std::ptr::write_unaligned((at + 8) as *mut usize, fresh as usize);
    std::ptr::write_unaligned((at + 16) as *mut usize, want.len());
    if cap > 0 && plausible(ptr) {
        HeapFree(heap, 0, ptr as *mut u8);
    }
    true
}

/// (display world, key, animation) of the monsters on screen: each animation they play is logged once (`SKIN ... plays`),
/// and when one leaves the screen (`SKIN ... gone`) - to see their attack and death play (the user: 「小龙没有攻击动作 死亡动作」).
static TRACK: Mutex<Vec<(usize, u64, String)>> = Mutex::new(Vec::new());
static PLAYED: Mutex<Vec<(usize, u64, String)>> = Mutex::new(Vec::new());

/// (display world, key) of every entity already written out by [`describe`].
static SEEN: Mutex<Vec<(usize, u64)>> = Mutex::new(Vec::new());

/// (显示世界, 实体号, 翻回去几次)：峡谷那一套小龙被游戏转向左边、本包又转回坑口的（第一次记一行日志，离开画面时写总数）。
static TURNED: Mutex<Vec<(usize, u64, u32)>> = Mutex::new(Vec::new());

/// One log line of a display entity as it is: its name, its resource and animation read as Strings, and the raw words
/// from +0x38 to +0xa0 of its value (to see how a monster's differ from a champion's).
unsafe fn describe(v: usize) -> String {
    let words: Vec<String> = (0..14).map(|i| format!("{:x}", q(v + 0x38 + 8 * i))).collect();
    format!("name {:?}, resource {:?} (owned {}), animation {:?}, words +0x38.. [{}]", name_of(v), string_at(v + RES_CAP, 160),
            owned_string_at(v + RES_CAP, 160).is_some(), string_at(v + 0x68, 64), words.join(" "))
}

unsafe fn dress(world: usize, ents: &[Ent]) {
    let (Ok(mut looks), Ok(mut seen), Ok(mut track), Ok(mut played), Ok(mut turned)) =
        (LOOKS.try_lock(), SEEN.try_lock(), TRACK.try_lock(), PLAYED.try_lock(), TURNED.try_lock())
    else {
        return;
    };
    let mut described_here = seen.iter().filter(|s| s.0 == world).count();
    let mut here: Vec<u64> = Vec::new();
    for e in ents {
        let v = e.elem + VALUE;
        let key = e.key;
        let res = string_at(v + RES_CAP, 160);
        let name = name_of(v);
        let by_res = res.as_deref().and_then(kind_of);
        let kind = by_res.or_else(|| name.as_deref().and_then(kind_of_name));
        // every monster once, and the first four entities of a world (champions) to compare with
        if (kind.is_some() || described_here < 4) && !seen.contains(&(world, key)) {
            seen.push((world, key));
            if seen.len() > 512 {
                seen.remove(0);
            }
            described_here += 1;
            wlog(format!("SKIN seen world {world:#x} #{key}{}: {}",
                         match kind { Some(Kind::Drake) => " (a drake)", Some(Kind::Baron) => " (Baron)", None => "" }, describe(v)));
        }
        let Some(kind) = kind else { continue };
        here.push(key);
        let anim = string_at(v + 0x68, 64).unwrap_or_default();
        match track.iter_mut().find(|t| t.0 == world && t.1 == key) {
            Some(t) => t.2.clone_from(&anim),
            None => track.push((world, key, anim.clone())),
        }
        if !played.iter().any(|p| p.0 == world && p.1 == key && p.2 == anim) && played.len() < 400 {
            played.push((world, key, anim.clone()));
            wlog(format!("SKIN world {world:#x} #{key}: plays {anim:?} (resource {:?}, facing byte {}, screen tick {:?})",
                         string_at(v + RES_CAP, 160), *((v + FLIP) as *const u8), game_places::clock::screen_tick()));
        }
        let want = match kind {
            Kind::Baron => Some(BARON.to_string()),
            // by id, by the clock, else what this entity was last drawn as (it is the same drake)
            Kind::Drake => drake_for(key)
                .or_else(|| looks.iter().find(|l| l.0 == world && l.1 == key).map(|l| l.2.clone())),
        };
        let Some(want) = want else { continue };
        // only a resource whose last part is the native monster's (or ours) is renamed, and only an owned String
        if by_res.is_none() {
            continue;
        }
        let Some(res) = owned_string_at(v + RES_CAP, 160) else { continue };
        if let Some(new) = renamed(&res, &want) {
            if put_string(v + RES_CAP, new.as_bytes()) && !looks.iter().any(|l| l.0 == world && l.1 == key && l.2 == want) {
                looks.retain(|l| !(l.0 == world && l.1 == key));
                looks.push((world, key, want.clone()));
                if looks.len() > 64 {
                    looks.remove(0);
                }
                wlog(format!("SKIN world {world:#x} #{key}: drawn as {new} (screen tick {:?})",
                             game_places::clock::screen_tick()));
            }
        }
        // 峡谷那一套只画了朝右上方坑口的一面：游戏打左边的人时把它翻成朝左上，这里翻回去。这个字节只该是 0 / 1，别的值不碰
        if string_at(v + RES_CAP, 160).is_some_and(|r| faces_the_pit(&r)) {
            let flip = (v + FLIP) as *mut u8;
            if *flip == 1 {
                *flip = 0;
                match turned.iter_mut().find(|t| t.0 == world && t.1 == key) {
                    Some(t) => t.2 += 1,
                    None => {
                        if turned.len() >= 64 {
                            turned.remove(0);
                        }
                        turned.push((world, key, 1));
                        wlog(format!("SKIN world {world:#x} #{key}: the game turned it to face left ({anim:?}, a target on its left) - \
                                      turned back to the pit's opening (screen tick {:?})", game_places::clock::screen_tick()));
                    }
                }
            }
        }
    }
    track.retain(|t| {
        let stays = t.0 != world || here.contains(&t.1);
        if !stays {
            let back = turned.iter().find(|x| x.0 == t.0 && x.1 == t.1).map_or(0, |x| x.2);
            wlog(format!("SKIN world {world:#x} #{}: gone (last animation {:?}, screen tick {:?}{})", t.1, t.2,
                         game_places::clock::screen_tick(),
                         if back > 0 { format!(", turned back to the pit {back} times") } else { String::new() }));
        }
        stays
    });
    turned.retain(|x| x.0 != world || here.contains(&x.1));
}

/// 加载时挂上显示钩子（一个 DLL 只挂一次）。
pub fn install_once() {
    HOOK.call_once(|| match game_places::hook::add("league_dragons", dress, |m: &str| wlog(m)) {
        Ok(p) => wlog(format!("SKIN on: {p}: drakes by element, Baron Nashor")),
        Err(e) => wlog(format!("SKIN off ({e}): the drakes and Baron keep the game's look")),
    });
}

#[cfg(test)]
mod tests {
    use super::super::rules::Element;
    use super::*;

    fn ev(tick: usize, what: What) -> feed::Event {
        feed::Event { m: 1, s: 1, tick, what }
    }

    #[test]
    fn the_native_monsters_and_ours_are_recognised_by_the_last_part() {
        assert_eq!(kind_of("serpen"), Some(Kind::Drake));
        assert_eq!(kind_of("ingame/serpen"), Some(Kind::Drake));
        assert_eq!(kind_of("asset/base/aseprite_resources/ingame/serpen"), Some(Kind::Drake));
        assert_eq!(kind_of("asset/base/aseprite_resources/ingame/league_drake_ocean"), Some(Kind::Drake));
        assert_eq!(kind_of("epic"), Some(Kind::Baron));
        assert_eq!(kind_of("serpen_monster"), Some(Kind::Drake));
        assert_eq!(kind_of("epic_monster"), Some(Kind::Baron));
        assert_eq!(kind_of("ingame/league_baron"), Some(Kind::Baron));
        assert_eq!(kind_of("ingame/serpentine"), None);
        assert_eq!(kind_of("league_jinx"), None);
        assert_eq!(kind_of("ingame/epic_buff_animation"), None);
    }

    #[test]
    fn the_simulations_monster_names_are_recognised_too() {
        assert_eq!(kind_of_name("serpen_monster"), Some(Kind::Drake));
        assert_eq!(kind_of_name("epic_monster"), Some(Kind::Baron));
        assert_eq!(kind_of_name("league_jinx"), None);
        assert_eq!(kind_of_name("blue_minion"), None);
    }

    #[test]
    fn renaming_keeps_the_prefix_and_is_idempotent() {
        assert_eq!(renamed("serpen", "league_drake_infernal").as_deref(), Some("league_drake_infernal"));
        assert_eq!(renamed("serpen_monster", "league_drake_ocean").as_deref(), Some("league_drake_ocean"));
        assert_eq!(renamed("epic_monster", BARON).as_deref(), Some("league_baron"));
        assert_eq!(renamed("ingame/serpen", "league_drake_infernal").as_deref(), Some("ingame/league_drake_infernal"));
        assert_eq!(renamed("asset/base/aseprite_resources/ingame/epic", BARON).as_deref(),
                   Some("asset/base/aseprite_resources/ingame/league_baron"));
        assert_eq!(renamed("ingame/league_drake_infernal", "league_drake_ocean").as_deref(), Some("ingame/league_drake_ocean"));
        assert_eq!(renamed("ingame/league_baron", BARON), None);
    }

    #[test]
    fn the_drake_on_screen_is_the_last_spawn_before_the_screen_tick() {
        let evs = vec![
            ev(7200, What::DrakeSpawn { element: Element::Ocean }),
            ev(8000, What::Drake { team: 0, element: Element::Ocean, total: 1 }),
            ev(14400, What::DrakeSpawn { element: Element::Cloud }),
            ev(40000, What::ElderSpawn),
        ];
        assert_eq!(drake_at(&evs, 100), None);
        assert_eq!(drake_at(&evs, 7200).as_deref(), Some("league_drake_ocean"));
        assert_eq!(drake_at(&evs, 9000).as_deref(), Some("league_drake_ocean"));
        assert_eq!(drake_at(&evs, 14400).as_deref(), Some("league_drake_cloud"));
        assert_eq!(drake_at(&evs, 50000).as_deref(), Some("league_drake_elder"));
    }

    #[test]
    fn on_rins_rift_the_drakes_are_the_sheets_turned_to_the_pit() {
        assert_eq!(on_map(sheet_of(Element::Ocean), false), "league_drake_ocean");
        assert_eq!(on_map(sheet_of(Element::Ocean), true), "league_drake_ocean_rift");
        assert_eq!(on_map(sheet_of(Element::Elder), true), "league_drake_elder_rift");
        // 已经是峡谷版的不会再加一次
        assert_eq!(on_map("league_drake_cloud_rift".to_string(), true), "league_drake_cloud_rift");
        // 峡谷版也认得出是小龙、改名照旧保留前缀
        assert_eq!(kind_of("asset/base/aseprite_resources/ingame/league_drake_hextech_rift"), Some(Kind::Drake));
        assert_eq!(renamed("serpen_monster", "league_drake_infernal_rift").as_deref(), Some("league_drake_infernal_rift"));
        assert_eq!(renamed("ingame/league_drake_infernal", "league_drake_infernal_rift").as_deref(),
                   Some("ingame/league_drake_infernal_rift"));
    }

    #[test]
    fn only_the_sheets_turned_to_the_pit_are_kept_from_being_mirrored() {
        // 峡谷那一套（六种元素和远古巨龙）不许游戏左右翻
        for e in [Element::Infernal, Element::Mountain, Element::Ocean, Element::Cloud, Element::Hextech, Element::Chemtech,
                  Element::Elder] {
            assert!(faces_the_pit(&format!("asset/base/aseprite_resources/ingame/{}", on_map(sheet_of(e), true))));
            // 正面那一套、游戏自己的小龙照旧让游戏转向目标
            assert!(!faces_the_pit(&format!("asset/base/aseprite_resources/ingame/{}", sheet_of(e))));
        }
        assert!(!faces_the_pit("ingame/serpen"));
        assert!(!faces_the_pit("serpen_monster"));
        assert!(!faces_the_pit("ingame/league_baron"));
        assert!(!faces_the_pit("league_rift"));
    }

    #[test]
    fn every_sheet_the_skin_names_ships_with_the_add_on_and_is_remapped() {
        let ov = include_str!("../mod.override_info");
        let elements = [Element::Infernal, Element::Mountain, Element::Ocean, Element::Cloud, Element::Hextech, Element::Chemtech,
                        Element::Elder];
        let mut names: Vec<String> = elements.iter().map(|e| sheet_of(*e)).collect();
        // Rin 的召唤师峡谷上的那一套
        names.extend(elements.iter().map(|e| on_map(sheet_of(*e), true)));
        names.push(BARON.to_string());
        // the add-on's own folder, also when league_addons compiles this file as one of its modules
        let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("..").join("league_dragons").join("effects");
        for n in names {
            for (dir, kind) in [("ingame", "sheet"), ("ingame", "anim"), ("champions", "sheet"), ("champions", "anim")] {
                let key = format!("\"asset/base/aseprite_resources/{dir}/{n}#{kind}\"");
                assert!(ov.contains(&key), "{key} not remapped");
                assert!(ov.contains(&format!("\"asset/league_dragons/effects/{n}#{kind}\"")), "{n}#{kind} remapped elsewhere");
            }
            assert!(dir.join(format!("{n}#sheet.png")).is_file(), "{n}#sheet.png missing");
            assert!(dir.join(format!("{n}#anim.fanim")).is_file(), "{n}#anim.fanim missing");
        }
    }
}
