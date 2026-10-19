//! 拉莫斯附加包（用户 2026-10-19：技能方案 A，做附加包）。主包保持纯数据；`mod.override_info` 把主包的拉莫斯换成 `override/` 里的
//! 副本（`make_override.py` 用 tools/kit/build_rammus.py 的 `native=1` 生成：被动换成本包的 `league_rammus:shell`，普攻的锥刺甲壳
//! 换成本包的 `league_rammus:spikes`，Q 只缩成球、挂上 `league_rammus_q_ball`，普攻、技能1 的说明开头加【附加包】），本包补数据做不到的
//! 三件事：
//!
//! - **锥刺甲壳按真实护甲**：普攻多造成 `P_DMG` + `P_AP`% 法强 + `P_ARM`% 护甲 的魔法伤害（英雄联盟：10 + 15% 护甲；主包数据读不到
//!   护甲，用最大生命代替）。
//! - **动力冲刺照英雄联盟滚**：副本的 Q 缩成球后挂 `q_ball`（最多 `q_ball_t` tick），本包让他越滚越快（移速 +`Q_MS0`% 到 +`Q_MS1`%，
//!   `Q_RAMP` tick 加满），他照常走向目标，身边 `Q_TOUCH` 内一有敌方单位（不算防御塔）就挂 1 tick 的 `q_go`，数据里每 tick 看一次的
//!   守望把它变成撞击（伤害、击退、减速、他弹出球来）。滚着的时候普攻也算撞上。主包里 Q 是一次冲到目标的冲刺。
//! - **整身换形态**（`view.rs`，只在游戏 0.6.4 上）：滚着的时候站着、走着、挨打都是滚动的刺球（`b_*`），尖刺防御开着的时候是蜷着的防御
//!   姿势（`c_*`）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_rammus.log`，每次启动游戏重写，上一次的留在 .prev.log：`ROLL`（缩成球、
//! 撞上谁 / 滚完没撞上、滚了多久）、`SPIKES`（锥刺甲壳按多少护甲打了多少）、`FORM`（画面里换形态），都限了条数。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

pub mod view;

