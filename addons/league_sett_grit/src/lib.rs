//! 瑟提附加包：「豪意」照英雄联盟按受到的伤害攒（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补
//! 附加包」）。
//!
//! 主包是纯数据，读不到受到多少伤害：豪意按挨打的**次数**算（最多 5 层），W「蓄意轰拳」的护盾和正中的真实伤害按层数分 6 档。
//! 英雄联盟里豪意是受到的伤害本身，W 的护盾就是全部豪意，正中的真实伤害也随豪意涨。本包：副本的 W 只留最低那一档（没有
//! 豪意时的护盾和真实伤害），放出时给瑟提挂 `SPEND`；正中那条线给打中的人挂 `HIT`。被动 `league_sett_grit:grit`：
//!
//! - 每 tick 记下他生命的下降（受到的伤害，回血不抵），最近 `WINDOW` tick 的和就是豪意，最多 `cap`% 最大生命。
//! - 看到 `SPEND`：给他「豪意」那么多的护盾（`SHIELD_TICKS`，同主包的护盾时长），豪意清零；之后 `HIT_WINDOW` tick 内正中
//!   挨打的人各补 `true`% 豪意的真实伤害。数字在英雄数据的 `passive.params`。
//!
//! 头顶的豪意层数画面还是主包数据按次数挂的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_sett_grit.log`。
//!
//! E「强手裂颅」两侧都拉到人才眩晕（0.1.2，用户 2026-11-14 看了「和英雄联盟不一样的地方」清单后说「全改吧」）：英雄联盟
//! "If Facebreaker affects at least one enemy on each side, all enemies are stunned for 1 second"。主包的数据分不出前后
//! （圆形范围、没有方向），改成「拉到两个及以上」。副本在抓人前 1 tick 调用原生效果 `league_sett_grit:sides`：本包看他身边
//! `E_RADIUS`（加两人的身体）里会被拉的敌人（不含防御塔，免控、选不中的不算——英雄联盟里被法术护盾挡下的不算），有两个
//! 从他看过去夹角大于 90°（在他两边）就给他挂 `BOTH`，抓人那一刻数据读它决定全部眩晕还是减速（R 之后的连招照旧拉到一个也晕）。
//! 0.1.1：`W`、`SPAWN` 整个游戏一个计数（预模拟先记 40 行、之后每 200 行一行，你看的那场每行都记；以前每个被动自己数
//! 「前 80 行」），正中的几行只跟着记了的那次 `W` 写，参数只在第一行 `SPAWN` 写。

