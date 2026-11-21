//! The tft pack's own code (tft.dll, next to tft/mod.mod_info): what a tft hero's data cannot do, one module a hero,
//! all in the one tft mod (the user, 2026-10-26: 「诺拉和爆爆合并在一个mod啊」「tft的英雄都放一个mod里 参考英雄联盟」).
//! A new hero: its module here, its `register` called from `init`.
//!
//! The heroes' dense (PPU) frames too (0.42.0, the pack going on the Workshop on its own): src/hd.rs is the pack's table,
//! drawn by hd_engine - the same engine league.dll's are. `init` hands it the table first: the first pack DLL loaded in
//! the game hooks it (tft.dll alone, or before league in the Mods menu), a later one hands its table to that one and
//! hooks nothing (hd_engine src/share.rs). Before 0.42.0 league.dll drew these heroes' dense frames, only with both packs
//! enabled. The engine's lines: `%APPDATA%\TeamSamoyed\TeamfightManager2\data\tft.log`, new each start (the last one
//! kept as tft.prev.log); each hero module keeps its own log.
//!
//! The effects too (0.55.0, 2026-11-09: 「补画你要成压缩包给我啊 另外云顶英雄的也要调啊」): every hero's effect sheet carries
//! `hd_` twins (tools/art/densify_fx.py: redrawn from Codex's raws where those are faithful, else Scale2x'd), listed in
//! src/fx_ppu.rs (tools/art/fx_ppu_table.py --pack tft). hd_engine draws them dense only where it shrinks every effect,
//! buff and projectile picture (`full_effects`), and hands them to a league.dll host only through its full door.
//!
//! 技能栏层数格（2026-11-22，用户：「还有很多叠层的技能在技能列表里看不到层数」）：比赛里左下角英雄信息面板的层数格，
//! 和 league.dll 同一份代码（`stacks`：league_main 的 src/stacks.rs 用 `#[path]` 引进来），表是本包自己的
//! src/stack_table.rs（tools/kit/stack_nums.py 生成，云顶的英雄）。比赛钩子 [`Stacks`] 只调 `stacks::on_tick`：每 6 tick
//! 看一次场上的英雄，名字不是 `tft_` 开头的直接跳过。league.dll 写它表里的，这里写这里的，谁先加载都一样。

pub mod alune;
pub mod aoshin;
pub mod baronnashor;
pub mod brambleback;
pub mod brock;
pub mod cinderling;
pub mod daeja;
pub mod elderdragon;
pub mod fx_ppu;
pub mod gromp;
pub mod hd;
pub mod sentry;
pub mod idas;
pub mod kobuko;
pub mod krug;
pub mod loris;
pub mod maddie;
pub mod meepsie;
pub mod mightymech;
pub mod murkwolf;
pub mod nomsy;
pub mod norra;
pub mod raptor;
pub mod renni;
pub mod riftherald;
pub mod scar;
pub mod scuttlecrab;
pub mod sentinel;
pub mod sevika;
pub mod shiohyu;
pub mod silco;
pub mod sim_tag;
pub mod smeech;
pub mod sohm;
#[path = "../../league_main/src/stacks.rs"]
pub mod stacks;
mod stack_table;
pub mod steb;
pub mod syfen;
pub mod terra;
pub mod thex;
pub mod vander;
pub mod violet;
pub mod zippy;

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

#[cfg(windows)]
use hd_engine::Role;
use mod_api_stable::*;

const VERSION: &str = env!("CARGO_PKG_VERSION");

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

/// The tests log into the temp folder (league_main's way: their lines must not make the game's tft.log look recent).
#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("tft_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("TFT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("tft.log");
        }
    }
    PathBuf::from("tft.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);
static T0: LazyLock<std::time::Instant> = LazyLock::new(std::time::Instant::now);

/// A line in tft.log (the engine's; the file stays open, as league.log does).
fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("[{:8.2}] {}\n", T0.elapsed().as_secs_f64(), msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first).
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

fn init(host: &StableHost) -> StableMod {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!("=== tft.dll {VERSION} (the tft heroes' rules and dense frames) loaded: game {}.{}.{} abi {} log={} ===",
        v.major, v.minor, v.patch, host.abi_level(), LOG_PATH.display()));
    // 显示钩子晚挂（2026-11-21）：当主时战场缩放第一帧（Frame）再换槽
    #[cfg(windows)]
    hd_engine::defer_display();
    // the dense frames first: this pack's table to the engine, which hooks the game from here or hands the table to the
    // pack DLL that did (league.dll loaded first)
    #[cfg(windows)]
    match hd_engine::start(&hd::table(), &format!("tft.dll {VERSION}"), |m: &str| wlog(m)) {
        Role::Host => host.log(LogLevel::Info, "tft.dll: dense (PPU) frames for the tft heroes."),
        Role::Guest { host: by, .. } => {
            host.log(LogLevel::Info, &format!("tft.dll: dense (PPU) frames for the tft heroes, drawn by {by}."))
        }
        Role::Off(why) => host.log(LogLevel::Info, &format!("tft.dll: the tft heroes' 1x frames - {why}.")),
    }
    let mut module = StableMod::new("tft");
    alune::register(host, &mut module);
    aoshin::register(host, &mut module);
    brambleback::register(host, &mut module);
    brock::register(host, &mut module);
    cinderling::register(host, &mut module);
    daeja::register(host, &mut module);
    elderdragon::register(host, &mut module);
    gromp::register(host, &mut module);
    sentry::register(host, &mut module);
    idas::register(host, &mut module);
    kobuko::register(host, &mut module);
    krug::register(host, &mut module);
    loris::register(host, &mut module);
    maddie::register(host, &mut module);
    meepsie::register(host, &mut module);
    mightymech::register(host, &mut module);
    murkwolf::register(host, &mut module);
    nomsy::register(host, &mut module);
    norra::register(host, &mut module);
    raptor::register(host, &mut module);
    renni::register(host, &mut module);
    riftherald::register(host, &mut module);
    scar::register(host, &mut module);
    scuttlecrab::register(host, &mut module);
    sentinel::register(host, &mut module);
    sevika::register(host, &mut module);
    shiohyu::register(host, &mut module);
    silco::register(host, &mut module);
    smeech::register(host, &mut module);
    sohm::register(host, &mut module);
    steb::register(host, &mut module);
    syfen::register(host, &mut module);
    terra::register(host, &mut module);
    thex::register(host, &mut module);
    baronnashor::register(host, &mut module);
    vander::register(host, &mut module);
    violet::register(host, &mut module);
    zippy::register(host, &mut module);
    #[cfg(windows)]
    module.set_extension(Frame);
    module.set_match_hook(Stacks);
    module
}

