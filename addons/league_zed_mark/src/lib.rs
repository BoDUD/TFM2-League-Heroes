//! 劫附加包：被动「影忍法·灭魂劫」读真实生命，大招「禁奥义！瞬狱影杀阵」按印记期间真实打出的伤害结算（用户：「这个改成用 rust 附加包」）。
//!
//! 主包保持纯数据：数据读不到生命也读不到伤害，主包里劫的被动是「技能刚打中过英雄」后的下一次普攻（`league_zed_cw_ready`），
//! 大招爆发按印记期间他打中英雄的次数（`r_1`..`r_3`）加伤害。`mod.override_info` 把主包的劫换成 `override/` 里的副本
//! （tools/kit/build_zed.py 的 native=1）：这两段数据去掉，`passive` 换成本包的 `league_zed_mark:edge`：
//!
//! - **蔑视弱者**：副本的普攻打中英雄时给目标挂 2 tick 的 `league_zed_cw_probe`；这里每 tick 看到它，目标**生命低于 `cw_hp`%**、
//!   这个目标的 `cw_cd` 冷却已过，就追加目标最大生命的 `cw_lo`/`cw_mid`/`cw_hi`%（劫 1–6 / 7–12 / 13 级起，英雄联盟的 6/8/10%）
//!   魔法伤害，播 `league_zed_cw_hit`（画面在数据里）。
//! - **死亡印记**：目标身上有 `league_zed_r_mark`（数据加的，`r_pop` tick）时，他打到这个目标的伤害（`on_attack`，技能也算）
//!   记下来；印记一消失（爆发那一刻），追加记下伤害的 `r_pct`%（物理）。数据的爆发（基础伤害、画面、声音）照旧。
//!
//! 数字都从英雄数据的 `passive.params` 来（`make_override.py` 从参数表 P 写进去），本包不另记一份。不用全局变量，服务端预模拟和
//! 你看的那场各算各的。日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_zed_mark.log`，每次启动游戏重写。

use std::collections::BTreeMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_zed_mark";

/// 主包劫的名字（buff、画面都以它开头）。
fn zd(x: &str) -> String {
    format!("league_zed_{x}")
}

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_ZED_MARK_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_zed_mark.log");
        }
    }
    PathBuf::from("league_zed_mark.log")
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
    /// 目标生命低于 `cw_hp`% 时触发蔑视弱者。
    pub cw_hp: usize,
    /// 追加目标最大生命的百分比：1–6 级、7–12 级、13 级起。
    pub cw_lo: usize,
    pub cw_mid: usize,
    pub cw_hi: usize,
    /// 同一个目标两次蔑视弱者之间的 tick。
    pub cw_cd: usize,
    /// 印记爆发追加记下伤害的百分比。
    pub r_pct: usize,
}

impl Default for Params {
    fn default() -> Self {
        Self { cw_hp: 50, cw_lo: 6, cw_mid: 8, cw_hi: 10, cw_cd: 600, r_pct: 35 }
    }
}

/// `{"cw_hp":50,...}` -> 参数；缺的键用默认值，认不得的键忽略。
pub fn parse_params(json: &str) -> Params {
    let mut p = Params::default();
    let body = json.trim().trim_start_matches('{').trim_end_matches('}');
    for pair in body.split(',') {
        let Some((k, v)) = pair.split_once(':') else { continue };
        let k = k.trim().trim_matches('"');
        let Ok(v) = v.trim().parse::<usize>() else { continue };
        let slot = match k {
            "cw_hp" => &mut p.cw_hp,
            "cw_lo" => &mut p.cw_lo,
            "cw_mid" => &mut p.cw_mid,
            "cw_hi" => &mut p.cw_hi,
            "cw_cd" => &mut p.cw_cd,
            "r_pct" => &mut p.r_pct,
            _ => continue,
        };
        *slot = v;
    }
    p
}

// ===================== 计算 =====================

