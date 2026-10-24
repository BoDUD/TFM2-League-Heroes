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

use std::collections::VecDeque;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_sett_grit";
pub const SPEND: &str = "league_sett_grit_spend";
pub const HIT: &str = "league_sett_grit_hit";
/// 豪意攒多久（主包：4 秒没挨打就散）。
pub const WINDOW: usize = 240;
/// 主包 W 护盾的时长。
pub const SHIELD_TICKS: usize = 180;
pub const HIT_WINDOW: usize = 60;

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
    /// 刚花掉的豪意和那一刻的 tick（正中的真实伤害按它算）。
    spent: Option<(usize, usize)>,
    n: usize,
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
        wlog(format!("{} SPAWN: the add-on's Sett (player {player}), {:?}", head(sim, me), self.p));
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
            self.spent = Some((grit, tick));
            self.n += 1;
            if self.n <= 80 || self.n % 25 == 0 {
                wlog(format!("{} W #{}: grit {grit} (hp {hp}/{max}, cap {cap}) -> shield +{grit}", head(sim, me), self.n));
            }
        }
        let Some((spent, at)) = self.spent else { return };
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
                if self.n <= 80 {
                    wlog(format!("{} W #{} center on #{id}: +{extra} true damage", head(sim, me), self.n));
                }
            }
        }
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        self.grit.reset();
        self.spent = None;
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Sett's Grit from the damage he takes) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:grit"), GritPassive::default());
    host.log(LogLevel::Info, "league_sett_grit v1 loaded (Grit from the damage Sett takes).");
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
}
