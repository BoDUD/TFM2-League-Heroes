//! 阿萝拉附加包：被动里的「灵纱洞开」按真实的生命触发（用户要的「残血时跳开」），驱灵奇术按敌人分别叠层，双界合一的领域按
//! 英雄联盟的规则，大招照会玩的阿萝拉来放（0.4.0，2026-11-26：「阿罗拉这个大招释放的没有英雄联盟高手的感觉」）。
//!
//! 主包保持纯数据：数据读不到生命、等级，`SwitchByBuff` 只看施法者身上的 buff，主包里阿萝拉的灵纱洞开是「有敌方英雄贴身」就
//! 后跳，驱灵奇术记在她身上；数据也找不到领域的边界、挪不了她，主包的领域只在她站在里面时减速其中的敌人。`mod.override_info`
//! 把主包的阿萝拉换成 `override/` 里的副本（tools/kit/build_aurora.py --native）：后跳还要她身上有 `league_aurora_low`，
//! 叠层和飞去来咒回程交给本包的原生效果（`spirit.rs`），领域交给本包（冲击波中心那根线的 end_effects 调 `league_aurora:rift`），
//! `passive` 换成本包的 `league_aurora:veil`：
//!
//! - 每 tick 读她的生命：低于最大生命的 `w_low`% 就挂上 3 tick 的 `league_aurora_low`（先摘再挂，只留一个），
//!   回到 `w_low`% 以上就不再挂，3 tick 后自己消失。数据在普攻和怪奇喷涌的开头读它（还要敌方英雄在 `w_near` 内、
//!   `w_cd` 已过）。她拿到击杀或助攻（读击杀记录）就摘掉灵纱洞开的冷却（英雄联盟 W 的规则）。
//! - 灵物（`spirit.rs` 抽出来的）：跟着她 `sp_t` tick，每 15 tick 按个数回一次血。
//! - 领域（`rift.rs`）：冲击波扩散 `r_grow` tick 后成形，按大招等级开 `r_t1`–`r_t3` tick；敌人碰到边界减速 `r_edge`%
//!   （一次穿越一次），她碰到边界就冲到对面（`r_wrap_t` tick），死了、出去了、成形时不在里面、时间到就关，里面没有敌方英雄了
//!   就提前关（英雄联盟再按 R）。
//!
//! 大招的时机和领域里怎么走由 AI 钩子 `league_aurora:realm` 挑（`realm.rs`：反开、一套带走、跟队友一起抓、开团、关住残血，
//! 其余时候按住；瞄准冲击波；领域里 R → E → Q、走 A、有人贴身就往边界走、穿到对面）。
//!
//! 数字从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份（原生效果读不到被动的参数，
//! 按 `Params` 的默认值，`make_override.py` 核对和 P 一样）。不用全局变量（只有日志的行数是全局的），服务端预模拟和你看的
//! 那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_aurora.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[allow(dead_code)]
#[path = "../../league_camille_wall/src/maps.rs"]
mod maps;
pub mod realm;
pub mod rift;
pub mod spirit;

