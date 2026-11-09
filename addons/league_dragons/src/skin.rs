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
//! `serpen` 的换成这一刻该是的元素亚龙，`epic` 的换成 `league_baron`；前面的部分（路径前缀）原样留着，游戏怎么拼路径都
//! 对得上。哪一种元素：显示世界收不到原生加的 buff（佛耶戈 0.1.3 / 0.1.6、妮蔻的教训），所以按屏幕上的比赛时钟
//! （`game_places::clock::screen_tick`）在 [`super::feed`] 里找这一场到这一刻为止最近的一次「元素亚龙出生 / 远古巨龙
//! 出生」；还没有（模组冲突时本包什么都不做，也就没有）或读不到时钟就不换，画原生的。每个实体换了什么记一行日志
//! （`SKIN`），第一次见到小龙 / 莫尔加德时把它原来的资源名也记下来。

use std::sync::{Mutex, Once};

use super::feed::{self, What};
use super::wlog;
use game_places::hook::{Ent, VALUE};

/// The display entity value's body resource name: String {cap, ptr, len} at +0x50 (league_neeko view.rs).
const RES_CAP: usize = 0x50;
/// The native monsters' resource names (the last part).
const SERPEN: &str = "serpen";
const EPIC: &str = "epic";
const DRAKE_PREFIX: &str = "league_drake_";
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
    if last == SERPEN || last.starts_with(DRAKE_PREFIX) {
        Some(Kind::Drake)
    } else if last == EPIC || last == BARON {
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

/// What the drake should be drawn as now on screen: None when the screen's match, clock or drake is unknown.
fn drake_now() -> Option<String> {
    let (m, s) = feed::current()?;
    let t = game_places::clock::screen_tick()?;
    drake_at(&feed::events(m, s), t)
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

/// A new String in the game's heap at `at` (the old one freed the game's way, league_neeko view.rs).
unsafe fn put_string(at: usize, want: &[u8]) -> bool {
    let (cap, ptr) = (q(at), q(at + 8));
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

unsafe fn dress(world: usize, ents: &[Ent]) {
    let mut drake: Option<Option<String>> = None; // asked once a frame, only when a drake is on screen
    let Ok(mut looks) = LOOKS.try_lock() else { return };
    for e in ents {
        let v = e.elem + VALUE;
        let Some(res) = string_at(v + RES_CAP, 160) else { continue };
        let Some(kind) = kind_of(&res) else { continue };
        let want = match kind {
            Kind::Baron => Some(BARON.to_string()),
            Kind::Drake => drake.get_or_insert_with(drake_now).clone(),
        };
        let Some(want) = want else { continue };
        let key = e.key;
        if !looks.iter().any(|l| l.0 == world && l.1 == key) {
            wlog(format!("SKIN world {world:#x} #{key}: a {} on screen, resource {res:?}",
                         if kind == Kind::Drake { "drake" } else { "Baron" }));
        }
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
        } else if !looks.iter().any(|l| l.0 == world && l.1 == key) {
            looks.push((world, key, want));
        }
    }
}

/// 加载时挂上显示钩子（一个 DLL 只挂一次）。
pub fn install_once() {
    HOOK.call_once(|| match game_places::hook::add("league_dragons", dress) {
        Ok((slot, prev)) => wlog(format!(
            "SKIN on: display slot {slot:#x} now calls this add-on, then {} ({prev:#x}): drakes by element, Baron Nashor",
            if game_places::hook::chained_to_game(prev) { "the game's own handler" } else { "another mod's handler (chained)" }
        )),
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
        assert_eq!(kind_of("ingame/league_baron"), Some(Kind::Baron));
        assert_eq!(kind_of("ingame/serpentine"), None);
        assert_eq!(kind_of("league_jinx"), None);
        assert_eq!(kind_of("ingame/epic_buff_animation"), None);
    }

    #[test]
    fn renaming_keeps_the_prefix_and_is_idempotent() {
        assert_eq!(renamed("serpen", "league_drake_infernal").as_deref(), Some("league_drake_infernal"));
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
    fn every_sheet_the_skin_names_ships_with_the_add_on_and_is_remapped() {
        let ov = include_str!("../mod.override_info");
        let mut names: Vec<String> =
            [Element::Infernal, Element::Mountain, Element::Ocean, Element::Cloud, Element::Hextech, Element::Chemtech,
             Element::Elder].iter().map(|e| format!("{DRAKE_PREFIX}{}", e.key())).collect();
        names.push(BARON.to_string());
        // the add-on's own folder, also when league_addons compiles this file as one of its modules
        let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("..").join("league_dragons").join("effects");
        for n in names {
            for kind in ["sheet", "anim"] {
                let key = format!("\"asset/base/aseprite_resources/ingame/{n}#{kind}\"");
                assert!(ov.contains(&key), "{key} not remapped");
                assert!(ov.contains(&format!("\"asset/league_dragons/effects/{n}#{kind}\"")), "{n}#{kind} remapped elsewhere");
            }
            assert!(dir.join(format!("{n}#sheet.png")).is_file(), "{n}#sheet.png missing");
            assert!(dir.join(format!("{n}#anim.fanim")).is_file(), "{n}#anim.fanim missing");
        }
    }
}
