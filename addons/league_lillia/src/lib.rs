//! 莉莉娅附加包：被动「梦满枝」的梦尘造成真正的百分比最大生命值魔法伤害，大招「夜阑谣」的昏睡受到伤害就醒（英雄联盟的规则）。
//!
//! 主包保持纯数据：数据里能读最大生命值的只有真实伤害（`FixedAttack` 的 `target_hp_ratio`），也没有「受伤就醒」的效果，
//! 所以主包的梦尘对英雄每次造成 `d_hp`% 最大生命值的真实伤害，大招让带梦尘的英雄困倦后眩晕（打不醒）。
//! `mod.override_info` 把主包的莉莉娅换成 `override/` 里的副本（`tools/kit/build_lillia.py` 的 `build(p, native=True)`）：
//!
//! - 技能打中敌方英雄时给他挂 buff `league_lillia_dust`（`d_t` tick，再中一下刷新），取代主包的真实伤害梦尘；
//! - 本包的被动 `league_lillia:dream` 每 tick 看一次：身上有梦尘的敌方英雄，从挂上的下一 tick 起每 `d_period` tick 受到
//!   `d_hp_bp` + 每 100 法强 `d_ap_bp`（万分比）× 最大生命值的**魔法伤害**；
//! - 莉莉娅身上出现大招的标记 `league_lillia_r_go`（主包的 R 照旧加它）时，所有带梦尘的敌方英雄**困倦**（buff
//!   `league_lillia_drowsy`，减速 `r_slow`%，`r_drowsy` tick），之后**昏睡**：原生眩晕 `r_sleep` tick + buff
//!   `league_lillia_sleep`（画面）；昏睡中生命 + 护盾少了（梦尘自己那一下除外）就**醒来**：眩晕解除，受到 `r_wake` +
//!   `r_wake_ratio`% 法强的魔法伤害（`league_lillia_wake` 的画面和声音）；
//! - 数据里的「Q / W 打到昏睡者加伤」那两段在副本里拿掉了（这里对任何伤害都生效）。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去）。状态记在每个莉莉娅自己的被动实例里，
//! 服务端预模拟和你看的那场各算各的。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_lillia.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_lillia";

/// 主包莉莉娅的名字（buff、声音、画面都以它开头）。
fn ll(x: &str) -> String {
    format!("league_lillia_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LILLIA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_lillia.log");
        }
    }
    PathBuf::from("league_lillia.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(&*LOG_PATH) {
        let _ = writeln!(f, "{}", msg.as_ref());
        let _ = f.flush();
    }
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
    /// 梦尘每隔多少 tick 跳一次。
    pub d_period: usize,
    /// 每跳：最大生命值的万分之 `d_hp_bp`，每 100 法强再加万分之 `d_ap_bp`。
    pub d_hp_bp: usize,
    pub d_ap_bp: usize,
    /// 困倦的 tick、减速 %，昏睡的 tick。
    pub r_drowsy: usize,
    pub r_slow: usize,
    pub r_sleep: usize,
    /// 惊醒伤害：固定值、法强 %。
    pub r_wake: usize,
    pub r_wake_ratio: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { d_period: 45, d_hp_bp: 100, d_ap_bp: 30, r_drowsy: 90, r_slow: 40, r_sleep: 120, r_wake: 80, r_wake_ratio: 40 }
    }
}

/// `{"d_period":45,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "d_period" => &mut p.d_period,
            "d_hp_bp" => &mut p.d_hp_bp,
            "d_ap_bp" => &mut p.d_ap_bp,
            "r_drowsy" => &mut p.r_drowsy,
            "r_slow" => &mut p.r_slow,
            "r_sleep" => &mut p.r_sleep,
            "r_wake" => &mut p.r_wake,
            "r_wake_ratio" => &mut p.r_wake_ratio,
            _ => continue,
        };
        *slot = v;
    }
    p.d_period = p.d_period.max(1);
    p
}

// ===================== 计算 =====================

/// 梦尘一跳的魔法伤害（减免前），至少 1。
pub fn dust_damage(p: &Params, max_hp: usize, ap: usize) -> usize {
    let bp = p.d_hp_bp as u64 + p.d_ap_bp as u64 * ap as u64 / 100;
    ((max_hp as u64 * bp / 10_000) as usize).max(1)
}

/// 惊醒伤害（减免前）。
pub fn wake_damage(p: &Params, ap: usize) -> usize {
    p.r_wake + p.r_wake_ratio * ap / 100
}