const ID: &str = "league_aurora";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_aurora") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};
/// The flag the data's veil reads (build_aurora.py: `sw("low", hop)`).
const LOW: &str = "league_aurora_low";
/// Ticks the flag lasts: renewed every tick while she is low, gone 3 ticks after she is not.
const LOW_TICKS: usize = 3;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));
/// The first this many lines of a kind, then every LOG_EVERY-th (the match on screen: every line).
const LOG_FIRST: usize = 40;
const LOG_EVERY: usize = 100;

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_AURORA_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_aurora.log");
        }
    }
    PathBuf::from("league_aurora.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

fn wlog(msg: impl AsRef<str>) {
    let _guard = LOG_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    // the file stays open (league_olaf_rage's lesson: opening it for every line stalled the simulation thread)
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

/// The `n`-th line of a kind is written: every one in the match on screen (`shown`), the presims' first `LOG_FIRST`,
/// then every `LOG_EVERY`-th (league_qiyana's `logged`).
pub fn logged(n: usize, shown: bool) -> bool {
    shown || n <= LOG_FIRST || n % LOG_EVERY == 0
}

/// Counts a line of this kind (for the whole launch); Some(n) when it is to be written.
fn counted(kind: &'static str, shown: bool) -> Option<usize> {
    let mut c = COUNTS.lock().unwrap_or_else(|e| e.into_inner());
    let n = c.entry(kind).or_insert(0);
    *n += 1;
    logged(*n, shown).then_some(*n)
}

/// The match on screen (the client's view, spectating, a replay), not a server presim.
fn on_screen(sim: &StableSim<'_>) -> bool {
    sim.sim_origin().and_then(|o| SimOriginKindV1::from_code(o.kind)).is_some_and(|k| {
        matches!(k, SimOriginKindV1::ClientMatchView | SimOriginKindV1::ClientSpectate | SimOriginKindV1::ClientReplay)
    })
}

pub fn dist(a: (f64, f64), b: (f64, f64)) -> f64 {
    ((a.0 - b.0).powi(2) + (a.1 - b.1).powi(2)).sqrt()
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

/// 主包参数表 P 里本包用到的数字（`passive.params`）。
#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    /// 生命低于最大生命的这个百分比算「残血」。
    pub w_low: usize,
    /// 领域：冲击波扩散多少 tick 后成形，成形后开多少 tick（大招 1 / 2 / 3 级，英雄联盟 0.75 秒 + 2.25 / 2.75 / 3.25 秒）。
    pub r_grow: usize,
    pub r_t1: usize,
    pub r_t2: usize,
    pub r_t3: usize,
    /// 大招 2 级、3 级从多少级起（团战经理 12 级，英雄联盟 18 级的 6 / 11 / 16 级换过来，5 级才有大招）。
    pub r_lv2: usize,
    pub r_lv3: usize,
    /// 碰到边界的敌人减速多少 %、多少 tick（英雄联盟 50%、1.5 / 1.75 / 2 秒）。
    pub r_edge: usize,
    pub r_edge_t1: usize,
    pub r_edge_t2: usize,
    pub r_edge_t3: usize,
    /// 她冲到对面要多少 tick（英雄联盟 0.4 秒）。
    pub r_wrap_t: usize,
    /// 大招的 Realm Hopper：加速多少 %、从跃出起多少 tick（英雄联盟 3.25 / 3.75 / 4.25 秒）。
    pub r_ms: usize,
    pub r_ms_t1: usize,
    pub r_ms_t2: usize,
    pub r_ms_t3: usize,
    /// 跃出到落地（数据的 r_leap_t）：Realm Hopper 从跃出就开始了。
    pub r_leap_t: usize,
    /// 冲击波放出这么多 tick 后才能提前关（英雄联盟再按 R 要等 1 秒）。
    pub r_recast: usize,
    /// 驱灵奇术：层数留多久；第三层最大生命的千分之 p_hp_pm、每 100 法强再加千分之 p_hp_ap_pm。
    pub p_t: usize,
    pub p_hp_pm: usize,
    pub p_hp_ap_pm: usize,
    /// 灵物：每秒回 sp0（1 级）到 sp1（12 级）+ sp_ap% 法强，跟着她 sp_t tick，最多 sp_max 个。
    pub sp0: usize,
    pub sp1: usize,
    pub sp_ap: usize,
    pub sp_t: usize,
    pub sp_max: usize,
    /// 飞去来咒回程：q2_dmg + q2_ratio% 法强，按已损失生命最多加 q2_miss%，小兵 q2_minion%、野怪 q2_monster%，
    /// q2_again_t tick 内第二颗起 q2_again%。
    pub q2_dmg: usize,
    pub q2_ratio: usize,
    pub q2_miss: usize,
    pub q2_minion: usize,
    pub q2_monster: usize,
    pub q2_again: usize,
    pub q2_again_t: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self {
            w_low: 35,
            r_grow: 45, r_t1: 135, r_t2: 165, r_t3: 195, r_lv2: 8, r_lv3: 11,
            r_edge: 50, r_edge_t1: 90, r_edge_t2: 105, r_edge_t3: 120, r_wrap_t: 24,
            r_ms: 30, r_ms_t1: 195, r_ms_t2: 225, r_ms_t3: 255, r_leap_t: 14, r_recast: 60,
            p_t: 240, p_hp_pm: 10, p_hp_ap_pm: 27,
            sp0: 3, sp1: 20, sp_ap: 2, sp_t: 240, sp_max: 4,
            q2_dmg: 100, q2_ratio: 55, q2_miss: 50, q2_minion: 40, q2_monster: 50, q2_again: 20, q2_again_t: 60,
        }
    }
}

impl Params {
    /// 大招几级（1–3），按她的等级。
    pub fn rank(&self, level: usize) -> usize {
        if level >= self.r_lv3 {
            3
        } else if level >= self.r_lv2 {
            2
        } else {
            1
        }
    }

    fn by_rank(&self, level: usize, v: [usize; 3]) -> usize {
        v[self.rank(level) - 1]
    }

    /// 领域成形后开多少 tick、碰边界减速多少 tick、Realm Hopper 多少 tick（按大招的等级）。
    pub fn r_t(&self, level: usize) -> usize {
        self.by_rank(level, [self.r_t1, self.r_t2, self.r_t3])
    }

    pub fn r_edge_t(&self, level: usize) -> usize {
        self.by_rank(level, [self.r_edge_t1, self.r_edge_t2, self.r_edge_t3])
    }

    pub fn r_ms_t(&self, level: usize) -> usize {
        self.by_rank(level, [self.r_ms_t1, self.r_ms_t2, self.r_ms_t3])
    }
}

/// `{"w_low":35,"r_t1":135,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "w_low" => &mut p.w_low,
            "r_grow" => &mut p.r_grow,
            "r_t1" => &mut p.r_t1,
            "r_t2" => &mut p.r_t2,
            "r_t3" => &mut p.r_t3,
            "r_lv2" => &mut p.r_lv2,
            "r_lv3" => &mut p.r_lv3,
            "r_edge" => &mut p.r_edge,
            "r_edge_t1" => &mut p.r_edge_t1,
            "r_edge_t2" => &mut p.r_edge_t2,
            "r_edge_t3" => &mut p.r_edge_t3,
            "r_wrap_t" => &mut p.r_wrap_t,
            "r_ms" => &mut p.r_ms,
            "r_ms_t1" => &mut p.r_ms_t1,
            "r_ms_t2" => &mut p.r_ms_t2,
            "r_ms_t3" => &mut p.r_ms_t3,
            "r_leap_t" => &mut p.r_leap_t,
            "r_recast" => &mut p.r_recast,
            "p_t" => &mut p.p_t,
            "p_hp_pm" => &mut p.p_hp_pm,
            "p_hp_ap_pm" => &mut p.p_hp_ap_pm,
            "sp0" => &mut p.sp0,
            "sp1" => &mut p.sp1,
            "sp_ap" => &mut p.sp_ap,
            "sp_t" => &mut p.sp_t,
            "sp_max" => &mut p.sp_max,
            "q2_dmg" => &mut p.q2_dmg,
            "q2_ratio" => &mut p.q2_ratio,
            "q2_miss" => &mut p.q2_miss,
            "q2_minion" => &mut p.q2_minion,
            "q2_monster" => &mut p.q2_monster,
            "q2_again" => &mut p.q2_again,
            "q2_again_t" => &mut p.q2_again_t,
            _ => continue,
        };
        *slot = v;
    }
    p
}

