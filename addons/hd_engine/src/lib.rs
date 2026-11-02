//! 高清帧（PPU）引擎：主包的 league.dll（league_main）和 tft 包的 tft.dll（tft）共用（2026-10-31 从 league.dll 拆出来：
//! tft 包要单独上创意工坊，只订阅 tft 包也要有高清帧）。两个 DLL 各带自己的表（league_main/src/hd.rs、tft/src/hd.rs，
//! [`Table`]），在 init 里调 [`start`]：进程里第一个调的挂钩（主），后来的把表交给它、自己不挂（客，src/share.rs）——
//! 两个包都开着时 Mods 菜单里谁先加载都一样，两边的英雄都画高清帧。
//!
//! 登记的英雄（最早是亚索，用户 2026-10-12「PPU 可以先改一版亚索试试」）在战场、卡牌、图鉴、头像上都画自己图里 PPU 倍密的
//! `hd_` 帧，大小不变、像素更细。src/lookup.rs：游戏按名字取动画表和贴图的两个函数上挂钩——动画表就地改成每个动作都是
//! 高清帧（矩形 ÷ PPU），贴图的宽高报 ÷ PPU，界面按帧大小画、UV 落在高清那块；战场按「UV × 图的真实像素」画，所以战场拿到
//! 真实的高清帧和真实宽高，src/view.rs 把实体的绘制缩放写成 ÷ PPU。只在 src/build.rs 认得的游戏版本上挂钩（每处要改要调的
//! 代码逐字节核对指纹，现在认得 0.7.0；认不得的版本由 game_places 在运行时找）；找不到的版本、Mac / Linux（没有 DLL）什么
//! 都不改，英雄照旧画 1 倍的帧。
//!
//! src/ui.rs（league.dll 0.7.140 起）：BP 格子、图鉴 / 头像、选人位、选中特写、记分板头像改画每个英雄自己的小图集（打包时
//! 生成，只有界面画的帧）——一屏画全部英雄的界面不再把整张战斗图集塞进游戏 256 MiB 的图片缓存（「BP界面非常的卡」）。
//!
//! 日志：引擎写进调它的 DLL 给的回调（league.dll 的 league.log、tft.dll 的 tft.log）；挂钩、取表、缩放的行都在主的日志里，
//! 客只写一行交给了谁、交了几个英雄。

pub mod build;
pub mod hd;
pub mod share;
#[cfg(windows)]
mod lookup;
#[cfg(windows)]
mod ui;
#[cfg(windows)]
mod view;

use std::sync::OnceLock;

pub use hd::Table;
pub use share::{Role, HOST_ENV, PROTOCOL};
#[cfg(windows)]
pub use lookup::{plausible, read};

static LOG: OnceLock<fn(&str)> = OnceLock::new();

/// A line in the calling DLL's log (league.log, tft.log): the callback [`start`] was given, nothing before it.
pub(crate) fn wlog(msg: impl AsRef<str>) {
    if let Some(log) = LOG.get() {
        log(msg.as_ref());
    }
}

/// The dense frames for `table`'s heroes, from the DLL `who` (its name in the others' logs: `league.dll 0.9.0`), its
/// lines through `log`. Called once from each pack DLL's init: the first in the process hooks the game and draws every
/// pack's heroes ([`Role::Host`]); a later one hands its table to that one and hooks nothing ([`Role::Guest`]).
pub fn start(table: &Table<'_>, who: &str, log: fn(&str)) -> Role {
    let _ = LOG.set(log);
    share::start_with(&share::ProcessEnv, &hd::REGISTRY, &share::process_tag(), table, who, share::door, install)
}

/// The game EXE's base in this process.
#[cfg(windows)]
pub fn module_base() -> usize {
    view::module_base()
}

/// The host's hooks, as league.dll put them in before the engine was shared: the build by its fingerprints (or found at
/// run time by game_places), the display pair published for the add-ons before the slot is swapped, the resource
/// lookups (and the UI sheets' sinks), then the battlefield's scale, body draw and effect draw. Err: no hooks at all - an
/// unknown build, or lookups another DLL hooked already (the scale is not touched then: it would shrink 1x frames).
#[cfg(windows)]
fn install() -> Result<(), String> {
    let found = build::detect(view::read_rva).or_else(|why| {
        // not a listed build: look for the same places by their patterns (game_places, made from the listed build)
        let t0 = std::time::Instant::now();
        let module = module_base();
        // the display pair through game_places::display (shared with the add-ons, read before anyone swaps the slot)
        let found = game_places::display().and_then(|(f, slot)| {
            let img = unsafe { game_places::Image::from_module(module) }?;
            game_places::resolve_with(&img, Some((f - module, slot - module)))
        });
        match found {
            Ok(p) => {
                for n in &p.notes {
                    wlog(n);
                }
                let name = format!("found at run time in {:.0} ms ({why}; patterns from {})",
                                   t0.elapsed().as_secs_f64() * 1000.0, game_places::sigs::FROM);
                Ok(build::from_places(p, name))
            }
            Err(e) => Err(format!("{why}; the run-time search: {e}")),
        }
    });
    let b = match found {
        Ok(b) => b,
        Err(why) => {
            wlog(format!("game build unknown ({why}): no hooks - every hero draws its 1x frames"));
            return Err(format!("this game build is not known ({why})"));
        }
    };
    wlog(format!("game build: {}", b.name));
    // publish the display pair for the add-ons' hooks before the slot is swapped (game_places::ENV)
    match game_places::display() {
        Ok((f, slot)) => wlog(format!("display handler {f:#x}, slot {slot:#x} ({}={:?})", game_places::ENV,
                                      std::env::var(game_places::ENV).unwrap_or_default())),
        Err(e) => wlog(format!("display handler not found by game_places ({e})")),
    }
    if !lookup::install_once(b) {
        return Err("the resource lookups could not be hooked (not the game's own code there any more)".into());
    }
    view::install_once(b);
    Ok(())
}

#[cfg(not(windows))]
fn install() -> Result<(), String> {
    Err("not Windows: no hooks".into())
}