/// 昏睡中这一 tick 被打了没有：生命 + 护盾比上一 tick 少，而且少的比梦尘自己这一 tick 打的多。
pub fn was_hit(guard: usize, now: usize, own_dust: usize) -> bool {
    guard.saturating_sub(now) > own_dust
}

// ===================== 被动 =====================

#[derive(Clone, Debug)]
struct Dusted {
    target: usize,
    next: usize,
}

#[derive(Clone, Debug)]
struct Sleeper {
    target: usize,
    /// 困倦结束、睡着的 tick。
    sleep_at: usize,
    asleep: bool,
    /// 睡着后到这一 tick 自己醒。
    until: usize,
    /// 上一 tick 的生命 + 护盾。
    guard: usize,
}

/// 每个莉莉娅一份：参数、带梦尘的敌人、困倦 / 昏睡中的敌人、上一 tick 有没有大招标记、诊断计数。
#[derive(Clone, Default)]
struct Dream {
    p: Params,
    dusted: Vec<Dusted>,
    sleepers: Vec<Sleeper>,
    go_was: bool,
    ticks: usize,
    lullabies: usize,
    sleeps: usize,
    wakes: usize,
    next_report: usize,
}

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id)
        .map_or(false, |e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn guard_of(sim: &StableSim<'_>, id: usize) -> usize {
    sim.get_entity(id).map_or(0, |e| e.hp().0 + e.shield())
}

impl Dream {
    /// 梦尘：每个身上有 `league_lillia_dust` 的活着的敌方英雄按时跳伤害。返回这一 tick 每个目标吃了多少。
    fn dust(&mut self, sim: &mut StableSim<'_>, me: usize, team: usize, ap: usize, tick: usize) -> Vec<(usize, usize)> {
        let dust = ll("dust");
        let mut now: Vec<usize> = Vec::new();
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(e) = sim.get_entity(id) else { continue };
            if e.team() == team || !e.is_alive() {
                continue;
            }
            if has_buff(sim, id, &dust) {
                now.push(id);
            }
        }
        self.dusted.retain(|d| now.contains(&d.target));
        for id in &now {
            if !self.dusted.iter().any(|d| d.target == *id) {
                self.dusted.push(Dusted { target: *id, next: tick + 1 });
            }
        }
        let mut dealt = Vec::new();
        for d in self.dusted.iter_mut() {
            if tick < d.next {
                continue;
            }
            d.next = tick + self.p.d_period;
            let Some(max) = sim.get_entity(d.target).map(|e| e.hp().1) else { continue };
            let dmg = dust_damage(&self.p, max, ap);
            let before = guard_of(sim, d.target);
            sim.deal_damage_typed(me, d.target, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            dealt.push((d.target, before.saturating_sub(guard_of(sim, d.target))));
            self.ticks += 1;
        }
        dealt
    }

    /// 大招：标记刚出现的那一 tick，所有带梦尘的敌人困倦，`r_drowsy` tick 后睡着。
    fn lullaby(&mut self, sim: &mut StableSim<'_>, me: usize, tick: usize) {
        let go = has_buff(sim, me, &ll("r_go"));
        let rising = go && !self.go_was;
        self.go_was = go;
        if !rising {
            return;
        }
        self.lullabies += 1;
        let targets: Vec<usize> = self.dusted.iter().map(|d| d.target).collect();
        for id in &targets {
            let mut b = BuffV1::timed(&ll("drowsy"), self.p.r_drowsy);
            b.move_speed_mult = -(self.p.r_slow as i32);
            sim.add_buff(*id, &b);
            sim.play_sfx(&ll("drowsy"), me, &InputTargetV1::target(*id));
            self.sleepers.retain(|s| s.target != *id);
            self.sleepers.push(Sleeper { target: *id, sleep_at: tick + self.p.r_drowsy, asleep: false, until: 0, guard: 0 });
        }
        if self.lullabies <= 8 || self.lullabies % 20 == 0 {
            wlog(format!("{} LULLABY #{}: {} dusted champion(s) {:?}", head(sim, me), self.lullabies, targets.len(), targets));
        }
    }

    /// 困倦到点的睡着；睡着的被打了就醒（惊醒伤害），到时间自己醒。
    fn sleep(&mut self, sim: &mut StableSim<'_>, me: usize, ap: usize, tick: usize, dealt: &[(usize, usize)]) {
        let mut keep = Vec::new();
        for mut s in std::mem::take(&mut self.sleepers) {
            if !sim.get_entity(s.target).map_or(false, |e| e.is_alive()) {
                continue;
            }
            if !s.asleep {
                if tick < s.sleep_at {
                    keep.push(s);
                    continue;
                }
                let cc = CcV1 { tick: self.p.r_sleep as u64, ..CcV1::default() };
                sim.apply_cc(s.target, &cc);
                sim.add_buff(s.target, &BuffV1::timed(&ll("sleep"), self.p.r_sleep));
                sim.play_sfx(&ll("sleep"), me, &InputTargetV1::target(s.target));
                s.asleep = true;
                s.until = tick + self.p.r_sleep;
                s.guard = guard_of(sim, s.target);
                self.sleeps += 1;
                keep.push(s);
                continue;
            }
            let now = guard_of(sim, s.target);
            let own = dealt.iter().filter(|(t, _)| *t == s.target).map(|(_, d)| *d).sum();
            if was_hit(s.guard, now, own) {
                sim.entity_clear_cc(s.target);
                sim.entity_remove_buff(s.target, &ll("sleep"));
                let at = InputTargetV1::target(s.target);
                sim.play_view_effect(&ll("wake"), me, &at, 0, 0, 0);
                sim.play_sfx(&ll("wake"), me, &at);
                let dmg = wake_damage(&self.p, ap);
                sim.deal_damage_typed(me, s.target, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
                self.wakes += 1;
                if self.wakes <= 8 || self.wakes % 20 == 0 {
                    wlog(format!(
                        "{} WAKE #{}: #{} hit for {} while asleep ({} ticks left) -> {dmg} magic",
                        head(sim, me),
                        self.wakes,
                        s.target,
                        s.guard.saturating_sub(now),
                        s.until.saturating_sub(tick)
                    ));
                }
                continue;
            }
            if tick >= s.until {
                continue;
            }
            s.guard = now;
            keep.push(s);
        }
        self.sleepers = keep;
    }
}

impl StablePassive for Dream {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.go_was = false;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Lillia (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let ap = e.stat().magic_power;
        let tick = sim.tick();
        // the dust and the sleepers go on after her death (League's do); only a living Lillia starts a lullaby
        let dealt = self.dust(sim, me, team, ap, tick);
        if sim.get_entity(me).map_or(false, |e| e.is_alive()) {
            self.lullaby(sim, me, tick);
        }
        self.sleep(sim, me, ap, tick, &dealt);
        if tick >= self.next_report {
            self.next_report = tick + 1800;
            if tick > 0 {
                wlog(format!(
                    "{} WATCH: dust ticks {}, lullabies {}, sleeps {}, wakes {}",
                    head(sim, me),
                    self.ticks,
                    self.lullabies,
                    self.sleeps,
                    self.wakes
                ));
            }
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Lillia's Dream Dust as % max-health magic, a sleep that breaks on damage) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:dream"), Dream::default());
    host.log(LogLevel::Info, "league_lillia v1 loaded (Lillia's Dream Dust magic damage and a sleep that breaks on damage).");
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
    fn params_come_from_the_champion_data() {
        let p = parse_params(r#"{"d_period":30,"d_hp_bp":120,"d_ap_bp":20,"r_drowsy":60,"r_slow":30,"r_sleep":90,"r_wake":50,"r_wake_ratio":20,"x":1}"#);
        assert_eq!(p, Params { d_period: 30, d_hp_bp: 120, d_ap_bp: 20, r_drowsy: 60, r_slow: 30, r_sleep: 90, r_wake: 50, r_wake_ratio: 20 });
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"d_period":0}"#).d_period, 1);
    }

    #[test]
    fn dust_is_a_share_of_max_health_growing_with_ap() {
        let p = Params::default();
        assert_eq!(dust_damage(&p, 2000, 0), 20); // 1%
        assert_eq!(dust_damage(&p, 2000, 100), 26); // 1.3%
        assert_eq!(dust_damage(&p, 50, 0), 1); // at least 1
        assert_eq!(wake_damage(&p, 150), 140);
    }

    #[test]
    fn only_damage_beyond_her_own_dust_wakes() {
        assert!(!was_hit(1000, 1000, 0)); // nothing happened
        assert!(!was_hit(1000, 1010, 0)); // healed
        assert!(!was_hit(1000, 980, 20)); // her dust only
        assert!(was_hit(1000, 979, 20)); // her dust and one more point
        assert!(was_hit(1000, 900, 0)); // a hit (or a shield broken: guard counts the shield)
    }

    #[test]
    fn buff_names_fit() {
        for x in ["dust", "drowsy", "sleep", "r_go", "wake"] {
            assert!(ll(x).len() <= BUFF_NAME_CAP);
        }
    }
}