// ===================== 计算 =====================

/// Is she low: health under w_low% of her maximum (a unit with no maximum never is).
pub fn is_low(p: &Params, hp: usize, max: usize) -> bool {
    max > 0 && hp * 100 < p.w_low * max
}

// ===================== 被动 =====================

/// 每个阿萝拉一份：参数、上一 tick 是不是残血（只为日志）、开着的领域、跟着她的灵物、读到第几条击杀记录。
#[derive(Clone, Default)]
struct Veil {
    p: Params,
    low: bool,
    turns: usize,
    rift: Option<rift::Rift>,
    /// 这条命的她（on_dead 只给玩家）。
    me: usize,
    /// 跟着她的灵物到哪一 tick（一起刷新，最多 sp_max 个）。
    spirits: Vec<usize>,
    /// 击杀记录读到第几条。
    kills_seen: usize,
}

/// 灵纱洞开的冷却（数据挂在她身上的 buff）：她拿到击杀或助攻就摘掉（英雄联盟 W 的规则）。
pub const VEIL_CD: &str = "league_aurora_w_cd";
/// 灵物多少 tick 回一次血。
pub const HEAL_EVERY: usize = 15;

/// 击杀记录里的「位置」是分路（LaneV1 的编号）：这一条算她的击杀或助攻吗。
pub fn is_takedown(k: &KillLogV1, team: usize, lane: u32) -> bool {
    k.killer_team == team
        && (k.killer_position == lane || k.assist_positions.iter().take(k.assist_count as usize).any(|&a| a == lane))
}

