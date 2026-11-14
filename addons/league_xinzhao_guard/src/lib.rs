//! 赵信附加包：R「新月护卫」之后 3 秒，挡住远处来的伤害（英雄联盟：免疫 450 码外敌人的伤害）。
//!
//! 主包保持纯数据：数据读不到伤害来自多远，主包的 R 之后 3 秒受到的伤害降低 40%（用户选的）。用户：「读不到多远就改
//! rust源代码 看看能不能」——这个附加包用原生代码读攻击者的位置：`mod.override_info` 把主包的赵信换成 `override/` 里的副本
//! （R 的护卫 buff `league_xinzhao_r_guard` 去掉 40% 减伤，只留画面和计时；`passive` 换成本包的 `league_xinzhao_guard:guard`），
//! 被动在他挨打时（`on_damaged`）看：护卫 buff 还在、攻击者离他超过 `far`（36000，英雄联盟的 450 码），这一下的伤害原样加回去。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从 tools/kit/build_xinzhao.py 的参数表 P 写进去），本包不另记一份。
//! 只有单元测试（经典 SDK 跑不了原生代码）。`on_damaged` 是在这一下扣血**之前**调的（0.1.1，2026-11-03 晚的日志：
//! `BLOCK 6 ...: hp 2750 -> 2750/2750` 之后下一下读到 2744，挡掉的 6 照样扣了）：先把血加上这一下，扣完正好回到原来的血；
//! 0.1.0 加到最大生命就停，满血、快满血时挡掉的伤害漏了进去（一次启动 230 下里 11 下、721 点）。超过上限的那一截（`refunded`
//! 的第二个数）记下来，这一下扣完以后再加回去：同一拍的下一下伤害来的时候（那时上一下已经扣了），或者下一拍。
//!
//! **三重爪击缩短别的冷却**（0.1.3，用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」，再说「接着做」）：英雄联盟
//! 的三重爪击（Q，V26.21）每一下 "reduce his other abilities' current cooldowns by 1 second"。主包的三下是他普攻树里的旗子
//! `league_xinzhao_q_1` → `q_2` → `q_3`（E 冲锋挂上第一个，每一下摘掉自己、挂上下一个；他的普攻树正在被另一边量，一点不能动），
//! 所以本包不碰普攻：被动每 tick 看他身上是哪一个旗子（[`q_state`]），1 → 2、2 → 3、3 → 没有（不是到时消失）就是刚打出了一下
//! （[`strike`]），用 `entity_reduce_cooldown` 把他的 E（技能，Q 并在里面）、W（技能 2）、R 当前的冷却各减 `Q_CUT`（60 tick）。
//! E 冲锋重新挂上第一个旗子不算。数据的三下照旧。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_xinzhao_guard.log`，每次启动游戏重写，上一次的留在 .prev.log。
//! 0.1.2：每种行整个启动一个计数（league_yasuo_wall 0.1.2 的做法：服务器的预演先记 40 行、之后每 100 行记一行，你看的那场每行都记，
//! 行末 `#k`）；以前一行都不限（11-08 一次启动 4303 行 BLOCK、519 行 BACK）。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_xinzhao_guard";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_xinzhao_guard") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
const GUARD: &str = "league_xinzhao_r_guard";
/// 三重爪击的三个旗子（主包普攻树里的，同时只有一个）。
pub const Q_FLAGS: [&str; 3] = ["league_xinzhao_q_1", "league_xinzhao_q_2", "league_xinzhao_q_3"];
/// 每一下给别的技能减的冷却（英雄联盟 1 秒）和减哪几格（E 带着 Q、W、R）。
pub const Q_CUT: usize = 60;
pub const Q_SLOTS: [SkillSlotV1; 3] = [SkillSlotV1::Skill, SkillSlotV1::Skill2, SkillSlotV1::Ult];
/// 旗子还剩这么多 tick 以上就没了：是打出去的那一下摘的，不是到时消失。
const Q_LIVE: usize = 3;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_XINZHAO_GUARD_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_xinzhao_guard.log");
        }
    }
    PathBuf::from("league_xinzhao_guard.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open: opening and closing it for every line took 0.6 ms a line in game (15 000 lines a session,
    // about 9 s of stalls on the simulation thread, 2026-10-12, the user: 「LOL mod让游戏掉帧很严重 加载很卡」)
    let mut file = LOG_FILE.lock().unwrap_or_else(|e| e.into_inner());
    if file.is_none() {
        *file = OpenOptions::new().create(true).append(true).open(&*LOG_PATH).ok();
    }
    if let Some(f) = file.as_mut() {
        let _ = f.write_all(format!("{}\n", msg.as_ref()).as_bytes());
    }
}

