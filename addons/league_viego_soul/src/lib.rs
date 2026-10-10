//! 佛耶戈附加包：被动「君命已决」照英雄联盟做——附身他参与击杀的英雄，**整个身体变成那个英雄**，用那类英雄的招式打。
//!
//! 主包是纯数据：数据看不到「谁死了」，只能靠一个「被打过的英雄身上的计时器断了」的近似（一个窗口里打过两个英雄，只看得到最后
//! 死的那个），附身后外形还是佛耶戈，只加一圈亡魂黑雾。`mod.override_info` 把主包的佛耶戈换成 `override/` 里的副本
//! （`make_override.py` 从 tools/kit/build_viego.py 的 native=1 生成）：他打中英雄时在对方身上挂 `league_viego_mark`
//! （p_win tick），被动 `league_viego_soul:possess` 每 tick：
//!
//! - **记功**：哪些敌方英雄身上有他的标记、最后一次看到是哪一 tick；
//! - **灵魂**：有标记的敌方英雄由活变死 = 他参与了击杀，尸体那里留下一个灵魂 soul_t tick；他活着、走到 soul_r 以内就**附身**
//!   （英雄联盟要去点那个灵魂；离得近就马上附身）；
//! - **附身** p_t tick：身上挂 `league_viego_soul:<英雄 id>`（给显示钩子看：整个身体画成那个英雄，src/view.rs）、
//!   `league_viego_soul_<类别>`（数据副本的普攻 / Q / W 按它换成五套招式之一：近战、射手、法师、辅助、刺客，类别按英雄 id 查
//!   src/souls.rs，查不到按攻击距离猜）、`league_viego_p_on`（借来的攻击 / 攻速 / 移速，远程类别再加攻击距离 s_range）、
//!   `league_viego_p_safe`（p_inv tick 无敌、免控）、一下技能冷却（p_skill：Q、W 刷新；大招按 p_ult）、回血，
//!   再挂 `league_viego_p_go` 让数据在他下一个动作里播吸魂的画面、动作和声音；
//! - **结束**：时间到、他阵亡、或数据的大招拿掉了 `league_viego_p_on`（英雄联盟：放 R 回到本体）——拿掉外形和类别 buff，
//!   挂 `league_viego_p_off` 让数据播回到本体的雾。
//!
//! 原生代码只做判断和 buff；画面、伤害在数据里。整身外形只在游戏 0.6.3 上（显示钩子核对函数开头），别的版本只有数据的黑雾。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_viego_soul.log`，每次启动游戏重写，上一次的留在 .prev.log。

use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

mod souls;
mod view;

const ID: &str = "league_viego_soul";
/// 主包里佛耶戈的 id。
pub const HERO: &str = "league_viego";
/// 数据副本挂在被打中的英雄身上的标记。
pub const MARK: &str = "league_viego_mark";
/// 给显示钩子的外形标记：`league_viego_soul:<英雄 id>`。
pub const LOOK: &str = "league_viego_soul:";
pub const ON: &str = "league_viego_p_on";
pub const SAFE: &str = "league_viego_p_safe";
pub const CDR: &str = "league_viego_p_cdr";
pub const GO: &str = "league_viego_p_go";
pub const OFF: &str = "league_viego_p_off";
/// 五套招式（数据副本里 `league_viego_soul_<类别>`）。
pub const CATS: [&str; 5] = ["melee", "range", "mage", "util", "assassin"];

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_VIEGO_SOUL_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_viego_soul.log");
        }
    }
    PathBuf::from("league_viego_soul.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub(crate) fn wlog(msg: impl AsRef<str>) {
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

// ===================== 计算 =====================

/// 从被动参数（整数 JSON，如 `{"p_t":600,"soul_r":35000}`）读一个值。
pub fn param(json: &str, key: &str) -> Option<u32> {
    let at = json.find(&format!("\"{key}\""))?;
    let rest = json[at + key.len() + 2..].trim_start().strip_prefix(':')?.trim_start();
    let end = rest.find(|c: char| !c.is_ascii_digit()).unwrap_or(rest.len());
    rest[..end].parse().ok()
}

/// 英雄 id → 五套招式之一：查表（本包英雄和原版英雄），查不到的（别的 mod）按攻击距离：35000 以上算射手。
pub fn category(name: &str, range: Option<u32>) -> &'static str {
    match souls::SOULS.binary_search_by(|s| s.0.cmp(name)) {
        Ok(i) => souls::SOULS[i].1,
        Err(_) if range.unwrap_or(0) >= 35000 => "range",
        Err(_) => "melee",
    }
}

/// 远程的三类（射手、法师、辅助）附身时加攻击距离。
pub fn ranged(cat: &str) -> bool {
    matches!(cat, "range" | "mage" | "util")
}

fn dist(a: (u64, u64), b: (u64, u64)) -> u64 {
    let dx = a.0.abs_diff(b.0) as f64;
    let dy = a.1.abs_diff(b.1) as f64;
    (dx * dx + dy * dy).sqrt() as u64
}