impl Veil {
    /// 新抽出的灵物（spirit.rs 挂的标记）、每 HEAL_EVERY tick 回一次血。
    fn spirits(&mut self, sim: &mut StableSim<'_>, me: usize, now: usize, level: usize, ap: usize, fresh: bool) {
        if fresh {
            sim.entity_remove_buff(me, spirit::NEW_SPIRIT);
            if self.spirits.len() < self.p.sp_max {
                self.spirits.push(now);
            }
            for t in self.spirits.iter_mut() {
                *t = now + self.p.sp_t;
            }
            sim.play_view_effect(spirit::HEAL_VIEW, me, &InputTargetV1::target(me), 0, 0, 0);
        }
        self.spirits.retain(|&t| now < t);
        if !self.spirits.is_empty() && now % HEAL_EVERY == 0 {
            let amount = self.spirits.len() * spirit::spirit_heal(&self.p, level, ap) * HEAL_EVERY / 60;
            if amount > 0 {
                sim.heal(me, me, amount);
            }
        }
    }

    /// 她拿到击杀或助攻：灵纱洞开的冷却清掉。
    fn takedowns(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        let n = sim.kill_log_count();
        if self.kills_seen > n {
            self.kills_seen = 0; // 被动换了一局，从头读
        }
        let Some((team, lane)) = sim.get_player(player).and_then(|p| Some((p.team(), p.lane()?.code()))) else {
            self.kills_seen = n;
            return;
        };
        let mut reset = false;
        while self.kills_seen < n {
            if let Some(k) = sim.kill_log_at(self.kills_seen) {
                reset |= is_takedown(&k, team, lane);
            }
            self.kills_seen += 1;
        }
        if reset && sim.entity_remove_buff(me, VEIL_CD) > 0 {
            if let Some(c) = counted("veil reset", on_screen(sim)) {
                wlog(format!("{} VEIL RESET: a takedown, Across the Veil is ready again #{c}", head(sim, me)));
            }
        }
    }
}

impl StablePassive for Veil {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.low = false;
        self.rift = None;
        self.spirits.clear();
        self.me = me;
        self.kills_seen = sim.kill_log_count();
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(n) = counted("spawn", on_screen(sim)) {
            wlog(format!("{} SPAWN: the add-on's Aurora (player {player}, team {team}), {:?} #{n}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, player: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() {
            return;
        }
        let (hp, max) = e.hp();
        let (level, ap) = (e.level(), e.stat().magic_power);
        let fresh = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == spirit::NEW_SPIRIT);
        let low = is_low(&self.p, hp, max);
        if low {
            sim.entity_remove_buff(me, LOW);
            sim.add_buff(me, &BuffV1::timed(LOW, LOW_TICKS));
        }
        if low != self.low {
            self.turns += 1;
            if self.turns <= 40 || self.turns % 100 == 0 {
                wlog(format!("{} {}: hp {hp}/{max} ({}%)", head(sim, me), if low { "LOW" } else { "UP" },
                             hp * 100 / max.max(1)));
            }
            self.low = low;
        }
        self.me = me;
        let now = sim.tick();
        self.spirits(sim, me, now, level, ap, fresh);
        self.takedowns(sim, player, me);
        rift::update(&mut self.rift, sim, me, &self.p);
    }

