//! 吉格斯扩展包（用户选：「可以」——小扩展包：W 炸塔 + 被动打塔加成）：主包数据读不到防御塔的血量，这两件事只能在这里做。
//!
//! `mod.override_info` 把主包的吉格斯换成 `override/` 里的副本（tools/kit/build_ziggs.py 的 native=1）：数据和主包一样，
//! 只是被动挂本包的 `league_ziggs:hexplode`，被动强化弹打中时给他挂 1 tick 的 `league_ziggs_p_now`。
//!
//! - **定点爆破炸塔**（英雄联盟：W 能直接炸掉血量低于 25–35% 的防御塔）：他活着、3 级以上、W 不在冷却（没有数据的
//!   `league_ziggs_w_cd`）、没在放别的技能（没有 `league_ziggs_busy`）时，每 tick 看身边 `w_hex_r` 以内的敌方防御塔，
//!   血量不到最大值的 `w_ex`% 就在塔上炸开炸药包（`league_ziggs_w_blast` 的画面和声音），把塔剩下的血全打掉（真实伤害，算他的
//!   击杀），给他挂上 `league_ziggs_w_cd`（`w_cd` tick），和数据里放一次 W 一样进冷却。本包不按任何技能键。
//! - **一触即发打塔**（英雄联盟：对建筑 ×1.75）：被动强化弹打中防御塔的那一下伤害 ×`p_tower`%（整下，含普攻本身的部分）。
//!
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_ziggs.log`，每次启动游戏重写。

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_ziggs";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是 league_addons 的。
const VERSION: &str = "0.1.0";

fn sn(x: &str) -> String {
    format!("league_ziggs_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ZIGGS_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_ziggs.log");
        }
    }
    PathBuf::from("league_ziggs.log")
}

static LOG_PATH: LazyLock<PathBuf> = LazyLock::new(log_path);

pub fn wlog(msg: impl AsRef<str>) {
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
const LOG_EVERY: usize = 50;
static COUNTS: LazyLock<Mutex<HashMap<&'static str, usize>>> = LazyLock::new(|| Mutex::new(HashMap::new()));

fn counted(kind: &'static str) -> Option<usize> {
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

// ===================== 参数 =====================

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Params {
    /// 炸塔的血量线：最大生命的百分比（英雄联盟 25–35%）。
    pub w_ex: u64,
    /// 炸塔的距离（他和塔中心）。
    pub w_hex_r: u64,
    /// 数据里 W 的冷却（tick）。
    pub w_cd: usize,
    /// 被动强化弹打塔的倍率（%）。
    pub p_tower: u64,
}

impl Default for Params {
    fn default() -> Self {
        Params { w_ex: 30, w_hex_r: 60000, w_cd: 900, p_tower: 175 }
    }
}

pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<u64>() else { continue };
        match k {
            "w_ex" => p.w_ex = v,
            "w_hex_r" => p.w_hex_r = v,
            "w_cd" => p.w_cd = v as usize,
            "p_tower" => p.p_tower = v,
            _ => {}
        }
    }
    p
}

// ===================== 计算（单元测试用） =====================

/// 这座塔低到能炸了吗（还活着、血量不到 w_ex%）。
pub fn hexplodable(p: &Params, hp: usize, max_hp: usize) -> bool {
    hp > 0 && max_hp > 0 && (hp as u64) * 100 <= p.w_ex * max_hp as u64
}

/// 塔在不在炸药包能扔到的地方。
pub fn in_reach(p: &Params, me: (u64, u64), tower: (u64, u64)) -> bool {
    let dx = me.0 as f64 - tower.0 as f64;
    let dy = me.1 as f64 - tower.1 as f64;
    dx * dx + dy * dy <= (p.w_hex_r as f64) * (p.w_hex_r as f64)
}

/// 被动强化弹打塔的伤害。
pub fn tower_hit(p: &Params, damage: usize) -> usize {
    (damage as u64 * p.p_tower / 100) as usize
}

// ===================== 被动 =====================

fn has(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

fn is_tower(sim: &StableSim<'_>, id: usize) -> bool {
    sim.get_entity(id).and_then(|e| e.kind()).is_some_and(|k| k == EntityKindV1::Tower)
}

#[derive(Clone, Default)]
struct Hexplode {
    p: Params,
    me: usize,
}

impl Hexplode {
    fn try_tower(&mut self, sim: &mut StableSim<'_>, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        if !e.is_alive() || e.level() < 3 {
            return;
        }
        let (team, pos) = (e.team(), e.pos());
        if has(sim, me, &sn("w_cd")) || has(sim, me, &sn("busy")) {
            return;
        }
        let mut found = None;
        for i in 0..sim.tower_count() {
            let id = sim.tower_id_at(i);
            let Some(t) = sim.get_entity(id) else { continue };
            if !t.is_alive() || t.team() == team {
                continue;
            }
            let (hp, max_hp) = t.hp();
            if hexplodable(&self.p, hp, max_hp) && in_reach(&self.p, pos, t.pos()) {
                found = Some((id, hp, max_hp, t.pos()));
                break;
            }
        }
        let Some((id, hp, max_hp, (x, y))) = found else { return };
        let at = InputTargetV1::pos(x, y);
        sim.play_view_effect(&sn("w_blast"), me, &at, 0, 0, 0);
        sim.play_sfx(&sn("w_blast"), me, &at);
        sim.play_sfx(&sn("vo_w"), me, &InputTargetV1::target(me));
        sim.deal_damage_typed(me, id, hp, DamageTypeV1::Fixed, AttackTypeV1::Skill);
        sim.add_buff(me, &BuffV1::timed(&sn("w_cd"), self.p.w_cd));
        if let Some(k) = counted("hexplode") {
            wlog(format!("{} HEXPLODE #{k}: tower #{id} at {hp}/{max_hp} blown up from ({}, {})", head(sim, me),
                         pos.0, pos.1));
        }
    }
}

impl StablePassive for Hexplode {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.me = me;
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        if let Some(k) = counted("spawn") {
            wlog(format!("{} SPAWN #{k}: the add-on's Ziggs (player {player}, team {team}), {:?}", head(sim, me), self.p));
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        self.try_tower(sim, me);
    }

    /// Short Fuse's bomb on a tower: x p_tower%.
    fn on_attack(&mut self, sim: &mut StableSim<'_>, _: usize, me: usize, target: usize, damage: &mut usize) {
        if *damage == 0 || !has(sim, me, &sn("p_now")) || !is_tower(sim, target) {
            return;
        }
        let was = *damage;
        *damage = tower_hit(&self.p, was);
        if let Some(k) = counted("fuse") {
            wlog(format!("{} FUSE #{k}: Short Fuse on tower #{target}: {was} -> {}", head(sim, me), *damage));
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Ziggs: Satchel Charge hexplodes low towers, Short Fuse x1.75 on towers) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:hexplode"), Hexplode::default());
    host.log(LogLevel::Info, "league_ziggs loaded (Satchel Charge hexplodes low towers, Short Fuse x1.75 on towers).");
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

    fn p() -> Params {
        Params::default()
    }

    #[test]
    fn params_from_the_kit() {
        assert_eq!(parse_params(r#"{"p_tower":175,"w_cd":900,"w_ex":30,"w_hex_r":60000}"#), Params::default());
    }

    #[test]
    fn hexplode_below_the_line_only() {
        assert!(hexplodable(&p(), 600, 2000));
        assert!(hexplodable(&p(), 1, 2000));
        assert!(!hexplodable(&p(), 601, 2000));
        assert!(!hexplodable(&p(), 0, 2000));
    }

    #[test]
    fn reach() {
        assert!(in_reach(&p(), (100000, 100000), (160000, 100000)));
        assert!(!in_reach(&p(), (100000, 100000), (160001, 100000)));
    }

    #[test]
    fn fuse_on_towers() {
        assert_eq!(tower_hit(&p(), 100), 175);
        assert_eq!(tower_hit(&p(), 0), 0);
    }
}