fn buff_names(sim: &StableSim<'_>, id: usize) -> Vec<String> {
    sim.get_entity(id).map_or_else(Vec::new, |e| {
        (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect()
    })
}

fn timed(name: &str, ticks: u32) -> BuffV1 {
    let mut b = BuffV1::named(name);
    b.duration_kind = BuffDurationV1::Time.code();
    b.duration_tick = ticks as usize;
    b
}

// ===================== 被动 =====================

#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub p_t: u32,
    pub p_inv: u32,
    pub p_heal: u32,
    pub p_heal_ratio: u32,
    pub p_ad: u32,
    pub p_as: u32,
    pub p_ms: u32,
    pub p_skill: u32,
    pub p_ult: u32,
    pub p_win: u32,
    pub soul_r: u32,
    pub soul_t: u32,
    pub s_range: u32,
}

impl Default for Params {
    fn default() -> Self {
        Params { p_t: 600, p_inv: 60, p_heal: 60, p_heal_ratio: 50, p_ad: 25, p_as: 30, p_ms: 15, p_skill: 10000,
                 p_ult: 0, p_win: 180, soul_r: 35000, soul_t: 480, s_range: 25000 }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct Soul {
    pub name: String,
    pub cat: &'static str,
    pub pos: (u64, u64),
    pub until: usize,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Possession {
    pub name: String,
    pub cat: &'static str,
    pub until: usize,
}

#[derive(Clone, Default)]
pub struct Possess {
    pub p: Params,
    /// 敌方英雄 → (最后一次看到他的标记的 tick, 上一 tick 活着)。
    pub marked: Vec<(usize, usize, bool)>,
    pub souls: Vec<Soul>,
    pub on: Option<Possession>,
    pub was_alive: bool,
}

impl Possess {
    /// 一个有标记的敌方英雄阵亡（`died` tick，最后一次看到标记在 `seen`）：算不算他的功劳。
    pub fn credited(&self, seen: usize, died: usize) -> bool {
        died <= seen + 3 || died - seen <= self.p.p_win as usize
    }

    /// 灵魂里离他最近、在 soul_r 以内的那个。
    pub fn reachable(&self, me: (u64, u64)) -> Option<usize> {
        self.souls
            .iter()
            .enumerate()
            .filter(|(_, s)| dist(s.pos, me) <= self.p.soul_r as u64)
            .min_by_key(|(_, s)| dist(s.pos, me))
            .map(|(i, _)| i)
    }

    fn end(&mut self, sim: &mut StableSim<'_>, me: usize, why: &str) {
        let Some(on) = self.on.take() else { return };
        sim.entity_remove_buff(me, &format!("{LOOK}{}", on.name));
        sim.entity_remove_buff(me, &format!("league_viego_soul_{}", on.cat));
        sim.entity_remove_buff(me, ON);
        sim.entity_remove_buff(me, SAFE);
        if why != "dead" {
            sim.entity_remove_buff(me, OFF);
            sim.add_buff(me, &timed(OFF, 600));
        }
        wlog(format!("{} END possession of {} ({why})", head(sim, me), on.name));
    }

    fn possess(&mut self, sim: &mut StableSim<'_>, me: usize, soul: Soul) {
        if self.on.is_some() {
            self.end(sim, me, "a new soul");
            sim.entity_remove_buff(me, OFF);
        }
        let p = self.p.clone();
        sim.add_buff(me, &timed(&format!("{LOOK}{}", soul.name), p.p_t));
        sim.add_buff(me, &timed(&format!("league_viego_soul_{}", soul.cat), p.p_t));
        let mut on = timed(ON, p.p_t);
        on.attack_mult = p.p_ad as i32;
        on.attack_speed_mult = p.p_as as i32;
        on.move_speed_mult = p.p_ms as i32;
        if ranged(soul.cat) {
            on.range = p.s_range as usize;
        }
        sim.entity_remove_buff(me, ON);
        sim.add_buff(me, &on);
        let mut safe = timed(SAFE, p.p_inv);
        safe.damaged_reduce = 100;
        safe.cc_immune = true;
        sim.entity_remove_buff(me, SAFE);
        sim.add_buff(me, &safe);
        let mut cdr = timed(CDR, 2);
        cdr.skill_cooldown_mult = p.p_skill as i32;
        cdr.ult_cooldown_mult = p.p_ult as i32 - p.p_skill as i32;
        sim.add_buff(me, &cdr);
        sim.entity_remove_buff(me, GO);
        sim.add_buff(me, &timed(GO, 600));
        let atk = sim.get_entity(me).map_or(0, |e| e.stat().attack.max(0) as usize);
        let heal = p.p_heal as usize + atk * p.p_heal_ratio as usize / 100;
        sim.heal(me, me, heal);
        wlog(format!("{} POSSESS {} ({}) for {} ticks, heal {heal}", head(sim, me), soul.name, soul.cat, p.p_t));
        self.on = Some(Possession { name: soul.name, cat: soul.cat, until: sim.tick() + p.p_t as usize });
    }
}

impl StablePassive for Possess {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        let d = Params::default();
        let g = |k: &str, v: u32| param(params_json, k).unwrap_or(v);
        self.p = Params {
            p_t: g("p_t", d.p_t).max(1),
            p_inv: g("p_inv", d.p_inv),
            p_heal: g("p_heal", d.p_heal),
            p_heal_ratio: g("p_heal_ratio", d.p_heal_ratio),
            p_ad: g("p_ad", d.p_ad),
            p_as: g("p_as", d.p_as),
            p_ms: g("p_ms", d.p_ms),
            p_skill: g("p_skill", d.p_skill),
            p_ult: g("p_ult", d.p_ult),
            p_win: g("p_win", d.p_win),
            soul_r: g("soul_r", d.soul_r),
            soul_t: g("soul_t", d.soul_t),
            s_range: g("s_range", d.s_range),
        };
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _player: usize, me: usize) {
        let now = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        let (alive, team, mpos) = (e.is_alive(), e.team(), e.pos());
        if alive != self.was_alive {
            self.was_alive = alive;
            if !alive {
                self.end(sim, me, "dead");
                self.souls.clear();
            }
        }
        // 记功：敌方英雄身上的标记；有标记的由活变死 = 一个灵魂
        let mut born = Vec::new();
        for i in 0..sim.champion_count() {
            let id = sim.champion_id_at(i);
            let Some(c) = sim.get_entity(id) else { continue };
            if c.team() == team {
                continue;
            }
            let c_alive = c.is_alive();
            let has = (0..c.buff_count()).filter_map(|k| c.buff_at(k)).any(|b| b.name() == MARK);
            let slot = match self.marked.iter().position(|m| m.0 == id) {
                Some(s) => s,
                None => {
                    self.marked.push((id, usize::MAX, c_alive));
                    self.marked.len() - 1
                }
            };
            if has && c_alive {
                self.marked[slot].1 = now;
            }
            let (seen, was) = (self.marked[slot].1, self.marked[slot].2);
            if was && !c_alive && seen != usize::MAX && self.credited(seen, now) {
                let name = c.name().unwrap_or_default();
                let range = None::<u32>;
                born.push(Soul { cat: category(&name, range), name, pos: c.pos(), until: now + self.p.soul_t as usize });
            }
            self.marked[slot].2 = c_alive;
        }
        for s in born {
            wlog(format!("{} SOUL {} ({}) at {:?}, {} away", head(sim, me), s.name, s.cat, s.pos, dist(s.pos, mpos)));
            self.souls.retain(|o| o.name != s.name);
            self.souls.push(s);
        }
        self.souls.retain(|s| s.until > now);
        // 附身中：时间到 / 数据的大招拿掉了 p_on
        if let Some(on) = &self.on {
            if now >= on.until {
                self.end(sim, me, "time");
            } else if !buff_names(sim, me).iter().any(|b| b == ON) {
                self.end(sim, me, "Heartbreaker");
            }
        }
        if alive {
            if let Some(i) = self.reachable(mpos) {
                let s = self.souls.remove(i);
                self.possess(sim, me, s);
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
        "=== {ID} v{} (Viego: possess the champions he helps kill, their whole body on game 0.6.3) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:possess"), Possess::default());
    view::install_once();
    host.log(LogLevel::Info, "league_viego_soul loaded (Viego: Sovereign's Domination as in League).");
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
    fn params_are_read_from_the_passive_json() {
        let mut p = Possess::default();
        p.configure(r#"{"p_t":540,"soul_r":30000,"s_range":20000}"#);
        assert_eq!((p.p.p_t, p.p.soul_r, p.p.s_range, p.p.p_win), (540, 30000, 20000, 180));
    }

    #[test]
    fn categories_come_from_the_table_or_the_range() {
        assert_eq!(category("league_jinx", None), "range");
        assert_eq!(category("league_garen", None), "melee");
        assert_eq!(category("league_lux", None), "mage");
        assert_eq!(category("league_soraka", None), "util");
        assert_eq!(category("league_zed", None), "assassin");
        assert_eq!(category("archer", None), "range");
        assert_eq!(category("someone_elses_hero", Some(60000)), "range");
        assert_eq!(category("someone_elses_hero", None), "melee");
        assert!(ranged("mage") && !ranged("assassin"));
    }

    #[test]
    fn a_death_counts_inside_the_window() {
        let p = Possess::default();
        assert!(p.credited(1000, 1001));
        assert!(p.credited(1000, 1180));
        assert!(!p.credited(1000, 1181));
    }

    #[test]
    fn the_nearest_soul_in_reach_is_taken() {
        let mut p = Possess::default();
        let s = |n: &str, x| Soul { name: n.into(), cat: "melee", pos: (x, 0), until: 99 };
        p.souls = vec![s("a", 50_000), s("b", 20_000), s("c", 30_000)];
        assert_eq!(p.reachable((0, 0)), Some(1));
        p.souls = vec![s("a", 50_000)];
        assert_eq!(p.reachable((0, 0)), None);
    }

    #[test]
    fn the_table_is_sorted_for_the_search() {
        assert!(souls::SOULS.windows(2).all(|w| w[0].0 < w[1].0));
        assert!(souls::SOULS.iter().all(|s| CATS.contains(&s.1)));
    }
}
