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

// ---- 下面几个小工具给第三、四批的千蛾、沉锚、返照、缓刑、赊命、无痕、陨夜、丧钟共用 ----

/// 技能数据 `passive.params` 里的一个整数（生成脚本把参数表 PARAMS 的数写进去，引擎按键名排好序传进来，
/// 形如 `{"r_t":210,"r_p":30}`）。没有这个键就是 None，调用处用自己的默认值。
pub(crate) fn kit_param(json: &str, key: &str) -> Option<usize> {
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    body.split(',').find_map(|pair| {
        let (k, v) = pair.split_once(':')?;
        (k.trim().trim_matches('"') == key).then(|| v.trim().parse().ok()).flatten()
    })
}

/// 地图上能站的范围：场上所有单位（塔、水晶、泉水都在里面）围出来的框，再夹在地图边线以内
/// （30 格 × 32000 = 960000，四边各留一个身位，和 league_urgot 一样）。墙在里面看不到。
pub(crate) fn map_box(sim: &StableSim<'_>) -> ((u64, u64), (u64, u64)) {
    const LO: u64 = 12_000;
    const HI: u64 = 948_000;
    let mut b: Option<((u64, u64), (u64, u64))> = None;
    for i in 0..sim.entity_count() {
        let Some(e) = sim.entity_at(i) else { continue };
        let p = e.pos();
        b = Some(match b {
            None => (p, p),
            Some((lo, hi)) => ((lo.0.min(p.0), lo.1.min(p.1)), (hi.0.max(p.0), hi.1.max(p.1))),
        });
    }
    let ((lx, ly), (hx, hy)) = b.unwrap_or(((LO, LO), (HI, HI)));
    let (lx, ly) = (lx.clamp(LO, HI), ly.clamp(LO, HI));
    ((lx, ly), (hx.clamp(LO, HI).max(lx), hy.clamp(LO, HI).max(ly)))
}

/// 把一个算出来的落点（可能出了地图）夹回 [`map_box`] 里。
pub(crate) fn onto_map(bx: ((u64, u64), (u64, u64)), x: f64, y: f64) -> (u64, u64) {
    let ((lx, ly), (hx, hy)) = bx;
    let fx = if x.is_finite() { x } else { lx as f64 };
    let fy = if y.is_finite() { y } else { ly as f64 };
    (fx.round().clamp(lx as f64, hx as f64) as u64, fy.round().clamp(ly as f64, hy as f64) as u64)
}

/// 放一个动作（和数据里的 CasterAnimation 一样：带名字的 Animation 控制，放完之前不能干别的）。
pub(crate) fn animate(sim: &mut StableSim<'_>, id: usize, tag: &str, ticks: usize) {
    let mut cc = CcV1::of_kind(CcKindV1::Animation, ticks.max(1) as u64);
    cc.set_name(tag);
    sim.apply_cc(id, &cc);
}

/// 这会儿能不能出招：被控（眩晕、击飞、恐惧、魅惑、嘲讽、沉默、被强制位移）或者正在放别的动作，就不能。
pub(crate) fn can_cast(sim: &StableSim<'_>, id: usize) -> bool {
    const NO: [CcKindV1; 8] = [
        CcKindV1::Airborne, CcKindV1::Stun, CcKindV1::Taunt, CcKindV1::Fear,
        CcKindV1::Charm, CcKindV1::BlockSkill, CcKindV1::ForceMove, CcKindV1::Animation,
    ];
    sim.get_entity(id).is_some_and(|e| {
        e.is_alive() && (0..e.cc_count()).filter_map(|i| e.cc_at(i)).all(|c| NO.iter().all(|k| k.code() != c.kind))
    })
}

/// 待命没用上：把这个技能格子剩下的冷却退到只剩 `keep` tick，AI 过一会儿会再按一次待命。
pub(crate) fn refund_cooldown(sim: &mut StableSim<'_>, id: usize, slot: SkillSlotV1, keep: usize) {
    let left = sim.get_entity(id).and_then(|e| e.cooldown(slot)).map_or(0, |c| c.remaining);
    if left > keep {
        sim.entity_reduce_cooldown(id, slot, left - keep);
    }
}

/// 挨打前（`on_damaged` 在这一下扣血之前调）先把 `back` 点血加回去，扣完正好少挨这么多：
/// 返回 (现在把生命设成多少, 这一下扣完以后还要再加回的)。生命最多设到上限，超出的那截等扣完再加
/// （league_braum 0.1.3 的 refund）。这一下本来会把人打死、加回之后本该活着：要先挂一下不死，
/// 扣完剩 1 血，再补上差的，所以 `lethal` 为真时第二个数已经减掉了那 1 血。
pub(crate) fn refund_hit(now: usize, max: usize, back: usize, damage: usize) -> (usize, usize, bool) {
    let want = now.saturating_add(back);
    let set = want.min(max);
    let over = want - set;
    if set <= damage && want > damage {
        (set, want - damage - 1, true)
    } else {
        (set, over, false)
    }
}

/// 测试用：从生成好的 `.data_champion` 里抠出 `passive.params` 那一段（去掉空白），就是引擎传给 configure 的样子。
#[cfg(test)]
pub(crate) fn kit_params_of(kit: &str) -> String {
    let at = kit.find("\"params\"").expect("passive.params");
    let rest = &kit[at..];
    let (a, b) = (rest.find('{').expect("{"), rest.find('}').expect("}"));
    rest[a..=b].chars().filter(|c| !c.is_whitespace()).collect()
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
