//! Lucian walks firing The Culling (needs League of Legends Heroes): while his R fires - the main pack's channel flag
//! `league_lucian_r_ch` on him (183 ticks from the cast, taken away by crowd control as the shots stop) - the `run` the
//! game plays when he walks is drawn as `r_run`, his walk with both pistols levelled forward (Codex's 8 frames, his
//! sheet's r_run / hd_r_run / lo_r_run: tools/art/casts_lucian_runshoot.py). The user, 2026-10-27: 「移动大招看不出来放大
//! 只听得到音乐」「是不是少了点动作？」「动作可以，继续做附加包让开大时换成这套动作」. No data of his is replaced: only the
//! name of the animation on screen ([`view`]). Windows, game 0.6.4 on (the display handler's place found at run time by
//! game_places); elsewhere nothing happens and he runs as before.
//!
//! **Facing his shots** (0.2.0; the user 2026-11-06: 「卢锡安可以倒着放大招？」). The main pack's R does not lock a
//! direction (unlike League's): every 9 ticks a `Delayed` shot flies from wherever he is at the nearest enemy champion
//! (40000, then 75000, 110000 - the user's choice, unchanged here), so the bullets always go at the enemy. His body did
//! not: the game turns a walking unit to the way it walks (the display's move handler sets the picture's flip from each
//! step to the side) and turns it to a target only for an action - a cast or an attack - and the shots are no action.
//! Kiting away while it fired he walked with his back to the enemy, both pistols levelled the other way, the bullets
//! coming out of his back. Now:
//! - [`Aim`] (a match hook: every tick of every simulation, so the server's pre-simulations and the screen's stay the
//!   same) keeps a hidden flag on him while the R fires, [`FACE_L`] or [`FACE_R`]: the side of the enemy champion his
//!   next shot goes to (the nearest alive, targetable, visible one within [`R_REACH`]; one straight above or below him,
//!   less than [`FRONT_SLACK`] to the side, changes nothing). The flags are names only: no stat, no picture, nothing
//!   reads them but [`view`]; taken off when the R ends.
//! - [`view`] turns him to that side at every step while he stands, walks or draws (`idle`, `r_run`, `ult`), after the
//!   game's own step would have turned him back (a Q or E he casts meanwhile still faces its own target), and while he
//!   walks away from his shots plays `r_run` backwards: he backs off with both pistols on the enemy, League's strafe.
//!
//! In the add-on bundle `league_addons` forwards its match hook to [`Aim`] (a mod has one); installed alone this
//! add-on sets it.
//!
//! Log: `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_lucian.log`, rewritten at each launch (the last one in
//! .prev.log):
//! - `MATCH HOOK #n: running` once a match and simulation (the first 40, then every 50th);
//! - `[<view|presim> m=<match> s=<set>] t=<tick> #<Lucian> AIM <left|right>: <champion>#<id> <dx> to the side, <d> away -
//!   his R fires that way #n`: his flag changed side (the first 40, then every 50th);
//! - `FORM display world .. Lucian #<id>: R FIRING - run drawn as r_run, facing <left|right|as the game has him> (playing
//!   <animation>)`: what the display shows changed;
//! - `FACE display world .. Lucian #<id>: the game turned him <side> (<animation>), his shots go <side> - turned back #n`:
//!   the first turn of each R (the 10 s line counts them all);
//! - `BACK display world .. Lucian #<id>: walking <side> away from his shots (<side>) - r_run played backwards #n`;
//! - every 10 s with him on screen: `display handler: <calls> calls, Lucian seen <n> times, <k> animation names swapped,
//!   <t> turns to his shots, <b> frames walked backwards in 10 s`.

use std::collections::HashMap;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::{LazyLock, Mutex};

use mod_api_stable::*;

#[cfg(windows)]
pub mod view;

/// The main pack's R channel flag: the display hook swaps his run while it is on.
pub const FORM: &str = "league_lucian_r_ch";
/// This add-on's hidden flags while the R fires ([`Aim`]): his next shot goes to his left / right. Neither: no enemy
/// champion in reach yet (the display leaves him as the game has him - the cast turned him to its target).
pub const FACE_L: &str = "league_lucian_r_face_l";
pub const FACE_R: &str = "league_lucian_r_face_r";
/// The R's shots look this far for an enemy champion (the kit's widest ring: 40000, 75000, 110000).
pub const R_REACH: u64 = 110_000;
/// An enemy champion less than this to the side (2 game px) is straight above or below him: he keeps facing the way he
/// faces.
pub const FRONT_SLACK: u64 = 2_000;
/// A flag lasts this long when put on (a little more than the R's 183 ticks; taken off as soon as the R ends).
pub const FACE_T: usize = 240;

