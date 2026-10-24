//! 萨科附加包：「背刺」照英雄联盟看是不是从背后打的（用户 2026-10-24：「查看现在没有做附加包的英雄有明显不一样的话全部补
//! 附加包」）。
//!
//! 主包是纯数据，读不到朝向：普攻和毒刃打中**被控制**的敌方英雄（被恐惧的人背对着他逃跑）才多一下背刺。英雄联盟里从背后
//! 打到就是背刺，和控制无关。本包：副本里那两枚只打 `EnemyChampionInCC` 的分身弹改成打所有敌方英雄、只给他挂 `ASK`
//! （3 tick）；被动 `league_shaco_backstab:backstab` 每 tick 记下敌方英雄最近 `TRACK` tick 的位置，看到标记就判断：
//!
//! - **朝向**：这段时间走了 `MOVED` 以上，就是他走的方向；站着不动（在打东西）就朝着离他最近的萨科一方单位（英雄、小兵）。
//! - **背后**：萨科在他朝向的反方向那一半（朝向和「他→萨科」的夹角大于 90°）。
//! - 是背刺就补 `base` + `ad`% 攻击力的物理伤害（数字在英雄数据的 `passive.params`，同主包），播主包的背刺画面和声音。
//!
//! Q 落地那一刀（必定暴击）、R 幻像的背刺都在主包数据里，不变。
//! 日志：`%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_shaco_backstab.log`。

use std::collections::{HashMap, VecDeque};
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

const ID: &str = "league_shaco_backstab";
pub const ASK: &str = "league_shaco_bs_ask";
pub const VIEW: &str = "league_shaco_bs_hit";
pub const TRACK: usize = 10;
pub const MOVED: f64 = 1_500.0;

// ===================== 日志 =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_SHACO_BACKSTAB_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_shaco_backstab.log");
        }
    }
    PathBuf::from("league_shaco_backstab.log")
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

// ===================== 朝向 =====================

type Pt = (f64, f64);

fn sub(a: Pt, b: Pt) -> Pt {
    (a.0 - b.0, a.1 - b.1)
}

fn len(v: Pt) -> f64 {
    (v.0 * v.0 + v.1 * v.1).sqrt()
}

/// Which way he faces: where he walked (`trail`, oldest first), else toward `foe` (the nearest of Shaco's side).
pub fn facing(trail: &VecDeque<Pt>, foe: Option<Pt>) -> Option<Pt> {
    let (first, last) = (trail.front()?, trail.back()?);
    let walk = sub(*last, *first);
    if len(walk) >= MOVED {
        return Some(walk);
    }
    foe.map(|f| sub(f, *last)).filter(|v| len(*v) > 1.0)
}

/// Is Shaco at `shaco` behind someone at `at` facing `face`? (the back half: more than 90° off his facing)
pub fn behind(at: Pt, face: Pt, shaco: Pt) -> bool {
    let v = sub(shaco, at);
    face.0 * v.0 + face.1 * v.1 < 0.0
}

fn pos(e: &StableEntity<'_, '_>) -> Pt {
    (e.pos().0 as f64, e.pos().1 as f64)
}

fn has_buff(e: &StableEntity<'_, '_>, name: &str) -> bool {
    (0..e.buff_count()).filter_map(|i| e.buff_at(i)).any(|b| b.name() == name)
}

#[derive(Clone, Default)]
struct Backstab {
    p: Vec<(String, usize)>,
    trails: HashMap<usize, VecDeque<Pt>>,
    asked: usize,
    stabs: usize,
}

impl StablePassive for Backstab {
    fn clone_box(&self) -> Box<dyn StablePassive> {
        Box::new(self.clone())
    }

    fn configure(&mut self, params_json: &str) {
        self.p = params(params_json);
    }

    fn on_spawn(&mut self, sim: &mut StableSim<'_>, player: usize, me: usize) {
        wlog(format!("{} SPAWN: the add-on's Shaco (player {player}), {:?}", head(sim, me), self.p));
    }

    fn on_update(&mut self, sim: &mut StableSim<'_>, _: u64, _: usize, me: usize) {
        let Some(e) = sim.get_entity(me) else { return };
        let (team, at, attack) = (e.team(), pos(&e), e.stat().attack);
        let mine: Vec<Pt> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() == team && u.is_alive() && (u.is_champion() || u.is_minion()))
            .map(|u| pos(&u)).collect();
        let foes: Vec<(usize, Pt, bool)> = (0..sim.entity_count()).filter_map(|i| sim.entity_at(i))
            .filter(|u| u.team() != team && u.is_champion())
            .map(|u| (u.id(), pos(&u), u.is_alive() && has_buff(&u, ASK)))
            .collect();
        let mut asks = Vec::new();
        for (id, p, ask) in &foes {
            let t = self.trails.entry(*id).or_default();
            if t.back().is_some_and(|b| len(sub(*b, *p)) > 20_000.0) {
                t.clear(); // a recall, a respawn or a blink: no walking direction across it
            }
            t.push_back(*p);
            while t.len() > TRACK {
                t.pop_front();
            }
            if *ask {
                let near = mine.iter().copied().min_by(|a, b| len(sub(*a, *p)).total_cmp(&len(sub(*b, *p))));
                asks.push((*id, *p, facing(t, near)));
            }
        }
        let damage = get(&self.p, "base", 15) + attack * get(&self.p, "ad", 25) / 100;
        for (id, p, face) in asks {
            sim.entity_remove_buff(id, ASK);
            self.asked += 1;
            let Some(face) = face else { continue };
            if !behind(p, face, at) {
                continue;
            }
            sim.deal_damage_typed(me, id, damage, DamageTypeV1::Ad, AttackTypeV1::Skill);
            sim.play_view_effect(VIEW, me, &InputTargetV1::target(id), 0, 0, 0);
            sim.play_sfx(VIEW, me, &InputTargetV1::target(id));
            self.stabs += 1;
            if self.stabs <= 80 || self.stabs % 25 == 0 {
                wlog(format!("{} BACKSTAB #{} on #{id}: +{damage} physical ({} of {} hits from behind)", head(sim, me),
                             self.stabs, self.stabs, self.asked));
            }
        }
    }
}

// ===================== 注册 =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{} (Shaco's Backstab from behind, by where the target faces) loaded: game {}.{}.{} abi {} log={} ===",
        env!("CARGO_PKG_VERSION"),
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    module.add_native_passive(format!("{ID}:backstab"), Backstab::default());
    host.log(LogLevel::Info, "league_shaco_backstab v1 loaded (Backstab from behind).");
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
    fn walking_away_shows_his_back() {
        let t: VecDeque<Pt> = (0..10).map(|k| (k as f64 * 300.0, 0.0)).collect();
        let f = facing(&t, None).unwrap();
        assert!(f.0 > 0.0);
        // Shaco chasing him from the left: behind; in front on the right: not
        assert!(behind((2_700.0, 0.0), f, (-5_000.0, 0.0)));
        assert!(!behind((2_700.0, 0.0), f, (9_000.0, 0.0)));
    }

    #[test]
    fn standing_he_faces_the_nearest_foe() {
        let t: VecDeque<Pt> = (0..10).map(|_| (0.0, 0.0)).collect();
        let f = facing(&t, Some((10_000.0, 0.0))).unwrap();
        assert!(behind((0.0, 0.0), f, (-8_000.0, 1_000.0)));
        assert!(!behind((0.0, 0.0), f, (8_000.0, 0.0)));
        assert_eq!(facing(&t, None), None);
    }
}