const ID: &str = "league_rammus";
const VERSION: &str = env!("CARGO_PKG_VERSION");
/// 滚球（副本的 Q 挂的）和尖刺防御（数据的守望挂的）：view.rs 照它们换画面。
pub const BALL: &str = "league_rammus_q_ball";
pub const CURL: &str = "league_rammus_w_on";
/// 撞上的信号（本包挂 1 tick，副本 Q 的守望看到就撞）和本包给的加速。
pub const GO: &str = "league_rammus_q_go";
pub const RUSH: &str = "league_rammus_q_rush";
/// 锥刺甲壳：固定、法强 %、护甲 %（build_rammus.P 的 p_dmg / p_ap / p_arm，make_override.py 核对）。
pub const P_DMG: usize = 15;
pub const P_AP: usize = 30;
pub const P_ARM: usize = 15;
/// 动力冲刺：一 tick 一 tick 加速的起点、终点（移速 %）、几 tick 加满；离敌人多近算撞上（P 的 q_ms0 / q_ms1 / q_ramp / q_touch）。
pub const Q_MS0: usize = 30;
pub const Q_MS1: usize = 100;
pub const Q_RAMP: usize = 120;
pub const Q_TOUCH: usize = 26_000;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_RAMMUS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_rammus.log");
        }
    }
    PathBuf::from("league_rammus.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

pub(crate) fn counted(kind: &'static str) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (*n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

fn head(sim: &StableSim<'_>, id: usize) -> String {
    let o = sim.sim_origin().unwrap_or_default();
    let kind = match SimOriginKindV1::from_code(o.kind) {
        Some(SimOriginKindV1::ServerPresim) => "presim",
        Some(SimOriginKindV1::ClientMatchView) => "view",
        Some(SimOriginKindV1::ClientSpectate) => "spectate",
        Some(SimOriginKindV1::ClientReplay) => "replay",
        Some(SimOriginKindV1::Tool) => "tool",
        _ => "unknown",
    };
    let m = |v: u64| if v == SimOriginV1::NONE { "-".to_string() } else { v.to_string() };
    format!("[{kind} m={} s={}] t={} #{id}", m(o.match_id), m(o.set_index), sim.tick())
}

// ===================== 规则（单元测试用） =====================

pub type Pt = (f64, f64);

pub fn dist(a: Pt, b: Pt) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
}

/// 锥刺甲壳的伤害：固定 + 法强 % + 护甲 %。
pub fn spikes(ap: usize, armour: usize) -> usize {
    P_DMG + P_AP * ap / 100 + P_ARM * armour / 100
}

/// 滚了 t tick 时的加速（移速 %）：从 Q_MS0 线性加到 Q_MS1，Q_RAMP tick 加满。
pub fn rush(t: usize) -> i32 {
    let k = t.min(Q_RAMP);
    (Q_MS0 + (Q_MS1 - Q_MS0) * k / Q_RAMP) as i32
}

fn pos(sim: &StableSim<'_>, id: usize) -> Option<Pt> {
    sim.get_entity(id).map(|e| (e.pos().0 as f64, e.pos().1 as f64))
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn target_of(input: &InputTargetV1) -> Option<usize> {
    (InputTargetKindV1::from_code(input.kind) == Some(InputTargetKindV1::Target)).then_some(input.target_id)
}

// ===================== 锥刺甲壳（普攻里的原生效果） =====================

fn spikes_hit(sim: &mut StableSim<'_>, me: usize, input: InputTargetV1) {
    let Some(foe) = target_of(&input) else { return };
    if !sim.get_entity(foe).is_some_and(|e| e.is_alive()) {
        return;
    }
    let Some(st) = sim.get_entity(me).map(|e| e.stat()) else { return };
    let amount = spikes(st.magic_power, st.defence);
    sim.deal_damage_typed(me, foe, amount, DamageTypeV1::Ap, AttackTypeV1::BaseAttack);
    if let Some(k) = counted("spikes") {
        wlog(format!("{} SPIKES #{foe}: armour {} AP {} -> {amount} magic #{k}", head(sim, me), st.defence, st.magic_power));
    }
}

struct Step(fn(&mut StableSim<'_>, usize, InputTargetV1));
impl StableEffectType for Step {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        (self.0)(sim, caster, input);
    }
}

// ===================== 被动：动力冲刺的滚球 =====================

#[derive(Clone, Default)]
struct Shell {
    /// 这一次滚球已经滚了几 tick（没在滚是 None）。
    rolling: Option<usize>,
    /// 缩成球时的位置（日志里记滚了多远）。
    from: Option<Pt>,
}

impl Shell {
    /// 身边 Q_TOUCH 内最近的敌方单位（不算防御塔、要能被选中）。
    fn touched(sim: &StableSim<'_>, me: usize) -> Option<(usize, f64)> {
        let e = sim.get_entity(me)?;
        let (team, at) = (e.team(), (e.pos().0 as f64, e.pos().1 as f64));
        let mut best: Option<(usize, f64)> = None;
        for i in 0..sim.entity_count() {
            let Some(u) = sim.entity_at(i) else { continue };
            if u.team() == team || !u.is_alive() || u.is_tower() || !u.is_targetable() {
                continue;
            }
            let d = dist((u.pos().0 as f64, u.pos().1 as f64), at) - u.radius() as f64;
            if d <= Q_TOUCH as f64 && best.is_none_or(|b| d < b.1) {
                best = Some((u.id(), d));
            }
        }
        best
    }
}

impl StablePassive for Shell {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn on_spawn(&mut self, _sim: &mut StableSim<'_>, _player: usize, _entity: usize) {
        self.rolling = None;
        self.from = None;
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let alive = sim.get_entity(me).is_some_and(|e| e.is_alive());
        let ball = alive && has_buff(sim, me, BALL);
        if !ball {
            if let Some(t) = self.rolling.take() {
                sim.entity_remove_buff(me, RUSH);
                if let Some(k) = counted("roll") {
                    let far = match (self.from, pos(sim, me)) {
                        (Some(a), Some(b)) => dist(a, b),
                        _ => 0.0,
                    };
                    wlog(format!("{} ROLL over after {t} ticks, {far:.0} rolled #{k}", head(sim, me)));
                }
            }
            return;
        }
        let t = match self.rolling {
            None => {
                self.from = pos(sim, me);
                if let Some(k) = counted("roll") {
                    wlog(format!("{} ROLL curled up #{k}", head(sim, me)));
                }
                0
            }
            Some(t) => t + 1,
        };
        self.rolling = Some(t);
        // faster and faster: one buff, its speed raised every tick
        let mut b = BuffV1::timed(RUSH, 3);
        b.move_speed_mult = rush(t);
        sim.entity_remove_buff(me, RUSH);
        sim.add_buff(me, &b);
        if t % 24 == 12 {
            if let Some(at) = pos(sim, me) {
                sim.play_view_effect("league_rammus_q_dust", me, &InputTargetV1::pos(at.0 as u64, at.1 as u64), 0, 0, 0);
            }
        }
        if has_buff(sim, me, GO) {
            return;
        }
        if let Some((foe, d)) = Self::touched(sim, me) {
            sim.add_buff(me, &BuffV1::timed(GO, 2));
            if let Some(k) = counted("hit") {
                wlog(format!("{} ROLL hit #{foe} after {t} ticks at +{}% speed ({d:.0} away) #{k}", head(sim, me), rush(t)));
            }
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Rammus: Spiked Shell by armour, League's rolling Powerball, the ball / curl bodies) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    view::install_once();
    module.add_native_effect(format!("{ID}:spikes"), Step(spikes_hit));
    module.add_native_passive(format!("{ID}:shell"), Shell::default());
    host.log(LogLevel::Info, "league_rammus loaded (Spiked Shell by armour, the rolling Powerball, the ball / curl bodies).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

// league_addons compiles this file as one of its modules and registers it with the others
#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn spiked_shell_counts_armour() {
        assert_eq!(spikes(0, 0), 15);
        assert_eq!(spikes(100, 100), 15 + 30 + 15);
        assert_eq!(spikes(0, 300), 15 + 45); // a full tank: League's 10 + 15% of 300 armour, near enough
    }

    #[test]
    fn the_ball_speeds_up_then_holds() {
        assert_eq!(rush(0), 30);
        assert_eq!(rush(60), 65);
        assert_eq!(rush(120), 100);
        assert_eq!(rush(400), 100);
    }

    #[test]
    fn the_copy_names_this_crates_effects() {
        let s = include_str!("../override/league_rammus.data_champion");
        assert!(s.contains("\"league_rammus:shell\""));
        assert!(s.contains("\"league_rammus:spikes\""));
        assert!(s.contains(&format!("\"{BALL}\"")) && s.contains(&format!("\"{GO}\"")) && s.contains(&format!("\"{CURL}\"")));
    }
}