/// 蔑视弱者的百分比（按劫的等级）。
pub fn cw_share(p: &Params, level: usize) -> usize {
    match level {
        0..=6 => p.cw_lo,
        7..=12 => p.cw_mid,
        _ => p.cw_hi,
    }
}

/// 该不该触发：目标生命低于线、冷却已过。
pub fn want_contempt(p: &Params, hp: usize, max: usize, now: usize, ready_at: usize) -> bool {
    max > 0 && hp * 100 < p.cw_hp * max && now >= ready_at
}

/// 蔑视弱者的伤害：目标最大生命的 share%，至少 1。
pub fn contempt_damage(max: usize, share: usize) -> usize {
    (max * share / 100).max(1)
}

/// 印记爆发追加的伤害。
pub fn mark_bonus(p: &Params, stored: usize) -> usize {
    stored * p.r_pct / 100
}

// ===================== 小工具 =====================

fn has_buff(sim: &StableSim<'_>, id: usize, name: &str) -> bool {
    sim.get_entity(id).is_some_and(|e| (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name))
}

/// 敌方活着的英雄。
fn enemy_champions(sim: &StableSim<'_>, team: usize) -> Vec<usize> {
    (0..sim.entity_count())
        .filter_map(|i| sim.entity_at(i))
        .filter(|e| e.is_champion() && e.is_alive() && e.team() != team)
        .map(|e| e.id())
        .collect()
}

// ===================== 被动 =====================

/// 一个印记：记下的伤害、挂上时目标的生命（日志对照用）。
#[derive(Clone, Copy, Debug, Default)]
struct Mark {
    stored: usize,
    hp_at: usize,
}

/// 每个劫一份：参数、每个目标的蔑视弱者冷却（到哪一 tick）、正在跑的印记。
#[derive(Clone, Default)]
struct Edge {
    p: Params,
    cw_ready: BTreeMap<usize, usize>,
    marks: BTreeMap<usize, Mark>,
    cw_count: usize,
    pops: usize,
}

impl Edge {
    fn contempt(&mut self, sim: &mut StableSim<'_>, me: usize, enemies: &[usize]) {
        let probe = zd("cw_probe");
        let tick = sim.tick();
        let level = sim.get_entity(me).map_or(1, |e| e.level());
        for &t in enemies {
            if !has_buff(sim, t, &probe) {
                continue;
            }
            sim.entity_remove_buff(t, &probe);
            let Some((hp, max)) = sim.get_entity(t).map(|e| e.hp()) else { continue };
            let ready_at = self.cw_ready.get(&t).copied().unwrap_or(0);
            if !want_contempt(&self.p, hp, max, tick, ready_at) {
                continue;
            }
            let dmg = contempt_damage(max, cw_share(&self.p, level));
            sim.deal_damage_typed(me, t, dmg, DamageTypeV1::Ap, AttackTypeV1::Skill);
            sim.play_view_effect(&zd("cw_hit"), me, &InputTargetV1::target(t), 0, 0, 0);
            self.cw_ready.insert(t, tick + self.p.cw_cd);
            self.cw_count += 1;
            if self.cw_count <= 30 || self.cw_count % 50 == 0 {
                wlog(format!("{} CONTEMPT #{} on #{t}: hp {hp}/{max} ({}%) +{dmg} magic", head(sim, me), self.cw_count,
                             hp * 100 / max.max(1)));
            }
        }
    }