/// Lets go of the log file: each load starts a fresh one (renamed to .prev.log first), the tests delete it between runs.
fn close_log() {
    *LOG_FILE.lock().unwrap_or_else(|e| e.into_inner()) = None;
}

/// Lines a launch, each kind on its own count (0.1.2; 11-08's logs: 466 KB and 210 KB, every line written - 4303 BLOCK and
/// 519 BACK in one launch): the server's presims the first `LOG_FIRST`, then every `LOG_EVERY`-th; the match on screen all
/// of them (league_yasuo_wall 0.1.2's).
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;

static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

/// One more line of `kind`: its count this launch when it is to be written (`shown`: the match on screen).
fn noted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    (shown || *n <= LOG_FIRST || *n % LOG_EVERY == 0).then_some(*n)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

fn tally(sim: &StableSim<'_>, kind: &'static str) -> Option<usize> {
    noted(kind, on_screen(sim))
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

// ===================== 参数 =====================

/// 主包参数表 P 里本包用到的数字（`passive.params`，全是非负整数）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 攻击者离他超过这么远（距离单位，中心到中心），伤害挡掉。
    pub far: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { far: 36_000 }
    }
}

/// `{"far":36000}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        if k == "far" {
            p.far = v;
        }
    }
    p
}

// ===================== 判断 =====================

/// 这一下要不要挡：护卫还在，伤害大于 0，攻击者不是他自己，离他比 `far` 远。
pub fn blocks(p: &Params, guarded: bool, damage: usize, self_hit: bool, dist_sq: u64) -> bool {
    let far = p.far as u64;
    guarded && damage > 0 && !self_hit && dist_sq > far.saturating_mul(far)
}

/// 挡掉这一下：(现在设成的生命, 之后再加回的)。`on_damaged` 在扣血之前调，生命设成现在 + 这一下，扣完正好是现在的；
/// 生命最多设到上限，超出的那一截要等这一下扣完再加回去（0.1.0 直接丢了它：满血时挡掉的伤害照样扣）。
pub fn refunded(now: usize, max: usize, damage: usize) -> (usize, usize) {
    let want = now.saturating_add(damage);
    (want.min(max), want.saturating_sub(max))
}

/// 这一下扣完以后加回超出的那一截：生命 `hp` 加上 `owed`，不超过上限。
pub fn paid_back(hp: usize, max: usize, owed: usize) -> usize {
    hp.saturating_add(owed).min(max)
}

/// 他身上的三重爪击：(第几下的旗子 1..=3，0 = 没有, 它还剩几 tick)。
/// 他的 buff 一个一个看、名字按 `&str` 比，不为每个 buff 造一个 String（每 tick 都跑；league_renata 的 `any_buff` 说过：
/// 先把 buff 收集起来曾占合集后台模拟一半的时间）。
pub fn q_state(buffs: impl Iterator<Item = BuffV1>) -> (usize, usize) {
    for b in buffs {
        if let Some(i) = Q_FLAGS.iter().position(|f| *f == b.name()) {
            return (i + 1, b.duration_tick);
        }
    }
    (0, 0)
}

/// 上一 tick 和这一 tick 的 [`q_state`]：刚打出了第几下（1 -> 2、2 -> 3，或者 3 没了而且不是到时消失）。E 重新挂上第一个、
/// 旗子到时消失都不算。
pub fn strike(was: (usize, usize), now: (usize, usize)) -> Option<usize> {
    match (was.0, now.0) {
        (1, 2) | (2, 3) => Some(was.0),
        (3, 0) if was.1 > Q_LIVE => Some(3),
        _ => None,
    }
}

fn guarded(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == GUARD))
}

// ===================== 被动 =====================

#[derive(Clone, Default)]
struct Guard {
    p: Params,
    /// 挡掉的伤害里生命上限放不下的那一截（0.1.1）：这一下扣完血以后加回去（下一下伤害来时或下一拍）。
    owed: usize,
    /// 上一 tick 的三重爪击（[`q_state`]，0.1.3）。
    q: (usize, usize),
}