const ID: &str = "league_lucian";
/// 附加包自己的版本（mod.mod_info）：编进 league_addons 时 CARGO_PKG_VERSION 是合集的，合集的 build.rs 把每个附加包的
/// mod.mod_info 版本给它（ADDON_VERSION_<id>）。
const VERSION: &str = match option_env!("ADDON_VERSION_league_lucian") {
    Some(v) => v,
    None => env!("CARGO_PKG_VERSION"),
};

// ===================== log =====================

static LOG_LOCK: Mutex<()> = Mutex::new(());
static LOG_FILE: Mutex<Option<std::fs::File>> = Mutex::new(None);

fn log_path() -> PathBuf {
    if let Some(path) = std::env::var_os("LEAGUE_LUCIAN_LOG") {
        return PathBuf::from(path);
    }
    if let Some(appdata) = std::env::var_os("APPDATA") {
        let dir = PathBuf::from(appdata).join("TeamSamoyed").join("TeamfightManager2").join("data");
        if dir.is_dir() {
            return dir.join("league_lucian.log");
        }
    }
    PathBuf::from("league_lucian.log")
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

// ===================== which way the R fires =====================

/// Whom his R's next shot goes to from `me`: the nearest of `foes` (where the enemy champions it can shoot stand)
/// within [`R_REACH`] (its index), `None` with nobody in reach. The kit takes any champion in its first ring that has
/// one (40000, 75000, 110000): the nearest is always in it.
pub fn aim_at(me: (u64, u64), foes: &[(u64, u64)]) -> Option<usize> {
    let d2 = |p: (u64, u64)| {
        let (dx, dy) = (p.0 as i128 - me.0 as i128, p.1 as i128 - me.1 as i128);
        dx * dx + dy * dy
    };
    let reach2 = (R_REACH as i128) * (R_REACH as i128);
    (0..foes.len()).filter(|&i| d2(foes[i]) <= reach2).min_by_key(|&i| d2(foes[i]))
}

/// The side a shot from `me` at `foe` goes to: `Some(true)` his left, `Some(false)` his right, `None` straight above or
/// below him (less than [`FRONT_SLACK`] to the side).
pub fn side_of(me: (u64, u64), foe: (u64, u64)) -> Option<bool> {
    (foe.0.abs_diff(me.0) >= FRONT_SLACK).then_some(foe.0 < me.0)
}

/// The flag to put on (and the one to take off) for a side.
pub fn flags(left: bool) -> (&'static str, &'static str) {
    if left {
        (FACE_L, FACE_R)
    } else {
        (FACE_R, FACE_L)
    }
}

/// Every Lucian on the field: while his R fires, the flag of the side his next shot goes to; once it stops, none.
pub fn aim(sim: &mut StableSim<'_>) {
    let champs: Vec<usize> = (0..sim.champion_count()).map(|i| sim.champion_id_at(i)).collect();
    for &me in &champs {
        // (alive, his team, where he stands, his buffs) - read before any change
        let Some((alive, team, at, buffs)) = sim.get_entity(me).filter(|e| e.name().as_deref() == Some(ID)).map(|e| {
            let buffs: Vec<String> = (0..e.buff_count()).filter_map(|i| e.buff_at(i)).map(|b| b.name().to_string()).collect();
            (e.is_alive(), e.team(), e.pos(), buffs)
        }) else {
            continue;
        };
        let has = |n: &str| buffs.iter().any(|b| b == n);
        if !(alive && has(FORM)) {
            for flag in [FACE_L, FACE_R] {
                if has(flag) {
                    sim.entity_remove_buff(me, flag);
                }
            }
            continue;
        }
        let foes: Vec<(usize, (u64, u64))> = champs
            .iter()
            .filter_map(|&id| {
                let u = sim.get_entity(id)?;
                (u.team() != team && u.is_alive() && u.is_targetable() && sim.is_visible(team, id)).then(|| (id, u.pos()))
            })
            .collect();
        let Some(k) = aim_at(at, &foes.iter().map(|f| f.1).collect::<Vec<_>>()) else { continue };
        let (foe, there) = foes[k];
        let Some(left) = side_of(at, there) else { continue };
        let (on, off) = flags(left);
        if has(on) && !has(off) {
            continue;
        }
        if has(off) {
            sim.entity_remove_buff(me, off);
        }
        if !has(on) {
            sim.add_buff(me, &BuffV1::timed(on, FACE_T));
        }
        if let Some(n) = counted("aim") {
            let who = sim.get_entity(foe).and_then(|e| e.name()).unwrap_or_else(|| "?".into());
            let away = (((there.0 as f64 - at.0 as f64).powi(2) + (there.1 as f64 - at.1 as f64).powi(2)).sqrt()) as u64;
            wlog(format!(
                "{} AIM {}: {who}#{foe} {} to the side, {away} away - his R fires that way #{n}",
                head(sim, me),
                if left { "left" } else { "right" },
                there.0.abs_diff(at.0)
            ));
        }
    }
}

/// The match hook ([`aim`] every tick). In the bundle league_addons's `BundleMatch` calls it; alone, this add-on sets it.
pub struct Aim;

impl StableMatchHook for Aim {
    fn on_match_start(&self, sim: &mut StableSim<'_>) {
        if let Some(k) = counted("match_hook") {
            wlog(format!("{} MATCH HOOK #{k}: running - his R's flag of the side it fires to", head(sim, 0)));
        }
    }

    fn on_match_tick(&self, sim: &mut StableSim<'_>, _rng_seed: u64) {
        aim(sim);
    }
}

// ===================== register =====================

pub fn register(host: &StableHost, module: &mut StableMod) {
    close_log();
    let _ = std::fs::rename(&*LOG_PATH, LOG_PATH.with_extension("prev.log"));
    let v = host.game_version();
    wlog(format!(
        "=== {ID} v{VERSION} (Lucian: his walk while The Culling fires, facing his shots) loaded: game {}.{}.{} abi {} log={} ===",
        v.major,
        v.minor,
        v.patch,
        host.abi_level(),
        LOG_PATH.display()
    ));
    // one match hook a mod: in the bundle league_addons's BundleMatch calls Aim
    #[cfg(not(league_bundle))]
    module.set_match_hook(Aim);
    #[cfg(league_bundle)]
    let _ = &module;
    #[cfg(windows)]
    view::install_once();
    host.log(LogLevel::Info, "league_lucian loaded (his walk while The Culling fires, facing his shots).");
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
    fn the_nearest_enemy_champion_in_reach_is_aimed_at() {
        let me = (500_000, 500_000);
        // the nearest of two: the one 30000 to his left, not the one 60000 to his right
        let foes = [(560_000, 500_000), (470_000, 500_000)];
        assert_eq!(aim_at(me, &foes), Some(1));
        assert_eq!(side_of(me, foes[1]), Some(true));
        assert_eq!(side_of(me, foes[0]), Some(false));
        // out of the widest ring: nobody
        assert_eq!(aim_at(me, &[(500_000 + R_REACH + 1, 500_000)]), None);
        assert_eq!(aim_at(me, &[(500_000 + R_REACH, 500_000)]), Some(0));
        assert_eq!(aim_at(me, &[]), None);
        // straight above or below him: no side
        assert_eq!(side_of(me, (500_000 + FRONT_SLACK - 1, 430_000)), None);
        assert_eq!(side_of(me, (500_000 - FRONT_SLACK, 430_000)), Some(true));
    }

    #[test]
    fn one_flag_on_the_other_off() {
        assert_eq!(flags(true), (FACE_L, FACE_R));
        assert_eq!(flags(false), (FACE_R, FACE_L));
        assert!(FACE_T > 183, "a flag outlasts the R");
    }

    /// The rings his R's shots look for an enemy champion in (`RandomTarget` ... `"casting_target": "EnemyChampion"`).
    fn rings(ult: &str) -> Vec<u64> {
        let mut out = Vec::new();
        for (at, _) in ult.match_indices("\"type\": \"RandomTarget\"") {
            let rest = &ult[at..];
            let num = |key: &str| rest.find(key).map(|k| &rest[k + key.len()..]);
            let (Some(range), Some(target)) = (num("\"range\": "), num("\"casting_target\": \"")) else { continue };
            let range: u64 = range[..range.find(',').unwrap()].trim().parse().unwrap();
            if target.starts_with("EnemyChampion\"") {
                out.push(range);
            }
        }
        out.sort_unstable();
        out.dedup();
        out
    }

    #[test]
    fn the_reach_is_the_kits_widest_ring() {
        // the ult's shots look for an EnemyChampion 40000, then 75000, then 110000 around him
        let data = include_str!("../../../league/champion/league_lucian.data_champion");
        let ult = &data[data.find("\"ult\"").expect("his ult")..];
        let ult = &ult[..ult.find("\"view_projectiles\"").unwrap_or(ult.len())];
        assert_eq!(rings(ult), vec![40_000, 75_000, R_REACH]);
        // the flags are this add-on's own: nothing in his kit uses them
        assert!(!data.contains(FACE_L) && !data.contains(FACE_R));
        assert!(ult.contains(&format!("\"{FORM}\"")));
    }
}