    fn marks(&mut self, sim: &mut StableSim<'_>, me: usize, enemies: &[usize]) {
        let name = zd("r_mark");
        for &t in enemies {
            if has_buff(sim, t, &name) && !self.marks.contains_key(&t) {
                let hp_at = sim.get_entity(t).map_or(0, |e| e.hp().0);
                self.marks.insert(t, Mark { stored: 0, hp_at });
                wlog(format!("{} MARK on #{t}: hp {hp_at}", head(sim, me)));
            }
        }
        let ended: Vec<usize> = self.marks.keys().copied().filter(|&t| !has_buff(sim, t, &name)).collect();
        for t in ended {
            let Some(m) = self.marks.remove(&t) else { continue };
            let alive = sim.get_entity(t).is_some_and(|e| e.is_alive());
            let hp_now = sim.get_entity(t).map_or(0, |e| e.hp().0);
            let bonus = mark_bonus(&self.p, m.stored);
            if alive && bonus > 0 {
                sim.deal_damage_typed(me, t, bonus, DamageTypeV1::Ad, AttackTypeV1::Skill);
            }
            self.pops += 1;
            if self.pops <= 30 || self.pops % 20 == 0 {
                wlog(format!("{} POP #{} on #{t}: stored {} (hp drop {}), +{bonus}{}", head(sim, me), self.pops, m.stored,
                             m.hp_at.saturating_sub(hp_now), if alive { "" } else { " (dead: none)" }));
            }
        }
    }
}

impl StablePassive for Edge {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = parse_params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        self.marks.clear();
        let team = sim.get_entity(me).map_or(0, |e| e.team());
        wlog(format!("{} SPAWN: the add-on's Zed (player {player}, team {team}), {:?}", head(sim, me), self.p));
    }

    fn on_attack(&mut self, _sim: &mut StableSim<'_>, _: usize, _me: usize, target: usize, damage: &mut usize) {
        if let Some(m) = self.marks.get_mut(&target) {
            m.stored += *damage;
        }
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let team = e.team();
        let enemies = enemy_champions(sim, team);
        self.contempt(sim, me, &enemies);
        self.marks(sim, me, &enemies);
    }

    fn on_dead(&mut self, _sim: &mut StableSim<'_>, _: usize) {
        // a dead Zed's mark still bursts in League; the data's burst stays, the stored part goes with him
        self.marks.clear();
    }
}

// ===================== 注册 =====================

/// Everything this add-on registers, into `module`: its own DLL's (`init`) or league_addons' (all add-ons in one).
pub fn register(host: &StableHost, module: &mut StableMod) {
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v1 (Contempt for the Weak below 50% health, Death Mark from the damage dealt) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:edge"), Edge::default());
    host.log(LogLevel::Info, "league_zed_mark v1 loaded (Zed's Contempt for the Weak and Death Mark read health and damage).");
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
        assert_eq!(parse_params(r#"{"cw_hp":45,"cw_lo":5,"r_pct":40,"x":1}"#),
                   Params { cw_hp: 45, cw_lo: 5, r_pct: 40, ..Params::default() });
        assert_eq!(parse_params("{}"), Params::default());
    }

    #[test]
    fn contempt_only_below_the_line_and_off_cooldown() {
        let p = Params::default();
        assert!(want_contempt(&p, 499, 1000, 10, 0));
        assert!(!want_contempt(&p, 500, 1000, 10, 0));
        assert!(!want_contempt(&p, 200, 1000, 10, 11));
        assert!(want_contempt(&p, 200, 1000, 11, 11));
        assert!(!want_contempt(&p, 0, 0, 10, 0));
    }

    #[test]
    fn contempt_grows_with_his_level() {
        let p = Params::default();
        assert_eq!(cw_share(&p, 1), 6);
        assert_eq!(cw_share(&p, 7), 8);
        assert_eq!(cw_share(&p, 13), 10);
        assert_eq!(contempt_damage(2000, 8), 160);
        assert_eq!(contempt_damage(5, 6), 1);
    }

    #[test]
    fn the_mark_adds_a_share_of_what_he_dealt() {
        let p = Params::default();
        assert_eq!(mark_bonus(&p, 1000), 350);
        assert_eq!(mark_bonus(&p, 0), 0);
    }

    #[test]
    fn the_names_fit() {
        for x in ["cw_probe", "cw_hit", "r_mark"] {
            assert!(zd(x).len() <= BUFF_NAME_CAP);
        }
    }
}
