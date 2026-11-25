//! Abyss Pact (渊契) native DLL (`abysspact.dll`):
//! signature mechanics for all 20 dark-fantasy original champions plus shared HD PPU registration.

pub mod anchor;
pub mod bloodmoon;
pub mod bonebow;
pub mod carapace;
pub mod corvus;
pub mod debtor;
pub mod effigy;
pub mod faceless;
pub mod faceless_view;
pub mod hd;
pub mod hourglass;
pub mod knell;
pub mod leech;
pub mod noctua;
pub mod oathbreaker;
pub mod reprieve;
pub mod sevenfold;
pub mod starfall;
pub mod traceless;
pub mod undertaker;
pub mod vesper;
pub mod view_forms;
pub mod voice;
pub mod whisperer;

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

#[cfg(test)]
fn log_path() -> PathBuf {
    std::env::temp_dir().join("abysspact_test.log")
}

#[cfg(not(test))]
fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("ABYSSPACT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("abysspact.log");
        }
    }
    PathBuf::from("abysspact.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);
static T0: LazyLock<std::time::Instant> = LazyLock::new(std::time::Instant::now);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("[{:8.2}] {}\n", T0.elapsed().as_secs_f64(), msg.as_ref()).as_bytes());
    }
}

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// Squared Euclidean distance between two `(u64, u64)` world positions.
pub(crate) fn dist_sq(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0.abs_diff(b.0);
    let dy = a.1.abs_diff(b.1);
    dx.saturating_mul(dx).saturating_add(dy.saturating_mul(dy))
}

pub(crate) fn has_buff(sim: &StableSim<'_>, id: usize, want: &str) -> bool {
    let Some(e) = sim.get_entity(id) else { return false };
    let n = e.buff_count();
    (0..n).any(|i| e.buff_at(i).is_some_and(|b| b.name() == want))
}

pub(crate) fn consume_buff(sim: &mut StableSim<'_>, id: usize, want: &str) -> bool {
    sim.entity_remove_buff(id, want) > 0
}

/// 活着的敌方英雄：(单位号, 位置)。只走英雄表（十个人），不走全部单位——每 tick 走一遍全部单位（小兵、野怪上百个，
/// 每个都把 buff 一个个拷出来）在预模拟里很费。
pub(crate) fn foe_champions(sim: &StableSim<'_>, team: usize) -> Vec<(usize, (u64, u64))> {
    (0..sim.champion_count())
        .map(|i| sim.champion_id_at(i))
        .filter_map(|id| sim.get_entity(id).filter(|e| e.is_alive() && e.team() != team).map(|e| (id, e.pos())))
        .collect()
}

/// 一次走完单位的 buff 表，看 `names` 里每个在不在（按 `names` 的顺序）。
pub(crate) fn buffs_present<const N: usize>(sim: &StableSim<'_>, id: usize, names: [&str; N]) -> [bool; N] {
    let mut out = [false; N];
    let Some(e) = sim.get_entity(id) else { return out };
    for i in 0..e.buff_count() {
        let Some(b) = e.buff_at(i) else { continue };
        let name = b.name();
        for (k, want) in names.iter().enumerate() {
            if name == *want {
                out[k] = true;
            }
        }
    }
    out
}

/// 看冷却认出刚放的技能：某个槽的剩余冷却比上一 tick 一下子高出 `CAST_JUMP` 以上，就是刚放了（终末包巨灵们的做法）。
#[derive(Clone, Default)]
pub(crate) struct CastWatch {
    last: [usize; 4],
}

pub(crate) const CAST_JUMP: usize = 30;

impl CastWatch {
    /// 这一 tick 的剩余冷却（普攻、技能一、技能二、大招）→ 哪几个槽刚放了。
    pub fn step(&mut self, now: [usize; 4]) -> [bool; 4] {
        let mut cast = [false; 4];
        for k in 0..4 {
            cast[k] = now[k] > self.last[k].saturating_add(CAST_JUMP);
        }
        self.last = now;
        cast
    }

    /// 读这名玩家这一 tick 的冷却再 [`CastWatch::step`]；读不到算谁都没放。
    pub fn watch(&mut self, sim: &StableSim<'_>, player: usize) -> [bool; 4] {
        match sim.get_player(player).and_then(|p| p.cooldowns()) {
            Some((a, q, w, r)) => self.step([a, q, w, r]),
            None => [false; 4],
        }
    }
}