/// 本包唯一的比赛钩子（`set_match_hook` 只留最后一个）：技能栏层数格（`stacks::on_tick`，每 6 tick 一次，只看英雄）。
struct Stacks;

impl StableMatchHook for Stacks {
    fn on_match_tick(&self, sim: &mut StableSim<'_>, _rng_seed: u64) {
        stacks::on_tick(sim);
    }
}

/// 云顶这张表和英雄模块对得上：表里数的 buff 就是各模块挂的那个，数出来是模块叠的层数。
#[cfg(test)]
mod stack_rows {
    use crate::stacks::{count, rows, value, Rule, Stat, STACKS};
    use mod_api_stable::BuffV1;

    fn rule(hero: &str) -> Rule {
        let mut r = rows(hero);
        let st = r.next().unwrap_or_else(|| panic!("{hero} is not in the table"));
        assert!(r.next().is_none(), "{hero}: one row");
        st.rule
    }

    #[test]
    fn the_native_stacks_count_as_the_modules_lay_them() {
        assert!(STACKS.iter().all(|s| s.hero.starts_with("tft_")));
        // 魔沼蛙、索姆：引擎的叠层 buff，一层一个
        let purple = crate::gromp::purple_buff(&crate::gromp::Params::default());
        assert_eq!(count(rule("tft_gromp"), &[purple, purple, purple]), 3);
        let mut tide = BuffV1::named("tft_sohm_p_tide");
        tide.magic_power_mult = 9;
        assert_eq!(count(rule("tft_sohm"), &[tide, tide]), 2);
        // 深红锋喙鸟：碎甲在敌人身上
        let shred = crate::raptor::shred_buff(&crate::raptor::Params::default());
        let st = rows("tft_raptor").next().unwrap();
        assert!(st.foes);
        let (one, three) = (vec![shred], vec![shred, shred, shred]);
        assert_eq!(value(st, &[shred; 4], &[0; 3], &[&one, &three]), 3, "the enemy with the most, not her own");
        // 赛芬、呲呲、麦迪：一个 buff，数值是层数 x 一层的量（表里的 per 跟着数据的参数）
        let sp = crate::syfen::Params::default();
        assert_eq!(rule("tft_syfen"), Rule::Per("tft_syfen_p_rage", Stat::Attack, sp.p_ad));
        assert_eq!(count(rule("tft_syfen"), &[crate::syfen::fury_buff(4, &sp)]), 4);
        let zp = crate::zippy::Params::default();
        assert_eq!(rule("tft_zippy"), Rule::Per("tft_zippy_p_guild", Stat::Defence, zp.p_def));
        assert_eq!(count(rule("tft_zippy"), &[crate::zippy::guild_buff(3, &zp)]), 3);
        let mp = crate::maddie::Params::default();
        let mut bounty = BuffV1::named("tft_maddie_p_bounty");
        bounty.attack_speed_mult = mp.w_as * 2;
        assert_eq!(rule("tft_maddie"), Rule::Per("tft_maddie_p_bounty", Stat::AttackSpeedMult, mp.w_as as usize));
        assert_eq!(count(rule("tft_maddie"), &[bounty]), 2);
        // 峡谷先锋：受到的伤害减少几成
        assert_eq!(count(rule("tft_riftherald"), &[crate::riftherald::shell_buff(12)]), 12);
    }

    #[test]
    fn the_data_ladders_are_listed() {
        // 拉露恩的月相、绯红树怪的绯红霸符、希尔科的主宰：数据自己的梯子
        let ph = BuffV1::named("tft_alune_ph2");
        assert_eq!(count(rule("tft_alune"), &[ph]), 2);
        assert_eq!(count(rule("tft_cinderling"), &[BuffV1::named("tft_cinderling_p_full")]), 4);
        assert_eq!(count(rule("tft_silco"), &[BuffV1::named("tft_silco_d1"), BuffV1::named("tft_silco_d5")]), 5);
    }
}

/// 每帧：高清帧引擎当主时的显示钩子第一帧挂上、被跳过就接回来（hd_engine::frame）。本包原来没有客户端扩展。
#[cfg(windows)]
struct Frame;

#[cfg(windows)]
impl StableExtension for Frame {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        hd_engine::frame(ctx.is_in_game(), |p| ctx.ui_visible(p), |p| ctx.ui_text(p));
    }
}

declare_stable_mod!(init, requires = 9);