use std::collections::{HashMap, VecDeque};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_sett_grit";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_sett_grit") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
pub const SPEND: &str = "league_sett_grit_spend";
pub const HIT: &str = "league_sett_grit_hit";
/// 豪意攒多久（主包：4 秒没挨打就散）。
pub const WINDOW: usize = 240;
/// 主包 W 护盾的时长。
pub const SHIELD_TICKS: usize = 180;
pub const HIT_WINDOW: usize = 60;
/// E 的两侧：副本抓人前 1 tick 调用的原生效果、两边都有人时挂给他的旗子（抓人那一 tick 数据读）。
pub const SIDES: &str = "league_sett_grit:sides";
pub const BOTH: &str = "league_sett_grit_both";
pub const BOTH_T: usize = 3;
/// E 拉人的半径（主包的 `RangeEffect`，另加两人的身体；`make_override.py` 核对）。
pub const E_RADIUS: u64 = 24_000;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SETT_GRIT_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_sett_grit.log");
        }
    }
    PathBuf::from("league_sett_grit.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
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

fn head(sim: &StableSim<'_>, me: usize) -> String {
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
    format!("[{kind} m={} s={}] t={} #{me}", m(o.match_id), m(o.set_index), sim.tick())
}

/// Lines of each kind a launch (0.1.1, league_irelia's): the server's presims (hundreds a launch, each with new passives -
/// a count in the passive counts one sim) the first `LOG_FIRST`, then every `LOG_EVERY`-th; the match on screen all.
/// 2026-11-03 night logs: the passive's own "first 80" let 596 W and 409 center lines through (95% of the log).
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 200;

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

/// The params the log showed last (the champion data's: the same in every sim of a launch).
static PARAMS_SHOWN: Mutex<Option<Vec<(String, usize)>>> = Mutex::new(None);

/// `p` not in the log yet: once a launch, again only if they ever differ (league_talon_vault's).
fn params_new(p: &[(String, usize)]) -> bool {
    let mut shown = PARAMS_SHOWN.lock().unwrap_or_else(|e| e.into_inner());
    if shown.as_deref() == Some(p) {
        return false;
    }
    *shown = Some(p.to_vec());
    true
}

fn params(json: &str) -> Vec<(String, usize)> {
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    body.split(',')
        .filter_map(|pair| {
            let (k, v) = pair.split_once(':')?;
            Some((k.trim().trim_matches('"').to_string(), v.trim().parse::<usize>().ok()?))
        })
        .collect()
}

fn get(p: &[(String, usize)], k: &str, d: usize) -> usize {
    p.iter().find(|(n, _)| n == k).map_or(d, |(_, v)| *v)
}

// ===================== 豪意 =====================

/// The damage he took in the last `WINDOW` ticks: (tick, amount) chunks, oldest first.
#[derive(Clone, Debug, Default)]
pub struct Grit {
    chunks: VecDeque<(usize, usize)>,
    last_hp: Option<usize>,
}

impl Grit {
    /// Feed his hp at `tick`; returns the grit now, capped at `cap`.
    pub fn feed(&mut self, tick: usize, hp: usize, cap: usize) -> usize {
        if let Some(l) = self.last_hp {
            if hp < l {
                self.chunks.push_back((tick, l - hp));
            }
        }
        self.last_hp = Some(hp);
        while self.chunks.front().is_some_and(|c| c.0 + WINDOW <= tick) {
            self.chunks.pop_front();
        }
        self.now(cap)
    }

    pub fn now(&self, cap: usize) -> usize {
        self.chunks.iter().map(|c| c.1).sum::<usize>().min(cap)
    }

    pub fn clear(&mut self) {
        self.chunks.clear();
    }

    pub fn reset(&mut self) {
        self.chunks.clear();
        self.last_hp = None;
    }
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

#[derive(Clone, Default)]
struct GritPassive {
    p: Vec<(String, usize)>,
    grit: Grit,
    /// 刚花掉的豪意、那一刻的 tick（正中的真实伤害按它算）、这次 W 那一行的编号（记了才有；正中的几行跟着它记）。
    spent: Option<(usize, usize, Option<usize>)>,
}

impl StablePassive for GritPassive {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.grit.reset();
        self.spent = None;
        // the params in the first SPAWN line of a launch only; the line itself capped in the presims
        let params = params_new(&self.p).then(|| format!(", {:?}", self.p));
        if tally(sim, "spawn").is_some() || params.is_some() {
            wlog(format!("{} SPAWN: the add-on's Sett (player {player}){}", head(sim, me), params.unwrap_or_default()));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let tick = sim.tick();
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            self.grit.reset();
            return;
        }
        let (hp, max) = e.hp();
        let team = e.team();
        let spend = has_buff(&e, SPEND);
        let cap = max * get(&self.p, "cap", 50) / 100;
        let grit = self.grit.feed(tick, hp, cap);
        if spend {
            sim.entity_remove_buff(me, SPEND);
            if grit > 0 {
                sim.entity_add_shield(me, grit, SHIELD_TICKS);
            }
            self.grit.clear();
            // counted for the launch, not the passive (2026-11-03 night logs: each Sett's own "first 80")
            let k = tally(sim, "w");
            if let Some(k) = k {
                wlog(format!("{} W #{k}: grit {grit} (hp {hp}/{max}, cap {cap}) -> shield +{grit}", head(sim, me)));
            }
            self.spent = Some((grit, tick, k));
        }
        let Some((spent, at, line)) = self.spent else { return };
        if tick > at + HIT_WINDOW {
            self.spent = None;
            return;
        }
        let hit: Vec<usize> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_alive() && has_buff(u, HIT))
            .map(|u| u.id()).collect();
        let extra = spent * get(&self.p, "true", 25) / 100;
        for id in hit {
            sim.entity_remove_buff(id, HIT);
            if extra > 0 {
                sim.deal_damage_typed(me, id, extra, DamageTypeV1::Fixed, AttackTypeV1::Skill);
                // the center lines of a W whose own line was written
                if let Some(k) = line {
                    wlog(format!("{} W #{k} center on #{id}: +{extra} true damage", head(sim, me)));
                }
            }
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.grit.reset();
        self.spent = None;
    }
}

// ===================== E：两侧都拉到人才眩晕 =====================

/// 从 `me` 看过去，`foes` 里有没有两个在他两边（夹角大于 90°：两个方向的点积小于 0）。站在他身上的（方向是 0）不算。
pub fn both_sides(me: (u64, u64), foes: &[(u64, u64)]) -> bool {
    let dirs: Vec<(i64, i64)> = foes.iter()
        .map(|&(x, y)| (x as i64 - me.0 as i64, y as i64 - me.1 as i64))
        .filter(|&d| d != (0, 0))
        .collect();
    dirs.iter().enumerate().any(|(i, a)| dirs[i + 1..].iter().any(|b| a.0 * b.0 + a.1 * b.1 < 0))
}

/// 会被这一下 E 拉过来的敌人在不在 `E_RADIUS` 里（中心距离不超过半径加两人的身体，同主包的 `RangeEffect`）。
pub fn in_reach(d2: u64, body: usize, foe_body: usize) -> bool {
    let r = E_RADIUS + body as u64 + foe_body as u64;
    d2 <= r * r
}

/// 抓人前 1 tick：他两边都有会被拉的敌人就挂 `BOTH`。
fn sides(sim: &mut StableSim<'_>, sett: usize, _: InputTargetV1) {
    let Some((at, team, body)) = sim.get_entity(sett).filter(|e| e.is_alive()).map(|e| (e.pos(), e.team(), e.radius())) else {
        return;
    };
    let foes: Vec<(usize, (u64, u64), bool)> = (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|u| u.team() != team && u.is_alive() && u.is_targetable() && !u.is_tower()
            && !matches!(u.kind(), Some(EntityKindV1::Tower | EntityKindV1::Nexus)))
        .filter(|u| in_reach(sim.distance_sq(sett, u.id()), body, u.radius()))
        .filter(|u| !(0..u.buff_count()).filter_map(|i| u.buff_at(i)).any(|b| b.cc_immune))
        .map(|u| (u.id(), u.pos(), u.is_champion()))
        .collect();
    let spots: Vec<(u64, u64)> = foes.iter().map(|f| f.1).collect();
    let both = both_sides(at, &spots);
    sim.entity_remove_buff(sett, BOTH);
    if both {
        sim.add_buff(sett, &BuffV1::timed(BOTH, BOTH_T));
    }
    if let Some(k) = tally(sim, if both { "e both" } else { "e one side" }) {
        let champions = foes.iter().filter(|f| f.2).count();
        wlog(format!("{} E SIDES #{k}: {} enemies in reach ({champions} champions) - {}", head(sim, sett), foes.len(),
                     if both { "both sides: all stunned" } else { "one side: slowed" }));
    }
}

struct Sides;

impl StableEffectType for Sides {
    fn apply(&self, sim: &mut StableSim<'_>, _: u64, caster: usize, input: InputTargetV1) {
        sides(sim, caster, input);
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Sett's Grit from the damage he takes, Facebreaker stuns with enemies on both sides) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:grit"), GritPassive::default());
    module.add_native_effect(SIDES, Sides);
    host.log(LogLevel::Info, "league_sett_grit v1 loaded (Grit from the damage Sett takes, Facebreaker's two sides).");
}

#[cfg_attr(league_bundle, allow(dead_code))]
fn init(host: &StableHost) -> StableMod {
    let mut module = StableMod::new(ID);
    register(host, &mut module);
    module
}

#[cfg(not(league_bundle))]
declare_stable_mod!(init, requires = 9);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn grit_is_the_damage_of_the_last_four_seconds_capped() {
        let mut g = Grit::default();
        assert_eq!(g.feed(0, 1000, 500), 0);
        assert_eq!(g.feed(10, 900, 500), 100);
        assert_eq!(g.feed(20, 950, 500), 100); // a heal takes nothing back
        assert_eq!(g.feed(30, 600, 500), 450);
        assert_eq!(g.feed(40, 400, 500), 500);
        assert_eq!(g.feed(250, 400, 500), 500); // the first 100 has gone, 550 left, capped
        assert_eq!(g.feed(275, 400, 900), 200);
        assert_eq!(g.feed(500, 400, 500), 0);
    }

    #[test]
    fn presim_lines_are_capped_for_the_launch_and_the_match_on_screen_is_not() {
        let logged: Vec<usize> = (0..LOG_EVERY * 3).filter_map(|_| noted("test presim", false)).collect();
        assert_eq!(logged.len(), LOG_FIRST + 3);
        assert_eq!(logged[LOG_FIRST..], [LOG_EVERY, LOG_EVERY * 2, LOG_EVERY * 3]);
        assert!((0..LOG_EVERY * 2).all(|_| noted("test shown", true).is_some()));
    }

    /// League: "at least one enemy on each side"; here two of the enemies he pulls more than 90 degrees apart as seen
    /// from him.
    #[test]
    fn e_stuns_only_with_enemies_on_both_sides() {
        let me = (500_000, 500_000);
        // one in front, one behind: 180 degrees
        assert!(both_sides(me, &[(520_000, 500_000), (480_000, 500_000)]));
        // 120 degrees apart
        assert!(both_sides(me, &[(520_000, 500_000), (490_000, 517_320)]));
        // exactly 90 degrees: not more than 90
        assert!(!both_sides(me, &[(520_000, 500_000), (500_000, 520_000)]));
        // a crowd on one side (two, three of them) or a single enemy: no
        assert!(!both_sides(me, &[(520_000, 500_000), (515_000, 510_000)]));
        assert!(!both_sides(me, &[(520_000, 490_000), (515_000, 510_000), (530_000, 500_000)]));
        assert!(!both_sides(me, &[(520_000, 500_000)]));
        assert!(!both_sides(me, &[]));
        // one standing on him counts for no side; a third one behind the crowd does
        assert!(!both_sides(me, &[(500_000, 500_000), (520_000, 500_000)]));
        assert!(both_sides(me, &[(520_000, 490_000), (515_000, 510_000), (485_000, 500_000)]));
        // near the map's corner (small coordinates) the signs still work
        assert!(both_sides((10_000, 10_000), &[(0, 10_000), (30_000, 12_000)]));
    }

    #[test]
    fn e_reaches_as_far_as_the_datas_circle_with_both_bodies() {
        let r = E_RADIUS + 6_000 + 7_000;
        assert!(in_reach(r * r, 6_000, 7_000));
        assert!(!in_reach(r * r + 2 * r, 6_000, 7_000));
        assert!(in_reach(0, 0, 0));
    }

    /// The copy: E's stun reads `BOTH` (no "two or more" count left), set by `SIDES` one tick before the grab.
    #[test]
    fn the_copy_stuns_by_the_native_sides() {
        let copy = include_str!("../override/league_sett.data_champion").replace("\r\n", "\n");
        assert!(!copy.contains("league_sett_e_two") && !copy.contains("league_sett_e_one"), "the count is still there");
        assert_eq!(copy.matches(&format!("\"buff_name\": \"{BOTH}\"")).count(), 1, "the stun's switch");
        assert_eq!(copy.matches(&format!("\"effect_ref\": \"{SIDES}\"")).count(), 1, "the native");
        let native = copy.find(SIDES).unwrap();
        let before = &copy[..native];
        let delayed = before.rfind("\"type\": \"Delayed\"").unwrap();
        assert!(before[delayed..].contains("\"tick\": 7"), "the native is not one tick before the grab (8)");
        assert!(copy.contains("description.league_sett_grit.skill\""), "E's text is the add-on's");
    }

    #[test]
    fn the_params_are_logged_once() {
        let p = params(r#"{"cap":50,"true":25}"#);
        assert!(params_new(&p));
        assert!(!params_new(&p));
        assert!(params_new(&params(r#"{"cap":60,"true":25}"#)), "other params: again");
    }
}