fn init(host: &StableHost) -> StableMod {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== abysspact.dll {VERSION} (Abyss Pact heroes & HD frames) loaded: game {}.{}.{} abi {} ===",
        v.major, v.minor, v.patch, host.abi_level()
    ));

    #[cfg(windows)]
    hd_engine::defer_display();

    #[cfg(windows)]
    match hd_engine::start(&hd::table(), &format!("abysspact.dll {VERSION}"), |m: &str| wlog(m)) {
        Role::Host => host.log(LogLevel::Info, "abysspact.dll: dense (PPU) frames for Abyss Pact heroes."),
        Role::Guest { host: by, .. } => host.log(
            LogLevel::Info,
            &format!("abysspact.dll: dense (PPU) frames for Abyss Pact heroes, drawn by {by}."),
        ),
        Role::Off(why) => host.log(LogLevel::Info, &format!("abysspact.dll: 1x frames - {why}.")),
    }

    let mut module = StableMod::new("abysspact");
    // Batch 1
    oathbreaker::register(host, &mut module);
    faceless::register(host, &mut module);
    whisperer::register(host, &mut module);
    bonebow::register(host, &mut module);
    corvus::register(host, &mut module);
    faceless_view::install();
    // Batch 2
    bloodmoon::register(host, &mut module);
    undertaker::register(host, &mut module);
    effigy::register(host, &mut module);
    sevenfold::register(host, &mut module);
    vesper::register(host, &mut module);
    // Batch 3
    carapace::register(host, &mut module);
    leech::register(host, &mut module);
    noctua::register(host, &mut module);
    anchor::register(host, &mut module);
    hourglass::register(host, &mut module);
    // Batch 4
    reprieve::register(host, &mut module);
    debtor::register(host, &mut module);
    traceless::register(host, &mut module);
    starfall::register(host, &mut module);
    knell::register(host, &mut module);
    view_forms::install();

    #[cfg(windows)]
    module.set_extension(Frame);
    module
}

#[cfg(windows)]
struct Frame;

#[cfg(windows)]
impl StableExtension for Frame {
    fn post_update(&self, ctx: &mut StableClient<'_>, _dt: u64) {
        hd_engine::frame(ctx.is_in_game(), |p| ctx.ui_visible(p), |p| ctx.ui_text(p));
        faceless_view::observe_clock(ctx);
    }
}

declare_stable_mod!(init, requires = 9);

/// 一张图（`#anim.fanim`）里某个动画一共几 tick（各帧秒数加起来 × 60，四舍五入）；没有这个动画给 None。
#[cfg(test)]
pub(crate) fn fanim_ticks(json: &str, tag: &str) -> Option<usize> {
    let key = format!("\"{tag}\"");
    let at = json.find(&key)? + key.len();
    let open = at + json[at..].find('[')?;
    let close = open + json[open..].find(']')?;
    let frames = &json[open..close];
    let mut secs = 0.0f64;
    let mut rest = frames;
    while let Some(k) = rest.find("\"duration\"") {
        rest = &rest[k + "\"duration\"".len()..];
        let rest_num = rest.trim_start().trim_start_matches(':').trim_start();
        let num: String = rest_num.chars().take_while(|c| c.is_ascii_digit() || *c == '.').collect();
        secs += num.parse::<f64>().ok()?;
    }
    Some((secs * 60.0).round() as usize)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fanim_ticks_reads_one_tags_frames() {
        let json = r#"{"anims":{"hd_ult":{"frames":[{"duration":0.5,"data":{"x":0.0}}]},"ult":{"frames":[{"duration":0.1,"data":{"x":0.0}},{"duration":0.2,"data":{"x":1.0}}]}}}"#;
        assert_eq!(fanim_ticks(json, "ult"), Some(18));
        assert_eq!(fanim_ticks(json, "hd_ult"), Some(30));
        assert_eq!(fanim_ticks(json, "run"), None);
    }

    #[test]
    fn a_cast_is_a_cooldown_that_jumps_up() {
        let mut w = CastWatch::default();
        assert_eq!(w.step([0, 0, 0, 0]), [false; 4]);
        // 技能一刚放：冷却从 0 跳到 420
        assert_eq!(w.step([0, 420, 0, 0]), [false, true, false, false]);
        // 之后一 tick 一 tick 往下走，不算
        assert_eq!(w.step([0, 419, 0, 0]), [false; 4]);
        // 减冷却也不算
        assert_eq!(w.step([0, 200, 0, 0]), [false; 4]);
        // 大招刚放
        assert_eq!(w.step([0, 199, 0, 4200]), [false, false, false, true]);
    }
}
