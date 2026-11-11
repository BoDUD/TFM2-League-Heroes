//! 主包 `league` 自己的 DLL（league.dll）：用户 2026-10-12「PPU 可以先改一版亚索试试」「这个要装进主包里 不是附加包」。
//!
//! 主包的英雄还是数据（只有两处借这个 DLL：下面的 `league:range` 和 `league:low_hp`）；这个 DLL 主要做数据做不到的画面：**高清帧（PPU）**——登记在 src/hd.rs 的英雄（先是亚索，PPU 3：
//! 身体 1 倍图整 3 倍，Codex 画的头每格 2×2）在战场、卡牌、图鉴、头像上都画自己图里 PPU 倍密的 `hd_` 帧，大小不变、
//! 像素更细；界面（BP 格子、图鉴 / 头像、选人位、选中特写、记分板头像）画每个英雄自己的小图集（0.7.140）。
//!
//! 画法——游戏按名字取动画表和贴图的两个函数上的钩子、战场的绘制缩放、界面小图集、认游戏版本（现在认得 0.7.0，认不得的
//! 由 game_places 在运行时找）——0.9.0 起在 addons/hd_engine，和 tft 包的 tft.dll 共用（tft 包要单独上创意工坊，只订阅它
//! 也要有高清帧）。init 把 src/hd.rs 的表交给引擎：进程里第一个加载的包 DLL 挂钩、画两个包的英雄；league.dll 加载在
//! tft.dll 之后时自己一个钩子都不挂，把表交给它（hd_engine src/share.rs）——两个包都开着时 Mods 菜单里谁先谁后都一样。
//! 认不得的游戏版本、Mac / Linux（没有 DLL）什么都不改，英雄照旧画 1 倍的帧。
//!
//! src/cache.rs（0.8.16）：游戏的 GPU 图片缓存（Skia 的 GrResourceCache，默认 256 MiB）放大到 1 GiB——一屏英雄多的界面
//! 不再因为装不下而每帧清掉、重新上传贴图；0.9.14 起 1.5 GiB（物理内存不到 8 GiB 的机器仍 1 GiB），用到 90%、到顶清图时
//! 写日志。
//!
//! src/range.rs（0.9.15）：原生效果 `league:range`。英雄的攻击距离 buff 不再带 `range`（游戏的 AI 按它站位、却不按它出手，
//! 英雄停在够不着的地方），改成官方的 `range_adjust`：这个效果的 range_adjust 是施放者身上标记 buff 的射程之和
//! （表在 src/range_table.rs，由 tools/kit/range_buffs.py 生成），数据把它放在普攻最外层的 Combine 里。引擎每一处射程判断都读它，
//! AI 的也是。没有这个 DLL 时（Mac / Linux）这个效果找不到，经典 SDK 的引擎对此只记一条警告，英雄只是没有那份射程。
//!
//! 0.9.16：hd_engine 给列进 DRAWN_EFFECTS 的特效图记绘制日志（league.log 里 `PIC` 开头的行），查永恩 E 留在原地的身体
//! 看不见（hd_engine src/view.rs）。
//!
//! src/low_hp.rs（0.9.17）：原生效果 `league:low_hp`。数据读不到当前生命值，施放者生命低于 35% 时它给他挂 3 tick 的
//! `league_low_hp`，数据用 `SwitchByBuff` 分支（瑞兹的 R：残血只逃不追）。没有这个 DLL 时标记不出现，数据照旧。
//!
//! src/warm.rs（0.7.27）：标题画面出来以后，后台线程把主包 `sound/bgm/` 里的音频按盘上的顺序读一遍进系统缓存，
//! 比赛里音频第一次播放就不用在主线程等读盘。
//!
//! src/diverge.rs（0.9.12；0.9.14 重写）：比赛钩子每 600 tick 给每份模拟（屏幕上的比赛、服务器的两份预演、启动时成对跑的
//! 原版模拟）拍一张快照——每个玩家的金币、等级、复活、冷却、装备、属性，每个活着的单位的位置、血量、buff 名——算哈希；只有
//! 同一小局的几份（第一个 tick 的 rng 相同）互相比，走到同一个 tick 就对一对：不一样写 `DIVERGE`，说出第一处不同的行（任何
//! 种类）和字段，之后接着比（`EQUAL` 又一样了）——找「屏幕上的比赛和预演从哪里起不同」。只写有配对的 run。
//!
//! 0.9.21（2026-11-08 的日志）：src/diverge.rs 的名字表跟着留着的行走（以前只增不减，开局 15 分钟就满了，之后 DIVERGE 说不出
//! 哪里不同、汇总里英雄读成「?」）；每 60 tick 给每个玩家一个细哈希，DIVERGE 写第一处不同在哪 60 tick 之间、哪些玩家
//! （`first differs between t A and t B, player N …`）；没列出的塔 / 水晶的不同行总是接在后面（`| structures: …`）；END 在
//! 比分差旁边写两队玩家的击杀数（`(kills 17:4)`，和 log.log 的 live_score 比；比分差是 server_score 那种，处决也算）。
//! hd_engine src/view.rs：妮蔻假扮（和高清的佛耶戈附身高清英雄）时身体的绘制缩放不再除两次（`league_neeko 0.400 -> 0.160`）。
//! 0.9.20（科加斯 BP 格，没装过）一起带上。
//!
//! 0.9.25（用户 2026-11-09：「大小龙模型呢？codex做吗 还有攻击动画」「龙魂的也都交付了 你处理完」）：src/hd.rs 登记 league_dragons
//! 的 8 张怪物图（六种元素亚龙、远古巨龙 1.8，纳什男爵 1.5；男爵也进 DRAWN_EFFECTS，他咬中的特效在点上画）。附加包的显示钩子
//! 把小龙 / 莫尔加德的资源名换成这些图，身体按名字找到后按 1 / PPU 画。0.9.24 是特效 PPU（#730）的。
//!
//! src/stacks.rs（0.9.29，用户 2026-11-11：「现在叠层数的技能英雄在游戏里看不到多少层」「不能放技能栏里面吗 和联盟一样」）：
//! 比赛钩子每 6 tick 数一次 src/stack_table.rs 里英雄身上的层数（同名 buff 有几个、数值加起来，或梯子爬到第几级），写进他的
//! 属性 `stack`：游戏自己的英雄信息面板在技能图标旁边显示它（数据里的 `stack_skill_index` 选图标，tools/kit/stack_nums.py
//! 生成表和这个字段）。基础属性按宿主自己的机器码读出布局、原样读出来只换 `stack` 再写回，布局对不上就不写。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league.log`，每次启动游戏重写（上一次的留作 league.prev.log）。
//! 挂钩、取表、缩放的行写在挂钩的那个 DLL 的日志里：tft.dll 先加载时在 tft.log，这里只有一行「交给了谁」。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