impl Guard {
    /// Three Talon Strike (0.1.3): a thrust just thrown (his flags moved on) takes `Q_CUT` off his other cooldowns.
    fn talons(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(now) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| {
            q_state((0..e.buff_count()).filter_map(|i| e.buff_at(i)))
        }) else {
            self.q = (0, 0);
            return;
        };
        let was = std::mem::replace(&mut self.q, now);
        let Some(k) = strike(was, now) else { return };
        let before: Vec<usize> = Q_SLOTS
            .iter()
            .map(|&s| sim.get_entity(me).and_then(|e| e.cooldown(s)).map_or(0, |c| c.remaining))
            .collect();
        for &s in &Q_SLOTS {
            sim.entity_reduce_cooldown(me, s, Q_CUT);
        }
        let after: Vec<usize> = Q_SLOTS
            .iter()
            .map(|&s| sim.get_entity(me).and_then(|e| e.cooldown(s)).map_or(0, |c| c.remaining))
            .collect();
        if let Some(n) = tally(sim, "talon") {
            wlog(format!("{} TALON {k}/3: E / W / R cooldowns {before:?} -> {after:?} (-{Q_CUT} each) #{n}", head(sim, me)));
        }
    }

    /// The blocked hits before now have landed: give back what his maximum health could not hold when they were blocked.
    fn pay_back(&mut self, sim: &mut StableSim<'_>, me: usize) {
        if self.owed == 0 {
            return;
        }
        let owed = std::mem::take(&mut self.owed);
        let Some((now, max)) = sim.get_entity(me).filter(|e| e.is_alive()).map(|e| e.hp()) else { return };
        let hp = paid_back(now, max, owed);
        sim.entity_set_hp(me, hp);
        if let Some(k) = tally(sim, "back") {
            wlog(format!("{} BACK {owed} the cap held back: hp {now} -> {hp}/{max} #{k}", head(sim, me)));
        }
    }
}