    fn on_dead(&mut self, sim: &mut StableSim<'_>, _: usize) {
        // 死了 buff 全清，下一条命满血；领域跟着关（英雄联盟一样），灵物也散了
        self.low = false;
        self.spirits.clear();
        if let Some(r) = self.rift.take() {
            rift::died(sim, self.me, &r);
        }
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    COUNTS.lock().unwrap_or_else(|e| e.into_inner()).clear();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Across the Veil at low health, Spirit Abjuration on each enemy, Between Worlds' rift as in League - its border slows, she crosses it - and its timing like a good Aurora player's) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:veil"), Veil::default());
    module.add_native_effect(format!("{ID}:rift"), rift::Open);
    for src in spirit::SOURCES {
        module.add_native_effect(format!("{ID}:mark_{src}"), spirit::Mark { src });
    }
    module.add_native_effect(format!("{ID}:hex_back"), spirit::HexBack);
    module.add_player_input_ai(realm::Realm::default());
    host.log(LogLevel::Info, "league_aurora loaded (Aurora's Across the Veil reads her health, her passive stacks on each enemy, her rift has League's border, her R is cast as a good player casts it).");
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
        assert_eq!(parse_params(r#"{"w_low":30,"x":1}"#), Params { w_low: 30, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
        assert_eq!(parse_params(r#"{"w_low":35,"r_t1":135,"r_edge":50,"r_edge_t2":105,"r_wrap_t":24}"#), Params::default());
        let p = parse_params(r#"{"r_t3": 150, "r_edge": 40, "r_edge_t1": 80, "r_wrap_t": 20, "q2_miss": 30}"#);
        assert_eq!((p.r_t3, p.r_edge, p.r_edge_t1, p.r_wrap_t, p.q2_miss), (150, 40, 80, 20, 30));
    }

    #[test]
    fn the_ult_grows_with_her_level() {
        let p = Params::default();
        assert_eq!((p.rank(5), p.rank(7), p.rank(8), p.rank(10), p.rank(11), p.rank(12)), (1, 1, 2, 2, 3, 3));
        // 英雄联盟：冲击波扩散 0.75 秒后领域 2.25 / 2.75 / 3.25 秒，边界减速 1.5 / 1.75 / 2 秒
        assert_eq!((p.r_t(5), p.r_t(9), p.r_t(12), p.r_grow), (135, 165, 195, 45));
        assert_eq!((p.r_edge_t(5), p.r_edge_t(9), p.r_edge_t(12)), (90, 105, 120));
        assert_eq!((p.r_ms_t(5), p.r_ms_t(9), p.r_ms_t(12)), (195, 225, 255));
    }

    #[test]
    fn a_takedown_is_hers_by_her_lane() {
        let k = KillLogV1 { tick: 10, killer_team: 0, killer_position: 2, killed_position: 0, assist_count: 2,
                            assist_positions: [1, 3, 0, 0] };
        assert!(is_takedown(&k, 0, 2), "her kill");
        assert!(is_takedown(&k, 0, 3), "an assist");
        assert!(!is_takedown(&k, 0, 4), "not in it");
        assert!(!is_takedown(&k, 1, 2), "the other team's");
        assert!(!is_takedown(&KillLogV1 { assist_count: 1, ..k }, 0, 3), "only the first assist_count count");
    }

    #[test]
    fn the_match_on_screen_logs_every_line() {
        assert!(logged(1, false) && logged(LOG_FIRST, false) && !logged(LOG_FIRST + 1, false));
        assert!(logged(LOG_EVERY, false) && logged(LOG_FIRST + 1, true));
    }

    #[test]
    fn low_is_under_the_threshold() {
        let p = Params::default();
        assert!(!is_low(&p, 1000, 1000));
        assert!(!is_low(&p, 350, 1000));
        assert!(is_low(&p, 349, 1000));
        assert!(is_low(&p, 1, 1000));
        assert!(!is_low(&p, 0, 0));
    }

    #[test]
    fn the_flag_is_the_one_the_data_reads() {
        assert_eq!(BuffV1::timed(LOW, LOW_TICKS).name(), "league_aurora_low");
    }
}