#[cfg(windows)]
use hd_engine::Role;
use mod_api_stable::*;

#[cfg(windows)]
mod cache;
pub mod diverge;
pub mod hd;
pub mod low_hp;
pub mod range;
mod range_table;
pub mod stacks;
mod stack_table;
#[cfg(windows)]
mod warm;

pub const ID: &str = "league";
const VERSION: &str = "0.9.30";

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

/// `cargo test` lines (league_test ...) went into the game's own league.log and made an old game's log look recent
/// (2026-10-13): the tests log into the temp folder instead, the DLL keeps its path.
#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("league_main_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league.log");
        }
    }
    PathBuf::from("league.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);
static T0: LazyLock<std::time::Instant> = LazyLock::new(std::time::Instant::now);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (15 000 lines a session,
    // about 9 s of stalls on the simulation thread, 2026-10-12, the user: 「LOL mod让游戏掉帧很严重 加载很卡」)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("[{:8.2}] {}\n", T0.elapsed().as_secs_f64(), msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

fn init(host: &StableHost) -> StableMod {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!("=== {ID}.dll {VERSION} (dense frames) loaded: game {}.{}.{} abi {} log={} ===",
        v.major, v.minor, v.patch, host.abi_level(), LOG_PATH.display()));
    // the GPU image cache first, whatever the build: it only needs Skia's GrResourceCache (src/cache.rs)
    #[cfg(windows)]
    cache::install_once(hd_engine::module_base());
    // the dense frames: this pack's table to the engine - it hooks the game from here (build, display pair, lookups,
    // scale, as before 0.9.0), or hands the table to the pack DLL that did (tft.dll loaded first: hd_engine src/share.rs)
    #[cfg(windows)]
    match hd_engine::start(&hd::table(), &format!("{ID}.dll {VERSION}"), |m: &str| wlog(m)) {
        Role::Host => host.log(LogLevel::Info, "League Heroes: dense (PPU) frames for the heroes that have them."),
        Role::Guest { host: by, .. } => host.log(LogLevel::Info,
            &format!("League Heroes: dense (PPU) frames for the heroes that have them, drawn by {by}.")),
        Role::Off(why) => host.log(LogLevel::Info, &format!("League Heroes: 1x frames - {why}.")),
    }
    let mut module = StableMod::new(ID);
    #[cfg(windows)]
    module.set_extension(warm::Warm);
    // `league:range`: the attack range of the pack's marker buffs, read by every range check (src/range.rs)
    module.add_native_effect(range::NODE, range::Range);
    // `league:low_hp`: a flag for the data when the caster's health is low - the data reads no health (src/low_hp.rs)
    module.add_native_effect(low_hp::NODE, low_hp::LowHp);
    // the only match hook this module may set: the stack counts for the champion panel (src/stacks.rs), then the
    // per-600-tick simulation checksum (src/diverge.rs)
    module.set_match_hook(Match);
    module
}

/// The module's one match hook (`StableMod::set_match_hook` keeps only the last): the stack counts first, so the
/// checksum's snapshot sees this tick's `stack` in every run alike.
struct Match;

impl StableMatchHook for Match {
    fn on_match_tick(&self, sim: &mut StableSim<'_>, rng_seed: u64) {
        stacks::on_tick(sim);
        diverge::Diverge.on_match_tick(sim, rng_seed);
    }
}

declare_stable_mod!(init);