impl StablePassive for Guard {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, _: &mut StableSim<'_>, _: usize, _: usize) {
        self.owed = 0;
        self.q = (0, 0);
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        // every hit of the last tick has landed by now
        self.pay_back(sim, me);
        self.talons(sim, me);
    }

    fn on_damaged(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, attacker: usize, damage: usize) {
        if !sim.get_entity(me).is_some_and(|e| e.is_alive()) {
            self.owed = 0;
            return;
        }
        // this runs before the hit's health is taken off, after the hits before it in this tick landed (the 11-03 night
        // logs: two blocks in one tick, the second read the health the first left)
        self.pay_back(sim, me);
        let Some((now, max)) = sim.get_entity(me).map(|e| e.hp()) else { return };
        let dist_sq = sim.distance_sq(me, attacker);
        if !blocks(&self.p, guarded(sim, me), damage, attacker == me, dist_sq) {
            return;
        }
        let (hp, over) = refunded(now, max, damage);
        sim.entity_set_hp(me, hp);
        self.owed += over;
        if let Some(k) = tally(sim, "block") {
            wlog(format!(
                "{} BLOCK {damage} from #{attacker} at {:.0} (far {}): hp {now} -> {hp}/{max}{} #{k}",
                head(sim, me),
                (dist_sq as f64).sqrt(),
                self.p.far,
                if over > 0 { format!(", {over} back after the hit") } else { String::new() }
            ));
        }
    }

    fn on_dead(&mut self, _: &mut StableSim<'_>, _: usize) {
        self.owed = 0;
        self.q = (0, 0);
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Crescent Guard blocks the damage from afar; Three Talon Strike cuts his other cooldowns) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:guard"), Guard::default());
    host.log(LogLevel::Info, "league_xinzhao_guard v1 loaded (Xin Zhao's R blocks the damage from afar, Three Talon Strike cuts his other cooldowns).");
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
    fn presim_lines_are_capped_a_launch_the_screen_s_are_not() {
        // 0.1.1 wrote every BLOCK and BACK: 4822 lines in one launch
        let logged: Vec<usize> = (0..LOG_EVERY * 3).filter_map(|_| noted("test presim", false)).collect();
        assert_eq!(logged.len(), LOG_FIRST + 3);
        assert_eq!(logged[LOG_FIRST..], [LOG_EVERY, LOG_EVERY * 2, LOG_EVERY * 3]);
        assert!((0..LOG_EVERY * 2).all(|_| noted("test shown", true).is_some()));
    }

    #[test]
    fn each_thrust_thrown_is_a_strike_the_flags_running_out_are_not() {
        let st = |v: &[(&str, usize)]| q_state(v.iter().map(|(n, t)| BuffV1::timed(n, *t)));
        assert_eq!(st(&[("league_xinzhao_e_as", 200), ("league_xinzhao_q_2", 240)]), (2, 240));
        assert_eq!(st(&[("league_xinzhao_r_guard", 9)]), (0, 0));
        // E arms the first (from nothing, or again mid-way): no strike
        assert_eq!(strike((0, 0), (1, 240)), None);
        assert_eq!(strike((2, 100), (1, 240)), None);
        // the three thrusts
        assert_eq!(strike((1, 230), (2, 240)), Some(1));
        assert_eq!(strike((2, 200), (3, 240)), Some(2));
        assert_eq!(strike((3, 180), (0, 0)), Some(3));
        // a flag running out
        assert_eq!(strike((3, 2), (0, 0)), None);
        assert_eq!(strike((1, 1), (0, 0)), None);
        assert_eq!(strike((2, 50), (0, 0)), None, "only the third thrust takes the last flag");
        assert_eq!(Q_CUT, 60, "League: 1 second a thrust");
    }

    #[test]
    fn the_copy_still_carries_the_three_talon_flags_and_points_e_to_the_add_on_text() {
        let copy = include_str!("../override/league_xinzhao.data_champion").replace("\r\n", "\n");
        for f in Q_FLAGS {
            assert!(copy.contains(&format!("\"name\": \"{f}\"")), "the main pack's Three Talon Strike flag {f} is gone");
        }
        assert!(copy.contains("description.league_xinzhao_guard.skill"));
    }

    #[test]
    fn params_come_from_the_champion_data() {
        assert_eq!(parse_params(r#"{"far":30000,"unknown":4}"#).far, 30_000);
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn only_the_far_hits_while_guarded() {
        let p = Params::default();
        let far2 = 40_000u64 * 40_000;
        let near2 = 20_000u64 * 20_000;
        assert!(blocks(&p, true, 80, false, far2));
        assert!(!blocks(&p, true, 80, false, near2));          // the one beside him (the challenged) still hurts
        assert!(!blocks(&p, false, 80, false, far2));          // the guard is over
        assert!(!blocks(&p, true, 0, false, far2));
        assert!(!blocks(&p, true, 80, true, far2));            // his own costs
        assert!(!blocks(&p, true, 80, false, 36_000u64 * 36_000)); // exactly at the edge: not beyond it
    }

    #[test]
    fn the_refund_stops_at_full_health_and_owes_the_rest() {
        assert_eq!(refunded(500, 1000, 120), (620, 0));
        assert_eq!(refunded(950, 1000, 120), (1000, 70));
        assert_eq!(refunded(1000, 1000, 6), (1000, 6));
        assert_eq!(paid_back(930, 1000, 70), 1000);
        assert_eq!(paid_back(990, 1000, 70), 1000);
    }

    /// The host's order (the 11-03 night logs): `on_damaged` first, then the hit's health comes off; the next hit's
    /// `on_damaged` (or the next update) reads what the last one left. `owed` is paid back first, as the passive does.
    fn hit(hp: &mut usize, max: usize, owed: &mut usize, damage: usize, blocked: bool) {
        *hp = paid_back(*hp, max, std::mem::take(owed));
        if blocked {
            let (set, over) = refunded(*hp, max, damage);
            *hp = set;
            *owed += over;
        }
        *hp = hp.saturating_sub(damage);
    }

    #[test]
    fn blocked_damage_never_lands_even_at_full_health() {
        // `BLOCK 6 ...: hp 2750 -> 2750/2750`, then the next block read 2744: 0.1.0 lost the 6
        let (max, mut hp, mut owed) = (2750, 2750, 0);
        hit(&mut hp, max, &mut owed, 6, true);
        assert_eq!((hp, owed), (2744, 6), "the hit landed on the capped health");
        hp = paid_back(hp, max, std::mem::take(&mut owed)); // the next update
        assert_eq!(hp, 2750);
        // `BLOCK 449 ...: hp 2195 -> 2546/2546` and in the same tick `BLOCK 9 ...: hp 2097 -> 2106/2546` (98 lost)
        let (max, mut hp, mut owed) = (2546, 2195, 0);
        hit(&mut hp, max, &mut owed, 449, true);
        assert_eq!(hp, 2097);
        hit(&mut hp, max, &mut owed, 9, true);
        assert_eq!((hp, owed), (2195, 0), "the second block paid the first one's rest back before its own refund");
        // a near hit after a capped block in the same tick takes only its own damage
        let (max, mut hp, mut owed) = (2750, 2750, 0);
        hit(&mut hp, max, &mut owed, 300, true);
        hit(&mut hp, max, &mut owed, 100, false);
        assert_eq!(paid_back(hp, max, owed), 2650);
        // a far hit bigger than his health left is still blocked (the health is raised before it comes off)
        let (max, mut hp, mut owed) = (2000, 300, 0);
        hit(&mut hp, max, &mut owed, 500, true);
        assert_eq!((hp, owed), (300, 0));
    }
}
